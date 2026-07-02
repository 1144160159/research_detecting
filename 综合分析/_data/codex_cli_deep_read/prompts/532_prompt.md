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
# [532] Scalable Large Model for Unlabeled Anomaly Detection With Trio-Attention U-Transformer and Manifold-Learning Siamese Discriminator
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
编号：532
题名：Scalable Large Model for Unlabeled Anomaly Detection With Trio-Attention U-Transformer and Manifold-Learning Siamese Discriminator
年份：2025
DOI：10.1109/tsc.2025.3536306
来源：IEEE Transactions on Services Computing
PDF：paper/10.1109_TSC.2025.3536306.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测、加密流量分类与应用识别
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\532.txt
- 原始字符数：68013
- 本次发送字符数：68013
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1012

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 18, NO. 2, MARCH/APRIL 2025

Scalable Large Model for Unlabeled Anomaly
Detection With Trio-Attention U-Transformer
and Manifold-Learning Siamese Discriminator
Muyan Yao , Member, IEEE, Dan Tao , Member, IEEE, Peng Qi , Member, IEEE,
and Ruipeng Gao , Member, IEEE

Abstract—To identify pattern deviations in large-scale industrial
infrastructures, anomaly detection is crucial yet challenging. Previous research has not adequately addressed the characteristics
and deployment considerations in these complex scenarios. In this
paper, we present InoU, a scalable anomaly detection framework
to process unlabeled multivariate time-series data. We incorporate
a VAE filter to ease impacts from noisy components in training materials. We propose a scalable trio-attention U-Transformer to construct the typical representation of high-dimensional streams and
produce pseudo labels that enable the later training process. The
ultra perception and intra-/ inter-flow attention mechanisms are
delicately designed to aggregate information from different flows
with variable granularities while keeping a global view of the data.
Its nested structure helps to maintain high efficiency even when the
model is scaled down. We introduce a Siamese discriminator that
projects target data into manifolds, and collates discrepancies at the
embedding level. This paradigm elevates detection performance
far beyond segment-wise error comparison in prior works. We
apply contrastive and adversarial learning techniques to optimize
manifold projection and detection performance when processing
unseen samples. Extensive experiments on five large-scale datasets
demonstrate the effectiveness of InoU with an average F1-Score
improvement of 5.58%, significantly outperforming the state-ofthe-art.
Index Terms—Anomaly detection, service and system
management, self-supervised, Siamese network, Transformer,
contrastive, manifold learning.

I. INTRODUCTION
HE massive deployment of sensors, actuators, and other
assets in industrial scenarios has formed an increasingly
complex network architecture [1], [2], enabling a series of
automated and intelligent operations [3], [4]. The deployments,
in turn, pose pressing urges for their maintenance [5]. Anomaly
detection, which identifies unusual or unexpected patterns or

T

Received 6 August 2023; revised 27 December 2024; accepted 18 January
2025. Date of publication 30 January 2025; date of current version 10 April 2025.
This work was supported in part by the Natural Science Foundation of China
under Grant 62472023, Grant 62402027 and Grant 62072029, and in part by
the Natural Science Foundation of Beijing Municipality under Grant L221003.
(Corresponding author: Dan Tao.)
Muyan Yao, Dan Tao, and Peng Qi are with the School of Electronic and
Information Engineering, Beijing Jiaotong University, Beijing 100040, China
(e-mail: muyanyao@bjtu.edu.cn; dtao@bjtu.edu.cn; pengqi1@bjtu.edu.cn).
Ruipeng Gao is with the School of Cyberspace Science and Technology, Beijing Jiaotong University, Beijing 100040, China (e-mail: rpgao@bjtu.edu.cn).
Digital Object Identifier 10.1109/TSC.2025.3536306

Fig. 1.

Challenges of deploying anomaly detection in industrial scenarios.

events in the target data, provides a new viewpoint to address
this need [6], [7], [8], thus attracting widespread attention.
Most existing solutions [9], [10], [11], [12], [13] use data
normalization and windowing techniques to pre-process the
data, and deploy generative models to extract patterns and reconstruct the target data. The criteria for identifying anomalies
are usually based on the segment-wise reconstruction error
of the normalized data. Seemingly promising, these solutions
face challenges (Fig. 1) caused by a series of factors in actual
industrial deployment, including the massive volume and variety
of on-site data, the heterogeneity in different devices, and the
imbalanced hardware resources in different configurations.
First, the insufficient consideration of discrepancy analysis
in prior works contributes to the potential neglects of anomalies. Differences in high-dimensional data easily become subtle
after segment-wise averaging, which is a common practice of
error calculation. Moreover, the data normalization that transforms data with variable ranges to a uniform scale, potentially
contributes to overlooking fluctuations in channels with more
dynamic ranges.
Second, the choice of window length and the inadequate availability of labeled data further cause barriers in actual industrial
practice. Longer windows dilute the presence of data points that
deviate from the norm, while shorter windows fail to capture
sufficient contextual information over time. Moreover, the labeling process in industrial scenarios is costly and labor-intensive,
while the model tuning process in a self-supervised manner has
not yet been fully explored.
Lastly, the resources in industrial scenarios are usually imbalanced, posing challenges to the scalability of models to be
deployed. While Multi-Access Edge Computing (MEC) offers a potential solution for near-source model inference, its

1939-1374 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

YAO et al.: SCALABLE LARGE MODEL FOR UNLABELED ANOMALY DETECTION

computational capabilities are inherently limited. Resources on
clouds are usually more abundant, but remote deployment is
not acceptable for latency-sensitive applications. These characteristics of a typical industrial environment determine that the
anomaly detection framework should maintain adaptability and
scalability.
To address these challenges, we redesign an anomaly detection pipeline that best fits industrial needs, and propose
a scalable framework InoU that incorporates a trio-attention
U-Transformer and a manifold-learning Siamese discriminator
under a unified yet flexible architecture with tunable parameters
ranging from approximately 100 million to 6 billion, depending
on the specific configuration and data source. During the design
of its architecture, we adopt a complementary rationale, where
the unified structure utilizes generative models to extract typical
patterns and reconstruct data, while leveraging discriminative
models for manifold projection and discrepancy analysis.
Adapting to the data properties under industrial setups, we
decouple the VAE (Variational Autoencoder) model from direct
involvement in the anomaly detection task, but to filter irregularities and noise from the raw training materials. In this way,
we bypass the risk of the VAE model being biased or improperly
trained, and offset the impacts of noise and anomalies without
the need for human intervention.
To learn the embeddings of normal data while maintaining a high level of scalability, we propose a trio-attention UTransformer. The ultra perception and intra-/ inter-flow attention
mechanisms within each flow assist information aggregation in
variable granularities without losing a high-level perspective of
the complex industrial data. The U-shaped nested structure also
helps the model maintain high efficiency even when the model
is scaled down.
Furthermore, we devise a contrastive manifold-learning
Siamese discriminator to cope with the challenge of anomaly
overlooking in conventional numerical error comparison based
works while processing high-dimensional industrial data. Furthermore, we design a contrastive manifold-learning Siamese
discriminator to address the limitation of conventional numerical
error comparison methods, which often encounter the challenge
of anomaly overlooking when processing high-dimensional industrial data. This structure projects the observed and reconstructed sequences into the manifold through a shared backbone,
and adaptively collates their discrepancies at the embedding
level. We introduce techniques from contrastive and adversarial
learning to the duet outputs from the Siamese backbones to
optimize the manifold projection approach and achieve a more
constructed latent space.
The contributions of this work are summarized here.
r We present the anomaly detection framework InoU, incorporating a trio-attention scalable U-Transformer reconstructor and a manifold-learning Siamese discriminator
in a unified architecture. This design inspects embedding
discrepancies in a fine-grained manner while maintaining
high scalability.
r We design a refined data processing pipeline to offset
the impacts of noise and anomalies in the raw training materials and adapt to industrial properties. We also

1013

