# Strict-v4 known-validation router confirmation

State: **rejected**; runs: 30; scenario blocks: 15.
Seed repeats are averaged within scenarios before inference.
Endpoint counts: `{'cauchy_all': 21, 'cauchy_modality_support_union': 9}`.

| Metric | Reference | Router | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.721096 | 0.721096 | +0.000000 | [+0.000000, +0.000000] | 0/15/0 | NA |
| unknown_auroc | 0.776590 | 0.771214 | -0.005377 | [-0.049095, +0.029803] | 7/3/5 | 1 |
| unknown_aupr | 0.581252 | 0.548692 | -0.032559 | [-0.095048, +0.017690] | 6/3/6 | 1 |
| unknown_fpr95 | 0.529504 | 0.465379 | +0.064126 | [-0.040453, +0.173123] | 8/3/4 | 0.903809 |
| oscr | 0.544956 | 0.561939 | +0.016983 | [-0.005729, +0.039644] | 8/3/4 | 0.814453 |
| known_acceptance_rate | 0.945227 | 0.946527 | +0.001301 | [-0.000311, +0.002954] | 7/3/5 | NA |
| unknown_rejection_rate | 0.337857 | 0.321790 | -0.016067 | [-0.069301, +0.024435] | 6/4/5 | NA |

Frozen gate: **FAIL**.
