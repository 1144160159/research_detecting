# Strict-v4 LINe-IDTune pilot analysis

Expand LINe-IDTune to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.791481 | 0.710610 | 0.602572 | 0.565661 | 0.591212 | 1.25 |
| mlp_energy | 0.760686 | 0.679914 | 0.545394 | 0.589621 | 0.580155 | 2.25 |
| line_idtune | 0.760686 | 0.673998 | 0.519235 | 0.550657 | 0.578695 | 2.50 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: PASS
- `suite_robustness`: FAIL
