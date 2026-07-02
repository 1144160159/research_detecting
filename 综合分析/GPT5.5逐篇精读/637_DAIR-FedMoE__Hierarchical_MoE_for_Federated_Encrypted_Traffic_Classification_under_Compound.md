# [637] DAIR-FedMoE: Hierarchical MoE for Federated Encrypted Traffic Classification under Compound Drift

## 1. 基本信息

编号 637；题名可译为“DAIR-FedMoE：复合漂移下用于联邦加密流量分类的层次化 MoE”。作者包括 Shamaila Fardous、Kashif Sharif、Fan Li 等。来源为 IEEE Transactions on Dependable and Secure Computing，DOI 为 `10.1109/TDSC.2026.3676447`。正文包 117048 字，标记为未截断。主题属于加密流量分类、联邦学习、分布漂移、类别不均衡、MoE、差分隐私和强化学习专家管理。

代码包位于 [source/DairFM](F:/泉城实验室/二期/论文/异常检测/source/DairFM/README.md:1)，包含模型、训练、仿真、漂移检测、隐私机制、RL 管理和图表生成脚本。

## 2. 中文翻译与核心摘要

这篇论文的核心意思是：联邦学习能让多个边缘网络节点在不共享原始流量的情况下协同训练加密流量分类器，但真实网络流量会同时发生特征漂移 `P(X)`、概念漂移 `P(Y|X)` 和标签漂移 `P(Y)`，而且这些漂移在不同客户端上异步、重叠、强度不同。传统联邦 ETC 方法通常只处理非 IID 或单一漂移，个性化 FL 或多全局模型又带来通信、存储和协调成本。

DAIR-FedMoE 的方案是用一个全局模型承载多个专家：GShard Transformer 负责流量表示，层次化 MoE 将样本路由到稳定专家或漂移专家；每个专家内部用熵驱动的类别权重强化低置信度、少数类或新兴类；服务器端再用 PPO 管理专家池的生成、剪枝和合并。论文声称该方法在 ISCX-VPN、ISCX-Tor、VNAT、USTC-TFC2016 上提升 Macro-F1、少数类召回和漂移恢复速度，同时保持较低通信开销与差分隐私保护。

## 3. 论文解决的具体问题

论文不是单纯做“加密流量分类精度提升”，而是聚焦一个更贴近部署的问题：联邦 ETC 在非平稳环境下会遇到复合漂移。客户端的数据分布不仅类别比例不同，还会因协议升级、应用行为变化、匿名网络、恶意流量演化等因素，使输入特征、类别先验和分类语义同时变化。

已有方法的问题在于：集中式 ETC 默认数据稳定；普通 FL ETC 只关注隐私协同；漂移感知 FL 多处理概念漂移或标签偏移的一部分；个性化 FL、多全局模型虽然能适配客户端差异，但需要维护多套模型，通信和存储成本高；静态 MoE 有专家路由能力，却不能随漂移动态扩容、收缩或合并。

## 4. 创新点深度提炼

第一，论文把“复合漂移”明确建模为联邦 ETC 的核心挑战，而不是把 feature drift、concept drift、label drift 分开处理。这个视角适合网络安全场景，因为真实攻击、协议和用户行为往往一起变化。

第二，提出稳定专家与漂移专家的层次化 MoE。根门控用表示向量和漂移分数判断走稳定分支还是漂移分支，二级门控再选择具体专家，试图在单一全局模型内同时保留稳定知识和快速适配能力。

第三，用专家预测熵做类别重加权。低置信度类别会得到更高损失权重，这本质上是把“专家不确定性”作为动态类别不均衡的代理信号，避免手工指定少数类权重。

第四，用 PPO 管理专家生命周期。专家不是固定数量，而是根据利用率、漂移参与度、置信度、性能变化和专家年龄执行 spawn、prune、merge 或 NoOp，从而在适应性和模型规模之间动态折中。

