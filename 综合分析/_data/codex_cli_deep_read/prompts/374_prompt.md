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
# [374] Bi-Grid Reconstruction for Image Anomaly Detection
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
编号：374
题名：Bi-Grid Reconstruction for Image Anomaly Detection
年份：2025
DOI：10.1109/tip.2025.3644787
来源：IEEE Transactions on Image Processing
PDF：paper/10.1109_TIP.2025.3644787.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\374.txt
- 原始字符数：48553
- 本次发送字符数：48553
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

8599

Bi-Grid Reconstruction for Image
Anomaly Detection
Aimin Feng , Huichuan Huang , Guangyu Wei , and Wenlong Sun
Abstract—In the domain of image anomaly detection, significant progress has been made in unsupervised and self-supervised
methods with datasets containing only normal samples. Although
these methods perform well in general industrial anomaly detection scenarios, they often struggle with over- or under-detection
when faced with fine-grained anomalies in products. In this
paper, we propose GRAD: Bi-Grid Reconstruction for Image
Anomaly Detection, which utilizes two continuous grids to detect
anomalies from both normal and abnormal perspectives. In this
work: 1) Grids serve as feature repositories to assist in the
reconstruction task, achieving stronger generalization compared
to discrete storage, while also helping to avoid the Identical Shortcut (IS) problem common in general reconstruction methods.
2) An additional grid storing abnormal features is introduced
alongside the normal grid storing normal features, which refines
the boundaries of normal features, thereby enhancing GRAD’s
detection performance for fine-grained defects. 3) The Feature
Block Pasting (FBP) module is designed to synthesize a variety
of anomalies at the feature level, enabling the rapid deployment
of the abnormal grid. Additionally, benefiting from the powerful
representation capabilities of grids, GRAD is suitable for a unified
task setting, requiring only a single model to be trained for
multiple classes. GRAD has been comprehensively tested on
classic industrial datasets including MVTecAD, VisA, and the
newest GoodsAD dataset, showing significant improvement over
current state-of-the-art methods.
Index Terms—Image anomaly detection,
method, reconstruction method, grid sampling.

self-supervised

I. I NTRODUCTION
MAGE anomaly detection and localization aim to identify and precisely segment abnormal regions in images,
with applications spanning industrial inspection [1], medical
imaging [2], and video surveillance [3]. However, this task

I

Received 20 June 2025; revised 14 November 2025; accepted 10 December
2025. Date of publication 22 December 2025; date of current version
29 December 2025. This work was supported in part by the Fundamental Research Funds for Central Universities under Grant NJ2024031; in
part by the State Key Laboratory for Novel Software Technology, Nanjing
University Funding Project, under Grant KFKT2025B56; and in part by
the Collaborative Innovation Center of Novel Software Technology and
Industrialization. An earlier version of this paper was presented in part at
the Proceedings of IEEE International Conference on Multimedia and Expo
(ICME), in 2025 [DOI: 10.1109/ICME59968.2025.11209568]. The associate
editor coordinating the review of this article and approving it for publication
was Prof. Huanqiang Zeng. (Corresponding author: Aimin Feng.)
Aimin Feng is with the School of Computer Science and Technology,
Nanjing University of Aeronautics and Astronautics, Nanjing 211106, China,
also with the MIIT Key Laboratory of Pattern Analysis and Machine Intelligence, Nanjing 211106, China, and also with the State Key Lab for Novel
Software Technology, Nanjing University, Nanjing 210023, China (e-mail:
amfeng@nuaa.edu.cn).
Huichuan Huang, Guangyu Wei, and Wenlong Sun are with the School
of Computer Science and Technology, Nanjing University of Aeronautics
and Astronautics, Nanjing 211106, China (e-mail: hchuang@nuaa.edu.cn;
weiguangyu@nuaa.edu.cn; wenlong.sun@nuaa.edu.cn).
Digital Object Identifier 10.1109/TIP.2025.3644787

faces challenges due to the scarcity of abnormal samples and
the diversity of anomaly patterns, such as minor scratches
to significant structural damages in industrial production [4],
[5]. Under these challenges, there is an increasing interest in
developing un- and self-supervised methods.
In anomaly detection, self-supervised methods are often
categorized under unsupervised approaches. However, in this
paper, we explicitly distinguish self-supervised methods from
unsupervised ones, defining the latter as methods that exclusively utilize normal samples without incorporating synthetic
anomalies. Notable examples in unsupervised approaches
include PaDiM [5], SPADE [6] and PatchCore [7], which rely
on an external vector database to store features extracted from
normal samples. During inference, anomalies are identified by
calculating the Euclidean distance between the test sample and
its nearest neighbor in the database. Despite their effectiveness,
these methods suffer from limitations due to their discrete storage of features. This not only hampers generalization but also
necessitates the storage of a large number of diverse normal
features, leading to high spatial complexity and resourceintensive search operations.
To address the shortcomings of insufficient generalization
in the aforementioned methods, approaches such as MemAE
[8] and DAAD [9] have been developed. These methods
incorporate discrete repositories into the reconstruction task
to generate generalized normal features and detect anomalies
by comparing samples before and after reconstruction. By
leveraging attention mechanisms, these models gather diverse
normal features from the repository, resulting in stronger
robustness to test data and thus enhancing generalization
performance. However, controlling the training of generative
models remains challenging. Over-generalization can lead to
the IS issue, where the input sample is mapped too closely to
the reconstructed sample, as highlighted in UniAD [10].
To balance the generalization, CRAD [11] proposes using
continuous grids instead of discrete vector databases in the
reconstruction task. Compared to other methods [8] that rely
on vector databases to store numerous features and then
combine them for anomaly reconstruction, grid sampling
both enhances generalizatboion performance through interpolation techniques and reduces the risk of generating identical
anomaly features, effectively mitigating the IS problem.
Although the aforementioned unsupervised methods have
shown good performance, the boundaries of normal data they
define often lack sufficient accuracy due to the absence of
real anomaly data. This is particularly problematic when dealing with fine-grained defects, where over- or under-detection
frequently occurs. Additionally, thanks to the development

