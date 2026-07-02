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
# [572] VarAD: Lightweight High-Resolution Image Anomaly Detection via Visual Autoregressive Modeling
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
编号：572
题名：VarAD: Lightweight High-Resolution Image Anomaly Detection via Visual Autoregressive Modeling
年份：2024
DOI：10.1109/tii.2024.3523574
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2024.3523574.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 5
已有代码状态：已下载；VarAD -> source\VarAD

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\572.txt
- 原始字符数：50152
- 本次发送字符数：50152
- 是否截断：False

代码包：
- 仓库：VarAD
  - URL：https://github.com/caoyunkang/VarAD
  - 状态：downloaded
  - 本地目录：source\VarAD
  - 顶层结构：.gitignore、.idea/、LICENSE、README.md、assets/、config/、dataset/、init.sh、main.py、model/、tool/
  - 主要语言：Python:36、JSON:14、Shell:1
  - README 标题：VarAD: Lightweight High-Resolution Image Anomaly Detection via Visual Autoregressive Modeling、Abstract、Framework、Install、Run、Performance under 1024 Resolution、BibTex、Index Terms、VarAD: Lightweight High-Resolution Image Anomaly Detection via Visual Autoregressive Modeling、Abstract
  - README 运行线索：bash sh init.sh # note that there may be some remained bugs；bash python main.py --image_size 512 --model dinov2_vits14；bash sh init.sh # note that there may be some remained bugs；bash python main.py --image_size 512 --model dinov2_vits14；bash sh init.sh # note that there may be some remained bugs；bash python main.py --image_size 512 --model dinov2_vits14
  - 关键文件：{"推理/演示入口": ["main.py"], "模型定义": ["model/VarAD/tokenizer_backbones/dino/model.py"], "训练入口": ["model/VarAD/trainer.py"]}
  - 数据集线索：Quic、Tor、dapt、mvtec、nsl、quic、ton、tor

论文正文包开始：
<<<PAPER_TEXT
3246

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 4, APRIL 2025

VarAD: Lightweight High-Resolution Image
Anomaly Detection via Visual
Autoregressive Modeling
Yunkang Cao , Graduate Student Member, IEEE, Haiming Yao , Graduate Student Member, IEEE,
Wei Luo , Student Member, IEEE, and Weiming Shen , Fellow, IEEE

Abstract—This article addresses a practical task: highresolution image anomaly detection (HRIAD). In comparison to conventional image anomaly detection for lowresolution images, HRIAD imposes a heavier computational
burden and necessitates superior global information capture capacity. To tackle HRIAD, this article translates image anomaly detection into visual token prediction and
proposes visual autoregressive modeling-based anomaly
detection (VarAD) based on visual autoregressive modeling
for token prediction. Specifically, VarAD first extracts multihierarchy and multidirectional visual token sequences,
and then employs an advanced model, Mamba, for visual
autoregressive modeling and token prediction. During the
prediction process, VarAD effectively exploits information
from all preceding tokens to predict the target token. Finally, the discrepancies between predicted tokens and original tokens are utilized to score anomalies. Comprehensive
experiments on four publicly available datasets and a realworld button inspection dataset demonstrate that the proposed VarAD achieves superior HRIAD performance while
maintaining lightweight, rendering VarAD a viable solution
for HRIAD.
Index Terms—Autoregressive modeling, image anomaly
detection, token prediction.

I. INTRODUCTION
MAGE anomaly detection (AD) aims to identify irregular
patterns within images, playing a crucial role in industrial
defect inspection [1]. While existing AD methods [2], [3] excel
in low-resolution settings, typically 256 × 256, and achieve
high-detection performance on standard datasets like MVTec

I

Received 15 November 2024; accepted 14 December 2024. Date of
publication 16 January 2025; date of current version 4 April 2025. This
work was supported by the Ministry of Industry and Information Technology of the People’s Republic of China under Grant #2023ZY01089,
and in part by the HPC Platform of Huazhong University of Science and
Technology where the computation is completed. Paper no. TII-24-6079.
(Corresponding author: Weiming Shen.)
Yunkang Cao and Weiming Shen are with the State Key Laboratory of Intelligent Manufacturing Equipment and Technology, Huazhong
University of Science and Technology, Wuhan 430074, China (e-mail:
cyk_hust@hust.edu.cn; wshen@ieee.org).
Haiming Yao and Wei Luo are with the State Key Laboratory of Precision Measurement Technology and Instruments, Department of Precision Instrument, Tsinghua University, Beijing 100084, China (e-mail:
yhm22@mails.tsinghua.edu.cn; luow23@mails.tsinghua.edu.cn).
Code is available at https://github.com/caoyunkang/VarAD.
Digital Object Identifier 10.1109/TII.2024.3523574

AD [4], real-world applications often demand high-resolution
images (1024 × 1024 or higher) for inspection.
This requirement is due to the potential defects being extremely minute compared to the overall product, rendering
low-resolution AD methods less effective [5]. Although it is
feasible to directly downsample high-resolution images to a
lower resolution for inspection, this process can cause the loss of
critical details regarding subtle anomalies. For instance, certain
scenarios like plastic part inspection [2] and lens inspection [6]
necessitate detecting anomalies of approximately 1 mm× 1 mm
in a product measuring 100 mm× 100 mm. Such anomalies are
incredibly challenging to detect in low-resolution (256 × 256)
images, as they occupy only about five pixels. Conversely, in
high-resolution images (1024 × 1024), these anomalies occupy
around 100 pixels, significantly easing the detection process.
While it can be feasible to apply a sliding window strategy [7]
to high-resolution images to obtain smaller patches instead of
downsampling, this approach can lose global information within
images and lead to unreliable detection results. Hence, this study
proposes to detect anomalies directly in high-resolution images,
namely high-resolution image anomaly detection (HRIAD).
In comparison to the typical low-resolution AD setting,
HRIAD faces several inherent challenges. Thus, the computational burden increases significantly with high-resolution images, and capturing global information, which can be critical for detecting certain anomalies, is more challenging compared to low-resolution counterparts. Some reconstructionbased AD methods, like reverse distillation for anomaly detection (RD4AD) [8], can capture a certain level of global
information. Specifically, these methods begin by extracting
visual tokens using a vision tokenizer and then reconstructing
these tokens through a bottleneck module. Anomaly scores
are derived from the discrepancies between the original and
reconstructed visual tokens. The bottleneck can be based on
convolutional neural networks (CNNs) or vision transformers.
However, while the CNN-based bottleneck [8] [see Fig. 1(a)]
contributes to capturing neighboring information for reconstruction, its receptive fields remain limited and cannot utilize
all tokens for reconstruction, potentially diminishing their effectiveness for HRIAD. On the other hand, transformer-based
bottlenecks [9], [10] [see Fig. 1(b)] can achieve global receptive
fields through self-attention. However, the self-attention mechanism leads to a significant increase in computational demands
due to the quadratic complexity of attention calculations, making
transformer-based bottlenecks impractical for the HRIAD task.

