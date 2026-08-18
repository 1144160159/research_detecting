# CAEOS-EMTD 项目现状梳理报告

> 生成方式：本机 AI 会话对 `方向分析\多模态开放集加密恶意流量检测` 与 `source\CAEOS-EMTD` 的全量只读梳理 + 远端本地镜像核对（截至本地最新镜像 2026-08-15）。
> 本文件是辅助汇总，权威状态始终以方法论 README（2026-08-06 更新）与 `论文实验执行状态_2026-08-12.md` 为准。

## 1. 项目一句话

Evidence-OpenEMTD：证据冲突感知的可信开放集加密恶意流量检测（CAEOS-EMTD = Conflict-Aware Evidential Open-Set Encrypted Malicious Traffic Detection）。不解密载荷，多模态侧信道证据 + Dirichlet 意见 + 冲突折扣融合 + known-only 阈值 + 可审计证据包，目标期刊 IEEE TIFS。

## 2. 两条交付线与验收

| 交付线 | 表示 | 验收 |
|---|---|---|
| 工程线 | 流统计 / 包长序列 / IAT 序列 | 工程 95%/5% 六项门 |
| 论文线 | 统计/时序主干 + payload 语义或通信图等异构信息 | 六项门 + Unknown label Recall≥95% + 三层指标 + 消融 |

三层指标：①已知类（Known Macro-F1、Balanced Acc、逐类 Recall、Benign FPR）；②未知检测（AUROC-Out、AUPR-Out、FPR_known@95TPR、Unknown-F1@冻结阈值）；③联合开放集（exact OSCR、Known Acceptance、Unknown Rejection）。

## 3. 权威当前判定（2026-08-06 README）

| 目标 | 状态 | 关键数字 |
|---|---|---|
| 工程自有算法 95%/5% | **未通过** | PCAP 三模态 v38 seed307：Alert Acc 60.17%、Attack Recall 58.86%、Unknown alert Recall 50.72%；仅 Precision 99.96%、Benign FPR 0.65% 过门 |
| 论文多模态 95%/5% | **未完成** | Known Macro-F1 91.83%、Unknown AUROC 48.75%、FPR95 92.00%、OSCR 45.31% |
| 选择性 SOTA | 未授权 | 先过绝对安全门，再做预注册相对比较 |
| 全面 SOTA | 不作为可交付结论 | strict-v4 机器总账 `goal_achieved=false`，8–9 项阻断 |

## 4. 关键根因（审计基准 2026-08-01 §11）

1. 目标与实验对象长期漂移（表格 strict-v4 / PCAP 三模态 / 双告警 / SOTA 并存）；
2. DDoS/DoS/Mirai 被 v1–v38 反复揭盲 → 全部降级 development unknown，最终需外部未见家族；
3. 三模态同源重叠（序列与图共用长度/IAT/方向）→ v38 AUROC≈0.49，风险排序近随机；
4. 过度保守告警边界（Precision 99.96% 但召回不足）；
5. 基线补在复杂模型之后，收益来源无法定位；
6. 工程完整性（protocol/watcher/audit/测试）长期领先科学效果；
7. 缺最终外部确认与部署回流。

## 5. 整改后门禁体系（2026-08-12 冻结）

`contracts/caeos_paper_closure_contract_v1.json`：D0（数据身份/分组 split）→ P0（预处理冻结+train-deploy 等价）→ F0（七组多模态消融）→ B0（同拆分基线资格）→ M0（自有方法单变量冻结，`caeos_conflict_support_pairwise`）→ C0（五种子外部确认）。
开发种子 81001/81007/81011；确认种子 81013/81017/81019/81023/81031（M0 前封存）。

## 6. 数据状态

