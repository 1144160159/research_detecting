# DPDK 工作线程可选实时隔离

## 问题与证据

多队列版本完成构建后，单队列 1 Mpps 兼容性运行
`hft_r0_dpdk_20260731T020124813509403Z` 出现 51,935 个 `imissed/rx_nombuf`
和 9.52 ms 最大时延。运行同期存在一个不属于 HFT-MGBS 的 pytest 任务，
占用约 83 个逻辑核且系统负载超过 100；旧版单队列 B128 在无该干扰时已零丢包并通过
P99/P999 门禁。因此该轮不能直接判定为 Rust 多队列回归。

## 修复

- Rust CLI 新增 `--realtime-priority`，默认值为 0，即保持普通调度。
- 显式启用时只把已固定到独占收发核的 DPDK worker 设置为
  `SCHED_FIFO`；main 线程和其他进程不变。
- 优先级硬限制在 0–20，避免不受控的高优先级配置；配置失败立即退出。
- 运行 JSON、manifest 和结果报告均记录该参数；报告 schema 升级为 3。
- 证据包补齐 `Cargo.toml`、`build.rs` 和 C shim 头文件，确保实现快照可复核。
- worker 就绪通道现在返回初始化成功或具体错误，避免亲和性、调度策略或
  DPDK thread register 失败被统一掩盖成 5 秒超时。
- 扰动脚本在解绑 PF 前检查 `RLIMIT_RTPRIO` 和一次短生命周期 `chrt` 探针；
  主机无权限时 fail-closed，不再进入网卡解绑阶段。

## 受控验证

1. 先运行 `Q1/B128 @ 1 Mpps, RT=10`，验证功能回归、零丢包和时延。
2. 仅当第 1 步全硬门通过时，运行 `Q2/B128 @ 5 Mpps, RT=10`。
3. 仅当第 2 步全硬门通过时，才允许创建并运行 10 Mpps 候选。
4. 每轮必须恢复双 PF 至 bnx2x、接口 UP/10GbE、hugepages 和 UIO 前缀状态。

## 实测结论

冻结候选 `Q1/B128 @ 1 Mpps, RT=10` 的首次运行
`hft_r0_dpdk_20260731T022059475661619Z` 在 worker 就绪阶段退出，未发包、未生成
`result.json`。主机实测 `RLIMIT_RTPRIO=0`，`chrt -f 10 true` 返回
`Operation not permitted`，所以 RT10 在当前部署环境不可用。该轮自动恢复验证通过：
双 PF 回绑 bnx2x、双口 UP/10GbE、hugepages=0、运行前缀残留=0。

RT10 候选因此被拒绝，不通过修改系统限制强行启用。后续回退到
`realtime_priority=0`，在外部高负载任务自然结束后重新运行 Q1，再决定是否进入 Q2。

## 风险与回退

实时调度只在冻结候选配置中显式开启，线程固定在 CPU 36–37 和 44–45，
测试持续 15 秒。进程退出后实时线程随即销毁。若功能回归失败、门禁失败或恢复验证失败，
停止放大负载并回退为默认 `realtime_priority=0`。

该修复仍属于双 PF capture-only R0 诊断，不构成全链路 Pareto 合格证据，
`final_pareto_ingestion_allowed=false`。
