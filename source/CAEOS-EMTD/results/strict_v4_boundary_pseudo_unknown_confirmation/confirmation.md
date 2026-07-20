# Strict-v4 boundary pseudo-unknown confirmation

State: **rejected**; runs: 12; scenario blocks: 6.
Endpoint counts: `{'cauchy_modality_support_union': 7, 'pseudo_unknown_learned_blend': 5}`.

| Metric | Reference | Candidate | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.705142 | 0.705142 | +0.000000 | [+0.000000, +0.000000] | 0/6/0 | NA |
| unknown_auroc | 0.654574 | 0.648486 | -0.006089 | [-0.025183, +0.005500] | 2/3/1 | 1 |
| unknown_aupr | 0.479175 | 0.481553 | +0.002378 | [-0.005140, +0.013048] | 1/3/2 | 1 |
| unknown_fpr95 | 0.752985 | 0.711489 | +0.041495 | [-0.017247, +0.108021] | 2/3/1 | 1 |
| oscr | 0.453414 | 0.456720 | +0.003306 | [-0.000984, +0.007673] | 2/3/1 | 1 |
| known_acceptance_rate | 0.942933 | 0.943067 | +0.000135 | [-0.001180, +0.001584] | 1/4/1 | NA |
| unknown_rejection_rate | 0.245695 | 0.275861 | +0.030166 | [-0.001833, +0.073582] | 2/3/1 | NA |

Frozen gate: **FAIL**.
