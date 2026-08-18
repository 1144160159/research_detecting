//! Borrowed TPACKET_V3/PACKET_FANOUT receive rings owned by HFT-MGBS.
//!
//! A frame slice is valid only for the duration of the `poll_borrowed` visitor.
//! The block is always returned to the kernel, including when the visitor fails.

use anyhow::{bail, Context, Result};
use serde::Serialize;
use std::ffi::CString;
use std::mem::{size_of, zeroed};
use std::os::fd::RawFd;
use std::ptr;
use std::sync::atomic::{fence, Ordering};

const ETH_P_ALL: u16 = 0x0003;
const PACKET_RX_RING: libc::c_int = 5;
const PACKET_STATISTICS: libc::c_int = 6;
const PACKET_ADD_MEMBERSHIP: libc::c_int = 1;
const PACKET_VERSION: libc::c_int = 10;
const PACKET_FANOUT: libc::c_int = 18;
const PACKET_MR_PROMISC: u16 = 1;
const TPACKET_V3: libc::c_int = 2;
const TP_STATUS_KERNEL: u32 = 0;
const TP_STATUS_USER: u32 = 1;
const TP_FT_REQ_FILL_RXHASH: u32 = 1;

#[derive(Clone, Copy, Debug)]
pub enum FanoutMode {
    Hash,
    Qm,
}

impl FanoutMode {
    pub fn kernel_value(self) -> u16 {
        match self {
            Self::Hash => 0,
            Self::Qm => 5,
        }
    }

    pub fn label(self) -> &'static str {
        match self {
            Self::Hash => "hash",
            Self::Qm => "qm",
        }
    }
}

#[derive(Clone, Debug)]
pub struct RingConfig {
    pub interface: String,
    pub fanout_mode: FanoutMode,
    pub fanout_id: u16,
    pub block_size: u32,
    pub block_count: u32,
    pub frame_size: u32,
    pub retire_block_timeout_ms: u32,
}

