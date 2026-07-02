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
# [356] ADPS: Asymmetric Distillation Postsegmentation for Image Anomaly Detection
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
编号：356
题名：ADPS: Asymmetric Distillation Postsegmentation for Image Anomaly Detection
年份：2024
DOI：10.1109/tnnls.2024.3390806
来源：IEEE Transactions on Neural Networks and Learning Systems
PDF：paper/10.1109_TNNLS.2024.3390806.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\356.txt
- 原始字符数：67071
- 本次发送字符数：67071
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 4, APRIL 2025

7051

ADPS: Asymmetric Distillation Postsegmentation
for Image Anomaly Detection
Peng Xing , Hao Tang , Jinhui Tang , Senior Member, IEEE, and Zechao Li , Senior Member, IEEE

Abstract— Knowledge distillation-based anomaly detection
(KDAD) methods rely on the teacher–student paradigm to
detect and segment anomalous regions by contrasting the unique
features extracted by both networks. However, existing KDAD
methods suffer from two main limitations: 1) the student network
can effortlessly replicate the teacher network’s representations
and 2) the features of the teacher network serve solely as a
“reference standard” and are not fully leveraged. Toward this
end, we depart from the established paradigm and instead
propose an innovative approach called asymmetric distillation
postsegmentation (ADPS). Our ADPS employs an asymmetric
distillation paradigm that takes distinct forms of the same image
as the input of the teacher–student networks, driving the student
network to learn discriminating representations for anomalous
regions. Meanwhile, a customized Weight Mask Block (WMB)
is proposed to generate a coarse anomaly localization mask that
transfers the distilled knowledge acquired from the asymmetric
paradigm to the teacher network. Equipped with WMB, the
proposed postsegmentation module (PSM) can effectively detect
and segment abnormal regions with fine structures and clear
boundaries. Experimental results demonstrate that the proposed
ADPS outperforms the state-of-the-art methods in detecting
and segmenting anomalies. Surprisingly, ADPS significantly
improves average precision (AP) metric by 9% and 20% on
the MVTec anomaly detection (AD) and KolektorSDD2 datasets,
respectively.
Index Terms— Anomaly detection (AD), asymmetric distillation, postsegmentation module (PSM), weight mask block
(WMB).

I. I NTRODUCTION

A

NOMALY detection (AD) strives to identify abnormal
images and segment the anomalous regions [1], [2], [3],
[4], [5], [6]. Its broad applications span from industrial defect
detection [4], [7], [8], [9], [10], [11], [12], [13] and medical
image diagnosis [14], [15], [16], [17], [18] to the emerging
domain of autonomous driving [19], [20]. However, the task
of AD is fundamentally different from general classification
or segmentation tasks, as anomalies are hard to define and
impossible to categorize exhaustively. Therefore, AD models
are trained with normal images. Relying only on normal
Manuscript received 13 July 2023; revised 8 January 2024; accepted
15 April 2024. Date of publication 29 April 2024; date of current version
7 April 2025. This work was supported in part by the National Natural
Science Foundation of China under Grant U20B2064 and Grant U21B2043.
(Corresponding author: Zechao Li.)
The authors are with the School of Computer Science and Engineering,
Nanjing University of Science and Technology, Nanjing 210094, China
(e-mail: xingp_ng@njust.edu.cn; tanghao0918@njust.edu.cn; jinhuitang@
njust.edu.cn; zechao.li@njust.edu.cn).
Digital Object Identifier 10.1109/TNNLS.2024.3390806

sample modeling poses a great challenge to detect and segment
anomalies.
Substantial advancements in AD have occurred in recent
years, with reconstruction-based methods dominating the landscape [10], [21], [22], [23], [24], [25]. The methodology
behind these approaches is based on training an autoencoder
under a self-supervised paradigm to ensure that out-ofdistribution anomalous images are reconstructed with notable
errors. The anomalies can then be spotted by assessing the
difference between the reconstructed and original image at a
high resolution. Innovations such as the self-supervised tasks
proposed by Fei et al. [10], focusing on rotation and color
prediction, and by Salehi et al. [23], utilizing image patch sorting, have significantly bolstered the efficacy of this approach.
Meanwhile, MemAE [21] undermines the generalization ability of the autoencoder by introducing a memory module that
enables the recovery of images solely via the stored features.
These techniques aspire to inflate the reconstruction error of
the anomalous images by increasing the image reconstruction
complexity, thereby proving an effective tool to detect out-ofdistribution data “unseen” by the model.
Recent studies have shown that knowledge distillation-based
anomaly detection (KDAD) methods are promising [4], [12],
[13], [26], [27], [28], which enable the student network to
learn the consistent representation from the teacher network
for normal images. Subsequently, the difference in knowledge
representation between the teacher network and the student
network is utilized as an AD way, that is, the difference
between the features extracted by the teacher–student networks. In the conventional symmetric distillation paradigm,
the teacher network’s features are simply used as a “reference
standard” and the regions in which the features extracted
by the student network do not match them are identified
as anomalies, as shown in Fig. 1(a). However, existing
advanced methods, such as MKDAD [12] and STPM [29],
limit themselves by not delving into the rich knowledge
inherent in the pretrained teacher network. Furthermore, they
stick to a symmetric distillation paradigm which often leads
to over-simulation in the student network, that is, the student
model will extract similar representations to the teacher model
when confronted with anomalous regions, thereby impeding its
ability to generate differentiated representations for anomalous
regions. By observing the results of the symmetric distillation
models as shown in Fig. 2, we experimentally find that
the features generated by the anomaly regions only have
slight differences compared to those generated by the normal

2162-237X © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

7052

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 4, APRIL 2025

Fig. 1. Schematic of (a) conventional distillation-based symmetric paradigm
and (b) proposed asymmetric paradigm.

Fig. 2.
Visualization of the feature differences extracted by different
teacher–student distillation structures. (a) Comparison of using symmetric
or asymmetric distillation paradigm in the proposed ADPS. (b) Comparison
of ADPS with two representative distillation-based methods: MKDAD [12]
and RD [13]. The color of the legend indicates the magnitude of the feature
differences in the teacher–student model. Closer to the “Small” side indicates
smaller feature differences. On the contrary, closer to the “Large” side
indicates large feature differences.

regions, this is particularly problematic when the anomalous
regions are similar to the normal regions.
To address the aforementioned issues, we propose a novel
asymmetric distillation postsegmentation (ADPS) method,
namely ADPS, for image AD, which departs from the common symmetric distillation paradigm by proposing instead
to establish a novel asymmetric distillation paradigm. It is
inspired by the prior reconstruction-based autoencoder that
utilizes asymmetry to augment the complexity of the student
network’s alignment with the teacher network. As illustrated
in Fig. 1(b), ADPS assembles a teacher–student network with
a Weight Mask Block (WMB) and a postsegmentation module
(PSM).
First, the proposed asymmetric distillation paradigm is
applied by ADPS to the teacher–student networks, allowing
the same layer of both networks to process diverse forms
of the same data. Specifically, the holistic image is assigned
to the teacher network while the student network is given
nonoverlapping patches. The insight behind the employed
asymmetric inputs is that the student network is encouraged to explore unique expressive abilities different from
the teacher network, thus enabling the teacher–student networks to generate more differentiated features when meeting

