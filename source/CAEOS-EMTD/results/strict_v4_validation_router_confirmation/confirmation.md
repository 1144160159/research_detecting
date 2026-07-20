# Strict-v4 known-validation router confirmation

State: **rejected**; runs: 30; scenario blocks: 15.
Seed repeats are averaged within scenarios before inference.
Endpoint counts: `{'cauchy_modality_support_union': 15, 'cauchy_all': 15}`.

| Metric | Reference | Router | Oriented gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.722593 | 0.722593 | +0.000000 | [+0.000000, +0.000000] | 0/15/0 | NA |
| unknown_auroc | 0.713303 | 0.730603 | +0.017300 | [+0.005831, +0.029289] | 8/4/3 | 0.0556641 |
| unknown_aupr | 0.484351 | 0.491656 | +0.007306 | [-0.001336, +0.016120] | 8/4/3 | 0.147461 |
| unknown_fpr95 | 0.670483 | 0.573882 | +0.096601 | [+0.031615, +0.163431] | 8/4/3 | 0.0556641 |
| oscr | 0.511059 | 0.542779 | +0.031720 | [+0.013080, +0.057419] | 11/4/0 | 0.00390625 |
| known_acceptance_rate | 0.946846 | 0.948899 | +0.002053 | [+0.000460, +0.003977] | 8/4/3 | NA |
| unknown_rejection_rate | 0.224734 | 0.229501 | +0.004767 | [-0.005000, +0.017634] | 6/5/4 | NA |

Frozen gate: **FAIL**.
