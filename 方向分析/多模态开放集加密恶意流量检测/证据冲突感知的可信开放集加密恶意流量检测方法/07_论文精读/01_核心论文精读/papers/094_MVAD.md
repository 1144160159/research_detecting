# 094 多视图深度异常检测：系统探索 / MVAD

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | 本卡 | 状态 |
|---|---|---|
| Abstract / I Introduction | 第 2 至 3 节 | 已覆盖 |
| II Related Work / III Formulation | 第 4 至 5 节 | 已覆盖 |
| IV Proposed Baselines | 第 6 至 10 节 | 已覆盖 |
| V Benchmark Datasets | 第 11 节 | 已覆盖 |
| VI Evaluation / VII Discussion | 第 12 至 16 节 | 已覆盖 |
| VIII Conclusion | 第 17 节 | 已覆盖 |

## 1. 文献身份

- 标题：Multiview Deep Anomaly Detection: A Systematic Exploration。
- 作者：Siqi Wang、Jiyuan Liu、Guang Yu、Xinwang Liu、Sihang Zhou、En Zhu、Yuexiang Yang、Jianping Yin、Wenjing Yang。
- 期刊：IEEE Transactions on Neural Networks and Learning Systems，35(2)，2024，1651–1663。
- DOI：10.1109/TNNLS.2022.3184723。
- 方法：11 个多视图深度单类异常检测基线的系统比较。
- 定位：CAEOS 多模态融合、对齐、视图质量与消融设计的理论/实验依据；不是网络恶意流量专用方法。

## 2. 摘要缩译

现代对象常由多个传感器、模态或观察角度共同描述，但深度异常检测与多视图学习的交叉长期缺少正式定义。论文首次形式化“多视图深度异常检测”，系统设计 11 个基线，并把公开数据加工为 30 多个多视图 benchmark。

作者在图像、视频和既有多模态数据上综合评估，结论不是某个复杂模型全面胜出，而是简单平均融合经常很强、不同数据集的最佳方法差异大、盲目融合冗余视图甚至劣于最佳单视图。

## 3. 任务边界

论文严格区分：

- AD：训练只给纯 normal class，测试判断 normal/abnormal，属于半监督单类学习。
- OD：直接从受污染无标签数据中找 outlier，属于无监督任务。
- Multiview OD：还可检测跨视图不一致，但训练设定不同。

因此本文的 multiview deep AD 与 CAEOS 的 unknown rejection 有共性，但不包含“Benign＋已知攻击家族”的多类 closed-set discrimination。

## 4. 相关工作缩译

深度 AD 包括 DAE、GAN、Deep SVDD、自监督几何变换和 pseudo-outlier。多视图学习主要分 fusion 与 alignment：前者生成 joint representation，后者强化跨视图共同结构。

既有 multiview OD 多从污染数据中用聚类结构找 attribute/class outlier，不能直接替代只用纯 normal 训练的 AD。作者因此以统一任务重新适配并比较这些路线。

## 5. 形式化定义

给定 normal class Cₙ，训练样本由 V≥2 个视图构成：

> x = {x⁽ᵛ⁾}ᵥ₌₁ⱽ，且 x⁽ᵛ⁾∈Cₙ。

模型 Mθ 输出正常性分数 S(x)，再由阈值二分：

> Mθ(x) = 1，当 x∈Cₙ；否则 Mθ(x) = 0。

各视图允许异构维度与张量结构。该定义强调观察对象必须配对，即不同视图描述同一个样本。

## 6. 融合式基线

每个视图先由独立 encoder 得到：

> h⁽ᵛ⁾ = Enc⁽ᵛ⁾(x⁽ᵛ⁾)。

再用融合函数生成 joint representation：

> h = Fᶠ({h⁽ᵛ⁾}ᵥ₌₁ⱽ)。

每个 decoder 从 h 重构对应视图，训练损失为：

> Lᵣ = Σᵥ₌₁ⱽ ‖x⁽ᵛ⁾ − x̂⁽ᵛ⁾‖₂²。

