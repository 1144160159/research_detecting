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
# [344] A Novel Hybrid, BERT and Deep Learning Model Network Intrusion Detection System for Healthcare Electronics
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
编号：344
题名：A Novel Hybrid, BERT and Deep Learning Model Network Intrusion Detection System for Healthcare Electronics
年份：2024
DOI：10.1109/tce.2024.3412199
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2024.3412199.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\344.txt
- 原始字符数：45939
- 本次发送字符数：45939
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1322

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

A Novel Hybrid, BERT and Deep Learning Model
Network Intrusion Detection System for
Healthcare Electronics
Ali Alferaidi, Kusum Yadav , Yasser Alharbi , Eissa Jaber Alreshidi, Abdulrahman Alreshidi ,
Bassam W. Aboshosha , Rohit Sharma , Ahmed Alkhayyat , and Daniel Gavilanes Aray

Abstract—IoMT has become an attractive playground for
cybercriminals due to its market value and rapid growth. As the
amount of sensitive data transmitted across IT infrastructures
grows, healthcare organizations and companies that generate
wearable data become targets for attackers. Recently, government
agencies and healthcare organizations have prioritized collecting
this data and using machine learning to protect users’ privacy.
In all test cases, the proposed method performed better than
any other method, including the IoMT intrusion dataset, with an
accuracy increase of 2.9%. It can also monitor IoMT networks
within the healthcare and medical environment to protect IoMT
devices and networks from attackers. Based on the ECU-IoHT
dataset, it achieves 99% performance improvement in accuracy,
precision, recall, and F1-score compared with existing anomaly
detection models. The proposed model shows higher detection
accuracy than the existing latest state-of-arts.
Index Terms—IoMT, wearable electronics devices, detection
systems.

I. I NTRODUCTION
OBILE devices and wearables have accelerated Internet
of Things (IoT) technologies in healthcare. In addition
to real-time human activity monitoring, wearables and mobile
sensors can enhance medical rehabilitation and elderly care.
Therefore, gain insight into people’s daily behaviours and

M

Manuscript received 10 December 2023; revised 24 March 2024; accepted
1 June 2024. Date of publication 11 June 2024; date of current version
12 June 2025. This work was supported by the Scientific Research Deanship
at the University of Ha’il – Saudi Arabia Ha’il, Saudi Arabia, under Project
RG-21 104. (Corresponding author: Rohit Sharma.)
Ali Alferaidi, Kusum Yadav, Yasser Alharbi, Eissa Jaber Alreshidi,
and Abdulrahman Alreshidi are with the College of Computer Science
and Engineering, University of Ha’il, Hail 81481, Saudi Arabia
(e-mail: a.alfredi@uoh.edu.sa; y.kusum@uoh.edu; y.alharbi@uoh.edu.sa;
e.alreshidi@uoh.edu.sa; ab.alreshidi@uoh.edu.sa).
Bassam W. Aboshosha is with the Department of Communication and
Computer Engineering, Higher Institute of Engineering, El-Shorouk Academy,
El-Shorouk City 11937, Egypt (e-mail: bassam.ahmed32@gmail.com).
Rohit Sharma is with the Department of Electronics and Communication
Engineering, ABES Engineering College, Ghaziabad 201009, India (e-mail:
rohitapece@gmail.com).
Ahmed
Alkhayyat
is
with
the
College
of
Technical
Engineering, The Islamic University, Najaf 54001, Iraq (e-mail:
ahmedalkhayyat85@gmail.com).
Daniel Gavilanes Aray is with the Engineering Research and Innovation
Group, Universidad Europea del Atlántico, 39011 Santander, Spain, also with
the Engineering Research and Innovation Group, Universidad Internacional
Iberoamericana, Campeche 24560, Mexico, and also with the Department
of Project Management, Fundación Universitaria Internacional de Colombia,
Bogotá 111311, Colombia.
Digital Object Identifier 10.1109/TCE.2024.3412199

Fig. 1.

The architecture of the IOMT system.

interactions using Human Activity Recognition (HAR) in
ubiquitous computing environments. These developments have
led to extensive research on the Internet of Healthcare Things
(IoHT) [1], [2]. In real-time, wireless sensor networks can
collect and transmit posture data (e.g., accelerometers and
gyroscopes) from various body parts (e.g., heads, chests, upper
arms, forearms, shins, etc). (For instance, wearable devices
such as inertial sensors and smartphones are examples.) [3].
As a result of sensor technologies, it may be possible for
HAR to become more robust when it comes to sensing and
fusion of multimodal data, enabling us to create applications
and services based on real-time big data environments that
enhance sensed information for human-centred applications
and services [4], [5], [6].
It adheres to a three-tier architectural framework for IoT
applications that comprises perception, network, and transmission layers as a focused personification of IoT in the medical
area. As shown in Figure 1, the IoMT architecture is based on
the cloud.
Wearable’s and mobile devices have built-in inertial sensors,
which can easily gather motion data from people’s physical
activities. It is common to use smart devices to recognize,
analyze, and understand the status of a person across a variety
of different environments in a wide range of applications and
systems [7], [8], [9]. HAR relies heavily on sensor data, but
several challenges can be overcome. It is essential to design
well-labelled datasets to extract features that are effective in
machine learning methods [10]. Although people may not use
smart devices to perform sensible actions, built-in sensors on
those devices continuously generate ADL data. As a result,
annotating and recording well-labelled data is labour-intensive.
Data collected by wearable sensors that are weakly labelled

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1558-4127 
See https://www.ieee.org/publications/rights/index.html for more information.

ALFERAIDI et al.: NOVEL HYBRID, BERT AND DEEP LEARNING MODEL NETWORK INTRUSION DETECTION SYSTEM

Fig. 2.

The IOMT network.

