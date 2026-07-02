use cellshift::data::{DatasetReader, DatasetWriter};
use gtt23::AugmentedCircuit;

use crate::{cli::MergeArgs, util};

pub fn run_merge(args: &MergeArgs) -> anyhow::Result<()> {
    log::info!("Merging databases");

    let n_tot_circs = {
        let mut n_tot_circs = 0;
        for path in &args.databases {
            n_tot_circs += hdf5::File::open(path)?.dataset("circuits")?.size();
        }
        n_tot_circs
    };

    log::info!(
        "Merging {n_tot_circs} circuits across {} files",
        args.databases.len()
    );

    // Make a dataset with the known size.
    let mut output: DatasetWriter<AugmentedCircuit> =
        DatasetWriter::new(&args.output, n_tot_circs, args.compress)?;

    // Track progress.
    let pb = util::pb_new(n_tot_circs, "Copying circuits".to_string());
    pb.tick();

    // Read/Write in chunks for better performance and progress updates.
    let mut tot_written = 0;
    let mut tot_read = 0;

    for path in &args.databases {
        log::info!("Starting to merge circuits from {path:?}");

        let db: DatasetReader<AugmentedCircuit> = DatasetReader::new(path)?;

        for slice in db.iter(args.rw_slice_len, None, None)? {
            tot_read += slice.len();
            let (n_written, _) = output.write_arr(slice)?;
            tot_written += n_written;
            pb.inc(n_written as u64);
        }

        log::info!("Finished merging circuits from {path:?}",);

        db.close()?;
    }

    log::info!("Read {tot_read} circuits and wrote {tot_written} circuits");

    // Sanity checks.
    if tot_read != n_tot_circs {
        log::warn!("Only processed {tot_read}/{n_tot_circs} circuits");
    }
    if tot_written != n_tot_circs {
        log::warn!("Only wrote {tot_written}/{n_tot_circs} circuits");
    }

    output.truncate_and_close()?;

    Ok(())
}
