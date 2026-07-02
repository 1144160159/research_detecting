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
# [427] FC2P: Feature Cross-Channel Projection for Unsupervised Anomaly Segmentation
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
编号：427
题名：FC2P: Feature Cross-Channel Projection for Unsupervised Anomaly Segmentation
年份：2025
DOI：10.1109/tim.2025.3608319
来源：IEEE Transactions on Instrumentation and Measurement
PDF：paper/10.1109_TIM.2025.3608319.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测
相关性：弱相关，分数 3
已有代码状态：已下载；work-2 -> source\work-2

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\427.txt
- 原始字符数：70751
- 本次发送字符数：70751
- 是否截断：False

代码包：
- 仓库：work-2
  - URL：https://github.com/Karma1628/work-2
  - 状态：downloaded
  - 本地目录：source\work-2
  - 顶层结构：README.md、fc2p/
  - 主要语言：Python:15
  - README 标题：work-2、work-2、work-2
  - README 运行线索：
  - 关键文件：{"推理/演示入口": ["fc2p/main.py"], "数据处理入口": ["fc2p/models/extraction_builder.py"], "模型定义": ["fc2p/models/model_utils.py"]}
  - 数据集线索：MVTec、Tor、dapt、mvtec、tor

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

5044613

FC2P: Feature Cross-Channel Projection for
Unsupervised Anomaly Segmentation
Yichi Chen , Weizhi Xian , Junjie Wang , Graduate Student Member, IEEE,
Xian Tao , Senior Member, IEEE, and Bin Chen

Abstract—Unsupervised anomaly segmentation plays a critical
role in real-world industrial product quality inspection. While
feature reconstruction-based methods have shown promising
performance by detecting anomalies through differences between
pretrained features and their reconstructions, existing approaches
often suffer from shortcut learning, and leading to reconstruction
failures and inaccurate anomaly representation across multistage features. To address these limitations, we propose feature
cross-channel projection (FC2 P), a novel approach for anomaly
segmentation. FC2 P divides features into two subsets based
on neighboring channels and employs two autoencoders for
closed-loop prediction, effectively mitigating shortcut effects while
capturing semantic relationships for efficient reconstruction. In
addition, we introduce an anomaly exposure network (AExNet),
which progressively amplifies anomalies across multistage feature
residuals, generating precise anomaly score maps for accurate segmentation. Extensive experiments on MVTec AD and
Visa benchmark datasets demonstrate that the proposed FC2 P
achieves state-of-the-art (SOTA) performance, with average precision (AP) scores of 79.8% and 44.8%, respectively. Moreover,
visualization results on real industrial data further show the
practicality of our proposed method. The code will be made
publicly available at https://github.com/Karma1628/work-2 to
ensure reproducibility and facilitate further research.
Index Terms—Anomaly detection, anomaly segmentation, feature cross-channel projection (FC2 P), feature reconstruction,
self-supervised learning.

I. I NTRODUCTION

A

NOMALY segmentation aims at detecting pixels that
deviate from normal behavior within an image. Many

Received 4 June 2025; accepted 26 August 2025. Date of publication
10 September 2025; date of current version 18 September 2025. This work was
supported in part by the National Natural Science Foundation of China under
Grant 62373350; in part by the Youth Innovation Promotion Association,
Chinese Academy of Sciences (CAS), under Grant 2023145; in part by the
Natural Science Foundation of Chongqing under Grant CSTB2023NSCQMSX0070; in part by the Science and Technology Project of Shenzhen under
Grant GXWD-20220811170603002; and in part by the Beijing Nova Program
under Grant 20240484687. The Associate Editor coordinating the review
process was Dr. Xianqiang Yang. (Corresponding author: Xian Tao.)
Yichi Chen is with Chengdu Institute of Computer Application, Chinese
Academy of Sciences, Chengdu 610041, China (e-mail: chenyichi21@
mails.ucas.ac.cn).
Weizhi Xian is with Chongqing Research Institute, Harbin Institute of
Technology, Chongqing 401151, China (e-mail: wasxxwz@163.com).
Junjie Wang and Bin Chen are with the International Research Institute
for Artificial Intelligence, Harbin Institute of Technology, Shenzhen 518000,
China (e-mail: jjwanghz@stu.hit.edu.cn; chenbin2020@hit.edu.cn).
Xian Tao is with the Institute of Automation, Chinese Academy of Sciences,
Beijing 100190, China, and also with the School of Artificial Intelligence,
University of Chinese Academy of Sciences, Beijing 100049, China (e-mail:
taoxian2013@ia.ac.cn).
Digital Object Identifier 10.1109/TIM.2025.3608319

challenging and complex visual tasks, including medical diagnosis [1], [2], industrial defect detection [3], and autonomous
driving [4], necessitate anomaly detection. In practical applications, abnormal samples are extremely scarce, while the
abnormal categories are often unpredictable. To this end,
many researchers from both industry and academia [5], [6],
[7] conduct anomaly segmentation in an unsupervised setting, where only normal samples are available for training.
The mainstream approaches to tackle this problem encompass embedding-based methods [8], [9] [10], knowledge
distillation-based methods [11], [12] [13], and reconstructionbased methods [14], [15] [16], [17].
The proposed approach in this study falls under the category
of reconstruction-based methods, which dominate unsupervised anomaly segmentation. Reconstruction-based methods
implicitly learn the latent distribution of normal data, using
autoencoders [17], [18], generative adversarial networks [14],
[19], and denoising diffusion probabilistic models [20], [21],
through the minimization of reconstruction loss during training. At inference time, these methods assume that the latent
manifold learned exclusively from normal samples cannot
effectively reconstruct abnormal regions. Therefore, the reconstruction residual, calculated as pixelwise differences between
the reconstructed result and the original input, serves to
represent the pixel anomaly scores.
A promising subbranch of reconstruction-based methods
involves reconstructing multistage features [7], [23], [24]
extracted from normal images using a pretrained network.
Previous reconstruction-based methods primarily operate in
image space, where slight reconstructive perturbations of pixels produce reconstruction errors comparable to those induced
by real anomalies, failing to meet the basic assumption. As
shown in the first row and third column of Fig. 1, for
the image reconstruction method DRAEM [6], the failure
to accurately reconstruct the texture details of the carpet
produces numerous false positives (red circles) near actual
cutting anomalies. In contrast, pretrained features are inherently more informative and discriminative, which increases
the representational distance between normal and abnormal
regions, thereby mitigating the aforementioned interference.
As illustrated in the first row and fourth column of Fig. 1,
feature reconstruction method DFR [7] produces almost no
false positives near the anomaly in the carpet.
However, feature reconstruction-based methods still face
two primary challenges in practical applications. One is
common in reconstruction schemes, where the reconstructive

1557-9662 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

5044613

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 1. Qualitative results of image reconstruction-based method DRAEM
[6], feature reconstruction-based method DFR [7] and the proposed FC2 P on
the MVTec AD [22] dataset for anomaly segmentation. The categories are
carpet, transistor, and cable (top to bottom). The interior regions of green
boundaries in the second column denote abnormal areas from actual binary
segmentation masks. Compared with previous methods, our proposed method
not only significantly enhances the saliency of anomaly segmentation but also
effectively suppresses false alarms in normal backgrounds.

network sometimes overgeneralizes, resulting in anomalies in
features also being well reconstructed. This occurs because
the reconstruction network’s output is identical to the input
during training, leading to shortcuts where the network merely
replicates the original input. The second row of Fig. 1 illustrates the issue of false negatives caused by overgeneralizing,
as previous reconstruction-based methods, both in image and
feature space, reconstruct the background instead of the missing transistor. Another challenge is that anomalies can be
overwhelmed in multistage features, thus preventing effective
segmentation and leading to missed detections. Each feature
stage contains information at different scales and semantic
levels, leading to varying emphasis on different anomalies.
Intuitively, summing the feature reconstruction residuals over
channels to represent the anomaly score for each spatial
location is inadequate. In DFR [7], four stages of features
suffice for detecting pixel-level anomalies in the texture-based
tile, but as deeper features are introduced, the performance
deteriorates. In addition, this issue also manifests in situations
where anomalies are suppressed by other anomalies. As shown
in the third row and fourth column of Fig. 1, the missing
anomaly of the cable is severely suppressed by the color
change anomaly (red circle) in DFR [7]. This is because the
latter anomaly accounts for a low proportion in the feature
reconstruction residuals, which cannot be revealed in the
anomaly score map by traditional summation methods.
To address the aforementioned challenges, we propose feature cross-channel projection along with an anomaly exposure
network (AExNet), called FC2 P, a novel feature reconstruction framework for anomaly segmentation and detection. It
is observed that the feature map of each stage is derived
from the abstraction and nonlinear combination of all feature
maps from the previous stage. Therefore, the intuition behind
our method is that there is a potential mapping relationship
between the feature maps of the neighborhood channels,
governed by the structure of the pretrained network. This

