# [586] A Novel Contrastive Loss for Zero-Day Network Intrusion Detection

## 1. 基本信息

- 题名译法：一种面向零日网络入侵检测的新型对比损失
- 年份与来源：2026，IEEE Transactions on Network and Service Management
- DOI：10.1109/TNSM.2026.3652529
- 作者：Jack Wilkie 等
- 任务定位：网络入侵检测中的已知攻击检测、零日攻击检测、开放集识别
- 数据集：Lycos2017，14 类流量，约 178.9 万条 flow
- 代码：`source\CLOSR`，包含 CLAD、CLOSR、二分类与开放集基线实现

## 2. 中文翻译与核心摘要

这篇论文的核心动机很直接：传统监督式 NIDS 在已知攻击上很强，但遇到训练集中没有出现过的攻击类会退化；异常检测模型理论上能发现未知攻击，但只学习 benign 分布，常常误报高。作者提出 CLAD，把 benign 流量显式建模为单位超球面上的 vMF 分布，同时仍使用已知恶意样本作为对比负样本来塑造边界。这样模型不是去学习“所有恶意是什么”，而是更稳地学习“正常流量应该靠近哪里”。

进一步，作者把 CLAD 扩展为 CLOSR：为每个已知类建立独立投影子空间和类中心，用类中心相似度做闭集分类，用与各类中心近似正交的表现识别未知类。论文的贡献不在于换一个网络结构，而在于把对比学习从“所有类对称拉开”改成“围绕已知正常/已知类分布的开放世界建模”。

## 3. 论文解决的具体问题

论文针对的是 NIDS 中三类模型的断层：

1. 监督分类器依赖闭集假设。训练集中见过的攻击类型可以识别，但新攻击不一定落在“恶意”决策区。
2. 异常检测只学 benign，能避开闭集假设，却容易把新的正常子类、业务漂移或罕见 benign 行为判成攻击。
3. 既有对比学习能缓解类别不平衡，但通常仍把所有训练类对称建模，零日攻击没有参考样本时，嵌入空间未必支持“远离 benign 中心”的推断。

作者要解决的具体问题是：能否在训练时利用已知恶意样本降低误报，同时在推理时不把“已知恶意分布”等同于“所有恶意分布”。

## 4. 创新点深度提炼

- **非对称对比学习**：CLAD 只以 benign 为锚类优化，已知攻击只是负样本，避免把恶意类当作封闭全集。
- **vMF 分布解释**：单位超球面上的 benign 嵌入被解释为 vMF 分布，中心方向成为可用于推理的统计代理，而不是普通聚类中心。
- **中心点推断而非闭集 logits**：CLAD 推理时计算测试样本与 benign centroid 的余弦相似度/距离，零日攻击无需类别原型。
- **CLOSR 的类级子空间**：每个已知类有独立 projection head，缓解多类共享超球面时类中心挤压的问题。
- **开放集 OOD 分数**：CLOSR 假设未知类在各类子空间中更接近正交/弥散分布，用加权平方相似度构造未知类分数。
- **对比学习服务于低误报零日检测**：论文不是单纯追求 representation learning，而是把嵌入几何与 NIDS 的误报/漏报权衡绑定起来。

## 5. 科学问题与研究假设

科学问题可以概括为：在只拥有 benign 与部分已知攻击样本时，如何学习一个对未知攻击仍有效、且误报率低的流量表示空间？

主要假设如下：

- benign 流量在合适的嵌入空间中可以形成紧致方向分布。
- 已知恶意样本虽然不能代表所有恶意，但可以帮助 benign 分布获得更大的安全间隔。
- 零日攻击不应被强行吸附到任何已知攻击类中心；更合理的几何表现是远离 benign 中心，或在 CLOSR 中与已知类中心弱相关。
- 多类开放集识别中，为每个类单独建模比把所有类塞进同一个共享超球面更适合发现未知类。
- 对 NIDS 而言，阈值无关指标 AUROC、FPR@95 比固定阈值准确率更能反映部署价值。

## 6. 科学方法与技术路线

CLAD 的技术路线是：

1. 用 MLP 将 flow 特征映射到单位超球面。
2. 使用重缩放余弦距离 `d=(1-cos)/2`。
3. 对 benign-anchor 的正样本对最小化距离，对 benign 与非 benign 的负样本对最大化距离；在最终形式中近似为 `正对 d^2 + 负对 (1-d)^2`。
4. 训练结束后，用训练集中 benign 嵌入的归一化均值作为 centroid。
5. 推理时，测试样本越接近 benign centroid 越像正常，越远越像异常/攻击。

