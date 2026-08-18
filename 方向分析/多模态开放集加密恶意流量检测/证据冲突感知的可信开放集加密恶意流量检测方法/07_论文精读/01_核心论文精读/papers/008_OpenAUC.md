# 008 面向 AUC 的开放集识别 / OpenAUC: Towards AUC-Oriented Open-Set Recognition

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | 本文对应内容 | 覆盖状态 |
|---|---|---|
| Abstract | 第 2 节 | 已覆盖 |
| 1 Introduction | 第 3 节 | 已覆盖 |
| 2 Preliminary | 第 4 节 | 已覆盖 |
| 3 Existing Metrics | 第 5 至 7 节 | 已覆盖 |
| 4 OpenAUC | 第 8 至 11 节 | 已覆盖 |
| 5 Experiments | 第 12 至 14 节 | 已覆盖 |
| 6 Broad Impact | 第 15 节 | 已覆盖 |
| 7 Conclusion | 第 16 节 | 已覆盖 |
| Appendices | 第 10、13、14 节按证明、实现和附加实验合并 | 关键内容已覆盖 |

## 1. 文献身份

- 标题：OpenAUC: Towards AUC-Oriented Open-Set Recognition。
- 中文题名：OpenAUC：面向 AUC 的开放集识别。
- 作者：Zitai Wang、Qianqian Xu、Zhiyong Yang、Yuan He、Xiaochun Cao、Qingming Huang。
- 发表：NeurIPS 2022。
- arXiv：2210.13458v3，2023-02-22 版本。
- 本地全文：`paper/2210.13458.pdf`。
- 项目页：`wang22ti/OpenAUC`。
- 研究对象：图像开放集识别的评价指标与可优化目标，不是流量方法，也不是多模态方法。

## 2. 摘要缩译

开放集识别要求模型同时正确处理闭集样本和开放集样本，但既有评价指标与这一联合目标并不完全一致。由闭集分类扩展而来的 open-set F-score、Youden 指数和 Normalized Accuracy，可能让较差的未知拒识被较好的闭集分类掩盖；仅用于新颖性检测的 AUC 又忽略已知类分类是否正确。

论文提出单一数值指标 OpenAUC。它用一个已知样本和一个未知样本组成样本对：只有当已知样本被正确分类时，才检查未知分数是否把未知样本排在已知样本之前。因此，已知分类和未知排序以乘积形式耦合。作者进一步把 OpenAUC 写成经验风险，使用已知类特征的 manifold mixup 生成代理开放集样本，构造端到端训练目标。标准与细粒度图像基准上的结果支持该指标和优化方法。

## 3. 引言与指标问题缩译

OSR 包含两个同时发生的行为：正确分类已知样本，以及把未知样本从已知集合中拒绝。论文把既有指标分为两类：

1. 分类扩展类指标：先由阈值构造含 unknown 的混淆矩阵，再计算 F-score、Youden 或加权准确率。
2. 新颖性排序指标：把所有已知类合并为 known 超类，用 AUC 衡量 known 与 unknown 的排序。

第一类受固定阈值、未知比例和混淆矩阵聚合方式影响，甚至可能鼓励不合理的拒识决策。第二类不依赖阈值，但完全不关心已知类内部是否分类正确。把 accuracy 与 AUC 分别报告虽然直观，却形成多目标比较，也无法用一个数表达两项任务是否由同一模型同时完成。

论文提出的研究问题是：是否存在与 OSR 联合目标一致的单一数值指标？OpenAUC 给出的回答是，把已知分类正确作为未知排序得分成立的前置条件。

## 4. 任务定义与指标四项要求缩译

已知训练样本为：

> zᵢ =（xᵢ，yᵢ），yᵢ ∈ Yₖ = {1，…，C}。

所有未知类在决策层合并为一个超级未知类 Yᵤ = {C + 1}。拒识器 R = g₁ ∘ r，其中 r（x）是开放集风险分数；当 r（x）大于阈值 t 时，样本被判为 unknown。未被拒绝的样本再由已知分类器 h = g₂ ∘ f 分到某个已知类。

论文提出 OSR 指标应满足：

- P1：已知样本不仅要获得较低未知分数，还必须被 h 分类正确。
- P2：未知样本应获得较高未知分数。
- P3：指标应尽量不依赖阈值，因为部署时 unknown 比例通常未知。
- P4：输出单一数值，便于比较整体性能。

这四项要求面向模型排序与方法研究。安全验收仍需要固定阈值上的已知召回、良性误报和未知拒识指标，不能只保留 P4。

