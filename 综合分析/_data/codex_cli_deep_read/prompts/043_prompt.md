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
# [043] FS-Net: A Flow Sequence Network For Encrypted Traffic Classification
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
编号：043
题名：FS-Net: A Flow Sequence Network For Encrypted Traffic Classification
年份：2019
DOI：10.1109/infocom.2019.8737507
来源：IEEE INFOCOM 2019 - IEEE Conference on Computer Communications
PDF：paper/10.1109_infocom.2019.8737507.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 15
已有代码状态：已下载；Akrusher/Fs-net -> source\Fs-net; WSPTTH/FS-Net -> source\WSPTTH_FS-Net

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\043.txt
- 原始字符数：51563
- 本次发送字符数：51563
- 是否截断：False

代码包：
- 仓库：Akrusher/Fs-net
  - URL：https://github.com/Akrusher/Fs-net
  - 状态：downloaded
  - 本地目录：source\Fs-net
  - 顶层结构：20191118.log、NIMS.arff、NIMS_test.arff、NIMS_train.arff、README.md、data/、dataset_pcap_length.py、graph.png、model.py、model_test.py、split_train_test.py、tensorboard.png、test.py、test_pcap_length.txt、traffic_dataset.py、train.py、train_pcap_length.txt
  - 主要语言：Python:7
  - README 标题：Fs-net、This is an implementation about FS-net、Fs-net、This is an implementation about FS-net、Fs-net、This is an implementation about FS-net
  - README 运行线索：
  - 关键文件：{"数据处理入口": ["dataset_pcap_length.py"], "模型定义": ["model.py", "model_test.py"], "训练入口": ["train.py"], "评估/测试入口": ["test.py"]}
  - 数据集线索：tor
- 仓库：WSPTTH/FS-Net
  - URL：https://github.com/WSPTTH/FS-Net
  - 状态：downloaded
  - 本地目录：source\WSPTTH_FS-Net
  - 顶层结构：README.md、dataset.py、eval.py、main.py、model.py、preprocess.py、requirement.txt、train.py
  - 主要语言：Python:6
  - README 标题：FS-Net、Longtao He and、Gang Xiong and、Zigang Cao and、Requirement、Dataset Format、How to use、Step 1. Pre-Process The Dataset、Step 2: Train The Model、Step 3: Evaluation.
  - README 运行线索：python >= 3.4；bash python main.py --mode=prepro；bash python main.py --mode=train；bash python main.py --mode=test --test_json=xxxxxx --test_model_dir=yyyyy；python >= 3.4；bash python main.py --mode=prepro；bash python main.py --mode=train；bash python main.py --mode=test --test_json=xxxxxx --test_model_dir=yyyyy
  - 关键文件：{"推理/演示入口": ["main.py"], "数据处理入口": ["dataset.py", "preprocess.py"], "模型定义": ["model.py"], "训练入口": ["train.py"], "评估/测试入口": ["eval.py"]}
  - 数据集线索：tor

论文正文包开始：
<<<PAPER_TEXT
FS-Net: A Flow Sequence Network For Encrypted
Trafﬁc Classiﬁcation
Chang Liu1,2 , Longtao He3 , Gang Xiong1,2 , Zigang Cao1,2 , Zhen Li1,2
1.Institute of Information Engineering, Chinese Academy of Sciences
2.School of Cyber Security, University of Chinese Academy of Sciences
3.National Computer Network Emergency Response Technical Team/Coordination Center of China
Abstract—With more attention paid to user privacy and
communication security, the volume of encrypted trafﬁc rises
sharply, which brings a huge challenge to traditional rulebased trafﬁc classiﬁcation methods. Combining machine learning algorithms and manual-design features has become the
mainstream methods to solve this problem. However, these
features depend on professional experience heavily, which needs
lots of human effort. And these methods divide the encrypted
trafﬁc classiﬁcation problem into piece-wise sub-problems, which
could not guarantee the optimal solution. In this paper, we
apply the recurrent neural network to the encrypted trafﬁc
classiﬁcation problem and propose the Flow Sequence Network
(FS-Net). The FS-Net is an end-to-end classiﬁcation model
that learns representative features from the raw ﬂows, and
then classiﬁes them in a uniﬁed framework. Moreover, we
adopt a multi-layer encoder-decoder structure which can mine
the potential sequential characteristics of ﬂows deeply, and
import the reconstruction mechanism which can enhance the
effectiveness of features. Our comprehensive experiments on the
real-world dataset covering 18 applications indicate that FS-Net
achieves an excellent performance (99.14% TPR, 0.05% FPR
and 0.9906 FTF) and outperforms the state-of-the-art methods.
Index Terms—Encrypted Trafﬁc Classiﬁcation, Recurrent
Neural Network, Reconstruction Mechanism

I. I NTRODUCTION
Network trafﬁc classiﬁcation is a vital task in the network
management and cyberspace security [1], [2]. In the network
management, the trafﬁc needs to be classiﬁed based on
different priority strategies to guarantee the quality of service
(QoS) of networks. In cyberspace security, the malware trafﬁc
needs to be identiﬁed from benign trafﬁc for the network
anomaly detection. Nowadays, as the extensive use of encryption techniques for protecting user privacy, encrypted trafﬁc
rises sharply and takes a large share of network trafﬁc [3].
However, encrypted trafﬁc classiﬁcation is a huge challenge
to traditional rule-based methods, due to the fact that all the
communication contents are randomized after encryption [4].
Therefore, encrypted trafﬁc classiﬁcation becomes a focus
issue and attracts the widespread attention of industries and
academia [5]–[12].
Combining machine learning algorithms and statistical
characteristics extracted artiﬁcially from raw trafﬁc ﬂows
becomes the mainstream method for encrypted trafﬁc classiﬁcation. The general procedures include feature engineering
and model training [5]–[8], [13]. The feature engineering is to
select effective features for the encrypted trafﬁc classiﬁcation,

such as maximum packet length, average packet length and
byte distribution. This procedure depends on professional experience heavily, and the effectiveness of manually designed
features needs to be further veriﬁed. The model training is
to feed the selected features into a speciﬁc classiﬁcation
model, e.g. the logistic regression classiﬁer. However, the
classiﬁcation models are also needed to be carefully selected
to generate convincing results. Obviously, this kind method
decomposes the encrypted trafﬁc classiﬁcation problem into
two sub-problems, and the result of each sub-problem will
directly affect the ﬁnal classiﬁcation performance. An alternative idea is to design an end-to-end model, i.e., combining the
feature engineering and model training into a uniﬁed model.
This end-to-end model can learn features from the raw input
directly, and the learned features are guided by the real labels
to boost performance. Therefore, it can save human effort for
designing and verifying features.
In this paper, we purpose an end-to-end model named Flow
Sequence Network (FS-Net) for encrypted trafﬁc classiﬁcation. The FS-Net learns representative features from the raw
ﬂow sequences rather than manually designed features. The
major structure of the FS-Net model includes an encoder to
generate the features, a decoder with reconstruction layer
to restore the input sequences and a softmax classiﬁer to
recognize applications. Both the encoder and decoder are the
multi-layer bi-directional recurrent neural networks to handle
the input sequences with different ﬂow lengths. The features
for classiﬁcation are learned automatically from the raw ﬂow
sequences by the encoder and are boosted by the decoder and
reconstruction mechanism. Moreover, the decoder also learns
features to enhance the discrimination of ﬂows. The encoder,
decoder and classiﬁer are jointly trained with the raw ﬂow
sequences and application labels. The ﬂexible architecture
increases the generalization of the FS-Net.
Our contributions can be brieﬂy summarized as follows:
• We purpose an end-to-end FS-Net model for the encrypted trafﬁc classiﬁcation. The FS-Net jointly learns
features from the raw ﬂow sequences and makes classiﬁcation to identify ﬂows, and consists of an encoder, a
decoder, a classiﬁer and a reconstruction layer.
• The reconstruction mechanism is used to boost the feature learning. By keeping reconstructed sequences and
raw ﬂow sequences as similar as possible, the generated
features can contain more discriminative information,

