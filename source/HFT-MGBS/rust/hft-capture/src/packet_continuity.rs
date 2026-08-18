//! Kernel-pktgen payload continuity evidence for the frozen traffic profile.
//!
//! Linux pktgen writes a big-endian `pktgen_hdr` at the start of the UDP
//! payload (`magic`, `seq_num`, seconds, microseconds). The frozen generator
//! uses `clone_skb=64` and `burst=8`. pktgen advances the clone counter once
//! per `pktgen_xmit()` call while transmitting eight packets (and advancing
//! its internal sequence eight times) per call. Consequently, one serialized
//! header is observed for 64 * 8 = 512 packets and the next rebuilt header's
//! sequence advances by 512. The first and last observed groups are
//! deliberately boundary-unverified because capture can begin/end inside a
//! clone group.

use serde::Serialize;
use std::collections::BTreeMap;

const PKTGEN_MAGIC: u32 = 0xbe9be955;
const CLONE_SKB: u64 = 64;
const BURST: u64 = 8;
const OBSERVED_GROUP_PACKETS: u64 = CLONE_SKB * BURST;
const SEQUENCE_STEP: u64 = OBSERVED_GROUP_PACKETS;
const SEQUENCE_RESIDUE: u32 = 1;
const MAX_FORWARD_GROUP_SCAN: u64 = 1_000_000;
const PAYLOAD_OFFSET: usize = 14 + 20 + 8;

#[derive(Debug, Clone, Default)]
struct GroupObservation {
    count: u64,
    first_timestamp_us: u64,
    last_timestamp_us: u64,
}

#[derive(Debug, Clone)]
struct ActiveGroup {
    sequence: u32,
    observation: GroupObservation,
}

#[derive(Debug, Default)]
struct WindowAccumulator {
    completed: BTreeMap<u64, u64>,
    current: Option<(u64, u64)>,
}

impl WindowAccumulator {
    #[inline]
    fn record(&mut self, window: u64) {
        match self.current {
            None => self.current = Some((window, 1)),
            Some((current, count)) if current == window => {
                self.current = Some((current, count.saturating_add(1)))
            }
            Some((current, count)) => {
                *self.completed.entry(current).or_insert(0) += count;
                self.current = Some((window, 1));
            }
        }
    }

    fn entries(&self) -> impl Iterator<Item = (u64, u64)> + '_ {
        self.completed
            .iter()
            .map(|(window, count)| (*window, *count))
            .chain(self.current.into_iter())
    }
}

#[derive(Debug)]
pub struct PacketContinuityShard {
    input_packets: u64,
    invalid_by_window: WindowAccumulator,
    valid_by_window: WindowAccumulator,
    active_groups: [Option<ActiveGroup>; 8],
    finalized_groups: Vec<(u8, u32, GroupObservation)>,
}

impl Default for PacketContinuityShard {
    fn default() -> Self {
        Self {
            input_packets: 0,
            invalid_by_window: WindowAccumulator::default(),
            valid_by_window: WindowAccumulator::default(),
            active_groups: std::array::from_fn(|_| None),
            finalized_groups: Vec::with_capacity(131_072),
        }
    }
}

impl PacketContinuityShard {
    #[inline]
    pub fn observe(&mut self, frame: &[u8], timestamp_us: u64) {
        self.input_packets = self.input_packets.saturating_add(1);
        let Some((queue, sequence)) = extract_frozen_pktgen_header(frame) else {
            self.invalid_by_window.record(timestamp_us / 1_000_000);
            return;
        };
        self.observe_valid(queue, sequence, timestamp_us);
    }

