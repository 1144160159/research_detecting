# 010 可靠冲突多视图学习 / Reliable Conflictive Multi-View Learning

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | PDF 页码 | 本文缩译标题 | 图/表/公式 | 覆盖状态 | 省略内容及理由 |
|---|---:|---|---|---|---|
| Abstract、Introduction | 1-2 | 摘要与引言 | 图1-2 | 已覆盖 | 压缩一般多视图应用举例 |
| Related Work | 2 | 相关工作 | 无 | 已覆盖 | 合并逐篇引用 |
| Method: Problem Definition | 2-3 | 问题定义 | 图3 | 已覆盖 | 无 |
| Method: Evidential Learning | 3-5 | 视图证据学习 | 式(1)-(5)、(13)-(15) | 已覆盖 | 无 |
| Method: Conflictive Aggregation | 4-6 | 冲突意见聚合与理论分析 | 式(6)-(12)、(16)-(17)；命题1-2 | 已覆盖 | 无 |
| Experiments | 6-7 | 实验设置与结果 | 表1-3；图4-5 | 已覆盖 | 图中密度曲线不抄无法核对的点值 |
| Conclusion | 7 | 结论 | 无 | 已覆盖 | 无 |
| Technical Appendix | 官方仓库独立附件 | 附录审计 | 算法1、命题证明、表1、图1 | 已覆盖 | 已核验仓库 HEAD `c9c5ab41` 的独立附录 |

## 1. 标题、摘要与关键词

### 1.1 标题

中文题名为“可靠冲突多视图学习”。作者把问题命名为 Reliable Conflictive Multi-view Learning（RCML），提出的方法名为 Evidential Conflictive Multi-view Learning（ECML）。

### 1.2 摘要缩译

多视图学习把多个特征组合为更完整的数据描述，但以往通常假定视图严格对齐。真实数据中会出现低质量的“冲突实例”：不同视图表达互相冲突的信息。既有方法多删除这类实例或替换冲突视图，然而实际应用仍需对冲突实例作出决策并说明决策是否可靠。作者据此提出 RCML 问题，要求模型为冲突数据同时输出类别和可靠性。ECML 先由各视图网络收集对每一类别的非负证据，形成包含 belief 和 reliability 的视图意见；再用冲突意见聚合策略融合。作者声称该策略能精确表达共同可靠性与视图特有可靠性的关系，并在6个数据集上验证（PDF第1页）。

### 1.3 关键词

原文首页未列独立关键词。可定位术语包括冲突多视图学习、证据深度学习、主观逻辑、冲突意见聚合；它们不是作者给出的正式 keyword 列表。

## 2. 引言缩译

多传感器、用户图文评论等数据通常含一致和互补信息，但严格对齐假设会被噪声或错配打破。图1给出食品图文例子：文本指向“sauce”，其他视图却指向“burger”。已有两类处理方式，一类把跨视图不一致视为离群点并删除，另一类先估计对齐关系，再用另一实例的视图替换冲突内容。作者认为这没有回答真正部署问题：当冲突实例必须被分类时，系统不仅要给类别，还要回答“这项决策是否可靠”（PDF第1-2页）。

ECML 的两阶段思路是：各视图 EDL 产生 evidence 和 Dirichlet 意见；用 projected probability 的距离乘双方 certainty 定义冲突度；训练时最小化正常训练样本的跨视图冲突，以减少模型自身错误造成的伪冲突；推理时用新的冲突意见平均规则聚合。作者特别批评 TMC 一类规则的性质：加入任何意见后 uncertainty 都下降，而当新意见不可靠或与原意见冲突时，合理行为应是 uncertainty 上升（PDF第2页）。

## 3. 相关工作缩译

