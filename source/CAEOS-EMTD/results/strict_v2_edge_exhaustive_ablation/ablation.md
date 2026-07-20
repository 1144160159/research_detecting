# Strict-v2 Edge component ablation

Validated runs: 70; inference units: 14 scenarios; seeds: [7, 11, 19, 23, 37].
Seed repeats are averaged within each scenario before inference.
Holm family: 172 hypotheses across all ablations and unknown-detection metrics.

| Ablation | Metric | Ablation | Final | Oriented improvement | 95% CI | W/T/L | Holm p |
|---|---|---:|---:|---:|---:|---:|---:|
| anchor_support | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| anchor_support | unknown_auroc | 0.656547 | 0.836599 | +0.180052 | [+0.117052, +0.246208] | 13/0/1 | 0.034424 |
| anchor_support | unknown_aupr | 0.514600 | 0.733479 | +0.218880 | [+0.148538, +0.280574] | 13/0/1 | 0.043213 |
| anchor_support | unknown_fpr95 | 0.686669 | 0.517759 | +0.168910 | [+0.035054, +0.315161] | 8/1/5 | 1.000000 |
| anchor_support | oscr | 0.581989 | 0.764639 | +0.182650 | [+0.124107, +0.249722] | 13/0/1 | 0.034424 |
| baseline | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| baseline | unknown_auroc | 0.847499 | 0.836599 | -0.010900 | [-0.078581, +0.073034] | 4/0/10 | 1.000000 |
| baseline | unknown_aupr | 0.766263 | 0.733479 | -0.032784 | [-0.118437, +0.069858] | 4/0/10 | 1.000000 |
| baseline | unknown_fpr95 | 0.442058 | 0.517759 | -0.075702 | [-0.243097, +0.120308] | 5/0/9 | 1.000000 |
| baseline | oscr | 0.781629 | 0.764639 | -0.016991 | [-0.082209, +0.058314] | 4/0/10 | 1.000000 |
| cauchy_all | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_all | unknown_auroc | 0.860233 | 0.836599 | -0.023635 | [-0.098029, +0.082311] | 2/0/12 | 1.000000 |
| cauchy_all | unknown_aupr | 0.798534 | 0.733479 | -0.065055 | [-0.159709, +0.048124] | 3/0/11 | 1.000000 |
| cauchy_all | unknown_fpr95 | 0.354302 | 0.517759 | -0.163458 | [-0.326337, +0.022595] | 2/0/12 | 1.000000 |
| cauchy_all | oscr | 0.791412 | 0.764639 | -0.026774 | [-0.100863, +0.068158] | 3/0/11 | 1.000000 |
| cauchy_baseline | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_baseline | unknown_auroc | 0.848261 | 0.836599 | -0.011662 | [-0.081630, +0.069618] | 4/0/10 | 1.000000 |
| cauchy_baseline | unknown_aupr | 0.796115 | 0.733479 | -0.062636 | [-0.148153, +0.032550] | 4/0/10 | 1.000000 |
| cauchy_baseline | unknown_fpr95 | 0.425504 | 0.517759 | -0.092256 | [-0.241970, +0.082055] | 4/0/10 | 1.000000 |
| cauchy_baseline | oscr | 0.781333 | 0.764639 | -0.016695 | [-0.082382, +0.057091] | 4/0/10 | 1.000000 |
| cauchy_bidirectional | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_bidirectional | unknown_auroc | 0.836089 | 0.836599 | +0.000510 | [-0.073494, +0.099386] | 4/0/10 | 1.000000 |
| cauchy_bidirectional | unknown_aupr | 0.783544 | 0.733479 | -0.050065 | [-0.133741, +0.045776] | 4/0/10 | 1.000000 |
| cauchy_bidirectional | unknown_fpr95 | 0.455265 | 0.517759 | -0.062494 | [-0.222689, +0.112728] | 6/0/8 | 1.000000 |
| cauchy_bidirectional | oscr | 0.771851 | 0.764639 | -0.007212 | [-0.078955, +0.083654] | 4/0/10 | 1.000000 |
| cauchy_bidirectional_evidence | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_bidirectional_evidence | unknown_auroc | 0.799582 | 0.836599 | +0.037017 | [-0.049860, +0.162728] | 5/0/9 | 1.000000 |
| cauchy_bidirectional_evidence | unknown_aupr | 0.744061 | 0.733479 | -0.010582 | [-0.081890, +0.078919] | 5/0/9 | 1.000000 |
| cauchy_bidirectional_evidence | unknown_fpr95 | 0.475565 | 0.517759 | -0.042194 | [-0.194965, +0.133993] | 6/0/8 | 1.000000 |
| cauchy_bidirectional_evidence | oscr | 0.741459 | 0.764639 | +0.023180 | [-0.058558, +0.141127] | 5/0/9 | 1.000000 |
| cauchy_bidirectional_support | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_bidirectional_support | unknown_auroc | 0.833880 | 0.836599 | +0.002719 | [-0.070601, +0.101326] | 4/0/10 | 1.000000 |
| cauchy_bidirectional_support | unknown_aupr | 0.788404 | 0.733479 | -0.054925 | [-0.132374, +0.038460] | 4/0/10 | 1.000000 |
| cauchy_bidirectional_support | unknown_fpr95 | 0.476429 | 0.517759 | -0.041330 | [-0.207258, +0.143094] | 6/0/8 | 1.000000 |
| cauchy_bidirectional_support | oscr | 0.769682 | 0.764639 | -0.005044 | [-0.076406, +0.086965] | 4/0/10 | 1.000000 |
| cauchy_conflict | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_conflict | unknown_auroc | 0.827551 | 0.836599 | +0.009048 | [-0.064738, +0.100109] | 4/0/10 | 1.000000 |
| cauchy_conflict | unknown_aupr | 0.773614 | 0.733479 | -0.040135 | [-0.126422, +0.057459] | 4/0/10 | 1.000000 |
| cauchy_conflict | unknown_fpr95 | 0.454209 | 0.517759 | -0.063550 | [-0.204586, +0.100430] | 4/0/10 | 1.000000 |
| cauchy_conflict | oscr | 0.760306 | 0.764639 | +0.004332 | [-0.066735, +0.087532] | 4/0/10 | 1.000000 |
| cauchy_distance_class_knn | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_distance_class_knn | unknown_auroc | 0.667349 | 0.836599 | +0.169250 | [+0.101421, +0.237724] | 12/0/2 | 0.118408 |
| cauchy_distance_class_knn | unknown_aupr | 0.526047 | 0.733479 | +0.207433 | [+0.131111, +0.276978] | 12/0/2 | 0.088867 |
| cauchy_distance_class_knn | unknown_fpr95 | 0.675407 | 0.517759 | +0.157648 | [+0.013192, +0.312467] | 7/0/7 | 1.000000 |
| cauchy_distance_class_knn | oscr | 0.594845 | 0.764639 | +0.169793 | [+0.115569, +0.227341] | 14/0/0 | 0.020996 |
| cauchy_distance_knn | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_distance_knn | unknown_auroc | 0.631503 | 0.836599 | +0.205096 | [+0.144380, +0.264252] | 13/0/1 | 0.034424 |
| cauchy_distance_knn | unknown_aupr | 0.505165 | 0.733479 | +0.228314 | [+0.164401, +0.284754] | 13/0/1 | 0.034424 |
| cauchy_distance_knn | unknown_fpr95 | 0.720719 | 0.517759 | +0.202960 | [+0.055164, +0.362311] | 8/0/6 | 1.000000 |
| cauchy_distance_knn | oscr | 0.570047 | 0.764639 | +0.194592 | [+0.141776, +0.248885] | 13/0/1 | 0.034424 |
| cauchy_distance_lof | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_distance_lof | unknown_auroc | 0.719946 | 0.836599 | +0.116652 | [+0.070464, +0.164369] | 11/0/3 | 0.158936 |
| cauchy_distance_lof | unknown_aupr | 0.585466 | 0.733479 | +0.148013 | [+0.062167, +0.234462] | 10/0/4 | 1.000000 |
| cauchy_distance_lof | unknown_fpr95 | 0.759591 | 0.517759 | +0.241832 | [+0.112847, +0.378368] | 11/0/3 | 0.581055 |
| cauchy_distance_lof | oscr | 0.648595 | 0.764639 | +0.116043 | [+0.078799, +0.155636] | 13/0/1 | 0.034424 |
| cauchy_evidence | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_evidence | unknown_auroc | 0.828249 | 0.836599 | +0.008349 | [-0.074881, +0.135298] | 3/0/11 | 1.000000 |
| cauchy_evidence | unknown_aupr | 0.757788 | 0.733479 | -0.024309 | [-0.097446, +0.066789] | 3/0/11 | 1.000000 |
| cauchy_evidence | unknown_fpr95 | 0.394670 | 0.517759 | -0.123089 | [-0.288924, +0.062194] | 3/0/11 | 1.000000 |
| cauchy_evidence | oscr | 0.769714 | 0.764639 | -0.005076 | [-0.075524, +0.094705] | 3/0/11 | 1.000000 |
| cauchy_local_support | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_local_support | unknown_auroc | 0.659889 | 0.836599 | +0.176709 | [+0.109442, +0.245459] | 14/0/0 | 0.020996 |
| cauchy_local_support | unknown_aupr | 0.507812 | 0.733479 | +0.225667 | [+0.173166, +0.278835] | 14/0/0 | 0.020996 |
| cauchy_local_support | unknown_fpr95 | 0.673190 | 0.517759 | +0.155431 | [-0.017954, +0.329102] | 8/0/6 | 1.000000 |
| cauchy_local_support | oscr | 0.617763 | 0.764639 | +0.146876 | [+0.089494, +0.207169] | 13/0/1 | 0.034424 |
| cauchy_modality_knn | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_modality_knn | unknown_auroc | 0.625639 | 0.836599 | +0.210960 | [+0.148991, +0.276381] | 13/0/1 | 0.034424 |
| cauchy_modality_knn | unknown_aupr | 0.498818 | 0.733479 | +0.234661 | [+0.175643, +0.289756] | 14/0/0 | 0.020996 |
| cauchy_modality_knn | unknown_fpr95 | 0.766698 | 0.517759 | +0.248939 | [+0.113931, +0.391643] | 12/1/1 | 0.280273 |
| cauchy_modality_knn | oscr | 0.563493 | 0.764639 | +0.201146 | [+0.146933, +0.263649] | 14/0/0 | 0.020996 |
| cauchy_modality_support | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| cauchy_modality_support | unknown_auroc | 0.604506 | 0.836599 | +0.232093 | [+0.164552, +0.300554] | 13/0/1 | 0.034424 |
| cauchy_modality_support | unknown_aupr | 0.482740 | 0.733479 | +0.250739 | [+0.196354, +0.301164] | 14/0/0 | 0.020996 |
| cauchy_modality_support | unknown_fpr95 | 0.769932 | 0.517759 | +0.252173 | [+0.109518, +0.400181] | 11/1/2 | 0.457764 |
| cauchy_modality_support | oscr | 0.549978 | 0.764639 | +0.214661 | [+0.156921, +0.277312] | 14/0/0 | 0.020996 |
| class_knn_distance | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| class_knn_distance | unknown_auroc | 0.733834 | 0.836599 | +0.102765 | [+0.048623, +0.162627] | 12/0/2 | 0.211060 |
| class_knn_distance | unknown_aupr | 0.600076 | 0.733479 | +0.133403 | [+0.066957, +0.202812] | 11/0/3 | 0.314209 |
| class_knn_distance | unknown_fpr95 | 0.656696 | 0.517759 | +0.138937 | [-0.005333, +0.300584] | 8/0/6 | 1.000000 |
| class_knn_distance | oscr | 0.647742 | 0.764639 | +0.116897 | [+0.068048, +0.170987] | 13/0/1 | 0.066528 |
| class_support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| class_support_union | unknown_auroc | 0.690143 | 0.836599 | +0.146455 | [+0.083298, +0.216112] | 12/0/2 | 0.118408 |
| class_support_union | unknown_aupr | 0.546636 | 0.733479 | +0.186843 | [+0.114810, +0.253237] | 13/0/1 | 0.118408 |
| class_support_union | unknown_fpr95 | 0.726485 | 0.517759 | +0.208725 | [+0.082302, +0.339372] | 11/1/2 | 0.555908 |
| class_support_union | oscr | 0.596795 | 0.764639 | +0.167843 | [+0.115401, +0.227363] | 14/0/0 | 0.020996 |
| conflict | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| conflict | unknown_auroc | 0.329522 | 0.836599 | +0.507077 | [+0.450957, +0.565045] | 14/0/0 | 0.020996 |
| conflict | unknown_aupr | 0.302706 | 0.733479 | +0.430773 | [+0.379435, +0.485563] | 14/0/0 | 0.020996 |
| conflict | unknown_fpr95 | 0.834319 | 0.517759 | +0.316560 | [+0.170869, +0.460146] | 12/0/2 | 0.211060 |
| conflict | oscr | 0.294619 | 0.764639 | +0.470019 | [+0.415138, +0.523473] | 14/0/0 | 0.020996 |
| conflict_augmented | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| conflict_augmented | unknown_auroc | 0.843470 | 0.836599 | -0.006871 | [-0.077922, +0.079960] | 4/0/10 | 1.000000 |
| conflict_augmented | unknown_aupr | 0.765577 | 0.733479 | -0.032097 | [-0.121348, +0.072652] | 4/0/10 | 1.000000 |
| conflict_augmented | unknown_fpr95 | 0.449782 | 0.517759 | -0.067977 | [-0.239714, +0.131661] | 4/0/10 | 1.000000 |
| conflict_augmented | oscr | 0.778918 | 0.764639 | -0.014279 | [-0.081602, +0.063978] | 4/0/10 | 1.000000 |
| conflict_support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| conflict_support_union | unknown_auroc | 0.770415 | 0.836599 | +0.066184 | [+0.042261, +0.095448] | 14/0/0 | 0.020996 |
| conflict_support_union | unknown_aupr | 0.662729 | 0.733479 | +0.070751 | [+0.058128, +0.083187] | 14/0/0 | 0.020996 |
| conflict_support_union | unknown_fpr95 | 0.760423 | 0.517759 | +0.242664 | [+0.153724, +0.328095] | 12/2/0 | 0.056152 |
| conflict_support_union | oscr | 0.676206 | 0.764639 | +0.088433 | [+0.049504, +0.136713] | 14/0/0 | 0.020996 |
| density_support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| density_support_union | unknown_auroc | 0.707906 | 0.836599 | +0.128693 | [+0.074703, +0.182357] | 11/0/3 | 0.158936 |
| density_support_union | unknown_aupr | 0.576792 | 0.733479 | +0.156687 | [+0.068544, +0.244238] | 10/0/4 | 0.872803 |
| density_support_union | unknown_fpr95 | 0.854855 | 0.517759 | +0.337095 | [+0.204787, +0.463958] | 12/2/0 | 0.056152 |
| density_support_union | oscr | 0.626377 | 0.764639 | +0.138261 | [+0.091216, +0.186482] | 13/0/1 | 0.034424 |
| disagreement_augmented | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| disagreement_augmented | unknown_auroc | 0.861774 | 0.836599 | -0.025175 | [-0.094479, +0.061206] | 3/0/11 | 1.000000 |
| disagreement_augmented | unknown_aupr | 0.808472 | 0.733479 | -0.074993 | [-0.162843, +0.032613] | 3/0/11 | 1.000000 |
| disagreement_augmented | unknown_fpr95 | 0.418963 | 0.517759 | -0.098797 | [-0.269717, +0.101670] | 3/0/11 | 1.000000 |
| disagreement_augmented | oscr | 0.795818 | 0.764639 | -0.031179 | [-0.095241, +0.047316] | 3/0/11 | 1.000000 |
| distance | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| distance | unknown_auroc | 0.551676 | 0.836599 | +0.284923 | [+0.208441, +0.364172] | 13/0/1 | 0.034424 |
| distance | unknown_aupr | 0.431303 | 0.733479 | +0.302176 | [+0.223272, +0.380444] | 13/0/1 | 0.034424 |
| distance | unknown_fpr95 | 0.789500 | 0.517759 | +0.271741 | [+0.128642, +0.417164] | 11/0/3 | 0.496826 |
| distance | oscr | 0.497033 | 0.764639 | +0.267606 | [+0.198881, +0.338685] | 14/0/0 | 0.020996 |
| dual_knn_support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| dual_knn_support_union | unknown_auroc | 0.710505 | 0.836599 | +0.126094 | [+0.066699, +0.190740] | 11/0/3 | 0.211060 |
| dual_knn_support_union | unknown_aupr | 0.566338 | 0.733479 | +0.167141 | [+0.094064, +0.238772] | 11/0/3 | 0.211060 |
| dual_knn_support_union | unknown_fpr95 | 0.788257 | 0.517759 | +0.270498 | [+0.139955, +0.405465] | 9/2/3 | 0.496826 |
| dual_knn_support_union | oscr | 0.592740 | 0.764639 | +0.171899 | [+0.114536, +0.237017] | 14/0/0 | 0.020996 |
| entropy | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| entropy | unknown_auroc | 0.871214 | 0.836599 | -0.034615 | [-0.110230, +0.076788] | 2/0/12 | 1.000000 |
| entropy | unknown_aupr | 0.816901 | 0.733479 | -0.083422 | [-0.177900, +0.022569] | 4/0/10 | 1.000000 |
| entropy | unknown_fpr95 | 0.375336 | 0.517759 | -0.142424 | [-0.329732, +0.066435] | 4/0/10 | 1.000000 |
| entropy | oscr | 0.811938 | 0.764639 | -0.047299 | [-0.118255, +0.051763] | 2/0/12 | 1.000000 |
| foss_partition | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| foss_partition | unknown_auroc | 0.511168 | 0.836599 | +0.325431 | [+0.262007, +0.387619] | 14/0/0 | 0.020996 |
| foss_partition | unknown_aupr | 0.397091 | 0.733479 | +0.336389 | [+0.269849, +0.393123] | 14/0/0 | 0.020996 |
| foss_partition | unknown_fpr95 | 0.897672 | 0.517759 | +0.379912 | [+0.249390, +0.508480] | 12/2/0 | 0.056152 |
| foss_partition | oscr | 0.331879 | 0.764639 | +0.432760 | [+0.349534, +0.512805] | 14/0/0 | 0.020996 |
| knn_distance | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| knn_distance | unknown_auroc | 0.668328 | 0.836599 | +0.168270 | [+0.109546, +0.231580] | 13/0/1 | 0.034424 |
| knn_distance | unknown_aupr | 0.534263 | 0.733479 | +0.199216 | [+0.135501, +0.255402] | 13/0/1 | 0.043213 |
| knn_distance | unknown_fpr95 | 0.723325 | 0.517759 | +0.205566 | [+0.054685, +0.367972] | 9/1/4 | 1.000000 |
| knn_distance | oscr | 0.594615 | 0.764639 | +0.170024 | [+0.118014, +0.226644] | 14/0/0 | 0.020996 |
| knn_view_0 | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| knn_view_0 | unknown_auroc | 0.500612 | 0.836599 | +0.335987 | [+0.271277, +0.391190] | 14/0/0 | 0.020996 |
| knn_view_0 | unknown_aupr | 0.386422 | 0.733479 | +0.347057 | [+0.264346, +0.423486] | 13/0/1 | 0.034424 |
| knn_view_0 | unknown_fpr95 | 1.000000 | 0.517759 | +0.482241 | [+0.332625, +0.626680] | 12/2/0 | 0.056152 |
| knn_view_0 | oscr | 0.077956 | 0.764639 | +0.686682 | [+0.590633, +0.766059] | 14/0/0 | 0.020996 |
| knn_view_1 | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| knn_view_1 | unknown_auroc | 0.618546 | 0.836599 | +0.218053 | [+0.114700, +0.344173] | 13/0/1 | 0.066528 |
| knn_view_1 | unknown_aupr | 0.512031 | 0.733479 | +0.221448 | [+0.137787, +0.299858] | 13/0/1 | 0.088867 |
| knn_view_1 | unknown_fpr95 | 0.779333 | 0.517759 | +0.261574 | [+0.083890, +0.455008] | 9/1/4 | 1.000000 |
| knn_view_1 | oscr | 0.541257 | 0.764639 | +0.223381 | [+0.122955, +0.346500] | 13/0/1 | 0.034424 |
| knn_view_2 | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| knn_view_2 | unknown_auroc | 0.514118 | 0.836599 | +0.322480 | [+0.281737, +0.362102] | 14/0/0 | 0.020996 |
| knn_view_2 | unknown_aupr | 0.373930 | 0.733479 | +0.359549 | [+0.317091, +0.406822] | 14/0/0 | 0.020996 |
| knn_view_2 | unknown_fpr95 | 1.000000 | 0.517759 | +0.482241 | [+0.337690, +0.627514] | 12/2/0 | 0.056152 |
| knn_view_2 | oscr | 0.063784 | 0.764639 | +0.700855 | [+0.624544, +0.762684] | 14/0/0 | 0.020996 |
| lof_density | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| lof_density | unknown_auroc | 0.707764 | 0.836599 | +0.128835 | [+0.066967, +0.190539] | 11/0/3 | 0.256348 |
| lof_density | unknown_aupr | 0.586166 | 0.733479 | +0.147313 | [+0.063767, +0.235304] | 10/0/4 | 1.000000 |
| lof_density | unknown_fpr95 | 0.780619 | 0.517759 | +0.262859 | [+0.109754, +0.420610] | 11/0/3 | 0.496826 |
| lof_density | oscr | 0.622510 | 0.764639 | +0.142128 | [+0.087299, +0.194764] | 12/0/2 | 0.088867 |
| max_modality_knn | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| max_modality_knn | unknown_auroc | 0.629381 | 0.836599 | +0.207217 | [+0.144387, +0.274685] | 13/0/1 | 0.034424 |
| max_modality_knn | unknown_aupr | 0.520272 | 0.733479 | +0.213207 | [+0.137360, +0.281461] | 13/0/1 | 0.088867 |
| max_modality_knn | unknown_fpr95 | 0.766698 | 0.517759 | +0.248939 | [+0.115841, +0.396568] | 12/1/1 | 0.280273 |
| max_modality_knn | oscr | 0.565693 | 0.764639 | +0.198945 | [+0.141890, +0.261807] | 14/0/0 | 0.020996 |
| mean_modality_knn | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| mean_modality_knn | unknown_auroc | 0.625632 | 0.836599 | +0.210967 | [+0.149373, +0.276519] | 13/0/1 | 0.034424 |
| mean_modality_knn | unknown_aupr | 0.499029 | 0.733479 | +0.234450 | [+0.175667, +0.290168] | 14/0/0 | 0.020996 |
| mean_modality_knn | unknown_fpr95 | 0.766698 | 0.517759 | +0.248939 | [+0.115487, +0.392848] | 12/1/1 | 0.280273 |
| mean_modality_knn | oscr | 0.563485 | 0.764639 | +0.201153 | [+0.145250, +0.262844] | 14/0/0 | 0.020996 |
| modality_knn_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| modality_knn_union | unknown_auroc | 0.630086 | 0.836599 | +0.206513 | [+0.141451, +0.270498] | 13/0/1 | 0.034424 |
| modality_knn_union | unknown_aupr | 0.508927 | 0.733479 | +0.224552 | [+0.143738, +0.298440] | 13/0/1 | 0.088867 |
| modality_knn_union | unknown_fpr95 | 0.951878 | 0.517759 | +0.434119 | [+0.304159, +0.563924] | 12/2/0 | 0.056152 |
| modality_knn_union | oscr | 0.490908 | 0.764639 | +0.273731 | [+0.196659, +0.353940] | 14/0/0 | 0.020996 |
| modality_support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| modality_support_union | unknown_auroc | 0.611416 | 0.836599 | +0.225183 | [+0.140330, +0.308946] | 12/0/2 | 0.088867 |
| modality_support_union | unknown_aupr | 0.505638 | 0.733479 | +0.227841 | [+0.132851, +0.310696] | 12/0/2 | 0.118408 |
| modality_support_union | unknown_fpr95 | 0.900582 | 0.517759 | +0.382823 | [+0.240558, +0.523167] | 11/2/1 | 0.095703 |
| modality_support_union | oscr | 0.463735 | 0.764639 | +0.300904 | [+0.203496, +0.402925] | 13/0/1 | 0.034424 |
| mondrian_class_support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| mondrian_class_support_union | unknown_auroc | 0.714707 | 0.836599 | +0.121891 | [+0.047692, +0.191978] | 11/0/3 | 0.708984 |
| mondrian_class_support_union | unknown_aupr | 0.606799 | 0.733479 | +0.126680 | [+0.035715, +0.214221] | 10/0/4 | 1.000000 |
| mondrian_class_support_union | unknown_fpr95 | 0.775867 | 0.517759 | +0.258108 | [+0.092660, +0.435577] | 9/2/3 | 0.496826 |
| mondrian_class_support_union | oscr | 0.626468 | 0.764639 | +0.138170 | [+0.080508, +0.195080] | 11/0/3 | 0.256348 |
| mondrian_support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| mondrian_support_union | unknown_auroc | 0.679858 | 0.836599 | +0.156741 | [+0.080355, +0.229799] | 11/0/3 | 0.314209 |
| mondrian_support_union | unknown_aupr | 0.578322 | 0.733479 | +0.155157 | [+0.067129, +0.238621] | 10/0/4 | 0.496826 |
| mondrian_support_union | unknown_fpr95 | 0.815470 | 0.517759 | +0.297711 | [+0.138059, +0.458113] | 10/2/2 | 0.211060 |
| mondrian_support_union | oscr | 0.594901 | 0.764639 | +0.169737 | [+0.094154, +0.246022] | 11/0/3 | 0.211060 |
| msp | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| msp | unknown_auroc | 0.851634 | 0.836599 | -0.015035 | [-0.099604, +0.106715] | 3/0/11 | 1.000000 |
| msp | unknown_aupr | 0.781447 | 0.733479 | -0.047968 | [-0.138395, +0.054819] | 4/0/10 | 1.000000 |
| msp | unknown_fpr95 | 0.397240 | 0.517759 | -0.120520 | [-0.319099, +0.099763] | 4/0/10 | 1.000000 |
| msp | oscr | 0.787993 | 0.764639 | -0.023354 | [-0.112339, +0.107678] | 2/0/12 | 1.000000 |
| support_distance | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| support_distance | unknown_auroc | 0.650091 | 0.836599 | +0.186507 | [+0.126569, +0.244957] | 13/0/1 | 0.043213 |
| support_distance | unknown_aupr | 0.504234 | 0.733479 | +0.229245 | [+0.161878, +0.286793] | 13/0/1 | 0.034424 |
| support_distance | unknown_fpr95 | 0.666187 | 0.517759 | +0.148427 | [+0.021954, +0.280254] | 8/0/6 | 1.000000 |
| support_distance | oscr | 0.583541 | 0.764639 | +0.181098 | [+0.130599, +0.233144] | 13/0/1 | 0.034424 |
| support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| support_union | unknown_auroc | 0.664119 | 0.836599 | +0.172480 | [+0.109016, +0.234195] | 12/0/2 | 0.066528 |
| support_union | unknown_aupr | 0.519250 | 0.733479 | +0.214229 | [+0.141990, +0.283321] | 12/0/2 | 0.066528 |
| support_union | unknown_fpr95 | 0.752212 | 0.517759 | +0.234453 | [+0.105181, +0.370340] | 9/1/4 | 0.703369 |
| support_union | oscr | 0.570039 | 0.764639 | +0.194599 | [+0.129622, +0.266560] | 13/0/1 | 0.034424 |
| top2_modality_knn | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| top2_modality_knn | unknown_auroc | 0.625632 | 0.836599 | +0.210967 | [+0.148726, +0.275388] | 13/0/1 | 0.034424 |
| top2_modality_knn | unknown_aupr | 0.499029 | 0.733479 | +0.234450 | [+0.178133, +0.289980] | 14/0/0 | 0.020996 |
| top2_modality_knn | unknown_fpr95 | 0.766698 | 0.517759 | +0.248939 | [+0.115252, +0.398351] | 12/1/1 | 0.280273 |
| top2_modality_knn | oscr | 0.563485 | 0.764639 | +0.201153 | [+0.144343, +0.261765] | 14/0/0 | 0.020996 |
| tree_disagreement | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| tree_disagreement | unknown_auroc | 0.850185 | 0.836599 | -0.013587 | [-0.086219, +0.095986] | 3/0/11 | 1.000000 |
| tree_disagreement | unknown_aupr | 0.764859 | 0.733479 | -0.031380 | [-0.112881, +0.066344] | 4/0/10 | 1.000000 |
| tree_disagreement | unknown_fpr95 | 0.433314 | 0.517759 | -0.084446 | [-0.275269, +0.123649] | 5/0/9 | 1.000000 |
| tree_disagreement | oscr | 0.764574 | 0.764639 | +0.000064 | [-0.086627, +0.137031] | 2/0/12 | 1.000000 |
| triple_support_union | known_macro_f1 | 0.927941 | 0.927941 | +0.000000 | [+0.000000, +0.000000] | 0/14/0 | NA |
| triple_support_union | unknown_auroc | 0.726180 | 0.836599 | +0.110418 | [+0.055804, +0.162523] | 10/0/4 | 0.398926 |
| triple_support_union | unknown_aupr | 0.583253 | 0.733479 | +0.150226 | [+0.059821, +0.237050] | 10/0/4 | 1.000000 |
| triple_support_union | unknown_fpr95 | 0.780904 | 0.517759 | +0.263145 | [+0.145566, +0.378728] | 11/2/1 | 0.211060 |
| triple_support_union | oscr | 0.620793 | 0.764639 | +0.143845 | [+0.095566, +0.190228] | 12/0/2 | 0.066528 |

