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
# [622] CAN Bus Intrusion Detection Based on Deep Learning With Data Augmentation for Connected Autonomous Vehicles
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
编号：622
题名：CAN Bus Intrusion Detection Based on Deep Learning With Data Augmentation for Connected Autonomous Vehicles
年份：2025
DOI：10.1109/tvt.2025.3603056
来源：IEEE Transactions on Vehicular Technology
PDF：paper/10.1109_TVT.2025.3603056.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、其他AI安全与跨域异常检测
相关性：强相关，分数 14
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\622.txt
- 原始字符数：66734
- 本次发送字符数：66734
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 75, NO. 2, FEBRUARY 2026

2253

CAN Bus Intrusion Detection Based on Deep
Learning With Data Augmentation for Connected
Autonomous Vehicles
Xiang Wang, Jian Zhao , Member, IEEE, Pengbo Liu, Nianmin Yao , and Zheng Xu

Abstract—As the de-facto standard for in-vehicle networks, the
Controller Area Network (CAN) is exposed to different types of
cyber-attacks due to the lack of security mechanisms. Intrusion
Detection Systems (IDS) can be deployed to identify the attacks
by monitoring host and network activities. However, there is little
abnormal historical data that can be used to train deep learning
models, resulting in data imbalance and biased trained model.
Hence, we propose a prediction-based IDS framework for detecting
the attacks on a CAN bus, which consists of two deep-learning models of the data augmentation module and the prediction module.
Firstly, the Generative Adversarial Networks (GAN) was utilized
as the data augmentation module to automatically generate highquality attack data and balance the training set. Two networks were
introduced as the prediction module, and the first one is a convolutional neural networks (CNN) that predicts correlated data of all
CAN IDs, and the second one is an LSTM that predicts messages
individually using times series data for each CAN ID. Furthermore,
an intrusion detection equipment for the CAN bus was designed and
the real vehicle test was conducted. The experimental results show
that the proposed method can detect CAN attacks, with an average
F1-score of 99.74% and an accuracy of 99.78%. Compared with
the reference work, the F1-score of attack detection is improved by
15.25%, and also the detection time is reduced by 29.11%.
Index Terms—In-vehicle networks, CAN, IDS, CNN, LSTM,
data augmentation.

I. INTRODUCTION
ITH the development of Internet of Vehicles (IoVs)
and mobile communication technology, the connected
autonomous vehicles (CAVs) are equipped with a variety of
sensors and onboard computing devices, which contribute significant improvement to driving experience, and play a vital
role in Intelligent Transportation Systems (ITS) [1]. While CAV
introduces a range of comfort and safety features, all of the
added components, the interaction between vehicles and external

W

Received 2 August 2024; revised 4 February 2025, 18 April 2025, and 7 August 2025; accepted 18 August 2025. Date of publication 26 August 2025; date
of current version 13 February 2026. This work was supported by the National
Key Research and Development Program under Grant 2022YFB3203600. The
review of this article was coordinated by Dr. Wenshuo Wang. (Corresponding
author: Jian Zhao.)
Xiang Wang, Jian Zhao, Pengbo Liu, and Zheng Xu are with the State Key
Laboratory of Structural Analysis for Industrial Equipment, Dalian University
of Technology, Dalian 116024, China (e-mail: wangxiang@mail.dlut.edu.cn;
jzhao@dlut.edu.cn; pengboliu@dlut.edu.cn; xu_zheng@mail.dlut.edu.cn).
Nianmin Yao is with the School of Computer Science, Dalian University of
Technology, Dalian 116024, China (e-mail: lucos@dlut.edu.cn).
Digital Object Identifier 10.1109/TVT.2025.3603056

access will become more frequently, resulting in new attack
surfaces and causing security issues for in-vehicle networks [2],
[3], [4], [5]. As the de-facto standard for in-vehicle networks,
the Controller Area Network (CAN) has become the dominant
protocol used in vehicles due to its advantages of multiple master
control, high transmission speed, high reliability, and low cost
[6]. However, the CAN bus is a broadcast media, and a CAN
message is not intrinsically provided with security mechanisms,
such as encryption and authentication. Due to the simplified
structure and the lack of security insight, the CAN protocol is
vulnerable to many attacks, including injection, Dos, replay,
drop, and tampering attacks [7]. When a hacker has collected
CAN traffic, the reverse engineering analysis techniques can
be utilized to analyze the vehicle’s critical driving information
transmitted through CAN traffic, then the hacker can get into
the CAN bus through external wireless or physical access such
as OBD-II Port to gain unauthorized control of a vehicle, which
would compromise the safety of driver, the passengers, and the
vehicles. Koscher et al. [8] developed CarShark, a software
designed to monitor and manipulate messages on the CAN
bus through the OBD-II Port and then control the door locks,
headlights, ECUs and other components of the vehicle. In order
to safeguard CAVs, Intrusion Detection Systems (IDS) can be
deployed to discover suspicious network activity of in-vehicle
networks and detect attack traffic.
Deep learning techniques have been extensively employed
by the intrusion detection systems in ITS due to their ability to analyze data in an independent manner without relying
on any human knowledge [9], [10], [11]. However, they have
limitations. Since CAN specifications are kept confidential and
privately owned by manufactures, it is difficult to analyze and
understand in-vehicle data. These data-driven models require
massive amount of historical CAN traffic to capture the data
features and gain the ability to identify attack traffic. Several
in-vehicle datasets have been shared to promote vehicle security
research [12], [13]. Still, there are few attack samples in these
datasets to train intrusion detection systems for CAN bus, so
models cannot fully learn the characteristics of attack data and
be fully utilized, resulting in biased trained models that could
not identify attacks well [14]. To address this issue, various data
augmentation approaches have been proposed (e.g., SMOTE
[15] ADASYN [16]). Although the data set is expanded to
a certain extent, they are essentially simple replication and
rearrangement strategies, which cannot generate substantial

0018-9545 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

2254

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 75, NO. 2, FEBRUARY 2026

data, and easily leads to over-fitting with learning. With arrival of
Generative Adversarial Networks (GAN), new methods for data
augmentation have appeared. Kumar et al. [17] provided an intrusion detection system based on an XGBoost Classifier, which
used Wasserstein Conditional Generative Adversarial Network
(WCGAN) to generates attack data and balance the training set.
Yuan et al. [18] proposed a data augmentation method named
B-GAN, using a combination of GAN, LSTM and RNN. The
finding showed that B-GAN can generate high-quality attack
samples and improve the performance of intrusion detection.
As one of the most popular models in the field of deep learning,
GAN has been widely used in computer vision, natural language
processing and other fields, but there are few applications in the
field of in-vehicle networks security [19], [20]. Song et al. [21],
[14], [22] were the first to introduce GAN into the CAN bus
security. They proposed several deep learning-based methods,
which detected anomalies using GAN and DCNN as classifier,
respectively. Nevertheless, they did not consider the spatiotemporal correlation of CAN messages contents and the authors
stated that the proposed methods still show poor performance
for tampering attacks detection. CAN messages are time series
data and can be broadcast via different ECUs, which means
there is a correlation between the ECUs since they are designed
to collaborate to perform complex in-vehicle tasks. Therefore,
the correlation of CAN messages can be incorporated to improve
the performance of model.
The goal of this paper is to provide an IDS that can achieve
high detection accuracy and low detection time in a resource limited and data imbalanced environment. Considering the temporal
correlation between CAN messages, a lightweight deep learning
model can be used to effectively extract spatiotemporal features.
Additionally, data augmentation method can be introduced to
deal with the model underfitting problem caused by the lack
of attack samples. Therefore, a prediction-based IDS with data
augmentation is proposed for CAN bus attacks detection. The
prediction module consists of two networks, one based on CNN
and the other on LSTM. The CNN module predicts correlated
data for all sequential CAN IDs based on the interdependence
of different ECUs. The LSTM module predicts time series data
for each CAN ID using payload data that contains information
crucial for the operation of the vehicle. These models leverage
the correlation of CAN message contents, which makes it better
suited for CAN buses with constrained resources and detection
time. To address the data imbalance problem, GAN is utilized
to automatically generate high-quality attack samples, making
it possible to deal with the imbalance of malicious CAN traffic
and achieve good performance with limited attack data. The
data augmentation module generates attack data by directly
processing the bit representation of the CAN ID and payload
data without the need for private CAN specifications from manufacturers, which simplifies the processing procedures and makes
it easier to be adapted to different manufacturers and vehicles
without requiring the reverse engineering analysis techniques.
The main contributions of this paper can be summarized as
follows:
1) We propose a novel IDS for CAN bus by fusing a CNN
and LSTM with data augmentation, which is more suitable