introduce contrastive and adversarial learning to optimize
the projection of manifold and further elevate the anomaly
detection performance.
r We evaluate InoU on five large-scale datasets from realworld industrial applications. InoU achieves an overall
F1-Score of 0.9168, outperforming the latest state-ofthe-art. Extensive experiments validate its scalability and
effectiveness.
The rest of this paper is organized in the following ways.
Section II introduces the underlying methodology, and we further present the design details of InoU in Section III. In Section IV, we discuss the settings and results of the extensive
experiments. Section V briefly reviews recent research on multivariate time series anomaly detection. Finally, we conclude this
work in Section VI.
II. METHODOLOGY
In this section, we provide the necessary information to help
readers comprehend the motivation and highlight the design of
InoU.
Data Pre-processing: In industrial setups, the deployed assets
produce multivariate time series streams as they perform designated tasks. These multivariate data are usually sampled at a
fixed or variable frequency to record metrics in various industrial
processes. Due to the properties of these processes behind the
streams, there may be significant differences in the numerical
ranges of different channels.1
The
data
stream
is
denoted
as
x=
{x(1) , x(2) , x(3) , . . . , x(N ) }, x ∈ RN ×M , where N represents
the total number of time steps, and M is the total number of
features. Each one of its components x(t) (1 ≤ t ≤ N ) is a
1 × M vector. A max-min scaler is then deployed to normalize
x, and use a sliding window with length L = 128 to segment
the scaled time series data into slices. For example, we use
x(t−L+1:t) ∈ RL×M to denote a recording sequence that starts
at time t − L + 1 and ends at time t.
Considering that a data segment is the minimal unit that
the deep learning network consumes, we use xt to represent
x(t−L+1:t) for a clear description in later parts of the paper. We
also use x to represent the pre-processed dataset in instances
where the dataset is mentioned, e.g., in the equations of the
model optimization, but without the need to specify a specific
timestep.
Anomaly Detection: Most prior anomaly detection works
are built based on numerical error comparison. They rely on
generative models to reconstruct data. Then, they calculate the
deviation between the observed and the reconstructed values and
determine if the sequences are anomalous based on the numerical
segment-wise error. This criterion is based on the assumption
that anomalies will have a more significant reconstruction error
than normal data. However, there are a few things to note in
actual practice:

1 By using the term “channel,” we refer to the univariate recordings in the multivariate time series data, with the intention to emphasize their physical meanings.
This word may be used interchangeably with “feature” in the following parts.

1014

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 18, NO. 2, MARCH/APRIL 2025

Fig. 2. Capture of temporal dependencies in segmented data. Orange sequences are anomalous.

Fig. 3. Fluctuations in a high dynamic channel become less salient after
normalization, leading to potential overlooks of anomalies.

1) Segment length and limitations in dependency capture: As
stated, the operation of reconstruction and error calculation are
all based on the length L that segments the original data stream.
A longer length captures more temporal information but, on the
other hand, dilutes fluctuations during the error calculation along
the time axis (Fig. 2(a)). Meanwhile, a shorter length magnifies
these fluctuations, but the limited temporal dependency that is
captured may be insufficient to identify contextual or collective
anomalies (Fig. 2(b)).
2) Data normalization and deviation assessment: Data normalization is an essential step in data preprocessing, ensuring
that each channel is represented on a comparable scale. This
technique helps neural networks to converge effectively, but it
may also weaken the dynamics of each channel in the original
data (Fig. 3(a)).
Under the principle of normalization, channels with high
dynamic ranges will be processed with larger scaling factors.
As such, fluctuations and irregularities in these channels become
less salient after normalization, leading to potential neglect of
anomalies (Fig. 3(b)). Besides, it can also be observed that the
channels in these streams may have diverse physical meanings.
This information is directly discarded since the error calculation
treats all channels equally.

Fig. 4.

III. DESIGN OF INOU
A. Framework Overview
Fig. 4 shows the overall structure of InoU. This framework
comprises two major parts: offline training and online detection.
Offline Training: During the training process, an efficient VAE
(Variational Autoencoder) is trained on the unlabeled, noisy
training materials. When this VAE model converges, it is again
reused in the data pre-process pipeline. In this way, it serves as
a filter that offsets the noisy and anomalous components in the
training materials without the need for human intervention.

Overall framework of InoU.

Based on the filtered training material, the U-Transformer
is guided to extract the dependencies and reconstruct the data.
During this step, the U-Transformer captures the essential representations of normal data, so their reconstructions can be done
with high fidelity. However, the anomalies are less presented in
the training materials, resulting in more significant reconstruction deviations. Driven by this principle, the U-Transformer is
employed in two tasks: reconstructing the incoming sequences
for further discrepancy analysis, and generating pseudo labels
for the rest of the training process.
Utilizing contrastive learning techniques, the Siamese Discriminator is trained with two primary objectives: achieving
high anomaly detection performance, and creating a manifold
projection methodology that effectively metrics related to discrepancies even for samples that are unseen in historical recordings. The adversarial learning technique is further applied with
a small learning rate, which optimizes embedding distributions
by adjusting the manifold.
Online Detection: To identify anomalies in the data stream,
the target samples are processed and reconstructed by the
U-Transformer. Then, the Siamese Discriminator parallelly

YAO et al.: SCALABLE LARGE MODEL FOR UNLABELED ANOMALY DETECTION

1015

Recurrent Unit layer, which bridges temporal dependencies. The
operations of a GRU layer are presented as follows.



 t−1 |xh
(3)
rt = σ W r · h
t



 t−1 |xh
ut = σ W u · h
(4)
t



 t−1 |xh
ht = tanh W h · r t  h
(5)
t
 t−1 + ut  ht
 t = (1 − ut )  h
h
t
[μt , δ t ] = h

Fig. 5.

The VAE model is used as a filter in the data processing pipeline.

examines the observed and reconstructed sample pairs, and
compares their discrepancies at the embedding level. The final
inspection results are thus generated.
B. VAE Driven Filtering of Unlabeled Training Material
Many prior works utilize VAE as the generative model to
extract typical patterns from unlabeled training materials. However, some researchers [13], [14], [15], [16] have also pointed
out that the VAE model based anomaly detection solutions
may encounter performance issues when confronted with high
noise levels, which is common in industrial setups. Besides,
VAE models can also be biased in real-world events for several
reasons [17]. This is due to the dilemma that the VAE model is
trained to reconstruct the majority of training materials, but to
what extent the data fitting should reach remains a challenging
question.
To bypass this issue, we design a novel data processing
pipeline (Fig. 5(a)) that decouples the VAE model from direct
involvement in the anomaly detection task. The VAE model is
employed to filter the training materials, rather than to reconstruct them. The underlying rationale of this design is intuitive.
Since the unlabeled training materials exhibit significant imbalances, skewness, and noise in industrial scenarios, we deploy the
VAE model as a filter to process the raw unlabeled training set
Dtrain,raw . This way, we form the filtered training set Dtrain,f lt
to ease impacts from the noisy and anomalous components.
Details of this pipeline are as follows.
The VAE model (Fig. 5(b)) used for the processing pipeline
mainly consists of two parts: the encoder and the decoder. The
encoder in this VAE model interprets the input xt into extracted
data descriptions xht , which are then used to generate the latent
embeddings μt and δ t .
xht = ReLU (Conv1D (xt , k3, s2)) × 3
 
μt , δ t = GRU xht

(1)
(2)

Here, we use Conv1D to denote the 1D convolution operation, whose arguments are (input, kernel_size, stride), respectively. ReLU is the Rectified Linear Unit activation function
that introduces non-linearity to the model. GRU is the Gate

(6)
(7)

where r t , ut are the reset and update gate, [·] is the concatenation
operation, and  is the Hadamard product. Besides, σ(·) and
tanh represent the sigmoid and hyperbolic tangent activation
functions.
Based on the latent embeddings μt and δ t , the decoder generates the reconstructed sample x̄t by performing symmetrical
operations as compared to the encoder.
xzt = GRU (Rep (μt , δ t ))

