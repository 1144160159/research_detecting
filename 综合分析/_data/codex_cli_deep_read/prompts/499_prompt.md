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
# [499] Multitask Hybrid Knowledge Distillation for Unsupervised Anomaly Detection
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
编号：499
题名：Multitask Hybrid Knowledge Distillation for Unsupervised Anomaly Detection
年份：2025
DOI：10.1109/tii.2025.3556083
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2025.3556083.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：中相关，分数 9
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\499.txt
- 原始字符数：53441
- 本次发送字符数：53441
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
5666

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 7, JULY 2025

Multitask Hybrid Knowledge Distillation for
Unsupervised Anomaly Detection
Muhao Xu , Cuiping Zhu, Guang Feng, and Sijie Niu

Abstract—Detecting both logical and structural anomalies in an unsupervised anomaly detection task is a significant challenge due to the inherent differences between
the two types of anomalies. The use of two-branch knowledge distillation to deal with these two types of anomalies separately is a generalized approach. However, existing methods often design dual branches separately, which
does not effectively utilize the shared information between
these two branches. Also, due to the introduction of bottleneck layers, a large amount of detailed information is often
lost during the reconstruction process, resulting in many
false positives. To overcome these drawbacks, we structure
the student network as a multitask model to enhance its
feature extraction capability, thereby improving its ability
to distinguish between logical and structural anomalies,
especially under the constraint of limited training data.
In addition, we incorporated a self-supervised distillation
loss within the logical detection branch and trained the
model using a hybrid distillation approach. By leveraging
the differences in features between self-distillations to detect logical anomalies, we effectively minimized the false
positives that often arise from image reconstruction blurring due to feature compression in the logical branch. We
conducted experiments on three well-known anomaly detection datasets to demonstrate the effectiveness of our
approach. In particular, on the challenging MVTec LOCO
AD dataset, our method achieved impressive results with a

Received 20 November 2024; revised 23 December 2024 and 16
February 2025; accepted 6 March 2025. Date of publication 18 April
2025; date of current version 13 June 2025. This work was supported in
part by the National Natural Science Foundation of China under Grant
62471202 and Grant 62302191, in part by the Development Program
Project of Youth Innovation Team of Institutions of Higher Learning
in Shandong Province, Shandong Provincial Key Medical and Health
Laboratory of Pediatric Cancer Precision Radiotherapy (Shandong Cancer Hospital), in part by the Natural Science Foundation of Shandong
Province, China, under Grant ZR2023QF001, in part by the Development Program Project of Youth Innovation Team of Institutions of Higher
Learning in Shandong Province under Grant 2023KJ315, and in part by
the Young Talent of Lifting engineering for Science and Technology in
Shandong, China, under Grant SDAST2024QTA014. Paper no. TII-246203. (Corresponding author: Sijie Niu.)
Muhao Xu is with the Shandong Key Laboratory of Ubiquitous Intelligent Computing, School of Information Science and Engineering,
University of Jinan, Jinan 250022, China, and also with the Department
of Mechanical Engineering, Key Laboratory of High Efficiency and Clean
Mechanical Manufacture of Ministry of Education, Shandong University,
Jinan 250061, China (e-mail: 202420710@mail.sdu.edu.cn).
Cuiping Zhu, Guang Feng, and Sijie Niu are with the Shandong
Key Laboratory of Ubiquitous Intelligent Computing, School of Information Science and Engineering, University of Jinan, Jinan 250022,
China (e-mail: 202221100454@stu.ujn.edu.cn; ise_fengg@ujn.edu.cn;
sjniu@hotmail.com).
Source code are available online at https://github.com/Xmh-L/
MHKD4AD
Digital Object Identifier 10.1109/TII.2025.3556083

pixel-level sPRO of 82.9% and an image-level area under the
receiver operating characteristic curve (AUROC) of 91.0%.
Index Terms—Anomaly detection (AD), dual-student
knowledge distillation framework (DSKD), template-guided
hierarchical feature restoration (THFR).

I. INTRODUCTION
NSUPERVISED anomaly detection [1], [2], [3], [4], [5]
refers to the effective identification and localization of
anomalies in the inference phase by training the model only
on anomaly free images, which is an important and extensively
researched area within computer vision. Anomalies in industrial
detection tasks can be broadly classified into two categories:
structural anomalies and logical anomalies, as illustrated in
Fig. 1. Current methods [6], [7] in this area focus primarily
on identifying structural anomalies in relatively simple scenarios. These defects typically include surface imperfections,
such as scratches, dents, or various forms of contamination.
However, these methods have limitations in detecting logical
anomalies under highly semantically complex conditions. Any
sample that is missing or does not conform to this arrangement is an anomaly. The complex and consistent arrangement within the image poses substantial challenges for existing anomaly detection algorithms, particularly in terms of
accurately localizing and identifying logical anomalies. This
complexity underscores the need for enhanced methods that
can effectively interpret and process such intricate semantic
structures.
Previous anomaly detection methods can be grouped into
three main categories: feature representation-based [8], [9], [10],
reconstruction-based [11], [12], [13], and distillation-based [14],
[15]. During the training phase, feature representation-based
methods used pretrained networks to extract and store patch
features of normal images. During testing, anomalies are detected by comparing the differences between the features of the
input image and the stored features of normal images. These
methods are particularly effective in dealing with structural
anomalies. However, these methods have the drawback of losing
global information between images, making them less effective
in dealing with complex anomalies that violate logic. In addition,
these methods store extensive patch feature data from normal
images, with their efficiency and memory needs tied to the
dataset size. Using an encoder–decoder scheme, reconstructionbased methods assume models trained on normal images struggle to accurately reconstruct the anomalies. While effective

U

1941-0050 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html
for more information.

XU et al.: MULTITASK HYBRID KNOWLEDGE DISTILLATION FOR UNSUPERVISED ANOMALY DETECTION

