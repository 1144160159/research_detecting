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
# [222] Fast and Accurate Multi-Task Learning for Encrypted Network Traffic Classification
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
编号：222
题名：Fast and Accurate Multi-Task Learning for Encrypted Network Traffic Classification
年份：2024
DOI：10.3390/app14073073
来源：Applied Sciences
PDF：paper/10.3390_app14073073.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 14
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\222.txt
- 原始字符数：86105
- 本次发送字符数：86105
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
applied
sciences
Article

Fast and Accurate Multi-Task Learning for Encrypted Network
Traffic Classification
Jee-Tae Park 1 , Chang-Yui Shin 2 , Ui-Jun Baek 1 and Myung-Sup Kim 1, *
1

2

*

Department of Computer and Information Science, Korea University, Sejong 30019, Republic of Korea;
pjj5846@korea.ac.kr (J.-T.P.); pb1069@korea.ac.kr (U.-J.B.)
C4ISR System Development Quality Research Team, Defense Agency for Technology and Quality,
Daejeon 35409, Republic of Korea; superego99@dtaq.re.kr
Correspondence: tmskim@korea.ac.kr

Abstract: The classification of encrypted traffic plays a crucial role in network management and
security. As encrypted network traffic becomes increasingly complicated and challenging to analyze,
there is a growing need for more efficient and comprehensive analytical approaches. Our proposed
method introduces a novel approach to network traffic classification, utilizing multi-task learning
to simultaneously train multiple tasks within a single model. To validate the proposed method,
we conducted experiments using the ISCX 2016 VPN/Non-VPN dataset, consisting of three tasks.
The proposed method outperformed the majority of existing methods in classification with 99.29%,
97.38%, and 96.89% accuracy in three tasks (i.e., encapsulation, category, and application classification,
respectively). The efficiency of the proposed method also demonstrated outstanding performance
when compared to methods excluding lightweight models. The proposed approach demonstrates
accurate and efficient multi-task classification on encrypted traffic.
Keywords: encrypted traffic classification; multi-task classification; BERT; transformer

1. Introduction
Citation: Park, J.-T.; Shin, C.-Y.; Baek,
U.-J.; Kim, M.-S. Fast and Accurate
Multi-Task Learning for Encrypted
Network Traffic Classification. Appl.
Sci. 2024, 14, 3073. https://doi.org/
10.3390/app14073073
Academic Editor: Stefan Fischer
Received: 6 March 2024
Revised: 29 March 2024
Accepted: 3 April 2024
Published: 5 April 2024

Copyright: © 2024 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license (https://
creativecommons.org/licenses/by/

The advancement of science and technology and ultra-high-speed networks is accompanied by the rise of various applications. With the advancement of modern network
technologies such as cloud computing and edge computing, research on efficient network
management has been actively conducted. Among them, network traffic classification
research is one of the key factors for efficient network management [1–5].
Traffic classification methods encompass traditional, signature-based, learning-based,
and transformer-based approaches [3–8]. Traditional methods rely on port-based and
payload-based techniques. Port-based classification uses origin and destination ports,
offering simplicity and low computational cost, but it faces limitations with dynamic
ports. Payload-based classification utilizes fixed payload content, providing simplicity
and high performance, but it is susceptible to encrypted traffic and struggles to adapt to
new protocols [9]. Signature-based methods classify traffic based on specific patterns or
signatures, demonstrating high performance for defined signatures. However, they face
challenges in adapting to changing patterns and encrypted traffic. Overall, network traffic
classification research plays a key role in enhancing efficient network management amid
evolving technological landscapes.
With recent advances in AI and technologies, most studies are using learning-based
methods [10–32]. Learning-based methods utilize machine learning (ML) and deep learning
(DL) algorithms to learn and classify traffic. Models are trained on large amounts of traffic
data to identify specific patterns or trends, which are then used to predict or classify new
traffic. Due to these advantages, many studies have utilized learning-based methods, and
they have improved performance in many areas.

4.0/).

Appl. Sci. 2024, 14, 3073. https://doi.org/10.3390/app14073073

https://www.mdpi.com/journal/applsci

Appl. Sci. 2024, 14, 3073

2 of 23

Transformer-based methods are one of the more recent deep learning techniques to
emerge, applying structures that have performed particularly well in natural language
processing (NLP) for traffic classification [33–36]. The self-attention mechanism of the
transformer effectively learns the global dependencies of sequence data, which has shown
promising performance in a variety of applications. For instance, the field of NLP has
witnessed a notable advancement with the introduction of bidirectional encoder representation from transformers (BERT) pre-training models [35,36]. BERT has demonstrated high
performance in many fields and can be effectively applied to downstream tasks by learning
relationships and structures for unbiased data from unlabeled data. In line with this trend,
many studies have been conducted in the field of network traffic classification by applying
transform-based methods. These methods have shown higher performance than traditional
learning-based methods.
With the growing concerns regarding personal privacy and security, most applications
now utilize encrypted traffic [37–39]. As encrypted communications protect payload
content, traditional traffic classification methods have become inapplicable. Researchers
use publicly available encrypted traffic datasets such as ISCX 2016 VPN/Non-VPN [40].
for encrypted traffic classification studies. In these encrypted traffic classification studies,
public datasets are mainly divided into intrusion detection systems (IDS) and application
classification, each of which is in turn divided into specific tasks. For example, the ISCX
2016 VPN/Non-VPN, which is often used for application classification studies, consists of
three tasks: encapsulation, category, and application.
Traffic classification methods are categorized into single-task learning (STL) and
multi-task learning (MTL) based on the target data task. STL focuses on training a model
for a specific task in machine learning, enhancing performance by learning task-specific
features and patterns. However, this optimized model may have limited applicability to
other tasks. On the other hand, MTL involves training a model on multiple related tasks,
utilizing shared representations to improve overall performance. MTL shares common
low-level features across tasks while incorporating task-specific high-level features. This
approach is valuable for diverse yet interrelated tasks, leading to more efficient and effective
learning [41–43].
Most network traffic classification research has traditionally used STL, and while
classification performance has improved, there are some limitations to applying traditional
STL. First, the evolving complexity of networks, including intricate network traffic patterns,
new network environments, applications, and encryption technologies, has challenged the
applicability of traditional STL. Second, STL requires training a separate model for each task,
which is time and resource intensive. Third, malicious activity on the network is becoming
increasingly sophisticated. Attackers are adept at evading or defeating traditional security
methods, requiring more detailed analysis that is more diverse and broader than traditional
research. Therefore, it is essential to study traffic classification with MTL, which can address
the limitations of traditional research by analyzing network traffic more comprehensively
and in-depth compared to STL.
In this paper, we propose a multi-task classification method utilizing DistilBERT [36],
a variant of the BERT model within a transformer architecture, for classifying encrypted
traffic. This approach enables the performance of traffic classification for various tasks with
a single training, using BERT. Our contributions can be summarized as follows:

•

•

We adopt a multi-task learning (MTL) approach for encrypted traffic classification,
leveraging the DistilBERT model. The proposed method is based on a model that
can handle multiple classification tasks simultaneously. The proposed method allows
for a thorough and detailed analysis of encrypted network traffic, addressing the
complexity of various tasks within a unified training framework.
To validate our proposed method, we conducted verification experiments, focusing
on three specific tasks using the ISCX 2016 VPN/Non-VPN dataset. We compared
our approach with other methods, assessing classification accuracy and efficiency. In
terms of classification accuracy, we demonstrated average accuracies ranging from

Appl. Sci. 2024, 14, x FOR PEER REVIEW
Appl. Sci. 2024, 14, 3073

3 of 23
3 of 23

terms
of modelacross
eﬃciency,
our outperforming
approach showed
per
samplemethods.
processing
96.89~99.29%
all tasks,
the favorable
majority of
existing
In
time
compared
to
existing
models.
Through
our
experiment
results,
we
validate
terms of model efficiency, our approach showed favorable per sample processing that
time
our
proposed
method,models.
employing
multi-task
classification
for encrypted
traﬃc,
is our
efcompared
to existing
Through
our experiment
results,
we validate
that
fective
in
terms
of
both
classification
performance
and
eﬃciency.
proposed method, employing multi-task classification for encrypted traffic, is effective

We
applied
weight
adjustments
(class weight,
task
weight) within the model to solve
in terms
of both
classification
performance
and
efficiency.
related
to data imbalance
and varying
task diﬃculty.
We problems
applied weight
adjustments
(class weight,
task weight)
within theThrough
model toaddisolve
• the
tional
experiments,
we
validated
the
impact
of
both
weights
on
performance
imthe problems related to data imbalance and varying task difficulty. Through additional
provement.
This
underscores
the
eﬀectiveness
of
our
approach
in
diverse
scenarios,
experiments, we validated the impact of both weights on performance improvement.
enhancing
its applicability
across various
situations.in diverse scenarios, enhancing its
This underscores
the effectiveness
of our approach
applicability
situations.
The
remainderacross
of thisvarious
paper is
organized as follows. In Section 2, we will describe the
related
work,
and in of
Section
3, weiswill
provideasa follows.
detailed In
explanation
The
remainder
this paper
organized
Section 2, of
wethe
willproposed
describe
method.
In Section
4, we
conduct3,an
byausing
theexplanation
ISCX 2016 VPN/Non-VPN
the related
work, and
in Section
weexperiment
will provide
detailed
of the proposed
dataset,
classification
experiment,
we will
discuss
several ismethod.including
In Sectiona 4,multi-task
we conduct
an experiment
by usingand
the ISCX
2016
VPN/Non-VPN
sues
in Section
5. Finally,
we conclude
the paper
and outline
future
directions
in
dataset,
including
a multi-task
classification
experiment,
and we
willresearch
discuss several
issues
Section
6. 5. Finally, we conclude the paper and outline future research directions in
in Section
Section 6.
2. Related Works
2. Related Works
2.1. Overview of the Network Traﬃc Classification
2.1. Overview of the Network Traffic Classification
Network traﬃc classification research is the study of analyzing the traﬃc generated
Network traffic classification research is the study of analyzing the traffic generated
by computer communications, which is essential for the eﬀective management, monitorby computer communications, which is essential for the effective management, monitoring,
ing, and security of computer networks. As shown in Figure 1, network traﬃc classificaand security of computer networks. As shown in Figure 1, network traffic classification
tion research is broadly classified according to the field of research, methodology, classiresearch is broadly classified according to the field of research, methodology, classification
fication level, and data units processed.
level, and data units processed.

Figure1.1.Overview
Overviewof
ofthe
thenetwork
networktraﬃc
trafficclassification.
classification.
Figure

