# 2026-08-13 Rust 端最终证据与恢复契约修复

## 范围与边界

本修复只改动 `rust/hft-capture` 的 Rust 源码、Rust 测试和本文档。未修改
`traffic-analysis-platform/rust`，未修改 runner、配置、Python 或 GPU 服务，也未执行网卡抓包。
验证只在由物理机 HFT-MGBS 副本构造的 `/tmp/hft_final_rust_patch_20260813`
隔离树中进行，隔离树使用 official `Cargo.lock` 并通过 `--locked` 构建。

## 修复内容

1. GPU transport circuit-open 固定为 200 ms，以便 300 ms 外部恢复门限保留网络、握手和推理时间。
2. reverse transport 接受连接后，先在同一 TCP 连接发送 `{"op":"health"}`，逐字段核对
   CLI 提供的 candidate、schema、model SHA-256 和 inference engine，成功后才置 ready。
   当前 direct Python listener 每连接只处理一个请求，health 与后续 inference 不能同连接强绑定，
   因此 direct transport 明确 fail-closed。
3. 只有完整、身份匹配且 prediction 数量与请求流数一致的响应才逐 flow 写 completion receipt。
   receipt 包含稳定 source ID、flow ID 及 FNV-1a hash、request/index/window、trigger、
   materialization-to-completion、kernel-to-remote、recovery attempts 和 backend identity。
   瞬时失败进入 bounded recovery queue，不计最终 inference failed；只有缓存溢出或关闭后仍未解决
   才进入 terminal/inference-failed，保证每个 key flow 最终状态唯一。
4. 外部故障注入、故障发现和恢复事件同时记录 wall-clock epoch 和
   `CLOCK_MONOTONIC` 纳秒值，恢复耗时继续来自 `Instant`。
5. packet continuity 在真实收包闭包内读取 Linux pktgen UDP payload 起始处的 big-endian
   magic `0xbe9be955` 与 sequence。冻结模型同时绑定 `clone_skb=64` 与 `burst=8`：clone counter
   每次 `pktgen_xmit()` 只增加一次，但一次调用会发送 8 包并使内部 sequence 增加 8，因而同一
   header sequence 的观测组严格为 `64 * 8 = 512` 包，下一次重建 header 的 sequence 步长也为
   512（起始 residue 为 1）。首尾组是 boundary-unverified，不形成硬门；中间组的少包、超过
   512、跨组缺口、乱序和 u32 wrap 分别计数。每 worker 独立记录，结束时按
   `(queue, sequence)` 合并，并输出 input/valid/invalid 与 ownership merge 守恒。

Linux pktgen 的头格式、网络字节序以及 sequence 在成功发送后递增来自上游
`net/core/pktgen.c`。由于本次明确禁止网卡运行，真实环境是否保持冻结的
clone-64/burst-8/group-512 形态必须由
后续 preflight/live receipt 证明；magic、sequence residue 或 ownership 不符合时均 fail-closed，
不得由 wrapper 填写 `packet_gap=0`。

## TDD 与验收门

测试覆盖：direct fail-closed、错误 model health 永不 ready、同连接 reverse health 后 inference、
失败缓存后 retry 成功且 `key_flows_inference_failed=0`、失败不写 completion、逐流 completion
守恒、外部 injection monotonic 字段、首尾 partial group 不误报、组内 missing/duplicate、step=512、
跨多个组、u32 wrap、乱序、invalid magic/sequence、跨 worker 合并和 queue owner 唯一。

冻结前必须依次通过：

```text
cargo fmt --all -- --check
cargo check --locked --all-targets
cargo test --locked --all-targets
cargo build --release --locked --bin tpacket_v3_full_pipeline
sha256sum Cargo.lock target/release/tpacket_v3_full_pipeline
```

任何 identity、continuity、receipt 守恒或 monotonic 字段失败都保持资格为 false。

## 隔离验证结果

- 最终 group-512 隔离树：`/tmp/hft_final_evidence_group512_20260813/HFT-MGBS`
- `cargo fmt --all -- --check`：通过。
- `cargo check --locked --all-targets`：通过；仅有未修改上游 `probe-agent` 的既有 warning。
- `cargo test --locked --all-targets`：59 passed、0 failed、4 ignored；ignored 均为显式 microbenchmark。
- `cargo build --release --locked --bin tpacket_v3_full_pipeline`：通过。
- official-derived `Cargo.lock` SHA-256：
  `a6ba911cc943c6dfca0fc2f4a233a7dce99db28829a1fbe20bc6d0c191946123`。
- 隔离 release binary SHA-256：
  `6b905a46e664843340e5f378bc625b3d07b8c9b4baf43ccccabc5b7abeb956e8`。
- 本地已有 `Cargo.lock` SHA-256 仍为
  `3f6faca7b54cf63dc3ee606a806f3367844b7a63f255f83ce5bb29199b178399`；本修复未覆盖它，
  formal 构建以隔离树 official lock 为准。

本结果仅证明源码、测试和隔离 binary 已冻结，不等同于网卡 live 通过或 2.79 Mpps 正式重复通过。

## 10.0.5.8 formal 集成记录

- 备份与构建证据：
  `/home/wangwt/task/datasets/replay/hft_current_279_rust_final_evidence_build_20260813T131454Z`。
- 只同步本修复记录列出的 8 个白名单对象；`packet_continuity.rs` 最终 SHA-256 为
  `b12c22695e12df6f21a0c60b73abcca64297d0632db76779f2970ad340851896`。
- formal `Cargo.lock` 在同步前后均为
  `a6ba911cc943c6dfca0fc2f4a233a7dce99db28829a1fbe20bc6d0c191946123`。
- formal 树再次通过 fmt/check/test/release 四道门：59 passed、0 failed、4 ignored；formal release
  binary SHA-256 为
  `9c4e6cfab251b1d595dc9366f77752f8c333f9e2b2fd1092f2f1ebc7aa557255`。
- `/home/wangwt/phase_2/code/traffic-analysis-platform/rust` 同步前后整树摘要均为
  `e1e4efe619fb458afeafe097a80cbbf8e8846156d52e324ae807bd77317fb51d`，未发生修改。
- 本次没有运行网卡、pktgen 或故障注入；formal 构建成功仍不是 live 资格。
