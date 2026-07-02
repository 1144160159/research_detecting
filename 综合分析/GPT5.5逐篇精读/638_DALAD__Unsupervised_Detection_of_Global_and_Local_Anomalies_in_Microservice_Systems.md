# [638] DALAD: Unsupervised Detection of Global and Local Anomalies in Microservice Systems

## 1. 基本信息

题名可译为“DALAD：面向微服务系统的全局与局部异常无监督检测”。论文发表于 IEEE Transactions on Services Computing，DOI 为 `10.1109/tsc.2025.3649198`。用户元数据标注年份为 2025；正文页眉为 IEEE TSC 2026 年第 19 卷第 1 期，说明该工作在 2025 年完成录用/在线发表，正式期卷为 2026 年。

研究对象是微服务系统中的分布式 trace。已有粗分类“时序、日志、KPI 与云原生异常检测”是合理的，因为 DALAD 实际把 trace 拓扑、事件模板、变量模板、服务级 KPI、调用边 KPI 统一成图表示。

## 2. 中文翻译与核心摘要

DALAD 的核心主张是：微服务异常不只有“整体执行路径明显偏离正常模式”的全局异常，还包括“整体看起来仍像正常请求，但某个服务、局部调用或局部事件指标异常”的局部异常。多数现有方法只学习正常 trace 的全局分布，因此对局部异常不敏感。

论文提出三段式方法：先用 ADGS 从正常 trace 合成多种异常 trace；再用 DALTR 将正常 trace 与合成异常 trace 联合编码为多元高斯分布式向量；最后用 DCAD 分别拟合正常分布和异常分布，并比较一个待测 trace 在两类分布下的对数似然。若异常分布似然更高，则判为异常。

一句话概括：DALAD 把“单类正常建模”改成“正常分布 vs 合成异常分布”的概率比较，用分布式 trace 表示强化局部差异。

## 3. 论文解决的具体问题

论文针对的是微服务系统运行时异常检测中一个很具体的盲区：只看端到端请求路径或整体 trace 表示时，局部服务退化、局部调用异常、局部事件顺序异常可能仍落在正常 trace 的全局簇附近。

作者把异常分成两类：全局异常表现为完整执行模式明显偏离；局部异常则在整体模式上仍符合正常请求，但在某个服务、事件、调用边或指标上发生偏离。Fig. 1 的含义不是为了展示 t-SNE 本身，而是说明局部异常可能嵌在正常簇附近，传统“离群于正常簇”的判别会漏检。

## 4. 创新点深度提炼

第一，问题定义上强调“局部异常”。这比常见 trace anomaly detection 的“偏离正常全局模式”更细，因为微服务故障经常先体现为一个服务的响应时间、错误率、调用成功率或局部链路断裂。

第二，用合成异常构造“异常分布”。ADGS 不是简单数据增强，而是把工业微服务中的五类异常模式参数化为图扰动：事件属性扰动、服务指标扰动、调用指标扰动、执行顺序扰动、调用中断。这样在没有真实异常训练标签的场景下，也能形成正常/异常双分布学习。

第三，trace 表示不是单点向量，而是多元高斯参数向量。论文认为均值和方差信息能保留不确定性、相关性和细粒度差异；代码中实际输出为 `mu || log_var`，再在损失中转为 `sigma`。

第四，检测阶段不是单阈值重构误差或密度离群，而是比较 `log PA - log PN`。这使告警分数天然具有“更像异常分布还是正常分布”的解释。

## 5. 科学问题与研究假设

科学问题可以表述为：在真实异常稀缺、局部异常与正常全局模式高度相似的条件下，是否能通过合成异常和分布式 trace 表示提升无监督检测能力？

关键假设有四个：正常 trace 覆盖了主要请求类型；ADGS 合成的异常能近似真实微服务异常的结构和指标偏移；分布式表示比单点表示更能捕捉局部差异；GMM 足以拟合正常/异常 trace 表示的多模态分布。实验主要验证后两点，前两点仍依赖数据覆盖和扰动设计的合理性。

## 6. 科学方法与技术路线

技术路线是 `trace -> SETG -> ADGS -> HNTE -> AVAE -> GMM likelihood comparison`。