for such a data imbalanced environment and more effective
for CAN messages that carries time series physical signals
of different limited-resource ECUs. The evaluation results
show that the proposed method of using data augmentation
to train model successfully improves the performance of
the IDS, with the average accuracy is 99.74% and the
average F1-score is improved by 15.25%.
2) Our method directly processes the bit representation of the
CAN ID and payload data, which simplifies the processing
procedures and makes it more efficient and effective. The
experiments show that the proposed model can complete
anomaly detection within 0.56 ms, which is reduced by
29.11%.
3) We design an equipment for CAN bus to detect and simulate online attacks on a real vehicle. The proposed model
is also tested on two domain controllers. The experiments
show that the accuracy and the detection time of the
proposed model are close to the performance on a PC.
The rest of this paper is organized as follows. Some previous
studies on intrusion detection systems for CAN bus security are
reviewed in Section II. Each module of our proposed IDS structure is introduced in detail in Section III. Section IV provides the
performance evaluation of the proposed method. In Section V,
we introduce an equipment for CAN bus to detect and simulate
attacks on a real vehicle. Finally, conclusions are provided in
Section VI.
II. RELATED WORKS
The intrusion detection systems for CAN bus security have
been widely investigated by several pioneer researchers over
the years. Based on the detection scope and basis, the studies
can be grouped into statistical and machine learning-based IDS.
The statistical-based studies learn normal behavior based on
conditional statistical relationship analysis and establish thresholds for anomalies detection through baseline patterns. Gmiden et al. [23] introduced an anomaly detection system using
the time intervals of CAN messages to detect anomalies like
Dos and replay attacks. The system checked the arrive time of
each CAN messages then detected attacks based on the time
intervals compared to last messages. Taylor et al. [24] provided
an intrusion detection method based on the analysis of CAN
data flow, which can compare the statistical value of the current
and historical traffic in 1-s time window. Muter et al. [25]
firstly introduced entropy into CAN bus security. The entropy of
CAN messages was calculated to distinguish the Dos and replay
attacks. Similarly, Wu et al. [26] also proposed an improved
entropy-based IDS. They calculated the information entropy
of CAN traffic over a fixed-length sliding window to detect
attacks. The findings showed that the performance of their
method demonstrated better than previous entropy-based IDS.
Koyama et al. [27] presented a frequency-based anomaly detection method to discover violations in the network traffic using
quantized intervals of the CAN payload values. HAN et al. [28]
developed an IDS using survival analysis model to monitor CAN
traffic and the survival rate of each CAN ID is calculated to
detect anomalies. Evaluation results showed that the normal and

WANG et al.: CAN BUS INTRUSION DETECTION BASED ON DEEP LEARNING WITH DATA AUGMENTATION

attack traffic could be detected with high accuracy. While these
statistics-based methods showed decent performance for highvolume attacks, they did not consider the low-volume attacks
that have little effect on CAN traffic flow [12].
Furthermore, several machine learning-based solutions have
been proposed to detect attacks on the in-vehicle network.
Avatefipour et al. [29] proposed an IDS based on a modified
one-class SVM (OCSVM) in the CAN traffic. The result proved
that the proposed method achieved the highest performance
for anomaly detection compared to classical one-class SVM
and Isolation Forest. Duan et al. [30] proposed an improved
isolation forest method for tampering attacks detection. They
quantified the degree of anomalies by calculating the data mass
of CAN messages, and identified attacks by the anomaly score.
The method was evaluated on three datasets - one generated
by the CANOE and two standard datasets. It was compared
to iForest, LOF, and one-class SVM and achieved an accuracy
of 99.93%, which is better than the baseline. Kang et al. [31]
provided an IDS based on Deep Neural Networks (DNN) to
learn normal traffic and to detect anomalies. Unsupervised deep
belief networks were used to initialize the parameters of DNN
to improve the detection performance. Tests were conducted
with a simulated dataset generated by CANOE and the result
demonstrated that the performance of their method was better
compared to models based on SVM and ANN with an accuracy
of 98%. Considering the temporal correlation of CAN messages, several studies incorporated recurrent neural networks
(RNN) with memory in their structure into their methods. Taylor et al. [32] introduced an IDS for CAN bus which uses a Long
Short-Term Memory (LSTM) unit in its structure. Anomalies on
the CAN messages can be individually detected for each CAN
ID without the need to extracted features from CAN messages
during the preprocessing stage. Zhang et al. [33] proposed an
anomaly detection system for CAN bus by fusing CNN and
RNN with an attention mechanism. The temporal features of
each ECU can be automatically learned without professional
knowledge. Qin et al. [34] introduced GAN-based intrusion
detection system named GPIDS, to detect attacks in CAN traffic
by fusing a generative adversarial network and assisted contextual pattern-aware. They achieved an average accuracy of
97.42% by performing this experiment using dataset performed
on four vehicles that had six types of attacks: bus-off, spoofing,
masquerade, replay, fuzzy and SOME. Jeong et al. [35] proposed
an IDS for in-vehicle network which uses raw payloads to
improve the intrusion detection performance. They introduce
several modules to reach the trade-off between prediction performance and the computational consumption. Gao et al. [36]
designed a CAN image generation method to convert CAN
traffic data into CAN images, which makes the attack visible
and traceable. The experiments show that the proposed IDS has
a decent performance for Dos attack detection. However, their
method did not consider the data imbalance issues. Therefore, it
may not be as effective at distinguishing between normal traffic
and previously unseen attacks. Guo et al. [37] [38] proposed
an attack detection scheme for connected vehicles by fusing a
refined kinematic model, measurement model, and attack model.

2255

