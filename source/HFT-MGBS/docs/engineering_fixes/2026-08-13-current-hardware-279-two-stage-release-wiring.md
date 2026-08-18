# 2026-08-13 当前硬件 2.79 Mpps 两阶段发布接线

## 问题与冲突边界

`current_hardware_279` v2 已能从 3 次 normal 与 3 次 fallback 的原始输入重算单个候选，但输出边界明确固定为非生产、不可进入最终 Pareto。历史 unified/Pareto 链不能直接接入该结果：历史链冻结了 10/12 Mpps R0、R1--R4、native AF_XDP/DPDK standby 以及 10 Mpps 硬门；当前 BCM57810 的 TPACKET 2.79 Mpps 候选不满足这些语义。强行复用会把当前上限候选误报为历史 10/12 Mpps 生产候选。

因此本修复新增独立命名空间，不修改以下历史文件。修改前后复核 SHA-256 相同：

- `scripts/audit_unified_release.py`: `44f4d06f8e423aaaacd4478b84afef861021efa13af2e9abeae0604413434a14`
- `hft_mgbs/production_pareto.py`: `d33f9212b44e12d5d6fc529b8ea8276c83835de5f64b8ab3682d08f9f207dbe9`
- `scripts/select_production_pareto.py`: `d00d419bb95703ce6d9c6295675f85cf0c7ca0b86cdc3566bc1b8135361448f8`
- `configs/release_manifest_v2.json`: `8d9097e73d66575e8a73677ece76c59127a4abdb48097592ca26668876db0d2f`
- `configs/final_pareto_policy_v1.json`: `754c0cad3e9aae5c69cec5592a3f218eb5caba6f9127406cd89302258c478c9e`

旧 B1/B2 突破 acceptance、旧 DPDK acceptance、失败 normal、单个合格候选均不能获得本链资格。

## 两阶段语义

### Stage A：统一候选证据

Stage A 接受一个 `hft_mgbs_current_hardware_2_79_campaign_receipt_v1`。审计器不会信任 receipt、raw-run audit 或 candidate audit 中的正向布尔值，而是执行以下操作：

1. 重哈希冻结的 v2 profile、六个 raw-run input、六个存档 raw-run audit、candidate input、candidate audit 和 campaign receipt。
2. 对每个 raw-run input 再次执行 `compose_current_hardware_raw_run_v2`，要求 normal/fallback 各 3 次，mode/repeat 矩阵完整，六个输入内容哈希不同。
3. 对 candidate input 再次执行 `compose_current_hardware_candidate_v2`，并逐项比较存档 audit 与重算结果。
4. 从重算窗口派生吞吐、丢包、关键流覆盖、五层延迟、质量和 fallback 恢复指标；receipt 中的指标必须完全相同。
5. 在调用 v2 composer 前后重哈希 raw input、evidence manifest 的全部条目及所有显式 artifact，拒绝父目录/文件 symlink、同路径别名、自引用和 TOCTOU 漂移。
6. `identity_receipt` 与 `diagnostic_receipt` 必须同时绑定 runner、config、capture binary、model、runtime manifest、service/engine source 和 launcher 的 SHA-256，并绑定同一 run/generator/hardware/code 身份。仅替换 binary 并重封 evidence manifest 仍会被拒绝。

Stage A 成功只允许：

- `candidate_evidence_accepted=true`
- `full_pipeline_qualified=true`
- `final_pareto_ingestion_allowed=true`

它固定保持 `selection_performed=false`、`selected_candidate=null`、`production_release_accepted=false`、`accepted=false`，因此不会把一个候选自称为生产冠军。

### Stage B：当前硬件冠军发布

Stage B 对每个候选重新读取并重哈希 Stage-A manifest、unified audit 和 campaign receipt，然后重新执行完整 Stage A。只有至少 2 个候选均完成评估、candidate ID、campaign receipt 及真实 evaluation identity 均不重复、所有重算值一致时，才进入选择。evaluation identity 由 backend 加代码、runner、config、capture binary、model、runtime manifest、service/engine source 和 launcher 身份共同构成；仅修改 candidate 标签不能计为第二个候选。

Stage B 在 Pareto 前再次独立执行冻结硬门。硬门逐项冻结关系、限值与量纲，包括 2.79 Mpps、15 个完整窗口、零丢包、关键流覆盖、五层延迟、质量和 fallback 恢复；目标函数方向与 champion 顺序也按精确 JSON 类型冻结。policy 将 `true` 换成 `1`、将吞吐方向换成 `min` 或弱化阈值都会 fail-closed。

Stage B 成功时的 `production_release_scope` 只能是 `current_hardware_bcm57810_2.79_mpps_only`，同时永久输出 `ten_mpps_or_line_rate_claim_allowed=false`。它不能替代历史 10/12 Mpps 发布结论。

## 工程执行流程

