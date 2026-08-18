# XDP UMEM 清理与多队列适配修复

## 问题现象

ens8f0 上的 `xdp` 与 `xdp-skb` 均能启动并进入数据面，但 15 秒诊断结束时进程以 134 退出：

`CRITICAL: UMEM dropped with 2048 frames still allocated`

两次失败目录：

- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T070349672137157Z`
- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T070528386156305Z`

## 根因

只读上游 XDP 实现向 fill ring 初始提交 2,048 个 UMEM 帧，但停止时关闭 XSK 后没有归还仍由 fill/RX ring 持有的帧；同时仅注册 queue 0，而 ens8f0 当前启用 8 个 combined RX 队列，无法满足全流量覆盖。

## 修改范围

- 在 HFT-MGBS 内新增自有 `HftXdpCapture` 适配层，不修改只读上游。
- 从 `ethtool -l` 获取当前 combined 队列数，并为所有活动 RX 队列注册 XSK。
- 每队列显式跟踪 kernel-owned UMEM frame；停止时先卸载 BPF、关闭 XSK，再归还所有未消费帧。
- native XDP 与 xdp-skb 使用严格独立模式；native 失败时不静默降级。
- XDP kernel drop/invalid/ring-full/fill-empty 计数保守并入 capture drop。
- AF_XDP descriptor 地址按 UMEM 相对偏移解释，以 `addr/frame_size` 计算帧号；不再调用上游按绝对地址解释的 `addr_to_frame`。
- 当前适配层在复制包数据后立即归还 XDP 帧，避免上游 `PacketBatch` 生命周期与 XSK ring 所有权交叉；该额外复制必须纳入资源/P99 Pareto 比较。
- promisc guard 在释放 UMEM 队列前恢复，确保即使后续清理失败也不遗留混杂模式。
- 新增 HFT 自有 `hft_xdp_redirect.c`：在 XDP 入口用 `bpf_ktime_get_ns` 写入 8 字节 data metadata，用户态结合 CLOCK_MONOTONIC 与 CLOCK_REALTIME 偏移得到可审计的 kernel-XDP-to-feature 时间。
- 每次运行都从源代码构建 eBPF 对象、复制到证据目录并记录 SHA-256；不复用无时间戳的上游对象。
- AF_PACKET 时间戳模式继续作为安全回退。

## 验证计划与证据

实现完成后必须依次完成：

1. Rust 单元测试与 release 构建；
2. native XDP 15 秒诊断，验证正常退出且接口无残留；
3. xdp-skb 15 秒诊断；
4. 通过后同一后端三次稳定复测；
5. 与 AF_PACKET 比较丢包、P99、资源、关键流覆盖和回退约束。

本记录将在每次实测后追加运行目录、哈希和结论。

首次多队列 generic XDP 复测目录为
`/home/wangwt/task/datasets/replay/hft_pdiag_20260730T072352511628607Z`。
该次将原先 2,048 帧泄漏缩小到 1 帧，并暴露 descriptor 地址语义错误；
进程 panic 导致 promisc 临时残留，已人工恢复为 0。该结果仍判定失败，不进入候选前沿。

时间戳 metadata 首次成功运行目录：
`/home/wangwt/task/datasets/replay/hft_pdiag_20260730T074012436618501Z`。
该次 8 队列收到 151,563/151,563 包、drop 0、正常退出且无接口残留；
kernel-XDP-entry-to-feature P99 为 4,416 us、P999 为 8,050 us，
GPU batch P99 为 67,235.691 us，关键流覆盖 1.0。eBPF 对象 SHA-256 为
`1f81856eb3e23c8437fea4cd3ae05d43daf95e492a11db8293ecd0dde0297624`。
组合器因尚未识别新 provenance 而拒绝；随后新增独立的
`kernel_xdp_entry_realtime` 起点，避免将 XDP 时间伪装成 AF_PACKET 时间。

首次三重复测的第 1 次目录为
`/home/wangwt/task/datasets/replay/hft_pdiag_20260730T074859762291451Z`。
XDP 正常退出并收到 151,499 包、drop 0，但注入器在 15 秒截止边界遇到
TX `EAGAIN` 后返回错误。根因是 `send_batch` 将“截止时间到达”误判为
发送失败，并且外层会把未发送的尾部帧计入 offered。修复后
`send_batch` 返回实际 sent 数、重试数和 deadline 标志，外层只累计实际发送帧；
截止正常结束，整次零包才失败关闭。

修复后的三次稳定复测目录：

- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T080059864471667Z`
- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T080201984456560Z`
- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T080247651528258Z`

汇总证据：
`/home/wangwt/task/datasets/replay/hft_xdp_skb_stability_v1_20260730/summary.json`，
SHA-256 为
`8567cb456cf35781607d13661696a089af0e1a9a01a19e834a4079a146442386`。
三次均发送/接收 151,563 包、抓包丢包 0、解析拒绝率
0.0003562875、关键流覆盖 1.0。最坏 kernel-XDP-entry-to-feature
P99/P999 为 4,533/9,216 us，内部特征 P99 为 1,854.637 us，
GPU batch P99/P999 为 98,316.482/120,260.719 us，物理进程最大 RSS
为 939,928 KiB。三次 capture 二进制与 eBPF 对象哈希分别一致。

同场资源三重复测目录：

- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T082012112035696Z`
- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T082112946699326Z`
- `/home/wangwt/task/datasets/replay/hft_pdiag_20260730T082217894934194Z`

物理汇总 SHA-256 为
`e1843998728339951540998ac3345cf1eb209d65bbdd9c9c0686265b32b0a2cc`；
跨主机时间绑定与资源汇总 SHA-256 为
`8935a0f46403302a2cfaf86cc220650bfe8a64ebf78a568aeaaea3d167864df7`。
三组采样重叠分别为 14.569、14.115、14.677 秒，均超过 12 秒门槛。
物理进程最大 RSS 为 940,028 KiB；A09 推理服务最坏使用 1.0211 个
CPU 核、RSS 228,769,792 B，服务无 GPU 进程上下文。系统 GPU
利用率与显存占比最坏 1.0/0.1355 是同机背景进程，只保留为干扰证据，
不归因给 A09。

native XDP 严格探测目录为
`/home/wangwt/task/datasets/replay/hft_pdiag_20260730T072240949838968Z`，
bnx2x 返回 `EOPNOTSUPP`。因此当前诊断候选顺序为
`xdp-skb` 优先、`af-packet-ts` 安全回退；不能宣称 native/zero-copy XDP。

## 性能影响与回退

默认每队列 4,096 个 4 KiB 帧；8 队列 UMEM 约 128 MiB。多队列消除 queue 0 覆盖缺口，但会增加锁页内存和轮询成本。任一 XDP 模式若出现非零丢包、未核验 P99、资源越界、关键流覆盖不足、清理失败或残留程序，立即回退 `af-packet-ts`。

## 遗留风险

`bpf_ktime_get_ns` 是 XDP 入口的软件内核时间，不是 NIC 硬件时间戳。必须验证 metadata 在 bnx2x generic XDP 到 AF_XDP 的传递、时钟偏移稳定性和 P99/P999；失败时不能冒充 kernel-to-feature P99，并回退 `af-packet-ts`。

以上均为 0.01 Mpps、15 秒物理链路诊断。生产目标负载、SLA、在线抓包
驱动回退和 24/72 小时长稳尚未冻结或完成，所以
`final_pareto_ingestion_allowed=false`。
