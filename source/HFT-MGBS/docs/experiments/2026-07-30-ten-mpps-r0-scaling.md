# 10 Mpps R0 抓包快路径逐级实验

## 边界

- 物理机：`10.0.5.8`
- 发送口：`ens8f1`
- 接收口：`ens8f0`
- 后端：`xdp-skb`，仅作为当前 `bnx2x` 网卡上的诊断后端
- 流量：Rust 多线程合成 Ethernet/IPv4/UDP 64 B 帧，改变五元组以覆盖 8 个 RSS 队列
- 抓包：8 个独占 AF_XDP 队列工作线程，借用 UMEM 回调、忙轮询、NUMA 固定 CPU
- 门禁：实发速率达到目标、发送包数等于接收包数、网卡丢包为 0、原始 P99 不超过 100 us、P999 不超过 500 us
- 所有结果均为 R0 抓包快路径诊断，`full_pipeline_qualified=false`、`final_pareto_ingestion_allowed=false`。

## 结果

| 目标 | 证据目录 | 最低实发 Mpps | 发送/接收差值 | 网卡丢包 | P99/P999 (us) | CPU 核均值 | R0 |
|---:|---|---:|---:|---:|---:|---:|---|
| 0.5 | `hft_r0_xdp_20260730T124827393434529Z` | 0.504954 | 0 | 0 | 11/18 | 7.881 | PASS |
| 1.0（旧 PCAP 发生器） | `hft_r0_xdp_20260730T125032986517886Z` | 0.747320 | 0 | 0 | 11/21 | 7.830 | FAIL：发生器未达目标 |
| 1.0（Rust 合成发生器） | `hft_r0_xdp_20260730T131042755573282Z` | 1.009971 | 0 | 0 | 10/14 | 7.878 | PASS |
| 5.0（`sendmmsg`） | `hft_r0_xdp_20260730T131338121633352Z` | 2.655573 | 163,937 | 297,124 | 2,904/8,591 | 7.508 | FAIL：TX 与 RX 均触顶 |
| 5.0（`PACKET_TX_RING`，TX 48 us） | `hft_r0_xdp_20260730T132028906367179Z` | 2.750788 | 11 | 22 | 22/29 | 7.492 | FAIL：TX descriptor 触顶 |
| 5.0（`PACKET_TX_RING`，TX 24 us） | `hft_r0_xdp_20260730T132538853911361Z` | 2.680883 | 0 | 0 | 17/23 | 7.455 | FAIL：未达目标 |
| 5.0（`PACKET_TX_RING`，TX 0 us） | `hft_r0_xdp_20260730T132703740488898Z` | 2.680703 | 0 | 0 | 16/22 | 7.438 | FAIL：未达目标 |
| 5.0（AF_XDP TX COPY-mode） | `hft_r0_xdp_20260730T133857824025230Z` | 2.778831 | 0 | 0 | 13/23 | 7.687 | FAIL：208,374,956 次 TX stall |

## 当前分析

旧的单路径 PCAP 回放器是 1 Mpps 前的首个瓶颈，不是抓包侧丢包瓶颈。独立 CPU 上的多线程、预构造批量发送器解除该限制后，1 Mpps R0 完整通过。

第一轮 5 Mpps 表明 `sendmmsg` 发生器只有约 2.79 Mpps 平均能力且存在大量套接字重试；同时 generic XDP 接收也出现丢包和毫秒级排队。先以 `PACKET_TX_RING` 消除发生器开销，再重跑 5 Mpps。只有发生器稳定实发达到目标时，才能把剩余失败归因到链路/驱动/接收架构；不能跨级宣称 10 Mpps 能力。

`PACKET_TX_RING` 将接收 P99/P999 恢复到 22/29 us，但发送端仍只有约 2.82 Mpps，并在所有 8 个 TX 队列上累计新增 2,474,594 次 exhaustion。后续仅验证 TX coalescing 24/0 us 两个候选；若仍失败，则 generic/AF_PACKET 路径按停止规则淘汰。

