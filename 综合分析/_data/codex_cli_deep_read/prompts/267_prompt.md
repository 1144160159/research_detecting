你是使用 GPT-5.5 的资深网络安全与异常检测论文精读助手。请真正阅读下面提供的论文正文包和代码包，理解后输出一篇中文深度解析 Markdown。

重要要求：
1. 不要用模板化空话，不要说“程序自动抽取显示”。你需要像研究员读完论文后写读书笔记一样表达。
2. 必须围绕正文内容提炼：具体问题、创新点、科学问题、研究假设、科学方法、实验步骤、关键结论、局限与待解决问题。
3. 如果代码包存在，请把论文方法与代码目录、关键文件、运行线索对应起来，指出哪些源码文件可能对应数据预处理、模型、训练和评估。
4. 如果正文包被截断，必须在“局限性与待解决问题”中说明：本次理解基于提供的正文包，仍需回到 PDF 复核被截断部分。
5. 不要长篇复制英文原文。可以短引极少量关键词，但主体必须是中文理解和分析。
6. 输出必须是完整 Markdown，且必须包含下面 13 个二级标题，标题文字不得改名。
7. “实验设计与实验步骤”要写成可复核流程：数据、预处理、模型/基线、训练、指标、消融/敏感性、结果核查。
8. “本篇精华”要给出 5-8 条高密度要点，能直接服务综述或科研汇报。

必须使用的文档结构：
# [267] Multimodal Brain Tumor Segmentation Boosted by Monomodal Normal Brain Images
## 1. 基本信息
## 2. 中文翻译与核心摘要
## 3. 论文解决的具体问题
## 4. 创新点深度提炼
## 5. 科学问题与研究假设
## 6. 科学方法与技术路线
## 7. 实验设计与实验步骤
## 8. 关键结果、结论与证据
## 9. 局限性与待解决问题
## 10. 与本项目的关系
## 11. 代码对照分析
## 12. 本篇精华
## 13. 建议精读路线

元数据：
编号：267
题名：Multimodal Brain Tumor Segmentation Boosted by Monomodal Normal Brain Images
年份：2024
DOI：10.1109/tip.2024.3359815
来源：IEEE Transactions on Image Processing
PDF：paper/10.1109_TIP.2024.3359815.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：无
相关性：弱相关，分数 1
已有代码状态：候选不可访问；Normal-BrainBoost-Tumor-Segmentation

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\267.txt
- 原始字符数：51661
- 本次发送字符数：51661
- 是否截断：False

代码包：
- 仓库：Normal-BrainBoost-Tumor-Segmentation
  - URL：https://github.com/hb-liu/Normal-BrainBoost-Tumor-Segmentation
  - 状态：failed
  - 本地目录：source\Normal-BrainBoost-Tumor-Segmentation
  - 顶层结构：
  - 主要语言：
  - README 标题：
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 33, 2024

1199

Multimodal Brain Tumor Segmentation Boosted by
Monomodal Normal Brain Images
Huabing Liu , Zhengze Ni , Dong Nie , Dinggang Shen , Fellow, IEEE, Jinda Wang, and Zhenyu Tang

Abstract— Many deep learning based methods have been
proposed for brain tumor segmentation. Most studies focus on
deep network internal structure to improve the segmentation
accuracy, while valuable external information, such as normal
brain appearance, is often ignored. Inspired by the fact that
radiologists often screen lesion regions with normal appearance
as reference in mind, in this paper, we propose a novel deep
framework for brain tumor segmentation, where normal brain
images are adopted as reference to compare with tumor brain
images in a learned feature space. In this way, features at
tumor regions, i.e., tumor-related features, can be highlighted
and enhanced for accurate tumor segmentation. It is known
that routine tumor brain images are multimodal, while normal
brain images are often monomodal. This causes the feature
comparison a big issue, i.e., multimodal vs. monomodal. To this
end, we present a new feature alignment module (FAM) to
make the feature distribution of monomodal normal brain
images consistent/inconsistent with multimodal tumor brain
images at normal/tumor regions, making the feature comparison effective. Both public (BraTS2022) and in-house tumor
brain image datasets are used to evaluate our framework.
Experimental results demonstrate that for both datasets, our
framework can effectively improve the segmentation accuracy
and outperforms the state-of-the-art segmentation methods.
Codes are available at https://github.com/hb-liu/Normal-BrainBoost-Tumor-Segmentation.
Index Terms— Brain tumor segmentation, normal brain
images, normal reference, feature alignment, BraTS2022 dataset.

I. I NTRODUCTION

S

EGMENTATION of brain tumor from multimodal magnetic resonance (MR) images is an essential task for

Manuscript received 20 August 2022; revised 16 July 2023 and 28 December
2023; accepted 24 January 2024. Date of publication 5 February 2024; date
of current version 7 February 2024. This work was supported in part by the
National Natural Science Foundation of China under Grant 62073012 and
in part by the Beijing Municipal Natural Science Foundation under Grant
7222307. The associate editor coordinating the review of this manuscript and
approving it for publication was Dr. Christophoros Nikou. (Huabing Liu and
Zhengze Ni contributed equally to this work.) (Corresponding authors: Zhenyu
Tang; Jinda Wang.)
Huabing Liu, Zhengze Ni, and Zhenyu Tang are with the School of
Computer Science and Engineering, Beihang University, Beijing 100191,
China (e-mail: tangzhenyu119@hotmail.com).
Dong Nie is with the Department of Computer Science, University of North
Carolina at Chapel Hill, Chapel Hill, NC 27599 USA.
Dinggang Shen is with the State Key Laboratory of Advanced Medical
Materials and Devices, School of Biomedical Engineering, ShanghaiTech
University, Shanghai 201210, China, also with Shanghai United Imaging Intelligence Co., Ltd., Shanghai 200230, China, and also with the Shanghai Clinical Research and Trial Center, Shanghai 201210, China (e-mail: Dinggang.
Shen@gmail.com).
Jinda Wang is with the Sixth Medical Center of PLA General Hospital, Senior Department of Cardiology, Beijing 100853, China (e-mail:
wjd301@163.com).
Digital Object Identifier 10.1109/TIP.2024.3359815

