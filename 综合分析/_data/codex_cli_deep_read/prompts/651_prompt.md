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
# [651] Dual-Masked and Discriminative Reconstruction for Unified Vision Anomaly Detection
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
编号：651
题名：Dual-Masked and Discriminative Reconstruction for Unified Vision Anomaly Detection
年份：2026
DOI：10.1109/tip.2026.3687095
来源：IEEE Transactions on Image Processing
PDF：paper/10.1109_TIP.2026.3687095.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测
相关性：中相关，分数 5
已有代码状态：已下载；D2Rec -> source\D2Rec

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\651.txt
- 原始字符数：64527
- 本次发送字符数：64527
- 是否截断：False

代码包：
- 仓库：D2Rec
  - URL：https://github.com/gaobb/D2Rec
  - 状态：downloaded
  - 本地目录：source\D2Rec
  - 顶层结构：.gitignore、LICENSE、README.md、asserts/、dataset.py、main.py、metrics/、models/、requirements.txt、utils/
  - 主要语言：Python:98、YAML:12
  - README 标题：D2Rec、Introduction、D2Rec Framework、1. Environments、2. Prepare Datasets、MVTec AD、VisA、BTAD、Medical、3. Training
  - README 运行线索：conda environment and install required packages.；conda create -n d2rec python=3.8.12；conda activate d2rec；pip install -r requirements.txt；conda environment and install required packages.；conda create -n d2rec python=3.8.12；conda activate d2rec；pip install -r requirements.txt
  - 关键文件：{"依赖环境": ["requirements.txt", "models/dinov2/eval/setup.py"], "推理/演示入口": ["main.py"], "数据处理入口": ["dataset.py"], "训练入口": ["models/dinov2/run/train/train.py", "models/dinov2/train/train.py"], "配置文件": ["models/dinov2/utils/config.py"]}
  - 数据集线索：MVTec、TOR、Tor、cert、dapt、mvtec、ton、tor

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 35, 2026

4701

Dual-Masked and Discriminative Reconstruction for
Unified Vision Anomaly Detection
Bin-Bin Gao
Abstract—Unsupervised reconstruction networks have shown
promise for unified vision anomaly detection, i.e., image-level
anomaly classification and pixel-level anomaly segmentation,
where a single model trained on multi-class normal images can
detect various anomalies. This is more challenging than most
existing separate methods, i.e., one model for one class, as it
requires handling a more complex data distribution. Notably,
pure reconstruction networks often suffer from overfitting due
to “identity shortcut”, where both normal and anomaly images
may be well recovered and thus fail in detecting anomalies.
Recent efforts have focused on developing specific modules for
different network architectures, e.g., Convolutions and Transformers. However, it is still unclear how to essentially and
effectively prevent learning from this shortcut in a simpler
and more general manner. Furthermore, most existing methods
consider anomaly detection solely as unsupervised classification,
resulting in inaccurate anomaly segmentation due to “weak
discrimination”, where normal and anomaly features may be
entangled. To address these challenges, we propose a simple
yet general Dual-masked and Discriminative Reconstruction
(D2Rec) for unified vision anomaly detection. First, we propose
a general dual-masked reconstruction, i.e., using a pair of
complementary masks, resolving the “identity shortcut” so that
all masked positions are reconstructed by unmasked original
features. Second, we propose a self-supervised discriminator,
which refines reconstruction errors with synthesized anomaly
images to enhance the discrimination ability between normal
and abnormal features. The dual-masked reconstruction and selfsupervised discriminator can serve as universal plugins, easily
integrated into reconstruction-based anomaly detection methods
of any architecture. Despite its simplicity, D2Rec outperforms
previous methods on three industrial benchmarks (MVTec,
BTAD, and VisA), and three medical datasets (Brain MRI, Liver
CT and Retinal OCT). The code for D2Rec is available at https://
github.com/gaobb/D2Rec
Index Terms—Dual-masked reconstruction, self-supervised discriminator, unsupervised anomaly detection, unified anomaly
detection.

I. I NTRODUCTION
NSUPERVISED vision anomaly detection aims to identify anomaly images (i.e., classification or detection) and
segment anomaly regions (i.e., segmentation or localization)
using only normal training images. It is increasingly emerging
with wide applications, such as quality inspection in intelligent
manufacturing [1], [2], [3], medical image diagnosis [4], [5],
and video surveillance [6], [7], [8], [9], thus attracting more

U

Received 25 January 2025; revised 27 October 2025; accepted 5 April 2026.
Date of publication 1 May 2026; date of current version 6 May 2026. The
associate editor coordinating the review of this article and approving it for
publication was Prof. Vittoria Bruni.
The author is with the Tencent YouTu Lab, Shenzhen 518057, China
(e-mail: csgaobb@gmail.com).
This article has supplementary downloadable material available at
https://doi.org/10.1109/TIP.2026.3687095, provided by the authors.
Digital Object Identifier 10.1109/TIP.2026.3687095

research attention. Notably, most existing anomaly detection
methods [10], [11], [12], [13], [14], [15], [16], [17], [18], [19],
[20] mainly focus on training separate models (i.e., one model
for one class) for different objects. However, this separate
paradigm may not be practical in real-world applications, as
it requires high memory consumption and storage overhead,
especially when increasing the number of categories. In contrast, unified anomaly detection (i.e., one model for multiple
classes) detects anomalies for multi-class objects with a single
model. Notably, the categorical information (i.e., class label)
is inaccessible at both the training and inference stages in
this unified setting. Undoubtedly, the unified paradigm is both
more practical and more challenging, but it remains a relatively
new and under-explored area.
UniAD [21] is the first unified unsupervised anomaly detection work, which is typically based on an encoder-decoder
transformer. Notably, the pure encoder-decoder transformer
suffers from overfitting. It cannot achieve satisfactory performance because of “identity shortcut” issue, which returns a
direct copy of the input disregarding its content, as shown
in Fig. 1a. Layer-wise query decoder and neighbor-masked
attention are proposed in UniAD [21] to prevent the model
from learning the shortcut. Similar to UniAD, DUMA [22]
applies a max-mask matrix in self-attention to reduce the noise
dependencies in transformer-based reconstruction networks,
and SSPCAB [23] proposes a masked convolutional kernel for
convolutional-based reconstruction networks. However, these
methods are limited to specific network architectures, such as
transformers or convolutions. Furthermore, RD [16] proposes
a simple student-teacher reconstruction model, where the
student restores the multiscale representations of the teacher
from high-level to low-level. EfficientAD [19] combines a
lightweight student-teacher model and an autoencoder model
for efficient and accurate detection of vision anomalies. However, RD [16] and EfficientAD [19] are originally designed
for separate settings, and there is still a large performance
gap when they are extended to a unified setting. Here, we
raise a question: how to prevent the reconstruction networks
regardless of architecture under a unified setting from falling
into overfitting in a simpler and more general manner?
Furthermore, the current unified anomaly detection
methods, e.g., UniAD [21] and MoEAD [24], are still not
satisfactory for pixel-level anomaly segmentation when
using a more suitable evaluation metric (see more detailed
discussions in Sec. V), e.g., Pixel-level AUPR, as shown in
Figs. 1c and 2. The main reason is “weak discrimination”
between normal and anomaly features because they are trained
only on normal training images in low-resolution feature
space. The “weak discrimination” makes normal and anomaly

1941-0042 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

4702

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 35, 2026

