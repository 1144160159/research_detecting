# 098 基于多维约束表征的恶意流量噪声标签统一处理框架 / MCRe

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | 本卡 | 状态 |
|---|---|---|
| Abstract / I Introduction | 第 2 至 3 节 | 已覆盖 |
| II Related Work | 第 4 节 | 已覆盖 |
| III Problem / Constraints | 第 5 至 8 节 | 已覆盖 |
| IV Architecture | 第 9 至 13 节 | 已覆盖 |
| V Experiments | 第 14 至 20 节 | 已覆盖 |
| VI Conclusion | 第 21 节 | 已覆盖 |

## 1. 文献身份

- 标题：MCRe: A Unified Framework for Handling Malicious Traffic With Noise Labels Based on Multidimensional Constraint Representation。
- 作者：Qingjun Yuan、Gaopeng Gou、Yanbei Zhu、Yuefei Zhu、Gang Xiong、Yongjuan Wang。
- 期刊：IEEE Transactions on Information Forensics and Security，19，2024，133–146。
- DOI：10.1109/TIFS.2023.3318962。
- 数据：作者发布 Malicious_TLS，包含 22 类真实 TLS 恶意流量及 TLS 良性流量。
- 方法：autoencoder information preservation＋cluster separability＋momentum class-core proximity。
- 定位：闭集标签噪声清洗和鲁棒训练基线；不是未知攻击检测方法。

## 2. 摘要缩译

真实恶意流量标签会受标注工具、威胁情报覆盖和 0-day 影响。既有 data cleaning 偏向简单样本，可能删除 hard samples；robust training 强调全局知识，却可能在高噪声下过拟合错误标签。

MCRe 把两类任务统一为“逼近理想表征函数”，以 information integrity、cluster separability 和 core proximity 三个约束同时学习个体、类内和全局分布。在最高 90% 合成标签噪声下，论文报告清洗后 pure-sample rate 约 85%、分类 accuracy 约 82%。

## 3. 引言缩译

论文认为 task-guided 方法只围绕清洗纯度或分类准确率设计，容易选择性忽略数据知识。替代方案是 attribute-guided training：先定义理想表征应有的属性，再让网络逐步逼近。

理想表征既能保留输入信息，又使同一真实类靠近、不同类分离，并把样本拉向可信类别核心。因此同一个 representation backbone 可同时服务 MCRe-dc 与 MCRe-cls。

## 4. 噪声标签背景

错误标签来源包括标注系统不完整、不同 annotator 的分布误判、已知攻击变体与 0-day 超出规则知识。错误标签会同时污染模型训练、模型选择和真实性能评估。

现有方法：

- Data cleaning：INCV、Confident Learning、FINE、ULDC，输出更纯数据。
- Robust training：MentorNet、Co-teaching、Co-teaching+、Co-learning，直接输出噪声鲁棒分类器。

论文把 zero-day 作为标签噪声动机，但没有构造未见攻击家族测试；不能据此声称 MCRe 已解决未知攻击。

## 5. 问题定义

含噪标签数据：

> D = {(xᵢ,ỹᵢ)}ᵢ₌₁ᴺ，ỹᵢ∈{1,…,C}。

每个样本存在唯一潜在真标签 yᵢ*。理想表征 G_idl 满足：

> d(Gⁱᵈˡ(xᵢ),Gⁱᵈˡ(xⱼ))≤ε ⇔ yᵢ*=yⱼ*。

这一定义假设真实类别固定且互斥，是 closed-set label correction；无法表达一个样本属于训练 label space 外的 unknown。

## 6. Information Integrity Constraint

目标是压缩后尽量保留输入信息：

> G ← arg minᴳ [H(x)−H(G(x))]。

实际实现为 7-layer fully connected encoder G 与对称 decoder G⁻¹，重构 x̂=G⁻¹(G(x))，使用 binary cross-entropy：

> Lⁱⁱᶜ = −(1÷|D|)ΣᵢΣⱼ[xᵢⱼlog x̂ᵢⱼ +(1−xᵢⱼ)log(1−x̂ᵢⱼ)]。

原文从 entropy/mutual information 推到 reconstruction BCE 的论证较松：低重构误差是信息保留代理，不等价于严格最大化 mutual information。

## 7. Cluster Separability Constraint

先在当前 decision space 对样本聚类。对 xᵢ，类内平均距离与最近类外距离为：

