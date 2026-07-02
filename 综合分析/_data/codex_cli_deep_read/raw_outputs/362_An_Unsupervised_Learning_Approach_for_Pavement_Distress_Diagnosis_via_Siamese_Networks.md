# [362] An Unsupervised Learning Approach for Pavement Distress Diagnosis via Siamese Networks

## 1. 基本信息

- 论文题名：An Unsupervised Learning Approach for Pavement Distress Diagnosis via Siamese Networks
- 作者：Ruiqi Ren, Peixin Shi, Pengjiao Jia, Jinwoo Kim
- DOI：10.1109/TITS.2024.3500030
- 期刊：IEEE Transactions on Intelligent Transportation Systems
- 发表信息：2024 年在线发表，正文页眉为 Vol. 26, No. 2, February 2025
- 研究对象：道路路面病害图像，尤其是裂缝、坑槽、龟裂等细粒度前景目标
- 方法关键词：无监督/自监督表征学习、Siamese network、ViT、自注意力可视化、像素级病害分割
- 本地代码状态：未发现该论文对应的本地开源代码包

## 2. 中文翻译与核心摘要

这篇论文研究的是：在没有人工标注的情况下，能否让模型从大量路面图像中学到足够细的病害表征，并进一步实现像素级病害定位与分割。

作者认为，路面病害诊断的难点不只是“有没有标签”，还在于病害目标本身很细、形态不规则、前景与背景纹理相似。传统监督学习依赖像素级或框级标注，成本高；常见无监督异常检测往往需要先筛选“正常样本”；MAE、BEiT 这类掩码重建方法又容易忽略细长裂缝等小目标。因此，论文提出 SiapaveNet：一种基于 Siamese 网络的预测式自监督框架，用显式 prediction head 和高维 cross-entropy 预测任务来构造隐式类别监督，再借助 ViT 的自注意力图进行无监督像素级病害分割。

核心结果是：SiapaveNet 在 Copave 和 Pavementscapes 数据集上的无监督病害分割优于 f-AnoGAN、GANomaly、FastFlow、MAE、BEiT 等方法；在 Copave 上达到 mDice 0.523、mIoU 0.366、mPA 0.807。进一步地，用 SiapaveNet 预训练 ResNet-50 后迁移到裂缝语义分割、目标检测、实例分割任务，通常比从头训练收敛更快，也能在部分任务上达到或超过 ImageNet 监督预训练的效果。

## 3. 论文解决的具体问题

论文面对的具体问题是：如何在缺乏人工标注的路面图像中，学习能够区分细微病害前景和相似路面背景的表征，并把这种表征转化为像素级诊断结果。

这个问题有三个实际约束：

第一，路面病害标签昂贵。像素级裂缝标注尤其耗时，且不同病害形态复杂，难以大规模覆盖。

第二，病害目标细小、细长、非刚性。裂缝常常只占图像很小区域，MAE 类重建任务可能只学背景纹理而不学裂缝。

第三，异常检测的“正常样本假设”在路面场景中不稳。真实巡检数据通常混有轻微病害、污渍、阴影、修补痕迹，很难干净地筛出正常路面。

所以论文并不是简单做“裂缝检测”，而是在问：能否设计一个更适合路面病害图像的自监督预训练任务，使网络自己形成对病害前景的注意，并用于无监督分割和下游迁移。

## 4. 创新点深度提炼

1. 将路面病害分割从监督学习推进到完全无标签表征学习场景  
   论文不是只做分类或检测预训练，而是尝试直接用自监督训练后的 ViT attention map 做像素级病害分割。这一点比普通“自监督预训练再微调”更进一步。

2. 提出面向路面病害的预测式 Siamese 框架 SiapaveNet  
   它采用双分支增强视图，一支作为较稳定的被预测分支，另一支通过 predictor 去预测前者。相比 MoCo、BYOL、SimSiam、DINO，作者强调 prediction head + cross-entropy + 高维输出更适合捕捉细粒度病害差异。

3. 用高维 cross-entropy 形成隐式类别标签  
   论文的一个关键判断是：路面图像批内背景过于相似，单纯拉近/推远特征或做余弦回归不够。高维 softmax 输出和 CE 损失为模型提供更细的梯度结构，使其不只学习“同图增强一致”，还更容易形成细微模式区分。

4. 将 ViT 自注意力作为无监督分割桥梁  
   作者利用 ViT patch token 间的 self-attention 来定位前景病害。实验中不同 attention head 对病害敏感性不同，最终发现某些 head 更稳定关注裂缝前景。

5. 系统比较无监督表征学习与异常检测路线  
   论文不仅比较 MAE、BEiT，也比较 f-AnoGAN、GANomaly、FastFlow。这个设计有助于说明：路面病害不能简单照搬医学/工业异常检测范式。