Fig. 1. Examples of different types of anomaly samples, including normal images (left), structural anomalies (middle), and logical anomalies
(right). Structural anomalies introduce new local structures (such as
a bunch of keys, broken plastic bags, and stained connecting wires),
while logical anomalies violate the logical constraints of normal images
(such as swapped breakfast boxes, incorrect numbers of long and short
screws, and two connecting wires).

for complex samples, this can lead to poor reconstruction and
difficulties in detecting finer structural anomalies due to network
generalization and feature compression.
Distillation-based approaches were first applied to anomaly
detection in [6], [14], and [16], combining the advantages of
both the features representation-based and reconstruction-based
methods. Compared to representation-based and reconstructionbased methods, these methodologies show outstanding effectiveness in detecting both logical and structural anomalies,
which utilize a teacher network to guide the student network
in extracting normal image features and identify anomalies by
comparing the discrepancies between the teacher and student
networks. Efficient AD [17] separates the detection of logical anomalies and structural anomalies into two distinct tasks
and utilizes a multistudent network architecture to detect each
type of anomaly independently. To detect structural anomalies,
efficient anomaly detection (AD) employs distillation encoder
student networks and utilizes differences between the teacher
and student networks to facilitate detection. However, this design
is almost ineffective in detecting logical anomalies. Since the
structural branch lacks the ability to detect logical anomalies and
the overall anomaly detection result still comes from the combination of the outputs of the two branches, the overall anomaly
detection is not effective. Dual-student knowledge distillation
framework (DSKD) [18] adopts a multitask framework, where
a teacher network guides the learning of two student networks
to detect anomalies. For logical anomalies, the student network
employs an autoencoder structure to memorize the features of
normal images through the bottleneck structure. During the
testing phase, it attempts to restore the anomalous image to a
normal state for logical anomaly detection. However, this feature
compression leads to the loss of detailed textures, resulting in
blurred reconstructions and an increase in false positives in the
detection results.
To address these limitations, we propose a novel approach for
detecting and localizing anomalies by employing a multitask

5667

Fig. 2. Different strategies for anomaly detection. (a) Framework of
Efficient AD. (b) Framework of DSKD. (c) Framework of ours.

hybrid knowledge distillation framework. As illustrated in Fig. 2,
compared to the single-task and multitask frameworks described
in the preceding paragraph, we designed the student network as
a multitask model, employing a hard parameter-sharing strategy
within the encoder. This design facilitates joint training across
tasks for detecting logical and structural anomalies, enhancing
the extraction of shared features. Our proposed method
effectively addresses the limitations of existing methods in
capturing both structural and logical anomalies and maximizes
the use of limited training data, thereby improving overall
detection accuracy. To strengthen logical anomaly detection,
we introduced different levels of feature compression before the
structural detection branch (LDecoder), bolstering its logical
anomaly detection capabilities. In addition, the bottleneck
layer in the GDecoder often complicates the reconstruction
task and may lead to misclassification. To address this issue,
we utilized the final output of the logical detection branch as
supervisory information for the output of the shallow encoder
in the student network, resulting in the SEncoder1 generation
of a smoothed representation of the teacher network’s feature
output. This strategy effectively aligns with the principles of
a self-distillation mechanism. This approach detects logical
anomalies by leveraging the differences between the logical
detection branch and the student encoder, which strategy
enhances anomaly detection performance without introducing
additional modules or increasing computational overhead.
Our contributions can be summarized as follows.
1) We propose an efficient teacher–student network structure
that utilizes multitask student networks for unsupervised
anomaly detection tasks in complex situations.
2) We introduce a self-distillation loss that enhances the
student network’s feature extraction capabilities, leading
to a significant improvement in the performance of logical
anomaly detection.
3) To validate the effectiveness of the method, we conducted
experiments on three publicly anomaly detection datasets,
on the MVTec LOCO AD dataset we achieved stateof-the-art (SOTA) performance (pixel-sPRO 82.9% and

5668

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 7, JULY 2025

image-AUROC 91.0%), and on the MVTec AD and ViaA
datasets we achieved results with competitive results.
II. RELATED WORK
We briefly review recent research in unsupervised anomaly
detection, which can be categorized into three approaches:
feature representation-based, reconstruction-based, and
distillation-based.
Feature representation-based methods: Reiss et al. [9] proposed a method that utilizes a pretrained network to extract the
feature representation of an image and model its distribution.
During inference, anomalies are detected by analyzing the divergence between the sample’s feature representation and the
distribution of normal samples. However, this approach heavily
relies on the quality of the pretrained network and may struggle
with subtle anomalies that have minimal deviation from the
learned normal distribution. In addition, the method does not explicitly address the challenge of feature compression, which can
impact the detection accuracy in cases with complex or diverse
anomaly types. PaDiM [19] improves upon this by storing the
multivariate Gaussian distributions of the feature representations
and calculating the Mahalanobis distance between test samples
and the stored normal distributions for anomaly detection. While
this approach benefits from using a statistical distance metric,
its reliance on the Gaussian assumption limits its effectiveness
when dealing with non-Gaussian data distributions. Moreover,
the storage of multivariate Gaussian parameters for each feature
map can lead to increased memory usage, making it less suitable
for large-scale applications. Patch Core [8] introduces a patch
description method that more effectively characterizes the extracted features. A key innovation of Patch Core is the utilization
of a greedy algorithm to optimize the normal feature library.
Instead of maintaining a large, exhaustive set of normal features,
which can be computationally expensive and inefficient, Patch
Core selectively reduces the size of this library. The greedy algorithm systematically identifies and retains the most representative normal features, thereby streamlining the feature library
without sacrificing descriptive power. Consequently, Patch Core
achieves a delicate balance between maintaining high detection
accuracy and ensuring operational efficiency, addressing some
of the critical challenges in the field of unsupervised anomaly
detection. However, Patch Core may still encounter challenges
in detecting anomalies that appear in low-frequency or sparsely
sampled regions of the feature space, as the greedy selection
process could potentially exclude subtle but critical features. In
addition, the method requires careful tuning of the number of
retained features to avoid compromising detection performance.
Overall, these methods provide important advancements in unsupervised anomaly detection, yet they exhibit limitations in
handling complex data distributions, feature compression, and
balancing detection accuracy with computational resources.
Reconstruction-based methods: The authors in [12] and [13]
are trained to minimize the reconstruction error of normal images. These methods rely on accurately reconstructing normal
images while failing to do so for abnormal images during the
testing phase. Common approaches include generative adversarial networks [20] and variational autoencoders (VAEs) [21],

