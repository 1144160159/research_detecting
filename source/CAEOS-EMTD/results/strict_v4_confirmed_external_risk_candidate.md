# Strict-v4 current confirmed external-risk candidate

Status: **confirmed_for_full_matrix_evaluation**.
Endpoint: `mlp/openmax` + `rank_union`.
Record SHA256: `82e22f3a8bc49b62f49bbb7003ed599efc71401bc0bdc754e4d4a4d9f36c7673`.

| Metric | Base CAEOS | Fused CAEOS | Oriented gain | 95% CI | Holm p |
|---|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.729267 | 0.729267 | +0.000000 | [+0.000000, +0.000000] | NA |
| unknown_auroc | 0.747864 | 0.766443 | +0.018579 | [+0.003594, +0.034816] | 0.125 |
| unknown_aupr | 0.499260 | 0.519460 | +0.020200 | [+0.007340, +0.033303] | 0.125 |
| unknown_fpr95 | 0.565273 | 0.503131 | +0.062142 | [+0.033212, +0.091649] | 0.125 |
| oscr | 0.550608 | 0.570219 | +0.019611 | [+0.009581, +0.031127] | 0.125 |

This record authorizes full strict-v4 evaluation only. It is not a seven-dataset SOTA or multiple-comparison significance claim.
