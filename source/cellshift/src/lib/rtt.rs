use std::{collections::VecDeque, ops::Sub};

use gtt23::{Cell, Direction, RelayCommand};

use crate::SourcePosition;

#[derive(Clone)]
pub struct RttEstimator {
    /// The position from which the trace was observed.
    position: SourcePosition,
    /// The RTT estimates computed for the original trace.
    rtts: Vec<TimeEstimate>,
    /// The minimum of the RTT estimates computed for the original trace.
    rtt_min: Option<f64>,
    /// The number of non-padding cells in the original trace.
    len_cells: usize,
}

/// Estimates circuit RTTs based on cell metadata and timing.
impl RttEstimator {
    pub fn new(trace: &[Cell; 5000], trace_len: usize, trace_pos: SourcePosition) -> Self {
        let mut estimator = Self {
            rtts: Vec::new(),
            rtt_min: None,
            len_cells: trace_len,
            position: trace_pos,
        };

        let mut rtts = CellTimingMeasurements::new().estimate_rtts(trace, trace_pos);
        estimator.rtts.reserve_exact(rtts.len());

        while let Some(estimate) = rtts.pop_front() {
            let rtt_min = estimator.rtt_min.get_or_insert(estimate.time);
            *rtt_min = rtt_min.min(estimate.time);
            estimator.rtts.push(estimate);
        }

        estimator
    }

    pub fn position(&self) -> SourcePosition {
        self.position
    }

    pub fn len_rtts(&self) -> usize {
        self.rtts.len()
    }

    pub fn len_cells(&self) -> usize {
        self.len_cells
    }

    pub fn propagation_delay(&self) -> Option<f64> {
        self.rtt_min
    }

    // Inefficiently obtains the RTT corresponding to any cell index.
    fn _rtt_at(&self, cell_index: usize) -> Option<f64> {
        self.iter_rtts().nth(cell_index).map(|est| est.time)
    }

    // Inefficiently obtains the congestion corresponding to any cell index.
    fn _congestion_at(&self, cell_index: usize) -> Option<f64> {
        self.iter_congestion().nth(cell_index).map(|est| est.time)
    }

    pub fn iter_congestion(&self) -> TimeEstimateIterator {
        TimeEstimateIterator::new(self, true)
    }

    pub fn iter_rtts(&self) -> TimeEstimateIterator {
        TimeEstimateIterator::new(self, false)
    }
}

#[derive(Clone)]
pub struct TimeEstimateIterator<'a> {
    estimator: &'a RttEstimator,
    estimate_index: usize,
    cell_index: usize,
    is_congestion: bool,
}

impl<'a> TimeEstimateIterator<'a> {
    fn new(estimator: &'a RttEstimator, is_congestion: bool) -> Self {
        TimeEstimateIterator {
            estimator,
            estimate_index: 0,
            cell_index: 0,
            is_congestion,
        }
    }
}

impl<'a> Iterator for TimeEstimateIterator<'a> {
    type Item = TimeEstimate;

