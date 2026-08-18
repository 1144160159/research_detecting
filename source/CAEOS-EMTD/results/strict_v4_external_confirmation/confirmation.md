# Strict-v4 final algorithm vs strongest external comparator

Candidate: `caeos_pairwise`; comparator: `opendetect`.

| Metric | Comparator | Candidate | Gain | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.762873 | 0.794300 | +0.031427 | [+0.026757, +0.036396] | 102/0/0 | NA |
| unknown_auroc | 0.716103 | 0.773355 | +0.057252 | [+0.026906, +0.089224] | 66/0/36 | 0.000335 |
| unknown_aupr | 0.511447 | 0.584167 | +0.072720 | [+0.043515, +0.103027] | 76/0/26 | 2.39e-06 |
| unknown_fpr95 | 0.527120 | 0.485244 | +0.041876 | [-0.017359, +0.101159] | 55/0/47 | 0.194 |
| oscr | 0.582429 | 0.631643 | +0.049214 | [+0.017861, +0.080428] | 72/0/30 | 0.000172 |
| known_acceptance_rate | 0.941782 | 0.941885 | +0.000104 | [-0.004714, +0.005157] | 56/0/46 | NA |
| unknown_rejection_rate | 0.284054 | 0.399126 | +0.115072 | [+0.060296, +0.169093] | 66/1/35 | NA |

Confirmation gate: **FAIL**.
