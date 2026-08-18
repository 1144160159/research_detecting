# Strict-v4 k-LND pilot analysis

Selected variant: `klnd3`.
Expand selected k-LND to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.782832 | 0.681331 | 0.559837 | 0.583576 | 0.575264 | 1.25 |
| mlp_energy | 0.756102 | 0.647549 | 0.510657 | 0.570481 | 0.560952 | 1.75 |
| mlp_msp | 0.756102 | 0.609129 | 0.460407 | 0.596534 | 0.543471 | 3.75 |
| klnd3 | 0.756102 | 0.590787 | 0.480836 | 0.626373 | 0.490938 | 4.25 |
| klnd2 | 0.756102 | 0.582201 | 0.485798 | 0.605259 | 0.483343 | 4.75 |
| klnd1 | 0.756102 | 0.589526 | 0.472214 | 0.637966 | 0.488157 | 5.25 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_only_fit`: PASS
- `nondegenerate_score`: PASS
- `known_f1_tolerance`: PASS
- `top_half_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
