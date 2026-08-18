//! Unwired, fail-closed A09 local-fallback inference foundation.
//!
//! The production dispatcher does not use this module yet.  It loads a compact
//! parameter artifact only when the artifact and every frozen source identity
//! match caller-supplied SHA-256 roots.  Prediction follows the existing
//! `numpy_exact_v1` arithmetic order: f32 split inputs, f64 thresholds, ordered
//! tree accumulation, then ordered three-member accumulation.

use anyhow::{bail, ensure, Context, Result};
use serde::Deserialize;
use std::collections::HashSet;
use std::path::{Component, Path};

pub const BACKEND_IDENTITY: &str = "local_cpu_rust_a09_portable_exact_v1";
pub const PORTABLE_SCHEMA_VERSION: u32 = 1;
pub const RAW_FEATURE_COUNT: usize = 38;
pub const PROJECTED_FEATURE_COUNT: usize = 34;
const MAGIC: &[u8; 8] = b"HFTA09P1";
const MEMBER_COUNT: usize = 3;
const TREES_PER_MEMBER: usize = 200;
const MAX_TOTAL_NODES: usize = 1_000_000;

pub const PROJECTED_FEATURE_NAMES: [&str; PROJECTED_FEATURE_COUNT] = [
    "byte_direction_imbalance",
    "deep_tier_available",
    "directional_iat_std_s_max_log1p",
    "directional_iat_std_s_min_log1p",
    "directional_mean_iat_s_max_log1p",
    "directional_mean_iat_s_min_log1p",
    "flow_ack_flag_count_log1p",
    "flow_bytes_log1p",
    "flow_cwr_flag_count_log1p",
    "flow_duration_s_log1p",
    "flow_ece_flag_count_log1p",
    "flow_fin_flag_count_log1p",
    "flow_iat_std_s_log1p",
    "flow_length_std_log1p",
    "flow_max_length_log1p",
    "flow_mean_iat_s_log1p",
    "flow_mean_length_log1p",
    "flow_min_length_log1p",
    "flow_packets_log1p",
    "flow_payload_bytes_log1p",
    "flow_psh_flag_count_log1p",
    "flow_rst_flag_count_log1p",
    "flow_syn_flag_count_log1p",
    "flow_tcp_flags_or",
    "flow_urg_flag_count_log1p",
    "packet_direction_imbalance",
    "payload_byte_ratio",
    "payload_direction_imbalance",
    "payload_entropy",
    "payload_printable_ratio",
    "payload_zero_ratio",
    "protocol",
    "protocol_tcp",
    "protocol_udp",
];