Fig. 2. Different feature reconstruction frameworks. (a) Conventional identical
feature reconstruction, where the reconstructive target treats the input data and
the target as identical, allowing the autoencoder to take shortcuts and merely
replicate the input. (b) Our proposed FC2 P uses the similarity of neighborhood
channel feature maps, enabling the autoencoder to perform two nonidentical
proxy tasks: inpainting the pseudo-anomaly and predicting the neighborhood
channel feature maps, thereby mitigating the aforementioned issue.

motivates the use of deep autoencoders to learn this mapping, as an additional normal attribute to fully leverage the
structural characteristics of the pretrained network. Fig. 2(a)
and (b) illustrates the framework differences between conventional identical feature reconstruction and our proposed
FC2 P, respectively. Previous methods aggregate multichannel
feature maps into a unified representation, focusing on scale
differences [25], [26] or improving network architecture [27],
[28] [29] to enhance reconstruction quality. However, they
often suffer from shortcut issues due to the reconstruction
target being identical to the input. In contrast, our method uses
deep autoencoders to simultaneously perform two nonidentical
prediction tasks, effectively mitigating this problem. Specifically, normal images are superimposed with synthetic patterns
to simulate pseudo-anomalies, so the extracted features are
actually corroded according to certain rules. The features
are then split into two nonoverlapping feature subsets based
on neighborhood channels. Due to the intrinsic correlation
between neighborhood channel feature maps, autoencoders
can be employed for closed-loop prediction from one feature
subset to another to ensure the integrity of the features. In
addition, the autoencoder must not only predict neighborhood
channel relationships but also complete the pseudo-anomaly
inpainting task. Inpainting anomalies in features helps to
reduce the impact of noise and redundant information, while
also allowing anomalies to vary in scale and shape, thus
enhancing the robustness of reconstruction.
Furthermore, considering that anomalies can be overwhelmed in the multistage representation space of features, we
design an AExNet to adaptively estimate the anomaly score
map from neighborhood feature reconstruction residuals. The
network is trained under the popular self-supervised framework [6], [30], guided by pseudo-abnormal binary masks,
and has been shown to generalize well for detecting real
anomalies. Specifically, the key component is the Siamese
anomaly propagator (SAP), which leverages the similarity
between neighborhood subsets to obtain enhanced common
representations of anomalies and propagates them across

CHEN et al.: FC2 P: FEATURE CROSS-CHANNEL PROJECTION FOR UNSUPERVISED ANOMALY SEGMENTATION

5044613

stages. Notably, the feature reconstruction residuals are divided
into aggregated and multiscale morphologies, which are
decoded using the U-Net structure. This design, inspired
by the divide-and-conquer approach, not only balances the
representation of anomalies across the entire feature space but
also gradually enhances anomalies across hierarchical stages.
Extensive experiments conducted on various benchmark
datasets demonstrate the effectiveness of our approach.
Notably, the proposed method achieves the state-of-the-art
(SOTA) anomaly segmentation performance with an average
precision (AP) metric of 79.8% on the widely used MVTec
AD [22] dataset and 44.8% on the challenging Visa [31]
dataset. We also conduct comprehensive ablation studies and
visualizations to validate the effectiveness of our proposed
components. The main contributions of our proposed method
are summarized as follows.
1) We propose FC2 P, a new paradigm for feature reconstruction. The inherent relationship among the neighborhood feature maps enables the autoencoder to
accomplish two nonidentical prediction tasks, thereby
mitigating the issue of over generalization in the conventional reconstruction scheme.
2) We propose an AExNet to adaptively estimate an
anomaly score map based on the similarity between
neighborhood reconstruction residuals. Its design inherits the divide-and-conquer principle, which is conducive
to simultaneously perceiving anomalies in features both
globally and hierarchically.
3) Extensive experiments on several datasets demonstrate
the superiority of our proposed FC2 P over several SOTA
methods for both unsupervised anomaly segmentation
and detection tasks. The visualization results in realworld scenarios also demonstrate the practicality of our
method.

coverage compared with GANs, AnoDDPM [21] proposes a
multiscale simplex noise diffusion process that controls the
target size of pseudo-noises to detect larger anomalies.
However, deep autoencoders tend to “generalize” so well
that they directly replicate abnormal areas in their reconstruction, resulting in misdetections of anomalies. To address
this issue, MemAE [15] introduces an updatable memory
module with an attention mechanism to enhance the latent
space, encouraging reconstruction to approach the normal
prototype in memory. MemSTC-Net [16] combines the advantages of [15] and [17], dynamically storing structure–texture
information in the memory bank. Nevertheless, MemSTCNet performs poorly in reconstructing details because the
memory module constrains the representation capacity of the
autoencoder. A viable solution is to reconstruct an image,
whose partial regions are randomly removed guided by masks,
in an inpainting manner as in [36]. To generate diverse masks,
SCDAN [37] introduces multiple scale and strip directions
in them to encourage the reconstructive network to learn
the semantic context from different locations, scales, and
directions. However, during inference, SCDAN requires iterating over all combinations of masks. To improve inference
efficiency, SSM [5] designs a progressive mask refinement
approach, which iteratively refines masks and focuses them
on the abnormal regions based on reconstruction errors.
Although image reconstruction-based methods are straightforward, the limited and uniform nature of normal samples
restricts the representations that autoencoders can learn, making them inadequate for handling complex anomalies. This
article introduces inpainting pseudo-anomalies within discriminative pretrained features, thereby compelling the autoencoder
to learn diverse normal representations.

II. R ELATED W ORKS

Deep feature extractors [38], [39] trained on largescale datasets [40] have become integral components in
anomaly segmentation methods. Generalized pretrained features, derived from diverse natural images [41], generate more
discriminative representations for normal images, thereby
increasing the discrepancies between normal and abnormal
data. Embedding-based methods [8], [9], [42] and knowledge distillation-based methods [11], [13], [43] are among
the pioneering approaches in applying pretrained features
in anomaly detection tasks. The embedding-based methods
aim to model the pretrained region descriptors in statistical
approaches, such as multivariate Gaussian distributions [9]
and normalizing flows [10], to explicitly quantify deviations
of anomalies within the distribution. Knowledge distillationbased methods [11], [13], [44] assume that the student network
cannot imitate the behavior of anomalies in the pretrained
teacher network. However, these methods are highly sensitive to the configuration of pretrained networks, including
the selection of stages, network structure, and distribution
design [41].
In contrast, feature reconstruction-based methods are more
effective at capturing the latent space distribution of normal
pretrained features and offer greater flexibility in structural

A. Image Reconstruction-Based Methods
Reconstruction-based methods assume that the reconstructive network trained on normal samples generates higher
reconstruction errors on abnormal regions. Therefore, anomaly
segmentation can be achieved through the discrepancy between
the test image and its reconstruction. AEs [15], [17] and GANs
[14], [19], [32], both of which follow the encoder–decoder
framework, are commonly employed reconstructive networks.
Moreover, leveraging the inherent prior information in the
image can enhance reconstruction performance. For example,
EdgeRec [33] reconstructs the original RGB image from its
grayscale edge, incorporating skip connections in the autoencoder to preserve high-frequency information. To improve
EdgeRec, ensuring consistency between the image and its
structure, P-Net [17] incorporates the encoded latent space
of the image into the structural latent space. Furthermore,
it has been demonstrated that using GANs and DDPMs can
improve generation results [34], [35]. For instance, GANomaly
[32], one of the first GANs used for anomaly detection, learns
representations in both image and latent vector space jointly
in an adversarial training process. To achieve superior mode

B. Feature Reconstruction-Based Methods

