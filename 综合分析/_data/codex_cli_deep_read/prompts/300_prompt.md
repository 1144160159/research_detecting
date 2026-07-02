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
# [300] Self-Supervised Masked Convolutional Transformer Block for Anomaly Detection
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
编号：300
题名：Self-Supervised Masked Convolutional Transformer Block for Anomaly Detection
年份：2023
DOI：10.1109/tpami.2023.3322604
来源：IEEE Transactions on Pattern Analysis and Machine Intelligence
PDF：paper/10.1109_TPAMI.2023.3322604.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测、多媒体、医学、遥感与视频异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\300.txt
- 原始字符数：98556
- 本次发送字符数：98556
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

525

Self-Supervised Masked Convolutional Transformer
Block for Anomaly Detection
Neelu Madan , Nicolae-Cătălin Ristea , Radu Tudor Ionescu , Member, IEEE, Kamal Nasrollahi ,
Fahad Shahbaz Khan , Senior Member, IEEE, Thomas B. Moeslund , and Mubarak Shah , Life Fellow, IEEE

Abstract—Anomaly detection has recently gained increasing attention in the field of computer vision, likely due to its broad set
of applications ranging from product fault detection on industrial
production lines and impending event detection in video surveillance to finding lesions in medical scans. Regardless of the domain,
anomaly detection is typically framed as a one-class classification
task, where the learning is conducted on normal examples only.
An entire family of successful anomaly detection methods is based
on learning to reconstruct masked normal inputs (e.g. patches,
future frames, etc.) and exerting the magnitude of the reconstruction error as an indicator for the abnormality level. Unlike other
reconstruction-based methods, we present a novel self-supervised
masked convolutional transformer block (SSMCTB) that comprises the reconstruction-based functionality at a core architectural
level. The proposed self-supervised block is extremely flexible,
enabling information masking at any layer of a neural network
and being compatible with a wide range of neural architectures.
In this work, we extend our previous self-supervised predictive
convolutional attentive block (SSPCAB) with a 3D masked convolutional layer, a transformer for channel-wise attention, as well
Manuscript received 24 April 2023; revised 14 September 2023; accepted
4 October 2023. Date of publication 6 October 2023; date of current version
5 December 2023. This work was supported in part by Romanian Ministry of
Education and Research, CNCS - UEFISCDI, project no. PN-III-P2-2.1-PED2021-0195 under Grant 690/2022, within PNCDI III, in part by NO Grants 20142021, project ELO-Hyp under Grant 24/2020, in part by Milestone Systems
through the Milestone Research Programme at AAU, and in part by SecurifAI.
Recommended for acceptance by A. B. Chan. (N. Madan and N. C. Ristea
contributed equally.) (Corresponding author: Radu Tudor Ionescu.)
Neelu Madan is with the Center for Research in Computer Vision (CRCV),
Department of Computer Science, University of Central Florida, Orlando,
FL 32816 USA, and also with the Department of Architecture, Design,
and Media Technology, Aalborg University, 9220 Aalborg, Denmark (e-mail:
nema@create.aau.dk).
Nicolae-Cătălin Ristea is with the Department of Telecommunications, University Politehnica of Bucharest, 060042 Bucureşti, Romania, and also with the
Department of Computer Science, University of Bucharest, 060042 Bucureşti,
Romania (e-mail: r.catalin196@yahoo.ro).
Radu Tudor Ionescu is with SecurifAI, 105100 Azuga, Romania, and also
with the Department of Computer Science, University of Bucharest, 060042
Bucureşti, Romania (e-mail: raducu.ionescu@gmail.com).
Kamal Nasrollahi is with Department of Architecture, Design, and Media
Technology, Aalborg University, 9220 Aalborg, Denmark, and also with Milestone Systems, 2605 Brondby, Denmark (e-mail: kn@create.aau.dk).
Fahad Shahbaz Khan is with the Mohamed bin Zayed University of Artificial
Intelligence (MBZUAI), Masdar City 50819, UAE, and also with Linköping
University, 58183 Linköping, Sweden (e-mail: fahad.khan@liu.se).
Thomas B. Moeslund is with the Department of Architecture, Design,
and Media Technology, Aalborg University, 9220 Aalborg, Denmark (e-mail:
tbm@create.aau.dk).
Mubarak Shah is with the Center for Research in Computer Vision (CRCV),
Department of Computer Science, University of Central Florida, Orlando, FL
32816 USA (e-mail: shah@crcv.ucf.edu).
We release our code and data as open source at: https://github.com/ristea/
ssmctb.
Digital Object Identifier 10.1109/TPAMI.2023.3322604

as a novel self-supervised objective based on Huber loss. Furthermore, we show that our block is applicable to a wider variety of
tasks, adding anomaly detection in medical images and thermal
videos to the previously considered tasks based on RGB images
and surveillance videos. We exhibit the generality and flexibility
of SSMCTB by integrating it into multiple state-of-the-art neural
models for anomaly detection, bringing forth empirical results that
confirm considerable performance improvements on five benchmarks: MVTec AD, BRATS, Avenue, ShanghaiTech, and Thermal
Rare Event.
Index Terms—Abnormal event detection, anomaly detection,
attention mechanism, masked convolution, self-attention, selfsupervised learning, transformer.

I. INTRODUCTION
HE applications of vision-based anomaly detection are
very diverse, ranging from industrial settings, where the
need is to detect faulty objects in the production line [1], [2],
to video surveillance, where the need is to detect abnormal
behavior [3] such as people fighting or shoplifting, and even
medical imaging, where the need is to detect abnormal tissue [4]
such as malignant lesions. One of the major challenges of the
anomaly detection task is that the definition of what represents
an anomaly implies a high dependence on context. For instance,
a car driven in a pedestrian area is labeled as anomalous, whereas
the same action can be considered normal in a different context,
e.g. when the car is driven on the road. Due to the reliance on
context and the sheer diversity of possible anomalies, it is often
very difficult to gather abnormal examples for training. As a
result, anomaly detection is commonly devised as a one-class
classification task, where the generic approach implicitly or explicitly learns the distribution of the normal training data. During
inference, examples that do not belong to the normal training
data distribution are labeled as abnormal. There are several
categories of methods that are guided by this generic approach,
such as dictionary-learning methods [5], [6], [7], [8], [9], [10],
change-detection frameworks [11], [12], [13], [14], distancebased models [15], [16], [17], [18], [19], [20], [21], [22], [23],
[24], [25], [26], [27], probabilistic frameworks [28], [29], [30],
[31], [32], [33], [34], [35], [36], [37], and reconstruction-based
models [3], [38], [39], [40], [41], [42], [43], [44], [45], [46],
[47], [48].
Our approach belongs to the category of reconstruction
methods, which have recently become a prominent choice in
anomaly detection [38], [39], [41], [43], [44], [46], [47], [48].
Reconstruction-based models implicitly learn the normal data

T

0162-8828 © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

526

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

Fig. 1. Overview of our self-supervised masked convolutional transformer block (SSMCTB). At every location where the masked filters are applied, the proposed
block has to rely on the visible regions (sub-kernels) to reconstruct the masked region (center area). A transformer module performs channel-wise self-attention
to selectively promote or suppress reconstruction maps via a set of weights returned by a sigmoid (σ) layer. The block is self-supervised via the Huber loss
(LSSMCTB ) [49] between masked and returned activation maps. Best viewed in color.

distribution by minimizing the reconstruction error of the normal instances at training time. These models are based on the
assumption that the learned latent manifold does not offer the
means to reconstruct the abnormal samples robustly, due to
the unavailability of such samples at training time. Hence, the
reconstruction error is directly employed as the anomaly score.
A particular subcategory of reconstruction-based models relies
on learning to predict masked inputs [41], [42], [50], [51] as
a self-supervised pretext task. In this case, the reconstruction
error with respect to the masked information is used to assess
the abnormality level of an input instance. Depending on the
input type (image or video), methods in this subcategory mask
various parts of the input, e.g. superpixels in images [41], future
frames in video [42], or middle bounding boxes in object-centric
temporal sequences [50], [51], and employ the whole model to
reconstruct the masked input. We, on the other hand, propose
to encapsulate the functionality of reconstructing the masked
information into a novel neural block. There are two major
benefits when wrapping the reconstruction task as a low-level
architectural component: (i) it enables introducing the reconstruction of masked information as a self-supervised task at any
layer of a neural network (not only at the input), and (ii) it
eases integrating the self-supervised reconstruction task into a
broad variety of neural architectures, regardless of whether the
respective models are reconstruction-based or not. Due to its
advantages, our block is very flexible and generic.
Our self-supervised reconstruction block consists of a dilated
masked convolution followed by a channel-wise transformer
module. The center area of our convolutional kernel is masked,
hence hiding the center of the receptive field at every location
where the filters are applied. In other words, each component
of the input tensor is certainly masked at some point during
the convolution operation, which means that the entire input
tensor ends up being masked. Next, the convolutional activation
maps are transformed into tokens using an average pooling layer.
Then, the resulting tokens are passed through a transformer

module [52], [53] that performs channel-wise self-attention.
The proposed block is equipped with a transformer module
to avoid the direct reconstruction of the masked area through
linearly interpolating the visible regions of the convolutional
kernels. The final activation maps are multiplied with the resulting attention tokens. Our block is designed in such a way
that the output tensor has the same dimensions as the input
tensor, which allows us to easily introduce a loss within our
block to minimize the reconstruction error between the output
tensor and the masked input tensor. By integrating this loss,
our block becomes a self-contained trainable component that
learns to predict the masked information via self-supervision.
As such, we coin the term self-supervised masked convolutional
transformer block (SSMCTB) to designate our novel neural
component for anomaly detection. As shown in Fig. 1, SSMCTB
learns to reconstruct the masked region based on the available
context (visible regions of the receptive field), for each location
where the dilated kernels are applied. Notably, we can graciously
control the level (from local to global) of the contextual information by choosing the appropriate dilation rate for the masked
kernels.
SSMCTB is an extension of the self-supervised predictive
convolutional attentive block (SSPCAB) introduced in our recent CVPR 2022 paper [54]. In the current work, we modify
SSPCAB in three different ways: (i) we replace the standard
channel attention module in the original SSPCAB [54] with
a multi-head self-attention module [52], [53] to increase the
modeling capacity, (ii) we extend the masked convolution operation with 3D convolutional filters, enabling the integration
of SSMCTB into networks based on 3D convolutional layers,
and (iii) we replace the mean squared error (MSE) loss with the
Huber loss [49], since the latter loss is less sensitive to outliers
than the former loss. Aside from these architectural changes,
we demonstrate the applicability of our block to more domains,
adding anomaly detection in medical images and thermal videos
to the previously considered tasks based on RGB images and

MADAN et al.: SELF-SUPERVISED MASKED CONVOLUTIONAL TRANSFORMER BLOCK FOR ANOMALY DETECTION