Fig. 1. Comparisons among (a) AE, (b) MAE, (c) UniAD and our (d) DRec and (e) D2Rec with Eb4 +Trans architecture on MVTec. The simple
AE tends to learn an “identity shortcut”, i.e., regressing the overall network to an identity mapping, which can result in the model copying input as output at
inference, thereby failing to detect anomalies. We also observe that AE suffers from serious overfitting, i.e., low training loss but poor testing performance, due
to the “identity shortcut”. The UniAD can alleviate the “identity shortcut”, but it is primarily designed for transformer architectures. To some extent, Masked AE
(MAE) can also mitigate the “identity shortcut”, but its effectiveness depends on an ideal mask ratio. In contrast, the proposed Dual-masked Reconstruction
(DRec) is simple, general, and robust across various mask ratios. DRec effectively resolves the “identity shortcut” by reconstructing all masked positions
using unmasked features. However, both UniAD and DRec still suffer from the “weak discrimination” issue, which leads to entanglement between normal
and anomaly features, ultimately resulting in inaccurate anomaly segmentation. To this end, our D2Rec integrates DRec and Self-Supervised Discriminator
(SSD) into a unified framework. This approach successfully resolves both the “identity shortcut” and “weak discrimination” issues simultaneously, achieving
superior anomaly detection performance, particularly in anomaly segmentation.

Fig. 2. Comparisons of popular reconstruction-based anomaly detection models, e.g., AE and RD, and our DRec and D2Rec with diverse architectures.
The averaged results of all classes on each dataset are reported in P-AUPR for anomaly segmentation and I-AUROC for anomaly classification, respectively.

features always entangled, and ultimately results in inaccurate
anomaly segmentation. We expect that anomaly segmentation
performance can be improved if the “weak discrimination”
issue is mitigated through discriminative learning. Recently,
some discriminative models have been trained on synthetic
anomalies generated on anomaly-free images [15], [20], [25],
[26] or features [17]. However, current approaches either use
synthetic anomalies at the image level, resulting in weak performance, or utilize a complex segmentation model, incurring
high computational costs. We expect to design a discriminator
that is as lightweight as possible to refine reconstruction
errors for achieving better anomaly segmentation.
To overcome “identity shortcut” and “weak discrimination”
issues for unified visual anomaly detection, we propose
an embarrassingly simple but general D2Rec framework.
First, we proposed a Dual-masked Reconstruction (DRec)
mechanism, which ensures that all masked positions are
reconstructed using unmasked features, thus completely solving the “identity shortcut” in unsupervised reconstruction.
Experiments have demonstrated that the proposed DRec is
robust and insensitive to mask ratio. Second, to further boost
the anomaly segmentation performance caused by “weak
discrimination” between normal and abnormal features, we

proposed a lightweight Self-Supervised Discriminator (SSD)
to further refine the reconstruction error from low-resolution to
high-resolution (coarse to fine) with normal and anomaly-free
pseudo images. Our contributions are summarized as follows:
• We rethink and analyze reconstruction networks for
unified anomaly detection, and then find that they
severely suffer from overfitting and result in unsatisfactory performance due to “identity shortcut” and “weak
discrimination”.
• We propose a simple and general dual-masked reconstruction for unsupervised reconstruction networks, which
provides a unified solution to address the “identity
shortcut” in reconstruction networks of any architecture.
• To alleviate “weak discrimination”, we propose a selfsupervised discriminator to refine reconstruction errors
with synthesized anomaly images, which significantly
boosts anomaly segmentation performance.
• We propose a simple, effective, general and robust vision
anomaly detection framework integrating unsupervised
dual-masked
reconstruction
and
self-supervised
discriminator, and achieve competitive performance
on both industrial and medical anomaly detection
benchmarks.

GAO: DUAL-MASKED AND DISCRIMINATIVE RECONSTRUCTION FOR UNIFIED VISION ANOMALY DETECTION

II. R ELATED W ORK
Unsupervised vision anomaly detection methods can
be mainly grouped into three types, i.e., embedding-,
discrimination-, and reconstruction-based methods.
A. Embedding-Based Methods
aim at leveraging deep models pre-trained on large-scale
data to extract offline features from images for anomaly detection. It assumes that offline features preserve the discriminative
information that helps distinguish anomalies from normal
samples. PaDiM [11], MDND [27], and DFM [12] model
a multivariate Gaussian distribution for normal features, then
utilize a distance metric to measure anomalies. PatchCore [13]
captures normal features and then stores them in a memory
bank, and finally calculates anomaly scores by Euclidean
distance between query features and the memory bank at
inference. CS-Flow [10] and PyramidFlow [28] transform
normal feature distribution into a Gaussian distribution via
normalizing flow. CFA [14] and PADA [29] propose feature
adaptation for adapting target datasets. Recent studies have
shown that multiple designed or learnable text prompts on
a powerful vision-language model [30], [31], [32] or only
one normal image prompt on a pure vision model [33] can
yield excellent performance for zero- and few-shot anomaly
detection. However, these methods mainly focus on a separate setting, which has significant performance degradation
when they are naively extended to a unified paradigm. While
zero-/few-shot variants offer practical flexibility, they still
lag behind full-shot methods. We focus on a unified setting
and aim to achieve competitive performance with separate
approaches.
B. Discrimination-Based Methods
are typically trained to distinguish normal images from
synthesized anomaly images and hope that they can generalize
to unseen real anomalies at test time. CutPaste [25] proposes a
simple strategy to generate synthetic anomalies. It cuts a small
rectangular area of variable sizes and aspect ratios from normal
training images and pastes this patch back to the image at a
random location. Similar to CutPaste, DRAEM [15] generates
noise images using Perlin. A boundary-guided semi-push-pull
loss is proposed to learn more discriminative features with synthetic samples in [34]. PRN [35] presents a variety of anomaly
generation strategies for more accurate anomaly localization.
Instead of synthesizing anomalies on images, SimpleNet [17]
synthesizes anomaly features by adding Gaussian noise to
normal features and then learns a binary discriminator to
distinguish anomaly features from normal ones. Recently,
GLASS [20] synthesizes global and local anomalies and
achieves excellent performance in industrial anomaly detection
and localization tasks. AnoGen [36] guides a diffusion model
to generate realistic and diverse anomalies with only a few
real anomaly images. Different from generating anomalies,
this paper mainly aims to propose a simple, general, and
lightweight self-supervised discriminator trained with normal
and anomaly-free pseudo images to alleviate the issue of
inaccurate anomaly segmentation.

4703

C. Reconstruction-Based Methods
assume that anomaly image regions cannot be properly
reconstructed since they do not exist in normal training images.
Some works use generative models such as auto-encoders
[37], [38], [39] and GANs [40], [41], [42] to reconstruct
normal images. Recent works frame anomaly detection as
an inpainting problem, where patches from images are partly
masked. RIAD [43] randomly removes partial image regions
and reconstructs the image from partial inpaintings with a
convolutional neural network. SSPCAB [23] learns to reconstruct masked regions using contextual information with a
masked convolutional kernel. RGI [44] proposes a robust
GAN-inversion that can restore any input image (even with
gross corruptions) to a clean image and identify the corrupted
region mask by solving the optimization problems thereof. A
pyramid deformation module is proposed to model diverse
normal and measure the severity of anomaly in [45]. These
methods tend to be computationally expensive because they
involve reconstruction in image space.
UniAD [21] reconstructs features and achieves strong
performance for unified anomaly detection. Moreover, RD
[16] and EfficientAD [19] propose a simple and lightweight
student-teacher reconstruction model, where the student
restores the teacher’s multiscale representations from highlevel to low-level. Recently, some works, e.g., DiAD [46] and
OneNIP [47], try to use additional conditions or complex modules, such as normal image prompts and stable diffusion, to
improve reconstruction models and achieve good performance
for unified anomaly detection. However, these works are either
designed for specific architectures, such as Trans or Convs,
or are originally designed for separate settings. Therefore,
they do not work well when extended to a unified setting or
are difficult to generalize to different network architectures.
This paper aims to propose a simple and general method for
reconstruction networks of any architecture.
III. M ETHOD
The proposed Dual-masked and Discriminative Reconstruction (D2Rec) jointly learns by reconstruction and discrimination for unified vision anomaly detection, as shown in
Fig. 3. It is composed of a multi-level features fusion, a dualmasked reconstruction, and a self-supervised discriminator. We
elaborately introduce them in this section.
A. Multi-Level Features Fusion
Following existing anomaly detection works, we extract
image features using pre-trained models. Given an input image
I ∈ R3×H×W , we extract multi-level features {Zi } from multiple
stages of a pre-trained backbone F, that is
Zi = F(I),

