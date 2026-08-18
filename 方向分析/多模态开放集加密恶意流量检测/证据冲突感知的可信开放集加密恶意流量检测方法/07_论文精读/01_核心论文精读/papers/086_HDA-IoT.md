# 086 面向 IoT 入侵检测的异构域适配：几何图对齐 / HDA-IoT

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | 本卡 | 状态 |
|---|---|---|
| Abstract / I Introduction | 第 2 至 3 节 | 已覆盖 |
| II Related Work | 第 4 节 | 已覆盖 |
| III Preliminary / Architecture | 第 5 至 7 节 | 已覆盖 |
| IV GGA Algorithm | 第 8 至 13 节 | 已覆盖 |
| V Experiments | 第 14 至 20 节 | 已覆盖 |
| VI Conclusion | 第 21 节 | 已覆盖 |

## 1. 文献身份

- 标题：Heterogeneous Domain Adaptation for IoT Intrusion Detection: A Geometric Graph Alignment Approach。
- 作者：Jiashu Wu、Hao Dai、Yang Wang、Kejiang Ye、Chengzhong Xu。
- 期刊：IEEE Internet of Things Journal，10(12)，2023，10764–10777。
- DOI：10.1109/JIOT.2023.3239872。
- 方法：Geometric Graph Alignment（GGA）＋三票一致 Pseudo-Label Election（PLE）。
- 定位：异构数据集、不同特征空间下的半监督闭集域适配；不是 open-set domain adaptation。

## 2. 摘要缩译

IoT 入侵数据少，而传统网络入侵数据较丰富。论文把传统 NID 作为 source domain，把数据稀缺的 IoT IID 作为 target domain，通过几何图对齐迁移攻击类别知识。

每个域被表示为类别 centroid graph：vertex 是攻击类别，edge 是类别关系。GGA 同时保持图形状、旋转方向、中心位置和类别语义；PLE 用神经网络预测、几何相似和邻域投票共同选择可靠伪标签。五个数据集的跨域实验报告优于九个适配基线。

## 3. 引言缩译

IoT 设备资源有限、维护频率低，规则库难以覆盖不断变化的攻击；完全监督模型又需要大量目标域标签。由于传统网络与 IoT 网络共享 DoS、password、backdoor 等类别，作者把问题设为 semi-supervised heterogeneous domain adaptation。

“Heterogeneous”包含 source/target feature dimension 不同、feature semantics 不同和 distribution shift。论文认为只对齐 embedding distribution 太粗，需显式保持类别之间的几何关系。

## 4. 相关工作缩译

IID 方法包括规则扫描、K-means＋decision tree、feedforward network、autoencoder、BiLSTM。域适配对照包括 LadderNet、local MMD、TNT、G-JDA、DDA、STN、STAR、MME、APE、CDAC 与 graph methods。

作者批评直接预测/阈值式 pseudo-label 忽略类别几何与局部邻域，容易接受“高置信但几何错误”或 boundary-ambiguous 样本；复杂 graph embedding 又依赖大量目标数据。

## 5. 半监督 HDA 定义

Source domain：

> Dˢ = {(xᵢˢ,yᵢˢ)}ᵢ₌₁ⁿˢ，xᵢˢ∈ℝᵈˢ，yᵢˢ∈{1,…,K}。

Target domain 分为少量有标签与大量无标签：

> Dᵀ = Dᵀᴸ∪Dᵀᵁ，nᵀᴸ≪nᵀᵁ，xᵀ∈ℝᵈᵀ。

论文假设 source 与 target 共享相同 K 类，允许 dˢ≠dᵀ。默认目标有标签/无标签比例 1:50；这不是 zero-shot，也不是 unknown-blind。

## 6. 域图构造

两个域分别建 complete graph Gˢ、Gᵀ。类别 i 的 vertex 是类别 centroid：

> Vᵢˣ = (1÷nᵢˣ)Σⱼxⱼˣ，X∈{S,T}。

edge weight 是两个类别 centroid 的 Euclidean distance，所有 edge 组成 weighted adjacency matrix Mˣ。

该图每个 vertex 都依赖已知类别标签；若 target 存在 source 未见私有类，centroid correspondence 与 GGA theorem 的前提都会失效。

## 7. 双 projector 与共享 classifier

Source 和 target 使用独立 feature projector 映射到共同 dᶜ 维空间：

