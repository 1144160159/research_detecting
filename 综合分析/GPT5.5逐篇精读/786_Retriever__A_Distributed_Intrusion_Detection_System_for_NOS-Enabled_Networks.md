# [786] Retriever: A Distributed Intrusion Detection System for NOS-Enabled Networks

## 1. 基本信息

- 题名：Retriever: A Distributed Intrusion Detection System for NOS-Enabled Networks
- 中文题名：Retriever：面向启用网络操作系统的网络的分布式入侵检测系统
- 年份：2025，IEEE 页面显示发表于 2025 年 11 月，当前版本为 2026 年 3/4 月刊
- DOI：10.1109/TDSC.2025.3635127
- 来源：IEEE Transactions on Dependable and Secure Computing
- 主题归类：入侵检测、网络异常检测、溯源图、APT 检测、NOS/白盒交换机安全
- 代码状态：本地未发现该论文开源代码包

## 2. 中文翻译与核心摘要

这篇论文关注一个过去主机 IDS 和流量 IDS 都没有充分覆盖的场景：云厂商越来越多地在白盒交换机上部署 Linux 化、容器化的网络操作系统，例如 SONiC。交换机不再只是黑盒转发设备，而是带有容器、CLI、Redis、路由协议进程、netlink 事件和可编程控制面的边缘计算节点。攻击者一旦进入 NOS，就可能修改 ACL、伪造邻居表、发布恶意 BGP 路由、劫持流量，甚至把交换机变成攻击基础设施。

Retriever 的核心思想是：不要把所有审计日志都传回中心，也不要只在中心看流量，而是在交换机本地做轻量事件追踪和初筛，在中心服务器做语义图分析和告警评估。它在本地用 eBPF/BCC 采集内核函数、系统调用、netlink 消息和部分 NOS 控制面事件，构建紧凑的 Subject-Object-Event Diagram，遇到训练期未出现的行为就生成可疑溯源子图并上报。中心端再用知识图谱嵌入和 GIN 图神经网络计算边级、图级异常分数，给安全分析员提供聚合后的告警和可解释子图。

论文的主张是：在白盒交换机这种资源敏感设备上，IDS 的关键不是“全量记录再分析”，而是“本地只抓关键因果事件，中心做语义评估”。实验在阿里生产/测试网络中部署到 50 多台交换机，处理 26 亿级事件，并在 DARPA TC 数据集上验证。结果显示 Retriever 在工业网络攻击场景中能达到接近 100% 的检测表现，同时本地 CPU 开销低于约 0.5%，内存约 150 MB，网络上报低于 1 KB/s。

## 3. 论文解决的具体问题

论文解决的是 NOS-enabled networks 中的边缘交换机入侵检测问题，而不是传统意义上的主机入侵检测或流量异常检测。

具体问题包括：

1. NOS 让交换机暴露出新的攻击面  
   SONiC 这类 NOS 使用容器运行 BGP、LLDP、telemetry、syncd 等组件，并通过 Redis 同步控制面配置。管理员可以 SSH、CLI 登录甚至进入容器。攻击者一旦获得权限，可以在交换机控制面制造攻击，而这些行为不一定表现为传统流量 IDS 容易识别的恶意流量。

2. 传统 IDS 不适合部署在交换机上  
   CamFlow、Linux Auditd、全量系统审计、深度日志模型都可能对 CPU、内存、磁盘、网络传输造成高负担。交换机控制面资源有限，且要保证路由计算、网络监控、管理协议和数据面配置同步，不能承受重型审计。

3. 只看系统调用不足以识别 NOS 攻击  
   交换机攻击往往涉及 netlink、ARP/邻居表、BGP 路由更新、ACL 和数据面同步。很多关键安全事件发生在内核网络栈或 NOS 控制面，而不是普通用户态 syscall 序列中。

4. 中心端面临告警过载和图数据语义稀疏问题  
   即使本地只上报可疑子图，中心仍可能收到大量来自交换机的异常报告。如何把这些子图转成可比较、可聚合、可评分的语义表示，是另一个核心问题。

5. 生产网络会持续变化  
   新业务、新容器、新路由配置、新邻居、新设备都会引入训练期未见实体。Retriever 因此加入了 human feedback 和 lifelong learning，试图缓解模型老化。

