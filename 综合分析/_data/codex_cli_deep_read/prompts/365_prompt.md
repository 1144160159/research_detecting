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
# [365] Anomaly Detection Framework With Contrastive Learning and Multiview Augmentation for Time-Series Domain Generalization
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
编号：365
题名：Anomaly Detection Framework With Contrastive Learning and Multiview Augmentation for Time-Series Domain Generalization
年份：2024
DOI：10.1109/tim.2024.3507042
来源：IEEE Transactions on Instrumentation and Measurement
PDF：paper/10.1109_TIM.2024.3507042.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\365.txt
- 原始字符数：47388
- 本次发送字符数：47388
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

2502109

Anomaly Detection Framework With Contrastive
Learning and Multiview Augmentation for
Time-Series Domain Generalization
Yeseul Lee , Seunghwan Song , Kwan-Yong Park , Byoung-Mo Koo , and Jun-Geol Baek

Abstract— Time-series data are generated and collected
in manufacturing processes. Time-series data have different
distribution characteristics, with the underlying assumption
being that all data originate from the same distribution. Timeseries anomaly detection methods are trained on stationary data
derived from the source domain. However, the performance of the
trained model diminishes when confronted with a nonstationary
distribution in the target domain. Consequently, there is a need
for a model that can adapt to any distribution using only the
source domain. In this study, we propose an anomaly detection
framework with contrastive learning and multiview augmentation
for time-series domain generalization. The proposed method
uses multiview augmentation to learn three representations for
time-series domain generalization. Moreover, the augmented
samples use a temporal convolutional network (TCN) to extract
these representations. Subsequently, the extracted representations
are trained with a contrastive learning method inspired by
simple triplet representation learning (SimTriplet). Therefore,
the proposed method can attain the diversity and generalization
performance of the source domain. The performance superiority
of our proposed method is experimentally validated across
various domain shift scenarios. Additionally, the effectiveness of
the modules used in the proposed method is confirmed through
qualitative analysis.
Index Terms— Contrastive learning, multiview augmentation,
temporal convolutional network (TCN), time-series domain
generalization.

I. I NTRODUCTION

I

N THE digital twin manufacturing process, the data are
collected from several sensors. A large amount of normal
data and a small amount of abnormal data are collected during
the manufacturing process. The few abnormal data are related
to the yield of the manufacturing process. Semisupervised
anomaly detection aims to train the normality of a timeseries representation under the assumption that most of the
training data are normal [1]. However, these methods rely on

Received 9 August 2024; accepted 19 September 2024. Date of publication
27 November 2024; date of current version 9 December 2024. This work was
supported by the National Research Foundation of Korea (NRF) grant funded
by the Korean government (MSIT) (NRF- 2022R1A2C2004457). Also, this
work was supported by Samsung Electronics Co., Ltd (IO201210-07929-01)
and BK21 FOUR funded by the Ministry of Education of Korea and National
Research Foundation of Korea. The Associate Editor coordinating the review
process was Dr. Zhibin Zhao. (Yeseul Lee and Seunghwan Song are co-first
authors.) (Corresponding author: Jun-Geol Baek.)
The authors are with the Department of Industrial and Management
Engineering, Korea University, Seoul 02841, Republic of Korea (e-mail:
yetsyl0705@korea.ac.kr;
ss-hwan@korea.ac.kr;
gamja331@korea.ac.kr;
kbm970709@korea.ac.kr; jungeol@korea.ac.kr).
Digital Object Identifier 10.1109/TIM.2024.3507042

the distribution of the training data [2]. This is because most
models assume that all the data are collected from the same
distribution during training and testing. However, this strong
assumption is not appropriate in the real world. In particular,
distributions often change during manufacturing processes due
to labor, machine changes, or maintenance. In this study, this
situation is referred to as a domain shift. Since a domain
shift causes performance degradation in existing models,
appropriate measures are required [3].
Domain adaptation has been proposed to address domain
shifts by transferring knowledge or information obtained from
training data (i.e., the source domain) to a model based on test
data (i.e., the target domain) [4], [5]. This process primarily
involves reducing or adjusting the differences between the
source and target domains, enabling the model to be trained
in the source domain and adaptable to the target domain [6].
Despite its success in various tasks, domain adaptation still
faces significant challenges. First, training in the target
domain becomes unstable if the distribution is nonstationary.
Domain adaptation aims to generalize from in-distribution
(ID) data with stationarity. However, model performance
degrades when the target domain distribution shifts to out-ofdistribution (OOD) and becomes nonstationary, necessitating
additional learning. Second, effective domain adaptation
requires collecting samples from all possible distributions,
which is inefficient and impractical [7]. Consequently, there
is a need for models that can adapt to any distribution using
only the source domains collected from the ID.
Domain generalization aims to maintain performance on
unknown domains by training multiple independent source
domains [8]. Domain adaptation focuses on minimizing the
difference between the source and target domains; in contrast,
domain generalization has been proposed as a technique
to address the inherent limitations of domain adaptation.
Domain generalization has been successful in a variety
of vision tasks [9], [10] and natural language processing
(NLP) tasks [11], [12], [13]. Representation learning is
often used in domain generalization to extract a generalized
representation for the source domain. Contrastive learning
among representation learning has demonstrated effective
performance for feature extraction [14], [15], [16]. Contrastive
learning trains the same classes (i.e., positive pairs) to
be closer in distance, while different classes (i.e., negative
pairs) are further apart. Contrastive learning-based domain
generalization studies typically aim to train domain-invariant

