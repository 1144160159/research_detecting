# Strict-v4 frozen domain-safe router confirmation

Validation: **PASS**; paired runs: 306; scenarios: 102; seeds: [137, 139, 149].
Seed repeats are averaged inside each dataset-scenario before inference.

| Metric | Pairwise | Router | Gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.794300 | 0.794300 | +0.000000 | [+0.000000, +0.000000] | 0/102/0 | NA |
| unknown_auroc | 0.773355 | 0.773496 | +0.000141 | [-0.009280, +0.008683] | 25/60/17 | 0.409 |
| unknown_aupr | 0.584167 | 0.584654 | +0.000487 | [-0.008171, +0.008494] | 28/60/14 | 0.409 |
| unknown_fpr95 | 0.485244 | 0.467835 | +0.017408 | [-0.011557, +0.045465] | 27/60/15 | 0.153 |
| oscr | 0.631643 | 0.637717 | +0.006074 | [-0.002968, +0.014972] | 26/60/16 | 0.181 |
| known_acceptance_rate | 0.941885 | 0.940863 | -0.001022 | [-0.003783, +0.000953] | 19/60/23 | NA |
| unknown_rejection_rate | 0.399126 | 0.405184 | +0.006058 | [-0.010364, +0.022797] | 24/60/18 | NA |

## Decision

Frozen confirmation gate: **FAIL**.
