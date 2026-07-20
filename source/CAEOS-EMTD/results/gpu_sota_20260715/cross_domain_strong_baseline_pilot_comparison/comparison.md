# Neural open-set baseline comparison

## edge_iiot

Runs: 1

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.708876 | 0.000000 | 0.708876 | - | - | - |
| opendetect | 0.615546 | 0.000000 | 0.615546 | +0.093330 | 1/0/0 | 1 |
| sieve | 0.472125 | 0.000000 | 0.472125 | +0.236751 | 1/0/0 | 1 |

Test-label oracle neural upper bound: 0.615546; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.860056 | 0.708876 | 0.452217 | 0.522977 | 0.591022 | 0.959041 | 0.056056 |
| opendetect | 0.778399 | 0.615546 | 0.388748 | 0.768731 | 0.480352 | 0.951548 | 0.045045 |
| sieve | 0.534527 | 0.472125 | 0.299454 | 0.923576 | 0.320346 | 0.881618 | 0.032032 |

## nf_cse

Runs: 1

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.769286 | 0.000000 | 0.769286 | - | - | - |
| sieve | 0.835465 | 0.000000 | 0.835465 | -0.066179 | 0/0/1 | 1 |
| opendetect | 0.748793 | 0.000000 | 0.748793 | +0.020493 | 1/0/0 | 1 |

Test-label oracle neural upper bound: 0.835465; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.770748 | 0.769286 | 0.186271 | 0.399617 | 0.690725 | 0.846191 | 0.290984 |
| sieve | 0.705965 | 0.835465 | 0.312221 | 0.584571 | 0.613137 | 0.953043 | 0.266393 |
| opendetect | 0.753075 | 0.748793 | 0.177518 | 0.362722 | 0.584302 | 0.936272 | 0.036885 |

## ustc_tfc2016

Runs: 1

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.974070 | 0.000000 | 0.974070 | - | - | - |
| opendetect | 0.889184 | 0.000000 | 0.889184 | +0.084886 | 1/0/0 | 1 |
| sieve | 0.783572 | 0.000000 | 0.783572 | +0.190498 | 1/0/0 | 1 |

Test-label oracle neural upper bound: 0.889184; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.904189 | 0.974070 | 0.950437 | 0.103470 | 0.898112 | 0.961913 | 0.872000 |
| opendetect | 0.871021 | 0.889184 | 0.700658 | 0.139018 | 0.803333 | 0.962124 | 0.104000 |
| sieve | 0.765293 | 0.783572 | 0.754131 | 0.517774 | 0.629283 | 0.918536 | 0.478333 |
