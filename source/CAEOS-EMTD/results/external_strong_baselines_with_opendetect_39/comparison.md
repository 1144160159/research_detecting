# Neural open-set baseline comparison

## doh

Runs: 9

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.867092 | 0.059342 | 0.783586 | - | - | - |
| opendetect | 0.628822 | 0.121646 | 0.431895 | +0.238270 | 9/0/0 | 0.00391 |
| cade | 0.523544 | 0.075608 | 0.416979 | +0.343549 | 9/0/0 | 0.00391 |
| closr | 0.520955 | 0.151615 | 0.291311 | +0.346137 | 9/0/0 | 0.00391 |

Test-label oracle neural upper bound: 0.668449; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.972182 | 0.867092 | 0.919924 | 0.498355 | 0.847115 | 0.917053 | 0.558278 |
| opendetect | 0.945503 | 0.628822 | 0.764238 | 0.818130 | 0.611893 | 0.920035 | 0.188778 |
| cade | 0.865653 | 0.523544 | 0.684103 | 0.899174 | 0.470240 | 0.919271 | 0.066833 |
| closr | 0.873818 | 0.520955 | 0.686628 | 0.771088 | 0.487711 | 0.925206 | 0.080278 |

## mal_tls

Runs: 18

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.993660 | 0.003404 | 0.986872 | - | - | - |
| closr | 0.914436 | 0.040738 | 0.863561 | +0.079224 | 17/0/1 | 1.53e-05 |
| opendetect | 0.909772 | 0.092249 | 0.691693 | +0.083888 | 15/0/3 | 0.000328 |
| cade | 0.700762 | 0.149022 | 0.424522 | +0.292899 | 18/0/0 | 7.63e-06 |

Test-label oracle neural upper bound: 0.954932; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.974769 | 0.993660 | 0.972678 | 0.012953 | 0.970318 | 0.949253 | 0.999861 |
| closr | 0.823432 | 0.914436 | 0.773682 | 0.216132 | 0.770473 | 0.945884 | 0.436250 |
| opendetect | 0.933525 | 0.909772 | 0.758569 | 0.220432 | 0.856910 | 0.949315 | 0.580231 |
| cade | 0.841597 | 0.700762 | 0.517393 | 0.727208 | 0.590065 | 0.947322 | 0.197315 |

## hikari

Runs: 12

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.890776 | 0.073500 | 0.737747 | - | - | - |
| opendetect | 0.738691 | 0.158624 | 0.349744 | +0.152085 | 8/0/4 | 0.064 |
| closr | 0.730986 | 0.268085 | 0.226182 | +0.159791 | 7/0/5 | 0.11 |
| cade | 0.604984 | 0.273630 | 0.040394 | +0.285792 | 12/0/0 | 0.000488 |

Test-label oracle neural upper bound: 0.890434; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.974263 | 0.890776 | 0.889497 | 0.178453 | 0.859763 | 0.947053 | 0.356115 |
| opendetect | 0.974770 | 0.738691 | 0.760276 | 0.467987 | 0.720705 | 0.936524 | 0.177789 |
| closr | 0.942810 | 0.730986 | 0.780286 | 0.343683 | 0.699681 | 0.950724 | 0.323486 |
| cade | 0.941217 | 0.604984 | 0.675499 | 0.551725 | 0.589178 | 0.939161 | 0.040480 |
