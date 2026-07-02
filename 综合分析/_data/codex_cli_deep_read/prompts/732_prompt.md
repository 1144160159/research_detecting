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
# [732] LSTM-1DResNet: An Intrusion Detection Model for Connected and Autonomous Vehicles Based on Deep Learning
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
编号：732
题名：LSTM-1DResNet: An Intrusion Detection Model for Connected and Autonomous Vehicles Based on Deep Learning
年份：2026
DOI：10.1109/tvt.2026.3663771
来源：IEEE Transactions on Vehicular Technology
PDF：paper/10.1109_TVT.2026.3663771.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、其他AI安全与跨域异常检测
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\732.txt
- 原始字符数：68360
- 本次发送字符数：68360
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

1

LSTM-1DResNet: An Intrusion Detection Model
for Connected and Autonomous Vehicles Based on
Deep Learning
Qiyi He, Yifan Zhang, Ao Xu, Zhiwei Ye, Wen Zhou, Qiao Lin, Tingting Zhang

Abstract—Connected and Autonomous Vehicles (CAVs) are
pivotal for enabling intelligent mobility and autonomous driving,
yet their inherent connectivity exposes critical vulnerabilities to
cyber-attacks, which can precipitate life-threatening accidents,
privacy breaches, and systemic failures in transportation networks. Given the escalating deployment of CAVs, ensuring robust
cybersecurity is not merely a technical challenge but an urgent
safety imperative. Traditional machine learning algorithms, such
as Decision Trees (DT) and Support Vector Machines (SVM), often suffer from inadequate feature extraction in high-dimensional
network traffic data, significantly compromising the accuracy
of cyber-attack identification. Deep learning has emerged as a
mainstream solution for Intrusion Detection Systems (IDS) due to
its proficiency in handling complex data and automating feature
extraction. To address these challenges, we propose LSTM1DResNet, a novel deep learning-based intrusion detection model
comprising an autoencoder and a classifier. The autoencoder
innovatively integrates a Long Short-Term Memory Network
(LSTM) with a one-dimensional convolutional residual module
(Conv1D ResNet), substantially enhancing spatiotemporal feature
extraction capabilities for high-dimensional traffic data. The
classifier employs a Multilayer Perceptron (MLP) to deliver
precise attack classification. The model was evaluated on both
the NSL-KDD and CICIDS2017 datasets. On NSL-KDD, LSTM1DResNet achieved 94.38% accuracy, outperforming standalone
CNN and LSTM models by 11%. On CICIDS2017, it achieved
97.98% accuracy, precision of 98.11%, and recall of 97.98%,
alongside high F1-scores(96.90%). This dual-dataset validation
demonstrates the model’s strong potential for enhancing intrusion
detection in CAV-related contexts, particularly in addressing
high-dimensional feature extraction challenges.
Index Terms—Connected and Autonomous Vehicles, Deep
learning, Long Short-Term Memory, Residual Network, Intrusion
detection systems.

I. I NTRODUCTION

Qiyi He is with the School of Computer Science, Hubei University of
Technology, Wuhan, Hubei, 430068 China e-mail:(qiyi.he@hbut.edu.cn).
Yifan Zhang is with the School of Computer Science, Hubei
University of Technology, Wuhan, Hubei, 430068 China email:(zhangyifan hbut@hbut.edu.cn).
Ao Xu is with the School of Computer Science, Hubei University of
Technology, Wuhan, Hubei, 430068 China e-mail:(102211178@hbut.edu.cn).
Zhiwei Ye is with the School of Computer Science, Hubei University of
Technology, Wuhan, Hubei, 430068 China e-mail:(hgcsyzw@hbut.edu.cn).
Wen Zhou is with the School of Computer Science, Hubei University of
Technology, Wuhan, Hubei, 430068 China e-mail:(zw mmwh@hbut.edu.cn).
Qiao Lin is with the School of Computer Science, University of Nottingham
Ningbo China, Ningbo, 315100 China e-mail:(qiao.lin@nottingham.edu.cn).
Tingting Zhang is with the School of Computer Science,
Hubei University of Technology, Wuhan, Hubei, 430068 China email:(tingtingzhang0114@163.com).

AVS are deeply integrated with the external environment
through in-vehicle networks, enabling vehicles to share
information about their attributes and dynamic information,
such as location, speed and driving status, with the Internet.
In this way, a high level of information interaction and sharing
can be achieved between vehicle and vehicle, vehicle and road,
vehicle and human, and vehicle and cloud services. CAVs are
developing rapidly due to advances in 4G/5G communication
technologies, cellular networks and Bluetooth, as well as the
emergence of IoT and big data technologies, further advancing
smart mobility applications such as autonomous driving, traffic
management and personalised information services [1]. With
the development of CAVs, the network data received by
vehicles grows exponentially, the network behaviour becomes
more complex, and the traditional cybersecurity system gradually fails to meet the demand. Cyber-attacks do not only
affect the quality of personalised information services.2020
Tencent Cohen Labs published a Lexus car security report [2],
which states that an attacker can exploit security issues with
the in-vehicle Bluetooth and diagnostic functions to wirelessly
control the car to perform a number of unintended physical
operations. This suggests that if an attacker gains control of a
vehicle, it would also pose a significant threat to the safety
of the driver and passengers. Network Intrusion Detection
System (IDS) is a widely used protection technology in the
field of network security that enhances the security of a
system by monitoring network behaviour to identify malicious
or unauthorised actions [3]. Identifying abnormal network
behaviour through network intrusion detection is the key to
ensure network security and reliability and is an important
aspect of the future development of CAVs [4].
Network intrusion detection systems can be categorized
into two main types: signature-based and anomaly-based.
Signature-based network intrusion detection systems (SIDS)
can detect network traffic in real time and identify known
network attacks efficiently and accurately. However, SIDS
are based on predefined signature libraries whose validity is
limited by their timeliness, and SIDS have inherent limitations
in detecting unknown threats. Therefore, ensuring the continued effectiveness of the system requires regular maintenance
and updating of the signature libraries [5]. Anomaly-based
network intrusion detection system (AIDS) identifies intrusion
attacks by analyzing the characteristics of network behaviors
and still has the ability to protect against unknown attacks.
Compared to SIDS, AIDS does not rely on a feature library
and is more adaptable and flexible [6]. In the design of

C

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