1171
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:29:34 UTC from IEEE Xplore. Restrictions apply.

Port-based method [14] is used to identify the application type with a given port list provided by the Internet
Assigned Numbers Authority (IANA). However, this method
is failed in the situations with port dynamic allocation [15]
and common communication protocol port [16]. Payloadbased method [17] uses the speciﬁc signature strings in the
payload for matching. Keralapura et al. (2009) provided a
self-learning trafﬁc classiﬁer to identify the P2P trafﬁc in
high-speed networks with application payload signatures [18],
while Roughan et al. (2004) used statistical signatures to
classify P2P application trafﬁc [19]. However, both port-based
and payload-based methods lose their efﬁciency in encrypted
trafﬁc classiﬁcation, because it is impossible to get signatures
from payloads after encryption.

classiﬁcation [1]. However, these methods are mainly based
on the rich experiences, professional knowledge and lots of
human effort. An alternative way is to learn representative
features from the raw ﬂow data directly.
2) Sequential Features: Sequential features are learned
from the raw ﬂow sequences. The mainstream methods learn
the generation probabilities of ﬂows which are determined by
each packet of ﬂows. Korczyński et al. (2014) ﬁrst proposed to
represent the trafﬁc ﬂow sequence by Markov transformation
matrix [22]. They used message type sequences of encrypted
trafﬁc to build ﬁrst-order Markov model with the maximum
generation probability to classify encrypted trafﬁc. Based on
this method, Shen et al. clustered the certiﬁcate length and the
ﬁrst packet length to improve the classiﬁcation performances
under second-order Markov model [6], [23]. Chang et al.
(2017) integrated both message type sequences and length
block sequences to build Markov models, and all the generation probabilities are fed into classiﬁers to make decisions
[11]. Moreover, Fu et al. (2016) segmented encrypted trafﬁc
ﬂows into sessions in a hierarchical way and extracted packet
length and time delay sequences to build hidden Markov
models (HMM) [9], which can identify service usages and
the end-user in-app behaviors. In addition, work [24] considered the sub-ﬂows during the HTTPS handshake process
and the following data transmission period, and combined
Markov and HMM models with optimal emission probability
to classify encrypted trafﬁc. However, these methods cannot
handle the long-term relationship due to the small order (e.g.,
1 or 2) of Markov model. These methods also split the feature
learning and classiﬁcation procedures, i.e., the application
labels cannot guide the feature representation.

B. Encrypted Trafﬁc Classiﬁcation

C. Deep Learning Based Methods

which improves the classiﬁcation performance.
Our FS-Net achieves excellent results on the real-world
network trafﬁc data for the encrypted trafﬁc classiﬁcation, and outperforms several state-of-the-art methods.
The rest of the paper is organized as follows. Section II
summarizes the related work. The preliminaries are described
in Section III, and the detailed system architecture is proposed
in Section IV. Section V presents the comparison experiments. Finally, we conclude this paper in Section VI.
•

II. R ELATED W ORK
Researches on trafﬁc classiﬁcation emerge in an endless
stream, and in this section, we introduce conventional trafﬁc
classiﬁcation, encrypted trafﬁc classiﬁcation and deep learning models in this ﬁeld.
A. Conventional Trafﬁc Classiﬁcation

With the appearance of machine learning techniques, researchers mainly work on the feature engineering, i.e., consider how to construct enough effective features rather than
extract the signatures from payload contents. There are two
kinds of features commonly used in the encrypted trafﬁc
classiﬁcation: statistical features and sequential features.
1) Statistical Features: Statistical features are proposed
to solve encrypted trafﬁc classiﬁcation problem combined
with various traditional machine learning algorithms, e.g.
logistic regression, random forest and support vector machine.
Liu et al. (2012) designed packet-level statistical features
which include maximum, minimum and mean of sent and
received bytes, and proposed a composite feature-based semisupervised method for encrypted trafﬁc classiﬁcation [20].
Anderson et al. (2016) preferred to ﬂow-level features and
took ﬂow metadata, packet length distributions, time distributions, byte distributions and unencrypted TLS header information as joint features to identify malware encrypted trafﬁc with
the logistic regression algorithm [21]. A robust application
identiﬁcation method with the concept of the burst and ﬂow
statistical features was proposed by work [5]. And Shi et al.
(2018) built a deep learning framework to select and combine
the statistical features to enhance the performances of trafﬁc

Deep learning (DL) has been well applied to the image
processing and natural language processing, but it is still a
new research idea for encrypted trafﬁc classiﬁcation. There
are several attempts to apply DL to it. Lotfollahi et al.
(2017) adopted the stacked autoencoder and one-dimensional
convolution neural network to extract features from encrypted
trafﬁc payloads automatically [25]. Rui et al. (2018) provided
a byte segment neural network for trafﬁc classiﬁcation where
the segments of payloads are put into the attention encoder
to get the features, and then the softmax classiﬁer is used for
classiﬁcation [26]. However, they only use the encrypted payloads of ﬂows to classify behaviors and do not consider other
ﬂow information, which can fail in some encrypted trafﬁc
classiﬁcation problems, like application-level classiﬁcation. In
this paper, we attempt to design a new DL network structure
which is ﬁt for ﬂow sequence characteristic, and adopt the
reconstruction mechanism to enhance the performances of
both the feature representation and classiﬁcation.
III. P RELIMINARIES
In this section, we ﬁrst give the deﬁnition of the encrypted trafﬁc classiﬁcation problem. Then, the recurrent neural

1172
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:29:34 UTC from IEEE Xplore. Restrictions apply.

