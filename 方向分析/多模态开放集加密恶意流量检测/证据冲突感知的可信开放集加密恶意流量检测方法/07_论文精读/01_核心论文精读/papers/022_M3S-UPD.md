# 022 多阶段自监督加密流量分类与未知模式发现 / M3S-UPD

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | 本文对应内容 | 覆盖状态 |
|---|---|---|
| Abstract | 第 2 节 | 已覆盖 |
| I Introduction | 第 3 节 | 已覆盖 |
| II Related Work | 第 4 节 | 已覆盖 |
| III Problem Definition | 第 5 节 | 已覆盖 |
| IV Method | 第 6 至 10 节 | 已覆盖 |
| V Experimental Evaluation | 第 11 至 16 节 | 已覆盖 |
| VI Conclusion | 第 17 节 | 已覆盖 |

## 1. 文献身份

- 标题：M3S-UPD: Efficient Multi-Stage Self-Supervised Learning for Fine-Grained Encrypted Traffic Classification with Unknown Pattern Discovery。
- 中文题名：M3S-UPD：面向细粒度加密流量分类和未知模式发现的高效多阶段自监督学习。
- 作者：Yali Yuan、Yu Huang、Xingjian Zeng、Hantao Mei、Guang Cheng。
- 版本：arXiv:2505.21462v1，2025-05-27。
- 本地全文：`paper/10.48550_arXiv.2505.21462.pdf`。
- 发表状态：本地版本是 arXiv 预印本。页眉中的 “JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015” 是 IEEE 模板占位信息，不是正式期刊卷期。
- 研究对象：Tor 应用/流量类型的少标注分类、未知类别拒识和专家参与的持续更新。

## 2. 摘要缩译

复杂加密流量同时带来已知应用多分类和未知模式发现问题。监督模型在现实部署中受到标注稀缺、概念漂移和更新成本制约。论文提出 M3S-UPD，通过四阶段迭代过程联合利用少量已标注数据和未标注流量：生成分类概率与嵌入、聚类发现结构、把簇与已知类分布对齐、根据预测与对齐的一致性更新模型。

作者声称该方法不合成未知样本，也不需要未知类别先验标签。未能对齐已知类且分类置信度较低的未标注流量被识别为 unknown；与已知类对齐且预测标签一致的高置信样本被赋予伪标签并加入训练。实验在 ISCXTor2016 和作者自采 TDTor 上进行，报告少标注已知分类、未知拒识以及引入专家标注后的持续学习结果。

## 3. 引言与任务动机缩译

论文把加密流量分类拆为两个应用任务：

1. 多分类：识别应用、服务或流量类型，用于 QoS 和网络管理。
2. 未知检测：发现分类器训练阶段未见的流量类型。

作者认为二者共享同一表征和在线流，因此可以在一个持续学习框架中处理。但原文所说“二者都是分类问题”不能理解为二者具有相同决策边界或可使用同一个指标。已知多分类与 unknown 接收/拒识仍是不同任务。

论文关注三项现实困难：初始标注数据有限、未见类别不断出现、模型更新中的伪标签错误会累积。M3S-UPD 试图用聚类几何与分类概率之间的一致性降低确认偏差。

## 4. 相关工作缩译

相关路线包括手工流量统计、深度序列分类、Tor 和网站指纹、少样本分类、生成式未知样本、开放集原型与在线模型更新。论文特别批评两类方法：依赖 GAN 等生成 unknown 的方法成本高且生成分布不可靠；仅凭最大预测概率做自训练的方法容易把错误伪标签加入训练。

M3S-UPD 的差异在于直接读取未标注池的嵌入结构，并要求 cluster alignment 与 classifier prediction 一致。该机制更接近半监督自训练和 transductive clustering，而不是通常意义上通过预文本任务学习表示的自监督学习。

## 5. 问题定义缩译

初始训练集为：

> D = {（x₁，y₁），…，（xₙ，yₙ）}，且 yᵢ ∈ C = {l₁，…，lₘ}。

在时刻 t，模型 Fₜ 基于先前数据 Dₜ₋₁ 和已知标签集合 Cₜ₋₁。新到达流量 Nₜ 由已知流 Kₜ 和未知流 Uₜ 组成。模型既要把 Kₜ 映射到 Cₜ₋₁ 中的具体类别，又要把 Uₜ 从 Kₜ 中分离。

高置信已知样本可用伪标签加入 Dₜ。若专家进一步标注发现的未知样本，则 Uₜ 中被标注的类别也被加入数据集和标签集合，模型进入下一轮持续学习。由此可见，论文实际包含两条不同协议：