    /// Hot-path entry after the strict fixed-profile parser already proved the
    /// Ethernet/IP/UDP tuple. Only the pktgen header remains to be validated.
    #[inline(always)]
    pub fn observe_fixed_profile(&mut self, frame: &[u8], timestamp_us: u64) {
        self.input_packets = self.input_packets.saturating_add(1);
        let header = frame.get(PAYLOAD_OFFSET..PAYLOAD_OFFSET + 8);
        let Some(header) = header else {
            self.invalid_by_window.record(timestamp_us / 1_000_000);
            return;
        };
        let magic = u32::from_be_bytes(header[..4].try_into().expect("fixed pktgen magic width"));
        let sequence =
            u32::from_be_bytes(header[4..].try_into().expect("fixed pktgen sequence width"));
        let queue = frame[27];
        if magic != PKTGEN_MAGIC
            || queue >= 8
            || sequence.wrapping_sub(SEQUENCE_RESIDUE) % SEQUENCE_STEP as u32 != 0
        {
            self.invalid_by_window.record(timestamp_us / 1_000_000);
            return;
        }
        self.observe_valid(queue, sequence, timestamp_us);
    }

    #[inline]
    pub fn observe_non_profile(&mut self, timestamp_us: u64) {
        self.input_packets = self.input_packets.saturating_add(1);
        self.invalid_by_window.record(timestamp_us / 1_000_000);
    }

    #[inline(always)]
    fn observe_valid(&mut self, queue: u8, sequence: u32, timestamp_us: u64) {
        self.valid_by_window.record(timestamp_us / 1_000_000);
        let slot = &mut self.active_groups[queue as usize];
        if let Some(active) = slot.as_mut() {
            if active.sequence == sequence {
                active.observation.count = active.observation.count.saturating_add(1);
                active.observation.last_timestamp_us =
                    active.observation.last_timestamp_us.max(timestamp_us);
                return;
            }
        }
        if let Some(previous) = slot.take() {
            self.finalized_groups
                .push((queue, previous.sequence, previous.observation));
        }
        *slot = Some(ActiveGroup {
            sequence,
            observation: GroupObservation {
                count: 1,
                first_timestamp_us: timestamp_us,
                last_timestamp_us: timestamp_us,
            },
        });
    }
}

#[derive(Debug, Clone, Default, Serialize)]
pub struct PacketContinuityWindow {
    pub epoch_second: u64,
    pub observed_valid_packets: u64,
    pub verified_groups: u64,
    pub missing_packets: u64,
    pub duplicate_packets: u64,
    pub reordered_group_packets: u64,
    pub invalid_packets: u64,
    pub unsupported_transitions: u64,
    pub boundary_unverified_groups: u64,
    pub hard_gate_eligible: bool,
}

#[derive(Debug, Clone, Default, Serialize)]
pub struct PacketContinuityReport {
    pub supported: bool,
    pub profile_id: &'static str,
    pub clone_skb: u64,
    pub burst: u64,
    pub observed_group_packets: u64,
    pub sequence_step: u64,
    pub packet_continuity_windows: Vec<PacketContinuityWindow>,
    pub packet_gap: u64,
    pub duplicate_packets: u64,
    pub reordered_group_packets: u64,
    pub invalid_packets: u64,
    pub unsupported_transitions: u64,
    pub boundary_unverified_groups: u64,
    pub input_packets: u64,
    pub valid_pktgen_packets: u64,
    pub merged_group_packets: u64,
    pub queue_valid_packets: BTreeMap<u8, u64>,
    pub queue_distinct_groups: BTreeMap<u8, u64>,
    pub queue_owner_conflicts: u64,
    pub input_conservation_ok: bool,
    pub ownership_merge_conservation_ok: bool,
}

#[inline(always)]
fn extract_frozen_pktgen_header(frame: &[u8]) -> Option<(u8, u32)> {
    if frame.len() != 64
        || frame.get(12..14)? != [0x08, 0x00]
        || frame[14] != 0x45
        || frame[23] != 17
        || frame[26] != 10
        || frame[27] >= 8
        || frame[28] != 0
        || frame[29] != 1
        || frame[30] != 11
        || frame[31] != frame[27]
        || frame[32] != 0
        || !(1..=145).contains(&frame[33])
        || u16::from_be_bytes([frame[34], frame[35]]) != 10_000 + u16::from(frame[27])
        || u16::from_be_bytes([frame[36], frame[37]]) != 53
        || u32::from_be_bytes(frame[PAYLOAD_OFFSET..PAYLOAD_OFFSET + 4].try_into().ok()?)
            != PKTGEN_MAGIC
    {
        return None;
    }
    let sequence = u32::from_be_bytes(
        frame[PAYLOAD_OFFSET + 4..PAYLOAD_OFFSET + 8]
            .try_into()
            .ok()?,
    );
    // pktgen_clear_counters starts at one. With clone_skb=64 and burst=8,
    // rebuilt headers retain residue one modulo the 512-packet sequence step.
    if sequence.wrapping_sub(SEQUENCE_RESIDUE) % SEQUENCE_STEP as u32 != 0 {
        return None;
    }
    Some((frame[27], sequence))
}

