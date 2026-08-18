//! Strict parser for the frozen 64-byte traffic-v2 profile.
//!
//! A frame is accepted only when every frozen profile invariant is proven;
//! every other frame is delegated to the upstream `PacketParser`.

use anyhow::Result;
use probe_agent::parser::{PacketParser, ParsedPacket};
use std::net::{IpAddr, Ipv4Addr};

pub enum ProfileParse {
    Fast(ParsedPacket),
    Fallback(Option<ParsedPacket>),
}

impl ProfileParse {
    pub fn into_packet(self) -> Option<ParsedPacket> {
        match self {
            Self::Fast(packet) => Some(packet),
            Self::Fallback(packet) => packet,
        }
    }

    pub fn is_fast(&self) -> bool {
        matches!(self, Self::Fast(_))
    }
}

/// Parse the exact deterministic traffic-v2 frame or invoke the general
/// parser. The strict checks intentionally reject VLAN, IPv4 options,
/// fragments, length disagreement, non-UDP and out-of-profile five-tuples.
#[inline]
pub fn parse_profile_or_fallback(frame: &[u8], timestamp_us: u64) -> Result<ProfileParse> {
    if let Some(packet) = parse_fixed_64b_ipv4_udp(frame, timestamp_us) {
        Ok(ProfileParse::Fast(packet))
    } else {
        PacketParser::parse(frame, timestamp_us).map(ProfileParse::Fallback)
    }
}

#[inline(always)]
fn parse_fixed_64b_ipv4_udp(frame: &[u8], timestamp_us: u64) -> Option<ParsedPacket> {
    const ETHERNET_LEN: usize = 14;
    const IPV4_LEN: usize = 20;
    const UDP_LEN: usize = 8;
    const FRAME_LEN: usize = 64;
    const IP_TOTAL_LEN: u16 = (FRAME_LEN - ETHERNET_LEN) as u16;
    const UDP_TOTAL_LEN: u16 = (FRAME_LEN - ETHERNET_LEN - IPV4_LEN) as u16;

    if frame.len() != FRAME_LEN {
        return None;
    }
    // Exact IPv4 EtherType. VLAN/QinQ EtherTypes therefore fall back.
    if frame[12] != 0x08 || frame[13] != 0x00 {
        return None;
    }
    let ip = ETHERNET_LEN;
    if frame[ip] != 0x45 {
        return None;
    }
    if u16::from_be_bytes([frame[ip + 2], frame[ip + 3]]) != IP_TOTAL_LEN {
        return None;
    }
    let flags_fragment = u16::from_be_bytes([frame[ip + 6], frame[ip + 7]]);
    if flags_fragment & 0x3fff != 0 {
        return None;
    }
    if frame[ip + 9] != 17 {
        return None;
    }

    let src = [
        frame[ip + 12],
        frame[ip + 13],
        frame[ip + 14],
        frame[ip + 15],
    ];
    let dst = [
        frame[ip + 16],
        frame[ip + 17],
        frame[ip + 18],
        frame[ip + 19],
    ];
    let queue = src[1];
    if src[0] != 10
        || queue >= 8
        || src[2] != 0
        || src[3] != 1
        || dst[0] != 11
        || dst[1] != queue
        || dst[2] != 0
        || !(1..=145).contains(&dst[3])
    {
        return None;
    }

    let udp = ip + IPV4_LEN;
    let src_port = u16::from_be_bytes([frame[udp], frame[udp + 1]]);
    let dst_port = u16::from_be_bytes([frame[udp + 2], frame[udp + 3]]);
    let udp_len = u16::from_be_bytes([frame[udp + 4], frame[udp + 5]]);
    if src_port != 10_000 + queue as u16 || dst_port != 53 || udp_len != UDP_TOTAL_LEN {
        return None;
    }
    // UDP length must agree with both the IPv4 total length and captured frame.
    if udp_len != IP_TOTAL_LEN - IPV4_LEN as u16
        || udp as u16 + udp_len != frame.len() as u16
        || udp_len < UDP_LEN as u16
    {
        return None;
    }

    Some(ParsedPacket {
        src_ip: IpAddr::V4(Ipv4Addr::from(src)),
        dst_ip: IpAddr::V4(Ipv4Addr::from(dst)),
        src_port,
        dst_port,
        protocol: 17,
        tcp_flags: 0,
        payload_len: udp_len - UDP_LEN as u16,
        total_len: frame.len() as u16,
        timestamp: timestamp_us,
        is_fragment: false,
        fragment_offset: 0,
        more_fragments: false,
        vlan_id: None,
        ttl: frame[ip + 8],
        tos: frame[ip + 1],
        fragment_id: None,
    })
}