both of which are based on the principle of reconstructing
normal patterns and identifying the deviations. However, these
reconstruction-based methods face significant challenges, particularly in scenarios where the anomalies share similar characteristics with the normal data. In such cases, the models may
inadvertently reconstruct anomalous features, leading to a failure
in detecting anomalies effectively. SCADN [22] extends this
concept through inpainting frameworks that train models on
data with masked normal regions, enabling them to leverage
contextual information to reconstruct unseen areas. While this
approach aids in detecting anomalies by evaluating the quality
of the reconstructed regions, there remains an inherent limitation due to the strong generalization ability of deep learning models. These models are often capable of reproducing
features that closely resemble the training data, even if they
include subtle anomalies that were not explicitly present during training. This can lead to the unintended reconstruction
of anomalous features, diminishing the visibility of anomalies and reducing the accuracy and robustness of the detection
process.
Distillation-based methods: Bergmann et al. [14] used the difference between teacher and student networks to detect anomalies, leveraging the discrepancy between the networks’ outputs
to identify deviations from normal patterns. However, this approach may struggle to detect subtle or contextually complex
anomalies where the differences are not pronounced enough to
trigger detection. Reverse distillation (RD) [15] improves upon
this concept by introducing reverse distillation networks with an
encoder–decoder structure, aiming to enhance the performance
of anomaly detection. Despite the improvements, the encoder–
decoder design still faces challenges related to feature compression and information loss, which can reduce the accuracy when
detecting anomalies with fine details. To address the issue of
reconstruction detail loss, template-guided hierarchical feature
restoration (THFR) [13] uses a template-based approach to help
the image recover details by referencing a normal image as a kind
of template. While this method can improve the quality of reconstructed abnormal images by guiding the recovery process, it
also introduces a significant drawback. The differences between
the normal template and the input image can negatively impact
the reconstruction quality for normal images, often resulting
in incomplete or inaccurate reconstruction. During testing, the
template may aid in reconstructing an abnormal image to appear
normal, but for normal images, it can be counterproductive,
leading to a failure in preserving fine details and, consequently,
a decrease in detection accuracy.
Summary: Our model integrates a novel hybrid distillation
strategy that combines self-distillation and knowledge distillation, effectively reducing false positives caused by low reconstruction quality in the logical branch. Specifically, selfdistillation supervises the shallow features of the student network with its own outputs, identifying logical anomalies by
measuring inconsistencies between them. In contrast to conventional approaches that rely solely on knowledge distillation, our
model employs a multitask knowledge distillation framework.
This framework overcomes critical limitations in unsupervised
anomaly detection, which is inadequate handling of diverse

XU et al.: MULTITASK HYBRID KNOWLEDGE DISTILLATION FOR UNSUPERVISED ANOMALY DETECTION

Fig. 3.

5669

Overview architecture of the proposed multitask hybrid knowledge distillation framework.

anomaly types. By addressing these challenges, our method significantly enhances the robustness and adaptability of anomaly
detection systems.
III. PROPOSED METHOD
In this article, we propose a multitask hybrid knowledge
distillation model for anomaly detection, the architecture of
which is detailed in Fig. 3. In the training phase, the teacher
network Ft guided the learning of both the logical and the
structural decoder branches within the student network Fs . In
addition, the logical decoder branch, GDecoder, supervised the
learning of the student network’s low-level encoder, SEncoder1.
During the testing phase, structural anomaly maps As and logical anomaly maps Ag are generated by comparing features from
the teacher with those from the structural (LDecoder) and logical
(GDecoder/SEncoder1) components, respectively. Finally, we
were able to combine the two anomaly scores to obtain the final
anomaly score A.
A. Teacher Network
The architecture of our teacher network Ft is composed of six
convolutional layers coupled with two average pooling layers.
This configuration is analogous to that utilized in the Efficient
AD [17], where each neuron in the output layer of Ft encompasses a receptive field spanning 33 × 33 pixels. This design prevents anomalies in one region from affecting distant, unrelated
areas, thereby enhancing localization accuracy in anomaly detection tasks. Ft is distillated from a pretrained WideResNet-101
model [23], leveraging the extensive ImageNet dataset. During
the distillation process, we utilize the mean square error as the
loss function to guide the learning of Ft .
To enhance the efficacy of our model, we adopt the feature
postprocessing strategy from PatchCore [8], and then, each
feature vector is mapped into a compressed 384-D space, where
the feature representation is optimized. We obtain the features
ft ∈ Rh×w×c by feeding the training images x into the Ft ,
defined as
ft = Ft (x).

(1)

B. Student Network
The student network Fs comprises four components:
SEncoder1, SEncoder2, LDecoder, and GDecoder. SEncoder1
includes six convolutional layers and two max-pooling layers.
The configuration of convolutional and max-pooling layers in
SEncoder1 differs substantially from that of the teacher network,
with variations in both layer arrangement and channel count.
Such a deliberately engineered asymmetry in the architectural
design is strategically implemented to enhance the network’s
sensitivity to anomalous images. This enhancement significantly
improves the overall accuracy of anomaly detection, as elaborated in [24]. We extract the shallow subfeatures fl of the training
image x by adopting the SEncoder1 network. Subsequently,
SEncoder2, a simplified encoder with two convolutional layers,
processes this subfeature fl to generate an enhanced feature map
fh , which can be written as
fl = SEncoder1(x)
fh = SEncoder2(fl ).

