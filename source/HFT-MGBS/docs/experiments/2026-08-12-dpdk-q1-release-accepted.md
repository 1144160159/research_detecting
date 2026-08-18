# DPDK Q1 1 Mpps 正式发布门验收

## 结论

`R0_DPDK_BNX2X_Q1_1.0_B128_RELEASE_V2` 已完成一次 fail-closed 正式运行，
派生回执判定 `runner_qualified=true`、`r0_capture_only_qualified=true`。
该结论只覆盖 BCM57810/bnx2x DPDK 单 RX 队列、64 B、1 Mpps、15 秒的
capture-only R0，不覆盖 10/12 Mpps、解析/特征/预算/A09 全链路或最终 Pareto。

## 冻结输入

- capture/replay PF：`0000:cb:00.0` / `0000:cb:00.1`
- 队列：Q1；burst：128；帧长：64 B；目标：1.0 Mpps
- main/RX/TX CPU：50/52/54；SMT 同胞：106/108/110
- release 二进制 SHA-256：
  `3c655ef3684f8157e52d12a89157a6c1c5f0d586fe493d610b60a2fc796ec0a6`
- 冻结配置 SHA-256：
  `07a553d97a262eb66f294a389961e7f967e4a660a8487b31437ef6bffb20f064`
- runner SHA-256：
  `c2f3945a05f7d59ed683dde8f1ac6ac6620a3a4cc0606418b7a79ea00a076d08`

## 正式数据

证据目录：
`/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260812T075417740346047Z`

| 指标 | 正式观测值 | 判定 |
| --- | ---: | --- |
| 完整 1 秒窗口 | 15 | 通过 |
| TX 最低窗口速率 | 1.009920 Mpps | 通过 |
| RX 最低窗口速率 | 1.009927 Mpps | 通过 |
| 发送/接收包数 | 15,150,080 / 15,150,080 | 通过 |
| 收发差值 | 0 | 通过 |
| `imissed/ierrors/rx_nombuf/oerrors` | 0/0/0/0 | 通过 |
| P50/P99/P999 | 9.184/22.346/82.223 us | 通过 |
| 最大时延 | 415.045 us | 观测 |
| 进程 CPU | 0.97 核 | 通过 |
| 最大 RSS | 40,360 KiB | 通过 |
| HugePage | 1 GiB | 通过 |
| 墙钟附加开销 | 3.880 s | 通过 |

## 证据与恢复

- `acceptance.json` SHA-256：
  `1e7a68009c04e1165a14a2784ba92b6d52eddcb728cb3e06fafe531331a5383e`
- `evidence_sha256_base.txt` 与 `evidence_sha256_complete.txt` SHA-256 均为：
  `2ed05399a2fed3948e3d5bbd05920266e081df420729ae26bade678f5abfbbbe`
- 两份清单已在远端独立执行 `sha256sum -c` 并全部通过。
- acceptance 状态中的原始运行、恢复、validator、base/complete 哈希检查均为 0；
  `evidence_complete_before_hash=true`、`hash_checks_verified=true`、
  `restoration_verified=true`。
- 运行后独立复核：ens8f0/ens8f1 均恢复 `bnx2x`、UP/LOWER_UP、10GbE、
  carrier；node0/node1 两种 HugePage 数均为 0，无 UIO 模块或 HFT DPDK 进程残留。

## 能力边界与停止规则

- 官方 bnx2x PMD 能力边界不支持 RSS/TSS；历史 Q2 实测也始终为
  `rx_queue_packets=[15150080,0]`，因此 Q2 多 RX 分支正式停止，不继续通过参数扫描
  制造候选。
- Q1 的 1 Mpps 正式通过只能证明当前单队列 DPDK capture-only 可逆可运行；它没有
  12 Mpps capture headroom，不能进入最终 Pareto。
- 当前硬件上的下一项有界候选固定为非破坏性
  `TPACKET_V3 + PACKET_FANOUT_HASH/QM`。若该候选仍无法跨过发生器/抓包硬门，工程
  结论将收敛为更换支持 native AF_XDP zero-copy 或成熟多队列 RSS PMD 的网卡。

