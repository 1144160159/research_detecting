# Strict-v4 current confirmed risk candidate

Status: **confirmed_for_full_matrix_evaluation**.
Risk selection: `nested_boundary_pairwise_pseudo_unknown_blend`.
Record SHA256: `1d65b57c43b0254c662ded463175aae3172b3c76b4339820c9d0f1e5944d4d56`.

| Metric | Reference | Candidate | Oriented gain | 95% CI |
|---|---:|---:|---:|---:|
| known_macro_f1 | 0.701935 | 0.701935 | +0.000000 | [+0.000000, +0.000000] |
| unknown_auroc | 0.799028 | 0.801085 | +0.002057 | [+0.000195, +0.004528] |
| unknown_aupr | 0.562558 | 0.565154 | +0.002596 | [-0.001045, +0.008179] |
| unknown_fpr95 | 0.518136 | 0.474451 | +0.043685 | [-0.002288, +0.105536] |
| oscr | 0.558342 | 0.565010 | +0.006668 | [+0.000749, +0.016647] |

This promotes the candidate to full strict-v4 evaluation only. It is not a seven-dataset SOTA claim.
