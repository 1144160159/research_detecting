# 2026-08-13 当前 2.79 final-evidence runner 合同

## 目的与边界

新增独立 `run_current_hardware_279_tpacket_final_evidence.sh`、对应 JSON 合同与合同测试。它不覆盖
fixed64、rx-usecs 或 traffic-v3 runner，也不修改 `traffic-analysis-platform/rust`。本次只完成静态
合同和 formal binary 绑定，没有运行网卡、pktgen 或 GPU 流量。

runner 冻结 formal binary SHA-256
`9c4e6cfab251b1d595dc9366f77752f8c333f9e2b2fd1092f2f1ebc7aa557255`，并在启动 Rust 前显式传入：

- candidate `A09`；
- schema `1`；
- model SHA-256 `fa9d29858bb7a20f9a66be2105a6182368e4b3029a59ead5fd77f6228b0eb5d2`；
- inference engine `numpy_exact`。

## 新增的硬门

raw gate 必须从 `pipeline_raw.json` 的真实字段读取：顶层捕获/解析/连续性字段以及
`pipeline_metrics` 内的 completion receipts、completion conservation、GPU batch evidence、GPU
queue/full/failed、identity failure、terminal unresolved 与 pending counters。不得由 wrapper 补零。

连续性合同冻结 `clone_skb=64`、`burst=8`、观测组 512 包、sequence step 512、residue 1；逐窗
continuity 必须存在，且全局 gap、duplicate、reorder、invalid、unsupported transition、owner conflict
均为 0，input 与 ownership merge 守恒必须为真。每个完整窗口还要求至少 1000 个远端 completion
receipt、100 个 GPU batch receipt，并要求 source ID 唯一、receipt 不截断、远端 scored 与 completion
receipt 守恒。GPU/feature/capture 队列和所有失败计数均为 0，完整窗口最小吞吐不得低于 2.79 Mpps。

## 为什么 runner 当前静态阻断

Rust 的 active expiry 条件是 `last_ts - first_ts >= active_timeout`，idle expiry 条件是
`now - last_ts >= idle_timeout`。当前两者均为 1 秒。group-512 流量下，2.8 Mpps 约产生
5469 个 flow materialization/s；1160 个 flow identity 的完整重访周期约为 0.21 秒。该重访频率会
持续刷新 flow，且不能在未实证前假定每个完整窗口能够闭合至少 1000 个 flow 并远端完成。

因此合同将 `flow_completion_density_precondition_proved=false`，runner 在创建证据目录和任何主机
mutation 之前固定以 RC 86 退出。即使提供正确授权与三个外部 SHA trust root，也不能绕过该门。
后续只能用一个版本化、独立审查的 flow-churn/capacity 证据解除，不能直接删除阻断或降低门槛。

## 验证

合同测试覆盖 candidate/config/diagnostic receipt 一致性、formal binary、A09 四字段、group-512 raw
字段路径、GPU capacity/drop/conservation、Rust expiry 语义，以及 RC 74/RC 86 负路径。测试只做静态
检查与 mutation 前退出，不执行网卡。
