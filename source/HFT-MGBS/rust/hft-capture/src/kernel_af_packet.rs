use anyhow::{bail, Context, Result};
use probe_agent::capture::{
    CaptureStats, CaptureTimestamp, CaptureTimestampProvenance, Capturer, PacketBatch,
};
use std::ffi::CString;
use std::mem::{size_of, zeroed};
use std::os::fd::RawFd;

const ETH_P_ALL: u16 = 0x0003;
const RECEIVE_BATCH: usize = 64;
const FRAME_SIZE: usize = 65_536;
const CONTROL_SIZE: usize = 128;
const PACKET_IGNORE_OUTGOING_OPT: libc::c_int = 23;
const PACKET_OTHERHOST_TYPE: u8 = 3;

#[repr(align(16))]
#[derive(Clone)]
struct ControlBuffer([u8; CONTROL_SIZE]);

pub struct KernelTimestampAfPacket {
    fd: RawFd,
    ifindex: i32,
    running: bool,
    buffers: Vec<Vec<u8>>,
    stats: CaptureStats,
    timestamp_missing: u64,
    packet_type_counts: [u64; 8],
    interface_mismatch_count: u64,
}

impl KernelTimestampAfPacket {
    pub fn new(interface: &str) -> Result<Self> {
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
            return Err(std::io::Error::last_os_error())
                .context("create timestamped AF_PACKET socket");
        }
        if let Err(error) = configure_socket(fd, ifindex as i32) {
            unsafe {
                libc::close(fd);
            }
            return Err(error);
        }
        Ok(Self {
            fd,
            ifindex: ifindex as i32,
            running: false,
            buffers: (0..RECEIVE_BATCH).map(|_| vec![0u8; FRAME_SIZE]).collect(),
            stats: CaptureStats::default(),
            timestamp_missing: 0,
            packet_type_counts: [0; 8],
            interface_mismatch_count: 0,
        })
    }
}

impl Drop for KernelTimestampAfPacket {
    fn drop(&mut self) {
        eprintln!(
            "hft_af_packet_direction_stats ifindex={} packet_type_counts={:?} \
             interface_mismatch_count={}",
            self.ifindex, self.packet_type_counts, self.interface_mismatch_count
        );
        unsafe {
            libc::close(self.fd);
        }
    }
}

#[async_trait::async_trait]
impl Capturer for KernelTimestampAfPacket {
    async fn start(&mut self) -> Result<()> {
        self.running = true;
        Ok(())
    }

    async fn stop(&mut self) -> Result<()> {
        self.running = false;
        Ok(())
    }

    fn poll(&mut self) -> Result<Option<PacketBatch>> {
        if !self.running {
            return Ok(None);
        }
        let mut iovecs: Vec<libc::iovec> = self
            .buffers
            .iter_mut()
            .map(|buffer| libc::iovec {
                iov_base: buffer.as_mut_ptr() as *mut libc::c_void,
                iov_len: buffer.len(),
            })
            .collect();
        let mut controls = vec![ControlBuffer([0u8; CONTROL_SIZE]); RECEIVE_BATCH];
        let mut addresses: Vec<libc::sockaddr_ll> =
            (0..RECEIVE_BATCH).map(|_| unsafe { zeroed() }).collect();
        let mut messages = Vec::with_capacity(RECEIVE_BATCH);
        for index in 0..RECEIVE_BATCH {
            let mut message: libc::mmsghdr = unsafe { zeroed() };
            message.msg_hdr.msg_name =
                &mut addresses[index] as *mut libc::sockaddr_ll as *mut libc::c_void;
            message.msg_hdr.msg_namelen = size_of::<libc::sockaddr_ll>() as libc::socklen_t;
            message.msg_hdr.msg_iov = &mut iovecs[index];
            message.msg_hdr.msg_iovlen = 1;
            message.msg_hdr.msg_control = controls[index].0.as_mut_ptr() as *mut libc::c_void;
            message.msg_hdr.msg_controllen = CONTROL_SIZE;
            messages.push(message);
        }
        let received = unsafe {
            libc::recvmmsg(
                self.fd,
                messages.as_mut_ptr(),
                RECEIVE_BATCH as u32,
                libc::MSG_DONTWAIT,
                std::ptr::null_mut(),
            )
        };
        if received < 0 {
            let error = std::io::Error::last_os_error();
            if matches!(
                error.kind(),
                std::io::ErrorKind::WouldBlock | std::io::ErrorKind::TimedOut
            ) {
                return Ok(None);
            }
            return Err(error).context("timestamped recvmmsg failed");
        }
        if received == 0 {
            return Ok(None);
        }
        let mut packets = Vec::with_capacity(received as usize);
        for index in 0..received as usize {
            let address = &addresses[index];
            let packet_type = address.sll_pkttype;
            if let Some(count) = self.packet_type_counts.get_mut(packet_type as usize) {
                *count += 1;
            }
            if address.sll_ifindex != self.ifindex {
                self.interface_mismatch_count += 1;
                continue;
            }
            if !is_ingress_packet_type(packet_type) {
                continue;
            }
            let length = messages[index].msg_len as usize;
            let Some(timestamp_us) = kernel_timestamp_us(&messages[index].msg_hdr) else {
                self.timestamp_missing += 1;
                continue;
            };
            packets.push((
                self.buffers[index][..length].to_vec(),
                CaptureTimestamp::from_epoch_micros(
                    timestamp_us,
                    CaptureTimestampProvenance::KernelPerFrame,
                ),
            ));
            self.stats.packets_received += 1;
            self.stats.bytes_received += length as u64;
        }
        if packets.is_empty() {
            return Ok(None);
        }
        Ok(Some(PacketBatch::from_owned_packets(packets)))
    }

