# 修复：独立 Rust DPDK bnx2x R0 快路径

## 目标

generic XDP/AF_XDP COPY-mode 在当前 BCM57810 上约 2.8 Mpps 触顶。新增独立 `rust/hft-dpdk` crate，用 DPDK bnx2x PMD 直接验证 64 B 小包 1/5/10/12 Mpps，不让 DPDK 依赖污染或阻断现有 `hft-capture` 构建。

## 实现

- Rust 负责 EAL 参数、端口选择、NUMA CPU 固定、TX/RX 并发、节流、统计、硬门禁与证据 JSON。
- 小型 C shim 只封装 DPDK 宏/内联 burst、mbuf bulk 与端口配置；数据面每个 burst 只跨 FFI 常数次。
- 两个 PCI 设备均显式 allow-list；不允许同一 PCI 同时作为收发口。
- bnx2x PMD 无 RSS，R0 明确采用单 RX 队列；通过后再以软件无锁环分片到解析线程。
- TX 报文写入 TSC 时间戳，RX 每 1,024 包采样端到端延迟。
- R0 硬门禁：最低 1 秒实发达到目标、发送接收差值为 0、`imissed/ierrors/rx_nombuf` 均为 0、P99 不超过 100 us、P999 不超过 500 us。
- 无论 R0 是否通过，完整管线和最终 Pareto 标志保持 false。

## 构建隔离

`build_hft_dpdk.sh` 仅在找到固定 DPDK build manifest 时编译该 crate。普通 `hft-capture` 的 8 个测试和 release 构建不依赖 DPDK。

## 未授权阶段

当前仅实现和编译。加载 UIO、hugepage 分配、关闭链路、解绑 `bnx2x` 和运行 DPDK 仍需可回退脚本与显式批准。

## 首次编译修复

首次 `cc-rs` 编译在 DPDK 头内报告 `ssize_t` 未定义、`strnlen` 未声明，并提示 `rte_pktmbuf_append` 的 `char*` 到 `uint8_t*` 符号差异。shim 改为在所有头之前定义 `_GNU_SOURCE`、显式包含 `sys/types.h`，并对 mbuf 数据指针做明确转换。该失败发生在编译期，没有加载 PMD或改变网卡。