冲突多视图研究主要是多视图离群检测和部分视图对齐。前者比较各视图的聚类/自表示行为以找离群实例，后者学习对齐矩阵并重建配对；共同目标仍是清理数据，而非为原冲突实例给可靠决策。另一条线是不确定性深度学习，包括单次确定性方法、贝叶斯网络、集成和测试时增强。TMC 把 EDL 扩展到多视图，后续方法继续设计意见聚合，但通常具有“融合后 uncertainty 降低”的单调性质。ECML 把这点视为主要缺口（PDF第2页）。

## 4. 预备知识、问题定义与威胁模型缩译

RCML 数据有 V 个视图、N̄ 个 normal instances 和 Ñ 个 conflictive instances。第 n 个样本第 v 个视图为 xₙᵛ ∈ ℝᴰᵛ，标签为 K 类 one-hot yₙ。训练集合只含 N̄ₜᵣₐᵢₙ 个正常实例；剩余正常实例和所有冲突实例构成测试集。模型目标是在两类测试样本上预测 yₙ，并给 uncertainty uₙ ∈ [0,1]，可靠性定义为 1 − uₙ（PDF第2-3页）。

图3把冲突分成两类：noise view 不属于任何目标类别；unaligned view 实际表达另一个类别。冲突测试实例是人工构造的，作者脚注承认没有真实 uncertainty 标签，只预期人工冲突样本应有较大 u。论文没有 unknown 类、开放集拒识或攻击者模型；它是闭集类别空间内的视图污染/错配问题。

## 5. 数据与预处理缩译

表1（PDF第6页）列出六个多视图数据集及维度：HandWritten 2,000样本、10类、六视图维度 240/76/216/47/64/6；CUB 11,788样本，实验取10类，图像/文本维度 1024/300；HMDB 6,718样本、51类、两视图均1000维；Scene15 4,485样本、15类、维度 20/59/40；Caltech101 8,677样本，正文称只取前10类而表1仍列 K = 101，两视图均4096维，存在正文与表格身份不一致，必须回看代码；PIE 680样本、68类、维度 484/256/279。

冲突测试集构造有两种。noise view：对部分测试实例的某个视图加标准差 σ 的高斯噪声；unaligned view：选择部分实例，把一个随机视图改成与真实标签不一致的另一实例信息。每种方法运行10次，报告均值和标准差。主表3使用的冲突实例比例、噪声强度组合、正常训练/测试比例、归一化和随机种子值全文未定位。图5的单独 uncertainty 实验明确在 CUB 测试集50%实例上加 σ ∈ {0.1,1,5,10} 的高斯噪声（PDF第6-7页）。

## 6. 方法全文缩译

### 6.1 总体架构

图2（PDF第3页）的信息流为：每视图 DNN fᵛ 输出对 K 类的证据 eₙᵛ；证据参数化 Dirichlet；由 Dirichlet 构造 (belief, uncertainty, base rate) 主观意见；用冲突意见聚合形成联合意见、类别概率和 u。训练额外最小化各视图意见的冲突度。

### 6.2 视图特有证据学习

式(1)要求 ∑ₖ bₖ + u = 1，式(2)以 Pₖ = bₖ + aₖu 得到 projected probability，通常均匀先验 aₖ = 1 ÷ K。式(3)-(4)给出 Dirichlet 密度和单纯形。网络用 ReLU 等非负输出替代 softmax，α = e + 1；式(5)给出：

bₖ = eₖ ÷ S = (αₖ − 1) ÷ S

u = K ÷ S，S = ∑ₖ(eₖ + 1)

作者把 u 解释为证据 vacuity，即观测越少、总证据越低，u 越大（PDF第3-4页）。

### 6.3 冲突意见聚合

定义1（式(6)-(8)，PDF第4页）对两个意见 A、B 计算：

bₖᴬ◇ᴮ = (bₖᴬuᴮ + bₖᴮuᴬ) ÷ (uᴬ + uᴮ)

uᴬ◇ᴮ = 2uᴬuᴮ ÷ (uᴬ + uᴮ)

