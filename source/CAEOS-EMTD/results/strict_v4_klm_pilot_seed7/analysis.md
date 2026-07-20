# Strict-v4 KLM pilot analysis

Expand KLM to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.769013 | 0.848994 | 0.651362 | 0.337673 | 0.683092 | 1.00 |
| mlp_energy | 0.743401 | 0.776583 | 0.594109 | 0.426248 | 0.650151 | 2.00 |
| klm | 0.743401 | 0.735157 | 0.574731 | 0.579268 | 0.581681 | 3.00 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