subsequent diagnosis and treatment. Due to the inter-subject
variance of brain tumors in location, shape, and appearance,
accurate tumor segmentation is a challenging task.
With the advance of deep learning (DL), many brain
tumor segmentation methods [1], [2], [3], [4], [5], [6], [7],
[8] using various DL networks have been proposed, e.g.,
3D convolutional neural network (CNN) [2], U-Net [9],
and Transformer [10]. Although they have shown promising
results, most of them try to improve the learning capacity of
tumor-related features by elaborating deep network’s internal
structure. However, valuable external information, such as
normal brain appearance, is usually ignored or underutilized.
It is known that radiologists are usually first trained with
normal samples before performing robust screening of lesion
regions. Following this observation, anomaly detection has
arisen for lesion region segmentation [11], [12], [13], [14].
The basic idea is to compare images containing lesion regions
(e.g., tumor brain images) with their normal appearance reconstructed by autoencoder [15], in this way, lesion regions can be
highlighted and relatively easy to be segmented. For example,
Baur et al. [11] utilized a deep spatial autoencoder to reconstruct normal brain images from input tumor brain images.
Then, brain tumors can be segmented using thresholding on
the residual images produced by the tumor brain images
and its normal appearance reconstruction. Astaraki et al. [12]
proposed to use variational autoencoder (VAE) [13] to generate synthetic normal lung images. Different from [11], the
residual images are concatenated with original tumor lung
images and fed to the segmentation backbone. As a result,
tumor regions can be highlighted in the segmentation process.
Kobayashi et al. [14] proposed a discriminative network to
detect brain tumor regions patch-wisely by calculating the
L2 distance between tumor brain image patches and the
corresponding reconstructed normal brain image patches in the
learned feature space. In anomaly detection based methods,
target images (with lesion regions) and reconstructed images
(with normal appearance) are of the same modality and are
often monomodal [16], so direct comparison (e.g., L2 distance)
at image- or feature-level can be performed. However, in the
context of brain tumor segmentation, routine tumor brain
images are multimodal [17], e.g., T1, T1 contrast enhanced
(T1c), T2, and FLAIR MR images, while normal brain images
are usually monomodal, e.g., T1 MR images [18]. Therefore,
existing anomaly detection based methods are difficult to be
applied for multimodal brain tumor segmentation.
In this paper, we propose a novel deep learning based
framework for multimodal brain tumor segmentation. In our

1941-0042 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

1200

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 33, 2024

Fig. 1. Structure of the proposed framework. It is composed of two networks: the segmentation backbone (blue region), and the normal appearance network
(green region). The segmentation backbone learns features from multimodal tumor brain images {IT1 , . . . , ITM } and outputs tumor segmentation results Y ′ .
A global correlation block (GCB) is used in the segmentation backbone to fuse features learned from different modalities. The normal appearance network
learns features from monomodal normal brain images IR reconstructed by introspective variational autoencoder (IntroVAE). At each decoding level, features
from both networks are sent to the feature alignment module (FAM) to perform feature alignment and comparison to generate the attention map, by which
tumor-related features in the segmentation backbone can be highlighted and enhanced.

framework, a new self-attention based global correlation block
(GCB) is proposed to achieve effective fusion of tumor brain
features learned from multimodal tumor brain images. More
importantly, monomodal normal brain images are adopted in
our framework as reference, from which normal brain features
are learned and compared with the tumor brain features.
In this way, tumor-related features can be highlighted and
enhanced, and the segmentation performance can be improved.
To solve the incomparable issue between features learned from
multimodal and monomodal images, a new feature alignment
module (FAM) is presented. Based on FAM, the distribution of
normal brain features is consistent/inconsistent with the tumor
brain features at normal/tumor regions, facilitating the feature
comparison as well as the final segmentation. The proposed
framework is evaluated using public (BraTS2022) and inhouse tumor brain image datasets. The experimental results
demonstrate that our framework outperforms the state-of-theart segmentation methods in both datasets. Our contributions
are summarized as follows:
• A novel multimodal deep learning framework for brain
tumor segmentation is proposed, where monomodal normal brain images are adopted as reference and compared
with multimodal tumor brain images in a learned feature
space, by which tumor-related features can be highlighted
and enhanced.
• A new feature alignment module (FAM) is presented to
solve the incomparable issue between features learned
from multimodal tumor brain images and monomodal
normal brain images, making the feature comparison
more effective.
• Evaluation results of public (BraTS2022) and in-house
datasets show superior performance of our framework
over the state-of-the-art segmentation methods. Moreover,
further ablation studies confirm the effectiveness of the
proposed components.

•

To the best of our knowledge, our framework is the first
work, which presents a possible way of using normal
brain images to boost tumor brain image segmentation in
the context of clinical situation, i.e., tumor brain images
and normal brain images are of different number of
modalities.
II. M ETHOD

The structure of our framework is shown in Fig. 1. The
framework is composed of two networks: the segmentation
backbone and the normal appearance network. The input of
the segmentation backbone is multimodal tumor brain images
denoted as IT1 , . . . , ITM , where M indicates the number of
different modalities. The input of the normal appearance
network is monomodal normal brain images IR generated by
introspective variational autoencoder (IntroVAE) [19] from the
T1 sequence of the multimodal tumor brain images, e.g., ITM .
Considering high computational efficiency of 2D convolution
and the advantage of using 3D spatial information, all inputs of
our framework are 2.5D slices, which contain one 2D slice to
be segmented and its K neighboring slices, i.e., 2K +1 number
of slices.
In our framework, the segmentation backbone learns features from the input multimodal tumor brain images and
produces the final tumor segmentation results. The normal
appearance network learns features from the input monomodal
normal brain images, and these features are sent to the
segmentation backbone to highlight and enhance the tumorrelated features via feature comparison. In this way, the final
tumor segmentation results can be improved. Details of each
network are presented in the following sections.
A. The Segmentation Backbone
The segmentation backbone is of encoder-decoder structure, and skip connections are adopted to combine low-level

LIU et al.: MULTIMODAL BRAIN TUMOR SEGMENTATION BOOSTED BY MONOMODAL NORMAL BRAIN IMAGES

1201

where ωlc (m) is the weight for the m-th channel (i.e., modality)
c
in flc . In this way, the fused feature of channel c, i.e., f l , can
be obtained by:
c

fl =

M
X

ωlc (m) · flc (m),

(3)

m=1

Fig. 2. Global correlation block (GCB) at the l-th encoding level. The input
flc is formed by features at the c-th channel in flm , m = 1, . . . , M. Two
parallel fully connected layers are used to get Q and K , based on which the
c
correlation matrix Mlc is obtained and used to get the fused feature f l .

