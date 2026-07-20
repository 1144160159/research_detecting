# Strict-v4 ASH pilot analysis

Expand ASH to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.780840 | 0.755478 | 0.546968 | 0.523552 | 0.628559 | 1.00 |
| mlp_energy | 0.757600 | 0.706431 | 0.519941 | 0.579778 | 0.599078 | 2.00 |
| ash_s_90 | 0.706656 | 0.562880 | 0.405167 | 0.795492 | 0.457863 | 3.00 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_tolerance`: FAIL
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