SETG 将 trace 转为服务事件图：节点是服务运行/调用事件，节点特征包含事件模板、变量模板、服务级指标；边表示调用关系，边特征包含调用类型与调用指标。HNTE 用异构节点类型变换、边类型/边属性嵌入、多头注意力聚合和图池化得到 trace 单点向量。AVAE 再把该向量映射成高斯参数表示，并通过正常 trace 与合成异常 trace 的联合损失拉开两类隐分布。DCAD 最后分别训练正常 GMM 和异常 GMM，推理时以似然差作为异常分数。

## 7. 实验设计与实验步骤

1. 数据：TT 来自 Train Ticket，45 个微服务，151911 条正常 trace、15138 条异常 trace；SN 来自 Social Network，21 个微服务，13612 条正常 trace、1106 条异常 trace。

2. 预处理：解析 trace、日志模板、变量模板、服务 KPI、服务关系 KPI；用 Drain 得到模板，用 GloVe/TF-IDF 得到事件向量；构建 SETG。

3. 模型与基线：DALAD 对比 DeepLog、LogAnomaly、TraceAnomaly、DeepTraLog、iTCRL-LOF，覆盖日志、trace、多模态和图表示方法。

4. 训练：正常 trace 按 8:1:1 划分训练/验证/测试，所有真实异常放入测试；训练时 ADGS 为正常样本随机生成异常样本；默认 `K=32, D=32, L=1, beta=1.0, lr=1e-4, lambda=1e-4`，重复 5 次取平均。

5. 指标：有效性用 Precision、Recall、F1；成本用参数量、训练时间、推理时间、训练显存、推理显存。

6. 消融/敏感性：RQ3 去掉 ADGS，改用不同比例真实异常训练；RQ4 分别扫描 GMM 组件数、嵌入维度、层数、对抗损失权重、学习率、正则系数。

7. 结果核查：重点看 F1 与 Precision 是否提升、Recall 是否牺牲、低异常覆盖下 ADGS 是否稳定、推理成本是否适合在线部署。

## 8. 关键结果、结论与证据

在 TT 和 SN 两个数据集上，DALAD 的 F1 和 Precision 均优于五个基线。论文叙述给出的提升范围是：TT 上 Precision 提升约 10.13% 到 100.36%，F1 提升约 5.03% 到 51.54%；SN 上 Precision 提升约 12.32% 到 99.96%，F1 提升约 5.37% 到 54.04%。但 Recall 不是总是最高，TT 上略低于 DeepTraLog 和 iTCRL-LOF，SN 上低于 iTCRL-LOF。

成本方面，DALAD 虽然结合 GNN、VAE 和 GMM，但推理成本较低。正文明确给出 TT 训练时间 1671.77 秒、推理时间 40.16 秒；SN 上推理显存最低，为 68 MB。作者的核心结论是训练成本集中在线下阶段，线上推理可行。

ADGS 的证据来自 RQ3：异常覆盖率低于 80% 时，DALAD 明显优于无 ADGS 变体；覆盖率很高时，真实异常训练的变体接近甚至超过 DALAD。这说明 ADGS 的价值主要在真实异常稀缺场景。

## 9. 局限性与待解决问题

第一，ADGS 生成的异常是专家设计的五类扰动，可能覆盖不了真实生产中的复杂级联故障、灰度发布问题、资源争抢和业务语义异常。

第二，论文把合成异常分布作为异常分布来学习，但真实异常空间通常开放且长尾；模型可能更擅长识别“像 ADGS 的异常”，而不是所有未知异常。

第三，实验数据来自 Train Ticket 和 Social Network，尚未接入真实生产系统。作者也承认外部有效性需要云厂商生产环境验证。

第四，正常数据覆盖不足会导致误报。若训练集中缺少某些正常业务路径，DALAD 会把它们推向异常侧。

第五，当前正文包未截断，但表格单元格没有完整展开；Table III/IV 的逐项数值仍建议回到 PDF 复核。论文叙述性结论足够支持总体判断，但不够支持逐行复算每个基线的差值。

## 10. 与本项目的关系

如果本项目关注云原生、微服务、日志/trace/KPI 联合异常检测，DALAD 相关性较高：它提供了一个可借鉴的“局部异常”建模框架，尤其适合处理整体请求路径正常但局部指标异常的场景。

如果本项目偏传统网络安全流量检测，DALAD 的直接复用性中等：它依赖分布式 trace、span、服务调用图和服务指标，不是面向五元组流、包序列或主机审计日志的通用方法。但“合成异常分布 + 正常/异常似然比较”的思想可以迁移到网络流图、会话图或主机行为图。

