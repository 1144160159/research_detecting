use anyhow::{bail, Context, Result};
use clap::Parser;
use serde_json::{json, Value};
use std::fs;
use std::io::{BufRead, BufReader, Write};
use std::net::{Shutdown, TcpListener, TcpStream};
use std::path::PathBuf;
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

const RAW_FEATURE_COUNT: usize = 38;

#[derive(Debug, Parser)]
#[command(about = "Measure reverse-worker recovery on the split HFT-MGBS deployment")]
struct Args {
    #[arg(long, default_value = "0.0.0.0:50053")]
    listen: String,
    #[arg(long)]
    output: PathBuf,
    #[arg(long, default_value_t = 300.0)]
    max_recovery_ms: f64,
    #[arg(long, default_value_t = 10_000)]
    accept_timeout_ms: u64,
    #[arg(long, default_value_t = 1_000)]
    io_timeout_ms: u64,
}

fn accept_until(listener: &TcpListener, timeout: Duration) -> Result<TcpStream> {
    let deadline = Instant::now() + timeout;
    loop {
        match listener.accept() {
            Ok((stream, _)) => return Ok(stream),
            Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => {
                if Instant::now() >= deadline {
                    bail!("timed out waiting for reverse worker");
                }
                thread::sleep(Duration::from_millis(1));
            }
            Err(error) => return Err(error).context("accept reverse worker"),
        }
    }
}

fn request(stream: &mut TcpStream, request_id: &str) -> Result<Duration> {
    let payload = json!({
        "schema_version": 1,
        "request_id": request_id,
        "candidate_id": "A09",
        "feature_encoding": "raw_v1",
        "prediction_encoding": "ordered_v1",
        "flows": [{"features": vec![0.0; RAW_FEATURE_COUNT]}],
    });
    let started = Instant::now();
    serde_json::to_writer(&mut *stream, &payload)?;
    stream.write_all(b"\n")?;
    stream.flush()?;
    let mut line = String::new();
    BufReader::new(stream.try_clone()?).read_line(&mut line)?;
    if line.is_empty() {
        bail!("reverse worker closed without a response");
    }
    let response: Value = serde_json::from_str(&line)?;
    if response.get("ok").and_then(Value::as_bool) != Some(true) {
        bail!(
            "reverse worker rejected probe: {}",
            response
                .get("error")
                .and_then(Value::as_str)
                .unwrap_or("unknown error")
        );
    }
    if response
        .get("predictions")
        .and_then(Value::as_array)
        .map(Vec::len)
        != Some(1)
    {
        bail!("reverse worker returned an incomplete prediction");
    }
    Ok(started.elapsed())
}

fn main() -> Result<()> {
    let args = Args::parse();
    if args.max_recovery_ms <= 0.0 {
        bail!("--max-recovery-ms must be positive");
    }
    let listener = TcpListener::bind(&args.listen)
        .with_context(|| format!("bind recovery probe listener {}", args.listen))?;
    listener.set_nonblocking(true)?;
    let io_timeout = Duration::from_millis(args.io_timeout_ms);

    let mut first = accept_until(&listener, Duration::from_millis(args.accept_timeout_ms))?;
    first.set_read_timeout(Some(io_timeout))?;
    first.set_write_timeout(Some(io_timeout))?;
    let baseline = request(&mut first, "split-recovery-baseline")?;

    let recovery_started = Instant::now();
    first.shutdown(Shutdown::Both)?;
    drop(first);

    let mut recovered = accept_until(&listener, Duration::from_millis(args.accept_timeout_ms))?;
    let reconnect = recovery_started.elapsed();
    recovered.set_read_timeout(Some(io_timeout))?;
    recovered.set_write_timeout(Some(io_timeout))?;
    let recovered_request = request(&mut recovered, "split-recovery-confirm")?;
    let recovery_to_success = recovery_started.elapsed();
    let recovery_ms = recovery_to_success.as_secs_f64() * 1_000.0;
    let passed = recovery_ms <= args.max_recovery_ms;
    let generated_unix_ms = SystemTime::now().duration_since(UNIX_EPOCH)?.as_millis();
    let report = json!({
        "schema_version": 1,
        "evidence_scope": "physical Rust listener to Python reverse worker recovery",
        "candidate_id": "A09",
        "listen": args.listen,
        "generated_unix_ms": generated_unix_ms,
        "baseline_round_trip_ms": baseline.as_secs_f64() * 1_000.0,
        "reconnect_ms": reconnect.as_secs_f64() * 1_000.0,
        "recovered_round_trip_ms": recovered_request.as_secs_f64() * 1_000.0,
        "recovery_to_success_ms": recovery_ms,
        "max_recovery_ms": args.max_recovery_ms,
        "passed": passed,
    });
    if let Some(parent) = args.output.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(&args.output, serde_json::to_vec_pretty(&report)?)?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    if !passed {
        bail!(
            "split recovery {:.3} ms exceeds {:.3} ms",
            recovery_ms,
            args.max_recovery_ms
        );
    }
    Ok(())
}
