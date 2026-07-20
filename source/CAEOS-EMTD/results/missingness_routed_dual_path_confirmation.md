# Dual-path Modality-dropout Confirmation

State: **confirmed**

| Scenario | Condition | Baseline F1 | Candidate F1 | Delta F1 | Baseline OSCR | Candidate OSCR | Delta OSCR | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---|
| backdoor | clean | 0.9358 | 0.9358 | +0.0000 | 0.8362 | 0.8362 | +0.0000 | PASS |
| backdoor | field_missing_m1_050 | 0.4132 | 0.7462 | +0.3330 | 0.2336 | 0.3666 | +0.1330 | PASS |
| sql_injection | clean | 0.9562 | 0.9562 | +0.0000 | 0.7964 | 0.7964 | +0.0000 | PASS |
| sql_injection | field_missing_m1_050 | 0.4607 | 0.7812 | +0.3205 | 0.2402 | 0.3979 | +0.1577 | PASS |

Corrupted-scenario mean gains: Known F1 +0.3267, OSCR +0.1454.

This is a promotion gate for a larger robustness matrix, not a final SOTA or significance claim.