First,in
interms
termsof
ofresearch
researchareas,
areas,ititconsists
consistsof
ofvarious
varioussubfields,
subfields,including
includingapplication
application
First,
classification
[10–26],
malicious
traffic
detection
[29–32],
user
behavior
profiling
[27–30],
classification [10–26], malicious traﬃc detection [29–32], user behavior profiling [27–30],
and
web
fingerprinting
[44–46],
of
which
application
classification
and
malicious
traffic
and web fingerprinting [44–46], of which application classification and malicious traﬃc
detection
are
the
most
widely
studied.
Second,
in
terms
of
methodologies,
methods
such
detection are the most widely studied. Second, in terms of methodologies, methods such
as port-based and payload-based methods have traditionally been widely used. Portas port-based and payload-based methods have traditionally been widely used. Portbased classification categorizes traffic based on known port numbers, which is inapplicable
based classification categorizes traﬃc based on known port numbers, which is inapplicabecause many applications use dynamic ports. Payload-based methods classify applicable because many applications use dynamic ports. Payload-based methods classify applitions based on fixed payload content. Signature-based methods extend the mechanisms
cations based on fixed payload content. Signature-based methods extend the mechanisms
of payload-based methods to various traffic characteristics, defining common statistical,
of payload-based methods to various traﬃc characteristics, defining common statistical,
header, and behavioral characteristics of traffic as signatures and classifying based on
header, and behavioral characteristics of traﬃc as signatures and classifying based on
them. Both payload-based and signature-based methods perform poorly on encrypted
them. Both payload-based and signature-based methods perform poorly on encrypted
traffic. To solve these limitations, learning-based methods using machine learning and deep
traﬃc. To solve these limitations, learning-based methods using machine learning and
learning are the most active, and recently, methods using transformer models have also
deep learning are the most active, and recently, methods using transformer models have
been performed. Third, in terms of classification level, it consists of the following levels:
also been performed. Third, in terms of classification level, it consists of the following
application classification, which distinguishes each application; service classification, which

Appl. Sci. 2024, 14, 3073

4 of 23

categorizes the detailed features, services, and behaviors of the application; application
type classification, which categorizes the characteristics of the application such as Chat
or File Transfer; and encryption classification, which categorizes the presence or absence
of encryption. Fourth, in terms of data units, it is categorized into unidirectional and
bidirectional flows, packets, and bursts. A flow is a set of packets with the same 5-tuples
of information in the packet header, and a burst is a set of time-adjacent network packets
originating from either the request or the response in a single-session flow [34].
As mentioned before, we propose a multi-task classification method for encrypted
traffic using DistilBERT to perform encapsulation, application type, and application classification on ISCX 2016 VPN/Non-VPN data. In Figure 1, the green-colored parts represent
the four aspects of our proposed method.
2.2. Encrypted Traffic Classification
Network traffic classification has been around for a long time and has primarily utilized traditional methods based on port and payload, as well as signature-based methods.
However, traditional traffic analysis methods are ineffective because many modern applications, including mobile, cloud, and IoT, rely primarily on encrypted traffic. To address the
limitations of traditional methods, recent research has turned to learning-based approaches
involving ML and DL [10–25].
In [10], Lotfollahi et al. introduced Deep Packet, a system that utilizes a stacked
autoencoder and CNN. They achieved an impressive F1 score of 98% for application
identification on the ISCX 2016 VPN/Non-VPN dataset. Wang et al. [11] introduced a
novel method to convert packets into images and process them using 1D-CNN, which
showed promising results on ISCX 2016 VPN/Non-VPN. In [12], Zou et al. pre-sent an
encrypted network traffic classification approach using CNNs and LSTM networks; in [13],
they proposed an innovative fusion of CNNs and designed RNNs for service recognition
in IoT traffic; in [14], they used naïve Bayes, C4. 5 decision trees, Bayesian networks, and
naive Bayes trees. They performed a comprehensive analysis comparing the performance
of these algorithms using 22 features extracted from network flows. In [15], they introduced
flow sequence network (FS-NET) for encrypted traffic classification. FS-NET utilizes
both RNNs and a multi-layer encoder–decoder structure. In [16], the authors proposed
FlowPic, a classification method that converts consecutive packet sizes in a flow into a
two-dimensional gray image and uses CNNs for classification. While FlowPic is simple
and performs well, it is not suitable for real-time traffic classification because it requires the
capture of traffic over a long period of time. The authors also note that it is not applicable
to classifying some encrypted traffic. In [17], the authors proposed TSCRNN, which
automatically extracts features for efficient traffic classification based on spatiotemporal
features. To validate the proposed method, the authors conducted experiments on ISCX
Tor 2016 data and obtained high accuracy. In [18], the authors proposed MIMETIC, which
exploits traffic data heterogeneity by learning both intra- and inter-modality dependencies
to overcome performance limitations. MIMETIC outperforms single-modality DL-based,
state-of-the-art ML-based mobile traffic classifiers. In [19], the authors propose an improved
DAGSVM classification method by focusing on the error accumulation of the traditional
DAGSVM algorithm. Experimental results show that the proposed method has higher
classification accuracy than traditional DAGSVM while having an acceptable time cost. The
studies in [39] and [47] have conducted research with a focus on lightweight models rather
than classification performance. While most studies primarily emphasize performance, they
highlight the importance of lightweight approaches for handling large-scale traffic data.
In recent years, there has been a surge in research centered on transformer architectures
characterized by self-attention and multi-headed attention mechanisms. Transformerstructured models mainly utilize the BERT model, which has proven to show strong
performance in the NLP field, but recently, research has also been conducted using the
masked autoencoder (MAE), which is used in the CV field [33–35].

Appl. Sci. 2024, 14, 3073

5 of 23

In [34], the authors proposed ET-BERT, a novel approach inspired by transformer architectures. It presents a new pre-training method designed for encrypted traffic classification
and fine-tuned for optimal performance achieving an accuracy of over 97%. In [21], the
authors propose a method called PERT (payload encoding representation from transformer)
utilizing dynamic word embedding. PERT outperforms other methodologies on publicly
available encrypted traffic datasets and captures Android HTTPS traffic. In [22], the authors
propose the BFCN model, which combines BERT and CNN models to derive global traffic
features with a pre-trained BERT model and byte-level local traffic features with a CNN
model. The experimental results show F1 scores of 99.11% and 99.41% in the traffic service
and application identification tasks operating on the ISCX 2016 VPN/Non-VPN dataset,
respectively. In [23], similar to [22], a pre-trained BERT model and a bidirectional LSTM
are applied together, with an accuracy of about 99%. In [33], the authors utilize DistilBERT
to perform encrypted traffic classification research. They introduce comparative learning
to enhance classification speed without degrading performance. Although our study is
similar to [33], which focuses on STL, our study specifically targets MTL. We apply MTL to
simultaneously learn three tasks on a single model, resulting in superior performance.
In [24,25], both studies utilize MAE for traffic classification research. The authors propose a pre-training model for MAE that introduces a mask patch model, a self-supervised
learning pre-training task, to capture unbiased representations from bursts of varying
lengths and patterns. Experiment results show that the proposed system achieves new high
levels of accuracy of 98%, classification speed, memory efficiency, and robustness across a
wide range of network traffic types.
2.3. Overview of the Multi-Task Learning
The advent of deep learning has led to significant performance improvements in CV
and NLP, as well as network traffic classification. The typical approach is to learn these
tasks in isolation, where a separate neural network is trained for each individual task [15–25].
Nevertheless, deep learning-based methods suffer from a number of limitations in terms
of time and memory. Recently, research has been conducted on MTL techniques, which
have shown promising results in terms of performance, computational, and/or memory
efficiency [41–43]. MTL is the joint handling of multiple tasks through a learned shared
representation. In [41], the author introduces hard parameter sharing and soft parameter
sharing and discusses techniques such as deep relationship networks and fully adaptive
feature sharing. In [42], the authors investigate various aspects of MTL. First, we provide a
definition of MTL, and then we categorize supervised MTL models into five main approaches
and discuss their characteristics The authors note that outlier tasks that are unrelated to other
tasks are known to degrade the performance of all tasks when learning collaboratively, and
they present this as a challenge. In [43], the authors present an overview of architectural
and optimization-based strategies for MTL within the scope of deep neural networks. They
also introduce how to set weights for each task in an MTL. In summary, MTL leverages
useful information from multiple related tasks with the goal of improving the generalization
performance of any task. MTL is efficient in terms of performance, time, and memory as
it can handle multiple tasks using a single model. However, it is important to consider the
correlation between tasks, the structure of the model, and optimization because certain tasks
can degrade the performance of others.
With the rising interest in MTL, there is a gradual increase in research applying MTL
to traffic classification studies [48–50]. In [48], the authors claim to be the first to apply MTL
in network traffic classification research and utilize CNNs to perform malware detection.
In [49], the authors employ three time-series features and utilize CNN for multi-task
classification on QUIC and ISCX 2016 VPN/Non-VPN datasets. However, the detection
performance appears relatively low with an accuracy range of 82–92%. The classification
task is configured slightly differently compared to previous studies. In [50], the authors
perform multi-task classification using transformer and 1D-CNN, achieving an accuracy
of 97–98% on the ISCX 2016 VPN/Non-VPN dataset. Our work is similar to their work.

Appl. Sci. 2024, 14, x FOR PEER REVIEW

Appl. Sci. 2024, 14, 3073

6 of 23

is configured slightly differently compared to previous studies. In [50], the authors perform
6 of 23
multi-task classification using transformer and 1D-CNN, achieving an accuracy of 97–98%
on the ISCX 2016 VPN/Non-VPN dataset. Our work is similar to their work. Their study is
similar to ours, but we demonstrate accuracy exceeding 99% across all three tasks. AddiTheir
study
similarthe
to ours,
but we
accuracy exceeding
all three
tionally,
we is
evaluate
efficiency
of demonstrate
multi-task classification,
an aspect99%
not across
addressed
in
tasks.
Additionally,
we
evaluate
the
efficiency
of
multi-task
classification,
an
aspect
not
their work.
addressed in their work.
3. Proposed Method
3. Proposed Method
3.1. Model
3.1.
Model Architecture
Architecture
The
entire
systemstructure
structureconsists
consistsofofthree
three
sub-systems
(i.e.,
data
preprocessing,
The entire system
sub-systems
(i.e.,
data
preprocessing,
byte
byte
tokenizing,
and
multi-task
classification)
and
is
shown
in
Figure
2.
preprotokenizing, and multi-task classification) and is shown in Figure 2. Data Data
preprocessing
cessing
is the process
of converting
raw traﬃc
data an
intoinput
an input
format
before
applying
is
the process
of converting
raw traffic
data into
format
before
applying
it to
it
to
DistilBERT
model,
resulting
in
byte-separated
data
as
the
output.
Byte
tokenizing
DistilBERT model, resulting in byte-separated data as the output. Byte tokenizing takes
takes
thefrom
data the
from
the previous
module
the input
and performs
tokenization
for each
the
data
previous
module
as theasinput
and performs
tokenization
for each
byte.
byte.
Multi-task
classification
takes
the
tokenized
data
as
the
input,
performs
embedding,
Multi-task classification takes the tokenized data as the input, performs embedding, runs it
runs it through
the DistilBERT
and predicts
label
fortask.
each task.
through
the DistilBERT
model,model,
and predicts
a labelafor
each