base rate 取均值。式(9)把该二元操作递归扩展到 V 个视图。命题1指出该意见聚合等价于证据平均 eᴬ◇ᴮ = (eᴬ + eᴮ) ÷ 2，因此实现是简单 average pooling。命题2说明，如果新增意见的 u 小于原意见，聚合 u 下降；反之聚合 u 上升（PDF第5页）。

这条规则并不依据“意见标签是否冲突”来改变融合权重，而只对证据做等权平均；“冲突”主要由最终 u 和另一个训练正则表达。两份高证据、低 u 但类别相反的意见平均后，会使多个类别都有高证据；u = K ÷ S 可能仍然较低。因此作者所谓可靠冲突响应不能仅由式(7)-(8)推出，必须结合概率分散、冲突度和实验判断。

### 6.4 冲突度

定义2（式(10)-(12)，PDF第4-5页）令 c(ωᴬ,ωᴮ) = cₚc꜀。其中 cₚ 是 projected probabilities 的总变差/L1距离（PDF文本抽取丢失了绝对值符号，原式需在正式引用前再次视觉核验）；c꜀ = (1 − uᴬ)(1 − uᴮ) 是 conjunctive certainty。至少一方完全无知时 c꜀ = 0，即使点概率不同也不判高冲突；双方都确定且概率分布完全不同时 c 接近 1。该量明确试图区分“共同/单方无知”和“高置信分歧”。

### 6.5 损失与训练

式(13)是 Dirichlet 下期望交叉熵 ∑ⱼ yⱼ[ψ(S) − ψ(αⱼ)]。式(14)把真类浓度替换为 1 后，对均匀 Dirichlet 加 KL，惩罚误类证据。式(15)以 λₜ = min(1,t ÷ T) 退火组合两项，避免早期误分类样本过快退化为均匀分布。式(16)对所有有序视图对的 c 求平均，得到 consistency loss。式(17)的总损失为联合意见 accuracy loss，加 β 乘各视图 accuracy loss，再加 γL꜀ₒₙ。网络只用正常对齐训练实例，因此 L꜀ₒₙ 学习视图一致性；它没有见过人工冲突训练样本（PDF第5页）。

### 6.6 推理和可靠性

推理时各视图证据经 average pooling，联合 alpha 给 projected probability 和 u；argmax 给闭集类别，`1-u` 为可靠性。原文没有拒识阈值、coverage、abstention 或 unknown 输出。图4可视化 c，图5比较正常/冲突样本 u 分布；这只是连续可靠性评分。

## 7. 实验设置缩译

特征融合基线为 DCCAE、CPM-Nets、DUA-Nets；决策融合基线为 TMC 和 TMDL-OA。作者把主表分为正常测试集和人工冲突测试集。所有方法运行10次。正文没有给网络层数、优化器、学习率、batch、epoch、T 或 train/test 比例。官方仓库独立 Technical Appendix 补充说明：预提取向量由带 ReLU 的全连接网络提取 view-specific evidence；所有数据预先归一化；β=1、γ=1；在一张 NVIDIA GeForce GTX 3070 上运行，并给出训练/测试算法1。附录文本写“PyTorch 3.10”，该版本表述疑似把 Python 与 PyTorch 版本混淆，仍需以环境文件核对。

## 8. 实验结果全文缩译

### 8.1 正常测试集主结果

表2（PDF第7页）中 ECML 在六个数据集均最高：HandWritten `99.40±0.00%`；CUB `98.50±2.75%`，比 TMDL-OA `95.43±0.20%` 高3.07个百分点；HMDB `90.84±1.86%`，比 TMDL-OA `88.20±0.58%` 高2.64个百分点；Scene15 `76.19±0.12%`；Caltech101 `95.36±0.38%`；PIE `94.71±0.02%`。表中 Delta% 使用相对提升而非百分点，例如 HMDB 标2.99%。作者把收益归因于 consistency loss，但本地正文未给对应消融表。

### 8.2 冲突测试集主结果

