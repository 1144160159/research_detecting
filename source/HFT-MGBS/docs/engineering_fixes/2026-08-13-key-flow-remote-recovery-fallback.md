# 关键流远端恢复 fallback 闭环

## 原问题

`GpuDispatcher` 原有 fallback 不是完成路径。GPU 请求失败或断路器开启时，
代码只增加 `fallback_flows`/`key_flows_inference_failed` 计数，随即丢弃整批。
`key_flows_local_fallback_completed` 在生产路径中从未增加，因此不能声称关键流
在 GPU 故障后已完成推理或质量等价 fallback。

物理机 Rust 端没有 A09 模型参数和可验证的本地等价推理引擎。
本修复因此不实现启发式“伪 A09”，不增加
`key_flows_local_fallback_completed`，而是实现可验证的“有界缓存→断路器探测→
TCP 重连→同一远端 A09 评分”恢复闭环。

## 实现

### 有界恢复缓存

- GPU 批次失败或 300 ms 断路器打开期间，只保留关键流；
- 恢复队列容量与现有 key GPU queue 容量一致，为硬上限；
- 断路器到期后优先 FIFO 重试恢复队列，再消费新流；
- 重试失败会重新进入有界队列；缓存已满则进入
  `key_flows_terminal_unresolved`，不得写成 completed；
- 两个输入 channel 都关闭后最多给予 2 s 恢复 grace；到期仍未评分的
  关键流转为 terminal unresolved，避免 `finish()` 无限挂起。

普通流在 GPU 失败后仍保持非阻塞丢弃，以保护捕获热路；
`fallback_flows` 是失败尝试/丢弃事件数，同一恢复流多次重试可多次计入，
不是 distinct-flow 守恒分母。

### 远端 backend 身份

远端响应只有同时满足以下条件才计入 remote scored：

1. `ok=true`；
2. `schema_version` 与请求相同；
3. `request_id` 与当前批次相同；
4. `candidate_id=A09`；
5. predictions 数量与批次流数完全相同。

报告中显式写入：

- `remote_backend_identity=A09/schema_v1/ordered_v1`；
- `local_fallback_backend_identity=none_without_equivalent_a09_model`；
- `local_fallback_quality_qualified=false`；
- `key_flow_quality_qualified=false`。

即使本次所有缓存关键流最终由远端评分，也不会自动宣布“本地
fallback 质量合格”。只有未来引入受控 A09 参数并通过训练-部署等价性门，
才能另行开放质量资格。

### 守恒与原始证据

`MetricsReport` 新增以下可对账字段：

- eligible: `key_flows_total`；
- enqueued / enqueue_failed；
- remote_scored / local_fallback_completed；
- recovery_cached/retried/recovery_remote_scored；
- recovery_pending / terminal_unresolved；
- `eligible == enqueued + enqueue_failed`；
- `enqueued == remote_scored + local_fallback_completed + recovery_pending + terminal_unresolved`。

报告保留最多 100,000 条逐批原始证据、100,000 个逐秒窗口和 100,000 个故障 episode，超限时
通过 `gpu_batch_evidence_truncated` / `gpu_window_evidence_truncated`
和 `gpu_fault_recovery_evidence_truncated` 显式计数。逐批证据使用单调 sequence，
并包含 request ID、attempt kind、outcome、flow/key 数、远端完成数、
缓存/终止数、RTT、failure code 和 observed backend identity。

`GpuDispatcher::mark_fault_injection(label)` 可在受控故障注入前记录时间和标签；
首个失败记录 detected time，恢复后记录 recovery time、recovery duration 和 backend
identity。未调用该 API 的外部故障仍会记录 detected/recovery，但 injection time 为
`null`，不伪造时间。

为满足 v2 profile 的独立重算要求，报告另外输出
`raw_latency_sample_receipts`，而不只是 Rust 自报 percentile。每个原始样本含：

- 报告内唯一 `source_id`和 metric name；
- `observed_epoch_us`、进程内单调 `observed_monotonic_us` 和
  `window_id=observed_epoch_us/1_000_000`；
- 如果存在，保留原始 kernel/source event epoch timestamp；
- 未汇总的原始 `value_us`。

收据覆盖 packet processing、flow-materialization-to-enqueue、
kernel-receive-to-feature-enqueue、GPU batch round trip 和 budget planned/actual cost。
与 GPU 批次证据一样，样本超出硬上限时必须通过 truncated 计数显式失败，
不得静默抽样。适配器可用 window ID 与 TPACKET kernel realtime packet epoch 对齐，
并用 monotonic timestamp 检查同进程内顺序。

