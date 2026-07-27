from __future__ import annotations

import copy

import pytest

from audit_medaf_baseline_admission import inspect_source


def source_fixture():
    return {
        "README.md": "official",
        "core/net.py": """
branch1_cls branch2_cls branch3_cls
gate_pred = F.softmax(x)
gate_logits = gate_logits.sum(-1)
nn.Conv2d(1, 1, 1)
nn.AdaptiveAvgPool2d(1)
""",
        "core/train.py": """
def attnDiv(cams):
    return cams
def train(train_loader, model, criterion, optimizer, args):
    value = attnDiv(branch_cams)
""",
        "core/test.py": """
fpr, tpr, thresholds = roc_curve(open_labels, prob)
thresh_idx = np.abs(np.array(tpr) - 0.95).argmin()
open_pred = (total_pred > threshold)
print('AUROC:', 'AUPR_IN:', 'AUPR_OUT:')
""",
        "misc/osr.yml": """
score_wgts : [1,0,0]
branch_opt : -1
gate_temp  : 100
lgs_temp    : 100
""",
        "osr_main.py": """
if (epoch + 1) % options['test_step'] == 0:
    evaluation(model, test_loader, out_loader)
""",
        "requirements.txt": "numpy\n",
    }


def test_source_contract_detects_test_threshold_and_missing_metrics() -> None:
    checks = inspect_source(source_fixture())
    assert checks["three_expert_branches_present"] is True
    assert checks["attention_diversity_training_present"] is True
    assert checks["source_threshold_uses_combined_test_unknown_labels"] is True
    assert checks["source_evaluates_test_and_unknown_each_epoch"] is True
    assert checks["official_score_is_gated_msp"] is True
    assert checks["source_reports_fpr95"] is False
    assert checks["source_reports_oscr"] is False
    assert checks["source_reports_ece"] is False


def test_source_contract_rejects_missing_diversity_mechanism() -> None:
    files = copy.deepcopy(source_fixture())
    files["core/train.py"] = "def train(train_loader): pass"
    with pytest.raises(ValueError, match="source contract mismatch"):
        inspect_source(files)
