# TPACKET_V3 有限候选搜索与工程结论

## 结论

TPACKET_V3 + PACKET_FANOUT_HASH/QM 已完成 Rust 实现、构建与物理双口实测。后续
队列/IRQ 对齐修复已使它在约 2.794 Mpps 同时满足严格零丢包与 100/500 us 尾延迟门，
但发生器仍无法达到 12 Mpps headroom。因此当前 BCM57810 不存在满足全部硬约束的
最终生产 Pareto 点。

## 实现验证

- 新增 `tpacket_v3_fastpath_probe`：TPACKET_V3 mmap、每 worker 独立 ring、
  PACKET_FANOUT_HASH/QM、固定 CPU、借用式包处理、测试签名计数、软件时间戳 P99/P999、
  PACKET_STATISTICS、per-socket 混杂 membership 和原始 JSON。
- Rust 3 项单测、目标 clippy `-D warnings`、release build 通过；最终二进制 SHA-256：
  `a84fcd0e7c680c4b6d930535c0471e26e84898ee0090aefb9d2b269d3caab658`。
- 上游只读 `traffic-analysis-platform/rust` 未修改；其现有 14 个 warning 不归入 HFT
  源码修改。

## 结果矩阵

| 配置 | 实发/接收 | 驱动/TPACKET drop | 最低完整秒 | P99/P999 | 结论 |
| --- | ---: | ---: | ---: | ---: | --- |
| 默认 RX=453，4 worker，1 Mpps | 15,150,080 / 15,120,990 | 29,090 / 0 | 0.994252 | 2100/2758 us | 驱动丢包 |
| RX=4078，4 worker，1 Mpps | 15,150,080 / 15,150,080 | 0 / 0 | 1.009664 | 704/726 us | 功能通过、时延失败 |
| RX=4078，2 worker，1 Mpps | 15,150,080 / 15,150,080 | 0 / 0 | 1.009664 | 673/708 us | CPU 1.82 核、时延失败 |
| RX=4078，8-thread pktgen 上探 | 41,762,153 / 41,739,312 | 22,841 / 0 | 2.716999 | 49/64 us | 速率与零丢包失败 |
| RX=4078，fixed8/clone64/burst1/QM8 | 40,173,943 / 40,173,943 | 0 / 0 | 2.791521 | 94/131 us | 零丢包及时延通过，12 Mpps 失败 |
| RX=4078，fixed8/clone64/burst8/QM8 | 41,691,559 / 41,691,559 | 0 / 0 | 2.790743 | 93/126 us | 零丢包及时延通过，12 Mpps 失败 |

上探的平均实发约 2.784 Mpps；缺口 22,841 与 ens8f0 `rx_discards` 增量严格相等。
后续取消逐包随机化、使用 `PACKET_FANOUT_QM` 并对齐 8 路 IRQ/worker 后消除了该缺口，
但 burst=1/8 的 offered 都只有约 2.794 Mpps。pktgen 与既有 Rust
PACKET_TX_RING/AF_XDP COPY 都在约 2.8 Mpps 附近触顶，无法生成 12 Mpps 合格证据。

## 证据

- 4-worker 零丢包：
  `/home/wangwt/task/datasets/replay/hft_tpacket_v3_1m_rxring4078_20260812T091500Z`；
  acceptance/list SHA-256：
  `0dfbe4a192d1542218540a2b86757b84c0740d77b48e498251a668f453709ea6` /
  `723cb99c6f07bb38cb7f081dc96c3e11d7c75dad02e870f3645e79e6cc5180d2`。
- 2-worker 零丢包：
  `/home/wangwt/task/datasets/replay/hft_tpacket_v3_1m_rxring4078_w2_20260812T093000Z`；
  acceptance/list SHA-256：
  `3a098cb968a61d41e3c3685054bd77a77c7f5b8442bcf4b1e3afe66e248a9303` /
  `7d250b302ce9d2b1820160f10405e9da7f3057089e6f9328d942d14c35842ae3`。
- pktgen 上探：
  `/home/wangwt/task/datasets/replay/hft_tpacket_v3_pktgen_line_rate_20260812T100000Z`；
  acceptance/list SHA-256：
  `c0420fd4246fa7a39de7d6ebe2780314fe54dd921f963ec4175abee5de772bc1` /
  `35b7bc254873a7de2a4d3673d55ab735f4b33c1f582a450d1da9bb92f855d1c4`。
- QM/IRQ B1：
  `/home/wangwt/task/datasets/replay/hft_tpacket_breakthrough_b1_20260812T111500Z`；
  acceptance/list SHA-256：
  `204c4ecbdda2e9cc1ceb840ab6d8a72b32fdaba30f5e8ecb96474c0289845dbf` /
  `f02c9337cd161c2942f49a1a2723c27bdc012bdb1497c5f50a5c95d43464bdf7`。
- QM/IRQ B2：
  `/home/wangwt/task/datasets/replay/hft_tpacket_breakthrough_b2_20260812T113000Z`；
  acceptance/list SHA-256：
  `b833a63befbf8564f8702cb4b5ce8dc21e33c3845d488b04aa94093d79212b80` /
  `d80ce813e0a208bcba2567af02b1580bcddd5c1cbfe98c5bb8d0a4dd141a45ab`。
- 每轮结束均恢复 ens8f0 RX=453、promiscuity=0，pktgen 模块由本轮加载时已卸载。

## 停止规则

候选预算固定为 6 个后端分支，现已全部裁决，活跃候选为 0。继续微调 worker、block、
coalesce 或发生器线程不会弥合 2.8→12 Mpps 的倍数差距。下一工程变更必须是新增/更换
支持 native AF_XDP zero-copy 或成熟多队列 RSS DPDK PMD 的发生器/抓包网卡；换硬件
后复用相同 1→5→10→12 Mpps fail-closed 门，不重开无界算法搜索。
