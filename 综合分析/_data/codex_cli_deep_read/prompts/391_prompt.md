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
# [391] D 3 Former: Dual-Decoder Dual-Transformer Reconstruction Network for Hyperspectral Anomaly Detection
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
编号：391
题名：D 3 Former: Dual-Decoder Dual-Transformer Reconstruction Network for Hyperspectral Anomaly Detection
年份：2025
DOI：10.1109/tgrs.2025.3614482
来源：IEEE Transactions on Geoscience and Remote Sensing
PDF：paper/10.1109_TGRS.2025.3614482.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：弱相关，分数 4
已有代码状态：已下载；TGRS-D3Former -> source\TGRS-D3Former

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\391.txt
- 原始字符数：70310
- 本次发送字符数：70310
- 是否截断：False

代码包：
- 仓库：TGRS-D3Former
  - URL：https://github.com/YKYANG01/TGRS-D3Former
  - 状态：downloaded
  - 本地目录：source\TGRS-D3Former
  - 顶层结构：README.md
  - 主要语言：
  - README 标题：TGRS-D3Former、TGRS-D3Former、TGRS-D3Former
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 63, 2025

5528215

D3Former: Dual-Decoder Dual-Transformer
Reconstruction Network for Hyperspectral
Anomaly Detection
Tan Guo , Member, IEEE, Yukun Yang , Fulin Luo , Senior Member, IEEE, Chuan Fu , Member, IEEE,
and Lei Zhang , Senior Member, IEEE

Abstract—Hyperspectral anomaly detection (HAD) aims to
identify and locate anomalous targets in hyperspectral image
(HSI) data that are significantly different from the surrounding
background or environment. Most existing deep learning (DL)
methods for HAD utilize reconstruction errors by reconstructing
the background, but they often result in equivalent reconstruction of both background and anomalies, failing to effectively
separate them. To address this issue, we propose a novel dualdecoder dual-transformer reconstruction network (D3 Former).
Specifically, we introduce a new background feature purification decoding task, which focuses attention on the background
direction during image reconstruction. In addition, we develop
an anomaly stripping auxiliary branch that uses an autoencoder
(AE) and dynamic large convolution kernels to mask anomalies
and learn local background information, further diminishing the
impact of anomalies on the reconstruction process. Furthermore,
we design a new cross-guided multihead self-attention mechanism
that integrates multiscale background attributes globally to
suppress anomalous pixels and guide the reconstruction of a
pure background. Finally, we adopt a synergistic optimization
(SYO) loss to achieve twofold suppression of potential anomalies
in both spatial–spectral and frequency domains, resulting in more
accurate detection. Extensive experiments on multiple datasets
demonstrate that our method outperforms existing state-of-theart approaches in detection performance. The codes are available
at https://github.com/YKYANG01/TGRS-D3Former.

Received 7 August 2025; accepted 19 September 2025. Date of publication
25 September 2025; date of current version 16 October 2025. This work
was supported in part by the National Natural Science Foundation of China
under Grant 62201109, Grant 62371076, and Grant 62501087; in part by
China Postdoctoral Science Foundation under Grant 2025T180950 and Grant
2025MD774183; in part by the New Chongqing Youth Innovative Talents
Project under Grant CSTB2024NSCQ-QCXMX0071; and in part by the
Natural Science Foundation of Chongqing under Grant CSTB2024NSCQMSX0393. (Corresponding author: Fulin Luo.)
Tan Guo is with the School of Communications and Information Engineering, Chongqing University of Posts and Telecommunications, Chongqing
400065, China, and also with the Key Laboratory of Monitoring, Evaluation and Early Warning of Territorial Spatial Planning Implementation,
Ministry of Natural Resources (LMEE), Chongqing 401147, China (e-mail:
guot@cqupt.edu.cn).
Yukun Yang is with the School of Communications and Information Engineering, Chongqing University of Posts and Telecommunications, Chongqing
400065, China (e-mail: yangyukun100@163.com).
Fulin Luo and Chuan Fu are with the College of Computer Science,
Chongqing University, Chongqing 400044, China (e-mail: luoflyn@163.com;
fuchuan@cqu.edu.cn).
Lei Zhang is with the School of Microelectronics and Communication Engineering, Chongqing University, Chongqing 400044, China (e-mail:
leizhang@cqu.edu.cn).
Digital Object Identifier 10.1109/TGRS.2025.3614482

Index Terms—Autoencoder (AE), dual-decoder, hyperspectral
anomaly detection (HAD), image reconstruction, transformer.

I. I NTRODUCTION

H

YPERSPECTRAL images (HSIs) are of significant
importance in remote sensing due to their ability to
identify fine spectral features of ground objects, particularly excelling in target detection and localization [1], [2].
Hyperspectral anomaly detection (HAD) involves identifying
anomalous targets with spectral features that are significantly
different from the background in the absence of prior information. HAD finds wide applications in fields such as Earth
sciences [3], remote sensing, agriculture, military, and environmental monitoring [4]. Anomalies typically refer to targets that
are significantly different from the background in the spectral
domain and occupy a very small area. In HAD tasks, the
lack of prior knowledge about targets and backgrounds makes
the separation of anomalies from the background be a key
challenge [5], [6]. To address this, various methods have been
proposed to model the background using different strategies
to detect anomalous targets that deviate from background patterns [7], [8]. Existing HAD methods are mainly categorized
into three types: statistical theory-based methods, representation learning-based methods, and deep learning (DL)-based
methods.
A. Statistical Theory-Based Methods
Statistical theory-based HAD methods typically model the
background using the statistical characteristics of HSI. Among
these, the Reed–Xiaoli (RX) detector is pioneering, assuming
a multivariate Gaussian distribution for the background and
detecting anomalies via the calculation of the Mahalanobis
distance between the global pixels and the background, thereby
acting as a global RX (GRX) detector [9]. To emphasize
local background features, local RX (LRX) [10] computes the
covariance matrix using a sliding window. Advanced methods,
such as the kernel isolation forest detector (KIFD) [11], use
the isolation forest algorithm to model local backgrounds.
Tao et al. [12] enhance anomaly detection (AD) with score
Fourier entropy (FrFE). The two-step generalized likelihood
ratio test (2S-GLRT) [13] employs a sliding double-window
technique to improve the accuracy of multipixel AD through
a two-step process.

1558-0644 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

5528215

B. Representation Learning-Based Methods
Most statistical theory-based AD methods assume that
the background conforms to a certain statistical distribution
model. However, due to the complexity of HSI backgrounds
and the interference from various factors, these assumptions
are difficult to meet in practice. In contrast, representationbased [14], [15] HAD methods reconstruct background pixels
using a dictionary, where anomalous pixels fail to reconstruct effectively, with reconstruction errors used for detection.
Representation learning encompass sparse representation (SR)
[16], collaborative representation (CR) [17], [18], and lowrank representation (LRR) [19], [20]. SR assumes background
samples are represented by a few atoms, while anomalies cannot be done. CR emphasizes collaborative relationships among
dictionary atoms, representing a pixel as a linear combination
of its neighbors [21]. Improved CR models include the CRbased detector (CRD) [22] and relaxed CR detector (RCRD)
[23]. LRR captures global structures by decomposing HSI
into a low-rank background and a sparse anomaly matrix.
Based on LRR theory, Li et al. [24] combined low-rank and
sparse decomposition with a mixture of Gaussian (LSDMMoG) using Manhattan distance to reduce noise effects.
To utilize local geometric structural information from HSI,
Feng et al. [25] proposed the local spatial constraint and
total variation (LSCTV) method. In [26], a learnable background endmember with subspace representation (LEBSR)
was developed to optimize background dictionary construction. He et al. [27] proposed the tensor low-rank approximation
(TLRA-MSL) model that combines spatial and spectral information for HAD.
C. DL-Based Methods
In recent years, DL [28] has made significant progress
in the fields of computer vision and remote sensing [29],
[30]. DL-based HAD methods enhance the ability to recognize backgrounds and anomalous targets by extracting deep
features. Common methods are divided into the similarity measurement-based models and the reconstruction-based
models.
Similarity measurement models use a convolutional neural
network (CNN) as the core framework, with pixel pairs
selected from labeled HSI during training to learn pixel
similarity for AD. Li et al. [31] proposed the CNN-based
detection (CNND) method outputs anomaly scores by comparing the differences between pixel pairs. Rao et al. [32]
designed a transferable Siamese network (TSN) that converts
pixel similarity into anomaly probabilities. However, these
methods rely heavily on the quantity and quality of labeled
data, resulting in limited transferability.
Relative to this, reconstruction-based unsupervised DL techniques have demonstrated their effectiveness and achieved
promising results in HAD tasks. Autoencoder (AE) [33] and
generative adversarial networks (GANs) [34] are among the
typically used network architectures. Jiang et al. [35] proposed
a weakly supervised GANs based on spectral constraints to
enhance the discriminative capability for anomalous targets.
To improve the network’s robustness in handling anomalies

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 63, 2025

