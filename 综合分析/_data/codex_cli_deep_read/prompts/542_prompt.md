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
# [542] Self-Supervised Monocular Depth Estimation From Videos via Adaptive Reconstruction Constraints
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
编号：542
题名：Self-Supervised Monocular Depth Estimation From Videos via Adaptive Reconstruction Constraints
年份：2024
DOI：10.1109/tcsvt.2024.3492201
来源：IEEE Transactions on Circuits and Systems for Video Technology
PDF：paper/10.1109_TCSVT.2024.3492201.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测
相关性：弱相关，分数 1
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\542.txt
- 原始字符数：60665
- 本次发送字符数：60665
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. 35, NO. 3, MARCH 2025

2161

Self-Supervised Monocular Depth Estimation From
Videos via Adaptive Reconstruction Constraints
Xinchen Ye , Member, IEEE, Yuxiang Ou, Biao Wu, Rui Xu , Member, IEEE, and Haojie Li

Abstract— To estimate depth maps from monocular videos in
a self-supervised way, existing methods simultaneously predict
the pose changes between adjacent frames and the depth maps
of each frame, and then reconstruct the forward or backward
frames using them, thereby casting depth estimation as a frame
reconstruction problem. The corresponding reconstruction loss,
which serves as a key supervision signal for training the whole
network, can adversely affect the depth estimation accuracy if it
is not properly established. In this paper, we propose a novel selfsupervised monocular depth estimation method from videos via
adaptive reconstruction constraints, i.e., designing the loss functions by establishing more accurate reconstruction constraints.
Specifically, we first propose a pose-adaptive reconstruction
loss to adaptively select the optimal pose parameterizations
that yield the minimum reconstruction errors, reducing the
impact of inaccurate posture on frame reconstruction. Then,
we propose a region-sensitive reconstruction loss that fully
utilizes the pretrained image reconstruction model to adaptively
identify the poorly reconstructed regions and characterize the
deviation of these regions on feature space. Finally, we additionally construct a multi-frame depth estimation network and
design a reconstruction-guided bidirectional distillation loss to
adaptively adjust the direction of distillation between networks
of multi-frame and monocular depth estimation based on their
current reconstruction quality, which encourages them to learn
from each other and benefits the core task of monocular
depth estimation. With our proposed losses, we achieve superior
performance in comparison with state-of-the-art methods on
benchmark datasets.
Index Terms— Unsupervised, depth estimation, monocular,
adaptive reconstruction, video.

I. I NTRODUCTION

M

ONOCULAR depth estimation is a fundamental
and critical computer vision task that estimates the
pixel-wise depth information from 2D images. Results from
accurate depth estimation can facilitate various applications
Received 16 August 2024; revised 10 October 2024; accepted 2 November
2024. Date of publication 6 November 2024; date of current version 7 March
2025. This work was supported in part by the National Natural Science
Foundation of China (NSFC) under Grant 62376053, Grant 61976038, and
Grant 61932020. This article was recommended by Associate Editor S. He.
(Corresponding author: Haojie Li.)
Xinchen Ye, Yuxiang Ou, Biao Wu, and Rui Xu are with the DUT-RU
International School of Information Science and Engineering, Dalian University of Technology, Dalian, Liaoning 116024, China, and also with the
Key Laboratory for Ubiquitous Network and Service Software of Liaoning
Province, Dalian 116024, China.
Haojie Li is with the College of Computer Science and Engineering,
Shandong University of Science and Technology, Qingdao 266590, China
(e-mail: hjli@sdust.edu.cn).
Digital Object Identifier 10.1109/TCSVT.2024.3492201

such as virtual reality [1], scene reconstruction [2] and
autonomous driving [3]. Despite the success of supervised
methods [4], [5], [6], they are hindered by the need of
time-consuming and labor-intensive ground truth annotation. As an alternative, existing video-based self-supervised
methods [7], [8], [9] casts depth estimation as a frame
reconstruction problem. They simultaneously predict the pose
changes between two adjacent frames (called source frame and
target frame respectively) and the depth map of target frame,
and then reconstruct the source frame on the target view using
the predicted pose and depth information. The photometric
reconstruction loss, which measures the consistency between
the reconstructed frame and the original target frame, serves as
a key supervision for evaluating the quality of depth estimation
and guiding the training of the whole network. However,
when this loss is not effectively established, it can potentially
lead to detrimental effects and hinder the accuracy of depth
estimation.
Therefore, some current methods focus on improving
the reconstruction loss from the following aspects: 1) utilizing feature-level reconstruction loss [10], [11] which
leverages image features extracted from an additional pretrained image reconstruction auto-encoder model to strengthen
the pixel fidelity in textureless areas; 2) identifying and
excluding occluded areas using masking [12], [13], [14],
or employing minimum reprojection of adjacent frames [7] to
mitigate the photometric inconsistencies caused by occlusions;
3) developing regularization for brightness [15], [16], [17] to
address illumination inconsistencies between adjacent frames.
By modifying the reconstruction loss, the above methods can
improve the accuracy of depth estimation to some extent,
but many problems are still ignored when designing the
reconstruction loss.
First, based on our observations of real-world driving scenarios, vehicles (or cameras) predominantly travel in straight
trajectories, with turns occurring primarily at lane changes
or intersections. This observation is further corroborated by
an analysis of the KITTI dataset, as depicted in Figure 1,
which highlights the imbalanced nature of rotation and translation in real-world scenarios, making it difficult for previous
methods to simultaneously focus on the estimation of both
rotation and translation in the pose network. It is worth
noting that rotation is highly non-linear and often more difficult to estimate than translation. As a result, this limitation
has a significant negative impact on the reconstruction loss,
which in turn affects the performance of depth estimation.

1051-8215 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

2162

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. 35, NO. 3, MARCH 2025

Fig. 1. Statistical results on the KITTI odometry dataset [19] consisting of
11 sequences. We use the ground truth poses to analyze the rotation between
consecutive frames. To facilitate the interpretation, we convert the rotation
matrices to Euler angles and examine the relative rotation angles to investigate
the proportion of the rotations that exceed a certain angle threshold. The table
specifically shows the percentages of rotation angles exceeding 0.5◦ , 0.75◦ ,
1◦ , and 1.25◦ in sequences 01, 03, and 05 (left), and the overall trajectory
plot for sequence 08 (right).

