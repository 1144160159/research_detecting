# HFT-MGBS 工程与实验进度

更新时间：`2026-08-13T00:24:25Z`

## 当前结论

> 2026-08-13 收敛更新：已执行 stock bnx2x IPv4/TCP 256 五元组、双 PF 对称
> Q2/1 Mpps 的最后一次多队列假设检验。15 秒内发送和接收均为
> `15,150,080` 包，TX 队列为 `[7,575,040, 7,575,040]`，但 RX 队列为
> `[15,150,080, 0]`；丢包和 NIC 错误为 0，P99/P999 为
> `11.0035/151.453 us`，13 项主机恢复全部通过。由于第二 RX 队列占比为 0，
> 冻结的每队至少 40% 门失败，当前 BCM57810 的 Q2/Q4 分支已按停止规则关闭。
> 达到 10 Mpps 的唯一保留路径是新增具备 strict native XDP、forced AF_XDP
> zero-copy、DPDK RSS/TSS 和至少 8 RX/8 TX 队列的 10/25GbE NIC，并由独立
> 发生器执行 12 Mpps、15 秒、三次零丢包验收。

> 算法最优性更新：受控搜索预算为 8--12 个、实际 10 个候选。只有 A09/A10
> 具备 normal/fallback 各三次成对指标，严格 Pareto 前沿为 A09/A10，
> `epsilon=0.03` 的实用前沿为 A09；A01--A08 尚无同协议成对重复，且 10 个
> 候选均缺少可重哈希的 evidence SHA。因此 A09 只能称为当前 finalist，不能称
> 全 10 候选的已证明最优。运行时无生产后端，联合 Pareto 前沿为空、Champion
> 为 null，统一发布保持 `accepted=false`。

> 控制面更新：本轮使用已信任主机密钥和 `ClearAllForwardings=yes` 成功登录
> `10.0.5.103:25696`。Python PID 1888 正在 `0.0.0.0:50051` 监听，GPU 本机 NDJSON
> health 返回 `ok=true`；但 runtime manifest 仍声明旧 PID 1857，实际 manifest SHA
> 已变为 `eac2beab0ba42d158c6ea4acb4c10b07c9e80b58f04fcff3dc71b83826035620`，
> 物理机到 50051 当前 connection refused，50052 也没有 listener/ESTABLISHED 连接。
> 因此只确认孤立 Python 服务存活，不确认双机生产运行身份。

> 2026-08-12 更新：当前 BCM57810 双口上的 12 Mpps R0 仍不合格。最新
> TPACKET/QM 零丢包上限为约 2.794 Mpps；正式 DPDK 12 Mpps 请求仅达到
> TX/RX 最低 2.570/2.569 Mpps 且 P99 为 522.373 us。两次路径均已验证恢复，
> 结论是必须进入新网卡硬件门，而不是继续无界调参。

> 统一审计更新：3 份最新吞吐观测均通过路径、SHA、计数与恢复核验；TPACKET
> B1/B2 归因为本轮发生器受限，DPDK 12 Mpps Q1 归因为单队列收发路径受限。
> `audit_complete=true` 不等于可发布；当前仍为
> `production_release_accepted=false`。

- 离线 finalist：`A09`。它在 A09/A10 的新鲜成对确认中为 practical winner，
  但全 10 候选最优性审计为 `false`，不得称为已发布算法最优解。
- 最终 Pareto 资格：`false`。当前运行时决策为 `stop_fail_closed`、生产后端为空，
  联合 Pareto 前沿为空且 Champion 为 null。
- “最优”边界：算法预算已冻结为 8--12 个且实际探索 10 个；只有补齐全部 10
  候选的同协议 normal/fallback 重复与证据哈希后，才能证明该有界集合内的算法
  最优。生产最优还必须叠加新 NIC 的 12 Mpps R0、R1--R4、资源、关键流和回退门。

## 受控算法探索

- 搜索预算：最少 8、最多 12、实际 10 个候选。
- 搜索维度：特征配置 3 种、分类器族 2 种、阈值策略 4 种、自适应策略 2 种。
- 已具备同协议成对指标的子集严格 Pareto 前沿：`A09, A10`；实用前沿：
  `A09`；其身份是待继续验收的 finalist，不是全搜索或生产最终选择。
- `A09`：`invariant_no_ports_v1 + extra_trees + calibration_macro_f1_floor080 + calibration_weighted_weight500`。
- 子集选择依据：A10 的 Macro-F1 与良性召回增益均低于 0.03，而 A09 的攻击召回
  与 AUPRC 增益均超过 0.03，且 A09 的 ECE 更低。A01--A08 的缺失证据仍会阻断
  `algorithm_only_optimal`。

## 受控运行时探索

- 总实验量：`24` 次（4 候选 × 2 轮 × 每轮 3 次）；任一轮失败即淘汰，聚合使用跨轮最坏值。
- 通过全部硬约束：`2` 个；Pareto 前沿：`thread_cpu0_3, thread_all`；初选 `thread_cpu0_3`，当前激活 `thread_all`。激活变更未扩展候选集合，依据后续完整 PCAP 最坏值复核。
- 冻结部署：`prediction_execution=thread`、`cpu_set=all`、可用 CPU `80`、`model_n_jobs=1`。
- 选择项跨轮最坏值：推理 P99 `92546.5us`、内部 P99 `4897.14us`、端到端 P99/P999 `8249/8385us`。
- 两个 inline 候选均因历史轮次越过尾延迟硬门禁被淘汰；最近一轮的更快结果不能覆盖历史失败。

## 已验证硬约束

| 约束 | 门限 | 保守观测值 | 状态 | 证据范围 |
| --- | ---: | ---: | --- | --- |
| 同域分组 Macro-F1 | >= 0.9 | 0.955874 | 通过 | 新鲜确认组 |
| 独立留出 Macro-F1 | >= 0.7 | 0.730858 | 通过 | 独立留出 |
| 攻击召回率 | >= 0.72 | 0.764706 | 通过 | 独立留出 |
| 良性召回率 | >= 0.93 | 0.945051 | 通过 | 独立留出 |
| AUPRC | >= 0.45 | 0.522967 | 通过 | 独立留出 |
| ECE | <= 0.05 | 0.0383549 | 通过 | 独立留出 |
| 事件召回率 | >= 0.7 | 0.735043 | 通过 | 独立留出 |
| 物理机离线回放丢包率 | <= 0 | 0 | 通过 | 三次完整 PCAP |
| GPU 批次往返 P99(us) | <= 100000 | 70282.7 | 通过 | 三次完整 PCAP |
| 流物化至特征入队 P99(us) | <= 5000 | 3981.66 | 通过 | 三次完整 PCAP，非端到端 |
| 关键流覆盖率 | >= 0.99 | 1 | 通过 | 三次完整 PCAP |
| 预算超限次数 | <= 0 | 0 | 通过 | 三次完整 PCAP |
| 真实双机恢复时间(s) | <= 0.3 | 0.0459103 | 通过 | 三次断链恢复 |
| 稳健运行时推理 P99(us) | <= 100000 | 92546.5 | 通过 | 4 候选 × 2 轮 × 3 次 |
| 稳健运行时端到端 P99(us) | <= 10000 | 8249 | 通过 | 虚拟链路诊断，跨轮最坏值 |
| 虚拟链路分层丢包率 | <= 0 | 0 | 通过 | 最终二进制三次严格计数对账 |
| xdp-skb 物理诊断丢包 | <= 0 | 0 | 通过 | ens8 双口三次诊断 |
| XDP 入口至特征 P99(us) | <= 10000 | 4533 | 通过 | ens8 双口三次诊断 |
| XDP 入口至特征 P999(us) | <= 50000 | 9216 | 通过 | ens8 双口三次诊断 |
| xdp-skb 关键流覆盖率 | >= 0.99 | 1 | 通过 | ens8 双口三次诊断 |
| xdp-skb 同场推理 CPU 占整机 | <= 0.85 | 0.0127633 | 通过 | 物理/GPU 三组时间绑定 |
| xdp-skb 同场推理内存占整机 | <= 0.85 | 0.000423144 | 通过 | 物理/GPU 三组时间绑定 |
| XDP 至 AF_PACKET 回退恢复(ms) | <= 300 | 118.946 | 通过 | 三次注入式运行时故障 |
| Python 服务进程树 CPU 占整机 | <= 0.85 | 0.0137589 | 通过 | 与三次完整 PCAP 同步采样 |
| Python 服务进程树内存占整机 | <= 0.85 | 0.000422546 | 通过 | 与三次完整 PCAP 同步采样 |
| A09 服务归因 GPU 利用率 | <= 0.85 | 0 | 通过 | PID 归因；系统 GPU 仅作背景 |

