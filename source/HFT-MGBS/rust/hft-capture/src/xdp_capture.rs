//! HFT-owned AF_XDP adapter.
//!
//! The upstream capture crate is consumed read-only. This adapter fixes two
//! deployment blockers locally: all active RX queues are registered, and
//! frames still owned by the kernel fill/RX rings are reclaimed after the
//! XSK sockets have been closed.

use anyhow::{bail, Context, Result};
use aya::maps::XskMap;
use aya::programs::{Xdp, XdpFlags};
use aya::Bpf;
use probe_agent::capture::xdp_sys::{XDP_COPY, XDP_ZEROCOPY};
use probe_agent::capture::{
    CaptureStats, CaptureTimestamp, CaptureTimestampProvenance, Capturer, PacketBatch,
    PromiscuousMode, Umem, UmemConfig, XdpDesc, XskSocket, XskSocketConfig,
};
use std::ffi::CString;
use std::path::PathBuf;
use std::process::Command;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

const MAX_XSK_BATCH_SIZE: usize = 256;
const XSK_RING_SIZE: u32 = 2048;
type OwnedPacket = (Vec<u8>, CaptureTimestamp);
type OwnedReceiveBatch = (Vec<OwnedPacket>, u64);

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum HftXdpMode {
    Native,
    Skb,
}

impl HftXdpMode {
    fn attach_flags(self) -> XdpFlags {
        match self {
            Self::Native => XdpFlags::DRV_MODE,
            Self::Skb => XdpFlags::SKB_MODE,
        }
    }

    fn bind_flags(self) -> u16 {
        match self {
            Self::Native => XDP_ZEROCOPY,
            Self::Skb => XDP_COPY,
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::Native => "native",
            Self::Skb => "skb",
        }
    }
}

struct QueueState {
    queue_id: u32,
    umem: Arc<Umem>,
    socket: Option<XskSocket>,
    kernel_owned_frames: Vec<bool>,
    receive_descriptors: Vec<XdpDesc>,
}

pub struct HftXdpCapture {
    interface: String,
    ifindex: u32,
    mode: HftXdpMode,
    queue_count: u32,
    frames_per_queue: usize,
    receive_batch_size: usize,
    ebpf_object: PathBuf,
    realtime_minus_monotonic_ns: i128,
    queues: Vec<QueueState>,
    bpf: Option<Bpf>,
    promisc_guard: Option<PromiscuousMode>,
    stats: CaptureStats,
    running: bool,
    next_queue: usize,
    diagnostic_fail_after_packets: Option<u64>,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct BorrowedPollStats {
    pub packets: usize,
    pub bytes: u64,
}

pub struct HftXdpQueueWorker {
    queue: Option<QueueState>,
    realtime_minus_monotonic_ns: i128,
    receive_batch_size: usize,
    packets: u64,
    bytes: u64,
}

// QueueState owns its socket and UMEM mappings exclusively. Moving that
// ownership to exactly one worker thread does not introduce shared ring access.
unsafe impl Send for HftXdpQueueWorker {}

impl HftXdpQueueWorker {
    pub fn queue_id(&self) -> u32 {
        self.queue
            .as_ref()
            .map(|queue| queue.queue_id)
            .unwrap_or(u32::MAX)
    }

    pub fn packets(&self) -> u64 {
        self.packets
    }

    pub fn bytes(&self) -> u64 {
        self.bytes
    }

    pub fn poll_borrowed<F>(&mut self, mut visitor: F) -> Result<BorrowedPollStats>
    where
        F: FnMut(u32, &[u8], u64) -> Result<()>,
    {
        self.poll_borrowed_with_idle_wait(&mut visitor, Some(1))
    }

    pub fn poll_borrowed_busy<F>(&mut self, mut visitor: F) -> Result<BorrowedPollStats>
    where
        F: FnMut(u32, &[u8], u64) -> Result<()>,
    {
        self.poll_borrowed_with_idle_wait(&mut visitor, None)
    }