surveillance videos. Moreover, we conduct a more extensive
ablation study, thus providing a more comprehensive set of
results. We also show that our module is suitable for both
convolutional and transformer-based architectures.
We introduce SSMCTB into multiple state-of-the-art neural
models [42], [44], [55], [56], [57], [58], [59], [60], [61], [62] for
anomaly detection and conduct experiments on five benchmarks:
MVTec AD [1], BRATS [63], Avenue [9], ShanghaiTech [3],
and Thermal Rare Event. The Thermal Rare Event data set is a
novel benchmark for anomaly detection, which we constructed
by manually labeling abnormal events from the Seasons in Drift
data set [64]. The chosen benchmarks belong to various domains,
ranging from industrial and medical images to RGB and thermal
videos. This is to show that SSMCTB is applicable to multiple
domains. When adding SSMCTB to the state-of-the-art models,
our experiments show evidence of consistent improvements
across all models and tasks, indicating that our block is generic
and easily adaptable. When compared to SSPCAB, we observe
performance gains in the majority of cases, showing that the
multi-head self-attention and the Huber loss are beneficial in
detriment of the standard channel attention [65] and the MSE
loss, respectively.
In summary, our contribution is multifold:
r We introduce the masked convolution operation and integrate it into a novel self-supervised masked convolutional
transformer block which exhibits the inherent ability to
detect anomalies.
r We encapsulate our block into several state-of-the-art
methods [42], [44], [55], [56], [57], [58], [59], [60], [61],
[62] for anomaly detection, showing considerable performance gains across multiple models, benchmarks and
domains.
r We extend the 2D masked convolution to a 3D masked
convolution that considers a 3D context, and we integrate
the new 3D SSMCTB into two 3D networks for anomaly
detection [55], [56].
r We replace the Squeeze-and-Excitation module [65]
of SSPCAB with a transformer module that performs
channel-wise attention.
r We substitute the MSE loss in SSPCAB with the Huber loss, improving the sensitivity to outliers during selfsupervised learning.
r We conduct a more comprehensive set of experiments,
including new methods and benchmarks from previously
missing domains (medical images, thermal videos).
r We provide an extensive ablation study, including different
variations of the proposed self-supervised block.
r We annotate a subset (one week of video) of the Seasons
in Drift [64] data set with anomaly labels, obtaining a new
benchmark for anomaly detection in thermal videos.
II. RELATED WORK
A. Transformers
Vaswani et al. [53] introduced the self-attention mechanism,
sparking the research of neural architectures relying solely on

527

attention, including research on vision transformers [52], [66],
[67], [68], [69], [70], [71], [72], [73], [74], [75], [76]. These
models are now embraced at a fast pace in the field of computer
vision, certainly due to the imposing performance levels across
a broad variety of tasks, ranging from object recognition [52],
[71], [72] and object detection [66], [75], [76] to image generation [70], [73], [74] and anomaly detection [62], [77], [78],
[79], [80]. Unlike approaches using only transformer-based
attention [52], [66], [67], [68], [69], [70], [71], [72], [75],
[76], [81], we propose a novel and flexible block that employs
transformer-based attention along with masked convolution,
which can be integrated into multiple architectures that are not
necessarily transformer-based. To endorse this statement, we
introduce SSMCTB into a variety of models and conduct a series
of experiments showing that our block can bring significant
performance gains. Another difference from vision transformers
is that our block performs channel-wise self-attention, while
conventional vision transformers perform spatial attention [52].
We conduct an ablation study to compare channel and spatial
attention inside SSMCTB, showing that channel attention provides superior performance and faster processing.
B. Self-Supervision Via Information Masking
The reconstruction of masked information has recently become an attractive area of interest [60], [82], [83], [84], [85].
Models based on information masking are usually pre-trained
on a self-supervised reconstruction task, being later employed
for downstream visual tasks such as object detection and image
segmentation. For instance, He et al. [60] proposed to reconstruct
masked (erased) patches as a self-supervised pretext task for
pre-training auto-encoders, subsequently using them for mainstream tasks, including object detection and object recognition.
They reported optimal results when a majority (75%) of the
patches is masked. Masked auto-encoders are directly applicable
to anomaly detection. However, we show that SSMCTB can
boost the performance of masked auto-encoders, suggesting
that it can leverage information masking in a distinct way.
Wei et al. [83] aimed at pre-training video models, proposing
to mask spatio-temporal cubes from a video and predict the
features of the masked regions. Chang et al. [84] introduced
a bidirectional decoder that learns to predict masked tokens
by attending them from all directions. The proposed method
provides an efficient substitute for generative transformers. Yu
et al. [85] used a masked point modeling task for pre-training
a point cloud transformer. They showed that the representation learned by the model transfers well to new (downstream)
tasks and domains. Distinct from such methods, we integrate
information masking at a core operational level inside neural
networks via our masked convolutional layer. We self-supervise
our block (which incorporates masked convolution) through a
reconstruction loss and show that modeling the context towards
reconstructing the masked information results in an effective
discriminative manifold for anomaly detection.
We underline that some recent approaches [42], [50], [86]
utilize masking as a surrogate task for anomaly detection. We

528

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

discuss these methods and explain how our approach is different
in a separate subsection below.
C. Anomaly Detection
Anomaly detection frameworks are usually trained in a oneclass setting, where only normal data is available at training time,
whereas both normal and abnormal examples are present at test
time. The anomaly detection methods operating in this setting
can be classified into different categories, which are briefly
presented below. Dictionary learning methods [5], [6], [7], [8],
[9], [10] construct a dictionary of atoms from normal instances,
labeling examples that are not represented in the dictionary as
abnormal. Change detection frameworks [11], [12], [13], [14]
are applied directly on test videos, measuring the degree of
change between current and preceding video frames to detect
anomalies. Probabilistic models [28], [29], [30], [31], [32], [33],
[34], [35], [36], [37] learn the probability density function of
the normal data, flagging examples outside the distribution as
abnormal. Distance-based approaches [15], [16], [17], [18], [19],
[20], [21], [22], [23], [24], [25], [26], [27], [87] learn a distance
function between samples, such that the distance between normal instances is lower than the distance between normal and
abnormal instances. Reconstruction-based methods [3], [38],
[39], [40], [41], [42], [43], [44], [45], [46], [47], [48], [56], [88]
learn to reconstruct normal examples, detecting anomalies based
on the magnitude of the reconstruction error, as anomalies tend
to have larger errors than normal instances.
Reconstruction-based methods: Since our block belongs to
the category of reconstruction-based models, we discuss this
category in more detail next. Reconstruction-based models
are often chosen for both image and video anomaly detection [44], [50], [56], [59]. These approaches typically employ
auto-encoders and generative adversarial networks (GANs) to
learn a powerful latent manifold representing the normal data
distribution. For the video domain, some anomaly detection
approaches [17], [42], [59] incorporate additional cues by reconstructing the optical flow to capture motion information, enabling the detection of motion-based anomalies such as running
and jumping. Doshi et al. [89] proposed a continual learning
setup, which could be easily extended for future normal and
abnormal patterns.
As the amount of normal training data is generally high, latent
manifolds show a tendency to generalize too well, being capable
of reconstructing abnormal instances with low error. In the
context of anomaly detection, generalizing to out-of-distribution
samples, e.g. anomalies, is not desired, although this would be
mostly desirable in other application domains. To mitigate this
issue, researchers employed various techniques, such as adding
memory modules [39], [44], [59] or pseudo-anomalies during
training [58], [86]. Memory-based auto-encoders [39], [59]
generally employ an additional module to memorize the normal
patterns observed in the training data. Consequently, memory
modules increase the computational complexity of the model,
and the faithful reconstruction of normal samples highly relies on
the size of the memory module. Georgescu et al. [58] proposed to
optimize the model on pseudo-anomalies with gradient ascent,

while still using gradient descent to learn the normal data distribution. This results in a powerful discriminative subspace for the
robust detection of the abnormal samples. The pseudo-abnormal
instances are samples collected from different contexts, such as
flowers, animals, cartoons, and textures, unrelated to the object
distribution (comprising humans, cars, bicycles, etc.) observed
in typical urban surveillance scenes. Similarly, Astrid et al. [86]
generated pseudo-anomalies by skipping a few frames from
the video and training an auto-encoder by maximizing the loss
for pseudo-anomalies and minimizing it for normal samples.
Introducing pseudo-anomalies increases the training time and
may sometimes cause instability if the balance between gradient
descent on normal data and gradient ascent on pseudo-abnormal
data is not tuned. Different from related reconstruction-based
methods, we increase the difficulty of the reconstruction task by
masking information wherever SSMCTB is introduced into a
neural model, thus making it harder for the model to generalize
to abnormal data. As shown by our experimental results, our
block adds a marginal computational overhead.
Masking for Anomaly Detection: Some approaches [38], [42],
[50], [77], [80], [90], [91], [92] are already using the prediction
of masked inputs as a surrogate task for anomaly detection.
These models form a distinctive subcategory of reconstructionbased methods. Liu et al. [42] proposed a GAN for predicting
a future frame based on a few past frames, where anomalies
are classified according to the prediction error. Another GANbased approach [93] performs joint detection and localization of
anomalies via inpainting. The generator of this method learns
to inpaint a patch from the input image, while the discriminator
learns to identify if the inpainted patch is normal or abnormal.
Interestingly, the inpainting task has also been studied in conjunction with vision transformers [80].
Generalizing over the method of Liu et al. [42], Yu et al. [92]
employed the Cloze task [94], which is about learning to complete the video when certain frames are removed. Georgescu et
al. [50] proposed the masking of the middle box of each temporal
cube centered on an object. Anomalies are detected based on the
assumption that motion reconstruction for an abnormal object is
more difficult than for the normal ones. Fei et al. [38] proposed
the Attribute Restoration Network (ARNet), where attributes
such as color and orientation of the input are removed, and the
network learns to restore those attributes. The idea is based on the
assumption that the anomalous data can be distinguished based
on the restoration error. Haselmann et al. [90] introduced an
approach for surface anomaly detection by erasing a rectangular
box from the center of the image and using the interpolation
error for the classification of samples into normal or abnormal.
Inspired by the success of masked auto-encoders [60], Jiang et
al. [77] proposed a masked Swin Transformer [95] that is trained
to inpaint masked regions. To cope with the lack of abnormal
samples during training, the authors used simulated anomalies.
Ristea et al. [91] employed self-distilled masked auto-encoders
to reach an unprecedented level of time efficiency.
Unlike other models based on information masking, we propose a novel approach that incorporates the reconstruction-based
functionality into a single neural block, which can be easily
integrated into other state-of-the-art anomaly detection models.

MADAN et al.: SELF-SUPERVISED MASKED CONVOLUTIONAL TRANSFORMER BLOCK FOR ANOMALY DETECTION

529

Our experimental results confirm that our block is a valuable
addition to various models, including both CNNs and transformers, which are applied to anomaly detection in a wide range of
domains.
III. METHOD
A. Motivation and Overview
A wide set of computer vision tasks, including anomaly
detection [44], [58], [59], [96], [97], are often addressed with
convolutional neural networks (CNNs) [98], [99], due to the impressive performance levels reached by these models, sometimes
even surpassing human-level accuracy. The defining component
of a CNN architecture is the convolutional layer, which typically
comprises multiple filters (kernels) that activate on discriminative local patterns captured within the receptive field of the
respective filters. Each filter produces an activation map that is
further given as input to the next convolutional layer. Since each
filter in the subsequent layer processes all activation maps from
the previous layer at once, the local features extracted by the
previous layer are combined into more complex features. This
sequential processing of features over multiple convolutional
layers gives rise to a hierarchy of features during the learning process. Earlier convolutional layers activate on low-level
features such as corners or edges, and later layers gradually
shift to higher-level features such as car wheels or human body
parts, as shown by Zeiler et al. [100]. Although the learned
hierarchy of features is very useful in solving discriminative
tasks, CNNs do not have the direct means to model the global
arrangement of local features [101], since they do not generalize
well to novel viewpoints or affine transformations [102]. The
inability of grasping the global arrangement of local features is
mainly caused by the fact that convolutional filters operate on a
limited (and typically small) receptive field, not making use of
the context.
We hereby propose a self-supervised masked convolutional
transformer block (SSMCTB), which is aimed at learning to
reconstruct masked information based on contextual information. To accurately solve the reconstruction of its masked input,
the proposed block is required to employ the context and learn
the global structure of the local patterns. Hence, it inherently
learns to cope with the problem stated by Sabour et al. [101],
specifically the fact that CNNs lack the proper comprehension
of the global arrangement of local features. To embed this
learning capability into our block, we structure SSMCTB as
a convolutional layer with dilated masked kernels, followed
by a transformer module that performs channel attention. We
attach a self-supervised loss function to our block in order to
minimize the reconstruction error between the masked input and
the predicted output.
We emphasize that SSMCTB is quite flexible, since it can
be inserted at any level of almost any CNN or transformer
model, generating powerful features that offer the capability
of reconstructing masked information based on context. While
the ability of learning and harnessing the global arrangement
of local patterns is potentially useful in solving a broader set
of computer vision tasks, we conjecture that anomaly detection