- no-expert：目标 unknown 无标签，但其样本分布参与训练过程。
- with-expert：检测出的 target unknown 被人工标注并转化为新 known。

## 6. 第一阶段：模型准备缩译

先用少量已标注数据训练一个闭集分类器，损失为平均交叉熵：

> Lₛ =（1 ÷ N）∑ᵢH（yᵢ，ŷᵢ）。

训练后的模型为每个未标注样本输出嵌入向量和 K 个已知类 logit。SoftMax 概率为：

> pᵢ = exp（zᵢ）÷∑ⱼ₌₁ᴷexp（zⱼ）。

最大 pᵢ 被当作样本属于某个已知类的置信度。原文没有说明底层分类器架构、原始输入特征、优化器、学习率、训练 epoch 或正式代码地址，复现信息明显不足。

## 7. 第二阶段：嵌入聚类缩译

所有未标注流量先经当前模型变换到嵌入空间，再使用 DBSCAN 聚类。作者选择 DBSCAN，是因为它不要求预先指定簇数，并允许类别数随在线流量变化。

聚类使用整个未标注池的空间结构。若该池包含 target unknown，则模型在训练阶段已经读取目标未知分布，即使没有使用未知标签。这与严格 known-only OSR 不同。

原文未报告 DBSCAN 的 ε、min_samples、距离标准化、噪声点处理或参数选择来源。不同 unknown 比例和嵌入尺度都可能显著改变簇结构。

## 8. 第三阶段：空间分布对齐缩译

未标注簇 uᵢ 的中心为 vᵢ，已知类 m 的标注嵌入中心为 μₘ。簇到已知类的距离为：

> d（uᵢ，kₘ）= ‖vᵢ − μₘ‖₂。

簇的辅助标签规则为：

> ỹᵢ = potential unknown，当 minₘd（uᵢ，kₘ）≥t；否则 ỹᵢ = arg minₘd（uᵢ，kₘ）。

若簇与所有已知类中心的最小距离都超过阈值 t，则簇被标为潜在 unknown；否则整个簇临时对齐到最近已知类。

该规则只有单中心距离，没有建模类内尺度、类别不平衡、多峰结构或簇大小。原文也没有给出 t 的数值、校准集合或选择方法，因此无法判断 unknown 信息是否参与阈值确定。

## 9. 第四阶段：一致性检查与模型更新缩译

对已对齐样本，只有当簇辅助标签与分类器最大概率类别一致时，样本才以伪标签加入训练集。对未对齐簇，如果样本最大 SoftMax 概率处于整个未标注池的最低置信区间，则被识别为 unknown。高置信和低置信候选数量分别由 tₜₒₚ 与 tᵦₒₜₜₒₘ 控制；中间样本推迟到下一轮。

这相当于使用两种同源证据：

- 几何证据：DBSCAN 簇及其到已知原型的距离。
- 判别证据：闭集分类器最大 SoftMax 概率。

一致且高置信的样本用于已知类自训练；几何未对齐且判别置信度低的样本被拒识。原文没有给出 tₜₒₚ、tᵦₒₜₜₒₘ 数值及其选择来源，也没有量化两种证据冲突的连续程度。

## 10. 方法风险缩译与补充分析

如果 unknown 获得较高 SoftMax 且其簇靠近某个已知中心，它会被错误赋予已知伪标签并污染后续模型；如果少数 known 类形成稀疏簇且置信度偏低，则可能被误拒识。由于高低置信区间由整个未标注池排序得到，规则还依赖当前 known/unknown 比例，部署流量组成变化会导致判定漂移。

M3S-UPD 使用的是同一分类器产生的嵌入和概率，二者并非独立模态证据。它具备“表示空间与预测空间一致性”思想，但不能直接称为多模态证据冲突融合。

## 11. 数据集缩译与身份边界

实验使用两个 Tor 流量类型数据集：

| 数据集 | 类别 | 表中样本总数 | 类别数 |
|---|---|---:|---:|
| ISCXTor2016 | Audio、Browsing、Chat、File-Transfer、Mail、P2P、Video、VoIP | 12,808 | 8 |
| TDTor | Audio、Browser、Mail、Message、P2P、Video、VoIP | 27,385 | 7 |

正文却称 ISCXTor “over 8000” 和 TDTor “over 12000”，与表 I、II 的 12,808 和 27,385 不一致。ISCXTor 描述为 85 个 PCAP、22.8GB；TDTor 为作者自采，但本地预印本没有给出公开下载地址、采集清单、校验值和复现 manifest。

