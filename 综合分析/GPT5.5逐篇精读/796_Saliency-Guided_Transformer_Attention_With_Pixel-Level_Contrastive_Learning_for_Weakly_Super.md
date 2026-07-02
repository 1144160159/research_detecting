# [796] Saliency-Guided Transformer Attention With Pixel-Level Contrastive Learning for Weakly Supervised Defect Localization

## 1. 基本信息

- 论文题名：Saliency-Guided Transformer Attention With Pixel-Level Contrastive Learning for Weakly Supervised Defect Localization
- 作者：Dejene M. Sime, Nan Ouyang, Kai Sheng 等
- 来源：IEEE Transactions on Industrial Informatics
- DOI：10.1109/TII.2025.3648429
- 发表信息：正文显示 accepted 为 2025-12-21，online publication 为 2026-01-15，current version 为 2026-04-06；用户元数据年份为 2025，可理解为 DOI/录用年份。
- 任务类型：弱监督工业缺陷定位与分割，只用图像级标签生成 CAM，再用 CAM 伪标签训练分割网络。
- 代码：STAC，已下载到 `source\STAC`。我已检查 README、主训练、模型、损失、数据集、评估和分割目录。

## 2. 中文翻译与核心摘要

这篇论文研究的是：在工业表面缺陷场景中，如果只有图像级缺陷类别标签，而没有像素级标注，如何仍然生成足够准确的缺陷定位图和伪分割标签。传统 CAM 方法常能把图像分类做对，却把热力图激活到背景、纹理或无关区域；这种“分类正确但定位错误”的矛盾，在低对比、形状不规则、边界模糊、类间相似和类内变化大的工业缺陷图像中尤其严重。

作者提出 STAC：用 Transformer 的 class-to-patch attention 生成类别相关定位图，再用 patch embedding 上的 CNN 辅助 CAM 进行细化，并引入外部显著性图约束前景/背景分离。进一步，利用逐步细化的 CAM 选取高置信像素，做像素级对比学习，让同类缺陷像素特征靠近、不同类或背景特征分开。最后，生成的 CAM/伪标签用于训练 DeepLabV3+、SegFormer 等分割网络。

论文最核心的观点是：工业缺陷弱监督分割不能只依赖分类 CAM，需要同时补足三类信息：全局上下文、前景/背景边界提示、像素级表征可分性。

## 3. 论文解决的具体问题

论文针对的不是一般异常检测，而是工业视觉缺陷的弱监督定位/分割。具体问题包括：

- 图像级标签过于稀疏：标签只告诉“这张图有某类缺陷”，不告诉缺陷在哪里。
- CAM 与分类目标错位：分类网络会抓住最有判别力的小区域，甚至抓住背景纹理，导致高分类置信度不等于正确定位。
- 工业缺陷比自然物体更难：缺陷边界低对比、不规则、局部细小，且同一类别内部差异大，不同类别之间又可能形态相似。
- 多类别激活重叠：不同缺陷类别可能激活相同背景或纹理区域，造成 co-occurrence/overlapping activation。
- 伪标签质量不足会传导到第二阶段分割网络：CAM 如果噪声大，后续 DeepLabV3+ 或 SegFormer 训练也会被错误监督拖累。

## 4. 创新点深度提炼

1. **把 Transformer class token 与 patch token 的注意力直接用于类别定位**  
   方法不是简单拿 CNN 最后一层 CAM，而是在 DeiT 中为每个类别设置 class token，从 pairwise attention 中取 class-to-patch attention，形成类别特异的定位图。

2. **Transformer attention 与 patch embedding CAM 相乘细化**  
   Transformer attention 提供全局关系，patch embedding 经 CNN head 得到辅助 CAM，二者逐元素相乘得到更聚焦的 `Aref`。这相当于用全局上下文约束局部激活。

3. **显著性图只解决“前景在哪里”，分类分支解决“是哪一类”**  
   PFAN 生成的 saliency map 是 class-agnostic 的前景提示。论文没有把它当作最终标签，而是用 MSE 约束所有前景类 CAM 的和，让模型学会前景/背景分离。

4. **CAM 引导的像素级对比学习**  
   论文用 refined CAM 生成高置信伪像素标签，再在 projection feature map 上构造正负样本：同类像素靠近，异类/背景像素远离。这直接针对工业缺陷中的类间混淆和边界模糊。

