# FHMM 同拆分三初始化集成 Botnet 试点

## 1. 目的与协议

本试点用于判断 FHMM-CAEOS 的跨初始化不稳定性是否可由固定三成员集成缓解。实验在远端 A6000 上完成，数据拆分种子与模型初始化种子分离：

- split37：model101、model103、model107；
- split41：model109、model113、model127；
- 攻击概率与 open score 分别取三成员算术均值；
- 类型预测取三成员硬多数票，三方平票时取最小类别编号；
- 告警阈值只由 known-only validation 的良性样本按 `0.049` 预算校准；
- open 阈值只由 known-only validation 的已知攻击样本按 `0.04` 预算校准；
- 两个拆分均通过预注册门后才允许扩展到七个未知家族。

协议在训练前冻结。`protocol.json` 的 manifest SHA-256 为
`be5572532f69fe7ffc1c151e70dc2631854e55d311271ac2be9f37941c3024df`。

## 2. 操作验收表

| 拆分 | Alert Acc | Benign FPR | Known type Acc | Unknown alert Recall | Unknown rejection Recall |
|---|---:|---:|---:|---:|---:|
| 37 | 0.866180 | 0.047955 | 0.943098 | 0.417073 | 0.019512 |
| 41 | 0.898967 | 0.060649 | 0.954805 | 0.575610 | 0.052033 |
| 双拆分均值 | 0.882573 | 0.054302 | 0.948952 | 0.496341 | 0.035772 |

两个拆分均未通过预注册效果门，因此不得扩展到七个未知家族，也不得将该简单均值集成替换为当前自有算法。

## 3. 开放集研究表

| 拆分 | Known Macro-F1 | Balanced Acc | Unknown AUROC | Unknown AUPR-Out | FPR_known@95TPR_unknown | OSCR |
|---|---:|---:|---:|---:|---:|---:|
| 37 | 0.936941 | 0.953150 | 0.774353 | 0.378736 | 0.436330 | 0.773322 |
| 41 | 0.942403 | 0.956607 | 0.799018 | 0.419356 | 0.476951 | 0.797686 |
| 双拆分均值 | 0.939672 | 0.954879 | 0.786685 | 0.399046 | 0.456641 | 0.785504 |

结果直接支持“已知识别与未知拒识不能混为一个任务”：已知 Balanced Accuracy 已超过 `0.95`，但 Unknown AUROC 仅为 `0.787`，FPR95-Out 高达 `0.457`。

## 4. 完整性与资源

- 六个成员的 CUDA 与资源审计全部通过；
- 成员平均 GPU 利用率均值为 `81.76%`，范围为 `68.91%–86.72%`，峰值均为 `100%`；
- 每个成员的 PyTorch 峰值预留显存约 `17.45–17.51 GiB`；
- `split37_model103` 在第 76–78 轮出现 `training_loss`、`validation_loss` 与 `meta_outer_loss` 为 NaN，其余五个成员无非有限损失；
- 因此 completion 的资源门为真、效果门为假、完整性门为假。

成员间 test attack probability Pearson 为 `0.9988–0.9999`，类型预测一致率为 `0.9858–0.9991`；但 test open score Pearson 仅为 `0.0152–0.4931`。简单平均主要稀释了开放集风险排序，并未形成有用的成员互补。

## 5. 文件说明

- `protocol.json`：训练前冻结协议；
- `completion.json`：远端双拆分完整性、资源与效果总门；
- `evaluation_split37.json`、`evaluation_split41.json`：固定集成评估；
- `member_evaluation_*.json`：六个成员的只读事后指标补算，不用于挑选权重或阈值；
- `resource_audit_*.json`：六个成员的 GPU 利用率和显存审计；
- `members/*/metrics.json`、`gpu_execution.json`：成员训练与 CUDA 原始证据；
- `local_summary.json`：本地只读聚合，manifest SHA-256 为
  `f3f8db881ebcb2a464c0a0a1adbf48efcda24ef2d32308a511f6f8b0e084fbbb`。

## 6. 决策

不采纳“固定三初始化算术均值”作为下一版自有算法。下一轮只允许在新协议中处理三项问题：

1. 将二阶 meta 更新置于 FP32，并增加每步非有限损失 fail-fast，不能继续使用产生 NaN 后仍回滚到旧 checkpoint 的训练结果；
2. 优先建立 capture/session-grouped 拆分，当前 flow_id 哈希拆分只保留为开发证据；
3. 使用 known-only validation 预注册的稳健 open-score 聚合或单模型选择规则，必须在未知测试揭盲前冻结，禁止按当前 Botnet 测试结果挑成员或权重。

