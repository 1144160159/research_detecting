# Current-2.79 受控 transport fault runner 实现记录

## 范围

本次只增加独立的故障注入 runner、配置与测试，不修改正常 TPACKET runner、Rust、unified release 或旧 v2。未执行网卡、iptables 或故障实验，也未停止、重启或发送信号给 GPU 服务。

该 runner 只验证“有界缓存 + circuit + reverse TCP 重连到同一冻结 A09”。它不能证明本地 fallback、生产高可用或 Pareto 准入。

## 安全模型

- 三个逐字授权、change ticket、外部 runner/config SHA 和独占 `flock` 缺一即退出。
- 在任何 mutation 前，校验冻结 parent runner/config/binary、v3 profile 和 Rust recovery source。
- 运行中从 `ss` 取得唯一 ESTABLISHED 四元组，并要求 socket PID 与冻结 capture process receipt 一致。
- 仅在物理机 OUTPUT 插入一条规则：源 `10.0.5.8:50052`、目的 `10.0.5.103:<本连接临时端口>`、owner UID 0、conntrack ESTABLISHED、唯一 comment、`REJECT tcp-reset`。
- 不涉及 SSH、50051，也没有 GPU host 的 stop/kill/restart 命令。
- `setsid` 超时 watchdog 与 shell trap 双重删除；删除后要求完整 `iptables-save` 字节 SHA 恢复一致。
- 防火墙后端、owner/comment/conntrack、路由、唯一连接或恢复任一不可证时 fail closed。
- raw fault receipt 使用 monotonic 事件、前后 ruleset SHA、连接四元组、唯一 comment，并作为外部文件按 SHA 绑定到 transport receipt。
- 逐窗 `packet_gap/capture_drop` 必须来自 Rust raw report 的显式 `packet_continuity_windows`；runner 不会把汇总 drop 推断或伪造成逐窗 0。

## 当前 NO-GO（预 mutation）

冻结 v3 合同要求端到端 `recovery_ms <= 300.0`，当前 Rust `CIRCUIT_OPEN_DURATION` 恰为 300 ms。故障被检测后仍需等待 circuit，再重连和完成一次 A09 推理，所以理论上不可能严格满足该合同。runner 的静态门要求 `circuit_open_ms < recovery_ms_max`，当前因此以 RC 91 在任何目录创建、parent runner 启动或 iptables 变更前退出。

当前 pipeline raw schema 也没有逐窗 `packet_gap`/`packet_continuity_windows`，即使 circuit 后续降到 200 ms，仍会以 RC 92 在 mutation 前退出。必须由后续版本化 Rust candidate 提供真实逐窗连续性 receipt，不能由 wrapper 补零。

## 2026-08-13 只读 capability preflight

- 主机 `10.0.5.8`：iptables 1.8.7 legacy；nft 1.0.0；`timeout/flock/ss/sha256sum/python3` 存在。
- route：`10.0.5.103 dev br0 src 10.0.5.8`。
- 现有 OUTPUT policy ACCEPT，同时有 Kubernetes 与 libvirt 链，因此 runner 不 flush、不 replace，仅精确插入/删除自身规则。
- `iptables-save` 当时 SHA-256：`f026332006ee2b04c2d5207f18653b8ee2c3329106ca9ee51eecd990ca316634`；HFT fault comment 数为 0。
- `xt_comment`、`nf_conntrack` 已加载，`xt_owner.ko` 存在，iptables wait lock 可用。
- 预检时未运行流量，50052 没有 ESTABLISHED connection；50051 从物理机探测为 connection refused。因此当前运行态也不是 fault trial 的 GO 状态。

## 后续准入

只有在新的 Rust candidate 同时满足以下条件并重新绑定 config SHA 后，才允许申请一次 live trial：circuit 明确低于 300 ms；raw report 有真实逐窗连续性；50051 health 为同一 A09；50052 唯一连接可绑定 capture PID；防火墙前置快照与 owner/comment/conntrack preflight 全通过。正式运行仍需另行提供三重授权与 change ticket。