表3（PDF第7页）中所有方法准确率下降，但 ECML 仍最高。代表性数字：HandWritten `94.40±0.05%`，最强基线 TMDL-OA `93.05±0.05%`；HMDB `70.84±1.19%`，TMDL-OA `67.62±0.28%`；Scene15 `56.97±0.52%`，TMDL-OA `48.42±1.02%`，高8.55个百分点；PIE `84.00±0.14%`，TMDL-OA `68.16±0.34%`，高15.84个百分点。由于冲突比例和强度未与表3绑定，这些数字不能独立复现，也不能与语义 unknown 比较。

### 8.3 冲突度、uncertainty 与消融

图4在 HandWritten 六视图上，把第一视图内容替换为错配内容；正常实例位于图左、冲突实例位于右，作者称 c 能区分二者。图5在 CUB 的50%测试实例加不同 σ 噪声：σ = 0.1 时正常与冲突 u 分布接近，噪声增强到 1、5、10 后冲突实例 u 上升。原文没有为冲突检测报告 AUROC、FPR95、阈值或数值表。

官方附录图1在 Scene15 扫描 γ∈{0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.5,2.0}。γ=0 表示只用平均证据融合、不使用跨视图 consistency loss，accuracy 约 73.02%；γ=1 最好，为 76.19%。低 γ 有轻微负效应，γ>1 后性能下降。该单数据集扫描支持一致性项在适当权重下有增益，但不是六数据集完整消融。

附录表1还增加 MCDO、Deep Ensemble、UA+ 和单视图 EDL 四个 uncertainty-aware baselines。因这些方法原本是单视图，作者把所有视图原始特征直接拼接后输入。ECML 在六数据集均最高；例如 HMDB 为 90.84±1.86%，第二名 UA+ 为 58.90±1.18%；Scene15 为 76.19±0.12%，第二名 MCDO 为 52.93±1.34%。这些大差距同时受到多视图架构与输入适配方式影响，不能纯归因于 conflict modeling。

仍缺“保持相同 per-view encoder、仅移除 L꜀ₒₙ”“TMC 规则加 L꜀ₒₙ”“显式 discount”“oracle 删除坏视图”等关键反事实，因此方法机制证据已补强但不完整。

## 9. 讨论、局限与未来工作缩译

作者用色盲观察者例子解释：当两个视图都可能可靠但意见冲突时，不能像既有规则那样因为增加视图就自动降低 uncertainty；应让冲突或低质量视图增加 uncertainty（PDF第5-6页）。原文没有独立局限或 future work 节，没有讨论人工冲突是否代表真实多模态错配、等权证据平均是否会被高证据错误视图支配、类别不平衡、校准或 `beta/gamma` 敏感性。

## 10. 结论缩译

论文总结 ECML 为 RCML 提供视图意见和可靠性，通过 average pooling 实现冲突意见聚合，并用冲突度一致性正则训练。作者称理论说明聚合可表达共同与视图特有可靠性，六数据集验证有效（PDF第7页）。结论没有涉及开放集、OOD类别拒识或网络安全。

## 11. 附录和补充材料中的关键内容

正文引用的 Technical Appendix 已从作者官方仓库 `https://github.com/jiajunsi/RCML` 核验，仓库 HEAD 为 `c9c5ab41e6fe62a85e5f6441a4dc7b568e1fa421`。附录包含命题1/2证明、Dirichlet KL 推导、算法1、实现设置、γ 敏感性以及 uncertainty-aware baseline 表。

算法1确认：训练时每视图产生 evidence/opinion，平均融合后计算总损失并梯度更新；测试时返回 projected probability p=α÷S 与 uncertainty u。命题证明确认平均 belief fusion 等价于 evidence arithmetic mean，并给出新增意见 uncertainty 高低决定聚合 uncertainty 升降的条件。

# 第二部分：独立技术分析

## A. 文献身份

