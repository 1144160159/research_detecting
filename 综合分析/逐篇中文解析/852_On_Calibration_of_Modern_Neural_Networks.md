# [852] On Calibration of Modern Neural Networks

## 1. 基本信息

- **原始题名**：On Calibration of Modern Neural Networks
- **中文释义**：现代神经网络的置信度校准
- **年份**：2017
- **DOI**：10.48550/arXiv.1706.04599
- **来源**：Proceedings of the 34th International Conference on Machine Learning
- **PDF**：`paper/10.48550_arXiv.1706.04599.pdf`
- **相关性**：中相关

## 2. 核心内容

本文系统讨论深度神经网络的置信度校准问题，指出现代网络虽然准确率高，但预测概率常常过度自信。论文提出并评估温度缩放等校准方法，并使用 ECE 等指标衡量预测置信度与真实正确率之间的一致性。

## 3. 对本项目的价值

可信开放集检测不能只报告 F1 或 AUROC，还需要说明模型输出的风险分数是否可信。本文可支撑初稿中的 ECE、Brier Score、温度缩放、risk-coverage 等校准指标。

## 4. 可引用位置

1. 实验指标：ECE、NLL、Brier Score。
2. 方法模块：不确定性校准和阈值校准。
3. 讨论：开放集阈值跨场景迁移时需要校准。

## 5. 局限性

校准本身不能发现未知攻击，它只能改善置信度解释。因此在本项目中应与 evidence、原型距离和能量分数联合使用。