四种 early/joint fusion：

- SUM：h = (1÷V)Σᵥh⁽ᵛ⁾。
- MAX：逐维取 max。
- NN：拼接后经全连接网络映射。
- TF：外积张量融合，再用 low-rank decomposition 降低指数复杂度。

测试异常分数来自各视图重构误差；需要 late fusion 时默认取平均。

## 7. 对齐式基线

Alignment 不强制生成单一 joint embedding，而是最小化：

> L = Lᵣ + αLₐ。

作者比较三类跨视图约束：

- DIS：同一样本各视图 embedding 的 Lₚ distance。
- SIM：同样本相似、不同样本至少相隔 margin m 的 hinge objective。
- DCCA：最大化两个视图 embedding covariance 的 canonical correlation。

对齐仍以 reconstruction score 检测异常。DCCA 跨 batch 估计 covariance，表现比 DIS 更不稳定。

## 8. 深度 AD 适配基线

对每个视图独立训练 AD 模型，测试时融合分数：

> S(x) = Fˡ(S⁽¹⁾, S⁽²⁾, …, S⁽ⱽ⁾)。

论文适配：

- DAE：以负 reconstruction error 为 normality score。
- DSVDD：使 normal embedding 靠近非零中心 c⁽ᵛ⁾，分数为负平方距离。

还把 MODDIS 与 CAAE 从污染式 multiview OD 改为 pure-normal training，作为补充参照。

## 9. 自监督跨视图预测

作者把视图索引划分为输入集合 P 与预测集合 Q，从 P 的表示预测 Q：

> hᴾ = Fᶠ({h⁽ⁱ⁾}ᵢ∈P)，

> Lᵖʳᵉᵈ = Σⱼ∈Q ‖Dec⁽ʲ⁾(hᴾ) − x⁽ʲ⁾‖₂²。

两种生成式 pretext task：

- PPRD：其余视图预测单个目标视图，轮换目标。
- SPRD：单个视图预测全部视图，轮换输入。

其优势是显式学习 view correspondence；其风险是某视图可由捷径预测时，低误差未必代表安全语义。

## 10. Late Fusion

默认平均：

> Fˡ(S⁽¹⁾,…,S⁽ⱽ⁾) = (1÷V)Σᵥ₌₁ⱽS⁽ᵛ⁾。

论文另比较 max 与 min。平均总体最好；min 也常可接受，符合“任一视图异常即可提高风险”的直觉；max 在 Citeseer/Cora 等数据上可能很差。

重要的是，作者不使用负类验证来学习融合权重。这为 CAEOS 的 known-only fusion selection 提供了直接协议参考。

## 11. 数据集构建

论文构建与收集 30 多个多视图任务，主要来自：

- 小图像：颜色直方图、GIST、两种 HOG、LBP、SIFT 六视图。
- 高分辨率图像：VGG、InceptionV3、ResNet34、DenseNet121 的 penultimate embeddings 四视图。
- 视频：RGB appearance 与 FlowNetV2 optical flow 两视图。
- 既有多模态：Citeseer、Cora、Reuters、BBC、Wiki、BDGP、Caltech20、AwA、NUS-Wide、SunRGBD、YoutubeFace、CMU-MOSEI、DriverAD。

非 AD 专用多类数据按 one-versus-all：每轮一类 normal，其余类全部 abnormal；至少要求 normal class 有 300 个训练样本。

## 12. 拆分与预处理

有官方 split 的数据直接使用；无 split 的数据随机取当前 normal class 70% 训练，剩余 normal 与所有 negative 测试，重复 10 次。

训练每个视图按训练集 min/max 归一化到 [−1,1]，测试沿用训练统计。重构误差还除以输入维度，使不同视图的 score scale 更可比较。

该预处理原则合格，但 image/video patch 之间仍可能有对象、视频或时间邻接泄漏，论文并未针对网络流量的 connection/capture grouping 问题给出答案。

