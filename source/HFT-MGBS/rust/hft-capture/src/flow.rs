use probe_agent::aggregator::{
    canonicalize_observation, FlowKey, FlowValue, ObservationScope, ObservedEndpoints,
    PacketInfo, PartitionedFlowTable,
};
use probe_agent::parser::{tcp_flags, ParsedPacket};
use serde::Serialize;
use std::collections::HashMap;
use std::sync::atomic::Ordering;
use std::time::Instant;

pub const RAW_FEATURE_ORDER: [&str; 38] = [
    "packet_protocol",
    "packet_src_port",
    "packet_dst_port",
    "flow_packets",
    "flow_bytes",
    "flow_payload_bytes",
    "flow_duration_s",
    "flow_mean_length",
    "flow_length_std",
    "flow_min_length",
    "flow_max_length",
    "flow_mean_iat_s",
    "flow_iat_std_s",
    "flow_tcp_flags_or",
    "flow_fwd_packets",
    "flow_bwd_packets",
    "flow_fwd_bytes",
    "flow_bwd_bytes",
    "flow_fwd_payload_bytes",
    "flow_bwd_payload_bytes",
    "flow_fwd_mean_iat_s",
    "flow_bwd_mean_iat_s",
    "flow_fwd_iat_std_s",
    "flow_bwd_iat_std_s",
    "flow_fwd_tcp_flags_or",
    "flow_bwd_tcp_flags_or",
    "flow_fin_flag_count",
    "flow_syn_flag_count",
    "flow_rst_flag_count",
    "flow_psh_flag_count",
    "flow_ack_flag_count",
    "flow_urg_flag_count",
    "flow_ece_flag_count",
    "flow_cwr_flag_count",
    "payload_entropy",
    "payload_printable_ratio",
    "payload_zero_ratio",
    "quality_seen_deep_tier",
];
const COMMON_SERVICE_PORTS: [u16; 14] = [
    21, 22, 23, 25, 53, 80, 110, 123, 143, 443, 445, 993, 995, 3389,
];

#[derive(Default)]
struct FlowExtras {
    first_ts_us: u64,
    last_ts_us: u64,
    last_packet_ts_us: u64,
    first_src_port: u16,
    first_dst_port: u16,
    protocol: u8,
    payload_bytes: u64,
    payload_fwd: u64,
    payload_bwd: u64,
    iat_sum_us: f64,
    iat_sum_sq_us: f64,
    flag_counts: [u64; 8],
    fin_fwd: bool,
    fin_bwd: bool,
    rst_seen: bool,
    payload_sample: Vec<u8>,
}

/// Worker-local statistics with the same integer accumulation and f32
/// materialization semantics as probe-agent's `FastStats`, but without atomics.
#[derive(Default)]
struct LocalFastStats {
    count: u64,
    sum: u64,
    sum_sq: u64,
    min: u32,
    max: u32,
}

impl LocalFastStats {
    #[inline(always)]
    fn update(&mut self, value: u32) {
        self.count += 1;
        self.sum += value as u64;
        self.sum_sq += (value as u64) * (value as u64);
        if self.count == 1 {
            self.min = value;
            self.max = value;
        } else {
            self.min = self.min.min(value);
            self.max = self.max.max(value);
        }
    }

    #[inline]
    fn mean(&self) -> f32 {
        if self.count == 0 {
            0.0
        } else {
            self.sum as f32 / self.count as f32
        }
    }

    #[inline]
    fn std(&self) -> f32 {
        if self.count <= 1 {
            return 0.0;
        }
        let mean = self.mean();
        let variance = self.sum_sq as f32 / self.count as f32 - mean * mean;
        if variance > 0.0 {
            variance.sqrt()
        } else {
            0.0
        }
    }
}

/// A UDP flow is owned by exactly one TPACKET worker after the runtime QM
/// affinity proof. Keeping its state local removes DashMap, atomic and
/// parallel `extras` table work from the per-packet UDP path.
#[derive(Default)]
struct LocalUdpFlowState {
    first_ts_us: u64,
    last_ts_us: u64,
    last_packet_ts_us: u64,
    first_src_port: u16,
    first_dst_port: u16,
    payload_bytes: u64,
    payload_fwd: u64,
    payload_bwd: u64,
    iat_sum_us: f64,
    iat_sum_sq_us: f64,
    packets_fwd: u64,
    packets_bwd: u64,
    bytes_fwd: u64,
    bytes_bwd: u64,
    pktlen_stats: LocalFastStats,
    iat_fwd_stats: LocalFastStats,
    iat_bwd_stats: LocalFastStats,
    last_pkt_time_fwd: u64,
    last_pkt_time_bwd: u64,
    // HighestDscp policy, retained for exact parity with the generic table
    // even though RAW_FEATURE_ORDER currently does not export TOS.
    tos: u8,
    payload_sample: Vec<u8>,
}

#[derive(Debug)]
pub struct ClosedFlow {
    pub flow_id: String,
    pub is_key_flow: bool,
    pub priority: f64,
    pub ready_at: Instant,
    pub trigger_timestamp_us: Option<u64>,
    base_features: Vec<f64>,
    payload_sample: Vec<u8>,
}

