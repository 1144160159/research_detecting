# 025 ECNet：多视图特征与置信机制的鲁棒恶意流量检测

## 1. 文献身份

- 论文：*ECNet: Robust Malicious Network Traffic Detection With Multi-View Feature and Confidence Mechanism*
- 作者：Xueying Han 等
- 期刊：*IEEE Transactions on Information Forensics and Security*, 19, 6871-6885, 2024
- DOI：`10.1109/TIFS.2024.3426304`
- 本地全文：`04_120篇全文抽取/025_ECNet_Robust_Malicious_Network_Traffic_Detection_With_Multi_View_Feature.txt`
- 当前状态：`project_mapped`；全文缩译与 CAEOS 映射完成，Zotero/引用键、表格逐项数值和代码复现待完成。

## 2. 摘要缩译

真实网络同时包含已知、变种和未知恶意流量，检测器既要准确，也要泛化和说明预测是否可信。监督方法擅长已知攻击，却会对未知攻击静默高置信误判；无监督方法可发现异常，但误报高且不能利用已知攻击标签。ECNet 从传输内容与通信模式两个视角提取特征，以门控结构融合，并联合训练类别概率和置信度。测试时，高置信样本依靠正常/恶意概率分类，低置信样本直接视为未知恶意。作者在 CICIDS2018 与自建 EnTra2023 重组出的六个任务上对比七种方法，称未知攻击 F1 最多优于最佳监督方法 22.41 个百分点、优于最佳无监督方法 14.15 个百分点。

## 3. 任务边界与威胁模型

ECNet 的输出空间只有 normal 与 malicious。训练见到正常流量和若干已知恶意类型；测试包含已知恶意、同类攻击变种和全新恶意家族。它借低置信触发把未见攻击归为 malicious，而不是把它们输出为独立 unknown，也不对恶意家族做已知细分类。因此 ECNet 解决的是“开放环境下的二元恶意检测”，不是 CAEOS 的“良性+已知攻击家族分类，同时拒识未知攻击家族”。

样本是双向五元组 session，可部署在网络边界或交换机镜像口。攻击范围包括暴力破解、DoS/DDoS、C&C、扫描和横向移动等会产生网络流量的主动行为；不覆盖提权、被动流量分析或本地漏洞利用等无网络表现的攻击。

作者假设正常网络模式在一段时间内变化不大，因此“不熟悉且低置信”的流量可直接判恶意。这一假设是方法成立的关键：若部署后出现新正常应用、TLS/QUIC 版本迁移或业务切换，低置信规则会提高良性误报。

## 4. 多视图输入缩译

### 4.1 内容视图

每个 session 随机选 nₚ = 4 个包并按时间排序。删除 IP 和 MAC 地址，每包保留前 200 字节，超长截断、短包补零。三层 1D CNN 与两层全连接组成 PacketCNN：

f′ₚ = Fᴾᶜ(fₚ)

为让模型自动选择握手或数据阶段的重要包，对包特征使用四头注意力：

Attention(Q, K, V) = softmax[(QKᵀ) ÷ √dₖ]V

MultiAtt = concat(head₀, …, head₃)Wʰ

f⁽ᶜ⁾ = (1 ÷ nₚ)∑ᵢ₌₁ⁿᵖ MultiAttᵢ

随机采包降低存储和计算，但也使同一流多次推理可能不同。论文仅称四包在性能/复杂度间最佳，没有固定采样种子、采样分层规则或预测方差。它不能作为 CAEOS 统一预处理“只保留四包”的依据；完整包级信息仍应保存在基础 CSV，四包只是 ECNet 基线的模型侧选择。

### 4.2 模式视图

从完整 session 提取包长序列 L = (l₁, …, lₙ) 和方向序列 D = (d₁, …, dₙ)。连续同方向包构成 burst；每行放一个 burst 的包长，列数 m = 3，长 burst 跨相邻行并插入空行保持方向边界，得到二维编码 vˢᵠ。两层 2D CNN 和两层全连接构成 SessionCNN：

fₑ = Fˢᶜ(vˢᵠ)

