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
# [304] Sliding Dual-Window-Inspired Reconstruction Network for Hyperspectral Anomaly Detection
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
编号：304
题名：Sliding Dual-Window-Inspired Reconstruction Network for Hyperspectral Anomaly Detection
年份：2024
DOI：10.1109/tgrs.2024.3351179
来源：IEEE Transactions on Geoscience and Remote Sensing
PDF：paper/10.1109_TGRS.2024.3351179.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\304.txt
- 原始字符数：79339
- 本次发送字符数：79339
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 62, 2024

5504115

Sliding Dual-Window-Inspired Reconstruction
Network for Hyperspectral Anomaly Detection
Degang Wang , Lina Zhuang , Member, IEEE, Lianru Gao , Senior Member, IEEE, Xu Sun , Member, IEEE,
Xiaobin Zhao , and Antonio Plaza , Fellow, IEEE
Abstract— Hyperspectral anomaly detection (HAD) aims to
identify anomalous objects that deviate from surrounding backgrounds in an unlabeled hyperspectral image (HSI). Most available neural networks that make use of the reconstruction error
to perform HAD tend to fit both backgrounds and anomalies,
resulting in small reconstruction errors for both and not being
effective in separating targets from background. To address this
issue, we develop Dual-window-inspired reconstruction Network
(DirectNet), a new background reconstruction network for HAD
that seamlessly integrates a sliding dual-window model into a
blind-block architecture. Concretely, DirectNet establishes an
inner window within the network’s receptive field by erasing the
center block information so that the content of the inner window
remains invisible during the reconstruction of the central pixel.
In addition, the depth of our reconstruction network is adaptive
to the size of the input image patch, ensuring that the network’s
receptive field aligns with the dimensions of the input patch. The
receptive field outside the inner window is considered an outer
window. This weakens the impact of anomalies on the reconstruction process, causing the reconstructed pixels to converge
toward the background distribution in the outer window region.
Consequently, the reconstructed HSI can be regarded as a pure
background HSI, leading to further amplification of reconstruction errors for anomalous targets. This enhancement improves the
discriminatory ability of DirectNet. Specifically, DirectNet solely
utilizes the outer window information to predict/reconstruct the
central pixel. As a result, when reconstructing pixels inside
anomalous targets of different sizes, the targets primarily fall
within the inner window. Comprehensive experiments (conducted
on four datasets) demonstrate that DirectNet achieves competitive
performance compared to other state-of-the-art detectors.
Index Terms— Blind-spot network, convolutional neural networks (CNNs), deep learning (DL), hyperspectral images (HSIs),
image reconstruction, self-supervised learning.
Manuscript received 23 August 2023; revised 2 November 2023;
accepted 20 November 2023. Date of publication 15 January 2024; date of
current version 19 January 2024. This work was supported in part by the
National Natural Science Foundation of China under Grant 42325104 and
Grant 62161160336, and in part by the Spanish Ministerio de Ciencia e
Innovación under Project PID2019-110315RB-I00 (APRISA). (Corresponding
author: Lina Zhuang.)
Degang Wang is with the Key Laboratory of Computational Optical Imaging
Technology, Aerospace Information Research Institute, Chinese Academy of
Sciences, Beijing 100094, China, and also with the College of Resources and
Environment, University of Chinese Academy of Sciences, Beijing 100049,
China (e-mail: wangdegang20@mails.ucas.ac.cn).
Lina Zhuang, Lianru Gao, and Xu Sun are with the Key Laboratory of
Computational Optical Imaging Technology, Aerospace Information Research
Institute, Chinese Academy of Sciences, Beijing 100094, China (e-mail:
zhuangln@aircas.ac.cn; gaolr@aircas.ac.cn; sunxu@aircas.ac.cn).
Xiaobin Zhao is with the Beijing Key Laboratory of Fractional Signals
and Systems, School of Information and Electronics, Beijing Institute of
Technology, Beijing 100081, China (e-mail: xiaobinzhao@bit.edu.cn).
Antonio Plaza is with the Hyperspectral Computing Laboratory, Department
of Technology of Computers and Communications, Escuela Politécnica,
University of Extremadura, 10003 Cáceres, Spain (e-mail: aplaza@unex.es).
Digital Object Identifier 10.1109/TGRS.2024.3351179

I. I NTRODUCTION

H

YPERSPECTRAL images (HSIs) can discriminate the
fine spectral features of different ground materials [1],
[2], and this property enables these images to be applied
for detecting and locating objects of interest [3], [4]. Among
many different HSI interpretation tasks, hyperspectral anomaly
detection (HAD) is extensively utilized in both military and
civilian applications by virtue of its ability to identify anomalous targets with no prior information [5], [6]. The anomalies
are commonly defined as objects that occupy an extremely
small area and deviate from the overall pattern of their
surrounding background as well [7], [8]. The absence of
prior knowledge about targets and background in the HAD
task poses a critical challenge to separate anomalies from
background and numerous detectors model such background
through diverse approaches, where those samples not conforming to the background pattern are defined as anomalies.
The mainstream existing methods are classified into three
categories: statistical modeling-based, representation learningbased, and deep learning (DL)-based approaches.
A. Statistical Modeling-Based Methods
As the baseline of the statistical-based methods, the
Reed–Xiaoli (RX) detector assumes that the background of an
HSI obeys a multivariate Gaussian distribution and typically
estimates the background using the global information of the
image [9]. Those pixels with a large Mahalanobis distance
from the estimated background have more potential to be
considered as anomalies in a way that can be viewed as a
global RX (GRX) detector. In order to alleviate the anomalous
contamination during the process of background modeling, the
local RX (LRX) [10] uses a sliding dual-window strategy.
Here, the outer window pixels are analyzed to estimate the
background, while the inner window avoids the leakage of
target information. The weighted RX [11] method boosts the
detection performance of the model by endowing the potential
background with a high weight. To enhance the separability
of anomalies from backgrounds, Kwon and Nasrabadi [12]
adopted a kernel trick into the RX detector, and Tao et al. [13]
introduced the fractional Fourier transform [14] into the HAD
task. Subsequently, Li et al. [15] proposed the sliding dualwindow-based 2S-GLRT method to locate multipixel anomalous targets of the HSI. Vincent et al. [16] modified the RX
scheme by adopting the replacement model as a more realistic
anomaly detection framework. Yang et al. [17] combined the
detection results of different features on a random RX detector

1558-0644 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

5504115

with the aid of ensemble learning to leverage the multiple
characteristics in HSI.
B. Representation Learning-Based Methods
Since then, representation learning (encompassing sparse
representation (SR) [18], [19], [20], [21], collaborative representation (CR) [22], and low-rank representation (LRR) [23],
[24], [25]) has attracted extensive attention [26], [27],
[28]. Among them, SR-based studies emphasize that normal/background samples can be represented by only a few
atoms in an overcomplete dictionary, while anomalous ones
cannot [29]. CR-based detectors [30], in contrast, focus on
the collaborative relationships among all dictionary atoms
and thus analyze whether each sample can be linearly represented by its surrounding neighbors. Both of them take
reconstruction residuals to indicate the degree of anomaly
of the testing pixels. To acquire more accurate detection
results, many variants of CRD have been presented [22], [31].
Examining the global structural information of HSIs from
the perspective of LRR, an HSI can be decomposed into
background (with low-rank properties) and anomalies (with
sparse properties) [32], [33]. Zhang et al. [34] employed the
Mahalanobis distance between the pixels to be measured and
the low-rank matrix to detect anomalies in the HSI, while
Li et al. [35] introduced the Manhattan distance to recognize
anomalies and represented the sparse matrix by utilizing a
mixture of Gaussian noise models. In addition, LRR-based
methods have emerged with diverse background dictionary
constructions for better representation of HSIs, such as the
works by Xu et al. [36] and Fu et al. [37], who obtained
the background dictionary by leveraging K -means clustering, while Qu et al. [38] performed mean-shift clustering in
the abundance matrix and separated anomalous pixels from
the constructed dictionary. Given the spatial correlation of
neighboring pixels, the total variation technique (which allows
dictionary atoms to represent the background more efficiently)
was introduced into LRR-based approaches [39]. Besides, HSI
can be directly treated as a third-order tensor, and taking into
account the use of both spatial and spectral information of
HSI, He et al. [40] recently proposed a novel tensor low-rank
approximation method for performing HAD.
C. DL-Based Methods
In recent years, DL has emerged as a successful approach
in HSI processing, including the HAD task, by virtue of its
powerful capabilities for mining deep characteristics [41], [42],
[43]. The prevailing DL-based HAD methods can be categorized as similarity measurement models and reconstruction
models.
Similarity measurement models commonly incorporate a
convolutional neural network (CNN) [44] as the backbone,
and a vast number of training pixel pairs are selected in
advance from the labeled HSIs. The paired pixels from the
same category are labeled as 0, while the pixels paired from
different categories are labeled as 1. This value means the
dissimilarity between the two. This property empowers the
backbone network to measure the similarity of the input

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 62, 2024

