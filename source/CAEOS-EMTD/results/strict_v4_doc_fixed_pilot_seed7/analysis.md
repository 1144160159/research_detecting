# Strict-v4 DOC-Fixed pilot analysis

Expand DOC-Fixed to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.766127 | 0.800369 | 0.635266 | 0.350782 | 0.637880 | 1.00 |
| mlp_energy | 0.734638 | 0.693708 | 0.541199 | 0.473140 | 0.573935 | 2.00 |
| mlp_msp | 0.734638 | 0.534830 | 0.348210 | 0.633106 | 0.492447 | 3.25 |
| doc_fixed | 0.764091 | 0.506392 | 0.394597 | 0.698118 | 0.443588 | 3.75 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_tolerance`: PASS
- `optimization_integrity`: PASS
- `nondegenerate_score`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
