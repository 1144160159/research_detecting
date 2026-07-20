# NF-CSE / USTC 固定风险开发筛查

- 开发种子：`7`。
- 场景块：`24`。
- 固定风险：`44`。
- 状态：`frozen_unconfirmed`，开发筛查使用未知测试标签，只能生成候选。
- manifest SHA-256：`68a990fa6e4d2238610d526de56d576717608b1aabb13cb2955aec35f01aa22a`。

## nf_cse

选择 `disagreement_augmented`；LOSO 路径为 `{'disagreement_augmented': 13, 'entropy': 1}`。

| AUROC | AUPR | FPR95 有向 | OSCR |
|---:|---:|---:|---:|
| +0.061962 | +0.030108 | +0.058961 | +0.054380 |

## ustc_tfc2016

选择 `cauchy_conflict`；LOSO 路径为 `{'cauchy_conflict': 10}`。

| AUROC | AUPR | FPR95 有向 | OSCR |
|---:|---:|---:|---:|
| +0.033975 | +0.067824 | +0.043785 | +0.030270 |

## 确认边界

候选只允许在全新种子 `83/89/97/101` 上确认。运行时仅按已知数据集标识使用固定风险，不允许用未知类或测试标签切换。若组合 AUROC 的场景块 bootstrap 下界不大于 0、任一安全指标回退超过 0.01，或任一数据集四项有向均值不全为正，则保留当前确认策略。