anomalous samples (see Fig. 2). Meanwhile, smaller local
patches can induce the distillation model to focus on identifying minor anomalies within a local region. As a result,
the distilled knowledge obtained by asymmetric distillation
possesses a more powerful anomaly discrimination ability.
Based on the characteristics of the asymmetric distillation
paradigm, a customized WMB is proposed to transfer the
distilled knowledge to the teacher network, exploiting feature
correlations to generate a coarse localization mask. This is
expected to improve the discriminability of the teacher model
to identify abnormal regions. Contemplating that distilled
knowledge may contribute to reducing spurious error and predicting fine anomalies, we develop a novel PSM that implicitly
injects the distilled knowledge into the decoding process
to further explore normal/abnormal distributions and obtain
high-confidence segmentation results with clear boundaries.
Extensive experiments on three benchmark datasets demonstrate the effectiveness of our ADPS, which outperforms the
recent state-of-the-art methods on both the challenging MVTec
AD dataset [4] and KolektorSDD2 [30], achieving more than
9% and 20% improvement, respectively, in terms of the AP
metric for anomaly segmentation. The main contributions of
this work are summarized as follows.
1) We propose a novel ADPS method, that is, ADPS,
which establishes an efficient asymmetric knowledge
distillation paradigm to boost the performance of image
AD.
2) We carefully design the WMB and PSM to incorporate
distilled knowledge and improve the representation of
discriminative features for the abnormal region.
3) Experimental results demonstrate that the proposed
ADPS achieves competitive results on three challenging datasets, particularly in solving AD and anomaly
segmentation simultaneously.
The remainder of this article is arranged as follows.
Section II provides a comprehensive discussion about the
literature directly associated with our work. The technical
details of the proposed ADPS are presented in Section III.
Section IV reports experimental results, ablation studies, and
comprehensive analysis. Ultimately, we summarize our findings and suggestions for future research in Section V.
II. R ELATED W ORK
A. Autoencoder-Based AD
Autoencoder-based methods are a widely used approach for
AD, commonly employing different self-supervised pretext
tasks for training and identifying anomalies by measuring
the pixel-level difference between the original input and the
reconstructed output of the model [20], [31]. Examples of such
methods include AE-SSIM [31], MemAE [21], MGNAD [22],
and DAAD [32], which mainly employ image reconstruction
techniques. Other approaches proposed by Li et al. [33] and
Zavrtanik et al. [34] utilize image inpainting techniques to
complete the content within missing masks, assuming that
the model cannot infer anomalous content. However, due
to the strong ability of potent pixel-level reconstruction,

XING et al.: ADPS: ASYMMETRIC DISTILLATION POSTSEGMENTATION FOR IMAGE ANOMALY DETECTION

these autoencoder-based models sometimes lead to wellreconstructed anomalies, which is referred to as the “identity
shortcut” [35]. To prevent the recovery of abnormal images,
some studies [21], [22], [32], [36], [37] introduce memory modules that store normal features. Meanwhile, other
methods [10], [23] introduce more complex self-supervised
tasks, such as coloring and rotation prediction, to detect
unseen anomalies that cannot be easily recovered. Despite
their strengths, autoencoder-based approaches often struggle
with anomaly segmentation due to high reconstruction errors
in normal regions [35], [38].

7053

the distribution. Rudolph et al. [53] and Roth et al. [54], for
example, utilize normalizing flow to model the relationship
between the original and normal feature distributions. Recent
studies [55], [56] similarly seek to model the distribution
relationship between patches. Notably, the method presented
in [56] introduces visual rotation invariant features and graph
networks. Despite these advancements, a significant challenge
remains: these methods have not yet delivered effective results
in anomaly segmentation.

D. Knowledge Distillation-Based AD
B. Generative Model-Based AD
To overcome the limitations of autoencoder-based methods,
research has explored generative model-based approaches,
such as GAN [39]), as demonstrated in previous works [40],
[41]. In these methods, anomalies are identified if the generated sample significantly differs from the input sample [20],
[40]. AnoGAN [40] is one such method that employs noise
to generate a target image and then compares the differences
between the original and the generated image. However,
during the inference phase, this model suffers from a significant drawback involving computationally expensive and
time-consuming parameter updating processes. To overcome
this issue, EffGAN [42] introduced an encoder that constrains the input noise to its output, successfully alleviating
the time-constraint issue. Further refinements in this direction led to GANomaly [41] and f-AnoGAN [14], which
improved the generator’s ability to impose constraints on spatial feature reconstruction. In parallel, DefGAN [43] improved
the discriminator segment by integrating multiple discriminators. Recently, Hou et al. [32] introduced an additional
discriminator to distinguish the generated image from the
original one, enhancing the quality of generation. While
these developments signify substantial progress, they fail to
effectively handle anomalous samples with minuscule anomaly
regions.
C. Deep Feature Modeling-Based AD
Another distinctive approach to detecting anomalies
involves deep feature modeling-based methods, which assume
the existence of a gap between normal and abnormal distributions. These methods begin by constructing a feature space
specifically for normal images and then determine whether an
image is abnormal by evaluating spatial boundaries [9], [44],
[45], [46], [47], [48]. Among these methods, SPADE [48]
stands out by deploying a pretrained WideResNet50 [49] to
extract patch features. The presence of anomalies is established
by determining whether the tested patch contains k adjacent
normal patches. PaDiM [9] builds on this method by further
refining the process. It utilizes a pretrained model for feature
extraction and models normality at each location using a
multivariate Gaussian distribution [50], [51]. Further efforts
have been made to explore the interrelationships within the
data. For instance, Liu et al. [52] proposed a method that
models the relationship between a data point and its neighbors. Other approaches have attempted to implicitly model

Knowledge distillation-based methods leverage discrepancies in the expressive abilities of the teacher–student
networks, thereby enabling them to extract differential features
when encountering abnormalities. The pioneering work of UStd [26] employed a knowledge distillation model for AD.
MKDAD [12] was subsequently introduced to address a flaw
in U-Std, namely that it only leverages the output of the final
layer. Wang et al. [29] proposed the student–teacher feature
pyramid matching (STPM), implementing the multiscale feature map approach, which differs from MKDAD by utilizing
the discrepancy between multifeature maps to derive localization maps instead of the gradient of the loss function. However,
models with symmetric paradigms or similar structures are
unable to extract differentiated features. RD [13] employs a
pretrained model as an encoder, enabling the student decoder
to align with the encoder. However, it merely employs the
output of the teacher network as a “reference standard” without
further exploiting the strong characteristics of the teacher.
Additionally, while RD predominantly excels in detecting
anomalies, it falls short in accurately segmenting anomalous
regions. To address these limitations, ADPS introduces the
asymmetric distillation paradigm. This paradigm enhances
symmetric distillation paradigms to concentrate on fine anomalies and simultaneously employs Weighted Mask Block and
PSM to amalgamate distilled knowledge with pretrained prior
knowledge. This enables a more nuanced exploration of normal and anomalous feature distributions, which is crucial for
accurately segmenting fine anomalous regions.

III. P ROPOSED A PPROACH
As illustrated in Fig. 3, this article proposes a novel
method called ADPS, which includes an asymmetric distillation paradigm, a WMB and a PSM specialized for AD. The
asymmetric distillation paradigm devises inputs with asymmetry that are utilized to enhance the representation ability
gap of the teacher–student networks, thereby generating more
discriminative differential features to anomalous regions. The
distilled knowledge is further exploited by WMB and injected
into the features extracted from the pretrained teacher network.
PSM accepts features of the teacher network consisting of
prior knowledge and distilled knowledge as input and utilizes
the segmentation module to learn the distribution of normal
features. The detailed architecture of our ADPS is described as
follows.

7054

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 4, APRIL 2025

Fig. 3. Overview of the proposed ADPS framework. The asymmetric distillation paradigm uses asymmetric data (e.g., I /I S and Ti /Si′ ) to stimulate S
in learning effective discriminative representations. WMB generates a coarse localization mask to transfer distilled knowledge to the teacher model with a
powerful representation capability, leading to the feature Ci . Based on WMB, PSM explicitly learns normal and anomaly feature distribution in Ci with a
segmentation module to precisely segment finer anomaly regions. In fact, ADPS applied asymmetric inputs to the input layers, Stage 1 and Stage 2 of the
student model.