    fn next(&mut self) -> Option<Self::Item> {
        let has_estimate = self.estimate_index < self.estimator.rtts.len();
        let is_last = has_estimate && self.estimate_index == self.estimator.rtts.len() - 1;

        if has_estimate {
            let est = &self.estimator.rtts[self.estimate_index];

            if (self.cell_index <= est.cell_index)
                || (is_last && self.cell_index < self.estimator.len_cells())
            {
                self.cell_index += 1;

                let mut est = est.clone();
                if self.is_congestion {
                    est.time = est
                        .time
                        .sub(self.estimator.propagation_delay().unwrap_or_default())
                }

                Some(est)
            } else {
                self.estimate_index += 1;
                self.next()
            }
        } else {
            None
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct TimeEstimate {
    time: f64,
    cell_index: usize,
}

impl TimeEstimate {
    fn new(time: f64, cell_index: usize) -> Self {
        Self { time, cell_index }
    }

    pub fn time(&self) -> f64 {
        self.time
    }

    pub fn cell_index(&self) -> usize {
        self.cell_index
    }
}

struct PartialRttEstimate {
    begin: f64,
}

impl PartialRttEstimate {
    fn new(begin: f64) -> Self {
        Self { begin }
    }

    fn into_rtt_estimate(self, end: f64, cell_index: usize) -> TimeEstimate {
        // Cell timestamps only have microsec resolution.
        let rtt = crate::round_micro_res(end - self.begin);
        assert!(rtt > 0.0);
        TimeEstimate::new(rtt, cell_index)
    }
}

// Initial RTT estimate is client<-exit: CONNECTED -to- client->exit:DATA
//     Relay.BEGIN  ->
//                  <- Relay.CONNECTED
//     Relay.DATA   ->
// Subsequent RTT estimates are client<-exit: 31st DATA -to- client->exit:SENDME
//                  <- Relay.DATA (every 31st of these)
//     Relay.SENDME ->
struct CellTimingMeasurements {
    first_connected: Option<PartialRttEstimate>,
    primary_rtt: Option<TimeEstimate>,
    num_data_sent: usize,
    sendme_triggers: VecDeque<PartialRttEstimate>,
    updated_rtts: VecDeque<TimeEstimate>,
    use_sendme_estimates: bool,
}

impl CellTimingMeasurements {
    fn new() -> Self {
        Self {
            first_connected: None,
            primary_rtt: None,
            num_data_sent: 0,
            sendme_triggers: VecDeque::new(),
            updated_rtts: VecDeque::new(),
            use_sendme_estimates: true,
        }
    }

    fn estimate_rtts(
        mut self,
        trace: &[Cell; 5000],
        position: SourcePosition,
    ) -> VecDeque<TimeEstimate> {
        if position != SourcePosition::Exit {
            // Here are some possible RTTs from a client source position:
            // - client->exit EXTEND to client<-exit EXTENDED
            // - client->exit EXTEND2 to client<-exit EXTENDED2
            // - client->exit RESOLVE to client<-exit RESOLVED
            // - client->exit 31st DATA to client<-exit SENDME
            unimplemented!(
                "Sorry! Transducing from a client source position can be done, 
                but I have not worked through the details yet."
            )
        }

        for (i, cell) in trace.iter().enumerate() {
            log::trace!("{:?}", cell);

            // Report to the measurement module when we sent a CONNECTED or DATA, and
            // when we received a DATA or SENDME. Those are used for RTT estimates.
            match cell.direction {
                Direction::SERVER_TO_CLIENT => {
                    if cell.relay_cmd == RelayCommand::CONNECTED {
                        self.sent_connected(cell.time, i);
                    } else if cell.relay_cmd == RelayCommand::DATA {
                        self.sent_data(cell.time, i);
                    }
                }
                Direction::CLIENT_TO_SERVER => {
                    if cell.relay_cmd == RelayCommand::DATA {
                        self.received_data(cell.time, i);
                    } else if cell.relay_cmd == RelayCommand::SENDME {
                        self.received_sendme(cell.time, i);
                    }
                }
                Direction::PADDING => {
                    // Do nothing
                }
            }
        }

        self.into_rtt_estimates()
    }

    // Initial RTT estimate is: exit->client: CONNECTED --to-- client->exit: DATA
    fn sent_connected(&mut self, cell_time: f64, _cell_index: usize) {
        if self.primary_rtt.is_none() && self.first_connected.is_none() {
            self.first_connected = Some(PartialRttEstimate::new(cell_time));
        }
    }

    // The initial RTT can be estimated with the first ->DATA after the first <-CONNECTED.
    fn received_data(&mut self, cell_time: f64, cell_index: usize) {
        if self.primary_rtt.is_none() {
            if let Some(partial) = self.first_connected.take() {
                self.primary_rtt = Some(partial.into_rtt_estimate(cell_time, cell_index));
            }
        }
    }

    // Every 31 DATA cells sent by exit will trigger a SENDME from client.
    // 31 is the default value for cc_sendme_inc.
    // https://spec.torproject.org/proposals/324-rtt-congestion-control.html
    fn sent_data(&mut self, cell_time: f64, _cell_index: usize) {
        self.num_data_sent += 1;
        if self.num_data_sent % 31 == 0 {
            self.sendme_triggers
                .push_back(PartialRttEstimate::new(cell_time));
        }
    }

    // Subsequent estimates are from ->SENDME responses to every 31st <-DATA cell.
    fn received_sendme(&mut self, cell_time: f64, cell_index: usize) {
        if let Some(partial) = self.sendme_triggers.pop_front() {
            self.updated_rtts
                .push_back(partial.into_rtt_estimate(cell_time, cell_index));
        } else {
            log::warn!(
                "We just got a SENDME before we sent 31 DATAs; thus, we \
                will not use SENDME-based RTT estimation on this circuit.",
            );
            self.use_sendme_estimates = false;
        }
    }

    fn into_rtt_estimates(mut self) -> VecDeque<TimeEstimate> {
        let mut rtts = if self.use_sendme_estimates {
            self.updated_rtts
        } else {
            VecDeque::new()
        };

        if let Some(estimate) = self.primary_rtt.take() {
            rtts.push_front(estimate);
        }

        rtts
    }
}

#[cfg(test)]
mod tests {
    use crate::tests::CircuitBuilder;

    use super::*;

    #[test]
    fn basic_parse() {
        let rtt = 0.2;
        let circ = CircuitBuilder::build_basic(rtt);
        let est = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        assert_eq!(est.rtts.len(), 1);
        assert_eq!(est.rtt_min, Some(rtt));

        assert_eq!(est.rtts[0].time, rtt);
        assert_eq!(est.rtts[0].cell_index, 2);
    }

    #[test]
    fn basic_iter() {
        let rtt = 0.2;
        let circ = CircuitBuilder::build_basic(rtt);
        let est = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        let mut iter = est.iter_rtts();

        // The existing estimate applies to the first 3 cells
        for _ in 0..3 {
            assert_eq!(iter.next(), Some(est.rtts[0].clone()));
        }

        // The next cells would use later estimates
        assert_eq!(iter.next(), None);
    }

    #[test]
    fn basic_cycle() {
        let rtt = 0.2;
        let circ = CircuitBuilder::build_basic(rtt);
        let est = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        let mut cycle = est.iter_rtts().cycle();

        // Existing estimate is repeated forever
        for _ in 0..10 {
            assert_eq!(cycle.next(), Some(est.rtts[0].clone()));
        }
    }

    #[test]
    fn standard_parse() {
        let rtt = 0.2;
        let circ = CircuitBuilder::build_standard(rtt);
        let est = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        assert_eq!(est.rtts.len(), 4);
        assert_eq!(est.rtt_min, Some(rtt));

        assert_eq!(est.rtts[0].cell_index, 2);
        assert_eq!(est.rtts[1].cell_index, 36);
        assert_eq!(est.rtts[2].cell_index, 70);
        assert_eq!(est.rtts[3].cell_index, 104);

        assert_eq!(est.rtts[0].time, rtt);
        assert!(est.rtts[1].time > rtt);
        assert!(est.rtts[2].time > rtt);
        assert!(est.rtts[3].time > rtt);
    }

    #[test]
    fn standard_iter() {
        let rtt = 0.2;
        let circ = CircuitBuilder::build_standard(rtt);
        let est = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        let mut iter = est.iter_rtts();

        for _ in 0..3 {
            assert_eq!(iter.next(), Some(est.rtts[0].clone()));
        }
        for _ in 0..34 {
            assert_eq!(iter.next(), Some(est.rtts[1].clone()));
        }
        for _ in 0..34 {
            assert_eq!(iter.next(), Some(est.rtts[2].clone()));
        }
        for _ in 0..34 {
            assert_eq!(iter.next(), Some(est.rtts[3].clone()));
        }

        // The next cells would use later estimates
        assert_eq!(iter.next(), None);
    }

    #[test]
    fn standard_cycle() {
        let rtt = 0.2;
        let circ = CircuitBuilder::build_standard(rtt);
        let est = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        let mut cycle = est.iter_rtts().cycle();

        // Existing estimates are repeated forever
        for _ in 0..10 {
            for _ in 0..3 {
                assert_eq!(cycle.next(), Some(est.rtts[0].clone()));
            }
            for _ in 0..34 {
                assert_eq!(cycle.next(), Some(est.rtts[1].clone()));
            }
            for _ in 0..34 {
                assert_eq!(cycle.next(), Some(est.rtts[2].clone()));
            }
            for _ in 0..34 {
                assert_eq!(cycle.next(), Some(est.rtts[3].clone()));
            }
        }
    }

    #[test]
    fn iter_all_cells() {
        let rtt = 0.2;
        let circ = CircuitBuilder::build_standard_with_trailing_cells(rtt);
        let rest = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        let mut iter = rest.iter_rtts();

        for _ in 0..circ.len {
            // Every non-padding cell should have an appropriate estimate.
            // The tricky case here are the cells with an index greater than
            // the cell_index in which the final rtt estimate was taken.
            let est = iter.next();
            assert_ne!(est, None);
        }

        // Now we've gone though all cells so the iter is done.
        assert_eq!(iter.next(), None);
    }

    #[test]
    fn cycle_all_cells() {
        let rtt = 0.2;
        let circ = CircuitBuilder::build_standard_with_trailing_cells(rtt);
        let rest = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        let mut cycle = rest.iter_rtts().cycle();

        for _ in 0..circ.len {
            // Every non-padding cell should have an appropriate estimate.
            let est = cycle.next();
            assert_ne!(est, None);
        }

        // Now we've gone though all cells but cycle should continue.
        assert_ne!(cycle.next(), None);
    }

    #[test]
    fn iter_equals_cycle() {
        let rtt = 0.2;
        let circ = CircuitBuilder::build_standard_with_trailing_cells(rtt);
        let rest = RttEstimator::new(&circ.cells, circ.len as usize, SourcePosition::Exit);

        let mut cycle = rest.iter_rtts().cycle();

        for _ in 0..5 {
            let mut iter = rest.iter_rtts();

            for _ in 0..circ.len {
                // Every non-padding cell should have an appropriate estimate.
                // The tricky case here are the cells with an index greater than
                // the cell_index in which the final rtt estimate was taken.
                let iter_est = iter.next();
                assert_ne!(iter_est, None);

                let cycle_est = cycle.next();
                assert_ne!(cycle_est, None);

                // The estimates should be the same.
                assert_eq!(iter_est, cycle_est);
            }

            // Now we've gone though all cells so the iter is done.
            // But the cycle will start over from the beginning when we loop.
            assert_eq!(iter.next(), None);
        }
    }
}
