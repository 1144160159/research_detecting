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
# [265] Multi-Task Scenario Encrypted Traffic Classification and Parameter Analysis
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
编号：265
题名：Multi-Task Scenario Encrypted Traffic Classification and Parameter Analysis
年份：2024
DOI：10.3390/s24103078
来源：Sensors
PDF：paper/10.3390_s24103078.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 14
已有代码状态：已下载；PETReLM -> source\PETReLM

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\265.txt
- 原始字符数：88219
- 本次发送字符数：88219
- 是否截断：False

代码包：
- 仓库：PETReLM
  - URL：https://github.com/ssy198/PETReLM
  - 状态：downloaded
  - 本地目录：source\PETReLM
  - 顶层结构：README.md、dataprepocess.py、evaluate.py、finetuning.py、pt_model/
  - 主要语言：JSON:4、Python:3
  - README 标题：PETReLM、Using PETReLM、Content、PETReLM、Using PETReLM、Content、PETReLM、Using PETReLM、Content
  - README 运行线索：
  - 关键文件：{"评估/测试入口": ["evaluate.py"], "配置文件": ["pt_model/config.json"]}
  - 数据集线索：Tor、VPN、tor

论文正文包开始：
<<<PAPER_TEXT
sensors
Article

Multi-Task Scenario Encrypted Traffic Classification and
Parameter Analysis
Guanyu Wang and Yijun Gu *
College of Information and Cyber Security, People’s Public Security University of China, Beijing 100038, China;
gyc0016@163.com
* Correspondence: guyijun@ppsuc.edu.cn

Abstract: The widespread use of encrypted traffic poses challenges to network management and
network security. Traditional machine learning-based methods for encrypted traffic classification no
longer meet the demands of management and security. The application of deep learning technology
in encrypted traffic classification significantly improves the accuracy of models. This study focuses
primarily on encrypted traffic classification in the fields of network analysis and network security. To
address the shortcomings of existing deep learning-based encrypted traffic classification methods
in terms of computational memory consumption and interpretability, we introduce a ParameterEfficient Fine-Tuning method for efficiently tuning the parameters of an encrypted traffic classification
model. Experimentation is conducted on various classification scenarios, including Tor traffic service
classification and malicious traffic classification, using multiple public datasets. Fair comparisons are
made with state-of-the-art deep learning model architectures. The results indicate that the proposed
method significantly reduces the scale of fine-tuning parameters and computational resource usage
while achieving performance comparable to that of the existing best models. Furthermore, we
interpret the learning mechanism of encrypted traffic representation in the pre-training model by
analyzing the parameters and structure of the model. This comparison validates the hypothesis that
the model exhibits hierarchical structure, clear organization, and distinct features.
Keywords: encrypted traffic; network management; interpretability analysis; fine-tuning

Citation: Wang, G.; Gu, Y. Multi-Task
Scenario Encrypted Traffic
Classification and Parameter Analysis.
Sensors 2024, 24, 3078. https://
doi.org/10.3390/s24103078
Academic Editor: Alberto Gotta
Received: 15 April 2024
Revised: 9 May 2024
Accepted: 10 May 2024
Published: 12 May 2024

Copyright: © 2024 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license (https://
creativecommons.org/licenses/by/
4.0/).

1. Introduction
In network management and cybersecurity domains, network traffic classification
plays an integral role. Traffic classification refers to the process of identifying and distinguishing different categories of network traffic according to specific requirements and
designs, enabling further analysis. Accurate network traffic classification can help us obtain
an overall perception of network bandwidth, capture different network usage habits, and
assess network security. Internet Service Providers (ISPs) optimize network resources and
enhance network management through traffic classification, while security departments
leverage traffic analysis to monitor network security states, identifying and responding to
malicious network attacks. However, the widespread use of traffic encryption technologies
such as Transport Layer Security (TLS) presents significant challenges to network traffic
classification [1]. Encrypted traffic, where plaintext payloads are encrypted and transmitted
as ciphertext, can only be decrypted by the sender and the receiver, making it difficult for
third parties to interpret. Traditional traffic analysis methods, which rely on extracting
valuable information from plaintext payloads (such as port-based methods, Deep Packet
Inspection (DPI) methods, and statistical methods), may become ineffective. This encryption prevents network administrators from directly extracting useful plaintext information
from network traffic, complicates management tasks, and creates convenient channels for
malicious actors to transmit malicious traffic, increasing network security risks [2,3].
In this complex scenario, encrypted traffic classification methods based on feature
engineering extract statistically designed features and classify them using classical machine

Sensors 2024, 24, 3078. https://doi.org/10.3390/s24103078

https://www.mdpi.com/journal/sensors

Sensors 2024, 24, 3078

2 of 21

learning [4–7] or deep learning [8,9]. This approach differs from traditional methods as they
do not solely rely on plaintext information such as ports, resulting in better classification
performance and ease of deployment. However, performance depends on the comprehensiveness and effectiveness of manually selected features [10]. Alternatively, representation
learning-based methods for encrypted traffic classification employ deep learning models
to automatically extract and process representations from encrypted traffic [2,10–14]. This
approach has become a high-performance algorithmic solution to the problem of encrypted
traffic classification [15,16]. While these methods can improve classification performance,
they also expose the immaturity of applying deep learning to this problem and are constrained by the limitations inherent in deep learning itself. Improper design may result
in biased conclusions or exaggerated classification outcomes. Neglecting the alignment
between deep learning methods and the challenges in this domain prevents designers from
fully harnessing the potential of deep learning [17]. Unlike natural language and images,
encrypted byte streams are difficult for humans to understand. The relevance of the loaded
bytes, coupled with the complexity of the deep learning model itself, makes the problem of
poor interpretability even more pronounced.
Among the many deep learning frameworks, pre-training models have been extensively applied and have shown exceptional performance in fields such as Natural Language
Processing (NLP) and Computer Vision (CV) [14]. In the increasingly complex network
environment, pre-training model-based encrypted traffic classification methods outperform
other deep learning architectures. Pre-training models first undergo training with a large
volume of unlabeled data to pre-train the initial model, followed by fine-tuning with a
small amount of labeled data from downstream tasks. The fine-tuned model can then be
directly applied to well-designed tasks [18]. However, traditional pre-training methods
that adjust all parameters of the model lead to increasingly expensive training costs as the
model size and number of downstream tasks grow.
The feature engineering-based encrypted traffic classification methods and the representation learning-based methods demonstrate that it is possible to classify traffic in a
fine-grained manner. Statistical representation, plaintext information, and features present
in the original payloads are discriminative enough to make each class easily separated
from one another [19]. We therefore focus on designing a fine-grained encrypted traffic
classification method with broad applicability and stable results in a generic network environment. We aim to implement encrypted traffic functional classification methods under
limited conditions. The application scenarios for encrypted traffic classification include
four types: (I) the network analytics domain, (II) the network security domain, (III) the
user privacy domain, and (IV) the domain of network functions in middleboxes [3]. Our
research primarily focuses on two subdomains within Scenarios (I) and (II): application
identification, network intrusion detection, and malware detection, particularly emphasizing application identification in different network environments. Specifically, we aim to
design a representation learning framework that can be trained in different scenarios to
achieve encrypted traffic functional classification. For example, distinguishing different
services (VPN Email, Email, VPN Chat, Chat, etc.) and applications (Netflix, P2P, SCP, etc.)
in VPN traffic, distinguishing normal traffic (BitTorrent, Facetime, FTP, etc.) from traffic
generated by malware (Cridex, Geodo, etc.) in mixed traffic, and distinguishing different
attack traffic in the IoT environment (DDoS ACK Fragmentation, ARP Spoofing, XSS, etc.).
In this paper, we propose the Parameter-Efficient Fine-Tuning (PEFT)-based Encrypted
Traffic Representation Learning Method (PETReLM). We develop suitable data preprocessing methods based on the characteristics of encrypted traffic and use pre-training models
for representation learning to accomplish encrypted traffic classification tasks.
Our contributions are as follows:

•

We propose a novel packet-level encrypted traffic classification method based on
pre-trained models and PEFT methods. We introduce the Low-Rank Adaptation
(LoRA) [20] method into encrypted traffic classification, enhancing pre-training and
fine-tuning methods to adapt to encrypted traffic classification tasks. Our method

Sensors 2024, 24, 3078

3 of 21

•

•

can learn different types of traffic representations in different scenarios with wide
applicability and also improve the efficiency of parameter utilization.
We validate the existence of comprehensive traffic representation information in individual packets and demonstrate the feasibility of classifying traffic for specific scenarios based on these representations. We also discuss the limitations of packet-level
encrypted traffic classification.
Based on singular values and vectors, we compare the matrix parameters of the finetuned model with those of the pre-trained model to analyze the model’s representation
learning mechanism and fine-tuning principles.

The rest of the paper is structured as follows: Section 2 introduces related work on
encrypted traffic classification and PEFT. Section 3 describes our proposed method for
encrypted traffic classification. Section 4 presents our experimental settings and results.
In Section 5, we analyze the mechanism of encrypted traffic representation extraction and
fine-tuning. In Section 6, we discuss the limitations of our method and conclude the paper.
2. Related Works
In this section, we review the related research in the fields of encrypted traffic classification and PEFT, discussing the advantages and limitations of these methods.
2.1. Encrypted Traffic Classification
The methods of encrypted traffic classification mainly include feature engineeringbased approaches and representation learning-based methods. The objective is to classify
encrypted traffic according to predefined criteria by learning statistical features, payload
features, etc., of the encrypted traffic. Table 1 reports relevant work in these domains and
summarizes the fundamental aspects of the methodologies employed.
Table 1. Comparison of encrypted traffic classification algorithms.
Input Data
IP, Port, Packet Lenth, Packet Direction,
TLS Certificate
IP, Protocol, Packet Length
Packet Lenth, Packet Direction
Certificate, Packet Length
Packet Length, Arrival Time
Packet Lenth, Packet Direction
Payload
Payload
Payload
Payload
Payload
Payload

Algorithms

Paper

Random Forest, Correlation Graph

FlowPrint [4]

Random Forest
Random Forest
Second-order Markov Chains
Auto Encoder
GNN
1D-CNN
SAE, 1D-CNN
1D-CNN, BiLSTM
BiLSTM, TextCNN
ALBERT
BERT

APPScanner [5]
Conti et al. [6]
Shen et al. [7]
Yu et al. [8]
Shen et al. [9]
Wang et al. [11]
Deep Packet [10]
TCSRNN [2]
Jiang et al. [12]
PERT [13]
ET-BERT [14]

