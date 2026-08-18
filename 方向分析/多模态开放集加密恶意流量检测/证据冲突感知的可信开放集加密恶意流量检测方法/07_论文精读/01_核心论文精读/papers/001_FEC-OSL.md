# 001 面向细粒度加密流量分类的端到端开放集半监督学习 / End-to-End Open-Set Semi-Supervised Learning for Fine-Grained Encrypted Traffic Classification

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | PDF页 | 本文缩译标题 | 图/表/公式 | 覆盖状态 | 省略内容及理由 |
|---|---:|---|---|---|---|
| Abstract、Introduction | 1-2 | 摘要与引言 | 图1 | 已覆盖 | 压缩加密比例等行业背景 |
| Related Work | 2-3 | 相关工作 | 无 | 已覆盖 | 按监督/半监督/OSR合并 |
| Method III-A/B | 3-4 | 问题定义与总览 | 图2 | 已覆盖 | 无 |
| Method III-C | 4-5 | 双分支流特征 | 式(1)-(7) | 已覆盖 | 常规Transformer层不逐参数展开 |
| Method III-D | 5-6 | 能量已知/未知分类 | 图3；式(8)-(13) | 已覆盖 | 无 |
| Method III-E/F | 6-7 | 未知聚类与联合训练 | 式(14)-(17) | 已覆盖 | 无 |
| Evaluation IV-A-D | 7-10 | 数据、设置、主结果 | 表1；图4-7 | 已覆盖 | 图4-6无法可靠恢复的曲线点不抄录 |
| Evaluation IV-D/E | 10-11 | 解释与概念漂移 | 图8-10；表2 | 已覆盖 | 表2图像表格数字未从文本可靠恢复 |
| Evaluation IV-F/G | 12-14 | 消融与敏感性 | 表3-4；图11-13 | 已覆盖 | 以正文明确数字为准 |
| Discussion、Conclusion | 14 | 讨论、局限、结论 | 无 | 已覆盖 | 无 |
| Appendix | 无 | 附录 | 不适用 | 不适用 | 本地PDF未含附录 |

## 1. 标题、摘要与关键词

### 1.1 标题

中文题名为“面向细粒度加密流量分类的端到端开放集半监督学习”，方法简称 FEC-OSL。

### 1.2 摘要缩译

现实网络不断出现训练期未定义的新流量类，闭集分类器会把它们静默分到已知类。已有开放世界方法常分阶段训练，未知检测或新类估计不够可靠。论文提出端到端 FEC-OSL，含三个相互促进的模块：双分支流特征提取同时捕获细粒度字节和交互特征；基于能量边界学习区分已知/未知；自适应深度聚类把未知流进一步细分。三个模块以联合损失训练，作者在三个真实数据集上评估已知分类、未知区分和未知聚类（PDF第1页）。

### 1.3 关键词

加密流量分类、开放集半监督学习、端到端、能量模型、网络安全（PDF第1页）。

## 2. 引言缩译

加密保护隐私，也使载荷明文检测失效，恶意软件借 TLS/SSL 隐蔽通信。现实开放世界要求同时完成两件事：正确细分已知流量，并拒绝训练未见类；若希望系统持续演化，还需估计/聚类未知类。作者认为现有 OSR 常只用单一统计视角、softmax置信或重建误差，特征可分性不足、未知边界不稳；未知发现又依赖离线聚类和人工调参。FEC-OSL 试图把双视图表征、能量边界和未知聚类端到端联合起来（PDF第1-2页）。

作者列出三项贡献：提出同时完成已知/未知区分、已知分类和未知聚类的端到端框架；设计字节矩阵 CViT 与流交互 TAGCN 双分支，并以能量约束形成边界、以深聚类迭代伪标签；在三个数据集、不同开放程度、概念漂移、消融和敏感性实验中验证（PDF第2页）。

## 3. 相关工作缩译

