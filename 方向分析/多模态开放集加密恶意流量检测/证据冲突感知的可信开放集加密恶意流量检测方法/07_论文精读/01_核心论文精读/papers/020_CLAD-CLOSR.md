# 020 CLAD/CLOSR：用于零日网络入侵检测的新型对比损失

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | PDF页 | 本卡位置 | 关键证据 | 状态 |
|---|---:|---|---|---|
| Abstract / Introduction | 1-2 | 第1-2节 | 摘要定量结果 | 已覆盖 |
| Related Work | 2-3 | 第3节 | 异常检测、OSR、对比学习 | 已覆盖 |
| Proposed Approach | 3-7 | 第4-6节 | 式1-17、图1 | 已覆盖 |
| Experiments | 7-9 | 第7-8节 | 表I-IV、图2-3 | 已覆盖 |
| Ablations / Efficiency | 9-12 | 第8节 | 表V-VII、图4-5 | 已覆盖 |
| Discussion / Conclusion | 12 | 第9-10节 | 局限 | 已覆盖 |

## 1. 标题、摘要与关键词

作者为 Jack Wilkie、Hanan Hindy、Craig Michie、Christos Tachtatzis、James Irvine 和 Robert Atkinson。论文发表于 IEEE Transactions on Network and Service Management，2026 年，第23卷，DOI 为 10.1109/TNSM.2026.3652529。

论文提出 Contrastive Learning for Anomaly Detection（CLAD）和其开放集扩展 CLOSR。核心动机是：纯监督分类器对已知攻击强但对零日类失效；只用良性的异常检测器能发现零日攻击，却常以高误报为代价。CLAD 同时利用良性和已知恶意样本训练，但只把良性锚点显式压入 von Mises-Fisher 分布，使已知和未知恶意流量都远离良性中心。CLOSR 再为每个已知攻击类建立独立投影子空间和类条件分布，用于已知分类与 unknown 拒识。

## 2. 引言缩译

作者将零日检测建模为表征几何问题。传统二分类把 benign 与 known malicious 建成对称边界，容易把未知恶意误判为良性。纯异常检测不使用恶意监督，无法利用已知攻击的判别信息。论文希望形成一个非对称空间：良性样本集中，已知恶意与其相反，同时不强迫所有恶意类形成封闭分布，从而为零日恶意保留可分区域。

## 3. 相关工作缩译

相关工作涵盖一类 SVM、DeepSVDD、自动编码器、Isolation Forest、OpenMax、DOC、CROSR、G-OpenMax、生成 unknown 和基于特征距离的 OSR。作者指出，重构误差对部分攻击过低会抬高误报；OpenMax 类方法依赖闭集分类特征；一般监督对比损失对各类对称建模，仍带有闭世界假设。

## 4. 问题定义与数据缩译

二分类 CLAD 的标签为 benign 与 malicious，训练恶意只含已知攻击，测试再分别评估 known attack 与 zero-day attack。CLOSR 的训练类为 benign 加多个 known malicious classes，某个恶意类留作 unknown。

数据为修正后的 Lycos2017，共 1,789,954 flows、14 类，良性超过 100 万条，恶意类从 11 到 100,000 不等。论文按每类均匀样本数做 50%/50% 训练测试划分；训练侧再在消融中按 80%/20% 分为训练和验证。全文未证明按原始 PCAP、捕获时间或五元组指纹分组，存在同源泄漏风险。

## 5. CLAD 方法缩译

编码器 φ 把输入 x 映射到单位超球面。普通监督对比学习同时优化各类，而 CLAD 只选择良性锚点：让良性对接近，让良性与恶意对接近超球面的相反方向。距离使用缩放余弦距离，范围为 0 至 1；论文把正负距离平方，使远离目标的样本产生更大梯度。最优 margin 在搜索中收敛到 1.0，即把 benign 与 malicious 推向近似对跖区域。

推理时，训练良性嵌入的均值方向为 μ₀，测试嵌入 z 的 OOD 分数由 z 与 μ₀ 的余弦相似度或 vMF 似然给出。低于阈值的样本判为 malicious。论文主要报告 AUROC 和 FPR@95，因此没有冻结实际部署阈值；作者建议实际系统在 held-out benign validation 上按 SOC 可承受误报率选择阈值。

## 6. CLOSR 开放集扩展缩译

CLOSR 为每个已知类 c 建立独立线性投影头 h꜀，并计算训练嵌入中心 μ꜀。已知类别后验由各投影子空间中的相似度经 SoftMax 得到：

p(y = c ∣ x, y∈K) = exp(h꜀(z)·μ꜀) ÷ ∑ᵢ∈K exp(hᵢ(z)·μᵢ)

unknown 风险来自测试样本在各类子空间中的高斯似然。论文的 soft-weighted Gaussian score 用闭集后验给各类似然加权；分数低于阈值时输出 unknown。论文认为 zero-day 嵌入在多个维度上较分散，与任何已知类中心近似正交。

## 7. 实验设置缩译

所有模型训练 200 epochs，AdamW，20 epochs 线性 warm-up 后余弦退火，使用加权采样。学习率、批量、权重衰减、dropout、宽度和深度以 200 次随机搜索、训练数据 5-fold CV 选择，目标为 mean AUROC。最终报告 20 次训练/评估均值，并以 p<0.01 标注显著性。论文未说明多重比较校正和效应量。