该编码不直接用正负号表示方向，目的是避免交换源/目的主机造成方向符号噪声，同时保留序列、频率和 burst 结构。约 80% burst 长度不超过 3，因此作者取 m = 3。

### 4.3 门控融合

内容与模式特征通过两个不共享参数的双线性门：

g⁽ᶜ⁾ = σ[(f⁽ᶜ⁾)ᵀW⁽ᶜ,ᵍ⁾fₑ + b⁽ᶜ,ᵍ⁾]，gₑ = σ[fₑᵀWₑᵍf⁽ᶜ⁾ + bₑᵍ]

fₛ = concat(g⁽ᶜ⁾ ⊙ f⁽ᶜ⁾, gₑ ⊙ fₑ)

这是样本自适应特征门控，但门值不是概率校准后的可靠性，也没有 Dempster-Shafer 证据质量或显式冲突项。两个视图又都来自同一 PCAP，统计依赖明显；直接把它称为独立多模态证据会夸大方法含义。

## 5. 置信训练与检测缩译

### 5.1 概率与置信双头

概率头和置信头各为两层线性层加 dropout：

p = softmax[Fᴾᴳ(fₛ)]，c = σ[Fᶜᴳ(fₛ)]

概率头输出 normal/malicious 概率，置信头输出标量 c ∈ (0, 1)。训练时模型可向真实标签 y“请求提示”，修正概率为

p′ᵢ = cpᵢ + (1 − c)yᵢ

低置信会更多借用真实标签，故分类损失

Lₚ = −∑ᵢ₌₁² yᵢ log p′ᵢ

之外，还用

L⁽ᶜ⁾ = −log c

惩罚过度请求提示，总损失为

L = Lₚ + λ(s)L⁽ᶜ⁾，λ(s) = λ₀ exp(−s ÷ β)

作者给 50% 输入提供提示。衰减方向意味着后期使用低置信提示的代价减小，需结合原代码核查其与“后期增强置信”的文字是否完全一致。

### 5.2 困难样本增强

为防止模型把所有训练输入都给置信 1，内容增强随机把四个包特征中的一个置零；模式增强随机选择二维编码的一半行，对每行一至两个元素加减 1并截断负值。内容增强比例 α_c 最优约 10%，模式增强在 30%-50% 范围表现稳定。这些是同源遮挡/扰动，不是外部未知数据，因此仍可属于 known-only 训练。

### 5.3 推理规则

测试时若 c < δ_c，直接判 malicious；否则按概率最大类输出：

r = 1，当 c < δ_c

r = arg max_{i∈{0,1}} p′ᵢ，当 c ≥ δ_c

低置信样本不保留 unknown 标志，因此未知检测性能只能间接反映在二元 malicious recall/F1 中。论文从训练集再抽 10% 作 validation 用于超参数和模型选择，原则上未把测试未知写入训练；但图 14 在最终 unknown 数据集上扫描 δ_c 并讨论 0.6-0.9 的效果，正文没有明确最终阈值是否仅由 known-only validation 固定。保守记为 `P0-candidate/P3-threshold-sensitivity-risk`。

## 6. 数据集重组与评价协议

基础数据为 CICIDS2018 和 EnTra2023。后者正常流量来自企业主机一天活动，恶意流量来自 Malware Capture Facility Project 的 64 个 PCAP，覆盖 spyware、miner、ransomware、botware 和 adware。

每个基础数据重组成三种任务：

- I（known）：混合全部正常/恶意后随机分 train/test。
- II（variant）：CICIDS2018 把同一大类但不同工具的攻击分到训练和测试；正常流量按前五天/后三天分。EnTra2023 按不同 PCAP 和时间拆分。
- III（unknown）：CICIDS2018 按不同攻击类型拆分；EnTra2023 训练只含三种恶意软件，测试含其他类别/类型；正常流拆分沿用 II。

这种 I/II/III 分层比单一随机划分更接近真实泛化，但没有对每个 unknown family 做 leave-one-family-out、多种子与置信区间。所有数据还被采样以平衡 normal/malicious，这会使 accuracy、precision 和 F1 与真实基率下的 FAR 不一致。