第五，把隐私威胁模型写入方法链路。论文假设半诚实服务器或部分客户端可观察聚合更新，但不能访问原始包数据；使用 DP-SGD、裁剪、Gaussian noise、安全聚合和 DP 后处理性质来约束泄漏。

## 5. 科学问题与研究假设

科学问题 1：单一全局模型能否在联邦 ETC 中同时处理客户端异构性和复合漂移？论文假设 MoE 的稀疏专家结构可以替代多全局模型，以较低开销实现局部专门化。

科学问题 2：漂移感知路由是否能减少稳定知识被新分布破坏？论文假设稳定流量进入稳定专家，漂移流量进入漂移专家，能降低参数振荡和灾难性遗忘。

科学问题 3：专家熵是否能作为少数类或难分类类的有效信号？论文假设低置信度类别往往对应稀有、变化或未充分学习类别，因此应在损失中上调权重。

科学问题 4：RL 是否能比固定专家池更好地控制模型容量？论文假设 PPO 能从漂移和性能反馈中学会在漂移期扩容，在稳定期剪枝或合并。

## 6. 科学方法与技术路线

技术路线可概括为：加密流量会话转为 token/embedding，进入 GShard Transformer；在 MoE 层中加入 HMoE，客户端用滑动窗口计算当前分布和历史分布的 Jensen-Shannon divergence，并用 EMA 平滑得到漂移分数；根门控根据 `[h; drift_score]` 选择稳定或漂移专家分支；专家输出类别分布，同时累计每类预测熵；熵经 EMA 后转为置信度，再取反形成类别权重，进入加权交叉熵。

联邦训练每轮由服务器广播专家、门控和全局置信度；客户端本地训练 5 个 epoch，batch size 32；更新先裁剪并加 Gaussian DP 噪声，再安全聚合；服务器用 FedAvg 聚合专家与门控参数。PPO 状态包含专家利用率、漂移参与度、类别置信度、Macro-F1/恢复速度变化和专家年龄；动作是剪枝、生成、合并或不操作；奖励同时考虑 F1 增益、漂移恢复和专家数量惩罚。

## 7. 实验设计与实验步骤

数据：使用 ISCX-VPN、ISCX-Tor、VNAT、USTC-TFC2016。论文描述中类数存在不完全一致处，例如 ISCX-VPN 同时出现 14 类和 12 类表述，ISCX-Tor 也出现 10 应用类、30 复合类和图中 16 类的差异，复现实验时必须先锁定最终 label map。

预处理：流量以 PCAP/flow/session 为单位提取包头、payload、时间间隔、长度、统计量等特征；论文描述 Transformer token 来自固定长度字节块，部分 ISCX 特征来自 flow-level 统计。

联邦划分：用 Dirichlet 非 IID 划分，论文展示 `α=0.1` 与 `α=0.5` 的客户端类别偏斜；VNAT 加入应用偏好和时间段偏好；USTC 按威胁严重度和类内 Dirichlet 继续分层。

漂移注入：每个客户端采样多个漂移事件，事件有随机起始轮次、持续时间、漂移类型集合、强度和 abrupt/gradual 模式；特征漂移加噪声或扰动，标签漂移改变类别先验，概念漂移用受控重标记或类别映射改变 `P(Y|X)`。

模型/基线：主模型是 GShard Transformer + HMoE + 熵重加权 + PPO 专家管理 + DP-SGD。基线覆盖 FS-Net、FlowPic、DeepPacket、Flow-GNN、FedETC、FedPacket、FL-ETC、BC-FLETC、FedDrift、FedCCFA、FedIBD、Cross-FCL、Master-FL、FairFedDrift、FairINC、FedStream、FedMoE-DA。

训练：论文设定 250 轮、20 客户端、每轮本地 5 epoch、batch size 32、Adam `1e-3`；模型 hidden size 512、12 层 Transformer、8 头注意力、4 个稳定专家和 4 个漂移专家；漂移窗口 `W=500`，EMA `α=0.95`；DP 裁剪 `C=1.0`，噪声 `σ=1.2`。

