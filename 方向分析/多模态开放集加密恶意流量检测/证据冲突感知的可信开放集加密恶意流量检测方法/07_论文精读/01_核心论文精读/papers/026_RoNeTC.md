# 026 RoNeTC：可靠开放集网络流量分类

## 1. 文献身份与结论状态

- 论文：*Reliable Open-Set Network Traffic Classification*
- 作者：Xueman Wang、Yipeng Wang、Yingxu Lai、Zhiyu Hao、Alex X. Liu
- 期刊：*IEEE Transactions on Information Forensics and Security*, 20, 2313-2328, 2025
- DOI：`10.1109/TIFS.2025.3544067`
- 本地全文：`04_120篇全文抽取/026_Reliable_Open_Set_Network_Traffic_Classification.txt`
- 当前状态：`project_mapped`；全文方法和结果已缩译，严格复现、Zotero/引用键与表格逐项核验待完成。

## 2. 摘要缩译

多数网络流量分类器只认识训练标签，在已知和大量未知应用并存的开放环境中会把未知类强行归为已知类。RoNeTC 为提升准确性和可靠性，把流内每个包拆成三个视图，联合提取包内局部表示与跨包全局表示；随后用 Dirichlet 二阶分类概率表示每个视图的类别信念和决策不确定性，并按不确定性动态融合多视图意见。最终以联合不确定性区分 known/unknown，再用融合概率细分已知类。论文在六个跨数据集开放场景与四个基线比较，报告 RoNeTC 的 F1 平均领先 25.94 个百分点。

## 3. 任务定义与研究动机

RoNeTC 面向应用/设备流量分类，不是恶意流量检测。设训练标签为 K 个已知应用或设备类；测试样本可能属于这 K 类，也可能来自未见数据集中的应用类。模型输出已知类标签或统一 unknown。它与 CAEOS 在“已知细分类+未知拒识”的数学结构上接近，但语义对象不同：RoNeTC 的 unknown 可能只是未见正常应用/设备，并不等于未知攻击家族。

作者批评 softmax 会把未知样本也压成高置信概率；概率阈值或梯度阈值虽可拒识，却不直接给出决策可靠性。其核心主张是：known 样本能产生充足类别证据，Dirichlet 意见应低不确定；unknown 没有训练支持，证据较少、联合不确定性较高。

## 4. 输入预处理缩译

每个双向五元组流取前 l 个包，每包取前 b 字节。依据 TCP/IP 协议栈把字节拆成三视图：IP Header、Transport Header、Packet Payload。各视图独立嵌入为二维张量并行训练。

这三个视图都来自同一个包，不是真正独立传感器模态，但比把通道直接拼成一张图更接近 CAEOS 的分支式结构。其优势是可以对每个视图产生独立意见；局限是视图高度相关，IP/传输头长度随协议变化，非 TCP/UDP、IPv6 扩展头、TLS/QUIC payload 以及缺失字段的处理规则未在正文充分说明。

论文的 l ∈ {4, 8, 12, 16}，b ∈ {64, 128, 256}。注意这些只是模型输入选择；不能据此从 CAEOS 基础数据集中删除更多包或字节。完整提取仍应保留，RoNeTC adapter 再按场景选择前缀。

## 5. 全局-局部表征缩译

对单视图输入 X（形状为 H × W × C），先用 3 × 3 卷积学习包内局部特征，再以 1 × 1 卷积投影到 D 维，得到 Xᴸ（形状为 H × W × D）。

为捕获跨包同一字段位置的状态变化，把 Xᴸ 展开为不重叠 patch，并把多个包相同位置的 patch 组成序列 Xᵁ。Transformer 在该序列上计算全局依赖：

Xᵀ⁽ᵖ⁾ = Transformer(Xᵁ⁽ᵖ⁾)，p = 1, …, P

再折叠回 Xᶠ（形状为 H × W × D），投影到 C 维，与原局部表示拼接并经 CNN 融合。论文还把每 r 个包按非重叠交叉方式拼成通道，例如 12 包每 4 包一组形成 3 通道，patch 通常取 2 × 2。

该结构的假设是“跨包同位置字段相关性强于包内无关位置”。对固定头字段合理，但 payload 中相同偏移在加密后未必有一致语义；论文解释性热图也显示 payload 贡献通常低于 IP/传输头，只有含明文握手时首包贡献提高。

## 6. 单视图证据意见缩译

每个视图不用 softmax，而以 softplus 输出非负证据 eₖ⁽ᵛ⁾ ≥ 0，令