The experiment results show that their methods demonstrate
decent detection performance and high reliability.
III. METHOD
The ability of most algorithms to identify and detect intrusions
relies on historical data. Therefore, in order to establish a reliable
intrusion detection model, a large amount of attack data of CAN
traffic is required during the training stage. However, attack data
is difficult to be obtained in the real world, and when deep
neural network is used, data imbalance may cause overfitting
and improper bias problems. In fact, it is difficult to perform
the known attacks for all IDs inside a vehicle. Due to the safety
issues, it is difficult to collect attack data while driving a vehicle.
Furthermore, there is no standard specifying the meaning of IDs
and encoding of the signals transmitted in the payload data,
which means that manufacturers can design their own policies
for different vehicles. Even for the same manufacturer, it may use
different combinations of IDs and payloads due to the types of
vehicle models. Additionally, CAN messages of a vehicle differs
due to different driving scenarios, driver habits, road conditions
and so forth. Thus, the objectives of this paper are to solve the
data imbalance problem and achieve high detection accuracy
in the case of resource-constrained and extremely limited attack
samples, making it easier to be adapted to different vehicles from
various manufacturers without requiring the reverse engineering
analysis techniques and the private CAN specifications from
manufacturers.
To accomplish this, a method is proposed, which involves
a data augmentation module based on WGAN-GP to generate
high-quantity attack samples, and a prediction module based on
lightweight models to identify anomalies using the spatiotemporal correlation of CAN messages. The complete structure of our
proposed framework is depicted in Fig. 1. The training samples
consisting of CAN ID and its payload are converted from 1D
time series vector to 2D image. Then, the data augmentation
module trains WGAN-GP architecture to learn the distribution
of the normal CAN traffic data. At this point, the generator of
WGAN-GP is used to generate substantial CAN attack samples
and balance the training set. Actually, the occurrence of normal
data is significantly more than that of attack data, and then, it is
suggested to collect as much normal data as possible for gasping
the main feature. So, the WGAN-GP can be trained with normal
data to generate attack data. With the increase of normal data
in the training process, the real permitted range for each signal
will become clearer. Finally, the prediction module consists of a
LSTM and a CNN, which is trained with the augmented dataset
to distinguish between normal traffic and attack data by using
the spatiotemporal correlation of CAN messages contents.
A. Feature Extraction
In the feature extraction stage, the messages from the CAN bus
are collected, then the ID and payload of each CAN message is
extracted and arranged by timestamp. Furthermore, the payload
is categorized based on ID. The features selected from CAN
messages are taken as input for subsequent detection. These

2256

Fig. 1.

Fig. 2.

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 75, NO. 2, FEBRUARY 2026

The algorithm structure of the proposed IDS.

The process of converting CAN messages into images.

features include the CAN IDs and eight bytes of payload data.
Since GAN is introduced to generated attack samples for data
augmentation and GAN has advantages in image processing,
the 1D time series vector of the selected features is mapped into
the 2D image with one-hot-vector. The process of converting
CAN IDs and payloads into images is illustrated in Fig. 2. The
11-bit CAN ID is mapped into [1,48] matrix and the 64-bit
payload into a [1,256] matrix. Specifically, each element of

CAN ID and payload is converted from hexadecimal string to
binary from with 16 digits using one-hot-vector encoding. For
instance, each element of the CAN ID ‘0x2C1’ is represented
by a 16-dimensional vector with 15 bits are ‘0’ and only one bit
is ‘1’. Then, each CAN ID is represented as a [1,48] matrix
while the payload is represented as a [1,256] matrix. After
that, 64 successive CAN IDs are spliced to generate a CAN
ID image, and successive 256 payloads of each ID are spliced
to generate a CAN payload image. In the model training stage,
both IDs and payloads are converted into images and input into
WGAN-GP to generate attack samples for data augmentation,
and LSTM-CNN is trained using the augmentation datasets for
intrusion detection. In the model testing stage, IDs are converted
into images and input into the CNN to predict the correlated data
of all IDs. A window is set to buffer the w most recent frames,
and the frames in a window are sorted in chronological order.
When the window initialization is completed, the IDS only needs
to use the latest CAN message to update the window to come to
a conclusion. The payloads of each message are directly input
into the LSTM to predicts messages individually using times
series data for each ID.
B. GAN-Based Data Augmentation for Anomaly Detection
The WGAN-GP is trained to generate synthetic images of
anomalies CAN traffic and balance the training set of intrusion
detection system. GAN is a generative deep modelling approach
designed based on game theory, which has been recently used

WANG et al.: CAN BUS INTRUSION DETECTION BASED ON DEEP LEARNING WITH DATA AUGMENTATION

2257

for data augmentation [39]. A GAN architecture consists of the
generator and the discriminator, which corresponds to a minimax
two-player game. The training stage updates parameters and
optimizes objective function through the competition between
the generator and the discriminator.
The generator takes noise samples as input to generate fake
samples. The discriminator takes the real data and the fake
samples created by the generator as input to distinguish real
data and fake samples.
Wasserstein Generative Adversarial Network (WGAN), an
enhanced version of GAN, was introduced to solve the vanishing
gradient problem of GAN [40]. Wasserstein distance W is
introduced to measure the difference between the distribution
of real data and fake samples, which can be defined as:
W (Pr , Pg ) ≈ L = min max P (D, G)
G

D

= Ex∼Pr (x) [D (x)] − Ez∼Pg (z) [D (G (z))]

(1)

where D is the discriminator, D(x) represents the probability of
an anomaly in real samples x, G is the generator, G(z) represents
fake samples generated from random noise z, Pr represents
the distribution of real data, and Pg is the distribution of fake
samples. The discriminator is required to satisfy the 1st order
Lipschitz constraint, we will have:
∇x̄ D (x̄) ≤ I

(2)

where x̄ represents the linear interpolation between real samples
x and random noise z, which can be calculated as:
x̄ = tx + (1 − t) z, t ∈ [0, 1]

(3)

However, WGAN has limitations in the time consumption
and the model convergence. To address this issue, the Wasserstein Generative Adversarial Network with Gradient Penalty
(WGAN-GP), was introduced by Ishaan et al. [41]. WGAN-GP
introduces a gradient penalty method to compel the discriminator to satisfy the 1st order Lipschitz function constraint. Optimal
engineering results are achieved by constraining gradient values
around 1, and thus, the gradient penalty term GP is stated as:


Δ
GP = Ex∼P (x) (∇x D (x̄)2 − 1)2
(4)
The optimization objective of the discriminator is to maximize
the probability of correctly distinguishing between fake samples
G(z) and real samples x, which can be defined as:
max L (D, G) = Ex∼Pr (x) [D (x)] − Ez∼Pg(z) [D (G (z))]
θ


−λEx−P (x) (∇x D (x̄)2 − 1)2
(5)
where λ is a hyperparameter used to adjust the gradient penalty
term.
The optimization objective for the generator is to minimize
the Wasserstein distance between the distribution of generated
samples Pg and the distribution of real samples Pr . Due to
Ez∼Pg [D(G(z))] is independent of the generator, the objective
function for the generator can be defined as:
min L (D, G) = −Ez∼Pg [D (G (z))]
φ

(6)

Fig. 3. Architecture of WGAN-GP based on CAN ID. (a) Architecture of
generator. (b) Architecture of discriminator.

The data augmentation module consists of two WAGN-GP
models. Since each ECU collaborates to perform various tasks
in the vehicle, there is a correlation between ECUs. It means
that payloads with different IDs are temporally correlated at
a specific point in time. For example, a vehicle’s speed, engine
power, torque and emission values are all affected when it detects
an obstacle ahead and then brakes. In addition, payloads with
the same ID is time series data and tend to change with a certain
periodicity. Each field of the payload is divided by different
signals, and the data of each field is transmitted continuously
and changes regularly within a specific range. For instance, ID =
0x064 represents engine data, which contains six signals in eight
bytes, namely IdelRunning, EngTemp, PetroLevel, EngForce,
EngPower and EngSpeed. The time interval between messages
with ID = 0x064 is 10 ms, and when EngSpeed changes, EngPower and EngForce will change accordingly. The first model
based on CAN ID is designed to learn the interdependence
of different ECUs, and the second based on CAN payload is
designed to learn the temporal correlation of time series data.
Both of them are consist of a discriminator and a generator. The
only difference between them is the parameters of the network
architecture. As can be seen in Figs. 3(a) and 4(a), the generator
consists of a deconvolutional neural network composed of four
layers, which takes random noise as the input to generate fake
CAN images that are similar to the real CAN images. The
discriminator, as depicted in Figs. 3(b) and 4(b) consists of a
deep neural network composed of four layers, which is used to
identify the fake CAN images that generated by the generator.
Moreover, an early stopping mechanism is employed while the
training of the intrusion detection model to avoid overfitting.
C. Prediction Module Neural Network Design
Two lightweight networks are trained to identify anomalies
from normal CAN traffic, based on the spatiotemporal correlation of CAN messages contents.
1) CNN-Based Network: The CAN messages are correlated
due to different ECUs collaborate to perform complex in-vehicle

