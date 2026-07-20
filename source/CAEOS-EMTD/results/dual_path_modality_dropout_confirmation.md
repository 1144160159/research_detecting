# Dual-path Modality-dropout Confirmation

State: **rejected**

| Scenario | Condition | Baseline F1 | Candidate F1 | Delta F1 | Baseline OSCR | Candidate OSCR | Delta OSCR | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---|
| ddos_http | clean | 0.9629 | 0.9634 | +0.0005 | 0.6707 | 0.6706 | -0.0001 | PASS |
| ddos_http | field_missing_m1_050 | 0.4854 | 0.8027 | +0.3173 | 0.2822 | 0.4492 | +0.1670 | PASS |
| ransomware | clean | 0.8721 | 0.8692 | -0.0029 | 0.5095 | 0.5092 | -0.0003 | FAIL |
| ransomware | field_missing_m1_050 | 0.4178 | 0.6699 | +0.2521 | 0.2220 | 0.3360 | +0.1140 | PASS |

Corrupted-scenario mean gains: Known F1 +0.2847, OSCR +0.1405.

This is a promotion gate for a larger robustness matrix, not a final SOTA or significance claim.
