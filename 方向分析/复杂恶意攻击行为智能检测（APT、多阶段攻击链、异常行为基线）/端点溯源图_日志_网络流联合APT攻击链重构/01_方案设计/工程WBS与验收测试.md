# 工程 WBS 与验收测试

- 版本：`Engineering WBS v1.1-deep-read`
- 日期：2026-07-29
- 代码根：`source/EACR-APT`

## 1. 当前代码基线

| 模块 | 当前状态 | 可复用 | 缺口 |
|---|---|---|---|
| `schema.py` | 已有 Event/ChainGroundTruth | 模态校验、真值分离 | 时间区间、sensor health、typed edges、版本迁移 |
| `alignment.py` | 已有解释性 pair score 和 ambiguity 拒绝 | H1 最简下界 | 候选生成、训练/校准、Top-k、批处理、评测 |
| `reconstruct.py` | 已有链评分和确定性 beam search | B1 下界 | UCTEG、约束子图、分支、unknown、证据包 |
| dataset collectors | 较完整 | 远端下载和完整性 | 不等于研究数据适配器 |
| local policy/sync | 已有 | 本地禁存与前向同步 | 需纳入每次 gate |
| tests | 2026-07-29 核心 9/9 通过 | 最小回归 | 缺 adapters/evaluator/e2e/performance/fault tests |

## 2. 建议代码结构

```text
eacr_apt/
  schema/
  adapters/
  truth/
  quality/
  candidates/
  alignment/
  graph/
  seeds/
  reconstruction/
  calibration/
  evaluation/
  reporting/
  runtime/
configs/
  datasets/
  splits/
  methods/
  experiments/
tests/
  unit/
  property/
  golden/
  integration/
  leakage/
  performance/
  fault/
```

## 3. WBS

### W0：控制面（E0）

| ID | 工作包 | 产物 | 验收 |
|---|---|---|---|
| W0.1 | 路径配置统一 | typed path config | 所有写路径位于远端允许根 |
| W0.2 | manifest schemas | data/split/run/environment | schema validation |
| W0.3 | 本地禁存策略 | 扩展检查器和 ignore 策略 | forbidden fixture 必须阻断 |
| W0.4 | run ID/状态机 | runtime manifest | complete/failed/timeout/unrun/unknown 正确 |
| W0.5 | 同步和远端测试 | sync report | 前向同步、不删远端重资产 |
| W0.6 | 传感器健康契约 | drop/reorder/clock/integrity schema | 不健康和未知状态不能静默转为正常 |

### W1：数据适配和真值（E1）

| ID | 工作包 | 产物 | 验收 |
|---|---|---|---|
| W1.1 | 统一 schema v2 | Event/Entity/TypedEdge | round-trip/property tests |
| W1.2 | DARPA TC adapter | normalized shards+quality | 样本可回溯 |
| W1.3 | CICAPT adapter | provenance/flow/truth views | 派生/独立源标记正确 |
| W1.4 | LANL adapter | auth/proc/DNS/flow | 未标注不变良性 |
| W1.5 | strong-truth adapter | steps/alignment/chain truth | truth 不可被训练模块 import |
| W1.6 | quality reporter | per-source quality JSON | 解析、缺失、乱序、时钟完整 |
| W1.7 | 会话与身份解析 | logon GUID/session/NAT/alias map | 可输出一对多候选和冲突，不强制唯一 |

### W2：下界和评测器（E2）

| ID | 工作包 | 产物 | 验收 |
|---|---|---|---|
| W2.1 | oracle/硬对齐 | exact/window/5-tuple/session | golden pairs |
| W2.2 | 图搜索 | BackTracker/BFS/k-shortest | golden graph |
| W2.3 | Steiner-like | 最小连接下界 | 小图与精确解对照 |
| W2.4 | 分层 evaluator | 六层指标 | 手工算例逐项一致 |
| W2.5 | evidence serializer | 基线证据包 | 每条边可追踪 |

### W3：多源 MVP（E3）