(1)

where Zi ∈ Rci ×hi ×wi , ci is the channel number, and hi × wi
is the spatial shape of the i-th level feature. Considering
l
that multi-level features {Zi }i=1
usually represent hierarchical
semantic information and their shapes may be different, we

4704

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 35, 2026

Fig. 3. Framework of the proposed D2Rec for unified vision anomaly detection. In the training stage, both normal and synthetic pseudo anomaly images
are fed a pre-trained backbone for extracting multi-level features. These features are transformed into a unified space to obtain compact representations with
multi-level features fusion. Next, a dual-masked reconstruction is utilized to reconstruct normal features, and a self-supervised discriminator with a mask head
is used to refine the reconstruction errors from coarse to fine. At inference, the synthesized images are removed, and only testing images are fed into D2Rec.
The final prediction is a weighted combination of the reconstruction error and the segmentation map from the mask head.

Fig. 4. Visualization comparisons of several baselines and our DRec and D2Rec with diverse network architectures on selected testing images from MVTec
[1], BTAD [2], VisA [3] and BMAD [50] datasets. Here, the superscript † , ‡ and ? means Eb4 +Trans, WR50 +Convs and ViT-B+Trans, respectively.

have to fuse them into a unified space to obtain a compact
representation F, that is
l
.
F = Fuse{Zi }i=1

(2)

For a fair comparison, we adopt the same multi-scale feature
fusion strategy consistent with the state-of-the-art methods,
which varies across backbones and model architectures. The
respective fusion details are described in Section IV-A.
B. Dual-Masked Reconstruction
MAE reconstructs the original signal given its partial observation. It has proven to be a powerful self-supervised method
for both computer vision [48] and natural language processing.
Similar to all autoencoders, MAE has an encoder-decoder
architecture, where the encoder maps the observed signal
to a latent representation and the decoder reconstructs the
original signal from the latent representation. The difference

is that MAE adopts an asymmetric encoder-decoder, which
allows the encoder to operate only on a small portion of the
observed signal through random masking with a mask ratio,
and the decoder reconstructs the full signal from the latent
representation and learnable mask tokens. We empirically
found that pure MAE is only effective when using a high
mask ratio, but its performance is highly sensitive to mask
ratios and still suffers from overfitting, as shown in Fig. 6.
In MAE, unmasked features are easily reconstructed by
learning a shortcut. To avoid overfitting (shortcut), we propose
a Dual-masked Reconstruction (DRec), which works well with
various mask ratios for unsupervised vision anomaly detection.
The DRec consists of a dual-masked encoder/decoder.
1) Dual-Masked Encoder: The dual-masked encoder is
applied only to visible (i.e., unmasked) features. The encoder
embeds the compact representation F derived from multilevel features fusion. Different from the general encoder, our

GAO: DUAL-MASKED AND DISCRIMINATIVE RECONSTRUCTION FOR UNIFIED VISION ANOMALY DETECTION

4705

Fig. 5. Comparisons of Performance, Complexity and Efficiency of different methods with a unified setting on MVTec [1]. Note that M means million (106 )
and FPS means the number of inferencing images in one second on one NVIDIA V100 GPU, with a batch size of 64. Our methods (DRec and D2Rec)
equipped with a lightweight network architecture (Eb4 +Trans) outperform most previous ones in Pixel AUPR (about 10%) with comparable parameters (7.1M)
and inference speed (400 + FPS). The best anomaly detection performance is obtained by our D2Rec when using a more powerful network (ViT-B+Trans)
but with acceptable parameter size (58.8M) and inference speed (104 FPS).

Fig. 6. Comparisons of training loss and testing metrics on MVTec using MAE, DRec, and D2Rec, with varying mask ratios and Eb4 +Trans architecture.
Notably, dual mask ratios are used in D2Rec, e.g., 10% corresponds to 10% and 90%. The MAE only works well with a high masking ratio, e.g., 90%, as
shown in the last of the first row, while lower mask ratios still suffer from overfitting. In contrast, DRec demonstrates robust performance across various mask
ratios, suggesting that the dual-masked mechanism effectively addresses the over-fitting issue of MAE. Moreover, D2Rec shows significant improvements in
pixel-level AUPR across all mask ratios, indicating that the self-supervised discriminator enhances the discriminability between normal and anomaly features.
Consequently, D2Rec is most effective when integrating dual-masked reconstruction and self-supervised discriminator.

encoder only operates on a partial subset (e.g., 50%) of the
full features, i.e., any spatial features are in F, through random
masking M ∈ Rh×w , where each element of M is either 0 or
1. Therefore, the input of our encoder is
F̄m = M

F,

(3)

where represents an element-wise multiplication and masked
tokens are removed from F̄m . For simplicity, the corresponding
latent representation of the encoder is still denoted as F̄m .
Notably, the masked encoder operates on a subset of the
visible features and reconstructs the full features, including
both visible (unmasked) and invisible (masked) features, with
another decoder described below. To some extent, the random
masking operation alleviates over-fitting during the reconstruction process. However, the issue of over-fitting still exists
because the observed features can be completely reconstructed
by simply copying inputs as the outputs, especially for low
mask ratios. To alleviate this issue, we propose a dual mask

as a complementary component of common random masking
as follows:
F̄1−m = (1 − M) F.
(4)
Combining Eqs. 3 and 4 together (i.e., dual-masked encoder),
we can ensure that all masked (reconstructed) features depend
on unmasked ones rather than themselves. Therefore, the
overfitting issue in MAE may be thoroughly resolved by using
the proposed dual-masked mechanism.
2) Dual-Masked Decoder: The input to our dual-masked
decoder is a full set consisting of latent representations F̄m
derived from the dual-masked encoder on visible features and
mask tokens T ∈ Rc . Each mask token T is a shared and
learned embedding that indicates the presence of invisible
features to be predicted. In our implementation, we first restore
the latent representation F̄m into the original spatial location
depending on the mask M, and fill the remaining locations with
this shared mask token. Notably, the mask token would have

4706

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 35, 2026

no location information, and we add positional embeddings
to the mask token in this constructed full set. Then, we feed
the resulting full set via the decoder. Here, we denote the
output of the masked-decoder as F̂mc×h×w . On the other hand,
c×h×w
adopting
we can derive another reconstructed feature F̂1−m
the above decoder processing on another latent representation
F̂1−m .
Notably, F̂m and F̂1−m are reconstructed by visible F̄m and
F̄1−m , respectively. In other words, the visible features could be
completely reconstructed by copying the input as the output.
In order to avoid the issue, we combine F̂m and F̂1−m with
their corresponding opposite masks, that is
F̂ = (1 − M)

F̂m + M

F̂1−m .

(5)

