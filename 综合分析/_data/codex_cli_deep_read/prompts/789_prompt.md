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
# [789] RGPKD: Reconstruction-Guided and Prompt-Enhanced Asymmetric Knowledge Distillation for Anomaly Detection
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
编号：789
题名：RGPKD: Reconstruction-Guided and Prompt-Enhanced Asymmetric Knowledge Distillation for Anomaly Detection
年份：2026
DOI：10.1109/tii.2026.3688668
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2026.3688668.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\789.txt
- 原始字符数：54335
- 本次发送字符数：54335
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

1

RGPKD: Reconstruction-Guided and
Prompt-Enhanced Asymmetric Knowledge
Distillation for Anomaly Detection
Kaiyue Wang , Chengyan Qin , Jieru Chi, Chenglizhao Chen, and Teng Yu

Abstract—Current anomaly detection methods based on
knowledge distillation typically adopt symmetric teacher–
student network architectures and perform anomaly detection by localizing feature discrepancies between the two
networks. However, the symmetric structure leads to insignificant feature differences in subtle anomalous regions,
which tends to cause missed detection in anomalous areas. In addition, due to upsampling operations during the
decoding process, the student network is prone to losing
detailed information, further compromising the quality of
feature reconstruction. Therefore, this article attempts to
integrate a novel prompt module into the classical knowledge distillation framework and redesigns the architecture
to dynamically inject rich detail information into the decoding process of the student network. Compared with existing
methods, the proposed approach significantly enhances
the fidelity of normal feature recovery and the salience
of anomalous feature discrepancies through explicit reconstruction constraints and a detail enhancement mechanism. Experimental results demonstrate that our method
achieves significant improvements over existing state-ofthe-art techniques.
Index Terms —Anomaly detection, knowledge distillation
(KD), prompt module, reconstruction guidance, unsupervised learning.

I. INTRODUCTION
NDUSTRIAL image anomaly detection spots surface defects
for quality control. Unsupervised methods, trained only on
normal samples, beat supervised ones since anomalies are rare
and labeling costs high [1], [2], [3].
Among unsupervised methods, knowledge distillation (KD) is
widely used—simple and effective. A pretrained teacher guides

I

Received 16 March 2026; accepted 24 April 2026. This work was
supported in part by the National Natural Science Foundation of China
(NNSFC) under Grant 62172229 and in part by the Natural Science
Foundation of Shandong Province, China under Grant ZR2021MF025.
Paper no. TII-26-2313. (Corresponding author: Teng Yu.)
Kaiyue Wang, Chengyan Qin, Jieru Chi, and Teng Yu are
with the College of Electronics and Information (Micro-Nano
Technology College), Qingdao University, Qingdao 266071, China
(e-mail:
2024020691@qdu.edu.cn;
2025020290@qdu.edu.cn;
chijieru@qdu.edu.cn; yuteng@qdu.edu.cn).
Chenglizhao Chen is with the College of Computer Science and Technology, China University of Petroleum, Qingdao 266580, China (e-mail:
chenglizhaochen@upc.edu.cn).
Data and code are available online at https://github.com/Cariaaaaaa/
RGPKD.
Digital Object Identifier 10.1109/TII.2026.3688668

a student to mimic its features on normal data. At test time,
anomalies cause the student to fail, creating feature discrepancies that localize defects (see Fig. 1). Unlike reconstruction
methods, KD avoids the reconstruction bottleneck and taps the
teacher’s generalization prior for stronger discrimination.
But mainstream KD has problems. First, symmetric architectures let students mimic teacher features too well on normal regions. On anomalies, the student’s normal-only training
creates tiny discrepancies, so defects are missed. Second, student decoders lose detail during upsampling, blurring anomaly
boundaries. Third, information flow for low-level details is
weak—skip connections are not enough.
We fix these with reconstruction-guided and prompt-based
knowledge distillation (RGPKD), using reconstruction for
self-supervised learning and teacher features as priors for detail
recovery.
Consequently, we design an asymmetric distillation framework tailored for reconstruction. The student aligns multiscale
teacher features and produces high-quality reconstructions under reconstruction guidance, learning accurate normal representations. A prompt module queries student encoder features to
retrieve similar templates from a teacher-based prompt bank,
fusing features bidirectionally. This injects teacher details into
the student decoder, bridging the detail gap. Our key contributions are as follows.
1) We propose the first asymmetric distillation framework
combining prompt modules with reconstruction guidance, strengthening the student’s learning of normal
patterns via reconstruction loss and enhancing feature
discrepancies for anomalies.
2) We introduce an efficient prompt module that improves
decoder detail recovery by matching and fusing features from the teacher’s repository, boosting boundary
precision in anomaly localization.
3) We demonstrate that our method generalizes to 3-D
anomaly detection using only RGB images, achieving
89.0% image-level AUROC (I-AUROC) on MVTec 3DAD and outperforming prior methods by a large margin
(+6.0% over CS-Flow).
II. RELATED WORK
A. Unsupervised Anomaly Detection
Unsupervised anomaly detection methods fall into two main
categories: reconstruction-based and feature embedding-based

1941-0050 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html
for more information.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

2

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

(a)

(b)

Fig. 1. Method pipeline of the proposed method. The main highlight of our method is the newly designed prompt module, which provides detailed
prompts before reconstructing features in student networks. The technical details are shown in Fig. 2. (a) Traditional symmetric KD framework
(baseline). (b) Proposed RGPKD framework(ours).

approaches [4], [5], [6]. Reconstruction-based methods [autoencoders, variational autoencoders (VAEs), and generative adversarial networks (GANs)] learn to reconstruct normal samples.
They flag anomalies by measuring reconstruction errors. But
they often struggle with complex textures, leading to false detections. Feature embedding methods assume normal features form
tight clusters. Deep SVDD pushes them into a compact hypersphere. Pretrained networks (ResNet) extract features and model
normal distributions using Gaussian methods. Recent work also
explores self-supervised learning, energy-based models [7], and
domain-specific techniques (for medical imaging) [7], [8], [9],
[10], [11], [12].

PatchCore [21]: it stores normal features and compares them
with test features during inference to find anomalies [22].
The catch? These approaches are passive. They only match
features at test time and do not guide the student during training. Newer techniques add attention mechanisms [23], but they
usually work at one scale and lack bidirectional learning.
But our prompt module is active—it actually retrieves
multiscale teacher features during training based on the student’s
query. It computes bidirectional affinity [see Equation (9)] to
capture fine-grained correspondences, then injects those features
at multiple decoder stages. So the student learns from teacher
details throughout training, not just at test time.