paired pixels, which is then transferred into the HAD task
for identifying those anomalous pixels that are significantly
different from their surroundings. Li et al. [45] considered
the difference between the pixel pairs as the input, causing
the constructed single-stream CNN to directly output the
difference scores between the tested pixel and outer window
pixels. Unlike this, Rao et al. [46] devised a Siamese network
with feature extraction and similarity measurement abilities
and took the original pixel pairs as the input to explore the
similarity between each pixel and the surrounding ground
objects at the latent layer. However, the detection efficiency
of this family of methods is reliant on the quantity of paired
data and the quality of labels, and transferability cannot be
fundamentally guaranteed.
Conversely, reconstruction model-based methods have
demonstrated their effectiveness and adaptability in the unsupervised HAD task, due to the fact that they directly apply
unlabeled HSIs to be detected as training data and mine the
intrinsic abstract features in unsupervised learning fashion.
This category of methods primarily applies autoencoders [AEs
or generative adversarial networks (GANs)] to reconstruct
the raw data and employs the reconstruction error to obtain
the final anomaly detection result. Since background pixels
occupy the overwhelming majority of the HSI, the model
could fully learn the background characteristics and emerge
as a well-behaved background reconstructor. The proportion
of anomalies is quite low, rendering the model to generate
large reconstruction errors for them. Bati et al. [47] introduced
AEs to the HAD task with a first attempt to reconstruct all
samples in the detected image. To exploit the spatial features
of HSIs in a reasonable way, Xiang et al. [48] introduced a
guided model in the hidden layer of the AE to strengthen
the network’s power to represent the background, while
Fan et al. [49] imposed a graph regularization constraint on
the hidden features of the AE to enhance the robustness of the
model in reconstructing background samples. Wang et al. [50]
implemented an automatic end-to-end HAD, with the aid of a
fully convolutional AE. Furthermore, unlike the traditional AE,
the memory AE (with an external memory module recording
latent representations of background samples) was introduced
into HAD in [51], [52]. In order to inspire AEs to represent
the background more prominently, several efforts have been
dedicated to embedding discriminators into AEs (forming
GANs) by also imposing Gaussian constraints on them [53] or
performing background screening on the training samples in
advance [54], [55]. All these strategies can further increase the
reconstruction error for anomalies. Very recently, Li et al. [56]
integrated spatial and spectral characteristics via a two-stream
convolutional AE architecture, with a parameter-free clustering
approach chosen to select background samples.
D. Motivation and Contributions
Among the DL-based HAD methods described above, similarity measurement models tend to involve a complicated
training sample generation process, and the model’s generalizability is relatively limited. Meanwhile, most reconstruction
models take the input HSI as the learned target, which is prone

WANG et al.: SLIDING DUAL-WINDOW-INSPIRED RECONSTRUCTION NETWORK FOR HAD

Fig. 1. Blind-spot reconstruction network has a blind area in the receptive
field corresponding to a single central pixel (i.e., the white area invisible
to the network/eye). Therefore, the network has to predict/reconstruct the
central pixel (represented by a red rectangle) using only the surrounding pixels
(the blue area seen by the eye). (a) Original blind-spot network contains
a blind spot in the center of the receptive field. Here, the reconstruction
of anomalous pixels is interfered with by neighboring pixels that are also
anomalous, ultimately leading to undesirable results in relatively large-sized
targets. (b) Our proposed DirectNet improves the original blind-spot network
by conceiving a dual-window blind-block reconstruction model. Specifically,
the original receptive field of DirectNet is divided into a dual window, where
the blind-block area is considered the inner window (represented by a green
dashed rectangle) and the receptive field outside the inner window (represented
by a magenta dashed rectangle) is regarded as the outer window. Fortunately,
DirectNet possesses promising detection performance for both large- and
small-sized targets, thus extending the application range of blind-spot models.

to lead to the identity mapping being learned [57], [58], i.e.,
parts of the anomalies will inevitably appear in the reconstructed HSI, although it is expected that the model serves
as a pure background reconstructor. Therefore, the obtained
results manifested by the reconstruction errors make it difficult
to separate anomalies from the background, resulting in a
degradation of the model performance.
To address the aforementioned issues, we opted to perform HAD using a self-supervised learning technique. Selfsupervised learning is similar to unsupervised learning in that
only unlabeled HSIs are required, yet it generates supervision signals from the raw data for network training [59],
[60]. Nowadays, self-supervised learning has proven to be
effective in diverse topics related to HSI processing, such
as denoising [61], fusion [62], [63], spectral unmixing [64],
and classification [65]. More recently, the blind-spot network [66] (as a representative of self-supervised learning)
has been introduced to HAD for accurately identifying smallsized subpixel anomalous targets in HSIs [67]. However, this
technique is unable to detect large-sized targets effectively in
a direct way. To explain the challenge of detecting large-sized
targets using the original blind-spot network, a toy example
is given in Fig. 1. We emphasize that the original blindspot network possesses a special receptive field centered on a
blind spot, implying that the network fails to see the spectral
information of the receptive field’s central pixel. Hence, the
network’s prediction value for the blind spot depends only
on its neighboring pixels, excluding its own information and
avoiding identity mapping [68]. When the central pixel is
an anomaly (i.e., significantly different from its surrounding

5504115

pixels), the blind-spot network will not predict/reconstruct the
central one adequately, leading to an increased reconstruction
error and a high anomaly score. Accordingly, the architecture
of blind-spot networks is well-suited to perform the HAD
task. Nevertheless, as it can be seen in Fig. 1(a), the original
blind-spot network does not succeed in recognizing large-sized
anomaly targets. This is because the network is influenced by
the neighboring pixels containing the target’s spectral information when predicting the central anomalous pixel, which causes
large-sized anomalies to exhibit low reconstruction errors and
low anomaly scores.
To tackle this challenge, we conceive a sliding dualwindow-inspired reconstruction network for HAD in a selfsupervised manner. As shown in Fig. 1(b), our network divides
the original receptive field into a dual window, where only the
outer window pixels are exploited to predict the central pixel,
while the inner window works as a guard window against
potential contaminating effects coming from anomalous pixels. When the central anomalous sample is reconstructed,
sparsely distributed and small-occupancy targets with a certain
spatial size tend to lie in the inner window, whereas the
network will be unable to see the inner window information, so that no anomalous properties are learned. Those
backgrounds with large scales and homogeneous properties
always remain located in the outer window, which impels
the samples predicted by the network to converge to the
surrounding background distribution, resulting in an increase
in the reconstruction error of anomalies. Specifically, first,
training patch pairs are constructed from the unlabeled part
of the observed HSI. Then, the designed background reconstruction model cannot see the center block of the receptive
field (inner window) and has to predict/reconstruct the central
pixel using only the receptive field area outside the center
block (outer window), which is in accordance with the idea of
the dual-window model, weakening the ability to fit anomalous features. Finally, the trained network turns out to be a
superb background reconstructor, and the reconstruction error
is employed to reflect the degree of anomaly of each pixel.
Compared with existing HAD methods, the core contributions
of our proposed sliding Dual-window-inspired reconstruction
Network (DirectNet) are summarized as threefold.
1) We propose a novel blind-block architecture-based
network for HAD purposes, which operates in a
fully self-supervised learning manner, i.e., generating training pairs from an unlabeled observed HSI,
leading to impressive detection performance (surpassing that achieved by unsupervised reconstruction
models).
2) To fully leverage the spatial–spectral features of an HSI,
we propose an adaptive depth reconstruction network.
This network adjusts its depth according to the size
of the input image patch, ensuring that the network’s
receptive field aligns with the dimensions of the input
patch.
3) To address the limitations of blind-spot networks in
handling large-size targets, we propose a novel dualwindow-inspired blind-block network. Unlike traditional
blind-spot networks that focus on one-pixel blind spots,

5504115

Fig. 2.

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 62, 2024

Flowchart of the proposed DirectNet.

our approach considers a large-size block as the blind
area of the receptive field. We erase the center block
information of the image patch, meaning that the network is unable to see this information when reconstructing the central pixel. The blind center block serves as
an inner window, which prevents large-sized anomalies
located in the inner window from influencing the reconstruction of the central pixel. Simultaneously, the regions
of the receptive field outside the center block are considered the outer window. By leveraging the surrounding
outer window pixels, our network predicts/reconstructs
the central pixel. This design forces the network to rely
on the outer window information, leading to significant reconstruction errors for anomalous targets. Consequently, our DirectNet shows promising potential in
recognizing both large- and small-sized targets, thus
expanding the application scope of original blind-spot
networks.
The rest of this article is organized as follows. We give the
details of the proposed DirectNet in Section II. In Section III,
comprehensive experimental results between DirectNet and
state-of-the-art detectors are discussed. Finally, the conclusion
is summarized in Section V.
II. P ROPOSED A NOMALY D ETECTOR : DirectNet
We designed a background reconstruction network inspired
by a sliding dual-window model, called DirectNet, whose
overall flowchart is shown in Fig. 2. More specifically, DirectNet can be divided into two stages.
1) Training Phase: First, pairs of input and pseudo-labeled
data (in the form of patches) are obtained from the
observed HSI, and then, they are fed into the background

reconstruction network. Finally, a masking scheme is
devised to modify the self-supervised objective function. (The mask here is different from the mainstream
definition, as described in [69]. Instead of representing
the occluded regions during training, it refers to the
portions that are not utilized in the calculation of the
loss function.) The above process forces the network
not to see the information of the center block of the
receptive field (inner window), but instead to reconstruct
the central pixel using the remaining receptive field
(outer window).
2) Detection Phase: The whole observed HSI is fed into
the well-trained DirectNet to estimate the expected pure
background HSI, and the reconstruction error is treated
as the final detection result. Next, we fully detail each
part of DirectNet.
A. Problem Formulation
R×C
Let us consider an HSI as X = {xi ∈ R L×1 }i=1
, where
R, C, and L, respectively, represent the row number, column
number, and band/channel number of X, and xi denotes the
ith spectral vector pixel of size L. The proposed DirectNet
is expected to be a superior background reconstructor using
a self-supervised strategy, i.e., only using the observed HSI
X without any labeled background and anomaly information,
to well-identify the anomalous targets. Furthermore, DirectNet
divides its own receptive field into a dual window, which is
illustrated in Fig. 3. The pixel information lying in the inner
window is invisible to the network when reconstructing the
central pixel. Our DirectNet empowers the feature expression
of the background, generating a small reconstruction error for
backgrounds and a large reconstruction error for anomalies.

