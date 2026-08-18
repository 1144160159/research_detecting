# 034 基于不确定性量化的可扩展加密流量应用标注 / Ext-UQ

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | 本卡 | 状态 |
|---|---|---|
| Abstract / I Introduction | 第 2 至 3 节 | 已覆盖 |
| II Related Work / III Dataset | 第 4 至 5 节 | 已覆盖 |
| IV Methods | 第 6 至 9 节 | 已覆盖 |
| V Experiments | 第 10 至 14 节 | 已覆盖 |
| VI Discussion / VII Conclusion / Appendix | 第 15 至 16 节 | 已覆盖 |

## 1. 文献身份

- 标题：Extensible Machine Learning for Encrypted Network Traffic Application Labeling via Uncertainty Quantification。
- 作者：Steven Jorgensen 等。
- 期刊：IEEE Transactions on Artificial Intelligence，5(1)，2024，420–432。
- DOI：10.1109/TAI.2023.3244168。
- 方法：time-window feature＋prototypical network＋relative Mahalanobis KDE p-value。
- 定位：可信已知分类和 known-only calibrated OOD score；不是恶意攻击专用方法。

## 2. 摘要缩译

加密流量模型会随新应用出现而失效，因此既要输出校准类别概率，也要指出样本是否不属于任何训练类别。论文发布包含 10 个应用、5 个类别的 VPN/非 VPN PCAP 数据集，并提出可少样本快速训练的 prototype framework。

该框架用 relative Mahalanobis distance 排序 OOD，再用 held-out ID calibration 的 KDE 转换为可解释 p-value。自建数据 Micro-F1 为 0.98；企业网络 Zoom 等新应用获得高 OOD score，加入少量新标签后可快速扩展。

## 3. 引言缩译

VPN 隐藏 payload、port、address 和连接边界，只留下 packet size 与 timing。作者区分：

- Predictive uncertainty：在已有类别之间犹豫。
- Model/OOD uncertainty：样本可能不属于任何已知类别。

高 softmax confidence 在 OOD 上没有意义，因此需要独立 distance score。模型按固定时间窗持续预测，不依赖完整 connection 的开始和结束。

## 4. 相关工作缩译

论文回顾 flow statistics、wavelet features、FlowPic、深度 encoder、website fingerprinting、ECE/temperature scaling、ensemble、Mahalanobis 与 relative Mahalanobis OOD。

作者还指出 ISCXVPN2016 某些 PCAP 可能含可见明文或混合连接，因而另建数据以降低 shortcut。

## 5. 数据集

自建数据含 10 applications、5 coarse categories：Command & Control、Chat、File Transfer、Streaming、VoIP。处理后 40.96 秒 windows 数量分别为 1,675、10,498、851、1,827、243。

企业扩展测试包括：

- 已见应用/已见类别：YouTube→Streaming。
- 新应用/已见类别：Avaya→VoIP、SMB/Code42→File Transfer。
- 新应用/新类别：Zoom→Video Teleconference。

## 6. 预处理和特征

按五元组组流，每条 connection 切为 40.96 秒窗口，少于 20 packets 的窗口丢弃；timestamp、payload size 和 direction 以 0.01 秒离散为长度 4096 的序列。

每窗口生成 129 features：

- Forward/backward packet count、length、interarrival、active/idle statistics。
- Haar discrete wavelet 0–12 bands 的 relative energy、Shannon entropy、absolute mean/std。

该输入是同一流量源的统计与 wavelet 多视图，不是 payload byte＋sequence＋statistics 三个独立 encoder。

## 7. Prototypical Network

Embedding network 有 4 个 64-unit fully connected layers，ReLU，在中间连接使用 25% dropout，embedding dimension 64。

类别 k 的 prototype：

> cₖ = (1 ÷ S)Σₛfθ(xₛᵏ)。

预测概率：

> P(y = k ∣ x) = exp[−d(fθ(x), cₖ)] ÷ Σₖ′exp[−d(fθ(x), cₖ′)]。

Episodic training 使用 20,000 episodes、每次 512 query、每类 5 support，按 query cross-entropy 更新。

## 8. Relative Mahalanobis

普通 Mahalanobis：

> M(x; μ, Σ) = (x − μ)ᵀΣ†(x − μ)。

