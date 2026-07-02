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
# [165] A Temporal Convolutional Network-Based Approach for Network Intrusion Detection
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
编号：165
题名：A Temporal Convolutional Network-Based Approach for Network Intrusion Detection
年份：2024
DOI：10.1109/iciics63763.2024.10860234
来源：2024 International Conference on Integrated Intelligence and Communication Systems (ICIICS)
PDF：paper/10.1109_iciics63763.2024.10860234.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：时序、日志、KPI 与云原生异常检测
相关性：强相关，分数 16
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\165.txt
- 原始字符数：32535
- 本次发送字符数：32535
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2024 International Conference on Integrated Intelligence and Communication Systems (ICIICS)

arXiv:2412.17452v1 [cs.CR] 23 Dec 2024

A Temporal Convolutional Network-based
Approach for Network Intrusion Detection
Rukmini Nazre

Rujuta Budke

Omkar Oak

Department of CSE,
School of Computational Sciences
COEP Technological University
nazrerukmini@gmail.com

Department of CSE,
School of Computational Sciences
COEP Technological University
rujutabudke@gmail.com

Department of CSE,
School of Computational Sciences
COEP Technological University
omkarsoak@gmail.com

Suraj Sawant

Amit Joshi

Department of CSE,
School of Computational Sciences
COEP Technological University
sts.comp@coeptech.ac.in

Department of CSE,
School of Computational Sciences
COEP Technological University
adj.comp@coeptech.ac.in

Abstract—Network intrusion detection is critical for securing
modern networks, yet the complexity of network traffic poses
significant challenges to traditional methods. This study proposes
a Temporal Convolutional Network(TCN) model featuring a
residual block architecture with dilated convolutions to capture
dependencies in network traffic data while ensuring training
stability. The TCN’s ability to process sequences in parallel
enables faster, more accurate sequence modeling than Recurrent
Neural Networks. Evaluated on the Edge-IIoTset dataset, which
includes 15 classes with normal traffic and 14 cyberattack types,
the proposed model achieved an accuracy of 96.72% and a
loss of 0.0688, outperforming 1D CNN, CNN-LSTM, CNNGRU, CNN-BiLSTM, and CNN-GRU-LSTM models. A classwise classification report, encompassing metrics such as recall,
precision, accuracy, and F1-score, demonstrated the TCN model’s
superior performance across varied attack categories, including
Malware, Injection, and DDoS. These results underscore the
model’s potential in addressing the complexities of network
intrusion detection effectively.
Index Terms—Deep Learning, Temporal Convolution Networks, Network Intrusion Detection System, Recurrent Neural
Networks, Multiclass Classification, Network Security

I. I NTRODUCTION
The rapid growth of IoT devices and edge computing has
transformed network topologies, creating complex systems
for data collection and processing near the source to improve smart city applications’ efficiency. This shift to edge
computing distributes computational resources closer to data
sources but also brings significant security risks. The expanded
attack surface of IoT networks makes them prime targets
for cyberattacks, highlighting the need for strong intrusion
detection systems (IDS) to protect sensitive information [1].
These networks face an array of sophisticated cyber threats,
including malware intrusions, Distributed Denial of Service
(DDoS) attacks, and Man-In-The-Middle (MITM) exploits [2].
Previous research has extensively explored various
approaches to address these security challenges. Classical
Machine Learning (ML) algorithms, such as k-Nearest

979-8-3315-0496-0/24/$31.00 ©2024 IEEE

Neighbors (KNN), Support Vector Machines (SVM), and
Random Forests (RF), have been implemented for intrusion
detection [3]–[5]. However, these traditional methods face
several limitations in terms of their adaptability to evolving
attack patterns, insufficient capability to handle heterogeneous
traffic patterns, reduced effectiveness in processing temporal
dependencies in network traffic, and challenges in real-time
detection and scalability. Motivated by these challenges, this
research aims to develop a more robust and efficient intrusion
detection system specifically designed for edge computing
environments. Our primary objectives include designing
a novel IDS framework utilizing Temporal Convolution
Networks (TCNs), evaluating their effectiveness in capturing
sequential patterns within network traffic, comparing their
performance against traditional CNN architectures, and
validating the system’s effectiveness using the comprehensive
Edge-IIoTset dataset [6].
This work makes several significant contributions to the
field of network security in edge computing environments.
First, we develop a novel TCN-based architecture specifically
optimized for network intrusion detection. Second, we provide
a comprehensive comparative analysis of the proposed TCN
model against conventional CNN architectures. Third, we
conduct empirical validation using the Edge-IIoTset dataset,
demonstrating superior detection accuracy and reduced false
positive rates. Thus, we present a scalable framework that
can be deployed across diverse edge computing scenarios.
The remainder of this paper is organized as follows. Section II
presents a comprehensive review of related work in network
intrusion detection. Section III details the proposed TCNbased methodology. Section IV presents the experimental
setup, evaluation measures, results and comparative analysis.
Finally, Section V concludes the paper and discusses future
research directions.

