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
# [347] A Spatial Contexts-Informed Self-Supervised Learning Approach for Pavement Distress Segmentation
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
编号：347
题名：A Spatial Contexts-Informed Self-Supervised Learning Approach for Pavement Distress Segmentation
年份：2025
DOI：10.1109/tits.2025.3612736
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2025.3612736.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测
相关性：弱相关，分数 1
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\347.txt
- 原始字符数：59516
- 本次发送字符数：59516
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 12, DECEMBER 2025

23419

A Spatial Contexts-Informed Self-Supervised
Learning Approach for Pavement Distress
Segmentation
Ruiqi Ren , Peixin Shi , and Jinwoo Kim

Abstract—Detection and repair of pavement distress in time are
crucial to maximize functional performance and service life, while
minimizing maintenance costs on extensive roadway networks.
Manual distress detection is labor intensive and error prone.
While deep learning techniques offer unparalleled capabilities for
automated and accurate pixel-level pavement distress segmentation, their reliance on extensive manual annotations remains
a bottleneck. To address this challenge, we propose an openended self-supervised framework enabling flexible integration of
various pretext tasks for pavement distress segmentation without
manual annotations. We introduce a spatial contexts-informed
pretext task that automatically generates pseudo labels by leveraging the highly consistent semantic information inherent across
continuous pavement images within localized areas. A multiline parallel network architecture is then employed, where each
line extracts a distinct deep representation aligned with the
pseudo-label generation process. These representations are jointly
optimized through a shared weight update scheme augmented
by momentum encoders to capture long-range dependencies.
A vision transformer processes the input images during inference,
utilizing self-attention to highlight distressed regions based on
the learned representations for precise segmentation. Extensive
evaluations validate the performance of our framework, outperforming state-of-the-art self-supervised methods by 0.075 mIoU
on average, while remarkably surpassing weakly supervised techniques requiring manual image-level annotations. These results
are far more promising given that our self-supervised approach
avoids human labeling costs, striking a trade-off between model
effectiveness and annotation efficiency for large-scale deployments. It helps transportation agencies to realize timely, proactive
infrastructure maintenance through scalable, accurate distress
monitoring over extensive road networks.
Index Terms—Pavement distress segmentation, self-supervised
learning, spatial contexts, multi-line parallel networks.

I. I NTRODUCTION

D

ETECTION and repair of pavement distress in time
are crucial to maximize functional performance and
service life, while minimizing maintenance costs on extensive roadway networks. Manual visual distress inspection
Received 19 November 2024; revised 10 April 2025; accepted 28 August
2025. Date of publication 2 October 2025; date of current version 1 December
2025. This work was supported by the National Natural Science Foundation
of China under Grant 52278405. The Associate Editor for this article was
M. Guo. (Corresponding author: Peixin Shi.)
Ruiqi Ren and Peixin Shi are with the School of Rail Transportation, Soochow University, Suzhou 215000, China (e-mail: 20204046002@
stu.suda.edu.cn; pxshi@suda.edu.cn).
Jinwoo Kim is with the Department of Civil and Environmental Engineering, Hanyang University, Seoul 04763, South Korea (e-mail: jinwookim@
hanyang.ac.kr).
Digital Object Identifier 10.1109/TITS.2025.3612736

is labor-intensive, time-consuming, and error-prone. Digital
and automated distress detection technologies, such as computer vision, thermal imaging technology and laser scanning,
have become a promising solution [1], [2]. Among emerging
technologies, computer vision–based methods have attracted
significant attention in recent years [3], [4], as pavement distresses are typically expressed through visual cues that signal
early stages of road deterioration. Currently, vehicles mounted
with optical cameras are widely used in practice to regularly
inspect pavement, locate and evaluate the distresses through
computer vision technologies, and then provide information
to support maintenance decisions [5], [6].
Supervised deep learning have become the core engine
of computer vision-based pavement distress detection due to
their high accuracy and strong generalization performance
[7]. Although supervised learning shows considerable potential, its reliance on large volumes of training images and
labor-intensive annotations limits widespread use in pavement
distress detection [8], [9], [10]. This challenge is especially
pronounced in segmentation tasks, where pixel-level annotations are required [11], [12]. Potential solutions to mitigate this
challenge include data augmentation techniques [13] and transfer learning [14], [15]. While these approaches have demonstrated enhanced performance in pavement distress detection
and segmentation, they cannot entirely bypass the requirement
for manual annotations, given that each roadway has unique
surrounding environments. Therefore, exploring methods to
significantly lower or completely eliminate the requirement for
manual annotations has become a worthwhile endeavor [16].
Training deep learning models without access to ground
truth labels poses a fundamental challenge in defining effective learning objectives. Researchers have developed various
approaches to reduce manual annotation requirements to
varying degrees. Weakly supervised learning methods utilize
coarse-grained labels (such as image-level annotations) to
guide a learning process. They often learn a distribution of
normal data and identify anomalies as instances that exhibit
statistical deviations [17], [18], [19], [20], [21], [22]. These
methods significantly lower the annotation burden compared
to fully supervised approaches, but still require a substantial
amount of labeled data.
Self-supervised learning eliminates the need for explicit
annotations by leveraging data structure to generate pseudolabels through pretext tasks. For example, models learn feature
representations by reconstructing masked patches or aligning

1558-0016 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

23420

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 12, DECEMBER 2025

Fig. 1. Training schema of unsupervised siamese networks for pavement distress segmentation.

augmented views [23], [24], [25], [26]. However, these methods struggle to extract features of small pavement distress.
Masked patches may obscure critical details, while similar
pavement backgrounds make it difficult to optimize deep
representation learning based on similarity. Self-supervised
approaches also prioritize instance-level discrimination over
dense predictions, limiting their effectiveness for precise localization or segmentation. Designing more suitable pretext tasks
is essential for accurate pavement distress segmentation.
To achieve pixel-level pavement distress segmentation
without manual annotations, we propose a spatial contextsinformed self-supervised learning approach for pixel-level
pavement distress segmentation, as shown in Figure 1.
A spatial contexts-informed pretext task leverages consistent
semantic information across continuous pavement images to
automatically generate pseudo-labels. A multi-line parallel
network architecture is then trained on these pseudo-labeled
inputs, updating parameters through shared weights and
momentum encoders. Finally, pavement distress segmentation
is achieved by the self-attention mechanism of the vision
transformer (ViT).

