# Strict-v2 SOTA decision

Mean rank and confirmatory significance are reported separately.

Highest supported claim: `comprehensive_confirmed_sota`
Full SOTA claim allowed: `True`

## Claim gates

| Gate | Pass |
|---|---:|
| global_primary_mean_rank_one | true |
| global_all_metrics_mean_rank_one | true |
| global_primary_confirmed | true |
| global_all_metrics_confirmed | true |
| cross_suite_primary_mean_rank_one | true |
| cross_suite_all_metrics_mean_rank_one | true |
| cross_suite_primary_confirmed | false |
| cross_suite_all_metrics_confirmed | false |
| comprehensive_confirmed_sota | true |

A full SOTA claim requires rank one and confirmatory superiority on all five metrics in the global scenario-blocked family, plus rank one on all five metrics in every reported suite. Suite-wise significance is reported as stronger replication evidence but is not required because small suite-level scenario counts can make family-wise significance mathematically unattainable.

## global

Scenarios: 38; baselines: 7

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.839183 | 1/8 | opendetect | 0.725590 | +0.113594 | [+0.059264, +0.171714] | 0.000704719 | true |
| unknown_aupr | 0.737376 | 1/8 | opendetect | 0.587420 | +0.149956 | [+0.096336, +0.204610] | 4.09186e-05 | true |
| unknown_fpr95 | 0.401565 | 1/8 | opendetect | 0.546521 | +0.144956 | [+0.044228, +0.242624] | 0.0197933 | true |
| oscr | 0.755264 | 1/8 | opendetect | 0.637653 | +0.117611 | [+0.071625, +0.164409] | 5.48508e-05 | true |
| known_macro_f1 | 0.877701 | 1/8 | opendetect | 0.836475 | +0.041226 | [+0.032691, +0.050310] | 2.54659e-10 | true |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `True`
All metrics strongest comparisons confirmed: `True`

## edge_iiot

Scenarios: 14; baselines: 7

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.836599 | 1/8 | opendetect | 0.714953 | +0.121645 | [+0.035528, +0.217222] | 0.0981445 | false |
| unknown_aupr | 0.733479 | 1/8 | opendetect | 0.573505 | +0.159974 | [+0.068923, +0.251483] | 0.0671387 | false |
| unknown_fpr95 | 0.517759 | 1/8 | arpl | 0.675217 | +0.157457 | [-0.031080, +0.351007] | 0.459229 | false |
| oscr | 0.764639 | 1/8 | opendetect | 0.603558 | +0.161081 | [+0.084277, +0.244179] | 0.0274658 | true |
| known_macro_f1 | 0.927941 | 1/8 | opendetect | 0.852150 | +0.075790 | [+0.069032, +0.082049] | 0.00427246 | true |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`

## nf_cse

Scenarios: 14; baselines: 7

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.838957 | 1/8 | arpl | 0.722857 | +0.116100 | [-0.018968, +0.249858] | 0.811523 | false |
| unknown_aupr | 0.721551 | 1/8 | arpl | 0.577334 | +0.144217 | [-0.016215, +0.304241] | 0.811523 | false |
| unknown_fpr95 | 0.271590 | 1/8 | opendetect | 0.415947 | +0.144357 | [-0.013266, +0.304818] | 0.811523 | false |
| oscr | 0.717072 | 1/8 | arpl | 0.655405 | +0.061667 | [-0.034535, +0.157272] | 0.811523 | false |
| known_macro_f1 | 0.788887 | 1/8 | opendetect | 0.771237 | +0.017650 | [+0.014780, +0.020831] | 0.00427246 | true |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`

## ustc_tfc2016

Scenarios: 10; baselines: 7

| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| unknown_auroc | 0.843119 | 1/8 | sieve | 0.770521 | +0.072598 | [+0.009946, +0.153193] | 0.292969 | false |
| unknown_aupr | 0.764988 | 1/8 | sieve | 0.687518 | +0.077470 | [+0.003215, +0.151084] | 0.421875 | false |
| unknown_fpr95 | 0.420857 | 1/8 | opendetect | 0.523034 | +0.102176 | [-0.010122, +0.213531] | 0.419922 | false |
| oscr | 0.795608 | 1/8 | arpl | 0.711776 | +0.083832 | [+0.055042, +0.114646] | 0.0683594 | false |
| known_macro_f1 | 0.931705 | 1/8 | opendetect | 0.905864 | +0.025842 | [+0.023285, +0.028443] | 0.0683594 | false |

All primary means rank first: `True`
All metrics mean rank first: `True`
All primary strongest comparisons confirmed: `False`
All metrics strongest comparisons confirmed: `False`