(2)

To address the distinct challenges of structural and logical
anomaly detection, we designed a two-path decoder framework.
The LDecoder branch is mainly employed to detect structural
anomalies, while the GDecoder branch detects logical anomalies by analyzing global image features to identify deviations
from standard composition and coherence. The structure of the
GDecoder network consists of convolutional layers, upsampling
layers, and dropout layers. The feature map fh is fed into the
bottleneck layer Conv-1, which uses a convolutional kernel
of size 16, to compress the input into a 1-D global feature
representation fg ∈ R1×1×64 when the input image size is 256.
The fundamental difference between the GDecoder and LDecoder branches lies in the feature compression strategy. This
strategy compresses image features into a 1-D vector, effectively
preventing the reconstruction of anomalies during the testing
phase. By doing so, it forces the network to memorize only the
prominent features of normal images during the training process.
After the initial extraction, the global feature fg is subjected to a
meticulous restoration process facilitated by the GDecoder. This
restorative procedure aims to transform fg into the features fg ,

5670

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 7, JULY 2025

aligning them with the spatial resolution of the feature map ft .
This process is characterized as follows:
fg = GDecoder(fh ).

(3)

A dropout layer is also incorporated into this architecture,
strategically designed to mitigate the risk of network overfitting.
The computation of the reconstruction loss for the GDecoder
is formulated as follows:

ft − fg 2F .
(4)
LG = (hwc)−1
c

LDecoder, comprising upsampling, convolutional, and
dropout layers, takes the output feature fh from SEncoder2 as
input to generate structure feature fs , as defined by the following
formula:

Fig. 4. Quantitative results on MVTec LOCO AD dataset for anomaly
detection, as measured on the average image-AUROC.

fs = Lecoder(fh ).

IV. EXPERIMENTS

(5)

The structural loss function LL is formulated as follows:

LL = (hwc)−1
ft − fs 2F .
(6)
c

We design a self-supervised distillation loss LSG to enhance
feature consistency across different components, defined as follows:

fg − fl 2F .
(7)
LSG = (hwc)−1
c

The overall loss of the model is
Ltotal = αLL + βLG + γLSG

(8)

where α, β, and γ are used to adjust the relative contributions
of the three loss terms.
C. Anomaly Map
In the testing phase, we use the difference between SEncoder1
and GDecoder as logical anomaly score Ag .
The structural anomaly scores As are computed by comparing
the output feature fs of the LDecoder with the feature ft from the
teacher network Ft , indicating the model’s capability to detect
structural anomalies. After obtaining both the structural anomaly
scores As and the logical anomaly scores Ag , we normalize them
to ensure that they are on similar scales. This normalization is
critical because the disparity in scale could cause noise from one
graph to obscure accurate detection in the other when combined.
Following the approach used in Efficient AD, we compute the
set of all pixel anomaly scores in the validation image for both
anomaly maps. Then, two p-quantiles are computed separately
for each set, and a linear transformation is performed for each.
The structural and logical anomaly scores are then normalized by
their respective linear transformations. Finally, the normalized
scores are interpolated to the original image size and then
summed to give the overall anomaly score, which is denoted
as A. The process can be written as follows:
A = ϕ(As ) + ϕ(Ag )
where ϕ represents the linear interpolation operation.

(9)

A. Experimental Setup
To validate the effectiveness of our proposed method, the
empirical evaluations on the MVTec LOCO AD, MVTec AD,
and VisA datasets are performed.
MVTec LOCO AD dataset [28], specifically tailored for
unsupervised anomaly detection, was provided by MVTec in
Germany. MVTec LOCO AD dataset is designed to challenge
and benchmark SOTA methods in the field. Notably, the MVTec
Logical Constraints Anomaly Detection dataset is currently one
of the most challenging datasets available. It simulates realworld scenarios in industrial inspection, with data collected and
produced directly from production lines. Structural anomalies,
such as scratches, dents, and contamination, are common occurrences in industrial settings. Logical anomalies, on the other
hand, involve misplacements of objects or the appearance of
allowed objects in invalid locations. This dataset encompasses
five authentic subdatasets, featuring a training set with 1772
normal images for training, 304 normal images for validation,
and 1568 images for testing.
VisA dataset [32] is comprised of 12 subsets, each corresponding to different objects, as illustrated in Fig. 5. In total, there are
10 821 images, including 9621 normal samples and 1200 anomalous samples. Among these subsets, four represent various
types of printed circuit boards (PCBs), which feature relatively
complex structures incorporating components, such as transistors, capacitors, and chips. In addition, the dataset includes
four subsets—Capsules, Candles, Macaroni1, and Macaroni2—
where multiple instances within a single view vary significantly
in their locations and poses. Another four subsets consist of
Cashew, Chewing Gum, Fryum, and Pipe Fryum, where the
objects are more roughly aligned. The anomalous images capture
a range of flaws, encompassing surface defects such as scratches,
dents, color spots, and cracks, as well as structural defects like
misplaced or missing parts. Each defect type is represented by
5 to 20 images, and it is common for a single image to display
multiple defects.
MVTec AD dataset [33] is one of the most challenging
anomaly detection datasets mainly dominated by structural
anomalies. These anomalies may arise due to object damage,
defects, deformations, or other structural issues. It consists of

XU et al.: MULTITASK HYBRID KNOWLEDGE DISTILLATION FOR UNSUPERVISED ANOMALY DETECTION

Fig. 5.

5671

Visualization of anomaly localization results on different categories of MVTec LOCO AD dataset and VisA dataset.