    fn poll_borrowed_with_idle_wait<F>(
        &mut self,
        visitor: &mut F,
        idle_poll_timeout_ms: Option<i32>,
    ) -> Result<BorrowedPollStats>
    where
        F: FnMut(u32, &[u8], u64) -> Result<()>,
    {
        let queue = self.queue.as_mut().context("XDP queue worker is empty")?;
        let mut result = BorrowedPollStats::default();
        if let Some((packets, bytes)) = HftXdpCapture::receive_from_queue_with(
            queue,
            self.realtime_minus_monotonic_ns,
            self.receive_batch_size,
            visitor,
        )? {
            result.packets = packets;
            result.bytes = bytes;
            HftXdpCapture::refill(queue, self.receive_batch_size);
            self.packets = self.packets.saturating_add(packets as u64);
            self.bytes = self.bytes.saturating_add(bytes);
        } else {
            HftXdpCapture::refill(queue, self.receive_batch_size);
            if let Some(timeout_ms) = idle_poll_timeout_ms {
                if let Some(socket) = queue.socket.as_ref() {
                    let _ = socket.poll(timeout_ms)?;
                }
            } else {
                std::hint::spin_loop();
            }
        }
        Ok(result)
    }

    fn into_queue(mut self) -> QueueState {
        self.queue.take().expect("XDP queue worker is empty")
    }
}

impl Drop for HftXdpQueueWorker {
    fn drop(&mut self) {
        if let Some(queue) = self.queue.as_mut() {
            HftXdpCapture::cleanup_queue(queue);
        }
    }
}

impl HftXdpCapture {
    pub fn new(
        interface: String,
        mode: HftXdpMode,
        requested_queue_count: u32,
        frames_per_queue: usize,
        receive_batch_size: usize,
        ebpf_object: PathBuf,
        diagnostic_fail_after_packets: Option<u64>,
    ) -> Result<Self> {
        if frames_per_queue < XSK_RING_SIZE as usize {
            bail!(
                "xdp frames per queue must be at least {}, got {}",
                XSK_RING_SIZE,
                frames_per_queue
            );
        }
        if !(1..=MAX_XSK_BATCH_SIZE).contains(&receive_batch_size)
            || !receive_batch_size.is_power_of_two()
        {
            bail!(
                "xdp receive batch size must be a power of two in 1..={}, got {}",
                MAX_XSK_BATCH_SIZE,
                receive_batch_size
            );
        }
        let name = CString::new(interface.as_str()).context("interface contains a NUL byte")?;
        let ifindex = unsafe { libc::if_nametoindex(name.as_ptr()) };
        if ifindex == 0 {
            return Err(std::io::Error::last_os_error())
                .with_context(|| format!("resolve interface {interface}"));
        }
        let queue_count = if requested_queue_count == 0 {
            active_combined_queue_count(&interface)?
        } else {
            requested_queue_count
        };
        if queue_count == 0 || queue_count > 64 {
            bail!("xdp queue count must be in 1..=64, got {}", queue_count);
        }
        Ok(Self {
            interface,
            ifindex,
            mode,
            queue_count,
            frames_per_queue,
            receive_batch_size,
            ebpf_object,
            realtime_minus_monotonic_ns: 0,
            queues: Vec::new(),
            bpf: None,
            promisc_guard: None,
            stats: CaptureStats::default(),
            running: false,
            next_queue: 0,
            diagnostic_fail_after_packets,
        })
    }

    fn create_queues(&mut self) -> Result<()> {
        let umem_config = UmemConfig {
            frame_size: 4096,
            frame_count: self.frames_per_queue,
            fill_queue_size: XSK_RING_SIZE as usize,
            comp_queue_size: XSK_RING_SIZE as usize,
            headroom: 16,
            use_huge_pages: false,
        };
        let socket_config = XskSocketConfig {
            rx_ring_size: XSK_RING_SIZE,
            tx_ring_size: XSK_RING_SIZE,
            fill_ring_size: XSK_RING_SIZE,
            comp_ring_size: XSK_RING_SIZE,
            bind_flags: self.mode.bind_flags(),
            xdp_flags: 0,
        };
        for queue_id in 0..self.queue_count {
            let umem = Arc::new(Umem::new(&umem_config)?);
            let socket = XskSocket::new(&umem, self.ifindex, queue_id, socket_config.clone())
                .with_context(|| format!("create XSK socket for RX queue {queue_id}"))?;
            self.queues.push(QueueState {
                queue_id,
                umem,
                socket: Some(socket),
                kernel_owned_frames: vec![false; self.frames_per_queue],
                receive_descriptors: vec![
                    XdpDesc {
                        addr: 0,
                        len: 0,
                        options: 0,
                    };
                    self.receive_batch_size
                ],
            });
        }
        Ok(())
    }