1941-0050 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html
for more information.

CAO et al.: VarAD: LIGHTWEIGHT HIGH-RESOLUTION IMAGE ANOMALY DETECTION VIA VISUAL AUTOREGRESSIVE MODELING

3247

3) VarAD proposes to extract multihierarchy and multidirectional visual token sequences and utilizes Mamba for
autoregressing, achieving a better detection performance.
II. RELATED WORK
A. Image Anomaly Detection

Fig. 1. Motivation. By translating AD into token prediction, VarAD
demonstrates the ability to capture global information while remaining
lightweight.

Therefore, this study aims to introduce a lightweight HRIAD
model capable of capturing global information. Specifically, the
study proposes visual autoregressive modeling-based anomaly
detection (VarAD), which employs visual autoregressive (VAR)
modeling to capture the sequential relationships between visual
tokens. VarAD draws inspiration from the success of autoregressive models in large language models [11], renowned for
their robust global modeling capacity through next-token prediction. Similarly, VarAD formulates the HRIAD task as a token
prediction task, as illustrated in Fig. 1(c). It initially tokenizes
images into a sequence and trains the model to predict future
tokens based on previous ones. By training on normal images, the
model is expected to predict only normal tokens during testing.
Discrepancies between predicted and original tokens are then
utilized to score anomalies. In contrast to reconstruction-based
approaches with transformer-based bottlenecks [12], [13], [14],
which employ all input tokens to reconstruct normal tokens, our
method uses only preceding tokens to predict future ones. With
advanced VAR models, we reduce complexity to a linear scale
while preserving global information capture capabilities.
To enhance detection performance, VarAD proposes to
adapt a pretrained vision model (self-distillation with no labels(DINO) [15]) as the vision tokenizer for extracting visual
tokens. These multihierarchy visual tokens are then traversed
spatially via multiple directions into multiple token sequences.
These multihierarchy and multidirectional visual token sequences provide informative contexts and enable comprehensive
prediction of normal tokens. Furthermore, VarAD leverages
Mamba [16], an up-to-date autoregressive model for token prediction, achieving superior modeling capacity and efficiency.
Experimental results on four widely used public AD datasets
demonstrate the effectiveness and efficacy of VarAD.
In summary, this study makes the following contributions.
1) This study addresses a more practical setting, i.e.,
HRIAD, and conducts systematic benchmarks on this
setting, making a step toward practical industrial applications. While previous studies [5] have introduced HRIAD,
our benchmark is more comprehensive, encompassing
seven methods across four datasets with resolutions ranging from 256 × 256 to 1024 × 1024.
2) This study proposes to reformulate image anomaly detection as a token prediction task. VarAD based on VAR
modeling is proposed to address this task.

This study classifies existing image anomaly detection methods based on the type of information utilized, namely, local and
global information.
1) Local Information: Many image anomaly detection methods focus on extracting local information. These methods typically employ pretrained CNNs to extract image embeddings,
which are then used to model the distribution of these embeddings. Anomalies are detected based on discrepancies between
testing and training embeddings. Existing methods can be categorized into knowledge distillation [17], [18], [19], memory
bank [3], [20], discriminative [21], [22], and flow-based [23],
[24] methods. For example, knowledge distillation-based methods [17] align a pretrained teacher network with a randomly
initialized student network via normal images. They assume
that since the student and teacher networks are only aligned
via normal images, they will have different outputs for abnormal
images, and these discrepancies are utilized to detect anomalies.
Memory bank-based methods [3], [20], on the other hand, store
representative normal embeddings and score anomalies based
on the nearest distance to this bank. Sliding window-based selfsupervised learning (SWSSL) [7] introduces self-supervised
learning for augmentation-invariant features and combines these
features with memory banks for high-resolution medical image
anomaly detection. However, SWSSL still relies on a patch
encoder for feature extraction, which can only perceive local
information. Discriminative approaches like SimpleNet [22] and
global and local anomaly co-synthesis strategy (GLASS) [21]
typically train a network to differentiate between normal and
abnormal features for anomaly detection; however, such networks are often implemented using simple convolutional layers, which are limited to capturing local information. In addition, flow-based methods [23], [24] use flow models to model
normal embedding distribution directly. While these methods
have achieved promising detection performance for traditional
low-resolution scenarios, their effectiveness may diminish in
high-resolution images due to their limited capacity to capture
global information.
2) Global Information: Certain image anomaly detection
methods enhance their capacity to capture global information
by modifying their model architectures. Conventional image
anomaly detection methods are based on CNNs. For instance,
collaborative discrepancy optimization (CDO) [2] replaces
conventional backbones with high-resolution net (HRNet) [25]
to extract image embeddings with larger receptive fields.
RD4AD [8] and omni-frequency channel-selection reconstruction generative adversarial network (OCR-GAN) [26] introduce
bottlenecks to extract global context, followed by embedding
reconstruction based on global semantic information. In
addition, methods like global-local correspondence framework
(GLCF) [14] establish two network branches (global and
local) to extract and aggregate global and local embeddings,
respectively, thereby improving the capture of global
information. Similarly, EfficientAD [27] extends the

3248

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 4, APRIL 2025

