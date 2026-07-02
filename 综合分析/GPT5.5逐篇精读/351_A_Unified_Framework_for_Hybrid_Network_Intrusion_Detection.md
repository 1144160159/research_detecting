# [351] A Unified Framework for Hybrid Network Intrusion Detection

## 1. 基本信息
题名：A Unified Framework for Hybrid Network Intrusion Detection  
中文题名：面向混合网络入侵检测的统一框架  
年份/来源：2025，IEEE Transactions on Network and Service Management  
DOI：10.1109/TNSM.2025.3609854  
主题归属：入侵检测、网络异常检测、开放集/未知攻击检测、零样本攻击分类。

## 2. 中文翻译与核心摘要
这篇论文的核心主张是：混合式 NIDS 不能只是把多个模型串起来，而应明确每个模型的单一职责。作者提出 AUF，把检测流程拆成四级：detector 先判断良性/恶意，discriminator 再判断恶意流量属于已见类还是未知类，classifier 负责已见攻击分类，customized model 处理额外需求，例如用零样本学习辅助未知攻击标注。

这比传统 MADF 的关键变化在于顺序和解耦：良性流量占多数，因此先用 detector 过滤，良性样本不必再进入后续模型；原先 misuse detector 同时承担“已见/未知判别”和“已见类分类”，AUF 将其拆开；四个模块功能独立，也更适合边缘侧检测、云端判别和分类的部署方式。

## 3. 论文解决的具体问题
论文瞄准的是 HNIDS 中的“loss-gain imbalance”：为了提高最终准确率而牺牲推理速度、功能完整性、模块可部署性和对未知攻击的处理能力。

具体说，MADF 类框架有三类问题：第一，良性流量必须经过 misuse detector 和 anomaly detector，推理慢；第二，misuse detector 既要分类已知攻击，又要间接区分未知攻击，职责混杂导致性能瓶颈；第三，两个检测器若分布在不同设备，流量传输和级联延迟高，不利于云边协同。

## 4. 创新点深度提炼
第一，AUF 把“检测、已见/未知判别、已见分类、定制处理”拆成四个统一接口，给混合式 NIDS 一个可复用架构，而不是只提出一个模型组合。

第二，论文把 discriminator 提升为独立模块，这是最关键的设计点。没有 discriminator，detector 只能知道“恶意”，classifier 又只能处理已见类，未知攻击会在系统中没有明确去向。

第三，自适应 KNN 判别器利用了一个网络安全流量上的经验假设：同类攻击在特征空间中更聚集，已见攻击样本的近邻更可能来自训练集，未知攻击的近邻更可能来自测试批次。自适应 k 用局部密度缓解类别极不平衡。

第四，customized model 用 SG-ZSL 处理未知攻击分类，把 SecureBERT 提取的攻击类别语义、WGAN 特征生成、语义匹配、互信息最大化和监督对比学习组合起来，目标是降低管理员给未知攻击打标签的成本。

## 5. 科学问题与研究假设
科学问题可以概括为：在同时存在已知攻击、未知攻击和严重类别不平衡的网络环境中，是否能通过功能解耦的混合框架，同时获得较好的检测准确率、分类完整性、推理速度和部署灵活性？

主要假设包括：良性流量在真实网络中占多数；detector 能对未知恶意流量保持一定泛化能力；恶意流量在特征空间具有可利用的类簇结构；局部密度能反映多数类/少数类对 k 的不同需求；攻击类别名称或描述中包含足以辅助零样本分类的语义信息。

## 6. 科学方法与技术路线
技术路线是一个级联但解耦的四阶段流水线。

阶段 1：XGBoost detector 输出异常分数，超过阈值的样本进入恶意流量分支。  
阶段 2：自适应 KNN discriminator 在训练集已见恶意样本和测试恶意样本的联合空间中查近邻，根据近邻中来自训练集的比例计算 OOD 分数。局部平均距离越小，k 越大；局部密度低的少数类使用较小 k。  
阶段 3：XGBoost classifier 对已见恶意类别做多分类。  
阶段 4：SG-ZSL 为未知恶意类别生成特征并训练 unseen classifier，用于辅助标注未知攻击。

