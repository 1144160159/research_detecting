# 039 面向加密流量指纹的鲁棒开放集分类 / Robust Open-Set Classification for Encrypted Traffic Fingerprinting

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | 本文对应内容 | 覆盖状态 |
|---|---|---|
| Abstract / 1 Introduction | 第 2 至 3 节 | 已覆盖 |
| 2 Background | 第 4 至 6 节 | 已覆盖 |
| 3 Robust Open-set Framework | 第 7 至 10 节 | 已覆盖 |
| 4 Results | 第 11 至 15 节 | 已覆盖 |
| 5 Related Work | 第 16 节 | 已覆盖 |
| 6 Conclusion / Appendices | 第 17 节 | 已覆盖 |

## 1. 文献身份

- 标题：Robust open-set classification for encrypted traffic fingerprinting。
- 中文题名：面向加密流量指纹的鲁棒开放集分类。
- 作者：Thilini Dahanayaka、Yasod Ginige、Yi Huang、Guillaume Jourjon、Suranga Seneviratne。
- 期刊：Computer Networks，236，109991，2023。
- DOI：10.1016/j.comnet.2023.109991。
- 方法：regularized classifier、k-Logit Neighbor Distance（k-LND）和 int8 post-training quantization。
- 任务定位：目标网站、视频或语音命令的已知类别分类，同时拒绝其他背景类别；不是恶意/良性攻击检测。

## 2. 摘要缩译

加密流量会通过 packet size、direction 和 timing 泄露内容，traffic fingerprinting 可识别网站、视频和应用活动。以往方法多采用 closed-set 假设，实际部署却需要识别目标类并拒绝任意背景流量。

论文提出三部分框架：更充分正则化 closed-set classifier；利用 logit 空间类中心距离进行开放集拒识的三种 k-LND；把模型权重量化为 int8 以适配交换机等受限设备。五个数据集上，作者报告量化后的 k-LND 相对其他开放集方法提高 F-Score 8.9% 至 77.3%。

## 3. 引言缩译

作者以 Tor 目标网站监控为例：执法方只关心目标列表中的网站，其他网站均应拒为 background。普通 closed-set classifier 会把所有背景访问强制归到目标网站，造成大量误报。

已有方案包括训练 background class、额外 binary filter、softmax threshold。它们可能需要一部分 known-unknown 样本，且训练时可见的背景无法覆盖未来全部 unknown-unknown；softmax 又可能对错误样本高置信。

论文同时考虑在 P4/Juniper 等网络设备部署。int8 量化可减少内存并避免浮点运算，因此作者把表示正则、开放集距离和量化联合研究。

## 4. 对比开放集方法

### 4.1 Background Class

从开放集抽取 known-unknown classes，作为一个 background class 参与训练。它明确使用辅助未知样本，属于 exposure protocol，且假设这些样本代表未来 unknown。

### 4.2 Softmax Threshold

若最大 softmax probability 低于阈值，则拒为 unknown。原文指出阈值可借助 known-unknown 数据选择，但 softmax 对 OOD 可能高置信。

### 4.3 OpenMax

OpenMax 在 correctly classified training activations 上估计 class MAV，并用 EVT 建模到类中心的尾部距离。论文针对 traffic 数据缩短 activation vector，并使用 class-wise thresholds，避免一个 global threshold 对低置信类别产生不公平拒绝。

### 4.4 Ensemble

训练多个模型并平均输出，再对 confidence 阈值拒识。其成本高于单模型方法。

## 5. 五个数据集

| 数据集 | 指纹任务 | 已知目标类 | 原始/构造开放集 |
|---|---|---:|---|
| AWF | Tor 网站 | 200 | 400,000 background classes/traces 体系 |
| DF | Tor 网站 | 95 | 40,716 open-set samples/classes 体系 |
| DC | YouTube 视频 | 10 原始类 | 40% 类作 known，其余 unknown |
| SETA | Netflix 视频 | 20 原始类 | 40% 类作 known，其余 unknown |
| IoT | Google Home 语音命令 | 98 原始类 | 40% 类作 known，其余 unknown |

AWF/DF 使用上传为 +1、下载为 −1 的 packet-direction sequence；DC/SETA 把三分钟划为 500 个时间槽，只保留 uplink packet count；IoT 使用前 475 个 packet directions。

这些都是内容/活动指纹数据，没有 benign、malicious、attack family 语义。

## 6. 数据拆分

DC、SETA、IoT 按类别构造 unknown：40% classes 为 known，其余为 open set。DC/SETA 做 5 个随机 class splits，IoT 做 10 个，并报告均值和标准差。

