# Strict-v4 representative pilot

Validation: **PASS**; scenarios: 6; methods: 15.
This is a descriptive single-seed budget gate, not confirmatory inference.

| Rank | Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | opendetect | 0.684121 | 0.835658 | 0.707983 | 0.378178 | 0.552125 | 2.75 |
| 2 | mlp_knn | 0.667424 | 0.826961 | 0.724882 | 0.340936 | 0.542393 | 3.00 |
| 3 | mlp_openmax | 0.654224 | 0.854765 | 0.693387 | 0.405173 | 0.566329 | 3.25 |
| 4 | caeos | 0.710071 | 0.823516 | 0.647782 | 0.362155 | 0.583803 | 3.25 |
| 5 | mlp_vim | 0.667424 | 0.811125 | 0.636691 | 0.421418 | 0.554145 | 5.25 |
| 6 | mlp_mahalanobis | 0.667424 | 0.799694 | 0.703175 | 0.403989 | 0.513951 | 6.50 |
| 7 | mlp_energy | 0.667424 | 0.795948 | 0.612623 | 0.437122 | 0.551930 | 6.75 |
| 8 | mlp_energy_cea | 0.667424 | 0.786848 | 0.573503 | 0.446843 | 0.543596 | 7.75 |
| 9 | mlp_relative_mahalanobis | 0.667424 | 0.783651 | 0.699851 | 0.458772 | 0.530286 | 8.00 |
| 10 | mlp_scale | 0.657059 | 0.752652 | 0.545584 | 0.469021 | 0.541232 | 9.75 |
| 11 | mlp_max_logit | 0.667424 | 0.735263 | 0.494080 | 0.485662 | 0.542236 | 10.25 |
| 12 | mlp_nci | 0.667424 | 0.690044 | 0.457637 | 0.496155 | 0.524136 | 11.75 |
| 13 | mlp_nci_cea | 0.667424 | 0.687765 | 0.448727 | 0.503525 | 0.519460 | 12.75 |
| 14 | mlp_msp | 0.667424 | 0.524918 | 0.353414 | 0.647077 | 0.454880 | 14.50 |
| 15 | ronetc | 0.625070 | 0.507097 | 0.361973 | 0.618134 | 0.411226 | 14.50 |

## Budget decision

State: **hold_for_risk_adaptation**.
Gates: `{'mean_unknown_rank_at_most_1_5': False, 'auroc_within_0_02_of_strongest': False, 'oscr_within_0_02_of_strongest': True, 'known_f1_within_0_02_of_strongest': True, 'every_task_auroc_within_0_10': False}`.
Worst per-task AUROC oriented delta: `-0.112860`.

## Group-cache audit

Eligible CICIoT2023 classes: 33; excluded: `['Uploading_Attack']`; rows: 33000.
