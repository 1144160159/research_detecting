# KRC cross-suite known-certificate diagnostic

State: **valid_partial_diagnostic**.

| Suite | Captures | Complete scenarios | Known classes | Known F1 mean (>=0.9) | Error AUROC mean (>=0.7) | Source-safety failed scenarios | RRC eligible |
|---|---:|---:|---|---:|---:|---:|---:|
| cic_iot2023 | 96 | 32 | 32 | 0.611716 (0) | 0.703697 (55) | 0 | 20 |
| cic_ton_iot | 27 | 9 | 7,8 | 0.802709 (0) | 0.709086 (16) | 9 | 0 |
| cicids2017 | 1 | 0 | 14 | 0.974061 (1) | 0.908810 (1) | 0 | 0 |

This report uses known-validation diagnostics only. It cannot select an
algorithm, change a frozen gate, pool partial results as terminal effect,
or authorize comprehensive SOTA.

Manifest: `1ca089da6da32d503979110f39f867886770ec1d5c339470c4ff1ddb585f3b43`.