II. R ELATED W ORK
This section reviews relevant literature in pavement distress segmentation, encompassing three primary learning
paradigms, supervised deep learning techniques that leverage
fully annotated datasets, weakly supervised learning methods
which exploit partial annotations to reduce manual labeling efforts, and self-supervised learning approaches that aim
to extract meaningful representations from unlabeled data
through carefully designed pretext tasks.

A. Supervised Deep Learning for Pavement Distress
Segmentation
The advent of convolutional neural networks, notably UNet [27] and fully convolutional networks (FCN) [28], has
significantly influenced pavement distress detection, primarily through supervised learning approaches. Crack is the
most commonly occurred and complex distress form, and
has received extensive attention in academia. For instance,
Zhang et al. enhance the U-Net by incorporating a generative
adversarial network. This modification forces the network
to segment images with fine crack details, thus improving
segmentation precision [13]. Wang et al. introduce a rectangular convolution pyramid and edge enhancement network
(RENet) for precise small crack segmentation [29]. Liu et al.
propose CrackFormer, featuring a pyramid-shaped transformer
structure and customized scaling attention for sharpened crack
detection [11]. To mitigate the limitation of training data
scarcity in supervised methods, Hou et al. achieve significant segmentation performance improvements by utilizing
Wasserstein generative adversarial network-gradient penalty
(WGAN-GP) for image enhancement before crack segmentation [30]. Zheng et al. manage to reduce the need for labeled
images through active learning [15]. Despite these significant contributions, the persistent need for extensive manual
annotation remains a major obstacle, impeding the widespread
adoption of computer vision technologies in pavement distress
detection.
B. Weakly Supervised Learning to Reduce Annotation
Dependency
Efforts to mitigate the reliance on extensive manual annotations have led to the development of weakly supervised

REN et al.: SPATIAL CONTEXTS-INFORMED SELF-SUPERVISED LEARNING APPROACH

learning approaches. These methods often leverage imagelevel annotations, assuming the majority of data represents
normal conditions. One approach trains encoder-decoder networks exclusively on normal instances, enabling accurate
reconstruction of normal data. When presented with abnormal inputs, these networks struggle to reconstruct anomalous
regions, leading to discernible deviations. By comparing
original and reconstructed images, anomalies can be localized without pixel-level annotations. For instance, GANomaly
employs an encoder-decoder architecture with a discriminator
for anomaly detection in luggage [17], while f-AnoGAN
explores W-GAN for medical imaging [18]. Wang et al.
enhanced this structure for pavement distress detection by
incorporating modules that comprehend fundamental texture
information [31]. Yu et al. proposed FastFlow, utilizing 2D
normalizing flows as a probability distribution estimator [32].
However, the direct application of these methods to pavement
distress segmentation may be suboptimal due to the nonstandardized nature of field-acquired pavement images and
the prevalence of distressed sections in typical data collection
practices.
Another weakly supervised learning scheme tries to establish a mapping between different image categories. This
approach is to train a mapping from class A images to class
B based on GANs. It is often used for entertainment tasks
such as image style transfer. For example, Zhao et al. propose
a GAN-based method with adversarial consistency loss for
selfie to anime and other similar tasks [20]. If the image is
classified as normal or abnormal, and a mapping function from
abnormal image to normal one is trained, the abnormal region
can be obtained by comparing the images before and after
mapping, and the pixel-level segmentation can be realized.
Siddiquee et al. devises a Fixed-Point network that utilizes
weak label information, resulting in a more robust human
disease detection capability than f-AnoGAN since the image is
pre-categorized as normal or abnormal [21]. Ren et al. create
a PAD-Net for detecting pavement distress, which enhances
the detection ability of fine objects and achieves pixel-level
distress segmentation [16].
Despite these advancements, fully unsupervised pixel-level
solutions for pavement distress segmentation remain limited.
The discussed weakly supervised methods utilize image-level
annotations to guide network convergence, achieving pixellevel segmentation but still requiring a degree of supervision.
This limitation emphasizes the need for further research into
unsupervised methods that can effectively address the challenges specific to pavement distress detection.
C. Self-Supervised Learning Without Manual Annotations
and Knowledge Gaps
Self-supervised learning offers an effective tool to achieve
unsupervised representations by designing pretext tasks that
generate artificial labels, enabling feature learning under
unsupervised conditions. Wu et al. develop an instance discrimination task, where an image and its argumentations are
considered positive samples while all other images are negative
ones, delineating the direction for network optimization [33].
Tian et al. propose a contrast learning method by maximizing

23421

mutual information between different views of the same scene
[34]. Pathak et al. train context encoders by contrasting an
image and the same image with missing regions [35]. More
recently, a unified scheme that predicts different views of the
same image via Siamese networks has emerged [23], [25].
However, these generic pretext tasks may not be optimal for
“long and strip” pavement images with scattered foreground
objects, and mere deep representation is insufficient for pixellevel segmentation. Consequently, three critical questions arise
in developing self-supervised learning for pavement distress
segmentation: (i) how to automatically generate pseudo-labels
from pavement images? (ii) how to train a deep neural network
using these potentially noisy pseudo-labels? and (iii) how to
utilize the trained deep neural network for segmentation?
Addressing these challenges requires leveraging domainspecific characteristics, such as the spatial contexts between
continuous pavement images. The design of task-specific pretext tasks is crucial, as they should be customized to each
computer vision application to exploit inherent data structures
effectively.
III. S PATIAL C ONTEXTS -I NFORMED S ELF -S UPERVISED
PAVEMENT D ISTRESS S EGMENTATION
The proposed scheme builds upon self-supervised learning
but addresses the limitations of existing approaches, including:
(i) proposing a spatial contexts-informed pretext task leverages consistent semantics across continuous pavement images;
(ii) introducing open-ended multi-line parallel networks to
exploit various noisy pseudo labels; and (iii) achieving distress
segmentation in a fully unsupervised condition through the
incorporation of the self-attention mechanism.
A. Spatial Contexts-Informed Pretext Task
Consider the set of continuous image frames captured by
the pavement detection vehicle as {xt }, where xt represents the
image captured at time t. When the time interval between xt1
and xt2 is sufficiently small, it can be assumed that they contain
similar semantic information. This characteristic can be termed
as spatial contexts. These similar images are then input to the
network N for deep representations, which can be express as
N(xt1 ) = z1 , N(xt2 ) = z2 . Valuable deep representations can be
learned by optimizing the network N by minimizing loss function L(z1 , z2 ). Specifically, a pavement image xt obtained at any
given time can be expressed as xt = (α1 , α2 , α3 , · · · β1 , · · · ),
where αi represents the normal areas and βi represents the
abnormal distress areas on the pavement. Given that the
pavement is constructed to uniform standards, the normal
pavement should be consistent. Therefore, the network N
should focus on the abnormal areas. Highlighting the focused
areas can help to segment the abnormal areas, which in this
case are pavement distress.
Contemporary datasets of pavement images in practical
applications typically consist of entire road that have been
segmented by mileage. The dataset used in this paper comprises 1,000 images sorted by mileage, each with a size of
3008 × 2048. As shown in Figure 1, a sliding window is
designed with a size of 256 × 256 and a stride of 64 to