AIDS, machine learning (ML) is widely used, such as DT
and SVM techniques, to classify normal and abnormal samples
by manually extracting features. However, these methods may
negatively affect the protection performance of CAVs due to
the increased difficulty of feature processing when facing massive and high-dimensional data. Deep learning (DL) is more
adept at handling massive high-dimensional data because of
its automatic feature extraction capability, and DL has shown
excellent performance in natural language processing (NLP)
and computer vision (CV), and is gradually being widely used
in AIDS design. Deep learning techniques can extract potential
data features in network data to identify network attack behaviors, so DL-based intrusion detection models need to have
strong feature extraction capabilities. Currently, many studies
have used models such as Convolutional Neural Networks
(CNN) [7], Autoencoder (AE) [8], Recurrent Neural Networks
(RNN) [9], Long Short-Term Memory Networks (LSTM)
[10], Generative Adversarial Networks (GAN) [11], and Deep
Belief Networks (DBN) [12] to implement CAV intrusion detection. However, existing deep learning-based IDSs continue
to face significant challenges in CAV networks. CAV network
traffic constitutes high-dimensional structured data wherein
individual traffic samples exhibit dynamic sequential field
dependencies (e.g., temporal logic in protocol headers) and
fine-grained feature coupling (e.g., anomalous payload patterns), causing substantial overlap between benign behavioral
mutations (e.g., transient sensor perturbations) and malicious
attacks in the feature space. Current single-model approaches
fail to effectively decouple long-range sequential dependencies
from deep spatial features: convolutional neural networks
(CNNs) capture local spatial patterns but neglect long-distance
field dependencies (e.g., cross-protocol-layer anomalies); long
short-term memory networks (LSTMs) model sequential relationships yet suffer from high-dimensional feature degradation
during recursive propagation. Furthermore, CAVs’ real-time
operational constraints necessitate low-latency inference with
uncompromised accuracy, yet existing methods consistently
struggle with the trade-off dilemma between deep feature
extraction and computational efficiency, thereby failing to
simultaneously achieve robustness and adaptability in complex vehicular networks. Consequently, a mechanism that
synergistically optimizes sequential modeling and deep feature
extraction is required to enhance feature discriminability while
maintaining computational efficiency.
To address the above problems, this paper proposes a deep
learning-based LSTM-1DResNet intrusion detection model.
Given the characteristics of CAVs network traffic, which
include high dimensionality, temporal dependency, and finegrained feature coupling, the model employs a cascaded feature extraction architecture: first, a LSTM module is used to
capture long-range temporal dependencies across fields in the
data stream, effectively modeling the dynamic logic between
protocol layers; The output is then fed into a one-dimensional
convolutional residual network (1DResNet), which uses multilayer convolutional operations to decouple and enhance deep
spatial features. The residual connection mechanism helps
mitigate the vanishing gradient problem in deep networks
while maintaining low computational overhead, meeting the

2

real-time requirements of in-vehicle systems. Finally, the
extracted high-level features are analyzed by a multi-layer
perceptron (MLP) classifier to predict the attack category.
Experimental results on the NSL-KDD dataset show that the
proposed model achieves approximately 11% better detection
performance compared to independent CNN and LSTM models. On the CICIDS2017 dataset, which better aligns with
CAVs network environments, the model also demonstrates
excellent detection performance (accuracy of 97.98%, F1 score
of 96.90%), preliminarily validating its adaptability in diverse
network environments. The main contributions of this paper
are as follows:
(1) This paper proposes a deep learning framework called
LSTM-1DResNet, which combines LSTM with a 1DResNet
for intrusion detection in CAVs scenarios. The model uses
LSTM modules to capture long-term dependencies between
fields in network traffic and further extracts high-dimensional
spatial features using residual modules built on Conv1D. Compared with traditional convolutional structures, this approach
enhances feature expression capabilities and model training
stability to a certain extent.
(2) The feature extraction sequence of this article is to first
perform sequence modelling, then deep extraction, placing the
Conv1D residual module after the LSTM. This design aims to
preserve the integrity of the original data’s temporal structure
and avoid the potential interference of convolution operations
on sequence information, thereby more effectively achieving
the staged decoupling and fusion of spatio-temporal features.
(3) The model was evaluated on two public datasets: NSLKDD and CICIDS2017. The experimental results show that
the proposed model achieves an accuracy rate of 94.38% on
NSL-KDD and an accuracy rate of 97.98%, a precision rate of
98.11%, a recall rate of 97.98%, and an F1 score of 96.90%
on CICIDS2017, verifying its feasibility and effectiveness in
processing high-dimensional network traffic data.
The rest of the paper is structured as follows: the second
section introduces the related research work; the third section
describes in detail the structure of the LSTM-1DResNet model
and the roles of each module; the fourth section describes the
dataset used in the experiments, the experimental setup, and
the experimental results, and analyzes the experimental results;
and the fifth section summarizes the work of the paper.
II. R ELATE W ORK
Many ML methods have been applied in IDS design, such
as SVM [13-14], K-Nearest Neighbor (KNN) [15-16], and
Random Forest (RF) [17]. However, these methods have high
complexity of feature extraction for certain massive and highdimensional data, which may lead to higher false alarm rate
of IDS and lower detection rate of cyber-attacks.Kim et al
[18] proposed an intrusion detection system using Genetic
Algorithm (GA) to optimize SVM. In this study, GA is
combined with SVM to improve the overall efficiency of SVM
based IDS. This fusion approach helps in determining the
“best detection model” for the SVM classifier and selecting
the “best parameters” for the SVM. On the other hand, Panda
et al [19] used Naive Bayes (NB) algorithm in their study

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

3

TABLE I
S UMMARY OF EXISTING INTRUSION DETECTION METHODS AND THEIR LIMITATIONS

Method

Key Limitations

Dataset

Accuracy

SVM [13]

- Limited handling of high-dimensional network
traffic
- Models struggle to adapt to the rapid evolution of
new types of cyber attacks

KDDCUP’99

89.85%

KNN [15]

- Computationally expensive for real-time detection
- Sensitive to hyperparameter selection

NSL-KDD

98.87%

Naive Bayes [19]

- The assumption of feature independence of Naive
Bayes deviates from the complex correlation of
actual network traffic
- High-dimensional data processing is inefficient
and cannot meet the performance requirements of
real-time intrusion detection

KDDCUP’99 (10%)

96.00%

LSTM [36]

- The false alarm rate is relatively high, which may
generate a large number of false alarms in actual
deployment and affect system availability

CSE-CIC-IDS2018

99.97%

CNN [37]

- Limited temporal feature extraction
- SMOTE introduces synthetic artifacts

AWID

94.00%

CNN-LSTM [38]

- Distributed processing relying on the Apache
Spark framework may face challenges in terms of
computing resources and real-time performance on
resource-constrained in-vehicle devices

NSL-KDD

99.70%

LSTM-CNN [44]

- The model is highly complex and requires
significant computing resources, which may pose
challenges in balancing performance and efficiency
during actual deployment

NSL-KDD
UNSW-NB15
CICIDS-2018

95.70%
94.90%
96.70%

to address anomaly detection challenges and evaluated it on
KDD Cup dataset. The results show that the NB algorithm
exhibits superior performance in terms of maintaining a lower
false alarm rate and operational time cost compared to many
existing IDS schemes.
Based on the existing research, further exploration also
involves the development and application of multiple parallel
and hybrid categorization strategies. Yang et al [20] proposed
a novel integrated IDS framework called Leader Category and
Confidence Decision Integration (LCCDE). The framework is
constructed by selecting the best performing model from three
state-of-the-art machine learning algorithms (XGBoost, LightGBM, and CatBoost) for each category or attack type. These
categorical leadership models and their predictive confidence
values are then utilized to accurately identify various types of
cyber attacks. Experiments show that the proposed LCCDE
framework can be effectively applied to intrusion detection in
both in-vehicle and external networks.
Traditional machine learning algorithms have demonstrated
a certain degree of effectiveness in identifying cybersecurity
threats, with detection accuracy that meets basic requirements under specific conditions. However, as CAVs become
increasingly widespread, the dynamic and complex nature
of network environments has significantly intensified. The
limitations of traditional machine learning methods in feature
processing capabilities have become increasingly apparent,
particularly when dealing with high-dimensional, unstructured

