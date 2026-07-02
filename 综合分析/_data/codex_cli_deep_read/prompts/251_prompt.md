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
# [251] Let model keep evolving: Incremental learning for encrypted traffic classification
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
编号：251
题名：Let model keep evolving: Incremental learning for encrypted traffic classification
年份：2023
DOI：10.1016/j.cose.2023.103624
来源：Computers & Security
PDF：paper/10.1016_j.cose.2023.103624.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\251.txt
- 原始字符数：96794
- 本次发送字符数：96794
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Computers & Security 137 (2024) 103624

Contents lists available at ScienceDirect

Computers & Security
journal homepage: www.elsevier.com/locate/cose

Let model keep evolving: Incremental learning for encrypted traﬃc
classiﬁcation
Xiang Li a,b , Jiang Xie c , Qige Song c , Yafei Sang a,∗ , Yongzheng Zhang d , Shuhao Li c ,
Tianning Zang a,b
a

Institute of Information Engineering, Chinese Academy of Sciences, Beijing, China
School of Cyber Security, University of Chinese Academy of Sciences, Beijing, China
c
Zhongguancun Laboratory, Beijing, China
d
China Assets Cybersecurity Technology CO., Ltd., Beijing, China
b

A R T I C L E

I N F O

Keywords:
Encrypted traﬃc classiﬁcation
Evolve
Incremental learning
Multi-view sequences
Cross-view information
Exemplar selection

A B S T R A C T
Encrypted Traﬃc Classiﬁcation (ETC) is valuable for many network management and security solutions as it
provides insights into applications active on the network. However, the network environment constantly evolves,
and new applications emerge in an endless stream daily, which gradually makes well-trained ETC models
ineﬀective. The conventional approach to adapting new applications is to re-train the models on a re-formed
dataset with both pre-existing and new application samples. The major limitation is that requiring redundant
computing resources and suﬃcient storage spaces. In this work, we propose an Incremental Learning (IL)
framework based on multi-view sequences fusion, MISS, to keep ETC models evolving with new applications. The
key novelty of MISS is three-fold: extract cross-view information from multi-view sequences to capture suﬃcient
knowledge; propose an exemplar selection algorithm from communication patterns to reduce redundant
consumption; design a pair of branches from the learnability of parameters to mitigate accuracy loss during
evolution. MISS outperforms the existing IL methods of ETC, and the state-of-the-art ETC models using the
classic IL framework, on the real-world network traﬃc datasets, which achieves satisfactory improvements
of 11.37%↑ and 1.58%↑. Furthermore, we comprehensively perform incremental experiments to evaluate the
evolution ability of MISS, which is able to select representative exemplars of old applications, counteract the
adverse eﬀects of homogeneous applications, and keep evolving with unknown applications.

1. Introduction
Traﬃc classiﬁcation is the process of identifying network applications and classifying the corresponding traﬃc, which is considered to
be the most fundamental functionality in QoS, QoE, and network management (Chen et al., 2021; Zhao et al., 2021). In recent years, we have
witnessed the rapid development of new network technologies and mobile ecosystems, accompanied by one key evolution where the traﬃc
is encrypted from plaintext in nature. A large number of websites and
applications utilize TLS technology for privacy protection and secure
communication (Liu et al., 2017). According to the Annual Report of
Let’s Encrypt (Group, 2020), HTTPS page loads reach 84% globally.
Such a trend of encryption dramatically reduces the available plaintext

information, disabling the traditional methods that rely on plaintext,
such as DPI (Deep Packet Inspection).
Several solutions for Encrypted Traﬃc Classiﬁcation (ETC) have
been proposed by researchers (Liu et al., 2019; Shen et al., 2017; Zheng
et al., 2020), which extract classiﬁable sequence features (mostly sidechannel information) from their standpoint. However, most of these
only work in close-world environments, namely, training ETC models
with a ﬁxed number of applications. Obviously, these models face a practical problem: when deployed in an open network environment, they gradually
lose their classiﬁcation ability due to the growing number of new applications. An intuitive explanation is shown in Fig. 1. The old model  in
the 0th phase, trained on TikTok, Amap, and Twitter, couldn’t classify
Alipay, Taobao, and Pingduoduo in the 1th phase. The most straightfor-

* Corresponding author.
E-mail addresses: lixiang1@iie.ac.cn (X. Li), sangyf793@gmail.com (Y. Sang).
https://doi.org/10.1016/j.cose.2023.103624
Received 24 March 2023; Received in revised form 21 October 2023; Accepted 22 November 2023
Available online 4 December 2023
0167-4048/© 2023 Elsevier Ltd. All rights reserved.

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

branch of model ′ to preserve learnability and then freezes itself as
the stable branch to maintain old knowledge. All learnable parameters
of model ′ are modiﬁed on a handful of pre-existing exemplars and
all new samples.
Our contribution can be brieﬂy summarized as:
• We design an IL framework, MISS, to keep ETC models classifying
new applications without training from scratch. In addition, a selection algorithm of representative exemplars is provided for ETC
tasks to avoid redundant storage.
• We build a pure TLS-encrypted traﬃc dataset, named PURE-TLS,
which contains 100 applications with 166,939 TLS ﬂows. Evaluations on PURE-TLS and three public datasets prove that MISS has
great classiﬁcation accuracy and evolution ability, compared with
the existing IL methods of ETC and the state-of-the-art (SOTA) ETC
models using the classic IL framework.
• We conduct extensive incremental experiments to evaluate the evolution ability of MISS, which is able to select more representative
exemplars, counteract the adverse eﬀects of homogeneous applications, and keep evolving with unknown applications.
Fig. 1. The old model trained on TikTok, Amap, and Twitter in the 0th phase
is unable to perform classiﬁcation eﬀectively in the 1th phase because Alipay,
Taobao, and Pingduoduo are added.

Roadmap: The rest of the paper is organized as follows. Section 2
summarizes the existing ETC and IL methods. Section 3 introduces the
basic deﬁnitions and concepts Details of the MISS framework are provided in Section 4. Section 5 shows the experiments and evaluations.
Section 6 and Section 7 put the discussion and conclusion.

ward approach for alleviating this issue is to re-train a new model ′
by combining pre-existing samples and the new ones. However, frequently re-train the model from scratch is redundant, time-consuming,
and costly (Xu et al., 2020b; Zhu et al., 2021).
Natural learning systems such as humans inherently work in an incremental evolution as concepts increase over time. An ideal ETC model
should also keep evolving incrementally like natural learning systems without
training from scratch when new applications are considered. However, the
model evolution inevitably forgets knowledge acquired from old applications, since the new optimizer will override the parameters tuned by
the old. It is not a wise choice by replaying the entire pre-existing samples to regain forgotten knowledge. This imperfection, as mentioned
above, can be reﬂected in two parts, for one thing, this is redundant
work while training resource is wasted, and for another, the storage
space is limited for entirely storing increasing samples.
In this paper, we propose an Incremental Learning (IL) framework
based on Multi-view Sequences FuSion, MISS,1 to keep ETC models
evolving with new applications. The key novelty of MISS is three-fold:

2. Related work
We focus on two research areas in terms of related work: Encryption
Traﬃc Classiﬁcation and Incremental Learning. Firstly, the past decade
has seen extensive research exploring encrypted traﬃc. We focus on the
utility of statistical and sequence features for the ETC. IL has continuous
research in Computer Vision (CV), and part of the work has appeared
in ETC. We elaborate on the existing work on IL from two perspectives:
IL methods for CV and IL methods for ETC.
2.1. Encryption traﬃc classiﬁcation
ETC tasks are based on the characteristics of encrypted traﬃc into
diﬀerent classes, such as applications, protocols or services, and have
important applications in network management, security and personalized recommendations.
Early on, researchers propose approaches based on port number and
data packet inspection, where traﬃc is classiﬁed by examining the trafﬁc port number or packet header information (Bujlow et al., 2015;
Finsterbusch et al., 2013). However, this approach is susceptible to
interference from techniques such as port masquerading, packet obfuscation and encryption. Then, machine learning-based approaches are
increasingly being employed for ETC tasks for their automated modeling and analysis capabilities (Velan et al., 2015). Researchers have
proposed several approaches combining statistical features and machine
learning algorithms to solve ETC tasks, e.g., (Aceto et al., 2017; Liu et
al., 2012; Taylor et al., 2017). Encrypted applications leak information
about dependencies or transfers between data messages, i.e., sequence
features, which are proven more eﬃcient and capture richer content
and contextual information (Liu et al., 2019; Wang et al., 2017a, 2020).
Korczynski et al. (Korczynski and Duda, 2014) proposed to represent
the TLS content type sequence with a markov transformation matrix
to recognize the encrypted ﬂow of applications. Rebuﬃ et al. (Shen et
al., 2017) propose an attribute-aware ETC method based on the secondorder markov chains that incorporating the attribute bigrams into the
homogeneous markov chains.
Currently, deep learning-based approaches with excellent performance on ETC tasks, which draw on deep learning techniques from
ﬁelds such as CV (e.g., convolutional neural networks, recurrent neural

❶ Evolution is the extension of the old model. How to get an outstanding
old model for evolution?
❷ Storage is limited. How to save as few pre-existing samples as possible
to reduce redundant storage?
❸ Forgetting is inevitable. How to reduce the forgetting of old knowledge
when learning new applications?
To answer ❶, MISS extracts cross-view information based on multiview sequences to enhance the initial classiﬁcation ability of old model
, and to provide enough information that can be inherited stably by
the next phase. In response to ❷, an exemplar selection algorithm from
the communication patterns is proposed to reduce the redundant storage of pre-existing samples. For ❸, a pair of plastic and stable branches
of new model ′ are designed: one for learning new applications, and
the other for maintaining old knowledge, to mitigate accuracy loss in
evolution.
Overall, MISS constructs an old model  that captures suﬃcient
knowledge by extracting cross-view information based on multi-view
sequences. During the evolution process, model  initializes the plastic

1

For readability not meaning, we shuﬄe the order to form a word.
2

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

networks, attention mechanisms), encode and classify raw traﬃc data
or high-level representations directly, without decomposing the problem into sub-problems of feature selection and classiﬁcation (Rezaei
and Liu, 2019; Wang et al., 2019). Deep learning is a breakthrough
compared to other methods, being able to automatically extract complex features from traﬃc, eliminating the need for expert knowledge to
select features, and having a signiﬁcant learning capability. Zheng et al.
(Zheng et al., 2020) built an autoencoder model to restore the packet
length sequence. Lin et al. (Lin et al., 2022) adopted the bidirectional
encoder representations transformer to extract features from payloads
byte sequence. Fu et al. (Fu et al., 2016) extracted packet length and
arrival time sequences to build a hidden markov model, which in turn
enhances the intrinsic richness of the model.
Most of the existing ETC methods are based on a single or fewer sequence
features, which are only highly generalized for one aspect of the encrypted
traﬃc and easily inﬂuenced by the network environment. Exploring the sufﬁcient knowledge and association relationship from multiple sequence views
to get an outstanding ETC model is one of the main contributions of this
work.

classiﬁcation to handle tight bandwidth resources and unstable channels eﬃciently.
Encrypted ﬂows have richer background information and a priori information compared with images. IL for ETC can be achieved not only by
balancing old and new knowledge with IL frameworks, but also be guided
to completion by some extra additional information. However, the existing
work only performs framework migration from CV to ETC. In contrast to
them, we systematically design an IL framework applicable to ETC that exploits traﬃc-speciﬁc information.
3. Preliminaries
3.1. IL problem deﬁnition of ETC
IL diﬀers from the conventional classiﬁcation setting in three aspects
(Liu et al., 2020): 1) the training data come in as a stream where the
samples of diﬀerent applications occur in diﬀerent phases; 2) in each
phase, the IL classiﬁer is expected to provide competitive performance
for all seen applications so far; 3) the machine storage is limited, so it
is impossible to save all data to replay the network training. Based on
the above conditions, we deﬁne the IL problem of ETC.
Suppose there are 𝑁+1 phases, i.e., one initial phase,2 and 𝑁 incremental phases, of the ETC process. In the 0th (initial){phase, we
}

2.2. Incremental learning
2.2.1. IL methods for CV
IL aims to learn eﬃcient models gradually in a series of incremental phases, each with new classes (Liu et al., 2021; Zhang et al., 2021).
Recent methods in CV have focused on how to avoid forgetting old
knowledge. Rebuﬃ et al. (Rebuﬃ et al., 2017) used a ﬁxed-size storage
space to store the exemplars of old classes, which replayed to reduce forgetting. Ostapenko et al. (Ostapenko et al., 2019) proposed a method
that synthesizes fake samples of the old tasks to balance the number of
exemplars between old and new classes. Rusu et al. (Rusu et al., 2016)
proposed the progressive network, which dedicated partially invariant
model parameters in diﬀerent incremental phases. Hou et al. (Hou et al.,
2019) introduced a set of regularization terms to mitigate the adverse
eﬀects of data imbalance between old and new classes. Douillard et al.
(Douillard et al., 2020) introduced PODNet, which uses varied pooling
dimensions in knowledge distillation to bridge feature representations
between consecutive models. Yan et al. (Yan et al., 2021) introduced
DER, which learned new features through the addition of a new network at each incremental step, and then utilized the concatenated old
and new features for the classiﬁcation. Kang et al. (Kang et al., 2022)
proposed a class-incremental learning method that uses knowledge distillation with adaptive feature consolidation to prevent the model from
forgetting the knowledge of old classes while learning new ones.