(8)

x̄t = ReLU (Conv1DT (xzt , k3, s2)) × 3

(9)

Here, the term Rep denotes the reparameterize process. The
arguments of Conv1DT (transposed 1D convolution) are similar
to those of Conv1D, consisting of (input, kernel_size, stride).
To optimize the parameters of this VAE filter model, we deploy
a Kullback-Leibler divergence based loss:
Lf lt = Eqφ (z|x) [log pθ (x|z)] − KL [qφ (z|x)pθ (z)]

(10)

Based on the trained VAE filter model, the error set E of the
unlabeled training set Dtrain,raw is calculated as:
L

et =

1
x(i) − x̄(i) 22
L i=1

E = {et | 1 ≤ t ≤ N }

(11)
(12)

where  · 2 is the L2 Norm, and L is the length of the window
used to segment the data (Section II). x̄(i) is the i-th time step
inside the sequence being processed, in this case, the x̄t .
A threshold κ for the filtering process is then determined based
on the distribution of E. By applying the filter, a filtered training
set Dtrain,f lt is generated.
xt ∈ Dtrain,f lt , if et ≤ κ

(13)

C. Trio-Attention U-Transformer for Representation Bridging
and Data Reconstruction
Overview: Enlightened by advancements in U-Net [18], [19]
and transformer [20], we design a trio-attention U-Transformer
structure (Fig. 6) that is optimized for multivariate time series
representation bridging and reconstruction while keeping outstanding scalability.
The U-Transformer is employed to construct the typical
representations from the filtered training set Dtrain,f lt . Since
the learned patterns are derived from the filtered data, the UTransformer is expected to amplify discrepancies between the

1016

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 18, NO. 2, MARCH/APRIL 2025

output of the i-th head in the multi-head attention mechanism,
which is calculated as follows:


(i)
(i)
(i)
(15)
ρ1 = Att W (i)
q xin_lef t , W k xin_1 , W v xin_1
(i)

(i)

(i)

where W q , W k , and W v are the query, key, and value
weights for the i-th head, respectively. Att is the dot-product
attention mechanism:


(16)
Att(q, k, v) = Softmax qkT v

Fig. 6.

The structure of the trio-attention U-Transformer.

In the second tier, the information fusion focuses on aggregating information from different flows. This step helps the
U-Transformer capture significant patterns at different granularities without losing a global perspective on the data stream.
xultra_p = [xin_lef t , xsc_1 , xsc_2 , · · · xsc_ω ]

Fig. 7. The two-tier information flow aggregation in each block of the UTransformer.

input and output when anomalies occur. To achieve this goal,
we weave a delicate structure (Fig. 6) with multiple tricks for
information extraction and aggregation.
Ultra Perception Shortcut Attention Driven Two-Tier Information Flow Aggregation: One key feature of the nested structure in U-Transformer is the long shortcut connections that allow
information to flow between different levels of the network. To
enhance the aggregation of information from shallower or deeper
levels that is processed with different granularity, we design a
two-tier information flow aggregation mechanism that is based
on the ultra perception shortcut attention technique (Fig. 7).
For clarity in notation, we use xin_lef t for the output of the
horizontal left block of the current block where this attention
mechanism is applied. Similarly, we use xin_o to denote the
output of blocks that are connected to the current block through
shortcut connections, where o in the subscript indicates their
sequence number. We denote the total number of these shortcut
connected blocks as ω.
In detail, the ultra perception aggregation mechanism functions in a two-tier manner. In the first tier, the fusion of information flow performs in a block-to-block way. During this
process, the remote information from the shortcut connected
blocks is compared and aggregated with the information from
the horizontal left block. Take the fusion between xin_lef t and
xin_1 as an example.


(1)
(2)
(i)
(H)
(14)
xsc_1 = LN ρ1 , ρ1 , . . . , ρ1 , . . . , ρ1
Here, LN denotes the layer normalization operation that
helps to stabilize the training process, [·] is the concatenation
(i)
operation, and H is the total number of attention heads. ρ1 is the

(17)

Intra-Flow Attention Driven Feature Map Contraction and
Expansion: To guide the model to generate representations that
are more informative, we use this technique to further process the
output from the ultra perception shortcut attention mechanism.
The specific process of this operation varies depending on
the location of the flow. Two main paths form the universal
data flow in the U-Transformer: the contraction path and the
expansion path. The former bridges complex dependencies by
compressing the incoming sequences. Meanwhile, the latter
weaves the information coming from various flows, and fuses
them adaptively. In this way, the U-Transformer is able to keep
a high level of scalability while extracting the most significant
patterns from the data.
On the contraction path, the aggregated flow xultra_p is
processed by two cascaded 1D convolutional (Conv1D) layers:
xif = Conv1D+S(Conv1D+S(xultra_p , k3, s1), k3, s2) (18)
Here, Conv1D+S denotes the Conv1D operation with SeLU
(Scaled Exponential Linear Unit) activation. Then, a follow-up
multi-head attention module is applied to the output xif for
fine-grained dependency extraction.


(1)
(2)
(i)
(H)
(19)
xis_f mc = LN ρic , ρic , . . . , ρic , . . . , ρic
(i)

where H is the total number of attention heads. ρic is the output
of the i-th head in the multi-head attention mechanism to process
the information in xif (18):


(i)
(i)
(i)
ρic = Att W (i)
(20)
q xif , W k xif , W v xif
On the expansion path, the resolution of the feature map
gradually gets restored through the cascaded transposed 1D
convolutional (Conv1DT) layers.
xif = Conv1DT+S (Conv1DT+S (xultra_p , k3, s2) , k3, s1)
(21)
Here, Conv1DT+S denotes the Conv1DT operation with SeLU
activation. This operation is also followed by a multi-head
attention module:


(i)
(i)
(i)
ρie = Att W (i)
q xif , W k xif , W v xif

YAO et al.: SCALABLE LARGE MODEL FOR UNLABELED ANOMALY DETECTION

1017

Fig. 9.

The structure of the Siamese discriminator.

Here,  · 2 is the L2 Norm. To help the intermediate layers of the
U-Transformer converge effectively and perform in an aligned
way, we further impose a deep supervision loss to the output
node set:
Fig. 8.

The alignment and aggregation of output flows in the U-Transformer.

xis_f me = LN



(1)
(2)
(i)
(H)
ρie , ρie , . . . , ρie , . . . , ρie


(22)

Inter-Flow Attention Driven Output Alignment and Aggregation: Owing to the unique architecture, the U-Transformer model
demonstrates the capability to extract patterns at various levels
of granularity while maintaining excellent scalability. However,
in actual practice, the effective regulation and alignment of the
output nodes are crucial for ensuring the model’s performance.
To address this challenge, we propose an inter-flow attention
driven output alignment and aggregation mechanism (Fig. 8).
For clear descriptions, we denote the output nodes, i.e., the
nodes on the top level of the U-Transformer that generate reconstruction results, as O 0_1 to O 0_4 . Take the aggregation between
O 0_4 and O 0_1 as an example, the output alignment happens as
follows:


(1)
(2)
(i)
(H)
(23)
ρ4,1 = LN ρ4,1 , ρ4,1 , . . . , ρ4,1 , . . . , ρ4,1
where the calculation of the output from different heads is
performed as follows:


(i)
(i)
(i)
(24)
ρ4,1 = Att W (i)
q O 0_4 , W k O 0_1 , W v O 0_1
A more general aggregation that forms the fused output is
then conducted:
ρoaa = O 0_4 ⊕ ρ4,3 ⊕ ρ4,2 ⊕ ρ4,1

(25)

Here, ⊕ denotes the in-place addition operation. Finally, the
 is obtained by applying a mapping
reconstruction result x
operation:
 = Conv1D+S (ρoaa , k1, s1)
x

(26)