data. Their detection accuracy is easily affected by changes
in the environment, and controlling false positive rates poses
significant challenges. Therefore, to adapt to the complex
network environment of CAVs, it is necessary to further optimise the performance of IDS to improve detection accuracy
and reduce false positive rates. This research direction has
been preliminarily argued in relevant literature [21-22]. In this
context, enhancing the feature extraction capabilities of models
is considered one of the key paths to improving the protective
effectiveness of IDS.
DL has provided feasible solutions for NLP [23-25], CV
[26-27], and speech recognition [28-30] and other fields,
thanks to the core neural network (NN) technology of DL,
which has the ability to perform hierarchical representation
and feature learning, as well as process high-dimensional data
and extract effective information. Therefore, DL has significant
advantages when dealing with high-dimensional and timeseries network traffic data. Specifically, deep learning models can automatically extract multi-level features from highdimensional raw network traffic, effectively reducing reliance
on manual feature engineering, and capturing complex nonlinear attack patterns. Additionally, it supports joint modelling
of spatio-temporal features, enabling the simultaneous capture
of local spatial anomalies within packet payloads and longrange temporal dependencies across packets, thereby providing
a more comprehensive understanding of attack behaviour. This
capability endows the model with robust nonlinear fitting and

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

generalisation performance, enabling it not only to accurately
identify known attacks but also to discover unknown or variant
attacks with limited training data, significantly enhancing the
adaptability and robustness of intrusion detection systems in
addressing new network threats [41]. Early studies attempted
to combine shallow learning and deep learning techniques
[31]. For example, [32] proposed an information entropy-based
deep belief network model (IE-DBN), which uses information
gain (IG) to reduce the dimensionality of high-dimensional
data features to eliminate redundant features, and determines
the number of hidden layer neurons and network depth of
the DBN network based on information entropy, thereby
optimising the model structure. Anzer et al. employed a multilayer perceptron (MLP) neural network to detect abnormal
behaviour in internet environments. Their research results
were presented in the form of predicted outputs, classification
reports, and confusion matrices. Simulation analyses indicated
that this method has a certain degree of effectiveness under
specific conditions [33].
In addition, deep learning models such as LSTM [34] and
CNN [35] have gradually been applied in intrusion detection
research. LSTM is used to mitigate the vanishing gradient
and exploding gradient phenomena that traditional recurrent
neural networks (RNNs) may encounter when processing longterm dependencies, thereby improving their ability to learn
from long sequence data to a certain extent. CNNs demonstrate certain applicability in local feature capture and pattern
recognition. For example, [36] adopted a network intrusion
detection system (WNIDS) model based on a bidirectional
long short-term memory network (BiLSTM), which demonstrated certain detection capabilities for network intrusion
behaviour under specific experimental conditions. Research
by [37] designed a network architecture that integrates CNN
into the data processing layer and combines synthetic minority
class oversampling technique (SMOTE) to optimise the data
processing workflow, aiming to enhance the stability of the
learning process. During the testing phase, a nearest neighbour
classifier is used to identify new attack types. Experimental
results based on the AWID dataset indicate that the model
demonstrates certain detection accuracy advantages over SVM
and RF methods under specific scenarios.To build a more
adaptive IDS, combining LSTM and CNN methods is one
of the directions that researchers are exploring. For example,
Alferaidi et al. [38] proposed an intrusion detection model
for vehicle networks (AA distributed combined deep learning
model) based on the Apache Spark distributed computing
framework. This model integrates CNN and LSTM to extract and analyse features from large-scale data, aiding in
the identification of intrusion behaviour and monitoring of
abnormal activities. Sun et al. [40] proposed a CNN-LSTM
model with attention mechanism (CLAM), which uses onedimensional convolution (Conv1D) to extract signal features
at time nodes and inputs them into a bidirectional LSTM
to capture temporal dependencies; the attention mechanism
calculates the weight distribution of the bidirectional LSTM
hidden states and performs weighted focusing on key time
steps. Experimental analysis indicates that this method may
help accelerate model convergence and improve prediction

4

accuracy under specific conditions. Xue et al. [44] proposed
the HAE-HRL model, which combines a hybrid autoencoder
(HAE) for feature selection and designs a residual networkbased LSTM-CNN hybrid classifier (HRL), achieving highperformance detection on multiple datasets such as NSLKDD, UNSW-NB15, and CIC-IDS-2018 datasets, highlighting
the synergistic value of feature optimisation and deep hybrid
architectures.
Existing research has demonstrated that the combination
of LSTM and CNN can effectively identify network attack
behaviour(Table I). This hybrid architecture combines the spatial feature extraction capabilities of CNN with the temporal
modelling capabilities of LSTM, providing intrusion detection
systems with a more comprehensive feature representation.
The proposed LSTM-1DResNet model adopts a ‘sequencefirst, spatial-second’ feature extraction order: first, the LSTM
module processes the input data to fully capture the longrange temporal dependencies across fields in network traffic;
subsequently, 1DResNet is used for deep feature decoupling,
where Conv1D replaces traditional Conv2D to more efficiently
process one-dimensional network traffic data. This design
choice is based on an analysis of the characteristics of CAVs
network traffic. Placing the LSTM at the front end ensures
the integrity of the temporal structure of the raw data and
avoids potential interference with sequence information caused
by convolution operations in the early stages, thereby more
effectively achieving the staged decoupling and fusion of
spatio-temporal features [45]. Additionally, the introduction
of residual modules not only enhances feature extraction
capabilities but also improves model training stability through
a skip connection mechanism.
III. M ODEL
The LSTM-1DResNet intrusion detection model proposed
in this paper, aimed at detecting cyber-attacks on CAVs,
comprises autoencoder and classifiers, with its architecture depicted in Fig.1. The principal objective of securing the network
within the CAV environment is the identification of cyberattack behaviors; consequently, the LSTM-1DResNet model
is configured as a binary classification model. This section
introduces the LSTM and residual module components utilized
by LSTM-1DResNet and provides a detailed exposition of the
LSTM-1DResNet model.
A. Long-term Memory Network
LSTM is a modified RNN method designed to alleviate the
gradient explosion and vanishing problems. Traditional RNNs
suffer from the vanishing gradient problem, which hinders the
modelling of long-term dependencies. LSTMs introduce gated
memory units to retain key temporal features. Specifically,
the forget gate regulates the retention of information from
previous states, the input gate controls the integration of new
features, and the output gate determines state propagation,
thereby jointly achieving the persistent storage of attackrelated patterns across extended sequences.The structure of the
LSTM cell is shown in Fig.4.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

5

Residual block

LSTM Layer
1x1
Convolution1D

1x3
Convolution1D

LSTM
unit

LSTM
unit

LSTM
unit

LSTM
unit

LSTM
unit

LSTM
unit

LSTM
unit

LSTM
unit

Input

1x3
Convolution1D

LSTM
unit

Max-Pool
1x1
Convolution1D

Output

FC

1x3
Convolution1D

1x3
Convolution1D

Residual block

Classifiers

Fig. 1. Structure of LSTM-1DResNet.

