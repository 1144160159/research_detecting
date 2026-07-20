# Strict-v4 NECO-ID90 pilot analysis

Expand NECO-ID90 to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.770719 | 0.683294 | 0.503985 | 0.626929 | 0.578047 | 1.50 |
| mlp_energy | 0.746256 | 0.636243 | 0.485875 | 0.587831 | 0.544774 | 2.25 |
| neco_id90 | 0.746256 | 0.660776 | 0.473864 | 0.599999 | 0.545413 | 2.25 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `nondegenerate_dimension`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: PASS
- `overall_gain`: PASS
- `suite_robustness`: FAIL