Figure 2.
2. Architecture
Figure
Architecture of
of the
the proposed
proposed method.
method.

3.1.1. Data Preprocessing
Preprocessing
(1) Target
Target Dataset: While
available
network
traffic
datasets
While there
therehave
havebeen
beenmany
manypublicly
publicly
available
network
traﬃc
dafor a for
long
time,time,
encrypted
traffic
datasets
are
Thereare
aresevsevtasets
a long
encrypted
traﬃc
datasets
arethe
themost
mostcommon.
common. There
eral encrypted
encrypted traﬃc
traffic datasets
datasetsavailable,
available,but
butwe
weuse
usethe
the ISCX
ISCX 2016
2016 VPN/Non-VPN
VPN/Non-VPN
eral
dataset[40],
[40],which
which
most
popular
in this
research
This dataset
is captured
dataset
is is
thethe
most
popular
in this
research
area.area.
This dataset
is captured
from
from
real
traffic
and
is
a
publicly
available
dataset
in
raw
pcap
format
consisting
real traffic and is a publicly available dataset in raw pcap format consisting of traffic fromof
traffic from
various Since
applications.
Since
it is the
mostused
popular
dataset
used in
several
various
applications.
it is the most
popular
dataset
in several
previous
studies,
studies,
it allows and
for the
comparison
interpretation
experimental
itprevious
allows for
the comparison
interpretation
of and
experimental
resultsoffrom
multiple
results from
multiple
studies.categorized
The datasetinto
is broadly
categorized
into three classes
studies.
The dataset
is broadly
three classes
(i.e., encapsulation,
cat(i.e., encapsulation,
category,
and application),
and studies
separateare
classification
studies are
egory,
and application),
and separate
classification
typically performed
typically
performed
eachinformation
label. Tableabout
1 shows
information
about
classes for
for
each label.
Table 1for
shows
the classes
for each
task.the
Encapsulaeachrefers
task. to
Encapsulation
to theof
presence
or absence
of encryption
on the
target
tion
the presencerefers
or absence
encryption
on the target
traﬃc and
consists
traffic
and
consists
of
two
classes:
VPN
and
Non-VPN.
Category
refers
to
the
nature
of two classes: VPN and Non-VPN. Category refers to the nature of the application
of the
application
and consists
of sixweb
classes,
excluding
web browsing.
and
consists
of six classes,
excluding
browsing.
Application
indicatesApplication
the appliindicates
the
application
used
and
consists
of
sixteen
classes.
cation used and consists of sixteen classes.

Appl. Sci. 2024, 14, 3073

7 of 23

Table 1. Class information for three tasks in ISCX 2016 VPN/Non-VPN dataset.
Task

Classes

Encapsulation (2)

VPN, Non-VPN

Category (6)

Chat, Email, Streaming, File Transfer, P2P, VoIP

Application (16)

Skype, ICQ, Hangout, Facebook, Email, Gmail, FTP, SFTP, SCP, Netflix,
Spotify, Vimeo, YouTube, AIM Chat, VOIPBuster, BitTorrent

(2)

Preprocessing: We perform the following preprocessing. First, we convert the packetlevel pcap file to flow-level. We segment the capture files into bidirectional flows using
the SplitCap tool. Second, we remove irrelevant flows from the converted flow file.
The ISCX 2016 VPN/Non-VPN dataset contains approximately 309 K flows in total.
However, as noted in [51], the dataset contains a lot of irrelevant flows. For example,
it also includes traffic that is not application-specific, such as NBSS, LLMNR, DNS,
etc. and the disrupted three-way handshake flows. Through the preprocessing steps
outlined in [51], a total of 29,195 flows were identified. We performed further analysis
and found that there were specific flows within these flows, characterized by UDP, a
destination IP of 255.255.255.255, and a consistent inclusion of the string “Beacon~” in
the payload. These flows were considered non-essential for the research objectives;
therefore, we removed these unnecessary flows from the converted flow data. After
going through the first and second process, we finally obtained 8763 flows. Third,
we performed zero-padding and flow splicing from the converted data. Considering
the subsequent byte tokenization process, we extract 63 bytes from each of the eight
packets in the flow. In this process, if the number of bytes in a packet is less than 63,
we perform zero-padding. If the packet has more than 63 bytes, we perform splicing.
Based on other research [33,34] and experiments under various configurations, we
chose 63 as the optimal byte value. The 63 bytes are composed of (1) IP, (2) TCP or
UDP, and (3) Payload, depending on the network layer and data. In this case, the
IP has the same number of bytes at 20 bytes, but the lengths of the headers for TCP
and UDP are 20 and 8 bytes, respectively, so the length of the payload that comes
after it will be different. Therefore, the UDP header is extended to 20 bytes by using
zero-padding at the end. We also perform zero-padding for flows that are less than
63 bytes in length for the entire flow, and in the case of UDP, additional padding is
performed for the UDP header. Finally, we remove the Ethernet header and, masking
the IP, port to zero. These are masked as it can cause biased interpolation as it has
strong identifying information. Figure 3 shows the distribution of bidirectional flows
by class for pre-processed data. In Figure 3, we can see that the three tasks suffer from
data imbalance between each class, which we address in Section 3.2.1.

bytes in length for the entire flow, and in the case of UDP, additional padding i
formed for the UDP header. Finally, we remove the Ethernet header and, ma
the IP, port to zero. These are masked as it can cause biased interpolation as
strong identifying information. Figure 3 shows the distribution of bidirectional
8 oftasks
23
by class for pre-processed data. In Figure 3, we can see that the three
suﬀer
data imbalance between each class, which we address in Section 3.2.1.

Appl. Sci. 2024, 14, 3073

Appl. Sci. 2024, 14, x FOR PEER REVIEW

8

(a)

(b)

(c)