αₖ⁽ᵛ⁾ = eₖ⁽ᵛ⁾ + 1

S⁽ᵛ⁾ = ∑ₖ₌₁ᴷ αₖ⁽ᵛ⁾

由此定义 Dirichlet 二阶概率密度

Dir(p ∣ α) = [1 ÷ B(α)]∏ₖ₌₁ᴷ exp[(αₖ − 1) ln pₖ]

以及 subjective opinion

bₖ⁽ᵛ⁾ = eₖ⁽ᵛ⁾ ÷ S⁽ᵛ⁾

u⁽ᵛ⁾ = K ÷ S⁽ᵛ⁾

u⁽ᵛ⁾ + ∑ₖ₌₁ᴷ bₖ⁽ᵛ⁾ = 1

投影类别概率为 p̂ₖ⁽ᵛ⁾ = αₖ⁽ᵛ⁾ ÷ S⁽ᵛ⁾。证据越多，u 越低；若所有类别都缺证据，u 接近 1。该不确定性是总证据量的函数，并不自动区分“各视图彼此冲突”与“所有视图都无知”。

## 7. 多视图 Dempster 融合缩译

对两个意见 M₁ = (b₁, u₁) 与 M₂ = (b₂, u₂)，冲突质量为

C = ∑ᵢ≠ⱼ b₁ᵢb₂ⱼ

Dempster 组合为

bₖ = (b₁ₖb₂ₖ + b₁ₖu₂ + b₂ₖu₁) ÷ (1 − C)

u = u₁u₂ ÷ (1 − C)

三视图通过递归组合得到联合意见，再由

S = K ÷ u，eₖ = bₖS，αₖ = eₖ + 1

恢复融合证据。

这一公式是 RoNeTC 与 CAEOS 最关键的交叉点。RoNeTC 虽计算 C，却把它仅作为 Dempster 归一化因子；没有把高冲突本身作为风险，也没有在 C → 1 时折扣不可靠视图。强冲突下 1 ÷ (1 − C) 会放大剩余质量，这正是 CAEOS 引入显式 conflict risk、reliability discount 和 abstention 的必要性。

## 8. 训练损失缩译

Dirichlet 上的期望交叉熵为

Lₐcₑ(αᵢ) = ∑ⱼ₌₁ᴷ yᵢⱼ[ψ(Sᵢ) − ψ(αᵢⱼ)]

为抑制非真实类别上的多余证据，令 α̃ᵢ = yᵢ + (1 − yᵢ) ⊙ αᵢ，加入到均匀 Dirichlet 的 KL：

L(αᵢ) = Lₐcₑ(αᵢ) + λₜ KL[Dir(p ∣ α̃ᵢ) ∥ Dir(p ∣ 1)]

总损失同时监督联合意见和三个单视图：

Lₐₗₗ = ∑ᵢ₌₁ᴺ [L(αᵢ) + ∑ᵥ₌₁³ L(αᵢ⁽ᵛ⁾)]

正文明确训练阶段没有 unknown 样本。文中“penalize unknown classes”实际应理解为压低错误已知类证据，而非用真实 unknown 监督。该 known-only 训练设计符合严格 OSR 的训练侧要求。

## 9. 拒识阈值与协议审计

推理用联合不确定性 u：低于阈值判 known 并取最大融合概率，高于阈值判 unknown。论文借鉴 Youden 指标，以 TPR/FPR 构造 η(σ) 并选择最大点附近的阈值。

问题在于已知数据按 60%/20%/20% 分 train/validation/test，而来自另一个数据集的全部 unknown 只加入 open-set test。若 TPR/FPR 的正负类是 known/unknown，就无法仅靠 known validation 计算该阈值。正文没有另设 auxiliary unknown validation，也没有说明用已知正确/错误样本替代 unknown。

更明确的泄漏来自参数选择：论文逐个开放场景扫描 b、l，直接按该场景最高 open-set F1 选择最优组合。例如 Scenario-A 以 96.44% F1 选参数，Scenario-B 以 98.16% F1 选另一组合。由此，所报最佳结果属于 `P3-test-tuned`，不能进入 CAEOS strict known-only-validation 主表。它可以作为论文复现表或弱可比附表，严格复现必须重新固定阈值和前缀参数。

## 10. 数据集与六个开放场景

三个公开数据集为：

- Dataset-I：UNSW 智能环境设备流量，采集约 26 周，每类选 1,000 个流。
- Dataset-II：CIC IoT Dataset 2022，每类选 500 个流。
- Dataset-III：MApps 移动应用流量，10 名志愿者、8 部手机、连续 6 个月采集，每类选 500-1,000 个流。