    fn load_and_attach_bpf(&mut self) -> Result<()> {
        let mut bpf = Bpf::load_file(&self.ebpf_object).with_context(|| {
            format!(
                "load HFT timestamped XDP object {}",
                self.ebpf_object.display()
            )
        })?;
        {
            let program: &mut Xdp = bpf
                .program_mut("xdp_redirect")
                .context("XDP program xdp_redirect is missing")?
                .try_into()
                .context("xdp_redirect is not an XDP program")?;
            program.load().context("load xdp_redirect program")?;
            program
                .attach(&self.interface, self.mode.attach_flags())
                .with_context(|| {
                    format!("attach {} XDP to {}", self.mode.label(), self.interface)
                })?;
        }
        let map = bpf
            .map_mut("XSKS_MAP")
            .context("XSKS_MAP is missing from xdp_redirect")?;
        let mut xsk_map = XskMap::try_from(map).context("convert XSKS_MAP")?;
        for queue in &self.queues {
            let socket = queue.socket.as_ref().context("XSK socket missing")?;
            xsk_map
                .set(queue.queue_id, socket.fd(), 0)
                .with_context(|| format!("register XSK socket for RX queue {}", queue.queue_id))?;
        }
        self.bpf = Some(bpf);
        Ok(())
    }

    fn refill(queue: &mut QueueState, target_frames: usize) {
        let Some(socket) = queue.socket.as_mut() else {
            return;
        };
        debug_assert!(target_frames <= MAX_XSK_BATCH_SIZE);
        let mut frames = [0usize; MAX_XSK_BATCH_SIZE];
        let mut addresses = [0u64; MAX_XSK_BATCH_SIZE];
        let mut allocated = 0usize;
        while allocated < target_frames {
            let Some(frame) = queue.umem.alloc_frame() else {
                break;
            };
            frames[allocated] = frame;
            addresses[allocated] = queue.umem.frame_addr_raw(frame) as u64;
            allocated += 1;
        }
        if allocated == 0 {
            return;
        }
        let filled = socket.fill_queue.fill(&addresses[..allocated]);
        for frame in &frames[..filled] {
            queue.kernel_owned_frames[*frame] = true;
        }
        for frame in &frames[filled..allocated] {
            queue.umem.free_frame(*frame);
        }
    }

    fn receive_from_queue_with<F>(
        queue: &mut QueueState,
        realtime_minus_monotonic_ns: i128,
        receive_batch_size: usize,
        visitor: &mut F,
    ) -> Result<Option<(usize, u64)>>
    where
        F: FnMut(u32, &[u8], u64) -> Result<()>,
    {
        let received = {
            let Some(socket) = queue.socket.as_mut() else {
                return Ok(None);
            };
            if socket.rx_needs_wakeup() {
                socket.wakeup()?;
            }
            if socket.rx_queue.available() == 0 {
                return Ok(None);
            }
            debug_assert_eq!(queue.receive_descriptors.len(), receive_batch_size);
            socket.rx_queue.receive(&mut queue.receive_descriptors)
        };
        if received == 0 {
            return Ok(None);
        }
        let mut bytes = 0u64;
        for index in 0..received {
            let descriptor = queue.receive_descriptors[index];
            let address = descriptor.addr as usize;
            let frame = address / queue.umem.frame_size();
            if frame >= queue.umem.frame_count() {
                bail!(
                    "RX queue {} returned out-of-range UMEM address {}",
                    queue.queue_id,
                    address
                );
            }
            if !queue.kernel_owned_frames[frame] {
                bail!(
                    "RX queue {} returned untracked UMEM frame {}",
                    queue.queue_id,
                    frame
                );
            }
            let metadata_address = address
                .checked_sub(std::mem::size_of::<u64>())
                .context("XDP descriptor has no timestamp metadata headroom")?;
            let metadata = queue
                .umem
                .get_data(metadata_address, std::mem::size_of::<u64>())
                .context("read XDP timestamp metadata")?;
            let monotonic_ns = u64::from_ne_bytes(
                metadata
                    .try_into()
                    .context("XDP timestamp metadata length")?,
            );
            let realtime_ns = i128::from(monotonic_ns)
                .checked_add(realtime_minus_monotonic_ns)
                .context("convert XDP monotonic timestamp to realtime")?;
            if realtime_ns <= 0 || realtime_ns > i128::from(u64::MAX) {
                bail!("converted XDP timestamp is outside the u64 range");
            }
            let timestamp = (realtime_ns as u64) / 1000;
            let data = queue
                .umem
                .get_data(address, descriptor.len as usize)
                .with_context(|| {
                    format!(
                        "read RX queue {} UMEM address {} length {}",
                        queue.queue_id, address, descriptor.len
                    )
                })?;
            let visit_result = visitor(queue.queue_id, data, timestamp);
            queue.umem.free_frame(frame);
            queue.kernel_owned_frames[frame] = false;
            visit_result?;
            bytes = bytes.saturating_add(descriptor.len as u64);
        }
        Ok(Some((received, bytes)))
    }