A. Asymmetric Distillation Paradigm
In the field of AD, knowledge distillation has been leveraged to exploit the differential knowledge representation
abilities possessed by the teacher and student networks to
accurately identify anomalous regions from extracted features. However, a crucial drawback of conventional distillation
frameworks, such as the symmetric distillation paradigm
depicted in Fig. 2(a), is that the teacher–student network
becomes insensitive to disparities in the representation of
anomalous regions. This insensitivity stems from the fact
that the teacher and student networks tend to learn analogous representations of anomalous regions. Thus, to address
these concerns, a feasible solution is to widen the discrepancy in the representational abilities of the teacher–student
networks.
The representational abilities of a model are inherently
linked to its inputs. Therefore, modifying different inputs for
teacher–student networks can obtain different knowledge representation capabilities. We propose an asymmetric distillation
paradigm, wherein we construct semantically equivalent, yet
structurally different inputs for the teacher–student networks.
The disparity in format aims to probe their expressiveness
while simultaneously escalating the difficulty of alignment
between the student and teacher networks for unfamiliar
anomalous regions. As a result, the preservation of the same
semantic guarantees that, through training, the student network
learns the same features as the teacher network for normal
samples. Another key factor is that the local features obtained
by the student network are affected only by their own patches
and do not stray from anomalous feature vectors in remote
parts.

Our ADPS proposes a straightforward yet effective approach
for generating distinct but semantically identical data by
splitting original images. To implement this approach, a given
normal image I ∈ R H ×W ×C , is split into nonoverlap2
j
j
ping local patches, I S = {I S1 , . . . , I S , . . . , I Sk }, where I S ∈
(H/k)×(W/k)×C
2
R
, and k denotes the number of 2-D patches.
In the teacher network, I serves as the direct input, and feature
Ti is obtained by a pretrained encoder in stage i. The use of
the original image as input in the teacher model assures that
Ti does not lose any information about the original image.
Meanwhile, in the student network, I S is utilized as a series
of inputs. In fact, this takes k 2 forward processes, and in
each forward a patch j of (H/k) × (W/k) × C is fed into
j
the student network to extract Si . During k 2 times forward,
we can obtain I in the feature representation of the student
2
j
network, that is, Si′ = {Si1 , . . . , Si , . . . , Sik }. During the
parameter update, the extracted Si′ is subsequently reshaped
into Si based on the original position correspondence, and
Si is calculated as the loss by distillation loss with Ti .
The approach, named asymmetric distillation paradigm, could
theoretically extend to feature distillation in every intermediate
layer by simply splitting features extracted by the intermediate
layer.
Since the student network receives a patch of
(H/k) × (W/k) × C as the input, it will pay more attention
to local regions and detect tiny anomalies. Additionally,
the asymmetry between local and global receptive fields
can exacerbate the complexity of feature alignment in
teacher–student networks. The different inputs allow the
student network to acquire unique data representation
abilities. Therefore, the distilled knowledge of the asymmetric

XING et al.: ADPS: ASYMMETRIC DISTILLATION POSTSEGMENTATION FOR IMAGE ANOMALY DETECTION

distillation paradigm presents higher discrimination efficiency
between normal and abnormal patterns.
B. Weight Mask Block
Given that prior knowledge in the pretrained teacher
network is acquired from an upstream task, such as image classification, it lacks discriminability for normal and abnormal
patterns. To further utilize the pretrained a priori knowledge
for AD, the proposed WMB transfers distilled knowledge to
the teacher network. Formally, “distilled knowledge” refers to
the rough localization information of the anomalous region
obtained through the asymmetric distillation model. Specifically, features extracted from the teacher and student networks
in the asymmetric distillation paradigm are utilized to generate
a coarse localization mask (i.e., distilled knowledge, as mentioned above). We then take a weighted approach to explicitly
transfer the distilled knowledge to Ti .
An overview of our approach is presented in Fig. 3, where
WMB takes Ti and Si as inputs that belong to Rh×w×c . The
correlation of Ti and Si is utilized to generate the coarse
localization mask, with the cosine similarity function being
used for this purpose. Specifically, the similarity between x
and y positions in the feature map is defined as
x,y

Wi

=

Ti
Ti

x,y

x,y

x,y

x,y

· Si
x,y
× Si

(1)

x,y

where Ti
∈ R1×1×c and Si
∈ R1×1×c . The similarity of each position is then evaluated to form the matrix
x,y
Wi = {Wi |x ∈ [1, h], y ∈ [1, w]}. Since the anomalous features in two networks are inclined to be unaligned,
1 − Wi represents the coarse localization of the anomalous
regions and servers as an abnormal coarse localization mask.
Finally, utilizing explicit weighting, WMB transfers the coarse
localization information related to anomalies obtained from
distilled knowledge to Ti , with this process being expressed
as
Ci = (1 − Wi ) · Ti

(2)

where Ci denotes the outputs generated by WMB. The
weighted approach is more suitable for the ADPS than the feature fusion approach, as described in the ablation experiment
(Ref. Section IV-D). Therefore, Ci contains rich knowledge
obtained through the pretrained model’s prior knowledge while
simultaneously providing the ability to roughly discriminate
between abnormal and normal regions based on distilled
knowledge.
C. Postsegmentation Module
Traditional KDAD methods often infer the difference
obtained from the distillation model as the result of anomaly
segmentation. This results in two drawbacks: one is that
the features extracted from the pretrained network are only
used as a “reference standard” and not explored further for
their potential, and another is that the segmentation results
obtained yield low resolution with low accuracy. To solve these
drawbacks simply and effectively, we leverage the advantages
of Ci , which retains both prior and distilled knowledge, and

7055

Algorithm 1 Framework of the Proposed ADPS
Input: Pretrained Teacher model T , student model S, test
image set U , Postsegmentation model PS.
Output: Each image’s anomaly map M and its anomaly score
Sc.
1: for I ∈ U do
2:
I S ← Split (I ) ▷ Split into nonoverlapping patches
3:
Ti ← T . f or war d(I )
4:
Si ← S. f or war d(I S )
5:
for i ∈ [1, n] do ▷ n represents the number of layers
6:
Wi ← Ti , Si are calculated according to (1)
7:
Ci ← Ti , Wi are calculated according to (2)
8:
end for
9:
M ← PS. f or war d([C1 , . . . , Cn ])
10:
Sc ← max(G(M))
▷ G(·) is Gaussian function.
11: end for

develop the PSM to identify the normal and abnormal distribution from Ci . PSM seeks to segment the abnormal regions
with high accuracy and clear boundaries. Specifically, PSM
employs the multiple UpBlock layers of UNet [57] as the
backbone. To fully exploit the features extracted from each
layer of the pretrained teacher model, we use the weighted
multiscale feature map C = {C1 , C2 , . . . , Cn } as the input.
Here, n represents the number of multiscale layers. We present
UpBlock i as an example to illustrate the upsampling process.
In UpBlock layer i of PSM, the output Pi−1 of UpBlock
i − 1 is fed as the input
Pim = TrConvi (Pi−1 )

(3)

where TrConvi (·) denotes the 2× transposed convolution, and
Pim is the output of the transposed convolution. Subsequently,
Pim and Ci are concatenated together along the channel dimension
Pic = cat(Pim , Ci )

(4)

where cat(·) denotes the concatenation of two feature maps
along the channel dimension. Finally, we obtain the output Pi
of UpBlock i via the convolution layer

