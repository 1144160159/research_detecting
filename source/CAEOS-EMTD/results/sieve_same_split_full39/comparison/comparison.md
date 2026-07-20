# Neural open-set baseline comparison

## doh

Runs: 9

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.867092 | 0.059342 | 0.783586 | - | - | - |
| sieve | 0.739576 | 0.092532 | 0.610344 | +0.127517 | 9/0/0 | 0.00391 |

Test-label oracle neural upper bound: 0.739576; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.972182 | 0.867092 | 0.919924 | 0.498355 | 0.847115 | 0.917053 | 0.558278 |
| sieve | 0.837552 | 0.739576 | 0.813985 | 0.728863 | 0.661122 | 0.922394 | 0.238556 |

## mal_tls

Runs: 18

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.993660 | 0.003404 | 0.986872 | - | - | - |
| sieve | 0.834467 | 0.078444 | 0.644616 | +0.159194 | 18/0/0 | 7.63e-06 |

Test-label oracle neural upper bound: 0.834467; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.974769 | 0.993660 | 0.972678 | 0.012953 | 0.970318 | 0.949253 | 0.999861 |
| sieve | 0.747642 | 0.834467 | 0.609386 | 0.327510 | 0.662139 | 0.949034 | 0.237222 |

## hikari

Runs: 12

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.890776 | 0.073500 | 0.737747 | - | - | - |
| sieve | 0.683302 | 0.315836 | 0.111273 | +0.207474 | 10/0/2 | 0.0122 |

Test-label oracle neural upper bound: 0.683302; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.974263 | 0.890776 | 0.889497 | 0.178453 | 0.859763 | 0.947053 | 0.356115 |
| sieve | 0.931087 | 0.683302 | 0.744709 | 0.436975 | 0.653100 | 0.950665 | 0.206087 |