15 real-world sub-datasets including five classes of textures and
ten classes of objects.
Retinal OCT Dataset [34], from the spectralis OCT system
(Heidelberg Engineering, Germany), serves as a vital resource
for evaluating anomaly detection in retinal images. This dataset
comprises four distinct categories: choroidal neovascularization
(CNV), diabetic macular edema (DME), Drusen, and a normal control group. For a balanced and fair comparison, the
dataset is meticulously divided into training and test sets by
the publisher. The training set consists of a substantial 26 315
normal images. The test set is composed of 1000 images—250
normal and 750 abnormal—encompassing the three mentioned
disease categories (CNV, DME, and Drusen). Utilizing the
normal images from the original training set, our model is
trained to recognize the standard retinal features. Subsequently,
we evaluate performance on the complete test set, enabling a
comprehensive assessment of our model’s ability to accurately
identify anomalies.
Training details: We implement our method based on the PyTorch framework and train it from scratch using a machine with
one NVIDIA GeForce RTX 3090 GPU. All images are resized to
a resolution of 256 × 256. The one-model-per-category setting
from previous studies is followed. For dataset segmentation, we
use the predefined splits for training, validation, and testing provided with the publicly available datasets, ensuring consistency
across all experiments and comparability with prior work. Each
student is trained for 80 000 epochs with a batch size of 1. The
Adam optimizer is used with a learning rate of 10−4 and weight
decay of 10−5 . When 76 000 rounds have passed, the learning
rate is reduced to 10−5 . During the training phase, the dropout
ratio is set at 0.2. The anomaly score map A is resized back to
the original image resolution using bilinear interpolation.
To assess the effectiveness of our proposed approach, we
include a variety of classical and SOTA methods for comparison
as follows.

1) AE [12], VAE [21], and f-AnoGAN [20] are well-known
reconstruction-based techniques. It employs encoder–
decoder architecture, utilizing image reconstruction errors or feature reconstruction errors to identify anomalies.
2) SPADE [27], Patch Core [8], and PaDiM [19] record the
feature representations of normal samples during training
and detect anomalies by comparing test sample representations against these stored features.
3) VM [25] and MNAD [26] are traditional methods of
anomaly detection.
4) S-T [14], RD [15], GCAD [28], DSKD [18], THFR [13],
and Efficient AD [17] transfer knowledge of normal patterns from pretrained teacher network to a simpler student
network, enhancing anomaly detection performance.
5) DRAEM [31] and SimpleNet [29] introduce artificially
generated defective images into the training process,
enabling models to learn to differentiate between these
synthetic anomalies and normal examples.
6) FastFlow [30] relies on flow-based models to estimate the density of normal data. Normal examples
are expected to exhibit high likelihood under the
learned distribution, while anomalies fall outside this
range.
Evaluation metrics: To evaluate no-threshold image-level
anomaly detection, we use the area under the receiver operating characteristic curve (AUROC) as the main metric, which
measures an algorithm’s ability to distinguish between normal and anomalous samples. To evaluate anomaly localization, AUROC is a suitable metric as it can measure algorithm performance in detecting structural anomalies. However,
for logical anomalies such as missing objects, annotating and
segmenting each pixel is difficult. The saturated per-region
overlap (sPRO) metric [28] is used. This is an extended version of the PRO metric used to assess anomaly localization
performance.

5672

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 7, JULY 2025

TABLE I
QUANTITATIVE RESULTS ON MVTEC LOCO AD DATASET FOR ANOMALY LOCALIZATION, AS MEASURED ON PIXEL-SPRO

B. Anomaly Detection and Localization
Results on MVTec LOCO AD: We compared our proposed
method with the current SOTA techniques, and the quantitative
results are summarised in Table I. Experimental data for all
comparison methods were derived from the results reported
in the respective papers. As shown in Table I, it is clear that
distillation-based methods (e.g., GCAD [28], THFR [13], and
Efficient AD [17]) outperform others in detecting both structural
and logical anomalies. In comparison to other representationand reconstruction-based methods, our proposed approach
achieves the best performance in terms of pixel-sPRO and
image-level AUROC. Specifically, the pixel-sPRO surpasses the
SOTA by an average of 3.1%, reaching 82.9%. As illustrated in
Fig. 4, with an image AUROC of 0.91, our method demonstrates
a high level of reliability in distinguishing between normal
and anomalous images. The clear advantage over Efficient AD,
despite its already remarkable performance, underscores the
superior robustness and precision of our approach.
Our method also achieved clear advantages in challenging
scenarios, such as breakfast boxes, screw bags, splicing connectors, and pushpins, where complex contextual logic constraints present considerable difficulties for other techniques.
In the screw bags and pushpins categories, both logical and
structural anomalies tend to be small in scale, and normal
images often exhibit irregular arrangements. Our proposed
self-distillation strategy effectively mitigates the issue of false
positives caused by these subtle differences, while the shared
encoder structure is optimized to capture the diverse characteristics of normal images. These design choices contribute to the
superior performance of our method in detecting anomalies under these challenging conditions, highlighting its effectiveness
and robustness across various demanding anomaly detection
scenarios.

