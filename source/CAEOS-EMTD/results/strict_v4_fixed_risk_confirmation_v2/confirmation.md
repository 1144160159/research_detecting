# Strict-v4 fixed-risk frozen confirmation

State: **rejected**; runs: 12; scenario blocks: 6.
Seed repeats are averaged within scenarios before inference.

| Metric | Reference | Candidate | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.710562 | 0.710562 | +0.000000 | [+0.000000, +0.000000] | 0/6/0 | NA |
| unknown_auroc | 0.728314 | 0.694177 | -0.034136 | [-0.141778, +0.049258] | 3/0/3 | 1 |
| unknown_aupr | 0.389197 | 0.385636 | -0.003561 | [-0.056037, +0.040704] | 3/0/3 | 1 |
| unknown_fpr95 | 0.696998 | 0.637595 | +0.059403 | [-0.128026, +0.269258] | 4/0/2 | 1 |
| oscr | 0.522011 | 0.531454 | +0.009443 | [-0.040992, +0.053057] | 3/0/3 | 1 |
| known_acceptance_rate | 0.943888 | 0.946643 | +0.002755 | [-0.000603, +0.006774] | 5/0/1 | NA |
| unknown_rejection_rate | 0.146159 | 0.159024 | +0.012865 | [-0.014983, +0.035514] | 4/0/2 | NA |

## Decision

Frozen gate: **FAIL**.
Candidate paths: `{'cauchy_all': 12}`.
Reference paths: `{'cauchy_modality_support_union': 12}`.