and high-level features. Considering that early fusion of
features learned from different modalities could lose modalityspecific information [20], [21], [22], multi-encoder structure
is adopted, where each encoding pathway is responsible for
learning features from one image modality of the tumor brain.
There are four convolution layers in each encoding pathway,
and each convolution layer uses 3×3 kernel with stride of two
followed by batch normalization (BN) and rectified linear unit
(ReLU) activation. The output features of the first convolution
layer have 64 channels, and the channel number is doubled
after each subsequent convolution layers.
To fully exploit correlations among features from different
modalities and perform effective multimodal image feature
fusion before sending to the decoder via the skip connections,
inspired by cross modality convolution (CMC) [23] and selfattention [10], [24], we propose a global correlation block
(GCB) for the fusion module (see Fig. 2).
1) The Fusion Module With Global Correlation Block
(GCB): At each encoding level l of the backbone, the inputs of
the fusion module are features flm ∈ R H ×W ×C , learned from
tumor brain images of different modalities ITm , m = 1, . . . , M,
respectively. Then features at the same channel in flm are concatenated, getting C number of features flc ∈ R H ×W ×M , c =
1, . . . , C. In CMC, each flc is proceeded by 3D convolution
with kernel size of M × 1 × 1 and concatenated together to get
the final fused features. We notice that such convolution has
limited receptive fields and lacks global correlations. To this
end, in GCB, a self-attention mechanism is adopted to explore
the global correlations among all modalities. Specifically, flc
is flattened to M × (H × W ) and sent to two parallel fully
connected (FC) layers. The resulting two features are reshaped
as Q ∈ R M×d and K ∈ Rd×M respectively to get the
correlation matrix Mlc defined as:
Mlc = β Q K ,

(1)

where β is used to counteract the numerical explosion. Similar
to [10], β is set to √1 , and d is set to 768 as adopted
d

in [25]. In Mlc , each element Mlc (i, j) indicates the correlation between the i-th and j-th modalities. Based on Mlc , the
weighting vector ωlc = {ωlc (m)|m = 1, . . . , M} is calculated
by:
PM
c
e j=1 Ml (m, j)/M
c
ωl (m) = P
,
PM
c
M
j=1 Ml (i, j)/M
e
i=1

(2)

where flc (m) is the feature at m-th channel in flc . At last, the
c
fused features of all channels f l , c = 1, . . . , C are concatenated as the final fused feature f l at the l-th encoding level of
the segmentation backbone. Since the global correlations are
considered in GCB, the feature fusion is more effective and
comprehensive as compared with CMC.
2) The Decoding Stage of Segmentation Backbone: The
decoding stage contains four deconvolution layers and one
convolution layer. The input of the first deconvolution layer,
i.e., decoding level l = 1, is the fused feature produced
by the fusion module at the bottleneck of the encoder (i.e.,
f 4 ), while for the rest deconvolution layers (l = 2, 3, 4),
the input includes feature from the previous deconvolution
layer enhanced by the attention map Al (i.e., FT,l−1 ⊙ Al−1 )
and the fused feature (i.e., f 5−l ) from the corresponding
fusion module at the encoding stage. The attention map Al
is produced by the feature alignment module (FAM), which is
discussed later. A softmax nonlinear unit is applied after the
last convolution layer to generate the final segmentation result
Y ′ , which is in the form of a probability map, and the value
at each channel in Y ′ indicates the probability of each tumor
region of interest (ROI).
The Dice index loss [26] is adopted as the loss function of
the segmentation backbone, which is defined as:
P
2 x∈ Y (x) · Y ′ (x)
′
P
LDice (Y, Y ) = − P
,
(4)
′
x∈ Y (x) +
x∈ Y (x)
where x is the position at image region , Y ′ and Y are the
segmentation result and the ground truth, respectively.
B. The Normal Appearance Network
The normal appearance network is a simple U-Net. It is
used to learn features from monomodal normal brain images.
Considering commonly used image modality for normal brain,
the modality of input monomodal normal brain images IR
is set to T1. Inspired by anomaly detection methods, in our
framework, IR is reconstructed from the T1 MR tumor brain
image (e.g., ITM ) contained in the input multimodal tumor
brain images using IntroVAE (see Fig. 1).
1) The IntroVAE: As shown in Fig. 3a, IntroVAE is composed of an encoder for projecting input brain images to a
latent distribution and a decoder for producing reconstructed
brain images based on the latent distribution. IntroVAE is
trained in an adversarial manner by self-estimating the differences between input and reconstructed normal brain images.
Given N T1 MR normal brain images from healthy subjects
(denoted as IHi , i = 1, . . . , N ) as training images, the encoder
projects each normal brain image IHi to a feature embedding
z H = µ + ϵ · σ , where µ and σ are mean and deviation of
z estimated by the encoder, respectively, and ϵ is a randomly
generated vector under the standard normal distribution. Based

1202

Fig. 3. Structure of IntroVAE. The encoder is trained to maximize LReg
of the reconstructed normal brain image to discriminate it from the real one,
while the decoder is responsible for reconstructing the normal brain image
with small LRec , by which LReg can be minimized to confuse the encoder.
In the inference stage, T1 MR tumor brain image ITM is used as input of
IntroVAE to reconstruct the normal brain image IR .

on z H , the decoder can produce the corresponding reconstructed normal brain image IRi . A reconstruction loss LRec
is applied on IHi and IRi to minimize the reconstruction error,
and a regularization loss LReg is applied on z H to enforce the
posterior distribution to match the prior distribution. In this
way, effective representation of normal brain appearance can
be achieved. Details of IntroVAE are referred to [19].
After the training of IntroVAE, T1 sequence, e.g., ITM ,
selected from the multimodal tumor brain images IT1 , . . . , ITM
is used as the input of IntroVAE, where ITM is projected to
a certain feature embedding z representing the closest normal
brain appearance. Based on the feature embedding, the corresponding T1 MR normal brain image IR can be reconstructed
(see Fig. 3b) and used in the normal appearance network to
learn normal brain features. The normal brain features are sent
to the segmentation backbone as reference, and by comparing
them with the tumor brain features, tumor-related features can
be highlighted and enhanced for accurate tumor segmentation.
However, in the context of brain tumor segmentation, the normal brain features learned from monomodality and the tumor
brain features from multimodality are incomparable. To solve
this issue, a new feature alignment module is proposed.
2) The Feature Alignment Module: We denote the tumor
and normal brain features at each decoding level l of the
segmentation backbone and the normal appearance network as
FT,l and FR,l , l = 1, . . . , 4, respectively (see Fig. 1). FT,l (x)
and FR,l (x) are feature at position x. The main idea of FAM is
to make the distribution of FR,l (x) consistent/inconsistent with
FT,l (x) at normal/tumor regions. In this way, tumor regions
in FT,l can be effectively highlighted according to feature
consistency compared with the reference FR,l . Structure of
FAM is shown in Fig. 4. It is composed of two parts: the first
part is feature alignment, where two 1 × 1 convolution layers
ζ and g are adopted to align FT,l and FR,l at normal regions;

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 33, 2024

