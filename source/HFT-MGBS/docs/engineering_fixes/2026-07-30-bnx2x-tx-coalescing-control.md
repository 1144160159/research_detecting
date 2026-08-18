# 修复：bnx2x TX coalescing 有界控制与自动恢复

## 触发证据

`PACKET_TX_RING` 版本在 `hft_r0_xdp_20260730T132028906367179Z` 中仍仅达到 2.820871 Mpps，最低 1 秒速率 2.750788 Mpps。8 个 TX 队列均有近似均衡的包增量，但 `tx_exhaustion_events` 总计新增 2,474,594；这把主要瓶颈定位到网卡 TX descriptor 回收/节流，而不是 Rust 构包、单队列或 `sendmmsg` 系统调用。

该次接收侧仅有 22 个网卡丢包，发送/接收差值 11，P99/P999 为 22/29 us，表明 TX ring 已改善排队稳定性，但仍不满足零丢包和 5 Mpps 门禁。

## 修复

- `run_xdp_fastpath_probe.sh` 新增可选环境变量 `REPLAY_TX_USECS`。
- 运行前读取并校验发送口原始 `tx-usecs`。
- 候选值写入 manifest，接口运行前快照保存实际生效状态。
- 无论正常退出、实验失败、中断还是错误，退出 trap 都恢复原始 `tx-usecs`。
- 只探索 `24 us` 与 `0 us` 两个候选；默认空值保持原配置 `48 us`。

## 停止规则

若 `0 us` 仍无法使发生器达到 5 Mpps，停止继续搜索 generic XDP/AF_PACKET 微参数。后续高吞吐验证转入支持 native AF_XDP zero-copy 的网卡，或在经过停机/接口解绑批准后验证 DPDK `bnx2x` PMD。

## 验证结果

| 候选 | 证据目录 | 最低实发 Mpps | 丢包 | P99/P999 (us) | 结论 |
|---:|---|---:|---:|---:|---|
| 24 us | `hft_r0_xdp_20260730T132538853911361Z` | 2.680883 | 0 | 17/23 | 未达 5 Mpps |
| 0 us | `hft_r0_xdp_20260730T132703740488898Z` | 2.680703 | 0 | 16/22 | 未达 5 Mpps |

两次运行结束后均核验 `ens8f1 tx-usecs=48`。停止规则已触发，24/0 us 不进入默认配置。