3) Reconstruction Function: The reconstruction function is
used to measure pixel-wise errors between the reconstructed
output F̂ of the dual-masked decoder and the original input
features F. In Eq. 5, each element of F̂ is reconstructed by
its corresponding unmasked features without relying on its
own original (i.e., visible or masked) features. Therefore, it
thoroughly solves the “identity shortcut” because all masked
positions are reconstructed by unmasked original features,
where there is no overlap between masked and unmasked
features. We use the same loss function as state-of-the-arts to
measure reconstruction errors between the reconstructed and
original features as
Lrec (F̂, F),
(6)
where Lrec is either mean squared error or cosine similarity,
depending on the used framework. The loss details for different
frameworks are described in Section IV-A.
C. Self-Supervised Discriminator
The DRec partially solves “identify shortcut” and achieves
good performance on both I- and P-AUROC for unified
anomaly detection. However, it still performs poorly when
using a more rigorous metric (i.e., P-AUPR) as shown in
Fig. 1d. It is not surprising that DRec (like UniAD) is only
trained on normal training images, which may result in “weak
discrimination” between normal and abnormal features.
To enhance the discrimination between normal and anomaly
features, the easiest way is to learn a binary classifier by
normal and anomaly training images. Unfortunately, there are
only normal images for unsupervised anomaly detection tasks.
This is, in fact, also a sound setting for practical applications,
such as industry inspection and medical image diagnosis,
because anomaly images are always rare and difficult to collect
on a large scale. Therefore, we have to synthesize anomaly
images using normal ones for learning a discriminator. Fortunately, some researchers have tried to synthesize anomaly
images and achieved good performance in anomaly detection
fields, such as CutPaste [25] and DRAEM [15]. In this paper,
we directly utilize CutPaste [25] and DRAEM [15] to synthesize anomaly images. Different from CutPaste [25], we learn
a pixel-level discriminator with these synthesized anomaly
images. Furthermore, we design a lightweight discriminator
to refine the dual-masked reconstruction errors, which is also
different from DRAEM [15], using a heavy segmentation
model in image space.

Given a normal training image I n and the corresponding
anomaly mask Y n , we denote its synthesized anomaly image
and anomaly mask as I a and Y a , respectively. We feed the
synthesized anomaly image I a into a pre-trained backbone and
derive multi-level features {Zia }. Then, we can derive the compact representation F a applying Eq. 2. Then, we reconstruct
F a with the proposed DRec, and denote the corresponding
features as F̂ a . Here, we use an element-wise reconstruction
error E a between reconstructed and original features, that is
E a = Error(F̂ a , F a ).

(7)

To ensure stable training, we set the reconstruction error E a
matching the corresponding reconstruction loss, i.e., Eq. 6.
The discriminator is designed with several convolution
blocks following a 1 × 1 convolution layer for performing
pixel segmentation. Here, each convolution block is composed
of a 3 × 3 convolution, a BatchNorm, a ReLU, and a 2 × 2
deconvolution. The reconstruction error E a is fed into the
designed discriminator to obtain an estimated anomaly map
as Ŷ a . For computing the loss between Ŷ a and the groundtruth Y a , we resize Ŷ a to the size of Y a . Considering that
anomaly pixels are typically in the minority in anomaly
detection, we utilize Dice loss [49], which is effective for
learning from extremely imbalanced data, that is
L seg = 1 −

2 · Ŷ a · Y a
,
(Ŷ a )2 + (Y a )2

(8)

D. Training
Considering both the reconstruction and discrimination
objectives of the two sub-networks, the total loss used in
training D2Rec is
L = Lrec + λL seg ,

(9)

where λ > 0 is a weight that balances the importance of the
two loss functions Lrec and L seg .
E. Inference
1) Anomaly Segmentation: The result of anomaly segmentation is an anomaly score map, which assigns an anomaly
score for each pixel. For the dual-masked reconstruction, the
anomaly score map, S rec , is calculated by the reconstruction
error. For the self-supervised discriminator, the anomaly score
map is predicted as the Ŷ ∈ RH×W . Finally, we combine S rec
and Ŷ and take it as the final anomaly segmentation map, that
is
S = w · S rec + (1 − w) · Ŷ,
(10)
where w ∈ [0, 1] is a weight.
2) Anomaly Classification: Anomaly classification aims
to detect whether an image contains anomaly regions. We
transform the anomaly score map S to the anomaly score of
the image by taking the maximum value of S .
IV. E XPERIMENTS
A. Experimental Setup
We follow the previous works and evaluate our method
on three popular industry anomaly detection benchmarks,

GAO: DUAL-MASKED AND DISCRIMINATIVE RECONSTRUCTION FOR UNIFIED VISION ANOMALY DETECTION

MVTec [1], BTAD [2], and VisA [3], and three medical
datasets [50], Brain MRI, Liver CT and Retina OCT.
Protocol: Following the unified anomaly detection protocol
in UniAD, we train a single model for detecting all categories.
For fair comparisons, we use the original training/testing splits
given in previous works [1], [2], [3], [50].
Metric: We evaluate and compare state-of-the-art anomaly
detection methods and our D2Rec for image-level anomaly
classification and pixel-level anomaly segmentation with
AUPR and AUROC metrics. It is worth noting that the
AUPR metric is better for anomaly segmentation measurement
due to the imbalance issue between normal and anomaly
pixels [3], [51].
Competed Methods: Our approach is compared with popular anomaly detection methods including CS-Flow [10],
PaDiM [11], DFM [12], PatchCore [13], CFA [14], DRAEM
[15], SimpleNet [17], RD [16], UniAD [21], MoEAD [24] and
OneNIP [47]. To fully verify the effectiveness of our method,
we insert the proposed D2Rec into several popular baselines,
AE [21], RD [16], and RD? , using diverse backbones and
reconstruction networks, e.g., EfficientNet-b4 + Transformers, WideRes-50 + Convolutions, ViT-B/14 + Transformers
(denoted as Eb4 +Trans, WR50 +Convs and DINOv2 ViTB+Trans for simplicity). The details of these baselines are
summarized as follows:
UniAD [21] is the first work for unified anomaly detection.
It builds on an encoder-decoder transformer architecture
and an EfficientNet-b4 [52] backbone. To prevent the
“identity shortcut”, UniAD introduces layer-wise query and
neighborhood-masked attention. AE is a degraded version
of UniAD. To ensure fair comparisons, we use the same
hyperparameters and network architecture as in UniAD
[21] but fully remove all components in UniAD. Following
4
UniAD, we extract multi-scale features {Zi }i=1
from the
1-th to 4-th stage of a pre-trained EfficientNet-b4. All these
features are resized to the same size (h × w), i.e., the size of
the smallest one. Then, we concatenate these resized features
in the channel dimension to obtain the fusion representation
F. The reconstruction loss, Eq. 6, is set to the mean squared
error (MSE), and the error, Eq. 7, is measured by the absolute
element-wise subtraction, respectively.
RD [16] is convolution-based reconstruction network using
WideRes-50 backbone. It is originally designed for a separate
setting, and here we extend it to the unified paradigm. Instead
of reconstructing a compact feature in AE and UniAD, RD
takes the compact feature as input and reconstructs multi-level
original features in a reverse manner. Following RD [16], we
3
extract multi-scale feature maps {Zi }i=1
from the 1-th to 3-th
stage of a pre-trained WideRes-50. Different from the simple
resizing operation in UniAD, RD utilizes two trainable blocks,
MFF and OCE, for obtaining the compact representation F.
We use cosine similarity as reconstruction loss and error in
Eqs. 6 and 7.
RD? is a simple extension of RD using a more powerful
backbone, DINOv2 ViT-B/14 [53], and a transformer decoder.
Unlike convolution-based EfficientNet-b4 and WideRes-50,
DINOv2 ViT-B/14 adopts full transformer architectures, and
all features from different stages share the same dimensions.

4707

