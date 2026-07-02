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
# [428] FeatDAE: Introducing Features With Denoising Autoencoder for Anomaly Detection
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
编号：428
题名：FeatDAE: Introducing Features With Denoising Autoencoder for Anomaly Detection
年份：2025
DOI：10.1109/tim.2025.3565336
来源：IEEE Transactions on Instrumentation and Measurement
PDF：paper/10.1109_TIM.2025.3565336.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\428.txt
- 原始字符数：68444
- 本次发送字符数：68444
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

2529914

FeatDAE: Introducing Features With Denoising
Autoencoder for Anomaly Detection
Zheyuan Zhou , Student Member, IEEE, Jichun Wang , Zian Yu , Zili Wang , Member, IEEE,
Xiaojian Liu , Lemiao Qiu , Member, IEEE, and Shuyou Zhang

Abstract— Anomaly detection (AD) is a critical task in
manufacturing inspection. Reconstructive AD methods restore
the normal appearance of an object, ideally modifying only
the anomalous regions. However, previously commonly used
reconstruction-based architecture always struggles with overgeneralization and overfitting problems, leading to poor reconstruction performance on real defective samples. In this study,
we propose a more general denoising autoencoder, by introducing
a feature hierarchy design to address these challenges in unsupervised AD. In particular, we operate feature transformation in
the latent space to cope with the robustness of unseen anomalies
in reality. Furthermore, the method enhances the discriminative
capability of the model by focusing on multiple knowledge,
including pixel color, histogram of oriented gradient (HOG)
feature, and deep features. Additionally, a feature alignment
module is proposed to manage the varied sizes and morphologies
of features. Experiments conducted on both the MVTec AD
dataset and the VisA dataset demonstrate that our FeatDAE
significantly outperforms existing methods, achieving state-of-theart results with high efficiency.
Index Terms— Anomaly detection (AD), denoising autoencoder,
industrial defect detection, self-supervised learning, unsupervised
learning.

I. I NTRODUCTION
NOMALY detection (AD) aims to identify instances that
contain anomalous and localized regions that deviate
from normal object patterns, playing an essential role in
various applications such as industrial quality control [1], [2],
[3]. However, the scarcity and diversity of anomalies pose
significant challenges in collecting and labeling, resulting in
the inability to construct large datasets to train a classifier or
detector. In addition, the pattern differences between normal
and abnormal images are usually fine-grained, while defects
may occupy only a small fraction of image pixels. Therefore,
AD based on only normal data encounters unique challenges
different from those of a typical supervised learning problem.
Many recently popular and successful unsupervised AD
models are reconstruction-based [4], [5]. These models learn to

A

Received 4 January 2025; revised 17 March 2025; accepted 3 April 2025.
Date of publication 29 April 2025; date of current version 2 June 2025. This
work was supported in part by the National Natural Science Foundation of
China under Grant 52375271 and in part by the “Pioneer” and “Leading
Goose” Research and Development Program of Zhejiang Province under
Grant 2024C01044. The Associate Editor coordinating the review process was
Dr. Xianqiang Yang. (Corresponding author: Xiaojian Liu.)
The authors are with the State Key Laboratory of Fluid Power and
Mechatronic Systems, Zhejiang University, Hangzhou 310058, China (e-mail:
liuxj@zju.edu.cn).
Digital Object Identifier 10.1109/TIM.2025.3565336

construct a latent space of normal samples by minimizing the
discrepancy between the original normal instances and their
reconstructions. It can be further subdivided into the following
two paradigms. Generative methods [6], [7], [8] assume that
an autoencoder will be optimized to reproduce normal patterns,
thereby failing to accurately reconstruct anomalous regions.
As a result, the poor reconstruction of defective areas leads to
significant differences between the reconstructed output and
the input images. This discrepancy can be used to identify and
localize the anomalous regions. However, the high generalization capacity of autoencoders allows them to even reconstruct
anomaly fidelity, especially when similar local features are
presented [9], as illustrated in Fig. 1(a). This overgeneralization violates the basic assumption of generating anomaly
maps based solely on the reconstruction error, significantly
increasing the rate of false negatives (FNs). Discriminative
methods [1], [10], [11] train models by synthesizing anomalies to extend these models to recognize real defects. They
simultaneously generate masks indicating the locations of
anomalies and enhance the network’s ability to discriminate
and localize defects by incorporating a segmentation head.
However, it often suffers from overfitting problems, where the
synthetic samples may be far from the real defects. A simple
classification network can achieve nearly 100% accuracy in
distinguishing between synthesized anomaly samples and real
anomaly samples after only a few training epochs. Training
with such a set results in an unclear discriminator that generalizes poorly to real anomalies, where indistinct objects could
be included in inlier feature space, causing large false-positive
(FP) detections, as shown in Fig. 1(b). The discriminative
model shows improvement but still struggles to accurately
reconstruct anomalous not covered by the simulation.
To simultaneously address the above-mentioned problems,
we propose a new feature-level denoising autoencoder explicitly for surface AD, dubbed as FeatDAE, as illustrated in
Fig. 2. Our FeatDAE introduces feature radial transformation
(FRT) and feature omnidirectional injection (FOI) in the
latent space after the encoder and incorporates a meticulously
symmetrical decoder to seamlessly restore the latent noised
representation back to the reconstruction result. By concurrently introducing distinct perturbations at both the image
and feature levels, our FeatDAE is proficient in discerning the intrinsic information and distribution of the data,
showcasing enhanced robustness when addressing a myriad
of real-world anomalies. Second, the objects we reconstruct

1557-9662 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

2529914

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

state-of-the-art methods by a significant margin while
maintaining a high inference speed of 110 FPS.
II. R ELATED W ORKS

Fig. 1. Pilot study on reconstruction-based methods. (a) Generative model
takes the original image X or the noise-added image X ′ as input, and is
trained using the reconstruction loss L rec to reconstruct its input. The anomaly
map M is obtained by comparing the input X with the reconstruction
b. (b) Discriminative model combines the synthesized image X ′
result X
b, and is supervised by the corresponding
with the reconstruction result X
synthesized mask M′ and the segmentation loss L seg to produce a more
accurate localization of defects. As shown, the minor discrepancy between
b renders it difficult to accurately
the input X and the reconstructed result X
discern and differentiate anomalies. This highlights the challenge inherent
in reconstruction-based methods, which stems from their limited capacity to
distinctly characterize real anomaly samples.

encompass information of various granularity and types, such
as pixel color, hand-crafted descriptors, and deep features.
The diversity in the reconstructed targets further contributes
to a comprehensive and precise depiction of features, thereby
enhancing the downstream AD performance. In addition,
we have devised a feature alignment module to address the
varied sizes and morphologies of the reconstructed features.
The aligned features are then fed into the head to handle
discrepancies in a trainable manner, alleviating the overfitting
of synthetic defects.
The main contributions of our paper are summarized as
follows.
1) We introduce stochastic perturbations in both the input
and latent space, extending and generalizing the concept
of the denoising autoencoder. This approach directly
addresses the issue of overfitting to simulated defects,
a common problem in recent discriminative methods.
2) We propose a multifeature reconstruction mechanism
that enables the autoencoder to learn from different types
of features. The aligned features demonstrably mitigate
the issue of overgeneralization and reduce the high FN
rate.
3) We introduce a novel framework, FeatDAE, specifically
designed for surface AD. FeatDAE is capable of handling a wide variety of anomalies effectively, making it
versatile and adaptable to different applications.
4) Extensive experiments on the challenging MVTec AD
dataset [12] and the VisA dataset [13] demonstrate
the effectiveness and versatility of our method across
various scenarios. Our FeatDAE sets a new state of the
art in AD, achieving 96.3% region-wise AUPRO and
81.5% pixel-wise AP on the MVTec AD dataset, and
93.3% region-wise AUPRO and 47.1% pixel-wise AP
on the VisA dataset. These results surpass the previous