Figure 3. Data
of thedata
pre-processed
data
for (a)
theencapsulation
three tasks: (a)task
encapsulation
tas
Figure 3. Data composition
of composition
the pre-processed
for the three
tasks:
(two
classes),
category
task
classes),task
(c) application
task (sixteen classes).
classes), (b) category
task(b)
(six
classes),
(c) (six
application
(sixteen classes).

3.1.2. Byte Tokenizing
3.1.2. Byte Tokenizing

Byte tokenizing
is the
process ofisseparating
preprocessed
data
into bytes and
convertByte
tokenizing
the process
of separating
preprocessed
data
into bytes and
ing the separated
bytes
into
tokens.
There
are
two
parts
to
this
process:
First,
we
split
the First, we
verting the separated bytes into tokens. There are two parts to this process:
preprocessed the
datapreprocessed
into bytes todata
use into
as the
input.
Second,
the
process
of
converting
the
bytes to use as the input. Second, the process of convertin
extracted bytes
of data into
tokens
is performed.
Inperformed.
this process,Initthis
is crucial
to it
determine
extracted
bytes
of data
into tokens is
process,
is crucial to deter
the number ofthe
tokens
to beofused
forto
organizing
theorganizing
data. If thethe
number
tokens
is too
number
tokens
be used for
data. Ifofthe
number
of tokens
high, it may increase
the
data
processing
load,
while
too
few
tokens
can
result
in
the
loss
of
high, it may increase the data processing load, while too few tokens can result in th

of essential information for classification, leading to performance degradation. Add
ally, considering that BERT can handle a maximum of 512 tokens, selecting an approp
number of tokens is essential. After experimenting with various combinations, we
mately chose 63 bytes for the first eight packets, which can accommodate a total o
tokens, including two special tokens [CLS] and [SEP]. We present a performance com

Appl. Sci. 2024, 14, 3073

9 of 23

essential information for classification, leading to performance degradation. Additionally,
considering that BERT can handle a maximum of 512 tokens, selecting an appropriate number of tokens is essential. After experimenting with various combinations, we ultimately
chose 63 bytes for the first eight packets, which can accommodate a total of 506 tokens,
including two special tokens [CLS] and [SEP]. We present a performance comparison based
on input shape in Section 5.3.
3.1.3. Multi-Task Classification
BERT is an NLP model that utilizes a transformer-based architecture and excels
in bidirectionally understanding context within sentences. It encompasses two phases:
pre-training and fine-tuning. In the pre-training stage, BERT undergoes immersion in
extensive amounts of unlabeled data. This process involves two phases: next sentence
prediction (NSP) and masked language modeling (MLM). In the NSP phase, the model
learns to predict whether a sentence follows another sentence in the input text, enhancing
its grasp of discourse-level context. In the MLM phase, certain words in the input sentences
are randomly masked, and model is trained to predict these masked words, fostering a
bidirectional understanding of context at the word level. In the fine-tuning phase, the
pre-trained BERT model is further refined for specific tasks, such as text classification or
question answering, optimizing the process for each task. In network traffic classification
research, a large amount of unlabeled traffic is collected in a pre-training phase to learn the
structure and relationships within the traffic. Each downstream classification task is then
performed in a fine-tuning phase. In [33], pre-training was performed using about 30 GB of
unlabeled traffic data, and five tests were performed with fine-tuning.
Our proposed method does not utilize an additional pre-training model and directly
uses the fine-tuning model of DistilBERT. This is because in the field of network traffic
classification, the pre-training process has several limitations. First, the traffic structure
is very diverse and extensive, but the input dimensions of the BERT model are limited.
Second, the temporal and spatial features in the packet header are ignored, resulting in
performance degradation. These limitations make it difficult for the model to fully learn
the characteristics of different network traffic. Third, the pre-training process is computationally intensive, requiring substantial time, memory overhead, and high-performance
hardware due to the utilization of extensive traffic data. In addition, we perform byte-level
tokenizing as in [51]. As the authors of [51] note, the values derived from the previous
traffic preprocessing and byte tokenizing are represented as integers between 0 and 255,
allowing us to directly fine tune the DistilBERT [36] model, which is explicitly provided as
“distilbert-base-uncased”.
The output layer uses [CLS] as the final sequence representation for downstream
task classification. The [CLS] token output may be converted into a class probability
based on the task. MTL predicts multiple task labels from [CLS] tokens, with approaches
such as hard parameter sharing (tasks share all parameters) and soft parameter sharing
(tasks have their own parameters, sharing some). Hard parameter sharing is efficient with
shared parameters, suitable for related tasks, while soft parameter sharing allows task
specialization for tasks with diverse characteristics.
Therefore, it is important to consider the relevance and nature of the task within the
target dataset and choose the appropriate method. As mentioned before, we target three different tasks in the ISCX 2016 VPN/Non-VPN dataset, and all three tasks are related to each
other as they perform task-specific classification on the same data. Therefore, we utilized
the hard parameter sharing for MTL, and Figure 4 shows the proposed MTL structure.
Figure 4 is organized into shared layers and task specific layers, where the model and
different parameter sets are shared in the shared layer, and the task-specific layers are used
to classify and derive results for each task. The shared layers include the embedding layer
and the transformer encoding layer used by the DistilBERT model.

Appl. Sci. 2024, 14, 3073

specialization for tasks with diverse characteristics.
Therefore, it is important to consider the relevance and nature of the task within the
target dataset and choose the appropriate method. As mentioned before, we target three
diﬀerent tasks in the ISCX 2016 VPN/Non-VPN dataset, and all three tasks are related to
each other as they perform task-specific classification on the same data. Therefore, we
uti10 of
23
lized the hard parameter sharing for MTL, and Figure 4 shows the proposed MTL structure.

Figure 4.
4. Structure
Structure of
of the
the proposed
proposed MTL.
MTL.
Figure

3.2. Weight Adjustment
3.2.1. Class Weight for Imbalanced Data
As shown in Figure 3, the data are heavily imbalanced. Data imbalance stands as
a significant challenge constraining the performance of ML models, particularly when
the samples of the minority class are insufficient [52,53]. To address this issue, common
practices involve the utilization of undersampling and oversampling techniques. However,
these methods come with risks of underfitting and overfitting, respectively, potentially
limiting the generalization ability of the model.
Wkj = 1 −

Ckj
∑ j Ckj

(1)

In recent research, weighted classes have been recognized as one approach to addressing data imbalance [33]. Weighted classes can significantly reduce the bias in the data; thus,
we utilize a method for calculating class weights. Equation (1) indicates the method for
calculating the normalized weights for each class. In Equation (1), Wki is the weight for
each class in task k, Cki is the number of samples for each class label within the k tasks, k
indicates target task, and j indicates class label. These weights are utilized to adjust the
training of the model, taking into consideration the imbalance within each class, thereby
aiding in enhancing the overall model performance.
3.2.2. Task Weight for Loss Calculation
In a typical DL, loss is a metric that represents the difference between the model’s
predictions and the actual target. Minimizing this difference allows the model to learn the
desired outcome more effectively. Loss is often calculated through an objective function
(loss function), most commonly the cross-entropy, mean squared error, etc. In multi-task
classification, the loss is different for each task, so it is necessary to calculate the loss for each
task step by step and combine them effectively to obtain the final loss. Equations (2) and (3)
indicate the method for accumulating losses in multi-task classification. In Equation (2),
y′i is the model’s predicted value, yi is the actual value, and f i is the objective function for
task i. After calculating the loss for each task, they are combined to obtain the final loss.
In Equation (3), Total Loss is the final loss, which is the aggregate of the losses from each
task, N is the number of tasks, and αi is a weight that represents the relative importance of
each task.
Li = Wkj × f i (y′i , yi )
(2)

Appl. Sci. 2024, 14, 3073

11 of 23

N

Total Loss = ∑i=1 αi × Li

(3)

In MTL, performance and learning time can vary due to differences in the difficulty
of each task. Typically, easier tasks converge quickly to achieve high accuracy, while
more difficult tasks face complications in convergence and require more extensive training.
Allocating equal weights to all tasks in MTL may not be appropriate, as it could lead to
higher weights for easier tasks, diminishing the model’s learning capacity for difficult
tasks. Therefore, in MTL, it is essential to consider the difficulty of each task and assign
appropriate weights. Equation (4) illustrates a method for determining the weights for each
task in light of their respective difficulties.
αi =

Ei
N
∑i=1 Ei

(4)

In Equation (4), Ei represents the minimum number of epochs required to converge to
performance β. β is measured by accuracy and can be dynamically adjusted. However,
continuous weight adjustments may decrease the model’s stability and increase the risk of
overfitting to specific tasks. Therefore, we set β to 90% through various experiments. For
example, assuming that there are four tasks and it takes 5 epochs in task #1, 10 epochs in
task #2, 15 epochs in task #3, and 20 epochs in task #4 to achieve 90% accuracy each, the
weights are set to 0.1 (5/50), 0.2 (10/50), 0.3 (15/50), and 0.4 (20/50), respectively.
4. Evaluation, Result and Analysis
4.1. Evaluation Environment Setup
The proposed method was implemented using Python 3.10.9 and PyTorch 2.0.1 with
CUDA 11.8. All experiments were performed on a Linux Ubuntu 20.04.6 LTS server with a
24-core Intel(R) Core(TM) i9-10920X CPU (3.50 GHz) and NVIDIA GeForce RTX 4090 GPU
(24 GB memory). We set the optimal parameters for the model through various experiments.
We set the learning rate to 2 × 10−5 , the batch size to 16, and the dropout ratio to 0.1 and
used AdamW as the optimization tool. Each dataset is divided into the training set and
the testing set according to the ratio of 7:3. We randomly selected 500 samples from each
task (6 categories, 16 applications in total) and entered them into the dataset; however,
if the number of samples for some applications (e.g., Gmail, SFTP within an application
classification) was less than 500, we selected all samples for that application.
4.2. Evaluation Metrics
When evaluating the performance of a model, the evaluation metrics are important.
We utilized four evaluation metrics that have been used in several studies: accuracy, recall,
precision, and F1 score. Equations (5)–(8) show the method for calculating these metrics
Accuracy =

TP + TN
( TP + FN + FP + TN )

(5)

TP
( TP + FN )

(6)

TP
( TP + FP)

(7)

2 × Recall × Precision
( Recall + Precision)

(8)

Recall =

Precision =
F1 Score =

True positive (TP) is when the model correctly classifies something as positive, and
true negative (TN) is when the model correctly classifies something as negative. False
positive (FP) is when the model incorrectly classifies something as positive when it was
negative, and false negative (FN) is when the model incorrectly classifies something as
negative when it was positive.

Appl. Sci. 2024, 14, 3073

12 of 23

As previously mentioned, the ISCX 2016 VPN/Non-VPN data are highly imbalanced
between classes. To account for the potential bias in the results due to the imbalance
between the different categories of data, we used macro average [36]. Macro average
calculates the average value of precision, recall, accuracy, and F1 scores for each category
to provide a more comprehensive and unbiased assessment across all categories.
4.3. Evaluation Result
In this section, we describe our experiments and results to validate the proposed
method. We present the classification performance of our proposed model in Section 4.3.1
and conduct a performance comparison with other models in Section 4.3.2. We validate
the efficiency of our proposed method in Section 4.3.3 and describe several discussions in
Section 5.
4.3.1. Performance of the Proposed Method
To validate our proposed method, we performed experiments on three tasks. In task
#1, classifying the encryption, the highest accuracy, precision, recall, and F1 score were
99.29%, 98.61%, 99.47%, and 99.03%, respectively. In task #2, classifying the category, the
highest accuracy, precision, recall, and F1 score were 97.38%, 97.31%, 95.93%, and 96.61%,
respectively. In task #3, classifying the application, the highest accuracy, precision, recall,
and F1 score were 96.89%, 96.91%, 95.13%, and 96.01%, respectively.
Figure 5 illustrates the confusion matrix detailing accuracy for each task. In subfigures
(a), (b), and (c), the confusion matrix is presented for each task. In Figure 5, while the
majority of classes within each task demonstrate a high accuracy exceeding 95%, AimChat
and ICQChat in Figure 5c exhibit relatively lower accuracy. These applications, designed
for online chatting and offering various services like voice and video calls, share common
traits. However, the similarities between these applications make it difficult to distinguish
traffic patterns accurately, leading to decreased classification accuracy. The intricacies of
these chat applications contribute to the difficulty in achieving higher performance.
Table 2 shows the best class segmentation results for evaluation performance by class
within each task, and 50 epochs in total were performed for the experiment. Task #1
involves classifying two classes (i.e., VPN and Non-VPN), resulting in 98~99% accuracy,
precision, recall, and F1 score. Task #2 involves categorizing traffic into six classes (i.e., Chat,
Email, File Transfer, P2P, Streaming, VoIP). In task #2, the classes Email, P2P, Streaming,
and VoIP are classified with 98~100% accuracy, while File Transfer and Chat are classified
with relatively low accuracy of 95.44% and 94.86%. Task #3 involves categorizing traffic
into sixteen classes (i.e., AimChat, Facebook, Hangout, ICQChat, Skype, Email, Gmail,
FTP, SCP, SFTP, BitTorrent, Netflix, Spotify, Vimeo YouTube, VoIPBuster). In Task #3, most
classes were classified with 96–100% accuracy, with some relatively low accuracy results
for certain classes such as Aim Chat, ICQ Chat, FTP, and SFTP.
Table 2. Performance for three tasks of ISCX 2016 VPN/Non-VPN Classification.
Proposed Method
Task

Class

Accuracy (%)

Precision (%)

Recall (%)

F1-Score (%)

Task #1:
Encapsulation

VPN
Non-VPN

99.45
98.69

98.72
99.72

99.87
97.23

99.29
98.46

Task #2:
Category

Chat
Email
File Transfer
P2P
Streaming
VoIP

94.86
98.21
95.44
100.00
99.41
97.99

97.65
96.90
97.58
100.00
99.71
96.06

94.86
98.21
95.44
100.00
99.41
97.99

96.21
97.55
96.50
100.00
99.56
97.02

Appl. Sci. 2024, 14, 3073

13 of 23

Table 2. Cont.
Proposed Method
Task

Class

Accuracy (%)

Precision (%)

Recall (%)

Appl. Sci. 2024, 14, x FOR PEER REVIEW

Task #3:
Application

AimChat
Facebook
Hangout
ICQChat
Skype
Email
Gmail
FTP
SCP
SFTP
BitTorrent
Netflix
Spotify
Vimeo
YouTube
VoIPBuster

F1-Score (%)
12 of 23

