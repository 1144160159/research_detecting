# 新高速 NIC R0 到货执行缺口审计（2026-08-13）

## 结论

现有到货门可回答“新卡是否具备开始实验的硬件能力”，但不能回答“12 Mpps 工程
目标是否通过”。本次新增的独立 R0 链已经冻结后一个问题的证据合同和自动编排边界；
由于当前没有新卡，也没有与新卡型号绑定的 helper，当前真实状态仍为
`hardware_pending`，不是 `r0_qualified`。

## 完整 R0 所需证据与当前完成度

| R0 证据 | 到货门已有 | 本次独立链 | 仍需新硬件 |
|---|---:|---:|---:|
| PCIe/NUMA/管理面隔离、driver/firmware/DDP | 是 | 外部 hash 绑定 | 正式 inventory |
| native AF_XDP + forced zero-copy | 能力探针 | 三次原始运行复算 | XDP helper/实测 |
| DPDK RSS/TSS/RETA、至少八队 | 能力探针 | 三次原始运行复算 | PMD helper/实测 |
| 64 B、12 Mpps、15 s | 否 | 合同强制、sent/time 重算 | 独立发生器 |
| 零丢包/重复/乱序 | 探针级队列包量 | 六窗全部计数门 | 序列 marker 流量 |
| P99/P999 | 否 | 累计直方图复算 | PTP/marker 时基 |
| CPU/内存/RSS/HugePage | 否 | 每窗首尾覆盖与上限 | resource helper |
| 关键流覆盖 | 否 | 独立 marker 分母、每窗 99% | marker manifest |
| XDP 故障到 DPDK 恢复 | 否 | 三次 monotonic 重算、300 ms | 预置回退拓扑 |
| 管理面与数据面完整恢复 | 部分 | 九类状态 canonical equality | restore helper |
| 证据真实性 | helper 根 | arrival 根 + helper 根 + campaign 根 | 外部批准记录器 |

## 硬件/拓扑约束

- 12 Mpps 的 64 B 以太网包按 84 B 线速占用约 8.064 Gbit/s，10 GbE 理论上可达，
  但发生器、交换/直连链路和接收端都需要足够余量；不能再使用同卡本地 loopback
  作为独立发生器证明。
- 小于 300 ms 的 DPDK 回退不能依赖故障发生后再把同一 PF 从 kernel driver 改绑到
  vfio。必须在实验开始前预置第二 PF、VF/SF 或 bifurcated PMD，并由到货 inventory
  证明管理面不在这些端口上。
- XDP 主路径必须明确拒绝 generic/SKB 和 COPY fallback；DPDK 回退必须输出实际
  RSS/TSS/RETA 与每队包量，不能只写 `rss_enabled=true`。
- P99/P999 只有在所有 unique packet 有时间戳、负延迟为零且时基误差不超过 5 us
  时才可使用。

## 风险封闭顺序

1. 到货 gate 失败：不进入 R0。
2. helper manifest 或到货 evidence 外部 SHA 不匹配：不开始任何变更。
3. R0 执行中断：trap 自动恢复；不可捕获终止后通过 `RECOVER` 使用同一冻结 helper。
4. 恢复失败：留下 `RECOVERY_REQUIRED`，不得 compose。
5. evidence manifest 未在 campaign 外记录：只保留 `evidence_pending`。
6. R0 任一指标失败：`r0_rejected`；不得进入生产 Pareto。

## 与现有发布链的接口

本次没有改 `unified_release_audit` 或 `production_pareto`。未来接入时，统一审计必须
绑定 R0 contract、runner、composer、evaluator 和外部 evidence-manifest SHA，并
重新核对 `r0_qualified`；不能只读取一个状态布尔。R0 通过也只能解锁后续 R1--R4，
不能直接成为生产候选。

