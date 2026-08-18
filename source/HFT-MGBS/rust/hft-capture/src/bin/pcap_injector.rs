use anyhow::{bail, Context, Result};
use clap::Parser;
use probe_agent::capture::{Capturer, PcapReplayer, ReplaySpeed};
use serde::Serialize;
use std::borrow::Cow;
use std::ffi::CString;
use std::fs::File;
use std::io::Write;
use std::os::fd::RawFd;
use std::path::PathBuf;
use std::thread;
use std::time::{Duration, Instant};

const ETH_P_ALL: u16 = 0x0003;
const RATE_HEADROOM_RATIO: f64 = 1.01;

#[derive(Debug, Parser)]
#[command(about = "Bounded PCAP to AF_PACKET traffic generator for HFT live acceptance")]
struct Args {
    #[arg(long)]
    pcap: PathBuf,
    #[arg(long)]
    interface: String,
    #[arg(long)]
    duration_s: u64,
    #[arg(long, conflicts_with = "target_gbps")]
    target_mpps: Option<f64>,
    #[arg(long, conflicts_with = "target_mpps")]
    target_gbps: Option<f64>,
    #[arg(long)]
    output: PathBuf,
    #[arg(long, default_value = "physical_nic_live_replay")]
    evidence_scope: String,
}

#[derive(Serialize)]
struct InjectorReport {
    schema_version: u32,
    scope: String,
    interface: String,
    source: String,
    duration_s: f64,
    configured_target_mpps: Option<f64>,
    configured_target_gbps: Option<f64>,
    interface_mtu: usize,
    source_packets_read: u64,
    segmented_source_packets: u64,
    generated_tcp_segments: u64,
    rate_headroom_ratio: f64,
    offered_packets: u64,
    offered_bytes: u64,
    achieved_mpps: f64,
    achieved_gbps: f64,
    rate_window_s: f64,
    rate_sample_count: usize,
    observed_mpps_min_1s: Option<f64>,
    observed_gbps_min_1s: Option<f64>,
    send_would_block_retries: u64,
}

struct Socket(RawFd);