AD: has been the focus of extensive research in recent
years, and a plethora of approaches have been proposed to
tackle this challenging task in industry. These methods can be
broadly categorized into two main paradigms: reconstructionbased and embedding-based.
Reconstruction-based methods involve training an autoencoder network [6], [9], [14], [15], [16], [17] or a generative
model [4], [18], [19] and operate under the assumption that
anomalies will be poorly reconstructed, thereby making them
distinguishable by their reconstruction error. However, due to
the excellent generalization capabilities of the autoencoder,
this assumption does not always hold, causing suboptimal
performance. Some recent works [6], [20], [21] involved
masking parts of the image or adding random noise, leading to
better robustness of the autoencoder. Some methods [1], [10],
[11], [22], [23], [24] are inspired by supervised segmentation
tasks, by synthetically generating defects during the training
phase with the idea that the model can then generalize on real
anomalies. However, this discriminative model often leads to
overfitting the training set and does not generalize well to real
defects.
Embedding-based methods utilize feature maps [25], [26],
[27] extracted through a pretrained network to learn normality
on these maps. Certain methods [28], [29], [30] operate under
the premise that the characteristics of normal data conform
to a multivariate Gaussian distribution. Consequently, these
approaches leverage the normal training examples to estimate
the pertinent parameters and assume they will not be effective
for anomaly data. Moreover, a variety of approaches [31], [32],
[33], [34] based on normalizing flow have emerged, which
endeavor to approximate the density by projecting an arbitrary
distribution onto a Gaussian distribution. Nevertheless, all
these methodologies presuppose that the distribution of normal
regions will be adequately represented within the training data,
rendering them ineffective when confronted with rare normal
regions that remain unseen during the training phase, thereby
resulting in FPs while facing real anomalous samples.
Denoising autoencoder [35] is an extension of the basic
autoencoder and is trained to use a corrupted version of
the input to reconstruct the original input. A variety of
methods [36], [37], [38], [39], [40] can be considered as
a generalized denoising autoencoder. Building on advancements in natural language processing [41], [42], [43], recent
studies [44], [45], [46] have shown that modern vision
Transformers hold significant potential when applied to representation learning. The inherent disadvantage of two-stage
methods stems from their reliance on a pretrained VAE [47],
tasked with transforming originally continuous data into
intentionally discretized target visual tokens. Conversely,
end-to-end training for masked autoencoders [48], [49] significantly enhances the model’s performance in terms of both
efficacy and efficiency. Our approach further adds noise at the
feature level to improve the generalization of the model while
maintaining accuracy and efficiency.

ZHOU et al.: FeatDAE: INTRODUCING FEATURES WITH DENOISING AUTOENCODER FOR AD

2529914

Fig. 2. Comparison of different architectures for defect detection and localization. (a) Generative model exhibits overgeneralization, leads to a failure in
accurately localizing regions of test-time anomaly samples. (b) Discriminative model struggles to reconstruct real-world anomalies that differ significantly from
the simulated ones, highlighting its limitations in handling unseen or more complex anomalies. (c) Our proposed FeatDAE addresses these issues by applying
transformations at the feature level, significantly expanding the simulated space of anomalous and mitigating the overfitting problem. By reconstructing multiple
types of features, our method achieves a more robust and accurate AD.

Fig. 3. Overview of our framework. By adding Perlin noise at the input space and making feature transformation at the latent space, our FeatDAE is able
to learn more essential features of the sample. The reconstructed features are sent to the feature alignment module along with the noising features, and the
final result is obtained after the segmentation head.

III. M ETHODOLOGY
A. Framework
Let I train = {I1train , . . . , Intrain } be the training set with
anomaly-free samples only, and I test = {I1test , . . . , Imtest } be
the testing set containing both normal and abnormal images.
The goal of AD is to learn from the normal samples in the
training set to accurately identify and locate faults when
presented with a test set. Normal samples in both the training
and test sets are considered to follow the same pattern.
Any out-of-distribution is deemed abnormal. By juxtaposing
input samples of unknown normalcy with previously modeled

normal samples, the derivation of a conclusive anomaly map is
achieved.
Fig. 3 depicts the proposed FeatDAE framework for AD.
At the training stage, the original input image I train ∈ I train
is first fed into a freeze features extractor to obtain normal
histogram of oriented gradient (HOG) feature XHOG and deep
features Xdeep . Second, the image-level noise is added to the
input image and together they are passed into the encoder.
Furthermore, our proposed FRT and FOI are integrated into
the latent space to enrich and simulate a diverse array of defect
characteristics. The decoder generates the corresponding muld
d [
timodal features{X
pix , Xhog , Xdeep }, which are sent into the

2529914

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

feature alignment module together with the previous noising
′
′
features {Xpix
, X ′ hog , Xdeep
}. These aligned features are finally
optimized in the segmentation head to localize the anomalous
regions. For inference, the denoising autoencoder takes the
b. The pixelinput image I test ∈ I test to restore the features X
level anomaly map is generated in an end-to-end manner with
b, and
the aligned input features X and reconstructed features X
the corresponding image-level anomaly scores are computed
through postprocessing.
B. Feature-Level Denoising Autoencoder
Autoencoder is a neural network that is trained to reconstruct its input [50], [51]. The main purpose is to learn,
in an unsupervised manner, an “informative” representation
of the data that can be used for various implications such as
b be the output data,
clustering. Let X be the input data and X
the aforesaid can be formulated as follows:
b = F(X )
X

(1)

where F is the function of the encoder. As formally defined
b and
in [52], the distance between the reconstructed samples X
the inputs X is regarded as the optimization objective. After
being well-trained on anomaly-free sets, the expected outcome
of the autoencoder is to accurately reconstruct normal samples
but not abnormal ones. Therefore, the distance between each
pixel in the input and output can be directly treated as an
anomaly map.
Denoising autoencoder [35] can be viewed as a regularization option, which can extract more crucial information
compared to stander autoencoder [53]. As the difference in the
reconstruction errors in anomalous and nonanomalous regions
increases, the downstream AD results improve [6]. Similar
to an ordinary autoencoder, a denoising autoencoder can be
represented as

b = F X′
X
(2)
where X ′ are generated from X by noise addition.
However, adding noise at the pixel level has several limitations. We observe that methods for simulating noise [1], [10]
inevitably suffer from overfitting. Specifically, while they can
effectively reconstruct noisy training images, they struggle to
accurately reconstruct real anomaly images. In other words,
the pixel-level noise, initially intended to enhance generalization, has paradoxically become a source of overfitting.
Simultaneously, the images themselves contain inherent redundancies. For an extreme example, consider shifting all columns
to the right by one pixel; while the ℓ2 distance between the
old and new images would significantly increase, the intrinsic
information conveyed by the image remains unchanged. The
encoder typically extracts features from the pixels to obtain
a high-dimensional representation Z, which simplifies and
decouples the data to some extent. Hence, we argue that
manipulating features in the latent space can be more effective
in increasing the separation between normal and abnormal
samples, thereby better accommodating the various defects
encountered in real-world scenarios. For instance, we use
ResNet [54] as the encoder and decoder architecture, and
the model consists of several residual-like blocks to ensure

mirror symmetry. Specifically, the encoder downsamples the
input image into latent space Z by four residual blocks while
the corresponding decoder replaces all downsampling with
bilinear upsampling restores the noise-added Z ′ .
To mitigate the aforementioned issues, we have proposed
FeatDAE, a feature-level denoising autoencoder. Inspired by
the success of denoising autoencoders in enhancing network
generalization by introducing noise in the pixel space, our
method operates on features within the latent space. Specifically, FeatDAE applies two operations in the latent space:
FRT and FOI. Our goal is to increase the diversity of samples
in the latent space, thereby reducing overfitting to pixel-level
synthetic defective samples and guiding the network to focus
its generalization on real anomaly samples.
1) Feature Radial Transformation: For a batch containing
B identities, where each feature map Z ∈ RC×H ×W , we notice
that traditional convolution kernels often focus only on local
information, which may not fully capture global context
even after passing through multiple layers of deep networks.
To enhance the model’s global understanding and increase
diversity in the latent space, we introduce a radial movement to
each feature, moving it away from the batch samples’ hidden
space centroid. The centroid of a feature map can be defined
as the average spatial coordinates of its nonzero elements. For
simplicity, we assume the centroids are calculated over the
spatial dimensions (H, W ) for each channel c
!
P H PW
P H PW
w
·
Z
(h,
w)
h
·
Z
(h,
w)
i
i
h=1
w=1
h=1
w=1
, P
.
ci =
P H PW
H PW
Z
(h,
w)
i
h=1
w=1
h=1
w=1 Zi (h, w)
(3)
The center Z ∈ RC×H ×W for the batch samples is computed
as the mean across all feature maps
B