Deep Supervision Guided Model Training: Since its introduction, deep supervision has been widely explored for improving
the performance of various downstream tasks [21], [22], [23].
We adapt this technique to the U-Transformer structure to regulate the convergence of the intermediate layers. Take the output
from the output node O 0_4 for example, we impose a similarity
loss to guide its output:
N

Lu0_4 =
t=1

xt − O 0_4 22

(27)

Luds = η0 Lu0_a + η1 Lu0_1 + η2 Lu0_2
+ η3 Lu0_3 + η4 Lu0_4

(28)

where η0 − η4 are the seasoning weights. Lu0_a denotes the
similarity loss applied to the aggregated output in (26).
D. Siamese Discriminator for Embedding Level Discrepancy
Analysis
Overview: As discussed in Section II, most prior works use
segment-wise numerical reconstruction error to identify anomalies. This scheme is less effective for industrial data, especially
the one featuring high dimensionality and high levels of noise
and anomalies. To tackle this unique challenge in industrial scenarios, we design a Siamese discriminator (Fig. 9) that projects
the observed and reconstructed sequences into manifold space,
and adaptively collates their discrepancies at the embedding
level. As such, InoU gains the ability to inspect even the most
subtle inconsistencies between the observed and reconstructed
sequences, which is crucial for improving anomaly detection
performance in industrial settings.
Manifold Projection: To project the target sequences into the
abstract manifold, we design a Siamese backbone that processes
the observed and the reconstructed sequences with a shared set
of parameters in parallel. We define an elementary block in the
Siamese backbone as follows:
xse1 = Conv1D+S(xin , k3, s1)
xse2 = Res1D(xse1 )
xse3 = BN(MP(xse2 , 2))

(29)

Here, xin is the input of this elementary block, BN is the batch
normalization operation, and MP is the max pooling operation.
Res1D denotes the 1D residual module, which operates as:
xse2 = xse1 ⊕ Conv1D+S(xse1 , k3, s1) × 3

(30)

Based on the elementary block (“Elem” in later parts) described in (29)–(30), we further form the backbone of the
Siamese discriminator. Since the primary function of this backbone is to extract and expose the most salient features for
subsequent discrepancy analyses, its architecture needs to be
carefully crafted to balance feature extraction efficiency and the
ability to capture both low-level and high-level embeddings. To
satisfy this need, we design two distinct output structures for
different purposes: the representation output R that generates

1018

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 18, NO. 2, MARCH/APRIL 2025

the projected manifold of the incoming sequence, and the projection head P that has a relatively deeper structure, and is used
to regulate the convergence.
The representation output is generated as:
R = Elem(xin ) × 4

(31)

Whereas the projection head is further formed through:
xsp1 = Elem(R)
xsp2 = [GRUf (xsp1 ), GRUb (xsp1 )]
P = BN(Conv1D+S(xsp2 , k3, s1))

(32)

Here, GRUf and GRUb represent the forward and backward
calculations in a Bidirectional GRU module.
Inference on Anomalies: The employment of this Siamese
architecture enables us to implement the downstream task of
discrepancy comparison in an efficient yet robust way. By applying a shared set of parameters, i.e., the Siamese backbone,
the target sequences are thus projected into an abstract manifold
space that reveals pivotal metric information. Based on the
projected manifolds, numerical inconsistencies of the concerned
sequences that used to be subtle or less noticeable become much
more pronounced during the embeddings level discrepancy
comparison. In this way, the overall performance of anomaly
detection is enhanced, particularly in industrial scenarios.
To describe this process, we notate a random normal sequence
as xn , and a random anomalous one as xa . As the convergence
of the U-Transformer happens on the filtered training material
Dtrain,f lt , the reconstruction deviation of xa will be significantly larger. Then we can have:
Sim (R(xa ), R(
xa )) → 0

(33)

where Sim is the calculation of cousin similarity:
Sim(α, β) =

αT β
τ1 αβ

(34)

in which  ·  is the L1 Norm, and τ1 is a coefficient to adjust
this calculation. On the other hand, representations for a set of
normal sequences result in a higher similarity:
Sim (R(xn ), R (
xn )) → 1

(35)

Based on the properties of R, we cascade a discriminator
to implement the anomaly detection task. Since the Siamese
backbone processes both the observed sequence and the reconstructed one with a shared set of parameters, the discrepancies
between the two sequences are thus reflected in the embeddings
generated by the R. The output of the backbone is concatenated
as Rcct
t :
Rcct
xt )]
t = [R(xt ), R(

(36)

Then, several blocks are employed for metric analysis:

Training workflow of the Siamese discriminator.

The inference results are generated through:
lt = Softmax(xra )

(38)

t.
where lt is the inference result for the input pair xt and x
Training Workflow: To form an informative manifold space
and ensure the full expression of metrics related to discrepancies,
we design a contrastive learning based training workflow for the
Siamese discriminator. As depicted in Fig. 10, this workflow
comprises two stages: self-supervised contrastive learning and
task-oriented fine-tuning.
1) Self-supervised contrastive learning: In this part, the
Siamese discriminator is trained on unlabeled data in a selfsupervised manner. The U-Transformer is first trained on the
filtered training set Dtrain,f lt . Then, we use the U-Transformer
to process the raw training set Dtrain,raw , and calculate its error
set E. The error set is then used to calculate the threshold κ as
stated in Section III-B, and thereafter generate the pseudo label
set Ipsd . With Dtrain,raw and Ipsd , we use the output from the
projection head in the Siamese discriminator to form the loss for
matched pairs:
xt ))
Dis = 1 − Sim (P(xt ), P(
Lcmatch = Dis × (1 − yt,psd )

(39)

where yt,psd is the pseudo label of xt .
Similarly, for the mismatched pairs, we have:
xt )) × yt,psd
Lcmismatch = Sim (P(xt ), P (

(40)

By integrating the two components as in (39)–(40), we form
the contrastive loss for the Siamese backbone:
Lcsum = τ2 Lcmatch + τ3 Lcmismatch

(41)

where τ2 and τ3 are the seasoning weights.
2) Task-oriented fine-tuning: Apart from the contrastive regulation being applied to the Siamese backbone, we utilize other
techniques to assist in the formation of the manifold. Considering that in some industrial scenarios, a limited amount of labeled
data may be available, a binary cross entropy loss is applied:
N

xma1 = BN(Conv1D+S(Rcct
t , k3, s2))

Ldbce = −

xma2 = BN(Conv1D+S(xma1 , k3, s1))
xra = Conv1D(Flatten(xma2 ), k1, s1)

Fig. 10.

(37)

1
[yt · log(p(yt ))
N t=1

+ (1 − yt ) · log(1 − p(yt ))]

(42)

YAO et al.: SCALABLE LARGE MODEL FOR UNLABELED ANOMALY DETECTION

1019

Here, yt is the ground-truth label of the limited dataset. Besides,
a center loss [24] is also employed to enhance the inter-class
sparsity:
N

Ldctr =

1
R(xt ) − cyt 22
N t=1

(43)

where cyt is the cluster for xt in the feature space. Based on (42)–
(43), the following sum loss is formed to optimize the Siamese
discriminator:
Ldsum = Ldbce + Ldctr

(44)

However, scenarios with no available human labeled resources are also common in industrial applications. To address
this situation, the ground-truth labels yt can be replaced with the
pseudo labels yt,psd . This workaround also effectively supports
the training of InoU, as it is validated later in Section IV-D.

Fig. 11.

Anomaly cause visualization.

TABLE I
DATASET PROPERTIES

E. Manifold Adjusting Via Adversarial Learning
In industrial scenarios, on-site data usually contain a considerable proportion of noise and anomaly components. Besides,
historical recordings may not cover all cases in actual deployment. To enhance InoU’s ability to spot historically unobserved
samples and to improve the Siamese discriminator’s capacity
for metric expression in the manifold space, we introduce an
adversarial learning based manifold adjusting scheme.
With the two primary components, i.e., U-Transformer and
the Siamese discriminator, being integrated under the unified
framework, InoU naturally fits the concept of an adversarial
architecture. Driven by this finding, the following adversarial
loss is applied:
u
d
Ladv
sum = min Lds + min Lsum
MU-Tran

+ max

MSiamese

min τ2 Lcmatch

MU-Tran MSiamese

+ min τ3 Lcmismatch
MSiamese

(45)

To ensure that the minor yet stable alternation to the learned
parameters, the adversarial loss is applied with a small learning
rate. The effects of this adversarial pipeline are validated and
illustrated in Section IV-H.
F. Anomaly Cause Localization
In the middle of an undesirable event, localization of anomaly
cause assists engineers in identifying the most probable origin
of the incident. As such, the process to re-gain control of the
case can be expedited. To realize this goal, we analyze the intermediate vector xra in the Siamese discriminator (37), and infer
their contribution to the formation of an anomalous event. The
visualization in Fig. 11 is presented on an anomalous sample.
IV. EVALUATION
A. Datasets and Metrics
Dataset: We incorporate five large-scale industrial datasets
to evaluate the performance of InoU under different industrial

scenarios. These datasets are widely used in many other anomaly
detection works.
1) SMD [10]: This dataset contains KPI (Key Performance
Indicator) recordings from a computing center of a cloud service
provider.
2-3) SWaT [25] & WADI [25]: The Secure Water Treatment
(SWaT) and the Water Distribution (WADI) are two datasets that
record the operation status of attacked water treatment systems.
4-5) SMAP [26] & MSL [26]: The Soil Moisture Active Passive (SMAP) and the Curiosity Rover on Mars (MSL) datasets
contain telemetry recordings from spacecrafts.
The properties of these datasets are listed in Table I.
Metrics: We use the metric set as in other works to reflect a concerned system’s overall anomaly detection performance: Precision, Recall, and F1-Score. Their calculations are
TP
TP
, Recall = TP+FN
, and F1-Score =
as follows: Precision = TP+FP
2×Precision×Recall
.
Precision + Recall