指标：Macro-F1 是主指标，同时报告 macro precision/recall、accuracy、少数类召回、漂移恢复分数、通信成本、运行时间、专家池变化和隐私预算。

消融/敏感性：移除 RL 专家管理、移除自适应重加权、移除漂移路由；扫描 PPO 奖励权重 `λd` 和 `µ`；扫描漂移窗口 `W` 与 EMA `α`；扫描 DP 的 `C` 与 `σ`。

结果核查：应检查表格均值方差、漂移曲线恢复轮数、PR 曲线、混淆矩阵、客户端 boxplot、公平性和专家动作密度，而不仅看最终平均 F1。

## 8. 关键结果、结论与证据

主结果显示 DAIR-FedMoE 在四个数据集上均为最佳或接近最佳。论文报告 ISCX-VPN Macro-F1 为 `96.28±0.59`，ISCX-Tor 为 `93.43±0.35`，VNAT 为 `95.76±0.41`，USTC-TFC2016 为 `98.06±0.41`。漂移恢复分数也最低，约为 11.82 到 15.38，说明恢复更快。

消融证据很强：完整模型在 ISCX-VPN 上 Macro-F1 `96.28`、少数类召回 `89.62`、恢复 12 轮；去掉 RL 后降到 `82.71/77.06/45`；去掉自适应重加权后为 `85.09/75.25/29`；去掉路由后为 `86.90/69.33/38`。这说明论文的三个模块都不是装饰性组件。

通信与资源方面，论文称 DAIR-FedMoE 平均通信成本为 FedAvg 的 `1.10×`，低于 FedDrift 的 `1.25×`；客户端模型约 3.57M 参数、15MB、峰值 RAM 1.29GB、每轮约 10.22 秒。结论是它牺牲少量计算换取漂移窗口中的稳定性和恢复速度。

## 9. 局限性与待解决问题

第一，漂移主要来自模拟器。虽然论文用随机起始、持续时间、强度和 domain randomization 增强真实性，但 feature/label/concept drift 的注入仍是人为构造，尤其概念漂移的受控重标记不一定等价于真实应用语义变化。

第二，论文正文内部存在若干复现敏感的不一致：数据集类别数、VNAT 类别口径、ISCX-Tor 类别口径、隐私预算描述均需要回 PDF、附录或官方代码进一步核对。

第三，DP 结果需要更严谨复核。正文一处称 250 轮后约 `(ε,δ)≈(5.4,10^-5)`，而隐私权衡表中默认 `(C=1.0, σ=1.2)` 对应 `ε=11.81`。这不一定表示错误，但说明 accountant 设置、采样率或表格口径没有在正文中完全统一。

第四，威胁模型偏半诚实，未充分处理恶意客户端投毒、后门、漂移伪造、专家路由操纵等主动攻击。对安全论文而言，这部分仍有拓展空间。

第五，训练设定是同步全参与 FL，现实边缘网络中的掉线、慢客户端、异步更新和数据延迟没有被充分实验化。

第六，代码包当前不能直接视为论文完整复现实验实现，见第 11 节。

## 10. 与本项目的关系

这篇论文与“异常检测”项目强相关，但它更准确地说是监督式加密流量应用/恶意流量分类，而不是纯无监督异常检测。可借鉴价值在于：把网络流量的非平稳性拆成特征漂移、概念漂移和标签漂移；把联邦隐私约束、类别不均衡和模型容量控制放在同一个框架里；用少数类召回和漂移恢复速度评价安全场景，而不是只看 accuracy。

如果本项目关注跨域异常检测或分布式安全监测，DAIR-FedMoE 可作为“漂移鲁棒联邦检测”的方法参考；但若目标是未知攻击发现，还需要加入开放集识别、OOD 检测、异常分数校准或无标签自适应机制。

## 11. 代码对照分析

数据处理对应 [dataset.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/utils/dataset.py:43) 和 [pcap_processor.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/utils/pcap_processor.py:19)。前者提供 ISCX-VPN、ISCX-Tor、CIC-IDS2017、UNSW-NB15 读取与 Dirichlet 客户端划分；后者用 EditCap/SplitCap、Scapy 提取 flow、payload、包长、IAT、协议比例等特征。

