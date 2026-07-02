use cli::{Commands, LogLevel};
use env_logger::{Builder, Target};
use log::{self, LevelFilter};

pub mod cli;
mod index;
mod merge;
mod trace;
pub mod util;

fn main() -> anyhow::Result<()> {
    hdf5::filters::blosc_set_nthreads(16);

    let cli = cli::parse_cli();

    let level = match &cli.log_level {
        LogLevel::Debug => LevelFilter::Debug,
        LogLevel::Info => LevelFilter::Info,
        LogLevel::Warn => LevelFilter::Warn,
        LogLevel::Error => LevelFilter::Error,
        LogLevel::Off => LevelFilter::Off,
    };

    Builder::new()
        .target(Target::Stderr)
        .filter_level(level)
        .init();
    log::info!("Parsed CLI args and initialized logger!");

    log::info!(
        "Blosc is available {} num threads {}",
        hdf5::filters::blosc_available(),
        hdf5::filters::blosc_get_nthreads()
    );

    let result = match cli.command {
        Commands::Index(args) => {
            log::info!("Running index subcommand");
            index::run_index(&args)
        }
        Commands::Merge(args) => {
            log::info!("Running merge subcommand");
            merge::run_merge(&args)
        }
        Commands::Morph(args) => {
            log::info!("Running morph subcommand");
            trace::run_tracemorph(&args)
        }
        Commands::Move(args) => {
            log::info!("Running move subcommand");
            trace::run_tracemove(&args)
        }
    };

    if let Err(e) = &result {
        log::error!("Error occurred: {}", e);
        log::error!("Caused by: {}", e.root_cause());
    }
    log::info!("Returning cleanly from main");
    result
}
