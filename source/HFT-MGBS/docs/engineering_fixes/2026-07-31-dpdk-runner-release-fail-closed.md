# DPDK runner 发布级失败闭锁整改

## 问题现象

既有双 PF runner 能完成受控数据面测试和常规回绑，但仍不足以作为发布资格入口：

- Rust 只把 TX 最低 1 秒速率纳入硬门，RX 速率虽有输出却未独立判门；
- `result.json`、资源观测、恢复快照和 stdout/stderr 没有全部作为必需证据；
- `/usr/bin/time -v` 只记录 CPU/RSS，不按预先冻结的资源预算判门；
- 信号处理共用 `trap 'restore_host || true'`，可能吞掉恢复错误；
- interface、PCI BDF、master、全表路由、并发 DPDK 所有权和内部互斥检查不完整；
- 原始 Rust 结果把“数据面硬门通过”直接写成
  `r0_capture_only_qualified=true`，容易被误读为资源和恢复也已通过。

历史 Q1/B128/1 Mpps 结果仍是有效的历史数据面证据，但其 CPU/RSS 只能保持
observational，不能把观测值反向解释为当时已经存在的发布资源门。

## 根因

原实现把数据面、资源、主机恢复和证据完整性混在一个成功码中，而且 runner 的安全条件有一部分依赖外层人工命令。这样无法保证一次独立调用同时满足以下四个条件：

1. 冻结候选与实际二进制参数完全一致；
2. TX、RX、丢包和时延均通过；
3. CPU、RSS 和 HugePage 均在事先冻结的预算内；
4. 主机恢复与证据清单均可独立复核。

## 修改范围

### Rust 原始结果 schema 5

`rust/hft-dpdk/src/main.rs` 新增：

- `candidate_id` 与 `frozen_thresholds_sha256`；
- `main_cpu/rx_cpus/tx_cpus` 和实际 P99/P999 门限；
- TX 与 RX 两个独立速率错误项；
- TX/RX 共享单调时钟起点并使用固定 1 秒窗口，同时输出完整窗口数；
- replay `oerrors` 硬门；
- 单队列后端标识 `dpdk_bnx2x_single_queue`；
- `data_plane_qualified` 与 `resource_gate_evaluated` 的显式分离。

原始进程只知道数据面状态，因此 schema 5 固定输出
`resource_gate_evaluated=false`、`r0_capture_only_qualified=false`、
`full_pipeline_qualified=false` 和
`final_pareto_ingestion_allowed=false`。只有外层资源与恢复验收全部通过后，
派生 `acceptance.json` 才能把本次 R0 capture-only 标记为合格。

### 冻结发布候选

新增
`configs/r0_dpdk_probe_1mpps_b128_release_gate_v2.json`，仅适用于未来运行，
不追认历史结果。候选固定为 Q1/B128/1 Mpps/15 s，并冻结：

- 进程平均 CPU：不高于 1.5 核；
- 最大 RSS：不高于 65,536 KiB；
- HugePage：512 × 2 MiB，即不高于 1 GiB；
- P99/P999：不高于 100/500 us；
- 运行前连续 5 个 1 秒样本中，main/RX/TX 及其 SMT sibling 利用率均不高于 5%；
- TX/RX 最低完整 1 秒速率：均不低于 1 Mpps；
- 数据面丢包、收发差值和 replay oerrors：均为 0。

该预算用于后续候选验收，不改变历史 1 Mpps 的 observational 标签。

### 派生验收器

新增 `scripts/validate_dpdk_run.py`，在不改写原始 `result.json` 的前提下生成
`acceptance.json`。验收器拒绝以下任一情况：

- schema、候选 ID、配置 SHA-256、PCI、CPU 亲和性或门限不一致；
- TX/RX 任一速率、时长、丢包、收发差值或时延失败；
- `/usr/bin/time -v` 缺失、CPU/RSS 超限；
- GNU time wall time 与 Rust 数据面时长不一致或初始化/清理开销超出 5 秒预算；
- HugePage 数量、页大小与冻结候选不一致或超限；
- 延迟样本少于 10,000、采样步长或 TSC 时间戳来源不一致；
- Rust 原始数据面结果含错误；
- 原始结果自行宣称资源、完整 R0 或最终 Pareto 已通过。

### runner 生命周期