1941-0042 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

8600

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

overcoming the limitations of existing methods in detecting fine-grained anomalies.
II. R ELATED W ORK
This section reviews various unsupervised anomaly detection methods, including reconstruction-based, embeddingbased, and synthesis-based methods. It also discusses unified
anomaly detection frameworks that address the challenges of
multi-class scenarios and highlights the advantages of our
grid feature representation for efficient and effective anomaly
detection.
A. Unsupervised Anomaly Detection
Fig. 1. In the comparison of complex products and fine-grained anomalies,
our model shows significant advantages over other models.

of generative models, methods such as DFMGAN [12] and
AnomalyDiffusion [13] have emerged, capable of synthesizing
more effective and diverse anomalies.
Building on this, we propose GRAD, which introduces an
abnormal grid that stores abnormal features in addition to the
normal grid that stores normal features. This complements
the knowledge learned from accessible synthetic anomalies,
refines the boundaries of normal features, thereby enhancing
the model’s performance in detecting fine-grained anomalies
in complex products. As shown in Fig. 1, our model demonstrates significant improvements over previous methods in
handling more complex products and fine-grained anomalies.
Given that training models like DFMGAN and AnomalyDiffusion to synthesize realistic anomalies requires substantial
computational resources, we also designed the FBP module.
This module focuses on the efficiency, effectiveness, and
diversity of anomaly synthesis, synthesizing various shapes,
sizes, strengths, and positions of controllable anomalies at the
feature level to facilitate rapid training of available abnormal
grid.
Our comprehensive analysis confirms GRAD as an effective
AD solution, addressing the limitations of existing methods
and contributing to the integration of synthetic anomalies with
unsupervised approaches. The main contributions of this paper
are summarized as follows:
• We propose a novel anomaly classification and localization method called GRAD. This method introduces an
abnormal grid that incorporates knowledge from synthetic
anomalies to refine the boundaries of normal features,
significantly enhancing the detection performance for
fine-grained anomalies.
• We design a lightweight method for anomaly synthesis at
the feature level, called FBP, which allows flexible control
over the location, size, intensity, and shape of synthetic
anomalies.
• We evaluate GRAD on three image anomaly detection
datasets: MVTec AD [4], VisA [14], and GoodsAD
[15]. The results show that GRAD achieves top-tier
anomaly detection performance under a unified setting,

Regarding the various unsupervised anomaly detection
methods that have been proposed, they can be broadly categorized into three types:
a. Reconstruction-based methods: These methods assume
models trained on normal samples reconstruct normal areas
well but struggle with anomalies. Early efforts used various
generative models like AE [16], [17], [18], [19], [20], [21],
GAN [22], [23], [24], Transformer [25], [26], and Diffusion
Model [27] to learn the normal data distribution, attempting to
replicate input data, and detect anomalies through reconstruction errors.
b. Embedding-based methods: These methods extract and
store normal image representations from pre-trained networks,
identifying anomalies via feature comparison. SPADE uses a
multi-resolution semantic pyramid, PaDiM models the normal
class with multivariate Gaussian distributions, and PatchCore
employs greedy coreset subsampling for a memory-efficient
approach. Anomalies are detected through feature cataloging
and comparison.
c. Synthesis-based methods: These methods create anomalies on normal images, turning anomaly detection into
supervised learning. CutPaste [28] cuts and pastes patches randomly, DRÆM [29] uses Perlin noise for out-of-distribution
features, and NSA [30] merges scaled patches with Poisson
image editing. SimpleNet [31] adds Gaussian noise in the
feature space.
B. Unified Anomaly Detection
As illustrated in Fig. 2(a), traditional methods train separate
models for each object category. This approach becomes
impractical and resource-intensive in real-world scenarios
where there are numerous intra-class or inter-class instances.
Although these methods are effective for single-category
anomaly detection, the requirement for multiple models in
multi-class scenarios significantly increases both memory and
computational demands.
To solve the problem above, UniAD introduced a framework
with a hierarchical query decoder in a transformer. Learnable queries with Neighbor-Masked Attention were used to
prevent query features from attending to input features at
the same or adjacent locations, but performance was limited
due to lack of class-specific query designs. OmniAL [32]
advanced anomaly synthesis and localization using panelguided synthetic data, providing a unified model for all

FENG et al.: Bi-GRID RECONSTRUCTION FOR IMAGE ANOMALY DETECTION

8601

are XT rain and XT est , respectively, with XT rain containing
only normal samples and XT est including both normal and
abnormal samples. For a sample xi ∈ R3×H×W , we use a pretrained EfficientNet-B6 [44] on ImageNet to extract features
Φi ∼ Φ(xi ). Due to data bias in the pre-trained network [7],
[31], we adapt it by selecting intermediate layers. Through
experiments, we chose layers 3 and 4 from EfficientNet-B6
layers 1 to 5, denoted as φl,i ∼ Φ(xi ) ∈ RCl ×Hl ×Wl , where
l ∈ L = {1, 2, 3, 4, 5} represents the selected layers.
φaligned (xi ) = Concat({Resize(φl,i , (Hmax , Wmax ))|l ∈ L}).
Fig. 2. Comparison of Separated and Unified Task Settings: (a) In the
separated setup, models are trained separately for each category of products,
whereas in (b) the unified setup, a single, unified model is trained for all
categories.