Fig. 2. Our 2D masked convolutional kernel. The visible area of the receptive
field is denoted by the regions K i , ∀i ∈ {1, 2, 3, 4}, while the masked area is
denoted by M . A dilation factor d controls the local or global nature of the
visible information with respect to M . Best viewed in color.

is a natural and immediate application domain for SSMCTB,
hence focusing our work in this direction. Indeed, since anomaly
detection models are typically trained on normal data only, integrating SSMCTB into a neural model will lead to the learning of
features that recover only masked normal data. Hence, when an
anomalous sample is given as input during inference, SSMCTB
is likely less capable of reconstructing the masked information.
This empowers the model to directly estimate the abnormality
level of a data sample via the reconstruction error given by SSMCTB. Our claims are supported through the comprehensive set
of experiments on image and video anomaly detection presented
in Section IV.
B. Architecture
Our initial self-supervised block introduced in [54] was
formed of a 2D masked convolution and a Squeeze-andExcitation (SE) module [65]. To broaden the applicability of
our block, we now introduce a 3D masked convolutional layer
to replace the 2D masked convolution, whenever this is needed.
Moreover, we replace the SE attention module with a modern transformer-based attention module [52], [53] to attend to
the channels given as output by the masked convolution. We
describe the individual components of our block below, while
providing a graphical overview of SSMCTB in Fig. 1.
2D Masked Convolution: Fig. 2 shows our 2D masked convolutional kernel, where the corner regions of this kernel (in green
color) are the learnable parameters (weights) defining the visible
regions of the receptive field. The four learnable sub-kernels are


denoted by K i ∈ Rk ×k ×c , ∀i ∈ {1, 2, 3, 4}, where the spatial

+
size k ∈ N of each sub-kernel is a hyperparameter of our
block, while the number of channels c ∈ N + always matches
the number of channels of the input tensor. Our masked region
M ∈ R1×1×c (in pink color) is located at the center of the
receptive field. Each sub-kernel K i is located at a configurable
distance d ∈ N + (also referred to as dilation rate) from the
masked region M . To keep the number of hyperparameters to
a bare minimum, we fix the spatial size of the masked region to
1 × 1. As a result, the spatial size k of the entire receptive field
of our 2D masked convolution is k = 2 · k  + 2 · d + 1.
Let X ∈ Rh×w×c be the input tensor of the masked convolutional layer, where c ∈ N + denotes the number of channels, and

530

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

Fig. 3. Our 3D masked convolutional kernel. The visible area of the receptive
field is denoted by the regions K i , ∀i ∈ {1, 2, . . ., 8}, while the masked area
is denoted by M . A dilation factor d controls the local or global nature of the
visible information with respect to M . Best viewed in color.

h, w ∈ N + represent the height and width of the input tensor, respectively. When we apply our custom kernel at a given location
(a, b) of the input tensor X, only the input values that overlap
with the sub-kernels K i are taken into consideration during
the masked convolution operation, resulting in a single output
value. We underline that our masked convolution is equivalent
to convolving the input independently with the sub-kernels K i ,
where each sub-kernel has a different spatial shift with respect to
the current location (a, b), and the resulting values are summed
up to produce a single output value. The output value at position
(a, b) represents the reconstruction for only one value of the
tensor M located at the same position (a, b). To reconstruct the
entire tensor M , our layer requires the application of c masked
convolutional filters, each reconstructing the masked value from
a distinct channel at position (a, b). Convolving a single masked
filter over the entire input generates a complete activation map.
Since there are c masked convolutional filters, the output tensor
Z is formed of c activation maps. Our aim is to apply the masked
convolution such that every element in the input tensor is masked
exactly once, i.e. we want to mask and predict the reconstruction
for every spatial location of the input. As such, we set the stride
to 1 and apply a zero-padding of k  + d in each direction. With
this configuration in place, the output tensor Z has h × w × c
components, exactly as the input tensor X. To obtain the final
values, the output tensor Z is passed through Rectified Linear
Units (ReLU) [103]. Finally, we emphasize that k  and d are
the only tunable hyperparameters of our masked convolutional
layer.
3D Masked Convolution: Considering that anomaly detection
is often applied on 3D inputs, e.g. video or medical scans, some
researchers naturally resort to employing 3D CNNs. To this
end, we extend our 2D masked convolution to the 3D domain,
broadening the applicability of SSMCTB. We thus reformulate
the 2D spatial reconstruction task into a more difficult one,
which implies learning a global 3D structure of the discovered



local patterns. Let K i ∈ Rk ×k ×k ×c , ∀i ∈ {1, 2, . . ., 8}, be the
learnable 3D sub-kernels depicted in Fig. 3, where k  and c are

defined above. The masked region M is located in the center of
the 3D kernel, equally distant from the sub-kernels K i . The size
of the receptive field of our 3D masked convolution is k × k × k,
where k = 2 · k  + 2 · d + 1.
To compute the feature response using the 3D masked convolutional layer, the input X ∈ Rh×w×r×c is convolved with our
custom masked kernel, where r represents the depth, and h, w
and c are defined as before. The 3D filter is applied analogously
to the 2D one, the only difference being that the input data and
the kernel itself are 3D. The number of 3D convolutional filters is
equal to the number of channels c, such that the spatial dimension
of the output tensor Z ∈ Rh×w×r×c is identical to that of the
input X. The 3D masked convolution has the same number of
configurable hyperparameters, these being k  and d.
Channel-wise transformer block: To better exploit the interdependencies between the different activation maps produced
by the masked convolutional layer, we replace the Squeezeand-Excitation module in SSPCAB [54] with a self-attention
transformer-based module. The new attention module is able
to capture more complex channel-wise interrelations through its
higher modeling capacity, as it learns to assign attention weights
to the reconstructed information corresponding to each masked
convolutional filter in order to reduce the reconstruction error of
SSMCTB.
Let Z ∈ Rh×w×c be the output tensor of a 2D masked convolutional layer with c filters. First, we apply a spatial average


pooling, obtaining Ẑ ∈ Rh ×w ×c , where h ≤ h and w ≤ w.
The average pooling layer is followed by a reshape operation,
obtaining a matrix A ∈ Rc×n , which contains a vector of n =
h · w components on each row to represent each masked filter.
Next, A is fed into a linear projection layer to obtain the tokens
T ∈ Rc×dt , which are further summed up with the positional
embeddings to obtain the final tokens T ∗ ∈ Rc×dt .
Let f be a multi-head attention layer with H ∈ N + heads, g a
multi-layer perceptron, norm a normalization layer, and P , R ∈
Rc×dt some auxiliary tensors. The operations performed inside
the transformer are formally described as follows:
P = f (norm(R)) + R,

(1)

R = g(norm(P )) + P .

(2)

As illustrated in Fig. 1, the whole process described in (1) and
(2) is repeated L times, where L ∈ N + represents the number
of transformer blocks inside the transformer module. For the
first transformer block, R is initialized with T ∗ . In (1), the
sequence of c tokens R is normalized, fed into the multi-head
attention layer and added to itself, obtaining P . Further, P is
normalized, fed into a multi-layer perceptron and also added to
itself, according to (2).
The transformer is aimed at capturing the interaction among
all c tokens by encoding each token in terms of the channel-wise
contextual information. This is achieved via the multi-head
attention layer f . Each head j ∈ {1, 2, . . ., H} comprises three
learnable weight matrices denoted as W Qj ∈ Rdt ×dq , W Kj ∈
Rdt ×dk and W Vj ∈ Rdt ×dv , where dq = dk . The weight matrices are multiplied with the input tokens R, producing the
queries Qj , keys K j and values V j . In other words, the input

MADAN et al.: SELF-SUPERVISED MASKED CONVOLUTIONAL TRANSFORMER BLOCK FOR ANOMALY DETECTION

sequence R is projected onto these weight matrices to get Qj =
R · W Qj , K j = R · W Kj and V j = R · W Vj , respectively.
The output Y j ∈ Rc×dv of each self-attention head is given by:


Qj · K 
j

(3)
· V j,
Y j = sof tmax
dq
where K 
j is the transpose of K j . The outputs returned by the
self-attention heads are simply summed into Y , i.e.:
Y =

H


Y j.

(4)

j=1

We can now rewrite (1) as follows:
P = Y + R.

(5)

The output sequence R returned by the final transformer block is
averaged along the token dimension, obtaining R̂ ∈ Rc×1 , then
fed into a sigmoid layer to generate the final attention weight
assigned to each channel. Finally, the resulting attention weights
are applied to the tensor Z, obtaining the reconstructed output
denoted by X̂ ∈ Rh×w×c , as follows:
X̂ = Z ⊗ σ(R̂),

(6)

where ⊗ denotes the element-wise multiplication, and σ denotes
the sigmoid layer. The entire processing performed by the transformer module is analogously applied when the preceding layer
is a 3D masked convolution.
C. Self-Supervised Reconstruction Loss
We devise an integrated reconstruction loss to train the proposed SSMCTB in a self-supervised manner. To better cope
with outlier values and reduce the sensitivity of the model to
outliers, we define the self-supervised objective as the Huber
loss between the reconstructed output X̂ and the input X,
replacing the mean squared error (MSE) used by SSPCAB. The
self-supervised objective enables our model to learn reconstructing the masked information at every location where the masked
filters are applied. Let G denote the SSMCTB function. With this
notation, the self-supervised reconstruction loss of our block can
be computed as follows:
1
·(G(X)−X)2 , 
if |G(X)−X| < δ
LSSMCTB (G, X) = 2 
δ· |G(X)−X|− 2δ , otherwise
⎧
2
⎨ 1 · X̂ −X ,
if |X̂ −X| < δ
2
, (7)
=
δ
⎩δ· |X̂ −X|− , otherwise
2

where δ ∈ R+ is a hyperparameter representing the error threshold that determines when to switch from the squared loss (applied for errors below δ) to the absolute loss (applied for errors
higher than or equal to δ).
When integrating SSMCTB into some neural network F , we
can simply add our loss LSSMCTB to the loss function LF of the
respective neural model, resulting in a new loss function comprising both terms. Formally, the overall loss can be computed

531

as follows:
Ltotal = LF + λ · LSSMCTB ,

(8)