#[derive(Debug, Serialize)]
pub struct ScheduledFlow {
    #[serde(skip_serializing)]
    pub flow_id: String,
    #[serde(skip_serializing)]
    pub is_key_flow: bool,
    #[serde(skip_serializing)]
    pub ready_at: Instant,
    #[serde(skip_serializing)]
    pub trigger_timestamp_us: Option<u64>,
    pub features: Vec<f64>,
}

impl ClosedFlow {
    pub fn into_scheduled(self, include_deep: bool) -> ScheduledFlow {
        let mut features = self.base_features;
        if include_deep {
            let (entropy, printable, zero) = payload_statistics(&self.payload_sample);
            features[34] = entropy;
            features[35] = printable;
            features[36] = zero;
            features[37] = 1.0;
        } else {
            features[37] = 0.0;
        }
        ScheduledFlow {
            flow_id: self.flow_id,
            is_key_flow: self.is_key_flow,
            ready_at: self.ready_at,
            trigger_timestamp_us: self.trigger_timestamp_us,
            features,
        }
    }
}

#[cfg(test)]
pub(crate) fn test_closed_flow(flow_id: &str, is_key_flow: bool, priority: f64) -> ClosedFlow {
    ClosedFlow {
        flow_id: flow_id.to_string(),
        is_key_flow,
        priority,
        ready_at: Instant::now(),
        trigger_timestamp_us: None,
        base_features: vec![0.0; RAW_FEATURE_ORDER.len()],
        payload_sample: Vec::new(),
    }
}

pub struct HftFlowTable {
    table: PartitionedFlowTable,
    scope: ObservationScope,
    extras: HashMap<FlowKey, FlowExtras>,
    udp: HashMap<FlowKey, LocalUdpFlowState>,
    max_active_flows: usize,
    idle_timeout_us: u64,
    active_timeout_us: u64,
    max_payload_sample: usize,
}

impl HftFlowTable {
    pub fn new(
        max_active_flows: usize,
        idle_timeout_s: u64,
        active_timeout_s: u64,
        max_payload_sample: usize,
    ) -> Self {
        Self {
            table: PartitionedFlowTable::auto(max_active_flows),
            scope: ObservationScope::global_l3(),
            extras: HashMap::with_capacity(max_active_flows.min(1_000_000)),
            udp: HashMap::with_capacity(max_active_flows.min(1_000_000)),
            max_active_flows,
            idle_timeout_us: idle_timeout_s.saturating_mul(1_000_000),
            active_timeout_us: active_timeout_s.saturating_mul(1_000_000),
            max_payload_sample,
        }
    }

    pub fn update(&mut self, parsed: &ParsedPacket, frame: &[u8]) -> Vec<ClosedFlow> {
        let mut closed = Vec::new();
        self.update_into(parsed, frame, &mut closed);
        closed
    }

    /// Update one flow and append closures into a caller-owned batch.
    ///
    /// The live hot path uses this form so packets that do not close a flow do
    /// not allocate an empty `Vec` merely to extend the pending batch.
    pub fn update_into(
        &mut self,
        parsed: &ParsedPacket,
        frame: &[u8],
        closed: &mut Vec<ClosedFlow>,
    ) {
        if parsed.protocol == 17 {
            self.update_udp_into(parsed, frame, closed);
        } else {
            self.update_general_into(parsed, frame, closed);
        }
    }

    fn update_general_into(
        &mut self,
        parsed: &ParsedPacket,
        frame: &[u8],
        closed: &mut Vec<ClosedFlow>,
    ) {
        let Ok(identity) = canonicalize_observation(ObservedEndpoints {
            src_ip: parsed.src_ip,
            dst_ip: parsed.dst_ip,
            src_port: parsed.src_port,
            dst_port: parsed.dst_port,
            protocol: parsed.protocol,
        }) else {
            return;
        };
        let is_forward = identity.packet_direction.is_forward();
        let key = FlowKey::new(&identity, &self.scope);
        let packet = PacketInfo::new(
            parsed.total_len,
            parsed.tcp_flags,
            is_forward,
            parsed.timestamp,
            parsed.tos,
        );
        if self
            .table
            .update_with_time(&key, &packet, parsed.timestamp / 1000)
            .is_err()
        {
            return;
        }

        let extras = self
            .extras
            .entry(key.clone())
            .or_insert_with(|| FlowExtras {
                first_ts_us: parsed.timestamp,
                last_ts_us: parsed.timestamp,
                last_packet_ts_us: parsed.timestamp,
                first_src_port: parsed.src_port,
                first_dst_port: parsed.dst_port,
                protocol: parsed.protocol,
                ..FlowExtras::default()
            });
        if extras.last_packet_ts_us > 0 && parsed.timestamp >= extras.last_packet_ts_us {
            let iat = (parsed.timestamp - extras.last_packet_ts_us) as f64;
            extras.iat_sum_us += iat;
            extras.iat_sum_sq_us += iat * iat;
        }
        extras.last_packet_ts_us = parsed.timestamp;
        extras.last_ts_us = extras.last_ts_us.max(parsed.timestamp);
        extras.payload_bytes += parsed.payload_len as u64;
        if is_forward {
            extras.payload_fwd += parsed.payload_len as u64;
        } else {
            extras.payload_bwd += parsed.payload_len as u64;
        }
        update_tcp_control_state(extras, parsed.tcp_flags, is_forward);
        if extras.payload_sample.len() < self.max_payload_sample {
            let remaining = self.max_payload_sample - extras.payload_sample.len();
            let payload = payload_slice(frame);
            extras
                .payload_sample
                .extend_from_slice(&payload[..payload.len().min(remaining)]);
        }

        let close_now = extras.rst_seen || (extras.fin_fwd && extras.fin_bwd);
        if close_now {
            if let Some(flow) = self.remove_and_materialize(&key, Some(parsed.timestamp)) {
                closed.push(flow);
            }
        } else {
            self.evict_oldest_if_needed(parsed.timestamp, closed);
        }
    }

