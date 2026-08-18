# 2026-08-12 生产联合 Pareto 选择闭环

## 修复目标

原有 `optimization.py` 适合单层候选的工程探索，但最终发布还缺少一个独立、
可密封的联合选择层。新的 `production_pareto.py` 不修改算法搜索和运行时搜索，
只接收“算法质量 + 数据面 + 运行时 + 回退/恢复 + 证据身份”已经合并的部署封装。
因此，最高吞吐或最高准确率都不能绕过其余硬门成为最终结果。

## 冻结候选数量

- 一个联合候选代表一个可直接发布的算法与运行时数据面封装；
- 至少需要 2 个联合候选，单候选不能声称比较意义上的 Pareto 最优；
- 最多接收 10 个联合候选和 10 个不同算法，超限时整个选择无效；
- selector 会实际重算 `configs/algorithm_search_rc1.json` 的 SHA-256，并核对
  其中 `actual_candidates=10`。原探索配置允许最多 12 个，但生产准入上限单独
  冻结为 10，不能据此扩展最终候选集合。

## 硬门与多目标

先执行以下硬门，全部通过后才计算非支配集：

- 10 Mpps、丢包数 0、P99 不超过 10 ms、P99.9 不超过 50 ms；
- CPU、GPU、主存、显存利用率均不超过 0.85，预算超限数为 0；
- 关键流覆盖率不低于 0.99，fallback 恢复不超过 0.30 s；
- grouped Macro-F1 不低于 0.90；
- 独立留出 Macro-F1、攻击召回、良性召回、AUPRC 分别不低于
  0.70、0.72、0.93、0.45，ECE 不高于 0.05；
- ground-truth 事件召回不低于 0.70。

质量不会压缩为一个自报 `quality`。Pareto 目标保留上述七个质量维度，并联合
吞吐、关键流覆盖、收益/成本、P99、P99.9、资源压力、恢复时间和复杂度。
Champion 只在非支配集中使用冻结权重的归一化多目标效用产生；每个被淘汰项
输出失败阶段、约束实际值/阈值，或明确列出支配它的候选。

## 证据密封

64 位十六进制字符串本身不构成证据。每个可入选候选必须引用一个实际存在的
`sealed_unified_production_release_receipt`：

- selector 重新读取文件并计算 SHA-256；
- receipt 还必须绑定一个实际存在并重新验哈希的
  `hft_mgbs_unified_release_audit`；该统一审计需同时满足 accepted、production
  release、full pipeline、最终准入为真且 `errors=[]`；
- 联合指标只能来自统一审计中的 `derived_production_pareto_metrics`，并与候选和
  receipt 完整深度一致，不能在复用 receipt 后单独改吞吐、质量或资源指标；
- receipt 必须绑定 candidate、algorithm、backend、代码/输入/证据清单哈希；
- `production_release_accepted`、fallback、主机恢复和最终准入必须全部为真；
- 至少三次 run ID 必须非空且互异，并与候选的重复次数一致；
- receipt 中的证据标志必须与联合候选逐项一致。

CLI 同时重算 policy 与 candidates 文件哈希并写入审计输出。这样
`final_pareto_ingestion_allowed=true` 的候选自报不能单独取得准入资格。

## Backend 边界

当前 bnx2x 环境只验证了 generic/SKB XDP，因此 `xdp-generic` 和 `xdp-skb`
在生产 Pareto 中直接淘汰。XDP 优先级只在两个候选目标值和效用完全相同时作为
确定性 tie-break；它不能覆盖吞吐、丢包、时延、资源、质量或恢复差异，也不是
性能捷径。

## 当前环境执行结果

执行：

```text
PYTHONPATH=. python scripts/select_production_pareto.py \
  --policy configs/final_pareto_policy_v1.json \
  --candidates configs/current_environment_joint_candidates_v1.json \
  --output docs/experiments/current_environment_production_pareto_audit_v1.json
```

预期退出码为 10（无合格 Champion）。实际审计输出：

- `candidate_count=2`，`algorithm_candidate_count=1`；
- `pareto_front_ids=[]`，`champion_id=null`，`selection_qualified=false`；
- DPDK 封装因缺少同窗全链路指标、实际 receipt、fallback/恢复和证据哈希被拒；
- xdp-skb 另有 `backend.production_capability` 明确淘汰原因；
- 审计 JSON SHA-256：
  `33c2e1d718c822eb9192b6f549453cd47b6e4416778b7c94320b1f7bf1457030`。

## 回归验证

`tests/test_final_pareto_selector.py` 的 13 项测试覆盖：单指标不可直通、全部数据面
硬门、实际 receipt 重哈希、独立 run ID、fallback/恢复、候选数量上限、
统一发布审计门、指标篡改、未知算法淘汰、generic XDP 淘汰、严格非支配解释及
仅限完全平局的 XDP 优先，以及不设置 `PYTHONPATH` 时从项目根目录直接执行 CLI。
测试先在模块缺失时得到预期红灯，完成实现后 13/13 通过。
