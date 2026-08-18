# XDP 多队列空闲等待修复留存

## 问题现象

XDP receive batch 64/128/256 在固定 0.05 Mpps 下均为零丢包、关键流覆盖
1.0，但 kernel-XDP-entry-to-feature P99 均约 32.5--33.4 ms。单包处理
P99 只有约 2.65 us，物理进程只使用 16%--22% 的一个 CPU 配额量级，
说明尾延迟不是解析算力饱和，也不能通过扩大 receive batch 解决。

## 根因

HFT 自有适配层注册了 8 个 XSK RX 队列，但一次完整扫描没有数据时，只对
`next_queue` 的单个 socket 执行 1 ms `poll`。其余 7 个队列在等待窗口内
到达数据不会唤醒该 poll，导致多队列就绪通知不完整。它不一定是全部
32 ms 尾延迟的唯一来源，但属于可确认的多队列等待错误。

## 修改范围

- 在 HFT 自有 `HftXdpCapture` 中构造全部活动 XSK fd 的 `pollfd` 数组。
- 空闲时使用一次 `libc::poll` 同时监听所有 RX queue 的 `POLLIN`。
- `EINTR` 视为无数据并重试；其他 poll 错误携带上下文失败关闭。
- 数据面扫描、receive batch、UMEM 所有权和 eBPF 程序保持不变。
- 不修改只读上游 `/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 验证计划

1. Rust 全量测试、release 构建和格式门；
2. 固定 receive batch=64、0.05 Mpps、同一 PCAP 单次 A/B 复测；
3. 检查零抓包丢包、关键流覆盖、P99/P999、RSS 与退出清理；
4. 只有 P99 <=10 ms 且其余硬门均通过，才进入三重复验。

实验完成后在本文件追加运行目录、SHA-256 和接受/拒绝结论。

单次 A/B 复测目录：
`/home/wangwt/task/datasets/replay/hft_pdiag_20260730T104438474646878Z`；
组合证据 SHA-256 为
`00f4d831b0f083042ebc647944d03daaf70a142f607236b4598ac360f907ea51`。
固定 receive batch=64 后结果为：

- offered/received 均为 757,523，capture drop=0；
- observed minimum=0.0504973 Mpps，关键流覆盖=1.0；
- kernel P50/P99/P999=1,156/30,449/38,623 us；
- 内部特征入队 P99=1,479.247 us，GPU batch P99=60,157.03 us；
- `gpu_queue_full=0`、时间戳异常=0、时钟阶跃=0；
- 退出后 ens8f0/ens8f1 均为 UP/LOWER_UP，未残留 XDP 程序。

相对同配置修复前 XRB64 的 P99 33,068 us，下降 2,619 us（7.92%），
说明修复有效但不足以通过 10,000 us 硬门。该结果不进入最终 Pareto，也
不执行三重复验；后续用 0.01--0.05 Mpps 已知通过/失败区间做有限边界搜索。

## 性能影响与回退

每次空闲等待创建最多 8 个 `pollfd`，增加很小的栈外向量分配和一次多 fd
poll；预期换取正确的任意队列唤醒。若 CPU、RSS 或延迟恶化，恢复上一版
单 fd 等待并保留失败证据；不得通过延长 poll timeout 掩盖问题。

## 遗留风险

该修复只覆盖“空闲等待监听错误”，不证明调度抖动、NUMA、generic XDP
copy 路径或注入突发已解决。当前仍是 diagnostic-only，不能设置
`final_pareto_ingestion_allowed=true`。