The key function of LSTM is to record long-term information. The forgetting gate controls the selective forgetting of
information in the cell state, the input gate selectively adds new
information to the cell state, and the output gate selectively
outputs information. At time point t, the LSTM cell processes
the cell state Ct −1 at the previous time point t−1 through the
forgetting gate, input gate and output gate, and then generates
the cell state Ct at the current time point t and passes Ct to
the next cell.
LSTM excels in extracting long-distance dependency features. Through its gating mechanism, LSTM is able to effectively capture and maintain long term dependencies in
sequential data and thus extract key features, which is crucial
for accurately identifying complex network attack patterns.
By retaining key features in sequence data, LSTM is able
to effectively distinguish data with attack behaviours, thus
improving the detection performance of intrusion detection
systems.
B. 1DResNet
In deep learning, increasing the number of hidden layers is a simple and effective method for improving model
performance. However, with the increase in the number of
hidden layers, the problem of gradient vanishing or gradient
explosion is prone to occur, and even model degradation

can occur. The residual network (ResNet) [46] proposed by
He Kaiming’s team in 2015 innovatively introduces shortcut
connections to skip one or more layers, transforming the
′
′
f (x) = x − x1 problem into the x = f (x) + x1 problem,
which effectively alleviates these problems. Fig.2(a) shows the
residual structure more visually. Inspired by ResNet, in this
paper, the convolutional layer using Conv2D is replaced by
the convolutional layer using Conv1D, and a 1x1 convolutional
layer is added to the shortcut connection (shown in Fig.2(b)),
where the 1x1 convolution serves to adjust the number of
channels of the input to match the output of the convolutional
layer.
The advantage of using 1D convolution(Fig.3(b)) instead
of 2D convolution(Fig.3(a)) is that 1D convolution is more
suitable for processing one-dimensional sequence data and
can extract local features in sequence data more efficiently.
Compared with 2D convolution, 1D convolution is also more
efficient in terms of computational complexity and resource
consumption. Especially when dealing with large-scale 1D
data, it can improve the running speed and processing capability of the model.
In the LSTM-1DResNet proposed in this paper, it uses
LSTM to extract long-range dependent features, uses the
residual module to further extract data features, and it mitigates
the risk of overfitting and improves the depth and stability

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

6

1x3Conv1D

3x3Conv2D

1x1Conv1D

3x3Conv2D

1x3Conv1D

( )

( )
+

+

’

’
（a）

（b）

Fig. 2. (a)Residual block in ResNet, (b)Residual block in LSTM-1DResNet.

1x3Conv1D

3x3Conv2D

Input data

Output data

（a）

Input data

Output data

（b）

Fig. 3. Structure of LSTM-1DResNet.

of the model. The residual module alleviates the degradation
problem of deep networks through identity shortcuts, reconstructing layer learning as residual functions. This mechanism
maintains representation capabilities while preserving gradient
flow during backpropagation, which is particularly critical
for hierarchical extraction of multi-scale attack features in
intrusion detection.

where length is the length of a single piece of data, and
channels is the number of channels in the data, which is set
to 1 by default.After this processing, the data flows to the
LSTM layer, capturing the sequential dependencies between
different feature dimensions in the data. After processing by
the LSTM layer, the output of the last time step of each
sequence is selected to form a new output data dimension
(batchsize, length).

C. LSTM-1DResNet

Then, the data output from the LSTM is reconstructed into
(batchsize, channels, length) after which it is fed into the
residual layer to further extract data features. The residual
layer consists of two residual modules, each with the same
structure(Fig.2(b)). The backbone of the residual module

As shown in Fig.1, the first component of the model is
composed of LSTM units. In order to adapt to the input format
of LSTM, we add a dimension to the input data x and adjust
the order of the dimensions to (batchsize, length, channels),

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

7

+

X

X
X

ℎ

ℎ

mance. In the classifier, the vectors are first converted to 32
dimensions and then further compressed to 16 dimensions,
which is a series of linear operations aimed at accurately
filtering and compressing the feature information that is crucial
to the classification task. Finally, the predictions are output
through the output layer and processed by a Sigmoid activation
function to ensure that all output values are within the range
(0,1).
IV. E XPERIMENTAL
TABLE II
C OMPOSITION OF THE NSL-KDD DATASET

Fig. 4. Structure of LSTM unit.

Input Layer

Hidden Layers

Class

Train

Percentage

Test

Percentage

Normal

67343

53.458%

9710

43.075%

DoS

45927

36.458%

7457

33.080%

Probe

11656

9.253%

2421

10.740%

R2L

995

0.790%

2754

12.217%

U2R

52

0.041%

200

0.887%

Total

125973

100%

22545

100%

Output Layer

a[1]1
a[3]2
a[1]2

X

a[3]3

a[4]

Ŷ

a[1]3

a[3]n
a[1]n

Fig. 5. Structure of MLP.

contains two convolutional layers using 1x3 convolutional
kernels, where the first layer is responsible for extracting
the base features from the raw data, and the second layer
performs feature fusion and abstraction on top of the base
features to further extract more advanced features. The fast
connectivity boosts the channel dimension of the data through
a convolutional layer using a 1x1 convolutional kernel with
the aim of matching the output of the backbone for residual
operations. In the first residual module of the residual layer,
the channel dimension of the data will be increased from 1
to 32, and then the data will be downsampled by a onedimensional maximum pooling layer. Downsampling serves to
enhance local features and reduce computational complexity.
In the second residual module, the feature dimension of the
data will be further extended to 64 and feature extraction is
completed after the data passes through the residual layer.
The output of the residual layer is converted into a one
dimensional vector using Flatten layer which is used as an
input to the classifier. The classifier is an MLP consisting of
fully connected layers(Fig.5).
As shown in Fig.5, the classifier has an inverted pyramid
structure. The inverted pyramid structure helps the network
learn the mapping from raw inputs to higher-order abstract
features by reducing the number of nodes layer by layer,
which can effectively reduce the risk of overfitting and reduce
the network complexity. It makes the model more lightweight
and efficient while maintaining good generalisation perfor-

A. NSL-KDD dataset
The NSL-KDD dataset is obtained based on the KDDcup99 dataset, which is further optimised for the KDDcup99
dataset.KDDcup99 contains a large number of redundant and
duplicate records, and the NSL-KDD dataset is very useful in removing redundant and duplicate records from the
KDDcup99 dataset.Therefore, most of the intrusion detection
researches have used NSL-KDD dataset as the training and
testing dataset. sets as training and test datasets.NSL-KDD
provides training dataset KDDTrain and test dataset KDDTest
with the number of 125,973 and 22,544, respectively.Each
data point has 41 attributes (3 nominal attributes, 6 binary
attributes, and 32 numeric attributes), which represent different
characteristics of the network flow. As well as labels indicating
the type of attack or normal behaviour. For the attack types,
there are four different attack modes:
1) Denial of Service Attack (DoS): DoS is an attack that
consumes resources by sending a large amount of traffic to a
target system so that it is unable to process legitimate network
traffic or service access;
2) Probing: In a probing attack, the attacker aims to obtain
information about the target system (e.g., scanning for ports
in use and scanning for IP addresses);
3) Remote to Local (R2L): R2L is an attack that attempts
to gain local access to a remote machine by sending spoofed
remote traffic to the target.Actions such as password guessing
and HTTP tunneling are considered R2L attacks;
4) Use of Root Users (U2R): In the case of U2R, the attacker
first gains access to the target system as an honest user and
then gains root privileges by causing system failures (e.g.,
buffer overflows and rootkits).

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