B. KD-Based Anomaly Detection
KD [13], [14] originally came from model compression,
but researchers adapted it for anomaly detection. The idea: a
student network learns normal patterns from a pretrained teacher.
Early methods used symmetric architectures, minimizing feature
differences between teacher and student [13]. Problem is that
symmetric structures often produce tiny feature differences in
anomalous regions—so you miss defects. Later, asymmetric
distillation frameworks emerged, like reverse distillation [15].
It uses a teacher encoder with a student decoder to create
asymmetry. That helps, but still has two issues: 1) it only aligns
features, with no pixel-level supervision and 2) the decoder loses
detail during upsampling, with no fix. Our RGPKD tackles both.
We add reconstruction guidance (pixel-level supervision) and a
prompt module that feeds teacher details into the decoder.
C. Feature Matching and Prompt Learning
Some methods use external memory modules or feature
banks to help detect anomalies [16], [17], [18], [19], [20]. Take

D. Summary
To sum up: existing methods either cannot create enough
feature discrepancy (symmetric distillation), lose detail (asymmetric without pixel supervision), or only match features at
inference (memory banks). Our RGPKD fixes all that. We combine an asymmetric U-Net student with reconstruction guidance
and an active, multiscale prompt module that retrieves and
fuses teacher features during training. Next section lays out the
framework.

III. METHOD
A. Overview of the Overall Framework
We propose RGPKD, fixing key issues in symmetric teacher–
student anomaly detection [15], [24], [25]. Fig. 2 shows three
parts: frozen teacher (T), trainable student (S), and a prompt
module linking them. Training uses only normal images I ∈
RH×W ×3 .

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

WANG et al.: RGPKD: RECONSTRUCTION-GUIDED AND PROMPT-ENHANCED ASYMMETRIC KNOWLEDGE DISTILLATION

Fig. 2.

Overall network architecture of our proposed.

3

external memory that complements the internal reconstruction
process. This design is therefore necessary to restore authentic
details and sharpen anomaly boundaries.
1) Base Loss: Specifically, in each training iteration, the
base loss of the model is composed of the losses between the
multiscale feature maps generated by the student decoder—S 5 ∈
R16×16×256 , S 6 ∈ R32×32×128 , and S 7 ∈ R64×64×64 —and the
corresponding scale feature maps from the teacher network—
T 1 ∈ R64×64×64 , T 2 ∈ R32×32×128 , and T 3 ∈ R16×16×256 . This
chapter employs the mean squared error (mse) loss to compute
the discrepancy between the feature maps from the teacher
network and the student decoder. We represent the feature loss
calculation as follows:
2

(1)
M l (Hl , Wl ) = T l (Hl , Wl )i,j − S l+4 (Hl , Wl )i,j
MSEl =

Lossbasic =

Hl
Wl 

1
M l (Hl , Wl )
Wl × Hl i=1 j=1
3


βl × MSEl , with βl ≥ 0.

(2)

(3)

l=1

Fig. 3.

Principle of UNet reconstruction guidance.

The teacher is ResNet18 pretrained on ImageNet for multiscale features [26]. The student is a U-Net encoder–decoder with
our Prompt Module [27].
During training, the student generates self-guided reconstruction maps, while the prompt module feeds teacher features into
the decoder to recover upsampling details. At inference, we spot
anomalies by comparing multiscale feature differences between
teacher and student decoder outputs.
B. U-Net Reconstruction Guidance
Reconstruction guidance uses the U-Net’s map to steer the student toward normal feature distributions, enforcing pixel-level
fidelity for interpretable learning (see Fig. 3). During training,
RGPKD takes anomaly-free images. The teacher extracts multiscale features: T 1 (64 × 64 × 64), T 2 (32 × 32 × 128), and T 3
(16 × 16 × 256). The student encoder outputs four features: S 1
(64 × 64 × 64), S 2 (32 × 32 × 128), S 3 (16 × 16 × 256), and
S 4 (8 × 8 × 512). S 4 goes to the decoder for reconstruction.
Using S 3 as a query, nearest neighbor features are retrieved
from the prompt bank and injected into the decoder (see
Section III-C). The decoder outputs S 5 (16 × 16 × 256), S 6
(32 × 32 × 128), and S 7 (64 × 64 × 64), and reconstructed Irec
(256 × 256 × 3).
Although the reconstruction loss enforces pixel-level fidelity,
upsampling operations in the decoder inevitably cause irreversible loss of high-frequency details (edges, fine textures).
This loss cannot be fully compensated by the pixelwise supervision alone, as demonstrated by the blurred boundaries. The
prompt module explicitly retrieves detail-rich features from the
teacher’s bank and injects them into the decoder, providing

Here, T l (Hl , Wl )i, j and S l+4 (Hl , Wl )i, j are feature vectors
at position (i, j) from teacher layer l and student layer l + 4;
Hl and Wl are feature map dimensions. Groups pair teacher
and student features of matching size, indexed by l ∈ [1, 2, 3].
MSEl denotes the mse loss for the lth teacher–student pair. βl
represents the weight assigned to the lth feature-map group; we
set βl = 1 for all l to give equal importance to each scale.
2) Reconstruction Loss: The model’s reconstruction loss is
computed between the input image I and its reconstruction Irec .
This work employs both mse and structural similarity index measure (SSIM) losses to balance pixelwise accuracy with structural
similarity, achieving a better equilibrium during reconstruction.
This loss combination effectively guides the UNet to learn more
accurate reconstructions while preserving image structure and
details, yielding higher quality outputs. We represent the mse
loss as follows:
W 
H

1
(I(H, W )i,j − Irec (H, W )i,j )2
Lossrm =
W × H i=1 j=1
(4)
where I(H, W )i,j and Irec (H, W )i,j denote the pixel vectors
at spatial position (i, j) from the input image I and the reconstructed image Irec , respectively; H and W denote the height and
width of the images. Lossrm represents the mse loss between I
and Irec .
We represent the SSIM loss as follows:
(2μI μIrec + C1 ) (2σIIrec + C2 )


Lossrs =  2
(5)
μI + μ2Irec + C1 σI2 + σI2rec + C2
where μI and μIrec denote the mean values of image I and
Irec , respectively; σI2 and σI2rec denote their variances; σIIrec
denotes their covariance; C1 and C2 are constants. Equation (5)
defines the SSIM similarity. In our implementation, the loss
term minimized in (6) is Lossrs = 1 − SSIM(I, Irec ), where
SSIM(I, Irec ) is computed, as shown in (5).
We represent the total reconstruction loss as follows:
Lossrec = Lossrm (I, Irec ) + Lossrs (I, Irec ).

(6)

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

4

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

