# XDP 运行时抓包驱动回退修复

## 问题现象

`xdp-skb` 已通过正常路径三轮诊断，但原实现遇到 XDP poll 错误会直接退出，
无法在同一进程内切到 `af-packet-ts`。这只具备启动/停止清理能力，不满足
运行中故障后的恢复约束。

## 根因

主循环对 `capturer.poll()` 使用 `?` 直接传播错误；运行指标也没有回退次数、
恢复耗时、原因和回退后真实流量计数，无法区分“成功恢复”与“进程退出后
外部重启”。

## 修改范围

- 新增可选 `--capture-fallback-driver af-packet-ts`。
- XDP 启动或 poll 失败时，先读取并累计主驱动丢包、执行 XDP/UMEM 清理，
  再创建并启动 timestamped AF_PACKET，主循环不中断。
- 新增回退次数、恢复耗时、原因和回退后处理包数指标。
- 新增只在显式 `--allow-diagnostic-fault-injection` 下可用的 XDP poll
  故障注入；在线运行脚本进一步限制它只能用于物理诊断作用域。
- 新增专用运行器、单轮验证器和三轮保守聚合器。
- 未修改只读上游 `traffic-analysis-platform/rust`。

## 验证证据

三次运行目录：

- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T092308905574298Z`
- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T092545928785276Z`
- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T092626476188838Z`

聚合证据：
`/home/wangwt/task/datasets/replay/hft_xdp_skb_capture_fallback_v1_20260730/summary.json`，
SHA-256 为
`7292d6763ecacc3af631786156650b33329a129c41fdfb9ad6c4ddf3b860e55f`。

每轮在约 50,000 包后注入 XDP poll 故障，均只触发 1 次回退。最坏恢复
118.946 ms，小于 300 ms 门；回退后每轮至少继续处理 100,249 包。三轮
退出后均 promisc=0、无残留 XDP 程序且 GRO 恢复。Rust 5 个库测试、
3 个注入器测试与 Python 2 个回退证据测试通过。

首次全量同步在 `cargo fmt --check` 发现 `pcap_injector.rs` 一处纯排版
差异并失败关闭；已在物理机用同一 Rust 工具链格式化、同步回本地后重跑。
该差异不改变注入器逻辑或上述运行证据。

## 性能影响与回退

正常路径未配置回退时不增加数据面分支之外的额外 socket；配置回退后只在
错误发生时创建 AF_PACKET socket。切换窗口三轮最多少收 1,307 包，因此
回退实验不复用正常路径零丢包证据，也不进入正常路径 Pareto 指标。

若 XDP 清理失败、AF_PACKET 启动失败、恢复超过 300 ms、回退后没有真实
流量、残留 XDP/promisc 或 GRO 未恢复，则失败关闭并退出，不连续尝试第二次
回退。

## 遗留风险

当前只是 0.01 Mpps、15 秒、注入式单故障诊断。切换不是无损热备，生产负载
下的包损失、P99、资源与重复故障行为尚未验证；因此
`production_fallback_evidence_complete=false`、
`final_pareto_ingestion_allowed=false`。
