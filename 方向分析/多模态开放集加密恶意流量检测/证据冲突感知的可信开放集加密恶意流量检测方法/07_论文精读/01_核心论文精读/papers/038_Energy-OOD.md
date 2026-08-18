# 038 基于能量的分布外检测 / Energy-based OOD Detection

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | 本文对应内容 | 覆盖状态 |
|---|---|---|
| Abstract | 第 2 节 | 已覆盖 |
| 1 Introduction | 第 3 节 | 已覆盖 |
| 2 Background | 第 4 节 | 已覆盖 |
| 3 Energy-based OOD Detection | 第 5 至 7 节 | 已覆盖 |
| 4 Experimental Results | 第 8 至 12 节 | 已覆盖 |
| 5 Related Work | 第 13 节 | 已覆盖 |
| 6 Conclusion and Outlook | 第 14 节 | 已覆盖 |
| 7 Broader Impact | 第 15 节 | 已覆盖 |

## 1. 文献身份

- 标题：Energy-based Out-of-distribution Detection。
- 中文题名：基于能量的分布外检测。
- 作者：Weitang Liu、Xiaoyun Wang、John D. Owens、Yixuan Li。
- 会议：34th Conference on Neural Information Processing Systems，NeurIPS 2020。
- arXiv：2010.03759。
- 本地全文：`paper/10.48550_arXiv.2010.03759.pdf`。
- 原文代码：`https://github.com/wetliu/energy_ood`。
- 方法定位：通用判别分类器的 OOD risk baseline；不是流量专用编码器，也不包含多模态结构。

## 2. 摘要缩译

开放环境中的模型必须判断输入是否来自训练分布之外。传统最大 softmax confidence 会对 OOD 输入产生过高置信度。论文提出使用 energy score：它可直接从任意预训练分类器的 logits 计算，无需重新训练；也可作为训练正则项，显式拉开 ID 与辅助 OOD 样本的 energy gap。

在 CIFAR-10 WideResNet 上，仅把 MSP 替换为 energy score，平均 FPR95 降低 18.03 个百分点。使用辅助 OOD 数据进行 energy-bounded fine-tuning 后，论文在六个 OOD benchmark 上进一步超过 Outlier Exposure 等方法。

## 3. 引言缩译

softmax 只描述已知类别之间的相对概率。ReLU 网络可能对远离训练数据的输入仍输出极高最大 softmax。Energy score 使用所有 logits 的绝对尺度，避免把最大 logit 减去 logsumexp 后丢失整体信息。

论文提出两条路线：

1. Inference-time energy：不改模型参数，用 energy 替换 MSP。
2. Energy-bounded learning：用 ID 与辅助 OOD 数据微调，使 ID energy 更低、OOD energy 更高。

这两条路线的数据要求不同，不能作为同一个 protocol baseline 报告。

## 4. Energy-based Model 背景缩译

Energy-based model 把输入映射到非概率标量 E。给定标签条件 energy，Gibbs 分布为：

> p(y | x) = exp[−E(x, y) ÷ T] ÷ Σᵧ′ exp[−E(x, y′) ÷ T]。

自由能为：

> E(x) = −T log Σᵧ′ exp[−E(x, y′) ÷ T]。

判别分类器 f(x) 输出 K 个 logits。令类别 energy 为：

> E(x, y) = −fᵧ(x)。

则输入 free energy 可直接由 logits 得到：

> E(x; f) = −T log Σᵢ exp[fᵢ(x) ÷ T]。

E 越低，模型越倾向认为样本来自 ID；E 越高，越倾向 OOD。也可使用 knownness score −E，此时方向相反。

## 5. 推理时 Energy Score 缩译

若定义 energy risk 为 E，则二值决策为：

> G(x) = 0，当 E(x; f) ≤ τ，判为 ID。

> G(x) = 1，当 E(x; f) > τ，判为 OOD。

论文建议只用 ID 数据选择阈值，使较高比例 ID 被接受。若改用 knownness −E，则 OOD 条件变为 −E < τ。两种写法完全等价，但实现中必须固定方向。

Energy 可用 logsumexp 直接计算，不需要估计对整个输入空间积分的 partition function。论文据此把它解释为与 log density 线性相关。

## 6. Energy 与 MSP 的关系缩译

当 T = 1 时：

> log MSP(x) = f最大(x) − log Σᵢ exp[fᵢ(x)]。

结合 energy 定义：

> log MSP(x) = E(x; f) + f最大(x)。

softmax 对所有 logits 同时加常数保持不变，而 energy 会随共同平移改变。论文认为 MSP 的最大 logit 平移造成偏置，energy 保留了更有用的绝对 logit scale。

需要补充的限制是：交叉熵本身并不唯一确定所有 logits 的共同偏移。因此判别分类器的 energy 并非天然校准密度；它的有效性是理论联系与经验结果的组合，仍需验证 logit shift、class bias 和跨域稳定性。

