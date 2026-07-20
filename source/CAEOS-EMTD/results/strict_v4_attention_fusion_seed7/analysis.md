# Strict-v4 entropy-conditioned attention fusion

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | ECE |
|---|---:|---:|---:|---:|---:|---:|
| uniform_probability_average | 0.731063 | 0.721614 | 0.512741 | 0.523668 | 0.618369 | 0.161888 |
| entropy_conditioned_learnable_attention | 0.733796 | 0.706727 | 0.489718 | 0.514855 | 0.614743 | 0.076775 |
| caeos_reliability_fusion | 0.736052 | 0.732723 | 0.515156 | 0.484859 | 0.631096 | 0.087127 |

Decisions: `{"attention_beats_caeos_reliability_fusion": false, "attention_beats_uniform_probability_average": false}`.
