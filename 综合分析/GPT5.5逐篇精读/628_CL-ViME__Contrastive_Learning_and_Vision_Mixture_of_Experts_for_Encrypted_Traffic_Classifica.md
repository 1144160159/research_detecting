# [628] CL-ViME: Contrastive Learning and Vision Mixture of Experts for Encrypted Traffic Classification

## 1. 基本信息

- 题名：CL-ViME: Contrastive Learning and Vision Mixture of Experts for Encrypted Traffic Classification
- 作者：Saihua Cai、Lizhou Chen、Jinfu Chen、Shengran Wang、Guofeng Zhang
- 来源：IEEE Transactions on Network and Service Management
- DOI：10.1109/TNSM.2025.3650038
- 发表信息：2025 年 12 月 31 日在线发表，当前版本为 2026 年 1 月 13 日，卷期显示为 IEEE TNSM Volume 23, 2026
- 任务类型：加密流量分类、应用识别、恶意流量检测辅助
- 方法关键词：自监督学习、对比学习、Vision Transformer、Mixture of Experts、包级/流级双粒度表示
- 本地代码状态：未发现该论文对应的本地开源代码，因此代码分析只能依据论文方法推断应有模块结构，不能做源码级复核。

## 2. 中文翻译与核心摘要

这篇论文的核心目标是：在加密协议普及、有效载荷不可见、标注数据稀缺的情况下，仍然学习到可迁移、可区分类别的加密流量表示。作者提出 CL-ViME，将原始 PCAP 流量构造成“包-时间矩阵”，再用垂直切分的 ViT-MoE 主干提取包级与流级特征，最后用双粒度对比学习把两个视角对齐到统一潜空间。

论文不是简单把流量当字节序列或灰度图，而是强调网络流量矩阵的两个轴并不等价：横向承载单个包内部字段，纵向承载多个包的时序与交互关系。因此，标准 ViT 的方形 patch 会破坏这种语义结构。CL-ViME 用垂直 patching 适配这种各向异性结构，并用 MoE 专家路由处理不同类型的局部模式。

整体结论是：CL-ViME 在 ISCX-VPN、CICIoT2023、CTU-Malware 三个有标签数据集上优于多种自监督和监督基线，尤其在宏平均指标上更稳定，说明它对类别不平衡和少数类更友好。

## 3. 论文解决的具体问题

论文面对的是加密流量分类中的三重困难。

第一，载荷不可见导致传统深度模型很难依赖内容语义。加密后能稳定利用的信息主要来自包头、长度、方向、时序、交互模式等侧信道式特征。

第二，高质量标签稀缺。真实网络流量标注成本高，很多公开数据集又来自虚拟或实验环境，监督学习容易被数据规模、标签质量和场景偏差限制。

第三，已有表示和模型存在结构错配。把流量切成固定字节序列会弱化包边界；转灰度图会引入图像视觉假设；标准 ViT 的方形 patch 假设横纵语义相似，但流量矩阵中横向和纵向分别代表包内字段与包间时序，不能按自然图像方式处理。

因此，CL-ViME 实际解决的问题是：如何在无标签或少标签条件下，构造一种保留包级细节与流级时序的表示，并设计与该表示结构匹配的自监督分类框架。

## 4. 创新点深度提炼

1. 包-时间矩阵表示  
   作者将双向流按五元组聚合并按时间排序，每个包抽取固定 60 字节表示，包括匿名化后的 IP/TCP 头部、选项空间和少量协议控制字段。每个包占一行，最多堆叠成 60×60 矩阵。这个设计把包内字段组织在横轴，把包间时序组织在纵轴，比单纯字节序列或灰度图更符合流量本体结构。

2. 垂直 Vision Transformer-MoE  
   标准 ViT 使用方形 patch，适合自然图像但不适合流量矩阵。CL-ViME 使用垂直条带切分，例如将 60×60 输入按宽度 2 切成 30 个 N×2 patch，使模型沿结构化字段方向保持包序列完整性。MoE 层替代普通前馈网络，让不同专家动态处理不同局部模式。

