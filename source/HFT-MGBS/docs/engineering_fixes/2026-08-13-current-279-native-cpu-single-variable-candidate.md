# Current-2.79 native CPU 单变量候选

## 目的与边界

本候选仅验证同一份冻结 Rust 源码在物理机本机 CPU 指令集优化下的吞吐差异。它是一次 capacity diagnostic，不是正式 repeat、不执行 fallback，也不声明生产资格。

## 单变量约束

- 基线 runner/config 保持字节不变：`826ceb8f...e85c59` / `7e7df0e7...6cdd6`。
- Rust 源码、`Cargo.lock`、QM 分流、8 个捕获 worker、CPU/IRQ 绑定、traffic v2、抓包与发生时长、GPU 服务、恢复流程全部保持一致。
- 唯一实现变量为编译参数 `RUSTFLAGS='-C target-cpu=native'`；使用 `cargo test --release --locked` 和 `cargo build --release --locked`。
- native 二进制使用独立路径 `target/release/tpacket_v3_full_pipeline_native_cpu`，固定 SHA-256 为 `8ddab139045b9e9a9b1a9fbfa89836869aedef67c8fb95ffbfb2d7ff2cff0623`。
- native 候选使用独立 ID、config、runner 与证据目录；其 runner 还把竞争进程检测扩展到 `tpacket_v3_full_pipeline*`，避免 generic/native 并发污染。

## 审计门

执行前必须同时通过：三项外部授权、runner/config/binary 三哈希信任根、无符号链接及二次哈希、冻结 JSON 语义合同、CPU 空闲度、双 PF/驱动/NUMA/链路、无 IP/XDP/qdisc、GPU 反向服务、无竞争进程、IRQ 拓扑与硬件队列检查。任一失败均在网卡和 irqbalance 变更前停止。

执行后必须验证：runner 退出状态、restoration ledger、irqbalance 状态和进程身份、双 PF 及接口恢复、hugepage、无残留 pktgen/capture/testpmd/DPDK 进程、证据 `manifest.sha256`。结果只作为 native 单变量诊断样本。

## 唯一单轮结果

2026-08-13 只执行一次，证据目录为 `/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T174200Z_native_cpu_capacity_r1`。本轮获得 18 个完整窗口，`min_full_epoch_mpps=2.786285`，21 秒抓取 52,961,785 包；但是 ens8f0 `rx_discards` 增加 6,316（queue 1 为 4,214、queue 2 为 2,102），触发零丢包硬门，runner 以 RC=1 结束。因此该候选明确为不合格，不能写入正式 repeat 或 Pareto 集，也未执行 fallback。

本轮 GPU 通道完成 281 个 batch、失败 0；2,021/2,021 个 key flow 均远端评分，QM 观测 1,160 个 distinct flow hash 且跨 worker collision 为 0。`gpu_batch_round_trip_latency` P99/P999 为 16.791752/16.917733 ms。推理进程 PID 1939474、start_ticks 3258220341 以及 runtime manifest/model/service/numpy engine/launcher 哈希运行前后未漂移，运行后 50051 主服务仍监听且无 50052 残留连接。

证据 `evidence.sha256` 全量校验通过，`restoration_verified=true`。现场复核 irqbalance active/enabled，ens8f0/ens8f1 均为 bnx2x 且 UP/LOWER_UP，两 NUMA 节点 hugepage 均为 0，pktgen 模块已卸载，并且不存在 capture/testpmd/hft-dpdk 残留进程。未进行第二次运行。