objects. UCAD [33] developed a Continual Prompting Module (CPM) with a streamlined memory bank and integrated
Structure-based Contrastive Learning (SCL) with the Segment
Anything Model (SAM) for improved anomaly segmentation.
IUF [34] further eliminates memory bank dependency through
incremental learning, employing object-aware attention and
semantic compression to enhance adaptability for new objects.
CRAD uses the grid instead of a memory bank to store
continuous normal features, leveraging the powerful structural
representation capabilities of grids to manage diverse classes
within a single model.
C. Grid Feature Representation
In the evolution of neural fields or neural representations, grid-based representations of signals parameterized by
coordinate functions have proven effective across a range
of applications, such as image and video processing [35],
[36], 3D reconstruction [37], [38], and novel view synthesis
[39], [40], [41]. These grid structures efficiently capture highfrequency details without spectral bias [42], [43] and facilitate
effective feature generalization through continuous feature
spaces.
As stated above, CRAD uses a continuous grid for anomaly
detection, replacing discrete feature memory banks to improve
generalization and address the IS problem. Furthermore, it
combines global and local perspectives to capture structural features and detect anomalies across multiple classes,
making it ideal for unified anomaly detection. In terms of
computational complexity, the O(1) time complexity of grid
calculations also surpasses the O(n) time complexity associated with discrete methods.
III. M ETHODS
GRAD mainly consists of a Feature Extractor, a Bi-Grid
Reconstruction module, and an FBP module. In this section,
we will explain these three components in sequence and
provide details on our training and inference processes at the
end.
A. Feature Extractor
We redefined the feature extraction process as a preliminary step for our subsequent work. Training and test sets

(1)

Next, we align the feature maps from different levels to
the same size (Hmax , Wmax ), where Hmax and Wmax are the
maximum height and width for all feature maps, and finally
concatenate them along the channel dimension to obtain the
output features for this stage.
B. Bi-Grid Reconstruction
GRAD consists of a normal grid and an abnormal grid.
Normal grid is trained exclusively with normal samples and
serves as the primary reconstructor in the reconstruction task,
aiming to reconstruct input features into normal features
through grid sampling, regardless of whether the input features
are normal or abnormal. Abnormal grid serves as a specialized
knowledge base for learning anomalies and assists normal
grid in refining the boundaries of normal features during
anomaly detection. This collaboration enhances the model’s
performance in addressing fine-grained issues within complex
scenarios. In a self-supervised setting, abnormal grid is trained
with artificially synthesized anomalies during the training
process. In a supervised setting, it is trained using externally
available anomaly samples.
1) 2D Grid PSampling: Firstly, for the feature map
φaligned (xi ) ∈ R l∈L Cl ×Hmax ×Wmax obtained from the previous
stage, we need to transform each pixel of aligned feature map
into corresponding coordinates using convolutional layers with
a 1×1 kernel size, followed by a hyperbolic tangent activation
function, in order to perform grid sampling operations in the
next step. We define the coordinate mapping function fco (·):
v(xi ) = fco (φaligned (xi )) ∈ RCco ×Hmax ×Wmax .

(2)

In this work, we only use a 2D grid, so here Cco = 2.
Next, we use the coordinates obtained above to perform
sampling within the grid, the process is described as follows:
ϕ((x, y); G) =

N X
N
X

wi (x) · w j (y) · G(xi , y j ),

(3)

i=1 j=1

fG (xi ) = {ϕ((x, y); G)|(x, y) ∈ v(xi )},

(4)

where ϕ((x, y); G) : RCco → R l∈L Cl represents sampling
from the grid G using
the coordinates (x, y), and fG (xi ) :
P
RCco ×Hmax ×Wmax → R l∈L Cl ×Hmax ×Wmax performs grid sampling
for each pixel’s corresponding coordinates.
2) Normal Grid: PWe define a function to obtain local
coordinates, vl (·) : R l∈L Cl ×Hmax ×Wmax → RCco ×Hmax ×Wmax , which
generates pixel-wise coordinates based on the input features,
where Cco is the dimension of the generated coordinates,
P

8602

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

set to 2 in this work. Subsequently, based on the pixel-wise
obtained coordinates, normal features are sampled from the
Cco -dimensional normal local grid Gln , where each
P dimension
has a resolution of Rl and a channel count of l∈L Cl . The
l
equation
for the local representation, fG,n
(·) : RCco ×H×W →
P
C
×H×W
R l∈L l
, can be written as follows:

After obtaining the global features through grid sampling,
these features are reshaped to match the original shape of the
initial features. Subsequently, they are concatenated with the
local features to yield the final features of the abnormal grid:

l
fG,n
(xi ) = {ϕ((x, y); Gln )|(x, y) ∈ vl (xi )}.

4) Feature Fusion: For the two sets of features obtained
above, we employ element-wise addition for feature fusion,
resulting in preliminary reconstructed features x̂ipre rec .

x̂ipre rec = λ x̂i,n ⊕ (1 − λ) x̂i,a ,
(11)

(5)

Normal grid local representations correspond to normal
image patches. For abnormal patches, they are replaced by
similar context normal patches. For normal patches without
exact matches in training data, normal features are interpolated from nearby coordinates. Since the grid lacks abnormal
training features, abnormal patches are represented by the
best-matching normal features based on their coordinates,
preventing direct interpolation of abnormal features. This
approach effectively addresses the IS problem in existing
methods, which often suffer from IS due to attention-based
feature aggregation by similarity [8], [11], [45].
To capture global information, we integrate a supplementary
global grid within the
P normal grid framework. We introduce
a function vg (·) : R l∈L Cl ×Hmax ×Wmax → RCco to extract global
normal coordinates. Using these coordinates, we sample norg
mal features from the Cco -dimensional
P global normal grid Gn
with resolution Rg and feature depth
l∈L C l HW.PThe global
g
feature representation function fG,n
(·) : RCco → R( l∈L Cl )HW is
defined as follows:
g
fG,n
(xi ) = ϕ(vgn (xi ); Ggn ).

(6)

Following the sampling of global features from the grid and
reshaping them to match the original feature dimensions, we
concatenate these with the local features to obtain the final
features of the normal grid:
g
l
x̂i,n = fn (xi ) = C( fcat ( fG,n
(xi ), reshape( fG,n
))).

(7)