Second, although the feature-level reconstruction loss [11] can
explicitly constrain each pixel to be discriminative in feature
space, it does not fully exploit the capability of the pretrained
image reconstruction auto-encoder model to emphasize on
the feature inconsistency caused by poor frame reconstruction
in self-supervised depth estimation. From the perspective of
anomaly detection [18], the auto-encoder model pretrained
on original target frames can obviously reconstruct a target
frame better than an abnormal frame.1 Thus, introducing such
reconstruction deviations from the pretrained auto-encoder
model into the loss design can better identify the poorly
reconstructed regions in the abnormal frame and properly
guide the training of the depth estimation network.
In addition, the monocular depth estimation network only
acquires limited information because of the single-frame input,
which fails to fully exploit temporal information from adjacent frames. Recent methods [20], [21], [22] have attempted
to address this issue by constructing a teacher network to
take more associative data (e.g., stereo images) as input
to infer depth maps. The teacher provides more accurate
depth information to effectively transfer knowledge to the
monocular depth estimation network (student) through unidirectional distillation. However, these methods ignore the
fact that the teacher also has errors in depth estimation and
is even less accurate than student in some areas. Note that,
monocular depth estimation relies mainly on the understanding
of appearance and semantic knowledge within features, which
can better handle occluded regions and avoid unreliable depth
estimation issues that often arise in multi-view (temporal or
stereo) depth estimation. Therefore, it is necessary to design
mutual learning strategies to promote learning from respective
strengths (multi-view vs. monocular) and ultimately facilitate
the task of monocular depth estimation.
To address the aforementioned problems, our core idea is
to design the loss functions by establishing more accurate
adaptive reconstruction constraints, thus properly guiding
the training of monocular depth estimation. As shown in
Fig. 2, we first propose a pose-adaptive reconstruction loss
to mitigate the impact of inaccurate pose estimation on frame
1 In our scenario, an abnormal frame refer to the source frame synthesized
on the target view using inaccurate estimation of pose and depth information.

reconstruction. Instead of directly outputting a single 6-DoF
pose vector, we propose to decompose the pose network
into three parallel branches, each dedicated to independently
estimating pure translation, pure rotation and full 6-DoF pose
components. Upon this, we adaptively select the optimal pose
parameterizations that yield the minimum reconstruction errors
to establish the reconstruction loss, which can efficiently
utilize the complementary information provided by different pose estimators. Second, we propose a region-sensitive
reconstruction loss that fully utilizes the pretrained image
reconstruction auto-encoder model to adaptively identify the
poorly reconstructed regions on feature space. We first apply
the warping and reconstruction selection on source frame to
obtain a reconstructed frame, then form the loss by computing
the difference between features of both reconstructed and
target frames extracted from the pretrained model. Thus, the
model can easily recognize the poorly reconstructed regions in
the reconstructed frame as an anomaly, and provide significant
deviated features than those of target frame, forcing the network to optimize these regions by back-propagating a greater
loss caused by feature inconsistency. Finally, we additionally
construct a multi-frame depth estimation network as a teacher
and design a reconstruction-guided bidirectional distillation
loss to adaptively adjust the direction of distillation between
networks of multi-frame and monocular depth estimation
based on their current reconstruction quality. This encourages
them to learn from each other in an iterative collaborative
training and benefits the core task of monocular depth estimation.
Through designing reasonable loss functions and imposing more accurate reconstruction constraints into the losses,
our method achieves superior performance of self-supervised
monocular depth estimation in comparison with state-of-theart methods on benchmark datasets. Besides, our improvement
focuses on the loss design and is suitable for assembly on
any backbone network, which would not increase the runtime
of depth estimation during testing. To summarize, our main
contributions are listed as follows:
• We propose a pose-adaptive reconstruction loss to adaptively select the optimal pose parameterizations that yield
the minimum reconstruction errors to establish the reconstruction loss, reducing the impact of inaccurate posture
on frame reconstruction.
• We propose a region-sensitive reconstruction loss that
fully utilizes the pretrained image reconstruction model
to adaptively identify the poorly reconstructed regions as
anomaly and characterize the feature deviation of these
regions on feature space.
• We propose a reconstruction-guided bidirectional distillation loss to adaptively adjust the direction of distillation
based on the reconstruction quality, encouraging both
networks of multi-frame and monocular depth estimation
to learn from each other.
II. R ELATED W ORKS
A. Self-Supervised Monocular Depth Estimation
We divide self-supervised depth estimation methods into
two categories according to the supervisory signal. The first

YE et al.: SELF-SUPERVISED MONOCULAR DEPTH ESTIMATION FROM VIDEOS

2163

Fig. 2. Overview of our whole framework for self-supervised monocular depth estimation. Given a target frame and its adjacent source frame from a video,
the goal is to predict a depth map from the target frame by a trainable backbone network. We highlight our contributions of three loss functions with different
color rectangles. Through proper guidance of the proposed losses, the backbone network can be well trained.

category uses monocular sequences exclusively, while the
second category uses additional auxiliary information such as
stereo images, stereo videos, or semantics.
For the first category, SfM learner [23] first jointly learned
monocular depth and ego-motion from monocular videos in
a self-supervised way. However, such techniques still struggle
with inferior depth estimation results when comparing with
supervised methods because the photometric loss that plays
a crucial role in the entire training process fails to establish
effectively in cases such as occlusion and textureless areas.
Numerous works are therefore suggested to address these
limitations. Monodepth2 [7] leveraged masks to eliminate
relatively static pixels and manages occlusion issues with
minimal reprojection of adjacent frames. In order to establish effective supervision on textureless regions, feature-level
reconstruction loss [10], [11] is applied to strengthen the pixel
fidelity in textureless areas. Besides, some works also focus
on the improvement of network architecture. For example,
Bae et al. [24] proposed a CNN-Transformer hybrid network
with multi-level feature aggregation to complement the shape
bias and spatial locality bias to improve the performance and
generalization of depth estimation.
For the second category, Garg et al. [25] first proposed to
estimate stereo correspondences by minimizing a photometric
loss between the left input image and the warped right image.
Godard et al. [26] used consistency between the left and
right views as a new constraint for training, reconstructing
both the left and right views and calculating consistency to
produce more accurate predictions. Ye et al. [20] utilized

recursive estimation and adaptive refinement to get more
precise depth inference from stereo pairs, and then condensed
the depth information into a monocular network. Further, many
methods [7], [27], [28] employed stereo videos for training,
which combines monocular sequence with stereo data as selfsupervision signals. Besides, some works utilize semantic
information to help depth estimation. Jung et al. [29] proposed
a metric learning method that makes use of semantics-guided
local geometry to optimize intermediate depth representations.
Li et al. [30] proposed a semantic-aware spatial feature modulation scheme to relate depth distributions to the semantic
category information.
In this paper, we focus on the task of video-based monocular depth estimation that uses only monocular sequences as
supervision. Compared with stereo images/videos, monocular
sequences are easier to obtain and apply in practical situations.
However, methods based on monocular sequences need to
bridge the relationship between adjacent frames by additionally estimating the camera ego-motion, which makes the task
of depth estimation more difficult. Therefore, part of our work
focuses on designing reasonable pose decomposition network
and pose-adaptive reconstruction loss to mitigate the impact
of inaccurate pose estimation on depth estimation.
B. Anomaly Detection
Anomaly detection establishes on the fundamental assumption that anomalous regions cannot be accurately reconstructed
as they deviate from the learned normal patterns in training
samples. These methods leverage generative models [31] to

2164

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. 35, NO. 3, MARCH 2025