1557-9662 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

2502109

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

and class-variant representations. Contrastive learning is
an effective method for domain generalization, which is
the problem of interest in this study. It affords several
advantages over traditional methods, such as less dependence
on labeled data, improved robustness to domain shifts, and
utilization of effective data augmentation techniques for
time-series data [15], [16]. Dou et al. [17] proposed modelagnostic learning of semantic features (MASF). This method
can be used to extract domain-invariant and class-variant
representations. In contrast, Kim et al. [16] overcame the
instability of training due to negative pairs with self-supervised
contrastive regularization (SelfReg), which uses only positive
pair samples.
However, adapting contrastive learning-based domain generalization to time-series data presents several challenges.
First, previous studies have focused on supervised learning
or assumed fully annotated datasets [18]. In manufacturing
processes, obtaining sufficient labeled data is time-consuming,
making these approaches impractical. Second, many of these
methods are designed for vision and NLP tasks, which
utilize data augmentation techniques to diversify the source
domain [19]. Contrastive learning-based domain generalization
uses data augmentation to diversify the source domain used for
training. Data augmentation is a technique used to increase
the size of a practical dataset by diversifying the source
domain [20]. Adding random noise, changing colors, and
shapes have been used to augment the source domain [21],
[22], [23]. However, because data augmentation is specialized
for vision and NLP tasks, augmentation for time-series data
is limited. Therefore, appropriate augmentation for time-series
data is required.
Meanwhile, defining negative pairs in time-series data is
difficult owing to the dependencies between time variables
and inter-variables. Therefore, it is necessary to design a
model that uses only positive pairs [24]. Liu et al. [25]
proposed a simple triplet representation learning (SimTriplet)
that uses only positive pairs. SimTriplet is a modified version
of the exploring simple Siamese representation learning
(SimSiam) [26] network structure. Compared to SimSiam,
it has the advantage of learning multiple representations by
adding features. SimTriplet uses the spatial property that
geographically adjacent images are more likely to belong
to the same class, achieved through two-view consistency
learning, which minimizes the distance between two positive
pairs. However, there are limitations when applied to
time-series data, as they lack distinct classes and spatial
features.
In this study, we proposed an anomaly detection framework
with contrastive learning and multiview augmentation for
time-series domain generalization. The proposed method
aims to detect time-series anomalies in a domain shift
situation by extracting a generalized representation. First, the
proposed method uses multiview augmentation for time-series
data. Multiview augmentation learns three representations
for time-series domain generalization: 1) domain-invariant
representation; 2) robust representation; and 3) task-adaptive
representation. These representations have the advantage
of providing source domain diversity and generalization

performance. Then, the augmented sample is processed using
a temporal convolutional network (TCN). A TCN is a
convolutional neural network (CNN)-based model that can be
used for time-series modeling and has the advantage of fast
computation speed [27]. Finally, the extracted representation
is trained using a contrastive learning method inspired by
SimTriplet [25].
The key contributions of this study are as follows:
1) multiview augmentation improves domain generalization
by generating multiple representations of time-series
data;
2) the TCN and SimTriplet structures make training
suitable for time-series data; and
3) domain generalization experiments on various timeseries datasets demonstrate the robustness of the
proposed method.
The remainder of this study is organized as follows.
Section II provides a detailed description of the proposed
method and its structure. Section III presents an evaluation of
three different time-series datasets using the proposed method
to verify its performance. Finally, Section IV presents the
conclusions and future works of this study.
II. P ROPOSED M ETHOD
In this section, we propose an anomaly detection framework
with contrastive learning and multiview augmentation for timeseries domain generalization. The proposed method draws
inspiration from SimTriplet [25] but undergoes a model
redesign to better suit the requirements of time-series anomaly
detection. Initially, multiview augmentation is employed to
enhance the diversity of time-series data in the source
domain. Subsequently, the TCN encoder is utilized to extract
representations for each augmented time-series dataset. The
overall structure of the proposed method is depicted in Fig. 1.
A. Multiview Augmentation
Effective time-series domain generalization necessitates
achieving three primary objectives [14]. First, the consideration of domain-invariant representations between the source
domains allows for the learning of generalized representations
across domain variations without being constrained to a
specific domain. Second, the model must exhibit robustness
against external environments, ensuring stable training under
diverse conditions by accounting for noise. Lastly, it must
possess task-adaptive capabilities to effectively perform tasks
in the target domain, making the model applicable to realworld scenarios. In this study, we utilized three augmentations
to perform domain generalization in time-series anomaly
detection. First, we extracted general features from multiple
tasks in the source domain; this helps achieve performance
in the target domain. It also enables the extraction of
representations that are robust to real-world, noisy time-series
anomalies.
To attain these objectives, multiview augmentation is
employed, incorporating adversarial attacks and jitter-based
data augmentation. Adversarial attacks for data augmentation
are implemented using the fast gradient sign method (FGSM)

LEE et al.: ANOMALY DETECTION FRAMEWORK WITH CONTRASTIVE LEARNING AND MULTIVIEW AUGMENTATION

Fig. 1.

2502109

Contrastive learning with multiview augmentation for time-series domain generalization framework.

[28] in this study. The FGSM-based data augmentation is
expressed as follows:
xadversarial = x+ ∈adversarial ·sign(∇x L(θ, x, y))