加密流量分类被分为监督、无监督和半监督。监督方法用 CNN/Transformer/GNN 从字节或流图学特征；无监督方法学习正常模式并以重建偏离检异常；半监督降低标注依赖。作者认为这些工作大多仍是闭集。OSR方法则包括 softmax置信、重建误差和生成分布：置信法可能对未知高置信，重建阈值敏感，生成法分阶段且误差传播。论文强调自己的能量全局分数和端到端未知聚类（PDF第2-3页）。

## 4. 预备知识、问题定义与威胁模型缩译

训练集 Dᵗʳᵃⁱⁿ 由有标签已知集 Dᵏ 与无标签辅助未知集 Dᵃᵘ 组成。已知标签 Yᵏ = {B} ∪ {Aᵢ}，含良性 B 和 Cᵏ − 1 个已知攻击；辅助未知潜在标签 Yᵃᵘ 与 Yᵏ 不交。测试集定义为已知类、辅助未知类和全新 Dⁿᵘ/Yⁿᵘ，后者同时与已知和辅助未知不交。目标是：分类 Yᵏ；识别全新 Yⁿᵘ；用伪标签细分 Dᵃᵘ；后续把可信新未知并入 Dᵃᵘ 并周期重训（PDF第3、7页）。

这不是目标 unknown 完全不可见的OSR。每个实验把 unknown 类的一半作为无标签 auxiliary unknown 参与训练，另一半才作 novel unknown 测试（PDF第9页）。因此作者的 operational protocol 至少是 `P1-auxiliary-unknown`；在线累积并重训还属于 open-world adaptation。论文未定义攻击者可操纵包长、字节、方向或图结构的能力，也未给捕获点和决策时延。

## 5. 数据与预处理缩译

三数据集是 USTC-TFC-2016（10类恶意软件+10类良性应用）、CIC-IDS-2018（正常+6类攻击）、ISCX-Tor-2016（16类Tor应用，实验选8类；PDF第7、9页的比例总数为8）。后两者并非都在做“未知恶意攻击”：Tor数据是应用类别；USTC的unknown随机类可能是良性应用或恶意家族。论文没有说明是否强制良性始终为known，也没有逐场景列known/auxiliary/novel的具体类名。

原始PCAP用 SplitCap 划成双向流；去以太网头，匿名化IP和端口。每流取前5个连续包，分别把header和payload零填充为固定矩阵；header最终20×20、payload 40×40。每包又作图节点，节点特征有方向、长度、时间戳、burst包数/字节数、相邻burst包数比/字节比；按同burst相邻包和相邻burst首/尾包建立无向边，最多30节点（PDF第4-5、8页）。类别不平衡用 class-balanced sampling，但总流数、各类流数、去重、流超时、burst阈值、train/validation/test比例和采集会话隔离全文未定位。

开放程度：USTC known:unknown 为 16:4、12:8、8:12、4:16；CICIDS 为 5:2、4:3、3:4、2:5；Tor 为 6:2、4:4、2:6。每个 Nu 中向下取整的一半类为 auxiliary unknown 训练，另一半为 novel unknown 测试（PDF第9页）。类如何随机选择、场景是否多次重采样、种子未定位。

## 6. 方法全文缩译

### 6.1 总体架构

图2（PDF第4页）的信息流为：PCAP → 双向流 → 字节矩阵 CViT 与包交互图 TAGCN → 拼接 h → Cᵏ + 1 类能量分类与阈值 → known 类别或 unknown → unknown 深聚类。共享特征提取器由分类/能量损失和聚类损失交替更新。

### 6.2 字节分支

header和payload各自按不跨包的 P × P patch切分。式(1)先在每patch卷积，式(2)线性嵌入加位置编码，式(3)-(4)为预归一化 MHA/FFN 残差。全局池化得到 zʰ、zᵖ，拼接为 hᵇ（PDF第4-5页）。header/payload是同一流内的同源多视图，不是真多源模态；两者共享“相同feature extraction process”，是否共享参数全文未明确。

### 6.3 交互图分支

