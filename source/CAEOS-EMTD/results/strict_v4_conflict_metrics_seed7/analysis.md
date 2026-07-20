# Strict-v4 D1-D7 conflict metric analysis

Posthoc mechanism analysis on 102 frozen seed7 scenarios; test labels are used only for statistical evaluation.

| Metric | AUROC mean | Effect mean | Spearman(U) | LL gain | Sig. positive rate |
|---|---:|---:|---:|---:|---:|
| d1_label_disagreement | 0.625370 | 0.250739 | 0.506808 | 0.03666709 | 0.676 |
| d2_cosine_distance | 0.642711 | 0.285422 | 0.302313 | 0.05321646 | 0.706 |
| d3_jensen_shannon | 0.629649 | 0.259298 | 0.210086 | 0.05482221 | 0.716 |
| d4_symmetric_kl | 0.628075 | 0.256151 | 0.168127 | 0.05329548 | 0.686 |
| d5_raw_ds_conflict | 0.570844 | 0.141688 | -0.154473 | 0.05419442 | 0.814 |
| d6_conditional_ds_conflict | 0.714025 | 0.428050 | 0.721814 | 0.05441761 | 0.755 |
| d7_reliability_conditional_conflict | 0.722043 | 0.444087 | 0.715196 | 0.05893815 | 0.735 |

D6-D5 AUROC: mean +0.143181, positive rate 0.716.
D7-D6 AUROC: mean +0.008018, positive rate 0.500.

Decisions: `{"conditional_conflict_has_incremental_information": true, "conditional_normalization_supported": true, "reliability_weighting_supported": false}`.