## 11. 代码对照分析

代码包核心入口是 [TT_execute.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/TT_execute.py:18) 和 [SN_execute.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/SN_execute.py:18)，超参数与论文默认设置一致：batch 32、epoch 10、embedding 32、层数 1、`beta=1.0`、`k=32`、学习率和权重衰减均为 `1e-4`。

数据预处理对应 [TTDataset.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/dataset/TTDataset.py:85) 与 [SNDataset.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/dataset/SNDataset.py:46)。它们读取 trace graph、log template、variable template、service KPI、relation KPI，并构造成 PyG `Data(x, variableX, ServiceX, node_type, edge_type, edge_index, edge_attr, y)`，对应论文的 SETG。

ADGS 对应 [ADGS.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/ADGS/ADGS.py:7)：`Event_masking` 对应操作异常，`Event_Metric_masking` 对应服务指标异常，`invocation_Metric_masking` 对应调用指标异常，`invocation_swap_nodes` 对应顺序/调用方向扰动，`invocation_interruption` 对应调用中断。不过代码里的中断实现更像保留随机节点的 k-hop 子图，和论文“移除下游 span 事件”的语义并不完全等价。

模型主体是 [MDAD.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/model/MDAD.py:6)。HNTE 由 [MDADEmbedding.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/model/MDADEmbedding.py:7) 和 [MDADConv.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/model/MDADConv.py:11) 实现，包含异构线性变换、边类型/边属性编码、多头注意力消息传递和注意力池化。AVAE 对应 [VAE.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/model/VAE.py:6)，代码用两个独立 VAE 分别处理正常和合成异常分支。

训练、GMM 和评估集中在 [Trianer.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/model/Trianer.py:17)。`train_GMM` 在 [Trianer.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/model/Trianer.py:160) 训练两个 `GaussianMixture`；`test` 在 [Trianer.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/model/Trianer.py:187) 用 `score_samples` 比较正常/异常似然。需要注意：代码损失在 [Trianer.py](F:/泉城实验室/二期/论文/异常检测/source/DALAD/model/Trianer.py:233) 中采用 `(正常损失+异常损失)/(beta * KL距离)` 的形式，不是直观的加性损失；这与论文公式排版所表达的形式存在实现层面的差异。

复现实用线索：README 只说明从 Zenodo 下载数据并放到主目录 [README.md](F:/泉城实验室/二期/论文/异常检测/source/DALAD/README.md:1)。本地包未包含 `OBD/` 数据目录和 `Experiments/` 输出目录，且 import 依赖 `Microservices.AnomalyDetection.DALAD` 与 `Microservices.observability.utils.log.Logger`，因此不是开箱即跑的独立仓库。当前环境只读，也无法生成 processed 数据或模型文件，所以我没有执行训练。

## 12. 本篇精华

- DALAD 的真正切入点是局部异常，而不是简单把 GNN、VAE、GMM 拼接起来。
- 它把无监督异常检测转化为“正常分布与合成异常分布的似然比较”，降低了真实异常样本稀缺的影响。
- SETG 是方法落地的关键：节点融合事件模板、变量模板、服务 KPI，边融合调用类型和调用 KPI。
- 分布式 trace 表示的价值在于表达不确定性和局部细粒度差异，适合识别正常簇附近的异常。
- ADGS 在低异常覆盖率场景贡献最大，但也带来合成异常偏置。
- 实验显示 Precision 和 F1 明显提升，但 Recall 并非全场景最优，说明模型更偏向降低误报。
- 代码实现与论文主线一致，但损失函数、调用中断实现、包路径和数据依赖需要复核后再用于严肃复现。

## 13. 建议精读路线

先读 Introduction 的 Fig. 1，抓住“全局异常 vs 局部异常”的问题设定。再读 Section III 的三段流程，重点看 ADGS 五类扰动、HNTE 的节点/边注意力聚合、AVAE 的 `mu/sigma` 表示、DCAD 的似然差判别。随后读 RQ1-RQ4，只关注 Precision/F1、低异常覆盖下 ADGS 的贡献和超参数敏感性。最后对照代码从 `dataset -> ADGS -> MDADEmbedding/MDADConv -> VAE -> Trianer` 顺一遍，就能判断论文方法是否可复现、哪里可能需要补工程脚手架。

<!-- codex-cli-deep-read: complete -->