每流每包为节点，按burst构图。TAGCN图滤波器是邻接矩阵多项式 G = ∑ₖ wₖAᵏ（式(5)），式(6)聚合不同节点特征维度和 k 跳邻域，式(7)readout得到图级 hᵍ。最终 h = [hᵇ, hᵍ]（PDF第5页）。该分支仍由同一PCAP派生，属于同源多视图；拼接本身不包含可靠性、冲突或缺失视图机制。

### 6.4 能量分类器

式(8)把类条件能量边缘化为 Helmholtz free energy。分类器输出 Cᵏ + 1 个 logits，最后一类把所有 auxiliary unknown 合并；E(h, y) = −gʸ(h)，式(9)是 Gibbs/softmax 概率，式(10)为 E(h; g) = −T log ∑ⱼ exp(gⱼ ÷ T)（PDF第6页）。这说明训练期已经有一个显式辅助unknown类，不是仅用known学习边界。

式(11)是已知/辅助未知交叉熵加 λLᵉⁿᵉʳᵍʸ。式(12)对 known 要求 E(h) ≤ mᵏ，对 auxiliary unknown 要求 E(h) ≥ mᵃᵘ，用平方 hinge 形成间隔。推理把 known 样本的负能量 −E 拟合 Weibull；若 −E ≥ τ，则在 Yᵏ 内取最小能量类，否则输出 U（式(13)，PDF第6页）。注意训练分类头含 Cᵏ + 1 类，但推理 known 决策限定 Yᵏ，unknown 由独立 τ 决定。

### 6.5 未知自适应聚类

unknown特征先经一个 CNN ψθ 细化，分类器 g′ 的初始类数设为“大于潜在真实unknown类数”的值；初始聚类给伪标签，样本库保存特征/标签，中心库保存簇中心。式(14)用伪标签交叉熵训练；式(15)以 β 动量更新样本特征；式(16)按最近中心重分配伪标签（PDF第6-7页）。初始聚类算法、初始簇上限、如何删并空簇、β 和停止准则全文未定位，且“设为大于真实unknown类数”隐含需要上界先验。

测试时，作者把 known Weibull 尾部 p < 0.01、特征距离位于 top 5% 且形成高密度簇的 novel unknown 视为可信，加入 Dᵃᵘ 并周期重训（PDF第7页）。评估是否实际启用这一在线重训、何时更新、是否会让test影响后续test结果全文未定位。

### 6.6 联合训练

式(17)为 Lᵗᵒᵗᵃˡ = L₁ + L₂，分类/能量模块与聚类模块交替优化，共享双分支特征。作者解释 known 被压到低能量紧簇，auxiliary unknown 被推到高能量并由聚类收紧，从而让 novel unknown 落在类似辅助未知区域（PDF第7、10页）。两个损失没有额外总权重；但 L₁ 内部 λ = 0.1。

## 7. 实验设置缩译

闭集基线包括 GraphDApp、DeepPacket、PERT、ET-BERT、Kitsune、FlowPrint；开放集基线为 CVAE-EVT、ECNet、Trident(AE/RNN/GNN)。指标：known分类AC/PR/RC/F1，known-vs-unknown ROC AUC，unknown聚类AMI（PDF第7-8页）。论文没有FPR95、AUPR-Out、OSCR、OpenAUC、ECE/Brier/NLL。

实现为 Python3.8.19、PyTorch1.8.1、RTX3090、SGD；双分支/分类学习率 10⁻⁴，聚类学习率 10⁻³，训练 50 epochs，batch size 为 64；T = 10，λ = 0.1，mᵏ = −10，mᵃᵘ = −5。τ 用 known 负能量 Weibull 分位数：USTC/CICIDS 取 0.05，Tor 取 0.1（PDF第8页）。没有验证集、seed数、SGD动量、weight decay、Weibull shape/tail-size或基线代码/调参预算。