and noise, some HAD methods consider the noise model
in AE, such as a fully convolutional AE (CAE, Auto-AD)
[36], and robust graph AE (RGAE) [37]. The guided AE
(GAED) [38] enhances the representation capability of the
background. In order to better refine background recovery,
SMCNet [39], KACNet [40], and some methods incorporate
masking strategies and clustering concepts have been proposed. Recently, self-supervised learning (SSL) AD techniques
have also garnered attention. SSL designs self-supervised tasks
in HAD by leveraging techniques such as contrastive learning
and masked reconstruction to enhance feature representation
and generalization ability. Combined with deep networks,
it constructs an efficient detection framework, providing an
effective label-free solution for HAD. In [41], a self-supervised
anomaly prior (SAP) network redefines the optimization criterion for anomalies in spatial structure. Sun et al. [42]
proposed a contrastive self-supervised background reconstruction (CSSBR) approach to improve the model’s transferability.
Other methods, such as NL2Net [43] and ACRL [44], enhance
surrounding background awareness by coupling nonlocal and
local features. Liu et al. [45] proposed a self-supervised
multiscale network (MSNet) that combines multiscale feature
extraction to address the issue of reconstructing anomalies
of different sizes. Approaches including PDBSNet [46] and
DirectNet [47] utilize blind spot networks to reduce the feature
representation of anomalies.
D. Motivation and Contributions
Although the established DL-based HAD methods have
made significant progress, there are still some challenging
issues that need to be addressed.
1) Most existing reconstruction-based HAD networks use a
single encoding–decoding structure to extract the latent
representation of the background. However, this limits
the depth and diversity of feature extraction, and the single encoding–decoding path also restricts the generation
of robust feature maps.
2) Existing background reconstruction-based HAD networks apply constraints on features only at the pixel
level, which makes it easy to reconstruct anomalies
in complex scenarios. They lack an active suppression
strategy for anomalies in the background reconstruction.
3) There is a lack of constraints on anomalies in the
frequency domain. In this case, the network learns
to recover information from all frequencies, resulting in high-frequency anomaly features being unconsciously restored, which lowers the purification of the
background.
To address these challenges, transformer [48], [49] has been
used in HAD due to its powerful capability for modeling
global dependencies [50], [51]. However, existing methods still
have shortcomings in suppressing potential anomalies and are
unable to effectively adapt to the requirements of AD.
Therefore, the core issue of HAD lies in how to effectively reconstruct background pixels through a specific feature
encoding–decoding mechanism, fully utilizing the spatial
correlations of the background area while eliminating the

GUO et al.: D3 FORMER: DUAL-DECODER DUAL-TRANSFORMER RECONSTRUCTION NETWORK FOR HAD

mapping contamination caused by anomalies. To address this
issue, this article proposes an end-to-end background reconstruction method based on a dual-decoder dual-transformer
reconstruction network (D3 Former). The newly designed dualdecoder structure can dynamically adjust its focus on the
background and anomalies, fully leveraging the extracted
global–local diversified features. It maps the uniform noise
space into the HSI space to learn the spatial dependencies
of the background and reduce the visibility of anomalous
targets. To further prevent the reconstruction of anomalous
pixels, an anomaly removal auxiliary branch is designed,
which combines a CAE with an anomaly masking attention
mechanism to effectively eliminate the significance of anomalous targets. This branch establishes an explicit suppression
pathway for the anomaly’s spatial–spectral structure. Notably,
our proposed background reconstruction architecture features
a unique cross-guided attention design that enhances the
statistical dependencies of the background while effectively
mitigating the spatial dependencies related to anomalous pixels. Different self-attention mechanisms cross-capture local
background features, improving background quality from the
perspective of structural feature complementarity. Furthermore, to improve the model’s reconstruction performance, we
introduce a synergistic optimization (SYO) loss function. By
utilizing a frequency-domain loss term, it compensates for
the limitation of reconstruction-based HAD methods that only
suppress anomalies in the spatial domain. This enhancement
penalizes anomalous targets more effectively in both the
spatial–spectral domain and the frequency domain through
background-prior mapping with weighting, allowing the model
to better separate anomalies from the background.
In summary, the novelty and main contributions of this
article are emphasized as follows.
1) To focus feature attention on the background during
reconstruction, we propose an end-to-end background
reconstruction method based on D3 Former. By incorporating a new background purification decoding task to
prevent the network from learning features of anomalous pixels. The dual-decoder framework provides a
combined bridge for different features, enabling the
complementary diversity of features, which makes the
generated background more robust.
2) To address the issue of anomaly contamination, we
develop an anomaly removal and masking auxiliary
branch (ARMAB) that utilizes AE and dynamic large
convolution kernels to blur anomalous targets, supplementing a comprehensive spatial–spectral background
information flow. In addition, we designed an innovative
cross-guided multihead attention mechanism that globally integrates multiscale background attributes, ensuring
that anomalies are not reconstructed.
3) To improve the quality of “anomaly-free” background
reconstruction, we employ an SYO loss function. By
introducing a new frequency-domain loss, we suppress potential anomalous components in both spatial
and frequency domains. The interaction between the
domains can also help preserve the texture details of the
background.

5528215

The remainder of this article is organized as follows.
Section II outlines the general architecture of our network
and elaborates on each component. In Section III, we validate
the effectiveness of our method through experiments. Finally,
Section IV presents the conclusion.
II. M ETHODOLOGY
In this section, we will provide a comprehensive presentation of our D3 Former. Section II-A introduces the
overall structural framework of our network. Following that,
Sections II-B–II-E delve into several key components of
our network, including dual-decoder, ARMAB, cross-guided
transformer module (CGTM), SYO loss function, background
feature fusion module (BFFM) and detection phase.
A. Overall Structure
The overall framework of the proposed D3 Former is shown
in Fig. 1. During inference, the testing HSI is input into the
fine feature (FF) encoder–decoder network, while uniform
noise is fed into the lower layer background purification
decoder (BPD) to simulate anomaly masking and reduce the
model’s visibility to anomalous targets. This dual-decoder
structure facilitates hierarchical background feature extraction,
improving the detection capability for diverse anomalies and
backgrounds. In the upper layer, the Swin transformer [52],
[53] module (SWTM) is employed as the feature extractor to
capture fine background features. The FF encoder features and
the BPD outputs are passed to the CGTM, explicitly guiding
attention toward background semantic information and reducing the weight of anomalous pixels. The processed features
are then integrated with the upper layer FF decoder outputs
using the BFFM to further enhance background reconstruction.
In addition, an auxiliary branch is designed for anomaly
separation, where anomalies features are extracted and masked
as supplementary inputs for the fused feature maps at each
stage, thereby improving the model’s anomaly suppression
capability. Finally, the model is iteratively optimized using
an SYO loss function, ensuring the generation of accurate
and realistic pure background images across different decoding
stages.
B. Dual-Decoder Structure for Background Reconstruction
Conventional U-shaped networks (UNet) use a single
encoder–decoder connection, which results in significant information loss when processing complex HSI. Increasing network
depth by stacking convolutional layers can improve feature
extraction, but it also inevitably leads to the reconstruction of
anomalies during background generation, reducing detection
performance. To overcome these challenges, we designed a
dual-decoder structure that facilitates feature sharing between
layers and extracts a precise background without anomalies. BPD provides a combinatorial bridge for the diverse,
nonanomalous background features, enhancing the robustness
and detail richness of the reconstructed background. In BPD,
all stages of background information, along with methods
for anomaly suppression, are fully utilized, ensuring that the
anomalies in the reconstruction background are suppressed as

5528215

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 63, 2025

Fig. 1. D3 Former for HAD. The observed HSI first undergoes the FF encoding and decoding process, and the uniform noise is fed into the lower layer BPD
to simulate anomaly-free input. CGTM enhances feature representation in background regions, while ARMAB reduces the weight of anomalous pixels. During
the detection stage, BFFM performs cross-stage feature fusion of background information from different layers to obtain the reconstructed “anomaly-free”
background HSI1 , and the final detection result is acquired via the difference between the “anomaly-free” background HSI1 and the original HSI.