    #[inline]
    fn update_udp_into(
        &mut self,
        parsed: &ParsedPacket,
        frame: &[u8],
        closed: &mut Vec<ClosedFlow>,
    ) {
        debug_assert_eq!(parsed.protocol, 17);
        debug_assert_eq!(parsed.tcp_flags, 0);
        let Ok(identity) = canonicalize_observation(ObservedEndpoints {
            src_ip: parsed.src_ip,
            dst_ip: parsed.dst_ip,
            src_port: parsed.src_port,
            dst_port: parsed.dst_port,
            protocol: parsed.protocol,
        }) else {
            return;
        };
        let is_forward = identity.packet_direction.is_forward();
        let key = FlowKey::new(&identity, &self.scope);
        let state = self.udp.entry(key).or_insert_with(|| LocalUdpFlowState {
            first_ts_us: parsed.timestamp,
            last_ts_us: parsed.timestamp,
            last_packet_ts_us: parsed.timestamp,
            first_src_port: parsed.src_port,
            first_dst_port: parsed.dst_port,
            ..LocalUdpFlowState::default()
        });

        if state.last_packet_ts_us > 0 && parsed.timestamp >= state.last_packet_ts_us {
            let iat = (parsed.timestamp - state.last_packet_ts_us) as f64;
            state.iat_sum_us += iat;
            state.iat_sum_sq_us += iat * iat;
        }
        state.last_packet_ts_us = parsed.timestamp;
        state.last_ts_us = state.last_ts_us.max(parsed.timestamp);
        state.payload_bytes += parsed.payload_len as u64;
        if is_forward {
            state.packets_fwd += 1;
            state.bytes_fwd += parsed.total_len as u64;
            state.payload_fwd += parsed.payload_len as u64;
            update_directional_iat(
                &mut state.last_pkt_time_fwd,
                &mut state.iat_fwd_stats,
                parsed.timestamp,
            );
        } else {
            state.packets_bwd += 1;
            state.bytes_bwd += parsed.total_len as u64;
            state.payload_bwd += parsed.payload_len as u64;
            update_directional_iat(
                &mut state.last_pkt_time_bwd,
                &mut state.iat_bwd_stats,
                parsed.timestamp,
            );
        }
        state.pktlen_stats.update(parsed.total_len as u32);
        update_highest_dscp(&mut state.tos, parsed.tos);
        if state.payload_sample.len() < self.max_payload_sample {
            let remaining = self.max_payload_sample - state.payload_sample.len();
            let payload = payload_slice(frame);
            state
                .payload_sample
                .extend_from_slice(&payload[..payload.len().min(remaining)]);
        }
        self.evict_oldest_if_needed(parsed.timestamp, closed);
    }

    fn evict_oldest_if_needed(&mut self, trigger_timestamp_us: u64, closed: &mut Vec<ClosedFlow>) {
        if self.extras.len() + self.udp.len() <= self.max_active_flows {
            return;
        }
        let general_oldest = self
            .extras
            .iter()
            .min_by_key(|(_, value)| value.last_ts_us)
            .map(|(key, value)| (key.clone(), value.last_ts_us));
        let udp_oldest = self
            .udp
            .iter()
            .min_by_key(|(_, value)| value.last_ts_us)
            .map(|(key, value)| (key.clone(), value.last_ts_us));
        let close_udp = match (&general_oldest, &udp_oldest) {
            (None, Some(_)) => true,
            (Some(_), None) => false,
            (Some((_, general_ts)), Some((_, udp_ts))) => udp_ts < general_ts,
            (None, None) => return,
        };
        let flow = if close_udp {
            self.remove_and_materialize_udp(
                &udp_oldest.expect("present").0,
                Some(trigger_timestamp_us),
            )
        } else {
            self.remove_and_materialize(
                &general_oldest.expect("present").0,
                Some(trigger_timestamp_us),
            )
        };
        if let Some(flow) = flow {
            closed.push(flow);
        }
    }

    pub fn expire(&mut self, now_us: u64) -> Vec<ClosedFlow> {
        let mut keys: Vec<(FlowKey, bool)> = self
            .extras
            .iter()
            .filter(|(_, value)| {
                now_us.saturating_sub(value.last_ts_us) >= self.idle_timeout_us
                    || value.last_ts_us.saturating_sub(value.first_ts_us) >= self.active_timeout_us
            })
            .map(|(key, _)| (key.clone(), false))
            .chain(
                self.udp
                    .iter()
                    .filter(|(_, value)| {
                        now_us.saturating_sub(value.last_ts_us) >= self.idle_timeout_us
                            || value.last_ts_us.saturating_sub(value.first_ts_us)
                                >= self.active_timeout_us
                    })
                    .map(|(key, _)| (key.clone(), true)),
            )
            .collect();
        keys.sort_by(|left, right| stable_flow_key_cmp(&left.0, &right.0));
        keys.into_iter()
            .filter_map(|(key, udp)| {
                if udp {
                    self.remove_and_materialize_udp(&key, Some(now_us))
                } else {
                    self.remove_and_materialize(&key, Some(now_us))
                }
            })
            .collect()
    }