相对距离：

> M相对ᵏ(x) = M(x; μₖ, Σₖ) − M(x; μ₀, Σ₀)。

减去总体分布距离可消除对 ID/OOD 不具判别力的公共方向。训练后每类最多抽 100 个 training supports 估计均值和 full covariance。

## 9. Known-only KDE 校准

对每类 held-out ID calibration samples 计算 relative distance，并拟合 class-conditional univariate Gaussian KDE Gₖ。

测试样本先预测为 k*，relative distance 为 r，其 ID 右尾 p-value：

> p = ∫ᵣ∞Gₖ*(r′)dr′。

定义 OOD risk：

> sᴼᴼᴰ = 1 − p。

所以 risk 越大越 OOD；`sᴼᴼᴰ > 0.95` 等价于 p < 0.05。理想 calibration 下，阈值 α 会拒绝约 (1 − α) 的 ID，天然对应 95% Known Acceptance / 5% ID rejection。

## 10. 闭集与校准结果

随机 80/20 split、10 trials：全部数据 Micro-F1 0.982 ± 0.004；只用约 10% 数据仍接近 0.96，ECE 约 0.04；全量 ECE 约 0.03。

UTMobileNet2021 17 applications 上 accuracy 80%。应用标签从 5 增到 20 时 accuracy 从 93% 降到 80%，显示粗类别性能不能直接外推细粒度 family classification。

## 11. 企业同域/新应用测试

YouTube 40 samples 几乎全部正确识别为 Streaming，OOD risk 多数较低。

Avaya 全部识别为 VoIP，但约一半 risk > 0.95，说明“分类正确”和“分布内可信”可分离。SMB、Code42 初始不能稳定识别为 File Transfer，分别约 78%、63% risk > 0.95。

加入 91 SMB samples 后 test accuracy 92%、高 risk 降至 10%；加入 42 Code42 后 accuracy 98%、高 risk 降至 5%。

## 12. 新类别 Zoom

323 Zoom examples 中，训练前约 78% risk > 0.95。加入 195 labeled Zoom 作为新 VTC 类后，held-out 高 risk 降至 26%，Zoom accuracy 约 73%。错误 Zoom 中约 97% risk > 0.95，说明 risk 可筛出多数错误，但新类拟合仍不充分。

该结果是单个 target OOD application 的 threshold detection，不是多场景 AUROC 结论。

## 13. Padding 鲁棒性

把所有 packet sizes 统一为 1500 bytes 后重新训练，Micro-F1 仍为 0.971 ± 0.008，仅比原始 0.982 ± 0.004 略降，说明 timing/wavelet signal 仍强。

## 14. OOD baseline

对照假设 squared Mahalanobis 服从 64 自由度 χ²。χ² risk 在 ID 上接近 0/1 两极，不如 relative Mahalanobis＋KDE 接近 uniform calibration。两者都能给 Zoom 较高 risk，但 KDE score 更可解释。

## 15. 讨论缩译

作者强调该数据只覆盖有限应用，模型用于形成可扩展分析直觉。未来可对高 OOD samples 聚类、交由 analyst 命名并增量训练。主要限制是 window size/bin size、环境变化、类别粗粒度、未知类型有限及人工标注成本。

## 16. 结论缩译

论文最强贡献不是 0.98 F1，而是把类别 probability calibration 与 known-only OOD p-value 分开。它提供了符合部署解释的 operating threshold，但没有现代 OSR 全曲线指标和联合分类拒识评价。

# 第二部分：独立技术分析

## A. 一句话结论

Ext-UQ 是 CAEOS 应纳入的强 P0 prototype-distance calibration baseline；其 `relative Mahalanobis＋class KDE p-value` 与 95%/5% 安全门直接一致，但必须补齐 grouped split、多 unknown families、AUROC/AUPR/FPR95、OSCR 和恶意标签语义。

## B. 两条交付线

### 工程线

在统一 encoder embedding 上实现 class mean/full covariance、global mean/covariance、relative distance、class KDE。所有 statistics/KDE 仅用 known training/calibration。

### 论文线

将其列为 P0 校准距离基线，不把 Zoom 单类 78% 检出率写成 SOTA。与 k-LND3、Mahalanobis、Energy、OpenMax 同 encoder 比较。

