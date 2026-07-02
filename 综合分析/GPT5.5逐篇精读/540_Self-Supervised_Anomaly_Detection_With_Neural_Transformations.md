# [540] Self-Supervised Anomaly Detection With Neural Transformations

## 1. 基本信息
- 题名：Self-Supervised Anomaly Detection With Neural Transformations
- 作者：Chen Qiu, Marius Kloft, Stephan Mandt, Maja Rudolph
- 来源：IEEE Transactions on Pattern Analysis and Machine Intelligence；正文显示在线发表为 2024-12-18，期刊卷期为 2025 年 3 月刊。
- DOI：10.1109/TPAMI.2024.3519543
- 方法名：NeuTraL AD，即 Neural Transformation Learning for Anomaly Detection。
- 代码：`source\NeuTraL-AD`。本地代码包主要对应作者 2021 ICML 版 NeuTraLAD 核心实现，覆盖时间序列、表格、原始图像和图像特征；TPAMI 论文新增的文本、图级异常检测和部分 OOD 实验在该代码包中未看到直接实现。

## 2. 中文翻译与核心摘要
这篇论文的核心命题是：自监督异常检测依赖“变换/增强”构造辅助任务，但图像之外的数据很难人工设计可靠变换。论文提出让模型自己学习一组神经变换，并用一种确定性对比损失 DCL 同时训练变换器、编码器和异常分数。

DCL 的直觉很清楚：同一个样本经过不同神经变换后，仍应保留与原样本相关的语义；但不同变换视图又必须彼此可区分。训练完成后，如果一个测试样本来自正常分布，模型能产生“语义一致但视图多样”的结构，损失低；异常样本不能被这些正常模式下学到的变换关系很好解释，损失高。因此训练损失本身就是异常分数。

## 3. 论文解决的具体问题
论文解决的不是“如何做一个新的分类器”，而是异常检测里更基础的问题：非图像数据缺少自然的数据增强。

具体痛点包括：
- 图像可用旋转、裁剪、翻转等人工变换，时间序列、表格、文本、图结构没有通用变换。
- 传统对比学习常依赖 batch 内其他样本作为负样本，测试时异常分数会受样本池选择影响，不适合单样本打分。
- Deep SVDD/OCC 类方法把正常样本压向单个中心，表达能力有限，容易忽略正常类内部的多视角结构。
- 对网络安全、医疗、传感器等领域，异常往往不是局部噪声，而是样本整体结构不符合正常机制，需要能学习“正常样本内部可变换关系”的方法。

## 4. 创新点深度提炼
第一，论文把“数据增强设计”转成“神经变换学习”。NeuTraL AD 不要求人预先定义哪些变换是合理的，而是学习 K 个变换视图。

第二，DCL 的负样本不是其他数据点，而是同一样本的其他变换视图。这让异常分数只依赖当前样本，避免了传统对比学习在异常检测测试阶段的负样本偏差。

第三，DCL 同时约束“语义保持”和“视图多样”。分子项拉近变换视图与参考视图 T0，分母项拉开不同变换视图。论文的 β 消融说明，只追求语义会导致视图塌缩，只追求多样会丢失语义。

第四，NeuTraL AD 可被看成 Deep OCC 的多视图推广。若把相似度换成负欧氏距离，DCL 退化出多视图 one-class 形式；T0(x) 相当于样本相关中心，比固定中心 c 更灵活。

第五，TPAMI 版把方法推广到时间序列、表格、图像特征、文本和图级异常检测，并展示了图像 mask、文本 attention word、图级 performance flip 等分析。

## 5. 科学问题与研究假设
科学问题：能否在无异常标签或少标签条件下，自动学习适合异常检测的数据变换，使自监督损失成为可靠异常分数？

核心研究假设：
- 正常样本存在稳定的“内部语义结构”，不同变换视图可以共享这些结构。
- 异常样本不遵循正常数据中的这种变换一致性，因此 DCL 会更高。
- 有效异常检测需要同时满足两点：变换不能破坏语义，变换之间也不能完全相同。
- 多个样本相关视图比单中心 one-class embedding 能捕获更丰富的正常模式。

## 6. 科学方法与技术路线
对每个样本 x，模型构造 K+1 个表示：T0(x) 是参考嵌入，T1(x)…TK(x) 是学习得到的变换嵌入。DCL 对每个 Tk(x) 计算：它应接近 T0(x)，同时远离其他 Tl(x)。

技术路线：
- 输入无标签训练集，默认大多数或全部为正常样本。
- 为不同数据类型选择变换器 φk 和编码器 f。
- 用 DCL 联合训练所有变换器和编码器。
- 测试时直接计算同一个 DCL loss，作为异常分数 s(x)。
- 阈值 τa 由应用场景或验证集校准。