T 在 {0.01, 0.1, 1, 10, 100} 中以 known/unknown AUC 选最优；mᵏ/mᵃᵘ 按训练 known/auxiliary 能量均值构造候选，再以 AUC 选 −10/−5；τ 分位数也通过 AUC/F1 敏感性选择（PDF第13-14页）。全文没有说明这些 AUC 来自独立 validation 还是最终 test novel unknown，因此不能按 P0 或纯 P1 解释；按最严格审计，主结果存在 `P3-test-tuned` 风险。

## 8. 实验结果全文缩译

### 8.1 闭集与开放集主结果

表1是图像化表格，当前文本未可靠恢复逐格数值。正文称FEC-OSL相对最强监督方法在三个数据集的AC分别提高1.56、0.43、1.4个百分点，F1提高1.16、0.42、1.1个百分点；CICIDS上Trident-RNN accuracy最高但F1低于FEC-OSL（PDF第8页）。在没有逐格视觉复核前，不把这些相对值转换为绝对SOTA结论。

图4-6比较不同开放程度的AUC、known F1、unknown AMI。作者称低开放度AUC接近1，开放度增大时FEC-OSL下降更慢；USTC 取 4:16 时，CVAE-EVT/Trident AUC约降到80%，FEC-OSL仍较高。图中精确点值未从全文文本可靠恢复，故写“全文未定位精确数值”（PDF第9-10页）。

### 8.2 特征解释与概念漂移

USTC 取 12:8 时，t-SNE显示训练后known紧簇、auxiliary unknown分离，测试novel unknown多落在辅助unknown区域（图7，PDF第10页）。Weibo/Zeus attention rollout关注header不同字段；SHAP显示Weibo更依赖方向-长度和burst字节，Zeus更依赖时间戳与方向-长度（图8-9，PDF第11页）。这些是定性解释，不能证明因果贡献。

CIC-IDS-2018-new把不同日期良性和不同工具的相似攻击分开，如训练DDoS来自LOIC-HTTP、测试来自LOIC-UDP。概念漂移下F1接近90%，AC/PR/RC均超过90%（图10，PDF第11页）；精确值和多次运行统计未定位。

### 8.3 消融

USTC闭集表3/正文：完整模型最佳；去字节分支F1降1.80个百分点，去header降2.61，去payload降1.52，去交互分支降2.29（PDF第12页）。USTC开放集取 16:4 的表4中，完整 known/unknown AUC为 99.13%；去字节分支降至 86.42%，去交互分支降至 80.35%；换softmax后 AUC为 89.65%。图11显示softmax known/unknown置信分布重叠，而能量分布分离。该消融同时改变特征容量/输入信息，没有等参数替代分支。

### 8.4 敏感性

header 为 20 × 20 时 F1 为 99.59%；payload 取 40 × 40 最好；图节点数 30 最好。τ 分位数从 0.1 到 0.5“稳定接近最优”，但实现细节却为 USTC/CICIDS 取 0.05，正文建议 0.1，存在表述不一致（PDF第8、13页）。T = 10 时 AUC 最好。mᵏ 候选为 {−8, −10, −12, −14, −16}，mᵃᵘ 候选为 {−7, −6, −5, −4, −3}，要求 mᵃᵘ > mᵏ；间隔 5 到 7 通常有较高 AUC，(−10, −5) 最好（图12-13，PDF第13-14页）。

### 8.5 缺失结果

没有不同具体unknown类组合/难度的逐场景表；没有多seed均值标准差、显著性、FPR95、benign FAR、OSCR、校准、推理吞吐/显存；没有“无auxiliary unknown”严格对照；没有验证在线累计重训是否造成测试顺序依赖。

## 9. 讨论、局限与未来工作缩译

作者认为固定尺寸使单流计算稳定、总体成本随流数线性，概念漂移实验支持鲁棒性。明确局限是只取前30包，可能漏掉后期攻击行为；双分支和聚类增加开销，限制低延迟/资源受限部署。未来研究可变长度/上下文感知流建模、轻量化，以及测试时训练/适配以应对新攻击（PDF第14页）。论文没有讨论auxiliary unknown依赖、超参AUC选择泄漏、随机类留出语义或未知中良性/恶意混杂。

