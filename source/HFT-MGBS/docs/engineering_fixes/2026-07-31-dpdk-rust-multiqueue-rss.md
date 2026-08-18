# Rust DPDK 多队列 RSS/TSS 扩展

## 问题与证据

单队列 B128 在 1 Mpps 通过，但 5 Mpps 运行
`hft_r0_dpdk_20260731T014313443709656Z` 只有 `2.5697 Mpps`。收发包数
完全一致且 NIC/DPDK 丢包为 0，但单个 TX 和 RX 线程均接近占满一核，
TX 空返回约 2.61 亿次，P99 为 475.7 us。

DPDK 25.11.2 bnx2x 源码显示 PF 的 `max_rx_queues/max_tx_queues` 均来自
硬件 fast-path 数，且包含 RSS 和 TSS 初始化；原 HFT shim 却把两口强制
配置为 1 RX/1 TX 队列。

## 修改

- C shim 的 port init 增加 `queue_count`：
  - 多队列时配置 `RTE_ETH_MQ_RX_RSS` 和 IPv4 UDP RSS；
  - 为每个 queue 独立建立 RX/TX descriptor ring；
  - RX/TX burst API 显式接收 queue id。
- Rust CLI 增加 `--queue-count`、`--rx-cpus`、`--tx-cpus`。
- 一队列一 Rust 线程，所有 worker CPU 必须互不重复且不得占用 main CPU。
- 总目标速率均分到 TX 队列；最后一个 TX 完成后才通知全部 RX 进入
  200 ms 排空阶段。
- 报告 schema 升级为 2，新增逐队列收发包数和 `rss_queue_coverage`
  硬门；速率、CPU、stall 和时延按队列汇总。
- 运行配置把 queue 数和 CPU 列表冻结进 JSON 与 manifest。

## 受控候选

1. `Q2/B128 @ 5 Mpps`。
2. 仅当 Q2 全硬门通过时执行 `Q4/B128 @ 10 Mpps`。
3. 仅当 Q4 全硬门通过时决定是否执行 12 Mpps；不做无界队列搜索。

## 验证

- 原单队列配置必须保持兼容。
- 格式、单元测试、Clippy `-D warnings`、release 和静态 DPDK 符号门通过。
- Q2 必须两个 RX 队列均收到包、总收发差值为 0、零 DPDK/NIC 丢包，
  并通过冻结的 P99/P999。
- 每轮退出继续验证 bnx2x、10GbE、大页、UIO、hugetlbfs 和运行前缀。

## 边界

该扩展仍是 capture-only R0，不代表解析、特征、预算调度和 A09 全链路；
`final_pareto_eligible=false`。
