# fixed64 候选的 rx-usecs=12 单变量实验

## 目的与边界

该实验只检验 BCM57810 接收中断合并时间由 `24 us` 降为 `12 us`，能否消除 fixed64 候选在 2.79 Mpps 附近的接收丢弃。它是一次性原始诊断，不构成生产资格、完整流程资格或 Pareto 入选证明。

## 冻结项

- 二进制固定为 `tpacket_v3_full_pipeline_fixed64`，SHA-256 为 `6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca`。
- 流量 profile、包长、flowlen、clone/burst、QM、CPU/IRQ 亲和性、RX ring、TPACKET ring、GPU endpoint、批大小及所有硬门与 fixed64 基线相同。
- 唯一参数变化为 `ens8f0 rx-usecs: 24 -> 12`。
- 使用独立 runner、config、contract test 与本文档；不覆盖 generic/fixed64 历史证据。
- 实机只允许执行一次；失败后不重跑、不自动回退到其他参数。

## 安全与证据

runner 在变更前核验外部 runner/config/binary SHA-256、双 PF、驱动/NUMA/carrier/IP、竞争进程、pktgen、GPU reverse 端口和保留 CPU。它记录变更前后状态、逐队列统计、完整流水线/GPU/QM/fixed64 计数、恢复账本及全目录 SHA-256 清单。退出 trap 必须恢复 ring、rx-usecs、IRQ affinity、irqbalance、pktgen 与网卡状态；任何恢复失败均强制非零退出。

派生 runner 初次生成时，大文件读取输出被工具截断，合同测试在实机同步前发现它与基线不等；该未执行文件已删除并从基线原始字节分块重建。合同因此增加 shebang 必须位于 byte 0、总行数相等、反向替换后全字节相等，以及 cleanup、恢复等价性、丢弃门和证据清单后半段锚点检查，防止截断文件进入远端。

远端首次启动命令因 SCP 未保留 runner 可执行位而在 shell 入口前返回 `126 Permission denied`。runner 未开始执行、证据目录未创建，且复核无 pktgen/捕获进程、锁空闲、`rx-usecs=24`、irqbalance active+enabled、双 PF 状态未变，因此不构成一次参数实验。修复仅为给已通过 SHA/合同的同一 runner 添加执行位；内容 SHA-256 不变，随后只允许一次真正进入 runner 的实机实验。

## 判定

重点报告 15 个完整窗口中的最低接收 Mpps、`ens8f0` 每队列 discard 增量、fixed64 fast/fallback 守恒、GPU 批处理/错误、key-flow 计数、恢复账本和证据清单。现有流量 profile 的流关闭密度门仍可能令 runner 非零退出；不得据此隐去容量与丢弃原始结果，也不得把本次诊断标成闭环通过。

## 唯一实机结果

- 证据目录：`/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T125000Z_fixed64_rxusecs12_single_run`。
- runner 返回 `RC=1`，硬失败为 `ens8f0 rx_discards delta=526`；逐队列增量为 `[0,0,0,526,0,0,0,0]`。因此该候选淘汰，不得重跑或回退。
- 18 个完整窗口的最低接收速率为 `2.789465 Mpps`，比 `2.790000 Mpps` 门低 `0.000535 Mpps`；全程收到并解析 `52,911,026` 包，fixed64 fast=`52,911,026`、fallback=`0`、parse reject=`0`。
- GPU 共 `263` 个批次，`1,988/1,988` flow 和 key-flow 全部 remote scored，失败/terminal unresolved/queue drop 均为 `0`；RTT P50/P99/P999/max 分别为 `6.423052/16.837500/19.678652/19.678652 ms`。
- QM 记录 `1,160` 个 distinct flow hash、`0` 个跨 worker collision，runtime verified。流关闭总数仅 `1,988`，同样不足 `18*1000` 的聚合密度门。
- `restoration_failed=false`：RX ring 恢复 `453`、rx-usecs 恢复 `24`、16 个 IRQ affinity 恢复、pktgen 卸载、irqbalance 恢复 active+enabled 且双 PF 状态一致。证据清单 `176` 项，重新执行 `sha256sum -c evidence.sha256` 返回 `0`。
- GPU 主服务在实验前后均为 PID `1939474`、start ticks `3258220341`，继续监听 `50051` 且 argv 保持 A09 `numpy_exact`/reverse `10.0.5.8:50052` 不变。