WANG et al.: SLIDING DUAL-WINDOW-INSPIRED RECONSTRUCTION NETWORK FOR HAD

Fig. 3. Illustration of the dual window provided by our DirectNet. Note that
only the outer window pixels are employed to predict the central pixel.

Therefore, the reconstruction error showcases the degree of
anomaly for each pixel naturally, facilitating the recognition
of anomalous targets in HSIs.
B. Training Phase
Here, we introduce the training phase of DirectNet, i.e.,
the generation of training patch pairs as well as the specific
structure.
Let poi ∈ RWout ×Wout ×L denote a patch centered at pixel xi ,
where Wout is the width of the patch (usually an odd number).
R×C
Symbol Po = {poi }i=1
denotes the patches extracted from
the HSI. In order to keep the network from seeing the pixels
in the center block (denoted as pci ∈ RWin ×Win ×L ) of poi ,
we erase the spectral information covering the corresponding
center block. It is implemented by randomly picking Win ×Win
pixels from the region excluding pci to replace all pixels
R×C
of pci , with the purpose of forming Pr = {pri }i=1
, where
Wout ×Wout ×L
pri ∈ R
is the ith patch that removes the information
of pci . Indeed, Pr and Po are considered as the input data and
learned target of DirectNet. A tailored masking strategy will
be subsequently devised to allow the network to concentrate
its efforts on reconstructing the central pixel of each patch.
The above procedure creates an inner window (guard window)
of size Win × Win for the corresponding receptive field of the
network during the prediction of the central pixel, enabling the
need to avoid the pixels located in the inner window whenever
the central pixel is reconstructed. In the case of reconstructing
anomalous pixels, targets of a certain spatial size normally
fall in the inner window, which lessens the contribution of
anomalous information. This is unlike the original blind-spot
network, as the setting of the inner window endows our
DirectNet with the ability to detect targets of different sizes.
Next, a ResNet block-based background reconstruction network (whose receptive field is adaptively matched to the
training patch size) is designed. The number of network layers,
i.e., the number of adopted ResNet blocks, is automatically
derived from the patch size, avoiding manually configured
parameters. Since the size of the network’s receptive field and
patch aligned well, this ensures that the reconstruction of the
central pixel will exploit all the spatial–spectral information
of the patch. Nevertheless, owing to the setting of the inner
window (meaning that the network is unable to see this area),
the pixels actually devoted to the reconstruction come from

5504115

only the contents of the patch lying outside the inner window.
Clearly, the receptive field of the network for reconstructing
the central pixel is partitioned into a dual window, where the
inner window is of size Win × Win and the outer window is
of size Wout × Wout (with the same spatial size as the training
patch), and when the network reconstructs the central pixel,
it only utilizes the surrounding pixels in the outer window.
Concretely, the detailed network structure is presented in
Fig. 4, where the convolution kernel size of all convolution
layers is 3 × 3. The first convolution layer is followed by the
Rectified Linear Unit (ReLU) function, and the penultimate
convolution layer is followed by a batch normalization layer.
We applied Nr ResNet blocks, where Nr = (Wout −7)/4 that is
derived from the network’s receptive field. For example, when
the outer window size is 15×15 (i.e., Wout is 15), our DirectNet
contains two ResNet blocks. In the ResNet block, there are two
convolution layers both followed by the batch normalization
layer, and the first layer also takes the ReLU function. The
pixel-level summation (the same as given next) is performed
on the output and input feature maps to realize skip connections. Meanwhile, to fuse the beginning low-level visual with
high-level semantic features, the feature maps obtained from
the first and penultimate convolution layers are summed and
fed into the last convolution layer. We denote the proposed
background reconstruction model as Fr , parameterized by θ.
Then, Pr is input into Fr to get the output, i.e.,
Pb = Fr (Pr ; θ )
R×C
where Pb = {pbi }i=1

Wout ×Wout ×L

(1)

and pbi ∈ R
indicates the
patch corresponding to pri , in which L is the number of
convolution channels in the last layer, which is equal to the
number of bands of X.
Given that Po is the supervision information for Pr , the
optimization goal of the proposed DirectNet is to make Pb
(excluding the center block information) converge to Po .
In particular, DirectNet only exploits the contents within the
outer window of Po to reconstruct the corresponding central
pixel, which inspires us to impose a mask-learning scheme to
enable Fr to specialize in reconstructing/predicting the central
pixel of the patch, serving the dual-window model construction. More specifically, we additionally applied a binary mask
to Pb and Po to obtain Pbm and Pom (see Fig. 2), aiming
to only calculate the loss at the central pixel position during
backpropagation. By now, only the outer window pixels of the
receptive field are available for DirectNet to reconstruct the
central pixel, in which the homogeneous background would
commonly be located inside the outer window, impelling the
background samples to be reconstructed successfully. Meanwhile, it induces that each pixel reconstructed by DirectNet
will satisfy the background distribution of the outer window,
weakening the model’s power to fit anomalous targets, and
motivating its promise to be a well-performing background
reconstructor.
Our DirectNet Fr (·; θ ) is trained using an ℓ1 loss-based
objective function as follows:
θ̂ = arg min Lsel f
θ

= arg min∥Fr (Pr ; θ) ⊙ M − Po ⊙ M∥1
θ

5504115

Fig. 4.

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 62, 2024

Details of the proposed overall network structure (the numbers above Conv, such as 64, represent the number of output channels).

= arg min∥Pb ⊙ M − Po ⊙ M∥1

Algorithm 1 DirectNet

θ

= arg min∥Pbm − Pom ∥1
θ

(2)

R×C
where M = {mi }i=1
represents the patches of binary mask,
Wout ×Wout ×L
is the mask corresponding to pbi and
mi ∈ {0, 1}
poi (see Fig. 2), the position of the one in mi denotes the
position of the central pixel, and the rest of the elements
are all zeros. Symbol ⊙ denotes elementwise multiplication.
Here, for better generalization, we adopt the ℓ1 loss instead
of the typical ℓ2 loss that is more attentive to larger errors
but less sensitive to smaller ones [70]. This ℓ1 norm loss
function is based on the mean absolute error, which requires
calculating the absolute value of the difference between the
output predicted data and the supervision information, and
its gradient descent process is based on the adaptive moment
estimation (Adam) stochastic optimization algorithm [71] that
comes with the PyTorch framework.

C. Detection Phase
In the detection phase, the observed HSI X is fed into the
well-trained DirectNet, parameterized by θ̂, to acquire the final
b = {x̂i ∈ R L×1 } R×C ), i.e.,
reconstructed image (denoted as X
i=1
b = Fr (X; θ̂).
X

(3)

After the aforementioned self-supervised training procedure,
the proposed DirectNet behaves as an efficient background
b becomes a pure
reconstruction model; thus, the output X
background image, and naturally, anomalies have larger reconstruction errors compared to backgrounds. Finally, the reconstruction error is recognized as a detection result as follows:
Di = xi − x̂i 2

(4)

b respectively,
where xi and x̂i denote the ith pixels of X and X,
and Di stands for the abnormal response value of the ith
R×C
pixel and constitutes the final HAD map D = {Di }i=1
.
This ℓ2 norm reconstruction error is based on the mean
square error, which requires calculating the square value of the
difference between the output predicted data and the original
one. The key steps of the proposed DirectNet are summarized
in Algorithm 1.
III. E XPERIMENTAL R ESULTS
In this section, the superior performance of the proposed
DirectNet is validated qualitatively and quantitatively through
extensive experiments.

R×C
Input: Observed HSI X = {xi ∈ R L×1 }i=1
;
Parameters: 1) width of inner window Win , 2)
width of outer window Wout .
R×C
Output: Final detection result D = {Di }i=1
.
1 Stage 1: Training Phase;
2 for i = 1 : N (N = R × C) do
3
Construct patch poi ∈ RWout ×Wout ×L centered at pixel
xi ;
4
Replace all pixels in the center block
pci ∈ RWin ×Win ×L of poi with Win × Win pixels
randomly selected from the region outside of pci ;
5
Get the patch pri ∈ RWout ×Wout ×L that removes the
information of pci ;
6 end
R×C
R×C
7 Obtain pairs of Pr = {pri }i=1 and Po = {poi }i=1 as
input data and learned target for network training,
respectively;
8 for i = 1 : N do
9
Train a reconstruction network Fr with
Nr = (Wout − 7)/4 ResNet blocks by minimizing
loss function Eq. (2);
10 end
11 Obtain a well-trained network Fr , parameterized by θ̂;
12 Stage 2: Detection phase;
13 Acquire a reconstructed HSI by feeding X into the
b = Fr (X; θ̂ );
well-trained DirectNet, i.e., X
14 Calculate the degree of anomaly Di of each pixel in X
by Eq. (4);

A. Datasets
1) Salinas Dataset: This is a synthetic image collected by
the Airborne Visible Infrared Imaging Spectrometer (AVIRIS)
covering the Salinas valley [72], and we adopted the anomaly
target implantation approach of [73], which follows a linear
mixing model [74], [75], [76], i.e., n = f a a + (1 − f a )b,
where a, b, n ∈ R L×1 are spectral vectors of the anomaly,
background, and final mixture of the two, respectively, and
f a denotes the nonnegative abundance fraction of a. The
16 anomalous objects (buildings) with a spatial size of 3 × 3
were randomly embedded into this sub-HSI, and the abundance fraction of a for these targets begins at 0.05 and
increases by 0.04 in turn.
2) Pavia Dataset: It was captured by the Reflective Optics
System Spectrographic Imaging System (ROSIS-03) sensor

WANG et al.: SLIDING DUAL-WINDOW-INSPIRED RECONSTRUCTION NETWORK FOR HAD