network, gated recurrent unit and autoencoder framework are
introduced brieﬂy.
A. Problem Deﬁnition
The encrypted trafﬁc classiﬁcation problem in this paper is
to classify the encrypted trafﬁc into speciﬁc applications with
the ﬂow sequences as the only raw trafﬁc information. A raw
ﬂow can be represented as several sequences with the same
ﬂow length and different types (e.g. message type sequences
and packet length sequences). In general, we consider one
kind of sequences as the ﬂow sequences, and other sequences
can be used in the same way. Assume that there are N
samples and C applications in total. Let the sequence of the
(p)
(p)
(p)
p-th sample be xp = [L1 , L2 , ..., Lnp ], where np is the
(p)
length of xp and Li is the packet value at time step i. The
application label of xp is denoted as Ap , 1 ≤ Ap ≤ C. We
aim to build an end-to-end model ψ(xp ) to predict a label Âp
that is exactly the real label Ap .
B. RNN model
The Recurrent Neural Network (RNN) [27] is one of the
most popular neural networks to model sequences. RNN can
infer the current state based on the previous state and the
current input, and the previous state encodes the past information. Therefore, RNN can remember the past information,
which is naturally suitable for sequence modeling.
Speciﬁcally, given the input lt ∈ Rm at time step t, the
hidden state ht ∈ Rn of the vanilla RNN is calculated as
follows:
ht = tanh(W [ht−1 , lt ] + b)

(1)

where ht encodes the input of lt and ht−1 with the historical
information (i.e., the previous l1 , ...lt−1 are kept in the ht−1 ).
W and b are the parameters needed to be learned in the
training process. And [, ] is the concatenation operation.

As shown in Figure 1(a), the GRU cell contains a reset gate
and an update gate. The output of the reset gate (the orange
square) at time step t is as follows,
rt = σ (Wr [lt , ht−1 ] + br )

where Wr and br are trainable variables and σ(x) =
1
1+exp(−x) is the sigmoid function. Similarly, the update gate
(the purple square) is computed by
ut = σ (Wu [lt , ht−1 ] + bu )

ht = ut  ht−1 + (1 − ut )  ĥt

ht-1

ൈ

൅

Compressed Features
ht

ࡸ࢕࢙࢙
Reconstructed
Input

1െ
ൈ

ൈ
ut

rt

࣌

࣌

ࡰࢋࢉ࢕ࢊࢋ࢘

෪࢚
ࢎ
࢚ࢇ࢔ࢎ

Compressed
Representation

ࡱ࢔ࢉ࢕ࢊࢋ࢘
lt

Original Input

(a)

(b)

Fig. 1. 1(a) shows the architecture of gated recurrent unit, and 1(b) shows
the basic structure of autoencoder.

(4)

where  is the element-wise product and ĥt is the new
memory as shown below,
ĥt = tanh (Wh [lt , rt  ht−1 ] + bh )

(5)

where Wh and bh are also learnable parameters.
From Eq. (2) to Eq. (5), we can update the state ht of
the GRU. The reset gate rt decides how much the past state
information contributes to the current state, and drops the
irrelevant and useless information. When the reset gate is 0,
the new memory will forget the previous hidden state and
reset with the current input. On the other hand, the update
gate ut controls how much information from the previous
hidden state is saved and how much new information is added.
The update gate controls both the forget and update of the
hidden state and helps the GRU cell to remember the longterm information. Moreover, the new state ht is the linear
interpolation between the previous hidden state ht−1 and
the new candidate state ĥt , which can avoid the vanishing
gradient problem [30] and model the long-term dependency.
In the rest of the paper, we take the following equation to
describe the update of GRU hidden state brieﬂy, i.e.,
ht = GRU(ht−1 , lt )

ht

(3)

where Wu and bu are weight matrix and bias to be learned.
Therefore, the hidden state ht can be updated as follows,

C. Gated Recurrent Unit
The main weak point of the vanilla RNN in Eq. (1) is the
vanishing gradient problem which cannot retain the long-term
information [28], [29]. The Gated Recurrent Unit (GRU) cell
[30] adds the gating mechanism to control the information
transformation between the hidden states, and tracks the states
of the input sequences without using separate memory cells.

(2)

(6)

Note that the state ht is also the output of the GRU cell at
time step t.
D. Autoencoder
Autoencoder compresses the raw input and learns features
that can represent the main points of the raw input under
the reconstruction mechanism [30]. In order to achieve this
recurrence, autoencoder needs to capture the most important
factors as the representative features of the input data.
The architecture of autoencoder is shown in Figure 1(b).
Encoder, decoder and loss function are three elements of
autoencoder. Encoder layer codes the original input x into
compressed representation y as the abstract features of x.
And the feature vector y is used by decoder to generate the
reconstructed sample x̂. Finally, the loss function computes
the difference between the reconstructed sample x̂ and original input x. During the training procedure, the autoencoder
jointly learns the parameters in both encoder and decoder

1173
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:29:34 UTC from IEEE Xplore. Restrictions apply.

by minimizing loss function, and can obtain the compressed
expressive features to represent the sample x.
Autoencoder is an unsupervised method that learns representative features from the raw data, and we take the
reconstruction mechanism of autoencoder to enhance the
feature learning in our end-to-end method.

The bi-GRU [30] is adopted to incorporate contextual information of the embedding sequence by summarizing sequential
information from both directions. Given an embedding sequence Si = [e1 , e2 , · · · , en ], the bi-GRU contains a forward
−−→
GRU network GRU which reads Si from e1 to en and a
←−−
backward GRU network GRU which reads Si from en to e1 :

−
→
→
−−→ −
h t = GRU h t−1 , et , t ∈ [1, n]

←
−
−
←−− ←
h t = GRU h t+1 , et , t ∈ [1, n]

IV. T HE F LOW S EQUENCE N ETWORK
Our end-to-end Flow Sequence Network (FS-Net) is a hierarchical model and consists of 7 layers as shown in Figure 2.
The FS-Net considers both feature learning and classiﬁcation
together. The supervised signals from the application labels
will guide the feature representation to be more differentiated.
And the self-learning behind the reconstruction mechanism
can also enhance the representation. FS-Net enjoys the advantages of both supervised and unsupervised learning. In the
following of this section, we will present each layer in detail.
In order to express simplicity in the latter, the subscript p of
the sample xp is omitted.
A. Embedding Layer
Learning from word embedding [31] in natural language
processing, we embed each element (i.e., one aspect of the
packet) in the ﬂow sequence to a vector via embedding layer.
Given the element set E with the size of K and dimension
d of element embedding vectors, the total embedding can be
viewed as a matrix E ∈ RK×d . Note that the E is trainable
and will be learned in the training process. The embedding
layer is a lookup table essentially. Given a speciﬁc element B
and the embedding matrix E, the corresponding embedding
vector of B is the B-th row of E, i.e., EB . Similarly,
given a ﬂow sequence with n elements x = [L1 , L2 , ..., Ln ],
each element Li , i ∈ [1, n] needs to be converted into a ddimension vector ELi . Finally, we can obtain the embedding
sequence [e1 , e2 , · · · , en ] where ei = ELi .
There are several advantages to take the embedding vectors.
1) With the embedding vectors, some non-numeric values
(e.g. message type) can be easily represented into numeric
values for computing. 2) The vector representation enriches
the information saved in each element of one sequence. Each
dimension of the embedding vector is a latent feature that
inﬂuences the generation of the ﬂow. The same element
in different sequences may have different meanings and
aspects. For example, various certiﬁcate packets may have the
same length, but they have different meanings. The mixture
information behind the speciﬁc length can be captured by an
embedding vector (imagining a one-hot vector whose each
dimension is a speciﬁc certiﬁcate). 3) With the trainable
setting of the embedding vectors, our model can learn the
task-oriented representation of the embedding vector of each
element, which can boost the classiﬁcation performance.
B. Encoder Layer
The encoder layer takes the embedding vectors of a ﬂow
as input, and generates the compressed features. The encoder
layer consists of stacked bidirectional GRUs (bi-GRU).

