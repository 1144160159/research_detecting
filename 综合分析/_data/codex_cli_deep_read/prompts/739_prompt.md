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
# [739] Memory Augment Is All You Need for Image Restoration
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
编号：739
题名：Memory Augment Is All You Need for Image Restoration
年份：2026
DOI：10.1109/tce.2026.3655769
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2026.3655769.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：无
相关性：弱相关，分数 2
已有代码状态：已下载；MemoryNet -> source\MemoryNet

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\739.txt
- 原始字符数：38512
- 本次发送字符数：38512
- 是否截断：False

代码包：
- 仓库：MemoryNet
  - URL：https://github.com/zhangbaijin/MemoryNet
  - 状态：downloaded
  - 本地目录：source\MemoryNet
  - 顶层结构：Datasets/、LICENSE、MemoryNet.py、README.md、Test-image-RICE/、cloud-results.jpg、config.py、data_RGB.py、dataset_RGB.py、demo.py、evaluate_PSNR_SSIM.m、losses.py、memory.py、pretrained_models/、shadow-results.jpg、structure.png、test.py、train.py、training.yml、utils/
  - 主要语言：Python:14、MATLAB:1、YAML:1
  - README 标题：MemoryNet:Memory augument is All You Need for image restoration、IEEE Transactions on Consumer Electronics 2025、The structure of MemoryNet、Results of Shadow removal on ISTD dataset、Quick Run、Pretrained model、Dataset、To reproduce PSNR/SSIM scores of the paper, run MATLAB script、ACKNOLAGEMENT、MemoryNet:Memory augument is All You Need for image restoration
  - README 运行线索：python demo.py --task Task_Name --input_dir path_to_images --result_dir save_images_here；MATLAB script；python demo.py --task Task_Name --input_dir path_to_images --result_dir save_images_here；MATLAB script；python demo.py --task Task_Name --input_dir path_to_images --result_dir save_images_here；MATLAB script
  - 关键文件：{"推理/演示入口": ["demo.py"], "数据处理入口": ["dataset_RGB.py", "utils/dataset_utils.py"], "模型定义": ["utils/model_utils.py"], "训练入口": ["train.py"], "评估/测试入口": ["evaluate_PSNR_SSIM.m", "test.py"], "配置文件": ["config.py"]}
  - 数据集线索：Quic、dapt、tor

论文正文包开始：
<<<PAPER_TEXT
3764

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

Memory Augment Is All You Need
for Image Restoration
Xiaofeng Zhang , Xuhang Chen , Chaochen Gu, Shanying Zhu, Kim-Fung Tsang ,
and Xinping Guan , Fellow, IEEE

Abstract—The quality of images captured by consumer electronic devices, such as smartphones and digital cameras, is often
compromised by adverse environmental conditions, leading to
degradations like rain, shadows, blur, and low light. These issues
significantly impact the user experience. This paper introduces
MemoryNet, a novel image restoration framework designed
to enhance the quality of images captured with consumer
devices. We also propose Degradation-Aware CLIP (DA-CLIP)
for the perceptual classification of degraded images, a common
challenge in consumer photography. MemoryNet utilizes a threegranularity memory layer and contrastive learning to effectively
restore images. The memory layer retains deep image features,
while contrastive learning ensures the alignment of learned
features for a balanced restoration. We have tested our model on
several challenging tasks, including de-raining, de-shadowing, deblurring, and low-light enhancement. The results show significant
improvements in PSNR and SSIM in four datasets, demonstrating
that MemoryNet can produce restored images with high perceptual authenticity, making it a promising solution to improve the
imaging capabilities of consumer electronics. The code can be
accessed in https://github.com/zhangbaijin/MemoryNet
Index Terms—Image restoration, memory augmentation,
degradation-aware CLIP.

I. I NTRODUCTION

I

MAGE restoration pertains to a fundamental vision task
focused on enhancing degraded images captured by consumer electronic devices. In the era of ubiquitous consumer
electronics, smartphones, digital cameras, dashcams, and
surveillance systems have become integral to daily life. However, images captured by these devices often suffer from
various degradations, including noise, blur, low light conditions, and weather-related artifacts, significantly affecting the
user experience and device functionality. The rapid progress
in computer vision has enabled addressing an expanding array
Received 10 December 2025; accepted 15 January 2026. Date of publication
19 January 2026; date of current version 2 June 2026. This work was
supported in part by the National Natural Science Foundation under Grant
62273235; in part by the National Major Scientific Research Instrument
Development Project under Grant 62227811; in part by the Joint Fund of the
Ministry of Education under Grant 8091B022101; and in part by the Deep
Blue Program Fund Project, Second Institute of Oceanography, Ministry of
Natural Resources. (Corresponding author: Chaochen Gu.)
Xiaofeng Zhang, Chaochen Gu, Shanying Zhu, and Xinping Guan are
with the Center for Intelligent Wireless Network and Collaborative Control, Shanghai Jiao Tong University, Shanghai 200240, China (e-mail:
framebreak@sjtu.edu.cn; jacygu@sjtu.com; shyzhu@sjtu.com).
Xuhang Chen and Kim-Fung Tsang are with Shenzhen Institutes of
Advanced Technology, Chinese Academy of Sciences, Shenzhen 518055,
China (e-mail: xx.chen2@siat.ac.cn; kftsang@ieee.org).
Digital Object Identifier 10.1109/TCE.2026.3655769

