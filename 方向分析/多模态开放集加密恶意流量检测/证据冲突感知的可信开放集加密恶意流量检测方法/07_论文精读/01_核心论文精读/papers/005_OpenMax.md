# 005 面向开放集深度网络 / Towards Open Set Deep Networks

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | 页码 | 本文缩译标题 | 图/表/公式 | 覆盖状态 | 省略内容及理由 |
|---|---:|---|---|---|---|
| Abstract、Introduction | 1-2 | 摘要、问题与贡献 | 图 1 | 已覆盖 | 压缩通用视觉识别背景 |
| Open Set Deep Networks | 2-4 | 开放空间风险、激活向量和元识别 | 算法 1-2；式(1)-(2)；定理 1 | 已覆盖 | 无 |
| Experimental Analysis | 4-5 | ImageNet 协议、参数与结果 | 图 2-4 | 已覆盖 | 图中无法可靠抄录的曲线点不逐点转写 |
| Discussion | 5-6 | 使用方式、失败与未来方向 | 图 5 | 已覆盖 | 无 |
| Supplement | 6-10 | 尾长、top-α、距离、定性失败和 1-vs-set | 图 6-14 | 已覆盖 | 大量定性图片不逐张描述，保留结论与代表数字 |

## 1. 文献身份

- 记录号：CAEOS-L3-005
- 英文题名：Towards Open Set Deep Networks
- 中文译名：面向开放集深度网络
- 作者：Abhijit Bendale、Terrance E. Boult
- 版本：arXiv:1511.06233v1，2015-11-19；正式论文发表于 CVPR 2016
- DOI：10.1109/CVPR.2016.263
- 本地 PDF：[1511.06233.pdf](F:/泉城实验室/二期/论文/异常检测/paper/1511.06233.pdf)
- 全文抽取：[005_Towards_Open_Set_Deep_Networks.txt](F:/泉城实验室/二期/论文/异常检测/方向分析/多模态开放集加密恶意流量检测/证据冲突感知的可信开放集加密恶意流量检测方法/07_论文精读/04_120篇全文抽取/005_Towards_Open_Set_Deep_Networks.txt)
- Zotero Item / Citation Key：pending / pending
- 精读日期：2026-08-06
- 当前状态：project_mapped；G10 未通过

## 2. 摘要缩译

深度网络在闭集视觉识别中表现出色，但必须从已知类别中选择一个标签，因此会对无意义图像、未见类别和某些对抗图像产生高置信错误。论文提出 OpenMax，在 SoftMax 前的激活向量空间为每个已知类拟合元识别模型，估计输入偏离该类训练分布的程度，再把部分已知类激活重新分配给显式 unknown 类。

OpenMax 的关键是把极值理论应用于倒数第二层/分类激活向量，而不是对归一化后的 SoftMax 分数直接拟合。作者证明，若元识别概率随样本到类均值激活向量的距离单调衰减，则阈值化后的 OpenMax 在该特征空间形成 compact abating probability，从而限制开放空间风险。ImageNet、开放类别和 fooling 图像实验表明，OpenMax 优于原始网络和 SoftMax 阈值拒识。

## 3. 引言缩译

闭集网络的 SoftMax 概率总和为 1，即使输入不属于任何已知类，也会产生最大类别。单纯用最大 SoftMax 概率阈值只能拒绝“不确定输入”，无法阻止某些未见或 fooling 图像获得极高已知类概率。

开放集识别必须同时控制已知类分类错误和把远离训练数据的开放空间错误标成已知类的风险。论文提出在激活向量空间测量距离，因为输入像素空间中的视觉距离不一定对应类别语义，而倒数第二层包含各类别关联响应模式。一个真实鲨鱼不仅激活目标鲨鱼类，也会以较稳定方式激活其他鲨鱼、鲸和大型鱼类；fooling 图像可能只抬高目标 logit，整体关联模式却与真实类均值相距较远。

贡献包括：将多类元识别用于深网激活向量；提出 OpenMax 和开放空间风险证明；在真实已知图像、未见类别与 fooling 图像上评价。

## 4. 开放集深网与元识别缩译

### 4.1 SoftMax 阈值的不足