    pub fn flush(&mut self) -> Vec<ClosedFlow> {
        let mut keys: Vec<(FlowKey, bool)> = self
            .extras
            .keys()
            .cloned()
            .map(|key| (key, false))
            .chain(self.udp.keys().cloned().map(|key| (key, true)))
            .collect();
        keys.sort_by(|left, right| stable_flow_key_cmp(&left.0, &right.0));
        keys.into_iter()
            .filter_map(|(key, udp)| {
                if udp {
                    self.remove_and_materialize_udp(&key, None)
                } else {
                    self.remove_and_materialize(&key, None)
                }
            })
            .collect()
    }

    fn remove_and_materialize(
        &mut self,
        key: &FlowKey,
        trigger_timestamp_us: Option<u64>,
    ) -> Option<ClosedFlow> {
        let ready_at = Instant::now();
        let extras = self.extras.remove(key)?;
        let (_, value) = self.table.remove(key)?;
        Some(materialize(
            key,
            &value,
            extras,
            ready_at,
            trigger_timestamp_us,
        ))
    }

    fn remove_and_materialize_udp(
        &mut self,
        key: &FlowKey,
        trigger_timestamp_us: Option<u64>,
    ) -> Option<ClosedFlow> {
        let ready_at = Instant::now();
        let state = self.udp.remove(key)?;
        Some(materialize_udp(key, state, ready_at, trigger_timestamp_us))
    }
}

#[inline(always)]
fn update_directional_iat(last: &mut u64, stats: &mut LocalFastStats, timestamp_us: u64) {
    let previous = *last;
    *last = timestamp_us;
    if previous > 0 && timestamp_us >= previous {
        let iat = timestamp_us - previous;
        if iat <= 3_600_000_000 {
            stats.update(iat as u32);
        }
    }
}

#[inline(always)]
fn update_highest_dscp(current_tos: &mut u8, packet_tos: u8) {
    if packet_tos != 0 && packet_tos >> 2 > *current_tos >> 2 {
        *current_tos = packet_tos;
    }
}

/// Update TCP-only control state without paying eight flag tests for the
/// dominant UDP path (`tcp_flags == 0`). Iterating only set bits is exactly
/// equivalent to the previous fixed 0..8 loop for every possible u8 value.
#[inline]
fn update_tcp_control_state(extras: &mut FlowExtras, tcp_flags: u8, is_forward: bool) {
    if tcp_flags == 0 {
        return;
    }
    let mut remaining = tcp_flags;
    while remaining != 0 {
        let bit = remaining.trailing_zeros() as usize;
        extras.flag_counts[bit] += 1;
        remaining &= remaining - 1;
    }
    if is_forward {
        extras.fin_fwd |= tcp_flags & tcp_flags::FIN != 0;
    } else {
        extras.fin_bwd |= tcp_flags & tcp_flags::FIN != 0;
    }
    extras.rst_seen |= tcp_flags & tcp_flags::RST != 0;
}

fn stable_flow_key_cmp(left: &FlowKey, right: &FlowKey) -> std::cmp::Ordering {
    left.src_ip
        .cmp(&right.src_ip)
        .then_with(|| left.src_port.cmp(&right.src_port))
        .then_with(|| left.dst_ip.cmp(&right.dst_ip))
        .then_with(|| left.dst_port.cmp(&right.dst_port))
        .then_with(|| left.protocol.cmp(&right.protocol))
}

