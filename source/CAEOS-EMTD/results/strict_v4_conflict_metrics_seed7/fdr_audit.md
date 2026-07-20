# Strict-v4 conflict metric FDR audit

| Metric | Positive coef. | FDR significant | FDR significant positive | Rate |
|---|---:|---:|---:|---:|
| d1_label_disagreement | 75 | 94 | 69 | 0.676 |
| d2_cosine_distance | 77 | 93 | 72 | 0.706 |
| d3_jensen_shannon | 75 | 99 | 73 | 0.716 |
| d4_symmetric_kl | 76 | 94 | 70 | 0.686 |
| d5_raw_ds_conflict | 88 | 95 | 83 | 0.814 |
| d6_conditional_ds_conflict | 78 | 97 | 77 | 0.755 |
| d7_reliability_conditional_conflict | 78 | 96 | 75 | 0.735 |

D6-D5: mean +0.143181, 95% bootstrap CI [+0.083157, +0.203062], one-sided Wilcoxon p=1.4688825e-06.

Decisions: `{"conditional_conflict_increment_survives_fdr": true, "conditional_normalization_paired_supported": true}`.
