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
# [754] Multimodal Industrial Anomaly Detection via Attention-Enhanced Memory-Guided Network
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
编号：754
题名：Multimodal Industrial Anomaly Detection via Attention-Enhanced Memory-Guided Network
年份：2025
DOI：10.1109/tmm.2025.3632646
来源：IEEE Transactions on Multimedia
PDF：paper/10.1109_TMM.2025.3632646.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\754.txt
- 原始字符数：66192
- 本次发送字符数：66192
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 28, 2026

1133

Multimodal Industrial Anomaly Detection via
Attention-Enhanced Memory-Guided Network
Shuaibo Liu , Graduate Student Member, IEEE, Xiaoli Luan , Senior Member, IEEE, and Yueyang Li

Abstract—Anomaly detection is a key technology in quality
control for automated production lines. Currently, 2D-based
anomaly detection methods fail to identify geometric structure
anomalies in products. To address this limitation, this paper
proposes a multimodal anomaly detection model using 3D
point clouds and RGB images. To ensure the single-domain
inference capability of each modality, we design an attentionenhanced dual memory bank to separately store local point
cloud features and RGB features. The attention mechanism
enhances the informativeness and discriminability of the feature
descriptors, significantly improving the data quality in the
memory bank. During the inference phase, the local point cloud
features in the dual memory bank guide the RGB features in
calculating anomaly scores in the 2D modality. This memoryguided approach strengthens the correlation between information
across different modalities. Moreover, to improve the overall
segmentation precision of the model, we propose an anomaly
scoring scheme based on a weight map of signed distance values.
The final anomaly detection results are obtained by integrating
the advantages of point cloud data in geometric structure anomaly
detection and RGB data in color anomaly detection. Extensive
experiments demonstrate that the proposed method achieves
superior segmentation precision compared to other advanced
methods on the MVTec 3D-AD and Eyecandies datasets.
Index Terms—Anomaly detection, point cloud, signed distance
values, multimodal learning.

I. INTRODUCTION
ITH the development of artificial intelligence technology, anomaly detection (AD) in multimedia data has
been widely applied in fields such as medical image analysis [1], [2], industrial defect detection [3], [4], security monitoring [5], [6], and autonomous driving [7]. AD is a critical aspect
of industrial quality control, aiming at identifying anomalies in
a product to ensure the quality and reliability of the product [8].
Since abnormal samples are scarce and difficult to collect in
real-world manufacturing, unsupervised methods are primarily
employed to identify anomalies within industrial environments.

W

Received 23 December 2024; revised 14 April 2025; accepted 8 May 2025.
Date of publication 14 November 2025; date of current version 6 March 2026.
This work was supported by the National Natural Science Foundation of China
under Grant 61991402. The associate editor coordinating the review of this
article and approving it for publication was Vania Vieira Estrela. (Corresponding
author: Xiaoli Luan.)
Shuaibo Liu and Xiaoli Luan are with the Key Laboratory of Advanced
Process Control for Light Industry (Ministry of Education), Jiangnan University, Wuxi 214122, China (e-mail: liushuaibo@stu.jiangnan.edu.cn; xlluan@jiangnan.edu.cn).
Yueyang Li is with the College of Internet of Things Engineering, Jiangnan
University, Wuxi 214122, China (e-mail: lyueyang@jiangnan.edu.cn).
Digital Object Identifier 10.1109/TMM.2025.3632646

Such methods are usually trained only on a large set of normal samples and the target samples are detected in the inference
stage. Currently, the majority of industrial anomaly detection
methods [9], [10], [11], [12], [13] are still based on RGB image
analysis. However, in many industrial scenarios, relying only
on color images makes it difficult to accurately identify anomalies [14]. Different lighting conditions may lead to false detections, while anomalies of geometric structure types may not
present variations in color. Therefore, effectively leveraging the
synergy between RGB and 3D information is crucial for improving the AD performance. However, using multimodal data for
AD also presents several challenges. First, different modalities
may provide conflicting information. An RGB image may show
a color anomaly, while the 3D data indicates that the geometric
structure is normal. Such inconsistencies can make it difficult
for the model to accurately identify anomalies. Moreover, different modalities are affected by different factors. RGB images
can be influenced by lighting conditions, while 3D data may
suffer from noise or missing points. These quality differences
may cause multimodal data to fail in accurately representing
anomalies.
The recently released MVTec 3D-AD dataset [15], as a benchmark resource, has greatly advanced the field of multimodal
anomaly detection [16], [17], [18]. AST [19] reduces the overgeneralization of anomalous samples by using an asymmetric
teacher-student network, but it relies on the role of RGB information and does not fully leverage the detection advantages
of 3D data, which limits its detection performance. To leverage the inferential advantages of each modality, MIAD [20]
achieves anomaly detection by comparing the differences between the features mapped through two cross-modal mapping
functions and those learned by the feature extractor. In addition, MIAD obtains three variants, MIAD-M, MIAD-S, and
MIAD-T, by pruning the network layers of the feature extractor.
However, they require designing complex training goals separately for each modality. Memory bank-based methods have
gained significant attention, as these approaches only need to
store features of normal samples during training without requiring complex training designs. BTF [14] attempts to improve
the utilization of multimodal data by connecting features from
two modalities into a memory bank. Nevertheless, directly connecting multimodal features overlooks potential interference between them, which can significantly impact detection performance. M3DM [21] adopts a hybrid fusion scheme to alleviate
the problem of interference among modalities. It constructs three
memory banks for each modality and fusion feature separately to

1520-9210 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

1134

strengthen the single-domain inference capability of the model.
Nonetheless, this approach results in substantial memory costs.
Shape-guided [22] reduces memory usage by constructing a dual
memory bank with two expert models. However, the direct guidance approach between the expert models does not ensure the
quality of the features stored in the memory bank, which directly
impacts the final detection performance.
To alleviate the issue of data quality in the memory bank,
we use attention-enhanced memory guidance to construct a
dual memory bank. Specifically, we use attention mechanism
to strengthen connections between multimodal data. The 3D
features guide the attention-enhanced RGB features, together
forming the dual memory bank. Although 3D features provide
geometric structural information about objects, in RGB images,
color variations in certain regions may exhibit more anomaly
potential than changes in 3D geometry. The attention mechanism effectively enhances the feature representation of these regions. The design provides two advantages. First, the attention
mechanism enhances the informativeness and distinctiveness of
feature descriptors, significantly improving data quality within
the memory bank. Second, it increases pixel-level alignment accuracy between modalities, which is crucial for detecting subtle anomalies. Meanwhile, we design a weighted map anomaly
scoring scheme based on signed distance values for point cloud
data and a cosine similarity scoring scheme for RGB data. The
above design ensures the single-domain inference capability of
each modality. For the final anomaly localization, we first map
the RGB score distribution to align with the 3D score distribution, and then select the larger value at each pixel location as the
final pixel-level anomaly score. The above operation effectively
combines the detection advantages from different modalities.
It is noteworthy that our method shows superior anomaly detection and segmentation performance on the MVTec 3D-AD
benchmark, maintaining competitive results even at low false
positive rate (FPR) settings.
The contributions of this study can be summarized as follows:
r This study proposes an unsupervised multimodal industrial
anomaly detection method based on an attention-enhanced
memory-guided network. The method effectively combines the advantages of RGB and 3D data for anomaly
detection, addressing the performance limitations inherent
in single-modality approaches.
r This study employs attention mechanism to improve the
data quality in the memory bank, thereby enhancing the
pixel-level correspondence accuracy between multimodal
data during the memory-guided process.
r An anomaly scoring scheme based on a weight map of
signed distance values is proposed in this paper, which
effectively solves the problem of poorly localized regions
with weakly expressed anomalies. This greatly improves
the final detection and segmentation precision of the model.
r To the best of our knowledge, the proposed method
achieves state-of-the-art performance in anomaly segmentation on the MVTec 3D-AD dataset and Eyecandies
dataset. Even under high precision requirements, it still
demonstrates leading segmentation results.

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 28, 2026