𝑐0 , ..., 𝑐𝑛0
0
th
(shortly as  ) applications. In the 𝑖 (incremental) phase, model 𝑖−1
build an initial model 0 on dataset 0 , which consists of

is unable to perform eﬀective classiﬁcation when 𝑖 consisting of  𝑖 applications{arrives. Due}to the storage limitation, we can’t keep the entire
previous 0 , ..., 𝑖−1 (as 0∶𝑖−1 ), but instead, we select and store a
handful of exemplars, namely 𝜆0∶𝑖−1 , as a replacement with |𝜆| ≪ ||.
All that needs to be done is to build the 𝑖 initialized by 𝑖−1 using
the new 𝑖 and the old 𝜆0∶𝑖−1 loading from storage, in order to achieve
a competitive classiﬁcation performance on the test data (unseen) of all
applications observed so far.
3.2. Descriptions of multi-view sequence features
In this work, the basic unit of ETC is a ﬂow, which is a collection
of packets exchanged between a pair of endpoints for the purpose of
inter-process communication across the Internet (Wang et al., 2013).
And the ﬂow is bi-directional, comprising a pair of unidirectional subﬂows going in opposite directions, in which the packets sent in each
direction can be identiﬁed by a unique 5-tuple {source IP, destination IP,
source port, destination port, protocol}. In order to apply machine/deep
learning classiﬁcation techniques, the ﬂow is further described by its
measurements on a predetermined sequence feature set (Millar et al.,
2021; Rezaei and Liu, 2019). In other words, each ﬂow is represented by

2.2.2. IL methods for ETC
IL for ETC also attracts researchers to explore. Sun et al. (Sun et
al., 2017) utilized a strategy known as one vs rest (OvR) to expand
the binary SVM model for identifying new applications. This approach
was also adopted by Chen et al. (Chen et al., 2021), who used OvR in
conjunction with neural network classiﬁers to classify encrypted traﬃc
incrementally. However, the scalability of the OvR approach is limited,
mainly when a large number of new applications are introduced. In response to this limitation, alternative approaches have been explored.
Bovenzi et al. (Bovenzi et al., 2021) investigated using the iCarl framework for the incremental classiﬁcation of encrypted traﬃc. Wu et al.
(Wu et al., 2022) proposed using knowledge distillation and bias correction to mitigate the issue of catastrophic forgetting in standard CNNs
when new applications are introduced. Li et al. (Li et al., 2020) introduced an incremental classiﬁcation framework based on a multiclass
support vector machine that can add new classiﬁcation planes and update all old planes for better classiﬁcation quality. Lee et al. (Lee et
al., 2020) employed an incremental SVM with a Stochastic Gradient
Descent algorithm to accomplish the encrypted malware traﬃc detection task. Zhu et al. (Zhu et al., 2022) proposed a federated incremental
learning scheme, Fed-SOINN, suited to Internet of Things (IoT) traﬃc

{ }𝑉

a vector set 𝑥𝑣 𝑣=1 , which can be regarded as a data instance observed
from 𝑉 views.
Speciﬁcally, we deﬁne the sequence feature set from the perspective of multiple granularity views that provide suﬃcient information
for the inheritance of evolution, as shown in Fig. 2. We measure the
inter-arrival time sequence feature of packets based on a sliding window,
along with the packet length sequence feature from the whole packet, and
the content type and payload byte sequence features from the detailed
TLS header and TLS payload, respectively (Table 1). Depending on the
existing work experience and sensitivity analysis (Lin et al., 2022; Lotfollahi et al., 2020), We extract the sequences of 𝑛=32 packets, and
based on that, only the ﬁrst 𝑚=128 bytes of payload are extracted.
3.2.1. Inter-arrival time sequence feature
We measure the inter-arrival time in seconds between each packet
of a ﬂow. To reduce the interference of network problems (e.g., network

2
For new applications/models, only the 0th phase is initial, and the others
are called old.

3

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

Fig. 4. Payload sequence feature with embedding.
Fig. 2. Extract the inter-arrival time, packet length, content type, and payload byte
sequence features from multiple granularity views, respectively.

the client to the server and negative to indicate sent from the server
to the client, e.g., [−𝟹𝟸𝟾, 𝟷𝟶𝟽𝟺, 𝟷𝟾𝟶, −𝟹𝟸𝟾, −𝟺𝟼𝟼...]. To process this raw
data for our learning model, we also employ a 1-gram dictionary for
re-encoding and perform subsequent embedding operations. This procedure transforms the sequence of packet lengths (including ±) into a
series of numbers, which are then embedded, just like the payload sequence feature operation.

Table 1
List of sequence features.
Symbol

Description

𝑥1

Inter-arrival time sequence feature.

𝑥2

Payload sequence feature.

𝑥3

Packet length sequence feature.

𝑥4

Content type sequence feature.

3.2.4. Content type sequence feature
The content type is a ﬂag in the TLS header that indicates
the semantic information, e.g., handshake:22, application data:23, of
the packet encrypted using TLS (Rescorla and Modadugu, 2012).
We also use positive and negative to denote directionality, e.g.,
[−𝟸𝟸, −𝟸𝟶, −𝟸𝟸, 𝟸𝟹, 𝟸𝟸, 𝟸𝟶, 𝟸𝟸...]. We again utilize a 1-gram dictionary
for re-encoding and performing embedding operations.
Especially to deserve to be mentioned, the sequence feature set of MISS
is scalable due to the fact that feature extraction is performed independently
for each view. It is recommended to use more sequence views (e.g., calculated
window size) to ensure the diversity and complementarity of application
knowledge.
4. The proposed MISS
In this section, we detail the proposed MISS. The overall workﬂow
of MISS is depicted in Fig. 5. We describe the initial model in the 0th
phase in detail, where the sequence features extraction, interaction, and
fusion processes between diﬀerent views are represented. Then, the evolution in the 𝑖th phase is elaborated from the data and model structure
perspectives. The optimization strategy is presented ﬁnally.

Fig. 3. Inter-arrival time sequence feature with embedding.

jitter), we split the ﬂow into multiple segments based on a sliding window 𝑤𝑖𝑛 (e.g., 0.1 s), and extend the inter-arrival time, e.g., [𝟸𝟺.𝟹𝟹𝟷𝟹,
𝟸𝟺.𝟹𝟹𝟷𝟻, 𝟸𝟺.𝟹𝟾𝟷𝟼, 𝟸𝟺.𝟺𝟾𝟻𝟸, 𝟸𝟺.𝟻𝟶𝟾𝟾...], into a 2-tuple 𝑥1 ={𝑣𝑠 , 𝑣𝑡 }, e.g.,
[{𝟶, 𝟶}, {𝟶, 𝟷𝟸𝟸}, {𝟶, 𝟻𝟶𝟹}, {𝟷, 𝟶} , {𝟷, 𝟸𝟹𝟼}...], one of the segment number, the other of the interval time from the ﬁrst packet in its segment.
To normalize the extended inter-arrival time into a vector, we perform
word embedding of {𝑣𝑠 , 𝑣𝑡 } through the parameter matrix 𝑊 ∈ ℝ𝑤×𝑑 ,
which transforms the discrete input sequence {𝑣𝑠 , 𝑣𝑡 } ∈ ℝ𝑛×1 into a
high-dimensional vector {𝑣𝑠 , 𝑣𝑡 } ∈ ℝ𝑛×𝑑 , where 𝑤 denotes the size of
𝑊 , and 𝑑 is the dimension. Then they are added and averaged together
bitwise, as shown in Fig. 3.

4.1. Solution overview
We construct the solution as a two-stage process, i.e., the initial model
in the 0th phase and the evolution in the 𝑖th phase, according to the problem deﬁnition: the aim of the ﬁrst stage is to design an outstanding
initial model in the 0th (initial) phase, and the second is to maintain
learning new applications and reduce the forgetting of the old in the 𝑖th
(incremental) phase.
For an evolvable ETC model, the initial classiﬁcation ability is the
key to determining the subsequent ability, which can provide accurate
and suﬃcient information to be inherited stably by the next phase.
In the 0th phase, the initial model structure mainly consists of three
components: multi-view sequence features extraction, cross-view information generation, and multi-view adaptive fusion, which seamlessly embeds
various view sequence features, generates stable cross-view information, and makes joint decisions by adaptive fusion strategy to improve
the classiﬁcation performance.
In the evolution process, forgetting is unavoidable because the parameters adjusted by the old applications will be overwritten when
learning the new. From the problem deﬁnition, it is clearly unwise to
store the entire previous samples to regain forgotten knowledge. In the
𝑖th phase, we design the evolution from the data and model structure

3.2.2. Payload sequence feature
Although TLS encrypts the payload, some side-channel information
can still be leaked (Sherry et al., 2015). To extract more contextsensitive information, we divide the payload into two-byte chunks.
For instance, the payload [𝟶𝟸𝟻𝟼𝟿𝚏𝟾𝚊𝚎𝚌𝟺𝟿𝟿𝚏𝟾𝚊𝟼𝟿𝚊𝚊...] is divided into
[𝟶𝟸𝟻𝟼, 𝟿𝚏𝟾𝚊, 𝚎𝚌𝟺𝟿, 𝟿𝚏𝟾𝚊, 𝟼𝟿𝚊𝚊...]. Following this, we recode it using a 1-gram dictionary. An exemplar of this is {𝟶𝟸𝟻𝟼 ∶ 𝟶, 𝟿𝚏𝟾𝚊 ∶ 𝟷,
𝚎𝚌𝟺𝟿 ∶ 𝟸, 𝟼𝟿𝚊𝚊 ∶ 𝟹...}. This allows us to form the payload feature vector, for instance [𝟶, 𝟷, 𝟸, 𝟷, 𝟹...], which is then embedded as shown in
Fig. 4.
3.2.3. Packet length sequence feature
We measure the packet length in bytes. Due to the bi-directional
nature of the ﬂow, we further use positive and negative to denote directionality. Speciﬁcally, we use positive to indicate the packet sent from
4

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

Fig. 5. Overview of MISS framework. ❶-❿ indicate the operations required to perform evolution. In the 0th phase, the initial model is involved as a whole to initialize
and freeze the next phase branches, and in the 1th phase, only the plastic model branch is used to initialize and freeze the next phase branches.

perspectives, involving three parts: representative exemplar selection, plastic and stable branches, and classiﬁcation layer with distillation loss. We
select (operation ❶) a handful of representative exemplars of old applications and all samples of the new to re-form the dataset, which is used
to train (operation ❺) all learnable parameters on the plastic and stable
branches. The plastic branch is initialized (operation ❷, ❽) by the previous plastic branch and preserves previous detection capabilities, as well
as the stable branch is the previous plastic branch that freezes (operation
❸, ❾) the vast majority of learnability. Note that, forgetting can only
be slowed down, not avoided (French, 1999; Kirkpatrick et al., 2017).
Based on this principle, we only reuse the model parameters of the most
recent phase instead of all previous phases. To fuse the outputs of both
branches, we further use a balanced dataset to train (operation ❻) the
weights [𝜀𝑝 , 𝜀𝑠 ] and feed them into a classiﬁcation layer with distillation
loss.
A list of abbreviations is presented in Table 2 to facilitate understanding of the notations adopted in what follows.

Table 2
List of abbreviations.
The ETC model in the 𝑖th phase.

𝑖

The application classes in the 𝑖th phase.

𝑖

The train set in the 𝑖th phase.

𝜆𝑖

The exemplars of 𝑖 in the 𝑖th phase.

𝑥𝑣

The sequence feature measured from the 𝑣th view of ﬂow 𝑥.

𝑓𝑣

The feature extraction network of the 𝑣th view.

𝑦𝑣

The advanced feature extracted by the 𝑣th neural network.

𝐶𝑣

The cross-view information of the 𝑣th view.

𝑌

The fusion vector of 𝑥 in the 0th phase.

{ }𝑉
For each ﬂow 𝑥, we extract various sequence features 𝑥𝑣 𝑣=1 from
𝑉 = 4 views to ensure the diversity and complementary of application
{ }𝑉
knowledge. Deﬁne a set of neural networks 𝑓𝑣 𝑣=1 where 𝑓𝑣 is the
th
extraction network of 𝑣 view and transforms 𝑥𝑣 from ℝ𝑑𝑣 into ℝ𝑑 , as

𝑖

The destination information Λ𝑖 of 𝑖 .

%

The exemplar retention rate.



The minimum number of exemplars per class.

𝑌 𝑝,𝑠

The plastic/stable fusion vectors of 𝑥 in the 𝑖th phase.

𝜀

4.2.1. Multi-view sequence features extraction

𝑝,𝑠

The weights of plastic/stable fusion vectors in the 𝑖th phase.

𝜂

The weighted output of plastic and stable fusion vectors.

𝑐

The cross-entropy loss.

𝑑

The distillation loss.

