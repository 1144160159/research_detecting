use std::{num::NonZeroUsize, path::PathBuf};

use cellshift::{DestinationPosition, SourcePosition, TimeUnit};
use clap::{Args, Parser, Subcommand, ValueEnum};

#[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ValueEnum)]
pub enum LogLevel {
    Debug,
    Info,
    Warn,
    Error,
    Off,
}

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
/// Transduce and augment Tor cell traces in the GTT23::Circuit format.
pub struct Cli {
    /// The level at which to filter log messages.
    #[arg(
        short,
        long,
        value_enum,
        global = true,
        value_name = "LEVEL",
        default_value = "info"
    )]
    pub log_level: LogLevel,
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
/// Holds the supported subcommands and their args.
pub enum Commands {
    /// Runs TraceMove to produce a new database of transduced circuits
    Move(MoveArgs),
    /// Runs TraceMorph to produce a new database of transduced+augmented circuits
    Morph(MorphArgs),
    /// Merge multiple circuit databases into a new database
    Merge(MergeArgs),
    /// Write an index into a circuit database
    Index(IndexArgs),
}

#[derive(Args)]
pub struct IoArgs {
    /// Input path to an HDF5 database of GTT23::Circuits targeted for shifting
    #[arg(value_name = "IN_DB_PATH", required = true)]
    pub input: PathBuf,
    /// Output path to write an HDF5 file of shifted GTT23::AugmentedCircuits
    #[arg(value_name = "OUT_DB_PATH", required = true)]
    pub output: PathBuf,
    /// Read circuits from input database in chunks to improve performance
    #[arg(short, long, value_name = "NUM", default_value = "1000")]
    pub read_slice_len: NonZeroUsize,
    /// When writing, compress chunks in the output dataset.
    #[arg(short, long)]
    pub compress: bool,
}

#[derive(Args)]
pub struct FilterArgs {
    /// Consider only circuits with at least this many cells
    #[arg(short, long, value_name = "NUM")]
    pub min_length: Option<u16>,
    /// Consider only circuits from the specified timeframe
    #[arg(short = 'v', long, value_name = "NUM,NUM,...", value_delimiter = ',')]
    pub time_vals: Option<Vec<u8>>,
    /// The unit of time used to interpret the time-vals
    #[arg(
        short = 'u',
        long,
        value_enum,
        value_name = "UNIT",
        default_value = "week"
    )]
    pub time_unit: TimeUnit,
}

#[derive(Args)]
pub struct PositionArgs {
    /// The vantage point in which circuits in the input DB were observed
    #[arg(
        short,
        long,
        value_enum,
        value_name = "POSITION",
        default_value = "exit"
    )]
    pub source: SourcePosition,
    /// The vantage point into which circuits should be transduced
    #[arg(
        short,
        long,
        value_enum,
        value_name = "POSITION",
        default_value = "entry"
    )]
    pub destination: DestinationPosition,
}

#[derive(Args)]
pub struct MoveArgs {
    #[command(flatten)]
    pub io: IoArgs,
    #[command(flatten)]
    pub filter: FilterArgs,
    #[command(flatten)]
    pub position: PositionArgs,
}

#[derive(Args)]
pub struct MorphArgs {
    #[command(flatten)]
    pub base: MoveArgs,
    /// Number of transduced+augmented circuits to produce for each input circuit
    #[arg(value_parser = clap::value_parser!(u16).range(1..))]
    pub aug_factor: u16,
    /// Path to an HDF5 database of GTT23::Circuits used to train the latency and
    /// congestion distributions (if None, train directly on IN_DB_PATH)
    #[arg(short, long, value_name = "TRAIN_DB_PATH")]
    pub train: Option<PathBuf>,
    /// Use a specified seed for deterministic augmentation
    #[arg(short = 'z', long, value_name = "NUM")]
    pub seed: Option<u64>,
}

#[derive(Args)]
pub struct MergeArgs {
    /// Output path to write an HDF5 file of GTT23::AugmentedCircuits
    #[arg(value_name = "OUT_DB_PATH", required = true)]
    pub output: PathBuf,
    /// Input paths to one or more HDF5 databases of GTT23::AugmentedCircuits
    #[arg(value_name = "IN_DB_PATH", value_parser, num_args = 1.., value_delimiter = ' ')]
    pub databases: Vec<PathBuf>,
    /// Read/write circuits in chunks to improve performance
    #[arg(short, long, value_name = "NUM", default_value = "1000")]
    pub rw_slice_len: NonZeroUsize,
    /// When writing, compress chunks in the output dataset.
    #[arg(short, long)]
    pub compress: bool,
}

#[derive(Args)]
pub struct IndexArgs {
    /// Input paths to an HDF5 database of GTT23::AugmentedCircuits into which we will write the index
    #[arg(value_name = "IN_DB_PATH", required = true)]
    pub input: PathBuf,
}

pub fn parse_cli() -> Cli {
    Cli::parse()
}
