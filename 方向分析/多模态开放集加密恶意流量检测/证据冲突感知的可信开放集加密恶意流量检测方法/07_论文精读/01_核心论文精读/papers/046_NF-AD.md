# 046 使用归一化流的可解释网络流量异常检测 / NF-AD

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | 本卡 | 状态 |
|---|---|---|
| Abstract / I Introduction | 第 2 至 3 节 | 已覆盖 |
| II Related Work / III Background | 第 4 至 5 节 | 已覆盖 |
| IV Proposed Method | 第 6 至 10 节 | 已覆盖 |
| V Evaluation / VI Explainability | 第 11 至 18 节 | 已覆盖 |
| VII Conclusion | 第 19 节 | 已覆盖 |

## 1. 文献身份

- 标题：Explainable Anomaly Detection in Network Traffic Using Normalizing Flows。
- 作者：Lior Shafir、Raja Giryes、Avishai Wool。
- 期刊：IEEE Transactions on Networking，34，2026，1205–1220。
- DOI：10.1109/TON.2025.3617580。
- 代码：作者发布 `NF-anomaly-detection` 实现。
- 方法：良性单类 Normalizing Flow 密度估计＋SHAP/LIME 特征筛选和局部解释。
- 定位：强二元异常检测与密度风险基线；不是已知恶意家族分类和未知家族拒识的完整 OSR 方法。

## 2. 摘要缩译

监督式网络异常检测依赖覆盖充分的攻击标签，难以应对持续变化的威胁。论文仅用正常流量训练双向归一化流，通过精确似然识别低概率流，并用 Shapley 值解释哪些特征使样本偏离正常分布。

作者进一步提出两种特征选择：少样本方案使用少量标注异常；传导式方案在无标签正常/异常混合集上寻找 Shapley 波动较大的特征。方法在 CICIoT-2023、ISCXTor2016 和 CICIDS2017 上评估，CICIoT-2023 报告 0.9951 accuracy。

## 3. 引言缩译

网络攻击不断变化，监督模型既受未知攻击影响，也受类别不平衡影响。单类异常检测把正常行为作为可学习对象，偏离正常分布的样本均视为异常，因而训练阶段不依赖攻击标签。

归一化流兼有可逆映射和精确似然，既能拟合复杂良性分布，也能为单样本提供连续异常分数。论文的核心主张是：密度预测结合局部 Shapley 值，不仅可以报出异常，还能指出导致低似然的具体流特征。

## 4. 相关工作缩译

作者回顾统计 IDS、AE/VAE、GAN、OCSVM、Kitsune、记忆增强 AE、对抗检测与 normalizing flow。现有生成方法往往依赖重构误差或合成异常，而 NF 可直接计算观测点密度。

XAI 部分讨论 Shapley 与 LIME。作者承认 Shapley 通常解释的是模型输出而非真实因果，且特征交互会使不同模型间的重要度不可比，因此为特征筛选引入随机噪声“中性基线”。

## 5. Normalizing Flow 基础

设可逆映射 x = f(z)，基础分布为 p_z。变量替换给出：

> pₓ(x) = pᴢ(f⁻¹(x)) · |det Jf⁻¹(x)|。

K 层变换的对数密度为：

> log pₓ(x) = log pᴢ(z₀) − Σₖ₌₁ᴷ log|det ∂fₖ(zₖ₋₁) ÷ ∂zₖ₋₁|。

可逆层必须同时具备足够表达能力和可计算的 Jacobian determinant。训练最大化良性流量似然，等价于最小化：

> L = −Σᵢ₌₁ᴺ log pₓ(xᵢ)。

## 6. 数据表征与预处理

输入仅采用 flow-level header statistics，不读取 payload。特征包括：

- Flow duration、双向 packet count 与 byte count。
- Packet length 的均值、方差和极值。
- Flow/forward/backward IAT。
- TCP flags、window size、active/idle statistics。
- Network/transport protocol characteristics。

删除 port、IP address 和 absolute timestamp，以减弱数据采集环境与标签捷径。所有特征做 z-score：

> zᵢ = (xᵢ − μ) ÷ σ。

论文未充分说明 μ、σ 是否在每次拆分中严格只由训练良性样本拟合，这是复现实验必须固定的细节。

