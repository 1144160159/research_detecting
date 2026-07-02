# [182] AutoML4ETC: Automated Neural Architecture Search for Real-World Encrypted Traffic Classification

## 1. 基本信息

- 题名：AutoML4ETC: Automated Neural Architecture Search for Real-World Encrypted Traffic Classification
- 中文题名：AutoML4ETC：面向真实世界加密流量分类的自动神经架构搜索
- 年份：元数据为 2023；论文正式刊于 IEEE TNSM Vol. 21 No. 3, June 2024，在线发表时间为 2023-10-17。
- DOI：10.1109/TNSM.2023.3324936
- 主题：加密流量分类、AutoML、NAS、TLS/QUIC、早期分类、数据漂移。
- 相关性判断：强相关。它不是异常检测模型本身，但明确把流量分类视为 IDS/anomaly detection 的前置能力，并重点解决真实生产数据漂移下模型退化问题。

## 2. 中文翻译与核心摘要

论文的核心意思是：深度学习加密流量分类器在实验数据上表现不错，但一旦进入 ISP 级真实网络，性能会随时间下降；单纯用新数据重训只能部分恢复，根因之一是旧架构已经不再适配新数据分布。作者提出 AutoML4ETC，用神经架构搜索自动为目标数据集生成轻量、高性能的加密流量分类神经网络。

它的关键不是泛泛使用 AutoML，而是为“包头原始字节 + 早期分类”专门设计搜索空间：从 TLS 前 3 个握手包或 QUIC 的单个 ClientHello 中学习分类信号，并在 Normal/Reduction cell 内搜索输入连接和候选操作。实验覆盖 Orange 移动网络真实 TLS/QUIC 流量和公开数据集，生成架构总体优于 UWOrange-H、UCDavis CNN、DeepPacket CNN、E2E CNN 等手工设计模型，同时参数量显著更小。

## 3. 论文解决的具体问题

论文针对的是生产环境中的三个具体痛点。

第一，数据漂移导致加密流量分类器老化。UWOrange 原先在 Orange 数据和公开数据上表现很好，但后续同一采集流程的新数据上性能下降，说明问题不只是训练样本不足，而是数据统计属性和类别分布变化后，原架构归纳偏置失配。

第二，手工调架构成本高。重新调学习率、卷积层数、核大小、分支结构和正则化策略需要专家经验，而且主要靠试错，不适合周期性生产维护。

第三，真实网络需要早期、轻量分类。ISP 或安全监测场景不能等完整流结束，论文希望只用 TLS 前 3 个握手包或 QUIC 的首个 ClientHello，就完成服务级或应用级分类，并降低模型参数量。

## 4. 创新点深度提炼

- 面向 ETC 的专用 NAS 搜索空间：不是把图像 NAS 直接搬过来，而是把 ETC 中有效的 1D raw byte CNN 经验、separable convolution、pooling、identity、skip/loose-end 汇合组织成可搜索 cell。
- 把“早期分类”纳入架构设计目标：TLS 只看前 3 个握手包，QUIC 只看 ClientHello，避免依赖长流统计。
- 将生产数据漂移问题转化为自动架构适配问题：论文的主张不是“模型重训一次即可”，而是“新数据到来时可重新搜索更适配的新架构”。
- 兼顾准确率和模型复杂度：搜索目标虽然主要以验证性能为 reward，但实验持续报告参数量，强调 AutoML4ETC 生成模型比手工 CNN 更轻。
- 系统比较搜索空间、搜索算法和训练策略：分别评估 AutoML4ETC 搜索空间、RL/MCTS/EA/RS 搜索算法、10 epoch partial training 与 40 epoch full training。

## 5. 科学问题与研究假设

科学问题可以概括为：在真实加密流量分布随时间变化的条件下，是否存在一种 ETC 专用架构搜索空间，使得自动搜索得到的轻量模型比人工设计模型更稳定、更准确、更适合早期分类？

核心假设包括：

- 加密流量包头原始字节仍包含足够的服务/应用分类信号，即使 SNI、cipher、IP 等显式标识被遮蔽。
- 手工架构在特定历史数据上最优，不代表在新月份、新协议或新类别分布上仍最优。
- 搜索空间质量比搜索算法复杂度更关键；若搜索空间足够贴合 ETC，简单随机搜索也能找到较好架构。
- 对 child model 训练不足会节省搜索时间，但可能错选架构，因此存在搜索时间与最终性能之间的权衡。

## 6. 科学方法与技术路线

技术路线是“数据预处理与脱敏标注 -> ETC 专用 NAS 搜索空间 -> 多搜索算法搜索 child architecture -> 训练/验证 -> 与手工模型和其他搜索空间比较”。