## 5. Open-set F-score 与 Youden 指数批判缩译

open-set F-score 汇总已知类别的 precision 和 recall：

> F = 2 × Pₖ × TPRₖ ÷（Pₖ + TPRₖ）。

Youden 指数进一步加入已知类真负率：

> J = TPRₖ + TNRₖ − 1。

论文的命题 1 指出，如果指标不直接约束超级未知类的真阳性、假阴性和假阳性，就可能构造出另一个预测器：指标值不变，但所有未知样本都被错误接收为已知。这被称为不一致性质 I。其要点不是 F-score 本身毫无价值，而是仅聚合已知类混淆项不能保证未知拒识得到真实评价。

## 6. Normalized Accuracy 批判缩译

Normalized Accuracy 把已知准确率 AKS 与未知准确率 AUS 加权：

> NAcc = λₙₐ × AKS +（1 − λₙₐ）× AUS。

当 λₙₐ 与测试 unknown 比例匹配时，它可对应整体准确率；但真实部署前通常不知道该比例。命题 2 表明，在一定条件下可以选择一个更差的拒识器，使所有 unknown 都被接收为 known，同时 NAcc 反而更高。论文将其称为不一致性质 II：固定聚合权重和阈值可能偏好错误的 known/unknown 取舍。

## 7. 传统 AUC 与简单聚合批判缩译

传统未知检测 AUC 可写成成对排序概率：

> AUC = E［𝟙（r（xᵤ）> r（xₖ））］。

它衡量随机抽取一个未知样本 xᵤ 和一个已知样本 xₖ 时，风险分数把未知排在已知之前的概率。AUC 对阈值和类别比例不敏感，但不检查 xₖ 的已知类别预测是否正确。

把 closed-set accuracy 与 AUC 分别计算后再求和、求积或逐样本相加，也可能让两个模型在聚合数值上相同，但联合 OSR 行为不同。论文将这种问题称为不一致性质 III。其真正针对的是任意标量聚合，不能据此否定三层指标体系；多指标报告的目的正是保留不同错误的可解释性，而不是强行生成一个总分。

## 8. OSCR 与 OpenAUC 的关系缩译

OSCR 曲线横轴是未知样本被接收为 known 的比例，纵轴是已知样本既被接收又分类正确的比例。论文将二者推广为：

> OFPR（t）= Eᵤ［𝟙（r（x）≤ t）］，

> COTPR（t）= Eₖ［𝟙（r（x）≤ t 且 y = h（x））］。

OFPR 是 unknown 被误接收的概率，COTPR 是 known 在阈值下被接收且分类正确的概率。OpenAUC 是 OFPR-COTPR 曲线下面积，因此可视为 OSCR 面积的广义、可计算形式。

原文积分式把积分上下限印为负无穷到正无穷，但横轴 OFPR 是概率，定义域应落在 0 至 1。项目实现应优先使用下一节的成对概率定义，不照抄该积分上下限。

## 9. OpenAUC 定义缩译

命题 4 给出核心等价式：

> OpenAUC = E［𝟙（yₖ = h（xₖ））× 𝟙（r（xᵤ）> r（xₖ））］。

第一个指示项要求已知样本分类正确；第二个指示项要求未知样本风险高于该已知样本。只有两个条件同时成立，该 known-unknown 样本对才贡献 1。

由此得到三个性质：

1. 对 known，既检查已知类别分类，也检查其风险排序。
2. 对 unknown，要求风险分数把它排在 known 之前。
3. 通过乘积把已知识别和未知排序耦合，而非独立相加。

OpenAUC 的上界受闭集准确率限制。若已知分类错误，即使未知排序正确，该样本对仍记为 0。这是指标有意设计的联合惩罚，也是解释结果时必须保留的语义。

## 10. 理论性质缩译

命题 5 至 7 分别说明 OpenAUC 不受论文定义的三类不一致构造影响。特别地，命题 6 给出阈值行为的下界。若 OpenAUC = k，且某阈值处未知类相关 FPR 为 a ≠ 0，则：

> TPRᵤ ≥ 1 −（1 − k）÷a。

随着 k 趋近 1，更容易找到具有非零未知召回的阈值。但该结论是带条件的下界，不等于 OpenAUC 高就自动满足任意固定的 FPR@95TPR，更不等于良性流量 FAR 低于 5%。

论文没有给出开放集学习的一般化界，并在 Broad Impact 中明确把这一点列为未解决问题。