impl RingConfig {
    pub fn validate(&self) -> Result<()> {
        if self.interface.is_empty() {
            bail!("interface must not be empty");
        }
        if self.fanout_id == 0 {
            bail!("fanout id must be non-zero");
        }
        if self.block_size == 0
            || self.block_count == 0
            || self.frame_size == 0
            || self.frame_size < 128
            || !self.frame_size.is_multiple_of(16)
            || !self.block_size.is_multiple_of(self.frame_size)
        {
            bail!(
                "ring sizes must be positive; frame size must be at least 128 bytes, 16-byte aligned and divide block size"
            );
        }
        let page_size = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };
        if page_size <= 0 || !self.block_size.is_multiple_of(page_size as u32) {
            bail!("block size must be a multiple of the system page size");
        }
        u64::from(self.block_size)
            .checked_mul(u64::from(self.block_count))
            .context("ring memory size overflow")?;
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Default, Serialize)]
pub struct SocketStatistics {
    pub packets: u32,
    pub drops: u32,
    pub freeze_queue_count: u32,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct BorrowedBlockStats {
    pub packets: u64,
    pub bytes: u64,
}

#[repr(C)]
#[derive(Clone, Copy, Default)]
struct TpacketReq3 {
    tp_block_size: u32,
    tp_block_nr: u32,
    tp_frame_size: u32,
    tp_frame_nr: u32,
    tp_retire_blk_tov: u32,
    tp_sizeof_priv: u32,
    tp_feature_req_word: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct TpacketBdTs {
    ts_sec: u32,
    ts_nsec: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct TpacketHdrV1 {
    block_status: u32,
    num_pkts: u32,
    offset_to_first_pkt: u32,
    blk_len: u32,
    seq_num: u64,
    ts_first_pkt: TpacketBdTs,
    ts_last_pkt: TpacketBdTs,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct TpacketBlockDesc {
    version: u32,
    offset_to_priv: u32,
    hdr: TpacketHdrV1,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct Tpacket3Hdr {
    tp_next_offset: u32,
    tp_sec: u32,
    tp_nsec: u32,
    tp_snaplen: u32,
    tp_len: u32,
    tp_status: u32,
    tp_mac: u16,
    tp_net: u16,
}

#[repr(C)]
#[derive(Clone, Copy, Default)]
struct KernelSocketStatistics {
    tp_packets: u32,
    tp_drops: u32,
    tp_freeze_q_cnt: u32,
}

#[repr(C)]
#[derive(Clone, Copy, Default)]
struct PacketMreq {
    mr_ifindex: libc::c_int,
    mr_type: u16,
    mr_alen: u16,
    mr_address: [u8; 8],
}

pub struct PacketRing {
    fd: RawFd,
    base: *mut u8,
    map_len: usize,
    request: TpacketReq3,
    block_index: usize,
}

struct BlockLease<'a> {
    ring: &'a mut PacketRing,
    status: *mut u32,
}

impl Drop for BlockLease<'_> {
    fn drop(&mut self) {
        fence(Ordering::Release);
        unsafe {
            ptr::write_volatile(self.status, TP_STATUS_KERNEL);
        }
        self.ring.block_index =
            (self.ring.block_index + 1) % self.ring.request.tp_block_nr as usize;
    }
}

unsafe impl Send for PacketRing {}

impl Drop for PacketRing {
    fn drop(&mut self) {
        if !self.base.is_null() && self.map_len != 0 {
            unsafe {
                libc::munmap(self.base.cast(), self.map_len);
            }
        }
        if self.fd >= 0 {
            unsafe {
                libc::close(self.fd);
            }
        }
    }
}

impl PacketRing {
    pub fn open(config: &RingConfig) -> Result<Self> {
        config.validate()?;
        let protocol = ETH_P_ALL.to_be() as libc::c_int;
        let fd = unsafe {
            libc::socket(
                libc::AF_PACKET,
                libc::SOCK_RAW | libc::SOCK_CLOEXEC,
                protocol,
            )
        };
        if fd < 0 {
            return Err(std::io::Error::last_os_error()).context("open AF_PACKET socket");
        }
        let mut ring = Self {
            fd,
            base: ptr::null_mut(),
            map_len: 0,
            request: TpacketReq3::default(),
            block_index: 0,
        };
        set_packet_option(ring.fd, PACKET_VERSION, &TPACKET_V3)?;
        let frames_per_block = config.block_size / config.frame_size;
        ring.request = TpacketReq3 {
            tp_block_size: config.block_size,
            tp_block_nr: config.block_count,
            tp_frame_size: config.frame_size,
            tp_frame_nr: frames_per_block
                .checked_mul(config.block_count)
                .context("ring frame count overflow")?,
            tp_retire_blk_tov: config.retire_block_timeout_ms,
            tp_sizeof_priv: 0,
            tp_feature_req_word: TP_FT_REQ_FILL_RXHASH,
        };
        set_packet_option(ring.fd, PACKET_RX_RING, &ring.request)?;
        ring.map_len = (config.block_size as usize)
            .checked_mul(config.block_count as usize)
            .context("ring map size overflow")?;
        let base = unsafe {
            libc::mmap(
                ptr::null_mut(),
                ring.map_len,
                libc::PROT_READ | libc::PROT_WRITE,
                libc::MAP_SHARED,
                ring.fd,
                0,
            )
        };
        if base == libc::MAP_FAILED {
            return Err(std::io::Error::last_os_error()).context("mmap TPACKET_V3 ring");
        }
        ring.base = base.cast();

        let interface = CString::new(config.interface.as_str())
            .context("interface contains an embedded NUL")?;
        let interface_index = unsafe { libc::if_nametoindex(interface.as_ptr()) };
        if interface_index == 0 {
            return Err(std::io::Error::last_os_error())
                .with_context(|| format!("resolve interface {}", config.interface));
        }
        let mut address: libc::sockaddr_ll = unsafe { zeroed() };
        address.sll_family = libc::AF_PACKET as u16;
        address.sll_protocol = ETH_P_ALL.to_be();
        address.sll_ifindex = interface_index as i32;
        let status = unsafe {
            libc::bind(
                ring.fd,
                (&address as *const libc::sockaddr_ll).cast(),
                size_of::<libc::sockaddr_ll>() as libc::socklen_t,
            )
        };
        if status != 0 {
            return Err(std::io::Error::last_os_error())
                .with_context(|| format!("bind AF_PACKET socket to {}", config.interface));
        }
        let membership = PacketMreq {
            mr_ifindex: interface_index as libc::c_int,
            mr_type: PACKET_MR_PROMISC,
            ..PacketMreq::default()
        };
        set_packet_option(ring.fd, PACKET_ADD_MEMBERSHIP, &membership)
            .context("enable per-socket PACKET_MR_PROMISC membership")?;
        let fanout =
            u32::from(config.fanout_id) | (u32::from(config.fanout_mode.kernel_value()) << 16);
        set_packet_option(ring.fd, PACKET_FANOUT, &fanout)?;
        Ok(ring)
    }

    pub fn poll_borrowed<F>(&mut self, mut visitor: F) -> Result<Option<BorrowedBlockStats>>
    where
        F: for<'frame> FnMut(&'frame [u8], u64, u32) -> Result<()>,
    {
        let block_size = self.request.tp_block_size as usize;
        let block = unsafe { self.base.add(self.block_index * block_size) };
        let descriptor = block.cast::<TpacketBlockDesc>();
        let status_pointer = unsafe { ptr::addr_of_mut!((*descriptor).hdr.block_status) };
        let status = unsafe { ptr::read_volatile(status_pointer) };
        if status & TP_STATUS_USER == 0 {
            return Ok(None);
        }
        fence(Ordering::Acquire);
        let _lease = BlockLease {
            ring: self,
            status: status_pointer,
        };
        let result = unsafe { visit_block(block, block_size, &mut visitor) };
        result.map(Some)
    }

    /// Read-once PACKET_STATISTICS; Linux resets these counters on read.
    pub fn take_socket_statistics(&self) -> Result<SocketStatistics> {
        let mut stats = KernelSocketStatistics::default();
        let mut length = size_of::<KernelSocketStatistics>() as libc::socklen_t;
        let status = unsafe {
            libc::getsockopt(
                self.fd,
                libc::SOL_PACKET,
                PACKET_STATISTICS,
                (&mut stats as *mut KernelSocketStatistics).cast(),
                &mut length,
            )
        };
        if status != 0 {
            return Err(std::io::Error::last_os_error()).context("read PACKET_STATISTICS");
        }
        if length as usize != size_of::<KernelSocketStatistics>() {
            bail!("PACKET_STATISTICS returned unexpected length {length}");
        }
        Ok(SocketStatistics {
            packets: stats.tp_packets,
            drops: stats.tp_drops,
            freeze_queue_count: stats.tp_freeze_q_cnt,
        })
    }
}

pub fn pin_current_thread(cpu: usize) -> Result<()> {
    if cpu >= 1024 {
        bail!("CPU {cpu} exceeds cpu_set_t capacity");
    }
    let mut set: libc::cpu_set_t = unsafe { zeroed() };
    unsafe {
        libc::CPU_ZERO(&mut set);
        libc::CPU_SET(cpu, &mut set);
    }
    let status = unsafe {
        libc::pthread_setaffinity_np(libc::pthread_self(), size_of::<libc::cpu_set_t>(), &set)
    };
    if status != 0 {
        return Err(std::io::Error::from_raw_os_error(status))
            .with_context(|| format!("pin worker to CPU {cpu}"));
    }
    Ok(())
}

fn set_packet_option<T>(fd: RawFd, option: libc::c_int, value: &T) -> Result<()> {
    let status = unsafe {
        libc::setsockopt(
            fd,
            libc::SOL_PACKET,
            option,
            (value as *const T).cast(),
            size_of::<T>() as libc::socklen_t,
        )
    };
    if status != 0 {
        return Err(std::io::Error::last_os_error())
            .with_context(|| format!("setsockopt SOL_PACKET option {option}"));
    }
    Ok(())
}

unsafe fn visit_block<F>(
    block: *mut u8,
    block_size: usize,
    visitor: &mut F,
) -> Result<BorrowedBlockStats>
where
    F: for<'frame> FnMut(&'frame [u8], u64, u32) -> Result<()>,
{
    let descriptor = ptr::read_unaligned(block.cast::<TpacketBlockDesc>());
    if descriptor.version != TPACKET_V3 as u32 {
        bail!("unexpected TPACKET block version {}", descriptor.version);
    }
    let occupied = descriptor.hdr.blk_len as usize;
    if occupied < size_of::<TpacketBlockDesc>() || occupied > block_size {
        bail!("invalid TPACKET block occupied length {occupied}");
    }
    let mut offset = descriptor.hdr.offset_to_first_pkt as usize;
    let packet_count = descriptor.hdr.num_pkts as usize;
    let mut stats = BorrowedBlockStats::default();
    for packet_index in 0..packet_count {
        if offset > occupied.saturating_sub(size_of::<Tpacket3Hdr>()) {
            bail!("packet header offset {offset} exceeds occupied block length {occupied}");
        }
        let header = ptr::read_unaligned(block.add(offset).cast::<Tpacket3Hdr>());
        let mac_offset = offset
            .checked_add(header.tp_mac as usize)
            .context("packet MAC offset overflow")?;
        let snaplen = header.tp_snaplen as usize;
        if mac_offset > occupied || snaplen > occupied.saturating_sub(mac_offset) {
            bail!("packet payload exceeds TPACKET block");
        }
        let timestamp_us = u64::from(header.tp_sec)
            .saturating_mul(1_000_000)
            .saturating_add(u64::from(header.tp_nsec) / 1_000);
        let frame = std::slice::from_raw_parts(block.add(mac_offset), snaplen);
        visitor(frame, timestamp_us, header.tp_len)?;
        stats.packets = stats.packets.saturating_add(1);
        stats.bytes = stats.bytes.saturating_add(u64::from(header.tp_len));
        if packet_index + 1 < packet_count {
            if header.tp_next_offset == 0 {
                bail!("zero tp_next_offset before final packet in block");
            }
            offset = offset
                .checked_add(header.tp_next_offset as usize)
                .context("packet offset overflow")?;
        }
    }
    Ok(stats)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[repr(align(16))]
    struct AlignedBlock([u8; 512]);

    #[test]
    fn fanout_values_match_linux_uapi() {
        assert_eq!(FanoutMode::Hash.kernel_value(), 0);
        assert_eq!(FanoutMode::Qm.kernel_value(), 5);
    }

    #[test]
    fn borrowed_block_visitor_receives_frame_without_copy() {
        let mut storage = AlignedBlock([0; 512]);
        let base = storage.0.as_mut_ptr();
        let descriptor = unsafe { &mut *(base.cast::<TpacketBlockDesc>()) };
        descriptor.version = TPACKET_V3 as u32;
        descriptor.hdr.num_pkts = 1;
        descriptor.hdr.offset_to_first_pkt = 64;
        descriptor.hdr.blk_len = storage.0.len() as u32;
        let header = unsafe { &mut *(base.add(64).cast::<Tpacket3Hdr>()) };
        header.tp_sec = 7;
        header.tp_nsec = 123_000;
        header.tp_snaplen = 4;
        header.tp_len = 8;
        header.tp_mac = 64;
        unsafe { ptr::copy_nonoverlapping([1u8, 2, 3, 4].as_ptr(), base.add(128), 4) };
        let mut seen_pointer = ptr::null();
        let mut seen = Vec::new();
        let stats = unsafe {
            visit_block(
                base,
                storage.0.len(),
                &mut |frame, timestamp, original_len| {
                    seen_pointer = frame.as_ptr();
                    seen.push((frame.to_vec(), timestamp, original_len));
                    Ok(())
                },
            )
        }
        .unwrap();
        assert_eq!(seen_pointer, unsafe { base.add(128) });
        assert_eq!(seen, vec![(vec![1, 2, 3, 4], 7_000_123, 8)]);
        assert_eq!(stats.packets, 1);
        assert_eq!(stats.bytes, 8);
    }

    #[test]
    fn malformed_packet_bounds_fail_closed() {
        let mut storage = AlignedBlock([0; 512]);
        let base = storage.0.as_mut_ptr();
        let descriptor = unsafe { &mut *(base.cast::<TpacketBlockDesc>()) };
        descriptor.version = TPACKET_V3 as u32;
        descriptor.hdr.num_pkts = 1;
        descriptor.hdr.offset_to_first_pkt = 500;
        descriptor.hdr.blk_len = storage.0.len() as u32;
        let error =
            unsafe { visit_block(base, storage.0.len(), &mut |_, _, _| Ok(())) }.unwrap_err();
        assert!(error.to_string().contains("packet header offset"));
    }

    #[test]
    fn block_lease_returns_ownership_and_advances_cursor() {
        let mut status = TP_STATUS_USER;
        let mut ring = PacketRing {
            fd: -1,
            base: ptr::null_mut(),
            map_len: 0,
            request: TpacketReq3 {
                tp_block_nr: 2,
                ..TpacketReq3::default()
            },
            block_index: 0,
        };
        {
            let _lease = BlockLease {
                ring: &mut ring,
                status: &mut status,
            };
        }
        assert_eq!(status, TP_STATUS_KERNEL);
        assert_eq!(ring.block_index, 1);
    }
}
