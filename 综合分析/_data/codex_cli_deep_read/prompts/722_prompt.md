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
# [722] Learning With Noisy Labels for Industrial Time Series Outlier Detection: A Transformer-Embedded Contrastive Learning Framework
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
编号：722
题名：Learning With Noisy Labels for Industrial Time Series Outlier Detection: A Transformer-Embedded Contrastive Learning Framework
年份：2025
DOI：10.1109/tii.2025.3616850
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2025.3616850.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：时序、日志、KPI 与云原生异常检测
相关性：弱相关，分数 
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\722.txt
- 原始字符数：56213
- 本次发送字符数：56213
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 2, FEBRUARY 2026

903

Learning With Noisy Labels for Industrial
Time Series Outlier Detection: A
Transformer-Embedded Contrastive
Learning Framework
Jingzhong Fang , Member, IEEE, Zidong Wang , Fellow, IEEE, Weibo Liu , Member, IEEE,
Nianyin Zeng , Senior Member, IEEE, Yimeng He , Yu Cao, Linwei Chen , and Xiaohui Liu

Abstract—In many real-world industrial scenarios, acquiring accurately labeled data are often challenging due
to limited resources or unexpected errors. Learning with
noisy labels (LNL) has emerged as a significant research
topic, aiming to develop reliable deep learning models using noisy-labeled training data. In this article, a
novel Transformer-embedded LNL framework with fuzzyclustering-assisted contrastive learning is developed for
industrial time series outlier detection under noisy labels.
Specifically, a fuzzy-clustering-assisted contrastive learning strategy is proposed to enhance the robustness of the
Transformer encoder against noisy labels by leveraging
the intrinsic characteristics of raw data. Furthermore, a
dynamic two-stage training scheme is introduced to train
the outlier detector. In the first training stage, the Transformer encoder is pretrained through data reconstruction
to improve feature extraction capabilities for industrial time
series. In the second stage, the outlier detector is jointly
trained with the Transformer encoder, incorporating a joint
learning strategy. Furthermore, a label-consistency regularization term is designed to enhance the robustness of
the outlier detector against noisy labels by minimizing the
discrepancy between the outputs of the outlier detector
and the clustering algorithm. The proposed framework is
applied to industrial time series data collected from a realworld wire arc additive manufacturing (WAAM) process. Experimental results demonstrate that the developed framework outperforms selected representative LNL approaches
Received 10 August 2025; revised 13 September 2025; accepted 22
September 2025. Date of publication 22 October 2025; date of current
version 5 February 2026. This work was supported in part by the Independent Innovation Foundation of AECC under Grant ZZCX-2023-005,
in part by the Natural Science Foundation for Distinguished Young
Scholars of the Fujian Province of China under Grant 2023J06010, in
part by the National Key Research and Development Program of China
under Grant 2024YFC3407000, in part by the Royal Society of the U.K.,
and in part by the Alexander von Humboldt Foundation of Germany.
Paper no. TII-25-5427. (Corresponding author: Zidong Wang.)
Jingzhong Fang, Zidong Wang, Weibo Liu, Yu Cao, Linwei Chen,
and Xiaohui Liu are with the Department of Computer Science, Brunel
University London, UB8 3PH Uxbridge, U.K. (e-mail: Zidong.Wang@
brunel.ac.uk).
Nianyin Zeng is with the Department of Instrumental and Electrical Engineering, Xiamen University, Xiamen 361102, China (e-mail:
zny@xmu.edu.cn).
Yimeng He is with the State Key Laboratory of Industrial Control Technology, College of Control Science and Engineering, Zhejiang University, Hangzhou 310027, China Digital Object Identifier
10.1109/TII.2025.3616850

in WAAM outlier detection under both low and high noise
ratios.
Index Terms—Industrial time series analysis, learning
with noisy labels (LNL), outlier detection, weakly supervised learning.

I. INTRODUCTION
EEP learning (DL) has been extensively studied in recent
years due to its remarkable ability to process large-scale
data and its superior performance in feature extraction [17].
In DL, the quality of training data are crucial in determining
the overall effectiveness of DL models. The accuracy of labels within the training dataset is of paramount importance, as
mislabeled data (commonly referred to as noisy labels) may
introduce misleading information during training, thereby impairing the model’s generalization ability and degrading overall
performance in real-world applications.
To mitigate the adverse effects of noisy labels on DL models,
learning with noisy labels (LNL) has recently been investigated
extensively, leading to the proposal of numerous approaches [9],
[11], [15], [23], [33], [36]. Among existing LNL methods,
sample selection, label correction, and robust training have been
recognized as three prominent categories due to their satisfactory
performance and ease of implementation. Specifically, sample
selection and label correction approaches aim to enhance the
quality of training labels by identifying correctly labeled samples and rectifying noisy labels, respectively. Meanwhile, robust
training approaches focus on developing noise-robust training
strategies or model architectures to mitigate the influence of
noisy labels during model training.
It should be noted that sample selection approaches may lead
to the exclusion of potentially valuable data, thereby reducing
the diversity and completeness of the training set. Meanwhile,
label correction approaches can introduce further errors if the
corrected labels are inaccurate, ultimately misleading the training process and potentially reinforcing incorrect patterns in the
model. Furthermore, each data point in an industrial time series
contains essential intrinsic and structural information, which is
critical for accurately identifying outliers, preserving temporal

D

1941-0050 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html
for more information.

904

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 2, FEBRUARY 2026