Fig. 2. Illustration of our dual-decoder structure.

much as possible. This significantly improves the quality of
background reconstruction and detection accuracy.
Fig. 2 illustrates our dual-decoder structure based on UNet
design, featuring two parallel decoding subnetworks. To begin
with, we denote an HSI as X ∈ RH×W×C , H, W, and C
represent height, width, and spectral bands, respectively. The
encoder receives the original HSI as input and uses a 3 × 3
convolutional layer to change the number of channels from
C to N. The feature map then goes through two SWTMs,
followed by a 1×1 convolutional layer and a downsample layer
for shallow feature extraction. The downsample layer consists
of a 2 × 2 stride convolutional layer, which reduces the
spatial resolution of the feature map by half while doubling the
number of channels. The sizes of the feature maps for different
nodes become E1,2 ∈ RH/2×W/2×2N and E1,3 ∈ RH/4×W/4×4N ,
where subscript (·)i, j represents the jth feature extraction block
of the ith encoder or decoder. The bottleneck of the model is
a single SWTM, which further extracts features while keeping
the shape of the feature map B1,0 ∈ RH/4×W/4×4N unchanged.

Then, symmetrically with the encoder, the upper decoder uses
two 2 × 2 stride deconvolutional layers, a 1 × 1 convolutional
layer, and an SWTM for deep feature map representation
learning. After decoding, the size of the feature map returns
to H × W × C.
The BPD uses the mapped input noise Xu ∈ RH/4×W/4×4N ,
after passing through the bottleneck BFFM and upsample
layer to B2,0 ∈ RH/2×W/2×2N . Then, through skip connections,
the feature maps from the encoding and decoding stages of
the upper layer are passed to the CGTM and BFFM for
feature interaction, allowing the BPD to learn more contextual
information. After this stage, the final feature map generates
a real background X̂ ∈ RH×W×C .
C. Anomaly Removal and Masking Auxiliary Branch
In HAD, traditional deep models may lack sufficient information to learn the differences between anomalies and the
background. As a result, they attempt to reconstruct every part
of the input, including the anomalies. To enhance the differences between the background and anomaly target features
and to encourage the model not to focus on the anomalies, we
propose to construct an ARMAB, as shown in Fig. 3, which
includes the following several components.
1) Background Anomaly Separation: The previous stage
of the entire branch completes background reconstruction by
using a CAE to capture local features, providing a flow
of local feature information about the background from a
different structural perspective. In parallel, during the anomaly
separation process, the CAE preserves the overall details of
the background and further suppresses the reconstruction of
anomalies by using large kernel convolutions to reduce the
attention on anomalous pixels. The local feature information

GUO et al.: D3 FORMER: DUAL-DECODER DUAL-TRANSFORMER RECONSTRUCTION NETWORK FOR HAD

5528215

Fig. 3. Illustration of ARMAB.

flow enhances the local–global interaction from different
structural perspectives, providing supplementary information
for fine pure background reconstruction. The encoding block
consists of a 3 × 3 convolution (stride = 2) and a 1 × 1
convolution (with batch normalization and LeakyReLU). The
input of the ith encoding block can be represented as

Ei = Conv3×3 Conv1×1 (Ei−1 )
(1)
where 0 < i < 5. The decoding block consists of an upsample
layer and a 1 × 1 convolution (with batch normalization and
LeakyReLU). Combined with skip connections, it preserves
shallow features. The input of the decoding process can be
represented as


Di = Concat Ei−1 , Conv1×1 Upsample (Di−1 ) . (2)
The independent path of the CAE provides multiple reconstruction perspectives and distinguishes the background from
anomalies. As training progress, this subtraction approach
increasingly highlights the anomaly regions, removing some
redundant background information while preserving the overall background detail. In this way, our designed anomaly
masking mechanism utilizes the large kernel convolutions
in a feature space that has been preliminarily stripped and
dominated by the background, rather than struggling to identify anomalous targets in the original features. Based on the
separated feature map, subsequent large kernel convolutions
can effectively blur and suppress the residual anomaly components. The calculation method for the entire residual result
S is as follows:
2

Si, j = X(i, j,:) − X̂0(i, j,:) 2

(3)

where (·)i, j,: is the spectral vector at position (i, j).
2) Anomaly Feature Masking: After obtaining the separated
feature map S, S ∈ RH×W is replicated along the spectral
dimension using channel expansion operation, transforming
it into tensor S0 ∈ RH×W×C . Since anomalies are small and
isolated pixels, which occupy only a small portion of the space.
We introduce an anomaly masking mechanism to eliminate the
feature space mapping of anomaly information. In the anomaly

masking phase, we divide it into three parts to perform
hierarchical suppression of anomalies. First, we use a separate
large convolution kernel along with two sets of cascaded
large convolution kernels in parallel. Through hierarchical
extraction, anomalies are flattened by the convolution calculations of the surrounding background pixels. This reduces the
strong distinguishability of the anomalies, achieving a blurring
effect. The large convolution kernels provide a wider receptive
field, focusing on larger background areas, thereby “diluting”
and dispersing the anomalous information within the feature
maps S3



0
Dw
Dw
0
S3 = Concat WDw
(4)
5×5 S , W7×7 W5×5 S
where WDw
k×k represents 5 × 5 depth-wise convolution
(DwConv) and 7 × 7 DwConv.
Then, the obtained feature maps are passed through a
combination of mean pooling (MEP) and max pooling (MAP)
for processing. This process allows MEP to reduce the relative
value of anomalies and focus on the globally consistent background. MAP selects local background information, ensuring
that anomalies are no longer the focal point of the global information. Following this, a 1 × 1 convolution and an activation
function are applied to obtain the background selections W1
and W2

[W1 , W2 ] = Sigmoid Conv1×1 [MAE (S3 ) , MAX (S3 )] . (5)
The processed information is passed into two parallel convolutional structures and combined using element-wise addition
to reduce the prominence of anomalies in the fused feature
map. A channel attention mechanism is then applied to dynamically reduce the weights of channels containing anomalies.
The refined output is multiplied with the feature maps from the
convolutional structures, achieving multidimensional anomaly
suppression across channel, spatial, and scale levels. This
produces a final feature map that accurately represents background information, effectively masks anomalies, and provides
richer supplementary information for anomaly suppression
during decoding.

5528215

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 63, 2025

and V2 each undergo a 3 × 3 DwConv to yield K̃2 =
DwConv3×3 (K2 ) and Ṽ2 = DwConv3×3 (V2 ). Compared to
the decoding attention branch, we employ two DwConvs to
enhance the extraction of local abnormal features, and the subsequent operations are the same. Therefore, the computation
for the encoding multihead self-attention branch is as follows:
T !
Q̃i2 K̃i2
i
Ṽi2 .
(9)
Att2 = Softmax
√
d
Fig. 4. Schematic of CGTM.

D. Cross-Guided Transformer Module
Transformer models can strengthen features through global
attention. Although it performs well in capturing overall data
information, it still has limitations, such as insensitivity to
modeling local details and loss of complex background details.
To tackle these issues and enhance the model’s ability to distinguish between background and anomalies during training,
we introduce a new transformer CGTM in Fig. 4.
First, we apply the conditional position embedding (CPE)
[54] to the lower layer decoder input through a 3 × 3 DwConv
layer. Then, we divide the entire module into a decoding
multihead self-attention branch and an encoding multihead
self-attention branch. The input lower layer decoder information X1 and encoder information X2 are linearly project to
obtain the queries Q, keys K, and values V
Qi = Xi Wqi , Ki = Xi Wki , Vi = Xi Wvi
where Wqi ,

(6)

Wki , and Wvi represent the projection weights for

the Q, K, and V, respectively.
After the mapping is completed, the decoding multihead
attention branch performs background smoothing recovery by
capturing the spectral dimensional deep features of the decoding information. The obtained Q1 , K1 , and V1 is processed
using nonoverlapping windows (with a size of M×M) to yield
0 0
2
0
[Q̃1 , K̃1 , Ṽ1 ] ∈ RH W /M×M ×C . Subsequently, they are divided
into multiple heads along the channel dimension, as follows:


Q̃1 = Q̃11 , Q̃21 , . . . , Q̃h1


K̃1 = K̃11 , K̃21 , . . . , K̃h1


