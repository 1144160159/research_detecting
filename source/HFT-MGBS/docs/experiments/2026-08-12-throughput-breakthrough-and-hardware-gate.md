# 2.8 Mpps 瓶颈突破实验与硬件门

## 结论

当前 BCM57810 双口测试拓扑无法建立 12 Mpps R0 证据。TPACKET 的队列/IRQ 对齐已在
2.794 Mpps 实现零丢包和合格 P99/P999，但 pktgen 无法继续提高 offered；同一目标由
DPDK 单队列绕过内核后，最低 TX/RX 仍只有 2.570/2.569 Mpps，且 P99 达 522 us。
因此可以确认 Rust TPACKET 接收逻辑在已提供的 2.794 Mpps 内不是丢包瓶颈；
尚未提供 12 Mpps，不能据此排除 Rust 在目标负载下成为瓶颈。DPDK 结果进一步确认
当前单队列收发路径在约 2.57 Mpps 触顶。当前可验证的阻断是发生器能力与
BCM57810/bnx2x 单队列路径，最终 12 Mpps 捕获能力仍属未证明。

## 有限候选矩阵

| 候选 | Offered/最低 RX Mpps | 发/收 | 驱动/socket drop | P99/P999 us | 恢复 | 决策 |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| B1 fixed8, clone64, burst1, QM8 | 2.793908/2.791521 | 40,173,943/40,173,943 | 0/0 | 94/131 | 通过 | generator gate 失败 |
| B2 fixed8, clone64, burst8, QM8 | 2.794217/2.790743 | 41,691,559/41,691,559 | 0/0 | 93/126 | 通过 | generator gate 失败 |
| B3 rx-usecs48 | 未运行 | — | — | — | — | offered>=12 前提不成立 |
| DPDK Q1 target12, burst256 | 2.569692/2.569457 | 38,547,638/38,547,638 | 0/0 | 522.373/529.255 | 通过 | 速率和 P99 失败 |

B1/B2 实际只用了 3 个预算中的 2 个。DPDK 12 Mpps 使用独立的 release-gate 冻结配置，
不是对 B3 的替代，也没有据结果回改阈值。

## 证据

- B1：`/home/wangwt/task/datasets/replay/hft_tpacket_breakthrough_b1_20260812T111500Z`；
  acceptance/list SHA-256：
  `204c4ecbdda2e9cc1ceb840ab6d8a72b32fdaba30f5e8ecb96474c0289845dbf` /
  `f02c9337cd161c2942f49a1a2723c27bdc012bdb1497c5f50a5c95d43464bdf7`。
- B2：`/home/wangwt/task/datasets/replay/hft_tpacket_breakthrough_b2_20260812T113000Z`；
  acceptance/list SHA-256：
  `b833a63befbf8564f8702cb4b5ce8dc21e33c3845d488b04aa94093d79212b80` /
  `d80ce813e0a208bcba2567af02b1580bcddd5c1cbfe98c5bb8d0a4dd141a45ab`。
- DPDK：`/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260812T092747626930383Z`；
  acceptance/result/list SHA-256：
  `673ef84fd3f4e33fb3181df14257ed0739dc540f2f1b85c3e60a2d446467599a` /
  `c21249871b7bf9f33175a3355b8d2dcbe05796eec4318016ac25326dad76c088` /
  `618b6ecc66da9fc506a5136899ebd0d7dd912559a7cc2bec6d4e5bf7edaf157d`。

## 外部能力边界

- DPDK 官方 bnx2x PMD 文档明确列出 RSS、TSS 均不支持，因此当前单队列瓶颈不能靠
  增加 queue_count 扩展：[DPDK bnx2x PMD](https://doc.dpdk.org/guides/nics/bnx2x.html)。
- Linux 内核 AF_XDP 文档规定可以用 `XDP_ZEROCOPY` 强制零拷贝，否则绑定失败；新卡
  验收必须使用强制模式，不能把自动降级 copy 当作通过：
  [Linux AF_XDP](https://docs.kernel.org/networking/af_xdp.html)。
- Intel ice 内核驱动明确支持 XDP 和 AF_XDP zero-copy；DPDK ice PMD覆盖 E810 类
  10/25/50/100/200Gbps 设备并支持 RSS，可作为首个采购验证类别：
  [Linux ice driver](https://cdn.kernel.org/doc/html/latest/networking/device_drivers/ethernet/intel/ice.html)、
  [DPDK ice PMD](https://doc.dpdk.org/guides-25.11/nics/ice.html)。

上述资料只用于缩小硬件候选，不能替代本机三次 12 Mpps 零丢包实测。新硬件进入
`configs/capture_hardware_upgrade_gate_v1.json` 后，必须按 R0→R4 重新验收；在此之前
`full_pipeline_qualified=false`、`final_pareto_ingestion_allowed=false`。