2258

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 75, NO. 2, FEBRUARY 2026

using the temporal correlation of time series physical signals.
Also, in our case, the CAN payload data is classified based on
their CAN ID and then detected by the corresponding IDS. Once
one of the IDSs detects anomalies, the vehicle will immediately
receive an abnormal alarm.
IV. SIMULATION EXPERIMENT

Fig. 4. Architecture of WGAN-GP based on CAN payload. (a) Architecture
of generator. (b) Architecture of discriminator.

The experiments are performed to compare the performance
of our proposed method and other models, including LSTM-AE,
OCSVM, iForest. Also, we analyze the effectiveness of the data
augmentation module on prediction performance and compare
our proposed method with other data augmentation algorithms,
including GAN, SMOTE and ADASYN. Additionally, the quality of generated samples is analyzed using feature maps and
statistics.
A. Implementation Details

Fig. 5.

CNN-based prediction network architecture.

Fig. 6.

LSTM-based prediction module architecture.

tasks. Therefore, we use a lightweight CNN architecture here to
learn the spatial contiguity in normal CAN traffic. As can be
seen in Fig. 5, the CNN prediction network, which consists six
layers, four convolutional layers, two fully connected layers to
extract CAN images. The ReLU is used as the activation function
after each convolution layer and the model is trained with Adam
optimizer. The CNN is trained to distinguish between attacks
and normal CAN traffic, based on the CAN traffic images form.
2) LSTM-Based Network: Since the LSTM model is more
effective to predict time series data, we convert the CAN payload
images onto 1D feature vectors using one-hot-vector. As can be
seen in Fig. 6, the lightweight LSTM prediction network, which
consists two layers, one LSTM layer and one fully connected
layer to extract CAN messages. The LSTM is trained to determines whether the current CAN message has been tampered

1) Experiment Environment: The experiment is run on the
equipment of AMD Ryzen 5 5600H with Radeon Graphics
@3.30 GHz, equipped with NVIDIA GeForce RTX3050, and
Windows 10 for the operating system.
2) Attack Model: The communication mechanism of CAN
bus is broadcast. Each ECU on a CAN bus can receive and send
messages to control the vehicle. A CAN messages is not protected with authentication mechanism. The attackers can access
the CAN bus through OBD-II port or wireless. Attack messages
will cause normal messages to be blocked or tampered with.
When attack messages carry high priority IDs and are sent at a
higher frequency than normal, the bus will be overloaded and the
transmission of normal messages will be blocked. In addition,
when the payload content of normal messages is tampered with,
the tampered messages will cause false dashboard displays and
incorrect vehicle feedback operations. A detailed description of
these attacks models is as follows:
r Injection: The injection attack relies on the legitimate ID
to be effectively implemented. The attacker injects attack
messages with random IDs and payloads into the CAN bus.
The ECU will feedback when the injection ID is legitimate.
Subsequently, the legitimate ID can be used to generate
effective attacks to interfere with vehicle operations.
r Dos: Vulnerabilities in the CAN bus arbitration mechanism
are used to block the transmission of normal messages.
Messages with the highest priority ID = 0x000 are injected
into the CAN bus at frequency higher than the normal
message. Since illegal messages always occupy CAN bus
resources, other ECUs cannot transmit legal messages.
r Replay: Legitimate messages are collected and injected
into the CAN bus at random times. The ID and payload are
valid, but they do not comply with the temporal correlation
between ECUs.
r Drop: In an in-vehicle network, the gateway is responsible for connecting high-speed CAN and low-speed CAN
to transmit messages. An attacker can compromise and
control the gateway through external wireless or physical
access such as OBD-II Port. Then, the attacker can choose
to discard the messages of key ECUs, such as engine ECU,

WANG et al.: CAN BUS INTRUSION DETECTION BASED ON DEEP LEARNING WITH DATA AUGMENTATION

2259

TABLE I
CHARACTERISTICS OF DIFFERENT IDS

Fig. 7.

In-vehicle network simulation based on the CANOE.

battery management ECU and tire pressure monitoring
ECU, thus affecting the normal operation of the vehicle
[20].
r Tampering: In this attack, the meaning of the CAN message
is exposed to the attacker. The attacker can send an attack
message containing a specific ID and payload by manipulating a specific ECU. As a legitimate ECU periodically
transmits CAN messages with the same ID, the attack will
make the data receiving node confused, unable to identify
the legitimacy of the message. If the data receiving node
receives a tampered message and responds, the behavior of
vehicle may become abnormal.
3) Dataset: The dataset comes from two parts: one is the automotive controller area network bus intrusion dataset provided
by Dupont et al. [42] containing real vehicle data of two cars
(i.e., Renault Clio and Opel Astra) and abnormal data under five
attack scenarios of injection, DoS, replay, drop and tampering
attacks, the other is the simulation data generated by the CANOE
(A CAN bus analysis tool developed by Vector) simulation scenario. The CAN data packets are simulated and collected by the
CANOE, which consist of time sequences, ID, and payload data
with eight bytes. As shown in Fig. 7, there are three ECUs in the
CANOE simulation environment built in this article, including
engine, gateway, and NM_Tester_PT, which transmit messages
with 500 kbps CAN traffic. The IG module can customize the
message type and time interval, and simulate the ECU sending
messages to the CAN bus. The replay module can show the
saved CAN history messages. In the preprocessing stage, we
collect the original CAN traffic and group them into 12 different
IDs, representing different ECUs and nodes. The payload data of
each CAN ID carries information crucial for the operation of the
vehicle. Table I illustrates the characteristics of different IDs in
detail. To achieve the best validation loss, tree-structured Parzen
estimator is utilized to automatically choose the configuration of
hyper-parameter. The ranges of the hyper-parameter are given
in Table II.
B. Image Encoding Size
In the feature extraction stage, the CAN IDs and payload are
converted into images with widths of 48 and 256, respectively,
the height of these images remains undetermined. Therefore,

TABLE II
HYPER-PARAMETER SEARCH SPACE FOR BOTH GAN AND CLASSIFIER

Fig. 8.

Accuracy of the proposed IDS according to image size.

we analyze the relationship between the size of the CAN image
and the detection performance. Specifically, the image size is
increased from the minimum of 32 and 64 to the maximum of
128 and 1024, then we compare the accuracy and detection time
of the proposed IDS in different image sizes. When the size of
the spliced image is small, the image features are sparse and
the average processing time for each message is longer, so the
accuracy is lower and the detection delay is higher. As the image
size increases, the average processing time for each message
gradually decreases, but too large a spliced image size will
also lead to model overfitting and reduce detection accuracy. As
shown in Figs. 8 and 9, the results show that the best performance
is achieved when the sizes of CAN image are set to be 48 × 64
and 256 × 256, respectively.

2260

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 75, NO. 2, FEBRUARY 2026

TABLE III
STATISTICS COMPARISON

Table III shows the range of each byte of the three data, where
the EngPower signal is represented by the 1st and 2nd bytes,
the EngForce signal is represented by the 3rd and 4th bytes, the
PetroLevel signal is represented by the 5th byte, the IdelRunning
signal and the EngTemp signal are represented by the 6th byte,
the EngSpeed signal is represented by the 7th and 8th bytes. It
can be seen that the range of each signal of the generated data and
the attack data is close. The generated data conform to the attack
data format, and each signal value is within the real permitted
range. In addition, the mean difference between normal data,
attack data and generated data is close to 0, which means that the
byte range overlap between the three data is high. Furthermore,
the difference in variance is large, which means there are still
differences between the three data. The experimental results
verify the effectiveness of the generated attacks and show that the
generated attacks are accurate representations of actual attack.
Fig. 9.