2.1.1. Feature Engineering-Based Methods
Feature engineering-based methods involve extracting manually designed traffic
features and classifying encrypted traffic using classic machine learning or deep learning.
Commonly effective features include basic features, time-series features, statistical features,
and multi-protocol payload characteristics [21]. Designers produce features based on
experience, screen features by comparing their information content and redundancy, and
provide these features as input to the designed model. Common classification granularities
include data flows (unidirectional or bidirectional), TCP connections, etc.
FlowPrint [4] utilizes the temporal correlation of traffic communication destination
addresses to discover different patterns in network traffic, creating a fingerprint library for
network traffic. APPScanner [5] employs manually selected traffic statistical features to
identify mobile applications, exploring the extent to which mobile app fingerprints can be

Sensors 2024, 24, 3078

4 of 21

constructed and assessing the robustness of the app fingerprint framework. Conti et al. [6]
generate different time-series cumulative graphs based on varied network behaviors and
learn the associations of network traffic cumulative graphs related to specific behaviors.
Shen et al. [7] propose constructing application fingerprints by merging the application
attribute bigrams into the second-order homogeneous Markov chains, where the attribute
bigram comprises certificate packet lengths and the size of the first application data in
encrypted sessions. Yu et al. [8] extract traffic statistical features and certificate features from
the TLS handshake to the verification phase, extend traffic features into higher dimensions,
and introduce hierarchical clustering to reduce data computation. Shen et al. [9] use traffic
packets to build the traffic interaction graph and then employ Graph Neural Networks
(GNNs) to achieve decentralized APP recognition.
The aforementioned methods lack flexibility and adaptability in the realistic mobile
context. Feature engineering relies on task characteristics and expert experience. Manually selected features may not fully capture the characteristics of traffic. This selection
process, coupled with method usage, imposes certain limitations on the applicability of
classification methods.
2.1.2. Representation Learning-Based Methods
Representation learning-based methods avoid manually designing traffic features
and allow for deep learning frameworks to automatically extract representations from
raw encrypted byte streams in an end-to-end manner. Typically, these methods focus on
classifying at the granularity of data flows (unidirectional or bidirectional), packets, TCP
connections, and traffic bursts.
Wang et al. [11] use a One-Dimensional Convolutional Neural Network (1D-CNN) for
end-to-end encrypted traffic classification. They transform traffic into two-dimensional
images by truncating traffic payloads to a fixed length and converting bytes into image
pixels, subsequently using 1D-CNN to learn image representations. Lotfollahi et al. [10]
introduce Deep Packet architecture employing Stacked Auto-Encoders (SAE) [22] and a
1D-CNN to handle both traffic representation and application identification tasks. For
learning temporal dimension representations, TSCRNN [2] proposes using 1D-CNN to
extract spatial features of encrypted traffic, followed by stacked BiLTSM [23] to extract
temporal features based on these low-dimensional feature mappings. Jiang et al. [12] use
BiLSTM and TextCNN [24] to capture local features and temporal relationship of traffic,
employing a multi-head attention mechanism to select important features and reduce
the impact of noisy features. PERT [13] devises a novel method to convert encrypted
traffic payloads into byte streams, using the A Lite BERT (ALBERT) model [25] for packetlevel traffic representation learning, learning the contextual distribution of unlabeled
payload bytes, and then reusing the pre-trained model for data stream-level fine-tuning.
ET-BERT [14] designs an encrypted traffic representation model based on Bidirectional
Encoder Representation from Transformers (BERT) [18] and pre-training tasks more suitable
for encrypted traffic, achieving significant improvements in generalization ability and
performing well on multiple datasets.
Methods that take raw input data as input enable models to automatically extract
representations from the raw data, reducing the overall reliance on human expertise.
While current methods achieve good results, deep learning models selected by these
representation learning-based methods face certain constraints. The performance of the
methods is influenced by preprocessing methods for raw traffic, the adaptability of deep
learning models to encrypted traffic classification tasks, and the inherent limitations of
deep learning itself, such as slow convergence, high computational resource usage, and
poor interpretability.
2.2. PEFT
PEFT aims to enhance the performance of pre-training models on new tasks by reducing the number of fine-tuning parameters and computational complexity, thereby

Sensors 2024, 24, 3078

5 of 21

alleviating the high training costs of large pre-training models. PEFT methods can overcome catastrophic forgetting [26] and exhibit excellent robustness in out-of-distribution
evaluations [27].
Houlsby et al. [28] design the Adapter module consisting of two feedforward projection matrices and a nonlinear layer embedded within the Transformer [29] structure.
During training, Transformer parameters are frozen, and only the newly added Adapter
module parameters are adjusted. The Adapter achieves results close to full fine-tuning with
just 3.6% of the original model’s parameter size. Lin et al. [27] construct a set of prompt
tokens as Prefix connected to the left side of each attention layer input in Transformer,
keeping model parameters unchanged during fine-tuning and updating only the Prefix
part. The Prefix Tuning approach has achieved good results in various language models.
Liu et al. [30] develop the IA3 method, which scales activations by learned vectors in attention layers and the Feedforward Neural Network (FNN), achieving stronger performance
than full model fine-tuning. Liu et al. [31] propose converting prompts into learnable
embedding layers and processing prompt embedding layers with MLP+LSTM, enhancing
BERT’s performance on few-sample tasks, and significantly reducing the need for prompt
engineering. Hu et al. [20] design the LoRA method based on the intrinsic “low rank” of
parameter update matrices. LoRA maintains the pre-trained model parameters unchanged
and uses two low-rank matrices to replace weight update matrices, avoiding inference
delay issues introduced by inserting other modules.
The shortcoming of PEFT is that it sacrifices a portion of the model’s performance and
fails to establish a connection with the pre-trained model, leaving room for improvement
in interpretability.
3. Our Methods
In this section, we present the overall framework and implementation details of the
PETReLM. The PETReLM is designed to extract representations of encrypted traffic and
classify traffic based on traffic representations. Our open-source code is hosted at the
following GitHub repository: https://github.com/ssy198/PETReLM.
3.1. Architectural Overview
We propose the overall framework of the PETReLM as shown in Figure 1. We select
BERT [18] as the foundational model architecture for pre-training and fine-tuning, and the
approach consists of three main stages:
(1)

(2)

(3)

Traffic Preprocessing: This stage involves trimming and transforming raw encrypted
traffic data. We tailor traffic packets by removing irrelevant information and the
convert tailored traffic into a format suitable for the model.
Model Pre-training: This stage employs a Masked Language Model (MLM) and a
modified Next Sentence Prediction (mNSP) task as pre-training tasks for the model
to learn general representations of traffic. This enables the model to initially extract
basic general representations.
Model Fine-tuning: In this stage, the pre-trained model parameters are reused for
downstream classification task training. The pre-trained model parameters are frozen,
and the newly embedded PEFT module and added fully connected layer classifier parameters are fine-tuned. This enables the model to learn task-specific representations
and achieve encrypted traffic classification in specific scenarios.

Sensors 2024, 24, x FOR PEER REVIEW
Sensors 2024, 24, 3078

6 of 21
6 of 21

Pre-training
mNSP
Tasks

MLM

Downstream Task 3
Downstream Task 2

Output

O0

O1

O2

O3

ON

ON

CLS
O0

Downstream Task 1
O1

O2

ON

O3

ON

BERT
BERT

Trainable
Parameters

Model
Pre-training
Input

I0

I1

I2

I3

IN

PEFT

+
Frozen
Parameters

IN

Trainable
Parameters

Byte Pair Encoding&Word Piece

Raw Encrypted
Traffic

Traffic
Preprocessing

I0

I1

I2

I3

IN

IN

Model
Fine-tuning
Figure 1. Overview of model framework.
Figure 1. Overview of model framework.

3.2. Preprocessing
3.2. Preprocessing
The preprocessing of traffic involves traffic trimming and traffic transformation. Traffic
The preprocessing
of traffic involves
traffic
and traffic
transformation.
trimming
refers to appropriately
trimming
thetrimming
original traffic
to reduce
interferenceTraffrom
ficnoise
trimming
refers toTraffic
appropriately
trimming
thetooriginal
traffic
totrimmed
reduce interference
information.
transformation
refers
converting
the
traffic into a
from
information.
Traffic
transformation
refersencrypted
to converting
theintrimmed
datanoise
format
suitable for
model
input. We classify
traffic
a packettraffic
level,into
with
a specific
data format
suitable
for model
input.4.1.
We classify encrypted traffic in a packet level, with
rationale
detailed
in Section
specific
rationale
in Sectionbased
4.1. on the TCP/IP protocol suite and discuss which
We
analyzedetailed
packet structure
analyze
packet or
structure
based
on thethe
TCP/IP
protocol
suite
and discuss
which
partWe
should
be retained
discarded.
Because
data link
layer (L2)
header
and trailer
only
contain
essential
controlorinformation
for communication
between
adjacent
hosts,
part
should
be retained
discarded. Because
the data link
layer (L2)
header
andwhich
traileris
not very
helpful
for encrypted
traffic classification,
they should between
be removed.
The network
only
contain
essential
control information
for communication
adjacent
hosts,
layer
(L3)
IP
packet
header
mainly
includes
communication
addresses
(IP
addresses)
which is not very helpful for encrypted traffic classification, they should be removed. The
within the
packet-switched
Whileincludes
the server’s
IP address in
normal (IP
traffic
network
layer
(L3) IP packet network.
header mainly
communication
addresses
ad-is
valuable
for encrypted
traffic classification,
considering
that IP
VPNs,
malware,
etc.,trafmay
dresses)
within
the packet-switched
network. While
the server’s
address
in normal
actualfor
IP encrypted
addresses and
theclassification,
complexity of considering
translating IPthat
addresses
meaningful
ficobscure
is valuable
traffic
VPNs, into
malware,
etc.,
information
for deep
learning models,
we remove of
the
network layer
header information.
may
obscure actual
IP addresses
and the complexity
translating
IP addresses
into meanThe
transport
layer
(L4)
is
a
crucial
part
of
a
packet,
consisting
of
the
TCP
and
UDP
ingful information for deep learning models, we remove the network layer header
inforprotocols.
Most
services
are
designed
based
on
these
protocols.
The
transport
layer
header
mation. The transport layer (L4) is a crucial part of a packet, consisting of the TCP and
includes
information
such asare
ports
and session
indicate
information
about
UDP
protocols.
Most services
designed
basedcontrol.
on thesePorts
protocols.
The
transport layer
processes,
and ifinformation
the port is asuch
well-known
portsession
number,control.
the service
be directly
header
includes
as ports and
Portscategory
indicatecan
information
determined.
Although
ports
be obfuscated
in number,
some malicious
traffic
scenarios,
the
about
processes,
and if the
portmay
is a well-known
port
the service
category
can be
transport
layer
header
is
an
important
reference
for
host
process
communication
behavior.
directly determined. Although ports may be obfuscated in some malicious traffic scenarWethe
believe
that retaining
information
from the transport
header
yields
greater benefits
ios,
transport
layer header
is an important
reference layer
for host
process
communication
than
the
information
loss
from
discarding
it,
so
we
keep
the
relevant
information
from
behavior. We believe that retaining information from the transport layer header yields
the
transport
layer.
Finally,
the
application
layer
(L5)
is
a
crucial
reference
for
encrypted
greater benefits than the information loss from discarding it, so we keep the relevant intraffic classification
and is retained.
In summary,
to retain
efficient
that
formation
from the transport
layer. Finally,
the application
layer
(L5) isrepresentations
a crucial reference
enable
the
separation
of
different
categories
for
downstream
tasks,
we
discard
network
for encrypted traffic classification and is retained. In summary, to retain efficient reprelayer headers
and retain
relevant information
the transport
layer and the
application
sentations
that enable
the separation
of differentfrom
categories
for downstream
tasks,
we dislayer for further processing.
card network layer headers and retain relevant information from the transport layer and
The length of encrypted traffic payload is not fixed, and we also need to preserve the
the application layer for further processing.
transportation layer header information and part of the application layer payload byte
The length of encrypted traffic payload is not fixed, and we also need to preserve the
stream by the truncation operation. This step reduces the dimensions of the input data and
transportation layer header information and part of the application layer payload byte

