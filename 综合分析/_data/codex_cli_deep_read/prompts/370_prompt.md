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
# [370] AutoKAN: A Federated Lightweight Anomaly Detection Framework for Securing Constrained IoT Healthcare Diabetes Monitoring Systems
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
编号：370
题名：AutoKAN: A Federated Lightweight Anomaly Detection Framework for Securing Constrained IoT Healthcare Diabetes Monitoring Systems
年份：2025
DOI：10.1109/tce.2025.3596250
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3596250.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：入侵检测与网络异常检测、IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\370.txt
- 原始字符数：56713
- 本次发送字符数：56713
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

11303

AutoKAN: A Federated Lightweight Anomaly
Detection Framework for Securing Constrained IoT
Healthcare Diabetes Monitoring Systems
Nguyen Khanh Son , Arun Kumar Sangaiah , Chuang Chun-Chi, Honda Hsu, Chung-Chian Hsu ,
and Chuan-Yu Chang
Abstract—The adoption of Internet of Things (IoT) technology in healthcare has significantly enhanced patient care by
improving both the efficiency and cost-effectiveness of healthcare delivery systems. Specifically, for diabetic patients, IoT
facilitates continuous health monitoring, enabling healthcare
professionals to track patients’ conditions in real time and
detect potential complications at an early stage. However, the
growing number of IoT devices has also introduced security
concerns, particularly in terms of cyber threats that exploit
resource limitations such as power and memory. Especially
in the healthcare sector, where data is highly sensitive and
distributed in nature, privacy is one of the most critical aspects.
A promising privacy-preserving technology, known as federated
learning, addresses these challenges effectively. This research
presents a lightweight federated anomaly detection framework
tailored for constrained environments, including small-scale IoT
devices. We conceptualize IoT devices as essential components
within the edge continuum and leverage anomaly detection
models to enhance security. Our anomaly detection model is
built on an autoencoder architecture; however, rather than
relying on conventional multilayer perceptron (MLP) networks,
we utilize Kolmogorov–Arnold Networks (KAN) with an adaptive
threshold to minimize parameter complexity and enable realtime deployment. Additionally, the federated learning mechanism
is applied to ensure the privacy of patient data is safeguarded.
Experimental results indicate that our model achieves an accuracy exceeding 99.5% and a precision of 100%, outperforming
traditional autoencoders while utilizing 50% fewer parameters
Received 19 March 2025; revised 24 May 2025 and 27 July 2025; accepted
2 August 2025. Date of publication 6 August 2025; date of current version
8 December 2025. This work was supported in part by the Ministry of
Education (MOE), Taiwan, through the Yushan Young Scholar Fellowship
under Grant MOE-111-A013, and in part by the Dalin Tzu Chi Hospital,
Buddhist Tzu Chi Medical Foundation under Grant TCRD113(2)-C-02.
(Nguyen Khanh Son and Arun Kumar Sangaiah contributed equally to this
work.) (Corresponding authors: Chuang Chun-Chi; Honda Hsu.)
Nguyen Khanh Son and Arun Kumar Sangaiah are with the International
Graduate School of Artificial Intelligence, National Yunlin University
of Science and Technology, Douliu 64002, Taiwan (e-mail: khanhsonnguyen0811@gmail.com; aksangaiah@ieee.org).
Chuang Chun-Chi is with the Department of Surgery, Division of
Plastic Surgery, Dalin Tzu Chi Hospital, Buddhist Tzu Chi Medical
Foundation, Dalin 622, Chia-Yi, Taiwan (e-mail: rosa71234@tzuchi.com.tw;
putinto3@gmail.com).
Honda Hsu is with the Department of Surgery, Division of Plastic Surgery,
Dalin Tzu Chi Hospital, Buddhist Tzu Chi Medical Foundation, Dalin 622,
Chia-Yi, Taiwan, and also with the School of Medicine, Tzu Chi University,
Hualien 97004, Taiwan (e-mail: hondahsu@yahoo.com.tw).
Chung-Chian Hsu is with the Department of Information Management,
National Yunlin University of Science and Technology, Douliu 64002, Yunlin,
Taiwan (e-mail: hsucc@yuntech.edu.tw).
Chuan-Yu Chang is with the Department of Computer Science and
Information Engineering, National Yunlin University of Science and
Technology, Douliu 64002, Taiwan (e-mail: chuanyu@yuntech.edu.tw).
Digital Object Identifier 10.1109/TCE.2025.3596250

and achieving twice the speed in training and inference time.
This demonstrates the superiority of our approach in anomaly
detection, particularly in fields where precision is the most
important metric, such as medical applications.
Index Terms—Federated learning, smart healthcare, IoT,
anomaly detection, Kolmogorov-Arnold networks, diabetes
monitoring.

S YMBOL D EFINITIONS
•

L: Total number of layers in a KAN network.
z0 : Input to the KAN, z0 ∈ Rd0 .
• l : Function matrix corresponding to the l-th layer in
KAN.
• ψl,j,i : Activation function linking layer l to layer l+1,
where l =
0, 1, 2, . . . , L−1; i =
1, 2, . . . , dl ;
j = 1, 2, . . . , dl+1 .
• dl : Number of nodes in layer l.
• dl+1 : Number of nodes in layer l + 1.
• zl,i : Input to ψl,j,i .
• z̃l,j,i : Output of ψl,j,i .
• z(l+1),j : Activation value of the (l + 1, j) neuron.
• αs : A learnable parameter in the activation function.
• αr : A learnable parameter in the activation function,
initialized according to Xavier initialization.
• S(z): A learnable function computed using B-spline basis
functions.
• wtl : AutoKAN model at round t, where l ∈ {1, 2, 3, . . . ,
L} and L is the number of devices.
• Z: Input to the Encoder network, (z1 , z2 , z3 , . . . , zn ).
• K: Encoder network.
• h: Output of the Encoder network, K(Z).
• K  : Decoder network.
• Z  : Output of the Decoder network, K  (h).
• LAutoKAN : Loss function, calculated using Mean Squared
Error (MSE).
• gt : Gradient at time step t.
• θ : Learnable parameters {αs , αr , c}.
• mt : Moving average of gradients.
• vt : Moving average of squared gradients.
• β1 , β2 : Hyperparameters for momentum and variance
decay.
• η: Learning rate.
• : Small constant for numerical stability.
• nl : Number of samples on device l.
• N: Total dataset size across selected devices.
• Ei : Reconstruction error for Zi .
•

c 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
1558-4127 
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

11304

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

λmax : Maximum reconstruction error.
λmin : Minimum reconstruction error.
• Eitest : Reconstruction error for test data Ti .
•
•