where λ ∈ R+ is a hyperparameter deciding the importance of
LSSMCTB with respect to LF . Naturally, the hyperparameter λ
can vary across neural models or visual tasks.
IV. EXPERIMENTS AND RESULTS
A. Data Sets
We carry out experiments on five benchmarks from various domains, considering the most popular data set choices,
e.g. MVTec AD [1], BRATS [63], CUHK Avenue [9], ShanghaiTech [3], whenever such an option is available for a certain
domain. For the thermal video domain, we build our own data
set.
MVTec AD: MVTec AD [1] has become a standard data
set for benchmarking anomaly detection methods applied in
inspecting industrial defects. The data set contains over 5,000
images distributed over 15 different categories of textures (10)
and objects (5). It comprises 3,629 defect-free training samples,
as well as 1,725 test images with and without defects.
BRATS: BRATS [63] is a multimodal magnetic resonance
imaging (MRI) data set for brain tumor segmentation. It is
an intrinsically heterogeneous data set that contains brain tumors of different shape, appearance and histology. The data
set comprises manually annotated MRI scans acquired by 19
institutions employing different clinical protocols. To evaluate
anomaly detection models, we introduce a novel split of the data
set, such that all training images are lesion-free, i.e. all images
with lesions are kept for testing. The training set includes 11,280
slices (125 scans), which leaves 27,745 slices (180 scans) for the
test set.
Avenue: CUHK Avenue [9] is one of the most widely-used
data sets for video anomaly detection. It contains 16 videos for
training and 21 videos for testing. The training videos comprise
only normal events, whereas the test videos contain both normal
and abnormal events. The data set contains videos from a single
surveillance camera. Avenue contains people-related anomalies
such as running, walking in the wrong direction, jumping, dancing, loitering and throwing objects.
ShanghaiTech: ShanghaiTech [3] is one of the largest benchmarks for video anomaly detection, comprising 330 training
and 107 test videos. As in CUHK Avenue, abnormal instances
appear only at test time. The data set includes videos from
multiple scenes. Examples of anomalies are related to people,
e.g. fighting, jumping and stealing, as well as vehicles, e.g. bikes
and cars in pedestrian (forbidden) zones.
Thermal Rare Event: To construct the Thermal Rare Event
data set, we sampled one week of videos (330 clips) from the
Seasons in Drift (SiD) data set [64]. The SiD data set [64] is an
unlabeled thermal surveillance data set captured from a single
view over a period of 8 months. The data set captures activities
near a harbor front during day and night. Each clip is about 2
minutes long and contains 120 frames, being sampled at 1 frame
per second (FPS). Out of the 330 clips, there are 29 clips containing rare (anomalous) events. We manually annotated these

532

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

TABLE I
RARE EVENTS IN OUR THERMAL ANOMALY DETECTION DATA SET ALONG
WITH THE FREQUENCY OF EACH EVENT TYPE

the intersection over union (IOU) between the detected and the
ground-truth anomalous region is greater than α. TBDC marks
each tracked region as a true positive if the overlap with the
ground-truth anomalous track is greater than β. We set the same
values for α and β as previous works [19], [58], i.e. α = 0.1 and
β = 0.1.
C. Implementation Details

rare events at the frame level. In total, our Thermal Rare Event
data set contains 36,120 frames for testing and 3,480 frames for
training. The list of rare events in our data set along with their
respective frequencies are summarized in Table I. Examples of
rare events from different categories are: activities in restricted
zones (people sitting, standing, and running close to the pier),
jumping (person jumping, group jumping), unexpected activities
(doing yoga, smoking), unexpected interactions (running with
stroller, embarking to a boat, debarking from a boat, chasing,
dancing), unexpected vehicles (different types of trucks). We
release the Thermal Rare Event data set along with our code at:
https://github.com/ristea/ssmctb/.
B. Evaluation Measures
Image Anomaly Detection: Following Bergmann et al. [1], we
carry out the evaluation on MVTec AD and BRATS considering the area under the receiver operating characteristics curve
(AUROC) and the average precision (AP). To generate the ROC
curve, the true positive rate (TPR) is plotted against the false
positive rate (FPR). We evaluate both detection and localization
performance levels of anomaly detection methods. In anomaly
detection, TPR is the proportion of images correctly classified as
abnormal, and FPR is the proportion of normal images wrongly
classified as abnormal. For the localization task, TPR denotes
the proportion of correctly classified abnormal pixels, while FPR
represents the proportion of normal pixels incorrectly classified
as abnormal. For the localization task, we obtain anomaly segments by applying a threshold to produce a binary decision for
each pixel, as described in [1]. The localization AP is obtained
by taking the mean at different threshold levels.
Video Anomaly Detection: As the majority of previous
works [104], we evaluate the detection performance of video
anomaly detection methods using the frame-level area under the
curve (AUC). To compute the AUC measure, a video frame is
marked as abnormal if at least one pixel is abnormal. Inspired
by Georgescu et al. [58], we employ both micro AUC and
macro AUC. The micro AUC is computed by first concatenating
all frames in all videos into a single video, while the macro
AUC represents the average of the AUC scores which are
independently computed for each single video in the test set.
To evaluate the localization performance, we report the regionbased detection criterion (RBDC) and the track-based detection
criterion (TBDC) proposed by Ramachandra et al. [19]. RBDC
considers each detected region, marking it as a true positive if

We choose ten state-of-the-art approaches [42], [44], [55],
[56], [57], [58], [59], [60], [61], [62] for image and video
anomaly detection to serve as underlying models, on top of
which we add SSPCAB [54] and SSMCTB (ours). We alternatively integrate SSPCAB and SSMCTB directly into the official implementations of the chosen baselines, while preserving
all hyperparameter values, e.g. the number of epochs and the
learning rate, as specified in the corresponding papers [42],
[44], [55], [56], [57], [58], [59], [60], [61], [62]. Even so, we
are unable to exactly reproduce the original results for two
baselines methods, i.e. those of Park et al. [44] and Liu et
al. [42]. However, our reproduced quantitative results are still
close to the originally reported results. For a fair comparison,
we compare the models based on SSPCAB and SSMCTB with
the reproduced baselines. Additionally, when we repurpose the
approach of Park et al. [44] from the RGB domain to the thermal
domain, we modify some hyperparameters, namely the number
of epochs and the mini-batch size.
Following Ristea et al. [54], we replace the penultimate convolutional layer with SSMCTB in most underlying models. One
exception is the architecture of Georgescu et al. [50], where
SSPCAB and SSMCTB are integrated into the penultimate convolutional layer of the decoder instead of the final classification
network. Another exception is the masked auto-enconder [60]
based on the ViT backbone, where we place SSPCAB and
SSMCTB before the first transformer block.
In our previous work [54], we conducted a set of preliminary
experiments to find an optimal value for the hyperparameter
λ representing the contribution of our self-supervised loss to
the total loss defined in (7), taking values from 0.1 to 1 at an
interval of 0.1. Following our previous work [54], we keep λ =
0.1 across all data sets. However, for two baselines [57], [59],
we notice that the magnitude of our loss is too high with respect
to the original losses of the respective models, dominating the
optimization. Following our previous work [54], we decrease λ
to 0.001 to reduce the dominant influence of our loss on these
two particular models [57], [59].
For the channel-wise transformer, we fix the activation map
size after the average pooling layer to 1 × 1, the token size dt
to 64, the number of heads H to 4, as well as the number of
successive transformer blocks L to 2. We discuss results for
other transformer configurations in Section IV-H.
D. Preliminary Results
We conduct a series of preliminary experiments on Avenue to
determine the hyperparameters of SSMCTB, namely the dilation
rate d and the sub-kernel size k  . We perform experiments with
d ∈ {0, 1, 2, 3} and k  ∈ {1, 2, 3}. We also consider alternative

MADAN et al.: SELF-SUPERVISED MASKED CONVOLUTIONAL TRANSFORMER BLOCK FOR ANOMALY DETECTION

TABLE II
MICRO AUC SCORES (IN %) OBTAINED ON THE AVENUE DATA SET WITH
DIFFERENT HYPERPARAMETER CONFIGURATIONS, VARYING THE KERNEL SIZE
(k ), THE DILATION RATE (d), THE LOSS TYPE, AND THE ATTENTION TYPE,
WHILE INTEGRATING SSMCTB INTO THE METHOD OF PARK ET AL. [44]

533

for the reported performance gains. To compare the losses on
the one hand, and attention types on the other, we fix k  = 1.
When alternating between MAE, MSE, SSIM and Huber as our
self-supervised loss, we generally observe higher performance
with Huber loss. We thus continue the experiments with Huber
loss. Regarding the attention type, we note that channel attention
(CA) generally leads to better results than spatial attention
(SA). Hence, for the remaining experiments, we employ the
transformer module based on channel attention. We continue by
increasing the size of the sub-kernels, without obtaining further
performance gains. We obtain the best micro AUC (86.7%) with
d = 1 and k  = 1, while using channel attention. We make another attempt to further boost the performance by combining the
channel and spatial attention (CA+SA), while fixing d = 1 and
k  = 1. This attempt is also unsuccessful. Our final SSMCTB
configuration, which we employ across all underlying models
and data sets, is based on d = 1, k  = 1 and channel attention.
We underline that the corresponding hyperparameters for
SSPCAB were tuned in a similar manner, in our previous
work [54]. Hence, we simply use the already tuned hyperparameters for SSPCAB. Importantly, we underline that our observations above are mostly consistent with those reported in our
previous work [54], i.e. both SSPCAB and SSMCTB use channel
attention, a dilation rate of d = 1 and sub-kernels of size k  = 1.
The only difference is that SSMCTB is based on the Huber loss
instead of the MSE loss. We should also emphasize that it is not
common for anomaly detection data sets to have validation splits.
Since the training set contains normal instances only, keeping a
representative training subset (with both normal and abnormal
examples) for validation is not possible. This is the reason behind
our decision to avoid hyperparameter tuning for each model and
data set. We believe that this evaluation procedure is more fair
because it avoids overfitting in hyperparameter space.

E. Anomaly Detection in Images
attention types, namely channel attention (CA), spatial attention
(SA) and both channel and spatial attention (CA+SA). Additionally, we alternate between multiple losses to self-supervise
our block, such as the mean absolute error (MAE), the mean
squared error (MSE), the Huber loss, and the Structured Similarity Index Measure (SSIM) loss. For the Huber loss, we set the
hyperparameter δ to the default value, i.e. δ = 1.
We employ the method of Park et al. [44] in our preliminary
experiments, since this is the most lightweight and unpretentious
method among the chosen ones [42], [44], [55], [56], [57], [58],
[59], [60], [61], [62]. The corresponding micro AUC scores are
presented in Table II. Except for a single SSMCTB configuration
based on spatial attention (SA), all other SSMCTB configurations bring performance improvements over the approach of
Park et al. [44] (first row). Our first set of preliminary experiments is aimed at evaluating the capacity of the standalone
masked convolution. Even without the attention module, our
masked convolution brings gains higher than 1% for d = 2 and
d = 3. While adding the attention module is definitely useful,
we conclude that it is clearly not the only factor responsible

Baselines: We introduce SSMCTB into three state-of-the-art
baselines for image anomaly detection on MVTec AD, namely
a self-supervised model based on natural synthetic anomalies
(NSA) [57], a discriminatively trained reconstruction anomaly
embedding model (DRAEM) [56], and a version of FastViT [61]
based on the T8 backbone. Since FastViT [61] is not particularly
designed for anomaly detection, we actually couple it with
NSA [57] to perform the designated task. All three baselines are
based on very recent studies, attaining strong results on MVTec
AD. The NSA approach of Shülter et al. [57] generates synthetic
anomalies using Poisson image editing, blending scaled patches
of different sizes from separate images. In this way, it generates
a wide range of synthetic anomalies that are similar to natural
irregularities. DRAEM [56] comprises a reconstructive network
and a discriminative network to detect and localize anomalies.
The reconstructive network is based on a simple auto-encoder
architecture which learns to reconstruct original images from
artificially corrupted images. The discriminative network is a
U-Net that learns to segment the introduced artifacts (corrupted
regions).

534

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

TABLE III
DETECTION AUROC AND LOCALIZATION AUROC/AP (IN %) OF THREE STATE-OF-THE-ART METHODS [56], [57], [61] ON MVTEC AD, BEFORE AND AFTER
ALTERNATIVELY ADDING SSPCAB AND SSMCTB