(7)
(8)

→
−
←
−
where h t and h t are the forward and backward hidden
→
−
states respectively, and the initial hidden state vectors h 0
←
−
→
−
and h n+1 are both zero vectors. Note that h t summarizes
←
−
the information before et and h t summarizes that behind et .
→
−
Therefore, we concatenate the forward hidden state h t and
←
−
summarization
of
the backward hidden state h t to obtain the
→
− ←
−
the whole ﬂow at time step t, i.e., ot = h t , h t .
To further improve the representation of the encoder,
we stack the multi-layer bi-GRUs in our model. The lowlevel expressions learn the local features, while the highlevel expressions are composed of combinations of low-level
expressions to obtain global features. Formally, the input of
(i−1)
the i-th layer at time step t is the output ot
of the (i-1)-th
layer at time step t. That is
−
→(i) −−→ −
→(i) (i−1) 
h t = GRU h t−1 , ot
, t ∈ [1, n], i > 0


−(i) (i−1)
←
−(i) ←−− ←
, t ∈ [1, n], i > 0
h t = GRU h t+1 , ot

(9)
(10)

We concatenate the ﬁnal hidden states of both forward and
backward directions of all the layers to obtain the encoderbased feature vector ze of the input ﬂow x as follows:
−
→
←
−(1)
−
→(J) ←
−(J) 
ze = h (1)
n , h1 ,··· , hn , h1

(11)

where J is the number of layers of bi-GRUs in encoder. With
this setting, ze contains bidirectional contextual information
of the whole ﬂow sequence.
C. Decoder Layer
The decoder layer adopts another stacked bi-GRU network
similar to the encoder layer. Learning from the architecture
of autoencoder, the encoder-based feature vector ze is input
into the decoder at each time step t, i.e.,
−−→ →
−
→
s t = GRU (−
s t−1 , ze ) , t ∈ [1, n]
←
−
−
−
←
−
s t+1 , ze ) , t ∈ [1, n]
s t = GRU (←

(12)
(13)

−
−
where →
s t and ←
s t are the forward and backward hidden states
of decoder respectively. And we also take the stacked multilayer bi-GRUs similar to Eq. (9) and (10), and the number of
layers is also J.
The output of decoder consists of two parts. The ﬁrst part
is the ﬂow reconstruction vector at each time step t, and we
can obtain the decoder output sequence D = {d1 , d2 , ..., dn }
where dt (similar to ot in encoder layer) is the concatenation
of the forward and backward hidden states of all J bi-GRU

1174
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:29:34 UTC from IEEE Xplore. Restrictions apply.

bi-GRU

Packet Length
Length Embedding

ࡸ૚

ࢋ૚

ࡸ૛

ࢋ૛

ࡸ૜

ࢋ૜

…

…

ࡸ࢔-1

ࢋ࢔ -1

ࡸ࢔

ࢋ࢔

flow

Embedding Layer

࡭࢖

Dense Layer

Softmax

Classification Layer

Application Label

෡࢖
࡭

Loss
漨

࡭࢖

…

…
…

…

ࡸ෠ ૚

ࡸ૚

ࡸ෠ ૛

ࡸ૛

ࡸ෠ ૜

…

Encoder Layer

…

Decoder Layer

漨

ࡸ૜

…

…

ࡸ෠ ࢔ି૚

ࡸ࢔-1

ࡸ෠ ࢔

ࡸ࢔

Reconstruction Layer

Loss

…

Fig. 2. The system overview of the FS-Net.

layers at time step t. The decoder sequence will be used in the
reconstruction layer to recover the original input sequence.
The second part is the decoder-based feature vector zd of
input ﬂow x, which is the concatenation of all the ﬁnal hidden
states of both directions of all J bi-GRU layers.


→
←
−(1)
−
→(J) ←
−(J)
zd = −
s (1)
n , s 1 ,··· , s n , s 1

z = [ze , zd , ze  zd , |ze − zd |]



(14)

Compared with ze which maintains the main components of
the ﬂow, zd shows the ﬂow features from the ﬁne-grained
perspective. The decoder extracts the information saved in
ze at each time step and generates the essential signals to
reconstruct the original input sequence. The hidden states of
the decoder are the remaining ﬁne-grained features behind
the ﬂow sequence. These features may be helpful for the
classiﬁcation problem.
D. Reconstruction Layer
The decoder sequence D is input into the reconstruction
layer to generate the probability distribution over the element
set E. Speciﬁcally, softmax classiﬁer is used to generate the
distribution:
exp(θiT x + bi )
pt (i) = K
T
k=1 exp(θk x + bk )

more advantageous local features for better classiﬁcation
results.
To enrich the classiﬁcation features, we take the following
as the compound feature vector z of the ﬂow sequence:

(15)

where pt (i) is the probability of the element i at time step
t, and θk , 1 ≤ k ≤ K are the trainable parameters. With the
distribution, we can recover the t-th packet information L̂t
which is the element with the maximum probability in the
distribution pt .
E. Dense Layer
The dense layer ﬁrst combines the encoder-based feature
vector ze and the decoder-based feature vector zd as a compound feature vector z, and then compresses z by choosing

(16)

where  is the element-wise product and | · | is the elementwise absolute value. ze  zd measures the consistency of ze
and zd , while |ze − zd | gives the difference between these two
vectors. However, the dimension of z is very high, which is
under the risk of over-ﬁtting. Therefore, we take a two-layer
perceptron with Selu activation function [32] to compress it:
zc = Selu (W2 Selu (W1 z + b1 ) + b2 )

(17)

where W1 , W2 , b1 and b2 are the parameters needed to learn.
The combination of encoder-based and decoder-based feature vectors increases the non-linearity of the classiﬁcation
features. Moreover, the feature compression of the two-layer
perceptron avoids over-ﬁtting effectively. Therefore, the dense
layer can improve the representation of the FS-Net.
F. Classiﬁcation Layer
The compressed feature vector zc is sent to another softmax
classiﬁer similar to Eq. (15) to obtain the distribution q over
different applications. And we take the application with the
maximum probability as the prediction label Â.
G. Loss
The loss function of FS-Net consists of two parts with α
as the trade-off:
L = LC + αLR

(18)

where LC is the loss of classiﬁcation and LR is the loss of
reconstruction.

1175
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:29:34 UTC from IEEE Xplore. Restrictions apply.

Given the distribution qp over applications for the sample
xp , the classiﬁcation loss is the cross entropy as follows,
1 
I (Ap = c) log qp (c)
N p c=1
N

LC = −

TABLE I
T HE S TATISTICAL I NFORMATION OF 18 A PPLICATIONS
ID
1
3
5
7
9
11
13
15
17

C

(19)

where I (Ap = c) = 1 if Ap is c, else 0, and qp (c) is the
probability of application c for the sample xp . The classiﬁcation loss will guide the learning direction of the trainable
parameters in the FS-Net (i.e., embedding, encoder, decoder
and dense layers) to generate the representative features which
are suitable for the classiﬁcation task.
The reconstruction loss is another cross entropy loss,
np K
N

1  1    (p)
LR = −
I Lt = e log ppt (e)
N p np t=1 e=1

(20)

The reconstruction loss is the average loss of all the packets
of all the samples. This loss can guide the FS-Net (i.e.,
embedding, encoder, decoder layers) to learn boosted features
of ﬂows that can represent the ﬂows.
With the joint learning architecture, the classiﬁcation and
reconstruction share most of trainable parameters of the FSNet. The balance of these two losses can learn distinguishing
features which are beneﬁcial for the ﬁnal classiﬁcation.
V. E VALUATION
In this section, we present the dataset, experimental setting,
comparison results and sensitivity analysis.
A. Dataset
We use the dataset of [11] which is captured from a realworld campus network environment to test and verify our
method FS-Net. The dataset was collected for 7 days long and
consists of 956+ thousand encrypted trafﬁc ﬂows referring to
18 popular applications after packet recombination and ﬂow
reduction techniques. The statistical information of dataset is
shown in Table I. We adopt 5-fold cross validation to enhance
the reliability of our experiments.

Flows
16,560
111,471
7,488
22,993
12,168
9,001
114,985
17,267
46,545

ID
2
4
6
8
10
12
14
16
18

Apps
Alipay
Baidu
Gmail
JD
Mozilla
OneNote
Sogou
Weibo
Zhihu

Flows
20,299
373,177
100,339
48,146
4,265
6,486
4,498
24,289
16,318

1. NeCmusic means Netease Cloud Music.

MaMPF [11] uses the output probabilities of the message
type and the length block Markov models as features
to classify encrypted trafﬁc with the random forest
classiﬁer. The number of trees is set as 50.
2) Setting of the FS-Net: We take the packet length sequences as the input of the FS-Net, and experiments on other
sequences can be found in Section V-C2. The dimension of
the packet length embedding vector is set as 128. We set the
dimension of hidden states of each GRU as 128, and take
the 2-layer bi-GRU network in both encoder and decoder
layers. The hyper-parameter α is set as 1. Moreover, we take
dropout [33] with 0.3 ratio to avoid over-ﬁtting, and the Adam
optimizer [34] with learning rate 0.0005 is used. Our model
FS-Net is implemented with TensorFlow.
3) Metrics: We evaluate all the methods based on the
True Positive Rate (TPR), False Positive Rate (FPR) and
FTF referring to [6], [11]. We also use T P RAV E (the ratio
between all the rightly classiﬁed ﬂows and the total ﬂows),
F P RAV E (the ratio between all the wrongly classiﬁed ﬂows
and the total ﬂows) to measure the overall performance. The
deﬁnitions are as follows:
•