## 11. OpenAUC 风险与训练方法缩译

等价风险写为：

> R（f，r）= E［𝟙（yₖ ≠ h（xₖ））+ 𝟙（yₖ = h（xₖ））× 𝟙（r（xᵤ）≤ r（xₖ））］。

第一项惩罚 known 分类错误；只有 known 分类正确时，第二项才惩罚 unknown 排序错误。经验目标使用交叉熵 L 和连续 AUC 代理损失 ℓ：

> R̂ =（1 ÷ Nₖ）∑ᵢL（h（xᵢ），yᵢ）+（λ ÷（NₖNᵤ））∑ᵢ∑ⱼ𝟙（yᵢ = h（xᵢ））ℓ（r（xⱼ）−r（xᵢ））。

论文训练集没有真实开放集样本。作者在特征空间对不同已知类样本做 manifold mixup：

> x̃ᵤ = λᵦfₚᵣₑ（xᵢ）+（1 − λᵦ）fₚᵣₑ（xⱼ），且 yᵢ ≠ yⱼ。

λᵦ 来自 Beta（α，α）分布，默认 α = 2。这些合成特征被当作代理 unknown，用于 AUC 风险项。由于合成点可能靠近第三个已知类流形，作者再用 λ 控制排序项权重，并在 {0.1，0.2，0.3，0.4，0.5，0.6} 中搜索。

这种方法属于 known-only synthetic unknown，而非真实目标 unknown 训练。合成 unknown 的分布是否代表真实未知攻击，必须单独验证。

## 12. 数据集与实验协议缩译

- MNIST、SVHN、CIFAR10：随机选择 4 个类作为 unknown。
- CIFAR+10、CIFAR+50：4 个 CIFAR10 类为 known，CIFAR100 中 10 或 50 个不重叠类为 unknown。
- TinyImageNet：20 类 known，180 类 unknown。
- CUB：按照语义新颖性构造 Easy、Medium、Hard unknown。
- 比较方法：Softmax、GCPL、RPL、ARPL、ARPL+CS、CE+ 和去掉条件开关的 Acc+AUC。

主干在常规数据集采用 VGG32，CUB 采用 ResNet50。大多数实验训练 600 epochs、batch size 128；TinyImageNet 为 64，CUB 为 32。采用余弦退火并在第 200、400 epoch 重启学习率，统一使用 RandAugment 和 label smoothing。

论文给出 λ 敏感性曲线，并称 0.1 或 0.2 最优，但正文与附录没有明确 λ 是在 known-only validation、代理 unknown validation 还是最终目标 unknown 结果上选定。该项必须标记超参数选择风险。

## 13. 标准基准结果缩译

表 2 报告 OpenAUC 的均值与标准差：

| 方法 | MNIST | SVHN | CIFAR10 | CIFAR+10 | CIFAR+50 | TinyImageNet |
|---|---:|---:|---:|---:|---:|---:|
| Softmax | 99.2±0.1 | 92.8±0.4 | 83.8±1.5 | 90.9±1.3 | 88.5±0.7 | 60.8±5.1 |
| GCPL | 99.1±0.2 | 93.4±0.6 | 84.3±1.7 | 91.0±1.7 | 88.3±1.1 | 59.3±5.3 |
| RPL | 99.4±0.1 | 93.6±0.5 | 85.2±1.4 | 91.8±1.2 | 89.6±0.9 | 53.2±4.6 |
| ARPL | 99.4±0.1 | 94.0±0.6 | 86.6±1.4 | 93.5±0.8 | 91.6±0.4 | 62.3±3.3 |
| ARPL+CS | 99.5±0.1 | 94.3±0.3 | 87.9±1.5 | 94.7±0.7 | 92.9±0.3 | 65.9±3.8 |
| CE+ | 99.1±0.2 | 93.9±0.4 | 88.1±1.7 | 93.2±0.6 | 90.2±0.4 | 74.3±3.9 |
| Acc+AUC | 99.3±0.2 | 94.0±0.9 | 87.6±1.9 | 93.6±1.0 | 92.0±0.5 | 74.0±4.0 |
| OpenAUC 优化 | 99.4±0.1 | 95.0±0.4 | 89.2±1.9 | 95.2±0.7 | 93.6±0.3 | 75.9±4.1 |

作者的方法在六个基准的 OpenAUC 上均取得表中最高值。Acc+AUC 低于条件耦合目标，支持“只有 known 分类正确时才计算排序损失”的设计。但这些是图像数据和原文 split 上的结果，不能直接作为加密流量数值基线。

