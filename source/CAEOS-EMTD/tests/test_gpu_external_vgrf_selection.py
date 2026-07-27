from __future__ import annotations

import json
from pathlib import Path

from create_gpu_external_evaluation_protocol import verify_design
from summarize_gpu_external_evaluation import report


ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    design_path = ROOT / "results/gpu_external_dataset_evaluation_v1/design_protocol.json"
    design = json.loads(design_path.read_text(encoding="utf-8"))
    verify_design(design, ROOT)
    selected = "caeos_validation_gated_class_conditional_reliability_fusion"
    assert selected in design["allowed_selected_algorithms"]
    assert design["selection_sources"]["vgrf_pilot"]["final_selection_path"].endswith("final_selection.json")
    assert design["vgrf_policy"]["unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction"] is False
    metrics = {
        "schema_version": "strict_v4_validation_gated_reliability_fusion_metrics_v1",
        "diagnostics": {
            "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction": False,
            "test_labels_used_for_final_metrics_only": True,
            "enabled": False,
            "exact_fallback": True,
        },
        "reports": {"candidate": {
            "known_macro_f1": 0.9,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "unknown_fpr95": 0.2,
            "oscr": 0.75,
        }},
    }
    parsed = report(metrics, selected)
    assert parsed["unknown_auroc"] == 0.8 and parsed["unknown_fpr95"] == 0.2
    watcher = (ROOT / "scripts/wait_and_run_gpu_external_evaluation.sh").read_text(encoding="utf-8")
    assert "VGRF_BRANCH/branch_complete" in watcher and "MAL_TLS_CONFIRMATION/confirmation_complete" in watcher
    print("6/6 PASS")


if __name__ == "__main__":
    main()