六个场景做两两跨数据集：A/B 以 Dataset-I 为 known、Dataset-II/III 为 unknown；C/D 以 Dataset-II 为 known、Dataset-I/III 为 unknown；E/F 以 Dataset-III 为 known、Dataset-II/I 为 unknown。每个已知类按 60/20/20 划分，unknown 全部进入测试。Dataset-I 的 known 类数在效率章节记为 13，Dataset-III 为 48；Dataset-II 精确类数需从表 II 图像复核。

这是较强的跨数据集 unknown 设计，但同时混入采集设备、时间、协议和数据处理域差异，模型可能检测 dataset identity，而不是开放类语义。每类固定抽样也改变真实基率。正文未见多随机种子、跨场景配对置信区间或 family-level 留一实验。

## 11. 指标与结果缩译

论文主指标为开放集宏平均 Recall、Precision、F1，把每个已知类与统一 unknown 共同计算；另画 known-vs-unknown ROC/AUC。它未报告 OSCR、FPR@95TPR、AUPR、Unknown-F1、ECE/Brier 或良性 FAR。

### 11.1 六场景最佳结果

| 场景 | Known | Unknown | RoNeTC F1 | 关键参数/结果 |
|---|---|---|---:|---|
| A | I | II | 96.44% | Recall 95.92%，Precision 97.22% |
| B | I | III | 98.16% | Recall 98.11%，Precision 98.32%，AUC 99.66% |
| C | II | I | 94.56% | b = 256，l = 4 |
| D | II | III | 94.03% | b = 256，l = 16 |
| E | III | II | 91.71% | 48 known 类，最复杂场景之一 |
| F | III | I | 93.26% | 48 known 类 |

六场景只有 A/B 的 F1 超过 95%；C-F 均未过 CAEOS 95% 目标。论文摘要的平均领先 25.94 个百分点是相对弱基线的差值，不等于安全门达标。

### 11.2 闭集与基线

Dataset-I 闭集 F1/Recall/Precision 均超过 99%，最佳接近 99.96%；Dataset-II 最佳 F1/Recall 99.11%、Precision 99.13%；Dataset-III 最佳 F1 94.88%、Recall 94.39%，已低于 95%。

ETC-PS 在 Scenario-A F1 93.03%，比 RoNeTC 低 3.41；Scenario-E 仅 70.79%。AutoUA 最好在 F 为 65.85%，在 D 仅 36.11%。GradBP-max 在 A 为 F1 85.19%、Recall 92.08%、Precision 79.20；在 B 为 66.15%。GradBP-square-root 在 E 为 80.31%，在 D 为 52.83%。这些比较说明 RoNeTC 优势明显，但各基线的阈值和输入长度来源不同，且共同使用 RoNeTC 选出的场景最优参数并不能保证等调参预算。

### 11.3 鲁棒性、解释性与效率

作者向每个场景再加入第三个 unknown 数据集，保持模型、阈值和参数不变。RoNeTC 多数场景变化较小，在 MixB/MixF 的 F1 约下降 3%，优于基线。这是比单一 unknown 集更有价值的稳健性测试，但仍是数据集级域识别。

热图显示 IP Total Length、TTL 和传输层 Window Size 等固定字段及其跨包变化重要；加密 payload 重要性低，含握手时首包明文会提高 payload 贡献。该结果同时提示 IP/端口/设备指纹泄漏风险，必须在跨 capture 分组后复核。

在 A800 上每个场景测试 20 次。Scenario-E 的特征提取、Dirichlet、总时延分别约 1.97 × 10⁻⁵、3.43 × 10⁻⁶、2.31 × 10⁻⁵ s/flow，吞吐 43,290 flow/s；Scenario-B 总时延 2.32 × 10⁻⁵ s/flow，吞吐 43,103 flow/s。大 batch 的 Scenario-A 最高 220,361 flow/s。Dirichlet 部分复杂度为 O(K²)，但整体特征提取占主导；这些是 A800 大批量结果，不能直接外推到本项目 48 GB GPU 的在线单流延迟。

## 12. 作者结论与独立局限

作者认为三视图全局-局部特征、Dirichlet 二阶概率和 Dempster 动态融合共同提升了开放集流量分类的可靠性，并在新增大量 unknown 后保持稳健。

独立审计的主要局限为：