5044613

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 3. Overview of FC2 P. During the training phase, pseudo-abnormal images and their corresponding normal images are fed into the pretrained feature
extractor to obtain multistage aggregated features. Two autoencoders separately project subsets of features from the pseudo-abnormal feature, which are
divided by neighborhood channel split, onto normal feature subsets, thereby accomplishing proxy tasks for neighborhood prediction and inpainting. The
feature reconstruction residual subsets are then fed into the AExNet that is trained under the supervision of pseudo-abnormal masks. During the testing phase,
the data flow of test images is kept consistent with that of the pseudo-abnormal images.

design. DFR [7] first proposed using convolutional autoencoders to reconstruct multiscale pretrained features with a
single forward pass, achieving smooth segmentation results.
ADTR [23] introduces a transformer-based autoencoder to
address the identity mapping issue in convolutional networks.
UTRAD [24] integrates skip connections and pyramid structures in the transformer-based autoencoder to detect multiscale
structural and nonstructural anomalies.
However, because the reconstruction target is identical to
the original input data, autoencoders tend to uncontrollably
replicate input behavior. In contrast, our proposed approach
enables the reconstruction network to effectively circumvent
the identity mapping process by accomplishing two proxy
tasks: inpainting pseudo-anomalies in features and projecting
across feature channels, thereby enhancing its reconstructive
capabilities for structure and semantic information. The latter
primarily relies on the fact that the cross-channel feature
maps are combined by the unique structure of the pretrained
network, thus motivating us to exploit the potential correlation
between them.
C. Self-Supervised Learning Approaches
Recent self-supervised learning methods have yielded
promising results in anomaly segmentation by introducing
pseudo-abnormal samples to learn the boundaries between
abnormal and normal pixels. CutPaste [45] generates pseudoanomalies by cutting and pasting parts of normal images
and then employs a one-class classifier to distinguish them.
However, for anomaly segmentation, the use of Grad-CAM
[46] in CutPaste can only roughly locate anomalies. Subsequently, DRAEM [6] proposes leveraging a discriminative
network with U-Net [47] to learn pixel differences between the

pseudo-abnormal image and its inpainted in a self-supervised
manner. This not only reduces overfitting to pseudo-anomalies
but also enhances the ability to segment abnormal regions
with finer granularity. To reduce dependency on external data
during the synthesis of pseudo-anomalies in [6], DSR [48]
samples discrete latent space features to generate pseudoanomalies, improving the detection of anomalies near the
distribution. Furthermore, DiffAD [49] employs latent diffusion models [50] to improve image reconstruction performance
and proposes interpolated channels to increase reconstruction
diversity. The discriminative network can also be integrated
with other methods, extending beyond image reconstruction, to
segment discrepancies. For instance, MemSeg [30] introduces
a memory module that stores multistage normal features to
guide the decoding process of the discriminative network
through an attention mechanism. DeSTSeg [12] proposes
a segmentation network that perceives feature differences
between the denoising student network and the fixed teacher
network. The denoising student network is trained on pseudoabnormal samples to generate feature representations similar
to those of the teacher network. To further improve the student
network’s feature representation of abnormal regions, DAF
[51] introduces auxiliary loss heads to supervise each stage
of the student network.
However, these works focus on processing overall differences and do not fully consider the propagation of anomalies
across different feature stages. Although DAF uses auxiliary
losses to supervise the stages of the student network, it
still simply aggregates their results, making the anomaly
score map coarse. In contrast, our proposed method adopts
the idea of divide and conquer, not only considering the
overall performance of anomalies in aggregated features,

CHEN et al.: FC2 P: FEATURE CROSS-CHANNEL PROJECTION FOR UNSUPERVISED ANOMALY SEGMENTATION

but also allowing anomalies to progressively enhance across
stages.
III. M ETHODS
This section elaborates on the principle of our proposed
FC2 P, whose training framework is illustrated in Fig. 3.
The model consists of three cascaded components: paired
feature extraction, FC2 P, and an AExNet. Specifically, during the training phase, pseudo-abnormal images and their
corresponding normal images are fed into a weights-shared
pretrained network to extract aggregated multistage discriminative features. Subsequently, the features are divided into
two subsets through neighborhood channel split, achieving
closed-loop prediction by cross-channel feature projection.
The novelty lies in projecting the pseudo-abnormal feature
subset onto the neighborhood normal feature subset, thus
avoiding the replication of original input behavior caused
by identical reconstruction. Finally, the AExNet accurately
segments anomalies, which could be overwhelmed in the
feature reconstruction residuals, for effectively producing the
precise anomaly score map.
A. Paired Feature Extraction
The training of our model requires pseudo-abnormal images
synthesized on normal samples as self-supervised signals. In
this work, the synthesis algorithm for pseudo-abnormal images
is consistent with [6], which involves utilizing a binarized
2-D perlin noise map as a mask to alpha blend external texture
data from [52] onto normal images. Formally, in the training
phase, given a normal image XN ∈ RH×W×C , where H, W, and
C denote the dimensions of image height, width, and channels,
its pseudo abnormal image XP is generated at the same time
using a binary pseudo-mask MP ∈ RH×W×1 and an external
texture image XE . The synthesis process can be expressed as
follows:
XP = XN

MP + α (XN

MP ) + (1 − α) (XE

MP )

(1)

where MP = 1 − MP , is the elementwise product, and α ∈
(0, 0.8] denotes the opacity factor, controlling the degree of
pseudo-anomalies to increase diversity.
To obtain more discriminative representations, a frozen
pretrained network [53] with four different stages is employed
to extract multistage features from images. Considering that
the features from the last stage are more abstract and highly
correlated with the training task, they are typically discarded
in fine-grained downstream tasks [54]. Let φi ∈ RHi ×Wi ×Ci
be the feature map extracted from stage i, where Hi , Wi ,
and Ci denote the height, width, and channels of the feature
map, and i = 1, 2, 3. Subsequently, these feature maps from
different stages are aggregated using a simple strategy, which
involves resizing them to the resolution of the largest feature
map (H1 , W1 ) and then concatenating them along the channel
dimension. Therefore, by aggregating the feature maps of
the first three stages (φ1 , φ2 , φ3 ) extracted from XN and XP ,
the normal feature ΦN ∈ RH1 ×W1 ×Csum and pseudo-abnormal
feature ΦP ∈ RH1 ×W1 ×Csum can be obtained in pairs, where
Csum = C1 +C2 +C3 . Intuitively, aggregating multistage feature

5044613

maps can integrate both low-level and high-level semantic
representations of both normal and abnormal images. Compared with DeSTSeg [12], where features are reconstructed
hierarchically, this strategy can facilitate the interaction of
information across different stages.
B. Feature Cross-Channel Projection
The proposed FC2 P is motivated by the observation of the
features extracted via the pretrained network. In pretrained
networks, it is evident that the feature map xij ∈ RHi ×Wi of
stage i with channel index j originate from the abstraction
and nonlinear combination, which is denoted as f j (·), of
the features φi−1 from the preceding stage i − 1. Then, the
feature map xij and its neighborhood feature map xij+1 can be
formulated as follows:
xij = f j (φi−1 ) ,

xij+1 = f j+1 (φi−1 )

(2)

where f is typically determined by the structure of the
pretrained network. Obviously, there exists an inherent correlation between the neighborhood feature maps. The correlation
F·7→· (·) can be presented as follows:





−1
xij+1
xij = F j+17→ j xij+1 = f j−1 f j+1
 

 
−1
xij+1 = F j7→ j+1 xij = f j+1
f j−1 xij .
(3)
This insight inspires us to leverage deep networks to realize
the mutual projection across channels. Furthermore, under
the introduction of pseudo-anomalies, this projection also
encompasses an inpainting function.
Specifically, for the feature Φ, feature maps of neighborhood
channels are divided into two subsets Ae ∈ RH1 ×W1 ×(Csum /2) and
Ao ∈ RH1 ×W1 ×(Csum /2) , referred to as neighborhood channel split.
The above process can be presented in detail as follows:
˚

Ae = cat Φk | k = 2 j
˚

