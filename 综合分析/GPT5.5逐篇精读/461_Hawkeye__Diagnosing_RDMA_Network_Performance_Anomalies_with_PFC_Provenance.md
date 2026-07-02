# [461] Hawkeye: Diagnosing RDMA Network Performance Anomalies with PFC Provenance

## 1. 基本信息

论文发表于 ACM SIGCOMM 2025，题名可译为“基于 PFC 溯源诊断 RDMA 网络性能异常的 Hawkeye”。DOI 为 `10.1145/3718958.3750490`。正文包完整，未截断。代码仓库为 `wangshicheng1225/Hawkeye`，本地目录是 `source/Hawkeye`。

这篇文章与“图学习”关系并不强，更准确地说是“网络遥测 + 因果溯源图 + 规则签名诊断”。它面向 RDMA/RoCEv2 数据中心中的性能异常诊断，安全相关点主要在 LoRDMA、PFC 注入、租户间隐蔽性能干扰等场景。

## 2. 中文翻译与核心摘要

Hawkeye 关注的问题不是简单检测“链路拥塞”，而是当某条 RDMA 流出现 RTT、吞吐或完成时间退化时，回答：它是被本地队列竞争影响，还是被远端 PFC 回压间接影响？PFC 从哪里开始传播？根因是突发流、负载不均衡、PFC 注入主机，还是形成了死锁？

论文提出三层机制：细粒度 PFC 感知遥测、数据面内 PFC 因果追踪、基于异构 provenance graph 的诊断算法。核心结果是：在 NS-3 和 Tofino 原型上，对代表性 RDMA NPA 能达到超过 90% precision、接近 100% recall，并比全网遥测、NetSight 一类方法低 1 到 4 个数量级开销。

## 3. 论文解决的具体问题

RDMA 为了无损传输依赖 PFC，但 PFC 是逐跳暂停机制，一旦下游端口拥塞，会把阻塞向上游传播。这样，受害流可能根本不经过初始拥塞点，也不和根因流共享同一个队列。传统“看受害流路径上的队列竞争”的方法会把局部同队列流误判为根因。

论文具体覆盖五类诊断对象：由 incast/micro-burst/负载不均衡触发的 PFC backpressure；由主机持续 PFC 注入触发的 PFC storm；由环形缓冲依赖形成的 initiator-in-loop deadlock；由环外 PFC 注入或环外竞争触发的 initiator-out-of-loop deadlock；以及退化为普通队列竞争的传统拥塞。

## 4. 创新点深度提炼

第一，Hawkeye 把“PFC 对每条流的影响”变成一等遥测对象，而不是只看端口是否暂停。每流记录 packet count、queue depth、paused packet count，每端口记录 queue depth、paused packet count。

第二，它用端口对端口的 traffic meter 表示 PFC 传播因果强度。一个端口被暂停，并不意味着所有下游暂停端口都相关；只有存在从该端口到下游端口的流量，才构成可解释的等待关系。

第三，polling packet 不是普通探针，而是携带 victim flow 和 tracing flag 的诊断触发器：沿受害流路径走，遇到 PFC 后再沿 PFC 因果路径扩展，避免全网拉取遥测。

第四，诊断算法不是流交互图的简单扩展，而是异构 wait-for provenance graph：`flow -> port` 表示流被端口 PFC 暂停，`port -> port` 表示 PFC 传播等待关系，`port -> flow` 表示本地队列竞争贡献。

## 5. 科学问题与研究假设

科学问题是：在 PFC 造成的跨跳级联拥塞中，能否只收集因果相关交换机的遥测，就恢复足够完整的异常传播链和根因？

主要假设包括：受害端主机能通过 RTT 等端到端指标触发诊断；短 epoch 内的 PFC、队列和流量统计足以表达因果邻接；端口间流量计数与下游队列积压可以近似 PFC 传播贡献；代表性 RDMA NPA 可以用图结构签名区分，例如路径终点有无正向 port-flow 贡献、port-level graph 是否存在环。