资源最坏观测：物理进程 CPU 占单核 `17%`、物理主机 CPU 上界 `0.002125`、物理内存占比 `0.000385266`；与三次完整 PCAP 同步的 Python 服务进程树共采样至少 `314` 次，最坏使用 `1.10071` 核、占整机 CPU `0.0137589`、RSS `228446208` 字节、内存占比 `0.000422546`、线程 `4`。A09 服务在至少 `71` 个 GPU 样本中无计算上下文，归因 GPU/显存占比均为 `0/0`；系统 GPU 背景最高 `0`，不归因给 CPU ExtraTrees。这些仍不替代物理在线目标负载资源门。

## 工程实现状态

- 物理机 `10.0.5.8`：Rust 抓包、解析、多粒度特征、预算调度、反向推理传输和 Rust PCAP 批量发包器；只修改 `/home/wangwt/phase_2/code/HFT-MGBS`。
- GPU 节点 `10.0.5.103`：Python A09 推理服务；算法实际为 CPU ExtraTrees，未伪称 GPU 加速。
- RC1 运行参数：`n_jobs=1`、`batch=128`、`feature_flush=1000us`、`timeout=150ms`、`budget=5000us`、`safety_ratio=0.5`。
- 正常路径：三轮各 `78786` 包、`4939` 流；评分、关键流覆盖均完整，队列满、批次失败、回退和预算超限均为 0。
- 内部流物化至特征队列入队 P99 最坏 `3981.66us`，GPU 批次往返 P99 最坏 `70282.7us`；前者只证明内部排队边界，不替代 NIC/内核接收到特征入队的端到端 P99。
- `af-packet-ts` 已在隔离虚拟链路验证严格计数对账与内核 `SO_TIMESTAMPNS` 来源：三轮每次至少 `50546` 包、分层丢包 `0`、关键流覆盖 `1`；`3491` 个端到端样本的内核接收至特征入队 P99 `1139us`，时间戳异常 `0`、实时时钟步变 `0`。该证据是诊断证据，不能进入最终物理 NIC Pareto。
- 两个 10GbE 口均为 `bnx2x`（`0000:cb:00.0, 0000:cb:00.1`），`ens8f0/ens8f1` 均为 10GbE、UP、无 IP/管理桥/默认路由。bnx2x 原生 XDP 严格探测返回 EOPNOTSUPP；HFT 自有 8 队列 `xdp-skb` 三轮诊断均零丢包、关键流覆盖 1.0，最坏 kernel-XDP-entry-to-feature P99/P999 为 `4533/9216us`，GPU batch P99 `98316.5us`。
- `xdp-skb` 同场跨主机资源三轮通过：物理 RSS 最坏 `940028` KiB，A09 推理使用 `1.02106` 核、RSS `228769792` 字节，服务无 GPU 进程上下文。当前优先 `xdp-skb`、安全回退 `af-packet-ts`。
- 三次注入式运行中回退最坏 `118.946ms`，回退后至少继续处理 `100249` 包；退出后 promisc=0、无残留 XDP 程序且 GRO 已恢复。切换窗口最多少收 `1307` 包，因此该证据不复用正常路径零丢包结论，生产目标负载回退压力门仍未完成。
- 资源归因修正：一次探索采样发现整机 GPU 可被其他任务推至 100%，但 A09 服务 PID 始终无 GPU 上下文；发布硬门因此只使用服务 PID 归因值，系统 GPU 保留为背景干扰，不用整机忙碌度错误淘汰 CPU 模型。
- 恢复路径：三轮真实断链—反向重连—再次推理，最坏恢复 `45.9103ms`，门限 `300ms`。

## 最新在线预检

- 运行：`hft_10gbe_requalification_ens8_v1_20260730`，结果 `accepted=false`。
- 捕获口 `ens8f0`：carrier `1`、operstate `up`、speed `10000` Mbps。
- 回放口 `ens8f1`：carrier `1`、operstate `up`、speed `10000` Mbps。
- 捕获口 XDP metadata 时间戳能力：`true`。
- 阈值冻结：`false`。

阻塞项：

- `thresholds.not_frozen`
- `thresholds.target_load`
- `thresholds.max_parse_reject_rate`
- `thresholds.max_end_to_end_p99_us`
- `thresholds.max_end_to_end_p999_us`
- `thresholds.min_run_duration_s`

## 临时替代接口（历史诊断）

- 已按 `temporary-ens9f0-passive-shadow-v1` 使用 `ens9f0` 完成 `3` 次、每次 60 秒的被动确认；该口为 `br0` 的 1GbE 管理/集群上联，不执行 PCAP 注入或主动发流。
- `ens8f0/ens8f1` 恢复后，`ens9f0` 不再是主验收接口；其历史结果仅保留用于回归比较。
- 每轮最少接收 `727727` 包，捕获丢包率最坏 `0`、解析拒绝率最坏 `0.000207495`，关键流覆盖最小 `1`，GPU 最少评分 `814` 流，批次失败/回退/预算超限均为 0。
- 最终临时组合为 `batch=128`、`feature_flush=1000us`、`runtime=thread_all`；GPU 批次往返 P99 最坏 `87176.5us`，内部特征入队 P99 最坏 `2866.45us`，均通过临时硬门。该结果只证明临时被动捕获与双机推理链路可用，不证明独立 10GbE 生产 P99。
- `final_pareto_ingestion_allowed=false`，不得将 1GbE 管理口结果冒充独立 10GbE 生产证据。

## 最终 10GbE 双口就绪状态

- 生产接口硬门固定为：两个不同物理接口、速率至少 `10000Mbps`、无管理桥、无 IP、无默认路由；当前候选对为 `ens8f0/ens8f1`。
- 当前硬件合格接口 `2` 个、合格接口对 `1` 对；连同冻结阈值检查后的完整合格接口对 `0` 对，因此 `final_live_run_allowed=false`。
- 在线脚本只要证据合成失败也会返回非零状态，不再允许“原始运行完成但严格证据不合格”被误报为成功。

## 证据索引

