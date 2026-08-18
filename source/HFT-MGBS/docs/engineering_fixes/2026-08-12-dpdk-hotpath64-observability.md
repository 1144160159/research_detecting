# DPDK 64B 热路径与瓶颈可观测性修复

## 问题现象

2026-08-12 的 Q1 12 Mpps 诊断只能达到约 2.57 Mpps。旧版 `tx_stalls` 同时累计
mbuf 批量分配失败和 `rte_eth_tx_burst()` 返回 0，`rx_stalls` 也只表示空轮询次数；
结果中没有驱动实际采用的 descriptor 数量，也没有运行前后的 mempool 可用/占用数量。
因此旧证据无法区分分配池耗尽、发送队列无法回收、partial burst、RX 空轮询和包准备
成本。

## 根因与修改范围

修改仅位于 HFT-MGBS 自有 `rust/hft-dpdk`，未改动只读上游：

- `main.rs` 分离 TX 的 `prepare_calls/alloc_fail/tx_calls/tx_zero/tx_partial/tx_full/
  tx_successful_bursts`，以及 RX 的 `rx_polls/rx_nonzero/rx_zero`；旧 `stalls` 字段保留为
  兼容聚合值，不再作为唯一归因证据。
- C shim 返回 `rte_eth_dev_adjust_nb_rx_tx_desc()` 后的实际 RX/TX descriptor，并读取
  `rte_mempool_avail_count()` 与 `rte_mempool_in_use_count()` 的运行前后快照。
- 当且仅当 frame size 为 64 且模板数是 2 的幂时，模板选择从除法取模改为掩码，复制
  固定为 64 字节；其他帧长仍走原有安全通用途径，时间戳偏移和 mbuf 所有权不变。
- 连续 TX/RX zero poll 每 64 次检查一次单调时钟和窗口；任何成功或 partial burst 后仍
  检查。独立 worker 生命周期 watchdog、RX drain quiet period 和失败退出未删除。

## 契约与验证

物理机首次编译时，Rust 1.93 的严格 Clippy 门将手工取模判定识别为
`manual_is_multiple_of` 并阻断构建；已改为 `is_multiple_of(64)`，随后远端
`cargo test` 13/13、Clippy 和 release 构建均通过。该修复不改变轮询周期语义。
release 二进制 SHA-256 为
`0b7a85fe3194636a03d2ce3a1fae461ce3e63f215c81ef8a32d603574b6ef038`；
新增独立冻结的 1 Mpps/B256 安全回归合同，未覆盖任何历史证据配置。
该合同已在物理机运行通过：15/15 完整 TX/RX 窗口最低均为 1.00992 Mpps，
15,150,080 包零 gap，P99/P999 为 14.4146/132.1932 us；TX 59,180 个 burst
全部 full，`alloc_fail/tx_zero/tx_partial=0`。acceptance、恢复账本和完整证据
SHA-256 检查均通过，远端目录为
`/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260812T123553090231277Z`。

- 执行合同：`configs/dpdk_hotpath_10mpps_execution_v1.json`，规定本环境的
  compile -> 1 Mpps -> 5 Mpps -> 10 Mpps 三次阶梯、零丢包/时延/恢复/完整证据硬门。
- 静态契约：`tests/test_dpdk_hotpath_contract.py`。
- 本地运行静态契约与既有 runner 契约：11/11 通过。
- 本地 Windows 未安装 Rust/DPDK 工具链，因此尚未声称编译通过或性能改善；必须在
  10.0.5.8 使用既有隔离 DPDK 构建环境完成编译后，重新冻结二进制哈希再触发双 PF。

## 性能预期与判读

64B 掩码和定长复制减少模板索引除法及动态长度分支，时钟摊薄减少空轮询路径上的
`clock_gettime`/`Instant` 调用。它们是低风险降本，不预设能够单独从 2.57 Mpps 提升到
10 Mpps。新计数应按以下顺序判读：

- `alloc_fail > 0` 或 mempool available 接近 0：优先扩大/拆分 mempool 或加快回收；
- `tx_zero/tx_calls` 高且 `alloc_fail == 0`：发送描述符回收/PMD/硬件队列是主限制；
- `tx_partial` 高：评估 descriptor/cleanup threshold 与 burst 配置；
- TX 达标但 RX 不达标且 `imissed/rx_nombuf > 0`：接收路径或单队列是主限制；
- TX 与 RX 均达标且 packet gap 为 0，才进入正式三次 10 Mpps 门。

## 回退条件与遗留风险

任一编译/单测失败、watchdog 超时、恢复失败、证据哈希失败或 1 Mpps 安全门失败立即
回退到上一冻结二进制。bnx2x 单队列是否具备 10 Mpps 能力仍未证明；本修复提供低风险
优化和可归因证据，但不会把未达标诊断提升为 R0 验收或最终 Pareto 证据。