设网络对输入 x 的 N 维激活向量为

v(x) = [v₁(x), …, vᴺ(x)]

SoftMax 类别概率为

P(y = j ∣ x) = exp[vⱼ(x)] ÷ ∑ᵢ₌₁ᴺ exp[vᵢ(x)]

该归一化不包含 unknown 类，也不要求高已知概率区域靠近训练样本。只要某一 logit 足够大，即使其他维度和整体模式异常，已知概率仍可接近 1。

### 4.2 类均值激活向量

对每个已知类 j，只使用被基础网络正确分类的训练样本，计算均值激活向量

μⱼ = meanᵢ v(xᵢⱼ)

它不是输入特征均值，而是该类样本在所有已知类别 logit 上的平均关联模式。单个 MAV 假设同一类不同视角在关联响应空间近似集中。

### 4.3 极值元识别

计算每个正确训练样本到 μⱼ 的距离，并取最大的 η 个距离拟合 Weibull 尾部分布。每类模型记为

ρⱼ = (τⱼ, κⱼ, λⱼ)

其中 τ、κ、λ 分别是位移、形状和尺度参数。论文使用 libMR FitHigh；主实验尾长 η = 20。距离采用归一化欧氏距离与余弦距离的加权组合。

ρⱼ 给出输入相对类 j 成为尾部离群点的概率。作者强调直接对 SoftMax 后验拟合 EVT 不合适，因为 SoftMax 已被强制归一为 logistic 形式，且 fooling 样本可以具有极高后验。

### 4.4 OpenMax 重标定

测试时先按原始激活从大到小排序，只重标定前 α 个类。对排名更高且距类 MAV 更远的类，使用 Weibull CDF 给出更强的削减。将重标定权重记为 ωⱼ(x)，则

v̂ⱼ(x) = vⱼ(x)ωⱼ(x)

被削减的总激活转移给显式 unknown 类：

v̂₀(x) = ∑ⱼ vⱼ(x)[1 − ωⱼ(x)]

随后对 0, 1, …, N 共 N + 1 个激活重新归一：

P̂(y = j ∣ x) = exp[v̂ⱼ(x)] ÷ ∑ᵢ₌₀ᴺ exp[v̂ᵢ(x)]

如果最大类别为 0，或最大 OpenMax 概率低于不确定性阈值 ε，则拒识为 unknown；否则输出最大已知类。

### 4.5 参数

- η：每类 Weibull 尾长，主实验为 20。
- α：参与重标定的 top 类数，主实验为 10。
- ε：最终最大概率拒识阈值。
- ρⱼ：每类已知训练分布尾部模型。

补充实验显示尾长增大有利于拒绝 unknown/fooling，但超过 20 后已知验证性能下降；α 小于 10 时 F-measure 下降，超过 10 收益很小；欧氏-余弦组合略优于单独欧氏或余弦。

## 5. 理论结果缩译

定理 1 声称：在激活向量上使用距离型元识别，并用 OpenMax 做单调加权变换，可构成开放集识别函数。

证明逻辑是：Weibull CDF 随 ‖μⱼ − x‖ 单调增加，所以类保留权重随距离单调衰减；它形成 compact abating probability。OpenMax 是该衰减概率的加权单调变换，因此阈值化 unknown 概率可以限制激活向量空间中的开放空间风险。

该定理只证明几何衰减与风险有界，不证明：

1. MAV 能正确描述真实类的多峰分布。
2. 未知类一定远离所有已知 MAV。
3. Weibull 概率经过校准。
4. 在任意分布漂移下 FPR95、OSCR 或 Unknown-F1 达到某数值。

## 6. 三类输入的解释缩译

### 6.1 真实已知类

正确已知样本的整体激活关联模式通常接近对应 MAV，因此 top 类激活只被轻微削减。

### 6.2 开放类别

未见类别仍会被基础网络映射到某个已知类。若整体激活模式远离该类 MAV，OpenMax 会把较多激活转移给 unknown。但若未知类是已知类的细粒度近邻，激活模式可能足够接近而被误接纳。

### 6.3 Fooling 图像

fooling 生成过程常只抬高目标 logit，没有同时构造与真实类别一致的其他关联响应，因此 AV 到 MAV 距离较大，容易被 OpenMax 拒绝。

