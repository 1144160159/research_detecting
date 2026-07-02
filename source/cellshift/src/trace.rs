use anyhow::{Context, bail};
use cellshift::SourcePosition;
use cellshift::data::{DatasetReader, DatasetWriter};
use cellshift::rtt::RttEstimator;
use cellshift::shift::CellShift;
use gtt23::{AugmentedCircuit, Circuit};
use rand::seq::IndexedRandom;
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;

use crate::cli::{FilterArgs, IoArgs, MorphArgs, MoveArgs};
use crate::util;

pub fn run_tracemove(args: &MoveArgs) -> anyhow::Result<()> {
    log::info!("Running the move command now");

    process_all_circuits(&args.io, &args.filter, 1, |circuit: &Circuit| {
        let estimator =
            RttEstimator::new(&circuit.cells, circuit.len as usize, args.position.source);

        let Some(prop_delay) = estimator.propagation_delay() else {
            bail!("Unable to estimate propagation delay for circuit")
        };

        Ok(vec![CellShift::new(circuit, &estimator, 0)?.shift(
            args.position.destination,
            &estimator,
            prop_delay,
        )?])
    })
}

pub fn run_tracemorph(args: &MorphArgs) -> anyhow::Result<()> {
    log::info!("Running the morph command now");

    let seed = match args.seed {
        Some(seed) => seed,
        None => rand::rng().random(),
    };
    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    log::info!("Using ChaCha8Rng seeded with {seed}");

    let mut targets: MorphTargets = train_tracemorph(args)?;

    log::info!("Training complete, processing input circuits now");

    process_all_circuits(
        &args.base.io,
        &args.base.filter,
        args.aug_factor,
        |circuit: &Circuit| {
            let mut aug_index = 0u16;

            // First transduce circuit on itself. This part is the same as TraceMove.
            let estimator = RttEstimator::new(
                &circuit.cells,
                circuit.len as usize,
                args.base.position.source,
            );

            let Some(prop_delay) = estimator.propagation_delay() else {
                bail!("Unable to estimate propagation delay for circuit")
            };

            let mut augmented = vec![CellShift::new(circuit, &estimator, aug_index)?.shift(
                args.base.position.destination,
                &estimator,
                prop_delay,
            )?];
            aug_index += 1;

            // Now augment with the trained target propagation delays and congestions.
            for (dst_prop_delay, dst_estimator) in targets.iter(args.aug_factor - 1, &mut rng)? {
                assert!(aug_index < args.aug_factor);

                let shifted = CellShift::new(circuit, &estimator, aug_index)?.shift(
                    args.base.position.destination,
                    dst_estimator,
                    dst_prop_delay,
                )?;
                aug_index += 1;

                augmented.push(shifted);
            }

            Ok(augmented)
        },
    )
}

fn process_all_circuits<F>(
    io: &IoArgs,
    filter: &FilterArgs,
    aug_factor: u16,
    mut process_circuit_f: F,
) -> anyhow::Result<()>
where
    F: FnMut(&Circuit) -> anyhow::Result<Vec<AugmentedCircuit>>,
{
    // Create our circuit database helper.
    let input: DatasetReader<Circuit> = DatasetReader::new(&io.input)?;

    // Handle the timeframe filter conversion if needed.
    let filter_days = util::get_days_filter(filter);

    let slice_iter = input.iter(io.read_slice_len, filter.min_length, filter_days)?;
    let n_circuits = slice_iter.total_size();

    // We will write out some number of circuits for each input circuit.
    let mut output: DatasetWriter<AugmentedCircuit> =
        DatasetWriter::new(&io.output, n_circuits * (aug_factor as usize), io.compress)?;

    // Run cellshift over the dataset while incrementally reading and writing.
    let pb = util::pb_new(n_circuits, "Processing circuits".to_string());
    pb.tick();

    // Read each slice.
    let mut n_skipped = 0;
    for slice in slice_iter {
        // Transduce each circuit in the slice.
        let mut transduced: Vec<AugmentedCircuit> = Vec::new();

        for circuit in slice.iter() {
            match process_circuit_f(circuit) {
                Ok(mut shifted) => transduced.append(&mut shifted),
                Err(e) => {
                    n_skipped += 1;
                    log::debug!("Skipped circuit {}: {:?}", circuit.uuid, e);
                }
            }
        }

        if !transduced.is_empty() {
            let num_to_write = transduced.len();
            // Write out the augmented circuits in a chunk.
            let (write_len, _) = output.write_vec(transduced)?;
            assert!(write_len > 0);
            assert_eq!(write_len, num_to_write);
        }

        pb.inc(slice.len() as u64);
    }

    log::info!(
        "Finished processing {}/{n_circuits} circuits",
        pb.position(),
    );
    if n_circuits > 0 {
        log::info!(
            "Skipped {n_skipped}/{n_circuits} invalid circuits ({} %)",
            100.0 * (n_skipped as f64) / (n_circuits as f64),
        );
    }

    let final_size = output.truncate_and_close()?;
    input.close()?;

    log::info!("Final written dataset contains {final_size} circuits");

    Ok(())
}