and the second part is feature comparison, where regions with
low feature consistency between ζ (FT,l ) and g(FR,l ), e.g.,
ζ (FT,l )(x) at tumor regions vs. g(FR,l )(x) at normal regions,
are identified to produce the attention map Al for highlighting
and enhancing the tumor regions in FT,l . Details of each part
are discussed as follows.
In the feature alignment part as shown in Fig. 4a, ζ (FT,l )
and g(FR,l ) should have similar/different feature distribution
at normal/tumor regions. To make the training of ζ and g
more effective, a representation learning method called Simple
Siamese network (SimSiam) [27] is adopted (see Fig. 4c). The
SimSiam network is composed of an encoder F, a projection
MLP K, and a prediction MLP H. It takes each positive sample
pair {I1 , I2 }, i.e., samples of the same class, as input and
maximizes the cosine similarity between two output vectors
p1 and v2 :
v2
p1
·
(5)
D(I1 , I2 ) = −
|| p1 ||2 ||v2 ||2
where p1 ≜ H(K(F(I1 ))), v2 ≜ K(F(I2 )), and
|| · ||2 is L2-norm. In our framework, the feature pairs
{ζ (FT,l )(x), g(FR,l )(x)}, x ∈ NR (x at normal region) are
defined as positive samples, and the normal region NR is
determined according to the label images in the training
dataset. In FAM, ζ and g are regarded as the encoder F in
the SimSiam network, and the loss function of the SimSiam
network is defined as:
1 X
LSim (FT,l , FR,l ) =
D(FT,l (x), FR,l (x))
2
x∈NR

+ D(FR,l (x), FT,l (x)).

(6)

It is worth noting that the SimSiam network is used in
the training stage and is removed at the inference stage.
Moreover, to make the segmentation backbone focus on tumor
segmentation rather than feature alignment, a stop gradient
operation is applied before ζ to stop back-propagation to the
segmentation backbone (see Fig.4a).
In the feature comparison part as shown in Fig. 4b, feature
consistency between ζ (FT,l ) and g(FR,l ) is measured to get
the attention map Al using soft-attention [28], [29], which is
defined as:
Al = σ2 (ψ(σ1 (−ζ (FT,l ) · g(FR,l ))))

(7)

where σ1 is ReLU, σ2 is sigmoid activation function. The
attention map Al is used to highlight and enhance tumorrelated features in FT,l , i.e., FT,l ⊙ Al .
FAM is applied at each level of the decoding stage in the
segmentation backbone. In this way, the tumor-related features
could be strengthened in a coarse-to-fine manner, and the final
tumor segmentation results can be improved.
III. R ESULTS
The proposed framework is evaluated using a public dataset
BraTS2022 [30], which contains multimodal MR tumor brain
images (T1, T1c, T2 and FLAIR) of 1251 glioma patients.
Corresponding manually labeled tumor masks of three tumor
ROIs, i.e., edema, enhancing core, and necrosis, are available.

LIU et al.: MULTIMODAL BRAIN TUMOR SEGMENTATION BOOSTED BY MONOMODAL NORMAL BRAIN IMAGES

1203

Fig. 4. Structure of FAM at decoding level l. In the feature alignment part, two 1 × 1 convolutional layers (ζ and g) are adopted to align tumor brain
features FT,l and normal brain features FR,l , and the feature consistency at normal regions is improved by the SimSiam network during training. In the feature
comparison part, the attention map Al is generated in a dot-product soft-attention manner.
TABLE I
S UMMARY OF THE GBM PATIENTS IN THE IN -H OUSE DATASET

Besides the BraTS2022 dataset, an in-house dataset captured
by our cooperation hospital is also adopted in the experiment.
The in-house dataset contains multimodal MR tumor brain
images, including T1c, B0, mean diffusivity (MD), and fractional anisotropy (FA) of 104 glioblastoma (GBM) patients.
The latter three modalities are derived from diffusion-weighted
imaging (DWI). The key statistics of the GBM patients in
the in-house dataset are summarized in Table I, including
age, sex, tumor location, and the located brain hemisphere.
Manually labeled whole tumor masks are available in the
in-house dataset. Although the in-house dataset has no T1
modality, considering that T1c is T1 with contrast agents in
the vessel and both modalities exhibit similar appearance of
gray matter and white matter at normal regions [31], for the
in-house dataset, we adopt T1c MR tumor brain images as the
input of IntroVAE to reconstruct T1 MR normal brain images.
It is worth noting that IntroVAE is trained independently
before integrated into our framework, i.e, the parameters of
IntroVAE are fixed in the training stage of our framework.
Specifically, the IXI dataset [32], which contains 581 T1 MR
normal brain images, are used to train IntroVAE. All images of
the IXI dataset go through the same pre-processing stage used
in the BraTS2022 and in-house datasets to reduce possible
distribution shift. The training strategy of IntroVAE follows
the paper [14], where the hyperparameters, such as the batch
size and maximal number of training epochs, are set to 120 and
200, respectively.
Besides our framework, exisiting state-of-the-art methods,
including V-Net [33], Attention U-Net [34], nnU-Net [35],
UNETR [36], nnFormer [37], TransBTS [5], MultiCNN [38],
MultiFormer [39], and TuningUNet [40] are also evaluated.
Moreover, ablation experiments of our framework are also
conducted. Specifically, Baseline-1 and Baseline-2 use only

the segmentation backbone of our framework (no normal
appearance network), and the only difference between them
is that Baseline-1 uses cross modality convolution (CMC) in
the fusion module, while global correlation block (GCB) is
adopted in Baseline-2. Baseline-3 is similar to our framework,
but it does not use SimSiam network in the feature alignment
module (FAM).
For both public and in-house datasets, we randomly split
all samples into 70%, 10% and 20% for training, validation
and testing, respectively. All methods under evaluation are
implemented using PyTorch and trained with RTX 3090 GPU.
The input of all methods under evaluation is 2.5D slices with
K = 2, i.e., five successive slices. The batch size is set to
four, and the maximal number of training epochs is 300.
A. Evaluation of Segmentation Results
Accuracy of tumor segmentation results is quantified using
Dice score, Sensitivity, Hausdorff distance, Precision, Specificity, and Jaccard index. Specifically, the Dice score and
Jaccard index are used to evaluate the overlap ratio between
the segmentation results and the ground truth, the Hausdorff
distance measures the consistency between the boundaries of
the segmented tumor and the ground truth, the Sensitivity is
an indicator of the true positive rate, while the Precision and
Specificity can indicate the segmentation ability to correctly
identify the tumor and non-tumor regions.
For the BraTS2022 dataset, the average and standard deviation of the six metrics on enhancing tumor (ET, i.e., enhancing
core), tumor core (TC, i.e., ET+necrosis), and whole tumor
(WT, i.e., ET+TC+edema) are calculated, while for the inhouse dataset, the corresponding metrics on whole tumor are
calculated. Details of the evaluation results comparing with the
nine state-of-the-art methods and the ablation study are shown
in Table II. It is clear that our framework outperforms the
other methods in terms of all metrics on both datasets. Moreover, the evaluation results of the ablation study demonstrate
that each proposed component in our framework, including
GCB, normal appearance network, and SimSiam based FAM,
plays an effective and positive role in the segmentation. The
patient-wise Wilcoxon signed rank test [41] is adopted to
the evaluation results between our framework and the other
methods, and all resulting p values are < 0.05, i.e., statistical
significance. It is worth noting that although Baseline-3 adopts