模型对应 [dair_fedmoe.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/models/dair_fedmoe.py:14)、[gshard_transformer.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/models/gshard_transformer.py:93)、[hierarchical_moe.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/models/hierarchical_moe.py:53)。代码实现了 Transformer 和两个 router 相乘的 MoE，但未看到论文中明确的 stable/drift 专家池、`[h; drift_score]` 根门控、top-1 硬路由和熵重加权训练闭环。

漂移检测对应 [drift_detector.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/drift/drift_detector.py:27)，使用 softmax 后特征分布与 reference distribution 的 JSD；这比论文中的滑动窗口 KDE、同一 encoder snapshot 重嵌入和 EMA per-sample 漂移分数要简化。

训练入口是 [examples/train.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/examples/train.py:105)，联邦训练类是 [federated_trainer.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/training/federated_trainer.py:29)。但当前代码中 RL 管理器被初始化却没有在 `train_round` 中真正执行专家 spawn/prune/merge；隐私聚合在 [privacy_mechanism.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/privacy/privacy_mechanism.py:104)。

仿真入口包括 [simulate_scheduled_drift.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/examples/simulate_scheduled_drift.py:73) 和 [federated_env.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/simulation/federated_env.py:12)。这里是固定 50/100/150/200 轮注入 feature/concept/label/combined drift，和论文后半部分强调的随机异步复合漂移不完全一致。

复现风险很高：`FederatedEnvironment` 引用 `PrivacyMechanism`，但隐私文件中实际是 `PrivacyManager`；仿真代码调用 `return_expert_indices` 和 `model.compute_loss()`，模型类没有这些接口；配置文件字段也不一致，例如模型代码使用 `expert_dim`、`ff_expansion`、`aux_loss_weight`，而 `ModelConfig` 未完整定义。图表生成脚本如 [generate_macro_f1.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/generate/generate_macro_f1.py:10) 和 [generate_cm.py](F:/泉城实验室/二期/论文/异常检测/source/DairFM/dair_fedmoe/generate/generate_cm.py:10) 主要按设定参数和随机种子生成曲线/混淆矩阵，不等同于训练评估日志。

## 12. 本篇精华

- 真正的问题不是 ETC 分类器不够强，而是联邦 ETC 在客户端异构、时间演化和类别偏斜共同作用下会发生复合漂移。
- 单一全局模型加层次化 MoE，是对多全局模型和个性化 FL 高成本的一种折中。
- 稳定专家保留旧知识，漂移专家吸收新分布，是论文最关键的结构假设。
- 熵驱动重加权把“专家不确定”转化为少数类和新兴类的训练信号。
- PPO 专家生命周期管理体现了模型容量也应随网络环境漂移而变化。
- 评价体系强调 Macro-F1、少数类召回和漂移恢复速度，比单纯 accuracy 更适合安全监测。
- 代码包展示了模块雏形和论文图表生成逻辑，但距离严格复现实验仍需修补接口、配置和数据集口径。

## 13. 建议精读路线

先读 Introduction 和 Fig. 1，抓住复合漂移为何不同于普通 non-IID。再读 Method 的 HMoE、熵重加权和 PPO 三个模块，重点看公式 5-18 与 Algorithm 1。随后读实验的 drift injection protocol，因为它决定结果是否可信。最后读消融表和隐私表，不要只看主表精度。

读代码时建议按 `utils/dataset.py`、`models/dair_fedmoe.py`、`models/hierarchical_moe.py`、`drift/drift_detector.py`、`training/federated_trainer.py`、`rl/expert_manager.py`、`privacy/privacy_mechanism.py` 的顺序走一遍，并把论文方法和源码差异单独列清。当前环境中 `python` 命令不可用，我未运行训练；上述代码判断来自静态阅读。

<!-- codex-cli-deep-read: complete -->
