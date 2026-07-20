# Paired CAEOS candidate comparison

| Scope | Runs | Reference AUROC | Candidate AUROC | Delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| hikari | 12 | 0.890776 | 0.893559 | +0.002782 | 8/0/4 | 0.424 |
| global | 12 | 0.890776 | 0.893559 | +0.002782 | 8/0/4 | 0.424 |

## Secondary metrics

| Metric | Reference | Candidate | Oriented improvement | W/T/L |
|---|---:|---:|---:|---:|
| known_macro_f1 | 0.974263 | 0.974612 | +0.000349 | 5/3/4 |
| unknown_auroc | 0.890776 | 0.893559 | +0.002782 | 8/0/4 |
| unknown_aupr | 0.889497 | 0.893554 | +0.004056 | 7/0/5 |
| unknown_fpr95 | 0.178453 | 0.178662 | -0.000209 | 6/1/5 |
| oscr | 0.859763 | 0.854652 | -0.005111 | 8/0/4 |
| known_acceptance_rate | 0.947053 | 0.940493 | -0.006560 | 6/0/6 |
| unknown_rejection_rate | 0.356115 | 0.387756 | +0.031641 | 7/3/2 |