Finally, the reconstruction loss Lossrec is expressed as the sum
of the two aforementioned losses between the input image I and
the reconstructed image Irec .
3) Total Loss: The total loss combines Lossbasic , Lossrm
(MSE), and Lossrs (SSIM) between I and Irec [see Equation (7)].
Loss = λ1 Lossbasic + λ2 Lossrm + λ3 Lossrs

(7)

where λ1 , λ2 , and λ3 are weighting hyperparameters that balance
the contributions of the base loss and the two reconstruction
losses. In our implementation, we set λ1 = λ2 = λ3 = 1.
Together, the three losses guide student feature learning
and reconstruction, improving anomaly detection accuracy and
robustness while maintaining image quality.
C. Prompt Module
During decoding, upsampling loses fine details, causing blurring on edges and textures. A prompt bank fixes this by feeding
multiscale features into the decoder for richer context and better
detail recovery [16].
1) Prompt Bank: The pretrained teacher guides the student (trained from scratch), providing rich features. The
prompt bank stores these multiscale normal features: P =
i
{A11 , . . . , Aik , . . . , AN
K } (Ak : kth layer feature from sample i).
For MVTec AD, we extract features from all training images
per category—N ranges from 60 (like Toothbrush) to 391 (Carpet). For MVTec 3D-AD, N runs from 70 to 300. Each sample
gives three feature maps: 64 × 64 × 64, 32 × 32 × 128, and
16 × 16 × 256. That is about 3.2 MB per sample (float32). Total
memory per category lands between 0.2 GB and 1.2 GB—fine
on a modern graphics processing unit (GPU).
2) Prompt Bank Matching Strategy: Given an input sample
IK ∈ R256×256×3 , the third-layer feature generated by the student network, S 3 ∈ R16×16×256 , is used as a query to find the
most similar nearest neighbor feature in the prompt bank. We
formulate the process as follows:
 

(8)
d S3 ,Ai3
f = argmin
C⊂1,...,N i∈C

where d(·) denotes the cosine similarity between the input
feature query S 3 and the template feature key A3i ; C denotes the
set of candidate feature indices, which in our implementation is
the full set of indices in the prompt bank, i.e., C = {1, 2, . . . , N }
where N is the number of stored templates. We perform an
exhaustive nearest neighbor search over all templates because
N is at most a few hundred per category, which is computationally efficient during training. f denotes the retrieved nearest
neighbor feature. The multiscale feature group corresponding
to f is denoted as F = {F 1 , F 2 , F 3 }, where F 1 ∈ R64×64×64 ,
F 2 ∈ R32×32×128 , and F 3 ∈ R16×16×256 .
We deliberately use the intermediate student feature S 3
(stride 16) as the query. Higher resolution features (e.g.,
S 1 and S 2 ) contain fine details but are more sensitive to local texture variations, which may introduce noisy matches;
lower resolution features (S 4 ) are too abstract to retain spatial
specificity. S 3 strikes a balance between semantics and spatial
resolution, yielding robust retrieval.
To recover S 5 , we compute relationships between upsampled
4
S (64 × 64 × 64) and prompt feature F 1 (64 × 64 × 64). Let

rSi4 →Fj1 be the affinity between feature points i and j, defined
as dot-product in an embedding space [17]. Moreover, since the
teacher and student share the same pretraining domain, their
feature spaces are roughly aligned; thus a simple global nearest
neighbor with cosine distance suffices—complex mechanisms,
such as deformable attention, are unnecessary and introduce
excessive overhead. This choice is also validated by the ablation
study in Section IV-E4, where we show that advanced matching
mechanisms yield marginal gains at significantly higher computational cost. We represent this relationship as follows:
 T  
(9)
rSi4 →Fj1 =θ Si4 φ Fj1
where θ and φ are two embedding functions implemented via
1 × 1 spatial convolutional layers. Similarly, the affinity from
the jth feature point of the prompt feature to the ith feature
point of the input feature, denoted as rFj1 →Si4 , can be obtained
in the same manner.
The bidirectional relationship between input and template points is (rS i →F j , rF j →S i ). The relational matrix R ∈
1
1
4
4
Rm×m captures all pairwise affinities. For input point i, ri =
1
1
, rF1,...,n
[rSi4 →F1,...,n
→Si4 ] [17]—first half treats input as query,
second half reverses roles. These relational features guide recovery [see Fig. 4(a)].
Here is how the prompt module works [see Fig. 4(b)]: Input
and template features are projected, concatenated with relational
features, and fused via 1 × 1 convolutions. This fused feature
enters the decoder to produce S 5 , then upsampled to 32 ×
32 × 128. Pairwise relations between F 2 and S 5 generate the
next fused feature for S 6 . Repeating yields S 7 (64 × 64 × 64).
This matching strategy boosts feature recovery and downstream
detection.
D. Anomaly Scoring
During inference, test image J ∈ R256×256×3 passes through
the teacher–student network. Teacher outputs T 1 (64 × 64 ×
64), T 2 (32 × 32 × 128), and T 3 (16 × 16 × 256). Student outputs S 5 (16 × 16 × 256), S 6 (32 × 32 × 128), and S 7 (64 ×
64 × 64). We localize anomalies by comparing multiscale
features. Teacher and student features of matching scales
form groups (l ∈ [1, 2, 3]). For each group, T l (Hl , Wl )i,j and
S l+4 (Hl , Wl )i,j are feature vectors at position (i, j), and an
anomaly score map is computed. Note that the student decoder
outputs features indexed from 5 to 7 (S 5 , S 6 , and S 7 ), corresponding to the teacher’s layers T 1 , T 2 , and T 3 , respectively.
Hence, we use l + 4 to align the layers: l = 1 matches S 5 , l = 2
matches S 6 , and l = 3 matches S 7 . The feature vectors are first
normalized by their L2-norms, and then the anomaly score map
for each group is calculated. We represent the computation as
follows:
l

T (Hl , Wl )i,j
Tl (J)i,j = l
|T (Hl , Wl )i,j |

(10)

l+4

S (Hl , Wl )i,j
Sl+4 (J)i,j = l+4
|S (Hl , Wl )i,j |

2
Ωl (J)i,j = Tl (J)i,j − Sl+4 (J)i,j

(11)
(12)

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

WANG et al.: RGPKD: RECONSTRUCTION-GUIDED AND PROMPT-ENHANCED ASYMMETRIC KNOWLEDGE DISTILLATION

(a)

5

(b)
(c)

Fig. 4. Principle of the prompt module. (a) Correspondence calculation. (b) Feature prompt engineering. (c) Prompt feature matching and fusion
strategy.

