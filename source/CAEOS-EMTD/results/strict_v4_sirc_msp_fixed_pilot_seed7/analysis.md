# Strict-v4 SIRC-MSP-Fixed pilot analysis

Expand any SIRC variant to full 102: `YES`.
Passing variants: `sirc_msp_residual`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| sirc_msp_residual | 0.757017 | 0.738878 | 0.540371 | 0.460899 | 0.633014 | 1.50 |
| opendetect | 0.783181 | 0.743494 | 0.514343 | 0.508182 | 0.644400 | 2.00 |
| sirc_msp_l1 | 0.757017 | 0.707220 | 0.486652 | 0.501730 | 0.615316 | 2.75 |
| mlp_msp | 0.757017 | 0.703197 | 0.486077 | 0.505195 | 0.613944 | 3.75 |

## sirc_msp_l1 expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `nondegenerate_score`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: PASS
- `overall_gain`: PASS
- `oscr_gain`: PASS
- `suite_robustness`: PASS

## sirc_msp_residual expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `nondegenerate_score`: PASS
- `top_two_rank`: PASS
- `metric_breadth`: PASS
- `overall_gain`: PASS
- `oscr_gain`: PASS
- `suite_robustness`: PASS
