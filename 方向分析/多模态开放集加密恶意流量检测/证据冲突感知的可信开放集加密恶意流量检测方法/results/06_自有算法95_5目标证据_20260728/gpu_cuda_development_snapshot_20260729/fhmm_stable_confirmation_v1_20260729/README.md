# FHMM-SR-CAEOS 双新拆分确认

日期：2026-07-29

## 1. 协议与边界

本轮用于确认开发拆分 37/41 上选出的固定 FHMM 稳定化候选能否迁移到未运行的
split43/47。协议在训练前冻结，随后才在远端 A6000 上训练：

- split43：model131、137、139；
- split47：model149、151、157；
- 每个拆分内三个成员并行，两个拆分顺序执行；
- 训练采用 FP32 一阶 family-held-out meta update，非有限损失 fail-fast；
- 攻击分数固定为 family score 的三成员 maximum；
- open score 固定为三成员 maximum；
- 类型固定选择 known-only validation Macro-F1 最优成员；
- alert/open 预算均为 `0.04`，阈值仅由 known-only validation 校准；
- 确认阶段不搜索候选、权重、风险公式或阈值预算。

协议文件 SHA-256 为
`fdd6a4cdfad3883b386e0253ce451672c6436e452a80a23f96c80630a740d086`，
内部 manifest 为
`c07f53695679f6d7477cc2471bc08f9c2c4d6714635218893c6855356ae76ad8`。
开发配置曾使用旧拆分的真实 Botnet 标签排序，因此本轮即使通过，也只能证明固定候选的
fresh-split 迁移，不能替代未知家族完全未见的七场景正式证据。

## 2. 操作验收

| 拆分 | Alert Acc | Benign FPR | Known type Acc | Unknown alert Recall | Unknown rejection Recall |
|---|---:|---:|---:|---:|---:|
| 43 | 0.990378 | 0.032440 | 0.954261 | 0.974797 | 0.491057 |
| 47 | 0.901818 | 0.038082 | 0.950449 | 0.573984 | 0.382114 |
| 均值 | 0.946098 | 0.035261 | 0.952355 | 0.774390 | 0.436585 |

split43 通过用户 95%/5% 门、确认主门和机器字段
`full_typed_known_unknown_95_5`；split47 三门均失败。该历史字段只检查告警、FPR、
Known type 和 Unknown alert，不检查 Unknown rejection 95%，因此不得写成完整未知拒识
目标已达成；split43 的 Unknown rejection Recall 实际仅为 `0.491057`。
联合确认要求两个拆分逐一通过，因此 `expand_to_seven_unknown_families=false`。
不能用均值 FPR 和 Known type 达标抵消 split47 的 Alert Accuracy 与 Unknown alert
Recall 失败。

## 3. 开放集研究指标

| 拆分 | Known Macro-F1 | Balanced Acc | Unknown AUROC | AUPR-Out | FPR_known@95TPR_unknown | OSCR |
|---|---:|---:|---:|---:|---:|---:|
| 43 | 0.957952 | 0.966933 | 0.952772 | 0.777189 | 0.080100 | 0.950354 |
| 47 | 0.965516 | 0.968207 | 0.886194 | 0.660436 | 0.377910 | 0.883679 |
| 均值 | 0.961734 | 0.967570 | 0.919483 | 0.718812 | 0.229005 | 0.917016 |

split47 的已知分类、AUROC 和 OSCR 均达到本轮下限，但操作告警仍失败。这是项目内
“已知识别、未知风险排序、部署阈值决策必须分层报告”的直接证据。失败集中在攻击先验
分数对未知 Botnet 的跨拆分覆盖，而不是良性误报或已知家族分类。

## 4. 完整性与 GPU

- 六个任务的参数、数据集 SHA、训练器 SHA、有限损失历史和 CUDA 身份全部通过；
- 六个资源审计全部通过，成员平均 GPU 利用率范围为 `69.28%–85.91%`，
  六成员均值为 `79.86%`，峰值均为 `99%` 或 `100%`；
- 各成员 PyTorch 峰值预留显存约 `17.36–17.48 GiB`；
- AMP 动态缩放共记录每成员 3–5 次 scale reduction，未产生非有限训练历史；
- completion manifest 为
  `c7b5fe133d8b2cdf0542eef1ccac1cef00068af760a3a6c28886d8bf605d7649`。

## 5. 决策

不扩展到七个未知家族，不将 FHMM-SR-CAEOS v1 写成达到 95%/5% 的正式自有算法。
下一版只处理攻击告警跨拆分稳定性：

1. attack source/routing 只能由嵌套 leave-one-known-family validation 的最坏家族召回
   选择，不再使用目标 Botnet 标签；
2. 显式解耦 binary maliciousness 与 known-family type，避免以 family maximum 代替
   对未知攻击的恶意性判断；
3. 新版本在开发门通过后使用全新拆分冻结确认，不能复用 split43/47 做确认；
4. 只有新确认逐拆分通过，才进入七家族、至少五种子的正式比较与层级统计。

## 6. 文件

- `remote_results/protocol.json`：训练前冻结协议；
- `remote_results/evaluation.json`：固定配置的双拆分评价；
- `remote_results/completion.json`：完整性、资源、效果和扩展总门；
- `remote_results/resource_audit_*.json`：六成员 GPU 资源审计；
- `members/*/metrics.json`、`gpu_execution.json`：成员训练与 CUDA 原始证据；
- 分数 NPZ 与模型只保留在远端 run 目录，本地不复制。