Pi+1 = σ (BNi1 (Convi1 σ BNi2 Convi2 Pic
(5)
where Convi1 (·) and Convi2 (·) indicates two 3 × 3 convolution
layers with stride 1 in UpBlock i layer, BNi1 (·) and BNi2 (·)
denotes two batch normalization layers, σ (·) denotes the ReLU
activation function. Finally, the output Pn is convolved by
3 × 3 convolution layer to obtain the segmentation mask M
with the size of H × W
M = Softmax(Conv f (Pn ))

(6)

where Softmax(·) denotes the Softmax function and Conv f (·)
represents 3 × 3 convolution layer.
In Algorithm 1, we show each step of the ADPS framework.
With ADPS, we can infer the anomaly score and anomaly
segmentation map of the image to be tested.

7056

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 4, APRIL 2025

D. Loss Function
To train ADPS, this work follows the DRAEM [58] to
generate simulated anomaly samples. Additionally, distillation
loss and focal loss [59] are introduced as part of the loss
function. The distillation loss, defined as follows, is used in
the model training
Ld =

n
X


(1 − Y ) · 1 −

i=1

Ti · Si
∥Ti ∥ × ∥Si ∥


+Y ·

Ti · Si
∥Ti ∥ × ∥Si ∥
(7)

where Y denotes the ground-truth (GT) label of training
samples such that Y = {yu,v ∈ {0, 1}|u ∈ [1, h], v ∈ [1, w]}.
Indeed, L D essentially expects the teacher–student model to
output features close to each other when fed normal samples
and away from each other when fed forged anomaly samples.
Furthermore, the proposed approach utilizes the focal loss Ls
[59] defined as follows:
(
−(1 − pi, j )τ log( pi, j ), yi, j = 1
Ls =
(8)
− pi,τ j log(1 − pi, j ),
yi, j = 0
where pi, j denotes the probability of the abnormality in the
coordinate (i, j) of M. To incorporate the distillation loss Ld
and segmentation loss Ls in the training process of ADPS, the
overall loss L is defines as follows:
L = Ld + λLs

(9)

where λ is set to control the importance of the two losses.
IV. E XPERIMENTS
A. Experimental Settings
1) Datasets: To demonstrate the effectiveness of our proposed ADPS, we conducted experiments on three datasets:
MVTec AD [4], KolektorSDD [64], and KolektorSDD2 [30].
1) The MVTec AD [4] dataset consists of 15 classes of
high-resolution images derived from actual industrial
scenarios, subdivided into five categories of texture
images (referred to as “Texture”) and ten categories of
object images (referred to as “Object”). The training
dataset contains only normal images, while the testing
dataset includes a variety of anomaly patterns, such as
scratches, defects, and so on. This dataset presents a
considerable challenge due to the subtle anomalies and
high-resolution nature.
2) The KolektorSDD [64] dataset consists of 399 images,
each with dimensions of 500 × 1250. These images
were acquired under controlled conditions in a
real-world industrial setting.
3) The KolektorSDD2 [30] is a comprehensive surface
defect detection dataset containing over 3000 images,
with each having a size of approximately 230 × 630.
This dataset exposes a range of defect types commonly
found in the industry, including scratches, dots, and
surface defects.

2) Implementation Details: The input image resolution is
fixed at 256 × 256, while k is set to 8. In the training phase,
the learning rate is set to 0.0001 and the batch size is set
to 32. The network is trained for 300 epochs by the Adam
optimizer [65], with a learning rate decay at epochs 240 and
270 with a decay rate of 0.2. We set the value of λ to 1.
3) Baseline Approaches: We compare our ADPS against
several baselines, including: U-Std [26], MKDAD [12],
MF [61], RD [13], DAAD+ [32], RIAD [34], Cutpaste [62],
DRAEM [58], DRAEM + SSPCAB [66], AnoSeg [63],
SGSF [67], SPADE [48], Patchcore [54], PaDim [9],
MAD [60], and Semi-orthogonal [68]. Among these, SPADE,
PaDim, Semi-orthogonal, Patchcore, and RD utilize WideResNet50 [49] as the backbone, while MF introduces a
Transformer-based structure. DRAEM, DRAEM + SSPCAB,
Cutpaste, and our ADPS introduce simulated anomalous samples.
4) Evaluation Metrics: As per previous studies [9], [13],
[69], commonly used evaluation metrics for anomaly classification tasks is the area under the receiver-operating
characteristic (AUROC), and for anomaly segmentation tasks
are per-region-overlap (PRO) and AUROC. However, these
metrics inadequately reflect the actual segmentation performance when dealing with small anomalous regions due to
the overwhelming number of normal pixels. Toward this
end, Tao et al. [69] introduce a more convincing metric,
average precision (AP), to reflect the performance of the
proposed method for pixel-level segmentation. In this work,
the performance of anomaly classification is evaluated using
AUROC cla , while anomaly segmentation performance is measured using AUROC seg , PROseg , and AP seg collectively.
Notable, on account of the significantly lower number of
abnormal pixels than normal ones, AP seg better indicates the
segmentation accuracy.
B. Comparison With State-of-the-Art Methods
1) MVTec AD: Table I illustrates the anomaly classification
results obtained on the MVTec AD dataset. ADPS achieves
very competitive anomaly classification results, with 100%
classification accuracy achieved across four categories. Significantly, ADPS shows notable performance improvement
in several categories, outperforming the methods employing
WideResNet-50 with improved accuracy by approximately
3%–10%. These results demonstrate that ADPS makes full
use of the pretrained model’s knowledge to achieve efficient anomaly classification. In comparison to Cutpaste [62],
which further introduces simulated anomalous samples, ADPS
obtains a superior performance gain of 2.7%. Thus, the strategy of leveraging asymmetric distillation to achieve coarse
localization and fine segmentation of anomalies proves more
effective than training the classifier directly. Overall, the
experimental results highlight that ADPS, integrating distilled
and prior knowledge, provides a more accurate normal image
distribution and delivers powerful anomaly classification capability.
In addition to anomaly classification, we demonstrate the
anomaly segmentation performance of ADPS and compare it

XING et al.: ADPS: ASYMMETRIC DISTILLATION POSTSEGMENTATION FOR IMAGE ANOMALY DETECTION

7057

TABLE I
A NOMALY C LASSIFICATION R ESULTS IN T ERMS OF AUROC CLA (%) ON THE MVT EC AD DATASET. T HE B EST R ESULTS A RE M ARKED IN B OLD

TABLE II
A NOMALY S EGMENTATION R ESULTS IN T ERMS OF AUROC SEG , PRO SEG , AND AP SEG (%) ON THE MVT EC AD DATASET. T HE P ROPOSED ADPS
O UTPERFORMS R ECENT M ETHODS BY N EARLY 10% IN T ERMS OF AP SEG . T HE B EST R ESULTS A RE M ARKED IN B OLD .
PA D IM∗ D ENOTES A NOTHER R ESULT F ROM [9] W ITH R ES N ET-18 AS THE BACKBONE

to current state-of-the-art methods. The evaluation is based
on three key metrics on the MVTec AD dataset, with
the results presented in Table II. Our approach, ADPS,
outperforms knowledge distillation-based methods such as
U-Std and MKDAD by 5%–10% on AUROC seg and 3%
on PROseg . It also exceeds U-Std by 32% on AP seg ,
demonstrating its excellent anomaly segmentation capability.

Compared to recent distillation methods, the superior performance of ADPS is attributed to its asymmetric distillation
paradigm, which shows effectiveness in handling anomalous images. The representations extracted from the student
network of input local images are harder to match with
those of the teacher network of input global images. This
leads to better detection of intricate anomalous regions,

7058

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 4, APRIL 2025

Fig. 4. Anomaly segmentation results on the MVTec AD dataset. Compared with RD [13], ADPS achieves high-confidence segmentation results in both
anomalous and normal regions with different categories. (a)–(d) represent the horizontal coordinates and (1)–(3) represent the vertical coordinates in Fig. 4.
In total, 12 examples are listed to compare the proposed ADPS with RD.

TABLE III
P ERFORMANCE C OMPARISON W ITH THE L ATEST U NSUPERVISED
A NOMALY D ETECTION M ETHODS AND S UPERVISED A NOMALY
D ETECTION M ETHODS ON THE MVT EC AD DATASET

resulting in a significant improvement in segmentation
precision.
Meanwhile, ADPS significantly outperforms Patchcore [54]
in its ability to localize anomalies at the pixel level, for
example, the APseg metric outperforms it by 16%. This is
due to the powerful anomaly segmentation capability of the
ADPS PSB after obtaining distillation knowledge. Second,
Patchcore takes more time in inference because it computes
anomaly scores based on the similarity measure between an
image’s patch features and each stored memory bank item.
ADPS also surpasses DRAEM, DRAEM + SSPCAB, and
Cutpaste methods that rely on forged anomalous samples, even
though DRAEM (including combined SSPCAB) have larger
parameters of networks, achieving an impressive AP seg of
77.4%. In particular, DRAEM similarly uses a segmentation
module, while ADPS significantly outperforms its anomaly
segmentation capability. The competitive results of ADPS are
attributed to its integration of two fundamental components:
harnessing the feature representation capabilities inherent in
the teacher network and using distilled knowledge to obtain a
coarse localization of anomalous regions followed by precise
anomaly segmentation.
Fig. 4 shows the visualization image of anomaly segmentation on the MVTec AD dataset. a1–a3 demonstrate
the anomalous region segmentation capability of RD and