Fig. 5. Pseudocolor images and ground truth maps of the four considered
HSI datasets. (a) Salinas. (b) Pavia. (c) El Segundo. (d) Indiana.
TABLE I
D ETAILS OF THE E XPERIMENTAL DATASETS

over the city of Pavia [77]. There are several vehicles embedded in the bridge as anomalous targets.
3) El Segundo Dataset: It was collected by AVIRIS and
covered an urban scene in El Segundo city [78], in which the
anomalies mainly consist of storage tanks on the oil refinery.
4) Indiana Dataset: It was acquired from the Earth Observing One (EO-1) Hyperion sensor over the Indiana area [79],
and some storage bins and roofs of small size are considered
to be anomalies in this image.
Notably, the above four images contain both small- and
large-sized anomalous targets, and more detailed features of
these images are shown in Table I. In addition, the pseudocolor images and ground truth maps of targets are shown in
Fig. 5.

5504115

models to reconstruct backgrounds, and all adopt the residual
spectral error between the original and reconstructed HSIs to
measure the degree of anomaly of each pixel. This remains
in line with the motivation of our proposed DirectNet. Meanwhile, the blind-spot network architecture endows BS3 LNet
with the power to detect subpixel small-sized anomalies in
the HSI. Hence, the differences between the detection effect
of these five methods require to be involved in emphasizing the
effectiveness of coupled dual window with deep reconstruction
networks. For the proposed DirectNet, it is implemented
by PyTorch on a GeForce RTX 2080 Ti GPU with 11-GB
memory. The batch size and the learning rate were set to
100 and 1e−4 , respectively, for all datasets. The spatial sizes of
the input patches for the four datasets (namely, Salinas, Pavia,
El Segundo, and Indiana) were set to 15×15, 19×19, 19×19,
and 23 × 23, with the number of training epochs for the four
datasets set to 700, 1000, 700, and 950, respectively.
2) Evaluation Metrics: To evaluate the performance of the
different popular compared detectors, some well-known criteria are adopted, i.e., receiver operating characteristic (ROC),
the area under the ROC curve (AUC) [80], and the statistical
separability map. Among them, the ROC curve reveals the
relationship between the probability of detection and the false
alarm rate (FAR), revealing the detection accuracy of the
model in a holistic manner. The corresponding AUC value
can assess the detection accuracy quantitatively. An excellent
detector would carry an ROC curve in near proximity to the
upper left corner, with an AUC value near 1. Moreover, the
separability map provides the statistical range of the abnormal
response values at the pixel location of the background and
anomalous classes, and these values are distributed in two
separated boxes (blue for the background and red for the
anomaly), each with a statistical interval from 10% to 90%.
Clearly, if the detector demonstrates a predominant ability to
extrude anomalies and suppress backgrounds, the blue box will
be at the exact bottom and narrow width, with a big interval
from the red box.
C. Detection Performance for Different Methods

B. Comparison Algorithms and Evaluation Metrics
1) Comparison Algorithms: To assess the efficacy of the
proposed DirectNet, some well-established competitive methods selected for comparison embrace four statistical modelingbased methods (i.e., GRX [9], FrFE [13],1 LRX [10], and
2S-GLRT [15]2 ), two representation learning-based methods
(i.e., CRD [30] and LSDM-MoG [35]3 ), and four DL-based
methods (i.e., GAED [48],4 RGAE [49],5 Auto-AD [50],6
and BS3 LNet [67]). Among the above detectors, all based on
cutting-edge DL technology, GAED, RGAE, Auto-AD, and
BS3 LNet methods are designed to enhance the capacity of
1 https://github.com/xudongzhao461/Hyperspectral-Anomaly-Detection-byFractional-Fourier-Entropy
2 https://github.com/zephyrhours/Hyperspectral-Anomaly-Detection-2SGLRT
3 https://github.com/l7170/LSDM-MoG
4 https://github.com/pei-xiang/GAED
5 https://github.com/FGH00292/Hyperspectral-anomaly-detection-withRGAE
6 https://github.com/RSIDEA-WHU2020/Auto-AD

Figs. 6–9 visualize the HAD colored results obtained by the
11 considered methods on the four considered datasets, where
the first one in each figure is the ground truth of detected
anomalous targets, and the rest are the resulting maps for
different detectors. Also, Figs. 10 and 11 show the ROC curves
and separability boxplots of these 11 methods, whose AUC
scores are listed in Table II. Note that the best results are
marked in boldface (the same as given next).
Across the board, Figs. 6–9 show that the proposed DirectNet attains an acceptable tradeoff in anomaly detectability
and background suppressibility, and its corresponding detection maps are closest to the ground truth. Considering the
Salinas dataset as an example, GRX and FrFE do not work
satisfactorily because the shapes of 16 targets are barely
visible in the result maps. Although LSDM-MoG, GAED,
and RGAE perform relatively well in highlighting anomalies,
they maintain some background structural information and so
suffer from varying degrees of false alarms. LRX, 2S-GLRT,
CRD, Auto-AD, and BS3 LNet can restrain the background to

5504115

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 62, 2024

Fig. 6. HAD colored maps obtained by different algorithms for the Salinas dataset. (a) Ground truth. (b) GRX. (c) FrFE. (d) LRX. (e) 2S-GLRT. (f) CRD.
(g) LSDM-MoG. (h) GAED. (i) RGAE. (j) Auto-AD. (k) BS3 LNet. (l) DirectNet.

Fig. 7. HAD colored maps obtained by different algorithms for the Pavia dataset. (a) Ground truth. (b) GRX. (c) FrFE. (d) LRX. (e) 2S-GLRT. (f) CRD.
(g) LSDM-MoG. (h) GAED. (i) RGAE. (j) Auto-AD. (k) BS3 LNet. (l) DirectNet.

Fig. 8. HAD colored maps obtained by different algorithms for the El Segundo dataset. (a) Ground truth. (b) GRX. (c) FrFE. (d) LRX. (e) 2S-GLRT.
(f) CRD. (g) LSDM-MoG. (h) GAED. (i) RGAE. (j) Auto-AD. (k) BS3 LNet. (l) DirectNet.

a certain extent but cannot effectively highlight the anomalous
targets. Conversely, our DirectNet avoids the aforementioned
issues and can accurately identify the embedded pixels with
high abnormal response values and low false alarms.
Another example is the Pavia dataset. CRD, LSDM-MoG,
and RGAE can highlight these anomalous targets, yet they

outline the boundaries of backgrounds, making the distinction
between backgrounds and anomalies not clear. Although GRX,
FrFE, LRX, 2S-GLRT, GAED, and BS3 LNet can locate most
of the vehicles, they risk misjudging the background. AutoAD and DirectNet can suppress background interference to a
large degree, yet our DirectNet is more capable of enhancing

WANG et al.: SLIDING DUAL-WINDOW-INSPIRED RECONSTRUCTION NETWORK FOR HAD

5504115

Fig. 9. HAD colored maps obtained by different algorithms for the Indiana dataset. (a) Ground truth. (b) GRX. (c) FrFE. (d) LRX. (e) 2S-GLRT. (f) CRD.
(g) LSDM-MoG. (h) GAED. (i) RGAE. (j) Auto-AD. (k) BS3 LNet. (l) DirectNet.

Fig. 10.

ROC curves obtained by different detectors for the four considered datasets. (a) Salinas. (b) Pavia. (c) El Segundo. (d) Indiana.

Fig. 11.

Separability maps obtained by different detectors on the four considered datasets. (a) Salinas. (b) Pavia. (c) El Segundo. (d) Indiana.

anomalous characteristics compared to Auto-AD while yielding a lower FAR. Analogous results are displayed on the
other two datasets, and the above visualizations show that
DirectNet holds a better capacity for separating targets from
backgrounds. The main reason lies in the fact that the proposed
DirectNet couples the sliding dual-window model in a selfsupervised way, indicating promising performance in strengthening anomalous characteristics and restraining background
interference.
In addition, other metrics were operated to evaluate the
detection performance of different algorithms from qualitative
and quantitative views. In Fig. 10, overall, the red curve
of DirectNet lies mostly above the other colored curves
and generally exceeds the other detectors. Unsurprisingly,
compared with the other ten competing methods, DirectNet
achieves the highest AUC values on the first three datasets

and second place on the Indiana dataset. BS3 LNet, known for
its effectiveness in detecting small-sized subpixel anomalous
targets while excelling on the Indiana dataset, performs poorly
on the other three datasets with large-sized targets. To further
verify the strong background suppressibility and anomalous
target separability of DirectNet, Fig. 11 draws separability
boxplots of all detectors regarding backgrounds and anomalies.
On these four datasets, the red anomaly boxes of DirectNet
are normally not located at the highest place, but its blue background boxes are at a rock-bottom level and narrow enough,
implying that DirectNet is well qualified for restraining the
background. At the same time, on the Salinas and Indiana
datasets, DirectNet can ensure a larger gap between the two
boxes and swimmingly extract anomalies from the suppressed
backgrounds. Apparently, this accords with the visual analysis
effects described earlier.

5504115

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 62, 2024

TABLE II
AUC VALUES OF THE 11 C ONSIDERED D ETECTORS FOR D IFFERENT DATASETS

Fig. 12. AUC values of the proposed DirectNet with inner windows of different widths (Win ) and ResNet blocks of different numbers (Nr ) on the four
considered datasets. (a) Salinas. (b) Pavia. (c) El Segundo. (d) Indiana.