Ao = cat Φk | k = 2 j − 1
(4)
where Φk ∈ RH1 ×W1 ×1 is the feature map of channel index
k in feature Φ and j = (1, 2, . . . , (Csum /2)). cat(·) denotes the
concatenation along the channel dimension. Therefore, following the neighborhood channel split of ΦN and ΦP , the normal
neighborhood feature subsets (AeN , AoN ) and pseudo-abnormal
neighborhood feature subsets (AeP , AoP ) can be obtained.
To explore the latent feature distribution of normal samples, the convolutional autoencoder is used to accomplish
two proxy tasks: inpainting pseudo-anomalies and predicting
the neighborhood feature map. Specifically, an encoder is
employed to compress features into a latent space, followed by
a decoder that maps this latent space back to the corresponding
normal neighborhood features. The projection process can be
formulated as follows:

ÂeN = D1 E1 AoP

ÂoN = D2 E2 AeP
(5)
where ÂeN , ÂoN ∈ RH1 ×W1 ×(Csum /2) are the projected features,
E1 , E2 and D1 , D2 denote the encoders and decoders used for
the projection process, respectively. Given that neighborhoods

5044613

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 4. SAP of AExNet for self-supervised learning. Not only the aggregated
feature reconstruction residuals are fused, but the representation of anomalies
in their multistage feature sets is encoded with shared weights and integrated
with the previous stage by other convolutional blocks.

are mutual and nonoverlapping, two autoencoders are required
to complete the closed-loop mapping, which can concurrently
maintains the integrity of the projected feature.
Finally, reconstruction-based anomaly segmentation methods typically employ pixelwise reconstruction errors to
describe the severity of anomalies. For the features, a simple approach is to directly use the elementwise L2 distance
between the original input and its reconstruction as follows:
S e (i, j, k) = kÂeN (i, j, k) − AeN (i, j, k) k2
S o (i, j, k) = kÂoN (i, j, k) − AoN (i, j, k) k2

(6)

H1 ×W1 ×(Csum /2)

where S , S ∈ R
are feature reconstruction
residuals, and i, j, and k denote the index of height, width, and
channel, respectively. As the distance increases, it indicates
that the region is more likely to be abnormal.
e

o

C. Anomaly Exposure Network
Anomalies at each spatial position can be manifested
through the collective element discrepancies across channels.
However, features typically vary in both resolution and number
of channels for stages, making the direct summation of errors
along the channel dimension suboptimal. To address this issue,
we propose an AExNet, as shown in Fig. 3, inspired by
the divide-and-conquer approach. Specifically, considering that
anomalies behave various in different stages, resulting in being
overwhelmed in aggregation, a SAP is further proposed to
allow discrepancies, enhancing through the stages as illustrated
in Fig. 4. The aggregated feature reconstruction residual is split
into three subsets according to their original stages, and their
resolutions are simultaneously restored. Hence, for S e and S o ,
their three-stage feature subsets {S 1e , S 2e , S 3e } and {S 1o , S 2o , S 3o }
can be obtained, where the subscript numbers denote the stage
they belong but their channel count is only half of the original.
Notably, the reacquisition of multiscale information is pivotal
for anomaly segmentation practices.
Since neighborhood features possess inherent correlations,
they typically exhibit high similarity in response to anomalies.

Therefore, this similarity can be utilized to calibrate and filter
out the noise information. For S e and S o with their feature
subsets, weights shared 3 × 3 convolutional blocks are utilized
to learn consistent feature representations of anomalies. Furthermore, to obtain unified feature reconstruction residuals,
the neighborhood features encoded with shared weights are
concatenated and integrated with the previous stage by other
convolutional blocks. These blocks can calibrate the unstable
offsets in neighborhood features and encode these features into
more compact features Fall , F1 , F2 , and F3 , where Fall denotes
the fused aggregated feature and others are fused features of
different stages.
Finally, the fused compact features from SAP are gradually
incorporated into the decoding process through skip connections according to their resolution. Interestingly, anomalies
propagate from lower to deeper stages in SAP, while the
decoding process supports the propagation of anomalies from
low to high resolution. This ensures that anomalies are exposed
in each feature stage. Furthermore, the aggregated Fall are
connected to the last decoder with F1 , following a squeezeand-excitation (SE) [55] head to adaptively weight the feature
maps for predicting the precise anomaly score mask Mpre .
D. Self-Supervised Loss Functions
For the FC2 P, the training objective is to minimize the
discrepancy between the normal neighborhood features AeN and
AoN and the reconstructed features ÂeN and ÂoN . Therefore, we
introduce the projection loss Lpro , which can be expressed as
follows:
Lpro =k ÂeN − AeN k22 + k ÂoN − AoN k22
(7)
where k · k22 is the mean square error, commonly used for
training autoencoders. It is worth noting that autoencoders
under the guidance of Lpro accomplish two proxy tasks: one
is to inpaint the pseudo-anomalies in features, and the other
is to predict the features of the neighborhood channels.
To supervise the pixel-level anomaly prediction of the
AExNet, we introduce segmentation loss Lseg under the guidance of pseudo-abnormal mask, which can be represented as
follows:


Lseg = LDice Mpre , MP + LCE Mpre , MP
(8)
where LDice (·) denotes the dice loss [56] and LCE (·) denotes
the pixelwise binary cross-entropy loss. Since our proposed
method follows an end-to-end training mode, the overall loss
can be expressed as follows:
Ltotal = λLpro + (1 − λ) Lseg

(9)

where λ ∈ (0, 1) is the loss weight.
IV. E XPERIMENTS
In this section, our proposed method is validated on the
MVTec AD [22] and Visa [31] datasets and compared with
SOTA methods for image-level anomaly detection and pixellevel anomaly segmentation. To evaluate the effectiveness,
ablation studies are conducted in terms of the network architecture and loss function. Furthermore, to demonstrate the

CHEN et al.: FC2 P: FEATURE CROSS-CHANNEL PROJECTION FOR UNSUPERVISED ANOMALY SEGMENTATION

5044613

TABLE I
P IXEL -L EVEL A NOMALY S EGMENTATION R ESULTS W ITH AUC/AP (%) M ETRICS ON MVT EC AD DATASET. S UPERSCRIPT † : R EPRODUCED
R ESULTS F ROM AVAILABLE O FFICIAL I MPLEMENTATIONS . T HE O PTIMAL AND S UBOPTIMAL R ESULTS A RE S HOWN IN B OLD
AND U NDERLINE , R ESPECTIVELY. S UBSEQUENT TABLES F OLLOW THE C ONSISTENT P RESENTATIONS

practicality, visualization results are shown on the KSDD2 [57]
and Magnetic Tile [58] datasets that are obtained from realworld scenarios. Finally, the efficacy of the proposed AExNet
is demonstrated through the visualization of abnormal features
at different stages.

A. Experimental Setups
1) Datasets: The proposed method is validated on two
popular and challenging anomaly detection datasets. Furthermore, to demonstrate its effectiveness and practicality, we
perform visual validation on two datasets derived from realworld industrial scenarios. All four datasets provide precise
pixel-level ground truth for validating anomaly segmentation
performance.
1) MVTec AD [22] comprises 5354 images distributed
over ten categories of objects and five categories of
textures. Each category consists of approximately 200
normal images for training and 100 defective images
for testing. The resolution of original images ranges
between 700 × 700 and 1024 × 1024 pixels.
2) Visa [31] contains 10 821 images, including 9621 normal
samples and 1200 abnormal samples, which are divided
into 12 distinct subsets. Four of the subsets belong to
the PCB category, and their structures are relatively
complex. In some categories, such as capsules, multiple
objects together constitute the target to be detected.
Hence, this dataset is more challenging for anomaly
detection and segmentation.
3) Magnetic Tile [58] originates from a real industrial
scene, the largest magnetic tile production base in Zhejiang, China. It contains 1344 images, including 952
normal samples. The defect samples are divided into five
subcategories, including blowhole, break, crack, fray,
and uneven, which are defects on the magnetic tiles.
The images exhibit large resolution differences and have
different aspect ratios. In addition, the brightness of the
images, the shape of the defects, and the texture of the
tiles are also inconsistent.