dependencies, and maintaining feature integrity in the presence
of noisy labels [9].
To establish a reliable outlier detection model based on robust
training approaches, the extraction of inherent patterns and
features from industrial data is of critical importance. As a
powerful family of feature extraction techniques, encoder-based
methods have been widely employed in robust training-based
LNL approaches due to their capability of capturing complex
data representations [2], [25]. Among encoder-based methods,
the Transformer has been particularly effective in handling time
series data, primarily due to its self-attention mechanism [27].
The Transformer encoder allows multivariate time series to be
processed simultaneously while capturing dependencies across
different dimensions, thereby eliminating the need for data
preprocessing [29].
It is worth mentioning that the standard training scheme of the
Transformer encoder typically follows a supervised approach,
which is susceptible to the adverse effects of noisy labels.
In contrast, self-supervised learning (SSL) has emerged as a
viable alternative, as it does not rely on label information during
training. Among SSL techniques, contrastive learning has been
particularly effective, as it aims to bring similar (i.e., positive)
samples closer together while pushing dissimilar (i.e., negative)
samples further apart. To date, contrastive learning has been
widely adopted in robust training-based LNL approaches for
constructing reliable encoders [14], [25].
Existing LNL approaches based on contrastive learning identify positive and negative sample pairs through data augmentation [13], [20]. Nevertheless, conventional data augmentation methods often fail to capture the intricate characteristics
of time series data and tend to increase computational costs,
particularly when handling large-scale datasets. To overcome
these limitations, clustering algorithms, which group similar
data points into distinct clusters based on inherent features,
have been successfully employed for selecting positive and
negative sample pairs in contrastive learning [4]. Recognized as a
well-established clustering algorithm, the fuzzy C-means (FCM)
algorithm enables data points to belong to multiple clusters
with varying degrees of membership, leveraging fuzzy logic
principles. Compared with hard clustering algorithms, FCM is
not only easier to implement but also offers greater flexibility in
handling complex data distributions. However, its performance
may degrade when applied to high-dimensional data, primarily
due to the presence of sparse and redundant features extracted
by the Transformer encoder [8].
A seemingly natural solution for clustering high-dimensional
data is to adopt the uniform manifold approximation and projection (UMAP) method, which serves as a competitive manifoldlearning-based dimensionality reduction technique, in order to
obtain a low-dimensional embedding from the high-dimensional
input [1], [30]. The extracted low-dimensional representation
can then serve as the input for the FCM algorithm, improving
clustering effectiveness while mitigating the impact of irrelevant features. It is noticeable that clustering algorithms have
been widely utilized in outlier detection as they are capable of
uncovering the intrinsic structures and relationships within data,

thereby providing valuable insights. As such, beyond determining positive and negative sample pairs, the partitions generated
by the FCM algorithm can also be leveraged for model regularization, further enhancing the model’s generalization ability and
overall performance.
Motivated by the above discussions, this article proposes
a novel Transformer-embedded LNL framework with fuzzyclustering-assisted contrastive learning (TFCCL) for outlier detection in industrial time series data with noisy labels. Specifically, a fuzzy-clustering-assisted contrastive learning (FCCL)
approach is developed to train the Transformer encoder, where
the UMAP-based FCM (UFCM) algorithm is introduced to
determine positive and negative sample pairs for contrastive
learning based on clustering results. A dynamic two-stage
scheme is formulated for training the outlier detector. In the
first training stage, the Transformer encoder is pretrained to
enhance its feature extraction capability on industrial time series data through data reconstruction. In the second stage, the
outlier detector is trained jointly with the Transformer encoder,
while the UFCM algorithm is dynamically updated throughout
the training process. Furthermore, a joint learning strategy is
proposed for the second training stage, incorporating a labelconsistency regularization term to minimize the discrepancy
between outputs from the outlier detector and the UFCM algorithm, thereby improving the model’s robustness against noisy
labels.
The main contributions of this article are summarized as
follows.
1) A novel FCCL strategy is proposed for training the Transformer encoder, where the UFCM algorithm is designed
to process high-dimensional features and identify positive
and negative sample pairs for contrastive learning.
2) A dynamic two-stage training scheme is introduced for
the outlier detector, where the Transformer encoder is
pretrained in the first stage via data reconstruction, and
in the second stage, the outlier detector is jointly trained
with the Transformer encoder.
3) A joint learning strategy is developed, incorporating
a label-consistency regularization term to improve the
model’s generalization ability and robustness against
noisy labels by minimizing the discrepancy between outputs from the outlier detector and the UFCM algorithm.
4) The proposed TFCCL framework is applied to outlier
detection in real-world industrial time series data with
noisy labels, specifically collected from a wire arc additive manufacturing (WAAM) pilot line. Experimental
results validate the effectiveness of the proposed TFCCL
framework.
The rest of this article is organized as follows. Section II
discusses the background of LNL and WAAM while presenting
the relevant preliminaries. In Section III, the proposed TFCCL
framework and the training scheme are introduced. Experimental results for WAAM outlier detection under noisy labels
are presented in Section IV. Finally, Section V concludes this
article and provides discussions on potential future research
directions.

FANG et al.: LEARNING WITH NOISY LABELS FOR INDUSTRIAL TIME SERIES OUTLIER DETECTION

II. BACKGROUNDS
A. Related Work
1) Learning With Noisy Labels: Existing LNL approaches
can be broadly classified into two main categories: improving
the quality of training data and mitigating the impact of noisy
labels during the training process.
The first category of LNL approaches focuses on selecting
training samples that are likely to have correct labels (i.e., clean
samples) or on correcting noisy labels within the dataset. For
instance, in [11], a classic approach known as coteaching has
been proposed, where a Siamese network structure is employed,
and each network selects low-loss samples to update its peer network, thereby improving training robustness. In [15], a sample
selection approach called DivideMix has been developed, incorporating an improved semi-supervised training strategy that
enables the model to learn from both selected clean samples and
unselected samples. Furthermore, a joint training method with
coregularization (JoCoR) has been introduced in [32], where
a joint loss function with a coregularization term is designed
to facilitate the selection of clean samples for training, thereby
enhancing model stability in the presence of noisy labels.
The second category of LNL approaches focuses on mitigating the influence of noisy labels during the training process by
designing robust DL models through specialized architectures
or noise-resistant training strategies. These methods aim to enhance model robustness without directly modifying the training
labels. For instance, in [25], a training framework has been
proposed in which an encoder, combined with an SSL approach,
is employed to improve the model’s resistance to label noise.
Similarly, in [26], a self-supervised adversarial noisy masking
framework has been introduced, where adversarial noisy masking is applied to prevent the model from overfitting to noisy
labels, while self-supervised reconstruction provides additional
noise-free supervision, thereby improving model generalization
in the presence of label noise.
2) Outlier Detection in WAAM: The WAAM is a type of
additive manufacturing (AM) technology that utilizes a continuous metal wire feedstock and an electric arc as the heat
source to melt the wire and deposit material layer by layer,
thereby constructing physical objects. Compared with other AM
technologies, WAAM is particularly suitable for manufacturing
large-scale components and offers relatively higher deposition
rates [6], [10]. Over the past few years, WAAM has been widely
adopted across various industrial sectors, including aerospace,
automotive, and power systems [10].
In WAAM, the electric arc serves as the primary heat source,
and its operation is governed by the total current and arc voltage, which directly influence the melting process, deposition
rate, and overall manufacturing quality. It should be noted that
in real-world applications, sudden fluctuations in current and
voltage may occasionally occur, potentially leading to defects
such as incomplete fusion or uneven material deposition [12].
Over the past few years, outlier detection has attracted increasing
attention in the research community due to its critical role
in various real-world applications [18], [27], [31], [38]. As a
result, in the field of WAAM, numerous approaches have been

