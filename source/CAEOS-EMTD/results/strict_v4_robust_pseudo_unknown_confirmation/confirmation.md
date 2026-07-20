# Strict-v4 robust pseudo-unknown confirmation

State: **rejected**; runs: 12; scenario blocks: 6.
Endpoint counts: `{'cauchy_modality_support_union': 2, 'pseudo_unknown_learned_blend': 10}`.
Seed repeats are averaged within scenarios before inference.

| Metric | Reference | Candidate policy | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.704910 | 0.704910 | +0.000000 | [+0.000000, +0.000000] | 0/6/0 | NA |
| unknown_auroc | 0.676875 | 0.677848 | +0.000973 | [-0.012403, +0.015260] | 2/1/3 | 1 |
| unknown_aupr | 0.500296 | 0.482993 | -0.017303 | [-0.078383, +0.020054] | 3/1/2 | 1 |
| unknown_fpr95 | 0.762121 | 0.651553 | +0.110567 | [-0.012262, +0.237246] | 3/1/2 | 0.9375 |
| oscr | 0.471041 | 0.490505 | +0.019465 | [+0.006741, +0.032752] | 5/1/0 | 0.25 |
| known_acceptance_rate | 0.938467 | 0.939930 | +0.001463 | [-0.003094, +0.005360] | 4/1/1 | NA |
| unknown_rejection_rate | 0.272873 | 0.275320 | +0.002448 | [-0.073250, +0.070729] | 3/1/2 | NA |

Frozen gate: **FAIL**.