## 4. 创新点深度提炼

1. 首次把溯源图 IDS 系统化迁移到 NOS 白盒交换机场景  
   论文真正的场景创新在于把“主机溯源图 APT 检测”改造为“网络操作系统控制面入侵检测”。这不是简单换数据集，因为 NOS 的关键事件包含 netlink、路由表、ARP/BGP 更新、Redis 控制面同步和容器行为。

2. 本地 SOED 基线模型兼顾低开销和可追踪性  
   Subject-Object-Event Diagram 用分层树和查找表表示正常行为，把 subject、object、event、attribute 编码为紧凑结构。它不是端到端深度模型，而是一个适合交换机本地运行的行为白名单/基线结构。其价值在于用很少内存判断“是否见过这种主体-对象-动作-属性组合”。

3. eBPF/BCC 与 BPF table 过滤用于资源敏感采集  
   Retriever 不是全量采集审计日志，而是在内核侧用 hash table、LPM trie 等 BPF table 做过滤，减少 kernel-user 通信。这个设计直接服务于交换机可部署性。

4. 可疑子图上报，而非原始日志上报  
   本地只在异常队列触发时做前向/后向追踪，构造包含异常事件及必要良性上下文的子图。这样保留因果链，又避免把海量事件推到中心。

5. 中心端组合知识图谱嵌入与 GIN 图模型  
   TransE 类知识图谱嵌入用于把实体和关系转为语义表示，边级异常分数衡量给定头实体和关系时尾实体出现的可能性；GIN 则学习整个子图级别的异常模式。这种双层评分比纯序列日志模型更适合 APT 因果结构。

6. 把人工反馈纳入持续学习  
   论文没有把模型视为一次性训练完成，而是让分析员反馈更新知识图谱实体嵌入和 GIN 模型，处理生产网络中的新实体、新业务和概念漂移。

7. 实验包含生产网络红蓝对抗  
   相比只在 DARPA TC 上做离线评估，论文有 3 周红蓝对抗、50+ 交换机、26 亿事件、138 个攻击步骤，这让其工程可信度明显高于纯实验室 IDS 论文。

## 5. 科学问题与研究假设

核心科学问题可以概括为：

1. 在资源受限的 NOS 交换机上，能否只采集少量关键系统/网络事件，就足以发现 APT 式控制面攻击？
2. NOS 攻击是否会在 subject-object-event 级别留下与良性基线不同的因果结构？
3. 本地轻量异常筛选加中心语义图评估，是否能同时满足高检测率、低误报和低运行开销？
4. 知识图谱语义嵌入是否能提升可疑子图的异常判别能力？
5. 面对生产网络持续变化，反馈式更新是否能降低新业务引发的误报？

论文隐含和显式假设包括：

- 训练阶段存在相对干净的 attack-free network，可用于建立 SOED 正常基线。
- eBPF 子系统和采集框架本身可信，能正确提供监控保障。
- 攻击者虽然可能控制 NOS 的某些进程、容器或配置，但无法篡改 Retriever 的采集和处理完整性。
- APT 行为会导致训练期未见的事件组合、属性变化或异常因果子图。
- 红队攻击样本和 DARPA TC 攻击样本足以代表一部分实际 NOS/主机入侵行为。

这些假设里最强的是“干净训练期”和“采集框架可信”。如果生产网络初始状态已被污染，或攻击者能关闭/绕过 eBPF 采集，Retriever 的检测基础会被削弱。

## 6. 科学方法与技术路线

Retriever 的技术路线是两级架构。

本地侧部署在 NOS 交换机：

1. 事件追踪  
   通过 eBPF/BCC hook 内核函数、系统调用、tracepoint，并通过 Redis API 捕获路由表等网络控制面变化。采集对象包括进程、文件、网络连接、路由/邻居表等。

2. 内核侧过滤  
   使用 BPF table 做精确匹配和 IP 前缀匹配，把无关事件尽量挡在内核侧，减少上报和用户态分析开销。