3. 双粒度正样本构造  
   一路视图来自原矩阵随机 mask，偏流级视角；另一路视图来自转置矩阵再 mask，偏包级视角。转置不是普通图像增强，而是把横纵结构互换，迫使模型学习同一流量在包级和流级两个视角下的一致语义。

4. MoE projector 与路由辅助损失  
   作者不仅在主干里使用 MoE，还在 projector 中用 MoE 将异构视角映射到统一潜空间。辅助损失一方面让同一样本两个增强视图的路由有所差异，增加专家使用多样性；另一方面要求 query encoder 与 momentum target encoder 对同一视图的路由保持一致，稳定训练。

5. 只微调分类头  
   下游阶段冻结预训练 backbone，只训练轻量分类头。这样实验结果更能反映预训练表示质量，而不是依赖全模型监督调参。

## 5. 科学问题与研究假设

科学问题可以概括为：加密流量在缺少明文载荷和标签的条件下，是否仍可通过结构化包头、包序列时序和双粒度自监督约束学习到可泛化表示？

论文隐含了几个关键假设。

第一，加密不会完全抹除可分类信号。包头字段、TCP 选项、协议控制字段、包到达顺序和交互模式仍保留应用或攻击行为的统计指纹。

第二，包级微观特征与流级宏观特征互补。前者更接近协议/实现细节，后者更接近行为过程；单独使用任一粒度都不充分。

第三，流量矩阵具有各向异性，不能直接套用自然图像模型。横轴和纵轴语义不同，模型结构必须尊重这种差异。

第四，MoE 路由可以缓解单一投影器或单一前馈网络对异构流量模式表达不足的问题。

## 6. 科学方法与技术路线

CL-ViME 的技术路线分为三段。

第一段是结构化表示。PCAP 被按五元组重组为双向流，包按时间排序。作者去除 MAC 地址，匿名化源/目的 IP，仅保留 IP 的最后字节片段；TCP 头部统一分配空间，不足补零，过长截断；额外保留 7 字节加密层之后仍可解析的控制字段。最终每个包得到 60 字节，60 个包堆叠成 60×60 包-时间矩阵。

第二段是自监督预训练。对每个矩阵生成两个视图：原矩阵 mask 后作为流级视角，转置矩阵 mask 后作为包级视角。两者构成正样本，batch 内其他样本构成负样本。Vertical ViT-MoE 提取表示，momentum target encoder 提供稳定目标，MoE projector 将两个粒度映射到共同潜空间。

第三段是下游分类。冻结预训练主干，只训练分类头，并使用加权交叉熵处理类别不平衡。这样下游结果主要检验自监督表示的迁移能力。

## 7. 实验设计与实验步骤

可复核流程如下。

1. 数据  
   预训练使用 MAWI 2025 年 1 月 1 日至 1 月 5 日的无标签骨干网流量。有标签评估使用 ISCX-VPN、CICIoT2023 和 CTU-Malware。三者按 8:1:1 划分训练、验证、测试集，并保持类别不平衡分布。

2. 预处理  
   从 PCAP 中按五元组抽取双向流，按时间戳排序；移除 MAC，匿名化 IP；构造每包 60 字节表示；按包到达顺序堆叠为 60×60 矩阵；对不足长度做 padding，对超出长度做截断。

3. 模型/基线  
   表示对比：feature sequence、gray-scale image、packet-temporal matrix。  
   主干对比：ResNet18、AutoEncoder、GNN、ViT、Vertical ViT-MoE。  
   自监督对比：MoCo、SimCLR、BYOL。  
   综合对比：CETP、SmartDetector、MIETT、MTC-MAE、CL-FlowPic、YaTC 等。

