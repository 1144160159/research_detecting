# Strict-v4 local-rank confirmation

State: **rejected**; runs: 12; scenario blocks: 6.
Endpoint counts: `{'cauchy_modality_support_union': 10, 'pseudo_unknown_local_rank_blend': 2}`.

| Metric | Reference | Candidate | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.706518 | 0.706518 | +0.000000 | [+0.000000, +0.000000] | 0/6/0 | NA |
| unknown_auroc | 0.647747 | 0.645970 | -0.001777 | [-0.005165, +0.000000] | 0/4/2 | 1 |
| unknown_aupr | 0.476839 | 0.475224 | -0.001615 | [-0.004924, +0.000080] | 1/4/1 | 1 |
| unknown_fpr95 | 0.775581 | 0.753586 | +0.021995 | [-0.005544, +0.071530] | 1/4/1 | 1 |
| oscr | 0.450923 | 0.452831 | +0.001908 | [-0.002627, +0.008352] | 1/4/1 | 1 |
| known_acceptance_rate | 0.949343 | 0.950223 | +0.000880 | [+0.000000, +0.002640] | 1/5/0 | NA |
| unknown_rejection_rate | 0.232296 | 0.220608 | -0.011687 | [-0.044250, +0.009188] | 1/4/1 | NA |

Frozen gate: **FAIL**.