| 证据 | 路径 | SHA-256 |
| --- | --- | --- |
| A01--A10 三路只读取证回执 | `docs/experiments/2026-08-13-algorithm-evidence-access-three-route.json` | `87346b16e75a78962444623cda46858245477ad55e67bb97434d19218373171b` |
| 跨轮稳健运行时选择 | `/home/wangwt/task/datasets/replay/hft_runtime_robust_selection_rc1_20260729.json` | `3317b90e117c5ae84b5b1687c0df4290160eedd6888f175c922ed41f35ee45ad` |
| 最终虚拟链路诊断三轮 | `/home/wangwt/task/datasets/replay/hft_vdiag_thread_cpu0_3_final_v3_20260729.json` | `8470365c4e24c61b75ea90f08aa2c3cb74d6cabadc629fea55f86acce996ed87` |
| Python 推理节点资源三轮 | `/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/runs/resource_confirmation/hft_resource_thread_all_stable_v1_20260730/summary.json` | `e931f98c3ce745c3865e0fddab43daef77e930997df141f057c3beebd346e33e` |
| 物理机完整回放三轮 | `/home/wangwt/task/datasets/replay/hft_confirmation_rc2_stable_b128_thread_all_v1_20260730.json` | `a33c7d3849cb9231d9e23cbdc0421f84a8b1b834b9ca943ce7faecd5c716775b` |
| 双机恢复三轮 | `/home/wangwt/task/datasets/replay/hft_split_recovery_confirmation_rc1_final_v3_20260729.json` | `3f6dff1a18e00626727f3b27c9051dbb4294141e69238d730ec89ec5494286fb` |
| 内核接收时间戳驱动探针 | `/home/wangwt/task/datasets/replay/hft_timestamp_driver_probe_final_v3_20260729/metrics.json` | `fd3723cae238c37e7fcc69eed48b1fb9186fb9b0a7ef18221f769ea883e95649` |
| 最新 10GbE 双口预检包 | `/home/wangwt/task/datasets/replay/hft_10gbe_requalification_ens8_v1_20260730` | `16fc6db237e0579009e08ba335e5ee70afb019ebd19dea7d7b8abc2f07fe151c` |
| 最终 10GbE 双口就绪审计 | `/home/wangwt/task/datasets/replay/hft_10gbe_requalification_ens8_v1_20260730/summary.json` | `16fc6db237e0579009e08ba335e5ee70afb019ebd19dea7d7b8abc2f07fe151c` |
| xdp-skb 三轮物理诊断 | `/home/wangwt/task/datasets/replay/hft_xdp_skb_stability_v1_20260730/summary.json` | `8567cb456cf35781607d13661696a089af0e1a9a01a19e834a4079a146442386` |
| xdp-skb 同场跨主机资源 | `/home/wangwt/task/datasets/replay/hft_xdp_skb_joint_resource_v1_20260730/joint_summary.json` | `8935a0f46403302a2cfaf86cc220650bfe8a64ebf78a568aeaaea3d167864df7` |
| xdp-skb 运行时抓包回退三轮 | `/home/wangwt/task/datasets/replay/hft_xdp_skb_capture_fallback_v1_20260730/summary.json` | `7292d6763ecacc3af631786156650b33329a129c41fdfb9ad6c4ddf3b860e55f` |
| ens9f0 临时被动影子捕获 | `/home/wangwt/task/datasets/replay/hft_shadow_confirmation_60s_stable_b128_thread_all_v1_20260730/summary.json` | `d31e8d24e7438422613d2a1674f3931948d48a4566083d3a779284240683ae06` |
| ens9f0 三候选运行矩阵 | `/home/wangwt/task/datasets/replay/hft_shadow_matrix_3x3_v3_vector_no_inner_flush_20260730/summary.json` | `808163ee2ec7291d96c727b25c3c3723d62b5fcb81a422566b876372abe8f714` |
| 旧版到新版基础特征映射 | `/home/wangwt/task/datasets/replay/hft_feature_equivalence_vector_v6_b128_stable_keys_20260730/base_mapping_comparison.json` | `e1b52d38cebf68696fea34c87fe95a2686b997bd8ebe3c4cf1dd4814c710358f` |
| 新版完整特征确定性 | `/home/wangwt/task/datasets/replay/hft_feature_equivalence_vector_v6_b128_stable_keys_20260730/determinism_comparison.json` | `3fde356b5d6f84074cf9ee7d868c213dfb1daaa1e033b30320bee3440f12351e` |
| 当前推理运行清单 | `/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/runs/split_deployment/runtime_manifest.json` | `27cfd83ca869ac1a247e5e74c499528bd7ff82a34dc6aed17b71a35af2de2c84` |
| 远端发布审计 | `/home/wangwt/task/datasets/replay/hft_remote_release_audit_rc1_xdp_fallback_v2_20260730.json` | `104640fe9e846da13c829d0a99331f54bdb40268db3d2db90d97c5ca5da330e3` |
| DPDK 双 PF 1 Mpps 重复运行完整清单 | `/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260731T041221978805926Z/evidence_sha256_complete.txt` | `75b10aad82866378b071d8119cfacbb424027560bd8e3ea72fd1ceb98eab9b2e` |
| DPDK 5 Mpps 前置阻断完整清单 | `/home/wangwt/task/datasets/replay/hft_dpdk_preflight_blocked_20260731T040339734758305Z/evidence_sha256_complete.txt` | `8201d7389e5dc3c694d23365f45d587d5201884514d452fa3f945b405988d843` |

## 下一执行门

1. 由业务方冻结目标 Mpps/Gbps、解析拒绝率、端到端 P99/P999 和最小时长；不得从 0.01 Mpps 诊断结果反推生产门限。
2. 在冻结生产负载下对 `xdp-skb` 到 `af-packet-ts` 的已实现运行时回退做压力复测，单独报告切换损失，不复用正常路径零丢包证据。
3. 在冻结目标负载下执行至少三次独立 Rust 发包/抓包，保留分层 NIC、ring、parser、HFT、sender 与跨主机资源原始证据。
4. 完成 24 小时影子和 72 小时生产长稳门，期间要求零残留 XDP 程序、零未解释丢包和时间戳异常。
5. 全部门通过后才重新计算最终 Pareto 前沿并变更 `final_pareto_eligible`。

## 2026-07-30 10 Mpps Rust 快路径整改进展

### 已落地代码

- XDP RX 热路径：descriptor/refill 预分配、稠密 frame 所有权位图、借用 UMEM 回调、8 队列独占线程、NUMA 固定和忙轮询。
- R0 发生器候选按停止规则依次实现并验证：PCAP/`sendmmsg`、`PACKET_TX_RING`、TX coalescing 24/0 us、AF_XDP TX COPY-mode；候选总数受控，没有在失败分支无限调参。
- DPDK 路线：隔离构建 DPDK 25.11.2，新增独立 `rust/hft-dpdk` crate、burst C shim、Rust EAL/双线程/硬门禁/证据输出，以及双 PF 失败自动回绑脚本。
- DPDK 不进入现有 `hft-capture` workspace；普通环境仍保持原 8 个 Rust 测试与 release 构建可用。

### R0 实验边界

| 后端/目标 | 最低实发 Mpps | 发送/接收差值 | 丢包 | P99/P999(us) | 结论 |
| --- | ---: | ---: | ---: | ---: | --- |
| XDP 借用快路径 0.5 Mpps | 0.504954 | 0 | 0 | 11/18 | R0 PASS |
| XDP 借用快路径 1 Mpps（新发生器） | 1.009971 | 0 | 0 | 10/14 | R0 PASS |
| `sendmmsg` 目标 5 Mpps | 2.655573 | 163937 | 297124 | 2904/8591 | FAIL |
| `PACKET_TX_RING` 目标 5 Mpps | 2.750788 | 11 | 22 | 22/29 | FAIL |
| TX coalescing 24/0 us | 2.680883/2.680703 | 0/0 | 0/0 | 17/23、16/22 | FAIL |
| AF_XDP TX COPY-mode | 2.778831 | 0 | 0 | 13/23 | FAIL |

当前证据证明 Rust 借用式 XDP RX 在 1 Mpps 内不是瓶颈，也证明 BCM57810 的 Linux/generic/COPY TX/RX 路径约 2.8 Mpps 触顶；不能据此声称 5 或 10 Mpps。generic 分支已停止，后续只保留 native AF_XDP 网卡与 DPDK bnx2x 两个架构候选。

### DPDK 就绪但未运行

- 两个 PF：`0000:cb:00.0/0000:cb:00.1`，同一 BCM57810、NUMA 1、固件 7.15.x、10GbE UP。
- bnx2x PMD 无 RSS；R0 采用单 RX 队列，若通过再用软件无锁环分片解析。
- SR-IOV 不可用，必须让两个 PF 同时脱离 `bnx2x`；预检标记 `explicit_approval_required=true`。
- DPDK build manifest SHA-256：`d061fef51ea303fccfe4d735893fb177e08cec414784205c91e2073f862de332`。
- Rust DPDK 二进制 SHA-256：`ad95644fe6240d7cd0088e7a513c9431b695328d1c9e5d6fbfdde1b69925aac5`；2 个 crate 单测通过。
- 只读预检：`/home/wangwt/task/datasets/replay/hft_dpdk_preflight_20260730T141500Z/preflight.json`，SHA-256 `b02c13630d1c08572be740a8361ed274bb2ab2a49168f2adfd6feeb689225c4e`。
- 回退脚本未授权时已验证拒绝执行；目前网卡仍由 `bnx2x` 驱动，未加载 UIO、未分配 hugepage、未执行 DPDK 数据面。

### 当前门禁

- 已冻结 DPDK R0 1/5/10/12 Mpps、64 B、burst 256 配置。
- 下一步需要明确批准 ens8f0/ens8f1 短暂中断，先执行 1 Mpps；只在零差值、零 DPDK drop、P99/P999 和速率全部通过后逐级升级。
- 即使 12 Mpps R0 通过，`full_pipeline_qualified` 与 `final_pareto_ingestion_allowed` 仍为 false；必须继续完成解析、特征、预算、A09、回退压力与 24/72h 门。