where Ωl (J)i,j denotes the anomaly score at position (i, j) for
the ith feature-map group. Considering that different feature
layers have different spatial resolutions, a multiscale fusion
strategy is adopted to merge the anomaly maps. First, each
layer’s anomaly score map Ωl (J) is upsampled via bilinear
interpolation to a unified resolution of [256, 256]. Then, the three
resized anomaly maps are summed to obtain Ω(J), we represent
the final anomaly map by summing the three upsampled anomaly
maps as follows:
Ω(J)=

3




Upsample Ωl (J) .

(13)

l=1

To suppress noise in the anomaly score map Ω(J), a Gaussian
filter with a kernel size of k × k (k = 11) is applied for smoothing, which helps eliminate isolated noisy points. The smoothed
map is then normalized to [0, 1] via min–max scaling across
the entire map. Finally, for visualization purposes only, a fixed
threshold τ = 0.5 is applied to obtain a binary segmentation
mask. We emphasize that all quantitative evaluations [pixel-level

AUROC (P-AUROC) and PRO] are performed on the continuous anomaly scores without binarization, following standard
practice [28].
To obtain a binary segmentation mask for visualization, the
anomaly map Ω(J) is first normalized to [0, 1] via min–max
scaling across the whole map. A fixed threshold τ = 0.5 is then
applied to produce the binary mask. Note that for quantitative
evaluation (P-AUROC and PRO), we directly use the continuous
anomaly scores without binarization, following standard practice [28], [29]. The threshold τ is kept constant for all categories
and images; no per-image or per-class calibration is performed
to ensure fair comparison.
IV. EXPERIMENTS
A. Experimental Datasets
We evaluate RGPKD on MVTec AD and MVTec 3D-AD—
standard benchmarks with diverse defects, pixel-level masks,
and broad adoption for fair comparison.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

6

Fig. 5. Example of MVTec AD dataset. Among them, (a) and (d)
are normal images, (b) and (e) are abnormal images, (c) and (f) are
corresponding ground truth.

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

Image-level AUROC (I-AUROC) measures whole-image
classification for initial screening. Pixel-level AUROC (PAUROC) assesses localization accuracy by comparing pixel
probabilities to ground truth. Since P-AUROC may stay high
even with incomplete anomaly coverage, we add per-region
overlap (PRO), which averages overlap between predicted and
true regions—crucial for continuous defects such as scratches.
Together, I-AUROC, P-AUROC, and PRO provide a 3-D
assessment: overall discriminability, pixel accuracy, and region
completeness.
D. Comparative Experiment

Fig. 6. Example of MVTec 3D-AD dataset. Among them, (a) and (d)
are normal images, (b) and (e) are abnormal images, (c) and (f) are
corresponding ground truth.

MVTec AD [28] is the leading 2-D benchmark: 15 categories
(five textures, ten objects), 5354 high-res images (1024 × 1024),
pixelwise masks, and challenging defects, such as scratches and
dents (see Fig. 5). Training uses only normal samples.
MVTec 3D-AD [30] adds 3-D: 4137 scans across ten objects
(see Fig. 6). We use only its RGB images to test whether RGPKD infers 3-D structural anomalies from 2-D projections—a
practical setup using accessible cameras, not costly 3-D sensors.
This checks if the method implicitly captures 3-D patterns for
real-world inspection.
B. Experimental Environment
Experiments ran on an NVIDIA RTX 3090 Ti (24 GB), Intel
i7-12700KF, 64 GB RAM, with Python 3.8, PyTorch 1.11.0,
CUDA 11.3, and cuDNN 8.2. We followed the unsupervised
protocol. Teacher: fixed ResNet-18 pretrained on ImageNet1 k. Student: standard four-block U-Net with skip connections.
Prompt module integrated at decoder levels S5–S7.
Input images were resized to 256 × 256 and normalized. A
separate model was trained per category on MVTec AD. Training used a batch size of 32 and an stochastic gradient descent
(SGD) optimizer (momentum 0.9, weight decay 1e4). The initial
learning rate was 0.001, scheduled via Cosine Annealing, for 800
epochs. Loss weights were set as in the text (λ1 = λ2 = λ3 = 1).
During inference, multiscale discrepancy maps are fused directly into the final anomaly map. Only lightweight postprocessing (Gaussian smoothing and min–max normalization) is
applied before visualization; no additional refinement modules
are used.
C. Evaluation Metrics
We evaluate RGPKD on three levels: detection, identification,
and localization.

As Table I shows, RGPKD achieves 99.8% overall AUROC,
outperforming CS-Flow (98.7%) and MSTUnet (99.1%). It
performs strongly on both textures and objects.
On textures, it hits 100% on Grid, Leather, Tile, and averages
99.9%—slightly above CS-Flow (99.8%). On objects, it scores
100% on five categories and excels on hard ones: Capsule
(99.6%, +1.8 over MSTUnet) and Screw (99.0%, +2.0 over RD).
The asymmetric design and reconstruction guidance boost both
global and local anomaly detection.
We further compare with SimpleNet [25], a nondistillation
method that achieves state-of-the-art (SOTA) by feature adaptation and Gaussian density estimation. To ensure fairness, we reevaluate SimpleNet under exactly the same protocol (ResNet18,
256 × 256, 800 epochs) using its official code. RGPKD surpasses SimpleNet by +0.6% overall I-AUROC (99.8% versus
99.2%), with particularly notable gains on challenging object
categories, such as Capsule (+2.1%) and Screw (+1.8%). This
demonstrates that distillation-based approaches, when properly
enhanced with reconstruction guidance and prompting, can still
outperform the latest feature-modeling paradigms.
At pixel level (see Table II), RGPKD excels. On textures, pixel
AUROC averages 98.4% (+0.7 versus RD) and PRO 95.5%—
near CS-Flow (95.7%) but more stable due to prompt detail
restoration. On objects, it hits 98.9% pixel AUROC on Transistor
(+6.4 versus RD) and PRO 87.6%, leading clearly. Capsule
shows 98.8% pixel AUROC but 88.3% PRO, leaving room for
finer detail recovery. Overall, RGPKD achieves 98.3% pixel
AUROC and 94.4% PRO across MVTec AD, outperforming
all methods. This confirms reconstruction guidance and prompt
module effectiveness for robust anomaly localization.
In Fig. 7(b) and (c), RGPKD’s anomaly map aligns closely
with ground truth, outperforming other methods. Its heatmap,
as shown in Fig. 7(d), precisely highlights anomaly cores with
minimal noise.
Fig. 8 plots pixel AUROC versus PRO across 15 categories. Most points cluster in high-performance regions (AUROC >98%, PRO >94%). Capsule and Transistor show high
AUROC (98.8%, 98.9%) but lower PRO (88.3%, 87.6%), likely
due to tiny defects. Textures, such as Carpet, Grid, and Leather,
excel on both (PRO >97%, AUROC >99%), confirming
robustness.
Fig. 9 compares mean pixel AUROC on textures versus objects. Most methods show bias (CSFlow: 98.7% texture, 97.5%
object). RGPKD achieves top-tier on both (98.4% texture, 98.6%
object), surpassing second-best on objects by 0.1% and trailing
CS-Flow on textures by only 0.3%.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

