# 新 NIC R0 campaign 接入 Unified 的只读设计

## 结论与边界

冻结的 R0 campaign 不能塞进现有 `physical_observations` 的三个独立 acceptance
条目。它是一个同时含 XDP×3、DPDK×3、fallback×3 与一次 before/after 恢复闭环的
整体证据包，DPDK backend 名称也与 unified 旧别名不同。正确入口是在 release
manifest 顶层新增一个互斥的 `new_nic_r0_campaign` bridge，由 unified 从 27 个
hash-bound artifact 调用冻结 evaluator 重新计算；不得只读取 `r0_audit.status`。

本设计不修改 `scripts/audit_unified_release.py`、`configs/release_manifest_v2.json`、
生产 Pareto 或已冻结 campaign 文件。

## Manifest 入口

`release_manifest_v2.json` 后续新增两个条目：

```json
{
  "config_artifacts": {
    "new_nic_r0_trust_profile": {
      "path": "schemas/new_nic_r0_unified_trust_profile_v1.schema.json",
      "sha256": "<local-file-sha256>"
    }
  },
  "new_nic_r0_campaign": {
    "schema_version": 1,
    "scope": "hft_mgbs_new_nic_r0_unified_bridge",
    "integration_mode": "exclusive_new_nic_campaign_v1",
    "campaign_id": "<campaign-id>",
    "artifact_root": "/home/wangwt/task/datasets/replay/hft_new_nic_r0_<id>",
    "trust_profile_config_name": "new_nic_r0_trust_profile",
    "artifact_manifest": {"path": "<absolute-path>", "sha256": "<sha256>"},
    "r0_audit": {"path": "<absolute-path>", "sha256": "<sha256>"},
    "runner_state": {"path": "<absolute-path>", "sha256": "<sha256>"},
    "frozen_helper_manifest": {"path": "<absolute-path>", "sha256": "<sha256>"},
    "external_trust_root_receipt": {"path": "<absolute-path-outside-artifact-root>", "sha256": "<sha256>"},
    "external_change_record": {"path": "<absolute-path-outside-artifact-root>", "sha256": "<sha256>"},
    "trusted_evidence_manifest_sha256": "<sha256>",
    "trusted_helper_manifest_sha256": "<sha256>",
    "trusted_arrival_manifest_sha256": "<sha256>",
    "backend_mapping": {
      "campaign_primary": "native_af_xdp_forced_zerocopy",
      "unified_primary": "native_af_xdp_forced_zerocopy",
      "campaign_fallback": "dpdk_rss_tss_multiqueue",
      "unified_fallback": "dpdk_multiqueue_rss_tss"
    },
    "expected_result": {
      "status": "r0_qualified",
      "xdp_primary_repeats_qualified": 3,
      "dpdk_fallback_repeats_qualified": 3,
      "fallback_trials_qualified": 3,
      "restoration_qualified": true,
      "r0_qualified": true,
      "mutations_performed": true,
      "production_qualified": false,
      "final_pareto_ingestion_allowed": false
    }
  }
}
```

精确字段合同见：

- `configs/schemas/new_nic_r0_unified_bridge_v1.schema.json`
- `configs/schemas/new_nic_r0_unified_trust_profile_v1.schema.json`

`new_nic_r0_campaign` 与旧 `physical_observations[*].counts_toward_r0=true` 必须互斥；
诊断观察可以保留，但旧计数路径必须全部为 false。否则同一流量可能被双重计数。

## 27 个 campaign artifact role

Unified 必须要求 artifact manifest 中 role 集合与合同完全相等，不能只检查子集：

```text
campaign, contract, arrival_inventory, arrival_preflight,
arrival_evidence_manifest, restoration_before, restoration_after,
xdp_run_1, xdp_run_2, xdp_run_3,
dpdk_run_1, dpdk_run_2, dpdk_run_3,
fallback_trial_1, fallback_trial_2, fallback_trial_3,
xdp_runner, dpdk_runner, generator_runner, resource_sampler,
fallback_orchestrator, restore_helper, campaign_executor,
trust_root_recorder, runner, composer, evaluator
```

静态信任 profile 固定以下已冻结代码身份：

| role | SHA-256 |
|---|---|
| contract | `93726304934626f0929799bd4492e7b6924be4704b2975078e150bd6572849ec` |
| runner | `8ca178ba71341369f4046693d5c1e31400c51be72125b6576f0fb24e516ed0b7` |
| composer | `209063c8031f9289a6a1c2087e3bd2f44aca9e78088199267224249bb8e0408f` |
| evaluator | `1665ad49a32edf9ce9d8c57a47d89120257cc7408bfc0d0d8f6296a7dfda222e` |

八个硬件 helper 的 SHA 在新卡到货、代码审查和变更批准后填入 profile，不能用
campaign 自己提交的 hash 作为批准值。profile 本身必须是 unified manifest 的本地
相对路径 config artifact，并受 release manifest hash 绑定。

## Unified 复算入口

建议新增纯函数，不改旧 observation validator：

```text
audit_new_nic_r0_campaign(
    bridge: dict,
    trust_profile: dict,
    receipt_root: Path,
    errors: list[str],
    evidence_hashes: dict[str, str],
) -> (physical_r0_qualified: bool,
      host_restoration_qualified: bool,
      physical_identity_summary: dict)
```