knowledge-distillation scheme by operating in local and
global feature spaces simultaneously. Some approaches
explicitly target the capture of global information by using
visual transformers for reconstruction, such as partial semantic
aggregation vision transformer (PSA-VT) [9], prior normality
prompt transformer (PNPT) [13], and MLDFR [28], or
for inpainting, like inpainting transformer (Intra) [10]
and adaptive mask inpainting network (AMI-Net) [12].
However, the attention mechanisms in transformers often
lead to intensive computational demands due to the quadratic
complexity of attention calculations in both computation and
memory, hindering their applications in HRIAD. In contrast,
spatiotemporal consistency incorporated knowledge distillation
(STCIKD) [5] adopts a strategy to predict future tokens based
on several preceding tokens but still fails to extract information
from all preceding tokens. To capture global information
and enable lightweight detection, the proposed VarAD also
translates the anomaly detection task into token prediction and
exploits VAR modeling for great efficiency.
B. Autoregressive Modeling
1) Language Autoregressive Modeling: Language autoregressive modeling has gained significant traction for its promising global capture capacity, exemplified by GPT-4 [11]. A recent
advancement in this field is Mamba [16], which allows each
token in a sequence to interact with previously scanned tokens
via a compressed hidden state, reducing quadratic complexity
to linear. The efficacy of Mamba in long sequence modeling has
garnered considerable attention.
2) VAR Modeling: The success of language autoregressive
modeling has spurred efforts in VAR modeling. Early work,
such as vector quantized generative adversarial networ (VQGAN) [29], employs a decoder-only transformer to generate
image tokens in a standard raster-scan autoregressive manner,
leading to improved image generation quality. More recently,
VAR modeling has been utilized to construct visual foundation models. For instance, the large vision model (LVM) [30]
translates visual data into visual sentences and utilizes autoregressive training for next token prediction, enabling the solution
of various vision tasks by designing suitable visual prompts at
test time. The success of Mamba has also inspired numerous
works in the field of visual data. For example, the pioneering
endeavor VMamba [31] proposes traversing the spatial domain,
converting images into multidirectional visual token sequences,
and then utilizing Mamba for modeling, showcasing promising
capabilities across various visual perception tasks. Drawing
inspiration from these advancements in VAR modeling, this
study chooses to reformulate anomaly detection as a token
prediction task and utilizes Mamba for VAR modeling. The
proposed VarAD presents to have better HRIAD performance
and higher efficiency.

III. VARAD METHODOLOGY
A. Problem Definition
The HRIAD task is designed to meet practical requirements.
Following the mainstream unsupervised anomaly detection setting [2], the training set Ttrain for HRIAD consists of a collection

of high-resolution images (1024 × 1024 in this study) representing normal instances of a specific product category. The
objective is to develop a model capable of identifying anomalies
within unseen images from the same category and generating
a corresponding anomaly map A ∈ RH×W , where H and W
denote the resolution of the original images. In the anomaly map,
higher values indicate that the corresponding coordinate position
is more likely to be abnormal. Typically, the highest score of the
anomaly map can indicate the overall anomaly degree of the
whole image.
B. Method Overview
The proposed HRIAD method, VarAD, introduces a novel
approach by reformulating anomaly detection as a token prediction task. As shown in Fig. 2, this method comprises several key
steps. First, given an image, VarAD extracts multihierarchy and
multidirectional visual token sequences. Subsequently, in the
VAR modeling phase, VarAD leverages Mamba [16] to predict
future tokens based on previous tokens in an autoregressive
manner. Following this, VarAD computes the prediction errors
between the predicted tokens and the original tokens to assess
anomalies. Finally, the results from multihierarchy and multidirectional predictions are aggregated to produce the final anomaly
detection results.
C. Visual Token Sequence Extraction
The visual token sequence extraction step consists of two substeps: tokenizing the image into multihierarchy visual tokens,
which are then sequentialized into multidirectional visual token
sequences.
1) Image Tokenized: The descriptive quality of visual tokens, as described in LVM [30], plays a crucial role in the
autoregressive modeling process. VarAD proposes to adapt a
pretrained vision model, DINO [15], as the visual tokenizer.
Specifically, the image is inputted into the pretrained visual
model, and tokens from specific layers are extracted to form
H
W
multihierarchy visual tokens Fh ∈ RC× N h × N h , where N h is
the downsampling ratio of hth hierarchy and H is the number
of hierarchies. However, since the pretrained model is trained
on natural image datasets, its descriptiveness may diminish
when applied to the target category due to domain gap issues.
Therefore, VarAD addresses this challenge by adapting the
pretrained DINO model. This adaptation involves integrating
a feature adapter φh (·) for each hierarchy feature and utilizing
a residual connection to obtain the adapted tokens F̂h
F̂h = φh (Fh ) + Fh , h = 1, . . . , H.

(1)

During training, the visual model remains frozen, while the
adapters are trainable. This approach mitigates the domain gap
without compromising the original descriptiveness.
2) Token Sequentialized: Autoregressive modeling is naturally designed for 1-D sequences and cannot be directly applied
to 2-D visual tokens. Hence, VarAD employs a spatial traversal
of the visual tokens and translates them into visual token sequences. A straightforward strategy might involve expanding the
visual tokens linearly along the row axis. However, this approach
restricts the token prediction process to only consider preceding

CAO et al.: VarAD: LIGHTWEIGHT HIGH-RESOLUTION IMAGE ANOMALY DETECTION VIA VISUAL AUTOREGRESSIVE MODELING

Fig. 2.

3249

Framework of the proposed VarAD.

tokens, thereby potentially sacrificing valuable post-target information. To overcome this limitation, VarAD introduces a multidirectional scanning function denoted as MDS, which scans
visual tokens in multiple directions. This innovation allows for
the comprehensive retention of information crucial for accurate
token prediction. Illustrated in Fig. 2, VarAD unfolds visual
tokens along rows and columns into sequences, proceeding
to scan along four distinct directions: top-left to bottom-right,
bottom-right to top-left, top-right to bottom-left, and bottom-left
to top-right. This ensures that each token integrates information
from all tokens, enhancing predictive accuracy across various
directions. The process is formulated as follows:
 