Z=

1 X
Zi
B i=1

(4)

where i indexes the individual feature maps within the batch.
Similarly, the centroid of the center Z is
!
P H PW
P H PW
h=1
w=1 h · Z(h, w)
h=1
w=1 w · Z(h, w)
, P H PW
.
c=
P H PW
h=1
w=1 Z(h, w)
h=1
w=1 Z(h, w)
(5)
The translation vector (tx , t y ) of the translation matrix T
for the ith sample is calculated as the difference between the
centroid of the feature map ci and the centroid of the center c
(tx , t y ) = ci − c.

(6)

This ensures that the translation moves the feature map away
from the center in the direction from c to ci , with the
magnitude being a proportion α of the distance between the
two centroids. The translation matrix T is addressed by


0 0 tx
T = 0 0 t y .
(7)
0 0 1
Rotation can break this locality, acting as a form of “feature
rearrangement” that changes the spatial structure of features
and forces the model to understand and integrate these changes

ZHOU et al.: FeatDAE: INTRODUCING FEATURES WITH DENOISING AUTOENCODER FOR AD

at a higher level, which is especially important for latent space
features requiring global understanding. Specifically, when we
randomly select an angle θ to rotate the extracted 2-D feature
map, the rotation transformation around the origin by an angle
θ can be represented by the following matrix:


cos(θ ) − sin(θ ) 0
cos(θ )
0.
R(θ ) =  sin(θ )
(8)
0
0
1
To combine the rotation and translation into a single affine
transformation, we multiply the rotation matrix R(θ ) by the
translation matrix T with a scale factor α ∈ [0, 1]. Applying
the combined affine transformation to the original coordinates
(x, y) in the feature map Zi gives us the final transformed
coordinates (x ′ , y ′ )
 ′ 
 
x
cos(θ ) − sin(θ ) α · tx
x
 y ′  =  sin(θ )
cos(θ )
α · t y  y .
(9)
1
0
0
1
1
2) Feature Omnidirectional Injection: Our approach aims
to expand the distribution of anomalies in the hidden space.
Inspired by the widely adopted practice of adding noise at
the image level for data augmentation [55], we introduce
Gaussian noise with a mean of 0 directly into the latent space.
As the depth of neural networks escalates, they are predisposed
to the vanishing gradient problem, a phenomenon where the
gradients diminish exponentially as they are backpropagated
through the layers, which can impede the learning process and
degrade the performance of deep models [54]. In the context
of our proposed method, noise introduced at the input image
level tends to have a diminishing impact as it is propagated
through the network. By the time this noise reaches the latter
stages of the network, particularly the decoder, its influence
is substantially attenuated. This observation motivates us to
introduce noise directly into the latent space, an approach
that capitalizes on the inherent robustness of the deeper
decoder layers. We aim to augment the model’s ability to
generalize from the training data to unseen data, especially
when faced with real-world anomalies that were not present
during training. The injection of noise into the latent space
serves as a form of regularization, which not only helps
mitigate the risk of overfitting but also improves the model’s
resilience against various types of anomalies. Consequently,
this strategy enhances the overall robustness and adaptability
of the computer vision system, making it more reliable and
effective in practical defects.
Unlike the introduced FRT, which imposes a directional bias
on the feature transformation, the FOI does not specify the
transformation direction. It diffuses features uniformly across
all dimensions, leading to a more isotropic distribution of
the anomalies in the latent space. To control the intensity of
the Gaussian noise, we employ a random scaling factor β,
allowing us to modulate the magnitude of the perturbation.
This is achieved according to the following formula:

Z ′′ = Z ′ + β · N 0, σ 2
(10)
where Z ′ represents the latent representation after the previous FRT, N (0, σ 2 ) denotes the Gaussian noise, and β is a
randomly determined coefficient that scales the strength of the

2529914

noise. By adjusting β, we can effectively balance the degree
of perturbation and the preservation of the feature structure,
ensuring that the data remains representative of the underlying
distribution while providing sufficient variability to train a
more generalized model.
C. Reconstruction Targets
For autoencoder based on reconstruction, a crucial issue
lies in selecting the target feature X for reconstruction.
We simultaneously consider reconstruction at different levels
of granularity, including pixel features Xpix directly from
the image samples, histogram of oriented gradients (HOG)
features Xhog extracted through traditional operators, and deep
features Xdeep obtained through a pretrained neural network.
Pixel color is the most simple and straightforward target for
feature reconstruction. In various similar tasks such as image
inpainting [37] and mask prediction [56], pixel color reconstruction has been widely employed. Specifically, we treat
the image from the dataset I as the reconstruction target
Xpix for the autoencoder. Unlike the masked image modeling
approaches [48], [49] that only count the masked area, our
method computes the loss of all pixels.
HOG is a feature descriptor widely used in computer vision
and image processing for object detection. It characterizes
local object appearance and shape based on gradient orientations within an image. Given an image I , HOG first computes
the gradient information
G x (x, y) = p(x + 1, y) − p(x − 1, y)
G y (x, y) = p(x, y + 1) − p(x, y − 1)

(11)
(12)

where G x (x, y) and G y (x, y) are the horizontal gradient and
vertical gradient at pixel p(x, y), respectively. The gradient
magnitude G(x, y) and orientation θ (x, y) are calculated as
q
(13)
∇G(x, y) = G x (x, y)2 + G y (x, y)2


G y (x, y)
θ (x, y) = arctan
.
(14)
G x (x, y)
The next process involves dividing the image into small
connected regions called cells and computing histograms
for each cell. Specifically, the gradients within each cell
are then accumulated into orientation histogram vectors of
several bins, voted by gradient magnitudes. The final HOG
descriptor is the concatenation of all normalized histograms
from the cells, which captures local texture patterns and
edge directions. Since HOG operates on localized cells of
the image, it maintains good invariance to geometric and
photometric transformations. The coarse spatial sampling and
fine orientation sampling allow robustness while strong local
normalization handles illumination changes. The efficiency
and robustness to various conditions make HOG suitable for
pattern recognition [57], [58] and feature reconstruction [59].
We collect HOG in each RGB channel to include color
information which can improve its performance. The image
samples I that computed the HOG feature map on the whole
image are formed into Xhog . Our method then learns to restore
the histograms Xhog from the input noising image X ′ .
Deep features are obtained by extracting intermediate layer
features from a neural network. The neural network transforms

2529914

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

