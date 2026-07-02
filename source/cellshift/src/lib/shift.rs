use anyhow::{Context, bail};
use uuid::Uuid;

use gtt23::{AugmentedCircuit, Circuit, Direction};

use crate::rtt::RttEstimator;
use crate::{DestinationPosition, SourcePosition};

pub struct CellShift<'a> {
    /// The new shifted circuit.
    shifted: AugmentedCircuit,
    /// The estimator from the original circuit.
    estimator: &'a RttEstimator,
    /// The time of the last server-to-client cell; helps maintain an in-order stream.
    prev_time_inward: f64,
    /// The time of the last client-to-server cell; helps maintain an in-order stream.
    prev_time_outward: f64,
}

impl<'a> CellShift<'a> {
    pub fn new(
        circuit: &Circuit,
        estimator: &'a RttEstimator,
        aug_index: u16,
    ) -> anyhow::Result<Self> {
        // Generates a new uuid.
        let uuid = gtt23::fixedascii_from_str::<32>(&Uuid::new_v4().simple().to_string()[..])?;

        Ok(Self {
            estimator,
            // Copy the original circuit and cell metadata.
            shifted: AugmentedCircuit {
                uuid,
                uuid_gtt23: circuit.uuid,
                aug_index,
                len: circuit.len,
                cells: circuit.cells,
            },
            prev_time_inward: 0.0,
            prev_time_outward: 0.0,
        })
    }

    pub fn shift(
        mut self,
        dst_pos: DestinationPosition,
        dst_estimator: &RttEstimator,
        dst_prop_delay: f64,
    ) -> anyhow::Result<AugmentedCircuit> {
        // We require a valid circuit RTT otherwise the algorithm will not work as intended.
        if self.estimator.propagation_delay().is_none() {
            bail!("Source propagation delay estimate is not available.")
        }
        if dst_estimator.propagation_delay().is_none() {
            bail!("Destination propagation delay estimate is not available.")
        }

        // This iter will return an RTT for every cell prior to the start of padding.
        let mut rtt_iter = self.estimator.iter_rtts();

        // This returns a congestion for every cell; it cycles in case the dst circuit is shorter.
        let mut dst_cong_cycle = dst_estimator.iter_congestion().cycle();

        for i in 0..(self.shifted.len as usize) {
            // Get the appropriate RttEstimate objects corresponding to this cell.
            let src_est = rtt_iter
                .next()
                .context("Unexpectedly missing source RTT estimates")?;
            let dst_est = dst_cong_cycle
                .next()
                .context("Unexpectedly missing destination congestion estimates")?;

            // The source estimate gives us the RTT of the cell.
            let src_rtt = src_est.time();
            assert!(src_rtt >= 0.0);

            // The destination estimate give us the congestion for the cell.
            let dst_cong = dst_est.time();
            assert!(dst_cong >= 0.0);

            // The full target RTT.
            let dst_rtt = dst_prop_delay + dst_cong;
            assert!(dst_rtt >= 0.0);

            // Shift the cell to the new vantage point.
            self.shift_cell_time(i, self.estimator.position(), src_rtt, dst_pos, dst_rtt)?;
        }

        // Sort the cells to realign the two opposite direction cell streams.
        // Do not include the padding suffix part of the trace when sorting.
        self.shifted.cells[0..(self.shifted.len as usize)].sort();

        Ok(self.shifted)
    }

    fn shift_cell_time(
        &mut self,
        cell_index: usize,
        src_pos: SourcePosition,
        src_rtt: f64,
        dst_pos: DestinationPosition,
        dst_rtt: f64,
    ) -> anyhow::Result<()> {
        let cell_direction = self.shifted.cells[cell_index].direction;
        let cell_time = self.shifted.cells[cell_index].time;

        // Shift the cell time based on the positions.
        let shifted_time = match cell_direction {
            Direction::SERVER_TO_CLIENT => match src_pos {
                SourcePosition::Client => match dst_pos {
                    // Client was the observed sender of the cell.
                    // Erase src RTT, then transduce vantage point according to dst RTT.
                    DestinationPosition::ISP => {
                        cell_time - latency(src_rtt, 3.0) + latency(dst_rtt, 2.5)
                    }
                    DestinationPosition::Entry => {
                        cell_time - latency(src_rtt, 3.0) + latency(dst_rtt, 2.0)
                    }
                },
                SourcePosition::Exit => match dst_pos {
                    // Exit was already the observed sender of the cell.
                    // Transduce vantage point according to the dst RTT.
                    DestinationPosition::ISP => cell_time + latency(dst_rtt, 2.5),
                    DestinationPosition::Entry => cell_time + latency(dst_rtt, 2.0),
                },
            },
            Direction::CLIENT_TO_SERVER => match src_pos {
                SourcePosition::Client => match dst_pos {
                    // Client was already the observed sender of the cell.
                    // Transduce vantage point according to dst RTT.
                    DestinationPosition::ISP => cell_time + latency(dst_rtt, 0.5),
                    DestinationPosition::Entry => cell_time + latency(dst_rtt, 1.0),
                },
                SourcePosition::Exit => match dst_pos {
                    // Exit was the observed sender of the cell.
                    // Erase src RTT, then transduce vantage point according to dst RTT.
                    DestinationPosition::ISP => {
                        cell_time - latency(src_rtt, 3.0) + latency(dst_rtt, 0.5)
                    }
                    DestinationPosition::Entry => {
                        cell_time - latency(src_rtt, 3.0) + latency(dst_rtt, 1.0)
                    }
                },
            },
            Direction::PADDING => bail!("Unexpected padding too early in trace"),
        };

        // Ensure that the cells in both directional cell streams remain in-order.
        let shifted_time = match cell_direction {
            Direction::CLIENT_TO_SERVER => self.next_outward_time(shifted_time),
            Direction::SERVER_TO_CLIENT => self.next_inward_time(shifted_time),
            Direction::PADDING => bail!("Unexpected padding too early in trace"),
        };

        // Sanity checks.
        if shifted_time < 0.000001 {
            bail!("Shifted cell time is < 1 micro ({shifted_time})")
        }
        let diff = shifted_time - cell_time;
        if diff.abs() > 86_400.0 {
            bail!(
                "Shifted cell time is > 1 day different from original 
                (orig: {cell_time}, aug: {shifted_time}, diff: {diff})"
            )
        }

        self.shifted.cells[cell_index].time = shifted_time;

        Ok(())
    }

