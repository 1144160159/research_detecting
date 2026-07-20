# Frozen candidate confirmation

Paired runs: 96; inference units: 24 scenarios.
Seed repeats are averaged within scenarios before inference.

| Metric | Reference | Candidate | Oriented improvement | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.847295 | 0.847295 | +0.000000 | [+0.000000, +0.000000] | 0/24/0 | NA |
| unknown_auroc | 0.824772 | 0.853062 | +0.028290 | [+0.008569, +0.049984] | 20/0/4 | 0.0317 |
| unknown_aupr | 0.703081 | 0.730558 | +0.027477 | [+0.004458, +0.051455] | 18/0/6 | 0.0357 |
| unknown_fpr95 | 0.354040 | 0.305294 | +0.048746 | [+0.010266, +0.090704] | 18/0/6 | 0.0357 |
| oscr | 0.741753 | 0.767729 | +0.025976 | [+0.007786, +0.047119] | 17/0/7 | 0.0317 |
| known_acceptance_rate | 0.909129 | 0.914659 | +0.005531 | [-0.004107, +0.014779] | 14/0/10 | NA |
| unknown_rejection_rate | 0.526552 | 0.578466 | +0.051914 | [+0.001790, +0.103856] | 17/0/7 | NA |

## Decision

Mean safety gate: **PASS**
Confirmatory evidence: **PASS**

The confirmatory gate requires positive AUROC, non-regressing AUPR/OSCR, FPR95 raw regression no greater than 0.01, a positive AUROC bootstrap lower bound, and Holm-adjusted AUROC p < 0.05.

## Frozen cross-suite gate

Status: **confirmed**.

```json
{
  "frozen_gate": "cross_suite_fixed_risk_v1",
  "combined_auroc_bootstrap_lower_gt_zero": true,
  "combined_safety_nonregression_tolerance": 0.01,
  "combined_safety_metrics": {
    "known_macro_f1": true,
    "unknown_aupr": true,
    "unknown_fpr95": true,
    "oscr": true
  },
  "all_combined_safety_metrics_pass": true,
  "suite_unknown_metric_positive": {
    "nf_cse": {
      "unknown_auroc": true,
      "unknown_aupr": true,
      "unknown_fpr95": true,
      "oscr": true
    },
    "ustc_tfc2016": {
      "unknown_auroc": true,
      "unknown_aupr": true,
      "unknown_fpr95": true,
      "oscr": true
    }
  },
  "all_suite_unknown_metrics_positive": true,
  "passes": true
}
```