Sensors 2024, 24, x FOR PEER REVIEW

7 of 21

Sensors 2024, 24, 3078

7 of 21

stream by the truncation operation. This step reduces the dimensions of the input data
and improves the efficiency of model training and inference. Details regarding the trunimproves the efficiency of model training and inference. Details regarding the truncation
cation operation are discussed in Section 4.2.
operation are discussed in Section 4.2.
Encrypted traffic is a distinct data type separate from natural language or images.
Encrypted traffic is a distinct data type separate from natural language or images.
However, from an abstract perspective, traffic data can be considered sequential data.
However, from an abstract perspective, traffic data can be considered sequential data.
Therefore,
Therefore, we
we employ
employ sequence
sequence data
data preprocessing
preprocessing methods
methods to
to handle
handle trimmed
trimmed traffic
traffic
payloads.
To
transform
the
byte
stream
of
payloads
into
a
sequence
of
basic
character
payloads. To transform the byte stream of payloads into a sequence of basic character
units
units
akin
to
natural
language,
we
employ
a
Byte-Pair
Encoding
method
[13].
It
concateakin to natural language, we employ a Byte-Pair Encoding method [13]. It concatenates
nates
two adjacent
to form
a basic
character
(0000—ffff),
turning
the byte
stream
two adjacent
bytesbytes
to form
a basic
character
unit unit
(0000—ffff),
turning
the byte
stream
into
into
a
string
of
byte
pairs.
Subsequently,
the
Word
Piece
algorithm
[32]
is
used
to
tokenize
a string of byte pairs. Subsequently, the Word Piece algorithm [32] is used to tokenize
these
thesebyte
bytepair
pairstrings.
strings.For
Forsubsequent
subsequenttask
taskprocessing,
processing,special
specialtokens
tokens[CLS],
[CLS],[SEP],
[SEP],[PAD],
[PAD],
and
[MASK]
are
added
to
the
dictionary
generated
by
the
Word
Piece
algorithm.
and [MASK] are added to the dictionary generated by the Word Piece algorithm. Each
Each
token
tokensequence
sequence begins
beginswith
with [CLS],
[CLS], representing
representing the
the hidden
hidden layer
layer state
state output
output for
forthe
thefinal
final
classification
thethe
end
of of
a sub-sequence,
[PAD]
is used
for padding
seclassificationtask.
task.[SEP]
[SEP]marks
marks
end
a sub-sequence,
[PAD]
is used
for padding
quences
to
reach
a
minimum
length,
and
[MASK]
is
used
to
obscure
existing
tokens
for
sequences to reach a minimum length, and [MASK] is used to obscure existing tokens for
pre-training
The token
token embedding
embeddingtransformed
transformedby
bythe
theWord
WordPiece
Piecealgorithm
algorithmis
pre-training task
task MLM.
MLM. The
is
summed
with
the
segment
and
position
embeddings
to
obtain
the
input
sequence.
Fig-2
summed with the segment and position embeddings to obtain the input sequence. Figure
ure
2 illustrates
the process
of traffic
preprocessing.
illustrates
the process
of traffic
preprocessing.
Input

I0

I1

...

Ik

Ik+1

...

IN

Segment
Embeddings

EA

EA

...

EA

EB

...

EB

+

+

+

+

Position
Embeddings

E0

E1

...

Ek

Ek+1

...

EN

+

+

+

Token
Embeddings

+

E[CLS]

E[d56f]

...

E[SEP]

E[537b]

...

E[SEP]

[CLS]

d56f

...

[SEP]

537b

...

[SEP]

8805

...

61fa

de

61

+
+

Word Piece
d56f

Byte Pair
Encoding

Payload from
network layer (L3)

Raw Encrypted
3c18...
Traffic

6f01

d5

6f

01bb

bb88

01

88

bb

05

...

fa

d56 f0 1b b8 80 5e 2f3 f39 84 80 d8 0 ...

de 61 fa

d56 f0 1b b8 80 5e 2f3 f39 84 80 d8 0 ...

de 61 fa

Figure 2. Encrypted traffic preprocessing.
Figure 2. Encrypted traffic preprocessing.

3.3. Pre-Training
3.3. Pre-Training
Pre-training leverages unlabeled data to train the model to learn general representaunlabeled
data toare
train
the model into
to learn
general representationsPre-training
of encryptedleverages
traffic. Plaintext
payloads
transformed
unintelligible
ciphertext
tions
of
encrypted
traffic.
Plaintext
payloads
are
transformed
into
unintelligible
ciphertext
through encryption algorithms. Cryptographic implementation of encryption algorithms
through
algorithms.
Cryptographic
implementation
of encryption
algorithms
exhibits encryption
a certain degree
of non-complete
randomness
[33], indicating
a high information
exhibits
certain
of non-complete
randomness
[33], indicating
a high
information
content aand
highdegree
uncertainty
in the ciphertext.
Encryption
algorithms
(e.g.,
AES, etc.)
content
and
high
uncertainty
in
the
ciphertext.
Encryption
algorithms
(e.g.,
AES,
mix bytes from input plaintext blocks, enhancing the entropy of the ciphertext etc.)
and mix
also
bytes
from
input
plaintext
blocks,
enhancing
the
entropy
of
the
ciphertext
and
alsoitself
inincreasing the correlation between bytes within the blocks. Although the ciphertext
creasing
the
correlation
between
bytes
within
the
blocks.
Although
the
ciphertext
itself
appears random, there are still some abstract representations that can be learned by neuappears
random,
there
are still
some abstract
representations
canand
be learned
by neural
ral networks,
such
as the
frequency
of occurrence
of certainthat
bytes
the relationships
networks,
such asbytes.
the frequency
occurrence
of certainBERT’s
bytes and
the relationships
bebetween specific
Therefore,ofwe
directly introduce
original
pretraining task,
tween
bytes.the
Therefore,
we directly
BERT’s
original representations
pretraining task,
MLM, specific
and improve
original NSP
methodintroduce
to adapt to
the byte-level
of
the encrypted traffic.

Sensors 2024, 24, 3078

8 of 21

The model’s core structure is a BERT base [18], consisting of 12 Transformer [29]
Encoder modules. Each Encoder’s input and output vectors correspond one to one and
maintain consistent dimensions. Within each Encoder module, there are two sequential
sub-layers: the first is a multi-head self-attention mechanism, and the second is an FNN.
Both sub-layers employ residual connections followed by layer normalization.
To learn the contextual relationships of token embeddings, the MLM task randomly
masks part of the input tokens, and the output hidden layer vectors corresponding to the
masked tokens are computed in a fully connected layer to predict the actual tokens. A total
of 15% of the tokens in the input sequence are masked, with 80% replaced by [MASK], 10%
replaced by random tokens, and 10% unchanged. The negative log-likelihood function is
used as the loss function for this task, as shown in Equation (1):
M

L MLM (θ, θ MLM ) = − ∑ log P(tokeni |θ, θ MLM ) .

(1)

i =1

In this equation, θ denotes the parameter of the Encoder part, θ MLM is the parameter
of the fully connected layer of the MLM task, M is the number of randomly masked tokens,
and tokeni represents the token predicted by the model at position i of the sequence.
The mNSP task learns the matching relationship of payload by determining whether
two sub-sequences belong to the same packet. Unlike natural language, encrypted traffic
payloads are continuous byte streams without clear sentence demarcation or independent
meaning, so it is not feasible to divide them using punctuation as in natural language.
However, encrypted payloads from different plaintext have distinct ciphertext feature
distributions, allowing for us to determine whether two sub-sequences belong to the same
payload. In this task, payloads are divided into two nearly equal-length sub-sequences,
each ending with [SEP] to mark the end of the sub-sequence. The second sub-sequence
is replaced with another packet’s sub-sequence in 50% of cases. The complete input byte
sequence consists of [CLS] at the beginning followed by the two sub-sequences. The
output hidden layer vector corresponding to [CLS] is passed through a binary classifier to
determine whether the sub-sequences belong to the same packet. This classifier comprises
two fully connected layers. The negative log-likelihood function is used as the loss function
for this task, as indicated in Equation (2):
N

LmNSP (θ, θmNSP ) = − ∑ log P(y j θ, θmNSP ) .

(2)

j=1

In this equation, θmNSP is the binary classifier parameter followed by Encoder, N
is the number of input sequences, y j ∈ [0, 1] is the output result of the binary classifier
(1 represents paired sub-sequences and 0 represents unpaired ones).
The sum of the loss functions from both tasks is used to calculate the model loss for
gradient updates, as shown in Equation (3):
L(θ, θ MLM , θmNSP ) = L MLM (θ, θ MLM ) + LmNSP (θ, θmNSP ).

(3)

3.4. Fine-Tuning
During the fine-tuning phase, the model is trained on small-scale labeled datasets
for given tasks to learn task-specific representations. Adjusting all parameters in a pretrained model enables quick adaptation to downstream tasks. However, full parameter
fine-tuning in a pre-trained model demands high computational and memory resources.
As the model size and number of tasks increase, training and storing a new model for each
task exacerbates the issue of inefficient parameter use.
The PEFT method, particularly LoRA [20], effectively mitigates this problem. We
apply LoRA’s parallel matrix approach to the encrypted traffic classification model to

Sensors 2024, 24, 3078