3. SOED 基线建模  
   将正常阶段事件编码为 subject-object-event-attribute 分层结构。subject 包含进程 ID、可执行路径 hash、用户、cgroup、时间戳等；object 包含对象类型、名称、owner、tag；event 用紧凑字节编码表示系统调用或网络事件。

4. 异常匹配  
   新事件到来时，与 SOED 中已有主体、对象、事件、属性组合比较。不匹配则标记为 suspicious。

5. 可疑子图生成  
   从异常事件出发做前向和后向追踪，选取必要上下文节点和边，合并连续同类事件，避免无限膨胀。异常队列通过 decay 参数控制重复异常聚合和遗忘。

中心侧部署在服务器/集群：

1. 子图语义抽取  
   将可疑子图拆成三元组 `<head, relation, tail>`，使用 TransE 类知识图谱嵌入学习实体与关系表示。

2. 边级异常评分  
   给定头实体和关系，预测尾实体出现概率，概率越低，边级异常越高。

3. 图级异常评分  
   将子图转为带表示的图，输入 GIN，输出图级异常分数。监督设置中使用正常子图和红队恶意子图；无监督设置中可用聚类。

4. 告警聚合与解释  
   用 GIN 的图嵌入聚类相似告警，减少分析员工作量，并把高分子图翻译成人类可读描述。

5. 持续学习  
   对新实体使用归纳式知识图谱嵌入，对 GIN 使用带正则的微调，减少灾难性遗忘。

## 7. 实验设计与实验步骤

可复核流程如下。

1. 数据准备  
   - 私有云数据：50+ 白盒交换机，3 周红蓝对抗，约 26 亿系统与网络事件，357 GB 数据，10 次攻击、138 个攻击步骤。
   - 公共数据：DARPA Transparent Computing Engagement 5，选用 THEIA 和 CADETS 两个主机审计数据集。
   - 攻击标签：根据红队记录或 DARPA ground truth，用时间戳、host ID、session ID、命令行、IP、端口、方向等信息标注攻击事件。

2. 预处理  
   - 私有云：由于生产环境不能全量长期审计，论文采集一台设备两天日志用于训练，并保留攻击期间受害设备的原始日志和子图用于离线比较。
   - DARPA：转换为 Common Data Format；使用前两天数据训练基线和知识图谱；过滤高频文件读写事件，约过滤 70%，模拟 Retriever 不上报这些低价值事件。
   - 本地 SOED：用无攻击阶段事件构建正常 subject-object-event-attribute 基线。

3. 模型与基线  
   - Retriever 本地：SOED 匹配式异常检测，可疑子图生成。
   - Retriever 中心：知识图谱嵌入 + 边级异常评分 + GIN 图级异常评分。
   - 对比方法：DeepLog、DeepCase、Unicorn。
   - DeepLog/DeepCase 使用 Drain 解析后的日志事件 ID 进行序列建模。
   - Unicorn 使用运行时溯源图检测 APT，是最接近 Retriever 的主机溯源图基线。

4. 训练流程  
   - 用前两天正常数据训练 SOED、知识图谱表示和 GIN/聚类模型。
   - 私有云红队攻击子图可用于监督 GIN；无监督设置下通过特征距离输出异常评估。
   - DARPA THEIA/CADETS 用前两天作为训练，后续天数作为测试。

5. 检测流程  
   - 本地匹配新事件是否出现在 SOED。
   - 不匹配事件进入异常队列。
   - 按报告间隔或队列容量触发子图构造。
   - 中心计算边级和图级异常分数。
   - 超阈值告警与 ground truth 子图匹配，判定 TP/FP/FN/TN。

6. 评价指标  
   - 成本指标：CPU、内存、网络传输开销。
   - 检测指标：precision、recall、accuracy、F1-score。
   - true positive 定义为最终检测子图中包含 ground truth 攻击事件。
   - false positive 定义为不含攻击事件但被判为异常的子图。

7. 消融与敏感性分析  
   - BPF safelist/filtering：比较无过滤、过滤项增加时 CPU、网络与检测表现。
   - 报告间隔：观察 30 秒、1 分钟、10 分钟等设置对报告数量、实时性和精度的影响。
   - decay 参数：比较 0.1、0.5、1、2、7 天遗忘周期对误报和漏报的影响。
   - 子图 branch size：分析上下文节点数量过少或过多对 GIN 的影响。
   - search depth：分析前后向追踪深度对召回率的影响。
   - 知识图谱数据比例：用 0%、25%、50%、75% 等比例验证语义知识对检测精度的贡献。
   - lifelong learning：引入业务变化和未见实体，比较更新前后的 precision/recall。