B. Baselines and the Test Environment
Baselines: We compare the performance of InoU with
state-of-the-art works: VAE-LSTM [9], OmniAnomaly [10],
USAD [11], InterFusion [12], CAE-M [13], AMSL [15],
TranAD [27], and AnoTran [28]. We also employ a classical
algorithm, Isolation Forest, for performance comparison, though
not involve it in the discussions.
Environment: We use a workstation to conduct the evaluation.
Its main configurations are listed in Table II.
Parameters: Table III lists the parameters used to train InoU.
The arguments are left as the default if not otherwise specified.

1020

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 18, NO. 2, MARCH/APRIL 2025

TABLE II
TESTBED CONFIGURATION

compared to these baselines, enabling engineers to identify and
address potential issues promptly.
We continue discussing the effectiveness of our design in InoU
in the following sections.
D. Validation of InoU When Strictly Unsupervised

TABLE III
PARAMETERS

C. Performance and Analysis
In this section, we compare the anomaly detection performance of InoU with the baselines. During this experiment, all
results are the average of three randomized trials. The overall
performance results are presented in Table IV.
It can be observed that InoU outperforms the baselines on
every dataset in terms of F1-Score. On these large, real-world,
industrial datasets, InoU gets the best average F1-Score of
0.9168, with an increment of 5.58% compared to the state-ofthe-art. Among these results, several findings should be noted.
All baselines’ performance slightly drops on the WADI dataset,
possibly due to its low anomaly portion and high dimension.
InoU, however, achieves a boost in F1-Score of 28.20% on
this dataset. This finding echoes the observations on the SWaT
and MSL datasets, which are characterized by their high dimensionality. The utilization of the Siamese discriminator in InoU
also yields significant improvements in F1-Score on the two
datasets: the SWaT dataset with 51 features and the MSL dataset
with 55 features. Respectively, InoU achieves a performance
improvement in F1-Score by 3.08% and 2.53% on these two
datasets.
Moreover, our proposed work InoU demonstrates significant
performance improvement, even on datasets where the state-ofthe-art models already perform well. On the SMD and SMAP
datasets, InoU achieves a substantial increase in the F1-Score
by 1.08% and 1.64%, respectively. These results validate the
effectiveness of InoU across various datasets, highlighting its
robust performance in industrial anomaly detection.
Apart from the results suggested by the F1-Score, we can also
observe the robustness of InoU from other aspects. It is clear
from Table IV, InoU achieves the best recall performance on
SMD, SWaT, SMAP, and MSL, and its recall is the second-best on
WADI. A higher recall is crucial in industrial applications, as it
represents the ability to accurately detect all anomalous samples
without missing any. The improvement in recall indicates a
notable reduction in the number of undetected anomaly samples

InoU is designed to utilize unlabeled industrial datasets to
the greatest extent. By developing a training pipeline that incorporates a VAE filter, contrastive / adversarial learning, and
task-oriented fine-tuning, the robustness of InoU gets improved.
In this section, we use ablation studies to discuss the potential
impacts caused by the materials used in the fine-tuning process
of the Siamese discriminator. Three cases are introduced in this
experiment:
1) Best Baseline: the results of the best baseline, namely
AnoTran [28].
2) Strictly Unsupervised: the calculation of (42) relies only
on the pseudo label set Ipsd that the U-Transformer produces. In this case, no human labeled resource is involved.
3) Fine-tuned: the original training workflow as introduced
in Section III-D.
In this ablation study, we select three industrial datasets covering low, medium, and high numbers of features to obtain a more
generalizable conclusion. The experiment results are presented
in Table V.
As suggested by the data, a slight performance drop can be
observed when InoU is trained on a fully unlabeled dataset.
It is clear that the effectiveness of the strict unsupervised
manner shows connections with characteristics of the dataset
being processed. In the case of strictly unsupervised manner,
high-dimensional dataset, e.g., WADI, may experience a more
brutal performance impact than those with fewer features, such
as SWaT and SMAP. This finding indicates that expert domain
knowledge and human-labeled materials continue to play a significant role in enhancing the performance of anomaly detection
systems.
However, it is worth noting that InoU, when trained strictly
unsupervised, still beats the best baseline on these datasets, with
an increment in the average F1-Score of 5.40%. This is to say,
though removing limited labeled data from the training materials when fine-tuning the Siamese discriminator may lead to a
slight performance impact, InoU still provides a competitive and
robust performance for the anomaly detection task in industrial
environments.
E. Ablation Study on Critical Components
Under the framework of InoU, many critical components are
designed to work seamlessly and function effectively. In this
section, we design an ablation study to assess their impacts on
the overall performance of InoU. The concerned components
include:
1) deep supervision in the U-Transformer (28);
2) implementation of the recurrent layers in Siamese
discriminator (32);
3) the filter in the data pre-processing workflow
(Section III-B);

YAO et al.: SCALABLE LARGE MODEL FOR UNLABELED ANOMALY DETECTION

1021

TABLE IV
ANOMALY DETECTION PERFORMANCE. MP: MEAN PRECISION, MR: MEAN RECALL, MF1: MEAN F1-SCORE

TABLE V
PERFORMANCE COMPARISON IN A STRICTLY UNSUPERVISED MANNER

Fig. 12.

To finish these experiments, the following configurations are
deployed correspondingly:
C1) we deactivate deep supervision on nodes O 0_1 to O 0_3
(C1-NS), keep deep supervision on nodes O 0_3 and O 0_4 (C1HS), and compare these two variants with the fully activated
deep supervision in InoU (C1-DS).
C2) we compare two other variants of recurrent structure, i.e.,
RNN (Recurrent Neural Network) and LSTM (Long Short-Term
Memory) with the GRU module used in our work. These variants
are marked as C2-RNN, C2-LSTM, and C2-UM, respectively.
C3) we use the Spectral Residual technique to replace the
VAE filter in our data processing pipeline. Results are noted as

Ablation study on the effects of critical components.

