from __future__ import annotations

from dataclasses import dataclass

from caeos.pairwise_deployment import PairwiseDeploymentBundle


@dataclass
class KRCDeploymentBundle(PairwiseDeploymentBundle):
    """Raw-feature preprocessing bound to one frozen KRC runtime."""

    source_split_fingerprint: str
    source_capture_manifest_sha256: str

    def evidence(self) -> dict[str, object]:
        value = dict(super().evidence())
        value.update(
            {
                "schema_version": "strict_v4_krc_deployment_bundle_v1",
                "algorithm": "krc_csr_caeos_v1",
                "source_split_fingerprint": self.source_split_fingerprint,
                "source_capture_manifest_sha256": (
                    self.source_capture_manifest_sha256
                ),
                "preprocessing_reconstructed_without_model_refit": True,
                "parrot_used_for_fit_selection_calibration_or_threshold": False,
            }
        )
        return value