> dᵢⁱⁿ = [1÷(|clusₖ|−1)]Σ(xⱼ∈clusₖ)‖uᵢ−uⱼ‖₂，

> dᵢᵒᵘᵗ = min(xⱼ∉clusₖ)‖uᵢ−uⱼ‖₂。

分离度：

> δᵢ = (dᵢᵒᵘᵗ−dᵢⁱⁿ)÷dᵢᵒᵘᵗ。

归一化后最小化：

> Lᶜˢᶜ = 1−(1÷|D|)ΣᵢNorm(δᵢ)。

该约束主要由当前无标签 cluster assignment 决定，可减弱 observed label noise，但也可能固化 early clustering error。

## 8. Core Proximity Constraint

Simple sample 定义为模型预测与 observed label 一致：

> xᵢ∈Simₖ，当 ỹᵢ=arg maxₖFₖ(uᵢ)。

每类在二次投影 z-space 中维护 momentum prototype：

> zₖ ← Norm[mzₖ+(1−m)zᵢ]，m=0.999。

样本被拉向最近类别 core：

> Lᶜᵖᶜ = (1÷|D|)Σᵢ minₖ CE(zᵢ,zₖ)。

这一“保守信任”降低高噪声影响，但预测与错误 observed label 一致的样本仍可能进入 core；90% 噪声下稳定性依赖 cluster/self-training 动力学。

## 9. 总模型

Encoder 输出 uᵢ=G(xᵢ;θ_G)，分类 head F 仍使用 observed noisy labels 计算：

> Lᶜˡˢ = CE(ỹ,F(u))。

总损失：

> L = Lⁱⁱᶜ + Lᶜˢᶜ + Lᶜᵖᶜ + Lᶜˡˢ。

论文认为表示层比分类 head 更晚过拟合标签噪声，因此即使 noisy/random labels 也可提供部分监督。该主张应以训练时长和 early stopping 消融验证，不能无限延伸。

## 10. MCRe-dc 数据清洗

根据样本到各 momentum core 的距离差计算 label confidence。远离所有可信 core 的样本被丢弃；靠近另一 core 且有高置信归属的样本可纠正标签。

实验采用固定 sample discard ratio/threshold，但正文没有充分说明该比例是否由已知注入噪声率或验证真标签确定。正式复现必须记录阈值来源、删除率和每类删除比例。

## 11. MCRe-cls 鲁棒分类

在 MCRe representation 上用 K-means 划分 cluster，再通过 Kuhn–Munkres 将 cluster 对应到类别标签，输出分类结果。

K-means 的 cluster 数等于已知 C 类，仍是 closed-set。若存在 unknown family，它会被迫进入某个已知 cluster，除非另加距离拒识或 DP mixture。

## 12. Malicious_TLS 数据集

作者从真实 edge network devices 收集 2018–2021 四年 TLS 恶意流量，用 threat intelligence 标注 22 种恶意类型，同时加入 TLS benign。为隐私删除 IP、port、timestamp、payload 等，发布 semantic、statistical、spatiotemporal features。

MCRe 把所有字段拼成统一 vector 交给 fully connected encoder。即使字段来自不同特征族，也不是 payload/sequence/statistics 三路独立 encoder 的多模态模型。

## 13. 公共数据集

核心对照使用 CICIDS2017 提供的特征，不从 PCAP 重新提取。泛化实验还包括 NSL-KDD、UNSW-NB15、LITNET-2020、IoT-23、CICMalDroid-2020。

这些数据集具有不同标签体系与特征空间，论文是分别训练/测试，不是统一 schema 的跨数据集迁移。

## 14. 合成标签噪声

噪声率从 0.1 到 0.9。两种 corruption：

- Asymmetric：每个恶意类别中按比例抽样，把标签翻为 benign。
- Symmetric：除上述恶意→benign 外，再把 benign 按比例随机翻为某一恶意类别。

所谓 symmetric 并非标准的所有类别均匀互翻，而是以 benign/attack 混淆为核心的双向噪声。该设计贴近“降低 false positive 的标注器”，但不覆盖恶意家族之间的细粒度错标。

## 15. 拆分与重复

Robust training 随机 7:3 分 train/validation；只翻转 training labels，validation 保持干净且只评估。共五次独立随机拆分，最终结果取最后五个 epoch 的平均。

