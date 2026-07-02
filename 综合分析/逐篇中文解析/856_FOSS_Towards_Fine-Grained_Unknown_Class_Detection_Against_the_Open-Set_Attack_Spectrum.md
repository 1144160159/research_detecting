# [856] FOSS: Towards Fine-Grained Unknown Class Detection Against the Open-Set Attack Spectrum With Variable Legitimate Traffic

## 1. 基本信息

- **原始题名**：FOSS: Towards Fine-Grained Unknown Class Detection Against the Open-Set Attack Spectrum With Variable Legitimate Traffic
- **中文释义**：面向开放集攻击谱和动态合法流量的细粒度未知类检测
- **年份**：2024
- **DOI**：10.1109/TNET.2024.3413789
- **来源**：IEEE/ACM Transactions on Networking
- **PDF**：`paper/10.1109_TNET.2024.3413789.pdf`
- **相关性**：强相关

## 2. 核心内容

FOSS 面向异常型 NIDS 的真实部署痛点：未知攻击类别不断出现，合法流量也会变化。论文强调 fine-grained unknown class detection 和 variable legitimate traffic adaptation，不把未知攻击简单视为二值异常，而是关注开放集攻击谱下的细粒度未知识别。

## 3. 对本项目的价值

该论文可补强 Evidence-OpenEMTD 的“未知攻击不是单一 Unknown 类”和“正常业务漂移会影响开放集阈值”的论证。它适合作为最新开放集 NIDS 边界工作。

## 4. 可引用位置

1. 相关工作：开放集 NIDS 与未知攻击检测。
2. 实验设置：动态合法流量、开放集攻击谱。
3. 讨论：Unknown 风险需要结合业务漂移和复核机制。

## 5. 局限性

FOSS 重点在异常型 NIDS 和未知攻击细粒度检测，并不直接解决加密恶意流量中的多模态证据融合。因此本项目可在“加密多模态证据冲突”上形成差异。