## 7. 单类训练与似然检测

训练矩阵只保留 y = 0 的 normal samples。检测阶段计算 log pₓ(x)，并按阈值二分：

> f(x) = Normal，当 log pₓ(x) > τ；否则为 Anomalous。

该决策只回答“是否偏离正常流量”，不输出攻击家族，也不区分已知攻击与未知攻击。其 anomaly 包括恶意攻击，也可能包括罕见但合法的良性变化。

## 8. Shapley 局部解释

特征 i 的 Shapley 值为：

> φᵢ = Σₛ⊆N∖{i} [|S|!(n−|S|−1)! ÷ n!] · [v(S∪{i}) − v(S)]。

在本文中 v 是 NF 的 log-likelihood。负贡献表示该特征压低样本似然，正贡献表示该特征更符合正常分布。它解释模型打分机制，不自动等同攻击因果或真实根因。

## 9. 少样本特征选择

少样本方案取 k 个标注异常与同量正常样本。对每个候选特征 f，将其与 base set S 组合，重新训练 NF，计算异常/正常样本的局部贡献，再用完整测试集 AUROC 检查贡献排序与检测性能的相关性。

作者发现强判别特征作为 S 会造成交互干扰；用 [−1,1] 均匀随机噪声作中性特征后，异常样本 Shapley 分布的 90% 分位数与 AUROC 显著相关。主实验 k = 20，消融覆盖 10、20、50、100、200。

该路线明确使用 target anomaly labels，且研究阶段以完整测试 AUROC 验证候选特征。因此它是半监督特征选择证据，不能写成严格 unknown-blind 选择。

## 10. 传导式特征选择

传导式方案从测试环境抽取无标签正常/异常混合样本，按 mean absolute Shapley 排序：

> TShapᵢ = (1 ÷ N)Σⱼ₌₁ᴺ|φᵢⱼ|。

ISCXTor2016 使用 100 Tor 与 100 Non-Tor 测试样本计算该分数。它不需要标签，但读取了目标测试分布，属于 transductive setting，不能与完全 inductive、测试不可见协议混写。

## 11. 数据集与任务定义

### CICIoT-2023

数据含 33 种攻击、7 个大类：DDoS、DoS、Reconnaissance、Web-based、Brute Force、Spoofing、Mirai。论文将全部攻击合并为 anomaly，只训练 benign，因此丢失细粒度攻击分类任务。

### CICIDS2017

只评估 Wednesday 的 DoS/DDoS：Hulk、GoldenEye、Slowloris、Slowhttptest，以便与 MemAE/SparseMemAE 比较。结论不能外推到全部 CICIDS2017 攻击家族。

### ISCXTor2016

Non-Tor 用作 normal，Tor 用作 anomaly。这是加密流量类型异常，不是恶意流量检测，因为 Tor 本身不等于恶意。

## 12. 拆分、采样与阈值

每个数据集随机抽取 20,000 normal 和 10,000 anomaly。10,000 normal 用于训练，10,000 normal 与 10,000 anomaly 用于 test。

阈值相关指标另设 1,000 normal＋1,000 anomaly validation，并选择使 TPR−FPR 最大的阈值；测试集保持 10,000＋10,000。实验运行五个随机种子，AUROC 报告均值。

这一阈值协议直接查看异常验证标签，不符合 CAEOS “阈值只能用 known-only validation”的安全门。随机 flow sampling 也没有证明按 capture、device 或 connection grouping，仍可能存在同源泄漏。

## 13. ISCXTor2016 结果

排除与 Tor 标签高度相关的 Protocol Type 后，NF ensemble AUROC 为 0.8731；若保留 Protocol Type，最好 AUROC 可达 0.932。单 NF 使用 Bwd IAT Std 与 Active Mean 时 AUROC 约 0.851。

排除捷径特征的处理是合理的，但 0.8731 仍只表示 Tor/Non-Tor 二元分离，不能作为未知恶意检测成绩。

## 14. CICIDS2017 结果

NF 在所选 DoS/DDoS 子集上 AUROC 约 0.93，优于论文复现的 OCSVM、AE、MemAE、SparseMemAE 和 Kitsune。最佳五个特征包括 Bwd Packet Length Mean、Fwd Packets/s、ACK Flag Count、Total Length of Bwd Packets 和 Flow Duration。