(7)
Ṽ1 = Ṽ11 , Ṽ21 , . . . , Ṽh1
where h represents the number of divided heads. During this
process, different attention heads can focus on the correlations
between different spectral bands, allowing for fine background
representation in the spectral dimension. Then, the multihead
self-attention mechanism is computed for each head, ensuring
that the model can more accurately describe the local details
in the background
T !
Q̃i1 K̃i1
i
Ṽi1 .
(8)
Att1 = Softmax
√
d
In the encoding multihead attention branch, we focus more
on the fine-grained background reconstruction of the encoded
information. Before the nonoverlapping window division, K2

To apply greater weight to the decoupled background
information, we establish a connection between the features
of the encoder and decoder. The attention output from the
decoding branch is used as the Q, while the K are derived
from the window-partitioned and V of the encoding branch’s
attention. The second combination of K1 and Att1 further
cross-fuses the related information with the encoded feature
values Att2 . This leads to a cross-guided attention computation
to restore background details, followed by rearrangement and
linear layers to integrate the multiple heads. The final attention
computation is as follows:
!!
T !
Atti1 K̃i1
i
Att2
(10)
Attout = Linear Re Softmax
√
d

where Re(·) indicates the rearrangement operation on the
0
0
0
tensor. Finally, Attout ∈ RH ×W ×C is passed through a
feedforward network.
CGTM jointly processes the inputs from the encoder and
decoder, leveraging the information exchange between them
to enhance the background confidence and weaken the local
spatial dependencies of anomalies.
E. SYO Loss
During iterative training, our goal is to align the background
pixels in the generated image with those in the original HSI
while suppressing the reconstruction of anomalous pixels.
Inspired by GAED [38], a background-priority mapping SYO
loss function is adopted for HAD, calculated as follows:
dn =

C
X


t i, j (c) − un (c)

2

(11)

c=1

where (n = 1, 2, . . . , 8) represents the number of subvolumes,
and t i, j (c) and un (c) denote the pixel values of the cth band at
position (i, j) for the HSI and the average vector of each subvolume, respectively. The spectral similarity score is computed
to update the pixel values and obtain the background-guided
map G, as follows:
 2
g x,y = max e−dn .
(12)
n

Therefore, the reconstruction loss in the spatial–spectral
domain is defined as follows:


Lm + L s = mse X, GX̂ + SmoothL1 X, GX̂0
(13)
where GX̂ is the Hadamard product result of G and X̂.

GUO et al.: D3 FORMER: DUAL-DECODER DUAL-TRANSFORMER RECONSTRUCTION NETWORK FOR HAD

The background-guided map assigns higher confidence to
background pixels and lower weights to anomalies, reducing
their influence in the loss function and suppressing anomalies.
The mse loss function preserves HSI’s spatial continuity and
spectral gradient characteristics of object edges, while the
SmoothL1 loss function is sensitive to large gradient changes
(e.g., anomalies) and robust to small changes (e.g., textures),
avoiding excessive punishment on edge details. To evaluate
reconstruction quality, we combine mse loss and SmoothL1
loss to balance anomaly suppression and the robustness of
background reconstruction in the task.
In practical image reconstruction tasks, important anomalies
details are often concentrated in the high-frequency components of the frequency domain. However, loss functions
such as mse and SmoothL1 tend to overlook these features
in the frequency domain, leading to the reconstruction of
anomalies. To solve this, we propose a new frequency-domain
loss [55] that transforms the image into the frequency domain
and compares distribution differences, improving sensitivity
to high-frequency anomalies. We combine mse, SmoothL1,
and frequency-domain losses to optimize background reconstruction and overcome the limitations of relying only on
high-frequency suppression. The SYO suppresses anomalies
in both spatial and frequency domains, while the losses also
optimize and preserve edge and texture details. The frequencydomain representation of the input image is obtained using a
discrete Fourier transform (DFT), as follows:
X (u, v) =

H−1 W−1
X
X

x (i, j) · e



vj
−i2π ui
H+W

.

(14)

i=0 j=0

The frequency mask is applied for separation, where
frequencies greater than the default distance threshold of
0.5 represent high-frequency components with rapid spatial
changes, corresponding to anomalies
(
1, if k f k > threshold
M (f) =
(15)
0, if k f k ≤ threshold

Xlow = X (u, v) · M̄ ( f ) , Xhigh = X (u, v) · M ( f )
(16)
where k f k = ( fu2 + fv2 )1/2 is the Euclidean distance of f (u, v)
and M̄( f ) = 1 − M( f ). The final frequency domain loss is
defined as a weighted sum of the two components
Lf =


 2
1
(1 − ω) Xlow − X̂low + ω Xhigh − X̂high F
HW
(17)

5528215

Algorithm 1 D3 Former
Input: 1) The observed HSI X ∈ RH×W×C ; 2) uniform noise
H
W
Xu ∈ R 4 × 4 ×4N .
Output: Final detection result R.
Stage 1: Training Phase;
1: X is processed by the FF encoder to extract abstract
background feature Ei, j .
2: ARMAB calculates the residual S using Eq. (3) and
performs anomaly masking on S to obtain a pure coarse
background information B.
3: Ei, j and Xu are restored into background features through
the FF decoder and BPD.
4: During the decoding phase, B is simultaneously delivered
to BPD as supplementary information.
5: The input data and pure background are used as training
targets for the reconstruction network D3 Former.
6: Minimize SYO loss function guides the model to suppress
anomalies.
7: Integrate background decoding feature Di, j from each
stage through BFFM.
8: Obtain the final reconstructed background HSI1 .
Stage 2: Detection Phase;
9: Compute the reconstruction residual for each pixel in X
by Eq. (19).

F. BFFM and Detection Phase
In this BFFM shown in Fig. 5, the output X1 from the lower
layer BPD and the output X3 from the upper layer FF decoder
are first concatenated along the channel dimension. The fused
feature map is then processed through a spatial attention
mechanism to enhance information interaction between different spatial locations, highlighting the key information in the
background. X1 and X3 are processed through depth attention
to capture important fine-grained background details.
Next, the output of the spatial attention is added to the result
of X3 after depth attention processing. This summed result
is then element-wise multiplied with the feature map of X1
after depth attention refining, enhancing important background
information while suppressing anomalous interference, generating the final output feature. The entire process maintains
background integrity through the collaborative effect of depth
attention and spatial attention, ultimately producing a clean
background X̂.
Finally, the reconstruction error is calculated to represent
the detection result as the following equation:
2

Ri, j = X(i, j,:) − X̂(i, j,:) 2
where ω is the weighting parameter that assigns a lower
weight to the high-frequency component to enhance anomaly
suppression. By using the above designs, a larger weight
is assigned to the background areas as much as possible,
thereby increasing their influence in the loss calculation. The
overall loss function is a joint constraint considering both
spatial–spectral and frequency domains as follows:
L = Lm + L s + L f .

(18)

(19)

where (·)i, j,: is the spectral vector at position (i, j). The detailed
steps of D3 Former are introduced in Algorithm 1.
III. E XPERIMENT R ESULT AND A NALYSIS
In the experiments, we validated the performance of the
D3 Former model on six real datasets. The D3 Former model
was implemented in Python (version 3.10.6) using the PyTorch
framework with PyCharm 2021.3 as the compiler. The computational environment was a computer equipped with an

5528215

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 63, 2025

where a, b, n ∈ RL×1 represent the spectral vectors of the
anomaly, background, and final mixture, respectively, while fa
denotes the abundance fraction of a. 25 targets were randomly
embedded in the subimage, with corresponding abundance fa
values ranging from 0.04 to 1.
B. Experimental Settings

Fig. 5. Schematic representation of BFFM.

