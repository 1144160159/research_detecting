# Neural open-set baseline comparison

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