> f(x) = Eˢ(x)，x∈Xˢ；f(x) = Eᵀ(x)，x∈Xᵀ。

映射后共享 classifier C。两个 projector 允许输入维度和字段不同，是本文对 CAEOS 跨数据集适配最有价值的工程设计。

## 8. Pseudo-Label Election

无标签目标样本只有三个 vote 一致时才赋 pseudo-label：

1. NN prediction：共享 classifier 的类别预测。
2. Geometric vote：与 source＋labeled-target 类别 centroid cosine 最相似的类。
3. Neighborhood vote：KNN 邻域多数类别。

几何票为：

> PLᵍ(x) = arg maxₖ cos(μₖˢ⁺ᵀᴸ,x)。

若高置信预测与 centroid geometry 冲突，或邻域在边界处不能形成多数一致，则拒绝 pseudo-label。这里的“拒绝”只是训练时暂不使用样本，不是测试阶段 unknown rejection。

## 9. Shape Keeping

GGA 生成 source、labeled target、labeled＋pseudo-labeled target 三个 WAM。Discriminator 判断 WAM 来自 source 还是 target，projector 反向使 discriminator 混淆，从而对齐图形状。

形状对齐损失概念上为：

> Lˢᵏ = log D(Mˢ) + ½Σ(M∈{Mᵀᴸ,Mᵀᴸ⁺ᴾᴸ})[1−log D(M)]。

原文表达存在非标准 adversarial log 形式，复现应以作者代码核对 BCE sign 与 gradient reversal 实现。

## 10. Rotation Avoidance

仅使 edge distance 相同仍可整体旋转。作者要求对应类别 vertex 的方向一致：

> Lᴿ = Σᵢ₌₁ᴷ[1−cos(Vᵢˢ,Vᵢᵀ)]。

此约束依赖共同坐标原点与类别严格一一对应；projector 的任意尺度/平移会影响其几何解释。

## 11. Centre Point Matching

图形状和方向一致仍可能因对称产生错位，因此匹配两域全局中心：

> μˣ = (1÷nˣ)Σᵢxᵢˣ，

> Lᶜᵖ = ‖μˢ−μᵀ‖₂。

该项使用所有目标样本，不要求 pseudo-label，属于 transductive unsupervised target exposure。

## 12. Vertex Semantic Preservation

Source 类别 k 的平均 soft prediction 构成 correlation semantic：

> q⁽ᵏ⁾ = (1÷nₖˢ)Σ(x∈Xₖˢ)Softmax(C(f(x))÷T)。

Labeled target 样本预测为 pᵢ。用 cross-entropy 使 pᵢ 保持相应 source 类别 correlation structure，再与目标真标签监督组合为 L_V。

它利用“类别与其他类别的相似性分布”做 vertex-level alignment，但仍假设所有目标类已在 source label space 中定义。

## 13. 总目标与定理

Source supervision：

> Lˢᵘᵖ = (1÷nˢ)ΣᵢCE(C(f(xᵢ)),yᵢ)。

总目标：

> min(C,Eˢ,Eᵀ) maxᴰ [Lˢᵘᵖ + γLˢᵏ + ηLᴿ + λLᶜᵖ + Lⱽ]。

γ 从 0.01 线性增至 0.1，让早期不成熟 graph 少受 shape alignment 干扰。作者声称当 Same Shape、Same Angle、Same Centre 三规则同时成立时两图精确对齐。

该定理只证明抽象点图在强条件下的几何对应，不证明有限样本训练能满足条件，也不证明 class-conditional distributions 或决策风险已对齐。

## 14. 数据集与特征

Source NID：

- NSL-KDD：20% 数据，41 维中使用 top-31 features。
- UNSW-NB15：2700 records，49 维中删除四个近全零字段。
- CICIDS2017：creator 20% portion，77 维中使用 information-gain top-40。

Target IID：

- UNSW-BoT-IoT：10,000 records，46 维中使用 top-10 informative features。
- UNSW-ToN-IoT：约 10%，选择 weather meter 与 GPS tracker 两设备，各自特征维度不同。

大量子采样与有监督 feature ranking 会改变真实类别比例；论文没有说明 feature ranking 是否严格只用 training labels。

## 15. 共享标签映射

不同数据集最多人工映射八个 shared intrusion categories。共享类覆盖率分别约为：NSL-KDD 100%、UNSW-NB15 54.9%、CICIDS2017 100%、BoT-IoT 100%、ToN-IoT 98.3%。