of degradation challenges in consumer imaging applications,
such as super-resolution for mobile photography, defogging
for automotive cameras, de-shadowing for outdoor surveillance, removal of rain artifacts from dashcam footage, and
enhancement of low-light images captured by smartphone.
Image restoration is a fundamental yet inherently ill-posed
inverse problem: a single degraded image can correspond
to infinitely many plausible high-quality reconstructions, as
real-world degradation processes—such as motion blur, rain
streaks, shadows, or low-light noise—irreversibly discard
visual information. In consumer electronics (e.g., smartphones,
dashcams, surveillance cameras), this ambiguity is further
amplified by the highly diverse and uncontrolled imaging
conditions under which images are captured. Unlike controlled
laboratory settings, consumer devices must handle arbitrary
combinations of degradations without access to ground-truth
degradation models or auxiliary inputs (e.g., shadow masks),
making restoration both technically challenging and practically
critical for user experience.
To regularize this ill-posed problem, image priors are
essential to guide the solution toward perceptually plausible
and structurally coherent results. Classical priors—such as
sparsity or total variation—often fail to generalize across
real-world scenes and device-specific artifacts. While modern
deep learning approaches have made significant progress by
learning implicit priors from large-scale data, most existing
methods focus narrowly on architectural innovation (e.g.,
attention mechanisms, transformers, or Generative Adversarial
Networks (GANs) [1], [2]. Crucially, they overlook a key
insight from human vision: the ability to restore corrupted
perception often relies on memory of typical structures and
patterns—such as the expected shape of a car, the texture
of pavement, or the lighting consistency of a scene. This
structural memory enables robust inference even under severe
degradation, yet it remains underexplored in current consumeroriented restoration frameworks.
Moreover, practical deployment in consumer electronics
imposes stringent constraints: algorithms must be lightweight,
fast, and mask-free, while still delivering high perceptual
quality. Unfortunately, many state-of-the-art methods either
require auxiliary inputs (e.g., shadow masks [1], [3]), rely on
heavy generative models unsuitable for on-device inference,
or fail to leverage semantic guidance in a degradation-aware
manner. Meanwhile, recent advances in vision-language models (e.g., Contrastive Language-Image Pre-training (CLIP))

1558-4127 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

ZHANG et al.: MEMORY AUGMENT IS ALL YOU NEED FOR IMAGE RESTORATION

offer powerful semantic priors but are ill-suited for lowlevel restoration tasks due to their insensitivity to fine-grained
structural details and their assumption of clean inputs.
To address these gaps, we propose MemoryNet, a novel
image restoration framework that explicitly integrates hierarchical structural memory with degradation-aware semantic
guidance—tailored for real-world consumer electronics. Our
approach is motivated by two key observations: (1) Memoryaugmented representation enables the model to recall and
reconstruct prototypical patterns at multiple granularities (part,
instance, and semantic levels), thereby constraining the solution space toward structurally consistent outputs without
requiring masks or paired degradation labels; (2) Pre-trained
vision-language models can be adapted for low-level tasks if
made aware of input degradation, allowing them to provide
meaningful perceptual supervision even when the input is
severely corrupted.
Accordingly, we introduce two core components: (i) a
three-granularity memory augmentation module that encodes
learnable structural prototypes to enhance restoration fidelity
and generalization; and (ii) a Degradation-Aware CLIP
(DA-CLIP) that repurposes CLIP’s semantic knowledge for
perceptual classification and guidance under degradation.
MemoryNet is designed to be lightweight, mask-free,
and end-to-end trainable, making it suitable for realtime deployment on consumer devices. It achieves strong
performance across four representative tasks—shadow
removal, raindrop cleaning, motion deblurring, and low-light
enhancement—demonstrating that memory is indeed “all you
need” to bridge the gap between real-world degradation and
perceptually authentic restoration.
The key contributions of this paper are as follows:
1) We developed an innovative memory augmentation module that models a learnable latent property variable
to capture globally representative structural prototype
patterns, optimized for efficient execution on consumer
device processors.
2) We proposed a degradation-aware visual language model
(DA-CLIP) to effectively adapt the pre-trained visual
language model for low-level visual tasks in consumer
electronics, serving as a comprehensive framework for
image restoration in smartphones, cameras, and other
consumer imaging devices.
3) We conducted extensive experiments across four common image restoration tasks relevant to consumer
electronics: synthetic image de-shadowing for outdoor
photography, real image deraining for dashcam applications, image deblurring for handheld camera shake
correction, and image low-light enhancement for smartphone night photography.
II. R ELATED W ORK
A. The Development of Memory Modules
He et al. [4] pioneered the use of a memory module for
anomaly detection, conceptualizing the Encoder as a means to
generate queries. The Decoder employs fresh feature maps
from the Memory module to reconstruct images, thereby