- 记录号：`CAEOS-L3-010`
- 作者：Cai Xu、Jiajun Si、Ziyu Guan、Wei Zhao、Yue Wu、Xiyue Gao
- 年份/来源：AAAI 2024 版式；本地 arXiv:2402.16897v2，2024-02-28
- DOI/URL：`10.48550/arXiv.2402.16897`
- 本地 PDF：[2402.16897.pdf](F:/泉城实验室/二期/论文/异常检测/paper/2402.16897.pdf)
- 全文抽取：[010_Reliable_Conflictive_Multi_View_Learning.txt](F:/泉城实验室/二期/论文/异常检测/方向分析/多模态开放集加密恶意流量检测/证据冲突感知的可信开放集加密恶意流量检测方法/07_论文精读/04_120篇全文抽取/010_Reliable_Conflictive_Multi_View_Learning.txt)
- Zotero Item/Citation Key：`pending/pending`
- 精读层级：L3 内容完成；未运行代码
- 证据角色：B-方法支柱
- 当前状态：`project_mapped`，不是 `complete`

## B. 一句话结论

- 真正解决：闭集多视图中，对人工噪声/错配视图实例输出类别与可靠性。
- 对 CAEOS 价值：ECML 提供 `概率分歧 × 双方确定性` 的显式冲突量，是必须实现的冲突基线。
- 最大风险：融合本身等价证据平均，未显式按冲突折扣；附录只有单数据集 γ 扫描，主表冲突比例、强度与 split 仍不完整。

## C. 研究问题与威胁模型

- 对象：通用多视图分类实例。
- 训练可见：只有正常、严格对齐的闭集样本。
- 测试变化：随机视图高斯噪声或标签错配。
- 攻击者：未定义，污染不是自适应攻击。
- 输出：闭集类别、u、成对冲突度 c。
- 部署位置/决策时点：全文未定位。

## D. 任务定义

- 监督范式：监督式 evidential multi-view classification。
- 类空间：闭集；conflictive sample detection/uncertainty，不是 OOD 类别。
- 输出：单标签、belief、u、pairwise c。
- 泛化：同数据集人工污染。
- 操作性定义：作者对“conflictive”定义明确，但其 noise/unaligned 构造不等于 unknown attack。

## E. 数据集逐项审计

六数据集规模见缩译第5节。Caltech101 正文“取前10类”与表1 K = 101 冲突；train/test、冲突比例、σ 和标准化缺失。全部数据非流量，数值对 CAEOS 为 C0；方法结构可为 C1/C2。

## F. Known/Unknown 与协议审计

- known：全部训练类别。
- unknown：不适用；冲突视图仍来自已知类别或噪声。
- 阈值：没有 unknown 拒识阈值。
- 协议等级：`P1-closed-set-clean-train-synthetic-conflict-test/P3-split-conflict-ratio-and-strength-unclear`。
- 迁移要求：CAEOS 需在 target unknown 完全隔离时单独校准风险阈值。

## G. 输入、特征与多模态判定

每个既有特征向量由独立 DNN 编码。CUB 图文属于真多源；HandWritten/PIE/Scene15 等是同对象不同描述符；没有缺失模态。错配是一视图换成另一类实例，噪声是高斯扰动。CAEOS 应复用其错配实验但不能把同一 PCAP 派生视图称为真多源。

## H. 预处理流水线

1. 读取公开多视图向量。
2. 正常对齐样本训练各视图 EDL 和联合头。
3. 测试时对部分实例随机视图加噪或换成另一类内容。
4. 运行10次报 mean±std。
- 拟合范围、归一化、split和随机性控制：全文未定位。

## I. 模型与信息流

xᵥ → fᵥ → eᵥ → αᵥ → (bᵥ,uᵥ,pᵥ) → average evidence → joint opinion → class/u；训练再对所有视图对计算 c = cₚc꜀ 并最小化。冲突量参与训练正则，不直接作为可学习折扣权重，也不直接决定 unknown 风险。

## J. 关键公式与优化目标

