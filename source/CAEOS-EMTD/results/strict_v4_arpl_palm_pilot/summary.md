# Strict-v4 ARPL/PALM baseline expansion

Validation: **PASS**; scenarios: 6; methods: 18.
This is a same-split single-seed pilot, not confirmatory inference.

| Rank | Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | opendetect | 0.684121 | 0.835658 | 0.707983 | 0.378178 | 0.552125 | 2.750 |
| 2 | mlp_openmax | 0.654224 | 0.854765 | 0.693387 | 0.405173 | 0.566329 | 3.250 |
| 3 | mlp_knn | 0.667424 | 0.826961 | 0.724882 | 0.340936 | 0.542393 | 3.250 |
| 4 | caeos | 0.710071 | 0.823516 | 0.647782 | 0.362155 | 0.583803 | 3.250 |
| 5 | mlp_vim | 0.667424 | 0.811125 | 0.636691 | 0.421418 | 0.554145 | 5.250 |
| 6 | mlp_energy | 0.667424 | 0.795948 | 0.612623 | 0.437122 | 0.551930 | 6.750 |
| 7 | mlp_mahalanobis | 0.667424 | 0.799694 | 0.703175 | 0.403989 | 0.513951 | 7.250 |
| 8 | mlp_energy_cea | 0.667424 | 0.786848 | 0.573503 | 0.446843 | 0.543596 | 8.250 |
| 9 | mlp_relative_mahalanobis | 0.667424 | 0.783651 | 0.699851 | 0.458772 | 0.530286 | 8.500 |
| 10 | mlp_scale | 0.657059 | 0.752652 | 0.545584 | 0.469021 | 0.541232 | 10.500 |
| 11 | mlp_max_logit | 0.667424 | 0.735263 | 0.494080 | 0.485662 | 0.542236 | 11.000 |
| 12 | palm_ssd_plus | 0.657173 | 0.765526 | 0.578564 | 0.543612 | 0.531623 | 11.250 |
| 13 | hcrp_osd_adapter | 0.658410 | 0.718892 | 0.466669 | 0.509114 | 0.545018 | 11.500 |
| 14 | mlp_nci | 0.667424 | 0.690044 | 0.457637 | 0.496155 | 0.524136 | 14.000 |
| 15 | arpl | 0.654862 | 0.695232 | 0.460482 | 0.551397 | 0.525703 | 14.250 |
| 16 | mlp_nci_cea | 0.667424 | 0.687765 | 0.448727 | 0.503525 | 0.519460 | 15.000 |
| 17 | mlp_msp | 0.667424 | 0.524918 | 0.353414 | 0.647077 | 0.454880 | 17.500 |
| 18 | ronetc | 0.625070 | 0.507097 | 0.361973 | 0.618134 | 0.411226 | 17.500 |

## Added baseline decisions

- `arpl`: `hold_at_pilot`; unknown wins versus CAEOS 0/4; deltas `{'known_macro_f1': -0.055209280428559215, 'unknown_auroc': -0.12828416070452775, 'unknown_aupr': -0.18730040181754837, 'unknown_fpr95': -0.18924147863453256, 'oscr': -0.05809995988415073}`.
- `palm_ssd_plus`: `hold_at_pilot`; unknown wins versus CAEOS 0/4; deltas `{'known_macro_f1': -0.05289796226866694, 'unknown_auroc': -0.0579908003138041, 'unknown_aupr': -0.06921846847104995, 'unknown_fpr95': -0.1814566571997206, 'oscr': -0.052179694078278493}`.

## Task-level CAEOS gaps

- `cic_iot2023/mirai_udpplain` endpoint `cauchy_modality_support_union`: AUROC -0.112860, AUPR -0.456383, FPR95 -0.170117, OSCR -0.031616.
- `cic_ton_iot/scanning` endpoint `pseudo_unknown_learned_blend`: AUROC -0.105982, AUPR -0.115708, FPR95 -0.174234, OSCR -0.054559.
- `cic_ton_iot/xss` endpoint `pseudo_unknown_learned_blend`: AUROC -0.095362, AUPR -0.147769, FPR95 -0.158562, OSCR -0.055276.
- `cic_iot2023/command_injection` endpoint `cauchy_modality_support_union`: AUROC -0.056906, AUPR +0.032582, FPR95 -0.220417, OSCR -0.030998.
- `cic_iot2023/ddos_icmp_flood` endpoint `cauchy_modality_support_union`: AUROC -0.020049, AUPR -0.201686, FPR95 -0.023602, OSCR -0.004850.
- `cic_ton_iot/ransomware` endpoint `pseudo_unknown_learned_blend`: AUROC +0.007901, AUPR +0.019587, FPR95 -0.058140, OSCR +0.060505.

## CAEOS budget decision

State: **hold_for_risk_adaptation**.
Gates: `{'mean_unknown_rank_at_most_1_5': False, 'auroc_within_0_02_of_strongest': False, 'oscr_within_0_02_of_strongest': True, 'known_f1_within_0_02_of_strongest': True, 'every_task_auroc_within_0_10': False}`.
Worst task AUROC delta: `-0.112860`.
