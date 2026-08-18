use anyhow::{Context, Result};
use clap::Parser;
use hft_capture::capture_runtime_decision::{
    decision_exit_code, evaluate_runtime_decision, parse_rfc3339_millis, RuntimeObservation,
    RuntimePolicy,
};
use std::fs::File;
use std::io::{BufReader, Write};
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Parser)]
#[command(about = "Non-mutating XDP-primary/DPDK-fallback runtime decision")]
struct Args {
    #[arg(long)]
    policy: PathBuf,
    #[arg(long)]
    observation: PathBuf,
    #[arg(long)]
    output: Option<PathBuf>,
    #[arg(long)]
    now_utc: Option<String>,
}

fn read_json<T: serde::de::DeserializeOwned>(path: &Path) -> Result<T> {
    let file = File::open(path).with_context(|| format!("open {}", path.display()))?;
    serde_json::from_reader(BufReader::new(file))
        .with_context(|| format!("parse strict JSON {}", path.display()))
}

fn now_millis(value: Option<&str>) -> Result<i64> {
    if let Some(value) = value {
        return parse_rfc3339_millis(value).map_err(anyhow::Error::msg);
    }
    let elapsed = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .context("system clock precedes Unix epoch")?;
    i64::try_from(elapsed.as_millis()).context("current time exceeds i64 milliseconds")
}

fn write_output(path: Option<&Path>, bytes: &[u8]) -> Result<()> {
    if let Some(path) = path {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)
                .with_context(|| format!("create output directory {}", parent.display()))?;
        }
        let temporary = path.with_extension("tmp");
        let mut file =
            File::create(&temporary).with_context(|| format!("create {}", temporary.display()))?;
        file.write_all(bytes)?;
        file.sync_all()?;
        std::fs::rename(&temporary, path).with_context(|| format!("replace {}", path.display()))?;
    } else {
        std::io::stdout().write_all(bytes)?;
    }
    Ok(())
}

fn run(args: &Args) -> Result<i32> {
    let policy: RuntimePolicy = read_json(&args.policy)?;
    let observation: RuntimeObservation = read_json(&args.observation)?;
    let decision =
        evaluate_runtime_decision(&policy, &observation, now_millis(args.now_utc.as_deref())?)
            .map_err(anyhow::Error::msg)?;
    let mut output = serde_json::to_vec_pretty(&decision)?;
    output.push(b'\n');
    write_output(args.output.as_deref(), &output)?;
    Ok(decision_exit_code(&decision))
}

fn main() {
    let args = Args::parse();
    match run(&args) {
        Ok(code) => std::process::exit(code),
        Err(error) => {
            eprintln!("capture runtime decision contract error: {error:#}");
            std::process::exit(2);
        }
    }
}