I. I NTRODUCTION
IABETES is a chronic health condition that arises when
the pancreas fails to produce sufficient insulin or when
the body is unable to use insulin effectively. The World Health
Organization (WHO) reported that in 2021, an estimated
830 million individuals were affected by diabetes, leading to
approximately 2 million deaths. Furthermore, elevated blood
glucose levels were linked to nearly 11% of deaths associated
with cardiovascular diseases [1].
Advancements in IoT-based biomedical devices are playing
a crucial role in both self-management for diabetic patients
and supporting healthcare organizations responsible for patient
care [2]. IoT healthcare sensors and smart devices collect a
variety of health parameters, including blood pressure, glucose
levels, heart rate, and electrocardiogram (ECG) readings. The
gathered data is then transmitted to a healthcare server for
storage and analysis via wireless networks, such as WLANs,
PANs, or WMANs. In recent years, the Ambient Assisted
Living (AAL) methodology has been introduced to improve
care for elderly diabetic patients. This approach enables caregivers to monitor blood sugar and glucose levels in real time
using smart devices. Additionally, IoT-enabled solutions, such
as ambulance dispatch systems, ensure immediate medical
assistance in emergency situations. Anomaly detection in
IoT healthcare refers to identifying observations, events, or
data points that deviate significantly from normal patterns,
distinguishing them from the rest of the sensor dataset.
Identifying and handling anomalies is crucial because they
can impact the decision-making process of medical professionals and directly affect patient well-being. Furthermore,
detecting anomalies improves data quality, contributing to the
integrity and reliability of data, which is essential not only
for training machine learning models but also for accurate
patient diagnosis. The main cause of unusual events is sensor inaccuracies, which can lead to anomalies for various
reasons, such as low latency, cyberattacks, or hardware failures. Additionally, anomalies can arise in resource-constrained
environments.
In the healthcare domain, Abououf et al. [3] introduced
an interpretable method for anomaly detection, utilizing an
autoencoder to rapidly identify anomalous events, while a deep
neural network handles classification. To enhance explainability, the authors incorporated KernelSHAP. Likewise,
Aguilar et al. [4] integrated a decision tree with an autoencoder
to enhance the interpretability of the autoencoder’s outputs,
offering domain experts a more intuitive explanation. Although
autoencoders offer a promising approach for anomaly detection, their performance still needs improvement [5], [6], [7],
[8], particularly in IoT systems, where millions of data points
are generated daily. Even a 1% error rate can translate into a
significant number of misdetections, making accuracy crucial
in such environments.
In IoT systems, edge devices often have limited computational
resources, making the development of lightweight anomaly

D

detection models essential. Fan et al. [9] introduced LUAD,
a lightweight anomaly detection framework that integrates a
Temporal Convolutional Network with a Variational autoencoder. Their approach significantly reduces the number of
parameters—nearly ten times fewer than the OmniAnomaly
model—while maintaining comparable accuracy. Additionally,
several studies have also focused on designing lightweight
anomaly detection models for edge devices [10], [11], [12].
However, many of these works primarily demonstrate their
effectiveness in high-computing environments and often rely on
a limited set of evaluation metrics, which may not fully validate
their performance in real-world edge computing scenarios. On
the other hand, privacy is also an important aspect of healthcare,
and concerns about data security often hinder the sharing
of healthcare information, thereby limiting opportunities for
improvement and innovation in the field.
This research aims to address the following questions:
1) What level of accuracy and precision can a lightweight
anomaly detection framework based on Kolmogorov–
Arnold Networks (KANs) achieve in IoT-based
healthcare monitoring systems?
2) How does the proposed framework perform in
resource-constrained environments compared to traditional autoencoder-based methods?
3) How does integrating federated learning into the
AutoKAN framework support the preservation of patient
data privacy while maintaining effective anomaly detection in decentralized healthcare settings?
To address the challenges mentioned above, this
work proposed a novel deep federated learning anomaly
autoencoder-based detection in IoT healthcare system,
focusing on lightweight, performance, privacy, and precision
detection. Inspired by the latest existing research, an
autoencoder-based model has been developed due to
the advantage of Kolmogorov–Arnold Networks [13] in
performance. The reconstructed error is calculated and
used as the anomaly score with an adaptive threshold to
ensure the scalability and model accuracy, especially in an
uncertainty environment like IoT. Therefore, a federated
learning mechanism is proposed to aggregate local data while
ensuring patient privacy. Hence, the contribution of this work
can be written as follows:
1) Develop the AutoKAN federated anomaly detection
framework for healthcare IoT, ensuring high accuracy,
efficiency, privacy and robustness in detecting anomalies
within a controlled environment. The model is designed
to adapt to real-world healthcare scenarios, where reliability and privacy are critical.
2) Simulate a resource-constrained computing environment
to evaluate the efficiency and scalability of the proposed
model. This includes testing under limited computational resources to assess the feasibility of deploying
AutoKAN in edge and IoT-based healthcare systems.
The results showcase the model’s proficiency in terms
of execution time, inference speed, and overall computational complexity, ensuring its practicality for real-time
applications.
3) Enhance detection reliability by minimizing false
positives and false negatives through an adaptive

SON et al.: AutoKAN: A FEDERATED LIGHTWEIGHT ANOMALY DETECTION FRAMEWORK

thresholding mechanism. This approach dynamically
adjusts detection thresholds based on contextual factors, improving accuracy while ensuring scalability. The
proposed method contributes to more reliable anomaly
detection, making it suitable for large-scale deployments
in diverse healthcare environments.
The structure of this paper is organized as follows: Section II
reviews related work. Section III describes the methodology
for stress prediction and the experimental design. Further
details on the experimental setup are provided in Section IV.
Section V evaluates the performance of the proposed model
and includes a discussion. The study’s limitations and potential future research directions are outlined in Section VI-C.
Finally, Section VII summarizes the key findings of this
paper.
II. R ELATED W ORK
Anomaly detection in IoT, particularly in healthcare, has
emerged as a critical area of research due to the increasing
connectivity of medical devices and the associated security
risks. This section provides a detailed exploration of anomaly
detection techniques, frameworks, and models tailored for
IoT healthcare applications, drawing insights from recent
studies. Additionally, a Comparison of related work is detailed
in Table I.
A. Anomaly Detection in IoT
Anomaly events may be well-reconstructed but difficult
to distinguish. Zeng et al. [26] applied particle swarm
optimization to optimize hyperparameters for an adversarial
VAE for anomaly detection. Their method achieves high
performance in various domains, such as secure water treatment, water distribution, the Mars Science Laboratory, and
power systems. Katbi et al. [27] propose a novel IoT anomaly
detection system that uses a one-class approach with a deep
learning architecture. Their methodology involves integrating a Deep SVDD objective function with an adversarial
interpolated network structure to achieve effective grouping
of normal data points in the latent space. Using a multihead graph attention network (MD-GAT) to capture feature
correlations and a temporal convolution network to learn
temporal dependencies, Tang et al. [28] proposed a supervised
contrastive learning-based spatiotemporal variational autoencoder (SC-STVAE). Vijai and Sivakumar [14] propose a novel
anomaly detection approach for industrial applications using
a BiLSTM-Variational Autoencoder (BiLSTM-VAE) model
with a dynamic loss function. The model aims to overcome
the limitations of traditional anomaly detection methods, such
as scalability issues, high false alarm rates, and reliance on
skilled expertise.
Focusing on energy-efficient models by reducing anomalyirrelevant sensory data transmitted within the network,
Guo et al. [15] developed EGNN, an anomaly detection
method utilizing a graph neural network. Nonetheless, this
approach lacks generalization and scalability. Utilizing a biastrained artificial intelligence neural network to formulate
a set of rules at each node of a tree-based algorithm,

