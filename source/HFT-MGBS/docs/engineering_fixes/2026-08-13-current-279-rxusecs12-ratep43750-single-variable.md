# current-2.79：rx-usecs12 下的 pktgen 等速单变量候选

## 问题与证据

固定 64 字节解析器在 `rx-usecs=24` 的单轮完整秒最低值为
`2.791566 Mpps`，但 capture NIC `rx_discards=1774`，全部集中在队列 5。
将唯一变量改为 `rx-usecs=12` 后，丢弃降为 `526`，但迁移到队列 3，完整秒
最低值为 `2.789465 Mpps`。两个运行的 pktgen 实际总速率分别为
`2,794,730 pps` 和 `2,792,786 pps`，队列速率均呈现约 `395 kpps` 与
`334 kpps` 两档，变异系数约 `7.64%`。这说明剩余丢弃随突发热点队列漂移，
而不是固定 IRQ 核饱和；IRQ 核仍约有 88% 以上空闲。

## 关键语义修正

Linux 5.10 `net/core/pktgen.c` 的 `ratep V` 实现为
`delay=floor(1,000,000,000/V)`。发送循环每等待一次会执行一次 `burst`；本候选
保留 `burst=8`，因此不能写 `ratep 350000`，否则目标将接近每队列
`2.8 Mpps`。正确值是 `ratep 43750`：回读 `delay=22857 ns`，理论有效速率约
`43750 * 8 = 350000 pps/queue`，8 队列约 `2.800 Mpps`。

## 唯一变量与不变量

- 唯一负载变量：每个 replay pktgen device 增加 `ratep 43750`。
- 固定：`rx-usecs=12`、`rx ring=4078`、8 个 generator/IRQ/worker 映射、
  `clone_skb=64`、`burst=8`、traffic-v2 144 flows/queue、`flowlen=36`、
  QM fanout、fixed64 binary SHA-256
  `6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca`。
- `ratep`、候选身份和观测硬门以外的配置/runner 内容必须与 rx-usecs12
  基线机械一致；合同测试会反向规范化并逐字比较。

## 唯一一轮的硬门与停止规则

执行前必须通过本地/远端合同测试、`bash -n`、三个信任根哈希、安全预检和
既有互斥/恢复门。运行时/运行后必须同时满足：

1. 8 个 configured/current device 都回读 `delay=22857`、`burst=8`、
   `clone_skb=64`，且 pktgen `errors=0`；
2. 每队列实测 `345000..355000 pps`，8 队列合计不低于 `2,800,000 pps`；
3. 至少 15 个完整一秒窗口，最低值不低于 `2.79 Mpps`；
4. NIC 每队列及总 `rx_discards`、packet socket drop/freeze、feature/key queue
   drop、parse rejection 全部为 0；capture/internal delivery lossless 和所有
   worker error-free 为真；
5. QM flow-affinity、fixed64 fast/fallback 守恒、GPU 既有流水线门及主机恢复门
   全部通过。

本候选保持 traffic-v2 的 `flowlen=36`。其已知流关闭密度不足既有
`closed_flows >= full_windows * 1000` 全流水线门，因此 runner 最终 RC 仍可能
为 1；这不覆盖 `pktgen_rate_gate.json`、`nic_rx_discards_gate.json` 和
`capacity_capture_gate.json` 对速率/抓包容量的独立判定。只有后续把等速设置与
`flowlen=1` 及最终证据 binary 合并后，才测试完整闭环资格。

任一硬门失败即停止，不尝试 `rx-usecs=6`，也不把本轮诊断写成生产资格证据。
若本轮失败，2.79 不是当前环境下的可验证无丢上限；下一步应按相同闭环合同在
较低目标上取得连续 3 次零丢证据，而不是继续堆叠未隔离变量。

## 唯一轮结果（2026-08-13）

证据目录：
`/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T142500Z_fixed64_rxusecs12_ratep43750_capacity_r1`。
冻结 runner/config/binary 的 SHA-256 分别为
`622a9e2ed836b22270fc1dce1732a0d871dffd19b05b12f9f7e4695888ff081d`、
`b5a1cacdfdb8046edfffec825d0073d91d548a7e23c8081430cc85f2a97c4655`、
`6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca`；
证据清单自校验通过，runner RC=1，恢复验证通过。

8 个队列均正确回读 `delay=22857`、`burst=8`、`clone_skb=64`，实测速率为
`339568, 339379, 339467, 339459, 339588, 339600, 339463, 339453 pps`，
合计 `2,715,977 pps`。队列变异系数从无限速运行的约 `7.64%` 降至
`0.0217%`，证明等速确实消除了热点队列偏斜；但 Linux pktgen 的调度/发送开销
使实际速率低于名义值。18 个完整秒中，前 8 个约为 `2.800 Mpps`，随后降至
`2.617..2.727 Mpps`，最低 `2.616893 Mpps`，所以 2.79 速率门明确失败。

这次运行的零丢侧证据为：before/after NIC 总及 8 队列 `rx_discards` 增量均为
0；packet socket drops/freeze、feature/key queue drops、parse rejection 均为
0；capture/internal delivery lossless 和 all-workers-error-free 均为真。GPU
`222/222` 批成功、`1701/1701` flow scored；fixed64 fast path 处理
`50,321,531` 包、fallback 0；QM 有 1160 个 distinct flow、跨 worker collision
为 0。由于速率门在预期的流密度门之前失败，本轮仍不是完整流水线资格结果。

按停止规则不再尝试 `rx-usecs=6`，也不重跑该候选。当前证据不能把 2.79 写成
“零丢可验证上限”。如果必须先形成可重复的当前硬件基线，建议以 `2.60 Mpps`
作为首个三连零丢验证目标；它是下一轮的保守验证目标，不是已证明的最大值。

本轮还暴露了证据可观测性问题：旧 runner 在首个队列速率越界时立即退出，未写
`pktgen_rate_gate.json`。本地后续版本已改为先收集全部 8 队列并写失败 receipt，
再 fail-closed；冻结证据仍保留原 runner 哈希，未被回填或篡改。