the input data into a more expressive form, which is capable
of capturing the essence of the data across various contexts.
Taking inspiration from knowledge distillation [60], we design
our student networks to learn from the teacher networks
similarly. However, unlike knowledge distillation, our method
involves different inputs for the teacher and student networks.
Our DAE serves as the student network and performs denoising reconstruction on input anomaly images, whether they
are real anomalous or noise-added. In contrast, the teacher
network processes anomaly-free images. Further, to better
leverage the semantic information from low-resolution to
high-resolution, we proposed a layer-by-layer deep features
reconstruction hierarchy. In our method, we use an ImageNet
[61] pretrained ResNet [54] as our feature extractor to derive
features from normal images. Specifically, the deep features
3
2
4
{Xdeep
, Xdeep
, Xdeep
} are obtained from the conv2_x, conv3_x,
and conv4_x blocks with strides of {4, 8, 16} pixels relative to
the input image.
D. Features Alignment Module
As illustrated in Section III-C, our reconstruction targets
incorporate a variety of distinct feature types. Pixel color
features have the lowest dimensionality and primarily capture
the original texture information necessary for reconstructing
anomaly-free samples. In comparison, HOG features are more
robust to variations in lighting and are capable of capturing
edge and shape information within the image. While both
pixel color and HOG features ensure detail preservation at
larger scales, the deep features of different sizes predominantly
contain different levels of semantic information, which is critical for subsequent segmentation tasks. Therefore, to handle
the features discriminability varies across different levels of
abstraction, we proposed the features alignment module to
b
better integrate features between input X and reconstructed X
as described in Fig. 4. Each lateral connection fuses the input
features and reconstructed features of the same spatial size and
type form and computes the corresponding reconstruction loss
L krec . These merged features are then resized and concatenated
into the aligned features used for subsequent segmentation
heads.
Through element-wise multiplication, the paired features are
merged without change in dimension. We also investigate alternative ways to compute the aligned features in Section IV-F.
Among the multiple feature targets, pixel color and HOG
have the same size as the original image, while deep features
include multiple scales. We uniformly scaled all the features
into 1/4th of the input size, the same size as the largest feature
map in deep features. While this scale results in loss of detail
to some extent, oversizing exponentially increases the amount
of computation and memory usage, which is critical for
real-time applications.
E. Objective
As mentioned earlier, our feature space varies in type and
dimensions. We follow [7] of using cosine distance for knowledge transferring to more accurately capture the relationship
between high- and low-dimensional information [65]. At each

Fig. 4. Features alignment module. At each scale, the input and reconstructed
features are fused through pixel-wise multiplication. The merged features
then undergo a resizing operation to ensure uniformity in size, followed
by concatenation along the feature dimensions. The spectrum of multiscale
features comprises pixel color, HOG, and deep features.

scale k, we calculate their vector-wise cosine similarity loss
along the channel axis
L cos
k =1−

L cos
rec =

K
X

ck
Xk · X


ck ∥2 , ϵ
max(∥X k ∥2 , ϵ) · max ∥X
L cos
k

(15)

(16)

k=1

where ϵ is a small value to avoid division by zero and k is
the target features number.
We follow DRAEM [1] training a segmentation head guided
by additional supervision to discriminate the fusion features
appropriately. By concurrently inputting the reconstructed
results and the original image into the head, employing the
mask as the supervise for training the anomaly map as follows:

c
L dis
(17)
seg = ℓ1 M, M
c are the ground-truth binary masks generated
where M and M
from noise and the output anomaly segmentation masks from
the head, respectively. Since defects usually make up only
a small portion of the image, only a minority of pixels
are considered foreground for the segmentation task. Focal
loss [66] allows the model to focus more on hard samples
and helps to solve the problem of background and foreground
imbalance
γ
L focal
seg = −(1 − p) log( p)

c + (1 − M) 1 − M
c
p = MM

(18)
(19)

where γ is the focusing parameter.
Along with the reconstruction loss and the segmentation
losses mentioned above, the total objective of our network is
formulated as follows:
dis
focal
L = L cos
rec + L seg + L seg .

(20)

Specifically, we normalize each loss term by dividing it by its
maximum value across the training dataset. This normalization
ensures that no single loss term dominates the others, allowing
for a more stable and effective training process.

ZHOU et al.: FeatDAE: INTRODUCING FEATURES WITH DENOISING AUTOENCODER FOR AD

2529914

TABLE I
C OMPARISON IN I MAGE -W ISE AUROC AND P IXEL -W ISE AUROC W ITH S TATE - OF - THE -A RT W ORKS ON THE
MVT EC AD DATASET (I-AUROC/P-AUROC). W E D ENOTE THE B EST R ESULTS BY B OLD

TABLE II
C OMPARISON IN P IXEL -W ISE AP AND R EGION -W ISE AUPRO W ITH S TATE - OF - THE -A RT W ORKS ON THE
MVT EC AD DATASET (AP/AUPRO). W E D ENOTE THE B EST R ESULTS BY B OLD

IV. E XPERIMENTS
A. Dataset
We conducted our experiments on the most recent challenging MVTec AD dataset [12] and the popular VisA dataset [13],
as the standard benchmarks for evaluating unsupervised surface AD and localization. The MVTec AD dataset consisted of
five texture and ten object categories stemming from manufacturing, with 3629 training images and 1725 test images. The
image size ranged from 700 × 700 to 1024 × 1024 pixels.
The training split was composed of normal images, and the
testing split contained both normal and anomaly images with
various types of defects. It also provided detailed pixel-wise
mask annotations for defective test images. The VisA AD
dataset [13] was a challenging collection of images designed
for evaluating machine-learning models’ performance in identifying anomalies. It consisted of 10 821 images in total, with
9621 normal images and 1200 abnormal images. The dataset
was organized into 12 subsets, each representing a distinct
class of objects. Abnormal images within the MVTec and

VisA datasets exhibited a range of defects, including surface
imperfections like scratches, dents, colored spots, or cracks,
as well as structural issues such as misplacement or missing
components. The dataset was also divided into normal images
in the training set and labeled normal and abnormal images
in the testing set, making it suitable for unsupervised AD
approaches.
B. Evaluation Metrics
In prior works, the area under the receiver operating curve
(AUROC) was utilized to evaluate image-wise AD and pixelwise anomaly localization. While only a minority of pixels
were attributed to abnormal, the AUROC did not reveal
the accuracy of localization under heavily imbalanced conditions [67]. For pixel-wise evaluation, we additionally reported
the average precision (AP) [68] and area under per-regionoverlap (AUPRO) [69], which expressed the performance for
anomaly localization more effectively. The AUPRO assigned
equal weight to connected components of different sizes in

2529914

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

TABLE III
C OMPARISON IN I MAGE -W ISE AUROC AND P IXEL -W ISE AUROC W ITH S TATE - OF - THE -A RT W ORKS
ON THE V IS A DATASET (I-AUROC/P-AUROC). W E D ENOTE THE B EST R ESULTS BY B OLD

TABLE IV
C OMPARISON IN P IXEL -W ISE AP AND R EGION -W ISE AUPRO W ITH S TATE - OF - THE -A RT W ORKS ON THE V IS A
DATASET (AP/AUPRO). W E D ENOTE THE B EST R ESULTS BY B OLD

the ground truth (GT) and repeatedly computed the overlap
between the prediction and the GT for the FP rate within 30%.
C. Implementation Details
Our implementation was based on the PyTorch framework.
We used ResNet-18 [54] as our encoder and a symmetric
reverse ResNet-18 architecture with upsampling instead of
downsampling in all residual blocks as our decoder. Note that
the encoder was pretrained on the ImageNet [61] dataset, while
the decoder utilized the Kaiming initialization [70]. For the
segmentation head, we adopted the widely used ASPP [71]
structure. The learning rate was set to 0.001 on the SGD optimizer with a momentum of 0.9 and a weight decay of 0.001.
We trained the denoising autoencoder for 4000 iterations and
the segmentation head for 16 000 iterations with a batch size
of 8. We uniformly resized the images to 256 × 256 pixels,
applied a random rotation of up to 5◦ for nonaligned targets
(cable, wood, and zipper), and another random rotation within
360◦ for rotation-invariant textures (carpet, grid, leather, and
tile) and objects (bottle, hazelnut, and screw). All images were
normalized using the mean and standard deviation of ImageNet
before feeding them into the model.
D. Quantitative Results
1) Accuracy: Table I quantitatively compared FeatDAE
with recent state-of-the-art approaches on the MVTec AD