WANG et al.: RGPKD: RECONSTRUCTION-GUIDED AND PROMPT-ENHANCED ASYMMETRIC KNOWLEDGE DISTILLATION

7

TABLE I
DETECTION RESULTS OF I-AUROC(%) ANOMALY ON THE MVTEC AD DATASET

TABLE II
DETECTION RESULTS OF P-AUROC(%) AND PRO(%) ANOMALY ON THE MVTEC AD DATASET

TABLE III
DETECTION RESULTS OF I-AUROC(%) ANOMALY ON THE MVTEC 3D-AD DATASET

These results validate RGPKD’s design: prompt module injects texture details for defect discrimination, while asymmetric
architecture and reconstruction loss improve object anomaly
capture.

Table III compares RGPKD with five SOTA methods on
MVTec 3D-AD RGB. RGPKD achieves 89.0% I-AUROC, outperforming ATSN (86.9%) by 2.1 points and CS-Flow (83.0%)
by six points, with over 12-point gains against PatchCore and
PaDiM.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

8

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

Fig. 7. Visualization example of RGPKD on the MVTec AD dataset.
(a) Original image. (b) Real anomaly annotation diagram. (c) Predicted
anomaly localization map. (d) Original image after heatmap overlay.

Fig. 11. Qualitative examples on MVTec 3D-AD RGB images for categories with prominent 3-D structural anomalies. From top to bottom:
input RGB image, input 3-D image, ground-truth anomaly mask, and
RGPDK predicted anomaly heatmap. The model accurately localizes
volumetric defects, demonstrating its implicit capability to perceive 3-D
structure from 2-D projections.

Fig. 12.

Fig. 8. Scatter plot of P-AUROC versus PRO for RGPKD across categories.

Fig. 9.

Average AUROC Bar Chart.

Fig. 10.

Generalization Comparison on MVTec 3D-AD.

Experimental results under different weight parameters.

Per category, RGPKD excels on complex objects: Cookie
hits 99.8% AUROC (versus ATSN 78.5%, CS-Flow 79.5%),
showing high sensitivity to subtle surface pits. Tire reaches
94.5% (+10.7 versus ATSN), indicating strong detection of
3-D distortions. Bagel, Cable_Gland, and Carrot consistently
exceed 90%. Performance dips on Peach and Potato, likely due
to low-contrast color or fine texture changes requiring better
detail discrimination—a future direction.
Overall, RGPKD’s asymmetric prompt and reconstruction
guidance effectively capture 3-D spatial differences, jointly
modeling surface and structure. It maintains 2-D texture detection while enhancing 3-D shape sensitivity, confirming robustness for complex material inspection.
To assess whether RGPDK can infer 3-D structural anomalies
solely from 2-D RGB projections—a practical and low-cost
setting—we evaluate on the RGB images of MVTec 3D-AD.
This task is not full 3-D anomaly detection, but rather tests the
model’s cross-dimensional generalization: the ability to capture
3D-related patterns (dents, bulges, and twists) through their 2-D
manifestations.
Fig. 11 provides qualitative examples on categories with
prominent 3-D deformations. For Tire, the ground-truth anomaly
is a volumetric bulge; our model highlights exactly the bulging
region from the 2-D image, leveraging shading and contour distortion cues. On Cookie, subtle surface pits are accurately localized despite their small 3-D depth. These visualizations confirm
that RGPDK implicitly learns structural-aware representations
through the prompt module and reconstruction guidance, bridging the 2D–3D gap without requiring explicit depth input.
Fig. 10 compares RGPKD, AST, and CSFlow on MVTec
3D-AD RGB. RGPKD averages 89.0% AUROC, excelling

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

WANG et al.: RGPKD: RECONSTRUCTION-GUIDED AND PROMPT-ENHANCED ASYMMETRIC KNOWLEDGE DISTILLATION

9

TABLE VI
ABLATION EXPERIMENT RESULTS OF THE PROMPT MODULE

Fig. 13. Qualitative comparison of reconstruction and anomaly localization with and without the prompt module. The prompt module significantly sharpens edges and recovers fine defect fragments (see red
boxes).
TABLE IV
RESULTS OF ABLATION EXPERIMENTS ON UNET ARCHITECTURE AND
RECONSTRUCTED IMAGES

TABLE V
RESULTS OF ABLATION EXPERIMENTS ON NETWORK ARCHITECTURE AND
RECONSTRUCTED IMAGES

on Cookie (99.8%, +21.3 versus AST) and Tire (94.5%,
+20 versus CSFlow). The prompt module fuses multiscale
teacher features to boost sensitivity, while reconstruction
loss enforces local consistency. Strong results on Bagel and
Cable_Gland confirm consistent effectiveness. This demonstrates robust cross-dimensional generalization for complex
industrial inspection.
E. Ablation Experiment
1) Network Structure and Reconstruction Guidance:

Table IV ablates the asymmetric student and reconstruction
guidance. Adding a decoder boosts I-AUROC from 91.4% to
95.7%, showing symmetric structures limit performance. A full
U-Net forces the student to recover multiscale teacher features
from a bottleneck, amplifying anomaly deviations.
Adding reconstruction guidance pushes I-AUROC to 97.9%.
The loss constrains the student to both match abstract features
and accurately reconstruct inputs, forcing it to capture global
and local details.
Pixel-level gains are smaller: P-AUROC moves from 96.6%
(encoder only) to 96.7% (decoder only), reaching 97.7% with
guidance. This indicates asymmetry and guidance mainly
boost macro discrimination; precise localization needs detail
recovery—hence our prompt module.
Second, ablation in Table V validates the necessity of
the asymmetric architecture and reconstruction guidance. The