`gpu_window_evidence` 在同一 realtime 1 s window 输出 eligible/deep-selected、
enqueued/enqueue-failed、remote-scored、cached/pending/unresolved、batch ok/fail/circuit-open
以及 GPU queue-full。这是 scheduler-to-remote 窗口；捕获 worker 在 feature queue 前丢弃的
关键流仍需由 full-pipeline worker receipt 补齐，所以当该 drop 非零时
`key_flow_quality_qualified` 依然必须为 false。

GPU worker join panic 不再被静默吞掉，会进入 `gpu_worker_join_failures`。
normal-r1b 的 GPU service CPU6 direct server batch8 P99 为 8.8 ms，但 Rust
persistent reverse RTT P99/max 为 55.139/58.699 ms（302 样本、0 failure），
符合小批 NDJSON 受 Nagle/delayed ACK 组合影响的特征。因此 direct 连接和
reverse accepted stream 都强制开启并回读验证 `TCP_NODELAY`；read/write timeout
或 `TCP_NODELAY` 任一配置失败都拒绝该 reverse 连接。每次 infer 成功/失败
都同步更新 ready 状态。该修改只建立了可验证的机制，在新二进制完成
同配置重跑前，不声称 P99 已降到 direct server 水平。

## 测试边界

新增单元与独立集成测试：

- mock GPU 第一次返回错误 candidate identity，验证该批不计 scored；
- 关键流进入有界恢复队列，断路器后重试；
- mock GPU 第二次返回正确 A09 身份和预测数，验证远端完成；
- 验证 fault injection/detection/recovery 证据和两条守恒式；
- 验证缓存满后只增加 terminal unresolved，local completed 仍为 0；
- 验证所有 quality-qualified 字段保持 false。
- 验证 reverse accepted socket 的 `TCP_NODELAY` 和 read/write timeout 实际回读值。
- 验证 raw latency receipt 的 source ID 唯一、epoch/monotonic timestamp 和 1 s window ID 可重算。

隔离验证使用
`/tmp/hft_official_drift_fix_20260813T051243Z/HFT-MGBS/rust/hft-capture`，
复用只读 `traffic-analysis-platform/rust`。未修改 runner/campaign/unified，
未覆盖物理机正式 HFT 目录，未运行网卡实验。

## 隔离验证结果

2026-08-13 在上述隔离树执行：

- `cargo fmt -- --check`：通过；
- `cargo check --tests --locked`：通过；
- `cargo test --release --locked`：35 个测试通过，0 失败；
- `cargo build --release --locked --bin tpacket_v3_full_pipeline`：通过；
- `Cargo.lock` 构建前后 SHA-256 均为
  `a6ba911cc943c6dfca0fc2f4a233a7dce99db28829a1fbe20bc6d0c191946123`。

隔离产物及关键源码 SHA-256：

- `src/gpu.rs`: `2918cefdc7b27136d59c59302e67dd0bfff559426e41d8a6c579538d6698c544`；
- `src/metrics.rs`: `2ff301ae17f001b8c5928100fe5844b009147c86ea1f3a33cc4a1806ffe143ff`；
- `src/scheduler.rs`: `f556e1a87f4364a8dccef044c3d7e20622cf4d412fdec59a508f7b1a1a916c77`；
- `src/tpacket_v3.rs`（本轮未修改）:
  `b19121b07accf139a050553fed8750d590da798ed04271a3c560cfb5ee88485a`；
- `tests/gpu_fallback_recovery.rs`:
  `02ce5874c38fd263035e84e3eca00bc2b3e85fa6832e279cf023f795eb0e1f5e`；
- `target/release/tpacket_v3_full_pipeline`:
  `fe90b64d8ba2e25c78b4275ff25935c9977cdf8b62d6d4f76e23e1bcc5a22fa3`。

这些结果只证明隔离源码可编译、恢复/守恒/证据契约通过测试；尚未同步到
物理机正式目录，也没有执行真实网卡或 GPU 故障注入。特别是 raw receipt
目前可独立重算各阶段窗口，但没有跨 packet/flow/GPU completion 的统一相关 ID，
因此不能据此单独宣称完整 e2e latency 样本门已满足；v2 profile 的正式资格仍保持 false。
