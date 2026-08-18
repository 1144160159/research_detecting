# TPACKET_V3 RX ring 与独立发生器整改

## 1 Mpps 分层定位

- 默认 ens8f0 RX descriptor 为 453。首次 1 Mpps 诊断实发 15,150,080、签名接收
  15,120,990，差值 29,090；TPACKET ring drop/freeze 为 0。
- ens8f0 驱动 `rx_discards` 同步增加 29,090，精确解释缺口，证明丢包发生在
  bnx2x 硬件 RX ring/NAPI 层，而不是 Rust TPACKET 用户态。
- 临时把 RX ring 提升至硬件上限 4078 后，4-worker 与 2-worker 两轮均完成
  15,150,080/15,150,080 严格对账，`rx_discards` 增量、TPACKET drop/freeze 均为 0，
  最低完整秒均为 1.009664 Mpps。

## 尾延迟与停止规则

- 4-worker P99/P999 为 704/726 us，CPU 约 3.88 核。
- 2-worker P99/P999 为 673/708 us，CPU 约 1.82 核。
- 两者均未通过 100/500 us 尾延迟门；2-worker 只略降时延，因此 1 Mpps worker 数
  调参在此停止，不继续扩展候选。

## 12 Mpps 发生器

现有 Rust PACKET_TX_RING/AF_XDP COPY 发生器约 2.8 Mpps 触顶，不能验证 12 Mpps。
新增 `run_pktgen_tpacket_v3_probe.sh`，使用内核 pktgen 的 8 个线程/8 个 TX queue 做
一次线速上探。脚本只操作专用 ens8f0/ens8f1，并在退出或信号时停止 pktgen、恢复 RX
ring、撤销混杂 socket、卸载本轮加载模块并保存接口状态。

任何 pktgen 结果仍须以 RX 签名计数、驱动 `rx_discards`、TPACKET drop、完整秒速率和
P99/P999 共同判定；只看到 pktgen 发送速率不能视为捕获通过。
