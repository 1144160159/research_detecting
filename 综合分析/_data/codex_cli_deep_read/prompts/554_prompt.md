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
# [554] SWANet: A Sliding Window Affinity Network With Dual-Branch Structure for Detection of Automotive Chip Packaging Carriers
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
编号：554
题名：SWANet: A Sliding Window Affinity Network With Dual-Branch Structure for Detection of Automotive Chip Packaging Carriers
年份：2025
DOI：10.1109/tim.2025.3558829
来源：IEEE Transactions on Instrumentation and Measurement
PDF：paper/10.1109_TIM.2025.3558829.pdf
已有粗分类：加密流量分类与应用识别
二级关联：无
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\554.txt
- 原始字符数：63981
- 本次发送字符数：63981
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

5027713

SWANet: A Sliding Window Affinity Network
With Dual-Branch Structure for Detection of
Automotive Chip Packaging Carriers
Huimin Wang , Bumin Meng , Member, IEEE, Jiang Zhu , and Rui Du , Graduate Student Member, IEEE

Abstract— In automotive chip packaging carrier (ACPC) defect
detection, distinguishing defects is particularly challenging due
to the high similarity between missing regions and background
textures. Additionally, the scarcity of defect samples further
exacerbates this issue. To address these problems, a defect
detection network based on sliding window affinity (SWA) with
a dual-branch structure has been proposed. The defect sample
pool is effectively expanded through a region transformation
augmentation technique, which helps alleviate class imbalance
issues. Affinity maps are calculated via local affine transformations to enhance internal pixel relationships, and heterogeneous
feature parsing (HFP) is employed to emphasize subtle proactive
layer features. This method achieves a significant improvement
in detection accuracy, reaching 74.38% mAP on the ACPC
dataset, and demonstrates strong robustness under varying noise
conditions. The results indicate that the proposed method meets
the requirements of real-world production environments and has
the potential for application in other industrial scenarios.
Index Terms— Automotive chip packaging carriers (ACPCs),
cross-region transformation, detection, dual-branch, sliding
window affinity (SWA).

I. I NTRODUCTION
ITH the scarcity of oil and the increasing emphasis
on environmental protection in various countries, new
energy vehicles and electric vehicles have been developing
rapidly in recent years. As the core of controlling most of the
application scenarios of electric vehicles, chips are also the
most important factor in determining the safety, comfort, and
service life of the entire vehicle. Automotive chip packaging
carriers (ACPCs), as the carrier for placing IC chips, are the
key to ensuring the normal operation of electric vehicle chips.
They provide a stable and reliable operating environment for
electric vehicle chips, shielding them from physical shocks,
temperature fluctuations, humidity, and other environmental
factors, as well as electromagnetic interference. Additionally,

W

Received 4 December 2024; revised 14 March 2025; accepted 24 March
2025. Date of publication 14 April 2025; date of current version 30 April
2025. This work was supported in part by the Hunan Province Natural
Science Foundation of China under Grant 2025JJ50376. The Associate Editor
coordinating the review process was Dr. Donghoon Kang. (Corresponding
authors: Bumin Meng; Jiang Zhu.)
Huimin Wang, Bumin Meng, and Jiang Zhu are with the School
of Automation and Electronic Information, Xiangtan University, Xiangtan 411105, China (e-mail: 16673296983@163.com; mengbm@163.com;
zhu_jiang@xtu.edu.cn).
Rui Du is with the School of Robotics, Hunan University, Changsha 410012,
China (e-mail: durui@hnu.edu.cn).
Digital Object Identifier 10.1109/TIM.2025.3558829

Fig. 1.
ACPCs production line. Manually detecting missing positions
in assembly boxes. (a) Production equipment, (b) manual assembly, and
(c) ACPCs missing assembly detection.

they prevent the integrated circuits from overheating, thereby
reducing the likelihood of failures and the need for frequent
replacements.
Fig. 1 shows the actual production line of ACPCs. The
ACPCs are first cut by the relevant production equipment and
then loaded into the test cassettes by the assembly equipment.
During the assembly process, ACPCs may be missed due to
aging of the machine or other factors, which affect the production efficiency. Detecting the missing assembly of ACPCs is
of great significance to reduce production costs and improve
production efficiency. At present, the missing detection of
ACPCs is mainly performed manually by skilled workers.
However, this detection method is labor-intensive, inefficient,
and inaccurate. It is crucial to research machine vision-based
detection of missing assembly of ACPCs. In general, machine
vision-based missing assembly detection can be regarded as a
special object detection task.
Currently, deep learning [1], [2] methods have been widely
applied in industrial product inspection. While dedicated
research on the automated detection of missing components
in ACPCs remains relatively limited, related defect detection studies offer valuable insights. Similar scenarios can
be referenced in surface defect detection based on machine
vision, such as battery defect detection [3], [4], [5], steel
strip defect detection [6], [7], [8], and electric two-wheeled
vehicle defect detection [9]. For example, Badmos et al. [3]
learned an accurate representation of microstructural images
by the CNN to accurately distinguish between defective and
nondefective cases. Zhao et al. [6] improved the traditional
fast R-CNN by using a multiscale algorithm, replacing the
traditional convolution with a deformable convolution to
improve the accuracy of the detection of defects in steel
belts. In another study, a convolutional neural network (CNN)
steered with wavelet synchro squeezing transform (WSST)based scalograms is proposed for fault identification in an

1557-9662 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

5027713

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

electric two-wheel [9]. Zhang et al. [10] proposed an insulator
defect detection framework based on image reconstruction,
which achieved high-precision detection of various insulator
defects by collecting images of catenary insulators captured
by high-speed rail inspection equipment and constructing the
catenary insulator defect (CID) dataset. However, given that
catenary insulators are large detection objects, this method
is not suitable for small object detection tasks like those
involving ACPCs.
Although these methods have achieved promising results in
industrial product inspection, several challenges are encountered when directly applied to ACPCs missing component
detection.
1) There is a scarcity of samples in the ACPC’s missing
component regions, resulting in the issue of sample
imbalance. Several methods have been employed to
enhance data and increase sample diversity. CutPaste
[11], for instance, offers a way to generate defect
samples by randomly copying and pasting regions of
the original samples to augment the data. However, due
to the ordered arrangement of ACPCs, directly applying
this method would disrupt the actual distribution of
samples, resulting in a significant difference from real
test samples, thereby limiting generalization.
2) The pixel proportion of missing regions in ACPCs is
small, making it difficult to effectively extract discriminative features. Some multimodal approaches address
similar small-object issues through multiscale fusion.
For example, Zhu et al. [12] proposed an efficient
multiscale perception enhancement network (ADDet)
for detecting aluminum defects, considering the inherent characteristics of aluminum surface defects, which
exhibit diverse morphologies and multiscale variations.
Zheng et al. [13] introduced a novel efficient conflict
filtering network (ECF-Net) specifically for detecting
small defects. However, these methods are challenging
to apply directly to ACPCs, where the difference in
texture and color between the detection object and
the background is minimal, making such tasks more
complex.
3) The proactive layer and supporting layer of ACPCs are
highly similar, making direct differentiation challenging.
Existing Transformers are primarily designed for global
information modeling, while CNNs excel at capturing
local information. ACPCs, built upon this foundation,
must distinguish between the proactive layer and the
supporting layer under conditions where their colors
closely resemble those of the background, resulting in
minimal pixel variance across regions. The mere use of
CNNs or Transformers struggles to yield robust feature
discriminability; additionally, the pixel features in the
missing areas are not pronounced, often overlooked in
the feature extraction by existing CNNs or Transformers,
complicating precise localization.
To address these challenges, a sliding window affinity
network (SWANet) with a dual-branch structure is proposed
in this article for the detection of ACPCs. The network