8. 结果核查  
   - 私有云中 Retriever 达到接近 100% 的检测表现，且能覆盖网络设备特有攻击。
   - DARPA 中 Retriever 与 Unicorn 接近，明显优于 DeepLog/DeepCase 的误报表现。
   - 本地开销符合交换机部署要求：事件追踪 CPU 低于约 0.5%，内存约 150 MB，网络上报平均约 0.24 KB/s，低于论文摘要中的 1 KB/s 描述。

## 8. 关键结果、结论与证据

1. Retriever 在工业 NOS 场景中检测效果显著优于日志序列模型  
   DeepLog 和 DeepCase 在私有云中能有较高召回，但 precision 很低，意味着会制造大量误报。论文认为直接在 raw logs 或事件 ID 序列上建模不足以处理工业网络中的复杂行为。

2. Retriever 能检测 NOS 特有攻击  
   ARP spoofing 场景中，传统 syscall tracing 不容易看到内核邻居状态变化，但 Retriever 通过 netlink 和邻居表更新识别同一 IP 对应不同 MAC 的异常属性。Traffic hijacking 场景中，Retriever 能把恶意路由规则、BGP 更新和后续路由表变化连成子图，帮助定位根因。

3. 本地开销足够低  
   eBPF + BPF table 过滤比 Linux Auditd 更适合交换机。论文报告 Retriever 本地 CPU 低于约 0.5%，内存约 150 MB。无 BPF 过滤时 CPU 和网络开销分别增加约 150% 和 800%，说明内核侧过滤不是优化细节，而是系统可部署性的关键。

4. 子图上下文存在最佳范围  
   branch size 太小会缺少攻击上下文，太大会引入太多正常节点，干扰 GIN 判断。论文最终选择 branch size 约 10。search depth 超过 5 后收益趋于饱和，说明多数攻击因果链在这个范围内可覆盖。

5. 知识图谱提高 precision  
   消融显示语义知识主要提升威胁检测精度。没有知识图谱数据时，私有云场景甚至无法把样本正确分类为攻击，说明实体/关系语义对 NOS 攻击判断很重要。

6. lifelong learning 能缓解生产变化造成的误报  
   引入未见实体和事件后，precision 会明显下降；经过新实体嵌入和模型再训练后，precision 和 recall 均恢复。论文给出的私有云结果显示 precision 从 75.00% 提升到 84.62%，recall 从 56.25% 提升到 100.00%。

7. DARPA 上的表现证明方法不只适用于 NOS  
   在 THEIA 和 CADETS 主机数据上，Retriever 达到与 Unicorn 接近的高准确率，说明它的图异常检测机制具有一定跨场景泛化能力。不过它的真正价值仍在 NOS 场景。

## 9. 局限性与待解决问题

1. 训练期干净假设较强  
   SOED 基线依赖 attack-free network。如果训练阶段已经存在潜伏攻击、异常配置或业务灰色行为，基线会被污染，后续检测可能漏报。

2. 对采集完整性有信任假设  
   论文假设 eBPF 和 Retriever 采集框架可信。但现实中，获得 root 权限的攻击者可能尝试关闭探针、篡改上报、攻击 sidecar 容器或利用内核漏洞绕过监控。

3. 对资源耗尽类攻击覆盖不足  
   论文明确指出 DDoS 等资源耗尽攻击不在主要范围内，因为这类攻击未必产生恶意行为因果链。未来需要结合 CPU、内存、网络、FPGA 等可观测指标。

4. 自适应规避仍是问题  
   攻击者若了解 SOED、branch size、search depth 或 GIN 的行为，可能把攻击链拆散、模仿良性命令、延迟执行或制造大量正常上下文稀释异常信号。

