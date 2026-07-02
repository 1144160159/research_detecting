# [855] Energy-Based Out-of-Distribution Detection

## 1. 基本信息

- **原始题名**：Energy-Based Out-of-Distribution Detection
- **中文释义**：基于能量的分布外检测
- **年份**：2020
- **DOI**：10.48550/arXiv.2010.03759
- **来源**：Advances in Neural Information Processing Systems
- **PDF**：`paper/10.48550_arXiv.2010.03759.pdf`
- **相关性**：中相关

## 2. 核心内容

本文提出用能量分数替代最大 softmax 置信度进行 OOD 检测。能量分数由 logits 计算，理论上比 softmax 置信度更贴近输入概率密度，也更不容易受到未知样本高置信误判问题影响。

## 3. 对本项目的价值

Evidence-OpenEMTD 中的 Unknown 风险建议联合 uncertainty、conflict、prototype distance 和 energy score。本文可支撑能量分数作为开放集风险信号。

## 4. 可引用位置

1. 方法章节：能量异常分数。
2. 实验基线：Energy OOD。
3. 消融实验：去掉 energy score 后 Unknown 检测是否下降。

## 5. 局限性

单独使用能量分数仍无法解释多模态证据冲突，也无法处理训练集中的开集污染。因此本项目应将其作为多信号 Unknown 风险的一部分。
