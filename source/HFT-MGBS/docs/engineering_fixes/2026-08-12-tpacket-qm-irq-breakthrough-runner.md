# TPACKET QM/IRQ 突破运行器修复记录

## 问题

原 pktgen 上探同时使用逐包随机四元组、4 路 `PACKET_FANOUT_HASH`，而两块 BCM57810
各有 8 个硬件队列，IRQ 又由 irqbalance 分散到 NUMA1 的物理核与 SMT sibling。
这使发生器生成、RSS/队列映射、IRQ 和用户态 worker 四层混在一个实验中，无法定位
约 2.8 Mpps 上限。

## 修复

- 新增 `scripts/run_tpacket_v3_breakthrough.sh`：8 个 pktgen TX queue 各使用一条
  固定 IPv4/UDP 流，取消逐包随机化，候选显式冻结 `clone_skb`、`burst` 与
  `rx-usecs`。
- 捕获改为 8 路 `PACKET_FANOUT_QM`，保留 skb `queue_mapping`，使硬件 RX queue
  与用户态 socket 的关系可观测。
- ens8f0 8 个 RX IRQ 固定 CPU 28--35；TPACKET worker 固定 36--43；ens8f1
  TX IRQ 与 pktgen thread 固定 44--51，均位于 NIC 本地 NUMA1 且不共享物理核。
- 运行前保存两口 16 个 IRQ affinity、RX ring、coalesce、链路、统计与模块状态；
  运行中保存 active/pre-restore affinity；清理期忽略二次 HUP/INT/TERM，恢复所有
  状态并生成 `runner_exit_status.env`。
- 派生回执同时绑定发收计数、驱动/socket drop、P99/P999、IRQ 稳定、主机资源和
  恢复结果；任何证据缺失都报错，不产生合格结论。

## 验证

- 本地合同测试 2/2、Python 编译、JSON 解析通过；远端 `bash -n` 与 Python 编译通过。
- B1/B2 均实现零丢包和合格时延，但 offered 只有约 2.794 Mpps；B3 的冻结触发条件
  offered>=12 Mpps 未成立，因此未运行。
- 两轮均确认 IRQ 未漂移、RX ring/coalesce/链路/模块完整恢复。

该修复提高了可解释性和 2.8 Mpps 下的零丢包能力，但不声称达到 12 Mpps，也不改变
`full_pipeline_qualified=false` 与 `final_pareto_ingestion_allowed=false`。