fn materialize(
    key: &FlowKey,
    value: &FlowValue,
    extras: FlowExtras,
    ready_at: Instant,
    trigger_timestamp_us: Option<u64>,
) -> ClosedFlow {
    let packets_fwd = value.packets_fwd.load(Ordering::Relaxed);
    let packets_bwd = value.packets_bwd.load(Ordering::Relaxed);
    let bytes_fwd = value.bytes_fwd.load(Ordering::Relaxed);
    let bytes_bwd = value.bytes_bwd.load(Ordering::Relaxed);
    let packets = packets_fwd + packets_bwd;
    let bytes = bytes_fwd + bytes_bwd;
    let duration_s = extras.last_ts_us.saturating_sub(extras.first_ts_us) as f64 / 1_000_000.0;
    let iat_count = packets.saturating_sub(1).max(1) as f64;
    let mean_iat_us = extras.iat_sum_us / iat_count;
    let iat_var_us = (extras.iat_sum_sq_us / iat_count - mean_iat_us * mean_iat_us).max(0.0);
    let mut features = vec![0.0; RAW_FEATURE_ORDER.len()];
    features[0] = extras.protocol as f64;
    features[1] = extras.first_src_port as f64;
    features[2] = extras.first_dst_port as f64;
    features[3] = packets as f64;
    features[4] = bytes as f64;
    features[5] = extras.payload_bytes as f64;
    features[6] = duration_s;
    features[7] = value.pktlen_stats.mean() as f64;
    features[8] = value.pktlen_stats.std() as f64;
    features[9] = value.pktlen_stats.min() as f64;
    features[10] = value.pktlen_stats.max() as f64;
    features[11] = mean_iat_us / 1_000_000.0;
    features[12] = iat_var_us.sqrt() / 1_000_000.0;
    let flags_fwd = value.tcp_flags_fwd.load(Ordering::Relaxed);
    let flags_bwd = value.tcp_flags_bwd.load(Ordering::Relaxed);
    features[13] = (flags_fwd | flags_bwd) as f64;
    features[14] = packets_fwd as f64;
    features[15] = packets_bwd as f64;
    features[16] = bytes_fwd as f64;
    features[17] = bytes_bwd as f64;
    features[18] = extras.payload_fwd as f64;
    features[19] = extras.payload_bwd as f64;
    features[20] = value.iat_fwd_stats.mean() as f64 / 1_000_000.0;
    features[21] = value.iat_bwd_stats.mean() as f64 / 1_000_000.0;
    features[22] = value.iat_fwd_stats.std() as f64 / 1_000_000.0;
    features[23] = value.iat_bwd_stats.std() as f64 / 1_000_000.0;
    features[24] = flags_fwd as f64;
    features[25] = flags_bwd as f64;
    for (index, count) in extras.flag_counts.iter().enumerate() {
        features[26 + index] = *count as f64;
    }
    let is_key_flow = COMMON_SERVICE_PORTS.contains(&key.src_port)
        || COMMON_SERVICE_PORTS.contains(&key.dst_port)
        || extras.rst_seen
        || bytes >= 1_000_000;
    let priority = (packets as f64 + 1.0).ln()
        + (bytes as f64 + 1.0).ln() / 10.0
        + if is_key_flow { 10.0 } else { 0.0 };
    ClosedFlow {
        flow_id: format!(
            "{}:{}-{}:{}/{}",
            key.src_ip, key.src_port, key.dst_ip, key.dst_port, key.protocol
        ),
        is_key_flow,
        priority,
        ready_at,
        trigger_timestamp_us,
        base_features: features,
        payload_sample: extras.payload_sample,
    }
}

fn materialize_udp(
    key: &FlowKey,
    state: LocalUdpFlowState,
    ready_at: Instant,
    trigger_timestamp_us: Option<u64>,
) -> ClosedFlow {
    let packets = state.packets_fwd + state.packets_bwd;
    let bytes = state.bytes_fwd + state.bytes_bwd;
    let duration_s = state.last_ts_us.saturating_sub(state.first_ts_us) as f64 / 1_000_000.0;
    let iat_count = packets.saturating_sub(1).max(1) as f64;
    let mean_iat_us = state.iat_sum_us / iat_count;
    let iat_var_us = (state.iat_sum_sq_us / iat_count - mean_iat_us * mean_iat_us).max(0.0);
    let mut features = vec![0.0; RAW_FEATURE_ORDER.len()];
    features[0] = 17.0;
    features[1] = state.first_src_port as f64;
    features[2] = state.first_dst_port as f64;
    features[3] = packets as f64;
    features[4] = bytes as f64;
    features[5] = state.payload_bytes as f64;
    features[6] = duration_s;
    features[7] = state.pktlen_stats.mean() as f64;
    features[8] = state.pktlen_stats.std() as f64;
    features[9] = state.pktlen_stats.min as f64;
    features[10] = state.pktlen_stats.max as f64;
    features[11] = mean_iat_us / 1_000_000.0;
    features[12] = iat_var_us.sqrt() / 1_000_000.0;
    features[14] = state.packets_fwd as f64;
    features[15] = state.packets_bwd as f64;
    features[16] = state.bytes_fwd as f64;
    features[17] = state.bytes_bwd as f64;
    features[18] = state.payload_fwd as f64;
    features[19] = state.payload_bwd as f64;
    features[20] = state.iat_fwd_stats.mean() as f64 / 1_000_000.0;
    features[21] = state.iat_bwd_stats.mean() as f64 / 1_000_000.0;
    features[22] = state.iat_fwd_stats.std() as f64 / 1_000_000.0;
    features[23] = state.iat_bwd_stats.std() as f64 / 1_000_000.0;
    // UDP tcp_flags and all eight flag counts are zero by construction.
    let is_key_flow = COMMON_SERVICE_PORTS.contains(&key.src_port)
        || COMMON_SERVICE_PORTS.contains(&key.dst_port)
        || bytes >= 1_000_000;
    let priority = (packets as f64 + 1.0).ln()
        + (bytes as f64 + 1.0).ln() / 10.0
        + if is_key_flow { 10.0 } else { 0.0 };
    ClosedFlow {
        flow_id: format!(
            "{}:{}-{}:{}/{}",
            key.src_ip, key.src_port, key.dst_ip, key.dst_port, key.protocol
        ),
        is_key_flow,
        priority,
        ready_at,
        trigger_timestamp_us,
        base_features: features,
        payload_sample: state.payload_sample,
    }
}

fn payload_statistics(payload: &[u8]) -> (f64, f64, f64) {
    if payload.is_empty() {
        return (0.0, 0.0, 0.0);
    }
    let mut counts = [0u32; 256];
    let mut printable = 0usize;
    let mut zero = 0usize;
    for byte in payload {
        counts[*byte as usize] += 1;
        printable += usize::from((32..=126).contains(byte));
        zero += usize::from(*byte == 0);
    }
    let total = payload.len() as f64;
    let entropy = counts
        .iter()
        .filter(|count| **count > 0)
        .map(|count| {
            let p = *count as f64 / total;
            -p * p.log2()
        })
        .sum();
    (entropy, printable as f64 / total, zero as f64 / total)
}