incorporates a cross-region transformation algorithm (CRTA),
a sliding window affinity (SWA) module, a dual-branch structure, and a heterogeneous feature parsing (HFP) module.
The CRTA is employed to augment sample data and mitigate overfitting by randomly transforming missing regions
and background segments. The SWA module enhances the
detection of missing component regions by calculating local
feature affinity through a sliding window mechanism. The
dual-branch structure is designed to extract the proactive layer
and supporting layer features separately, thereby addressing
the issue of high similarity between the proactive layer and the
supporting layer in ACPC images. The HFP module parses
the features extracted by the dual branches and strengthens
the correlation between the proactive layer and the supporting
layer using a cross-attention (CA) mechanism, facilitating
precise localization of missing regions. To further improve
detection accuracy, multiscale feature decoding is utilized to
fuse deep and shallow features for the accurate detection of
small objects.
In summary, the main contributions of this article are as
follows.
1) To tackle the issues of data imbalance and the scarcity
of defective samples, the CRTA has been introduced,
utilizing regional random transformations and positional
exchanges to augment the dataset and enhance the
network’s generalization capability. This data augmentation technique effectively mitigates class imbalance and
improves the network’s robustness under varying noise
conditions.
2) The SWA has been proposed, which enhances pixel
interconnections in object regions through pixel affinity
calculations in local areas. This mechanism not only
effectively captures both local and global contextual
information but also improves the detection accuracy
of small objects in ACPCs, demonstrating exceptional
performance in scenarios where pixel features exhibit
high similarity.
3) An innovative dual-branch structure has been designed
to separately extract proactive layer and supporting layer
features, addressing the high similarity between these
elements in ACPCs. Through the parsing conducted by
the HFP module, this dual-branch structure effectively
amplifies the differences between the proactive layer and
the supporting layer, thereby enhancing the network’s
ability to discern missing components and subtle variations, particularly in complex industrial environments.
The rest of the article is organized as follows. Related work
is presented in Section II. SWANet is discussed in Section III.
The constructed dataset and related experiments are presented
in Section IV. Section V presents the conclusions of this study.
II. R ELATED W ORK
This study is related to the application of computer vision
techniques for missing assembly detection of ACPCs. In turn,
missing assembly detection serves as an important category
in the defect detection of ACPCs. Currently, there are fewer
missing assembly detections for ACPCs. Similar work can

WANG et al.: SWANet WITH DUAL-BRANCH STRUCTURE FOR DETECTION OF ACPCs

be referred to as industrial surface defect detection, which is
categorized into traditional methods, CNN-based methods, and
Transformer-based methods.
A. Traditional Methods for Defect Detection
Traditional methods have continued to play an important role in industrial surface defect detection for a long
time, mainly through manually extracted features for defect
detection. Currently, traditional defect detection methods are
categorized into three main types: 1) statistical-based defect
detection methods [17], [18], [19], [20]; 2) structure-based
defect detection methods [21], [22], [23], [24]; and 3) modelbased defect detection methods [25], [26], [27], [28]. The first
method consists of learning models from data to differentiate
between normal data objects and anomalies for defect detection. Yuan et al. [29] proposed an improved Otsu method
for detecting defects on product surfaces by weighted object
variance (WOV). However, the method depends heavily on
the key point detection algorithm or similarity measurement
strategy. The second method focuses on the spatial location
of pixels. Tolba and Raafat [30] proposed the multiscale
structural similarity index (MS-SSIM), which shows the strong
discriminative ability of MS-SSIM between normal and abnormal surfaces. The computational complexity of the third
method is strongly affected by the estimation of the stochastic
model parameters. Wang et al. [17] applied the entity sparsity
pursuit (ESP) method to identify surface defects based on
the fact that surface image textures usually form a low-rank
structure.
B. Deep Learning Methods for Defect Detection
In the past few years, the emergence of deep learning algorithms has brought deep transformations to machine learning
algorithms, distinguishing them from traditional methods such
as eddy current inspection [31] and ultrasonic inspection [32]
by their convenience and speed. For example, for the surface quality inspection problem of LED chips, Shu et al.
[33] proposed a parallel DCNN model and built a fully
automated inspection system operating with high detection
accuracy (99%) to solve the cover glass defect detection
problem. Lu et al. [34] presented a multiscale feature-enhanced
fusion (MFEF) for surface defects detection and a named
MRD-Net reverse attention (RA) network for real-time and
end-to-end defect segmentation. Liang et al. [35] used deep
dynamic convolution as the basic structure of the network to
detect surface defects of nickel-plated perforated steel strips
using adaptive feature extraction. Li et al. [36] suggested an
automated vision and line-laser feeding system combining
industrial object localization and classification methods to
detect defects in the assembly of crankshaft shingle covers.
Recently, due to the remarkable performance of Transformers in computer vision, a multitude of studies have been
devoted to introducing Transformers into defect detection
tasks. In contrast to CNNs, where the inherent localization
of convolution prevents them from explicitly modeling longrange interactions, Transformer-based networks can correlate
each element of the data with each other through their built-in
global self-attention mechanism. Zhu et al. [37] proposed

5027713

a novel network architecture called LSwin Transformer to
construct a convolutional embedding module and an attention patch merging module to improve the retention of
image information. Zhang et al. [38] proposed a two-stage
“promote–suppress” Transformer (PST) framework, which
employs wavelet features to direct the network to focus on
the detailed features in the image and accurately localize and
classify the defective regions in the image. Zhou et al. [39]
effectively classified and sensed defects of different shapes
and sizes by fusing two modules, ETDNet, a Transformerbased detection network, and a channel-modulated feature
pyramid network (CM-FPN). Gao et al. [14] constructed a
novel Transformer detection framework for surface defect
detection of automotive bearings and so on, which outperforms
CNN detection. Luo et al. [15] addressed the problem of
semantic gaps between multiscale features by importing the
CA Transformer (CAT) into the encoder–decoder network
(EDNet). Yu et al. [40] presented a dynamic Transformer
network for surface defect detection, which utilizes a selfattention-based Transformer to accurately capture long-range
semantic information in the routing space, enabling accurate
online detection of multiscale surface defects.
C. Anomaly Detection Methods
Additionally, anomaly detection methods have become
an important research direction in industrial scenarios.
In recent years, both self-supervised and unsupervised learning
approaches have made significant progress in this field. The
DRAEM method proposed by Zavrtanik et al. [41] utilizes an
anomaly synthesis strategy within a self-supervised learning
framework to enhance surface anomaly detection performance.
The anomaly detection method based on a self-supervised
predictive convolutional attentive block (SCAB) proposed by
Ristea et al. [42] has also shown excellent performance,
combining prediction with self-supervised learning to improve
the detection accuracy of industrial defects. The unsupervised
anomaly detection method based on a masked convolutional
Transformer block proposed by Madan et al. [43] further
demonstrates how convolution and Transformer can be combined under unsupervised conditions to enhance the model’s
ability to perceive defect regions. Building on this, Roth et al.
explored how to improve anomaly detection performance in
industrial settings through a global recall mechanism, proposing PatchCore, which effectively balances memory-efficient
feature sampling with high recall performance in industrial
anomaly detection [44]. Additionally, Liu et al. [45] proposed
the appearance-motion prototype network (AMP-net), which
leverages external memory mechanisms to capture appearance and motion features, excelling in anomaly detection
for surveillance videos. This approach balances the effective representation of normal events and anomaly detection,
achieving state-of-the-art (SOTA) performance [45]. Liu et al.
[46] also developed the memory-enhanced spatial–temporal
encoding (MSTE) framework, specifically designed for industrial scenarios, addressing the challenges of scarce industrial
video data and the complexity of anomaly events, improving
the accuracy and spatial–temporal localization of anomaly

