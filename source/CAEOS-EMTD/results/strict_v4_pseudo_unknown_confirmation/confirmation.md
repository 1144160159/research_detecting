# Strict-v4 pseudo-unknown risk confirmation

State: **rejected**; runs: 12; scenario blocks: 6.
Seed repeats are averaged within scenarios before inference.
Endpoint counts: `{'pseudo_unknown_learned_blend': 12}`.

| Metric | Reference | Candidate policy | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.689758 | 0.689758 | +0.000000 | [+0.000000, +0.000000] | 0/6/0 | NA |
| unknown_auroc | 0.631606 | 0.628839 | -0.002767 | [-0.046851, +0.036861] | 3/0/3 | 1 |
| unknown_aupr | 0.360266 | 0.351550 | -0.008716 | [-0.038558, +0.025215] | 3/0/3 | 1 |
| unknown_fpr95 | 0.696809 | 0.596356 | +0.100452 | [+0.039153, +0.171609] | 6/0/0 | 0.125 |
| oscr | 0.424096 | 0.473367 | +0.049271 | [+0.008395, +0.095238] | 5/0/1 | 0.28125 |
| known_acceptance_rate | 0.954724 | 0.954298 | -0.000425 | [-0.002740, +0.002124] | 3/0/3 | NA |
| unknown_rejection_rate | 0.183334 | 0.236785 | +0.053450 | [-0.001164, +0.144529] | 4/0/2 | NA |

Frozen gate: **FAIL**.
