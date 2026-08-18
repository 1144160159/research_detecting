# 修复：stock bnx2x TCP RSS 有界诊断数据面

## 问题与边界

DPDK 25.11.2 stock `bnx2x` 不向 ethdev 上报 RSS hash capability，应用显式请求
UDP RSS 时会在通用校验层失败。历史实验补齐 UDP 能力上报和配置时序后，以实际
双 PF MAC 和 256 个变化 UDP 五元组运行 Q2，RX 仍为
`[15150080, 0]`。因此不能把 queue1 为零解释成单流，也不能继续把实验 UDP 补丁
作为生产候选。

源码同时显示 stock PMD 在 PF 启动时会无条件配置 regular RSS、IPv4/TCP hash 和
indirection table。为只验证这条既有硬件路径，本修复在 HFT 自有
`rust/hft-dpdk` 中增加一个默认关闭的 TCP RSS 诊断 profile；不修改 DPDK PMD、
上游 `traffic-analysis-platform/rust`、现有 runner 或冻结配置。

## 实现

- CLI 新增 `--traffic-profile`：
  - 默认 `udp-compat`，保留原 UDP 模板、offset 42 时间戳和多队列 UDP RSS 请求；
  - `tcp-rss-diagnostic` 仅允许精确 64 B、至少两个对称队列。
- C shim 为 TCP 诊断 profile 向 ethdev 提交
  `mq_mode=RTE_ETH_MQ_RX_NONE`、`rss_hf=0`，避开虚假的 capability 声明；
  `rte_eth_dev_configure(port, queue_count, queue_count, ...)` 继续保证每个 PF 的
  RXQ/TXQ 对称。是否真实分流只能由逐队列实测判定。
- TCP profile 建立 256 个唯一 IPv4/TCP 五元组，使用运行时读取的双 PF MAC，
  IPv4 total length 固定为 40，生成合法的无 payload SYN 头并计算 IPv4/TCP
  checksum。
- 64 B 帧中 offset 54 之后属于 IPv4/TCP 之外的 Ethernet padding。每个 burst
  的 TSC 时间戳写入 offset 54--61，不会覆盖 TCP 头，也不会使 TCP checksum
  失效。C shim 同时校验 `timestamp_offset + 8 <= frame_size`。
- schema 继续保持 5，避免改变默认 UDP/Q1 的现有解析语义；报告额外绑定
  `traffic_profile`、`synthetic_flow_count`、`ip_protocol`、
  `timestamp_offset_bytes` 和 `port_configuration`。TCP profile 使用独立 backend
  名 `dpdk_bnx2x_stock_tcp_rss_diagnostic`。

## 验证

Rust 单元测试覆盖：

- 默认 UDP profile 和原 MAC/协议布局；
- TCP IPv4 checksum、TCP pseudo-header checksum、20 B TCP header 与 SYN 标志；
- offset 54 位于 IP packet 结束之后且 8 B 时间戳完整落在 64 B 帧内；
- 256 个模板的五元组全部唯一；
- TCP profile 对 Q1 或非 64 B 输入 fail-closed。

Python 静态合同测试检查 CLI 默认值、Rust/C profile 编号、stock TCP 的
`mq_none/hf_zero` 配置、对称 port configure、动态时间戳边界以及报告字段。

本地没有 DPDK `libdpdk.pc`，只执行不链接 DPDK 的静态合同测试；Rust 格式、单测、
Clippy 和 release build 必须在物理机的固定 DPDK 25.11.2 环境重新执行并封存二进制
哈希。现有 release config 绑定旧二进制，不得用新二进制冒充原 Q1 release。

## 有界运行与停止规则

该 profile 只产生新的诊断能力，不代表已运行或已通过：

1. 新建独立冻结合同后先运行 stock Q2/TCP/64 B；两个 RX queue 必须都大于零，
   且满足包守恒、零错误、逐窗吞吐、尾延迟和完整恢复。
2. Q2 任一门失败即停止 bnx2x 多队列分支，不应用历史 UDP RSS 补丁。
3. Q2 全通过才允许一个 Q4 scaling 候选；达到 10 Mpps 也不能替代 12 Mpps、
   三次独立重复和最终要求队列数的生产硬门。
4. 本诊断结果始终保持 `r0_capture_only_qualified=false`、
   `final_pareto_ingestion_allowed=false`，直到新的外部证据链完成正式重算。

回退只需不传 `--traffic-profile tcp-rss-diagnostic`；默认 UDP 路径不变。若需要
二进制级回退，使用旧冻结合同绑定的旧二进制哈希。