评价只用 Accuracy、Precision、Recall、F1。没有 Known Macro-F1、每攻击家族 recall、Unknown AUROC/AUPR/FPR95、OSCR、ECE 或 Brier。论文把变种和未知都按最终 malicious 二元标签计算，因此不能直接放入 CAEOS 三层指标主表。

## 7. 主要实验结果缩译

### 7.1 已知攻击

在 CICIDS2018-I 和 EnTra2023-I 上，ECNet 的 accuracy 均为 99.97%，F1 均为 99.98%；不含置信头的 ECNet-Simple F1 也达到 99.71% 和 99.98%。说明已知任务的主要收益来自内容/模式表征，置信分支在同分布测试中贡献很小。

### 7.2 变种与未知攻击

CICIDS2018-II 上 ECNet accuracy 98.97%、F1 94.59%，相比 I 下降 1.01 和 5.39 个百分点；FS-Net recall 69.73%、F1 78.71%。Kitsune recall 91.31% 接近 ECNet，但 precision 更低，说明正常误报更多。

CICIDS2018-III 上部分监督基线接近失效：FS-Net accuracy 41.65%、F1 56.08%，CICAutoML F1 35.85%。ECNet F1 为 85.78%，相对最佳监督方法高 22.41 个百分点；相对 Kitsune 等无监督方法的最大 F1 优势为 14.15 个百分点。即便如此，85.78% 仍明显低于 CAEOS 的 95% 安全目标。

EnTra2023-II 上 ECNet accuracy 99.82%、F1 99.79%；EnTra2023-III 中 ECNet 与 ECNet-Simple 的 F1 分别为 99.08% 和 95.10%，accuracy 为 99.25% 和 98.12%。这也说明在该数据上低置信分支并非唯一未知检测来源，内容/模式表征本身已经强；数据集容易程度和采集域可能占较大影响。

### 7.3 类别召回、置信与复杂度

CICIDS2018-III 中约 50% 恶意流量的 c < 0.5，低置信分支贡献明显；EnTra2023-III 只有少量恶意样本低置信，多数依靠概率头正确判恶意。EnTra2023-III 最低恶意大类召回为 spyware 97.14%。这证明 c 的语义依赖数据域，并不天然等于 epistemic uncertainty。

复杂度表的逐项数字在当前文本抽取中未恢复。正文只称 ECNet 参数量和时延略高于 ACID/CVAE-EVT，但可近实时；正式引用前需从表 VII 图像核对参数量、每 session 时延、硬件和批处理口径。

## 8. 消融与敏感性缩译

只用模式特征时，CICIDS2018-II accuracy 下降 6.53 个百分点、F1 下降 20.39 个百分点；CICIDS2018-III 只用内容特征时 F1 下降 10.82 个百分点。说明两个视图在不同类型域偏移下互补，而不是某一视图始终占优。

门控融合相对直接拼接在 CICIDS2018-III 上提升 accuracy 1.57 个百分点、F1 4.41 个百分点。nₚ = 4 与 6 性能接近，2 包明显不足；m 对效果影响小但影响空间/时延。随着 δ_c 从 0 增大，未知恶意召回提高；0.6-0.9 时 precision 略降，因为新正常 session 被误判恶意。这正是 CAEOS 必须显式报告 Benign FAR 的原因。

## 9. 作者讨论与独立局限

作者认为攻击者若要规避，需要同时修改原始包、包长和方向，还因随机采包而必须修改全部包；但这只是成本论证，没有白盒/黑盒自适应攻击实验。作者承认剧烈环境变化仍需要重新采集数据和重训，未来拟结合增量学习并自适应设置置信阈值。

更关键的独立局限是：

1. 低置信一律恶意把开放集拒识和异常二分类混为一体，无法处理新正常类别。
2. 任务最终不输出 unknown，无法计算 unknown rejection 或 OSCR。
3. 数据被二元平衡采样，论文 precision/F1 不能代表生产环境低恶意基率下的 FAR。
4. 置信头没有 ECE/Brier/NLL 校准验证；c 是训练出的选择性提示权重，不等于可信概率。
5. CICIDS2018-I 随机混合划分可能存在 capture/fingerprint 泄漏；II/III 虽更严格，也未给多种子 family-level 统计。
6. 内容与模式均来自同一 PCAP，门控没有建模证据冲突和模态缺失。