All told that, from the findings by visual inspection,
the proposed DirectNet presents remarkable visual results.
Besides, the comparison and analysis of the ROC curves, AUC
scores, and separability boxplots for different methods reveal
that DirectNet achieves the highest average AUC of 0.9927,
which is 0.0099 larger than that of the second-best Auto-AD,
as reported in Table II. In addition, the FAR of DirectNet
remains generally at a low value, further achieving a satisfactory balance between anomaly detectability and background
suppressibility, thus affirming the efficacy of DirectNet.
D. Parameter Analysis
The proposed DirectNet involves two parameters: the width
of the inner window Win and the number of ResNet blocks Nr
(whose setting is adaptive to the width of the outer window,
i.e., Wout = 4 × Nr + 7). It is noteworthy that the feasible
value of Win needs to be an odd number greater than 1. If Win
is equal to 1, then DirectNet degenerates into a blind-spot
network with a coupled single-window model. Among them,
the values of Win and Nr for all the datasets are set to {3, 5,
7, 9} and {2, 3, 4, 5} (i.e., Wout is set to {15, 19, 23, 27}),
respectively. Then, the AUC scores under different parameter
settings are summarized in Fig. 12.
It can be found from Fig. 12 that the detection accuracy
of DirectNet (coupled with dual-window of different sizes)
does not exhibit significant fluctuations on the Salinas dataset.
For the El Segundo dataset (with large-sized targets), Win
should be chosen as a larger value, and for datasets with
small-sized targets (such as Pavia and Indiana), the smaller
value should be selected for Win to further promote the
performance of DirectNet. As long as the inner window size
is selected appropriately, the outer window size (number of
ResNet blocks) brings little impact, manifesting the stability of
DirectNet in the task of detecting anomalous targets of diverse

sizes. For the four datasets containing targets of different
spatial sizes, the parameter Win is fixed to 5, 3, 9, and 3 as
the optimal setting.
E. Ablation Study
This section evaluates the contribution of each component
to the proposed DirectNet on all datasets. As a baseline,
we employ a traditional unsupervised learning-based reconstruction model (denoted as USLNet), which uses the same
framework as DirectNet, except for the fact that it trains the
background reconstruction network directly with the original
patches, without removing any information. By placing the
inner window in the center of the receptive field (meaning that
this information is not visible to the network) and the outer
window (corresponding to the receptive field area) outside
of the center block, our DirectNet couples a dual-window
model, which is well-suited for detecting anomalous targets
of different sizes. When there is no inner window (i.e., the
width of the inner window is 1), DirectNet degenerates into
a blind-spot network with a single-window model (denoted
as BaseNet). Meanwhile, we also compared the effect of
different types (i.e., ℓ1 and ℓ2 ) of reconstruction errors on
the detection performance. The details of AUC comparisons
on these datasets are shown in Table III.
As seen from Table III, BaseNet has some advantages over
the unsupervised learning-based method on most datasets,
especially for the Indiana dataset containing slightly smallsized targets, where BaseNet achieves an overwhelming
superiority by virtue of its blind-spot network architecture. However, when reconstructing the pixels within largesized anomalous targets, both the unsupervised learning-based
USLNet and the self-supervised learning-based BaseNet (joint
spatial–spectral learning-based models) are prone to interference from neighboring anomalous pixels, which causes

WANG et al.: SLIDING DUAL-WINDOW-INSPIRED RECONSTRUCTION NETWORK FOR HAD

TABLE III
AUC VALUES A FTER THE A BLATION S TUDY FOR D IFFERENT DATASETS

5504115

reliably leverage the self-supervised learning-based blind-spot
framework for HAD purposes, thus extending its applications.
G. Comparison of Inference Times

the models to overfit anomalies and limits the detection
performance. In contrast, DirectNet (coupled with a sliding
dual-window model) avoids the abovementioned problems,
where the inner window prevents potential contamination of
anomalies to reconstruct HSIs with pure backgrounds. As a
result, the capability of DirectNet in recognizing anomalies
from HSIs is significantly enhanced, yielding higher AUC
values. In addition, the reconstruction errors as the degree of
anomaly of each pixel based on ℓ1 and ℓ2 have comparable
effects in separating anomalous targets from the original HSI
by the model, which reflects the robustness of DirectNet in
the task of detecting anomalies.

The inference times of different methods on all datasets
are recorded in Table V to assess the models’ computational
burden. Other than Auto-AD, BS3 LNet, and DirectNet, which
were implemented based on the PyTorch 1.12.1 framework,
the remaining methods were implemented with MATLAB
2019b. Compared to the traditional model-based detectors
using several tricks (e.g., fractional Fourier transform, sliding
dual window, and representation learning), GRX acquires the
fastest computation time due to its clean design principle, but
its detection effect is deemed relatively ineffective. Furthermore, because the five DL-based methods employ analogous
procedures for HAD (these networks promise to be excellent
background reconstruction models, and most of them adopt
mean square error-based reconstruction errors as the final
anomaly scores), they achieve comparable inference times on
different datasets. Although the inference time of the proposed
DirectNet is nonoptimal, DirectNet obtains promising results
and its competitiveness is outstanding.
IV. D ISCUSSION

F. Performance Analysis Between Target Size and Inner
Window Size
To investigate the relationship between the inner window
size and the target size, we regularly embed 2 × 2 anomalous
targets on a background subimage, and their spatial sizes are
set between 1 × 1 and 9 × 9. Among them, a background
image and anomaly spectrum (building) were chosen from the
Salinas dataset. Meanwhile, the abundance of all targets and
the inner window size Win × Win were set to 0.3 and {1 × 1,
3 × 3, 5 × 5, 7 × 7, 9 × 9}, respectively. Then, the AUC
values attained by the proposed DirectNet on the nine synthetic
datasets (using different inner window sizes) are reported in
Table IV. We reiterate that, when Win is set to 1, DirectNet
degenerates into a blind-spot network with a single-window
model (same as BaseNet in Section III-E).
We observed that BaseNet behaved with varying degrees of
performance degradation on HSIs with target sizes larger than
4×4, and the larger the target sizes, the lower the corresponding AUC scores. Moreover, when Win is small (e.g., 3 and 5),
DirectNet appears to manifest a similar behavior on HSIs with
relatively larger target sizes. However, as Win increases, the
applicability of DirectNet becomes broader, particularly when
the inner window size is 9 × 9, DirectNet always performs
optimally on HSIs containing synthetic targets of different
sizes. This is a result of DirectNet coupling a sliding dualwindow reconstruction model, where the inner window (which
is not available for reconstructing the central pixel) mitigates
the interference of anomalies with the outer window (the
receptive field outside of the inner window) pixels, enforcing
the model’s ability to reconstruct the background samples
on the one hand, and weakening its representation ability
for anomalous samples on the other, thus achieving a purer
background. Especially for large-sized targets, DirectNet can

At present, mainstream DL-based HAD methods, such as
GAED, RGAE, and Auto-AD, commonly adopt AE as the
background reconstruction models and train the networks in
an unsupervised learning manner, with the reconstruction error
as the final detection result. However, the above methods may
fit anomalous targets to varying degrees and yield unsatisfactory effects. In this article, we incorporate a blind-spot
network based on self-supervised learning as the backbone
and seamlessly embed a sliding dual-window model into
this. Unlike BS3 LNet that concerns one-pixel blind spots, our
DirectNet places the center block of the receptive field as a
blind area (inner window), preventing potential contamination
from anomalous pixels. Therefore, DirectNet is considered
as a superior background reconstructor to enhance the background reconstruction and restrain the anomaly reconstruction.
BS3 LNet is only applicable to recognize anomalous targets for
small-sized subpixels, while DirectNet is flexible in detecting
both large- and small-sized targets, expanding the application
range of blind spot networks.
From a practical application perspective, our DirectNet is
similar to the traditional unsupervised reconstruction model,
only requiring unlabeled observed HSI to identify anomalous
targets by using the reconstruction error. Yet, DirectNet can
further weaken the fitting ability for anomalies, favorably
separating anomalies from HSI and apparently performing
better. Therefore, DirectNet will probably showcase more
potential and advantages in practical applications. However,
limited by the initial design concept, the insufficient generalization performance remains an existing issue for most
models in the hyperspectral remote sensing field, including our
DirectNet. In the HAD task, several researchers have made
some efforts to achieve generalizability for models, such as
WeaklyAD [81], AUD-Net [82], and AETNet [83]. Among

5504115

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 62, 2024

TABLE IV
AUC VALUES OF THE P ROPOSED D IRECT N ET W ITH D IFFERENT PARAMETERS ON THE S YNTHETIC DATASET

TABLE V
RUNNING T IMES ( IN S ECONDS ) OF THE 11 C ONSIDERED D ETECTORS

them, WeaklyAD and AETNet are devoted to enhancing the
discrimination between the background and anomaly of the
reconstructed image and employ GRX or other detectors
directly on the reconstructed image to identify anomalous
targets efficiently. AUD-Net, on the other hand, aims at
estimating the central pixel by the contextual information and
exploits the relation embedding difference between each pixel
and the surrounding pixels as the anomaly scores. Meanwhile,
AUD-Net and AETNet use a huge number of training samples
from multiple HSIs to improve the generalization capability of
models, benefiting from the rich information provided. Unlike
the aforementioned methods, our DirectNet is trained on a
single HSI in a fully self-supervised manner, so as to obtain
a model that can adequately reconstruct the background of
this HSI, and it employs the reconstruction error to detect
anomalies. The generalization performance of DirectNet is
relatively limited; therefore, in future work, we will focus on
designing frameworks with strong generalization capability for
HAD for practical engineering applications.
V. C ONCLUSION
In this article, the sliding dual-window model is creatively
coupled with a deep reconstruction network for HAD purposes. To be specific, we built a background reconstruction
network whose receptive field is adaptively matched to the
training patch size so that the spatial–spectral features of the
HSIs come into full play. Besides, the center block information
of the receptive field is erased so that it is not seen by the
network at all, and it is regarded as an inner window. An elaborate mask-learning strategy allows the network to concentrate
on the reconstruction of the central pixel. Ultimately, our
DirectNet divides its receptive field into a dual window and
only uses outer window (the receptive field outside the inner
window) pixels to reconstruct each pixel. As a result, the
interference of anomalous samples on the reconstructed HSI