Here, the multi-level features are extracted from the intermediate 8 stages, i.e., {2, 3, · · · , 9}. For simplicity, we average these
features from different stages to obtain the final representation
F. Furthermore, we built a reconstruction decoder with the
standard ViT block, which is also different from the original
convolution block. The cosine similarity is used to measure
reconstruction loss and error in Eqs. 6 and 7, which is the
same as RD [16].
Implementation Details: Unless otherwise specified, we
resize input images to 224 × 224 resolution for all methods
both training phase and inference time. For DRec and D2Rec,
we set the layer numbers of the encoder and decoder to 4 for
Eb4 +Trans, and build the encoder for the identity function
for WR50 +Convs and ViT-B+Trans, respectively. For the
self-supervised discriminator, the number and dimension of
the convolution block are set to 2 and 128 for balancing
performance and computation costs. The loss weight λ in
Eq. 9 and coefficient w in Eq. 10 are set to 0.5 by default,
respectively.
We conduct experiments based on the open-source framework PyTorch and NVIDIA V100 GPU. For Eb4 +Trans, we
train the reconstruction model with a total of 1000 epochs
on 8 Tesla V100 GPUs with batch size 64, and use AdamW
optimizer with weight decay 1 × 10−4 . The learning rate is
1×10−4 initially and drops by 0.1 after 800 epochs. For WR50
+Convs and ViT-B+Trans, we train the reconstruction model
with a total of 50 epochs on 1 Tesla V100 GPUs with batch
size 16, and use AdamW optimizer with weight decay 1×10−4 .
The initial learning rate is set to 2 × 10−3 and using a cosine
annealing learning rate scheduler. We use the official codes for
DRAEM [15], SimpleNet [17], RD [16], UniAD [21], MoEAD
[24] and OneNIP [47], and publicly available implementations
for other methods (e.g., CS-Flow [54], PaDiM [11], PatchCore
[13] and CFA [14]).
B. Comparisons With State-of-the-Arts
Results of industrial anomaly segmentation on MVTec,
BTAD and VisA are reported in Tab. I. 1) Most baseline and
state-of-the-art methods with a unified setting (one model for
multiple classes) suffer from a performance drop compared to
the original results reported in their papers with one model
for one class setting, which is also consistent with observations in UniAD. For example, state-of-the-art SimpleNet
[17] drops about 17% (from 98.1% to 81.0%) in pixel-level
AUROC. 2) The pixel-level AUPR performance is far lower
than AUROC for all methods under a unified setting (e.g.,
less than 50%). This indicates that AUPR metric may be better
than AUROC for measuring pixel-level anomaly segmentation.
3) Our method beats all baselines and achieves the best pixellevel AUPR on two widely used industrial benchmarks, 74.3%
on MVTec, and 48.5% on VisA. Our method significantly
outperforms state-of-the-art by a larger margin. On BTAD, the
anomaly segmentation performance of our D2Rec is slightly
weaker than its baseline (RD) when using a reverse distillation
network with a powerful ViT-B+Trans. We hypothesize that
the limitations may be attributed to the annotation quality of
the dataset, as BTAD contains a certain level of noise [55].

4708

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 35, 2026

TABLE I

TABLE II

P IXEL -L EVEL A NOMALY S EGMENTATION (U PPER PART ) AND
I MAGE -L EVEL A NOMALY C LASSIFICATION (B OTTOM PART )
C OMPARISON W ITH AUROC/AUPR ON T HREE I NDUSTRIAL
B ENCHMARKS , MVT EC , BTAD AND V IS A. T HE B EST
R ESULTS A RE H IGHLIGHTED IN B OLD

P IXEL -L EVEL A NOMALY S EGMENTATION (U PPER PART ) AND I MAGE L EVEL A NOMALY C LASSIFICATION (B OTTOM PART ) C OMPARISONS
W ITH AUROC/AUPR ON T HREE M EDICAL DATASETS , I NCLUDING
B RAIN MRI, L IVER CT AND R ETINAL OCT, F ROM THE BMAD
[50]. T HE B EST R ESULTS A RE H IGHLIGHTED IN B OLD

TABLE III
C OMPARISONS OF D IFFERENT R ESOLUTIONS U SING D2R EC W ITH
V I T-B+T RANS ON MVT EC , BTAD, V IS A AND BMAD

Results of industrial anomaly classification on MVTec,
BTAD and VisA are presented in Tab. I. 1) We observe a
significant drop in anomaly classification performance when
extending separated methods (one model for one class) to
the unified setting (one model for multiple classes), which
is consistent with the findings for anomaly segmentation.
2) Our method outperforms all baselines and state-of-thearts and achieves the best average AUROC and AUPR
scores on MVTec, BTAD and VisA. It is noteworthy that
our method only introduces a dual-masked mechanism to
reconstruction networks and refines the reconstruction errors
with self-supervised discriminator, supporting any network
architectures, e.g., convolution and transformer. Compared to
UniAD [21], our approach is simpler and more general and
can be considered as an alternative to UniAD for different
network architectures.
Results of medical anomaly classification and
segmentation on BMAD [50] are reported in Tab. II. First,
the performance trend of our method on the medical dataset
is consistent with that of industrial datasets. It significantly
outperforms the corresponding baseline methods including
AE, UniAD [21], RD [16] and RD? in both image-level
anomaly classification and pixel-level anomaly segmentation.
Second, our method can be flexibly scaled to stronger
backbones, such as DINOv2 ViT-B/14, and more diverse
reconstruction networks, such as transformer-based reversed
distillation, and can steadily improve the performance of
image-level anomaly classification (from 82.3% to 88.6% in
AUROC) and pixel-level anomaly segmentation (from 42.7%
to 60.6% in AUPR).

Results on Different Resolutions The results in Tab. III
demonstrate that increasing the input resolution to 448 × 448
generally benefits both anomaly segmentation and classification tasks, with a more significant and consistent positive
impact on the pixel-level localization capability. This suggests
that the D2Rec benefits from finer spatial details provided by
the higher resolution, which is crucial for precise anomaly
segmentation.
Qualitative comparisons of anomaly segmentation. In
Fig. 4, we visualize the prediction heatmaps of our methods
(DRec and D2Rec) and several strong baselines (AE, UniAD,
RD and RD? ) on MVTec, BTAD, VisA and BMAD testing
images with the unified setting. Our D2Rec provides the most
precise predictions of anomaly regions with high confidence,
especially on small and slender defects (e.g., contamination
on bottle, hole on hazelnut, and crack on title), while the
baseline methods exhibit some ambiguous predictions due
to the confusion between normal and anomaly samples in
feature space. This further suggests that the proposed
self-supervised
discriminator
indeed
enhances
the
discrimination between normal and anomaly samples,
and thus alleviates the “weak discrimination” issue in existing
reconstruction-based anomaly detection methods.
Comparison of complexity and efficiency Under a unified
setting (one model for multiple classes), we compare the
number of learnable parameters (M) and inference speed
(FPS) of our methods (DRec and D2Rec) with their baselines
(AE, MAE and RD) and all competitors, CS-Flow [54],

GAO: DUAL-MASKED AND DISCRIMINATIVE RECONSTRUCTION FOR UNIFIED VISION ANOMALY DETECTION

4709