(2)
{v1 , . . . , vLh }hk = MDS F̂h , k = 1, 2, 3, 4
where {v1 , . . . , vLh }hk represents the kth directional visual token
sequence of the hth hierarchy. Lh denotes the length of the visual
token sequences, which is equal to NHh × NWh .
D. Visual Autogressive Modeling
VarAD utilizes VAR modeling for token prediction. Specifically, Mamba [16] is utilized as the autoregressive model.
1) Mamba: The architecture of the Mamba model is visualized in Fig. 2, within which the state-space model (SSM) is
the most vital component. Specifically, SSMs are conventionally
recognized as linear time-invariant systems mapping stimulation
x(t) ∈ RL to response y(t) ∈ RL . These SSMs are typically
formulated as linear ordinary differential equations (ODEs) [see
(3)], with parameters including A ∈ RP ×P , B, C ∈ RP for a
state size P
h (t) = Ah(t) + Bx(t), y(t) = Ch(t).

(3)

The continuous parameters A and B can be discretized from
the continuous system into discrete parameters A and B with
zero-order hold with a timescale parameter 
A = exp (A)
B = (A)−1 (exp(A) − I) · B.

(4)

Postdiscretization, the model can be represented as
h(t) = Ah(t − 1) + Bx(t), y(t) = Ch(t).

(5)

In addition, Mamba associates the matrices A, B, C with the
input, thereby ensuring the dynamism of weights within autoregressive modeling.
2) Token Prediction: VarAD utilizes Mamba to predict the
lth token based on the previous tokens. However, due to the
potentially strong correlation between neighboring visual tokens, the conventional autoregressive approach used in language
modeling, i.e., next-token prediction, tends to overfocus on
nearby tokens for visual data. This overemphasis on neighboring tokens may hinder the learning of global information.
Therefore, VarAD proposes to predict the lth token based on
previous tokens, excluding the M nearest tokens, denoted by
{v1 , . . . , vl−M }. Given that the resolutions of features vary
across hierarchies, this study associates M with the feature
resolutions, setting M h = m NHh and M h = m NWh for the rowspanned and column-spanned token sequences, respectively,
where m is a hyperparameter named prediction step that controls
the length of tokens to be excluded.
Then, (5) for predicting the lth token is rewritten as
h(l) = Ah(l − 1) + Bvl−M , v l = Ch(l)

(6)

where h(l) denotes the hidden state at the lth step, incorporating
information from {v1 , . . . , vl−M }, and v l represents the predicted token. Thus, the token prediction process maintains linear
complexity, ensuring high efficiency even for high-resolution
images.
To predict the first M tokens, VarAD adds beginning of
sequence (BOS) tokens to the beginning of each visual token
sequence and end of sequence (EOS) tokens to the end, where
[BOS], [EOS] ∈ RM ×C . Then, utilizing (6), VarAD obtains the
predicted tokens as follows:
{[BOS], v1 , . . . , vL } −→ {v 1 , . . . , v L , [EOS]}

(7)

3250

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 4, APRIL 2025

TABLE I
STATISTICAL INFORMATION OF THE UTILIZED DATASETS

E. Anomaly Detection
The hypothesis of VarAD is that through training solely with
normal samples, the autoregressive model can exclusively predict normal tokens, thus the disparities between predicted tokens
and original tokens can be utilized to score anomalies. With (7),
VarAD has obtained predicted tokens for multihierarchy and
multidirectional visual token sequences. Subsequently, VarAD
proposes to aggregate predicted tokens from multiple directions,
thus ensuring that the prediction encompasses information from
all tokens (excluding neighboring ones). The process is formulated as


h
(8)
F = MDS−1 {v 1 , . . . , v Lh }hk , k = 1, 2, 3, 4
where MDS−1 represents the reverse function of the multidirectional scanning process MDS, which first traverses individual
1-D predicted token sequences back to 2-D visual tokens as
like F̂h , and then averages all the predicted 2-D tokens into the
h
predicted visual tokens F .
Subsequently, the prediction errors across multiple hierarchies are aggregated to produce the final anomaly maps A,
h

Ahij = ||Fij − F̂hij ||22
Aij =

H


(Ahij ).

2) Implementation Details: This study adopts a default resolution of 1024 × 1024 for HRIAD. All images undergo resizing
to match the dimensions of 1024 × 1024, followed by normalization using the mean and standard deviation obtained from the
ImageNet dataset. For image tokenization, DINO (ViT-S/14)1 is
utilized as the default method. Tokens from the fourth, eighth,
and 12th layers are selected to form multihierarchy visual tokens,
each possessing a channel size of C = 384. The hyperparameter
prediction step m is by default set to 4. The training process
utilizes the AdamW optimizer with a learning rate of 5 × 10−4
for 10 epochs. All experiments are performed on a computing
system equipped with Xeon(R) Gold 6226R CPUs@2.90GHz,
accompanied by one NVIDIA 3090-Ti GPU with 24 GB of
memory.
3) Evaluation Metrics: This study employs three widely used
metrics to evaluate anomaly detection performance: the area
under the receiver operating characteristic curve (AUROC), the
maximum F1 Score under optimal thresholds (max-F1), and
average precision (AP). The primary focus of the evaluation
is on pixel-level anomaly detection, while image-level metrics
are reported only for the main experiments. Notably, although
the per-region overlap (PRO) score is commonly used to assess
pixel-level performance and is widely adopted in low-resolution
settings, this study excludes it due to the significant computational overhead it imposes in HRIAD.
4) Comparison Methods: This study conducts a comparative analysis of the proposed VarAD with several popular anomaly detection methods. Specifically, the comparison methods include CNN-based methods, pretrained feature
mapping (PFM) [18], RD4AD [8], PatchCore [3], CDO [2],
PyramidFlow [23], and MultiScale Flow (MSFlow) [24], and
transformer-based methods, AMI-Net [12] and PNPT [13]. We
utilize their publicly available implementations, only adjusting
input resolutions to assess their performance in HRIAD.