C3-SR (Spectral Residual), and C3-VAE (our original version
that enables the VAE filter).
We provide the results in Fig. 12. Listed below are the key
findings:
Effects of the deep supervision: The removal of deep supervision results in noticeable differences in performance on the
tested datasets. For the C1-HS, the drop of F1-Score is less
significant on SMD (4.74%) than on SMAP (6.76%). On the
other hand, the C1-NS variant performs better on SMAP with a
drop of 13.94%, milder than the one on SMD (15.82%). As the
results reflect, it is straightforward that deep supervision helps

1022

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 18, NO. 2, MARCH/APRIL 2025

Fig. 13. Performance and computation overhead of different variants of the
U-Transformer. Solid line: F1-Score; Dashed line: Parameter amount.

regulate the update of parameters in the intermediate layers and
gains a better performance.
Effects of the recurrent module: The results across the datasets
indicate that GRU in our model is more efficient than its two
variants in bridging temporal connections. This finding is intuitive for the following reasons. As discussed in [29], the RNNs
suffer from gradient problems, potentially limiting their ability
to capture long-term dependencies. Due to the trio-gate design,
the LSTM network is computationally heavy, which may lead
to difficulties converging on noisy materials. These factors may
contribute to the performance limitations of these two variants.
Effects of the filter module: Industrial data usually contain
noise and anomalous samples, whereas human labeling is laborious and time-consuming. To elevate anomaly detection
performance in such scenarios, we introduce an efficient VAE
filter in the data pre-processing pipeline to offset the impacts
of noised and anomalous samples. Though Spectral Residual
offers a solution for data cleaning, its insufficient utilization of
contextual information can result in a performance drop when
processing complex industrial data.

Fig. 14.

Performance across different anomaly portions.

O 0_3 provides a more efficient solution (25% parameter amount
with 98% performance). As for O 0_2 , its parameter amount is
comparable to O 0_1 , but comes up with a 4% to 14% increment
in F1-Score.
To summarize, the nested structure built in U-Transformer
enables the model to sense and capture multi-scale context
information from different levels. Thus, it is possible to adjust
the overall computation overhead by altering the flow through
which data are passed. By doing so, the model can be adapted
to various deployment scenarios, while maintaining a high level
of anomaly detection performance.
G. Impacts of Anomaly Portion

F. Scalability of the U-Transformer
The U-Transformer in the InoU framework is designed with a
nested structure, enabling this structure to capture multi-scale information while maintaining excellent scalability and efficiency.
To evaluate the scalability of the U-Transformer, we conduct
experiments to assess its performance under different trimming
settings. To be specific, we capture the output from O 0_1 to
O 0_4 , and connect these outputs to the Siamese discriminator
for the task of anomaly detection. The performance of trimmed
versions of the U-Transformer is compared with that of the
full-size model. We present the corresponding results in Fig. 13.
It is straightforward that, the original, full-sized model that
outputs from O 0_4 achieves the best anomaly detection results
on the tested dataset. However, this output flow also incurs
the heaviest computation overhead, as it activates most of the
parameters in the U-Transformer. On the contrary, O 0_1 is the
most computation-efficient flow in the nested structure. From
these figures, we can observe a parameter reduction of up to
97% with a general 10% - 20% performance drop. For the
two intermediate output nodes O 0_2 and O 0_3 , a more flexible
solution can be achieved between computation cost and performance, addressing the needs for varied deployment targets. The

The datasets used for experiments exhibit a noticeable imbalance, with anomalies being substantially underrepresented compared to normal samples. This disparity reflects the real-world
scenario where anomalies are typically rare events. However, it
is important to note that the frequency of anomalies can fluctuate
considerably in industrial environments due to the diverse and
often unpredictable operational conditions of on-site equipment
and processes.
To assess the robustness of InoU across varying levels of
anomaly percentages, we conduct experiments on two representative datasets, namely the SWaT and SMAP. The test set
is varied to include different proportions of anomalies, ranging
from 1% to 30%. Specifically, we evaluate performance at seven
distinct anomaly levels: 1%, 5%, 10%, 15%, 20%, 25%, and
30% anomalies. Precision, Recall, and F1-Score results of this
experiment are presented in Fig. 14.
In general, InoU maintains a high availability of anomaly
detection across different anomaly portions. At the extremely
low anomaly percentage (1%), a decrease can be observed in
the performance of InoU on both datasets. On the SWaT dataset,
the F1-Score drops to 0.9001 when the anomaly percentage is
set to 1%. The decrease in SMAP is less pronounced, with the

YAO et al.: SCALABLE LARGE MODEL FOR UNLABELED ANOMALY DETECTION

Fig. 15. Visualization of the Manifold Space of the Projection Head in the
Siamese Discriminator. Blue points: representations of normal samples; Red
points: representations of anomalies.

F1-Score keeping at a relatively high level of 0.9467. However,
in other cases, the anomaly detection performance of InoU
remains stable. For anomaly percentages from 5% to 30%, the
F1-Score of InoU on the two datasets is consistently high, fluctuating around 0.94 and 0.98 on SWaT and SMAP, respectively.
This finding suggests that InoU is capable of maintaining a
robust anomaly detection performance across a wide range of
anomaly percentages. Even under extreme conditions, where the
anomaly percentage is as low as 1%, InoU still delivers a robust
performance.

H. Impacts of Contrastive and Adversarial Learning
Techniques
We incorporate contrastive learning as a crucial part of the
training of Siamese discriminator (Section III-D). Besides, adversarial learning is employed to further optimize the distribution of the manifold space and improve the expression of metrics
related to discrepancies. In this section, we use experiments to
compare the manifold space of the Siamese discriminator under
different training settings.
Specifically, we visualize the manifold of the projection head
P of the Siamese discriminator (as described in (32)) on the
SMAP dataset using the t-SNE algorithm. During this comparison, three typical cases are considered:
1) Only With Cross Entropy. Train the Siamese discriminator
using only (42).
2) Cross Entropy + Contrastive. Train the Siamese discriminator using both (41) and (44).
3) After Adversarial Tuning. Train the Siamese discriminator
using both (41) and (44). Then, fine-tune the manifold with
(45).
We can observe from Fig. 15 that the employment of the
proposed training protocol optimizes the manifold space of the

1023

Siamese discriminator and consequently enhances the detection
performance.
For comparison, when only trained with cross entropy, the
distribution of embeddings in the manifold appears more intermingled. As depicted in the lower dimension, the representation
of samples, both normal and anomalous ones, are sparsely
distributed in the manifold space. Consequently, the distinction
between these two classes becomes blurred, which may compromise the detection performance when encountering unobserved
or ambiguous anomalous samples if the samples are projected
into overlapping regions.
On the other hand, the condensation is improved with the help
of contrastive learning. This technique encourages the projection
of samples to be clustered and informative. As a result, the
compact localization of both normal and abnormal samples
is achieved, thereby improving the clarity of the distribution
characteristics.
In addition, the adversarial tuning further optimizes the manifold space of the Siamese discriminator. This process adjusts
the distribution of the embeddings, so that the clusters become
more pronounced and distinguishable. In this way, the separation between normal and anomalous samples is more distinct,
which in turn enhances the detection capabilities of the Siamese
discriminator.
V. RELATED WORK
The advancement of the industry has brought a surge in the
scale of deployed assets. To ensure the smooth of their operation
and reduce the cost of downtime, the reliability of these systems
has become a critical concern.
Some works deploy their models near the deployed assets
to get a reduced response time. Work [30] uses statistics Mahalanobis distances as the metrics for early-stage fault diagnosis. Researchers [31] introduce clustering and k-means for
fast anomaly filtering. However, performing anomaly detection
locally on the device is challenging due to limited power and
computation capacity. They then have to rely on a slim model or
simple rules, resulting in spaces for performance improvement.
Other works embrace deep learning techniques in their workflow to get more robust results. Kim et al. [32] discuss the
possibility of using CNN (Convolutional Neural Network) for
feature extraction in anomaly detection. Canizo et al. [33]
further adopt CNN and RNN (Recurrent Neural Network) as
the backbone, using a classification-based workflow to achieve
anomaly detection. However, discriminant models are prone
to overfit when the dataset is not properly balanced, which
is common in this scenario. Consequently, their performance
gets worse in the presence of unobserved anomalous sequences.
Considering this, researchers are shifting to generative models,
i.e., AE (Autoencoder) and VAE (Variational Autoencoder).
Luo et al. [34] propose an AE based anomaly detection approach for WSN (Wireless Sensor Network) that compares the
observed and predicted sequences from sensors. Researchers
in [9] combine VAE and LSTM to capture long-time dependencies in time series, so that short and long-period anomalies
can be spotted. Su et al. [10] use planar normalizing to process

