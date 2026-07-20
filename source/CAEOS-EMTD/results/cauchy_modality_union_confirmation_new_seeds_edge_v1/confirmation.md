# Frozen candidate confirmation

Paired runs: 56; inference units: 14 scenarios.
Seed repeats are averaged within scenarios before inference.

| Metric | Reference | Candidate | Oriented improvement | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.919206 | 0.919206 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| unknown_auroc | 0.625018 | 0.818679 | +0.193661 | [+0.106070, +0.299162] | 13/0/1 | 0.00146 |
| unknown_aupr | 0.500257 | 0.700913 | +0.200656 | [+0.124495, +0.274074] | 12/0/2 | 0.00146 |
| unknown_fpr95 | 0.726481 | 0.522144 | +0.204337 | [+0.083734, +0.328108] | 12/0/2 | 0.0107 |
| oscr | 0.548415 | 0.749511 | +0.201096 | [+0.128665, +0.282845] | 13/0/1 | 0.00146 |
| known_acceptance_rate | 0.952079 | 0.911775 | -0.040304 | [-0.058269, -0.023680] | 0/0/14 | NA |
| unknown_rejection_rate | 0.171696 | 0.467625 | +0.295929 | [+0.187463, +0.397823] | 13/0/1 | NA |

## Decision

Mean safety gate: **PASS**
Confirmatory evidence: **PASS**

The confirmatory gate requires positive AUROC, non-regressing AUPR/OSCR, FPR95 raw regression no greater than 0.01, a positive AUROC bootstrap lower bound, and Holm-adjusted AUROC p < 0.05.
