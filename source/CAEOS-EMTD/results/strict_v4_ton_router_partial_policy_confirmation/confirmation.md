# Strict-v4 ToN router partial-policy confirmation

State: **rejected**; runs: 18; scenarios: 9.
Endpoint counts: `{'cauchy_all': 12, 'cauchy_modality_support_union': 6}`. CICIoT2023 remains exact current-risk fallback.

| Metric | Reference | Router | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.801493 | 0.801493 | +0.000000 | [+0.000000, +0.000000] | 0/9/0 | NA |
| unknown_auroc | 0.726587 | 0.749467 | +0.022880 | [-0.004599, +0.050483] | 4/3/2 | 0.625 |
| unknown_aupr | 0.605691 | 0.624985 | +0.019294 | [-0.001665, +0.041170] | 4/3/2 | 0.625 |
| unknown_fpr95 | 0.625721 | 0.593894 | +0.031826 | [-0.126059, +0.179249] | 4/3/2 | 0.625 |
| oscr | 0.571566 | 0.601621 | +0.030055 | [+0.003588, +0.057535] | 4/3/2 | 0.625 |
| known_acceptance_rate | 0.941862 | 0.945208 | +0.003346 | [+0.000938, +0.005872] | 5/3/1 | NA |
| unknown_rejection_rate | 0.304670 | 0.295447 | -0.009222 | [-0.049278, +0.017333] | 4/3/2 | NA |

Frozen gate: **FAIL**.