fn payload_slice(frame: &[u8]) -> &[u8] {
    if frame.len() < 14 {
        return &[];
    }
    let mut offset = 14usize;
    let mut ether_type = u16::from_be_bytes([frame[12], frame[13]]);
    while matches!(ether_type, 0x8100 | 0x88a8) && frame.len() >= offset + 4 {
        ether_type = u16::from_be_bytes([frame[offset + 2], frame[offset + 3]]);
        offset += 4;
    }
    match ether_type {
        0x0800 if frame.len() >= offset + 20 => {
            let ihl = ((frame[offset] & 0x0f) as usize) * 4;
            let protocol = frame[offset + 9];
            let transport = offset + ihl;
            transport_payload(frame, transport, protocol)
        }
        0x86dd if frame.len() >= offset + 40 => {
            let protocol = frame[offset + 6];
            transport_payload(frame, offset + 40, protocol)
        }
        _ => &[],
    }
}

fn transport_payload(frame: &[u8], offset: usize, protocol: u8) -> &[u8] {
    match protocol {
        6 if frame.len() >= offset + 20 => {
            let header = ((frame[offset + 12] >> 4) as usize) * 4;
            frame.get(offset + header..).unwrap_or(&[])
        }
        17 if frame.len() >= offset + 8 => frame.get(offset + 8..).unwrap_or(&[]),
        _ => frame.get(offset..).unwrap_or(&[]),
    }
}

#[cfg(test)]
mod tests {
    use super::{
        payload_statistics, update_tcp_control_state, ClosedFlow, FlowExtras, HftFlowTable,
        RAW_FEATURE_ORDER,
    };
    use probe_agent::parser::{tcp_flags, ParsedPacket};
    use std::net::{IpAddr, Ipv4Addr};
    use std::time::Instant;

    fn udp_packet(
        reverse: bool,
        timestamp: u64,
        total_len: u16,
        payload_len: u16,
        tos: u8,
    ) -> ParsedPacket {
        let (src_ip, dst_ip, src_port, dst_port) = if reverse {
            (
                Ipv4Addr::new(198, 51, 100, 9),
                Ipv4Addr::new(192, 0, 2, 7),
                53,
                40_001,
            )
        } else {
            (
                Ipv4Addr::new(192, 0, 2, 7),
                Ipv4Addr::new(198, 51, 100, 9),
                40_001,
                53,
            )
        };
        ParsedPacket {
            src_ip: IpAddr::V4(src_ip),
            dst_ip: IpAddr::V4(dst_ip),
            src_port,
            dst_port,
            protocol: 17,
            tcp_flags: 0,
            payload_len,
            total_len,
            timestamp,
            tos,
            ..ParsedPacket::default()
        }
    }

    fn udp_frame(payload: &[u8]) -> Vec<u8> {
        let mut frame = vec![0u8; 14 + 20 + 8];
        frame[12..14].copy_from_slice(&0x0800u16.to_be_bytes());
        frame[14] = 0x45;
        frame[23] = 17;
        frame.extend_from_slice(payload);
        frame
    }

    fn compare_closed(mut fast: Vec<ClosedFlow>, mut legacy: Vec<ClosedFlow>) {
        fast.sort_by(|a, b| a.flow_id.cmp(&b.flow_id));
        legacy.sort_by(|a, b| a.flow_id.cmp(&b.flow_id));
        assert_eq!(fast.len(), legacy.len());
        for (fast, legacy) in fast.into_iter().zip(legacy) {
            assert_eq!(fast.flow_id, legacy.flow_id);
            assert_eq!(fast.is_key_flow, legacy.is_key_flow);
            assert_eq!(fast.priority.to_bits(), legacy.priority.to_bits());
            assert_eq!(fast.trigger_timestamp_us, legacy.trigger_timestamp_us);
            assert_eq!(fast.payload_sample, legacy.payload_sample);
            let fast_features = fast.into_scheduled(true).features;
            let legacy_features = legacy.into_scheduled(true).features;
            assert_eq!(fast_features.len(), RAW_FEATURE_ORDER.len());
            for (index, (actual, expected)) in
                fast_features.iter().zip(&legacy_features).enumerate()
            {
                assert_eq!(
                    actual.to_bits(),
                    expected.to_bits(),
                    "feature[{}]={}: actual={actual:?} expected={expected:?}",
                    index,
                    RAW_FEATURE_ORDER[index]
                );
            }
        }
    }

    fn feed_both(
        fast: &mut HftFlowTable,
        legacy: &mut HftFlowTable,
        packet: &ParsedPacket,
        frame: &[u8],
    ) {
        let mut unexpected = Vec::new();
        fast.update_into(packet, frame, &mut unexpected);
        assert!(unexpected.is_empty());
        legacy.update_general_into(packet, frame, &mut unexpected);
        assert!(unexpected.is_empty());
    }

    #[test]
    fn entropy_handles_empty_and_uniform_payloads() {
        assert_eq!(payload_statistics(&[]), (0.0, 0.0, 0.0));
        let (entropy, printable, zero) = payload_statistics(&[0, 0, 0, 0]);
        assert_eq!(entropy, 0.0);
        assert_eq!(printable, 0.0);
        assert_eq!(zero, 1.0);
    }

