# XDP fill ring 初始填充修复留存

## 问题现象

多队列 idle poll 修复使 0.05 Mpps 的 kernel P99 从 33,068 us 降至
30,449 us，但仍失败。进一步边界扫描中，0.02/0.03/0.04 Mpps 的 P99
分别为 16,333/24,353/29,604 us；抓包均零丢包、关键流覆盖均为 1.0，
单包处理 P99 仍为微秒量级，表现为 AF_XDP 入口后的排队而非解析饱和。

边界扫描汇总：
`/home/wangwt/task/datasets/replay/hft_xdp_load_boundary_20260730T105642059031272Z/summary.json`，
SHA-256 为
`9376b9c74f06e3b3c0f4f5a7f8d9a05d95f19e1a2aed9ad53217c69d1ec8379a`。

## 根因

每个 XSK 的 fill ring 容量为 2,048，UMEM 每队列有 4,096 帧，但启动时
复用了 receive batch=64 作为初始 fill 数量，导致每个队列只有 64 个
可供内核重定向的帧。运行中消费后补充 64 是合理的，启动时只预填 64
则没有建立设计容量，容易在突发下反复耗尽/唤醒并形成排队。

## 修改范围

- 启动阶段每队列按 `XSK_RING_SIZE=2048` 完整预填 fill ring。
- 正常消费后的补充仍使用冻结的 receive batch，避免过量临时分配。
- 将 refill 参数重命名为 `target_frames`，明确“初始深度”和“接收批量”
  是两个独立概念。
- UMEM 总帧数、ring 大小、清理顺序与 kernel-owned frame 跟踪不变。
- 不修改只读上游 `/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 验证计划

先完成 Rust 测试、release 构建和退出清理；再固定 0.05 Mpps、receive
batch=64 做单次 A/B。若仍失败，回到 0.02 Mpps 验证改动是否仅移动边界；
只有全部硬门通过才进入三重复验。

单次 A/B 目录：
`/home/wangwt/task/datasets/replay/hft_pdiag_20260730T110254929439950Z`；
组合证据 SHA-256 为
`ab3e66630989a8a69b1d0e5db65361ea5e00f0cdb0ceb540620f96b9a2554937`。
结果为 offered/received 757,523、capture drop=0、关键流覆盖=1.0，但
kernel P99/P999 为 35,511/41,705 us，内部特征入队 P99 为 5,622.843 us，
RSS 为 1,037,212 KiB。相对修复前多 fd poll 基线 30,449 us，P99 恶化
16.63%，且内部入队 P99 超过 5 ms 门。

因此该假设被拒绝，代码已恢复启动时按 receive batch=64 填充；不进入
0.02 Mpps 复测，也不进入 Pareto。保留本记录和失败证据，避免后续重复
尝试“加深缓冲等于降低延迟”。

## 性能影响与回退

每队列由内核持有的初始帧从 64 增至 2,048，8 队列共约 64 MiB packet
frame 数据区实际进入 fill 所有权；UMEM 的 128 MiB 预分配上限不变。
可能提高页驻留和启动时间，但应降低突发时 fill 饥饿。若 RSS 越界、清理
出现未归还帧、drop 增长或 P99 恶化，恢复 64 并保留失败证据。

上述回退条件已经触发并执行；当前有效实现恢复为 64。

## 遗留风险

该修复不解决 bnx2x generic XDP copy 的硬件上限，也不解决 0.10 Mpps
以上的 GPU 队列容量瓶颈。当前仍是 diagnostic-only，不能设置
`final_pareto_ingestion_allowed=true`。
