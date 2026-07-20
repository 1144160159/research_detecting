# Nested anchor/conflict gate summary

| Suite | Runs | New AUROC | Baseline AUROC | Delta | W/T/L | Selection accuracy | Regret |
|---|---:|---:|---:|---:|---:|---:|---:|
| nf_unsw | 54 | 0.763173 | 0.747583 | +0.015589 | 12/41/1 | 46.3% | 0.032292 |
| global | 54 | 0.763173 | 0.747583 | +0.015589 | 12/41/1 | 46.3% | 0.032292 |

Global Wilcoxon p-value: `0.00170898`.

Direct gate mean AUROC: `0.763173`; hierarchical gate mean AUROC: `0.747583`.
Primary summary mode: `joint_gate_vs_hierarchical`.
Primary baseline: `v1.4.3 hierarchical gate`.

The original nested gate is reconstructed from the same run by applying the original rule to `support_union` and `cauchy_evidence`; the v1.4.3 hierarchical gate additionally replaces the support branch with `anchor_support`.

| Metric | New | Baseline | Oriented improvement |
|---|---:|---:|---:|
| unknown_aupr | 0.485895 | 0.469441 | +0.016455 |
| oscr | 0.702611 | 0.692317 | +0.010294 |
| unknown_fpr95 | 0.461441 | 0.466166 | +0.004725 |
| unknown_f1 | 0.195567 | 0.173797 | +0.021770 |
| known_acceptance_rate | 0.939636 | 0.938688 | +0.000948 |
| unknown_rejection_rate | 0.153468 | 0.136890 | +0.016578 |