II. R ELATED W ORKS
Traditional ML models are not used in Network Intrusion
Detection as they fail to capture intricate patterns from
complex network traffic. So, more advanced Deep Learning
(DL) approaches have been developed, demonstrating
significantly improved performance. CNNs are frequently used
for network intrusion detection [7]. By using convolutional
layers, 1D CNN models are able to capture patterns in
network traffic, such as the frequency of certain types of
packets or anomalies. However, CNNs lack the ability to
capture temporal dependencies, that are critical for analyzing
network traffic sequences. To address this, hybrid models
that combine CNN with recurrent networks including Long
Short-Term Memory (LSTM) and Gated Recurrent Units
(GRU), have been explored. GRUs and LSTMs are designed
to handle time-series data by maintaining a memory of earlier
inputs, making them effective for sequential data analysis
[8], [9]. The use of Bidirectional LSTM (BiLSTM) further
enhances temporal modeling by considering the context
from both past and future inputs [10]. Hybrid models like
CNN-BiLSTM and CNN-GRU have demonstrated strong
performance in various anomaly detection tasks but come with
higher computational complexity and longer training times,
especially on large datasets [11]. Most of these models focus
on specific attack types or simplified network environments,
leaving room for more comprehensive solutions.
Recent advancements in DL have introduced TCNs [12],
which offer an alternative to recurrent models. TCNs use one
dimensional convolutional layers with dilated convolutions
that help capture dependencies over a long range in data,
enabling them to process sequential information in a
parallelized manner. This architecture mitigates the common
issues in recurrent networks, such as vanishing gradients
and slow training times [13]. Many studies have explored
the usefulness of TCNs for time series prediction tasks, but
their application in network intrusion detection still remains
relatively new. The ability of TCNs to handle sequential
data without relying on recurrence makes them particularly
suitable for processing network traffic data, which can exhibit
temporal patterns of normal and abnormal behavior. Their
use provides an opportunity to enhance detection accuracy
while maintaining faster processing times compared to
traditional recurrent networks. Existing work on IDS in IoT
environments has been centered primarily around specific
attacks like DDoS [14] using datasets such as IoT-23 [15]
and CIC-IDS2018 [16]. These datasets, while useful, do
not capture the comprehensive nature of IoT threats. The
Edge-IIoTset dataset [6] is a comprehensive benchmark for
evaluating the performance of various models on 14 different
types of attacks. The dataset’s rich collection of various types
of attacks, such as malware, injection, MITM and scanning,
has made it a reliable resource for testing the performance
of various DL models [17], [18]. Existing studies have
shown that while CNN-LSTM and CNN-GRU are effective
at detecting DDoS attacks, they struggle with more complex

