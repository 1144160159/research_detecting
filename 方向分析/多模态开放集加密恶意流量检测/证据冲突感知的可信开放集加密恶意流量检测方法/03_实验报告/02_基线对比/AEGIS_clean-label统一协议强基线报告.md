# AEGIS clean-label 统一协议强基线报告

## 1. 适配边界

AEGIS 原方法面向标签噪声并使用训练真标签精度选 checkpoint，发布版还存在 Conv1d 通道维问题。strict-v4 clean-label adapter 保留 1D-ResNet、监督对比、密度原型伪标签纠正和 k=50 特征近邻未知评分；checkpoint 只按 known-validation Macro-F1 选择，拒绝阈值只由 known-validation 95% 分位确定。该实验评价干净已知训练下的开放集能力，不等同于原论文标签去噪主张。

14 场景协议和扩展门在结果为 0 时冻结，SHA 分别为 `6b593c2e2c09de882f692d9a06f01a2e319ea2eabe3bf6962081c90fef9e3dd9` 和 `54136f2c499c1a9b86340a517d65950108c925f348b9890c14e5d1790b9da413`。

## 2. 完整性与结果

`14/14` 场景完成、失败 0；拆分指纹和无泄漏检查均为 `14/14 PASS`。

| 方法 | Known F1 | AUROC | AUPR | FPR95 | OSCR | 四指标平均秩 |
|---|---:|---:|---:|---:|---:|---:|
| AEGIS clean-label adapter | 0.768204 | 0.834617 | 0.667903 | 0.346459 | 0.666426 | 1.00 |
| OpenDetect | 0.766127 | 0.800369 | 0.635266 | 0.350782 | 0.637880 | 2.00 |

AEGIS 相对 OpenDetect 的 AUROC/AUPR/FPR95/OSCR 有向增益为 `+0.034249/+0.032637/+0.004323/+0.028546`，四项平均 `+0.024939`；Known F1 平均/最差场景差为 `+0.002077/-0.014973`。完整性、无泄漏、Known F1、Top-2、指标广度和总体增益门均通过。

## 3. 冻结扩展决策

逐套件四指标平均增益为：CIC-IoT `-0.008442`、CIC-ToN-IoT `-0.095161`、CICIDS `+0.128716`、Edge-IIoT `+0.110982`、NF-CSE `+0.118210`、NF-UNSW `+0.020830`、USTC-TFC `-0.100566`。只有 4/7 套件非负且最差低于 `-0.05`，故跨套件稳健性门失败，`expand_to_full102=[]`。watcher 已写 `strict_v4_aegis_training_full102_seed7/not_required`。

结论是 AEGIS 在小规模开发屏幕上平均优于 OpenDetect，但跨域退化显著，不能据此进入 102 场景主表或替换冻结外部比较器。该结果支持继续使用域安全路由，而不是全局采用单一深度强基线。

远端权威产物位于 `/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717/results/strict_v4_aegis_training_pilot_seed7`；本地轻量镜像位于 `source/CAEOS-EMTD/results/strict_v4_aegis_training_pilot_seed7`。