TABLE IV
A NOMALY D ETECTION R ESULTS FOR THE KOLEKTOR SDD
AND KOLEKTOR SDD2 DATASETS

ADPS. ADPS utilizes the segmentation module to improve
its segmentation accuracy by exploiting coarse localization
features from the distilled knowledge. Conversely, RD approximates the location of anomalous regions but is accompanied
by significant noise. c1, d2, and d3 demonstrate the high
resemblance between anomalous and normal regions, which
poses challenges to the efficient segmentation of current
AD methods. However, the exceptional ability of ADPS in
anomaly segmentation stands out.
In addition, we compare the proposed ADPS with recent
state-of-the-art unsupervised and fully supervised AD methods. The comparison results are demonstrated in Table III.
Compared with the state-of-the-art unsupervised methods,
the proposed ADPS is more challenging to localize the
anomalies, especially in the metric AP seg , which reaches
the highest 77.4%. Compared to the AD method RN [7]
based on the knowledge distillation method, ADPS exceeds
17% on the AP seg metric. Compared to the fully supervised
method DRA [72], the proposed ADPS leads in all aspects.
Undeniably, ADPS still has room for improvement for the
state-of-the-art fully supervised method PRN [73]. However,
the anomaly segmentation aspect also achieves a performance
that wants to be close. The above experimental results demonstrate the advancement of ADPS.

XING et al.: ADPS: ASYMMETRIC DISTILLATION POSTSEGMENTATION FOR IMAGE ANOMALY DETECTION

Fig. 5.

7059

Anomaly segmentation results on the KolektorSDD2 dataset.
Fig. 7.
Visualization images using symmetric distillation (k = 1) and
asymmetric distillation methods (k = 8).

C. Effectiveness of Asymmetric Distillation Paradigm

Fig. 6. Performance of asymmetric distillation paradigm (k = 2, 4, 8, 16)
and symmetric distillation paradigm (k = 1).

2) KolektorSDD&KolektorSDD2: To further demonstrate
the effectiveness of ADPS, we conduct anomaly classification
and anomaly segmentation experiments on two additional
benchmark datasets (i.e., KolektorSDD and KolektorSDD2).
The results, presented in Table IV, show that ADPS achieves
state-of-the-art performance on both datasets. Notably, for the
KolektorSDD2 dataset, ADPS achieves an AP seg of 72.5%,
which is a substantial improvement of 20% and 21% over
the performance of DRAEM and SGSF, respectively. It is
worth mentioning that both DRAEM and SGSF employ forged
anomaly samples and segmentation frameworks. This significant performance advantage can be attributed to the thorough
exploration of the potential of pretrained models by ADPS for
AD tasks. To achieve accurate anomaly segmentation, distilled
knowledge, and prior knowledge are utilized to generate
coarse localization information, which is further utilized by
the segmentation module. The results of anomaly segmentation
are shown in Fig. 5. Exemplary segmentation of anomaly
contours and normal regions, along with high-confidence
segmentation results, is achieved by ADPS, outperforming
RD in this regard. Furthermore, by uniformly calibrating the
segmentation threshold at 0.5 across all categories, ADPS
obtains precise anomaly segmentation maps.

1) Asymmetric Inputs: We first conduct experiments on
the MVTec AD dataset to validate the influence of various
inputs on the asymmetric distillation paradigm. When k = 1,
ADPS adopts the symmetric distillation paradigm. In the cases
where k belongs to {2, 4, 8, 16}, ADPS utilizes the asymmetric
distillation paradigm by dividing the input into k × k patches
at the input layer, respectively. The experimental results are
illustrated in Fig. 6. The supremacy of the asymmetric distillation paradigm is visibly established, particularly in terms of
AP seg . Moreover, the optimal performance is achieved when
k = 4 or 8. The division into patches facilitates the focused
attention of the student network on specific regions, enabling
ADPS to recognize anomalous pixels that closely resemble
normal ones. However, excessive division (when k = 16) can
cause a loss of crucial original structural information leading
to a decrease in performance. We visualize the anomaly
segmentation results for the symmetric distillation paradigm
and the asymmetric distillation paradigm shown in Fig. 7.
It is observed that the student network with an asymmetric
input can better capture the anomalous features of tiny regions
with detailed boundaries. In scenarios like the ‘Grid’ category,
the sequential learning of local images allows the student
network to concentrate more intensely on local details, thereby
facilitating a more accurate localization map for “foreign
objects.”
2) Asymmetric Layers: In addition to introducing the asymmetric inputs, ADPS introduces the asymmetric distillation
paradigm at various feature levels in different stages. Taking
WideResNet-50 as the backbone of the teacher network as
an example, we introduce the asymmetric distillation strategy
in Stage 1 and Stage 2, building upon the asymmetric input
layer. The AD results are shown in Table V. The introduction of asymmetric distillation at the shallow layer (stage 1)
improves the AD performance for texture images, although its
effect on the “Object” type is not substantial. However, the
performance drops significantly upon further adoption at the
deep layers (stage 2). This may occur due to the low resolution
of segmented features in the deeper layers, which disrupts

7060

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 4, APRIL 2025

TABLE V
R ESULTS OF I NTRODUCING A SYMMETRIC K NOWLEDGE PARADIGM FOR D IFFERENT S TAGES W ITH k = 4. “S TAGE i ” I NDICATES T HAT AT S TAGE i

the original nearest-neighbor relationships within the image.
Consequently, the destruction of structural information impairs
the effectiveness of distillation in providing coarse localization
information, thereby influencing the detection capability of
ADPS.
D. Effect of Weight Mask Block on ADPS
We investigate three ways for combining distilled knowledge and pretrained knowledge to obtain Ci , as illustrated in
Fig. 8.
1) Method (1): This method involves utilizing the differences in features between the teacher network and the
student network as Ci , which is then directly input into
PSM.
2) Method (2): The features extracted from the student
network and the teacher network are combined directly,
where a 3 × 3 convolution is employed to achieve
dimensional reduction and fusion for obtaining Ci .
3) WMB: The distilled knowledge Wi is leveraged in
WMB to re-weight the original pretrained representations, resulting in Ci .
The experimental results corresponding to the three ways are
shown in Table VI. Comparing Method (1) and Method (2)
reveals that the AD capability of Method (1) significantly
surpasses that of Method (2). This observation demonstrates
that explicitly incorporating coarse localization information
outperforms direct feature fusion. Accordingly, we designed
a more effective weighted method called WMB. WMB integrates not only the coarse localization information Wi , but
also the multiscale contextual information extracted from
the pretrained teacher network Ti . WMB exhibits superior
performance compared to Method (1), establishing it as the
suitable module within the ADPS framework. Despite the
simplicity of this weighted approach, it provides a solution
for fusing distilled knowledge and pretrained prior knowledge
for high-performance AD. Its advantage lies in ingeniously
integrating distilled knowledge and pretrained knowledge,
thereby enabling PSM to derive fused features optimized for
AD.
In addition, we investigated the effect of different distillation
losses on ADPS performance in WMB. We compare the cosine
similarity (Cosine) loss with the mean squared error (MSE)
loss. In Table VII, we show four setups, where the column
‘Wi ’ contains the two ways to compute Wi . The experimental
results are shown in Table VII. When using both MSE and
Cosine similarity losses, the AD performance is reduced.
Employing the Cosine loss yields better AD and anomaly

Fig. 8. Illustration of the different ways to transfer distilled knowledge to Ti .

