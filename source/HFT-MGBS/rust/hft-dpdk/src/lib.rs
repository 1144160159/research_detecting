use anyhow::{bail, Context, Result};
use serde::Serialize;
use std::ffi::{c_char, c_void, CString};
use std::thread;
use std::time::{Duration, Instant};

const FULL_PIPELINE_PORT_PROFILE: u32 = 2;
const REQUESTED_RX_DESCRIPTORS: u16 = 4096;
const REQUESTED_TX_DESCRIPTORS: u16 = 1024;

#[repr(C)]
#[derive(Clone, Copy, Debug, Default, Serialize)]
pub struct DpdkStats {
    pub ipackets: u64,
    pub ibytes: u64,
    pub imissed: u64,
    pub ierrors: u64,
    pub rx_nombuf: u64,
    pub opackets: u64,
    pub obytes: u64,
    pub oerrors: u64,
}

impl DpdkStats {
    pub fn delta(self, before: Self) -> Self {
        Self {
            ipackets: self.ipackets.saturating_sub(before.ipackets),
            ibytes: self.ibytes.saturating_sub(before.ibytes),
            imissed: self.imissed.saturating_sub(before.imissed),
            ierrors: self.ierrors.saturating_sub(before.ierrors),
            rx_nombuf: self.rx_nombuf.saturating_sub(before.rx_nombuf),
            opackets: self.opackets.saturating_sub(before.opackets),
            obytes: self.obytes.saturating_sub(before.obytes),
            oerrors: self.oerrors.saturating_sub(before.oerrors),
        }
    }

    pub fn receive_drop_count(self) -> u64 {
        self.imissed
            .saturating_add(self.ierrors)
            .saturating_add(self.rx_nombuf)
    }
}

extern "C" {
    fn hft_dpdk_eal_init(argc: i32, argv: *mut *mut c_char) -> i32;
    fn hft_dpdk_eal_cleanup() -> i32;
    fn hft_dpdk_thread_register() -> i32;
    fn hft_dpdk_thread_unregister();
    fn hft_dpdk_port_count() -> u16;
    fn hft_dpdk_find_port(name: *const c_char, port_id: *mut u16) -> i32;
    fn hft_dpdk_port_init(
        port_id: u16,
        mempool: *mut c_void,
        rx_desc: u16,
        tx_desc: u16,
        queue_count: u16,
        traffic_profile: u32,
        actual_rx_desc: *mut u16,
        actual_tx_desc: *mut u16,
    ) -> i32;
    fn hft_dpdk_port_link(port_id: u16, speed_mbps: *mut u32, up: *mut u8) -> i32;
    fn hft_dpdk_port_stats(port_id: u16, stats: *mut DpdkStats) -> i32;
    fn hft_dpdk_port_stop_close(port_id: u16);
    fn hft_dpdk_mempool_create(
        name: *const c_char,
        count: u32,
        cache_size: u32,
        socket_id: i32,
    ) -> *mut c_void;
    fn hft_dpdk_mempool_free(mempool: *mut c_void);
    fn hft_dpdk_socket_id() -> i32;
    fn hft_dpdk_tsc_hz() -> u64;
    fn hft_dpdk_rdtsc() -> u64;
    fn hft_dpdk_rx_burst(
        port_id: u16,
        queue_id: u16,
        packets: *mut *mut c_void,
        capacity: u16,
    ) -> u16;
    fn hft_dpdk_packet_view(packet: *mut c_void, data: *mut *const u8, length: *mut u32) -> i32;
    fn hft_dpdk_free_burst(packets: *mut *mut c_void, count: u16);
}

#[derive(Clone, Debug)]
pub struct DpdkEnvironmentConfig {
    pub capture_pci: String,
    pub file_prefix: String,
    pub main_cpu: usize,
    pub queue_count: usize,
    pub mempool_capacity: u32,
    pub minimum_link_speed_mbps: u32,
}

#[derive(Clone, Copy, Debug, Serialize)]
pub struct DpdkPortConfiguration {
    pub port_id: u16,
    pub queue_count: usize,
    pub requested_rx_descriptors: u16,
    pub actual_rx_descriptors: u16,
    pub requested_tx_descriptors: u16,
    pub actual_tx_descriptors: u16,
    pub mempool_capacity: u32,
    pub link_speed_mbps: u32,
}

pub struct DpdkEnvironment {
    port_id: u16,
    mempool: *mut c_void,
    configuration: DpdkPortConfiguration,
    active: bool,
}