### 2026-07-30 DPDK 非中断复核

- `scripts/run_dpdk_bnx2x_validation.sh` 已通过 `bash -n`；未设置
  `HFT_ALLOW_DISRUPTIVE_DPDK=YES` 时以退出码 `13` 拒绝执行。
- 拒绝门复核后，`ens8f0/ens8f1` 仍为 `UP,LOWER_UP` 且均由 `bnx2x`
  驱动；NUMA 1 的 2 MiB hugepage 数仍为 `0`，`uio_pci_generic` 未加载。
- DPDK 只读预检 `3/3`、`hft-capture` Rust 测试 `8/8`、独立
  `hft-dpdk` Rust 测试 `2/2` 通过；DPDK release 二进制 SHA-256 仍为
  `ad95644fe6240d7cd0088e7a513c9431b695328d1c9e5d6fbfdde1b69925aac5`。
- 一次手工复现命令把 `PKG_CONFIG_PATH` 误写为不存在的
  `lib64/pkgconfig`，该次失败不计为代码缺陷或测试失败。项目固定入口
  `scripts/build_hft_dpdk.sh` 使用正确的 `lib/pkgconfig`，随后从项目入口
  完成测试与 release 构建。
- DPDK 脚本、配置、Rust 源码和工程文档共 `19` 个受控文件已逐文件
  SHA-256 核对，本地与 `10.0.5.8` 完全一致。
- `10.0.5.103:25450` 当前仍在 SSH banner exchange 阶段超时，因此本轮
  新增 DPDK 源码尚未完成 GPU 节点同步；不得报告“三端同步完成”。
- 本轮没有执行双 PF 解绑、UIO 绑定、大页分配或 DPDK 数据面实验；
  `final_pareto_eligible` 继续保持 `false`。

## 2026-07-31 DPDK 双 PF 实测最终状态

本节取代上文“DPDK 就绪但未运行”的旧状态。已依据明确授权在
`ens8f0/ens8f1` 执行 DPDK 双 PF 数据面实验；GPU 服务继续暂停，本轮未连接或同步
`10.0.5.103`。

### 当前稳定交付

- 活动 DPDK 为原始已校验 25.11.2 bnx2x，manifest
  `experimental_bnx2x_rss=NO`；失败的 RSS 补丁只作为候选代码留存，默认构建会撤销。
- 当前 Rust DPDK release SHA-256：
  `3afc47faf9899ce5788afaad0e2590fec0e2b480a1eb86235919cd84e5c357b9`。
- 最终 Q1/B128/1 Mpps：
  `/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260731T025831490425073Z`。
  15,150,080 发/收完全一致，`imissed/ierrors/rx_nombuf=0`，最低 1 秒
  TX/RX 为 `1.009976/1.009962 Mpps`，P99/P999 为 `81.802/438.530 us`，
  `r0_capture_only_qualified=true`。
- 最终 result SHA-256：
  `9a1769961de66610b5406450d07b12c7a60fb73f9b7a4da5fa7f7cf2ae9b9447`；
  证据清单 SHA-256：
  `7eec7ee9da73c102df7d6c60fbb29f48af9b1e594d130193bfebabe163e0d055`，
  清单内文件已全部 `sha256sum -c` 通过。
- 每轮退出均核验双 PF 回绑 bnx2x、接口 UP/10GbE、hugepage 恢复为 0。
  最终审计另发现 `/var/run/dpdk` 遗留 14 个 EAL fbarray 元数据目录；确认
  无 HFT DPDK 进程后已按严格 HFT 运行前缀定向清理，并把该目录纳入后续
  自动回退硬门。修复记录见
  `engineering_fixes/2026-07-31-dpdk-runtime-prefix-cleanup.md`。

### 已拒绝分支

| 候选 | 证据 | 结果 | 停止理由 |
| --- | --- | --- | --- |
| 单队列 B128，5 Mpps | `hft_r0_dpdk_20260731T014313443709656Z` | 最低约 2.570 Mpps，P99 475.742 us | TX/RX 单核触顶 |
| Q2，5 Mpps | `hft_r0_dpdk_20260731T024226277475329Z` | 2.593 Mpps，丢 2,833，RX `[38886459,0]`，P99 1066.602 us | 目标速率、零丢包、RSS 覆盖、时延均失败 |
| Q2 RSS 冒烟，1 Mpps | `hft_r0_dpdk_20260731T024920052633840Z` | 零丢包但 RX `[15150080,0]`，P99 129.209 us | UDP RSS 配置修复后仍无队列覆盖 |
| Q2 实际 MAC 冒烟，1 Mpps | `hft_r0_dpdk_20260731T025306882795396Z` | 零丢包但 RX `[15150080,0]`，P99 130.182 us | 排除混杂目的 MAC 后仍失败 |
| RT10 | `hft_r0_dpdk_20260731T022059475661619Z` | 未发包；`RLIMIT_RTPRIO=0` | 主机不允许 SCHED_FIFO；前置门禁现已在 PF 解绑前拒绝 |

Q2 未通过，因此 10/12 Mpps 没有执行。当前 BCM57810 + bnx2x 的 DPDK 多 RX
分支和 Linux generic/COPY 分支均已按停止规则关闭；不能把 1 Mpps Q1 结果外推为
5/10 Mpps。

### 代码与质量门

- `hft-dpdk`：格式、5/5 单元测试、Clippy `-D warnings`、release、静态 PMD
  与符号门全部通过。
- `hft-capture`：格式、8/8 release 测试、HFT-MGBS 自身 Clippy
  `-D warnings` 全部通过。
- Clippy 构建仍显示只读上游 `traffic-analysis-platform/rust` 的 15 条既有警告；
  未修改该目录，且这些警告不属于 HFT-MGBS lint 失败。
- 所有修复均已写入 `docs/engineering_fixes`；本地只同步代码、配置、测试和文档，
  数据、二进制与运行证据只保留在物理机。

### 工程决策

当前硬件上继续微调 Rust burst、队列数或时延阈值不会产生 10 Mpps 合格证据。
下一步若仍要求 10 Mpps，必须先更换为经实测支持多 RX RSS 与 native
AF_XDP zero-copy 或成熟 DPDK PMD 的抓包硬件/驱动，再从 1→5→10 Mpps 重新执行同一
硬门；在此之前保持 `full_pipeline_qualified=false`、
`final_pareto_ingestion_allowed=false`。

## 2026-07-31 DPDK 双 PF 授权复测补充（不改变最终资格）

- 在物理机本地光纤回环上，以
  `ens8f1/0000:cb:00.1 TX → ens8f0/0000:cb:00.0 RX` 执行
  Q1/B128/1 Mpps；`Q1` 是队列数，不是单 PF。
- 固定 CPU 集合首次不满足空闲门后，没有停止外部进程；重新筛选并使用
  `main=53/RX=44/TX=55`。15,150,080 包发收完全一致，最低 1 秒 TX/RX
  `1.009959/1.009965 Mpps`，零 `imissed/ierrors/rx_nombuf`，
  P99/P999 `81.224/434.806 us`，重复通过 R0 capture-only 门。
- 最大 RSS 40,460 KiB、进程 CPU 100% 等资源数据只作为观测，不冒充尚未冻结的
  发布资源门。
- 5 Mpps 最终复检时 CPU 44/53 及其部分 SMT sibling 未达到 95% 空闲门，
  因而在 PF 解绑前停止；runner 未启动，没有新增 5 Mpps 测量。
- 有效运行和前置阻断的 base/complete 清单均通过 `sha256sum -c`。退出后两个
  PF 恢复 bnx2x/10GbE/UP，hugepage、UIO、本次 EAL 前缀和 HFT 进程均为 0。
- DPDK 执行期间 GPU 节点保持暂停且未触碰；数据与原始运行证据只保存在物理机，
  本地仅新增代码侧实验文档。
- 详细证据见
  `docs/experiments/2026-07-31-dpdk-dual-pf-authorized-repeat.md`。当前仍为
  `full_pipeline_qualified=false`、`final_pareto_ingestion_allowed=false`。

## 2026-07-31 GPU 25150 恢复与 DPDK 发布门整改

- `10.0.5.103:25150` 已在严格主机密钥检查下使用本机私钥认证成功；50051
  Python 服务稳定监听，候选 A09 health 为 `ok=true`。