TABLE IV
DETECTION AUROC AND LOCALIZATION AUROC/AP (IN %) OF THREE
STATE-OF-THE-ART METHODS [56], [57], [61] ON BRATS, BEFORE AND
AFTER ALTERNATIVELY ADDING SSPCAB AND SSMCTB

Fig. 4. Examples of image-level anomaly localization results from MVTec
AD given by DRAEM [56], before (blue contour) and after (green contour)
integrating SSMCTB. The ground-truth anomalies are shown in red. Best viewed
in color.

Results on MVTec AD: We report the results on MVTec
AD in Table III. Considering the detection results, we observe
that adding SSPCAB and SSMCTB leads to superior results
for all three models. Considering the localization results, the
AUROC scores of DRAEM do not show any improvements
when adding SSPCAB and SSMCTB. However, the localization
AP of DRAEM exhibits gains of around 2% by adding SSPCAB
and SSMCTB. In addition, the localization AUROC values of
NSA and FastViT+NSA grow when SSPCAB and SSMCTB are
introduced into the respective architectures.
In Fig. 4, we present some examples of qualitative results from
MVTec AD, obtained by DRAEM [56], before and after adding
SSMCTB. In all shown cases, we observe that the anomaly
localization results are better aligned with the ground-truth
regions when SSMCTB is integrated into DRAEM.
Results on BRATS: In Table IV, we present the brain lesion
detection and localization results obtained by the anomaly detection models [56], [57], [61] on BRATS, before and after
adding SSPCAB and SSMCTB, respectively. Remarkably, we

notice that the results of DRAEM, NSA and FastViT+NSA show
significant performance improvements when integrating SSMCTB. Moreover, the performance gain brought by SSMCTB is
always higher than the gain brought by SSPCAB. When taking
advantage of the 3D nature of the MRI scans by employing the
3D SSMCTB, we attain even higher performance with DRAEM.
In Fig. 5, we present several examples of qualitative results
from BRATS, given by DRAEM [56], before and after adding

MADAN et al.: SELF-SUPERVISED MASKED CONVOLUTIONAL TRANSFORMER BLOCK FOR ANOMALY DETECTION

535

Fig. 5. Examples of image-level anomaly localization results from BRATS
given by DRAEM [56], before (blue contour) and after (green contour) integrating SSMCTB. The ground-truth anomalies are shown in red. Best viewed
in color.

SSMCTB. In general, the localization results based on SSMCTB
exhibit a higher overlap with the ground-truth regions, explaining why SSMCTB leads to superior performance levels.
F. Anomaly Detection in Videos
Baselines: We select six recent methods [42], [44], [55], [58],
[59], [62] yielding state-of-the-art performance on Avenue and
ShanghaiTech. Liu et al. [42] proposed a GAN-based framework to detect anomalies based on the future frame prediction
error. Park et al. [44] presented a memory-based auto-encoder
classifying anomalies based on the reconstruction error. The
model comprises a memory module that memorizes prototypes
of normal samples. Liu et al. [59] employed a hybrid framework
based on flow reconstruction and frame prediction, using the
accumulated error to detect anomalies. Georgescu et al. [58]
introduced a training scheme where the latent subspaces of
appearance and motion auto-encoders are improved by performing gradient ascent on pseudo-anomalies during training.
Wang et al. [62] proposed a novel transformer-based spatiotemporal auto-encoder for object-centric video anomaly detection, which employs an input perturbation approach to improve
the reconstruction capability of the model. Bărbălău et al. [55]
extended the previous work of Georgescu et al. [50] with two
3D transformer-based self-supervised multi-task architectures
trained on new sets of proxy tasks. Among the two versions
proposed in [55], we opt for SSMTL++v2. We included this 3D
model [55] because it serves as a good baseline for applying our
3D SSMCTB.
We also experiment with the recently proposed masked autoencoder framework [60], which is based on the ViT backbone [52]. We add this seventh baseline model to further demonstrate the applicability of SSMCTB to vision transformers.
Results on RGB videos: We present the results on Avenue
and ShanghaiTech in Table V. As for the image anomaly detection experiments, we compare the results of the underlying
models before and after adding SSPCAB [54] and SSMCTB,
respectively. For the method of Liu et al. [42], both SSPCAB
and SSMCTB lead to performance improvements, but the gains
brought by SSMCTB are always higher than those brought by
SSPCAB. Since the methods of He et al. [60] and Park et al. [44]

Fig. 6. Frame-level anomaly scores of the method of Georgescu et al. [58],
before (baseline) and after (ours) integrating SSMCTB, for test video 02 from
the Avenue data set. Anomaly localization results correspond to the model based
on SSMCTB. Best viewed in color.

are only capable of detecting anomalies at the frame level, we
only report their frame-level micro and macro AUC scores.
The vanilla masked auto-encoder obtains competitive results on
both Avenue and ShanghaiTech. On Avenue, SSMCTB brings
higher gains to the masked auto-encoder than SSPCAB. On
ShanghaiTech, SSMCTB is better than SSPCAB in terms of the
micro AUC, but SSPCAB exhibits higher macro AUC gains.
In summary, both SSMCTB and SSPCAB improve the masked
auto-encoder, with SSMCTB having the upper hand. Considering the results of Park et al. [44] on Avenue, SSMCTB leads to
higher gains in terms of the micro AUC (from 82.8% to 87.0%),
while SSPCAB leads to a higher macro AUC (from 86.8% to
88.6%). On ShanghaiTech, we observe higher gains after adding
SSMCTB rather than SSPCAB. Moving on to the object-centric
models of Liu et al. [59] and Georgescu et al. [58], we observe
that the top gains are mainly shared between SSPCAB and
SSMCTB. However, for the object-centric transformer of Wang
et al. [62], SSMCTB yields higher gains than SSPCAB.
When integrating our 3D SSMCTB into the 3D architecture
presented in [55], we observe performance improvements according to most metrics. Overall, SSMCTB leads to the highest
performance levels on Avenue for three metrics, namely the
micro AUC (93.2%), the macro AUC (93.9%) and the RBDC
(66.04%). At the same time, SSPCAB attains the highest TBDC
score (89.28%) on Avenue. On ShanghaiTech, it appears that
the best scores are obtained by adding the 3D SSMCTB into the
underlying model of Bărbălău et al. [55], since our 3D SSMCTB
brings performance gains for three metrics.
In Figs. 6 and 7, we illustrate the anomaly detection performance on two test videos from Avenue, before and after
integrating SSMCTB into the model of Georgescu et al. [58].
Our approach produces superior frame-level anomaly scores,
being able to detect the person running in the first video (Fig. 6)
and the person throwing an object in the second one (Fig. 7).
Moreover, in the second video, we also notice that SSMCTB
increases the anomaly score for the penultimate abnormal event,

536

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

TABLE V
MICRO-AVERAGED FRAME-LEVEL AUC, MACRO-AVERAGED FRAME-LEVEL AUC, RBDC, AND TBDC SCORES (IN %) OF VARIOUS STATE-OF-THE-ART METHODS
ON AVENUE AND SHANGHAITECH. AMONG THE EXISTING MODELS, WE SELECT SEVEN MODELS [42], [44], [55], [58], [59], [60], [62]
TO SHOW RESULTS BEFORE AND AFTER INCLUDING SSPCAB AND SSMCTB, RESPECTIVELY

resolving the false negative detection of the baseline. Similarly,
in Fig. 8, we show the effect of adding SSMCTB into the
architecture of Liu et al. [59] applied on a test video from
ShanghaiTech. Once again, SSMCTB improves the frame-level
detection performance, being able to detect the person riding a
bike in a pedestrian area, which is forbidden. SSMCTB correctly
raises the anomaly scores for about 50 video frames, starting at
around frame index 150, thus reducing the false negative rate.
Results on thermal videos: Since texture is not present in
the thermal domain, there is no need to apply very deep architectures, as noticed by Nikolov et al. [64]. Moreover, object
detectors pre-trained on natural images do not work equally well
in the thermal domain due to the distribution shift. To this end, the
object-centric [55], [58], [59], [62] and very deep [42] baselines
attain very poor results (micro AUC values under 50%). Hence,
we resort to employing the architecture of Park et al. [44] as

TABLE VI
MICRO AND MACRO AUC SCORES (IN %) ON THERMAL RARE EVENT,
OBTAINED WHILE ALTERNATIVELY INCLUDING SSPCAB [54] AND SSMCTB
INTO THE METHOD OF PARK ET AL. [44]

underlying model for SSPCAB and SSMCTB. As shown in
Table VI, the chosen baseline attains a micro AUC of 53.2% and
a macro AUC of 66.5%. Both SSPCAB and SSMCTB seem to
have a positive influence on the micro AUC score, but the gains of
the latter block are significantly higher (above 5%). In summary,
the results reported on Thermal Rare Event demonstrate the

MADAN et al.: SELF-SUPERVISED MASKED CONVOLUTIONAL TRANSFORMER BLOCK FOR ANOMALY DETECTION

Fig. 7. Frame-level anomaly scores of the method of Georgescu et al. [58],
before (baseline) and after (ours) integrating SSMCTB, for test video 10 from
the Avenue data set. Anomaly localization results correspond to the model based
on SSMCTB. Best viewed in color.

537

Fig. 9. Frame-level anomaly scores of the method of Park et al. [44], before
(baseline) and after (ours) integrating SSMCTB, for test video 39 from the
Thermal Rare Event data set. Anomaly localization results correspond to the
model based on SSMCTB. Best viewed in color.

TABLE VII
INFERENCE TIME (IN MILLISECONDS) PER EXAMPLE FOR THREE
FRAMEWORKS [42], [56], [58], BEFORE AND AFTER INTEGRATING SSPCAB
AND SSMCTB, RESPECTIVELY

Fig. 8. Frame-level anomaly scores of the method of Liu et al. [59], before
(baseline) and after (ours) integrating SSMCTB, for test video 02_0164 from the
ShanghaiTech data set. Anomaly localization results correspond to the model
based on SSMCTB. Best viewed in color.

utility of SSMCTB, further confirming the gains observed on
RGB video data sets.
In Fig. 9, we show the anomaly detection performance on a
test video from Thermal Rare Event, before and after integrating
SSMCTB into the model of Park et al. [44]. SSMCTB leads to
important gains in terms of the frame-level scores, being able to
detect the vehicle moving backwards.
G. Inference Time
Regardless of the underlying framework [42], [44], [55], [56],
[57], [58], [59], [60], [61], [62], similar to Ristea et al. [54],
we add only one instance of SSMCTB, usually replacing the
penultimate convolutional layer. Considering that the channel
attention from SSPCAB is replaced with a channel-wise transformer block in SSMCTB, we might expect a slightly higher

processing time. To assess the amount of extra time added
by SSMCTB, we present the running times before and after
integrating SSPCAB and SSMCTB into two state-of-the-art
frameworks [42], [58] in Table VII. For both baseline models,
the time added by SSMCTB is at most 0.1 ms higher than the
time taken by SSPCAB. Moreover, the computational time of
SSMCTB does not exceed a difference of 0.4 ms with respect to
the original baselines. Another important question is how does
the 3D version of SSMCTB impact the running time. To answer
this question, we take the DRAEM model [56] and measure
the running time before and after adding the 3D SSMCTB.
The reported time measurements show that the running time
increase due to the 3D SSMCTB is still marginal, being around
0.2 ms. Hence, the processing delays caused by the introduction
of the 2D or 3D SSMCTB versions are within the same range. In
summary, we consider that the accuracy gains brought by SSMCTB outweigh the marginal running time expansions reported
in Table VII.