8

TABLE III
C OMPOSITION OF THE CICIDS2017 DATASET
File Name

Type of Traffic

Number of Records

Monday-WorkingHours.pcap ISCX.csv
Tuesday-WorkingHours.pcap ISCX.csv

Benign
Benign
SSH-Patator
FTP-Patator
Benign
DoS Hulk
DoS GoldenEye
DoS Slowloris
DoS Slowhttptest
Heartbleed
Benign
Web Attack-Brute Force
Web Attack-Sql Injection
Web Attack-XSS
Benign
Infiltration
Benign
Bot
Benign
Portscan
Benign
DDoS

529,918
432,074
5,897
7,938
440,031
231,073
10,293
5,796
5,499
11
168,186
1,507
21
652
288,566
36
189,067
1,966
127,537
158,930
97,718
128,027

Wednesday-WorkingHours.pcap ISCX.csv

Thursday-WorkingHours-Morning-WebAttacks.pcap ISCX.csv

Thursday-WorkingHours-Afternoon-Infiltration.pcap ISCX.csv
Friday-WorkingHours-Morning.pcap ISCX.csv
Friday-WorkingHours-Afternoon-PortScan.pcap ISCX.csv
Friday-WorkingHours-Afternoon-DDoS.pcap ISCX.csv
Total Instance/Record

Table II illustrates the entire distribution of the NSL-KDD
dataset over normal and attack categories. As can be seen
from Table 1, even though the NSL-KDD dataset is obtained
by improving the KDDcup99 dataset, there is still a large
gap in the amount of data in different attack categories.
However, when the classification conditions are set to normal
and attack types for binary classification, 53.46% of the NSLKDD dataset is normal type data and 46.54% is attack type
data, and its data distribution maintains a certain balance, so
in this paper, the NSL-KDD dataset is used to train and test
the binary classification performance of the model.

B. CICIDS2017 dataset
The CICIDS2017 dataset, released by the ISCX/CIC consortium, is a widely recognised benchmark encompassing
contemporary network traffic and attack scenarios. The MachineLearningCSV split is adopted, comprising eight trafficmonitoring sessions stored as comma-separated value (CSV)
files. The corpus contains benign traffic and 14 distinct attack categories, as summarised in Table III. CICIDS2017
provides rich flow-level attributes suitable for characterising
modern and sophisticated behaviours. For example, Subflow
Fwd Bytes and Total Length of Fwd Packets are critical for
detecting Infiltration and Bot attacks; Bwd Packet Length Std
is informative for DDoS, DoS Hulk, DoS GoldenEye, and
Heartbleed; Init Win Fwd Bytes is relevant to Web-Attack,
SSH-Patator, and FTP-Patator; while Min Bwd Packet Length
and Fwd Average Packet Length assist in recognising benign
traffic. Owing to its fidelity to real-world traffic and threat

2,830,743

characteristics, CICIDS2017 is widely adopted for evaluating
intrusion-detection methodologies.
C. Dataset preprocessing
In order for the model to better extract data features and
enhance the model prediction performance, Dataset was preprocessed before feeding the data into the model:
1) Feature Processing: Convert the feature values of character types to numerical types through unique thermal encoding, and unify the feature scales through standardization
methods to ensure that all features are in the same magnitude,
which is beneficial for model understanding and training.
2) Feature selection: A feature selection method using
recursive elimination removes redundant features and selects
a subset of features that are more relevant to the classification
result for training and prediction.
These steps help to improve the feature extraction ability
of the model on the data and enhance the classification
performance of the model. In addition, the training set is
divided into a training set and a validation set in the ratio of
7:3 to test the performance of the model during the training
process.
D. Evaluation indicators
In this paper, the commonly used Accuracy, Precision,
Recall and F1 scores are used as evaluation metrics to evaluate
the performance of all models.
1) Accuracy: Accuracy measures the proportion of total
samples that are correctly predicted by the model. Accuracy is
an intuitive and commonly used metric for binary classification
problems.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

9

2) Precision: Precision measures the proportion of positive
cases predicted by the model that are actually positive. For
intrusion detection systems, Precision reflects the accuracy of
the system’s prediction of intrusion behavior. Higher Precision
means fewer false alarms (misreporting normal behavior as
intrusion), which reduces unnecessary alarm processing.
3) Recall: Recall measures the proportion of actual positive
case samples that are correctly predicted as positive cases by
the model. For intrusion detection systems, Recall reflects the
system’s ability to recognize actual intrusions. A higher Recall
means fewer missed alarms (misreporting intrusions as normal
behavior), which implies a higher level of security for the
system.
4) F1: The F1 score is the reconciled average of Precision
and Recall, which takes into account the balance between the
two and can reflect the overall performance of the model
more comprehensively. For intrusion detection systems, the
F1 score can reduce false alarms while ensuring as much
as possible that the system can correctly identify the actual
intrusion behavior.
In the experiments in this paper, normal data is labeled as
0 and abnormal data is labeled as 1. The LSTM-1DResNet
model outputs either 0 or 1, where 1 indicates that the data
is predicted to be abnormal and 0 indicates that the data is
predicted to be normal. Abnormal data is true positive (TP) if
it is correctly predicted to be 1. If abnormal data is incorrectly
predicted to be 0, it is called false negative (FN); normal data
is correctly predicted to be 0 is true negative (TN); and if
normal data is incorrectly predicted to be 1, it is called false
positive (FP).
In the experiment, the confusion matrix is constructed based
on the prediction results of the model on the test set, and the
four evaluation metrics of Accuracy, Precision, Recall and F1
score are calculated. The evaluation metrics are calculated as
follows:
TP + TN
(1)
Accuracy =
total
Precision =

TP
TP + FP

(2)

Recall =

TP
TP + FN

(3)

F1 = 2 ·

Recall · Precision
Recall + Precision

(4)

Traditional machine learning approaches demonstrate significant limitations in handling high-dimensional network traffic,
as evidenced by SVM’s performance of 75.38% accuracy and
70.62% F1-score on the NSL-KDD dataset. These results
confirm the inadequacy of conventional methods for extracting
complex patterns inherent in vehicular network communications. Deep learning models offer moderate improvements,
with one-dimensional convolutional neural networks achieving 81.41% accuracy and long short-term memory networks
reaching 82.48% accuracy on NSL-KDD. However, both approaches exhibit constrained performance in comprehensive
spatiotemporal feature extraction, particularly when processing
the multi-layer protocol dynamics characteristic of CAV traffic.
Contemporary hybrid architectures present notable tradeoffs that warrant careful consideration. The CNN-GRU model
achieves 93.10% accuracy on NSL-KDD but shows reduced
effectiveness on CICIDS2017 with 90.17% accuracy, indicating potential dataset-specific limitations. Similarly, JAYALSTM demonstrates high recall of 97.68% on NSL-KDD yet
suffers from precision of only 88.11%, suggesting challenges
in minimizing false positive detections—a critical concern
for safety-critical vehicular systems. The LSTM-CNN architecture reports the highest NSL-KDD accuracy at 95.70%,
but this performance comes at substantial computational cost.
Its complex design incorporating hybrid autoencoders, six
convolutional layers, and self-attention mechanisms requires
447.10 million floating-point operations per second and 80,000
parameters, which may create significant barriers for deployment in resource-constrained vehicular environments.
In contrast, the proposed LSTM-1DResNet model achieves
94.38% accuracy on NSL-KDD, representing improvements
of 12.97 percentage points over one-dimensional convolutional neural networks and 11.90 percentage points over
standalone long short-term memory networks. On the CICIDS2017 dataset, the model demonstrates robust performance with 97.98% accuracy, 98.11% precision, 97.97%
recall, and 98.00% F1-score. Crucially, this performance is
attained with only 27.8 million floating-point operations per
second and 220 parameters, establishing a 16.1-fold reduction
in computational complexity compared to the LSTM-CNN
architecture. This efficiency profile positions the model as
a viable candidate for embedded deployment in vehicular
systems, where balancing detection accuracy with real-time
processing constraints remains a persistent challenge. The
consistent high performance across both datasets suggests the
architecture’s adaptability to diverse network environments.