where 𝔼 is the cross-correlation matrix, and ⊤ means transpose. We
introduce a compressed network 𝜙 to project each element of 𝐶𝑣 from
the embedded space ℝ𝑑×𝑑 into ℝ𝑑 , in order to incorporate with 𝑦𝑣 ,
deﬁned as,

follows,

[
]
Υ𝑣 = 𝑦𝑣 | 𝜙(𝑊𝜙 (𝐶𝑣 ) + 𝑏𝜙 )

(1)

where 𝑦𝑣 ∈ ℝ𝑑 , and the parameters of each view are learned independently in parallel.

(3)
𝑑×𝑑 2

where | is the splicing operation, 𝑊𝜙 ∈ ℝ
and 𝑏𝜙 ∈ ℝ𝑑 which parameters are learned and shared across 𝑉 views.

4.2.2. Cross-view information generation
We deﬁne the cross-view information, generated by cross-correlating
attributes between diﬀerent sequence views, to obtain more stable and
potential information for the evolution. For the 𝑣th view, we calculate
the cross-correlation matrix (Xu et al., 2020a; Zbontar et al., 2021) between 𝑦𝑣 with other (𝑉 -1) views,

]}
{ [
𝐶𝑣 = 𝔼 𝑦 𝑣 , 𝑦 ⊤
𝑣̃
𝑣={1,⋯,𝑉
̃
}∖𝑣

Description

𝑖

Λ

4.2. The initial model in the 0th phase

𝑦𝑣 = 𝑓𝑣 (𝑥𝑣 )

Symbol

4.2.3. Multi-view adaptive fusion
Sequential features from diﬀerent views complement classiﬁcation
tasks, yet the precise contribution of each feature is uncertain. To
address this issue, we assemble all view feature matrices into multichannels to form a 3D matrice 𝑋 and input them into a multi-layer
perceptrons (MLPs) (Tolstikhin et al., 2021). This network, composed of
fully-connected layers and activation functions, adaptively captures the

(2)
5

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

of samples in some clusters might be less than  or that some samples
might not be clustered, we consolidate these samples into a comprehensive cluster.
Intra-cluster Herding. For each cluster of application 𝑐 , we acknowledge its importance in the exemplar selection process. To better
capture the characteristics of cluster 𝑧, we ﬁrst compute the average
feature vector 𝜂̄ of it using model 𝑀𝑖−1 . Subsequently, we employ the
herding algorithm (Welling, 2009), an iterative sample selection method
designed to pick samples that best represent the overall data distribution. Unlike methods that rely on randomness, the herding algorithm iteratively selects exemplars closest to the current average feature vector,
ensuring that the chosen exemplar set maximally reﬂects the original
data’s feature distribution. To ensure that all applications are treated
equitably during the selection process, we determine the value of 𝐾 ,
which represents the number of representative exemplars selected from
each cluster. Speciﬁcally, we have:

Fig. 6. Representative exemplar selection for 𝑖−1 . The selected exemplars will
be stored after each phase completion.

intrinsic relationships between diﬀerent views. Speciﬁcally, the operations are expressed as:

𝑋 = [Υ1 | Υ2 | ... | Υ𝑉 ],
𝑈 = 𝑋 + 2 𝜎(1 (𝐿𝑁(𝑋))),

(4)

(

𝑌 = 𝑈 + 4 𝜎(3 (𝐿𝑁(𝑈 )))

𝐾 = ceil

where 𝐿𝑁 means the LayerNorm operation, 1−4 denote the fullyconnected layers, and 𝜎 is an element-wise nonlinearity (e.g., GELU
(Hendrycks and Gimpel, 2016)). The resultant multi-view feature representation, 𝑌 (the output of MLPs), is then fed into the classiﬁcation
layer to predict the label, which is optimized by the cross-entropy loss.

𝐶̄ ×  % × len(𝑧)
len(𝑐)

)
(5)

where 𝐾 ≥ 1, ceil(⋅) is a mathematical function that rounds a number up to the nearest integer, 𝐶̄ denotes the average sample count of
the class,  % is the exemplar retention rate, and len(⋅) is a quantity
measurement function. Through the selection strategy of the herding
algorithm, we ensure that the average feature vector of the representative exemplars closely approximates the average feature vector of all
samples within the application. Moreover, by treating all applications
uniformly and considering all clusters for each application, we guarantee that the data’s diversity and completeness are fully taken into
account. This strategy, while retaining a subset of samples as exemplars, minimizes the risk of altering or eliminating the relationships and
diﬀerences between classes.

4.3. The evolution in the 𝑖th phase
4.3.1. Representative exemplar selection
The number of exemplars 𝜆0∶𝑖−1 is signiﬁcantly smaller than 0∶𝑖−1 .
Existing IL methods (Castro et al., 2018; Hou et al., 2019; Liu et al.,
2020) are always based on the assumption that the model trained on
a handful of exemplars also minimizes the loss of all old samples.
In order to achieve this in ETC tasks, we split the exemplar selection
into two steps: Intra-class Clustering and Intra-cluster Herding. Initially,
for each old class, we identify all its communication pattern clusters
through Intra-class Clustering. This step ensures that we capture the diverse communication patterns inherent within each class. Subsequently,
during the Intra-cluster Herding phase, we select the most representative
exemplars from each identiﬁed communication pattern cluster. This
meticulous selection approach guarantees that the chosen exemplars
comprehensively and accurately reﬂect the intrinsic structure and distribution characteristics of each class, thereby providing a more holistic
and representative exemplar set for model evolution, as illustrated in
Fig. 6. Algorithm 1 further details this process.
Intra-class Clustering. Applications typically consist of various
modules, each communicating with external servers or services to fulﬁll their functionalities. Such communications are often associated with
speciﬁc network destinations, such as server IP addresses and ports.
These communication destinations tend to remain relatively stable over
time, providing clues to the inherent communication patterns of applications. To capture these patterns, we cluster the samples of application
𝑐 in 𝑖−1 based on the following two criteria:

Algorithm 1: Representative Exemplar Selection.
: Dataset 𝑖−1 of applications  𝑖−1
Destination information Λ𝑖−1 of 𝑖−1
Average sample amount 𝐶̄ (per class)
Minimum  and top  %
Require: (𝑖 − 1) th phase model 𝑖−1
Clustering algorithm Ψ
Index mapping function 𝜉
for 𝑐 in  𝑖−1 do
 ← Ψ(Λ𝑖−1
, ) // Intra-class Clustering
𝑐
for 𝑧 in  do
Input

∑
𝜂̄ ← mean( 𝑚∈𝑧 𝑖−1 (𝜉(𝑚, 𝑖−1 ))
̄
𝐾 = 𝑐𝑒𝑖𝑙(𝐶 ×  % × 𝑙𝑒𝑛(𝑧)∕𝑙𝑒𝑛(𝑐))
for 𝑗 = 1, ⋯ , 𝐾 do
∑𝑗−1
𝑝𝑗 ← argmin‖𝜂̄ − 1𝑗 × [𝑖−1 (𝜉(𝑚, 𝑖−1 )) + 𝑘=1 𝑖−1 (𝜉(𝑝𝑘 , 𝑖−1 ))]‖
𝑚∈𝑧

// Intra-cluster Herding

𝑃𝑧 ← {𝑝1 , ⋯ , 𝑝𝐾 }
𝑐 ← {𝑃𝑧 }𝑧∈
𝜆𝑖 ← {𝑐 }𝑐∈ 𝑖−1

if 𝑖 = 1 then
Output : Exemplar set 𝜆𝑖−1
else

𝜆0∶𝑖−1 ← {𝜆0 , ⋯ , 𝜆𝑖−2 } + 𝜆𝑖−1

• Samples containing identical {destination IP, destination port}tuples.
• Samples containing identical/similar TLS certiﬁcates.

Output : Exemplar set 𝜆0∶𝑖−1

4.3.2. Plastic and stable branches
In the 𝑖th phase, our model deploys a pair of branches, namely,
the Plastic Branch and the Stable Branch, distinguished by the diﬀerent learnability of their parameters. The Plastic Branch, initialized by
𝑖−1 (or the entire initial model 0 ), serves to adapt and learn from
new data. All parameters in this branch are learnable and updated at
each stage, allowing the model to continuously optimize with the introduction of new information. The Stable Branch, on the other hand, acts
as the knowledge store of our model. After the Plastic Branch initializes
the next phase, the current model freezes itself as the Stable Branch,

This clustering approach is grounded in a deep understanding of
real-world communication patterns exhibited by applications. It’s worth
noting that while identical {destination IP, destination port}-tuples
might map to diﬀerent services due to mechanisms like CDNs or load
balancers, our objective isn’t to precisely identify speciﬁc service attributes of the traﬃc. Instead, we aim to select representative exemplars
that eﬀectively capture the unique communication patterns of applications. Consequently, choosing representative exemplars from consistent
CDN traﬃc or load balancers aids the model in gaining a deeper understanding of these patterns. Additionally, considering that the number
6

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

• The aggregation weights [𝜀𝑝 , 𝜀𝑠 ] can be updated by mini-batches of
a balanced dataset when the learnable parameters are temporarily
ﬁxed.

only preserving the neuron-level scaling weights to maintain the structural pattern within the neuron (Liu et al., 2021; Sun et al., 2019). This
process ensures the retention of learned knowledge, acting as a protective mechanism against the catastrophic forgetting problem in the
continuous learning process of deep learning models. By re-training all
learnable parameters of both branches on the exemplars 𝜆0∶𝑖−1 and new
samples 𝑖 , we strike a balance between adaptation to new data and
preservation of previous knowledge. Given a ﬂow instance, we compute the plastic vector 𝑌 𝑝 and the stable vector 𝑌 𝑠 , through the plastic
and stable branches, respectively. Let 𝜀𝑝 and 𝜀𝑠 denote the aggregation
weights, and the weighted sum of 𝑌 𝑝 and 𝑌 𝑠 can be derived as,

𝜂 = 𝜀𝑝 ⋅ 𝑌 𝑝 + 𝜀𝑠 ⋅ 𝑌 𝑠

In this way, the optimality of learnable parameters imposes a constraint on the aggregation weights and vice versa. Algorithm 2 describes
the optimization strategy.
Algorithm 2: The Optimization Strategy.
Input : 𝑖 and exemplars 𝜆0∶𝑖−1
Require: (𝑖 − 1)th phase model 𝑖−1
Get 𝑖 and load 𝜆0∶𝑖−1
Select exemplars 𝜆𝑖 from 𝑖 by Algorithm 1 with 𝑖−1
Initialize and freeze 𝑖 with 𝑖−1
for epochs do
for batches in 𝜆0∶𝑖−1 ∪ 𝑖 do
Train parameters of 𝑖−1 on 𝜆0∶𝑖−1 ∪ 𝑖

(6)

where 𝜀𝑝 and 𝜀𝑠 are learnable parameters, and we describe the optimization strategy in detail in Section 4.4.

for mini-batches in 𝜆0∶𝑖−1 ∪ 𝜆𝑖 do
Train [𝜀𝑝 , 𝜀𝑠 ] on 𝜆0∶𝑖−1 ∪ 𝜆𝑖

4.3.3. Classiﬁcation layer with distillation loss
As we introduce new classes, we strategically discard the existing
classiﬁcation layer. This allows us to introduce a new layer, tailored
to accommodate both new and old classes. This approach ensures our
model remains adaptable to new classes without sacriﬁcing its proﬁciency with the old ones. The new classiﬁcation layer is modiﬁed to
combine the distillation loss (Hinton et al., 2015) and the cross-entropy
loss, which allows remembering the old applications while learning the
decision boundaries for the new. The distillation loss 𝑑 encourages the
𝑖 and previous 𝑖−1 to maintain the same prediction ability on old
applications, formulated as,

Update exemplar 𝜆𝑖 from 𝑖 by Algorithm 1 with 𝑖

The balanced dataset, pivotal for our optimization process, is used
in mini-batches. It’s carefully assembled by combining representative
exemplars of new classes, which are initially chosen via our proposed
exemplar selection algorithm and based on the representations from the
preceding model 𝑖−1 , with exemplars from both old 𝜆0∶𝑖−1 and new
classes 𝜆𝑖 . This ensures an even distribution of samples from both sets
of classes, eﬀectively reducing class-speciﬁc bias and optimizing for a
more precise [𝜀𝑝 , 𝜀𝑠 ].
As we transition to the current phase model 𝑖 , it becomes crucial
to reselect exemplars for the new classes according to the updated representations. This ensures that the new class exemplars align with the
latest model representations, making the selected samples more indicative of the exemplars required by the current model.

𝑀
∑
(
)
𝑑 𝑖 ; 𝑖−1 ; 𝜂 = −
𝜋̂ 𝑚 (𝜂) log 𝜋𝑚 (𝜂)
𝑚=1

𝑒𝑝̂𝑚 (𝜂)∕𝑡

𝜋̂ 𝑚 (𝜂) = ∑𝑀

𝑗=1 𝑒

𝑝̂𝑗 (𝜂)∕𝑡

,

𝑒𝑝𝑚 (𝜂)∕𝑡
𝜋𝑚 (𝜂) = ∑𝑀
𝑝𝑗 (𝜂)∕𝑡
𝑗=1 𝑒

(7)

where 𝑀 is the number of applications in 𝜆0∶𝑖−1 , 𝑝𝑚 (𝑥) and 𝑝̂𝑚 (𝑥) denote the prediction logits of the 𝑚th application from 𝑖 and 𝑖−1 ,
and 𝑡 is a temperature scalar set to be greater than 1 to assign larger
weights to smaller values. The cross-entropy loss 𝑐 still is used as the
classiﬁcation loss, formulated as,
𝑀+𝑀
∑
(
)
𝑐 𝑖 ; 𝜂 = −
▽𝑦=𝑚
log 𝑝𝑚 (𝜂)
̃

5. Experiments
In this section, we are dedicated to evaluating the performance of
MISS. We ﬁrst introduce the public datasets and a newly proposed
dataset used for conducting comprehensive experiments (Section 5.1),
and then explain the experimental settings (Section 5.2). After that, we
thoroughly compare MISS with the existing IL methods of ETC, and the
SOTA ETC models using classic IL framework, in terms of classiﬁcation
accuracy and evolution ability (Section 5.3). Finally, we comprehensively evaluate the eﬀect of diﬀerent increment settings on the evolution
ability of MISS (Section 5.4). Additionally, our experiments were implemented with Pytorch 1.10.0, conducted with NVIDIA 3090 GPUs.

′

(8)

𝑚=1

where 𝑀 ′ is the number of applications in 𝑖 , 𝑦̃ is the ground-truth
label, and ▽𝑦=𝑚
is an indicator function. As mentioned earlier, we only
̃
calculate 𝑐 in the 0th phase, and jointly calculate 𝑑 and 𝑐 to add up
in the other phases.

5.1. Dataset description

4.4. The optimization strategy

To comprehensively validate the performance of the MISS framework, we conduct experiments on three public datasets and one newly
proposed dataset, as shown in Table 3.

In each incremental phase, we optimize two groups of parameters in
MISS:
• The learnable parameters of both branches.
• The aggregation weights [𝜀𝑝 , 𝜀𝑠 ] of branches’ output.

5.1.1. Cross-platform dataset
The Cross-Platform (iOS) (Ren et al., 2019) and Cross-Platform (Android) (Ren et al., 2019) collect most popular applications for iOS and
Android from each country (US, China, and India), of which randomly
select 190 and 200 applications for experiments, respectively. These
datasets with long-tail data distribution over all applications.

The former is for network parameters, and the latter is for hyperparameters. The aim of the 𝑖th phase is to learn the optimal branches’
parameters and [𝜀𝑝 , 𝜀𝑠 ] that minimize the loss on all training samples
seen so far. Based on this objective, we formulate the overall optimization process as a bilevel optimization program (BOP) (Goodfellow et al.,
2014; Liu et al., 2021):

5.1.2. USTC-TFC-2016 dataset
Encrypted malicious traﬃc is one of the Internet security threats.
The USTC-TFC-2016 (Wang et al., 2017b) is a collection of encrypted
traﬃc consisting of malware and benign applications, containing 10
benign and 10 malicious.

• The learnable parameters of both branches are trained using the
aggregation weights [𝜀𝑝 , 𝜀𝑠 ] as hyperparameters.
7

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

Table 3
The Statistical Information and Incremental Settings of Datasets. Total means the
total number of applications, and Half means the half (or close to half) of the
total. N means the number of incremental phases of the dataset, and C means the
number of new applications per increment phase.
Dataset

Flow

Total

Half

N Phases

C Classes

Cross-Platform (iOS)

23,987

190

90

[1, 10, 25]

[100, 10, 4]

Cross-Platform (Android)

34,642

200

100

[1, 10, 25]

[100, 10, 4]

USTC-TFC-2016

28,516

20

10

[1, 5]

[10, 2]

PURE-TLS

166,939

100

50

[1, 10, 25]

[50, 5, 2]

5.1.3. PURE-TLS dataset
Most existing public network traﬃc datasets mix encrypted TLS trafﬁc ﬂows with vast amounts of unencrypted TCP/UDP ﬂows. However,
over 90% of today’s network traﬃc is encrypted (Google, 2022). To analyze pure encrypted TLS traﬃc, we collect 100 applications using Monkeyrunner (Chang et al., 2016) to constitute the PURE-TLS dataset, as
seen details in Table 4. For the construction of PURE-TLS, we install the
target applications and the necessary system applications on a rooted
Google Pixel3 phone, and then connect to a computer WIFI hotspot to
produce the network traﬃc. Based on PCAPDroid,3 we capture the trafﬁc with application labels directly from the network interface of the
Android device. PCAPDroid will add a fake Ethernet header containing
the application name to the packet to encapsulate the original IP header
and data during traﬃc capture. In addition, to further ensure the authenticity of data and the accuracy of annotations, we simultaneously
employ Wireshark to capture hotspot data on the computer side, and
verify the relationship between the Wireshark raw streams and the application labels in PCAPDroid with the ﬁve-tuple and timestamp (Aceto
et al., 2019a). Finally, we collect and compile a complete dataset of
pure encrypted traﬃc.
To provide a better understanding of the PURE-TLS dataset, we illustrate the ﬂow number distribution of the dataset, as presented in Fig. 7.
Additionally, a series of the sequence features of the PURE-TLS dataset
is depicted as heatmaps. Each row corresponds to a diﬀerent application, while columns represent diﬀerent sequence positions (packet index), with values averaged across all ﬂows. Upon closely examining the
heatmaps, we observe signiﬁcant variations in ﬂow distribution across
diﬀerent classes. Quantitatively, the most predominant class comprises
7127 ﬂows, while the least populated class has only 98. When analyzing
the sequence distribution of average packet lengths, the ﬁrst 32 packets
emerge as crucial for class diﬀerentiation. The distribution of average
inter-arrival times underscores the dataset’s intricacy, revealing unique
communication patterns across various applications. Additionally, the
packet direction sequence, represented by ±1, enhances feature classiﬁcation. This representation oﬀers deep insights into the nuanced
behaviors distinguishing diﬀerent applications.
5.2. Experimental settings
5.2.1. Traﬃc preprocessing
We need to perform preprocessing to remove the ethernet header
and follow (Lin et al., 2022; Wang et al., 2017a) without feature extraction for the IP header and protocol port of ﬂows in the classiﬁcation
process to avoid the eﬀect of the packet header, which may introduce
biased interference for classiﬁcation in a ﬁnite set with strong identiﬁcation information. The IP and port background knowledge is only used
as a priori information (van Ede et al., 2020; Wang et al., 2013) to guide
the clustering process when selecting exemplars. We extract the payload
byte, arrival time, and packet length sequence views for the three public datasets, adding the content type sequence view for the PURE-TLS
dataset.

3

Fig. 7. Visualizations of PURE-TLS dataset. (a) Flow number distribution. (b) Sequence distribution (the ﬁrst 100 packets) of the average packet length of each
class. (c) Sequence distribution of the average inter-arrival time of each class.
(d) Sequence distribution of the packet direction (±1) of each class.

5.2.2. Training & testing
For each dataset, approximately half of the total applications are
selected to train an initial model, serving as the starting point. The remaining applications are equally divided for 𝑁 incremental phases,
following the recommendations in (Castro et al., 2018; Hou et al.,
2019; Rebuﬃ et al., 2017). To determine the application subset for

https://emanuele-f.github.io/PCAPDroid.
8

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

then divided into the training set, the validation set, and the testing set
according to the ratio of 6:1.5:2.5, with a random initialization based
on random seeds to prevent potential biases from sample partitioning.

Table 4
Details of the PURE-TLS Dataset.
ID

Application

Flow

ID

Application

Flow

1

allhistory

108

51

sogou

130

2

instagram

4,114

52

baidumap

1,841

3

qqmusic

399

53

baiduhomework

294

4

douyu

649

54

lizhifm

700

5

jxedt

704

55

youku

3,943

6

bilibili

1,390

56

blued

4,786

7

gifmaker

320

57

changba

156

8

TikTok

2,972

58

mtt

619

9

qiyivideo

1,456

59

tuchong

3,507

10

baiduvideo

3,038

60

toutiao

4,324

11

ijinshan

322

61

funshionvideo

308

12

taobao

4,861

62

Lark

2,819

13

TripAdvisor

2,943

63

browser2345

642

14

linkedin

1,524

64

mobiletv

699

15

ctrip

3,366

65

kuwo

213

16

vipshop

6,598

66

kmxsreader

285

17

yangshipin

814

67

letv

237

18

articlevideo

877

68

huya

2,640

19

storm

862

69

ximalaya

540

20

12306MobileTicket

299

70

amap

1,682

21

iReaderFree

432

71

haokan

2,737

22

quark

108

72

duoshan

3,148
863

23

guotaijunan

2,153

73

tencentnews

24

meiyancamera

626

74

baidutieba

1,000

25

qq

102

75

iﬂytek

117

26

acfundanmaku

385

76

cmvideo

371

27

mtxx

669

77

weibo

2,285

28

airbnb

2,777

78

neteasecloudmusic

3,484

29

huajiao

797

79

mjweather

484

30

lemon

733

80

kugoufanxing

688

31

github

3,813

81

baiduwangpan

815
1,155

32

alipay

3,821

82

DCar

33

Qunar

208

83

zhihu

2,998

34

gogokid

1,234

84

UCMobile

413

35

mmweather

1,013

85

baidusearchbox

3,536

36

Reddit

4,519

86

tencentmap

9,58

37

qqreader

672

87

m2u

98

38

articlenews

1,295

88

superb

909

39

comicsisland

505

89

qqpimsecure

318

40

youthnew

831

90

twitter

2,057

41

pinduoduo

4,738

91

shuqi

415

42

booking

7,127

92

souhutv

342

43

imgo

3,624

93

kuaikan

1,325

44

ugclive

734

94

tujia

521

45

weishi

2,715

95

qqlive

612

46

ele

5,865

96

dragonread

901

47

tudou

1,309

97

weidian

321

48

wuba

491

98

baiduwenku

1,173

49

facebook

2,568

99

meituan

3,052

50

jingdong

3,894

100

anjuke

2,104

5.2.3. Methods to compare
To obtain a comprehensive understanding of the performance of
MISS, we use two existing IL methods of ETC to conduct comparisons,
• Omt-CNN (Wu et al., 2022) is an online multimedia incremental
framework that uses the sliding window to capture the ﬂow slices
for feature extraction. The knowledge distillation and bias correction techniques are applied with old and new samples to overcome
the catastrophic forgetting of the standard CNN when new ones
appear.
• CNN-iCarl+ (Bovenzi et al., 2021) is an adapted version based
on the classical IL framework, iCarl (Rebuﬃ et al., 2017), for the
ETC task, which uses a classiﬁcation layer with Softmax to replace
the nearest mean classiﬁer of iCarl and a dynamic output layer
expansion ﬁtting the number of new applications.
In an eﬀort to create more detailed comparisons, we introduce two
methods of migration as shown in Table 5,
• Mv Frame Migration. We utilize the multi-view (Mv) framework
MIMETIC (Aceto et al., 2019b), developed for CNN network architectures, to overhaul the feature construction of both the OmtCNN
and the CNN-Model, with maintaining the same types of feature
input, resulting in Omt-CNN (Mv) and CNN-iCarl+ (Mv). For
instance, we extract features such as Packet length, Inter arrival
time, and Packet direction by the 1d-CNN of CNN-iCarl+, respectively. We then employ the merged layer and associated part of
the MIMETIC framework to amalgamate these features before additional processing.
• IL Frame Migration. For comparison with SOTA ETC models
(without incremental ability), we migrate the iCarl framework to
the EBSNN (Xiao et al., 2021) and ET-BERT (Lin et al., 2022), resulting in EBSNN (IL) and ET-BERT (IL). As suggested by (Bovenzi
et al., 2023, 2021), we retain the overall structures (input layer,
feature extraction layer, and output layer) and training methods
of SOTA models while adding the iCarl’s model parameter passing, speciﬁc loss function, and exemplar selection components to give
them incremental ability. For instance, we use the ET-BERT’s model
structure as the initial model in the 0th phase, and feed the initial
model parameters to the 1th phase by iCarl’s model parameter passing
in order to replace ET-BERT’s loss with iCarl’s speciﬁc loss function
and select old samples by iCarl’s exemplar selection after each incremental phase.
5.2.4. Evaluation metrics
The primary goal of ETC is Accuracy, namely, correctly identifying more encrypted traﬃc ﬂows and avoiding misclassiﬁcation (Xu
et al., 2022). However, considering the long-tail data distribution nature of the dataset, we use an additional evaluation metric, F1-score,
which considers both Precision and Recall. Meanwhile, we adopt the
macro-average, which averages the performances of each individual application (𝑘 applications here),

𝐴𝑐𝑐𝑢𝑟𝑎𝑐𝑦 1 + … + 𝐴𝑐𝑐𝑢𝑟𝑎𝑐𝑦 𝑘
𝑘
∑
∑
( 𝑘1 𝑘𝑖=1 𝑃 𝑟𝑒𝑖 ) ∗ ( 𝑘1 𝑘𝑖=1 𝑅𝑒𝑐𝑖 )
𝐹1 = 2 ∗
1 ∑𝑘
1 ∑𝑘
𝑖=1 𝑃 𝑟𝑒𝑖 + 𝑘
𝑖=1 𝑅𝑒𝑐𝑖
𝑘

𝐴𝐶𝐶 =

each phase, we initialize the class labels list using a random seed
to shuﬄe the list in each repeated experiment. From this shuﬄed
list, classes are randomly selected for both the initial and incremental phases. This method ensures variance in both the category selection
for the initial model and the order of class addition during the incremental phases, mitigating potential biases. We randomly select up to
𝑚𝑖𝑛(#𝐹 𝑙𝑜𝑤, 500) ﬂows from each application of all public datasets and
𝑚𝑖𝑛(#𝐹 𝑙𝑜𝑤, 1, 000) ﬂows of the newly proposed dataset. These ﬂows are

(9)

where 𝐴𝐶𝐶 is macro-average Accuracy, 𝐹 1 is macro-average F1-score,
𝑃 𝑟𝑒 is Precision, and 𝑅𝑒𝑐 is Recall. The mean and standard deviation
of metrics are reported by repeating 3 times to ensure the robustness of
the results.
9

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

Table 5
Summary of the compared methods. Mv Frame means MIMETIC multi-view framework. IL Frame means iCarl incremental
learning framework.
Method

Network

Feature Input

Mv Frame Migration

Omt-CNN (Mv)

CNN

Packet length, Inter arrival time, Byte rate

✓
✓

IL Frame Migration

CNN-iCarl+ (Mv)

CNN

Packet length, Inter arrival time, Packet direction

EBSNN (IL)

RNN

Header segment, Payload segment

✓

ET-Bert (IL)

Transformer

Payload (with Pre-training)

✓

Table 6
Average incremental Accuracies (avg.ACC)% and F1-score (avg.F1)% on Cross-Platform (iOS) and PURE-TLS datasets.
Method

Omt-CNN

Omt-CNN (MV)
CNN-iCarl+

CNN-iCarl+ (MV)
EBSNN (IL)

ET-Bert (IL)
MISS-CNN

MISS-TF

Dataset
Phase
avg.ACC
avg.F1

Cross-Platform (iOS)
UB
N=1
85.25 ± 0.31
79.70 ± 0.60
82.99 ± 0.25
77.25 ± 0.63

N=10
76.90 ± 0.60
75.63 ± 0.63

N=25
74.24 ± 0.71
71.12 ± 0.46

PURE-TLS
UB
87.04 ± 0.45
82.80 ± 0.44

N=1
81.22 ± 0.56
76.60 ± 0.63

N=10
75.02 ± 0.55
74.99 ± 0.63

N=25
75.72 ± 0.60
70.85 ± 0.56

avg.ACC
avg.F1
avg.ACC
avg.F1

87.93 ± 0.38
85.62 ± 0.34
90.27 ± 0.32
84.06 ± 0.28

82.37 ± 0.51
80.31 ± 0.57
85.81 ± 0.49
82.79 ± 0.58

79.08 ± 0.33
78.51 ± 0.38
84.90 ± 0.37
82.74 ± 0.42

76.27 ± 0.56
73.92 ± 0.64
83.21 ± 0.48
80.61 ± 0.49

89.57 ± 0.34
85.05 ± 0.29
84.32 ± 0.58
82.84 ± 0.60

83.97 ± 0.40
79.98 ± 0.44
82.62 ± 0.38
80.45 ± 0.35

77.19 ± 0.42
74.99 ± 0.44
81.98 ± 0.43
81.07 ± 0.72

78.75 ± 0.59
73.68 ± 0.63
77.18 ± 0.57
75.53 ± 0.53

avg.ACC
avg.F1
avg.ACC
avg.F1

92.13 ± 0.36
85.21 ± 0.42
92.12 ± 0.74
86.71 ± 0.81

85.99 ± 0.45
82.67 ± 0.51
87.22 ± 0.51
83.33 ± 0.49

83.12 ± 0.45
79.70 ± 0.38
86.38 ± 0.74
82.51 ± 0.60

79.56 ± 0.40
78.72 ± 0.43
83.10 ± 0.75
79.73 ± 0.81

90.22 ± 0.44
88.87 ± 0.39
87.59 ± 0.79
86.22 ± 0.85

85.78 ± 0.56
84.95 ± 0.60
82.75 ± 0.44
81.35 ± 0.37

83.90 ± 0.35
82.01 ± 0.31
78.86 ± 0.63
77.96 ± 0.59

79.38 ± 0.57
79.61 ± 0.60
76.06 ± 0.68
75.88 ± 0.79

avg.ACC
avg.F1
avg.ACC
avg.F1

98.84 ± 0.24
97.20 ± 0.14
95.87 ± 0.50
91.06 ± 0.44

95.60 ± 0.33
94.01 ± 0.37
93.89 ± 0.27
89.84 ± 0.32

95.54 ± 0.12
93.37 ± 0.12
92.85 ± 0.32
89.21 ± 0.32

95.33 ± 0.17
92.92 ± 0.15
89.13 ± 0.24
84.68 ± 0.27

98.68 ± 0.06
97.35 ± 0.27
90.40 ± 0.26
87.60 ± 0.27

96.11 ± 0.29
95.97 ± 0.29
86.45 ± 0.38
83.86 ± 0.40

95.39 ± 0.58
93.48 ± 0.51
84.64 ± 0.21
81.26 ± 0.26

94.61 ± 0.42
94.44 ± 0.37
82.15 ± 0.37
79.22 ± 0.39

avg.ACC
avg.F1

98.12 ± 0.31
97.71 ± 0.25

97.18 ± 0.32
97.03 ± 0.28

97.03 ± 0.2
96.56 ± 0.19

96.71 ± 0.34
96.09 ± 0.36

98.24 ± 0.25
98.34 ± 0.28

96.84 ± 0.21
97.06 ± 0.20

97.29 ± 0.35
97.46 ± 0.37

96.40 ± 0.23
96.61 ± 0.17

5.2.5. Implementation details
To evaluate the impact of the initial model, we use Text-CNN (Chen,
2015) and Transformer (Vaswani et al., 2017), the advanced models
with promising sequence modeling capabilities, as the multi-view sequence features extraction networks, respectively. For Text-CNN, we use
a set of SGD optimizers with a momentum of 0.9 and a batch size of
256, one with a learning rate of 0.01 to train the ETC model and another with a learning rate of 1 × 10−6 to learn 𝜀. For Transformer, we
only replace the training model optimizer by BertAdam with a learning rate of 0.05 in the 0th phase. And the incremental phases are set
up in the same way as TextCNN. We impose a constraint to ensure that
𝜀𝑝 + 𝜀𝑠 = 1, initialized to [𝜀𝑝 =0.5, 𝜀𝑠 =0.5]. Empirically, we put  and
 % in the preliminary experiments as 10 and 10%. These hyperparameter settings perform best on our development set.

5.3.1. Analysis of diﬀerent initial models
Under the same IL framework, the UB of MISS-TF is improved by
2.25% and 6.65% compared with MISS-CNN on Cross-Platform (iOS),
whose excellent performance is inherited in incremental phases, i.e.,
the average drop (avg.ACC/F1 of UB − avg.ACC/F1 of N) of MISS-TF is
2.71%↓ and 2.03%↓ less than MISS-CNN. Similarly, the same trend is
observed between ET-Bert (IL) and others using the iCarl IL framework,
i.e., EBSNN (IL) and EBSNN (IL), more pronounced for 𝑁 =25.
5.3.2. Analysis of diﬀerent IL frameworks
Under similar Transformer feature extraction networks, MISS-TF,
without pre-training, does not perform as well as the pre-training ETBert (IL) in the UBs of multiple datasets, but outperforms ET-Bert (IL)
in the evolution of all datasets. MISS-TF achieves the best performance
on avg.ACC and avg.F1 of Cross-Platform (iOS) as 97.18% and 97.03%,
which are only 0.94%↓ and 0.68%↓ drops compared to the UB, 1.58%
and 3.02% higher compared to ET-Bert (IL). Under similar CNN feature
extraction networks, MISS-CNN achieves the best results compared with
diﬀerent IL frameworks, i.e., Omt-CNN and CNN-iCarl+. MISS-CNN only
drops by 1.98%↓ on avg.ACC when 𝑁 is 1, but Omt-CNN by 5.55%↓
and CNN-iCarl+ by 4.46%↓.
In comparing the two groups that employed the Mv Frame migration
methods, the multi-view feature approach is proven to improve the UB
performance of the models, providing a solid start for the incremental
phase. The UB of Omt-CNN (Mv) outperforms Omt-CNN by 2.68% and
2.63%, respectively, and correspondingly, the incremental phase has
also improved by an average of 2.29% and 2.91%. However, although
the UB of CNN-iCarl+ (Mv) is improved, the incremental phase of some
datasets sees a decrease, potentially due to compatibility issues brought
about by the Mv Frame method.

5.3. Comparison with IL methods and SOTA models of ETC
We evaluate the classiﬁcation accuracy and evolution performance
of MISS with four datasets, as shown in Table 6 and Table 7, where the
average incremental 𝐴𝐶𝐶 (avg.ACC) and 𝐹 1 (avg.F1), i.e., the average values of metrics in all phases, are reported as the ﬁnal evaluation.
Note that the phase-wise ACC and F1 in each phase of Cross-Platform
(iOS) and PURE-TLS datasets can be found in Fig. 8. Two IL methods
of ETC, Omt-CNN, CNN-iCarl+, and two SOTA ETC models using the
iCarl IL framework, EBSNN (IL) and ET-Bert (IL), are used as comparison approaches (details in Section 5.2.3). Note that we produce two
variants of the MISS framework, MISS-CNN and MISS-TF, with diﬀerent feature extraction networks, Text-CNN and Transformer (details in
Section 5.2.5). For the purpose of better comparison, we state here two
concepts: in each phase, the result of retraining (without any incremental measures) the new model using all the resources, i.e., all the training
datasets 0∶𝑖 , is called the Upper Bound (UB); correspondingly, the result of using the restricted resources in each phase, i.e., the training data
set 𝑖 of the current phase and the exemplar set 𝜆0∶𝑖−1 of the previous
phases, is called the Lower Bound (LB).

Takeaway. A well-designed IL framework combined with a matching feature
extraction architecture can signiﬁcantly mitigate the degradation of model
classiﬁcation performance. Moreover, establishing a high Upper Bound for
the initial model proves to be a crucial factor in its successful evolution.
10

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

Table 7
Average incremental Accuracies (avg.ACC)% and F1-score (avg.F1)% on Cross-Platform (Android) and USTC-TFC-2016 datasets.
Method

Omt-CNN

Omt-CNN (MV)
CNN-iCarl+

CNN-iCarl+ (MV)
EBSNN (IL)

ET-Bert (IL)
MISS-CNN

MISS-TF

Dataset
Phase
avg.ACC
avg.F1

Cross-Platform (Android)
UB
N=1
84.63± 0.33
80.59± 0.44
80.49± 0.34
74.77± 0.52

N=10
79.08± 0.53
72.29± 0.59

N=25
74.29± 0.35
70.08± 0.34

USTC-TFC-2016
UB
N=1
86.02± 0.46
79.20± 0.38
86.48± 0.38
78.73± 0.39

N=5
76.17± 0.46
77.53± 0.42

avg.ACC
avg.F1
avg.ACC
avg.F1

88.19± 0.34
84.12± 0.29
87.59± 0.52
85.24± 0.50

83.56± 0.53
77.49± 0.59
83.68± 0.49
84.12± 0.58

82.21± 0.30
75.94± 0.34
81.91± 0.50
81.35± 0.56

77.60± 0.49
73.96± 0.51
79.08± 0.60
78.51± 0.70

89.05± 0.52
89.55± 0.59
89.83± 0.50
88.06± 0.61

81.76± 0.51
81.30± 0.42
85.08± 0.55
83.86± 0.47

79.84± 0.43
80.62± 0.49
84.38± 0.44
83.59± 0.42

avg.ACC
avg.F1
avg.ACC
avg.F1

88.86± 0.36
83.83± 0.33
90.32± 0.52
85.79± 0.46

84.41± 0.36
82.72± 0.34
85.17± 0.68
81.98± 0.61

82.61± 0.47
80.08± 0.51
84.28± 0.34
81.84± 0.41

78.28± 0.36
77.14± 0.38
81.45± 0.37
78.64± 0.32

91.70± 0.45
89.98± 0.53
81.41± 0.35
78.93± 0.41

86.04± 0.58
85.87± 0.63
72.36± 0.74
69.97± 0.86

85.84± 0.55
84.65± 0.45
76.46± 0.36
71.31± 0.32

avg.ACC
avg.F1
avg.ACC
avg.F1

98.74± 0.19
94.28± 0.18
90.20± 0.25
88.89± 0.23

94.99± 0.30
92.56± 0.27
88.76± 0.22
87.55± 0.20

94.93± 0.25
92.32± 0.29
85.75± 0.33
83.23± 0.31

94.06± 0.24
91.38± 0.22
80.37± 0.21
77.00± 0.19

99.51± 0.22
99.57± 0.20
99.03± 0.38
98.81± 0.36

93.96± 0.37
93.34± 0.31
97.57± 0.33
97.76± 0.35

95.71± 0.06
95.55± 0.05
97.54± 0.25
97.70± 0.28

avg.ACC
avg.F1

97.77 ± 0.30
97.02 ± 0.33

97.12 ± 0.20
95.88 ± 0.18

97.11 ± 0.24
95.28 ± 0.21

96.52 ± 0.22
95.23 ± 0.25

99.43 ± 0.33
99.15 ± 0.36

97.54 ± 0.28
98.38 ± 0.29

96.38 ± 0.24
96.97 ± 0.22

Fig. 8. Phase-wise Accuracies (%) and F1-score (%) of Cross-Platform (iOS) and PURE-TLS datasets. (a) Accuracies andF1-score of Cross-Platform (iOS). In the 0th
phase, the old model is trained on 90 applications; the remaining applications are given evenly in the subsequent phases. (b) Accuracies and F1-score of PURE-TLS.
In the 0th phase, the initial model is trained on 50 applications; the remaining applications are given evenly in the subsequent phases.

5.4. Incremental evaluations of ETC
We comprehensively explore the incremental eﬀects of representative exemplar selection and design rich incremental experiments to
explore the eﬀects of diﬀerent incremental strategies, focusing on the
Transformer-based MISS-TF (hereinafter referred to as, MISS) and
PURE-TLS dataset.
5.4.1. Comparison with diﬀerent exemplar selections
To verify the superiority of our proposed representative exemplar
selection, we pick the iCarl’s exemplar selection (iCarl-ES) and Random
exemplar selection (Random-ES) as comparison schemes to replace the
exemplar selection MISS-ES of MISS, and gradually reduce  % from
[10%, 5%, 2%], to explore diﬀerent exemplar selections with diﬀerent
exemplar retention rates. We can see two apparent trends as shown in
Fig. 9 and Tables 8-9,

Fig. 9. Schematic of avg.ACC and avg.F1 of diﬀerent exemplar selections. 30
implies the starting point for evaluation metric values. Each part from left to
right is MISS-ES, iCarl-ES, and Random-ES, and the white part is the re-trained
Lower Bound (LB) classiﬁcation eﬀect.

 %=2%, as shown in Table 8. Under extreme LB conditions, MISSES signiﬁcantly improves avg.F1 scores over iCarl and Random
exemplar selection, underscoring the eﬀectiveness of our exemplar
selection strategy.

• MISS-ES can select more representative exemplars, shows signiﬁcant superiority over iCarl-ES and Random-ES, and keep the better
classiﬁcation eﬀect on LB. The increase is most pronounced when
11

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

Fig. 10. The accuracy drops after each incremental phase under the diﬀerent initial application amounts. (a) The accuracy drops in all applications when new
applications are added. (b) The accuracy drops in initial applications when new applications are added.

Table 8
Compared with iCarl and Random exemplar selections on the
avg.F1 when  %=2%. ↓ means the decline compared with MISS.
Method
MISS-ES
iCarl-ES
Random-ES

N=1
89.51
↓2.02(87.49)
↓5.65(83.86)

MISS-ES-LB
iCarl-ES-LB
Random-ES-LB

75.96

35.92

34.14

↓2.75(73.21)
↓6.94(69.02)

↓3.80(32.12)
↓3.59(32.33)

↓0.12(34.02)
↓2.71(31.42)

N=10
91.81
↓5.02(86.79)
↓10.73(81.08)

Table 9
Runtime (h) and
 %=[10%,5%,2%].

N=25
90.68
↓4.45(86.23)
↓10.11(80.57)

Phase
N=1

N=10

N=25

• A higher exemplar retention rate  % improves the evolution effect but increases resource consumption. Total.RT represents the
cumulative runtime across all (𝑁+1) phases, avg.RT denotes the
average runtime per phase, Storage refers to the actual traﬃc storage resources utilized in the ﬁnal (𝑁+1)th phase, as Table 9 shows.
This also aligns with our cognition: a higher exemplar retention
rate translates to increased runtime and storage resources.

Storage

(GB)

of

N+1

phases

under

Metrics

UB

 %=10%

 %=5%

 %=2%

total.RT (h)
avg.RT (h)
Storage (GB)

3.23
1.62
41.91

2.41
1.21
21.65

2.27
1.14
20.29

2.07
1.04
19.43

total.RT (h)
avg.RT (h)
Storage (GB)

15.37
1.40
41.91

3.72
0.34
6.65

3.23
0.29
4.47

2.63
0.24
3.05

total.RT (h)
avg.RT (h)
Storage (GB)

38.66
1.49
41.91

5.53
0.21
5.72

4.47
0.17
3.43

3.15
0.12
1.82

Takeaway. Reasonable exemplar selection can improve the evolution effect.  % is the art of balancing evolution performance with computational
resource consumption. To pursue a faster evolution is achieved by the reasonable exemplar selection according to a low  %, which could not be neglected
to ensure that the absolute amount of exemplars should remain in an appropriate interval.
Fig. 11. Phase-wise metrics on IL strategies of homogeneous applications. (a)
The metrics of MISS. (b) The metrics of ET-Bert (IL).

5.4.2. Comparison of diﬀerent initial application amounts
We now discuss how performance is aﬀected by diﬀerent initial
application amounts in the 0th phase. In Fig. 10(a), we compare the
performance of the initial model trained on the amount from [0, 25,
50, 75], and execute up to 5 incremental phases, each adding 5 new applications. To complement the analysis, we give the classiﬁcation ability
of the initial applications in the 0th phase (when the amount is 0, the
1th phase is analyzed) after new applications are added, as shown in
Fig. 10(b). We can observe an overlapping trend: under the incremental
application amount is ﬁxed, the fewer initial applications, the more signiﬁcantly decreases the accuracy of all applications and old applications
after each incremental phase, especially when the initial applications
are less than half the total applications. Meanwhile, the accuracy of
initial applications can be severely detrimental (↓13.64%) at the ﬁnal
incremental phase when too few initial applications are available.

• Randomly select 40 applications in 4 phases.
• Select 10 applications from each Alibaba, Baidu, ByteDance, and
Tencent family.
• Select 10 applications from each Shopping, Social, Reading, and
Video type.
We make a comparison with ET-Bert (IL) for further analysis, and the
results are shown in Fig. 11. The IL Strategies of homogeneous applications reduce the gain of the IL framework, but MISS possesses certain
robustness, especially for the same family. Fig. 12 visualizes the embedding feature spaces of MISS and ET-Bert (IL) using t-SNE (Van der
Maaten and Hinton, 2008), which intuitively demonstrates that the embeddings of ﬂows within the same family generated by MISS are more
compact and separable (especially inside the circle box). We argue that
MISS deals with the diﬃculty of classifying homogenous applications
from the same families and types by considering features from diﬀerent views. For homogeneity problems speciﬁc to ETC, the multi-view
sequence features perform better. We provide the ablation experiments
for diﬀerent view sequence features to enable a better demonstration,
as shown in Fig. 13. Diﬀerent view sequence features perform diﬀerently in incremental phases on the homogenous applications, e.g., the
homogenous types are better in the content type view than other views.

Takeaway. Fewer initial applications in the 0th phase, the more negative
impact of incremental phases on accuracy. For an evolving ETC model, a
full training should be performed after several incremental phases, resetting
the 0th phase.
5.4.3. IL strategies for homogeneous applications
We observe homogeneity in the PURE-TLS dataset: the applications
from the same families and types, e.g., Taobao and Alipay are both from
the Alibaba family, Facebook and Instagram are both social applications. We set the initial application amount as 50, with  %=10%, and
set up three sets of experiments:
12

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

Fig. 12. Visualizations of MISS and ET-Bert (IL) using t-SNE in the ﬁnal phase respectively. (a) Visualizations of MISS with homogenous family. (b) Visualizations of
ET-Bert (IL) with homogenous family. (c) Visualizations of MISS with homogenous type. (d) Visualizations of ET-Bert (IL) with homogenous type.

Fig. 13. Phase-wise metrics on homogeneous applications for diﬀerent view sequence features. (a) The payload byte view. (b) The packet length view. (c) The TLS
content type view. (d) The arrival time view.

• Task#5: The ISCX-17 dataset (Draper-Gil et al., 2016) is selected
for the VPN-encrypted Traﬃc Classiﬁcation task. It encompasses
seven traﬃc types related to both VPN and non-VPN communications, originating from various applications. This results in 17
distinct classes, and we use 8 as the initial number of classes for
our analysis.

Takeaway. Once encountering a severe group of homogeneous applications
in IL, it will reduce the performance after evolution. Therefore, we suggest
that the variability of the added applications should be guaranteed, which
could be artiﬁcially divided with prior information.
5.4.4. Comparison of CV IL framework migration
To delve deeper into the performance of MISS in the context of
encrypted traﬃc tasks, we embark on an exploration of migrating IL
frameworks from the CV ﬁeld, under the guidance of (Bovenzi et al.,
2023, 2021), to carry out further comparison.

On Task#1, MISS achieves an avg.ACC of 97.18% and an avg.F1
of 97.03%, outstripping iCarl-M2 by margins of 1.76% and 3.59%, and
DER-M2 by 0.92% and 1.71%, respectively. On Task#2, for the CrossPlatform (Android), MISS surpasses iCarl-M2 by 2.76% in avg.ACC and
5.46% in avg.F1, and outpaces DER-M2 by 1.55% and 3.53%, respectively. For the MIRAGE-2019 dataset, MISS exceeds iCarl-M2 by 4.78%
in avg.ACC and 6.17% in avg.F1, and outclasses DER-M2 by 2.10% and
3.29% in the same metrics. On Task#3, the robustness of MISS is evident, overshadowing iCarl-M2 by a signiﬁcant 5.09% in avg.ACC and
7.09% in avg.F1. Task#4 and Task#5 further highlight MISS’s versatility. In the PURE-TLS dataset, MISS leads iCarl-M2 by 1.42% in avg.ACC
and 2.10% in avg.F1, and surpasses DER-M2 by 0.97% and 1.64%. Even
within the ISCX-17 dataset, MISS maintains its superiority, outperforming iCarl-M2 and DER-M2 by 3.02% and 0.80% in avg.ACC, respectively.

• iCarl: As delineated, iCarl (Rebuﬃ et al., 2017) amalgamates a speciﬁc loss. It introduced the exemplar selection, underscoring the
eﬃcacy of the nearest-mean-of-exemplars classiﬁcation in IL scenarios.
• DER: Dynamical Expandable Representations (DER) (Yan et al.,
2021) appends a fresh feature extractor at each phase, updating
it while keeping previous ones. For the 𝑖th phase, outputs from all
𝑖 + 1 extractors are combined for classiﬁcation.
We retain the feature extraction capabilities of the 0th phase model
and migrate iCarl and DER IL frameworks, respectively, to form the
iCarl-M2 and DER-M2 variants. These variants are benchmarked against
MISS on 5 traﬃc tasks, with a focus on 𝑁 =1 incremental phase, as
shown in Table 10:

Takeaway. MISS, tailored for encrypted traﬃc, consistently outshines CVfocused IL frameworks. Its robust performance across varied datasets underscores its potential as a benchmark in encrypted traﬃc tasks.

• Task#1: ETC of iOS Applications using the Cross-Platform (iOS)
dataset for this investigation.
• Task#2: For ETC on Android Applications, both the Cross-Platform
(Android) and MIRAGE-2019 (Aceto et al., 2019a) datasets are considered. MIRAGE-2019 analyzes traﬃc from 40 applications on 3
Android devices, with its public subset covering 20 applications on
2 devices. For the sake of brevity, we focus on traﬃc from the Xiaomi Mi5 using 10 as the initial number of classes.
• Task#3: For ETC on Malicious Applications, we use the USTC-TFC2016 dataset.
• Task#4: We utilize the PURE-TLS dataset for Pure-encrypted Trafﬁc Classiﬁcation task.

5.4.5. IL strategies for unknown applications
We envision the scenario in which the initial model discovers unknown applications rather than acquiring manually labeled applications
for evolution, discovering unknown, clustering unknown, and using
clusters as new applications for evolution. The IL Problem of ETC is
th
transformed into feeding the 𝑖th phase test set 0∶𝑖
𝑡𝑒𝑠𝑡 and the (𝑖 + 1)
𝑖+1
th
𝑖
phase 
to the 𝑖 phase model  during the testing process, discovering the samples of 𝑖+1 and clustering them. It is not necessary to
evolve on all samples of 𝑖+1 , and the correctly obtained from the discovering and clustering process are enough (Leo and Kalita, 2021). We
use OpenMax instead of SoftMax to equip MISS with the ability to reject
unknown applications. OpenMax is training independently as described
13

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

Table 10
Comparison of avg.ACC and avg.F1 scores for iCarl-M2 , DER-M2 , and MISS across 5 traﬃc classiﬁcation tasks.
Method

N=1
Metrics
avg.ACC
avg.F1

Task#1
Cross-Platform (iOS)
98.12
97.71

Task#2
Cross-Platform (Android)
97.77
97.02

MIRAGE-2019
82.10
78.94

Task#3
USTC-TFC-2016
99.43
99.15

Task#4
PURE-TLS
98.24
98.34

Task#5
ISCX-17
88.35
84.52

iCarl-M2

avg.ACC
avg.F1

95.42
93.44

94.42
90.42

74.86
71.65

92.45
91.29

95.53
94.96

82.46
80.29

DER-M2

avg.ACC
F1

96.26
95.32

95.57
92.35

77.54
74.53

96.85
95.28

95.87
95.42

84.68
82.01

MISS

avg.ACC
avg.F1

97.18
97.03

97.12
95.88

79.64
77.82

97.54
98.38

96.84
97.06

85.48
81.81

UB

after several evolution phases to reset the 0th phase. Finally, the problem of homogeneous applications is not negligible. We suggest that the
variability of the added applications should be guaranteed, which could
be artiﬁcially divided with prior information.

Table 11
The average metrics for the diﬀerent counts of phase. The values
in parentheses correspond to the results from Table 6.
Phases

avg.ACC𝑜𝑠

avg.ACC↓

avg.F1𝑜𝑠

N=1

85.76

↓11.08(96.84)

84.88

avg.F1↓

↓12.18(97.06)

N=10

88.86

↓8.43(97.29)

87.43

↓10.03(97.46)

N=25

91.29

↓5.11(96.40)

92.14

↓4.47(96.61)

6.2. Limitations

6. Discussion

Experiments show that our MISS framework has excellent performance, but there are some limitations.
Firstly, from the dataset perspective, the PURE-TLS dataset we constructed contains encrypted traﬃc data from 100 applications. However, some applications have less data, and the dataset as a whole
exhibits an unbalanced phenomenon. This is because many applications
are not pure TLS traﬃc at runtime, and we removed all non-TLS traﬃc
during preprocessing. This treatment during data collection may result
in the loss of some important information, particularly for applications
that generate a substantial amount of non-TLS traﬃc during operation.
Therefore, although this treatment helps us focus on analyzing TLS trafﬁc, we recognize that it may limit the generalizability of our dataset.
In the future, we will continuously update the PURE-TLS dataset to increase the number of application types and the scale of traﬃc ﬂows.
Secondly, regarding our experiments, selecting a maximum of 500
(or 1000) ﬂows might diminish the variability among the classes. In our
future endeavors, we aim to adopt proportional undersampling to preserve class diﬀerences and more accurately capture their inherent variability. Further, classifying applications from the same cloud provider,
given their overlapping APIs and services, needs deeper exploration.
Such overlaps challenge ETC models, leading to reduced accuracy and
F1-score for MISS in these contexts.
Finally, MISS is a lightweight ETC model with excellent performance
in multiple ETC tasks, but there is still potential for enhancement. For
exemplar, pre-training technology has achieved promising results in
many research ﬁelds, which can help MISS further improve the processing capability for ETC tasks, especially the detection capability for
unknown applications, and to address the performance decreasing on
non-exactly labeled increments.

6.1. Implication

7. Conclusion

Our observations in this paper can provide implications for exploration. We ﬁnd that an ETC model with a well-designed IL framework could keep evolving well when new applications emerge, signiﬁcantly reducing resource consumption while maintaining excellent
performance. Firstly, in our observations, a high Upper Bound of the
initial model is crucial for its evolution. We suggest building an excellent initial model as much as possible at the feature design level or
model structure level. Secondly, the exemplar retention rate  % is the
art of balancing evolution performance with computational resource
consumption. A lower  % can be appropriately selected to reduce the
evolution runtime signiﬁcantly. Thirdly, we ﬁnd that the fewer initial
applications in the 0th phase, the higher the loss of accuracy due to
evolution. We suggest a full training of all samples should be performed

In this paper, we proposed an IL framework named MISS allowing the ETC models to keep evolving when new applications emerge.
MISS is more applicable to sequence features of ETC than the existing IL frameworks and migration work. We conclude a comprehensive
experimental analysis and discussion to evaluate the feasibility and
robustness nature of MISS, which improve 11.37%↑ and 1.58%↑ compared to the existing IL methods of ETC and the SOTA ETC models
using classic IL framework. Furthermore, we comprehensively perform
incremental experiments to evaluate the evolution ability of MISS, by
comparison with diﬀerent exemplar selections, diﬀerent initial application amounts, homogeneous applications increments, and unknown
applications increments, and obtain a series of valuable ﬁndings. We
believe our research work can positively contribute to the vision of onin (Bendale and Boult, 2016), which uses a conﬁdence value to identify open set data. OpenMax revises SoftMax activation vectors adding
a special “synthetic” unknown node (by using weighting induced by
Weibull). We follow existing work (Lyu et al., 2023; Oveis et al., 2022)
and set the Weibull distribution set to 20. The clustering algorithm is
Modiﬁed PCKMeans, which uses 3-tuples (IP address, port, TLS certiﬁcate) as pairwise constraints to guide the clustering, and we respect
the parameter settings in (Zhang et al., 2019). Following (Bendale and
Boult, 2015; Ge et al., 2017), we use the Open-Set metrics to measure
the evaluation performance (ACC𝑜𝑠 , F1𝑜𝑠 ), e.g., ACC𝑜𝑠 is deﬁned as,
0∶𝑖

𝑖+1


𝑡𝑒𝑠𝑡
]
]
1 ∑ [ 𝑖( )
1 ∑ [ 𝑖( )
𝐴𝐶𝐶.𝑜𝑠 =
 𝐱 𝑗 = 𝑦𝑗 +
 𝐱𝐣 = UNK (10)
0∶𝑖
𝑖+1

𝑡𝑒𝑠𝑡 𝑗=1
𝑗=1

Results are shown in Table 11. Compared to the manually labeled
in Table 6, the classiﬁcation eﬀect is severely reduced when the number of unknown applications is similar to the initial applications (when
𝑁 =1). It also gives relatively better results when the added applications in each phase are much smaller than the initial applications (when
𝑁 =25) because this limits the error in the non-incremental part.
Takeaway. The non-incremental component mainly inﬂuences the evolution
eﬀect of unknown applications, which is an inevitable negative eﬀect. Errors
in the discovering and clustering processes increase and propagate when more
unknown applications are added simultaneously in one phase.

14

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.

line evolution in traﬃc classiﬁcation models and automation in traﬃc
analysis systems.

van Ede, T., Bortolameotti, R., Continella, A., Ren, J., Dubois, D.J., Lindorfer, M.,
Choﬀnes, D., van Steen, M., Peter, A., 2020. Flowprint: semi-supervised mobile-app
ﬁngerprinting on encrypted network traﬃc. In: Network and Distributed System Security Symposium (NDSS).
Finsterbusch, M., Richter, C., Rocha, E., Muller, J.A., Hanssgen, K., 2013. A survey
of payload-based traﬃc classiﬁcation approaches. IEEE Commun. Surv. Tutor. 16,
1135–1156.
French, R.M., 1999. Catastrophic forgetting in connectionist networks. Trends Cogn.
Sci. 3, 128–135.
Fu, Y., Xiong, H., Lu, X., Yang, J., Chen, C., 2016. Service usage classiﬁcation with encrypted internet traﬃc in mobile messaging apps. IEEE Trans. Mob. Comput. 15,
2851–2864.
Ge, Z., Demyanov, S., Chen, Z., Garnavi, R., 2017. Generative openmax for multi-class
open set classiﬁcation. ArXiv preprint arXiv:1707.07418.
Goodfellow, I., Pouget-Abadie, J., Mirza, M., Xu, B., Warde-Farley, D., Ozair, S., Courville,
A., Bengio, Y., 2014. Generative adversarial nets. Adv. Neural Inf. Process. Syst. 27.

CRediT authorship contribution statement
Xiang Li: Conceptualization, Data curation, Formal analysis, Methodology, Software, Validation, Visualization, Writing – original draft,
Writing – review & editing. Jiang Xie: Conceptualization, Formal analysis, Investigation, Methodology, Resources, Writing – review & editing.
Qige Song: Conceptualization, Investigation, Methodology, Writing –
review & editing. Yafei Sang: Data curation, Project administration, Supervision, Writing – original draft. Yongzheng Zhang: Data curation,
Project administration, Resources, Supervision. Shuhao Li: Funding acquisition, Resources, Supervision. Tianning Zang: Conceptualization,
Methodology, Writing – review & editing.

Google, 2022. Https encryption on the web. https://transparencyreport.google.com/
https/overview?hl=en.
Group, I.S.R., 2020. 2020 annual report. https://letsencrypt.org/.
Hendrycks, D., Gimpel, K., 2016. Gaussian error linear units (gelus). ArXiv preprint arXiv:
1606.08415.
Hinton, G., Vinyals, O., Dean, J., 2015. Distilling the knowledge in a neural network.
ArXiv preprint arXiv:1503.02531.
Hou, S., Pan, X., Loy, C.C., Wang, Z., Lin, D., 2019. Learning a uniﬁed classiﬁer incrementally via rebalancing. In: Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition, pp. 831–839.
Kang, M., Park, J., Han, B., 2022. Class-incremental learning by knowledge distillation
with adaptive feature consolidation. ArXiv e-prints arXiv:2204.00895.
Kirkpatrick, J., Pascanu, R., Rabinowitz, N., Veness, J., Desjardins, G., Rusu, A.A., Milan,
K., Quan, J., Ramalho, T., Grabska-Barwinska, A., et al., 2017. Overcoming catastrophic forgetting in neural networks. Proc. Natl. Acad. Sci. 114, 3521–3526.

Declaration of competing interest
The authors declare that they have no known competing ﬁnancial
interests or personal relationships that could have appeared to inﬂuence
the work reported in this paper.
Data availability
Data will be made available on request.
Acknowledgements

Korczynski, M., Duda, A., 2014. Markov chain ﬁngerprinting to classify encrypted traﬃc.
In: Infocom. IEEE.
Lee, I., Roh, H., Lee, W., 2020. Encrypted malware traﬃc detection using incremental
learning. In: IEEE INFOCOM 2020-IEEE Conference on Computer Communications
Workshops (INFOCOM WKSHPS). IEEE, pp. 1348–1349.
Leo, J., Kalita, J., 2021. Incremental deep neural network learning using classiﬁcation
conﬁdence thresholding. IEEE Trans. Neural Netw. Learn. Syst.
Li, J., Xue, D., Wu, W., Wang, J., 2020. Incremental learning for malware classiﬁcation in
small datasets. Secur. Commun. Netw. 2020, 1–12.
Lin, X., Xiong, G., Gou, G., Li, Z., Shi, J., Yu, J., 2022. Et-bert: a contextualized datagram representation with pre-training transformers for encrypted traﬃc classiﬁcation. ArXiv preprint arXiv:2202.06335.
Liu, C., He, L., Xiong, G., Cao, Z., Li, Z., 2019. Fs-net: a ﬂow sequence network for encrypted traﬃc classiﬁcation. In: IEEE INFOCOM 2019-IEEE Conference on Computer
Communications. IEEE, pp. 1171–1179.
Liu, H., Wang, Z., Wang, Y., 2012. Semi-supervised encrypted traﬃc classiﬁcation using
composite features set. J. Netw. 7, 1195.

This work was supported by the National Key Research and Development Program of China (Grant No. 2018YFB0804702), and the National
Natural Science Foundation of China (Grant No. U1736218).
References
Aceto, G., Ciuonzo, D., Montieri, A., Persico, V., Pescapé, A., 2019a. Mirage: mobile-app
traﬃc capture and ground-truth creation. In: 2019 4th International Conference on
Computing, Communications and Security (ICCCS). IEEE, pp. 1–8.
Aceto, G., Ciuonzo, D., Montieri, A., Pescape, A., 2017. Traﬃc classiﬁcation of mobile
apps through multi-classiﬁcation. In: GLOBECOM 2017-2017 IEEE Global Communications Conference. IEEE, pp. 1–6.
Aceto, G., Ciuonzo, D., Montieri, A., Pescapè, A., 2019b. Mimetic: mobile encrypted traﬃc
classiﬁcation using multimodal deep learning. Comput. Netw. 165, 106944.
Bendale, A., Boult, T., 2015. Towards open world recognition. In: Proceedings of the IEEE
Conference on Computer Vision and Pattern Recognition, pp. 1893–1902.
Bendale, A., Boult, T.E., 2016. Towards open set deep networks. In: Proceedings of the
IEEE Conference on Computer Vision and Pattern Recognition, pp. 1563–1572.
Bovenzi, G., Nascita, A., Yang, L., Finamore, A., Aceto, G., Ciuonzo, D., Pescapé, A., Rossi,
D., 2023. Benchmarking class incremental learning in deep learning traﬃc classiﬁcation. IEEE Trans. Netw. Serv. Manag.
Bovenzi, G., Yang, L., Finamore, A., Aceto, G., Ciuonzo, D., Pescape, A., Rossi, D., 2021.
A ﬁrst look at class incremental learning in deep learning mobile traﬃc classiﬁcation.
ArXiv preprint arXiv:2107.04464.
Bujlow, T., Carela-Español, V., Barlet-Ros, P., 2015. Independent comparison of popular
dpi tools for traﬃc classiﬁcation. Comput. Netw. 76, 75–89.
Castro, F.M., Marín-Jiménez, M.J., Guil, N., Schmid, C., Alahari, K., 2018. End-to-end incremental learning. In: Proceedings of the European Conference on Computer Vision
(ECCV), pp. 233–248.
Chang, W.L., Sun, H.M., Wu, W., 2016. An android behavior-based malware detection
method using machine learning. In: 2016 IEEE International Conference on Signal
Processing, Communications and Computing (ICSPCC). IEEE, pp. 1–4.
Chen, Y., 2015. Convolutional neural network for sentence classiﬁcation. Master’s thesis.
University of Waterloo.
Chen, Y., Zang, T., Zhang, Y., Zhou, Y., Ouyang, L., Yang, P., 2021. Incremental learning
for mobile encrypted traﬃc classiﬁcation. In: ICC 2021-IEEE International Conference
on Communications. IEEE, pp. 1–6.
Douillard, A., Cord, M., Ollion, C., Robert, T., Valle, E., 2020. Podnet: pooled outputs
distillation for small-tasks incremental learning. In: Computer Vision–ECCV 2020:
16th European Conference, Proceedings, Part XX 16. Glasgow, UK, August 23–28,
2020. Springer, pp. 86–102.
Draper-Gil, G., Lashkari, A.H., Mamun, M.S.I., Ghorbani, A.A., 2016. Characterization of
encrypted and vpn traﬃc using time-related. In: Proceedings of the 2nd International
Conference on Information Systems Security and Privacy (ICISSP), pp. 407–414.

Liu, J., Fu, Y., Ming, J., Ren, Y., Sun, L., Xiong, H., 2017. Eﬀective and real-time in-app
activity analysis in encrypted internet traﬃc streams. In: Proceedings of the 23rd
ACM SIGKDD International Conference on Knowledge Discovery and Data Mining,
pp. 335–344.
Liu, Y., Schiele, B., Sun, Q., 2021. Adaptive aggregation networks for class-incremental
learning. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 2544–2553.
Liu, Y., Su, Y., Liu, A.A., Schiele, B., Sun, Q., 2020. Mnemonics training: multi-class incremental learning without forgetting. In: Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pp. 12245–12254.
Lotfollahi, M., Jafari Siavoshani, M., Shirali Hossein Zade, R., Saberian, M., 2020. Deep
packet: a novel approach for encrypted traﬃc classiﬁcation using deep learning. Soft
Comput. 24, 1999–2012.
Lyu, Z., Gutierrez, N.B., Beksi, W.J., 2023. Metamax: Improved open-set deep neural networks via Weibull calibration. In: Proceedings of the IEEE/CVF Winter Conference
on Applications of Computer Vision, pp. 439–443.
Van der Maaten, L., Hinton, G., 2008. Visualizing data using t-sne. J. Mach. Learn. Res. 9.
Millar, S., McLaughlin, N., del Rincon, J.M., Miller, P., 2021. Multi-view deep learning
for zero-day android malware detection. J. Inf. Sec. Appl. 58, 102718.
Ostapenko, O., Puscas, M., Klein, T., Jähnichen, P., Nabi, M., 2019. Learning to remember:
a synaptic plasticity driven framework for continual learning. ArXiv preprint arXiv:
1904.03137.
Oveis, A.H., Giusti, E., Ghio, S., Martorella, M., 2022. Open set recognition in sar images
using the openmax approach: challenges and extension to boost the accuracy and
robustness. In: EUSAR 2022; 14th European Conference on Synthetic Aperture Radar,
VDE, pp. 1–4.
Rebuﬃ, S.A., Kolesnikov, A., Sperl, G., Lampert, C.H., 2017. icarl: incremental classiﬁer
and representation learning. In: Proceedings of the IEEE Conference on Computer
Vision and Pattern Recognition, pp. 2001–2010.
15

Computers & Security 137 (2024) 103624

X. Li, J. Xie, Q. Song et al.
Ren, J., Dubois, D., Choﬀnes, D., 2019. An International View of Privacy Risks for Mobile
Apps.
Rescorla, E., Modadugu, N., 2012. Datagram Transport Layer Security Version 1.2.
Rezaei, S., Liu, X., 2019. Deep learning for encrypted traﬃc classiﬁcation: an overview.
IEEE Commun. Mag. 57, 76–81.
Rusu, A.A., Rabinowitz, N.C., Desjardins, G., Soyer, H., Kirkpatrick, J., Kavukcuoglu, K.,
Pascanu, R., Hadsell, R., 2016. Progressive neural networks. ArXiv preprint arXiv:
1606.04671.
Shen, M., Wei, M., Zhu, L., Wang, M., 2017. Classiﬁcation of encrypted traﬃc with
second-order Markov chains and application attribute bigrams. IEEE Trans. Inf.
Forensics Secur. 12, 1830–1843.
Sherry, J., Lan, C., Popa, R.A., Ratnasamy, S.P., 2015. Blindbox: deep packet inspection
over encrypted traﬃc. In: Computer Communication Review: A Quarterly Publication
of the Special Interest Group on Data Communication.
Sun, G., Li, S., Chen, T., Su, Y., Lang, F., 2017. Traﬃc classiﬁcation based on incremental learning method. In: International Conference on Advanced Hybrid Information
Processing. Springer, pp. 341–348.
Sun, Q., Liu, Y., Chua, T.S., Schiele, B., 2019. Meta-transfer learning for few-shot learning. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pp. 403–412.
Taylor, V.F., Spolaor, R., Conti, M., Martinovic, I., 2017. Robust smartphone app identiﬁcation via encrypted network traﬃc analysis. IEEE Trans. Inf. Forensics Secur. 13,
63–78.
Tolstikhin, I.O., Houlsby, N., Kolesnikov, A., Beyer, L., Zhai, X., Unterthiner, T., Yung, J.,
Steiner, A., Keysers, D., Uszkoreit, J., et al., 2021. Mlp-mixer: an all-mlp architecture
for vision. Adv. Neural Inf. Process. Syst. 34.
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Ł.,
Polosukhin, I., 2017. Attention is all you need. Adv. Neural Inf. Process. Syst. 30.
Velan, P., Čermák, M., Čeleda, P., Drašar, M., 2015. A survey of methods for encrypted
traﬃc classiﬁcation and analysis. Int. J. Netw. Manag. 25, 355–374.
Wang, P., Chen, X., Ye, F., Sun, Z., 2019. A survey of techniques for mobile service encrypted traﬃc classiﬁcation using deep learning. IEEE Access 7, 54024–54033.
Wang, W., Zhu, M., Wang, J., Zeng, X., Yang, Z., 2017a. End-to-end encrypted traﬃc
classiﬁcation with one-dimensional convolution neural networks. In: 2017 IEEE International Conference on Intelligence and Security Informatics (ISI). IEEE, pp. 43–48.
Wang, W., Zhu, M., Zeng, X., Ye, X., Sheng, Y., 2017b. Malware traﬃc classiﬁcation using convolutional neural network for representation learning. In: 2017 International
Conference on Information Networking (ICOIN). IEEE, pp. 712–717.
Wang, X., Chen, S., Su, J., 2020. Automatic mobile app identiﬁcation from encrypted
traﬃc with hybrid neural networks. IEEE Access 8, 182065–182077.
Wang, Y., Xiang, Y., Zhang, J., Zhou, W., Wei, G., Yang, L.T., 2013. Internet traﬃc classiﬁcation using constrained clustering. IEEE Trans. Parallel Distrib. Syst. 25, 2932–2943.
Welling, M., 2009. Herding dynamical weights to learn. In: Proceedings of the 26th Annual International Conference on Machine Learning, pp. 1121–1128.
Wu, Z., Dong, Y.n., Qiu, X., Jin, J., 2022. Online multimedia traﬃc classiﬁcation from the
qos perspective using deep learning. Comput. Netw. 108716.
Xiao, X., Xiao, W., Li, R., Luo, X., Zheng, H.T., Xia, S.T., 2021. Ebsnn: extended byte
segment neural network for network traﬃc classiﬁcation. IEEE Trans. Dependable
Secure Comput.
Xu, J., Li, W., Liu, X., Zhang, D., Liu, J., Han, J., 2020a. Deep embedded complementary
and interactive information for multi-view classiﬁcation. In: Proceedings of the AAAI
Conference on Artiﬁcial Intelligence, pp. 6494–6501.
Xu, S.J., Geng, G.G., Jin, X.B., Liu, D.J., Weng, J., 2022. Seeing traﬃc paths: encrypted
traﬃc classiﬁcation with path signature features. IEEE Trans. Inf. Forensics Secur. 17,
2166–2181.
Xu, Y., Zhang, Y., Guo, W., Guo, H., Tang, R., Coates, M., 2020b. Graphsail: graph
structure aware incremental learning for recommender systems. In: Proceedings of
the 29th ACM International Conference on Information & Knowledge Management,
pp. 2861–2868.
Yan, S., Xie, J., He, X., 2021. Der: dynamically expandable representation for class incremental learning. In: Proceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, pp. 3014–3023.
Zbontar, J., Jing, L., Misra, I., LeCun, Y., Deny, S., 2021. Barlow twins: self-supervised
learning via redundancy reduction. In: International Conference on Machine Learning. PMLR, pp. 12310–12320.

Zhang, C., Song, N., Lin, G., Zheng, Y., Pan, P., Xu, Y., 2021. Few-shot incremental learning with continually evolved classiﬁers. In: Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pp. 12455–12464.
Zhang, Y., Zhao, S., Sang, Y., 2019. Towards unknown traﬃc identiﬁcation using deep
auto-encoder and constrained clustering. In: International Conference on Computational Science. Springer, pp. 309–322.
Zhao, J., Jing, X., Yan, Z., Pedrycz, W., 2021. Network traﬃc classiﬁcation for data fusion:
a survey. Inf. Fusion 72, 22–47.
Zheng, W., Gou, C., Yan, L., Mo, S., 2020. Learning to classify: a ﬂow-based relation
network for encrypted traﬃc classiﬁcation. In: Proceedings of the Web Conference
2020, pp. 13–22.
Zhu, K., Cao, Y., Zhai, W., Cheng, J., Zha, Z.J., 2021. Self-promoted prototype reﬁnement
for few-shot class-incremental learning. In: Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pp. 6801–6810.
Zhu, M.y., Chen, Z., Chen, K.f., Lv, N., Zhong, Y., 2022. Attention-based federated incremental learning for traﬃc classiﬁcation in the internet of things. Comput. Commun. 185, 168–175.

Xiang Li received the B.Eng. degree from Northeast Agricultural University, China, in
2019. He is currently pursuing a Ph.D. degree with the School of Cyber Security, University of Chinese Academy of Sciences, China, and the Institute of Information Engineering,
Chinese Academy of Sciences, China. His research interests include mobile security and
traﬃc analysis.
Jiang Xie received the B.Eng. degree from Nankai University, China, in 2018. He is
currently a graduate student studying for Ph.D. in the Institute of Information Engineering, Chinese Academy of Sciences, China. His research interests include network security
and artiﬁcial intelligence.
Qige Song received the B.Eng. from Beijing Jiaotong University, China, in 2017, and
the M.Eng. in the Institute of Information Engineering, Chinese Academy of Sciences,
China, in 2020. She is currently pursuing the Ph.D. degree with the Institute of Information Engineering, Chinese Academy of Science, China. Her current research interests
include IoT security and artiﬁcial intelligence.
Yafei Sang received the B.Eng. degree from Shanxi University, China, in 2013, and
the Ph.D. degree from the Institute of Information Engineering, Chinese Academy of
Sciences, China, in 2018. He is currently an Associate Professor with the Institute of Information Engineering, Chinese Academy of Sciences, China. His research interests include
encrypted traﬃc measurement and analysis, threat detection, application identiﬁcation,
and ﬁngerprint extraction.
Yongzheng Zhang received the B.S. and Ph.D. degrees from the Harbin Institute of
Technology, China, in 2001 and 2006, respectively. He was a professor and doctoral supervisor at the Institute of Information Engineering, Chinese Academy of Sciences, and
now works in the China Assets Cybersecurity Technology CO., Ltd., China. His research
interests include network security, particularly cyberspace security situational awareness.
He was honored with the First Prize of the Chinese National Award for Science and Technology Progress in 2011.
Shuhao Li received the B.Eng. and M.Eng. degrees from the Harbin Institute of Technology, China, in 2006 and 2008, respectively, and the Ph.D. degree from the Institute of
Computing Technology, Chinese Academy of Sciences, China, in 2012. He is a Professor
and a Ph.D. Supervisor with the School of Cyber Security, University of Chinese Academy
of Sciences, China, and the Institute of Information Engineering, Chinese Academy of Sciences, China. His research interests include network and information security, particularly
mobile malware attacks and defense.
Tianning Zang received the Master and Ph.D. degrees in computer science from the
Harbin Engineering University, China, in 2007 and 2011, respectively. He is currently a
senior engineer and Ph.D. supervisor at the Institute of Information Engineering, Chinese
Academy of Sciences, China. His research interests include network security, particularly
cyberspace security situational awareness.

16
PAPER_TEXT