The rest of this paper is organized as follows: Section II provides a review of related works. Section III presents our method.
Section IV conducts the experiments. Finally, Section V concludes the paper and discusses the limitations of the proposed
methods.
II. RELATED WORK
A. 2D Industrial Anomaly Detection
The public availability of the MVTec AD dataset [23]
has significantly contributed to the development of 2D industrial anomaly detection research. Common approaches include reconstruction-based [24], [25], [26], [27] and feature
embedding-based [28], [29], [30], [31] methods. For reconstruction methods, regions where the reconstructed image differs significantly from the input image are considered as the
location of the real anomalies. On this basis, in order to enable the model to learn anomalous features during training, researchers employ data augmentation techniques [32], [33] that
introduce pseudo-anomalies into normal images. Knowledge
distillation [34], [35] is based on a teacher model to train student networks for image reconstruction or feature extraction.
Anomaly localization is achieved by comparing the representation differences across the networks. Feature embedding methods aim to transform the original data into a new representation space that facilitates anomaly detection. Normalization
flows [28] employ invertible transformations to map data features to a normal distribution. This process allows normal and
anomalous samples to exhibit distinguishable probability density distributions in the embedding space. Visual-language models identify anomalies by calculating the similarity between images and textual descriptions [36]. The use of learnable prompts
can effectively enhance model performance [37], [38]. Methods
based on pre-trained networks and memory banks [39] often
face memory issues and computational burdens. PatchCore [12]
stores local features of normal samples in a memory bank and
then locates anomalies by comparing the similarity between the
target sample and the stored features. Inspired by this approach,
we applied the memory bank method to multimodal anomaly
detection tasks and achieved excellent performance.
B. Multimodal Industrial Anomaly Detection
Research [14] shows that effectively combining RGB and 3D
information leads to significantly better anomaly detection performance than using only RGB data. With the release of the
MVTec 3D-AD dataset [15], 3D industrial anomaly detection
has become a new research focus. The study that published the
dataset also offered baseline models based on GAN, AE, and
variational models, each trained on 3D data represented by voxel
grids or depth maps. 3D-ST [18] proposes a student-teacher
framework, where the teacher network encodes local geometric descriptions from patches to locate geometric anomalies in
point cloud data. BTF [14] examines the role of 3D information
in anomaly detection tasks, revealing the potential advantages of
combining RGB and 3D information for anomaly localization.

LIU et al.: MULTIMODAL INDUSTRIAL ANOMALY DETECTION VIA ATTENTION-ENHANCED MEMORY-GUIDED NETWORK

1135

Fig. 1. Diagram of the inference process. The proposed method consists of three main parts: (1) 3D signed distance function model predicts the signed distance
values of the local features in the point cloud, generating an anomaly score map for the 3D data. PointNet is a pre-trained 3D feature extractor, and the NIF model is
a multi-layer perceptron used to represent local 3D shapes. (2) 2D feature association model uses Wide-ResNet50-2 to extract RGB features. Multi-dimensional
attention enhances the detailed representation of the RGB feature map. The guided RGB features are obtained through the mapping of the SDF features. Finally,
an anomaly score map for the RGB data is produced. (3) Attention-enhanced dual memory banks store the normal features of each modality during the training
phase. M3D stores local 3D features, while M2D retains the attention-enhanced and guided RGB features. The quality of the stored data impacts the final model’s
performance.

However, if the advantages of multimodal data are not fully
integrated, performance may be lower than when using only
RGB data. For example, AST [19] and EasyNet [40] primarily
rely on RGB features to identify anomalies, while the contribution of 3D features is limited. In these cases, directly combining RGB and 3D features can reduce model performance,
as 3D features may be viewed as interference to RGB features.
Therefore, effectively integrating the advantages of multimodal
data is crucial for improving anomaly detection performance.
DRAIN [41] employs a lightweight MLP and a dual-attention
information entropy fusion strategy within a dual-reconstruction
network to enhance feature extraction and integration. Existing methods fail to fully ensure the single-domain inference
capability of each modality. Inspired by this, we design an
attention-enhanced memory-guided network that retains the advantages of single-modal detection while improving the quality
of data in the memory banks. The multi-dimensional attention
mechanism [42] with its representational advantages in modeling across three dimensions, enables the model to better distinguish between normal and anomalous instances. In addition,
the correlation between the information in different modalities
is strengthened by utilizing 3D local features to guide the RGB
features. Finally, efficient integration of the advantages of each
modality is achieved by mapping the anomaly scores to the same
distribution and then by taking the maximum value for each
pixel.

TABLE I
REFERENCE TABLE OF KEY NOTATIONS AND VARIABLES IN THIS PAPER

the attention-enhanced dual memory bank is constructed during
the training phase and utilized in the inference phase to calculate
anomaly scores across different modalities. The construction
processes of the memory banks for each modality are described
separately in Sections III-A and III-B, while their roles during
inference are detailed in Section III-C. The anomaly scoring
scheme based on a weighted map further helps the model achieve
more accurate anomaly segmentation results, as described in
Section III-C2. The inference diagram of the proposed method
is shown in Fig. 1. The key notations and variables used in this
paper, along with their definitions, are detailed in Table I.

III. METHOD
The proposed method consists of three main components: a
3D signed distance function model, a 2D feature association
model, and an attention-enhanced dual memory bank. Notably,

A. 3D Signed Distance Function Model
The 3D signed distance function model detects anomalies
by focusing on local geometric features. As shown in Fig. 2,

1136

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 28, 2026

B. 2D Feature Association Model

Fig. 2.

Diagram of the 3D signed distance function model.

PointNet [43] and neural implicit functions (NIF) [44] are used
to capture 3D local structural information. The design of the
model is driven by two core principles: anomalies are typically
reflected in local rather than global features, and learning local
geometric features offers better scalability.
Concretely, the entire point cloud is divided into multiple 3D
local patches, and each patch undergoes local feature learning.
Each patch is composed of 500 points sampled from the point
cloud, and PointNet is used to extract their feature vectors f ,
which represent the local geometric structure. The NIF model of
the multilayer perceptron architecture is denoted as ψ, which can
be used for the anomaly detection task after the below training.
Following the approach by Ma et al. [45], a set of query points
Q = {q1 , q2 · · · qi } is sampled near the surface of each 3D local
region. These query points, along with the feature vectors f
extracted by PointNet, are input into the NIF model ψ. The
model then predicts their signed distance values {s1 , s2 · · · si }.
The process of predicting the signed distance s of each query
point q relative to the local surface is represented as:
Ψ,f

qi ∈ Q −−→ s = ψ (q; f )

(1)

Each pair {ψ, f } forms a signed distance function (SDF) that
measures the local surface geometry of the point cloud. The
NIF model predicts the signed distance s for each query point q
through the process described above. ψ minimizes the distance
between the pulled points and the actual surface points during
the training process achieved by the pulling loss, which enables
the model to learn accurate local geometric features. The loss is
defined as follows:
Lpull =

I


1
2
t − ti 2
I i=1 i

(2)