E. Experimental set
The experiments were conducted using pytorch to build the
model, running in Ubuntu system, with hardware using 16G
RAM and NVIDIA GTX3060 GPU. the activation function
used the relu activation function, the learning rate was set to
0.0001, and the model was trained for 100 epochs at a time.
F. Experimental results and analysis
The evaluation conducted on NSL-KDD and CICIDS2017
datasets provides critical insights for intrusion detection in
Connected and Autonomous Vehicle environments(Table IV).

G. Ablation Experiment
The ablation study systematically evaluates two core architectural components through comparative analysis presented in
Table V and visualized in Fig. 6 and Fig. 7. First, the sequencefirst configuration, where long short-term memory processes
temporal dependencies before one-dimensional residual network feature extraction, demonstrates measurable advantages
over the spatial-first alternative. On the NSL-KDD dataset, the
sequence-first approach achieves 94.38% accuracy with 6956
correctly classified normal traffic instances and 1652 correctly

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

10

TABLE IV
P ERFORMANCE COMPARISON OF DIFFERENT MODELS
NSL-KDD

CICIDS2017

Method

Accuracy

Precision

Recall

F1-Score

Accuracy

Precision

Recall

F1-Score

SVM

0.7538

0.7548

0.7598

0.7062

0.9312

0.8996

0.8793

0.8890

1DCNN

0.8141

0.8377

0.8300

0.7680

0.9692

0.9358

0.9744

0.9535

LSTM

0.8248

0.8432

0.8370

0.7782

0.9587

0.9167

0.9658

0.9384

CNN-GRU [42]

0.9310

0.9375

0.9029

0.9234

0.9017

0.9234

0.9124

0.9205

JAYA-LSTM [43]

0.9200

0.8811

0.9768

0.9411

0.9421

0.9811

0.9251

0.9111

CNN-LSTM [39]

0.9225

0.8930

0.9804

0.9349

-

-

-

-

LSTM-CNN [44]

0.9570

0.9660

0.9580

0.9570

-

-

-

-

LSTM-1DResNet

0.9438

0.9262

0.9047

0.8675

0.9798

0.9811

0.9797

0.9800

TABLE V
P ERFORMANCE COMPARISON OF A BLATION EXPERIMENT
NSL-KDD

CICIDS2017

Method

Accuracy

Precision

Recall

F1-Score

Accuracy

Precision

Recall

F1-Score

LSTM-1DResNet

0.9438

0.9262

0.9047

0.8675

0.9798

0.9811

0.9797

0.9800

1DResNet-LSTM

0.92938

0.91770

0.86711

0.84199

0.9788

0.9519

0.9866

0.9677

LSTM-1DCNN

0.92116

0.91167

0.84728

0.82712

0.9759

0.9486

0.9800

0.9632

identified attack instances, compared to 92.94% accuracy for
the spatial-first approach with 6979 correctly classified normal instances but only 1497 correctly identified attacks. The
confusion matrices reveal that the sequence-first configuration
reduces false negatives by 55 instances (189 vs. 166 false
negatives for normal traffic) while maintaining comparable
false positive rates (323 vs. 323 for attack traffic), resulting in
a more balanced precision-recall profile. This pattern persists
in the CICIDS2017 evaluation, where the sequence-first model
correctly identifies 165,272 attack instances with only 15,443
false negatives, compared to 166,631 correctly identified attacks but 17,620 false negatives for the spatial-first approach.
The loss curves provide critical insights into the training
dynamics of these configurations. On the NSL-KDD dataset,
the spatial-first model initially converges quickly with the
training loss but gradually diverges from the optimal trajectory after approximately 30 epochs, indicating reduced
stability in later training stages. In contrast, the sequence-first
model maintains consistent alignment between training and
validation losses throughout the entire training process. On
the CICIDS2017 dataset, the spatial-first model consistently
demonstrates poorer alignment between training and validation losses, failing to achieve the same level of convergence
as the sequence-first approach, which maintains stable loss
trajectories across all training epochs.

Second, the contribution of the residual module is rigorously assessed by comparing the full LSTM-1DResNet model
against an ablated version using standard one-dimensional
convolutional layers (LSTM-1DCNN). On NSL-KDD, the
residual-enhanced model correctly classifies 1,652 attack instances with only 189 false negatives, while the non-residual
variant identifies only 1,418 attacks with 161 false negatives.
The confusion matrices further reveal that the residual model
maintains superior precision by reducing false positives from
558 to 323 while preserving high recall. This advantage becomes even more pronounced in the CICIDS2017 evaluation,
where the residual model correctly identifies 165,272 attacks
with 15,443 false negatives, compared to 164,762 correct
identifications with 18,198 false negatives for the non-residual
variant.
The loss curve analysis reveals distinct training patterns
between these variants. On the NSL-KDD dataset, the LSTM1DCNN model demonstrates reasonable convergence during
early training stages but exhibits increasing oscillation amplitude in validation loss during the later training phase,
indicating reduced stability as training progresses. In contrast,
the residual-enhanced model maintains consistent and stable
loss trajectories throughout the entire training process. On
the CICIDS2017 dataset, the LSTM-1DCNN model shows
substantial oscillations in validation loss both during early and

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

LSTM-1DResNet Training LOSS(NSL-KDD)

（a）

11

LSTM-1DCNN Training LOSS(NSL-KDD)

（b）

1DResNet-LSTM Training LOSS(NSL-KDD)

（c）

LSTM-1DResNet Training LOSS(CICIDS2017)

LSTM-1DCNN Training LOSS(CICIDS2017)

1DResNet-LSTM Training LOSS(CICIDS2017)

（d）

（e）

（f）

Fig. 6. Loss curve of ablation experiment.

LSTM-1DResNet Confusion Matrix(NSL-KDD)

LSTM-1DCNN Confusion Matrix(NSL-KDD)

（a）

（b）

LSTM-1DResNet Confusion Matrix(CICIDS2017)

LSTM-1DCNN Confusion Matrix(CICIDS2017)

（d）

（e）

1DResNet-LSTM Confusion Matrix(NSL-KDD)

（c）
1DResNet-LSTM Confusion Matrix(CICIDS2017)