基线有的只用良性训练，有的使用少量攻击，监督条件并不完全相同；结果只能按训练标签条件分组比较。

## 15. CICIoT-2023 结果

NF 仅用 10,000 良性样本训练，阈值指标与监督 RF、DNN、AdaBoost、LR、XGBoost 比较，并报告最高 accuracy 0.9951。XGBoost 使用同一 10,000 良性再加 10,000 攻击样本。

高 accuracy 来自平衡二元测试和含异常验证的阈值，不代表已知攻击 family Macro-F1≥95%，也不证明 Benign FAR≤5%。表格 OCR 未可靠保留全部 Precision/Recall/F1 数值，不能据此补写缺失数据。

## 16. 跨数据集泛化

因 CICIoT-2023 与 CICIDS2017 特征集合不同，作者使用特征兼容的 CICIDS2017 与 CICDDoS2019 互训互测。训练一个数据集的 benign、测试另一个数据集的 benign 与 attacks，性能较同域略降但保持较高。

这是有价值的跨域压力测试，但目标域标签仍参与阈值/结果选择，且两个 CIC 系列数据共享提取体系，不能替代更异构的跨数据集 OSR。

## 17. 可解释性结果

合成二维例子比较 NF、OCSVM 和 XGBoost。NF 的 Shapley 能分别指出 F1/F2 偏离；OCSVM 对两个特征给出近似相同贡献；XGBoost 可能只依赖 F1。

真实 CICIoT-2023 例子构造“仅一个特征低概率”的攻击子集，以 Gaussian KDE 估计单特征 likelihood。NF Shapley 能突出 Variance 或 fin count 等人为定义的 deviant feature，XGBoost 有时突出无关 Magnitude。

作者明确承认这些结果主要是 anecdotal cases，尚未形成大规模人工根因标注或因果验证。

## 18. 消融结论

- 随机噪声 base feature 能减弱跨模型交互导致的 Shapley 不可比。
- SHAP 与 LIME 均能在少样本设置下形成重要度与 AUROC 的显著相关。
- 少样本数量从 10 增至 200 时趋势总体稳定。
- Ensemble 仅当所有 NF 都判异常才拒绝，偏保守但可能提高漏报；论文未给 95% known acceptance 下的完整安全表。

## 19. 结论缩译

论文证明 NF 可用良性流量学习精确密度，并在三个数据集上取得较强二元异常检测结果。结合 Shapley 后，可支持特征筛选和样本级偏离解释。跨数据集存在性能下降，作者建议未来引入自监督预训练改善域泛化。

# 第二部分：独立技术分析

## A. 一句话结论

NF-AD 值得作为 CAEOS 的“良性单类密度＋解释”适配基线，但原论文用 target anomalies 选阈值和少样本特征，任务也没有已知攻击家族分类，因此不能直接进入严格 OSR 主表或支撑 95%/5% 验收。

## B. 两条交付线

### 工程线

在统一 split 与相同统计输入上实现 NF negative log-likelihood risk；预处理、模型、阈值均按场景重拟合。严格版本用 known-only validation quantile；复现版本单列 anomaly-labeled validation。

### 论文线

把 NF-AD 放入密度/一类异常基线组，注明其原始任务、监督条件和适配差异。不得把二元 accuracy 与 Known Macro-F1、Unknown AUROC 或 OSCR 混为同一指标。

## C. 协议审计

- NF 训练：normal-only。
- 阈值：normal＋target anomaly validation，最大化 TPR−FPR。
- Few-shot selection：使用 target anomaly labels，并以完整 test AUROC 验证特征。
- Transductive selection：使用目标测试混合分布但不读标签。
- Split：random flow sampling，未证明 capture/device/connection grouping。
- Protocol：`P2-target-anomaly-validation-and-feature-selection/P3-random-flow-split-and-transductive-test-exposure`。

## D. 与三层指标的关系

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | 二元 Accuracy/Precision/Recall/F1 | Family Macro-F1、BA、per-class Recall、Benign FAR | 任务不一致 |
| 未知检测 | AUROC，但 positive 为合并 anomaly | Unknown AUROC、AUPR-Out、FPR95、Unknown-F1 | 可适配，不可直比 |
| 联合开放集 | 无 | OSCR、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 经验阈值，无 ECE/Brier/NLL | ECE、Brier、NLL、risk reliability | 缺失 |