    fn receive_owned_from_queue(
        queue: &mut QueueState,
        realtime_minus_monotonic_ns: i128,
        receive_batch_size: usize,
    ) -> Result<Option<OwnedReceiveBatch>> {
        let mut packets = Vec::with_capacity(receive_batch_size);
        let received = Self::receive_from_queue_with(
            queue,
            realtime_minus_monotonic_ns,
            receive_batch_size,
            &mut |_queue_id, data, timestamp| {
                packets.push((
                    data.to_vec(),
                    CaptureTimestamp::from_epoch_micros(
                        timestamp,
                        CaptureTimestampProvenance::CorrelatedMonotonic,
                    ),
                ));
                Ok(())
            },
        )?;
        Ok(received.map(|(_, bytes)| (packets, bytes)))
    }

    fn collect_kernel_drop_stats(&mut self) {
        let mut drops = 0u64;
        for queue in &self.queues {
            let Some(socket) = queue.socket.as_ref() else {
                continue;
            };
            if let Ok(stats) = socket.statistics() {
                drops = drops
                    .saturating_add(stats.rx_dropped)
                    .saturating_add(stats.rx_invalid_descs)
                    .saturating_add(stats.rx_ring_full)
                    .saturating_add(stats.rx_fill_ring_empty_descs);
            }
        }
        self.stats.packets_dropped = self.stats.packets_dropped.saturating_add(drops);
    }

    fn wait_for_any_queue(&self, timeout_ms: i32) -> Result<bool> {
        let mut poll_fds: Vec<libc::pollfd> = self
            .queues
            .iter()
            .filter_map(|queue| queue.socket.as_ref())
            .map(|socket| libc::pollfd {
                fd: socket.fd(),
                events: libc::POLLIN,
                revents: 0,
            })
            .collect();
        if poll_fds.is_empty() {
            return Ok(false);
        }
        let ready = unsafe {
            libc::poll(
                poll_fds.as_mut_ptr(),
                poll_fds.len() as libc::nfds_t,
                timeout_ms,
            )
        };
        if ready < 0 {
            let error = std::io::Error::last_os_error();
            if error.kind() == std::io::ErrorKind::Interrupted {
                return Ok(false);
            }
            return Err(error).context("poll XDP RX queues");
        }
        Ok(ready > 0
            && poll_fds
                .iter()
                .any(|descriptor| descriptor.revents & libc::POLLIN != 0))
    }

    fn cleanup(&mut self) {
        self.bpf = None;
        self.promisc_guard = None;
        for queue in &mut self.queues {
            Self::cleanup_queue(queue);
        }
        self.queues.clear();
        self.running = false;
    }

    fn cleanup_queue(queue: &mut QueueState) {
        queue.socket = None;
        for (frame, kernel_owned) in queue.kernel_owned_frames.iter_mut().enumerate() {
            if *kernel_owned {
                queue.umem.free_frame(frame);
                *kernel_owned = false;
            }
        }
    }

    pub fn take_queue_workers(&mut self) -> Result<Vec<HftXdpQueueWorker>> {
        if !self.running {
            bail!("XDP capture must be running before queue workers are taken");
        }
        if self.queues.len() != self.queue_count as usize {
            bail!(
                "expected {} XDP queues before sharding, got {}",
                self.queue_count,
                self.queues.len()
            );
        }
        Ok(std::mem::take(&mut self.queues)
            .into_iter()
            .map(|queue| HftXdpQueueWorker {
                queue: Some(queue),
                realtime_minus_monotonic_ns: self.realtime_minus_monotonic_ns,
                receive_batch_size: self.receive_batch_size,
                packets: 0,
                bytes: 0,
            })
            .collect())
    }