二分类基线包括异常检测、监督分类和对比学习方法；开放集基线包括 DOC、OpenMax、CROSR 等。指标包括 AUROC、FPR@95、closed-set Accuracy、open-set AUC 和 OpenAUC。

## 8. 实验结果、消融与效率缩译

摘要报告：CLAD 相对既有方法在已知攻击 AUROC 上提高 0.000065，在零日攻击 AUROC 上提高 0.060883；CLOSR 的 OpenAUC 提高 0.170883。表I-II显示 CLAD 对零日攻击的 AUROC 与 FPR@95 改善具有统计显著性；已知攻击 FPR@95 改善未达到显著。

CLOSR 的 open-set AUC 最高，但 closed-set Accuracy 略低；将 CLOSR 作为独立 OOD 检测器与 Siamese 闭集分类器组合，可同时取得两者各自较强的一端。消融中，margin 趋向 1.0 时 AUROC 更高且平方距离更稳定；浓度权重 α 在 0.1 至 0.9 扫描时，mean AUROC 为 0.999574，标准差 0.000570。

类代理消融显示 benign centroid 优于 median、trimmed mean、medoid 和 nearest neighbor。CLOSR 风险消融显示 soft-weighted Gaussian likelihood 优于 energy 和未加权 Gaussian。已知嵌入矩阵 normalized rank 为 0.0625，留出零日类为 0.4375，支持“unknown 更分散”的假设。

效率实验在 RTX 3090、Xeon W-2255、Ubuntu 22.04、PyTorch 2.0.1 上进行。CLAD 参数量较大但延迟/吞吐优于 RENOIR；CLOSR 因每类投影头而随类数增长，效率低于部分非对比 OSR 基线，但优于依赖训练集近邻搜索的 Siamese 推理。

## 9. 讨论与局限缩译

CLOSR 的模型大小和计算量随已知类数线性或更快增长；尚未在对抗攻击、污染训练集、跨网络和少样本场景中验证。论文也未报告冻结 operating point 下的 known acceptance、unknown rejection、OSCR、ECE、Brier 或 NLL。

## 10. 结论缩译

CLAD 用非对称对比目标结合 benign 与 known-malicious 监督，减少纯异常检测的误报；CLOSR 把类条件子空间扩展到已知分类和零日拒识。其最有价值之处是损失几何和 known-only 阈值建议，而不是已经证明满足严格 95%/5% 门槛。

# 第二部分：独立技术分析

## A. 文献身份与状态

- 记录号：020；短名：CLAD/CLOSR；证据角色：A-直接核心。
- 本地 PDF：`paper/10.1109_TNSM.2026.3652529.pdf`。
- 全文抽取：`04_120篇全文抽取/020_A_Novel_Contrastive_Loss_for_Zero_Day_Network_Intrusion_Detection.txt`。
- 精读层级：L3；当前状态：`project_mapped`。
- Zotero Item / Citation Key：pending。

## B. 协议审计

模型训练不使用目标 zero-day 类；作者明确建议实际阈值只用 held-out closed-set/benign validation，属于 `P0-known-only-candidate`。但论文正式主结果以阈值无关指标和测试 ROC 上的 FPR@95 为主，没有实际冻结阈值；50/50 随机 flow 拆分也未证明 capture-grouped。因此只能视为 P0 候选，不能直接认定 strict-v4 合规。

## C. 与 CAEOS 的关系

CLOSR 是强风险基线：它没有证据冲突模块，却把每类投影子空间、类中心、Gaussian likelihood 和闭集后验组合成 unknown score。CAEOS 应在完全相同的三模态输入、split、seed 和 known-only validation 阈值下与其比较。CLAD 的 benign-centroid 分支还可作为良恶第一层基线。

## D. 95%/5% 安全门

论文报告 FPR@95，但该 FPR 的正类/负类口径需按 CAEOS unknown-positive 统一；测试 ROC operating point 不能直接当作可部署阈值。论文没有证明 Known Macro-F1≥95%、Benign FAR≤5%、Unknown FPR95≤5% 和 OSCR 同时成立，也未报告校准指标。

## E. 采纳与新增实验

1. `E-BASELINE-CLOSR`：同输入、同 strict-v4 split、5 seeds，阈值只由 known validation 的 95% acceptance 冻结；主指标六项全部报告。
2. `E-COMPONENT-CLAD`：把 CAEOS 编码器的闭集交叉熵分别替换/联合 CLAD，比较已知 Macro-F1、良性 FAR、unknown AUROC 与 OSCR。
3. `E-ABLATION-GAUSSIAN`：比较 soft-weighted Gaussian、energy、prototype distance、CAEOS conflict 和组合风险；权重只通过 known-class inner leave-one-out 确定。
4. `E-ROBUST-CLOSR`：加入标签噪声、良性污染、缺失模态和跨数据集测试；若 per-class head 随类别扩展导致显存/延迟不可接受，则仅保留风险分支。

## F. 最终审计

- G0-G1：通过。
- G2：身份核至 DOI；Zotero 未核。
- G3-G9：通过。
- G10：未通过。
- 最终状态：`project_mapped`，不能标为 complete。