23422

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 12, DECEMBER 2025

independently at the main view xt . As shown in Figure 2,
the latent representation obtained from the view that leaves
the input image unchanged after forwarding the network is
considered the label, while the latent representations obtained
from the remaining views after forwarding the network serve
as predictions. Subsequently, evaluating the difference between
the label and the prediction through cross-entropy loss is a
feasible solution:
S(z1 , z2 ) = −z2 log z1

(1)

Indeed, this constitutes a mutual prediction problem where
any view can be treated as a label. Consequently, the calculation can be expressed as follows:
1
1
S (z1 , z2 ) + S (z2 , z1 )
(2)
2
2
The final loss function is obtained by accumulating the
different views and the original input image:
L(z1 , z2 ) =

Fig. 2. Training pipeline of multi-line parallel network.

simulate the image frames. Specifically, it will intercept the
image frames xt from the original dataset images Xi in turn
and name them according to the two-dimensional coordinates.
Considering the calculation cost, a queue is employed to store
the large images Xi and Xi+1 . They are contacted into image
Xc during obtaining the frames. Xi exits the queue when the
sliding window is completely across it, then Xi+2 joins the
queue, and so on. It can avoid the dismiss of information at the
connect areas of each image. After this preprocessing, about
1 300 000 image frames are obtained. Adjacent frames can be
located according to their coordinates. For example, an image
xt with coordinate (m, n) has 4 adjacent images, which are
image x(m−1,n) , x(m+1,n) , x(m,n−1) , and x(m,n+1) . Considering their
similar semantic information, the spatial contexts-informed
pretext task is proposed. The aim is to learn a mapping
function N(xt ) = z to implement a deep representation of
the feature space and evaluate the spatial contexts from the
parallel models as d = S (N(v1 ), N(v2 )), where S is a metric
function. v1 and v2 are the different views of the input image xt .
Here the direction of convergence of the deep leaning model
is artificially created by minimizing d = S (N(v1 ), F(v2 )), it
enables an unsupervised training pipeline without any manual
labeling.
B. Multi-Line Parallel Network for Various Pretext Tasks
To incorporate the proposed spatial contexts-informed pretext task into deep representation learning, we extend the
Siamese Network into an open-ended multi-line parallel network. This architecture leverages spatial contexts-informed
pseudo-labels while remaining flexible for integrating additional pretext tasks, as shown in Figure 2. This structure
enables the input data to acquire deep representations within
the same batch and complete the evaluation after passing
through the projection layer. Taking the case where the batch
size is 1 as an example, the deep representation y = f (v)
is initially obtained through the backbone network, utilizing different views v. Subsequently, z = g(y) is derived
through a multi-layer perceptron (MLP). These projection
vectors undergo softmax processing, and the loss is calculated

Ltotal = L1 (v1 , v2 ) + L2 (v1 , v3 ) + · · · + Li (v1 , vi+1 )

(3)

The standard ViT [32] is chosen as the backbone network
f (v), with its classifier removed. All parallel networks employ
an identical architecture based on the same backbone network,
initialized randomly. In branch 1 of the main view, parameters
are not updated through backpropagation. Instead, a stop
gradient strategy is employed, and parameters are updated
through a momentum encoder from other branches that utilize
normal backpropagation. This process is encapsulated by the
following equation:
θt = αθt−1 + (1 − α)θt

(4)

where θ is the network parameter, t represents the iteration
step, and α is the smoothing parameter that controls the
moving average of the momentum encoder.
C. Unsupervised Segmentation via Self Attention
The backbone network trained by parallel networks has
acquired the ability to represent the image frame xt and its
different views, which contain similar semantic information. It
directs attention either towards regions of normal pavement,
serving as the background, or towards regions of pavement
distress, signifying the foreground. Pixel-level segmentation
of pavement distress can be realized by revealing areas of
focus or neglect by the backbone network. Following selfdistillation with no labels (DINO) [36], when utilizing ViT
as the backbone network, the input image is initially encoded
into vectors through linear projections:
zi = xip E,

2

E ∈ R(P •C)×D

(5)

These vectors, together with position embeddings and classification token, make up the input to the ViT encoder:
y0 = [xclass ; zi ;] + E pos ,

E ∈ R(N+1)×D

(6)

y0 will be normalized and put into the MSA block and MLP
block:
y01 = MSA (LN(y0 )) + y0

y1 = MLP LN(y01 ) + y01

(7)
(8)

REN et al.: SPATIAL CONTEXTS-INFORMED SELF-SUPERVISED LEARNING APPROACH

23423

Here MSA performs the following calculations:


QK T
Attention(Q, K, V) = softmax √
V
(9)
dk
√
In the above equation, softmax(QK T / dk ) denotes the attention scores. For the one-dimensional classification token, its
attention scores indicate the importance of each patch in measuring the semantic information about the consistency of the
input image, considering the spatial contexts-informed pretext
task. By visualizing the attention scores, a self-attention map
can be created. Semantic segmentation images can then be
obtained through simple thresholding.
D. Other Details
Following some settings from related contrastive learning
work [37], [38], the centering is set up for each branch
updated via backpropagation. Two A40 GPU is employed for
the experiments, with a batch size of 64. AdamW is utilized
as the optimizer and the learning rate is set to 0.0005. The
momentum parameter is set to 0.996.
IV. E XPERIMENTS
We conducted a comprehensive series of experiments to
evaluate the effectiveness of the proposed spatial contextinformed pretext task and the open-ended multi-line parallel
network architecture in pavement distress segmentation. The
proposed method requires the utilization of continuous pavement image characteristics. Although images captured under
standard conditions are generally sequential, only a few
available datasets meet this requirement. Consequently, our
experiments were conducted using the previously mentioned
continuous pavement dataset, Copave, which satisfies these
criteria. Our experimental analysis centers on three key
aspects:
(i) The comparative segmentation accuracy of our spatial
context-informed method against other pretext tasks.
(ii) The potential performance gains of the proposed
open-ended multi-line parallel network when integrated with
multiple pretext tasks.
(iii) The segmentation accuracy of our fully unsupervised
methods relative to weakly supervised approaches in the
context of pavement distress segmentation.
A. Experiment 1: Evaluating Spatial Context-Informed
Pretext Task Against Existing Methods
To quantitatively assess the segmentation accuracy of our
proposed spatial context-informed pretext task in comparison with state-of-the-art self-supervised learning methods, we
evaluate its task-specific suitability and efficacy for pavement
distress segmentation.
1) Baselines: Three state-of-the-art approaches are chosen
as baseline models, including:
(i) Masked autoencoders (MAE) [26]. As depicted in
Figure 3(a), MAE employs an masked image reconstruction pretext task to train the backbone and obtain a deep
representation of the image.