Detection time of the proposed IDS according to image size.

D. Data Augmentation Analysis

Fig. 10.

The feature distribution map of normal data, attack data and real data.

C. Generated Data Analysis
To verify the effectiveness of the generated attacks, we use the
feature map to compare the distribution of normal data, attack
data and generated data. Due to the different scales of each
feature, the data is normalized using the min-max technique,
and then the frequency of the data features is counted. It can
be seen from Fig. 10 that the generated data has the probability
structure of the attack data, which is similar but not the same
as the normal data. Also, we evaluate the effectiveness of the
generated data using the range of each signal by comparing
the minimum, maximum, mean, and variance of the features.
In our case, we select ID = 0x064 engine data as an example.

1) Varying Balance Size: In order to analyze the contributions of the data augmentation module to the prediction performance, we vary the balance size of the training data. Specifically,
the percentage of attack data is increased from 0% (original
dataset) to 10%, 20%, 30%, 40% and 50%. The accuracy of
our proposed model, measured by varying the training balance
size in training set. As can be seen in Fig. 11, the proposed
method utilizes the data augmentation module to gain accuracy.
We note that the performance of all types of attacks improves
as the percentage of attacks data increases within the training
process. The performance of an intrusion detection model for
CAN bus can be improved with accuracy achieved is lower than
that on the percentage of attacks of 30%, but it is still higher than
the accuracy on the original dataset (balance size = 0%) when
no data augmentation has been performed. The results prove that
the detection performance is successfully improved by the data
augmentation module, enabling the model to detect previously
unseen attacks.
2) WGAN vs GAN vs SMOTE and ADASYS: Also, we analyze the effectiveness of the data augmentation module by comparing it with the representative data augmentation algorithms —
GAN, SMOTE and ADASYN. To do so, we train the proposed
model with three different data augmentation modules, which

WANG et al.: CAN BUS INTRUSION DETECTION BASED ON DEEP LEARNING WITH DATA AUGMENTATION

2261

TABLE IV
DETECTION PERFORMANCE COMPARED TO BASELINE AND EXISTING WORKS
RESULTS IN FIVE ATTACK SCENARIOS

Fig. 11. Accuracy performane (axis Y), measured by varying the size of the
balance (axis X) – the percentage of attacks on the entire training set – between
0% (original dataset) to 10%, 20%, 30%, 40% and 50% (augmented dataset).

Fig. 12. Accuracy performance (axis Y), measured with WGAN, GAN,
SMOTE and ADASYN on the balance size of 50%.

are denoted as GAN, SMOTE and ADASYN. The only difference between them is that the WGAN-based data augmentation
is replaced with GAN, SMOTE and ADASYN, respectively. As
can be seen in the Fig. 12, the WGAN-based data augmentation
module provided in our proposed method perform better than
the representative data augmentation algorithms in terms of ac
curacy, which may be related to the defects of these techniques.
GAN suffers from gradient explosion problem. SMOTE based
on the nearest neighbor method is easy to cause data redundancy.
ADASYN based on τ distribution is susceptible to outliers.
E. Comparison to Other Algorithms
The baseline methods are representative classification methods, which are OCSVM, iForest, and a deep learning-based
model called LSTM-AE. Furthermore, we compare the proposed
model with three existing works (GPIDS, X-CANIDS, CanNet)
discussed in Section II under five attack scenarios. We compare
the detection performance of our proposed model for CAN bus
with the baseline and existing works. The proposed LSTM-CNN
and baseline methods are trained using public datasets and
simulated datasets. Since the simulation of a CAN bus only
generates normal CAN traffic, there is no attack data in the

original simulated datasets. Therefore, we use the IG module to
customize the message type and time interval, and simulate the
ECU sending abnormal messages to the CAN bus. In addition,
the labelled LSTM-CNN and LSTM-AE methods are trained
using public datasets, simulated datasets and generated datasets
to evaluate the performance improvements of models trained
with augmentation datasets.
The performance of these models for CAN traffic intrusion
detection is shown in Table IV. It can be observed that the
proposed method performs better than the baselines and existing
works. We can see that the proposed method can extract the
temporal correlation of CAN messages contents, and it can
reach high accuracy over all types of attacks. Generally, the
average accuracy of the proposed method is 99.78%, and the

2262

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 75, NO. 2, FEBRUARY 2026

TABLE V
RESOURCES CONSUMPTION COMPARED TO EXISTING WORKS RESULTS

Fig. 13.

average score of F1 is 99.74%. Although the detection performance of the proposed method in injection attack is slightly
lower than that of the X-CANIDS method, and the detection
performance in Dos and replay attacks is slightly lower than that
of the CanNet method, the accuracy of our proposed method for
these attacks is still above 99.8%. Compared with the model
that trained using public datasets and simulated datasets, we
note that the accuracy of LSTM-CNN and LSTM-AE methods,
which are trained with the balanced dataset that contains public
datasets, simulated datasets and generated datasets, improved
significantly by 56.54% (from 63.74% to 99.78%) and 50.17%
(from 60.48% to 90.82%), respectively. The result proves that the
data augmentation module implemented in our proposed model
successfully improve the detection performance for CAN bus by
generating high-quality attack samples. OCSVM and iForest,
which are trained without generated data, show poor performance for CAN bus intrusion detection. Though the detection
performance of the proposed method for tampering attacks is
the worst among all types of attacks scenarios, it is still better
than the other methods in Table IV. In future, the detection
of tampering attacks will be a more challenging issue. Before
tampering attacks occurs, the attacker listens and sniffs packet
on a CAN bus. Reverse engineering technique is then used to
identify the corresponding messages of each ECU. The attacker
manages to override messages sent to brakes, gears, and engine
and displayed fake speedometer readings on the dashboard. Even
so, the accuracy of our proposed model in detecting tampering
attacks is still higher than the baselines and above 99 percent.
F. Efficiency Evaluation
To evaluate whether our proposed method is suitable for
CAN bus in real vehicles, we compare the proposed model
with three existing works based on the resource consumption.
Table V show the comparison of the proposed intrusion detection
model with existing works in terms of memory footprint and
average detection time per CAN frame. It can be observed that
the footprint of our proposed LSTM-CNN model is smaller
than GPIDS, X-CANIDS and CanNet, and the proposed model
still has less detection time. Compared with the X-CANIDS,
the representative model proposed above, the F1-score of our
proposed model is improved by 15.25%, and the detection time
of our proposed model is reduced by 29.11%. As a lightweight
model, our proposed intrusion detection system for CAN bus
can efficiently detect all types of attacks with better detection

The hardware architecture of the proposed equipment.