## 7. Energy-bounded Learning 缩译

仅使用预训练模型时，ID/OOD energy gap 未必充分。论文增加辅助 OOD 训练数据，优化：

> L总 = L交叉熵 + λL能量。

能量正则由两个 squared hinge 构成：

> L能量 = Eᵢₙ[max(0, E(xᵢₙ) − mᵢₙ)²] + Eₒᵤₜ[max(0, mₒᵤₜ − E(xₒᵤₜ))²]。

第一项惩罚 ID energy 高于 ID margin；第二项惩罚 auxiliary OOD energy 低于 OOD margin。目标是形成低 energy 的 ID 区域和高 energy 的 OOD 区域。

该方法明确使用 unlabeled auxiliary OOD training data。它不是 unknown-blind closed-set training，而是 external outlier exposure。

## 8. 实验协议缩译

ID datasets 为 CIFAR-10、CIFAR-100 和 SVHN，使用标准 train/test split。OOD test datasets 为 Textures、SVHN、Places365、LSUN-Crop、LSUN-Resize 和 iSUN；当 SVHN 作为 ID 时使用相应的其他 OOD 集。

辅助 OOD training data 来自 80 Million Tiny Images，并删除与 CIFAR-10/100 重叠的样本。目标 OOD test datasets 没有用于训练，但 margin hyperparameters 使用带 OOD 的 validation protocol 选择。

因此协议应分为：

- inference-time energy：不使用 auxiliary OOD，可视为 OOD-agnostic 后处理。
- energy fine-tuning：使用 external auxiliary OOD，属于 P1 outlier exposure。

## 9. 指标口径缩译

论文报告：

- FPR95：以 ID 为 positive，在 ID TPR = 95% 时，OOD 被错误接受为 ID 的比例。
- AUROC：区分 ID 与 OOD 的 ROC area。
- AUPR：论文实现沿用 ID-positive 口径，不是 AUPR-Out。
- In-distribution test error：闭集分类错误率。

这与 CAEOS 当前“unknown 为 positive”的 Unknown AUROC/AUPR-Out 体系存在方向差异。AUROC 在正确反转 score 后数值一致，但 AUPR 与 FPR@95TPR 不可直接搬运。

## 10. 训练设置缩译

分类 backbone 为 WideResNet。Energy fine-tuning 中 λ = 0.1，训练 10 epochs，initial learning rate 0.001 并使用 cosine decay；ID batch size 128，auxiliary OOD batch size 256。

ID/OOD margins 通过 OE 论文使用的 validation set 选择，以 validation FPR95 最小为目标。Temperature 实验显示 T 增大后 ID/OOD energy 更难分离，因此作者建议直接固定 T = 1。

## 11. CIFAR-10 主结果缩译

### 11.1 不重新训练

| 方法 | 平均 FPR95 | AUROC | AUPR | ID Test Error |
|---|---:|---:|---:|---:|
| MSP | 51.04 | 90.90 | 97.92 | 5.16 |
| Energy score | 33.01 | 91.88 | 97.83 | 5.16 |
| ODIN | 35.71 | 91.09 | 97.62 | 5.16 |
| Mahalanobis | 37.08 | 93.27 | 98.49 | 5.16 |

Energy 相对 MSP 把平均 FPR95 降低 18.03 个百分点，但 AUPR 略降 0.09，AUROC 也低于 Mahalanobis。它是强、简单的 baseline，不是所有指标绝对最优。

### 11.2 使用辅助 OOD 微调

| 方法 | 平均 FPR95 | AUROC | AUPR | ID Test Error |
|---|---:|---:|---:|---:|
| Outlier Exposure | 8.53 | 98.30 | 99.63 | 5.32 |
| Energy fine-tuning | 3.32 | 98.92 | 99.75 | 4.87 |

Energy fine-tuning 明显改善 OOD 指标。正文另出现 4.98% 的 ID error 表述，与表 2 的 4.87% 不一致；正式引用应优先按表格并注明原文内部差异。

## 12. 分 OOD 与 CIFAR-100 结果缩译

在 CIFAR-10 预训练模型上，energy score 对六个 OOD datasets 的 FPR95 均优于 MSP，但 Texture 和 SVHN 的 AUROC/AUPR 有时低于 MSP。Energy fine-tuning 相对 OE 大多数指标更强，但 LSUN-Crop 的 AUROC/AUPR 略有下降。

CIFAR-100 更困难：

| 方法 | 平均 FPR95 | AUROC | AUPR | ID Test Error |
|---|---:|---:|---:|---:|
| MSP | 80.41 | 75.53 | 93.93 | 24.04 |
| Energy score | 73.60 | 79.56 | 94.87 | 24.04 |
| Mahalanobis | 54.04 | 84.12 | 95.88 | 24.04 |
| Outlier Exposure | 58.10 | 85.19 | 96.40 | 24.30 |
| Energy fine-tuning | 47.55 | 88.46 | 97.10 | 24.58 |