5027713

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 2. Pipelines of the detection network. Stage 1 is used for feature extraction; Stages 2–4 are for multiscale feature learning, including MHSA, SWA,
and HFP.

detection. Gong et al. [47] proposed the memory-augmented
autoencoder (MemAE), which enhances the ability to memorize normal patterns by incorporating a memory module
into the autoencoder architecture, thereby improving anomaly
detection performance. Wang et al. [48] introduced a
dual-branch learning framework with prior information for
surface anomaly detection, which effectively mitigates the
overkill problem, a common issue in industrial defect detection. Liu et al. [49] developed SimpleNet, a lightweight
yet effective model designed to enhance the compatibility between defect detection models and industrial imaging,
thereby improving detection accuracy. Li et al. [50] proposed
a novel approach for few-shot anomaly detection by leveraging
prompt learning based solely on normal samples, enabling
more efficient learning in scenarios with limited anomaly data.
III. P ROPOSED M ETHOD
A. Structure of the Detection Model
In this article, a SWANet with a dual-branch structure is
proposed for the detection of missing components in ACPCs.
Initially, the data undergoes augmentation via the CRTA
before being fed into the network. As illustrated in Fig. 2,
the network employs an encoder–decoder architecture. Unlike
traditional object detection networks, the proposed encoder
utilizes a dual-branch structure to separately extract and process distinctive features of the proactive layer and supporting
layer, significantly enhancing the network’s capability to perceive subtle differences between these two elements, thereby
addressing the issue of high similarity in ACPC images.
In the dual-branch structure, the proactive layer and the
supporting layer, respectively, take on the roles of capturing core information and providing auxiliary support. This
division enables the network to more effectively distinguish
key features and background details in complex scenarios,
thereby enhancing its ability to detect missing components,
especially in ACPC images with high-similarity features.
Each branch comprises four feature extraction and processing stages. Specifically, the input image is downsampled to

one-eighth of its original size in the first stage. Unlike the first
stage, the second to fourth stages perform a 2× downsampling
between adjacent stages. Moreover, to address variations in
angle and scale present in the captured images, the network
incorporates a multiscale structure. Three MHSA-SWA structures are designed to learn the multilevel features of ACPCs.
In the MHSA-SWA structure, the global modeling capability
of the Transformer is utilized to extract discriminative global
features for the proactive layer Fi (i = 1, 2, 3) and supporting
layer Bi (i = 1, 2, 3). These global features are then input into
the corresponding SWA modules of each stage, where pixel
affinity relationships are established through a sliding window
mechanism.
The features of the proactive layer and the supporting layer
are first obtained by mapping to high-dimensional embeddings
through a weight-sharing CNN. Subsequently, two MHSA
branches with nonshared weights are constructed to extract
the proactive layer and supporting layer features separately.
This overall CNN–Transformer structure effectively captures
detailed information about the object while establishing comprehensive global connections.
To parse the heterogeneous features within the dual
branches, the HFP module is constructed to accurately differentiate between the proactive layer and the supporting
layer, allowing the network to focus on detecting assembly
differences of the missing components. During the decoding
phase, the multiscale HFP features are progressively decoded
through CA, facilitating the gradual fusion of features across
different levels. These discriminative features are directly input
into the detection head for identifying missing regions within
the ACPC assembly.
B. Cross-Region Transformation Algorithm
Due to the small number of missing samples in the collected
ACPCs dataset, there is a problem of imbalance between
positive and negative samples, which will cause over-fitting.
Therefore, to avoid the above problems, it is necessary to
enhance the collected image data to achieve the purpose of

WANG et al.: SWANet WITH DUAL-BRANCH STRUCTURE FOR DETECTION OF ACPCs

Fig. 3. Pipelines of CRTA. The input image is divided into six equally sized
subregions. The random function f and probability matrix p are used for
exchanging subregions. Optimize parameters θ through loss function L.

expanding the data. Compared with only using data augmentation methods such as color transformation, this article can
change the pixel distribution of the whole image by using the
above local region transformation method, so that the network
pays more attention to the difference between the missing
area and the normal area, thereby improving the generalization
ability of the model.
Before initiating the data augmentation step, it is essential to
extract the object region from the collected images to facilitate
subsequent subregion swapping. As illustrated in the figure,
the input image I is set with dimensions H × W and divided
into m × n areas with each area sized ((H/m), (W/n)),
where m = 2 and n = 3. The specific process is shown in
Fig. 3.
Each subregion Ri, j is defined by its row i and column j
indices and can be specifically expressed as
 
  
H
H
: (i + 1) ·
Ri, j = I i ·
m
m
 
 
W
W
j·
: ( j + 1) ·
.
(1)
n
n
Following this, two different subregions (i 1 , j1 ) and (i 2 , j2 )
are randomly selected, ensuring they are distinct. This selection process can be mathematically expressed as
(i 1 , j1 ) ∼ Uniform(1, m) × Uniform(1, n)
(i 2 , j2 ) ∼ Uniform(1, m) × Uniform(1, n)
(i 1 , j1 ) ̸ = (i 2 , j2 ).

(2)

A swap operation S is defined, where the selected areas
Ri1, j1 and Ri2, j2 are exchanged. The image after swapping,
I ′ , is represented as
I ′ (Ri1 , j1 ) = Ri2 , j2
I ′ (Ri2 , j2 ) = Ri1 , j1

(3)

with other areas remaining unchanged.
The swap position selection function f is defined as
(i 1 , j1 ), (i 2 , j2 ) = f ( p; θ), where p is a probability matrix
representing the likelihood of each area being selected, learned
through training network parameters θ.
Finally, a loss function L is defined based on the L2 loss,
which minimizes the pixel-wise difference between the transformed image I ′ and the target image I . It is formulated
as: θ
L(θ) = ∥I ′ −I ∥2

(4)

5027713

Algorithm 1 Random Region Exchange Module
1: Input: Image I of size H ×W , divided into m ×n regions,
network parameters θ
2: Output: Augmented image I ′
3: Divide I into regions Ri, j where i ∈ {1, . . . , m} and
j ∈ {1, . . . , n}:


H
W
W
H
: (i + 1) · , j ·
: ( j + 1) ·
Ri, j = I i ·
m
m
n
n
4:
5:
6:

Generate probability matrix p using the network f (p; θ )
Randomly select two regions (i 1 , j1 ) and (i 2 , j2 ) based
on p such that (i 1 , j1 ) ̸ = (i 2 , j2 )
Perform region exchange:
I ′ (Ri1 , j1 ) = Ri2 , j2
I ′ (Ri2 , j2 ) = Ri1 , j1

7:
8:
9:

Keep other regions unchanged
Compute the loss L(θ ) using I ′ and I
Update θ to minimize the loss:
θ ← θ − η · ∇θ L(θ )

10: Return: Augmented image I ′

where I is the object image, guiding the network to learn
how to enhance data through region swapping and improve
the model’s generalization capability.
To avoid the disruption of data distribution consistency
caused by random region transformations, we supervise the
similarity between regions before and after transformation
based on the aforementioned mathematical model. The specific
process is detailed in Algorithm 1, where the transformation
parameters θ are set to be learned through the network. This
adaptive transformation parameter learning approach prevents
excessive region transformations that could lead to abnormal
data distribution, ensuring the expansion of samples while
maximizing the similarity between the original and augmented
samples.
C. Sliding Window Affinity
To make the network learn the location of the missing area
in ACPCs more quickly, we use a new method to calculate
the similarity between the object pixel area and the nonobject
pixel area, that is, the SWA method. The calculation result
of the similarity of different regions is affinity. The sliding
window size of the sliding affinity module is set to be 5 × 5,
and the sliding step size is 1. First, the local window of 5 ×
5 in the upper left corner of the feature map is selected. In the
feature map part of the selected local window, linear mapping
is performed to obtain the Q and the K , and the local affinity is
obtained by multiplying Q and K . Finally, the local affinity
is mapped to the original position of the feature map. The
calculation process is shown in Fig. 4.
The feature map of 28 × 28 sizes obtained after feature
fusion is connected to the sliding affinity module. The window
slides on the original feature map according to the step size.
The feature map selected by the sliding window continues

5027713

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 4. Pipelines of SWA. A 5 × 5 local window in the feature map is
selected and linearly mapped to obtain Q and K , from which the local affinity
is computed and mapped back to the original position. The sliding window
traverses the feature map with a stride of 1, repeatedly computing and mapping
the local affinity. For overlapping regions, affinities are multiplied, ultimately
generating a complete affinity map.

to calculate the local affinity and is also mapped to the
corresponding position of the feature map. If there is an
overlapping part, the affinity is multiplied. Then, repeat the
steps of sliding, calculating affinity, and mapping to the feature
map until the sliding is completed, and the affinity map of the
entire feature map is obtained.
Let f be the original feature map, w f and h f be the width
and height of f , respectively, and the feature map of each
local window divided by f is
f i j = f [5i : 5i + 5/5, 5 j : 5 j + 5/5]
i = 0, 1, . . . , w f − 5, j = 0, 1, . . . , h f − 5.
The local affinity diagram calculated by SWA is

p 
affi( f i j ) = softmax Q × K T / dk .

(5)
(6)

(7)

Among them, Q, K , and V are obtained by the linear
transformation of the characteristic map f
Q = wq f i j
K = wk f i j
V = wv f i j .

(8)
(9)
(10)

Finally, the affinity map of the characteristic map f is
obtained as
X
Affi( f ) =
affi( f i j ) × αi j .
(11)

Fig. 5. Pipelines of HFP. The proactive layer and the supporting layer features
undergo linear transformations, with the supporting layer generating queries
(Q) and the proactive layer generating keys (K ) and values (V ). A multihead
self-attention mechanism captures the feature relationships, focusing on subtle
differential regions. The output features are processed through a feedforward
network and normalization layers.

layer features. This approach allows the network to effectively
learn distinguishing characteristics for each region, thereby
improving the model’s ability to detect subtle differences in
the assembly areas.
As illustrated in Fig. 5, the features are first processed
through their respective linear layers to ensure that each
set undergoes appropriate transformation before the attention
computation. A multihead CA mechanism is then employed,
where the supporting layer features are used to generate
queries (Q), while the proactive layer features produce keys
(K ) and values (V ). This configuration enables the network to learn the relationships between the proactive layer
and the supporting layer, allowing it to focus on regions
where the differences, though subtle, are crucial. The use of
the self-attention mechanism aids the network in capturing
long-range dependencies, which is particularly beneficial in
identifying the anomalies related to missing components in
ACPC assembly. The output features are subsequently processed by a feedforward network and normalization layers
to ensure that the parsed features maintain a high level of
discriminative power. This design significantly enhances the
model’s performance in distinguishing between the proactive
layer and the supporting layer, especially in environments
where the assembly regions closely resemble the background.
E. Loss Function
To jointly optimize both classification and bounding box
regression, we combine focal loss and CIoU loss using a
weighted sum. The total loss function is defined as

i, j

Among them, αi j is the weight coefficient, which determines
the proportion of local affinity in the affinity map at each
position.
D. Heterogeneous Feature Parsing
HFP is intended to address the challenges associated with
the high similarity between ACPC assembly regions and
their background, a similarity that complicates the detection
of missing components. This resemblance makes it difficult
for traditional methods to accurately distinguish between the
regions. The core design principle of the HFP module lies in
processing the heterogeneous proactive layer and supporting
layer features separately, followed by the application of an
attention mechanism to prioritize the more salient proactive

Ltotal = λ1 Lfocal + λ2 LCloU

(12)

where Lfocal is the focal loss for classification, LCloU is the
CIoU loss for bounding box regression, and λ1 and λ2 are the
weights that control the tradeoff between the classification and
localization loss, respectively.
Focal loss is used to reduce the impact of easily classified
negative samples in ACPCs and focus more on hard-to-classify
positive samples. It reshapes the standard cross-entropy loss
by lowering the weight of correctly classified examples and
increasing the weight of misclassified or difficult examples.
The definition of focal loss is as follows:
Lfocal ( pt ) = −αt (1 − pt )γ log( pt )

(13)

based on empirical experience, we set αt = 0.25 and γ = 2.

WANG et al.: SWANet WITH DUAL-BRANCH STRUCTURE FOR DETECTION OF ACPCs

5027713

CIoU loss is used to improve the localization accuracy
of bounding boxes. This loss function not only considers
the overlap between the predicted and ground-truth boxes of
ACPCs but also takes into account their aspect ratios and the
distance between their center points. The definition of CIoU
loss is as follows:
LCloU = 1 − IoU +

ρ 2 (b, bg )
+ αv.
c2

(14)

Here, b and bg are the center points of the predicted and
ground-truth boxes, ρ is the Euclidean distance between these
points, c is the diagonal length of the smallest enclosing
box covering both the predicted and ground-truth boxes, v
measures the similarity of aspect ratios, and α is a positive
tradeoff parameter.
IV. E XPERIMENT

Fig. 6. ACPC image acquisition system using Basler CCD industrial camera,
demonstrating the process of flat placement for missing assembly detection.

