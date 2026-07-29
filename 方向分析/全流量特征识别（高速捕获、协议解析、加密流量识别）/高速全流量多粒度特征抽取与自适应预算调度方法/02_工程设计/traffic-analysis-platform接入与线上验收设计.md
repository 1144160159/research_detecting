# traffic-analysis-platform 接入与线上验收设计

更新日期：2026-07-24。

目标是把 HFT-MGBS 接入真实采集数据面，并补齐物理 NIC 丢包、端到端 P99/P999、资源、关键流覆盖、回退恢复和长稳证据。此阶段不更换平台总体语言，也不把 Python 管线直接放入逐包热路径。

## 1. 语言与职责边界

| 层级 | 保留语言 | HFT-MGBS 职责 |
|---|---|---|
| 采集、解析、逐包/逐流热路径 | Rust | 基础特征、关键流判定、预算调度、可选层升级、熔断回退、细粒度计数器 |
| 配置、探针管理、gRPC/Kafka、策略发布 | Go | 下发版本化预算配置和阈值，采集探针心跳与证据 manifest，不执行逐包特征 |
| 秒/分钟级跨流窗口与下游流处理 | Java/Flink | 跨流窗口、会话、聚合和告警特征，不重复 Rust 已完成的逐包统计 |
| 训练、候选生成、离线复现、证据合并 | Python | 保留现有 HFT-MGBS 实现作为语义参照和离线实验控制面 |

结论：只把经过验证的 Python 语义移植到 Rust 热路径；平台不应整体改写成 Python，也不需要把 Go/Java 改成 Rust。

## 2. 具体接入位置