attack vectors such as MITM or malware due to their reliance
on temporal sequence modeling [19]. TCNs offer a promising
solution for this task [20], [21]. They have been adopted for
use on other datasets such as the APA-DDoS Dataset [22]
and the Bot-IoT Dataset [23]. They have also been used
for Binary Classification on the Edge-IIoTset dataset [24].
However, there is a lack of studies focusing on TCN-based
frameworks for Multiclass Classification on the EdgeIIoTset
dataset. This study proposes a TCN based model for 15-class
classification on the EdgeIIoTSet dataset, and compares
its performance with 1D CNN, CNN-LSTM, CNN-GRU,
CNN-BiLSTM and CNN-GRU-LSTM.
III. P ROPOSED M ETHOD
This section focuses on model development and dataset
preparation. It covers the implementation of CNN, hybrid
CNN models, and the proposed TCN model followed by a
detailed description of the dataset, data preprocessing techniques, and the classification of output attack types.
A. Prediction models
1) One-directional CNN: 1D CNNs [25] process sequential
data by applying convolutional filters along the temporal
dimension, efficiently extracting local features that are useful
for sequential data applications like language modeling, speech
recognition, or time series analysis. However, their limited
receptive field restricts their ability to capture long-range
dependencies in the sequence, making it difficult to identify
relationships between distant timesteps.
2) Hybrid CNN: Hybrid models like CNN-GRU, CNNLSTM, and CNN-BiLSTM enhance 1D CNNs by integrating recurrent layers to better capture temporal dependencies.
CNN-GRU offers a balance of performance and efficiency,
while CNN-LSTM is effective for long-term dependencies but
with higher computational costs. CNN-BiLSTM processes sequences bidirectionally, improving context understanding but
increasing training time. Among these, CNN-LSTM is often
preferred for its robust long-term dependency management,
despite its complexity. While hybrid models improve upon traditional 1D CNNs, their sequential nature limits parallelization
and increases overfitting risks.
3) Proposed Model: The proposed model, shown in Figure
1, employs TCN to overcome the limitations of hybrid models
like CNN-LSTM. TCNs utilize causal convolutions to ensure
predictions depend only on past data, preserving temporal
order and enabling efficient parallel processing. Dilated convolutions expand the receptive field without increasing network
depth, allowing TCNs to effectively capture both short and
long range dependencies. TCN architecture has residual connections, which improve gradient flow and mitigate vanishing
gradient issues, stabilizing training and enhancing representation learning.
The proposed model consists of three stacked residual
blocks with varying dilation rates to capture dependencies
across different time scales. Following these blocks, the output

TABLE II
L IST OF I NPUT F EATURES

Fig. 1. Architecture of the Proposed Model

is flattened, processed through a fully connected layer containing 128 neurons with dropout for regularization, and concludes
with a softmax layer for classification. By integrating parallel
computation, dilated convolutions, and residual connections,
the proposed TCN model effectively manages long-term dependencies while minimizing computational costs.
B. Dataset
This study utilizes the publicly available Edge-IIoTset
dataset [6], specifically the DNN-EdgeIIoT dataset, which
consists of a CSV file containing 61 features along with
two label columns— ‘Attack Label’ and ‘Attack Type’. The
dataset simulates 14 types of cyberattacks, classified into the
following major subcategories: Information gathering, MITM,
DoS/DDoS, Malware, and Injection attacks. The dataset includes features enabling identification of network intrusion
patterns such as TCP control flags, HTTP request types, ICMP
sequence numbers, DNS query names, and MQTT topics.
TABLE I
L IST OF A LL L ABEL C LASSES
Attack Type
Normal
DDoS UDP
DDoS ICMP
SQL injection
DDoS TCP
Vulnerability scanner
Password
DDoS HTTP
Uploading
Backdoor
Port Scanning
XSS
Ransomware
Fingerprinting
MITM

Support Count
349906
30392
16985
12706
12515
12507
12483
12136
9239
6007
4994
3767
2422
213
90

This study uses the dataset for multiclass classification,
15 classes specifically, which are shown in Table I. After
preprocessing, the dataset contains 4,86,362 entries. A train,
test and validation split of 70%, 20% and 10% respectively
is used. The training dataset has 3,40,452 values, test 97,273
and validation 48,637.
C. Data Preprocessing
1) Encoding and Size Reduction: Label encoding is applied
to categorical features related to HTTP requests, DNS queries,
and MQTT protocol fields. Figure II contains all of the features
used for classification. The features are one-hot encoded to
prepare them for model training. Duplicate rows are identified
and removed to maintain data integrity. Additionally, a hashbased method is used to find columns with identical content,

Feature
1. tcp.ack
2. tcp.ack raw
3. icmp.transmit timestamp
4. tcp.seq
5. udp.stream
6. dns.qry.name
7. icmp.checksum
8. icmp.seq le
9. tcp.dport
10. tcp.checksum
11. mqtt.hdrflags
12. tcp.len
13. http.content length
14. udp.time delta
15. mqtt.len
16. mqtt1.len
17. tcp.flags
18. http1 2
19. mqtt1 1
20. http1 0
21. mqtt1 encoded
22. mqtt3 2
23. dns 1
24. dns encoded
25. dns 3
26. mqtt3 encoded
27. mqtt2 encoded
28. mqtt2 encoded
29. mqtt.topic len
30. mqtt.msgtype
31. http1 0

