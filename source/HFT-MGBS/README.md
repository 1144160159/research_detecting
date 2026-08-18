# HFT-MGBS

High-speed Full-Traffic Multi-Granularity feature extraction and adaptive Budget Scheduling。

本地目录是代码唯一编辑源：`F:\泉城实验室\二期\论文\异常检测\source\HFT-MGBS`。
远端部署拆为两个节点：

- 物理数据面 `10.0.5.8:/home/wangwt/phase_2/code/HFT-MGBS` 使用 Rust，负责抓包、解析、流表、多粒度特征、预算调度、PCAP 回放和有界异步推送；
- Python 推理面 `10.0.5.103:/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS` 运行冻结候选 A09；
- 物理机数据先使用 `/home/wangwt/task/datasets`，所有选定回放输入、抓包和回放证据统一放入 `/home/wangwt/task/datasets/replay`；
- GPU 机共享数据集只从 `/opt/data/private/wangwt/ParkAttackKE/datasets` 读取；本地目录仍只保存代码、配置和测试。

Rust 工程通过只读 path dependency 复用
`/home/wangwt/phase_2/code/traffic-analysis-platform/rust/probe-agent/probe-agent` 暴露的
`Capturer`、`PcapReplayer`、`PacketBatch`、`PacketParser` 和流表 API。禁止修改
`traffic-analysis-platform/rust`；所有 HFT 适配代码和构建产物只能写入 HFT-MGBS。
冻结复用基线为平台 HEAD `a6df362989ac3d19d0f55d2520c3e64e8a33d04d`、
Rust tree `e642d4beb27c385ccc4c43f7420cbae1c89def9a`。

## 已落地的最小工程闭环

