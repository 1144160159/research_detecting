# Frozen candidate confirmation

Paired runs: 70; inference units: 14 scenarios.
Seed repeats are averaged within scenarios before inference.

| Metric | Reference | Candidate | Oriented improvement | 95% CI | W/T/L | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| unknown_auroc | 0.674764 | 0.836599 | +0.161835 | [+0.090939, +0.257611] | 13/0/1 | 0.0011 |
| unknown_aupr | 0.557569 | 0.733479 | +0.175910 | [+0.110820, +0.237334] | 13/0/1 | 0.00171 |
| unknown_fpr95 | 0.657188 | 0.517759 | +0.139429 | [+0.007872, +0.278289] | 9/0/5 | 0.135 |
| oscr | 0.609146 | 0.764639 | +0.155493 | [+0.099009, +0.227079] | 13/0/1 | 0.000977 |
| known_acceptance_rate | 0.941292 | 0.928227 | -0.013065 | [-0.024405, -0.003065] | 2/0/12 | NA |
| unknown_rejection_rate | 0.256571 | 0.517014 | +0.260443 | [+0.160671, +0.364515] | 14/0/0 | NA |

## Decision

Mean safety gate: **PASS**
Confirmatory evidence: **PASS**

The confirmatory gate requires positive AUROC, non-regressing AUPR/OSCR, FPR95 raw regression no greater than 0.01, a positive AUROC bootstrap lower bound, and Holm-adjusted AUROC p < 0.05.