establish pixel-level anomaly scores based on the pixel-wise
reconstruction error. Alternative approaches [18] address
anomaly detection as an inpainting problem, where patches
from images are randomly masked and then predicted through
the network. Thus, the pixel-wise reconstruction error can
be computed as anomaly scores. Besides, embedding-based
anomaly detection methods [32], [33] mainly project features
into a compressed space and measure the distance between
embedding vectors of normal training images and test examples. Among these methods, pre-trained deep neural networks
are commonly used for feature extraction.
Inspired by the embedding-based anomaly detection,
we propose a region-sensitive feature-level reconstruction loss
that fully utilizes an image reconstruction model pretrained
only on normal frames to identify the poorly reconstructed
regions in abnormal frames and characterize the feature deviation of these regions on feature space.
C. Knowledge Distillation
Knowledge distillation, which is first proposed in [34] for
condensing a large network into a smaller model, has garnered
various interests recently [35]. Extensive works of monocular depth estimation also utilize the distillation technique to
transfer knowledge from a sophisticated teacher network to a
naive student network [20], [21], [36], [37]. Pilzer et al. [21]
distilled the reconstruction difference between the original and
re-synthesized input images to the student network through the
computation of cycle inconsistency. Liu et al. [36] trained a
stereo depth estimation network (teacher) to generate pseudo
depth labels, then leverage the generated labels as supervision
to distill more accurate depth information into the monocular
network (student). Ye et al. [20] developed the recursive stereo
distillation method to iteratively transfer depth information
from a stereo network to a monocular network. Different
from [20] and [36], Petrovai and Nedevschi [37] constructed
their teacher network by taking three consecutive frames as
input instead of stereo images.
In general, teacher networks take more useful information as
input (e.g., cycle inconsistency, stereo image, temporal frames)
and generate more accurate results than those of students
that takes only single image as input. Through distillation,
performances of monocular depth estimation can be obviously
improved. However, the above methods ignore the fact that
the teacher also has errors in depth estimation. Upon this,
we design a bidirectional distillation loss to promote mutual
learning from respective strengths of both networks and ultimately facilitate the task of monocular depth estimation.
III. M ETHODS
A. Preliminaries
Given a target frame It and its adjacent source frame
Is ∈ {It−1 , It+1 } from a video, the goal is to predict a depth
map Dt from It by a trainable network φd . Let K be the
known camera intrinsic matrix and Pt→s be the relative pose
between It and Is obtained by a trainable pose network φ p ,
each point pt in It can be warped into the corresponding pixel

ps in the source view of Is by:
ps ∼ K Pt→s Dt ( pt )K −1 pt

(1)

where ∼ represents the homogeneous equivalence. With
Eq.(1), we can recover the target frame It from Is by:
Iˆt = Is W(Dt , Pt→s , K ) ,

(2)

where · is a differentiable bilinear interpolation [38] and
W(·, ·, ·) is the warping operation corresponding to Eq. (1).
Following [7], the training loss is the photometric reconstruction errors between the target frame It and the reconstructed frame Iˆt . based on the L1 and SSIM metrics, which
is defined as:


1 − SSIM Iˆt , It
+ (1 − α) Iˆt − It , (3)
L p ( Iˆt , It ) = α
2
where α is set to 0.85. Also, a smoothness loss [7] is added
to encourage the predicted depth map to be smooth, which is
computed as follows:
L s = |∂x Dt | e−|∂x It | + ∂ y Dt e−|∂ y It |

(4)

Besides, we employ the minimum photometric error, automasking and multi-scale depth loss techniques introduced
in [7] to reduce the negative impact of occlusion and stationary
objects, thus further improving the performance of baseline.
B. Network Architecture
Our framework is based on the above self-supervised
paradigm which contains a backbone monocular depth estimation network φd and a pose network φ p . Upon this,
we novelly design three loss functions by establishing adaptive
reconstruction constraints, thus properly guiding the training
of whole network. Specifically, as shown in Fig.2, we first
propose a pose-adaptive reconstruction loss to mitigate the
impact of inaccurate pose estimation on frame reconstruction.
Instead of directly outputting a single 6-DoF pose vector,
we introduce a pose decomposition network to independently
estimate pure translation and pure rotation, together with the
6-DoF pose vector. Through warping, we obtain a set of
reconstructed frames based on different poses and adaptively
select an optimal one corresponding to the minimum reconstruction errors from the reconstructed frames through the
reconstruction selection module. Upon this, the photometric
reconstruction loss L p can be established by computing the
difference between the target frame and the selected frame.
Second, we propose a region-sensitive reconstruction loss
that fully utilizes the pretrained encoder of an image reconstruction model to adaptively identify the poorly reconstructed
regions on feature space. We send the selected frame and
the target frame into the encoder to extract their respective
feature maps and form the loss by computing the difference
between them. Note that, the encoder pretrained on original
frames can provide significant deviated features of poorly
reconstructed regions (regarded as anomaly) in reconstructed
frames compared to those of target (original) frames, forcing
the network to optimize these regions by back-propagating a
greater loss caused by feature inconsistency.

YE et al.: SELF-SUPERVISED MONOCULAR DEPTH ESTIMATION FROM VIDEOS

TABLE I

2165

D. Region-Sensitive Reconstruction Loss

L IST OF S YMBOLS AND N OTATIONS

Finally, we additionally construct a teacher depth estimation
network with adjacent multiple frames as input, which enables
the network to better model the temporal information. Upon
this, we design a reconstruction-guided bidirectional distillation loss to adaptively adjust the direction of distillation
between the student and teacher networks. Once obtaining
the selected frames from reconstruction selection of both
networks, we compute the distillation direction mask by comparing their reconstruction qualities through the reconstruction
evaluation module and adaptively steer the distillation direction, which can encourage both networks to learn from each
other in an iterative collaborative training and benefits the
student. The symbols and notations used are summarized in
Table I.

In [11], the authors proposed to utilize feature-level reconstruction loss to strengthen the pixel fidelity and discriminant
in textureless areas on feature space. However, they just
leverage the pretrained image reconstruction model (shown
in Fig. 2) as a feature extractor, but ignore the potential
capabilities of the model to identify the poorly reconstructed
frames as anomaly, which motivate us to go a step further.
Unlike [11] that directly extracts features of original source
and target frames from the pretrained model and then applies
warping operation to align source features to the target view
for the convenience of per-pixel loss computation, we invert
the entire process. That is, we first apply the pipeline of
warping and reconstruction selection on source frame and
∗
then extract features of both the selected frame Iˆti and
the target frames It from the pretrained model. Since the
model is trained on normal original frames, it cannot easily
reconstruct the abnormal regions (caused by wrong depth
∗
information in the warping) in Iˆti and provide significant
deviated features than those of target frame It . Upon this,
we obtain our region-sensitive reconstruction loss, which is
defined as follows:
∗

L r = φe ( Iˆti ) − φe (It )

1

(6)

where φe is the pretrained encoder of an image reconstruction
model that is obtained similar to the way introduced in [11].
E. Reconstruction-Guided Bidirectional Distillation Loss

