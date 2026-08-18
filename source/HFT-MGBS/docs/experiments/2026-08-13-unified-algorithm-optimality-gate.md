# Unified release 的算法最优性门修复（2026-08-13）

## 问题

统一发布审计此前只校验 `algorithm_search_rc1.json` 的声明字段与文件
SHA，并继续采用旧的 offline release 审计结果。这不足以证明 10 个受控候选中
的全局/实用最优算法，伪造的 `accepted=true` 也没有独立重算门阻止其进入发布
判断。

## 修复

- 增加冻结产物 `configs/current_algorithm_optimality_audit_v1.json`，并在
  `configs/release_manifest_v2.json` 中绑定其 SHA-256。
- `scripts/audit_unified_release.py` 从已经通过 SHA 校验的
  `algorithm_search_rc1.json` 直接调用 `audit_algorithm_search` 重算最优性。
- 冻结 audit 必须与重算结果结构一致；冻结或重算 winner 都必须与搜索记录中
  的 `selected_candidate=A09` 一致。
- `accepted`、`algorithm_only_practical_optimum_proven` 只要任一未由重算证明，
  `algorithm_search_qualified` 与 `offline_algorithm_candidate_accepted` 均保持
  fail-closed。
- 补充伪造 accepted、冻结 audit 漂移、winner mismatch、artifact SHA 漂移四类
  负向测试。

## 当前证据与结论

当前受控搜索为 10 个候选，但只有 A09、A10 具备 paired normal/fallback
metrics，10 个候选均没有候选 evidence SHA。因此冻结 audit 中：

- `paired_metric_complete_candidate_count=2`
- `evidence_hash_complete_candidate_count=0`
- `confirmatory_practical_winner=A09`（仅是可用 finalist metrics 比较结果）
- `accepted=false`
- `algorithm_only_practical_optimum_proven=false`

统一审计现场重算结果：

- `algorithm_search_qualified=false`
- `offline_algorithm_candidate_accepted=false`
- `production_release_accepted=false`
- `accepted=false`

这意味着 A09 仍可作为待补证的工程候选，但不能再被表述为已经证明的受控搜索
最优算法，也不能进入最终生产 Pareto 发布。

## 验证

运行：

```text
python -m unittest tests.test_unified_release_audit
```

结果：23/23 通过。

关键 SHA-256：

- `current_algorithm_optimality_audit_v1.json`:
  `a758fde8fcc8ef4c6c29c6421b56984c8814afc1a4795457ae748ce23d009269`
- `scripts/audit_unified_release.py`:
  `4f665a185630cd64b9dcab0198605cb45d706b3c80b4d803ff7ffdfdca874cf0`
- `configs/release_manifest_v2.json`:
  `02a9e2baeb88beef87d2c9880a796b57745390a5912b319cb9e7660848ec3625`
- `tests/test_unified_release_audit.py`:
  `36a3a92e00d2682a3d6889125a1c7606e5c1b2494d431ec97f3a8656b325a681`

## 后续解除门条件

为所有 10 个候选补齐 hash-bound 的 normal/fallback paired metrics、每模式独立
重复以及输入 manifest hash，重新生成冻结 audit；只有重算得到唯一 practical
winner 且冻结结果完全匹配时，本门才允许算法候选继续进入生产联合 Pareto。
