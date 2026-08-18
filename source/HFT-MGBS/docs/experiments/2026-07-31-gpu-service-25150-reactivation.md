# GPU 服务 25150 端口恢复与分离部署现状

## 连接与边界

- GPU 节点：`10.0.5.103:25150`；
- SSH 使用本机私钥
  `C:\Users\LongShine\.ssh\id_rsa`、`BatchMode=yes`、
  `IdentitiesOnly=yes`、`ClearAllForwardings=yes` 和
  `StrictHostKeyChecking=yes`；
- 新端口 ED25519 指纹：
  `SHA256:ptg8SMNQvUQYHV0/hafU4hBlhZ/vb4wJUmM1XTVlROI`；
- 项目：
  `/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS`；
- Python 环境：
  `/opt/data/private/wangwt/anaconda3/envs/py3.9`。

本次没有把用户提供的口令写入命令、脚本、配置或日志。

## 服务状态

2026-07-31T04:58:59Z 启动的服务在两次后续快照中保持稳定：

- pidfile/Conda wrapper PID：9906；
- 实际 Python 监听 PID：9927；
- 监听：`0.0.0.0:50051`；
- 运行目录：
  `/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS`；
- health：`ok=true`，候选 `A09`，
  `extra_trees_3_seed_ensemble`，
  `invariant_no_ports_v1`；
- `algorithm_device=cpu`、`gpu_required=false`、`model_n_jobs=1`；
- warmup：512 条，约 68,796.36 us；
- threshold：0.340336；
- runtime manifest SHA-256：
  `363ff8b55f3150a80ded52d6728b2ddf5bf0df5f8d9ae9267c3889b48a606595`。

节点具有 RTX A6000，但当前 A09 是 CPU ExtraTrees；“部署在 GPU 主机”不能写成
“算法使用 GPU 加速”。

## 物理端链路状态

runtime manifest 配置了 `10.0.5.8:50052`，但两次 `ss -ntp` 快照均没有
`:50052` 或 `10.0.5.8` socket，日志也没有 `reverse_connected`。因此当前只证明
GPU 服务独立可用，不能证明物理 Rust 端与 GPU Python 端已形成分离部署链路。

物理端 50052 listener、反向连接、真实流量请求、重连和 fallback 仍需单独验证。

## 源码一致性

对 `hft_mgbs/scripts/rust/deploy/configs/tests` 及顶层工程文件做逐文件 SHA-256
清单比较（排除 `__pycache__/*.pyc`）：

| 项目 | 数量 |
| --- | ---: |
| 本地文件 | 219 |
| GPU 文件 | 165 |
| 同路径同哈希 | 156 |
| 本地独有 | 54 |
| GPU 独有 | 0 |
| 同路径不同哈希 | 9 |

运行中的 Python 包 `hft_mgbs` 共 25 个文件，本地与 GPU 同路径同哈希；54 个本地
独有文件主要是 27 个 XDP/DPDK 配置、10 个 Rust/DPDK 文件、12 个工程脚本和
5 个测试文件。9 个同路径漂移文件为：

- `.gitignore`；
- `rust/hft-capture/src/gpu.rs`；
- `rust/hft-capture/src/kernel_af_packet.rs`；
- `rust/hft-capture/src/main.rs`；
- `rust/hft-capture/src/metrics.rs`；
- `rust/hft-capture/src/scheduler.rs`；
- `rust/hft-capture/src/xdp_capture.rs`；
- `scripts/run_live_acceptance.sh`；
- `scripts/run_physical_link_diagnostic.sh`。

因此不得宣称本地、物理机、GPU 三端全源码一致。GPU 运行包可用与全工程同步完成是
两个不同结论。

## 测试与审计副作用

- 同步后的 GPU 全量 Python 测试曾执行并通过：173 项；
- 当前本地继续新增了 DPDK release gate 测试，尚未再次同步到 GPU；
- 远端 release audit：
  `accepted=true`、候选 A09、offline 与 split recovery 历史门通过，
  但 `physical_live_gate_pending=true`、
  `final_pareto_eligible=false`。

审计最初误用一次 HTTP `curl` 和一次错误转义 JSON 请求探测 JSONL 服务，使进程内
`failures` 计数增加到 2。随后停止请求；日志 size/mtime/hash、manifest 和源文件均未
变化，服务未重启。后续性能或可靠性实验必须在新 run ID 中隔离这一审计污染，不能把
当前计数当成生产失败。

## 当前资格

- GPU 独立服务健康：是；
- 物理端到 GPU 的 50052 分离链路：未形成证据；
- 全源码三端一致：否；
- GPU 加速：否，当前算法为 CPU ExtraTrees；
- `full_pipeline_qualified=false`；
- `final_pareto_ingestion_allowed=false`。