CLOSR 的路线是在 CLAD 上做类级扩展：共享 backbone 先提取中间表示，再为每个已知类设置一个投影头；每个投影头只学习对应类相对其他类的 vMF 分布。闭集分类取最大类中心相似度，开放集检测则使用加权平方相似度的负值作为 OOD 分数。代码里符号相反：先算正的 `sum(sim^2 * softmax(sim))`，评估 AUROC 时再乘 `-1`。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据：使用 Lycos2017，包含 benign 与多种攻击流量；论文将 Web Attack SQL Injection、Heartbleed 作为 zero-day，仅放入测试侧。
2. 预处理：删除 `flow_id, src_addr, src_port, dst_addr, dst_port, ip_prot, timestamp` 等元数据列，删除全零特征列，用训练集均值方差做 z-normalization。
3. 切分：已知类按 50%/50% 划分训练/测试；代码中 `sample_thres=100` 会把低样本类剔出训练并作为 zero-day。
4. 采样：训练 DataLoader 使用 `WeightedRandomSampler` 做类别平衡，处理流量数据天然不均衡。
5. 模型：CLAD 为普通 MLP + 单 projection head；CLOSR 为 MLP + 每类 projection head。
6. 基线：二分类比较 AE、DAE-LR、DUAD、Deep SVDD、One-class SVM、Isolation Forest、RENOIR、MLP、Siamese；开放集比较 MultiStage、DOC、OpenMax、CROSR、Siamese。
7. 训练：AdamW，200 epoch，20 epoch warmup 后 cosine annealing；论文用 200 次随机搜索和 5-fold CV 选超参，最终报告 20 次训练/评估均值。
8. 指标：二分类用 AUROC、FPR@95；开放集用 closed-set accuracy、open-set AUC、OpenAUC。
9. 消融：margin、平方距离、浓度权重比例 `alpha`、类代理点、CLOSR OOD score、嵌入可视化、线性探针、计算成本。
10. 结果核查：不仅看 AUROC，还要检查 zero-day 是否确实远离 benign centroid，以及 closed-set 精度是否因开放集能力而下降。

## 8. 关键结果、结论与证据

CLAD 在已知攻击检测上的平均 AUROC 为 **0.999855**，略高于强基线 RENOIR 的 **0.999790**，提升 **0.000065**。这个提升数值很小，但说明 CLAD 没有因为开放世界目标牺牲已知攻击性能。

更关键的是 zero-day：CLAD 平均 AUROC 为 **0.996627**，优于最强基线 DUAD 的 **0.935744**，提升 **0.060883**。这说明已知恶意样本作为负样本确实提高了 benign 边界质量，而没有让模型过拟合“已知恶意 = 所有恶意”。

开放集上，CLOSR closed-set accuracy 为 **0.995276**，低于 Siamese 的 **0.997722**；但 open-set AUC 达到 **0.974022**，OpenAUC 达到 **0.969420**，相比 MultiStage 的 OpenAUC **0.798537** 提升 **0.170883**。论文的实际结论是：CLOSR 用少量闭集精度换来了显著更强的未知类拒识能力。

消融进一步支持了机制解释：平方距离更稳定，margin 趋近 1.0 时更好；`alpha` 对性能不敏感；centroid 比 median、trimmed mean、medoid、nearest neighbour 更适合作为 CLAD 的类代理；zero-day 嵌入的归一化 rank 明显高于已知类嵌入，符合“未知类更弥散”的假设。

## 9. 局限性与待解决问题

论文自己承认 CLOSR 的每类 projection head 会使参数量和计算成本随类别数增长，这在网络攻击类较少时可接受，但迁移到上千类场景会困难。

实验主要依赖 Lycos2017，zero-day 只由少数被留出的攻击类模拟，尚不能证明跨网络、跨时间、跨组织环境的泛化能力。阈值也没有真正部署校准，论文使用 AUROC、FPR@95 等阈值无关指标；实际 CSOC 仍需用验证集按可承受误报率选阈值。

鲁棒性方面，论文没有评估对抗样本、污染 benign 训练数据、概念漂移、特征缺失或加密流量特征变化。vMF、各子空间独立、zero-day 近似各向同性这些假设有实验支撑，但还不是严格充分的网络安全语义解释。

