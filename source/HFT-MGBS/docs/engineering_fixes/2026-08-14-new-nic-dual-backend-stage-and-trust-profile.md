# 新 NIC 双 backend stage 绑定与 trust-profile 实例修复

## 修复范围

本修复只补齐两个此前会阻塞新 NIC 闭环的本地合同能力，不执行远端或硬件
实验，也不改变算法、campaign runner、Rust、统一审计入口和 release manifest：

1. R0 输出的 XDP 主路径与 DPDK 回退路径，能够被 R1--R4 原始证据聚合器按
   backend role 精确绑定；
2. 用实际 pending profile 实例替代“把 JSON Schema 当成配置实例”的做法，并
   提供一个不能自我批准的严格 finalizer。

本修复没有完成 `scripts/audit_unified_release.py` 的端到端接线，也没有形成任何
新 NIC R0/R1--R4 运行证据。当前生产结论保持 fail-closed。

## 问题与根因

### 双 backend stage campaign

新 NIC R0 identity 同时包含：

- primary: `native_af_xdp_forced_zerocopy`
- fallback: `dpdk_multiqueue_rss_tss`

原 stage 聚合器只允许全 campaign 使用一个 backend。丢弃 fallback identity 会把
XDP 主路径成功错误等同为完整回退闭环；把两个 backend 混在同一重复计数中，又会
让某一 backend 缺失时仍可能满足 stage 的总重复数。

`aggregate_stage_evidence(..., backend_binding=...)` 现在要求：

- binding 只能包含 `primary_backend` 与 `fallback_backend`，二者必须是不同的非空值；
- 每张 receipt 必须有 `backend_role=primary|fallback`，其 backend 必须与 role 精确对应；
- 每个 stage 分别满足 primary 与 fallback 的 `required_repeats`，不能互相补数；
- runtime manifest、capture binary、stage config 在各 backend 内分别保持冻结；
- code、input、contract、model、hardware 仍跨两个 backend 保持一致；
- 所有 run/generator/evidence identity 仍跨全部 receipt 唯一；
- 丢包、P99/P999、资源、关键流、fallback、质量与复杂度等原始硬门不放宽，最终
  Pareto 指标继续按全部 receipt 的保守最差值聚合。

`stage_backend_binding_from_r0_identity()` 只接受顺序和别名都精确的 XDP-primary /
DPDK-fallback identity，为后续统一审计接线提供窄接口。它不替代 R0 qualified gate。

## Pending trust profile

`configs/new_nic_r0_unified_trust_profile_v1.json` 是实际配置实例，但其状态明确为
`hardware_helpers_pending`。四个已冻结 core role 使用真实 SHA-256；尚未实现和独立
审批的八个硬件 helper 必须为 JSON `null`。该实例故意不能通过
`_validate_profile()`，所以不能被当作 approved profile 接入统一审计。

待实现和审批的八个 helper 为：

```text
xdp_runner, dpdk_runner, generator_runner, resource_sampler,
fallback_orchestrator, restore_helper, campaign_executor,
trust_root_recorder
```

## Finalizer 信任边界

`scripts/finalize_new_nic_r0_trust_profile.py` 不是审批主体，不生成 helper manifest、
trust receipt 或 approval record。只有以下条件同时成立时才创建新 approved 文件：

1. pending profile 字段、role 顺序、四个 core SHA 与 approved schema 常量精确一致；
2. helper manifest 恰好包含 12 个 code/executable role，四个 core 指向仓库冻结路径，
   八个 helper 指向指定 helper root 内的真实文件；
3. 12 个文件均为非 symlink 普通文件，路径和文件 identity 不复用，内容 SHA 与
   manifest 精确一致；八个 helper 在 POSIX 上还必须可执行；
4. helper manifest SHA 等于调用方预先钉住的 SHA，并与外部 trust receipt 的单行
   小写 SHA 一致；
5. 外部 approval record 精确绑定 pending-profile SHA、helper-manifest SHA、12 个
   实际 role SHA、合同、change ID 与 approver，且其自身 SHA 也由调用方预先钉住；
6. approval record 与 trust receipt 均位于仓库、helper root 和输出目录之外；
7. 所有 JSON 拒绝重复 key、NaN/Infinity 和非对象顶层；批准输出满足现有
   `_validate_profile()`，但 `production_qualified` 与
   `final_pareto_ingestion_allowed` 仍为 `false`；
8. 输出必须不存在且不能与 pending 输入同路径；成功时用临时文件、fsync 和
   create-if-absent 方式提交，失败不覆盖或遗留 approved 文件。

仅在命令行同时传入 helper manifest SHA 和外部 approval-record SHA，不代表密码学
签名；它要求上游变更系统或 release 流程在调用 finalizer 之前独立冻结这两个根。
如果没有这种独立钉住关系，就不能运行 finalizer，更不能把 pending 改名为 approved。

## 最短后续工程路径

1. 实现并代码审查八个真实 helper；冻结 12-role helper manifest，并在独立变更系统
   记录 manifest SHA、pending-profile SHA 和 12 个 role SHA。
2. 由独立流程写入 trust receipt 与 approval record，预先冻结 approval-record SHA。
3. 调用 finalizer 生成新的 approved profile；不覆盖 pending 实例。
4. 在统一审计中显式调用 `stage_backend_binding_from_r0_identity()`，并把结果作为
   `backend_binding` 传给 `aggregate_stage_evidence()`；同时要求 stage receipt 引用层
   校验 `backend_role` 和对应 backend。
5. 更新 release manifest，使 `new_nic_r0_trust_profile` 指向生成的 approved 实例及其
   精确 SHA。只有真实新 NIC R0 通过后，才采集双 backend R1--R4 campaign。
6. 完成双 backend 运行、丢包/P99/P999/资源/关键流/fallback 全门及最终 Pareto 重算；
   在此之前不得声称端到端接线、生产 qualified 或最终 Pareto 已完成。

## TDD 与回归

新增测试先证明旧聚合器不能接受双 backend 参数，再实现能力。覆盖：完整双 backend、
缺 fallback role、role/backend 对调、R0 identity 缺 fallback/顺序或别名错误、pending
不可批准、外部根完整时批准、helper 漂移、未钉住审批记录、symlink helper 与禁止覆盖。
原单 backend campaign 和所有既有 stage 原始硬门测试继续通过。
