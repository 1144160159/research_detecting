# [683] FedScope—Federated Host Embeddings From Telescope Traffic: Design and Implementation

## 1. 基本信息

2026 年 IEEE TNSM 论文，DOI `10.1109/TNSM.2026.3685756`。主题是把多个 network telescope/darknet 观测到的恶意扫描流量，通过联邦学习训练成 sender/host embedding，而不共享原始包数据。正文包完整，未截断。代码仓库已下载到 `source\fedscope`。

## 2. 中文翻译与核心摘要

论文核心意思是：单个网络望远镜只能看到恶意扫描活动的一部分，受 IP 段大小和地理/网络位置影响很大；把多个望远镜合起来能提升可见性，但原始流量共享成本高，也有组织策略和隐私顾虑。FedScope 的做法不是共享流量，而是让各方本地把“源 IP 访问端口序列”训练成 host embedding，再通过联邦学习合成全局模型。它继承 i-DarkVec/Word2Vec 思路，把发送方 IP 当作“词”，把同一时间窗口、同一服务上的到达序列当作“句子”，使行为相近或协同活动的主机在嵌入空间里靠近。

论文的关键结论是：FedScope 生成的 embedding 在分类和聚类下游任务中接近集中式训练，优于单点本地训练；它还能扩大可覆盖的 sender 集合；词表同步与淘汰机制让动态 IP 词表在资源受限环境中可控。

## 3. 论文解决的具体问题

它解决的不是一般入侵检测分类问题，而是“多组织、多望远镜场景下如何共同学习恶意主机行为表示”。困难有三层：第一，单点望远镜视野有限，小望远镜尤其容易看不到低频或分散扫描者；第二，原始 telescope traffic 体量大，且可能暴露观测基础设施、payload、目标网络策略等敏感信息；第三，Word2Vec 式 embedding 模型的输入/输出神经元绑定词表，而每个望远镜看到的 IP 集合不同、每天还在变化，这打破了传统 FL 默认的固定模型结构。

## 4. 创新点深度提炼

最重要的创新是把联邦学习用于“自监督主机表示学习”，而不是训练一个特定攻击类别的监督检测器。FedScope 学到的是可迁移 embedding，可服务分类、聚类、异常发现等多个下游任务。

第二个创新是词表同步阶段：在普通 FedAvg 训练前，客户端先上报本地 sender 及兴趣统计，服务端生成统一全局词表，并据此调整 Word2Vec 模型结构。这直接回应了“不同客户端词表不一致”的核心工程障碍。

第三个创新是 IP 淘汰策略。论文用历史兴趣的指数滑动平均和当前包数、目标端口数构造兴趣分数，在全局词表超过上限 `M` 时保留最有价值的 sender。这个机制把“安全可见性”和“内存/通信成本”放在同一设计里权衡。

第四个贡献是评价维度较完整：不仅比较 local、centralised、federated 三种学习范式，还分别看分类 F1、覆盖率、聚类 silhouette、内存、通信和时间开销。

## 5. 科学问题与研究假设

论文的三个研究问题可以概括为：共享望远镜信息是否能学到更好的主机活动模式；这种收益如何在大/小望远镜之间分配；动态、异构词表下 FL 是否可行。

背后的假设是：恶意扫描和僵尸网络活动具有跨观测点的协同性，不同望远镜看到的是同一全局行为过程的局部投影；如果把这些局部投影合并，embedding 空间会更稳定、更可分。另一个假设是，近期活跃、包量大、触达端口多的 sender 对安全分析更有价值，因此可用兴趣分数近似控制词表淘汰而不显著损害下游效果。

## 6. 科学方法与技术路线

技术路线是“包级观测 → 序列语料 → 自监督 embedding → 联邦聚合 → 下游验证”。客户端从每个时间窗口中提取源 IP、目的端口、协议和包量，按小时与服务构造 IP 序列；Word2Vec/Skip-gram 学习源 IP 的向量表示。联邦流程分两阶段：先做 vocabulary synchronisation，服务端合并 sender 与兴趣统计，生成全局词表并初始化/裁剪 embedding 矩阵；再做 model training，各客户端用本地语料训练统一架构模型，服务端用 FedAvg 聚合。

