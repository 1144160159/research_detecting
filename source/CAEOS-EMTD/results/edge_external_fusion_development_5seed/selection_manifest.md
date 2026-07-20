# Edge external-risk fusion development selection

Status: `frozen_unconfirmed`
Development seeds: `[7, 11, 19, 23, 37]`
Reserved confirmation seeds: `[67, 71, 73, 79]`

## Frozen candidate

- Expert risk: `relative_mahalanobis` from `mlp`
- Fusion: `rank_union`
- Screened candidates: 72

| Metric | Gate mean | Candidate mean | Oriented delta | W/T/L |
|---|---:|---:|---:|---:|
| unknown_auroc | 0.836580 | 0.848441 | +0.011860 | 40/0/30 |
| unknown_aupr | 0.733777 | 0.769269 | +0.035493 | 42/0/28 |
| unknown_fpr95 | 0.518204 | 0.467564 | +0.050640 | 37/0/33 |
| oscr | 0.764812 | 0.779525 | +0.014713 | 40/0/30 |
| known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | 0/70/0 |

This is development-only evidence. The candidate must not be promoted until the reserved confirmation seeds pass the frozen gate.
