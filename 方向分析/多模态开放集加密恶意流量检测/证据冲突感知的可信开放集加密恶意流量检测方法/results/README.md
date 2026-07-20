# 实验结果索引

本目录只保存论文写作和结果复核所需的轻量摘要、指标文件与审计记录。模型权重、逐样本预测和大规模中间文件保留在 GPU 服务器，不在本地重复存储。

| 目录 | 内容 | 对应研究问题 |
|---|---|---|
| [01_基础与闭集验证](01_基础与闭集验证) | 冒烟测试、收敛检查、MC7 多分类与完整数据结果 | 已知恶意类别能否稳定识别 |
| [02_开放集验证](02_开放集验证) | Mal_TLS、DoH 的留一未知类、支持风险和指纹分组结果 | 未知类别能否在无泄漏条件下拒识 |
| [03_模态污染鲁棒性](03_模态污染鲁棒性) | 模态缺失、置乱、污染与冲突折扣消融 | 冲突建模能否抵抗证据质量变化 |
| [04_跨数据集验证](04_跨数据集验证) | HIKARI、DoH、Mal_TLS 的跨数据集与分组审计 | 方法是否具有跨场景稳定性 |
| [05_层级门控确认](05_层级门控确认) | 支持/冲突路径选择及嵌套无泄漏确认 | 不用真实未知标签能否选择风险路径 |

## strict-v4 证据位置

strict-v4 的轻量 JSON/Markdown 镜像位于 `F:/泉城实验室/二期/论文/异常检测/source/CAEOS-EMTD/results`。当前最关键的入口为：

- `strict_v4_mandatory_scores_full102_seed7/summary.json`：28 方法 seed7 完整开发屏幕。
- `strict_v4_running_confirmation_health/health.json`：不读取中间测试指标的三矩阵运行完整性快照；v2 分别审计 Router CAEOS、Router MLP/OpenMax 和 Tail-aware 的产物、协议、拆分指纹与无泄漏标记。
- `strict_v4_risk_coverage_seed7/analysis.json`：选择性风险与固定工作点。
- `strict_v4_component_ablation_seed7/ablation.json`：102 场景核心机制消融。
- `strict_v4_external_training_pilot_seed7/`：CLOSR/CADE/Sieve 独立训练强基线终态镜像；`42/42`、零失败、无泄漏，三者均未过 full102 扩展门。
- `strict_v4_complementary_training_pilot_seed7/`：ARPL/PALM/RoNeTC/FOSS 互补训练试点终态；`56/56`、零失败，四者均未过冻结扩展门。
- `strict_v4_complementary_training_full102_seed7/not_required`：互补组无人过门，完整 102 场景扩展按协议免除。
- `strict_v4_attention_fusion_seed7/`：F3 熵条件可学习注意力的 102 场景完整负基线及协议绑定结果。
- `strict_v4_fusion_operators_seed7/`：F2/F3/F4/F5/F6/F9 在同一 102 场景冻结证据上的完整融合算子对照；v1 口径漂移已归档，v2 为权威结果。
- `strict_v4_aegis_training_pilot_seed7/`：AEGIS clean-label/1D-ResNet 试点终态；`14/14`、零失败，平均领先 OpenDetect 但未过套件稳健性门。
- `strict_v4_aegis_training_full102_seed7/not_required`：AEGIS 未过冻结扩展门，完整 102 场景扩展按协议免除。
- `strict_v4_comprehensive_sota_audit/`：综合 SOTA 审计 v9；三组训练强基线、正/负扩展义务和 F2-F9 融合矩阵交叉一致性均为硬门，只有完整 PASS 后才允许升级论文声明。
- `strict_v4_final_efficiency_readiness_seed7/readiness.json`：冻结效率协议 v1 的可执行性审计；Pairwise 候选可加载模型覆盖为 `0/102`，OpenDetect 为 `102/102`，因此禁止直接效率比较并要求最终选模后冻结 v2。
- `strict_v4_{complementary,aegis}_training_full102_seed7/`：仅在对应试点过门时生成，保存零结果冻结协议、102 场景完整汇总和扩展完成证据。
- `01_基础与闭集验证/mal_tls_xgboost_multiseed/`：XGBoost 2.1.4 五种子闭集基线的冻结协议、完成汇总和完成态完整性审计；逐种子模型与原始运行仍只在 GPU 端。
- `source/CAEOS-EMTD/results/strict_v4_conflict_metrics_seed7/`：D1-D7 七类冲突度量的 102 场景分析、BH-FDR、多种比较校正和配对稳健性审计。

完整逐样本分数、模型、证据包和确认矩阵只位于 GPU 项目 `/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717/{caches,runs,results}`；原始数据位于 `/opt/data/private/wangwt/ParkAttackKE/datasets`。

## 使用原则

1. 论文主表优先引用 `03_实验报告` 中已经核对的汇总，不直接从单次运行推导结论。
2. `results` 用于证据追溯，不作为新的实验入口；可执行代码和配置统一位于 `source/CAEOS-EMTD`。
3. 新结果先进入对应分类目录，再更新实验报告和 `05_过程记录/实验迭代记录.md`，禁止恢复顶层平铺。
4. 文件名中的日期或实验编号保持不变，以便与 GPU 端运行目录和历史日志对应。