## 14. CUB 细粒度结果缩译

CUB 的 Close-set Accuracy、AUC 和 OpenAUC 如下，开放集指标按 Easy / Medium / Hard 报告：

| 方法 | Closed Accuracy | AUC | OpenAUC |
|---|---:|---:|---:|
| Softmax | 78.1 | 79.7 / 73.8 / 66.9 | 67.2 / 63.0 / 57.8 |
| GCPL | 82.5 | 85.0 / 78.7 / 73.4 | 74.7 / 70.3 / 66.7 |
| RPL | 82.6 | 85.5 / 78.1 / 69.6 | 74.5 / 69.0 / 62.4 |
| ARPL | 82.1 | 85.4 / 78.0 / 70.0 | 74.4 / 68.9 / 62.7 |
| CE+ | 86.2 | 88.3 / 82.3 / 76.3 | 79.8 / 75.4 / 70.8 |
| ARPL+ | 85.9 | 83.5 / 78.9 / 72.1 | 76.0 / 72.4 / 66.8 |
| OpenAUC 优化 | 86.2 | 88.8 / 83.2 / 78.1 | 80.2 / 76.1 / 72.5 |

OpenAUC 优化方法的 Error@95%TPR 为 28.1 / 39.7 / 47.6。即使它在对比方法中最好，hard split 的错误率仍接近一半。这说明联合面积指标的领先不等于达到安全门槛。

## 15. 广泛影响与局限缩译

作者承认没有任何指标适合所有应用。OpenAUC 汇总全部 OFPR 范围，但自动驾驶等高风险应用只关心高 unknown recall 或低 OFPR 区域。全曲线面积可能被与部署无关的工作点影响，带来安全误判。作者建议未来研究 partial OpenAUC，只积分目标 OFPR 区间；代价是优化更困难。此外，OpenAUC 优化的一般化界仍未建立。

## 16. 结论缩译

论文通过理论反例说明若干既有 OSR 指标与联合目标存在不一致，提出同时耦合 known 分类正确与 unknown 排序的 OpenAUC，并给出基于合成未知特征的端到端优化方法。实验结果支持该方法提升 OpenAUC，但其适用范围仍受工作点、超参数选择和合成 unknown 代表性限制。

# 第二部分：独立技术分析

## A. 一句话结论

OpenAUC 值得加入 CAEOS 的第三层联合指标和消融目标，但它不能取代 Known Macro-F1、Unknown AUROC、FPR@95TPR、良性 FAR 与校准指标；论文自身也承认全曲线面积不适合直接作安全工作点验收。

## B. 协议审计

- 真实 target unknown 训练：未使用。
- 代理 unknown 训练：使用不同 known 类的特征 mixup。
- 目标 unknown 测试：用于计算 OpenAUC、AUC 和其他开放集指标，合理。
- λ 选择：候选集合明确，但独立验证来源不明确。
- unknown F-score：附录明确使用 optimal threshold，属于 test-optimal 描述值，不能进入严格部署主表。
- 协议等级：训练数据层面为 `P0-known-only-synthetic-unknown-candidate`；λ 选择和 optimal-threshold F-score 另标 `P3-hyperparameter/threshold-risk`。
- 主表资格：OpenAUC 指标可进入联合层；OpenAUC 优化方法只有在 λ 与阈值均由 known-only validation 冻结后才具备 strict 主表资格。

## C. “联合指标”与“三层指标”的关系

论文批判的是把 accuracy 与 AUC 随意聚合为一个数，而不是反对分别报告两个任务。CAEOS 应这样处理：

1. 第一层保留已知类识别，诊断分类器是否学会已知攻击族。
2. 第二层保留未知类检测，诊断风险分数能否区分未知攻击。
3. 第三层同时报告 OSCR 和 OpenAUC，诊断“已知分类正确且未知排序正确”的联合行为。

OpenAUC 是补充指标，不是主表六指标的替代物。若只给 OpenAUC，仍无法知道失败来自闭集分类、未知排序还是固定阈值。

## D. 公式与实现审计

推荐直接实现成对估计：

> OpenAUC =（1 ÷（NₖNᵤ））∑ᵢ∑ⱼ𝟙（yᵢ = h（xᵢ））𝟙（r（xⱼᵤ）> r（xᵢₖ））。

也可把分类错误的 known 样本风险置于所有 unknown 风险之上，再调用标准 AUC 工具。实现时必须固定：

