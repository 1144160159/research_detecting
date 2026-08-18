#[path = "../src/a09_fallback.rs"]
mod a09_fallback;

use a09_fallback::{
    project_raw_features, sha256_hex, ExpectedPortableA09Identity, PortableA09,
    VerifiedLocalFallback, PROJECTED_FEATURE_COUNT, PROJECTED_FEATURE_NAMES,
};
use serde_json::json;

fn push_tree(bytes: &mut Vec<u8>, probability_left: f64, probability_right: f64) {
    bytes.extend_from_slice(&3u32.to_le_bytes());
    for (left, right, feature, threshold, probability) in [
        (1i32, 2i32, 31i32, 6.0f64, 0.0f64),
        (-1, -1, -2, 0.0, probability_left),
        (-1, -1, -2, 0.0, probability_right),
    ] {
        bytes.extend_from_slice(&left.to_le_bytes());
        bytes.extend_from_slice(&right.to_le_bytes());
        bytes.extend_from_slice(&feature.to_le_bytes());
        bytes.extend_from_slice(&threshold.to_bits().to_le_bytes());
        bytes.extend_from_slice(&probability.to_bits().to_le_bytes());
    }
}

fn artifact() -> (Vec<u8>, ExpectedPortableA09Identity) {
    let source = "11".repeat(32);
    let engine = "22".repeat(32);
    let contract = "33".repeat(32);
    let mut bytes = Vec::new();
    bytes.extend_from_slice(b"HFTA09P1");
    bytes.extend_from_slice(&1u32.to_le_bytes());
    bytes.extend_from_slice(&(PROJECTED_FEATURE_COUNT as u32).to_le_bytes());
    bytes.extend_from_slice(&38u32.to_le_bytes());
    bytes.extend_from_slice(&3u32.to_le_bytes());
    bytes.extend_from_slice(&[0x11; 32]);
    bytes.extend_from_slice(&[0x22; 32]);
    bytes.extend_from_slice(&[0x33; 32]);
    bytes.extend_from_slice(&0.5f64.to_bits().to_le_bytes());
    bytes.extend_from_slice(&(PROJECTED_FEATURE_COUNT as u32).to_le_bytes());
    for name in PROJECTED_FEATURE_NAMES {
        bytes.extend_from_slice(&(name.len() as u16).to_le_bytes());
        bytes.extend_from_slice(name.as_bytes());
    }
    for member in 0..3 {
        bytes.extend_from_slice(&(0.2f64 + member as f64 * 0.1).to_bits().to_le_bytes());
        bytes.extend_from_slice(&1u32.to_le_bytes());
        bytes.extend_from_slice(&200u32.to_le_bytes());
        for tree in 0..200 {
            let left = if tree == 0 {
                0.25 + member as f64 * 0.25
            } else {
                0.0
            };
            push_tree(&mut bytes, left, 1.0);
        }
    }
    let artifact_sha256 = sha256_hex(&bytes);
    (
        bytes,
        ExpectedPortableA09Identity {
            artifact_sha256,
            source_model_sha256: source,
            numpy_engine_sha256: engine,
            campaign_contract_sha256: contract,
        },
    )
}

#[test]
fn sha256_matches_known_vector() {
    assert_eq!(
        sha256_hex(b"abc"),
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    );
}

#[test]
fn identity_mismatch_fails_closed() {
    let (bytes, mut expected) = artifact();
    expected.source_model_sha256 = "44".repeat(32);
    assert!(PortableA09::from_bytes(&bytes, &expected).is_err());
}

#[test]
fn artifact_mutation_fails_closed() {
    let (mut bytes, expected) = artifact();
    let last = bytes.len() - 1;
    bytes[last] ^= 1;
    assert!(PortableA09::from_bytes(&bytes, &expected).is_err());
}

#[test]
fn f32_split_and_ordered_ensemble_are_deterministic() {
    let (bytes, expected) = artifact();
    let model = PortableA09::from_bytes(&bytes, &expected).unwrap();
    let mut projected = [0.0f32; PROJECTED_FEATURE_COUNT];
    projected[31] = 6.0;
    let prediction = model.predict_projected(&projected).unwrap();
    let expected_probability: f64 = ((0.25 / 200.0) + (0.5 / 200.0) + (0.75 / 200.0)) / 3.0;
    assert_eq!(
        prediction.probability.to_bits(),
        expected_probability.to_bits()
    );
    assert_eq!(prediction.label, 0);
    assert_eq!(prediction.node_visits, 1_200);
    projected[31] = f32::from_bits(6.0f32.to_bits() + 1);
    assert!(model.predict_projected(&projected).unwrap().probability > 0.99);
}