NVIDIA 3090 24-GB GPU. The datasets, shown in Fig. 6,
include their pseudo-color images and corresponding ground
truth (GT) values.
A. Dataset Description
1) Pavia Dataset [33]: This real dataset was obtained from
an airborne sensor called the Reflective Optics System Imaging
Spectrometer (ROSIS), with a spatial resolution of 1.3 m and
a wavelength range of 430–860 nm. The image has a size of
100 × 100 with 102 spectral bands and contains 71 anomalies.
2) San Diego (SD) Dataset [56]: This HSI was captured by
the Airborne Visible/Infrared Imaging Spectrometer (AVIRIS)
sensor in San Diego, CA, USA, with a spatial resolution
of 3.5 m and a wavelength range of 370–2510 nm. The
spatial dimensions are 100 × 100, with 189 spectral bands,
excluding low signal-to-noise ratio (SNR) and absorption
bands. Referred to as SD, this HSI identifies 58 airport pixels
as anomalies.
3) Texas Coast (TC) Dataset [57]: The two city datasets
were captured by the AVIRIS sensor over the coast of Texas in
the USA in 2010. Both of these scenes have a spatial resolution
of 17.2 m and a size of 100 × 100 pixels. The first scene
contains 67 anomalous pixels and 204 spectral bands, with
a wavelength range of 450–1350 nm. Buildings of different
scales are considered anomalies. The second scene has 207
bands, and all bands were used in each experiment. These
two HSIs are referred to as TC-1 and TC-2.
4) Gainesville (GA) Dataset [57]: This dataset represents
an urban scene captured by the AVIRIS airborne sensor
in Gainesville, FL, USA. By removing water-absorbing and
SNR bands from the original data, 191 bands were retained
for experimentation. In addition, the dataset has a spatial
resolution of 3.5 m and a size of 100×100 pixels. This dataset
contains 156 anomalous pixels, accounting for 1.56% of the
entire image, which are yet to be explored.
5) Salinas Dataset [47]: The synthetic image was derived
from the AVIRIS sensor and selected a background subimage
from the Salinas scene. The anomalous target insertion method
was applied after using a linear mixing model and is written
as follows:
n = fa a + (1 − fa ) b
(20)

We selected ten methods for comparison, including GRX
[9], CRD [22], FrFE [12], RCRD [23], PCA-TLRSR [58],
LEBSR [26], GAED [38], Auto-AD [36], PDBSNet [46], and
MSNet [45]. GRX is a method based on probability distribution. CRD, RCRD, and PCA-TLRSR are representation-based
methods. FrFE employs frequency-domain transformations
to detect anomalies. LEBSR detects anomalies by learning
the background end members. GAED, Auto-AD, PDBSNet,
and MSNet reconstruct the background in a self-supervised
manner. For our method, the learning rate is set to 10−4 .
Training epochs and the regularization parameters ω were set
to 800, 600, 800, 600, and 1400, 0.1, 0.3, 0.3, 0.1, and 0.1
for the Pavia, SD, TC, GA, and Salinas datasets, respectively.
We suggest setting the training epochs within the range of
[600, 1000] to achieve more promising and stable learning
performance.
To measure the detection performance of different AD
methods, the receiver operating characteristic (ROC) curve is
widely used for intuitive observation. We use the ROC curves
of (P f , Pd ) and (P f , τ) to represent overall detection accuracy
and background suppression capability, respectively. P f and
Pd are related to τ, and they can be expressed as follows:
P(τ)
d =

FP(τ)
T P(τ)
, P(τ)
f =
Nano
Nbkg

(21)

where TP(τ) and FP(τ) denote the number of anomalies and
background pixels whose detection values are greater than a
given threshold τ, and Nano and Nbkg are the total number of
anomalies and background pixels.
C. Experimental Results and Analysis
1) Quantitative Comparisons: Table I shows the area
under the curve (AUC) values of the ROC curves, where
AUC(P f , Pd ) indicates detection accuracy, while AUC(P f , τ)
measures background suppression capability. From the table, it
can be seen that our proposed D3 Former method achieves the
highest score for AUC(P f , Pd ) across six datasets. Regarding
the AUC(P f , τ) for this method, it scored the lowest on five
datasets, while ranking second on the remaining dataset. Overall, D3 Former achieved the best average scores in AUC(P f , Pd )
and AUC(P f , τ) across all six datasets, owing to its effective
reconstruction of the background and suppression of anomalies
through the dual-decoder transformer network structure, which
in turn augments detection rates and background suppression
effectiveness.
2) Visual Comparisons: To visually reflect the detection
results, we present the detection outcomes of different AD
algorithms on six HSI datasets, as shown in Fig. 7. From
Fig. 7, it is evident that the RX algorithm misses many anomalous targets across these six datasets while misclassifying a

GUO et al.: D3 FORMER: DUAL-DECODER DUAL-TRANSFORMER RECONSTRUCTION NETWORK FOR HAD

5528215

Fig. 6. Pseudo-color image and GT of experimental datasets. (a) Pavia, (b) SD, (c) TC-1, (d) TC-2, (e) GA, and (f) Salinas.
TABLE I
AUC VALUES OF A LL C OMPARED M ETHODS ON D IFFERENT DATASETS

large number of background pixels. This is because RX is
based on simple statistical rules, which do not adapt well to
the complex statistical distributions of HSI data. Although the
CRD and RCRD methods present a relatively complete background, this leads to difficulties in distinguishing anomalies
from the background. FrFE and PCA-TLRSR also produce
many erroneous anomaly results during detection. While
LEBSR and Auto-AD are able to detect anomalous targets
across all datasets, the background is still quite pronounced.
In contrast, the GAED, PDBSNet, and MSNet methods effectively detect anomalies, with MSNet performing better in
terms of background suppression. Compared to the other
methods, the proposed D3 Former method not only successfully

detects anomalous targets but also effectively separates anomalies from the background, significantly improving detection
accuracy and achieving excellent background suppression.
To further qualitatively analyze the detection performance
of different methods, we present two ROC curves in Fig. 8.
For better visualization, they are displayed on a logarithmic
scale. The ROC curves of (P f , Pd ) and (P f , τ) are close to
the upper left and lower left corners, respectively, indicating
that the detector can achieve a high probability of detection
with low false alarms. From the ROC curve of (P f , Pd ),
D3 Former shows a higher detection probability across selected
datasets compared to other methods at various false alarm
rates. Overall, the proposed D3 Former method demonstrates

5528215

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 63, 2025

Fig. 7. Detection maps of different methods. (a) Pavia, (b) SD, (c) TC-1, (d) TC-2, (e) GA, and (f) Salinas.

Fig. 8. ROC curves of (P f , Pd ) and (P f , τ) for different methods on (a) Pavia, (b) SD, (c) GA, and (d) Salinas datasets.

superior performance on the ROC curve (P f , Pd ) compared
to other methods, while its performance on the ROC curve
(P f , τ) is lower than that of other methods. This indicates that
our method can maintain a high detection rate and a low false
positive rate across all datasets, thereby exhibiting consistency
in visual detection results, as shown in Fig. 8.
3) Separability Analysis: To evaluate the separation capability between the background and anomalies, Fig. 9 presents
box plots based on the detection values, revealing the separability of anomalous targets from background pixels, which is
used to measure detection performance. The red box plot represents anomalous targets, while the blue box plot represents
the background. Overall, different methods exhibit varying

separation effects across the datasets. A larger boundary
between the background and anomalies indicates that anomalous pixels can be more easily detected, suggesting better
detection performance of the method. In datasets such as SD
and TC-1, the anomalies from the RCRD and GAED methods
significantly overlap with the background, indicating their
weak separation capabilities. A small background box suggests
that the background is more concentrated, demonstrating a
strong background suppression effect. However, RCRD and
PCA-TLRSR exhibit a highly divergent background across
various datasets, showing significant limitations in background
suppression. In contrast, D3 Former shows almost no overlap
between the background and anomalies across the six datasets,

GUO et al.: D3 FORMER: DUAL-DECODER DUAL-TRANSFORMER RECONSTRUCTION NETWORK FOR HAD

5528215

Fig. 9. Background-anomaly separability results for different methods on (a) Pavia, (b) SD, (c) TC-1, (d) TC-2, (e) GA, and (f) Salinas datasets.

with the background appearing highly concentrated. These
results demonstrate that the method has significant advantages
in background suppression and anomaly separation.

TABLE II
A BLATION S TUDY OF D UAL -D ECODER W ITH
D IFFERENT N OISE C ONDITIONS

D. Validation of Network Structure
We first effectively simulate complex scenarios in HAD by
altering the input images of the BPD in the dual-decoder. In
addition, we introduce different network variants to conduct
extensive experiments on classic datasets to validate the effectiveness of our proposed D3 Former.
1) Distinct Inputs for BPD: We input two different images
into the encoder and BPD. One input is the original image,
while the other input is a different noise image. This effectively
simulates complex scenarios in HAD and enhances the robustness of the model. To demonstrate the effectiveness of the
noise modeling approach, we introduce three different noise
inputs for validation.
1) w/ Gaussian: In this variant, the input to the encoder
remains unchanged, while the input to the lower layer
BPD is transformed into an image of Gaussian noise.
2) w/ salt-pepper: In this variant, the input to the encoder
remains unchanged, while the input to the BPD is
transformed into an image of salt-and-pepper noise.
3) w/ striped: In this variant, the input to the encoder
remains unchanged, while the input to the BPD is
transformed into an image of stripe noise.
Table II shows the impact of using different noise inputs on
detection accuracy. The results indicate that the use of uniform
noise leads to better detection performance. The uniform noise
is evenly distributed without prominent patterns, preventing
the model from extracting abnormal spatial–spectral features.
At the same time, it can simulate the uniform statistical