Fig. 5. AD performance versus FPS on the MVTec AD dataset, where our
FeatDAE outperforms all previous methods on both accuracy and efficiency
by a significant margin.

dataset under the AUROC metric. For the image-level AD
task, FeatDAE achieved a perfect I-AUROC score in 7 out of
15 classes.
Table II further reported the pixel-wise AP and AUPRO
for the pixel-level anomaly localization task, in addition to
the P-AUROC metric. Overall, our FeatDAE also achieved

ZHOU et al.: FeatDAE: INTRODUCING FEATURES WITH DENOISING AUTOENCODER FOR AD

2529914

Fig. 6. Case of ambiguous anomalies on the MVTec AD dataset. From left
to right: sampled image, GT, and anomaly map.

the best average results across these metrics. Our FeatDAE
significantly outperformed all previous best-performing AD
methods by a large margin. On average, our method surpassed
the cutting-edge methods by 5.7% points in terms of pixel-wise
AP. Our method achieved optimal performance in the majority
of categories, demonstrating its applicability and robustness
across various scenarios.
We also conducted experiments on the popular VisA dataset,
which is a comprehensive benchmark for AD. We used the
same metrics as the MVTec AD dataset to evaluate the
performance across image-wise AUROC, pixel-wise AUROC,
pixel-wise AP, and region-wise AUPRO. These metrics provided a holistic view of the model’s ability to detect anomalies
at different levels of granularity. Notably, our FeatDAE utilized
ResNet-18 [54] as the backbone, while previous methods [7],
[24], [25] employed WideResNet-50 [72]. Therefore, our
method could be more readily deployed on edge devices with
suboptimal performance in actual industrial pipelines.
As can be seen in Table III, the image-wise AUROC and the
pixel-wise AUROC were strong, indicating high accuracy in
distinguishing between normal and anomalous images with the
lightweight ResNet-18 backbone. Table IV reports the pixelwise AP and AUPRO on the VisA dataset. In pixel-wise AP,
FeatDAE also performed well, achieving an average score
of 47.1%, ranking it among the top methods. Notably, our
method ranked second in terms of region-wise AUPRO, with
an average score of 93.3%. While the GLAD method [64]
achieves high accuracy, it suffers from inefficiency due to
the step-by-step generation process of diffusion models. The
superior performance in these metrics underscored the exceptional capability of our method in accurately pinpointing
anomalous. Our FeatDAE precisely localized the regions of
interest, making it a powerful tool for applications requiring
fine-grained AD.
2) Efficiency: Anomaly detector is commonly employed
in industrial production lines, where the system must be
lightweight to meet real-time processing demands. As illustrated in Fig. 5, we evaluate the model’s capability in
accurately localizing defects using the AUPRO metric, and its
operational efficiency is assessed by the frames per second
(FPS). The figure demonstrates that our proposed method
attains a balance between precision and speed, achieving
optimal performance on both metrics.

Fig. 7. Qualitative comparison on the MVTec AD dataset. Input image,
anomaly map, and GT are shown.

3) Ambiguity: Upon meticulous examination, it was discerned that a portion of the detection inaccuracies could be
ascribed to imprecise GT labels in cases of equivocal anomalies. This phenomenon was exemplified in Fig. 6, wherein
the GT contained only the deformed sections of the capsule,
yet it comprehensively included every aspect of the pill. Our
method delineated the entire deformed area of the capsule and
accurately segmented the yellow spots on the pill. However,
discrepancies with the actual GT led to cumulative errors in
the localization metrics. Despite this, we believed our approach
remained viable in such scenarios.
E. Qualitative Results
We also compared the qualitative results of different models
on the MVTec AD dataset, as illustrated in Fig. 7. Test set
images are displayed to demonstrate each model’s performance on previously unseen anomalous samples. Accompanying these images are prediction anomaly maps, where red
signifies high detection confidence and blue indicates low
confidence. GT masks delineate the actual anomaly regions,
enabling a direct comparison between predicted and true defect
locations.
From the results, it is evident that our method achieves
precise localization of all anomalies compared to alternative
approaches. For smaller anomaly regions, such as those in the
capsule and screw categories, RD [7] tends to overestimate
the size of the mask region, while DRAEM [1] introduces
FPs. In contrast, our method produces sharp and accurate
boundaries. In cases of irregularly shaped defects, like those
found in the hazelnut and transistor categories, other methods
either underestimate the defect area or exhibit other inaccuracies. Our method, however, aligns closely with the true

2529914

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 8.

Visualization examples of our method on the MVTec AD dataset. Sampled images, GTs, and anomaly maps are shown.

Fig. 9.

Visualization examples of our method on the VisA dataset. Sampled images, GTs, and anomaly maps are shown.

contours of the anomalies and exhibits higher confidence in
its predictions. When dealing with multiple anomaly regions
within a single sample, such as in the pill and wood categories, SimpleNet [24] suffers from overdetection, whereas
DRAEM [1] experiences underdetection. Moreover, the localization of anomaly areas by other methods can be imprecise.
Our approach, on the other hand, accurately predicts the
number of defects present and provides precise localization,
thereby demonstrating consistent accuracy in detecting anomalies across different types of objects and defect patterns.
We further provided visualization examples showcasing the
performance of our method on the MVTec AD dataset and
the VisA dataset in Figs. 8 and 9, respectively. In each figure,
we displayed a selection of images alongside their GT labels

and the anomaly maps generated by our approach. These
visualizations served as a testament to the robustness and
accuracy of our AD method across diverse object categories
and anomaly types.
F. Ablation Studies
1) Architecture: The ablation studies presented in Table V
provide insights into the contributions of our proposed FRT,
FOI, and the selection of reconstruction targets, including
pixel color, HOG features, and deep features, to the overall
performance of our model. In an ablation study examining
the contributions of our main design elements, we observe
significant impacts on detection (reported in AUROC) and
localization (reported in AP) performances. Notably, when

ZHOU et al.: FeatDAE: INTRODUCING FEATURES WITH DENOISING AUTOENCODER FOR AD

2529914

TABLE V

TABLE VII

A BLATION S TUDIES ON O UR M AIN D ESIGNS . D ETECTION (D ET.)
R ESULTS A RE R EPORTED IN AUROC AND L OCALIZATION (L OC .)
R ESULTS A RE R EPORTED IN AP. T HE D EFAULT E NTRY
I S M ARKED AS G RAY

A BLATION S TUDIES ON THE T YPE OF THE N OISE IN I NPUT
S PACE . T HE D EFAULT E NTRY I S M ARKED AS G RAY

TABLE VIII
A BLATION S TUDIES ON F EATURE -L EVEL N OISE S CALE .
T HE D EFAULT E NTRY I S M ARKED AS G RAY

TABLE VI
A BLATION S TUDIES ON F EATURES A LIGNMENT M ODULE
I MPLEMENTATION . T HE D EFAULT E NTRY I S M ARKED AS G RAY

FRT is absent but feature-level omnidirectional injection (FOI)
is applied (Experiment 2), the model achieves a high detection
score of 99.3% and a localization score of 80.9%, indicating
that FOI alone significantly enhances the model’s robustness.
Conversely, Experiment 3, where FRT is present without FOI,
shows slightly lower performance metrics, suggesting that
while beneficial, its impact does not match that of FOI in this
context. Further insights are gained from Experiments 4 to 6,
which omit pixel, HOG, and deep feature reconstructions,
respectively. The importance of these features for maintaining high localization accuracy is evident, with the absence
of HOG features (Experiment 4) leading to a decrease in
localization performance from the optimal baseline of 81.5%
down to 79.9% and excluding deep features (Experiment 6)
resulting in a detection score of 98.7% and a localization
score of 73.6%. This underscores the essential roles of HOG
features in capturing texture and edge information and deep
features in conveying higher level semantic details critical
for precise anomaly localization. The default setup (Experiment 7), incorporating all design elements—FRT, FOI, and
comprehensive feature reconstruction—achieves the highest
detection AUROC of 99.4% and localization AP of 81.5%.
This highlights the synergistic benefits of integrating all proposed strategies, optimizing both detection and localization
capabilities.
2) Operator in Feature Alignment Module: Table VI
presents the results of experiments conducted using different
fusion operations including addition, subtraction, multiplication, and concatenation on the input features and reconstructed
features illustrated in Fig. 4. The subtraction operation exhibited superior performance compared to addition in localization,
as it simulated the calculation of the reconstruction loss and
introduced more prior knowledge. The concatenation operator
achieved higher results due to retaining complete information
from both the input features and the reconstruction features.
However, these operators were all inferior to the multiplication
operator, indicating its suitability for our task. Excessive prior