performance. In the simulation experiment, the waiting time
for collecting frames is not factored in the detection time since
the datasets are offline. The experimental results show that the
detection time of our proposed model is 0.56 ms, which means
that 1785 physical signals of different ECUs can be predicted
in one second. Therefore, while our proposed model achieves
a high accuracy-score, it also only consumes lower memory
and less detection time, so the proposed IDS is better suited for
in-vehicle networks with constrained resources and detection
time.
V. INTRUSION DETECTION EQUIPMENT
A. Hardware Architecture
The proposed equipment is designed to be deployed in a gateway or an onboard unit that can receive all CAN messages. The
detection performance of our proposed equipment can be used as
a baseline to evaluate the detection performance of vehicles. The
architecture of Windows system and microcomputer hardware
is typically adopted by such testing equipment, which aligns
with our proposed equipment. The size of the equipment is
430 mm × 400 mm × 215 mm. Fig. 13 shows the complete hardware architecture, which consists a CAN bus receiving module,
a CAN bus attack sending module, and an onboard computing
module. The main function of this equipment is to detect attacks
and achieve simulation on a real CAN bus. Two micro controllers
of STM32F103s are used to establish communication between
the equipment and the CAN bus. The first microcontroller is
used as the CAN bus receiving module to automatically match
the vehicle CAN bus rate and receive CAN messages. The
second one is used as the CAN bus attack sending module,
which is responsible for injecting attack messages generated
by the onboard computing module into the vehicle CAN bus,
or inputting instructions to filter specified ID messages into the
CAN bus receiving module to achieve shielded transmission
of specific ECU messages. A microcomputer is introduced as
the onboard computing module, equipped with Intel(R) Core
(TM) i3-9100H @ 3.10 GHz, which stores the proposed model
and the visualization software. The onboard computing module
is responsible for intrusion detection according to the received
CAN messages and generating specified types of attack messages. One end of the two STM32F103 is connected to the
onboard computing module via the UART (Universal Asynchronous Receiver/Transmitter), and the other end is directly

WANG et al.: CAN BUS INTRUSION DETECTION BASED ON DEEP LEARNING WITH DATA AUGMENTATION

Fig. 14.

2263

The software architecture of the proposed equipment.

connected to the vehicle OBD-II port. The proposed equipment
involves two communication stages. The communication baud
rate between the vehicle and the CAN bus receiving module is
921600. The UART baud rate between the CAN bus receiving
module and the onboard computing module is also 921600. In
the vehicle testing scenario, attack messages are injected into the
in-vehicle network via the CAN bus attack sending module to
test whether the vehicle and the proposed method can accurately
identify the attacks. The detection performance of the vehicle is
evaluated by comparing the test results. This equipment is only
involved in intrusion detection and does not participate in the
training of neural networks. In the experiments of this article,
the training of the model network relies on the AMD-based PC.
Currently, this type of equipment includes detection prototypes
and onboard real-time detection devices. The proposed equipment is a detection prototype. In order to facilitate experimental
operation and debugging, and display CAN traffic flow, a 13
inches display screen is added, and a software interface is
designed to visualize the entire algorithm process. These are
also the differences compared to existing equipment. However,
more and more vehicles are incorporating CAN-FD running at
speeds higher than 1 Mbps. The use of UART for relaying CAN
messages can still be a communication bottleneck which limits
the applicability of the current setup to standard CAN. Therefore,
the proposed model is also transplanted to automotive embedded
devices, and we test the performance of the proposed model on
two real vehicles.
B. Software Architecture
Each module of the equipment collaborates to perform vehicle testing. The equipment performs online detection of the
CAN bus network, and simulates attacks in a real vehicle. The
software consists of CAN bus communication establishment,
data preprocessing, attacks detection and simulation. The test
steps of the software are shown in the Fig. 14. To begin with,
the communication between the equipment and the CAN bus is
established. Then, the messages are extracted from the CAN bus
and categorized based on their CAN IDs. After that, the CAN

Fig. 15.

The main configuration screen of the software.

IDs are converted into images and the payload of each CAN ID
is processed as time series data. The IDS take these data as input
for attack detection and flags anomalies once they are detected.
If no attack occurs, the IDS continues to collect messages
on the CAN bus and detect attacks. Additionally, the attacks
data can be generated by the onboard computing module and
injected into the CAN bus to simulate intrusion. The intrusion
detection model development environment is python3.9.7 and
tensorflow2.7.0. The software is developed based on QT and
can run across platforms to facilitate Fig. 15.
C. Online Detection Evaluation for Real Vehicles
In order to evaluate the effectiveness of the proposed equipment, we performed real vehicle experiments, testing our proposed equipment on a real vehicle (RAV4). The connection
between experimental components on the vehicle is shown in
Fig. 16(a). As can be seen in this figure, the equipment is
connected to the in-vehicle CAN networks through the OBD-II
port of the real vehicle. The bandwidth of the real vehicle is
automatically recognized by the CAN bus receiving module
as 500 kbps. Since the tested vehicle is not equipped with an
embedded intrusion detection device, we test the performance
of the proposed equipment by artificially generating attacks
and injecting them into the in-vehicle network. We access the
CAN bus and perform all types of attacks through the CAN bus
receiving module and the CAN bus attack sending module.
Due to the computing power of ECUs is differ from a PC, and
intrusion detection for in-vehicle network is limited- resources.
Furthermore, we test the detection performance of our model on
the automotive embedded devices in two real vehicles (Volkswagen and Dongfeng). The Volkswagen is equipped with a domain
controller APEX AD10, and the Dongfeng is equipped with a
domain controller GEACX2, as shown in Fig. 16(b) and (c). Both
the APEX AD10 and the GEACX2 are equipped with a Jetson

2264

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 75, NO. 2, FEBRUARY 2026

Fig. 16. Test setup on the real vehicle. (a) A RAV4 equipped with a PC. (b) A Volkswagen equipped with an APEX AD 10. (c) A Dongfeng equipped with a
GEACX2.

Fig. 17.

Average recall, precision, F1 score and accuracy values for online detection on different platforms.

AGX Orin 32GB processor module, which includes 8 Core ARM
Cortex-A78 @ 2.2 GHz and NVIDIA Ampere 1792-CUDA
Core. Specifically, we cross-platform port the software containing the proposed model to the APEX AD10 and the GEACX2,
respectively. Due to safety issues, we perform the experiment
while the vehicle is in standby state. The CAN messages consist
of different signals, including door locks, headlights, wipers,
and so on. The details of attacks we simulated are illustrated as
follows:
r Injection: CAN messages with illegal ID are injected into
the CAN bus to disrupt the operations of vehicles and collect vital commands. The CAN ID is randomly generated
from 0x001 to 0x7ff.
r Dos: CAN messages with the highest priority ID = 0x000
are injected into the CAN bus at high frequency (ie, sending
period = 1 ms). The normal traffic is blocked because the
abnormal traffic takes over the CAN bus.

r Replay: we collect normal messages and inject them into
the CAN bus at random times. Due to the attack data is
extracted from the normal CAN traffic, it is challenging
for IDS to distinguish between authentic and fraudulent
messages.
r Drop: we filter the CAN messages with specified ID based
on the CAN bus receiving module, then, specific ECU
messages are discarded.
r Tampering: we first collect real vehicle CAN message data,
select the specified message ID by analyzing the message
sending cycle, modify the data field value of the specified
message, and inject it into the real vehicle CAN bus through
the CAN bus attack sending module.
The average detection performance of our proposed model on
different platforms is shown in Fig. 17. It can be observed that
our proposed method shows good detection performance over
all types of attacks. We note that the experiment results of our

WANG et al.: CAN BUS INTRUSION DETECTION BASED ON DEEP LEARNING WITH DATA AUGMENTATION

2265

TABLE VI
THE RESOURCES CONSUMPTION OF THE MODEL ON REAL VEHICLE