(1)

where x and y denote the train data and labels, respectively, θ
is the weight of the network, and L(·) is the loss function. The
process for creating an adversarial sample using the FGSM is
as follows:
Step 1: Calculate the gradient ∇x L(θ, x, y) for the loss
function on the training data.
Step 2: The gradient ∇x L(θ, x, y) is updated in a direction
opposite to the label y.
Step 3: The noise sign(∇x L(θ, x, y)) that can cause
misclassification during the update process is defined.
Step 4: The noise sign(∇x L(θ, x, y)) is adjusted by a
hyperparameter ∈adversarial , which is added to the original
data x.
FGSM-based data augmentation was used for source
domain-invariant and task-adaptive representations. This is
achieved by updating the noise values obtained from each
model in the existing FGSM equation. By contrast, jitter-based
augmentation is used for external robustness.
1) Domain-Invariant Representation: If the model is trained
on common and general patterns across the source domains,
it can achieve performance in the target domain. This implies
that training the model to distinguish between source domains
prevents overreliance on a particular domain. In this study,
we utilized FGSM-based data augmentation. FGSM trains
the source domain-invariant representation by adding noise to
the original data [28]. This process increases the uncertainty
of the model because it generates an adversarial sample
that confuses the model, leading to misclassification. In this
study, we employed long short-term memory (LSTM) [29]
as a classification model to consider the temporal pattern,
and cross-entropy served as the loss function. Consequently,
the creation of an adversarial sample for a domain-invariant
representation is shown in the following equation:

x̃ DI = x+ ∈DI ·sign ∇x L θ S , D S , y S
(2)
where x is the original data and D S and y S are the data
and labels in the source domain, respectively. In addition, θ S
is the source domain network weights and ∇x L(θ S , D S , y S )

denotes the gradient of the loss function. The noise
sign(∇x L(θ S , D S , y S )) is adjusted by the hyperparameter ∈DI .
Consequently, x̃ DI trains the source domain-invariant representation by adding noise, which can lead to misclassification.
2) Robust Representation: In the real world, a model that
can reliably perform in various environments is required.
In particular, considerable noise is generated during the manufacturing process, making it crucial to ensure the robustness
of generalized performance under diverse conditions and
environments. In this study, we employed jitter-based data
augmentation, as it has been demonstrated to effectively handle
real-world noise in several studies [30]. The creation of a
sample for a robust representation is shown in the following
equation:
x̃ R = x+ ∈ R ·σ

(3)

where x is the original data and σ is the standard deviation
for each variable. The standard deviation σ is adjusted by
the hyperparameter ∈ R . Consequently, x̃ R trains the robust
representation to deal with real-world noise and variation.
3) Task-Adaptive Representation: Time-series domain generalization must be task-adaptive to the target domain,
signifying that the proposed model can be applied in
new environments. For this purpose, we utilized inverse
FGSM (InvFGSM) [28]. InvFGSM enhances task-adaptive
performance by subtracting the noise of the model from the
original data. In this process, InvFGSM aids in achieving better
performance by adjusting the inputs with minimal loss [31].
Therefore, InvFGSM-based data augmentation can enhance
anomaly detection performance in the target domain. In this
study, we employed a temporal convolutional autoencoder
(TCN-AE) [32] as an anomaly detection model, with the mean
squared error (mse) serving as the loss function. The creation
of an adversarial sample for a task-adaptive representation is
as shown in the following equation:

x̃ TA = x− ∈TA ·sign ∇x L θiS , DiS , i = 1, . . . , M (4)
where x is the original data, and DiS is the ith source domain.
The total number of source domains is M. In addition, θiS
is the ith source domain network weights and ∇x L(θiS , DiS )
denotes the gradient of the ith loss function. The ith noise
sign(∇x L(θiS , DiS )) is adjusted by the hyperparameter ∈TA .

2502109

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Consequently, x̃ TA trained the task-adaptive representation to
allow the model to achieve more robust results.
B. TCN Encoder for Feature Extraction and Predictor
In this study, we employed a TCN encoder for feature
extraction from the augmented samples. TCN is a CNNbased model that can be used in sequence modeling and
uses dilated convolution [27]. Dilated convolution has the
advantage of increasing the receptive field to obtain long
time step information without the need for a convolutional
layer. TCN is suitable for time-series modeling and offers the
advantage of faster computation compared to a recurrent neural
network (RNN)-based models [27]. The proposed method
utilized three parallel TCN encoders with shared weights,
extracting features from the multiview augmented samples.
In this study, we utilized ten dilated convolution layers in
the TCN encoder, enabling the extraction of generalized
representations from long-term timesteps. As a result, TCN
encoders could process each sequential input and capture the
relationship between the augmented samples.
The predictor and stop-gradient are devices to prevent mode
collapse that occurs when SimTriplet performs contrastive
learning using only positive pairs. The predictor utilizes a
multilayer perceptron structure with two linear layers, which
is the same as the SimTriplet structure.

as pDI , p R , and pTA . The proposed method involves two
loss functions for time-series domain generalization: 1)
minimizing the dissimilarity between the source domaininvariant representation and the robust representation to ensure
that the learned features are stable and generalizable across
different domains and 2) minimizing the dissimilarity between
the task-adaptive representation for the target domain and the
robust representation to enhance the model’s ability to adapt
to new tasks and improve anomaly detection performance in
the target domain. Each loss function is expressed as follows:

1
(6)
L RDI = NCS(z DI , p R ) + NCS(z R , pDI )
2

1
(7)
L RTA = NCS(z TA , p R ) + NCS(z R , pTA ) .
2
In (6), L RDI maximizes the similarity between the source
domain-invariant representation and the robust representation,
promoting a robust domain-invariant to facilitate learning
and avoid misclassification among between different source
domains. Conversely, L RTA in (7) maximizes the similarity
between the task-adaptive representation for the target domain
and the robust representation, fostering robust task adaptation
to enhance the extraction of representations for improved
anomaly detection performance in the target domain. The final
loss function of the proposed method is shown in the following
equation:
L Total = L RDI + L RTA .

C. Loss Function
In domain generalization, training and testing are performed
using the source and target domains, respectively. In this study,
we trained an encoder that can extract the representation with
the loss function negative cosine similarity (NCS) loss using
the source domain data in the training process. In the test
process, we defined the Euclidean distance between the target
domain representation and the source domain representation
obtained by the encoder as the anomaly score and utilized it
for anomaly detection.
Our model for contrastive-learning-based time-series
domain generalization relies on positive pairs exclusively,
drawing inspiration from the SimTriplet [25]. The suitability
of two-view consistency learning in SimTriplet for learning
the relationship between augmented samples motivated this
choice. Consequently, each output of the TCN encoder serves
as an asymmetrical predictor, with a stop gradient applied.
The NCS [33] is employed to calculate dissimilarity between
the outputs, reducing differences between the augmented
samples through opposite characteristics. The NCS is shown
in the following equation:
q
p
·
.
(5)
NCS( p, q) = −
∥ p∥2 ∥q∥2
In (5), p and q denote two vectors. Further, ∥ p∥2 and ∥q∥2
denote the Euclidean distances between the two vectors. NCS
makes the two vectors more similar and ranges from −1 to 1.
In this study, x̃ DI , x̃ R , and x̃ TA were created using
multiview augmentation. These representations are processed
using the TCN encoder to obtain z DI , z R , and z TA . These
features were passed on to the predictor and expressed

(8)

The final loss function of the proposed method helps TCN
encoders with shared weights in embedding the representations
of different augmentations. Meanwhile, the stop-gradient is
accomplished by stopping or not propagating a particular
gradient during backpropagation [26]. Therefore, the proposed
method can be trained to avoid mode collapse through the final
loss function and to stop the gradient.
Consequently, the output of the proposed method is the
latent vector calculated by the TCN. Training of the proposed
method yields a feature extractor that is task-adaptive and
capable of extracting domain-invariant representations.
III. E XPERIMENT
A. Datasets
The aim of the proposed method is to train a representation
for time-series data in the source domain, enabling effective
time-series anomaly detection, even in a domain shift situation
in the target domain. Therefore, two datasets were selected to
evaluate the proposed method.
1) SKAB Dataset: The Skoltech Anomaly Benchmark
(SKAB) dataset was collected during the simulation of a
water circulation system [34]. It comprises Valve1 at the outlet
and Valve2 at the inlet of the water circulation pump. Each
subset of Valve1 and Valve2 signifies the time order in which
they were collected. There were 14 subsets of Valve1 and
four subsets of Valve2. The data consist of eight variables
(accelerometer1, accelerometer2, temperature, thermocouple,
current, pressure, voltage, and rate) along with a time step.
The SKAB dataset contains the following anomaly types:
abrupt change, contextual anomalies, collective anomalies, and

LEE et al.: ANOMALY DETECTION FRAMEWORK WITH CONTRASTIVE LEARNING AND MULTIVIEW AUGMENTATION

TABLE I
TASK I NFORMATION FOR T IME , M ACHINE , AND
O PERATION D OMAIN S HIFT S CENARIO

gradual change. Additionally, both normal and abnormal data
are labeled, with a 35% anomaly ratio.
2) CNC Milling Machine Dataset: The computer numerical
control (CNC) milling machine dataset was collected during
the processing of a piece of aluminum [34]. It includes
three machine subsets and 15 operation subsets, reflecting
the variability in the physical flow of production during the
manufacturing process. The data consist of three variables (xaxis, y-axis, and z-axis vibrations) along with a time step.
The CNC milling machine dataset contains the following
anomaly types: tool wear, spindle malfunction, unexpected
vibrations, temperature anomalies, and misalignment. Normal
and abnormal data are labeled, with a 4.12% anomaly ratio.
B. Problem Definition
The proposed method aims for good performance in the
target domain by training in the source domain. Therefore,
three domain shift scenarios were considered using the SKAB
and CNC milling machine datasets. For the time domain shift
scenario, the SKAB dataset is considered because it contains
valves collected at different times in the same environment.
For the machine and operation domain shift scenarios, the
CNC milling machine dataset is considered as it contains
information about different machines or operations collected
simultaneously. The task information for each domain shift
scenario is presented in Table I.
The time domain shift assesses the performance of the
proposed method as the temporal distribution undergoes
changes. Valve1 was considered because it contained sufficient
subsets of the SKAB dataset. There are 14 subsets of Valve1
ranging from Valve1_00 to Valve1_13, where “t” in each
Valve1_t signifies the temporal order. Tasks for evaluating the
time domain shift scenario were categorized from T1 to T7,
with the number of source domains increasing by one for
each task to align with the temporal order. The target domain
consists of a subset immediately after each task.
The machine domain shift assesses the performance
of the proposed method as the distribution of machines

