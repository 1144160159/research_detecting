# KRC cross-suite known-certificate diagnostic

State: **valid_partial_diagnostic**.

| Suite | Captures | Complete scenarios | Known classes | Known F1 mean (>=0.9) | Error AUROC mean (>=0.7) | Source-safety failed scenarios | RRC eligible |
|---|---:|---:|---|---:|---:|---:|---:|
| cic_iot2023 | 96 | 32 | 32 | 0.611716 (0) | 0.703697 (55) | 0 | 20 |
| cic_ton_iot | 27 | 9 | 7,8 | 0.802709 (0) | 0.709086 (16) | 9 | 0 |
| cicids2017 | 9 | 3 | 14 | 0.962111 (9) | 0.910294 (9) | 0 | 3 |

This report uses known-validation diagnostics only. It cannot select an
algorithm, change a frozen gate, pool partial results as terminal effect,
or authorize comprehensive SOTA.

Manifest: `16290c245f7094524e1d279f023f4b8fb0aae8d6504d73b77f196053f6d4444d`.