where I represents the total number of query points. ti is the
actual nearest neighbor point of qi in the point cloud P. ti is the
pulled query point’s position. The pulling process is expressed
by the equation below:
ti = qi − s ×

Δs
Δs2

(3)

where Δs represents the gradient, which is the derivative of s
with respect to the position of the query point q.
In summary, through the above process, the model gains the
ability to characterize normal local geometric features, and it
can effectively identify abnormal features in the inference phase.
After training the 3D SDF model, all local region feature vectors
{f } are stored in a memory bank M3D . This process implicitly
encodes all “normal” local geometric representations.

The 2D feature association model relies on the interrelationship between 3D data and corresponding RGB images. Based
on the previously developed 3D SDF model, the mapping relationship between SDF and RGB features is established using
pixel-level coordinate information from the data. Specifically,
the goal of the 2D feature association model is to construct an
SDF-guided memory bank, denoted as M2D , for reconstructing
the normal patterns of RGB features. As shown in Fig. 3, for
each 3D patch feature outputted by PointNet (in blue), we map
the coordinates of 500 points within its local region onto a 2D
plane to locate the associated RGB region (marked by a dashed
red circle). Additionally, we expand the associated RGB region
by a 2-pixel neighborhood (yellow area surrounding the red circle). This strategy effectively enhances the model’s ability to
capture color variations and texture details. Ultimately, multiple
RGB feature vectors (in light pink) associated with each SDF
feature are stored in the memory bank M2D . M3D and M2D
together form the attention-enhanced dual memory bank.
Fig. 4 illustrates how the input feature maps are processed
through the three separate paths of the attention module. In the
top path, the feature map is first rotated 90◦ counterclockwise
around the H-axis to form an intermediate feature map F̆W .
To simulate deep dependencies between channels and spatial
dimensions, F̆W undergoes a squeeze transformation to obtain
the aggregated feature map F̂W . Subsequently, F̂W is processed
through an excitation transformation to capture spatial feature
interactions, resulting in the feature weight map F̃W . These feature weight maps are then processed by a sigmoid function to
yield the attention weight map AW , which is combined with


F̆W to generate the enhanced feature map FW
. Finally, FW
is
◦
rotated 90 clockwise around the H-axis to match the shape of
the original input feature map, resulting in the final feature map

. The process described above is represented by the followFW
ing equation:
F̆W = P MH (F )

(4)

F̂W = Tsq (F̆W ), F̃W = Tex (F̂W )

(5)


AW = σ(F̃W ), FW
= AW ⊗ F̆W

(6)


−1

= P MH
(FW
)
FW

(7)

where P MH (·) represents a 90◦ counterclockwise rotation
−1
(·) represents the corresponding
around the H-axis, and P MH
inverse rotation. Tsq (·) and Tex (·) denote the squeeze and excitation transformations, respectively, and σ represents the sigmoid
activation function. The middle path operates similarly to the top
path. The bottom path focuses on channel interactions. Initially,
the feature map F is mapped to F̆C . Then, F̆C undergoes squeeze
and excitation transformations to form the aggregated feature
map F̂C and the feature weight map F̃C . Subsequently, F̃C is
processed by the sigmoid function to obtain the channel-specific
attention weight map AC , which scales F̆C to generate the enhanced feature map FC . Finally, FC is remapped to form FC .
The above process can be described by the equations below:
F̆C = IM (F )

(8)

LIU et al.: MULTIMODAL INDUSTRIAL ANOMALY DETECTION VIA ATTENTION-ENHANCED MEMORY-GUIDED NETWORK

1137

Fig. 3. Attention-enhanced dual memory banks. The 3D SDF model stores feature vectors {f } of all 3D patches in the memory bank M3D . Each patch corresponds
to a specific region in the RGB feature map, generating a dedicated dictionary. All RGB dictionaries guided by patch information are stored in the memory bank
M2D . M3D and M2D together form the dual memory banks utilized during inference. Notably, the RGB feature map is refined through multi-dimensional
attention, which significantly improves the data quality in the memory banks.

Fig. 4. Illustration of the multi-dimensional attention mechanism. The architecture contains three branches. The top branch and the middle branch are concerned
with capturing feature interactions in the spatial dimensions W and H, respectively. While the bottom branch focuses on capturing interactions between channels.
⊗ denotes the element-wise multiplication operation and ⊕ denotes the element-wise summation operation. This design strengthens the refined representation of
features by efficiently integrating information from different dimensions.

F̂C = Tsq (F̆C ), F̃C = Tex (F̂C )

(9)

AC = σ(F̃C ), FC = AC ⊗ F̆C

(10)

FC = IM (FC )

(11)

where IM (·) refers to the identity mapping function. The multidimensional attention mechanism enhances the learning and representational capacity of RGB features through direct averaging
aggregation across three branches, thereby significantly improving the pixel-level correspondence precision between 3D and
RGB features. Furthermore, the enhancement of data quality
within the memory bank positively contributes to the model’s
performance.
C. Inference Phase of the Proposed Model
Based on the above process, we utilize the 3D signed distance function model, the 2D feature association model, and the
attention-enhanced dual memory bank to identify anomalies in
the test sample x. The schematic of the inference phase is presented in Fig. 1, with the following steps:

1) Feature Extraction: PointNet and Wide-ResNet50-2 are
used to extract all patch-level SDF and RGB features from the
test sample x. The SDF feature vectors are denoted as {f˜}. The
multidimensional attention mechanism models attention across
channels, height, and width, enhancing the expressive power of
the RGB feature map. Pixels related to at least one SDF feature in
{f˜} are considered the foreground of the RGB image. The RGB
feature vectors associated
with the SDF features after attention
...
are denoted as { f }.
2) Inference of the 3D Signed Distance Function Model: For
each SDF in {f˜}, find 10 nearest neighbors in the M3D to form a
feature dictionary and perform sparse coding to obtain approximate features {fˆ}. The purpose of sparse coding is to represent the input features {f˜} as a sparse linear combination of
the nearest neighbor features. This allows the original features
{f˜} to be approximated by a few neighboring features, achieving a sparse representation. Since sparse coding uses normal
features in M3D as basis vectors, the sparse representation can
accurately describe normal features, facilitating the distinction
between normal and anomalous features. For each patch of x,
compute the signed distance values of all 3D points {q̂} using

1138

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 28, 2026

the patch-reconstructed {fˆ}, denoted as s = ψ(q̂; fˆ). Since in
the training phase, the NIF model has learned to represent normal 3D local features. In the testing phase, a signed distance
value of 0 predicted by the NIF model indicates normal features, while non-zero signed distance values are considered to
be an indication of anomalies. Both positive and negative values
of s represent anomalies, with the absolute value of s indicating
the extent of the anomaly. Therefore, the absolute value of s is
considered as the score to quantify the anomaly. Our aim is to
detect all anomalies. If the difference in the absolute values of
s is too large, smaller s values may not be accurately localized.
This can affect the model’s final detection and segmentation
performance. To overcome this problem, we design an anomaly
scoring scheme based on a logarithmic weighting map of s. The
scheme is described in more detail below:
First, the absolute value of the signed distance s is taken for all
3D points {q̂}. Next, the logarithmic function log(1+x) is used as
a smoothing function to compute the weights. The logarithmic
function exhibits rapid growth for small x and slower growth
for large x, which reduces the magnitude differences of s and
enhances the focus on smaller s values. The above process can
be described as:
sL = |sL |

(12)

weight = log (1 + sL )

(13)