Feature
32. http1 2
33. http.response
34. dns 0
35. mqtt3 0
36. mqtt1 0
37. mqtt2 0
38. tcp.connection.syn
39. http3 5
40. http1 1
41. tcp.flags.ack
42. http1 4
43. http1 encoded
44. http2 encoded
45. http2 2
46. mqtt.proto len
47. mqtt.confflags
48. http2 3
49. mqtt3 encoded
50. http3 2
51. tcp.connection.fin
52. http4 4
53. http4 5
54. mqtt.conf.cleaness
55. mqtt1 2
56. mqtt3 2
57. mqtt2 2
58. dns.retransmit
59. mbtcp.trans id
60. mbtcp.unit id
61. mbtcp.func id
62. http3 12

Feature
63. dns 6
64. mqtt3 1
65. mqtt2 1
66. mbtcp.transmit request
67. mbtcp.transmit request in
68. dns 4
69. dns 6
70. http1 7
71. http3 7
72. http3 3
73. http3 10
74. dns 9
75. dns 5
76. mqtt1 1
77. http3 1
78. http1 8
79. dns.retransmit request
80. mqtt1 11
81. dns 8
82. mqtt3 2
83. http5 1
84. http5 2
85. mqtt1 3
86. http3 2
87. mqtt1 4
88. http5 1
89. http3 2
90. dns 7
91. http3 5
92. mqtt1 5

and the duplicate columns are dropped. The Chi-Squared test
is employed to identify and rank features based on their
significance in relation to the target variable. The Chi-Squared
test is a statistical test that evaluates the relationship between
two categorical variables. It is chosen for feature selection
because it can help determine which features are most strongly
associated with the target variable - ’Attack type’. By ranking
the features based on their Chi-Squared statistic, the most
informative features can be identified and selected for model
training. Certain columns irrelevant to the analysis, such as
timestamps, IP addresses, as well as specific protocol data
fields are removed. The distribution of different attack types
is confirmed through an inspection of the attack type labels,
and the redundant icmp.unused column is removed for its
lack of meaningful contribution. To optimize the dataset for
model training, a size reduction is implemented using stratified
sampling. The dataset is reduced by a factor of 0.25, ensuring
that the class distribution of the ‘Attack type’ column remains
consistent.
2) Feature Scaling: In this stage, feature scaling is performed using standardization to ensure that the input features
have a standard deviation equal to one and a mean equal
to zero. The StandardScaler is fitted to the training set, and
subsequently applied to transform the test, validation, and
training sets. This helps to mitigate issues related to differing
scales of the features, thereby improving the performance and
convergence speed of the models. By standardizing the data,
this study ensures that each feature contributes equally to
the distance calculations in algorithms that rely on distance
metrics.
D. Output Classes
The dataset includes both normal and malicious network
traffic, categorized into various attack types. Normal traffic
corresponds to communication or data exchanges which are
non-malicious and legitimate. DDoS attacks flood systems

with excessive traffic, preventing normal operations. These
include DDoS attacks targeting different network protocols
such as ICMP, UDP, TCP and HTTP. SQL Injection allows
attackers to manipulate databases through malicious queries,
while Uploading involves uploading harmful files to compromise systems. Cross-Site Scripting (XSS) injects malicious
scripts into web pages, leading to data theft or session hijacking. Vulnerability Scanners and Port Scanning detect system
weaknesses, while Fingerprinting gathers system data for exploitation. Password Attacks focus on unauthorized access by
cracking credentials, and Malware includes Backdoor attacks,
which bypass authentication, and Ransomware, which encrypts
files for ransom. Lastly, MITM attacks attempt to alter as well
as intercept communications taking place amongst two entities.
These attack types highlight key methods by which systems
and networks can be compromised, essential for understanding
cybersecurity threats.

This section discusses the experimental setup, evaluation
measures and results, as well as a comparison with existing
research.
A. Experimental Setup
The models are trained and tested in identical environments
using Google Colab, equipped with an NVIDIA T4 GPU
accelerator. The software requirements consist of Python 3.10
or a higher version, along with TensorFlow 2.17. The models
are trained for 5 epochs using a learning rate of 0.001 and a
batch size of 32. The Adam optimizer is used, and the loss
function is Sparse Categorical Crossentropy.
B. Evaluation Measures
1) Overall Accuracy: Overall accuracy represents the percentage of correct predictions made by the model on the
dataset, as shown in Equation 1.
TP + TN
TP + TN + FP + FN