## 6. 科学方法与技术路线

技术路线是“触发式诊断”，不是持续全量采集。主机 agent 发现 RTT 超阈值后发送 polling packet；交换机数据面根据 victim flow 转发，并在 egress 侧读取 paused count 和 port meter 判断是否继续沿 PFC 路径传播；交换机 CPU 收到镜像 polling packet 后批量读取寄存器并上报。

离线 analyzer 用 telemetry 构图。port-level 边权把上游 paused packet 数、端口间 meter 比例、下游平均 queue depth 合成；flow-port 边权是该流被 PFC 暂停的包数；port-flow 边权来自队列 replay 后的净等待贡献，正权重是贡献者，负权重更像受害者。

## 7. 实验设计与实验步骤

数据：NS-3 中使用工业 RoCEv2 长尾流量分布，构造 100 组不同负载 trace；异常通过同步短突发、主机 PFC 注入、路由错误/环形依赖注入。硬件侧用 Tofino 切成两个逻辑交换机，连接两台 Dell 服务器。

预处理：交换机按 epoch 记录 flow/port telemetry，CPU 或仿真输出后转换为 provenance graph；代码中的 `simulation/mix/data/graph.py` 负责把 telemetry 文本整理为 `telemetry.json`。

模型/基线：Hawkeye 对比 SpiderMon、NetSight、full polling、victim-only polling；另做 port-only telemetry 与 flow-only telemetry 对照。

训练：没有机器学习训练过程，核心是参数扫描与规则签名匹配；参数包括 RTT detection threshold 和 epoch size。

指标：precision、recall、telemetry processing size、monitoring bandwidth overhead、采集交换机数量、causal switch coverage、Tofino 资源占用、CPU polling 时间。

消融/敏感性：epoch 从 100 us 到 2 ms，阈值从 200% 到 500% RTT；比较 2/4 epoch、flow-only/port-only telemetry、victim-only/full-polling。

结果核查：论文定义 true positive 必须同时识别异常类型和根因流/主机；case study 通过四类 provenance graph 检查路径、环、根因端口和贡献流是否吻合。

## 8. 关键结果、结论与证据

Hawkeye 在合适 epoch 和阈值下可达到 100% precision/recall；epoch 过大会把相邻事件错误关联，尤其影响瞬时 burst 的根因定位。相较 full polling，Hawkeye 精度接近但采集规模小得多；相较 victim-only，Hawkeye 对 deadlock 明显更稳，因为死锁环通常不完全落在单条受害流路径上。

SpiderMon、NetSight 这类传统方法在普通队列竞争上有效，但缺少 PFC 可见性，无法解释 PFC backpressure、storm、deadlock 的跨路径根因。硬件评估显示 Tofino 资源可承载；CPU 读取 2/4 epoch 约需 80/120 ms；CPU 过滤零值与批量打包可使 telemetry 大小减少 80% 以上、上报包数减少约 95%。

## 9. 局限性与待解决问题

论文承认覆盖的是代表性 NPA，不是完整 RDMA 异常空间；签名规则需要人工扩展，尚不是通用因果推理器。partial deployment 会削弱诊断，因为 PFC 路径在非 Hawkeye 交换机处中断。参数也依赖网络规模、RTT 基线和应用敏感度。

另一个现实限制是主机触发：如果 host agent 未覆盖、阈值过高或异常没有显著反映到 RTT，诊断不会启动。Tofino 原型还需要修改 `rxconfig` 让 PFC frame 进入 P4 pipeline，这说明商用交换机的 PFC 可见性接口会直接影响部署难度。正文包未截断；但若用于正式复现，仍建议回 PDF 核对图 7-14 的具体数值刻度。

## 10. 与本项目的关系

若本项目聚焦“网络异常检测”，这篇文章的价值在于根因诊断范式：从“判定异常”提升到“解释传播链和根因实体”。它适合放在网络性能异常、云数据中心 RDMA、可编程交换机遥测、因果图诊断一类综述中。

