# [441] Few-Shot Anomaly Detection via Category-Agnostic Registration Learning

## 1. 基本信息

- 题名：Few-Shot Anomaly Detection via Category-Agnostic Registration Learning，可译为“通过类别无关配准学习的小样本异常检测”。
- 年份与来源：DOI 记录为 2024，论文当前期刊版为 IEEE TNNLS, Vol. 36, No. 7, July 2025。
- DOI：10.1109/TNNLS.2024.3465446。
- 任务类型：工业视觉异常检测与像素级异常定位，属于视觉 FSAD，不是网络入侵检测方法本身。
- 代码：CAReg，已下载到 `source\CAReg`，官方仓库为 `https://github.com/Haoyan-Guan/CAReg`。

## 2. 中文翻译与核心摘要

这篇论文的核心问题是：已有异常检测方法大多是“每个类别训练一个模型”，即使是 few-shot AD，也通常需要针对新类别微调。CAReg 试图改成“一个模型适配所有类别”：训练时只用多个已知类别的正常图像，测试时给定一个新类别的少量正常支持样本，通过比较测试图像与支持样本的配准后特征来发现异常。

方法上，作者把“配准”设计成自监督代理任务：同一类别的正常图像虽然姿态、位置、方向不同，但经过特征级空间变换后应当变得可比较。模型学习的不是某个类别的缺陷模式，而是跨类别可复用的对齐与比较能力。测试时再把支持集特征送入 PaDiM、OAD 或 PatchCore 这类正常分布估计器，测试图像中偏离正常分布的 patch 被判为异常。

## 3. 论文解决的具体问题

论文瞄准的是 few-shot anomaly detection 中三个具体约束同时成立的场景：训练集只有正常样本，没有异常图像和像素标注；测试类别与训练类别完全不重合；每个测试类别只给 2、4 或 8 张正常图像作为支持集。

传统 AD 的困难在于，每个类别的正常外观分布不同，模型往往被迫为每个类别单独训练。TDG、DiffNet 这类早期 FSAD 方法虽然减少了目标类样本需求，但仍然有“目标类微调”或“目标类专用模型”的负担。CAReg 要解决的是更现实的部署问题：新类别来了之后，不重新训练模型，只用少量正常样本即时估计正常分布。

## 4. 创新点深度提炼

第一，论文把异常检测重写为“配准后比较”问题，而不是“学习某类正常外观”问题。这个转换很关键，因为比较本身天然不依赖类别语义。

第二，使用特征级配准而不是像素级配准。工业图像中同类样本的纹理、边缘和局部结构更适合在 CNN 特征空间对齐，像素级严格对齐反而容易被光照、背景、局部变形干扰。

第三，训练阶段采用 SimSiam 风格的 Siamese 注册损失：query 图像特征与支持集聚合特征互相预测，负余弦距离作为目标，并用 stop-gradient 防止表征坍塌。

第四，支持集不是单张参考图，而是 accumulated features，即多张正常支持图像的聚合特征。相比 RegAD 的单参考配准，这更符合 few-shot 场景，也降低支持样本偶然性的影响。

第五，CAReg 被设计为正常分布估计器前面的可插拔特征学习模块。论文分别接 PaDiM、OAD、PatchCore，说明贡献不只是某个打分器，而是更通用的表征增强。

第六，提出按 Wasserstein 距离选择支持集增强。作者没有简单堆叠所有增强，而是剔除会明显改变正常分布的增强，尤其避免对特定类别破坏性过强的变换。

## 5. 科学问题与研究假设

核心科学问题是：只用正常样本训练的模型，能否学到一种跨类别可迁移的“正常样本对齐能力”，使新类别在没有微调的情况下仍可做异常检测？

论文的关键假设包括：同一类别正常样本在合适特征空间中经过空间配准后，其 patch 分布会更紧凑；这种配准能力可从多类别正常图像中学习，并迁移到未见类别；异常区域在配准后仍会偏离由少量正常支持样本估计出的局部分布；支持集增强如果控制得当，可以改善少样本分布估计，而不会引入伪异常模式。

## 6. 科学方法与技术路线

训练阶段，模型从训练类别中采样一张 query 正常图像和同类的 K 张正常支持图像。主干为 ResNet 前三层，并在 C1、C2、C3 后插入 STN 模块，学习旋转、缩放、平移或仿射等空间变换。论文强调保留空间分辨率，因此丢弃 ResNet 最后一层和全局池化。

注册模块采用共享参数的 encoder 和 predictor。query 分支输出 `p_a`，支持集分支先对 K 张图像特征求均值得到聚合特征 `z_B`，损失为双向负余弦相似度：一边让 query 预测支持集聚合特征，另一边让支持集聚合特征预测 query，并在被预测分支停止梯度。

测试阶段，目标类别只提供少量正常支持样本。CAReg 先提取并配准支持集多层特征，再用 PaDiM 的逐位置高斯、OAD 的低秩高斯或 PatchCore 的 coreset memory bank 建模正常分布。测试图像的 patch 特征与正常分布计算距离，形成 anomaly map；图像级分数取 anomaly map 最大值。