各模态实现思路：
- 时间序列：1D 卷积残差变换器，残差或乘性 mask，K=11。
- 表格：MLP 变换器和 MLP 编码器，K=11。
- 图像：原始图像用卷积 mask；图像特征用预训练 ResNet 特征加线性变换，K=15。
- 文本：GloVe word embedding，逐词 mask，再用 attention 聚合句子表示，K=10。
- 图：每个 Tk 是 GIN，使用负欧氏距离保留图大小等范数信息，K=5。

## 7. 实验设计与实验步骤
可复核流程如下：

1. 数据：时间序列使用 SAD、NATOPS、CT、Epilepsy、RS；表格使用 Arrhythmia、Thyroid、KDD、KDDRev；图像使用 F-MNIST、CIFAR-10、CIFAR-100 和 OOD 数据；文本使用 Reuters；图使用 DD、PROTEINS、NCI1、AIDS、IMDB-BINARY、REDDIT-BINARY。
2. 预处理：分类数据转 one-vs-rest 或 n-vs-rest；训练集只保留正常类；测试集保留正常与异常类。KDD 做 one-hot 和连续特征标准化；文本小写、去停用词、tokenize 后取 GloVe；图数据做 10-fold cross-validation。
3. 模型/基线：比较 OCSVM、IF、LOF、Deep SVDD、DAGMM、DROCC、GOAD、RNN/LSTM-ED、GEOM、CSI、DN2、PANDA、CVDD、OCGIN、Graph2Vec/FGSD/WLK/PK 等。
4. 训练：用 Adam 或 SGD 变体最小化 DCL；温度多为 0.1；不同模态使用不同 K 和网络结构。
5. 指标：时间序列、图像、文本、图主要报告 AUC；表格遵循前作报告 F1；部分实验还报告 AP 和 performance flip。
6. 消融/敏感性：调节 β 检查语义项和多样性项；比较 DCL、普通 contrastive loss、classification loss；做 n-vs-rest 检查正常分布多模态化后的鲁棒性。
7. 结果核查：不仅看平均 AUC/F1，还看例外情形：RS 上人工变换仍强，SAD 多正常类时 LOF 强，CIFAR-100 n-vs-rest 时 DN2 强，原始图像上 NeuTraL-I 不如人工几何变换。

## 8. 关键结果、结论与证据
- 时间序列 one-vs-rest 平均 AUC 提升约 7.2%；Epilepsy 从 82.6% 提到 92.6%。
- 时间序列 n-vs-rest 平均 AUC 提升约 7.9%，说明方法对正常类变复杂有一定鲁棒性，但 KNN/LOF 在部分多模态正常分布上仍有优势。
- 表格数据上 NeuTraL AD 在 Arrhythmia、Thyroid、KDD、KDDRev 全部优于基线，平均 F1 提升约 2.9%。
- Reuters 文本异常检测平均 AUC 达 94.7%，优于无 outlier exposure 的既有结果。
- 图级异常检测六个数据集平均 AUC 提升约 7.5%，相对 OCGIN 平均提升约 15.4%，且没有出现 performance flip。
- 图像结论更克制：原始图像上学习变换不如人工几何变换；但在预训练图像特征上，NeuTraL-F 有价值，避免 KNN 式测试时存储训练集。

## 9. 局限性与待解决问题
- 方法仍假设训练数据主要是正常样本，污染训练集下的鲁棒性不是本文重点。
- one-vs-rest/n-vs-rest 是由分类数据集改造的异常检测基准，和真实网络攻击、工业故障、欺诈事件仍有差距。
- 阈值选择在实际部署中仍需要验证集、业务规则或风险预算。
- 原始图像上学习变换未超过人工设计变换，说明“自动学变换”不是在所有模态都天然优越。
- 多正常类、多峰正常分布下，LOF/DN2 这类近邻方法有时更强。
- TPAMI 正文包未截断；本次理解不受正文缺页影响。但本地代码包不是 TPAMI 全量扩展实现，文本、图级异常检测和部分 OOD 实验仍需查作者补充材料或新版仓库复核。

## 10. 与本项目的关系
与“入侵检测与网络异常检测”的关系是弱到中等：论文不是专门做网络流量安全，但 KDD/KDDRev 是网络入侵表格数据，方法思想可迁移。

可借鉴点：
- 对 NetFlow、系统调用统计、主机行为画像等表格特征，可用 NeuTraL AD 作为深度 one-class baseline。
- 对时间窗口流量序列，可采用时间序列分支，让模型学习频段、突发、周期等 mask 或残差变换。
- 对通信图、账号交易图、主机进程图，可参考论文图级 GIN 版本，但本地代码包未包含该部分。
- 对安全解释，可分析乘性 mask 关注哪些字段或时间段，例如端口、协议、包长、连接间隔、失败登录频次。

