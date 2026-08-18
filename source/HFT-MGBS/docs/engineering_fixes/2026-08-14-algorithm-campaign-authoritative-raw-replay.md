# Algorithm campaign 权威只读 raw replay

日期：2026-08-14

## 结果

新增 `hft_mgbs/algorithm_campaign_replay.py`，提供：

```python
verify_algorithm_campaign_raw_replay(
    repo_root,
    contract_path,
    campaign_root,
    formal_receipt_path,
    search_path=None,
)
```

该 API 从 GPU campaign 树的正式回执出发，调用同一 formal finalizer 的验证链重新计算，但将 finalizer 拟写出的 JSON 全部截获在内存中，不覆盖任何正式产物。重放前后分别对完整 campaign 树做稳定 inode、类型、权限、大小、mtime 和内容 SHA-256 快照；重放期间另有写操作拦截。只有前后树完全相同，重算结果才可标记为 `authoritative_raw_replay_complete=true`。

## 权威重放范围

一次成功重放必须同时满足：

- `plan.json` 可由当前 hash-bound contract 和冻结 search 精确重编译；
- `input_sha256.json` 精确覆盖 training manifest、holdout manifest、ground truth 和样本文件，共 27 个绝对路径，并重新读取全部文件验证大小和 SHA-256；
- `input_stat_identity.json` 从 27 个现场文件的 device/inode/mode/link count/size/mtime/ctime 逐项重算；
- `environment_identity.json` v2 不再信任 Conda 命令或名称，而是把 contract/plan 中的直接 `python_executable` 与 `environment_prefix` 作为执行身份；它从 v4 whole-prefix exact-tree `environment_files_sha256.json`、`runtime_bootstrap_identity.json` 和 `external_tools_sha256.json` 实际文件重算 SHA-256、项数及现场文件身份，并把 `-I -S` 隔离启动器绑定的 Python executable、`site_packages`、numpy/scipy/sklearn/joblib 和线程环境精确交叉核验；
- 候选集合精确为 A01--A10，且 `evaluated_candidate_count=10`；`feasible/qualified` 按 hard constraints 独立计数，不得把未过硬约束的候选伪装为“未评估”；每个候选精确包含 normal/fallback 两种模式和种子 7/11/19，共 60 份 raw repeat；
- 每份 raw repeat 的候选参数、全部执行上限、dataset role、capture count、输入清单、关键流分子/分母、非 training 流标签指纹、事件召回分子/分母和逐事件 witness、seed 预测数组、混淆矩阵、校准阈值与 conservative 汇总重新验证；
- 10 份 run manifest、code manifest、result manifest 和 summary 从原始文件重验；summary 不能替代 raw repeat；
- finalizer 在内存中重新生成 10 份 candidate receipt、suggested projection 和 formal campaign receipt，共 12 个拟产物；
- 上述 12 个拟产物与磁盘正式产物逐字段相等、canonical JSON 字节相等且 SHA-256 相等；projection optimality audit 也必须由 raw 指标重算一致；formal receipt 若绑定外部 contract trust root，重放将同一 trust root 交回 finalizer 并由 finalizer 重新核验。

成功的 raw replay 仍只证明算法 campaign 的证据重放完整性。返回值固定保持 `production_joint_optimum_proven=false` 和 `final_pareto_ingestion_allowed=false`；生产放行仍需 XDP 主路径、DPDK 回退路径的物理吞吐、丢包、P99、资源、关键流覆盖与回退恢复证据共同通过。

## 失败关闭测试

`tests/test_algorithm_campaign_replay.py` 构造了 27 项冻结输入、A01--A10、normal/fallback、每模式 3 个种子的完整正式 campaign，再针对以下情况逐项验证失败关闭：

- raw seed 漂移，即使攻击者同步重封 result manifest；
- fresh evaluation group、`selected_flow_label_sha256` 或逐事件 witness 漂移；
- 缺失 raw repeat；
- summary 指标伪造；
- direct-target Python executable 或整个 environment prefix 树漂移；
- candidate receipt 的 campaign identity 伪造；
- receipt 路径逃逸；
- campaign 树任意 symlink；
- plan campaign ID、input entry count、input stat、Python environment whole-prefix exact tree、runtime bootstrap、external tools、run/code/result manifest、projection、formal audit 和 external contract trust root 漂移；
- finalizer 绕过 JSON 捕获直接尝试写 campaign 树。

本地 Python 3.7.6 验证：

```text
python -m py_compile hft_mgbs/algorithm_campaign_replay.py tests/test_algorithm_campaign_replay.py
python tests/test_algorithm_campaign_replay.py -v
Ran 11 tests
OK
```

## 集成边界

本补丁刻意不修改 shared gate、unified audit、Pareto selector、contract 或 runner。下一步由 release gate 显式调用该 API；gate 必须同时要求 formal campaign 自身 `accepted=true`、raw replay `authoritative_raw_replay_complete=true`，不得仅凭 10 份 summary/candidate receipt 放行。