- A09 实际是 CPU ExtraTrees，`algorithm_device=cpu`、
  `gpu_required=false`；不能因为服务位于 RTX A6000 主机就声称使用 GPU 加速。
- GPU runtime manifest 配置了物理端 `10.0.5.8:50052`，但两次 socket
  快照和服务日志均没有成功连接证据；当前是 GPU 服务独立健康，不是双机在线链路通过。
- 本地/GPU 受控清单为 219/165 个文件：156 个同路径同哈希、54 个本地独有、
  9 个同路径漂移；运行中的 `hft_mgbs` Python 包 25 个文件一致，但不得宣称
  三端全源码一致。
- DPDK 新增 schema 5 原始结果、release gate v2 冻结配置、派生资源验收器和
  fail-closed runner。TX/RX、CPU、RSS、HugePage、恢复与证据完整性现在分层判定；
  原始 Rust 结果不再自行宣称完整 R0 或最终 Pareto 通过。
- 本地 DPDK 验收/runner/CPU 空闲预检测试 21 项通过，runner `bash -n` 和 Python
  `py_compile` 通过。
- release gate v2 仍为 `binary_freeze_pending=true`：必须先在物理机完成 schema 5
  release 构建并回填二进制 SHA-256；pending 期间 runner 只允许 non-mutating
  preflight，任何双 PF 变更都会提前拒绝。
- 外部写入审批通道因 Codex 当前用量限制拒绝 `scp`；上述新 DPDK 代码尚未同步到
  10.0.5.8，远端 Rust fmt/test/clippy/build 和新双 PF 运行均待执行。历史 1 Mpps
  资源继续保持 observational，不被新门限追认。
- 审计曾用两个错误协议请求使 GPU 服务内存 `failures=2`，无日志或文件变化；
  后续正式运行必须用新 run ID 隔离，不能把该计数纳入生产可靠性结论。
- 详细记录：
  `docs/engineering_fixes/2026-07-31-dpdk-runner-release-fail-closed.md` 与
  `docs/experiments/2026-07-31-gpu-service-25150-reactivation.md`。
- 当前仍为 `full_pipeline_qualified=false`、
  `final_pareto_ingestion_allowed=false`。

## 2026-08-12 DPDK Q1 实机推进与当前阻断

- 物理机 release 构建已完成：Rust fmt、12 项单元测试、clippy `-D warnings` 和 release
  build 通过；二进制 SHA-256 为
  `3c655ef3684f8157e52d12a89157a6c1c5f0d586fe493d610b60a2fc796ec0a6`。
- DPDK Python/runner 合同测试在证据封存修复后为本地与物理机 31/31 通过；本地代码保留
  策略为 0 违规。远端 `.deps` 是构建工具链，不属于“本地只保留代码”策略的通过证据。
- 首次正式尝试因 CPU28/36/92 超过 5% 在 PF 解绑前阻断；10 秒初筛后改为 29/43/41，
  第二次又因 CPU29 突增到 88.17% 阻断，两次均为 `mutations_performed=false`。
- 30 秒 NUMA1 稳定性扫描后把同一候选映射固定为 50/52/54，SMT 同胞为 106/108/110；
  算法、二进制、速率、burst、队列和全部硬阈值未变，不计为新算法候选。
- 一次正式诊断运行完成 15 个窗口：TX/RX 最低约 1.009920/1.009925 Mpps，收发
  15,150,080 包，数据面计数无丢包，P99/P999 约 20.92/80.55 微秒，进程 CPU 约
  0.97 核、RSS 40,492 KiB、墙钟开销约 3.89 秒；数据/资源门通过且恢复账本全绿。
- 上述诊断运行在证据封存阶段触发 Bash 空数组 nounset，并错误返回 0；虽然独立检查确认
  两口已恢复 bnx2x、UP/10GbE/carrier，全部 NUMA 巨页为 0、无 DPDK/UIO 残留，但该次
  没有完整哈希和 acceptance，明确不得作为发布验收。
- runner 已显式初始化证据数组，并增加清理期 EXIT 应急保护（未预期致命错误返回 99）
  与 evidence build 非零返回 17；修复后 runner SHA-256 为
  `c2f3945a05f7d59ed683dde8f1ac6ac6620a3a4cc0606418b7a79ea00a076d08`。
- 修复后的正式重跑仍被 CPU110 单秒 37.76% 峰值阻断；有界双预检一次通过、一次因
  CPU108 10% 峰值失败。Kubernetes CPU Manager 为 `none`，无 isolcpus/nohz_full，根
  cpuset 和默认 IRQ 亲和均覆盖 0–111，因此没有可直接复用的隔离核。
- 不采用“反复采样直到偶然通过”的选择偏差。下一步需要获准临时 CPU shielding，并把
  业务线程迁移/IRQ 亲和、DPDK 运行和完整恢复纳入同一 fail-closed 账本；未获授权前不执行。
- GPU SSH 入口 `10.0.5.103:25696` 已使用
  `ClearAllForwardings=yes` 复核；PID 1888 正监听 `0.0.0.0:50051`，NDJSON health
  返回 `ok=true`、候选 A09、`algorithm_device=cpu`、`gpu_required=false`。本轮先用 HTTP
  误探测一次使累计 `failures` 从 0 变为 1；正式实验必须按计数增量或新 run/service
  生命周期隔离，不能把该探针错误归因于推理链路。
- 详细修复见 `2026-08-12-dpdk-q1-cpu-remap.md` 与
  `2026-08-12-dpdk-evidence-empty-array-exit-code.md`。当前仍为
  `r0_capture_only_qualified=false`、`full_pipeline_qualified=false`、
  `final_pareto_ingestion_allowed=false`。

## 2026-08-01 GPU 25696 入口与服务恢复

- GPU SSH 入口已切换为 `10.0.5.103:25696`，本机公钥和严格主机密钥检查直连成功。
- GPU 容器重启后 50051 未自动监听；使用受控启动脚本恢复后，实际 Python PID 1888
  监听 `0.0.0.0:50051`。
- NDJSON 健康检查返回 A09 `ok=true`、`failures=0`；运行时仍为 CPU ExtraTrees，
  `gpu_required=false`。
- 当前未观察到连接 `10.0.5.8:50052` 的 ESTABLISHED socket，故只确认 GPU 本地服务
  恢复，不确认双机在线链路。
- 同步脚本和两份部署配置已统一为 SSH 端口 25696；修复详情见
  `docs/engineering_fixes/2026-08-01-gpu-ssh-port-25696-service-recovery.md`。
- `full_pipeline_qualified=false`、`final_pareto_ingestion_allowed=false` 保持不变。

## 2026-08-12 DPDK 发布门终审加固

- Rust worker 已具备 panic 安全的 TX 完成守卫和生命周期 watchdog；runner 新增运行
  硬超时以及清理期间二次信号屏蔽，避免 RX 永久等待或双 PF 遗留 UIO。
- HugePage 证据改为全 NUMA node 计数；接口发布基线冻结 UP、MTU、txqlen、features、
  coalesce、ring、channels 与 qdisc，恢复后除动态 stats 外要求快照一致。
- iproute2 策略规则同时识别 `iif/oif` 与 `iifname/oifname`。
- runner、validator、composer、两项 preflight 和 DPDK manifest 均纳入配置哈希绑定；
  远端 release 二进制已经构建并冻结。
- 最终 acceptance 改为封存清单核验后的派生回执，并明确
  `standalone_receipt_trusted=false`；不能把未封存回执单独作为资格证据。
- 本地与物理机 DPDK 相关合同测试在后续回归修复后为 31 项通过，Python 编译检查和
  本地策略检查通过；实机运行已产生诊断数据，但完整发布 acceptance 仍被 CPU 隔离条件阻断。
- 详细记录见
  `docs/engineering_fixes/2026-08-12-dpdk-release-lifecycle-sealing.md`。
- 当前仍为 `full_pipeline_qualified=false`、
  `final_pareto_ingestion_allowed=false`。

## 2026-08-12 DPDK Q1 正式 acceptance 与后端收敛

- 终审加固后的正式运行目录为
  `/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260812T075417740346047Z`；
  派生回执为 `runner_qualified=true`、`r0_capture_only_qualified=true`，且
  `errors=[]`。
