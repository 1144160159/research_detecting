import numpy as np

from caeos.krc_deployment import KRCDeploymentBundle


class Runtime:
    clean_threshold = 0.8

    def predict(self, views):
        count = len(views[0])
        return {
            "prediction": np.zeros(count, dtype=np.int64),
            "probability": np.tile([[0.9, 0.1]], (count, 1)),
            "risk": np.full(count, 0.2),
        }

    def evidence(self):
        return {"schema_version": "strict_v4_krc_csr_runtime_v1"}


def test_deployment_evidence_records_no_refit_boundary():
    bundle = KRCDeploymentBundle(
        runtime=Runtime(),
        modality_names=("flow",),
        modalities={"flow": ("feature",)},
        processor_states={
            "flow": {
                "median": [0.0],
                "mean": [0.0],
                "std": [1.0],
            }
        },
        class_names=("Benign", "Attack"),
        benign_index=0,
        selected_threshold=0.8,
        risk_policy_name="frozen",
        source_config_sha256="a" * 64,
        source_split_fingerprint="b" * 64,
        source_capture_manifest_sha256="c" * 64,
    )
    evidence = bundle.evidence()
    assert evidence["schema_version"] == "strict_v4_krc_deployment_bundle_v1"
    assert evidence["preprocessing_reconstructed_without_model_refit"] is True
    assert (
        evidence["parrot_used_for_fit_selection_calibration_or_threshold"]
        is False
    )
