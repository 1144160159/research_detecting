# Strict-v4 NNGuide pilot analysis

Expand NNGuide to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.781245 | 0.706469 | 0.504451 | 0.547006 | 0.605379 | 1.25 |
| nnguide_energy | 0.755270 | 0.662106 | 0.437152 | 0.538943 | 0.558579 | 1.75 |
| mlp_energy | 0.755270 | 0.612044 | 0.408809 | 0.604198 | 0.546615 | 3.00 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `top_two_rank`: PASS
- `metric_breadth`: PASS
- `overall_gain`: PASS
- `suite_robustness`: FAIL