- `hft_mgbs/features.py`：包/流/时间窗三级流式统计，深层载荷特征按需计算；
- `hft_mgbs/scheduler.py`：按优先级、实测成本 EMA、效用 EMA 和系统压力分配流级/深层预算，配置预算为不可扩张硬上限；
- `hft_mgbs/optimization.py`：先执行丢包/P99/资源/关键流覆盖/回退硬约束，再计算 Pareto 前沿和 Champion；
- `hft_mgbs/pipeline.py`：基础特征全量抽取、昂贵特征渐进升级、执行期实测预算守卫、关键流优先和熔断恢复；
- `rust/hft-capture`：复用平台抓包/解析 API 的物理数据面；逐包热路径不执行同步 GPU RPC；
- `rust/hft-capture/src/xdp_capture.rs` / `rust/hft-capture/ebpf/hft_xdp_redirect.c`：HFT 自有 8 队列 generic XDP 适配、可审计 XDP 入口时间戳和无残留清理；不修改只读上游；
- `hft_mgbs/gpu_service.py`：最多 512 流的有界 A09 Python 推理服务；RC1 使用预热后的 `n_jobs=1`、128 流批次；
- `scripts/export_a09_bundle.py`：按冻结的适配、校准、三种子协议导出 A09 模型包，模型只写 GPU 服务器；
- `scripts/run_physical_replay.sh`：把选定 PCAP 按 SHA-256 固化到物理机 `replay` 后执行回放；
- `scripts/aggregate_replay_metrics.sh`：聚合三次完整回放的最坏值，先判定丢包、P99、覆盖、回退与预算硬门；
- `scripts/select_runtime_candidate.py`：对冻结 A09 的 4 个运行时候选执行跨两轮、每轮三次的稳健审计；任一轮失败即淘汰，跨轮最坏值通过硬门后才进入 Pareto；
- `scripts/sample_inference_node_resources.py` / `scripts/aggregate_inference_node_resources.py`：与完整 PCAP 回放同步采样生产 Python 服务进程树的 CPU、RSS、线程、亲和性和 PID 归因 GPU 上下文，三轮取最坏值；系统 GPU 忙碌度只保留为背景，不能错误归因给 CPU ExtraTrees；
- `scripts/run_virtual_live_diagnostic.sh` / `scripts/validate_virtual_live_diagnostics.py`：在隔离 veth 链路验证最终 Rust 二进制的发包、NIC 可见计数、抓包接收、解析、覆盖、预算与端到端时间戳；证据强制标记为诊断态，不能进入最终物理 NIC Pareto；
- `scripts/run_temporary_shadow_capture.sh` / `scripts/run_temporary_shadow_matrix.sh`：当独立 10GbE 口不可用时，按 `configs/temporary_interface_ens9f0_shadow.json` 在 1GbE 管理口 `ens9f0` 做最长 60 秒的被动影子捕获，并在三个冻结批次候选内做三次重复；必须显式确认管理口风险，禁止回放和发流，结果不得进入最终 Pareto；
- `sync_split_deployment.cmd`：从本地执行的一键代码同步入口，只打包代码、配置、测试和文档；分别部署到物理机与 GPU 机，恢复 `scripts/*.sh` 执行位，并在物理机执行 Python/Rust 回归、在 GPU 机执行 py3.9 回归。它不传输数据集、模型、运行结果或抓包证据；
- `scripts/run_feature_equivalence_probe.sh`：验证优化前后前 34 维基础特征映射，并以两次独立执行验证优化后 38 维特征流的确定性；Rust 对到期/冲刷流键及同优先级流使用稳定排序；
- `scripts/run_inference_resource_confirmation.sh`：对当前推理运行时做三轮 40 秒进程树与 PID 归因 GPU 资源确认；
- `scripts/start_gpu_service.sh` / `check_gpu_service.py`：以 PID、日志和健康请求管理 Python 推理节点；
- `hft_mgbs/experiment.py`：三次重复取保守最差值，并在 Pareto 计算前剔除预算、覆盖、资源和已冻结时延约束的违规候选；
- `scripts/evaluate_grouped_quality.py`：按完整 PCAP 分组的质量探针，禁止同一 capture 跨训练/测试泄漏；
- `scripts/benchmark_fallback_recovery.py`：在同一候选管线中注入 deep 故障、处理真实 PCAP 降级流量并测量探针恢复；
- `scripts/merge_offline_candidate_evidence.py`：合并性能、同域分组质量、独立留出与回退恢复证据，硬门禁后再输出离线 Pareto 前沿；
- `scripts/validate_live_evidence.py`：拒绝缺失物理 NIC 可见性、分层计数对账、目标负载、端到端时延或冻结阈值的线上证据；
- `scripts/run_live_acceptance.sh`：链路恢复且阈值冻结后，使用 HFT 自有 Rust `pcap_injector` 在独立回放口批量发包，并在独立捕获口执行定时 Rust 抓包；所有预检、二进制/输入/阈值哈希、NIC 前后计数器、进程资源和原始指标统一落到 `/home/wangwt/task/datasets/replay`；
- `scripts/run_new_nic_acceptance.sh` / `scripts/preflight_new_nic.py`：新高速 NIC 到货后的
  默认只读验收入口；排除现有 BCM57810/BCM5719，核验 PCIe/NUMA/管理面、native XDP
  forced-zero-copy、DPDK RSS/TSS 与至少 8 队覆盖。危险探针必须同时具备维护授权、变更单、
  外部可信 manifest SHA 和冻结 helper，且任何本地自洽回执都不能直接取得生产资格；
- `scripts/run_physical_link_diagnostic.sh` / `scripts/summarize_xdp_stability.py` / `scripts/summarize_xdp_joint_resources.py`：在 ens8 双口执行隔离诊断，三次取最坏值，并把物理 XDP 运行与 GPU 节点资源按 UTC 时间窗一对一绑定；
- `scripts/run_capture_fallback_diagnostic.sh` / `scripts/aggregate_capture_fallback.py`：向 XDP poll 路径显式注入诊断故障，验证同进程切换到 `af-packet-ts`、真实流量继续处理和接口/XDP/GRO 清理，三次取最坏恢复值；
- `scripts/compose_live_evidence.py`：按冻结的 bnx2x 计数映射对账发包器、回放口、捕获口、ring、parser、HFT 与 sender；缺少内核/硬件时间戳端到端延迟、跨主机资源峰值或真实流量回退证据时强制输出 `incomplete`；
- `scripts/generate_engineering_progress.py`：从受控算法搜索和发布候选配置重建 `docs/ENGINEERING_PROGRESS.md`，每次实验或工程门状态变化后更新结论、硬门数据、证据哈希、阻塞项和下一步；
- `scripts/benchmark_synthetic.py`：无数据落盘的确定性合成吞吐烟测；
- `scripts/check_local_policy.py`：阻止数据、流量、特征、模型参数和运行产物进入本地目录；
- `tests/`：特征正确性、预算上界、压力反馈、管线降级与存储边界测试。