The PEFT method, particularly LoRA [20], effectively mitigates this problem. We apply LoRA’s parallel matrix approach to the encrypted traffic classification model to conserve computational parameters. The advancement of LoRA over other PEFT methods in
encrypted traffic classification is shown in Section 4.6.
9 of 21
LoRA involves inserting matrices parallel to the pre-trained model matrices while
freezing the pre-trained model. This allows for the model to maintain new small-scale
parameter
matrices for downstream tasks. Unlike classic fine-tuning methods, the model
conserve computational parameters. The advancement of LoRA over other PEFT methods
can
switch PEFT
parameters
as in
needed
in encrypted
trafficmodule
classification
is shown
Sectionfor
4.6.different traffic classification tasks
without
replacing
the
entire
model’s
parameters,
parameter
utilization
LoRA involves inserting matrices parallel to theenhancing
pre-trained
model matrices
whileefficiency
and
reducing
deployment
and allows
switching
costs
for multi-task
models.
Compared to
freezing
the
pre-trained
model. This
for the
model
to maintain
new small-scale
other
PEFTmatrices
methods,
modules
compute
in parallel
with the
pre-trained
model,
parameter
for LoRA
downstream
tasks.
Unlike classic
fine-tuning
methods,
the model
avoiding
thePEFT
computational
bottlenecks
inference
delays traffic
of newclassification
serial modules.
can switch
module parameters
as and
needed
for different
tasks
without
replacing
theonly
entire
model’s
enhancing weight
parameter
utilization
efficiency
LoRA
updates
the
query parameters,
and value projection
matrix
of each
Encoder’s
and reducing
deployment
costsconnected
for multi-task
models.
Compared
to other
multi-head
attention
layer and
andswitching
the final fully
classifier
layer.
Specifically,
leverPEFT the
methods,
LoRA modules
compute
in parallel with
the pre-trained
model, avoiding
aging
low “intrinsic
rank” of
over-parametrized
models
[20], it employs
the product
the
computational
bottlenecks
and inference
delays
of new
modules.
of
two
low-rank matrices
to replace
the original
matrix
forserial
gradient
updates during backLoRA
updates
only
the
query
and
value
projection
weight
matrix
of each Encoder’s
propagation, as demonstrated in Equation (4).
multi-head attention layer and the final fully connected classifier layer. Specifically, leveraging the low “intrinsic rank” of over-parametrized
models[20], it employs the product of
h = W (i ) x + ΔWx = W ( i ) x + BAx .
(4)
two low-rank matrices to replace the original matrix for gradient
updates during backpropr
agation, as demonstrated in Equation (4).
(i )
d k
In this equation, W 
represents the projection weight matrix of layer i
α
(i )
(i )
h
=
W
x
+
∆Wx = W
x + BAx.A  r k , B  d r is used
(4) to
with rank r ( r  d , k ) selected, the product
of matrices
r
(i )
replace the updated weight
matrix ΔW of W , x is the input vector, h is the output
In this equation, W(i) ∈ Rd×k represents the projection weight matrix of layer i with
vector, and  is the deflation parameter of the updatedr×weight
matrix. We use a random
rank r (r << d, k) selected, the product of matrices A ∈ R k , B ∈ Rd×r is used to replace
(i )
(
i
)
Gaussian
initialization
for each
zero
for Bh. isWthe output
is kept vector,
frozen and
during
A and
the updated
weight matrix
∆W element
of W , xofis the
input
vector,
α istraining
the deflation
parameter
of the updated
weightand
matrix.
We use
the
process,
and gradients
are computed
updated
for aArandom
, B . Gaussian
) is kept frozen during the training
initialization
element of A and
zeroof
forLoRA,
B. W(iwe
Drawingfor
oneach
the computational
ideas
introduce this computational approcess,into
andour
gradients
computed
and updated
for A, B.
proach
model.are
Figure
3 illustrates
the computational
operation for a single EnDrawing
on
the
computational
ideas
of
LoRA,
we
introduce
this computational apcoder.
proach into our model. Figure 3 illustrates the computational operation for a single Encoder.
Output

y0

y1

...

y2

yN

Initialization
Add & Norm

Frozen

Feed Forward

Frozen

Add & Norm

Transformer
Encoder

Frozen

W(i)d×k

Multi-Head Attention
Frozen

Q

K

A = N (0, σ2)
B=0

Frozen
Parameters

B d×r
A r×k
Trainable Parameters

V

Frozen

Input

x0

x1

x2

...

xN

Figure 3. Fine-tuning computational diagram.

Figure 3. Fine-tuning computational diagram.

As for the fully connected classifiers, the classic LoRA method preserves the first
fully connected layer parameter of the pre-trained model’s NSP task classifier and allows
for only the second fully connected layer parameter to undergo gradient updating due
to the consideration of the relevance of the NLP fine-tuning task to the pre-training task.
However, because of the distinct association manner of encrypted traffic payloads compared
to natural language sentences, continuing to use the first fully connected layer might not
effectively synthesize feature information. Since the association between encrypted traffic

Sensors 2024, 24, 3078

10 of 21

payloads and natural language sentences differs, and different encryption algorithms
encrypt traffic with varying byte-level features, to accommodate these differences and
improve the model’s effectiveness, we design both fully connected layers of the classifier
subjected to gradient updates.
The loss function for the fine-tuning stage is formulated as shown in Equation (5).
k

L(θ A,B , θcls ) = − ∑ log P( predicti |θ, θ A,B , θcls ) .

(5)

i =1

Here, θA, B represent the parameters of all A and B, θcls is the classifier, θ is the
frozen parameters from the pre-trained model, k is the batch, and predicti is the classifier’s
prediction label.
4. Experiments
This section validates the advanced performance of the PETReLM from multiple
perspectives. We first introduce the datasets, experimental setup, and evaluation metrics
used in our experiments, then present the classification results of the model on these
datasets, and follow by ablation studies to prove the effectiveness of each module.
4.1. Datasets
For model pre-training and fine-tuning, we utilize various public encrypted traffic
datasets, each with its specific characteristics:
Browser2020 [4]: This dataset comprises traffic generated by accessing the top 1000 websites on Alexa using four different browsers: Google, Firefox, Samsung Internet, and UC.
Each website visit lasts for 15 s, with scripts simulating random clicks and browsing behavior.
CIC-IDS 2017 [34]: A network attack traffic dataset containing benign and malicious
traffic based on protocols like HTTP, HTTPS, FTP, and SSH. The traffic is segmented into
different time periods, each producing various types of traffic.
ISCXTor2017 [35]: A dataset focusing on The Onion Routing (Tor) traffic which includes eight different types of Tor traffic collected using onion routing.
ISCXVPN2016 [36]: A Virtual Private Network (VPN) traffic dataset that gathers traffic
generated by different types of applications under conditions of using or not using a VPN,
simulated between two hosts. This dataset is one of the most commonly used datasets
currently. The dataset categorizes encrypted applications into 17 classes and encrypted
services into 12 classes.
USTC-TFC2016 [37]: This dataset comprises malicious traffic collected in a real network
environment alongside normal traffic.
CIC IoT Dataset 2023 [38]: This dataset contains IoT attack traffic collected from a
topology consisting of 105 IoT devices. It includes both normal IoT traffic and network
attack traffic generated by 33 types of malicious IoT devices.
The granularity of encrypted traffic classification mainly includes a packet level and a
session level. Encrypted traffic sessions contain more information than individual packets.
However, it is challenging to obtain datasets with sufficient diversity and undisputed
ground truth [19]. Labeled encrypted traffic datasets may suffer from class sample imbalances, with limited samples collected for certain categories under constrained conditions.
For instance, in the ISCXVPN2016 dataset (see Table 2), the AIM and ICQ categories each
contain only 49 and 45 valid sessions, respectively (we consider a session to be valid if it
contains more than 4 packets). The limited samples may hinder deep learning models from
effectively learning sample representations. Therefore, we confine our study to packet-level
representation learning. We validate that valuable information about traffic can still be
obtained from packets. Additionally, packet-level traffic classification can alleviate the
problem of insufficiently labeled training samples.

Sensors 2024, 24, 3078

11 of 21

Table 2. Description of fine-tuning datasets.
Dataset

Task

Classes

Classification Basis

ISCXTor2017 [35]

ISCXT8

8

Tor Service

Audio, Browsing, Chat, FTP, Mail, P2P, Video, VoIP

ISCXS12

12

VPN Service

VPN: Email, Chat, Stream, File transfer, VoIP, P2P; Non-VPN:
Email, Chat, Stream, File transfer, VoIP, P2P

ISCXA17

17

VPN Application

AIM, Email, Facebook, FTP, Gmail, Hangouts, ICQ, Netflix, P2P,
SCP, SFTP, Skype, Spotify, tor, Vimeo, Voipbuster, Youtube

USTC20

20

Malware

Benign: BitTorrent, Facetime, FTP, Gmail, MySQL, Outlook,
Skype, SMB, Weibo, World of Warcraft; Malware: Cridex,
Geodo, Htbot, Miuref, Neris, Nsis-ay, Shifu, Tinba, Virut, Zeus

IoT Cyberattack

DDoS: ACK Fragmentation, HTTP Flood, ICMP Flood, ICMP
Fragmentation, PSHACK Flood, RSTFIN Flood, SlowLoris,
SynonymousIP Flood, SYN Flood, TCP Flood, UDP Flood, UDP
Fragmentation; Brute Force: Dictionary Brute Force; Spoofing:
ARP Spoofing, DNS Spoofing; DoS: HTTP Flood, SYN Flood,
TCP Flood, UDP Flood; Recon: Host Discovery, OS Scan, Ping
Sweep, Port Scan, Vulnerability Scan; Web Based: Backdoor
Malware, Browser Hijacking, Command Injection, SQL
Injection, Uploading Attack, XSS; Mirai: Greeth Flood, GREIP
flood, UDPPlain

ISCXVPN2016 [36]

USTC-TFC2016 [37]

CIC IoT Dataset 2023
CICIoT33
[38]

33

Specific Categories

For pre-training, we use benign traffic from Browser, CIC-IDS 2017, and the CIC
IoT Dataset 2023 as the pre-training dataset. This dataset comprises 955,000 unlabeled
traffic data, totaling 11.3 GB. For fine-tuning, we use datasets as shown in Table 2. It is
worth mentioning that our datasets encompass a wide range of protocols such as QUIC.
By selecting datasets that cover a variety of protocols, we aim to enable the model to learn
more general and effective representations. We select datasets from various classification
scenarios to validate the model’s performance. ISCXT8, ISCXS12, and ISCXA17 simulate
traffic classification in network management scenarios, while USTC20 and CICIoT33 simulate malicious traffic classification in network security scenarios. Our experiment ensures
the orthogonality between the pre-trained and fine-tuned datasets, simulating the scenario
where the model learns representations of encrypted traffic it has never seen before.
We select 5000 samples from each category in the fine-tuning dataset with a ratio of
8:1:1 for the training, validation, and test sets, respectively.
4.2. Experimental Settings
The experiments are conducted using the NVIDIA Tesla V100 GPU, with Python
version 3.10.12, CUDA version 11.7, and PyTorch version 1.13.0.
In BERT-base, each multi-head self-attention sublayer within the Encoders contains
12 attention heads. The dimension of the embedding vectors is set to 768, and the maximum
length for input vector sequences is 512.
During the model’s pre-training phase, the batch size is set to 32, with a total step
count of 500,000 and a learning rate of 2 × 10−5 . For the fine-tuning phase, the batch size
remains at 32, and the learning rate is adjusted to 8 × 10−4 . We consistently use AdamW as
the optimization tool. The deflation parameter of the updated weight matrix is set to 32,
and the rank for the weight update matrix is set to 4. The fine-tuning process is conducted
over 10 epochs.
By comparing the distribution of network layer payload lengths in each fine-tuning
dataset, we determine the specific truncation length. Figure 4 illustrates the distribution
of network layer payload lengths for the four fine-tuning datasets. We observe that the
payload distribution of the datasets mostly falls below 300 bytes, with some datasets
having a proportion of over 1000 bytes. As shown in Figure 2, since most byte pairs are
converted into one token and a byte appears in two adjacent byte pairs, it is reasonable to
approximate one byte as one token. If a larger value is chosen for the input token length, a

Sensors 2024, 24, 3078

ing a proportion of over 1000 bytes. As shown in Figure 2, since most byte
verted into one token and a byte appears in two adjacent byte pairs, it is
approximate one byte as one token. If a larger value is chosen for the input
of 21
a high proportion of samples requires padding with [PAD].12 Conversel
smaller value compromises the model’s ability to learn representations of t
layer
payload.
Considering
overall
of dataset
and
high
proportion
of samples
requires the
padding
with distribution
[PAD]. Conversely,
selecting apayloads
smaller
value
compromises
the model,
model’s ability
to learn
representations
thethe
application
layer
of the
pre-trained
we opt
to use
512 tokensofof
payload
as the m
payload. Considering the overall distribution of dataset payloads and the generality of the
length for pre-training. With TCP packets having a fixed header of 20 b
pre-trained model, we opt to use 512 tokens of the payload as the maximum input length
packets
having
anTCP
8-byte
header,
of comp
for
pre-training.
With
packets
having athis
fixedchoice
header ensures
of 20 bytesthe
and retention
UDP packets
having
an
8-byte
header,
this
choice
ensures
the
retention
of
complete
transport
layer
layer header information and most of the application layer encrypted paylo
header information and most of the application layer encrypted payload while mitigating
igating the impact of excessive [PAD] on model classification results.
the impact of excessive [PAD] on model classification results.

Figure 4. The network layer load length distribution of fine-tunning datasets.

Figure 4. The network layer load length distribution of fine-tunning datasets.

4.3. Evaluation Metrics
use classicMetrics
metrics to evaluate model performance, including Accuracy (Acc),
4.3.We
Evaluation

Precision (Pre), Recall (Rec), and F1-Score (F1). For binary classification problems, the
Weare
use
equations
as classic
follows: metrics to evaluate model performance, including Accur
cision (Pre), Recall (Rec), and F1-Score
TP + TN(F1). For binary classification proble
Acc =
(6)
TP
+
FP
+ FN + TN
tions are as follows:
TP
TP + FP

TP + TN
Acc =
TP TP + FP + FN + TN
Rec =
Pre =

TP + FN

(7)
(8)

Precision × Recall
Precision +Pre
Recall
=

(9)
TP
TP is+ true
FP negatives, and FN
where TP represents true positives, FP is false positives, TN
F1 = 2 ×

is false negatives. In multi-classification scenarios, we adopt the Macro Average [39]
method to calculate Precision, Recall, and F1-Score. It involves calculating these metrics for
TP
each category and then averaging the results. The Rec
accuracy
= metric is not affected by the
TP + FN
multi-class nature of the problem.
4.4. Performance Analysis

Precision  Recall

PETReLM’s performance is compared against
models based on deep learning
F1 = 2baseline

including 1D-CNN [11], Deep Packet [10], PERT [13], and
ET-BERT
The
Preci
sion + [14].
Recal
l motivation
for selecting these baseline models is that they represent typical deep learning methods
applied
encrypted
traffic true
classification.
Comparing
these baseline
models
can negati
wheretoTP
represents
positives,
FP is against
false positives,
TN
is true
objectively
demonstrate
the
performance
of
our
model.
These
models
are
replicated
with
false negatives. In multi-classification scenarios, we adopt the Macro Averag
their original structure and parameters, and their performance (in terms of Acc, F1) is
to calculate
Precision,
Recall,
and
F1-Score.
It in
involves
compared
with our
model across
various
datasets,
as shown
Table 3. calculating these m

category and then averaging the results. The accuracy metric is not affected
class nature of the problem.

Sensors 2024, 24, 3078

13 of 21

Table 3. Comparative experiment results of different methods.
Model
1D-CNN [11]
Deep Packet [10]
PERT [13]
ET-BERT [14]
PETReLM

ISCXT8

ISCXS12

ISCXA17

USTC20

CICIoT33

Acc

F1

Acc

F1

Acc

F1

Acc

F1

Acc

F1

0.9704
0.9722
0.9995
0.9998
0.9998

0.9709
0.9727
0.9995
0.9997
0.9997

0.9149
0.9169
0.9705
0.9785
0.9685

0.9147
0.9153
0.9706
0.9786
0.9686

0.9265
0.9154
0.9816
0.9911
0.9867

0.9181
0.9073
0.9782
0.9893
0.9830

0.7738
0.7911
0.9875
0.9940
0.9881

0.7508
0.7659
0.9876
0.9940
0.9881

0.7280
0.6987
0.8419
0.8065
0.8234

0.7307
0.7029
0.8400
0.8094
0.8247

Based on the experimental results, we observe that individual packets indeed contain
sufficient representations for distinguishing between traffic categories. Most methods are
effective in accurately classifying designed scenarios based on packet representations. Furthermore, convolutional deep learning methods (1D-CNN, Deep Packet) exhibit unstable
performance: they show significant discrepancies in performance on USTC20 and CICIoT33
datasets. There are two main reasons: (a) Convolutional neural networks have a relatively
narrow low-level field of view. Convolutions capture relationships between nearby bytes,
while distant relationships can only be learned at higher layers. Therefore, the overall byte
relationship extraction capability of convolutional methods may be lacking, resulting in
inferior representation extraction performance on complex datasets. (b) Convolutional
neural networks lack prior knowledge of encrypted traffic. Un-pretrained convolutional
methods cannot acquire universal representations of traffic and only learn proprietary
representations in limited datasets. The lack of incremental learning may also lead to
subpar performance.
In contrast, the excellent performance of pretraining-based methods highlights the
strong appeal of deep learning frameworks for encrypted traffic classification. Pretraining
models with large-scale parameters and architectures conducive for learning long sequences
are more suitable for encrypted traffic classification tasks. Specifically, ET-BERT and PERT
have similar structures and training methods. PERT uses the ALBERT architecture to
share all parameters between layers, resulting in performance fluctuations observed in the
ISCXA17 dataset. ET-BERT’s performance declines on the CICIoT33 dataset. Overall, the
PETReLM demonstrates more balanced performance across different application scenarios,
and it also performs similarly to the best baseline models.
At the same time, we identify potential limitations in our approach. From the classification results, we observe that the effectiveness of classifying IoT attack scenarios is
notably lower compared to other scenarios. As illustrated in Figure 5, the PETReLM classification heatmap reveals that the model nearly classifies all DoS SYN Flood traffic as
DDoS SYN Flood. This discrepancy arises because the primary difference between the
two attacks lies in the flood attack originating from multiple or fewer source hosts, which
may not be clearly evident at the level of individual packets. Similar issues are observed
with Command Injection, Uploading Attacks, and XSS, where all attacks involve similar
data transmission methods such as Web requests, and their application layer payloads
may also be comparable. These challenges extend to other confused categories, where the
representations of these categories within a single packet are similar, making them difficult
to distinguish. In summary, we find that the limitations of this approach may arise in
scenarios where the representation of individual packet is not sufficiently clear, and relying
solely on packet-level information may not effectively classify data accurately.

Sensors 2024, 24, 3078

arise in scenarios where the representation of individual packet14 ofis21not suﬃ
and relying solely on packet-level information may not eﬀectively classify d

Figure
5. Classification
heatmap
of IoT attack.
Figure
5. Classification
heatmap
of IoT attack.

4.5. Resource Usage Analysis

4.5. To
Resource
compare Usage
resourceAnalysis
usage, we take the USTC20 task as an example. We compare the

parameter scales of all baseline methods and also examine the GPU usage of pre-training
To compare resource usage, we take the USTC20 task as an example. W
models.
parameter
scales
all baseline
methods and
alsoaffect
examine
the GPU
Table 4 reveals
thatofsettings
of convolution-based
methods
the parameter
scale,usage o
5 . Pre-training methods have parameters scaled
with
an
average
magnitude
of
around
10
models.
1–2 orders of magnitude higher than convolutional methods. PERT reduces the parameter
Table 4 reveals that settings of convolution-based methods aﬀect the pa
scale by sharing parameters between layers, but fluctuates in performance. The PETReLM
5. Pre-training methods have para
with an
of around
10modules
reduces
theaverage
parametermagnitude
scale by inserting
additional
while maintaining stable
performance.
PETReLM’s
parameter
scale
accounts
for only 5.6% methods.
and 21.0% ofPERT
ET-BERT
1-2 orders of
magnitude
higher
than
convolutional
reduces
and PERT, respectively, and is in the same order of magnitude as small-scale convolutional
scale by sharing parameters between layers, but fluctuates in performance. T
models. The PETReLM utilizes the least GPU memory among pretrained models because
reduces
parameter
scale
by gradient
inserting
additional
modules
only
a smallthe
fraction
of parameters
accepts
updates,
reducing GPU
resource while
usage main
for
storing
gradients.
Updating
only
a
small
fraction
of
parameters
also
accelerates
model
performance. PETReLM’s parameter scale accounts for only 5.6% and 21.0
computation speed, reducing training time by 16.68% compared to ET-BERT. The PETReLM
and PERT, respectively, and is in the same order of magnitude a
is more suitable for multitask applications, as conventional methods require storing all
convolutional
Thewhile
PETReLM
utilizes
least
GPU
model
parameters models.
for each task,
the PETReLM
only the
needs
to store
the memory
inserted amo
modules
preserve task-specific
feature
extraction
task switching
modelstobecause
only a small
fraction
of capabilities.
parametersWhen
accepts
gradient upd
is needed, the PETReLM can quickly switch between different task scenarios by only
GPU resource usage for storing gradients. Updating only a small fraction
switching small modules.

also accelerates model computation speed, reducing training time by 16.68%
ET-BERT. The PETReLM is more suitable for multitask applications, as
methods require storing all model parameters for each task, while the P
needs to store the inserted modules to preserve task-specific featu
capabilities. When task switching is needed, the PETReLM can quickly sw
diﬀerent task scenarios by only switching small modules.

Sensors 2024, 24, 3078

15 of 21

Table 4. Parameter scales of different methods.
Trainable Parameters Pretraining Parameters Percentage (%)
1D-CNN [11]
Deep Packet [10]
PERT [13]
ET-BERT [14]
PETReLM

5.7 × 106
10.1 × 106
36.7 × 106
136.3 × 106
7.7 × 106

36.7 × 106
136.3 × 106
136.3 × 106

100
100
5.6

GPU (GB)
24.8
23.3
19.3

Overall, the PETReLM ensures that the model’s complexity is sufficient to learn the
basic representations of encrypted traffic while significantly reducing the required training
resources. It facilitates rapid task switching in multitask scenarios while maintaining
classification performance comparable to that of state-of-art models.
4.6. Ablation Analysis
To validate the effectiveness of our fine-tuning approach, we conduct ablation experiments focusing on two aspects:
(1)

(2)

Suitability of the modified LoRA for fine-tuning pre-trained models in encrypted traffic classification. We compare it with other traditional PEFT methods like Adapter [22],
Prefix Tuning [21], P-Tuning [25], and IA3 [24].
Applicability of using two fully connected layers as a classifier for encrypted traffic
classification. We compare two approaches: (i) Using a classifier composed of two
fully connected layers, where the first layer parameters from the mNSP task are
preserved and the second layer is subject to gradient updates (mNSP1 + FC2); (ii)
Using a classifier composed solely of one fully connected layer, which reduces the
input dimension to the classification dimension (FC1).

The experiments are conducted on the USTC20 dataset, and the results are presented
in Table 5.
Table 5. Comparison of ablation results.
Method

Acc

Pre

Rec

F1

Adapter
Prefix Tuning
P-Tuning
IA3
mNSP1 + FC2
FC1
PETReLM

0.9839
0.9706
0.8734
0.9698
0.9824
0.9861
0.9878

0.9842
0.9713
0.8816
0.9703
0.9824
0.9863
0.9888

0.9839
0.9706
0.8734
0.9698
0.9824
0.9861
0.9878

0.9839
0.9702
0.8722
0.9695
0.9817
0.9862
0.9877

The findings indicate that compared to other PEFT methods and classifier configurations, our model achieves superior results in encrypted traffic classification tasks. The
Adapter method is similar to the PETReLM in that both insert modules that function
to downscale and then upscale the input vectors to the output. The main difference is
that Adapter inserts serial parameter modules between layers while the PETReLM inserts
parallel parameter modules in the layers. IA3 reduces trainable parameters through vectorscaled activation. Prefix Tuning and P-Tuning construct prompts to minimize fine-tuning
parameters. The PETReLM shows improvement in F1-Score compared to these methods.
When comparing different classifier configurations, performance slightly drops with both
the original classifier and the use of a single fully connected layer as a classifier. Notably,
even with a 75% reduction in trainable parameter volume when using only one fully
connected layer, the performance exhibits only minor fluctuations. Therefore, employing
a single fully connected layer as a classifier also emerges as a balanced choice between
performance and resource utilization.

Sensors 2024, 24, 3078

16 of 21

5. Interpretability Analysis
This section analyzes the model’s matrix parameters using singular value decomposition, comparing the changes between pre-trained and fine-tuned model parameters
to explain the mechanism of learning traffic representations. We use the original pretrained model, the fully fine-tuned model, and the PETReLM for interpretability analysis,
aiming to explain the underlying learning mechanisms of the full fine-tuning and PEFT
methods by analyzing the correlations between model parameters in the pre-training and
fine-tuning phases.
5.1. Singular Value Analysis
The magnitude of the singular value corresponds to the importance of the left and
right singular vectors in a matrix. A large singular value indicates primary structures and
directions represented by their associated vectors. Singular values and singular vectors are
primarily used for interpretability analysis. In this section, we take the ISCXA17 task as
(i )

(i )

(i )

an example, and set W p , W f , and Wm to represent the query projection matrices of the
multi-head self-attention mechanism of the Encoder at layer i of the pre-trained model (p),
the fully fine-tuned model (f ), and the PETReLM (m), respectively. We merge PETReLM’s
parallel module with the pre-trained model to align the model sizes. The singular value
(i )

decomposition of matrix W p is as shown in Equation (10):
(i )

(i ) T

(i ) (i )

W p = U p Σ p (V p ) .

(10)

(i,j)

(i )

Setting the diagonal element σp represents the jth singular value of Σ p . We define
the magnification factor of the fine-tuned matrix’s jth singular value as the ratio of the jth
singular value of the fine-tuned matrix to the jth singular value of the pre-trained matrix.
For instance, the calculation formula of the jth singular value magnification factor for the
fully fine-tuned model is shown in (11):
(i,j)

f



(i )
(i )
W f , Wp , j



=

σf

(i,j)

.

(11)

σp
(i )

Figure 6a displays the jth singular value of W p for different values of i and j (represented as p-i in the figure), while Figure 6b shows the magnification factors (represented as
(i )

(i )

f -i, P-i in the figure) for W f and Wm . For brevity, only the first 10 singular values of the
odd-numbered layers are shown in the figures.
It can be observed that the singular values of the fully fine-tuned model and the pretrained model are closely aligned, increasing with layer number i, but they are generally
small in value. PETReLM significantly amplifies the first four singular values. Similar results
are observed in the value projection matrix and other matrices of the fully fine-tuned model.
Overall, the main features of the first layer query projection matrix of the pre-trained
model and the fully fine-tuned model are not pronounced, while the main features, especially in the last two layers near the output, are more prominent. The PETReLM amplifies
certain features of the original matrices to varying degrees. The magnification of singular
values in lower layers by the PETReLM is significantly higher than in higher layers, indicating substantial changes made by the PETReLM to the pre-trained model. The extent of
these changes is greater in extracting basic representations in lower layers compared to
abstract representations in higher layers.

Sensors 2024, 24, x FOR PEER REVIEW
Sensors 2024, 24, 3078

17 of 21
17 of 21

p-0
p-4
p-8

Singular values

3.5

p-2
p-6
p-10

3
2.5
2
1.5
1
0.5

25

Magnification factors

4

P-0
P-2
P-4
P-6
P-8
P-10

20
15

f-0
f-2
f-4
f-6
f-8
f-10

10
5
0

0
1

2

3

4

5

6

7

8

9

1

10

2

3

4

5

6

7

8

9

10

j-th Singular Value

j-th Singular Value

(a)

(b)

Figure
Figure6.6.Comparison
Comparisonof
ofsingular
singularvalues
valuesbetween
betweenpre-trained
pre-trainedand
andfine-tuned
fine-tunedmodels.
models.(a)
(a)Pre-trained
Pre-trained
model singular values of different layers; (b) Magnification factors of different fine-tuned matrix’s
model singular values of different layers; (b) Magnification factors of different fine-tuned matrix’s
singular values.
singular values.

5.2.
5.2.Subspace
SubspaceSimilarity
SimilarityAnalysis
Analysis
To
analyze
the
adjustments
madeby
bythe
thefine-tuned
fine-tuned
model
parameters
of the
To
the adjustments made
model
to to
thethe
parameters
of the
prepre-trained
model,
we
compare
the
feature
and
structural
similarity
of
matrices.
We
meastrained model, we compare the feature and structural similarity of matrices. We measure
ure
the similarity
by comparing
the overlap
of the subspaces
formed
byk ∈
the[1,first
the similarity
by comparing
the overlap
of the subspaces
formed by
the first
784]
kright
 [1,784]
right
singular
vectors
ofprojection
the query matrix
projection
matrix
in the first-layer
singular
vectors
of the
query
in the
first-layer
Encoder ofEncoder
the pretrained
model andmodel
the fine-tuned
model. The
normalized
matrix similarity
[40] is used
to
of
the pre-trained
and the fine-tuned
model.
The normalized
matrix similarity
[40]
calculate
the
subspace
similarity,
as
shown
in
(12):
is used to calculate the subspace similarity, as shown in (12):

∑ σi2 i 2
d (d
A,( B
A), B=) = i=1i =1
pp
p

p

pp== min
min{m,
m, n}.

(12)
(12)

mn
nn
Here, A
∈ Rl l ×
and B
∈ Rl l ×
representmatrices
matricescomposed
composedofofthe
thefirst
first mm and nnlA
B
Here,
and
represent
the
value
of
-dimensionalright
rightsingular
singularvectors,
vectors, respectively,
respectively, with
with σi ibeing
being
theithi singular
th singular
value
ldimensional
matrix AT B.T When the value of the normalized matrix similarity tends to one, it means
of matrix A B . When the value of the normalized matrix similarity tends to one, it means
that the subspaces formed by A, B have a high degree of overlap; equality to one means
that the subspaces formed by A , B have a high degree of overlap; equality to one
complete overlap; tendency to zero means low overlap; and equality to zero means no
means complete overlap; tendency to zero means low overlap; and equality to zero means
overlap at all.
no overlap at all.
Figure 7a,b shows the similarity of the subspaces formed by the first k right singular
Figure
7a,b shows
similarity
of the
subspaces
formed
the first kmodel
rightand
singuvectors
of each
layer ofthe
the
pre-trained
model
with the
fullyby
fine-tuned
the
lar
vectors
of
each
layer
of
the
pre-trained
model
with
the
fully
fine-tuned
model
and
the
PETReLM, respectively.
PETReLM,
respectively.
Each square
in the figure represents the similarity of the subspace consisting of the
Each
square
in the
figure represents
similarity
of the
subspace
consisting
of the
first k vectors of the
matrices.
The first 40the
singular
vectors
already
illustrate
the pattern
first
vectors
of
the
matrices.
The
first
40
singular
vectors
already
illustrate
the
pattern
k
well. The figure reveals that, apart from some fluctuations, the subspace similarity of the
well.
figure reveals
that, the
apart
from somemodel
fluctuations,
similarity
of the
fully The
fine-tuned
model with
pre-trained
remainsthe
at asubspace
high level.
The subspace
fully
fine-tuned
model
with
the
pre-trained
model
remains
at
a
high
level.
The
subspace
formed by the right singular vectors corresponding to the largest four singular values of the
formed
by and
the right
singular vectors
corresponding
the largest
four
singular number
values of
PETReLM
the pre-trained
model barely
overlap. to
However,
as the
dimension
of
the
PETReLM
and
the
pre-trained
model
barely
overlap.
However,
as
the
dimension
numthe subspace increases, the similarity rapidly grows, with most of the subspace formed by
ber
the
increases,
the similarity
grows,
of Similar
the subspace
the of
first
25subspace
singular values
overlapping.
Eachrapidly
layer shows
thewith
samemost
trend.
results
formed
by
the
first
25
singular
values
overlapping.
Each
layer
shows
the
same
trend. Simare observed for the left singular vectors.
ilar results are observed for the left singular vectors.

Sensors 2024, 24, x FOR PEER REVIEW

1

Sensors 2024, 24, 3078

Layer

18 of 21

11

0.084

0.853 0.659 0.702

10

0.084

0.561 0.828 0.784 0.892 0.902 0.909 0.932 0.963

0.952 0.974 0.950 0.957 0.941 0.927 0.932

9

0.952

0.927 0.904

0.936

0.894 0.928 0.823

0.885 0.866

0.905

0.907 0.923

0.904 0.901 0.892 0.892

8

0.963

0.931 0.937

0.921

0.895 0.920 0.922

0.834 0.910

0.915

0.860 0.906

0.892 0.884 0.901 0.875

7

0.941

0.925 0.948 0.952 0.908 0.946 0.872 0.893 0.891

0.900 0.922 0.882 0.878 0.890 0.892 0.890

6

0.959

0.926 0.865 0.877 0.863 0.904 0.826 0.837 0.872

0.881 0.898 0.893 0.878 0.894 0.892 0.900

5

0.928

0.507 0.734 0.875 0.908 0.921 0.815 0.846 0.844

0.889 0.923 0.923 0.909 0.905 0.892 0.903

4

0.931

0.582 0.801 0.751 0.917 0.928 0.936 0.935 0.845 0.909 0.927 0.867 0.893 0.883 0.883 0.900

3

0.904

0.929 0.669

2

0.982

0.952 0.824 0.863 0.758 0.817 0.895 0.817 0.877 0.893 0.851 0.866 0.865 0.875 0.864 0.862

1

0.992

0.977 0.924 0.843 0.902 0.926 0.858 0.927 0.864 0.863 0.905 0.870 0.856 0.857 0.856 0.867

0

0.839

0.924 0.883 0.810 0.677 0.660 0.701 0.731 0.710 0.683 0.722 0.822 0.827 0.839 0.851 0.879

1

2

3

0.835

4

0.895 0.941 0.945 0.936 0.961 0.966 0.966 0.937 0.955 0.942 0.940 0.932

0.911 0.902 0.883

5

6

7

0.907 0.917

8

9

0.914

10

0.899 0.891

15

0.875

0.625

0.375

0.899 0.882 0.883 0.890

20

25

30

35

0.125

40

The First k Right Singular Vectors

Layer

(a)

11

0.009 0.008 0.012 0.015 0.213 0.340 0.437 0.505 0.564 0.615 0.648 0.801 0.841 0.865 0.884 0.898

10

0.000 0.001 0.006 0.008 0.207 0.337 0.432 0.503 0.562 0.604 0.640 0.801 0.840 0.866 0.884 0.897

9

0.003 0.010 0.012 0.012 0.208 0.338 0.434 0.504 0.557 0.603

8

0.007 0.008 0.007 0.013 0.206 0.338 0.435 0.506 0.559 0.604 0.637 0.798 0.837 0.863 0.881 0.895

7

0.000 0.003 0.007 0.010 0.206 0.340 0.437 0.507 0.562 0.605 0.638 0.800 0.838 0.864 0.883 0.895

6

0.000 0.007 0.015 0.042 0.206 0.343 0.438 0.510 0.563 0.602 0.640 0.798 0.838 0.863 0.882 0.895

5

0.001 0.005 0.007 0.014 0.222 0.342 0.436 0.507 0.559 0.602 0.636 0.799 0.838 0.863 0.882 0.897

4

0.000 0.006 0.017 0.022 0.210 0.340 0.432 0.504 0.557 0.602 0.639 0.799 0.837 0.864 0.883 0.896

3

0.000 0.000 0.009 0.011 0.209 0.342 0.435 0.505 0.559 0.603 0.639 0.799 0.837 0.862 0.881 0.895

2

0.000 0.000 0.007 0.012 0.211 0.343 0.437 0.506 0.562 0.603 0.638 0.798 0.837 0.861 0.883 0.894

1

0.001 0.003 0.004 0.024 0.223 0.356 0.449 0.515 0.563 0.602 0.639 0.795 0.837 0.861 0.881 0.896

0

0.003 0.002 0.006 0.009 0.207 0.339 0.431 0.503 0.553 0.597 0.635 0.797 0.833 0.858 0.876 0.892
1

2

3

4

5

6

7

8

9

10

0637

15

0.875

0.798 0.838 0.864 0.881 0.895

20

25

30

35

0.625

0.375

0.125

40

The First k Right Singular Vectors

(b)

Figure7.
7. Subspace
Subspace similarity.
(a) Subspace
similarity
of the fully
fine-tuned
model with the
pre- with th
Figure
similarity.
(a) Subspace
similarity
of the
fully fine-tuned
model
trained
model;
(b)
Subspace
similarity
of
the
PETReLM
with
the
pre-trained
model.
trained model; (b) Subspace similarity of the PETReLM with the pre-trained model.

5.3. Summary of Interpretability Findings

5.3. Summary
of the
Interpretability
Findings
Combining
changes in singular
values and the subspace similarity between model

matrices,
we observe
thatchanges
the structure
featuresvalues
of the pre-trained
querysimilarity
projecCombining
the
in and
singular
and themodel’s
subspace
be
tion matrices are balanced and smooth. The matrices in the lowest layer are the smoothest,
model matrices, we observe that the structure and features of the pre-trained m
while the structure and features of the matrices in the higher layers are relatively more
query
projection
matrices
are balanced
and
smooth.features.
The matrices
in the lowest
lay
prominent,
with the
middle layers
having fewer
prominent
This characteristic
is

the smoothest, while the structure and features of the matrices in the higher laye
relatively more prominent, with the middle layers having fewer prominent feature
characteristic is more suitable for extracting general representations of traffic: the
layers use smoother matrices to extract general byte representations of the payloa

Sensors 2024, 24, 3078

19 of 21

more suitable for extracting general representations of traffic: the lower layers use smoother
matrices to extract general byte representations of the payload, the middle layers continually filter and process representations from byte representations to abstract features, and
the higher layers use matrices with more pronounced features to extract abstract features.
The fully fine-tuned model essentially maintains the structure and features of the pretrained model’s matrices, making only minor adjustments to the matrix structure. However,
since full fine-tuning alters the parameters of each matrix in the model, it is challenging to
observe the actual changes made by fine-tuning.
The PETReLM, by updating a minimal number of matrix parameters instead of the
full parameter set, allows for us to capture the subtle parameter changes at each layer,
reflecting the fine-tuning adjustments made to the parameters of the pre-trained model. The
PETReLM alters the model’s most crucial structure and features of the pre-trained model
while maintaining the essential structure and features. Specifically, at the microscopic
level, the matrix does not replicate the primary feature directions of the original matrix but
instead amplifies directions not emphasized in the original matrix. The amplification is
greater in the lower layers than in the higher layers. Macroscopically, this is reflected in
the rapid increase in subspace similarity within a certain range as the value of k increases.
Therefore, fine-tuning alters the overall feature extraction framework of the pre-trained
model, thoroughly changing the primary feature extraction pattern at each layer. This
includes more significant adjustments in the lower layers near the input for byte feature
extraction and relatively minor macroscopic changes in the higher layers for abstract feature
processing. This approach is more suitable for extracting specific traffic representations
for a given classification task, with the lower layers filtering and retaining representation
capabilities relevant to the given task and the higher layers focusing more on processing
abstract features related to the task.
6. Conclusions
Motivated by the need to achieve encrypted traffic functional service classification under limited conditions, we propose the PEFT-based encrypted traffic classification method,
the PETReLM. The method utilizes low-rank matrices instead of weight update matrices
for parameter fine-tuning, enabling precise functional classification at the packet level for
downstream tasks. We evaluate PETReLM’s generalization, robustness, and effectiveness
across various network analysis and network security scenarios, including Tor service
classification, VPN network service classification, VPN application classification, malware
classification, and IoT attack traffic classification. When compared with existing methods,
PETReLM maintains performance comparable to that of advanced models while reducing
the trainable parameters by 99.44%, effectively saving computational and storage resources
and reducing the deployment and switching costs of multi-task models. We explain the
underlying principles and mathematical logic of how the PETReLM extracts features from
the encrypted traffic, representing a novel attempt in encrypted traffic classification. We
find that the PETReLM changes the characteristics of model parameters so that parameter
hierarchy becomes distinct and the structure remains basically the same, which enhances
the interpretability of the model.
However, we also identify some limitations in our approach. Our method does not
consistently outperform existing state-of-the-art models in experimental performance.
Additionally, packet-level identification introduces inherent limitations to the classification
model. In scenarios where packet-level representations are not sufficiently effective, the
classification results may not be optimal. Therefore, designing a universal encrypted traffic
classification model may be more suitable for benign network environments in the field of
network application detection. For environments where malicious or deceptive traffic may
exist, more targeted designs are needed.
In the future, we hope to combine neural network model architectures with encrypted
traffic algorithms to analyze the representation extraction mechanisms of encrypted traffic,

Sensors 2024, 24, 3078

20 of 21

further improving model classification effectiveness, and providing a more universally
effective interpretative approach for encrypted traffic classification.
Author Contributions: Conceptualization, G.W. and Y.G.; methodology, G.W. and Y.G.; software,
G.W.; validation, G.W.; formal analysis, G.W.; investigation, G.W.; resources, G.W.; data curation, G.W.;
writing—original draft preparation, G.W.; writing—review and editing, G.W. and Y.G.; visualization,
G.W.; supervision, Y.G.; project administration, Y.G.; funding acquisition, Y.G. All authors have read
and agreed to the published version of the manuscript.
Funding: This research was funded by grant number 2023JC02 and the Fundamental Research Funds
for the Central Universities, grant number 2023JKF01ZK14.
Institutional Review Board Statement: Not applicable.
Informed Consent Statement: Not applicable.
Data Availability Statement: Data are contained within the article.
Conflicts of Interest: The authors declare no conflicts of interest.

References
1.

2.
3.
4.

5.
6.
7.
8.

9.
10.
11.

12.
13.

14.

15.
16.
17.

Isingizwe, D.F.; Wang, M.; Liu, W.; Wang, D.; Wu, T.; Li, J. Analyzing Learning-Based Encrypted Malware Traffic Classification
with AutoML. In Proceedings of the 2021 IEEE 21st International Conference on Communication Technology (ICCT), Tianjin,
China, 13 October 2021; pp. 313–322. [CrossRef]
Lin, K.; Xu, X.; Gao, H. TSCRNN: A Novel Classification Scheme of Encrypted Traffic Based on Flow Spatiotemporal Features for
Efficient Management of IIoT. Comput. Netw. 2021, 190, 107974. [CrossRef]
Papadogiannaki, E.; Ioannidis, S. A survey on encrypted network traffic analysis applications, techniques, and countermeasures.
ACM Comput. Surv. (CSUR) 2021, 54, 123. [CrossRef]
Van Ede, T.; Bortolameotti, R.; Continella, A.; Ren, J.; Dubois, D.J.; Lindorfer, M.; Choffnes, D.; Van Steen, M.; Peter, A. FlowPrint:
Semi-Supervised Mobile-App Fingerprinting on Encrypted Network Traffic. In Network and Distributed System Security Symposium;
Internet Society: San Diego, CA, USA, 2020. [CrossRef]
Taylor, V.F.; Spolaor, R.; Conti, M.; Martinovic, I. Robust smartphone app identification via encrypted network traffic analysis.
IEEE Trans. Inf. Forensics Secur. 2017, 13, 63–78. [CrossRef]
Conti, M.; Mancini, L.V.; Spolaor, R.; Verde, N.V. Analyzing Android Encrypted Network Traffic to Identify User Actions. IEEE
Trans. Inform. Forensic Secur. 2016, 11, 114–125. [CrossRef]
Shen, M.; Wei, M.; Zhu, L.; Wang, M. Classification of Encrypted Traffic With Second-Order Markov Chains and Application
Attribute Bigrams. IEEE Trans. Inform. Forensic Secur. 2017, 12, 1830–1843. [CrossRef]
Yu, T.; Zou, F.; Li, L.; Yi, P. An Encrypted Malicious Traffic Detection System Based on Neural Network. In Proceedings of the
2019 International Conference on Cyber-Enabled Distributed Computing and Knowledge Discovery (CyberC), Guilin, China,
17–19 October 2019; pp. 62–70. [CrossRef]
Shen, M.; Zhang, J.; Zhu, L.; Xu, K.; Du, X. Accurate Decentralized Application Identification via Encrypted Traffic Analysis
Using Graph Neural Networks. IEEE Trans. Inform. Forensic Secur. 2021, 16, 2367–2380. [CrossRef]
Lotfollahi, M.; Jafari Siavoshani, M.; Shirali Hossein Zade, R.; Saberian, M. Deep Packet: A Novel Approach for Encrypted Traffic
Classification Using Deep Learning. Soft Comput. 2020, 24, 1999–2012. [CrossRef]
Wang, W.; Zhu, M.; Wang, J.; Zeng, X.; Yang, Z. End-to-End Encrypted Traffic Classification with One-Dimensional Convolution
Neural Networks. In Proceedings of the 2017 IEEE International Conference on Intelligence and Security Informatics (ISI), Beijing,
China, 22–24 July 2017; pp. 43–48. [CrossRef]
Jiang, T.; Yin, W.; Cai, B.; Zhang, K. Encrypted malicious traffic identification based on hierarchical spatiotemporal feature and
multi-head attention. Comput. Eng. 2021, 47, 101–108. [CrossRef]
He, H.; Yang, Z.; Chen, X. PERT: Payload Encoding Representation from Transformer for Encrypted Traffic Classification. In
Proceedings of the 2020 ITU Kaleidoscope: Industry-Driven Digital Transformation (ITU K), Online, 7–11 December 2020; pp. 1–8.
[CrossRef]
Lin, X.; Xiong, G.; Gou, G.; Li, Z.; Shi, J.; Yu, J. ET-BERT: A Contextualized Datagram Representation with Pre-Training
Transformers for Encrypted Traffic Classification. In Proceedings of the ACM Web Conference 2022, Lyon, France, 25–29 April
2022; pp. 633–642. [CrossRef]
Aceto, G.; Ciuonzo, D.; Montieri, A.; Pescapè, A. DISTILLER: Encrypted traffic classification via multimodal multitask deep
learning. J. Netw. Comput. Appl. 2021, 183–184, 102985. [CrossRef]
Wang, P.; Chen, X.; Ye, F.; Sun, Z. A survey of techniques for mobile service encrypted traffic classification using deep learning.
IEEE Access 2019, 7, 54024–54033. [CrossRef]
Chen, Z.; Cheng, G.; Xu, Z. A survey on Internet encrypted traffic detection classification and identification. Chin. J. Comput. 2023,
46, 1060–1085. [CrossRef]

Sensors 2024, 24, 3078

18.

19.
20.
21.
22.

23.
24.
25.
26.
27.
28.

29.
30.
31.
32.
33.
34.

35.

36.

37.

38.
39.
40.

21 of 21

Devlin, J.; Chang, M.; Lee, K.; Toutanova, K. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
In Proceedings of the Conference of the North American Chapter of the Association for Computational Linguistics (NAACL),
Minneapolis, MN, USA, 2–7 June 2019; pp. 4171–4186. [CrossRef]
Shen, M.; Ye, K.; Liu, X.; Zhu, L.; Kang, J.; Yu, S.; Li, Q.; Xu, K. Machine Learning-Powered Encrypted Network Traffic Analysis: A
Comprehensive Survey. IEEE Commun. Surv. Tutor. 2023, 25, 791–824. [CrossRef]
Hu, E.J.; Shen, Y.; Wallis, P.; Allen-Zhu, Z.; Li, Y.; Wang, S.; Wang, L.; Chen, W. Lora: Low-rank adaptation of large language
models. arXiv 2021, arXiv:2106.09685.
Kang, P.; Yang, H.; Ma, H. TLS Malicious Encrypted Traffic Identification Research. J. Comput. Eng. Appl. 2022, 58, 11. [CrossRef]
Gehring, J.; Miao, Y.; Metze, F.; Waibel, A. Extracting Deep Bottleneck Features Using Stacked Auto-Encoders. In Proceedings of
the 2013 IEEE International Conference on Acoustics, Speech and Signal Processing, Vancouver, BC, Canada, 26–31 May 2013; pp.
3377–3381. [CrossRef]
Huang, Z.; Xu, W.; Yu, K. Bidirectional LSTM-CRF models for sequence tagging. arXiv 2015, arXiv:1508.01991.
Kim, Y. Convolutional neural networks for sentence classification. arXiv 2014, arXiv:1408.5882.
Lan, Z.; Chen, M.; Goodman, S.; Gimpel, K.; Sharma, P.; Soricut, R. ALBERT: A Lite BERT for Self-supervised Learning of
Language Representations. arXiv 2019, arXiv:1909.11942.
Pfeiffer, J.; Kamath, A.; Rücklé, A.; Cho, K.; Gurevych, I. AdapterFusion: Non-destructive task composition for transfer learning.
arXiv 2020, arXiv:2005.00247.
Li, X.L.; Liang, P. Prefix-Tuning: Optimizing Continuous Prompts for Generation. arXiv 2021, arXiv:2101.00190.
Houlsby, N.; Giurgiu, A.; Jastrzebski, S.; Morrone, B.; de Laroussilhe, Q.; Gesmundo, A.; Attariyan, M.; Gelly, S. Parameter-efficient
transfer learning for nlp. In Proceedings of the International Conference on Machine Learning (ICML), Long Beach, CA, USA,
9–15 June 2019.
Vaswani, A.; Shazeer, N.; Parmar, N.; Uszkoreit, J.; Jones, L.; Gomez, A.; Kaiser, L.; Polosukhin, I. Attention is all you need. Adv.
Neural Inf. Process. Syst. 2017, 30, 5998–6008.
Liu, H.; Tam, D.; Muqeeth, M.; Mohta, J.; Huang, T.; Bansal, M.; Raffel, C. Few-Shot Parameter-Efficient Fine-Tuning is Better and
Cheaper than In-Context Learning. In Proceedings of the NeurIPS, New Orleans, LA, USA, 28 November–9 December 2022.
Liu, X.; Zheng, Y.; Du, Z.; Ding, M.; Qian, Y.; Yang, Z.; Tang, J. GPT understands, too. arXiv 2021, arXiv:2103.10385. [CrossRef]
Wu, Y.; Schuster, M.; Chen, Z.; Le, Q.V.; Norouzi, M.; Macherey, W.; Krikun, M.; Cao, Y.; Gao, Q.; Macherey, K.; et al. Google’sneural
machine translation system: Bridging the Gap between human and machine translation. arXiv 2016, arXiv:1609.08144.
Doğanaksoy, A.; Ege, B.; Koc¸ak, O.; Sulak, F. Cryptographic randomness testing of block ciphers and hash functions. Cryptol.
Eprint Arch. 2010. Available online: https://eprint.iacr.org/2010/564 (accessed on 14 April 2024).
Sharafaldin, I.; Habibi Lashkari, A.; Ghorbani, A.A. Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic
Characterization: In International Conference on Information Systems Security and Privacy; SCITEPRESS-Science and Technology
Publications: Funchal, Madeira, Portugal, 2018; pp. 108–116. [CrossRef]
Lashkari, A.; Draper Gil, G.; Mamun, M.S.I.; Ghorbani, A.A. Characterization of Tor Traffic Using Time Based Features: In 3rd
International Conference on Information Systems Security and Privacy; SCITEPRESS-Science and Technology Publications: Porto,
Portugal, 2017; pp. 253–262. [CrossRef]
Draper-Gil, G.; Lashkari, A.H.; Mamun, M.S.I.; Ghorbani, A.A. Characterization of Encrypted and VPN Traffic Using Time-Related Features: In 2nd International Conference on Information Systems Security and Privacy; SCITEPRESS-Science and Technology Publications:
Rome, Italy, 2016; pp. 407–414. [CrossRef]
Wang, W.; Zhu, M.; Zeng, X.; Ye, X.; Sheng, Y. Malware Traffic Classification Using Convolutional Neural Network for Representation Learning. In Proceedings of the 2017 International Conference on Information Networking (ICOIN), Da Nang, Vietnam,
11–13 January 2017; pp. 712–717. [CrossRef]
Neto, E.C.P.; Dadkhah, S.; Ferreira, R.; Zohourian, A.; Lu, R.; Ghorbani, A.A. CICIoT2023: A Real-Time Dataset and Benchmark
for Large-Scale Attacks in IoT Environment. Sensors 2023, 23, 5941. [CrossRef]
Liu, C.; Wang, W.; Wang, M.; Lv, F.; Konan, M. An Efficient Instance Selection Algorithm to Reconstruct Training Set for Support
Vector Machine. Knowl.-Based Syst. 2017, 116, 58–73. [CrossRef]
Hamm, J.; Lee, D.D. Grassmann discriminant analysis: A unifying view on subspace-based learning. In Proceedings of the 25th
International Conference on Machine Learning, Helsinki, Finland, 5–9 July 2008; pp. 376–383. [CrossRef]

Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
PAPER_TEXT
