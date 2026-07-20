# Nested anchor/conflict gate summary

| Suite | Runs | New AUROC | Old AUROC | Delta | W/T/L | Selection accuracy | Regret |
|---|---:|---:|---:|---:|---:|---:|---:|
| nf_unsw | 18 | 0.714904 | 0.707812 | +0.007093 | 4/13/1 | 38.9% | 0.057633 |
| global | 18 | 0.714904 | 0.707812 | +0.007093 | 4/13/1 | 38.9% | 0.057633 |

Global Wilcoxon p-value: `0.138011`.

Direct gate mean AUROC: `0.714904`; hierarchical gate mean AUROC: `0.707812`.
Primary summary mode: `direct_gate`.

The old gate is reconstructed from the same run by applying the original nested rule to `support_union` and `cauchy_evidence`.