    pub fn restore_queue_workers(&mut self, workers: Vec<HftXdpQueueWorker>) -> Result<()> {
        if !self.running {
            bail!("XDP capture must be running before queue workers are restored");
        }
        if !self.queues.is_empty() {
            bail!("XDP capture still owns queues while restoring workers");
        }
        if workers.len() != self.queue_count as usize {
            bail!(
                "expected {} XDP queue workers, got {}",
                self.queue_count,
                workers.len()
            );
        }
        let mut seen = vec![false; self.queue_count as usize];
        let mut queues = Vec::with_capacity(workers.len());
        for worker in workers {
            let queue_id = worker.queue_id() as usize;
            if queue_id >= seen.len() || seen[queue_id] {
                bail!("invalid or duplicate XDP queue worker id {}", queue_id);
            }
            seen[queue_id] = true;
            self.stats.packets_received =
                self.stats.packets_received.saturating_add(worker.packets());
            self.stats.bytes_received = self.stats.bytes_received.saturating_add(worker.bytes());
            queues.push(worker.into_queue());
        }
        queues.sort_by_key(|queue| queue.queue_id);
        self.queues = queues;
        self.next_queue = 0;
        Ok(())
    }

    pub fn poll_borrowed<F>(&mut self, mut visitor: F) -> Result<BorrowedPollStats>
    where
        F: FnMut(u32, &[u8], u64) -> Result<()>,
    {
        if !self.running || self.queues.is_empty() {
            return Ok(BorrowedPollStats::default());
        }
        if self
            .diagnostic_fail_after_packets
            .is_some_and(|limit| self.stats.packets_received >= limit)
        {
            bail!(
                "diagnostic injected XDP poll failure after {} packets",
                self.stats.packets_received
            );
        }
        let queue_len = self.queues.len();
        let mut total = BorrowedPollStats::default();
        for offset in 0..queue_len {
            let index = (self.next_queue + offset) % queue_len;
            if let Some((packets, bytes)) = Self::receive_from_queue_with(
                &mut self.queues[index],
                self.realtime_minus_monotonic_ns,
                self.receive_batch_size,
                &mut visitor,
            )? {
                total.packets = total.packets.saturating_add(packets);
                total.bytes = total.bytes.saturating_add(bytes);
                Self::refill(&mut self.queues[index], self.receive_batch_size);
            } else {
                Self::refill(&mut self.queues[index], self.receive_batch_size);
            }
        }
        if total.packets == 0 {
            let _ = self.wait_for_any_queue(1)?;
        } else {
            self.stats.packets_received = self
                .stats
                .packets_received
                .saturating_add(total.packets as u64);
            self.stats.bytes_received = self.stats.bytes_received.saturating_add(total.bytes);
            self.next_queue = (self.next_queue + 1) % queue_len;
        }
        Ok(total)
    }
}

#[async_trait::async_trait]
impl Capturer for HftXdpCapture {
    async fn start(&mut self) -> Result<()> {
        if self.running {
            return Ok(());
        }
        if let Ok(guard) = PromiscuousMode::enable(&self.interface) {
            self.promisc_guard = Some(guard);
        }
        self.realtime_minus_monotonic_ns = realtime_minus_monotonic_ns()?;
        self.create_queues()?;
        self.load_and_attach_bpf()?;
        for queue in &mut self.queues {
            Self::refill(queue, self.receive_batch_size);
        }
        self.running = true;
        eprintln!(
            "hft_xdp_backend mode={} queues={} frames_per_queue={} receive_batch_size={}",
            self.mode.label(),
            self.queue_count,
            self.frames_per_queue,
            self.receive_batch_size
        );
        Ok(())
    }

    async fn stop(&mut self) -> Result<()> {
        if !self.running {
            self.cleanup();
            return Ok(());
        }
        self.collect_kernel_drop_stats();
        self.cleanup();
        eprintln!(
            "hft_xdp_stop mode={} packets={} drops={} cleanup=complete",
            self.mode.label(),
            self.stats.packets_received,
            self.stats.packets_dropped
        );
        Ok(())
    }