C. Pose Decomposition & Pose-Adaptive Reconstruction Loss
To accurately predict the pose transformation, we design
a pose decomposition network, which contains three parallel
branches to independently predict pure translation Tt→s ∈
T(3), pure rotation Rt→s ∈ SO(3) and full 6-DoF pose Pt→s ∈
SE(3). According to Eq.(1) and Eq.(2), we generate a set
of reconstructed frames { Iˆti , i ∈ (T(3), SO(3), SE(3), T(3) +
SO(3))} by considering four pose transformation cases, i.e.,
Tt→s , Rt→s , Pt→s and the combined pose Tt→s + Rt→s .
Then, in the reconstruction selection module, we subtract Iˆti
from the target frame Iˆt and generate reconstruction errors for
each Iˆti through the photometric reconstruction loss L ip ( Iˆti , It )
shown in Eq.(3). By comparing these error values and selecting
the one with the minimum reconstruction error, we obtain the
optimal pose parameterizations:
i ∗ = arg min L ip

(5)

i

Upon this, we can finally select the reconstruction frame
∗
∗
Iˆti and its corresponding reconstruction loss L ip to form our
pose-adaptive reconstruction loss. During back propagation for
current iteration of training, we only update the i ∗ -th branch
to make itself to be more specialized in estimating its own
pose transformation. When the combined pose Tt→s + Rt→s
is chosen to be optimal, both translation and rotation branches
will be updated. Through our improvement, the complementary information provided by different pose estimators can be
efficiently utilized to mitigate the impact of inaccurate pose
estimation on reconstruction loss.

The teacher network has the same architecture with the
student network except for its input that contains the target
frame and two adjacent source frames {It−1 , It , It+1 }, which
can better capture the geometric structure of the scene and
help train the student. However, it is important to note that in
scenarios with occlusions and moving objects, depth estimation results from the teacher are often unreliable. Therefore,
the key idea to promote collaborative learning between both
networks is to ensure that only relatively accurate knowledge
is distilled from the teacher to the student, and vice versa,
which motivate us to design the bidirectional distillation loss.
Specifically, assume that we frozen the teacher network and
train the student network in the current training stage, we can
obtain respective reconstructed frames Iˆttea , Iˆtstu and their
stu
corresponding photometric reconstruction errors L tea
p , Lp
2
from the reconstruction selection module. According to the
stu
pixel-wise comparison between L tea
p and L p , a mask τ is
generated to determine whether the depth information of each
pixel should be distilled from the teacher to the student:
tea
τ (k) = [L stu
p (k) > L p (k)]

Thus, the distillation loss can be defined as:

L d = τ ◦ Dt − Dttea 1

(7)

(8)

Here, Dttea represents the estimated depth map by the teacher
and ‘◦’ denotes element-wise multiplication. It indicates that
we only use the depth pixels of the teacher to supervise the
2 The superscript of i ∗ is omitted for easy presentation.

2166

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. 35, NO. 3, MARCH 2025

student when their corresponding reconstruction errors are
smaller than those of student.
After the student is trained, we frozen it and train the teacher
in the next training stage by an iterative fashion with the same
distillation strategy introduced above, which can be defined as:

tea
L tea
(9)
d = (1 − τ ) ◦ Dt − Dt
1
F. Total Loss
The training process mainly consists of three stages.
At beginning, we train the student network in a fully
self-supervised manner and the loss function incorporates
∗
three components, i.e., pose-adaptive reconstruction loss L ip ,
region-sensitive reconstruction loss L f and the smoothness
loss L s , which can be written as:
∗

L stu = λs L s + λ f L f + µL ip

(10)

where λs and λ f are the weighting factors that control the
importance of each loss. µ refers to the mask proposed in [7].
Similarly, the teacher network is trained from scratch with the
same loss of L stu .
Then, we fine-tune the teacher with the help of student. The
depth map of teacher network is adaptively supervised by that
of the student. As shown in Eq.(7) and Eq.(9), we compute the
mask τ and distill the knowledge from student to teacher with
L tea
d . For the reconstruction losses, we also introduce the mask
τ and revise the losses to avoid conflicts with the distillation
loss:
stu
tea
L tea
p = (1 − τ ) · L p + τ · L p

(11)

stu
tea
L tea
f = (1 − τ ) · L f + τ · L f

(12)

stu represent the reconstruction loss of the
where L stu
p , Lf
tea are for the teacher. Constudent network while L tea
p , Lf
sequently, the loss for training the teacher network is:
tea
tea
L tea = λs L s + λ f L tea
f + µL p + λd L d

(13)

where µ, λs and λ f are hyper-parameters similar to those used
in L stu . λd is the weighting factors of distillation.
Finally, we freeze the teacher and use it to guide the training
of the student. The loss function in this stage is similar to the
loss function L tea used for training the teacher network, and
we omit it for saving the space. Note that, the above training
pipeline can be iteratively conducted between the teacher and
student until the convergence.
IV. E XPERIMENTS
Training Dataset: We evaluate the proposed method on
KITTI [19] and Make3D [49] datasets. KITTI dataset [19]
comprises monocular sequences and corresponding 3D laser
scans of outdoor scenes captured by imaging equipment
mounted on a moving vehicle. For training purposes, we adopt
the dataset split proposed by [39]. After eliminating static
frames using a pre-processing step recommended by [23],
we are left with 39,810 monocular frame triplets for training
and 4,424 frame triplets for testing. Make3D [49] consists
of 400 images as training set and 134 images as testing set.
Since Make3D only includes RGB-D pairs without adjacent

frames, it cannot be used for training, and thus we only test
the generalization on Make3D through the well-trained KITTI
model. Besides, we also test the adaptability of our method
on NYU v2 dataset [50], a rotation-dominant indoor dataset.
In NYU v2, we use the officially provided 654 densely labeled
images for testing, and the rest sequences for training.
Implementation Details: The framework mainly contains
four parts, i.e., student and teacher networks for depth estimation, pose network in pose decomposition, and the encoder
pretrained from an image reconstruction model. For depth
estimation, we use the network architecture that replaced the
original ResNet-based depth encoder in Monodepth2 [7] with
HRNet-18 [51] as our backbone for both student and teacher,
but adjust the number of channels for multiple frame inputs
through an 1 × 1 convolution to adapt to the teacher network.
For pose estimation, we use the generic pose network proposed
in [7] as our backbone, which employs ResNet-18 [52] as
the encoder. For the pretrained encoder, we employ the same
method in [11] to construct an image reconstruction autoencoder model, and use its encoder as a frozen module to
extract features for computing the feature-level reconstruction
loss.
During the training process, we initially train the student
network and teacher network from scratch until they converge. Subsequently, we fine-tune the teacher network through
selective distillation, utilizing the fixed student network as a
reference. Then, we leverage the more capable teacher network
to assist the training of student network by fixing the teacher
and training the student until it converges again. The number
of iterations in collaborative training is set to 2 according to
our experimental verification. We set the batch size as 10 and
adopt the Adam optimizer with β1 = 0.9, β2 = 0.999, and
ϵ = 10−4 . We set the initial learning rate as 10−4 for the first
15 epochs and then 10−5 for fine-tuning the remainder. For the
adjustment parameters, λs , λ f , and λd are respectively set to
10−3 , 10−3 , and 1 according to experimental verification. The
whole training process is shown in Algorithm 1. We adopt the
measures used in [39] for quantitative evaluation.
A. Performance Comparison
1) Quantitative Result: Table II shows the comparison
results with state-of-the-art methods. Note that, all the compared methods use monocular images as input in testing
phase. For fair comparison, we only compare with methods
that exclusively using monocular videos (M) as supervision, and without any additional data incorporated. As a
result, our method exceeds other methods including the
transformer-based ones (i.e., MonoFormer and Lite-Mono8M), especially on the Sq Rel indicator, where it attains a
5% increase over the runner-up, proving its effectiveness.
2) Qualitative Result: Fig. 3 shows the qualitative results
of our depth predictions. Compared to other self-supervised
methods, our method can recover the details of thin objects
and the fine structures of objects (highlighted by the red
boxes in the figure), and achieve the lowest RMSE values
on each given example. For instance, in the first column, our
method can recover the depth of the billboards and fence posts,