11305

Sivapalan et al. [16] developed an interpretable rule-mining
solution for detecting anomalies in real-time ECG signals.
Additionally, the model achieves over 50% power savings in sensor consumption by transmitting only anomaly
events. However, its performance is not highly comparable,
reaching only approximately 85-90% accuracy. Achieving
100% effectiveness in malware detection for Linux-based
IoT, Breitenbacher et al. [17] proposed HADES-IoT, a hostbased anomaly detection system that not only ensures high
accuracy but also maintains low overhead, making it suitable for high-performance demanding tasks. Xu et al. [29]
proposed an unsupervised framework to jointly optimize the
graph contrastive learning module and the network reconstruction module for high-precision anomaly detection in
networks of consumer electronic devices. Their approach
shows superior results on three public benchmark datasets.
AlMahadin et al. [30] applied the deep learning technique
GRU to detect anomalies such as DDoS attacks in Vehicular
Ad-hoc Networks (VANETs). Similarly, Nissar et al. [31]
employed a variational autoencoder with various optimization
objectives, including divergence, KL-divergence, and reconstruction error, using the AGE-MOEA and R-NSGA-III
algorithms. Zhao et al. [32], using a convolutional encoder
and a deconvolutional decoder—each leveraging the parallelism of stacked Advanced Dilated Causal Convolutional
(ADCC) blocks—demonstrated that their approach outperforms traditional methods in anomaly detection within satellite
orbit environments. Zukai et al. [33] introduced a metalearning framework that demonstrated superior performance
compared to other algorithms across multiple datasets,
including USTL-EHMS-2020, IoTID20, and WUSTL-IIOT2021, attaining an accuracy of 99%. However, ensemble
methods may not be well-suited for IoT-based environments where real-time applications demand rapid processing.
Fang et al. [18] developed an anomaly detection model
tailored for medical IoT systems, utilizing rough set theory and fuzzy core vector machines. Despite its novel
approach, the model’s accuracy remains approximately 92%.
Albattah and Rassam [19] employed a convolutional long
short-term memory (ConvLSTM) network to detect anomalies in wireless body area networks. Experimental findings
validated the model’s effectiveness, reporting a 98% F1score and 99% accuracy, surpassing traditional CNN and
LSTM-based models. Likewise, Shaikh et al. [34] achieved
an impressive 99.78% accuracy in intrusion detection within
the Internet of Medical Things (IoMT) by leveraging a
hybrid approach combining CNN and LSTM architectures.
Building on LSTM-based methodologies, Wang et al. [35]
concentrated on constructing a distributed anomaly detection
system that ensures both high precision and low latency.
In a similar vein, Hasniuj et al. [36] proposed a robust
framework capable of identifying anomalous behaviors in IoT
devices while also implementing mechanisms to restrict and
mitigate their effects on interconnected systems. Their solution
incorporates a lightweight machine learning model designed
for accurate packet-level anomaly detection. Additionally,
Balaji et al. [20] explored an ensemble-based strategy by
integrating SqueezeNet and NasNet architectures to train a

11306

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

TABLE I
C OMPARISON OF R ELATED W ORK IN A NOMALY D ETECTION FOR I OT H EALTHCARE S YSTEMS

deep learning model aimed at intrusion detection within
healthcare-related IoT infrastructures.
B. Federated Learning In IoT Healthcare System
With the rise of privacy concerns and the growing number
of data breaches across industries, the need for technologies that safeguard data privacy while maintaining accuracy
and sustainability has become crucial. Federated learning is
gaining attention as a promising solution to address these
challenges. Elayan et al. [21] introduced a deep federated
learning approach for monitoring and analyzing healthcare
data to detect skin diseases. Meanwhile, Akter et al. [22]
developed a three-fold federated edge aggregator to enhance
the security of healthcare systems against privacy attacks. The
effectiveness of their model was evaluated using the MNIST,
CIFAR-10, STL-10, and COVID-19 chest X-ray datasets,
achieving an accuracy of approximately 90%. Utilizing NonFungible Tokens (NFTs) with federated learning, Sai et al. [23]
encouraged patients to store data in the NFT marketplace and

addressed some challenges in federated learning using the
Polyak-averaging method. To enhance privacy-aware access
control in IoT healthcare systems, Lin et al. [24] proposed
a deep federated learning approach that utilizes graph convolutional networks to gain user trust by obtaining users’
influences. Li et al. [25] developed a federated supervised
learning model focused on solving the data heterogeneity
problem. This approach outperforms state-of-the-art methods
such as SCFed, CBAFed, and FedCD by providing a suitable
strategy to mitigate imbalanced class distributions.

C. Kolmogorov-Arnold Networks
Nowadays, in addition to the popular MLP network, various
new architectures are emerging to explore novel structures
with better interpretability and higher performance. Abd
Elaziz et al. [13] introduced the Kolmogorov-Arnold Network
(KAN), drawing inspiration from the Kolmogorov-Arnold
representation theorem. The Kolmogorov–Arnold Network has

SON et al.: AutoKAN: A FEDERATED LIGHTWEIGHT ANOMALY DETECTION FRAMEWORK

recently garnered significant attention for its strong interpretability and exceptional performance. Seydi et al. [37]
compared various KAN variants, including Fully Connected
KAN, Chebyshev-KAN, Radial Basis Function KAN, and
Naïve-Fourier-KAN, for hyperspectral change detection. Their
experiments demonstrated that Chebyshev-KAN achieved
the best performance for this task. In another study,
Jiang et al. [38] employed the Kolmogorov–Arnold Network
for short-term load forecasting in power systems. Their
results demonstrated the effectiveness of the proposed model,
as the RMSE score outperformed other methods, such as
XGBoost and MLP. Liu et al. [39] utilized Kolmogorov–
Arnold Networks for semi-supervised impedance inversion.
Through experimental comparisons of acoustic impedance
fitting results, they showed that KAN and Convolutional
KAN exhibit stronger fitting capabilities for long-term acoustic
impedance data than traditional linear layers and CNNs.
To address the challenges related to limited computing and
memory resources, Song et al. [40] propose an adaptive
wavelet transform Kolmogorov–Arnold network approach
for hybrid control devices using motor imagery electroencephalography. Do et al. [41] evaluated and compared
multiple KAN variants, such as Original-KAN, Fast-KAN,
Jacobi-KAN, DeepKAN, and Chebyshev-KAN, for botnet
classification. Their findings indicated that the Original-KAN
achieved the best performance on the N-BaIoT, IoT23, and
IoT-BotNet datasets. The application of KAN shows its potential for better performance in various tasks. This motivates us
to conduct research with KAN for our work.