- 风险方向统一为“越大越未知”。
- 分数相等时采用 0、0.5 还是稳定排序。
- known 和 unknown 的样本权重以及分组聚合方式。
- 多 seed、多场景时先按场景计算，不能把所有流拼接后让大数据集支配结果。

原文积分上下限与概率横轴不一致，论文写作时采用成对定义，避免复现符号错误。

## E. 多模态与 CAEOS 映射

原文没有多模态机制。可迁移的组件是条件排序损失：

- 以融合风险 rₘ（x）计算主 OpenAUC。
- 以 packet、flow、payload 各自风险计算单模态 OpenAUC。
- 只有融合模型已知攻击分类正确时，优化 unknown 代理样本相对真实 known 的排序。
- conflict 风险是否有效，可用其单项 OpenAUC 与联合 OpenAUC 检验。

如果代理 unknown 由任意两个已知攻击特征直接插值，可能落入另一个真实已知家族。CAEOS 必须使用类间距离过滤、近邻排除或原型占用检查，并在消融中报告代理污染比例。

## F. 95%/5% 安全验收映射

OpenAUC 不直接回答以下验收项：

- Known Macro-F1 是否至少 95%。
- Balanced Accuracy 是否至少 95%。
- Benign FAR 是否不超过 5%。
- Unknown FPR@95TPR 是否不超过 5%。
- 在冻结阈值上 Unknown Rejection Rate 是否达到目标。

CUB hard 的 Error@95%TPR 为 47.6%，已经说明“OpenAUC 最优”与“5% 错误率通过”是完全不同的结论。安全表必须基于 validation 冻结阈值后的测试结果逐格验收。

## G. 对 CAEOS 的采纳与否决

### 采纳

- 将 OpenAUC 增加到第三层联合开放集附表。
- 增加条件 AUC 排序损失作为自有算法候选组件。
- 保留 OSCR 曲线，并比较 OpenAUC 与 OSCR 的一致性。
- 在 hard unknown 和低 OFPR 区间补充 partial OpenAUC。
- 对代理 unknown 训练单列协议与污染审计。

### 不采纳

- 不用 OpenAUC 替代三层指标。
- 不采用目标 unknown 上的 optimal threshold F-score 作为正式结果。
- 不把 mixup 样本称为真实未知攻击。
- 不直接采用原文 λ = 0.1 或 0.2，必须在 CAEOS 的 known-only validation 上重选。
- 不根据全区间面积宣称满足 95%/5% 安全标准。

## H. CAEOS 可执行实验

1. `E-OAUC-01`：在所有 strict-v4 场景补算 OpenAUC，并与 OSCR、AUROC 做相关性分析。
2. `E-OAUC-02`：CE、CE+AUC、CE+conditional OpenAUC 三组同协议消融。
3. `E-SYN-03`：无代理 unknown、特征 mixup、原型边界合成三种训练对照。
4. `E-CONTAM-04`：统计合成样本落入第三已知类近邻或原型接受域的比例。
5. `E-PARTIAL-05`：计算 OFPR ∈［0，0.05］区域的 partial OpenAUC。
6. `E-VIEW-06`：比较单模态与融合风险的 OpenAUC，检验冲突融合增量。
7. `E-GATE-07`：保持 OpenAUC 排序领先的同时，检查冻结阈值后的 95%/5% 验收是否真正改善。

## I. 可引用与不可引用主张

### 可引用

- 传统未知 AUC 忽略已知类内部是否分类正确。
- OpenAUC 把已知分类正确和未知风险排序耦合为成对概率。
- OpenAUC 可视为广义 OSCR 曲线的面积指标。
- 原文在六个标准图像基准上取得最高 OpenAUC。
- 全区间 OpenAUC 可能不适合只关心低 OFPR 的安全应用。

### 不可引用

- OpenAUC 可取代全部已知、未知和校准指标。
- OpenAUC 最优意味着已知准确率超过 95% 且误报低于 5%。
- manifold mixup 生成了真实未知攻击分布。
- 原文已经证明 OpenAUC 在多模态加密流量上有效。
- 论文中的 optimal-threshold F-score 符合 strict unknown-blind 协议。

## J. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过，本地 PDF 与全文抽取存在
- G2 身份门：通过至 PDF、arXiv、NeurIPS，Zotero 待办
- G3 任务门：通过
- G4 协议门：通过，`P0-known-only-synthetic-unknown-candidate/P3-hyperparameter-threshold-risk`
- G5 方法门：通过
- G6 结果门：通过
- G7 对比门：通过
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