where L represents the index variable for traversing each s value.
Then traverse the s value at each position to update the score
map and weight map. When updating the score map, if the s
value at a position is smaller than the value at the corresponding
position in the score map, the score map is updated to the current
s value. This ensures that the s value at each position represents
the distance to the nearest surface. Meanwhile, to consider the
effects of all SDFs in {f˜}, the weight map is updated by accumulating logarithmic weights about s values for all the same
positions. Additionally, normalize the weight map to balance the
weights. The specific computational procedure described above
is shown below:
s_mapL = min (s_mapL , sL )
w_map(p) =

N

n=1

w_map = 

weight (p), p ∈ P

(14)
(15)

n

w_map
w_map + ε

(16)

where w_map(p) denotes the value of the weight map at pixel
location p. P indicates all pixel positions. N means the number
of patches containing pixel position p. ε is a small constant to
prevent division by zero. The final score map is obtained by
multiplying the original score map with the weight map. The
description above is shown below:
s_mapsdf = s_map ⊗ w_map

(17)

where ⊗ represents element-wise multiplication. s_mapsdf represents the anomaly score map obtained from the SDF model
using 3D data as input.
3) Inference of the 2D Feature Association Model: For all the
associated SDFs used to compute the approximate feature {fˆ}

in M3D , the concatenation of their associated RGB dictionaries
is taken in M2D to form a memory-guided RGB
... dictionary, denoted as D̂. For the RGB feature vectors in { f }, identify their
5 nearest neighbors from D̂ and obtain their sparse representations, denoted as {f¯}. Since cosine similarity focuses on the
direction rather than the magnitude of vectors, it better handles
the similarity of sparse vectors. Here,
... we use cosine similarity to
calculate the similarity between { f } and {f¯}, with lower similarity indicating a higher degree of anomaly. The calculation
process for the anomaly score map is as follows:
...
(18)
s_maprgb = 1 − cos( f , f¯)
...
... 
f · f¯
...  
(19)
cos f , f¯ = 
 f  f¯
where s_maprgb represents the anomaly score map obtained
from the 2D feature association model using 2D data as input.
4) Score Map Alignment: To fully utilize the inference advantage of each modality, we map the RGB score distribution
to the SDF score distribution. Then the anomaly scores in both
modalities are compared pixel by pixel. The larger value is taken
as the final anomaly response. To obtain the mapping relationship between the score distributions of different modalities, we
simulate the inference process of 25 randomly selected training
samples. And exclude itself from the nearest neighbor search
in the dual memory bank during the inference process. The purpose of the above operation is to get the weights and biases about
the mapping function. The specific computational procedure is
shown below:
sdfupper − sdflower
(20)
w=
rgbupper − rgblower
b = 3dlower − w × rgblower

(21)

where w is the weight of the mapping function, and b is the bias.
sdfupper and sdf lower are the 3-sigma ranges of the SDF distribution (mean ± 3 standard deviations). rgbupper and rgblower
are the 3-sigma ranges of the RGB distribution. The process of
applying the mapping function to the RGB score distribution is
described as follows:
s _maprgb = s_maprgb × w + b

(22)

where s _maprgb represents the new RGB score map after mapping. Finally, the scores of the score maps for each modality are
compared pixel by pixel and the larger value at each pixel position is selected as the pixel-level anomaly score. The above
process is shown below:


s_map(p)f inall = max s _map(p)rgb , s_map(p)sdf (23)
where s_mapf inall represents the final anomaly localization result after combining the advantages of the two modalities. In addition, we perform Gaussian blurring on all the anomaly score
maps involved in the above process to reduce noise and make the
score maps smoother. We sort the anomaly scores of all pixels
in the score map and use these values as candidate thresholds to
compute precision and recall, respectively. The F1 score is then
used to evaluate the balance between precision and recall. The
threshold corresponding to the highest F1 score is selected as

LIU et al.: MULTIMODAL INDUSTRIAL ANOMALY DETECTION VIA ATTENTION-ENHANCED MEMORY-GUIDED NETWORK

the final segmentation threshold. All pixels with anomaly scores
higher than this threshold are identified as anomalous regions.
Moreover, compared with using a single modality, incorporating both RGB and 3D data increases the model complexity
and memory usage. Specifically, when using only RGB data,
the proposed method requires FLOPs of 5.02 G and memory
of 1742 MB. When using only 3D data, it requires FLOPs
of 1.29 G and memory of 2104 MB. When both modalities
are used, the method requires FLOPs of 6.31 G and memory
of 3820 MB. In practical industrial scenarios, especially with
large-scale datasets, it is important to make a trade-off between
computational cost and detection performance. Flexible modality combinations can further enhance the effectiveness of the
proposed method.
IV. EXPERIMENTS
A. Dataset and Evaluation Metrics
1) Dataset: We evaluate the effectiveness of the proposed
method on two multimodal anomaly detection datasets. The
MVTec 3D-AD [15] dataset contains 10 different types of industrial objects, totaling 2656 training samples, 294 validation
samples, and 1197 test samples. The Eyecandies [46] dataset is
a synthetic dataset containing 10 categories of candies, with a
total of 10000 training samples, 1000 validation samples, and
4000 test samples. Each sample in these datasets provides 3D information that is precisely aligned with the corresponding RGB
pixels, allowing us to obtain the (x, y, z) coordinates at each
pixel. This spatial information, combined with the corresponding color data, enables us to effectively perform the detection
task. In this paper, we focus on utilizing the complementary relationship between RGB and 3D information to enhance anomaly
detection performance.
2) Evaluation Metrics: In this study, multiple evaluation
metrics are used to comprehensively assess the anomaly detection and segmentation performance of the model. Anomaly
detection performance is evaluated by calculating the area under the receiver operating characteristic curve (I-AUROC), with
higher I-AUROC values indicating better overall detection performance. Segmentation performance is evaluated using the
pixel-level area under the receiver operating characteristic curve
(P-AUROC) and the area under the per-region overlap curve
(AUPRO) [47]. AUPRO assesses how well the predicted regions align with the actual anomaly regions. Typically, an integration threshold of 0.3 for the false positive rate (FPR) is
used to calculate AUPRO (referred to as AUPRO@30% ). To
reduce the FPR in industrial applications and meet the demands
of high-precision scenarios, this study also employs AUPRO
with a more stringent 0.01 integration threshold (referred to as
AUPRO@1% ).

1139

