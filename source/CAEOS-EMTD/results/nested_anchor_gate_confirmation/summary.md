# Nested anchor/conflict gate summary

| Suite | Runs | New AUROC | Old AUROC | Delta | W/T/L | Selection accuracy | Regret |
|---|---:|---:|---:|---:|---:|---:|---:|
| doh | 15 | 0.885980 | 0.885980 | +0.000000 | 0/15/0 | 100.0% | 0.000000 |
| hikari | 20 | 0.874612 | 0.862999 | +0.011613 | 18/0/2 | 100.0% | 0.000000 |
| mal_tls | 30 | 0.992721 | 0.992721 | +0.000000 | 0/30/0 | 100.0% | 0.000000 |
| global | 65 | 0.931747 | 0.928174 | +0.003573 | 18/45/2 | 100.0% | 0.000000 |

Global Wilcoxon p-value: `0.00573399`.

Direct gate mean AUROC: `0.931561`; hierarchical gate mean AUROC: `0.931747`.

The old gate is reconstructed from the same run by applying the original nested rule to `support_union` and `cauchy_evidence`.