1. 每个现场运行用 `compose_current_hardware_279_raw_run_v2.py` 绑定 runner 目录并产生一份 raw-run audit；若已独立准备好完整的 staged raw input，则可改用 `compose_current_hardware_279.py --kind raw-run-v2`。两条路径二选一，共形成六份 audit。正式 identity/diagnostic receipt 必须带本文件所列的双重 release artifact 绑定；旧 receipt 缺少这些字段时不得补写为合格，只能重新采集。
2. 将六份 audit 写入 candidate input，执行 `compose_current_hardware_279.py --kind candidate-v2`。
3. 使用 `scripts/seal_current_hardware_279_campaign.py`，传入冻结 policy/profile、candidate input/audit，并恰好重复六次 `--raw-run-input`，生成 campaign receipt。命令对矩阵或任何重算失败返回非零。
4. 复制 `configs/current_hardware_2_79_stage_a_pending_v1.json`，替换 `campaign_receipt` 为真实 path/SHA-256，并把 Stage-A claim 改为与真实重算结果一致；执行 `scripts/audit_current_hardware_279_release.py --stage a`。
5. 至少形成两个不同的 Stage-A 合格候选后，复制 `configs/current_hardware_2_79_stage_b_pending_v1.json`，为每个候选绑定 Stage-A manifest、unified audit 与 campaign receipt 的 path/SHA-256；执行同一审计 CLI 的 `--stage b`。
6. 只有 Stage B 退出码 0、`champion_id` 非空且 `production_release_accepted=true`，才完成“当前硬件 2.79 Mpps operating point”发布闭环。任何缺失或漂移返回退出码 2。

## 当前真实状态

仓库中尚无合格的 normal3+fallback3 campaign，也没有两个完成评估的候选，因此默认配置有意保持 fail-closed：

- Stage A pending audit：`candidate_evidence_accepted=false`，错误为 `stage_a.campaign_receipt.reference`。
- Stage B pending audit：`evaluated_candidate_count=0`、`champion_id=null`、`production_release_accepted=false`，错误包含 `0<2`。
- 两份 audit 都是当前状态审计，不是合格实验或生产发布收据。

## TDD 与回归

新增测试先覆盖以下失败路径，再实现正向路径：失败 normal 即使伪造正向声明、receipt/hash 漂移、旧 B1/B2 shape、单候选、重复候选/receipt、同一真实候选改标签、Stage-A 伪造 production、unified 漂移、binary 替换后重封 manifest、raw/Stage-A TOCTOU、父目录 symlink、嵌套 JSON 重复 key、NaN、自引用、policy 方向/硬门漂移、CLI 输出异常和默认 pending 配置，全部 fail-closed。

红队结论：初版存在 2 项 P0 与 3 项 P1，均已在本命名空间修复并由负测锁定。

- P0：Stage B 初版只去重 candidate ID 与 receipt，允许同一真实 variant 换标签计为两个候选；现改为 backend + 完整 artifact evaluation identity 去重。
- P0：v2 能重哈希 artifact，但初版 release 层没有证明运行 receipt 所述进程实际使用该 runner/config/binary/model/runtime；现要求 identity/diagnostic 双绑定。
- P1：Stage B 初版没有把全部硬门关系、阈值、单位和目标方向精确冻结并二次执行；现已显式冻结并在 Pareto 前验证。
- P1：初版存在二次按路径读取和父目录 symlink/TOCTOU 窗口；现对整棵证据引用执行前后稳定性检查并拒绝任一 symlink component。
- P1：CLI 输出路径异常会产生 traceback；现返回结构化 fail-closed JSON 到 stdout、退出码 2，且禁止覆盖 policy/input。

验证结果：

```text
python -m unittest discover -s tests -p test_current_hardware_279_release.py -v
Ran 13 tests in 645.578s
OK

显式绑定本地 tests 命名空间后运行：
current_hardware_279_v2 + raw_run_adapter + unified_release + final_pareto
Ran 56 tests in 64.910s
OK

python -m py_compile hft_mgbs/current_hardware_279_release.py \
  scripts/audit_current_hardware_279_release.py \
  scripts/seal_current_hardware_279_campaign.py
exit 0
```

本机 Python 安装中存在 `site-packages/tests`，会遮蔽仓库未带 `__init__.py` 的 `tests` 目录；旧回归使用显式本地测试命名空间执行。本修复未为此修改测试包结构或生产代码。

## 冻结字节

- `hft_mgbs/current_hardware_279_release.py`: `a24f90ae643b9d37ae89f065c2841a4b8e6fd4f98ad780319a4e1387648fcb0b`
- `scripts/audit_current_hardware_279_release.py`: `f9da7399d6a0575a61f24a636b90b421ad5a39253165b98c155cc7bd064b8b5c`
- `scripts/seal_current_hardware_279_campaign.py`: `fc42457d6ac08379a9e1d150b7702734f74c2bff88d9128c150f2303a4954154`
- `configs/current_hardware_2_79_two_stage_release_policy_v1.json`: `941de2c7b2c3258d35c5584e760b1dceeb20482490659304e0884d068cc5cb3e`
- `configs/current_hardware_2_79_stage_a_pending_v1.json`: `8b1aec3dbf55b9ac1216f570ffca7b535305be868b7da0161888ecb0a1a694ea`
- `configs/current_hardware_2_79_stage_b_pending_v1.json`: `c3bcba3682b17ff29c731a3bea1020c2f3c69a04e4979e9c98b2e22153b20212`
- `docs/experiments/current_hardware_2_79_stage_a_pending_audit_v1.json`: `7e0c2525beb60a1d6546332718d4e2dbacd8af7a9f3410d16c699a730328dd3f`
- `docs/experiments/current_hardware_2_79_stage_b_pending_audit_v1.json`: `270692107475251242df02c950d54dff64e8d103c5a9a25c8f66c679900884d7`
- `tests/test_current_hardware_279_release.py`: `097cd468de4288c4ee611524484ebfef99f1b8185eb56fd1faf010b7c1bbec4c`