## 7. 实验设计与实验步骤

1. 数据：MVTec AD 含 15 类、3629 张训练图像和 1725 张测试图像；MPDD 含 6 类金属零件图像，更强调姿态、位置、光照和背景变化。两者都有像素级缺陷标注用于测试。
2. 划分：采用 leave-one-out。每次选一个类别作为未见测试类别，其余类别只用正常训练图训练 CAReg；目标类别训练图不参与模型训练。
3. few-shot 设置：测试时从目标类别正常训练图中随机选 K 张作为支持集，K 为 2、4、8；每个设置重复 10 次，报告平均 AUC。
4. 预处理：图像 resize 到 224×224；训练主干使用 ImageNet 预训练权重；保留多层空间特征。
5. 模型与基线：FSAD 基线包括 TDG、DiffNet 及其多类别预训练扩展 TDG+、DiffNet+，还比较 RFR、PACKD、PromptAD；正常估计器基线包括 PaDiM、OAD、PatchCore；vanilla AD 上界包括 GANomaly、ARNet、MKD、CutPaste、FYD、PaDiM、PatchCore、CflowAD。
6. 训练：50 epoch，初始学习率 1e-4，cosine 调度，momentum SGD，batch size 32，单张 NVIDIA GTX 3090。
7. 指标：图像级 AD 使用 image-level ROC AUC；像素级定位使用 pixel-level ROC AUC；另外报告 adaptation time、不同支持集下的标准差和 FPR。
8. 消融与敏感性：分别去掉支持集增强、feature registration、STN、accumulated feature；比较不同 STN 自由度；比较固定增强、全部增强、Wasserstein/KL/JS 距离选择；做 MVTec 和 MPDD 跨数据集训练测试。
9. 结果核查：作者用定量表格、异常热图和 t-SNE 三类证据交叉验证：AUC 是否提升、定位是否更贴近 GT、正常特征是否更紧凑且类别间更可分。

## 8. 关键结果、结论与证据

CAReg 在 FSAD 上显著超过既有方法。论文摘要给出的总体结论是：相对当前 FSAD SOTA，MVTec 提升 11.3%，MPDD 提升 8.3%。细分 K=2、4、8 时，相对 FSAD 方法在 MVTec 分别提升 9.6%、12.4%、11.9%，在 MPDD 分别提升 7.1%、9.1%、8.8%。

相对正常分布估计器本身，CAReg 也稳定有效。以 PaDiM 为例，K=2、4、8 时在 MVTec 分别提升 10.8%、11.2%、10.7%，在 MPDD 分别提升 15.2%、14.1%、17.0%。以 PatchCore 为例，MVTec 分别提升 4.4%、4.9%、3.8%，MPDD 分别提升 8.8%、7.9%、7.4%。

效率结论也重要。PaDiM+CAReg 的平均 adaptation time 为 4.47 秒，而 DiffNet+ 为 357.75 秒，TDG+ 为 1559.76 秒。也就是说，CAReg 的优势不只在准确率，还在新类别部署时无需参数微调。

消融证据支持论文的机制解释。feature registration 在 MVTec 上带来约 2.6% 到 3.3% AUC 增益，在 MPDD 上带来约 1.7% 到 4.3% 增益；STN 在 MPDD 这类姿态变化更强的数据上作用尤其明显，K=8 时从 64.8% 提到 71.9%；支持集增强在 MVTec 上提升约 6.8% 到 6.9%。Wasserstein 增强选择还把 K=2 的平均 FPR 从 MVTec 的 5.44% 降到 2.65%，MPDD 的 29.3% 降到 19.8%。

## 9. 局限性与待解决问题

这篇论文仍然是工业视觉异常检测工作，方法高度依赖空间结构、patch 特征和配准假设。对网络流量、日志、系统调用序列这类网络安全数据，不能直接套用 STN 图像配准，需要重新定义“对齐”的对象，例如时间阶段、协议字段、会话状态或图结构节点。

CAReg 仍然依赖目标类别的少量干净正常支持样本。若支持集被污染、覆盖不充分或正常模式本身多峰严重，PaDiM/PatchCore 的估计会受影响。论文通过 accumulated features 和重复采样降低方差，但没有彻底解决支持集代表性问题。

增强选择建立在支持集分布距离上，假设“破坏正常属性的增强会导致较大分布偏移”。这个假设对物体类较合理，对纹理类影响较弱，论文自己的实验也显示纹理类别对增强选择不那么敏感。

代码开源部分与论文完整版方法不完全一致：我在仓库中没有看到 Wasserstein 增强自动选择、OAD 完整实现的清晰入口；当前 `train.py` 主路径实际使用 `wide_resnet50_2` 的 hook 特征和 PatchCore 风格流程，而论文主叙述是 ResNet18 前三层加 STN。若要严格复现实验表格，需要结合补充材料、作者脚本或历史 RegAD 代码进一步核对。

## 10. 与本项目的关系

这篇文章与“入侵检测与网络异常检测”的关系是弱相关，主要提供方法论启发，而不是直接可用的 IDS 算法。它有价值的地方在于：如何在新域只有少量正常样本、没有攻击样本时，训练一个跨类别或跨域可迁移的异常检测前端。