不宜过度外推：KDDCUP99 很旧，不能代表现代加密流量、APT 横向移动、云原生日志和概念漂移场景。

## 11. 代码对照分析
我核对的关键文件如下：

- 入口：[Launch_Exps.py](<F:/泉城实验室/二期/论文/异常检测/source/NeuTraL-AD/Launch_Exps.py>) 调用 `Grid` 读配置，再用 `KVariantEval` 循环 normal class。
- 配置映射：[config/base.py](<F:/泉城实验室/二期/论文/异常检测/source/NeuTraL-AD/config/base.py>) 把 `seqNTL/tabNTL/featNTL/visNTL`、`DCL/EucDCL`、Adam、StepLR 等字符串映射到类。
- 损失：[models/Losses.py](<F:/泉城实验室/二期/论文/异常检测/source/NeuTraL-AD/models/Losses.py>) 实现 DCL。`eval=True` 时返回每个样本的 DCL 和，正是异常分数。
- 模型封装：[models/NeutralAD.py](<F:/泉城实验室/二期/论文/异常检测/source/NeuTraL-AD/models/NeutralAD.py>) 根据 `trans_type` 执行 `forward/mul/residual`，拼接原视图和 K 个变换视图。
- 网络结构：`TabNets.py` 对应表格 MLP；`SeqNets.py` 对应 1D CNN 时间序列；`FeatNets.py` 对应预训练图像特征；`VisNets.py` 对应原始图像卷积 mask。
- 训练评估：[models/NeutralAD_trainer.py](<F:/泉城实验室/二期/论文/异常检测/source/NeuTraL-AD/models/NeutralAD_trainer.py>) 完成训练、AUC/AP/F1 计算；[evaluation/Kvariants_Eval.py](<F:/泉城实验室/二期/论文/异常检测/source/NeuTraL-AD/evaluation/Kvariants_Eval.py>) 做 one-vs-rest 多类循环。
- 数据加载：[loader/LoadData.py](<F:/泉城实验室/二期/论文/异常检测/source/NeuTraL-AD/loader/LoadData.py>) 构造正常训练集和混合测试集；[loader/LoadTabular.py](<F:/泉城实验室/二期/论文/异常检测/source/NeuTraL-AD/loader/LoadTabular.py>) 处理 Thyroid、Arrhythmia、KDD、KDDRev。
- 图像特征：[Extract_img_features.py](<F:/泉城实验室/二期/论文/异常检测/source/NeuTraL-AD/Extract_img_features.py>) 用 ImageNet 预训练 ResNet152 提取 CIFAR-10 2048 维特征。

运行线索：
```bash
python Launch_Exps.py --config-file config_kdd.yml --dataset-name kdd
python Launch_Exps.py --config-file config_arabic.yml --dataset-name arabic_digits
python Launch_Exps.py --config-file config_cifar10_feat.yml --dataset-name cifar10_feat
```

代码层面需要注意：`DATA` 目录当前基本没有实际数据；代码默认 `cuda`；`requiresments.txt` 文件名拼写异常；部分地方使用已弃用的 `np.int`；`load_data` 返回 `[trainset, testset, testset]`，验证集和测试集在该原型中重合；F1 阈值使用测试标签中的正常比例，部署时不能照搬。

## 12. 本篇精华
- NeuTraL AD 的核心不是新编码器，而是把“增强设计”学习化。
- DCL 的高明之处在于负样本来自同一样本的其他变换视图，因此异常分数可单样本确定计算。
- 方法同时要求语义保持和视图多样，缺任何一边都会塌缩或失去检测意义。
- Deep OCC 是它的一个退化视角；NeuTraL AD 用样本相关中心和多视图正常性替代固定中心。
- 非图像数据是本文最大价值点，尤其时间序列、表格和图级异常检测。
- 图像实验说明作者并不夸大：人工几何增强在原始图像上仍强，NeuTraL 更适合难以人工设计增强的表示空间。
- 对网络安全项目，可作为 flow/tabular/time-series/graph anomaly 的统一自监督 baseline，但不能直接证明其适合现代入侵检测。

## 13. 建议精读路线
1. 先读 Section II-B，吃透 T0、Tk、DCL 和 score 的关系。
2. 再读 Section II-C，把 DCL 与 Deep SVDD/OCC 对照，理解为什么多视图更强。
3. 精读 Section III-B 和 III-D，因为它们最接近时间序列异常和网络入侵表格数据。
4. 快读图像部分，重点看“原始图像不占优、特征空间有优势”的边界结论。
5. 读图部分时关注 negative Euclidean similarity 和 performance flip，这对通信图异常检测有启发。
6. 对照代码从 `models/Losses.py`、`models/NeutralAD.py`、`loader/LoadData.py`、`config_files/config_kdd.yml` 这条线读起，最快能把论文公式落到可运行实现。

<!-- codex-cli-deep-read: complete -->