这些类别是 Tor 应用或业务类型，不是恶意攻击大类。原文偶尔把实验写成 known/unknown attacks detection，但数据标签本身不能支持“未知攻击检测”这一扩大表述。

## 12. 数据拆分与四种设置缩译

原数据先按 6:2:2 划分训练、验证和测试。每个数据集构造 Setting 1 与 Setting 2：

- Setting 1：3 类 known，其余类别 unknown。
- Setting 2：5 类 known，其余类别 unknown。
- 初始训练只选择每个 known 类 30% 样本。
- no-expert：所有非 known 类合并为 unknown，不使用人工标签。
- with-expert：一致性检查发现的 unknown 可由专家标注并加入后续训练。

原文没有明确“30%”是完整 known 类总量的 30%，还是 6:2:2 后训练分区的 30%；也没有清楚说明 DBSCAN 使用哪个分区的未标注池。若测试样本进入迭代聚类，就是直接测试泄漏；即使仅使用未标注训练分区，仍属于目标未知无标签训练 P2。

作者最初把样本数最大的类别选为 known，并承认这隐含“unknown 总是少数类”的假设。随后又根据类别识别难度重新定义 known 类以降低配置影响，但未说明难度只由独立 validation 得到，存在 test-informed split 风险。

## 13. Setting 的具体类别缩译

ISCXTor Setting 1 的 known 为 VoIP、P2P、File-Transfer，unknown 为 Browsing、Video、Mail、Audio、Chat。ISCXTor Setting 2 增加 Video、Chat 为 known，unknown 为 Browsing、Mail、Audio。

TDTor Setting 1 的 known 为 Browser、Mail、P2P，unknown 为 VoIP、Message、Video、Audio。TDTor Setting 2 增加 VoIP、Message 为 known，unknown 为 Video、Audio。

类别组合是固定的两个场景，不是 leave-one-family-out 全矩阵，也没有多随机种子、均值、标准差或显著性检验。

## 14. no-expert 定量结果缩译

表 IV、V 报告 Accuracy、Precision、Recall 和 FPR：

| 数据集/设置 | 方法 | Accuracy | Precision | Recall | FPR |
|---|---|---:|---:|---:|---:|
| ISCXTor S1 | CVAE-EVT | 0.7381 | 0.7030 | 0.5665 | 0.1009 |
| ISCXTor S1 | Cls-Anomaly | 0.7991 | 0.7790 | 0.8256 | 0.0645 |
| ISCXTor S1 | EVM | 0.8187 | 0.8145 | 0.8046 | 0.0673 |
| ISCXTor S1 | M3S-UPD | 0.9469 | 0.9480 | 0.9365 | 0.0204 |
| ISCXTor S2 | CVAE-EVT | 0.7650 | 0.6365 | 0.6079 | 0.0512 |
| ISCXTor S2 | Cls-Anomaly | 0.7791 | 0.6878 | 0.6443 | 0.0476 |
| ISCXTor S2 | EVM | 0.7733 | 0.7064 | 0.7710 | 0.0432 |
| ISCXTor S2 | M3S-UPD | 0.8456 | 0.7812 | 0.8619 | 0.0289 |
| TDTor S1 | CVAE-EVT | 0.6903 | 0.7152 | 0.7416 | 0.1100 |
| TDTor S1 | Cls-Anomaly | 0.7175 | 0.7475 | 0.7912 | 0.0961 |
| TDTor S1 | EVM | 0.7241 | 0.7794 | 0.6697 | 0.1158 |
| TDTor S1 | M3S-UPD | 0.9428 | 0.9471 | 0.9409 | 0.0222 |
| TDTor S2 | CVAE-EVT | 0.8187 | 0.7009 | 0.7901 | 0.0367 |
| TDTor S2 | Cls-Anomaly | 0.8008 | 0.8119 | 0.7842 | 0.0395 |
| TDTor S2 | EVM | 0.7442 | 0.6951 | 0.7211 | 0.0517 |
| TDTor S2 | M3S-UPD | 0.9149 | 0.9146 | 0.9067 | 0.0169 |

M3S-UPD 在四个场景的表内指标均优于三种基线。不过论文没有定义这些 Precision、Recall、FPR 是 unknown 二分类、宏平均多分类，还是 N+1 混淆矩阵聚合。FPR 也不是 FPR@95TPR，无法与开放集安全指标直接对齐。

## 15. with-expert 与敏感性结果缩译

