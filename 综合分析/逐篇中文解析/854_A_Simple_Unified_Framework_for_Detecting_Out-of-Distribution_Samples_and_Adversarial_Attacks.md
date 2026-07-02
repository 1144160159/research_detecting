# [854] A Simple Unified Framework for Detecting Out-of-Distribution Samples and Adversarial Attacks

## 1. 基本信息

- **原始题名**：A Simple Unified Framework for Detecting Out-of-Distribution Samples and Adversarial Attacks
- **中文释义**：用于检测分布外样本和对抗样本的统一框架
- **年份**：2018
- **DOI**：10.48550/arXiv.1807.03888
- **来源**：Advances in Neural Information Processing Systems
- **PDF**：`paper/10.48550_arXiv.1807.03888.pdf`
- **相关性**：中相关

## 2. 核心内容

本文提出基于 Mahalanobis 距离的 OOD 检测方法。它在深度特征空间中为每个已知类别估计类条件高斯分布，并用样本到最近类分布的 Mahalanobis 距离作为异常或分布外分数。

## 3. 对本项目的价值

本项目中的“类原型距离”“已知类紧凑空间”“远离所有已知原型触发 Unknown 风险”都可以由本文支撑。它也可作为距离式 OOD 检测基线。

## 4. 可引用位置

1. 方法章节：原型距离 / Mahalanobis 风险。
2. 实验基线：Mahalanobis OOD detector。
3. 讨论：距离式方法在噪声标签下会受已知类原型污染影响。

## 5. 局限性

该方法通常假设已知类特征空间相对干净且类条件分布可估计。真实园区流量存在低质量标签和未知污染，因此需要先做样本净化或联合 evidence 风险。