TX coalescing 24/0 us 均实现零丢包，但最低实发速率都只有约 2.681 Mpps，低于保持 48 us 时的 2.751 Mpps。接口在每次实验退出时均恢复为 48 us。该微参数分支停止，不再扩大搜索空间。

AF_XDP TX COPY-mode 仍只有约 2.79 Mpps 平均能力，最低 1 秒速率 2.778831 Mpps，并出现 208,374,956 次 TX ring stall。接收侧保持零丢包且 P99/P999 为 13/23 us。结果证明 Rust 构包、AF_PACKET 系统调用和 qdisc 都不是剩余瓶颈；限制位于 `bnx2x` Linux/generic 数据路径。5/10/12 Mpps 不再在该路径重复。

## 2026-07-31 DPDK 1 Mpps 首次有效数据面

- 证据：
  `/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260731T013817616983065Z`
- B256、64 B、15 秒；发送和接收均为 `15,150,080` 包，差值 0。
- 最低 1 秒 TX/RX 为 `1.009976/1.009826 Mpps`；`imissed/ierrors/rx_nombuf`
  均为 0。
- P50/P99/P999/max 为
  `17.648/119.023/465.776/507.228 us`。
- 唯一硬门失败项为 `end_to_end_p99`；不能升级 5 Mpps。
- 回退完整：`restoration_verified=true`，两口恢复 bnx2x/10GbE UP，
  hugepage=0、运行前缀文件=0、UIO 未加载。
- 下一受控候选为 B128；不放宽 100 us 阈值。仅当 B128 仍失败时才允许
  测试 B64。

### B128 胜出

- 证据：
  `/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260731T014119532263589Z`
- 发送/接收均为 `15,150,080` 包，差值 0；最低 1 秒 TX/RX 为
  `1.009976/1.009937 Mpps`。
- `imissed/ierrors/rx_nombuf=0`，P50/P99/P999/max 为
  `9.201/81.135/412.149/459.276 us`。
- `r0_capture_only_qualified=true`，B128 进入 5 Mpps；B64 不再执行。
- 退出后 `restoration_verified=true`、hugepage=0、运行前缀文件=0。

### 5 Mpps 单队列停止

- 证据：
  `/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260731T014313443709656Z`
- 单队列 B128 最低 TX/RX 仅为 `2.569675/2.569659 Mpps`，两个线程均
  接近占满一核。
- 总发送/接收均为 `38,547,939`，差值 0；
  `imissed/ierrors/rx_nombuf=0`。
- P99/P999 为 `475.742/480.434 us`，硬门失败为
  `target_load/end_to_end_p99`。
- 单队列分支停止。下一且唯一的结构性扩展是 Q2/RSS；Q2 不通过即不执行
  10/12 Mpps。

## 2026-07-31 Q2/RSS 有界实验与停止结论

### 环境干扰与 RT 候选

多队列二进制首次 Q1 回归
`hft_r0_dpdk_20260731T020124813509403Z` 与一个占用约 83 核的外部 pytest
任务重叠，出现 51,935 个 `imissed/rx_nombuf` 和 9.52 ms 最大时延。未停止该任务；
任务自然结束后，Q1/RT0
`hft_r0_dpdk_20260731T022626737596943Z` 恢复为零丢包且 P99/P999
`82.356/441.984 us`，排除了多队列代码的 Q1 功能回归。

RT10 候选 `hft_r0_dpdk_20260731T022059475661619Z` 在 worker 就绪前失败，
`RLIMIT_RTPRIO=0` 且 `chrt -f 10` 返回 `Operation not permitted`。现有脚本已把
RT capability 检查移到 PF 解绑前；RT10 被拒绝，不修改系统限制。

### Q2 能力修复与运行

