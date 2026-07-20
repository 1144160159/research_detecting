# Frozen candidate confirmation

Paired runs: 96; inference units: 24 scenarios.
Seed repeats are averaged within scenarios before inference.

| Metric | Reference | Candidate | Oriented improvement | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.848956 | 0.848956 | +0.000000 | [+0.000000, +0.000000] | 0/24/0 | NA |
| unknown_auroc | 0.862990 | 0.878918 | +0.015928 | [-0.003591, +0.041266] | 16/0/8 | 1 |
| unknown_aupr | 0.759909 | 0.769628 | +0.009719 | [-0.014910, +0.034843] | 12/0/12 | 1 |
| unknown_fpr95 | 0.300814 | 0.278132 | +0.022681 | [-0.025621, +0.070728] | 15/0/9 | 1 |
| oscr | 0.777998 | 0.793382 | +0.015384 | [-0.003999, +0.041588] | 16/0/8 | 1 |
| known_acceptance_rate | 0.933886 | 0.938242 | +0.004356 | [-0.001292, +0.009963] | 16/0/8 | NA |
| unknown_rejection_rate | 0.548902 | 0.581977 | +0.033075 | [-0.033902, +0.107087] | 13/0/11 | NA |

## Decision

Mean safety gate: **PASS**
Confirmatory evidence: **FAIL**

The confirmatory gate requires positive AUROC, non-regressing AUPR/OSCR, FPR95 raw regression no greater than 0.01, a positive AUROC bootstrap lower bound, and Holm-adjusted AUROC p < 0.05.

## Frozen cross-suite gate

Status: **not_confirmed**.

```json
{
  "frozen_gate": "cross_suite_fixed_risk_v1",
  "combined_auroc_bootstrap_lower_gt_zero": false,
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
  "passes": false
}
```
