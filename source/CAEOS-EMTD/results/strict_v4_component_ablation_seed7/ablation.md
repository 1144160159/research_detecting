# Strict-v4 seed7 component ablation

Development-only descriptive evidence. It cannot select or modify the final algorithm.

Reference: `cauchy_modality_support_union`.

| Comparison | Known F1 gain | AUROC gain | AUPR gain | FPR95 reduction | OSCR gain | Four-metric mean |
|---|---:|---:|---:|---:|---:|---:|
| baseline | +0.000000 | -0.002177 | -0.003727 | -0.098905 | -0.034621 | -0.034857 |
| cauchy_evidence | +0.000000 | +0.011751 | +0.032342 | -0.086652 | -0.038016 | -0.020144 |
| modality_support_union | +0.000000 | +0.071824 | +0.062404 | +0.128297 | +0.097412 | +0.089984 |
| cauchy_modality_support | +0.000000 | +0.100251 | +0.097612 | +0.068948 | +0.069791 | +0.084150 |
| support_union | +0.000000 | +0.070747 | +0.067738 | +0.031774 | +0.079086 | +0.062336 |
| max_modality_knn | +0.000000 | +0.081910 | +0.082403 | +0.041036 | +0.058706 | +0.066014 |
| selected_pairwise_endpoint | +0.000000 | -0.003533 | -0.003147 | -0.015033 | -0.008681 | -0.007598 |

Positive values favor the fixed reference. The selected Pairwise endpoint is shown separately and is not a component ablation.

Selected risks: `{"cauchy_modality_support_union": 88, "pseudo_unknown_learned_blend": 14}`.