initial “encoder-only alignment” suffers from indistinct feature differences due to symmetry. Adding a decoder (symmetric U-Net) forces deeper normal pattern learning for multiscale recovery, producing clearer anomaly deviations and
the first performance leap. Comparing “RGPDK w/o Prompt”
and “Full RGPDK” in Table V, the prompt module brings a
significant improvement of +1.5% I-AUROC. The qualitative
comparison in Fig. 13 further shows that without prompting, the reconstructed image exhibits noticeable blur around
defect contours, and the anomaly map tends to miss small
fragments. After adding the prompt module, both the reconstruction fidelity and the anomaly localization integrity are
markedly enhanced. This confirms that the reconstruction guidance alone, even under an asymmetric architecture, is insufficient for fine-grained detail recovery—the prompt module is
indispensable.
The full model with prompt module delivers top-tier performance. The gain is subtle but crucial—it solves the bottleneck
of detail loss in decoding by retrieving teacher priors to bridge
the gap with authentic details.
2) Prompt Module: Table VI ablates prompt module placement across decoder levels. Single-level embedding at any stage
(S5, S6, and S7) improves performance, with S6 yielding the
largest gain—mid-level features best balance semantics and
spatial detail. Multilevel embedding outperforms all single-layer
variants, showing multiscale fusion is necessary to catch both
subtle texture flaws (high-level) and structural distortions (lowlevel). Full embedding at S5, S6, and S7 creates a coherent
detail pathway, achieving peak I-AUROC of 99.4%, confirming that multiscale collaboration systematically enhances detail
recovery.
3) Weight Parameters: The total loss in (7) involves three
hyperparameters λ1 , λ2 , and λ3 , which balance feature alignment
(Lossbasic ), pixelwise mse reconstruction (Lossrm ), and SSIM
reconstruction (Lossrs ). By default, we set λ1 = λ2 = λ3 = 1,
treating each supervision signal equally. To investigate the sensitivity of these weights, we conduct a series of ablation experiments on the MVTec AD dataset (averaged over all categories),
and the experimental results under different weight parameters
are shown in Fig. 12.
First, we vary λ1 while fixing λ2 = λ3 = 1. Table VII reports
the I-AUROC, P-AUROC, and PRO for different λ1 values.
Performance peaks at λ1 = 1 and degrades when λ1 deviates
too far from this balance. When λ1 is too small (< 0.5), the
model relies mainly on reconstruction losses and loses the
discriminative power from feature alignment; when λ1 is too
large (> 2), the reconstruction quality deteriorates, harming
localization accuracy.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

10

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

TABLE VII
SENSITIVITY ANALYSIS OF λ1 ON MVTEC AD

TABLE IX
COMPARISON OF PER-CATEGORY TRAINING AND MIXED-CATEGORY
TRAINING ON MVTEC AD TEXTURE CLASSES

TABLE VIII
COMPARISON OF DIFFERENT MATCHING MECHANISMS

TABLE X
ABLATION STUDY ON THE PROMPT SIZE N ON THE CAPSULE CATEGORY OF
MVTEC AD

We further examine the effect of λ2 and λ3 individually (by
varying one while keeping the others at 1). Both exhibit a
similar trend: the best performance is achieved at the default
value of 1, and performance drops gradually when the weight
moves away from 1. For brevity, we omit the full tables. This
confirms that equal weighting provides an optimal balance
among the three complementary objectives. Therefore, we adopt
λ1 = λ2 = λ3 = 1 for all experiments without additional tuning,
which also demonstrates the robustness of our method across
categories.
4) Matching Mechanism: To justify our design choice of
using a simple cosine nearest neighbor retrieval in the prompt
module, we compare it against two more advanced matching
mechanisms: deformable attention [36] and cross-attention [37].
Each mechanism is integrated into the prompt module exactly as
described in Section III-C, while keeping all other components
unchanged. We evaluate the performance on MVTec AD in
terms of I-AUROC, as well as model complexity (number of
parameters) and inference speed (milliseconds per image). The
results are reported in Table VIII.
As shown in Table VIII, our simple cosine nearest neighbor retrieval achieves the same top-level detection accuracy
(99.4% I-AUROC) as the more complex deformable attention,
and slightly outperforms cross-attention. However, it does so
with considerably lower computational overhead: our method
reduces the parameter count by 19% (11.5 versus 14.2 M) and
speeds up inference by 35% (18.3 versus 28.5 ms) compared
to deformable attention. This is because our retrieval avoids
expensive attention computation and directly operates on prealigned feature spaces. The results confirm that a lightweight
retrieval mechanism is sufficient for our prompt module, and
the extra complexity of advanced attention is unnecessary for
this task.
Furthermore, we ablate the number of retrieved neighbors in
our cosine search. Using a single nearest neighbor already yields
the best performance; averaging multiple neighbors slightly
degrades the results (I-AUROC drops to 99.2%), likely due to