执行顺序必须是：

1. 用 Draft 2020-12 或等价的严格代码验证 bridge/profile；JSON loader 同时拒绝重复
   key 和 NaN/Infinity。现 unified loader 只拒 NaN/Infinity，接线时必须补重复 key。
2. 通过现有 `receipt_root` 镜像规则解析所有绝对路径；拒绝 symlink、非普通文件、
   空文件、目录穿越和 artifact root 外的 campaign 文件。
3. 验证 artifact manifest 文件 hash 等于 bridge 的
   `trusted_evidence_manifest_sha256`，且与外部 trust-root receipt 的单一 64-hex 值一致；
   外部 receipt/change record 必须位于 artifact root 外。
4. 解析 artifact manifest：role/path 唯一、relative path 安全、27 个 role 精确相等，
   每个文件实际 hash 与 manifest 相等。
5. profile 的 12 个批准 role hash 必须与 manifest 一致；不能把 manifest 里的 helper
   hash 回填成“批准值”。合同中的 role 集合也必须等于 profile 集合。
6. 到货 manifest hash 必须等于 bridge 的 `trusted_arrival_manifest_sha256`；其 checksum
   list 必须绑定复制后的 arrival inventory/preflight 字节。arrival preflight 必须是
   `self_consistent_capability_receipts_only` 且 production=false。
7. 从 11 个原始 JSON artifact 直接调用冻结入口
   `hft_mgbs.new_nic_r0:evaluate_r0_campaign`；传入的 producer hash 必须来自已验证的
   artifact manifest，`trusted_manifest_verified=True` 只能在步骤 1--6 全过后设置。
8. 重新计算结果必须与 `r0_audit` 完整 canonical JSON 相等，且 runner state 必须为
   `status=r0_qualified`、phase=`COMPOSE`、mutations=true。仅 audit status 相等不够。
9. 只有 result 的 XDP=3、DPDK=3、fallback=3、restoration qualified=true、errors=[]、
   R0=true 且 production/Pareto=false 时，返回 physical R0=true。

## Unified 身份输出

当前 R1--R4 会用 `physical_r0_identity_summary` 绑定一个 backend 和一个 hardware hash。
新 campaign 有主/备两种 backend，因此必须扩展而不能伪装为三个同 backend observation：

```json
{
  "campaign_id": "<id>",
  "run_bundle_identities": ["sha256(xdp receipt 1)", "...共6个..."],
  "generator_run_identities": ["sha256(generator nested receipt 1)", "...共9个窗..."],
  "hardware_identity_sha256": ["sha256(canonical arrival candidate ports)"],
  "backends": [
    "native_af_xdp_forced_zerocopy",
    "dpdk_multiqueue_rss_tss"
  ],
  "primary_backend": "native_af_xdp_forced_zerocopy",
  "fallback_backend": "dpdk_multiqueue_rss_tss",
  "contract_sha256": "937263...",
  "artifact_manifest_sha256": "<trusted evidence root>"
}
```

随后的 `audit_stage_campaign` 应要求 production stage receipt 的 backend 明确属于这对
backend，另增加 primary/fallback role 字段；当前 `len(expected_backends)==1` 的约束
会拒绝正确的新 campaign，不能靠丢弃 DPDK identity 绕过。

## 必须的负向测试

接线至少覆盖以下拒绝项：

1. bridge/profile 重复 JSON key、NaN/Infinity、额外字段、畸形类型。
2. 缺/多/重复任一 role，role path 重复、绝对/穿越/symlink/非普通文件。
3. artifact manifest SHA 与 bridge、外部 receipt、实际字节任两者不一致。
4. 外部 receipt 或 change record 位于 campaign root 内。
5. contract/runner/composer/evaluator 任一与 profile 固定 SHA 不同。
6. 任一 helper 与独立批准 profile SHA 不同；禁止 manifest 自证。
7. arrival root、inventory、preflight 任一漂移，或 arrival 状态不是 capability-ready。
8. 保存的 `r0_audit` 为 true，但重新计算失败；完整 audit canonical 不一致。
9. 保存的 audit 失败，但原始证据重算通过；仍拒绝，要求重新 compose/封存。
10. XDP/DPDK/fallback 任一只有两次、重复 run/trial ID 或 hash 相同。
11. R0 result 试图设置 production/Pareto true。
12. runner state 不是 COMPOSE/r0_qualified/mutations=true，或存在
    `RECOVERY_REQUIRED`。
13. 旧 observation 与 campaign 同时 counts-toward-R0，防止双计数。
14. backend mapping 漂移，尤其把 `dpdk_rss_tss_multiqueue` 未显式映射就当成旧 unified
    `dpdk_multiqueue_rss_tss`。
15. stage campaign 只绑定 primary 或只绑定 fallback，或者 hardware identity 与 arrival
    candidate ports canonical hash 不一致。

## 当前态

现有 `release_manifest_v2.json` 没有 bridge，unified 仍走旧
`physical_observations`，因此当前 `physical_r0_qualified=false` 是正确结果。新增 schema
只是接线规范，不会使当前环境通过任何门。