YE et al.: SELF-SUPERVISED MONOCULAR DEPTH ESTIMATION FROM VIDEOS

2167

TABLE II
R ESULTS ON KITTI DATASET U SING THE E IGEN S PLIT [39]. A LL M ETHODS A RE T RAINED BY U SING M ONOCULAR V IDEOS W ITH N O A DDITIONAL
DATA I NCORPORATED . T HE B EST R ESULTS A RE M ARKED W ITH B OLD -FACE W HILE S ECOND B EST O NES W ITH U NDERLINE R ESPECTIVELY

Algorithm 1 Depth Estimation Process
Input: Monocular video frames {It }
Output: Estimated depth maps {Dt }
Model Training:
Phase 1: Student Training
for each frame It in each training epoch do
1. Estimate depth map Dtstu using φdstu
2. Estimate poses Tt→s , Rt→s , Pt→s using φ p
3. Generate reconstructed frames { Iˆti } for different poses
transformations
4. Compute photometric reconstruction losses {L ip } for
each Iˆti
5. Select optimal pose i ∗ = arg mini L ip
∗
6. Compute pose-adaptive reconstruction loss L ip using
∗
Iˆti
7. Compute region-sensitive reconstruction loss L r
8. Update φdstu using total loss L stu
end for
Phase 2: Teacher Training
Freeze student network φdstu
for each frame It in each training epoch do
1. Estimate depth map Dttea using φdtea
2. Compute photometric reconstruction errors L stu
p and
tea
L p through pose-adaptive reconstruction loss
tea
3. Generate mask τ by comparing L stu
p and L p
tea
4. Compute distillation loss L d for teacher network:
L tea
d
5. Compute region-sensitive reconstruction loss L r
6. Update φdtea using total loss L tea
end for
Phase 3: Iterative Updating
Swap roles of student and teacher networks and repeat
Phase 2
Model Testing:
Use the trained student network φdstu to estimate depth
maps Dt for test frames It

while other methods predict inaccurate depths or wrong shape.
In third column, Monodepth2, HR-Depth, and Lite-Mono fail

to recognize the wall on the left side of image. In the sixth
column, it is clear that our method provide the most accurate
depth prediction, both in terms of object perception and RMSE
numerical results.
B. Ablation Study
1) The Full Pipeline: In this section, we analyze the
performance of our method by studying the influence of
three losses we have proposed on the final depth prediction.
We compared the performances with and without our proposed losses and reported the results in Table IV. At the
starting point, the first row gives our baseline that replaced
the original ResNet-based depth encoder in Monodepth2 [7]
with HRNet-18 [51], and the same self-supervision pipeline
introduced in the Sec. III-A. Upon this, we replace the
pose network [7] with our pose decomposition module and
corresponding pose-adaptive reconstruction loss (the second
row), and the performance of depth estimation is obviously
improved, especially on Sq Rel and RMSE metrics (15.5%
and 4.8% improvement respectively). Similarly, introducing
the region-sensitive reconstruction loss solely (the third row)
can also bring an obvious improvement against the baseline.
Going a step further, introducing both of them into the baseline
(the fourth row) can push the performance to a new upper
bound. Finally, when further using the bidirectional distillation
to encourage a mutual learning from both teacher and student
networks (the last row), the ultimate superior performance is
achieved. Through the ablation study, each proposed loss can
present its contribution to the performance of depth estimation.
Next, we give some detailed analysis through visual and
numerical results to further demonstrate the effectiveness of
our proposed losses:
2) Pose-Adaptive Reconstruction Loss: Fig. 4 shows the
error maps of reconstructed images against groundtruth target
images without and with pose decomposition module and
pose-adaptive reconstruction loss. It is obvious that, under
the condition that the depth estimation network remains
unchanged, training with the loss will make the reconstruction
error smaller (highlighted by the red rectangles). Since the
displacement of the foreground between two frames will be

2168

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. 35, NO. 3, MARCH 2025

Fig. 3. Qualitative comparison with other methods on KITTI dataset: (a) Monodepth2 [7], (b) HR-Depth [42], (c) DIFFNet [28], (d) Lite-Mono-8M [46],
(e) Ours. Regions of red rectangles in predicted depth maps present obvious visual differences among these methods. Besides, error maps (red for higher
errors while blue for lower errors) against groudtruths and their corresponding RMSE values are given for better presentation.
TABLE III
A BLATION S TUDY OF THE P ROPOSED P OSE -A DAPTIVE R ECONSTRUCTION L OSS (PAR), R EGION -S ENSITIVE R ECONSTRUCTION L OSS (RSR), AND
R ECONSTRUCTION -G UIDED B IDIRECTIONAL D ISTILLATION L OSS (RGBD) ON KITTI DATASET

TABLE IV
Q UANTITATIVE R ESULT OF THE P OSE E STIMATION R ESULT ON KITTI
O DOMETRY DATASET

Fig. 4. Qualitative ablation study of the proposed pose-adaptive reconstruction loss. Error maps (red for higher errors while blue for lower errors) of
reconstructed images (b) without and (c) with pose-adaptive reconstruction
loss against groundtruth target images are shown.

relatively large, inaccurate pose estimation will cause wrong
re-reprojection, resulting in larger reconstruction error, especially around the fine structures of foreground objects. This
also proves that our pose estimation is more accurate and
avoids interference to the depth estimation network, which
indirectly helps improve the performance of depth estimation.
Moreover, we test the effectiveness of our pose decomposition network on the KITTI odometry dataset against the

baseline (without our proposed pose modules). As shown in
Table IV, absolute trajectory error (ATE), relative translation
error (RTE), and relative rotation error (RRE) are given.
Please note that ATE is calculated following the approach in
SfMLearner [23], while RTE and RRE are computed based
on SC-Depth [54]. RTE is the average translational root mean
square error (RMSE) drift in percentage on length from 100,
200, . . . , 800m, while RRE is the average rotation RMSE

YE et al.: SELF-SUPERVISED MONOCULAR DEPTH ESTIMATION FROM VIDEOS

2169

TABLE V
A BLATION S TUDY OF THE P ROPOSED R EGION -S ENSITIVE R ECONSTRUCTION L OSS AGAINST THE F EATURE M ETRIC L OSS [11]

