use std::io::{BufRead, BufReader};
use std::path::PathBuf;

use indicatif::{ProgressBar, ProgressStyle};
use zstd::stream::read::Decoder;

use crate::cli::FilterArgs;
use cellshift::TimeUnit;

pub fn open_input_stream(path: &PathBuf) -> anyhow::Result<Box<dyn BufRead>> {
    // Open the file in read-only mode with buffer.
    let file = std::fs::File::open(path)?;

    // Check if we have a zstd-compressed file.
    let use_zstd = if let Some(ext) = path.extension() {
        ext == "zst"
    } else {
        false
    };

    // Run an inline zstd::Decoder if the file is compressed.
    let data_stream: Box<dyn BufRead> = if use_zstd {
        Box::new(BufReader::new(Decoder::new(file)?))
    } else {
        Box::new(BufReader::new(file))
    };

    Ok(data_stream)
}

pub fn days_from_weeks(weeks: &[u8]) -> Vec<u8> {
    // GTT23 uses 1-indexing and represents days with a u8. So we match week 0
    // with day 0, but otherwise each day can be mapped to a single week.
    let mut days = vec![];
    for day in 0..=u8::MAX {
        let week = if day == 0 { 0 } else { ((day - 1) / 7) + 1 };
        if weeks.contains(&week) {
            days.push(day);
        }
    }
    days
}

pub fn get_days_filter(filter: &FilterArgs) -> Option<Vec<u8>> {
    // Handle the timeframe filter conversion if needed.
    match filter.time_unit {
        TimeUnit::Day => filter.time_vals.clone(),
        TimeUnit::Week => filter.time_vals.as_ref().map(|x| days_from_weeks(&x[..])),
    }
}

fn pb_style() -> ProgressStyle {
    ProgressStyle::with_template(
        "{msg}: {wide_bar:.green} {pos}/{len} ({percent}%) [{elapsed_precise} (eta {eta_precise})]",
    )
    .unwrap_or(ProgressStyle::default_bar())
}

pub fn pb_new(count: usize, message: String) -> ProgressBar {
    ProgressBar::new(count as u64)
        .with_message(message)
        .with_style(pb_style())
}

#[cfg(test)]
pub mod tests {
    use super::*;

    #[test]
    fn week_to_day_conversion() {
        assert_eq!(days_from_weeks(&[0]), vec![0]);
        assert_eq!(days_from_weeks(&[1]), vec![1, 2, 3, 4, 5, 6, 7]);
        assert_eq!(days_from_weeks(&[1, 1]), vec![1, 2, 3, 4, 5, 6, 7]);
        assert_eq!(days_from_weeks(&[0, 1]), vec![0, 1, 2, 3, 4, 5, 6, 7]);
        assert_eq!(days_from_weeks(&[2]), vec![8, 9, 10, 11, 12, 13, 14]);
        assert_eq!(
            days_from_weeks(&[1, 2]),
            vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        );
        assert_eq!(
            days_from_weeks(&[36]),
            vec![246, 247, 248, 249, 250, 251, 252]
        );
        assert_eq!(days_from_weeks(&[37]), vec![253, 254, 255]);
    }
}