Fig. 3. Training pipeline of different approaches: (a) MAE; (b) BEIT;
(c) MoCo v3; and (d) Ours.

(ii) Bidirectional encoder representation from image Transformers (BEIT) [39]. As depicted in Figure 3(b), the backbone
is trained by comparing the visual token obtained from the
masked image block through the BEIT encoder with the visual
token obtained from the trained image tokenizer.
(iii) Momentum contrast for unsupervised visual representation learning version 3 (MoCo v3) [40]. As depicted in
Figure 3(c), MoCo v3 utilizes parallel networks to train the
backbone by comparing the deep representations of various
views of the same input image in each network.
2) Experiment Settings: This experiment implements unsupervised visual representation learning through self-supervised
learning. ViT-small networks serve as the backbone for all
models, and the training is conducted on the pavement image
dataset created in this paper, consisting of 1,300,000 image
frames. The hyperparameter settings for the three baseline
models adhere to the specifications outlined in the original
paper. The self-attention maps are obtained by visualizing the
attention scores of the classification token using the trained
ViT backbone networks. The proposed method deviates from

23424

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 12, DECEMBER 2025

Fig. 4. Self-attention maps for different pretext tasks.
TABLE I
E VALUATION M ETRICS FOR D IFFERENT P RETEXT TASKS

the baseline solely in terms of pretext task training. Each
method undergoes training for 20 epochs.
3) Results and Analysis: Figure 4 presents the selfsupervised attention maps generated by the three baseline
models (MoCo v3, MAE, and BEIT) and the proposed method,
all trained from scratch using random weight initialization.
For each approach, the self-attention head yielding the best
performance is selected for visualization. The outcomes reveal
that all methods exhibit varying capabilities in attending to
pavement distress regions. Compared to the baseline models,
the proposed method more effectively discriminates between
distressed foreground areas and the background pavement,
suggesting that the classification token employed in the proposed approach is more adept at identifying distress regions.
MoCo v3 primarily focuses on a few anomalous areas (yellow
and green), which are not clearly distinguishable from the
background pavement. MAE tends to assign higher attention
scores to background pavement regions while underemphasizing obvious distress areas. BEIT exhibits an alternating
behavior, attending to distress regions in some instances (second row of Figure 4) and background areas in others (third
row of Figure 4). Additionally, it demonstrates a tendency
to emphasize extensive distress patterns while potentially
overlooking finer crack regions.
After obtaining the attention scores for each image patch,
semantic segmentation results are derived through simple
thresholding at a value of 0.5 across all methods. Manually
labeled images serve as the ground truth for evaluation. Three
metrics, namely mean Dice coefficient (mDice), mean Intersection over Union (mIoU), and mean Pixel Accuracy (mPA),
are selected to assess segmentation performance. As illustrated
in Table I, the results reveal that the proposed method attains
optimal performance across all evaluation indicators. Taking
the mIoU metric as an example, the proposed approach at least

improves the segmentation accuracy by an absolute value of
0.048 compared to the baseline models.
The reasons for the poor performance of the three baseline
methods are different, which is highly related to their pretext
task. For example, the mask setting in MAE might cover the
pavement distress areas, particularly when the distresses are
fine cracks or potholes. Reconstructing the original image from
the remaining portion may prove challenging due to the lack of
meaningful information in most of the pavement background
pixels. The ability of MAE to reconstruct the original image
even with a high percentage of mask ratio (e.g., 75%) is
a major contribution in the original paper, and it yielded
surprisingly good results. However, in our task, we tested mask
ratios of 25%, 50%, and 75%, with the best outcomes achieved
at a 50% mask ratio. Therefore, the findings in Table I do not
align with the initial 75% mask ratio configuration. Figure 4
provides additional evidence, showcasing that MAE prioritizes
the background area of the image over the distress area.
MoCo v3 and the proposed method share similarities in
terms of model construction. However, the pretext task in
MoCo v3 involves predicting different views of the same
image using conventional image augmentation techniques such
as random cropping, flipping, and color jittering. These techniques do not fully exploit the benefits of continuous shooting
of pavement images. In contrast, the proposed method can
apply the MoCo v3 pretext task while also incorporating the
spatial context-informed pretext task due to their similarity in
model construction. A detailed analysis will be presented in
section IV-B.
The poor performance of BEIT primarily stems from its
unstable attention allocation. It utilizes a self-supervised training model similar to BERT, a natural language processing
method, and introduces a pretext task called masked image
modeling (MIM). The main difference between BEIT and
MAE is the use of the image tokenizer, enabling training
based on comparing visual tokens. The training process for
BEIT is more time-consuming than MAE. Since this encoder
incorporates out-of-domain data rather than solely relying on
pavement images, the model may concentrate its attention on
foreground regions and, in other cases, focuses on background
regions due to the nature of the MIM pretext task. This
inconsistency is particularly evident when detecting small
cracks. Figures 4 further illustrate that while BEIT performs
relatively well on large-scale defects, its segmentation accuracy is markedly insufficient for fine-grained defects such as
alligator cracks.
B. Experiment 2: Multi-Task Integration in Open-Ended
Multi-Line Parallel Networks
To systematically evaluate the performance of our openended multi-line parallel network architecture in integrating
multiple pretext tasks, we quantify its ability to leverage
diverse self-supervised signals and examines their impact on
segmentation accuracy.
1) Baselines: The proposed flexible multi-line parallel network is designed to integrate multiple semantically related
pretext tasks. As illustrated in Figure 5, the experiments
in this section investigate the combination of the spatial

REN et al.: SPATIAL CONTEXTS-INFORMED SELF-SUPERVISED LEARNING APPROACH

Fig. 5. Training pipeline for combining different pretext tasks.
TABLE II
E VALUATION M ETRICS FOR VARIOUS P RETEXT TASK C OMBINATIONS

