# 自有算法 95%/5% 目标证据

更新时间：2026-07-29

本目录只保存从 GPU 服务器同步的轻量、只读证明材料。本地用于解析、制表和更新文档，不在本地训练、选择阈值或执行正式评估。需要区分“运行位置”和“计算后端”：旧工件虽来自 GPU 服务器，但其训练代码实际使用 CPU，现统一降级为诊断证据。远端工程根目录为：

`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717`

## 证据索引

| 子目录 | 远端结果目录 | 后端/身份 | 主要工件 | canonical SHA |
|---|---|---|---|---|
| `core_v2` | `results/strict_v4_core_warning_confirmation_v2` | CPU后端诊断 | `execution_protocol.json`、`evaluation.json`、`audit.json`、`completion.json`、`failure_analysis.json` | 评估 `698bc422...974f`；审计 `3378deae...f68`；完成 `f66d0a44...7c3c`；失效分析 `9e86c973...05b5` |
| `hybrid_development` | `results/strict_v4_hybrid_self_algorithm_development_v1` | CPU后端开发诊断 | `protocol.json`、`development.json` | 开发选择 `86cea815...e6b4` |
| `hybrid_confirmation` | `results/strict_v4_hybrid_self_algorithm_confirmation_v1` | CPU后端fresh诊断 | `protocol.json`、`confirmation.json` | fresh诊断 `a71c51e5...0b4` |
| `xgboost_development` | `results/strict_v4_xgboost_seed7_development_v1` | CPU后端基线开发诊断 | `protocol.json`、`progress.json`、`summary.json` | 开发汇总 `962f73a7...cce` |
| `xgboost_confirmation` | `results/strict_v4_xgboost_warning_confirmation_v3` | CPU后端基线fresh诊断 | `protocol.json`、`progress.json`、`summary.json` | fresh汇总 `94ece036...948` |
| `gpu_backend_probe` | `results/strict_v4_xgboost_cuda_backend_probe_v1` | CUDA能力探针，非效果结果 | `probe.json` | 探针 `2363745c...4932` |
| `gpu_family_development_v1_failure` | `results/strict_v4_cicids2017_attack_family_gpu_development_v1` | CUDA训练后审计误判的失败批次 | `protocol.json`、`progress.json`、`resource_samples.json` | 协议 `c5e1cdb4...b6682`；`0/7`完成、`7/7`失败 |
| `gpu_cuda_fix_smoke` | `runs/strict_v4_cicids2017_attack_family_gpu_cuda_fix_smoke_v1/botnet_seed17` | 修复后CUDA冒烟，非效果确认 | `gpu_execution.json`、`metrics.json`、`provenance.json` | GPU证据 `5b90666d...7a96` |
| `gpu_family_development_v2` | `results/strict_v4_cicids2017_attack_family_gpu_development_v2` | 正式GPU开发，效果阴性 | `protocol.json`、`completion.json`、`development.json`、`resource_samples.json`、`alert_budget_exploration.json` | 协议 `00136de7...8a77`；完成 `79e027e0...1202`；开发 `d22c7840...7bc3`；阈值扩展 `9a6eeda3...5a4d` |
| `gpu_binary_development` | `results/strict_v4_attack_family_binary_cuda_development_v2` | 双CUDA分类头开发，效果阴性 | `completion.json`、`evaluation.json` | 完成 `cbeb052e...0dd8`；评估 `1f2a3037...4ca9` |
| `gpu_autoencoder_smoke` | `runs/strict_v4_benign_autoencoder_cuda_smoke_v1/botnet_seed17` | 良性自编码器Botnet冒烟，效果阴性 | `metrics.json`、`gpu_execution.json`、`provenance.json` | 指标 `e2cdf2fd...a21d`；GPU证据 `5a368a35...eafd` |
| `gpu_cuda_development_snapshot_20260729` | PCAP来源审计及四个seed29 CUDA开发分支 | 本轮轻量远端快照，不含数据/分数/模型 | 87个JSON、2个协调日志、原始tar归档 | 序列数据 `80be732d...7e02`；PSF评估 `3538d956...c623`；PSF-F评估 `2abc917c...c730`；FSX评估 `ca87f97b...89c5`；FB-FSX评估 `a49d7e50...d252` |
| `gpu_cuda_development_snapshot_20260729/dmc_botnet_development_20260729` | DMC Botnet、统计消融、纯序列修正及PSF-DMC互补性 | A6000 CUDA训练加远端证据复用诊断，均为seed29开发 | 原始归档、完整评估JSON、CUDA证据、分数、代码、预注册及本地汇总 | 归档 `3a9bc5dc...5cba31`；DMC v3 `adc653cd...e26855`；互补性 `073226f5...291b09` |
| `gpu_cuda_development_snapshot_20260729/fhmm_botnet_research_metrics_v2_20260729` | FHMM Botnet seed29/31分层研究指标复算 | 既有A6000任务缓存的后选择只读评价，不训练、不选参 | 两种子完整JSON、指标方向、SHA与本地汇总 | seed29 `485d121f...f28eb`；seed31 `5abc99a2...3c22` |
| `gpu_cuda_development_snapshot_20260729/fhmm_same_split_ensemble_botnet_pilot_v1_20260729` | FHMM 双拆分、每拆分三初始化固定集成 | A6000 CUDA新训练；结果前冻结；未知测试不选权重/阈值 | 协议、6成员训练与GPU证据、2份集成评估、资源审计、completion及本地汇总 | protocol `be557253...024df`；completion `055822d2...d556e`；local summary `f3f8db88...4fbbb` |
| `gpu_cuda_development_snapshot_20260729/fhmm_stable_confirmation_v1_20260729` | FHMM稳定训练、split43/47双新拆分固定候选确认 | A6000 CUDA新训练；训练前冻结；确认期零候选搜索 | protocol、evaluation、completion、6成员metrics/GPU证据与资源审计 | protocol文件 `fdd6a4cd...d086`；evaluation `bd57eedc...64e82`；completion `c7b5fe13...7649` |
| `gpu_cuda_development_snapshot_20260729/fhmm_post_confirmation_development_20260729` | FHMM确认后的攻击路由、联合告警和70/10/20开发 | 前两项复用A6000确认分数只读搜索；70/10/20为6成员A6000 CUDA新训练 | 三组development、70/10/20协议/completion、成员metrics/GPU审计与日志 | 路由 `e5899865...3e95c`；联合告警 `ec7b3d3b...bf22`；70/10/20 development文件 `70e716b0...b69` |
| `rrc_workers4_reschedule` | `results/strict_v4_rrc_csr_confirmation_v1` | RRC canonical边界并发恢复 | `boundary_reschedule_state_seed709.json`、`boundary_rescheduler_launcher_seed709.json` | 状态 `9a348e6e...255ed`；新PID `465776`、workers4 |

