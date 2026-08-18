# Unified R0 可信链与阶段发布门加固

## 问题

统一发布审计器虽然已经核验 DPDK/TPACKET 回执与文件哈希，但仍存在四个会放大结论的缺口：

1. `audit_policy.backend_priority` 只是清单文字，审计器没有冻结“原生 XDP + 强制零拷贝优先、DPDK 多队列回退”的顺序。
2. 三次 R0 可以只靠路径/回执哈希区分，没有同时证明运行身份和独立发生器运行身份不同；DPDK 也没有证明是在 XDP 失败后才回退。
3. 12 Mpps 主要绑定阈值合同，缺少对同一密封目录中 `result.json` 原始计数的重新计算；恢复布尔值也没有逐项绑定驱动回绑、接口、HugePage、运行目录与最终状态账本。
4. R1/R2/R3/R4 通用回执中的 `qualified=true` 可以被直接消费，但尚无逐阶段原始指标验证器。

## 修复

- 冻结后端顺序和可计数后端：只有 `native_af_xdp_forced_zerocopy` 与 `dpdk_multiqueue_rss_tss` 能进入 R0 三次重复计数；TPACKET 与 AF_PACKET 永远只作诊断/安全回退。
- 每个可计数运行必须提供同目录、SHA-256 绑定的 `backend_selection.json`。该回执必须证明：已尝试 native XDP 和强制 zero-copy；选择 DPDK 时存在受限回退原因；发生器与抓包硬件身份不同且不共享抓包适配器包预算。
- 运行身份、发生器运行身份必须是不同的 SHA-256；三次运行要求路径、acceptance hash、evidence-manifest hash、运行身份和发生器身份均不同，同时硬件、后端和冻结合同相同。
- 可计数 R0 必须从同一密封目录读取并重新计算 `result.json`：64B、12 Mpps TX/RX 最低逐秒窗口、至少 15 个完整窗口、包数守恒、零丢包/零 `rx_nombuf`、P99/P999，以及 XDP native/zero-copy 或 DPDK RSS/TSS 与至少 8 RX/8 TX 队列。
- `result.json` 中 runner、二进制、validator 和 composer 的实际 SHA-256 必须与冻结合同一致，避免仅凭最终状态码信任未知执行器。
- DPDK 恢复账本要求 child 停止、双 PF 回绑 bnx2x、双接口恢复、运行前缀清理、HugePage 恢复、hugetlbfs 保留和最终状态核验；XDP 回执要求程序卸载、UMEM 释放、接口恢复和最终状态核验。证据哈希失败与恢复是否成功分开报告，避免一项遮蔽另一项。
- R1--R4 在逐阶段原始指标验证器落地前一律返回 `stage_validator_unimplemented`；通用 `qualified=true` 不能推动发布。
- 输出保留 `evidence_sha256`，新增 `physical_r0_identity_summary`。字段名与生产 Pareto 消费器统一为 `derived_production_pareto_metrics`；由于阶段验证器未实现，该字段为 `null`、`derived_production_pareto_metrics_available=false` 且列出阻断原因，不伪造 Pareto 输入。
- CLI 在导入项目内 `scripts` 模块前将检出树根目录加入 `sys.path`，因此可从项目根直接运行，不依赖 editable install 或调用者设置 `PYTHONPATH`；真实子进程回归会清除 `PYTHONPATH` 并验证当前非发布状态返回退出码 2 且写出完整审计 JSON。

## 修改范围

- `scripts/audit_unified_release.py`
- `configs/release_manifest_v2.json`
- `tests/test_unified_release_audit.py`

未修改 Pareto 选择器、运行时调度器、远端文件或远端设备状态。

## 验证

本地 bundled Python 执行：

```text
python -m py_compile scripts/audit_unified_release.py tests/test_unified_release_audit.py
python -m unittest tests.test_unified_release_audit -v
python scripts/audit_unified_release.py configs/release_manifest_v2.json --output docs/experiments/current_environment_unified_release_audit_v2.json
```

覆盖的负向合同包括：后端顺序漂移、未尝试 XDP 即选择 DPDK、原始 RX 只有 11.9 Mpps、重复发生器身份、证据哈希不匹配、恢复账本缺步骤、TPACKET 冒充生产 R0，以及 R4 自报 `qualified=true`。

## 当前边界

- 本次没有远端执行，也没有生成新的 XDP/DPDK 生产回执；当前 manifest 必须继续保持 `physical_r0_qualified=false` 与最终发布 false。
- 尚缺能够生产上述 `backend_selection.json`、生产版 `result.json` 和 native-XDP acceptance 的正式 runner/composer。
- R1--R4 的逐阶段原始数据 schema 与重算器尚未实现，因此当前无法形成可信 `derived_production_pareto_metrics`。
- `host_restoration_qualified` 只表达本地镜像中可核验的恢复证据，不替代实验后的独立远端只读核验。
