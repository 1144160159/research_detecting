# Strict-v2 Edge component ablation

Validated runs: 70; inference units: 14 scenarios; seeds: [7, 11, 19, 23, 37].
Seed repeats are averaged within each scenario before inference.
Holm family: 24 hypotheses across all ablations and unknown-detection metrics.

| Ablation | Metric | Ablation | Final | Oriented improvement | 95% CI | W/T/L | Holm p |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| baseline | unknown_auroc | 0.847499 | 0.836599 | -0.010900 | [-0.078581, +0.073034] | 4/0/10 | 1.000000 |
| baseline | unknown_aupr | 0.766263 | 0.733479 | -0.032784 | [-0.118437, +0.069858] | 4/0/10 | 1.000000 |
| baseline | unknown_fpr95 | 0.442058 | 0.517759 | -0.075702 | [-0.243097, +0.120308] | 5/0/9 | 1.000000 |
| baseline | oscr | 0.781629 | 0.764639 | -0.016991 | [-0.082209, +0.058314] | 4/0/10 | 1.000000 |
| cauchy_evidence | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_evidence | unknown_auroc | 0.828249 | 0.836599 | +0.008349 | [-0.074881, +0.135298] | 3/0/11 | 1.000000 |
| cauchy_evidence | unknown_aupr | 0.757788 | 0.733479 | -0.024309 | [-0.097446, +0.066789] | 3/0/11 | 1.000000 |
| cauchy_evidence | unknown_fpr95 | 0.394670 | 0.517759 | -0.123089 | [-0.288924, +0.062194] | 3/0/11 | 1.000000 |
| cauchy_evidence | oscr | 0.769714 | 0.764639 | -0.005076 | [-0.075524, +0.094705] | 3/0/11 | 1.000000 |
| modality_support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| modality_support_union | unknown_auroc | 0.611416 | 0.836599 | +0.225183 | [+0.140330, +0.308946] | 12/0/2 | 0.012817 |
| modality_support_union | unknown_aupr | 0.505638 | 0.733479 | +0.227841 | [+0.132851, +0.310696] | 12/0/2 | 0.014648 |
| modality_support_union | unknown_fpr95 | 0.900582 | 0.517759 | +0.382823 | [+0.240558, +0.523167] | 11/2/1 | 0.012817 |
| modality_support_union | oscr | 0.463735 | 0.764639 | +0.300904 | [+0.203496, +0.402925] | 13/0/1 | 0.005127 |
| cauchy_modality_support | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_modality_support | unknown_auroc | 0.604506 | 0.836599 | +0.232093 | [+0.164552, +0.300554] | 13/0/1 | 0.005127 |
| cauchy_modality_support | unknown_aupr | 0.482740 | 0.733479 | +0.250739 | [+0.196354, +0.301164] | 14/0/0 | 0.002930 |
| cauchy_modality_support | unknown_fpr95 | 0.769932 | 0.517759 | +0.252173 | [+0.109518, +0.400181] | 11/1/2 | 0.061035 |
| cauchy_modality_support | oscr | 0.549978 | 0.764639 | +0.214661 | [+0.156921, +0.277312] | 14/0/0 | 0.002930 |
| support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| support_union | unknown_auroc | 0.664119 | 0.836599 | +0.172480 | [+0.109016, +0.234195] | 12/0/2 | 0.010376 |
| support_union | unknown_aupr | 0.519250 | 0.733479 | +0.214229 | [+0.141990, +0.283321] | 12/0/2 | 0.010376 |
| support_union | unknown_fpr95 | 0.752212 | 0.517759 | +0.234453 | [+0.105181, +0.370340] | 9/1/4 | 0.094482 |
| support_union | oscr | 0.570039 | 0.764639 | +0.194599 | [+0.129622, +0.266560] | 13/0/1 | 0.005127 |
| max_modality_knn | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| max_modality_knn | unknown_auroc | 0.629381 | 0.836599 | +0.207217 | [+0.144387, +0.274685] | 13/0/1 | 0.005127 |
| max_modality_knn | unknown_aupr | 0.520272 | 0.733479 | +0.213207 | [+0.137360, +0.281461] | 13/0/1 | 0.012817 |
| max_modality_knn | unknown_fpr95 | 0.766698 | 0.517759 | +0.248939 | [+0.115841, +0.396568] | 12/1/1 | 0.037598 |
| max_modality_knn | oscr | 0.565693 | 0.764639 | +0.198945 | [+0.141890, +0.261807] | 14/0/0 | 0.002930 |

## Component decisions

- `baseline`: final directionally better on 0/4 unknown metrics; Holm-confirmed: none.
- `cauchy_evidence`: final directionally better on 1/4 unknown metrics; Holm-confirmed: none.
- `modality_support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, unknown_fpr95, oscr.
- `cauchy_modality_support`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `max_modality_knn`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, unknown_fpr95, oscr.