可迁移思想包括：用支持集比较代替类别专用分类；用自监督代理任务学习领域无关表征；用少量正常样本即时估计正常分布；用分布距离筛选数据增强；评估跨数据集泛化而不只看同分布性能。若迁移到网络安全，可把“配准”改造为流量时间窗对齐、协议字段对齐、会话阶段对齐或图节点对应，再接 Mahalanobis、低秩高斯或 memory bank 最近邻打分。

## 11. 代码对照分析

README 很简短，说明代码基于 RegAD，环境安装命令是 `pip install -r requirements.txt`，训练入口是 `python train.py --obj class_name --shot shot_number --data_path_train train_data_path --data_path_test test_data_path`，见 [README.md](F:/泉城实验室/二期/论文/异常检测/source/CAReg/README.md:17)。

数据部分在 [datasets/mvtec.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/datasets/mvtec.py:10)：显式列出 MVTec 15 类和 MPDD 6 类。`FSAD_all_Dataset_train` 会按数据集路径选择类别集合，并从每类 `train/good` 中构造 query/support 对，见 [mvtec.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/datasets/mvtec.py:162)。测试集读取 query、support、mask 和图像级标签，见 [mvtec.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/datasets/mvtec.py:313)。

论文中的 STN 结构保留在 [models/stn.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/models/stn.py:48)：支持 affine、translation、rotation、scale 等模式；ResNet 中在 layer1、layer2、layer3 后插入 `stn1/stn2/stn3`，见 [stn.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/models/stn.py:204)。代码还保存逆变换后的 `stn1_output/stn2_output/stn3_output`，对应论文中把 anomaly map 对齐回原图的思路，见 [stn.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/models/stn.py:252)。

Siamese 注册模块在 [models/siamese.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/models/siamese.py:27)，由 1×1 conv encoder 和 predictor 组成。负余弦与 stop-gradient 在 [losses/norm_loss.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/losses/norm_loss.py:20)：`data2.detach()` 对应论文的 `sg()`。

当前训练入口在 [train.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/train.py:91)。需要注意，主路径把 `stn_net(args)` 注释掉，实际加载 `wide_resnet50_2`，见 [train.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/train.py:153)。`train_patchcore2` 用 layer3 hook 取 query/support 特征，支持集 K 张图像求和平均，再用双向 `CosLoss` 训练，见 [train.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/train.py:433)。

测试中的支持集增强在 [train.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/train.py:586)：包括小角度旋转、平移、水平翻转、灰度化、90 度旋转；具体增强函数在 [utils/funcs.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/utils/funcs.py:37)。PatchCore 流程在 [train.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/train.py:625)：随机投影、k-center coreset、FAISS 最近邻检索和 anomaly map resize/smoothing，对应论文中的 PC 估计器。

PaDiM 风格 Mahalanobis 距离可在 `test.py` 与 `train.py` 的旧测试函数中看到：先拼接多层 embedding，再逐 patch 估计均值/协方差并求 Mahalanobis，距离函数在 [utils/funcs.py](F:/泉城实验室/二期/论文/异常检测/source/CAReg/utils/funcs.py:22)。但 OAD 和 Wasserstein 增强选择在当前代码包中没有清晰实现入口。

## 12. 本篇精华

- CAReg 的本质不是“更强分类器”，而是把 FSAD 转成“新类别 query 与少量正常 support 的配准后比较”。
- 论文最有价值的范式变化是 one-model-all-category：训练时多类别正常样本，测试新类别不微调。
- feature-level registration 是关键，既保留空间定位能力，又避免像素级对齐对光照和细节过敏。
- accumulated support features 比单参考图更符合 few-shot 场景，能降低支持集偶然性。
- CAReg 可接 PaDiM、OAD、PatchCore，说明贡献主要在表征与配准，不绑定某个异常打分器。
- 支持集增强不是越多越好，Wasserstein 距离筛选增强体现了“增强也要服从正常分布”的思想。
- 对网络安全项目的启发在跨域 few-shot 正常建模，但需要重新设计非图像数据上的“配准”定义。

## 13. 建议精读路线

先读 Section III 的问题定义，明确训练类别、测试类别、support set 和 K-shot 约束，否则容易把它误解为普通无监督 AD。

然后读 Section IV，重点看 STN 插入位置、SimSiam 式双向负余弦损失、accumulated features。这是论文真正的新意。

第三步读 Section V，把 PaDiM、OAD、PatchCore 看成三个可替换的正常分布估计器，关注 CAReg 如何给它们提供注册后特征。

第四步读实验中的 Table II、Table VI、Table IX。Table II 看主结果，Table VI 看哪些模块真正有效，Table IX 看跨数据集泛化是否支撑“category-agnostic”主张。

最后对照代码时，优先看 `datasets/mvtec.py`、`models/stn.py`、`models/siamese.py`、`losses/norm_loss.py`、`train.py`。复现前要特别核对当前代码主路径与论文描述的差异，尤其是 `wide_resnet50_2`、PatchCore 路径、固定 support set 文件和未显式开源的增强选择模块。