引入专家后，发现的 unknown 被标注成具体新类别并用于更新。ISCXTor 中部分新类准确率仍偏低：Setting 1 的 Video、Browsing、Mail 约为 97%、60%、61%，Chat 容易被分成 Mail，Audio 易被分成 Browsing；Setting 2 中 Browsing、Mail、Audio 约为 70%、69%、47%。TDTor 在作者报告的场景中 known 不低于 97%，新增类不低于 80%。

随着已知类样本比例从 10% 增至 90%，no-expert accuracy 在 ISCXTor S1/S2 从 85.28%/78.63% 增至 97.24%/94.38%，TDTor S1/S2 从 94.49%/85.90% 增至 96.20%/95.49%。这说明方法收益随初始标注比例显著变化，并非固定 few-shot 能力。

增加 unknown 类数量时总体 accuracy 下降。作者还观察到至少约 3 个 known 类后，专家标注比例才明显下降。这表明系统强依赖初始 known 覆盖和类别可分性。

## 16. 实验结论与可重复性缩译

论文认为，分类概率与嵌入簇的一致性可以在不合成 unknown 的情况下提升伪标签可靠性，并发现潜在 unknown。实验确实给出两个数据集、四个固定场景的正向结果，但复现所需的底层模型、输入特征、DBSCAN 参数、距离阈值、置信区间大小、迭代停止条件和完整阈值选择协议均未明确。

同时，no-expert 训练读取目标 unknown 的无标签样本；with-expert 进一步读取其真实标签。因此这些结果不能与 unknown 在训练和调参阶段完全不可见的 strict OSR 方法放在同一主表中。

## 17. 结论缩译

M3S-UPD 通过迭代利用未标注流量，逐步改善少标注分类器，并以簇对齐失败和低分类置信的联合条件识别 unknown。加入专家标注后，系统可把新类别转化为 known 并持续更新。该框架展示了开放世界适应价值，但其证据属于半监督、transductive 和专家参与协议，不是纯 known-only 开放集拒识。

# 第二部分：独立技术分析

## A. 一句话结论

M3S-UPD 的“几何对齐与分类置信不一致”可作为 CAEOS 冲突组件候选，但原文结果必须归入第二交付线的目标域无标签适应/专家更新，不能作为 strict-v4 unknown-blind 主线 SOTA 证据。

## B. 协议审计

- 初始监督训练：只使用 known 类少量标签。
- 未标注训练池：包含 known 与目标 unknown，DBSCAN 和全池置信排序均读取 target unknown 分布。
- no-expert：`P2-target-unknown-unlabeled-training/transductive`。
- with-expert：`P2-target-unknown-labeling/open-world-adaptation`。
- 阈值：t、tₜₒₚ、tᵦₒₜₜₒₘ 和 DBSCAN 参数来源不明，标记 `P3-threshold-selection-unclear`。
- split：固定类别组合，且存在基于识别难度重定义 known 的 test-informed 风险。
- 主表资格：不能进入 strict P0 主表；可进入第二交付线或协议敏感性附表。

## C. 两条交付线映射

第一交付线是静态 unknown-blind 检测：训练、风险公式和阈值均不能读取目标 unknown。M3S-UPD 不满足这一条件。

第二交付线是开放世界适应：允许观察无标签部署流，发现候选 unknown，并在专家标注后更新。M3S-UPD 正适合这一交付线。论文写作必须分别报告：更新前 unknown 检测、专家标注成本、更新后新类分类和遗忘程度。

## D. 多模态判定

M3S-UPD 不是多模态。分类概率和嵌入向量来自同一个分类器，DBSCAN 与 SoftMax 是同源表征的两种读出。它没有多个采集视图、独立编码器、模态可靠性或缺失模态处理。

但其一致性规则适合映射为 CAEOS 的同源冲突基线：比较 predictive evidence 与 geometric evidence 是否一致，再与真正的 packet、flow、payload 跨模态冲突机制对照。

## E. 冲突机制评价

优点：

- 使用“簇未对齐且低 SoftMax”双条件，优于单独 MSP 阈值。
- 中间置信样本暂缓处理，体现 abstention 思想。
- 高置信伪标签要求几何标签与分类标签一致，能够过滤部分确认偏差。

缺点：

- 两种证据共享同一 encoder，误差高度相关。
- conflict 只有离散规则，没有连续风险或校准概率。
- 依赖全池比例和 DBSCAN 批处理，不是真正逐流在线。
- unknown 高置信且近 known 时会被错误吸收，形成自训练污染。
- 类别不平衡和非球形簇会破坏中心距离对齐。