knowledge or overly comprehensive information might lead to
suboptimal network performance.
3) Input Space Noise Type: Table VII presents an ablation
study on the impact of different types of noise added to the
input space on detection performance. Rectangle simulates
anomaly regions by adding rectangular masks to the input
images. Masks of MAE are generated by splitting the image
into a grid of rectangular regions. For Gaussian noise and
Perlin noise, a threshold of 0.5 is applied to the noise before
generating the final mask.
The Perlin noise achieves the highest detection and localization accuracy, outperforming other noise types. This suggests
that Perlin noise, which generates more complex and varied
patterns, better mimics real-world anomalies, allowing the
model to learn more realistic and diverse defect patterns.
4) Latent Space Noise Scale: Table VIII revealed the effect
of σ on AD. The minuscule σ signified that the features
after passing through the encoder had not been endowed with
sufficient noise, resulting in the denoising autoencoder as a
whole failing to capture the intrinsic feature distribution of
the samples.
Consequently, its performance during testing was subpar.
However, an excessively large σ altered the original distribution of the extracted features, leading to inconsistent learning
within the network, thus causing ambiguous decision-making.
As can be seen from Table VIII, with the gradual increase
in σ , the final detection and segmentation results exhibited
a trend of first rising and then declining. Hence, we opted
for sampling σ within the range of (0.01, 0.04) and adding
feature-level Gaussian noise in this manner, as experiments
demonstrated it yielded optimal results.
5) Loss: In Table IX, we investigated the influence of
different loss functions. Utilizing traditional ℓ1 or ℓ2 distance
functions led to a significant decrease in results, mainly due
to our FeatDAE aggregating multiple feature reconstruction
results for the final segmentation. The cosine distance function was better equipped to handle high-dimensional features,
as our experiments validated the soundness of this choice.
Table X demonstrated the impact of different losses on the
segmentation task. Given that defects typically occupied only
a small portion of the sample, we employed focal loss [66] to
balance positive and negative samples. Although in the case of
using only a single type of loss, ℓ2 yielded relatively favorable

2529914

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

TABLE IX
A BLATION S TUDIES ON THE R ECONSTRUCTION L OSS .
T HE D EFAULT E NTRY I S M ARKED AS G RAY

TABLE X
A BLATION S TUDIES ON THE S EGMENTATION L OSS . T HE
D EFAULT E NTRY I S MARKED AS G RAY

TABLE XI
C OMPARISON IN P IXEL -W ISE AP, F1-M AX AND I TS C ORRESPONDING
P RECISION AND R ECALL W ITH S TATE - OF - THE -A RT W ORKS ON THE
MVT EC AD DATASET. W E D ENOTE THE B EST R ESULTS BY BOLD

TABLE XII
C OMPARISON ON C LASSIFICATION R ESULTS OF D IFFERENT A NOMALY
S IMULATION M ETHODS , ACC R EPRESENTS THE P ROBABILITY OF THE
G ENERATED S AMPLES B EING C ORRECTLY D ISTINGUISHED
F ROM R EAL S AMPLES

results, its combination with focal loss performed suboptimally
compared to our default entry. Thanks to ℓ1’s supervision of
defect edges and focal loss’s balance of small defects, the
accuracy of our method was greatly improved in the AD task.
G. Other Discussions
1) False Detection: To further validate the efficacy of
our proposed method in significantly reducing FPs and FNs,
we conducted a thorough evaluation of the MVTec AD
dataset. As shown in Table XI, our method outperforms
other approaches across all four key metrics. The F1-score,
being the harmonic mean of precision and recall, reflects
a balanced enhancement in both these metrics. Specifically,
our method attains an F1-score of 71.8%, surpassing the
nearest competitor’s score of 66.7%. With a precision of
71.3%, our approach ensures that a high proportion of detected
anomalies are genuine, thereby significantly reducing FP rates.
Simultaneously, a recall of 72.7% indicates that our method
successfully identifies a larger fraction of actual anomalies,
drastically lowering FN rates.
2) Domain Gap: To highlight the significant gap between
current anomaly simulation methods and real-world anomalous, we conducted an experiment using a simple classification
network. As shown in Table XII, this classifier rapidly learned

to distinguish between simulated and real anomalous after just
a few training epochs. This result underscores the limitations
of existing simulation techniques in capturing the complexity
and variability of real-world anomalous, leading to models
that perform well on synthetic data but fail to generalize
to practical applications, thereby compromising their utility.
However, by transforming the feature in the latent space,
we can develop more realistic training data, enhancing the
simulation’s ability to replicate the intrinsic characteristics of
actual anomalies. Our approach not only increases the diversity
of the simulated data but also leads to a more robust and
reliable AD model.
V. C ONCLUSION
A novel denoising autoencoder with features is tailored
for industrial AD tasks. Recent methods of AD that rely on
reconstruction, often falter in the face of genuine anomalies during the testing phase, attributed to the scarcity of
authentic defect samples throughout the training stage of
the task. By ingeniously incorporating noise at the latent
space, with a diverse array of reconstruction targets and a
unique feature alignment module, our FeatDAE adeptly overcomes the prevalent overgeneralization and overfitting issues
in reconstruction-based models. The experiments conducted on
the surface AD benchmarks reveal that each of our proposed
components markedly enhances the performance. Our results
outperform the previous state-of-the-art methods by 5.7%
pixel-wise AP on the MVTec AD dataset and 3.8% pixel-wise
AP on the VisA dataset, with an extremely high inference
speed. At present, the localization capability of our model
exhibits variability when confronted with different classes.
By taking into account disparities in size, texture, and labeling,
we leave achieving uniform performance across the spectrum
of anomalous and emerges as a paramount objective for future
work.
R EFERENCES
[1] V. Zavrtanik, M. Kristan, and D. Skočaj, “Draem—A discriminatively
trained reconstruction embedding for surface anomaly detection,” in
Proc. IEEE/CVF Int. Conf. Comput. Vis., Jun. 2021, pp. 8330–8339.
[2] Q. Wan, Y. Cao, L. Gao, X. Li, and Y. Gao, “Deep feature contrasting for
industrial image anomaly segmentation,” IEEE Trans. Instrum. Meas.,
vol. 73, pp. 1–11, 2024.
[3] X. Li, J. Jing, J. Bao, P. Lu, Y. Xie, and Y. An, “OTB-AAE: Semisupervised anomaly detection on industrial images based on adversarial
autoencoder with output-turn-back structure,” IEEE Trans. Instrum.
Meas., vol. 72, pp. 1–14, 2023.
[4] S. Akcay, A. Atapour-Abarghouei, and T. P. Breckon, “GANomaly:
Semi-supervised anomaly detection via adversarial training,” in Proc.
14th Asian Conf. Comput. Vis., Dec. 2019, pp. 622–637.
[5] S. Akcay, A. Atapour-Abarghouei, and T. P. Breckon, “Skip-GANomaly:
Skip connected and adversarially trained encoder–decoder anomaly
detection,” in Proc. Int. Joint Conf. Neural Netw., 2019, pp. 1–8.
[6] V. Zavrtanik, M. Kristan, and D. Skočaj, “Reconstruction by inpainting
for visual anomaly detection,” Pattern Recognit., vol. 112, Apr. 2021,
Art. no. 107706.
[7] H. Deng and X. Li, “Anomaly detection via reverse distillation from
one-class embedding,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2022, pp. 9737–9746.
[8] H. He et al., “A diffusion-based framework for multi-class anomaly
detection,” in Proc. AAAI Conf. Artif. Intell., Mar. 2024, vol. 38, no. 8,
pp. 8472–8480.
[9] P. Bergmann, S. Löwe, M. Fauser, D. Sattlegger, and C. Steger, “Improving unsupervised defect segmentation by applying structural similarity
to autoencoders,” 2018, arXiv:1807.02011.