概念上，论文写的是对共同 sender 的 embedding 做加权平均，默认权重与本地词表规模相关；附录还比较了按 host 包量和均匀权重，结论是权重方案对最终 F1 影响不大，能大致反映望远镜相对贡献即可。

## 7. 实验设计与实验步骤

1. **数据**：2021 年两个月真实 telescope 数据，包含一个校园 /24 和一个巴西 /19；嵌入质量实验主要用 2021-05-01 至 2021-05-31，资源实验用两个月。另有 2025 年 10 月的 7 个分布式 telescope 数据，用于多参与方实验。

2. **预处理**：按天处理，过滤每天包数不足的 sender；将 `src_ip` 作为词，将端口/协议合成服务，将同一小时、同一服务的 IP 到达序列作为句子。

3. **模型/基线**：比较 local i-DarkVec、集中式 raw-data 训练、FedScope/FL 三类表示学习方式。下游分类用 7-NN，聚类用 kNN 图加 Louvain。

4. **训练**：论文主实验保持 i-DarkVec 参数，日批次增量训练，每天 1 epoch，embedding 维度 `E=200`，主要对照实验关闭淘汰策略，即 `M=∞`。

5. **指标**：分类看 per-class 与宏平均 F1；覆盖率看能生成 embedding 并进入下游任务的 sender 数；聚类看 silhouette；系统实验看内存、模型大小、网络开销和每轮耗时。

6. **消融/敏感性**：改变第二个 telescope 的大小 `/20` 到 `/28`；改变参与 telescope 数量；改变淘汰上限 `M=40k..100k` 和 `β=0.01..0.99`；附录比较不同聚合权重。

7. **结果核查**：不仅比较平均 F1，还检查小样本类别如 Shodan、Internap、Driftnet 的收益；同时核查覆盖率是否提升，避免只看已覆盖 sender 的性能。

## 8. 关键结果、结论与证据

两个同等 /24 telescope 协作时，local 平均 F1 分别约为 0.86 和 0.83，而 centralised 与 FL 均达到约 0.89 以上；Driftnet、Internap 等类别提升尤其明显。覆盖率上，协作让两个 telescope 分别多覆盖约 14.77% 和 12.25% sender，约一万级新增可分类主机。

大小不对称时，小 telescope 收益最大。极小的 `/27` 或 `/28` 借助 /24 伙伴可获得超过 30% 的 F1 增益；覆盖率最高可提升到 123%。大 telescope 的主要收益不是 F1，而是补充少量视野。

多 telescope 实验显示，`/24`、`/25`、`/26` 级别参与方能通过协作提高模型质量，例如 `/26` 可从约 0.64 提升到 0.77；但 `/28` 太小，单独贡献的信号不足，多方相加也难以形成强模型。

系统层面，淘汰策略使模型和内存增长可控。`M=100000` 时模型最大约 160 MB，而不限制时约 340 MB；客户端内存稳定在 3 GB 以下，服务端不超过约 4 GB。词表同步额外通信开销小于 1.4%，训练时间约 98% 花在模型训练阶段。

聚类任务也验证 embedding 空间被改善。已知 scanner 群体如 ShadowServer、Censys 的 cluster silhouette 分别平均提升约 8% 和 13%；某个 Censys cluster 从 0.40 提升到 0.71，并剔除了一个误入的 unknown sender。

## 9. 局限性与待解决问题

隐私并未被完全解决。FedScope 不共享 raw packet、payload、目的 IP，但仍共享 sender 标识和兴趣统计，也共享模型参数；论文把模型泄漏、成员推断、反演攻击和安全聚合/差分隐私作为未来方向，而不是已解决问题。

评估标签有限。ground truth 主要来自 Mirai-like 指纹和公开 acknowledged scanner 列表，Unknown 类无法验证，因此聚类中“未知协同行为”的解释仍需要人工或外部情报确认。

