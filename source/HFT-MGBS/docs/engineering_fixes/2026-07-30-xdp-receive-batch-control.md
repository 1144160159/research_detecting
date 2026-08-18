# XDP 接收批量受控优化留存

## 问题现象

0.01 Mpps 的三重复测中，`xdp-skb` 的最坏
kernel-XDP-entry-to-feature P99 为 4,533 us；首次受控负载扫描提高到
0.05 Mpps 后，抓包仍为零丢包、关键流覆盖仍为 1.0，但 P99 上升到
34,369 us，超过诊断门限 10,000 us。0.10 Mpps 以上还出现 GPU 有界队列
饱和和关键流覆盖下降，不能把两个瓶颈混为一个算法结论。

首次负载扫描汇总：
`/home/wangwt/task/datasets/replay/hft_xdp_load_exploration_20260730T095613676528562Z/summary.json`，
SHA-256 为
`39f5600d3ac733750b8889315b6e421638a9cda6a5b902a9f0ed7bc81a525a68`。

## 根因假设

HFT 自有 AF_XDP 适配层原先把单队列每次 receive/refill 数量固定为 64。
0.05 Mpps 时物理进程 CPU 尚未饱和，却出现 XDP 到特征队列的尾延迟增长，
需要用有限候选对照检验 64 个 descriptor 的轮转/调用开销是否造成积压。
该项目前是待实验验证的根因假设，不作为已确认结论。

## 修改范围

- 新增 `--xdp-receive-batch-size`，默认 64，保持原行为。
- 参数只允许 1..=256 内的 2 的幂；命令行和 XDP 适配层双重 fail-closed
  校验，避免异常内存分配或未经控制的搜索。
- receive descriptor 数和 refill 数共同使用同一冻结值；后端启动日志记录
  实际值。
- `run_live_acceptance.sh` 通过环境变量 `XDP_RECEIVE_BATCH_SIZE` 传入并写入
  每次运行 manifest，保证候选可追溯。
- 不修改只读上游 `/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 验证证据

2026-07-30 首轮代码验证：

- `cargo fmt -- --check` 在格式化后通过；
- HFT Rust 8 个测试全部通过（5 个库/主程序测试和 3 个注入器测试）；
- `cargo build --release` 通过；
- `bash -n scripts/run_live_acceptance.sh` 通过；
- 非法候选 63 被明确拒绝，错误为
  `--xdp-receive-batch-size must be a power of two in 1..=256`。

只读上游编译仍有既存 warning，但未对上游文件执行修改。下一步仅探索
64、128、256 三个候选，固定 0.05 Mpps、15 秒、相同 PCAP、A09、GPU
batch=128 和其余运行参数。先做单次筛选；只有通过丢包、P99/P999、解析、
关键流覆盖与资源硬门限的候选，才允许进入三重复验。

受控实验已完成，活动目录：
`/home/wangwt/task/datasets/replay/hft_xdp_receive_batch_exploration_20260730T102449290918901Z`。
汇总 SHA-256 为
`b50fcd4824bb5fa99f329e57b04719816f3e903dd3d8119a8d2b5da5bf91a991`。

| 候选 | receive batch | observed Mpps | capture drop | 关键流覆盖 | kernel P99/P999(us) | GPU P99(us) | RSS(KiB) | 结论 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| XRB64 | 64 | 0.0504973 | 0 | 1.0 | 33068/41594 | 61816.394 | 1034528 | P99 失败 |
| XRB128 | 128 | 0.0504973 | 0 | 1.0 | 32541/45416 | 60821.854 | 1033288 | P99 失败 |
| XRB256 | 256 | 0.0504972 | 0 | 1.0 | 33350/51594 | 59033.157 | 1034276 | P99/P999 失败 |

三个候选均未通过硬门限，`passing_candidate_count=0`、
`pareto_front=[]`、`selected_for_confirmation=null`。接口退出后未残留
XDP 程序。由于 128 相对 64 只改善 527 us（约 1.59%）且仍超门限
225.41%，而 256 恶化 P999，因此确认“固定批量 64 是主要根因”的假设
不成立，不消耗三重复验预算。

## 性能影响与回退

增大接收批量可能降低 syscall/ring 操作开销，也可能扩大单队列占用时间并
恶化跨队列公平性和尾延迟，因此不预设“越大越好”。若三个候选都未通过，
默认值保持 64，并转向轮询策略或特征/GPU 队列的独立受控优化；不得以扩大
无界缓冲掩盖过载。

任一候选出现非零抓包丢包、关键流覆盖低于 0.99、P99 超过 10 ms、
P999 超过 50 ms、接口清理残留或资源越界，立即判定不合格并恢复默认 64。

本轮已按该条件保持默认 64；参数化能力保留用于可复现实验和以后不同硬件
复核，但 RC1 不选择 128/256。

## 遗留风险

当前均为 diagnostic-only 物理链路回放，不是生产 SLA；尚无 24/72 小时
长稳证据。即使某一批量通过首轮筛选，也不能设置
`final_pareto_ingestion_allowed=true`。

下一项优化必须检查多队列空闲等待是否只监听单一 XSK fd，以及捕获进程的
NUMA/CPU 调度；不得继续扩大 descriptor 批量或 GPU 队列来掩盖尾延迟。