context-informed (SC) task with regular data augmentation
(RDA) techniques, such as random flipping, color jitter, and
random grayscale [23], as well as the multi-crop strategy [24],
which involves representing the entire image using smaller,
localized patches. Multi-crop is commonly applied alongside traditional augmentation methods and has demonstrated
effectiveness in general visual representation learning. All
three tasks are suitable for self-supervised learning, as they
preserve semantic consistency with the original input and can
be compared against it during training. Following this process,
the trained network follows the testing method outlined in
Section III-C to obtain unsupervised segmentation results.
2) Experiment Settings: This section utilizes the same
encoder (ViT small) and loss function (described in
Section III-B) across all methods for consistency. The same
dataset containing 1.3 million images was used for training, with each method trained for 20 epochs. Pixel-level
segmentation is performed using the approach outlined in
Section III-C. The key difference lies in the self-supervised
pretext tasks employed during training, which include four
combinations: (1) using only regular data augmentation methods; (2) using only the proposed spatial context-informed task;
(3) combining regular data augmentation methods with multicrop augmentation; and (4) using the spatial context-informed
task along with regular data augmentation methods and multicrop augmentation.
3) Results and Analysis: Table II presents the quantitative
results under four experimental conditions. The outcomes
from Conditions 1 and 2 illustrate the adaptability of both
the regular data augmentation (RDA) method and the proposed spatial context-informed (SC) task for pavement distress
segmentation. The SC task outperformed RDA, achieving
0.515 mIoU, 0.635 mDice, and 0.778 mPA, representing

23425

Fig. 6. Self-attention maps for various pretext task combinations.

improvements of 17.0%, 10.4%, and 13.1%. When the multicrop strategy was introduced to the RDA method in Conditions
3, it exhibits notable performance gains. However, a substantial
performance gap remains when the SC task was excluded. As
shown in Condition 4, the proposed method achieved 0.583
mIoU, 0.706 mDice, and 0.827 mPA, representing improvements of 19.0%, 12.2%, and 14.7%. The comparison between
Condition 2 and Condition 4 underscore the benefit of the
flexible multi-line parallel network architecture, which enables
the integration of the SC task with other compatible pretext
tasks. As a result, the segmentation performance was further
enhanced by 0.068 mIoU, 0.071 mDice, and 0.049 mPA,
representing improvements of 13.2%, 11.2%, and 6.3%. These
results highlight two key strengths of the proposed method.
First, the spatial context-informed task is well-suited for
pavement distress segmentation. Second, the scalable multiline parallel architecture supports the seamless integration of
related self-supervised tasks, leading to consistently improved
segmentation performance.
Figure 6 illustrates the self-attention maps for various pretext task combinations. A comparison between condition 1
and condition 2 reveals that the spatial context-informed task
exhibits superior discrimination between foreground and background. This distinction is evident in the lower self-attention
score for the background, depicted in dark blue. Similarly,
when contrasting condition 2 with condition 3, it becomes
apparent that the spatial context-informed task outperforms the
combined pretext task involving normal data augmentation and
multi-crop. This is evident in the higher self-attention score
for the foreground patch, represented by a bright yellow/green
color. Condition 4 showcases our recommended optimal solution, amalgamating normal data augmentation, multi-crop, and
the spatial context-informed task. This solution effectively
distinguishes between foreground and background areas with
clarity and precision.
C. Experiment 3: Benchmarking Against Weakly Supervised
Frameworks
To benchmark our unsupervised approach against leading weakly supervised methodologies for pavement distress
segmentation, we empirically evaluate the viability of our

23426

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 12, DECEMBER 2025

label-free method as a practical alternative to approaches that
rely on image-level annotations.
1) Baselines: Given the scarcity of weakly supervised or
unsupervised methods explicitly tailored for pavement distress
segmentation, this section conducts a comparison with stateof-the-art anomaly detection methods commonly applied in
related domains, including human disease detection and industrial anomaly detection. These methods are categorized into
three groups based on the training pipeline, as illustrated in
Figure 7.
(i) Weakly supervised learning based on image reconstruction: The first step involves selecting normal images from
the original pavement dataset through image-level labeling.
Subsequently, a reconstruction network is trained with the
assumption that even for abnormal input images, the network
can generate a normal output. The identification of the distress
region is based on comparing the discrepancies between the
input and output images. Three commonly used methods
are employed in this experiment, including GANomaly [17],
f-Anogan [18], and FastFlow [32].
(ii) Weakly supervised learning based on image-to-image
translation: Initially, the original pavement dataset is categorized into two groups, normal and abnormal, guided by
image-level labels. Subsequently, a mapping function is trained
to transform abnormal images into a normal state. The detection of the distress area involves comparing the differences
observed before and after the transformation. Three commonly
used methods are employed in this experiment, including ACl
GAN [20], Fixed Point [21], and PAD Net [16]. Notably, PAD
Net is specifically designed for weakly supervised pavement
distress detection.
(iii) Self-supervised learning: The proposed method and
selected baseline approaches, including MAE [26], BEIT
[39] and MoCo v3 [40] (as mentioned in Section IV-A),
involve identifying distress regions through the utilization of
self-attention mechanisms. This is facilitated by formulating
pretext tasks and executing self-supervised training procedures.
2) Experiment Settings: Since this section involves completely different methods compared to the previous experiments, the recommended parameters for each weakly supervised method are followed, and training is performed until
convergence. All methods utilize the same dataset, which is
identical to the one used in Experiment 1 and Experiment
2. As weakly supervised methods require image-level labels,
400 images were manually labeled as either normal or abnormal, and a ResNet-101 classifier was trained to obtain these
image-level labels for the dataset.
3) Results and Analysis: Figure 8 illustrates the qualitative
outcomes of the experiments. FastFlow [32], f-Anogan [18],
and GANomaly [17] are classified as class A methods, while
ACl GAN [20], Fixed Point [21], and PAD Net [16] are
classified as class B methods. MAE [26], BEIT [39], MoCo
v3 [40] and the proposed approach are classified as class C
methods. The approaches tailored specifically for pavement
distress segmentation, such as PADNet and the proposed
method, demonstrated a distinct advantage by being capable of
approximately delineating the contours of cracks and potholes.

Fig. 7. Three types of training and testing for weakly supervised or
unsupervised pavement distress segmentation methods. (a) weakly supervised
learning based on image reconstruction; (b) weakly supervised learning based
on image-to-image translation; and (c) self-supervised learning.