（f）

Fig. 7. Confusion matrix of ablation experiment.

late training stages, suggesting fundamental instability in this
configuration when processing more complex network traffic
patterns. The residual-enhanced model, however, maintains
stable convergence across all training epochs, demonstrating
superior generalization capability across diverse network environments.
H. Discussion
The results highlight important considerations for CAV
intrusion detection. The computational efficiency of LSTM1DResNet is 27.8 M FLOPS, with an average inference
latency of 0.0242 milliseconds (24.23 microseconds) per sample, indicating that LSTM-1DResNet is feasible for practical
deployment in resource-constrained vehicular environments

where latency constraints typically require sub-100 millisecond response times. The observed performance differential
between sequence-first and spatial-first architectures supports
the rationale for prioritizing temporal dependency modeling in
CAV traffic analysis, as protocol-layer dynamics exhibit strong
sequential characteristics. Notably, the model achieves 97.98%
accuracy on CICIDS2017—a dataset featuring modern attack
patterns relevant to vehicular networks—with precision and
recall exceeding 97.97%, indicating robust capability in distinguishing normal and malicious traffic. While LSTM-CNN [44]
reports marginally higher NSL-KDD accuracy (95.70% vs.
94.38%), its substantially higher computational requirements
(447.10 M FLOPS) may limit practical deployment in embedded vehicular systems. The consistent performance across both

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

datasets (94.38% on NSL-KDD; 97.98% on CICIDS2017)
demonstrates the framework’s adaptability to diverse network
environments, though further validation in real-world CAV
testbeds remains warranted. The 11.90 percentage point improvement over standalone LSTM on NSL-KDD quantifies
the efficacy of the cascaded architecture in addressing highdimensional feature extraction challenges, while the ablation
study confirms the critical role of both the sequence-first
design and residual connections in optimizing model behavior.
These findings collectively suggest that balanced architectural
design can effectively address the tension between detection
performance and computational feasibility in vehicular security systems.
V. C ONCLUSION
Connected and autonomous vehicles (CAVs) critically enhance intelligent mobility yet introduce severe cybersecurity
vulnerabilities that threaten safety-critical operations. While
deep learning-based intrusion detection systems (IDS) offer
promise, existing models remain constrained by inadequate
spatiotemporal feature extraction and prohibitive computational demands for vehicular deployment. This work proposes LSTM-1DResNet, a novel end-to-end architecture integrating LSTM for long-range temporal dependency modeling and a one-dimensional convolutional residual network
(1DResNet) for spatial feature refinement. The model’s cascaded design—processing sequential dependencies before spatial extraction—preserves temporal integrity while avoiding
convolution-induced distortion of protocol-layer dynamics, a
critical limitation in prior hybrid architectures. Validated on
both NSL-KDD and CICIDS2017 datasets (the latter better reflecting modern CAV network characteristics), LSTM1DResNet achieves 94.38% accuracy on NSL-KDD and
97.98% accuracy, 98.11% precision, and 97.98% recall on
CICIDS2017. Crucially, it accomplishes this with only 27.8
M FLOPS and 220 parameters, enabling real-time operation
within vehicular latency constraints (¡100 ms). Despite these
advances, the severe class imbalance in current datasets (e.g.,
DoS attacks at 52.9% versus U2R attacks at 0.0009% in
NSL-KDD) risks bias toward prevalent attack types. Future
work will develop a robust end-to-end multi-class IDS incorporating adaptive focal loss and GAN-based minorityclass augmentation to ensure reliable detection of rare cyberattacks while maintaining ultra-low computational overhead
for safety-critical CAV environments.
ACKNOWLEDGMENT
The authors acknowledge the funding of following science
foundations: the National Natural Science Foundation of China
(No.42201464).
R EFERENCES
[1] S. Garg, D. Mehrotra, H. M. Pandey, et al., ”Accessible review of internet
of vehicle models for intelligent transportation and research gaps for
potential future directions,” Peer-to-Peer Networking and Applications,
vol. 14, no. 2, pp. 978-1005, 2021.
[2] ”Tencent Cohen Lab: Lexus vehicle safety research review report.”
Available online: https://keenlab.tencent.com/, 2020.

12

[3] N. Lewandowska, ”Intrusion Detection Systems: Categories, attack detection and response,” 2024.
[4] M. Kamal, G. Srivastava, M. Tariq, ”Blockchain-based lightweight and
secured v2v communication in the internet of vehicles,” IEEE Transactions on Intelligent Transportation Systems, vol. 22, no. 7, pp. 3997-4004,
2020.
[5] P. Manso, J. Moura, C. Serrão, ”SDN-based intrusion detection system
for early detection and mitigation of DDoS attacks,” Information, vol. 10,
no. 3, p. 106, 2019.
[6] E. Osa, P. E. Orukpe, U. Iruansi, ”Design and implementation of a
deep neural network approach for intrusion detection systems,” e-PrimeAdvances in Electrical Engineering, Electronics and Energy, vol. 7, p.
100434, 2024.
[7] L. Yang, A. Shami, ”A transfer learning and optimized CNN based
intrusion detection system for Internet of Vehicles,” in ICC 2022-IEEE
International Conference on Communications, IEEE, 2022, pp. 27742779.
[8] L. Xing, K. Wang, H. Wu, et al., ”FL-MAAE: An intrusion detection
method for the Internet of Vehicles based on federated learning and
memory-augmented autoencoder,” Electronics, vol. 12, no. 10, p. 2284,
2023.
[9] C. Yin, Y. Zhu, J. Fei, et al., ”A deep learning approach for intrusion
detection using recurrent neural networks,” IEEE Access, vol. 5, pp.
21954-21961, 2017.
[10] J. Ashraf, A. D. Bakhshi, N. Moustafa, et al., ”Novel deep learningenabled LSTM autoencoder architecture for discovering anomalous events
from intelligent transportation systems,” IEEE Transactions on Intelligent
Transportation Systems, vol. 22, no. 7, pp. 4507-4518, 2020.
[11] Y. Liu, M. Xiao, Y. Zhou, et al., ”An access control mechanism based
on risk prediction for the IoV,” in 2020 IEEE 91st Vehicular Technology
Conference (VTC2020-Spring), IEEE, 2020, pp. 1-5.
[12] R. K. Mahendran, S. Rajendran, P. Pandian, et al., ”A Novel Constructive
Unceasement Conditional Random Field and Dynamic Bayesian Network
Model for Attack Prediction on Internet of Vehicle,” IEEE Access, 2024.
[13] M. V. Kotpalliwar, R. Wajgi, ”Classification of attacks using support
vector machine (svm) on kddcup’99 ids database,” in 2015 Fifth International Conference on Communication Systems and Network Technologies,
IEEE, 2015, pp. 987-990.
[14] H. Gharaee, H. Hosseinvand, ”A new feature selection IDS based on
genetic algorithm and SVM,” in 2016 8th International Symposium on
Telecommunications (IST), IEEE, 2016, pp. 139-144.
[15] R. Wazirali, ”An improved intrusion detection system based on KNN
hyperparameter tuning and cross-validation,” Arabian Journal for Science
and Engineering, vol. 45, no. 12, pp. 10859-10873, 2020.
[16] K. V. Krishna, K. Swathi, B. B. Rao, ”A novel framework for nids
through fast knn classifier on CICIDS 2017 dataset,” International Journal of Recent Technology and Engineering (IJRTE), vol. 8, no. 5, pp.
3669-3675, 2020.
[17] Z. Liu, Y. Shi, ”A hybrid IDS using GA-based feature selection method
and random forest,” Int. J. Mach. Learn. Comput., vol. 12, no. 2, pp.
43-50, 2022.
[18] D. S. Kim, H. N. Nguyen, J. S. Park, ”Genetic algorithm to improve SVM based network intrusion detection system,” in 19th International Conference on Advanced Information Networking and Applications
(AINA’05) Volume 1 (AINA papers), IEEE, 2005, vol. 2, pp. 155-158.
[19] M. Panda, M. R. Patra, ”Network intrusion detection using naive bayes,”
International journal of computer science and network security, vol. 7,
no. 12, pp. 258-263, 2007.
[20] L. Yang, A. Shami, G. Stevens, et al., ”LCCDE: a decision-based
ensemble framework for intrusion detection in the internet of vehicles,”
in GLOBECOM 2022-2022 IEEE Global Communications Conference,
IEEE, 2022, pp. 3545-3550.
[21] M. Kakavand, N. Mustapha, A. Mustapha, et al., ”Effective dimensionality reduction of payload-based anomaly detection in TMAD model for
HTTP payload,” KSII Transactions on Internet and Information Systems
(TIIS), vol. 10, no. 8, pp. 3884-3910, 2016.
[22] H. M. Tahir, A. M. Said, N. H. Osman, et al., ”Oving K-means clustering
using discretization technique in network intrusion detection system,”
in 2016 3rd International Conference on Computer and Information
Sciences (ICCOINS), IEEE, 2016, pp. 248-252.
[23] S. Wu, K. Roberts, S. Datta, et al., ”Deep learning in clinical natural
language processing: a methodical review,” Journal of the American
Medical Informatics Association, vol. 27, no. 3, pp. 457-470, 2020.
[24] B. Singh, R. Desai, H. Ashar, et al., ”A trade-off between ML and
DL Techniques in natural language processing,” in Journal of Physics:
Conference Series, IOP Publishing, 2021, vol. 1831, no. 1, p. 012025.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3663771

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