Beyond quantitative assessments, our qualitative findings
on the MVTec LOCO AD datasets are illustrated in the last
five rows of Fig. 5. As visualized in each row, the anomaly
maps highlight defective regions with sharp boundaries while
maintaining low false-positive rates in the surrounding areas,
demonstrating strong foreground–background separation capabilities. For example, in cases such as “Splicing Connectors,”
“Pushpins,” and “Juice Bottle,” the high-response regions align
almost perfectly with the ground truth annotations, achieving
exceptional pixel-wise accuracy. In addition, Table I presents
notable pixel-sPRO scores on MVTec LOCO AD, where our
approach consistently outperforms existing methods, such as
PatchCore, GCAD, and THFR. Both quantitative and qualitative results demonstrate that our model achieves outstanding
performance across multiple benchmarks, effectively detecting
and precisely localizing anomalies at the pixel level.
Results on VisA: The performance of our anomaly detection
method was rigorously evaluated using the VisA dataset, with
the results summarized in Table II. Our approach achieved
exceptional results in both image-level anomaly detection (measured by image-AUROC) and anomaly localization (measured
by pixel-AUROC). Specifically, it achieved impressive scores
of 97.5% for image-level and 99.1% for pixel-level anomaly
detection, exceeding the current leading technology by 0.7%
and 0.3%, respectively. The results of the visualization of the
Visa dataset are shown in the first two rows of Fig. 5, where the
accurate localization in different PCBs and Macaroni highlights
the robustness and reliability of our method. These results highlight its capability to consistently detect and localize defects
with high accuracy, making it an indispensable and valuable
tool for effective anomaly detection in industrial applications.
It is worth noting that achieving improvements in established
performance metrics is challenging due to the maturity of current
SOTA technologies. This achievement highlights the advanced

XU et al.: MULTITASK HYBRID KNOWLEDGE DISTILLATION FOR UNSUPERVISED ANOMALY DETECTION

5673

TABLE II
QUANTITATIVE RESULTS ON VISA AND MVTEC AD DATASET FOR ANOMALY LOCALIZATION, AS MEASURED ON IMAGE-AUROC/PIXEL-AUROC

TABLE III
QUANTITATIVE RESULTS ON RETINAL OCT DATASET FOR ANOMALY
DETECTION

capabilities of our method in detecting anomalies accurately and
efficiently.
Results on Retinal OCT Dataset: To validate the generalizability of our method, we conducted experiments on the retinal
OCT dataset, which features medical images that are fundamentally different from industrial datasets. For performance
evaluation, we use five key metrics commonly employed in
medical applications: area under the curve (AUC), F1-score,
average classification accuracy (ACC), sensitivity (SEN), and
specificity (SPE). As detailed in Table III, our anomaly detection method achieves exceptional performance with an AUC of

99.24%, an F1-score of 98.21%, and an accuracy of 97.52%.
These results not only surpass those of existing SOTA methods
but also highlight the robustness of our approach across diverse
domains. In addition, the F1-score indicates a strong balance between precision and recall, crucial for minimizing false positives
and ensuring accurate anomaly detection in clinical settings. A
significant factor contributing to this success is our innovative
hybrid distillation strategy, which leverages self-distillation to
enhance the detection of subtle anomalies. This approach effectively mitigates issues related to reconstruction quality in
the logical branch, reducing false positives that can arise from
minor variations. Overall, the consistent improvement across all
metrics underscores the robustness of our method.
Results on MVTec AD: To demonstrate the superiority and
practicality of our proposed method, we conducted a comparative analysis with several SOTA methods on the well-established
MVTec AD dataset. The quantitative results are presented in
Table II. It is important to note that the MVTec AD dataset predominantly consists of structural anomalies, typically a single
target object against a simple background. We also employed an
early stopping strategy in our experiments. The results in Table II
clearly indicate that our proposed method achieves outstanding
performance. Specifically, our method attains an image-level
AUROC of 99.4%, demonstrating its superior capability in
detecting anomalies at a high level of accuracy. Moreover, for

5674

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 7, JULY 2025

TABLE IV
ABLATION EXPERIMENTS ON THE MVTEC LOCO AD DATASET

anomaly localization, our method achieves a pixel-level AUROC
of 98.5%, indicating its exceptional precision in identifying the
exact locations of anomalies within images. These results underscore the effectiveness of our method in both anomaly detection
and localization tasks. The high AUROC scores achieved by
our method demonstrate its exceptional ability to accurately
differentiate between normal and anomalous regions. This high
level of accuracy is particularly crucial for practical applications,
such as quality control and automated inspection systems, where
reliable identification and localization of defects are essential.
The integration of early stopping, combined with our method’s
ability to effectively learn both object-level and fine-grained
details, contributes to its superior performance in identifying
and localizing anomalies. This underscores the practicality and
robustness of our approach in real-world scenarios where precision and reliability are paramount.

Fig. 6. Visualization results for one of the channels of our proposed
approach.

C. Ablation Analysis
To validate the effectiveness of our method, we conducted ablation experiments to assess the contributions of self-distillation
loss and the SEncoder2 module to anomaly detection performance. As shown in Table IV, incorporating self-distillation
loss significantly improves all metrics, with Structural AUROC
reaching 0.812, Logical AUROC 0.673, Mean AUROC 0.742,
and Image-AUROC 0.830. The self-distillation loss facilitates
the refinement of features by leveraging the network’s own
predictions as a form of “soft supervision,” leading to enhanced
feature representations that improve the model’s ability to detect
both structural and logical anomalies. When combined with the
SEncoder2 module, overall performance is further enhanced, underscoring the complementary nature of these two components.
The output of GDecoder, fg (first column of the third row in
Fig. 6), may lead to false alarms when directly compared with the
output of the teacher network, ft (second column of the third row
in Fig. 6), due to the feature degradation during the spatial transformation. To address this issue, we develop a self-distillation
loss mechanism that replaces the output of SEncoder1 with the
output of the teacher network thereby improving the accuracy
of anomaly detection. We further analyzed the effects of loss
components by varying the hyperparameter ratios α, β, and γ
on the MVTec LOCO AD dataset. This analysis focused not
only on identifying the optimal combination of parameters but
also on understanding the underlying reasons for performance
variations across different settings. The results in Fig. 7 show that
the self-distillation loss ratio is too low, the model under-utilizes
the teacher guidance, leading to weaker alignment between the
GDecoder’s output and the teacher features. Conversely, an

Fig. 7. Results for different proportions of the hyperparameters α, β,
and γ on the MVTec LOCO AD dataset.
TABLE V
COMPUTATIONAL EFFICIENCY ANALYSIS EXPERIMENTS ON THE MVTEC
LOCO AD DATASET