11307

for j = 1, . . . , dl+1 . This can be rewritten as:
zl+1 = l zl
where:

⎡

(4)

⎤
ψl,1,3 . . . ψl,1,dl
ψl,2,3 . . . ψl,2,dl ⎥
⎥
⎥
..
..
..
⎦
.
.
.
ψl,dl+1 ,1 ψl,dl+1 ,2 ψl,dl+1 ,3 . . . ψl,dl+1 ,dl

ψl,1,1
⎢ ψl,2,1
⎢
l = ⎢ .
⎣ ..

ψl,1,2
ψl,2,2
..
.

(5)

The activation function is computed as:
ψ(z) = αr b(z) + αs S(z)

(6)

where:
z
(7)
1 + e−z
and S(z) is computed as, with ci are the learnable variable and
Bi (z) are B-spiline basis functions:

ci Bi (z)
(8)
b(z) =

i

In the initial stage, αs = 1, αr is initialized according to the
Xavier initialization and S(z) ≈ 0.
A smaller KAN network can achieve accuracy comparable
to or even surpass that of a larger MLP network by learning
the activation functions directly. This is especially beneficial
for developing lightweight models on devices with limited
computational resources.
B. AutoKAN Architecture

III. M ETHODOLOGY
A. KAN Layer
KAN emerges as a promising alternative to Multi-Layer
Perceptrons (MLPs), delivering enhanced performance and
faster computation. The primary difference between KAN and
MLP lies in their activation functions: while MLPs rely on
fixed activation functions, KAN utilizes learnable activation
functions on the edges, which are subsequently aggregated at
the nodes.
A KAN can be structured as a composition of multiple
KAN layers. Let L denote the total number of layers in a
KAN network, with the input represented as z0 ∈ Rd0 . The
transformation of KAN can be expressed as:


(1)
K(z) = L−1 ◦ L−2 ◦ · · · ◦ 0 (z)
where l represents the function matrix corresponding to the
l-th layer in KAN. More specifically, we define ψl,j,i with:
l = 0, 1, 2, . . . , L − 1;

i = 1, 2, . . . , dl ;

j = 1, 2, . . . , dl+1

(2)
where ψ denotes the activation function linking layer l to layer
l + 1. Here, dl and dl+1 represent the number of nodes in
layers l and l + 1, respectively. Let zl,i be the input to ψl,j,i
and z̃l,j,i be the corresponding output. The activation value of
the (l + 1, j) neuron is computed as:
z(l+1),j =

dl

i=1

z̃l,j,i =

dl

i=1

 
ψl,j,i zl,i

(3)

Based on the KAN layer, we design the proposed AutoKAN,
whose structure is illustrated in Figure 1. The AutoKAN
model, denoted as wtl at round t, where l ∈ {1, 2, 3, . . . , L} and
L is the number of devices in the federated network, consists
of two main components: the encoder and the decoder. Each
component is built using a stack of KAN layers. After training
for E local epochs, the weights are sent to the server to update
the global model.
We denote the encoder network as K, with input Z =
(z1 , z2 , z3 , . . . , zn ). By applying equation (1), we obtain:
K(Z) = (

L−1 ◦

L−2 ◦ · · · ◦

0 )Z = h

(9)

Similarly, the encoder network is denoted as K  , with input
h = K(Z), with P denoted as the total number of layers in
Decoder network, leading to:
K  (h) = (

P−1 ◦

P−2 ◦ · · · ◦

0 )h = Z



(10)

The loss function is calculated using the Mean Squared
Error (MSE):
2
1  
Z −Z
LAutoKAN =
(11)
N
The learnable parameters in KAN are updated using the
Adam optimizer. The optimization process can be described
as follows:
gt = ∇θ J(θt ),

where θ = {αs , αr , c}

mt = β1 mt−1 + (1 − β1 )gt
vt = β2 vt−1 + (1 − β2 )g2t

(12)
(13)
(14)

11308

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

Fig. 1. Federated mechanism for anomaly detection for privacy-preserving IoT diabetes healthcare system. This illustrates the flow of information and model
updates within the federated learning framework.

m̂t =

mt
,
1 − β1t

αs(t+1) = αs(t) −
αr(t+1) = αr(t) −
(t+1)

c

(t)

=c

−

vˆt =
η

vt
1 − β2t

(15)

Algorithm 1 Federated Learning Framework for Local Model
Aggregation (FedAvg)

m̂t

(16)

1: Input: Initial global model w0global , number of participatm̂t

(17)

vˆt + 
η

vˆt + 
η
m̂t
vˆt + 

(18)

where η represents the learning rate, β1 and β2 serve as
hyperparameters that influence momentum and variance decay,
and  is a small constant ensuring numerical stability by
preventing division by zero. The gradient at time step t is
denoted as gt , while mt and vt correspond to the moving
averages of gradients and squared gradients, respectively.
Additionally, t signifies the current iteration step.
This step-by-step optimization ensures efficient parameter
updates, allowing AutoKAN to learn feature representations
effectively.
C. Federated Autoencoder Kolmogorov-Arnold Networks
With Adaptive Threshold for Anomaly Detection
After training, the server aggregates updates using Federated
Averaging mechanism.
 nl
wt+1
(19)
wt+1
global =
l
N
t

ing devices L, local training epochs E, learning rate η, and
total communication rounds T.
2: Output: Optimized global model wT
global
3: Server Initialization:
4: The global model w0global is initialized
5: The initialized model is distributed to all devices l ∈ L
6: for t = 1 to T do
7:
Server selects a subset of devices St ⊆ L
8:
for each device l ∈ St concurrently do
9:
Retrieve the current global model wtglobal
10:
Train a local model on device l over E epochs,
following equations (12)–(18)
11:
Transmit the updated local model wt+1
back to the
l
server
12:
end for
13:
The server applies FedAvg to aggregate the models:
nl t+1
14:
wt+1
l∈St N wl
global =
15:
The updated global model wt+1
global is then shared with
all devices
16: end for
17: Return the final trained global model wT
global

l∈S

where nl is the number of samples on device l and N =
l∈St nl is the total dataset size across selected devices. The
updated global model is then sent back to all devices, and
this process repeats for T rounds until convergence. The final
model wTglobal is deployed for inference. Details process is
provided in Algorithm 1.
The process flow of testing and calculating adaptive threshold is illustrated in Algorithm 2. The normal data is fed
into AutoKAN to calculate the reconstruction error. Note that
the input data consists only of normal data. Our aim is to

intentionally overfit the model to the training data so that
techniques such as dropout and batch normalization are not
required. After training, the reconstruction error E can be used
to extract the threshold for normal data as follows:
λmax = max(E),

λmin = min(E)

During the testing phase, any value exceeding or falling
below this boundary is considered an anomaly.