This observation may stem from the low contrast of pavement
images captured in the field, as opposed to industrial or
medical images that typically exhibit a more standardized

REN et al.: SPATIAL CONTEXTS-INFORMED SELF-SUPERVISED LEARNING APPROACH

23427

TABLE III
E VALUATION M ETRICS FOR VARIOUS P RETEXT TASK C OMBINATIONS

Fig. 8. Segmentation results on baseline and proposed methods. (a) Input
image. (b)Manual label. (c) FastFlow. (d) GANormaly. (e) f-Anogan. (f) ACL
GAN. (g) Fixed Point. (h) PAD Net. (i) MAE. (j) MoCo v3 (k) BEIT (l) Ours.

and consistent shooting environment. Despite the comparison
being against weakly supervised schemes, the results achieved
by the proposed method are competitive.

The quantitative results of the experiments are presented
in Table III. Among the evaluated schemes, the proposed
method demonstrates superior performance except for PAD
Net in mIoU and mDice metric, but the proposed approach
exhibits a slight advantage in the mPA metric. Remarkably,
the proposed method surpasses the state-of-the-art unsupervised learning methods for general vision tasks, achieving a
substantial improvement of 0.143 when evaluated using the
mIoU index, as measured by the average accuracy across the
three methods. It is evident that different categories of methods
exhibit varying sensitivities to various evaluation metrics. The
direct application of weakly supervised methods, including
Class A and Class B, presents a trade-off: while these methods
are disadvantaged when prioritizing evaluation metrics such
as the intersection over union ratio (IoU), they exhibit an
advantage when favoring evaluation metrics like pixel accuracy (PA). This phenomenon can be attributed to the inherent
tendency of weakly supervised methods to regard objects
that are challenging to detect as background. Consequently,
pavement distresses often occupy a relatively small proportion
of the image, these methods can achieve high mPA scores
even when failing to detect all distresses. In contrast, selfsupervised methods (Class C) are predisposed to identifying
the foreground region, rendering them more susceptible to
misclassifying the background region.
While the performance difference between the proposed
method and the state-of-the-art weakly supervised schemes
like PAD Net is marginal, the proposed approach demonstrates
its own merits. Figure 9 illustrates the outcomes obtained when
training PAD Net and the proposed method on datasets of varying sizes. When trained on the entire dataset (100%), PAD Net
encountered a gradient vanishing issue, resulting in premature
termination. This problem can be attributed to the imbalance
between positive and negative samples, with 1,066,130 normal
images and only 259,473 abnormal images. The red square
points in Figure 9 represent the results obtained by training
on a dataset generated by cropping 1000 high-resolution
images into smaller ones, rather than using sliding windows
(followed as [16]). This cropping strategy offers the advantage
of creating a relatively balanced distribution of positive and
negative samples, yielding favorable outcomes. A comparative
analysis of these two competitive methodologies reveals the
following observations: First, the proposed method exhibits a

23428

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 12, DECEMBER 2025

Fig. 10. Self-Attention maps for different settings.

Fig. 9. Results of training PAD net and the proposed method using datasets
of different sizes, with different metrics of (a) mIoU, (b) mPA.

progressive increase in performance as the dataset size grows,
ultimately achieving optimal results constrained by the dataset
scale. In contrast, PAD Net exhibits an erratic convergence
behavior and consistently underperforms in terms of the mPA
metric. Second, as the dataset size expands, fully unsupervised
methods can operate unhindered, while weakly supervised
methods require additional manual annotations, potentially
leading to sample imbalances and subsequently impacting
detection outcomes.
V. D ISCUSSION
While deep representations based on self-supervised learning have achieved remarkable success in general computer
vision tasks, their application to pixel-level segmentation
remains an emerging area, especially for targets like pavement
distress dominated by small, elongated, and irregularly shaped
objects such as cracks. This has necessitated the exploration
of specialized methods for pretext tasks of creating pseudo
labels. The proposed spatial context-informed pretext task
can be viewed as analyzing a video sequence of continuously captured pavement images. As the frames advance, the
human visual system can perceive a motion effect akin to
moving pavement distress, allowing contextual information to
be exploited. Experimental results demonstrate that the proposed scheme is better suited for pavement distress detection
compared to mask-based approaches like MAE and BEIT that
have achieved success in general vision tasks. Consequently,
the proposed multi-line parallel network incorporates data

Fig. 11. Comparison of loss convergence in different settings.
TABLE IV
E VALUATION M ETRICS FOR VARIOUS P RETEXT TASK C OMBINATIONS

augmentation techniques that preserve complete image information, rather than including mask-based schemes. Moreover,
compared to weakly supervised models, the proposed unsupervised approach offers key advantages beyond competitive
accuracy: (i) it does not require balanced label distributions,
and its performance can continually improve with increasing
data volumes; (ii) the approach is highly scalable, allowing
the integration of diverse pretext tasks; and (iii) the underlying
transformer architecture provides opportunities to enhance performance by effectively fusing multimodal information sources
beyond just visual data.
However, it does not imply that self-supervised learning networks can converge effectively without additional measures.
To enable the network to accurately detect distress targets,
some necessary configurations are adopted. This paper follows
a variety of different practices in related works, such as batch
normalization (BN) and centering, that were correlated with
the convergence of the proposed method. Four combinations

REN et al.: SPATIAL CONTEXTS-INFORMED SELF-SUPERVISED LEARNING APPROACH

Fig. 12. Evaluation of different pretext task during trainin.

of these techniques are experimented, as shown in Table IV.
Figure 10 displays the self-attention map, and Figure 11
shows the corresponding convergence of the loss. The results
in Table IV indicate only minor differences but the selfattention maps reveal significant distinctions. It is observed
that without centering, the self-attention layers concentrate
more on the background pavement region rather than the
foreground distress region. Consequently, when centering is
not used, the opposite threshold setting, i.e., removing the
more focused regions are employed. When both BN and
centering are used, the self-attention layer becomes more
sensitive to changes in the pavement, shown as the distress
regions receiving higher attention scores, while some of the
pavement regions are equally attended to. This makes the selfattention map noisy and unsuitable for unsupervised pavement
distress segmentation. A more notable difference appears in the
convergence of the loss in Figure 11, which fails to converge
well when both BN and centering are used. Considering the
above, only centering as the setting in this paper is employed.
It obtains the best mDice and mPA and exhibits a better selfattention map and loss convergence process. Unfortunately,
the theoretical underpinnings for these various configurations
remain a subject of debate, their effectiveness can vary across
different tasks.
Beyond this, a natural consideration is whether pretraining the model on a large common vision dataset could
enhance its performance. To investigate this, the methods in
section IV-A were evaluated using weights from a ViTsmall backbone network pre-trained on the ImageNet dataset
followed by fine-tuning on the pavement dataset using the
described methodologies. Figure 12 illustrates the progression
of the mIoU evaluation metric for different methods across
training epochs. Counterintuitively, as presented in Table I,
all four methods underperformed compared to training from
scratch. It was observed that the performance of these methods
did not improve with continued training, suggesting that this
phenomenon is not unique to the proposed approaches but
rather inherent in self-supervised learning methods. A potential explanation for this outcome may lie in the substantial
domain discrepancy between the ImageNet dataset, consisting
of natural images, and the pavement dataset, consisting of
specialized infrastructure images. Moreover, the backbone network obtained through supervised training on a classification