Random sample split 没有按 malware family、capture、device、time 或 fingerprint grouping，四年私有流量尤其可能存在同源泄漏。把 clean validation 称为 test 也更严谨，且应另留未参与模型选择的 test set。

## 16. Data Cleaning 结果

在 Malicious_TLS 和 CICIDS2017 的 asymmetric/symmetric 噪声上，噪声率超过 20% 后 MCRe-dc 相对优势扩大。90% 噪声时清洗后 pure samples 均超过 85%，比其他方法高 25% 以上。

随噪声从低到高，MCRe-dc 清洗性能下降约 12%，其他方法至少下降 40%。论文在 90% 噪声下做 t-test，所有对比 p<0.001，但未给多重校正和 effect size。

“pure percentage”高不代表覆盖率高；固定删除率可能通过删除大量 hard samples 提纯，必须同时报告 retained fraction、class coverage 和 downstream performance。

## 17. Robust Training 结果

低噪声时 MCRe-cls 最多比最佳方法低约 1.4%；超过 asymmetric 10% 或 symmetric 20% 后通常领先。90% 噪声时 accuracy 约 82%，比对照高约 20%。

噪声率到 70% 时 accuracy 下降约 4%；到 90% 时最大下降约 18%。主要指标是 closed-set accuracy，未报告 Macro-F1、Benign FAR、per-class recall 或 open-set curves。

## 18. 消融

移除 iic、csc、cpc 任一约束均降低性能；完整 MCRe 在六种噪声场景最好。Core proximity 影响最大，去掉后某些分类 accuracy 约 70%。

训练曲线显示 reconstruction BCE 下降、NMI/ARI 上升、到类别 core 的平均距离下降。NMI/ARI 若使用 latent true labels 计算只能作为事后分析，不能作为部署时可用选择信号。

## 19. 泛化与扩展

在 NSL-KDD、UNSW-NB15、LITNET-2020、IoT-23、CICMalDroid-2020 上，asymmetric 80% 或 symmetric 50% 时 accuracy 均高于 87%。

把 MCRe representation 接到 Confident Learning 和 Co-teaching 后，高噪声下也有增益：90% 噪声时 CL pure percentage 可提高 40% 以上，Co-teaching accuracy 提高约 16%。

## 20. 统计与证据强度

五次随机实验优于单次结果，但最后五 epoch 平均会把时间点当重复观测，不能增加独立样本量。t-test 在多数据集、多噪声率、多基线下未做 family-wise correction。

更可靠方案是以相同 split/seed 为 paired unit，报告均值、标准差、paired Wilcoxon、Holm correction 和 dataset/scene-block bootstrap CI。

## 21. 结论缩译

MCRe 通过三类约束构建对标签噪声稳健的统一 representation，可用于数据清洗、聚类分类，并可插入其他 noisy-label 方法。作者把 few-shot、online detection 与 unknown attack detection 明确列为未来工作，进一步证明本文尚未完成开放集检测。

# 第二部分：独立技术分析

## A. 一句话结论

MCRe 应纳入 CAEOS 的“训练标签质量鲁棒性”附加实验，而不是未知攻击主基线；它能检验官方标签错配对三模态模型的影响，但 90% 噪声下 82% accuracy 与 95% Known Macro-F1/5% Benign FAR 安全门完全不是同一结论。

## B. 两条交付线

### 工程线

先在统一基础 CSV 上保留 immutable official label，再生成带 seed、noise matrix、noise rate 的 corrupted label column。MCRe 只读取 training corruption，validation/test official label 不变。

### 论文线

把 label noise robustness 放入附表：clean performance、noise-rate curve、retained coverage、correction precision/recall。主表的 strict OSR 仍使用官方 clean labels 和 known-only threshold。

## C. 协议审计

- Task：固定 C 类 closed-set label cleaning/classification。
- Noise：研究者知道 latent clean labels并人工注入。
- Validation：clean 30%，但无独立 test 说明。
- Split：random 7:3，无 capture/family/time grouping。
- Cleaning threshold：固定 discard ratio，选择来源不清。
- Unknown：没有 unknown family；列为 future work。
- Protocol：`P1-closed-set-synthetic-label-noise/P3-random-split-clean-validation-and-discard-threshold-unclear`。

## D. 与官方标签对齐工作的关系

