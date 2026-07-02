# [685] Fine-Grained Detection and Analysis of Unknown Encrypted Malicious Traffic From Mixed Noisy Labels

## 1. 基本信息
- 题名译法：**从混合噪声标签中细粒度检测与分析未知加密恶意流量**。
- 年份/来源：2026，IEEE Transactions on Dependable and Secure Computing，DOI: `10.1109/tdsc.2026.3697849`。
- 主题定位：恶意加密流量检测、未知攻击发现、闭集/开集混合标签噪声鲁棒学习。
- 代码：`source\Sieve`，主入口为 `train.py`、`unknown_traffic_detect.py`、`Unknown_Traffic_Labeling/`。

## 2. 中文翻译与核心摘要
论文要解决的是：真实 NIDS 训练数据往往不是“干净闭世界”，而是同时含有闭集错标和开集错标。闭集错标会模糊已知类别边界；开集错标更危险，因为未知攻击样本被强行贴成已知标签，模型会把未来未知攻击学成“正常”或“已知恶意”。

Sieve 的核心思路是先“筛”再“测”再“标”：先用邻域一致性和高置信扩展净化训练集，纠正闭集噪声并排除开集噪声；再在净化后的紧凑特征空间中用 Mahalanobis 距离做后验未知检测；最后对检测出的未知流量估计类别数并半监督聚类，辅助安全专家更新数据集。

## 3. 论文解决的具体问题
传统恶意流量分类默认训练标签可靠，未知检测方法也常默认已知类训练集干净。本文指出真实场景更复杂：自动标注、人工标注、跨数据源混入都会产生混合噪声。尤其是 open-set noise 无法通过“改成某个已知标签”解决，因为它本来就不属于已知类别。

因此，论文的具体问题是：在训练集同时存在闭集噪声和开集噪声时，如何保持已知恶意流量分类能力，同时把未知加密恶意流量从已知类分布外检测出来，并进一步组织成可人工复核的新类别。

## 4. 创新点深度提炼
- **问题设定更贴近真实 NIDS**：不是单独做 noisy-label learning，也不是单独做 open-set detection，而是在 mixed noisy labels 下联合考虑已知分类、未知检测和未知标注。
- **闭集纠正与开集拒绝分治**：闭集噪声用模型高置信预测纠正，开集噪声通过邻域一致性和置信度过滤掉，避免把未知攻击硬塞进已知标签空间。
- **后验未知检测避免训练耦合污染**：未知检测不参与训练损失，而是在净化训练完成后用 Mahalanobis 距离判断离群，降低噪声样本对检测边界的干扰。
- **对比学习服务于 OOD 几何结构**：自监督对比损失不是单纯提高分类准确率，而是压缩已知类类内分布，让未知样本在距离度量上更容易暴露。
- **检测后还有标注闭环**：未知流量不是只报一个告警，而是进入类别数估计和半监督 K-means++ 聚类，面向数据集增量更新。

## 5. 科学问题与研究假设
科学问题可以概括为三个层次：混合噪声下哪些样本可被信任；净化后的特征空间是否足以支撑未知检测；检测出的未知流量能否被低成本整理成新类。

核心假设是：干净样本与邻居标签更一致；闭集噪声在训练后可能被已知类高置信识别，开集噪声则难以对任何已知类产生稳定高置信；在净化数据上训练并加入对比学习后，已知类会形成紧凑簇，Mahalanobis 距离能有效刻画“远离所有已知类中心”的未知样本。

## 6. 科学方法与技术路线
Sieve 有三段技术路线。第一段是噪声标签纠正：用编码器提取特征，在特征空间做 KNN 投票，计算样本标签与邻域投票的一致性 `c_i`；`c_i >= ξ` 的样本进入干净子集，未选中但分类器置信度 `max p_i >= ζ` 的样本被预测标签扩展回训练集，然后用类均衡采样缓解类别不平衡。

第二段是模型训练：对选中子集做 MixUp 交叉熵监督训练，同时对全体训练样本做双视图自监督对比学习，损失为 `L = Lce + λLself`。第三段是未知检测与标注：用净化训练样本的类均值和协方差构造 Mahalanobis 检测器，再对未知样本估计类别数并半监督聚类。

## 7. 实验设计与实验步骤
1. 数据：Mal TLS2023 做 23 类恶意 TLS 分类，CipherSpectrum/TLS1.3 做未知类；DDoS2019 做二分类，IDS2018 做未知类。
2. 预处理：TLS 使用一维流统计特征，DDoS/IDS 使用 CICFlowMeter 风格流级统计特征；代码中 `TLS_feature_extract.py` 提取长度、方向、时间间隔、速率等特征。
3. 噪声构造：总噪声率设为 0.1/0.3/0.5，包含 symmetric/asymmetric 闭集噪声，并设置 open-set 噪声占噪声样本的 0.5。
4. 模型与基线：Sieve 使用 1D DeepResNet 编码器；对比 RAPIER、MCRe、DSDIR、FOSS、RFG-HELAD、AEGIS-Net 及 CNN。
5. 训练：100 epoch，SGD，momentum 0.9，weight decay `5e-4`，cosine schedule，`ξ=1.0`、`ζ=0.93`、`K=100`、`λ=1.0`。
6. 指标：已知分类看 Accuracy/F1；未知检测看 Accuracy/F1、AUC、TNR@TPR95、FPR；未知标注看 known/novel accuracy、NMI、ARI、harmonic accuracy。
7. 消融与敏感性：去掉 label correction、subset expansion、contrastive loss；扫描 `ξ/ζ/K`；用 MSP、Energy、Cosine 替换 Mahalanobis 做 OOD 对照。

