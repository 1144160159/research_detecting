# [851] Towards Open Set Deep Networks

## 1. 基本信息

- **原始题名**：Towards Open Set Deep Networks
- **中文释义**：面向开放集识别的深度网络
- **年份**：2016
- **DOI**：10.1109/CVPR.2016.173
- **来源**：2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)
- **PDF**：`paper/10.1109_CVPR.2016.173.pdf`
- **相关性**：中相关

## 2. 核心内容

本文提出 OpenMax，是深度开放集识别的经典起点。它指出普通深度网络的闭集 softmax 会强制把未知样本归入已知类别，从而产生高置信误判。OpenMax 通过对深度特征的激活向量进行 Weibull 分布拟合，估计样本偏离已知类中心的程度，并引入 unknown 概率。

## 3. 对本项目的价值

本项目做可信开放集加密恶意流量检测时，必须说明为什么不能只用 softmax 阈值。OpenMax 可作为“开放集深度网络”基础文献，用来支撑 Unknown 拒识问题定义和传统开放集基线。

## 4. 可引用位置

1. 相关工作：开放集/OOD 与未知攻击检测。
2. 实验基线：OpenMax 类方法。
3. 方法动机：闭集 softmax 容易对未知样本过度自信。

## 5. 局限性

OpenMax 主要来自视觉分类，直接迁移到加密流量时无法处理多模态证据冲突、低质量标签和流量漂移。因此它更适合作为基础基线，而不是最终方案。