The concatenation operation, denoted as C(·), is performed
along the channel dimension
to merge the
P
P two sets of features.
Specifically, C(·) : R2 l∈L Cl ×H×W → R l∈L Cl ×H×W represents
a dimensionality reduction convolutional network. By integrating both local and global representations, the normal grid is
capable of capturing feature information of the input image
from various scale perspectives.
3) Abnormal Grid: The abnormal grid, similar to the
normal grid in coordinate mapping and sampling, receives
anomaly images and masks during training. It categorizes features into two classes within the grid space using the mask and
employs contrastive learning to increase the distance between
these classes. This aids in reconstructing known anomalies
during inference, guiding the normal grid to enhance reconstruction of anomaly parts.
The abnormal grid and the normal grid share the same
coordinate mapping function. The equations for the anomaly
local representation and the anomaly
P global representation,
l
l
denoted asP fG,a
(·) : RCco ×H×W → R l∈L Cl ×H×W and fG,a
(·) :
Cco
Cl )HW
(
l∈L
R →R
, can be written as follows:
l
fG,a
(xi ) = {ϕ((x, y); Gla )|(x, y) ∈ vl (xi )},

(8)

g
fG,a
(xi ) = ϕ(vga (xi ); Gga ),

(9)

g
l
x̂i,a = fa (xi ) = C( fcat ( fG,a
(xi ), reshape( fG,a
))).

(10)

where ⊕ denotes element-wise addition, and λ is a hyperparameter used to control the blending ratio.
In early production stages, abnormal samples are scarce. To
quickly train and deploy anomaly detection models, anomalies
need to be synthesized on normal samples. Previous methods
like Cutpaste and DRÆM crudely paste anomalies at the
image level, creating unrealistic results. While DFMGAN
and AnomalyDiffusion produce more realistic anomalies, they
require extensive resources. Therefore, we are considering
whether it is possible to design a lightweight method to quickly
synthesize anomalies.
C. Feature Block Pasting
The FBP module is designed to facilitate the rapid training
of an abnormal grid that is deployment-ready. Compared to the
method of adding Gaussian noise used by SimpleNet [31], the
anomalies synthesized using FBP are more diverse, resulting
in a trained abnormal grid that achieves superior performance.
We describe the FBP module as follows:
φ pse ano , mask = FBP(φnor , M, B, I, P),

(12)

where φ pse ano and mask represent the generated synthetic
anomalies and their corresponding annotation information,
respectively. It takes five parameters: the feature map φnor
obtained from a normal image through the pretrained backbone, and the parameters M, B, I, P which control the shape,
size, intensity, and position of the generated anomalies,
respectively.
Specifically, the FBP module operates by defining the
block size B, block intensity I, and block center coordinates
P = (xc , yc ). We generate the initialization mask M as M =
zeros(2B+1, 2B+1), a (2B+1)×(2B+1) matrix initialized to
zero. A random walk mask is created by selecting the initial
position (x0 , y0 ) = (B, B) and randomly choosing the number
of steps N from [B, 2B]. The random walk updates the position
as (xk+1 , yk+1 ) = (xk + ∆x, yk + ∆y) with ∆x, ∆y ∈ {−1, 0, 1},
marking the corresponding position in M as 1. Finally, we
initialize the block paste tensor T of size 1 × 1 × H × W
(initialized to zero), paste the block with intensity I at the
marked positions in M, apply Gaussian blur to obtain T blurred ,
and paste T blurred onto the feature map φnor .
D. Training and Inference
1) Training: During the training phase, the normal grid of
GRAD learns normal patterns through a reconstruction task

FENG et al.: Bi-GRID RECONSTRUCTION FOR IMAGE ANOMALY DETECTION

8603

Fig. 3. Overall framework of our GRAD. The input samples are first processed by a pre-trained feature extractor to obtain initial features (the subsequent
FBP module is only activated during the training of the abnormal grid). These features are then mapped to 2D coordinates through the coordinate mapping
module. Based on these coordinates, sampling is performed from the normal and abnormal grid. The sampling results are fused and refined through the feature
refinement module to produce the final reconstructed features. The comparison between these reconstructed features and the initial features yields the final
anomaly detection results. (PS: The abnormal grid and normal grid have their top-left corner markers offset from each other, indicating that they also alternate
during training.

using the Mean Squared Error (MSE) loss as the objective
function:
1
||φaligned (x) − x̂)||22 ,
(13)
Lrec =
CHW
where φaligned (x) is the aligned feature of the input and x̂ is
the feature reconstructed by grid.
For the abnormal grid, we employ a contrastive learning
idea to train it to increase the distance between stored normal
and anomaly features. We utilize the following truncated L1
loss:
X
l+ =
max(0, th − d+ ),
(14)
d+ ∈D

l− =

X

max(0, −th + d− ),

(15)

d− ∈D

Lcon =

P

d+ ∈D max(0, th − d
|D+ |

+

)

+

l−
,
|D− |

Fig. 4. (a) Multiple anomaly patterns yield similar feature maps from the
pretrained extractor. (b) Our FBP module can transform normal images into
abnormal ones in the feature space.

(16)

where, th is manually set to create a buffer zone around the
separation boundary, with th set to 0.5 in our experiments; D is
a set of sample pair similarities constructed via Ground Truth,
where d+ denotes the similarity of positive pairs and d−
denotes that of negative pairs. The training of GRAD is
conducted in two stages: initially, the abnormal grid is trained,
followed by freezing the abnormal grid parameters and training
the normal grid.
2) Inference: During the inference process, the features
from the normal grid are first fused with those from the
abnormal grid. This fusion is then further refined with the

assistance of a similarity-based feature refinement module,
designed to enhance the confidence in known anomalies and
reduce the reconstruction effort in normal regions:
S im = λ1 I[mse(φaligned (x)h,w , x̂ipre rec ) < k]
+ λ2 cosim(φaligned (x), x̂ipre rec ),

(17)