4. 训练  
   预训练 300 epochs，学习率 3e-4，batch size 2048，momentum 0.99，AdamW，embedding dimension 120，ViT 12 层。  
   微调 50 epochs，学习率 1e-2，batch size 512，冻结 backbone，仅训练分类头，使用加权交叉熵。

5. 指标  
   使用 Accuracy、Macro-Precision、Macro-Recall、Macro-F1。宏平均指标是重点，因为三个数据集都存在明显类别不平衡。

6. 消融/敏感性  
   消融包括仅 flow-level CL、仅 packet-level CL、双粒度 F&P-CL、F&P-CL+MoE projector。论文还比较了不同表示方式和不同 backbone，但对 λ、mask 比例、专家数量、top-k 等超参数敏感性展示不够充分。

7. 结果核查  
   每个实验重复 30 次，报告均值和标准差。需要重点核查宏平均指标是否与总体 accuracy 同步提升，避免模型只学到多数类。

## 8. 关键结果、结论与证据

表示层面，包-时间矩阵在多数模型和数据集上优于特征序列与灰度图。论文报告在 ISCX-VPN 上，相比 feature sequence 和 gray-scale image，准确率分别提升约 7.02% 和 4.36%，宏精度分别提升约 5.87% 和 3.44%。这支持了“结构化双粒度表示优于粗糙图像化表示”的判断。

模型层面，Vertical ViT-MoE 优于 ResNet18、AutoEncoder、GNN 和普通 ViT。在 CTU-Malware 上，其 Macro-F1 达到 96.02%，比最佳基线 ViT 的 88.67% 高 7.35%。这说明垂直切分和专家路由确实缓解了标准视觉模型的结构错配。

自监督层面，完整 CL-ViME 优于 MoCo、SimCLR、BYOL。CICIoT2023 上 Macro-F1 达到 88.62%，超过 BYOL 的 81.70%。消融中，双粒度通常优于单粒度，加入 MoE projector 后进一步提升，例如 ISCX-VPN accuracy 从 98.75% 升至 99.46%，Macro-F1 从 93.90% 升至 97.94%。

综合性能上，CL-ViME 在 ISCX-VPN、CICIoT2023 上四项指标均第一；在 CTU-Malware 上 accuracy 略低于 CETP，但宏平均指标明显更好。论文强调这说明 CL-ViME 没有单纯偏向多数类，而是在少数类上更稳定。

## 9. 局限性与待解决问题

第一，计算成本偏高。12 层 Transformer、embedding dimension 120、60×60 输入切成多个垂直 patch，再加 MoE 与双编码器对比训练，预训练成本不低。论文也承认未来可用 CNN-based PatchEmbed 降低序列长度和维度。

第二，对概念漂移的处理不足。加密协议、应用行为、攻击策略不断变化，当前模型主要靠一次性预训练和下游微调，尚未纳入持续学习或增量学习机制。

第三，数据外推仍有限。MAWI、ISCX-VPN、CICIoT2023、CTU-Malware 覆盖面较广，但不能代表所有真实企业网、云原生、移动端、QUIC/HTTP3 或新型加密协议场景。

第四，基线复现存在不确定性。论文指出 CETP、MIETT、SmartDetector、CL-FlowPic 等部分模型没有官方源码，作者按论文描述复现，复现实验可能偏离原实现。

第五，方法细节仍需进一步验证。比如保留 7 字节控制字段是否对不同协议普适，60×60 截断是否会丢失长流行为，转置增强是否在所有流量类型上都语义合理，专家数量和路由策略如何影响效果，论文没有展开足够细的敏感性分析。

本次正文包未截断，因此理解覆盖了提供正文的完整内容；但由于没有本地代码，无法验证实现细节与论文描述是否一致。

## 10. 与本项目的关系

这篇论文与“加密流量分类与应用识别”强相关，也能服务“异常检测”和“跨域 AI 安全”方向。