the BTF method [14]. Then, since recent advances [44], [48]
in analyzing and modeling point clouds by dividing them into
multiple local regions have performed well, this study utilizes
farthest-point sampling (FPS) [49] to sample a set of points from
the original cloud. For each sampled point, we identify its K nearest neighbors within the receptive field to form local patches. In
addition, the resolution of the original point cloud and images is
resized to 224 × 224 using nearest-neighbor and bicubic interpolation [14]. To ensure full coverage of the point cloud while
allowing patches to share some neighborhood information, local
patches are set to be overlappable.
2) Parameter Settings: To ensure that overlapping local
patches collectively cover all points in the point cloud sample,
each 3D patch contains 500 points (K = 500), and the overlap
rate is set to 10. For a point cloud sample with approximately
7,750 points, this results in around 155 local patches, calculated
as “Overlap Rate × Total Number of Points ÷ K.” During SDF
model training, following the same settings as PCP [44], we
sample 20 query points around each real point. The learning
rate and batch size are set to 0.0001 and 32, respectively. All
experiments are conducted on a single NVIDIA GeForce RTX
3090, using the PyTorch 1.7.1 deep learning framework.
3) Training Process: The 3D signed distance function (SDF)
model employs pulling loss to minimize the distance between
pulled points and actual surface points. This enables the neural
implicit function (NIF) model to learn to predict signed distance values, thereby achieving an implicit representation of
local geometric information. The SDF features extracted from
normal point clouds by PointNet are stored in the memory
bank M3D . The RGB features of normal samples extracted by
Wide-ResNet50-2 are refined through the attention mechanism
and then stored in memory bank M2D under the guidance of SDF
features. Together, M3D and M2D form the attention-enhanced
dual memory bank.
4) Inference Process: During inference, for each SDF feature, we search for its 10 nearest neighbors in M3D . These
neighbors serve as basis vectors to reconstruct the input SDF
feature using sparse coding. The reconstructed feature is then
fed into the NIF model, where the pretrained SDF model computes the signed distance values for each local patch. The SDF
anomaly score map is obtained using the designed weighted
map anomaly scoring scheme. In M2D , all RGB features corresponding to the SDF features used for reconstruction in M3D
form a memory-guided RGB dictionary. For each input RGB
feature, we find its nearest neighbor in this dictionary and
reconstruct it using sparse coding. The RGB anomaly score
map is then obtained using the cosine similarity anomaly scoring scheme. Finally, the RGB scores are mapped to the 3D
score distribution. At each pixel location, the higher score
between the two modalities is selected as the final anomaly
response.

B. Implementation Details
1) Data Preprocess: The preprocessing of point clouds involves two main steps: background removal and local patch extraction. First, background point clouds in the raw data, which
interfere with modeling and analysis, are removed based on

C. Experiments Analysis
In this section, we provide a detailed comparison of the proposed method with other state-of-the-art approaches under different modal information as input. AST [19] effectively reduces

1140

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 28, 2026

TABLE II
IMAGE-LEVEL AUROC (I-AUROC) RESULTS OF VARIOUS METHODS FOR ANOMALY DETECTION PERFORMANCE ON THE MVTEC 3D-AD DATASET. THE BEST
RESULTS ARE SHOWN IN BOLD, AND THE SECOND-BEST RESULTS ARE UNDERLINED

the overgeneralization problem for anomalous samples but fails
to fully leverage the advantages of 3D data in geometric anomaly
detection. This limits its performance in multimodal scenarios. MIAD [20] achieves anomaly detection by learning two
cross-modal mapping functions, but it requires designing complex training objectives. MIAD-M, MIAD-S, and MIAD-T are
three variants obtained by pruning the network layers of the feature extractor in MIAD. BTF [14] improves the utilization of
multimodal data by connecting features from two modalities,
but it overlooks the potential interference between the modalities. M3DM [21] strengthens single-domain reasoning ability by
constructing three memory banks but leads to significant memory consumption. Shape-guided [22] reduces memory usage by
using dual memory banks but neglects the quality of features in
the memory banks.
Table II presents the anomaly detection performance using
I-AUROC, while Table III highlights the anomaly segmentation performance measured by AUPRO. Additionally, Table VI
provides a comparative analysis of segmentation performance,
focusing specifically on P-AUROC. 1) The proposed method
achieves the highest I-AUROC, outperforming M3DM [21] by
4.5% when using only 3D information for anomaly detection.

This result highlights the effectiveness of learning from overlapping local patches through PointNet [43]. For the segmentation task, the method achieves the best AUPRO in six data
subclasses and the second highest in four others, demonstrating
its strong generalization across different data categories, which
is essential for practical industrial applications. 2) In anomaly
detection using RGB information, since the proposed method
focuses on effectively combining multimodal information, i.e.,
RGB information guided by 3D information is used. However,
compared to AST [19], which directly uses RGB features for detection, the proposed method shows slightly lower performance
in I-AUROC. In contrast, for the segmentation task, the proposed approach achieves optimal results with 94.4% AUPRO,
attributed to multi-dimensional attention focused on learning the
details of RGB features and the application of cosine similarity
for sparse RGB feature computation. 3) In multimodal anomaly
detection using RGB + 3D, the proposed method achieves a
second-best I-AUROC of 95.6% , surpassing AST by 1.9% ,
and outperforming BTF [14] and M3DM, both of which utilize memory banks, by 8.3% and 1.1% , respectively. In terms
of segmentation performance, the proposed method also attains
optimal results. These results highlight the advantages of the

LIU et al.: MULTIMODAL INDUSTRIAL ANOMALY DETECTION VIA ATTENTION-ENHANCED MEMORY-GUIDED NETWORK

1141

TABLE III
AUPRO@30% RESULTS OF VARIOUS METHODS FOR ANOMALY SEGMENTATION PERFORMANCE ON THE MVTEC 3D-AD DATASET

TABLE IV
AUPRO@1% RESULTS OF VARIOUS METHODS FOR ANOMALY SEGMENTATION PERFORMANCE ON THE MVTEC 3D-AD DATASET

attention-enhanced memory-guided network, while demonstrating the effectiveness of the strategy that combines the strengths
of each modality’s detection based on memory-guided conditions. Table V presents the results of various multimodal methods on the Eyecandies dataset across multiple metrics. The results show that the proposed method achieves the best anomaly
segmentation performance, demonstrating its strong generalization ability across different detection targets.
Table IV demonstrates the actual performance of each method
in high precision requirement scenarios. The requirement of low
FPR has been the focus of industrial applications. The proposed
method achieves optimal and sub-optimal AUPRO@1% on 5
classes of data from MVTec 3D-AD, and the overall performance is 7.8% higher than that of BTF, 6.7% higher than that of
M3DM, and 0.6% higher than that of the current state-of-the-art

MIAD [20]. This study provides a booster study for the development of anomaly detection in high-precision industrial scenarios.
Fig. 5 presents a comparison of anomaly localization results
between the proposed method and Shape-guided [22]. The proposed method shows superior performance in reducing both
over-detection and missed detection, as illustrated by the score
and segmentation maps. Specifically, the Shape-guided method
exhibits multiple instances of over-detection in the second row
and a few minor cases of over-detection in the fourth row,
which the proposed method effectively mitigates. The results in
the third row highlight the advantage of the proposed method
in minimizing missed detections. Overall, the Shape-guided
method has two weaknesses. 1) The normal regions around the
target often have high anomaly scores. The proposed method

1142

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 28, 2026

TABLE V
MULTI-METRIC RESULTS OF VARIOUS MULTIMODAL METHODS ON THE EYECANDIES DATASET

Fig. 5. Qualitative results of the proposed method and other methods on the
MVTec 3D-AD dataset. From left to right: RGB anomaly image, ground truth,
score map and segmentation map of the Shape-guided method, and score map
and segmentation map of our method.

addresses this issue using an anomaly scoring scheme based on
a weight map of signed distance values. This effectively highlights anomalous regions while keeping anomaly scores lower in
normal areas. 2) There are over-detection and missed detection
issues. Our method enhances the informativeness and discriminability of feature descriptors through an attention mechanism.
This significantly improves the quality of data stored in the memory bank and helps mitigate these issues. More anomaly localization results for the proposed method are provided in Fig. 6.
D. Frame Rate and Memory Occupancy
In Table VI, we provide a detailed comparison of the proposed
method with previous advanced methods in terms of memory
footprint and inference speed (frames per second). In the field
of AD, methods that utilize memory banks have attracted much