    #[test]
    fn scheduled_feature_vector_preserves_frozen_indices() {
        let mut base_features = vec![0.0; RAW_FEATURE_ORDER.len()];
        base_features[0] = 6.0;
        base_features[3] = 42.0;
        let flow = ClosedFlow {
            flow_id: "test-flow".to_string(),
            is_key_flow: true,
            priority: 10.0,
            ready_at: Instant::now(),
            trigger_timestamp_us: Some(1),
            base_features,
            payload_sample: vec![0, 0, 0, 0],
        };

        let scheduled = flow.into_scheduled(true);

        assert_eq!(scheduled.features.len(), RAW_FEATURE_ORDER.len());
        assert_eq!(scheduled.features[0], 6.0);
        assert_eq!(scheduled.features[3], 42.0);
        assert_eq!(scheduled.features[34], 0.0);
        assert_eq!(scheduled.features[35], 0.0);
        assert_eq!(scheduled.features[36], 1.0);
        assert_eq!(scheduled.features[37], 1.0);
    }

    #[test]
    fn zero_tcp_flags_leave_control_state_untouched() {
        let mut extras = FlowExtras {
            flag_counts: [3, 5, 7, 11, 13, 17, 19, 23],
            fin_fwd: true,
            fin_bwd: false,
            rst_seen: true,
            ..FlowExtras::default()
        };
        let before = (
            extras.flag_counts,
            extras.fin_fwd,
            extras.fin_bwd,
            extras.rst_seen,
        );
        update_tcp_control_state(&mut extras, 0, false);
        assert_eq!(
            before,
            (
                extras.flag_counts,
                extras.fin_fwd,
                extras.fin_bwd,
                extras.rst_seen
            )
        );
    }

    #[test]
    fn sparse_flag_update_matches_fixed_eight_bit_reference_exhaustively() {
        for flags in 0u8..=u8::MAX {
            for is_forward in [false, true] {
                let mut actual = FlowExtras::default();
                update_tcp_control_state(&mut actual, flags, is_forward);

                let mut expected_counts = [0u64; 8];
                for bit in 0..8 {
                    if flags & (1 << bit) != 0 {
                        expected_counts[bit] += 1;
                    }
                }
                assert_eq!(actual.flag_counts, expected_counts, "flags={flags:#04x}");
                assert_eq!(actual.fin_fwd, is_forward && flags & tcp_flags::FIN != 0);
                assert_eq!(actual.fin_bwd, !is_forward && flags & tcp_flags::FIN != 0);
                assert_eq!(actual.rst_seen, flags & tcp_flags::RST != 0);
            }
        }
    }

    #[test]
    fn udp_local_fast_path_matches_generic_features_for_fixed_bidirectional_sequence() {
        let mut fast = HftFlowTable::new(128, 60, 60, 96);
        let mut legacy = HftFlowTable::new(128, 60, 60, 96);
        let cases = [
            (false, 1_000_000, 64, 22, 0x04, b"alpha".as_slice()),
            (true, 1_000_017, 1514, 1472, 0xb9, b"BETA\0".as_slice()),
            (false, 1_001_101, 128, 86, 0xfc, b"gamma".as_slice()),
            (true, 1_004_003, 300, 258, 0x2e, b"delta".as_slice()),
        ];
        for (reverse, ts, total, payload_len, tos, bytes) in cases {
            feed_both(
                &mut fast,
                &mut legacy,
                &udp_packet(reverse, ts, total, payload_len, tos),
                &udp_frame(bytes),
            );
        }
        compare_closed(fast.flush(), legacy.flush());
    }

