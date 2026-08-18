# 固定 64B IPv4/UDP 融合 parser 候选停止记录

## 候选与安全边界

本候选只在隔离树 `/tmp/hft_fixed_parse_proto_20260813/HFT-MGBS/rust/hft-capture` 实现和测试，未接入正式 `tpacket_v3_full_pipeline`、runner 或 config，未修改 `traffic-analysis-platform`，也未运行网卡。

原型仅在全部固定 profile 条件成立时直接构造 `ParsedPacket`：frame 精确 64 bytes、EtherType IPv4、version=4、IHL=5、IPv4 total length=50、无 MF/fragment offset、protocol=UDP、UDP length=30 且与 IP/capture length 一致、source 为每队列冻结的 `10.q.0.1:10000+q`、destination 为同 queue 的 `11.q.0.1--145:53`。VLAN/QinQ、IPv6、IP options、fragment、长度不一致、非 UDP、越界地址或端口不一致均调用原 `PacketParser`，没有 silent accept。

## TDD 结果

Release 隔离测试覆盖八个队列与目的地址边界，fast parser 与上游 parser 对 `ParsedPacket` 全字段逐项相等。负测试逐项破坏 frame length、EtherType/VLAN、IP version、IHL、fragment、IP total length、protocol、UDP length、source/destination 和 UDP ports，确认全部进入通用 fallback。20,000 包经 fast/general 两条 parse+flow 路径 flush 后，所有 flow ID 与 `RAW_FEATURE_ORDER` 38 维特征均按 `f64::to_bits()` 相等。定向等价测试结果为 3 passed、0 failed、1 ignored benchmark。

## 完整微基准与停止决策

Release 决策微基准使用 2,000,000 个固定 64B packet、145 个 flow，并在两侧都执行完整 parse 加相同 `HftFlowTable::update_into`：

- 上游 `PacketParser + flow`：257,062,179 ns；
- strict fast parser + flow：164,278,060 ns；
- speedup：1.565x。

门槛为至少 2.0x，测试按设计失败并返回非零。虽然 parser 原型语义等价且有收益，但不足以解释或消除现场约 100% worker CPU 与尾段退速，不具备部署优先级。因此候选停止：不进入正式 Rust 源、不重冻 binary、不修改 runner/config，不以局部 parser-only 数字替代完整 parse+flow 结果。