## 13. 指标

使用三个 threshold-independent 指标：

- AUROC。
- AUPR。
- TNR@95%TPR。

论文把 normality 作为正类，因此 95% TPR 表示 95% normal acceptance，TNR 表示 abnormal rejection。该指标可直接映射 CAEOS 的 95% Known Acceptance operating point，但不等于 Benign FAR，因为本文 normal class 不含“已知攻击家族”。

## 14. 主结果缩译

11 个基线在 28 个汇总数据集上没有统一赢家。主要观察：

- PPRD/SPRD 在 16/28 个数据集达到最优或与最优无显著差异，但在 UCSDped1、ShanghaiTech 等场景明显落后。
- SUM/MAX 等简单融合与 NN/TF 复杂融合总体接近，SUM 反而最稳定。
- DIS alignment 稳定，DCCA 波动较大。
- DAE 是强基线；DSVDD 多数任务较弱，仅在个别数据上最好。
- 从污染 OD 适配的 MODDIS/CAAE 表现不稳定，CAAE 通常强于 MODDIS。

## 15. 关键失败模式

在 26 个可比较数据集中的 12 个，最佳多视图基线仍劣于事后挑选的最佳单视图。这说明：

- 多视图不自动带来增益。
- 冗余或低质量视图会稀释有效证据。
- 无负类验证时，视图质量与融合权重很难可靠学习。
- 复杂 fusion 并不自动优于平均。

最佳单视图是 hindsight oracle，部署时不可得，但它揭示了多视图方法仍未充分提取互补信息。

## 16. 敏感性与统计分析

TF rank R、SIM margin m、alignment weight α 分别在给定网格内变化，多数场景 AUROC 波动小于 1%，说明单纯调参难以带来突破。

随机拆分数据表以 Student t-test 检查与最佳方法的差异，p<0.05 视为显著。该检验没有多重比较校正，也不是 CAEOS 所需的场景×种子 paired Wilcoxon/Holm 方案。

## 17. 结论缩译

论文完成多视图深度 AD 的问题定义、基线族和 benchmark 建设。实验证明该问题尚无“killer approach”，自监督跨视图预测有潜力，但 view contribution estimation、冗余抑制与 informed fusion 仍是核心难题。

# 第二部分：独立技术分析

## A. 一句话结论

MVAD 是 CAEOS 多模态路线最重要的负面证据之一：三模态不是把三个 encoder 拼接就成立，必须证明每个模态独立贡献、冲突机制优于简单平均、融合结果不劣于最佳单模态，并在严格 known-only 阈值下报告联合 OSR。

## B. 两条交付线

### 工程线

把 SUM、MAX、concat-MLP、late-average、late-min、cross-view prediction、distance alignment 建成统一三模态基线；所有 encoder、normalizer、融合参数和阈值仅使用 known training/validation。

### 论文线

将 MVAD 引为多模态设计与失效模式依据，而不是网络流量结果基线。明确“多种字段”“多种增强视图”和“不同信息生成机制的模态”三者区别。

## C. 协议审计

- Train：pure normal class。
- Negative/abnormal：只用于 test。
- Threshold-free metrics：AUROC/AUPR/TNR@95TPR。
- Fusion：不靠 negative validation 学权重。
- Random split：部分数据集 70/30，未做语义 group split。
- Hyperparameter source：论文称负类不可用于 validation，但具体 per-dataset selection 细节主要在 supplement。
- Protocol：`P0-normal-only-multiview-AD/P3-random-split-and-supplementary-selection-details`。

## D. 三层指标映射

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | 无多类分类 | Macro-F1、BA、per-family Recall、Benign FAR | 缺失 |
| 未知检测 | AUROC、AUPR、TNR@95%TPR | AUROC、AUPR-Out、FPR95、Unknown-F1 | 部分高度相关 |
| 联合开放集 | 无 | OSCR、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 无 | ECE、Brier、NLL、risk reliability | 缺失 |

## E. 95%/5% 对齐