- 标签（2026-08-06 完成）：8 套恶意数据集（5 严格流级 + 2 捕获/成员级 + DoHBrw2020 源质量例外），SQLite 共 177,729,893 条。删除比例需披露：CICDDoS2019 68.73%、ToN-IoT 43.58%、CICIDS2017 23.65%。
- 特征（v5 / 143 列 schema v4，契约 2026-08-15 冻结归档）：行单位=双向流段（30s/64 包）；三模态=payload（4096B 前缀，默认 512）、包行为（85 标量+17 序列+8 TLS/QUIC）、包交互图（实验层由序列构建）；19 列禁入模（端点/端口/时间/来源/应用提示）。
- manifest（2026-08-12 快照）：11 个合同中 10 个 complete（CICIoT2022 6.61M、Edge 7.60M、BoT 372M、ToN 14.67M、CICIDS2017 2.16M、CICIDS2018 84.98M、CICDDoS2019 18.98M、DoHBrw2020 4.58M、UNSW 6.31M、5GAD 369K）；**CICIoT2023 主开发集最终化中**（309/309 捕获完成，约 1.4 TB 大类 CSV，PID 1366369）。

## 7. 代码库（source/CAEOS-EMTD，唯一可编辑源）

- 顶层 888 文件：create_ 182 / summarize_ 109 / audit_ 102 / run_ 95+25sh / evaluate_ 84 / analyze_ 38 / train_ 31 / confirm_ 22 / prepare_ 21 / select_ 11 / screen_ 6 / materialize_ 4 / freeze_ 1；
- caeos 包 88 模块；tests/ 551；configs/ 29；contracts/ 2；protocols/ 1；scripts/ 227 sh；
- 权威入口（CODE_LAYOUT.md）：audit_project_contract.py、train_strict_v4_fhmm_stable_task_cuda.py（工程）、train_neural_open_set.py（论文骨干）、prepare_*_strict.py（数据）；
- 发布：sync_to_gpu.cmd → 远端 compileall + 定向 pytest → SOURCE_MANIFEST.sha256 → 原子推进 `CAEOS-EMTD/current`。

## 8. 远端 GPU 服务器（root@10.0.5.103:25696，parkattack32）

- RTX A6000（49,140 MiB）；配额 32 核 / 200 GiB / 48 GiB 显存；K8s Burstable Pod；
- 代码根 `/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD`（releases/current/active/legacy；current release `20260729T092408Z-...`；`paper_protocols/caeos_paper_closure_v1→v3`）；python 为 `.../anaconda3/envs/py3.9`；
- 数据根 `datasets/caeos_unified_multimodal_v5`；就绪 watcher（每 300s 刷新 readiness.json，fail-closed）；
- NFSv3 soft 挂载（10.32.0.10）曾致 30 GB 写入 EIO → 512 MiB 分块校验修复；改 hard/NFSv4 待平台；
- 注意：历史"GPU 正式确认"已撤回（旧 XGBoost/Pairwise/RRC 实为 CPU 后端），正式训练必须在 CUDA 且采样均值≥50%。

## 9. 论文写作状态

写作准备区（正文未启动）：5 启动门（引用/协议/数据/结果/声称）中引用门 G10=0/50、结果门 95%/5% 未过；主张矩阵 C4/C5 未证实/未通过；结构=引言/相关工作/问题定义/方法/实验/讨论，3 条可检验拟贡献。

## 10. 当前正在执行的下一步（按门禁）

1. CICIoT2023 大类 CSV 最终化 + dataset.manifest 生成；
2. 构建 D0（数据卡/重复指纹审计/capture-time-device grouped split）与 P0（preprocess_v1 + train-deploy 等价）；
3. D0/P0 通过后启动 F0 七组消融（payload-only / sequence-only / graph-only / 两两 / 三模态），主端点 exact OSCR；
4. F0/B0 通过后才做 CAEOS 单变量组件选择（M0）与五种子外部确认（C0）。

## 11. 远端实时核验（2026-08-17 09:03 UTC，SSH 免密直连）