4) KSDD2 [57] is a surface defect detection dataset with
over 3000 images, obtained while tackling a real-world
industrial problem. The image resolution is approximately 230 × 630 pixels. It contains 2979 normal
images and 356 defective images with several different
types of defects (scratches, minor spots, and surface
imperfections)
2) Evaluation Protocols: As in previous studies [6], [7],
[59], the area under the receiver operating characteristic
curve (AUC), the AP, and area under the per region overlap
(AUPRO) metrics are considered for evaluating the pixel-level
anomaly segmentation task. In addition, the AUC metric is
also employed to detect image-level anomalies. Both evaluation protocols distinguish normal from abnormal instances by
thresholding anomaly scores, with the AP focusing more on
the accuracy of segmentation within abnormal regions.
3) Implementation Details: The resolution of images and
masks is resized to 256 × 256 for both the training and
testing phase. The Swin Transformer [53] pretrained using
the ImageNet dataset serves as the feature extractor. The loss
weight λ is set to 0.5 by default. Adam optimizer is applied
with a learning rate of 1e−4 . The image-level anomaly scores
are obtained following the approach in [6]. Our models are
trained in an end-to-end mode for 400 and 200 epochs on
MVTec AD and Visa, respectively, using a batch size of 8 on
a single NVIDIA GTX 3090Ti, following the default PyTorch
2.2.1 framework.
B. Comparisons With SOTA Methods
This section presents quantitative results of the proposed
method on the MVTec AD and Visa dataset in detail, verifying
the superiority of our method over SOTA methods.
1) Results on MVTec AD Dataset: Table I shows the
pixel-level AUC and AP results for anomaly segmentation
on the MVTec dataset, while Table II showsthe pixel-level
AUPRO results. The baseline methods compared include
DFR [7], DRAEM [6], DSR [48], MemSeg [30], SimpleNet
[59], DAF [51], DiffAD [49], DeSTSeg [12], SSMCTP [60],
MambaAD [61], and GLAD [62]. The results show that the

5044613

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

TABLE II
C OMPARISON OF P IXEL -L EVEL A NOMALY S EGMENTATION W ITH AUPRO (%) ON MVT EC AD AND V ISA DATASETS

TABLE III
C OMPARISON OF I MAGE -L EVEL A NOMALY D ETECTION W ITH AUC (%) ON THE MVT EC AD DATASET. R ESULTS
A RE AVERAGED OVER A LL C ATEGORIES

TABLE IV
R ESULTS OF A NOMALY D ETECTION AND S EGMENTATION W ITH AUC AND
AP (%) M ETRICS ON THE V ISA DATASET, C OMPARING W ITH S EVERAL
SOTA M ETHODS . R ESULTS A RE AVERAGED OVER
A LL C ATEGORIES

Fig. 5. Comparison of inference speed (FPS) versus pixel AP for different
methods on MVTec AD benchmark.

proposed method outperforms all current SOTA methods for
the anomaly segmentation task and achieves a new SOTA on
the MVTec AD dataset, obtaining 98.7% AUC and 79.8% AP.
Focusing on AP protocols that better evaluate segmentation
performance, our method improves the score by a significant
4.1↑ compared with the current SOTA knowledge distillationbased method DeSTSeg with two-stage training mode and
by 13.0↑ compared with the SOTA image reconstructionbased method GLAD using a high computational cost latent
diffusion model. It is noteworthy that the proposed method
achieves optimal results in nine categories for AUC and eight
categories for AP, which is comparable to the SOTA method
in other categories, as well as yielding the best AURPO
result. Furthermore, Table III shows the image-level AUC
results of our method for anomaly detection on this dataset.
In addition, the frames per second (FPS) for inference speed
versus pixel AP is shown in Fig. 5. Our method strikes
a tradeoff between speed and performance, highlighting its
adaptability for practical applications. The results demonstrate
that the proposed method achieves comparable performance to
current SOTA methods. In summary, the evaluation of anomaly
segmentation and anomaly detection validates the effectiveness
and robustness of our proposed method.
2) Results on Visa Dataset: Table IV reports the AUC
and AP average results over all categories for image-level
anomaly detection (Det.) and pixel-level segmentation (Seg.),

and Table II shows the pixel-level AUPRO results on the Visa
dataset. The baseline methods compared include DFR [7],
PatchCore [8], DRAEM [6], SimpleNet [59], DAF [51], D3AD
[63], DeSTSeg [12], and MambaAD [61]. For the anomaly
detection task, our proposed method achieves performance
comparable to SOTA methods. Considering the anomaly segmentation results, our method is on par with the SOTA method
SimpleNet under the AUC. However, for the AP, our method
shows clear advantages, improving upon SimpleNet by 8.8↑.
SimpleNet adds Gaussian noise to the features to simulate
anomalies and uses a simple binary classifier for detection. In
contrast, our method generates more precise pseudo-anomalies
in the feature and utilizes the proposed AExNet to mine
anomaly representations in the multistage features, resulting
in more accurate anomaly score maps. For AUPRO, our
method outperforms the current SOTA methods DeSTSeg
and MambaAD by 2.9% and 2.5%, respectively. Notably,
the proposed method outperforms most previous methods
on the precise anomaly segmentation task. Previous SOTA
methods averaged around 36.0% AP, while our method reaches
44.8%, outperforming the SOTA method PatchCore by 8.1%↑.
These experimental results strongly demonstrate the excellent
performance of our method in anomaly segmentation and also
demonstrate its effectiveness and generalization capabilities.
3) Visualization Results: We present comprehensive qualitative results on the MVTec AD dataset to compare the
anomaly segmentation performance of our method with several

CHEN et al.: FC2 P: FEATURE CROSS-CHANNEL PROJECTION FOR UNSUPERVISED ANOMALY SEGMENTATION

5044613

Fig. 6. Qualitative visualized results for anomaly segmentation. The last row is the ground truth of the given input abnormal image. Compared with the
baseline methods, including DRAEM (second row), SimpleNet (third row), DAF (fourth row), and SOTA DeSTSeg (fifth row) on MVTec AD datasets, our
proposed approach FC2 P (sixth row) has a more accurate and compact anomaly location capability. Specifically, the superiority of our segmentation results
is manifested in the suppression of false positives within normal backgrounds and the accurate delineation of the contours of actual anomalies.

SOTA methods, as shown in Fig. 6. Our method outperforms SOTA methods, yielding more accurate and significant
anomaly segmentation results that closely align with the
ground truth. Specifically, our method excels in two key
aspects: 1) accurately delineating abnormal regions with welldefined boundaries and 2) reducing false positives in normal
regions. For example, our method accurately segments the
color anomalies in the cable’s circular periphery without
detecting the inner core. Notably, the anomaly segmentation
maps generated by our method for the carpet are more accurate
than the provided annotations, closely matching the actual
anomaly shapes.
Visualizations of the Visa dataset further demonstrate the
superiority of our method in anomaly segmentation. The
defects in the dataset are often small and challenging to detect,
as shown in Fig. 7. Furthermore, some categories exhibit
complex textures, such as the PCB. Despite these challenges,
our method achieves superior anomaly segmentation, with
more comprehensive and meaningful segmentation results and
fewer false positives in both object and background areas.
Fig. 8 shows visualizations of several cases from the real
magnetic tile defect and KSDD2 datasets. The predicted
anomaly score map closely matches the true label. Notably,
the true label in the second column does not mark the small
defect at the bottom (likely missed), whereas our proposed
method detects it. The results demonstrate the effectiveness
and practical implications of the proposed method.
C. Ablation Study
This section analyzes the contributions of the components
of the proposed method.
1) Influence of Different Components: Table V presents
the ablation studies on the MVTec AD dataset to assess the
effectiveness of each component of the proposed method. DFR
[7] is chosen as our baseline, and various capabilities are

Fig. 7. Qualitative results of anomaly segmentation on the challenging Visa
dataset, comparing with DRAEM and SOTA method DeSTSeg. The categories
from top to bottom are, respectively: candle, cashew, pcb1, pipe fryum, and
pcb4. The proposed method demonstrates significant segmentation capabilities
on objects with complex structures as well as on small defects, and it generates
fewer false positives in backgrounds.

gradually added, resulting in the following six experiments:
1) adding inpainting ability (inp.); 2) adding prediction ability
(pre.); 3) adding inpainting and prediction ability as complete
FC2 P; 4) adding SAP module without Fall ; 5) using vanilla
encoder in U-Net to segment Fall ; and 6) training with all
proposed components. The baseline method exhibits substantial improvement when the capabilities of two nonidentity
reconstructions are added (compared with 66.5 in Table I).
Furthermore, we perform a density analysis of the pixel
anomaly scores between the baseline and our proposed FC2 P,
as shown in Fig. 9. It can be observed that our proposed