905

developed to detect outliers, aiming to improve the WAAM
process and ensure high-quality production [5], [12], [19]. For
instance, in [5], a transfer learning approach has been introduced
for outlier detection in WAAM data under different operational
states. Furthermore, in [19], a semi-supervised method has been
proposed to enable real-time anomaly detection in WAAM using
current and voltage data, further enhancing the reliability and
stability of the manufacturing process.
B. Preliminaries
In an M -class classification task involving noisy labels, consider a noisy dataset denoted as D̃ = {(xi , ỹi )}N
i=1 , where N
denotes the number of samples, xi is the ith sample, and ỹi is the
corresponding observed (potentially noisy) label. Each sample
in D̃ is assumed to be independently and identically drawn from
a joint distribution P (X, Ỹ ), which is defined over the space
X × Ỹ. Here, X ⊂ Rd represents the input feature space, while
the label space is given by Ỹ = {ỹ ∈ {0, 1}M | ỹ1 = 1},
where each label ỹ is represented as a one-hot encoded vector,
ensuring that only a single class label is assigned per sample.
III. METHODOLOGY
A. Motivation
In the presence of noisy labels, the supervised training process
of the Transformer encoder may be adversely affected, leading
to degraded feature extraction performance. To mitigate this
issue, an effective approach is to reduce the model’s reliance
on ground-truth labels. As an SSL method, contrastive learning
leverages the intrinsic relationships among samples to learn
meaningful representations without requiring label supervision,
making it a valuable technique for improving model robustness.
In recent years, contrastive learning has been widely employed
to assist model training, particularly in LNL. For instance,
in [25], a self-supervised contrastive learning approach has been
introduced for LNL to demonstrate its effectiveness in training
both the encoder and classifier despite label noise.
It is worth noting that, in conventional contrastive learning,
positive and negative sample pairs for each data point are typically identified using data augmentation methods. However, this
approach is not well suited for large-scale time series datasets,
as it may fail to capture complex temporal dependencies and
could significantly increase computational costs. To overcome
this limitation, a clustering-based approach for selecting positive
and negative sample pairs presents a more efficient alternative.
By leveraging the underlying structural information within the
data, clustering enhances the correlation and diversity of positive and negative sample pairs while eliminating the need for
additional label information, thereby improving the reliability
of contrastive learning in noisy-label scenarios.
The FCM algorithm is a promising clustering technique for
handling noisy and large-scale data, as it employs fuzzy logic
to capture soft boundaries between clusters and assigns membership degrees to each data point across multiple clusters.
Furthermore, the membership degrees generated by FCM can
be used to regularize the classifier’s output, thereby reducing

906

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 2, FEBRUARY 2026

Fig. 1. Developed TFCCL framework, which consists of three key
components: the Transformer encoder, the FCM clustering module, and
the NN-based classifier.

the impact of label noise. To fully utilize both the inherent
features and structural information in time series data for clustering, the Transformer encoder has recently been widely employed to extract effective feature representations [4]. However,
directly using the high-dimensional features extracted by the
Transformer encoder from large-scale time series datasets may
degrade clustering performance. To overcome this challenge,
applying dimensionality reduction techniques presents a natural
and effective solution, as they can refine the extracted features
by preserving essential structures while reducing computational
complexity.
Motivated by the above discussions, in this article, a novel
TFCCL framework is developed for outlier detection on time
series data with noisy labels. Specifically, an FCCL strategy
is proposed to aid in training the Transformer encoder, where
a UFCM algorithm is designed to process high-dimensional
features and identify positive and negative sample pairs for
contrastive learning. A dynamic two-stage scheme is introduced
for training the outlier detector. In the first stage, the Transformer
encoder is pretrained to enhance feature extraction capability
on industrial time series data through data reconstruction. In
the second stage, the outlier detector is jointly trained with the
Transformer encoder, while the UFCM algorithm is dynamically
updated throughout the training process. Furthermore, a joint
learning strategy is proposed to improve the classifier’s robustness against noisy labels, incorporating a label-consistency
regularization term to minimize the discrepancy between the
outputs of the outlier detector and the UFCM algorithm.

Fig. 2. Architecture of the Transformer encoder, which comprises
multiple identical encoder layers. Each layer consists of a multihead
attention mechanism and a convolutional module.

convolutional module to mitigate gradient vanishing. Furthermore, the NN-based classifier and the decoder are implemented
as multilayer perceptrons. To enhance clustering performance,
UMAP is employed for dimensionality reduction.
C. Loss Function
1) Classification Loss: The proposed TFCCL framework is
designed to train a classifier for time series classification tasks.
Although noisy labels may negatively impact supervised learning performance, incorporating the classification loss during
training remains essential. In this article, cross-entropy is used
to compute the classification loss. The classification loss LCL is
defined as

1 
ỹij log(ŷij )
B i=1 j=1
B

LCL = −

The developed TFCCL framework is illustrated in Fig. 1,
which is designed to train a neural network-based (NN-based)
classifier for time series outlier detection in the presence of noisy
labels. The TFCCL framework consists of three key components: the Transformer encoder, the FCM clustering module,
and the NN-based classifier. As shown in Fig. 2, the Transformer encoder architecture comprises multiple identical encoder layers, each consisting of a multihead attention mechanism
and a convolutional module. Residual connections and layer
normalization are applied to both the attention layer and the

(1)

where B denotes the number of samples in the current
mini-batch; M is the number of classes; ỹij represents the jth
component of the label for the ith sample; and ŷij is the jth
component of the the predicted output for the ith sample.
2) Reconstruction Loss: The reconstruction loss is employed for pre-training the Transformer encoder. Specifically,
the mean squared error is used to calculate the reconstruction
loss LREC , which is given by
1 
xi − x̂i 2
B i=1
B

LREC =
B. Overview of the TFCCL Framework

M

(2)

where B represents the number of samples in the current minibatch; and xi and x̂i are the true value and the predicted value
of the ith sample, respectively.
3) Contrastive Loss: The contrastive loss is utilized to train
the Transformer encoder. In this article, a novel fuzzy-clusteringassisted contrastive loss LFCCL is designed, which is shown as
follows:

B
1 
z ∈P(zi ) exp(sim(zi , zj )/τ )
(3)
log  j
LFCCL = −
B i=1
zk ∈B(zi ) exp(sim(zi , zk )/τ )

FANG et al.: LEARNING WITH NOISY LABELS FOR INDUSTRIAL TIME SERIES OUTLIER DETECTION

where B is the number of samples in the current mini-batch;
zi ∈ Rd denotes the feature representation of the ith sample;
P(zi ) is the set of positive feature representations corresponding
to the ith sample; B(zi ) is the set of all feature representations in
the current mini-batch except the feature representation of the ith
sample; sim(·, ·) is the cosine similarity function between two
samples; and τ represents the temperature parameter, which is
a positive constant and controls the sharpness of the similarity
scores.
The contrastive loss in this article is formulated as a probability ratio that quantifies the likelihood of the model selecting
the correct positive pair over all other sample pairs within the
batch. The structure of the numerator and denominator reflects a
probabilistic approach to pairwise discrimination, which emphasizes the relative similarity between positive and negative pairs.
The exponential and logarithmic functions in (3) are combined
in the contrastive loss to formulate a normalized, probabilistic
objective based on the softmax and cross-entropy functions.
Remark 1: Traditional contrastive learning methods typically
identify positive and negative sample pairs for the ith sample
using augmented data or ground truth labels [20]. However,
the large volume of data and the presence of noisy labels can
interfere with the sample pairing process. To reduce computational costs and mitigate the effects of label noise, this article
introduces the FCCL strategy, where positive and negative sample pairs for the ith sample are determined based on clustering
results. Specifically, samples belonging to the same cluster as
the ith sample are considered positive, while those in different
clusters are treated as negative. The FCCL strategy enables the
Transformer encoder to be trained in an unsupervised manner,
thereby avoiding the adverse impact of noisy labels and improving its ability to extract meaningful feature representations.
4) Joint Learning Strategy: In this article, a label-consistency regularization term is introduced to quantify the discrepancy between the output membership of the UFCM algorithm
and the output probability of the classifier. Specifically, the
Kullback–Leibler (KL) divergence is employed to compute the
label-consistency regularization term LLCR , which is defined as
LLCR = DKL (P  U ) =

M

i=1


P (i) log

P (i)
U (i)


(4)

where M is the number of classes; P and U represent the distribution of the classifier’s output probability and the distribution
of the UFCM algorithm’s output membership, respectively; and
P (i) and U (i) represent the classifier’s output probability for
the ith class and the UFCM algorithm’s output membership for
the ith class, respectively.
Remark 2: The output membership of the UFCM algorithm
is independent of the noisy labels in the training data, making it
a valuable reference for mitigating the impact of label noise
on the classifier. It is important to note that KL divergence
is asymmetric, meaning that it quantifies the information loss
incurred when one probability distribution is used to approximate another, with the divergence value varying based on
the direction of comparison. Therefore, in this article, the KL
divergence DKL (P  U ) is computed instead of DKL (U  P ) as

907

the label-consistency regularization term, aiming to better align
the classifier’s predictions with the UFCM algorithm’s output
membership.
5) Overall Loss Function: The overall loss function of the
developed model consists of two parts: pretraining loss LPRE
and joint training loss L. The pretraining loss LPRE is given as
follows:
LPRE = LREC .

(5)

The joint training loss L is given by
L = μ1 LCL + μ2 LFCCL + μ3 LLCR

(6)

where μ1 , μ2 , and μ3 are three hyperparameters to balance the
weights among the classification loss, contrastive loss and labelconsistency regularization term.
D. Dynamic Two-Stage Training Scheme
1) Pretraining of the Transformer Encoder in the First Stage:

The feature representations extracted from the training data by
the Transformer encoder play a crucial role in the training process, as they are subsequently utilized by the classifier for classification and by the UFCM algorithm for contrastive learning and
regularization. Although the FCCL strategy is employed to train
the Transformer encoder, its performance is highly dependent
on the quality of initialization. To ensure the effectiveness of
FCCL and further enhance the Transformer encoder’s feature
extraction capabilities, this article employs a decoder to pretrain
the encoder through input reconstruction. As illustrated in Fig. 1,
during preraining, only the encoder and decoder parameters
are trainable, while all other parameters remain fixed. The
reconstruction loss LPRE is used as the loss function to guide
the encoder and decoder in learning stable and robust feature
representations. Pre-training allows the encoder to develop a
deeper understanding of the underlying data structure, thereby
improving training quality and overall model performance.
2) Dynamic Updating of the UFCM Algorithm in the Second
Stage: In this article, UMAP is employed before applying the

FCM algorithm to reduce the dimensionality of the Transformer
encoder output. Furthermore, cosine similarity is used to measure the similarity between data points and cluster centroids,
facilitating effective clustering of feature representations.
It should be noted that the updating frequency of the UFCM
algorithm during training is a critical hyperparameter. A low
updating frequency may cause the algorithm to become trapped
in local optima, while a high updating frequency can lead to
increased computational costs and unstable clustering performance. To address this issue, a dynamic updating strategy is
introduced to adjust the UFCM algorithm’s update frequency
throughout the training process. Specifically, the update frequency is relatively high in the early training stages and gradually decreases as training progresses. The exact epoch for
k+1
, is
performing the (k + 1)th UFCM update, denoted by eUFCM
calculated by
k+1
=
eUFCM

k ∗ (k + 1)
∗ ekUFCM .
2

(7)

908

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 2, FEBRUARY 2026

Algorithm 1: Training Procedure of the Developed TFCCL
Framework.

3) Training Procedure: The training procedure of the developed TFCCL framework is presented in Algorithm 1.

IV. OUTLIER DETECTION ON WAAM DATASETS WITH NOISY
LABELS
A. Experimental Setup
1) Data Description: The data used in this article is collected
from a pilot line for WAAM deployed in Sweden, which aims
at developing an end-to-end digital solution by integrating automation methodologies for metal component manufacturing.
Specifically, five datasets are employed in the experiments, each
representing a time series corresponding to an individual manufacturing process. Each time series consists of 98 000 instances,
where each instance contains measurements of welding current
and voltage recorded at a sampling interval of 0.0002 s during
the manufacturing process.
2) Data Preprocessing: In the experiments, each dataset is
segmented using a sliding window approach, where the window
length is set to 10 and the stride to 5. Each segment is assigned a
label (“Normal” or “Outlier”), determined based on the labels of
individual instances within the segment. Specifically, a segment
is labeled as “Normal” if all instances within it are labeled as
“Normal”; otherwise, it is classified as an “Outlier.” All labels
are converted into a one-hot format for ease of classification.
Each segmented dataset is then split into training and testing sets
in a 7 : 3 ratio. Min-max normalization is subsequently applied

