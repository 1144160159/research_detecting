# Strict-v4 NAC-UE-Fixed pilot analysis

Expand NAC-UE-Fixed to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.777043 | 0.723690 | 0.549098 | 0.512369 | 0.587063 | 1.00 |
| mlp_energy | 0.740311 | 0.670628 | 0.499860 | 0.548813 | 0.561655 | 2.50 |
| nac_ue_fixed | 0.740311 | 0.689500 | 0.480847 | 0.611261 | 0.572050 | 2.50 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `nondegenerate_score`: PASS
- `coverage_support`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: PASS
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