In this section, we show the evaluation results of the
proposed method on the ACPC dataset, which validates the
effectiveness of our proposed method.
A. Dataset and Environment
This study utilized an ACPC’s image acquisition system,
with the collection process illustrated in Fig. 6: ACPCs were
placed flat on a platform and illuminated by a single LED
light source. In this system, a Basler ruL2098-10gc chargecoupled device (CCD) industrial camera was used as the
acquisition sensor, and a display screen was used for real-time
monitoring of the acquisition process. Images with missing
assembly are manually filtered out for the object box labeling.
Due to the presence of different production lines for ACPCs,
there is no single type of chip for missing assembly detection,
posing higher requirements for the missing detection network.
Fig. 7 shows two missed and nonmissed chip maps with
different backgrounds were selected for gray value detection,
respectively, and the results show that the gray values of the
missed and nonmissed maps with different backgrounds are
very close to each other, which illustrates the characteristics
of the dataset in which the differences between the missed and
nonmissed regions are small.
Through the ACPC’s image acquisition system and data
augmentation algorithms, the ACPC dataset was established.
The images in the ACPC dataset were uniformly resized to
2560 × 1920 pixels to ensure consistency in model training
and testing. The dataset contains 1228 labeled missing images,
with 983 used for training and 245 for testing. In the missing
images, the average pixel proportion of the missing area is 1%.
The experiment is carried out on the Linux Ubuntu
20.4 platform. The GPU is NVIDIA Tesla A100, and the
deep learning environment is python3.8 + pytorch1.8 +
cuda11.4. The learning rate is 0.0001, epoch is 100, and the
optimizer is Adam.
B. Evaluation Metrics
In this study, the training loss curves, mean average precision (mAP), frames per second (FPS), and other relevant
metrics are used to evaluate the performance of the model.

Fig. 7. Comparison of gray values between (a) and (b) missing and (c) and
(d) nonmissing areas of ACPCs on different backgrounds.

1) Training Loss Curves: The curve represents the variation
of the model’s performance metrics on the training set with
the number of training samples. It is a curve with dataset size
as the horizontal axis and model accuracy as the vertical axis.
By gradually increasing the dataset size and observing the
trend of accuracy change on the training set, the optimization
space and overfitting of the model can be known. The performance of the model can be improved by adjusting the model
complexity or obtaining more data.
2) Mean Average Precision: The average precision (AP)
can be obtained in object detection tasks by calculating the
area under the P–R curve, reflecting the average accuracy rate
for different recall cases. AP50 is one of the commonly used
metrics, and it represents the AP value when the intersection
over the union (IoU) threshold is 50%. In this article, AP50 is

5027713

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

TABLE I
P ERFORMANCE C OMPARISON OF VARIOUS D ETECTION M ETHODS FOR ACPC M ISSING A SSEMBLY D ETECTION BASED ON M AP AND FPS

used to evaluate the detection performance of our method. The
mAP is the average accuracy summation of all the categories
divided by all the categories. The AP and mAP for a particular
category i are calculated as follows:
Z 1
A Pi =
P(R) d R
(15)
0
N

m AP =

1 X
A Pi
N i=1

(16)

where P(R) is the mapping relationship between P and R and
N is the total number of categories.
3) Frames Per Second: FPS indicates the inference speed of
the model, measured by the number of image frames processed
per second.
4) Params: Params denotes the parameters of the object
detection model.
5) GFLOPs: GFLOPs represent the computational complexity of the model, measured in billions of floating-point
operations.
C. Comparison With SOTA Methods
To demonstrate the effectiveness of our method on ACPCs,
we compared it with the current SOTA feature similarity-based
methods, including Faster RCNN [51], FCOS [52], RetinaNet
[53], and Swin Transformer [37]. The experimental results
are shown in Table I. To fully ensure the validity of the
results, the values in the table represent the mean and standard
deviation from fivefold cross-validation. All methods were
trained and tested in the same environment, and the results
indicate that our method outperforms the others. Specifically,
in the missing assembly detection task, we achieved the
best results in mAP50, mAP75, mAP50:95, and mAR50:95
(mean average recall at different thresholds). Fig. 8 shows
the training loss curves of the proposed method and other
methods. According to the comparison results, our method
achieved performance comparable to the best training curve
method, indicating better generalization on the ACPC test set.
We believe that when the randomness of the missing position is
strong, the features obtained by the SWA in this article exhibit
higher discrimination. This is because the feature embedding
vector of the missing position enhances the distinction from
the background through affinity, thereby improving the detection and localization of defects. Table I further compares
computational efficiency. Although Swin Transformer achieves
higher FPS, its computational cost is significantly higher. Our
method maintains optimal accuracy while reducing Params

Fig. 8.

Training loss curve comparison.

and GFLOPs by 15.8% and 44.6%, enhancing efficiency and
practicality.
To visually illustrate the detection efficacy of the model,
input test images were randomly chosen as depicted in
Fig. 9(a), with the visual outcomes contrasted with those of
other methods presented in Fig. 9(b)–(f). Enlargements of
the missing position and its adjacent pixels are positioned in
the upper left corner of each image. It is evident that our
method yields a higher single-image prediction probability and
a finer delineation of the detection box location compared to
other methods. This is attributed to SWA enhancing the pixel
connectivity via affinity, thereby ensuring that pixels in the
missing area secure a superior feature representation, which
leads to more precise positioning of the detection frame and
a discrimination probability that approaches 1.
To further highlight the network’s capability to precisely
identify areas of missing installation, the test images mentioned above were selected, and the feature maps resulting
from feature fusion were visualized, as shown in Fig. 10. In the
resulting visualization feature maps, areas that tend toward red
indicate a higher attention level by the network, suggesting that
these areas are more likely to be detected as missing parts
areas. The visualization analysis results clearly demonstrate
that the perception ability of the network model proposed in
this study significantly surpasses that of other comparative
methods. In contrast, the latter methods exhibit excessive
attention to normal areas and weaker recognition capability
for missing parts areas, indicating these network models’
inadequate performance in distinguishing between missing
parts areas and normal areas. Furthermore, this phenomenon is
attributed to the effectiveness of the SWA module within our
network model. The SWA module enhances the correlation
among pixels within missing parts areas, making the feature
representation of these areas more pronounced and thus more

WANG et al.: SWANet WITH DUAL-BRANCH STRUCTURE FOR DETECTION OF ACPCs

Fig. 9.

5027713

Visualization and detection results. (a) Original images. (b) Swin Transformer. (c) Faster RCNN. (d) FCOS. (e) Retinanet. (f) Ours.

easily recognized and located by the network. Consequently,
it can be concluded that the network model proposed in this
study demonstrates higher accuracy and precision in locating
missing parts areas on chips.

TABLE II
A BLATION R ESULTS OF D IFFERENT C OMPONENTS

D. Ablation Experiment
1) Different Components Proposed: To rigorously validate
the effectiveness of the proposed method, ablation experiments
were conducted to compare the contributions of each component. As a control, the CRTA was replaced with a randomly
replicated and pasted alternative. The experimental results,
as shown in Table II, indicate that the CRTA provided an
exceptionally robust data foundation. Building on this, the
SWA further enhanced the model’s representational capacity
through affinity, while the HFP improved the discriminative
power between the proactive layer and the supporting layer.
2) Results for Different Input Images: To evaluate the
impact of different input image resolutions on detection
results, images of various resolutions were fed into the network. The results, as presented in Table III. At a resolution of
224, all metrics demonstrated relatively low performance, particularly with map75 and map50:95 values of 0.544 and 0.507,
respectively. However, as the input size increased, performance
progressively improved, reaching its peak at a resolution
of 1300 × 800. At this resolution, map50, map50:95, and
mar50:95 achieved the highest values of 0.985, 0.743, and
0.782, respectively, indicating superior detection accuracy
and robustness. Additionally, although the input sizes of
896 × 896 and 1792 × 1792 showed similar performance in