to both sets to scale the data to a uniform range, further improving
the performance of outlier detection.
3) Evaluation Metrics: To comprehensively assess the performance of the developed TFCCL framework in WAAM outlier detection, essential evaluation metrics, such as accuracy,
precision, recall, and F1-score are utilized. Each experiment is
repeated five times, and the average values of these metrics are
reported to ensure the consistency and reliability of the results.
4) Baselines: In this article, several novel and representative
approaches are selected for comparison. In addition, a vanilla
outlier detection method is employed as a standard baseline for
comparison. The details of each selected approach are listed as
follows.
1) Coteaching [11], where two deep neural networks
(DNNs) are trained simultaneously and select low-loss
samples to update each other.
2) Coteaching + [37], where the disagreement-based updating strategy is combined with the original coteaching
framework.
3) JoCoR [32], where a coregularization term is employed
to help select clean samples for model training.
4) Colearning [25], where supervised learning and selfsupervised learning are combined to handle noisy labels.
5) Standard Baseline, where a classifier with the Transformer backbone is trained directly on the training data
with the presence of noisy labels.
5) Implementation Details: For fair comparisons, all experiments are carried out on a server with NVIDIA RTX A6000
GPU with 48 GB memory and Intel(R) Xeon(R) Silver 4214R
CPU. All approaches are implemented using Ubuntu 20.04.6,
Pytorch 2.5.1, Python 3.9.21 and CUDA 12.3.
It is worth mentioning that convolutional neural networks
(CNNs) are employed as the original backbone networks in
selected LNL approaches. As such, in the experiments, both
the CNN and the Transformer architectures are employed as
the backbone networks for selected approaches for comparisons
to fully investigate the competitive performance of the TFCCL
framework.
To verify the effectiveness of the FCM algorithm in the
TFCCL framework, the comparison experiment is conducted
in this paper. Specifically, the K-means algorithm and the hierarchical clustering algorithm are chosen as baseline clustering
algorithms to compare against the FCM used in the TFCCL
framework. Besides, the dynamic updating strategy of the proposed UFCM algorithm is evaluated through comparative experiments. To be specific, linear and logarithmic strategies are
selected as baselines for comparison.
The Transformer encoder consists of three encoder layers.
The CNN backbone consists of five convolutional layers and a
fully connected layer, where each convolutional layer is followed
by batch normalization. The decoder and the classifier are a
four-layer MLP and a three-layer MLP, respectively. In this
article, the hyperparameters are selected via grid search on a
held-out validation set. Each hyperparameter is explored from
a range of values and the combination that achieves the best
validation performance is selected. To be specific, the temperature parameter τ in contrastive loss LFCCL is set to 0.08. The

FANG et al.: LEARNING WITH NOISY LABELS FOR INDUSTRIAL TIME SERIES OUTLIER DETECTION

909

TABLE I
OUTLIER DETECTION PERFORMANCE OF SELECTED APPROACHES ON WAAM DATASET 1 WITH DIFFERENT NOISE RATIOS

TABLE II
OUTLIER DETECTION PERFORMANCE OF SELECTED APPROACHES ON WAAM DATASET 2 WITH DIFFERENT NOISE RATIOS

TABLE III
OUTLIER DETECTION PERFORMANCE OF SELECTED APPROACHES ON WAAM DATASET 3 WITH DIFFERENT NOISE RATIOS

hyperparameters μ1 , μ2 , and μ3 in the training loss L are set
as 0.3, 0.8, and 0.8, respectively. In the experiments, the Adam
optimizer is utilized for model training, where the learning rate
is 0.0001. The pre-training and training epochs are 15 and 50,
respectively. During the training process, the epoch number for
the first UFCM update e1UFCM is set to 3.
The noise ratio λ is an important parameter in LNL, which
indicates the ratio of the noisy labels in a dataset. It should be
noted that the outlier detection task in this article is formulated as
a binary classification problem with only two classes. As such,
symmetrical label noise is employed in the experiment, where
the label of each data point is corrupted with an equal probability defined by λ. For a comprehensive evaluation, multiple
experiments are conducted on each dataset with various values

of λ (e.g., 30%, 40%, 50%, and 60%). It should be noted that in
real-world industrial scenarios, the noise ratio usually remains
below 50%. To verify the outlier detection performance of the
TFCCL framework under severe label noise, the WAAM data
sets with a noise ratio of 60% are utilized in the experiments.
B. Evaluation of WAAM Outlier Detection
The results of WAAM outlier detection on five datasets
with noisy labels using selected approaches and the TFCCL
framework are illustrated in Tables I–V. According to the results, the TFCCL framework shows the leading performance
on five datasets with five different noise ratios. The selected
approaches using the Transformer backbone demonstrate better

910

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 2, FEBRUARY 2026

TABLE IV
OUTLIER DETECTION PERFORMANCE OF SELECTED APPROACHES ON WAAM DATASET 4 WITH DIFFERENT NOISE RATIOS

TABLE V
OUTLIER DETECTION PERFORMANCE OF SELECTED APPROACHES ON WAAM DATASET 5 WITH DIFFERENT NOISE RATIOS

performance than those using the CNN backbone. A detailed
evaluation of different noise ratios is presented below.
1) 30% and 40% Noisy Labels: It can be found that all
selected approaches with different backbones as well as the
TFCCL framework all achieve satisfactory performance on five
data sets. The standard approach also shows acceptable performance under 30% noise ratio. As indicated by the results,
the TFCCL framework outperforms the other approaches on
most datasets in terms of accuracy, precision, recall, and F1
score. Notably, on dataset 2 with a 30% noise ratio, coteaching,
coteaching+ and colearning (with both backbones) all achieve
higher accuracy than TFCCL. Datasets 1 and 2 with noise
ratios of 30%, colearning-transformer has higher accuracy than
TFCCL. On datasets 2, 3, and 5 with noise ratios of 30%
and 40%, JoCoR-CNN has higher accuracy than TFCCL as
well. Nevertheless, TFCCL attains the highest performance on
the remaining metrics in these scenarios, which demonstrates
the overall effectiveness of TFCCL in outlier detection with a
relatively small number of labels.
2) 50% Noisy Labels: In the scenario with a 50% noise
ratio, the TFCCL remains superior performance, whereas the
performance of all selected approaches decreases significantly
on all five datasets. Specifically, the accuracy and the F1 score
of the selected approaches are no more than 88% and 78%,
respectively. For TFCCL, the accuracy and the F1 score across
five datasets exceed 91% and 88%, respectively, which shows
the robustness of TFCCL against a moderate number of noisy
labels.