2502109

changes. Three different machines Machine01, Machine02,
and Machine03 of a CNC milling machine were considered for
this purpose. Three tasks (M1, M2, and M3) were established
to verify the machine domain shift, with each task’s source
domain comprising two machines and the target domain
consisting of the remaining machine not used in the source
domain.
The operation domain shift evaluates the proposed method’s
performance when the operating conditions of the machine
undergo changes. Fifteen different operations (Operation01 to
Operation15) from the CNC milling machine dataset were
considered for this purpose. Four tasks (O1, O2, O3, and O4)
were employed to verify operational domain shifts. In each
task, the source domain included the remaining 14 operations,
excluding one specific operation. In this study, Operation02,
Operation04, Operation07, and Operation10 were chosen as
specific operations because only four out of the 15 contain
both normal and abnormal data.
C. Experiment Details
Time-series domain generalization requires testing of
distributions that are not used in training. Therefore, M source
S
domains D S = [D1S , . . . , D M
] with only normal data used in
the training process. The testing process used the target domain
D T that was not part of the training, containing both normal
and abnormal data. This setup allowed the evaluation of the
performance of the target domain for a model trained in the
source domain.
The proposed method aims to achieve generalized performance in time-series anomaly detection. Consequently, various
time-series anomaly detection models were employed for comparison: deep support vector data description (Deep SVDD)
[36], multiscale convolutional recurrent encoder–decoder
(MSCRED) [37], unsupervised anomaly detection (USAD)
[38], deep transformer networks for anomaly detection
(TranAD) [39], and SimSiam [26]. All algorithms were trained
for 50 epochs with a window size of 60 and a batch size of 64,
and each experiment was repeated five times. The experiments
were implemented using the PyTorch software package in
the Python3 language. Training procedures utilized an Intel1
Core2 i9-12900K CPU at 3.60 GHz, 64 GB of RAM, and an
NVIDIA GeForce RTX 3090Ti graphics card with 32 GB of
G6X memory.
D. Evaluation Metrics
Two metrics were employed to evaluate the performance
of time-series domain generalization. First, the area under
the receiver operating characteristic (AUROC) curve assessed
the anomaly detection performance. A higher AUROC
value indicates effective discrimination between normal and
abnormal data. Second, to evaluate generalization performance
in domain shift situations, a new metric, the GP-Score, was
defined as follows:
AUROC of source to target domain
.
(9)
GP-Score =
AUROC of source to source domain
1 Registered trademark.
2 Trademarked.

2502109

Fig. 2.

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

GP-Score in time domain shift.

The GP-Score is calculated as the ratio of the AUROC
for different types of test data when the model is trained on
normal data from the source domain. In (9), the denominator
represents the AUROC when the model is trained on normal
data from the source domain and tested on normal and
abnormal data from the source domain. The numerator
represents the AUROC when the model is trained on normal
data from the source domain and tested on normal and
abnormal data from the target domain. Essentially, the GPScore quantifies the performance change as the distribution
shifts. Any GP-Score greater than 1 is scaled to 1, enabling
the observation of quantitative performance changes in domain
shift situations.
E. Experiment Results
1) Time Domain Shift Result: To assess the performance
of the proposed method under changes in the temporal
distribution, seven tasks (T1–T7) were considered using the
SKAB dataset. The source domains were utilized for training
in chronological order, while the target domain is a subset
immediately after each task. Table II and Fig. 2 present the
AUROC and GP-Score results for the time domain shifts,
respectively.
The experimental findings indicate that the proposed method
outperforms the comparison models in four out of seven tasks.
For the remaining three tasks, the proposed method exhibits
less performance degradation than the comparison models.
In contrast, anomaly detection models based on adversarial
learning, such as USAD and TranAD, exhibit limitations in
their ability to learn representations from source domains.
TranAD performs poorly due to overfitting to the source
domains caused by the transformer structure used in the model.
Additionally, deep SVDD performs inadequately as it involves
converting multiple source domains into a single center. The
GP-Score suggests that the proposed method maintains stable
performance under time domain shifts, indicating its ability
to sustain generalized performance even when the temporal
distribution changes.
2) Machine Domain Shift Result: To evaluate the performance of the proposed method under changes in the machine
distribution, three tasks (M1, M2, and M3) were considered
using the CNC milling machine dataset. Each task’s source
domain comprised two machines, and the target domain

Fig. 3.

GP-Score in machine domain shift.

Fig. 4.

GP-Score in operation domain shift.

included the remaining unused machines in the source domain.
Table III and Fig. 3 present the AUROC and GP-Score results,
respectively, for the machine domain shifts.
Experimental results reveal that the proposed method
performs the best in two out of the three tasks. The
AUROC performance for task M2 was suboptimal; however,
the GP-Score results remained stable compared to those
of other models. The comparison models, except for Deep
SVDD, demonstrated effective performance under machine
domain shifts. This is attributed to the CNC milling machine
dataset not inherently being prone to machine domain shifts.
Consequently, the results indicate that the proposed method
extracts general representations from multiple source domains
and adapts to variations in the machine distribution, suggesting
that stable performance can be achieved with a small number
of source domains.
3) Operation Domain Shift Result: To assess the performance of the proposed method under changes in machine
operating conditions, four tasks (O1, O2, O3, and O4) were
considered using the CNC milling machine dataset. The
source domain for each task included all 14 operations,
except for one specific operation, while the target domain
comprised the remaining unused operations in the source
domain. Table IV and Fig. 4 present the AUROC and GPScore results, respectively, for the operation domain shifts.
The experimental results showed that the proposed method
performed the best in all tasks. Because the experiment on
the operational domain shifts trains 14 source domains, most
of the comparison models also performed well. However,

