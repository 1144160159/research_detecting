# Current-2.79 fixed64 融合解析单变量候选

## 变更范围

本候选把隔离原型 `fixed_profile_parse.rs` 接入 `tpacket_v3_full_pipeline` 的唯一解析点。只在 traffic v2 的 64B Ethernet/IPv4/UDP 全部约束成立时直接构造 `ParsedPacket`；帧长、EtherType/VLAN、IPv4 version/IHL/total length、fragment、protocol、UDP length、源/目的地址或端口任一不匹配，都调用原 `PacketParser`，不静默接受。

现场历史证据中 `pktgen` 显示 `dst_min=11.q.0.1`、`dst_max=11.q.0.145`，QM runtime distinct flow 为 `1160=8×145`，因此严格 fast 范围为 `.1` 至 `.145`，`.146` 进入 general fallback。字段级测试覆盖八个 queue 和 `.145` 边界；负测试逐项破坏每一约束；20,000 包 parse+flow 后按 flow ID 对齐，38 维特征全部按 `f64::to_bits()` 与 general oracle 相等。

输出新增固定 profile ID，以及每 worker/aggregate 的 fast/fallback 计数，用于证明现场真实流量确实进入候选路径。其他 flow/GPU/metrics/scheduler 源码、QM、CPU/IRQ、ring、traffic v2 和 GPU 服务均保持冻结值。编译使用普通 release profile，不设置 `target-cpu=native`。

## 构建门

由于本地仅代码镜像中的 `Cargo.lock` 与远端 official lock 不一致，正式构建只在 10.0.5.8 的 HFT 临时副本完成，锁文件固定 SHA-256 `a6ba911cc943c6dfca0fc2f4a233a7dce99db28829a1fbe20bc6d0c191946123`，不覆盖本地 lock，也不修改只读 `traffic-analysis-platform/rust`。目标 HFT 文件通过定向 `cargo fmt --check`，随后 `cargo check/test/build --release --locked`；正式测试为 47 passed、0 failed、4 ignored（其中三个既有 microbench，另一个 fixed parser release-decision microbench）。

本候选只允许执行一次 capacity diagnostic，不计正式 repeat，不执行 fallback。执行及恢复结果在单轮结束后追加。

## 唯一单轮结果

证据目录：`/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T193000Z_fixed64_fused_capacity_r1`。本轮只执行一次，得到 17 个完整窗口，`min_full_epoch_mpps=2.791566`，共处理 51,834,447 包。所有包均命中 strict fast path（fast=51,834,447、general fallback=0、parse rejected=0），现场确认 `.1` 至 `.145` 的 traffic v2 范围与融合 parser 一致。

本轮 ens8f0 `rx_discards` 增加 1,774，全部位于 queue 5，触发零丢包硬门，runner RC=1，因此即使最低完整窗超过 2.79 Mpps，也不能作为合格 repeat 或 Pareto 候选。packet socket、feature queue 和 key feature queue drop 均为 0。

GPU 完成 272 batch、失败 0；1,948/1,948 个 key flow 均远端评分。QM distinct/observation/collision 为 1,160/1,948/0。GPU batch RTT P99/P999 为 27.405312/35.741623 ms，也不满足 10 ms 尾延迟目标。

`evidence.sha256` 全量校验通过，`restoration_verified=true`。运行后 irqbalance active/enabled，ens8f0/ens8f1 均为 bnx2x 且 UP/LOWER_UP，两 NUMA 节点 hugepage 为 0，pktgen 已卸载，无 capture/testpmd/hft-dpdk 残留。未执行第二轮或 fallback。