is reduced, rendering the proposed DirectNet as a promising
model for background reconstruction. Extensive experiments
have proven the superior and comprehensive performance of
our DirectNet on HSIs with anomalous targets of various sizes.
R EFERENCES
[1] B. Zhang et al., “Progress and challenges in intelligent remote sensing
satellite systems,” IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens.,
vol. 15, pp. 1814–1822, 2022.
[2] J. Li et al., “Deep learning in multimodal remote sensing data fusion:
A comprehensive review,” Int. J. Appl. Earth Observ. Geoinf., vol. 112,
Aug. 2022, Art. no. 102926.
[3] H. Su, Z. Wu, H. Zhang, and Q. Du, “Hyperspectral anomaly detection:
A survey,” IEEE Geosci. Remote Sens. Mag., vol. 10, no. 1, pp. 64–90,
Mar. 2022.
[4] Z. Zhang, D. Wang, X. Sun, L. Zhuang, R. Liu, and L. Ni, “Spatial
sampling and grouping information entropy strategy based on kernel
fuzzy C-means clustering method for hyperspectral band selection,”
Remote Sens., vol. 14, no. 19, p. 5058, Oct. 2022.
[5] W. Rao, L. Gao, Y. Qu, X. Sun, B. Zhang, and J. Chanussot, “Siamese
transformer network for hyperspectral image target detection,” IEEE
Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no. 5526419.
[6] X. Sun et al., “Ensemble-based information retrieval with mass estimation for hyperspectral target detection,” IEEE Trans. Geosci. Remote
Sens., vol. 60, 2022, Art. no. 5508123.
[7] L. Gao, X. Sun, X. Sun, L. Zhuang, Q. Du, and B. Zhang, “Hyperspectral
anomaly detection based on chessboard topology,” IEEE Trans. Geosci.
Remote Sens., vol. 61, 2023, Art. no. 5505016.
[8] X. Zhao, K. Liu, K. Gao, and W. Li, “Hyperspectral time-series target
detection based on spectral perception and spatial–temporal tensor
decomposition,” IEEE Trans. Geosci. Remote Sens., vol. 61, 2023,
Art. no. 5520812.
[9] I. S. Reed and X. Yu, “Adaptive multiple-band CFAR detection of an
optical pattern with unknown spectral distribution,” IEEE Trans. Acoust.,
Speech, Signal Process., vol. 38, no. 10, pp. 1760–1770, 1990.
[10] J. M. Molero, E. M. Garzón, I. García, and A. Plaza, “Analysis and
optimizations of global and local versions of the RX algorithm for
anomaly detection in hyperspectral data,” IEEE J. Sel. Topics Appl. Earth
Observ. Remote Sens., vol. 6, no. 2, pp. 801–814, Apr. 2013.
[11] Q. Guo, B. Zhang, Q. Ran, L. Gao, J. Li, and A. Plaza, “WeightedRXD and linear filter-based RXD: Improving background statistics
estimation for anomaly detection in hyperspectral imagery,” IEEE J. Sel.
Topics Appl. Earth Observ. Remote Sens., vol. 7, no. 6, pp. 2351–2366,
Jun. 2014.

WANG et al.: SLIDING DUAL-WINDOW-INSPIRED RECONSTRUCTION NETWORK FOR HAD

[12] H. Kwon and N. M. Nasrabadi, “Kernel RX-algorithm: A nonlinear
anomaly detector for hyperspectral imagery,” IEEE Trans. Geosci.
Remote Sens., vol. 43, no. 2, pp. 388–397, Feb. 2005.
[13] R. Tao, X. Zhao, W. Li, H.-C. Li, and Q. Du, “Hyperspectral anomaly
detection by fractional Fourier entropy,” IEEE J. Sel. Topics Appl. Earth
Observ. Remote Sens., vol. 12, no. 12, pp. 4920–4929, Dec. 2019.
[14] X. Zhao, Z. Hou, X. Wu, W. Li, P. Ma, and R. Tao, “Hyperspectral
target detection based on transform domain adaptive constrained energy
minimization,” Int. J. Appl. Earth Observ. Geoinf., vol. 103, Dec. 2021,
Art. no. 102461.
[15] J. Liu, Z. Hou, W. Li, R. Tao, D. Orlando, and H. Li, “Multipixel
anomaly detection with unknown patterns for hyperspectral imagery,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 10, pp. 5557–5567,
Oct. 2022.
[16] F. Vincent, O. Besson, and S. Matteoli, “Anomaly detection for replacement model in hyperspectral imaging,” Signal Process., vol. 185,
Aug. 2021, Art. no. 108079.
[17] X. Yang, X. Huang, M. Zhu, S. Xu, and Y. Liu, “Ensemble and random
RX with multiple features anomaly detector for hyperspectral image,”
IEEE Geosci. Remote Sens. Lett., vol. 19, 2022, Art. no. 6009505.
[18] L. Zhuang and M. K. Ng, “FastHyMix: Fast and parameter-free hyperspectral image mixed noise removal,” IEEE Trans. Neural Netw. Learn.
Syst., vol. 34, no. 8, pp. 4702–4716, Aug. 2023.
[19] L. Zhuang, M. K. Ng, X. Fu, and J. M. Bioucas-Dias, “Hy-demosaicing:
Hyperspectral blind reconstruction from spectral subsampling,” IEEE
Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no. 5515815.
[20] L. Zhuang, M. K. Ng, and Y. Liu, “Cross-track illumination correction
for hyperspectral pushbroom sensor images using low-rank and sparse
representations,” IEEE Trans. Geosci. Remote Sens., vol. 61, 2023,
Art. no. 5502117.
[21] L. Ren, Z. Ma, and F. Bovolo, “A novel dual-alternating direction method
of multipliers for spectral unmixing,” IEEE Geosci. Remote Sens. Lett.,
vol. 18, no. 3, pp. 528–532, Mar. 2021.
[22] X. Zhao, W. Li, C. Zhao, and R. Tao, “Hyperspectral target detection
based on weighted Cauchy distance graph and local adaptive collaborative representation,” IEEE Trans. Geosci. Remote Sens., vol. 60, 2022,
Art. no. 5527313.
[23] L. Gao, Z. Wang, L. Zhuang, H. Yu, B. Zhang, and J. Chanussot,
“Using low-rank representation of abundance maps and nonnegative
tensor factorization for hyperspectral nonlinear unmixing,” IEEE Trans.
Geosci. Remote Sens., vol. 60, 2022, Art. no. 5504017.
[24] L. Zhuang, X. Fu, M. K. Ng, and J. M. Bioucas-Dias, “Hyperspectral
image denoising based on global and nonlocal low-rank factorizations,”
IEEE Trans. Geosci. Remote Sens., vol. 59, no. 12, pp. 10438–10454,
Dec. 2021.
[25] L. Zhuang and M. K. Ng, “Hyperspectral mixed noise removal by ℓ1 norm-based subspace representation,” IEEE J. Sel. Topics Appl. Earth
Observ. Remote Sens., vol. 13, pp. 1143–1157, 2020.
[26] T.-X. Jiang, L. Zhuang, T.-Z. Huang, X.-L. Zhao, and J. M. BioucasDias, “Adaptive hyperspectral mixed noise removal,” IEEE Trans.
Geosci. Remote Sens., vol. 60, 2022, Art. no. 5511413.
[27] L. Ren, Z. Ma, F. Bovolo, and L. Bruzzone, “A nonconvex framework for sparse unmixing incorporating the group structure of the
spectral library,” IEEE Trans. Geosci. Remote Sens., vol. 60, 2022,
Art. no. 5506719.
[28] T.-X. Jiang, M. K. Ng, J. Pan, and G.-J. Song, “Nonnegative low
rank tensor approximations with multidimensional image applications,”
Numerische Math., vol. 153, no. 1, pp. 141–170, Jan. 2023.
[29] J. Li, H. Zhang, L. Zhang, and L. Ma, “Hyperspectral anomaly detection
by the use of background joint sparse representation,” IEEE J. Sel.
Topics Appl. Earth Observ. Remote Sens., vol. 8, no. 6, pp. 2523–2533,
Jun. 2015.
[30] W. Li and Q. Du, “Collaborative representation for hyperspectral
anomaly detection,” IEEE Trans. Geosci. Remote Sens., vol. 53, no. 3,
pp. 1463–1474, Mar. 2015.
[31] M. Vafadar and H. Ghassemian, “Anomaly detection of hyperspectral
imagery using modified collaborative representation,” IEEE Geosci.
Remote Sens. Lett., vol. 15, no. 4, pp. 577–581, Apr. 2018.
[32] L. Zhuang, L. Gao, B. Zhang, X. Fu, and J. M. Bioucas-Dias,
“Hyperspectral image denoising and anomaly detection based on lowrank and sparse representations,” IEEE Trans. Geosci. Remote Sens.,
vol. 60, 2022, Art. no. 5500117.
[33] L. Zhang, L. Song, B. Du, and Y. Zhang, “Nonlocal low-rank tensor
completion for visual data,” IEEE Trans. Cybern., vol. 51, no. 2,
pp. 673–685, Feb. 2021.

5504115