    fn next_inward_time(&mut self, time: f64) -> f64 {
        // Must be positive and in order, with a max resolution of microseconds.
        let new_time = crate::round_micro_res(time)
            .max(0.000001)
            .max(self.prev_time_inward);
        self.prev_time_inward = new_time;
        new_time
    }

    fn next_outward_time(&mut self, time: f64) -> f64 {
        // Must be positive and in order, with a max resolution of microseconds.
        let new_time = crate::round_micro_res(time)
            .max(0.000001)
            .max(self.prev_time_outward);
        self.prev_time_outward = new_time;
        new_time
    }
}

/// Convert 6-hop RTT into n-hop latency using a simple average heuristic.
fn latency(rtt: f64, num_hops: f64) -> f64 {
    rtt / 6.0 * num_hops
}

#[cfg(test)]
mod tests {
    use gtt23::RelayCommand;

    use crate::{SourcePosition, tests::CircuitBuilder};

    use super::*;

    #[test]
    fn shift_basic() {
        let rtt = 0.6;
        let circ = CircuitBuilder::build_basic(rtt);

        assert_eq!(circ.cells[0].direction, Direction::CLIENT_TO_SERVER);
        assert_eq!(circ.cells[0].time, 0.600001);

        assert_eq!(circ.cells[1].direction, Direction::SERVER_TO_CLIENT);
        assert_eq!(circ.cells[1].time, 0.610001);

        assert_eq!(circ.cells[2].direction, Direction::CLIENT_TO_SERVER);
        assert_eq!(circ.cells[2].time, 1.210001);

        let est = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);
        assert_eq!(est.propagation_delay(), Some(rtt));

        let aug_circ = CellShift::new(&circ, &est, 0)
            .unwrap()
            .shift(
                DestinationPosition::Entry,
                &est,
                est.propagation_delay().unwrap(),
            )
            .unwrap();

        assert_eq!(aug_circ.cells[0].direction, Direction::CLIENT_TO_SERVER);
        assert_eq!(aug_circ.cells[0].time, 0.400001);

        assert_eq!(aug_circ.cells[1].direction, Direction::SERVER_TO_CLIENT);
        assert_eq!(aug_circ.cells[1].time, 0.810001);

        assert_eq!(aug_circ.cells[2].direction, Direction::CLIENT_TO_SERVER);
        assert_eq!(aug_circ.cells[2].time, 1.010001);
    }

    #[test]
    fn shift_basic_extended() {
        let rtt = 0.6;
        let circ = CircuitBuilder::build_basic(rtt);

        let mut builder = CircuitBuilder::from(circ);
        builder.add_time(rtt + 0.000001);
        builder.add_cell(Direction::SERVER_TO_CLIENT, RelayCommand::DATA);
        builder.add_time(0.000001);
        builder.add_cell(Direction::CLIENT_TO_SERVER, RelayCommand::DATA);
        let circ = Circuit::from(builder);

        assert_eq!(circ.cells[3].direction, Direction::SERVER_TO_CLIENT);
        assert_eq!(circ.cells[4].direction, Direction::CLIENT_TO_SERVER);
        assert!(circ.cells[3].time < circ.cells[4].time);

        let est = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        let aug_circ = CellShift::new(&circ, &est, 0)
            .unwrap()
            .shift(
                DestinationPosition::Entry,
                &est,
                est.propagation_delay().unwrap(),
            )
            .unwrap();

        assert_eq!(aug_circ.cells[3].direction, Direction::CLIENT_TO_SERVER);
        assert_eq!(aug_circ.cells[4].direction, Direction::SERVER_TO_CLIENT);

        let mut prev = 0.0;
        for i in 0..aug_circ.len {
            let next = aug_circ.cells[i as usize].time;
            assert!(prev <= next);
            assert!(next > 0.0);
            prev = next;
        }
    }
}
