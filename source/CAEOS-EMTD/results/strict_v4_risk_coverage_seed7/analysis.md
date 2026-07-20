# Strict-v4 seed7 risk-coverage analysis

This is descriptive development evidence and does not select the final algorithm.

| Method | AURC | EAURC | Q=.95 known accept | Q=.95 unknown reject | Q=.95 open-set accuracy |
|---|---:|---:|---:|---:|---:|
| caeos_pairwise | 0.230306 | 0.095487 | 0.936218 | 0.413095 | 0.653447 |
| opendetect | 0.287912 | 0.142988 | 0.948052 | 0.282366 | 0.589353 |

## CAEOS oriented gains

- `aurc_reduction`: `+0.057606`
- `eaurc_reduction`: `+0.047502`
- `known_acceptance_rate_0.950`: `-0.011834`
- `unknown_rejection_rate_0.950`: `+0.130729`
- `known_accuracy_when_accepted_0.950`: `+0.029062`
- `open_set_accuracy_0.950`: `+0.064095`
- `selective_risk_reduction_0.950`: `+0.067537`
- `known_acceptance_rate_0.975`: `-0.008251`
- `unknown_rejection_rate_0.975`: `+0.140321`
- `known_accuracy_when_accepted_0.975`: `+0.027436`
- `open_set_accuracy_0.975`: `+0.069606`
- `selective_risk_reduction_0.975`: `+0.066148`