refers to data that is mostly unlabelled, with only a few
segments labelled [11], [12], [13]. Hence, a weakly supervised
or semisupervised learning framework is the best way to
handle such situations. The diagram in Figure 2 illustrates an
example of medical devices connected to a hospital network.
Today’s Machine learning is often called privacypreserving [14], [15]. To circumvent privacy concerns,
Google [16] proposes federated learning [17], which leverages
collaborative learning across IoT devices (Internet of Things).
Due to various constraints, IOT applications are difficult to
implement using traditional federated learning and central
servers. As a result, all IoT devices will have a significant
decline in accuracy as a result of a crash or malicious modification of the global model by the central server (e.g., Edge
server) [18], [19], [20], [21], [22], [23], [24]. The federation
of learning is hampered by the lack of power in IoT devices.
Due to this resource limitation, federated learning must be
implemented with optimized energy consumption [25].
For example, federated learning has been highly successful in optimizing mobile edge networks, suggesting
and predicting Google keyboard queries [26], [27], detecting
COVID-19 [28], [29], [30], facilitating vehicle communication [31], [32], the Internet of Drones [33], Intrusion detection,
Augmented Reality, [34], [35], [36] etc. Often, researchers
have difficulty deciding which type of learning method will be
most advantageous for testing and evaluating their proposed
security methods in IoT applications (e.g., centralized or
federated learning). It makes selecting the right method of
federated deep learning crucial. Taking advantage of the new
capabilities in federated deep learning, we plan to conduct an
experimental study with a comprehensive approach to better
understand IoT security through federated deep learning.
Information and networks are protected from cyber-attacks
through cyber security. An IoHT attack detection method
must be developed [37]. Due to safety risks and the potential
for harm and death, these attack datasets are not publicly
available [38]. Our methodology addresses these risks using
a novel ECU-IoHT dataset [38]. Various cyberattacks are
reflected in this report. Based on these issues, this paper
presents a deep learning-based system to detect an extensive
range of cyberattacks. Unlike existing approaches, this system
can detect ARP spoofing, Denial of Service (DoS) attacks,
Nmap port scans, and Smurf attacks in the Internet of
Things [38]. Considering the types of attacks observed in the

1323

IoHT environment, this deep learning approach appears to be
the most effective method of multiclass classification in the
IoHT environment to date.
This paper contributes the following contributions
• It is more important to detect different types of attacks
than specific attacks in the IoHT environment using a
hybrid model using BERT and deep learning.
• The proposed method trains and evaluates the model
using the ECU-IoHT dataset in the healthcare domain.
Since many publicly available datasets are inappropriate
for health care, the ECU-IoHT dataset was selected.
• The accuracy of the intrusion detection rate achieved
by BERT and Deep Learning-based intrusion detection
systems was 99.11% for five frequently occurring intrusions.
The paper is organized into five sections. Work related to the
topic is presented in Section II. Section III presents how the
model is mathematically analyzed and calculated. A detailed
description of the experimentation procedures, results analysis,
and performance evaluation can be found in Section IV. The
paper is concluded in Section V.
II. L ITERATURE R EVIEW
Recent theories suggest that using new technologies for
mutual benefit is crucial to economic growth. This definition
explains why Japanese Society 5.0 refers to an organization
that uses technologies and organizations to improve the world
through connected objects, big data, and artificial intelligence [39], [40]. We live in a changing world in this new era
of globalization and technological advancement. The evolution
also directly affects vertical markets and society. Values also
change with the diversity and complexity of citizens and the
environment. Digital technologies are at the heart of Industry
4.0, Made in China 2025, and Society 5.0 revolutions are
happening worldwide. The wave of digital transformation is
driving all of these activities.
The industrial strategy is flattering and reliant on digital
transformation [41], [42]. Due to this transformation, most
industrial applications and companies have completely transformed. New work models require employees who understand
and can use them. Hence, mastering process digitization,
redefining business lines, and integrating data within the
organization are the pillars of this transformation.
Several recent proposals have proposed how patients can
be monitored and assessed in real-time [43], [44], [45],
[46]. A framework for detecting and evaluating stress is
presented [46]. Based on patient vitals, breathing rate, heart
rate, and average blood pressure, stress signals are first
detected using skin conductance parameters and then estimated
stress levels using fuzzy inference systems. A study [43]
proposes a framework for managing healthcare data and
making informed decisions. An algorithm is in place to detect
emergencies and send critical records directly to the coordinator. Sensors are sampled at different frequencies according
to ANOVA and Fisher tests, which adjust the sampling rate
based on patient health conditions. A fuzzy set theory-based
decision matrix is proposed at the coordinator for data fusion

1324

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

and decision-making. This framework has many disadvantages
despite its advantages when it comes to patient assessment
and monitoring: 1) A medical staff cannot prevent patients
from entering dangerous situations since sensors only transmit
critical records to the coordinator; 2) the hospital will not
archive any data for low critical patients, so doctors cannot
review patient archives to monitor patient progress; 3) sensor
rate cannot be adapted for patients with medium criticality
based on ANOVA or Fisher tests, as they are sensitive only to
significant data variation.
A. Risks of the Internet of Medical Things (IOMT)
Healthcare is one of the industries where IoT is being
implemented, which comes with many risks:
1) If a patient’s personal information is disclosed, it can
seriously impact the patient’s health and hospital reputation.
2) When any medical device manipulates the transmitted
data, it will cause the wrong medical description and
high drug dosage due to the falsification of the data [47].
3) It has been reported that employees who are unhappy in
their jobs, those who are connected to organized crime,
or those who have bribed leak confidential information
of patients, which puts the patient’s life and privacy at
risk.
4) In some cases, doctors and nurses may cause permanent
disabilities to their patients, or worse, even cause their
death due to a lack of training.
5) Some specialized robots can perform medical operations
that are inaccurate, which might result in the patient’s
life being seriously affected or even causing them to
die [48].
The Internet of Medical Things offers the safety, reliability,
dynamic capabilities, and scalability of traditional Internet of
Things and larger capabilities. A combination of the Internet
of Things and the “Internet of Medical Things” can solve
medical and chronic problems for the elderly and chronic
diseases, which are sufficiently generic to cover a wide range
of diseases that require hydrogenous monitoring and actuation
simultaneously. The Internet of Medical Things faces a major
challenge in standardization. Vendors must take security measures to prevent hacking. Standardization of medical devices
is essential to ensuring their compatibility [49]. IOMT is not
just about mobility but also about monitoring and providing
medical care to patients wherever they are, regardless of
their mobility. Healthcare systems worldwide are becoming
increasingly aware that they need to be updated with the
latest technological innovations, and developing countries are
providing them with solutions to improve healthcare.
IoT has many opportunities and challenges in the medical field, especially in using and developing connected and
distributed medical devices [50]. With IOMT, body sensors
can be easily networked, allowing retrieval of patient data
from distant locations without installing several biosensors
and consuming many resources. IoMT focuses more on wearable devices than personal medical devices because wearable
devices often take wearable forms. In addition to sensors
and wearables, medical devices, clinical devices, and other