TABLE IV
C OMPLEXITY (#LP S , THE N UMBER OF L EARNABLE PARAMS ), E FFICIENCY (FPS) AND P ERFORMANCE (P-/I-AUPR AND P-/I-AUROC) C OMPARISONS
A MONG O UR M ETHODS (DR EC AND D2R EC ), T HEIR BASELINES (AE, MAE, RD AND RD? ) AND OTHER C OMPETITORS

PaDiM [11], PatchCore [13], CFA [14], DRAEM [15],
SimpleNet [17], RD [16], UniAD [21], MoEAD [24] and
OneNIP [47]. The experimental results are shown in Tab. IV
and Fig. 5. The main observations can be summarized as
follows:
Firstly, our methods (DRec and D2Rec) and their baselines
(AE and MAE) enjoy a reasonable complexity among all
competitors if we measure it with the number of learnable
parameters. Specifically, our D2Rec (DRec+SSD) with Eb4
+Trans still has fewer parameters compared to the state-of-theart UniAD [21] (7.1M vs. 7.7M). This benefit mainly comes
from two aspects. One is that we remove all components of
UniAD, especially layer-wise queries in each decoder layer.
The second one is the designed discriminator module as
lightweight as possible (only 0.6M).
Secondly, our methods (DRec and D2Rec) with Eb4 +Trans
achieve about 400 FPS at inference, which is faster than the
popular PatchCore [13] (about 20×) and comparable to stateof-the-arts, such as UniAD [21], MoEAD [24] and OneNIP
[47]. We find that D2Rec is faster (392 FPS vs. 131 FPS) than
MoEAD in actual inference, despite MoEAD having fewer
trainable parameters (4.9M vs. 7.1M). Note that PaDiM [11]
also drives a high inference speed (478 FPS) but brings a larger
number of parameters (950M).
Thirdly, our final solution (D2Rec) with Eb4 +Trans integrates two proposed proposals, dual-masked reconstruction
and self-supervised discriminator, into a framework, which
achieves better anomaly segmentation in pixel-level AUPR
(61.1%) and anomaly classification in image-level AUROC
(96.8%) with fewer parameters (7.1M) and comparable inference speed (393 FPS). Our D2Rec with Eb4 +Trans shows
a slight degradation compared to the current state-of-the-art
OneNIP [47], but it is worth noting that OneNIP requires one
additional normal image at inference.
Last but not least, our D2Rec with ViT-B+Trans still
enjoys reasonable inference speed (104 FPS) and achieves
the best anomaly detection performance (74.3% in pixel-level
AUPR and 98.9% in image-level AUROC) when extended
to a transformer-based reversed distillation network with a
more powerful backbone, DINOv2 ViT-B/14. This also implies
the strong scalability of our method. In other words, the
proposed two key components of our method can be freely
plugged into reconstructed networks of different architectures
and backbones.
C. Ablation Studies
To verify the effectiveness of all proposed components
and the effects of hyperparameters, we implement extensive

ablation studies on MVTec with a unified setting with Eb4
+Trans architecture, as shown in Tab. V and Fig. 6.
1) Dual-Masked Reconstruction: First, simple random
masking is effective for preventing over-fitting. However,
simple masked reconstruction only works well with a high
masking ratio (90%), while others with low mask ratios still
suffer from over-fitting (first row in Fig. 6); Second, the
masked reconstruction with low mask ratios causes over-fitting
because it may learn a simple copying operation that directly
outputs unmasked features as reconstruction. To prevent this
simple copying, we present dual-masked reconstruction, DRec,
which works well with various mask ratios (second row
in Fig. 6). This means that the dual-masked mechanism
thoroughly resolves the over-fitting of masked reconstruction.
Third, the proposed dual-masked reconstruction is simple yet
general, and it can be freely extended to reconstruct networks
with different architectures. It is worth noting that most
existing works are elaborately designed for specific network
architectures.
2) Self-Supervised Discriminator: It can be observed that
pixel-level AUPR curves (red) are still very low using DRec
(second row in Fig. 6) because it is only trained on anomalyfree training data, which may result in weak discrimination
between normal and abnormal samples in feature space. To
enhance feature discrimination, we propose a self-supervised
discriminator to refine reconstruction errors. In the last row
of Fig. 6 and Tab. V, it is most effective for anomaly
classification and segmentation when integrating dual-masked
reconstruction and self-supervised discriminator into a network
(i.e., D2Rec). In order to analyze the effects of the selfsupervised discriminator, we ablate it from model complexity
and synthesis methods. In Tab. Vb, we can see that more
convolution blocks and larger convolution dimensions help
improve the performance of anomaly detection. In Tab. Vf,
increasing the diversity of synthesis methods also contributes
to performance improvements. In addition, we empirically find
that stopping the gradient in the self-supervised discriminator
is helpful to improve performance, as shown in Tab. Va. The
stop-gradient effectively isolates the learning of unsupervised
reconstruction and self-supervised discriminator, thereby these
synthesized anomaly images only train the discrimination. It
is worth noting that there is a distribution gap between the
synthesized and the real anomaly images. The independent
optimization strategy effectively mitigates the overfitting risk
of reconstruction networks.
3) Effects of Hyper-Parameters: We carefully ablate the
effects of other hyperparameters, e.g., the combination coefficient w, the mask ratio, and the weight of the loss function

4710

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 35, 2026

TABLE V
A BLATION S TUDIES ON MVT EC . D EFAULT S ETTINGS A RE IN B LUE

for our D2Rec. The experimental results are reported in Tab.
Vc, d, and e. It can be seen that our D2Rec is robust when
the mask ratio and loss weights are set to a reasonable
interval. Furthermore, it is important to choose a reasonable
combination coefficient w for better performance. It will be
dependent on the DRec when the coefficient is large, and on
the self-supervised discriminator when the coefficient is small.
V. M ORE D ISCUSSIONS
A. AUROC and AUPR Metrics
For imbalanced anomaly segmentation, the AUROC metric
is, in fact, difficult to measure the performance gap for
different methods, and the AUPR is a more appropriate metric. The relationship between AUROC and AUPR has been
comprehensively studied [51] and some takeaways can be
concluded as follows: A random classifier has an AUROC
of 50% and an AUPR of the rate of positive examples; An
imbalanced dataset might skew ROC-curves and make them
look more similar than PR-curves; AUPR is more informative
than AUROC for an imbalanced dataset.
Anomaly detection is a typical binary classification with a
severe imbalance issue, especially in anomaly segmentation.
For example, the proportion of anomaly pixels is only 3.2% on
MVTec testing set, which means that a random classifier only
obtains 3.2% AUPR but 50% AUROC for anomaly segmentation. Furthermore, the AUROC (64.0%) is still high (but the
AUPR is low, i.e., 4.4%) even if we incorrectly predict all pixels of each anomaly testing image as anomaly ones. Therefore,
we believe that AUROC may be suitable to measure imagelevel anomaly classification and AUPR is better for pixel-level
anomaly segmentation because image-level anomaly classification is relatively balanced, while pixel-level anomaly
segmentation is extremely imbalanced. This also explains why
our method is very significant compared to state-of-the-art
when using the AUPR metric and marginal when using the
AUROC metric. In addition, the reliability of AUPR metric
as a measure is also corroborated in qualitative comparisons
in Fig. 4.
B. Comparisons of Separated and Unified Models
Most existing anomaly detection methods mainly focus
on training separate models for different classes. However,

TABLE VI
C OMPARISONS OF S EPARATE AND U NIFIED M ODELS . T HE S UPERSCRIPT ?
M EANS T HAT THE R ESULTS A RE R E -P RODUCED BY U S

this separate paradigm may not be practical in real-world
applications, as it may require high memory consumption and
storage overhead, especially when increasing the number of
categories. In addition, these separate models only perform
well on simple distributions (i.e., one model for one class)
but fail to handle such a challenging task (one model for
multiple classes). Therefore, the unified paradigm is both more
practical and more challenging. Furthermore, it is necessary
to study unified anomaly detection from a foundational model
perspective.
Following previous separate arts, we train separate models,
which are learned in the same way as our unified model, but
on simple data distributions (one model for one class). And
we compare separate models with unified ones in Table VI.
For fair comparisons, we re-implement UniAD for separate
training because the original paper doesn’t report the AUPR
results. Our D2Rec is better than the re-produced UniAD in
both image-level classification and pixel-level segmentation
with AUROC, and significantly better in pixel-level segmentation with AUPR (61.1% vs. 44.5%). More importantly, there
is no significant performance drop from the separate case to
the unified case (60.4% vs. 61.1%). In contrast, most existing
separate (i.e., one model for one class) methods suffer from
a significant performance drop when they are extended to
complex and challenging distributions (i.e., one model for
multiple classes).
C. Unsupervised Reconstruction on Real Normal Images and
Self-Supervised Discriminator on Pseudo Anomaly Images
We learn the dual-masked reconstruction model by optimizing the reconstruction loss between the reconstructed and
original features of normal training images. This process
allows the model to learn how to detect anomalies because