5044613

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 8. Visualization results on the Magnetic Tile (left) and KSDD2 (right)
datasets.
TABLE V
A BLATION S TUDIES FOR A NOMALY D ETECTION AND S EGMENTATION
W ITH D IFFERENT C OMPONENTS OF O UR P ROPOSED A RCHITECTURE
ON MVT EC AD DATASET. R ESULTS A RE R EPRESENTED AS THE
AVERAGE AP S CORE OVER A LL C ATEGORIES

Fig. 10. Performance with varied loss weights on MVTec AD for anomaly
detection (AUC) and segmentation (AP). The red dashed line indicates the
mean value. Optimal performance is achieved when the reconstruction loss
and segmentation loss are balanced. Furthermore, adjusting the weights can
be employed to favor different tasks.

Fig. 11. Performance with segmentation loss components for anomaly
detection and segmentation in all metrics. The combination of both CE and
dice losses indeed compensates for their respective deficiencies. Not only
maintains the accuracy of anomaly pixel classification in unbalanced classes
but also enhances the model’s sensitivity to abnormal regions.

Fig. 9. Probability density of both normal and abnormal pixel anomaly
score for feature reconstruction residual with FC2 P, comparing with the base
method.

method achieves a more compact distribution with less overlap
for both abnormal and normal pixels, making it easier to
distinguish them. These results show that traditional feature
reconstruction-based methods suffer from overgeneralization.
When the AExNet is added, anomaly segmentation performance improves significantly by at least 9% AP. Moreover, our
approach improves by +10.3%↑ when using Fall with vanilla
encoder, indicating that it actually contains rich abnormal
information. When the SAP module is added with Fall , our
proposed method achieves the optimal result. Based on the
divide-and-conquer approach, the gradual enhancement of
anomalies at different stages, combined with the integration of
overall feature reconstruction residuals, significantly improves
anomaly segmentation performance.
2) Influence of Loss Function: Fig. 10 illustrates the effect
of loss weights on the performance of anomaly detection and
segmentation on the MVTec AD dataset. The loss weight

λ controls the balance between reconstruction loss and segmentation loss during end-to-end training, thereby affecting
the resulting anomaly score maps. As the reconstruction loss
weight gradually increases to 0.4, the performance of imagelevel anomaly detection improves from 97.1% to 99.1%.
Beyond this threshold, the feature reconstruction module
FC2 P tends to overfit, resulting in a plateau in anomaly
detection performance. However, as the proportion of segmentation loss decreases, there is a noticeable decline in the
AP metric for anomaly segmentation. This suggests that the
AExNet, designed to mine anomalies from feature residuals,
is inadequately trained. Although the feature reconstruction
component is well-trained, the segmentation network fails
to extract anomalies from the features to produce accurate segmentation results. The results indicate that optimal
performance is achieved when the reconstruction loss and
segmentation loss are properly balanced. In addition, it is
observed that reconstruction loss is more conducive to imagelevel anomaly detection, making it beneficial for adapting to
various task types.
Furthermore, ablation analysis is conducted on the components of the segmentation loss, as shown in Fig. 11. Since the
CE loss focuses on independent pixel predictions, it performs
poorly when used alone in class-imbalanced segmentation
tasks, particularly in anomaly segmentation where normal
pixels vastly outnumber abnormal pixels. In contrast, the dice

CHEN et al.: FC2 P: FEATURE CROSS-CHANNEL PROJECTION FOR UNSUPERVISED ANOMALY SEGMENTATION

5044613

TABLE VI
A BLATION S TUDIES FOR A NOMALY D ETECTION AND S EGMENTATION
W ITH D IFFERENT BACKBONES ON MVT EC AD AND V ISA DATASETS

TABLE VII
A BLATION S TUDIES FOR A NOMALY D ETECTION AND S EGMENTATION
W ITH D IFFERENT C OMBINATIONS ON MVT EC AD DATASET
Fig. 12. Some examples of visualization of different feature residual stages
on MVTec AD dataset. The sixth column represents the results of aggregating
the three stages. The proposed method can exploit the advantages of all stages
and produce precise anomaly score maps, eliminating false positives in normal
areas.

loss focuses on the overall structural similarity of the abnormal
regions, which alleviates the class-imbalance issue to some
extent; however, the lack of confidence in pixel classification
results in an AP of only 79.8%. Interestingly, combining
these two types of losses compensates for their respective
limitations, not only maintaining the accuracy of abnormal
pixel classification but also increasing the model’s sensitivity
to abnormal regions, thereby significantly improving anomaly
segmentation performance.
3) Influence of Pretrained Network: Table VI illustrates
the impact of different pretrained backbones, including CNNbased (ResNet [38], WRN [64], and DenseNet [65]) and
Transformer-based (PVT [66], HorNet [67], and Swin [53])
models with their versions, on the performance of anomaly
detection and segmentation. The results on the MVTec AD
and Visa datasets demonstrate the significant advantage of
backbones following the Swin Transformer framework in both
anomaly detection and segmentation tasks. First, the Swin
Transformer not only captures long-range dependencies, a
characteristic absent in CNNs, but its hierarchical structure
also facilitates the processing of multiscale information. This is
essential for understanding both the macrostructure of normal
images and their fine-grained details. In addition, the windowbased self-attention mechanism enhances the model’s ability
to bridge local and global contexts, facilitating the accurate
identification and localization of abnormal regions.
4) Influence of Feature Stages: Table VII illustrates the
impact of combining different feature stages on anomaly
detection and segmentation performance in the MVTec AD
dataset. The results demonstrate that optimal performance
can be achieved by combining features from all three stages.
Notably, the combination of stages 1 and 2 is more beneficial
for segmentation, while the combination of stages 2 and 3 is
more beneficial for detection. The features from the second

stage play a key role, achieving relatively good results with
just this stage. This is because shallower features tend to
focus on detailed information in abnormal regions, while
deeper features are more concerned with semantic aspects.
Interestingly, the SOTA methods SimpleNet and Patchcore
both utilize stages 2 and 3 to achieve optimal performance.
However, the anomaly score map is often inaccurate due to
the absence of shallow information. It can be observed that
our proposed method fully exploits the characteristics of all
feature stages, achieving optimal results in both detection and
segmentation. This is primarily due to the fact that the AExNet
not only considers anomalies as a whole but also enables
anomalies to gradually enhance across the stages of feature
reconstruction residuals.
Furthermore, to validate that our method addresses the issue
of anomalies being overshadowed at different feature stages,
we visualize the feature reconstruction residuals and their
aggregation for anomaly segmentation in Fig. 12. We observe
that anomaly segmentation performance varies across different
stages and categories. For instance, the print anomaly on the
hazelnut is more prominent in stage 1, but aggregating all
levels can obscure this detail. Similarly, the two anomalies
on the pill are suppressed by false positives in stage 3,
rendering them insignificant in the aggregated results. Our
method alleviates this issue by reducing false alarms in normal
areas and producing clear outlines of abnormal areas. Notably,
even when the shallower stages (stages 1 and 2) fail to detect
the color anomaly on the carpet, our method can still extract
weak details to assist deeper stages in generating a precise
anomaly score map.
V. C ONCLUSION
This article proposes a novel feature reconstruction-based
framework named FC2 P to address the challenging and practical task of unsupervised anomaly segmentation. The proposed
method primarily alleviates the issues of overgeneralization

5044613

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

and overwhelming that are typically encountered in traditional
feature reconstruction-based approaches. Specifically, features
are split into two subsets based on neighboring channels, and
two autoencoders are employed for their closed-loop prediction, driven by our observation of the potential relationship
between neighboring channel feature maps in the pretrained
features. In addition, for the feature reconstruction residual
subsets, an AExNet is proposed, adopting the divide-andconquer principle, so that anomalies are gradually enhanced
across feature stages and combined with the aggregated feature
residuals to decode a precise anomaly score map. The proposed method outperforms SOTA methods on two widely used
benchmark datasets in both anomaly detection and anomaly
segmentation. Finally, the superiority and practicality of the
proposed method in anomaly segmentation are thoroughly
demonstrated through visual qualitative analysis.
Limitations: Although the proposed method achieves strong
performance, it sacrifices some inference efficiency. This is
primarily caused by the aggregation of multistage pretrained
features, which increases the number of channels and leads to
significant computational overhead during the reconstruction
process of the autoencoders.
Future Work: In future work, we plan to integrate knowledge
from large vision-language models [68] or vision foundational models [69] into our approach. This integration aims
to enhance the generalization capability of our method for
anomaly detection and segmentation tasks.
R EFERENCES
[1]