(9)

h=1

During training, VarAD minimizes the anomaly maps A for
normal images, thereby ensuring that the predicted tokens are
similar to the original tokens, formulated as

Aij .
(10)
L=
ij

By optimizing VarAD with normal images through this objective, the prediction errors for normal tokens are expected to be
minimized, while the errors for abnormal tokens can be larger,
as VarAD is not trained to predict abnormal tokens.
IV. EXPERIMENTS
A. Experiments Setup
1) Dataset Descriptions: This study systematically evaluates the proposed VarAD on four publicly available datasets:
MVTec AD [4], visual anomaly (VisA) [32], beantech anomaly
detection (BTAD) [33], and describable texture dataset (DTD)Synthetic [34]. The statistical information of these datasets is
summarized in Table I, encompassing 42 categories in total, with
15 287 normal training samples, and 2237 and 3695 normal and
abnormal testing samples, respectively. These extensive datasets
provide a comprehensive HRIAD benchmark.

B. Main Results
1) Pixel-Level Comparisons: Table II illustrates the qualitative comparisons between VarAD and other alternatives in
the proposed HRIAD setting. While representative methods
such as PatchCore [3] and RD4AD [8] have reported saturated
performance in their original reports under the low-resolution
setting, their detection performance for high-resolution images
shows a notable decline. CDO [2] achieves promising detection
performance for high-resolution images because of its utilized
backbone HRNet [25], demonstrating the importance of global
information in HRIAD. MSFlow also achieves promising results
thanks to the designed multiscale flow model. Surprisingly,
while AMI-Net [12] and PNPT [13] utilize vision transformers that should be able to capture global information, they
still achieve subpar anomaly detection performance in comparison to other alternatives. In contrast, VarAD achieves the
best performance across all datasets, with AUROC scores of
97.7%, 98.5%, 97.8%, and 98.8% on the four datasets, respectively. VarAD exhibits significant improvements on BTAD
and DTD-Synthetic, outperforming the second-place method
CDO by 6.5% and 5.0% in max-F1, respectively, which underscore the superior global modeling capacity of the proposed
1 [Online]. Available: https://github.com/facebookresearch/dinov2

CAO et al.: VarAD: LIGHTWEIGHT HIGH-RESOLUTION IMAGE ANOMALY DETECTION VIA VISUAL AUTOREGRESSIVE MODELING

3251

TABLE II
QUANTITATIVE COMPARISONS OF VARAD WITH ALTERNATIVE METHODS ON PUBLIC DATASETS

Fig. 3.

Anomaly maps on the four publicly available datasets and our private data from the real-world button inspection task.
TABLE III
QUANTITATIVE COMPARISONS OF VARAD WITH ALTERNATIVE METHODS ON PUBLIC DATASETS

VarAD. Fig. 3 visualizes the detection results of VarAD and the
comparison methods, further demonstrating the superiority of
VarAD.
2) Image-Level Comparisons: Image-level anomaly detection results are also critical for HRIAD. As shown in Table III,
all methods exhibit a notable performance decline in HRIAD
compared to their original results in low-resolution settings.
For instance, PatchCore [3] achieves 99.1% AUROC on MVTec
AD in the low-resolution scenario, but only 93.1% in HRIAD.
Overall, MSFlow and CDO demonstrate superior performance
on MVTec AD and VisA, whereas our proposed VarAD
achieves the highest performance on BTAD and DTD-Synthetic,
surpassing the second-place methods by 0.2% and 0.4%
AUROCs.

C. Ablation Study
This study performs a series of ablation experiments to
thoroughly assess the impact of individual components within
VarAD. Given the primary focus on pixel-level performance in
this study, only pixel-level metrics are reported in the following
experiments.
1) Influence of Sequentialized Direction: During the token
sequentialization process, VarAD scans the visual tokens in
multiple directions to prevent potential information loss. Fig. 4
presents a comparison of the detection performance of VarAD
when scanning in different directions. The results indicate that
aggregating information from all directions consistently yields
superior performance compared to using a single direction. This

3252

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 4, APRIL 2025

Fig. 4. Anomaly detection performance of VarAD with different setups. From top to bottom: different scanning directions; different prediction steps
m; different feature adapters, where w/o indicates that the pretrained model is used to directly extract tokens; and different feature hierarchies.

underscores the effectiveness of utilizing multidirectional visual
token sequences.
2) Hyperparameter Sensitive Analysis: The only hyperparameter for VarAD is m, which controls the length of neighboring tokens to be excluded in the token prediction process.
This study assesses the detection performance of VarAD with
different values of m, and the results are presented in Fig. 4.
Generally, the prediction process becomes more challenging
with increased m, as more information from neighboring tokens
is excluded. Hence, with increased m, VarAD is expected to
acquire a stronger global modeling capacity. However, a larger
m may lead to the loss of local information and influence
the prediction quality. As visualized in Fig. 4, the detection
performance exhibits an increasing and then decreasing trend
with larger values of m, peaking at m = 4. Nevertheless, VarAD
is not sensitive to changes in m, showing only slight variations
in detection performance under different values of m.
3) Influence of Feature Adapter: The visual token sequence
extraction process involves tokenizing images into visual tokens.
VarAD defaults to utilizing the pretrained model DINO for tokenization and proposes a feature adapter to mitigate the domain
gap between the pretrained natural image data and the target
industrial data. We design several feature adapters for evaluation,
including a simple linear layer and a more complex residual
block (ResBlock). In addition to appending the feature adapters
after the pretrained model, we also explore a parameter-efficient
fine-tuning method, low-rank adaptation (LoRA) [35], and its
combination with the designed feature adapters, as shown in
Fig. 4. It is evident from the table that the feature adapter,