excessively high self-distillation ratio tends to overshadow the
reconstruction-focused losses, potentially harming the model’s
ability to capture subtle anomalies.
In summary, the ablation experiments demonstrate that both
self-distillation loss and the SEncoder2 module are essential for
achieving superior anomaly detection performance.
D. Computational Efficiency Analysis
We compared our method with other representative approaches, focusing on computational efficiency and practical
deployment. Table V provides metrics including Pixel-sPRO,
parameters, floating point operations per second (FLOPs), latency (ms), and throughput (img/s), offering a comprehensive
evaluation. Our method strikes an effective balance between
performance and efficiency, with 35 million parameters and 234
billion FLOPs, comparable to EfficientAD’s 21 million parameters and 235 billion FLOPs. Importantly, it achieves a latency of

XU et al.: MULTITASK HYBRID KNOWLEDGE DISTILLATION FOR UNSUPERVISED ANOMALY DETECTION

8.2 ms and a throughput of 151 img/s, meeting real-world industrial requirements. In terms of anomaly detection, our method
achieves the highest Pixel-sPRO value of 0.829, significantly
outperforming EfficientAD’s 0.798. In summary, our method’s
ability to strike a commendable balance between computational
efficiency and practical applicability. Its superior performance
metrics, combined with low latency and high throughput, ensure
that our approach is not only robust in theory but also viable for
deployment in real-time industrial scenarios.
V. CONCLUSION
Our proposed multitask hybrid knowledge distillation method
for anomaly detection and localization incorporates two essential techniques: multitask student networks and self-distillation
loss. This hybrid distillation approach minimizes false positives
that often arise from image reconstruction blurring due to feature
compression in the logical branch. Employing this approach,
we attained SOTA performance on the MVTec LOCO AD
dataset and achieved competitive results on the MVTec AD and
VisA datasets. Our method offers a robust and straightforward
solution for addressing the complexities of anomaly detection,
demonstrating its potential applicability and effectiveness across
a range of industrial scenarios. However, the performance of
knowledge distillation-based methods heavily depends on the
quality of the reconstructed image. Due to the presence of the
bottleneck layer, the detection effectiveness may decrease if the
anomalies are too small or too similar to the background. In
the future, with the rise of large-scale models, general-purpose
zero-shot anomaly detection driven by such models is expected
to gain widespread attention and experience continuous development.
REFERENCES
[1] X. Tao, D. Zhang, W. Ma, Z. Hou, Z. Lu, and C. Adak, “Unsupervised
anomaly detection for surface defects with dual-siamese network,” IEEE
Trans. Ind. Informat., vol. 18, no. 11, pp. 7707–7717, Nov. 2022.
[2] Y. Zhang, X. Nie, R. He, M. Chen, and Y. Yin, “Normality learning in
multispace for video anomaly detection,” IEEE Trans. Circuits Syst. Video
Technol., vol. 31, no. 9, pp. 3694–3706, Sep. 2021.
[3] R. Chalapathy and S. Chawla, “Deep learning for anomaly detection: A
survey,” 2019, arXiv:1901.03407.
[4] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A survey,”
ACM Comput. Surveys, vol. 41, no. 3, 2009, Art. no. 15.
[5] S. Zhang et al., “Influence-aware attention networks for anomaly detection
in surveillance videos,” IEEE Trans. Circuits Syst. Video Technol., vol. 32,
no. 8, pp. 5427–5437, Aug. 2022.
[6] G. Wang, S. Han, E. Ding, and D. Huang, “Student-teacher feature pyramid
matching for anomaly detection,” 2021, arXiv:2103.04257.
[7] J. Jiang et al., “Masked swin transformer Unet for industrial anomaly
detection,” IEEE Trans. Ind. Informat., vol. 19, no. 2, pp. 2200–2209,
Feb. 2023.
[8] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler,
“Towards total recall in industrial anomaly detection,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit., 2022, pp. 14318–14328.
[9] T. Reiss, N. Cohen, L. Bergman, and Y. Hoshen, “PANDA: Adapting
pretrained features for anomaly detection and segmentation,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2021, pp. 2806–2814.
[10] M. Xu, X. Zhou, X. Gao, W. He, and S. Niu, “Discriminative feature
learning framework with gradient preference for anomaly detection,” IEEE
Trans. Instrum. Meas., vol. 72, 2022, Art. no. 5003410.
[11] W. Liu et al., “Towards visually explaining variational autoencoders,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2020,
pp. 8642–8651.

5675

