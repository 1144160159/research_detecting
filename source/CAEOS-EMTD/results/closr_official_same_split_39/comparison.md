# Neural open-set baseline comparison

## doh

Runs: 9

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.867092 | 0.059342 | 0.783586 | - | - | - |
| closr | 0.520955 | 0.151615 | 0.291311 | +0.346137 | 9/0/0 | 0.00391 |

Test-label oracle neural upper bound: 0.520955; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.972182 | 0.867092 | 0.919924 | 0.498355 | 0.847115 | 0.917053 | 0.558278 |
| closr | 0.873818 | 0.520955 | 0.686628 | 0.771088 | 0.487711 | 0.925206 | 0.080278 |

## mal_tls

Runs: 18

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.993660 | 0.003404 | 0.986872 | - | - | - |
| closr | 0.914436 | 0.040738 | 0.863561 | +0.079224 | 17/0/1 | 1.53e-05 |

Test-label oracle neural upper bound: 0.914436; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.974769 | 0.993660 | 0.972678 | 0.012953 | 0.970318 | 0.949253 | 0.999861 |
| closr | 0.823432 | 0.914436 | 0.773682 | 0.216132 | 0.770473 | 0.945884 | 0.436250 |

## hikari

Runs: 12

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.890776 | 0.073500 | 0.737747 | - | - | - |
| closr | 0.730986 | 0.268085 | 0.226182 | +0.159791 | 7/0/5 | 0.11 |

Test-label oracle neural upper bound: 0.730986; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.974263 | 0.890776 | 0.889497 | 0.178453 | 0.859763 | 0.947053 | 0.356115 |
| closr | 0.942810 | 0.730986 | 0.780286 | 0.343683 | 0.699681 | 0.950724 | 0.323486 |