medical devices comprise the Internet of Medical Things
ecosystem. Since the medical community adheres to strict
ethical standards, there are some concerns that biomedical
devices need to address. In this regard, there are
1) Reliability: The reliable system should achieve its functional goals every time, so there should be no unexpected
failures under normal circumstances. For IoT systems
to provide guaranteed information that is collected, The
potential diagnostic nature of the test requires reliability.
2) Safety: Safe schemes should not harm the operating
system. As far as IoT in medical devices is concerned,
at the very least, it must demonstrate that the system
will not harm its users.
3) Security: All medical systems must be protected from
external threats and attacks because they collect highly
sensitive information about individuals [51].
B. State-of-the-Art of Existing Work
An asymmetric (public key) algorithm differs from a
symmetric (secret key) algorithm. The security provided by
asymmetric cryptosystems is better than that of symmetric
encryption, but it requires significantly greater computing
power. Symmetric encryption is less resource-intensive than
asymmetric cryptosystems, which provide a higher level of
security. Most data exchanged between healthcare and personal servers occurs over public channels like the Internet, so
stronger security measures should be implemented.
Public-key cryptography is frequently used in the cloud
for authentication, data storage, and access control (Table I).
In comparison with traditional algorithms like Rivest-ShamirAdleman (RSA), ECC offers the most security [52], [53],
[54], [55], [56], [57], [58], [59], [60], [61], [62], [63],
[64]. Considering how lightweight they are for devices with
limited resources, symmetric cryptographic algorithms have
been used in access control and data transmission between
and between IoMT sensors. A symmetric cryptographic algorithm is often used as a session key in hybrid security
schemes [55], [61], [65], [66]. Moreover, the most commonly used attacks in adversarial/security analysis are chosen
plaintext attacks, replays, impersonations, insider attacks, and
MitM attacks. Their security schemes have been analyzed in
many research studies, including Mutual Authentication (MA),
Forward Security (FS), Contextual Privacy (CP), Anonymity
and Traceability (A&T), and Unlinkability. Separately, those
who used computer simulations, the rest performed experiments on a real-time basis [57], [65]. While some used
computer simulations, others used actual hardware.
III. M ETHODOLOGY
If an adversary modifies a URL, it will have a standard
structure. In literature, URLs are analyzed as regular sentences
by exploiting their standard structure. Hence, NLP techniques
can be used to analyze URLs (e.g., to predict words and classify words). Several NLP techniques rely on word embeddings
for their effectiveness. There are several methods for embedding words, but BERT is more successful than the others.
Google AI researchers have developed an open-sour BERT, an
open-source model developed by Google AI researchers ce,

ALFERAIDI et al.: NOVEL HYBRID, BERT AND DEEP LEARNING MODEL NETWORK INTRUSION DETECTION SYSTEM

1325

TABLE I
I O MT H EALTHCARE S YSTEM S ECURITY AND P RIVACY R ESEARCH (EHR = E LECTRONIC H EALTH R ECORD )

and a pre-trained NLP model called BERT [68]. Data representation efficiently uses autoencoders and word embeddings
through projections onto appropriate vector spaces. Word

embedding models, similar to autoencoding, learn vector space
embeddings. Figure 3 shows the BERT architecture, including
procedures for pre-training and fine-tuning.

1326

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

TABLE II
H YPER -PARAMETERS

Fig. 3.

Fig. 4.

Model for BERT’s pre-training and fine-tuning.

Tokenization of URLs.

An encoder-decoder stack can be viewed as BERT. On the
other hand, traditional encoder-decoder architectures forget
some learned characteristics, especially those accumulated
over time. Data processing left-to-right and right-to-left is
more efficient with transformers than with traditional encoderdecoder architectures. The BERT transformer network consists
of encoders and decoders, including feed-forward and selfattention mechanisms.
It is solved by inserting tokens at the beginning and end
of sentences (CLS and SEP tokens). Text processing also
uses a maximum length setting. If the sentence is shorter
than the maximum length, zeros are entered for the empty
fields. Alternatively, the length will be cut off if it exceeds
the maximum. An index is eventually created after dividing
a sentence into tokens. We will only consider the hidden
attention associated with the first token to simplify things.
After that, we determine the vector distance in the word
space for each word. Figure 4 illustrates our framework, which
begins with tokenizing the text via the BERT tokenizer. Several
schemes exist for classifying texts.
These models can analyze context in both directions through
extensive pre-training on huge corpora. Deep constituent
networks are difficult to generalize when the inner layers do
not retain this ability. A hyper-parameter-based model is then
created based on the fine-tuned outer layers of the network.
The hyper parameter and their values are presented in the
Table II.
A WordPieceModel is used to tokenize and manage words
that are not in the standard vocabulary [69]; the dictionary
uses sub-words common to most words. As an alternative,
the special token [SEP] separates phrases, and the hidden
dimension H is represented by the special token [CLS].
In the classification layer, transformers represent the final
fully connected layer, represented by the last hidden layer; we
calculate the probability for each of the K categories by using
C ∈ RH as a vector and W ∈ RKxH as a matrix.


