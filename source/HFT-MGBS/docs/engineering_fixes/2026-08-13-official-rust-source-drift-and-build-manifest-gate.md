# 正式 Rust 构建源漂移与 build manifest 门

## 事件和根因

2026-08-13 首次 TPACKET_V3 full-pipeline 实跑 R1 出现
`gpu_flows_scored=111`、`key_flows_enqueued=111`、`key_flows_scored=0`。
这不是同一 `RuntimeMetrics` 内的批次分类结果，而是正式物理机目录
`/home/wangwt/phase_2/code/HFT-MGBS/rust/hft-capture` 的依赖源陈旧。

当次 binary SHA-256
`324b3bc593e18a30fd080df10719957ea6c500d2498479591308f6e52e307fff`
是在正式目录的陈旧 `gpu.rs` 和 `scheduler.rs` 上构建的：

- 陈旧 `gpu.rs` 在成功批次中只增加 `gpu_flows_scored`，没有增加
  `key_flows_scored`；失败与 circuit-open 路径也没有增加
  `key_flows_inference_failed`。
- 陈旧 `scheduler.rs` 没有在调度阶段统计 key/base/deep 阶段，
  并用计划费用而非实际深特征费用判定 budget overrun。

先前隔离树的 fmt/test/build 通过只能证明隔离树输入，不能证明后续
正式目录的构建使用了同一组源。根因是构建前只冻结 binary/runner，
没有对 HFT 全 `src` 和 path/build 依赖生成并校验 manifest。

## 逐文件对比

对比本地代码权威目录与 10.0.5.8 正式目录的
`rust/hft-capture/src` 全部 19 个文件。17 个完全一致，所有漂移如下：

| 路径 | 本地权威 SHA-256 | 正式目录旧 SHA-256 | 处置 |
|---|---|---|---|
| `src/gpu.rs` | `069ddce35e4d331633532020c22c6cdf9d883f09c9e294493bea94fd512aadfa` | `eddfa3b90ff0d6fc5f72c637f48f8e91208b0e8e857a9ec61a24ba5360af507a` | 必须按白名单同步 |
| `src/scheduler.rs` | `6d6248165cba5d2719b55f99a264950db888148e0f675700821121a4d9ce2e66` | `5c9666e708a5de0ec7a3647a30e5e066294157d935f62464cb48e9e28e76f110` | 必须按白名单同步 |

`scheduler.rs` 的最初本地 SHA 为
`a77902a59bff58d27c43e3c76ca40ef984562b406e90f8a7fdecbd6df266cfcd`；
本次只按物理机 rustfmt 1.93.0 做了等价排版，得到上表新 SHA，
未改变功能。

其余 17 个一致文件为：
`capture_runtime_decision.rs`、`flow.rs`、`kernel_af_packet.rs`、`lib.rs`、`main.rs`、
`metrics.rs`、`tpacket_v3.rs`、`xdp_capture.rs`，以及 `src/bin` 下全部 9 个 bin。

Cargo 输入对比：

| 输入 | 本地 SHA-256 | 正式/验证 SHA-256 | 结论 |
|---|---|---|---|
| HFT `Cargo.toml` | `0d994ae88b6eed0cd16a3aa5b5fc1eafeff8d6eda3c92717a64c2a6264236633` | 同左 | 一致 |
| HFT `Cargo.lock` | `3f6faca7b54cf63dc3ee606a806f3367844b7a63f255f83ce5bb29199b178399` | `a6ba911cc943c6dfca0fc2f4a233a7dce99db28829a1fbe20bc6d0c191946123` | 漂移，不得从本地盲目覆盖 |
| HFT `build.rs` | 不存在 | 不存在 | 一致 |

lockfile 差异仅是正式 lock 包含 `sha1_smol 1.0.1` 及 UUID 对它的依赖边。
本地 HFT 的 Cargo path `../../../traffic-analysis-platform/...` 当前不存在，
因此本地 lock 不具备独立重生与 `--locked` 编译证据。本次继续使用已验证的
正式 lock，不将本地 lock 列入源码同步白名单。