[34] Y. Zhang, B. Du, L. Zhang, and S. Wang, “A low-rank and sparse matrix
decomposition-based Mahalanobis distance method for hyperspectral
anomaly detection,” IEEE Trans. Geosci. Remote Sens., vol. 54, no. 3,
pp. 1376–1389, Mar. 2016.
[35] L. Li, W. Li, Q. Du, and R. Tao, “Low-rank and sparse decomposition
with mixture of Gaussian for hyperspectral anomaly detection,” IEEE
Trans. Cybern., vol. 51, no. 9, pp. 4363–4372, Sep. 2021.
[36] Y. Xu, Z. Wu, J. Li, A. Plaza, and Z. Wei, “Anomaly detection in
hyperspectral images based on low-rank and sparse representation,”
IEEE Trans. Geosci. Remote Sens., vol. 54, no. 4, pp. 1990–2000,
Apr. 2016.
[37] X. Fu, S. Jia, L. Zhuang, M. Xu, J. Zhou, and Q. Li, “Hyperspectral
anomaly detection via deep plug-and-play denoising CNN regularization,” IEEE Trans. Geosci. Remote Sens., vol. 59, no. 11, pp. 9553–9568,
Nov. 2021.
[38] Y. Qu et al., “Hyperspectral anomaly detection through spectral unmixing and dictionary-based low-rank decomposition,” IEEE Trans. Geosci.
Remote Sens., vol. 56, no. 8, pp. 4391–4405, Aug. 2018.
[39] C. Zhao, C. Li, S. Feng, and X. Jia, “Enhanced total variation regularized representation model with endmember background dictionary for
hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote Sens.,
vol. 60, 2022, Art. no. 5518312.
[40] X. He, J. Wu, Q. Ling, Z. Li, Z. Lin, and S. Zhou, “Anomaly
detection for hyperspectral imagery via tensor low-rank approximation
with multiple subspace learning,” IEEE Trans. Geosci. Remote Sens.,
vol. 61, 2023, Art. no. 5509917.
[41] J. Li, K. Zheng, Z. Li, L. Gao, and X. Jia, “X-shaped interactive
autoencoders with cross-modality mutual learning for unsupervised
hyperspectral image super-resolution,” IEEE Trans. Geosci. Remote
Sens., vol. 61, 2023, Art. no. 5518317.
[42] Z. Wang, M. K. Ng, L. Zhuang, L. Gao, and B. Zhang, “Nonlocal
self-similarity-based hyperspectral remote sensing image denoising with
3-D convolutional neural network,” IEEE Trans. Geosci. Remote Sens.,
vol. 60, 2022, Art. no. 5531617.
[43] L. Gao, J. Li, K. Zheng, and X. Jia, “Enhanced autoencoders
with attention-embedded degradation learning for unsupervised hyperspectral image super-resolution,” IEEE Trans. Geosci. Remote Sens.,
vol. 61, 2023, Art. no. 5509417.
[44] S. Mei, X. Chen, Y. Zhang, J. Li, and A. Plaza, “Accelerating
convolutional neural network-based hyperspectral image classification
by step activation quantization,” IEEE Trans. Geosci. Remote Sens.,
vol. 60, 2022, Art. no. 5502012.
[45] W. Li, G. Wu, and Q. Du, “Transferred deep learning for anomaly
detection in hyperspectral imagery,” IEEE Geosci. Remote Sens. Lett.,
vol. 14, no. 5, pp. 597–601, May 2017.
[46] W. Rao, Y. Qu, L. Gao, X. Sun, Y. Wu, and B. Zhang, “Transferable
network with Siamese architecture for anomaly detection in hyperspectral images,” Int. J. Appl. Earth Observ. Geoinf., vol. 106, Feb. 2022,
Art. no. 102669.
[47] E. Bati, A. Caliskan, A. Koz, and A. A. Alatan, “Hyperspectral anomaly
detection method based on auto-encoder,” Proc. SPIE, vol. 9643,
Oct. 2015, Art. no. 96430N.
[48] P. Xiang, S. Ali, S. K. Jung, and H. Zhou, “Hyperspectral anomaly
detection with guided autoencoder,” IEEE Trans. Geosci. Remote Sens.,
vol. 60, 2022, Art. no. 5538818.
[49] G. Fan, Y. Ma, X. Mei, F. Fan, J. Huang, and J. Ma, “Hyperspectral
anomaly detection with robust graph autoencoders,” IEEE Trans. Geosci.
Remote Sens., vol. 60, 2022, Art. no. 5511314.
[50] S. Wang, X. Wang, L. Zhang, and Y. Zhong, “Auto-AD: Autonomous
hyperspectral anomaly detection network based on fully convolutional autoencoder,” IEEE Trans. Geosci. Remote Sens., vol. 60, 2022,
Art. no. 5503314.
[51] Z. Zhao and B. Sun, “Hyperspectral anomaly detection via memoryaugmented autoencoders,” CAAI Trans. Intell. Technol., vol. 8, no. 4,
pp. 1274–1287, Dec. 2023.
[52] Y. Lian, Y. Zhang, X. Feng, X. Jiang, and Z. Cai, “Low-rank constrained
memory autoencoder for hyperspectral anomaly detection,” in Proc.
IEEE Int. Conf. Acoust., Speech Signal Process. (ICASSP), Jun. 2023,
pp. 1–5.
[53] Y. Li, T. Jiang, W. Xie, J. Lei, and Q. Du, “Sparse coding-inspired GAN
for hyperspectral anomaly detection in weakly supervised learning,”
IEEE Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no. 5512811.
[54] W. Xie, X. Zhang, Y. Li, J. Lei, J. Li, and Q. Du, “Weakly supervised
low-rank representation for hyperspectral anomaly detection,” IEEE
Trans. Cybern., vol. 51, no. 8, pp. 3889–3900, Aug. 2021.

5504115

[55] D. Wang, L. Gao, Y. Qu, X. Sun, and W. Liao, “Frequency-to-spectrum
mapping GAN for semisupervised hyperspectral anomaly detection,”
CAAI Trans. Intell. Technol., vol. 8, no. 4, pp. 1258–1273, Dec. 2023.
[56] K. Li et al., “Spectral–spatial deep support vector data description for
hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote Sens.,
vol. 60, 2022, Art. no. 5522316.
[57] F. Ye, C. Huang, J. Cao, M. Li, Y. Zhang, and C. Lu, “Attribute
restoration framework for anomaly detection,” IEEE Trans. Multimedia,
vol. 24, pp. 116–127, 2022.
[58] C. Huang et al., “Self-supervision-augmented deep autoencoder for
unsupervised visual anomaly detection,” IEEE Trans. Cybern., vol. 52,
no. 12, pp. 13834–13847, Dec. 2022.
[59] L. Ericsson, H. Gouk, C. C. Loy, and T. M. Hospedales, “Self-supervised
representation learning: Introduction, advances, and challenges,” IEEE
Signal Process. Mag., vol. 39, no. 3, pp. 42–62, May 2022.
[60] D. Wang, L. Zhuang, L. Gao, X. Sun, M. Huang, and A. Plaza,
“BockNet: Blind-block reconstruction network with a guard window for
hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote Sens.,
vol. 61, 2023, Art. no. 5531916.
[61] L. Zhuang, M. K. Ng, L. Gao, J. Michalski, and Z. Wang, “Eigenimage2Eigenimage (E2E): A self-supervised deep learning network for
hyperspectral image denoising,” IEEE Trans. Neural Netw. Learn. Syst.,
early access, Jul. 19, 2023. [Online]. Available: https://ieeexplore.ieee.
org/abstract/document/10187207, doi: 10.1109/TNNLS.2023.3293328.
[62] Z. Wang, M. K. Ng, J. Michalski, and L. Zhuang, “A self-supervised
deep denoiser for hyperspectral and multispectral image fusion,” IEEE
Trans. Geosci. Remote Sens., vol. 61, 2023, Art. no. 5520414.
[63] H. Gao, S. Li, and R. Dian, “Hyperspectral and multispectral image
fusion via self-supervised loss and separable loss,” IEEE Trans. Geosci.
Remote Sens., vol. 60, 2022, Art. no. 5520917.
[64] Z. Han, D. Hong, L. Gao, J. Yao, B. Zhang, and J. Chanussot,
“Multimodal hyperspectral unmixing: Insights from attention networks,”
IEEE Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no. 5524913.
[65] J. Yue, L. Fang, H. Rahmani, and P. Ghamisi, “Self-supervised learning
with adaptive distillation for hyperspectral image classification,” IEEE
Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no. 5501813.
[66] A. Krull, T.-O. Buchholz, and F. Jug, “Noise2Void—Learning denoising
from single noisy images,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2019, pp. 2124–2132.
[67] L. Gao, D. Wang, L. Zhuang, X. Sun, M. Huang, and A. Plaza,
“BS3 LNet: A new blind-spot self-supervised learning network for hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote Sens., vol. 61,
2023, Art. no. 5504218.
[68] D. Wang, L. Zhuang, L. Gao, X. Sun, M. Huang, and A. J. Plaza, “PDBSNet: Pixel-shuffle downsampling blind-spot reconstruction network for
hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote Sens.,
vol. 61, 2023, Art. no. 5511914.
[69] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 15979–15988.
[70] G. Scarpa, S. Vitale, and D. Cozzolino, “Target-adaptive CNN-based
pansharpening,” IEEE Trans. Geosci. Remote Sens., vol. 56, no. 9,
pp. 5443–5457, Sep. 2018.
[71] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
in Proc. ICLR, 2015, pp. 1–15.
[72] K. Tan, Z. Hou, D. Ma, Y. Chen, and Q. Du, “Anomaly detection in
hyperspectral imagery based on low-rank representation incorporating a
spatial constraint,” Remote Sens., vol. 11, no. 13, p. 1578, Jul. 2019.
[73] M. S. Stefanou and J. P. Kerekes, “A method for assessing spectral
image utility,” IEEE Trans. Geosci. Remote Sens., vol. 47, no. 6,
pp. 1698–1706, Jun. 2009.
[74] L. Ren, D. Hong, L. Gao, X. Sun, M. Huang, and J. Chanussot,
“Hyperspectral sparse unmixing via nonconvex shrinkage penalties,”
IEEE Trans. Geosci. Remote Sens., vol. 61, 2023, Art. no. 5500415.
[75] B. Zhang, L. Zhuang, L. Gao, W. Luo, Q. Ran, and Q. Du, “PSOEM: A hyperspectral unmixing algorithm based on normal compositional model,” IEEE Trans. Geosci. Remote Sens., vol. 52, no. 12,
pp. 7782–7792, Dec. 2014.
[76] L. Ren, D. Hong, L. Gao, X. Sun, M. Huang, and J. Chanussot,
“Orthogonal subspace unmixing to address spectral variability for hyperspectral image,” IEEE Trans. Geosci. Remote Sens., vol. 61, 2023,
Art. no. 5501713.
[77] X. Kang, X. Zhang, S. Li, K. Li, J. Li, and J. A. Benediktsson, “Hyperspectral anomaly detection with attribute and edge-preserving filters,”
IEEE Trans. Geosci. Remote Sens., vol. 55, no. 10, pp. 5600–5611,
Oct. 2017.

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 62, 2024

