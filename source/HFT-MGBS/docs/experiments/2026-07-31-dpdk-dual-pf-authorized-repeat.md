# 2026-07-31 DPDK 双 PF 授权重复验证

## 范围与冻结配置

- 本轮依据明确授权，只在物理机 `10.0.5.8` 的本地光纤回环上执行 DPDK 双
  PF 测试：`ens8f1 / 0000:cb:00.1` 发送到
  `ens8f0 / 0000:cb:00.0`。
- `Q1` 表示每个端口使用 1 个队列，不表示单 PF；冻结候选为
  `Q1/B128/15 s`。
- 不访问网关、不向外部网络发流；运行证据只保存在
  `/home/wangwt/task/datasets/replay`。
- DPDK 数据面执行期间 GPU 服务保持暂停且未触碰；只读上游
  `/home/wangwt/phase_2/code/traffic-analysis-platform/rust` 未修改。

## 受控 CPU 替代

固定 CPU 集合 `28/36/44` 的初次空闲检查不满足运行门。未终止或干预任何其他
进程；在 NUMA 1 上重新执行 5 秒物理核、SMT sibling、affinity 与 IRQ 检查后，
选择 `main=53`、`RX=44`、`TX=55`。既有 DPDK file-prefix 审计通过，PF
解绑、运行、恢复和独立恢复审计均由同一 `flock` 临界区覆盖。

## 1 Mpps 有效重复运行

证据目录：

`/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260731T041221978805926Z`

| 指标 | 观测值 |
| --- | ---: |
| 运行时长 | 15.000107 s |
| 发送 / 接收 | 15,150,080 / 15,150,080 |
| 发收差值 | 0 |
| 最低 1 秒 TX / RX | 1.009959 / 1.009965 Mpps |
| `imissed / ierrors / rx_nombuf` | 0 / 0 / 0 |
| P99 / P999 | 81.224 / 434.806 us |
| 最大时延 | 464.258 us |

`r0_capture_only_qualified=true`，且 `hard_gate_errors=[]`。该结果是
Q1/B128/1 Mpps 的独立重复通过，不替换既有稳定基线，也不外推到 5、10 或
12 Mpps。

本轮资源只作为观测证据，不作为尚未冻结的发布资源硬门：wall time
18.47 s、user/system 18.35/0.16 s、进程 CPU 100%、最大 RSS 40,460 KiB、
voluntary/involuntary context switch 117,781/39、major/minor fault
835/1,177。

## 5 Mpps 前置门阻断

5 Mpps 没有启动。对同一 CPU 集合进行最终 5 秒复检时，冻结的最低空闲度
95% 未同时满足：

| CPU | 最低空闲度 | 结论 |
| --- | ---: | --- |
| 44 | 89.11% | 阻断 |
| 53 | 94.06% | 阻断 |
| 55 | 98.00% | 通过 |
| SMT 100 | 90.00% | 阻断 |
| SMT 109 | 95.96% | 通过 |
| SMT 111 | 88.89% | 阻断 |

停止证据目录：

`/home/wangwt/task/datasets/replay/hft_dpdk_preflight_blocked_20260731T040339734758305Z`

该目录名不用于推断与有效运行的严格时间顺序。门禁在 PF 解绑前触发：
runner 未启动、没有 5 Mpps 运行目录、没有新增 5 Mpps 吞吐或时延结果。
既有 5 Mpps 测量及其拒绝结论不被本次前置阻断覆盖。

## 回退与证据完整性

- 有效运行退出后，两个 PF 均恢复 `bnx2x`、10GbE、carrier 1、operstate
  `up`；combined queue 8、RX/TX ring 453/4078、RX/TX coalescing
  24/48、GRO/LRO on/off 均与独立前置快照一致。
- hugepage 恢复为 0，UIO 与 `uio_pci_generic` 未加载；本次 hugepage 文件、
  HFT 进程及 `/var/run/dpdk/hft_r0_dpdk_*` 当前前缀均为 0。
- 有效运行基础清单 `evidence_sha256.txt` SHA-256：
  `6dbdc946dc9d020d1dc1651942f545ad2c730c906d92c5890214f97e2ef5202a`。
- 有效运行完整清单 `evidence_sha256_complete.txt` SHA-256：
  `75b10aad82866378b071d8119cfacbb424027560bd8e3ea72fd1ceb98eab9b2e`。
- 前置阻断基础清单 SHA-256：
  `b822e4adc13a6fdd932a951c8e64d7eb0a959a05b40ea68ad016ebdc09f99a0d`。
- 前置阻断完整清单 SHA-256：
  `8201d7389e5dc3c694d23365f45d587d5201884514d452fa3f945b405988d843`。
- 四份清单各自覆盖的文件均已通过 `sha256sum -c`；完整清单额外绑定
  stdout、stderr、`process_time.txt`、前后快照及 preflight stdout。

## 资格边界

本轮只确认双 PF Q1/B128/1 Mpps 在另一组受控 CPU 上可重复。由于 5 Mpps
被环境门在解绑前阻断，不能产生新的 5 Mpps 结论。该夹具不包含协议解析、
多粒度特征抽取、自适应预算调度或关键流覆盖，因此保持：

- `r0_capture_only_qualified=true`
- `full_pipeline_qualified=false`
- `final_pareto_ingestion_allowed=false`

