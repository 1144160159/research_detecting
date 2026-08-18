# R1--R4 原始回执与逐阶段重算

## 问题

统一发布审计已经把 R1、R2、R3、R4_24h、R4_72h fail-closed，但原有通用回执只有
`candidate_id`、`run_bundle_identity` 和自报 `qualified=true`。这些字段无法证明 10 Mpps、
零丢包、尾延迟、预算、关键流、资源、回退、长稳和质量来自同一正式运行，也不能生成
最终 Pareto 选择器要求的 20 项数值指标。

## 合同与实现

- `configs/production_stage_receipt_contract_v1.json` 冻结五阶段原始 schema、阈值、身份和
  重复规则。回执禁止携带 `qualified`、`metrics` 或
  `derived_production_pareto_metrics`；审计结果只能由重算器产生。
- `hft_mgbs/stage_evidence.py` 提供 `validate_stage_receipt()` 与
  `aggregate_stage_evidence()`，独立于统一审计器，便于后续显式接入且不会形成循环信任。
- 每份回执绑定 run、发生器、硬件、代码、输入、合同、阶段配置、runtime manifest、模型、
  抓包二进制和完整证据清单 SHA-256。代码/输入/硬件/runtime/model/合同跨阶段一致；阶段
  配置在同阶段三重复内一致；run、发生器和证据清单身份逐回执唯一。资源采样和回退注入/
  恢复时间戳还必须处于该回执连续窗口内，A09 原始质量计数必须与同窗 scored unit 守恒。
- R1、R2、R3 各要求三次独立运行和至少 15 个完整秒窗。R4_24h/R4_72h 分别要求连续
  1440/4320 个 60 秒窗，不允许缺窗、时钟跳变或 runtime 身份切换。

## 逐字段硬门

R1 从 offered/received、NIC miss/error、socket drop、序列缺口、parsed/rejected 和分片
packet/byte counters 重算包守恒、零丢包、10 Mpps、解析拒绝率及 kernel-to-shard
P99/P999。延迟使用冻结直方图的保守 nearest-rank 桶上界，overflow 直接失败。

R2 在 R1 计数上增加 base-feature update/reject、预算超限和关键流 total/covered/
budget-skip 的非空分母重算，并分别约束 kernel-to-feature 和 internal-feature P99/P999。

R3 在同窗重算 A09 队列失败、本地 fallback、进程级 CPU/内存、服务归属 GPU/GPU 显存、
故障注入与逐步恢复。质量只接收原始 group/independent confusion、按分数降序桶、冻结
ECE 桶和事件匹配计数；由此重算 7 项质量指标。gain-per-cost 从基线质量及 optional/total
CPU 时间重算，complexity 从 5 个原始结构计数按冻结公式重算。

R4 对每个分钟窗重新应用 10 Mpps、零丢包、P99/P999、预算、关键流和资源门；24h 至少
4 次、72h 至少 12 次故障注入，并要求每次完整恢复。末四分位相对首四分位还约束吞吐
回退、P99 膨胀和内存增长，防止总体平均值掩盖漂移。

## Pareto 聚合接口

只有五阶段、全部重复、身份一致性和独立性都通过时，`aggregate_stage_evidence()` 才返回
非空 `derived_production_pareto_metrics`。字段集合与
`hft_mgbs.production_pareto.METRIC_NAMES` 精确一致：收益/覆盖/吞吐/质量取跨重复最小值，
ECE、丢包、尾延迟、资源、预算、回退和复杂度取最大值。任一错误时该字段强制为 `null`，
不能进入最终 Pareto。

## 测试

```text
python3.9 -m py_compile hft_mgbs/stage_evidence.py tests/test_stage_evidence.py
python3.9 -m unittest tests.test_stage_evidence tests.test_final_pareto_selector -v
Ran 24 tests in 45.016s
OK
```

覆盖：20 项字段精确一致、完整五阶段正例、自报合格拒绝、R1 丢包计数不一致、R2 空关键
流分母、R3 ECE/资源篡改、R4 时间断点/吞吐漂移、重复身份、合同哈希漂移、资源/回退越出
run 时间轴以及跨阶段输入漂移。

## 统一审计接入与当前边界

`audit_unified_release.py` 已显式接入 `aggregate_stage_evidence()`，并由
`release_manifest_v2.json` 绑定阶段合同实际 SHA-256。每份 stage receipt 与完整证据
清单必须同目录、各自由 release manifest 声明并重新哈希；receipt 身份再反向绑定证据
清单 SHA。证据清单必须逐项重哈希 code/input/stage config/runtime/model/capture binary，
不能用任意非空文件冒充。stage 的 backend、hardware identity 还必须等于已通过三次 R0
的冻结身份，runtime manifest 必须等于实时身份核验所用的实际清单哈希。

聚合器输出中的 `packet_drop_count` 与 `budget_overrun_count` 已强制保留整数类型，以匹配
最终 Pareto 选择器的严格 schema；R2 也补齐 internal-feature P999 50 ms 硬门。legacy
resources/key-flow/fallback 摘要不再具有发布权威性，这三项只能由同一原始 stage campaign
的对应阶段派生，避免跨运行拼接。

fallback trial 还要求非空且唯一的 `trial_id`，并要求故障注入时间严格递增；复制同一
trial 不能凑足 R3 的三次或 R4 的 4/12 次故障注入计数。对应负向测试会同时命中
`trial_id` 与时间顺序错误。

当前没有生成新的生产 receipt，`stage_campaign.status=pending`。统一审计实跑返回退出码
2，五个阶段、20 项指标、全流水线和生产发布全部为 false；正式 runner 仍需在物理机/GPU
同窗记录直方图、原始混淆计数、资源采样、故障注入步骤与恢复账本。R0 未通过前不能执行
或宣称 R1--R4 生产达标。