where I(·) is an indicator function that assigns a value of 1 if
the condition within the parentheses is met, and mse(·, ·) and
cosim(·, ·) represent the mean squared error and cosine similarity calculations, respectively. The similarity map described

8604

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 5. Qualitativeresults of GRAD on three datasets. Each row of the figure represents anomaly images, corresponding ground truth, results from different
methods. Notably, even for extremely subtle anomalies in categories such as Macaroni2, Drink Bottle, and Food Bottle, our model has provided precise
localization results.
TABLE I
I MAGE - AND P IXEL - L EVEL AUROC(%)↑ / AUPR(%)↑ ON G OODS AD DATASET, THE * IN THE U PPER R IGHT C ORNER OF S IMPLE N ET I NDICATES T HAT
I T I S T RAINED U NDER THE S EPARATED S ETTING

above is then applied to the reconstructed features to obtain
the final refined features:
i
x̂rec
= S im

x + (1 − S im)

x̂ipre rec ,

(18)

where
denotes element-wise multiplication. The final
0
0
anomaly score map pred ∈ RH ×W is derived by comparing
the reconstructed and original feature maps:
i
pred = ||φaligned (x) − x̂rec
||2 .

(19)

FENG et al.: Bi-GRID RECONSTRUCTION FOR IMAGE ANOMALY DETECTION

8605

TABLE II
I MAGE - AND P IXEL - L EVEL AUROC(%)↑ / AUPR(%)↑ ON MVT EC AD DATASET

Fig. 6. Comparative analysis of different methods on the GoodsAD dataset,
illustrating the trade-offs between inference speed (FPS), detection accuracy
(I-AUROC%), and memory requirements (VRAM). Bubble sizes represent
relative VRAM consumption.

For comparison, pred is reshaped to (H, W). Image-level
anomaly detection uses the max value in the anomaly score
map.

Fig. 7. Comparison of fine-tuning performance across three methods.

IV. E XPERIMENTS AND D ISCUSSION
A. Experiments Setup
1) Datasets: We assessed GRAD on three datasets:
MVTec AD, VisA, and GoodsAD. MVTec AD is a bench-

8606

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

TABLE III
I MPLEMENTATION D ETAILS OF VAD M ODELS

Characteristics (AU-ROC/AUC) and the Area Under
Precision-Recall (AUPR/AP) as metrics for assessing the
performance of our models.
B. Implementation Details

mark for industrial anomaly detection, VisA offers detailed
pixel-level annotations for real-world scenarios, and GoodsAD
focuses on anomalies in retail products, expanding the scope
of anomaly detection to retail automation. Our experiments on
these datasets evaluate methods’ performance and adaptability
across various contexts.
Algorithm 1 Feature Block Pasting (FBP)

This section outlines the experimental setup and implementation details. The backbones used were pretrained on
ImageNet. For Efficientnet-like architectures, the feature
extractor uses the 3rd and 4th layers. By default, Efficientnetb6 is the backbone. All comparison models were from
their official GitHub repositories, with parameters set to
default unless specified in III. Our model used only FBPsynthesized anomalies and no other realistic anomalies. All
methods were trained in a consistent framework, which
affected performance for one-class-one-model approaches like
SimpleNet.
All experiments ran on PyTorch 2.1.0/Python 3.10 (Ubuntu
22.04) using an NVIDIA RTX 4090 GPU and Intel Xeon Gold
6430 CPU.
C. Image and Pixel Level Detection Performance

2) Methods: We assembled a benchmark of advanced unsupervised anomaly detection methods, spanning reconstructionbased, synthesizing-based, and embedding-based categories.
The methods evaluated include PaDiM, RIAD [46], DFR [47],
UniAD, PatchCore, SimpleNet, and CRAD.
3) Metrics: Adhering to standard conventions, we
employ both the Area Under the Receiver Operating

As shown in I, GRAD demonstrates superior performance
on the GoodsAD benchmark, achieving state-of-the-art results
in packaging defect detection. For image-level classification,
the framework achieves 79.4% AUROC and 81.4% AUPR,
showing particular strength in food bottles(84.6% AUROC)
and drink cans(81.6% AUROC). The pixel-level evaluation
reveals even more impressive capabilities, with 96.8% AUROC
and 36.4% AUPR, demonstrating exceptional performance on
drink bottles (97.5% AUROC) and food packages (+ 8.5%
AUPR improvement over CRAD). These results highlight
the model’s effectiveness in real-world packaging inspection
scenarios.
The evaluation on the industrial inspection benchmark
MVTec AD (II) showcases our model’s perfect 100%/100%
scores in 5 out of 15 categories, including bottle and leather
products. The mean image-level performance reaches 99.3%
AUROC and 99.8% AUPR, surpassing all compared methods. At the pixel level, the framework achieves 54.2%
mean AUPR, with particularly significant improvements on
challenging cases: + 12.8% AUPR gain for screw defects
and + 5.4% AUPR improvement for grid textures compared
to PatchCore. The model maintains robust performance across
various material types, from homogeneous surfaces to complex
textures, demonstrating its versatility in industrial quality
control applications.
For the diverse VisA benchmark (IV) containing 12 object
categories, our model establishes new state-of-the-art performance with 93.8% AUROC and 89.4% AUPR at image level.
The pixel-level evaluation shows remarkable precision (98.9%
AUROC/40.6% AUPR). The framework excels in detecting
subtle anomalies (99.6% AUROC for macaroni2) while maintaining robustness across varying illumination conditions and
surface textures, making it particularly suitable for complex
real-world inspection tasks.
The comprehensive evaluation across GoodsAD,
MVTec AD, and VisA datasets demonstrates our model’s

FENG et al.: Bi-GRID RECONSTRUCTION FOR IMAGE ANOMALY DETECTION

8607

TABLE IV
I MAGE - AND P IXEL - L EVEL AUROC(%)↑ / AUPR(%)↑ ON V IS A DATASET