1. 以 open-set test F1 选 b、l，阈值又依赖 known/unknown TPR/FPR，存在明确 P3 风险。
2. Dempster 规则在高冲突时用 1 ÷ (1 − C) 归一，未折扣错误但高证据视图，也未把冲突直接用于拒识。
3. 不确定性只由总证据量 K ÷ S 给出，未验证 ECE/Brier/NLL，不能直接称为校准可信度。
4. 三视图同源且强依赖；IP/Transport 固定字段可能编码数据集或设备身份。
5. unknown 来自另一个数据集，类别开放与域偏移混合。
6. 主指标是联合 Macro-F1，不能分辨 known 分类改善还是 unknown 拒识改善。
7. MApps/IoT 应用分类并非恶意流量家族分类，语义可比性有限。

## 13. 对 CAEOS-EMTD 的吸收与纠偏

RoNeTC 必须进入 CAEOS 的正式基线矩阵，但分两版：

- `RoNeTC-paper`：忠实复现论文场景和 test-tuned 选择，只放附表并标 P3。
- `RoNeTC-strict`：相同模型、相同 grouped split、前缀参数只在训练/known validation 确定，拒识阈值仅用 known validation 分位数，进入主表。

自有算法相对 RoNeTC 的创新不能只写“也使用 EDL/DS”。必须证明三点：显式冲突 C 能预测错误/unknown；可靠性折扣优于原始 Dempster 归一；在模态缺失或矛盾时仍保持校准与 OSCR。否则只是 RoNeTC 的重复实现。

## 14. CAEOS 可执行实验

1. 实现 IP Header、Transport Header、Payload 三分支 RoNeTC official adapter，并锁定论文前缀候选。
2. 同时运行 `paper threshold` 与 `known-quantile threshold`，量化 test tuning 带来的乐观偏差。
3. 增加 `Dempster`、`uncertainty-weighted average`、`discounted belief fusion`、`conflict-aware abstention` 四种融合消融。
4. 单独计算 u、C、energy、distance、support 的 unknown AUROC 和 error AUROC。
5. 注入高冲突反事实：三个视图分别支持不同 known 类；扫描 C → 1 时概率、uncertainty 与拒识是否稳定。
6. 做 header-only、payload-only、missing-view、corrupted-view 和 TLS-with/without-handshake 分层评估。
7. 在 CICIoT2022/MApps 之外加入恶意流量 family holdout，避免只验证设备/应用 unknown。
8. 主表报告 Known Macro-F1、Balanced Accuracy、Unknown AUROC/AUPR/FPR95、OSCR；附表报告 Unknown-F1、ECE/Brier、KAR/URR。
9. 5 个种子，以场景×种子做配对 Wilcoxon+Holm 与 scenario-block bootstrap。

## 15. 95%/5% 验收判断

RoNeTC 在 A/B 的联合 F1 过 95%，但 C-F 未过；Dataset-III 闭集 F1 也只有 94.88%。论文没有 benign FAR 和 FPR@95TPR，无法判断 5% 门；最佳参数又由测试场景选择。因此现有论文数值不能作为 CAEOS 达到 95%/5% 的证据，只能说明这是一个强而必要的直接基线。

## 16. G0-G10

| 门 | 状态 | 说明 |
|---|---|---|
| G0 中文缩译 | 通过 | 主要章节完整覆盖 |
| G1 全文 | 通过 | 本地全文可定位 |
| G2 身份 | 未通过 | DOI 已核，Zotero/Citation Key 未绑定 |
| G3 任务 | 通过 | 应用/设备 known 分类与 unknown 拒识已区分 |
| G4 协议 | 通过 | 60/20/20、跨数据集 unknown 与 P3 风险已审计 |
| G5 方法 | 通过 | 三视图、全局局部、Dirichlet、DS 与损失已还原 |
| G6 结果 | 通过 | 六场景、闭集、基线与效率关键数值已记录 |
| G7 公平性 | 通过 | 调参、域偏移和基线预算问题已记录 |
| G8 局限 | 通过 | 冲突、校准、协议和语义局限均记录 |
| G9 项目映射 | 通过 | 已形成 paper/strict 双基线及九项实验 |
| G10 引用 | 未通过 | Zotero/证据卡待办 |

## 17. 一句话结论

RoNeTC 是 CAEOS 最直接的证据式开放集流量基线，但其最佳结果受测试集调参影响，原始 Dempster 融合又没有真正处理高冲突；CAEOS 的论文价值必须建立在严格阈值协议和可验证的冲突折扣增益上。