TABLE VI
A BLATION S TUDY OF THE P ROPOSED B IDIRECTIONAL D ISTILLATION L OSS . ‘T EACHER _I NITIAL’ AND ‘S TUDENT _I NITIAL’ R EPRESENT THE
C ONVERGED R ESULTS W HEN T RAINING F ROM S CRATCH W ITHOUT B IDIRECTIONAL D ISTILLATION , W HILE ‘T EACHER _E ND ’ AND
‘S TUDENT _E ND ’ A RE THE C ONVERGED R ESULTS W ITH D ISTILLATION

Fig. 6. Statistical results on indoor dataset [57]. We use the ground truth poses
to analyze the rotation between consecutive frames. The table specifically
shows the percentages of rotation angles exceeding 0.5o , 0.75o , 1o , and 1.25o
in sequences 0000, 0001, and 0699 (left), and the overall trajectory plot for
sequence 0000 (right).
Fig. 5. Qualitative ablation study of the proposed region-sensitive reconstruction loss (RSR) and bidirectional distillation loss (BD) on KITTI dataset.
(a) Target images, (b) Baseline, (c) Baseline + [11], (d) Baseline + RSR,
(e) Ours.

drift (◦ /100m) on length from 100, 200, . . . , 800m. The ATE
is a measure of global consistency between two trajectories,
comparing absolute distances between ground truth and predicted poses at each point in time. On sequence 09, our ATE
is 0.007 compared to the baseline of 0.020, while on sequence
10, our ATE is 0.005 compared to the baseline of 0.014.
Additionally, since our method separately estimates multiple
pose combinations and selects the optimal result from them,
there is an improvement in performance on both translation
and rotation metrics against other compared methods.
3) Region-Sensitive Reconstruction Loss: As stated in
Sec.III-D, our region-sensitive reconstruction loss can be
regarded as an improved version of feature-level loss based on
the work [11]. Although the processing flow is only different in
the order of viewpoint synthesis and feature extraction, it has
completely different meanings. Reference [11] just leverages
the pre-trained encoder as a pure feature extractor, but we
excavate the potential capabilities of the model to identify
the poorly reconstructed frames as anomaly. Table V verifies
our effectiveness. For fair comparison, both methods are introduced into the same baseline (also the first row of Table III)
and we achieve better performance. Fig. 5 additionally shows
the visual results. Focusing on the comparison between (c)
and (d), thanks to the pre-trained model’s holistic semantic

understanding of objects and sensitivity to anomalies, our
method performs better in recovering objects with large color
differences (the first column) or fine structures (the second and
third columns).
4) Reconstruction-Guided Bidirectional Distillation Loss:
Table VI shows the performance comparison between teacher
and student networks at the independent training stage
(training from scratch) and collaborative training stage with
bidirectional distillation. At beginning, the performance of the
teacher is better than that of the student owing to incorporate
more associative data (e.g., stereo images) as input. Through
collaborative learning with our proposed reconstruction-guided
bidirectional distillation loss, the student and the teacher can
learn from each other to further enhance their performance,
and ultimately achieve comparable results. Due to slightly different parameter settings or other loss function settings, their
performance will inevitably have some fluctuations, resulting
in situations similar to those in the table. However, their
performances are generally similar. Fig. 5 (e) also demonstrate
its effectiveness. With bidirectional distillation, the recovered
details are more accurate, such as the smoothness of the car
in the first example and the structure of the sticks in last two
examples.
C. Adaptability and Generalization
First, we validate the adaptability of our proposed
method on NYU v2 dataset, which features challenging
rotation-dominant indoor scenes. As shown in Figure 6, unlike

2170

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. 35, NO. 3, MARCH 2025

TABLE VII
A DAPTABILITY ON NYU V 2 DATASET [50]

TABLE VIII
M ODEL S IZE , RUNTIME , AND P ERFORMANCE C OMPARISON OF D IFFERENT M ETHODS ON M AKE 3D DATASET

Fig. 8. Qualitative comparison on Make3D dataset: (a) Color image, (b) Monodepth2 [7], (c) HR-Depth [42], (d) DIFFNet [28], (e) Lite-Mono-8M [46],
(f) Ours. Regions of red rectangles in predicted depth maps present obvious
visual differences among these methods.

Fig. 7.
Qualitative comparison on NYU v2 dataset: (a) Color image,
(b) Bian et al. (Baseline) [54], (c) Ours, (d) groundtruth.

outdoor scenes where vehicles mainly move straight and only
turn at lane changes or intersections, the pose variations in
indoor scenes are more complex, and the opposite situation
occurs: the proportion of rotations is much higher than that of
straight movements. However, this also represents a form of
imbalance between rotation and translation data. Our proposed
method is also applicable to this situation. The experiments in
Table VII can validate this. We use a recent self-supervised
depth estimation network [54] which is also applied to indoor
scenes, as our baseline. With our proposed pose-adaptive
reconstruction module, we achieve better performance against
the Baseline network, and outperform other methods that also
test on NYU v2 dataset. Fig. 7 shows the visual comparison.
Our method infers more accurate depth values and sharper
depth edges than the Baseline.

Next, we test the cross-dataset generalization ability and
apply our model trained on KITTI to Make3D dataset.
We compare with other methods among which their models are
available and can be tested on Makes3D directly. As shown
in Table VIII, we achieve the best performance in all metrics, demonstrating the effectiveness of the proposed method
in cross-dataset generalization. Fig. 8 shows the qualitative
results. In contrast, our method can recover fine structures of
objects and provide more reasonable depth values.
D. Runtime
As shown in Table VIII, our core improvement focuses on
the loss design and is suitable for assembly on any backbone
network, which would not increase the runtime of depth
estimation during testing. The running time mainly depends
on the size of backbone depth network. Monodepth2 adopts
the simplest ResNet-18 as the backbone network and presents
the fast runtime (32ms). Utilizing similar backbone, the case
‘Ours (RestNet-18)’ has the same model size and runtime as
Monodepth2 but achieves obvious performance improvement.
Similar result is concluded on DIFFNet backbone (HRNet-18).

YE et al.: SELF-SUPERVISED MONOCULAR DEPTH ESTIMATION FROM VIDEOS