whether a linear layer or a ResBlock, significantly improves
detection performance, while solely using LoRA fails to mitigate
the domain gap and leads to subpar detection results. Combining
LoRA with the linear layer or ResBlock shows improvements in
certain metrics but declines in others. Furthermore, the complex
adapter ResBlock does not consistently outperform the simple
linear layer but can introduce more parameters. Therefore, we
default to using only the linear layer for feature adaptation,
improving more than 10.0% in max-F1 on MVTec AD, VisA,
and BTAD compared to the unadapted model.
4) Influence of Token Hierarchy: This study evaluates
VarAD under different combinations of token hierarchies. Generally, tokens from a shallow layer contain structural information, while those from a deeper layer may incorporate more
global information. As shown in Fig. 4, the combination of the
fourth, eighth, and 12th token hierarchies consistently achieves
better performance compared to other combinations. Therefore,
this combination is selected as the default setting for VarAD.
5) Influence of Backbone: To comprehensively investigate
the influence of backbones, this study compares VarAD with different backbones, including vision transformer (ViT) [36] undergoing supervised pretraining, masked auto encoder (MAE) [37],
contrastive language-image pre-training (CLIP) [38], and DINO
with various architectures. The comparison results are shown
in Table IV. It clearly demonstrates that pretrained backbones
significantly influence detection performance, indicating that
backbones trained with specific objectives may better suit VAR
modeling. We will further study the underlying mechanisms in
the future. Overall, VarAD with DINO-ViT-B/14 achieves the

CAO et al.: VarAD: LIGHTWEIGHT HIGH-RESOLUTION IMAGE ANOMALY DETECTION VIA VISUAL AUTOREGRESSIVE MODELING

3253

TABLE IV
ABLATION STUDY ON DIFFERENT BACKBONES FOR VARAD

Fig. 5.

Fig. 7.

Complexity comparisons of different methods.

Fig. 8.

(a) Real-world button inspection platform. (b) Samples.

Anomaly detection performance under different resolutions.

Fig. 6. Anomaly maps under different resolutions. (a) PFM.
(b) RD4AD. (c) PatchCore. (d) CDO. (e) PyramidFlow. (f) MSFlow.
(g) AMI-Net. (h) PNPT. (i) VarAD.

best anomaly detection performance. However, DINO-ViT-B/14
requires nearly four times the parameters compared to DINOViT-S/14 and achieves only 3.8 FPS. Consequently, after trading
off all factors, this study elects to use DINO-ViT-S/14 as the
visual tokenizer, achieving lightweight, efficient, and promising
high-resolution anomaly detection performance.

TABLE V
STATISTICAL INFORMATION OF THE COLLECTED BUTTON DATASET

D. Analysis
1) Influence of Image Resolution: This study evaluates the
detection performance of comparison methods under different
resolutions, namely 256 × 256, 512 × 512, 768 × 768, 1024 ×
1024. Fig. 5 presents their detection performance on the four
datasets under different resolutions. It shows that the existing
AD methods tend to perform weaker with larger resolutions.
For instance, the AUROC on MVTec AD of PatchCore decreases from 98.4% to 95.8% when image resolutions increase
from 256 × 256 to 1024 × 1024. While CDO can better capture
global information compared to other existing AD methods, it
still witnesses some drops in detection performance. In contrast, the proposed VarAD achieves commendable detection
performance across all resolutions. Its AUROC remains stable

for different resolutions. VarAD even witnesses some slight
improvements in max-F1 and AP with increased resolutions for
all datasets. Whereas VarAD may underperform compared to
other methods at low resolutions, such as 512 × 512 on VisA,
certain scenarios necessitate high-resolution images to address
subtle anomalies. In these cases, subtle anomalies may occupy
very few pixels (e.g., five) in low-resolution images, making
them difficult to detect. Fig. 6 further visualizes the detection
results of these comparison methods under different resolutions.
It is evident that VarAD consistently achieves excellent detection
results under improved resolutions, while other methods exhibit
deficiencies.

3254

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 4, APRIL 2025

TABLE VI
QUANTITATIVE COMPARISONS OF VARAD WITH ALTERNATIVE METHODS ON THE COLLECTED BUTTON INSPECTION DATASET

2) Complexity Analysis: Considering practical applications,
both anomaly detection performance and model efficiency require comprehensive evaluation. Specifically, this study conducts a fair comparison of various methods across the following
four dimensions:
1) training time—measured on a single NVIDIA 3090Ti
with a batch size of two;
2) number of parameters;
3) floating-point operations per second (FLOPs);
4) inference speed in terms of frames per second (FPS).
Fig. 7 demonstrates that transformer-based methods exhibit
higher computational complexity compared to others, while
CNN-based methods generally offer greater efficiency. Overall,
the proposed VarAD achieves the fastest training time, significantly lower FLOPs, and the highest average max-F1 score
across the four datasets. Specifically, VarAD converges within
only 10 epochs (389 s), whereas other methods, such as CDO and
RD4AD, typically require 50 epochs (over 1200 s). Moreover,
the parameter count and FLOPs of VarAD are lower than those
of other methods, with only a slight increase compared to PyramidFlow and MSFlow, yet demonstrating significantly better
performance. In terms of inference speed, VarAD operates in
an autoregressive manner, leading to a slightly lower FPS than
CNN-based methods such as PyramidFlow and MSFlow, which
utilize efficient flow models for rapid inference. Nevertheless,
VarAD achieves a commendable speed of 8.0 FPS.

E. Evaluations on Real-World Data
To further assess the applicability and effectiveness of VarAD,
this study develops an image acquisition platform, as depicted
in Fig. 8(a), and gathers private data from a real-world button
inspection task. During the image acquisition process, various types of noise are intentionally introduced to assess the
robustness of the comparison methods, including unaligned
positions of buttons, different illumination conditions, and background interference. These noise types render the established
real-world button inspection dataset more challenging than the
four public datasets utilized in this study. In addition, these buttons feature potential subtle and small anomalies, necessitating
HRIAD. Hence, we acquire images with a high resolution of
1024 × 1024. Representative samples from the dataset are visualized in Fig. 8(b). The constructed dataset consists of four
categories of buttons. Table V shows the detailed statistical
information for the collected button datasets.
Table VI provides a category-level quantitative comparison of
results on the established dataset. It is apparent that all methods
demonstrate weaker performance on this dataset compared to
their results on public datasets, indicating the increased difficulty