本次正文包标记为未截断；不过若后续要引用 FPR@95 表格或 Table IV 的逐项数值，建议回到 PDF 原表逐项核对。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”强相关，尤其适合作为开放集/零日检测方向的核心方法参考。它给本项目的启发不是“再训练一个 MLP”，而是如何把训练目标改成开放世界友好的几何结构。

如果本项目面向多模态开放集恶意流量检测，CLAD/CLOSR 可以作为 flow-level 分支或 baseline：先在统计流特征上学习 benign/known-class 超球面分布，再与包序列、TLS/QUIC 元数据、日志行为特征融合。它也适合作为综述中“监督分类、异常检测、对比学习、开放集识别”之间的桥接论文。

## 11. 代码对照分析

本地代码与论文方法对应关系如下：

| 论文模块 | 代码位置 | 作用 |
|---|---|---|
| CLAD 损失 | `source\CLOSR\losses\clad_loss.py` | `CLADLoss` 只对 `target_class=0` 计算正对收缩、异类间隔；支持 `margin`、`squared`、`alpha` 消融 |
| CLOSR 损失 | `source\CLOSR\losses\closr_loss.py` | 对 `[batch, n_classes, dim]` 嵌入逐类计算 CLAD，再取平均 |
| MLP/backbone | `source\CLOSR\model\model.py` | `ContrastiveMLP` 对应 CLAD，`CLOSRMLP` 对应类级 projection head |
| 数据处理 | `source\CLOSR\data\load_data.py`、`data\loaders.py` | 读 `lycos.csv`、删列、删全零特征、低样本类作 zero-day、z-normalization、加权采样 |
| 特征抽取 | `source\CLOSR\util\features.py` | 分 chunk 提取嵌入，避免一次性推理全数据 |
| 距离与中心 | `source\CLOSR\util\distance.py` | 余弦距离、CLAD benign centroid、CLOSR class centroids |
| CLAD 训练/评估 | `train_clad.py`、`eval_clad.py` | 默认 4 层 1024、输出维度 8；评估时用 benign centroid 计算 AUROC/FPR@95 |
| CLOSR 训练/评估 | `train_closr.py`、`eval_closr.py` | 默认 3 层 1024、输出维度 64；评估 closed-set acc、open-set AUC、OpenAUC |
| 基线 | `baseline_implementations\...` | 包含 AE、SVDD、SVM、RENOIR、DOC、OpenMax、CROSR、Siamese 等 |

运行线索：仓库根目录下执行 `pip install -r requirements.txt`，将 Lycos2017 放为 `source\CLOSR\data\lycos.csv`，再运行 `python train_clad.py`、`python eval_clad.py`、`python train_closr.py`、`python eval_closr.py`。本地 `weights` 目录已有 `clad.pt.tar` 和 `closr.pt.tar`，但 `data\lycos.csv` 不存在，所以当前代码包不能直接完成评估。

## 12. 本篇精华

- CLAD 的关键是“只建模 benign，但训练时利用 known attack”，这是它区别于异常检测和监督分类的核心。
- 损失函数的非对称性比网络结构更重要：benign 是锚，恶意是边界塑形材料。
- 单位超球面 + vMF 分布让 centroid 推断有统计意义，zero-day 检测不依赖已知攻击原型。
- CLOSR 用每类独立子空间解决多类共享嵌入中类中心挤压的问题。
- 论文最强证据在 zero-day AUROC：0.996627，比最强异常检测基线高 0.060883。
- CLOSR 的开放集能力显著强，但 closed-set accuracy 略降，适合与强闭集分类器组合。
- 局限集中在跨域泛化、对抗鲁棒性、污染训练集、阈值校准和 projection head 扩展性。
- 代码实现清晰，适合复现 CLAD/CLOSR；但论文级随机搜索、20 次运行和统计检验需要自行补实验驱动脚本。

## 13. 建议精读路线

先读 Introduction 和 Proposed Approach，抓住“监督闭集假设、异常检测高误报、CLAD 非对称建模”这条主线。随后精读 Equation 7、8、9 和 CLOSR 的 Equation 12、16，重点理解训练损失和推理分数不是同一件事。

第二遍读实验部分时，不要只看平均 AUROC，要对照 known attack 与 zero-day attack 的差异，再看 FPR@95。最后读消融部分，特别是 margin、centroid proxy、alignment analysis 和 CLOSR OOD score，这几处最能判断方法是否真的靠假设工作，而不是偶然调参赢了基线。