LEE et al.: ANOMALY DETECTION FRAMEWORK WITH CONTRASTIVE LEARNING AND MULTIVIEW AUGMENTATION

2502109

TABLE II
AUROC OF T IME -S ERIES D OMAIN G ENERALIZATION IN T IME D OMAIN S HIFT (SKAB DATASET )

TABLE III
AUROC OF T IME -S ERIES D OMAIN G ENERALIZATION IN M ACHINE D OMAIN S HIFT (CNC M ILLING M ACHINE DATASET )

TABLE IV
AUROC OF T IME -S ERIES D OMAIN G ENERALIZATION IN O PERATION D OMAIN S HIFT (CNC M ILLING M ACHINE DATASET )

the performance of most models tended to drop sharply
at O4. This is because Operation10, which is used as the
target domain in O4, has a greater variation in the operation
distribution than the source domains. In contrast, the GP-Score
shows that the proposed method performs consistently and
well in all tasks. This demonstrates that the proposed method
maintained its generalized performance when the machine
operation distribution changed.
F. Ablation Study
We performed an ablation study involving a qualitative analysis of the proposed method to validate the effectiveness and
necessity of the employed modules. Multiview augmentation
achieves source domain-invariant, robust, and task-adaptive
representations in the target domain. Fig. 5 illustrates
the individual impact of multiview augmentation and the
sensitivity of each augmented sample to hyperparameters ∈DI ,
∈ R , and ∈TA .
Fig. 5(a) shows the AUROC performance as a result of the
individual impacts of multiview augmentations x̃ DI and x̃ TA .
The bar graph shows the mean, and the line graph shows the

standard deviation. The experiments were performed on the
SKAB dataset in a time domain shift scenario. Elucidating
the individual effects of multiview augmentation is difficult
because the framework used in this study consists of shared
weights of the three TCN encoders. Therefore, we replaced
the augmentation with jitter-based augmentation to verify its
effectiveness. Experiments showed that the best performance is
achieved when the multiview augmentation technique is fully
utilized. In addition, x̃ DI had the greatest impact on multiview
augmentation.
Fig. 5(b) shows the sensitivity of each augmented sample
to the hyperparameters ∈DI , ∈ R , and ∈TA of the multiview
augmentation. The box plot represents the AUROC of
the seven tasks in the SKAB dataset. The experimental
results show that x̃ DI and x̃ TA are hardly affected by
the hyperparameters, while x̃ R is considerably affected.
Consequently, multiview augmentation is relatively robust
to hyperparameters. This can lead to stable performance
in time-series domain generalization. The proposed method
used fixed hyperparameters regardless of the dataset: ∈DI =
0.001, ∈ R = 0.0005, and ∈TA = 0.005. The hyperparameter
values were determined through extensive experimentation

2502109

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

IV. C ONCLUSION

Fig. 5.
Ablation study of multiview augmentation. (a) Comparison of
the impacts of multiview augmentation. (b) Hyperparameter sensitivity in
multiview augmentation.

This study devised a novel anomaly detection framework
that utilizes multiview augmentation to enhance time-series
domain generalization. This structure leverages multiview
augmentation to learn three features for time-series domain
generalization. Subsequently, the time-series features are
extracted using a TCN encoder. Finally, the extracted
representations are trained using a contrastive learning method
inspired by SimTriplet. Experiments were conducted in three
domain shift scenarios to evaluate the performance of the
proposed method; the results demonstrated its effectiveness
in learning generalized features from various source domains
to perform reliably within the target domain. Moreover, the
proposed method exhibited high generalization performance
compared to existing methods. Finally, qualitative analysis was
performed to verify the effectiveness of the modules used in
the proposed method.
Despite the promising results, a few limitations must be
acknowledged. First, the proposed method heavily relies on the
quality and diversity of the source domain data. If the source
domains are not adequately representative of potential target
domains, the model’s generalization performance may suffer.
Second, while the method shows robustness in simulated
domain shifts, its performance in real-world applications,
where domain shifts can be more unpredictable and complex,
requires further validation. Future studies should focus on
addressing these limitations by exploring more efficient
algorithms, incorporating additional real-world datasets for
validation, and enhancing the adaptability of the model to
unforeseen domain shifts.
R EFERENCES

Fig. 6.

Ablation study for feature extraction.

to balance model performance in different domains and
tasks.
In this study, we utilized a TCN encoder for feature
extraction for the augmented samples. Comparison with other
encoder methods demonstrated the effectiveness of the TCN
encoder for time-series modeling. Three time-series encoders
were used for comparison: 1-D CNN, LSTM, and linear. Fig. 6
presents the ranking results for the AUROC performance upon
changing the encoder in the proposed method.
For the domain shift scenario, we performed investigations
by changing the encoder used for feature extraction.
We performed five experiments with each of the encoders
and ranked the results. As shown in Fig. 6, the best results
corresponded to the use of the TCN encoder on all datasets.
This shows that the TCN encoder can effectively extract
features from time-series data.