#[derive(Debug, Clone)]
pub struct ExpectedPortableA09Identity {
    pub artifact_sha256: String,
    pub source_model_sha256: String,
    pub numpy_engine_sha256: String,
    pub campaign_contract_sha256: String,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct LocalPrediction {
    pub probability: f64,
    pub label: u8,
    pub node_visits: u32,
}

#[derive(Debug, Clone)]
struct Node {
    left: i32,
    right: i32,
    feature: i32,
    threshold: f64,
    positive_probability: f64,
}

#[derive(Debug, Clone)]
struct Tree {
    nodes: Vec<Node>,
}

#[derive(Debug, Clone)]
struct Member {
    trees: Vec<Tree>,
}

#[derive(Debug, Clone)]
pub struct PortableA09 {
    source_model_sha256: String,
    numpy_engine_sha256: String,
    campaign_contract_sha256: String,
    effective_threshold: f64,
    members: Vec<Member>,
}

#[derive(Debug)]
pub struct VerifiedLocalFallback {
    model: PortableA09,
    artifact_sha256: String,
    quality_receipt_sha256: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct LocalFallbackQualityReceipt {
    schema_version: u32,
    scope: String,
    candidate_id: String,
    portable_artifact_sha256: String,
    source_model_sha256: String,
    numpy_engine_sha256: String,
    campaign_contract_sha256: String,
    holdout_input_sha256: String,
    equivalence_evidence_sha256: String,
    physical_benchmark_evidence_sha256: String,
    rust_fallback_source_sha256: String,
    capture_binary_sha256: String,
    evidence_manifest_sha256: String,
    cross_language_sample_count: u64,
    probability_bit_exact_count: u64,
    decision_exact_count: u64,
    physical_benchmark_runs: u64,
    physical_flows_per_second_min: f64,
    physical_p99_us_max: f64,
    accepted: bool,
    production_release_accepted: bool,
    final_pareto_ingestion_allowed: bool,
    errors: Vec<String>,
}

impl VerifiedLocalFallback {
    pub fn load(
        artifact_path: &Path,
        quality_receipt_path: &Path,
        expected_quality_receipt_sha256: &str,
        expected: &ExpectedPortableA09Identity,
    ) -> Result<Self> {
        validate_hex_sha("expected quality receipt", expected_quality_receipt_sha256)?;
        let artifact = read_stable_regular(artifact_path, 64 * 1024 * 1024)?;
        let receipt_raw = read_stable_regular(quality_receipt_path, 1024 * 1024)?;
        let receipt_sha = sha256_hex(&receipt_raw);
        ensure!(
            constant_time_eq(
                receipt_sha.as_bytes(),
                expected_quality_receipt_sha256.as_bytes()
            ),
            "local fallback quality receipt SHA-256 mismatch"
        );
        let receipt: LocalFallbackQualityReceipt =
            serde_json::from_slice(&receipt_raw).context("parse local fallback quality receipt")?;
        ensure!(
            receipt.schema_version == 1
                && receipt.scope == "hft_mgbs_local_a09_fallback_quality_receipt_v1"
                && receipt.candidate_id == "A09"
                && receipt.accepted
                && !receipt.production_release_accepted
                && !receipt.final_pareto_ingestion_allowed
                && receipt.errors.is_empty(),
            "local fallback quality receipt is not an accepted non-release receipt"
        );
        for (label, value) in [
            (
                "portable artifact",
                receipt.portable_artifact_sha256.as_str(),
            ),
            ("source model", receipt.source_model_sha256.as_str()),
            ("NumPy engine", receipt.numpy_engine_sha256.as_str()),
            (
                "campaign contract",
                receipt.campaign_contract_sha256.as_str(),
            ),
            ("holdout input", receipt.holdout_input_sha256.as_str()),
            (
                "equivalence evidence",
                receipt.equivalence_evidence_sha256.as_str(),
            ),
            (
                "physical benchmark",
                receipt.physical_benchmark_evidence_sha256.as_str(),
            ),
            (
                "Rust fallback source",
                receipt.rust_fallback_source_sha256.as_str(),
            ),
            ("capture binary", receipt.capture_binary_sha256.as_str()),
            (
                "evidence manifest",
                receipt.evidence_manifest_sha256.as_str(),
            ),
        ] {
            validate_hex_sha(label, value)?;
        }
        ensure!(
            receipt.portable_artifact_sha256 == expected.artifact_sha256
                && receipt.source_model_sha256 == expected.source_model_sha256
                && receipt.numpy_engine_sha256 == expected.numpy_engine_sha256
                && receipt.campaign_contract_sha256 == expected.campaign_contract_sha256,
            "local fallback quality receipt identity differs from the portable artifact contract"
        );
        ensure!(
            receipt.cross_language_sample_count > 0
                && receipt.probability_bit_exact_count == receipt.cross_language_sample_count
                && receipt.decision_exact_count == receipt.cross_language_sample_count,
            "local fallback cross-language equivalence is incomplete"
        );
        ensure!(
            receipt.physical_benchmark_runs >= 3
                && receipt.physical_flows_per_second_min.is_finite()
                && receipt.physical_flows_per_second_min > 0.0
                && receipt.physical_p99_us_max.is_finite()
                && receipt.physical_p99_us_max >= 0.0
                && receipt.physical_p99_us_max <= 10_000.0,
            "local fallback physical benchmark is incomplete or outside the P99 gate"
        );
        let model = PortableA09::from_bytes(&artifact, expected)?;
        Ok(Self {
            model,
            artifact_sha256: expected.artifact_sha256.clone(),
            quality_receipt_sha256: receipt_sha,
        })
    }

