# 当前环境 10 Mpps 瓶颈突破执行结论

## 结论

2026-08-12 已在 `10.0.5.8` 对 BCM57810 双 PF 执行独立 `testpmd` 容量隔离、
Rust/DPDK 热路径优化构建和 1 Mpps 安全回归。当前硬件/驱动组合没有达到
10 Mpps：成熟 `testpmd` Q1 的 12 个严格重叠窗口中，TX 最低为
2.569706 Mpps，RX 最低为 2.569691 Mpps。该值与旧 HFT Rust Q1 的约
2.57 Mpps 重合，故 4 倍差距不再归因于 Rust FFI、模板索引或逐批统计，而定位为
当前 bnx2x 单队列数据面边界。

这不是“10 Mpps 已完成”。当前可验证完成的是：软件热路径和恢复闭环在 1 Mpps
安全门通过；10 Mpps 在现有 BCM57810/bnx2x 路径上被实测否决。

## 独立容量隔离

- runner：`scripts/run_dpdk_testpmd_capacity.sh`；
- Q1 冻结合同：`configs/dpdk_testpmd_capacity_10mpps_v1.json`；
- 远端证据：
  `/home/wangwt/task/datasets/replay/hft_dpdk_testpmd_capacity_20260812T121024592199226Z`；
- 12 个使用窗口的 TX/RX 均稳定在约 2.5697 Mpps；
- 最终标准计数 `RX-missed/RX-errors/RX-nombuf/TX-errors` 全为 0，错误类 xstats
  全为 0；
- `capacity_qualified=false`，仅错误为 `rx_target_capacity/tx_target_capacity`；
- 恢复账本 13/13 通过，`restoration_verified=true`；
- `capacity_result.json` SHA-256：
  `c315c185eefd9d69bfecd1d91c221d4bf451bbfd9f98c5e7a69efcb57867aa1f`；
- `acceptance.json` SHA-256：
  `df44609b2fbc12578f87b41a169366c42976f1fd3894b4931c49272f35b652bf`；
- 完整证据清单 SHA-256：
  `528364f35758ad84a7f9d1a0690342b48950e7c745a14a6506b9aa6cdeee0eba`。

历史 Q4 候选曾根据 RX queue1 为 0 收敛为 TXQ4/RXQ1，但后续源码终审确认 stock
bnx2x 明确拒绝 `nb_tx_queues > nb_rx_queues`；该候选未进入数据面且现已在任何 PF
变更前永久拒绝。此前所有尝试也均在 5 次 1 秒、含 SMT sibling 的 5% CPU 空闲门被阻断，
日志明确 `no PF was mutated`。宿主机存在 ClickHouse、Java、Kubernetes 等正常
负载；本轮没有迁移、停止或降权这些服务，也没有降低门限制造不可复现实验。

最后一次 CPU-only V2 冻结合同使用 RX 45/46、TX 51/30/31/32/37；非变更预检
仍因 sibling CPU101 峰值 88.17%、CPU102 峰值 6.06% 而失败，证据目录为
`/home/wangwt/task/datasets/replay/hft_dpdk_testpmd_capacity_20260812T135350462128488Z`。
因此执行矩阵按“最后一次有界重试”停止；双 PF 未解绑，独立复核 bnx2x、接口 UP
以及 node0/node1 HugePage=0。

## Rust 热路径整改与运行验证

本轮仅修改 HFT-MGBS 自有 Rust/DPDK 代码，未修改只读上游
`traffic-analysis-platform/rust`：

- 64 B 模板索引使用 power-of-two mask 和定长复制，其他帧长保留通用途径；
- TX 分离 `prepare_calls/alloc_fail/tx_calls/tx_zero/tx_partial/tx_full`；
- RX 分离 `rx_polls/rx_nonzero/rx_zero`；
- 输出驱动实际 descriptor 和 mempool 前后快照；
- 连续空轮询每 64 次检查时间/窗口，独立 watchdog 保留。

远端 Rust 1.93 的 `cargo test` 13/13、Clippy 和 release 构建通过。二进制
SHA-256 为
`0b7a85fe3194636a03d2ce3a1fae461ce3e63f215c81ef8a32d603574b6ef038`。
独立冻结的 1 Mpps/B256 安全回归证据位于：

`/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260812T123553090231277Z`

关键结果：

- 15/15 个完整 TX/RX 窗口最低均为 1.00992 Mpps；
- offered/received 均为 15,150,080，packet gap=0；
- `imissed/ierrors/rx_nombuf/oerrors=0`；
- P99=14.4146 us，P999=132.1932 us；
- TX 59,180 个 burst 均 full，`alloc_fail/tx_zero/tx_partial=0`；
- 两个端口请求/实际 RX/TX descriptor 均为 1024；
- `runner_qualified=true`、`r0_capture_only_qualified=true`、恢复账本 12/12；
- `result.json` SHA-256：
  `2745d99a2bf78e027af86896b5aa955e20edbd177a643f950268532422898136`；
- `acceptance.json` SHA-256：
  `f5ac40eb9b9f781369d88098a21f35aa148551ceb8780d7e4cd4d93fdd19b604`；
- 完整证据清单 SHA-256：
  `889b593e01538f4d58c7a72046e50ba8fdf42ce4f778c45ac1407ec254147dd0`。

## 达到 10 Mpps 的工程落地决策

现有文档和实测已经裁决所有当前分支：bnx2x 不提供 native XDP，generic
`xdp-skb` 不是零拷贝；DPDK bnx2x 没有可用的成熟 RX RSS/TSS，Q2 历史实验也只有
queue0 收包；TPACKET/pktgen 在约 2.794 Mpps 触顶。继续调整 Rust burst、mempool
cache、coalesce 或 worker 数不能弥合 2.57/2.79 到 10 Mpps 的倍数差距。

若暂不更换捕获 NIC，唯一仍有判别价值的 10 Mpps 接收实验，是保留 ens8f0 的
bnx2x 驱动和既有 TPACKET_V3/QM8/IRQ/worker 冻结配置，由另一台独立 10/25GbE
线速发生器输入 64 B、至少 12 Mpps 流量，执行 15 秒×3。该实验可以判定内核接收
路径能否达到 10 Mpps；本机双 PF testpmd 只能诊断硬件/PMD 容量，不能替代独立
发生器，也不能证明 XDP/TPACKET 的 10 Mpps 能力。

实际 10 Mpps 的下一部署基线固定为：

1. 新增或更换支持 native XDP、AF_XDP zero-copy 和成熟多队列 RSS 的捕获 NIC；
2. XDP 作为首选数据面，至少四个独立 RX queue/worker，均位于 NIC 本地 NUMA；
3. 使用不共享当前适配器和宿主 CPU 预算的独立发生器；
4. 依次执行 1、5、10、12 Mpps，每档 15 秒，10/12 Mpps 各重复三次；
5. 每次均要求 packet gap、NIC/套接字 drop 为 0，P99/P999、CPU/内存和主机恢复
   全部通过；任何一次失败即停止，不做外推。

若必须继续使用当前物理机，先安排维护窗口，为 stock TCP RSS 对称 Q2/1 Mpps
诊断保留五个稳定 NUMA1 物理核及其 sibling。只有两条 RX/TX 软件队列各占至少
40%、零错误和完整恢复通过，才允许继续 Q2/5 Mpps；非对称 TXQ4/RXQ1 永不再运行。