proposed method achieve the best accuracy in Dos attack. The
main reason is that the transmission of legitimate messages in
the CAN bus is blocked by the highest priority messages sent
in DoS attacks. Since DoS attacks will cause great fluctuations
in CAN traffic, it is easy to detect DoS attacks. The result proves
that our proposed model can achieve high detection accuracy in
the case of resource-constrained and extremely limited attack
samples, making it easier to be adapted to different vehicles
from various manufacturers. In the real-vehicle experiment, the
frame collection time is factored in the detection time. For
the first message, we need to wait for window initialization to
collect 63 more successive messages to come to a conclusion.
When the window initialization is completed, each subsequent
message can be detected by updating the window. The window
initialization time and message collection time of the proposed
IDS on different platforms are shown in Table VI. It can be
observed that the detection time of the proposed model on PC,
APEX AD10 and the GEACX2 is 0.82 ms, 1.12 ms and 1.14 ms,
respectively. In addition, the average window initialization time
is 26.05 ms, and the average message collection time is 0.42 ms.
The experimental results show that the proposed IDS achieves
high detection accuracy and low detection time in a resource
limited and data imbalanced environment, which is close to the
offline detection performance on a PC, so the proposed model
is suitable for real vehicles.
VI. CONCLUSION
In this paper, one deep learning-based intrusion detection
system framework is proposed for in-vehicle CAN bus network, including WGAN-GP data augmentation module and
LSTM-CNN prediction module. CAN messages are used as
input for WGAN-GP to automatically generate high-quality
attack data and balance training data. The prediction module
consists of two networks, one based on CNN and the other on
LSTM. The CNN module is trained to detect anomalies based
on the image form of the samples, which takes advantage of the
spatial contiguity in CAN traffic. The LSTM module istrained
to detect anomalies using the temporal correlation of time series
data. The results of the experiments, performed on a simulated
dataset generated through the CANOE simulation, show that
the proposed method can effectively detect CAN attacks, with
an average F1-score of 99.74% and an accuracy of 99.78%.
Compared with the work in the related research fields, the
F1-score of attack detection is improved by 15.25%, and the
detection time is reduced by 29.11%. The result demonstrate that
the model trained by our proposed method has greatly improved
the detection performance in the case of limited resource and
extremely data imbalance. Furthermore, an intrusion detection
equipment is developed to detect and simulate online attacks on a

real vehicle. We also test the detection performance of our model
on two domain controllers. The result proves that the proposed
method is reliable and robust, making it easier to be adapted to
different vehicles from various manufacturers.
REFERENCES
[1] H. J. Jo and W. Choi, “A survey of attacks on controller area networks
and corresponding countermeasures,” IEEE Trans. Intell. Transp. Syst.,
vol. 23, no. 7, pp. 6123–6141, Jul. 2022.
[2] W. Wu et al., “A survey of intrusion detection for in-vehicle networks,”
IEEE Trans. Intell. Transp. Syst., vol. 21, no. 3, pp. 919–933, Mar. 2020.
[3] G. Karopoulos, G. Kambourakis, E. Chatzoglou, J. L. Hernández-Ramos,
and V. Kouliaridis, “Demystifying in-vehicle intrusion detection systems:
A survey of surveys and a meta-taxonomy,” Electronics, vol. 11, no. 7,
Mar. 2022, Art. no. 1072.
[4] K. Ren, Q. Wang, C. Wang, Z. Qin, and X. Lin, “The security of autonomous driving: Threats, defenses, and future directions,” Proc. IEEE,
vol. 108, no. 2, pp. 357–372, Feb. 2020.
[5] T. H. H. Aldhyani and H. Alkahtani, “Attacks to automatous vehicles:
A deep learning algorithm for cybersecurity,” Sensors, vol. 22, no. 1,
Jan. 2022, Art. no. 360, doi: 10.3390/s22010360.
[6] G. Dupont, J. Den Hartog, S. Etalle, and A. Lekidis, “A survey of network
intrusion detection systems for controller area network,” in Proc. IEEE
Int. Conf. Veh. Electron. Saf., 2019, pp. 1–6.
[7] N. Khatri, R. Shrestha, and S. Y. Nam, “Security issues with in-vehicle networks, and enhanced countermeasures based on blockchain,” Electronics,
vol. 10, no. 8, Apr. 2021, Art. no. 893, doi: 10.3390/electronics10080893.
[8] K. Koscher et al., “Experimental security analysis of a modern automobile,” in Proc. IEEE Symp. Secur. Privacy, 2010, pp. 447–462.
[9] S. Rajapaksha, H. Kalutarage, M. O. Al-Kadri, A. Petrovski, G. Madzudzo,
and M. Cheah, “AI-based intrusion detection systems for in-vehicle
networks: A survey,” ACM Comput. Surveys, vol. 55, no. 11, pp. 1–40,
Nov. 2023.
[10] K. Wang, A. Zhang, H. Sun, and B. Wang, “Analysis of recent deeplearning-based intrusion detection methods for in-vehicle network,” IEEE
Trans. Intell. Transp. Syst., vol. 24, no. 2, pp. 1843–1854, Feb. 2023.
[11] F. Amato, L. Coppolino, F. Mercaldo, F. Moscato, R. Nardone, and A.
Santone, “CAN-bus attack detection with deep learning,” IEEE Trans.
Intell. Transp. Syst., vol. 22, no. 8, pp. 5081–5090, Aug. 2021.
[12] E. Aliwa, O. Rana, C. Perera, and P. Burnap, “Cyberattacks and countermeasures for in-vehicle networks,” ACM Comput. Surveys, vol. 54, no. 1,
pp. 1–37, Jan. 2022.
[13] H. Lee, S. H. Jeong, and H. K. Kim, “OTIDS: A novel intrusion detection
system for in-vehicle network by using remote frame,” in Proc. 15th Annu.
Conf. Privacy, Secur. Trust, 2017, pp. 57–5709.
[14] H. M. Song and H. K. Kim, “Self-supervised anomaly detection for
in-vehicle network using noised pseudo normal data,” IEEE Trans. Veh.
Technol., vol. 70, no. 2, pp. 1098–1108, Feb. 2021.
[15] H. Zhang, L. Huang, C. Q. Wu, and Z. Li, “An effective convolutional
neural network based on SMOTE and Gaussian mixture model for intrusion detection in imbalanced dataset,” Comput. Netw., vol. 177, Aug. 2020,
Art. no. 107315.
[16] S.-Y. Bae, J. Lee, J. Jeong, C. Lim, and J. Choi, “Effective data-balancing
methods for class-imbalanced genotoxicity datasets using machine learning algorithms and molecular fingerprints,” Comput. Toxicol., vol. 20,
Nov. 2021, Art. no. 100178.
[17] V. Kumar and D. Sinha, “Synthetic attack data generation model applying
generative adversarial network for intrusion detection,” Comput. Secur.,
vol. 125, Feb. 2023, Art. no. 103054.
[18] L. Yuan, S. Yu, Z. Yang, M. Duan, and K. Li, “A data balancing approach
based on generative adversarial network,” Future Gener. Comput. Syst.,
vol. 141, pp. 768–776, Apr. 2023.

2266

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 75, NO. 2, FEBRUARY 2026

