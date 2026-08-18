# 物理双口诊断与 GRO 计数对齐修复

## 问题现象

ens8f1 发送 151,563 个线速包且 ens8f0 NIC 收到相同数量，但 AF_PACKET 用户态只获得 148,663 个包，严格计数审计报 `counter_reconciliation.nic_to_capture`。同时，原有运行器只有生产物理证据和虚拟诊断两种作用域，无法安全表达“物理链路诊断但不进入最终 Pareto”。

## 根因

ens8f0 的 GRO 开启，将部分线速分段在进入 AF_PACKET 用户态前聚合；这不是 NIC 丢包，但会破坏逐包计数和特征语义。作用域缺失则会造成诊断阈值与生产 SLA 混用风险。

## 修改范围

- 新增 `physical_link_live_diagnostic` 作用域和冻结的低负载诊断阈值。
- 新增物理双口诊断入口，只在 ens8f0 测试期间关闭 GRO/LRO，退出时恢复原状态。
- 运行证据记录 offload 策略和前后特性快照。
- 诊断证据强制 `diagnostic_only=true`、`final_pareto_ingestion_allowed=false`。
- 未修改 `/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 验证证据

- 初次失败：`/home/wangwt/task/datasets/replay/hft_pdiag_20260730T065603001813876Z`
- 修复后通过：`/home/wangwt/task/datasets/replay/hft_pdiag_20260730T070228877021587Z`
- 修复后发送、NIC 接收、用户态采集均为 151,563，capture drop 为 0；解析拒绝率 0.0003563，关键流覆盖 1.0，GPU P99 75,926.471 us。
- 退出后 ens8f0 GRO 恢复为 on、LRO 为 off。

## 性能影响与回退

关闭 GRO 会增加逐包处理开销，但保证逐包特征与丢包审计可解释。诊断脚本只做临时切换；任何异常退出均由 trap 恢复。生产配置在冻结目标负载后再比较 XDP 与 AF_PACKET 的资源/P99 Pareto。

## 遗留风险

该结果是 0.01 Mpps、15 秒机械诊断，不是生产 SLA 或最终 Pareto 证据；仍需三次 XDP 稳定复测、正式负载和 24/72 小时长稳。