P = sofmax CW T
(1)

The BERT model provides a Categorical Cross Entropy
loss function by default, but an alternative is provided in
this article. Torch library’s Binary Cross Entropy (BCE) loss
function was chosen as the loss function in this case; predicting
single labels with this method is the best. The BCE with Logits
method was selected to achieve greater numerical stability.
This method combines a BCE with a sigmoid using the
function LogSumExp. It is possible to use BCEwL for batch
size N in the following way:
l(x, y) = L = {l1 , . . . ., lN }T , ln
= −wn {yn .σ (xn )


+(1 − yn ). log(1 − σ (xn ))

(2)

Transformer: BERT architecture relies heavily on transformers [70]. Additionally, [CLS] is placed before [X], while
[SEP] follows after [X] and [Y], starting from the sequence
of sub-words [X] and [Y]. Thus, embedding occurs through
the embedding function E and the normalization layer LN:
h0i = E(xi ) + E(i) + E(1x )

(3)

 


h0j+|x| = E(yi ) + E(j + |x|) + E 1y

(4)

 

h0 = Dropout LN 
h0


(5)

The element-wise Gaussian error linear units (GELU)
activation function and the multihead self-attention (MHSA)
function originate from the Feed Forward layer transform
blocks.:




hi+1 = skip FF, Skip MHSA, hi
(6)
Skip(f , h) = LN(h + Dropout(f (h)))
(7)
 T
 T
FF(h) = GELU hW1 + b1 W2 + b2
(8)
The new position and hi

∈

R(|x|+|y|)×dh ,

R4dh ×dh , b1 ∈ R4dh , W2 ∈ R4dh ×dh , b2 ∈ R4dh , are:

W1





. . . , hi , . . . = MHSA h1 , . . . , h|x|+|y| ]


+ b0
= W0 Concat h1i , . . . , hN
i

∈

(9)

Attention heads N are characterized by the following:
|x|+|y|
j
hi =

(i,j)

