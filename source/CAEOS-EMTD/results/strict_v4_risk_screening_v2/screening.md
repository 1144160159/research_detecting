# Strict-v4 expanded-development risk screening

Runs: 18; scenario blocks: 12; fixed risks: 46.
The failed confirmation set is now development evidence. Screening uses unknown test labels and cannot itself support a final claim.
State: **frozen_unconfirmed**; candidate: `cauchy_all`.
Manifest: `8636e8111db54735cfa8f01387b0a8db8a4e50b40003d0696f999762a7805bb5`.

| Method | Eligible | AUROC | AUPR | FPR95 oriented | OSCR | Worst suite-metric | Worst LOSO-metric |
|---|---:|---:|---:|---:|---:|---:|---:|
| cauchy_all | true | +0.036384 | +0.031922 | +0.143394 | +0.046908 | +0.023440 | +0.026324 |
| disagreement_augmented | true | +0.034036 | +0.034430 | +0.167573 | +0.047161 | +0.013504 | +0.017644 |
| cauchy_conflict | true | +0.023334 | +0.015574 | +0.112812 | +0.036156 | +0.006611 | +0.001583 |
| conflict_augmented | true | +0.026786 | +0.027968 | +0.159803 | +0.043416 | +0.005076 | +0.006951 |
| missing_aware_cauchy_modality_support_union | false | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| cauchy_baseline | false | +0.014434 | +0.010898 | +0.106976 | +0.027694 | -0.007627 | -0.010421 |
| baseline | false | +0.014772 | +0.010529 | +0.148389 | +0.034814 | -0.008965 | -0.008470 |
| cauchy_distance_class_knn | false | +0.008550 | -0.009233 | +0.072428 | -0.000280 | -0.039544 | -0.027158 |
| knn_distance | false | +0.004527 | -0.032605 | +0.121969 | +0.004269 | -0.046073 | -0.045025 |
| cauchy_local_support | false | -0.003041 | -0.030999 | +0.061949 | +0.010013 | -0.047177 | -0.044496 |
| cauchy_distance_knn | false | -0.000294 | -0.013970 | +0.064058 | -0.009792 | -0.051981 | -0.035718 |
| class_support_union | false | -0.001499 | -0.005795 | +0.041761 | -0.017216 | -0.054012 | -0.035426 |
| support_distance | false | -0.008169 | -0.025271 | +0.064951 | -0.017858 | -0.062679 | -0.043907 |
| class_knn_distance | false | +0.003540 | -0.051744 | +0.115525 | +0.014419 | -0.069662 | -0.062693 |
| support_union | false | -0.013029 | -0.015882 | +0.037985 | -0.030268 | -0.071796 | -0.051061 |

A candidate is frozen only when one fixed risk is jointly safe across both suites and every leave-one-scenario-out fold.
