# Strict-v2 SOTA decision

Mean rank and confirmatory significance are reported separately.

## global

Scenarios: 14; baselines: 20

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.836599 | 1/21 | mahalanobis | 0.729741 | +0.106857 | [+0.034595, +0.187895] | 0.362549 | false |
| unknown_aupr | 0.733479 | 1/21 | knn | 0.637477 | +0.096002 | [-0.010900, +0.211567] | 1 | false |
| unknown_fpr95 | 0.517759 | 1/21 | mahalanobis | 0.602022 | +0.084262 | [-0.060982, +0.247764] | 1 | false |
| oscr | 0.764639 | 1/21 | opendetect | 0.603558 | +0.161081 | [+0.083880, +0.243020] | 0.109863 | false |
| known_macro_f1 | 0.927941 | 1/21 | opendetect | 0.852150 | +0.075790 | [+0.069245, +0.082250] | 0.012207 | true |

All primary means rank first: `True`
All strongest comparisons confirmed: `False`

## edge_iiot

Scenarios: 14; baselines: 20

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.836599 | 1/21 | mahalanobis | 0.729741 | +0.106857 | [+0.033849, +0.187518] | 0.362549 | false |
| unknown_aupr | 0.733479 | 1/21 | knn | 0.637477 | +0.096002 | [-0.012706, +0.210767] | 1 | false |
| unknown_fpr95 | 0.517759 | 1/21 | mahalanobis | 0.602022 | +0.084262 | [-0.060141, +0.245688] | 1 | false |
| oscr | 0.764639 | 1/21 | opendetect | 0.603558 | +0.161081 | [+0.084277, +0.244179] | 0.109863 | false |
| known_macro_f1 | 0.927941 | 1/21 | opendetect | 0.852150 | +0.075790 | [+0.069032, +0.082049] | 0.012207 | true |

All primary means rank first: `True`
All strongest comparisons confirmed: `False`