## 10. 结论缩译

FEC-OSL以字节+交互双分支、能量边界和深度聚类同时处理known分类、unknown识别和unknown细分。作者称三个基准验证优势，并计划测试时适配（PDF第14页）。结论应限定为论文自身auxiliary-unknown协议，不能扩大为unknown-free开放集证据。

## 11. 附录和补充材料中的关键内容

本地PDF无附录或补充配置。类清单、split文件、种子、代码地址和详细超参未在正文定位。

# 第二部分：独立技术分析

## A. 文献身份

- 记录号：`CAEOS-L3-001`
- 作者：Qian Yang、Wenxuan He、Minghao Chen、Hongyu Du、Sisi Shao、Fei Wu、Shangdong Liu、Yimu Ji、Kui Ren
- 年份/来源：IEEE TIFS, Vol.21, 2026, pp.1347起；正式页码终点待Zotero核验
- DOI：`10.1109/TIFS.2026.3653575`
- 本地 PDF：[10.1109_TIFS.2026.3653575.pdf](F:/泉城实验室/二期/论文/异常检测/paper/10.1109_TIFS.2026.3653575.pdf)
- 全文抽取：[001_End_to_End_Open_Set_Semi_Supervised_Learning_for_Fine_Grained_Encrypted_.txt](F:/泉城实验室/二期/论文/异常检测/方向分析/多模态开放集加密恶意流量检测/证据冲突感知的可信开放集加密恶意流量检测方法/07_论文精读/04_120篇全文抽取/001_End_to_End_Open_Set_Semi_Supervised_Learning_for_Fine_Grained_Encrypted_.txt)
- Zotero Item/Citation Key：`pending/pending`
- 精读层级：L3内容完成；未运行代码
- 证据角色：A-直接核心
- 当前状态：`project_mapped`，G10未过

## B. 一句话结论

- 真正解决：用有标签known加无标签auxiliary unknown训练，区分novel unknown并聚类未知流。
- 对CAEOS价值：是能量风险、同源双视图和auxiliary-unknown协议的必做强基线。
- 最大风险：并非P0；target-like辅助未知显式进训练，且T/margin/tau以AUC选优而未说明独立validation，可能test-tuned。

## C. 研究问题与威胁模型

- 对象：双向加密流；样本决策在前5包/最多30节点后。
- 训练可见：known标签、auxiliary unknown无标签及其类集合。
- 测试未知：另一半留出类；在线阶段还会并入训练。
- 攻击者能力/捕获点：全文未定位。
- 输出：known细类、unknown、unknown簇。
- 成功标准：AC/PR/RC/F1、AUC、AMI，不含安全FPR门。

## D. 任务定义

- 监督范式：开放集半监督、伪标签聚类、可选在线适配。
- 类空间：P1开放集+开放世界发现；不是P0 OSR。
- 安全任务：数据集混合应用分类、恶意家族分类、入侵类别；不一致。
- 输出：单标签known/U、能量、unknown簇。
- 泛化：同数据集随机类留出、一个跨日期/工具drift场景。

## E. 数据集逐项审计

三数据集和比例见缩译第5节。样本量/split/去重/会话隔离未定位；unknown类名未列；良性是否始终known不明。USTC/Tor可能把良性应用当unknown，不能等同unknown attack。CICIDS-new是作者重组但表2数字未从文本恢复。

## F. Known/Unknown 与协议审计

- unknown构造：类级留出，Nu一半aux train、一半novel test。
- 预训练/归一化：是否见novel unknown未定位。
- 模型训练：明确见auxiliary unknown。
- 超参/阈值：T、margin、quantile以AUC敏感性选，验证来源未说明。
- test选择：有直接风险；未给独立val。
- 协议等级：方法本质`P1-auxiliary-unknown`；所报最优配置按证据保守标 `P3-test-tuned-risk`，不能放CAEOS P0主表。

## G. 输入、特征与多模态判定

