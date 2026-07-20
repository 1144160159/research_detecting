# Neural open-set baseline comparison

## edge_iiot

Runs: 14

| Method | AUROC mean | std | min | Gate delta | W/T/L | Wilcoxon p |
|---|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.650458 | 0.191243 | 0.170157 | - | - | - |
| opendetect | 0.730028 | 0.094331 | 0.553886 | -0.079569 | 5/0/9 | 0.296 |
| sieve | 0.667814 | 0.147744 | 0.449245 | -0.017356 | 7/0/7 | 0.952 |

Test-label oracle neural upper bound: 0.771119; this is diagnostic only and is not a deployable baseline.

| Method | Known Macro-F1 | Unknown AUROC | AUPR | FPR95 | OSCR | Known accept | Unknown reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| nested_conflict_gate | 0.897087 | 0.650458 | 0.516127 | 0.644569 | 0.568270 | 0.954209 | 0.200245 |
| opendetect | 0.811761 | 0.730028 | 0.566511 | 0.716579 | 0.602295 | 0.957056 | 0.196542 |
| sieve | 0.543619 | 0.667814 | 0.459371 | 0.700441 | 0.408614 | 0.939542 | 0.160629 |
