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

Scenarios: 38; baselines: 24

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.860665 | 1/25 | relative_mahalanobis | 0.766636 | +0.094029 | [+0.048816, +0.144553] | 0.00447906 | true |
| unknown_aupr | 0.753463 | 1/25 | knn | 0.648123 | +0.105340 | [+0.057870, +0.155378] | 0.00125781 | true |
| unknown_fpr95 | 0.371785 | 1/25 | relative_mahalanobis | 0.460292 | +0.088506 | [+0.008040, +0.172953] | 0.0652346 | false |
| oscr | 0.776289 | 1/25 | relative_mahalanobis | 0.660121 | +0.116168 | [+0.077361, +0.158584] | 4.53845e-07 | true |
| known_macro_f1 | 0.877701 | 1/25 | opendetect | 0.836475 | +0.041226 | [+0.032691, +0.050310] | 8.73115e-10 | true |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`

## edge_iiot

Scenarios: 14; baselines: 24

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.836599 | 1/25 | mahalanobis | 0.729741 | +0.106857 | [+0.033849, +0.187518] | 0.362549 | false |
| unknown_aupr | 0.733479 | 1/25 | knn | 0.637477 | +0.096002 | [-0.012706, +0.210767] | 1 | false |
| unknown_fpr95 | 0.517759 | 1/25 | mahalanobis | 0.602022 | +0.084262 | [-0.060141, +0.245688] | 1 | false |
| oscr | 0.764639 | 1/25 | opendetect | 0.603558 | +0.161081 | [+0.084277, +0.244179] | 0.12207 | false |
| known_macro_f1 | 0.927941 | 1/25 | opendetect | 0.852150 | +0.075790 | [+0.069032, +0.082049] | 0.0146484 | true |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`

## nf_cse

Scenarios: 14; baselines: 24

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.888687 | 1/25 | relative_mahalanobis | 0.795966 | +0.092721 | [+0.049893, +0.137905] | 0.055542 | false |
| unknown_aupr | 0.752977 | 1/25 | relative_mahalanobis | 0.635813 | +0.117165 | [+0.075568, +0.159289] | 0.0476074 | true |
| unknown_fpr95 | 0.215842 | 1/25 | relative_mahalanobis | 0.318273 | +0.102431 | [+0.060105, +0.143386] | 0.0476074 | true |
| oscr | 0.764473 | 1/25 | relative_mahalanobis | 0.670492 | +0.093981 | [+0.057986, +0.132719] | 0.0146484 | true |
| known_macro_f1 | 0.788887 | 1/25 | opendetect | 0.771237 | +0.017650 | [+0.014780, +0.020831] | 0.0146484 | true |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`

## ustc_tfc2016

Scenarios: 10; baselines: 24

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.855128 | 1/25 | relative_mahalanobis | 0.814369 | +0.040760 | [+0.000132, +0.085502] | 0.878906 | false |
| unknown_aupr | 0.782122 | 1/25 | relative_mahalanobis | 0.729788 | +0.052334 | [+0.015013, +0.092048] | 0.792969 | false |
| unknown_fpr95 | 0.385741 | 1/25 | mahalanobis | 0.440106 | +0.054365 | [-0.063068, +0.182885] | 1 | false |
| oscr | 0.809141 | 1/25 | relative_mahalanobis | 0.749023 | +0.060118 | [+0.024952, +0.099610] | 0.792969 | false |
| known_macro_f1 | 0.931705 | 1/25 | opendetect | 0.905864 | +0.025842 | [+0.023285, +0.028443] | 0.234375 | false |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`