    #[test]
    fn udp_local_fast_path_matches_generic_features_for_randomized_sequences() {
        let mut fast = HftFlowTable::new(512, 60, 60, 128);
        let mut legacy = HftFlowTable::new(512, 60, 60, 128);
        let mut seed = 0x6a09_e667_f3bc_c909u64;
        let mut timestamp = 7_000_000u64;
        for index in 0..2_000 {
            seed = seed.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1);
            timestamp += 1 + (seed >> 32) % 20_000;
            let reverse = seed & 1 != 0;
            let total = 64 + ((seed >> 9) % 1_451) as u16;
            let payload_len = total.saturating_sub(42);
            let tos = (seed >> 24) as u8;
            let payload = seed.to_le_bytes();
            feed_both(
                &mut fast,
                &mut legacy,
                &udp_packet(reverse, timestamp, total, payload_len, tos),
                &udp_frame(&payload),
            );
            assert_eq!(
                index + 1,
                fast.udp.values().next().unwrap().pktlen_stats.count as usize
            );
        }
        let fast_state = fast.udp.values().next().unwrap();
        let legacy_tos = legacy.table.iter().next().unwrap().get_tos();
        assert_eq!(fast_state.tos, legacy_tos, "HighestDscp TOS must match");
        compare_closed(fast.flush(), legacy.flush());
    }

    #[test]
    fn udp_local_fast_path_matches_active_idle_expiry_and_flush() {
        let frame = udp_frame(b"expiry-fixture");

        let mut fast = HftFlowTable::new(16, 30, 1, 64);
        let mut legacy = HftFlowTable::new(16, 30, 1, 64);
        for ts in [1_000_000, 1_500_000, 2_000_000] {
            feed_both(
                &mut fast,
                &mut legacy,
                &udp_packet(false, ts, 96, 54, 0),
                &frame,
            );
        }
        compare_closed(fast.expire(2_000_000), legacy.expire(2_000_000));
        assert!(fast.flush().is_empty());
        assert!(legacy.flush().is_empty());

        let mut fast = HftFlowTable::new(16, 1, 30, 64);
        let mut legacy = HftFlowTable::new(16, 1, 30, 64);
        feed_both(
            &mut fast,
            &mut legacy,
            &udp_packet(false, 5_000_000, 96, 54, 0),
            &frame,
        );
        assert!(fast.expire(5_999_999).is_empty());
        assert!(legacy.expire(5_999_999).is_empty());
        compare_closed(fast.expire(6_000_000), legacy.expire(6_000_000));

        let mut fast = HftFlowTable::new(16, 30, 30, 64);
        let mut legacy = HftFlowTable::new(16, 30, 30, 64);
        feed_both(
            &mut fast,
            &mut legacy,
            &udp_packet(true, 8_000_000, 96, 54, 0),
            &frame,
        );
        compare_closed(fast.flush(), legacy.flush());
    }

    #[test]
    fn udp_local_fast_path_canonicalizes_both_directions_and_keeps_udp_flags_zero() {
        let mut fast = HftFlowTable::new(16, 30, 30, 64);
        let frame = udp_frame(b"canonical");
        let mut closed = Vec::new();
        fast.update_into(
            &udp_packet(true, 10_000_000, 100, 58, 0),
            &frame,
            &mut closed,
        );
        fast.update_into(
            &udp_packet(false, 10_000_010, 200, 158, 0),
            &frame,
            &mut closed,
        );
        assert!(closed.is_empty());
        assert_eq!(fast.udp.len(), 1);
        let scheduled = fast.flush().pop().unwrap().into_scheduled(false);
        assert_eq!(scheduled.features[3], 2.0);
        assert_eq!(scheduled.features[14], 1.0);
        assert_eq!(scheduled.features[15], 1.0);
        for index in 13..=13 {
            assert_eq!(scheduled.features[index], 0.0);
        }
        for index in 24..=33 {
            assert_eq!(scheduled.features[index], 0.0);
        }
    }

    #[test]
    #[ignore = "informational release microbenchmark; run explicitly"]
    fn microbench_udp_local_state_against_generic_partitioned_table() {
        use std::hint::black_box;
        const ITERATIONS: usize = 2_000_000;
        let frame = udp_frame(b"bench");
        let mut packet = udp_packet(false, 1_000_000, 64, 22, 0);

        let mut fast = HftFlowTable::new(256, 60, 60, 0);
        let mut sink = Vec::new();
        let fast_started = Instant::now();
        for index in 0..ITERATIONS {
            packet.timestamp = 1_000_000 + index as u64;
            packet.src_port = 40_000 + (index % 145) as u16;
            fast.update_udp_into(black_box(&packet), black_box(&frame), &mut sink);
        }
        let fast_elapsed = fast_started.elapsed();

        let mut legacy = HftFlowTable::new(256, 60, 60, 0);
        let legacy_started = Instant::now();
        for index in 0..ITERATIONS {
            packet.timestamp = 1_000_000 + index as u64;
            packet.src_port = 40_000 + (index % 145) as u16;
            legacy.update_general_into(black_box(&packet), black_box(&frame), &mut sink);
        }
        let legacy_elapsed = legacy_started.elapsed();
        compare_closed(fast.flush(), legacy.flush());
        eprintln!(
            "udp_local_state iterations={ITERATIONS} fast_ns={} generic_ns={} speedup={:.3}",
            fast_elapsed.as_nanos(),
            legacy_elapsed.as_nanos(),
            legacy_elapsed.as_secs_f64() / fast_elapsed.as_secs_f64()
        );
    }

    #[test]
    #[ignore = "informational release microbenchmark; run explicitly"]
    fn microbench_udp_zero_flag_fast_path_against_fixed_loop() {
        use std::hint::black_box;
        use std::time::Instant;
        const ITERATIONS: usize = 20_000_000;
        let mut optimized = FlowExtras::default();
        let optimized_started = Instant::now();
        for _ in 0..ITERATIONS {
            update_tcp_control_state(black_box(&mut optimized), black_box(0), true);
        }
        let optimized_elapsed = optimized_started.elapsed();

        let mut reference = FlowExtras::default();
        let reference_started = Instant::now();
        for _ in 0..ITERATIONS {
            for bit in 0..8 {
                if black_box(0u8) & (1 << bit) != 0 {
                    reference.flag_counts[bit] += 1;
                }
            }
            reference.fin_fwd |= black_box(0u8) & tcp_flags::FIN != 0;
            reference.rst_seen |= black_box(0u8) & tcp_flags::RST != 0;
        }
        let reference_elapsed = reference_started.elapsed();
        assert_eq!(optimized.flag_counts, reference.flag_counts);
        eprintln!(
            "udp_zero_flag_fast_path iterations={ITERATIONS} optimized_ns={} reference_ns={} speedup={:.3}",
            optimized_elapsed.as_nanos(),
            reference_elapsed.as_nanos(),
            reference_elapsed.as_secs_f64() / optimized_elapsed.as_secs_f64()
        );
    }
}