除另有说明，每个 known class 使用 200 train、100 validation、200 test traces。Background-class 方法另从 20% unknown classes 中取每类 200 train、100 validation samples 作为 known-unknown，并保证用于训练的 unknown classes 与 open-set test classes 不重叠。

这说明 background baseline 是 P1 auxiliary-unknown，而 k-LND 本身可按 P0 known-only 运行，二者不能混为同协议比较。

## 7. 正则化闭集分类器

作者认为 open-set 性能依赖 closed-set feature boundary。模型即使在 known test 上准确，也可能因过拟合把大量空白区域纳入类别边界，从而接受 unknown。

对 DC、SETA 和 IoT，论文增大 dropout rate，并只依据 validation accuracy 选择正则化配置。AWF/DF 沿用已充分调参的原模型。

正则化前后 closed-set accuracy 基本不变：DC 99.08%→99.82%，SETA 98.17%→98.87%，IoT 97.49%→97.33%，但多数开放集方法的综合 F-Score 改善。

## 8. k-LND 表示

设 closed-set 有 N 类，取 softmax 前 N 维 logits 作为表示。对类别 c，只使用训练集中被 classifier 正确分类的样本计算 Mean Activation Vector：

> MAV꜀ = Mean{θ(x) ∣ x 属于类别 c 且预测正确}。

对输入 x，令 p 为 closed-set predicted class，dᵢ 为 x 到 MAVᵢ 的 Euclidean distance。三种 score 为：

> D₁ = dₚ。

> D₂ = Σᵢ₌₁…ₖ(dᵢ − dₚ)，其中 i ≠ p。

> D₃ = dₚ ÷ Σᵢ₌₁…ₖ dᵢ，其中 i ≠ p。

k-LND1 只看 predicted-class distance；k-LND2/3 同时利用邻近 class centers，要求 known sample 靠近自身中心并远离其他中心。原文认为 D₃ 的相对距离在不同数据集和量化扰动下更稳定。

## 9. 类条件阈值

对每个类别 c，把 known validation samples 按 closed-set prediction 分组，计算对应 D 值并取第 90 百分位：

> τ꜀ = Quantile₀.₉₀{D(x) ∣ x 来自 known validation 且预测为 c}。

推理规则为：

> 接受为类别 p，当 D(x) ≤ τₚ。

> 拒为 unknown，当 D(x) > τₚ。

MAV 使用 known training，τ 使用 known validation，k-LND 无需 target unknown。这是论文最值得 CAEOS 复用的协议设计。

## 10. 量化

使用 TensorFlow post-training integer quantization，把模型权重映射为 int8。模型缩小至少 60%，例如 AWF 从 8.51 MB 降到 2.14 MB、DF 从 8.30 MB 降到 2.08 MB。

论文比较量化前后各种 open-set score 的稳定性，认为相对 logit distance 比 background/softmax/OpenMax 更耐受量化误差。

## 11. 指标定义

原文报告：

- Closed-set accuracy：known samples 被正确分类为具体 known class 的比例。
- Open-set accuracy：unknown samples 被正确拒识的比例，即 unknown rejection rate。
- Micro F-Score：把所有 known classes 与一个 unknown class 合并计算。

Micro precision、recall 与 F-Score 为：

> P微 = ΣᵢTPᵢ ÷ Σᵢ(TPᵢ + FPᵢ)。

> R微 = ΣᵢTPᵢ ÷ Σᵢ(TPᵢ + FNᵢ)。

> F微 = 2P微R微 ÷ (P微 + R微)。

作者承认 unknown 规模远大于单个 known class，F-Score 会被 unknown performance 主导。它不等价于 Macro-F1、Unknown-F1 或 OSCR。

## 12. 非量化 k-LND 结果

| 数据集 | k-LND1 Closed/Open | k-LND2 Closed/Open | k-LND3 Closed/Open |
|---|---:|---:|---:|
| AWF | 89.37/85.43 | 89.88/88.12 | 97.98/89.23 |
| DF | 88.45/83.99 | 88.29/88.04 | 97.84/87.21 |
| DC | 91.63/87.78 | 94.24/86.26 | 94.51/86.92 |
| SETA | 85.41/84.69 | 85.21/85.16 | 95.42/87.84 |
| IoT | 85.62/65.92 | 85.49/76.19 | 97.33/74.47 |

k-LND3 的 closed accuracy 始终较高，但并非每个数据集 open accuracy 最优：DC 的 k-LND1 更高，IoT 的 k-LND2 更高；DF 的 background class 达到 95.20/97.40，也强于 k-LND3，但它使用 auxiliary unknown。