搜索空间中，每个 child model 由 Normal cell 和 Reduction cell 组成；cell 前面分别接 Filter Alignment 或 Factorized Reduction。每个 cell 内有若干节点，节点从已有节点输出中选择两个输入，再分别选择操作：identity、3/5 核 separable convolution、3 核 average pooling、3 核 max pooling，最后将两个分支相加。未被后续节点使用的 Loose Ends 也会并入输出，避免中间信息浪费。

训练上采用 Adam、初始学习率 0.001、每 10 epoch 学习率减半、sparse categorical cross-entropy。搜索算法比较 RL、MCTS、EA 和 RS；最终论文选择 RL、100 trials、每个 child model 40 epochs 作为主实验设置。

## 7. 实验设计与实验步骤

1. 数据：使用 6 个 Orange 移动网络真实数据集，其中 5 个 TLS、1 个 QUIC；另加 3 个公开 benchmark。每个数据集按 80% 训练、20% 测试/评估划分。
2. 预处理：PCAP 先移除 TLS/QUIC header 之后的 payload；按五元组切分 flow。TLS 提取前 3 个 handshake packet header；QUIC 只提取 handshake 阶段第一个 ClientHello。
3. 标注与脱敏：用 SNI 生成标签，但随后遮蔽 SNI、cipher 信息和 IP 地址；无 SNI 的相邻 flow 通过 session-id 或接近开始时间进行近似扩展标注。
4. 输入表示：真实数据采用 600-byte cutoff；目标是让模型学习包头内在模式，而不是直接记忆 SNI 到类别的映射。
5. 模型与基线：比较 UWOrange-H、UCDavis CNN、DeepPacket CNN、E2E CNN；另构造 CNN-2D+MLP、CNN-1D+MLP、ENAS Micro 等搜索空间作消融。
6. 训练：child model 用 Adam 训练；搜索空间评估中 May 2021 TLS 数据集用于计时和比较；主设置为 100 trials、40 epochs。
7. 指标：报告 accuracy、weighted precision、weighted recall、weighted F1-score。
8. 消融/敏感性：比较搜索空间、RL/MCTS/EA/RS、10 epoch partial training 与 40 epoch full training。
9. 结果核查：纯文本正文没有展开 Table VII/VIII 的所有逐项数值，因此精确逐数据集结果仍应回 PDF 表格复核；但正文明确给出总体提升区间和关键数值。

## 8. 关键结果、结论与证据

搜索空间对比中，May 2021 TLS 数据集上，CNN-2D+MLP 200 trials 后准确率 77.55%、约 2200 万参数；CNN-1D+MLP 为 78.75%；ENAS Micro 为 80.4%、约 12.06 万参数；AutoML4ETC 搜索空间只用 100 trials 达到 82.86%、约 11.15 万参数。

搜索算法对比中，top-1 child model 的差异很小，最好模型准确率标准差仅 0.25%，说明搜索空间本身贡献很大。MCTS 在 top-5 到 top-30 平均表现上更稳定，但 RL 找到的 top-1 模型参数更少，因此论文主实验采用 RL。

训练策略上，10 epoch partial training 的 top model 为 79.71%；40 epoch full training 达到 82.86%。部分训练约节省 75% 搜索时间，但损失约 3% 准确率且参数量更大。

最终与手工 ETC 模型相比，AutoML4ETC 在服务级和应用级分类中均优于 state-of-the-art，正文给出的总体结论是准确率高出约 1% 到 60.1%，平均参数量少 50 倍以上。在 synthetic QUIC-UCDavis 上达到 100% accuracy，且参数量约少 100 倍。

## 9. 局限性与待解决问题

正文包标注为未截断，本次理解不是基于截断文本；但纯文本缓存没有展开若干表格的完整行列，尤其 Table I/II/VII/VIII 的逐数据集细粒度数值仍需回 PDF 复核。

方法上仍有几个局限：它主要处理闭集服务/应用分类，不能直接解决未知类、恶意流量检测或开放集异常检测；SNI 用于生成标签，虽然训练前被遮蔽，但标签噪声和近邻 flow 扩展标注会影响上限；搜索成本仍不低，40 epoch × 100 trials 对生产周期仍有压力；搜索空间没有纳入 Transformer/Attention，这也是作者列出的未来方向。

## 10. 与本项目的关系

对“异常检测”项目，它的价值主要在三点。

第一，提供加密流量早期表征思路：只用握手阶段包头字节进行识别，可作为异常检测前的协议/应用上下文建模模块。第二，提供应对数据漂移的工程范式：当部署环境变化时，不只重训参数，还要自动调整模型结构。第三，提供轻量化基线：对边缘监测、运营商侧在线检测或高速流量预筛选有参考意义。