V. C ONCLUSION AND F UTURE D IRECTIONS
This paper proposes three novel self-supervised losses via
adaptive reconstruction constraints, including pose-adaptive
reconstruction loss, region-sensitive reconstruction loss, and
bidirectional distillation loss. We achieve superior performance
compared with other state-of-the-art methods.
For future directions, we aim to address the failure of
photometric loss in adverse conditions such as nighttime.
We will investigate the use of alternative loss functions and
data augmentation techniques that can enhance the model’s
performance under low-light conditions.
R EFERENCES
[1] D.-Y. Nam and J.-K. Han, “An efficient algorithm for generating
harmonized stereoscopic 360◦ VR images,” IEEE Trans. Circuits Syst.
Video Technol., vol. 31, no. 12, pp. 4864–4882, Dec. 2021.
[2] C. Li et al., “Hybrid-MVS: Robust multi-view reconstruction with hybrid
optimization of visual and depth cues,” IEEE Trans. Circuits Syst. Video
Technol., vol. 33, no. 12, pp. 7630–7644, Mar. 2023.
[3] C. Tao, J. Cao, C. Wang, Z. Zhang, and Z. Gao, “Pseudo-mono for
monocular 3D object detection in autonomous driving,” IEEE Trans.
Circuits Syst. Video Technol., vol. 33, no. 8, p. 1, 2023.
[4] M. Song, S. Lim, and W. Kim, “Monocular depth estimation using
Laplacian pyramid-based depth residuals,” IEEE Trans. Circuits Syst.
Video Technol., vol. 31, no. 11, pp. 4381–4393, Nov. 2021.
[5] Y. Cao, T. Zhao, K. Xian, C. Shen, Z. Cao, and S. Xu, “Monocular depth
estimation with augmented ordinal depth relationships,” IEEE Trans.
Circuits Syst. Video Technol., vol. 30, no. 8, pp. 2674–2682, Aug. 2020.
[6] S. F. Bhat, I. Alhashim, and P. Wonka, “AdaBins: Depth estimation using
adaptive bins,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
Jan. 2021, pp. 4009–4018.
[7] C. Godard, O. M. Aodha, M. Firman, and G. Brostow, “Digging into
self-supervised monocular depth estimation,” in Proc. IEEE/CVF Int.
Conf. Comput. Vis. (ICCV), Oct. 2019, pp. 3828–3838.
[8] R. Li, P. Ji, Y. Xu, and B. Bhanu, “MonoIndoor++: Towards better
practice of self-supervised monocular depth estimation for indoor environments,” IEEE Trans. Circuits Syst. Video Technol., vol. 33, no. 2,
pp. 830–846, Feb. 2023.
[9] S. Chen, Z. Pu, X. Fan, and B. Zou, “Fixing defect of photometric loss
for self-supervised monocular depth estimation,” IEEE Trans. Circuits
Syst. Video Technol., vol. 32, no. 3, pp. 1328–1338, Mar. 2022.
[10] H. Zhan, R. Garg, C. S. Weerasekera, K. Li, H. Agarwal, and I. M. Reid,
“Unsupervised learning of monocular depth estimation and visual
odometry with deep feature reconstruction,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., Jun. 2018, pp. 340–349.
[11] C. Shu, K. Yu, Z. Duan, and K. Yang, “Feature-metric loss for selfsupervised learning of depth and egomotion,” in Proc. ECCV. Cham,
Switzerland: Springer, 2020, pp. 572–588.
[12] K. Zhou et al., “DevNet: Self-supervised monocular depth learning
via density volume construction,” in Proc. ECCV. Cham, Switzerland:
Springer, 2022, pp. 125–142.
[13] Z. Zhou and Q. Dong, “Learning occlusion-aware coarse-to-fine depth
map for self-supervised monocular depth estimation,” in Proc. 30th ACM
Int. Conf. Multimedia, Oct. 2022, pp. 6386–6395.
[14] G. Wang, J. Zhong, S. Zhao, W. Wu, Z. Liu, and H. Wang, “3D
hierarchical refinement and augmentation for unsupervised learning of
depth and pose from monocular video,” IEEE Trans. Circuits Syst. Video
Technol., vol. 33, no. 4, pp. 1776–1786, Apr. 2023.
[15] W. Miled, J.-C. Pesquet, and M. Parent, “A convex optimization
approach for depth estimation under illumination variation,” IEEE Trans.
Image Process., vol. 18, no. 4, pp. 813–830, Apr. 2009.
[16] C. Chaux, M. El-Gheche, J. Farah, J.-C. Pesquet, and
B. Pesquet-Popescu, “A parallel proximal splitting method for
disparity estimation from multicomponent images under illumination
variation,” J. Math. Imag. Vis., vol. 47, no. 3, pp. 167–178, Nov. 2013.
[17] N. Yang, L. von Stumberg, R. Wang, and D. Cremers, “D3VO: Deep
depth, deep pose and deep uncertainty for monocular visual odometry,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2020, pp. 1278–1289.

2171

[18] N.-C. Ristea et al., “Self-supervised predictive convolutional attentive
block for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2022, pp. 13576–13586.
[19] A. Geiger, P. Lenz, C. Stiller, and R. Urtasun, “Vision meets robotics:
The KITTI dataset,” Int. J. Robot. Res., vol. 32, no. 11, pp. 1231–1237,
2013.
[20] X. Ye, X. Fan, M. Zhang, R. Xu, and W. Zhong, “Unsupervised
monocular depth estimation via recursive stereo distillation,” IEEE
Trans. Image Process., vol. 30, pp. 4492–4504, 2021.
[21] A. Pilzer, S. Lathuilière, N. Sebe, and E. Ricci, “Refine and distill:
Exploiting cycle-inconsistency and knowledge distillation for unsupervised monocular depth estimation,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jun. 2019, pp. 9768–9777.
[22] Z. Liu, R. Li, S. Shao, X. Wu, and W. Chen, “Self-supervised monocular
depth estimation with self-reference distillation and disparity offset
refinement,” IEEE Trans. Circuits Syst. Video Technol., vol. 33, no. 12,
p. 1, 2023.
[23] T. Zhou, M. Brown, N. Snavely, and D. G. Lowe, “Unsupervised
learning of depth and ego-motion from video,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017, pp. 1851–1858.
[24] J. Bae, S. Moon, and S. Im, “Deep digging into the generalization of
self-supervised monocular depth estimation,” in Proc. AAAI Conf. Artif.
Intell., 2023, vol. 37, no. 1, pp. 187–196.
[25] R. Garg, B. G. V. Kumar, G. Carneiro, and I. Reid, “Unsupervised CNN
for single view depth estimation: Geometry to the rescue,” in Proc. Eur.
Conf. Comput. Vis. (ECCV), 2016, pp. 740–756.
[26] C. Godard, O. M. Aodha, and G. J. Brostow, “Unsupervised monocular
depth estimation with left-right consistency,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017, pp. 270–279.
[27] J. Watson, M. Firman, G. Brostow, and D. Turmukhambetov, “Selfsupervised monocular depth hints,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis. (ICCV), Oct. 2019, pp. 2162–2171.
[28] H. Zhou, D. Greenwood, and S. Taylor, “Self-supervised monocular
depth estimation with internal feature fusion,” in Proc. BMVC, 2021,
p. 378.
[29] H. Jung, E. Park, and S. Yoo, “Fine-grained semantics-aware representation enhancement for self-supervised monocular depth estimation,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021,
pp. 12642–12652.
[30] R. Li et al., “Learning depth via leveraging semantics: Self-supervised
monocular depth estimation with both implicit and explicit semantic
guidance,” Pattern Recognit., vol. 137, May 2023, Art. no. 109297.
[31] D. Zimmerer, F. Isensee, J. Petersen, S. Kohl, and K. Maier-Hein,
“Unsupervised anomaly localization using variational auto-encoders,” in
Proc. MICCAI. Cham, Switzerland: Springer, 2019, pp. 289–297.
[32] O. Rippel, P. Mertens, and D. Merhof, “Modeling the distribution of
normal data in pre-trained deep features for anomaly detection,” in Proc.
25th Int. Conf. Pattern Recognit. (ICPR), Jan. 2021, pp. 6726–6733.
[33] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and
P. Gehler, “Towards total recall in industrial anomaly detection,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2022,
pp. 14318–14328.
[34] G. Hinton, O. Vinyals, and J. Dean, “Distilling the knowledge in a neural
network,” 2015, arXiv:1503.02531.
[35] M. Phuong and C. Lampert, “Distillation-based training for multi-exit
architectures,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2019, pp. 1355–1364.
[36] H. Liu, J. Yuan, C. Wang, and J. Chen, “Pseudo supervised
monocular depth estimation with teacher-student network,” 2021,
arXiv:2110.11545.
[37] A. Petrovai and S. Nedevschi, “Exploiting pseudo labels in a
self-supervised learning framework for improved monocular depth estimation,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2022, pp. 1568–1578.
[38] M. Jaderberg, K. Simonyan, A. Zisserman, and K. Kavukcuoglu, “Spatial transformer networks,” in Proc. Adv. Neural Inf. Process. Syst.,
vol. 28, Dec. 2015, pp. 2017–2025.
[39] D. Eigen, C. Puhrsch, and R. Fergus, “Depth map prediction from a
single image using a multi-scale deep network,” in Proc. Adv. Neural
Inf. Process. Syst., vol. 27, 2014, pp. 2366–2374.
[40] J. Zhou, Y. Wang, K. Qin, and W. Zeng, “Unsupervised high-resolution
depth learning from videos with dual networks,” in Proc. IEEE Int. Conf.
Comput. Vis., Nov. 2019, pp. 6872–6881.
[41] V. Guizilini, R. Ambrus, S. Pillai, A. Raventos, and A. Gaidon,
“3D packing for self-supervised monocular depth estimation,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020,
pp. 2485–2494.

