# Strict-v4 DCC frozen pilot

Scenarios: `14/14`; failures: `0`; expand: `false`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.785087 | 0.727455 | 0.458034 | 0.485456 | 0.602436 | 1.250 |
| mahalanobis_pp | 0.762301 | 0.711754 | 0.465043 | 0.531275 | 0.563052 | 1.750 |
| mlp_mahalanobis | 0.762301 | 0.706064 | 0.457754 | 0.535095 | 0.558197 | 3.000 |
| dcc | 0.762301 | 0.678972 | 0.438487 | 0.619925 | 0.535440 | 4.000 |

DCC vs Mahalanobis++ oriented four-metric mean gain: `-0.043900`.
This seed-7 pilot is a development screen and is not confirmatory SOTA evidence.