[12] J. An and S. Cho, “Variational autoencoder based anomaly detection using
reconstruction probability,” Special Lecture IE, vol. 2, no. 1, pp. 1–18,
2015.
[13] H. Guo et al., “Template-guided hierarchical feature restoration for
anomaly detection,” in Proc. IEEE/CVF Int. Conf. Comput. Vis., 2023,
pp. 6447–6458.
[14] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Uninformed
students: Student-teacher anomaly detection with discriminative latent
embeddings,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2020, pp. 4183–4192.
[15] H. Deng and X. Li, “Anomaly detection via reverse distillation from
one-class embedding,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2022, pp. 9737–9746.
[16] M. Salehi, N. Sadjadi, S. Baselizadeh, M. H. Rohban, and H. R.
Rabiee, “Multiresolution knowledge distillation for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2021,
pp. 14902–14912.
[17] K. Batzner, L. Heckler, and R. König, “EfficientAD: Accurate visual anomaly detection at millisecond-level latencies,”
in Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis., 2024,
pp. 128–138.
[18] J. Zhang, M. Suganuma, and T. Okatani, “Contextual affinity distillation
for image anomaly detection,” in Proc. IEEE/CVF Winter Conf. Appl.
Comput. Vis., 2024, pp. 149–158.
[19] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “PaDiM:
A patch distribution modeling framework for anomaly detection
and localization,” in Proc. Int. Conf. Pattern Recognit., 2021,
pp. 475–489.
[20] T. Schlegl, P. Seeböck, S. M. Waldstein, G. Langs, and U. SchmidtErfurth, “f-AnoGAN: Fast unsupervised anomaly detection with generative adversarial networks,” Med. Image Anal., vol. 54, pp. 30–44,
2019.
[21] P. Bergmann, S. Löwe, M. Fauser, D. Sattlegger, and C. Steger, “Improving
unsupervised defect segmentation by applying structural similarity to
autoencoders,” 2018, arXiv:1807.02011.
[22] X. Yan, H. Zhang, X. Xu, X. Hu, and P.-A. Heng, “Learning semantic
context from normal samples for unsupervised anomaly detection,” in
Proc. AAAI Conf. Artif. Intell., 2021, pp. 3110–3118.
[23] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image
recognition,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2016, pp. 770–778.
[24] M. Rudolph, T. Wehrbein, B. Rosenhahn, and B. Wandt, “Asymmetric student-teacher networks for industrial anomaly detection,” in Proc.
IEEE/CVF Winter Conf. Appl. Comput. Vis., 2023, pp. 2592–2602.
[25] C. Steger, M. Ulrich, and C. Wiedemann, Machine Vision Algorithms and
Applications, Wiley, 2018.
[26] H. Park, J. Noh, and B. Ham, “Learning memory-guided normality for
anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2020, pp. 14372–14381.
[27] N. Cohen and Y. Hoshen, “Sub-image anomaly detection with deep pyramid correspondences,” 2020, arXiv:2005.02357.
[28] P. Bergmann, K. Batzner, M. Fauser, D. Sattlegger, and C. Steger, “Beyond
dents and scratches: Logical constraints in unsupervised anomaly detection
and localization,” Int. J. Comput. Vis., vol. 130, no. 4, pp. 947–969,
2022.
[29] Z. Liu, Y. Zhou, Y. Xu, and Z. Wang, “SimpleNet: A simple network
for image anomaly detection and localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2023, pp. 20402–20411.
[30] J. Yu et al., “FastFlow: Unsupervised anomaly detection and localization
via 2D normalizing flows,” 2021, arXiv:2111.07677.
[31] V. Zavrtanik, M. Kristan, and D. Skočaj, “DRAEM-A discriminatively trained reconstruction embedding for surface anomaly
detection,” in Proc. IEEE/CVF Int. Conf. Comput. Vis., 2021,
pp. 8330–8339.
[32] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, “Spot-the-difference
self-supervised pre-training for anomaly detection and segmentation,” in
Proc. Eur. Conf. Comput. Vis., 2022, pp. 392–408.
[33] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec AD–
A comprehensive real-world dataset for unsupervised anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2019,
pp. 9592–9600.
[34] D. S. Kermany et al., “Identifying medical diagnoses and treatable diseases
by image-based deep learning,” Cell, vol. 172, no. 5, pp. 1122–1131, 2018.
[35] T. D. Tien et al., “Revisiting reverse distillation for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2023,
pp. 24511–24520.

5676

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 7, JULY 2025

[36] W. Liu, H. Chang, B. Ma, S. Shan, and X. Chen, “Diversity-measurable
anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2023, pp. 12147–12156.
[37] S. Akcay, A. A.-Abarghouei, and T. P. Breckon, “GANomaly: Semisupervised anomaly detection via adversarial training,” in Proc. Asian
Conf. Comput. Vis., 2019, pp. 622–637.
[38] H. Zhao et al., “Anomaly detection for medical images using selfsupervised and translation-consistent features,” IEEE Trans. Med. Imag.,
vol. 40, no. 12, pp. 3641–3651, Dec. 2021.
[39] S. Lu, W. Zhang, H. Zhao, H. Liu, N. Wang, and H. Li, “Anomaly
detection for medical images using heterogeneous auto-encoder,” IEEE
Trans. Image Process., vol. 33, pp. 2770–2782, 2024.

Muhao Xu received M.S. degree in computer
science and technology from the School of Information Science and Engineering, University
of Jinan, Shandong, China, in 2024. He is currently pursuing the Ph.D. degree in mechanical
engineering at Shandong University, Shandong,
China.
His research interests include medical image
processing, anomaly detection and multimodal
information mining.

Cuiping Zhu is currently working toward the
master’s degree in computer science and technology with the Visual Computing and Perception Innovation Team, School of Information
Science and Engineering, University of Jinan,
Guangzhou, China.
With image anomaly detection as her core
research direction, she focuses on exploring
the innovative application of deep learning and
text information in image anomaly detection. It
includes single-class anomaly detection, multiclass anomaly detection and small-sample anomaly detection. During
her postgraduate study, she wrote two academic papers, focusing on
text-guided multiclass anomaly detection algorithms.

Guang Feng received the Ph.D. degree in signal and information processing from the Dalian
University of Technology, Dalian, China, in 2022.
He is currently an Associate Professor with
the Shandong Provincial Key Laboratory of Network Based Intelligent Computing, School of Information Science and Engineering, University
of Jinan, Jinan, China. His research interests include referring expression comprehension and
saliency detection.

Sijie Niu received the B.S. degree from the
School of Computer Science, Liaocheng University, Liaocheng, China, in 2007, and the Ph.D.
degree from the School of Computer Science,
Nanjing University of Science and Technology,
Nanjing, China, in 2016.
He was a Visiting Scholar with Stanford University, Stanford, CA, USA, in 2014. Now, he is a
Postdoctoral with medical image analysis, UNC,
Chapel Hill, NC, USA. He is currently a Professor with the School of Information Science and
Engineering, University of Jinan, Jinan, China. His research interests
include Pattern recognition, machine learning, image processing, and
medical image analysis.
PAPER_TEXT