23429

task may differ fundamentally from those acquired through
unsupervised learning objectives. These findings underscore
the necessity of a large, domain-specific dataset and a tailored training strategy to effectively address pavement distress
detection tasks.
Although the proposed method has achieved competitive
results on the task of unsupervised pavement distress segmentation, there are still some limitations. Due to dataset and
computational resource constraints, this study, as an initial
exploration, failed to fully capture the deepest potential of
the proposed method. Based on the experience with existing
large multimodal models, the proposed approach may achieve
more competitive results as data size and model capacity
increase. On the other hand, under limited equipment and data
scenarios, efficient, rapid, and lightweight model training is
also a problem worth exploring.
VI. C ONCLUSION
Automated and intelligent distress detection is a crucial
enabler for future transportation infrastructure maintenance.
To circumvent the time-consuming and labor-intensive manual annotation required by deep learning-based pavement
distress segmentation methods, this paper explores a novel
self-supervised learning approach that eliminates the need
for manual labeling. The authors leverage the spatial context
present in continuous pavement images to create pseudolabels and design an open-ended multi-line parallel network
to learn deep representations using these labels, ultimately
segmenting distress regions via self-attention mechanisms.
Experimental results demonstrate that: (1) the proposed spatial
context-informed pretext task achieves an average 0.075 mIoU
higher accuracy than state-of-the-art approaches such as MAE,
BEIT, and MoCo v3 on the pavement distress segmentation task; (2) the proposed open-ended multi-line parallel
network exhibits the potential to integrate multiple pretext
tasks, with the combined scheme successfully improving
detection accuracy by 0.068 mIoU; (3) the proposed unsupervised method remains competitive with weakly supervised
approaches requiring image-level labels, surpassing most
weakly supervised techniques. The authors acknowledge that
the performance of the proposed approach is currently constrained by model and dataset size limitations but believe
that these findings will contribute to the development of
fully automated pavement distress detection systems, with
substantial performance enhancements achievable by scaling
these factors.
R EFERENCES
[1]
[2]
[3]
[4]
[5]

H. D. Cheng and M. Miyojim, “Automatic pavement distress detection
system,” Inf. Sci., vol. 108, nos. 1–4, pp. 219–240, Jul. 1998.
K. C. Wang and W. Gong, “Real-time automated survey system of
pavement cracking in parallel environment,” J. Infrastructure Syst.,
vol. 11, no. 3, pp. 154–164, Sep. 2005.
L. Ying and E. Salari, “Beamlet transform-based technique for pavement
crack detection and classification,” Comput.-Aided Civil Infrastruct.
Eng., vol. 25, no. 8, pp. 572–580, Nov. 2010.
Q. Li, Q. Zou, D. Zhang, and Q. Mao, “FoSA: F* seed-growing approach
for crack-line detection from pavement images,” Image Vis. Comput.,
vol. 29, no. 12, pp. 861–872, Nov. 2011.
W. Wang et al., “Pavement crack image acquisition methods and
crack extraction algorithms: A review,” J. Traffic Transp. Eng. (English
Edition), vol. 6, no. 6, pp. 535–556, Dec. 2019.

23430

[6]

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 12, DECEMBER 2025