1204

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 33, 2024

TABLE II
E VALUATION R ESULTS OF A LL M ETHODS U NDER C OMPARISON

LIU et al.: MULTIMODAL BRAIN TUMOR SEGMENTATION BOOSTED BY MONOMODAL NORMAL BRAIN IMAGES

1205

Fig. 5. Examples of segmentation results using all methods under evaluation in the BraTS2022 dataset (left) and in-house dataset (right). Note that, the
BraTS2022 dataset contains three tumor ROIs, i.e., edema (gray), enhancing core (white), and necrosis (dark gray), while the in-house dataset has one whole
tumor region. It is clear that the segmentation results using our framework are more accurate than the other methods under evaluation in both BraTS2022 and
in-house datasets, especially at the regions marked in red circles.

the normal appearance network, FT,l learned from multimodal
tumor brain images and FR,l learned from monomodal normal
brain images suffer from the incomparable issue as no SimSiam network is applied before feature comparison. Therefore,
the improvement using Baseline-3 is minor as compared with
Baseline-2 which has no normal appearance network.
Fig. 5 shows some examples of the segmented brain tumors
using each method under evaluation on both datasets. It is clear
that for each tumor ROI in the BraTS2022 dataset and the
whole tumor region in the in-house dataset, the segmentation
results using our framework are more consistent with the
ground truth than the other SOTA methods under evaluation,
especially at the regions marked in red circles.

while the weights of T1 and T1c are close to zero. This is
because T2 and FLAIR exhibit clear boundary and shape of
whole brain tumor, which can be directly reflected by low-level
features. As the network depth increasing (encoding level l =
3 and 4), details of tumor structure contained in T1 and T1c are
learned as high-level features, thus, the weights of T1 and T1c
are increased. For the in-house dataset, the trend of modality
weights is similar to the BraTS2022 dataset. Specifically, B0,
MD, and FA, which have high contrast tumor appearance, are
assigned with large weights at low levels, while for T1c, which
contains details of tumor structure, large weights are assigned
at high levels.

B. Evaluation of Global Correlation Block

C. Evaluation of Feature Alignment Module

Table II shows that the global correlation block (GCB) can
do more effective fusion of features learned from multimodal
images than the traditional cross modality convolution (CMC).
As aforementioned (Section II-A), at each encoding level l of
the segmentation backbone, GCB fuses features of different
modalities channel-wisely according to the weighting vector
ωlc ∈ R M , c = 1, . . . , C defined in (2). Each element in ωlc
indicates the importance of the corresponding modality at the
c-th channel. C = 64, 128, 256, and 512 at the encoding
level l = 1, 2, 3, and 4, respectively. Fig. 6 shows the
average ωlc (m), i.e., average weight of the m-th modality,
of all input images calculated at the testing stage. The vertical
axis indicates the average weights of each modality, and the
horizontal axis indicates the channel. Dotted lines indicate the
quarter and three-quarter weights.
It is clear that for the BraTS2022 dataset, the weights of T2
and FLAIR are close to one at encoding level l = 1 and 2,

To give an intuitive view of the effect of the feature
alignment module (FAM) as well as the SimSiam network in it,
distributions of features in ζ (FT,l ) and g(FR,l ) (after feature
alignment) are plotted in Fig. 7. Specifically, features, i.e.,
ζ (FT,l )(x) and g(FR,l )(x), are divided into three classes: (1)
tumor regions in ζ (FT,l ); (2) normal regions in ζ (FT,l ); and
(3) normal regions in g(FR,l ). All features are projected onto
a 2D plane using principal component analysis (PCA) [42].
Clearly, with the SimSiam network, features at normal
regions in ζ (FT,l ) and g(FR,l ) can be effectively aligned and
are different from the features at tumor regions in ζ (FT,l ).
In contrast, good feature alignment cannot be achieved without
the SimSiam network, causing the feature incomparable issue.
Fig. 8 shows some examples of the attention maps Al produced
after the feature comparison at each decoding level (l =
1, . . . , 4) of our framework and Baseline-3. It is clear that, Al
of our framework has more concentrated tumor regions than

1206

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 33, 2024

Fig. 6. Modality weights during the channel-wise feature fusion in the fusion
module at each encoding level l of the segmentation backbone using the
BraTS2022 and in-house datasets. The vertical axis represents weights, and
the horizontal axis indicates channels.

Baseline-3. As a result, the final tumor segmentation results
using our framework is more consistent with the ground truth.

D. Sensitivity to Normal Brain Images
Normal brain images, which are used as reference to highlight tumor-related features, play an important role in our
framework. In this section, we evaluate the influence of normal
brain images to our framework. Specifically, we conduct
this experiment to answer the following questions: (1) How
does image noise in the reconstructed normal brain images
affect the segmentation? (2) What is the performance of our
framework using other generative models instead of IntroVAE?
(3) Can we use normal brain images from healthy subjects in
our framework?
To the first question, we gradually add Gaussian noise to
each normal brain image reconstructed by IntroVAE following
a forward Markovian diffusion process [43] over T iterations:
q(IRT |IR ) =

T
Y

q(IRt |IRt−1 )

t=1

q(IRt |IRt−1 ) = N (IRt ;

√ t−1
αt IR , (1 − αt )I ),

(8)
(9)

Fig. 7. Distribution of features in ζ (FT,l ) and g(FR,l ) at each decoding
level l of our framework and Baseline-3 (l = 1, . . . , 4) using BraTS2022
and In-house datasets. Features are from three classes, i.e., tumor regions in
ζ (FT,l ), normal regions in ζ (FT,l ) and normal regions in g(FR,l ), which are
colored in blue, green and orange, respectively.