Dropout(∝k
k=1

Wvj hk

(10)

ALFERAIDI et al.: NOVEL HYBRID, BERT AND DEEP LEARNING MODEL NETWORK INTRUSION DETECTION SYSTEM

1327

TABLE III
T HE ECU-I O HT DATASET I NCLUDES THE F OLLOWING ATTACKS AND
I NPUT F IELDS

Fig. 5.

A description of the dataset’s layout and features.

TABLE IV
A N I NSTANCE OF AN ATTACK I S D IVIDED I NTO A T RAINING I NSTANCE
AND A T EST I NSTANCE


(i,j)

∝k

T
j
j
WQ h i Wk h k
exp √d /N
h

T
j
j
WQ h i Wk h k ,
|x|+|y|
√
exp
,
k =1
dh /N

=

(11)

dh

where hi
∈
R( N ) , W0
∈
Rdh ×dh , b0
∈
j
j
j
d
d
/N×d
h
h
h
,
R and WQ , WK , WV ∈ R
To conduct Web attacks, attackers usually modify URLs, so
it is essential to maintain the string of words and characters.
Our framework then converts tokenized URLs into numerical
values merged into word vectors, represented as words or
sentences. The architecture of our system is consequently
built on a text classification infrastructure. Using the BERT
tokenizer, as in many text classification schemes, we begin by
tokenizing the text, as shown in Figure 4.
j

IV. R ESULTS A NALYSIS AND D ISCUSSION
Detection of DDoS attacks in medical IoT networks was
tested using our collaborative learning model against conventional models. We compared our simulation results to those of
other models to validate our proposed model’s generalization
in different environments. We implemented our proposed
model with an NVIDIA GeForce RTX 3060 GPU on a
Windows server with an Intel Core i7-10700F CPU and 32GB
of RAM.
A. Dataset and Feature Presentation
ECU-IoHT, which analyses cyberattacks on the Internet of
Things [38], was used for the experiment. There are eight
fields in the ECU-IoHT dataset: the host address, the source
address, the destination address, the network protocol, the
length of packets, and information about packets.
An attack label in the dataset can be divided into type
(network status) and type (attack type). Network status fields
were used to determine labels. Packet information reports do
not help detect attacks, so we excluded them from the input
features. To accomplish this, the training process used five
input features. In Table III, shows the ECU-IOHT dataset
statistics.
Port scanning and DoS attacks are both part of DDoS
attacks. As another form of DDoS attack, Smurf attacks
flood targeted network devices with Internet Control Message
Protocol (ICMP) packets to turn off network services and
render them unusable. In this experiment, we used Nmap
port scanning, DoS attacks, and Smurf attacks. Thus, a total

of 108849 attacks were recorded during this experiment,
consisting of 85395 attacks and 23454 no-attacks.
B. Dataset Pre-Processing
Categorical information is encoded in the dataset as the first
step in pre-processing. Target output was encoded using label
encoding, while source IP, destination IP, and network protocol
were encoded using One-Hot encoding. We then used minmax scaling to normalize the dataset.
Xnew =

X − Xmin
Xmax − Xmin

(12)

The dataset contains the field X. There are two groups of
input fields. Time stamps and packet lengths are in one group,
while the remaining fields are in another. A group of input
fields was assigned to each collaborative agent. ARP Spoofing,
Nmap attacks, Smurf attacks and DoS attacks are among the
cyber-attacks presented in Figure 5.
As part of the implementation process, the following stages
were followed: (i) various cyber-attacks are analyzed using the
ECU IoHT dataset; (ii) this dataset contains five categorical
features encoded using one-hot encoding; (iii) to prepare for
the multiclass classification process, the dataset is categorized
as Normal, DoS attacks, Nmap attacks, ARP Spoofing and
Smurf attacks; (iv) there is a 70% training dataset and a 30%
testing dataset; (v) to train the proposed model, these labels
are selected as target features, and a trained model is provided
from the training dataset; (vi) The training dataset is used to
test the proposed model for its ability to predict normal attacks
or other types of attacks. Table IV summarizes the training and
testing instances of 108849 attack instances from the ECUIoHT dataset.

1328

Fig. 6.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

Training and validation accuracy versus number of epochs.

Fig. 7.

Training and validation loss versus number of epochs.

C. Evaluation Metrics
Accuracy, Precision, Recall, and F1-Score are evaluated to
detect anomalies. We evaluate the proposed anomaly detection
model using Accuracy, Precision, Recall, and F1-Score:
Accuracy: A measure of how well the model detects log
sequences.
TP + TN
(13)
TP + FP + TN + FN
Precision: Percentage of anomalies identified by the model
that are correctly detected.
Accuracy =

TP
(14)
TP + FP
Recall: The percentage of anomalies that the model correctly detects out of all the anomalies.
Precision =

Precision × Recall
(15)
Precision + Recall
True positives (TP) represent anomalies detected correctly
by the model. The model detects TN (true negative) when
there are normal log sequences. An anomalous log sequence
may be mistakenly detected as a true anomaly by the model if
there are several false positives (FP). An anomaly not detected
by the model is a false negative (FN).
F1 − Score = 2 ×

D. Experimental Results
Based on a dataset containing normal and abnormal
instances, an approach is proposed to detect different attacks in
IoHT. Different epoch values between 500 and 1000 are used
to train the model. The proposed model’s 500 and 1000 epochs
training time is 1582 seconds and 2559 seconds, respectively.
In this model, 1000 epochs were used for maximum validation
accuracy, and the minimum loss of 1000 epoch dataset is
shown in Figures 6 and 7.
Following the proposed model, we compare the F1 score
for ARP Spoofing, Nmap, Smurf attacks, Port Scan, and DoS
attacks. ARP and Nmap attacks of all types can be detected,
as described in Figure 8.

Fig. 8. Performance Analysis based on the feature classes with 1000 epochs.

As shown in Figure 9, the proposed model performed better
with 1000 epochs than it did with 500 epochs in terms
of Accuracy, Precision, Recall, and F1 Score. Regarding
Accuracy, Average Precision, Recall, and F1-Score, the model
with 1000 epochs performs better than the others.
In this sense, the proposed technique is superior to other
techniques and can detect normal class attacks and other
attacks, such as ARP spoofing and Nmap attacks, as illustrated
in Figure 8.
A comparison of the proposed system against existing
models is shown in Table V. Based on Table V, it can be
seen that the system proposed is significantly more effective
at detecting Nmap PortScan attacks than the existing system.
V. C ONCLUSION
A security compromise in the healthcare system could
directly result in the loss of human life, which makes the
IoMT (Internet of Medical Things) require increased security.

ALFERAIDI et al.: NOVEL HYBRID, BERT AND DEEP LEARNING MODEL NETWORK INTRUSION DETECTION SYSTEM

1329

TABLE V
T HE C OMPARATIVE P ERFORMANCE E VALUATION W ITH THE E XISTING M ODEL

others, will also be tested with the proposed methodology.
A larger dataset must be used to validate this model, and
low-complexity feature sets can enhance its effectiveness. The
performance of this model can also be enhanced by using
transformer models and incremental learning operations to
optimize the model continuously in real-time clinical settings.
R EFERENCES

Fig. 9. Performance Analysis based on the accuracy, precision, recall and
F1-Score with 500 and 1000 epochs.

This article proposes a hybrid model for detecting intrusions in
IoMT systems based on network flows and patient biometrics
that combines BERT and deep learning. It passes network
flows and biometric information into multiple hidden deeplearning layers to learn the optimal feature representation.
As part of BERT, centralized healthcare operations will be
transformed into distributed healthcare operations while maintaining user privacy. The proposed model’s precision, recall
and F1-Score are 99%, indicating that the positively identified
intrusions are correct. A similar performance is observed
for the recall and F1-score, which vary from 98-99% based
on the ARP, DoS, Nmap, Normal, and Smurf, respectively.
A comparison with the state-of-the-art study showed that
the model was more reliable and robust. Future work could
also improve and test the method presented in this paper.
Various datasets, including many classes, features, and many

[1] H. F. Nweke, Y. W. Teh, G. Mujtaba, and M. A. Al-Garadi, “Data fusion
and multiple classifier systems for human activity detection and health
monitoring: Review and open research directions,” Inf. Fusion, vol. 46,
pp. 147–170, Mar. 2019.
[2] P. Rani, S. Verma, S. P. Yadav, B. K. Rai, M. S. Naruka, and D. Kumar,
“Simulation of the lightweight blockchain technique based on privacy
and security for healthcare data for the cloud system,” Int. J. E-Health
Med. Commun., vol. 13, no. 4, pp. 1–15, 2022.
[3] J. Mills, J. Hu, and G. Min, “Communication-efficient federated learning
for wireless edge intelligence in IoT,” IEEE Internet Things J., vol. 7,
no. 7, pp. 5986–5994, Jul. 2020.
[4] S. Ahamad et al., “Deep learning-based cancer detection technique,”
in Handbook of Research on Thrust Technologies’ Effect on Image
Processing. Hershey, PA, USA: IGI Global, 2023, pp. 222–243.
doi: 10.4018/978-1-6684-8618-4.ch014.
[5] N. Kumar, P. Rani, V. Kumar, S. V. Athawale, and D. Koundal,
“THWSN: Enhanced energy-efficient clustering approach for three-tier
heterogeneous wireless sensor networks,” IEEE Sensors J., vol. 22,
no. 20, pp. 20053–20062, Oct. 2022.
[6] X. Wang, L. T. Yang, H. Liu, and M. J. Deen, “A big data-as-a-service
framework: State-of-the-art and perspectives,” IEEE Trans. Big Data,
vol. 4, no. 3, pp. 325–340, Sep. 2018.
[7] O. D. Lara and M. A. Labrador, “A survey on human activity recognition
using wearable sensors,” IEEE Commun. Surveys Tuts., vol. 15, no. 3,
pp. 1192–1209, 3rd Quart., 2013.
[8] Q. Zhang, L. T. Yang, Z. Yan, Z. Chen, and P. Li, “An efficient deep
learning model to predict cloud workload for industry informatics,” IEEE
Trans. Ind. Informat., vol. 14, no. 7, pp. 3170–3178, Jul. 2018.
[9] B. Bhola et al., “Quality-enabled decentralized dynamic IoT platform
with scalable resources integration,” IET Commun., to be published,
doi: 10.1049/cmu2.12514.
[10] R. Krishnamoorthy, M. Gupta, G. Swathi, K. Tanaka, C. Raja, and
J. V. N. Ramesh, “An intelligent IoT-based smart healthcare monitoring
system using machine learning,” in 5G-Based Smart Hospitals and
Healthcare Systems. Boca Raton, FL, USA: CRC Press, 2023.
[11] J. He, Q. Zhang, L. Wang, and L. Pei, “Weakly supervised human activity recognition from wearable sensors by recurrent attention learning,”
IEEE Sensors J., vol. 19, no. 6, pp. 2287–2297, Mar. 2019.

1330

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

[12] Q. Zhu, Z. Chen, and Y. C. Soh, “A novel semisupervised deep learning
method for human activity recognition,” IEEE Trans. Ind. Informat.,
vol. 15, no. 7, pp. 3821–3830, Jul. 2019.
[13] P. Rani and R. Sharma, “Intelligent transportation system for internet
of vehicles based vehicular networks for smart cities,” Comput. Electr.
Eng., vol. 105, Jan. 2023, Art. no. 108543.
[14] D. Javeed, M. S. Saeed, I. Ahmad, P. Kumar, A. Jolfaei, and M. Tahir,
“An intelligent intrusion detection system for smart consumer electronics
network,” IEEE Trans. Consum. Electron., vol. 69, no. 4, pp. 906–913,
Nov. 2023, doi: 10.1109/TCE.2023.3277856.
[15] Y. Zhang, Q. Wu, and M. Shikh-Bahaei, “Vertical federated learning based privacy-preserving cooperative sensing in cognitive radio
networks,” in Proc. IEEE Globecom Workshops (GC Wkshps, 2020,
pp. 1–6.
[16] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. Artif. Intell. Stat., 2017, pp. 1273–1282.
[17] P. Rani et al., “Federated learning-based misbehaviour detection for the
5G-enabled Internet of Vehicles,” IEEE Trans. Consum. Electron., early
access, Oct. 27, 2023, doi: 10.1109/TCE.2023.3328020.
[18] N. Bouacida and P. Mohapatra, “Vulnerabilities in federated learning,”
IEEE Access, vol. 9, pp. 63229–63249, 2021.
[19] L. Feng, Y. Zhao, S. Guo, X. Qiu, W. Li, and P. Yu, “BAFL: A
blockchain-based asynchronous federated learning framework,” IEEE
Trans. Comput., vol. 71, no. 5, pp. 1092–1103, May 2022.
[20] G. Han, T. Zhang, Y. Zhang, G. Xu, J. Sun, and J. Cao, “Verifiable and
privacy preserving federated learning without fully trusted centers,” J.
Ambient Intell. Humaniz. Comput., to be published.
[21] M. S. Jere, T. Farnan, and F. Koushanfar, “A taxonomy of attacks on
federated learning,” IEEE Security Privacy, vol. 19, no. 2, pp. 20–28,
Mar./Apr. 2021.
[22] F. O. Olowononi, D. B. Rawat, and C. Liu, “Federated learning with
differential privacy for resilient vehicular cyber physical systems,” in
Proc. IEEE 18th Annu. Consum. Commun. Netw. Conf. (CCNC), 2021,
pp. 1–5.
[23] Y. Qi, M. S. Hossain, J. Nie, and X. Li, “Privacy-preserving blockchainbased federated learning for traffic flow prediction,” Future Gener.
Comput. Syst., vol. 117, pp. 328–337, Apr. 2021.
[24] Z. Xiong, Z. Cai, D. Takabi, and W. Li, “Privacy threat and defense
for federated learning with non-iid data in AIoT,” IEEE Trans. Ind.
Informat., vol. 18, no. 2, pp. 1310–1321, Feb. 2022.
[25] Z. Yang, M. Chen, W. Saad, C. S. Hong, and M. Shikh-Bahaei, “Energy
efficient federated learning over wireless communication networks,”
IEEE Trans. Wireless Commun., vol. 20, no. 3, pp. 1935–1949, Mar.
2021.
[26] A. Hard et al., “Federated learning for mobile keyboard prediction,” Feb.
2019, arXiv:1811.03604.
[27] Y. Lu, X. Huang, K. Zhang, S. Maharjan, and Y. Zhang, “Low-latency
federated learning and blockchain for edge association in digital twin
empowered 6G networks,” IEEE Trans. Ind. Informat., vol. 17, no. 7,
pp. 5098–5107, Jul. 2021.
[28] R. Kumar et al., “Blockchain-federated-learning and deep learning
models for Covid-19 detection using CT imaging,” IEEE Sens. J.,
vol. 21, no. 14, pp. 16301–16314, Jul. 2021.
[29] B. Liu, B. Yan, Y. Zhou, Y. Yang, and Y. Zhang, “Experiments
of federated learning for COVID-19 chest X-ray images,” Jul. 2020,
arXiv:2007.05592.
[30] W. Zhang et al., “Dynamic-fusion-based federated learning for COVID19 detection,” IEEE Internet Things J., vol. 8, no. 21, pp. 15884–15891,
Nov. 2021, doi: 10.1109/JIOT.2021.3056185.
[31] Q. Kong et al., “Privacy-preserving aggregation for federated learningbased navigation in vehicular fog,” IEEE Trans. Ind. Informat., vol. 17,
no. 12, pp. 8453–8463, Dec. 2021, doi: 10.1109/TII.2021.3075683.
[32] P. Rani and R. Sharma, “An experimental study of IEEE 802.11n
devices for vehicular networks with various propagation loss models,” in Advanced IoT Sensors, Networks and Systems (Lecture Notes
in Electrical Engineering 1027), A. K. Dubey, V. Sugumaran, and
P. H. J. Chong, Eds., Singapore: Springer Nat., 2023, pp. 125–135,
doi: 10.1007/978-981-99-1312-1_11.
[33] D. Chen et al., “Federated learning based mobile edge
computing for augmented reality applications,” in Proc. Int.
Conf. Comput., Netw. Commun. (ICNC), Feb. 2020, pp. 767–773,
doi: 10.1109/ICNC47757.2020.9049708.
[34] I. Cvitić, D. Perakovic, B. B. Gupta, and K.-K. R. Choo,
“Boosting-based DDoS detection in Internet of Things systems,”
IEEE Internet Things J., vol. 9, no. 3, pp. 2109–2123, Feb. 2022,
doi: 10.1109/JIOT.2021.3090909.

[35] M. H. Ur Rehman, A. M. Dirir, K. Salah, E. Damiani, and D. Svetinovic,
“TrustFed: A framework for fair and trustworthy cross-device federated learning in IIoT,” IEEE Trans. Ind. Informat., vol. 17, no. 12,
pp. 8485–8494, Dec. 2021, doi: 10.1109/TII.2021.3075706.
[36] X. Wang et al., “Toward accurate anomaly detection in Industrial
Internet of Things using hierarchical federated learning,” IEEE
Internet Things J., vol. 9, no. 10, pp. 7110–7119, May 2022,
doi: 10.1109/JIOT.2021.3074382.
[37] N. Hussain and P. Rani, “Comparative studied based on attack resilient
and efficient protocol with intrusion detection system based on deep
neural network for vehicular system security,” in Distributed Artificial
Intelligence. Boca Raton, FL, USA: CRC Press, 2020, pp. 217–236.
[38] M. Ahmed, S. Byreddy, A. Nutakki, L. F. Sikos, and P. HaskellDowland, “ECU-IoHT: A dataset for analyzing cyberattacks in Internet
of Health Things,” Ad Hoc Netw., vol. 122, Nov. 2021, Art. no. 102621,
doi: 10.1016/j.adhoc.2021.102621.
[39] B. S. Glaser, Made in China 2025 and the Future of American Industry,
Center Strategic Int. Stud., Washington, DC, USA, 2019.
[40] T. Salimova, N. Guskova, I. Krakovskaya, and E. Sirota, “From industry
4.0 to Society 5.0: Challenges for sustainable competitiveness of Russian
industry,” in Proc. IOP Conf. Ser. Mater. Sci. Eng., vol. 497, Mar. 2019,
Art. no. 12090, doi: 10.1088/1757-899X/497/1/012090.
[41] R. Borawake-Satao and R. Prasad, “Green Internet of Things
schemes and techniques for adaptive energy saving in emergency
services,” in Internet of Things, Smart Computing and Technology:
A Roadmap Ahead (Studies in Systems, Decision and Control),
N. Dey, Parikshit. N. Mahalle, P. M. Shafi, V. V. Kimabahune,
and A. E. Hassanien, Eds. Cham, Switzerland: Springer Int., 2020,
pp. 173–188, doi: 10.1007/978-3-030-39047-1_8.
[42] J. Huang, Y. Meng, X. Gong, Y. Liu, and Q. Duan, “A novel deployment
scheme for green Internet of Things,” IEEE Internet Things J., vol. 1,
no. 2, pp. 196–205, Apr. 2014, doi: 10.1109/JIOT.2014.2301819.
[43] C. Habib, A. Makhoul, R. Darazi, and C. Salim, “Self-adaptive data
collection and fusion for health monitoring based on body sensor
networks,” IEEE Trans. Ind. Informat., vol. 12, no. 6, pp. 2342–2352,
Dec. 2016, doi: 10.1109/TII.2016.2575800.
[44] C. Habib, A. Makhoul, R. Darazi, and R. Couturier, “Real-time
sampling rate adaptation based on continuous risk level evaluation
in wireless body sensor networks,” in Proc. IEEE 13th Int. Conf.
Wireless Mobile Comput., Netw. Commun. (WiMob), Oct. 2017, pp. 1–8,
doi: 10.1109/WiMOB.2017.8115777.
[45] C. Habib, A. Makhoul, R. Darazi, and R. Couturier, “Health risk
assessment and decision-making for patient monitoring and decisionsupport using Wireless Body Sensor Networks,” Inf. Fusion, vol. 47,
pp. 10–22, May 2019, doi: 10.1016/j.inffus.2018.06.008.
[46] M. Koussaifi, C. Habib, and A. Makhoul, “Real-time stress evaluation
using wireless body sensor networks,” in Proc. Wireless Days (WD),
Apr. 2018, pp. 37–39, doi: 10.1109/WD.2018.8361691.
[47] F. R. Vogenberg and J. Santilli, “Healthcare trends for 2018,” Am. Health
Drug Benefits, vol. 11, no. 1, pp. 48–54, Feb. 2018.
[48] W. Si, G. Srivastava, Y. Zhang, and L. Jiang, “Green internet of things
application of a medical massage robot with system interruption,” IEEE
Access, vol. 7, pp. 127066–127077, 2019.
[49] C. Iwendi et al., “Keysplitwatermark: Zero watermarking algorithm
for software protection against cyber-attacks,” IEEE Access, vol. 8,
pp. 72650–72660, 2020.
[50] G. Srivastava, J. Crichigno, and S. Dhar, “A light and secure healthcare
blockchain for IoT medical devices,” in Proc. IEEE Can. Conf. Electr.
Comput. Eng. (CCECE), 2019, pp. 1–5.
[51] W. Zhou, Y. Jia, A. Peng, Y. Zhang, and P. Liu, “The effect of IoT
new features on security and privacy: New threats, existing solutions,
and challenges yet to be solved,” IEEE Internet Things J., vol. 6, no. 2,
pp. 1606–1616, Apr. 2019.
[52] R. Boussada, B. Hamdane, M. E. Elhdhili, and L. A. Saidane, “Privacypreserving aware data transmission for IoT-based e-health,” Comput.
Netw., vol. 162, Oct. 2019, Art. no. 106866.
[53] R. Chaudhary, A. Jindal, G. S. Aujla, N. Kumar, A. K. Das, and
N. Saxena, “LSCSH: Lattice-based secure cryptosystem for smart
healthcare in smart cities environment,” IEEE Commun. Mag., vol. 56,
no. 4, pp. 24–32, Apr. 2018.
[54] R. Ding, H. Zhong, J. Ma, X. Liu, and J. Ning, “Lightweight privacypreserving identity-based verifiable IoT-based health storage system,”
IEEE Internet Things J., vol. 6, no. 5, pp. 8393–8405, Oct. 2019.
[55] M. Elhoseny, G. Ramírez-González, O. M. Abu-Elnasr, S. A. Shawkat,
N. Arunkumar, and A. Farouk, “Secure medical data transmission model for IoT-based healthcare systems,” IEEE Access, vol. 6,
pp. 20596–20608, 2018.

ALFERAIDI et al.: NOVEL HYBRID, BERT AND DEEP LEARNING MODEL NETWORK INTRUSION DETECTION SYSTEM

[56] A. Gupta, M. Tripathi, T. J. Shaikh, and A. Sharma, “A
lightweight anonymous user authentication and key establishment
scheme for wearable devices,” Comput. Netw., vol. 149, pp. 29–42,
Feb. 2019.
[57] H. Huang, T. Gong, N. Ye, R. Wang, and Y. Dou, “Private and secured
medical data transmission and analysis for wireless sensing healthcare
system,” IEEE Trans. Ind. Informat., vol. 13, no. 3, pp. 1227–1237, Jun.
2017.
[58] X. Liu and W. Ma, “ETAP: Energy-efficient and traceable authentication
protocol in mobile medical cloud architecture,” IEEE Access, vol. 6,
pp. 33513–33528, 2018.
[59] E. Luo, M. Z. A. Bhuiyan, G. Wang, M. A. Rahman, J. Wu, and
M. Atiquzzaman, “Privacyprotector: Privacy-protected patient data collection in IoT-based healthcare systems,” IEEE Commun. Mag., vol. 56,
no. 2, pp. 163–168, Feb. 2018.
[60] A. Mehmood, I. Natgunanathan, Y. Xiang, H. Poston, and
Y. Zhang, “Anonymous authentication scheme for smart cloud based
healthcare applications,” IEEE Access, vol. 6, pp. 33552–33567,
2018.
[61] A. Ostad-Sharif, D. Abbasinezhad-Mood, and M. Nikooghadam, “A
robust and efficient ECC-based mutual authentication and session key
generation scheme for healthcare applications,” J. Med. Syst., vol. 43,
no. 1, p. 10, 2019.
[62] A. Vaniprabha and P. Poongodi, “Augmented lightweight security
scheme with access control model for wireless medical sensor networks,”
Clust. Comput., vol. 22, pp. 12495–12505, Sep. 2019.
[63] Y. Yang, X. Zheng, and C. Tang, “Lightweight distributed secure data
management system for health Internet of Things,” J. Netw. Comput.
Appl., vol. 89, pp. 26–37, Jul. 2017.

1331

[64] A. Zhang, L. Wang, X. Ye, and X. Lin, “Light-weight and robust
security-aware D2D-assist data transmission protocol for mobile-health
systems,” IEEE Trans. Inf. Forensics Security, vol. 12, pp. 662–675,
2016.
[65] X. Cheng et al., “Secure identity authentication of community medical
Internet of Things,” IEEE Access, vol. 7, pp. 115966–115977, 2019.
[66] Y. Yang, X. Zheng, W. Guo, X. Liu, and V. Chang, “Privacy-preserving
smart IoT-based healthcare big data storage and self-adaptive access
control system,” Inf. Sci., vol. 479, pp. 567–592, Apr. 2019.
[67] Y. Zhang, D. Zheng, and R. H. Deng, “Security and privacy in smart
health: Efficient policy-hiding attribute-based access control,” IEEE
Internet Things J., vol. 5, no. 3, pp. 2130–2145, Jun. 2018.
[68] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training
of deep bidirectional transformers for language understanding,” 2018,
arXiv:1810.04805.
[69] Y. Wu et al., “Google’s neural machine translation system: Bridging the
gap between human and machine translation,” 2016, arXiv:1609.08144.
[70] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural Inf.
Process. Syst., vol. 30, 2017, pp. 1–15.
[71] S. Manimurugan, S. Al-Mutairi, M. M. Aborokbah, N. Chilamkurti,
S. Ganesan, and R. Patan, “Effective attack detection in internet of
medical things smart environment using a deep belief neural network,”
IEEE Access, vol. 8, pp. 77396–77404, 2020.
[72] A. A. Diro and N. Chilamkurti, “Distributed attack detection scheme
using deep learning approach for Internet of Things,” Future Gener.
Comput. Syst., vol. 82, pp. 761–768, May 2018.
[73] E. Anthi, L. Williams, and P. Burnap, “Pulse: An adaptive intrusion
detection for the Internet of Things,” in Proc. Living Internet Things
Cybersecurity, 2018, pp. 1–4.
PAPER_TEXT