segmentation performance than MSE loss. Interestingly, for
“textured” images, using MSE loss proves to be more effective.
In this article, ADPS uses the experimental setup of the second
row, that is, it uses the cosine similarity loss and computes Wi
by cosine similarity.
E. Ablation Study on the Framework of ADPS
To investigate each component of the proposed ADPS
framework, we compare ADPS with its variants on the
MVTec-AD dataset.
1) W/O. PW: The proposed ADPS without PSM and WMB.
2) W/O. T: The proposed ADPS without the teacher network, that is, direct training the student model and PSM.
3) W/O. S: The proposed ADPS removes the student network and directly uses a pretrained teacher network.
In this setting, only the parameters of the PSB can be
learned.
We show the variant models and their results in Table VIII.
Based on the experimental results, the following conclusions
can be made.
1) Pretrained Knowledge is Essential for the Teacher Network: The comparison results from W/O. T and W/O. S show a
significant drop in AD and anomaly segmentation performance
for multiple categories. Especially, the anomaly segmentation
performance decreases by 10% for AP seg . The experimental
results confirm the effectiveness of prior knowledge from the
pretrained model for AD and emphasize the need for further
exploration. Using only the teacher network is intuitively more
effective than using only the student network, as the pretrained
model provides a powerful feature representation for the PSB.
Another possible explanation is that after fixing the image
encoder (teacher model), the PSM module is more capable
of being trained more efficiently [74], yielding more accurate
segmentation results.

XING et al.: ADPS: ASYMMETRIC DISTILLATION POSTSEGMENTATION FOR IMAGE ANOMALY DETECTION

7061

TABLE VI
A NOMALY D ETECTION R ESULTS OF D IFFERENT T-S F EATURE F USION M ETHODS ON THE MVT EC AD DATASET.
WMB ACHIEVES THE B EST P ERFORMANCE . “ ” I NDICATES S UBOPTIMAL R ESULTS

TABLE VII
A BLATION S TUDY ON THE S ELECTION OF D IFFERENT K NOWLEDGE D ISTILLATION L OSS F UNCTIONS AND D IFFERENT G ENERATION M ETHODS OF Wi

TABLE VIII
P ERFORMANCE OF F OUR S TRUCTURES ON THE MVT EC AD DATASET. ADPS I S THE B EST IN T ERMS OF
A NOMALY C LASSIFICATION AND A NOMALY S EGMENTATION P ERFORMANCE

2) Exploitation Potential of the Teacher Network Is Significant: Comparing with ADPS, W/O. PW shows a decrease
of 7% in AUROC cla and 20% in AP seg , highlighting the
effectiveness and potential of the PSM and WMB modules
in utilizing the features extracted by the teacher network.
While the teacher network only serves as an extractor of
reference features without leveraging its powerful feature
representation capability, introducing WMB to utilize distilled
knowledge and PSM to fully exploit the features extracted
by the teacher model enhances the AD capability. Table VI
also demonstrates the significant impact of different methods
that employ pretrained knowledge and distilled knowledge on
AD. The proposed WMB may not be the optimal scheme, and
future research could explore methods that combine teacher
networks and distillation strategies to further enhance AD
ability.

Fig. 9. Anomaly heatmaps for four structures. ADPS captures more tiny
anomaly regions with clearer and more detailed decision boundaries. (a) and
(b) represent two cases of ablation studies in ADPS.

3) Asymmetric Distillation and WMB Contribute to the
Performance of ADPS: Comparing W/O. S with ADPS,
it can be observed that distilled knowledge obtained through

7062

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 4, APRIL 2025

asymmetric distillation significantly improves the performance
of ADPS. However, without the WMB, the distilled knowledge
cannot be effectively transferred to the teacher network. The
corresponding results demonstrate that fully integrating pretrained prior knowledge and distilled knowledge is effective in
improving the performance of AD. The insight behind this is
that prior knowledge provides powerful feature representation,
while distilled knowledge enhances the discrimination between
anomalies and normal instances.
a) Feature visualization: We present visualizations in
Fig. 9, which includes two examples that compare anomaly
segmentation results. Fig. 9(a) and (b) illustrates the boundary
between normal and abnormal features learned by W/O. S is
not accurate. Additionally, W/O. PW shows the inability to
derive the decision boundary between abnormal and normal
from low-resolution feature maps, which leads to inefficient
detection results. The limitations of W/O. S in capturing
differences in small anomalous regions are attributed to the
lack of an asymmetrical distillation model that focuses on local
regions. On the other hand, Fig. 9 demonstrates that AP seg is
more indicative of the performance of anomalous segmentation
(e.g., although the segmentation results of W/O. PS have many
errors, AUROC seg still maintains a high performance).
b) Discussion: Undoubtedly, the PSM plays a vital role,
particularly in the anomaly segmentation capability of ADPS.
It further confirms our hypothesis that solely relying on acquiring high-precision segmentation maps from low-resolution
feature map differences is extremely challenging. Consequently, solving the anomaly segmentation challenge may have
to rely on high-resolution images. Additionally, the approach
employed by ADPS to exploit the features extracted by the
pretrained model is straightforward. We believe that more
effective distilled knowledge can be obtained by leveraging
the discrepancy between the learning capabilities of the teacher
network and the student network.
V. C ONCLUSION
In this article, we presented a novel knowledge distillationbased framework, ADPS, to alleviate the main problems of
existing KDAD methods for image AD. Our proposed ADPS
framework establishes an asymmetric distillation paradigm
with asymmetric data streams to mitigate the problem of
the student network over-approximating the feature output of
the teacher network when anomalous images are input. The
asymmetric distillation paradigm further utilizes local patches
as inputs to facilitate the student model’s ability to capture
local details. Additionally, customized WMB and PSM were
developed to fully incorporate the distilled posterior knowledge and pretrained prior knowledge to produce high-quality
segmentation maps with fine structures and clear boundaries.
Extensive experiments on three benchmarks demonstrate that
our ADPS framework performs favorably against state-of-theart methods. Importantly, our simple framework is modular,
promising to serve as a strong baseline for future efficient
KDAD research.
Despite these advancements, ADPS’s reliance on simulated
anomalous samples remains a limitation. Moving forward, our
research will focus on reducing this dependency and exploring