6. 证明其预训练可服务下游监督任务  
   SiapaveNet 预训练的 ResNet-50 在语义分割、目标检测、实例分割上提升收敛速度，并在部分任务上优于 ImageNet 预训练，说明它学到的是更贴近路面域的表征。

## 5. 科学问题与研究假设

论文隐含的科学问题可以概括为：

- 在无人工标签条件下，路面病害图像中的细粒度前景是否能通过自监督任务被稳定分离出来？
- Siamese 网络中的预测式分类任务，是否比传统对比、回归或掩码重建任务更适合路面病害表征学习？
- ViT 的 self-attention 是否可以作为无监督像素级分割的可用信号？
- 路面域自监督预训练是否能替代甚至超过 ImageNet 监督预训练？

对应研究假设是：

- 同一图像的不同增强视图之间存在稳定病害语义，预测式 Siamese 学习可以逼迫模型捕获这些稳定结构。
- 病害前景虽然面积小，但其形态与纹理扰动具有一致性，高维 CE 输出能比 MSE、NCS、InfoNCE 提供更强的细粒度区分压力。
- ViT attention head 中会自然出现关注病害前景的头，可被用于无监督分割。
- 面向路面巡检数据预训练得到的表征，比通用自然图像预训练更适合道路病害下游任务。

## 6. 科学方法与技术路线

技术路线可以分成两条：无监督分割路线和下游迁移路线。

无监督分割路线：

1. 从未标注路面图像中采样图像 `x`。
2. 对同一图像做两次随机增强，得到两个视图 `v1` 和 `v2`。
3. 两个视图分别进入共享结构的 backbone，例如 ViT。
4. backbone 输出经过 projection MLP 得到特征向量。
5. 一支网络作为被预测分支，使用 stop-gradient、centering 和 momentum encoder 保持稳定。
6. 另一支网络通过 prediction MLP 去预测被预测分支输出。
7. 对两个 softmax 后的高维输出计算 cross-entropy。
8. 训练完成后，不依赖标注，取 ViT 的 self-attention map 作为病害前景定位依据。
9. 将 attention map 转为像素级或 patch 级分割结果，并用人工标注只在评估阶段计算 mDice、mIoU、mPA。

下游迁移路线：

1. 用 SiapaveNet 在无标签路面图像上预训练 ResNet-50。
2. 将预训练 backbone 迁移到三个监督任务：裂缝语义分割、目标检测、实例分割。
3. 与从头训练、ImageNet 监督预训练进行对比。
4. 观察收敛速度和最终精度。

## 7. 实验设计与实验步骤

**数据**

- Copave dataset：1000 张连续路面大图，来自路面巡检车。
- 预处理后裁剪为 88,088 张 256×256 小图。
- 病害类型包括横向裂缝、纵向裂缝、斜裂缝、龟裂、坑槽等。
- Pavementscapes dataset：同样裁剪预处理，用于验证跨数据集表现。
- 下游任务数据集：
  - Dataset I：裂缝语义分割，1896 张，640×360。
  - Dataset II：目标检测，1538 张，1612×1947。
  - Dataset III：实例分割，133 张，480×320。

**预处理**

- 对连续路面大图裁剪成 256×256 patch。
- 对输入图像做随机增强，生成 Siamese 网络的两个视图。
- 对 Pavementscapes 使用相同裁剪策略以保证可比性。

**模型/基线**

- 主模型：SiapaveNet + ViT，用 self-attention 做无监督分割。
- 迁移模型：SiapaveNet 预训练 ResNet-50。
- 无监督/自监督基线：MAE、BEiT。
- 异常检测基线：f-AnoGAN、GANomaly、FastFlow。
- Siamese 类方法对照：MoCo v3、BYOL、SimSiam、DINO。
- 可解释性分割对照：Grad-CAM、Ablation-CAM、Score-CAM，以及 ResNet-50 的 Grad-CAM。

**训练**

- GPU：A40。
- batch size：64。
- optimizer：AdamW。
- learning rate：0.0005。
- momentum parameter：0.996。
- 对 ViT 训练时，AdamW 明显优于 SGD；SGD 在该设置下 loss 不下降。
- 对 CNN/ResNet-50，下游部分显示 SGD 仍可有效。

**指标**

- 无监督分割：mDice、mIoU、mPA。
- 下游语义分割：mIoU。
- 下游目标检测与实例分割：mAP。

**消融/敏感性**

