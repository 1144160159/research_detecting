# Paired CAEOS candidate comparison

| Scope | Runs | Reference AUROC | Candidate AUROC | Delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| hikari | 12 | 0.890776 | 0.897038 | +0.006262 | 6/0/6 | 0.791 |
| global | 12 | 0.890776 | 0.897038 | +0.006262 | 6/0/6 | 0.791 |

## Secondary metrics

| Metric | Reference | Candidate | Oriented improvement | W/T/L |
|---|---:|---:|---:|---:|
| known_macro_f1 | 0.974263 | 0.974263 | +0.000000 | 0/12/0 |
| unknown_auroc | 0.890776 | 0.897038 | +0.006262 | 6/0/6 |
| unknown_aupr | 0.889497 | 0.892158 | +0.002661 | 6/0/6 |
| unknown_fpr95 | 0.178453 | 0.173690 | +0.004763 | 5/0/7 |
| oscr | 0.859763 | 0.849874 | -0.009889 | 6/0/6 |
| known_acceptance_rate | 0.947053 | 0.948946 | +0.001893 | 8/1/3 |
| unknown_rejection_rate | 0.356115 | 0.485409 | +0.129294 | 5/4/3 |