attention due to the fact that accurate localization of anomalies
can be achieved with only normal samples. However, these methods depend heavily on the quality of the data used to construct
the memory bank. Performance can be adversely affected if the
input data is of low quality or contains noise and bias. This study
performs a series of preprocessing steps on point cloud data to
reduce potential interference. By learning and storing local features of sample data, it achieves a more detailed representation of
normal features, thereby enhancing the data quality of the memory bank. In addition, previous methods tend to identify anomalies by calculating the similarity between each anomalous sample and all normal samples when using a memory bank, which
can bring a huge computational burden. The attention-enhanced
memory-guided network proposed in this study addresses this by
only using the K most relevant nearest-neighbor features from
the memory bank for each anomaly feature, thereby improving
inference efficiency.
Compared to the M3DM method, which uses three memory banks, the proposed method reduces memory usage by
2706.12 MB and increases inference speed by 0.118 fps. The
BTF method attempts to integrate 3D features into the 2D
features provided by a frozen convolutional model (WideResNet50-2) [50], but this approach fails to fully leverage the
benefits of multimodality. The AST method, based on normalized flow, employs a teacher-student architecture that favors
faster inference; however, it uses 3D data only as an additional
input channel in a 2D network architecture, resulting in lower
performance than M3DM. MIAD detects anomalies by evaluating inconsistencies between learned features from feature
extractors and cross-modal mapped features, achieving faster
inference speeds. Compared with all these methods, the proposed approach outperforms others across various metrics, including I-AUROC, P-AUROC, AUPRO@30% , and the more
stringent AUPRO@1% . Fig. 7(a) and (b) clearly highlight the
advantages demonstrated by the proposed approach in anomaly
detection and anomaly segmentation. Importantly, the proposed
algorithm surpasses the previous state-of-the-art method MIAD
in the AD task. Moreover, our work can be reproduced using an

LIU et al.: MULTIMODAL INDUSTRIAL ANOMALY DETECTION VIA ATTENTION-ENHANCED MEMORY-GUIDED NETWORK

1143

Fig. 6. Anomaly localization results of the proposed method on the MVTec 3D-AD dataset. From top to bottom: RGB anomaly image, ground truth, and the
score map and segmentation map of our method.
TABLE VI
INFERENCE SPEED, MEMORY OCCUPANCY, AND AD PERFORMANCE ON THE MVTEC 3D-AD DATASET. INFERENCE SPEED
IS MEASURED IN FPS, AND MEMORY IN MB.

Fig. 7. Comprehensive comparison of multimodal anomaly detection methods in terms of anomaly detection performance (I-AUROC, as shown in subfigure
(a)), anomaly segmentation performance (AUPRO@1% , as shown in subfigure (b)), inference speed, and memory occupancy. The area of each circle represents
memory usage.

1144

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 28, 2026

TABLE VII
ABLATION RESULTS OF EACH COMPONENT OF THE PROPOSED METHOD ON
THE MVTEC 3D-AD DATASET IN TERMS OF I-AUROC,
AUPRO@30% , AND AUPRO@1% .

Fig. 9.

Ablation study of the attention mechanism.

TABLE VIII
ABLATION RESULTS ON THE EFFECTIVENESS OF THE THREE ATTENTION
BRANCHES ON THE MVTEC 3D-AD DATASET

Fig. 10.

Ablation study of the weight map.

TABLE IX
INFERENCE TIME, ANOMALY DETECTION PERFORMANCE, AND ANOMALY
SEGMENTATION PERFORMANCE WITH VARIOUS PATCH SIZE K SETTINGS ON
THE MVTEC 3D-AD DATASET

Fig. 8.
ods.

Qualitative results of different RGB anomaly score calculation meth-

NVIDIA GeForce RTX 3090, and more powerful hardware is
expected to further improve the frame rate.

TABLE X
ANOMALY DETECTION AND SEGMENTATION PERFORMANCE OF THE PROPOSED
METHOD UNDER FEW-SHOT SETTINGS ON THE MVTEC 3D-AD DATASET

E. Ablation Study
This section presents a detailed ablation study. Table VII
highlights the advantage of using cosine similarity over L2
distance for anomaly scoring. It also highlights the benefits of
the weighted map scoring scheme for anomaly segmentation and
the role of the attention mechanism in improving the quality of
feature data stored in the memory bank. Table VIII provides
a more detailed ablation study on the three attention branches.
Additionally, we present a more intuitive visual comparison of
ablation studies. Fig. 8 demonstrates the scoring superiority of
cosine similarity over L2 distance. By enhancing the representation of RGB features, the attention mechanism also improves the
data quality within the memory bank. Segmentation results in
Fig. 9 illustrate the attention mechanism’s significant contribution to detecting subtle anomalies (W/O represents without, W/
represents with). Fig. 10 compares the effectiveness of directly
using the absolute value of SDF as the anomaly score versus the
weight map approach for anomaly localization. Table IX provides a detailed analysis of patch sizes. While K=300 yields the
highest I-AUROC, K=500 offers the optimal balance between
inference speed and anomaly segmentation accuracy. In fact,

as the patch size increases, the inference efficiency of the proposed method gradually improves. However, this comes at the
cost of reduced model performance. For industrial deployment,
the patch size can be adjusted flexibly to adapt to the specific
requirements of different tasks.
F. Performance of Few-Shot Setting
We evaluate the proposed method under few-shot settings, and
the results are shown in Tables X. Specifically, we randomly select 5, 10, and 50 images from each category of the MVTec
3D-AD dataset as training data. The model is then tested on the
full test set to assess its anomaly detection and segmentation performance under few-shot conditions. Notably, in the 5-shot and
10-shot settings, our method still outperforms some approaches
that are not designed for few-shot scenarios. The few-shot nature
enables our method to better scale to practical applications.

LIU et al.: MULTIMODAL INDUSTRIAL ANOMALY DETECTION VIA ATTENTION-ENHANCED MEMORY-GUIDED NETWORK

1145

TABLE XI
ABLATION RESULTS OF THE PROPOSED METHOD’S MULTIMODAL DATA INPUT ARCHITECTURE ON AUPRO@30%

TABLE XII
COMPARISON OF THE COMPUTATIONAL COMPLEXITY, INFERENCE SPEED, AND
MEMORY OCCUPANCY OF THE PROPOSED METHOD USING SINGLE-MODAL
AND MULTIMODAL DATA AS INPUT ON THE MVTEC 3D-AD DATASET

Fig. 11. Qualitative results before and after integrating multimodal information. From left to right: anomaly image, ground truth, score map and segmentation map from the RGB branch, score map and segmentation map using only 3D
information, and score map and segmentation map after combining RGB and
3D. The results show that our method solves the problem of anomaly localization
failure caused by relying solely on a single modality.

G. Effectiveness of Multimodal Integration
This section provides a detailed analysis of the effectiveness of combining multimodal data. Fig. 11 illustrates the benefits of combining RGB and 3D information in the proposed
method, which effectively avoids the problem of failing to localize anomalies in the case of a single modality. The types of
anomalies are diverse. RGB information tends to work well at
identifying color defects in objects, but it does not work well
for holes in bagels with complex surfaces. In contrast, 3D information is typically effective for detecting spatial anomalies on
the test object. Therefore, effectively combining RGB and 3D
information is key to improving anomaly detection and localization performance. This study realizes the effective utilization
of multimodal information by merging the detection advantages
in the two modalities. Table XI presents AUPRO@30% results
for each single modality and after combining the multimodal
information. Table XII shows the computational complexity, inference speed, and memory occupancy of the models using single modal and multimodal data respectively. The results indicate
that, compared to single modal data, although multimodal data
requires more memory occupancy, it achieves superior performance by integrating the advantages of each modality. Fig. 12
shows the distribution of image-level scores for the “Dowel”
subclass under various modality conditions. In normal data,