SON et al.: AutoKAN: A FEDERATED LIGHTWEIGHT ANOMALY DETECTION FRAMEWORK

Algorithm 2 AutoKAN Anomaly Detection With Adaptive
Threshold at the Local lth Device in Round t
1: Input: Normal data Z, Test data T, Local model wtl
2: Compute the reconstruction error:
Ei = wtl (Zi ) − Zi

∀Zi ∈ Z

(20)

3: E ← E ∪ {Ei }
4: Compute anomaly thresholds:

λmax = max(E),

λmin = min(E)

(21)

5: Test Phase:
6: for each Ti ∈ T do
7:
Compute the reconstruction error:

2
1  t
wl (Ti ) − Ti
(22)
N
8:
if Eitest > λmax or Eitest < λmin then
9:
Ti is classified as an Anomaly
10:
else
11:
Ti is classified as Normal
12:
end if
13: end for
14: Output: Classification result (Anomaly or Normal)
Eitest =

11309

utilized normal traffic from the 70% training set, resulting in
a total of 56,044 normal traffic samples specifically used for
model training.
B. System and Model Configuration
The experimental setup involved a high-performance computing system featuring an Intel Core i7-13700 processor (24
cores), 32GB of RAM, and an NVIDIA GeForce RTX 4060
GPU. The implementation was performed in Python 3.10.15,
leveraging the PyOD library [44] to execute anomaly detection
algorithms for benchmarking against the proposed method.
To further evaluate the model’s efficiency in real-world
deployment scenarios, we simulated a resource-constrained
environment comparable to a Raspberry Pi 5, featuring 2GB
RAM and a quad-core processor. This setup was used to assess
the feasibility of deploying the proposed model in low-power
edge computing devices.
The model was trained using Mean Squared Error (MSE)
Loss, with the Adam optimizer and a total of 30 training
epochs, learning rate α = 0.001. This configuration ensures
stable learning while minimizing reconstruction errors, making
the model suitable for anomaly detection in both high-end and
low-resource environments.
C. Evaluation Metrics

IV. E XPERIMENT D ESIGN
A. Dataset
The dataset simulates an IoT-based environment, specifically an Intensive Care Unit (ICU), populated with nine
patient monitoring devices. The detailed specifications of the
sensors integrated within this setup are illustrated in Figure 3.
To rigorously evaluate the system’s security and resilience,
four distinct types of cyberattacks were meticulously simulated: Message Queuing Telemetry Transport (MQTT)
Publish Flood, MQTT Authentication Bypass Exploit, MQTT
Malicious Packet Injection, and Constrained Application
Protocol (CoAP) Replay Exploit. The simulation was conducted using IoT-Flock [42], a specialized and open-source
tool designed explicitly for modeling and generating traffic in
diverse IoT environments. IoT-Flock was carefully configured
to closely emulate real-world ICU equipment and operational
dynamics, incorporating actual data profiles and time profiles
derived from the analysis of real-time value ranges of ICU
devices. During the simulation, network traffic, encompassing both normal and attack scenarios, was captured using
Wireshark, a widely-used network protocol analyzer, to log
both packet headers and payloads. Subsequently, a custom
Python script was employed to extract relevant networklayer and application-layer features from the captured traffic,
facilitating a detailed and focused analysis. The dataset,
originally created and openly published by Hussain et al. [43],
comprises 80,126 normal traffic samples and 76,810 attack
traffic samples, meticulously labeled as 0 (normal) and 1
(attack), respectively. In our experiment, we allocated 70% of
the data for training and 30% for testing to ensure robust model
development and evaluation. However, given that our approach
necessitates only normal data for training, we exclusively

To comprehensively assess the performance of the proposed
model, we consider multiple evaluation metrics.
1) Accuracy:
Accuracy =

Pt + Nt
Pt + Nt + Pf + Nf

(23)

where Pt , Nt , Pf , and Nf represent true positives, true negatives, false positives, and false negatives, respectively.
2) Precision:
Pt
Pt + Pf

(24)

Pt
Pt + Nf

(25)

Precision =
3) Recall (Sensitivity):
Recall =
4) F1-Score:

2PR
(26)
P+R
5) Memory Usage: Represents the amount of RAM
required by the model during inference, measured in
megabytes (MB) or gigabytes (GB).
6) Floating Point Operations per Second (FLOPs):
Indicates the total number of floating-point calculations performed by the model, reflecting computational efficiency.
7) Number of Parameters: Represents the total learnable
weights in the model, influencing both computational cost and
generalization ability.
8) Running Time: Measures the time taken by the model
to process whole test input samples, evaluated in seconds (s).
9) Traffic Per Second: Determines the number of data
points or samples processed by the model per second.
F1 =

11310

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

Fig. 2.
classes.

Two-dimensional (left) and three-dimensional (right) t-SNE embeddings of the dataset, revealing distinct clusters corresponding to two different

Fig. 3.

Overview of Patient Monitoring Sensors.

These metrics collectively provide a comprehensive evaluation of the model’s accuracy, efficiency, and computational
feasibility in different deployment scenarios.
V. E XPERIMENT R ESULT
A. Comparison With State-of-the-Art Anomaly Detection
Techniques
The results are presented in Table II, where it is evident that AutoKAN outperformed more than 28 methods,
including deep learning, unsupervised learning, and statistical
approaches, demonstrating its superior performance across
various anomaly detection techniques. AutoKAN achieved an
accuracy of 99.11% and a precision of 100%, indicating that
the model produced no false positives. The high F1-score of
99.08% further highlights the model’s proficiency in the medical field, where minimizing errors is crucial. Once again, deep
learning models clearly showcase their effectiveness in tasks
such as anomaly detection, particularly when large amounts of
data are available. For instance, deep learning-based models,
such as autoencoder and AnoGAN, exhibit significantly better
performance compared to other categories, such as ProximityBased and Outlier Ensemble methods. This can be attributed
to the increasing complexity of modern networks and IoT
environments, where traditional approaches fail to capture
intricate patterns. Deep learning models, on the other hand,
are better equipped to learn from complex data distributions.

However, not all deep learning approaches perform equally
well. Models such as DeepSVDD, MO_GAAL, and VAE
exhibit relatively lower performance, suggesting that certain
architectures may not be well-suited for specific anomaly
detection tasks.
Figure 4 illustrates the training loss of a model over 30
epochs, showing a general trend of decreasing loss as training
progresses. The loss decreases significantly in the initial
epochs (0-20), indicating rapid learning, and then plateaus
after epoch 20, suggesting convergence with diminishing
returns from further training. While the low final loss suggests
successful training, the plateauing raises the possibility of
overfitting, which is the goal we are trying to achieve. This
overfitting with normal training data aims to increase the
model’s sensitivity to anomalies. Figure 5 reveals that the
model performs exceptionally well in correctly classifying
normal events, with 24,082 out of 24,082 instances correctly
predicted. However, there is a small number of misclassifications in anomaly detection. Specifically, 420 anomaly events
were incorrectly classified as normal. This indicates that while
the model has a very low false positive rate, it exhibits a small
but non-zero false negative rate.
Another reason that contributes to the superiority of the
proposed method over other approaches is the adaptive thresholding strategy. Instead of using a fixed threshold, we define
dynamic boundaries by taking the maximum and minimum
values from the normal distribution. This allows the model