3) 60% Noisy Labels: In situations with the noise ratio of
60%, the baseline approach and JoCoR-CNN are affected by
severe label noise and are no longer capable of handling outlier detection tasks. The performance of the other selected
approaches is also not effective enough. It should be noted that
TFCCL still achieves satisfactory performance across five data
sets, with each dataset’s accuracy above 89% and F1 score above
86%. The results indicate the competitive performance of the
TFCCL in outlier detection with a large number of noisy labels.

C. Comparison Experiments
In this article, two comparison experiments are conducted.
Specifically, the first experiment aims to verify the effectiveness
of the selection of the FCM algorithm. The results are illustrated
in Table VI. According to the results, the FCM algorithm shows
competitive performance across all five datasets under different
noise ratios compared with other hard clustering algorithms,
demonstrating its robustness and adaptability in the presence of
label noise. The second experiment aims to verify the effectiveness of the proposed dynamic updating strategy for the UFCM
algorithm. As shown in Table VII, the developed dynamic updating strategy achieves the best results compared with other
updating strategies.
D. Ablation Study
In this article, a detailed ablation study is carried out to
verify the effectiveness of the main components in TFCCL

FANG et al.: LEARNING WITH NOISY LABELS FOR INDUSTRIAL TIME SERIES OUTLIER DETECTION

911

TABLE VI
COMPARISON OF DIFFERENT CLUSTERING ALGORITHMS WITHIN THE TFCCL FRAMEWORK ON WAAM DATASETS UNDER VARYING NOISE RATIOS

TABLE VII
COMPARISON OF DIFFERENT UFCM UPDATING STRATEGIES WITHIN THE TFCCL FRAMEWORK ON WAAM DATASETS UNDER VARYING NOISE RATIOS

TABLE VIII
RESULTS OF ABLATION STUDY ON WAAM DATASETS WITH DIFFERENT NOISE RATIOS

under various noise ratios. To be specific, the effects of the
pre-training, the FCCL strategy, the UMAP and the dynamic
UFCM updating strategy in TFCCL are verified. The results of
the ablation study are illustrated in Table VIII. Based on the
results, detailed analyses are given as follows.
1) The pretraining helps the Transformer encoder exploit
the internal structure and capture useful feature representations. When trained directly for classification without pre-training, the average performance of the TFCCL
framework declines with increasing noise ratios.
2) The FCCL strategy significantly improves the performance of outlier detection with noisy labels by utilizing
the intrinsic features of data. Employing the UMAP is
able to enhance the performance of the FCCL strategy
when dealing with severe label noise.

3) The dynamic UFCM updating strategy effectively stabilizes the training process and the final performance.
4) Each of the main components plays a critical role in the
TFCCL framework. The best performance of TFCCL can
be achieved only if all components work together.
V. CONCLUSION
In this article, a new TFCCL framework has been developed
for LNL in outlier detection on industrial time series. Specifically, a novel FCCL strategy has been introduced to update
the Transformer encoder, where a UFCM algorithm has been
proposed for identifying positive and negative sample pairs.
A dynamic two-stage training scheme has been designed to
train the outlier detector, incorporating a joint learning strategy
to enhance its robustness against noisy labels. Moreover, a

912

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 2, FEBRUARY 2026

dynamic updating strategy has been employed to update the
UFCM algorithm throughout the training process. To further
improve model reliability, a label-consistency regularization
term has been introduced to minimize the discrepancy between
the outputs of the outlier detector and the UFCM algorithm.
Experimental results have demonstrated the effectiveness of the
developed TFCCL framework. Future research directions can
be summarized as follows.
1) Utilizing optimization techniques for automatic hyperparameter selection [7], [16], [28], [34], [35].
2) Extending the developed TFCCL framework to multiclass
outlier detection tasks [21], [22].
3) Modifying the Transformer encoder architecture to enhance feature extraction performance [3], [27].
4) Refining the FCCL strategy by adjusting the contrastive
loss and improving the clustering algorithm [24], [27].
REFERENCES
[1] M. Boyapati and R. Aygun, “Semanformer: Semantics-aware embedding
dimensionality reduction using transformer-based models,” in Proc. IEEE
18th Int. Conf. Semantic Comput. (ICSC), Laguna Hills, USA, Feb. 2024,
pp. 134–141.
[2] A. Castellani, S. Schmitt, and B. Hammer, “Estimating the electrical power
output of industrial devices with end-to-end time-series classification in
the presence of label noise,” in Proc. Joint Eur. Conf. Mach. Learn. Knowl.
Discov. Databases, Bilbao, Spain, Sep. 2021, pp. 469–484.
[3] H. Chen et al., “Multi-scale class attention network for diabetes retinopathy
grading,” Int. J. Netw. Dyn. Intell., vol. 3, no. 2, 2024, Art. no. 100012.
[4] Y. Dai et al., “Clustering-based contrastive learning for fault diagnosis
with few labeled samples,” IEEE Trans. Instrum. Meas., vol. 73, 2023,
Art. no. 2504913.
[5] J. Fang, Z. Wang, W. Liu, L. Chen, and X. Liu, “A new particle-swarmoptimization-assisted deep transfer learning framework with applications
to outlier detection in additive manufacturing,” Eng. Appl. Artif. Intell.,
vol. 131, 2024, Art. no. 107700.
[6] J. Fang et al., “A new particle swarm optimization algorithm for outlier detection: Industrial data clustering in wire arc additive manufacturing,” IEEE Trans. Automat. Sci. Eng., vol. 21, no. 2, pp. 1244–1257,
Apr. 2024.
[7] W. Fang, B. Shen, A. Pan, L. Zou, and B. Song, “A cooperative stochastic
configuration network based on differential evolutionary sparrow search
algorithm for prediction,” Syst. Sci. Control Eng., vol. 12, no. 1, 2024,
Art. no. 2314481.
[8] M. Gong et al., “Deep fuzzy variable C-means clustering incorporated
with curriculum learning,” IEEE Trans. Fuzzy Syst., vol. 31, no. 12,
pp. 4321–4335, Dec. 2023.
[9] E. Hallaji, R. Razavi-Far, M. Saif, and E. Herrera-Viedma, “Label noise
analysis meets adversarial training: A defense against label poisoning in
federated learning,” Knowl.-Based Syst., vol. 266, 2023, Art. no. 110384.
[10] A. Hamrani, F. Bouarab, A. Agarwal, K. Ju, and H. Akbarzadeh, “Advancements and applications of multiple wire processes in additive manufacturing: A comprehensive systematic review,” Virtual Phys. Prototyping,
vol. 18, no. 1, 2023, Art. no. e2273303.
[11] B. Han et al., “Co-teaching: Robust training of deep neural networks with
extremely noisy labels,” in Proc. 32nd Int. Conf. Neural Inf. Process. Syst.,
Montreal, Canada, Dec. 2018, pp. 8536–8546.
[12] F. He et al., “Research and application of artificial intelligence techniques
for wire arc additive manufacturing: A state-of-the-art review,” Robot.
Comput.- Integr. Manuf., vol. 82, 2023, Art. no. 102525.
[13] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum
contrast for unsupervised visual representation learning,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Seattle, USA, Jun. 2020,
pp. 9726–9735.
[14] Z. Huang, J. Zhang, and H. Shan, “Twin contrastive learning with noisy
labels,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Vancouver, Canada, Jun. 2023, pp. 11661–11670.
[15] J. Li, R. Socher, and S. C. H. Hoi, “DivideMix: Learning with noisy labels
as semi-supervised learning, 2020, arXiv:2002.07394.