T P RAV E =

1 
T P Ri ∗ F lNi
N i=0

(21)

F P RAV E =

1 
F P Ri ∗ F lNi
N i=0

(22)

C

C

B. Experimental Setting
1) Comparison Methods: Some state-of-the-art methods
are summarized as comparison methods as follows:
• FoSM [22] uses message type sequences to build ﬁrstorder Markov model and takes the application with the
maximum probability as the classiﬁcation result.
• SOCRT [23] combines the certiﬁcate packet length and
the second-order Markov model to classify applications.
The certiﬁcate clustering number is taken as 5.
• SOB [6] imports the ﬁrst communication packet length
based on SOCRT to decide the ﬁnal classiﬁcation results.
We take 40 as the number of bi-gram clustering.
• FoLM is a variant of FoSM, which replaces the message
type sequences with the packet length sequences.
• SOB-L is a variant of SOB, which replaces the message
type sequences with the packet length sequences. 40 is
taken as the number of bi-gram clustering.

Apps
Alicdn
Apple
Github
iCloud
Kaipanla
NeCmusic1
QQ
Taobao
Youdao

FTF =

C

i=0

wi

T P Ri
1 + F P Ri

(23)

where F lNi is the ﬂow number of application i and wi is
the ratio between F lNi and the total ﬂow number N , i.e.,
lNi
wi = F N
.
C. Experiments
1) Comparison experiments: The comparison results are
shown in Table II. We can obtain the following conclusions:
1. FS-Net achieves the best performance, and outperforms
all the other methods. From Table II, the FS-Net obtains
the best TPR performances on 17 of 18 applications except
OneNote, but its FPR is the best, 0, which means there are no
any false trafﬁc samples classiﬁed as OneNote. And our FSNet can obtain the best performance on all the overall metrics

1176
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:29:34 UTC from IEEE Xplore. Restrictions apply.

TABLE II
E XPERIMENTAL R ESULTS ON TPR, FPR AND FTF (T HE B EST R ESULTS A RE IN B OLD )
ID

APP

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
11
12
13
14
15
16
17
18
-

Alicdn
Alipay
Apple
Baidu
Github
Gmail
iCloud
JD
Kaipanla
Mozilla
NeCmusic
OneNote
QQ
Sogou
Taobao
Weibo
Youdao
Zhihu
AVE
FTF

FoSM
FPR

SOCRT
TPR
FPR

TPR

0.5158
0.0054
0.5277
0.0190
0.6421
0.0024
0.7488
0.0002
0.4600
0.0097
0.9984
0.0076
0.6408
0.0281
0.0294
0.0007
0.5219
0.0098
0.7852
0.0063
0.8294
0.0332
0.9820
0.0053
0.0979
0.0149
0.7536
0.0478
0.0635
0.0096
0.4925
0.0065
0.8545
0.1434
0.7472
0.0302
0.6199
0.0211
0.6117

0.6171
0.0250
0.5786
0.0255
0.6493
0.0024
0.7954
0.0048
0.4546
0.0037
0.9993
0.0043
0.7290
0.0138
0.0483
0.0036
0.1089
0.0046
0.7951
0.0030
0.8329
0.0324
0.9734
0.0032
0.1168
0.0139
0.7514
0.0370
0.2848
0.0170
0.8226
0.0183
0.8368
0.1212
0.7914
0.0123
0.6543
0.0192
0.6457

0.7650
0.0224
0.5433
0.0098
0.7018
0.0034
0.8227
0.0051
0.4964
0.0040
0.9994
0.0044
0.7351
0.0059
0.0863
0.0076
0.9392
0.0126
0.7993
0.0030
0.8401
0.0334
0.9827
0.0139
0.2689
0.0256
0.7656
0.0150
0.3906
0.0124
0.5969
0.0030
0.8577
0.1146
0.7829
0.0017
0.7023
0.0165
0.6935

TPR

SOB

FoLM
FPR