### 6.4 对抗图像

论文图示了一些远类别对抗样本可被拒绝，但正式实验没有系统评价对抗图像，因为作者认为缺少有意义的对抗样本分布。若攻击把样本推向语义或激活空间邻近类，OpenMax 很可能失败。

## 7. 数据与实验协议缩译

基础模型为 Caffe Model Zoo 的 BVLC AlexNet，在 ILSVRC 2012 的 1000 类、约 130 万训练图像上训练。闭集测试使用 50,000 张 ILSVRC 2012 validation 图像。

未知类别取自 ILSVRC 2010 中未进入 2012 类表的约 360 类，采样 15,000 张。另使用 15,000 张由进化算法或像素梯度上升生成的 fooling 图像，每个 ILSVRC 2012 类 15 张。总测试集为 80,000 张。

每张图像使用 10 个 crop/channel，因此每类 MAV 和 Weibull 模型按 channel 分别拟合，最终输出 N + 1 类、10 个 channel 的概率，再跨 channel 平均。

## 8. 阈值与协议审计

类 MAV 和 Weibull 尾部只使用正确已知训练样本，这一阶段是 known-only。可是原文明确允许使用“训练图像加一批 open set 图像”网格搜索 ε、η、α，以 F-measure 校准总体尺度；fooling 图像不用于阈值选择。作者称使用 non-test data 调参，但辅助 unknown 仍参与拒识超参数选择。

因此协议应标为：

P1-auxiliary-unknown-calibration

它不是 CAEOS 所要求的 target unknown 完全不可见、阈值仅由 known validation 决定的 P0。CAEOS 复现必须区分：

- OpenMax-paper：允许辅助 unknown 校准，进入附表。
- OpenMax-strict：η、α 和 ε 只由 known validation、类内尾部和已知接纳率确定，进入主表。

## 9. 指标与结果缩译

论文在混合的已知、unknown 和 fooling 测试集上使用 F-measure，定义同时考虑正确已知分类、已知误分类以及 unknown/fooling 被误接纳。该定义不是现代以 unknown 为正类的 Unknown-F1，也不是 OSCR。

主要结果：

- OpenMax 相对最优 SoftMax 阈值方案提高约 4.3 个百分点。
- 相对无拒识基础网络提高约 12.3 个百分点。
- 在 80,000 张混合测试图像上，OpenMax 比最优 SoftMax 阈值多正确处理 3,450 张，比基础网络多 9,847 张。
- 补充实验中，FC8 上的 1-vs-set F-measure 为 0.407，OpenMax 为 0.595。
- OpenMax 对 fooling 图像的拒绝优势通常大于对细粒度开放类别的优势。

论文没有报告 Unknown AUROC、AUPR-Out、FPR@95TPR、Known Macro-F1、Balanced Accuracy、OSCR、ECE、Brier、NLL、多随机种子标准差或显著性检验。

## 10. 讨论与局限缩译

被拒样本可交给人工标注并增量学习，也可触发其他模态，或先做去噪再重新识别。OpenMax 还会拒绝一些含多目标或定位不佳的已知训练图像，可用于训练数据清理和目标定位。

主要失败模式：

1. 单 MAV 无法表达复杂多峰类内结构。
2. 细粒度 unknown 若与已知类激活模式接近，容易被接纳。
3. unknown 概率和最终阈值依赖辅助开放数据校准。
4. 重标定可能改变已知类别排序，并拒绝正确已知样本。
5. 理论只在 AV 空间限制开放空间风险。
6. 没有概率校准、跨域、缺失模态或真实安全流量实验。

# 第二部分：独立技术分析

## A. 一句话结论

- OpenMax 是后处理式开放集基线：类均值原型 + EVT 尾部 + top-logit 重分配 + 显式 unknown。
- 对 CAEOS 的直接价值：必须作为 prototype/EVT 风险线的经典基线。
- 最大边界：原论文使用辅助 unknown 调参，单 MAV 对细粒度未知攻击和多峰流量类可能失效。

## B. 任务与威胁模型