若 normality score 越大越 known，原文 TNR@95%TPR 等价于：

> Unknown Rejection ∣ Known Acceptance = 95%。

换成 unknown risk 后等价于报告 FPR@95TPR 的互补方向，但必须统一 positive-class 定义。CAEOS 表格必须明确 unknown 为正类，避免把 TNR95 与 FPR95 误当同一数值方向。

## F. 对证据冲突的直接启示

平均融合是强基线，复杂融合没有稳定优势。因此 conflict-aware 模块必须至少通过：

1. 相同 encoder 与 split 下超过 late-average。
2. 在单模态损坏/缺失/矛盾时降低错误接收。
3. 多模态结果不劣于事后最佳单模态的程度可解释。
4. conflict score 对错误和 unknown 的增量不被 distance/energy 替代。
5. 不使用 unknown validation 学习 conflict weight 或 threshold。

## G. CAEOS 模态定义

可接受的三模态应具有不同生成机制：payload byte、packet sequence/timing、flow statistics。由同一统计向量做三种投影通常只是多视图增强，不应写成三模态。

每条流的三视图必须严格配对；缺包、截断、方向混淆和 flow-label mismatch 都会制造伪冲突，需要 missingness mask 与质量变量。

## H. 采纳与否决

### 采纳

- 11 类 baseline taxonomy。
- SUM/average 作为强下限。
- 95% normal acceptance 下 abnormal rejection。
- 最佳单视图 hindsight oracle。
- 视图冗余可能负贡献的明确审计。

### 有条件采纳

- Cross-view prediction 需防止时间/IP/长度捷径。
- Alignment 需与无 alignment 同参数量比较。
- Late-min 对任一模态告警敏感，需检查 Benign FAR。

### 不采纳

- 不把 one-versus-all image AD 结果直接作为恶意流量 SOTA。
- 不用随机 sample split 处理流量 capture。
- 不用复杂网络结构代替模态贡献证明。
- 不因整体 AUROC 提升而省略已知分类和校准。

## I. CAEOS 可执行实验

1. `E-MVAD-01`：三单模态、两两组合、三模态完整消融。
2. `E-MVAD-02`：SUM、MAX、concat-MLP、late-average、late-min、tensor fusion。
3. `E-MVAD-03`：DIS/DCCA/no-alignment。
4. `E-MVAD-04`：PPRD/SPRD 跨模态预测预训练。
5. `E-MVAD-05`：单模态随机缺失、截断、噪声和矛盾压力测试。
6. `E-MVAD-06`：best-single hindsight gap 与 per-scenario view contribution。
7. `E-MVAD-07`：conflict vs average 的 paired Wilcoxon＋Holm＋scenario-block bootstrap。
8. `E-MVAD-08`：95% Known Acceptance 下 Unknown Rejection 与 Benign FAR 双门。

## J. 可引用与不可引用主张

### 可引用

- 论文正式定义了 pure-normal multiview deep AD。
- 系统设计 11 个基线并在 30 多个 benchmark 上评估。
- 简单 SUM/average 是强基线，复杂融合无稳定优势。
- 26 个数据集中的 12 个，最佳多视图基线劣于最佳单视图 hindsight。
- 指标包括 AUROC、AUPR、TNR@95%TPR。

### 不可引用

- 任意三视图融合都必然提升异常检测。
- 本文证明三模态加密恶意流量有效。
- TNR@95%TPR 等同 Benign FAR≤5%。
- DCCA 或 tensor fusion 是统一最优。
- Random 70/30 split 满足 capture-grouped 网络协议。

## K. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过
- G2 身份门：通过至 IEEE/DOI，Zotero 待办
- G3 任务门：通过
- G4 协议门：通过，`P0-normal-only-multiview-AD/P3-random-split-and-supplementary-selection-details`
- G5 方法门：通过，11 基线族已覆盖
- G6 结果门：通过，主结果、失败模式、敏感性已核读
- G7 对比门：通过
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
