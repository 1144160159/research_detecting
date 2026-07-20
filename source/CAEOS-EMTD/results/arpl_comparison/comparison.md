# Neural open-set baseline comparison

## hikari

Runs: 12

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.880130 | 0.079239 | 0.722453 | - | - | - |
| arpl | 0.347597 | 0.278119 | 0.050995 | +0.532533 | 12/0/0 | 0.000488 |

Test-label oracle neural upper bound: 0.347597; this is diagnostic only and is not a deployable baseline.

## doh

Runs: 9

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.867093 | 0.059342 | 0.783586 | - | - | - |
| arpl | 0.727201 | 0.121650 | 0.460988 | +0.139891 | 7/0/2 | 0.0273 |

Test-label oracle neural upper bound: 0.727201; this is diagnostic only and is not a deployable baseline.

## mal_tls

Runs: 18

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.993660 | 0.003404 | 0.986872 | - | - | - |
| arpl | 0.963045 | 0.034442 | 0.877892 | +0.030615 | 17/0/1 | 1.53e-05 |

Test-label oracle neural upper bound: 0.963045; this is diagnostic only and is not a deployable baseline.