对本项目最有价值的是三个思路：一是把流量表示从粗糙字节序列提升为保留包边界和时序结构的矩阵；二是用自监督预训练缓解安全数据标注不足；三是用宏平均指标和类别不平衡设置评估少数攻击类表现。

如果本项目关注异常检测，CL-ViME 可作为特征学习前端：先在大规模无标签流量上学习表示，再接入异常检测头、开放集检测头或少样本分类器。它尤其适合“有大量 PCAP、少量标签、类别不断变化”的安全场景。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此不能指出真实源码文件。但如果复现 CL-ViME，代码目录大概率应包含以下模块。

- 数据预处理：`pcap_to_flow.py`、`flow_builder.py`、`matrix_encoder.py`  
  负责读取 PCAP、五元组双向流聚合、时间排序、IP/MAC 处理、TCP 头部补齐/截断、生成 60×60 包-时间矩阵。

- 数据增强：`augmentations.py`  
  对应 `Tmask` 和 `Ttrans`，实现随机 mask、矩阵转置、双视图生成、batch 内正负样本组织。

- 模型主干：`vertical_vit_moe.py` 或 `models/cl_vime.py`  
  对应 Vertical Patching、PatchEmbed、CLS token、12 层 Transformer encoder、MoE FFN、top-k expert routing。

- 投影与损失：`moe_projector.py`、`losses.py`  
  对应 MoE projector、predictor、InfoNCE、双向对比损失、MoE routing auxiliary loss、momentum encoder 更新。

- 预训练脚本：`pretrain.py`  
  对应 MAWI 无标签预训练，batch size 2048、epoch 300、lr 3e-4、momentum 0.99。

- 微调与评估：`finetune.py`、`evaluate.py`  
  对应冻结 backbone、训练分类头、加权交叉熵、AdamW、输出 Accuracy/Macro-Precision/Macro-Recall/Macro-F1。

- 配置文件：`configs/*.yaml`  
  应记录数据集路径、矩阵尺寸、patch 宽度、embedding dimension、专家数、top-k、λ、mask 参数、训练轮数等。

真正复现时，最关键的不是模型代码，而是预处理一致性。60 字节字段构成、IP 匿名化策略、TCP option 截断、每条流取前 60 包还是滑窗切片，都会显著影响结果。

## 12. 本篇精华

- CL-ViME 的核心不是“又一个 ViT”，而是把加密流量重新定义为横向包内字段、纵向包间时序的各向异性矩阵。
- 论文认为标准图像增强会破坏流量结构，因此用“转置 + mask”构造包级/流级双视图。
- Vertical patching 是对流量矩阵语义结构的适配：避免方形 patch 混淆包头字段和时序关系。
- MoE 在这里有两层作用：主干中做异构模式提取，projector 中做双粒度潜空间对齐。
- 只训练分类头是一种较干净的验证方式，能更直接说明预训练表示是否有效。
- 在类别不平衡数据上，Macro-F1 比 Accuracy 更可信；CL-ViME 在 CTU-Malware 上的优势主要体现在宏平均指标。
- 主要短板是训练成本、概念漂移适应性和代码不可复核性。
- 对异常检测项目而言，它适合作为无标签流量表征学习模块，而不是只能做闭集应用分类。

## 13. 建议精读路线

1. 先读 Section III-B，彻底弄清 60×60 包-时间矩阵如何构造。这是论文后续所有模型设计的基础。
2. 再读 Section III-C 的双视图构造，重点理解为什么原矩阵代表流级视角、转置矩阵代表包级视角。
3. 接着读 Vertical ViT-MoE，关注 vertical patch 与标准 ViT patch 的差异，不必陷入所有公式细节。
4. 然后读损失函数部分，画出 query encoder、target encoder、MoE projector、predictor、InfoNCE 和 Lmoe 的数据流。
5. 最后读实验表 II、III、IV、V，按“表示有效性、主干有效性、对比学习有效性、综合性能”四个问题检查证据链是否闭合。

<!-- codex-cli-deep-read: complete -->
