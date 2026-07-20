# Strict-v4 full 102-scenario coverage screen

Validation: **PASS**; datasets: 7; scenarios: 102; methods: 22.
This is a seed7 coverage screen, not confirmatory multi-seed inference.

| Rank | Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | caeos_domain_safe_router | 0.785848 | 0.777024 | 0.595685 | 0.465323 | 0.635143 | 1.500 |
| 2 | caeos_openmax_rank_union | 0.785848 | 0.771483 | 0.570017 | 0.428827 | 0.647838 | 2.000 |
| 3 | caeos_pairwise | 0.785848 | 0.768855 | 0.586630 | 0.513630 | 0.618404 | 3.750 |
| 4 | opendetect | 0.746897 | 0.733439 | 0.525633 | 0.503411 | 0.591630 | 6.000 |
| 5 | caeos_reference | 0.785848 | 0.765327 | 0.583447 | 0.528651 | 0.609713 | 6.250 |
| 6 | mlp_knn | 0.721949 | 0.729736 | 0.536287 | 0.490749 | 0.571710 | 6.250 |
| 7 | mlp_vim | 0.721949 | 0.710376 | 0.496965 | 0.503066 | 0.581279 | 7.250 |
| 8 | mlp_mahalanobis | 0.721949 | 0.723642 | 0.525892 | 0.490248 | 0.561491 | 7.500 |
| 9 | mlp_relative_mahalanobis | 0.721949 | 0.710430 | 0.531966 | 0.523342 | 0.563577 | 9.000 |
| 10 | mlp_energy | 0.721949 | 0.695620 | 0.481334 | 0.514526 | 0.574054 | 9.000 |
| 11 | mlp_energy_cea | 0.721949 | 0.689040 | 0.457272 | 0.519912 | 0.566530 | 11.000 |
| 12 | caeos_openmax_risk | 0.785848 | 0.676917 | 0.461194 | 0.525414 | 0.576225 | 11.000 |
| 13 | mlp_max_logit | 0.721949 | 0.677720 | 0.455032 | 0.525910 | 0.571734 | 12.000 |
| 14 | mlp_openmax | 0.703789 | 0.676673 | 0.454999 | 0.525056 | 0.549221 | 13.500 |
| 15 | mlp_nci | 0.721949 | 0.642830 | 0.428730 | 0.558626 | 0.544942 | 15.500 |
| 16 | local_outlier_factor | 0.666155 | 0.676305 | 0.474406 | 0.674049 | 0.477271 | 16.000 |
| 17 | mlp_nci_cea | 0.721949 | 0.639074 | 0.415960 | 0.561511 | 0.539575 | 16.750 |
| 18 | mlp_scale | 0.712592 | 0.616903 | 0.419700 | 0.592126 | 0.518565 | 17.500 |
| 19 | mlp_msp | 0.721949 | 0.595978 | 0.388426 | 0.610990 | 0.529479 | 18.750 |
| 20 | one_class_svm | 0.666155 | 0.581904 | 0.414610 | 0.710957 | 0.391902 | 19.750 |
| 21 | pca_reconstruction | 0.666155 | 0.564582 | 0.391915 | 0.726487 | 0.383028 | 21.000 |
| 22 | isolation_forest | 0.666155 | 0.537803 | 0.366414 | 0.712155 | 0.356682 | 21.750 |

## Frozen domain-safe router versus pairwise CAEOS

| Metric | Pairwise | Domain-safe router | Oriented gain | 95% CI | W/T/L |
|---|---:|---:|---:|---:|---:|
| known_macro_f1 | 0.785848 | 0.785848 | +0.000000 | [+0.000000, +0.000000] | 0/102/0 |
| unknown_auroc | 0.768855 | 0.777024 | +0.008169 | [-0.001792, +0.018085] | 29/60/13 |
| unknown_aupr | 0.586630 | 0.595685 | +0.009055 | [-0.001090, +0.020041] | 26/60/16 |
| unknown_fpr95 | 0.513630 | 0.465323 | +0.048307 | [+0.009223, +0.087303] | 32/60/10 |
| oscr | 0.618404 | 0.635143 | +0.016739 | [+0.006628, +0.027830] | 29/60/13 |

## Decision

Final mean-rank-one: **False**.
All four means improve versus pairwise CAEOS: **True**.
Every suite is non-regressing versus pairwise CAEOS: **True**.
Full SOTA claim: **NOT YET ALLOWED**; this router was selected on seed7 and requires frozen new-seed confirmation.