(i.e., T P RAV E , F P RAV E and FTF), because it enjoys the
advantages of the end-to-end learning architecture (i.e., joint
learning of the feature representation and classiﬁcation) and
the reconstruction mechanism.
2. The FS-Net can better model the ﬂow sequences than
the Markov models. The FoLM, SOB-L and FS-Net all take
the packet length sequences as input, and our proposed FSNet outperforms the other two methods according to Table II.
Traditional Markov-based methods can only capture one or
two order information of adjacent packets in one ﬂow, while
the FS-Net uses the bi-GRU network to model the sequence
with the advantage of keeping the contextual information
of the whole ﬂow. The FS-Net is more consistent with the
generative context mechanism of ﬂows in the real world.
3. The end-to-end framework leads the FS-Net to achieve
a better performance than other piece-wise models. Our FSNet outperforms the MaMPF, although only packet length
sequences are taken as its input while MaMPF combines
the packet length sequences and message type sequences
to classify encrypted trafﬁc. Moreover, MaMPF takes the
well-performed random forest classiﬁer which usually obtains
better results than the pure softmax classiﬁer. However,
MaMPF is a piece-wise model, and the classiﬁer cannot
direct the features built from Markov models. By contraries,
our FS-Net can make up for this shortcoming, beneﬁted
from the end-to-end framework. The feature learning can
be guided by the classiﬁcation task and the reconstruction
mechanism. Therefore, the features are more distinguishable
for the encrypted trafﬁc classiﬁcation.
4. The packet length is more representative than the message type in the encrypted trafﬁc classiﬁcation task. Comparing FoSM, FoLM, SOB and SOB-L, the performances of
FoLM and SOB-L are vastly better than the other two methods. The main reason might be the high overlapping of the
message type sequences of different applications discovered
by [11]. There are more elements in the packet length set than

FPR

SOB-L
TPR
FPR

MaMPF
TPR
FPR

FS-Net
TPR
FPR

0.7894
0.0006
0.7820
0.0031
0.8395
0.0025
0.8871
0.0004
0.7747
0.0041
0.9994
0.0051
0.8134
0.0015
0.6564
0.0039
0.7762
0.0029
0.9003
0.0058
0.9822
0.0186
0.9953
0.0069
0.8231
0.0015
0.8923
0.0020
0.7134
0.0015
0.8781
0.0129
0.9695
0.0282
0.9803
0.0286
0.8699
0.0072
0.8662

0.7218
0.0004
0.9243
0.0006
0.9397
0.0008
0.9519
0.0002
0.8073
0.0002
1.0000
0.0536
0.8744
0.0001
0.9053
0.0010
0.6302
0.0001
0.9274
0.0000
0.9816
0.0002
0.9962
0.0000
0.9395
0.0006
0.8158
0.0001
0.7981
0.0020
0.9129
0.0009
0.9885
0.0001
0.9858
0.0004
0.9385
0.0034
0.9328

0.8237
0.0007
0.8592
0.0006
0.9561
0.0042
0.9909
0.0121
0.8507
0.0005
0.9993
0.0001
0.9668
0.0004
0.9083
0.0037
0.9789
0.0004
0.9114
0.0002
0.9552
0.0005
0.9906
0.0001
0.9622
0.0100
0.8724
0.0002
0.7798
0.0010
0.9155
0.0008
0.9641
0.0009
0.9333
0.0006
0.9632
0.0020
0.9567

0.9715
0.0006
0.9868
0.0004
0.9899
0.0016
0.9976
0.0008
0.9867
0.0001
1.0000
0.0000
0.9948
0.0001
0.9560
0.0017
0.9996
0.0001
0.9941
0.0000
0.9950
0.0001
0.9961
0.0000
0.9921
0.0013
0.9877
0.0000
0.9365
0.0007
0.9704
0.0007
0.9973
0.0002
0.9947
0.0002
0.9914
0.0005
0.9906

TPR

TABLE III
C OMPARISON E XPERIMENTS B ETWEEN T HE FS-N ET A ND I TS VARIANTS
Methods
FS-Net
FS-ND
FS-Net-S
FS-ND-S
FS-Net-SL
FS-ND-SL

T P RAV E
0.9914
0.9805
0.7353
0.7347
0.9919
0.9807

F P RAV E
0.0005
0.0007
0.0145
0.0147
0.0005
0.0007

FTF
0.9906
0.9798
0.7248
0.7152
0.9911
0.9800

the message type set, which increases the discrimination of
ﬂows. Comparing SOCRT and SOB, the ﬁrst communication
packet length can indeed improve the classiﬁcation results,
but the improvement is limited.
2) Analysis on FS-Net: We analyze several properties of
the proposed FS-Net.
• The reconstruction mechanism can enhance the feature
representation and discrimination by recovering the input
sequence. To verify it, we design a variant of our model
which abandons the decoder layer, reconstruction layer
and the reconstruction loss in Figure 2, i.e., only the
encoder-based feature vector ze is passed to the dense
layer for classiﬁcation. The variant is termed as FS-ND.
The packet length sequences are the default choice for
the FS-Net and FS-ND as the input.
• The message type sequences are used as the input of
traditional message type Markov based methods (i.e.,
FoSM, SOCRT and SOB). For ease of comparison, the
FS-Net and FS-ND are all under test combined with
message type sequences, and the corresponding methods
are denoted as FS-Net-S and FS-ND-S.
• Multi-attribute sequences (i.e., message type and packet length sequences) are united to enhance the performance. We double the feature learning layers, and
concatenate the encoder-based and decoder-based features from two different networks as the input of dense

1177
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:29:34 UTC from IEEE Xplore. Restrictions apply.

0.9898

FPR
0.9911

0.9917

0.992

0.9851

0.0008

0.975

0.0007
0.0006

0.0006

0.0006
0.0005

0.0005

0.97
0.965

0.9772

0.9836

4

8

0.0004

0.9871

0.9885

0.9888

0.9902

0.9909

0.9912

16

32

64

128

256

512

0.9913

FTF
0.9908

0.9911

0.9912

0.9911

TPR
0.9897

0.9907

FPR
0.9902

0.9896

0.988

0.001

0.979

0.0008

0.992

0.0012

0.985
0.98

0.0014

0.0012
0.988

0.9884

0.9868

0.984

TPR/FTF

0.0012

TPR
0.9895

FPR

TPR/FTF

0.99

0.9882

0.0004

0.0008

0.98
0.976
0.972

0.0002

0.968

0

0.964

0.001

0.0007
0.0006
0.0005

0.0005

0.0005

0.0005

0.0005

0.9904

0.9899

0.9903

0.9903

0.9902

0.125

0.25

0.5

1

2

0.0006

0.0007
0.0006

0.0006

FPR

FTF

0.995

0.0004

0.0005

0.0005

0.9887

0.9899

0.9892

0.9885

0.9867

0.9872

0.9854

4

8

16

32

64

128

256

0.0002
0

The number of hidden states

Fig. 3. Results of FS-Net with different dimensions of hidden states. TPR
and FPR in this ﬁgure means the metric T P RAV E and F P RAV E

Fig. 4. Comparison results of FS-Net with different α. TPR and FPR in this
ﬁgure means the metric T P RAV E and F P RAV E