第一次 Q2 初始化
`hft_r0_dpdk_20260731T022745794651819Z` 被 ethdev 拒绝：
bnx2x `flow_type_rss_offloads=0`，而 shim 请求 IPv4 UDP RSS `0x20`。
HFT-MGBS 内形成两个可哈希实验补丁：补报 PMD 已消费的 UDP RSS 位，并把
`sc->udp_rss` 读取移动到 `bnx2x_dev_configure()`。Cargo 同时增加外部 DPDK
manifest/静态库变化追踪，避免复用旧二进制。

| 目标/夹具 | 证据目录 | 最低 TX Mpps | 发收差值/丢包 | RX 队列包数 | P99/P999 (us) | 结论 |
| --- | --- | ---: | ---: | --- | ---: | --- |
| Q2/5 Mpps，实验 PMD | `hft_r0_dpdk_20260731T024226277475329Z` | 2.590801 | 2,833/2,833 | `[38886459,0]` | 1066.602/1073.565 | FAIL |
| Q2/1 Mpps，UDP RSS 时序修复 | `hft_r0_dpdk_20260731T024920052633840Z` | 1.009974 | 0/0 | `[15150080,0]` | 129.209/814.189 | FAIL |
| Q2/1 Mpps，双 PF 实际 MAC | `hft_r0_dpdk_20260731T025306882795396Z` | 1.005139 | 0/0 | `[15150080,0]` | 130.182/827.269 | FAIL |

最后一轮以 `18:c0:09:1c:53:69` 为目的 MAC、以
`18:c0:09:1c:53:6b` 为源 MAC，排除了未知目的 MAC 混杂路径；queue 1 仍为 0。
因此本机 BCM57810 + DPDK 25.11.2 bnx2x 多 RX 被拒绝。Q2/5 不再重跑，
Q4/10 Mpps 和 12 Mpps 均不执行。

### 默认回退与最终稳定回归

失败补丁保留为显式实验候选，但 bootstrap 默认
`HFT_ENABLE_EXPERIMENTAL_BNX2X_RSS=NO` 并逆序撤销补丁。活动 DPDK 已恢复原始
已校验源码，build manifest SHA-256
`29436d1b20abeb70ea0758470086cacc436245e127ffc16824105bab134e5143`。

最终 Q1 稳定证据：
`/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260731T025831490425073Z`。

- 发送/接收均为 `15,150,080`，差值与 DPDK/NIC 丢包均为 0。
- 最低 1 秒 TX/RX `1.009976/1.009962 Mpps`。
- P50/P99/P999/max `9.215/81.802/438.530/467.053 us`。
- `r0_capture_only_qualified=true`，但
  `full_pipeline_qualified=false`、`final_pareto_ingestion_allowed=false`。
- 结果 SHA-256：
  `9a1769961de66610b5406450d07b12c7a60fb73f9b7a4da5fa7f7cf2ae9b9447`；
  清单内全部证据已校验。

最终工程结论不是“Rust 已达到 10 Mpps”，而是“当前硬件/驱动下 Rust DPDK
Q1/1 Mpps 通过，单队列约 2.57 Mpps 触顶，多 RX 实测不可用”。若目标保持
10 Mpps，需要先更换经验证的多队列/zero-copy 抓包硬件或驱动，再重启逐级实验。

## 2026-07-31 双 PF 授权重复验证

使用另一组通过物理核与 SMT 空闲检查的 NUMA 1 CPU
`main=53/RX=44/TX=55`，Q1/B128/1 Mpps 再次实现 15,150,080 包发收一致、
零 DPDK/NIC 丢包、最低 TX/RX `1.009959/1.009965 Mpps`，P99/P999
`81.224/434.806 us`。5 Mpps 最终 CPU 空闲复检未同时达到 95%，因此在 PF
解绑前停止，runner 未启动且没有新增 5 Mpps 测量。完整证据、清单哈希、资源
观测和回退状态见
[`2026-07-31-dpdk-dual-pf-authorized-repeat.md`](2026-07-31-dpdk-dual-pf-authorized-repeat.md)。
该重复验证不改变 `full_pipeline_qualified=false` 与
`final_pareto_ingestion_allowed=false`。