TABLE III
R ESULTS FOR D IFFERENT I NPUT I MAGES

some metrics, the overall performance at 1300 × 800 was
the most outstanding, aligning well with the COCO dataset.
On the one hand, this resolution is closer to the actual
data distribution, helping to eliminate extraneous redundant
information. On the other hand, this size fully leverages the
multiscale characteristics of the network structure.

5027713

Fig. 10.

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Visualization effects of feature maps. (a) Original images. (b) Swin Transformer. (c) Faster RCNN. (d) FCOS. (e) Retinanet. (f) Ours.

E. Robustness Experiment
In the actual assembly process, due to changes in the site
environment or aging of equipment after long-term operation,
noise interference may occur when acquiring ACPC images.
To cope with new noises that may be generated in actual
production, it is necessary to verify the robustness of ours.
The original test set was randomly introduced into four groups
of different types of noise, and the strength of each group
of noise was compared with each other. The specific test
results are shown in Table IV. Among them, the strong noise
group includes Gaussian noise with a standard deviation of
10, salt-and-pepper noise with a ratio of 0.007, Poisson noise
with an average incidence rate of 25, and speckle noise
with a parameter of 0.05. The weak noise group includes
Gaussian noise with a standard deviation of 5 and a ratio of
0.005, salt-and-pepper noise, Poisson noise with an average
incidence rate of 2, and speckle noise with a parameter
of 0.01.
The results show that the different noises introduced in
the test set will cause a drop in detection accuracy of the
proposed method, but it is still within the acceptable range.
Under the most extreme perturbation of strong salt-and-pepper
noise, the one with the most change only dropped by 0.124.
The proposed method has good environmental adaptability and
can cope with various disturbances that randomly appear in the
actual assembly inspection process. Strong noise visual effects
are shown in Fig. 11. The images in the test set are randomly
selected, added with the above strong noise, and sent to the

network for detection, and the detection effect of the model
under the noise is intuitively displayed.
To verify the robustness of different models, the test set was
added with two sets of salt-and-pepper noise with different
intensities and then sent to different models for comparison.
It can be seen from Table IV that salt-and-pepper noise has
the greatest influence on the accuracy of the model compared
with other noise. Therefore, this experiment is representative.
The results are shown in Table V. For single-stage detection
methods such as FCOS and RetinaNet, the quality of feature
extraction has a great influence on the final results, so it is
difficult to cope with inclement noise. The Swin Transformer
and Faster RCNN, respectively, enhance the feature extraction
and candidate box generation, so the declining accuracy is
slightly better than the previous two methods. Under the
same extreme conditions, the accuracy of our model decreases
the least. The correlation between pixels is enhanced by
the proposed SWA. Even if the noise is added, the output
discriminative features can be output stably.
F. Generalization Experiments
To further evaluate the applicability and detection efficacy of the network model proposed in this study across
various detection objects, the NPSS dataset was introduced
as a new object for conducting generalization performance
experiments. The NPSS dataset [35] is specifically designed
for identifying defects in nickel-plated punched steel strips,
comprising 1500 images of nickel-plated punched steel strip

WANG et al.: SWANet WITH DUAL-BRANCH STRUCTURE FOR DETECTION OF ACPCs

TABLE IV

TABLE VI

A NTI -I NTERFERENCE E XPERIMENT

C OMPARISON R ESULTS W ITH VARIOUS F RAMEWORKS
FOR THE NPSS DATASET (%)

Fig. 12.

Fig. 11.

5027713

Strong noise visual effect.

Visual results of the NPSS dataset using the proposed method.

TABLE VII
R ESULTS OF THE P ROPOSED M ODULE ON THE MVT EC DATASET (%)

TABLE V
ROBUSTNESS C OMPARISON E XPERIMENT

defects collected on-site with industrial cameras. This dataset
is categorized into five defect types: blind hole (BH), connecting hole (CH), rusty spot (RU), scratch (SC), and water spot
(WS), with each category containing 300 images. Due to the
use of image stitching technology, these images vary in size.
The experimental comparison results on the NPSS dataset
are presented in Table VI, the network model proposed in
this study demonstrates exceptional performance across all five
categories of nickel-plated punched steel strip defect detection
tasks, particularly ranking first in four of the defect detection
categories. In terms of the mean mAP metric, the method
proposed in this study significantly outperforms other comparative methods. These results validate the proposed network’s

excellent generalization capability, affirming its suitability for
a variety of detection scenarios. To intuitively demonstrate the
generalization ability of this method, the visual results of the
NPSS dataset under this method are shown in Fig. 12. It can
be seen that this article has good detection performance in
categories such as CH and BH, which have similar structures
to the ACPCs dataset proposed in this article. Although the
positioning is slightly flawed for irregular categories such as
rusty, it can still meet the needs of actual industrial production,
further fully verifying the generalization of this article.
The scarcity of defect data and the reliance on supervised
learning on labeled defect samples impose significant limitations on supervised methods for industrial defect detection.
As industrial defect inspection tasks become increasingly
diverse, exploring self-supervised learning-based defect detection has become particularly crucial. Therefore, this paper
further investigates the feasibility and adaptability of the core
module SWA within an anomaly detection framework.

5027713

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Given that SimpleNet is the latest SOTA model in the field
of anomaly detection and its network architecture facilitates
seamless integration of external modules, we select SimpleNet
as the anomaly detection baseline and incorporate the SWA
module into its structure. Specifically, SWA is inserted after
the backbone feature extractor and before the feature adaptor,
aiming to enhance feature discriminability. Meanwhile, SimpleNet’s loss mechanism remains unchanged to ensure training
stability and compatibility.
Comparative experiments conducted on the public dataset
MVTec, as shown in Table VII, demonstrate that while the
SWA-enhanced SimpleNet does not surpass the original model
in overall detection accuracy, it achieves a higher PRO score,
validating the effectiveness of the SWA module in anomaly
localization tasks and further confirming its potential for
unsupervised defect detection.
V. C ONCLUSION
In this study, the ACPC dataset was initially constructed.
To address the issue of sample imbalance, the data were
effectively expanded using the fast region transformation
method. Then, a missing assembly detection algorithm based
on local window affinity calculation is proposed to calculate
the similarity relationship between pixels, strengthen the internal relationship between pixels, highlight the pixel difference
between the missing area and the normal area, and use multiscale feature fusion to enhance the defect feature and improve
the discrimination of small object area features. Ultimately,
this approach demonstrated significant advantages over other
methods and fulfilled industrial production requirements. This
research provides a reference for the application of vision
technology in intelligent industrial production lines.
However, certain limitations exist and should be addressed
in future work. The method relies on a grid-based structural
prior, which may limit its applicability to more complex
and unstructured industrial assembly scenarios. Additionally,
the incorporation of the SWA model and a dual-branch
structure introduces additional computational overhead, which
may affect real-time performance in high-speed industrial
production lines. Future research should focus on enhancing
adaptability, optimizing computational efficiency, and broadening applicability to diverse industrial defect detection tasks.
R EFERENCES
[1] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Las Vegas, NV, USA, Jun. 2016, pp. 770–778.
[2] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural Inf.
Process. Syst., vol. 30, 2017, pp. 5998–6008.
[3] O. Badmos, A. Kopp, T. Bernthaler, and G. Schneider, “Image-based
defect detection in lithium-ion battery electrode using convolutional neural networks,” J. Intell. Manuf., vol. 31, no. 4, pp. 885–897, Apr. 2020.
[4] D. Li, D. Yang, L. Li, L. Wang, and K. Wang, “Electrochemical
impedance spectroscopy based on the state of health estimation for
lithium-ion batteries,” Energies, vol. 15, no. 18, p. 6665, Sep. 2022.
[5] Z. Cui, L. Kang, L. Li, L. Wang, and K. Wang, “A hybrid neural network
model with improved input for state of charge estimation of lithium-ion
battery at low temperatures,” Renew. Energy, vol. 198, pp. 1328–1340,
Oct. 2022.
[6] W. Zhao, F. Chen, H. Huang, D. Li, and W. Cheng, “A new steel defect
detection algorithm based on deep learning,” Comput. Intell. Neurosci.,
vol. 2021, pp. 1–13, Mar. 2021.