3765

accentuating normal frames while magnifying reconstruction
errors in anomalous frames. Park et al. [5] advances the Auto
Encoder with information on normal frames to enhance the
distinction between normal and abnormal frames in video
anomaly detection. For de-raining tasks, MMOS [6] integrates
an intermediate Memory module to model and store diverse
rain patterns, assisting in the rain removal process.
B. Vision-Language Models
Recent research underscores the promising potential of
using pre-trained Vision-Language Models (VLMs) to improve
subsequent tasks by leveraging universal visual and text representations [7], [8], [9]. Typically, a VLM consists of a text
encoder and an image encoder, which work to obtain aligned
multimodal features from noisy image-text pairs through contrastive learning. The BLIP approach refines this by filtering
out noisy data from the web using generated captions. While
VLMs excel in zero-shot and label-free classification for
downstream tasks, their success in image restoration has been
limited due to the necessity for precise, specialized vocabulary.
A novel technique for refining vision-language models is
known as prompt learning [10], where words within the
prompt context are represented by learnable vectors which are
then optimized for the specific task. The degradation-aware
visual language model DA-CLIP [11] incorporates an Image
Controller to predict degradation types and uses a CLIP Image
Encoder module to extract high-quality content embeddings,
integrating DA-CLIP with a reconstruction network. For the
training of DA-CLIP, a hybrid dataset featuring 10 types of
degradation is constructed.
III. N ETWORK S TRUCTURE
The MemoryNet architecture is depicted in Fig. 1. This
paper presents the Degradation-aware CLIP (DA-CLIP) [11],
designed for low-level visual applications, offering a uniform
approach to image restoration. DA-CLIP creatively incorporates an extra controller to alter the standard CLIP image
encoder, which aids in forecasting enhanced feature embeddings. This process allows for the development of adaptive
classifiers tailored to diverse degradation scenarios such as
blur, dim lighting, shadows, and rain.
A. Memory Augmentation
1) How to Detect Abnormal Area?: Blur is categorized as
a type of irregular pattern. To distinguish and convert it into
a normal pattern, we employ a mixture of abnormal detection and a completion proxy. This method aligns well with
the transformer framework. Within this framework, shadow
images are treated as abnormal, whereas clean images are
deemed normal.
Our anomaly detection model adopts the conventional
Encoder-Decoder architecture. Within this framework,
pristine images are processed by a memory-augmented
encoder/decoder to capture standard patterns. This technique
draws on the approach described in [12]. It is not necessary
to alter the fundamental encoder/decoder of your existing
system. Just integrate memory and guidance into it. Once the

3766

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

Fig. 1. Overview of the proposed MemoryNet framework. (a) The degradation-aware CLIP module identifies image degradation types through text-guided
classification. (b) The core MemoryNet architecture features hierarchical memory augmentation and contrastive learning mechanisms for image restoration.

Fig. 2. Detailed illustration of the memory augmentation component.
Input features are processed through an encoder yielding tensors of shape
(bs, 256, W, H), subsequently transformed to (bs, W, H, 256) format. The
memory mechanism employs a learnable matrix T M ((M, C) dimensions) to
compute attention weights through matrix multiplication. A hard threshold
of 0.0025 is applied followed by normalization to generate the final output
features.

anomaly detection training phase is completed, the encoder
and decoder can reconstruct images, with the memory
preserving normal patterns. Nevertheless, if a blurred image
is input, the model fails to restore it to its original clarity.
2) Memory Module: The configuration of Memory augmentation is depicted in Fig. 2. When abnormal frames are
processed by the CNN model, its high capacity can lead to
low reconstruction errors and subsequently, incorrect results.
To address this challenge, we have embedded a Memory
Module in both the Encoder and Decoder. This inclusion

enables the capture of typical frame attributes and decreases
the CNN’s capacity to characterize them, thereby improving the differentiation between normal and abnormal frames.
Furthermore, in our research, we have redesigned the interpretability of probabilities processed in the final CNN layer for
classification-based ranking retrieval. We have also introduced
a hierarchical memory adjustment and alignment module to
mitigate domain bias.
The memory module consists of N prototypes, depicted
by a matrix M ∈ RN×C , where C refers to the constant
feature dimension. The parameter N, representing the number of memory items, can be adjusted. Addressing memory
involves determining how relevant each query is to all memory
items, which is then followed by the use of an attentionbased addressing mechanism. This mechanism, known as the
memory reader, serves to assign each image to a suitable
prototype:

exp d fi , m j
wi j = PN
 ,
j=1 exp d fi , m j
fi m>j

d fi , m j =
,
(1)
kfi k m j
where fi and m j are the feature and prototype slice prototype
matrix M from input f . wi j is the normalized weight to measure the cosine similarity d(·, ·) between fi and m j . Therefore,
the assigned prototype from feature f can be calculated h as:
y = Memory(f, M) =

H×W
N
XX
i=1

wi j m j .

(2)

j=1

Let fi ∈ RC denote the i-th spatial feature vector
extracted from the input feature map f ∈ RH×W×C , and let
m j ∈ RC denote the j-th prototype in the memory matrix
M = [m1 , . . ., mN ]> ∈ RN×C . The attention weight wi j is

ZHANG et al.: MEMORY AUGMENT IS ALL YOU NEED FOR IMAGE RESTORATION

computed as the normalized cosine similarity between fi and
m j:
exp d(fi , m j )
wi j = P N
,
k=1 exp d(fi , mk )


d(fi , m j ) =

fi> m j
.
kfi k km j k

H×W
N
XX
i=1

wi j m j .

1
PS Nc

(4)

j=1

(PSN
Xc )i

α mpart, j ,

(5)

j=(PSNc )(i−1)+1

where α is a learnable scalar weight (or can be absorbed into
the prototype learning process).
The hierarchical memory readout is performed sequentially:
ypart = Memory(f, Mpart ),
yins = Memory(hpart , Mins ),
ysem = Memory(hins , Msem ),

(6)

where hpart and hins denote intermediate feature representations
passed from the previous stage.
During the encoding phase, the memory-augmented features
are fused with shallow features from the decoder via skip
connections. The inputs to the three encoder stages are given
by:
Enc1input = ypart ,
Enc2input = yins + SFeDec1 ,
Enc3input = ysem + SFeDec2 ,

(7)

where SFeDeck denotes the shallow feature embedding from
the k-th decoder block.
To ensure faithful reconstruction of normal patterns and
effective suppression of anomalies, we impose a reconstruction
constraint:

Lrecon = Mem Dec(Enc(Y)) − Y 2 ,

The overall loss function L is a weighted sum of three
components:
L=

The Memory Augmentation (MA) module is designed to
capture hierarchical semantics through three granularities: part,
instance, and semantic levels. The full memory matrix M has
the structure 2 × (P × I × S × Nc ) × C, where P, I, and
S denote the number of prototypes at the part, instance, and
semantic levels, respectively, and Nc is the number of semantic
categories. Each higher-level prototype is constructed as a
weighted aggregation of lower-level prototypes. Specifically,
the i-th instance-level prototype mins,i ∈ RC is defined as:
mins,i =

B. Loss Function Design

(3)

The memory-augmented output feature map y ∈ RH×W×C is
then obtained by aggregating the prototypes according to the
attention weights:
y = Memory(f, M) =

3767

(8)

where Y is the ground-truth clean image, and Enc(·), Dec(·),
and Mem(·) denote the encoder, decoder, and memory readout
operations, respectively.

3
X


Lchar (X s , Y) + λLedge (X s , Y) + Lrecon ,

(9)

s=1

where X s denotes the output at scale s, and Y is the groundtruth image. The term Lchar is the Charbonnier loss, which
provides robust pixel-wise supervision. The term Ledge is
an edge loss that preserves high-frequency structural details.
Finally, Lrecon is the LMSE reconstruction constraint that
ensures the memory module learns representative patterns.
q
(10)
Lchar = kXS − Yk2 + ε2 ,
with the constant ε empirically set to 10−3 for all experiments.
In addition, Ledge is the edge loss, defined as:
q
Ledge = k∆ (XS ) − ∆(Y)k2 + ε2
(11)
IV. E XPERIMENT
A. Implementation Details
MemoryNet is a fully trainable model from scratch, eliminating the need for pre-training. It was developed with PyTorch
1.8.0 and an NVIDIA GTX 3090 GPU. Our evaluation
in this study utilized metrics such as PSNR, SSIM, and
RMSE.This study employs the ISTD dataset as referenced
in [1], DeRainDrop dataset [28], LOL-v2 dataset [29] and
GoPro dataset [30] for deblurring images. For optimization
of our network, we utilize the Adam optimizer with β1 = 0.9
and β2 = 0.999. Learning Rate: An initial learning rate of
2×10−4 was used, which was gradually reduced using a cosine
annealing scheduler over the training process. Batch Size: 16
for all experiments. Epochs: Training was conducted for 300
epochs on each dataset, with early stopping based on validation
performance.
B. Comparison With State-of-the-Art Methods
1) Shadow Removal: Our approach is evaluated against a
range of existing methods, such as Yang [13], Guo [14], Gong
[15], DeShadowNet [16], STC-GAN [1], DSC [18], MaskShadowGAN [23], RIS-GAN [19], DHAN [20], SID [17],
LG-shadow [24], G2R [22], DC-ShadowNet [53], Auto-exp
[21], SpA-Former [25], Shadow-Refiner [26], ShadowFormer
[3] and Diff-Shadow [27]. For assessment, we use the root
mean square error (RMSE), structural similarity index (SSIM),
and Peak Signal-to-Noise Ratio (PSNR) in the LAB color
space. Table I details the RMSE, SSIM, and PSNR outcomes
for these shadow removal techniques on the ISTD dataset
[1]. The comprehensive evaluation is depicted in Fig. 3.
MemoryNet excels in PSNR across partially, non-partially
shaded, and unshaded regions. In unshaded areas, our RMSE
also sets a new standard, outperforming the state-of-the-art
generally. SID [17] and G2R [22] sometimes inaccurately
assess dark non-shaded areas, leading to estimation errors.
Their models do not fully leverage the shadow mask data,