但要注意，它不是恶意流量检测论文，也不是开放集检测论文。若用于本项目，需要把其闭集分类器扩展为未知类拒识、漂移监测、异常分数估计或多任务安全检测框架。

## 11. 代码对照分析

代码仓库位于 `source\AutoML4ETC`，公开包更像论文方法的研究复现实现和 QUIC 示例，而不是完整 Orange 真实数据实验流水线。

- 入口与配置：`README.md` 给出 notebook 运行方式；`config.yml` 设置 `searchspace.arch: NRNR`、`init_filters: 64`、`node_num: 4`、`search.searchalgo: RL`、`max_trials: 100`、`training_epoch_per_trial: 40`。
- 主 API：`automl4etc_common.py` 中 `automl4etc_cnn_searchspace()` 构造搜索空间，输入先 reshape 成一维序列，再进入 stem、Normal/Reduction cell 和 softmax 分类头。
- 搜索空间：`hyperkeras/search_space/enas_common_ops_dropoutCNN_05_1DCNN.py` 对应论文 cell 操作，包含 3/5 核 separable conv、avg/max pooling、identity、Dropout(0.4)、ConnectLooseEnd 和 SafeMerge。
- Reduction/Alignment：`hyperkeras/search_space/enas_layers_1D.py` 实现 FilterAlignment、FactorizedReduction、CalibrateSize、SafeMerge。
- 搜索算法：`hyperkeras/searchers/enas_rl_searcher.py` 是 RL controller；`hypernets/searchers/mcts_searcher.py` 是 MCTS；`hypernets/searchers/random_searcher.py` 是 RS。
- 训练封装：`hyperkeras/hyper_keras.py` 负责编译 Keras 模型、学习率调度、评估和保存 `ENAS_models`。
- 数据加载：`commonio/datagen_separated.py` 读取 `.mat`，支持 header/flow 两路特征、归一化、padding/truncate、flow direction/size 分离。
- 示例数据：`test_automl4etc_ucDavisQUIC.ipynb` 调用 `quic_ucdavis_data_loader(path='./quic-dataset')`，五类为 GoogleDoc、GoogleDrive、GoogleMusic、GoogleSearch、Youtube；本地 `pretraining` 目录中五类 `.mat` 数量分别为 1221、1634、592、1915、1077。
- 代码注意点：`automl4etc_common.py` 的 `search()` 内部把 `searcher` 硬编码为 `"RS"`，会覆盖 `config.yml` 的 RL；同时示例 QUIC loader 使用 `flow_only=True` 和 `(1024, 3)` 输入，更像公开 QUIC 示例流程，不等同于论文 Orange TLS/QUIC 包头预处理全流程。复现实验前应检查并修正这些演示化痕迹。

## 12. 本篇精华

- 论文真正的问题意识是生产环境数据漂移下的“架构失配”，不是简单提升某个静态数据集准确率。
- AutoML4ETC 的贡献主要在 ETC 专用 NAS 搜索空间，而不是某个新搜索算法。
- 早期分类设定很强：TLS 前 3 个握手包、QUIC 单 ClientHello，适合在线网络管理和安全预警。
- SNI 只用于弱标注，训练前被遮蔽，方法试图避免学习显式域名映射。
- 1D raw-byte 表示优于把字节强行转成 2D 图像，论文认为 2D 邻接关系会引入无意义空间结构。
- 搜索空间足够好时，RS、RL、MCTS、EA 的 top-1 差距很小；MCTS 更善于稳定产生一批好模型。
- 40 epoch full training 比 10 epoch partial training 更可靠，节省搜索时间会带来可见准确率损失。
- 对异常检测项目，最值得借鉴的是“漂移感知的自动架构更新 + 早期加密流量表征”。

## 13. 建议精读路线

建议先读 Introduction 中 UWOrange 性能衰减和 data drift 动机，再读 Section III 的搜索空间定义，重点画出 Normal/Reduction cell、节点输入选择、候选操作和 Loose Ends。随后读 Section IV-C 的预处理与标注，因为 SNI 脱敏和 QUIC ClientHello 设定决定了实验可信度。最后精读 Section IV-D/F/G：先看搜索空间为什么有效，再看训练 epoch 权衡，最后看与手工模型的总体比较。

读代码时从 `README.md` 和 `test_automl4etc_ucDavisQUIC.ipynb` 入手，再进入 `automl4etc_common.py`、`enas_common_ops_dropoutCNN_05_1DCNN.py`、`enas_layers_1D.py`。复现实验前优先核查 `search()` 的硬编码搜索器和示例数据特征是否符合你要复现的论文设定。

<!-- codex-cli-deep-read: complete -->