[19] R. S. Rathore, C. Hewage, O. Kaiwartya, and J. Lloret, “In-vehicle communication cyber security: Challenges and solutions,” Sensors, vol. 22,
no. 17, Sep. 2022, Art. no. 6679.
[20] H. Sun, M. Chen, J. Weng, Z. Liu, and G. Geng, “Anomaly detection for
in-vehicle network using CNN-LSTM with attention mechanism,” IEEE
Trans. Veh. Technol., vol. 70, no. 10, pp. 10880–10893, Oct. 2021.
[21] H. M. Song, J. Woo, and H. K. Kim, “In-vehicle network intrusion detection using deep convolutional neural network,” Veh. Commun., vol. 21,
Jan. 2020, Art. no. 100198.
[22] E. Seo, H. M. Song, and H. K. Kim, “GIDS: GAN based intrusion detection
system for in-vehicle network,” in Proc. 16th Annu. Conf. Privacy, Secur.
Trust, 2018, pp. 1–6.
[23] M. Gmiden, M. H. Gmiden, and H. Trabelsi, “An intrusion detection
method for securing in-vehicle CAN bus,” in Proc. 17th Int. Conf. Sci.
Techn. Autom. Control Comput. Eng., 2016, pp. 176–180.
[24] A. Taylor, N. Japkowicz, and S. Leblanc, “Frequency-based anomaly
detection for the automotive CAN bus,” in Proc. World Congr. Ind. Control
Syst. Secur., 2015, pp. 45–49.
[25] M. Muter and N. Asaj, “Entropy-based anomaly detection for in-vehicle
networks,” in Proc. IEEE Intell. Veh. Symp. (IV), 2011, pp. 1110–1115.
[26] W. Wu et al., “Sliding window optimized information entropy analysis
method for intrusion detection on in-vehicle networks,” IEEE Access,
vol. 6, pp. 45233–45245, 2018.
[27] T. Koyama, T. Shibahara, K. Hasegawa, Y. Okano, M. Tanaka, and Y.
Oshima, “Anomaly detection for mxed transmission CAN messages using
quantized intervals and absolute difference of payloads,” in Proc. ACM
Workshop Automot. Cybersecur., 2019, pp. 19–24.
[28] M. L. Han, B. I. Kwak, and H. K. Kim, “Anomaly intrusion detection
method for vehicular networks based on survival analysis,” Veh. Commun.,
vol. 14, pp. 52–63, Oct. 2018.
[29] O. Avatefipour et al., “An intelligent secured framework for cyberattack
detection in electric vehicles’ CAN bus using machine learning,” IEEE
Access, vol. 7, pp. 127580–127592, 2019.
[30] X. Duan, H. Yan, D. Tian, J. Zhou, J. Su, and W. Hao, “In-vehicle CAN
bus tampering attacks detection for connected and autonomous vehicles
using an improved isolation forest method,” IEEE Trans. Intell. Transp.
Syst., vol. 24, no. 2, pp. 2122–2134, Feb. 2023.
[31] M.-J. Kang and J.-W. Kang, “Intrusion detection system using deep
neural network for in-vehicle network security,” PLoS One, vol. 11, no. 6,
Jun. 2016, Art. no. e0155781.
[32] A. Taylor, S. Leblanc, and N. Japkowicz, “Anomaly detection in automobile control network data with long short-term memory networks,” in
Proc. IEEE Int. Conf. Data Sci. Adv. Analytics, 2016, pp. 130–139.
[33] J. Zhang et al., “A deep learning framework for driving behavior identification on in-vehicle CAN-BUS sensor data,” Sensors, vol. 19, no. 6,
Mar. 2019, Art. no. 1356.
[34] J. Qin, Y. Xun, Z. Deng, and J. Liu, “GPIDS: GAN assisted contextual
pattern-aware intrusion detection system for IVN,” IEEE Trans. Veh.
Technol., vol. 73, no. 9, pp. 12682–12693, Sep. 2024.
[35] S. Jeong, S. Lee, H. Lee, and H. K. Kim, “X-CANIDS: Signal-aware explainable intrusion detection system for Controller area network-based Invehicle network,” IEEE Trans. Veh. Technol., vol. 73, no. 3, pp. 3230–3246,
Mar. 2024.
[36] S. Gao, L. Zhang, L. He, X. Deng, H. Yin, and H. Zhang, “Attack detection for intelligent vehicles via CAN-bus: A lightweight image network
approach,” IEEE Trans. Veh. Technol., vol. 72, no. 12, pp. 16624–16636,
Dec. 2023.
[37] G. Guo, Q. Xu, and C.-L. Zhang, “Adaptive fixed-time prescribed performance control of non-smooth systems subject to injection/deception
attacks,” IEEE Trans. Automat. Sci. Eng., vol. 22, pp. 12645–12654, 2025.
[38] J. Liu, G. Guo, X. Sun, Z. Li, and H. Lin, “Cooperative localization of
connected vehicles with attack detection and secure fusion,” IEEE Trans.
Veh. Technol., vol. 74, no. 4, pp. 5713–5723, Apr. 2025.
[39] I. Goodfellow et al., “Generative adversarial networks,” Commun. ACM,
vol. 63, no. 11, pp. 139–144, Oct. 2020.
[40] S. Cui and Y. Jiang, “Effective lipschitz constraint enforcement for wasserstein GAN training,” in Proc. 2nd IEEE Int. Conf. Comput. Intell. Appl.,
2017, pp. 74–78.
[41] I. Gulrajani, F. Ahmed, M. Arjovsky, V. Dumoulin, and A. C. Courville,
“Improved training of wasserstein GANs,” in Proc. 31st Int. Conf. Neural
Inf. Process. Syst., 2017, pp. 5767–5777.
[42] D. Basavaraj and S. Tayeb, “Towards a lightweight intrusion detection
framework for in-vehicle networks,” JSAN, vol. 11, no. 1, p. 6, Jan. 2022,
doi: 10.3390/jsan11010006.

Xiang Wang received the B.S. degrees in vehicle engineering from the Wuhan University of Science and
Technology, Wuhan, China, in 2022. He is currently
working toward the Ph.D. degree in vehicle engineering with the Dalian University of Technology, Dalian,
China. His research interests include connected autonomous vehicles, cybersecurity, machine learning,
and anomaly detection.

Jian Zhao (Member, IEEE) received the B.S. degree
from the Guilin University of Electronic Technology,
Guilin, China, in 2003 and the M.S. and Ph.D. degrees in mechatronics from Xidian University, Xi’an,
China, in 2006 and 2008, respectively. He is currently
a Postdoctoral with the Johannes Kepler University
of Linz, Linz, Austria. He is also a Professor with
the State Key Laboratory of Structural Analysis for
Industrial Equipment, Dalian University of Technology, China. He has got financial support from the
National Science Foundation of China, the Ministry
of Education of China, the National Key Research and Development Program,
and industries. He has authored or coauthored more than 100 articles in research
fields of automotive sensors, intelligent vehicles, and MEMS. He was granted
50 Chinese patents. He was also elected as a Technical Committee Member
of the Chinese Society of Micro-Nano Technology and a member of the National Standard Committee for Audio and Video. He was the recipient of the
Excellent Young Scientist, Xinghai Excellent Youth from the Dalian University
of Technology, Qianlingxi Excellent Teacher Award, Second Prize for Science
and Technology Achievement from the China Academy of Engineering Physics,
First Prize of Excellent Technical Research Papers, Special Award of Excellent
Technical Research Papers in Dalian City, and Best Paper Award elected by
Chinese Journal of Sensors and Actuators. He was also elected as the Program
Chair of the 2022 ASME MNS and the Conference Chair of 2023 ASME MNS.

Pengbo Liu received the Ph.D. degree in microelectronics and solid-state electronics from the Dalian
University of Technology, Dalian, China, in 2015.
He is currently a Senior Engineer with the College of
Automotive Engineering, Dalian University of Technology. His research interests include automobile sensors, and intelligent connected vehicle.

Nianmin Yao received the B.E., M.S., and Ph.D.
degrees from Jilin University, Changchun, China, in
1997, 2000, and 2003, respectively. He is currently
a Professor with the Dalian University of Technology, Dalian, China. He has been a Visiting Scholar
at the University of Connecticut, Storrs, CT, USA.
His primary research interests include machine learning, wireless sensor networks, and wireless network
security.

Zheng Xu received the B.S. degree in vehicle engineering from the Hefei University of Technology,
Hefei, China, in 2021. He is currently working toward the Ph.D. degree in vehicle engineering with
the Dalian University of Technology, Dalian, China.
His research interests include vehicle navigation and
positioning technology, particularly in sensor data
fusion, inertial navigation, and GNSS/INS integrated
navigation.
PAPER_TEXT
