# EFC strict-v2 pilot

Decision: `retain_three_task_pilot`. This gate controls compute budget only.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR |
|---|---:|---:|---:|---:|---:|
| efc | 0.825756 | 0.680736 | 0.524845 | 0.459798 | 0.583681 |
| caeos | 0.897148 | 0.762808 | 0.709999 | 0.421633 | 0.699321 |
| ronetc | 0.812388 | 0.653505 | 0.516092 | 0.543377 | 0.617623 |

## Budget gate

- `mean_auroc_not_worse`: PASS
- `mean_oscr_within_0_02`: FAIL
- `mean_known_f1_within_0_02`: PASS
- `every_task_auroc_within_0_10`: PASS