where IR is the original normal brain image reconstructed by
IntroVAE, q is data distribution, N represents Gaussian distribution, the scalar parameters α1:T determine the variance of
the noise added at each iteration, and I is the identity matrix.
At each iteration t = 1, . . . , T , the distribution of image IRt is
a combination of IRt−1 and Gaussian noise, and αt determines
how much the information of IRt−1 is preserved. Thus, the
higher t, the lower quality of the resulting normal brain image
IRt . In our experiment, α1:T is set to linearly increased from
α1 = 0.001 to αT = 0.02. We evaluate the segmentation
results of our framework using t = 200, 400, 700, and 1000,
respectively. Details of the evaluation results are shown in
Table III. It is clear that the performance of tumor region
segmentation is degraded as the quality of normal brain images
decreases. Specifically, for t = 200, the segmentation results
is relatively stable, but as the t increases the performance is
sharply decreased. Therefore, our framework is sensitive to the
noises in normal brain images.
To the second question concerning generative models, our
framework currently uses IntroVAE to reconstruct high quality normal brain images from corresponding tumor brain
images as input of the normal appearance network. In this

LIU et al.: MULTIMODAL BRAIN TUMOR SEGMENTATION BOOSTED BY MONOMODAL NORMAL BRAIN IMAGES

1207

TABLE III
S ENSTIVITY OF O UR F RAMEWORK TO THE Q UALITY OF N ORMAL B RAIN I MAGES

experiment, we replace IntroVAE with other generative models
commonly adopted in anomaly detection methods, such as
VAE [13] and f-AnoGAN [44]. The training dataset for each
generative model is the same as that used in IntroVAE, i.e.,
the IXI dataset. Some examples of the normal brain images
reconstructed by IntroVAE, VAE, and f-AnoGAN are shown
in Fig. 9. It is clear that the reconstructed normal brain
images using VAE are highly blurry, and important anatomical
structure, such as the brain sulcus and gyrus, is missing.
f-AnoGAN can reconstruct relatively clear brain anatomical
structure, but it cannot preserve anatomical consistency well.
Since IntroVAE combines the merits of both VAE and GAN,
the reconstruction quality is better than VAE and f-AnoGAN.
In our experiment, VAE and f-AnoGAN instead of IntroVAE
are respectively used in our framework to produce the normal
brain images for the normal appearance network. Details of
the evaluation results are shown in Table III. Clearly, the final
segmentation results using VAE and f-AnoGAN are inferior
to IntroVAE. Interestingly, the evaluation results show that
our framework with VAE is better than f-AnoGAN, the main
reason is that although the reconstructed normal brain images
using f-AnoGAN is clear, the anatomical structure is usually

unreal and disordered. In contrast, the anatomical structure
using VAE is consistent with human brain in general.
To the third question about using normal brain images
from healthy subjects instead of reconstruction. For each input
multimodal tumor brain images of our framework, T1 MR
normal brain images of healthy subjects, which have the
minimal L2 distance to the T1 modality of the tumor brain
images, are selected from the IXI normal brain dataset as the
input of the normal appearance network. Clearly, because of
inter-subject variation, normal brain images of healthy subjects
usually have lower anatomical consistency with tumor brain
images than those reconstructed by IntroVAE. To quantify
such consistency, average image intensity error ratio (ER)
between each tumor brain image and its corresponding normal
brain image is calculated, which is defined as
P
x∈NR |IT (x) − IR (x)|
P
,
(10)
ER(IT , IR ) =
x∈NR IT (x)
where IT and IR indicate tumor brain image (T1 modality) and
its corresponding T1 MR normal brain image (reconstructed
by IntroVAE or from healthy subjects), respectively, and NR
stands for normal regions in IT . Low ER indicates high

1208

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 33, 2024

Fig. 8. Examples of the attention maps generated after the feature comparison
at each decoding level. Clearly, the quality of the attention maps and the final
segmentation results produced by our framework (with SimSiam) are better
than Baseline-3 (without SimSiam).

Fig. 9.
Examples of reconstructed normal brain images of BraTS2022
and in-house datasets using IntroVAE, VAE, and f-AnoGAN. Specifically,
VAE has blurred reconstruction structure, f-AnoGAN has clear but disordered
structure, IntroVAE has clear and reasonable structure.

consistency between IT and IR . For the BraTS2022 dataset,
the averages and standard deviations of the error ratio are
0.274±0.043 (IntroVAE) vs. 0.495±0.168 (healthy subjects),
and for the in-house dataset, the results are 0.378 ± 0.010
(IntroVAE) vs. 0.573 ± 0.018 (healthy subjects). The corresponding p values of Wilcoxon signed rank test are 1.120 ×
10−12 (BraTS2022) and 1.149 × 10−6 (in-house dataset),
respectively. As aforementioned, for each input tumor brain
images, the most similar T1 MR normal brain image from
healthy subject is selected from the IXI dataset and sent to
the normal appearance network. The evaluation results of both
BraTS2022 and in-house datasets are shown in Table III.
It can be seen that the performance of our framework is little
decreased but still comparable to that using IntroVAE.

Specifically, we adopt TransBTS as the segmentation backbone of our framework and compare with pure TransBTS on
the BraTS2022 and in-house datasets. The evaluation results
are shown in Table IV. It is clear that TransBTS in our
framework, which is denoted as Ours (TransBTS), achieves
better performance than pure TransBTS in most metrics except
the Specificity on the in-house dataset. Therefore, our framework, which uses normal brain images as reference to conduct
feature-level comparison with tumor brain images, is broadly
applicable and can boost the segmentation performance of
existing methods.

E. Evaluation of Different Segmentation Backbone
The segmentation backbone of our framework is of a
simple U-net like encoder-decoder structure. Actually, the
segmentation backbone can be replaced by other segmentation
networks, such as TransBTS [5]. In this section, we evaluate the generalization ability of our framework and show
the advantage of integrating normal appearance network.

F. Model Complexity
To make a comprehensive comparison of all methods under
evaluation, besides the segmentation accuracy reported in the
previous sections, network parameters, number of floating
point operations (FLOPs), and average inference time are
investigated. The evaluation results are shown in Table V.
Specifically, except V-Net, and baseline-1 and -2 from the
ablation study, our framework has the smaller number of
parameters than the rest methods. The FLOPs of our framework is relatively large, and the main reason is the global

LIU et al.: MULTIMODAL BRAIN TUMOR SEGMENTATION BOOSTED BY MONOMODAL NORMAL BRAIN IMAGES

