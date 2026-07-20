# Paired CAEOS candidate comparison

| Scope | Runs | Reference AUROC | Candidate AUROC | Delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| hikari | 12 | 0.890776 | 0.884720 | -0.006056 | 1/8/3 | 0.375 |
| global | 12 | 0.890776 | 0.884720 | -0.006056 | 1/8/3 | 0.375 |

## Secondary metrics

| Metric | Reference | Candidate | Oriented improvement | W/T/L |
|---|---:|---:|---:|---:|
| known_macro_f1 | 0.974263 | 0.974263 | +0.000000 | 0/12/0 |
| unknown_auroc | 0.890776 | 0.884720 | -0.006056 | 1/8/3 |
| unknown_aupr | 0.889497 | 0.884721 | -0.004776 | 1/8/3 |
| unknown_fpr95 | 0.178453 | 0.181952 | -0.003499 | 0/9/3 |
| oscr | 0.859763 | 0.854489 | -0.005274 | 2/8/2 |
| known_acceptance_rate | 0.947053 | 0.947262 | +0.000210 | 3/8/1 |
| unknown_rejection_rate | 0.356115 | 0.361180 | +0.005066 | 1/10/1 |