of the established dataset. Nevertheless, VarAD achieves notably
superior detection results compared to other methods, with
impressive scores of 96.8% AUROC, 36.0% max-F1, and 30.8%
AP. VarAD surpasses the second-place method, CDO, by 0.1%
AUROC, 5.4% max-F1, and 4.6% AP. The qualitative anomaly
localization comparison results of various methods are depicted
in Fig. 3 (Button). It is evident that the proposed VarAD achieves
significantly better detection results than other alternatives.
V. CONCLUSION
In summary, this article presents VarAD, a novel approach for
detecting anomalies in high-resolution images. VarAD transforms anomaly detection into a token prediction task, utilizing Mamba for VAR modeling. By predicting future tokens
in multihierarchy and multidirectional visual token sequences,
VarAD effectively scores anomalies based on prediction errors.
Extensive evaluations on four publicly available datasets and a
real-world button inspection dataset attest to the superior detection performance and efficiency of VarAD. In future research,
we aim to extend VarAD to simultaneous anomaly detection
across multiple categories and improve its image-level anomaly
detection performance.
REFERENCES
[1] G. Xie et al., “IM-IAD: Industrial image anomaly detection benchmark
in manufacturing,” IEEE Trans. Cybern., vol. 54, no. 5, pp. 2720–2733,
May 2024.
[2] Y. Cao, X. Xu, Z. Liu, and W. Shen, “Collaborative discrepancy optimization for reliable image anomaly localization,” IEEE Trans. Ind. Informat.,
vol. 19, no. 11, pp. 10674–10683, Nov. 2023.
[3] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler,
“Towards total recall in industrial anomaly detection,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit., 2022, pp. 14318–14328.
[4] P. Bergmann, K. Batzner, M. Fauser, D. Sattlegger, and C. Steger, “The
MVTec anomaly detection dataset: A comprehensive real-world dataset
for unsupervised anomaly detection,” Int. J. Comput. Vis., vol. 129, no. 4,
pp. 1038–1059, 2021.
[5] Y. Cao, Y. Zhang, and W. Shen, “High-resolution image anomaly detection
via spatiotemporal consistency incorporated knowledge distillation,” in
Proc. IEEE Int. Conf. Autom. Sci. Eng., 2023, pp. 1–6.
[6] H. Bai et al., “Vision datasets: A benchmark for vision-based industrial
inspection,” 2023, arXiv:2306.07890.
[7] H. Dong, Y. Zhang, H. Gu, N. Konz, Y. Zhang, and M. A. Mazurowski,
“SWSSL: Sliding window-based self-supervised learning for anomaly
detection in high-resolution images,” IEEE Trans. Med. Imag., vol. 42,
no. 12, pp. 3860–3870, Dec. 2023.
[8] H. Deng and X. Li, “Anomaly detection via reverse distillation from
one-class embedding,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2022, pp. 9737–9746.
[9] H. Yao et al., “Scalable industrial visual anomaly detection with partial
semantics aggregation vision transformer,” IEEE Trans. Instrum. Meas.,
vol. 73, 2024, Art. no. 5004217.
[10] J. Pirnay and K. Chai, “Inpainting transformer for anomaly detection,” in
Proc. Int. Conf. Image Anal. Process., 2022, pp. 394–406.

CAO et al.: VarAD: LIGHTWEIGHT HIGH-RESOLUTION IMAGE ANOMALY DETECTION VIA VISUAL AUTOREGRESSIVE MODELING

