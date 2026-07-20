# Strict-v4 AdaSCALE pilot analysis

Expand AdaSCALE to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.784446 | 0.701389 | 0.482337 | 0.583002 | 0.603223 | 1.00 |
| mlp_energy | 0.760068 | 0.650331 | 0.451810 | 0.613100 | 0.570416 | 2.00 |
| mlp_scale | 0.754443 | 0.586852 | 0.436730 | 0.636833 | 0.522101 | 3.25 |
| adascale_a_60_85 | 0.758470 | 0.589646 | 0.433277 | 0.685710 | 0.519808 | 3.75 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_tolerance`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