调度器支持关键流最低 tier 预留和 `allow_deep=False` 显式回退；`SchedulePlan` 同时输出估算与实测可选层成本、两类越界次数、按实际执行重算的关键流覆盖和回退状态。计划不超限但实测超限同样是硬失败。

## 本地验证

```powershell
D:\soft\Anaconda3\python.exe scripts\check_local_policy.py
D:\soft\Anaconda3\python.exe -m unittest discover -s tests -v
$env:PYTHONPATH='.'
D:\soft\Anaconda3\python.exe scripts\benchmark_synthetic.py --packets 20000 --flows 1000
D:\soft\Anaconda3\python.exe scripts\benchmark_synthetic.py --packets 20000 --flows 1000 --disable-deep
D:\soft\Anaconda3\python.exe scripts\evaluate_pareto.py --smoke
```

真实 Pareto 评估使用 `evaluate_pareto.py --profile <约束JSON> --candidates <候选指标JSON>`。任何硬约束失败的候选不会进入 Pareto 前沿，即使其准确率更高。

远端只读 PCAP 基准入口为 `scripts/benchmark_pcap.py`；批量矩阵入口为 `scripts/run_remote_pcap_matrix.sh`；分组质量入口为 `scripts/run_remote_grouped_quality.sh`。离线输出会显式标注证据范围，不把应用处理丢弃等价为 NIC 丢包，也不把批次处理 P99 等价为线上端到端 P99。

当前 GPU 离线证据中，`batch=512、budget=5000us、execution safety=0.50` 的 normal/fallback 三次性能重复均满足实测预算超限 0、关键流覆盖 100% 和资源上限。18 个 USTC PCAP 的三次分组质量中 normal 最差 macro-F1 为 0.9567、fallback 为 0.9559；冻结输入哈希的 USTC→UNSW 独立留出中 fallback 最差 macro-F1 为 0.4157、normal 为 0.3265，事件覆盖为 0.6682，说明跨域泛化仍弱。受控 deep 故障、真实 Tinba PCAP 降级和恢复三次均通过，恢复时间最坏约 0.270 秒，且预算超限 0、关键流覆盖 100%。

normal 与 fallback 是同一部署配置的两个运行模式，不是两个可独立发布的 Champion。当前联合前沿仅表示模式间的离线权衡；在目标负载、物理 NIC 丢包、端到端 P99/P999、24/72 小时长稳及业务质量/恢复阈值冻结前，`final_pareto_eligible` 必须保持为 `false`。

分机部署 RC1 当前固定为 `A09 + invariant_no_ports_v1 + ExtraTrees 三种子 + thread_all + n_jobs=1 + batch=128 + feature_flush=1000µs + timeout=150ms`，物理机监听 50052，Python 节点反向连接。运行时搜索受控为 4 个候选、两轮独立实验、每候选共 6 次运行（总计 24 次）；只有 `thread_all` 与 `thread_cpu0_3` 通过全部硬门，两者构成 Pareto 前沿。初选 `thread_cpu0_3`，但 Rust 热路径优化后的完整 PCAP 复核出现 116.643ms 尾延迟，故在不扩展候选集合的前提下激活已通过硬门的 `thread_all`。两个 inline 候选仍因历史轮次越过 100ms 推理或 5ms 内部尾延迟门而淘汰。

最终捕获二进制 SHA-256 为 `20ec4f477e1580ef53be8237972b75293cbc8cf8e796893189bc309c52e5686a`。三次完整 FTP-EXP1 PCAP 每轮 78,786 包、4,939 流，最坏 GPU 批次 P99 为 70.283ms，最坏流物化至特征入队 P99 为 3.982ms，最坏包处理 P99 为 3.678µs，关键流覆盖与评分完整率均为 100%，丢包、队列满、批次失败、回退和预算超限均为 0。`ens9f0` 最新三轮 60 秒被动确认每轮至少接收 727,727 包，捕获丢包为 0、关键流覆盖为 100%，GPU/内部 P99 最坏为 87.177/2.866ms；该 1GbE 管理口结果仅用于诊断，不能替代物理双口目标负载验收。当前其余非 `ens8` 物理口 `ens9f1/ens9f2/ens9f3` 均无载波。