5. 中心模型细节仍不够完全可复现  
   论文说明使用私有云机器学习平台模块，未给出完整实现代码、模型超参数和训练细节。尤其是 GIN 结构、阈值选择、聚类半径、负采样策略等，复现实验需要更多工程细节。

6. 私有云数据不可公开验证  
   最有价值的 NOS 攻击数据来自生产/测试网络红蓝对抗，但外部研究者难以获取。DARPA 数据只能验证主机 APT 检测，不能完全复核 NOS 攻击检测结论。

7. 与联邦学习/隐私保护关系有限  
   虽然元数据中二级关联到“联邦学习、隐私保护与分布式协同”，但论文方法本身不是联邦学习。它是分布式采集、中心化分析，隐私保护不是主要贡献。

8. 正文包未截断  
   本次正文包显示未截断，因此上述理解基于完整提供文本；但图 1、图 5、表格中的视觉细节仍建议回到 PDF 原图复核。

## 10. 与本项目的关系

如果本项目关注“异常检测、入侵检测、分布式协同、工业/云网络安全”，这篇论文强相关，尤其适合作为以下方向的参考：

1. 面向网络设备控制面的异常检测  
   它把检测对象从服务器、终端、IoT 流量扩展到 NOS 白盒交换机，适合补充综述中“边缘网络基础设施安全”的空白。

2. 溯源图在资源受限环境中的轻量化  
   论文不是盲目套 GNN，而是先用 SOED 本地基线压缩事件空间，再把子图交给中心分析。这对实际部署有启发。

3. 系统安全与网络控制面结合  
   它证明 NOS 攻击不是单纯系统入侵，也不是单纯网络流量异常，而是系统行为、控制面状态和网络协议传播共同构成的因果问题。

4. 可作为“联邦/分布式异常检测”对照案例  
   Retriever 是边缘本地筛选 + 中心融合评估，不是模型参数联邦聚合。若本项目做联邦 IDS，可把它作为集中式协同架构的强基线。

5. 可借鉴实验设计  
   红蓝对抗、真实交换机、DARPA 迁移评估、开销评估、参数敏感性和 lifelong learning，是一套较完整的系统型 IDS 论文实验范式。

## 11. 代码对照分析

本地未发现该论文对应开源代码包，因此不能给出真实源码文件路径。但论文提供了较清楚的实现线索，可推断如果复现，代码应分为以下模块。

1. 数据采集与追踪模块  
   论文线索：BCC kernel code 2K+ 行，hook kernel functions、syscall、tracepoint，结合 Redis API 追踪 routing table 变化。  
   可能对应文件：
   - `collector/bcc/*.c` 或 `ebpf/*.c`：BPF probe、tracepoint、kprobe/uprobe 程序
   - `collector/syscall_tracer.py`：系统调用事件封装
   - `collector/netlink_tracer.py`：netlink/邻居表/路由更新采集
   - `collector/redis_tracer.py`：SONiC Redis DB 变化读取
   - `collector/bpf_filter.py`：BPF table safelist、hash/LPM trie 配置

2. 本地 SOED 与异常队列模块  
   论文线索：本地处理约 7.5K 行 Python，负责 SOED、事件编码、匹配、缓存、剪枝。  
   可能对应文件：
   - `local/soed.py`：Subject-Object-Event Diagram 构建和查询
   - `local/event_encoder.py`：subject/object/event 紧凑编码
   - `local/anomaly_queue.py`：异常队列、decay、报告触发
   - `local/provenance_graph.py`：本地溯源图维护
   - `local/pruning.py`：良性节点/边周期剪枝

3. 可疑子图生成模块  
   论文算法 1 对应前向/后向追踪。  
   可能对应文件：
   - `local/subgraph_builder.py`：`getNextEvent`、`getPreviousEvent`、search depth、branch size
   - `local/report_serializer.py`：子图压缩、语义属性保留、gRPC 上报格式

4. 通信与日志平台模块  
   论文线索：本地通过 gRPC tunnel 上报到 Kafka-like log service。  
   可能对应文件：
   - `proto/retriever.proto`
   - `local/grpc_client.py`
   - `server/grpc_receiver.py`
   - `server/log_ingest.py`