distribution of background, serving as a foundation for the
model to reconstruct the estimated pure background in combination with the structured features. The introduction of
uniform noise mainly prevents the model from learning
anomalies and preliminarily establishes the background statistical distribution. In contrast, the Gaussian noise follows
a specific statistical distribution, which will guide the model
to fit Gaussian characteristics and may mistakenly learn
anomalies. Salt-pepper noise introduces extreme pixel-level
values, increasing the risk of false alarms. Meanwhile, the
strong directional structure of striped noise will interfere with
background learning.
2) Dual-Decoder: We employ a dual-decoder structure
with different inputs to extract more meaningful supplementary
information, enriching the communication of contextual information and enabling strong constraints on anomalies during
background reconstruction. To demonstrate the effectiveness of
our dual-decoder, we introduce four different network variants
under mse for validation.
1) w/o BPD and ARMAB: Variant 1, we directly remove
the entire BPD part, retaining the FF encoder–decoder
components in the network.

5528215

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 63, 2025

TABLE III
A BLATION S TUDY OF D UAL -D ECODER S TRUCTURE W ITH D IFFERENT N ETWORK M ODULES

TABLE IV
A BLATION E XPERIMENTS ON S IX DATASETS

2) w/BFFM: Variant 2, we directly remove the entire BPD
portion, retaining the FF encoder–decoder components
and BFFM.
3) w/CNN: Variant 3, we modify the BPD structure by
adopting a standard convolutional framework, composed of convolutional layers, batch normalization, and
LeakyReLU.
4) w/CNN and ARMAB: Variant 4, we retain the use of
the CNN framework for BPD and ARMAB.
Table III presents the results of the ablation study on the
dual-decoder. When removing the entire lower layer BPD, and
leaving only the FF encoder and decoder, the AUC(Pd , P f )
value significantly decreases across the datasets. This suggests
the dual-decoder structure captures more useful information,
improving feature reconstruction. Adding BFFM alone has
little effect on AUC(Pd , P f ), indicating that the role of the
dual-decoder architecture is to serve as a bridge for introducing
diverse feature processing for ARMAB and CGTM, enabling
more refined background recovery. In comparison, using the
traditional CNN framework for the BPD results in a decrease
in the AUC(Pd , P f ) values by 1.91%, 1.55%, 1.03%, 1.37%,
1.43%, and 1.24% on the six datasets. This demonstrates
that our designed dual-transformer structure in CGTM better
integrates features at different levels and effectively mitigates
the influence of anomalous targets during background fusion.
Furthermore, when adding ARMAB to the CNN framework, a
significant improvement in the AUC(Pd , P f ) value is achieved,
further validating that ARMAB can significantly help recover
lost edge and texture details.

Fig. 10. Output map of the reconstruction results on the SD scene. (a) Original
HSI, (b) remove the BPD, (c) only use CNN, and (d) ours.

Fig. 10 shows the background reconstruction results for
the two variants and our D3 Former on the SD scene across
four different spectral bands. When the BPD is removed,
the generated background image in Fig. 10(b) prominently
reconstructs the aircraft as an anomalous target, and the background appears quite blurry. This emphasizes the importance
of our dual-decoder in preserving the spatial correlation of
the background. In Fig. 10(c), although using a traditional
CNN as the BPD shows a trend of suppressing anomalies,

GUO et al.: D3 FORMER: DUAL-DECODER DUAL-TRANSFORMER RECONSTRUCTION NETWORK FOR HAD

the anomalies are still inevitably reconstructed. In contrast,
the CGTM in the dual-decoder, as illustrated in (d), can
clearly eliminate anomalies, ensuring a cleaner anomaly-free
background.

5528215

TABLE V
A BLATION S TUDY OF O UR D 3 F ORMER W ITH D IFFERENT
C OMBINATIONS OF L OSS F UNCTIONS

E. Ablation Study
1) Specific Module Ablation: To further illustrate the rationality and effectiveness of the design of each module, we
use a dual-decoder network that only includes SWTM and
BFFM as the baseline for D3 Former. The proposed D3 Former
method mainly includes ARMAB, CGTM, and SYO loss, and
we analyze the impact of each component for the model.
Table IV shows the results of the overall ablation experimental
results. We observed that using CGTM alone can enhance
the model’s background representation capability, which led
to higher AUC(Pd , P f ) values. The introduction of the SYO
loss function, as a regularization mechanism in the frequency
domain, can further suppress anomalies. Upon comparison,
adding ARMAB alone can significantly improve detection
accuracy for each dataset, indicating that ARMAB is effective in suppressing anomalies as well as pure background
reconstruction. This is because ARMAB can explicitly model
the anomaly masking mechanism and promote the model
to filter out anomalies. The combination of ARMAB and
CGTM results in an average AUC(Pd , P f ) value improvement
of 2.22%, as CGTM can weaken the local spatial dependencies
of anomalies through cross-layer attention, making it harder
for anomalous features to be retained during multiscale feature
fusion. In summary, the core of our method is to combine the
advantages of these modules through collaborative ensemble
optimization. As a result, our D3 Former achieves the highest
AUC(Pd , P f ) value and the lowest AUC(P f , τ) value.
2) Different Loss Functions: To investigate the benefits of
different loss functions, we have compared our SYO with five
combinations of loss functions.
1) w/mse: Combination 1, we optimize HSI1 only using the
mse loss function.
2) w/L f : Combination 2, we optimize HSI1 only using the
frequency-domain loss function L f .
3) w/mse+mse: Combination 3, we simultaneously constrain both HSI1 and HSI2 using mse loss function.
4) w/mse+SmoothL1: Combination 4, we simultaneously
constrain both HSI1 and HSI2 using mse and SmoothL1
loss functions.
5) w/mse+mse+L f : Combination 5, we simultaneously
constrain both HSI1 and HSI2 using mse and L f loss
functions.
Table V reports the AUC performance for different combinations of loss functions. It can be observed that using the
frequency-domain loss L f alone shows good performance in
improving the AUC (Pd , P f ) value. This suggests that L f
can suppress the high-frequency components dominated by
anomalies, while having a relatively small impact on texture
detail suppression. Applying the mse loss function to optimize
both HSI1 and HSI2 can improve the AUC performance,
indicating that it plays a positive role in regulating the supplementary background information. Replacing the mse loss

TABLE VI
C OMPARED W ITH SSL H AD M ETHODS

function with the SmoothL1 loss function can yield even better
performance, confirming that the smoothing property of the
SmoothL1 loss function reduces the dominance of anomalous
pixels. To further verify the anomaly suppression capability
of the frequency-domain loss L f , synergizing it with mse and
SmoothL1 achieves the best detection performance. To some
extent, the introduction of L f loss function and the SYO
loss function can balance anomaly suppression with texture
preservation, significantly improving the model’s performance.
F. Relationship With SSL HAD Methods
To illustrate the relationship between our method and
SSL HAD methods, a comparison of the performance of
the recent SSL methods on three datasets is presented, as
shown in Table VI. Overall, the proposed D3 Former performs the best. By contrast, the NL2Net [43] focuses on
spatial feature modeling, while our D3 Former introduces a
frequency-domain suppression mechanism, which can suppresses anomalies more comprehensively when reconstructing
the background. In addition, although both D3 Former and
MSNet [45] adopt a multiscale structure, D3 Former introduces
a dual-decoder structure based on a transformer that considers feature diversity, enabling more refined reconstruction of
background features. Compared to other SSL methods such
as CSSBR [42] and SAP [41], these new frameworks (such
as transfer learning) can be incorporated into our future work.
This would further improve the generalization and adaptability
of the proposed method, making it better suited for practical
engineering applications.
G. Discussion
To verify the originality and versatility of the proposed
D3 Former, we conduct a comparative analysis using different
background priors and applying them to various methods.
Although our method borrows the background guidance map
G from GAED, it modifies it through an adaptive weighting
strategy. As shown in Table VII, comparative experiments

5528215

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 63, 2025

R EFERENCES