`thread_all` 三轮推理节点资源证据各覆盖 40 秒，进程样本每轮至少 314 个、GPU 样本每轮至少 71 个。生产服务进程树最坏使用 1.101 核，占 80 核主机 1.3759%，RSS 228,446,208 字节、内存占比 0.04225%、线程 4；A09 服务没有 GPU 计算上下文，归因 GPU 和显存占用均为 0。审计继续区分“服务 PID 归因资源”和“系统背景干扰”，不会把其他任务的 GPU 负载算到本方法。

分机恢复通过备用 50053/50054 探针完成三次真实断链—重连—再推理验证，最坏反向重连 2.224ms，最坏恢复到再次成功预测 45.910ms，满足 300ms 回退恢复门。远端发布审计核验 10 个算法候选、4 个运行时候选、跨轮证据、最终二进制、正常路径三轮、推理节点资源三轮、虚拟链路三轮、恢复三轮及其 SHA-256；因生产目标负载/SLA、抓包驱动运行时回退和 24/72 小时长稳仍缺失，保持 `final_pareto_eligible=false`。

最终在线预检要求两个不同物理接口均达到至少 10GbE，且不得挂接管理桥、配置 IP 或承载默认路由。当前 `ens8f0/ens8f1` 均为 10,000Mb/s、UP/LOWER_UP、无 IP/管理桥/默认路由，形成 1 对硬件合格接口；完整生产预检仍被未冻结的目标负载、解析拒绝率、P99/P999 与最小时长阻断。

`ens8f0/ens8f1` 是同一 `bnx2x` 适配器的两个 PCI 功能。严格 native XDP 探测返回 EOPNOTSUPP，因此不声称原生/硬件 XDP 或 AF_XDP 零拷贝；HFT 自有 8 队列 `xdp-skb` 三次诊断均发送/接收 151,563 包、抓包丢包 0、关键流覆盖 1.0，最坏 XDP 入口至特征 P99/P999 为 4.533/9.216ms。当前顺序是 `xdp-skb` 优先、`af-packet-ts` 安全回退。三次注入式运行中回退最坏 118.946ms，回退后至少继续处理 100,249 包，清理状态全部正常；切换窗口最多少收 1,307 包，所以该回退证据不复用正常路径零丢包结论。以上仍是 0.01 Mpps、15 秒诊断证据，不代表生产线速资格。

在线验收命令的输入顺序固定为：

```bash
/home/wangwt/phase_2/code/HFT-MGBS/scripts/run_live_acceptance.sh \
  <capture-interface> <replay-interface> <source-pcap> \
  <frozen-thresholds.json> [duration-s] [af-packet-ts|af-packet|xdp|xdp-skb]
```

捕获口与回放口必须是两个不同的物理接口。脚本会先对两个接口执行 fail-closed 预检；载波、速率、驱动、权限或冻结阈值任一缺失即退出，不启动抓包或发包。其输出是待组合的原始在线证据，不会自动冒充最终 Pareto 证据；仍需三次重复、分层计数对账、真实端到端 P99/P999 和 `validate_live_evidence.py` 全部通过。

## 同步到 GPU

运行 `sync_to_gpu.cmd`。同步只包含代码、配置、测试和文档；远端随后在 Conda `py3.9` 中完成策略检查、编译、单测与合成烟测。数据/模型/特征缓存/性能剖析/运行结果不会回传本地。

当前版本是可执行的工程基线，不代表最终性能最优。后续优化必须以真实流量回放下的吞吐、P99 延迟、丢包率、特征收益和资源占用联合验收。

## 生产联合 Pareto 门

`scripts/select_production_pareto.py` 使用
`configs/final_pareto_policy_v1.json` 对算法质量、数据面、资源、关键流、fallback、
主机恢复和统一发布审计组成的联合候选执行最终选择。至少需要 2 个、最多 10 个
联合候选；单候选、单指标最优、capture-only、generic/SKB XDP、缺少实际 receipt
或统一审计的候选均不能产生 Champion。当前环境清单及 fail-closed 审计分别为
`configs/current_environment_joint_candidates_v1.json` 和
`docs/experiments/current_environment_production_pareto_audit_v1.json`。
