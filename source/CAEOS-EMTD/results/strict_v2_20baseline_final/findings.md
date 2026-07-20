# strict-v2 20 基线最终判定

判定日期：2026-07-17

## 完整性

- CAEOS：190/190。
- 基线：20 个方法，38 个场景，5 个种子。
- 推断单元：先在场景内平均种子，再进行场景块 bootstrap 和配对 Wilcoxon。
- 多重比较：20 方法乘 5 指标，共 100 个 Holm 假设。
- 审计：`complete`，失败 0。

## 判定

CAEOS 在全局五项均值中全部排名第 1，并且在 Edge-IIoT、NF-CSE-CIC-IDS2018-v2、USTC-TFC2016 三个数据集内的五项均值也全部排名第 1。当前最高支持结论为 `cross_suite_primary_mean_sota_only`；`full_sota_claim_allowed=false`。

| 指标 | CAEOS | 最强基线 | 有向增益 | bootstrap 95% CI | Holm p | 已确认 |
|---|---:|---|---:|---|---:|---|
| AUROC | 0.839183 | relative_mahalanobis 0.766636 | +0.072548 | [0.022955, 0.127961] | 0.109668 | 否 |
| AUPR | 0.737376 | knn 0.648123 | +0.089253 | [0.038151, 0.143135] | 0.019580 | 是 |
| FPR95 | 0.401565 | relative_mahalanobis 0.460292 | +0.058727 | [-0.025347, 0.146539] | 0.313835 | 否 |
| OSCR | 0.755264 | relative_mahalanobis 0.660121 | +0.095143 | [0.051478, 0.141442] | 0.000056 | 是 |
| Known macro-F1 | 0.877701 | Open-Detect 0.836475 | +0.041226 | [0.032691, 0.050310] | 7.28e-10 | 是 |

AUROC 已有正 bootstrap 区间，但没有通过全表 Holm-Wilcoxon；FPR95 同时没有通过区间和 Holm 门。论文可以写“五项均值全部第一、其中三项对最强基线确认优越”，不能写“全面显著 SOTA”。

## 主要缺口

相对全局最强的 relative Mahalanobis，AUROC 有 25 胜、13 负，FPR95 有 22 胜、16 负。最主要的场景块为：

| 场景 | AUROC 有向差 | FPR95 有向差 |
|---|---:|---:|
| NF-CSE / Infilteration | -0.330024 | -0.422510 |
| Edge / Fingerprinting | -0.131157 | -0.281843 |
| Edge / Ransomware | -0.118895 | -0.280762 |
| Edge / Backdoor | -0.085533 | -0.339573 |
| Edge / XSS | -0.015989 | -0.388212 |
| Edge / Uploading | -0.025966 | -0.220328 |

问题不是整体均值不足，而是少数场景的大幅负差扩大场景块方差并削弱秩检验。仅继续增加随机种子不会改变 38 个场景推断单元，也不能可靠修复该门。

## 固定后续动作

1. 完成保留种子 `67/71/73/79` 的 entropy、entropy-Cauchy `rank_union` 和 external relative-Mahalanobis 融合确认。
2. 按预注册内部选择树确定最终风险，并重放全部 190 个 gate 后重新执行同一 100 项 Holm 家族；不能只替换表现好的场景。
3. 若 AUROC/FPR95 仍未闭门，通过开发种子研究 NF-CSE 与 USTC 的验证集可判别专家融合，再在全新种子确认；首要诊断场景为 NF-CSE Infilteration，不能使用未知类或测试标签触发路由。
4. 24 基线终审必须使用同一个最终自有风险，并将四个经典 OOD 方法纳入 120 项 Holm 家族。