TABLE V
C ROSS -DATASET G ENERALIZATION P ERFORMANCE C OMPARISON OF D IFFERENT A NOMALY D ETECTION M ETHODS

consistent superiority in both image-level classification
and pixel-level localization tasks. Key advantages include
cross-category robustness, small defect sensitivity, and
exceptional handling of complex patterns. With performance
improvements across different metrics and categories, the
framework proves highly effective for diverse industrial
inspection applications requiring precise defect detection and
localization. These results position our approach as a new
benchmark in automated visual inspection systems.

PaDiM, DFR, RIAD) in terms of frame rate and VRAM
consumption, measuring the complete processing pipeline
from image input (after resizing and normalization) to final
anomaly map generation. To ensure fair comparison, we
uniformly used a batch size of 1 during inference for all
evaluations.

D. Detect Frame Rate and VRAM Usage

1) Frame Rate Performance: The processing speeds vary
significantly across methods, ranging from 2.9 FPS (PaDiM)
to 85.6 FPS (DFR). Our method achieves 10.2 FPS, which,
while not matching the fastest DFR approach, still meets basic
real-time processing requirements.

The computational efficiency and memory usage of anomaly
detection models are critical for practical deployment.
As shown in Figure 6, we evaluated GRAD against seven stateof-the-art methods (CRAD, SimpleNet, Patch-Core, UniAD,

2) Memory Utilization: VRAM usage ranges from
233.9 MB (RIAD) to 683.2 MB (SimpleNet). Our method
consumes 633.7 MB, placing it in the middle range among
compared approaches.

8608

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 8. More visualization results on GoodsAD.

FENG et al.: Bi-GRID RECONSTRUCTION FOR IMAGE ANOMALY DETECTION

Fig. 9. More visualization results on MVTec AD.

8609

8610

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 10. More visualization results on VisA.

FENG et al.: Bi-GRID RECONSTRUCTION FOR IMAGE ANOMALY DETECTION

These results indicate that while GRAD has room
for improvement in computational efficiency, its overall
performance meets basic industrial application requirements,
particularly in scenarios demanding high detection accuracy.
Future work will focus on optimizing the model’s computational efficiency to further enhance its practical utility.
E. Cross-Dataset Generalization Evaluation
To evaluate generalization performance, we conducted
cross-dataset experiments under two transfer scenarios: zeroshot direct transfer and limited-epoch fine-tuning (10 and
20 epochs). This setup assesses each method’s ability to learn
domain-invariant representations and adapt to datasets with
different distributions.
As shown in Table V, our method demonstrates highly
competitive generalization capability. In the zero-shot transfer setting—where models are applied without any finetuning—our method delivers solid performance, outperforming
CRAD. While it does not surpass UniAD in this specific scenario, its strong baseline performance provides a
robust foundation for rapid adaptation. The key strength
of our approach is revealed during fine-tuning: with only
10 epochs, it achieves 88.0% I-AUROC and 98.6% P-AUROC
on MvtecAD→VisA, significantly exceeding both baselines
and demonstrating exceptional adaptability.
Figure 7 provides detailed insights into the fine-tuning
dynamics of the three methods. Several key observations can
be drawn from the progressive performance curves:
1) Initial Performance Gap: In the zero-shot setting
(epoch 0), UniAD shows a slight advantage in some metrics,
particularly in Image AUROC for both transfer directions.
However, our method maintains competitive initial performance, providing a solid foundation for subsequent adaptation.
2) Rapid Adaptation: Our method exhibits the steepest learning curves during the early fine-tuning stages
(epochs 0-10), indicating efficient knowledge transfer and
rapid adaptation to the target domain. This is particularly
evident in the Pixel AUROC metrics, where our method
quickly reaches near-perfect performance levels.
3) Consistent Superiority: Across all four evaluation metrics and throughout the fine-tuning process, our method either
maintains leadership or demonstrates the most consistent
improvement trajectory. The performance gaps between our
method and the baselines generally widen with additional finetuning, confirming the effectiveness of our approach.
4) Convergence Patterns: While all methods show performance saturation after 10-15 epochs, our method achieves
higher asymptotic performance levels. This suggests that our
approach not only learns faster but also discovers better
solutions for the target domain.
F. Ablation Study
1) N-Grid and A-Grid: The ablation study (Table VI)
shows combining N-Grid and A-Grid achieves optimal I/P
AUPR: 99.8%/54.2% on MVTec AD (+ 0.9%/2.0% over
N-Grid) and 81.4%/36.4% on GoodsAD (+ 4.1%/6.5% over

8611

TABLE VI
A BLATION S TUDY FOR N-G RID AND A-G RID ON I/P AUPR(%)

TABLE VII
I MPACT OF G RID S IZE C ONFIGURATION ON G OODS AD

TABLE VIII
A BLATION S TUDY FOR S OURCE OF S YNTHETIC A NOMALIES ON MVT EC AD

N-Grid). The dual-grid approach significantly outperforms
A-Grid alone (MVTec: 96.6%/49.2%), demonstrating
N-Grid’s core detection capability and A-Grid’s role in
enhancing localization, particularly improving GoodsAD
P-AUPR by 6.5%. This evidence confirms that A-Grid
effectively complements N-Grid by leveraging synthetic
anomaly knowledge to refine detection boundaries.
2) Grid Size: On GoodsAD, optimal performance
(81.4/36.4 I/P-AUPR) was achieved with a 32 × 32 local/4 × 4
global grid configuration, demonstrating that high local
resolution with moderate global context provides the best
accuracy-efficiency trade-off. Expanding the global grid to
8 × 8 showed diminishing returns.
3) Sources of Synthetic Anomalies: On MVTec AD
(Table VIII), our feature-level FBP synthesis achieved
99.8%/54.2% I/P-AUPR - comparable to AnomalyDiffusion (A-D: 99.8%/54.6%) and superior to Gaussian Noise
(G-N: 99.2%/52.3%). While FBP shows marginal performance
difference compared to A-D, it offers significantly superior
computational efficiency.
V. C ONCLUSION
We introduce GRAD, a novel anomaly detection method
that leverages continuous grids to store both normal and
abnormal features, addressing the limitations of existing unsupervised and self-supervised methods in handling fine-grained
anomalies. GRAD’s key innovations include using grids to
enhance generalization and avoid the IS problem, introducing
an additional abnormal grid to refine the boundaries of normal