(1)

Where T P , T N , F P , and F N represent true positives, true
negatives, false positives, and false negatives, respectively.
2) Overall Loss - Sparse Categorical Cross Entropy: This
loss function measures the difference between actual class
labels and predicted probabilities in a multiclass classification
model that uses class indices instead of one-hot encoding, as
defined in Equation 2.
N

Loss = −

1 X
log(pyi )
N i=1

Precision =

TP
TP + FP

(3)

ii) Recall: The number of positives predicted correctly
divided by the number of actual positives, showing how well
the model identifies positive cases, as defined in Equation 4.
Recall =

TP
TP + FN

(4)

iii) F1 Score: A metric providing a balanced performance
measure between recall and precision, as described in Equation
5.
F1 = 2 ×

Precision × Recall
Precision + Recall

(5)

iv) Support: The number of actual occurrences of each class,
showing how classes are distributed.

IV. R ESULTS AND D ISCUSSION

Accuracy =

3) Classification Report: The classification report provides
metrics for each class, including:
i) Precision: The number of positive predictions that are
correct divided by the number of positive predictions overall,
indicating accuracy, as shown in Equation 3.

(2)

where N is the number of samples, yi is the true class label
for sample i, and pyi is the predicted probability of the true
class.

C. Results and Comparison
As shown in Table III, the proposed TCN model outperforms all other architectures in both accuracy and loss. The
TCN achieves the highest test accuracy of 96.72% and the
lowest test loss of 0.0668, demonstrating its superior ability
to capture complex patterns and dependencies in the data.
In contrast, the 1D CNN has an accuracy of 96.18%, the
lowest among all evaluated models and the highest test loss of
0.0760, suggesting that it struggles to fully capture the intricate
relationships within the dataset.
TABLE III
P ERFORMANCE OF D IFFERENT M ODELS
Model
1D CNN
CNN GRU
CNN LSTM
CNN BiLSTM
CNN LSTM GRU
TCN

Test Accuracy
0.9618
0.9638
0.9635
0.9640
0.9640
0.9672

Test Loss
0.0760
0.0732
0.0739
0.0756
0.0733
0.0668

Models incorporating recurrent layers such as CNN-GRU,
CNN-LSTM, and CNN-LSTM-GRU improve accuracy and
reduce loss compared to the standalone CNN. CNN-LSTMGRU matches the performance of CNN-BiLSTM at 96.40%
accuracy. However, none of these models surpass the performance of the TCN. While existing research has utilized TCNs
in various contexts, none have specifically addressed the challenge of 15-way multiclass classification on the Edge-IIoTset
dataset [24]. This study demonstrates significant advancements
over existing research in network intrusion detection on this
dataset [6].
The classification reports for the models in Tables IV, V,
VI, VII, VIII and IX and the confusion matrix of the proposed
model in Figure 2 show that all models perform well on the
highly represented ‘Normal’ class. However, their performance
on classes with lower representation such as ‘SQL injection’

and ‘XSS’, is poor. The TCN architecture demonstrates robust
performance across both high-frequency and low-frequency
class distributions, particularly excelling in classes like ‘SQL
injection’ and ‘Uploading’ with a weighted F1-score of 0.97.
The proposed model outperforms existing models due to the
following key improvements. By using stacked residual blocks
with varying dilation rates, the model captures dependencies
across different time scales more effectively. The integration of
dilated convolutions allows the model to process both immediate and distant patterns. Additionally, the residual connections
facilitate the training of deeper networks, preventing gradient
problems. With the incorporation of parallel computation, the
model significantly enhances training efficiency, while the
fully connected layer and softmax classification ensure robust
performance on large datasets.

Precision
1
1
0.86
0.93
0.54
0.94
0.98
0.93
0.83
0.98
1
0.62
1
1
0.99

Recall
1
0.94
0.64
0.97
1
0.88
0.92
0.33
1
0.91
0.95
0.89
0.36
1
1

0.91
0.98

0.85
0.97

F1-Score
1
0.97
0.73
0.95
0.70
0.91
0.95
0.49
0.91
0.95
0.97
0.73
0.53
1
1
0.97
0.85
0.97