SON et al.: AutoKAN: A FEDERATED LIGHTWEIGHT ANOMALY DETECTION FRAMEWORK

11311

Fig. 5. Confusion matrix for AutoKAN on the testing dataset, showing the
number of correct and incorrect predictions for normal and anomaly events.
Fig. 4.

Training Loss Progression During Model Training (30 Epochs).

TABLE II
P ERFORMANCE C OMPARISON OF D IFFERENT A NOMALY D ETECTION
M ODELS

Fig. 6. Comparison of training time between autoEncoder and AutoKAN,
demonstrating the improved efficiency of AutoKAN.

Our model achieves the highest precision among all models.
However, for other metrics such as recall, accuracy, and F1score, supervised models demonstrate superior performance.
This outcome is expected, as supervised models rely on a
large volume of labeled data for training, allowing them to
effectively learn and recognize cyberattack patterns.
The key advantage of our model is that it does not require
labeled attack data for training. In real-world applications, the
lack of labeled data is often a significant challenge, both in
terms of data availability and cost. Despite this limitation, our
model still achieves comparable performance to supervised
models, with only approximately 0.01% error margin, which
is an acceptable trade-off given the benefits of unsupervised
learning.

to adapt more effectively to variations in data, ensuring
that anomalies are detected more reliably. By leveraging
this adaptive threshold, the proposed method achieves better
performance compared to other approaches, as it minimizes
both false positives and false negatives, making it more robust
in real-world anomaly detection tasks.
B. Compare With Supervised Models
In this section, we compare our model with various supervised models. The experiments and results are based on the
study by Hussain et al. [43], with details provided in Table III.

C. Model Complexity Compare With Traditional Auto
Encoder
In this section, we demonstrate the advantages of AutoKAN
compared to the conventional autoencoder in anomaly detection tasks. Additionally, we compare both models in terms
of model complexity and runtime performance. Table V provides details on memory usage, FLOPs, and the number of
parameters compared between the traditional autoencoder and
AutoKAN. The traditional autoencoder has seven times more
parameters than AutoKAN while achieving slightly lower
performance. Furthermore, AutoKAN requires only 0.01 MB

11312

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

TABLE III
P ERFORMANCE C OMPARISON OF ML C LASSIFIERS

TABLE IV
I NFERENCE P ERFORMANCE M ETRICS

TABLE V
C OMPARISON OF AUTOENCODER AND AUTO KAN

of memory–ten times less than the traditional autoencoder–
while the FLOPs of the autoencoder are nearly eighty times
higher than those of AutoKAN.
On the other hand, we recorded the training time in
Figure 6, which highlights a significant difference in computational efficiency between the two models. AutoKAN
requires only 95.9 seconds to train 50,000 samples, whereas
the autoencoder takes 157.6 seconds for the same dataset.
This demonstrates that AutoKAN not only accelerates the
training process but also scales more efficiently as the dataset
size increases. As training data grows, the gap in training
time between the two models is expected to widen, making
AutoKAN a more practical choice for large-scale applications
where computational efficiency is critical.

D. Model Performance in a Resource-Constrained
Environment
In this section, we demonstrate the efficiency of AutoKAN
in a resource-constrained environment, where computational capacity is highly limited. Table IV provides detailed
information based on ten independent runs, reporting the average values. The average runtime per sample is 0.0297 seconds,
indicating that AutoKAN can process more than 1.6 million
traffic samples per second. This meets the requirements for
real-time applications. Even when processing a high volume

of traffic simultaneously, AutoKAN demonstrates remarkable computational efficiency, utilizing only 21.82% of CPU
resources and approximately 1050 MB of memory. These
findings indicate that AutoKAN can handle substantial workloads without significantly taxing system resources, ensuring
smooth and uninterrupted performance. This efficiency is especially vital for deployment in resource-limited environments,
including embedded systems, edge computing devices, and
IoT applications, where computational power and memory
are restricted. AutoKAN stands out as a highly practical
solution by minimizing resource consumption while efficiently
processing large-scale data in real time. Its ability to perform high-speed anomaly detection with minimal hardware
investment makes it well-suited for such scenarios. Its ability to operate effectively under such conditions reinforces
its suitability for large-scale, cost-effective implementations
across various domains, including cybersecurity, industrial
monitoring, and healthcare analytics.

VI. D ISCUSSION
A. The Potential of AutoKan in Real-World Application
The AutoKAN model presents a significant potential for
real-world deployment in IoT devices for hospitals in monitoring sensor signals. Due to its lightweight design, the model can
offer the advantage of cost-effectiveness by using less powerful
processors and less memory, which results in a lower price
point per device. This is crucial for widespread deployment
in health settings, where numerous sensors and monitoring
devices might be needed across a hospital or for large numbers
of patients. Furthermore, the reduction in device cost makes
it more economically feasible to deploy on a large scale.
Hospitals can equip more beds and rooms with monitoring
capabilities without incurring exorbitant expenses.

SON et al.: AutoKAN: A FEDERATED LIGHTWEIGHT ANOMALY DETECTION FRAMEWORK

Fig. 7.

11313

Comparison of execution time and processing speed for autoEncoder and AutoKAN, highlighting AutoKAN’s superior performance.

B. The Ethical and Privacy Implications
Federated learning inherently provides a robust framework
for data privacy. In our framework, the federated averaging
algorithm is utilized to ensure that patient data remains
decentralized. Instead of transmitting raw data to a central
server for AI model training, federated learning offers a
decentralized solution where each local device trains its local
AutoKAN model using its own data. While KANs offer better
explainability than traditional MLPs, the federated learning
process itself can introduce complexity. Ensuring transparency
in the model aggregation process and providing explanations
for the model’s decisions are crucial ethical considerations,
particularly in healthcare. Furthermore, establishing clear data
governance and responsibility locally is another essential ethical and privacy aspect. Due to the model’s local deployment,
it becomes more sensitive to adversarial attacks, which also
raises ethical concerns about the reliability and security of the
AI system in patient care.
C. Limitation and Future Work
Through our experiments and results, we demonstrate the
potential of AutoKAN as a smart anomaly detection device
with the capability for large-scale deployment at a reasonable
cost. However, all testing in this study was conducted through
simulations, lacking real-device evaluations to validate its
performance in practical applications. In the future, we plan
to develop a smart device for anomaly detection using sensor
signals to monitor diabetes patients in hospitals. Furthermore,
evaluating the proposed approach on a larger and more diverse
scale, encompassing approximately 50 to 100 devices deployed
across multiple hospital wards, particularly in challenging nonIID scenarios with varying patient demographics and sensor
noise profiles, would provide a more robust demonstration of
its performance and generalizability in real-life applications.
This expanded evaluation would also allow us to assess the
system’s scalability and its ability to handle the complexities of
a real hospital environment, including network latency and data
synchronization issues. One key reason we chose Kolmogorov–
Arnold Networks (KAN) over traditional black-box neural
networks is their inherent explainability. As a next step, we aim

