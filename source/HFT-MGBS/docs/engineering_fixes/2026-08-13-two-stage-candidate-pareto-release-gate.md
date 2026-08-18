# 2026-08-13 统一候选证据门与最终 Pareto 发布门解耦

## 问题

旧闭环把统一审计同时当作“候选证据完整”“已完成 Pareto 选择”和“生产发布”证明。统一审计又要求最终 Pareto 尚不存在，导致两个阶段互相等待：没有统一审计就不能进入 Pareto，而统一审计又不能在选择前产生可接纳结果。因此即使构造全部密封证据，正向路径仍不可达。

## 修复边界

本次只修改统一审计、生产联合 Pareto、对应 CLI、策略、当前候选、测试和本记录；不修改 `production_stage_receipt_contract_v1.json`、runtime 决策或两个正在独立生成的 algorithm/new-NIC campaign 文件。

修复后采用严格两阶段语义：

1. `scripts/audit_unified_release.py` 只证明单个部署候选的证据密封与全流水线完整性。成功时输出 `candidate_evidence_accepted=true` 和 `final_pareto_ingestion_allowed=true`，但固定 `selection_performed=false`、`selected_candidate=null`、`production_release_accepted=false`、`accepted=false`、`final_pareto_eligible=false`。
2. `hft_mgbs/production_pareto.py` 重新读取并计算统一候选审计和候选证据收据的 SHA-256，校验候选、算法、backend、runtime receipt、原始证据和联合指标完全绑定，再执行硬门、Pareto 前沿和 Champion 选择。
3. 只有生产 Pareto 实际选出 Champion 时，最终输出才允许 `production_release_accepted=true`、`accepted=true` 和 `final_pareto_eligible=true`。
4. 原来容易误导的 `release_receipt` / `unified_release_audit` 输入名改为 `candidate_evidence_receipt` / `unified_candidate_evidence_audit`；策略冻结两个 scope 以及统一阶段必须保持非生产、未选择状态。
5. release manifest 新增独立的 `deployment_candidate_id`；原 `candidate_id=A09` 继续表示算法 ID，防止部署封装 ID 与算法候选 ID 混用。

## TDD 证据

实现前新增两个正向测试并确认红灯：

- 完整统一候选仍返回算法 ID 而不是部署候选 ID，且不能进入 Pareto ingestion；
- 两个完整密封候选不能产生最终 production release。

实现后定向回归 `tests.test_unified_release_audit` 与 `tests.test_final_pareto_selector` 共 `43/43` 通过。正向测试证明第一阶段可达但不自称发布，第二阶段只有 Champion 才授予最终发布；伪造 acceptance、收据漂移、指标篡改、缺失统一审计、未知算法和 generic/SKB XDP 仍 fail-closed。

## 当前环境结果

当前真实环境仍拒绝发布，符合预期：

- 统一候选审计退出码 `2`：`candidate_evidence_accepted=false`、`final_pareto_ingestion_allowed=false`、`production_release_accepted=false`、`accepted=false`，错误数 `10`。
- 生产 Pareto CLI 退出码 `10`：无 Champion，`production_release_accepted=false`、`accepted=false`，全局错误数 `6`。
- 当前统一审计 SHA-256：`f6e30dee778a10e63c4709687d99340782e39897263b44a960f7d44eda2ae88f`。
- 当前生产 Pareto 审计 SHA-256：`da4ab626f6784fe1fc56b9f5ce214f0184e39f6f5b5e42214a44e384bc7fd6e5`。

## 冻结字节

- `scripts/audit_unified_release.py`: `ad255d82338afa7d8966cf7fb0e6b906c405e613b6bb561db1025291cea9d9e5`
- `hft_mgbs/production_pareto.py`: `d33f9212b44e12d5d6fc529b8ea8276c83835de5f64b8ab3682d08f9f207dbe9`
- `scripts/select_production_pareto.py`: `d00d419bb95703ce6d9c6295675f85cf0c7ca0b86cdc3566bc1b8135361448f8`
- `configs/release_manifest_v2.json`: `d802546349464d4bfb08f70842cf2f77bff56de54deb80d2b1e6dad8d513c66f`
- `configs/final_pareto_policy_v1.json`: `754c0cad3e9aae5c69cec5592a3f218eb5caba6f9127406cd89302258c478c9e`
- `configs/current_environment_joint_candidates_v1.json`: `f44910417b1e334fbed289361d12d663e5e87f37c7cf629fd12d5140d143dbec`

## 第二阶段接线边界

algorithm qualification campaign 与 new-NIC R0 campaign 冻结后，必须由独立变更把它们的外部可信 artifact manifest、实际 SHA 和重算结果接入统一候选审计。不得仅复制 campaign 的 `qualified` 布尔值，也不得在 campaign 尚未冻结时把 pending 路径写入 release manifest。