- 视图1：header/payload字节矩阵，CViT。
- 视图2：包/burst交互图，TAGCN。
- 模态分类：同一PCAP派生的同源多视图；header/payload又是单视图内部两部分。
- 融合：特征拼接，无证据、不确定性、冲突或缺失模态处理。
- 可得性：payload加密但原始密文字节可得；匿名化IP/端口。

## H. 预处理流水线

PCAP → SplitCap 双向流 → 去以太网头/IP端口匿名 → 前5包 → header/payload 零填充矩阵与 burst 图 → balanced sampler → 训练。burst阈值、超时、去重、split、归一化拟合范围缺失。

## I. 模型与信息流

CViT bytes 与 TAGCN FIG → 拼接 h → Cᵏ + 1 个 logits/free energy → Weibull τ → known/U → CNN、memory bank 和 centroid pseudo-clustering。训练 L₁/L₂ 交替，共享 encoder；在线可信 novel 回流 Dᵃᵘ。

## J. 关键公式与优化目标

- 式(8)-(10)：free energy/log-sum-exp，E越低越known，负E越大越known。
- 式(11)-(12)：known CE + auxiliary energy hinge。
- 式(13)：Weibull tau拒识。
- 式(14)-(16)：unknown伪标签CE、动量特征、最近中心更新。
- 式(17)：L1+L2。
- 退化：auxiliary类分布决定边界；Ck+1 unknown logit与独立tau可能不一致；伪标签错误自增强；在线test顺序依赖。

## K. 证据、不确定性、冲突和融合

- evidence：不使用Dirichlet证据；能量/logit是risk representation。
- uncertainty/conflict/discount：均无显式机制。
- fusion：特征拼接。
- risk：free energy+Weibull known-tail。
- 与CAEOS：FEC-OSL只对risk与representation构成竞争，不对evidence/conflict/discount构成基线。

## L. 训练与复现条件

- 环境/硬件/超参见缩译第7节。
- seeds、代码、split、class lists、cluster参数缺。
- 复现状态：未运行。

## M. 基线与公平性

| 基线 | 任务/输入 | unknown协议 | 可比性 |
|---|---|---|---|
| ET-BERT等 | 闭集/各自输入 | 无unknown | C1 |
| CVAE-EVT | OSR重建 | 未在本文重述 | C2待核 |
| ECNet | 多视图/unknown | 未在本文重述 | C2待核 |
| Trident | 一类/重建多骨干 | 未在本文重述 | C2待核 |

基线是否也获得同一auxiliary unknown、同调参预算和同预处理未说明。将闭集方法与开放集方法放同一closed-set表不能证明OSR公平性。

## N. 指标定义

Accuracy/Precision/Recall/F1用于known分类，AUC用于known-vs-unknown，AMI用于unknown聚类。正类方向、macro/micro平均、拒绝known如何计入F1、AUC是否混合aux/novel全文未定位。

## O. 定量结果

| ID | 数据集/场景 | split/seed | 方法 | 指标 | 数值 | 对照 | 页/表 | 证据类型 | 可比性 |
|---|---|---|---|---|---|---|---|---|---|
| FEC-R1 | USTC 16:4 | 类留出/seed缺 | 完整 | AUC | 99.13% | w/o BFE 86.42%；w/o FIE 80.35% | PDF12/表4 | 论文自报 | C2 |
| FEC-R2 | USTC 16:4 | 同上 | softmax头 | AUC | 89.65% | 完整99.13%，-9.48pp | PDF12/表4 | 论文自报 | C2 |
| FEC-R3 | USTC敏感性 | 协议同主实验 | header20×20 | F1 | 99.59% | 其他尺寸见图 | PDF13/图12a | 论文自报 | C1 |
| FEC-R4 | CICIDS-new drift | 日期/工具分离 | 完整 | F1 | 接近90% | AC/PR/RC>90% | PDF11/图10 | 论文自报近似 | C1 |

## P. 95%/5% 验收映射

known恶意识别与Known Macro-F1定义不清；benign FAR、FPR@95TPR、OSCR、校准均不可核。AUC 99.13%不等于FPR95<=5%，且阈值可能test-tuned。不能证明任何正式场景满足95%/5%。