fn train_tracemorph(args: &MorphArgs) -> anyhow::Result<MorphTargets> {
    // Use circuits in train file if given, otherwise the input file.
    let (input, filter_min_length, filter_days) = match &args.train {
        Some(train_path) => {
            // We do not apply a filter to the training file.
            let input: DatasetReader<Circuit> = DatasetReader::new(train_path)?;
            (input, None, None)
        }
        None => {
            let input: DatasetReader<Circuit> = DatasetReader::new(&args.base.io.input)?;
            (
                input,
                args.base.filter.min_length,
                util::get_days_filter(&args.base.filter),
            )
        }
    };

    let slice_iter = input.iter(args.base.io.read_slice_len, filter_min_length, filter_days)?;

    let pb = util::pb_new(
        slice_iter.total_size(),
        "Training morph targets".to_string(),
    );
    pb.tick();

    let mut targets = MorphTargets::new();

    for slice in slice_iter {
        for circuit in slice.iter() {
            targets.train(circuit, args.base.position.source);
        }
        pb.inc(slice.len() as u64);
    }

    Ok(targets)
}

struct MorphTargets {
    estimators: Vec<RttEstimator>,
    prop_delay_dist: Vec<f64>,
    need_sort: bool,
}

impl MorphTargets {
    fn new() -> Self {
        Self {
            estimators: Vec::new(),
            prop_delay_dist: Vec::new(),
            need_sort: false,
        }
    }

    fn train(&mut self, circuit: &Circuit, position: SourcePosition) {
        let estimator = RttEstimator::new(&circuit.cells, circuit.len as usize, position);
        if let Some(prop_delay) = estimator.propagation_delay() {
            self.estimators.push(estimator);
            self.prop_delay_dist.push(prop_delay);
            self.need_sort = true;
        }
    }

    fn iter(
        &mut self,
        n_aug: u16,
        mut rng: &mut ChaCha8Rng,
    ) -> anyhow::Result<MorphTargetIterator> {
        let n_aug_orig = n_aug;

        // We want equidistant splits of the prop dist, so it needs to be sorted.
        if self.need_sort {
            self.prop_delay_dist.sort_by(|a, b| a.total_cmp(b));
            self.need_sort = false;
        }

        let mut n_aug = n_aug as usize;
        let mut prop_delay_splits: Vec<f64> = Vec::new();

        // Just in case n_aug is greater than the number of prop delays.
        while self.prop_delay_dist.len() <= n_aug {
            prop_delay_splits.extend_from_slice(&self.prop_delay_dist[..]);
            n_aug -= self.prop_delay_dist.len();
        }

        // Select equidistant prop delays using a step.
        let step = self.prop_delay_dist.len() / (n_aug + 1);
        for i in 0..n_aug {
            let j = step * (i + 1);
            prop_delay_splits.push(self.prop_delay_dist[j]);
        }
        assert_eq!(n_aug_orig as usize, prop_delay_splits.len());

        // Now get a random congestion profile to match with each equidistant prop delay.
        let mut targets: Vec<(f64, &RttEstimator)> = Vec::new();
        while let Some(prop_delay) = prop_delay_splits.pop() {
            let rand_estimator = self
                .estimators
                .choose(&mut rng)
                .context("Cannot choose random estimator")?;
            assert!(rand_estimator.propagation_delay().is_some());
            targets.push((prop_delay, rand_estimator));
        }

        Ok(MorphTargetIterator { targets })
    }
}

struct MorphTargetIterator<'a> {
    targets: Vec<(f64, &'a RttEstimator)>,
}

impl<'a> Iterator for MorphTargetIterator<'a> {
    type Item = (f64, &'a RttEstimator);

    fn next(&mut self) -> Option<Self::Item> {
        self.targets.pop()
    }
}