[78] S. Li, K. Zhang, P. Duan, and X. Kang, “Hyperspectral anomaly
detection with kernel isolation forest,” IEEE Trans. Geosci. Remote
Sens., vol. 58, no. 1, pp. 319–329, Jan. 2020.
[79] Z. Wu, W. Zhu, J. Chanussot, Y. Xu, and S. Osher, “Hyperspectral
anomaly detection via global and local joint modeling of background,”
IEEE Trans. Signal Process., vol. 67, no. 14, pp. 3858–3869, Jul. 2019.
[80] C.-I. Chang, “An effective evaluation tool for hyperspectral target
detection: 3D receiver operating characteristic curve analysis,” IEEE
Trans. Geosci. Remote Sens., vol. 59, no. 6, pp. 5131–5153, Jun. 2021.
[81] T. Jiang, W. Xie, Y. Li, J. Lei, and Q. Du, “Weakly supervised
discriminative learning with spectral constrained generative adversarial
network for hyperspectral anomaly detection,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 33, no. 11, pp. 6504–6517, Nov. 2022.
[82] N. Huyan, X. Zhang, D. Quan, J. Chanussot, and L. Jiao, “AUDNet: A unified deep detector for multiple hyperspectral image anomaly
detection via relation and few-shot learning,” IEEE Trans. Neural Netw.
Learn. Syst., early access, Oct. 27, 2022. [Online]. Available: https://
ieeexplore.ieee.org/abstract/document/9931456, doi: 10.1109/TNNLS.
2022.3213023.
[83] Z. Li, Y. Wang, C. Xiao, Q. Ling, Z. Lin, and W. An, “You only
train once: Learning a general anomaly enhancement network with random masks for hyperspectral anomaly detection,” IEEE Trans. Geosci.
Remote Sens., vol. 61, 2023, Art. no. 5506718.

Degang Wang received the B.S. degree in communication engineering from the Hebei University
of Technology, Tianjin, China, in 2020. He is currently pursuing the Ph.D. degree in cartography and
geography information system with the Key Laboratory of Computational Optical Imaging Technology,
Aerospace Information Research Institute, Chinese
Academy of Sciences, Beijing, China.
His research interests include hyperspectral image
processing, deep learning, and target detection.

Lina Zhuang (Member, IEEE) received the Ph.D.
degree in electrical and computer engineering from
the Instituto Superior Tecnico, Universidade de Lisboa, Lisbon, Portugal, in 2018.
From 2015 to 2018, she was a Marie Curie Early
Stage Researcher of Sparse Representations and
Compressed Sensing Training Network (SpaRTaN
number 607290) with the Instituto de Telecomunicações, Lisbon. SpaRTaN Initial Training Networks
(ITN) is funded under the European Union’s Seventh Framework Programme (FP7-PEOPLE-2013ITN) call and is part of the Marie Curie Actions-ITN funding scheme.
From 2019 to 2021, she was a Research Assistant Professor with the Math
Department, Hong Kong Baptist University, Hong Kong. From 2021 to 2022,
She was a Research Assistant Professor with the Math Department, The
University of Hong Kong, Hong Kong. She is currently a Professor with
the Aerospace Information Research Institute, Chinese Academy of Sciences,
Beijing, China. Her research interests include hyperspectral image restoration,
superresolution, and compressive sensing.

Lianru Gao (Senior Member, IEEE) received the
B.S. degree in civil engineering from Tsinghua University, Beijing, China, in 2002, and the Ph.D. degree
in cartography and geographic information system
from the Institute of Remote Sensing Applications, Chinese Academy of Sciences (CAS), Beijing,
in 2007.
He has been a Visiting Scholar at the University
of Extremadura, Cáceres, Spain, in 2014, and the
Mississippi State University (MSU), Starkville, MS,
USA, in 2016. He is currently a Professor with the
Key Laboratory of Computational Optical Imaging Technology, Aerospace
Information Research Institute, CAS. In the last ten years, he was the Principal
Investigator of ten scientific research projects at national and ministerial levels,

WANG et al.: SLIDING DUAL-WINDOW-INSPIRED RECONSTRUCTION NETWORK FOR HAD

including projects by the National Natural Science Foundation of China
(2018–2020, 2022–2025, and 2024–2028) and the National Key Research
and Development Program of China (2021–2025). He was supported by the
National Science Fund for Distinguished Young Scholars of China in 2023.
He has published more than 240 peer-reviewed articles, and there are more
than 150 journal articles included by the Science Citation Index (SCI). He was
coauthor of three academic books, including Hyperspectral Image Information
Extraction. He obtained 30 national invention patents in China. His research
focuses on hyperspectral image processing and information extraction.
Dr. Gao is a fellow of the Institution of Engineering and Technology.
He was awarded the Outstanding Science and Technology Achievement Prize
of CAS in 2016. He won the Second Prize of the State Scientific and
Technological Progress Award in 2018. He received the 2021 Outstanding
Paper Award at the IEEE Workshop on Hyperspectral Image Processing:
Evolution in Remote Sensing (WHISPERS). He is an Associate Editor of
IEEE IEEE T RANSACTIONS ON G EOSCIENCE AND R EMOTE S ENSING and
IET Image Processing.

Xu Sun (Member, IEEE) received the B.S. degree
in mathematics and application mathematics from
Tsinghua University, Beijing, China, in 2006, and
the Ph.D. degree in cartography and geographical
information system from the Graduate University of
Chinese Academy of Sciences, Beijing, in 2011.
He is currently an Associate Researcher with
the Aerospace Information Research Institute, Chinese Academy of Sciences, Beijing. His research
interests include hyperspectral image processing,
artificial intelligence algorithm, and high-resolution
remote sensing image information mining.

5504115

Xiaobin Zhao received the B.S. degree in electronic information science and technology from the
Guangxi University of Science and Technology,
Liuzhou, Guangxi, China, in 2014, the M.S. degree
in electronics and communications engineering from
Inner Mongolia University, Hohhot, Inner Mongolia,
China, in 2018, and the Ph.D. degree in information
and communications engineering from the Beijing
Institute of Technology, Beijing, China, in 2022.
He is currently a Post-Doctoral Researcher with
the School of Information and Electronics, Beijing
Institute of Technology. His research interests include remote image
processing and hyperspectral target detection.
Antonio Plaza (Fellow, IEEE) received the M.Sc.
and Ph.D. degrees in computer engineering from the
Department of Technology of Computers and Communications, University of Extremadura, Cáceres,
Spain, in 1999 and 2002, respectively.
He is currently a Full Professor and the Head of
the Hyperspectral Computing Laboratory, Department of Technology of Computers and Communications, University of Extremadura. He has authored
more than 700 publications and guest edited ten
journal special issues. He has reviewed more than
500 manuscripts for over 50 different journals.
Dr. Plaza was elected in 2020 as a member of Academia Europaea—
The Academy of Europe. He received the 2021 Outstanding Paper Award
at the IEEE Workshop: Hyperspectral Sensing meets Machine Learning and
Pattern Analysis (HyperMLPA), the 2019 Outstanding Paper Award at the
IEEE Workshop on Hyperspectral Image Processing: Evolution in Remote
Sensing (WHISPERS), and the Top Cited Article Award of Elsevier’s Journal
of Parallel and Distributed Computing from 2005 to 2010 for the contribution
entitled “Commodity Cluster-Based Parallel Processing of Hyperspectral
Imagery.” He was a recipient of the 2015 IEEE Signal Processing Magazine
Best Column Paper Award for the contribution entitled “Parallel Hyperspectral
Image and Signal Processing” published in IEEE Signal Processing Magazine
in April 2011, the 2014 Geoscience and Remote Sensing Society Prize Paper
Award of the IEEE J OURNAL OF S ELECTED T OPICS IN A PPLIED E ARTH
O BSERVATIONS AND R EMOTE S ENSING (JSTARS) for the contribution
entitled “A Web-Based System for Classification of Remote Sensing Data”
published in IEEE JSTARS in August 2013, the recognition of Best Reviewers
of IEEE T RANSACTIONS ON G EOSCIENCE AND R EMOTE S ENSING (TGRS)
in 2010, and the recognition of Best Reviewers of the IEEE G EOSCIENCE
AND R EMOTE S ENSING L ETTERS journal in 2009. He was the Editor-in-Chief
of IEEE TGRS from 2013 to 2017. From 2018 to 2021, he was included in
the Highly Cited Researchers List (Clarivate Analytics).
PAPER_TEXT