## 7. 实验设计与实验步骤
数据：使用 CIC-IDS2017 和 BoT-IoT。CIC-IDS2017 保留 70 维特征，含 14 类恶意流量；BoT-IoT 使用 10 维特征，含 DDoS、DoS、Reconnaissance、Theft 等恶意类别，二者都高度类别不平衡。

预处理：使用数据集提供的 CSV/特征文件；CIC-IDS2017 按既有工作预处理；不同阶段分别归一化，以适配 detector、discriminator 和 classifier。

模型/基线：AUF 使用 XGBoost detector、adaptive KNN discriminator、XGBoost seen classifier、SG-ZSL unseen classifier；对比 HIoT、DNN OOD、Verkerken 多阶段方法，以及 CE-GZSL、CO-GZSL、CD-GZSL 等零样本方法。

训练：CIC-IDS2017 随机选 11 个已见恶意类、3 个未知恶意类，98 个划分；BoT-IoT 选 2 个已见、2 个未知，保留 6 个划分。XGBoost 使用默认参数；SG-ZSL 使用 Adam、batch size 2048、学习率 1e-4，并为每个未知类生成 10000 个样本。

指标：detector/discriminator 用 AUC-ROC、AUC-PR、Micro Recall、Macro Recall；分类器和最终级联系统重点看 Micro/Macro Recall；统一按 TPR=0.99 选择阈值。

消融/敏感性：重点分析固定 k 与自适应 k、kmin/kmax/khat 对 discriminator 的影响，并用 UMAP、密度直方图和混淆矩阵核查错误来源。

结果核查：不仅看总 recall，还逐类检查 Heartbleed、Infiltration、SQL Injection、XSS 等少数类，确认错误是否来自 detector 漏检、discriminator 误判或 classifier 混淆。

## 8. 关键结果、结论与证据
检测阶段：XGBoost detector 在 CIC-IDS2017 上 AUC-ROC 0.9714、AUC-PR 0.9525；在 BoT-IoT 上 AUC-ROC 0.9988、AUC-PR 1.0。AUF 的检测推理时间也明显短于 MADF：CIC-IDS2017 为 0.1522s 对 0.5267s，BoT-IoT 为 0.0957s 对 0.1809s。

判别阶段：adaptive KNN 的 AUC-ROC 和 AUC-PR 均超过 0.99，并显著优于 HIoT 与 DNN。优势来自它不只看距离，也看近邻来自训练集还是测试集，从而更直接刻画“已见/未知”的分布差异。

分类阶段：seen classifier 的 Micro Recall 接近 1，但 Macro Recall 受少数类影响；SG-ZSL 在未知类分类上优于 CE-GZSL、CO-GZSL、CD-GZSL，说明语义引导和互信息约束确实改善了未知攻击特征生成。

最终级联：AUF 在 CIC-IDS2017 上达到 Micro Recall 0.8601、Macro Recall 0.8225；BoT-IoT 上达到 Micro Recall 0.9828、Macro Recall 0.9008。相比之下，HIoT 和 Verkerken 方法的 Macro Recall 明显偏低，主要瓶颈是无法可靠区分已见与未知恶意流量。

## 9. 局限性与待解决问题
最大局限是级联误差会被放大。某个少数类如果在 detector 阶段被漏掉，后续 discriminator 和 classifier 再强也无法恢复；论文中 XSS、Heartbleed、Infiltration 等类别就体现了这一点。

adaptive KNN 还有一个现实部署问题：它利用测试批次与训练集的联合近邻结构，更适合批处理或滑动窗口场景；若要逐流在线检测，需要重新设计近邻维护和阈值更新策略。

SG-ZSL 依赖未知攻击的类别语义或候选名称。它能降低标注成本，但不是完全自动发现未知攻击语义标签。

代码侧也有复现限制：本地仓库不包含数据切分、近邻矩阵和模型参数，只保留脚本与下载提示；`environment.yml` 中若干版本号看起来不可靠，直接复现前需要重建环境约束。

## 10. 与本项目的关系
这篇论文与“异常检测/入侵检测”项目强相关，尤其适合作为开放集网络异常检测的框架型参考。

它提供了三个可直接借鉴的方向：第一，把异常检测从单一二分类扩展为“恶意检测 + 未知攻击识别 + 攻击类型识别”；第二，把 Macro Recall 和少数类表现作为关键评价指标，而不是只看总体准确率；第三，把未知攻击处理从“发现异常”推进到“辅助标注/分类”，对构建实用安全运营系统更有价值。