- 15 个完整窗口的 TX/RX 最低速率为 `1.009920/1.009927 Mpps`；收发均为
  `15,150,080` 包，差值、`imissed`、`ierrors`、`rx_nombuf`、`oerrors` 均为 0。
- P50/P99/P999 为 `9.184/22.346/82.223 us`，最大 `415.045 us`；进程 CPU
  `0.97` 核，最大 RSS `40,360 KiB`，使用 1 GiB HugePage，墙钟附加开销约
  `3.880 s`。
- acceptance、base 清单、complete 清单 SHA-256 分别为
  `1e7a68009c04e1165a14a2784ba92b6d52eddcb728cb3e06fafe531331a5383e`、
  `2ed05399a2fed3948e3d5bbd05920266e081df420729ae26bade678f5abfbbbe`、
  `2ed05399a2fed3948e3d5bbd05920266e081df420729ae26bade678f5abfbbbe`；两份清单
  独立校验通过。
- 运行、恢复、validator 与两级哈希检查状态均为 0；独立复核确认双口已恢复
  bnx2x/UP/10GbE/carrier，node0/node1 HugePage 均清零，无 UIO/HFT DPDK 残留。
- 上文“仍需 CPU shielding 才能运行”的阻断已被本次完整正式运行取代；不执行会影响
  Kubernetes/ClickHouse 等业务线程的全局 shielding。
- bnx2x PMD 的正式能力边界不支持 RSS/TSS，且历史 Q2 实测持续只有 queue0 收包；
  Q2 多 RX 参数分支停止，不再计入活跃候选。Q1/1 Mpps 只取得 R0 capture-only
  资格，不满足 12 Mpps headroom。
- 下一有界候选为 `TPACKET_V3 + PACKET_FANOUT_HASH/QM`；若它也无法跨越硬门，
  当前硬件路线即收敛为“需要更换支持 native AF_XDP zero-copy 或成熟多队列 RSS PMD
  的网卡”，不继续无界调参。
- 详细数据见
  `docs/experiments/2026-08-12-dpdk-q1-release-accepted.md`。当前保持
  `full_pipeline_qualified=false`、`final_pareto_ingestion_allowed=false`。

## 2026-08-12 TPACKET_V3 有限搜索完成

- HFT 自有 Rust 已实现 TPACKET_V3 mmap、PACKET_FANOUT_HASH/QM、固定 CPU、测试
  签名计数、P99/P999、PACKET_STATISTICS 与 per-socket 混杂 membership；3 项单测、
  clippy `-D warnings` 和 release build 通过，二进制 SHA-256 为
  `a84fcd0e7c680c4b6d930535c0471e26e84898ee0090aefb9d2b269d3caab658`。
- 默认 RX=453 的 1 Mpps 缺口 29,090 与驱动 `rx_discards` 精确一致；临时 RX=4078
  后 4/2 worker 均完成 15,150,080/15,150,080、最低完整秒 1.009664 Mpps、驱动与
  TPACKET 零丢包，但 P99/P999 分别为 704/726 与 673/708 us，未过时延门。
- 8-thread/8-queue 内核 pktgen 上探只达到约 2.784 Mpps；签名接收
  41,739,312/41,762,153，缺口 22,841 与驱动 `rx_discards` 增量精确相等。此时
  P99/P999 为 49/64 us、TPACKET 自身 drop=0，但零丢包和 12 Mpps 均失败。
- 所有轮次退出后 ens8f0 恢复 RX=453、promiscuity=0，pktgen 模块无残留。抓包后端
  预算 6/6 已完成裁决、活跃后端 0；这是后端层预算。后续 TPACKET 突破微候选实际
  使用 2/3，第三项因 offered>=12 Mpps 前提不成立而按停止规则未运行。当前硬件不存在
  满足全部硬门的最终 Pareto 点。
- 下一有效工程变更是新增/更换支持 native AF_XDP zero-copy 或成熟多队列 RSS DPDK
  PMD 的发生器/抓包网卡；不再继续 worker/block/coalesce 参数扫描。详见
  `docs/experiments/2026-08-12-tpacket-v3-finite-search.md` 与
  `configs/capture_backend_search_v1.json`。

## 2026-08-12 吞吐突破复核与硬件迁移门

- 新增 `run_tpacket_v3_breakthrough.sh`，把发生器改为 8 条固定 UDP 流，使用
  `clone_skb=64`，接收端使用 8 路 `PACKET_FANOUT_QM`；ens8f0 IRQ 固定到
  CPU 28--35，接收 worker 固定到 36--43，ens8f1 TX IRQ 与 pktgen 固定到
  44--51。运行器会快照并恢复 16 个 IRQ、RX ring、coalesce、链路和 pktgen
  模块状态，IRQ 漂移或恢复失败均不得通过。
- B1（burst=1）实发/实收 `40,173,943/40,173,943`，最低完整秒
  `2.791521 Mpps`，驱动/socket 丢包 0，P99/P999 `94/131 us`；B2
  （burst=8）实发/实收 `41,691,559/41,691,559`，最低完整秒
  `2.790743 Mpps`，丢包 0，P99/P999 `93/126 us`。两轮 IRQ 全程稳定且主机
  恢复验证通过，但发生器都只有约 `2.794 Mpps`。
- B3 仅允许在 offered>=12 Mpps 且 RX 出现丢包时运行；前提未成立，故按冻结
  停止规则不运行。TPACKET 搜索实际使用 2/3 个候选，没有为追求好结果扩展预算。
- 双 PF DPDK 12 Mpps release-gate 先被一次 CPU 52 瞬时 9.09% 占用安全阻断，
  原配置复采样通过后才执行数据面。正式运行发送/接收均为 `38,547,638`，差值及
  `imissed/ierrors/rx_nombuf/oerrors` 均为 0，但最低 TX/RX 仅
  `2.569692/2.569457 Mpps`，P99/P999 `522.373/529.255 us`，因此未通过。
- DPDK 正式运行目录为
  `/home/wangwt/task/datasets/replay/hft_r0_dpdk_20260812T092747626930383Z`；
  acceptance/result/完整清单 SHA-256 分别为
  `673ef84fd3f4e33fb3181df14257ed0739dc540f2f1b85c3e60a2d446467599a`、
  `c21249871b7bf9f33175a3355b8d2dcbe05796eec4318016ac25326dad76c088`、
  `618b6ecc66da9fc506a5136899ebd0d7dd912559a7cc2bec6d4e5bf7edaf157d`。
  `restore_status=0`、`restoration_verified=true`；双口已恢复 bnx2x、UP、10GbE、
  RX=453、promiscuity=0，无 UIO/DPDK/pktgen 残留。
- 当前网卡的 bnx2x PMD 官方不支持 RSS/TSS，无法靠多队列横向扩展；当前主机只有
  这一块双口 10GbE BCM57810，另有的仅是 4 个 BCM5719 1GbE 口。新硬件必须通过
  `configs/capture_hardware_upgrade_gate_v1.json`：强制 native XDP、强制
  AF_XDP zero-copy、DPDK RSS/TSS、至少 8 RX/TX 队列，并由独立发生器完成三次
  12 Mpps 零丢包 R0，之后才继续 R1--R4。
- `full_pipeline_qualified=false`、`final_pareto_ingestion_allowed=false` 保持不变。

## 2026-08-12 统一审计与瓶颈归因

- 新增 `release_manifest_v2.json` 与 `audit_unified_release.py`，把算法搜索、抓包搜索、
  硬件门、DPDK 1/12 Mpps、TPACKET B1/B2、运行时身份、资源、关键流、回退和
  R1--R4 置于同一 fail-closed 发布判定。`audit_complete` 与
  `production_release_accepted` 已分离，缺少生产证据时 CLI 返回非零。
- 新增 `analyze_capture_bottleneck.py`。物理机对三份现有观测的实际运行输出为
  `analysis_valid=true`、`eligible_observations=3`、`generator_limited=true`、
  `single_queue_path_limited=true`、`capture_limited=false`、`target_unproven=true`；
  明确记录 `extrapolation_performed=false`。
- 瓶颈分析证据及 SHA-256：
  `/home/wangwt/task/datasets/replay/hft_capture_bottleneck_analysis_v1_20260812.json`，
  `2a63f2576cf66865dbf711b5a1964d4cd54f047c0cb4c94f95afcb5742567ddd`。