538

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

TABLE VIII
MICRO AUC (IN %) ON AVENUE BY INCORPORATING SSMCTB INTO
DIFFERENT CONV BLOCKS OF THE DECODER PROPOSED BY PARK ET AL. [44]

TABLE IX
MICRO AUC (IN %) ON AVENUE BY INCORPORATING SSMCTB INTO THE
MODEL OF PARK ET AL. [44]

TABLE X
MICRO AUC (IN %) ON AVENUE BY INCORPORATING SSMCTB INTO THE
MODEL OF PARK ET AL. [44], WHILE VARYING THE HYPERPARAMETERS OF
THE CHANNEL-WISE TRANSFORMER, NAMELY THE ACTIVATION MAP SIZE
(h × w ) AFTER THE AVERAGE POOLING LAYER, THE TOKEN SIZE (dt ) AFTER
THE PROJECTION LAYER, THE NUMBER OF HEADS (H), AS WELL AS THE
NUMBER OF SUCCESSIVE TRANSFORMER BLOCKS (L)

H. Ablation Study
Block placement: Across all the experiments presented so far,
recall that we introduce a single SSMCTB, which is usually
placed near the end of the architecture (penultimate convolutional layer), as mentioned in Section IV-C. The number of
blocks as well as their placement should be tuned on some
validation set, which could lead to higher performance gains.
However, anomaly detection data sets do not commonly contain
a validation set and there is no way to keep a number of training
samples for validation, as the training set comprises only normal
examples. To this end, we employed a single configuration (one
block, closer to the output) to fairly demonstrate the universality
of SSMCTB. Certainly, this choice might not always be optimal. Hence, we perform ablation experiments by incorporating
SSMCTB at different decoder levels of the network proposed
by Park et al. [44], considering different dilation rates (d). We
vary the dilation rate along with the block placement, because
Duţă et al. [113] observed that higher dilation rates are suitable
for earlier dilated convolutional layers, and lower dilation rates
are suitable for dilated convolutional layers closer to the output.
In Table VIII, we show the corresponding results on the Avenue data set. We start by adding SSMCTB into the earliest stage
of the decoder (first conv block), progressively moving the block
to the layers closer to the output of the decoder, until we reach
the very last one. For each decoder level (early, middle, late),
we vary the dilation rate to find a suitable value. We attain the
best micro AUC (87.0%) when integrating SSMCTB into the last
conv block of the decoder, while using a dilation rate of d = 1. A
dilation rate of d = 4 seems suitable when placing SSMCTB at
an earlier stage, while, for the middle stage placement, the optimal dilation rate appears to be d = 3. Interestingly, these results
are consistent with the observation made by Duţă et al. [113],
although their observation applies to dilated convolutions, while
ours applies to masked convolutions. Nevertheless, all the results
are consistently better than the baseline (82.8%), regardless of

the block placement or the dilation rate. We do not observe major
improvements when integrating multiple blocks, concluding that
integrating a single SSMCTB is sufficient.
Size of masked region: Increasing the size of the masked
region M can lead to a harder reconstruction task, at each
location where our masked convolution is applied. However,
it is unclear if making the task harder leads to better results.
To this end, we vary the spatial size of M , considering three
options: 1 × 1, 2 × 2 and 3 × 3. We present the corresponding
results in Table IX. The empirical results indicate that increasing
the size of M leads to lower anomaly detection scores. Hence,
we conclude that a size of 1 × 1 for the masked region M is
optimal.
Transformer architecture: In Table X, we present further
ablation experiments for the channel-wise transformer module.
We keep the underlying model of Park et al. [44] and report the
results on the Avenue data set. As variations for the transformer
module, we consider the following hyperparameters: the activation map size (h × w ) after the average pooling layer, the token
size (dt ) after the projection layer, the number of heads (H), as
well as the number of successive transformer blocks (L).
First, we analyze how activation maps of different dimensions,
given as output by the average pooling layer placed right before
the transformer, influence the results. We observe that shrinking
the maps to 1 × 1 gives the best micro AUC (87.0%). The

MADAN et al.: SELF-SUPERVISED MASKED CONVOLUTIONAL TRANSFORMER BLOCK FOR ANOMALY DETECTION

TABLE XI
MICRO AUC (IN %) ON AVENUE BY INCORPORATING SSMCTB INTO THE
MODEL OF PARK ET AL. [44], WHILE VARYING THE HYPERPARAMETER δ OF
THE HUBER LOSS

TABLE XII
MICRO AUC (IN %) ON AVENUE BY INCORPORATING SSMCTB INTO THE
MODEL OF PARK ET AL. [44], WHILE SWITCHING BETWEEN DILATED AND
MASKED CONVOLUTION. DIFFERENT VALUES FOR THE DILATION RATE d ARE
TESTED FOR THE TWO OPERATIONS

optimal configuration of the average pooling layer (producing
activation maps of 1 × 1) is equivalent to global average pooling.
For the projection layer, we consider output dimensions in the
set dt ∈ {16, 32, 64, 128}. The optimal size for the projection
layer is dt = 64. We consider transformer modules having 3
to 6 heads. The empirical evidence indicates that using H = 4
or H = 5 heads leads to equally good results. Finally, we experiment with transformer modules having 1 to 3 blocks. The
best performance is achieved with L = 2 successive transformer
blocks. We underline that all transformer configurations surpass
the baseline model [44].
Huber loss hyperparameter: Huber loss is the combination
of the L1 (MAE) and L2 (MSE) losses (see (7)), where δ
is a hyperparameter representing the threshold that switches
between the two loss functions. To study the effect of δ, we
consider different values for the hyperparameter δ ∈ {0.5, 1, 2},
reporting the results in Table XI. We find that the maximum
improvement corresponds to δ = 1, but the other values of δ
also lead to superior results compared to the baseline.
Comparison with dilated convolution: In Table XII, we compare the dilated convolution against the proposed masked convolution, alternating between the two operations inside SSMCTB.
We denote the block based on dilated convolution through the
acronym SSDCTB. When comparing the two convolutional
operations, we consider multiple dilation rates between 1 and
3. The experiments show that the proposed masked convolution
outperforms the dilated convolution, regardless of the dilation
rate. This confirms that the two operations are not equivalent,
essentially revealing the importance of the self-supervised task
based on reconstructing the masked region M situated in the
center of the receptive field.

539

V. CONCLUSION
In this paper, we extended our previous work [54] by introducing SSMCTB, a novel neural block composed of a masked
convolutional layer and a channel-wise transformer module,
which predicts a masked region in the center of the convolutional
receptive field. Our neural block is trained in a self-supervised
manner, via a reconstruction loss of its own. To show the benefits
of using SSMCTB in anomaly detection, we integrated our block
into a series of image and video anomaly detection methods [42],
[44], [55], [56], [57], [58], [59], [60], [61], [62]. In addition,
we included two new benchmarks from domains that were
not previously considered in our previous work [54], namely
medical images and thermal videos. Moreover, we extended the
2D masked convolution to a 3D masked convolution, broadening
the applicability of the self-supervised block to 3D neural architectures. To showcase the utility of the new 3D SSMCTB, we
integrated our 3D block into two 3D networks (3D DRAEM and
SSMTL++v2) for anomaly detection in image and video, respectively. Our empirical results across multiple benchmarks and
underlying models indicate that SSMCTB brings performance
improvements in a vast majority of cases. Furthermore, with
the help of SSMCTB, we are able to obtain new state-of-the-art
levels on the widely-used Avenue and ShanghaiTech data sets.
We consider this as a major achievement, which would not have
been possible without SSMCTB.
In future work, we aim to apply our novel self-supervised
block on other tasks, aside from anomaly detection. For example, due to the self-supervised loss computed with respect
to the masked region, our block could be integrated into various neural architectures to perform self-supervised pre-training,
before applying the respective models to downstream tasks.
Interestingly, the pre-training could be performed at multiple
architectural levels, i.e. wherever the block is added into the
model.
REFERENCES
[1] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec AD–
A comprehensive real-world dataset for unsupervised anomaly detection,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2019,
pp. 9592–9600.
[2] S. Lee, S. Lee, and B. C. Song, “CFA: Coupled-hypersphere-based feature adaptation for target-oriented anomaly localization,” IEEE Access,
vol. 10, pp. 78446–78454, 2022.
[3] W. Luo, W. Liu, and S. Gao, “A revisit of sparse coding based anomaly
detection in stacked RNN framework,” in Proc. IEEE Int. Conf. Comput.
Vis., 2017, pp. 341–349.
[4] N. Shvetsova, B. Bakker, I. Fedulova, H. Schulz, and D. V. Dylov,
“Anomaly detection in medical imaging with deep perceptual autoencoders,” IEEE Access, vol. 9, pp. 118571–118583, 2021.
[5] D. Carrera, F. Manganini, G. Boracchi, and E. Lanzarone, “Defect
detection in SEM images of nanofibrous materials,” IEEE Trans. Ind.
Inform., vol. 13, no. 2, pp. 551–561, Apr. 2017.
[6] K.-W. Cheng, Y.-T. Chen, and W.-H. Fang, “Video anomaly detection
and localization using hierarchical feature representation and Gaussian
process regression,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
2015, pp. 2909–2917.
[7] Y. Cong, J. Yuan, and J. Liu, “Sparse reconstruction cost for abnormal
event detection,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
2011, pp. 3449–3456.
[8] J. K. Dutta and B. Banerjee, “Online detection of abnormal events using
incremental coding length,” in Proc. AAAI Conf. Artif. Intell., 2015,
pp. 3755–3761.

540

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

