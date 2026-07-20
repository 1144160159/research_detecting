# Strict-v2 SOTA decision

Mean rank and confirmatory significance are reported separately.

Highest supported claim: `cross_suite_primary_mean_sota_only`
Full SOTA claim allowed: `False`

## Claim gates

| Gate | Pass |
|---|---:|
| global_primary_mean_rank_one | true |
| global_all_metrics_mean_rank_one | true |
| global_primary_confirmed | false |
| global_all_metrics_confirmed | false |
| cross_suite_primary_mean_rank_one | true |
| cross_suite_all_metrics_mean_rank_one | true |
| cross_suite_primary_confirmed | false |
| cross_suite_all_metrics_confirmed | false |
| comprehensive_confirmed_sota | false |

A full SOTA claim requires rank one and confirmatory superiority on all five metrics in the global scenario-blocked family, plus rank one on all five metrics in every reported suite. Suite-wise significance is reported as stronger replication evidence but is not required because small suite-level scenario counts can make family-wise significance mathematically unattainable.

## global

Scenarios: 38; baselines: 20

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.839183 | 1/21 | relative_mahalanobis | 0.766636 | +0.072548 | [+0.022955, +0.127961] | 0.109668 | false |
| unknown_aupr | 0.737376 | 1/21 | knn | 0.648123 | +0.089253 | [+0.038151, +0.143135] | 0.0195804 | true |
| unknown_fpr95 | 0.401565 | 1/21 | relative_mahalanobis | 0.460292 | +0.058727 | [-0.025347, +0.146539] | 0.313835 | false |
| oscr | 0.755264 | 1/21 | relative_mahalanobis | 0.660121 | +0.095143 | [+0.051478, +0.141442] | 5.62233e-05 | true |
| known_macro_f1 | 0.877701 | 1/21 | opendetect | 0.836475 | +0.041226 | [+0.032691, +0.050310] | 7.27596e-10 | true |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`

## edge_iiot

Scenarios: 14; baselines: 20

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.836599 | 1/21 | mahalanobis | 0.729741 | +0.106857 | [+0.033849, +0.187518] | 0.362549 | false |
| unknown_aupr | 0.733479 | 1/21 | knn | 0.637477 | +0.096002 | [-0.012706, +0.210767] | 1 | false |
| unknown_fpr95 | 0.517759 | 1/21 | mahalanobis | 0.602022 | +0.084262 | [-0.060141, +0.245688] | 1 | false |
| oscr | 0.764639 | 1/21 | opendetect | 0.603558 | +0.161081 | [+0.084277, +0.244179] | 0.109863 | false |
| known_macro_f1 | 0.927941 | 1/21 | opendetect | 0.852150 | +0.075790 | [+0.069032, +0.082049] | 0.012207 | true |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`

## nf_cse

Scenarios: 14; baselines: 20

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.838957 | 1/21 | relative_mahalanobis | 0.795966 | +0.042991 | [-0.030204, +0.107431] | 1 | false |
| unknown_aupr | 0.721551 | 1/21 | relative_mahalanobis | 0.635813 | +0.085738 | [+0.021134, +0.142319] | 0.845947 | false |
| unknown_fpr95 | 0.271590 | 1/21 | relative_mahalanobis | 0.318273 | +0.046683 | [-0.039753, +0.115302] | 1 | false |
| oscr | 0.717072 | 1/21 | relative_mahalanobis | 0.670492 | +0.046581 | [-0.018407, +0.099368] | 1 | false |
| known_macro_f1 | 0.788887 | 1/21 | opendetect | 0.771237 | +0.017650 | [+0.014780, +0.020831] | 0.012207 | true |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`

## ustc_tfc2016

Scenarios: 10; baselines: 20

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.843119 | 1/21 | relative_mahalanobis | 0.814369 | +0.028751 | [-0.002729, +0.067352] | 1 | false |
| unknown_aupr | 0.764988 | 1/21 | relative_mahalanobis | 0.729788 | +0.035200 | [-0.006019, +0.074340] | 1 | false |
| unknown_fpr95 | 0.420857 | 1/21 | mahalanobis | 0.440106 | +0.019249 | [-0.105651, +0.147918] | 1 | false |
| oscr | 0.795608 | 1/21 | relative_mahalanobis | 0.749023 | +0.046585 | [+0.018001, +0.080967] | 0.246094 | false |
| known_macro_f1 | 0.931705 | 1/21 | opendetect | 0.905864 | +0.025842 | [+0.023285, +0.028443] | 0.195312 | false |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`