- 统一审计已通过四份 acceptance、四份完整清单和主机恢复核验；当前
  `offline_algorithm_candidate_accepted=true`、`host_restoration_qualified=true`，
  但 12 Mpps R0 可行集为空，GPU 运行身份和 R1--R4 未验证，所以最终仍 false。
  审计证据及 SHA-256：
  `/home/wangwt/task/datasets/replay/hft_unified_release_audit_v1_20260812.json`，
  `d6bb2afec89320c07853060856706a2346ccced2e7324971c5c7b4efed38b013`。
- GPU 25696 本轮只读确认 50051 由 Python PID 1888 监听；SSH 随后间歇超时，未能把
  manifest、PID 命令行和协议 health 绑定为同一当前证据，因此不能沿用旧 manifest
  哈希宣称运行身份合格。
- 本地与物理机相关回归均为 43/43 通过；新工具不进入 Rust 热路径。下一有效实验是
  独立 15 Mpps 发生器加支持强制 native AF_XDP zero-copy、RSS/TSS 和至少 8 队列的
  新网卡，先完成三次 12 Mpps R0，再解锁 R1--R4。

## 2026-08-13 stock TCP RSS Q2 最终实测与分支封闭

- 前三次 Q2/TCP 诊断都在 PF 变更前被 CPU/SMT 5% 空闲门拦截。第四次复采样中
  CPU31/32/34/35/37 及其 sibling 的 5 个 1 秒样本全部通过，最高为 4.04%，因此
  runner 按冻结合同实际执行了双 PF 对称 RXQ2/TXQ2、256 个合法 IPv4/TCP 五元组、
  1 Mpps、15 秒诊断。
- 发送和接收均为 `15,150,080` 包，15 个完整共享窗口的最低 TX/RX 都为
  `1.009920 Mpps`，NIC 丢包和错误均为 0；P99/P999 为 `11.004/151.453 us`。
- 两个 TX 软件队列各发送 `7,575,040` 包，但 RX 软件队列为
  `[15,150,080, 0]`。因此不是 UDP 单流、目的 MAC、发生器不均衡或 Rust FFI 热路径
  导致的“假单队列”；stock bnx2x 的隐式 TCP RSS 仍没有产生多 RX 队列覆盖。
- `diagnostic_passed=false`、`q2_5m_unlocked=false`、`q4_unlocked=false`，冻结的
  `q2_failure_stops_branch=true` 生效。当前 BCM57810 不再运行 Q2/5 Mpps、Q4/10 Mpps
  或额外 burst/RSS 参数扫描。
- 13 步恢复账本全部通过；双 PF 回绑 bnx2x，ens8f0/ens8f1 恢复 UP/LOWER_UP，
  node0/node1 HugePage 都恢复为 0。完整证据清单 `sha256sum -c` 通过。
- 证据目录为
  `/home/wangwt/task/datasets/replay/hft_tcp_rss_q2_20260812T165732153923663Z`；
  acceptance/result/恢复账本/完整清单 SHA-256 分别为
  `732fbc815fa5099b93be6608d2875b67f2353a69b5fe5caeadcabb1918824448`、
  `54f6df71b49e1f21c4552416d3782b01a20e9fa0cf547308917063d6ebecf354`、
  `3cf1ca90777d036fe2a3b803fc3dee7b9d06e411ffd3934ed56447a2cd05db59`、
  `e63fe68bab32e4500e557c50c0b2bde8ef092775fb75fa19fc7ccde6d7eeb2ff`。
- GPU 主机 `10.0.5.103:25696` 的网卡/链路只读刷新在 120 秒连接窗口内无输出并超时，
  因此不能把 GPU 节点当作已验证独立高速发生器。下一工程动作已收敛为：在物理机空闲
  PCIe 插槽新增支持 native XDP、forced AF_XDP zero-copy、RSS/TSS 和逐队列计数的
  10/25GbE 以上 NIC，并配独立发生器完成三次 12 Mpps R0；GPU 保持 Python 推理职责。

## 2026-08-13 算法最优性、运行时和联合 Pareto 终审

- 算法搜索预算冻结为最少 8、最多 12、实际 10 个候选，禁止超预算继续调参。审计器
  不信任配置内声明的前沿或 winner，而是从 normal/fallback 成对指标重新计算硬门、
  严格 Pareto 前沿和 `epsilon=0.03` practical dominance。
- 当前只有 A09/A10 具备 normal/fallback 各三次的可重算指标；二者严格前沿为
  `[A09,A10]`，A09 是 finalist practical winner。A01--A08 缺成对指标，且十个候选
  都缺冻结的 evidence SHA，所以全 10 候选范围的算法最优性仍为 false，不能把 A09
  宣称为已证明的全局最优算法。
- 生产联合 Pareto 现强制重哈希 runtime decision receipt 和 raw windows，并重算吞吐、
  丢包、P99/P999、CPU/GPU/内存/显存、预算越界、关键流覆盖和回退恢复。native AF_XDP
  zero-copy 才能作为首选主路径；DPDK 仅允许独立 standby 或维护式回退。
- R1--R4 receipt 新增 code/input/stage/runtime/model 五类 identity manifest 的内容 schema、
  规范化哈希与 provenance 交叉验证；重复、乱序或重叠的 fault trial 不再计数。
- 三份当前状态已由 CLI 重新生成：runtime 为 `stop_fail_closed` 且无选中后端；联合
  Pareto 的 front 为空、champion 为 null；统一审计 `audit_complete=true`，但算法、R0、
  R1--R4、全流水线和发布均为 false。该状态是证据不足的正确拒绝，不是工具故障。

## 2026-08-13 新高速 NIC 到货验收链实跑

- 新增冻结合同、两份 JSON schema、Python 重算器、默认只读 runner 和 28 项负向/
  Linux 动态测试。合同同时排除现有六个旧 PCI 功能与 `14e4:168e/14e4:1657`
  设备 ID，避免插卡后 PCI 重枚举把旧 Broadcom 设备误判为新卡。
- XDP 与 DPDK receipt 均从每队原始包计数重算；要求至少 8 队各占总量 5%，拒绝
  `[N,1,1,...]` 假多队列。自洽回执状态只能是
  `self_consistent_capability_receipts_only`，不能获得硬件或生产资格。
- 最终代码同步后，物理机默认只读命令实际退出 `20`，状态为 `hardware_pending`、
  候选口 `0`、`mutations_performed=false`。最新证据目录为
  `/home/wangwt/task/datasets/replay/hft_new_nic_acceptance_20260813T002425014098848Z_BrmFie`；
  `evidence.sha256` 的 2 项全部复核通过，清单 SHA-256 为
  `ad58c9687524e2be9b163f0634cfd36ad9a576d3783a81f9a3fb92e33c05615d`。
- 物理机 28/28 新 NIC 测试、最终联合定向回归 55/55 和 `bash -n` 通过；本地
  27/27 可执行测试通过，Linux 动态用例
  按平台跳过。授权分支已加入外部可信 manifest SHA、独立冻结副本执行、全状态恢复
  指纹、TERM/KILL 超时及冻结入口切换顺序门；本轮没有设置授权变量，也没有执行
  PF/XDP/DPDK 状态变更。现场统一审计退出码 2（预期拒绝），重算 JSON 与冻结审计
  语义完全一致。
- 硬件门 SHA 已刷新为
  `e4b407961b0a3f4401c254393a8da89aa77fabf413bddc54b6f1b72a074dd14a`，并回填统一发布
  manifest。统一审计重算为 `audit_complete=true`、`accepted=false`，不存在哈希漂移，
  但算法、12 Mpps R0、R1--R4 与生产联合 Pareto 仍未通过。

## 2026-08-13 统一算法资格、R0 Campaign 与两阶段 Pareto 收敛

- 已冻结全 10 候选统一资格 campaign：10 个候选共享同一输入/代码/分组协议，分别运行
  `normal` 与 `fallback`，每种模式使用种子 `7/11/19`，合计 60 个原子可恢复作业；每个
  输出独立写入、复哈希、可断点续跑，并用 campaign 锁阻止重复训练。合同 SHA-256 为
  `2ea166044b6b7050c0c345ef6f7f537671d40169cfc02021dade6a2f38186941`。