GAO: DUAL-MASKED AND DISCRIMINATIVE RECONSTRUCTION FOR UNIFIED VISION ANOMALY DETECTION

TABLE VII
C OMPARISONS OF R ECONSTRUCTION - AND M EMORY-BANK -BASED M OD ELS . T HE B EST AND S ECOND -B EST R ESULTS A RE H IGHLIGHTED IN
R ED AND B LUE , R ESPECTIVELY

anomaly images are absent in normal training samples, and
they should not be accurately reconstructed. To enhance the
model’s discrimination ability, it is crucial to introduce pseudo
(synthesized) anomaly images for self-supervised training.
Notably, the pseudo anomaly images are generated by applying
region-level perturbations or disruptions to freely available
normal images, resulting in features that naturally contain
both positive (normal) and negative (anomaly) samples. Therefore, it is possible to train the self-supervised discriminator
using Eq. 8. The self-supervised discriminator refines reconstruction errors from low to high resolution for accurate
anomaly segmentation. It is worth noting that it is effective
to independently train the reconstruction network with real
normal images and the discrimination network with pseudo
anomaly images due to the distribution gap between real and
synthesized anomaly images. Here, the independent training
is effectively achieved by applying a stop-gradient operation
on the discrimination network, ensuring that the two networks
are trained separately yet effectively.
D. Comparisons of Reconstruction and Memory-Bank
Methods
Reconstruction-based methods are vulnerable to large-size
defects compared to memory-bank methods. However, our
D2Rec exhibits excellent performance on both large and
small defects. We roughly define large defects as more than
800 pixels with 224 × 224 resolution, and others as small
defects. We list top5 and bottom5 classes on MVTec and
the corresponding pixel AUPR results of PatchCore [13],
UniAD [21], and our D2Rec in Table VII. We can see
that reconstruction-based UniAD is good at detecting small
defects (bottom5) and memory-bank-based PatchCore is better
at detecting large defects in many cases. However, this issue
can be effectively balanced using our D2Rec method, which
significantly outperforms PatchCore (4 classes in top5) and
UniAD (4 classes in bottom5).
VI. C ONCLUSION
In this paper, we rethink reconstruction networks for unified
unsupervised vision anomaly detection, and then find that
they severely suffer from over-fitting and result in unsatisfactory performance because of “identity shortcut” and “weak
discrimination”. To address these two issues, we propose an
embarrassingly simple but effective D2Rec, which is mainly
composed of a dual-masked reconstruction and self-supervised

4711

discriminator. The dual-masked reconstruction is simple and
general, and it provides essential insights into addressing
“identity shortcut” that all masked positions are reconstructed
using unmasked features implemented with a simple dualmasked mechanism. Meanwhile, it is robust for mask ratio
and doesn’t involve other additional hyperparameters and thus
greatly simplifies state-of-the-art UniAD. Furthermore, when
integrating the dual-masked reconstruction and self-supervised
discriminator into a unified network, D2Rec achieves competitive performance on image-level anomaly classification and
pixel-level anomaly segmentation. Furthermore, the proposed
dual-masked reconstruction and self-supervised discriminator
can be easily used as a general plug-in into various reconstruction networks, consistently improving their performance.
A. Limitation
Our method requires a doubling of computational cost
during training due to the self-supervised discriminator on
additional synthesized images. However, the computational
consumption is comparable to its competitors at inference
because the synthesized branch will be removed.
R EFERENCES
[1]

P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec AD—A
comprehensive real-world dataset for unsupervised anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2019, pp. 9584–9592.
[2] P. Mishra, R. Verk, D. Fornasier, C. Piciarelli, and G. L. Foresti, “VTADL: A vision transformer network for image anomaly detection and
localization,” in Proc. IEEE 30th Int. Symp. Ind. Electron. (ISIE), Jun.
2021, pp. 01–06.
[3] Y. Zou, “Spot-the-difference self-supervised pre-training for anomaly
detection and segmentation,” in Proc. ECCV, 2024, pp. 392–408.
[4] T. Xiang, Y. Zhang, Y. Lu, A. L. Yuille, C. Zhang, W. Cai, and Z. Zhou,
“SQUID: Deep feature in-painting for unsupervised anomaly detection,”
in Proc. CVPR, Jun. 2023, pp. 23890–23901.
[5] J. Guo, S. Lu, L. Jia, W. Zhang, and H. Li, “Encoder–decoder contrast
for unsupervised anomaly detection in medical images,” IEEE TMI,
vol. 43, no. 3, pp. 1102–1112, Mar. 2023.
[6] K.-W. Cheng, Y.-T. Chen, and W.-H. Fang, “Gaussian process
regression-based video anomaly detection and localization with hierarchical feature representation,” IEEE Trans. Image Process., vol. 24,
no. 12, pp. 5288–5301, Dec. 2015.
[7] W. Sultani, C. Chen, and M. Shah, “Real-world anomaly detection in
surveillance videos,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., Jun. 2018, pp. 6479–6488.
[8] H. Park, J. Noh, and B. Ham, “Learning memory-guided normality
for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2020, pp. 14360–14369.
[9] M.-I. Georgescu, A. Barbalau, R. T. Ionescu, F. S. Khan, M. Popescu,
and M. Shah, “Anomaly detection in video via self-supervised and multitask learning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2021, pp. 12737–12747.
[10] M. Rudolph, T. Wehrbein, B. Rosenhahn, and B. Wandt, “Fully
convolutional cross-scale-flows for image-based defect detection,” in
Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis. (WACV), Jan. 2022,
pp. 1829–1838.
[11] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “PaDiM: A patch distribution modeling framework for anomaly detection and localization,”
in Proc. ICPR, 2021, pp. 475–489.
[12] N. Ahuja, I. J. Ndiour, T. Kalyanpur, and O. Tickoo, “Probabilistic modeling of deep features for out-of-distribution and adversarial detection,”
in Proc. NeurIPSW, 2019.
[13] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler,
“Towards total recall in industrial anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022,
pp. 14298–14308.

4712