上游项目：[`1144160159/traffic-analysis-platform`](https://github.com/1144160159/traffic-analysis-platform)。

### 2.1 采集入口

位置：

- `rust/probe-agent/probe-agent/src/capture/xdp.rs`
- `rust/probe-agent/probe-agent/src/capture/af_packet.rs`
- `rust/probe-agent/probe-agent/src/capture/packet_batch.rs`

这里仅增加可核验的驱动、socket/ring、UMEM 和批次时间戳证据，不执行昂贵特征。必须分别记录物理/驱动丢包、采集环丢包和应用拒绝，不能用一个 `dropped=0` 或合并计数替代。

### 2.2 HFT-MGBS 主热路径

首选入口：

- `rust/probe-agent/probe-agent/src/aggregator/packet_processor.rs`
- `PacketProcessor::process_batch`
- `PacketProcessor::process_packet`

实施顺序：

1. 批次开始时读取不可变配置快照，记录配置版本、硬预算和 safety ratio；
2. 沿用现有 `PacketParser` 与双向规范化 `FlowKey`；
3. 全量执行 packet/base 特征和流表更新；
4. 识别关键流并先为其保留 flow tier；
5. 按批次压力、成本 EMA、效用 EMA 和剩余预算决定普通 flow/deep 升级；
6. deep 失败时只关闭 deep 层，packet/flow 基线继续运行；
7. 输出实际使用预算、关键流覆盖、模式、回退原因和配置版本。

不要在 `process_packet_fast` 中调用 Python、gRPC、Kafka或同步 GPU RPC；任何跨进程调用都会破坏 P99。

### 2.3 流状态与可选特征

位置：

- `rust/probe-agent/probe-agent/src/aggregator/flow_table.rs`
- `FlowValue`
- `PacketInfo`

现有 `FlowValue` 已包含双向包/字节、TCP flags、包长、双向 IAT、active/idle 和 TOS 等基础统计，可直接映射大部分 HFT-MGBS flow tier。

新增原则：

- 全流量必需字段采用定长、无锁或原子结构；
- payload sketch、加密握手摘要等昂贵状态放入分区 sidecar，只为获批 flow/deep 流创建；
- 只保留有界前缀或统计摘要，不在热流表保存完整载荷；
- 每个可选状态都必须有字节上限、过期策略和驱逐指标；
- key-flow tier 可以使用配置硬上限，普通 flow/deep 只能使用 safety soft limit。

### 2.4 指标与证据

位置：

- `rust/probe-agent/probe-agent/src/metrics/mod.rs`
- `rust/probe-agent/probe-agent/src/interface_monitor.rs`

在现有 `PACKETS_DROPPED`、处理时延、CPU/RSS 等指标之上增加：

- `capture_driver_drop_total`
- `capture_ring_drop_total`
- `parse_reject_total`
- `hft_budget_overrun_total`
- `hft_key_flow_total` / `hft_key_flow_covered_total`
- `hft_optional_cost_seconds`
- `hft_stage_latency_seconds{stage}`
- `hft_fallback_state`
- `hft_fallback_transition_total{from,to,reason}`
- `hft_fallback_recovery_seconds`
- `delivery_drop_total`
- `feature_emit_e2e_seconds`

所有计数器需携带 `probe_id`、`interface`、`capture_driver`、`config_version` 和 `run_id`，但禁止以 flow ID 作为 Prometheus label，避免高基数。

### 2.5 配置、协议和下游

位置：

- `go/control-plane`
- `proto/traffic/v1`
- `java/flink-jobs/flink-feature-job`

Go 控制面新增版本化 HFT 配置，下发后由 Rust 原子切换不可变快照；探针心跳回传当前版本、模式、驱动计数器和最后恢复结果。Proto 新字段使用向后兼容的可选字段，至少包含 `feature_tier`、`budget_config_version`、`fallback_reason`、`key_flow` 和 `feature_schema_version`。

Flink 只接收 Rust 已产出的逐流特征，并补充跨流窗口；它不应重新解析原始包，也不应成为逐包预算调度器。

## 3. 丢包与端到端时延口径

必须同时冻结并核对以下计数：

```text
流量发生器 offered
  -> NIC hardware received / hardware missed
  -> XDP 或 AF_PACKET accepted / ring dropped
  -> parser accepted / rejected
  -> HFT base emitted / optional degraded
  -> sender delivered / delivery dropped
```

验收报告分别给出：

- 物理/驱动丢包率；
- capture ring/UMEM 丢包率；
- 解析拒绝率；
- HFT 预算降级率；
- 发送/交付丢弃率。

这些指标不能简单相加，也不能把解析不支持、预算降级或发送失败记成 NIC 丢包。每层使用相邻层计数对账，任何计数缺失都判定证据不完整。

端到端时延从 NIC 硬件时间戳开始；无硬件时间戳时，使用最早内核接收单调时钟并明确降级口径，结束点为带特征事件成功进入发送队列。分别输出 P50/P95/P99/P999/max，当前 Python 的批次处理 P99 仅作离线参照。

## 4. 上线验证顺序

1. **证据合同**：先落地配置版本、五段丢包计数和端到端时间戳；
2. **语义对齐**：同一 PCAP 同时通过 Python HFT-MGBS 与 Rust shadow path，对双向流、包数、字节、IAT、flags、窗口和 tier 决策逐项比对；
3. **真实 NIC shadow**：Rust 计算 HFT 特征但不改变现有输出，确认额外 CPU、RSS、P99 和丢包；
4. **预算启用**：启用 `batch512/budget5000us/safety0.50`，关键流先保留，普通/deep 使用 soft limit；
5. **回退演练**：分别注入 extraction、delivery 和 capture-driver 故障，验证三类回退原因不混淆；
6. **负载矩阵**：64B、IMIX、真实流量，在目标负载、1.2 倍峰值和高 churn 下至少三次重复；
7. **长稳**：先 24 小时、再 72 小时；期间执行配置切换、故障恢复和回滚；
8. **最终门禁**：冻结目标 Gbps/Mpps、丢包、P99/P999、资源、质量、事件覆盖和恢复阈值后，重新计算部署配置 Pareto 前沿。

## 5. 当前禁止事项

- 不把离线吞吐或批次 P99 写成线上指标；
- 不把 normal/fallback 当作两个独立部署 Champion；
- 不在未知物理 NIC、驱动和发生器计数时声明零丢包；
- 不在跨域 macro-F1 仍低且阈值未冻结时宣称质量通过；
- 不在热路径引入 Python RPC 或同步 GPU 调用；
- 不基于本次观测值反向制定刚好能通过的 SLA。