    pub fn predict_raw(&self, raw: &[f64]) -> Result<LocalPrediction> {
        self.model.predict_raw(raw)
    }

    pub fn backend_identity(&self) -> String {
        format!(
            "{};artifact_sha256={};quality_receipt_sha256={}",
            BACKEND_IDENTITY, self.artifact_sha256, self.quality_receipt_sha256
        )
    }

    pub fn quality_receipt_sha256(&self) -> &str {
        &self.quality_receipt_sha256
    }
}

fn read_stable_regular(path: &Path, maximum: u64) -> Result<Vec<u8>> {
    ensure!(
        path.is_absolute(),
        "local fallback artifact paths must be absolute"
    );
    ensure!(
        !path
            .components()
            .any(|component| matches!(component, Component::CurDir | Component::ParentDir)),
        "local fallback artifact path contains traversal components"
    );
    let mut current = std::path::PathBuf::new();
    for component in path.components() {
        current.push(component.as_os_str());
        let metadata = std::fs::symlink_metadata(&current)
            .with_context(|| format!("inspect local fallback path {}", current.display()))?;
        ensure!(
            !metadata.file_type().is_symlink(),
            "local fallback path contains a symlink"
        );
    }
    let before = std::fs::metadata(path)?;
    ensure!(
        before.is_file() && before.len() <= maximum,
        "bounded regular fallback artifact required"
    );
    let raw = std::fs::read(path)?;
    let after = std::fs::metadata(path)?;
    ensure!(
        before.len() == after.len()
            && before.modified().ok() == after.modified().ok()
            && raw.len() as u64 == before.len(),
        "local fallback artifact changed while being read"
    );
    Ok(raw)
}

impl PortableA09 {
    pub fn from_bytes(bytes: &[u8], expected: &ExpectedPortableA09Identity) -> Result<Self> {
        validate_hex_sha("expected artifact", &expected.artifact_sha256)?;
        validate_hex_sha("expected source model", &expected.source_model_sha256)?;
        validate_hex_sha("expected NumPy engine", &expected.numpy_engine_sha256)?;
        validate_hex_sha(
            "expected campaign contract",
            &expected.campaign_contract_sha256,
        )?;
        let actual_artifact_sha = sha256_hex(bytes);
        ensure!(
            constant_time_eq(
                actual_artifact_sha.as_bytes(),
                expected.artifact_sha256.as_bytes()
            ),
            "portable A09 artifact SHA-256 mismatch"
        );

        let mut reader = Reader::new(bytes);
        ensure!(
            reader.take(MAGIC.len())? == MAGIC,
            "portable A09 magic mismatch"
        );
        ensure!(
            reader.u32()? == PORTABLE_SCHEMA_VERSION,
            "unsupported portable A09 schema"
        );
        ensure!(
            reader.u32()? as usize == PROJECTED_FEATURE_COUNT,
            "portable A09 projected feature count mismatch"
        );
        ensure!(
            reader.u32()? as usize == RAW_FEATURE_COUNT,
            "portable A09 raw feature count mismatch"
        );
        ensure!(
            reader.u32()? as usize == MEMBER_COUNT,
            "portable A09 must contain exactly three members"
        );
        let source_model_sha256 = reader.sha256_hex()?;
        let numpy_engine_sha256 = reader.sha256_hex()?;
        let campaign_contract_sha256 = reader.sha256_hex()?;
        ensure!(
            constant_time_eq(
                source_model_sha256.as_bytes(),
                expected.source_model_sha256.as_bytes()
            ),
            "portable A09 source-model identity mismatch"
        );
        ensure!(
            constant_time_eq(
                numpy_engine_sha256.as_bytes(),
                expected.numpy_engine_sha256.as_bytes()
            ),
            "portable A09 NumPy-engine identity mismatch"
        );
        ensure!(
            constant_time_eq(
                campaign_contract_sha256.as_bytes(),
                expected.campaign_contract_sha256.as_bytes()
            ),
            "portable A09 campaign-contract identity mismatch"
        );
        let effective_threshold = f64::from_bits(reader.u64()?);
        ensure!(
            effective_threshold.is_finite() && (0.0..=1.0).contains(&effective_threshold),
            "portable A09 effective threshold is invalid"
        );

        let feature_name_count = reader.u32()? as usize;
        ensure!(
            feature_name_count == PROJECTED_FEATURE_COUNT,
            "portable A09 feature-name count mismatch"
        );
        for expected_name in PROJECTED_FEATURE_NAMES {
            let length = reader.u16()? as usize;
            ensure!(
                length > 0 && length <= 128,
                "portable A09 feature name is invalid"
            );
            let name = std::str::from_utf8(reader.take(length)?)
                .context("portable A09 feature name is not UTF-8")?;
            ensure!(name == expected_name, "portable A09 feature order mismatch");
        }

        let mut members = Vec::with_capacity(MEMBER_COUNT);
        let mut total_nodes = 0usize;
        for _ in 0..MEMBER_COUNT {
            let member_threshold = f64::from_bits(reader.u64()?);
            ensure!(
                member_threshold.is_finite() && (0.0..=1.0).contains(&member_threshold),
                "portable A09 member threshold is invalid"
            );
            ensure!(
                reader.u32()? == 1,
                "portable A09 positive class must be label 1"
            );
            let tree_count = reader.u32()? as usize;
            ensure!(
                tree_count == TREES_PER_MEMBER,
                "portable A09 member must contain exactly 200 trees"
            );
            let mut trees = Vec::with_capacity(tree_count);
            for _ in 0..tree_count {
                let node_count = reader.u32()? as usize;
                ensure!(node_count > 0, "portable A09 contains an empty tree");
                total_nodes = total_nodes
                    .checked_add(node_count)
                    .context("portable A09 node count overflow")?;
                ensure!(
                    total_nodes <= MAX_TOTAL_NODES,
                    "portable A09 is unreasonably large"
                );
                let mut nodes = Vec::with_capacity(node_count);
                for _ in 0..node_count {
                    nodes.push(Node {
                        left: reader.i32()?,
                        right: reader.i32()?,
                        feature: reader.i32()?,
                        threshold: f64::from_bits(reader.u64()?),
                        positive_probability: f64::from_bits(reader.u64()?),
                    });
                }
                validate_tree(&nodes)?;
                trees.push(Tree { nodes });
            }
            members.push(Member { trees });
        }
        ensure!(
            reader.remaining() == 0,
            "portable A09 artifact has trailing bytes"
        );
        Ok(Self {
            source_model_sha256,
            numpy_engine_sha256,
            campaign_contract_sha256,
            effective_threshold,
            members,
        })
    }