5. **同时验证 CAM、分割、泛化和复杂度**  
   论文不只报告 CAM mIoU，还用伪标签训练分割网络，并在 PASCAL VOC 与 MVTec 上测试跨域泛化；同时给出参数量、MACs、FPS 和显存。

## 5. 科学问题与研究假设

**科学问题：**  
在只有图像级标签的工业缺陷数据中，能否通过 Transformer attention、显著性先验和像素级对比学习，弥补分类监督与像素级定位之间的监督鸿沟？

**核心假设：**

- Transformer 的 class-to-patch attention 比 CNN CAM 更适合捕获缺陷区域与全局上下文的关系。
- 类别无关 saliency cue 虽不能区分类别，但能稳定提供前景/背景边界约束。
- 由 CAM 动态生成的高置信像素对，足以支持对比学习改善特征空间结构。
- 对工业缺陷而言，提升 CAM 质量比单纯提高分类精度更关键，因为多数方法分类 mAP 已接近饱和，但定位 mIoU 仍低。

## 6. 科学方法与技术路线

整体路线是“两阶段弱监督分割”：

1. **STAC 训练阶段**  
   图像被切成 patch，输入 DeiT；每个类别有一个 class token。Transformer 输出 class token embedding、patch embedding 和多层 attention。

2. **类别定位图生成**  
   从 pairwise attention `Apa` 中取类别 token 到 patch token 的子矩阵，得到 `Aca`。跨层聚合后形成 Transformer attention CAM。

3. **PEM 辅助细化**  
   patch embedding reshape 成空间特征图，经 3×3 CNN head 输出 class-specific CAM；与 Transformer attention 相乘，得到 refined CAM。

4. **显著性监督**  
   refined CAM 上采样到原图大小，按类别归一化并求和，得到类别无关前景响应，与 PFAN saliency map 做 MSE。

5. **像素级对比学习**  
   PCM/projection head 将 patch feature 投影到 256 通道并上采样到 224×224。CAM 与 saliency 生成伪像素标签和 mask，`pico_loss.py` 中用类原型作为正样本、其他类像素作为负样本做 ReCo 风格对比学习。

6. **分割网络训练阶段**  
   生成 `.npy` CAM 或 CRF 后处理伪标签，再训练 DeepLabV3+、SegFormer 等分割模型，最终用真实测试 mask 评估 mIoU。

## 7. 实验设计与实验步骤

可复核流程如下：

1. **数据**  
   NEU-Seg：3630 train，840 test，钢带缺陷。  
   DAGM：选取 6 个缺陷类，1080 train，270 test。  
   MTD：5 类磁瓦缺陷，仿射增强到 980 train，190 test。  
   PASCAL VOC2012：10582 train，1449 val。  
   MVTec：Bottle、Carpet、Grid、Hazelnut、Leather 五类。

2. **预处理**  
   缺陷图像 resize 到 224×224；VOC 使用 448×448 random resize/crop。训练使用随机增强。显著性图由预训练并微调的 PFAN 生成，论文还提到 CRF 和后处理提高一致性。

3. **模型/基线**  
   主模型为 DeiT-S backbone 的 STAC。对比方法包括 EPS、SEAM、P2P、L2G、AuxSNet、T-CAM、MCT+、ToCo、CTFA、CTI、SeCo 等。分割阶段使用 DeepLabV3+、SegFormer、Wide-ResNet 等。

4. **训练**  
   论文写 defect localization 训练 100 epochs，Adam，base LR 1e-3；VOC 用 1e-4。batch size：缺陷 16，VOC 4。损失为分类损失、saliency MSE、contrastive loss 加权和。

5. **指标**  
   CAM 和分割均用 mIoU；CAM 还报告 FP/FN。CAM 测试使用多尺度 `[1.0, 0.5, 1.5, 2.0]`。

6. **消融/敏感性**  
   检查 PEM、saliency、contrastive learning 各组件贡献；比较 CNN 与 Transformer 实现；考察 Transformer layer depth、CAM threshold、query/key sampling、loss 权重 λ/γ、backbone 复杂度。

7. **结果核查**  
   CAM 先由 `main.py --gen_attention_maps` 输出 `.npy`，再用 `evaluation.py` 以背景阈值 `t` 与各类 CAM 做 argmax 计算 mIoU。分割结果需把 CAM/CRF 伪标签转为 mask，再由 `segmentation/train_model_seg.py` 或相关脚本训练分割模型。