## 10. 对 CAEOS-EMTD 的吸收程度

ECNet 应作为两类基线进入工程：第一，字节内容+包长方向的双视图门控表征；第二，learning-confidence 风险头。它不应被当作完整开放集分类基线，因为它只做 normal/malicious 二分类，也不应把 c 直接命名为“可信度”。

CAEOS 可保留 ECNet 的概率头与置信头，但推理时应输出显式风险而不是把低置信直接改写为 malicious。设

rᶜᵒⁿᶠ = 1 − c

在 known-only validation 上定阈值，再分别测：低置信中有多少未知恶意、多少已知恶意、多少新正常。随后将 rᶜᵒⁿᶠ 与 energy、prototype distance、support、evidential conflict 做单项和融合对比。

## 11. CAEOS 可执行实验

1. 复现 `ECNet-Simple`、`ECNet-confidence` 和 `ECNet-gated` 三个同 split 基线。
2. 保留完整统一数据，不在预处理层删到四包；仅在 ECNet dataloader 固定种子采四包，并额外报告 4/6/全包摘要的差异。
3. 设计 known family 分类头而不是二元头，另设显式 unknown rejection；报告三层指标。
4. 在 known-only validation 固定 δ_c；不得根据 unknown test 图 14 选择阈值。
5. 增加 new-benign/OOD-benign 测试，单独报告 Benign FAR；这是验证低置信恶意假设的必要反例。
6. 对 c 做 ECE、Brier、NLL 和 risk-coverage；比较 MSP、energy、MC dropout、evidential uncertainty。
7. 做门控冲突实验：构造字节内容指向已知类而序列模式指向另一类的反事实样本，检查门值是否能反映冲突。
8. 使用 capture/fingerprint grouped split、5 个种子、paired Wilcoxon+Holm 与 scenario-block bootstrap，避免单一采样结果。

## 12. 95%/5% 安全验收判断

- Known-I：99.98% F1 表面通过，但任务只是二元 known malicious 检测，不能替代已知攻击家族 Macro-F1。
- Variant-II：CICIDS2018 F1 94.59%，未达 95%。
- Unknown-III：CICIDS2018 F1 85.78%，明显未达 95%；EnTra2023 99.08% 说明跨数据差异很大。
- 良性误报：正文没有以真实基率报告 Benign FAR，也没有给 FPR@95TPR，无法判定低于 5%。
- 联合开放集：没有 OSCR 与显式 unknown 输出，无法验收。

因此，ECNet 提供“为什么闭集很高而未知仍可能不足 95%”的直接证据，不能作为 CAEOS 已达安全门的支撑。

## 13. G0-G10

| 门 | 状态 | 说明 |
|---|---|---|
| G0 中文缩译 | 通过 | 覆盖摘要、动机、威胁、方法、实验、消融、讨论与结论 |
| G1 全文 | 通过 | 本地全文可定位 |
| G2 身份 | 未通过 | DOI 已核，Zotero/Citation Key 未绑定 |
| G3 任务 | 通过 | 已明确它是开放环境二元恶意检测 |
| G4 协议 | 通过 | I/II/III、validation 和阈值风险已审计 |
| G5 方法 | 通过 | 双视图、门控、置信损失和决策已还原 |
| G6 结果 | 通过 | 关键正文数值已记录；图像表逐格值待补 |
| G7 公平性 | 通过 | 已审计采样、任务和输入差异 |
| G8 局限 | 通过 | 作者与独立局限均记录 |
| G9 项目映射 | 通过 | 已形成八项实验 |
| G10 引用 | 未通过 | Zotero/证据卡待办 |

## 14. 一句话结论

ECNet 的双视图门控和学习置信头值得作为 CAEOS 组件基线，但“低置信即恶意”的二元决策既不等于开放集家族拒识，也无法保证新正常流量的 5% 误报门；其最大价值是提供一个必须被更严格三层指标重新检验的强对照。