[9] C. Lu, J. Shi, and J. Jia, “Abnormal event detection at 150 FPS in
MATLAB,” in Proc. IEEE Int. Conf. Comput. Vis., 2013, pp. 2720–2727.
[10] H. Ren, W. Liu, S. I. Olsen, S. Escalera, and T. B. Moeslund, “Unsupervised behavior-specific dictionary learning for abnormal event detection,”
in Proc. Brit. Mach. Vis. Conf., 2015, pp. 28.1–28.13.
[11] A. Del Giorno, J. Bagnell, and M. Hebert, “A discriminative framework
for anomaly detection in large videos,” in Proc. Eur. Conf. Comput. Vis.,
2016, pp. 334–349.
[12] R. T. Ionescu, S. Smeureanu, B. Alexe, and M. Popescu, “Unmasking the
abnormal events in video,” in Proc. IEEE Int. Conf. Comput. Vis., 2017,
pp. 2895–2903.
[13] Y. Liu, C.-L. Li, and B. Póczos, “Classifier two-sample test for video
anomaly detections,” in Proc. Brit. Mach. Vis. Conf., 2018, Art. no. 71.
[14] G. Pang, C. Yan, C. Shen, A. V. D. Hengel, and X. Bai, “Self-trained
deep ordinal regression for end-to-end video anomaly detection,” in Proc.
IEEE Conf. Comput. Vis. Pattern Recognit., 2020, pp. 12173–12182.
[15] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Uninformed
students: Student-teacher anomaly detection with discriminative latent
embeddings,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2020,
pp. 4183–4192.
[16] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “PaDiM: A patch distribution modeling framework for anomaly detection and localization,”
in Proc. Int. Conf. Pattern Recognit., 2021, pp. 475–489.
[17] R. T. Ionescu, F. S. Khan, M.-I. Georgescu, and L. Shao, “Object-centric
auto-encoders and dummy anomalies for abnormal event detection in
video,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2019,
pp. 7842–7851.
[18] R. T. Ionescu, S. Smeureanu, M. Popescu, and B. Alexe, “Detecting
abnormal events in video using narrowed normality clusters,” in Proc.
Winter Conf. Appl. Comput. Vis., 2019, pp. 1951–1960.
[19] B. Ramachandra and M. Jones, “Street scene: A new dataset and evaluation protocol for video anomaly detection,” in Proc. Winter Conf. Appl.
Comput. Vis., 2020, pp. 2569–2578.
[20] B. Ramachandra, M. Jones, and R. Vatsavai, “Learning a distance function with a Siamese network to localize anomalies in videos,” in Proc.
Winter Conf. Appl. Comput. Vis., 2020, pp. 2598–2607.
[21] M. Ravanbakhsh, M. Nabi, H. Mousavi, E. Sangineto, and N. Sebe,
“Plug-and-play CNN for crowd motion analysis: An application in abnormal event detection,” in Proc. Winter Conf. Appl. Comput. Vis., 2018,
pp. 1689–1698.
[22] M. Sabokrou, M. Fayyaz, M. Fathy, and R. Klette, “Deep-cascade:
Cascading 3D deep neural networks for fast anomaly detection and
localization in crowded scenes,” IEEE Trans. Image Process., vol. 26,
no. 4, pp. 1992–2004, Apr. 2017.
[23] M. Sabokrou, M. Fayyaz, M. Fathy, Z. Moayed, and R. Klette, “Deepanomaly: Fully convolutional neural network for fast anomaly detection in crowded scenes,” Comput. Vis. Image Understanding, vol. 172,
pp. 88–97, 2018.
[24] V. Saligrama and Z. Chen, “Video anomaly detection based on local statistical aggregates,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
2012, pp. 2112–2119.
[25] S. Smeureanu, R. T. Ionescu, M. Popescu, and B. Alexe, “Deep appearance features for abnormal behavior detection in video,” in Proc. Int.
Conf. Image Anal. Process., 2017, pp. 779–789.
[26] Q. Sun, H. Liu, and T. Harada, “Online growing neural gas for anomaly
detection in changing surveillance scenes,” Pattern Recognit., vol. 64,
pp. 187–201, Apr. 2017.
[27] H. T. Tran and D. Hogg, “Anomaly detection using a convolutional
winner-take-all autoencoder,” in Proc. Brit. Mach. Vis. Conf., 2017.
[28] A. Adam, E. Rivlin, I. Shimshoni, and D. Reinitz, “Robust real-time
unusual event detection using multiple fixed-location monitors,” IEEE
Trans. Pattern Anal. Mach. Intell., vol. 30, no. 3, pp. 555–560, Mar. 2008.
[29] B. Antic and B. Ommer, “Video parsing for abnormality detection,” in
Proc. IEEE Int. Conf. Comput. Vis., 2011, pp. 2415–2422.
[30] Y. Feng, Y. Yuan, and X. Lu, “Learning deep event models for crowd
anomaly detection,” Neurocomputing, vol. 219, pp. 548–556, 2017.
[31] R. Hinami, T. Mei, and S. Satoh, “Joint detection and recounting of
abnormal events by learning deep generic knowledge,” in Proc. IEEE
Int. Conf. Comput. Vis., 2017, pp. 3639–3647.
[32] J. Kim and K. Grauman, “Observe locally, infer globally: A spacetime MRF for detecting abnormal activities with incremental updates,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2009,
pp. 2921–2928.
[33] V. Mahadevan, W.-X. Li, V. Bhalodia, and N. Vasconcelos, “Anomaly
detection in crowded scenes,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., 2010, pp. 1975–1981.

[34] R. Mehran, A. Oyama, and M. Shah, “Abnormal crowd behavior detection
using social force model,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., 2009, pp. 935–942.
[35] M. Rudolph, B. Wandt, and B. Rosenhahn, “Same same but DifferNet:
Semi-supervised defect detection with normalizing flows,” in Proc. Winter Conf. Appl. Comput. Vis., 2021, pp. 1907–1916.
[36] B. Saleh, A. Farhadi, and A. Elgammal, “Object-centric anomaly detection by attribute-based reasoning,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit., 2013, pp. 787–794.
[37] S. Wu, B. E. Moore, and M. Shah, “Chaotic invariants of Lagrangian
particle trajectories for anomaly detection in crowded scenes,” in Proc.
IEEE Conf. Comput. Vis. Pattern Recognit., 2010, pp. 2054–2060.
[38] Y. Fei, C. Huang, C. Jinkun, M. Li, Y. Zhang, and C. Lu, “Attribute
restoration framework for anomaly detection,” IEEE Trans. Multimedia,
vol. 24, pp. 116–127, 2022.
[39] D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,” in
Proc. IEEE Int. Conf. Comput. Vis., 2019, pp. 1705–1714.
[40] M. Hasan, J. Choi, J. Neumann, A. K. Roy-Chowdhury, and L. S. Davis,
“Learning temporal regularity in video sequences,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit., 2016, pp. 733–742.
[41] Z. Li et al., “Superpixel masking and inpainting for self-supervised
anomaly detection,” in Proc. Brit. Mach. Vis. Conf., 2020.
[42] W. Liu, W. Luo, D. Lian, and S. Gao, “Future Frame Prediction for
Anomaly Detection–A New Baseline,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit., 2018, pp. 6536–6545.
[43] T.-N. Nguyen and J. Meunier, “Anomaly detection in video sequence with
appearance-motion correspondence,” in Proc. IEEE Int. Conf. Comput.
Vis., 2019, pp. 1273–1283.
[44] H. Park, J. Noh, and B. Ham, “Learning memory-guided normality for
anomaly detection,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
2020, pp. 14372–14381.
[45] M. Ravanbakhsh, M. Nabi, E. Sangineto, L. Marcenaro, C. Regazzoni, and N. Sebe, “Abnormal event detection in videos using generative adversarial nets,” in Proc. IEEE Int. Conf. Image Process., 2017,
pp. 1577–1581.
[46] M. Salehi, N. Sadjadi, S. Baselizadeh, M. H. Rohban, and H. R.
Rabiee, “Multiresolution knowledge distillation for anomaly detection,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2021,
pp. 14902–14912.
[47] Y. Tang, L. Zhao, S. Zhang, C. Gong, G. Li, and J. Yang, “Integrating
prediction and reconstruction for anomaly detection,” Pattern Recognit.
Lett., vol. 129, pp. 123–130, 2020.
[48] S. Venkataramanan, K.-C. Peng, R. V. Singh, and A. Mahalanobis,
“Attention guided anomaly localization in images,” in Proc. Eur. Conf.
Comput. Vis., 2020, pp. 485–503.
[49] P. J. Huber, “Robust estimation of a location parameter,” Ann. Math.
Statist., vol. 35, no. 1, pp. 73–101, 1964.
[50] M.-I. Georgescu, A. Bărbălău, R. T. Ionescu, F. S. Khan, M. Popescu, and
M. Shah, “Anomaly detection in video via self-supervised and multi-task
learning,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2021,
pp. 12742–12752.
[51] A. Acsintoae et al., “UBnormal: New benchmark for supervised open-set
video anomaly detection,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., 2022, pp. 20143–20153.
[52] A. Dosovitskiy et al., “An image is worth 16x16 words: Transformers for
image recognition at scale,” in Proc. Int. Conf. Learn. Representations,
2021.
[53] A. Vaswani et al., “Attention is all you need,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2017, pp. 5998–6008.
[54] N.-C. Ristea et al., “Self-supervised predictive convolutional attentive
block for anomaly detection,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., 2022, pp. 13576–13586.
[55] A. Bărbălău et al., “SSMTL++: Revisiting self-supervised multi-task
learning for video anomaly detection,” Comput. Vis. Image Understanding, vol. 229, 2023, Art. no. 103656.
[56] V. Zavrtanik, M. Kristan, and D. Skocaj, “DRAEM–A. Discriminatively
Trained Reconstruction Embedding for Surface Anomaly Detection,” in
Proc. IEEE Int. Conf. Comput. Vis., 2021, pp. 8330–8339.
[57] H. M. Schlüter, J. Tan, B. Hou, and B. Kainz, “Natural synthetic anomalies for self-supervised anomaly detection and localization,” in Proc. Eur.
Conf. Comput. Vis., 2022, pp. 474–489.
[58] M. I. Georgescu, R. Ionescu, F. S. Khan, M. Popescu, and M. Shah, “A
background-agnostic framework with adversarial training for abnormal
event detection in video,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 44,
no. 9, pp. 4505–4523, Sep. 2022.

MADAN et al.: SELF-SUPERVISED MASKED CONVOLUTIONAL TRANSFORMER BLOCK FOR ANOMALY DETECTION

[59] Z. Liu, Y. Nie, C. Long, Q. Zhang, and G. Li, “A hybrid video anomaly
detection framework via memory-augmented flow reconstruction and
flow-guided frame prediction,” in Proc. IEEE Int. Conf. Comput. Vis.,
2021, pp. 13588–13597.
[60] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit., 2022, pp. 16000–16009.
[61] P. K. A. Vasu, J. Gabriel, J. Zhu, O. Tuzel, and A. Ranjan, “FastViT:
A fast hybrid vision transformer using structural reparameterization,” in
Proc. Int. Conf. Comput. Vis., 2023, pp. 5785–5795.
[62] Y. Wang, C. Qin, Y. Bai, Y. Xu, X. Ma, and Y. Fu, “Making reconstructionbased method great again for video anomaly detection,” in Proc. IEEE
Int. Conf. Data Mining, 2022, pp. 1215–1220.
[63] B. H. Menze et al., “The multimodal brain tumor image segmentation benchmark (BraTS),” IEEE Trans. Med. Imag., vol. 34, no. 10,
pp. 1993–2024, Oct. 2015.
[64] I. Nikolov et al., “Seasons in drift: A long-term thermal imaging dataset
for studying concept drift,” in Proc. Int. Conf. Neural Inf. Process. Syst.,
2021.
[65] J. Hu, L. Shen, and G. Sun, “Squeeze-and-excitation networks,” in Proc.
IEEE Conf. Comput. Vis. Pattern Recognit., 2018, pp. 7132–7141.
[66] N. Carion, F. Massa, G. Synnaeve, N. Usunier, A. Kirillov, and S.
Zagoruyko, “End-to-end object detection with transformers,” in Proc.
Eur. Conf. Comput. Vis., 2020, pp. 213–229.
[67] J. Chen et al., “TransUNet: Transformers make strong encoders for
medical image segmentation,” 2021, arXiv:2102.04306.
[68] S. Khan, M. Naseer, M. Hayat, S. W. Zamir, F. S. Khan, and M.
Shah, “Transformers in vision: A survey,” ACM Comput. Surv., vol. 54,
pp. 1–41, 2021.
[69] N. Parmar et al., “Image transformer,” in Proc. Int. Conf. Mach. Learn.,
2018, pp. 4055–4064.
[70] N.-C. Ristea et al., “CyTran: Cycle-consistent transformers for noncontrast to contrast CT translation,” 2021, arXiv:2110.06400.
[71] H. Touvron, M. Cord, M. Douze, F. Massa, A. Sablayrolles, and H.
Jégou, “Training data-efficient image transformers & distillation through
attention,” in Proc. Int. Conf. Mach. Learn., 2021, pp. 10347–10357.
[72] H. Wu et al., “CvT: Introducing convolutions to vision transformers,” in
Proc. IEEE Int. Conf. Comput. Vis., 2021, pp. 22–31.
[73] X. Xu and N. Xu, “Hierarchical image generation via transformer-based
sequential patch selection,” in Proc. AAAI Conf. Artif. Intell., 2022,
pp. 2938–2945.
[74] B. Zhang et al., “StyleSwin: Transformer-based GAN for high-resolution
image generation,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
2022, pp. 11304–11314.
[75] M. Zheng, P. Gao, X. Wang, H. Li, and H. Dong, “End-to-end object
detection with adaptive clustering transformer,” in Proc. Brit. Mach. Vis.
Conf., 2020.
[76] X. Zhu, W. Su, L. Lu, B. Li, X. Wang, and J. Dai, “Deformable DETR:
Deformable transformers for end-to-end object detection,” in Proc. Int.
Conf. Learn. Representations, 2020.
[77] J. Jiang et al., “Masked swin transformer UNet for industrial anomaly
detection,” IEEE Trans. Ind. Inform., vol. 19, no. 2, pp. 2200–2209,
Feb. 2023.
[78] Y. Lee and P. Kang, “AnoViT: Unsupervised anomaly detection and localization with vision transformer-based encoder-decoder,” IEEE Access,
vol. 10, pp. 46717–46724, 2022.
[79] P. Mishra, R. Verk, D. Fornasier, C. Piciarelli, and G. L. Foresti, “VTADL: A vision transformer network for image anomaly detection and
localization,” in Proc. IEEE 30th Int. Symp. Ind. Electron., 2021, pp. 1–6.
[80] J. Pirnay and K. Chai, “Inpainting transformer for anomaly detection,”
in Proc. Int. Conf. Image Anal. Process., 2022, pp. 394–406.
[81] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int. Conf.
Learn. Representations, 2022.
[82] D. Pathak, P. Krähenbühl, J. Donahue, T. Darrell, and A. Efros, “Context
encoders: Feature learning by inpainting,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit., 2016, pp. 2536–2544.
[83] C. Wei, H. Fan, S. Xie, C.-Y. Wu, A. Yuille, and C. Feichtenhofer, “Masked feature prediction for self-supervised visual pretraining,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2022,
pp. 14668–14678.
[84] H. Chang, H. Zhang, L. Jiang, C. Liu, and W. T. Freeman, ”MaskGIT:
Masked generative image transformer,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit., 2022, pp. 11315–11325.

