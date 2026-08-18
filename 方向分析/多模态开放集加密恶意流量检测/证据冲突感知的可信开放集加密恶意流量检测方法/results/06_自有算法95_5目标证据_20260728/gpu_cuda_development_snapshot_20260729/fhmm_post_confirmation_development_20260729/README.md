# FHMM 稳定确认后的开发裁决

更新时间：2026-07-29

本目录保存 FHMM-SR-CAEOS 在 split43/47 稳定确认失败后的三组轻量、只读开发证据。所有训练与正式评价均在远端 A6000 GPU 服务器执行；本地仅同步 JSON/日志、核验 SHA256 和更新文档。三组结果均为阴性开发结果，不得进入论文确认主表，也未触发六个未见攻击家族的扩展训练。

## 证据索引

| 本地子目录 | 远端结果目录 | 搜索/变更 | 物理 SHA256 |
|---|---|---|---|
| `attack_routing_v3` | `results/strict_v4_fhmm_attack_routing_development_v3` | 4种攻击分数源 × 3种聚合 × 3个告警预算，共36组 | `development.json`: `e5899865...3e95c` |
| `joint_alert_v4` | `results/strict_v4_fhmm_joint_alert_development_v4` | 3种告警规则 × 3种开放分数聚合 × 3个告警预算，共27组 | `development.json`: `ec7b3d3b...bf22` |
| `known_split_70_10_20_v1` | `results/strict_v4_fhmm_70_10_20_development_v1` | 已知类由60/20/20改为70/10/20；split43/47各3个初始化 | protocol文件 `521c363f...12`；development文件 `70e716b0...b69`；completion文件 `66d0b0be...d6f` |

## 结果与裁决

### 1. 攻击路由 v3

- 36组配置中，双拆分用户预警门通过数为 `0`，双拆分已知/未知告警门通过数为 `0`。
- 选中开发配置为 family attack score、mean聚合、`0.049`告警预算、open maximum、`0.04`开放预算、validation-best类型成员。
- 双拆分均值：Alert Accuracy `0.954651`、Benign FPR `0.037377`、Known type Accuracy `0.952355`、Unknown alert Recall `0.814634`、Unknown rejection Recall `0.426423`。
- 最坏拆分：Alert Accuracy `0.922844`、Benign FPR `0.039492`、Known type Accuracy `0.950449`、Unknown alert Recall `0.668293`、Unknown rejection Recall `0.372358`、AUROC-Out `0.886194`、OSCR `0.883679`。
- 裁决：仅调整攻击分数来源、聚合与阈值不能修复跨拆分未知告警稳定性，关闭该局部搜索路线。

### 2. 联合告警 v4

- 27组配置中，双拆分用户预警门通过数为 `0`，双拆分已知/未知告警门通过数为 `0`；仅 `9` 组达到研究层最低门。
- maximum/noisy-or 将开放风险并入告警后反而恶化 split47，最终选择退回 attack-only，数值与攻击路由 v3 的选中配置相同。
- 裁决：简单 maximum/noisy-or 融合不能把开放排序优势稳定转成未知攻击告警，关闭该路由。

### 3. 已知类 70/10/20 v1

- 训练前冻结协议；未知样本仍全部只用于测试，阈值仍只由 known-only validation 拟合。
- 双拆分均值：Alert Accuracy `0.925989`、Benign FPR `0.040141`、Known type Accuracy `0.954682`、Unknown alert Recall `0.685366`、Unknown rejection Recall `0.330894`。
- 联合研究指标均值：Known Macro-F1 `0.956383`、Balanced Accuracy `0.965483`、AUROC-Out `0.848037`、AUPR-Out `0.610522`、`FPR_known@95TPR_unknown=0.344434`、OSCR `0.843393`。
- 最坏拆分：Alert Accuracy `0.901496`、Benign FPR `0.040845`、Known type Accuracy `0.945291`、Unknown alert Recall `0.573171`、Unknown rejection Recall `0.260976`、AUROC-Out `0.790634`、OSCR `0.782668`。
- 六个成员完整性门和资源门全部通过，成员平均GPU利用率为 `66.53%–85.47%`，峰值均为 `100%`。
- 裁决：增加已知训练样本没有改善未见家族表征，反而显著降低未知告警、未知拒识和开放集排序；拒绝70/10/20替换。

## 使用边界

- Botnet 已用于开发架构和配置选择，必须降级为开发未知类。后续若有候选通过开发门，最终确认只能使用与 Botnet 不相交的 BruteForce、DDoS、DoS、Exploit、Reconnaissance、WebAttack 未见家族。
- 主判断使用逐拆分 `Alert Accuracy >= 0.95` 且 `Benign FPR < 0.05`，并同时报告 Unknown alert Recall；不能用跨拆分均值、Known type Accuracy、AUROC 或 OSCR 替代操作门。
- 以上实验不证明完整未知攻击类型识别达到95%，也不构成SOTA结论。