## 8. 关键结果、结论与证据

- CAM 定位上，STAC 在三个工业数据集都最好：NEU-Seg test mIoU 74.71，DAGM test 66.53，MTD test 67.17。对应第二名通常低 6 到 20 个点不等，说明提升主要来自定位质量，而非分类精度。
- PASCAL VOC2012 上，STAC CAM mIoU 为 64.48，高于 baseline 60.68、Base+CON 62.89、Base+SAL 63.21，也略高于 MCT+ 的 63.72；但提升幅度小于工业缺陷场景，符合作者判断：自然物体预训练模型本身已有较强定位先验。
- MVTec 上，Transformer 版本 STAC-T 明显优于 Base-T 和 STAC-CNN。例如 Bottle mIoU 88.04，Carpet 79.15，Hazelnut 86.49，Leather 74.09；CNN 版本更容易出现非缺陷区域误激活。
- NEU-Seg 分割阶段，使用 STAC 伪标签训练的最佳 DeepLabV3+ EffNet-B4 mean mIoU 为 78.40，高于 WDLS 69.77 和 PLDL 74.33，但仍低于 fully supervised 的 85.90。
- DAGM/MTD 分割结果也支持伪标签有效性：DAGM test 最高 66.40，MTD test 最高 68.90。
- 复杂度上，STAC 为 21.75M 参数、4.29G MACs、283 FPS、156MB 显存；比 T-CAM 和 EPS 更轻，具备一定实时工业检测潜力。

## 9. 局限性与待解决问题

- 方法依赖外部 saliency map。虽然训练监督名义上是图像级标签，但 PFAN 显著性图提供了额外前景先验；saliency 质量差时，STAC 的前景/背景学习会受影响。
- MVTec 设置存在可讨论之处：论文说用 test set 中的缺陷样本做空间增强后加入训练，再在原始缺陷样本上报告结果。这对标准无监督异常检测范式可能引入测试分布信息泄漏风险。
- failure case 仍集中在低对比、边界不清、类内变化大的类别，如 NEU-Seg 的 Inclusion，以及 MTD 的 Blowhole、Crack、Uneven。
- 代码复现不够工程化：多处类别数、数据集导入和阈值需要手动改。`main.py` 当前直接 `from datasets_neu import build_dataset`，DAGM/MTD/MVTec 需要切换对应 dataset 文件；`engine_STAC.py` 中 `cam_labels(..., 3)`、`label_onehot(label, 4)` 等也写死了 NEU 配置。
- 正文包标注未截断；但部分表格在纯文本中是图片形式，表 VI/VII 的完整逐项数值未在正文文本中展开，若要复核所有消融精确数字，仍建议回到 PDF 表格逐项核对。

## 10. 与本项目的关系

已有粗分类为“其他AI安全与跨域异常检测”，相关性弱是合理的。本文不是网络安全异常检测，也不是日志、流量或主机行为异常检测；它主要是工业视觉缺陷定位。

对本项目的可迁移价值在方法思想：

- 弱标签异常定位：只有样本级异常/类别标签时，如何定位到局部区域或局部片段。
- 注意力可解释性校正：分类正确不代表定位正确，这一点对安全告警、时间序列异常解释同样成立。
- 显著性/先验 + 对比学习：可以类比为用外部规则、专家先验或粗粒度异常分数引导 token/事件级表示学习。
- 伪标签闭环：先生成粗定位，再训练下游精细模型，是弱监督异常检测中可借鉴的路线。

但直接复用难度较高，因为本文的 saliency、CAM、CRF、像素级对比都建立在图像二维结构上。

## 11. 代码对照分析

核心文件对应关系如下：

- README 与运行线索：[README.md](<F:\泉城实验室\二期\论文\异常检测\source\STAC\README.md>)  
  说明流程是训练 STAC、评估 CAM、用 CAM 伪标签跑 segmentation pipeline。

- 主入口：[main.py](<F:\泉城实验室\二期\论文\异常检测\source\STAC\main.py>)  
  负责参数、数据集构建、创建 `deit_small_STAC`、加载 DeiT 预训练权重、训练、评估和 `--gen_attention_maps` 推理。