impl Drop for Socket {
    fn drop(&mut self) {
        unsafe {
            libc::close(self.0);
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();
    if args.duration_s == 0 {
        bail!("--duration-s must be positive");
    }
    if args.target_mpps.is_none() && args.target_gbps.is_none() {
        bail!("one of --target-mpps or --target-gbps is required");
    }
    if !matches!(
        args.evidence_scope.as_str(),
        "physical_nic_live_replay"
            | "physical_link_live_diagnostic"
            | "virtual_link_live_diagnostic"
    ) {
        bail!("unsupported --evidence-scope: {}", args.evidence_scope);
    }
    if args
        .target_mpps
        .is_some_and(|value| value <= 0.0 || !value.is_finite())
    {
        bail!("--target-mpps must be finite and positive");
    }
    if args
        .target_gbps
        .is_some_and(|value| value <= 0.0 || !value.is_finite())
    {
        bail!("--target-gbps must be finite and positive");
    }

    let socket = open_bound_socket(&args.interface)?;
    let interface_mtu = read_interface_mtu(&args.interface)?;
    let source = args
        .pcap
        .to_str()
        .context("PCAP path is not UTF-8")?
        .to_string();
    let mut replayer = PcapReplayer::new(&source, ReplaySpeed::MaxSpeed, true)?;
    replayer.start().await?;

    let started = Instant::now();
    let duration = Duration::from_secs(args.duration_s);
    let mut offered_packets = 0u64;
    let mut offered_bytes = 0u64;
    let mut source_packets_read = 0u64;
    let mut segmented_source_packets = 0u64;
    let mut generated_tcp_segments = 0u64;
    let mut would_block_retries = 0u64;
    let mut window_started = Instant::now();
    let mut window_packets = 0u64;
    let mut window_bytes = 0u64;
    let mut mpps_samples = Vec::new();
    let mut gbps_samples = Vec::new();
    while started.elapsed() < duration {
        let Some(batch) = replayer.poll()? else {
            continue;
        };
        let source_frames: Vec<&[u8]> = batch.iter().map(|(frame, _)| frame).collect();
        if source_frames.is_empty() {
            continue;
        }
        let mut expanded = Vec::with_capacity(source_frames.len());
        for frame in source_frames {
            source_packets_read += 1;
            match segment_oversize_ipv4_tcp(frame, interface_mtu)? {
                Some(segments) => {
                    segmented_source_packets += 1;
                    generated_tcp_segments += segments.len() as u64;
                    expanded.extend(segments.into_iter().map(Cow::Owned));
                }
                None => expanded.push(Cow::Borrowed(frame)),
            }
        }
        let frames: Vec<&[u8]> = expanded.iter().map(|frame| frame.as_ref()).collect();
        let outcome = send_batch(socket.0, &frames, started, duration)?;
        would_block_retries += outcome.retries;
        let sent_frames = &frames[..outcome.sent];
        offered_packets += sent_frames.len() as u64;
        let batch_bytes = sent_frames
            .iter()
            .map(|frame| frame.len() as u64)
            .sum::<u64>();
        offered_bytes += batch_bytes;
        window_packets += sent_frames.len() as u64;
        window_bytes += batch_bytes;
        if outcome.deadline_reached {
            break;
        }
        pace(
            started,
            offered_packets,
            offered_bytes,
            args.target_mpps,
            args.target_gbps,
        );
        let window_elapsed = window_started.elapsed();
        if window_elapsed >= Duration::from_secs(1) {
            let seconds = window_elapsed.as_secs_f64();
            mpps_samples.push(window_packets as f64 / seconds / 1_000_000.0);
            gbps_samples.push(window_bytes as f64 * 8.0 / seconds / 1_000_000_000.0);
            window_started = Instant::now();
            window_packets = 0;
            window_bytes = 0;
        }
    }
    replayer.stop().await?;
    if offered_packets == 0 {
        bail!("injector reached its deadline without sending a packet");
    }

    let elapsed = started.elapsed().as_secs_f64();
    let report = InjectorReport {
        schema_version: 1,
        scope: args.evidence_scope,
        interface: args.interface,
        source,
        duration_s: elapsed,
        configured_target_mpps: args.target_mpps,
        configured_target_gbps: args.target_gbps,
        interface_mtu,
        source_packets_read,
        segmented_source_packets,
        generated_tcp_segments,
        rate_headroom_ratio: RATE_HEADROOM_RATIO,
        offered_packets,
        offered_bytes,
        achieved_mpps: offered_packets as f64 / elapsed / 1_000_000.0,
        achieved_gbps: offered_bytes as f64 * 8.0 / elapsed / 1_000_000_000.0,
        rate_window_s: 1.0,
        rate_sample_count: mpps_samples.len(),
        observed_mpps_min_1s: mpps_samples.iter().copied().reduce(f64::min),
        observed_gbps_min_1s: gbps_samples.iter().copied().reduce(f64::min),
        send_would_block_retries: would_block_retries,
    };
    if let Some(parent) = args.output.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut output = File::create(&args.output)
        .with_context(|| format!("create injector report {}", args.output.display()))?;
    serde_json::to_writer_pretty(&mut output, &report)?;
    output.write_all(b"\n")?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}

fn read_interface_mtu(interface: &str) -> Result<usize> {
    let path = PathBuf::from("/sys/class/net").join(interface).join("mtu");
    let raw = std::fs::read_to_string(&path)
        .with_context(|| format!("read interface MTU {}", path.display()))?;
    let mtu = raw
        .trim()
        .parse::<usize>()
        .with_context(|| format!("parse interface MTU {}", path.display()))?;
    if mtu < 576 {
        bail!("interface MTU is unexpectedly small: {mtu}");
    }
    Ok(mtu)
}

fn segment_oversize_ipv4_tcp(frame: &[u8], mtu: usize) -> Result<Option<Vec<Vec<u8>>>> {
    if frame.len() < 14 {
        bail!("Ethernet frame is shorter than 14 bytes");
    }
    let mut ether_type = u16::from_be_bytes([frame[12], frame[13]]);
    let mut ip_offset = 14usize;
    while matches!(ether_type, 0x8100 | 0x88a8 | 0x9100) {
        if frame.len() < ip_offset + 4 {
            bail!("truncated VLAN Ethernet frame");
        }
        ether_type = u16::from_be_bytes([frame[ip_offset + 2], frame[ip_offset + 3]]);
        ip_offset += 4;
    }
    if ether_type != 0x0800 {
        if frame.len() <= mtu + ip_offset {
            return Ok(None);
        }
        bail!(
            "oversize non-IPv4 frame is unsupported: ethertype=0x{ether_type:04x} len={}",
            frame.len()
        );
    }
    if frame.len() < ip_offset + 20 {
        bail!("truncated IPv4 header");
    }
    let version_ihl = frame[ip_offset];
    if version_ihl >> 4 != 4 {
        bail!("invalid IPv4 version");
    }
    let ip_header_len = usize::from(version_ihl & 0x0f) * 4;
    if ip_header_len < 20 || frame.len() < ip_offset + ip_header_len {
        bail!("invalid IPv4 header length");
    }
    let ip_total_len = usize::from(u16::from_be_bytes([
        frame[ip_offset + 2],
        frame[ip_offset + 3],
    ]));
    if ip_total_len < ip_header_len || frame.len() < ip_offset + ip_total_len {
        bail!("invalid or truncated IPv4 total length");
    }
    if ip_total_len <= mtu {
        return Ok(None);
    }
    if frame[ip_offset + 9] != 6 {
        bail!(
            "oversize IPv4 non-TCP packet is unsupported: protocol={} ip_len={ip_total_len}",
            frame[ip_offset + 9]
        );
    }
    let fragment = u16::from_be_bytes([frame[ip_offset + 6], frame[ip_offset + 7]]);
    if fragment & 0x3fff != 0 {
        bail!("oversize fragmented IPv4 packet is unsupported");
    }
    let tcp_offset = ip_offset + ip_header_len;
    if frame.len() < tcp_offset + 20 {
        bail!("truncated TCP header");
    }
    let tcp_header_len = usize::from(frame[tcp_offset + 12] >> 4) * 4;
    if tcp_header_len < 20 || tcp_offset + tcp_header_len > ip_offset + ip_total_len {
        bail!("invalid TCP header length");
    }
    let header_len = ip_header_len + tcp_header_len;
    if mtu <= header_len {
        bail!("interface MTU cannot hold IPv4 and TCP headers");
    }
    let payload_offset = tcp_offset + tcp_header_len;
    let payload_end = ip_offset + ip_total_len;
    let payload = &frame[payload_offset..payload_end];
    if payload.is_empty() {
        bail!("oversize TCP packet has no segmentable payload");
    }
    let maximum_payload = mtu - header_len;
    let base_sequence = u32::from_be_bytes([
        frame[tcp_offset + 4],
        frame[tcp_offset + 5],
        frame[tcp_offset + 6],
        frame[tcp_offset + 7],
    ]);
    let base_identification = u16::from_be_bytes([frame[ip_offset + 4], frame[ip_offset + 5]]);
    let mut segments = Vec::with_capacity(payload.len().div_ceil(maximum_payload));
    for (segment_index, chunk) in payload.chunks(maximum_payload).enumerate() {
        let mut segment = Vec::with_capacity(ip_offset + header_len + chunk.len());
        segment.extend_from_slice(&frame[..payload_offset]);
        segment.extend_from_slice(chunk);
        let segment_ip_len = header_len + chunk.len();
        segment[ip_offset + 2..ip_offset + 4]
            .copy_from_slice(&(segment_ip_len as u16).to_be_bytes());
        segment[ip_offset + 4..ip_offset + 6].copy_from_slice(
            &base_identification
                .wrapping_add(segment_index as u16)
                .to_be_bytes(),
        );
        let sequence = base_sequence.wrapping_add((segment_index * maximum_payload) as u32);
        segment[tcp_offset + 4..tcp_offset + 8].copy_from_slice(&sequence.to_be_bytes());
        if segment_index + 1 < payload.len().div_ceil(maximum_payload) {
            segment[tcp_offset + 13] &= !(0x01 | 0x08);
        }
        segment[ip_offset + 10..ip_offset + 12].fill(0);
        let ip_checksum = internet_checksum(&segment[ip_offset..ip_offset + ip_header_len]);
        segment[ip_offset + 10..ip_offset + 12].copy_from_slice(&ip_checksum.to_be_bytes());
        segment[tcp_offset + 16..tcp_offset + 18].fill(0);
        let tcp_checksum = ipv4_tcp_checksum(
            &segment[ip_offset..ip_offset + ip_header_len],
            &segment[tcp_offset..ip_offset + segment_ip_len],
        );
        segment[tcp_offset + 16..tcp_offset + 18].copy_from_slice(&tcp_checksum.to_be_bytes());
        segments.push(segment);
    }
    Ok(Some(segments))
}

fn internet_checksum(bytes: &[u8]) -> u16 {
    let mut sum = 0u32;
    let mut chunks = bytes.chunks_exact(2);
    for chunk in &mut chunks {
        sum += u32::from(u16::from_be_bytes([chunk[0], chunk[1]]));
    }
    if let Some(last) = chunks.remainder().first() {
        sum += u32::from(*last) << 8;
    }
    while sum >> 16 != 0 {
        sum = (sum & 0xffff) + (sum >> 16);
    }
    !(sum as u16)
}

fn ipv4_tcp_checksum(ip_header: &[u8], tcp_segment: &[u8]) -> u16 {
    let mut pseudo_header = Vec::with_capacity(12 + tcp_segment.len());
    pseudo_header.extend_from_slice(&ip_header[12..20]);
    pseudo_header.push(0);
    pseudo_header.push(6);
    pseudo_header.extend_from_slice(&(tcp_segment.len() as u16).to_be_bytes());
    pseudo_header.extend_from_slice(tcp_segment);
    internet_checksum(&pseudo_header)
}

fn open_bound_socket(interface: &str) -> Result<Socket> {
    let name = CString::new(interface).context("interface contains a NUL byte")?;
    let ifindex = unsafe { libc::if_nametoindex(name.as_ptr()) };
    if ifindex == 0 {
        return Err(std::io::Error::last_os_error())
            .with_context(|| format!("resolve interface {interface}"));
    }
    let fd = unsafe {
        libc::socket(
            libc::AF_PACKET,
            libc::SOCK_RAW | libc::SOCK_NONBLOCK,
            ETH_P_ALL.to_be() as i32,
        )
    };
    if fd < 0 {
        return Err(std::io::Error::last_os_error()).context("create AF_PACKET transmit socket");
    }
    let socket = Socket(fd);
    let mut address: libc::sockaddr_ll = unsafe { std::mem::zeroed() };
    address.sll_family = libc::AF_PACKET as u16;
    address.sll_protocol = ETH_P_ALL.to_be();
    address.sll_ifindex = ifindex as i32;
    let result = unsafe {
        libc::bind(
            socket.0,
            &address as *const libc::sockaddr_ll as *const libc::sockaddr,
            std::mem::size_of::<libc::sockaddr_ll>() as libc::socklen_t,
        )
    };
    if result < 0 {
        return Err(std::io::Error::last_os_error())
            .with_context(|| format!("bind AF_PACKET transmit socket to {interface}"));
    }
    Ok(socket)
}

#[derive(Debug, Eq, PartialEq)]
struct SendOutcome {
    sent: usize,
    retries: u64,
    deadline_reached: bool,
}

fn send_batch(
    fd: RawFd,
    frames: &[&[u8]],
    started: Instant,
    duration: Duration,
) -> Result<SendOutcome> {
    let mut iovecs: Vec<libc::iovec> = frames
        .iter()
        .map(|frame| libc::iovec {
            iov_base: frame.as_ptr() as *mut libc::c_void,
            iov_len: frame.len(),
        })
        .collect();
    let mut messages: Vec<libc::mmsghdr> = iovecs
        .iter_mut()
        .map(|iovec| {
            let mut message: libc::mmsghdr = unsafe { std::mem::zeroed() };
            message.msg_hdr.msg_iov = iovec;
            message.msg_hdr.msg_iovlen = 1;
            message
        })
        .collect();
    let mut sent = 0usize;
    let mut retries = 0u64;
    while sent < messages.len() {
        if started.elapsed() >= duration {
            return Ok(SendOutcome {
                sent,
                retries,
                deadline_reached: true,
            });
        }
        let count = unsafe {
            libc::sendmmsg(
                fd,
                messages[sent..].as_mut_ptr(),
                (messages.len() - sent) as u32,
                libc::MSG_DONTWAIT,
            )
        };
        if count > 0 {
            sent += count as usize;
            continue;
        }
        let error = std::io::Error::last_os_error();
        if matches!(
            error.kind(),
            std::io::ErrorKind::WouldBlock | std::io::ErrorKind::TimedOut
        ) {
            retries += 1;
            thread::sleep(Duration::from_micros(50));
            continue;
        }
        return Err(error).context("sendmmsg failed");
    }
    Ok(SendOutcome {
        sent,
        retries,
        deadline_reached: false,
    })
}

fn pace(
    started: Instant,
    packets: u64,
    bytes: u64,
    target_mpps: Option<f64>,
    target_gbps: Option<f64>,
) {
    let target_elapsed = if let Some(mpps) = target_mpps {
        packets as f64 / (mpps * RATE_HEADROOM_RATIO * 1_000_000.0)
    } else {
        bytes as f64 * 8.0 / (target_gbps.unwrap_or(1.0) * RATE_HEADROOM_RATIO * 1_000_000_000.0)
    };
    let actual_elapsed = started.elapsed().as_secs_f64();
    if target_elapsed > actual_elapsed {
        thread::sleep(Duration::from_secs_f64(target_elapsed - actual_elapsed));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tcp_frame(payload_len: usize) -> Vec<u8> {
        let ip_offset = 14usize;
        let tcp_offset = ip_offset + 20;
        let mut frame = vec![0u8; tcp_offset + 20 + payload_len];
        frame[0..6].fill(0x11);
        frame[6..12].fill(0x22);
        frame[12..14].copy_from_slice(&0x0800u16.to_be_bytes());
        frame[ip_offset] = 0x45;
        frame[ip_offset + 2..ip_offset + 4]
            .copy_from_slice(&((40 + payload_len) as u16).to_be_bytes());
        frame[ip_offset + 4..ip_offset + 6].copy_from_slice(&7u16.to_be_bytes());
        frame[ip_offset + 6..ip_offset + 8].copy_from_slice(&0x4000u16.to_be_bytes());
        frame[ip_offset + 8] = 64;
        frame[ip_offset + 9] = 6;
        frame[ip_offset + 12..ip_offset + 16].copy_from_slice(&[192, 0, 2, 1]);
        frame[ip_offset + 16..ip_offset + 20].copy_from_slice(&[198, 51, 100, 2]);
        frame[tcp_offset..tcp_offset + 2].copy_from_slice(&443u16.to_be_bytes());
        frame[tcp_offset + 2..tcp_offset + 4].copy_from_slice(&50000u16.to_be_bytes());
        frame[tcp_offset + 4..tcp_offset + 8].copy_from_slice(&1000u32.to_be_bytes());
        frame[tcp_offset + 8..tcp_offset + 12].copy_from_slice(&2000u32.to_be_bytes());
        frame[tcp_offset + 12] = 5 << 4;
        frame[tcp_offset + 13] = 0x19;
        frame[tcp_offset + 14..tcp_offset + 16].copy_from_slice(&65535u16.to_be_bytes());
        for (index, byte) in frame[tcp_offset + 20..].iter_mut().enumerate() {
            *byte = (index % 251) as u8;
        }
        frame[ip_offset + 10..ip_offset + 12].fill(0);
        let ip_checksum = internet_checksum(&frame[ip_offset..ip_offset + 20]);
        frame[ip_offset + 10..ip_offset + 12].copy_from_slice(&ip_checksum.to_be_bytes());
        let tcp_checksum =
            ipv4_tcp_checksum(&frame[ip_offset..ip_offset + 20], &frame[tcp_offset..]);
        frame[tcp_offset + 16..tcp_offset + 18].copy_from_slice(&tcp_checksum.to_be_bytes());
        frame
    }

    #[test]
    fn expired_batch_reports_partial_boundary_without_socket_error() {
        let frame = [0u8; 64];
        let started = Instant::now() - Duration::from_secs(2);
        let outcome = send_batch(-1, &[frame.as_slice()], started, Duration::from_secs(1)).unwrap();

        assert_eq!(
            outcome,
            SendOutcome {
                sent: 0,
                retries: 0,
                deadline_reached: true,
            }
        );
    }

    #[test]
    fn gro_tcp_frame_is_segmented_to_interface_mtu() {
        let segments = segment_oversize_ipv4_tcp(&tcp_frame(3000), 1500)
            .expect("segmentation should succeed")
            .expect("frame should be segmented");

        assert_eq!(segments.len(), 3);
        assert!(segments.iter().all(|segment| segment.len() <= 1514));
        let sequences: Vec<u32> = segments
            .iter()
            .map(|segment| u32::from_be_bytes([segment[38], segment[39], segment[40], segment[41]]))
            .collect();
        assert_eq!(sequences, vec![1000, 2460, 3920]);
        assert_eq!(segments[0][47] & 0x09, 0);
        assert_eq!(segments[1][47] & 0x09, 0);
        assert_eq!(segments[2][47] & 0x09, 0x09);
        for segment in segments {
            let ip_total_len = usize::from(u16::from_be_bytes([segment[16], segment[17]]));
            assert_eq!(internet_checksum(&segment[14..34]), 0);
            assert_eq!(
                ipv4_tcp_checksum(&segment[14..34], &segment[34..14 + ip_total_len],),
                0
            );
        }
    }

    #[test]
    fn frame_within_mtu_is_not_rewritten() {
        assert!(segment_oversize_ipv4_tcp(&tcp_frame(100), 1500)
            .expect("frame should be valid")
            .is_none());
    }
}
