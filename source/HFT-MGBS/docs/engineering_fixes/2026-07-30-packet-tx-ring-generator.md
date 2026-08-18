# 修复：发生器切换到 PACKET_TX_RING

## 触发证据

5 Mpps 阶梯实验 `hft_r0_xdp_20260730T131338121633352Z` 中，第一版多线程 `sendmmsg` 发生器仅达到 2.794795 Mpps，最低 1 秒速率为 2.655573 Mpps，累计出现 107,776,010 次 `EAGAIN/ENOBUFS` 重试。该结果说明普通 AF_PACKET 发送队列和重试循环本身已经成为首个瓶颈，不能用它判定抓包路径的 5/10 Mpps 上限。

同次实验接收侧记录 297,124 个丢包，发送/接收差值 163,937，原始 P99/P999 为 2,904/8,591 us，因此该次实验保持失败，不进入 Pareto 候选集。

## 修复

- 发生器后端从 `sendmmsg` 改为 `PACKET_TX_RING + TPACKET_V2`。
- 每个 NUMA 固定发送线程独占一个 2 MiB 内存映射环。
- 64 B 报文使用 128 B 环槽，每线程 16,384 个槽。
- 报文预构造后直接复制到共享环，批量标记 `TP_STATUS_SEND_REQUEST`，一次 `send()` 提交多个报文。
- 对 `AVAILABLE/SENDING/SEND_REQUEST/WRONG_FORMAT` 状态显式检查；错误格式和 2 秒排空超时均失败关闭。
- 发生器报告升级到 schema 2，记录 `packet_tx_ring_tpacket_v2` 后端和每线程环槽数。

## 安全与边界

- 只修改 `/home/wangwt/phase_2/code/HFT-MGBS` 对应本地源文件。
- `/home/wangwt/phase_2/code/traffic-analysis-platform/rust` 保持只读。
- 必须重新执行 Rust 格式化、全部目标测试、release 构建以及 5 Mpps 阶梯实验。
- 该修复只解决实验发生器的系统调用/套接字队列开销；不能预设 generic XDP 或 `bnx2x` 驱动可以达到 10 Mpps。