| ID | 工作包 | 产物 | 验收 |
|---|---|---|---|
| W3.1 | 分层候选器 | Top-k candidates | 真值召回/候选规模报告 |
| W3.2 | 对齐模型 | rule/logistic/GBDT | 同 split 比较 |
| W3.3 | edge calibration | calibrated score | Brier/NLL/ECE |
| W3.4 | UCTEG builder | typed graph shards | 图不变量通过 |
| W3.5 | 拒绝和歧义 | abstain/ambiguity sets | 冲突 fixture |

### W4：链闭环（E4）

| ID | 工作包 | 产物 | 验收 |
|---|---|---|---|
| W4.1 | constrained decoder | 最小充分子图 | H3 pilot fixture |
| W4.2 | ATT&CK soft prior | compatibility+unknown | no-prior ablation |
| W4.3 | chain calibration | confidence/risk | risk–coverage |
| W4.4 | evidence package | chain JSON/report | 原始定位符完整 |
| W4.5 | end-to-end CLI | manifest→report | 一条命令、可恢复、幂等 |

### W5：性能和运维（E5）

| ID | 工作包 | 产物 | 验收 |
|---|---|---|---|
| W5.1 | streaming/sharding | 分片图更新 | 顺序/分片等价 |
| W5.2 | candidate pruning | 可配置预算 | 真值边损失透明 |
| W5.3 | optional reduction | 连接点保真归约 | 保留率+缩减率 |
| W5.4 | observability | resource trace | p50/p95/p99、资源曲线 |
| W5.5 | fault recovery | checkpoint/resume | kill/restart 注入 |
| W5.6 | long-run | 稳定性报告 | 无未解释资源增长 |

### W6：工程验收（E6）

- 锁定依赖、环境、配置和 schema；
- 全量单元、property、golden、integration、leakage、performance、fault 测试；
- 新远端环境复现；
- 生成 SBOM/依赖版本、输入/输出哈希；
- 完成运维手册和 Engineering Acceptance Report。

## 4. 测试矩阵

| 测试类 | 关键断言 |
|---|---|
| unit | 每个特征、边类型、评分和约束正确 |
| property | schema round-trip、端口/时间边界、排序确定性 |
| golden | 人工小图的 edge/chain 指标和最优路径一致 |
| leakage | truth/campaign/attack labels 不可进入训练特征 |
| metamorphic | 平移所有时间后结果等价；重命名无语义 ID 后结果等价 |
| calibration | 完美/过度/不足置信 fixture 行为符合预期 |
| robustness | 缺源、偏移、NAT、别名、删边和噪声 |
| integration | adapter→candidate→graph→decoder→report |
| determinism | 同输入、配置、seed 输出哈希一致 |
| performance | events/s、p95/p99、RAM/VRAM/磁盘 |
| fault | OOM、磁盘满、文件损坏、进程中断、checkpoint 恢复 |
| storage | 本地禁存数据/权重/结果/凭据 |

## 5. 依赖顺序

```text
W0
 └─ W1
     └─ W2
         └─ W3
             └─ W4
                 ├─ W5
                 └─ 论文 P0 数据审计准备
W5 + 全量回归
 └─ W6
     └─ 论文 P0 正式启动
```

## 6. 优先级

### P0：立即

- manifest/schema v2；
- strong-truth 最小 3 runs；
- oracle/硬对齐/evaluator；
- candidate recall audit；
- UCTEG typed edges；
- 最小 evidence package。

### P1：核心方法通过后

- calibrated alignment；
- constrained decoder；
- ATT&CK soft prior；
- risk–coverage；
- LANL 长时间协议；
- 强基线复现。

### P2：论文 P4 前

- 未见攻击族；
- mimicry/定向日志删除；
- QoA/分析员负担；
- 外部公开多源验证。

### P3：H1—H4 通过后

- 181GB 优化；
- provenance reduction；
- 图数据库交互层；
- 学习式解码器。

## 7. Engineering Acceptance Report 最低目录

1. 版本和范围；
2. 代码/配置/环境/数据哈希；
3. 测试结果和未运行项；
4. 数据适配覆盖和质量；
5. 端到端场景；
6. 性能和稳定性；
7. 故障恢复；
8. 安全/凭据/本地存储审计；
9. 已知限制；
10. accepted/failed 决策。
