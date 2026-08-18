//! Pure, fail-closed XDP-primary/DPDK-fallback decision engine.
//!
//! This module consumes immutable JSON-compatible observations. It contains no
//! attach, PCI bind, sysfs, process-launch, or network mutation operations.

use serde::{Deserialize, Serialize};

pub const NATIVE_XDP_BACKEND: &str = "native_af_xdp_zerocopy";
pub const GENERIC_XDP_BACKEND: &str = "generic_xdp_skb";
pub const DPDK_BACKEND: &str = "dpdk";
pub const NO_BACKEND: &str = "none";

#[derive(Debug, Clone, Deserialize)]
pub struct RuntimePolicy {
    pub schema_version: u32,
    pub policy_id: String,
    pub backend_priority: Vec<String>,
    pub semantic_guards: SemanticGuards,
    pub freshness: FreshnessPolicy,
    pub xdp_requirements: XdpRequirements,
    pub dpdk_requirements: DpdkRequirements,
    pub online_gates: OnlineGates,
    pub switch_safety: SwitchSafety,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SemanticGuards {
    pub generic_xdp_skb_is_native: bool,
    pub generic_xdp_skb_is_zerocopy: bool,
    pub generic_xdp_skb_production_eligible: bool,
    pub empty_key_flow_denominator_is_qualified: bool,
    pub same_pf_rebind_is_automatic: bool,
}

#[derive(Debug, Clone, Deserialize)]
pub struct FreshnessPolicy {
    pub observation_max_age_s: f64,
    pub capability_max_age_s: f64,
    pub max_future_clock_skew_s: f64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct XdpRequirements {
    pub attach_mode: String,
    pub af_xdp_bind_mode: String,
    pub min_rx_queues: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DpdkRequirements {
    pub capture_headroom_mpps: f64,
    pub min_rx_queues: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct OnlineGates {
    pub evaluation_windows: usize,
    pub max_capture_drop_rate: f64,
    pub max_poll_errors: u64,
    pub max_invalid_descriptors: u64,
    pub max_ring_full: u64,
    pub max_fill_empty: u64,
    pub max_host_cpu_fraction: f64,
    pub max_memory_fraction: f64,
    pub max_budget_overrun_count: u64,
    pub max_fallback_recovery_ms: f64,
    pub kernel_to_feature_p99_us_max: f64,
    pub kernel_to_feature_p999_us_max: f64,
    pub min_key_flow_coverage: f64,
    pub key_flow_coverage_basis: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SwitchSafety {
    pub automatic_topologies: Vec<String>,
    pub maintenance_topologies: Vec<String>,
    pub required_handoff_flags: Vec<String>,
    pub decision_engine_performs_mutations: bool,
}

#[derive(Debug, Clone, Deserialize)]
pub struct RuntimeObservation {
    pub schema_version: u32,
    pub observed_at_utc: String,
    pub current_backend: String,
    pub capabilities: Capabilities,
    pub online_windows: Vec<OnlineWindow>,
    pub automatic_switch_authorized: bool,
    pub handoff: HandoffFlags,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Capabilities {
    pub xdp: XdpCapability,
    pub dpdk: DpdkCapability,
}

#[derive(Debug, Clone, Deserialize)]
pub struct XdpCapability {
    pub observed_at_utc: String,
    pub attach_mode: String,
    pub native_attach_succeeded: bool,
    pub af_xdp_bind_mode: String,
    pub forced_zerocopy_bind_succeeded: bool,
    pub copy_mode_active: bool,
    pub rx_queue_count: u32,
    pub probe_restoration_verified: bool,
    pub management_isolated: bool,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DpdkCapability {
    pub observed_at_utc: String,
    pub topology: String,
    pub pmd_probe_succeeded: bool,
    pub capacity_qualified: bool,
    pub observed_min_rx_mpps: f64,
    pub rx_queue_count: u32,
    pub rss_supported: bool,
    pub rx_queue_coverage_qualified: bool,
    pub zero_error_probe: bool,
    pub restoration_verified: bool,
    pub management_isolated: bool,
    pub standby_preflight_passed: bool,
    pub binary_sha256: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct OnlineWindow {
    pub start_utc: String,
    pub end_utc: String,
    pub capture_backend: String,
    pub packets_received: u64,
    pub packets_dropped: u64,
    pub capture_drop_rate: f64,
    pub poll_errors: u64,
    pub invalid_descriptors: u64,
    pub ring_full: u64,
    pub fill_empty: u64,
    pub host_cpu_fraction: f64,
    pub memory_fraction: f64,
    pub budget_overrun_count: u64,
    pub fallback_recovery_ms: f64,
    pub kernel_to_feature_p99_us: f64,
    pub kernel_to_feature_p999_us: f64,
    pub active_rx_queues: u32,
    pub key_flow_total: u64,
    pub key_flow_covered: u64,
    pub key_flow_coverage: Option<f64>,
    pub key_flow_coverage_basis: String,
    pub xdp_attach_mode: Option<String>,
    pub af_xdp_bind_mode: Option<String>,
    pub dpdk_pmd_active: Option<bool>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct HandoffFlags {
    pub traffic_quiesced: bool,
    pub state_snapshot_verified: bool,
    pub target_preflight_passed: bool,
    pub rollback_ready: bool,
}

impl HandoffFlags {
    fn get(&self, name: &str) -> Option<bool> {
        match name {
            "traffic_quiesced" => Some(self.traffic_quiesced),
            "state_snapshot_verified" => Some(self.state_snapshot_verified),
            "target_preflight_passed" => Some(self.target_preflight_passed),
            "rollback_ready" => Some(self.rollback_ready),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct RuntimeDecision {
    pub schema_version: u32,
    pub policy_id: String,
    pub observed_at_utc: String,
    pub decision_is_non_mutating: bool,
    pub action: String,
    pub current_backend: String,
    pub selected_backend: Option<String>,
    pub transition_permitted: bool,
    pub production_backend_available: bool,
    pub diagnostic_only_backends: Vec<String>,
    pub xdp_capability: CapabilityDecision,
    pub dpdk_capability: CapabilityDecision,
    pub online_gates: OnlineGateDecision,
    pub generic_xdp_production_eligible: bool,
    pub empty_key_flow_denominator_qualified: bool,
    pub reasons: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct CapabilityDecision {
    pub eligible: bool,
    pub reasons: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub native_verified: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub zerocopy_verified: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub attach_mode: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub af_xdp_bind_mode: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub topology: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub observed_min_rx_mpps: Option<f64>,
}

#[derive(Debug, Clone, Serialize)]
pub struct OnlineGateDecision {
    pub evaluated_windows: usize,
    pub capture_gate_qualified: bool,
    pub key_flow_gate_qualified: bool,
    pub runtime_safety_gate_qualified: bool,
    pub capture_reasons: Vec<String>,
    pub key_flow_reasons: Vec<String>,
    pub runtime_safety_reasons: Vec<String>,
    pub windows: Vec<WindowDecision>,
}

#[derive(Debug, Clone, Serialize)]
pub struct WindowDecision {
    pub capture_qualified: bool,
    pub key_flow_qualified: bool,
    pub runtime_safety_qualified: bool,
    pub capture_drop_rate: f64,
    pub key_flow_coverage: Option<f64>,
    pub capture_reasons: Vec<String>,
    pub key_flow_reasons: Vec<String>,
    pub runtime_safety_reasons: Vec<String>,
}

fn require_finite(name: &str, value: f64, minimum: f64) -> Result<(), String> {
    if !value.is_finite() || value < minimum {
        return Err(format!("{name} must be a finite number >= {minimum}"));
    }
    Ok(())
}

fn require_fraction(name: &str, value: f64) -> Result<(), String> {
    require_finite(name, value, 0.0)?;
    if value > 1.0 {
        return Err(format!("{name} must be <= 1"));
    }
    Ok(())
}

fn is_sha256(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}

fn push_unique(target: &mut Vec<String>, reason: impl Into<String>) {
    let reason = reason.into();
    if !target.contains(&reason) {
        target.push(reason);
    }
}

fn extend_unique(target: &mut Vec<String>, reasons: &[String]) {
    for reason in reasons {
        push_unique(target, reason.clone());
    }
}

fn days_from_civil(year: i64, month: i64, day: i64) -> i64 {
    let adjusted_year = year - i64::from(month <= 2);
    let era = if adjusted_year >= 0 {
        adjusted_year
    } else {
        adjusted_year - 399
    } / 400;
    let year_of_era = adjusted_year - era * 400;
    let adjusted_month = month + if month > 2 { -3 } else { 9 };
    let day_of_year = (153 * adjusted_month + 2) / 5 + day - 1;
    let day_of_era = year_of_era * 365 + year_of_era / 4 - year_of_era / 100 + day_of_year;
    era * 146_097 + day_of_era - 719_468
}

fn days_in_month(year: i64, month: i64) -> i64 {
    match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if year % 4 == 0 && (year % 100 != 0 || year % 400 == 0) => 29,
        2 => 28,
        _ => 0,
    }
}

/// Parse RFC3339 into milliseconds since Unix epoch without adding a time dependency.
pub fn parse_rfc3339_millis(value: &str) -> Result<i64, String> {
    let bytes = value.as_bytes();
    if bytes.len() < 20
        || bytes.get(4) != Some(&b'-')
        || bytes.get(7) != Some(&b'-')
        || bytes.get(10) != Some(&b'T')
        || bytes.get(13) != Some(&b':')
        || bytes.get(16) != Some(&b':')
    {
        return Err(format!("invalid RFC3339 timestamp: {value}"));
    }
    let parse = |start: usize, end: usize| -> Result<i64, String> {
        value
            .get(start..end)
            .ok_or_else(|| format!("invalid RFC3339 timestamp: {value}"))?
            .parse::<i64>()
            .map_err(|_| format!("invalid RFC3339 timestamp: {value}"))
    };
    let year = parse(0, 4)?;
    let month = parse(5, 7)?;
    let day = parse(8, 10)?;
    let hour = parse(11, 13)?;
    let minute = parse(14, 16)?;
    let second = parse(17, 19)?;
    if !(1..=12).contains(&month)
        || !(1..=days_in_month(year, month)).contains(&day)
        || hour > 23
        || minute > 59
        || second > 59
    {
        return Err(format!("invalid RFC3339 timestamp: {value}"));
    }

    let mut cursor = 19;
    let mut fractional_ms = 0i64;
    if bytes.get(cursor) == Some(&b'.') {
        cursor += 1;
        let fraction_start = cursor;
        while bytes.get(cursor).is_some_and(u8::is_ascii_digit) {
            cursor += 1;
        }
        if cursor == fraction_start {
            return Err(format!("invalid RFC3339 timestamp: {value}"));
        }
        let fraction = &value[fraction_start..cursor];
        let digits = &fraction[..fraction.len().min(3)];
        fractional_ms = digits
            .parse::<i64>()
            .map_err(|_| format!("invalid RFC3339 timestamp: {value}"))?
            * 10i64.pow((3 - digits.len()) as u32);
    }
    let offset_seconds = match bytes.get(cursor) {
        Some(b'Z') if cursor + 1 == bytes.len() => 0,
        Some(sign @ (b'+' | b'-')) if cursor + 6 == bytes.len() => {
            if bytes.get(cursor + 3) != Some(&b':') {
                return Err(format!("invalid RFC3339 timestamp: {value}"));
            }
            let offset_hour = value[cursor + 1..cursor + 3]
                .parse::<i64>()
                .map_err(|_| format!("invalid RFC3339 timestamp: {value}"))?;
            let offset_minute = value[cursor + 4..cursor + 6]
                .parse::<i64>()
                .map_err(|_| format!("invalid RFC3339 timestamp: {value}"))?;
            if offset_hour > 23 || offset_minute > 59 {
                return Err(format!("invalid RFC3339 timestamp: {value}"));
            }
            let seconds = offset_hour * 3600 + offset_minute * 60;
            if *sign == b'+' {
                seconds
            } else {
                -seconds
            }
        }
        _ => return Err(format!("invalid RFC3339 timestamp: {value}")),
    };
    let seconds = days_from_civil(year, month, day) * 86_400 + hour * 3600 + minute * 60 + second
        - offset_seconds;
    seconds
        .checked_mul(1000)
        .and_then(|value| value.checked_add(fractional_ms))
        .ok_or_else(|| format!("timestamp is out of range: {value}"))
}

fn freshness_reason(
    timestamp: &str,
    path: &str,
    reference_ms: i64,
    maximum_age_s: f64,
    future_skew_s: f64,
) -> Result<Option<String>, String> {
    let observed_ms = parse_rfc3339_millis(timestamp)?;
    let age_s = (reference_ms - observed_ms) as f64 / 1000.0;
    if age_s < -future_skew_s {
        Ok(Some(format!("{path}.future")))
    } else if age_s > maximum_age_s {
        Ok(Some(format!("{path}.stale")))
    } else {
        Ok(None)
    }
}

fn validate_policy(policy: &RuntimePolicy) -> Result<(), String> {
    if policy.schema_version != 1 {
        return Err("policy.schema_version must equal 1".into());
    }
    if policy.policy_id.is_empty() {
        return Err("policy.policy_id must be non-empty".into());
    }
    if policy.backend_priority.len() != 2
        || policy.backend_priority[0] != NATIVE_XDP_BACKEND
        || policy.backend_priority[1] != DPDK_BACKEND
    {
        return Err("policy backend priority must be native AF_XDP zero-copy then DPDK".into());
    }
    let guards = &policy.semantic_guards;
    if guards.generic_xdp_skb_is_native
        || guards.generic_xdp_skb_is_zerocopy
        || guards.generic_xdp_skb_production_eligible
        || guards.empty_key_flow_denominator_is_qualified
        || guards.same_pf_rebind_is_automatic
    {
        return Err("policy semantic guards must remain fail-closed".into());
    }
    if policy.xdp_requirements.attach_mode != "native"
        || policy.xdp_requirements.af_xdp_bind_mode != "zerocopy"
        || policy.xdp_requirements.min_rx_queues == 0
    {
        return Err("XDP requirements must require native/zerocopy and nonzero queues".into());
    }
    if policy.dpdk_requirements.min_rx_queues == 0
        || policy.online_gates.evaluation_windows == 0
        || policy.switch_safety.decision_engine_performs_mutations
    {
        return Err("policy queue/window/mutation contract is invalid".into());
    }
    for (name, value) in [
        (
            "freshness.observation_max_age_s",
            policy.freshness.observation_max_age_s,
        ),
        (
            "freshness.capability_max_age_s",
            policy.freshness.capability_max_age_s,
        ),
        (
            "freshness.max_future_clock_skew_s",
            policy.freshness.max_future_clock_skew_s,
        ),
        (
            "dpdk.capture_headroom_mpps",
            policy.dpdk_requirements.capture_headroom_mpps,
        ),
        (
            "online.max_capture_drop_rate",
            policy.online_gates.max_capture_drop_rate,
        ),
        (
            "online.max_fallback_recovery_ms",
            policy.online_gates.max_fallback_recovery_ms,
        ),
        (
            "online.p99",
            policy.online_gates.kernel_to_feature_p99_us_max,
        ),
        (
            "online.p999",
            policy.online_gates.kernel_to_feature_p999_us_max,
        ),
    ] {
        require_finite(name, value, 0.0)?;
    }
    for (name, value) in [
        (
            "online.max_host_cpu_fraction",
            policy.online_gates.max_host_cpu_fraction,
        ),
        (
            "online.max_memory_fraction",
            policy.online_gates.max_memory_fraction,
        ),
        (
            "online.min_key_flow_coverage",
            policy.online_gates.min_key_flow_coverage,
        ),
    ] {
        require_fraction(name, value)?;
    }
    if policy
        .switch_safety
        .automatic_topologies
        .iter()
        .any(|item| item == "same_pf_rebind" || item == "same_adapter_all_pf_rebind")
    {
        return Err("same-PF/all-PF rebind cannot be automatic".into());
    }
    if policy.switch_safety.required_handoff_flags.is_empty() {
        return Err("required handoff flags must not be empty".into());
    }
    for name in &policy.switch_safety.required_handoff_flags {
        if (HandoffFlags {
            traffic_quiesced: false,
            state_snapshot_verified: false,
            target_preflight_passed: false,
            rollback_ready: false,
        })
        .get(name)
        .is_none()
        {
            return Err(format!("unsupported required handoff flag: {name}"));
        }
    }
    Ok(())
}

fn evaluate_xdp(
    policy: &RuntimePolicy,
    observation: &RuntimeObservation,
    observation_ms: i64,
) -> Result<CapabilityDecision, String> {
    let capability = &observation.capabilities.xdp;
    let mut reasons = Vec::new();
    if let Some(reason) = freshness_reason(
        &capability.observed_at_utc,
        "observation.capabilities.xdp.observed_at_utc",
        observation_ms,
        policy.freshness.capability_max_age_s,
        policy.freshness.max_future_clock_skew_s,
    )? {
        reasons.push(reason);
    }
    if capability.attach_mode != policy.xdp_requirements.attach_mode {
        reasons.push("xdp.attach_mode_not_native".into());
    }
    if !capability.native_attach_succeeded {
        reasons.push("xdp.native_attach_not_verified".into());
    }
    if capability.af_xdp_bind_mode != policy.xdp_requirements.af_xdp_bind_mode {
        reasons.push("xdp.bind_mode_not_zerocopy".into());
    }
    if !capability.forced_zerocopy_bind_succeeded {
        reasons.push("xdp.forced_zerocopy_bind_not_verified".into());
    }
    if capability.copy_mode_active {
        reasons.push("xdp.copy_mode_active".into());
    }
    if capability.rx_queue_count < policy.xdp_requirements.min_rx_queues {
        reasons.push("xdp.rx_queues_insufficient".into());
    }
    if !capability.probe_restoration_verified {
        reasons.push("xdp.capability_probe_not_restored".into());
    }
    if !capability.management_isolated {
        reasons.push("xdp.interface_not_management_isolated".into());
    }
    Ok(CapabilityDecision {
        eligible: reasons.is_empty(),
        reasons,
        native_verified: Some(
            capability.attach_mode == "native" && capability.native_attach_succeeded,
        ),
        zerocopy_verified: Some(
            capability.af_xdp_bind_mode == "zerocopy"
                && capability.forced_zerocopy_bind_succeeded
                && !capability.copy_mode_active,
        ),
        attach_mode: Some(capability.attach_mode.clone()),
        af_xdp_bind_mode: Some(capability.af_xdp_bind_mode.clone()),
        topology: None,
        observed_min_rx_mpps: None,
    })
}

fn evaluate_dpdk(
    policy: &RuntimePolicy,
    observation: &RuntimeObservation,
    observation_ms: i64,
) -> Result<CapabilityDecision, String> {
    let capability = &observation.capabilities.dpdk;
    require_finite(
        "observation.capabilities.dpdk.observed_min_rx_mpps",
        capability.observed_min_rx_mpps,
        0.0,
    )?;
    let mut reasons = Vec::new();
    if let Some(reason) = freshness_reason(
        &capability.observed_at_utc,
        "observation.capabilities.dpdk.observed_at_utc",
        observation_ms,
        policy.freshness.capability_max_age_s,
        policy.freshness.max_future_clock_skew_s,
    )? {
        reasons.push(reason);
    }
    if !capability.pmd_probe_succeeded {
        reasons.push("dpdk.pmd_probe_failed".into());
    }
    if !capability.capacity_qualified {
        reasons.push("dpdk.capacity_not_qualified".into());
    }
    if capability.observed_min_rx_mpps < policy.dpdk_requirements.capture_headroom_mpps {
        reasons.push("dpdk.rx_capacity_insufficient".into());
    }
    if capability.rx_queue_count < policy.dpdk_requirements.min_rx_queues {
        reasons.push("dpdk.rx_queues_insufficient".into());
    }
    if !capability.rss_supported {
        reasons.push("dpdk.rss_not_verified".into());
    }
    if !capability.rx_queue_coverage_qualified {
        reasons.push("dpdk.rx_queue_coverage_not_verified".into());
    }
    if !capability.zero_error_probe {
        reasons.push("dpdk.error_counters_nonzero_or_unverified".into());
    }
    if !capability.restoration_verified {
        reasons.push("dpdk.restoration_not_verified".into());
    }
    if !capability.management_isolated {
        reasons.push("dpdk.interface_not_management_isolated".into());
    }
    if !capability.standby_preflight_passed {
        reasons.push("dpdk.standby_preflight_not_passed".into());
    }
    if !is_sha256(&capability.binary_sha256) {
        reasons.push("dpdk.binary_sha256_invalid".into());
    }
    Ok(CapabilityDecision {
        eligible: reasons.is_empty(),
        reasons,
        native_verified: None,
        zerocopy_verified: None,
        attach_mode: None,
        af_xdp_bind_mode: None,
        topology: Some(capability.topology.clone()),
        observed_min_rx_mpps: Some(capability.observed_min_rx_mpps),
    })
}

fn unavailable_online() -> OnlineGateDecision {
    OnlineGateDecision {
        evaluated_windows: 0,
        capture_gate_qualified: false,
        key_flow_gate_qualified: false,
        runtime_safety_gate_qualified: false,
        capture_reasons: vec!["online.windows_unavailable".into()],
        key_flow_reasons: vec!["online.windows_unavailable".into()],
        runtime_safety_reasons: vec!["online.windows_unavailable".into()],
        windows: Vec::new(),
    }
}

fn evaluate_online(
    policy: &RuntimePolicy,
    observation: &RuntimeObservation,
    observation_ms: i64,
) -> Result<OnlineGateDecision, String> {
    if observation.current_backend == NO_BACKEND {
        if !observation.online_windows.is_empty() {
            return Err("online windows must be empty when current_backend is none".into());
        }
        return Ok(unavailable_online());
    }
    let required = policy.online_gates.evaluation_windows;
    if observation.online_windows.len() < required {
        let mut result = unavailable_online();
        result.evaluated_windows = observation.online_windows.len();
        result.capture_reasons = vec!["online.windows_insufficient".into()];
        result.key_flow_reasons = vec!["online.windows_insufficient".into()];
        result.runtime_safety_reasons = vec!["online.windows_insufficient".into()];
        return Ok(result);
    }
    let selected = &observation.online_windows[observation.online_windows.len() - required..];
    let mut result = OnlineGateDecision {
        evaluated_windows: required,
        capture_gate_qualified: true,
        key_flow_gate_qualified: true,
        runtime_safety_gate_qualified: true,
        capture_reasons: Vec::new(),
        key_flow_reasons: Vec::new(),
        runtime_safety_reasons: Vec::new(),
        windows: Vec::new(),
    };
    let mut previous_end = None;
    for (index, window) in selected.iter().enumerate() {
        for (name, value) in [
            ("capture_drop_rate", window.capture_drop_rate),
            ("host_cpu_fraction", window.host_cpu_fraction),
            ("memory_fraction", window.memory_fraction),
            ("fallback_recovery_ms", window.fallback_recovery_ms),
            ("kernel_to_feature_p99_us", window.kernel_to_feature_p99_us),
            (
                "kernel_to_feature_p999_us",
                window.kernel_to_feature_p999_us,
            ),
        ] {
            require_finite(&format!("online_windows[{index}].{name}"), value, 0.0)?;
        }
        require_fraction(
            &format!("online_windows[{index}].capture_drop_rate"),
            window.capture_drop_rate,
        )?;
        require_fraction(
            &format!("online_windows[{index}].host_cpu_fraction"),
            window.host_cpu_fraction,
        )?;
        require_fraction(
            &format!("online_windows[{index}].memory_fraction"),
            window.memory_fraction,
        )?;
        if window.capture_backend != observation.current_backend {
            return Err(format!("online_windows[{index}] backend mismatch"));
        }
        let start_ms = parse_rfc3339_millis(&window.start_utc)?;
        let end_ms = parse_rfc3339_millis(&window.end_utc)?;
        if end_ms <= start_ms || end_ms > observation_ms {
            return Err(format!("online_windows[{index}] has an invalid interval"));
        }
        if previous_end.is_some_and(|previous| start_ms < previous) {
            return Err("online windows must not overlap".into());
        }
        previous_end = Some(end_ms);
        let denominator = window
            .packets_received
            .saturating_add(window.packets_dropped);
        let measured_drop = if denominator == 0 {
            0.0
        } else {
            window.packets_dropped as f64 / denominator as f64
        };
        if (measured_drop - window.capture_drop_rate).abs() > 1e-12 {
            return Err(format!(
                "online_windows[{index}] drop rate does not match counters"
            ));
        }
        if window.key_flow_covered > window.key_flow_total {
            return Err(format!(
                "online_windows[{index}] key flow covered exceeds total"
            ));
        }
        let key_coverage = if window.key_flow_total == 0 {
            if window.key_flow_coverage.is_some() {
                return Err(format!(
                    "online_windows[{index}] key coverage must be null for zero total"
                ));
            }
            None
        } else {
            let coverage = window
                .key_flow_coverage
                .ok_or_else(|| format!("online_windows[{index}] key coverage is missing"))?;
            require_fraction(
                &format!("online_windows[{index}].key_flow_coverage"),
                coverage,
            )?;
            let expected = window.key_flow_covered as f64 / window.key_flow_total as f64;
            if (coverage - expected).abs() > 1e-12 {
                return Err(format!(
                    "online_windows[{index}] key coverage does not match counters"
                ));
            }
            Some(coverage)
        };

        let mut capture = Vec::new();
        let mut key = Vec::new();
        let mut safety = Vec::new();
        if window.packets_received == 0 {
            capture.push("packets_received_zero".into());
        }
        if measured_drop > policy.online_gates.max_capture_drop_rate {
            capture.push("capture_drop_rate".into());
        }
        if window.poll_errors > policy.online_gates.max_poll_errors {
            capture.push("poll_errors".into());
        }
        if window.invalid_descriptors > policy.online_gates.max_invalid_descriptors {
            capture.push("invalid_descriptors".into());
        }
        if window.ring_full > policy.online_gates.max_ring_full {
            capture.push("ring_full".into());
        }
        if window.fill_empty > policy.online_gates.max_fill_empty {
            capture.push("fill_empty".into());
        }
        if window.kernel_to_feature_p99_us > policy.online_gates.kernel_to_feature_p99_us_max {
            capture.push("kernel_to_feature_p99_us".into());
        }
        if window.kernel_to_feature_p999_us > policy.online_gates.kernel_to_feature_p999_us_max {
            capture.push("kernel_to_feature_p999_us".into());
        }
        let required_queues = if observation.current_backend == DPDK_BACKEND {
            if window.dpdk_pmd_active != Some(true) {
                capture.push("runtime_dpdk_pmd_inactive".into());
            }
            policy.dpdk_requirements.min_rx_queues
        } else {
            let expected = if observation.current_backend == NATIVE_XDP_BACKEND {
                ("native", "zerocopy")
            } else if observation.current_backend == GENERIC_XDP_BACKEND {
                ("generic", "copy")
            } else {
                return Err("unsupported current backend".into());
            };
            if window.xdp_attach_mode.as_deref() != Some(expected.0) {
                capture.push("runtime_xdp_attach_mode".into());
            }
            if window.af_xdp_bind_mode.as_deref() != Some(expected.1) {
                capture.push("runtime_af_xdp_bind_mode".into());
            }
            policy.xdp_requirements.min_rx_queues
        };
        if window.active_rx_queues < required_queues {
            capture.push("active_rx_queues".into());
        }
        if window.host_cpu_fraction > policy.online_gates.max_host_cpu_fraction {
            safety.push("host_cpu_fraction".into());
        }
        if window.memory_fraction > policy.online_gates.max_memory_fraction {
            safety.push("memory_fraction".into());
        }
        if window.budget_overrun_count > policy.online_gates.max_budget_overrun_count {
            safety.push("budget_overrun_count".into());
        }
        if window.fallback_recovery_ms > policy.online_gates.max_fallback_recovery_ms {
            safety.push("fallback_recovery_ms".into());
        }
        if window.key_flow_coverage_basis != policy.online_gates.key_flow_coverage_basis {
            key.push("coverage_basis".into());
        }
        match key_coverage {
            None => key.push("empty_denominator".into()),
            Some(value) if value < policy.online_gates.min_key_flow_coverage => {
                key.push("coverage".into())
            }
            Some(_) => {}
        }
        for reason in &capture {
            result
                .capture_reasons
                .push(format!("window[{index}].{reason}"));
        }
        for reason in &key {
            result
                .key_flow_reasons
                .push(format!("window[{index}].{reason}"));
        }
        for reason in &safety {
            result
                .runtime_safety_reasons
                .push(format!("window[{index}].{reason}"));
        }
        result.windows.push(WindowDecision {
            capture_qualified: capture.is_empty(),
            key_flow_qualified: key.is_empty(),
            runtime_safety_qualified: safety.is_empty(),
            capture_drop_rate: measured_drop,
            key_flow_coverage: key_coverage,
            capture_reasons: capture,
            key_flow_reasons: key,
            runtime_safety_reasons: safety,
        });
    }
    result.capture_gate_qualified = result.capture_reasons.is_empty();
    result.key_flow_gate_qualified = result.key_flow_reasons.is_empty();
    result.runtime_safety_gate_qualified = result.runtime_safety_reasons.is_empty();
    Ok(result)
}

fn fallback_action(
    policy: &RuntimePolicy,
    observation: &RuntimeObservation,
    dpdk: &CapabilityDecision,
    reasons: &mut Vec<String>,
) -> (String, Option<String>, bool) {
    if !dpdk.eligible {
        extend_unique(reasons, &dpdk.reasons);
        return ("stop_fail_closed".into(), None, false);
    }
    let topology = observation.capabilities.dpdk.topology.as_str();
    if policy
        .switch_safety
        .maintenance_topologies
        .iter()
        .any(|item| item == topology)
    {
        push_unique(reasons, "dpdk.topology_requires_maintenance");
        return (
            "request_maintenance_dpdk_fallback".into(),
            Some(DPDK_BACKEND.into()),
            false,
        );
    }
    if !policy
        .switch_safety
        .automatic_topologies
        .iter()
        .any(|item| item == topology)
    {
        push_unique(reasons, "dpdk.topology_not_allowed");
        return ("stop_fail_closed".into(), None, false);
    }
    let mut ready = observation.automatic_switch_authorized;
    if !ready {
        push_unique(reasons, "dpdk.automatic_switch_not_authorized");
    }
    for name in &policy.switch_safety.required_handoff_flags {
        if observation.handoff.get(name) != Some(true) {
            ready = false;
            push_unique(reasons, format!("handoff.{name}"));
        }
    }
    if ready {
        ("switch_to_dpdk".into(), Some(DPDK_BACKEND.into()), true)
    } else {
        (
            "prepare_dpdk_fallback".into(),
            Some(DPDK_BACKEND.into()),
            false,
        )
    }
}

/// Evaluate one observation. No external state is read or changed.
pub fn evaluate_runtime_decision(
    policy: &RuntimePolicy,
    observation: &RuntimeObservation,
    now_ms: i64,
) -> Result<RuntimeDecision, String> {
    validate_policy(policy)?;
    if observation.schema_version != 1 {
        return Err("observation.schema_version must equal 1".into());
    }
    if ![
        NATIVE_XDP_BACKEND,
        GENERIC_XDP_BACKEND,
        DPDK_BACKEND,
        NO_BACKEND,
    ]
    .contains(&observation.current_backend.as_str())
    {
        return Err("unsupported current backend".into());
    }
    let observation_ms = parse_rfc3339_millis(&observation.observed_at_utc)?;
    let stale = freshness_reason(
        &observation.observed_at_utc,
        "observation.observed_at_utc",
        now_ms,
        policy.freshness.observation_max_age_s,
        policy.freshness.max_future_clock_skew_s,
    )?;
    let xdp = evaluate_xdp(policy, observation, observation_ms)?;
    let dpdk = evaluate_dpdk(policy, observation, observation_ms)?;
    let online = evaluate_online(policy, observation, observation_ms)?;
    let mut reasons = Vec::new();
    let (action, selected_backend, transition_permitted) = if let Some(reason) = stale {
        reasons.push(reason);
        if !xdp.eligible {
            extend_unique(&mut reasons, &xdp.reasons);
        }
        if !dpdk.eligible {
            extend_unique(&mut reasons, &dpdk.reasons);
        }
        ("stop_fail_closed".into(), None, false)
    } else if observation.current_backend != NO_BACKEND && !online.runtime_safety_gate_qualified {
        extend_unique(&mut reasons, &online.runtime_safety_reasons);
        push_unique(
            &mut reasons,
            "runtime_safety_failure_is_not_a_capture_backend_fallback_signal",
        );
        ("stop_fail_closed".into(), None, false)
    } else if observation.current_backend == NATIVE_XDP_BACKEND {
        if xdp.eligible && online.capture_gate_qualified && online.key_flow_gate_qualified {
            ("keep_xdp".into(), Some(NATIVE_XDP_BACKEND.into()), false)
        } else if online.capture_gate_qualified && !online.key_flow_gate_qualified {
            extend_unique(&mut reasons, &online.key_flow_reasons);
            push_unique(
                &mut reasons,
                "key_flow_failure_is_not_a_capture_backend_fallback_signal",
            );
            ("stop_fail_closed".into(), None, false)
        } else {
            extend_unique(&mut reasons, &xdp.reasons);
            extend_unique(&mut reasons, &online.capture_reasons);
            if !online.key_flow_gate_qualified {
                extend_unique(&mut reasons, &online.key_flow_reasons);
            }
            fallback_action(policy, observation, &dpdk, &mut reasons)
        }
    } else if observation.current_backend == GENERIC_XDP_BACKEND {
        reasons.push("generic_xdp_skb_is_diagnostic_copy_mode".into());
        reasons.push("generic_xdp_skb_is_not_native_or_zerocopy".into());
        extend_unique(&mut reasons, &xdp.reasons);
        if !online.key_flow_gate_qualified {
            extend_unique(&mut reasons, &online.key_flow_reasons);
        }
        fallback_action(policy, observation, &dpdk, &mut reasons)
    } else if observation.current_backend == DPDK_BACKEND {
        if dpdk.eligible && online.capture_gate_qualified && online.key_flow_gate_qualified {
            ("keep_dpdk".into(), Some(DPDK_BACKEND.into()), false)
        } else {
            extend_unique(&mut reasons, &dpdk.reasons);
            extend_unique(&mut reasons, &online.capture_reasons);
            extend_unique(&mut reasons, &online.key_flow_reasons);
            ("stop_fail_closed".into(), None, false)
        }
    } else if xdp.eligible {
        reasons.push("xdp.start_requires_external_state_snapshot_executor".into());
        (
            "prepare_xdp_primary".into(),
            Some(NATIVE_XDP_BACKEND.into()),
            false,
        )
    } else {
        extend_unique(&mut reasons, &xdp.reasons);
        fallback_action(policy, observation, &dpdk, &mut reasons)
    };
    let mut diagnostic = vec![GENERIC_XDP_BACKEND.into()];
    if !dpdk.eligible {
        diagnostic.push(DPDK_BACKEND.into());
    }
    Ok(RuntimeDecision {
        schema_version: 1,
        policy_id: policy.policy_id.clone(),
        observed_at_utc: observation.observed_at_utc.clone(),
        decision_is_non_mutating: true,
        action,
        current_backend: observation.current_backend.clone(),
        selected_backend,
        transition_permitted,
        production_backend_available: xdp.eligible || dpdk.eligible,
        diagnostic_only_backends: diagnostic,
        xdp_capability: xdp,
        dpdk_capability: dpdk,
        online_gates: online,
        generic_xdp_production_eligible: false,
        empty_key_flow_denominator_qualified: false,
        reasons,
    })
}

pub fn decision_exit_code(decision: &RuntimeDecision) -> i32 {
    if matches!(decision.action.as_str(), "keep_xdp" | "keep_dpdk") || decision.transition_permitted
    {
        0
    } else {
        10
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::Value;

    const POLICY: &str = include_str!("../../../configs/xdp_dpdk_runtime_policy_v1.json");
    const SNAPSHOT: &str =
        include_str!("../../../configs/current_bcm57810_runtime_snapshot_v1.json");
    const GOLDEN: &str =
        include_str!("../../../tests/fixtures/capture_runtime_current_golden_v1.json");

    fn inputs() -> (RuntimePolicy, RuntimeObservation) {
        (
            serde_json::from_str(POLICY).expect("parse policy fixture"),
            serde_json::from_str(SNAPSHOT).expect("parse snapshot fixture"),
        )
    }

    fn eligible_native_with_same_adapter_dpdk() -> RuntimeObservation {
        let mut value: Value = serde_json::from_str(SNAPSHOT).unwrap();
        value["current_backend"] = Value::String(NATIVE_XDP_BACKEND.into());
        value["capabilities"]["xdp"] = serde_json::json!({
            "observed_at_utc": "2026-08-12T13:05:52Z",
            "attach_mode": "native",
            "native_attach_succeeded": true,
            "af_xdp_bind_mode": "zerocopy",
            "forced_zerocopy_bind_succeeded": true,
            "copy_mode_active": false,
            "rx_queue_count": 8,
            "probe_restoration_verified": true,
            "management_isolated": true
        });
        value["capabilities"]["dpdk"] = serde_json::json!({
            "observed_at_utc": "2026-08-12T13:05:52Z",
            "topology": "same_adapter_all_pf_rebind",
            "pmd_probe_succeeded": true,
            "capacity_qualified": true,
            "observed_min_rx_mpps": 12.5,
            "rx_queue_count": 4,
            "rss_supported": true,
            "rx_queue_coverage_qualified": true,
            "zero_error_probe": true,
            "restoration_verified": true,
            "management_isolated": true,
            "standby_preflight_passed": true,
            "binary_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        });
        let window = |start: &str, end: &str| {
            serde_json::json!({
                "start_utc": start,
                "end_utc": end,
                "capture_backend": NATIVE_XDP_BACKEND,
                "packets_received": 10000000,
                "packets_dropped": 0,
                "capture_drop_rate": 0.0,
                "poll_errors": 0,
                "invalid_descriptors": 0,
                "ring_full": 0,
                "fill_empty": 0,
                "host_cpu_fraction": 0.25,
                "memory_fraction": 0.20,
                "budget_overrun_count": 0,
                "fallback_recovery_ms": 0.0,
                "kernel_to_feature_p99_us": 50.0,
                "kernel_to_feature_p999_us": 100.0,
                "active_rx_queues": 4,
                "key_flow_total": 100,
                "key_flow_covered": 100,
                "key_flow_coverage": 1.0,
                "key_flow_coverage_basis": "remote_scored_or_local_fallback_completed",
                "xdp_attach_mode": "native",
                "af_xdp_bind_mode": "zerocopy"
            })
        };
        value["online_windows"] = serde_json::json!([
            window("2026-08-12T13:04:00Z", "2026-08-12T13:04:05Z"),
            window("2026-08-12T13:04:10Z", "2026-08-12T13:04:15Z"),
            window("2026-08-12T13:04:20Z", "2026-08-12T13:04:25Z")
        ]);
        value["automatic_switch_authorized"] = Value::Bool(true);
        value["handoff"] = serde_json::json!({
            "traffic_quiesced": true,
            "state_snapshot_verified": true,
            "target_preflight_passed": true,
            "rollback_ready": true
        });
        serde_json::from_value(value).unwrap()
    }

    #[test]
    fn current_bcm57810_matches_shared_golden_and_returns_stop_exit() {
        let (policy, observation) = inputs();
        let now = parse_rfc3339_millis("2026-08-12T13:05:57Z").unwrap();
        let decision = evaluate_runtime_decision(&policy, &observation, now).unwrap();
        let golden: Value = serde_json::from_str(GOLDEN).unwrap();
        assert_eq!(decision.action, golden["action"].as_str().unwrap());
        assert_eq!(decision.selected_backend, None);
        assert_eq!(
            decision.production_backend_available,
            golden["production_backend_available"].as_bool().unwrap()
        );
        assert_eq!(
            decision.xdp_capability.eligible,
            golden["xdp_eligible"].as_bool().unwrap()
        );
        assert_eq!(
            decision.dpdk_capability.eligible,
            golden["dpdk_eligible"].as_bool().unwrap()
        );
        assert_eq!(
            decision.dpdk_capability.topology.as_deref(),
            golden["dpdk_topology"].as_str()
        );
        assert_eq!(decision_exit_code(&decision), 10);
    }

    #[test]
    fn same_adapter_all_pf_is_never_an_automatic_topology() {
        let (policy, _) = inputs();
        assert!(policy
            .switch_safety
            .maintenance_topologies
            .iter()
            .any(|item| item == "same_adapter_all_pf_rebind"));
        assert!(!policy
            .switch_safety
            .automatic_topologies
            .iter()
            .any(|item| item == "same_adapter_all_pf_rebind"));
    }

    #[test]
    fn same_adapter_capture_failure_requires_maintenance_and_exit_ten() {
        let (policy, _) = inputs();
        let mut observation = eligible_native_with_same_adapter_dpdk();
        observation.online_windows[2].poll_errors = 1;
        let now = parse_rfc3339_millis("2026-08-12T13:05:57Z").unwrap();
        let decision = evaluate_runtime_decision(&policy, &observation, now).unwrap();
        assert_eq!(decision.action, "request_maintenance_dpdk_fallback");
        assert_eq!(decision.selected_backend.as_deref(), Some(DPDK_BACKEND));
        assert!(!decision.transition_permitted);
        assert_eq!(decision_exit_code(&decision), 10);
    }

    #[test]
    fn key_flow_or_runtime_safety_failure_never_triggers_backend_switch() {
        let (policy, _) = inputs();
        let now = parse_rfc3339_millis("2026-08-12T13:05:57Z").unwrap();
        let mut key_failure = eligible_native_with_same_adapter_dpdk();
        key_failure.online_windows[2].key_flow_covered = 98;
        key_failure.online_windows[2].key_flow_coverage = Some(0.98);
        let decision = evaluate_runtime_decision(&policy, &key_failure, now).unwrap();
        assert_eq!(decision.action, "stop_fail_closed");
        assert!(decision.selected_backend.is_none());

        let mut safety_failure = eligible_native_with_same_adapter_dpdk();
        safety_failure.online_windows[2].host_cpu_fraction = 0.86;
        let decision = evaluate_runtime_decision(&policy, &safety_failure, now).unwrap();
        assert_eq!(decision.action, "stop_fail_closed");
        assert!(decision.selected_backend.is_none());
    }

    #[test]
    fn timestamps_are_timezone_normalized_and_staleness_is_enforced() {
        assert_eq!(
            parse_rfc3339_millis("2026-08-12T21:05:52+08:00").unwrap(),
            parse_rfc3339_millis("2026-08-12T13:05:52Z").unwrap()
        );
        let (policy, observation) = inputs();
        let now = parse_rfc3339_millis("2026-08-12T13:07:00Z").unwrap();
        let decision = evaluate_runtime_decision(&policy, &observation, now).unwrap();
        assert_eq!(decision.action, "stop_fail_closed");
        assert!(decision
            .reasons
            .iter()
            .any(|reason| reason == "observation.observed_at_utc.stale"));
    }
}