- 式(5)：EDL 映射。
- 式(7)-(9)：平均证据聚合。
- 式(10)-(12)：概率距离乘共同 certainty 的冲突度。
- 式(15)：退火 EDL accuracy loss。
- 式(16)：视图对冲突一致性损失。
- 式(17)：Lⱼₒᵢₙₜ + β∑ᵥ Lᵥᵢₑwᵛ + γL꜀ₒₙ。
- 潜在退化：一致性正则可能迫使互补视图过度一致；高置信相反证据平均后总证据仍高，u 未必上升；平均规则对坏视图无样本级剔除。

## K. 证据、不确定性、冲突和融合

- u：vacuity，不是完整 epistemic/aleatoric 分解。
- c：对称、理论上0到1；把分歧和确定性相乘，可区分无知与高置信分歧。
- discount：无。
- fusion：等权平均 evidence；不使用 c 对每视图折扣。
- 与 TMC：TMC用DS且常使u下降；ECML用平均证据并允许加入高u视图后联合u上升。
- 与 DBF：DBF根据跨模态冲突估 reliability 并折扣 belief；ECML没有该层。
- 与 CAEOS：必须证明新增的 conflict->discount->risk 链条不只是 ECML c 加一个权重。

## L. 训练与复现条件

- 10 runs；附录给出 β=γ=1、预归一化、全连接 ReLU evidence network 和 GTX 3070。
- 官方代码仓库已核验到 HEAD `c9c5ab41`；尚未运行代码，网络层数、split 与随机种子仍需配置/数据脚本核验。
- Technical Appendix 已补核；其“PyTorch 3.10”版本表述需环境证据澄清。
- 复现状态：未运行。

## M. 基线与公平性

| 基线 | 类型 | 输入 | conflict协议 | 可比性 |
|---|---|---|---|---|
| DCCAE/CPM-Nets/DUA-Nets | 特征融合 | 多视图向量 | 同人工污染，细节缺 | C2 |
| TMC/TMDL-OA | 证据决策融合 | 多视图向量 | 同人工污染，阈值无 | C2 |
| MCDO/DE/UA+/EDL | 不确定性单视图方法适配 | 拼接全部原始视图 | normal test；无同结构冲突消融 | C1 |

附录 γ=0 提供简单平均证据且无 consistency loss 的单数据集对照。仍缺 DBF、同结构六数据集无 L꜀ₒₙ、按 oracle 坏视图删除、missing-view 和 calibration 基线；网络容量/调参预算未给。

## N. 指标定义

只报告 normal/conflictive test accuracy；图4/5为 c/u 可视化。没有冲突检测 AUROC、风险-覆盖、ECE、Brier、NLL、FPR95 或拒识指标。

## O. 定量结果

| ID | 数据集/场景 | split/seed | 方法 | 指标 | 数值 | 最强基线/差值 | 页/表/图 | 证据类型 | 可比性 |
|---|---|---|---|---|---|---|---|---|---|
| ECML-R1 | HMDB normal | split未定位/10 runs | ECML | Accuracy | 90.84±1.86% | TMDL-OA 88.20±0.58%，+2.64pp | PDF7/表2 | 论文自报 | C2 |
| ECML-R2 | Scene15 conflictive | 协议缺/10 runs | ECML | Accuracy | 56.97±0.52% | TMDL-OA 48.42±1.02%，+8.55pp | PDF7/表3 | 论文自报 | C1 |
| ECML-R3 | PIE conflictive | 协议缺/10 runs | ECML | Accuracy | 84.00±0.14% | TMDL-OA 68.16±0.34%，+15.84pp | PDF7/表3 | 论文自报 | C1 |

## P. 95%/5% 验收映射

论文不能核对任何 CAEOS 正式门：没有 known恶意层级、benign FAR、unknown FPR95、OSCR或校准。Caltech normal accuracy超过95%也与安全门无关。

## Q. 消融、敏感性与鲁棒性

