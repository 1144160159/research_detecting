# Nested anchor/conflict gate summary

| Suite | Runs | New AUROC | Baseline AUROC | Delta | W/T/L | Selection accuracy | Regret |
|---|---:|---:|---:|---:|---:|---:|---:|
| nf_unsw | 18 | 0.760056 | 0.744254 | +0.015802 | 3/15/0 | 44.4% | 0.037095 |
| global | 18 | 0.760056 | 0.744254 | +0.015802 | 3/15/0 | 44.4% | 0.037095 |

Global Wilcoxon p-value: `0.25`.

Direct gate mean AUROC: `0.760056`; hierarchical gate mean AUROC: `0.744254`.
Primary summary mode: `joint_gate_vs_hierarchical`.
Primary baseline: `v1.4.3 hierarchical gate`.

The original nested gate is reconstructed from the same run by applying the original rule to `support_union` and `cauchy_evidence`; the v1.4.3 hierarchical gate additionally replaces the support branch with `anchor_support`.