`scripts/run_dpdk_bnx2x_validation.sh` 新增或收紧：

- runner 内部 `flock`，覆盖预检、双 PF 解绑、运行、恢复和证据生成；
- 精确校验 `ens8f0→0000:cb:00.0`、
  `ens8f1→0000:cb:00.1`，并要求授权对覆盖同卡全部 Ethernet PF；
- 拒绝 master/upper、IPv4/IPv6 地址与全表路由、策略路由、XDP 程序、
  活跃 DPDK 进程、活跃 EAL runtime 和所有权不明的 HugePage 文件；
- HUP/INT/TERM 分离处理，数据面置于独立进程组，EXIT finalizer 先停止自有子进程，
  再执行回绑；
- 在 PF 解绑前执行 CPU/SMT 空闲度采样；失败时生成
  `hft_dpdk_preflight_blocked_*` 证据并保持 `mutations_performed=false`；
- `restore_attempted` 与真实 `restore_status` 分离，重复清理不能把首次失败改成成功；
- 保存并恢复原始 `driver_override`，不再写 `new_id`，不再吞掉模块卸载失败；
- 恢复步骤写入 `restoration_ledger.json`，最终状态重新核验驱动、BDF、10GbE
  carrier、队列、ring、coalesce、GRO/LRO、qdisc、HugePage、UIO、mount 和
  EAL runtime；
- `result.json`、资源文件、前后快照、日志、验收结果和恢复账本全部为必需证据；
- 生成 base/complete SHA-256 清单并立即执行 `sha256sum -c`；
- 退出优先级固定为：恢复失败 15、证据不完整 16、资格失败 10、原始进程状态。

没有修改只读上游
`/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 验证证据

本地已完成：

- `bash -n scripts/run_dpdk_bnx2x_validation.sh`；
- `tests.test_dpdk_acceptance` 与
  `tests.test_dpdk_runner_contract`、`tests.test_dpdk_cpu_preflight`
  共 21 项，全部通过；
- `py_compile` 通过；
- 新增的 Rust 纯函数测试覆盖 RX 独立速率门和 replay/运行时延迟门。

截至本记录形成时，Codex 的外部写入审批通道因用量限制拒绝 `scp`，所以本轮新代码
尚未同步到 10.0.5.8，也尚未在物理机执行 `cargo fmt/test/clippy/build` 或新的双 PF
运行。此状态必须报告为“本地实现通过，远端编译与实机回归待执行”，不得报告为修复
已完成上线。

配置当前还保留 `binary_freeze_pending=true`。这是有意的两阶段门：先在物理机完成
schema 5 release 构建并取得二进制 SHA-256，再把该哈希写回配置并将 pending 改为
false。pending 期间 non-mutating preflight 可以执行，但 runner 会在任何 PF 变更前
拒绝数据面运行。

## 性能影响

runner 的额外开销只发生在数据面之前或之后，包括网络所有权检查、快照、资源解析和
哈希；不进入 15 秒 DPDK 热路径。Rust 热路径新增的判断只在运行结束后执行。实际吞吐
影响必须由后续同配置 A/B 实机回归确认。

## 回退条件

如 schema 5 二进制无法通过远端构建，或 runner 恢复故障注入发现不能可靠回绑，应：

1. 不执行双 PF 数据面；
2. 保留本次失败构建/测试证据；
3. 继续使用旧 runner 仅作 diagnostic，不允许进入发布资格；
4. 修复后重新从 Q1/B128/1 Mpps 开始，不复用历史资源观测作为新门禁结果。

## 遗留风险

- SIGKILL 和整机掉电无法由 shell trap 捕获，仍需要后续 systemd watchdog/
  `ExecStopPost` 或独立幂等恢复命令；
- 当前 release v2 明确只接受 Q1；bnx2x PMD 的 Q2/RSS 分支保持关闭；
- 固定 1 秒桶在 Q1 可用，但多队列“逐桶求和后再取最小”尚未实现；
- `acceptance.json` 已绑定 thresholds、result、GNU time、HugePage 快照、runner、
  二进制和 validator 的逐文件 SHA-256；完整清单再次封装这些输入；
- 最终 Pareto 仍需协议解析、加密流量识别、多粒度特征、预算调度、关键流覆盖、
  fallback 压测和长稳全部通过。