## 11. 代码对照分析
本地实际仓库为 [A-Unified-Framework-for-Hybrid-Network-Intrusion-Detection](</F:/泉城实验室/二期/论文/异常检测/source/A-Unified-Framework-for-Hybrid-Network-Intrusion-Detection/readme.md:1>)，目录名与元数据中的无连字符版本不同。README 说明需额外下载 dataset splits 和 model parameters 后运行 `main.py`。

数据预处理对应 [dataloader.py](</F:/泉城实验室/二期/论文/异常检测/source/A-Unified-Framework-for-Hybrid-Network-Intrusion-Detection/dataloader.py:5>)：读取 `data/{dataset}/{split}.npz` 与 `benign.npz`，构造 detector 二分类标签、seen/unseen 标签，并为三个阶段分别做 MinMaxScaler。

AUF 主流程在 [main.py](</F:/泉城实验室/二期/论文/异常检测/source/A-Unified-Framework-for-Hybrid-Network-Intrusion-Detection/main.py:459>)：XGBoost detector 在 459/472 行附近；近邻矩阵加载和 adaptive K 计算在 499-521 行；seen classifier 在 534-538 行；可选 customized model 加载 `cls.model` 和 `map.pt` 在 545-557 行；最终级联融合在 573 行以后。

SG-ZSL 的本地源码并不完整。[model.py](</F:/泉城实验室/二期/论文/异常检测/source/A-Unified-Framework-for-Hybrid-Network-Intrusion-Detection/model.py:5>) 只给出 `EmbeddingNet`，更像论文中 encoder/projection 的推理映射；WGAN、SecureBERT 语义提取、互信息估计和训练流程未在仓库中完整展开。

基线脚本包括 [DNN.py](</F:/泉城实验室/二期/论文/异常检测/source/A-Unified-Framework-for-Hybrid-Network-Intrusion-Detection/DNN.py:397>) 的第 K 近邻距离 OOD 分数、[Bovenzi.py](</F:/泉城实验室/二期/论文/异常检测/source/A-Unified-Framework-for-Hybrid-Network-Intrusion-Detection/Bovenzi.py:462>) 的 `1 / max(probability)` 判别分数，以及 [Verkerken.py](</F:/泉城实验室/二期/论文/异常检测/source/A-Unified-Framework-for-Hybrid-Network-Intrusion-Detection/Verkerken.py:551>) 的额外 benign 重判步骤。

## 12. 本篇精华
1. AUF 的真正贡献不是某个单点模型，而是把 HNIDS 的功能边界重新划清。  
2. detector 前置是为了速度：多数良性流量只经过一级模型。  
3. discriminator 独立化是为了完整性：它连接“恶意检测”和“攻击分类”，专门处理未知攻击流向。  
4. adaptive KNN 的核心是利用近邻来源，而不仅是近邻距离。  
5. 类别不平衡是贯穿全文的主要困难，Macro Recall 比 Micro Recall 更能暴露问题。  
6. SG-ZSL 将未知攻击分类转化为语义条件特征生成，适合“辅助标注”而非完全自动归因。  
7. 级联系统的最终性能由最弱上游模块限制，少数类漏检会在后续阶段被放大。  
8. 论文给出的 seen/unseen 划分协议可作为开放集 NIDS 后续研究的实验基线。

## 13. 建议精读路线
先读 Figure 1 和 Figure 2，弄清 AUF 相比 Non-framework cascading 与 MADF 的结构差异。

再读 Methodology 的 Discrimination 小节，重点理解 adaptive KNN 为什么用训练集近邻数量作为 OOD 证据。

然后读 Experimental Setup 的数据划分，这部分比模型细节更重要，因为它决定了论文是否真的在测未知攻击泛化。

最后集中看 Table IV、Table V、Table VI 和 Figure 15/16，把每个阶段的错误如何传递到最终混淆矩阵串起来。代码阅读则按 `dataloader.py -> main.py -> DNN.py/Bovenzi.py/Verkerken.py -> model.py` 的顺序最省时间。

<!-- codex-cli-deep-read: complete -->
