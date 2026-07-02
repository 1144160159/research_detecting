use clap::ValueEnum;

pub mod data;
pub mod rtt;
pub mod shift;

#[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ValueEnum)]
pub enum TimeUnit {
    Day,
    Week,
}

#[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ValueEnum)]
pub enum SourcePosition {
    Client,
    Exit,
}

#[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ValueEnum)]
pub enum DestinationPosition {
    ISP,
    Entry,
}

pub fn round_micro_res(time: f64) -> f64 {
    (time * 1_000_000.0).round() / 1_000_000.0
}

#[cfg(test)]
pub mod tests {
    use gtt23::{Cell, CellCommand, Circuit, Direction, RelayCommand};

    pub struct CircuitBuilder {
        circ: Circuit,
        cur_time: f64,
    }

    impl Default for CircuitBuilder {
        fn default() -> Self {
            Self::new()
        }
    }

    impl CircuitBuilder {
        pub fn new() -> Self {
            Self {
                circ: Circuit::empty(),
                cur_time: 0.000001,
            }
        }

        pub fn add_cell(&mut self, direction: Direction, relay_cmd: RelayCommand) {
            self.circ.cells[self.circ.len as usize] = Cell {
                time: self.cur_time,
                direction,
                cell_cmd: CellCommand::RELAY,
                relay_cmd,
            };
            self.circ.len += 1;
        }

        pub fn add_time(&mut self, duration: f64) {
            self.cur_time += duration;
            self.cur_time = crate::round_micro_res(self.cur_time);
        }

        pub fn build_basic(rtt: f64) -> Circuit {
            let mut builder = CircuitBuilder::new();
            builder.add_time(rtt);
            builder.add_cell(Direction::CLIENT_TO_SERVER, RelayCommand::BEGIN);
            builder.add_time(0.01);
            builder.add_cell(Direction::SERVER_TO_CLIENT, RelayCommand::CONNECTED);
            builder.add_time(rtt);
            builder.add_cell(Direction::CLIENT_TO_SERVER, RelayCommand::DATA);
            builder.into()
        }

        pub fn build_standard(rtt: f64) -> Circuit {
            let latency = 0.01;
            let congestion_small = 0.25;
            let congestion_large = 0.5;
            let mut builder = CircuitBuilder::from(Self::build_basic(rtt));

            for _ in 0..3 {
                builder.add_time(latency);
                for _ in 0..10 {
                    builder.add_cell(Direction::SERVER_TO_CLIENT, RelayCommand::DATA);
                }
                builder.add_time(rtt + congestion_small);
                builder.add_cell(Direction::CLIENT_TO_SERVER, RelayCommand::DATA);
                for _ in 0..10 {
                    builder.add_time(latency);
                    builder.add_cell(Direction::SERVER_TO_CLIENT, RelayCommand::DATA);
                }
                builder.add_time(latency);
                builder.add_cell(Direction::CLIENT_TO_SERVER, RelayCommand::DATA);
                for _ in 0..11 {
                    builder.add_time(latency);
                    builder.add_cell(Direction::SERVER_TO_CLIENT, RelayCommand::DATA);
                }
                builder.add_time(rtt + congestion_large);
                builder.add_cell(Direction::CLIENT_TO_SERVER, RelayCommand::SENDME);
            }

            builder.into()
        }

        pub fn build_standard_with_trailing_cells(rtt: f64) -> Circuit {
            let latency = 0.01;
            let mut builder = CircuitBuilder::from(Self::build_basic(rtt));
            builder.add_time(latency);
            for _ in 0..10 {
                builder.add_cell(Direction::SERVER_TO_CLIENT, RelayCommand::DATA);
            }
            builder.into()
        }
    }

    impl From<Circuit> for CircuitBuilder {
        fn from(circ: Circuit) -> Self {
            Self {
                circ,
                cur_time: circ.cells[(circ.len as usize).saturating_sub(1)].time,
            }
        }
    }

    impl From<CircuitBuilder> for Circuit {
        fn from(builder: CircuitBuilder) -> Self {
            builder.circ
        }
    }
}