ZHOU et al.: FeatDAE: INTRODUCING FEATURES WITH DENOISING AUTOENCODER FOR AD

[10] X. Zhang, S. Li, X. Li, P. Huang, J. Shan, and T. Chen, “DeSTSeg:
Segmentation guided denoising student–teacher for anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2023, pp. 3914–3923.
[11] M. Yang, P. Wu, and H. Feng, “MemSeg: A semi-supervised method
for image surface defect detection using differences and commonalities,”
Eng. Appl. Artif. Intell., vol. 119, Mar. 2023, Art. no. 105835.
[12] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec
AD—A comprehensive real-world dataset for unsupervised anomaly
detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2019, pp. 9584–9592.
[13] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, “SPotthe-difference self-supervised pre-training for anomaly detection and
segmentation,” in Proc. Eur. Conf. Comput. Vis., Jan. 2022, pp. 392–408.
[14] M. Sakurada and T. Yairi, “Anomaly detection using autoencoders with
nonlinear dimensionality reduction,” in Proc. MLSDA 2nd Workshop
Mach. Learn. Sensory Data Anal., Dec. 2014, pp. 4–11.
[15] Y. He, H. Yang, and Z. Yin, “Adaptive context-aware distillation
for industrial image anomaly detection,” IEEE Trans. Instrum. Meas.,
vol. 73, pp. 1–15, 2024.
[16] J. Zhu, P. Yan, J. Jiang, Y. Cui, and X. Xu, “Asymmetric teacher–student
feature pyramid matching for industrial anomaly detection,” IEEE Trans.
Instrum. Meas., vol. 73, pp. 1–13, 2024.
[17] H. Yao et al., “Scalable industrial visual anomaly detection with partial
semantics aggregation vision transformer,” IEEE Trans. Instrum. Meas.,
vol. 73, pp. 1–17, 2024.
[18] T. Schlegl, P. Seeböck, S. M. Waldstein, G. Langs, and U. SchmidtErfurth, “F-AnoGAN: Fast unsupervised anomaly detection with
generative adversarial networks,” Med. Image Anal., vol. 54, pp. 30–44,
May 2019.
[19] J. Wyatt, A. Leach, S. M. Schmon, and C. G. Willcocks, “AnoDDPM:
Anomaly detection with denoising diffusion probabilistic models using
simplex noise,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2022, pp. 650–656.
[20] A.-S. Collin and C. De Vleeschouwer, “Improved anomaly detection by
training an autoencoder with skip connections on images corrupted with
stain-shaped noise,” in Proc. 25th Int. Conf. Pattern Recognit. (ICPR),
Jan. 2021, pp. 7915–7922.
[21] A. Kascenas, N. Pugeault, and A. Q. O’Neil, “Denoising autoencoders
for unsupervised anomaly detection in brain MRI,” in Proc. Int. Conf.
Med. Imag. Deep Learn., 2022, pp. 653–664.
[22] V. Zavrtanik, M. Kristan, and D. Skočaj, “DSR—A dual subspace reprojection network for surface anomaly detection,” in Proc. Eur. Conf.
Comput. Vis., 2022, pp. 539–554.
[23] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Selfsupervised learning for anomaly detection and localization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 9664–9674.
[24] Z. Liu, Y. Zhou, Y. Xu, and Z. Wang, “SimpleNet: A simple network
for image anomaly detection and localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., Jun. 2023, pp. 20402–20411.
[25] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and
P. Gehler, “Towards total recall in industrial anomaly detection,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2022,
pp. 14318–14328.
[26] J. Jang, E. Hwang, and S.-H. Park, “N-pad: Neighboring pixel-based
industrial anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit., Jun. 2023, pp. 4364–4373.
[27] Y. Liu, X. Gao, J. Z. Wen, and H. Luo, “Unsupervised image anomaly
detection and localization in industry based on self-updated memory and
center clustering,” IEEE Trans. Instrum. Meas., vol. 72, pp. 1–10, 2023.
[28] K. Lee, K. Lee, H. Lee, and J. Shin, “A simple unified framework for
detecting out-of-distribution samples and adversarial attacks,” in Proc.
Adv. Neural Inf. Process. Syst., Jan. 2018, pp. 7167–7177.
[29] O. Rippel, P. Mertens, and D. Merhof, “Modeling the distribution of
normal data in pre-trained deep features for anomaly detection,” in Proc.
25th Int. Conf. Pattern Recognit. (ICPR), Jan. 2021, pp. 6726–6733.
[30] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “PaDiM: A patch
distribution modeling framework for anomaly detection and localization,” in Proc. Int. Conf. Pattern Recognit. Cham, Switzerland: Springer,
Jan. 2021, pp. 475–489.
[31] J. Yu et al., “FastFlow: Unsupervised anomaly detection and
localization via 2D normalizing flows,” 2021, arXiv:2111.
07677.

2529914

[32] D. Gudovskiy, S. Ishizaka, and K. Kozuka, “CFLOW-AD: Real-time
unsupervised anomaly detection with localization via conditional normalizing flows,” in Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis.
(WACV), Jan. 2022, pp. 98–107.
[33] M. Rudolph, T. Wehrbein, B. Rosenhahn, and B. Wandt, “Fully
convolutional cross-scale-flows for image-based defect detection,” in
Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis. (WACV), Jan. 2022,
pp. 1088–1097.
[34] M. Tailanian, Á. Pardo, and P. Musé, “U-flow: A U-shaped normalizing flow for anomaly detection with unsupervised threshold,” 2022,
arXiv:2211.12353.
[35] P. Vincent, H. Larochelle, Y. Bengio, and P.-A. Manzagol, “Extracting
and composing robust features with denoising autoencoders,” in Proc.
25th Int. Conf. Mach. Learn. (ICML), 2008, pp. 1096–1103.
[36] P. Vincent, H. Larochelle, I. Lajoie, Y. Bengio, P.-A. Manzagol, and
L. Bottou, “Stacked denoising autoencoders: Learning useful representations in a deep network with a local denoising criterion,” J. Mach. Learn.
Res., vol. 11, no. 12, pp. 3371–3408, 2010.
[37] D. Pathak, P. Krähenbühl, J. Donahue, T. Darrell, and A. A. Efros,
“Context encoders: Feature learning by inpainting,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2016, pp. 2536–2544.
[38] R. A. Yeh, C. Chen, T. Y. Lim, A. G. Schwing, M. Hasegawa-Johnson,
and M. N. Do, “Semantic image inpainting with deep generative
models,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., Jul. 2017,
pp. 5485–5493.
[39] J. Yu, Z. Lin, J. Yang, X. Shen, X. Lu, and T. Huang, “Free-form
image inpainting with gated convolution,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis. (ICCV), Oct. 2019, pp. 4471–4480.
[40] O. Henaff, “Data-efficient image recognition with contrastive predictive
coding,” in Proc. Int. Conf. Mach. Learn. (PMLR), 2020, pp. 4182–4192.
[41] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training
of deep bidirectional transformers for language understanding,” 2018,
arXiv:1810.04805.
[42] Y. Liu et al., “RoBERTa: A robustly optimized BERT pretraining
approach,” 2019, arXiv:1907.11692.
[43] T. B. Brown et al., “Language models are few-shot learners,” in Proc.
NIPS, 2020, pp. 1877–1901.
[44] M. Chen et al., “Generative pretraining from pixels,” in Proc. Int. Conf.
Mach. Learn., 2020, pp. 1691–1703.
[45] A. Dosovitskiy et al., “An image is worth 16×16 words: Transformers
for image recognition at scale,” 2020, arXiv:2010.11929.
[46] H. Bao, L. Dong, S. Piao, and F. Wei, “BEiT: BERT pre-training of
image transformers,” 2021, arXiv:2106.08254.
[47] A. Ramesh et al., “Zero-shot text-to-image generation,” in Proc. Int.
Conf. Mach. Learn. (ICML), Jul. 2021, pp. 8821–8831.
[48] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 16000–16009.
[49] Z. Xie et al., “SimMIM: A simple framework for masked image
modeling,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2022, pp. 9653–9663.
[50] D. E. Rumelhart and J. L. McClelland, Parallel Distributed Processing:
Explorations in the Microstructure of Cognition, vol. 1. Cambridge, MA,
USA: MIT Press, 1986.
[51] G. E. Hinton, A. Krizhevsky, and S. D. Wang, “Transforming autoencoders,” in Proc. 21st Int. Conf. Artif. Neural Netw. Artif. Neural Netw.
Mach. Learn. (ICANN), Espoo, Finland, Jun. 2011, pp. 44–51.
[52] P. Baldi, “Autoencoders, unsupervised learning, and deep architectures,”
in Proc. ICML Workshop Unsupervised Transf. Learn., 2012, pp. 37–49.
[53] D. Bank, N. Koenigstein, and R. Giryes, “Autoencoders,” in Machine
Learning for Data Science Handbook: Data Mining and Knowledge
Discovery Handbook. Cham, Switzerland: Springer, 2023, pp. 353–374.
[54] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.
[55] D. Hendrycks and T. Dietterich, “Benchmarking neural network
robustness to common corruptions and perturbations,” 2019,
arXiv:1903.12261.
[56] A. Dosovitskiy et al., “An image is worth 16×16 words: Transformers
for image recognition at scale,” in Proc. Int. Conf. Learn. Represent.,
2021, pp. 1–21.
[57] N. Dalal and B. Triggs, “Histograms of oriented gradients for human
detection,” in Proc. IEEE Comput. Soc. Conf. Comput. Vis. Pattern
Recognit. (CVPR), San Diego, CA, USA, Jun. 2005, pp. 886–893.