T. Fernando, H. Gammulle, S. Denman, S. Sridharan, and C. Fookes,
“Deep learning for medical anomaly detection—A survey,” 2020,
arXiv:2012.02364.
[2] A. Frotscher, J. Kapoor, T. Wolfers, and C. F. Baumgartner, “Unsupervised anomaly detection using aggregated normative
diffusion,” 2023, arXiv:2312.01904.
[3] X. Tao, X. Gong, X. Zhang, S. Yan, and C. Adak, “Deep learning for
unsupervised anomaly localization in industrial images: A survey,” IEEE
Trans. Instrum. Meas., vol. 71, pp. 1–21, 2022.
[4] D. Bogdoll, M. Nitsche, and J. M. Zollner, “Anomaly detection in
autonomous driving: A survey,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. Workshops (CVPRW), Jun. 2022, pp. 4487–4498.
[5] C. Huang, Q. Xu, Y. Wang, Y. Wang, and Y. Zhang, “Self-supervised
masking for unsupervised anomaly detection and localization,” IEEE
Trans. Multimedia, vol. 25, pp. 4426–4438, 2023.
[6] V. Zavrtanik, M. Kristan, and D. Skocaj, “DRÆM—A discriminatively trained reconstruction embedding for surface anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021,
pp. 8310–8319.
[7] Y. Shi, J. Yang, and Z. Qi, “Unsupervised anomaly segmentation
via deep feature reconstruction,” Neurocomputing, vol. 424, pp. 9–22,
Feb. 2021.
[8] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler,
“Towards total recall in industrial anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022,
pp. 14298–14308.
[9] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “PaDiM: A patch distribution modeling framework for anomaly detection and localization,”
2020, arXiv:2011.08785.
[10] J. Lei, X. Hu, Y. Wang, and D. Liu, “PyramidFlow: High-resolution
defect contrastive localization using pyramid normalizing flow,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023,
pp. 14143–14152.
[11] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Uninformed
students: Student–teacher anomaly detection with discriminative latent
embeddings,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2020, pp. 4182–4191.

[12] X. Zhang, S. Li, X. Li, P. Huang, J. Shan, and T. Chen, “DeSTSeg:
Segmentation guided denoising student-teacher for anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2023, pp. 3914–3923.
[13] M. Salehi, N. Sadjadi, S. Baselizadeh, M. H. Rohban, and H. R. Rabiee,
“Multiresolution knowledge distillation for anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021, pp.
14897–14907.
[14] T. Schlegl, P. Seeböck, S. M. Waldstein, G. Langs, and U. SchmidtErfurth, “F-AnoGAN: Fast unsupervised anomaly detection with
generative adversarial networks,” Med. Image Anal., vol. 54, pp. 30–44,
May 2019.
[15] D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1705–1714.
[16] K. Zhou et al., “Memorizing structure-texture correspondence for image
anomaly detection,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33,
no. 6, pp. 2335–2349, Jun. 2022.
[17] K. Zhou et al., “Encoding structure-texture relation with P-Net for
anomaly detection in retinal images,” in Proc. Eur. Conf. Comput. Vis.,
2020, pp. 360–377.
[18] K. Batzner, L. Heckler, and R. König, “EfficientAD: Accurate visual
anomaly detection at millisecond-level latencies,” in Proc. IEEE/CVF
Winter Conf. Appl. Comput. Vis. (WACV), Jan. 2024, pp. 128–138.
[19] S. Akcay, A. Atapour-Abarghouei, and T. P. Breckon, “Skip-GANomaly:
Skip connected and adversarially trained encoder–decoder anomaly
detection,” in Proc. Int. Joint Conf. Neural Netw., 2019, pp. 1–8.
[20] H. Zhang, Z. Wang, D. Zeng, Z. Wu, and Y.-G. Jiang, “DiffusionAD:
Norm-guided one-step denoising diffusion for anomaly detection,” 2023,
arXiv:2303.08730.
[21] J. Wyatt, A. Leach, S. M. Schmon, and C. G. Willcocks, “AnoDDPM:
Anomaly detection with denoising diffusion probabilistic models using
simplex noise,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
Workshops (CVPRW), Jun. 2022, pp. 649–655.
[22] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec AD—A
comprehensive real-world dataset for unsupervised anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2019, pp. 9584–9592.
[23] Z. You, K. Yang, W. Luo, L. Cui, Y. Zheng, and X. Le, “ADTR:
Anomaly detection transformer with feature reconstruction,” in Proc.
Neural Inf. Process., 2023, pp. 298–310.
[24] L. Chen, Z. You, N. Zhang, J. Xi, and X. Le, “UTRAD: Anomaly
detection and localization with U-transformer,” Neural Netw., vol. 147,
pp. 53–62, Mar. 2022.
[25] H. Zhi, H. Qin, L. Zhang, J. Guo, and B. Song, “CFFDist: Cross-scale
feature fusion distillation network for industrial anomaly localization,”
IEEE Trans. Instrum. Meas., vol. 74, pp. 1–11, 2025.
[26] W. Hu, W. Yu, Y. Tang, Y. Xie, and W. Zhang, “REDAD: A reliable
distillation for image anomaly detection,” IEEE Trans. Instrum. Meas.,
vol. 74, pp. 1–13, 2025.
[27] Y. Guo, M. Jiang, Q. Huang, Y. Cheng, and J. Gong, “MLDFR: A
multilevel features restoration method based on damaged images for
anomaly detection and localization,” IEEE Trans. Ind. Informat., vol. 20,
no. 2, pp. 2477–2486, Feb. 2024.
[28] B. Zhu, Z. Gu, G. Zhu, Y. Chen, M. Tang, and J. Wang, “ADFormer:
Generalizable few-shot anomaly detection with dual CNN-transformer
architecture,” IEEE Trans. Instrum. Meas., vol. 74, pp. 1–16, 2025.
[29] H. Yao, Y. Cao, W. Luo, W. Zhang, W. Yu, and W. Shen, “Prior normality
prompt transformer for multiclass industrial image anomaly detection,”
IEEE Trans. Ind. Informat., vol. 20, no. 10, pp. 11866–11876,
Oct. 2024.
[30] M. Yang, P. Wu, and H. Feng, “MemSeg: A semi-supervised method
for image surface defect detection using differences and commonalities,”
Eng. Appl. Artif. Intell., vol. 119, Mar. 2023, Art. no. 105835.
[31] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, “Spotthe-difference self-supervised pre-training for anomaly detection and
segmentation,” in Proc. Eur. Conf. Comput. Vis., 2022, pp. 392–408.
[32] S. Akcay, A. Atapour-Abarghouei, and T. P. Breckon, “GANomaly:
Semi-supervised anomaly detection via adversarial training,” in Proc.
14th Asian Conf. Comput. Vis., Dec. 2019, pp. 622–637.
[33] T. Liu, B. Li, Z. Zhao, X. Du, B. Jiang, and L. Geng, “Reconstruction
from edge image combined with color and gradient difference for
industrial surface anomaly detection,” 2022, arXiv:2210.14485.
[34] I. J. Goodfellow et al., “Generative adversarial nets,” in Proc. 27th Int.
Conf. Neural Inf. Process. Syst. (NIPS), 2014, pp. 2672–2680.

CHEN et al.: FC2 P: FEATURE CROSS-CHANNEL PROJECTION FOR UNSUPERVISED ANOMALY SEGMENTATION

