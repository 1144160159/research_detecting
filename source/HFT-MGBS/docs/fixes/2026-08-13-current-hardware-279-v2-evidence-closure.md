# 当前硬件 2.79 Mpps v2 独立证据闭环

## 问题

v1 候选审计接收已经人工整理成 `raw_run_v1` 的窗口对象，无法从 runner 原始证据重新验证文件身份、窗口连续性、发生器/NIC/socket/解析/特征/GPU/关键流守恒，也无法阻止低流数运行用汇总分位数或重复值伪装足量逐窗样本。runner 自报的 `qualified` 同样不能成为独立结论。

## 修复边界

本次只新增/修改：

- `configs/current_hardware_2_79_release_profile_v2.json`
- `hft_mgbs/current_hardware_279.py`
- `scripts/compose_current_hardware_279.py`
- `tests/test_current_hardware_279_v2.py`
- 本修复文档

未修改 runner、Rust、unified/Pareto 或旧 10M 证据链。v1 CLI 仍保持默认兼容。

## v2 证据契约

`raw-run-v2` 输入只允许提供证据根、运行身份和带 SHA-256 的路径引用。composer 独立执行：

1. 重哈希 runner、配置、capture binary、模型、runtime manifest、GPU 服务源码、精确推理引擎源码、服务 launcher、`pipeline_raw.json`、runner receipt、ready receipt、事件、身份、窗口、两节点资源和 NIC 统计。
2. 解析并逐项重哈希 runner `evidence.sha256`；关键文件既要匹配外部引用，也必须出现在 manifest 中。
3. 用 runtime manifest 反向绑定模型、服务源码、推理引擎和 launcher；不接受 manifest 中的自报结论。
4. 从严格 1 秒累积计数快照重算最长连续窗口，要求至少连续 15 窗；每窗 offered、NIC `rx_ucast`、socket receive 都必须达到 2.79 Mpps 且守恒，NIC discard/socket drop/sequence gap 必须为零。
5. 重算解析、特征、GPU、关键流 admission/inference/fallback/outstanding 守恒；不以 coverage 浮点自报值代替计数。
6. 分层样本门为 packet/flow/kernel-feature/E2E 每窗各至少 1000 个唯一 `sample_id` 与唯一 `source_event_id`；GPU batch 每窗至少 100 个且 `max <= 50 ms`。重复填充直接按 schema 失败，不扩权。
7. 物理节点与服务节点每窗各至少一个资源样本，并绑定同一 `run_id`。
8. 质量只从相互独立的 official/manual label artifact 与 prediction artifact 重算；预测必须绑定 label/model/runtime manifest 哈希，synthetic 或非 independent holdout 一律拒绝。
9. fallback 必须提供绑定同一 `run_id` 的原始有序事件，不能用布尔完成标记替代。

`candidate-v2` 仅在 normal 3 次、fallback 3 次全部为独立 sealed run，run/generator 身份无重复、代码/模型/运行构件无漂移、三个 fallback trial 唯一且不重叠时，才可得到 `candidate_evidence_qualified=true` 和当前硬件范围内的 `full_pipeline_qualified=true`。无论结果如何，`production_release_accepted` 和 `final_pareto_ingestion_allowed` 永远为 `false`。

## 当前 8-flow 证据判定

现有首轮原始证据只有约 71 个 flow、37 个 GPU batch，且只有 10 个完整窗口。即使 10 个完整窗口的最小速率达到 2.790404 Mpps，它仍同时违反：连续 15 窗、flow/kernel-feature/E2E 每窗 1000 个真实样本、GPU batch 每窗 100 个真实样本、关键流完成守恒、独立质量 artifact 等门槛。v2 设计和负测明确使该类证据 fail closed；不会将 capture-only 或低流量 synthetic loopback 提升为完整闭环。

## 验证

本地使用 `D:\soft\Anaconda3\python.exe` 通过 9/9 个 v2 单元测试。负测覆盖：缺窗、非连续窗、重复 run identity、哈希漂移、NIC discard、重复样本伪扩、flow 样本不足、关键流守恒、fallback 伪完成、资源缺失、质量缺失、现有 8-flow 形状 fail closed，以及 CLI 独立启动。