Fig. 12. Distribution of anomaly detection scores before and after fusion on
the dowel subclass. The relative difference in image-level scores between normal
and abnormal data is enhanced after the 3D + RGB fusion, facilitating better
anomaly detection.

scores should ideally be lower than those of anomalous data.
After combining RGB and 3D information, the relative size of
the score distributions for normal and abnormal data is enlarged.
This will help to better identify anomalies.
V. CONCLUSION AND LIMITATIONS
In this paper, we propose a multimodal industrial anomaly detection method based on an attention-enhanced memory-guided
network. It leverages point cloud and RGB image data to provide
a more comprehensive and accurate solution for quality control in automated production lines. By designing an attentionenhanced dual memory bank, the single-domain inference ability of each modality is fully preserved. The score distributions
from different modalities are fused through score mapping, effectively combining the strengths of point cloud data for geometric anomaly detection and RGB data for color anomaly detection.

1146

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 28, 2026

Additionally, we propose an anomaly scoring scheme based on
a weight map of signed distance values, which further improves
segmentation precision of the model. On the MVTec 3D-AD
and Eyecandies datasets, our method achieves state-of-the-art
anomaly segmentation performance compared to other advanced
approaches. Even under stricter false positive rate settings, our
method maintains superior segmentation performance. In the
future, with the advancement of computing power and the increasing availability of multimodal data acquisition technologies, multimodal anomaly detection is expected to be widely
applied in various industrial fields, driving the development of
industrial quality inspection technologies.
Although the proposed method exhibits excellent AD performance, it still has some limitations. Memory-based approaches
to implement anomaly detection often bring unavoidable memory footprints, leading to some limitations in inference speed as
well. To address these issues, future work will focus on three
potential improvement directions. 1) Dynamic memory pruning: This technique removes memory features with low relevance to the current input during inference. It effectively reduces
memory usage while minimizing unnecessary computations. 2)
Lightweight attention module: This module has fewer parameters and lower computational costs. 3) Knowledge distillation:
A lightweight student network, distilled from a teacher network,
can be used as the feature extractor.

REFERENCES
[1] V. Wargnier-Dauchelle, T. Grenier, F. Durand-Dubief, F. Cotton, and M.
Sdika, “A weakly supervised gradient attribution constraint for interpretable classification and anomaly detection,” IEEE Trans. Med. Imag.,
vol. 42, no. 11, pp. 3336–3347, Nov. 2023.
[2] M. Liu, Y. Jiao, J. Lu, and H. Chen, “Anomaly detection for medical
images using teacher–student model with skip connections and multiscale
anomaly consistency,” IEEE Trans. Instrum. Meas., vol. 73, 2024, Art.
no. 2520415.
[3] C. Huang, Q. Xu, Y. Wang, Y. Wang, and Y. Zhang, “Self-supervised masking for unsupervised anomaly detection and localization,” IEEE Trans.
Multimedia, vol. 25, pp. 4426–4438, 2023.
[4] J. Li, R. Wu, S. Zhang, Y. Chen, and Z. Dong, “FASCNet: An edgecomputational defect detection model for industrial parts,” IEEE Internet
Things J., vol. 11, no. 4, pp. 6622–6637, Feb. 2024.
[5] P. Wu, W. Wang, F. Chang, C. Liu, and B. Wang, “DSS-Net: Dynamic
self-supervised network for video anomaly detection,” IEEE Trans. Multimedia, vol. 26, pp. 2124–2136, 2024.
[6] K. Xu, X. Jiang, and T. Sun, “Anomaly detection based on stacked sparse
coding with intraframe classification strategy,” IEEE Trans. Multimedia,
vol. 20, no. 5, pp. 1062–1074, May 2018.
[7] K. Doshi and Y. Yilmaz, “Fast unsupervised anomaly detection in traffic
videos,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. Workshops,
2020, pp. 624–625.
[8] J. Liu et al., “Deep industrial image anomaly detection: A survey,” Mach.
Intell. Res., vol. 21, no. 1, pp. 104–135, 2024.
[9] Y. Liang et al.„ “Omni-frequency channel-selection representations for
unsupervised anomaly detection,” IEEE Trans. Image Process., vol. 32,
pp. 4327–4340, 2023.
[10] Y. Guo, M. Jiang, Q. Huang, Y. Cheng, and J. Gong, “MLDFR: A multilevel features restoration method based on damaged images for anomaly
detection and localization,” IEEE Trans. Ind. Informat., vol. 20, no. 2,
pp. 2477–2486, 2024.
[11] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “Padim: A patch distribution modeling framework for anomaly detection and localization,” in
Proc. Int. Conf. Pattern Recog., 2021, pp. 475–489.
[12] K. Roth et al., “Towards total recall in industrial anomaly detection,” in
Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2022, pp. 14318–14328.

[13] X. Yao, C. Zhang, R. Li, J. Sun, and Z. Liu, “One-for-all: Proposal masked
cross-class anomaly detection,” in Proc. Conf. Artif. Intell., vol. 37, no. 4,
2023, pp. 4792–4800.
[14] E. Horwitz and Y. Hoshen, “Back to the feature: Classical 3D features
are (almost) all you need for 3d anomaly detection,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit., 2023, pp. 2968–2977.
[15] P. Bergmann, X. Jin, D. Sattlegger, and C. Steger, “The mvtec 3d-ad dataset
for unsupervised 3D anomaly detection and localization,” in Proc. 17th
Int. Joint Conf. Comput. Vis., Imag. Computer Graph. Theory Appl., 2022,
pp. 202–213.
[16] Y. Cao, X. Xu, and W. Shen, “Complementary pseudo multimodal feature
for point cloud anomaly detection,” Pattern Recognit., vol. 156, 2024, Art.
no. 110761.
[17] C. Bi, Y. Li, and H. Luo, “Dual-branch reconstruction network for industrial anomaly detection with RGB-D data,” Proc. SPIE Pattern Recognit.,
vol. 13180, 2024, Art. no. 1318033
[18] P. Bergmann and D. Sattlegger, “Anomaly detection in 3D point clouds
using deep geometric descriptors,” in Proc. IEEE/CVF Winter Conf. Appl.
Comput. Vis., 2023, pp. 2613–2623.
[19] M. Rudolph, T. Wehrbein, B. Rosenhahn, and B. Wandt, “Asymmetric student-teacher networks for industrial anomaly detection,” in Proc.
IEEE/CVF Winter Conf. Appl. Comput. Vis., 2023, pp. 2592–2602.
[20] A. Costanzino, P. Z. Ramirez, G. Lisanti, and L. Di Stefano, “Multimodal
industrial anomaly detection by crossmodal feature mapping,” in Proc.
IEEE Conf. Comput. Vis. Pattern Recognit., 2024, pp. 17234–17243.
[21] Y. Wang et al., “Multimodal industrial anomaly detection via hybrid fusion,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2023, pp. 8032–
8041.
[22] Y.-M. Chu, L. Chieh, T.-I. Hsieh, H.-T. Chen, and T.-L. Liu, “Shape-guided
dual-memory learning for 3D anomaly detection,” in Proc. 40th Int. Conf.
Mach. Learn., 2023, pp. 6185–6194.
[23] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Mvtec ad–a comprehensive real-world dataset for unsupervised anomaly detection,” in
Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2019, pp. 9592–9600.
[24] V. Zavrtanik, M. Kristan, and D. Skočaj, “Reconstruction by inpainting for
visual anomaly detection,” Pattern Recognit., vol. 112, Art. no. 107706,
2021.
[25] R. Zhang, H. Wang, M. Feng, Y. Liu, and G. Yang, “Dual-constraint
autoencoder and adaptive weighted similarity spatial attention for unsupervised anomaly detection,” IEEE Trans. Ind. Informat., vol. 20, no. 7,
pp. 9393–9403, Jul. 2024.
[26] Y. Luo and Y. Ma, “Anomaly detection for image data based on data
distribution and reconstruction,” Appl. Intell., vol. 53, no. 19, pp. 22500–
22510, 2023.
[27] X. Du et al., “Anomaly-prior guided inpainting for industrial visual
anomaly detection,” Opt. Laser Technol., vol. 170, 2024, Art. no. 110296.
[28] D. Gudovskiy, S. Ishizaka, and K. Kozuka, “CFLOW-AD: Real-time unsupervised anomaly detection with localization via conditional normalizing flows,” in Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis., 2022,
pp. 98–107.
[29] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, “Spot-the-difference
self-supervised pre-training for anomaly detection and segmentation,” in
Proc. Eur. Conf. Comput. Vis., 2022, pp. 392–408.
[30] X. Wu, G. Mao, and S. Xing, “Unsupervised anomaly detection in images
using attentional normalizing flows,” Eng. Appl. Artif. Intell., vol. 127,
2024, Art. no. 107369.
[31] M. Campos-Romero, M. Carranza-Garcıá, and J. C. Riquelme, “Advancing
unsupervised anomaly detection with normalizing flow and multi-scale ensemble learning,” Eng. Appl. Artif. Intell., vol. 137, 2024, Art. no. 109088.
[32] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, “Cutpaste: Self-supervised learning for anomaly detection and localization,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit., 2021, pp. 9664–9674.
[33] C. Zhao et al., “Incremental generative occlusion adversarial suppression network for person reid,” IEEE Trans. Image Process., vol. 30,
pp. 4212–4224, 2021.
[34] H. Deng and X. Li, “Anomaly detection via reverse distillation from oneclass embedding,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
2022, pp. 9737–9746.
[35] H. Zhang, S. Liu, S. Lu, L. Yao, and P. Li, “Knowledge distillation for unsupervised defect detection of yarn-dyed fabric using the system daerd: Dual
attention embedded reconstruction distillation,” Color. Technol., vol. 140,
no. 1, pp. 125–143, 2024.
[36] J. Jeong et al., “Winclip: Zero-/few-shot anomaly classification and segmentation,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2023,
pp. 19606–19616.