to further explore and refine explainable AI (XAI) approaches
to interpret our model’s decision-making process with greater
granularity. This will involve not only identifying which input
features are most influential in the model’s predictions but also
quantifying the uncertainty associated with those predictions
and providing clinicians with actionable insights into the
factors contributing to each anomaly detection. This enhanced
explainability will help build trust and facilitate adoption
among users, such as hospitals and IT administrators, ensuring
transparency, reliability, and clinical utility in real-world
applications. Additionally, the AutoKAN federated learning
model is indeed designed to preserve data privacy by ensuring
patient data remains decentralized and is not transmitted to a
central server. This fundamental architectural choice inherently
supports privacy preservation, which is a key tenet of regulations
like HIPAA and GDPR. While the current study lays this
strong privacy-preserving foundation, future work will focus
on explicitly demonstrating compliance with such stringent
healthcare regulations.
VII. C ONCLUSION
In this study, we introduce AutoKAN, an anomaly detection model integrated with a federated learning mechanism.
AutoKAN outperforms over 28 state-of-the-art anomaly detection models, achieving an impressive 99% accuracy and
100% precision. Additionally, it demonstrates its capability to
function efficiently in resource-constrained environments with
limited computational resources. By integrating Kolmogorov–
Arnold Networks (KAN) into the autoencoder architecture,
AutoKAN serves as a lightweight and faster alternative to
traditional neural networks. Additionally, the adaptive threshold strategy has shown its effectiveness through experimental
results. In conclusion, the proposed framework holds significant application value in medical anomaly detection and has
the potential to be extended to other fields requiring efficient
and accurate anomaly detection.
R EFERENCES
[1] “Diabetes.” who.int. Accessed: Mar. 3, 2025. [Online]. Available: https://
www.who.int/news-room/fact-sheets/detail/diabetes

11314

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

[2] M. S. Farooq, S. Riaz, R. Tehseen, U. Farooq, and K. Saleem, “Role of
internet of things in diabetes healthcare: Network infrastructure, taxonomy, challenges, and security model,” Digit. health, vol. 9, Jun. 2023,
Art. no. 20552076231179056.
[3] M. Abououf, S. Singh, R. Mizouni, and H. Otrok, “Explainable AI for
event and anomaly detection and classification in healthcare monitoring
systems,” IEEE Internet Things J., vol. 11, no. 2, pp. 3446–3457,
Jan. 2024.
[4] D. L. Aguilar, M. A. Medina-Pérez, O. Loyola-Gonzalez,
K.-K. R. Choo, and E. Bucheli-Susarrey, “Towards an interpretable
autoencoder: A decision-tree-based autoencoder and its application in
anomaly detection,” IEEE Trans. Depend. Secure Comput., vol. 20,
no. 2, pp. 1048–1059, Mar./Apr. 2023.
[5] Z. Li and X. Zhang, “An enhanced autoencoder-based anomaly detection model for time series data from wearable medical devices,”
IEEE J. Biomed. Health Inform., early access, Aug. 20, 2024,
doi: 10.1109/JBHI.2024.3434420.
[6] A. Abusitta, G. H. de Carvalho, O. A. Wahab, T. Halabi, B. C. Fung,
and S. Al Mamoori, “Deep learning-enabled anomaly detection for IoT
systems,” Internet Things, vol. 21, Apr. 2023, Art. no. 100656.
[7] M. A. Rassam, “Autoencoder-based neural network model for anomaly
detection in wireless body area networks,” IoT, vol. 5, no. 4,
pp. 852–870, 2024.
[8] H. Gao, B. Qiu, R. J. D. Barroso, W. Hussain, Y. Xu, and X. Wang,
“Tsmae: A novel anomaly detection approach for internet of things time
series data using memory-augmented autoencoder,” IEEE Trans. Netw.
Sci. Eng., vol. 10, no. 5, pp. 2978–2990, Sep./Oct. 2023.
[9] J. Fan et al., “LUAD: A lightweight unsupervised anomaly detection
scheme for multivariate time series data,” Neurocomputing, vol. 557,
Nov. 2023, Art. no. 126644.
[10] M. Gu et al., “A lightweight convolutional neural network hardware
implementation for wearable heart rate anomaly detection,” Comput.
Biol. Med., vol. 155, Mar. 2023, Art. no. 106623.
[11] C. Li, L. Qi, and X. Geng, “A sam-guided two-stream lightweight model
for anomaly detection,” ACM Trans. Multimedia Comput., Commun.
Appl., vol. 21, no. 2, pp. 1–23, 2025.
[12] V. Goyal, A. Yadav, S. Kumar, and R. Mukherjee, “Lightweight LAE for
anomaly detection with sound-based architecture in smart poultry farm,”
IEEE Internet Things J., vol. 11, no. 5, pp. 8199–8209, Mar. 2024.
[13] M. Abd Elaziz, I. A. Fares, and A. O. Aseeri, “CKAN: Convolutional
Kolmogorov–Arnold networks model for intrusion detection in IoT
environment,” IEEE Access, vol. 12, pp. 134837–134851, 2024.
[14] P. Vijai and P. B. Sivakumar, “Anomaly detection solutions: The dynamic
loss approach in VAE for manufacturing and IoT environment,” Results
Eng., vol. 25, Mar. 2025, Art. no. 104277.
[15] H. Guo, Z. Zhou, D. Zhao, and W. Gaaloul, “EGNN: Energy-efficient
anomaly detection for IoT multivariate time series data using graph
neural network,” Future Gener. Comput. Syst., vol. 151, pp. 45–56,
Feb. 2024.
[16] G. Sivapalan, K. K. Nundy, A. James, B. Cardiff, and D. John,
“Interpretable rule mining for real-time ECG anomaly detection
in IoT edge sensors,” IEEE Internet Things J., vol. 10, no. 15,
pp. 13095–13108, Aug. 2023.
[17] D. Breitenbacher, I. Homoliak, Y. L. Aung, Y. Elovici, and
N. O. Tippenhauer, “HADES-IoT: A practical and effective host-based
anomaly detection system for IoT devices (extended version),” IEEE
Internet Things J., vol. 9, no. 12, pp. 9640–9658, Jun. 2022.
[18] L. Fang, Y. Li, Z. Liu, C. Yin, M. Li, and Z. J. Cao, “A practical model
based on anomaly detection for protecting medical IoT control services
against external attacks,” IEEE Trans. Ind. Informat., vol. 17, no. 6,
pp. 4260–4269, Jun. 2021.
[19] A. Albattah and M. A. Rassam, “A correlation-based anomaly detection
model for wireless body area networks using convolutional long shortterm memory neural network,” Sensors, vol. 22, no. 5, p. 1951, 2022.
[20] K. Balaji, S. S. Kumar, D. Vivek, S. P. K. Deepak, K. D. Sagar, and
S. T. Khan, “An effective deep learning-based intrusion detection system
for the Healthcare environment,” Int. J. Comput. Intell. Appl., vol. 24,
no. 1, 2024, Art. no. 2450033.
[21] H. Elayan, M. Aloqaily, and M. Guizani, “Sustainability of Healthcare
data analysis IoT-based systems using deep federated learning,” IEEE
Internet Things J., vol. 9, no. 10, pp. 7338–7346, May 2022.
[22] M. Akter, N. Moustafa, T. Lynar, and I. Razzak, “Edge intelligence:
Federated learning-based privacy protection framework for smart healthcare systems,” IEEE J. Biomed. Health Inform., vol. 26, no. 12,
pp. 5805–5816, Dec. 2022.

