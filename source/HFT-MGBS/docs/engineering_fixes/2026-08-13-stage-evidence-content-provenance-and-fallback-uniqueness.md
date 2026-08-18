# R1--R4 内容级身份溯源与回退试验唯一性加固

## 问题与风险

R1--R4 的统一审计已经能够重算吞吐、丢包、尾延迟、资源、关键流、回退和质量指标，
也会校验 `code_manifest.json`、`input_manifest.json`、`stage_config.json`、
`runtime_manifest.json`、`model_manifest.json` 与捕获二进制的外层 SHA-256。但是此前原始
stage validator 只接收这些哈希，没有检查 manifest 内容；攻击者可以生成
`{"code":"frozen"}` 之类的一键 JSON，令 receipt、文件和 evidence manifest 的哈希彼此
自洽，却不提供任何可定位的代码、输入、模型或运行 provenance。

回退验证此前已有唯一 `trial_id` 和故障注入时间严格递增检查，但最小次数由原始列表长度
预判，完成时间没有独立唯一性约束。复制时间轴、只改变 `trial_id`，或者构造彼此重叠的故障
区间，不应被算作独立 fault trial。

## 修复范围

本次仅修改原始证据层：

- `hft_mgbs/stage_evidence.py`
- `configs/production_stage_receipt_contract_v1.json`
- `tests/test_stage_evidence.py`
- `tests/test_unified_release_audit.py` 中对应的密封 stage fixture

未修改统一审计器、Pareto 选择器或算法搜索。当前没有实机 stage receipt，发布状态继续
fail-closed。

## 内容级身份合同

receipt 新增 `identity_manifests`，包含 code、input、model、runtime 和 stage_config 五份完整
JSON 文档。每份文档按 UTF-8、键排序、紧凑分隔符、禁止 NaN、末尾单 LF 的冻结规则规范化，
重算 SHA-256，并与 receipt `identity` 和外层 evidence manifest 已验证的对应文件闭环。

内容硬门包括：

- code：排序且路径唯一的文件清单；每项绑定相对路径、文件 SHA、字节数、语言和职责；至少
  同时包含 Rust/capture 与 Python/inference，清单本身再生成 `source_tree_sha256`。
- input：排序且来源唯一的数据清单；每项绑定 source ID、用途、内容 SHA、字节数、记录数和
  provenance URI；冻结 dataset、split、feature schema 与整个 source set。
- model：至少一个排序且路径唯一的模型产物，绑定 SHA 和字节数；必须反向绑定训练输入
  manifest 与相同 feature schema。
- runtime：至少包含 capture 和 inference 两个具名版本组件；捕获组件二进制必须等于 receipt
  的 `capture_binary_sha256`；绑定后端、硬件、代码、模型、捕获二进制以及不同的物理/GPU
  主机角色。
- stage config：绑定 stage、后端、合同、硬件、code/input/runtime/model/capture 全部身份；
  非空参数表也单独规范化哈希。

只重新计算 dummy JSON 自身哈希不能通过上述字段集合、内容集合和 provenance 边校验。

## 回退试验计数

每个 fault trial 现在必须同时满足：

1. `trial_id` 非空且全局唯一；
2. 注入时间全局唯一并严格递增；
3. 恢复完成时间全局唯一并严格递增；
4. 下一次注入必须晚于上一次恢复，试验区间不能重叠；
5. `recovery_ns` 等于两时间戳之差，时间位于同一运行窗口；
6. 无过渡包缺口、无捕获丢包、有切换后流量，且完整执行所有恢复步骤。

只有同时满足全部条件的 distinct valid trial 才计入 R3 的 3 次、R4_24h 的 4 次和 R4_72h
的 12 次下限。原始列表够长但有效独立试验不足时，返回
`fallback_trials.distinct_valid_count` 并拒绝该 receipt。

## 验证证据

窄回归覆盖完整五阶段正例、哈希自洽 dummy code、dummy input source、空模型产物、模型到输入
provenance 漂移、runtime 捕获组件漂移、stage config runtime 漂移、重复 ID/时间、恢复时间重复、
重叠区间以及有效次数不足。密封 stage campaign 正例还会把嵌入文档按规范化字节写入实际
evidence 文件，再由统一审计已有的外层清单校验路径验证。

最终命令、测试数量和新合同 SHA-256 在本轮验证完成后记录到交接结果；
`release_manifest_v2.json` 的旧合同哈希不在本修复范围内，由合并者刷新后再跑完整统一审计。

## 性能影响与回退

内容验证仅在发布审计阶段执行，不进入捕获、特征抽取或推理热路径，数据面性能影响为零。
正式 receipt 会增加几份小型 manifest 的序列化和哈希开销。若必须回退，应同时回退代码、
合同和 fixture；不能只删除 receipt 内嵌文档而保留“已验证 provenance”的发布声明。

## 遗留边界

本修复证明 manifest 结构、内容摘要和文档间 provenance 自洽；外层统一审计负责证明对应
manifest 文件和捕获二进制确实位于密封证据目录并匹配哈希。正式 runner 仍需进一步把清单中
每个代码、数据和模型产物的实际文件纳入完整 evidence manifest；没有物理/GPU 同窗运行的
真实 receipt 时，R1--R4 和最终 Pareto 仍不得宣称通过。