93.75
78.95
93.75
85.71
97.62
98.97
97.62
98.29
98.91
98.19
98.91
98.55
4.3.1. Performance
of the Proposed
72.73
88.89 Method
72.73
80.00
To
validate our proposed99.12
method, we performed
experiments on three 99.36
tasks. In task
99.61
99.61
#1, classifying
the highest accuracy, 97.96
precision, recall, and F1
score were
97.96 the encryption,98.97
98.46
99.29%,
98.61%, 99.47%, and 99.03%,
task #2, classifying the 92.86
category, the
96.30
89.66 respectively. In 96.30
highest
accuracy, precision, recall,
97.38%, 97.31%, 95.93%,89.51
and 96.61%,
87.78
91.30and F1 score were 87.78
respectively.
highest accuracy, precision,
99.76 In task #3, classifying
100.00the application, the
99.76
99.88 recall,
and F192.31
score were 96.89%, 96.91%,
respectively.
100.0095.13%, and 96.01%,
92.31
96.00
Figure
accuracy for each task.
In subfig100.005 illustrates the confusion
100.00 matrix detailing
100.00
100.00
ures (a),
(b), and (c), the confusion
for each task. In Figure98.82
5, while the
97.67
100.00matrix is presented97.68
majority
of classes within each95.16
task demonstrate a high
accuracy exceeding 95%,
AimChat
95.16
95.16
95.16
and ICQChat
designed
99.06 in Figure 5c exhibit
98.13relatively lower accuracy.
99.06 These applications,
98.59
for online
chatting and oﬀering
various services like voice
96.15
96.90
96.15 and video calls, share
96.53common
traits. 94.01
However, the similarities
between these applications
distinguish
96.90
96.15 make it diﬃcult to
92.88
traﬃc patterns accurately, leading to decreased classification accuracy. The intricacies of
these chat applications contribute to the diﬃculty in achieving higher performance.

(a)

(b)

(c)
Figure 5. Confusion matrix for three tasks: (a) encapsulation task (two classes), (b) category task (six
Figure 5. Confusion
matrix for three tasks: (a) encapsulation task (two classes), (b) category task
classes), (c) application task (sixteen classes).
(six classes), (c) application task (sixteen classes).

Appl. Sci. 2024, 14, 3073

14 of 23

Figure 6 shows the learning curve for the three tasks in training and testing. In Figure
6,
14 of 23
the losses represent the total losses for the three tasks, with the learning and testing losses
gradually decreasing.

Appl. Sci. 2024, 14, x FOR PEER REVIEW

Figure
Figure 6.
6. Learning
Learning curve
curve for
for the
the training
training and
and testing.
testing.

4.3.2. Comparison with Other Model
To validate the performance of our proposed method, we compare its performance
with various state-of-the-art methods
methods in network-encrypted
network-encrypted traﬃc
traffic classification.
classification. For
For acaccurate performance
performance validation,
validation, it
it is essential to compare methodologies using the same
dataset with
environment.
However,
direct
with identical
identicalpreprocessing
preprocessingmethods
methodsinina aconsistent
consistent
environment.
However,
dicomparisons
of different
methodologies
are often
impractical
due todue
various
constraints.
rect
comparisons
of diﬀerent
methodologies
are often
impractical
to various
conTherefore,
we took the
performance
presentedpresented
by each methodology
and usedand
them
for
straints. Therefore,
we took
the performance
by each methodology
used
the comparison.
The methods
are categorized
into the following:
(1) statistical
featurethem
for the comparison.
The methods
are categorized
into the following:
(1) statistical
based, (2) ML- (2)
and
DL-based,
and (3) and
pretraining-based,
and a total
17 methodologies
feature-based,
MLand DL-based,
(3) pretraining-based,
and aoftotal
of 17 methodare
compared.
ologies are compared.
(1) Statistical
Statistical feature-based
feature-based methodologies:
methodologies: AppScanner
AppScanner [54],
[54], CUMUL
CUMUL [44],
[44], BIND
BIND [45]
[45]
(2) MLML- and
Deep
Fingerprinting
(DF) (DF)
[46], FS-Net
[15], Graphand DL-based
DL-basedmethodologies:
methodologies:
Deep
Fingerprinting
[46], FS-Net
[15],
DApp [38], TSCRNN
[17], DeepPacket
[10], 1D-CNN
FastTraffic
MATEC [47]
GraphDApp
[38], TSCRNN
[17], DeepPacket
[10],[26],
1D-CNN
[26],[39],
FastTraﬃc
[39],
(3) MATEC
Pretraining-based
methodologies: PERT [21], ET-BERT (flow) [34], ET-BERT (packet) [34],
[47]
XENTC [33], BFCNmethodologies:
[22], Flow-MAEPERT
[25], YaTC
[24]
(3) Pretraining-based
[21], ET-BERT
(flow) [34], ET-BERT (packet)
[34],
[33],
[22],task
Flow-MAE
[25], YaTCon
[24]
MostXENTC
studies do
notBFCN
perform
#1 (Encapsulation)
the ISCX 2016 VPN/Non-VPN

Method
AppScanner [54]
CUMUL [44]
BIND [45]
DF [46]
FS-Net [15]

