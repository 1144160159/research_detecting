# UCTEG 与最小充分证据子图技术规格

- 版本：`Method Spec v1.1-deep-read`
- 日期：2026-07-29
- 对应假设：H1、H3、H4

## 1. 设计原则

1. 观测、候选、预测、真值四层隔离。
2. 先保证候选真值边召回，再优化边精度。
3. 跨源边默认不可信，必须携带支持、冲突和歧义。
4. ATT&CK 是软语义，不是硬真值。
5. 证据不足可以拒绝，不能用图补全制造确定性。
6. 简单、可审计方法优先；复杂模型必须通过独立消融证明必要性。
7. 跨主机边至少需要认证/登录会话与网络活动两类证据；单一相关信号只能形成候选。
8. 传感器不健康是外部事实边界，不能由图补全改写为“已恢复”。

## 2. 核心对象

### 2.1 统一事件

```text
Event {
  event_id, source_id, modality, event_type,
  host_id, actor_id, action, object_id,
  process_guid, parent_guid, user_id, session_id,
  src_ip, src_port, dst_ip, dst_port, protocol,
  ts_start_ns, ts_end_ns, ts_uncertainty_ns,
  sensor_health, raw_ref, attributes
}
```

`campaign_id`、攻击标签、ATT&CK technique、人工链 ID 只能存在于 evaluation-only truth 对象。

### 2.2 候选对齐边

```text
AlignmentCandidate {
  left_event_id, right_event_id, relation_type,
  candidate_generator, score_raw, probability_calibrated,
  feature_components, ambiguity_set_id,
  rank, accepted, rejection_reason, model_version
}
```

### 2.3 图边类型

| 边类型 | 来源 | 是否可视为事实 | 是否参与推断 | 是否对模型可见 |
|---|---|---:|---:|---:|
| `prov_fact` | 原生 provenance | 是 | 是 | 是 |
| `session_fact` | 认证/会话记录 | 有条件 | 是 | 是 |
| `flow_fact` | 原生 flow | 是，但不自动指向进程 | 是 | 是 |
| `align_candidate` | 跨源对齐器 | 否 | 是 | 是 |
| `lateral_candidate` | 网络+认证候选 | 否 | 是 | 是 |
| `ttp_soft` | 语义模型/规则 | 否 | 是 | 是 |
| `chain_prediction` | 解码器 | 否 | 输出 | 否，禁止回灌 |
| `truth_edge` | 标注/编排器 | 仅评测事实 | 否 | 否 |

`lateral_candidate` 的最低支持向量为：

```text
{auth_or_logon_session, src_host_candidate, dst_host_candidate,
 network_flow_candidate, credential_context, sensor_health}
```

缺少 logon GUID/session ID 或存在共享凭据时，必须保留多个竞争候选，不允许仅按用户名或 IP 唯一化。

## 3. 候选生成

### 3.1 分桶

候选先按以下键分桶，避免二次复杂度：

- 时间分桶：按传感器残差和事件类型使用不同窗口；
- 主机分桶：host ID、IP、hostname、agent ID 及别名集合；
- 会话分桶：user、logon/session、ticket、认证目标；
- 网络分桶：正反向五元组、连接持续时间和方向；
- 进程分桶：process GUID/PID、image、parent、command-line 摘要。

### 3.2 候选层硬门

- 候选真值边 Recall@k 是主门；
- 报告每个事件平均候选数、p95 候选数和候选爆炸率；
- 报告因裁剪丢失的真值边；
- 禁止使用 truth/campaign/attack filename 参与分桶；
- 若候选召回未达到冻结门，不进入概率模型比较。

## 4. 对齐特征与评分

### 4.1 特征组

| 组 | 典型特征 | 主要失败模式 |
|---|---|---|
| 时间 | 残差、区间重叠、开始/结束差、采集延迟 | 时钟漂移、批处理日志 |
| 主机 | host、IP、hostname、agent、资产别名 | DHCP、NAT、代理 |
| 身份 | user、session、logon、ticket | 共享账号、凭据盗用 |
| 进程 | GUID、PID、parent、image、command | PID 复用、日志缺字段 |
| 网络 | 正反五元组、方向、bytes、packets | NAT、复用连接、缺包 |
| 语义 | action/event type、DNS/SNI、对象类型 | 解析器漂移、加密 |
| 上下文 | 一到两跳邻域、前后事件兼容度 | 依赖爆炸 |
| 可靠性 | sensor health、缺失模式、时钟质量 | 传感器失效/篡改 |

### 4.2 模型晋级顺序