## 13. 正则化结果

增加 dropout 后，四种既有 OSR 方法的 F-Score 提升 2.99% 至 35.48%。但 improvement 不一致，例如 DC OpenMax 的 open accuracy 从 92.16% 降为 91.11%，closed accuracy同时上升。

这支持“更好闭集表示通常有益”，不支持 closed-set accuracy 与 unknown rejection 必然同步。

## 14. 量化结果

量化后的 k-LND3 Closed/Open accuracy 为：AWF 97.98/84.02、DF 97.98/87.22、DC 94.21/87.92、SETA 89.58/70.74、IoT 95.98/76.17。

量化会导致部分性能下降，但 k-LND 仍比多数对比方法稳定。作者按 F-Score 比较得到相对最佳 baseline 提升 8.9% 至 77.3%；这是相对增幅，不是 accuracy 提升百分点。

## 15. 结果分析缩译

Background class 的量化脆弱性来自 auxiliary unknown 被压入一个人工类别，参数离散化可能改变其边界。OpenMax 的 Weibull tail fit 和 softmax probability 也会放大量化造成的 activation error。

k-LND 使用 Euclidean relative distances，D₂/D₃ 中 predicted center 与其他 centers 的误差可部分抵消，因此更稳定。

## 16. 相关工作缩译

论文回顾 website/video/voice fingerprinting、background class、confidence rejection、OpenMax、ensemble，以及 OSR 中的 reconstruction、prototype 与 distance 方法。其贡献不是新 encoder，而是把 known-only class-conditional logit distance 与网络设备量化结合。

## 17. 结论缩译

论文证明良好正则化对开放集有帮助，k-LND 在五个指纹数据集上较稳定，int8 量化可显著缩小模型。方法适合资源受限流量指纹识别，但未研究恶意攻击家族、跨数据集 domain shift、概率校准或现代 OSR 排序指标。

# 第二部分：独立技术分析

## A. 一句话结论

k-LND3 是 CAEOS 应正式实现的 P0 class-conditional distance baseline；其阈值严格来自 known validation，但原文 90% quantile 与 95% Known Acceptance 安全门冲突，必须改为预注册的 95% quantile 对照而不能用 unknown test 选取。

## B. 两条交付线映射

### 工程线

在完全相同 encoder/logits 上实现 k-LND1/2/3；只用 correctly classified known training 计算 MAV，用 known validation 计算每类 τ。保留原论文 q = 0.90 复现线，并新增 q = 0.95 的 CAEOS 验收线。

### 论文线

把 k-LND 放在 `P0 known-only distance` 基线组。Background class 另列 `P1 auxiliary unknown`，不得按一个无暴露协议排名。

## C. 协议审计

- k-LND training：只使用 known classes。
- MAV：只用 correctly classified known training samples。
- threshold：只用 known validation，第 90 百分位，未使用 target unknown。
- unknown test：类别与 known 不重叠。
- model regularization：依据 known validation accuracy 调 dropout。
- k hyperparameter：大类数时需要选择，但具体 validation 规则未充分报告。
- split：DC/SETA/IoT 做多个 class splits；trace 是否按 capture/session/group 隔离未说明。
- AWF/DF：沿用原 open set，类别与采集身份隔离仍依赖原数据协议。
- protocol grade：`P0-known-only-class-conditional-distance/P3-k-and-trace-grouping-unclear`。

## D. 90% 阈值与 95%/5% 门

τ 为 known distance 的 90% quantile，理论上会在同分布 validation 上拒绝约 10% known samples，无法满足 Known Acceptance ≥ 95%。其 reported closed accuracy 还同时受分类错误和拒识影响，多数数据集 k-LND3 过 95%，但 DC 94.51% 未过线。

CAEOS 应固定两个运行点：

- 文献复现：q = 0.90。
- 安全验收：q = 0.95，使 known validation acceptance 目标为 95%。

两者都不能依据 unknown AUROC 或 unknown rejection 回调。

## E. 与恶意流量任务的差异

原文 unknown 是非目标网站、视频或语音命令，不是未知攻击家族；所有类别都可能是正常用户活动。因此其 open accuracy 证明“背景内容拒识”，不能证明 unknown malicious detection。

在 CAEOS 中，benign 是明确 known class，known malicious families 需要正确细分，held-out malicious families 才是 unknown。标签语义和错误代价都不同。

## F. k-LND 的局限