template blending that smooths out fine details. This indicates
that the teacher feature bank is sufficiently representative and
that our retrieval is robust to noise without requiring sophisticated aggregation.
5) Cross-category Training: Although the standard protocol
on MVTec AD trains a separate model Per-category, we
additionally investigate whether RGPDK can generalize when
trained on mixed-categories. We select all five texture classes
(Carpet, Grid, Leather, Tile, and Wood) and train a single model
on their combined training sets. The model is then evaluated
individually on each texture class. As shown in Table IX, the
mixed-training model achieves an average IAUROC of 98.7%,
which is 1.2% lower than the per-category models (99.9%).
The performance drop is more pronounced on classes with
distinct visual patterns (Tile drops from 100% to 97.5%). This
confirms that per-category training is necessary to capture
class-specific normal patterns, as the student network cannot
simultaneously fit all texture variations without sacrificing
precision. In industrial scenarios, where each production line
manufactures a single product, per-category training is the
natural and most effective choice.
6) Sensitivity to Prompt Size N : We investigate how the
number of stored templates affects performance by randomly
subsampling the training set to construct prompt banks of different sizes. Experiments are conducted on the Capsule category,
which has a medium-sized training set (119 images). As shown
in Table X, increasing N from 10 to the full set consistently
improves both I-AUROC and PRO, with diminishing returns
after N = 50. The full bank achieves the best result, indicating
that retaining all normal samples is beneficial for capturing
diverse normal patterns. Even with N = 10, the method still
outperforms many baselines (I-AUROC 98.5%), demonstrating
robustness to prompt reduction.
7) Runtime Analysis: We evaluate the inference speed of
RGPDK on the MVTec AD dataset (Carpet category, 391

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

WANG et al.: RGPKD: RECONSTRUCTION-GUIDED AND PROMPT-ENHANCED ASYMMETRIC KNOWLEDGE DISTILLATION

TABLE XI
INFERENCE TIME BREAKDOWN ON MVTEC AD (CARPET CATEGORY, IMAGE
SIZE 256 × 256)

TABLE XII
COMPARISON OF DIFFERENT DISTANCE METRICS FOR ANOMALY SCORING
[SEE EQUATION (12)] ON MVTEC AD

11

V. CONCLUSION
This article proposes RGPKD, a KD framework with reconstruction guidance and a prompt module for unsupervised
industrial anomaly detection. To overcome limited feature discrepancy in student networks and detail loss during decoding
within symmetric distillation structures, we incorporate a reconstruction loss as a strong self-supervised signal and design a
prompt module that retrieves and fuses details from the teacher’s
feature bank. This improves the student’s representation of
normal features and amplifies its deviation under anomalies.
Extensive experiments on benchmarks like MVTec AD show
that RGPKD achieves state-of-the-art performance in detection
and localization. Future work will investigate more efficient
prompt library strategies and extend the framework to domains
like video anomaly detection.
REFERENCES

templates) using an NVIDIA RTX 3090 Ti GPU. Table XI
reports the retrieval time, total inference time (including feature
extraction, retrieval, and anomaly scoring), and the corresponding frames per second (FPS).
The prompt module retrieves the nearest neighbor from the
bank in only 2.3 ms per image, thanks to the small bank size
(at most a few hundred templates) and efficient cosine similarity
computation. The total inference time is 15.7 ms, achieving 63.7
FPS, which comfortably exceeds the real-time requirement (30
FPS) for industrial inspection.
Compared with state-of-the-art distillation methods, RGPDK
is slightly slower than RD (81.3 FPS) and RD++ (76.3 FPS)
due to the additional retrieval step, but it still outperforms
CS-Flow (54.1 FPS) in speed. The marginal overhead of 2.3 ms
is a worthwhile tradeoff for the significant gains in detection
and localization accuracy (see Tables I–III). These results confirm that RGPDK is both effective and efficient for practical
deployment.
8) Impact of Distance Metrics for Anomaly Scoring: Equation (12) computes the anomaly score using the squared L2
distance between normalized teacher and student features. To
investigate whether other distance or similarity measures could
be more effective, we replace the squared L2 with three alternatives: cosine distance (1 − cos(T̂ , Ŝ)), L1 distance, and dot
product (without normalization). All other components of the
framework remain unchanged.
Table XII reports the results on MVTec AD. The squared
L2 distance achieves the highest performance across all metrics
(I-AUROC 99.8%, P-AUROC 98.3%, and PRO 94.4%). Cosine
distance performs similarly (99.7%, 98.2%, and 94.2%), which
is expected since cosine distance is closely related to squared
L2 on normalized vectors. L1 distance yields slightly lower
scores, especially in PRO (93.6%), indicating that it is less
sensitive to small but critical discrepancies. Dot product, which
omits normalization, performs the worst (98.9%, 96.8%, and
91.2%), confirming that normalization is essential to suppress
scale variations. These results justify our choice of squared L2
in (12).

[1] R. Wang, K. Nie, T. Wang, Y. Yang, and B. Long, “Deep learning for
anomaly detection,” in Proc. 13th ACM Int. Conf. Web Search Data Mining,
2020, pp. 894–896.
[2] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for anomaly
detection: A review,” ACM Comput. Surv., vol. 54, no. 2, pp. 1–38, 2022.
[3] L. Ruff et al., “A unifying review of deep and shallow anomaly detection,”
Proc. IEEE, vol. 109, no. 5, pp. 756–795, May 2021.
[4] C. Ding, G. Pang, and C. Shen, “Catching both gray and black swans:
Open-set supervised anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., pp. 7388–7398, 2022.
[5] K. Jang, K. E. S. Pilario, N. Lee, I. Moon, and J. Na, “Explainable artificial
intelligence for fault diagnosis of industrial processes,” IEEE Trans. Ind.
Informat., vol. 21, no. 1, pp. 4–11, Jan. 2025.
[6] Y. Qiang, J. Cao, S. Zhou, J. Yang, L. Yu, and B. Liu, “tGARD: Text-guided
adversarial reconstruction for industrial anomaly detection,” IEEE Trans.
Ind. Informat., vol. 21, no. 12, pp. 9297–9308, Dec. 2025.
[7] S. Yoon, Y.-U. Jin, Y.-K. Noh, and F. C. Park, “Energy-based models for
anomaly detection: A manifold diffusion recovery approach,” in Proc. 37th
Int. Conf. Neural Inf. Process. Syst., pp. 49445–49466, 2023.
[8] X. Shen, X. Ge, and W. Wang, “Unsupervised anomaly detection for
medical images based on multi-hierarchical feature reconstruction,” IEEE
Access, vol. 12, pp. 151395–151402, 2024.
[9] H. H. Nguyen, C. N. Nguyen, X. T. Dao, Q. T. Duong, D. P. Thi Kim,
and M.-T. Pham, “Variational autoencoder for anomaly detection: A
comparative study,” in Proc. IEEE Int. Conf. Consum. Electron., 2024,
pp. 1–6, doi: 10.1109/ICCE56470.2024.10427761.
[10] G. Pang, A. J. Van Den Hengel, C. Shen, and L. Cao, “Toward deep
supervised anomaly detection: Reinforcement learning from partially
labeled anomaly data,” in Proc. Knowl. Discov. Data Mining, 2020,
pp. 1298–1308.
[11] J. Yang, Y. Shi, and Z. Qi, “DFR: Deep feature reconstruction for unsupervised anomaly segmentation,” 2020, arXiv:2012.07122.
[12] P. Perera, R. Nallapati, and B. Xiang, “OCGAN: One-class novelty detection using GANs with constrained latent representations,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2019,
pp. 2893–2901.
[13] G. Hinton, O. Vinyals, and J. Dean, “Distilling the knowledge in a neural
network,” Comput. Sci., vol. 14, no. 7, pp. 38–39, 2015.
[14] C. Peng, Y. Sheng, W. Gui, Z. Tang, and C. Li, “A rolling bearing fault
diagnosis method based on multimodal knowledge graph,” IEEE Trans.
Ind. Informat., vol. 20, no. 11, pp. 13047–13057, Nov. 2024.
[15] H. Deng and X. Li, “Anomaly detection via reverse distillation from
one-class embedding,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2022, pp. 9737–9746.
[16] Y. Lim et al., “Few-shot semantic segmentation with uncertainty-based
joint prototypes,” in Proc. IEEE Int. Conf. Adv. Video Signal-Based
Surveill., 2025, pp. 1–6.
[17] X. Wang, R. Zhang, C. Shen, T. Kong, and L. Li, “Dense contrastive
learning for self-supervised visual pre-training,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2021, pp. 3024–3033.
[18] C. Huang et al., “Registration based few-shot anomaly detection,” in Proc.
Eur. Conf. Comput. Vis., 2022, pp. 303–3019.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