TABLE VII
P ERFORMANCE OF O UR D 3 F ORMER U SING
D IFFERENT BACKGROUND P RIORS

TABLE VIII
U SE OF BACKGROUND P RIORS IN D IFFERENT H AD M ETHODS

show that even when replacing the background guidance map
G with some other simple and representative background
guidance maps, such as the classical RX [9] predetection
and background weight map M [36], our model’s detection
accuracy remains superior, far outperforming most of the
comparison methods in Table I. This strongly proves that the
benefits of our architecture and modules are the cornerstone
of performance.
As shown in Table VIII, we applied the background guidance map G from GAED to different detection frameworks,
such as the Auto-AD [36] and MSNet [45], and the results
show that the detection accuracy of these detection frameworks
did not significantly improve, with only a marginal performance enhancement (compared in Table I). In addition, our
method’s accuracy consistently exceeds that these detection
frameworks equipped with the background guidance map G
from GAED, as well as the original GAED. This clearly
demonstrates that G is not the key to the superior performance
of our D3 Former model. Instead, it is the combination of our
original network architecture and modules that achieves the
two key goals in HAD, i.e., pure background reconstruction
and anomaly suppression. As a result, our method outperforms
existing SOTA approaches in terms of detection performance.
IV. C ONCLUSION
In this article, we propose a novel network called
D3 Former for HAD. Differing from previous HAD methods,
D3 Former promotes information flow interaction to model
the anomaly-free background by introducing a dual-decoder
and dual-transformer structure. Specifically, we design an
anomaly feature cleaning auxiliary task during the pure background decoding phase and leverage CGTM to guide the
clean reconstruction of the background, further diminishing
the representation of anomalies. In addition, by synergistically optimizing the loss function, we achieve suppression
of anomalies in both the spatial–spectral and frequency
domains. Extensive experimental results demonstrate that
D3 Former outperforms current state-of-the-art methods on
multiple benchmarks.

[1]

C.-I. Chang, “Effective anomaly space for hyperspectral anomaly
detection,” IEEE Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no.
5526624.
[2] J. Li, X. Wang, H. Zhao, and Y. Zhong, “Learning a cross-modality
anomaly detector for remote sensing imagery,” IEEE Trans. Image
Process., vol. 33, pp. 6607–6621, 2024.
[3] R. Zhao, Z. Yang, X. Meng, and F. Shao, “A novel fully convolutional
auto-encoder based on dual clustering and latent feature adversarial
consistency for hyperspectral anomaly detection,” Remote Sens., vol. 16,
no. 4, p. 717, Feb. 2024.
[4] B. Tu, X. Yang, W. He, J. Li, and A. Plaza, “Hyperspectral anomaly
detection using reconstruction fusion of quaternion frequency domain
analysis,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 6,
pp. 8358–8372, Jun. 2024.
[5] J. Li et al., “Deep learning in multimodal remote sensing data fusion:
A comprehensive review,” Int. J. Appl. Earth Observ. Geoinf., vol. 112,
Aug. 2022, Art. no. 102926.
[6] C. Li, B. Zhang, D. Hong, X. Jia, A. Plaza, and J. Chanussot, “Learning
disentangled priors for hyperspectral anomaly detection: A coupling
model-driven and data-driven paradigm,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 36, no. 4, pp. 6883–6896, Apr. 2025.
[7] L. Wang, X. Wang, A. Vizziello, and P. Gamba, “RSAAE: Residual
self-attention-based autoencoder for hyperspectral anomaly detection,”
IEEE Trans. Geosci. Remote Sens., vol. 61, 2023, Art. no. 5510614.
[8] R. Zhao, B. Du, L. Zhang, and L. Zhang, “A robust background
regression based score estimation algorithm for hyperspectral anomaly
detection,” ISPRS J. Photogramm. Remote Sens., vol. 122, pp. 126–144,
Dec. 2016.
[9] I. S. Reed and X. Yu, “Adaptive multiple-band CFAR detection of an
optical pattern with unknown spectral distribution,” IEEE Trans. Acoust.,
Speech, Signal Process., vol. 38, no. 10, pp. 1760–1770, Oct. 1990.
[10] J. M. Molero, E. M. Garzon, I. Garcia, and A. Plaza, “Analysis and
optimizations of global and local versions of the RX algorithm for
anomaly detection in hyperspectral data,” IEEE J. Sel. Topics Appl.
Earth Observ. Remote Sens., vol. 6, no. 2, pp. 801–814, Apr. 2013.
[11] S. Li, K. Zhang, P. Duan, and X. Kang, “Hyperspectral anomaly
detection with kernel isolation forest,” IEEE Trans. Geosci. Remote
Sens., vol. 58, no. 1, pp. 319–329, Jan. 2020.
[12] R. Tao, X. Zhao, W. Li, H.-C. Li, and Q. Du, “Hyperspectral anomaly
detection by fractional Fourier entropy,” IEEE J. Sel. Topics Appl. Earth
Observ. Remote Sens., vol. 12, no. 12, pp. 4920–4929, Dec. 2019.
[13] J. Liu, Z. Hou, W. Li, R. Tao, D. Orlando, and H. Li, “Multipixel
anomaly detection with unknown patterns for hyperspectral imagery,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 10, pp. 5557–5567,
Oct. 2022.
[14] R. Zhao, B. Du, and L. Zhang, “Hyperspectral anomaly detection via
a sparsity score estimation framework,” IEEE Trans. Geosci. Remote
Sens., vol. 55, no. 6, pp. 3208–3222, Jun. 2017.
[15] R. Zhao, B. Du, L. Zhang, and L. Zhang, “Beyond background feature
extraction: An anomaly detection algorithm inspired by slowly varying
signal analysis,” IEEE Trans. Geosci. Remote Sens., vol. 54, no. 3,
pp. 1757–1774, Mar. 2016.
[16] Q. Ling, Y. Guo, Z. Lin, and W. An, “A constrained sparse representation model for hyperspectral anomaly detection,” IEEE Trans. Geosci.
Remote Sens., vol. 57, no. 4, pp. 2358–2371, Apr. 2019.
[17] S. Chang and P. Ghamisi, “Nonnegative-constrained joint collaborative representation with union dictionary for hyperspectral anomaly
detection,” IEEE Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no.
5534913.
[18] R. Zhao, B. Du, and L. Zhang, “A robust nonlinear hyperspectral
anomaly detection approach,” IEEE J. Sel. Topics Appl. Earth Observ.
Remote Sens., vol. 7, no. 4, pp. 1227–1234, Apr. 2014.
[19] G. Liu, Z. Lin, S. Yan, J. Sun, Y. Yu, and Y. Ma, “Robust recovery
of subspace structures by low-rank representation,” IEEE Trans. Pattern
Anal. Mach. Intell., vol. 35, no. 1, pp. 171–184, Jan. 2013.
[20] T. Guo, Y. Yang, L. He, C. Fu, and F. Luo, “Anomaly detection of
hyperspectral image by coarse-to-fine tensor two-level decomposition,”
IEEE Geosci. Remote Sens. Lett., vol. 22, pp. 1–5, 2025.
[21] M. Xu, J. Zhang, S. Liu, and H. Sheng, “Hyperspectral anomaly
detection based on adaptive background dictionary construction and
collaborative representation,” Int. J. Remote Sens., vol. 45, no. 10,
pp. 3349–3369, May 2024.
[22] W. Li and Q. Du, “Collaborative representation for hyperspectral
anomaly detection,” IEEE Trans. Geosci. Remote Sens., vol. 53, no. 3,
pp. 1463–1474, Mar. 2015.

GUO et al.: D3 FORMER: DUAL-DECODER DUAL-TRANSFORMER RECONSTRUCTION NETWORK FOR HAD