[7] R. Wang et al., “Development of an improved YOLOv7-based model
for detecting defects on strip steel surfaces,” Coatings, vol. 13, no. 3,
p. 536, Mar. 2023.
[8] Y.-J. Cha, W. Choi, and O. Büyüköztürk, “Deep learning-based crack
damage detection using convolutional neural networks,” Comput.-Aided
Civil Infrastruct. Eng., vol. 32, no. 5, pp. 361–378, May 2017.
[9] A. Choudhary, T. Mian, S. Fatima, and B. K. Panigrahi, “Fault diagnosis of electric two-wheeler under pragmatic operating conditions
using wavelet synchrosqueezing transform and CNN,” IEEE Sensors J.,
vol. 23, no. 6, pp. 6254–6263, Mar. 2023.
[10] T. Zhang, S. Zhong, W. Xu, L. Yan, and X. Zou, “Catenary insulator
defect detection: A dataset and an unsupervised baseline,” IEEE Trans.
Instrum. Meas., vol. 73, pp. 1–15, 2024.
[11] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Self-supervised
learning for anomaly detection and localization,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit. (CVPR), Nashville, TN, USA,
Jun. 2021, pp. 9659–9669.
[12] J. Zhu, Q. Pang, S. Li, S. Tian, J. Li, and Y. Li, “ADDet: An efficient multiscale perceptual enhancement network for aluminum defect
detection,” IEEE Trans. Instrum. Meas., vol. 73, pp. 1–14, 2024.
[13] Y. Zheng, W. Lyu, C. Wang, Q. Guo, D. Zhou, and W. Xu, “Efficient
conflict-filtered network for defect detection,” IEEE Trans. Instrum.
Meas., vol. 72, pp. 1–14, 2023.
[14] L. Gao, J. Zhang, C. Yang, and Y. Zhou, “Cas-VSwin transformer:
A variant Swin transformer for surface-defect detection,” Comput. Ind.,
vol. 140, Sep. 2022, Art. no. 103689.
[15] Q. Luo, J. Su, C. Yang, W. Gui, O. Silvén, and L. Liu, “CAT-EDNet:
Cross-attention transformer-based encoder–decoder network for salient
defect detection of strip steel surface,” IEEE Trans. Instrum. Meas.,
vol. 71, pp. 1–13, 2022.
[16] L. Zhang, S.-F. Yan, J. Hong, Q. Xie, F. Zhou, and S.-L. Ran,
“An improved defect recognition framework for casting based on DETR
algorithm,” J. Iron Steel Res. Int., vol. 30, no. 5, pp. 949–959, May 2023.
[17] J. Wang, Q. Li, J. Gan, H. Yu, and X. Yang, “Surface defect detection via
entity sparsity pursuit with intrinsic priors,” IEEE Trans. Ind. Informat.,
vol. 16, no. 1, pp. 141–150, Jan. 2020.
[18] J. P. Yun, D. Kim, K. Kim, S. J. Lee, C. H. Park, and S. W. Kim, “Visionbased surface defect inspection for thick steel plates,” Opt. Eng., vol. 56,
no. 5, May 2017, Art. no. 053108.
[19] G. K. Nand, Noopur, and N. Neogi, “Defect detection of steel surface using entropy segmentation,” in Proc. Annu. IEEE India Conf.
(INDICON), Pune, India, Dec. 2014, pp. 1–6.
[20] N. Neogi, D. K. Mohanta, and P. K. Dutta, “Defect detection of steel
surfaces with global adaptive percentile thresholding of gradient image,”
J. Inst. Eng. India, B, vol. 98, no. 6, pp. 557–565, Dec. 2017.
[21] J. Kittler, R. Marík, M. Mirmehdi, M. Petrou, and J. Song, “Detection
of defects in colour texture surfaces,” in Proc. IAPR Workshop Mach.
Vis. Appl. (MVA), Kawasaki, Japan, Dec. 1994, pp. 558–567.
[22] K. Y. Song, J. Kittler, and M. Petrou, “Defect detection in random colour
textures,” Image Vis. Comput., vol. 14, no. 9, pp. 667–683, Oct. 1996.
[23] W. Wen and A. Xia, “Verifying edges for visual inspection purposes,”
Pattern Recognit. Lett., vol. 20, no. 3, pp. 315–328, Mar. 1999.
[24] J. Chen and A. K. Jain, “A structural approach to identify defects in
textured images,” in Proc. IEEE Int. Conf. Syst., Man, Cybern., vol. 1,
Beijing, China, Aug. 1988, pp. 29–32.
[25] F. Timm and E. Barth, “Non-parametric texture defect detection using
Weibull features,” Proc. SPIE, vol. 7877, pp. 150–161, 2011.
[26] J. Yang et al., “Development of an optical defect inspection algorithm
based on an active contour model for large steel roller surfaces,” Appl.
Opt., vol. 57, no. 10, p. 2490, 2018.
[27] H. Wang, J. Zhang, Y. Tian, H. Chen, H. Sun, and K. Liu,
“A simple guidance template-based defect detection method for
strip steel surfaces,” IEEE Trans. Ind. Informat., vol. 15, no. 5,
pp. 2798–2809, May 2019.
[28] F. Pernkopf, “3D surface inspection using coupled HMMs,” in Proc.
17th Int. Conf. Pattern Recognit. (ICPR), 2004, pp. 223–226.
[29] X.-C. Yuan, L.-S. Wu, and Q. Peng, “An improved Otsu method using
the weighted object variance for defect detection,” Appl. Surf. Sci.,
vol. 349, pp. 472–484, Sep. 2015.
[30] A. S. Tolba and H. M. Raafat, “Multiscale image quality measures for
defect detection in thin films,” Int. J. Adv. Manuf. Technol., vol. 79,
nos. 1–4, pp. 113–122, Jul. 2015.
[31] P. Zhu, Y. Cheng, P. Banerjee, A. Tamburrino, and Y. Deng, “A novel
machine learning model for eddy current testing with uncertainty,” NDT
& E Int., vol. 101, pp. 104–112, Jan. 2019.