## E. 95%/5% 安全门判断

原文 threshold 最大化 Youden J：

> J(τ) = TPR(τ) − FPR(τ)。

这既使用异常标签，也不保证 known acceptance 为 95%。0.9951 accuracy 受平衡测试比例影响，不能推出 Benign FAR < 5%。CAEOS 严格版应在 known-only validation 上取：

> τ = Q₀.₉₅(sᵏⁿᵒʷⁿ)，并在测试集独立报告 Known Acceptance、Benign FAR 和 Unknown Rejection。

## F. 与证据冲突方法的关系

NF likelihood 主要测量“样本是否符合整体良性密度”；CAEOS conflict 测量多模态证据是否互相矛盾。二者理论上互补，但高维 likelihood 存在 typicality failure，低似然也可能来自无害域漂移。

需要检验 NLL、energy、distance、vacuity、conflict 的 rank correlation、增量 AUROC 与条件错误率，不能仅把多个风险线性叠加后宣称贡献。

## G. 多模态判断

论文主模型只有 flow statistics 单模态。多种统计字段不是独立模态；没有 payload bytes、packet sequence encoder 或语义视图。它只能作为统计分支基线，不能证明 CAEOS 的三模态有效性。

## H. 采纳与否决

### 采纳

- Normal-only NF density baseline。
- 删除 IP、port、absolute time 的捷径审计。
- 跨数据集 benign shift 测试。
- 局部特征贡献用于错误分析。

### 有条件采纳

- SHAP feature selection 仅放入 P2 半监督支线。
- Transductive selection 单列，不与 inductive 结果混表。
- Ensemble 需在固定 Known Acceptance 下比较。

### 不采纳

- 不用 unknown validation 选择正式阈值。
- 不把 Tor 当未知恶意。
- 不以随机流拆分替代 capture/device grouped split。
- 不用 accuracy 推导 Macro-F1 或 FAR。
- 不把 Shapley attribution 称为攻击因果解释。

## I. CAEOS 可执行实验

1. `E-NFAD-01`：统一统计特征下 NF、OCSVM、AE、Energy 对照。
2. `E-NFAD-02`：原文 P2 阈值与 strict known-only 95% quantile 并列。
3. `E-NFAD-03`：NLL typicality、likelihood ratio 与 input complexity correction。
4. `E-NFAD-04`：within-dataset leave-family-out，5 seeds，全三层指标。
5. `E-NFAD-05`：跨数据集 grouped split 与 benign shift FAR。
6. `E-NFAD-06`：statistics-only、payload-only、sequence-only 与三模态消融。
7. `E-NFAD-07`：NLL＋conflict 的增量、相关性和失败样本归因。
8. `E-NFAD-08`：阈值 bootstrap CI 与每类/每域 Known Acceptance。

## J. 可引用与不可引用主张

### 可引用

- NF 只使用正常流量训练并以 log-likelihood 检测异常。
- CICIoT-2023 含 33 种攻击、7 个攻击大类。
- ISCXTor2016 排除 Protocol Type 后 AUROC 0.8731。
- CICIDS2017 所选 DoS/DDoS 子集 AUROC 约 0.93。
- CICIoT-2023 二元任务 accuracy 0.9951。
- 作者发布实现并进行了五个随机种子实验。

### 不可引用

- 0.9951 是已知攻击家族分类准确率。
- 原文满足 unknown-blind threshold selection。
- Accuracy 证明 Benign FAR≤5%。
- Tor anomaly 等同未知恶意流量。
- Shapley 值构成真实攻击根因证据。
- Random flow split 已排除 capture/device leakage。

## K. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过
- G2 身份门：通过至 IEEE/DOI，Zotero 待办
- G3 任务门：通过
- G4 协议门：通过，`P2-target-anomaly-validation-and-feature-selection/P3-random-flow-split-and-transductive-test-exposure`
- G5 方法门：通过
- G6 结果门：通过，三数据集、跨域、消融与解释案例已核读
- G7 对比门：通过
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