Support
69832
18
1872
479
2500
2507
2500
2507
1010
2495
1221
755
39
6005
3533
97273
97273
97273

Normal
MITM
Uploading
Ransomware
SQL injection
DDoS HTTP
DDoS TCP
Password
Port Scanning
Vulnerability scanner
Backdoor
XSS
Fingerprinting
DDoS UDP
DDoS ICMP
Accuracy
Macro avg
Weighted avg

Recall
1.00
1.00
0.52
0.97
0.59
0.90
0.92
0.77
1.00
0.92
0.95
0.67
0.41
1.00
1.00

0.89
0.97

0.84
0.96

F1-Score
1.00
1.00
0.66
0.95
0.66
0.89
0.95
0.61
0.91
0.94
0.97
0.64
0.58
1.00
1.00
0.96
0.85
0.96

Precision
1.00
1.00
0.93
0.79
0.70
0.79
0.97
0.54
0.85
0.96
0.98
0.78
1.00
1.00
0.99

Recall
1.00
1.00
0.58
0.90
0.66
0.96
0.93
0.72
1.00
0.92
0.88
0.33
0.18
1.00
1.00

0.89
0.97

0.80
0.96

F1-Score
1.00
1.00
0.71
0.84
0.68
0.87
0.95
0.61
0.92
0.94
0.93
0.46
0.30
1.00
1.00
0.96
0.81
0.96

Support
69832
18
1872
479
2500
2507
2500
2507
1010
2495
1221
755
39
6005
3533
97273
97273
97273

Normal
MITM
Uploading
Ransomware
SQL injection
DDoS HTTP
DDoS TCP
Password
Port Scanning
Vulnerability scanner
Backdoor
XSS
Fingerprinting
DDoS UDP
DDoS ICMP
Accuracy
Macro avg
Weighted avg

Precision
1.00
1.00
0.81
0.94
0.56
0.94
0.97
0.65
0.87
0.96
0.97
0.61
1.00
1.00
0.99

Recall
1.00
0.89
0.55
0.90
0.87
0.87
0.94
0.44
0.96
0.92
0.96
0.85
0.36
1.00
1.00

0.88
0.97

0.83
0.96

F1-Score
1.00
0.94
0.66
0.92
0.68
0.90
0.95
0.53
0.91
0.94
0.96
0.71
0.53
1.00
1.00
0.96
0.84
0.96

Support
69832
18
1872
479
2500
2507
2500
2507
1010
2495
1221
755
39
6005
3533
97273
97273
97273

TABLE VIII
CNN-LSTM-GRU C LASSIFICATION R EPORT

TABLE V
CNN-GRU C LASSIFICATION R EPORT
Precision
1.00
1.00
0.88
0.92
0.76
0.89
0.98
0.50
0.84
0.96
1.00
0.60
1.00
1.00
1.00

Normal
MITM
Uploading
Ransomware
SQL injection
DDoS HTTP
DDoS TCP
Password
Port Scanning
Vulnerability scanner
Backdoor
XSS
Fingerprinting
DDoS UDP
DDoS ICMP
Accuracy
Macro avg
Weighted avg

TABLE VII
CNN-B I LSTM C LASSIFICATION R EPORT

TABLE IV
1D CNN C LASSIFICATION R EPORT
Normal
MITM
Uploading
Ransomware
SQL injection
DDoS HTTP
DDoS TCP
Password
Port Scanning
Vulnerability scanner
Backdoor
XSS
Fingerprinting
DDoS UDP
DDoS ICMP
Accuracy
Macro avg
Weighted avg

TABLE VI
CNN-LSTM C LASSIFICATION R EPORT

Support
69832
18
1872
479
2500
2507
2500
2507
1010
2495
1221
755
39
6005
3533
97273
97273
97273

V. C ONCLUSION
This study proposes a novel TCN-based model for network intrusion detection, demonstrating strong performance
on the Edge-IIoTset dataset. The TCN demonstrated superior
performance, achieving the highest test accuracy of 96.72%
and the lowest test loss of 0.0668 compared to other existing models. The classification reports further highlight the

Normal
MITM
Uploading
Ransomware
SQL injection
DDoS HTTP
DDoS TCP
Password
Port Scanning
Vulnerability scanner
Backdoor
XSS
Fingerprinting
DDoS UDP
DDoS ICMP
Accuracy
Macro avg
Weighted avg