3768

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

Fig. 3. Qualitative results demonstrating shadow removal performance on the ISTD benchmark dataset.
TABLE I
Q UANTITATIVE E VALUATION OF S HADOW R EMOVAL M ETHODS ON THE ISTD B ENCHMARK

Fig. 4. Comparative visualization of raindrop removal results on the Raindrop benchmark.

despite its inclusion in their network inputs. Although Autoexp [21] and G2R [22] effectively employ triplet datasets
(input, mask, target) based on evaluative metrics, the need
for shadow mask acquisition in real-world application settings
is questionable. Our training only needs data pairs, while
testing requires just a basic shadow image, offering significant practical benefits. DSC [54], and SpA-Former [25] may
incorrectly handle relatively dark non-shaded regions bringing
some misestimation. It turns out that their model fails to take
full advantage of the shadow mask information, even if their
network input contains a shadow mask.
2) Rain Removal: As presented in Table II and Fig. 4, we
outline the PSNR/SSIM performance scores for rain removal

on the DeRainDrop testB and testA datasets. Our approach is
evaluated against existing techniques, such as CMFNet [55],
D-DAM [31], BPP [32], Maxim [34], IDT [35] and RaindropClarity [36]. On the test-b set, our MemoryNet attained
the top SSIM score of 0.84 and the second-highest PSNR
of 25.38 dB. In comparison, it achieved the highest SSIM
score of 0.904 and the best PSNR of 24.64 dB on test-a.
The visualization results for the DeRainDrop test-b image are
illustrated in the figure. These findings indicate the superior
effectiveness of our method in eliminating raindrops. The
images produced by our technique more closely resemble
the actual images than those produced by other models.
Additionally, we carried out rain removal experiments using

ZHANG et al.: MEMORY AUGMENT IS ALL YOU NEED FOR IMAGE RESTORATION

3769

Fig. 5. Qualitative comparison of motion deblurring performance on the GOPRO test set.

Fig. 6. Visual results comparing low-light enhancement performance using the LOL-v2 benchmark.
TABLE IV
TABLE II
Q UANTITATIVE R ESULTS FOR R AINDROP R EMOVAL
ON R AINDROP DATASET

TABLE III
M OTION D EBLURRING P ERFORMANCE M ETRICS
ON THE GOPRO T EST S ET

MMOS [6], a rain removal network that also incorporates
a memory module. Nonetheless, MMOS yielded unrealistic
results, proving ineffective on actual rain removal datasets.
We believe this may be due to the unsuccessful integration of
noisy data with pseudo-labels generated by the target network
during real data processing.

L OW-L IGHT E NHANCEMENT P ERFORMANCE C OMPARISON
ON THE LOL DATASET

3) Image Deblurring: Within Table III and Fig. 5, we
present the PSNR/SSIM results for various methods applied to
the deblurring task. Our analysis includes a comparison with
numerous leading algorithms such as Gao [37], DBGAN [38],
MT-RNN [39], MPRNet [33], DGUNet [41], MADANet [42],
SFNet and DeblurDiff [43]. The results of the quantitative
assessment are displayed in Table III. Despite MemoryNet
not achieving the top scores, its performance remains commendable, illustrating its ability to handle image degradation
effectively. DGUNet achieved superior performance metrics,
which can be credited to its novel gradient strategy integrated
into the proximal gradient descent (PGD) algorithm. This
enables the model to address complex, real-world image degradation scenarios, thus enhancing its suitability for practical
use.
4) Low-Light Image Enhancement: We compare our
approach against KinD [29], Zero-DCE [44], SCI [46], PairLie [47], GenerativePrior [48], NeRCO [49], CLIP-LIE [50],
LPDM [51] and Lighten-Diffusion [52]. The results of these
comparisons are displayed in Fig. 6 and Table IV. KinD [29]

3770

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