Energy fine-tuning 改善 OOD detection，但 ID error 从 24.04 增到 24.58，说明拒识增强不保证闭集分类同步改善。

## 13. 相关工作缩译

论文将 OOD 方法分为：MSP/ODIN/Mahalanobis/ensemble 等判别后处理，OE/辅助异常数据微调，生成式 likelihood 方法，以及 energy-based learning。生成模型可能给 OOD 赋予高 likelihood，且优化 normalization 较困难；energy 方法从判别 logits 直接构造非概率 score，工程上更简单。

## 14. 结论与展望缩译

Energy score 是 MSP 的低成本替代，可用于任意预训练分类器；辅助 OOD 微调可进一步塑造 energy surface。作者把超越 image classification 的应用留给未来研究。因此流量检测中的有效性需要重新实验，不能由 CIFAR 结果直接推出。

## 15. Broader Impact 缩译

作者认为 OOD uncertainty 可提高消费应用、交通和医疗等开放环境系统的可靠性，并通过开源促进安全部署。论文没有系统讨论误拒 ID、对 subgroup 的差异影响或 adversarial logit manipulation，这些在安全流量场景仍需补充。

# 第二部分：独立技术分析

## A. 一句话结论

Energy 是 CAEOS 必须保留的最小开放集风险基线；后处理版可进入 P0 strict 主表，辅助 OOD 微调版必须标为 P1-Energy-OE，二者的训练数据、阈值和指标方向必须完全分开。

## B. 两条交付线映射

### 工程线

在现有 classifier logits 上增加：

> r能量(x) = −T log Σᵢ exp[fᵢ(x) ÷ T]。

规定 risk 越大越 unknown；T 固定为 1；threshold 只取 known-only validation quantile。不得根据 unknown AUROC 决定是否取负号。

### 论文线

把 `Energy-posthoc` 与 `Energy-OE` 分成两行：前者不改变训练，后者使用外部 outliers。主文优先报告 posthoc P0；Energy-OE 放协议附表或单独 external-exposure 分组。

## C. 协议审计

- Posthoc energy：不使用 OOD training data，若 threshold 仅用 known validation，则为 P0。
- Energy fine-tuning：使用 80 Million Tiny Images，属于 P1 external auxiliary OOD。
- Target OOD test：未参与训练，优于直接用 target unknown 调参。
- Margin selection：使用带 OOD 的 validation protocol，不是 known-only。
- FPR95：论文通常从 evaluation score curve 取 95% ID TPR；部署 threshold 仍应在 validation 冻结。
- seeds/CI：主表未提供 CAEOS 要求的多场景统计检验。
- protocol grade：`P0-posthoc-known-only-threshold/P1-external-OOD-finetuning`。

## D. OOD 与未知攻击不是同义词

图像 OOD benchmark 的 unknown 通常与 ID 语义和低层统计差异明显。未知恶意 attack family 可能与 known attacks 共享协议、工具链和 payload 结构，距离更近；新的 benign device/capture 反而可能产生更大 energy。

因此 energy 在流量场景可能同时拒绝 benign domain shift 和 unknown attacks。必须联合报告 Benign FAR、Known Acceptance 和 Unknown Rejection，不能只报告总体 AUROC。

## E. Score 方向与指标方向

CAEOS 应固定：

- risk：E，越大越 unknown。
- knownness：−E，越大越 known。
- Unknown AUROC/AUPR-Out：unknown 为 positive，使用 E。
- 原文 ID-positive FPR95：使用 −E，表示 95% ID acceptance 时 unknown 被接受率。

若 CAEOS 报告 `FPR@95TPR_unknown`，它表示 95% unknown recall 时 known 被错误拒绝率，与原文 FPR95 完全不同。表头必须写清 positive class，最好同时保留 `OOD-FPR@95-ID-TPR` 作为文献对齐附表。

## F. Energy 的方法局限

- 对所有 logits 加共同常数不会改变 softmax，却会改变 energy。
- 不同 class 的 logit scale 可能不同，global threshold 会产生 class-conditional acceptance bias。
- temperature 与 logit norm 会影响 score，不能在 unknown test 上选择。
- energy 只表达总体 logit mass，不直接表达多模态证据冲突。
- 强 closed-set classifier 可能让 unknown 也产生较大 logit mass。

因此 CAEOS 的 conflict、distance、support 和 class-conditional calibration 仍有必要，energy 不能替代全部风险组件。