工程部署仍偏原型。论文说明当前 Flower 原型能容忍临时掉线，但动态加入客户端仍受框架编排限制。真实跨组织部署还需要身份认证、密钥管理、审计、失败恢复和长期运行策略。

本次正文包未截断；不过本地抽取文本存在少量编码噪声，表格和图中文字若用于精确引用，仍建议回 PDF 复核。

## 10. 与本项目的关系

对“异常检测”项目属于中高相关。它不是直接做企业内网 IDS 分类，而是提供一种适合弱标签场景的上游表示学习框架：把 host 行为压缩为 embedding，再用于分类、聚类、异常发现和新型协同扫描追踪。

如果本项目有多个观测点、多个园区或多租户日志源，FedScope 的价值很直接：可在不集中原始流量的情况下联合学习表示。若只有单点生产网流量，也可以借鉴其“源实体-服务-时间序列”的自监督建模方式，但需要重新定义语料、敏感字段和淘汰策略。

## 11. 代码对照分析

代码主入口是 [client.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/client.py:25>) 和 [server.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/server.py:34>)。客户端 `DarkVecClient` 负责读取某天数据、生成 proposal、过滤语料并训练本地模型；服务端负责收集 proposal、计算兴趣分数、更新词表和模型架构，然后调用自定义 Flower 策略训练。

数据预处理对应 [src/preprocess.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/src/preprocess.py:24>)：读取 `ts/src_ip/dst_port/proto`，把协议号转成 `tcp/udp/icmp/oth`，合成 `port/proto`。语料构造在 [src/corpus.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/src/corpus.py:63>)，按小时和 top ports 服务分组生成 IP 序列。

模型在 [src/word2vec_torch.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/src/word2vec_torch.py:6>)，包含输入/输出 embedding，并用 `update_with_removal` 支持词表裁剪后的参数迁移。训练样本和负采样在 [src/data_generation.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/src/data_generation.py:13>)，训练循环在 [src/SGNSTrainer.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/src/SGNSTrainer.py:18>)。

联邦改造主要在 [flwr/server/server.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/flwr/server/server.py:130>) 和 [architecture_update_fedavg.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/flwr/server/strategy/architecture_update_fedavg.py:52>)：每轮先 `proposals_request`，再 `compute_new_architecture`，最后 `architecture_fit_round`。兴趣分数实现在 [src/interest.py](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/src/interest.py:21>)。

需要注意几处复现差异：论文主实验写 `E=200`，但代码默认 `word2vec_e=50`；README 要求手动替换 pip 安装的 `flwr`；[docker/compose.yaml](<F:/泉城实验室/二期/论文/异常检测/source/fedscope/docker/compose.yaml:1>) 的 server 参数与当前 `server.py` 不匹配，含 `--round` 和异常的 `--beta 800`；代码包没有完整下游 kNN/Louvain 评估脚本，主要是 FedScope 训练系统原型。

## 12. 本篇精华

- FedScope 的核心不是“联邦分类器”，而是“联邦自监督 host embedding”，更适合弱标签安全监测。
- 多 telescope 协作同时提升 embedding 质量和 sender 覆盖率；小望远镜收益最大。
- 最大技术障碍是动态、不一致 IP 词表导致模型架构变化，论文用词表同步阶段解决。
- IP 淘汰策略是系统可落地的关键，否则模型随新 sender 持续增长。
- FL 性能接近集中式训练，但避免共享 raw telescope traffic。
- 下游聚类结果说明全局 embedding 不只改善已知类别，也有助于发现未知协同行为。
- 代码实现是可运行原型，但实验复现还需要数据集、参数校准和额外评估脚本。

## 13. 建议精读路线

先读 Section II 理解 i-DarkVec 如何把 telescope traffic 转成 host embedding；再读 Figure 1-3 和 Section III-IV，把“词表同步 + 模型训练”两阶段流程画出来。随后重点读 Table II、Figure 4-6，理解协作收益和大小不对称；再读 Figure 7-9，看淘汰策略和资源成本。最后读 Section VII 聚类实验和 Appendix 权重方案，判断该方法是否适合你的异常检测综述或多点协同监测方案。