### 11.1 主机与资源
- hostname parkattack32，运行 381 天，load 1.46/3.75/2.78；RTX A6000（550.127.05）**1 MiB 显存占用、0% 利用率**——无训练任务；
- 内存 503 GB（可用 488 GB）；NFS 6.8T→**5.7T/11T（57%）**（08-15 空间清理后）；挂载**仍为 NFSv3 soft**（P0 整改未落地），dmesg 最近一次 NFS 超时为 08-06；
- 唯一活跃进程是别的项目（HFT-MGBS gpu_service，08-13 起），**CAEOS-EMTD 无任何运行中进程**。

### 11.2 数据：11/11 数据集全部完成
- **CICIoT2023 主开发集于 08-14 完成**：309 捕获、8 类 CSV 约 3 TB、总行数 **1,558,865,789**（Benign 55.6 万；Botnet_Malware 467 万；Brute_Force 9,840；DDoS 15.2 亿且 payload 率仅 1.68%；DoS 2,926 万；Recon 130 万；Spoofing 25.3 万；Web 2.5 万）；冲突 0、排除 0；2 条重复 sample_id 已按 `sample_id_v2_20260814T104500Z` 修复重键；TShark 3.6.2 + splitpcap fca18e270fe4；
- CICIDS2018 与 CIC-BoT-IoT 于 **08-15~16 完成"split_every_pcap_min12"重建**（completion 分别 08-16 18:43 与 15:20），其余数据集 manifest 均为 08-07~14 生成。

### 11.3 D0/P0 流水线：自动启动、部分通过、卡在两处失败
- readiness watcher 在 08-13T12:24（第 11 个 manifest 出现时）自动触发 `D0_P0_pipeline_started`，08-13T19:07 最后一次快照后终止（launcher.log=Terminated）；
- 已完成并通过：内容冲突策略 **9/9 数据集 SUCCESS**（08-14 14:26 全部完成）；**train/deploy 视图等价门 `gate_pass=true`**（CICIoT2023，64 样本×8 类，16 包/512 payload 字节精确序列化一致）；duplicate audits v2（ciciot2023.v2 / cic_ton_iot.v2 / unsw_nb15.v2，08-13~14）与 content_contract_v2 审计（9 套）；
- **两处失败阻塞**：① `build_caeos_paper_d0_p0_artifacts.py` 报 `ValueError: duplicate audit did not pass`（D0 构建中止）；② `run_caeos_content_conflict_remediation.py` 中 `rebuild_caeos_dataset_completion.py` 退出码 1（修复重建失败）；
- **失败①根因（08-17 远程取证）**：CICIoT2023 原始数据存在大规模跨 capture 内容重复——v2 审计 `content.capture_equivalence_edges` 含数千条等价边（同一模型可见字节在几十个 capture 间重复出现），因此 v1（`ciciot2023.json`，gate_pass=false）与 v2（`ciciot2023.v2.json`，gate_pass=false）两次朴素重复审计都不过门。设计的补救路径"内容冲突策略"其实已完成：9/9 数据集策略 `gate_pass=true`（ciciot2023：4,683 个歧义内容键 / 62,547 行歧义，占 15.6 亿模型可用行的 0.004%）。但 D0 构建器仍读取旧审计文件 `duplicate_audits/ciciot2023.json` 做朴素 gate 判定，且 08-13 后未重跑；此外两次审计绑定的 `dataset_manifest_sha256`（a186f923…）与 08-14 最终 manifest 的 `manifest_sha256`（de350a67…）已不一致，即使重跑也会先撞"审计未绑定当前 manifest"。**状态：未解决**（需用 v2 审计+冲突策略重绑当前 manifest 后更新构建器并重跑）。
- **失败②根因（08-17 远程取证）**：edge_iiotset 的 completion 重建首次运行时，模板 `completion.lane3.ciciot2022.json` 缺少 `pcap_repair_manifest_sha256_at_start` 字段，`rebuild_caeos_dataset_completion.py` 在 line 129 抛 `KeyError` 退出码 1；同命令第二次执行（resume 重跑）成功：`{"all_complete": true, "completion_sha256": "90c8c01e…", "dataset_id": "edge_iiotset"}`，`completion.lane2.edge_iiotset.json` 已生成；queue.status.json `all_complete: true`，9/9 数据集 SUCCESS，ciciot2023 策略 SUCCESS.json `gate_pass=true`，`completion.lane1.ciciot2023.json` 已于 08-14 14:19 生成（queue.log 尾部残留的是首次崩溃的 traceback 记录）。**状态：已解决**。
- 门禁快照（最后更新 08-13T19:07，之后 watcher 已停）：`complete_manifest_count=11/11`、`development_manifest_ready=true`、`paper_inventory_manifest_ready=true`，但 **`D0_pass=false`、`P0_pass=false`、`F0_authorized=false`**；`data_cards/`、`splits/` 尚未生成，`preprocess_v1.manifest.json` 尚未生成；`paper_protocols/` 与 `paper_protocol_v1/` 自 08-16 后无任何文件变更——**D0/P0 构建器 08-13 失败后从未成功重跑**。