impl DpdkEnvironment {
    pub fn initialize(config: &DpdkEnvironmentConfig) -> Result<Self> {
        validate_file_prefix(&config.file_prefix)?;
        if config.queue_count == 0 || config.queue_count > u16::MAX as usize {
            bail!("DPDK queue count must be in 1..={}", u16::MAX);
        }
        if config.mempool_capacity < 16_384 {
            bail!("DPDK mempool capacity must be at least 16384");
        }
        if config.minimum_link_speed_mbps == 0 {
            bail!("minimum DPDK link speed must be positive");
        }
        let values = vec![
            "hft-dpdk-full-pipeline".to_owned(),
            "-l".to_owned(),
            config.main_cpu.to_string(),
            "-n".to_owned(),
            "4".to_owned(),
            "--main-lcore".to_owned(),
            config.main_cpu.to_string(),
            "--file-prefix".to_owned(),
            config.file_prefix.clone(),
            "--huge-unlink=always".to_owned(),
            "--iova-mode".to_owned(),
            "pa".to_owned(),
            "-a".to_owned(),
            config.capture_pci.clone(),
        ];
        let mut strings = values
            .iter()
            .map(|value| CString::new(value.as_str()).context("EAL argument contains NUL"))
            .collect::<Result<Vec<_>>>()?;
        let mut pointers = strings
            .iter_mut()
            .map(|value| value.as_ptr() as *mut c_char)
            .collect::<Vec<_>>();
        let status = unsafe { hft_dpdk_eal_init(pointers.len() as i32, pointers.as_mut_ptr()) };
        if status < 0 {
            bail!("rte_eal_init failed with {status}");
        }
        let mut environment = Self {
            port_id: u16::MAX,
            mempool: std::ptr::null_mut(),
            configuration: DpdkPortConfiguration {
                port_id: u16::MAX,
                queue_count: config.queue_count,
                requested_rx_descriptors: REQUESTED_RX_DESCRIPTORS,
                actual_rx_descriptors: 0,
                requested_tx_descriptors: REQUESTED_TX_DESCRIPTORS,
                actual_tx_descriptors: 0,
                mempool_capacity: config.mempool_capacity,
                link_speed_mbps: 0,
            },
            active: true,
        };
        if unsafe { hft_dpdk_port_count() } != 1 {
            bail!("full pipeline requires exactly one EAL allow-listed DPDK port");
        }
        let name = CString::new(config.capture_pci.as_str()).context("PCI address contains NUL")?;
        let status = unsafe { hft_dpdk_find_port(name.as_ptr(), &mut environment.port_id) };
        if status != 0 {
            bail!("DPDK port {} not found: {status}", config.capture_pci);
        }
        let pool_name = CString::new(format!("hft_full_pipeline_{}", std::process::id()))?;
        let socket_id = unsafe { hft_dpdk_socket_id() };
        let mempool = unsafe {
            hft_dpdk_mempool_create(pool_name.as_ptr(), config.mempool_capacity, 256, socket_id)
        };
        if mempool.is_null() {
            bail!("rte_pktmbuf_pool_create failed");
        }
        environment.mempool = mempool;
        let mut actual_rx = 0u16;
        let mut actual_tx = 0u16;
        let status = unsafe {
            hft_dpdk_port_init(
                environment.port_id,
                mempool,
                REQUESTED_RX_DESCRIPTORS,
                REQUESTED_TX_DESCRIPTORS,
                config.queue_count as u16,
                FULL_PIPELINE_PORT_PROFILE,
                &mut actual_rx,
                &mut actual_tx,
            )
        };
        if status != 0 {
            bail!("initialize full-pipeline DPDK port failed: {status}");
        }
        let link_speed = wait_link(environment.port_id, config.minimum_link_speed_mbps)?;
        environment.configuration = DpdkPortConfiguration {
            port_id: environment.port_id,
            queue_count: config.queue_count,
            requested_rx_descriptors: REQUESTED_RX_DESCRIPTORS,
            actual_rx_descriptors: actual_rx,
            requested_tx_descriptors: REQUESTED_TX_DESCRIPTORS,
            actual_tx_descriptors: actual_tx,
            mempool_capacity: config.mempool_capacity,
            link_speed_mbps: link_speed,
        };
        Ok(environment)
    }

    pub fn port_id(&self) -> u16 {
        self.port_id
    }

    pub fn configuration(&self) -> DpdkPortConfiguration {
        self.configuration
    }

    pub fn stats(&self) -> Result<DpdkStats> {
        let mut stats = DpdkStats::default();
        let status = unsafe { hft_dpdk_port_stats(self.port_id, &mut stats) };
        if status != 0 {
            bail!("read DPDK port stats failed: {status}");
        }
        Ok(stats)
    }

    pub fn tsc_hz(&self) -> u64 {
        unsafe { hft_dpdk_tsc_hz() }
    }
}