    pub fn source_model_sha256(&self) -> &str {
        &self.source_model_sha256
    }

    pub fn numpy_engine_sha256(&self) -> &str {
        &self.numpy_engine_sha256
    }

    pub fn campaign_contract_sha256(&self) -> &str {
        &self.campaign_contract_sha256
    }

    pub fn effective_threshold(&self) -> f64 {
        self.effective_threshold
    }

    pub fn predict_raw(&self, raw: &[f64]) -> Result<LocalPrediction> {
        let projected = project_raw_features(raw)?;
        self.predict_projected(&projected)
    }

    pub fn predict_projected(&self, projected: &[f32]) -> Result<LocalPrediction> {
        ensure!(
            projected.len() == PROJECTED_FEATURE_COUNT,
            "A09 projected feature count mismatch"
        );
        ensure!(
            projected.iter().all(|value| value.is_finite()),
            "A09 projected features contain non-finite values"
        );
        let mut ensemble_sum = 0.0f64;
        let mut node_visits = 0u32;
        for member in &self.members {
            let mut member_sum = 0.0f64;
            for tree in &member.trees {
                let mut node_index = 0usize;
                loop {
                    node_visits = node_visits.saturating_add(1);
                    let node = &tree.nodes[node_index];
                    if node.feature < 0 {
                        member_sum += node.positive_probability;
                        break;
                    }
                    let split_value = projected[node.feature as usize] as f64;
                    node_index = if split_value <= node.threshold {
                        node.left as usize
                    } else {
                        node.right as usize
                    };
                }
            }
            ensemble_sum += member_sum / member.trees.len() as f64;
        }
        let probability = ensemble_sum / self.members.len() as f64;
        ensure!(
            probability.is_finite() && (0.0..=1.0).contains(&probability),
            "A09 prediction is invalid"
        );
        Ok(LocalPrediction {
            probability,
            label: u8::from(probability >= self.effective_threshold),
            node_visits,
        })
    }
}

pub fn project_raw_features(raw: &[f64]) -> Result<[f32; PROJECTED_FEATURE_COUNT]> {
    ensure!(
        raw.len() == RAW_FEATURE_COUNT,
        "A09 raw feature count mismatch"
    );
    ensure!(
        raw.iter().all(|value| value.is_finite()),
        "A09 raw features contain non-finite values"
    );
    let ratio = |numerator: f64, denominator: f64| {
        if denominator <= 0.0 {
            0.0
        } else {
            numerator / denominator
        }
    };
    let log = |value: f64| value.max(0.0).ln_1p();
    let packets_fwd = raw[14];
    let packets_bwd = raw[15];
    let bytes_fwd = raw[16];
    let bytes_bwd = raw[17];
    let payload_fwd = raw[18];
    let payload_bwd = raw[19];
    let protocol = raw[0];
    let values = [
        ratio((bytes_fwd - bytes_bwd).abs(), bytes_fwd + bytes_bwd),
        raw[37],
        log(raw[22].max(raw[23])),
        log(raw[22].min(raw[23])),
        log(raw[20].max(raw[21])),
        log(raw[20].min(raw[21])),
        log(raw[30]),
        log(raw[4]),
        log(raw[33]),
        log(raw[6]),
        log(raw[32]),
        log(raw[26]),
        log(raw[12]),
        log(raw[8]),
        log(raw[10]),
        log(raw[11]),
        log(raw[7]),
        log(raw[9]),
        log(raw[3]),
        log(raw[5]),
        log(raw[29]),
        log(raw[28]),
        log(raw[27]),
        raw[13],
        log(raw[31]),
        ratio((packets_fwd - packets_bwd).abs(), packets_fwd + packets_bwd),
        ratio(payload_fwd + payload_bwd, bytes_fwd + bytes_bwd),
        ratio((payload_fwd - payload_bwd).abs(), payload_fwd + payload_bwd),
        raw[34],
        raw[35],
        raw[36],
        protocol,
        f64::from(protocol == 6.0),
        f64::from(protocol == 17.0),
    ];
    let mut projected = [0.0f32; PROJECTED_FEATURE_COUNT];
    for (target, value) in projected.iter_mut().zip(values) {
        ensure!(
            value.is_finite(),
            "A09 feature projection produced a non-finite value"
        );
        *target = value as f32;
    }
    Ok(projected)
}

fn validate_tree(nodes: &[Node]) -> Result<()> {
    let mut seen = HashSet::with_capacity(nodes.len());
    let mut stack = vec![0usize];
    while let Some(index) = stack.pop() {
        ensure!(
            index < nodes.len(),
            "portable A09 child index is out of range"
        );
        ensure!(
            seen.insert(index),
            "portable A09 tree has a cycle or shared child"
        );
        let node = &nodes[index];
        let leaf = node.left == -1 && node.right == -1;
        ensure!(
            leaf || (node.left >= 0 && node.right >= 0),
            "portable A09 node has a half-defined child pair"
        );
        if leaf {
            ensure!(
                node.feature == -2,
                "portable A09 leaf feature marker is invalid"
            );
            ensure!(
                node.positive_probability.is_finite()
                    && (0.0..=1.0).contains(&node.positive_probability),
                "portable A09 leaf probability is invalid"
            );
        } else {
            ensure!(
                node.feature >= 0 && node.feature < PROJECTED_FEATURE_COUNT as i32,
                "portable A09 split feature is out of range"
            );
            ensure!(
                node.threshold.is_finite(),
                "portable A09 split threshold is non-finite"
            );
            ensure!(
                node.left as usize > index && node.right as usize > index,
                "portable A09 children must follow their parent"
            );
            stack.push(node.right as usize);
            stack.push(node.left as usize);
        }
    }
    ensure!(
        seen.len() == nodes.len(),
        "portable A09 tree contains unreachable nodes"
    );
    Ok(())
}

fn validate_hex_sha(label: &str, value: &str) -> Result<()> {
    ensure!(
        value.len() == 64
            && value
                .bytes()
                .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte)),
        "{label} SHA-256 must be 64 lowercase hexadecimal characters"
    );
    Ok(())
}