12

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

[19] H. Cheng, J. Luo, and X. Zhang, “Multimodal industrial anomaly detection via uni-modal and cross-modal fusion,” IEEE Trans. Ind. Informat.,
vol. 21, no. 6, pp. 5000–5010, Jun. 2025.
[20] T. Park, A. A. Efros, R. Zhang, and J.Yan Zhu, “Contrastive learning for
unpaired image-to-image translation,” in Proc. Eur. Conf. Comput. Vis.,
2020, pp. 319–315.
[21] J. Yi and S. Yoon, “Patch SVDD: Patch-level SVDD for anomaly detection
and segmentation,” in Proc. Asian Conf. Comput. Vis., 2020, pp. 475–489.
[22] H. Guo, C. Zhao, Z. Liu, J. Wang, and H. Lu, “Learning coarse-to-fine
structured feature embedding for vehicle re-identification,” in Proc. AAAI
Conf. Artif. Intell., 2018, pp. 6960–6967.
[23] Y. Jiang, Y. Cao, and W. Shen, “Prototypical learning guided context-aware
segmentation network for few-shot anomaly detection. neural networks
and learning systems,” IEEE Trans. Neural Netw. Learn. Syst., vol. 36,
no. 7, pp. 12016–12026, Jul. 2025.
[24] K. Roth, L. Pemula, J. Zepeda, B. Schlkopf, and P. Gehler, “Towards total
recall in industrial anomaly detection,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit., 2021, pp. 14318–14328.
[25] Z. Liu, Y. Zhou, Y. Xu, and Z. Wang, “SimpleNet: A simple network
for image anomaly detection and localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2023, pp. 20402–20411.
[26] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, “A simple framework
for contrastive learning of visual representations,” in Proc. 37th Int. Conf.
Mach. Learn., 2020, pp. 1597–1607.
[27] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum
contrast for unsupervised visual representation learning,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2020, pp. 9729–9738,
doi: 10.1109/CVPR42600.2020.00975.
[28] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec AD—
A comprehensive real-world dataset for unsupervised anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2019,
pp. 9592–9600.
[29] L. Ruff, R. Vandermeulen, N. Görnitz, L. Deecke, and M. Kloft,
“Deep one-class classification,” in Proc. Int. Conf. Mach. Learn., 2018,
pp. 4393–4402.
[30] P. Bergmann, X. Jin, D. Sattlegger, and C. Steger, “The MVTec 3D-AD
dataset for unsupervised 3D anomaly detection and localization,” in Proc.
17th Int. Joint Conf. Comput. Vis., Imag. Comput. Graph. Theory Appl.,
2022, pp. 202–213.
[31] S. Lee, S. Lee, and Byung Cheol Song, “CFA: Coupled-hypersphere-based
feature adaptation for target-oriented anomaly localization,” IEEE Access,
vo. 10, pp. 78446–78454, 2022.
[32] S. Zhang, X. Wang, and T. Zhang, “Combining multi-scale U-Net with
transformer for welding defect detection of oil/gas pipeline,” IEEE Access,
vol. 13, pp. 5437–5445, 2025.
[33] D. Gudovskiy, S. Ishizaka, and K. Kozuka, “CFLOW-AD: Real-time unsupervised anomaly detection with localization via conditional normalizing
flows,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2022,
pp. 98–107.
[34] V. Zavrtanik, M. Kristan, and D. Skočaj, “DRAEM-A discriminatively
trained reconstruction embedding for surface anomaly detection,” in Proc.
IEEE/CVF Int. Conf. Comput. Vis., 2021, pp. 8330–8339.
[35] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “PaDiM: A patch
distribution modeling framework for anomaly detection and localization,”
in Proc. Int. Conf. Pattern Recognit., 2021, pp. 475–489.
[36] Z. Xia, X. Pan, S. Song, Li Erran Li, and G. Huang, “Vision transformer
with deformable attention,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2022, pp. 4794–4803.
[37] C.-F. Chen, Q. Fan, and R. Panda, “CrossViT: Cross-attention multi-scale
vision transformer for image classification,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis., 2021, pp. 357–366.

Kaiyue Wang received the bachelor’s degree in
software engineering from the School of Computer Science and Technology, Qingdao University, Qingdao, China, in 2024, where she is
currently working toward the master of science
degree in electronic science and technology.
Her research interest focuses on artificial
neural networks.

Chengyan Qin received the Bachelor of Engineering degree in communication engineering
in 2025 from the School of Electronic and Information Engineering, Qingdao University, China,
where he is currently working toward the master’s degree in electronic science and technology.
His research focuses on anomaly detection.

Jieru Chi received the B.S. degree in industrial
automation from Shandong University of Technology, Zibo, China, in 1992, the M.S. degree in
industrial automation from Shandong University
of Technology, Zibo, China, in 1995, and the
Ph.D. degree in system theory from Qingdao
University, Qingdao, China, in 2019.
She conducted academic research as a Visiting Scholar at Queensland University of Technology, Brisbane, Australia, from 2009 to 2010
and from 2017 to 2018. She is currently a Professor with the College of Electronics and Information, Qingdao University, Qingdao, China. She has authored or coauthored more than 30
papers in journals, such as IEEE TRANSACTIONS ON BIOMEDICAL ENGINEERING. Her research interests include Artificial Intelligence, image
processing, and intelligent information processing.

Chenglizhao Chen received the Ph.D. degree
from Beihang University, Beijing, China, in 2017.
He is a Professor with the College of Computer Science and Technology, China University
of Petroleum (East China), Qingdao, China. He
has authored or coauthored more than 50 papers in top-tier journals and conferences. He is
currently a Visiting Scholar with Beihang University. His research interests include virtual reality, computer vision, deep learning, and pattern
recognition.
Dr. Chen is an Associate Editor for the Neural Processing Letter and
an Editorial Member of Electronics.

Teng Yu received the B.S. degree in communication engineering from the Harbin Institute of Technology, Harbin, China, in 2010, and
the Ph.D. degree in electronic and communication engineering from Hanyang University,
Seoul, South Korea (under the China Scholarship Council Program), in 2015.
He is a Professor with the College of Electronics and Information, Qingdao University, Qingdao, China. He has authored or coauthored
more than 20 SCI papers in the fields of artificial
intelligence and computer vision in recent years, and is a Reviewer for
renowned journals, such as IEEE TRANSACTIONS ON IMAGE PROCESSING,
IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY,
IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, and EAAI. He research
interests include Artificial Intelligence, machine learning, computer
vision, and autonomous driving.
PAPER_TEXT
