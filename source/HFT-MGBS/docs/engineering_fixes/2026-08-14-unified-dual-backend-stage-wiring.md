# Unified 新 NIC 双 backend stage 接线

## 结果

`scripts/audit_unified_release.py` 已把新 NIC R0 输出的 XDP 主路径和 DPDK
回退路径接入 R1--R4 原始 stage campaign 重算。该接线只扩展统一审计的证据绑定，
不修改 release manifest、最终 Pareto 策略、当前审计产物、算法 campaign 或新 NIC
R0 信任配置。

当前 `new_nic_r0_unified_trust_profile_v1.json` 仍是
`hardware_helpers_pending`，当前 release manifest 的 stage campaign 仍是 pending；实跑
结论保持 `physical_r0_qualified=false`、R1--R4 全 false、
`full_pipeline_qualified=false`、`final_pareto_eligible=false`。

## 接线语义

统一审计保留两种互斥路径：

1. 旧 physical identity 不含 `primary_backend` / `fallback_backend` 时，继续要求
   `backends` 去重后恰好只有一个值，并按旧合同将每张 receipt 绑定同一个在线
   runtime manifest；
2. 新 physical identity 含主备字段时，必须由
   `stage_backend_binding_from_r0_identity()` 精确验证
   `native_af_xdp_forced_zerocopy` 为 primary、
   `dpdk_multiqueue_rss_tss` 为 fallback，且 `backends` 顺序与二者完全一致。

双 backend 路径中，每张 receipt 在统一引用层和原始聚合层都必须满足：

- `backend_role=primary` 只能绑定 XDP backend；
- `backend_role=fallback` 只能绑定 DPDK backend；
- 每个阶段的 primary 与 fallback 分别达到冻结的 repeat 数，不能互相补数；
- hardware、代码、输入、模型和合同保持跨 backend 一致；runtime manifest、capture
  binary 和 stage config 按 backend role 内冻结；
- 实时身份探针的 runtime SHA 绑定当前在线 primary；fallback runtime 继续通过密封
  receipt、identity manifest、evidence manifest 和逐文件 SHA 独立验证。

任何残缺或顺序错误的主备 identity、缺 fallback receipt、role/backend 对调以及
`physical_r0_qualified=false` 都会 fail-closed。即便双 backend stage 原始证据完整，
pending R0 信任也不能被绕过。

## TDD 与验证

在 `tests/test_unified_release_audit.py` 中新增真实密封 campaign 夹具，逐张写入 identity
manifests、原始计数、证据清单和 SHA-256，并覆盖：

- 完整 XDP-primary / DPDK-fallback campaign 正例；
- 单阶段缺一张 fallback repeat；
- primary/fallback role 对调；
- stage 证据完整但 R0 trust 仍 pending；
- 原单 backend campaign 回归。

本地验证结果：

```text
tests/test_unified_release_audit.py                         28 passed
tests/test_stage_evidence.py                               22 passed
tests/test_new_nic_stage_backend_adapter.py                 3 passed
tests/test_new_nic_r0_unified_integration_contract.py      12 passed
python -m py_compile scripts/audit_unified_release.py \
  tests/test_unified_release_audit.py                       passed
```

当前配置只读实跑结果：

```text
audit_complete=true
physical_r0_qualified=false
runtime_identity_current=false
r1/r2/r3/r4_24h/r4_72h=false
full_pipeline_qualified=false
candidate_evidence_accepted=false
production_release_accepted=false
final_pareto_eligible=false
stage.campaign.pending present
```

因此，本修复完成的是双 backend 的审计接线和拒绝语义，不是硬件实验完成或生产发布。