1209

TABLE IV
E VALUATION R ESULTS OF O UR F RAMEWORK U SING T RANS BTS A S S EGMENTATION BACKBONE

TABLE V
E VALUATION R ESULTS OF M ODEL C OMPLEXITY

correlation block (GCB), which is used for multimodal fusion
and requires large FLOPs. In a similar way, Baseline-1, which
adopt cross modality convolution (CMC) for multimodal
fusion, require large FLOPs too. It is worth noting that all
methods in our experiment take 2.5D slices as input, therefore,
the network parameter, FLOPs, and average inference time are
smaller than those working on 3D.
IV. C ONCLUSION
In this paper, we proposed a novel deep learning framework
for multimodal brain tumor segmentation, where monomodal
normal brain images were used as reference to compare with
multimodal tumor brain images in a learned feature space.
In this way, tumor-related features can be highlighted and
enhanced for good segmentation. In our framework, a new
self-attention based global correlation block (GCB) was presented to capture global correlations among features learned
from different modalities of tumor brain images for effective
feature fusion. Moreover, a new feature alignment module
(FAM) was proposed to tackle the incomparable issue between
features learned from multimodal tumor brain images and
monomodal normal brain images. Based on FAM, effective
feature comparison can be achieved, and high quality attention

maps Al can be generated, finally boosting the performance
of brain tumor segmentation.
Both public BraTS2022 and in-house datasets were used to
evaluate our framework. The experimental results showed that
our framework achieved the best performance of all methods
under evaluation in terms of Dice score, Sensitivity, Hausdorff
distance, Precision, Specificity, and Jaccard index. Besides the
comparison with the state-of-the-art segmentation methods,
ablation experiments were also conducted and demonstrated
that all proposed components, including IntroVAE, GCB,
FAM, and the normal appearance network, have positive
impacts on the segmentation results. Moreover, we investigated
the performance of our framework using normal brain images
with different qualities and sources. The experimental results
showed that our framework can be influenced by the noise
in normal brain images and the performance is relatively
stable using normal brain images from healthy subjects.
In addition, the evaluation results using VAE and f-AnoGAN
showed that reconstructed normal brain images with blurred
but consistent anatomical structure in general can provide more
effective information to enhance the segmentation than clear
but disordered anatomical structure. At last, we evaluated our
framework using different segmentation backbone, and the
results showed that our framework has high generalization
ability and can improve the performance of existing segmentation networks.
For the future study, although IntroVAE and FAM with
SimSiam are used in our framework, we noted that the domain
gap between the monomodal normal brain images and the
multimodal tumor brain images is still non-negligible. Thus,
we will explore possible ways of getting multimodal normal
brain images. Moreover, our framework has relatively large
computational workload, and we will explore more lightweight
techniques for effective fusion of cross-modality.
R EFERENCES
[1] H. Dong, G. Yang, F. Liu, Y. Mo, and Y. Guo, “Automatic brain
tumor detection and segmentation using U-Net based fully convolutional
networks,” in Proc. Annu. Conf. Med. Image Understand. Anal. Cham,
Switzerland: Springer, Jul. 2017, pp. 506–517.
[2] K. Kamnitsas et al., “Efficient multi-scale 3D CNN with fully connected
CRF for accurate brain lesion segmentation,” Med. Image Anal., vol. 36,
pp. 61–78, Feb. 2017.
[3] H. Jia, Y. Xia, W. Cai, and H. Huang, “Learning high-resolution and efficient non-local features for brain glioma segmentation in MR images,” in
Proc. Int. Conf. Med. Image Comput. Comput.-Assist. Intervent. Cham,
Switzerland: Springer, 2020, pp. 480–490.

1210

[4] D. Zhang, G. Huang, Q. Zhang, J. Han, J. Han, and Y. Yu, “Crossmodality deep feature learning for brain tumor segmentation,” Pattern
Recognit., vol. 110, Feb. 2021, Art. no. 107562.
[5] W. Wang, C. Chen, M. Ding, H. Yu, S. Zha, and J. Li, “TransBTS:
Multimodal brain tumor segmentation using transformer,” in Proc.
24th Int. Conf. Med. Image Comput. Comput.-Assist. Intervent. Cham,
Switzerland: Springer, 2021, pp. 109–119.
[6] Z. Jiang, C. Ding, M. Liu, and D. Tao, “Two-stage cascaded U-Net: 1st
place solution to BraTS challenge 2019 segmentation task,” in Proc. Int.
MICCAI Brainlesion Workshop, 2019, pp. 231–241.
[7] D. Nie, L. Xiang, Q. Wang, and D. Shen, “Dual adversarial learning
with attention mechanism for fine-grained medical image synthesis,”
2019, arXiv:1907.03297.
[8] Z. Tang, S. Ahmad, P.-T. Yap, and D. Shen, “Multi-atlas segmentation
of MR tumor brain images using low-rank based image recovery,” IEEE
Trans. Med. Imag., vol. 37, no. 10, pp. 2224–2235, Oct. 2018.
[9] O. Ronneberger, P. Fischer, and T. Brox, “U-Net: Convolutional
networks for biomedical image segmentation,” in Proc. Int. Conf.
Med. Image Comput. Comput.-Assist. Intervent. (MICCAI), 2015,
pp. 234–241.
[10] A. Vaswani et al., “Attention is all you need,” 2017, arXiv:1706.03762.
[11] C. Baur, B. Wiestler, S. Albarqouni, and N. Navab, “Deep autoencoding
models for unsupervised anomaly segmentation in brain MR images,”
in Proc. Int. MICCAI Brainlesion Workshop, 2018, pp. 161–169.
[12] M. Astaraki, I. Toma-Dasu, Ö. Smedby, and C. Wang, “Normal
appearance autoencoder for lung cancer detection and segmentation,”
in Proc. Int. Conf. Med. image Comput. Comput.-Assist. Intervent.
(MICCAI), 2019, pp. 249–256.
[13] D. P. Kingma and M. Welling, “Auto-encoding variational Bayes,” 2013,
arXiv:1312.6114.
[14] K. Kobayashi et al., “Learning global and local features of normal brain anatomy for unsupervised abnormality detection,” 2020,
arXiv:2005.12573.
[15] M. M. R. Siddiquee et al., “Learning fixed points in generative adversarial networks: From image-to-image translation to disease detection
and localization,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2019, pp. 191–200.
[16] C. Baur, S. Denner, B. Wiestler, N. Navab, and S. Albarqouni,
“Autoencoders for unsupervised anomaly segmentation in brain MR
images: A comparative study,” Med. Image Anal., vol. 69, Apr. 2021,
Art. no. 101952.
[17] B. M. Ellingson et al., “Consensus recommendations for a standardized
brain tumor imaging protocol in clinical trials,” Neuro-Oncol., vol. 17,
no. 9, pp. 1188–1198, Aug. 2015, doi: 10.1093/neuonc/nov095.
[18] Z. Tang, P.-T. Yap, and D. Shen, “A new multi-atlas registration
framework for multimodal pathological images using conventional
monomodal normal atlases,” IEEE Trans. Image Process., vol. 28, no. 5,
pp. 2293–2304, May 2019.
[19] H. Huang, Z. Li, R. He, Z. Sun, and T. Tan, “IntroVAE: Introspective variational autoencoders for photographic image synthesis,” 2018,
arXiv:1807.06358.
[20] T. Zhou, S. Canu, P. Vera, and S. Ruan, “Brain tumor segmentation with
missing modalities via latent multi-source correlation representation,” in
Proc. Int. Conf. Med. Image Comput. Comput.-Assist. Intervent., 2020,
pp. 533–541.
[21] F. Xu, H. Ma, J. Sun, R. Wu, X. Liu, and Y. Kong, “LSTM multi-modal
UNet for brain tumor segmentation,” in Proc. IEEE 4th Int. Conf. Image,
Vis. Comput. (ICIVC), Jul. 2019, pp. 236–240.
[22] T. Zhou, S. Canu, P. Vera, and S. Ruan, “Latent correlation representation learning for brain tumor segmentation with missing MRI
modalities,” IEEE Trans. Image Process., vol. 30, pp. 4263–4274, 2021.
[23] K.-L. Tseng, Y.-L. Lin, W. Hsu, and C.-Y. Huang, “Joint sequence learning and cross-modality convolution for 3D biomedical segmentation,”
in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017,
pp. 6393–6400.

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 33, 2024