- GPU 上 A01--A10 的旧 evidence 路径本轮全部存在并取得 SHA，但 A01--A08 仍是旧
  screening/formal 协议，不能与 A09/A10 的三次成对确认混合计入资格。新 campaign
  将旧文件只标记为 `legacy_discovery_only`，不会用“补旧哈希”冒充统一最优性证明。
- GPU 当前正在执行 CAEOS 正式数据处理，多个 worker 持续占用 CPU；本轮只同步和执行
  campaign dry-run，不启动 60 个训练作业，避免干扰已有任务。A6000 虽空闲，但当前
  ExtraTrees 候选属于 CPU 路径，不能把显卡空闲等同于可无冲突开跑。
- GPU campaign dry-run 还发现部署代码漂移：远端 `algorithm_search_rc1.json` SHA 为
  `b629ec321...`，冻结合同要求 `8ee9f2f0...`。该门在任何训练启动前拒绝，最终作业数
  保持 0/60；没有覆盖远端搜索文件，也没有为漂移状态重新签名。
- 已新增新 NIC R0 campaign：从 XDP 主路径 3 次、DPDK 回退 3 次、fallback 注入 3 次的
  原始逐队列计数、累计延迟直方图、发生器标记、资源样本与单调时钟重新计算所有硬门。
  当前物理机默认运行退出 20、`hardware_pending`、`mutations=false`；证据目录为
  `/home/wangwt/task/datasets/replay/hft_new_nic_r0_20260813T022841514083544Z_oySJ7i`，
  `evidence.sha256` 2/2 通过，清单 SHA-256 为
  `5717be463e2bf8cb4f27820fe5097578924ff32ab5aa6ab26ef3c6871525e4e3`。
- 修复了统一审计与 Pareto 的循环死锁：统一审计现在只密封候选完整证据并授予 Pareto
  ingestion 资格，不再自行宣称“已在 Pareto 被选中”；生产选择器必须重哈希至少两个
  完整候选并实际选出 Champion 后，才能输出 `production_release_accepted=true`。正向
  可达测试已覆盖，当前环境仍保持 unified RC=2、Pareto RC=10 的正确 fail-closed 状态。
- 本轮算法 campaign、R0 campaign、统一审计与 Pareto 联合回归 102/102 通过（Windows
  跳过 1 项 Linux 动态 runner）；扩展定向回归 149/149 通过（同一项跳过）。下一步是等
  CAEOS CPU 作业自然结束后执行 60 个统一算法资格作业，以及新 NIC/独立发生器到位后
  执行三次 12 Mpps R0；两条 campaign 的正式 receipt 冻结后再接入统一 manifest。

## 2026-08-14 2.79 Mpps 持续门收敛与算法 Campaign 入口修复

- 当前 BCM57810 环境的 `2.79 Mpps` 不能按“每个完整 1 秒窗且零丢包”的合同闭环。
  等速 busy-spin 与 timer-paced 两种独立发生节奏的完整窗下沿分别为约
  `2.616893/2.617057 Mpps`；后一轮 17 个完整窗仅 5 个达到 2.79。两种机制收敛到同一
  可持续下沿后已停止 rate sweep，不能把约 2.79 的部分窗口或平均值称为持续上限。
- timer-paced 有效诊断目录为
  `/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T154636Z_timerpaced_burst64_ratep5469_capacity_r2`。
  该轮共处理 `50,866,489` 包，固定 64 B parser 命中全部包、fallback/reject 均为 0；
  socket freeze/drop、feature/key queue drop、NIC `rx_discards` 增量均为 0。GPU 为
  `218/218` 批成功、`1704/1704` 关键流完成，GPU RTT P99/P999 为
  `16.596607/18.614589 ms`，退出后主机恢复账本通过。其 receipt 仍正确标记为
  `raw_diagnostic_only=true`、`runtime_identity_verified=false`、`full_pipeline_qualified=false`
  和 `final_pareto_ingestion_allowed=false`。
- 这次结果不改变 10/12 Mpps 生产合同，也未擅自把目标降为 2.60。当前双 BCM57810
  仍不支持 native AF_XDP forced zero-copy；DPDK Q1 约 `2.569 Mpps`，Q2 TCP RSS 实测
  第二 RX 队列为 0。满足 XDP 主路径、DPDK 备用及 8 队列合同仍需新增合格高速 NIC 和
  独立发生器。
- A01--A10 campaign 的 prepare CLI 已修复项目根自引导：清除 `PYTHONPATH` 后从项目根
  直接执行仍能生成未授权 dry-run 计划。campaign 合同测试 `25/25` 通过；prepare SHA
  为 `57e15ce255cc5174fae827b3daefbb2915ebe785638e33720ef719181e72c63a`，重冻结合同 SHA
  为 `0980bde18d354861d34c66d76d4a7ad5169a2e0c23a05445dbbeb2e00f215805`。
- 正式 60 单元算法比较当前仍不得启动：GPU 上 8 个 CAEOS worker 正持续占用 CPU；冻结
  训练 manifest 引用的 18 个 USTC-TFC2016 PCAP 全部缺失，而 UNSW 新鲜评估输入可读。
  此外 unified/Pareto 尚未直接重哈希正式 algorithm campaign receipt，旧链只绑定
  `algorithm_search` 与离线 audit；在共享 campaign gate 接线完成前不能用声明 SHA 冒充
  十候选最优性证明。
- GPU 合同代码根的四个漂移小文件已用临时文件、哈希核验、旧版备份和原子替换同步；
  远端 search/contract/prepare/test 哈希分别为 `8ee9f2f0.../0980bde1.../57e15ce2.../376b98ea...`。
  清空 `PYTHONPATH` 后的 GPU dry-run 已生成 10 候选未授权计划，GPU campaign 测试
  `25/25` 通过，正式执行仍保持 0/60。

## 2026-08-14 算法 Campaign 输入恢复与首次正式入口审计

- USTC-TFC2016 的 18 个合同 PCAP 已从固定提交
  `4bc9683b996f582c3843815b68da8e4dce9c7e1e` 恢复到 GPU 合同路径；18/18 目标
  SHA-256 复核通过，符号链接和残留 `.part` 均为 0。来源清单、PCAP 校验表和
  `ALL_DONE` SHA-256 分别为 `c2e0a5ed...`、`3d024b3f...`、`2ab66060...`。
- 使用正式 `freeze_input_manifest.py` 的独立预演重新发现 27 个唯一普通文件：2 个
  manifest、18 个 USTC PCAP、6 个 UNSW PCAP 和 1 个 GT CSV。预演清单不冒充正式
  campaign 清单；runner 仍需在新 run 根内重新冻结。
- 原 CAEOS 主进程当前为 `T(stopped)`，先前 8 个高 CPU worker 已退出，GPU 主机负载约
  `1.5/80 核`；本轮没有恢复、终止或迁移该任务。A09 推理服务继续监听 50051。
- 第一次正式入口 `algorithm_qualification_20260813T194500Z_formal_r1` 在生成 plan 或任何
  候选结果前退出：结果根为 NFS，原锁文件返回 `flock: No locks available`。失败目录只含
  空的 `runs/results/receipts` 和锁文件，0/60，不计为实验 repeat，也不删除。
- runner 已迁移到 GPU 本机 `/tmp` 锁，但其字节变化使旧合同 `0980bde1...` 正确失效；
  同时终审发现 finalizer 的结果目录前缀多一个下划线，以及输入 exact-set、符号链接/
  containment 和稳定读取门仍需修复。因此第二轮正式执行尚未启动，统一审计和 Pareto
  继续 fail-closed。
- 上述门已完成 TDD 修复：本机锁拒绝 NFS/symlink/错误权限并在获得锁后才写 owner；
  finalizer 精确匹配 run ID、重算 27 项输入 exact set，并以单 FD 稳定读取绑定大小、SHA
  与内容。campaign 本地回归 31/31 通过，最终合同 SHA 为 `1d6a48f8...`。共享算法门仍
  固定要求完整 raw replay；在权威 replay API 完成前，即使有摘要 receipt 也不会放行。
- 新 NIC 双后端 stage 已在统一审计代码层接线：R0 identity 可显式绑定 native XDP
  primary 与 DPDK fallback，并分别验证 role/repeat；旧单后端合同继续兼容。相关回归
  28+22+3+12 项通过，当前无新硬件且 trust profile 为 pending，故现场仍保持 false。