WANG et al.: SWANet WITH DUAL-BRANCH STRUCTURE FOR DETECTION OF ACPCs

[32] A. Wronkowicz, K. Dragan, and K. Lis, “Assessment of uncertainty
in damage evaluation by ultrasonic testing of composite structures,”
Compos. Struct., vol. 203, pp. 71–84, Nov. 2018.
[33] Y. Shu, B. Li, and H. Lin, “Quality safety monitoring of LED chips using
deep learning-based vision inspection methods,” Measurement, vol. 168,
Jan. 2021, Art. no. 108123.
[34] P. Lu, J. Jing, and Y. Huang, “MRD-Net: An effective CNN-based segmentation network for surface defect detection,” IEEE Trans. Instrum.
Meas., vol. 71, pp. 1–12, 2022.
[35] Y. Liang, J. Li, J. Zhu, R. Du, X. Wu, and B. Chen, “A lightweight
network for defect detection in nickel-plated punched steel strip images,”
IEEE Trans. Instrum. Meas., vol. 72, pp. 1–15, 2023.
[36] J. Li, R. Du, J. Zhang, J. Zhu, H. Xu, and M. Cai, “Autofeeding system
for assembling the CBCs on automobile engine based on 3-D vision
guidance,” IEEE Trans. Instrum. Meas., vol. 70, pp. 1–13, 2021.
[37] W. Zhu, H. Zhang, C. Zhang, X. Zhu, Z. Guan, and J. Jia, “Surface defect
detection and classification of steel using an efficient Swin transformer,”
Adv. Eng. Informat., vol. 57, Aug. 2023, Art. no. 102061.
[38] Q. Zhang, J. Lai, J. Zhu, and X. Xie, “Wavelet-guided promotionsuppression transformer for surface-defect detection,” IEEE Trans.
Image Process., vol. 32, pp. 4517–4528, 2023.
[39] H. Zhou, R. Yang, R. Hu, C. Shu, X. Tang, and X. Li, “ETDNet: Efficient
transformer-based detection network for surface defect detection,” IEEE
Trans. Instrum. Meas., vol. 72, pp. 1–14, 2023.
[40] H. Yu, D. Liu, Z. Zhang, and J. Wang, “A dynamic transformer network
with early exit mechanism for fast detection of multiscale surface
defects,” IEEE Trans. Instrum. Meas., vol. 72, pp. 1–10, 2023.
[41] V. Zavrtanik, M. Kristan, and D. Skocaj, “DRÆM—A discriminatively
trained reconstruction embedding for surface anomaly detection,” in
Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Montreal, QC, Canada,
Oct. 2021, pp. 8310–8319.
[42] N.-C. Ristea et al., “Self-supervised predictive convolutional attentive
block for anomaly detection,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. (CVPR), New Orleans, LA, USA, Jun. 2022,
pp. 13566–13576.
[43] N. Madan et al., “Self-supervised masked convolutional transformer block for anomaly detection,” IEEE Trans. Pattern Anal.
Mach. Intell., vol. 46, no. 1, pp. 525–542, Jan. 2024, doi:
10.1109/TPAMI.2023.3322604.
[44] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler,
“Towards total recall in industrial anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), New Orleans,
LA, USA, Jun. 2022, pp. 14298–14308.
[45] Y. Liu et al., “AMP-Net: Appearance-motion prototype network assisted
automatic video anomaly detection system,” IEEE Trans. Ind. Informat.,
vol. 20, no. 2, pp. 2843–2855, Feb. 2024.
[46] Y. Liu et al., “Memory-enhanced spatial–temporal encoding framework
for industrial anomaly detection system,” Expert Syst. Appl., vol. 250,
Sep. 2024, Art. no. 123718.
[47] D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1705–1714.
[48] S. Wang, C. Lv, Z. Zhang, and X. Wei, “Dual-branch learning with
prior information for surface anomaly detection,” IEEE Trans. Instrum.
Meas., vol. 72, pp. 1–11, 2023.
[49] X. Liu et al., “SimpleNet: A lightweight network for industrial defect
detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), 2023, pp. 20402–20411.
[50] X. Li et al., “PromptAD: Learning prompts with only normal samples
for few-shot anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2024, pp. 16848–16858.
[51] S. Ren, K. He, R. Girshick, and J. Sun, “Faster R-CNN: Towards realtime object detection with region proposal networks,” in Proc. Int. Conf.
Adv. Neural Inf. Process. Syst., vol. 28, 2015, pp. 91–99.
[52] Z. Tian, C. Shen, H. Chen, and T. He, “FCOS: Fully convolutional
one-stage object detection,” in Proc. IEEE/CVF Int. Conf. Comput. Vis.
(ICCV), Oct. 2019, pp. 9627–9636.
[53] T.-Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, “Focal loss for
dense object detection,” in Proc. IEEE Int. Conf. Comput. Vis. (ICCV),
Oct. 2017, pp. 2980–2988.

5027713

[54] Z. Ge, S. Liu, F. Wang, Z. Li, and J. Sun, “YOLOX: Exceeding YOLO
series in 2021,” 2021, arXiv:2107.08430.
[55] A. Bochkovskiy, C.-Y. Wang, and H.-Y. Mark Liao, “YOLOv4: Optimal
speed and accuracy of object detection,” 2020, arXiv:2004.10934.
[56] M. Tan, R. Pang, and Q. V. Le, “EfficientDet: Scalable and efficient
object detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020, pp. 10781–10790.
[57] K. Duan, S. Bai, L. Xie, H. Qi, Q. Huang, and Q. Tian, “CenterNet:
Keypoint triplets for object detection,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis. (ICCV), Oct. 2019, pp. 6568–6577.
[58] Y. Wang et al., “LEDNet: A lightweight encoder–decoder network
for real-time semantic segmentation,” in Proc. IEEE Int. Conf. Image
Process. (ICIP), Sep. 2019, pp. 1860–1864.

Huimin Wang was born in 2000. She received the
B.S. degree in automation from Xiangtan University,
Xiangtan, China, in 2022, where she is currently
pursuing the M.S. degree in electronic information
with the School of Automation and Electronic Information.
Her main research interests include machine
vision, industrial image processing, and object
detection.

Bumin Meng (Member, IEEE) received the Ph.D.
degree in control theory and control engineering
from Hunan University, Changsha, China, in 2018.
He is currently an Associate Professor with the
College of Automation and Electronic Information, Xiangtan University, Xiangtan, China, and a
Researcher with the National Engineering Research
Center of RVC, Changsha. His current research
interests include intelligent system control, energy
management, and optimization.

Jiang Zhu received the M.S. and Ph.D. degrees
in control science and engineering from Hunan
University, Changsha, China, in 2005 and 2011,
respectively.
He is currently a Professor with the School of
Automation and Electronics Information, Xiangtan
University, Xiangtan, China. His current research
interests include intelligent information processing,
pattern recognition, and parallel distributed systems.

Rui Du (Graduate Student Member, IEEE) was born
in 1996. He received the B.S. and M.S. degrees
from Xiangtan University, Xiangtan, China, in
2017 and 2020, respectively. He is currently pursuing the Ph.D. degree with the National Engineering
Research Center of Robot Visual Perception and
Control Technology, Hunan University, Changsha,
China.
His research interests include multimodal perception.
PAPER_TEXT