[24] X. Wang, R. Girshick, A. Gupta, and K. He, “Non-local neural
networks,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
Jun. 2018, pp. 7794–7803.
[25] A. Dosovitskiy et al., “An image is worth 16×16 words: Transformers
for image recognition at scale,” 2020, arXiv:2010.11929.
[26] L. R. Dice, “Measures of the amount of ecologic association between species,” Ecology, vol. 26, no. 3, pp. 297–302,
Jul. 1945.
[27] X. Chen and K. He, “Exploring simple Siamese representation learning,”
in Proc. IEEE Comput. Soc. Conf. Comput. Vision Pattern Recognit.,
Jun. 2021, pp. 15750–15758.
[28] S. Jetley, N. A. Lord, N. Lee, and P. H. S. Torr, “Learn to pay attention,”
2018, arXiv:1804.02391.
[29] F. Wang et al., “Residual attention network for image classification,” in
Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017,
pp. 3156–3164.
[30] B. H. Menze et al., “The multimodal brain tumor image segmentation benchmark (BRATS),” IEEE Trans. Med. Imag., vol. 34, no. 10,
pp. 1993–2024, Oct. 2015.
[31] E.-W. Radue, M. Weigel, R. Wiest, and H. Urbach, “Introduction to
magnetic resonance imaging for neurologists,” Continuum, Lifelong
Learn. Neurol., vol. 22, no. 5, pp. 1379–1398, 2016.
[32] IXI. Information Extraction From Images. Accessed: Feb. 1, 2022.
[Online]. Available: http://www.brain-development.org
[33] F. Milletari, N. Navab, and S.-A. Ahmadi, “V-Net: Fully convolutional
neural networks for volumetric medical image segmentation,” in Proc.
4th Int. Conf. 3D Vis. (3DV), Oct. 2016, pp. 565–571.
[34] J. Schlemper et al., “Attention gated networks: Learning to leverage salient regions in medical images,” Med. Image Anal., vol. 53,
pp. 197–207, Apr. 2019.
[35] F. Isensee, P. F. Jaeger, S. A. A. Kohl, J. Petersen, and K. H. Maier-Hein,
“nnU-Net: A self-configuring method for deep learning-based biomedical image segmentation,” Nature Methods, vol. 18, no. 2, pp. 203–211,
Feb. 2021.
[36] A. Hatamizadeh et al., “UNETR: Transformers for 3D medical image
segmentation,” in Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis.
(WACV), Jan. 2022, pp. 574–584.
[37] H.-Y. Zhou, J. Guo, Y. Zhang, L. Yu, L. Wang, and Y. Yu,
“NnFormer: Interleaved transformer for volumetric segmentation,” 2021,
arXiv:2109.03201.
[38] R. A. Zeineldin, M. E. Karar, O. Burgert, and F. Mathis-Ullrich,
“Multimodal CNN networks for brain tumor segmentation in MRI:
A brats 2022 challenge solution,” in Brainlesion: Glioma, Multiple
Sclerosis, Stroke and Traumatic Brain Injuries, S. Bakas et al., Eds.
Cham, Switzerland: Springer, 2023, pp. 127–137.
[39] J. Cho and J. Park, “Multi-modal transformer for brain tumor segmentation,” in Brainlesion: Glioma, Multiple Sclerosis, Stroke and Traumatic
Brain Injuries, S. Bakas et al., Eds. Cham, Switzerland: Springer, 2023,
pp. 138–148.
[40] M. Futrega, M. Marcinkiewicz, and P. Ribalta, “Tuning U-Net for brain
tumor segmentation,” in Brainlesion: Glioma, Multiple Sclerosis, Stroke
and Traumatic Brain Injuries, S. Bakas et al., Eds. Cham, Switzerland:
Springer, 2023, pp. 162–173.
[41] R. Woolson, “Wilcoxon signed-rank test,” in Wiley Encyclopedia of
Clinical Trials. Hoboken, NJ, USA: Wiley, 2007, pp. 1–3.
[42] I. T. Jolliffe and J. Cadima, “Principal component analysis: A review
and recent developments,” Phil. Trans. Roy. Soc. A, Math., Phys. Eng.
Sci., vol. 374, no. 2065, Apr. 2016, Art. no. 20150202.
[43] J. Ho, A. Jain, and P. Abbeel, “Denoising diffusion probabilistic models,”
in Proc. NIPS, vol. 33. Vancouver, BC, Canada: Curran Associates,
2020, pp. 6840–6851.
[44] T. Schlegl, P. Seeböck, S. M. Waldstein, G. Langs, and U. SchmidtErfurth, “F-AnoGAN: Fast unsupervised anomaly detection with
generative adversarial networks,” Med. Image Anal., vol. 54, pp. 30–44,
May 2019.
PAPER_TEXT