541

[85] X. Yu, L. Tang, Y. Rao, T. Huang, J. Zhou, and J. Lu, “Point-BERT:
Pre-training 3D point cloud transformers with masked point modeling,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2022,
pp. 19313–19322.
[86] M. Astrid, M. Z. Zaheer, and S.-I. Lee, “Synthetic temporal anomaly
guided end-to-end video anomaly detection,” in Proc. IEEE Int. Conf.
Comput. Vis. Workshops, 2021, pp. 207–214.
[87] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. V. Gehler,
“Towards total recall in industrial anomaly detection,” in Proc. IEEE
Conf. Comput. Vis. Pattern Recognit., 2022, pp. 14298–14308.
[88] S. Yamada, S. Kamiya, and K. Hotta, “Reconstructed student-teacher and
discriminative networks for anomaly detection,” in Proc. IEEE/RSJ Int.
Conf. Intell. Robots Syst., 2022, pp. 2725–2732.
[89] K. Doshi and Y. Yilmaz, “Rethinking video anomaly detection – A
continual learning approach,” in Proc. Winter Conf. Appl. Comput. Vis.,
2022, pp. 3961–3970.
[90] M. Haselmann, D. P. Gruber, and P. Tabatabai, “Anomaly detection using
deep learning based image completion,” in Proc. Int. Conf. Mach. Learn.
Appl., 2018, pp. 1237–1242.
[91] N.-C. Ristea, F.-A. Croitoru, R. T. Ionescu, M. Popescu, F. S. Khan,
and M. Shah, “Self-distilled masked auto-encoders are efficient video
anomaly detectors,” 2023, arXiv:2306.12041.
[92] G. Yu et al., “Cloze test helps: Effective video anomaly detection via
learning to complete video events,” in Proc. ACM Int. Conf. Multimedia,
2020, pp. 583–591.
[93] M. Sabokrou et al., “AVID: Adversarial visual irregularity detection,” in
Proc. Asian Conf. Comput. Vis., 2018, pp. 488–505.
[94] D. Luo et al., “Video cloze procedure for self-supervised spatio-temporal
learning,” in Proc. AAAI Conf. Artif. Intell., 2020, pp. 11701–11708.
[95] Z. Liu et al., “Swin transformer: Hierarchical vision transformer using shifted windows,” in Proc. IEEE Int. Conf. Comput. Vis., 2021,
pp. 10012–10022.
[96] X. Guo et al., “Discriminative-generative dual memory video anomaly
detection,” 2021, arXiv:2104.14430.
[97] C. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Self-supervised learning
for anomaly detection and localization,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit., 2021, pp. 9664–9674.
[98] Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner, “Gradient-based learning applied to document recognition,” Proc. IEEE, vol. 86, no. 11,
pp. 2278–2324, Nov. 1998.
[99] A. Krizhevsky, I. Sutskever, and G. E. Hinton, “ImageNet classification
with deep convolutional neural networks,” in Proc. Int. Conf. Neural Inf.
Process. Syst., 2012, pp. 1106–1114.
[100] M. D. Zeiler and R. Fergus, “Visualizing and understanding convolutional
networks,” in Proc. Eur. Conf. Comput. Vis., 2014, pp. 818–833.
[101] S. Sabour, N. Frosst, and G. E. Hinton, “Dynamic routing between capsules,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2017, pp. 3859–3869.
[102] A. Şandru, M.-I. Georgescu, and R. T. Ionescu, “Feature-level augmentation to improve robustness of deep neural networks to affine transformations,” in Proc. Eur. Conf. Comput. Vis. Workshops, 2022, pp. 332–341.
[103] V. Nair and G. E. Hinton, “Rectified linear units improve restricted Boltzmann machines,” in Proc. Int. Conf. Mach. Learn., 2010,
pp. 807–814.
[104] B. Ramachandra, M. J. Jones, and R. R. Vatsavai, “A survey of singlescene video anomaly detection,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 44, no. 5, pp. 2293–2312, May 2020.
[105] W. Sultani, C. Chen, and M. Shah, “Real-world anomaly detection in
surveillance videos,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
2018, pp. 6479–6488.
[106] P. Wu, J. Liu, and F. Shen, “A deep one-class neural network for
anomalous event detection in complex scenes,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 31, no. 7, pp. 2609–2622, Jul. 2020.
[107] S. Lee, H. G. Kim, and Y. M. Ro, “BMAN: Bidirectional multi-scale
aggregation networks for abnormal event detection,” IEEE Trans. Image
Process., vol. 29, pp. 2395–2408, 2019.
[108] F. Dong, Y. Zhang, and X. Nie, “Dual discriminator generative adversarial network for video anomaly detection,” IEEE Access, vol. 8,
pp. 88170–88176, 2020.
[109] K. Doshi and Y. Yilmaz, “Any-shot sequential anomaly detection in
surveillance videos,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
Workshops, 2020, pp. 934–935.
[110] C. Sun, Y. Jia, Y. Hu, and Y. Wu, “Scene-aware context reasoning for
unsupervised abnormal event detection in videos,” in Proc. ACM Int.
Conf. Multimedia, 2020, pp. 184–192.

542

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 1, JANUARY 2024

[111] Z. Wang, Y. Zou, and Z. Zhang, “Cluster attention contrast for
video anomaly detection,” in Proc. ACM Int. Conf. Multimedia, 2020,
pp. 2463–2471.
[112] M. Astrid, M. Z. Zaheer, J.-Y. Lee, and S.-I. Lee, “Learning not to
reconstruct anomalies,” in Proc. Brit. Mach. Vis. Conf., 2021.
[113] I. C. Duţă, M. I. Georgescu, and R. T. Ionescu, “Contextual convolutional
neural networks,” in Proc. IEEE Int. Conf. Comput. Vis. Workshops, 2021,
pp. 403–412.

Neelu Madan received the MSc degree in computer
science with a major as interactive systems and visualization from the University of Duisburg-Essen,
Germany. She is currently working toward the PhD
degree with the Department of Media Technology,
Aalborg University, Denmark. Her research interests
include artificial intelligence, computer vision, machine learning, and deep learning. She is the author
of a paper accepted for oral presentation at CVPR
2022.

Nicolae-Cătălin Ristea received the graduate degree as valedictorian from the Faculty of Electronics, Telecommunications and Information Technology, University Politehnica of Bucharest, in 2019,
and the MSc degree in the image processing field
from the University Politehnica of Bucharest. He is
currently working toward the PhD degree with the
University Politehnica of Bucharest. He is first author
of multiple papers accepted at top-tier conferences
and journals, such as CVPR and INTERSPEECH.
His research interests include AI, computer vision,
machine learning, signal processing, and deep learning.

Radu Tudor Ionescu (Member, IEEE) received the
PhD degree from the University of Bucharest, in
2013. He is a professor with the University of
Bucharest, Romania. He receiving the 2014 Award for
Outstanding Doctoral Research from the Romanian
Ad Astra Association. His research interests include
machine learning, computer vision, image processing, computational linguistics, and medical imaging.
He published more than 100 articles at international
venues (including CVPR, NeurIPS, ICCV, ACL, SIGIR, EMNLP, NAACL, TPAMI, IJCV, CVIU), and
a research monograph with Springer. He received the “Caianiello Best Young
Paper Award” at ICIAP 2013.

Kamal Nasrollahi is working in a dual position,
professor of computer vision and machine learning
with Aalborg University and head of machine learning with Milestone Systems. He is interested in fair,
ethical, and responsible use of technology, specifically machine learning applied to computer vision
for topics like object detection, tracking, anomaly
detection, and super-resolution.

Fahad Shahbaz Khan (Senior Member, IEEE) received the MSc degree in intelligent systems design
from the Chalmers University of Technology, Sweden, and the PhD degree in computer vision from
the Autonomous University of Barcelona, Spain. He
is a faculty member with the MBZ University of AI
(MBZUAI), UAE and Linköping University, Sweden.
Prior to joining MBZUAI, he worked as a lead scientist with the Inception Institute of Artificial Intelligence (IIAI), UAE. His research interests include a
wide range of topics within computer vision, such as
object recognition, object detection, action recognition, and visual tracking. He
has published articles in high-impact computer vision journals and conferences
in these areas.

Thomas B. Moeslund leads the Visual Analysis and
Perception lab, Aalborg University, the media technology section with Aalborg University and the AI for
the People Center, Aalborg University. His research
covers all aspects of software systems for automatic
analysis of visual data, especially including people.

Mubarak Shah (Life Fellow, IEEE) is the UCF
Trustee chair professor and the founding director of
the Center for Research in Computer Vision, University of Central Florida (UCF). He is a fellow of the
NAI, AAAS, IAPR, and SPIE. His research interests
include video surveillance, visual tracking, human activity recognition, visual analysis of crowded scenes,
video registration, UAV video analysis, among others.
He has served as an ACM distinguished speaker and
IEEE distinguished visitor speaker. He is a recipient of ACM SIGMM Technical Achievement award;
IEEE Outstanding Engineering Educator Award; Harris Corporation Engineering Achievement Award; an honorable mention for the ICCV 2005 “Where Am
I?” Challenge Problem; 2013 NGA Best Research Poster Presentation; 2nd place
in Grand Challenge at the ACM Multimedia 2013 conference; and runner up for
the best paper award in ACM Multimedia Conference in 2005 and 2010. At UCF
he has received the Pegasus Professor Award; University Distinguished Research
Award; Faculty Excellence in Mentoring Doctoral Students; Scholarship of
Teaching and Learning award; Teaching Incentive Program award; Research
Incentive Award.
PAPER_TEXT
