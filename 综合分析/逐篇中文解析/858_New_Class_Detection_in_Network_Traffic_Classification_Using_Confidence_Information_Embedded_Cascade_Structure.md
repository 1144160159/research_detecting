# [858] New Class Detection in Network Traffic Classification Using Confidence Information Embedded Cascade Structure

## 1. 基本信息

- **原始题名**：New Class Detection in Network Traffic Classification Using Confidence Information Embedded Cascade Structure
- **中文释义**：基于置信信息嵌入级联结构的网络流量新类检测
- **年份**：2025
- **DOI**：10.1109/TNSE.2025.3538564
- **来源**：IEEE Transactions on Network Science and Engineering
- **PDF**：`paper/10.1109_TNSE.2025.3538564.pdf`
- **相关性**：强相关

## 2. 核心内容

本文面向网络流量分类中新应用和新类别不断出现的问题，提出置信信息嵌入的级联结构，在保持已知类细粒度分类能力的同时提升新类检测能力。论文强调开放集环境下 known classification 与 new class detection 的平衡。

## 3. 对本项目的价值

该论文可支撑 Evidence-OpenEMTD 中“低可信已知类进入复核队列”和“风险分层输出”的设计。它也可作为开放集网络流量新类检测的最新对照。

## 4. 可引用位置

1. 相关工作：网络流量新类检测。
2. 方法设计：级联式风险分层。
3. 实验基线：confidence/cascade 类开放集检测方法。

## 5. 局限性

级联置信结构主要处理网络流量新类检测，不一定显式处理多模态证据冲突、加密协议字段缺失和标签污染。项目创新仍应落在可信 evidence 融合。