    fn stats(&self) -> CaptureStats {
        let mut stats = self.stats.clone();
        stats.packets_dropped = stats
            .packets_dropped
            .saturating_add(self.timestamp_missing)
            .saturating_add(packet_socket_drops(self.fd));
        stats
    }
}

fn is_ingress_packet_type(packet_type: u8) -> bool {
    packet_type <= PACKET_OTHERHOST_TYPE
}

fn configure_socket(fd: RawFd, ifindex: i32) -> Result<()> {
    let enabled: libc::c_int = 1;
    let timestamp_result = unsafe {
        libc::setsockopt(
            fd,
            libc::SOL_SOCKET,
            libc::SO_TIMESTAMPNS,
            &enabled as *const libc::c_int as *const libc::c_void,
            size_of::<libc::c_int>() as libc::socklen_t,
        )
    };
    if timestamp_result < 0 {
        return Err(std::io::Error::last_os_error()).context("enable SO_TIMESTAMPNS");
    }
    let ignore_outgoing_result = unsafe {
        libc::setsockopt(
            fd,
            libc::SOL_PACKET,
            PACKET_IGNORE_OUTGOING_OPT,
            &enabled as *const libc::c_int as *const libc::c_void,
            size_of::<libc::c_int>() as libc::socklen_t,
        )
    };
    if ignore_outgoing_result < 0 {
        return Err(std::io::Error::last_os_error()).context("enable PACKET_IGNORE_OUTGOING");
    }
    let receive_buffer: libc::c_int = 64 * 1024 * 1024;
    unsafe {
        libc::setsockopt(
            fd,
            libc::SOL_SOCKET,
            libc::SO_RCVBUF,
            &receive_buffer as *const libc::c_int as *const libc::c_void,
            size_of::<libc::c_int>() as libc::socklen_t,
        );
    }
    let mut address: libc::sockaddr_ll = unsafe { zeroed() };
    address.sll_family = libc::AF_PACKET as u16;
    address.sll_protocol = ETH_P_ALL.to_be();
    address.sll_ifindex = ifindex;
    let bind_result = unsafe {
        libc::bind(
            fd,
            &address as *const libc::sockaddr_ll as *const libc::sockaddr,
            size_of::<libc::sockaddr_ll>() as libc::socklen_t,
        )
    };
    if bind_result < 0 {
        return Err(std::io::Error::last_os_error()).context("bind timestamped AF_PACKET socket");
    }
    let mut membership: libc::packet_mreq = unsafe { zeroed() };
    membership.mr_ifindex = ifindex;
    membership.mr_type = libc::PACKET_MR_PROMISC as u16;
    let membership_result = unsafe {
        libc::setsockopt(
            fd,
            libc::SOL_PACKET,
            libc::PACKET_ADD_MEMBERSHIP,
            &membership as *const libc::packet_mreq as *const libc::c_void,
            size_of::<libc::packet_mreq>() as libc::socklen_t,
        )
    };
    if membership_result < 0 {
        return Err(std::io::Error::last_os_error())
            .context("enable AF_PACKET promiscuous membership");
    }
    Ok(())
}

fn kernel_timestamp_us(header: &libc::msghdr) -> Option<u64> {
    unsafe {
        let mut control = libc::CMSG_FIRSTHDR(header);
        while !control.is_null() {
            if (*control).cmsg_level == libc::SOL_SOCKET
                && (*control).cmsg_type == libc::SO_TIMESTAMPNS
            {
                let timestamp = *(libc::CMSG_DATA(control) as *const libc::timespec);
                if timestamp.tv_sec < 0 || timestamp.tv_nsec < 0 {
                    return None;
                }
                return Some(
                    (timestamp.tv_sec as u64)
                        .saturating_mul(1_000_000)
                        .saturating_add(timestamp.tv_nsec as u64 / 1000),
                );
            }
            control = libc::CMSG_NXTHDR(header, control);
        }
    }
    None
}

fn packet_socket_drops(fd: RawFd) -> u64 {
    let mut stats: libc::tpacket_stats = unsafe { zeroed() };
    let mut length = size_of::<libc::tpacket_stats>() as libc::socklen_t;
    let result = unsafe {
        libc::getsockopt(
            fd,
            libc::SOL_PACKET,
            libc::PACKET_STATISTICS,
            &mut stats as *mut libc::tpacket_stats as *mut libc::c_void,
            &mut length,
        )
    };
    if result < 0 {
        return 0;
    }
    stats.tp_drops as u64
}

pub fn require_linux() -> Result<()> {
    if !cfg!(target_os = "linux") {
        bail!("timestamped AF_PACKET capture requires Linux");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::is_ingress_packet_type;

    #[test]
    fn explicit_direction_filter_accepts_only_ingress_types() {
        assert!(is_ingress_packet_type(0));
        assert!(is_ingress_packet_type(1));
        assert!(is_ingress_packet_type(2));
        assert!(is_ingress_packet_type(3));
        assert!(!is_ingress_packet_type(4));
        assert!(!is_ingress_packet_type(5));
        assert!(!is_ingress_packet_type(6));
    }
}
