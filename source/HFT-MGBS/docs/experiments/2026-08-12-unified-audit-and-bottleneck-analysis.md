# 统一审计与抓包瓶颈归因实验

## 目标

把 DPDK 12 Mpps、TPACKET B1/B2、算法候选、硬件迁移门和当前 GPU 运行态放入
同一个 fail-closed 判定，并回答当前 2.6--2.8 Mpps 上限究竟能证明什么。实验只读取
既有封存 JSON 和清单；未重新解绑双 PF、未修改网卡，也未把远端结果复制到本地。

## 输入

| 证据 | SHA-256 |
| --- | --- |
| DPDK 12 Mpps result | `c21249871b7bf9f33175a3355b8d2dcbe05796eec4318016ac25326dad76c088` |
| DPDK 12 Mpps acceptance | `673ef84fd3f4e33fb3181df14257ed0739dc540f2f1b85c3e60a2d446467599a` |
| TPACKET B1 acceptance | `204c4ecbdda2e9cc1ceb840ab6d8a72b32fdaba30f5e8ecb96474c0289845dbf` |
| TPACKET B2 acceptance | `b833a63befbf8564f8702cb4b5ce8dc21e33c3845d488b04aa94093d79212b80` |
| 瓶颈决策合同 | `82e1835f7be6b3abf348a1a0fa3b2463bc2fd64c0a71d0aa18f10aeb1543a060` |

四份运行回执均另外由 `release_manifest_v2.json` 绑定各自完整证据清单；分析器不接受
主机恢复失败、封存状态损坏或计数不能精确对账的观测。

## 结果

| 路径 | 最低 offered/RX | 丢包 | 归因 | 12 Mpps |
| --- | ---: | ---: | --- | --- |
| TPACKET B1 | 2.793908/2.791521 Mpps | 0 | 本轮发生器受限 | 未证明 |
| TPACKET B2 | 2.794217/2.790743 Mpps | 0 | 本轮发生器受限 | 未证明 |
| DPDK Q1 target12 | 2.569692/2.569457 Mpps | 0 | 单队列收发路径受限 | 失败 |

聚合输出为 `analysis_valid=true`、`eligible_observations=3`、
`generator_limited=true`、`single_queue_path_limited=true`、
`capture_limited=false`、`target_unproven=true`。这里的 `capture_limited=false` 仅表示
三轮已提供负载内没有捕获丢包或“TX 已到 12、RX 跟不上”的证据，不代表 12 Mpps
捕获能力合格。

分析证据位于
`/home/wangwt/task/datasets/replay/hft_capture_bottleneck_analysis_v1_20260812.json`，
SHA-256 为 `2a63f2576cf66865dbf711b5a1964d4cd54f047c0cb4c94f95afcb5742567ddd`。

## 统一发布判定

统一审计直接核验了 8 份配置、4 份 acceptance、4 份完整清单和全部已执行轮次的恢复：

- 离线 A09 候选自洽：通过；
- 当前抓包可行集：空；
- 已执行物理轮次恢复：通过；
- 三次 12 Mpps R0：缺失；
- GPU 现役运行身份：未验证；
- 同一正式 R3 窗口的资源、关键流与生产回退：待补；
- R1、R2、R3、24h、72h：待补。

因此 `audit_complete=true`，但 `production_release_accepted=false`、
`full_pipeline_qualified=false`、`final_pareto_eligible=false`。审计证据位于
`/home/wangwt/task/datasets/replay/hft_unified_release_audit_v1_20260812.json`，
SHA-256 为 `d6bb2afec89320c07853060856706a2346ccced2e7324971c5c7b4efed38b013`。

## 决策

当前网卡上的 Rust/TPACKET 优化已经把 2.794 Mpps 内的丢包消除，但发生器没有提供
目标负载；DPDK 绕过内核后仍受单队列路径限制。继续调整同一卡上的 burst、block、
coalesce 或 worker 数无法形成 12 Mpps 合格证据。下一实验入口固定为：

1. 独立发生器先证明 64 B offered 至少 15 Mpps，且不共享当前适配器包处理预算；
2. 新抓包网卡强制 native XDP 与 `XDP_ZEROCOPY`，拒绝自动 copy 降级；
3. 同时验证 DPDK RSS/TSS 和至少 8 RX/TX 队列；
4. R0 三次 12 Mpps 零丢包通过后，才依次解锁 R1--R4。

在硬件/发生器条件到位前，不新增吞吐微参数候选，不改变现有硬门。