[16] Y. Liang, L. Tian, X. Zhang, X. Zhang, and L. Bai, “Multi-dimensional
adaptive learning rate gradient descent optimization algorithm for network
training in magneto-optical defect detection,” Int. J. Netw. Dyn. Intell.,
vol. 3, no. 3, 2024, Art. no. 100016.
[17] W. Liu, Z. Wang, X. Liu, N. Zeng, Y. Liu, and F. E. Alsaadi, “A survey
deep neural network architectures their applications,” Neurocomputing,
vol. 234, pp. 11–26, 2017.
[18] S. Lu, Z. Gao, and Y. Liu, “HFTL-KD: A new heterogeneous federated transfer learning approach for degradation trajectory prediction in
large-scale decentralized systems,” Control Eng. Pract., vol. 153, 2024,
Art. no. 106098.
[19] G. Mattera, J. Polden, A. Caggiano, L. Nele, Z. Pan, and J. Norrish, “Semisupervised learning for real-time anomaly detection in pulsed transfer wire
arc additive manufacturing,” Robot. Comput.- Integr. Manuf., vol. 128,
pp. 84–94, 2024.
[20] A. Oord, Y. Li, and O. Vinyals, “Representation learning with contrastive
predictive coding, 2018, arXiv:1807.03748.
[21] B. Qu, D. Peng, Y. Shen, L. Zou, and B. Shen, “A survey on recent advances
on dynamic state estimation for power systems,” Int. J. Syst. Sci., vol. 55,
no. 16, pp. 3305–3321, 2024.
[22] B. Qu, Z. Wang, B. Shen, and H. Dong, “Decentralized dynamic
state estimation for multi-machine power systems with non-Gaussian
noises: Outlier detection and localization,” Automatica, vol. 153, 2023,
Art. no. 111010.
[23] B. Song, S. Zhao, L. Dang, H. Wang, and L. Xu, “A survey on learning
from data with label noise via deep neural networks,” Syst. Sci. Control
Eng., vol. 13, no. 1, 2025, Art. no. 2488120.
[24] Y. Sun, M. Chen, K. Peng, L. Wu, and C. Liu, “Finite-time adaptive
optimal control of uncertain strict-feedback nonlinear systems based on
fuzzy observer and reinforcement learning,” Int. J. Syst. Sci., vol. 55, no. 8,
pp. 1553–1570, 2024.
[25] C. Tan, J. Xia, L. Wu, and S. Li, “Co-learning: Learning from noisy labels
with self-supervision,” in Proc. 29th ACM Int. Conf. Multimedia, China,
Oct. 2021, pp. 1405–1413.
[26] Y. Tu et al., “Learning with noisy labels via self-supervised adversarial
noisy masking,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Vancouver, Canada, Jun. 2023, pp. 16186–16195.
[27] C. Wang, Z. Wang, H. Dong, and G. Lu, “An optimal unsupervised
domain adaptation approach with applications to pipeline fault diagnosis:
Balancing invariance and variance,” IEEE Trans. Ind. Informat., vol. 20,
no. 8, pp. 10019–10030, 2024.
[28] C. Wang, Z. Wang, Q. Liu, H. Dong, and W. Sheng, “Support-sampleassisted domain generalization via attacks and defenses: Concepts, algorithms and applications to pipeline fault diagnosis,” IEEE Trans. Ind.
Informat., vol. 20, no. 4, pp. 6413–6423, Apr. 2024.
[29] H. Wang et al., “A novel transformer-based few-shot learning method
for intelligent fault diagnosis with noisy labels under varying working
conditions,” Rel. Eng. Syst. Saf., vol. 251, 2024, Art. no. 110400.
[30] R. Wang, X. Wu, T. Xu, C. Hu, and J. Kittler, “U-SPDNet: An SPD
manifold learning-based neural network for visual classification,” Neural
Netw., vol. 161, pp. 382–396, 2023.
[31] Y. Wang, C. Wen, and X. Wu, “Fault detection and isolation of floating wind
turbine pitch system based on Kalman filter and multi-attention 1DCNN,”
Syst. Sci. Control Eng., vol. 12, no. 1, 2024, Art. no. 2362169.
[32] H. Wei, L. Feng, X. Chen, and B. An, “Combating noisy labels by
agreement: A joint training method with co-regularization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Seattle, USA, Jun. 2020,
pp. 13723–13732.
[33] J. Xia et al., “GNN cleaner: Label cleaner for graph structured data,” IEEE
Trans. Knowl. Data Eng., vol. 36, no. 2, pp. 640–651, Feb. 2024.
[34] J. Xue and B. Shen, “A survey on sparrow search algorithms and their
applications,” Int. J. Syst. Sci., vol. 55, no. 4, pp. 814–832, 2024.
[35] Y. Xue et al., “Many-objective simulation optimization for camp location
problems in humanitarian logistics,” Int. J. Netw. Dyn. Intell., vol. 3, no. 3,
2024, Art. no. 100017.
[36] J. Yan, L. Luo, C. Deng, and H. Huang, “Adaptive hierarchical similarity
metric learning with noisy labels,” IEEE Trans. Image Process., vol. 32,
pp. 1245–1256, 2023.
[37] X. Yu, B. Han, J. Yao, G. Niu, I. Tsang, and M. Sugiyama, “How does
disagreement help generalization against label corruption?,” in Proc. 36th
Int. Conf. Mach. Learn., Long Beach, USA, Jun. 2019, pp. 7164–7173.
[38] Z. Yuan, C. Yao, X. Liu, Z. Gao, and W. Zhang, “Multiagent formation
control and dynamic obstacle avoidance based on deep reinforcement
learning,” IEEE Trans. Ind. Informat., vol. 21, no. 6, pp. 4672–4682,
Jun. 2025.