## G. 三层指标映射

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | ID test error | Known Macro-F1、BA、per-class Recall、Benign FAR | 很弱 |
| 未知检测 | ID-positive FPR95、AUROC、AUPR | Unknown AUROC、AUPR-Out、明确方向的 FPR95、Unknown-F1 | 需转口径 |
| 联合开放集 | 无 | OSCR、OpenAUC、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 无 | ECE、Brier、NLL | 缺失 |

## H. 95%/5% 安全验收

论文 posthoc energy 在 CIFAR-10 的平均 FPR95 为 33.01%，远高于 5%；只有使用 auxiliary OOD fine-tuning 后达到 3.32%。但这不是恶意流量结果，也不是 unknown-positive FPR@95TPR。

因此不能用该论文声称 CAEOS energy 已通过 5% 门。CAEOS 必须在每个 leave-family-out scenario 上独立填写 Known ≥ 95%、Benign FAR ≤ 5%、Unknown 指标和 OSCR。

## I. CAEOS 采纳与否决

### 采纳

- 采纳 T = 1 的 posthoc energy 作为无参数风险基线。
- 采纳 known-only validation quantile 选择 operational threshold。
- 采纳 MSP、Energy、Mahalanobis/prototype distance 同 encoder 比较。
- 采纳 energy-bounded loss 作为 P1 外部 outlier exposure 扩展。

### 有条件采纳

- Energy-OE 只能使用与 target unknown family 无关的外部 outliers。
- global energy threshold 需与 class-conditional/Mondrian threshold 对照。
- 多模态模型应比较 fused-logit energy 与 per-modality energy/conflict。

### 不采纳

- 不用 target unknown test 选择 score 正负、temperature、margin 或 threshold。
- 不把 posthoc 与 Energy-OE 结果放在同一无暴露协议行。
- 不把 ID-positive FPR95 直接改名为 unknown-positive FPR@95TPR。
- 不把图像 OOD 结果当作未知攻击实验证据。
- 不因 energy AUROC 提升就推断 known classification 也提高。

## J. CAEOS 可执行实验

1. `E-ENERGY-01`：同一 strict-v4 logits 比较 MSP、max-logit、energy 和 entropy。
2. `E-ENERGY-02`：T 固定 1 为主，T sensitivity 只用 known validation 或预注册网格。
3. `E-ENERGY-03`：global quantile 与 class-conditional/Mondrian energy threshold。
4. `E-ENERGY-04`：fused-logit energy、各模态 energy、energy+conflict 联合风险。
5. `E-ENERGY-05`：Energy-posthoc P0 与 Energy-OE P1 分表比较。
6. `E-ENERGY-06`：benign cross-dataset shift 与 unknown malicious family 分开评估。
7. `E-ENERGY-07`：记录 95% known acceptance 下 unknown acceptance，以及 95% unknown recall 下 known rejection 两种 FPR。
8. `E-ENERGY-08`：5 seeds、scenario-block bootstrap、Holm-Wilcoxon、OSCR/ECE/Brier。

## K. 对自有算法的直接判断

若当前 CAEOS 的 Known Macro-F1 未过 95%，单纯更换 energy 公式不会提高未拒识前的 closed-set classification；它最多通过改变 threshold 减少 known rejection，但通常会牺牲 unknown rejection。

若误报率未低于 5%，首先要区分 benign FAR、known false rejection 和论文式 OOD FPR95。只有当错误主要来自 global energy threshold 时，class-conditional calibration 才可能直接改善；若 encoder 本身把 benign/attack 分错，应先修复表征和分类边界。

## L. 可引用与不可引用主张

### 可引用

- Energy 可从任意分类器 logits 通过 negative logsumexp 计算。
- Posthoc energy 不需要重新训练或辅助 OOD 数据。
- 在 CIFAR-10 上，posthoc energy 把平均 ID-positive FPR95 从 51.04% 降到 33.01%。
- 使用外部 auxiliary OOD fine-tuning 后，平均 FPR95 降到 3.32%。
- Energy fine-tuning 不保证 ID classification 一定改善。

### 不可引用

- Energy 已证明适用于未知恶意流量。
- Energy-OE 是 unknown-blind P0 方法。
- 原文 FPR95 等于 CAEOS unknown-positive FPR@95TPR。
- Energy score 是已经校准的输入概率。
- Energy 在所有 OOD datasets 和所有指标上都优于 MSP。
- Energy 单项足以替代 conflict、distance 和 support。

## M. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过，本地 NeurIPS/arXiv PDF 与全文抽取存在
- G2 身份门：通过至会议、作者和 arXiv，Zotero 待办
- G3 任务门：通过，明确 OOD 与未知攻击的差异
- G4 协议门：通过，`P0-posthoc-known-only-threshold/P1-external-OOD-finetuning`
- G5 方法门：通过
- G6 结果门：通过，表 1 至表 3、温度/margin 和消融结果已核读
- G7 对比门：通过，需按 exposure 分组
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