## Component decisions

- `anchor_support`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `baseline`: final directionally better on 0/4 unknown metrics; Holm-confirmed: none.
- `cauchy_all`: final directionally better on 0/4 unknown metrics; Holm-confirmed: none.
- `cauchy_baseline`: final directionally better on 0/4 unknown metrics; Holm-confirmed: none.
- `cauchy_bidirectional`: final directionally better on 1/4 unknown metrics; Holm-confirmed: none.
- `cauchy_bidirectional_evidence`: final directionally better on 2/4 unknown metrics; Holm-confirmed: none.
- `cauchy_bidirectional_support`: final directionally better on 1/4 unknown metrics; Holm-confirmed: none.
- `cauchy_conflict`: final directionally better on 2/4 unknown metrics; Holm-confirmed: none.
- `cauchy_distance_class_knn`: final directionally better on 4/4 unknown metrics; Holm-confirmed: oscr.
- `cauchy_distance_knn`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `cauchy_distance_lof`: final directionally better on 4/4 unknown metrics; Holm-confirmed: oscr.
- `cauchy_evidence`: final directionally better on 1/4 unknown metrics; Holm-confirmed: none.
- `cauchy_local_support`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `cauchy_modality_knn`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `cauchy_modality_support`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `class_knn_distance`: final directionally better on 4/4 unknown metrics; Holm-confirmed: none.
- `class_support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: oscr.
- `conflict`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `conflict_augmented`: final directionally better on 0/4 unknown metrics; Holm-confirmed: none.
- `conflict_support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `density_support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: oscr.
- `disagreement_augmented`: final directionally better on 0/4 unknown metrics; Holm-confirmed: none.
- `distance`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `dual_knn_support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: oscr.
- `entropy`: final directionally better on 0/4 unknown metrics; Holm-confirmed: none.
- `foss_partition`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `knn_distance`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `knn_view_0`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `knn_view_1`: final directionally better on 4/4 unknown metrics; Holm-confirmed: oscr.
- `knn_view_2`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `lof_density`: final directionally better on 4/4 unknown metrics; Holm-confirmed: none.
- `max_modality_knn`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, oscr.
- `mean_modality_knn`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `modality_knn_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, oscr.
- `modality_support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: oscr.
- `mondrian_class_support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: none.
- `mondrian_support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: none.
- `msp`: final directionally better on 0/4 unknown metrics; Holm-confirmed: none.
- `support_distance`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: oscr.
- `top2_modality_knn`: final directionally better on 4/4 unknown metrics; Holm-confirmed: unknown_auroc, unknown_aupr, oscr.
- `tree_disagreement`: final directionally better on 1/4 unknown metrics; Holm-confirmed: none.
- `triple_support_union`: final directionally better on 4/4 unknown metrics; Holm-confirmed: none.