[14] S. Lee, S. Lee, and B. C. Song, “CFA: Coupled-hypersphere-based feature adaptation for target-oriented anomaly localization,” IEEE Access,
vol. 10, pp. 78446–78454, 2022.
[15] V. Zavrtanik, M. Kristan, and D. Skocaj, “DRAEM—A discriminatively trained reconstruction embedding for surface anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021,
pp. 8310–8319.
[16] H. Deng and X. Li, “Anomaly detection via reverse distillation from
one-class embedding,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2022, pp. 9727–9736.
[17] Z. Liu, Y. Zhou, Y. Xu, and Z. Wang, “SimpleNet: A simple network
for image anomaly detection and localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023, pp. 20402–20411.
[18] Y. Liang, J. Zhang, S. Zhao, R. Wu, Y. Liu, and S. Pan, “Omni-frequency
channel-selection representations for unsupervised anomaly detection,”
IEEE Trans. Image Process., vol. 32, pp. 4327–4340, 2023.
[19] K. Batzner, L. Heckler, and R. König, “EfficientAD: Accurate visual
anomaly detection at millisecond-level latencies,” in Proc. IEEE/CVF
Winter Conf. Appl. Comput. Vis. (WACV), Jan. 2024, pp. 127–137.
[20] Q. Chen, H. Luo, C. Lv, and Z. Zhang, “A unified anomaly synthesis
strategy with gradient ascent for industrial anomaly detection and
localization,” in Proc. ECCV, 2024, pp. 37–54.
[21] L. Cui et al., “A unified model for multi-class anomaly detection,” in
Proc. Adv. Neural Inf. Process. Syst., 2022, pp. 4571–4584.
[22] J. Pan, W. Ji, B. Zhong, P. Wang, X. Wang, and J. Chen, “DUMA: Dual
mask for multivariate time series anomaly detection,” IEEE Sensors J.,
vol. 23, no. 3, pp. 2433–2442, Feb. 2023.
[23] N.-C. Ristea et al., “Self-supervised predictive convolutional attentive
block for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2022, pp. 13566–13576.
[24] S. Meng, W. Meng, Q. Zhou, S. Li, W. Hou, and S. He, “MoEAD: A
parameter-efficient model for multi-class anomaly detection,” in Proc.
ECCV, 2024, pp. 345–361.
[25] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Selfsupervised learning for anomaly detection and localization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 9659–9669.
[26] M. Z. Zaheer, J.-H. Lee, A. Mahmood, M. Astrid, and S.I. Lee, “Stabilizing adversarially learned one-class novelty detection
using pseudo anomalies,” IEEE Trans. Image Process., vol. 31,
pp. 5963–5975, 2022.
[27] O. Rippel, P. Mertens, and D. Merhof, “Modeling the distribution of
normal data in pre-trained deep features for anomaly detection,” in Proc.
25th Int. Conf. Pattern Recognit. (ICPR), Jan. 2021, pp. 6726–6733.
[28] J. Lei, X. Hu, Y. Wang, and D. Liu, “PyramidFlow: High-resolution
defect contrastive localization using pyramid normalizing flow,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023,
pp. 14143–14152.
[29] T. Reiss, N. Cohen, L. Bergman, and Y. Hoshen, “PANDA: Adapting
pretrained features for anomaly detection and segmentation,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 2805–2813.
[30] J. Jeong, Y. Zou, T. Kim, D. Zhang, A. Ravichandran, and O. Dabeer,
“WinCLIP: Zero-/few-shot anomaly classification and segmentation,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2023, pp. 19606–19616.
[31] Q. Zhou, G. Pang, Y. Tian, S. He, and J. Chen, “AnomalyCLIP: Objectagnostic prompt learning for zero-shot anomaly detection,” in Proc.
ICLR, 2023.
[32] B.-B. Gao et al., “AdaptCLIP: Adapting CLIP for universal visual
anomaly detection,” in Proc. AAAI, vol. 40, 2026, pp. 4095–4103.
[33] B.-B. Gao, “MetaUAS: Universal anomaly segmentation with oneprompt meta-learning,” in Proc. Adv. Neural Inf. Process. Syst. 37, 2024,
pp. 39812–39836.
[34] X. Yao, R. Li, J. Zhang, J. Sun, and C. Zhang, “Explicit boundary guided
semi-push-pull contrastive learning for supervised anomaly detection,”
in Proc. CVPR, Jun. 2023, pp. 24490–24499.
[35] H. Zhang, Z. Wu, Z. Wang, Z. Chen, and Y.-G. Jiang, “Prototypical
residual networks for anomaly detection and localization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023,
pp. 16281–16291.
[36] G. Gui, B.-B. Gao, J. Liu, C. Wang, and Y. Wu, “Few-shot anomalydriven generation for anomaly classification and segmentation,” in Proc.
ECCV, 2024, pp. 210–226.
[37] Y. Bengio, L. Yao, G. Alain, and P. Vincent, “Generalized denoising
auto-encoders as generative models,” in Proc. NeurIPS, vol. 26, 2013,
pp. 899–907.

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 35, 2026

[38] D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1705–1714.
[39] J. Hou, Y. Zhang, Q. Zhong, D. Xie, S. Pu, and H. Zhou, “Divideand-assemble: Learning block-wise memory for unsupervised anomaly
detection,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct.
2021, pp. 8771–8780.
[40] P. Perera, R. Nallapati, and B. Xiang, “OCGAN: One-class novelty
detection using GANs with constrained latent representations,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2019,
pp. 2893–2901.
[41] X. Yan, H. Zhang, X. Xu, X. Hu, and P. Heng, “Learning semantic
context from normal samples for unsupervised anomaly detection,” in
Proc. AAAI, vol. 35, 2021, pp. 3110–3118.
[42] M. Zaigham Zaheer, J.-H. Lee, M. Astrid, and S.-I. Lee, “Old is
gold: Redefining the adversarially learned one-class classifier training
paradigm,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2020, pp. 14171–14181.
[43] V. Zavrtanik, M. Kristan, and D. Skočaj, “Reconstruction by inpainting
for visual anomaly detection,” Pattern Recognit., vol. 112, Apr. 2021,
Art. no. 107706.
[44] S. Mou et al., “RGI: Robust GAN-inversion for mask-free image
inpainting and unsupervised pixel-wise anomaly detection,” in Proc.
ICLR, 2023.
[45] W. Liu, H. Chang, B. Ma, S. Shan, and X. Chen, “Diversity-measurable
anomaly detection,” in Proc. CVPR, 2023, pp. 12147–12156.
[46] H. He et al., “A diffusion-based framework for multi-class anomaly
detection,” in Proc. AAAI, vol. 38, 2024, pp. 8472–8480.
[47] B.-B. Gao, “Learning to detect multi-class anomalies with just one
normal image prompt,” in Proc. ECCV, 2024, pp. 454–470.
[48] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 15979–15988.
[49] Q. Wei et al., “Learn to segment retinal lesions and beyond,” in Proc.
25th Int. Conf. Pattern Recognit. (ICPR), Jan. 2021, pp. 7403–7410.
[50] J. Bao, H. Sun, H. Deng, Y. He, Z. Zhang, and X. Li, “BMAD:
Benchmarks for medical anomaly detection,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW), Jun. 2024,
pp. 4042–4053.
[51] J. Davis and M. Goadrich, “The relationship between precision-recall
and ROC curves,” in Proc. ICML, 2006, pp. 233–240.
[52] M. Tan and Q. V. Le, “EfficientNet: Rethinking model scaling for
convolutional neural networks,” in Proc. ICML, 2019, pp. 6105–6114.
[53] M. Oquab et al., “DINOv2: Learning robust visual features without
supervision,” TMLR, 2023. [Online]. Available: https://openreview.net/
forum?id=a68SUt6zFt
[54] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Uninformed
students: Student–teacher anomaly detection with discriminative latent
embeddings,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2020, pp. 4182–4191.
[55] X. Jiang et al., “SoftPatch: Unsupervised anomaly detection with noisy
data,” in Proc. Adv. Neural Inf. Process. Syst., 2022, pp. 15433–15445.

Bin-Bin Gao received the B.S. and M.S. degrees in
applied mathematics in 2010 and 2013, respectively,
and the Ph.D. degree in computer science and technology from Nanjing University, China, in 2018. He
is currently a Senior Researcher with the Tencent
YouTu Lab. His research interests include computer
vision and machine learning. He has served as the
Area Chair for NeurIPS 2024/2025/2026 and ICML
2025/2026. He also has served as a regular reviewer
for top-tier journals and conferences in his field, such
as IEEE T RANSACTIONS ON I MAGE P ROCESSING,
IEEE T RANSACTIONS ON M EDICAL I MAGING, IEEE T RANSACTIONS ON
N EURAL N ETWORKS AND L EARNING S YSTEMS, IEEE T RANSACTIONS ON
I NDUSTRIAL I NFORMATICS, IEEE T RANSACTIONS ON K NOWLEDGE AND
DATA E NGINEERING, Neural Networks, Pattern Recognition, CVPR, ICCV,
ECCV, and AAAI.
PAPER_TEXT