layer. With this strategy, the FS-Net can be extended
with multi-attribute sequences. The strategy can also be
applied on the FS-ND. And these two variant models are
termed as FS-Net-SL and FS-ND-SL.
The experimental results of FS-Net and its ﬁve variants are
shown in Table III, and we can draw some conclusions.
1. The reconstruction mechanism can indeed enhance the
feature representation and improve the classiﬁcation performance. Comparing them with different sequences, the FS-Net
always outperforms the FS-ND with about 0.01 improvement
in FTF. With reconstruction mechanism, the features learned
from the encoder are guided to store richer information.
Moreover, the distinctiveness of decoder-based features is also
strengthened for encrypted trafﬁc classiﬁcation task.
2. Our variant model FS-ND is also better than the stateof-the-art models, and the performance gap between FS-Net
and FS-ND is not large. However, the FS-ND model takes
less layers than the FS-Net, which can be trained faster. The
FS-ND can be regarded as a distilled version of our model.
3. The end-to-end structure performs better than piecewise framework. Although using the same input (i.e., message
type sequences), the FS-Net-S and FS-ND-S outperform the
FoSM, SOCRT and SOB in Table II, because the classiﬁcation
results can guide the feature representation. Therefore, our
model can learn more distinguishable features.
4. The information of message type sequences is almost
incorporated into that of packet length sequences. The improvement from FS-Net to FS-Net-SL is not signiﬁcant (e.g.,
0.0005 in FTF). Similar phenomenon happens between FSND and FS-ND-SL. Moreover, the results of FS-Net and FSNet-S also demonstrate that the information in packet length
sequences is richer than that of message type sequences.

Therefore, we train the FS-Net with different dimensions
of hidden states (i.e., 4, 8, 16, 32, 64, 128, 256, 512) and
show the results in Figure 3. Obviously, as the dimensions of
hidden states increase, the T P RAV E and FTF rise while the
F P RAV E decreases. It is worthy to note that the FS-Net can
outperform the state-of-the-art models even the dimension of
hidden state is very small (e.g. 4). However, the improvement tends to be gentle with the exponential growth of the
dimension of hidden states. From 128 to 512 dimensions,
T P RAV E and FTF increase less than 0.1% between any two
adjacent tested values. The training time of the FS-Net is
nearly linear with the dimension of hidden states, i.e., the
model with small dimensions of hidden states can be trained
fast. Moreover, the model will face a high risk of over-ﬁtting
even if dropout is applied when the dimension of hidden states
is very large. Therefore, the dimension of hidden states should
be set according to the actual demand.
Considering the balance of performance and training time,
we choose 128 as the dimension in this paper.
2) Parameter α: The beneﬁt of reconstruction mechanism
in the FS-Net has been veriﬁed in Table III, which can
improve the ﬁnal classiﬁcation performance.
The parameter α controls the contributions of the reconstruction loss LR . Different values of α (i.e., 0.125, 0.25, 0.5,
1, 2, 4, 8, 16, 32, 64, 128, 256) are set and the results are
shown in Figure 4. The best performance (99.13% T P RAV E ,
0.05% F P RAV E and 0.9904 FTF) happens in α = 0.125
while the worst (98.68% T P RAV E , 0.07% F P RAV E and
0.9854 FTF) happens in α = 256. From the overall trend,
the metrics become worse as α increases. However, the
results are relatively stable when α is between 0.125 and 2.
The difference amplitude of T P RAV E and FTF is no more
than 0.0005, and F P RAV E do not change. Therefore, it is
recommended to set α with values in [0.125, 2].

D. Sensitivity Analysis
1) The dimension of hidden states: Hidden states of the
encoder and decoder in the FS-Net is to extract and store the
latent information of the ﬂow sequences, and each dimension
is an aspect to represent the latent information. The dimension
of hidden states directly affects the performance of the FSNet. Small value results in a bad performance due to the
weak ability to capture the latent information, while large
value can lead to over-ﬁtting because our model might learn
some useless information from the noise data.

VI. C ONCLUSIONS
In this paper, we design an end-to-end encrypted trafﬁc
classiﬁcation model named FS-Net. It jointly learns the representative features from the raw ﬂow sequences and classiﬁes
these ﬂows together. The FS-Net takes a multi-layer bi-GRU
encoder to learn the representation of the ﬂow sequence, and
reconstructs the original sequence with a multi-layer bi-GRU
decoder. The features learned from the encoder and decoder

1178
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:29:34 UTC from IEEE Xplore. Restrictions apply.

are combined for classiﬁcation. The end-to-end framework
makes the FS-Net learn representative information from data
and saves human effort to design features, while the reconstruction mechanism enhances the representability of features
and improves the performance of classiﬁcation. Moreover, the
FS-Net can be easily extended with multi-attribute sequences
as the input. We validate the effectiveness of the FS-Net on
the real-world network trafﬁc dataset, and the experimental
results demonstrate that the FS-Net can achieve an excellent
classiﬁcation performance and outperform the state-of-the-art
methods on encrypted trafﬁc classiﬁcation.
ACKNOWLEDGMENT
This work is supported by The National Key Research
and Development Program of China (No.2016QY05X1000
and No.2016YFB0801200) and The National Natural Science
Foundation of China (No.61602472, No.U1636217). Zhen Li
is the corresponding author.
R EFERENCES
[1] H. Shi, H. Li, D. Zhang, C. Cheng, and X. Cao, “An efﬁcient feature
generation approach based on deep learning and feature selection
techniques for trafﬁc classiﬁcation,” Computer Networks, vol. 132, pp.
81–98, 2018.
[2] T. Bujlow, V. Carela-Español, and P. Barlet-Ros, “Independent comparison of popular dpi tools for trafﬁc classiﬁcation,” Computer Networks,
vol. 76, pp. 75–89, 2015.
[3] J. Liu, Y. Fu, J. Ming, Y. Ren, L. Sun, and H. Xiong, “Effective and
real-time in-app activity analysis in encrypted internet trafﬁc streams,”
in Proceedings of the 23rd ACM SIGKDD International Conference on
Knowledge Discovery and Data Mining. ACM, 2017, pp. 335–344.
[4] P. Velan, M. Čermák, P. Čeleda, and M. Drašar, “A survey of methods
for encrypted trafﬁc classiﬁcation and analysis,” International Journal
of Network Management, vol. 25, no. 5, pp. 355–374, 2015.
[5] V. F. Taylor, R. Spolaor, M. Conti, and I. Martinovic, “Robust smartphone app identiﬁcation via encrypted network trafﬁc analysis,” IEEE
Transactions on Information Forensics and Security, vol. 13, no. 1, pp.
63–78, 2018.
[6] M. Shen, M. Wei, L. Zhu, and M. Wang, “Classiﬁcation of encrypted trafﬁc with second-order markov chains and application attribute
bigrams,” IEEE Transactions on Information Forensics and Security,
vol. 12, no. 8, pp. 1830–1843, 2017.
[7] B. Anderson and D. McGrew, “Machine learning for encrypted malware
trafﬁc classiﬁcation: accounting for noisy labels and non-stationarity,”
in Proceedings of the 23rd ACM SIGKDD International Conference on
Knowledge Discovery and Data Mining. ACM, 2017, pp. 1723–1732.
[8] V. F. Taylor, R. Spolaor, M. Conti, and I. Martinovic, “Appscanner:
Automatic ﬁngerprinting of smartphone apps from encrypted network
trafﬁc,” in Security and Privacy (EuroS&P), 2016 IEEE European
Symposium on. IEEE, 2016, pp. 439–454.
[9] Y. Fu, H. Xiong, X. Lu, J. Yang, and C. Chen, “Service usage
classiﬁcation with encrypted internet trafﬁc in mobile messaging apps,”
IEEE Transactions on Mobile Computing, vol. 15, no. 11, pp. 2851–
2864, 2016.
[10] M. Conti, L. V. Mancini, R. Spolaor, and N. V. Verde, “Analyzing
android encrypted network trafﬁc to identify user actions,” IEEE
Transactions on Information Forensics and Security, vol. 11, no. 1,
pp. 114–125, 2016.
[11] L. Chang, C. Zigang, X. Gang, G. Gaopeng, Y. Siu-Ming, and H. Longtao, “Mampf: Encrypted trafﬁc classifﬁcation based on multi-attribute
markov probability ﬁngerprints,” in Quality of Service (IWQoS), 2018
IEEE/ACM 24th International Symposium on. IEEE, 2018.
[12] B. Anderson and D. McGrew, “Identifying encrypted malware trafﬁc
with contextual ﬂow data,” in Proceedings of the 2016 ACM Workshop
on Artiﬁcial Intelligence and Security. ACM, 2016, pp. 35–46.