- Logit dimension 等于 known class count，场景变化后距离空间也变化。
- Euclidean distance 对 logit scale、temperature 和共同平移敏感。
- MAV 假设每类近似单中心，对多簇 capture/device/domain 分布可能失效。
- 只用 correctly classified samples 会忽略困难 known 子群。
- 第 90/95 quantile 在少样本类上估计不稳定。
- k-LND2 的差值可为负，score 方向与数值尺度跨类不稳定。
- k-LND3 分母受邻居数量影响，k 的选择必须冻结。
- 强 identity shortcut 可形成紧簇并产生虚假的开放集性能。

## G. 三层指标映射

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | Closed accuracy | Macro-F1、BA、per-class Recall、Benign FAR | 不足 |
| 未知检测 | Open accuracy | AUROC、AUPR-Out、FPR95、Unknown-F1 | 仅一个运行点 |
| 联合开放集 | Micro F-Score | OSCR、OpenAUC、Known Acceptance、Unknown Rejection | 不等价 |
| 校准 | 无 | ECE、Brier、NLL | 缺失 |

## H. CAEOS 采纳与否决

### 采纳

- 采纳 correctly classified training MAV。
- 采纳 class-conditional known-only quantile threshold。
- 采纳 k-LND1 与 k-LND3，k-LND2 作为补充。
- 采纳同 encoder 下 softmax、OpenMax、ensemble、k-LND 对照。
- 采纳模型量化作为部署附加实验。

### 有条件采纳

- q = 0.90 只用于复现，q = 0.95 用于安全门。
- 多中心 prototype/Mahalanobis 与单 MAV 对照。
- class sample 太少时报告 quantile CI 或使用 pooled shrinkage。
- int8 量化只在 float 模型定稿后开展。

### 不采纳

- 不用 target unknown 选择 k、q 或 score 方向。
- 不把 background class 与 k-LND 放在同协议无标识比较。
- 不把 open accuracy 写成 Unknown AUROC。
- 不把指纹 background rejection 写成未知恶意攻击检测。
- 不用 Micro F-Score 替代三层指标。

## I. CAEOS 可执行实验

1. `E-KLND-01`：MSP、MLS、Energy、k-LND1、k-LND3、Mahalanobis 同 encoder 比较。
2. `E-KLND-02`：q = 0.90 文献复现与 q = 0.95 安全验收双运行点。
3. `E-KLND-03`：global threshold 与 class-conditional threshold。
4. `E-KLND-04`：single MAV、multi-prototype、class covariance 三种几何假设。
5. `E-KLND-05`：logit、normalized logit、penultimate embedding 三种空间。
6. `E-KLND-06`：每类 correctly classified sample 数量与 quantile stability。
7. `E-KLND-07`：float32、float16、int8 对已知/未知/OSCR/校准的影响。
8. `E-KLND-08`：5 seeds、leave-family-out、scenario-block bootstrap 与 Holm-Wilcoxon。

## J. 对自有算法的直接判断

k-LND3 可检验“复杂 conflict fusion 是否真的优于简单 class-conditional distance”。若 CAEOS 不能稳定超过 k-LND3 的 Unknown AUROC、FPR95 与 OSCR，同时保持 Known Macro-F1，则自有风险融合缺乏必要性证据。

已知 Macro-F1 未过 95% 时，首先修复 encoder 和类别边界；k-LND 只在分类后执行拒识，无法纠正本来就被错分的 known samples。误报率高时则比较 global 与 class-conditional threshold，判断是否是统一阈值造成。

## K. 可引用与不可引用主张

### 可引用

- k-LND 用 logit class centers 和 class-conditional known-validation thresholds 拒识。
- 原文阈值为每类 known validation distance 的第 90 百分位。
- k-LND 本身不需要 target unknown 训练样本。
- k-LND3 在五个数据集保持较高 closed/open accuracy，但并非每项均最优。
- int8 量化可把模型大小减少至少 60%。

### 不可引用

- k-LND 已证明适用于未知恶意攻击。
- 原文 90% threshold 满足 95% Known Acceptance。
- Open accuracy 等于 AUROC 或 OSCR。
- background class 是 P0 unknown-blind 方法。
- k-LND3 在所有数据集的 unknown rejection 都最好。
- 量化后的网络已在真实 P4/Juniper 设备部署验证。

## L. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过，本地全文抽取存在
- G2 身份门：通过至期刊和 DOI，Zotero 待办
- G3 任务门：通过，指纹拒识与未知恶意检测已区分
- G4 协议门：通过，`P0-known-only-class-conditional-distance/P3-k-and-trace-grouping-unclear`
- G5 方法门：通过，三种 score、MAV、threshold 和 quantization 已核读
- G6 结果门：通过，表 1 至 8 与附录指标解释已核读
- G7 对比门：通过，P0/P1 方法已拆分
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