[23] S. Sai, V. Hassija, V. Chamola, and M. Guizani, “Federated learning
and NFT-based privacy-preserving medical-data-sharing scheme for
intelligent diagnosis in smart healthcare,” IEEE Internet Things J.,
vol. 11, no. 4, pp. 5568–5577, Feb. 2024.
[24] H. Lin, K. Kaur, X. Wang, G. Kaddoum, J. Hu, and M. M. Hassan,
“Privacy-aware access control in IoT-enabled healthcare: A federated
deep learning approach,” IEEE Internet Things J., vol. 10, no. 4,
pp. 2893–2902, Feb. 2023.
[25] B. Li, W. Gao, J. Xie, H. Li, and M. Gong, “A unified framework
for federated semi-supervised learning in heterogeneous IoT Healthcare
systems,” IEEE Internet Things J., vol. 11, no. 24, pp. 41110–41123,
Dec. 2024.
[26] G.-Q. Zeng, Y.-W. Yang, K.-D. Lu, G.-G. Geng, and J. Weng,
“Evolutionary adversarial autoencoder for unsupervised anomaly detection of Industrial Internet of Things,” IEEE Trans. Rel., early access,
Jan. 27, 2025, doi: 10.1109/TR.2025.3528256.
[27] A. Katbi and R. Ksantini, “One-class IoT anomaly detection system
using an improved interpolated deep SVDD autoencoder with adversarial
regularizer,” Digit. Signal Process., vol. 162, Jul. 2025, Art. no. 105153.
[28] L. Tang et al., “Online anomaly detection in industrial IoT networks
using a supervised contrastive learning-based spatiotemporal variational
autoencoder,” IEEE Internet Things J., vol. 12, no. 11, pp. 17399–17412,
Jun. 2025.
[29] B. Xu, J. Wang, Z. Zhao, H. Lin, and F. Xia, “Unsupervised anomaly
detection on attributed networks with graph contrastive learning for
consumer electronics security,” IEEE Trans. Consum. Electron., vol. 70,
no. 1, pp. 4062–4072, Feb. 2024.
[30] G. ALMahadin et al., “VANET network traffic anomaly detection using
GRU-based deep learning model,” IEEE Trans. Consum. Electron.,
vol. 70, no. 1, pp. 4548–4555, Feb. 2024.
[31] N. Nissar, N. Naja, and A. Jamali, “Securing VANETs: Multi-objective
intrusion detection with variational autoencoders,” IEEE Trans. Consum.
Electron., vol. 70, no. 1, pp. 3867–3874, Feb. 2024.
[32] H. Zhao, M. Liu, S. Qiu, and X. Cao, “Satellite unsupervised
anomaly detection based on deconvolution-reconstructed temporal convolutional autoencoder,” IEEE Trans. Consum. Electron., vol. 70, no. 1,
pp. 2989–2998, Feb. 2024.
[33] U. Zukaib, X. Cui, C. Zheng, M. Hassan, and Z. Shen, “Meta-IDS:
Meta-learning-based smart intrusion detection system for Internet of
Medical Things (IoMT) network,” IEEE Internet Things J., vol. 11,
no. 13, pp. 23080–23095, Jul. 2024.
[34] J. A. Shaikh et al., “RCLNet: An effective anomaly-based intrusion
detection for securing the IoMT system,” Front. Digit. Health, vol. 6,
Oct. 2024, Art. no. 1467241.
[35] R. Wang, H. Qiu, X. Cheng, and X. Liu, “Anomaly detection with a
container-based stream processing framework for Industrial Internet of
Things,” J. Ind. Inf. Integr., vol. 35, Oct. 2023, Art. no. 100507.
[36] H. Zahan, M. W. Al Azad, I. Ali, and S. Mastorakis, “IoT-AD: A
framework to detect anomalies among interconnected IoT devices,”
IEEE Internet Things J., vol. 11, no. 1, pp. 478–489, Jan. 2024.
[37] S. T. Seydi, M. Sadegh, and J. Chanussot, “Kolmogorov-Arnold network
for hyperspectral change detection,” IEEE Trans. Geosci. Remote Sens.,
vol. 63, Feb. 2025, Art. no. 5505515.
[38] B. Jiang, Y. Wang, Q. Wang, and H. Geng, “A novel interpretable shortterm load forecasting method based on Kolmogorov-Arnold networks,”
IEEE Trans. Power Syst., vol. 40, no. 1, pp. 1180–1183, Jan. 2025.
[39] M. Liu, F. Bossmann, and J. Ma, “Kolmogorov-Arnold networks for
semi-supervised impedance inversion,” IEEE Geosci. Remote Sens. Lett.,
vol. 22, Jan. 2025, Art. no. 7503205.
[40] Y. Song, H. Zhang, J. Man, X. Jin, and Q. Li, “AWKNet: A
lightweight neural network for motor imagery electroencephalogram
classification based on adaptive wavelet transform Kolmogorov–Arnold,”
IEEE Trans. Consum. Electron., vol. 71, no. 1, pp. 1219–1234,
Feb. 2025.
[41] P. H. Do, T. D. Le, T. D. Dinh et al., “Classifying IoT Botnet attacks with
Kolmogorov-Arnold networks: A comparative analysis of architectural
variations,” IEEE Access, vol. 13, pp. 16072–16093, 2025.
[42] S. Ghazanfar, F. Hussain, A. U. Rehman, U. U. Fayyaz, F. Shahzad,
and G. A. Shah, “IoT-flock: An open-source framework for IoT traffic
generation,” in Proc. Int. Conf. Emerg. Trends Smart Technol. (ICETST),
2020, pp. 1–6.
[43] F. Hussain et al., “A framework for malicious traffic detection in IoT
healthcare environment,” Sensors, vol. 21, no. 9, p. 3025, 2021.
[44] Y. Zhao, Z. Nasrullah, and Z. Li, “PyOD: A Python toolbox for scalable
outlier detection,” J. Mach. Learn. Res., vol. 20, no. 96, pp. 1–7, 2019.
PAPER_TEXT