1. 加权规则；
2. 逻辑回归；
3. GBDT/随机森林类可解释树模型；
4. 必要时才使用小型跨源图编码器。

每次晋级必须在同一候选集、相同 split 和相同校准方法上比较。复杂模型只有同时改善 H1 主指标和校准/错误类型才保留。

### 4.3 拒绝规则

拒绝原因至少包括：

- `below_threshold`；
- `ambiguous_margin`；
- `conflicting_identity`；
- `temporal_infeasible`；
- `sensor_unhealthy`；
- `candidate_budget_exceeded`；
- `out_of_support`。

## 5. UCTEG 图构建

### 5.1 图不变量

1. 每个节点都有 `raw_ref` 或明确标记为派生节点。
2. 每条边有类型、来源和版本。
3. `truth_edge` 对训练/推断不可见。
4. `chain_prediction` 不允许作为下一次输入事实。
5. 跨源候选边必须有概率或可解释分数。
6. 时间逆序边必须记录理由，不能静默修正。
7. 一个派生视图不得计为新的独立传感器支持。
8. 每条跨主机预测边必须能回溯到认证/会话和 flow 候选；若其中一类缺失，状态只能是 `incomplete`。

### 5.2 图存储

首版使用可重放的分片事件/边表和轻量索引；图数据库只作为交互查询层，不作为唯一事实源。每个图分片记录 schema 版本、数据 manifest、构建配置和 SHA-256。

## 6. 最小充分证据子图

### 6.1 输入

- 异常种子或人工 POI；
- UCTEG 局部候选图；
- 证据预算；
- 时间/会话/跨主机约束；
- ATT&CK 软兼容矩阵；
- 允许的拒绝和 `unknown` 状态。

### 6.2 目标

```text
maximize:
  seed coverage
  + key-step coverage
  + independent-source support
  + temporal/causal feasibility
  + soft stage compatibility
  - uncertain alignment cost
  - unsupported cross-host bridge
  - redundancy
  - temporal/session violation
```

“充分”必须由预注册的关键步骤覆盖、连接性和证据支持定义；“最小”通过节点/边数、原始事件数和分析员检查负担定义。不能只用图尺寸小证明质量。

### 6.3 解码器层级

| 层级 | 方法 | 作用 |
|---|---|---|
| B0 | 时间 BFS、反向/正向追踪 | 依赖扩张下界 |
| B1 | k-shortest/beam search | 可解释路径下界 |
| B2 | Steiner/NODLINK-like | 最小连接基线 |
| M1 | 受约束 beam/arborescence | 主方法首版 |
| M2 | 小图整数规划 | 验证 M1 近似质量 |
| M3 | 学习式解码 | 仅在 M1/M2 无法支持 H3 时评估 |

### 6.4 多分支和未知步骤

允许一个 campaign 有多个分支；允许中间步骤缺失。`unknown` 节点只表示“证据缺口”，不得生成不存在的事件。缺口两端保留未支持桥接惩罚和置信下降。

## 7. 校准与链置信

边概率和链置信分开校准：

- edge calibration：Brier、NLL、ECE；
- chain calibration：按“整链满足预注册正确标准”的二元结果校准；
- risk–coverage：逐步提高拒绝率，观察错误风险；
- 高置信错误单独列出，不被均值隐藏。

## 8. 证据包接口

```json
{
  "chain_id": "predicted-chain-id",
  "status": "complete|incomplete|abstain",
  "confidence": 0.0,
  "nodes": [],
  "edges": [],
  "alternative_hypotheses": [],
  "rejected_candidates": [],
  "metric_context": {},
  "run_id": "",
  "code_commit": "",
  "config_hash": "",
  "data_manifest_hash": ""
}
```

本地只允许保存 schema、空模板和聚合指标；含原始事件或完整链的证据包只保存在远端。

## 9. 必做消融

1. 无时间不确定区间；
2. 无身份/会话特征；
3. 无网络统计；
4. 无上下文特征；
5. 硬连接替代概率候选；
6. 无校准；
7. 无拒绝；
8. 无最小证据惩罚；
9. 无 ATT&CK 软先验；
10. 无 `unknown`；
11. 无跨源支持项；
12. 不同异常种子。

## 10. 技术停止条件

- 候选层真值召回不足：先修候选器，不训练更复杂模型；
- H1 不成立：主方法转对齐失败边界；
- H3 不成立：保留对齐贡献，删除最小子图创新；
- 校准不改善风险：只报告分数，不宣称概率或可信拒绝；
- 关键证据在归约后丢失：禁用效率层；
- 学习式方法与简单方法无显著差异：保留简单方法。