[23] Z. Wu et al., “Hyperspectral anomaly detection with relaxed collaborative representation,” IEEE Trans. Geosci. Remote Sens., vol. 60, 2022,
Art. no. 5533417.
[24] L. Li, W. Li, Q. Du, and R. Tao, “Low-rank and sparse decomposition
with mixture of Gaussian for hyperspectral anomaly detection,” IEEE
Trans. Cybern., vol. 51, no. 9, pp. 4363–4372, Sep. 2021.
[25] R. Feng, H. Li, L. Wang, Y. Zhong, L. Zhang, and T. Zeng, “Local spatial
constraint and total variation for hyperspectral anomaly detection,” IEEE
Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no. 5512216.
[26] T. Guo, L. He, F. Luo, X. Gong, L. Zhang, and X. Gao, “Learnable
background endmember with subspace representation for hyperspectral
anomaly detection,” IEEE Trans. Geosci. Remote Sens., vol. 62, 2024,
Art. no. 5501513.
[27] X. He, J. Wu, Q. Ling, Z. Li, Z. Lin, and S. Zhou, “Anomaly
detection for hyperspectral imagery via tensor low-rank approximation
with multiple subspace learning,” IEEE Trans. Geosci. Remote Sens.,
vol. 61, 2023, Art. no. 5509917.
[28] X. Cheng et al., “Deep feature aggregation network for hyperspectral
anomaly detection,” IEEE Trans. Instrum. Meas., vol. 73, pp. 1–16,
2024.
[29] B. Du, R. Zhao, L. Zhang, and L. Zhang, “A spectral–spatial based local
summation anomaly detection method for hyperspectral images,” Signal
Process., vol. 124, pp. 115–131, Jul. 2016.
[30] Z. Yang et al., “A multi-scale mask convolution-based blind-spot
network for hyperspectral anomaly detection,” Remote Sens., vol. 16,
no. 16, p. 3036, Aug. 2024.
[31] W. Li, G. Wu, and Q. Du, “Transferred deep learning for anomaly
detection in hyperspectral imagery,” IEEE Geosci. Remote Sens. Lett.,
vol. 14, no. 5, pp. 597–601, May 2017.
[32] W. Rao, Y. Qu, L. Gao, X. Sun, Y. Wu, and B. Zhang, “Transferable
network with Siamese architecture for anomaly detection in hyperspectral images,” Int. J. Appl. Earth Observ. Geoinf., vol. 106, Feb. 2022,
Art. no. 102669.
[33] Z. Wu et al., “Background-guided deformable convolutional autoencoder
for hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote
Sens., vol. 61, 2023, Art. no. 5531816.
[34] D. Wang, L. Gao, Y. Qu, X. Sun, and W. Liao, “Frequency-to-spectrum
mapping GAN for semisupervised hyperspectral anomaly detection,”
CAAI Trans. Intell. Technol., vol. 8, no. 4, pp. 1258–1273, Dec. 2023.
[35] T. Jiang, W. Xie, Y. Li, J. Lei, and Q. Du, “Weakly supervised
discriminative learning with spectral constrained generative adversarial
network for hyperspectral anomaly detection,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 33, no. 11, pp. 6504–6517, Nov. 2022.
[36] S. Wang, X. Wang, L. Zhang, and Y. Zhong, “Auto-AD: Autonomous
hyperspectral anomaly detection network based on fully convolutional
autoencoder,” IEEE Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no.
5503314.
[37] G. Fan, Y. Ma, X. Mei, F. Fan, J. Huang, and J. Ma, “Hyperspectral
anomaly detection with robust graph autoencoders,” IEEE Trans. Geosci.
Remote Sens., vol. 60, 2022, Art. no. 5511314.
[38] P. Xiang, S. Ali, S. K. Jung, and H. Zhou, “Hyperspectral anomaly
detection with guided autoencoder,” IEEE Trans. Geosci. Remote Sens.,
vol. 60, 2022, Art. no. 5538818.
[39] Z. Wu et al., “SMCNet: Sparse-inspired masked convolutional network
for hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote
Sens., vol. 62, 2024, Art. no. 5535317.
[40] Z. Wu, H. Lu, M. E. Paoletti, H. Su, W. Jing, and J. M. Haut,
“KACNet: Kolmogorov-Arnold convolution network for hyperspectral
anomaly detection,” IEEE Trans. Geosci. Remote Sens., vol. 63, 2025,
Art. no. 5506514.
[41] Y. Liu, K. Jiang, W. Xie, J. Zhang, Y. Li, and L. Fang, “Hyperspectral
anomaly detection with self-supervised anomaly prior,” Neural Netw.,
vol. 187, Jul. 2025, Art. no. 107294.

5528215

[42] X. Sun, Y. Zhang, Y. Dong, and B. Du, “Contrastive self-supervised
learning-based background reconstruction for hyperspectral anomaly
detection,” IEEE Trans. Geosci. Remote Sens., vol. 63, 2025, Art. no.
5504312.
[43] D. Wang, L. Ren, X. Sun, L. Gao, and J. Chanussot, “Nonlocal and
local feature-coupled self-supervised network for hyperspectral anomaly
detection,” IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens.,
vol. 18, pp. 6981–6993, 2025.
[44] J. Zhang et al., “A light CNN based on residual learning and background
estimation for hyperspectral anomaly detection,” Int. J. Appl. Earth
Observ. Geoinf., vol. 132, Aug. 2024, Art. no. 104069.
[45] H. Liu, X. Su, X. Shen, and X. Zhou, “MSNet: Self-supervised
multiscale network with enhanced separation training for hyperspectral
anomaly detection,” IEEE Trans. Geosci. Remote Sens., vol. 62, 2024,
Art. no. 5520313.
[46] D. Wang, L. Zhuang, L. Gao, X. Sun, M. Huang, and A. J. Plaza,
“PDBSNet: Pixel-shuffle downsampling blind-spot reconstruction network for hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote
Sens., vol. 61, May 2023, Art. no. 5511914.
[47] D. Wang, L. Zhuang, L. Gao, X. Sun, X. Zhao, and A. Plaza, “Sliding
dual-window-inspired reconstruction network for hyperspectral anomaly
detection,” IEEE Trans. Geosci. Remote Sens., vol. 62, 2024, Art. no.
5504115.
[48] Z. Wu and B. Wang, “Transformer-based autoencoder framework
for nonlinear hyperspectral anomaly detection,” IEEE Trans. Geosci.
Remote Sens., vol. 62, 2024, Art. no. 5508015.
[49] J. Lian, L. Wang, H. Sun, and H. Huang, “GT-HAD: Gated transformer
for hyperspectral anomaly detection,” IEEE Trans. Neural Netw. Learn.
Syst., vol. 36, no. 2, pp. 3631–3645, Feb. 2025.
[50] S. Xiao, T. Zhang, Z. Xu, J. Qu, S. Hou, and W. Dong, “Anomaly detection of hyperspectral images based on transformer with spatial–spectral
dual-window mask,” IEEE J. Sel. Topics Appl. Earth Observ. Remote
Sens., vol. 16, pp. 1414–1426, 2023.
[51] Z. He, D. He, M. Xiao, A. Lou, and G. Lai, “Convolutional
transformer-inspired
autoencoder
for
hyperspectral
anomaly
detection,” IEEE Geosci. Remote Sens. Lett., vol. 20, pp. 1–5,
2023.
[52] Z. Liu et al., “Swin transformer: Hierarchical vision transformer using
shifted windows,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2021, pp. 10012–10022.
[53] Z. Li, Y. Wang, C. Xiao, Q. Ling, Z. Lin, and W. An, “You only
train once: Learning a general anomaly enhancement network with random masks for hyperspectral anomaly detection,” IEEE Trans. Geosci.
Remote Sens., vol. 61, 2023, Art. no. 5506718.
[54] X. Chu, Z. Tian, B. Zhang, X. Wang, and C. Shen, “Conditinal positional encodings for vision transformers: Hierarchical vision transformer
using shifted windows,” in Proc. Int. Conf. Learn. Represent. (ICLR),
May 2023, pp. 1–19.
[55] L. Jiang, B. Dai, W. Wu, and C. C. Loy, “Focal frequency loss for image
reconstruction and synthesis,” in Proc. IEEE/CVF Int. Conf. Comput. Vis.
(ICCV), Oct. 2021, pp. 13919–13929.
[56] X. Yang, B. Tu, Q. Li, J. Li, and A. Plaza, “Graph evolutionbased vertex extraction for hyperspectral anomaly detection,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 35, no. 12, pp. 17372–17386,
Dec. 2024.
[57] X. Kang, X. Zhang, S. Li, K. Li, J. Li, and J. A. Benediktsson, “Hyperspectral anomaly detection with attribute and edgepreserving filters,” IEEE Trans. Geosci. Remote Sens., vol. 55, no. 10,
pp. 5600–5611, Oct. 2017.
[58] M. Wang, Q. Wang, D. Hong, S. K. Roy, and J. Chanussot, “Learning tensor low-rank representation for hyperspectral
anomaly detection,” IEEE Trans. Cybern., vol. 53, no. 1, pp. 679–691,
Jan. 2023.
PAPER_TEXT