## path 和 build 依赖冻结值

物理机实际解析的本地 path package 只有 HFT、`probe-agent`和
`proto-gen`。验证时的依赖输入为：

- traffic-analysis-platform workspace `Cargo.toml`:
  `3983d01169f9582549e4f26186354bdacd2805d42ee3ff1f3a72ab2282521675`
- `probe-agent/Cargo.toml`:
  `a1bc7657fe78979e84a3e24390f7ebba13d662ba400cd7345bd313b0b81134b1`
- `probe-agent` 的 `src` + package manifest 确定性 manifest root:
  `36b371d72c67bb6c149180897e760a134ea292891dd64c7a94ebf573e5386213`
- `proto-gen/Cargo.toml`:
  `037999ecbb833977452eea4293627d5ed5f9a7d35b4267e4e427f26471aff940`
- `proto-gen` 的 `src` + package manifest 确定性 manifest root:
  `2afb08a0fd4df6312f395d93197bed3cad5b2202578104762478d5e5bfda83bb`
- workspace `.cargo/config.toml`:
  `425bf0231670d33216b8b006fcb09458b256a1f6bdc83535806584be2481683b`
- toolchain: `cargo 1.93.0 (083ac5135 2025-12-15)` / 
  `rustc 1.93.0 (254b59607 2026-01-19)`。

`traffic-analysis-platform/rust` 仍是只读依赖，本次未修改。

## 最小同步白名单

正式 HFT 目录只需从本地权威树同步：

1. `rust/hft-capture/src/gpu.rs`
2. `rust/hft-capture/src/scheduler.rs`

不覆盖其他 `src`，不覆盖正式 `Cargo.lock`，不修改
`traffic-analysis-platform/rust`。同步后 HFT `src` + `Cargo.toml` + 正式
`Cargo.lock` 的确定性 manifest root 应为
`f3aaae0672b539200c1b36ac421eed200d5767cfe449daaddbf8711b54eca57f`。

## 防复发 build manifest 门

以后每次正式构建必须在编译前生成 manifest，并 fail closed 校验：

1. 记录 HFT 全 `src`、`Cargo.toml`、`Cargo.lock`、`build.rs` 的逐文件 SHA；
2. 通过 `cargo metadata --locked` 获取全部 path package，记录它们的
   manifest、source-tree root 和 `.cargo/config*` SHA；
3. 记录 `cargo --version --verbose`、`rustc -vV`、目标 triple 和 build flags；
4. 将 manifest SHA 绑定到输出 binary SHA；构建前后任一输入 SHA 变化即拒绝发布；
5. 使用 `cargo test --release --locked` 和
   `cargo build --release --locked --bin tpacket_v3_full_pipeline`；
6. 实验 runner 必须同时验证 binary SHA 和其 build-manifest SHA，
   不得只验 binary 或从另一隔离树的测试结果推导正式构建输入。

## 隔离验证

未覆盖正式 HFT 目录，未运行网卡实验。在
`/tmp/hft_official_drift_fix_20260813T051243Z` 复制正式树，只替换上述
两个白名单文件，并复用只读 traffic-analysis-platform 依赖：

- `cargo fmt -- --check`: PASS；
- `cargo test --release --locked`: 30/30 PASS；
- `cargo build --release --locked --bin tpacket_v3_full_pipeline`: PASS；
- 构建前后 `Cargo.lock` SHA 均为
  `a6ba911cc943c6dfca0fc2f4a233a7dce99db28829a1fbe20bc6d0c191946123`；
- 新隔离 binary SHA-256:
  `e8db9c370d1870344ee2de37d1662330eb1ad07275f1e761413f9ecbb8643ba0`。

该 binary 只是同步白名单的可编译/测试证据，未进行正式网卡运行，
不构成 2.79 Mpps 或 full-pipeline 资格证明。
