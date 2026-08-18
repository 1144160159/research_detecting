# XDP 每队列独占 worker 整改留存

## 问题现象

借用式单线程 capture-only 在 0.5 Mpps 下收到 7,574,905/7,575,002 包，
差 97 包，sampled P99/P999 为 108/124 us，平均消耗 0.859 个 CPU 核。
即使移除完整解析和远端推理，单线程也已接近一核上限；线性外推不可能达到
10 Mpps。

基线目录：
`/home/wangwt/task/datasets/replay/hft_r0_xdp_20260730T121215739636432Z`。

## 根因

8 个独立 XSK RX queue 仍由一个线程串行扫描、receive、refill 和回调。
NIC 与 CPU 都位于 NUMA node 1，现有 56 个本地逻辑 CPU 未被用于数据面
分片，RSS 的并行性在用户态被重新串行化。

## 修改范围

- 新增 `HftXdpQueueWorker`，将一个 XSK socket、UMEM 和所有权位图以独占
  所有权移动到一个线程。
- `take_queue_workers` 只允许在 capture 已启动、队列完整时执行；
  `restore_queue_workers` 验证数量、queue id 唯一性并汇总统计后归还。
- worker Drop 会先关闭 socket 再归还 kernel-owned frame，异常路径不跳过
  UMEM 清理。
- 对 `Send` 的 unsafe 实现附带限定：QueueState 完全独占移动，ring 不在
  多线程共享；每个 worker 只能操作自己的 SPSC rings。
- 新增 `xdp_sharded_fastpath_probe`，按显式 CPU 列表一队列一线程，并记录
  每队列包数、每 worker CPU、采样延迟和总 drop。
- 第一轮固定 NUMA node 1 的 CPU 36--43；不修改 IRQ affinity，先隔离变量。
- 不修改只读上游 `/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 验证计划

1. Rust 格式、测试、release 构建和非法 CPU/队列数 fail-closed；
2. 与单线程相同 0.5 Mpps/15 秒 A/B；
3. 通过后依次 1 Mpps，再根据发生器能力进入 5/10/12 Mpps；
4. 任一档失败立即停止升档，区分发生器未达标、抓包 drop 与 raw P99。

首次脚本启动目录
`/home/wangwt/task/datasets/replay/hft_r0_xdp_20260730T121842726963922Z`
未执行抓包：切换到 sharded 二进制后脚本仍传入仅顺序版支持的
`--mode skb`，Clap 以退出码 2 拒绝。注入器独立完成但没有 probe，因此该
目录不计入性能证据。脚本已移除该参数，并新增 fail-closed 分支：probe
或 injector 失败/缺少指标时不再调用汇总器，也不对不存在文件做 SHA，
只保存启动失败 manifest 与现有二进制/eBPF 哈希。

## 性能影响与回退

最多使用 8 个固定 CPU worker，换取 RX queue 并行；总 CPU 门仍按机器可用
核与 0.85 资源比例判断。若线程无法固定、queue ownership 不一致、
drop/P99 恶化或清理残留，则恢复单线程借用式探针并失败关闭。

首次成功运行目录：
`/home/wangwt/task/datasets/replay/hft_r0_xdp_20260730T124247726525938Z`，
summary SHA-256 为
`1b55f1086dc7fdafdbf3f55c4a5e53ef32354bddc0b7c44b282cfdce270b3377`。
8 worker 收到 offered 的全部 7,571,886 包、capture drop=0，消除了单线程
基线少收 97 包的问题；平均合计使用 1.5004 核。但 raw P99/P999 反而为
9,937/11,857 us。根因是低负载时每个独占 worker 仍对自己的 XSK 执行
1 ms 阻塞 poll，8 个线程的唤醒/调度尾部被放大。

10 Mpps R0 属于持续轮询数据面，因此新增显式 `poll_borrowed_busy`：无包时
只执行 `spin_loop`，不做 poll syscall/睡眠；原有阻塞方法保留给低功耗兼容
路径。sharded probe 固定使用 busy 模式，下一次仍用 0.5 Mpps A/B。该模式
预期占用约 8 个核，资源评价以“换取 10 Mpps 的固定核预算”而不是低负载
CPU 最小化为目标。

busy 方法首次编译暴露一个纯借用错误：内部 helper 已接收 `&mut F`，调用
`receive_from_queue_with` 时又多加一层 `&mut`。编译器 E0596 在构建期
失败关闭，未启动实验；已改为直接传递 `visitor`。该修正不改变运行语义。

## 遗留风险

bnx2x generic XDP 仍有内核 copy，8 worker 也可能达不到 10 Mpps；DPDK
bnx2x 缺少 RSS，TPACKET_V3 fanout 或更换为支持 native AF_XDP zero-copy
的 NIC 仍是后备路线。当前只验证 R0，不代表全特征和 A09 通过。