Precision
1.00
1.00
0.80
0.82
0.54
0.91
0.98
0.94
0.84
0.98
0.93
0.60
1.00
1.00
0.99

Recall
1.00
0.89
0.68
0.78
0.98
0.90
0.92
0.31
1.00
0.92
0.90
0.73
0.36
1.00
1.00

0.89
0.97

0.82
0.96

F1-Score
1.00
0.94
0.74
0.80
0.70
0.90
0.95
0.46
0.91
0.95
0.91
0.66
0.53
1.00
1.00
0.96
0.83
0.96

Support
69832
18
1872
479
2500
2507
2500
2507
1010
2495
1221
755
39
6005
3533
97273
97273
97273

TCN’s effectiveness in accurately identifying a wide range of
attack types, particularly excelling in detecting less frequent
and more complex threats like SQL injection and uploading attacks. The enhanced performance of the TCN can be
attributed to its ability to capture long-range dependencies
and efficiently model temporal patterns within the network
traffic data. Overall, the TCN-based model proves to be a
robust and reliable solution for improving network security

TABLE IX
P ROPOSED TCN M ODEL C LASSIFICATION R EPORT
Normal
MITM
Uploading
Ransomware
SQL injection
DDoS HTTP
DDoS TCP
Password
Port Scanning
Vulnerability scanner
Backdoor
XSS
Fingerprinting
DDoS UDP
DDoS ICMP
Accuracy
Macro avg
Weighted avg

Precision
1.00
1.00
0.86
0.92
0.55
0.93
0.98
0.92
0.87
0.98
1.00
0.61
1.00
1.00
0.99

Recall
1.00
1.00
0.67
0.97
1.00
0.89
0.94
0.33
0.98
0.92
0.95
0.83
0.36
1.00
1.00

0.91
0.98

0.86
0.97

F1-Score
1.00
1.00
0.75
0.95
0.71
0.91
0.96
0.48
0.92
0.95
0.97
0.71
0.53
1.00
1.00
0.97
0.86
0.97

Support
69832
18
1872
479
2500
2507
2500
2507
1010
2495
1221
755
39
6005
3533
97273
97273
97273

Fig. 2. Confusion Matrix for the Proposed Model

through accurate and efficient intrusion detection. Despite
its strong performance, the proposed TCN-based model has
certain limitations. It’s evaluation is limited to the EdgeIIoTset dataset, which may restrict its generalizability to other
datasets or real-time environments. The model’s computational
complexity could also challenge its deployment in resourceconstrained settings. In future work, classification accuracy can
be improved, especially for complex attacks. The scalability
and performance can also be evaluated in dynamic conditions.
Finally, the trust and usability of automated IDS in critical
infrastructure can be increased, helping administrators better
understand detection decisions.
R EFERENCES
[1] Corallo, A., Lazoi, M., Lezzi, M., & Luperto, A. (2022). Cybersecurity awareness in the context of the Industrial Internet of Things: A
systematic literature review. Computers in Industry, 137, 103614.
[2] Abdulganiyu, O. H., Tchakoucht, T. A., & Saheed, Y. K. (2024).
Towards an efficient model for network intrusion detection system (IDS):
systematic literature review. Wireless Networks, 30(1), 453-482.
[3] Gu, J., & Lu, S. (2021). An effective intrusion detection approach using
SVM with naı̈ve Bayes feature embedding. Computers & Security, 103,
102158.

