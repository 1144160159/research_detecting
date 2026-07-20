# Edge external-risk fusion development selection

Status: `frozen_unconfirmed`
Development seeds: `[7]`
Reserved confirmation seeds: `[67, 71, 73, 79]`

## Frozen candidate

- Expert risk: `relative_mahalanobis` from `mlp`
- Fusion: `rank_cauchy`
- Screened candidates: 72

| Metric | Gate mean | Candidate mean | Oriented delta | W/T/L |
|---|---:|---:|---:|---:|
| unknown_auroc | 0.835634 | 0.862372 | +0.026738 | 10/0/4 |
| unknown_aupr | 0.759932 | 0.781650 | +0.021719 | 10/0/4 |
| unknown_fpr95 | 0.568136 | 0.422796 | +0.145341 | 10/0/4 |
| oscr | 0.722520 | 0.766627 | +0.044107 | 9/0/5 |
| known_macro_f1 | 0.907194 | 0.907194 | +0.000000 | 0/14/0 |

This is development-only evidence. The candidate must not be promoted until the reserved confirmation seeds pass the frozen gate.