impl Drop for DpdkEnvironment {
    fn drop(&mut self) {
        if self.active {
            if self.port_id != u16::MAX {
                unsafe { hft_dpdk_port_stop_close(self.port_id) };
            }
            if !self.mempool.is_null() {
                unsafe { hft_dpdk_mempool_free(self.mempool) };
                self.mempool = std::ptr::null_mut();
            }
            unsafe {
                let _ = hft_dpdk_eal_cleanup();
            }
            self.active = false;
        }
    }
}

pub struct DpdkRxQueue {
    port_id: u16,
    queue_id: u16,
    packets: Vec<*mut c_void>,
    registered: bool,
}

impl DpdkRxQueue {
    pub fn register(port_id: u16, queue_id: u16, burst_size: usize) -> Result<Self> {
        if burst_size == 0 || burst_size > u16::MAX as usize {
            bail!("DPDK burst size must be in 1..={}", u16::MAX);
        }
        let status = unsafe { hft_dpdk_thread_register() };
        if status != 0 {
            bail!("rte_thread_register failed: {status}");
        }
        Ok(Self {
            port_id,
            queue_id,
            packets: vec![std::ptr::null_mut(); burst_size],
            registered: true,
        })
    }

    pub fn poll(&mut self) -> DpdkBurst<'_> {
        let count = unsafe {
            hft_dpdk_rx_burst(
                self.port_id,
                self.queue_id,
                self.packets.as_mut_ptr(),
                self.packets.len() as u16,
            )
        } as usize;
        DpdkBurst {
            packets: &mut self.packets,
            count,
        }
    }
}

impl Drop for DpdkRxQueue {
    fn drop(&mut self) {
        if self.registered {
            unsafe { hft_dpdk_thread_unregister() };
            self.registered = false;
        }
    }
}

pub struct DpdkBurst<'a> {
    packets: &'a mut [*mut c_void],
    count: usize,
}

impl DpdkBurst<'_> {
    pub fn len(&self) -> usize {
        self.count
    }

    pub fn is_empty(&self) -> bool {
        self.count == 0
    }

    pub fn packet(&self, index: usize) -> Result<&[u8]> {
        if index >= self.count {
            bail!("DPDK packet index is outside the received burst");
        }
        let mut data = std::ptr::null();
        let mut length = 0u32;
        let status = unsafe { hft_dpdk_packet_view(self.packets[index], &mut data, &mut length) };
        if status != 0 || data.is_null() {
            bail!("DPDK packet is not a supported single-segment frame: {status}");
        }
        Ok(unsafe { std::slice::from_raw_parts(data, length as usize) })
    }
}

impl Drop for DpdkBurst<'_> {
    fn drop(&mut self) {
        if self.count != 0 {
            unsafe { hft_dpdk_free_burst(self.packets.as_mut_ptr(), self.count as u16) };
            self.count = 0;
        }
    }
}

pub fn rdtsc() -> u64 {
    unsafe { hft_dpdk_rdtsc() }
}

fn validate_file_prefix(value: &str) -> Result<()> {
    if value.is_empty()
        || value.len() > 64
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_'))
    {
        bail!("file prefix must contain 1..=64 ASCII letters, digits, '-' or '_'");
    }
    Ok(())
}

fn wait_link(port_id: u16, minimum_speed: u32) -> Result<u32> {
    let started = Instant::now();
    loop {
        let mut speed = 0u32;
        let mut up = 0u8;
        let status = unsafe { hft_dpdk_port_link(port_id, &mut speed, &mut up) };
        if status != 0 {
            bail!("query DPDK link failed: {status}");
        }
        if up == 1 && speed >= minimum_speed {
            return Ok(speed);
        }
        if started.elapsed() >= Duration::from_secs(10) {
            bail!(
                "DPDK link did not reach {} Mbps (speed={}, up={})",
                minimum_speed,
                speed,
                up
            );
        }
        thread::sleep(Duration::from_millis(100));
    }
}

#[cfg(test)]
mod tests {
    use super::{validate_file_prefix, DpdkStats};

    #[test]
    fn file_prefix_is_narrow_and_replayable() {
        assert!(validate_file_prefix("hft_full_01").is_ok());
        assert!(validate_file_prefix("").is_err());
        assert!(validate_file_prefix("../escape").is_err());
    }

    #[test]
    fn receive_drop_count_is_fail_closed_sum() {
        let stats = DpdkStats {
            imissed: 2,
            ierrors: 3,
            rx_nombuf: 5,
            ..DpdkStats::default()
        };
        assert_eq!(stats.receive_drop_count(), 10);
    }
}