Fig. 7. Feature map visualizations comparing network activations: (a) baseline model without memory augmentation, (b) enhanced representations with
memory augmentation applied.
TABLE V
C OMPONENT A NALYSIS E VALUATING THE C ONTRIBUTION OF M EMORY
AUGMENTATION AND C ONTRASTIVE L EARNING
ON THE ISTD B ENCHMARK

Fig. 8. Comparative feature visualizations from the initial layer: left shows
raw features before processing, right displays enhanced features after memory
augmentation.

enhances image details and contrast by decomposing images
into illumination and reflection, effectively managing issues
like overexposure and color distortion. However, this technique
may not be ideal for images with highly uneven lighting
conditions. Zero-DCE [44] employs a deep learning approach
without a reference, adjusting well to diverse lighting, although
it might result in unnatural color changes, compromising the
image’s natural appearance. SCI [46] introduces an innovative strategy for enhancing low-light images, offering rapid
processing speed and adaptability. Despite impressive flexibility and speed, maintaining the image’s naturalness and
detail in low-light situations can be challenging. PairLie [47],
LPDM [51] and Lighten-Diffusion [52] offer a technique for
boosting low-light images by comparing them to their normallight counterparts. The approach processes image pairs, which
confines its usefulness to instances where a reference image
is unavailable. Nonetheless, the method detailed in the paper
yields acceptable outcomes concerning color and exposure,
among other factors.
C. Ablation Study on MemoryNet
1) Quantitative Comparisons on Memory Augmentation:
In order to evaluate the efficacy of the Memory augmentation

and contrastive learning techniques introduced in this study,
we carried out ablation analyses on the ISTD datasets. These
analyses are illustrated in Figs. 7 and 8, and Table V. Since
each Memory item calculates cosine similarity with all queries,
we explored different configurations of our Memory layer,
including three-branch, two-branch, and single-branch models.
The findings, as detailed in Table V, reveal that Memory
augmentation is especially effective within a three-stage recovery network. Additionally, to clarify the influence of Memory
augmentation, we visualized features within a compact network using a car image, as shown in Fig. 7. The comparative
visualization indicates that the feature map with Memory augmentation is more consistent with the network’s propagation,
unlike the original feature map without augmentation, which
diverges from the source image. The Memory augmentation
network adeptly highlights the prominent features of the
image, as demonstrated by the more distinct heatmap in the car
image, confirming the successful identification of key features.
2) Quantitative Comparisons on Contrastive Learning:
Our study investigates contrastive learning as a substitute for
generative learning. Unlike generative learning, contrastive
learning emphasizes distinguishing differences between data
on a conceptual level without examining the specific details
of each example. This approach simplifies the model and
optimization process, while also enhancing generalizability.
We apply contrastive learning following the residual network,
effectively converting it into a discriminator. This technique
aids in crafting an encoder capable of producing similar
representations for data in the same category, while amplifying
the differences between representations of data from different
categories. The outcomes of our research indicate that applying
contrastive learning significantly enhances certain tasks, such

ZHANG et al.: MEMORY AUGMENT IS ALL YOU NEED FOR IMAGE RESTORATION

as de-shadowing. Notably, integrating a memory network with
contrastive learning led to substantial improvements in metrics,
with PSNR increasing by 1 point to 33.44, SSIM rising to
0.986, and RMSE decreasing to 6.03, as detailed in Table V.
V. C ONCLUSION
This paper presents MemoryNet, a system that includes
two key components: DA-CLIP and MemoryNet. DA-CLIP
is tailored for perceptual classification of images with degradation, and MemoryNet features a tri-level memory layer and
contrastive learning. Our tests across four different settings
show the effectiveness of these approaches in improving image
restoration outcomes. Additionally, the model put forth in this
work exhibits significant improvements in both PSNR and
SSIM metrics across three datasets with different degradation
types, highlighting its capability to generate perceptually accurate restored images.
R EFERENCES
[1]