[11] J. OpenAI et al., “GPT-4 technical report,” 2024, arXiv:2303.08774.
[12] W. Luo, H. Yao, W. Yu, and Z. Li, “AMI-Net: Adaptive mask inpainting
network for industrial anomaly detection and localization,” IEEE Trans.
Autom. Sci. Eng., to be published, doi: 10.1109/TASE.2024.3368142.
[13] H. Yao, Y. Cao, W. Luo, W. Zhang, W. Yu, and W. Shen, “Prior normality
prompt transformer for multiclass industrial image anomaly detection,”
IEEE Trans. Ind. Informat., vol. 20, no. 10, pp. 11866–11876, Oct. 2024.
[14] H. Yao, W. Yu, W. Luo, Z. Qiang, D. Luo, and X. Zhang, “Learning
global-local correspondence with semantic bottleneck for logical anomaly
detection,” IEEE Trans. Circuits Syst. Video Technol., vol. 34, no. 5,
pp. 3589–3605, May 2024.
[15] M. Oquab et al., “DINOv2: Learning robust visual features without supervision,” Trans. Mach. Learn. Res., vol. 2024, 2024. [Online]. Available:
https://openreview.net/forum?id=a68SUt6zFt
[16] A. Gu and T. Dao, “Mamba: Linear-time sequence modeling with selective
state spaces,” in Proc. 1st Conf. Lang. Modeling, 2024. [Online]. Available:
https://openreview.net/forum?id=tEYskw1VY2
[17] Y. Cai, D. Liang, D. Luo, X. He, X. Yang, and X. Bai, “A discrepancy aware
framework for robust anomaly detection,” IEEE Trans. Ind. Informat.,
vol. 20, no. 3, pp. 3986–3995, Mar. 2024.
[18] Q. Wan, L. Gao, X. Li, and L. Wen, “Unsupervised image anomaly
detection and segmentation based on pretrained feature mapping,” IEEE
Trans. Ind. Informat., vol. 19, no. 3, pp. 2330–2339, Mar. 2023.
[19] Y. Cao, X. Xu, C. Sun, L. Gao, and W. Shen, “BiaS: Incorporating biased
knowledge to boost unsupervised image anomaly localization,” IEEE
Trans. Syst., Man, Cybern. Syst., vol. 54, no. 4, pp. 2342–2353, Apr. 2024.
[20] Q. Wan, L. Gao, X. Li, and L. Wen, “Industrial image anomaly localization
based on Gaussian clustering of pretrained feature,” IEEE Trans. Ind.
Electron., vol. 69, no. 6, pp. 6182–6192, Jun. 2022.
[21] Q. Chen, H. Luo, C. Lv, and Z. Zhang, “A unified anomaly synthesis strategy with gradient ascent for industrial anomaly detection and localization,”
in Proc. Comput. Vis.–ECCV 2024 – 18th Eur. Conf., (Lecture Notes in
Computer Science), Milan, Italy, vol. 15125, Sep. 29-Oct. 4, 2024, pp. 37–
54. [Online]. Available: https://doi.org/10.1007/978-3-031-72855-6_3
[22] Z. Liu, Y. Zhou, Y. Xu, and Z. Wang, “Simplenet: A simple network
for image anomaly detection and localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2023, pp. 20402–20411.
[23] J. Lei, X. Hu, Y. Wang, and D. Liu, “Pyramidflow: High-resolution
defect contrastive localization using pyramid normalizing flow,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2023, pp. 14143–14152.
[24] Y. Zhou, X. Xu, J. Song, F. Shen, and H. T. Shen, “Msflow:
Multiscale flow-based framework for unsupervised anomaly detection,” IEEE Trans. Neural Netw. Learn. Syst., to be published,
doi: 10.1109/TNNLS.2023.3344118.
[25] J. Wang et al., “Deep high-resolution representation learning for visual
recognition,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 43, no. 10,
pp. 3349–3364, Oct. 2021.
[26] Y. Liang, J. Zhang, S. Zhao, R. Wu, Y. Liu, and S. Pan, “Omni-frequency
channel-selection representations for unsupervised anomaly detection,”
IEEE Trans. Image Process., vol. 32, pp. 4327–4340, 2023.
[27] K. Batzner, L. Heckler, and R. König, “Efficientad: Accurate visual
anomaly detection at millisecond-level latencies,” in Proc. IEEE/CVF
Winter Conf. Appl. Comput. Vis., 2024, pp. 127–137.
[28] Y. Guo, M. Jiang, Q. Huang, Y. Cheng, and J. Gong, “MLDFR: A multilevel features restoration method based on damaged images for anomaly
detection and localization,” IEEE Trans. Ind. Informat., vol. 20, no. 2,
pp. 2477–2486, Feb. 2024.
[29] P. Esser, R. Rombach, and B. Ommer, “Taming transformers for highresolution image synthesis,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2021, pp. 12868–12878.
[30] Y. Bai et al., “Sequential modeling enables scalable learning for large
vision models,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2024, pp. 22861–22872.
[31] Y. Liu et al., “VMamba: Visual state space model,” in Proc. 38th
Annu. Conf. Neural Inf. Process. Syst., 2024. [Online]. Available: https:
//openreview.net/forum?id=ZgtLQQR1K7
[32] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, “Spot-the-difference
self-supervised pre-training for anomaly detection and segmentation,” in
Proc. Eur. Conf. Comput. Vis., 2022, pp. 392–408.
[33] P. Mishra, R. Verk, D. Fornasier, C. Piciarelli, and G. L. Foresti, “VTADL: A vision transformer network for image anomaly detection and
localization,” in Proc. IEEE Int. Symp. Ind. Electron., 2021, pp. 01–06.
[34] T. Aota, L. T. T. Tong, and T. Okatani, “Zero-shot versus many-shot:
Unsupervised texture anomaly detection,” in Proc. IEEE/CVF Winter
Conf. Appl. Comput. Vis., 2023, pp. 5553–5561.

3255

[35] E. J. Hu et al., “Lora: Low-rank adaptation of large language models,” in
Proc. Int. Conf. Learn. Representations, 2022, [Online]. Available: https:
//openreview.net/forum?id=nZeVKeeFYf9
[36] A. Dosovitskiy et al., “An image is worth 16x16 words: Transformers for
image recognition at scale,” in Proc. Int. Conf. Learn. Representations,
2021.
[37] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2022, pp. 16000–16009.
[38] A. Radford et al., “Learning transferable visual models from natural language supervision,” in Proc. Int. Conf. Mach. Learn., 2021, pp. 8748–8763.

Yunkang Cao (Graduate Student Member,
IEEE) received the B.S. degree in mechanical
design, manufacturing, and automation in 2020
from the Huazhong University of Science and
Technology, Wuhan, China, where he is currently working toward the Ph.D. degree in mechanical engineering.
His current research interests include machine vision, visual anomaly detection, and industrial foundation models.

Haiming Yao (Graduate Student Member,
IEEE) received the B.S. (Hons.) degree in measurement and control technology and instruments from the School of Mechanical Science
and Engineering, Huazhong University of Science and Technology, Wuhan, China, in 2022.
He is currently working toward the Ph.D. degree
in measurement and control technology and instruments with the Department of Precision Instrument, Tsinghua University, Beijing, China.
His research interests include visual anomaly
detection, deep learning, visual understanding, and artificial intelligence
for science.
Wei Luo (Student Member, IEEE) received the
B.S. degree in measurement and control technology and instruments from the School of Mechanical Science and Engineering, Huazhong
University of Science and Technology, Wuhan,
China, in 2023. He is currently working toward
the Ph.D. degree in measurement and control
technology and instruments with the Department of Precision Instrument, Tsinghua University, Beijing, China.
His research interests include deep learning,
anomaly detection, and machine vision.

Weiming Shen (Fellow, IEEE) received the
B.E. and M.S. degrees in mechanical engineering from Northern Jiaotong University, Beijing,
China, in 1983 and 1986, respectively, and the
Ph.D. degree in system control from the University of Technology of Compiegne, Compiegne,
France, in 1996.
He is currently a Professor with the Huazhong
University of Science and Technology (HUST),
Wuhan, China, and an Adjunct Professor with
the University of Western Ontario, London, ON,
Canada. Before joining HUST in 2019, he was a Principal Research
Officer with the National Research Council Canada. He is a Fellow
of Canadian Academy of Engineering and the Engineering Institute
of Canada. His work has been cited more than 16 000 times with an
h-index of 61. He authored or coauthored several books and more
than 560 articles in scientific journals and international conferences in
related areas. His research interests include agent-based collaboration
technologies and applications, collaborative intelligent manufacturing,
the Internet of Things, and big data analytics.
PAPER_TEXT