pub fn merge_packet_continuity<'a>(
    shards: impl IntoIterator<Item = &'a PacketContinuityShard>,
) -> PacketContinuityReport {
    let mut input_packets = 0u64;
    let mut invalid_by_window = BTreeMap::<u64, u64>::new();
    let mut valid_by_window = BTreeMap::<u64, u64>::new();
    let mut groups = BTreeMap::<(u8, u32), GroupObservation>::new();
    let mut queue_owners = [None::<usize>; 8];
    let mut queue_owner_conflicts = 0u64;
    for (shard_index, shard) in shards.into_iter().enumerate() {
        input_packets = input_packets.saturating_add(shard.input_packets);
        for (window, count) in shard.invalid_by_window.entries() {
            *invalid_by_window.entry(window).or_insert(0) += count;
        }
        for (window, count) in shard.valid_by_window.entries() {
            *valid_by_window.entry(window).or_insert(0) += count;
        }
        for (queue, sequence, observed) in &shard.finalized_groups {
            match queue_owners[*queue as usize] {
                None => queue_owners[*queue as usize] = Some(shard_index),
                Some(owner) if owner != shard_index => {
                    queue_owner_conflicts = queue_owner_conflicts.saturating_add(1)
                }
                Some(_) => {}
            }
            let merged = groups.entry((*queue, *sequence)).or_default();
            merged.count = merged.count.saturating_add(observed.count);
            if merged.first_timestamp_us == 0
                || observed.first_timestamp_us < merged.first_timestamp_us
            {
                merged.first_timestamp_us = observed.first_timestamp_us;
            }
            merged.last_timestamp_us = merged.last_timestamp_us.max(observed.last_timestamp_us);
        }
        for (queue, active) in shard.active_groups.iter().enumerate() {
            let Some(active) = active else { continue };
            match queue_owners[queue] {
                None => queue_owners[queue] = Some(shard_index),
                Some(owner) if owner != shard_index => {
                    queue_owner_conflicts = queue_owner_conflicts.saturating_add(1)
                }
                Some(_) => {}
            }
            let merged = groups.entry((queue as u8, active.sequence)).or_default();
            merged.count = merged.count.saturating_add(active.observation.count);
            if merged.first_timestamp_us == 0
                || active.observation.first_timestamp_us < merged.first_timestamp_us
            {
                merged.first_timestamp_us = active.observation.first_timestamp_us;
            }
            merged.last_timestamp_us = merged
                .last_timestamp_us
                .max(active.observation.last_timestamp_us);
        }
    }

    let mut windows = BTreeMap::<u64, PacketContinuityWindow>::new();
    for (window, invalid) in invalid_by_window {
        let item = windows.entry(window).or_default();
        item.epoch_second = window;
        item.invalid_packets = item.invalid_packets.saturating_add(invalid);
    }
    for (window, valid) in valid_by_window {
        let item = windows.entry(window).or_default();
        item.epoch_second = window;
        item.observed_valid_packets = item.observed_valid_packets.saturating_add(valid);
    }
    let valid_pktgen_packets = groups.values().map(|group| group.count).sum::<u64>();
    let mut queue_valid_packets = BTreeMap::new();
    let mut queue_distinct_groups = BTreeMap::new();
    for ((queue, _), group) in &groups {
        *queue_valid_packets.entry(*queue).or_insert(0u64) += group.count;
        *queue_distinct_groups.entry(*queue).or_insert(0u64) += 1;
    }

    for queue in 0u8..8 {
        let mut ordered = groups
            .iter()
            .filter_map(|((owner, sequence), group)| {
                (*owner == queue).then_some((*sequence, group))
            })
            .collect::<Vec<_>>();
        ordered.sort_by_key(|(_, group)| group.first_timestamp_us);
        if let Some((_, first)) = ordered.first() {
            let window = first.last_timestamp_us / 1_000_000;
            let item = windows.entry(window).or_default();
            item.epoch_second = window;
            item.boundary_unverified_groups = item.boundary_unverified_groups.saturating_add(1);
        }
        if ordered.len() > 1 {
            if let Some((_, last)) = ordered.last() {
                let window = last.last_timestamp_us / 1_000_000;
                let item = windows.entry(window).or_default();
                item.epoch_second = window;
                item.boundary_unverified_groups = item.boundary_unverified_groups.saturating_add(1);
            }
        }
        // Only interior groups are hard-verifiable: capture may cut both edges.
        for index in 1..ordered.len().saturating_sub(1) {
            let (sequence, group) = ordered[index];
            let (next_sequence, _) = ordered[index + 1];
            let window = group.last_timestamp_us / 1_000_000;
            let item = windows.entry(window).or_default();
            item.epoch_second = window;
            let delta = next_sequence.wrapping_sub(sequence);
            if delta == 0 || delta % SEQUENCE_STEP as u32 != 0 || delta > u32::MAX / 2 {
                item.reordered_group_packets =
                    item.reordered_group_packets.saturating_add(group.count);
                continue;
            }
            let forward_groups = u64::from(delta / SEQUENCE_STEP as u32);
            if forward_groups > MAX_FORWARD_GROUP_SCAN {
                item.unsupported_transitions = item.unsupported_transitions.saturating_add(1);
                continue;
            }
            item.verified_groups = item.verified_groups.saturating_add(1);
            item.missing_packets = item
                .missing_packets
                .saturating_add(OBSERVED_GROUP_PACKETS.saturating_sub(group.count));
            item.duplicate_packets = item
                .duplicate_packets
                .saturating_add(group.count.saturating_sub(OBSERVED_GROUP_PACKETS));
            let skipped_groups = forward_groups.saturating_sub(1);
            let absent_groups = (1..=skipped_groups)
                .filter(|step| {
                    let expected =
                        sequence.wrapping_add((*step as u32).wrapping_mul(SEQUENCE_STEP as u32));
                    !groups.contains_key(&(queue, expected))
                })
                .count() as u64;
            item.missing_packets = item
                .missing_packets
                .saturating_add(absent_groups.saturating_mul(OBSERVED_GROUP_PACKETS));
        }
    }
    for window in windows.values_mut() {
        window.hard_gate_eligible = window.verified_groups > 0
            && window.boundary_unverified_groups == 0
            && window.invalid_packets == 0;
    }
    let packet_continuity_windows = windows.into_values().collect::<Vec<_>>();
    let invalid_packets = packet_continuity_windows
        .iter()
        .map(|window| window.invalid_packets)
        .sum::<u64>();
    let merged_group_packets = groups.values().map(|group| group.count).sum::<u64>();
    let unsupported_transitions = packet_continuity_windows
        .iter()
        .map(|window| window.unsupported_transitions)
        .sum();
    PacketContinuityReport {
        supported: valid_pktgen_packets > 0
            && queue_valid_packets.len() == 8
            && invalid_packets == 0
            && queue_owner_conflicts == 0
            && unsupported_transitions == 0,
        profile_id: "linux_pktgen_ipv4_udp_be_header_clone64_burst8_group512_v2",
        clone_skb: CLONE_SKB,
        burst: BURST,
        observed_group_packets: OBSERVED_GROUP_PACKETS,
        sequence_step: SEQUENCE_STEP,
        packet_gap: packet_continuity_windows
            .iter()
            .map(|window| window.missing_packets)
            .sum(),
        duplicate_packets: packet_continuity_windows
            .iter()
            .map(|window| window.duplicate_packets)
            .sum(),
        reordered_group_packets: packet_continuity_windows
            .iter()
            .map(|window| window.reordered_group_packets)
            .sum(),
        invalid_packets,
        unsupported_transitions,
        boundary_unverified_groups: packet_continuity_windows
            .iter()
            .map(|window| window.boundary_unverified_groups)
            .sum(),
        input_packets,
        valid_pktgen_packets,
        merged_group_packets,
        queue_valid_packets,
        queue_distinct_groups,
        queue_owner_conflicts,
        input_conservation_ok: input_packets
            == valid_pktgen_packets.saturating_add(invalid_packets),
        ownership_merge_conservation_ok: merged_group_packets == valid_pktgen_packets
            && queue_owner_conflicts == 0,
        packet_continuity_windows,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn frame(queue: u8, sequence: u32) -> Vec<u8> {
        let mut value = vec![0u8; 64];
        value[12..14].copy_from_slice(&0x0800u16.to_be_bytes());
        value[14] = 0x45;
        value[23] = 17;
        value[26..30].copy_from_slice(&[10, queue, 0, 1]);
        value[30..34].copy_from_slice(&[11, queue, 0, 1]);
        value[34..36].copy_from_slice(&(10_000 + u16::from(queue)).to_be_bytes());
        value[36..38].copy_from_slice(&53u16.to_be_bytes());
        value[PAYLOAD_OFFSET..PAYLOAD_OFFSET + 4].copy_from_slice(&PKTGEN_MAGIC.to_be_bytes());
        value[PAYLOAD_OFFSET + 4..PAYLOAD_OFFSET + 8].copy_from_slice(&sequence.to_be_bytes());
        value
    }

    fn observe_group(shard: &mut PacketContinuityShard, queue: u8, seq: u32, count: u64, ts: u64) {
        for offset in 0..count {
            shard.observe(&frame(queue, seq), ts + offset);
        }
    }

    #[test]
    fn clone64_burst8_groups_count_missing_duplicate_and_skip_without_edge_false_positive() {
        let mut shard = PacketContinuityShard::default();
        observe_group(&mut shard, 0, 1, 7, 1_000_000); // first boundary
        observe_group(&mut shard, 0, 513, 508, 2_000_000); // four missing
        observe_group(&mut shard, 0, 1025, 514, 3_000_000); // two duplicate
        observe_group(&mut shard, 0, 2049, 512, 4_000_000); // skipped 1537
        observe_group(&mut shard, 0, 2561, 3, 5_000_000); // last boundary
        let report = merge_packet_continuity([&shard]);
        assert_eq!(report.clone_skb, 64);
        assert_eq!(report.burst, 8);
        assert_eq!(report.observed_group_packets, 512);
        assert_eq!(report.sequence_step, 512);
        assert_eq!(report.packet_gap, 4 + 512);
        assert_eq!(report.duplicate_packets, 2);
        assert_eq!(report.boundary_unverified_groups, 2);
        assert!(report.input_conservation_ok);
        assert!(report.ownership_merge_conservation_ok);
    }

    #[test]
    fn serialized_report_binds_clone_burst_group_and_sequence_step() {
        let mut shard = PacketContinuityShard::default();
        observe_group(&mut shard, 0, 1, 1, 1_000_000);
        let raw = serde_json::to_value(merge_packet_continuity([&shard])).unwrap();
        assert_eq!(raw["clone_skb"], 64);
        assert_eq!(raw["burst"], 8);
        assert_eq!(raw["observed_group_packets"], 512);
        assert_eq!(raw["sequence_step"], 512);
        assert_eq!(
            raw["profile_id"],
            "linux_pktgen_ipv4_udp_be_header_clone64_burst8_group512_v2"
        );
    }

    #[test]
    fn wrap_and_cross_worker_ownership_merge_are_conserved() {
        let mut left = PacketContinuityShard::default();
        let mut right = PacketContinuityShard::default();
        observe_group(&mut left, 3, u32::MAX - 510, 512, 1_000_000);
        observe_group(&mut left, 3, 1, 512, 2_000_000);
        observe_group(&mut left, 3, 513, 512, 3_000_000);
        observe_group(&mut right, 4, 1, 512, 1_000_000);
        observe_group(&mut right, 4, 513, 512, 2_000_000);
        observe_group(&mut right, 4, 1025, 512, 3_000_000);
        let report = merge_packet_continuity([&left, &right]);
        assert_eq!(report.packet_gap, 0);
        assert_eq!(report.input_packets, 3072);
        assert_eq!(report.merged_group_packets, 3072);
        assert_eq!(report.queue_owner_conflicts, 0);
        assert!(report.ownership_merge_conservation_ok);
    }

    #[test]
    fn invalid_magic_and_non_group_or_legacy_clone64_sequence_fail_closed() {
        let mut shard = PacketContinuityShard::default();
        let mut bad_magic = frame(0, 1);
        bad_magic[PAYLOAD_OFFSET] ^= 1;
        shard.observe(&bad_magic, 1_000_000);
        shard.observe(&frame(0, 2), 1_000_001);
        // Residue one modulo 64 is insufficient: the frozen burst=8 profile
        // requires residue one modulo the complete 512-packet step.
        shard.observe(&frame(0, 65), 1_000_002);
        let report = merge_packet_continuity([&shard]);
        assert_eq!(report.invalid_packets, 3);
        assert_eq!(report.valid_pktgen_packets, 0);
        assert!(report.input_conservation_ok);
        assert!(!report.supported);
    }

    #[test]
    fn fixed_profile_hot_path_matches_full_header_extraction() {
        let packet = frame(6, 513);
        let mut full = PacketContinuityShard::default();
        let mut fast = PacketContinuityShard::default();
        for offset in 0..512 {
            full.observe(&packet, 2_000_000 + offset);
            fast.observe_fixed_profile(&packet, 2_000_000 + offset);
        }
        let full = merge_packet_continuity([&full]);
        let fast = merge_packet_continuity([&fast]);
        assert_eq!(full.input_packets, fast.input_packets);
        assert_eq!(full.valid_pktgen_packets, fast.valid_pktgen_packets);
        assert_eq!(full.invalid_packets, fast.invalid_packets);
        assert_eq!(full.queue_valid_packets, fast.queue_valid_packets);
        assert_eq!(full.queue_distinct_groups, fast.queue_distinct_groups);
    }

    #[test]
    fn same_queue_on_two_workers_is_an_ownership_conflict_but_merge_stays_conserved() {
        let mut left = PacketContinuityShard::default();
        let mut right = PacketContinuityShard::default();
        observe_group(&mut left, 2, 1, 512, 1_000_000);
        observe_group(&mut right, 2, 513, 512, 2_000_000);
        let report = merge_packet_continuity([&left, &right]);
        assert!(report.queue_owner_conflicts > 0);
        assert!(report.input_conservation_ok);
        assert!(!report.ownership_merge_conservation_ok);
        assert!(!report.supported);
    }

    #[test]
    fn queue_owner_is_unique_and_reordered_group_is_not_reported_as_gap() {
        let mut shard = PacketContinuityShard::default();
        for queue in [0, 1] {
            observe_group(&mut shard, queue, 1, 512, 1_000_000);
            observe_group(&mut shard, queue, 1025, 512, 2_000_000);
            observe_group(&mut shard, queue, 513, 512, 3_000_000);
            observe_group(&mut shard, queue, 1537, 512, 4_000_000);
        }
        let report = merge_packet_continuity([&shard]);
        assert_eq!(report.queue_owner_conflicts, 0);
        assert_eq!(report.queue_valid_packets.get(&0), Some(&2048));
        assert_eq!(report.queue_valid_packets.get(&1), Some(&2048));
        assert_eq!(report.reordered_group_packets, 1024);
        assert_eq!(report.packet_gap, 0);
        assert!(report.input_conservation_ok);
    }
}