the application of ADPS in additional industrial contexts,
potentially broadening its scope and impact.
R EFERENCES
[1] M. Salehi, H. Mirzaei, D. Hendrycks, Y. Li, M. H. Rohban, and
M. Sabokrou, “A unified survey on anomaly, novelty, open-set, and
out-of-distribution detection: Solutions and future challenges,” 2021,
arXiv:2110.14051.
[2] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for
anomaly detection: A review,” ACM Comput. Surv., vol. 54, no. 2,
pp. 1–38, 2021.
[3] J. Liu, Z. Hou, W. Li, R. Tao, D. Orlando, and H. Li, “Multipixel
anomaly detection with unknown patterns for hyperspectral imagery,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 10, pp. 5557–5567,
Oct. 2022.
[4] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec
AD—A comprehensive real-world dataset for unsupervised anomaly
detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2019, pp. 9584–9592.
[5] T. Xiang et al., “SQUID: Deep feature in-painting for unsupervised
anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2023, pp. 23890–23901.
[6] Z. Liu, Y. Zhou, Y. Xu, and Z. Wang, “SimpleNet: A simple network
for image anomaly detection and localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., Jun. 2023, pp. 20402–20411.
[7] Z. Gu et al., “Remembering normality: Memory-guided knowledge
distillation for unsupervised anomaly detection,” in Proc. IEEE/CVF
Int. Conf. Comput. Vis. (ICCV), Oct. 2023, pp. 16401–16409.
[8] D. Carrera, F. Manganini, G. Boracchi, and E. Lanzarone, “Defect
detection in SEM images of nanofibrous materials,” IEEE Trans. Ind.
Informat., vol. 13, no. 2, pp. 551–561, Apr. 2017.
[9] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “PaDiM: A patch distribution modeling framework for anomaly detection and localization,”
in Proc. Int. Conf. Pattern Recognit., Jan. 2021, pp. 475–489.
[10] F. Ye, C. Huang, J. Cao, M. Li, Y. Zhang, and C. Lu, “Attribute
restoration framework for anomaly detection,” IEEE Trans. Multimedia,
vol. 24, pp. 116–127, 2022.
[11] M. Rudolph, B. Wandt, and B. Rosenhahn, “Same same but DifferNet:
Semi-supervised defect detection with normalizing flows,” in Proc. IEEE
Winter Conf. Appl. Comput. Vis. (WACV), Jan. 2021, pp. 1907–1916.
[12] M. Salehi, N. Sadjadi, S. Baselizadeh, M. H. Rohban, and H. R. Rabiee,
“Multiresolution knowledge distillation for anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 14902–14912.
[13] H. Deng and X. Li, “Anomaly detection via reverse distillation from
one-class embedding,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2022, pp. 9737–9746.
[14] T. Schlegl, P. Seeböck, S. M. Waldstein, G. Langs, and
U. Schmidt-Erfurth, “F-AnoGAN: Fast unsupervised anomaly detection
with generative adversarial networks,” Med. Image Anal., vol. 54,
pp. 30–44, May 2019.
[15] C. Baur, B. Wiestler, S. Albarqouni, and N. Navab, “Deep autoencoding models for unsupervised anomaly segmentation in brain
MR images,” in Proc. Int. MICCAI Brainlesion Workshop, 2018,
pp. 161–169.
[16] F. E. Fernandes and G. G. Yen, “Automatic searching and pruning of
deep neural networks for medical imaging diagnostic,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 32, no. 12, pp. 5664–5674, Dec. 2021.
[17] A. F. Mejia, M. B. Nebel, A. Eloyan, B. Caffo, and M. A. Lindquist,
“PCA leverage: Outlier detection for high-dimensional functional magnetic resonance imaging data,” Biostatistics, vol. 18, no. 3, pp. 521–536,
Jul. 2017.
[18] S. Venkataramanan, K.-C. Peng, R. V. Singh, and A. Mahalanobis,
“Attention guided anomaly localization in images,” in Proc. Eur. Conf.
Comput. Vis., Nov. 2020, pp. 485–503.
[19] T. Vojir, T. Šipka, R. Aljundi, N. Chumerin, D. O. Reino, and J. Matas,
“Road anomaly detection by partial image reconstruction with segmentation coupling,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2021, pp. 15651–15660.
[20] D. Bogdoll, M. Nitsche, and J. M. Zollner, “Anomaly detection in
autonomous driving: A survey,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. Workshops (CVPRW), Jun. 2022, pp. 4488–4499.

XING et al.: ADPS: ASYMMETRIC DISTILLATION POSTSEGMENTATION FOR IMAGE ANOMALY DETECTION

[21] D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1705–1714.
[22] H. Park, J. Noh, and B. Ham, “Learning memory-guided normality
for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2020, pp. 14372–14381.
[23] M. Salehi, A. Eftekhar, N. Sadjadi, M. H. Rohban, and H. R. Rabiee,
“Puzzle-AE: Novelty detection in images through solving puzzles,”
2020, arXiv:2008.12959.
[24] D. Li, Q. Tao, J. Liu, and H. Wang, “Center-aware adversarial autoencoder for anomaly detection,” IEEE Trans. Neural Netw. Learn. Syst.,
vol. 33, no. 6, pp. 2480–2493, Jun. 2022.
[25] Y. Zhou, X. Song, Y. Zhang, F. Liu, C. Zhu, and L. Liu, “Feature
encoding with autoencoders for weakly supervised anomaly detection,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2454–2465,
Jun. 2022.
[26] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Uninformed
students: Student–teacher anomaly detection with discriminative latent
embeddings,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2020, pp. 4183–4192.
[27] B. Qian, Y. Wang, H. Yin, R. Hong, and M. Wang, “Switchable
online knowledge distillation,” in Proc. ECCV, vol. 13671, Oct. 2022,
pp. 449–466.
[28] Z. Li, H. Tang, Z. Peng, G.-J. Qi, and J. Tang, “Knowledge-guided
semantic transfer network for few-shot image recognition,” IEEE Trans.
Neural Netw. Learn. Syst., pp. 1–15, Feb. 2023.
[29] G. Wang, S. Han, E. Ding, and D. Huang, “Student–teacher feature
pyramid matching for anomaly detection,” 2021, arXiv:2103.04257.
[30] J. Božič, D. Tabernik, and D. Skočaj, “Mixed supervision for surfacedefect detection: From weakly to fully supervised learning,” Comput.
Ind., vol. 129, Aug. 2021, Art. no. 103459.
[31] P. Bergmann, S. Löwe, M. Fauser, D. Sattlegger, and C. Steger, “Improving unsupervised defect segmentation by applying structural similarity
to autoencoders,” 2018, arXiv:1807.02011.
[32] J. Hou, Y. Zhang, Q. Zhong, D. Xie, S. Pu, and H. Zhou, “Divideand-assemble: Learning block-wise memory for unsupervised anomaly
detection,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2021, pp. 8791–8800.
[33] Z. Li et al., “Superpixel masking and inpainting for self-supervised
anomaly detection,” in Proc. BMVC, 2020, pp. 1–12.
[34] V. Zavrtanik, M. Kristan, and D. Skočaj, “Reconstruction by inpainting
for visual anomaly detection,” Pattern Recognit., vol. 112, Apr. 2021,
Art. no. 107706.
[35] Z. You et al., “A unified model for multi-class anomaly detection,” in
Proc. Adv. Neural Inf. Process. Syst., 2022, pp. 4571–4584.
[36] T. Wang, X. Xu, F. Shen, and Y. Yang, “A cognitive memory-augmented
network for visual anomaly detection,” IEEE/CAA J. Autom. Sinica,
vol. 8, no. 7, pp. 1296–1307, Jul. 2021.
[37] H. Tang, C. Yuan, Z. Li, and J. Tang, “Learning attention-guided pyramidal features for few-shot fine-grained recognition,” Pattern Recognit.,
vol. 130, Oct. 2022, Art. no. 108792.
[38] P. Xing and Z. Li, “Visual anomaly detection via partition memory bank
module and error estimation,” IEEE Trans. Circuits Syst. Video Technol.,
vol. 33, no. 8, pp. 3596–3607, Jan. 2023.
[39] I. J. Goodfellow et al., “Generative adversarial nets,” in Proc. 27th Int.
Conf. Neural Inf. Process. Syst. (NIPS), 2014, pp. 2672–2680.
[40] T. Schlegl, P. Seebóck, S. M. Waldstein, U. Schmidt-Erfurth, and
G. Langs, “Unsupervised anomaly detection with generative adversarial
networks to guide marker discovery,” in Proc. Int. Conf. Inf. Process.
Med. Imag., May 2017, pp. 146–157.
[41] S. Akcay, A. Atapour-Abarghouei, and T. P. Breckon, “GANomaly:
Semi-supervised anomaly detection via adversarial training,” in Proc.
Asian Conf. Comput. Vis., Dec. 2018, pp. 622–637.
[42] H. Zenati, C. S. Foo, B. Lecouat, G. Manek, and V. R. Chandrasekhar,
“Efficient GAN-based anomaly detection,” 2018, arXiv:1802.06222.
[43] D. Zhang, S. Gao, L. Yu, G. Kang, X. Wei, and D. Zhan, “DefGAN:
Defect detection GANs with latent space pitting for high-speed railway
insulator,” IEEE Trans. Instrum. Meas., vol. 70, pp. 1–10, 2021.
[44] Y. Chen, X. S. Zhou, and T. S. Huang, “One-class SVM for learning in
image retrieval,” in Proc. Int. Conf. Image Process., vol. 1, Oct. 2001,
pp. 34–37.
[45] L. Ruff et al., “Deep one-class classification,” in Proc. Int. Conf.
Mach. Learn., 2018, pp. 4393–4402.

7063