## 8. 关键结果、结论与证据
在 Mal TLS2023 上，Sieve 在多种混合噪声下已知类 Accuracy/F1 基本保持 94% 以上；即使 `0.5Sym 0.5Open`，表中仍约为 `94.96/94.75`。DDoS2019 上更稳定，多数场景接近或超过 98.5%，最高约 99%。

未知检测上，Sieve 在 Mal TLS2023 和 DDoS2019 的高噪声场景仍能保持很高 F1，明显优于 FOSS、AEGIS-Net、RFG-HELAD 及 Sieve 的 MSP/Energy/Cosine 变体。代码日志中，Mal TLS2023 `0.5Sym 0.5Open` 的 OOD 结果为 AUROC 约 `99.73%`、F1 约 `97.11%`，与论文结论一致。第三阶段结果显示已知类聚类可达到 1.0，但 novel accuracy 约 0.418，说明未知标注仍依赖人工合并和复核。

## 9. 局限性与待解决问题
论文自己承认未知流量标注存在过分割：估计类别数可能大于真实类别数，安全上比欠分割更可接受，但会增加人工合并工作。未知流量来自外部公开数据集的“模拟未知”，不等同于真实线上逐渐演化、形态分散、混杂概念漂移的未知攻击。

代码层面也有复现障碍：多个路径硬编码为 `/home/ju/Desktop/TNSE/Sieve/...`，直接在当前 Windows 工作区运行需要改路径；类别数估计源码中搜索目标用 Fowlkes-Mallows 与 Davies-Bouldin 的组合，和正文“ACC-DB”的表述略有差异。本次正文包显示未截断，因此理解不受正文截断影响。

## 10. 与本项目的关系
这篇论文与“异常检测/恶意流量/未知攻击发现”强相关，适合作为本项目中“噪声鲁棒开放集恶意流量检测”的核心参考。它的价值不只是一个模型，而是给出从低质量标签训练、未知检测、未知样本整理到数据集更新的闭环流程。

如果本项目面对真实安全运营数据，Sieve 的启发是：不要直接相信历史标签；先识别闭集噪声与开集噪声，再训练分类器；未知告警后不要只输出二值结果，而应聚类给分析员做新家族确认。

## 11. 代码对照分析
- 数据预处理：`datasets/TLS_feature_extract.py` 对 pcap 流提取一维统计特征；`datasets/dataloader_tls.py` 负责 Mal TLS2023、DDoS2019、TLS1.3、IDS2018 加载，并按比例注入闭集/开集噪声。
- 模型：`models/preresnet.py` 的 `DeepResNet` 是 1D 残差编码器，输出 256 维特征；`feature_list()` 支持检测阶段拼接多层特征。
- 训练：`train.py` 的 `evaluate()` 实现高置信重标注、KNN 邻域一致性筛选和扩展；`train()` 实现 MixUp 交叉熵与双向对比损失；`ClassBalancedSampler` 对选中样本做类均衡采样。
- 未知检测：`unknown_traffic_detect.py` 的 `Sieve_unknown_detect` 计算每类均值和伪逆协方差，返回负 Mahalanobis 距离最大值；阈值由训练得分低分位确定，以保证目标 TPR。
- 未知标注：`Unknown_Traffic_Labeling/save_ood_samples.py` 保存 ID/OOD 特征；`run_gcd_pipeline.py` 调用 `novel_category_discovery.py` 做类别数估计和半监督 K-means；`utils/faster_mix_k_means.py` 是半监督 K-means 实现。

## 12. 本篇精华
- 真实 NIDS 的核心难点不是“有没有未知攻击”这么简单，而是未知攻击可能已经以错标形式污染训练集。
- 开集噪声不能靠普通 label correction 解决，必须从训练监督中拒绝掉。
- 邻域一致性适合做第一层筛子，高置信预测适合把漏掉的闭集样本捞回来。
- 后验 Mahalanobis 检测的效果依赖前面净化和对比学习形成的紧凑已知类簇。
- Sieve 的贡献在于组合闭环：纠错/拒绝、鲁棒训练、未知检测、未知聚类标注。
- 结果显示高噪声下已知分类和未知检测都很强，但未知标注阶段仍是半自动，过分割和专家复核不可避免。
- 代码基本覆盖论文三模块，但复现前要处理硬编码路径、数据文件位置和 GPU 环境。

## 13. 建议精读路线
先读 Introduction 和 Problem Statement，抓住“closed-set noise vs open-set noise”的危害差异。再精读 Section IV，重点看 `c_i` 邻域一致性、`ζ` 高置信扩展、MixUp+contrastive loss、Mahalanobis score 四个连接点。

随后读实验表 IV-VI 和消融表 IX，判断每个模块是否真的必要。最后对照代码阅读顺序建议为：`datasets/dataloader_tls.py` → `train.py` → `unknown_traffic_detect.py` → `Unknown_Traffic_Labeling/novel_category_discovery.py`。

<!-- codex-cli-deep-read: complete -->