若本项目偏安全威胁情报或图学习，它的相关性中等：没有 GNN，也没有威胁情报知识图谱；但 LoRDMA、PFC 注入、租户间隐蔽干扰提供了安全化解读空间，provenance graph 可借鉴为攻击链/异常链表达。

## 11. 代码对照分析

仓库 README 明确分为 NS-3、DPU agent、Tofino P4、C 控制器四部分：[README.md](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/README.md:1)。

P4 数据面核心在 [switch/hawkeye.p4](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/switch/hawkeye.p4:332)：epoch、pause timer、flow telemetry、port telemetry、port meter、polling flag 匹配都在这里；polling header 与 pause/PFC header 在 [switch/headers.p4](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/switch/headers.p4:101)。

控制面在 [ctrl/ctrl.c](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/ctrl/ctrl.c:1823)：raw socket 接收镜像 polling packet，随后用 `registers_syn_get` 批量读取 port/flow 寄存器；拓扑和 polling 转发表入口在 [ctrl/switch_config.h](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/ctrl/switch_config.h:59)。

检测代理在 [detection-agent/host/main.c](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/detection-agent/host/main.c:151) 和 [detection_agent.c](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/detection-agent/host/detection_agent.c:29)：读取 flow RTT，超过阈值后发送 EtherType `0x6888` polling packet；设备侧 RTT 更新在 [rtt_template.c](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/detection-agent/device/rp/algo/rtt_template.c:331)。

NS-3 入口是 [simulation/scratch/third.cc](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/simulation/scratch/third.cc:856) 和 [third_deadlock.cc](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/simulation/scratch/third_deadlock.cc:229)。交换机 telemetry 结构与输出在 [switch-node.h](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/simulation/src/point-to-point/model/switch-node.h:29)、[switch-node.cc](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/simulation/src/point-to-point/model/switch-node.cc:132)；仿真 host agent 触发 polling 在 [rdma-hw.cc](F:/泉城实验室/二期/论文/异常检测/source/Hawkeye/simulation/src/point-to-point/model/rdma-hw.cc:550)。

代码包没有传统“模型训练”文件。`simulation/mix/data/graph.py` 更像论文 Algorithm 1 的简化落地：计算 `f2p_weight`、`p2f_weight`、`p2p_weight` 并输出 JSON，但完整的表 2 签名诊断器在公开代码中不明显。

## 12. 本篇精华

- Hawkeye 的核心洞察：RDMA NPA 的根因常在受害流路径之外，必须追踪 PFC 传播因果。
- PFC 可见性不能停留在端口级；每流 paused packet count 是区分“本地竞争”和“远端回压”的关键。
- port-pair traffic meter 是高效追踪 PFC causality 的最小充分信息之一。
- 异构 wait-for graph 把流、端口、PFC、队列竞争放进同一个解释框架。
- full polling 精度高但不可扩展；victim-only 省开销但漏掉死锁环和环外根因。
- 这篇不是 ML 异常检测论文，而是可编程网络遥测驱动的因果诊断系统论文。
- 代码原型覆盖 P4、控制面、DPU agent、NS-3，但公开 analyzer 更偏图数据生成，签名诊断复现需补齐。

## 13. 建议精读路线

先读 §2 和 Figure 1，弄清 PFC backpressure、storm、deadlock 为什么破坏传统队列归因。再读 §3.3-§3.4，把 epoch telemetry、polling flag、PFC causality tracing 连起来。

随后精读 §3.5 的 Algorithm 1/2 和 Table 2，这是论文真正的方法核心。最后看 §4 的 baseline 设计和消融，重点关注 epoch 过长导致误关联、victim-only 在 deadlock 上失败、flow-only/port-only 遥测都不充分这三点。代码阅读顺序建议：`README.md`、`switch/hawkeye.p4`、`ctrl/ctrl.c`、`detection-agent/host/main.c`、`simulation/src/point-to-point/model/switch-node.cc`、`simulation/mix/data/graph.py`。

<!-- codex-cli-deep-read: complete -->