## F. 三层指标缺口

| 层级 | 原文报告 | CAEOS 正式指标 | 判定 |
|---|---|---|---|
| 已知识别 | 混合总体 Accuracy/Precision/Recall | Known Macro-F1、Balanced Accuracy、per-class Recall、Benign FAR | 不充分 |
| 未知检测 | 未明确定义的 Recall/FPR | AUROC、AUPR-Out、FPR@95TPR、Unknown-F1 | 不充分 |
| 联合开放集 | 混合总体 Accuracy | OSCR、OpenAUC、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 无 | ECE、Brier、NLL | 缺失 |
| 持续学习 | 新类混淆矩阵 | 标注成本、更新增益、遗忘率、更新时延 | 部分覆盖 |

## G. 95%/5% 安全验收

论文表中 M3S-UPD 的 FPR 为 1.69% 至 2.89%，但不能据此填写 CAEOS 的“误报低于 5%”：

1. FPR 的正负类与聚合方式没有定义。
2. 它不是 unknown 为正类的 FPR@95TPR。
3. 数据集没有独立 benign 类，不能视为 Benign FAR。
4. accuracy 在 ISCXTor S2 仅 84.56%，TDTor S2 仅 91.49%。
5. target unknown 已经参与无标签训练，协议与 strict 安全表不同。

因此原文没有通过 CAEOS 的 95%/5% 验收。

## H. 数据与标签边界

ISCXTor 和 TDTor 的类别是 Tor 业务类型，不是恶意攻击家族。其 unknown 表示未见应用类别，而不是零日恶意攻击。CAEOS 可使用它们验证开放世界流量类型发现和同源冲突，但不能把结果归入“未知恶意家族检测”总表。

## I. CAEOS 采纳与否决

### 采纳

- 采纳嵌入簇与分类概率一致性作为冲突候选组件。
- 采纳中间置信样本 abstain，而非强制 known/unknown 二分。
- 采纳第二交付线中的候选池、专家标注和周期更新流程。
- 采纳更新前后分别评价的思想。

### 不采纳

- 不把使用 target unknown 无标签池的方法列为 P0。
- 不使用未说明来源的 DBSCAN 和距离阈值。
- 不把 Tor 应用类型称为攻击类别。
- 不用总体 accuracy 和未定义 FPR 替代三层指标。
- 不把同源 embedding/probability 一致性称为多模态证据融合。

## J. CAEOS 可执行实验

1. `E-M3S-01`：实现 geometry/probability consistency，只在第二交付线使用目标无标签池。
2. `E-M3S-02`：MSP、distance、DBSCAN alignment、双条件 conflict 四组消融。
3. `E-M3S-03`：记录每轮伪标签 precision、unknown 污染率和 deferred 比例。
4. `E-M3S-04`：把 t、tₜₒₚ、tᵦₒₜₜₒₘ 固定为 known-only validation 规则并做比例漂移测试。
5. `E-M3S-05`：比较无 target pool 的 P0、无标签 P2、专家标注 P2 三种协议。
6. `E-M3S-06`：更新后报告新类 Macro-F1、旧类遗忘率、标注量和更新时间。
7. `E-M3S-07`：以真正多模态 conflict 替换同源一致性，验证信息独立性是否带来增益。

## K. 可引用与不可引用主张

### 可引用

- M3S-UPD 用嵌入聚类对齐和分类概率一致性筛选伪标签与 unknown。
- 原文在两个 Tor 数据集的四个固定 no-expert 场景中优于所列三种基线。
- 专家标注可将检测出的 unknown 转化为新 known 并继续训练。
- 初始 known 类数量和样本比例显著影响持续学习结果。

### 不可引用

- M3S-UPD 是严格 unknown-blind 方法。
- 该文检测的是未知恶意攻击家族。
- 表中 FPR 小于 5% 等价于通过 CAEOS 安全验收。
- 该文是多模态证据冲突感知方法。
- arXiv 页眉代表 2015 年 IEEE 正式期刊发表。

## L. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过，本地 arXiv PDF 与全文抽取存在
- G2 身份门：仅通过至 arXiv v1；正式发表信息与 Zotero 待办
- G3 任务门：通过，但标签是 Tor 流量类型而非攻击家族
- G4 协议门：通过，`P2-target-unknown-unlabeled-training/P2-expert-adaptation/P3-threshold-selection-unclear`
- G5 方法门：通过
- G6 结果门：通过，表 I 至 V 与敏感性文字已核读
- G7 对比门：通过，但只有两个固定 split 且缺少同协议强基线
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
