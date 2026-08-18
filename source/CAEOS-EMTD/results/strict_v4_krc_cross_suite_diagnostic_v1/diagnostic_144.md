# KRC cross-suite known-certificate diagnostic

State: **valid_partial_diagnostic**.

| Suite | Captures | Complete scenarios | Known classes | Known F1 mean (>=0.9) | Error AUROC mean (>=0.7) | Source-safety failed scenarios | RRC eligible |
|---|---:|---:|---|---:|---:|---:|---:|
| cic_iot2023 | 96 | 32 | 32 | 0.611716 (0) | 0.703697 (55) | 0 | 20 |
| cic_ton_iot | 27 | 9 | 7,8 | 0.802709 (0) | 0.709086 (16) | 9 | 0 |
| cicids2017 | 21 | 7 | 14 | 0.960290 (21) | 0.908307 (21) | 0 | 7 |

This report uses known-validation diagnostics only. It cannot select an
algorithm, change a frozen gate, pool partial results as terminal effect,
or authorize comprehensive SOTA.

Manifest: `47d25186edc83fc679ec4d7e2bd13cb268d868a3176ea9d4c92cafa0cbfa420e`.