    fn poll(&mut self) -> Result<Option<PacketBatch>> {
        if !self.running || self.queues.is_empty() {
            return Ok(None);
        }
        if self
            .diagnostic_fail_after_packets
            .is_some_and(|limit| self.stats.packets_received >= limit)
        {
            bail!(
                "diagnostic injected XDP poll failure after {} packets",
                self.stats.packets_received
            );
        }
        let queue_len = self.queues.len();
        for offset in 0..queue_len {
            let index = (self.next_queue + offset) % queue_len;
            if let Some((packets, bytes)) = Self::receive_owned_from_queue(
                &mut self.queues[index],
                self.realtime_minus_monotonic_ns,
                self.receive_batch_size,
            )? {
                let packet_count = packets.len() as u64;
                self.stats.packets_received =
                    self.stats.packets_received.saturating_add(packet_count);
                self.stats.bytes_received = self.stats.bytes_received.saturating_add(bytes);
                Self::refill(&mut self.queues[index], self.receive_batch_size);
                self.next_queue = (index + 1) % queue_len;
                return Ok(Some(PacketBatch::from_owned_packets(packets)));
            }
            Self::refill(&mut self.queues[index], self.receive_batch_size);
        }
        let _ = self.wait_for_any_queue(1)?;
        Ok(None)
    }

    fn stats(&self) -> CaptureStats {
        self.stats.clone()
    }
}

fn realtime_minus_monotonic_ns() -> Result<i128> {
    let realtime_ns = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .context("system clock precedes UNIX epoch")?
        .as_nanos() as i128;
    let mut monotonic: libc::timespec = unsafe { std::mem::zeroed() };
    let status = unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, &mut monotonic) };
    if status != 0 {
        return Err(std::io::Error::last_os_error()).context("read CLOCK_MONOTONIC");
    }
    let monotonic_ns = i128::from(monotonic.tv_sec)
        .checked_mul(1_000_000_000)
        .and_then(|value| value.checked_add(i128::from(monotonic.tv_nsec)))
        .context("CLOCK_MONOTONIC conversion overflow")?;
    realtime_ns
        .checked_sub(monotonic_ns)
        .context("clock offset conversion overflow")
}

impl Drop for HftXdpCapture {
    fn drop(&mut self) {
        self.cleanup();
    }
}

fn active_combined_queue_count(interface: &str) -> Result<u32> {
    let output = Command::new("ethtool")
        .args(["-l", interface])
        .output()
        .with_context(|| format!("run ethtool -l {interface}"))?;
    if !output.status.success() {
        bail!(
            "ethtool -l {} failed: {}",
            interface,
            String::from_utf8_lossy(&output.stderr).trim()
        );
    }
    let text = String::from_utf8(output.stdout).context("ethtool output is not UTF-8")?;
    let mut current = false;
    for line in text.lines() {
        let trimmed = line.trim();
        if trimmed == "Current hardware settings:" {
            current = true;
            continue;
        }
        if current && trimmed.starts_with("Combined:") {
            let value = trimmed
                .split_once(':')
                .map(|(_, value)| value.trim())
                .context("parse current Combined channel count")?;
            return value
                .parse::<u32>()
                .context("parse current Combined channel count");
        }
    }
    bail!("current Combined channel count is unavailable for {interface}")
}

#[cfg(test)]
mod tests {
    use super::HftXdpMode;
    use aya::programs::XdpFlags;
    use probe_agent::capture::xdp_sys::{XDP_COPY, XDP_ZEROCOPY};

    #[test]
    fn modes_do_not_silently_fallback() {
        assert_eq!(
            HftXdpMode::Native.attach_flags().bits(),
            XdpFlags::DRV_MODE.bits()
        );
        assert_eq!(
            HftXdpMode::Skb.attach_flags().bits(),
            XdpFlags::SKB_MODE.bits()
        );
        assert_eq!(HftXdpMode::Native.bind_flags(), XDP_ZEROCOPY);
        assert_ne!(HftXdpMode::Native.bind_flags(), 0);
        assert_ne!(HftXdpMode::Native.bind_flags(), XDP_COPY);
        assert_eq!(HftXdpMode::Skb.bind_flags(), XDP_COPY);
    }
}