#[cfg(test)]
mod tests {
    use super::{parse_profile_or_fallback, ProfileParse};
    use crate::flow::HftFlowTable;
    use probe_agent::parser::{PacketParser, ParsedPacket};
    use std::hint::black_box;
    use std::time::Instant;

    fn frame(queue: u8, destination: u8, tos: u8, ttl: u8) -> Vec<u8> {
        let mut value = vec![0u8; 64];
        value[12..14].copy_from_slice(&0x0800u16.to_be_bytes());
        value[14] = 0x45;
        value[15] = tos;
        value[16..18].copy_from_slice(&50u16.to_be_bytes());
        value[18..20].copy_from_slice(&0x1234u16.to_be_bytes());
        value[20..22].copy_from_slice(&0x4000u16.to_be_bytes());
        value[22] = ttl;
        value[23] = 17;
        value[26..30].copy_from_slice(&[10, queue, 0, 1]);
        value[30..34].copy_from_slice(&[11, queue, 0, destination]);
        value[34..36].copy_from_slice(&(10_000 + queue as u16).to_be_bytes());
        value[36..38].copy_from_slice(&53u16.to_be_bytes());
        value[38..40].copy_from_slice(&30u16.to_be_bytes());
        for (index, byte) in value[42..].iter_mut().enumerate() {
            *byte = (index as u8).wrapping_mul(17).wrapping_add(destination);
        }
        value
    }

    fn assert_fields_equal(actual: &ParsedPacket, expected: &ParsedPacket) {
        assert_eq!(actual.src_ip, expected.src_ip);
        assert_eq!(actual.dst_ip, expected.dst_ip);
        assert_eq!(actual.src_port, expected.src_port);
        assert_eq!(actual.dst_port, expected.dst_port);
        assert_eq!(actual.protocol, expected.protocol);
        assert_eq!(actual.tcp_flags, expected.tcp_flags);
        assert_eq!(actual.payload_len, expected.payload_len);
        assert_eq!(actual.total_len, expected.total_len);
        assert_eq!(actual.timestamp, expected.timestamp);
        assert_eq!(actual.is_fragment, expected.is_fragment);
        assert_eq!(actual.fragment_offset, expected.fragment_offset);
        assert_eq!(actual.more_fragments, expected.more_fragments);
        assert_eq!(actual.vlan_id, expected.vlan_id);
        assert_eq!(actual.ttl, expected.ttl);
        assert_eq!(actual.tos, expected.tos);
        assert_eq!(actual.fragment_id, expected.fragment_id);
    }

    #[test]
    fn fixed_profile_parser_matches_general_parser_field_by_field() {
        for queue in 0..8 {
            for destination in [1, 2, 72, 144, 145] {
                let frame = frame(queue, destination, queue * 4, 32 + queue);
                let fast =
                    parse_profile_or_fallback(&frame, 9_000_000 + destination as u64).unwrap();
                assert!(fast.is_fast());
                let fast = fast.into_packet().unwrap();
                let general = PacketParser::parse(&frame, 9_000_000 + destination as u64)
                    .unwrap()
                    .unwrap();
                assert_fields_equal(&fast, &general);
            }
        }
    }

    #[test]
    fn every_profile_invariant_violation_uses_general_fallback() {
        let base = frame(3, 145, 0x2e, 64);
        let mut cases = Vec::new();
        let mut short = base.clone();
        short.pop();
        cases.push(short);
        let mut vlan = base.clone();
        vlan[12..14].copy_from_slice(&0x8100u16.to_be_bytes());
        cases.push(vlan);
        let mut ipv6 = base.clone();
        ipv6[12..14].copy_from_slice(&0x86ddu16.to_be_bytes());
        cases.push(ipv6);
        let mut version = base.clone();
        version[14] = 0x65;
        cases.push(version);
        let mut ihl = base.clone();
        ihl[14] = 0x46;
        cases.push(ihl);
        let mut fragment = base.clone();
        fragment[20..22].copy_from_slice(&0x2000u16.to_be_bytes());
        cases.push(fragment);
        let mut ip_len = base.clone();
        ip_len[16..18].copy_from_slice(&49u16.to_be_bytes());
        cases.push(ip_len);
        let mut protocol = base.clone();
        protocol[23] = 6;
        cases.push(protocol);
        let mut udp_len = base.clone();
        udp_len[38..40].copy_from_slice(&29u16.to_be_bytes());
        cases.push(udp_len);
        let mut src = base.clone();
        src[27] = 8;
        cases.push(src);
        let mut dst = base.clone();
        dst[33] = 146;
        cases.push(dst);
        let mut src_port = base.clone();
        src_port[34..36].copy_from_slice(&9999u16.to_be_bytes());
        cases.push(src_port);
        let mut dst_port = base.clone();
        dst_port[36..38].copy_from_slice(&54u16.to_be_bytes());
        cases.push(dst_port);

        for (index, case) in cases.into_iter().enumerate() {
            let parsed = parse_profile_or_fallback(&case, 123).unwrap();
            assert!(
                !parsed.is_fast(),
                "case {index} unexpectedly used fast path"
            );
            let expected = PacketParser::parse(&case, 123).unwrap();
            match (parsed, expected) {
                (ProfileParse::Fallback(actual), expected) => {
                    assert_eq!(actual.is_some(), expected.is_some());
                    if let (Some(actual), Some(expected)) = (actual, expected) {
                        assert_fields_equal(&actual, &expected);
                    }
                }
                _ => unreachable!(),
            }
        }
    }