[25] E. E. B. Adam, ”Deep learning based NLP techniques in text to speech
synthesis for communication recognition,” Journal of Soft Computing
Paradigm (JSCP), vol. 2, no. 04, pp. 209-215, 2020.
[26] X. Liu, L. Song, S. Liu, et al., ”A review of deep-learning-based medical
image segmentation methods,” Sustainability, vol. 13, no. 3, p. 1224,
2021.
[27] S. Srivastava, A. V. Divekar, C. Anilkumar, et al., ”Comparative analysis
of deep learning image detection algorithms,” Journal of Big data, vol.
8, no. 1, p. 66, 2021.
[28] H. Kheddar, M. Hemis, Y. Himeur, ”Automatic speech recognition using
advanced deep learning approaches: A survey,” Information Fusion, 2024,
p. 102422.
[29] W. Zhang, C. Liu, H. Fei, et al., ”Research on automatic speech
recognition based on a DL–T and transfer learning,” Chinese Journal
of Engineering, vol. 43, no. 3, pp. 433-441, 2021.
[30] H. Kheddar, Y. Himeur, S. Al-Maadeed, et al., ”Deep transfer learning for automatic speech recognition: Towards better generalization,”
Knowledge-Based Systems, vol. 277, p. 110851, 2023.
[31] R. Vinayakumar, K. P. Soman, P. Poornachandran, ”Applying convolutional neural network for network intrusion detection,” in 2017
International Conference on Advances in Computing, Communications
and Informatics (ICACCI), IEEE, 2017, pp. 1222-1228.
[32] H. Jia, J. Liu, M. Zhang, et al., ”Network intrusion detection based
on IE-DBN model,” Computer Communications, vol. 178, pp. 131-140,
2021.
[33] A. Anzer, M. Elhadef, ”A multilayer perceptron-based distributed intrusion detection system for internet of vehicles,” in 2018 IEEE 4th
international conference on collaboration and internet computing (CIC),
IEEE, 2018, pp. 438-445.
[34] S. Hochreiter, J. Schmidhuber, ”Long short-term memory,” Neural
computation, vol. 9, no. 8, pp. 1735-1780, 1997.
[35] Y. LeCun, Y. Bengio, ”Convolutional networks for images, speech, and
time series,” The handbook of brain theory and neural networks, vol.
3361, no. 10, pp. 1995, 1995.
[36] G. Sri vidhya, R. Nagarajan, ”A novel bidirectional LSTM model for
network intrusion detection in SDN-IoT network,” Computing, 2024, pp.
1-30.
[37] A. Alsaleh, ”A Novel Intrusion Detection Model of Unknown Attacks
Using Convolutional Neural Networks,” Computer Systems Science &
Engineering, vol. 48, no. 2, 2024.
[38] A. Alferaidi, K. Yadav, Y. Alharbi, et al., ”Distributed Deep CNNLSTM Model for Intrusion Detection Method in IoT-Based Vehicles,”
Mathematical Problems in Engineering, vol. 2022, no. 1, p. 3424819,
2022.
[39] R. B. Said, Z. Sabir, and I. Askerzade, ”CNN-BiLSTM: A Hybrid Deep
Learning Approach for Network Intrusion Detection System in SoftwareDefined Networking with Hybrid Feature Selection,” IEEE Access, vol.
11, pp. 138732–138747, 2023.
[40] H. Sun, M. Chen, J. Weng, et al., ”Anomaly detection for in-vehicle network using CNN-LSTM with attention mechanism,” IEEE Transactions
on Vehicular Technology, vol. 70, no. 10, pp. 10880-10893, 2021.
[41] S. Elsayed, K. Mohamed, and M. Ashraf Madkour, ”A Comparative
Study of Using Deep Learning Algorithms in Network Intrusion Detection,” IEEE Access, vol. 12, pp. 58851–58870, 2024.
[42] T. Bakhshi and B. Ghita, ”Anomaly Detection in Encrypted Internet
Traffic Using Hybrid Deep Learning,” Security and Communication
Networks, vol. 2021, no. 1, p. 5363750, 2021.
[43] N. Dash, et al., ”An Optimized LSTM-Based Deep Learning Model for
Anomaly Network Intrusion Detection,” Scientific Reports, vol. 15, no.
1, p. 1554, 2025.
[44] Y. Xue, C. Kang, and H. Yu, ”HAE-HRL: A Network Intrusion
Detection System Utilizing a Novel Autoencoder and a Hybrid Enhanced
LSTM-CNN-Based Residual Network,” Computers & Security, vol. 151,
p. 104328, 2025.
[45] P. Sinha, et al., ”A High Performance Hybrid LSTM CNN Secure
Architecture for IoT Environments Using Deep Learning,” Scientific
Reports, vol. 15, no. 1, p. 9684, 2025.
[46] K. He, X. Zhang, S. Ren, et al., ”Deep residual learning for image
recognition,” in Proceedings of the IEEE conference on computer vision
and pattern recognition, 2016, pp. 770-778.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

13
PAPER_TEXT