1024

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 18, NO. 2, MARCH/APRIL 2025

the stochastic variables in VAEs, and Li et al. [12] incorporate
inter-metric and temporal embeddings to improve its anomaly
detection performance on multivariate time series. VAEs provide
a new perspective to reconstruct data, but their utilization is not
straightforward. Being an unsupervised model, this model can
hardly be trained when the distribution of the dataset is skewed.
Besides, the design of VAEs needs careful consideration to avoid
under-fit or over-fit problems [35].
Targeting the model over-expression problem, there are
mainly two directions to rectify the reconstruction process. Some
works incorporate memory modules to address the model overexpression problem [13], [15]. On the other hand, some works
deploy an adversarial training protocol to force the decoder to
learn a more robust representation translation approach [11].
Despite their designs, these solutions do not explicitly solve the
problem of fine-grained discrepancy analysis, and training such
structures is also challenging.
There are other endeavors to enhance the bridging and construction of dependencies in complex multivariate time series
data. Inspired by the advancements in graph learning [36], [37],
[38], [39], GNNs (Graph Neural Network), or more broadly,
graph structures, are applied to enhance the overall performance. In Wu et al. [8], the authors investigate the application of GNN (Graph Neural Network) in IoT anomaly detection. Chen et al. [40] apply supervised contrastive learning
to the graph structure, so that the potential anomalous nodes
are identified and separated. Researchers in [41] use graphs
to project subsequences of original data into embeddings and
compare the characteristics. Ding et al. [42] use three graphs
with inner-modal and inter-modal attentions to extract node
dependencies in multi-modal IoT streams. Tuli et al. [27] involve
a transformer in anomaly detection for better data interpretation. Xu et al. [28] further deploy the concept of transformer
and adjacent-concentration to calculate association discrepancy.
Yang et al. [43] propose a method to examine the correlation
of representations in the latent space for anomaly detection.
Despite the advancements in model design, these solutions face
the challenge of huge overhead and scalability, and thus, may
not be suitable for deployment in an industrial environment.
Besides, most of these works depend on numerical discrepancies
to identify anomalies, which may not be robust enough for
complex industrial data.
VI. CONCLUSION
In this paper, we propose InoU as a scalable solution to
the challenges in prior anomaly detection works. To enable
the self-supervised training protocol and combat impacts from
noise components in training materials, a VAE filter is employed
in the processing pipeline of the target unlabeled data. We
then develop a trio-attention U-Transformer model to capture
intricate patterns and contextual information while maintaining outstanding scalability and efficiency. The ultra perception and intra-/ inter-flow attention based information aggregation enables the model to bridge dependencies across different
levels with variable granularities, but without losing a global

perspective of the data. Furthermore, we design a Siamese
discriminator that projects data into the manifold space, and
adaptively collates discrepancies at the embedding level. We also
introduce contrastive and adversarial learning to fine-tune the
projection of manifold and boost the overall anomaly detection
performance of InoU in industrial scenarios. Extensive experiments on five large-scale industrial datasets suggest significant
performance improvements.
For future work, we propose investigating other deep learning
methodologies, i.e., graph learning and meta learning, to enhance the construction of dependencies. We also plan to explore
potential solutions for optimizing the training overheads.
REFERENCES
[1] G. Wu, H. Wang, H. Zhang, Y. Shen, S. Shen, and S. Yu, “Mean-field
game-based task-offloaded load balance for industrial mobile edge computing systems using software-defined networking,” IEEE Trans. Mobile
Comput., vol. 23, no. 12, pp. 13773–13786, Dec. 2024.
[2] Y. Zhang et al., “Privacy-preserving and fairness-aware federated learning
for critical infrastructure protection and resilience,” in Proc. ACM Web
Conf., 2024, pp. 2986–2997.
[3] X. Zhang et al., “Cost-effective hybrid computation offloading in satelliteterrestrial integrated networks,” IEEE Internet Things J., vol. 11, no. 22,
pp. 36786–36800, Nov. 2024.
[4] D. G. Pivoto, L. F. de Almeida, R. da Rosa Righi, J. J. Rodrigues,
A. B. Lugli, and A. M. Alberti, “Cyber-physical systems architectures
for industrial Internet of Things applications in industry 4.0: A literature
review,” J. Manuf. Syst., vol. 58, pp. 176–192, 2021.
[5] S. Yu, O. Jin, Y. Shen, G. Wu, S. Yu, and S. Shen, “Availability evaluation
of industrial Internet of Things under malware propagation: An extended
reliability block diagram approach based on stochastic games,” IEEE
Trans. Rel., early access, Aug. 2024, doi: 10.1109/TR.2024.3434593.
[6] B. Peng et al., “An intelligent fault diagnosis method for rotating machinery based on data fusion and deep residual neural network,” Appl. Intell.,
vol. 52, no. 3, pp. 3051–3065, 2022.
[7] Z. Chen, D. Chen, X. Zhang, Z. Yuan, and X. Cheng, “Learning graph
structures with transformer for multivariate time-series anomaly detection
in IoT,” IEEE Internet Things J., vol. 9, no. 12, pp. 9179–9189, Jun. 2022.
[8] Y. Wu, H.-N. Dai, and H. Tang, “Graph neural networks for anomaly
detection in industrial Internet of Things,” IEEE Internet Things J., vol. 9,
no. 12, pp. 9214–9231, Jun. 2022.
[9] S. Lin, R. Clark, R. Birke, S. Schönborn, N. Trigoni, and S. Roberts,
“Anomaly detection for time series using VAE-LSTM hybrid model,”
in Proc. 2020 IEEE Int. Conf. Acoust. Speech Signal Process., 2020,
pp. 4322–4326.
[10] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 2828–2837.
[11] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,” in
Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 3395–3404.
[12] Z. Li et al., “Multivariate time series anomaly detection and interpretation
using hierarchical inter-metric and temporal embedding,” in Proc. 27th
ACM SIGKDD Conf. Knowl. Discov. Data Mining, 2021, pp. 3220–3230.
[13] Y. Zhang, Y. Chen, J. Wang, and Z. Pan, “Unsupervised deep anomaly
detection for multi-sensor time-series signals,” IEEE Trans. Knowl. Data
Eng., vol. 35, no. 2, pp. 2118–2132, Feb. 2023.
[14] H.-Z. Feng, K. Kong, M. Chen, T. Zhang, M. Zhu, and W. Chen, “SHOTVAE: Semi-supervised deep generative models with label-aware ELBO
approximations,” in Proc. AAAI Conf. Artif. Intell., 2021, pp. 7413–7421.
[15] Y. Zhang, J. Wang, Y. Chen, H. Yu, and T. Qin, “Adaptive memory networks
with self-supervised learning for unsupervised anomaly detection,” IEEE
Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12068–12080, Dec. 2023.
[16] H. Gao, B. Qiu, R. J. D. Barroso, W. Hussain, Y. Xu, and X. Wang,
“TSMAE: A novel anomaly detection approach for Internet of Things time
series data using memory-augmented autoencoder,” IEEE Trans. Netw. Sci.
Eng., vol. 10, no. 5, pp. 2978–2990, Sep./Oct. 2023.