- 对象：ImageNet 图像，不是网络流量。
- 类空间：1000 个 known 类加统一 unknown。
- 训练 unknown：基础网络和 Weibull 拟合不见 unknown；超参数校准可见辅助 open-set 图像。
- 攻击者：没有正式安全攻击者模型；fooling 图像是额外异常源。
- 输出：N 个已知类或 unknown。
- 多模态：否；10 crop 是数据增强/多视角推理，不是独立模态。

## C. 与 CAEOS 的可比性

| 模块 | 可比性 | 说明 |
|---|---|---|
| 已知类分类 | C0 | 图像任务与恶意流家族不同 |
| 类原型距离 | C1 | 可直接迁移到流量嵌入 |
| EVT 尾部 | C1 | 可作为 known-only 风险标定 |
| unknown 重分配 | C1 | 可与 energy、support、conflict 对照 |
| 多模态冲突 | C0 | OpenMax 无多视图意见 |
| 校准指标 | C0 | 原文未报告 |

## D. 关键复现条件

- 每类只用正确分类的训练样本计算 MAV。
- 距离默认欧氏与余弦组合。
- 每类独立拟合 Weibull 尾部。
- 主参数 η = 20、α = 10。
- 最终仍需 ε 拒识阈值。
- 对多 crop/channel 分别拟合再平均。
- 官方实现依赖 libMR；代码版本和提交待核验。

## E. 95%/5% 映射

OpenMax 原文没有 Benign FAR、已知恶意家族 Macro-F1、FPR@95TPR 或 OSCR，因此不能判断 95%/5% 安全门。开放集 F-measure 0.595 也不能换算成未知检出率或良性误报。

## F. CAEOS 采纳/否决

| 对象 | 结论 | 理由 |
|---|---|---|
| MAV + EVT | 必做基线 | 经典后处理、实现成本低 |
| 单 MAV 作为自有创新 | 否决 | 已是 OpenMax 核心 |
| 辅助 unknown 调参进入主表 | 否决 | 不符合 strict known-only |
| unknown 激活重分配 | 进入组件对照 | 可与原型距离直接阈值比较 |
| 有界开放空间风险写成性能保证 | 否决 | 理论边界被扩大 |
| 多模态融合主张 | 否决 | 方法没有模态证据与冲突 |

## G. CAEOS 可执行实验

| ID | 自变量/对照 | 固定条件 | 主指标 | 目的 |
|---|---|---|---|---|
| E-OM-01 | OpenMax-paper vs OpenMax-strict | 同 encoder/split/seed | AUROC/FPR95/OSCR | 量化辅助 unknown 调参偏差 |
| E-OM-02 | 单 MAV vs 多原型 | 同尾部拟合预算 | Known Macro-F1/Unknown AUROC | 检验类内多峰 |
| E-OM-03 | 欧氏、余弦、组合距离 | 同原型和阈值 | 三层指标 | 确定流量嵌入距离 |
| E-OM-04 | 每模态 OpenMax vs 融合后 OpenMax | 三模态 encoder 固定 | OSCR/ECE | 判断风险应在何层拟合 |
| E-OM-05 | η 与 α known-only 敏感性 | 5 seeds | worst-case FPR95 | 排除单配置偶然性 |
| E-OM-06 | 近邻 family unknown | leave-family-out | FPR95/OSCR | 压测 OpenMax 已知失败模式 |

## H. 可引用与不可引用主张

待 G10 通过后可引用：

1. OpenMax 用类激活均值和 EVT 尾部将已知激活质量重分配给 unknown。
2. 其开放空间风险证明建立在激活空间中的单调衰减模型上。
3. 原实验使用 ImageNet 2010 未进入 2012 的类别和 fooling 图像。

不可引用：

1. OpenMax 已在恶意流量上达到 SOTA。
2. OpenMax 概率已校准。
3. OpenMax 不需要任何 unknown 数据调参。
4. 理论证明未知检测率达到某阈值。

## I. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过
- G2 身份门：通过至 DOI/PDF，Zotero 待办
- G3 任务门：通过
- G4 协议门：通过，P1-auxiliary-unknown-calibration
- G5 方法门：通过
- G6 结果门：通过
- G7 对比门：通过
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：project_mapped，不能标 complete