[35] J. Ho, A. N. Jain, and P. Abbeel, “Denoising diffusion probabilistic
models,” in Proc. 34th Int. Conf. Neural Inf. Process. Syst., 2020,
pp. 1–7.
[36] V. Zavrtanik, M. Kristan, and D. Skočaj, “Reconstruction by inpainting
for visual anomaly detection,” Pattern Recognit., vol. 112, Apr. 2021,
Art. no. 107706.
[37] X. Yan, H. Zhang, X. Xu, X. Hu, and P.-A. Heng, “Learning semantic
context from normal samples for unsupervised anomaly detection,” in
Proc. AAAI Conf. Artif. Intell., vol. 35, May 2021, pp. 3110–3118.
[38] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.
[39] K. Simonyan and A. Zisserman, “Very deep convolutional networks for
large-scale image recognition,” 2014, arXiv:1409.1556.
[40] A. Krizhevsky, I. Sutskever, and G. E. Hinton, “ImageNet classification
with deep convolutional neural networks,” Commun. ACM, vol. 60,
no. 6, pp. 84–90, May 2017.
[41] L. Heckler, R. König, and P. Bergmann, “Exploring the importance of
pretrained feature extractors for unsupervised anomaly detection and
localization,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
Workshops (CVPRW), Jun. 2023, pp. 2917–2926.
[42] M. Rudolph, B. Wandt, and B. Rosenhahn, “Same same but DifferNet:
Semi-supervised defect detection with normalizing flows,” in Proc. IEEE
Winter Conf. Appl. Comput. Vis. (WACV), Jan. 2021, pp. 1906–1915.
[43] G. Wang, S. Han, E. Ding, and D. Huang, “Student-teacher feature
pyramid matching for anomaly detection,” 2021, arXiv:2103.04257.
[44] Z. Gu et al., “Remembering normality: Memory-guided knowledge
distillation for unsupervised anomaly detection,” in Proc. IEEE/CVF Int.
Conf. Comput. Vis. (ICCV), Oct. 2023, pp. 16355–16363.
[45] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Selfsupervised learning for anomaly detection and localization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 9659–9669.
[46] R. R. Selvaraju, M. Cogswell, A. Das, R. Vedantam, D. Parikh, and
D. Batra, “Grad-CAM: Visual explanations from deep networks via
gradient-based localization,” in Proc. IEEE Int. Conf. Comput. Vis.
(ICCV), Oct. 2017, pp. 618–626.
[47] O. Ronneberger, P. Fischer, and T. Brox, “U-Net: Convolutional networks for biomedical image segmentation,” in Proc. 18th Int. Conf.
Med. Image Comput. Comput.-Assist. Intervent., 2015, pp. 234–241.
[48] V. Zavrtanik, M. Kristan, and D. Skočaj, “DSR—A dual subspace reprojection network for surface anomaly detection,” in Proc. Eur. Conf.
Comput. Vis., 2022, pp. 539–554.
[49] X. Zhang, N. Li, J. Li, T. Dai, Y. Jiang, and S.-T. Xia, “Unsupervised
surface anomaly detection with diffusion probabilistic model,” in Proc.
IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2023, pp. 6759–6768.
[50] R. Rombach, A. Blattmann, D. Lorenz, P. Esser, and B. Ommer,
“High-resolution image synthesis with latent diffusion models,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2022,
pp. 10684–10695.
[51] Y. Cai, D. Liang, D. Luo, X. He, X. Yang, and X. Bai, “A discrepancy
aware framework for robust anomaly detection,” IEEE Trans. Ind.
Informat., vol. 20, no. 3, pp. 3986–3995, Mar. 2024.
[52] M. Cimpoi, S. Maji, I. Kokkinos, S. Mohamed, and A. Vedaldi,
“Describing textures in the wild,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit., Jun. 2014, pp. 3606–3613.
[53] Z. Liu et al., “Swin transformer: Hierarchical vision transformer using
shifted windows,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2021, pp. 9992–10002.
[54] T.-Y. Lin, P. Dollár, R. Girshick, K. He, B. Hariharan, and S. Belongie,
“Feature pyramid networks for object detection,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017, pp. 936–944.
[55] J. Hu, L. Shen, and G. Sun, “Squeeze-and-excitation networks,” in Proc.
IEEE Conf. Comput. Vis. Pattern Recognit., Jul. 2018, pp. 7132–7141.
[56] F. Milletari, N. Navab, and S.-A. Ahmadi, “V-Net: Fully convolutional
neural networks for volumetric medical image segmentation,” in Proc.
4th Int. Conf. 3D Vis. (3DV), Oct. 2016, pp. 565–571.
[57] J. Božič, D. Tabernik, and D. Skočaj, “Mixed supervision for surfacedefect detection: From weakly to fully supervised learning,” Comput.
Ind., vol. 129, Aug. 2021, Art. no. 103459.
[58] Y. Huang, C. Qiu, Y. Guo, X. Wang, and K. Yuan, “Surface defect
saliency of magnetic tile,” in Proc. IEEE 14th Int. Conf. Autom. Sci.
Eng. (CASE), Aug. 2018, pp. 612–617.
[59] Z. Liu, Y. Zhou, Y. Xu, and Z. Wang, “SimpleNet: A simple network
for image anomaly detection and localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023, pp. 20402–20411.

5044613

[60] N.-C. Ristea et al., “Self-supervised predictive convolutional attentive
block for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2022, pp. 13566–13576.
[61] H. He et al., “MambaAD: Exploring state space models for multi-class
unsupervised anomaly detection,” 2024, arXiv:2404.06564.
[62] H. Yao, M. Liu, Z. Yin, Z. Yan, X. Hong, and W. Zuo, “GLAD: Towards
better reconstruction with global and local adaptive diffusion models
for unsupervised anomaly detection,” in Proc. Eur. Conf. Comput. Vis.,
2024, pp. 1–17.
[63] J. Tebbe and J. Tayyub, “D3AD: Dynamic denoising diffusion probabilistic model for anomaly detection,” 2024, arXiv:2401.04463.
[64] S. Zagoruyko and N. Komodakis, “Wide residual networks,” 2016,
arXiv:1605.07146.
[65] G. Huang, Z. Liu, L. Van Der Maaten, and K. Q. Weinberger, “Densely
connected convolutional networks,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jul. 2017, pp. 2261–2269.
[66] W. Wang et al., “Pyramid vision transformer: A versatile backbone for
dense prediction without convolutions,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis. (ICCV), Oct. 2021, pp. 548–558.
[67] Y. Rao, W. Zhao, Y. Tang, J. Zhou, S.-N. Lim, and J. Lu, “HorNet: Efficient high-order spatial interactions with recursive gated convolutions,”
in Proc. Adv. Neural Inf. Process. Syst., 2022, pp. 10353–10366.
[68] A. Radford et al., “Learning transferable visual models from natural language supervision,” in Proc. Int. Conf. Mach. Learn., 2021,
pp. 8748–8763.
[69] A. M. Kirillov et al., “Segment anything,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis., Sep. 2023, pp. 4015–4026.

Yichi Chen received the Ph.D. degree in computer software and theory from
the University of Chinese Academy of Sciences, Beijing, China, in 2025.
His research interests include image anomaly detection and continual
learning.

Weizhi Xian received the Ph.D. degree in computer science and technology
from the College of Computer Science, Chongqing University, Chongqing,
China, in 2023.
He is currently a Post-Doctoral Researcher with Chongqing Research
Institute and the Faculty of Computing, Harbin Institute of Technology,
Chongqing. His research interests include pattern recognition, anomaly
detection, visual quality assessment, and video coding.

Junjie Wang (Graduate Student Member, IEEE) is currently pursuing the
Ph.D. degree with Harbin Institute of Technology, Shenzhen, China, under
the supervision of Prof. Zhuotao Tian and Prof. Bin Chen.
His research interests include computer vision, multimodal perception, and
topics related to multimodal large language models.

Xian Tao (Senior Member, IEEE) received the Ph.D. degree in control
theory and control engineering from the Institute of Automation (IA), Chinese
Academy of Sciences (CAS), Beijing, China, in 2016.
He is currently an Associate Professor with IA, CAS. His current research
interests include machine learning and automated surface inspection for
industries.

Bin Chen received the B.E. degree from Tsinghua University, Beijing, China,
in 1992, the M.S. degree from Sichuan University, Chengdu, China, in 2001,
and the Ph.D. degree from Chinese Academy of Sciences, Beijing, in 2005.
He has been a Research Professor with the International Research Institute
for Artificial Intelligence, Harbin Institute of Technology, Shenzhen, China,
since 2020. He has also been a Professor with the University of Chinese
Academy of Sciences, Beijing, since 2006. His research interests include
machine vision, deep learning, and artificial intelligence.
PAPER_TEXT