data;Most
rather,
they perform
tasks #2
(Category)
and #3 (Application)
classify
categories
studies
do not perform
task
#1 (Encapsulation)
on the ISCX to
2016
VPN/Non-VPN
and applications.
Therefore,
we#2
compare
these
methods
and approaches
thatcategories
target taskand
#2
data;
rather, they perform
tasks
(Category)
and
#3 (Application)
to classify
and #3, as these
tasks are
commonly
addressed.
results ofthat
ourtarget
experiments
are
applications.
Therefore,
wemore
compare
these methods
andThe
approaches
task #2 and
shown
in Tables
and
4. As
each method
varies inThe
terms
of metrics,
number of classes,
and
#3,
as these
tasks3are
more
commonly
addressed.
results
of our experiments
are shown
targeted
tasks,
we
only
summarize
the
information
presented
by
each
study.
in Tables 3 and 4. As each method varies in terms of metrics, number of classes, and targeted
tasks, we only summarize the information presented by each study.
TableThe
3. Comparison
forachieves
task #2 inabout
ISCX 2016
VPN/Non-VPN.
proposed results
method
96~98%
accuracy on tasks #2 and #3, outperforming most of the existing research methods. Although several methodologies exhibit
Comparison Results for Task #2: Category
slightly better performance (i.e., accuracy 0.69–1.67% in task #2 and accuracy 1.31–2.98%
Accuracy
(%)
Precision
(%)existing approaches
Recall (%)
Score (%) single
in task #3),
it is noteworthy
that the
are designed forF1
STL-based
task71.82
classification, while the73.39
proposed method is capable
tasks simul72.25 of classifying three
71.97
56.10
56.76 simultaneously is56.68
taneously.
This capability 58.83
to address multiple tasks
remarkable.
75.34 this multi-task classification,
75.83
74.20 high perThrough
the proposed74.88
method not only maintains
71.54
71.02
formance
but also proves to71.92
be more eﬃcient than 71.04
conventional approaches
in handling
72.05
75.02
72.38
71.31
the classification of multiple tasks concurrently.
Table 3. Comparison results for task #2 in ISCX 2016 VPN/Non-VPN.

Comparison Results for Task #2: Category

Appl. Sci. 2024, 14, 3073

15 of 23

Table 3. Cont.
Comparison Results for Task #2: Category
Method

Accuracy (%)

Precision (%)

Recall (%)

F1 Score (%)

GraphDApp [38]
TSCRNN [17]
Deep Packet [10]
1D-CNN [26]
FastTraffic [39]
MATEC [47]
PERT [21]
ET-BERT (flow) [34]
ET-BERT (packet) [34]
XENTC [33]
BFCN [22]
YaTC [24]
Flow-MAE [25]

59.77
93.29
98.30
94.50
73.20
93.52
97.29
98.90
97.03
99.12
98.07
99.15

60.45
92.70
93.77
94.77
84.43
94.00
97.56
98.91
99.13
99.24

62.20
92.60
93.06
94.26
82.40
93.49
97.31
98.90
99.11
99.15

60.36
92.60
93.21
98.60
94.40
82.87
93.68
97.33
98.90
97.06
99.11
98.04
99.17

Proposed

97.38

97.31

95.93

96.61

Table 4. Comparison results for task #3 in ISCX 2016 VPN/Non-VPN.
Comparison Results for Task #3: Application
Method

Accuracy (%)

Precision (%)

Recall (%)

F1 Score (%)

AppScanner [54]
CUMUL [44]
BIND [45]
DF [46]
FS-Net [15]
GraphDApp [38]
TSCRNN [17]
Deep Packet [10]
1D-CNN [26]
FastTraffic [39]
MATEC [47]
PERT [21]
ET-BERT (flow) [34]
ET-BERT (packet) [34]
XENTC [33]
BFCN [22]
YaTC [24]
Flow-MAE [25]

62.66
53.65
67.67
61.16
66.47
62.28
97.58
86.60
92.24
69.21
82.29
85.19
99.62
96.37
99.65
99.87

48.64
41.29
51.52
66.97
48.19
59.00
97.85
93.58
73.32
70.92
75.08
99.36
99.36
99.91

51.98
45.35
51.53
66.51
48.48
54.72
97.45
92.84
65.40
71.73
72.94
99.38
99.47
99.89

49.35
42.36
49.65
65.31
47.37
55.58
97.65
86.50
93.12
68.24
69.92
73.06
99.37
94.63
99.41
99.90

Proposed

96.89

96.91

95.13

96.01

The proposed method achieves about 96~98% accuracy on tasks #2 and #3, outperforming most of the existing research methods. Although several methodologies exhibit slightly
better performance (i.e., accuracy 0.69–1.67% in task #2 and accuracy 1.31–2.98% in task
#3), it is noteworthy that the existing approaches are designed for STL-based single task
classification, while the proposed method is capable of classifying three tasks simultaneously. This capability to address multiple tasks simultaneously is remarkable. Through this
multi-task classification, the proposed method not only maintains high performance but
also proves to be more efficient than conventional approaches in handling the classification
of multiple tasks concurrently.
4.3.3. Performance of the Efficiency
The proposed method utilizes MTL to perform multi-task classification on the ISCX
VPN/Non-VPN 2016 dataset. The goal is to achieve high performance by simultaneously

Appl. Sci. 2024, 14, 3073

16 of 23

handling various classification tasks. The efficiency of the model refers to its ability to
quickly adapt to downstream tasks. To evaluate this efficiency, we compared the proposed
method with other approaches and measured the processing speed. However, the interpretation of the model’s efficiency may vary depending on hardware performance and
data. Therefore, maintaining the same experimental environment and dataset is crucial for
a fair comparison. Since it is difficult to reproduce these conditions exactly, we compare
our results to those presented in other studies [8,33,34,39]. Table 5 shows the results on
fine-tune efficiency evaluation.
Table 5. Results on efficiency evaluation.
Method

Task

ST (ms)

PT (ms)

ET-BERT (Fine-Tune) [34]
XENTC [33]

STL (1 task)
STL (1 task)

8.30~9.61
-

155.7
15.1

MATEC [39]
FastTraffic [8]

STL (1 task)
STL (1 task)

2.10
0.25

1.3
0.59

Proposed

MTL (3 tasks)

1.27

30.7

In Table 5, ST represents the processing time for one sample and PT represents the
processing time for one packet. Among the four models, ET-BERT and XENTC are general
classification models, while MATEC and FastTraffic are models designed for lightweight
purposes. All of them perform single-task classification.
From an ST perspective, ET-BERT yields a range of 8.30~9.61 ms. The lightweight models,
MATEC and FastTraffic, yield 2.10 and 0.25 ms, respectively. The proposed method achieves
higher efficiency than ET-BERT with an execution time of 1.27 ms, but it is less efficient than
MATEC and FastTraffic. Nevertheless, considering the results in Tables 3 and 4, the proposed
method demonstrates 4.65~27.68% higher accuracy compared to MATEC and FastTraffic.
Furthermore, the proposed method is more efficient than MATEC as it can learn the three
tasks simultaneously.
From a PT perspective, ET-BERT yields 155.7 ms, XENTC produces 15.1 ms, MATEC
results in 1.3 ms, and FastTraffic yields 0.59 ms. The proposed method achieves an efficiency
of 30.7, which is higher than ET-BERT but lower than XENTC and FastTraffic. The proposed
method seems to exhibit relatively high PT since it processes eight packets within the flow.
However, similar to the ST perspective, the proposed method demonstrates high efficiency
considering both accuracy and multi-task classification.
The efficiency of a model is highly influenced by hardware performance and data
structure, and there is typically a trade-off between model performance and efficiency. Considering this trade-off, evaluating the balance between model performance and efficiency
becomes crucial. Further discussion is needed based on additional experimental results to
better understand this trade-off and assess the overall performance and efficiency of the
model. Therefore, in the future, we plan to enhance the model to achieve higher efficiency
while maintaining its classification performance.
5. Discussions
In this paper, we demonstrate high performance and efficiency by performing multitask classification on encrypted traffic. In this section, we provide some detailed discussion
of the proposed method.
5.1. Effect of Class Wight in Data Imbalance
We applied class weights to address the class imbalance in ISCX 2016 VPN/Non-VPN
data in Section 3.2.1. Class weight represents a weight that reflects the proportion of classes
in the data and can reduce the imbalance between classes. Figure 7 shows the distribution
of data for each class before and after applying class weight.

5.1. Eﬀect of Class Wight in Data Imbalance

Appl. Sci. 2024, 14, 3073

We applied class weights to address the class imbalance in ISCX 2016 VPN/Non-VPN
data in Section 3.2.1. Class weight represents a weight that reflects the proportion of clas17 of 23
ses in the data and can reduce the imbalance between classes. Figure 7 shows the distribution of data for each class before and after applying class weight.

(a)

(b)

(c)
Figure
ofof
data
before
andand
after
applying
classclass
weights.
(a) Encapsulation
task (two
Figure 7.7.Distribution
Distribution
data
before
after
applying
weights.
(a) Encapsulation
task
classes),
(b)
category
task
(six
classes),
(c)
application
task
(sixteen
classes).
(two classes), (b) category task (six classes), (c) application task (sixteen classes).

In
In Figure
Figure 7,
7, the
the x-axis
x-axis represents
represents the
the classes
classes per
per task
task and
and is
is organized
organized the
the same
same as
as in
in
Figure
3.
For
example,
in
Figure
7a,
“1”
and
“2”
represent
{VPN,
NonVPN},
respectively,
Figure 3. For example, in Figure 7a, “1” and “2” represent {VPN, NonVPN}, respectively,
and
and in
inFigure
Figure7b,
7b,“1~6”
“1~6”represent
represent{Chat,
{Chat,Email,
Email,File
FileTransfer,
Transfer,P2P,
P2P,Streaming,
Streaming,VoIP}.
VoIP}.ComComparing
paring the
the ‘Before’
‘Before’ and
and ‘After’
‘After’in
in Figure
Figure 7,
7, we
we can
can see
see that
that the
the imbalance
imbalance between
between each
each
class
class is
is significantly
significantly reduced.
reduced. However,
However,in
inFigure
Figure7c,
7c, we
we can
can see
see that
that there
there is
is still
still some
some
imbalance
imbalance as
as there
there are
are too
too few minority
minority classes.
classes. These
These limitations
limitations will
will be
be tackled
tackled in
in the
the
future
future with
with additional
additional weighting
weighting and
and sampling techniques.
5.2. Performance
PerformanceBased
Based on
on Weight
WeightAdjustment
Adjustment
5.2.
In order
order to
to address
address both
both data
data imbalance
imbalance issues
issues and
and variations
variations in
in diﬃculty
difficulty across
across
In
tasks, we
we applied
applied weight
weight adjustments
adjustments during
during the
the experiments.
experiments. The
The weight
weight adjustment
adjustment is
is
tasks,
implemented
in
two
aspects:
class
weights
and
task
weights.
Class
weights
were
introduced
implemented in two aspects: class weights and task weights. Class weights were
to mitigate data imbalance problems, while task weights were designed to prevent biased
learning, particularly when there were significant differences in difficulty among tasks.
The proper utilization of these two weights is crucial, especially in scenarios where specific
tasks converge rapidly; failure to handle this appropriately may lead to biased learning.
Figure 8 shows the test accuracy curve for the weight adjustment.

Appl. Sci. 2024, 14, 3073

gence speeds across each task, later showing higher performance in task #2 and #3 compared to task #1. Figure 8d shows the results with weight adjustments, applying class and
task weights, also yielding an accuracy of 98~99% across task #1 and 96–97% across tasks
#2 and #3. Through the above experiments, it is evident that adjusting weights for both
18 of 23
categories leads to higher performance. Therefore, it can be concluded that weight adjustment plays a crucial role in enhancing performance.

(a)

(b)

(c)

(d)

Figure 8.
8. Test
Figure
Test accuracy
accuracy curve
curve for
for weight
weight adjustment.
adjustment. (a)
(a) No
No weight,
weight, (b)
(b) class
class weight,
weight, (c)
(c) task
task weight,
weight,
and (d) class and task weights applied.
and (d) class and task weights applied.

5.3. Performance
Based on
Shape
Figure 8a shows
theInput
results
with weight adjustments, applying only class weight,
yielding
an accuracy
across task
across
task #2,
and 89~90%
across
the
In Section
3.1.1, of
we99%
described
that #1,
we90~91%
conducted
several
experiments
with
various
task
Figure
8b shows
resultsofwith
weight
only class
input#3.
shapes
based
on thethe
number
packets
andadjustments,
bytes in the applying
flow. Through
theseweight,
experyielding
an set
accuracy
of 98%shape
acrossastask
#1 andand
93–94%
across
#2 and #3.
8c
iments, we
the optimal
8 packets
63 bytes.
Intasks
this section,
weFigure
compare
shows the results with weight adjustments, applying only task weight, yielding an accuracy
of 93% across task #1 and 94~95% across tasks #2 and #3. In Figure 8a,b, rapid convergence
is observed in task #1, while Figure 8c tends to exhibit initially similar convergence speeds
across each task, later showing higher performance in task #2 and #3 compared to task #1.
Figure 8d shows the results with weight adjustments, applying class and task weights, also
yielding an accuracy of 98~99% across task #1 and 96–97% across tasks #2 and #3. Through
the above experiments, it is evident that adjusting weights for both categories leads to
higher performance. Therefore, it can be concluded that weight adjustment plays a crucial
role in enhancing performance.
5.3. Performance Based on Input Shape
In Section 3.1.1, we described that we conducted several experiments with various
input shapes based on the number of packets and bytes in the flow. Through these experiments, we set the optimal shape as 8 packets and 63 bytes. In this section, we compare the
performance based on different input shapes. The input shape can be variably defined, and
we set the range of packet counts to 4~8 and byte counts to 60~70, taking into account the
handshake process and header (IP, TCP/UDP) byte sizes within encrypted communication.

Appl. Sci. 2024, 14, 3073

19 of 23

As mentioned earlier, considering BERT’s maximum input token limit of 512, we excluded
cases where the total token count (packet count × byte count) exceeds 512.
Table A1 in Appendix A indicates the performance of the proposed method based on
input shapes. The experiments were conducted for 20 epochs with the same experimental
setup, as multiple experiments were required depending on the input shape. We selected
the target task as the most challenging task #3 among the three tasks. In Table A1, the
highest performance is observed with (8, 63). Therefore, we selected the optimal input
shape as 8 packets and 63 bytes.
6. Conclusions
Network traffic classification has been studied for a long time, and recently, a lot
of research has been conducted on encrypted traffic. Most studies perform single-task
classification, with DL- and transformer-based methods performing well. However, there
are limitations in their efficiency and effectiveness given the increasingly diverse and
complicated nature of traffic.
In this paper, we proposed multitask classification by using DistilBERT. The proposed
method can learn multiple tasks in one model with one training. We applied a weight
adjustment to improve the performance of our proposed method. The weight adjustment
consists of class weights and task weights. Class weights mitigate the problem of data
imbalance, and task weights prevent biased learning due to the difference in difficulty
between tasks in multi-task classification.
To evaluate the proposed method, we conducted experiments in terms of accuracy and
efficiency. Measured in terms of accuracy, the proposed approach achieves 96.89–99.29%
accuracy on three tasks, showing higher performance compared to most existing methods.
Furthermore, in terms of efficiency, it outperforms ET-BERT. While the proposed method
exhibits lower efficiency compared to FastTraffic and MATEC, which focus on lightweight
design, it achieves a significantly higher accuracy, ranging from 4.65 to 27.68% higher than
the two mentioned methods. We discussed the performance impact of class weight and
weight adjustment in Section 5. In addition, we validated the decision to select 8 packets
and 63 bytes based on performance experiments with input data shapes (in Appendix A,
Table A1). This input shape consists of packets generated during the handshake process
within TLS, which is the most widely utilized today and typically remains unencrypted.
Therefore, we believe it performs well despite being encrypted traffic.
However, the proposed method has some limitations. First, although the proposed
method demonstrated high performance on the ISCX 2016 VPN/Non-VPN dataset, validation was only conducted on specific datasets. As the ISCX 2016 VPN/Non-VPN dataset
comprises a small amount of data, leveraging AI models may yield high performance.
Therefore, additional validation experiments on other datasets such as ISCX Tor are necessary to verify the performance of the proposed method. Second, as mentioned earlier,
efficiency can vary depending on hardware performance and the dataset. In this paper,
we evaluated the method using results presented in other studies; however, for a precise
assessment, consistent experimental conditions and preprocessed datasets are necessary.
Third, as previously mentioned, the proposed method utilizes eight packets in the flow,
which results in a relatively high time to process a single packet. Fourth, the proposed
method applies class weights to address the problem of imbalanced data. Although the
class weights alleviate the problem of imbalanced data to some extent, they are still unevenly distributed. Nevertheless, the proposed method can perform three tests with one
training and shows high performance and efficiency.
In future research, we plan to perform multi-task classification using diverse datasets.
We will assess the effectiveness of our proposed method using identical experimental
setups and preprocessed datasets for evaluation. Additionally, we plan to improve the
model architecture and preprocessing methods to further enhance the performance and
efficiency of the proposed method, including PT.

Appl. Sci. 2024, 14, 3073

20 of 23

Author Contributions: Conceptualization, M.-S.K.; methodology, J.-T.P.; software, J.-T.P. and C.Y.S.; resources, J.-T.P., C.-Y.S. and U.-J.B.; data processing, U.-J.B. and J.-T.P. writing—original draft
preparation, J.-T.P.; writing—review and editing, J.-T.P.; visualization, J.-T.P.; supervision, M.-S.K.;
project administration, M.-S.K.; funding acquisition, M.-S.K. All authors have read and agreed to the
published version of the manuscript.
Funding: This work was supported by Institute of Information & communications Technology
Planning & Evaluation (IITP) funded by the Korea government (00235509, Development of security
monitoring technology based network behavior against encrypted cyber threats in ICT convergence environment).
Institutional Review Board Statement: Not applicable.
Informed Consent Statement: Not applicable.
Data Availability Statement: Data are contained within the article.
Conflicts of Interest: The authors declare no conflicts of interest.

Appendix A
Table A1. Performance based on different input shapes.
Performance Based on Input Shape (for Task #3: Application Classification)
Input Shape
(Packet, Byte)

Accuracy (%)

Precision (%)

Recall (%)

F1-Score (%)

(4, 60)
(4, 61)
(4, 62)
(4, 63)
(4, 64)
(4, 65)
(4, 66)
(4, 67)
(4, 68)
(4, 69)
(4, 70)

78.13
85.36
84.78
85.10
84.97
85.62
83.89
85.32
86.46
86.27
86.40

90.58
97.14
94.19
91.14
97.54
96.52
97.58
93.80
97.41
95.07
96.52

74.64
83.59
82.51
78.57
80.63
81.99
79.65
80.48
80.93
81.21
81.99

81.84
89.85
87.96
84.39
88.28
88.66
87.71
86.63
86.41
87.60
88.66

(5, 60)
(5, 61)
(5, 62)
(5, 63)
(5, 64)
(5, 65)
(5, 66)
(5, 67)
(5, 68)
(5, 69)
(5, 70)

84.24
85.23
83.46
86.46
84.93
84.63
84.27
82.81
82.24
83.35
84.51

96.10
97.58
97.57
96.77
97.49
92.94
97.50
88.00
90.15
91.15
96.37

80.34
80.13
80.61
82.63
81.82
79.14
79.32
74.26
74.78
76.79
81.98

87.51
87.99
88.28
89.14
88.97
85.49
87.48
83.55
81.75
83.36
88.59

(6, 60)
(6, 61)
(6, 62)
(6, 63)
(6, 64)
(6, 65)
(6, 66)
(6, 67)
(6, 68)
(6, 69)
(6, 70)

81.86
85.89
84.49
88.07
85.90
85.78
86.46
86.08
86.42
85.93
86.46

93.14
94.59
97.44
97.76
97.51
97.55
97.62
97.51
97.59
97.59
96.44

78.51
82.44
80.13
83.22
81.77
81.52
82.37
83.16
81.37
81.50
83.25

85.20
88.10
87.94
89.91
88.95
88.82
89.59
89.77
88.74
86.58
89.36

(7, 60)
(7, 61)
(7, 62)
(7, 63)
(7, 64)
(7, 65)
(7, 66)
(7, 67)
(7, 68)
(7, 69)
(7, 70)

81.45
84.18
87.74
87.42
82.62
86.43
86.73
86.35
84.37
85.46
84.79

90.61
92.27
97.43
97.60
89.23
96.59
97.49
97.34
91.88
96.86
94.01

80.11
81.77
83.99
82.26
78.18
82.87
82.60
82.87
78.47
84.35
79.11

85.03
86.70
90.21
89.27
83.34
89.20
89.43
89.52
84.65
90.17
85.92

(8, 60)
(8, 61)
(8, 62)
(8, 63)

86.86
86.58
88.16
90.28

96.56
97.59
95.39
98.17

79.62
81.14
82.19
86.28

87.28
88.61
88.30
91.84

Appl. Sci. 2024, 14, 3073

21 of 23

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
18.
19.

20.
21.

22.
23.

24.
25.

Callado, A.; Kamienski, C.; Szabó, G.; Gero, B.P.; Kelner, J.; Fernandes, S.; Sadok, D. A Survey on Internet Traffic Identification.
IEEE Commun. Surv. Tutor. 2009, 11, 37–52. [CrossRef]
Dainotti, A.; Pescape, A.; Claffy, K. Issues and Future Directions in Traffic Classification. IEEE Netw. 2012, 26, 35–40. [CrossRef]
Madhukar, A.; Williamson, C. A Longitudinal Study of P2P Traffic Classification. In Proceedings of the 14th IEEE International
Symposium on Modeling, Analysis, and Simulation, Monterey, CA, USA, 11–14 September 2006; pp. 179–188.
Nguyen, T.T.T.; Armitage, G. A Survey of Techniques for Internet Traffic Classification using Machine Learning. IEEE Commun.
Surv. Tut. 2008, 10, 56–76. [CrossRef]
Pacheco, F.; Exposito, E.; Gineste, M.; Baudoin, C.; Aguilar, J. Towards the Deployment of Machine Learning Solutions in Network
Traffic Classification: A Systematic Survey. IEEE Commun. Surv. Tutor. 2018, 21, 1988–2014. [CrossRef]
Al Khater, N.; Overill, R.E. Network Traffic Classification Techniques and Challenges. In Proceedings of the 2015 Tenth
International Conference on Digital Information Management (ICDIM), Jeju, Republic of Korea, 21–23 October 2015; pp. 43–48.
Feng, X.; Huang, X.; Tian, X.; Ma, Y. Automatic Traffic Signature Extraction based on Smith-Waterman Algorithm for Traffic
Classification. In Proceedings of the 2010 3rd IEEE International Conference on Broadband Network and Multimedia Technology
(IC-BNMT), Beijing, China, 26–28 October 2010; pp. 154–158.
Lim, H.-K.; Kim, J.-B.; Heo, J.-S.; Kim, K.; Hong, Y.-G.; Han, Y.-H. Packet-based Network Traffic Classification Using Deep
Learning. In Proceedings of the 2019 International Conference on Artificial Intelligence in Information and Communication
(ICAIIC), Okinawa, Japan, 11–13 February 2019; pp. 46–51.
Finsterbusch, M.; Richter, C.; Rocha, E.; Muller, J.A.; Hanssgen, K. A Survey of Payload-Based Traffic Classification Approaches.
IEEE Commun. Surv. Tutor. 2014, 16, 1135–1156. [CrossRef]
Lotfollahi, M.; Zade, R.S.H.; Siavoshani, M.J.; Saberian, M. Deep Packet: A Novel Approach for Encrypted Traffic Classification
using Deep Learning. Soft Comput. 2020, 24, 1999–2012. [CrossRef]
Wang, P.; Ye, F.; Chen, X.; Qian, Y. Datanet: Deep Learning Based Encrypted Network Traffic Classification in SDN Home Gateway.
IEEE Access 2018, 6, 55380–55391. [CrossRef]
Zou, Z.; Ge, J.; Zheng, H.; Wu, Y.; Han, C.; Yao, Z. Encrypted Traffic Classification with a Convolutional Long Short-Term
Memory Neural Network. In Proceedings of the 2018 IEEE 20th International Conference on High-Performance Computing and
Communications; IEEE 16th International Conference on Smart City; IEEE 4th International Conference on Data Science and
Systems (HPCC/SmartCity/DSS), Exeter, UK, 28–30 June 2018; pp. 329–334.
Lopez-Martin, M.; Carro, B.; Sanchez-Esguevillas, A.; Lloret, J. Network Traffic Classifier with Convolutional and Recurrent
Neural Networks for Internet of Things. IEEE Access 2017, 5, 18042–18050. [CrossRef]
Williams, N.; Zander, S.; Armitage, G. A Preliminary Performance Comparison of Five Machine Learning Algorithms for Practical
IP Traffic Flow Classification. ACM SIGCOMM Comput. Commun. Rev. 2006, 36, 5–16. [CrossRef]
Liu, C.; He, L.; Xiong, G.; Cao, Z.; Li, Z. FS-Net: A Flow Sequence Network for Encrypted Traffic Classification. In Proceedings of
the IEEE INFOCOM 2019—IEEE Conference on Computer Communications, Paris, France, 29 April–2 May 2019; pp. 1171–1179.
Shapira, T.; Shavitt, Y. FlowPic: Encrypted Internet Traffic Classification is as Easy as Image Recognition. In Proceedings of
the IEEE INFOCOM 2019—IEEE Conference on Computer Communications Workshops (INFOCOM WKSHPS), Paris, France,
29 April–2 May 2019; pp. 680–687.
Lin, K.; Xu, X.; Gao, H. TSCRNN: A Novel Classification Scheme of Encrypted Traffic based on Flow Spatiotemporal Features for
Efficient Management of IIoT. Comput. Netw. 2021, 190, 107974. [CrossRef]
Aceto, G.; Ciuonzo, D.; Montieri, A.; Pescapè, A. MIMETIC: Mobile Encrypted Traffic Classification using Multimodal Deep
Learning. Comput. Netw. 2019, 165, 106944. [CrossRef]
Hao, S.; Hu, J.; Liu, S.; Song, T.; Guo, J.; Liu, S. Network Traffic Classification based on Improved DAG-SVM. In Proceedings of
the 2015 International Conference on Communications, Management and Telecommunications (ComManTel), DaNang, Vietnam,
28–30 December 2015; pp. 256–261.
Yao, H.; Liu, C.; Zhang, P.; Wu, S.; Jiang, C.; Yu, S. Identification of Encrypted Traffic Through Attention Mechanism Based Long
Short-Term Memory. IEEE Trans. Big Data 2019, 8, 241–252. [CrossRef]
He, H.Y.; Yang, Z.G.; Chen, X.N. PERT: Payload Encoding Representation from Transformer for Encrypted Traffic Classification.
In Proceedings of the 2020 ITU Kaleidoscope: Industry-Driven Digital Transformation (ITU K), Ha Noi, Vietnam, 7–11 December
2020; pp. 1–8.
Shi, Z.; Luktarhan, N.; Song, Y.; Tian, G. BFCN: A Novel Classification Method of Encrypted Traffic Based on BERT and CNN.
Electronics 2023, 12, 516. [CrossRef]
Ma, X.; Liu, T.; Hu, N.; Liu, X. Bi-ETC: A Bidirectional Encrypted Traffic Classification Model Based on BERT and BiLSTM. In
Proceedings of the 2023 8th International Conference on Data Science in Cyberspace (DSC), Hefei, China, 18–20 August 2023; pp.
197–204.
Zhao, R.; Zhan, M.; Deng, X.; Wang, Y.; Wang, Y.; Gui, G.; Xue, Z. Yet Another Traffic Classifier: A Masked Autoencoder Based
Traffic Transformer with Multi-Level Flow Representation. Proc. AAAI Conf. Artif. Intell. 2023, 37, 5420–5427. [CrossRef]
Zijun, H.; Yuliang, L.; Yongjie, W.; Yi, X. Flow-MAE: Leveraging Masked AutoEncoder for Accurate, Efficient and Robust
Malicious Traffic Classification. In Proceedings of the RAID 2023: The 26th International Symposium on Research in Attacks,
Intrusions and Defenses, Hong Kong, China, 16–18 October 2023; pp. 297–314.

Appl. Sci. 2024, 14, 3073

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

41.
42.
43.
44.

45.

46.

47.
48.
49.
50.
51.

22 of 23

Wang, W.; Zhu, M.; Wang, J.; Zeng, X.; Yang, Z. End-to-End Encrypted Traffic Classification with One-Dimensional Convolution
Neural Networks. In Proceedings of the 2017 IEEE International Conference on Intelligence and Security Informatics IEEE,
Beijing, China, 22–24 July 2017; pp. 43–48.
Shahraki, A.; Abbasi, M.; Taherkordi, A.; Jurcut, A.D. Active Learning for Network Traffic Classification: A Technical Study. IEEE
Trans. Cogn. Commun. Netw. 2022, 8, 422–439. [CrossRef]
Park, K.; Kim, H. Encryption Is Not Enough: Inferring User Activities on Kakaotalk with Traffic Analysis. In International Workshop
on Information Security Applications (WISA); Springer: Cham, Switzerland, 2015; pp. 254–265.
Saltaformaggio, B.; Choi, H.; Johnson, K.; Kwon, Y.; Zhang, Q.; Zhang, X.; Xu, D.; Qian, J. Eavesdropping on Fine-Grained User
Activities Within Smartphone Apps Over Encrypted Network Traffic. In Proceedings of the 10th USENIX workshop on offensive
technologies (WOOT 16), Austin, TX, USA, 8–9 August 2016; pp. 69–78.
Fu, Y.; Xiong, H.; Lu, X.; Yang, J.; Chen, C. Service Usage Classification with Encrypted Internet Traffic in Mobile Messaging Apps.
IEEE Trans. Mob. Comput. 2016, 15, 2851–2864. [CrossRef]
Celdrán, A.H.; von der Assen, J.; Moser, K.; Sánchez PM, S.; Bovet, G.; Pérez, G.M.; Stiller, B. Early Detection of Cryptojacker
Malicious Behaviors on IoT Crowdsensing Devices. In Proceedings of the NOMS 2023-2023 IEEE/IFIP Network Operations and
Management Symposium, Miami, FL, USA, 8–12 May 2023; pp. 1–8.
Pathmaperuma, M.H.; Rahulamathavan, Y.; Dogan, S.; Kondoz, A.M. Deep Learning for Encrypted Traffic Classification and
Unknown Data Detection. Sensors 2022, 22, 7643. [CrossRef] [PubMed]
Shin, C.-Y.; Park, J.-T.; Baek, U.-J.; Kim, M.-S. A Feasible and Explainable Network Traffic Classifier Utilizing DistilBERT. IEEE
Access 2023, 11, 70216–70237. [CrossRef]
Lin, X.; Xiong, G.; Gou, G.; Li, Z.; Shi, J.; Yu, J. ET-BERT: A contextualized datagram representation with pre-training transformers
for encrypted traffic classification. arXiv 2022, arXiv:2202.06335.
Devlin, J.; Chang, M.-W.; Lee, K.; Toutanova, K. BERT: Pre-training of deep bidirectional transformers for language understanding.
arXiv 2018, arXiv:1810.04805.
Sanh, V.; Debut, L.; Chaumond, J.; Wolf, T. DistilBERT, a distilled version of BERT: Smaller, faster, cheaper and lighter. arXiv 2019,
arXiv:1910.01108.
Van Ede, T.; Bortolameotti, R.; Continella, A.; Ren, J.; Dubois, D.J.; Lindorfer, M.; Choffnes, D.; Van Steen, M.; Peter, A. FlowPrint:
Semi-Supervised Mobile-App Fingerprinting on Encrypted Network Traffic. In Proceedings of the 27th Annual Network and
Distributed System Security Symposium, NDSS 2020, San Diego, CA, USA, 23–26 February 2020.
Shen, M.; Zhang, J.; Zhu, L.; Xu, K.; Du, X. Accurate Decentralized Application Identification via Encrypted Traffic Analysis
Using Graph Neural Networks. IEEE Trans. Inf. Forensics Secur. 2021, 16, 2367–2380. [CrossRef]
Xu, Y.; Cao, J.; Song, K.; Xiang, Q.; Cheng, G. FastTraffic: A Lightweight Method for Encrypted Traffic Fast Classification. Comput.
Netw. 2023, 235, 109965. [CrossRef]
Draper-Gil, G.; Lashkari, A.H.; Mamun, M.S.I.; Ghorbani, A.A. Characterization of encrypted and vpn traffic using timerelated. In Proceedings of the 2nd International Conference on Information Systems Security and Privacy (ICISSP), Rome, Italy,
19–21 February 2016; pp. 407–414.
Ruder, S. An Overview of Multi-Task Learning in Deep Neural Networks. arXiv 2017, arXiv:1706.05098.
Zhang, Y.; Yang, Q. A Survey on Multi-Task Learning. IEEE Trans. Knowl. Data Eng. 2022, 34, 5586–5609. [CrossRef]
Vandenhende, S.; Georgoulis, S.; Van Gansbeke, W.; Proesmans, M.; Dai, D.; Van Gool, L. Multi-Task Learning for Dense Prediction
Tasks: A Survey. IEEE Trans. Pattern Anal. Mach. Intell. 2022, 44, 3614–3633. [CrossRef] [PubMed]
Panchenko, A.; Lanze, F.; Pennekamp, J.; Engel, T.; Zinnen, A.; Henze, M.; Wehrle, K. Website Fingerprinting at Internet Scale.
In Proceedings of the 23rd Annual Network and Distributed System Security Symposium, NDSS 2016, San Diego, CA, USA,
21–24 February 2016.
Al-Naami, K.; Chandra, S.; Mustafa, A.; Khan, L.; Lin, Z.; Hamlen, K.; Thuraisingham, B. Adaptive Encrypted Traffic Fingerprinting with Bi-Directional Dependence. In Proceedings of the ACSAC’16: 2016 Annual Computer Security Applications Conference,
Los Angeles, CA, USA, 5–8 December 2016; pp. 177–188.
Sirinam, P.; Imani, M.; Juarez, M.; Wright, M. Deep Fingerprinting: Undermining Website Fingerprinting Defenses with Deep
Learning. In Proceedings of the 2018 ACM SIGSAC Conference on Computer and Communications Security, CCS 2018, Toronto,
ON, Canada, 15–19 October 2018; pp. 1928–1943.
Cheng, J.; Wu, Y.; Yuepeng, E.; You, J.; Li, T.; Li, H.; Ge, J. MATEC: A Lightweight Neural Network for Online Encrypted Traffic
Classification. Comput. Netw. 2021, 199, 108472. [CrossRef]
Huang, H.; Deng, H.; Chen, J.; Han, L.; Wang, W. Automatic Multi-Task Learning System for Abnormal Network Traffic Detection.
Int. J. Emerg. Technol. Learn. 2018, 13, 4–20. [CrossRef]
Rezaei, S.; Liu, X. Multitask Learning for Network Traffic Classification. In Proceedings of the 2020 29th International Conference
on Computer Communications and Networks (ICCCN), Honolulu, HI, USA, 3–6 August 2020; pp. 1–9.
Wang, K.; Gao, J.; Lei, X. MTC: A Multi-Task Model for Encrypted Network Traffic Classification Based on Transformer and
1D-CNN. Intell. Autom. Soft Comput. 2023, 37, 619–638. [CrossRef]
Baek, U.-J.; Lee, M.-S.; Park, J.-T.; Choi, J.-W.; Shin, C.-Y.; Kim, M.-S. Preprocessing and Analysis of an Open Dataset in Application
Traffic Classification. In Proceedings of the 2023 24st Asia-Pacific Network Operations and Management Symposium (APNOMS),
Sejong, Republic of Korea, 6–8 September 2023; pp. 227–230.

Appl. Sci. 2024, 14, 3073

52.
53.

54.

23 of 23

Longadge, R.; Dongre, S. Class Imbalance Problem in Data Mining Review. arXiv 2013, arXiv:1305.1707.
Sharif, M.S.; Moein, M. An Effective Cost-Sensitive Convolutional Neural Network for Network Traffic Classification. In
Proceedings of the 2021 International Conference on Innovation and Intelligence for Informatics, Computing, and Technologies
(3ICT), Zallaq, Bahrain„ 29–30 September 2021; pp. 40–45.
Taylor, V.F.; Spolaor, R.; Conti, M.; Martinovic, I. Robust Smartphone App Identification via Encrypted Network Traffic Analysis.
IEEE Trans. Inf. Forensics Secur. 2017, 13, 63–78. [CrossRef]

Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
PAPER_TEXT