这说明实验并非完整数据集跨域：UNSW-NB15 近一半记录不在 shared-category transfer space。论文没有把非共享类作为 unknown 评估，而是围绕可对齐类别构造闭集任务。

## 16. 训练设置

Projector 为两层 LeakyReLU network；classifier 与 discriminator 为单层网络。固定超参数：α=0.1、γ=0.01→0.1、η=0.01、λ=0.01、dᶜ=3、T=5、neighbors=4。

Gradient reversal 实现 adversarial alignment，Adam 优化。目标 scarcity 比例覆盖 1:10 至 1:100，默认 1:50。

## 17. 指标

主要指标是 unlabeled target classification accuracy；补充 category-frequency-weighted Precision、Recall、F1 和 multiclass AUC。

加权 F1：

> F1ʷᵉⁱᵍʰᵗᵉᵈ = Σₖ(|Xₖᵀᵁ|÷nᵀᵁ) · [2PₖRₖ÷(Pₖ+Rₖ)]。

这不是 Macro-F1，会被多数类主导；AUC 也未说明 macro/micro/one-vs-rest averaging 细节。Benign FAR 和 per-class recall 未独立报告。

## 18. 主结果缩译

九个对照包括 TNT、MME、STN、APE、DDAS、DDAC、WCGN、CDAC、STAR。默认 1:50 下，GGA 比所有对照至少高 4.2% accuracy。

在三个随机选取任务的 1:10–1:100 scarcity 实验中，GGA 相对最佳 WCGN 平均提高 4.36%，相对第二名提高 8.29%；1:100 时相对 1:50 只下降 0.87%。

Precision/Recall/F1/AUC 只在两个随机任务上展示，不能据此声称所有跨域组合全面占优。

## 19. PLE 与消融

Full PLE 中期 pseudo-label accuracy 约 86.6%–90%，最终约 92.5%–96.2%；1:10 最终可达 99.06%，1:100 相对下降 4.27%。pseudo-label accuracy 使用隐藏目标真标签仅作事后分析。

Full GGA 相对消融平均提高 3.4%；rotation avoidance 贡献约 4.9%；移除任一 PLE vote 平均下降 3.3%；用单纯 vertex Euclidean alignment 替代完整 GGA 下降 2.8%。

作者在三个随机任务做 t-test，以 p<0.05 判断显著，但没有报告随机种子数、配对单位、多重比较校正或 effect size。

## 20. 敏感性与效率

固定超参数在多个任务中表现相对稳定。GGA 每 epoch 比 DDAC 快约 31 倍、比 WCGN 快 6.67%；单实例推理比 WCGN 快 15.79%。绝对硬件、吞吐与预处理成本披露有限。

## 21. 结论缩译

GGA 通过 PLE、shape keeping、rotation avoidance、centre matching 和 vertex semantic preservation，从整体图到类别 vertex 逐级对齐异构 intrusion domains。实验支持其在少量目标标签条件下改善闭集目标分类。

# 第二部分：独立技术分析

## A. 一句话结论

HDA-IoT 可为 CAEOS 提供“跨数据集异构 feature projector＋类别结构对齐”基线，但其共享 K 类、少量目标真标签和全目标无标签暴露构成半监督 transductive closed-set protocol，不能作为 strict leave-family-out OSR 主基线。

## B. 两条交付线

### 工程线

实现 source/target 双 projector、shared classifier、center/semantic alignment；将 original semi-supervised HDA 与 strict source-only/cross-dataset OSR 分为两个配置，禁止混报。

### 论文线

把原论文成绩列入跨域适配附表，注明 target-label ratio、target-unlabeled exposure、shared-class coverage 与 weighted metrics。主表只比较严格 unknown-blind 协议。

## C. 协议审计

- Source：全标签训练。
- Target：少量真标签＋大量无标签同时用于训练。
- Pseudo-label：仅共享已知 K 类。
- Private target classes：未作为 unknown 评估。
- Split/grouping：未证明按 capture/device/time grouped。
- Feature selection：多个数据集用有监督 top features，fit scope 不清。
- Protocol：`P1-semi-supervised-transductive-closed-set-HDA/P3-shared-class-filter-feature-selection-and-group-split-unclear`。

## D. 与开放集任务的差异

