# Strict-v4 fixed-risk frozen confirmation

State: **rejected**; runs: 12; scenario blocks: 6.
Seed repeats are averaged within scenarios before inference.

| Metric | Reference | Candidate | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.711913 | 0.711913 | +0.000000 | [+0.000000, +0.000000] | 0/6/0 | NA |
| unknown_auroc | 0.705404 | 0.723614 | +0.018210 | [-0.026228, +0.062518] | 3/0/3 | 1 |
| unknown_aupr | 0.448382 | 0.425886 | -0.022497 | [-0.094705, +0.032454] | 3/0/3 | 1 |
| unknown_fpr95 | 0.682141 | 0.475555 | +0.206586 | [+0.083812, +0.339629] | 5/0/1 | 0.25 |
| oscr | 0.496062 | 0.549780 | +0.053718 | [+0.026935, +0.076628] | 5/0/1 | 0.25 |
| known_acceptance_rate | 0.952211 | 0.954328 | +0.002117 | [-0.000453, +0.004487] | 4/0/2 | NA |
| unknown_rejection_rate | 0.262609 | 0.224292 | -0.038317 | [-0.125983, +0.021183] | 2/0/4 | NA |

## Decision

Frozen gate: **FAIL**.
Candidate paths: `{'cauchy_all': 6, 'conflict_augmented': 6}`.
Reference paths: `{'cauchy_modality_support_union': 12}`.