fn constant_time_eq(left: &[u8], right: &[u8]) -> bool {
    if left.len() != right.len() {
        return false;
    }
    left.iter()
        .zip(right)
        .fold(0u8, |difference, (a, b)| difference | (a ^ b))
        == 0
}

struct Reader<'a> {
    bytes: &'a [u8],
    offset: usize,
}

impl<'a> Reader<'a> {
    fn new(bytes: &'a [u8]) -> Self {
        Self { bytes, offset: 0 }
    }
    fn remaining(&self) -> usize {
        self.bytes.len() - self.offset
    }
    fn take(&mut self, count: usize) -> Result<&'a [u8]> {
        let end = self
            .offset
            .checked_add(count)
            .context("portable A09 offset overflow")?;
        if end > self.bytes.len() {
            bail!("portable A09 artifact is truncated");
        }
        let value = &self.bytes[self.offset..end];
        self.offset = end;
        Ok(value)
    }
    fn u16(&mut self) -> Result<u16> {
        Ok(u16::from_le_bytes(self.take(2)?.try_into().unwrap()))
    }
    fn u32(&mut self) -> Result<u32> {
        Ok(u32::from_le_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn i32(&mut self) -> Result<i32> {
        Ok(i32::from_le_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn u64(&mut self) -> Result<u64> {
        Ok(u64::from_le_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn sha256_hex(&mut self) -> Result<String> {
        Ok(hex_lower(self.take(32)?))
    }
}

fn hex_lower(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        output.push(HEX[(byte >> 4) as usize] as char);
        output.push(HEX[(byte & 0x0f) as usize] as char);
    }
    output
}

pub fn sha256_hex(bytes: &[u8]) -> String {
    const INITIAL: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
        0x5be0cd19,
    ];
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4,
        0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
        0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f,
        0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
        0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116,
        0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
        0xc67178f2,
    ];
    let bit_length = (bytes.len() as u64).wrapping_mul(8);
    let mut padded = Vec::with_capacity((bytes.len() + 72) & !63);
    padded.extend_from_slice(bytes);
    padded.push(0x80);
    while padded.len() % 64 != 56 {
        padded.push(0);
    }
    padded.extend_from_slice(&bit_length.to_be_bytes());
    let mut state = INITIAL;
    for block in padded.chunks_exact(64) {
        let mut words = [0u32; 64];
        for (index, chunk) in block.chunks_exact(4).enumerate() {
            words[index] = u32::from_be_bytes(chunk.try_into().unwrap());
        }
        for index in 16..64 {
            let s0 = words[index - 15].rotate_right(7)
                ^ words[index - 15].rotate_right(18)
                ^ (words[index - 15] >> 3);
            let s1 = words[index - 2].rotate_right(17)
                ^ words[index - 2].rotate_right(19)
                ^ (words[index - 2] >> 10);
            words[index] = words[index - 16]
                .wrapping_add(s0)
                .wrapping_add(words[index - 7])
                .wrapping_add(s1);
        }
        let [mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut h] = state;
        for index in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = h
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[index])
                .wrapping_add(words[index]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            h = g;
            g = f;
            f = e;
            e = d.wrapping_add(t1);
            d = c;
            c = b;
            b = a;
            a = t1.wrapping_add(t2);
        }
        for (slot, value) in state.iter_mut().zip([a, b, c, d, e, f, g, h]) {
            *slot = slot.wrapping_add(value);
        }
    }
    let mut digest = [0u8; 32];
    for (chunk, word) in digest.chunks_exact_mut(4).zip(state) {
        chunk.copy_from_slice(&word.to_be_bytes());
    }
    hex_lower(&digest)
}
