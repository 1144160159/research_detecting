# 算法候选最优性链独立重算与 fail-closed 修复

## 问题

原 `algorithm_search_rc1.json` 虽声明已探索 10 个候选、严格 Pareto 前沿为
`A09/A10`、实际前沿及选择为 `A09`，但发布审计只检查声明之间是否相互一致，
没有从候选原始指标重算前沿。A01--A10 的证据也没有逐项冻结 SHA-256，A01--A08
没有本地可重算的 normal/fallback 指标。因此旧记录不足以证明 A09 是 10 个候选中的
全局最优，更不能把离线质量最优提升为生产联合 Pareto 最优。

## 修改

- 搜索预算明确为最少 8、计划最多 12、硬上限 12、实际探索 10；候选数量和参数
  组合均由审计器重算，重复组合、超上限或少探索均拒绝。
- 冻结算法质量硬门：normal/fallback 成对，决赛候选每种模式至少 3 次；按两种模式
  的最坏值重算 Macro-F1、攻击/良性召回、AUPRC、ECE、事件召回、关键流覆盖、
  预算超限和预算上限。
- 明确离线资源预算只有 `batch_size=512`、每批 5000 us 和 0.5 安全比例。由于
  十个算法候选没有在同一运行合同下测量吞吐、丢包、端到端 P99、CPU/GPU/内存、
  关键流覆盖和回退，所以生产联合最优固定为 false。
- 新增独立 `algorithm_optimality.py` 和 CLI，不信任配置内的前沿/冠军字段；先过硬门，
  再重算严格 Pareto 和 epsilon=0.03 的 practical Pareto。缺路径、物理换行、证据
  哈希、成对指标、重复或资源合同均 fail-closed。
- CLI 严格按无 BOM UTF-8 读取并拒绝 JSON 重复键；本地只保留小型机器可读指标，
  不复制数据、模型或大型实验结果。

## 当前可证明结论

2026-08-13 从 GPU 节点只读取得 A09/A10 确认性摘要并重算：

| 候选 | Macro-F1 min | attack recall min | benign recall min | AUPRC min | ECE max |
|---|---:|---:|---:|---:|---:|
| A09 | 0.730858 | 0.764706 | 0.945051 | 0.522967 | 0.038355 |
| A10 | 0.738846 | 0.729412 | 0.945830 | 0.477949 | 0.041792 |

两者互不严格支配，严格前沿是 `A09/A10`。在不允许任一目标恶化超过 0.03、且至少
一个目标改善超过 0.03 的冻结规则下，A09 相比 A10 在攻击召回和 AUPRC 的改善超过
0.03，其他指标恶化不超过 0.03，因此决赛 practical winner 为 A09。

这只证明“有指标的 A09/A10 决赛比较”成立。A01--A08 尚无本地成对指标，十份远端
摘要也尚未全部取得和冻结 SHA-256；因此 `algorithm_only_practical_optimum_proven=false`。
此外当前物理抓包分支没有达到生产门，`production_joint_optimum_proven=false`、
`final_pareto_ingestion_allowed=false`。

## 验证和负测

`tests/test_algorithm_optimality.py` 覆盖：完整搜索正例、当前配置的精确 fail-closed、
伪造前沿/冠军、缺哈希、重复不足、篡改聚合指标、证据路径物理换行、重复 JSON key
和非法 UTF-8。发布配置、runtime decision、unified audit 和 production Pareto 均未修改。

## 剩余远端实验

1. 在 GPU SSH 恢复稳定后只读遍历 A01--A10 的十个现有证据文件，冻结实际 SHA-256、
   schema、normal/fallback 重复数、输入 manifest 哈希及最坏指标。
2. 若 A01--A08 的旧 screening 单文件不是成对三重复摘要，不能靠补元数据伪造证据；
   必须用相同确认性 groups、输入 manifest、batch/预算和三重复合同重跑十个候选。
3. 十个候选完整后执行本审计器；只有重算 practical front 唯一为 A09 才能声明
   “10 候选范围内的算法质量 practical 最优”。生产联合最优仍须另行通过同负载下
   的 XDP 优先/DPDK 回退、丢包、P99、资源、关键流和回退联合实验。