### 11.4 结论
远端目前处于 **"数据全部就绪、D0/P0 构建流水线中途失败停机"** 的状态：11 套数据全部完成且身份/等价门部分通过，但重复审计门未通过 + 内容冲突修复重建失败，导致 D0/P0 工件（数据卡、分组 split、preprocess_v1）尚未产出，F0 七组消融按门禁正确保持未启动。下一步需要修复 duplicate audit 判定与 content conflict 重建链后重跑 D0/P0 构建。

### 11.5 方案 A 修复完成（2026-08-18 执行，已生效）

按"重绑审计 → 换策略门 → 重跑构建"三步执行完毕：

1. **重绑审计**：`duplicate_audits/ciciot2023.json` 由失败 v1 审计替换为 `remediated_duplicate_audit.json`（补救后审计：gate_pass=true、绑定当前 manifest de350a67、链式锚定源 v2 审计 d7045180）；旧 v1 备份为 `.pre-remediation-20260817`；
2. **补丁构建器**（`build_caeos_paper_d0_p0_artifacts.py`，本地+远端同步，旧版备份 `.pre-d0fix-20260817`）：
   - 要求 canonical 审计必须是补救审计，并校验其与 v2 源审计的 SHA 绑定；
   - split 分组改用 **同标签** 捕获等价边（3,656 条原始边中丢弃 2,084 条跨标签边；跨标签重复行已按冲突策略排除出模型视图，故其边不再承担防泄漏职责），分组语义升级为 `capture_with_same_label_cross_capture_content_duplicate_union`，丢弃数写入 split manifest；
   - 数据卡新增 duplicate_remediation 披露（排除 4,683 键 / 62,547 行）与 8 个未切分小捕获、1 个零时间戳捕获的显式记录；
   - 兼容无 splitpcap 指纹的小捕获（时间戳取空并在数据卡披露）；
3. **重跑**：train/deploy 等价证明重跑（重绑 de350a67、64/64 通过）→ 构建器产出 3 个工件（gate_pass=true）→ 就绪审计 16/16 回归通过。

**最终门禁（2026-08-18T01:55:21Z readiness.json）：`D0_pass=true`、`P0_pass=true`、`F0_authorized=true`** —— 七组多模态消融实验已解锁，可随时按冻结协议启动。

⚠️ 遗留观察（未改动，属冻结协议行为）：按"组哈希 70/15/15"分配后 split 行数极不均衡——train 35,807,870（2.3%）、validation 1,522,797,219（97.7%）、test 260,700（0.02%），原因是同标签合并后的 13 个组中，巨型 DDoS 组（15.2 亿行）落入了 validation。启动 F0 前建议评估该不平衡对训练/验证的影响（是否调整组粒度或做组内限额采样，需预注册协议变更）。