LIU et al.: MULTIMODAL INDUSTRIAL ANOMALY DETECTION VIA ATTENTION-ENHANCED MEMORY-GUIDED NETWORK

[37] Z. Gu et al., “Anomalygpt: Detecting industrial anomalies using large
vision-language models,” in Proc. AAAI Conf. Artif. Intell., vol. 38, no. 3,
2024, pp. 1932–1940.
[38] C. Zhao et al., “Learning domain invariant prompt for vision-language
models,” IEEE Trans. Image Process., vol. 33, pp. 1348–1360, 2024.
[39] R. Liu et al., “Memformer: A memory based unified model for anomaly
detection on metro railway tracks,” Expert Syst. Appl., vol. 237, 2024, Art.
no. 121509.
[40] R. Chen et al., “Easynet: An easy network for 3D industrial anomaly
detection,” in Proc. 31st ACM Int. Conf. Multimedia., 2023, pp. 7038–
7046.
[41] Z. Li, Y. Ge, X. Wang, and L. Meng, “3 D industrial anomaly detection via
dual reconstruction network,” Appl. Intell., vol. 54, no. 20, pp. 9956–9970,
2024.
[42] Y. Yu et al., “MCA: Multidimensional collaborative attention in deep convolutional neural networks for image recognition,” Eng. Appl. Artif. Intell.,
vol. 126, 2023, Art. no. 107079.
[43] C. R. Qi, H. Su, K. Mo, and L. J. Guibas, “PointNet: Deep learning on
point sets for 3D classification and segmentation,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit., 2017, pp. 652–660.
[44] B. Ma, Y.-S. Liu, M. Zwicker, and Z. Han, “Surface reconstruction from
point clouds by learning predictive context priors,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit., 2022, pp. 6326–6337.
[45] B. Ma, Z. Han, Y.-S. Liu, and M. Zwicker, “Neural-pull: Learning signed
distance functions from point clouds by learning to pull space onto surfaces,” in Proc. 38th Int. Conf. Mach. Learn., 2021, pp. 7246–7257.
[46] L. Bonfiglioli, M. Toschi, D. Silvestri, N. Fioraio, and D. De Gregorio,
“The eyecandies dataset for unsupervised multimodal anomaly detection
and localization,” in Proc. Asian Conf. Comput. Vis., 2022, pp. 3586–3602.
[47] P. Bergmann, K. Batzner, M. Fauser, D. Sattlegger, and C. Steger, “The
mvtec anomaly detection dataset: A comprehensive real-world dataset for
unsupervised anomaly detection,” Int. J. Comput. Vis., vol. 129, no. 4,
pp. 1038–1059, 2021.
[48] C. Jiang et al., “Local implicit grid representations for 3D scenes,” in Proc.
IEEE Conf. Comput. Vis. Pattern Recognit., 2020, pp. 6001–6010.
[49] Y. Pang et al., “Masked autoencoders for point cloud self-supervised learning,” in Proc. Eur. Conf. Comput. Vis., 2022, pp. 604–621.
[50] S. Zagoruyko and N. Komodakis, “Wide residual networks,” in Proc. Brit.
Mach. Vis. Conf., 2016, pp. 871–883.

Shuaibo Liu (Graduate Student Member, IEEE) received the M.S. degree in engineering from School of
Electronics and Information, Xi’an Polytechnic University, Xi’an, China, in 2024. He is currently working toward the Ph.D. degree with the Key Laboratory of Advanced Process Control for Light Industry
(Ministry of Education), School of Internet of Things
Engineering, Jiangnan University, Wuxi, China. His
research interests include deep learning and visual
anomaly detection.

1147

Xiaoli Luan (Senior Member, IEEE) received the
B.Sc. degree in industrial automation and the M.Sc.
and Ph.D. degree s in control theory and control engineering from Jiangnan University, Wuxi, China, in
2002, 2006, and 2010, respectively. In 2016, she was
a Visiting Professor with the University of Alberta,
Canada. She is currently a Professor with the School
of Internet of Things Engineering, Jiangnan University. She has authored or coauthored more than 80
articles in professional journals, conference proceedings, and technical reports in these related areas. Her
research interests include robust control and optimization of complex industrial process. She hosted and participated several research programs funded by
National Natural Science Foundation, and was a reviewer of a number of international journals.

Yueyang Li received the B.Sc. degree in textile engineering from the Wuxi Institute of Light Industry, Wuxi, China, in 1994, the M.Sc. degree in computer application technology and the Ph.D. degree
in light industry information technology and engineering from Jiangnan University, Wuxi, in 2004 and
2010, respectively. He joined the Department of Computer Science, Jiangnan University in 2004 and is currently an Associate Professor. From February to May
2005, he was a Research Assistant with the Department of Computing, Hong Kong Polytechnic University. From 2008 to 2009, he was a Visiting Scholar with the Medical Image
Processing Group, Department of Radiology, University of Pennsylvania. His
research interests inlcude machine learning, computer vision and its application
in industry.
PAPER_TEXT