## C. 协议审计

- Encoder/prototypes：known training。
- Covariance：known training supports。
- KDE：held-out known calibration。
- OOD threshold：p-value 0.05，无 target OOD。
- Target OOD：只用于事后评估与 retraining extension。
- Split：随机 window 80/20，未证明 connection/capture grouping。
- Model selection：window/bin/features 的开发过程可能使用同数据经验，外部验证有限。
- Protocol：`P0-known-only-relative-Mahalanobis-KDE/P3-window-level-split-leakage-risk`。

## D. 95%/5% 对齐

`risk > 0.95` 理论对应 ID p-value < 0.05，因此 operational known false rejection 目标为 5%。但有限 calibration、KDE bandwidth 和 covariate shift 会破坏 uniformity，必须实测每类 Known Acceptance 与 Benign FAR。

它控制的是“ID 被拒率”，不自动等于 benign 被误报为 malicious 的 FAR。

## E. 与 EDL/Conflict 的关系

Relative distance 测量 support mismatch；prototype probability 测量已知类相对竞争；它不直接表达多模态证据冲突。CAEOS 应检验 distance、vacuity、conflict 是否各自提供增量，而不是重复融合高度相关风险。

## F. 三层指标

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | Micro-F1/accuracy | Macro-F1、BA、per-class Recall、Benign FAR | 不足 |
| 未知检测 | risk>0.95 比例、CDF | AUROC、AUPR-Out、FPR95、Unknown-F1 | 不足 |
| 联合开放集 | 无 | OSCR/OpenAUC/accept-reject | 缺失 |
| 校准 | ECE、KDE p-value | ECE/Brier/NLL/risk reliability | 部分强 |

## G. 采纳与否决

### 采纳

- Relative Mahalanobis。
- Class-conditional known-only KDE calibration。
- Predictive uncertainty 与 OOD uncertainty 分离。
- 新应用加入前后 risk distribution 对照。

### 有条件采纳

- Full covariance 需 shrinkage/diagonal 对照。
- 少样本类需最低 calibration size 与 bootstrap CI。
- KDE bandwidth 只用 known goodness-of-fit 选择。

### 不采纳

- 不随机拆同一 connection 的 windows。
- 不把 p-value 当真实 unknown probability。
- 不把 ID rejection 5% 等同 benign FAR 5%。
- 不把单个 Zoom 结果外推未知恶意家族。

## H. CAEOS 可执行实验

1. `E-EXTUQ-01`：Mahalanobis、relative Mahalanobis、k-LND3、Energy 同 encoder。
2. `E-EXTUQ-02`：global/class KDE 与 empirical quantile。
3. `E-EXTUQ-03`：full、diagonal、Ledoit-Wolf covariance。
4. `E-EXTUQ-04`：connection/capture grouped split。
5. `E-EXTUQ-05`：每类 p-value uniformity、coverage 与 reliability plot。
6. `E-EXTUQ-06`：distance＋conflict 增量和相关性。
7. `E-EXTUQ-07`：leave-family-out 5 seeds 全三层指标。
8. `E-EXTUQ-08`：增量加入 unknown family 前后重新校准。

## I. 可引用与不可引用主张

### 可引用

- Relative Mahalanobis 减去总体 distribution distance。
- KDE 只拟合 ID calibration distances。
- 1−p 提供 known-only calibrated OOD risk。
- Zoom 训练前约 78% samples risk>0.95，加入新类后降至 26%。
- Padding 后 Micro-F1 仍约 0.971。

### 不可引用

- OOD risk 是真实 unknown probability。
- 论文已证明 Benign FAR≤5%。
- 单 Zoom 结果证明未知恶意检测。
- Random window split 排除了连接泄漏。
- 0.98 Micro-F1 等于已知恶意 Macro-F1。

## J. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过
- G2 身份门：通过至 IEEE/DOI，Zotero 待办
- G3 任务门：通过
- G4 协议门：通过，`P0-known-only-relative-Mahalanobis-KDE/P3-window-level-split-leakage-risk`
- G5 方法门：通过
- G6 结果门：通过，OOD扩展、padding、baseline 已核读
- G7 对比门：通过
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