C. Xiang, V. J. L. Gan, J. Guo, and L. Deng, “Semi-supervised
learning framework for crack segmentation based on contrastive learning
and cross pseudo supervision,” Measurement, vol. 217, Aug. 2023,
Art. no. 113091.
[7] S. Dorafshan, R. J. Thomas, and M. Maguire, “Comparison of deep
convolutional neural networks and edge detectors for image-based
crack detection in concrete,” Construct. Building Mater., vol. 186,
pp. 1031–1045, Oct. 2018.
[8] S. Park, S. Bang, H. Kim, and H. Kim, “Patch-based crack detection
in black box images using convolutional neural networks,” J. Comput.
Civil Eng., vol. 33, no. 3, May 2019, Art. no. 04019017.
[9] Y. Cha, W. Choi, and O. Büyüköztürk, “Deep learning-based crack
damage detection using convolutional neural networks,” Comput.-Aided
Civil Infrastruct. Eng., vol. 32, no. 5, pp. 361–378, 2017.
[10] V. P. Tran, T. S. Tran, H. J. Lee, K. D. Kim, J. Baek, and T. T. Nguyen,
“One stage detector (RetinaNet)-based crack detection for asphalt pavements considering pavement distresses and surface objects,” J. Civil
Structural Health Monitor., vol. 11, no. 1, pp. 205–222, Feb. 2021.
[11] H. Liu, X. Miao, C. Mertz, C. Xu, and H. Kong, “CrackFormer: Transformer network for fine-grained crack detection,” in Proc. IEEE/CVF
Int. Conf. Comput. Vis. (ICCV), Oct. 2021, pp. 3783–3792.
[12] Z. Qu, C. Cao, L. Liu, and D.-Y. Zhou, “A deeply supervised convolutional neural network for pavement crack detection with multiscale
feature fusion,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 9,
pp. 4890–4899, Sep. 2022.
[13] K. Zhang, Y. Zhang, and H.-D. Cheng, “CrackGAN: Pavement crack
detection using partially accurate ground truths based on generative
adversarial learning,” IEEE Trans. Intell. Transp. Syst., vol. 22, no. 2,
pp. 1306–1319, Feb. 2021.
[14] R. Ren, F. Liu, P. Shi, H. Wang, and Y. Huang, “Preprocessing of crack
recognition: Automatic crack-location method based on deep learning,”
J. Mater. Civil Eng., vol. 35, no. 3, Mar. 2023, Art. no. 04022452.
[15] Y. Zheng, Y. Gao, S. Lu, and K. M. Mosalam, “Multistage semisupervised active learning framework for crack identification, segmentation,
and measurement of bridges,” Comput.-Aided Civil Infrastruct. Eng.,
vol. 37, no. 9, pp. 1089–1108, Jul. 2022.
[16] R. Ren, P. Shi, P. Jia, and X. Xu, “A semi-supervised learning approach
for pixel-level pavement anomaly detection,” IEEE Trans. Intell. Transp.
Syst., vol. 24, no. 9, pp. 10099–10107, Sep. 2023.
[17] S. Akcay, A. Atapour-Abarghouei, and T. P. Breckon, “GANomaly:
Semi-supervised anomaly detection via adversarial training,” in Proc.
14th Asian Conf. Comput. Vis., Perth, WA, Australia. Cham, Switzerland:
Springer, Dec. 2019, pp. 622–637.
[18] T. Schlegl, P. Seeböck, S. M. Waldstein, G. Langs, and U. SchmidtErfurth, “F-AnoGAN: Fast unsupervised anomaly detection with
generative adversarial networks,” Med. Image Anal., vol. 54, pp. 30–44,
May 2019.
[19] J. Song, K. Kong, Y.-I. Park, S.-G. Kim, and S.-J. Kang, “AnoSeg:
Anomaly segmentation network using self-supervised learning,” 2021,
arXiv:2110.03396.
[20] Y. Zhao, R. Wu, and H. Dong, “Unpaired image-to-image translation
using adversarial consistency loss,” in Proc. 16th Eur. Conf. Comput.
Vis. (ECCV), Glasgow, U.K. Cham, Switzerland: Springer, Aug. 2020,
pp. 800–815.
[21] M. M. R. Siddiquee et al., “Learning fixed points in generative adversarial networks: From image-to-image translation to disease detection
and localization,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2019, pp. 191–200.
[22] X. Huang, M.-Y. Liu, S. Belongie, and J. Kautz, “Multimodal unsupervised image-to-image translation,” in Proc. Eur. Conf. Comput. Vis.,
2018, pp. 172–189.
[23] J.-B. Grill et al., “Bootstrap your own latent-a new approach to selfsupervised learning,” in Proc. 34th Int. Conf. Neural Inf. Process. Syst.,
2020, pp. 21271–21284.
[24] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, “A simple framework
for contrastive learning of visual representations,” in Proc. Int. Conf.
Mach. Learn., 2020, pp. 1597–1607.
[25] X. Chen and K. He, “Exploring simple Siamese representation learning,”
in Proc. IEEE Comput. Soc. Conf. Comput. Vision Pattern Recognit.,
Jun. 2021, pp. 15750–15758.
[26] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 16000–16009.
[27] O. Ronneberger, P. Fischer, and T. Brox, “U-Net: Convolutional networks for biomedical image segmentation,” in Proc. 18th Int. Conf. Med.
Image Comput. Comput.-Assist. Intervent., vol. 9351. Cham, Switzerland: Springer, 2015, pp. 234–241.

[28] J. Long, E. Shelhamer, and T. Darrell, “Fully convolutional networks
for semantic segmentation,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2015, pp. 3431–3440.
[29] Y. Wang, K. Song, J. Liu, H. Dong, Y. Yan, and P. Jiang, “RENet:
Rectangular convolution pyramid and edge enhancement network for
salient object detection of pavement cracks,” Measurement, vol. 170,
Jan. 2021, Art. no. 108698.
[30] Y. Hou et al., “A deep learning method for pavement crack identification
based on limited field images,” IEEE Trans. Intell. Transp. Syst., vol. 23,
no. 11, pp. 22156–22165, Nov. 2022.
[31] W. Wang and C. Su, “Semi-supervised semantic segmentation network
for surface crack detection,” Autom. Construction, vol. 128, Aug. 2021,
Art. no. 103786.
[32] J. Yu et al., “FastFlow: Unsupervised anomaly detection and localization
via 2D normalizing flows,” 2021, arXiv:2111.07677.
[33] Z. Wu, Y. Xiong, S. X. Yu, and D. Lin, “Unsupervised feature learning
via non-parametric instance discrimination,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., Jun. 2018, pp. 3733–3742.
[34] Y. Tian, D. Krishnan, and P. Isola, “Contrastive multiview coding,”
in Proc. Eur. Conf. Comput. Vis., Glasgow, U.K.. Cham, Switzerland:
Springer, 2020, pp. 776–794.
[35] D. Pathak, P. Krahenbuhl, J. Donahue, T. Darrell, and A. A. Efros,
“Context encoders: Feature learning by inpainting,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2016, pp. 2536–2544.
[36] M. Caron et al., “Emerging properties in self-supervised vision
transformers,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2021, pp. 9650–9660.
[37] M. Caron, I. Misra, J. Mairal, P. Goyal, P. Bojanowski, and A. Joulin,
“Unsupervised learning of visual features by contrasting cluster
assignments,” in Proc. NIPS, Dec. 2020, pp. 9912–9924.
[38] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum contrast for
unsupervised visual representation learning,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020, pp. 9729–9738.
[39] H. Bao, L. Dong, S. Piao, and F. Wei, “BEiT: BERT pre-training of
image transformers,” 2021, arXiv:2106.08254.
[40] X. Chen, S. Xie, and K. He, “An empirical study of training selfsupervised vision transformers,” in Proc. IEEE/CVF Int. Conf. Comput.
Vis., Oct. 2021, pp. 9640–9649.

Ruiqi Ren received the B.E. degree in civil engineering from Central South University and the
Ph.D. degree in intelligent transportation science and
technology from Soochow University. His research
focuses on the application of deep learning and
computer vision techniques for infrastructure health
monitoring, with a particular interest in developing
efficient, automated methods for pavement distress
diagnosis and structural health assessment.

Peixin Shi received the Ph.D. degree in civil and
environmental engineering from Cornell University.
He is a Full Professor with the School of Rail Transportation, Soochow University. His research topics
include tunneling and underground space technology, smart infrastructure systems for underground
environments, and lifeline earthquake engineering.

Jinwoo Kim received the Ph.D. degree in civil and
environmental engineering from Seoul National University, South Korea. His long-term goal is to realize
human-centered digitalization and robotic automation in the construction industry. He is currently
working at the Department of Civil and Environmental Engineering, Hanyang University, South Korea,
as an Assistant Professor. To this end, he researches
how to leverage and integrate emerging artificial
intelligence and automation technologies with longestablished human theories and knowledge.
PAPER_TEXT