- 模型定义：[model_STAC.py](<F:\泉城实验室\二期\论文\异常检测\source\STAC\model_STAC.py>)  
  `STAC` 继承 `VisionTransformer`。这里能看到多类别 `cls_token`、patch positional embedding、CNN CAM head、projection head、class-to-patch attention 聚合，以及 `return_att=True` 时输出 CAM。

- 训练与 CAM 生成：[engine_STAC.py](<F:\泉城实验室\二期\论文\异常检测\source\STAC\engine_STAC.py>)  
  `train_one_epoch` 中组合 `multilabel_soft_margin_loss`、saliency MSE、`compute_pico_loss`。`generate_attention_maps_ms` 做多尺度 CAM 输出 `.npy` 和可视化 `.png`。

- 像素级对比损失：[pico_loss.py](<F:\泉城实验室\二期\论文\异常检测\source\STAC\pico_loss.py>)  
  ReCo 风格实现：按伪标签取有效像素，计算类原型，采样 hard query 和 negative keys，用 cosine similarity + cross entropy 做对比。

- 数据处理：[datasets_neu.py](<F:\泉城实验室\二期\论文\异常检测\source\STAC\datasets_neu.py>)、`datasets_dagm.py`、`datasets_mtd.py`、`datasets_mvtec.py`  
  对应不同数据集的 image list、`.npy` 图像级标签、`JPEGImages/SALmapsALL` 等目录读取。

- 评估：[evaluation.py](<F:\泉城实验室\二期\论文\异常检测\source\STAC\evaluation.py>)、`evaluation_mvtec.py`  
  把 CAM dict 转为类别通道，背景通道设为阈值 `t`，argmax 后与 GT mask 计算 IoU、FP、FN。

- 分割阶段：[segmentation](<F:\泉城实验室\二期\论文\异常检测\source\STAC\segmentation>)  
  `dataloader_seg.py` 读图像和 mask；`train_model_seg.py` 训练 DeepLabV3+/DEITMIX 等；`infer_seg.py` 做分割评估。注意 `run_SATC_seg.sh` 中出现 `./STAC/seg/...`，而本地目录名是 `segmentation`，脚本可能需要改路径。

- CNN 对照：[STAC-CNN](<F:\泉城实验室\二期\论文\异常检测\source\STAC\STAC-CNN>)  
  包含 ResNet38 CAM、EPS/saliency 分支和同类 `pico_loss.py`，更像论文里 CNN-based variant 和补充对照实现。

## 12. 本篇精华

1. 工业缺陷弱监督定位的核心矛盾是：分类置信度高不等于 CAM 定位正确。
2. STAC 的关键不是单一模块，而是 Transformer attention、显著性前景约束、像素级对比学习三者互补。
3. class-to-patch attention 给出类别相关全局定位，PEM 用 patch embedding 产生局部 CAM，再相乘抑制无关激活。
4. saliency map 在这里不是类别标签，而是前景/背景分离器；类别归属仍由图像级标签和 class token 学习。
5. pixel-level contrastive learning 针对的是工业缺陷中最难的类间相似和类内变化问题。
6. 结果显示，STAC 对工业缺陷数据提升远大于 VOC，说明该方法确实更贴近工业缺陷的弱监督痛点。
7. 复现时要特别小心代码里的硬编码类别数、数据集导入、loss 权重和阈值设置。
8. 对异常检测综述而言，本文适合归入“弱监督视觉异常/缺陷定位”而不是通用网络安全异常检测。

## 13. 建议精读路线

1. 先读 Introduction 的 Fig. 1，抓住“分类正确但定位错误”这个问题动机。
2. 再读 Fig. 3 和 Section III-A/B，理解 class token、patch token、class-to-patch attention 如何产生 CAM。
3. 重点读 Section III-C/E：PEM、saliency loss、contrastive loss 是真正让方法区别于 MCT+、T-CAM 的地方。
4. 对照 Table I 看 CAM mIoU，这是本文最有说服力的主结果。
5. 再看 Table IV/V，理解 CAM 伪标签如何传递到第二阶段分割网络。
6. 最后读 ablation：组件、layer depth、threshold、query/key sampling、loss 权重和复杂度，判断方法是否稳定。
7. 若要复现，先跑 NEU-Seg 单数据集；确认 `.npy` CAM、`evaluation.py` mIoU 和 segmentation mask 流程后，再扩展到 DAGM/MTD。

<!-- codex-cli-deep-read: complete -->
