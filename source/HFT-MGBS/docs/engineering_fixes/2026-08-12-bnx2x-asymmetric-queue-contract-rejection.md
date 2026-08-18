# bnx2x 非对称队列合同失效关闭

## 问题

`dpdk_testpmd_capacity_q4_10mpps_v1/v2.json` 曾把发送 PF 配置为
`RXQ1/TXQ4`，试图只隔离四发送队列能力。DPDK 25.11.2 的 stock bnx2x PMD 在
`bnx2x_dev_configure()` 中明确拒绝 `nb_tx_queues > nb_rx_queues`，因此该候选即使
通过 CPU 空闲门，也会在端口配置阶段返回 `-EINVAL`，不会进入数据面。

反向的 `RXQ4/TXQ1` 也不能作为替代：PMD 以两者最大值建立 fast-path，并为非默认
队列准备收发资源；缺失的对侧队列只记录错误而不能形成可信的非对称实验。bnx2x 的
每个 PF 必须按 `RXQ == TXQ` 配置。

## 修复

- `run_dpdk_testpmd_capacity.sh` 的冻结合同门恢复为只接受 Q1：
  `rx_queue_count == tx_queue_count == 1`，且后端只能是
  `dpdk_bnx2x_testpmd_q1_capacity`。
- 删除不可达的 Q4 `txonly-multi-flow` 参数分支。旧 Q4 JSON 保留为历史失败证据，
  但当前 runner 会在 HugePage、接口 down 和 PF 解绑之前拒绝它们。
- 合同测试明确断言两个旧 Q4 文件均为非对称、diagnostic-only，且不能再满足 runner
  schema。

## 边界与后续

该修复不改变既有 Q1 约 2.57 Mpps 的密封结果，也不宣称当前硬件达到 10 Mpps。
若验证多队列，只允许新建对称队列合同；接收多队列还必须提供逐软件队列包数、总包
守恒、零错误和完整恢复证据。旧 Q4 合同不得执行或进入 R0/Pareto。