2529914

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

[58] N. Dalal, B. Triggs, and C. Schmid, “Human detection using oriented
histograms of flow and appearance,” in Proc. Eur. Conf. Comput. Vis.
Cham, Switzerland: Springer, 2006, pp. 428–441.
[59] C. Wei, H. Fan, S. Xie, C.-Y. Wu, A. Yuille, and C. Feichtenhofer,
“Masked feature prediction for self-supervised visual pre-training,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2022, pp. 14668–14678.
[60] G. Hinton, O. Vinyals, and J. Dean, “Distilling the knowledge in a neural
network,” 2015, arXiv:1503.02531.
[61] J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei, “ImageNet:
A large-scale hierarchical image database,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit., Jun. 2009, pp. 248–255.
[62] A. Mousakhan, T. Brox, and J. Tayyub, “Anomaly detection with
conditioned denoising diffusion models,” 2023, arXiv:2305.15956.
[63] T. D. Tien et al., “Revisiting reverse distillation for anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2023, pp. 24511–24520.
[64] H. Yao, M. Liu, Z. Yin, Z. Yan, X. Hong, and W. Zuo, “GLAD: Towards
better reconstruction with global and local adaptive diffusion models
for unsupervised anomaly detection,” in Proc. Eur. Conf. Comput. Vis.
Cham, Switzerland: Springer, Oct. 2024, pp. 1–17.
[65] F. Tung and G. Mori, “Similarity-preserving knowledge distillation,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1365–1374.
[66] T.-Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, “Focal loss for
dense object detection,” in Proc. IEEE Int. Conf. Comput. Vis. (ICCV),
Oct. 2017, pp. 2980–2988.
[67] T. Saito and M. Rehmsmeier, “The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced
datasets,” PLoS ONE, vol. 10, no. 3, Mar. 2015, Art. no. e0118432.
[68] M. Everingham, L. Van Gool, C. K. I. Williams, J. Winn, and
A. Zisserman, “The Pascal visual object classes (VOC) challenge,” Int.
J. Comput. Vis., vol. 88, no. 2, pp. 303–338, 2010.
[69] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Uninformed
students: Student–teacher anomaly detection with discriminative latent
embeddings,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2020, pp. 4183–4192.
[70] K. He, X. Zhang, S. Ren, and J. Sun, “Delving deep into rectifiers:
Surpassing human-level performance on ImageNet classification,” in
Proc. IEEE Int. Conf. Comput. Vis. (ICCV), Dec. 2015, pp. 1026–1034.
[71] L.-C. Chen, G. Papandreou, I. Kokkinos, K. Murphy, and A. L. Yuille,
“DeepLab: Semantic image segmentation with deep convolutional nets,
atrous convolution, and fully connected CRFs,” IEEE Trans. Pattern
Anal. Mach. Intell., vol. 40, no. 4, pp. 834–848, Apr. 2017.
[72] S. Zagoruyko and N. Komodakis, “Wide residual networks,” 2016,
arXiv:1605.07146.
[73] T. Hu et al., “AnomalyDiffusion: Few-shot anomaly image generation with diffusion model,” in Proc. AAAI, vol. 38, Mar. 2024,
pp. 8526–8534.
[74] X. Zhang, M. Xu, and X. Zhou, “RealNet: A feature selection network with realistic synthetic anomaly for anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2024,
pp. 16699–16708.

Jichun Wang received the B.E. degree in
mechanical engineering from Zhejiang University,
Hangzhou, China, in 2019, where he is currently
pursuing the Ph.D. degree with the School of
Mechanical Engineering.
His research interests include robotic vision, image
understanding, and human–robot interaction.

Zheyuan Zhou (Student Member, IEEE) received
the B.E. degree in computer science from Zhejiang University of Technology, Hangzhou, China,
in 2020, and the M.S. degree in computer science
from Fudan University, Shanghai, China, in 2023.
He is currently pursuing the Ph.D. degree with the
School of Mechanical Engineering, Zhejiang University, Hangzhou.
His research interests include intelligent manufacturing, computer vision, and deep learning.

Shuyou Zhang is currently a Distinguished Professor and a Ph.D. Supervisor with the School
of Mechanical Engineering, Zhejiang University,
Hangzhou, China. His research interests include
computer graphics, computer vision, and product
digital design.

Zian Yu received the B.E. degree from the College
of Mechanical and Electrical Engineering, Beijing
University of Chemical Technology, Beijing, China,
in 2021. He is currently pursuing the Ph.D. degree
with the School of Mechanical Engineering, Zhejiang University, Hangzhou, China.
His research interests include industrial defect
detection and computer vision.

Zili Wang (Member, IEEE) received the Ph.D.
degree from the School of Mechanical Engineering,
Zhejiang University, Hangzhou, China, in 2018.
He is currently an Associate Professor with the
School of Mechanical Engineering, Zhejiang University. His research interests include intelligent
manufacturing, computer-aided design, and computer graphics.

Xiaojian Liu received the Ph.D. degree from the
School of Mechanical Engineering, Zhejiang University, Hangzhou, China, in 2011.
He is currently an Associate Professor at the
School of Mechanical Engineering, Zhejiang University. His research interests include intelligent
manufacturing, computer-aided design and computer
vision.

Lemiao Qiu (Member, IEEE) received the Ph.D.
degree from the School of Mechanical Engineering,
Zhejiang University, Hangzhou, China, in 2008.
He is currently a Professor with the School of
Mechanical Engineering, Zhejiang University. His
research interests include production informatization, computer graphics, and computer vision.
PAPER_TEXT