5. 中心知识图谱模块  
   论文线索：TransE、负采样、实体/事件语义表示。  
   可能对应文件：
   - `central/kg_dataset.py`
   - `central/transe_model.py`
   - `central/negative_sampling.py`
   - `central/edge_anomaly_score.py`

6. 中心 GIN 与告警模块  
   论文线索：GIN 图级异常分数、embedding clustering、ATT&CK 技术匹配、人工反馈。  
   可能对应文件：
   - `central/gin_model.py`
   - `central/graph_dataset.py`
   - `central/train_gin.py`
   - `central/score_subgraph.py`
   - `central/alert_cluster.py`
   - `central/feedback_update.py`
   - `central/lifelong_learning.py`

7. 评估脚本  
   论文线索：私有云 ground truth、DARPA CDF 转换、DeepLog/DeepCase/Unicorn 对比、参数敏感性。  
   可能对应文件：
   - `experiments/label_ground_truth.py`
   - `experiments/convert_darpa_tc.py`
   - `experiments/run_baselines.py`
   - `experiments/evaluate_metrics.py`
   - `experiments/ablation_report_interval.py`
   - `experiments/ablation_kg_ratio.py`

运行线索上，复现系统至少需要 Linux 内核 eBPF 支持、BCC、root/特权容器、SONiC 或类似 NOS 环境、Redis/SONiC DB 访问权限、gRPC 服务、中心 PyTorch/PyG 或 DGL 图学习环境。由于没有代码包，不能确认依赖版本、命令行入口和数据格式。

## 12. 本篇精华

1. Retriever 的核心贡献不是又一个 GNN IDS，而是把 IDS 部署对象推进到 NOS 白盒交换机，并围绕交换机资源约束重写了采集、过滤、建图和上报逻辑。

2. NOS 攻击的关键证据常在 netlink、邻居表、路由表、BGP 更新和控制面同步中；只看 syscall 或只看 TCP/UDP 流量都会漏掉一部分根因链。

3. SOED 是论文工程落地的关键：用紧凑 subject-object-event-attribute 基线在本地快速识别未见行为，避免全量日志上传。

4. 可疑子图比原始日志更适合作为中心分析对象，因为它保留了攻击因果上下文，同时把数据量压到交换机能承受的范围。

5. 中心端的知识图谱嵌入解决“实体和关系语义”问题，GIN 解决“整体子图结构”问题，两者分别对应边级和图级异常评分。

6. 实验最有说服力的是 50+ 交换机、3 周红蓝对抗、26 亿事件的生产/测试网络部署，证明系统不是只在离线数据集上成立。

7. Retriever 与联邦学习不同：它是分布式本地检测与中心化评估架构，适合作为分布式 IDS 的工程基线，而不是隐私保护训练方法。

8. 最大风险在于干净训练期、采集可信和自适应规避；这些问题决定了 Retriever 后续能否从“强工程原型”走向更强鲁棒性的安全系统。

## 13. 建议精读路线

1. 先读 Introduction 和 Background  
   把 NOS/SONiC 的安全问题读清楚，尤其是为什么交换机控制面会成为 APT 入口。

2. 重点读 Threat Model  
   关注攻击者能力、Retriever 的检测目标和采集完整性假设。这决定论文结论的适用边界。

3. 精读 Local Anomaly Detection  
   这是论文最核心的系统设计部分。建议画出事件从 eBPF 采集、BPF table 过滤、SOED 匹配、异常队列到子图上报的流程图。

4. 精读 Central Anomaly Assessment  
   重点理解 TransE 负责什么、GIN 负责什么、边级分数和图级分数如何互补。

5. 对照读 Case Study  
   ARP spoofing 和 traffic hijacking 是理解 NOS 场景价值的入口。建议把两个案例拆成“攻击动作、系统事件、网络事件、Retriever 证据链”。

6. 最后读 Evaluation  
   优先看 Table II、Table III、Table IV、Fig. 7、Fig. 8、Table V、Table VI，理解检测性能、系统开销和关键参数敏感性。

7. 做综述引用时  
   建议把它放在“provenance-based IDS in network infrastructure”或“NOS-enabled programmable network security”小节，而不是简单归入普通主机 IDS 或联邦入侵检测。

<!-- codex-cli-deep-read: complete -->
