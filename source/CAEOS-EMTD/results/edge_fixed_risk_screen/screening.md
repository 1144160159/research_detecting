# Edge fixed-risk candidate screening

Development runs: 70; scenarios: 14; fixed risks: 44.
Selected candidate: `entropy`.
Status: `frozen_unconfirmed`; manifest SHA-256: `50f9529ab4b394fdd932795711591ea5b61208002b48c8c9bc47a803ec80fbe1`.
Development test unknown labels are used only for candidate screening; the reserved confirmation seeds must remain unseen.

| Rank | Method | Gate | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean metric rank |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | entropy | PASS | 0.927941 | 0.871214 | 0.816901 | 0.375336 | 0.811938 | 1.25 |
| 2 | cauchy_all | PASS | 0.927941 | 0.860233 | 0.798534 | 0.354302 | 0.791412 | 2.50 |
| 3 | disagreement_augmented | PASS | 0.927941 | 0.861774 | 0.808472 | 0.418963 | 0.795818 | 2.75 |
| 4 | msp | PASS | 0.927941 | 0.851634 | 0.781447 | 0.397240 | 0.787993 | 4.75 |
| 5 | cauchy_baseline | PASS | 0.927941 | 0.848261 | 0.796115 | 0.425504 | 0.781333 | 5.50 |
| 6 | baseline | PASS | 0.927941 | 0.847499 | 0.766263 | 0.442058 | 0.781629 | 7.25 |
| 7 | conflict_augmented | PASS | 0.927941 | 0.843470 | 0.765577 | 0.449782 | 0.778918 | 8.50 |
| 8 | tree_disagreement | PASS | 0.927941 | 0.850185 | 0.764859 | 0.433314 | 0.764574 | 8.75 |
| 9 | cauchy_bidirectional | PASS | 0.927941 | 0.836089 | 0.783544 | 0.455265 | 0.771851 | 8.75 |
| 10 | cauchy_evidence | PASS | 0.927941 | 0.828249 | 0.757788 | 0.394670 | 0.769714 | 9.00 |
| 11 | cauchy_bidirectional_support | PASS | 0.927941 | 0.833880 | 0.788404 | 0.476429 | 0.769682 | 9.75 |
| 12 | cauchy_conflict | PASS | 0.927941 | 0.827551 | 0.773614 | 0.454209 | 0.760306 | 11.00 |
| 13 | cauchy_modality_support_union | PASS | 0.927941 | 0.836599 | 0.733479 | 0.517759 | 0.764639 | 12.00 |
| 14 | cauchy_bidirectional_evidence | FAIL | 0.927941 | 0.799582 | 0.744061 | 0.475565 | 0.741459 | 13.25 |
| 15 | class_knn_distance | FAIL | 0.927941 | 0.733834 | 0.600076 | 0.656696 | 0.647742 | 16.25 |

## Stability

Leave-one-scenario-out selected paths: `{'disagreement_augmented': 1, 'entropy': 13}`.
Pareto frontier: `['cauchy_all', 'entropy']`.

This screen is exploratory development evidence, not an independent confirmation result.