J. Wang, X. Li, and J. Yang, “Stacked conditional generative adversarial
networks for jointly learning shadow detection and shadow removal,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2018,
pp. 1788–1797.
[2] H. Zhang, V. Sindagi, and V. M. Patel, “Image de-raining using a
conditional generative adversarial network,” IEEE Trans. Circuits Syst.
Video Technol., vol. 30, no. 11, pp. 3943–3956, Nov. 2020.
[3] L. Guo, S. Huang, D. Liu, H. Cheng, and B. Wen, “ShadowFormer:
Global context helps shadow removal,” in Proc. AAAI, 2023, vol. 37,
no. 1, pp. 710–718.
[4] T. He, D. Gong, Z. Tian, and C. Shen, “Learning and memorizing
representative prototypes for 3D point cloud semantic and instance
segmentation,” in Proc. ECCV, 2020, pp. 564–580.
[5] H. Park, J. Noh, and B. Ham, “Learning memory-guided normality
for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2020, pp. 14372–14381.
[6] H. Huang, A. Yu, and R. He, “Memory oriented transfer learning for
semi-supervised image deraining,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jun. 2021, pp. 7732–7741.
[7] A. Radford et al., “Learning transferable visual models from natural
language supervision,” in Proc. Int. Conf. Mach. Learn., vol. 139, 2021,
pp. 8748–8763.
[8] C. Jia et al., “Scaling up visual and vision-language representation
learning with noisy text supervision,” in Proc. 38th Int. Conf. Mach.
Learn., vol. 139, M. Meila and T. Zhang, Eds., Jul. 2021, pp. 4904–4916
https://v139/jia21b.html
[9] J. Li, D. Li, C. Xiong, and S. Hoi, “Blip: Bootstrapping language-image
pretraining for unified vision-language understanding and generation,”
in Proc. ICML, 2022, pp. 12888–12900.
[10] K. Zhou, J. Yang, C. C. Loy, and Z. Liu, “Learning to prompt for vision
language models,” IJCV, vol. 130, no. 9, pp. 2337–2348, 2022.
[11] Z. Luo, F. K. Gustafsson, Z. Zhao, J. Sjölund, and T. B. Schön,
“Controlling vision-language models for universal image restoration,”
2023, arXiv:2310.01018.
[12] D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1705–1714.
[13] Q. Yang, K.-H. Tan, and N. Ahuja, “Shadow removal using bilateral
filtering,” IEEE Trans. Image Process., vol. 21, no. 10, pp. 4361–4368,
Oct. 2012.
[14] R. Guo, Q. Dai, and D. Hoiem, “Paired regions for shadow detection
and removal,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 35, no. 12,
pp. 2956–2967, Dec. 2013.
[15] H. Gong and D. Cosker, “Interactive shadow removal and ground truth
for variable scene categories,” in Proc. Brit. Mach. Vis. Conf. (BMVC),
2014, pp. 1–11.
[16] L. Qu, J. Tian, S. He, Y. Tang, and R. W. H. Lau, “DeshadowNet:
A multi-context embedding deep network for shadow removal,” in
Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017,
pp. 4067–4075.

3771

[17] H. Le and D. Samaras, “Shadow removal via shadow image
decomposition,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2019, pp. 8578–8587.
[18] X. Hu, C.-W. Fu, L. Zhu, J. Qin, and P.-A. Heng, “Direction-aware
spatial context features for shadow detection and removal,” IEEE Trans.
Pattern Anal. Mach. Intell., vol. 42, no. 11, pp. 2795–2808, Nov. 2020.
[19] L. Zhang, C. Long, X. Zhang, and C. Xiao, “RIS-GAN: Explore residual and illumination with generative adversarial networks for shadow
removal,” in Proc. AAAI, 2020, pp. 12829–12836.
[20] X. Cun, C.-M. Pun, and C. Shi, “Towards ghost-free shadow removal
via dual hierarchical aggregation network and shadow matting GAN,”
in Proc. AAAI Conf. Artif. Intell., 2020, pp. 10680–10687.
[21] L. Fu et al., “Auto-exposure fusion for single-image shadow removal,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2021, pp. 10571–10580.
[22] Z. Liu, H. Yin, X. Wu, Z. Wu, Y. Mi, and S. Wang, “From shadow
generation to shadow removal,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2021, pp. 4925–4934.
[23] X. Hu, Y. Jiang, C. Fu, and P. Heng, “Mask-ShadowGAN: Learning
to remove shadows from unpaired data,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis. (ICCV), Oct. 2019, pp. 2472–2481.
[24] Z. Liu, H. Yin, Y. Mi, M. Pu, and S. Wang, “Shadow removal by a
lightness-guided network with training on unpaired data,” IEEE Trans.
Image Process., vol. 30, pp. 1853–1865, 2021.
[25] X. Zhang, Y. Zhao, C. Gu, C. Lu, and S. Zhu, “SpA-former: An effective
and lightweight transformer for image shadow removal,” in Proc. Int.
Joint Conf. Neural Netw. (IJCNN), Jun. 2023, pp. 1–8.
[26] W. Dong et al., “ShadowRefiner: Towards mask-free shadow removal
via fast Fourier transformer,” 2024, arXiv:2406.02559.
[27] C. Li, B. Yang, Z. Wu, G. Chen, Y. Yu, and S. Zhou, “Shadow removal
based on diffusion, segmentation and super-resolution models,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW),
Jun. 2024, pp. 6045–6054.
[28] R. Qian, R. T. Tan, W. Yang, J. Su, and J. Liu, “Attentive generative
adversarial network for raindrop removal from a single image,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2018,
pp. 2482–2491.
[29] Y. Zhang, J. Zhang, and X. Guo, “Kindling the darkness: A practical
low-light image enhancer,” in Proc. 27th ACM Int. Conf. Multimedia
(ACM MM), Oct. 2019, pp. 1632–1640.
[30] S. Nah, T. H. Kim, and K. M. Lee, “Deep multi-scale convolutional
neural network for dynamic scene deblurring,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017, pp. 3883–3891.
[31] K. Zhang, D. Li, W. Luo, and W. Ren, “Dual attention-in-attention model
for joint rain streak and raindrop removal,” IEEE Trans. Image Process.,
vol. 30, pp. 7608–7619, 2021.
[32] P. N. Michelini et al., “Back–projection pipeline,” in Proc. ICIP, 2021,
pp. 1949–1953.
[33] S. W. Zamir et al., “Multi-stage progressive image restoration,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2021,
pp. 14821–14831.
[34] Z. Tu et al., “MAXIM: Multi-axis MLP for image processing,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022,
pp. 5769–5780.
[35] J. Xiao, X. Fu, A. Liu, F. Wu, and Z.-J. Zha, “Image de-raining
transformer,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 45, no. 11,
pp. 12978–12995, Nov. 2023.
[36] Y. Jin, X. Li, J. Wang, Y. Zhang, and M. Zhang, “Raindrop clarity:
A dual-focused dataset for day and night raindrop removal,” in Proc.
ECCV. Cham, Switzerland: Springer, 2024, pp. 1–17.
[37] H. Gao, X. Tao, X. Shen, and J. Jia, “Dynamic scene deblurring
with parameter selective sharing and nested skip connections,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2019,
pp. 3848–3856.
[38] K. Zhang et al., “Deblurring by realistic blurring,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020,
pp. 2734–2743.
[39] D. Park, D. U. Kang, J. Kim, and S. Y. Chun, “Multi-temporal recurrent
neural networks for progressive non-uniform single image deblurring
with incremental temporal training,” in Proc. Eur. Conf. Comput. Vis.
Cham, Switzerland: Springer, 2020, pp. 327–343.
[40] S. W. Zamir, A. Arora, S. Khan, M. Hayat, F. S. Khan, and M.-H. Yang,
“Restormer: Efficient transformer for high-resolution image restoration,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2022, pp. 5728–5739.