- 比较 MoCo v3、BYOL、SimSiam、DINO 和 SiapaveNet。
- 比较 predictor 的 MLP 层数，3 层效果最佳。
- 比较 prediction head 输出维度，较大维度能学习更细信息，但计算开销增加。
- 比较是否使用 batch normalization，本文模型中 prediction head 去掉 BN 更好。
- 比较 InfoNCE、NCS、CE，CE 最适合该框架；InfoNCE 在最优设置下出现表示坍塌。
- 比较 centering，加入 centering 后模型性能明显增强。
- 比较 SGD 和 AdamW，ViT 上 AdamW 收敛更好。

**结果核查**

- Copave 上 SiapaveNet 明确给出 mDice 0.523、mIoU 0.366、mPA 0.807。
- FastFlow 虽有较高 mPA，但视觉效果差，说明 mPA 在小目标背景占优时可能虚高。
- BEiT 通常是次优方法之一，说明 Transformer 表征对该任务有帮助，但单纯掩码预测不如 SiapaveNet。
- ViT attention 的不同 head 关注区域不同，论文选择更稳定关注前景的 head 用于分割。
- 下游任务中，SiapaveNet 预训练比从头训练更快收敛；与 ImageNet 预训练相比，在语义分割和实例分割上有竞争力，在目标检测上略弱。

## 8. 关键结果、结论与证据

最关键的实验证据有三组。

第一，像素级无监督病害分割有效。  
在 Copave 数据集上，SiapaveNet 达到 mDice 0.523、mIoU 0.366、mPA 0.807，整体优于异常检测方法和通用自监督方法。视觉结果显示，它能更准确地沿裂缝和病害区域聚焦，而不是只给出粗糙轮廓或大块背景响应。

第二，ViT self-attention 比 CNN 可解释性热图更适合此任务。  
Grad-CAM 类方法在 CNN 上只能给出较模糊的关注区域，难以贴合细裂缝形态；ViT 的部分 attention head 能更细地落在病害前景上。这说明论文方法的分割能力并不完全来自 Siamese 预训练，也依赖 ViT attention 的空间结构。

第三，路面域自监督预训练具有迁移价值。  
SiapaveNet 预训练的 ResNet-50 在三个下游任务中都比从头训练收敛更快。在小样本实例分割任务中，论文尤其强调无监督预训练优势明显。这支持了作者的判断：路面域内无标签数据能提供比通用 ImageNet 更贴近任务的先验。

总体结论是：对于路面病害这种小目标、细粒度、背景相似的场景，预测式 Siamese 自监督学习比传统异常检测和掩码重建更有针对性；但它目前更像一个有潜力的研究基线，而不是已经完全成熟的工程系统。

## 9. 局限性与待解决问题

1. 无监督分割精度仍有限  
   mDice 0.523、mIoU 0.366 说明方法确实有效，但离可靠工程级像素分割仍有距离。尤其在裂缝极细、背景纹理复杂、阴影/污渍干扰明显时，attention map 可能仍不稳定。

2. attention head 选择带有经验性  
   论文发现某些 self-attention head 更关注前景，并选择其中一个 head 用于分割。但这仍像是经验选择，缺少自动 head selection 或多 head 融合机制。

3. “无监督”表述需要审慎理解  
   训练过程不使用人工标签，但评估依赖标注 mask；异常检测基线也存在不同程度的正常样本筛选假设。因此论文的贡献更准确地说是自监督表征学习驱动的无标签训练，而不是完全脱离标注体系的闭环诊断。

4. 对病害类别区分讨论不足  
   论文主要强调前景分割，没有充分展示横裂、纵裂、龟裂、坑槽等不同病害类型的无监督类别发现能力。对于养护决策而言，仅有前景 mask 还不够。

5. 数据规模仍偏小  
   Copave 裁剪后有 88,088 张 patch，但原始大图只有 1000 张，与 COCO 等大规模视觉数据相比仍有限。作者也承认未来需要更大、更全面的数据和合成数据增强。

6. 与真实部署之间还有差距  
   巡检车图像可能存在光照、雨水、污渍、修补、路面材质差异等复杂因素。论文证明了方法潜力，但没有充分覆盖跨城市、跨设备、跨季节的稳定性。

7. 本次理解基于提供的正文包  
   正文包标注为未截断，因此没有明显缺页问题；但表格中的若干具体数值在文本抽取中未完整呈现，若要做严格复现实验或综述引用，仍建议回到 PDF 复核 Table I 到 Table VIII 的完整数值。

## 10. 与本项目的关系

从已有分类看，该文被归到“多媒体、医学、遥感与视频异常检测”，但和一般视频异常检测或工业异常检测的关系较弱，更准确的关联是：基础设施视觉巡检中的无监督异常/缺陷分割。