[13] C. Liu, Z. Cao, Z. Li, and G. Xiong, “Lafft: Length-aware fft based
ﬁngerprinting for encrypted network trafﬁc classiﬁcation,” in 2018
IEEE Symposium on Computers and Communications (ISCC). IEEE,
2018, pp. 1–6.
[14] Y. Qi, L. Xu, B. Yang, Y. Xue, and J. Li, “Packet classiﬁcation
algorithms: From theory to practice,” in INFOCOM 2009, IEEE. IEEE,
2009, pp. 648–656.
[15] F. Constantinou and P. Mavrommatis, “Identifying known and unknown
peer-to-peer trafﬁc,” in Network Computing and Applications, 2006.
NCA 2006. Fifth IEEE International Symposium on. IEEE, 2006, pp.
93–102.
[16] J. Erman, A. Mahanti, M. Arlitt, and C. Williamson, “Identifying and
discriminating between web and peer-to-peer trafﬁc in the network
core,” in Proceedings of the 16th international conference on World
Wide Web. ACM, 2007, pp. 883–892.
[17] M. Finsterbusch, C. Richter, E. Rocha, J.-A. Muller, and K. Hanssgen,
“A survey of payload-based trafﬁc classiﬁcation approaches,” IEEE
Communications Surveys & Tutorials, vol. 16, no. 2, pp. 1135–1156,
2014.
[18] R. Keralapura, A. Nucci, and C.-N. Chuah, “Self-learning peer-to-peer
trafﬁc classiﬁer,” in Computer Communications and Networks, 2009.
ICCCN 2009. Proceedings of 18th Internatonal Conference on. IEEE,
2009, pp. 1–8.
[19] M. Roughan, S. Sen, O. Spatscheck, and N. Dufﬁeld, “Class-of-service
mapping for qos: a statistical signature-based approach to ip trafﬁc
classiﬁcation,” in Proceedings of the 4th ACM SIGCOMM conference
on Internet measurement. ACM, 2004, pp. 135–148.
[20] H. Liu, Z. Wang, and Y. Wang, “Semi-supervised encrypted trafﬁc
classiﬁcation using composite features set,” Journal of Networks, vol. 7,
no. 8, p. 1195, 2012.
[21] B. Anderson, S. Paul, and D. McGrew, “Deciphering malwares use of
tls (without decryption),” Journal of Computer Virology and Hacking
Techniques, pp. 1–17, 2016.
[22] M. Korczyński and A. Duda, “Markov chain ﬁngerprinting to classify
encrypted trafﬁc,” in Infocom, 2014 Proceedings IEEE. IEEE, 2014,
pp. 781–789.
[23] M. Shen, M. Wei, L. Zhu, M. Wang, and F. Li, “Certiﬁcate-aware
encrypted trafﬁc classiﬁcation using second-order markov chain,” in
Quality of Service (IWQoS), 2016 IEEE/ACM 24th International Symposium on. IEEE, 2016, pp. 1–10.
[24] W. Pan, G. Cheng, and Y. Tang, “Wenc: Https encrypted trafﬁc
classiﬁcation using weighted ensemble learning and markov chain,”
in Trustcom/BigDataSE/ICESS, 2017 IEEE. IEEE, 2017, pp. 50–57.
[25] M. Lotfollahi, R. Shirali, M. J. Siavoshani, and M. Saberian, “Deep
packet: A novel approach for encrypted trafﬁc classiﬁcation using deep
learning,” arXiv preprint arXiv:1709.02656, 2017.
[26] L. Rui, X. Xi, N. Shiguang, Z. Haitao, and X. Shutao, “Byte segment
neural network for network trafﬁc classiﬁcation,” in IEEE/ACM International symposium on Quality of Service. IEEE, 2018.
[27] D. P. Mandic and J. Chambers, Recurrent neural networks for prediction: learning algorithms, architectures and stability. John Wiley &
Sons, Inc., 2001.
[28] K. Kawakami, “Supervised sequence labelling with recurrent neural
networks,” Ph.D. dissertation, PhD thesis. Ph. D. thesis, Technical
University of Munich, 2008.
[29] Y. Bengio, P. Simard, and P. Frasconi, “Learning long-term dependencies with gradient descent is difﬁcult,” IEEE transactions on neural
networks, vol. 5, no. 2, pp. 157–166, 1994.
[30] K. Cho, B. Van Merriënboer, C. Gulcehre, D. Bahdanau, F. Bougares,
H. Schwenk, and Y. Bengio, “Learning phrase representations using
rnn encoder-decoder for statistical machine translation,” arXiv preprint
arXiv:1406.1078, 2014.
[31] T. Mikolov, I. Sutskever, K. Chen, G. S. Corrado, and J. Dean,
“Distributed representations of words and phrases and their compositionality,” in Advances in neural information processing systems, 2013,
pp. 3111–3119.
[32] G. Klambauer, T. Unterthiner, A. Mayr, and S. Hochreiter, “Selfnormalizing neural networks,” in Advances in Neural Information
Processing Systems, 2017, pp. 971–980.
[33] G. E. Hinton, N. Srivastava, A. Krizhevsky, I. Sutskever, and
R. Salakhutdinov, “Improving neural networks by preventing coadaptation of feature detectors,” CoRR, vol. abs/1207.0580, 2012.
[34] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
CoRR, vol. abs/1412.6980, 2014.

1179
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:29:34 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