YAO et al.: SCALABLE LARGE MODEL FOR UNLABELED ANOMALY DETECTION

[17] K. Deshpande, N. S. Punn, S. K. Sonbhadra, and S. Agarwal, “Anomaly
detection in surveillance videos using transformer based attention model,”
in Proc. Int. Conf. Neural Inf. Process., 2022, pp. 199–211.
[18] O. Ronneberger, P. Fischer, and T. Brox, “U-net: Convolutional networks
for biomedical image segmentation,” in Proc. 18th Int. Conf. Med. Image
Comput. Comput.-Assisted Intervention, 2015, pp. 234–241.
[19] Z. Zhou, M. M. R. Siddiquee, N. Tajbakhsh, and J. Liang, “UNet:
Redesigning skip connections to exploit multiscale features in image
segmentation,” IEEE Trans. Med. Imag., vol. 39, no. 6, pp. 1856–1867,
Jun. 2020.
[20] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural Inf.
Process. Syst., 2017, pp. 6000–6010.
[21] C. Li, M. Z. Zia, Q.-H. Tran, X. Yu, G. D. Hager, and M. Chandraker, “Deep
supervision with intermediate concepts,” IEEE Trans. Pattern Anal. Mach.
Intell., vol. 41, no. 8, pp. 1828–1843, Aug. 2019.
[22] Y. Liu, M.-M. Cheng, D.-P. Fan, L. Zhang, J.-W. Bian, and D. Tao,
“Semantic edge detection with diverse deep supervision,” Int. J. Comput.
Vis., vol. 130, no. 1, pp. 179–198, 2022.
[23] Y. Sun, D. Dai, Q. Zhang, Y. Wang, S. Xu, and C. Lian, “MSCA-Net:
Multi-scale contextual attention network for skin lesion segmentation,”
Pattern Recognit., vol. 139, 2023, Art. no. 109524.
[24] Y. Wen, K. Zhang, Z. Li, and Y. Qiao, “A discriminative feature learning
approach for deep face recognition,” in Proc. Eur. Conf. Comput. Vis.,
2016, pp. 499–515.
[25] J. Goh, S. Adepu, K. N. Junejo, and A. Mathur, “A dataset to support
research in the design of secure water treatment systems,” in Proc. 11th
Int. Conf. Crit. Inf. Infrastructures Secur., Paris, France, 2017, pp. 88–99.
[26] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric
dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, 2018, pp. 387–395.
[27] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” Proc.
VLDB Endow., vol. 15, no. 6, pp. 1201–1214, Feb. 2022.
[28] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int. Conf.
Learn. Representations, 2022. [Online]. Available: https://openreview.net/
forum?id=LzQQ89U1qm_
[29] A. H. Ribeiro, K. Tiels, L. A. Aguirre, and T. Schön, “Beyond exploding and vanishing gradients: Analysing RNN training using attractors
and smoothness,” in Proc. 23rd Int. Conf. Artif. Intell. Statist., 2020,
pp. 2370–2380.
[30] H. Ji, “Statistics Mahalanobis distance for incipient sensor fault detection
and diagnosis,” Chem. Eng. Sci., vol. 230, 2021, Art. no. 116233.
[31] H. Zhang, H. Chen, Y. Guo, J. Wang, G. Li, and L. Shen, “Sensor fault
detection and diagnosis for a water source heat pump air-conditioning
system based on PCA and preprocessed by combined clustering,” Appl.
Thermal Eng., vol. 160, 2019, Art. no. 114098.
[32] T. Kim, S. C. Suh, H. Kim, J. Kim, and J. Kim, “An encoding technique for
CNN-based network anomaly detection,” in Proc. 2018 IEEE Int. Conf.
Big Data, 2018, pp. 2960–2965.
[33] M. Canizo, I. Triguero, A. Conde, and E. Onieva, “Multi-head CNN–
RNN for multi-time series anomaly detection: An industrial case study,”
Neurocomputing, vol. 363, pp. 246–260, 2019.
[34] T. Luo and S. G. Nagarajan, “Distributed anomaly detection using autoencoder neural networks in wsn for IoT,” in Proc. 2018 IEEE Int. Conf.
Commun., 2018, pp. 1–6.
[35] D. S. Tan, Y.-C. Chen, T. P.-C. Chen, and W.-C. Chen, “TrustMAE: A
noise-resilient defect classification framework using memory-augmented
auto-encoders with trust regions,” in Proc. IEEE/CVF winter Conf. Appl.
Comput. Vis., 2021, pp. 276–285.
[36] M. Li et al., “Guest editorial: Deep neural networks for graphs: Theory,
models, algorithms, and applications,” IEEE Trans. Neural Netw. Learn.
Syst., vol. 35, no. 4, pp. 4367–4372, 2024.
[37] L. Bai et al., “HAQJSK: Hierarchical-aligned quantum Jensen-Shannon
kernels for graph classification,” IEEE Trans. Knowl. Data Eng., vol. 36,
no. 11, pp. 6370–6384, Nov. 2024.
[38] C. Huang, M. Li, F. Cao, H. Fujita, Z. Li, and X. Wu, “Are graph convolutional networks with random weights feasible?,” IEEE Trans. Pattern
Anal. Mach. Intell., vol. 45, no. 3, pp. 2751–2768, Mar. 2023.
[39] K. Huang et al., “How universal polynomial bases enhance spectral
graph neural networks: Heterophily, over-smoothing, and over-squashing,”
2024, arXiv:2405.12474.
[40] B. Chen et al., “GCCAD: Graph contrastive coding for anomaly detection,”
IEEE Trans. Knowl. Data Eng., vol. 35, no. 8, pp. 8037–8051, Aug. 2023.

1025

[41] P. Boniol and T. Palpanas, “Series2graph: Graph-based subsequence
anomaly detection for time series,” Proc. VLDB Endow., vol. 13, no. 12,
pp. 1821–1834, Jul. 2020.
[42] C. Ding, S. Sun, and J. Zhao, “MST-GAT: A multimodal spatial–temporal
graph attention network for time series anomaly detection,” Inf. Fusion,
vol. 89, pp. 527–536, 2023.
[43] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “Dcdetector: Dual attention contrastive representation learning for time series anomaly detection,”
in Proc. 29th ACM SIGKDD Conf. Knowl. Discov. Data Mining, New York,
NY, USA: Association for Computing Machinery, 2023, pp. 3033–3045.

Muyan Yao (Member, IEEE) received the BS degree from the School of Electronic and Information
Engineering, Beijing Jiaotong University, Beijing,
China, in 2020. He is currently working toward the
PhD degree. His research interests include ubiquitous
computing and representation learning.

Dan Tao (Member, IEEE) received the BS and MS
degrees from Jilin University, China, in 2001 and
2004, and the PhD degree from the Beijing University
of Posts and Telecommunications, China, in 2007.
She was a visiting scholar with the Illinois Institute
of Technology, Chicago, IL, USA, from 2010 to
2011. She is currently a professor with the School
of Electronic and Information Engineering, Beijing
Jiaotong University, China. Her research interests
include wireless networks, Internet of Things, and
mobile computing.

Peng Qi (Member, IEEE) received the PhD degree
from the School of Computer Science, Beijing University of Posts and Telecommunications, Beijing,
China, in 2022. He is currently with the School
of Electronic and Information Engineering, Beijing
Jiaotong University, Beijing. His research interests
include data analysis, IoT, recommendation systems,
and LLM.

Ruipeng Gao (Member, IEEE) received the BS
degree from the Beijing University of Posts and
Telecommunications, China, in 2010, and the PhD
degree from Peking University, China, in 2016. He
was a visiting scholar with Purdue University, USA,
from 2018 to 2019. He is currently a professor with
the School of Cyberspace Science and Technology,
Beijing Jiaotong University, Beijing. His research
interests include mobile computing and applications,
Internet of Things, and intelligent transportation
systems.
PAPER_TEXT