如果本项目关注通用异常检测，这篇论文的价值在于提供了一个领域适配案例：异常不一定适合“只用正常样本建模”，也可以通过自监督表征和 attention 可视化获得前景定位。

如果本项目关注道路、桥梁、隧道等基础设施病害识别，这篇论文更有参考价值。它说明在标注昂贵的工程巡检场景中，可以先用无标签数据做领域预训练，再用于少样本监督任务。

如果本项目关注医学或遥感异常检测，该文的直接相关性较弱，但方法思想可迁移：当异常目标细小、背景相似、标签稀缺时，prediction head + 高维 CE 的 Siamese 自监督任务可能比掩码重建更适合。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此无法进行逐文件验证。根据论文方法，若后续找到代码，重点应查找以下模块：

- 数据预处理  
  可能对应 `datasets/`、`data/`、`preprocess.py`、`crop.py` 等文件。应包含连续路面大图裁剪为 256×256 patch、Pavementscapes 同尺度处理、数据增强策略。

- 模型主体  
  可能对应 `models/siapavenet.py`、`models/vit.py`、`models/resnet.py`。核心应包括 backbone `f`、projection MLP `g`、prediction MLP `q`，以及 momentum encoder 分支。

- 损失函数  
  可能对应 `losses.py` 或 `criterion.py`。应能看到 softmax temperature、stop-gradient、centering、高维 cross-entropy 的实现。

- 训练脚本  
  可能对应 `train_siapavenet.py`、`main_pretrain.py`。应包含 AdamW、batch size 64、learning rate 0.0005、momentum 0.996，以及中心向量 EMA 更新。

- 无监督分割/可视化  
  可能对应 `attention_vis.py`、`infer_seg.py`、`visualize.py`。重点是提取 ViT attention head，并将 attention map 转成病害 mask。

- 下游任务  
  可能对应 `finetune_seg.py`、`finetune_det.py`、`finetune_instance.py`。应包含 ResNet-50 预训练权重加载、语义分割 mIoU、检测/实例分割 mAP 评估。

- 消融实验  
  可能对应 `configs/ablation/`。应包含不同 MLP 层数、输出维度、BN、loss、centering、optimizer 的配置。

当前只能依据论文正文做方法-代码结构映射，不能确认作者实现细节、随机种子、阈值策略、attention head 选择逻辑或评估脚本是否与论文完全一致。

## 12. 本篇精华

1. 这篇论文的核心不是提出一个更强的裂缝监督分割器，而是证明无标签路面图像也能训练出可用于像素级病害定位的表征。

2. 路面病害的难点在于小目标、细长形态和背景相似，导致 MAE 类重建任务可能学背景，异常检测方法又依赖不可靠的正常样本筛选。

3. SiapaveNet 的关键组合是 prediction head、高维 cross-entropy、momentum encoder、stop-gradient、centering，以及无 BN 的 predictor。

4. 作者认为 prediction head + CE 比 InfoNCE、MSE、NCS 更适合捕捉路面病害的细粒度差异，这是论文最值得借鉴的方法判断。

5. ViT self-attention 是从自监督表征走向像素级分割的桥梁，但不同 attention head 差异明显，head 选择仍是潜在薄弱点。

6. Copave 上 SiapaveNet 的 mDice 为 0.523、mIoU 为 0.366、mPA 为 0.807，优于多种无监督表征和异常检测基线。

7. 作为预训练方法，SiapaveNet 对下游裂缝语义分割、目标检测、实例分割都有帮助，尤其在小样本任务中显示出比 ImageNet 预训练更贴近路面域的优势。

8. 论文更适合作为“无监督基础设施病害诊断”的研究起点，而不是可直接部署的工程终点。

## 13. 建议精读路线

1. 先读 Introduction 的问题定义  
   重点看作者如何区分监督学习、生成式无监督学习、Siamese 表征学习和异常检测方法的局限。

2. 精读 Section III-A 和 Algorithm 1  
   这是方法核心。需要弄清楚两个分支、projection、prediction、stop-gradient、softmax CE、centering 的关系。

3. 对照 Section III-C 理解 ViT attention 分割  
   注意论文并没有训练一个传统 decoder，而是利用 self-attention map 做无监督前景定位。

4. 精读 Table I、Table II 和 Figure 3、Figure 4、Figure 5  
   这些结果能判断方法到底比异常检测和 MAE/BEiT 强在哪里，以及 attention head 的选择是否可靠。

5. 读 Section IV-B 看迁移学习价值  
   这里体现论文对实际标注稀缺场景的意义：无监督预训练不是只为分割，还能提升下游监督任务。

6. 最后读 Ablation Study  
   优先关注 Table III 到 Table VIII：predictor、loss、BN、centering、optimizer 的消融是复现和改进这篇工作的关键。