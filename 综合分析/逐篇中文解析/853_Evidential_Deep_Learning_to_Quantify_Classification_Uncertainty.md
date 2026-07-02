# [853] Evidential Deep Learning to Quantify Classification Uncertainty

## 1. 基本信息

- **原始题名**：Evidential Deep Learning to Quantify Classification Uncertainty
- **中文释义**：用于分类不确定性量化的证据深度学习
- **年份**：2018
- **DOI**：10.48550/arXiv.1806.01768
- **来源**：Advances in Neural Information Processing Systems
- **PDF**：`paper/10.48550_arXiv.1806.01768.pdf`
- **相关性**：中相关

## 2. 核心内容

本文提出 evidential deep learning，将分类输出从单点 softmax 概率提升为 Dirichlet 分布参数。网络输出非负 evidence，由 evidence 得到 Dirichlet 参数、类别 belief 和整体 uncertainty。样本证据不足时，模型应输出更高不确定性。

## 3. 对本项目的价值

这是 Evidence-OpenEMTD 的理论根论文。项目中的“模态 evidence / belief / uncertainty”“证据不足触发 Unknown 风险”“Dirichlet evidence loss”都可以用本文作为基础依据。

## 4. 可引用位置

1. 方法章节：模态证据意见生成。
2. 损失函数：evidential loss 与 KL 正则。
3. 相关工作：证据深度学习和可信检测。

## 5. 局限性

原论文主要在通用分类和 OOD 场景验证，没有处理网络流量中的多模态冲突、协议字段缺失和低质量标签。因此本项目的创新应体现在多模态证据融合和开放集流量检测场景化。
