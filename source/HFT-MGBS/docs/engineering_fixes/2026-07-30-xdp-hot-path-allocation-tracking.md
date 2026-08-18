# XDP 热路径分配与帧所有权跟踪修复留存

## 问题现象

现有 `xdp-skb` 在 0.02 Mpps 已出现 16.333 ms P99，距离用户要求的
10 Mpps 约三个数量级。代码审计发现每次 RX poll 都新建 descriptor
`Vec`，每次 refill 都新建 frame/address 两个 `Vec`，每个包还通过
`HashSet` 做 kernel-owned frame 插入/删除。即使当前 CPU 总量未饱和，
这些热路径分配、哈希和缓存不命中也不适合作为 10 Mpps 数据面。

## 根因

AF_XDP frame id 是 0..frames_per_queue 的稠密整数，使用哈希集合跟踪所有权
没有必要；receive batch 上限也已冻结为 256，descriptor/refill 暂存区
可以预分配或使用固定数组。原实现把诊断期安全结构直接放进逐包热路径。

## 修改范围

- 每个 QueueState 启动时一次性预分配 `receive_descriptors`，poll 时复用。
- refill 的 frame/address 暂存改为上限 256 的固定数组，不再逐批堆分配。
- kernel-owned frame 从 `HashSet<usize>` 改为按 frame id 索引的
  `Vec<bool>`；receive、refill 和 cleanup 都执行边界内 O(1) 标记。
- cleanup 逐位归还仍由内核 ring 持有的帧，保持先关闭 XSK 再释放 UMEM 的
  原安全顺序。
- 当前仍保留 `PacketBatch::from_owned_packets` 的逐包数据复制，后续由
  借用式快路径独立消除，避免一次提交同时改变所有权生命周期。
- 不修改只读上游 `/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 验证计划

1. Rust 格式、8 个既有测试和 release 构建；
2. 0.05 Mpps 单次 A/B，检查 drop、P99、覆盖、RSS 和清理；
3. 增加 capture-only 借用式探针，分离 AF_XDP 原始接收上限与完整特征流水线；
4. 只有结果改善且无所有权错误才保留，否则恢复上一版。

## 性能影响与回退

每队列增加固定的 descriptor 和 frame bitmap 内存，约为 KiB 级；换取消除
逐批 descriptor/refill 分配和逐包哈希。若出现未跟踪帧、UMEM drop、
capture drop、panic 或接口残留，立即恢复 HashSet 版本并失败关闭。

## 遗留风险

本修复只降低 Rust 热路径常数，不会让 bnx2x generic XDP copy 自动达到
10 Mpps。逐包数据复制、单线程 8 队列、全量解析/单流表和 NDJSON 远端推理
仍需架构整改；当前不能设置 `final_pareto_ingestion_allowed=true`。