2172

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. 35, NO. 3, MARCH 2025

[42] X. Lyu et al., “HR-Depth: High resolution self-supervised monocular
depth estimation,” in Proc. AAAI Conf. Artif. Intell., vol. 35, no. 3,
2021, pp. 2294–2301.
[43] J. Yan, H. Zhao, P. Bu, and Y. Jin, “Channel-wise attention-based
network for self-supervised monocular depth estimation,” in Proc. Int.
Conf. 3D Vis. (3DV), Dec. 2021, pp. 464–473.
[44] T.-W. Hui, “RM-depth: Unsupervised learning of recurrent monocular
depth in dynamic scenes,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2022, pp. 1665–1674.
[45] W. Han, J. Yin, X. Jin, X. Dai, and J. Shen, “BRNet: Exploring comprehensive features for monocular depth estimation,” in Proc. 17th Eur.
Conf. Comput. Vis. (ECCV). Cham, Switzerland: Springer, Oct. 2022,
pp. 586–602.
[46] N. Zhang, F. Nex, G. Vosselman, and N. Kerle, “Lite-Mono:
A lightweight CNN and transformer architecture for self-supervised
monocular depth estimation,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., Jun. 2023, pp. 18537–18546.
[47] L. Sun, J.-W. Bian, H. Zhan, W. Yin, I. Reid, and C. Shen,
“SC-DepthV3: Robust self-supervised monocular depth estimation for
dynamic scenes,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 46, no. 1,
pp. 497–508, Jan. 2024.
[48] M. Xiong, Z. Zhang, J. Liu, T. Zhang, and H. Xiong, “Monocular
depth estimation using self-supervised learning with more effective
geometric constraints,” Eng. Appl. Artif. Intell., vol. 128, Feb. 2024,
Art. no. 107489.
[49] A. Saxena, S. H. Chung, and A. Y. Ng, “3-D depth reconstruction from
a single still image,” Int. J. Comput. Vis., vol. 76, no. 1, pp. 53–69,
2008.
[50] N. Silberman, D. Hoiem, P. Kohli, and R. Fergus, “Indoor segmentation
and support inference from RGBD images,” in Proc. Eur. Conf. Comput.
Vis. (ECCV). Cham, Switzerland: Springer, 2012, pp. 746–760.
[51] J. Wang et al., “Deep high-resolution representation learning for visual
recognition,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 43, no. 10,
pp. 3349–3364, Oct. 2020.
[52] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.
[53] T. Shen et al., “Beyond photometric loss for self-supervised ego-motion
estimation,” in Proc. Int. Conf. Robot. Autom. (ICRA), May 2019,
pp. 6359–6365.
[54] J.-W. Bian et al., “Unsupervised scale-consistent depth learning from
video,” Int. J. Comput. Vis., vol. 129, no. 9, pp. 2548–2564, Sep. 2021.
[55] J. Zhou, Y. Wang, K. Qin, and W. Zeng, “Moving indoor: Unsupervised
video depth learning in challenging environments,” in Proc. IEEE/CVF
Int. Conf. Comput. Vis. (ICCV), Oct. 2019, pp. 8617–8626.
[56] W. Zhao, S. Liu, Y. Shu, and Y.-J. Liu, “Towards better generalization:
Joint depth-pose learning without PoseNet,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020, pp. 9148–9158.
[57] A. Dai, A. X. Chang, M. Savva, M. Halber, T. Funkhouser, and
M. Nießner, “ScanNet: Richly-annotated 3D reconstructions of indoor
scenes,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jul. 2017, pp. 2432–2443.

Yuxiang Ou received the B.S. degree in software
engineering from Dalian University of Technology,
Dalian, Liaoning, China, in 2022, where he is
currently pursuing the M.S. degree. His research
interests include depth estimation and computer
vision.

Xinchen Ye (Member, IEEE) received the B.E.
and Ph.D. degrees from Tianjin University, Tianjin,
China, in 2012 and 2016, respectively. He was with
the Signal Processing Laboratory, EPFL, Lausanne,
Switzerland, in 2015, under the grant of the Swiss
Federal Government. Since 2016, he has been a Faculty Member with Dalian University of Technology,
Dalian, Liaoning, China, where he is currently an
Associate Professor. His current research interests
include image/video processing and 3D imaging.

Haojie Li received the B.E. degree from Nankai
University, Tianjin, in 1996, and the Ph.D. degree
from the Institute of Computing Technology,
Chinese Academy of Sciences, Beijing, in 2007.
He is currently a Professor with the College of Computer Science and Engineering, Shandong University
of Science and Technology. His research interests
include social media computing and multimedia
information retrieval.

Biao Wu received the B.S. and M.S. degrees in
software engineering from Dalian University of
Technology, Dalian, Liaoning, China, in 2020 and
2023, respectively. His research interests include
depth estimation and computer vision.

Rui Xu (Member, IEEE) received the Ph.D. degree
from the Graduate School of Science and Engineering, Ritsumeikan University, Japan, in 2007. He was
with the Digital Technology Research Center, Sanyo
Electric Company Ltd., Japan, from 2008 to 2010.
He was a Senior Researcher with Yamaguchi University and Ritsumeikan University from 2010 to 2015.
Since December 2015, he has been an Associate
Professor with Dalian University of Technology. His
research interests include intelligent computing in
medical images and computer vision.
PAPER_TEXT