`gpu_cuda_development_snapshot_20260729/caeos_strict_v4_lightweight_20260729.tar.gz`在远端与本地独立计算的SHA256均为`2612e0721fb2c001fcd332f6f09e7379d7fb9d9672fdd788b1660d661dc30632`。

## 使用边界

- `Empirical-Tail Hybrid CAEOS` 是当前唯一在 `907/911/919` 三个 fresh 种子的 CPU 后端诊断中全部通过基本预警门的自有算法候选；该结论不得写成 GPU 正式验收。
- 该算法的未知类型召回仍未达到 95%，不能写成完整开放集目标已完成。
- XGBoost 是闭集/预警锚点，不是自有算法，也没有 Unknown 标签头，不能替代自有算法验收。
- `seed7` 结果只用于开发选择；论文确认数字必须来自 fresh 确认文件。
- CUDA 探针证明 XGBoost 2.1.4 可在指定 A6000 上训练，不能证明任何检测效果。
- GPU开发v1 `c5e1cdb4...b6682`因训练后Booster重载审计误判而`7/7`失败；独立修复冒烟已记录`cuda:0`、58%利用率和350 MiB显存且`passes=true`。
- v2正式开发已`7/7`完成并证明真实CUDA执行，但基本门失败；阈值扩展、双CUDA分类头和良性自编码器也均为阴性开发结果。
- CICIDS2017 Afternoon时间戳修正覆盖`800814`条CSV流记录，修正后的包序列数据包含`23127`条流、良性加7个恶意大类；Exploit仅`35`条，相关指标必须保留小样本限制。
- 新增四个seed29 CUDA分支均为开发结果：PSF-CAEOS的Alert Accuracy最高（`93.07%`），FB-FSX的Known type达到`95.83%`，但四个分支均未通过完整95%/5%门。
- FB-FSX按细分类最多5000条保留`49193`条流，7/7任务完成；GPU均值`50.63%`、峰值`99%`。其Unknown alert Recall仅`60.74%`，说明细分类均衡不能替代未知家族表征学习。
- `953/967/971` fresh种子没有读取，确认未启动；失败的development配置不得进入论文确认表。
- DMC v1的Known type虽为`98.77%`，Unknown alert Recall仅`6.59%`；统计dropout 0.5提升至`48.54%`，修正纯序列v3提升至`50.98%`，仍低于PSF的`55.37%`和预注册扩展门槛`60.37%`，故不得扩展为7场景或进入fresh确认。
- PSF-DMC按内容指纹对齐覆盖测试`5612/5615`条流，候选只用验证已知标签选权，最终选回DMC且Unknown alert Recall仍为`50.98%`；简单后融合路线关闭。
- 并行dropout分支整卡GPU均值为`58.51%/61.95%`，达到最低50%负载；DMC单任务均值仅`20.44%/20.91%`，低于资源要求。后续多场景训练必须并行编排并同时报告均值、中位数和高负载占比。
- FHMM研究指标v2两种子均值为Known Macro-F1 `0.912975`、Balanced Accuracy `0.953785`、AUROC-Out `0.909433`、AUPR-Out `0.671632`、`FPR_known@95TPR_unknown=0.255249`、exact OSCR `0.902548`。seed31操作告警更强但开放集排序更差，进一步确认已知识别/告警与未知拒识必须分层报告。
- FHMM同拆分三初始化集成的双拆分均值为Alert Accuracy `0.882573`、Benign FPR `0.054302`、Known type Accuracy `0.948952`、Unknown alert Recall `0.496341`；Unknown AUROC `0.786685`、FPR95-Out `0.456641`、OSCR `0.785504`。六个资源门全过但两拆分效果门均失败，且一个成员在第76–78轮出现NaN，因此不扩展、不采纳简单均值集成。
- FHMM-SR-CAEOS稳定训练的六个完整性/资源门全部通过，GPU均值范围`69.28%–85.91%`；split43完整通过，但split47仅有Alert Accuracy `0.901818`和Unknown alert Recall `0.573984`，故双新拆分确认失败并停止七家族扩展。其split47 Known type `0.950449`、AUROC `0.886194`、OSCR `0.883679`仍达门，说明瓶颈是未知攻击先触发告警的跨拆分稳定性。
- 确认后的攻击路由36组和联合告警27组均为`0`组通过双拆分用户预警门；简单分数路由、maximum/noisy-or融合均停止。70/10/20的六个CUDA资源门虽全过，Alert Accuracy/Unknown alert Recall均值却降至`0.925989/0.685366`，故拒绝扩大已知训练比例这一路线。
- Botnet已经参与开发选择，只能作为开发未知类；任何后续正式确认必须换用与Botnet不相交的未见家族，并在确认前冻结协议。