- 已有：normal vs 人工 conflictive；sigma 密度图；错配冲突度图；Scene15 的 γ 扫描；γ=0 无 consistency 对照。
- 未提供：β 扫描、六数据集同结构消融、融合规则反事实、缺失模态、对抗冲突、跨域。
- γ 扫描支持一致性项在 Scene15 的局部贡献，但仍无法把六数据集全部收益归因到冲突度或平均聚合。

## R. 统计证据

10次运行、mean±std；seed、CI、检验、效应量、多重校正均未定位。主表差异与方差量级相近时不能宣称稳定优势。

## S. 局限与有效性

- 作者没有明确 limitations 节。
- 内部有效性：split/冲突比例与强度缺失，消融只覆盖单数据集；Caltech类数矛盾。
- 构念有效性：人工高斯/错配不覆盖真实跨模态冲突。
- 外部有效性：非流量数据、无异步/缺失/同源重复视图。
- CAEOS 风险：直接平均 evidence 会让高证据错误模态继续主导，且 L꜀ₒₙ 可能压平真实互补差异。

## T. CAEOS-EMTD 采纳/否决表

| 对象 | 结论 | 理由 | 所需实验 |
|---|---|---|---|
| 任务定义 | 否决 | 不是OSR/流量 | strict-v4重建 |
| 冲突定义 | 进入基线 | 明确区分分歧与无知 | 实现c并测单调性 |
| 证据生成 | 进入基线 | 标准EDL | 同encoder公平对照 |
| 折扣 | 否决 | 原文没有 | c驱动discount消融 |
| 融合 | 进入基线 | 平均evidence简单直接 | vs TMC/DBF/CAEOS |
| unknown风险 | 否决 | 无unknown与阈值 | P0风险头 |
| 指标 | 否决主表 | 只有accuracy | 三层+校准 |

## U. 新增实验动作

| ID | 类型 | 自变量/对照 | 固定条件 | 数据/场景/seeds | 主指标 | 判据 |
|---|---|---|---|---|---|---|
| E-ECML-01 | E-BASELINE | ECML c+平均证据 vs TMC/DBF/CAEOS | encoder/split一致 | strict-v4，5 seeds | OSCR/FPR95/ECE | CAEOS跨场景稳定优于ECML |
| E-ECML-02 | E-ABLATION | 无 L꜀ₒₙ、c不乘certainty、无联合loss | 其余固定 | 3数据集×5 seeds | 三层指标 | 识别真实贡献 |
| E-ECML-03 | E-ROBUST | 高斯、错位、缺失、同源复制、对抗高证据 | 训练不变 | 污染强度曲线 | worst OSCR | 冲突与风险单调 |
| E-ECML-04 | E-NEGATIVE | 互补视图被 L꜀ₒₙ 强迫一致 | γ扫描 | 细粒度场景 | Known F1/冲突校准 | 排除过度一致退化 |

## V. 可引用主张与证据

Citation Key pending，当前不得进入正文。核验后可引用其操作性定义：“冲突度由 projected probability 距离与 conjunctive certainty 相乘”（式(10)-(12)，PDF第4-5页），并注明该文任务是通用闭集多视图。

## W. 不能引用或尚未证明的内容

- 不能写 ECML 已解决未知攻击检测。
- 不能把 u 上升性质说成对高置信类别冲突的充分保证。
- 不能声称 L꜀ₒₙ 已被消融验证；本地全文未见表。
- 不能用表3数字与任何流量或 OSR 结果横比。

## X. 最终审计

- [x] G0 全文缩译门
- [x] G1 全文门
- [ ] G2 身份门（正式元数据/Zotero待核）
- [x] G3 任务门
- [x] G4 协议门（`P1-closed-set-clean-train-synthetic-conflict-test/P3-split-conflict-ratio-and-strength-unclear`）
- [x] G5 方法门
- [x] G6 结果门
- [x] G7 对比门（主文基线、附录不确定性基线与 γ=0 对照已核验；缺项已限定）
- [x] G8 局限门
- [x] G9 项目门
- [ ] G10 引用门
- 最终状态：`project_mapped`；L3内容完成，`complete=否`。
