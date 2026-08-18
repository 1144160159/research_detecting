# Algorithm qualification campaign 正式执行进度

日期：2026-08-14

## 当前结论

本记录是执行中的时间点快照，不是完成回执。当前硬件的 2.79 Mpps 证据仍应判定为“零丢包但持续速率 NOGO”；算法正式轮 `formal_r3` 仍为 `active`，尚未形成 60/60 正式结果、accepted formal receipt 或生产 Pareto 放行依据。新 NIC 上的 XDP 主路径与 DPDK 回退验证仍为 `pending`。

## 当前硬件 2.79 Mpps 判定

当前封存证据目录为：

```text
/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T154636Z_timerpaced_burst64_ratep5469_capacity_r2
```

该轮共接收并解析 `50,866,489` 个包，socket、内部队列及 NIC `rx_discards` 均为 0；GPU 侧完成 `218/218` 批和 `1704/1704` 流，P99/P999 为 `16.596607/18.614589 ms`，恢复检查通过。但 17 个对齐速率窗的实测速率为：最小 `2.617057 Mpps`、中位 `2.774362 Mpps`、最大 `2.791930 Mpps`，只有 `5/17` 个窗口达到 2.79 Mpps；发生器整轮平均仅 `2.738608 Mpps`。

因此该证据证明当前链路在本轮工作量下没有观察到丢包和恢复异常，但不能证明 2.79 Mpps 可持续。2.79 Mpps 只能保留为当前观察上限，持续 2.79 Mpps 门为 `NOGO`；该轮仍是 diagnostic/capacity evidence，不得改写为 runtime、full-pipeline 或 production Pareto 已通过。

## 正式 campaign 轮次

| 轮次 | 状态 | 正式单元 | 结论 |
| --- | --- | ---: | --- |
| `algorithm_qualification_20260813T194500Z_formal_r1` | failed closed | 0/60 | campaign 结果根位于 NFS，`flock` 返回 `No locks available`；失败发生在候选执行前，保留为入口失败证据，不复用。 |
| `formal_r2` | failed closed | 0/60 | `write_status` 调用的 argv 传递失败；失败发生在候选执行前，不计入任何正式结果。 |
| `formal_r3` | active | 未封口 | 当前仍在执行；`active` 只表示作业在运行，不等于 60/60、accepted receipt、算法最优或生产放行。 |

正式执行按第五次冻结（FIFTH）合同运行：

```text
configs/algorithm_qualification_campaign_v1.json
sha256=3ba9a81f3099c4aa5de111c9c9eef4ad0c347b65b8af8d1eacc1d2a9c61ad10b
```

该合同精确绑定 26 个 repository artifacts、A01--A10 共 10 个候选协议，以及 `10 candidates x 2 modes x 3 seeds = 60` 个正式评估单元。这里的“60 单元”是实验矩阵，不应与测试用例数量混淆。

冻结后的 campaign 回归测试已在本地和 GPU 远端分别达到 `60/60`；权威 raw replay 回归为 `11/11`。这些测试证明合同、执行器、finalizer 和重放器的失败关闭行为符合预期，但不代替 `formal_r3` 的 60 份现场 raw result，也不构成算法或生产完成回执。

## 并行工作负载与隔离边界

- CAEOS 所有者进程当前为 `T (stopped)`；本轮不发送 `CONT`、`TERM`、`KILL`，不迁移、不接管，也不以 campaign 名义改变其状态。
- 当前可见 8 个 duplicate-audit workers；保持现状并计入资源背景，不为 campaign 清理或终止这些 worker。
- A09/50051 服务保持在线稳定；它是独立服务健康事实，不等于 A09 已通过本次统一 60 单元资格 campaign。
- `formal_r3` 必须继续复用其既有 run ID 和 checkpoint，不能以新轮次覆盖或拼接前两次 0/60 的失败结果。

## 后续闭环门

算法阶段只有在 `formal_r3` 实际达到 60/60、finalizer 生成且复核 `accepted=true` 的 formal receipt、权威 raw replay 对正式树返回完整且只读一致后，才允许进入 shared algorithm release gate。此后仍须把合格算法结果与新 NIC 的 native XDP 主路径、DPDK 回退路径、丢包、P99、资源、关键流覆盖和恢复证据共同接入生产 Pareto。

截至本快照，新 NIC 尚未到货或尚未完成 R0--R4 正式验收，XDP/DPDK 双后端状态保持 `hardware_pending`。所以当前不能声称整个流程闭环、生产联合最优或最终发布完成。