## Q. 消融、敏感性与鲁棒性

已有分支、header/payload、softmax/energy、尺寸、节点、T、tau、margin和一个drift实验。缺无auxiliary unknown、固定encoder仅换risk头、同参数替代分支、unknown类组合、在线更新、模态污染、跨数据集、5seed统计。

## R. 统计证据

运行次数、seed、mean/std/CI、显著性均未定位；图/表似为单次最优配置。不能把小百分点优势视为稳定SOTA。

## S. 局限与有效性

- 作者自述：只看前30包；双分支/聚类开销；需轻量化与测试时适配（PDF14）。
- 复核：P1且可能P3；数据/类/split不透明；未知语义混杂；cluster上界先验；缺安全指标与统计。
- CAEOS风险：若用它作P0主表会给auxiliary unknown方法不公平优势；若照搬在线回流会污染独立test。

## T. CAEOS-EMTD 采纳/否决表

| 对象 | 结论 | 理由 | 所需实验 |
|---|---|---|---|
| 任务定义 | 部分采纳 | 三任务完整但aux unknown | P0/P1分表 |
| 数据协议 | 否决主协议 | 非unknown-free且调参不清 | strict-v4 |
| 模态设计 | 进入候选 | 字节+交互图同源互补 | 同encoder消融 |
| 表征 | 必做基线 | CViT+TAGCN强骨干 | 公平适配 |
| evidence/conflict/discount | 不适用 | 原文无 | 不冒名 |
| unknown risk | 必做基线 | energy+Weibull | known-only tau |
| 聚类 | 选做 | 属拒识后发现 | 二阶段隔离 |
| 指标 | 否决主表 | 缺FPR95/OSCR/校准 | 统一补算 |

## U. 新增实验动作

| ID | 类型 | 自变量/对照 | 固定条件 | 数据/场景/seeds | 主指标 | 判据 |
|---|---|---|---|---|---|---|
| E-FEC-01 | E-BASELINE | FEC-OSL P1 vs CAEOS P0/P1 | encoder/split一致 | 全场景×5 | 三层+校准 | 分协议报告 |
| E-FEC-02 | E-PROTOCOL | aux unknown比例0/25/50% | novel固定 | 3数据集×5 | FPR95/OSCR | 量化协议优势 |
| E-FEC-03 | E-BASELINE | energy+Weibull vs MSP/OpenMax/CAEOS risk | 同encoder | strict-v4×5 | OSCR/FPR95 | 阈值known-only |
| E-FEC-04 | E-ABLATION | CViT/TAGCN/concat | 风险头固定 | 3数据集×5 | KnownF1/UnknownAUROC | 隔离表征收益 |
| E-FEC-05 | E-NEGATIVE | 在线novel回流开/关/顺序 | checkpoint固定 | 时间序列 | 漂移收益/遗忘 | 不污染独立test |

## V. 可引用主张与证据

Citation Key pending，当前不得写正文。核验后可引用“FEC-OSL训练集显式含无标签auxiliary unknown，novel unknown另留测试”（PDF第3、9页），这是协议分类直接证据。

## W. 不能引用或尚未证明的内容

- 不能称FEC-OSL为strict unknown-free。
- 不能把USTC/Tor unknown全部称未知攻击。
- 不能把AUC99.13写成FPR95<=5%或同协议SOTA。
- 不能把双分支称真多源多模态。
- 不能声称在线适配已独立评估。

## X. 最终审计

- [x] G0 全文缩译门
- [x] G1 全文门
- [ ] G2 身份门（Zotero待核）
- [x] G3 任务门
- [x] G4 协议门（P1/P3风险已厘清）
- [x] G5 方法门
- [x] G6 结果门
- [x] G7 对比门（公平性缺口已审计）
- [x] G8 局限门
- [x] G9 项目门
- [ ] G10 引用门
- 最终状态：`project_mapped`；L3内容完成，`complete=否`。