[4] Liu, G., Zhao, H., Fan, F., Liu, G., Xu, Q., & Nazir, S. (2022). An
enhanced intrusion detection model based on improved kNN in WSNs.
Sensors, 22(4), 1407.
[5] Awotunde, J. B., Ayo, F. E., Panigrahi, R., Garg, A., Bhoi, A. K., &
Barsocchi, P. (2023). A multi-level random forest model-based intrusion
detection using fuzzy inference system for internet of things networks.
International Journal of Computational Intelligence Systems, 16(1), 31.
[6] Ferrag, M. A., Friha, O., Hamouda, D., Maglaras, L., & Janicke, H.
(2022). Edge-IIoTset: A new comprehensive realistic cyber security
dataset of IoT and IIoT applications for centralized and federated
learning. IEEE Access, 10, 40281-40306.
[7] Kilichev, D., & Kim, W. (2023). Hyperparameter optimization for 1DCNN-based network intrusion detection using GA and PSO. Mathematics, 11(17), 3724.
[8] Wang, Z., Huang, H., Du, R., Li, X., & Yuan, G. (2023). IoT intrusion
detection model based on CNN-GRU. Frontiers in Computing and
Intelligent Systems, 4(2), 90-95.
[9] Altunay, H. C., & Albayrak, Z. (2023). A hybrid CNN+ LSTM-based
intrusion detection system for industrial IoT networks. Engineering
Science and Technology, an International Journal, 38, 101322.
[10] Said, R. B., Sabir, Z., & Askerzade, I. (2023). CNN-BiLSTM: A
hybrid deep learning approach for network intrusion detection system in
software defined networking with hybrid feature selection. IEEE Access.
[11] Gao, J. (2022). Network intrusion detection method combining
CNN
and
BiLSTM
in
cloud
computing
environment.
Computational Intelligence and Neuroscience, 2022, 7272479.
https://doi.org/10.1155/2022/7272479
[12] Lea, C., Flynn, M. D., Vidal, R., Reiter, A., & Hager, G. D. (2017).
Temporal convolutional networks for action segmentation and detection.
In Proceedings of the IEEE Conference on Computer Vision and Pattern
Recognition (pp. 156-165).
[13] Shiri, F. M., Perumal, T., Mustapha, N., & Mohamed, R. A. (2023). A
Comprehensive Overview and Comparative Analysis on Deep Learning
Models. CNN, RNN, LSTM, GRU.
[14] Kumari, P., & Jain, A. K. (2023). A comprehensive study of DDoS
attacks over IoT network and their countermeasures. Computers &
Security, 127, 103096.
[15] Garcia, S., Parmisano, A., & Erquiaga, M. J. (2020). IoT-23: A labeled
dataset with malicious and benign IoT network traffic (Version 1.0.0)
[Data set]. Zenodo. http://doi.org/10.5281/zenodo.4743746
[16] Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). Toward
generating a new intrusion detection dataset and intrusion traffic characterization. ICISSp, 1, 108-116.
[17] Al Nuaimi, T., Al Zaabi, S., Alyilieli, M., AlMaskari, M., Alblooshi,
S., Alhabsi, F., ... & Al Badawi, A. (2023). A comparative evaluation
of intrusion detection systems on the edge-IIoT-2022 dataset. Intelligent
Systems with Applications, 20, 200298.
[18] Hamza, N., Lakmal, H. K. I. S., Maduranga, M. W. P., & Kathriarachchi,
R. P. S. (2023, August). Malware detection of IoT networks using
machine learning: An experimental study with Edge-IIoT dataset. In
30th Annual Technical Conference-IET Sri Lanka Network, Colombo,
Sri Lanka.
[19] Jose, J., & Jose, D. V. (2023). Deep learning algorithms for intrusion
detection systems in internet of things using CIC-IDS 2017 dataset.
International Journal of Electrical and Computer Engineering (IJECE),
13(1), 1134-1141.
[20] Shi, D., Xu, M., Wu, T., & Kou, L. (2021). Intrusion detecting system
based on temporal convolutional network for in-vehicle CAN networks.
Mobile Information Systems, 2021(1), 1440259.
[21] Cheng, P., Xu, K., Li, S., & Han, M. (2022). TCAN-IDS: Intrusion
detection system for internet of vehicle using temporal convolutional
attention network. Symmetry, 14(2), 310.
[22] Rani, Y. A., & Reddy, E. S. (2024). Deep intrusion net: An efficient
framework for network intrusion detection using hybrid deep TCN and
GRU with integral features. Wireless Networks, 1-24.
[23] DLiu, Z., Liu, S., & Zhang, J. (2024). An Industrial Intrusion DetectionMethod Based on Hybrid Convolutional Neural Networks with Improved
TCN. Computers, Materials & Continua, 78(1).
[24] Alotaibi, A., & Barnawi, A. (2024). LightFIDS: Lightweight and Hierarchical Federated IDS for Massive IoT in 6G Network. Arabian Journal
for Science and Engineering, 49(3), 4383-4399.
[25] LeCun, Y., Boser, B., Denker, J. S., Henderson, D., Howard, R. E.,
Hubbard, W., & Jackel, L. D. (1989). Backpropagation applied to
handwritten zip code recognition. Neural computation, 1(4), 541-551.
PAPER_TEXT