FANG et al.: LEARNING WITH NOISY LABELS FOR INDUSTRIAL TIME SERIES OUTLIER DETECTION

Jingzhong Fang (Member, IEEE) received the
B.Eng. degree in automation from the Shandong University of Science and Technology,
Qingdao, China, in 2020, and the M.Sc. degree in data science and analytics in 2021
from the Brunel University of London, Uxbridge,
U.K., where he is currently working toward the
Ph.D. degree in computer science.
His research interests include intelligent data
analysis and deep learning techniques.
Dr. Fang is a very active Reviewer for many
international journals.

Zidong Wang (Fellow, IEEE) received the
B.Sc. degree in mathematics from Suzhou
University, Suzhou, China, in 1986, and the
M.Sc. degree in applied mathematics and the
Ph.D. degree in electrical engineering from the
Nanjing University of Science and Technology,
Nanjing, China, in 1990 and 1994, respectively.
He is currently a Professor of dynamical systems and computing with the Department of
Computer Science, Brunel University London,
Uxbridge, U.K. From 1990 to 2002, he held
teaching and research appointments in universities in China, Germany,
and the U.K. He has authored or coauthored a number of papers in
international journals. His research interests include dynamical systems,
signal processing, bioinformatics, control theory and applications.
Dr. Wang was the recipient of the Alexander von Humboldt Research
Fellowship of Germany, the JSPS Research Fellowship of Japan, and
the William Mong Visiting Research Fellowship of Hong Kong. He is (or
has served as) the Editor-in-Chief for International Journal of Systems
Science, Neurocomputing, and Systems Science and Control Engineering, and an Associate Editor for 12 international journals including
IEEE TRANSACTIONS ON AUTOMATIC CONTROL, IEEE TRANSACTIONS ON
CONTROL SYSTEMS TECHNOLOGY, IEEE TRANSACTIONS ON NEURAL NETWORKS, IEEE TRANSACTIONS ON SIGNAL PROCESSING, and IEEE TRANSACTIONS ON SYSTEMS, MAN, AND CYBERNETICS-PART C. He is a Member of the Academia Europaea, European Academy of Sciences and
Arts, and program committees for many international conferences, an
Academician of the International Academy for Systems and Cybernetic
Sciences, and a Fellow of the Royal Statistical Society.

Weibo Liu (Member, IEEE) received the
B.Eng. degree in electrical engineering from
the Department of Electrical Engineering and
Electronics, University of Liverpool, Liverpool,
U.K., in 2015, and the Ph.D. degree in artificial
intelligence from the Department of Computer
Science, Brunel University of London, Uxbridge,
U.K., in 2020.
He is currently a Lecturer with the Department of Computer Science, Brunel University
of London. His research interests include intelligent data analysis, evolutionary computation, machine learning, deep
learning, and transfer learning.
Dr. Liu is an Associate Editor for the Journal of Ambient Intelligence
and Humanized Computing and the Journal of Cognitive Computation.
He is a very active Reviewer for many international journals and conferences.

913

Nianyin Zeng (Senior Member, IEEE) was born
in Fujian, China, in 1986. He received the
B.Eng. degree in electrical engineering and automation and the Ph.D. degree in electrical engineering from Fuzhou University, Fuzhou, China,
in 2008 and 2013, respectively.
From October 2012 to March 2013, he was
an RA with the Department of Electrical and
Electronic Engineering, The University of Hong
Kong, Hong Kong. From September 2017 to
August 2018, he was an ISEF Fellow, funded
by Korea Foundation for Advanced Studies, Seoul, South Korea, and
also a Visiting Professor with Korea Advanced Institute of Science and
Technology, Daejeon, South Korea. He is currently a Professor with the
Department of Instrumental and Electrical Engineering, Xiamen University, Xiamen, China. He has authored or coauthored several technical
articles. His current research interests include intelligent data analysis,
computational intelligence, time-series modeling, and applications.
Dr. Zeng is currently an Associate Editor for Neurocomputing, Evolutionary Intelligence, and Frontiers in Medical Technology, and also
an Editorial Board Member for Computers in Biology and Medicine,
BioMedical Engineering OnLine, and Mathematical Problems in Engineering. He is a very active Reviewer of many international journals and
conferences.
Yimeng He received the B.Eng. degree in automation from the School of Automation, Central South University, Changsha, China, in 2020,
and the Ph.D. degree in control science and
engineering with the State Key Laboratory of Industrial Control Technology, College of Control
Science and Engineering, Zhejiang University,
Hangzhou, China, in 2025.
Her research interests include causal discovery, data-driven industrial modeling, machine
learning, and deep learning.

Yu Cao received the B.Eng. degree in computer
science from Shandong Technology and Business University, Yantai, China, in 2019, and the
M.Sc. degree in data science and analytics in
2020 from Brunel University London, Uxbridge,
U.K., where he is currently working toward the
Ph.D. degree in computer science.
His research interests include video anomaly
detection and deep learning techniques.

Linwei Chen received the B.Eng. degree in
electrical and electronic engineering from the
University of Warwick, Coventry, U.K., in 2022.
She is currently working toward the Ph.D.
degree in computer science with Brunel University London, Uxbridge, U.K.
Her research interests include transfer learning and optimization.

Xiaohui Liu received the B.Eng. degree in computing from Hohai University, Nanjing, China, in
1982, and the Ph.D. degree in computer science
from Heriot-Watt University, Edinburg, U.K., in
1988.
He is currently a Professor of Computing
with Brunel University London, Uxbridge, U.K.,
where he conducts research in artificial intelligence, data science, and optimization, with applications in diverse areas including biomedicine
and engineering.
PAPER_TEXT