[46] R. Chalapathy, A. K. Menon, and S. Chawla, “Anomaly detection using
one-class neural networks,” 2018, arXiv:1802.06360.
[47] J. Yi and S. Yoon, “Patch SVDD: Patch-level SVDD for anomaly
detection and segmentation,” in Proc. ACCV, Jun. 2020, pp. 375–390.
[48] N. Cohen and Y. Hoshen, “Sub-image anomaly detection with deep
pyramid correspondences,” 2020, arXiv:2005.02357.
[49] S. Zagoruyko and N. Komodakis, “Wide residual networks,” in Proc.
Brit. Mach. Vis. Conf., 2016, pp. 87.1–87.12. [Online]. Available:
https://bmva-archive.org.uk/bmvc/2016/papers/paper087/index.html
[50] C. B. Do, “The multivariate Gaussian distribution,” Sect. Notes, Lect.
Mach. Learn., vol. 229, pp. 1–10, Oct. 2008.
[51] G. G. Hazel, “Multivariate Gaussian MRF for multispectral scene
segmentation and anomaly detection,” IEEE Trans. Geosci. Remote
Sens., vol. 38, no. 3, pp. 1199–1211, May 2000.
[52] H. Liu, X. Xu, E. Li, S. Zhang, and X. Li, “Anomaly detection
with representative neighbors,” IEEE Trans. Neural Netw. Learn. Syst.,
vol. 34, no. 6, pp. 2831–2841, Jun. 2023.
[53] M. Rudolph, T. Wehrbein, B. Rosenhahn, and B. Wandt, “Fully
convolutional cross-scale-flows for image-based defect detection,” in
Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis. (WACV), Jan. 2022,
pp. 1829–1838.
[54] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler,
“Towards total recall in industrial anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022,
pp. 14298–14308.
[55] J. Yu et al., “FastFlow: Unsupervised anomaly detection and localization
via 2D normalizing flows,” 2021, arXiv:2111.07677.
[56] G. Xie, J. Wang, J. Liu, F. Zheng, and Y. Jin, “Pushing the limits
of fewshot anomaly detection in industry vision: Graphcore,” 2023,
arXiv:2301.12082.
[57] O. Ronneberger, P. Fischer, and T. Brox, “U-Net: Convolutional networks for biomedical image segmentation,” in Proc. 18th Int. Conf. Med.
Image Comput. Comput.-Assist. Intervent., 2015, pp. 234–241.
[58] V. Zavrtanik, M. Kristan, and D. Skocaj, “DRÆM—A discriminatively trained reconstruction embedding for surface anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021,
pp. 8330–8339.
[59] T.-Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, “Focal loss for
dense object detection,” in Proc. IEEE Int. Conf. Comput. Vis. (ICCV),
Oct. 2017, pp. 2980–2988.
[60] O. Rippel, P. Mertens, and D. Merhof, “Modeling the distribution of
normal data in pre-trained deep features for anomaly detection,” in Proc.
25th Int. Conf. Pattern Recognit. (ICPR), Jan. 2021, pp. 6726–6733.
[61] J.-C. Wu, D.-J. Chen, C.-S. Fuh, and T.-L. Liu, “Learning unsupervised
metaformer for anomaly detection,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. (CVPR), Oct. 2021, pp. 4369–4378.
[62] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Selfsupervised learning for anomaly detection and localization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 9664–9674.
[63] J. Song, K. Kong, Y.-I. Park, S.-G. Kim, and S.-J. Kang, “AnoSeg:
Anomaly segmentation network using self-supervised learning,” 2021,
arXiv:2110.03396.
[64] D. Tabernik, S. Šela, J. Skvarč, and D. Skočaj, “Segmentation-based
deep-learning approach for surface-defect detection,” J. Intell. Manuf.,
vol. 31, no. 3, pp. 759–776, Mar. 2020.
[65] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
in Proc. ICLR, Y. Bengio and Y. LeCun, Eds., 2015.
[66] N.-C. Ristea et al., “Self-supervised predictive convolutional attentive
block for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2022, pp. 13566–13576.
[67] P. Xing, Y. Sun, D. Zeng, and Z. Li, “Normal image guided segmentation
framework for unsupervised anomaly detection,” IEEE Trans. Circuits
Syst. Video Technol., pp. 1–14, Oct. 2023.
[68] J.-H. Kim, D.-H. Kim, S. Yi, and T. Lee, “Semi-orthogonal
embedding for efficient unsupervised anomaly segmentation,” 2021,
arXiv:2105.14737.
[69] X. Tao, X. Gong, X. Zhang, S. Yan, and C. Adak, “Deep learning for
unsupervised anomaly localization in industrial images: A survey,” IEEE
Trans. Instrum. Meas., vol. 71, pp. 1–21, 2022.
[70] X. Zhang, S. Li, X. Li, P. Huang, J. Shan, and T. Chen, “DeSTSeg:
Segmentation guided denoising student-teacher for anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2023, pp. 3914–3923.

7064

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 4, APRIL 2025

[71] X. Yao, R. Li, J. Zhang, J. Sun, and C. Zhang, “Explicit boundary guided
semi-push-pull contrastive learning for supervised anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2023, pp. 24490–24499.
[72] C. Ding, G. Pang, and C. Shen, “Catching both gray and black swans:
Open-set supervised anomaly detection,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 7388–7398.
[73] H. Zhang, Z. Wu, Z. Wang, Z. Chen, and Y.-G. Jiang, “Prototypical
residual networks for anomaly detection and localization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023,
pp. 16281–16291.
[74] M. Qu et al., “SiRi: A simple selective retraining mechanism for
transformer-based visual grounding,” in Proc. ECCV, in Lecture Notes
in Computer Science, vol. 13695, S. Avidan, G. J. Brostow, M. Cissé,
G. M. Farinella, and T. Hassner, Eds., 2022, pp. 546–562.

Jinhui Tang (Senior Member, IEEE) received the
B.E. and Ph.D. degrees from the University of
Science and Technology of China, Hefei, China, in
2003 and 2008, respectively.
He is currently a Professor with Nanjing University of Science and Technology, Nanjing, China.
He has authored or coauthored more than 200 articles in top-tier journals and conferences. His
research interests include multimedia analysis and
computer vision.
Dr. Tang was a recipient of the Best Paper Awards
from ACM MM 2007 and ACM MM Asia 2020, the Best Paper Runner-Up
in ACM MM 2015. He has served as an Associate Editor for IEEE T RANS ACTIONS ON N EURAL N ETWORKS AND L EARNING S YSTEMS (TNNLS),
IEEE T RANSACTIONS ON K NOWLEDGE AND DATA E NGINEERING (TKDE),
IEEE T RANSACTIONS ON M ULTIMEDIA (TMM), and IEEE T RANSACTIONS
ON C IRCUITS AND S YSTEMS FOR V IDEO T ECHNOLOGY (TCSVT). He is a
Fellow of IAPR.

Peng Xing is currently pursuing the Ph.D. degree
with the School of Computer Science and Engineering, Nanjing University of Science and Technology,
Nanjing, China.
His current research interests include anomaly
detection and unsupervised deep learning.

Hao Tang received the B.E. degree from Harbin
Engineering University, Harbin, China, in 2018.
He is currently pursuing the Ph.D. degree with the
School of Computer Science and Engineering, Nanjing University of Science and Technology, Nanjing,
China.
His current research interests include fine-grained
image analysis, data-efficient learning, and multimodal learning.

Zechao Li (Senior Member, IEEE) received the
B.E. degree from the University of Science and
Technology of China, Hefei, China, in 2008, and the
Ph.D. degree from the National Laboratory of Pattern Recognition, Institute of Automation, Chinese
Academy of Sciences, Beijing, China, in 2013.
He is currently a Professor with Nanjing University of Science and Technology, Nanjing, China.
His research interests include big media analysis,
computer vision, and so on.
Dr. Li was a recipient of the best paper award in
ACM Multimedia Asia 2020, and the best student paper award in ICIMCS
2018. He serves as an Associate Editor for IEEE T RANSACTIONS ON
N EURAL N ETWORKS AND L EARNING S YSTEMS (TNNLS).
PAPER_TEXT