8612

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

features, and developing the FBP module for efficient and
flexible anomaly synthesis at the feature level. Comprehensive experiments on industrial datasets such as MVTecAD,
VisA, and the latest GoodsAD demonstrate GRAD’s superior
performance, improved detection accuracy, and support for a
unified task setting.
R EFERENCES
[1]

J. Liu et al., “Deep industrial image anomaly detection: A survey,” Mach.
Intell. Res., vol. 21, no. 1, pp. 104–135, Jan. 2024, doi: 10.1007/s11633023-1459-z.
[2] T. Xiang et al., “SQUID: Deep feature in-painting for unsupervised
anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2023, pp. 23890–23901. [Online]. Available:
https://api.semanticscholar.org/CorpusID:257766829
[3] K. K. Santhosh, D. P. Dogra, and P. P. Roy, “Anomaly detection in
road traffic using visual surveillance: A survey,” ACM Comput. Surveys,
vol. 53, no. 6, pp. 1–26, Dec. 2020, doi: 10.1145/3417989.
[4] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Mvtec ad—A
comprehensive real-world dataset for unsupervised anomaly detection,”
in Proc. CVPR, Jun. 2019, pp. 9592–9600.
[5] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “PaDiM: A patch distribution modeling framework for anomaly detection and localization,”
in Proc. Pattern Recognit. Int. Workshops Challenges, Jan. 2021,
pp. 475–489, doi: 10.1007/978-3-030-68799-1 35.
[6] N. Cohen and Y. Hoshen, “Sub-image anomaly detection with deep
pyramid correspondences,” 2020, arXiv:2005.02357.
[7] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler,
“Towards total recall in industrial anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022,
pp. 14298–14308. [Online]. Available: https://api.semanticscholar.org/
CorpusID:235436036
[8] D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1705–1714.
[9] J. Hou, Y. Zhang, Q. Zhong, D. Xie, S. Pu, and H. Zhou, “Divideand-assemble: Learning block-wise memory for unsupervised anomaly
detection,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct.
2021, pp. 8771–8780.
[10] Z. You et al., “A unified model for multi-class anomaly detection,” in
Proc. Adv. Neural Inf. Process. Syst., 2022, pp. 4571–4584. [Online].
Available:
https://proceedings.neurips.cc/paperfiles/paper/2022/file/
1d774c112926348c3e25ea47d87c835b-Paper-Conference.pdf
[11] J. C. Lee, T. Kim, E. Park, S. S. Woo, and J. H. Ko, “Continuous
memory representation for anomaly detection,” in Proc. ECCV, 2024,
pp. 438–454.
[12] Y. Duan, Y. Hong, L. Niu, and L. Zhang, “Few-shot defect image
generation via defect-aware feature manipulation,” in Proc. AAAI Conf.
Artif. Intell., vol. 37, 2023, pp. 571–578.
[13] T. Hu et al., “AnomalyDiffusion: Few-shot anomaly image generation
with diffusion model,” in Proc. AAAI Conf. Artif. Intell., Mar. 2024,
pp. 8526–8534.
[14] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, “Spotthe-difference self-supervised pre-training for anomaly detection and
segmentation,” in Proc. ECCV, 2022, pp. 392–408.
[15] J. Zhang, R. Ding, M. Ban, and L. Dai, “PKU-GoodsAD: A supermarket
goods dataset for unsupervised anomaly detection and segmentation,”
IEEE Robot. Autom. Lett., vol. 9, no. 3, pp. 2008–2015, Mar. 2024, doi:
10.1109/LRA.2024.3352358.
[16] P. Bergmann, S. Löwe, M. Fauser, D. Sattlegger, and C. Steger,
“Improving unsupervised defect segmentation by applying structural
similarity to autoencoders,” 2018, arXiv:1807.02011.
[17] J. Chen, S. Sathe, C. C. Aggarwal, and D. S. Turaga, “Outlier detection
with autoencoder ensembles,” in Proc. SIAM Int. Conf. Data Mining,
2017, pp. 90–98.
[18] C. Zhou and R. C. Paffenroth, “Anomaly detection with robust deep
autoencoders,” in Proc. 23rd ACM SIGKDD Int. Conf. Knowl. Discovery
Data Mining, Aug. 2017, pp. 665–674.
[19] D. Dehaene, O. Frigo, S. Combrexelle, and P. Eline, “Iterative energybased projection on a normal data manifold for anomaly localization,”
2020, arXiv:2002.03734.