CAEOS 当前基础数据集必须以官方 label 为唯一 ground truth，并记录未匹配/删除原因。MCRe 不能用于“自动改写官方标签”后再把改写结果当真值。

合理用途是：

- 把官方标签保留为 evaluation truth。
- 仅对 training copy 注入可复现噪声。
- 评估标签对齐误差对 encoder、prototype、threshold 与 conflict 的传播。
- 输出 suspect label 清单供人工审计，不直接覆盖基础 CSV。

## E. 三层指标

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | Accuracy | Macro-F1、BA、per-class Recall、Benign FAR | 明显不足 |
| 未知检测 | 无 | AUROC、AUPR-Out、FPR95、Unknown-F1 | 缺失 |
| 联合开放集 | 无 | OSCR、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 无 | ECE、Brier、NLL、risk reliability | 缺失 |
| 标签清洗 | Pure percentage | purity、coverage、correction P/R、class retention | 仅部分 |

## F. 与证据冲突的关系

训练标签错误会让某一模态与标签冲突，但这不同于多模态之间互相冲突。MCRe 的 cluster/core distance 可作为 label-quality risk；CAEOS 的 modality conflict 应独立建模。

需要四组消融：无噪声、标签噪声、模态损坏、标签噪声＋模态损坏。只有在后二者交叉场景保持三层指标，才能说明 conflict-aware training 不是单纯 noisy-label regularization。

## G. 多模态判断

Malicious_TLS 发布 semantic/statistical/spatiotemporal features，但 MCRe 将其统一成一个 vector，由单一 FC encoder 处理。论文没有视图专属 encoder、证据融合或 modality disagreement，因此不是 CAEOS 所需三模态算法。

## H. 采纳与否决

### 采纳

- Asymmetric malicious→benign 噪声模型。
- Label cleaning＋robust training 双任务。
- Reconstruction、cluster separation、class core 三项消融。
- 与 CL/Co-teaching 组合。
- 噪声率曲线和五种子。

### 有条件采纳

- Core prototype 只由高置信 training samples 更新。
- Cleaning threshold 只能用 known training/validation，不能看 test truth。
- K-means 分类需另加 unknown rejection 才能用于 OSR。

### 不采纳

- 不改写官方基础标签。
- 不用 latent true test labels 选 cleaning threshold。
- 不把 82% accuracy 解释为未知攻击效果。
- 不把字段集合称为多模态模型。
- 不省略删除覆盖率与删除原因。
- 不把最后五 epoch 当五个独立重复。

## I. CAEOS 可执行实验

1. `E-NOISE-01`：0/5/10/20/40% malicious→benign 噪声。
2. `E-NOISE-02`：benign↔malicious 与 family↔family confusion matrix。
3. `E-NOISE-03`：MCRe、CE、GCE、Co-teaching、Confident Learning。
4. `E-NOISE-04`：cleaning purity、coverage、correction P/R、per-family retention。
5. `E-NOISE-05`：clean/噪声下三层 OSR 指标与 ECE。
6. `E-NOISE-06`：标签噪声与单模态损坏二因素实验。
7. `E-NOISE-07`：official label suspect list 人工核查，不覆盖 ground truth。
8. `E-NOISE-08`：场景×种子配对检验和 block bootstrap。

## J. 可引用与不可引用主张

### 可引用

- MCRe 统一 data cleaning 与 robust training。
- 三约束为 information integrity、cluster separability、core proximity。
- Malicious_TLS 含 22 种真实 TLS 恶意流量并覆盖 2018–2021。
- 90% 合成噪声时清洗 purity 约 85%、分类 accuracy 约 82%。
- Unknown attack detection 被作者列为未来工作。

### 不可引用

- MCRe 已检测 0-day/unknown attacks。
- 90% 噪声 robustness 等同 open-set robustness。
- Random 7:3 split 排除同源泄漏。
- Pure percentage 高即清洗质量全面更好。
- Semantic/statistical/spatiotemporal 字段使 MCRe 成为多模态网络。
- Clean validation 等同独立 test。

## K. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过
- G2 身份门：通过至 IEEE/DOI，Zotero 待办
- G3 任务门：通过
- G4 协议门：通过，`P1-closed-set-synthetic-label-noise/P3-random-split-clean-validation-and-discard-threshold-unclear`
- G5 方法门：通过
- G6 结果门：通过，清洗、分类、消融、泛化、扩展已核读
- G7 对比门：通过
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