[1] F. Zhou, G. Wang, K. Zhang, S. Liu, and T. Zhong, “Semi-supervised
anomaly detection via neural process,” IEEE Trans. Knowl. Data Eng.,
vol. 35, no. 10, pp. 1–13, Apr. 2023, doi: 10.1109/TKDE.2023.3266755.
[2] F. Gao, J. Li, R. Cheng, Y. Zhou, and Y. Ye, “ConNet:
Deep semi-supervised anomaly detection based on sparse positive samples,” IEEE Access, vol. 9, pp. 67249–67258, 2021, doi:
10.1109/ACCESS.2021.3077014.
[3] Z. Sun et al., “Dynamic domain generalization,” 2022,
arXiv:2205.13913.
[4] C. Chen, F. Shen, J. Xu, and R. Yan, “Domain adaptation-based
transfer learning for gear fault diagnosis under varying working
conditions,” IEEE Trans. Instrum. Meas., vol. 70, pp. 1–10, 2021, doi:
10.1109/TIM.2020.3011584.
[5] G. Michau and O. Fink, “Unsupervised transfer learning for anomaly
detection: Application to complementary operating condition transfer,”
Knowl.-Based Syst., vol. 216, Mar. 2021, Art. no. 106816, doi:
10.1016/J.KNOSYS.2021.106816.
[6] P. Singhal, R. Walambe, S. Ramanna, and K. Kotecha, “Domain adaptation: Challenges, methods, datasets, and applications,” IEEE Access,
vol. 11, pp. 6973–7020, 2023, doi: 10.1109/ACCESS.2023.3237025.
[7] Y. Liao, R. Huang, J. Li, Z. Chen, and W. Li, “Deep semisupervised
domain generalization network for rotary machinery fault diagnosis
under variable speed,” IEEE Trans. Instrum. Meas., vol. 69, no. 10,
pp. 8064–8075, Oct. 2020.
[8] J. Wang et al., “Generalizing to unseen domains: A survey on
domain generalization,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 8,
pp. 8052–8072, Aug. 2022.
[9] C. Liu, “Learning causal semantic representation for out-of-distribution
prediction,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2021,
pp. 6155–6170.
[10] R. Gong, W. Li, Y. Chen, and L. Van Gool, “DLOW: Domain flow for
adaptation and generalization,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2019, pp. 2472–2481.

LEE et al.: ANOMALY DETECTION FRAMEWORK WITH CONTRASTIVE LEARNING AND MULTIVIEW AUGMENTATION