[20] W. Liu et al., “Towards visually explaining variational autoencoders,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2020,
pp. 8639–8648.
[21] J. Zhang et al., “Exploring plain ViT reconstruction for multi-class
unsupervised anomaly detection,” 2023, arXiv:2312.07495.
[22] M. Sabokrou, M. Khalooei, M. Fathy, and E. Adeli, “Adversarially
learned one-class classifier for novelty detection,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit., Jun. 2018, pp. 3379–3388.
[23] T. Schlegl, P. Seeböck, S. M. Waldstein, G. Langs, and U. SchmidtErfurth, “F-AnoGAN: Fast unsupervised anomaly detection with
generative adversarial networks,” Med. image Anal., vol. 54, pp. 30–44,
May 2019.
[24] Y. Liang, J. Zhang, S. Zhao, R. Wu, Y. Liu, and S. Pan, “Omnifrequency channel-selection representations for unsupervised anomaly
detection,” IEEE Trans. Image Process., vol. 32, pp. 4327–4340,
2023.
[25] J. Pirnay and K. Y. Chai, “Inpainting transformer for anomaly detection,”
in Proc. Int. Conf. Image Anal. Process., 2022, pp. 394–406.
[26] X. Yao, R. Li, Z. Qian, Y. Luo, and C. Zhang, “Focus the discrepancy:
Intra- and inter-correlation learning for image anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2023,
pp. 6803–6813.
[27] H. He et al., “A diffusion-based framework for multi-class anomaly
detection,” in Proc. AAAI Conf. Artif. Intell., Mar. 2024, pp. 8472–8480.
[28] C. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Self-supervised
learning for anomaly detection and localization,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit., Apr. 2021, pp. 9664–9674.
[29] V. Zavrtanik, M. Kristan, and D. Skočaj, “Draem-a discriminatively
trained reconstruction embedding for surface anomaly detection,” in
Proc. IEEE/CVF Int. Conf. Comput. Vis., Aug. 2021, pp. 8330–8339.
[30] H. M. Schlüter, J. Tan, B. Hou, and B. Kainz, “Natural synthetic
anomalies for self-supervised anomaly detection and localization,” in
Proc. Eur. Conf. Comput. Vis., 2021, pp. 474–489.
[31] Z. Liu, Y. Zhou, Y. Xu, and Z. Wang, “SimpleNet: A simple network
for image anomaly detection and localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023, pp. 20402–20411.
[32] Y. Zhao, “OmniAL: A unified CNN framework for unsupervised
anomaly localization,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2023, pp. 3924–3933.
[33] J. Liu et al., “Unsupervised continual anomaly detection with
contrastively-learned prompt,” in Proc. AAAI Conf. Artif. Intell., Mar.
2024, pp. 3639–3647.
[34] J. Tang et al., “An incremental unified framework for small
defect inspection,” in Proc. Eur. Conf. Comput. Vis., 2023,
pp. 307–324.
[35] J. Gao, Z. Wang, J. Xuan, and S. Fidler, “Beyond fixed grid: Learning
geometric image representation with a deformable grid,” in Proc. Eur.
Conf. Comput. Vis., 2020, pp. 108–125.
[36] J. C. Lee, D. Rho, J. H. Ko, and E. Park, “FFNeRV: Flow-guided framewise neural representations for videos,” in Proc. 31st ACM Int. Conf.
Multimedia, Oct. 2023, pp. 7859–7870, doi: 10.1145/3581783.3612444.
[37] C. M. Jiang, A. Sud, A. Makadia, J. Huang, M. Nießner, and
T. Funkhouser, “Local implicit grid representations for 3D scenes,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2020,
pp. 6000–6009.
[38] L. Mescheder, M. Oechsle, M. Niemeyer, S. Nowozin, and A. Geiger,
“Occupancy networks: Learning 3D reconstruction in function space,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2019,
pp. 4460–4470.
[39] A. Chen, Z. Xu, A. Geiger, J. Yu, and H. Su, “TensoRF: Tensorial
radiance fields,” in Proc. Eur. Conf. Comput. Vis., 2022, pp. 333–350.
[40] S. Fridovich-Keil, A. Yu, M. Tancik, Q. Chen, B. Recht, and
A. Kanazawa, “Plenoxels: Radiance fields without neural networks,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2022, pp. 5501–5510.
[41] L. Liu, J. Gu, K. Z. Lin, T. Chua, and C. Theobalt, “Neural sparse voxel
fields,” in Proc. Adv. Neural Inf. Process. Syst., 2020, pp. 15651–15663.
[42] J. Chan Lee, D. Rho, S. Nam, J. Hwan Ko, and E. Park, “Coordinateaware modulation for neural fields,” 2023, arXiv:2311.14993.
[43] N. Rahaman et al., “On the spectral bias of neural networks,” in Proc.
Int. Conf. Mach. Learn., 2018, pp. 5301–5310.
[44] M. Tan and Q. V. Le, “EfficientNet: Rethinking model scaling for
convolutional neural networks,” in Proc. Int. Conf. Mach. Learn., 2019,
pp. 6105–6114.
[45] H. Park, J. Noh, and B. Ham, “Learning memory-guided normality
for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. pattern
Recognit., Mar. 2020, pp. 14372–14381.

FENG et al.: Bi-GRID RECONSTRUCTION FOR IMAGE ANOMALY DETECTION

8613

[46] V. Zavrtanik, M. Kristan, and D. Skočaj, “Reconstruction by inpainting
for visual anomaly detection,” Pattern Recognit., vol. 112, Apr. 2021,
Art. no. 107706.
[47] Y. Shi, J. Yang, and Z. Qi, “Unsupervised anomaly segmentation via
deep feature reconstruction,” Neurocomputing, vol. 424, pp. 9–22, Feb.
2021, doi: 10.1016/j.neucom.2020.11.018.

Guangyu Wei received the B.E. degree in information engineering from Nanjing University of
Information Science and Technology in 2023. He
is currently pursuing the M.S. degree with Nanjing
University of Aeronautics and Astronautics. His
research interests include NLP, time series analysis,
and computer vision.

Aimin Feng is an Associate Professor and the
Master’s Supervisor with the School of Computer
Science and Technology, Nanjing University of
Aeronautics and Astronautics, and the State Key Lab
for Novel Software Technology, Nanjing University.
She has published over 30 papers and serves as a
reviewer for multiple journals. Her research interests
include machine learning and computer architecture.

Huichuan Huang received the B.E. degree in computer science and technology from Nanjing Tech
University in 2023. He is currently pursuing the
M.S. degree with Nanjing University of Aeronautics and Astronautics. His research interests include
computer vision and anomaly detection.

Wenlong Sun received the B.E. degree in computer
science and technology from Nanjing University of
Information Science and Technology in 2023. He
is currently pursuing the M.S. degree with Nanjing
University of Aeronautics and Astronautics. His
research interests include computer vision, multimodal learning, and anomaly detection.
PAPER_TEXT