#[test]
fn raw_projection_matches_frozen_feature_order() {
    let mut raw = [0.0f64; 38];
    raw[0] = 17.0;
    raw[3] = 9.0;
    raw[4] = 100.0;
    raw[5] = 40.0;
    raw[14] = 8.0;
    raw[15] = 2.0;
    raw[16] = 80.0;
    raw[17] = 20.0;
    raw[18] = 30.0;
    raw[19] = 10.0;
    raw[34] = 7.5;
    raw[37] = 1.0;
    let projected = project_raw_features(&raw).unwrap();
    assert_eq!(projected[0], 0.6);
    assert_eq!(projected[1], 1.0);
    assert_eq!(projected[7], 100.0f32.ln_1p());
    assert_eq!(projected[25], 0.6);
    assert_eq!(projected[26], 0.4);
    assert_eq!(projected[27], 0.5);
    assert_eq!(projected[28], 7.5);
    assert_eq!(projected[31], 17.0);
    assert_eq!(projected[32], 0.0);
    assert_eq!(projected[33], 1.0);
}

#[test]
fn non_finite_input_is_rejected() {
    let mut raw = [0.0f64; 38];
    raw[3] = f64::NAN;
    assert!(project_raw_features(&raw).is_err());
}

#[test]
fn verified_runtime_requires_bit_exact_holdout_and_physical_benchmark_receipt() {
    let (bytes, expected) = artifact();
    let root = std::env::temp_dir().join(format!(
        "hft-a09-fallback-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    std::fs::create_dir(&root).unwrap();
    let artifact_path = root.join("a09.portable");
    std::fs::write(&artifact_path, bytes).unwrap();
    let receipt_path = root.join("quality.json");
    let receipt = json!({
        "schema_version": 1,
        "scope": "hft_mgbs_local_a09_fallback_quality_receipt_v1",
        "candidate_id": "A09",
        "portable_artifact_sha256": expected.artifact_sha256.clone(),
        "source_model_sha256": expected.source_model_sha256.clone(),
        "numpy_engine_sha256": expected.numpy_engine_sha256.clone(),
        "campaign_contract_sha256": expected.campaign_contract_sha256.clone(),
        "holdout_input_sha256": "44".repeat(32),
        "equivalence_evidence_sha256": "55".repeat(32),
        "physical_benchmark_evidence_sha256": "66".repeat(32),
        "rust_fallback_source_sha256": "77".repeat(32),
        "capture_binary_sha256": "88".repeat(32),
        "evidence_manifest_sha256": "99".repeat(32),
        "cross_language_sample_count": 100,
        "probability_bit_exact_count": 100,
        "decision_exact_count": 100,
        "physical_benchmark_runs": 3,
        "physical_flows_per_second_min": 6000.0,
        "physical_p99_us_max": 9000.0,
        "accepted": true,
        "production_release_accepted": false,
        "final_pareto_ingestion_allowed": false,
        "errors": []
    });
    let receipt_raw = serde_json::to_vec(&receipt).unwrap();
    std::fs::write(&receipt_path, &receipt_raw).unwrap();
    let verified = VerifiedLocalFallback::load(
        &artifact_path,
        &receipt_path,
        &sha256_hex(&receipt_raw),
        &expected,
    )
    .unwrap();
    assert!(verified
        .backend_identity()
        .contains("quality_receipt_sha256="));
    let mut invalid = receipt;
    invalid["probability_bit_exact_count"] = json!(99);
    let invalid_raw = serde_json::to_vec(&invalid).unwrap();
    std::fs::write(&receipt_path, &invalid_raw).unwrap();
    assert!(VerifiedLocalFallback::load(
        &artifact_path,
        &receipt_path,
        &sha256_hex(&invalid_raw),
        &expected,
    )
    .is_err());
    std::fs::remove_dir_all(root).unwrap();
}