[11] G. Perez, “Improving domain generalization using style regularization,”
in Proc. LatinX AI Comput. Vis. Pattern Recognit. Conf., Jun. 2021,
pp. 1006–1016.
[12] Z. Wang, Q. Wang, C. Lv, X. Cao, and G. Fu, “Unseen target stance
detection with adversarial domain generalization,” in Proc. Int. Joint
Conf. Neural Netw. (IJCNN), Jul. 2020, pp. 1–8.
[13] B. Wang, M. Lapata, and I. Titov, “Meta-learning for domain
generalization in semantic parsing,” in Proc. Conf. North Amer. Chapter
Assoc. Comput. Linguistics, Hum. Lang. Technol., 2021, pp. 366–379.
[14] S. Motiian, M. Piccirilli, D. A. Adjeroh, and G. Doretto, “Unified deep
supervised domain adaptation and generalization,” in Proc. IEEE Int.
Conf. Comput. Vis. (ICCV), Oct. 2017, pp. 5716–5726.
[15] H. Yun, R. Wang, R. Rayhana, S. Pant, M. Genest, and Z. Liu,
“WaveCLR: Contrastive learning of guided wave representations for
composite damage identification,” IEEE Trans. Instrum. Meas., vol. 73,
pp. 1–14, 2024, doi: 10.1109/TIM.2024.3386207.
[16] D. Kim, Y. Yoo, S. Park, J. Kim, and J. Lee, “SelfReg: Selfsupervised contrastive regularization for domain generalization,” in Proc.
IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021, pp. 9599–9608.
[17] Q. Dou, K. Kamnitsas, and B. Glocker, “Domain generalization via
model-agnostic learning of semantic features,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2019, pp. 6447–6458.
[18] Q. Zhang et al., “Conditional adversarial domain generalization with a
single discriminator for bearing fault diagnosis,” IEEE Trans. Instrum.
Meas., vol. 70, pp. 1–15, 2021, doi: 10.1109/TIM.2021.3071350.
[19] X. Zhang, L. Zhou, R. Xu, P. Cui, Z. Shen, and H. Liu, “Towards
unsupervised domain generalization,” 2021, arXiv:2107.06219.
[20] L. Zhang et al., “When unseen domain generalization is unnecessary?
Rethinking data augmentation,” 2019, arXiv:1906.03347.
[21] J. Tobin, R. Fong, A. Ray, J. Schneider, W. Zaremba, and P. Abbeel,
“Domain randomization for transferring deep neural networks from
simulation to the real world,” in Proc. IEEE/RSJ Int. Conf. Intell. Robots
Syst. (IROS), Sep. 2017, pp. 23–30.
[22] X. B. Peng, M. Andrychowicz, W. Zaremba, and P. Abbeel, “Sim-toreal transfer of robotic control with dynamics randomization,” in Proc.
IEEE Int. Conf. Robot. Autom. (ICRA), May 2018, pp. 3803–3810.
[23] R. Khirodkar, D. Yoo, and K. Kitani, “Domain randomization for scenespecific car detection and pose estimation,” in Proc. IEEE Winter Conf.
Appl. Comput. Vis. (WACV), Jan. 2019, pp. 1932–1940.
[24] X. Zheng, X. Chen, M. Schurch, A. Mollaysa, A. Allam, and
M. Krauthammer, “Simple contrastive representation learning for time
series forecasting,” 2023, arXiv:2303.18205.
[25] Q. Liu et al., “SimTriplet: Simple triplet representation learning with a
single GPU,” 2021, arXiv:2103.05585.
[26] X. Chen and K. He, “Exploring simple Siamese representation learning,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2021, pp. 15745–15753.
[27] S. Bai, J. Zico Kolter, and V. Koltun, “An empirical evaluation of generic
convolutional and recurrent networks for sequence modeling,” 2018,
arXiv:1803.01271.
[28] M. Tasnim Pervin, L. Tao, A. Huq, Z. He, and L. Huo, “Adversarial
attack driven data augmentation for accurate and robust medical image
segmentation,” 2021, arXiv:2105.12106.
[29] R. C. Staudemeyer and E. Rothstein Morris, “Understanding LSTM—A
tutorial into long short-term memory recurrent neural networks,” 2019,
arXiv:1909.09586.
[30] E. Eldele et al., “Time-series representation learning via temporal and
contextual contrasting,” 2021, arXiv:2106.14112.
[31] S. Liang, Y. Li, and R. Srikant, “Enhancing the reliability
of Out-of-distribution image detection in neural networks,” 2017,
arXiv:1706.02690.
[32] M. Thill, W. Konen, H. Wang, and T. Bäck, “Temporal convolutional
autoencoder for unsupervised anomaly detection in time series,”
Appl. Soft Comput., vol. 112, Nov. 2021, Art. no. 107751, doi:
10.1016/J.ASOC.2021.107751.
[33] F. Baier, S. Mair, and S. G. Fadel, “Self-supervised Siamese
autoencoders,” 2023, arXiv:2304.02549.
[34] D. Pau, A. Khiari, and D. Denaro, “Online learning on tiny microcontrollers for anomaly detection in water distribution systems,” in Proc.
IEEE 11th Int. Conf. Consum. Electron. (ICCE-Berlin), Nov. 2021,
pp. 1–6.
[35] M.-A. Tnani, M. Feil, and K. Diepold, “Smart data collection system
for brownfield CNC milling machines: A new benchmark dataset for
data-driven machine monitoring,” Proc. CIRP, vol. 107, pp. 131–136,
Apr. 2022, doi: 10.1016/J.PROCIR.2022.04.022.

2502109

[36] L. Ruf et al., “Deep one-class classification,” in Proc. Int. Conf.
Mach. Learn., 2018, pp. 4393–4402.
[37] C. Zhang et al., “A deep neural network for unsupervised anomaly
detection and diagnosis in multivariate time series data,” in Proc. AAAI
Conf. Artif. Intell., 2019, pp. 1409–1416.
[38] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: UnSupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining,
Aug. 2020, pp. 3395–3404.
[39] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” Proc.
VLDB Endowment, vol. 15, no. 6, pp. 1201–1214, Feb. 2022.
Yeseul Lee received the B.S. degree in industrial
engineering from Hanyang University, Seoul,
South Korea, in 2022. She is currently pursuing
the M.S. degree in industrial and management
engineering with Korea University, Seoul.
Her research interests include time-series
anomaly detection and domain generalization for
manufacturing.

Seunghwan Song received the B.S. degree in
information statistics from Korea University, Seoul,
South Korea, in 2019, where he is currently pursuing
the M.S. and Ph.D. degrees in industrial and
management engineering.
His research interests include representation learning and prognostics and health management in
manufacturing. He is conducting research to improve
manufacturing systems using the latest deep learning
technologies.

Kwan-Yong Park received the B.S. degree in industrial engineering from Seoul National University
of Science and Technology, Seoul, South Korea,
in 2022. He is currently pursuing the M.S. and Ph.D.
degrees in industrial and management engineering
with Korea University, Seoul.
His research interests include anomaly detection,
fault detection, object detection, and representation
learning.

Byoung-Mo Koo received the B.S. degree in
statistics and industrial and management engineering
from Korea University, Seoul, South Korea, in 2023,
where he is currently pursuing the M.S. and Ph.D.
degrees in industrial and management engineering.
His research interests include anomaly detection,
fault detection, and classification.

Jun-Geol Baek received the B.S., M.S., and
Ph.D. degrees in industrial engineering from Korea
University, Seoul, South Korea, in 1993, 1995, and
2001, respectively.
From 2002 to 2007, he was an Assistant
Professor with the Department of Industrial Systems
Engineering, Induk University, Seoul. He was also
an Assistant Professor with the Department of
Business Administration, Kwangwoon University,
Seoul, from 2007 to 2008. In 2008, he joined the
School of Industrial and Management Engineering,
Korea University, where he is currently a Professor. His research interests
include fault detection and classification (FDC), advanced process control
(APC), prognostics and health management (PHM), and big data analytics in
manufacturing.
PAPER_TEXT