3772

[41] C. Mou, Q. Wang, and J. Zhang, “Deep generalized unfolding networks
for image restoration,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2022, pp. 17399–17410.
[42] D. Yang and M. Yamac, “Motion aware double attention network for dynamic scene deblurring,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. Workshops (CVPRW), Jun. 2022,
pp. 1112–1122.
[43] L. Kong et al., “DeblurDiff: Real-world image deblurring with generative
diffusion models,” 2025, arXiv:2502.03810.
[44] C. Guo et al., “Zero-reference deep curve estimation for low-light image
enhancement,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2020, pp. 1780–1789.
[45] R. Liu, L. Ma, J. Zhang, X. Fan, and Z. Luo, “Retinex-inspired
unrolling with cooperative prior architecture search for low-light image
enhancement,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2021, pp. 10561–10570.
[46] L. Ma, T. Ma, R. Liu, X. Fan, and Z. Luo, “Toward fast,
flexible, and robust low-light image enhancement,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022,
pp. 5637–5646.
[47] Z. Fu, Y. Yang, X. Tu, Y. Huang, X. Ding, and K.-K. Ma, “Learning
a simple low-light image enhancer from paired low-light instances,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2023,
pp. 22252–22261.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

[48] B. Fei et al., “Generative diffusion prior for unified image restoration and
enhancement,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
Jun. 2023, pp. 9935–9946.
[49] S. Yang, M. Ding, Y. Wu, Z. Li, and J. Zhang, “Implicit neural
representation for cooperative low-light image enhancement,” in Proc.
IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2023, pp. 12918–12927.
[50] Z. Liang, C. Li, S. Zhou, R. Feng, and C. C. Loy, “Iterative prompt
learning for unsupervised backlit image enhancement,” in Proc. IEEE
Int. Conf. Comput. Vis., 2023, pp. 8094–8103.
[51] S. Panagiotou and A. S. Bosman, “Denoising diffusion post-processing
for low-light image enhancement,” Pattern Recognit., vol. 156, Dec.
2024, Art. no. 110799.
[52] H. Jiang, A. Luo, X. Liu, S. Han, and S. Liu, “LightenDiffusion:
Unsupervised low-light image enhancement with latent-retinex diffusion
models,” in Proc. ECCV, 2024.
[53] Y. Jin, A. Sharma, and R. T. Tan, “DC-ShadowNet: Single-image hard
and soft shadow removal using unsupervised domain-classifier guided
network,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021,
pp. 5027–5036.
[54] P. Perona and J. Malik, “Scale-space and edge detection using
anisotropic diffusion,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 12,
no. 7, pp. 629–639, Jul. 1990.
[55] C.-M. Fan, T.-J. Liu, and K.-H. Liu, “Compound multi-branch feature
fusion for real image restoration,” 2022, arXiv:2206.02748.
PAPER_TEXT
