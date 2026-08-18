# UDP 单线程本地流状态热路径修复记录

## 适用边界

本修复是当前硬件 2.79 Mpps 闭环的第三个单变量候选，只改变 HFT-MGBS 自有 Rust 流状态路径，不修改 `traffic-analysis-platform`。它不更改 QM、GPU、调度、TPACKET、traffic-v2、IRQ、runner 资格逻辑或冻结配置。未进行网卡正式实验，因此不得把本修复标记为合格 repeat，`full_pipeline_qualified` 与最终 Pareto 资格必须继续保持 false，直到正式 runner 重新冻结并完成独立实跑。

## 两轮正式证据与决策原因

1. `qm_probe_r1`：18 个完整窗口最小值 2.783028 Mpps；NIC discard 11,665；GPU P99 16.637 ms；QM 运行时证据为 1,160 个 distinct flow、跨 worker collision=0；恢复台账全绿。该轮证明 QM flow-affinity 成立，但吞吐和零 discard 门未通过，不计合格 repeat。
2. `qm_hotpath_r2`：18 个完整窗口最小值 2.791237 Mpps；NIC discard 3,970 且全部位于 queue 1；GPU P99 16.961 ms；2,032 个闭流全部 scored；QM collision=0；恢复台账全绿。该轮已经越过每秒 2.79 Mpps 门，但零 NIC discard 仍未通过，不计合格 repeat。

两轮 worker CPU 仍约 99.6%，且第二轮只剩单队列极小丢包，因此第三个候选只针对每包流表成本，不同时更改流量、IRQ、QM 或 GPU 参数。

## 修复内容

- UDP 包在每个已由 QM 证明单 worker 归属的捕获线程内进入 `HashMap<FlowKey, LocalUdpFlowState>`，不再逐包访问 `PartitionedFlowTable` 的 DashMap/原子字段，也不再同时维护 `extras` 双表。
- TCP 和其他非 UDP 协议完整保留原通用途径。UDP 与通用流表共同参与全局容量淘汰；expire 和 flush 跨两类状态按冻结的 canonical `FlowKey` 顺序物化。
- 本地统计保持上游 `FastStats` 的整数累加和 f32 mean/std 物化语义；全局 IAT、方向 IAT、包长、payload、首包端口、双向 canonical key、HighestDscp TOS、UDP 零 flags、key-flow 和 priority 均保持旧路径语义。
- `RAW_FEATURE_ORDER` 未修改。UDP 专用途径物化的 38 维向量以旧通用途径作为 oracle 逐元素进行 bitwise 比对。
- expiry 首次扫描的调用时机不变；只把原先 `last_expire_timestamp_us=0` 产生的 epoch 级巨大 delta 标记为首样本省略，并新增有效 delta 样本数，避免把首轮启动时间误报成扫描间隔。

## TDD 与隔离验证

隔离树：`/tmp/hft_udp_fastpath_v1_20260813/HFT-MGBS/rust/hft-capture`。隔离树使用 official Cargo.lock，SHA-256 为 `a6ba911cc943c6dfca0fc2f4a233a7dce99db28829a1fbe20bc6d0c191946123`。

新增测试覆盖：固定双向 UDP 序列、2,000 包确定性随机序列、active expiry、idle expiry、flush、双向 canonical key、payload sample、全局/方向 IAT、包长、payload 字节、TOS HighestDscp 和 UDP flags=0。测试的旧路径 oracle 直接调用未优化的通用 `PartitionedFlowTable + FlowExtras` 路径，38 个特征逐元素按 `f64::to_bits()` 比对。

隔离 release 定向测试结果为 8 passed、0 failed、2 ignored。2,000,000 包、145 flow 的 release 微基准结果：本地 UDP 状态 120,079,684 ns，通用途径 375,719,771 ns，单线程合成热路径加速 3.129x。该微基准只证明实现候选具有显著 CPU 降本潜力，不代表正式网卡吞吐或零丢包已经通过。

## 停止门与正式发布顺序

- 任一 feature equivalence、active/idle/flush、canonical、TOS 或 payload fixture 失败，停止发布。
- official-derived `cargo fmt -- --check`、`cargo test --release --locked`、正式 binary build 或 Cargo.lock 哈希漂移，停止发布。
- 正式实跑必须继续证明 QM runtime affinity 完整、collision=0；否则 UDP 本地状态的单 owner 前提不成立，raw 结果不得使用。
- 仅在新的正式 binary SHA 写回 runner/config、冻结门更新、完整 runner 实跑且 NIC `rx_discards` delta=0、每个完整秒至少 2.79 Mpps、GPU/恢复/证据门全部通过后，才可把该轮计入 repeat。

