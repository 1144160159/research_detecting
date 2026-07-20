# Paired CAEOS candidate comparison

| Scope | Runs | Reference AUROC | Candidate AUROC | Delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| edge_iiot | 14 | 0.647653 | 0.836155 | +0.188502 | 12/0/2 | 0.000854 |
| global | 14 | 0.647653 | 0.836155 | +0.188502 | 12/0/2 | 0.000854 |

## Secondary metrics

| Metric | Reference | Candidate | Oriented improvement | W/T/L |
|---|---:|---:|---:|---:|
| known_macro_f1 | 0.907194 | 0.907194 | +0.000000 | 0/14/0 |
| unknown_auroc | 0.647653 | 0.836155 | +0.188502 | 12/0/2 |
| unknown_aupr | 0.527245 | 0.759121 | +0.231876 | 13/0/1 |
| unknown_fpr95 | 0.717547 | 0.567925 | +0.149622 | 8/1/5 |
| oscr | 0.571895 | 0.723399 | +0.151504 | 11/0/3 |
| known_acceptance_rate | 0.935082 | 0.935975 | +0.000893 | 8/0/6 |
| unknown_rejection_rate | 0.222000 | 0.550857 | +0.328857 | 13/1/0 |