    #[test]
    fn fast_parse_plus_flow_matches_general_parse_plus_flow_38_features_bitwise() {
        let frames = (1..=145)
            .map(|dst| frame(2, dst, 0x2e, 61))
            .collect::<Vec<_>>();
        let mut fast_table = HftFlowTable::new(256, 120, 120, 64);
        let mut general_table = HftFlowTable::new(256, 120, 120, 64);
        let mut fast_closed = Vec::new();
        let mut general_closed = Vec::new();
        for index in 0..20_000usize {
            let frame = &frames[index % frames.len()];
            let timestamp = 1_000_000 + index as u64 * 10;
            let fast = parse_profile_or_fallback(frame, timestamp)
                .unwrap()
                .into_packet()
                .unwrap();
            let general = PacketParser::parse(frame, timestamp).unwrap().unwrap();
            fast_table.update_into(&fast, frame, &mut fast_closed);
            general_table.update_into(&general, frame, &mut general_closed);
        }
        fast_closed.extend(fast_table.flush());
        general_closed.extend(general_table.flush());
        fast_closed.sort_by(|a, b| a.flow_id.cmp(&b.flow_id));
        general_closed.sort_by(|a, b| a.flow_id.cmp(&b.flow_id));
        assert_eq!(fast_closed.len(), general_closed.len());
        for (fast, general) in fast_closed.into_iter().zip(general_closed) {
            assert_eq!(fast.flow_id, general.flow_id);
            let fast = fast.into_scheduled(true).features;
            let general = general.into_scheduled(true).features;
            assert_eq!(fast.len(), 38);
            for (index, (fast, general)) in fast.iter().zip(general).enumerate() {
                assert_eq!(fast.to_bits(), general.to_bits(), "feature {index}");
            }
        }
    }

    #[test]
    #[ignore = "release decision microbenchmark; requires >=2x or candidate stops"]
    fn microbench_complete_fixed_parse_plus_flow_requires_two_x() {
        const PACKETS: usize = 2_000_000;
        let frames = (1..=145)
            .map(|dst| frame(4, dst, 0, 64))
            .collect::<Vec<_>>();
        let mut sink = Vec::new();

        let mut general = HftFlowTable::new(256, 120, 120, 0);
        let started = Instant::now();
        for index in 0..PACKETS {
            let frame = black_box(&frames[index % frames.len()]);
            let packet = PacketParser::parse(frame, 2_000_000 + index as u64)
                .unwrap()
                .unwrap();
            general.update_into(black_box(&packet), frame, &mut sink);
        }
        let general_elapsed = started.elapsed();

        let mut fast = HftFlowTable::new(256, 120, 120, 0);
        let started = Instant::now();
        for index in 0..PACKETS {
            let frame = black_box(&frames[index % frames.len()]);
            let packet = parse_profile_or_fallback(frame, 2_000_000 + index as u64)
                .unwrap()
                .into_packet()
                .unwrap();
            fast.update_into(black_box(&packet), frame, &mut sink);
        }
        let fast_elapsed = started.elapsed();
        let speedup = general_elapsed.as_secs_f64() / fast_elapsed.as_secs_f64();
        eprintln!(
            "complete_parse_plus_flow packets={PACKETS} general_ns={} fast_ns={} speedup={speedup:.3}",
            general_elapsed.as_nanos(), fast_elapsed.as_nanos()
        );
        assert!(
            speedup >= 2.0,
            "deployment proposal requires >=2x, observed {speedup:.3}x"
        );
    }
}
