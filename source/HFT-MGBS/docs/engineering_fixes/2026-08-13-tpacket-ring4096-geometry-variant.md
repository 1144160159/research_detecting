# TPACKET 4096×4096 ring geometry 单变量变体

## 依据与目标

历史 B2 zero-drop capture-only 证据使用 `block_size=4096`、`block_count=4096`，即每 worker 16 MiB ring。当前 full-pipeline runner 使用 `65536×256`，总容量同样为每 worker 16 MiB，但 block/lease 粒度扩大了 16 倍。R3 中八个 worker 仍接近 100% CPU，且出现 queue 0/5 共 10,796 NIC discard 和尾段吞吐下降，因此建立独立 ring-geometry 变体，验证较小 block 是否改善缓存局部性、block retirement/ownership 周期与队列排空及时性。

## 唯一变量

独立 runner/config 只改变：

- `block_size`: 65,536 → 4,096 bytes；
- `block_count`: 256 → 4,096。

两者乘积均为 16,777,216 bytes/worker。`frame_size=256`、`retire_block_timeout_ms=1`、8 worker、QM、CPU/IRQ、traffic-v2、active timeout、batch、GPU、持续时间、安全恢复、资格字段及正式 binary SHA `499b0b8e...` 全部不变。它不覆盖 current runner 或 traffic-v3 blocker 合同。

## 预期差异与风险

4 KiB block 每块最多容纳的 256-byte frame 数显著减少，理论上可缩短从内核填充到用户态获得 block lease 的周期，减少一次遍历跨越的 cache footprint，并更快归还 TP_STATUS_KERNEL。代价是 block 状态切换、poll/lease 获取和 retirement 次数约放大 16 倍，可能增加 syscall/元数据开销。历史 B2 只能作为硬件相关先验，不能证明 full pipeline 一定获益。

正式单变量判据仍是完整 runner 原始证据：至少 15 个完整窗、每窗目标吞吐、NIC 与 socket/internal drop、QM collision=0、GPU/关键流、worker CPU、restoration ledger 和 manifest。任何退化都停止该变体，不通过调节其他参数补偿。

## 验证边界

本轮只完成独立合同、静态测试与远端 `bash -n`，不运行网卡。合同测试要求 ring 总容量保持 16 MiB，严格存在 `4096×4096` argv，并拒绝旧 `65536×256` argv；同时锁定 binary、QM、worker CPU、frame、retire、batch、active timeout 和 duration 不漂移。