GGA 解决：相同标签空间、不同输入空间、目标有少量标签。CAEOS 解决：训练只有 known families，测试同时含 known 与 unknown，unknown 不得参与 threshold/fusion selection。

若目标私有攻击被强制 pseudo-label 到共享 K 类，GGA 可能加剧 negative transfer 和高置信误归类。必须增加 unknown-aware pseudo-label abstention 与 open-set domain adaptation 对照后才可进入主线。

## E. 三层指标

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | Accuracy、weighted P/R/F1 | Macro-F1、BA、per-class Recall、Benign FAR | 部分，不抗不平衡 |
| 未知检测 | 无 | AUROC、AUPR-Out、FPR95、Unknown-F1 | 缺失 |
| 联合开放集 | 无 | OSCR、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 无 | ECE、Brier、NLL、risk reliability | 缺失 |

## F. 对证据冲突的启示

PLE 的三票一致与 CAEOS 冲突拒绝有结构相似性：classifier、centroid geometry、neighborhood 若不一致则暂缓伪标签。但 PLE 只影响训练样本选取，没有定义测试 risk 或 calibrated threshold。

可把 prediction/geometry/neighborhood disagreement 作为辅助 conflict component，必须在 known-only validation 上校准，并与 distance、energy 和多模态 conflict 分开做增量分析。

## G. 跨数据集实验注意事项

- 先建立明确的 label ontology 与可审计映射，不能按名称模糊合并。
- 保留非共享 target 类作为 unknown，而不是删除。
- Feature intersection、双 projector 与 missingness adapter 分别比较。
- Target normalization 不能用 test labels，可区分 transductive unlabeled normalization 与 inductive source-only。
- 每个场景重新拟合 projector、prototype、risk normalization 和 threshold。

## H. 采纳与否决

### 采纳

- 异构 feature space 双 projector。
- Class-centroid relation alignment。
- 伪标签三票一致与 abstention。
- Target label scarcity curve。
- Shared/private class coverage 审计。

### 有条件采纳

- Centre matching 只放 transductive 支线。
- Pseudo-label 需 unknown-aware rejection。
- 图定理只作设计直觉，不作性能保证。

### 不采纳

- 不删除非共享类后宣称跨域开放集。
- 不把 weighted F1 写成 Macro-F1。
- 不在 strict 主线使用目标真标签或全目标测试分布。
- 不将 training pseudo-label abstention 写成 unknown detection。
- 不用少量随机任务替代全场景统计检验。

## I. CAEOS 可执行实验

1. `E-HDA-01`：feature intersection、zero padding、双 projector 三种异构适配。
2. `E-HDA-02`：source-only、unlabeled transductive、1:100/1:50 labeled target 分协议。
3. `E-HDA-03`：保留 target-private families 的 open-set HDA。
4. `E-HDA-04`：prediction/geometry/neighborhood 三票与单票消融。
5. `E-HDA-05`：center、shape、rotation、semantic alignment 消融。
6. `E-HDA-06`：跨 ToN/BoT/CIC/Edge 的 ontology coverage 和 unknown family matrix。
7. `E-HDA-07`：Known Macro-F1、Unknown AUROC/FPR95、OSCR、ECE 全三层指标。
8. `E-HDA-08`：场景×种子 paired Wilcoxon＋Holm＋block bootstrap。

## J. 可引用与不可引用主张

### 可引用

- GGA 面向不同特征空间的半监督异构域适配。
- 默认目标有标签/无标签比例为 1:50。
- PLE 同时要求 prediction、geometry、neighborhood 一致。
- 五数据集构造共享类别迁移，UNSW-NB15 共享覆盖仅 54.9%。
- GGA 相对消融平均提高约 3.4%。

### 不可引用

- GGA 已处理目标私有未知攻击。
- PLE rejection 等同 open-set rejection。
- Weighted F1 是 Macro-F1。
- 原协议完全不使用目标域信息。
- GGA theorem 保证现实分类性能。
- 论文结果证明 Benign FAR≤5%。

## K. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过
- G2 身份门：通过至 IEEE/DOI，Zotero 待办
- G3 任务门：通过
- G4 协议门：通过，`P1-semi-supervised-transductive-closed-set-HDA/P3-shared-class-filter-feature-selection-and-group-split-unclear`
- G5 方法门：通过
- G6 结果门：通过，主结果、PLE、消融、敏感性与效率已核读
- G7 对比门：通过
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
