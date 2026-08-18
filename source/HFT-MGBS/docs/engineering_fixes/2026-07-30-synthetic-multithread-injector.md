# 64B 多线程发生器整改留存

## 问题现象

sharded busy-poll capture 在 0.5 Mpps 已达到 offered=received、drop=0、
raw P99/P999=11/18 us。升档到 1 Mpps 时抓包仍收到发生器实际发送的全部
11,436,254 包且 raw P99=11 us，但旧 PCAP injector 的 1 秒最低速率只有
0.7473 Mpps，失败门仅为 `target_load`。因此此时瓶颈已从抓包转移到单线程
PCAP 读取、分段、构帧和 sendmmsg 的发生器。

1 Mpps 目录：
`/home/wangwt/task/datasets/replay/hft_r0_xdp_20260730T125032986517886Z`，
summary SHA-256 为
`ad375c7317560e9f5fdcb6f5d8fde8e586d760ff786429bd090b5aca698bd284`。

## 修改范围

- 新增 Rust `synthetic_packet_injector`，直接生成冻结的 64B
  Ethernet/IPv4/UDP 包，不在计时窗口读取 PCAP、分段或分配 payload。
- 预构建每 worker 的 256 包 `mmsghdr/iovec`，循环复用，热路径无构帧分配。
- 8 个 TX worker 固定到 NUMA node 1 的 CPU 44--51，与 capture worker
  36--43 隔离。
- 生成不同 IPv4/UDP 五元组，使硬件 RSS 能覆盖 8 个 RX 队列。
- 启用 `PACKET_QDISC_BYPASS`，每线程独立 AF_PACKET TX socket。
- 每线程独立限速和 1 秒窗口，汇总 offered、最低 Mpps、CPU 和 EAGAIN/
  ENOBUFS 重试。
- 不修改只读上游 `/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 验证计划

先替换 R0 脚本发生器并重跑 1 Mpps；通过后生成 5/10/12 Mpps 冻结配置，
逐档执行。若 1 Mpps 仍未达到，下一步改为 `PACKET_TX_RING` 或 DPDK TX，
不把发生器不足误报为抓包上限。

## 性能影响与回退

发生器最多占 8 个专用 CPU，且只在诊断运行中启动。任一线程 pin、socket、
sendmmsg 或汇总失败都会退出；脚本恢复 GRO/LRO 并检查 XDP 残留。真实 PCAP
注入器继续保留给语义/特征实验，synthetic 只证明小包吞吐，不能替代质量
证据。

## 遗留风险

AF_PACKET TX 即使多线程也可能受 qdisc、驱动锁或单适配器限制，10 Mpps
可能仍需 TX_RING/DPDK/外部硬件流量仪。静态 256 五元组不代表高 churn
真实流量，R2 还需独立 flow-profile 实验。
