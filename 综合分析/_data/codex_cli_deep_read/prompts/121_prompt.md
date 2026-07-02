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
# [121] Bi-ETC: A Bidirectional Encrypted Traffic Classification Model Based on BERT and BiLSTM
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
编号：121
题名：Bi-ETC: A Bidirectional Encrypted Traffic Classification Model Based on BERT and BiLSTM
年份：2023
DOI：10.1109/dsc59305.2023.00037
来源：2023 8th International Conference on Data Science in Cyberspace (DSC)
PDF：paper/10.1109_dsc59305.2023.00037.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\121.txt
- 原始字符数：37987
- 本次发送字符数：37987
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2023 8th International Conference on Data Science in Cyberspace (DSC)

2023 8th International Conference on Data Science in Cyberspace (DSC) | 979-8-3503-3103-5/23/$31.00 ©2023 IEEE | DOI: 10.1109/DSC59305.2023.00037

Bi-ETC:A Bidirectional Encrypted Traffic
Classification Model Based on BERT and BiLSTM
1st XiTing Ma

2nd Tao Liu

Cyberspace Institute of Advanced Technology
1st GuangZhou University
Guangzhou 510006,China
2112233031@e.gzhu.edu.cn

Cyberspace Institute of Advanced Technology
1st GuangZhou University
Guangzhou 510006,China
2112233168@e.gzhu.edu.cn

3th Ning Hu∗

4rd Xin Liu

Peng Cheng Laboratory
Shenzhen 518000, China
hun@pcl.ac.cn

College of computer Engineering and Applied Math
3rd ChangSha University
Changsha 410022, China
xinliu@ccsu.edu.cn

2

nd

protocol layers, which makes the classification of encrypted
traffic difficult. Even if the same encryption protocol is used,
the data distribution of encrypted traffic may show completely
different characteristics due to the different original traffic
distribution[3]. Therefore, the traffic classification method for
a certain type of encrypted traffic cannot adapt well to new
environments or unseen encryption policies.
The traditional port-based traffic identification method[4] is
no longer reliable in the classification of encrypted traffic,
and can only be used as an auxiliary means for traffic
classification. In addition, earlier works utilize the remaining
plaintext in encrypted traffic to build fingerprints and perform
fingerprint matching classification[5] are not applicable to
emerging encryption technologies, as plaintext becomes more
sparse or obfuscated. To this end, many scholars use machine
learning[6, 7] to assist traffic classification methods, and train
classifiers based on manually extracted packet or its statistical
features at the data flow level. Since these features require
prior knowledge and experience, they are also time-consuming
to extract. More importantly, there is no guarantee that these
features are really helpful to improve the classification performance. As a result, many researchers have utilized deep
learning methods[8, 9] to automatically learn complex patterns
from raw traffic and achieved significant performance gains.
However, these methods require a large amount of labeled
training data to achieve good performance.
In recent years, pre-trained models have made significant
breakthroughs in natural language processing[10], computer
vision[11] and other fields. The advantage of pre-trained
models is that they can learn the representation of the data
itself from a large amount of unlabeled data and only need
to fine-tune on a small amount of labeled data. So that the
downstream tasks can better learn their own features and the
required knowledge.At the same time, pre-training methods are
also widely used in network communication scenarios, and[12,
13, 14] proposed the application of pre-training methods in
solving encrypted traffic classification problems. However,

Abstract—While packet encryption technology provides user
privacy protection, it also brings challenges to traffic classification. Traditional traffic classification technologies based on
packet fields or payload data content are becoming powerless
in the face of encrypted traffic. Although traffic encryption
technology can hide data content, it cannot change the inherent
characteristics of application traffic. Therefore, how to classify
encrypted traffic by mining traffic features has become a topic of
widespread concern. An enormous amount of research shows that
machine learning algorithms achieve good results in encrypted
traffic classification. However, there is still room for improvement.
For example, deep learning methods require a large amount of
labeled training data, and it is difficult for pre-trained models
to capture the associated features of long sequences of packet.
This paper propose a Bidirectional encrypted traffic classification
model based on BERT and BiLSTM(Bi-ETC), by inserting
[CLS]Token at the connection of Token sequence between BERT
and BiLSTM, strengthens BiLSTM’s focus on packet-level features while maintaining BilSTM’s capture of Token sequence
context. Experimental results show that the Bi-ETC model is
superior to all proposed classification methods on the ISCX VPN
dataset, reaching 99.43%in F1 score and 99.7%in accuracy.
Index Terms—Privacy Protection, Network communication
security, Encrypted traffic classification, BERT, BiLSTM

I. I NTRODUCTION
In recent years, with the widespread need to protect data
transmission and user privacy, protocols and applications are
more inclined to adopt encryption methods. Therefore, how to
realize the accurate identification of network encrypted traffic
is an important issue in the field of cyberspace security, and is
also the focus of current network behavior analysis, network
planning and construction, network anomaly detection and
network traffic model research[1]. Encrypted traffic is growing
in a large number of current communication networks, and a
variety of encryption protocols have been used[2], such as
IPSec, SSL/TLS, SSH, Bitorrent, Skype, etc. Different encrypted protocol packets are also located in different network
*Corresponding author

979-8-3503-3103-5/23/$31.00 ©2023 IEEE
DOI 10.1109/DSC59305.2023.00037

197

Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:11:11 UTC from IEEE Xplore. Restrictions apply.

current research cannot capture the long-distance contextual
relationships in encrypted traffic Token sequences. In this
paper, we propose to use Bi-ETC for encrypted traffic classification tasks, which can not only capture the long-distance
contextual relations in traffic sequences, but also enhance
the model’s attention to traffic semantic features.The specific
contributions of this paper can be summarized as follows:
• According to the state of art we know we first propose to use the BiLSTM(Bidirectional Long Short
Term) model in encrypted traffic classification to
capture the long-distance dependencies well between
the BERT(Bidirectional Encoder Representations from
Transformers) output Token sequence features.
• we propose to insert packet-level [CLS]Token semantic
features at the forward and backward starting positions of
BiLSTM, so as to enhance BiLSTM’s attention to packetlevel features.
• Experiments show that our method achieves excellent results on publicly available encrypted traffic classification
datasets, and outperforms eleven state-of-the-art models
in terms of precision, recall, and F1-score.
The rest of this paper is organized as follows. In Section II,
we review some of the most important and recent research
on traffic classification. In Section III, we introduce the
motivation and objective of the model. Section IV introduces
our proposed method, namely Bi-ETC. In Section V, the
experimental results and application identification performance
are analyzed. Finally, we conclude the paper in Section VI.

time-series network traffic through a RNN(recurrent neural
network) and introduced an attention mechanism. Ren et
al.[26] proposed a tree-structured recurrent neural network
(tree-RNN), setting a specific classifier for each small classification. Liu et al.[9] proposed Flow Sequence Network(FSNet), which can deeply mine the latent sequence features of
flows, and introduced a reconstruction mechanism that can
improve feature effectiveness .
PERT[12] uses the state-of-art dynamic word embedding
technique to perform automatic traffic feature extraction and
provides a traffic classification framework in which unlabeled
traffic is used to pre-train an encoding network that learns
the contextual distribution of traffic payload bytes. Then,
the pre-trained network is reused for downward classification
to obtain the enhanced classification results. CBD[26] has
the generalization ability to classify encrypted traffic in the
real environment, and the overall structure of CBD can be
described as the encoder of a one-dimensional CNN and a
Transformer. The model classifies encrypted traffic from the
packet level and the traffic level. ET-BERT[13] pre-trains
deep contextualized datagram level representations from largescale unlabeled data, and the pre-trained model can finetune on a small amount of task-specific labeled data. ETBERT can effectively learn implicit relationships in unlabeled
traffic, thereby improving the effect of traffic classification in
different scenarios. Compared with ET-BERT[13], BFCN[14]
captures byte-level local features in traffic through convolution
operation.

II. R ELATED W ORK

III. M OTIVATION AND O BJECTIVE

In recent years, network traffic classification has become a
research hotspot in academia and industry[15]. With the rapid
growth of encrypted traffic in the network, traditional traffic
classification methods based on ports[16] and deep packet
inspection[17] can no longer meet the current requirements.
Machine learning has been widely used for identification
and classification of encrypted traffic, and FlowPrint[18] is a
semi-supervised method for fingerprinting mobile applications
from encrypted network traffic. AppScanner[19] utilizes the
statistical characteristics of packet size to train a random forest
classifier, while BIND[20] also utilizes statistical characteristics of temporality .
Recently, Aceto et al.[21] proposed a method combining
the advantages of deep learning and big data to solve the
problem of network traffic classification. Rezaei et al.[22]
outlined a general framework for deep learning-based traffic
classification , and introduced commonly used deep learning
methods and their applications in traffic classification tasks.
Traffic classification based on deep learning can be traced
back to 2015[23], where Wang et al. used a simple SAE
autoencoder. Lotfollahi et al.[8] , after an initial preprocessing
stage of the data, feed packets into a deep packet framework
that embeds stacked autoencoders and convolutional neural
networks to classify network traffic . Zeng et al.[24] proposed
a novel DL-based framework capable of classifying encrypted
traffic and detecting malware traffic. Yao et al.[25] modeled

Recently, pre-training has also been introduced into encrypted traffic classification[12, 13, 14] and achieved excellent
performance on multiple datasets. However, [12] lacks pretraining tasks designed for traffic and reasonable input to show
the effect of pre-training models. [13] can better represent encrypted traffic, but cannot capture the relationship between encrypted traffic Tokens. [14] Reasonable use of CNN to capture
the relationship between encrypted traffic Tokens, but cannot
capture long-distance contextual relationships from encrypted
traffic Token sequences. In encrypted traffic classification,
although the payload has no semantics, Sengupta et al.[27]
proposed that the randomness difference between different
ciphertexts can be used to distinguish different applications,
which shows that encrypted traffic is not completely random,
and there is an implicit pattern . Therefore, we need to use
the BERT module to extract the implicit features of encrypted
traffic and obtain the feature vector of each encrypted traffic
Token. And because the extracted feature vector of each
encrypted traffic Token has the same timing relationship as
the original encrypted traffic sequence, in order to solve
the problem of timing relationship in the encrypted traffic
sequence, this paper introduces the BiLSTM model based on
the BERT pre-training model. Due to the long byte sequence of
the data packet, the BiLSTM model alleviates the problem of
gradient disappearance and gradient explosion compared with
the traditional RNN. The ability to model the global context

198
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:11:11 UTC from IEEE Xplore. Restrictions apply.

of data. Therefore, by using BiLSTM, we can better process
sequence data and capture contextual semantic features and
timing features between Token feature representations.

TABLE I
DATASET LABEL

IV. M ETHODOLOGY
A. Data Pre-processing
In order to improve data quality and improve training
efficiency, we will first filter out retransmission and out-ofsequence data packets and network query data packets (eg,
ICMP, DNS, etc.), and only keep IP data packets. Because retransmissions and out-of-sequence packets are usually caused
by abnormal network transmissions, they may distort traffic
patterns and affect classification accuracy[8]. By removing
these packets, you can ensure more accurate and consistent
traffic patterns in your training and test datasets. However,
network query data packets are usually caused by network
requests such as domain name resolution, advertisement tracking, and statistical analysis, and they have nothing to do with
the purpose of traffic classification. Retaining only IP packets
can reduce the size of the data set and reduce unnecessary
processing and analysis during training and testing, thereby
improving efficiency.
Since our approach does not rely on any visible plaintext
information, we will only intercept the transport layer payload
of each packet and discard the rest (e.g., Ethernet headers, IP
headers, transport layer headers, etc.). The payload is then
converted to hexadecimal encoding for processing to ensure
data consistency and commonality, and to avoid character
encoding issues. Then, the hexadecimal payload is encoded by
the bi-gram model, which is converted into a Token sequence
to help capture the context between adjacent bytes.
1) labeling dataset
as mentioned in the previous section, the pcap files in the
dataset are labeled based on the application and the network
activity of the application, so in order to identify the application type, we need to redefine the label. We redefined the pcap
files collected during VPN sessions into 17 label categories, as
shown in Table 1 below. Then, a maximum of 5000 samples
were selected from each type of data, among which the number
of samples in AIM Chat and ICQ categories were 1340 and
823, respectively, to test the effect of our method on the
label imbalanced data set. Finally, we divided the dataset into
training, validation and testing datasets according to the ratio
of 8:1:1.

label

class

count

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

AIM Chat
Email
Facebook
Gmail
Hangout
ICQ
Netflix
SCP
Skype
Spotify
Tor
Torrent
Vimeo
VoipBuster
VPN-FTPS
VPN-SFTP
Youtube

1340
5000
5000
5000
5000
823
5000
5000
5000
5000
5000
5000
5000
5000
5000
5000
5000

label is introduced. By learning to model the semantic correlation between the representation of this special Token
label and the entire encrypted traffic Token sequence, the
BERT model obtains a feature vector representing the entire
encrypted traffic packet. Therefore, the features extracted by
the [CLS]Token label can be considered as the features that
represent the whole packet level and are the most classification
meaningful features. Similarly, other ordinary encrypted traffic
Token sequences have also been extracted with corresponding
features by BERT. In addition, although BiLSTM performs
better than LSTM(Long Short Term Memory networks) and
traditional RNN models on long sequences, there is still the
phenomenon of forgetting [28]. Therefore, the [CLS]Token
sequence of the head is copied to the end of the BiLSTM
input sequence, and for both forward and backward LSTM,
the [CLS]Token feature can be recalled again at the end of
the sequence to alleviate the forgetting of the most important
packetlevel feature information. Moreover, this can better
capture the effective classification features in the [CLS]Token
to achieve the purpose of accurate classification. In addition,
we adopt the dropout technique for the output of BiLSTM,
which reduces the complexity and capacity of the neural
network by randomly setting the output of some neurons to
zero during the training process, thereby reducing the risk of
overfitting.Finally, we concatenate the output features of the
last layer of the forward and backward LSTM as the final
classification features and put them into the SoftMax network
for classification to obtain the final classification target.
It is worth mentioning that in the experimental part, we
did two ablation experiments to verify the performance of
the model. First, compare the accuracy and loss of the two
strategies whether to insert [CLS]Token at the end of the

B. Model architecture
In this section, we will explain our proposed Bi-ETC,
whose network structure is shown in Figure 1 below. The
model mainly consists of a feature extraction module based
on BERT and one based on BiLSTM. The model is composed
of the up-down sequence text encoding module of Memory.
Specifically, we first input the pre-processed encrypted traffic
tokens into BERT, and use the BERT feature extraction module
to extract the token-level features of encrypted traffic. And
before each encrypted traffic Token sequence, the [CLS]Token

199
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:11:11 UTC from IEEE Xplore. Restrictions apply.

BERT

BiLSTM
LSTM
TN[cls]

CLS

E[CLS]

T [cls]
N

LSTM
TN781d

781d

E781d

T 781d

LSTM

T 1dc3
N

LSTM
TNc35f

...

...

...

Ef302

...

...

LSTM

N

...

...
f302

T c35f

...

Ec35f

LSTM

TNf302

T f302

SoftMax

E1dc3

c35f

LSTM

N

TN1dc3

1dc3

LSTM

LSTM

LSTM

N

LSTM
TN[cls]

LSTM

Fig. 1. Architecture of Bi-ETC model.

hidden layers are combined to obtain the feature vector H at
the end of the set. Then, the feature vector H is transferred to
a fully connected layer with PReLU function to classify the
encrypted traffic.

BiLSTM input sequence to verify the advantages of the model.
Second, the effects of two different activation functions, tanh
and PReLU, on the output features of BiLSTM were compared in SoftMax to verify the advantages of PReLU in this
classification task.
Corresponding to TN [cls] , TN [781d] , TN [1dc3] , · · · , including [CLS]) trained by BERT’s hidden layer by a learnable
weight.Wa ∈ Rda ×n as the input of the BiLSTM pattern. The
formula is as follows:
ai = g1 (Wa Ci + ba )

V. E XPERIMENTS AND R ESULT A NALYSIS
A. Dataset Selection
In network traffic classification, datasets and evaluation
criteria are not consistent. Many researchers use private selfgenerated datasets for verification. Although self-generated
datasets are relatively easy to obtain label information, their
own use of self-generated datasets causes the problem that
different algorithms cannot be compared. Therefore, in this
paper, we choose the ISCX VPN dataset published by the
University of New Brunswick [29].
This dataset divides network packets captured at the data
link layer into different pcap files based on the application
they were generated using (e.g., Gmail, Skype, Facebook, etc.)
and the different activities performed by the application during
network communication (e.g., chat, file transfer, or video call,
etc.).

(1)

where 1 ≤ i ≤ n, n denotes the dimension of the feature
vector output after fine-tuning of the BERT model,ai ∈ Rda
is the input vector of the BiLSTM layer, ba is the offset vector
of dimension da . Here, we adopt Sigmoid as the activation
function g1 .
The ordinary LSTM model calculates the one-way hidden
layer sequence h, while BiLSTM calculates the forward hid→
−
den layer vector as hi and the backward hidden layer vector
←
−
as hi and finally combines the two for output vector vi. The
calculation formula is as follows:
→
− ←
−
vi = hi + hi
(2)

B. Evaluation Metrics
We used four evaluation metrics: precision(Pc ), recall(Rc ),
F1 score(F 1c ), and accuary(acc). Since encrypted traffic
classification is a multi-category task, we need to calculate
the above metrics for each category separately. Specially,
we use N as the total number of training samples; T Pc
to indicate the quantity that originally belongs to category
c, and is predicted by the model as c; F Pc indicates the
quantity that originally does not belong to category c, but
is predicted by the model as c; T Nc indicates the quantity
that does not belong to category c, and is not predicted to be

In addition, the hidden layer of the model as follows:

hdi = g2 Whd ai + U hdi−1 + bdh
(3)
Where Whd ai ∈ Rdh ×da is the weight matrix of ai , d ∈ {0, 1}
represents two different directions in the hidden layer, and U
is the weight matrix of the output sequence hd of the hidden
layer at time i. hdi−1 corresponds to the hidden layer output
sequence at the previous time i − 1; bh represents the offset
vector in the d direction. Then, the output sequences bdh of all

200
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:11:11 UTC from IEEE Xplore. Restrictions apply.

TABLE II
C OMPARISON WITH S TATE - OF - THE - ART M ETHODS .

Method

Accuary

Precision

Recall

F1-Score

FlowPrint[18]

0.8767

0.6697

0.6651

0.6531

AppScanner[19]
BIND[20]

0.6266
0.6767

0.4864
0.5152

0.5198
0.5153

0.4935
0.4965

DF[r32]
FS-Net[9]
Tree-RNN[26]
Deep Packet[8]

0.6116
0.6647
0.9898
0.9758

0.5706
0.4819
0.9898
0.9785

0.4752
0.4848
0.9897
0.9745

0.4799
0.4737
0.9852
0.9765

PERT[12]
CBD[28]
ET-BERT(flow)[13]
ET-BERT(packet)[13]
BFCN[14]

0.8229
0.8388
0.8519
0.9962
0.9965

0.7092
0.8849
0.7508
0.9936
0.9936

0.7173
0.8381
0.7294
0.9947
0.9947

0.6992
0.8397
0.7306
0.9941
0.9941

Bi-ETC

0.9970

0.9934

0.9951

0.9943

class c; F Nc indicates the quantity that it belongs to class
F Nc , but is misclassified to other class. Hence, the definition
of aforementioned four evaluation metrics can be given by
Pc =

T Pc
T Pc + F Pc

(4)

Rc =

T Pc
T Pc + F Nc

(5)

2Pc Rc
Pc + Rc

(6)

T Pc + T Nc
T Pc + T Nc + F Pc + F Nc

(7)

F 1c =
acc =

tures well, can successfully distinguish each application, and
outperforms other models on the ISCX VPN dataset.Moreover,
the overall performance of the proposed model is higher
improved compared to previous models due to the following
two reasons.
• After BERT extracts the general features of the encrypted
traffic, use the hidden layer state of BiLSTM to record the
relevant feature information of the front and rear Token
sequences, so as to learn the long-distance dependencies
in the Token sequences.
• By simultaneously inserting packet-level Token semantic
features at the forward and backward starting positions of
BiLSTM, this helps the BiLSTM model capture packetlevel features and contextual relationships.
3) Controlled Experiment
1. BERT-BiLSTM VS. BERT-FFNN VS. BERT-LSTM
In our experiments, we use two control models:
(1) BERT-FFNN: This model is the pre-trained model for
our experiments [5] and employs BERT-Feed forward neural
networks (FFNN), which can provide a benchmark to evaluate
the performance of our model in capturing the contextual
sequence features of encrypted traffic tokens.
(2) BERT-LSTM: In order to verify the superiority of
BiLSTM forward learning and backward learning, we choose
BERT-LSTM as another control experimental model.
Since BERT-FFNN is the model selected in our pre-training
stage, and ISCX VPN dataset is also used in the pre-trained
large-scale unlabeled dataset. Therefore, at the beginning,
the model parameters of BERT-FFNN have fallen within a
good performance range. However, after the ninth epoch, we
observe that the model has reached the convergence point,
the Accuracy basically does not change, and the improvement
of the model performance by further training is no longer
significant. On the contrary, continued training may lead to

C. Experimental setup and result analysis
1) Implementation details
This experiment was performed with eight Tesla T4 Gpus.
The model parameters are set as follows: We set the number
of epochs to 15, the initial learning rate to 2×10-5, and
dynamically adjust the learning rate with the training process,
the ratio of warmup is set to 0.1, the batch size is set to 32,
and the dropout is set to 0.1. BERT input sequence length is
set to 128, BERT hidden size and BiLSTM hidden size are set
to 768, BiLSTM layer number is set to 2, and cross-entropy
loss function is used for loss calculation. AdamW was used
as the optimizer.
2) Comparison with State-of-the-art Methods
We compare the proposed Bi-ETC model with various stateof-the-art methods, including (1) fingerprint-based construction method: FlowPrint; (2) machine learning-based methods:
AppScanner, BIND; (3) Deep learning-based methods: DF,
FS-Net, Tree-RNN, Deep Packet; (4) Based on pre-training
methods: PERT, CBD, ET-BERT, BFCN.
According to the experimental results in Table 2, the proposed Bi-ETC model can extract and learn discriminative fea-

201
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:11:11 UTC from IEEE Xplore. Restrictions apply.

with the highest accuracy. This is because, for the lookahead
LSTM sequence, the sequence captures the most important
[CLS]Token feature sequence very early; For the backward
LSTM sequence, if we do not copy the [CLS]Token sequence
of the head to the end of the entire feature sequence, then
the backward LSTM sequence needs to be at the end to
extract the [CLS] feature sequence. So we consider inserting a
[CLS]Token feature sequence before and after the input vector
of the Bi-LSTM model. In other words, the output vector of
the one-before and one-after corresponding [CLS] in the last
hidden layer is used as the semantic feature representation
of all traffic, which helps the BiLSTM model to capture
the packetlevel features and context, and provides a more
comprehensive traffic classification representation.
2.tanh VS. PReLU
In this experiment, we selected two activation functions
for comparison. The first time we use tanh as the activation
function, the curves of tanh and sigmoid function are relatively
similar, the difference is the output interval, the output interval
of tanh is between (-1,1), and the whole function is centered
at 0. However, using tanh function as the activation function
in the BiLSTM model itself has the problem of gradient
disappearance. PReLU scales each negative element value
by a factor, which not only plays the role of nonlinear
transformation, but also uses a different scaling factor for each
channel on the negative axis, which plays a role similar to
the attention mechanism. The output vector of Bi-LSTM is
fed into a classifier with PReLU as the activation function to
obtain the final prediction result.

Fig. 2. Comparison of accuracy and loss values in control experiments.

overfitting. This observation suggests that further tuning the
model or exploring other optimization strategies may be a
more promising avenue to improve performance.
Since BERT-FFNN only inputs [CLS]Token features extracted by BERT into FFNN for classification, there are a lot of
Token features left unclassified, while BERT-bilSTM can capture complex patterns between tokens. To prevent overfitting,
we use dropout technique, so the accuracy fluctuates during
the period, but finally surpasses BERT-FFNN. BERT-LSTM,
on the other hand, forgets the most important [CLS] packetlevel features and thus performs even worse than FFNN.
4) Ablation Experiment
We conducted two ablation experiments on Bi-LSTM to
verify the feasibility and advantages of the Bi-ETC.
1. [CLS]-tokens-[CLS] VS. [CLS]-tokens;
(1) [CLS]-tokens-[CLS] : This is the approach described in
Bi-ETC, where the sequence of [CLS]tokens in the head is
copied to the end of the BiLSTM input sequence.
(2) [CLS]-tokens: It is all sequence features extracted by
BERT, including [CLS]token and all encrypted traffic token
sequences after it, and input them all into BiLSTM.
We observe that our Loss decreases faster and we end up

Fig. 4. Comparison of accuracy and loss values using different activation
functions tanh and PReLU.

5) Performance of different application recognition tasks
Table 3 shows the performance achieved by different models
on the application recognition task on the test set. We chose
two effect pre-trained models ET-BERT [5] and BFCN [6]
to compare with Bi-ETC on application task recognition. We
have achieved the best results in Precision, Recall, and F1 on
most of the classification samples, and we have also achieved
good recognition results on the 823 ICQ small samples.
Bi-ETC is able to make more comprehensive use of the
information in the packet in the encrypted traffic classification

Fig. 3. Comparison of accuracy and loss values between [CLS]-token and
[CLS]-token-[CLS].

202
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:11:11 UTC from IEEE Xplore. Restrictions apply.

TABLE III
P ERFORMANCE COMPARISON OF B I -ETC WITH ET-BERT AND BFCN IN THE APPLICATION IDENTIFICATION TASK .

Ours

Class
AIM Chat
Email
Facebook
Gmail
Hangout
ICQ
Netflix
SCP
Skype
Spotify
Tor
Torrent
Vimeo
VoipBuster
VPN-FTPS
VPN-SFTP
Youtube

ET-BERT

BFCN

Precision

Recall

F1-Score

Precision

Recall

F1-Score

Precision

Recall

F1-Score

0.978
0.994
0.998
0.992
0.996
0.941
1.000
1.000
0.996
1.000
1.000
0.994
1.000
1.000
1.000
1.000
1.000

0.978
1.000
0.992
0.998
0.996
0.976
1.000
0.994
0.996
1.000
1.000
1.000
1.000
0.990
1.000
0.998
1.000

0.978
0.997
0.995
0.995
0.996
0.958
1.000
0.997
0.996
1.000
1.000
0.997
1.000
0.995
1.000
0.999
1.000

0.997
0.994
0.996
0.986
0.996
0.920
1.000
1.000
0.998
1.000
1.000
0.992
1.000
1.000
1.000
1.000
1.000

0.970
1.000
0.984
0.994
0.998
0.976
1.000
0.994
0.998
1.000
1.000
1.000
1.000
0.998
1.000
0.998
1.000

0.974
0.997
0.990
0.990
0.997
0.947
1.000
0.997
0.998
1.000
1.000
0.996
1.000
0.994
1.000
0.999
1.000

0.992
0.994
0.992
0.986
1.000
0.941
1.000
1.000
0.994
1.000
1.000
0.992
1.000
1.000
1.000
1.000
1.000

0.978
1.000
0.990
0.994
0.996
0.976
1.000
0.994
0.998
1.000
1.000
0.998
1.000
0.998
1.000
0.998
1.000

0.985
0.997
0.991
0.990
0.998
0.958
1.000
0.997
0.996
1.000
1.000
.0995
1.000
0.994
1.000
0.999
1.000

features, thereby improving the performance and robustness of
the model.

task, and is able to consider the context of each tag, helping
us to better understand and distinguish between different types
of applications.
In addition, the confusion matrix is usually applied to
validate the results of the classification, to observe the performance of Bi-ETC on various categories, and to provide a
better diagram to understand how well Bi-ETC is working, the
performance confusion matrix of Bi-ETC is shown in Figure 8.
The dark elements on the main diagonal show that the Bi-ETC
model performs well on the classification of each application
with little confusion error.
VI. C ONCLUSION
In this paper, we introduce suitable BERT and BiLSTM
models, and propose a novel encrypted traffic feature extraction and traffic classification method to solve the problem that
pre-trained models are difficult to capture long-distance dependencies between traffic sequence features. In Bi-ETC, we use
BERT to generate feature representations of encrypted traffic
tokens, and capture the contextual semantic features between
tokens by BiLSTM. Bi-ETC achieves satisfactory performance
on the widely used ISCX-VPN dataset, with an F1 score of
99.43% and an accuracy of 99.7% respectively. In the future,
we will further expand and deeply study the scope of encrypted
traffic data to mine more traffic feature representations. We
plan to apply our method to more traffic classification tasks
to evaluate its generality and effect on different scenarios
and datasets. In addition, we plan to introduce an attention
mechanism on the output of BiLSTM to assist and enhance
the classification effect. Such an attention mechanism can
make the model pay more attention to important tokens and

Fig. 5. Confusion matrix for TETBB model performance.

ACKNOWLEDGMENT
This work was supported in The Major Key Project of
PCL (Grant No. PCL2022A03),the National Key Research
and Development Program of China (2021YFB2012402),The
National Natural Science Foundation of China (Grant
No. 61976064).Corresponding author: Ning Hu (e-mail:
hun@pcl.ac.cn)

203
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:11:11 UTC from IEEE Xplore. Restrictions apply.

R EFERENCES
[1]

[2]

[3]

[4]

[5]

[6]

[7]

[8]

[9]

[10]

[11]

[12]

[13]

[14]

[15]

Keke Gai, Meikang Qiu, and Hui Zhao. “Privacypreserving data encryption strategy for big data in
mobile cloud computing”. In: IEEE Transactions on Big
Data 7.4 (2017), pp. 678–688.
Liangchen Chen et al. “Research status and development trends on network encrypted traffic identification”.
In: Netinfo Secur.(03) (2019), pp. 19–25.
Fannia Pacheco et al. “Towards the deployment of
machine learning solutions in network traffic classification: A systematic survey”. In: IEEE Communications
Surveys & Tutorials 21.2 (2018), pp. 1988–2014.
Alberto Dainotti, Antonio Pescape, and Kimberly C
Claffy. “Issues and future directions in traffic classification”. In: IEEE network 26.1 (2012), pp. 35–40.
Soheil Hassas Yeganeh et al. “Cute: Traffic classification using terms”. In: 2012 21st International Conference on Computer Communications and Networks
(ICCCN). IEEE. 2012, pp. 1–9.
Vincent F Taylor et al. “Robust smartphone app identification via encrypted network traffic analysis”. In: IEEE
Transactions on Information Forensics and Security
13.1 (2017), pp. 63–78.
Khaled Al-Naami et al. “Adaptive encrypted traffic
fingerprinting with bi-directional dependence”. In: Proceedings of the 32nd Annual Conference on Computer
Security Applications. 2016, pp. 177–188.
Mohammad Lotfollahi et al. “Deep packet: A novel
approach for encrypted traffic classification using deep
learning”. In: Soft Computing 24.3 (2020), pp. 1999–
2012.
Chang Liu et al. “Fs-net: A flow sequence network for
encrypted traffic classification”. In: IEEE INFOCOM
2019-IEEE Conference On Computer Communications.
IEEE. 2019, pp. 1171–1179.
Jacob Devlin et al. “Bert: Pre-training of deep bidirectional transformers for language understanding”. In:
arXiv preprint arXiv:1810.04805 (2018).
Alexey Dosovitskiy et al. “An image is worth 16x16
words: Transformers for image recognition at scale”.
In: arXiv preprint arXiv:2010.11929 (2020).
Hong Ye He, Zhi Guo Yang, and Xiang Ning Chen.
“PERT: Payload encoding representation from transformer for encrypted traffic classification”. In: 2020 ITU
Kaleidoscope: Industry-Driven Digital Transformation
(ITU K). IEEE. 2020, pp. 1–8.
Xinjie Lin et al. “Et-bert: A contextualized datagram
representation with pre-training transformers for encrypted traffic classification”. In: Proceedings of the
ACM Web Conference 2022. 2022, pp. 633–642.
Zhaolei Shi et al. “BFCN: A Novel Classification
Method of Encrypted Traffic Based on BERT and
CNN”. In: Electronics 12.3 (2023), p. 516.
Petr Velan et al. “A survey of methods for encrypted
traffic classification and analysis”. In: International

[16]

[17]

[18]

[19]

[20]

[21]

[22]

[23]

[24]

[25]

[26]

[27]

[28]

[29]

Journal of Network Management 25.5 (2015), pp. 355–
374.
Alberto Dainotti, Antonio Pescape, and Kimberly C
Claffy. “Issues and future directions in traffic classification”. In: IEEE network 26.1 (2012), pp. 35–40.
Justine Sherry et al. “Blindbox: Deep packet inspection
over encrypted traffic”. In: Proceedings of the 2015
ACM conference on special interest group on data
communication. 2015, pp. 213–226.
Thijs Van Ede et al. “Flowprint: Semi-supervised
mobile-app fingerprinting on encrypted network traffic”.
In: Network and Distributed System Security Symposium
(NDSS). Vol. 27. 2020.
Vincent F Taylor et al. “Robust smartphone app identification via encrypted network traffic analysis”. In: IEEE
Transactions on Information Forensics and Security
13.1 (2017), pp. 63–78.
Khaled Al-Naami et al. “Adaptive encrypted traffic
fingerprinting with bi-directional dependence”. In: Proceedings of the 32nd Annual Conference on Computer
Security Applications. 2016, pp. 177–188.
Giuseppe Aceto et al. “Know your big data trade-offs
when classifying encrypted mobile traffic with deep
learning”. In: 2019 Network traffic measurement and
analysis conference (TMA). IEEE. 2019, pp. 121–128.
Shahbaz Rezaei and Xin Liu. “Deep learning for encrypted traffic classification: An overview”. In: IEEE
communications magazine 57.5 (2019), pp. 76–81.
Zhanyi Wang. “The applications of deep learning on
traffic identification”. In: BlackHat USA 24.11 (2015),
pp. 1–10.
Yi Zeng et al. “Deep − F ull − Range: a deep learning
based network encrypted traffic classification and intrusion detection framework”. In: IEEE Access 7 (2019),
pp. 45182–45190.
Haipeng Yao et al. “Identification of encrypted traffic
through attention mechanism based long short term
memory”. In: IEEE transactions on big data 8.1 (2019),
pp. 241–252.
Xinming Ren, Huaxi Gu, and Wenting Wei. “TreeRNN: Tree structural recurrent neural network for network traffic classification”. In: Expert Systems with
Applications 167 (2021), p. 114363.
Redvan Ghasemlounia et al. “Developing a novel framework for forecasting groundwater level fluctuations using Bi-directional Long Short-Term Memory (BiLSTM)
deep neural network”. In: Computers and Electronics in
Agriculture 191 (2021), p. 106568.
Xinyi Hu et al. “CBD: A deep-learning-based scheme
for encrypted traffic classification with a general pretraining method”. In: Sensors 21.24 (2021), p. 8231.
Payap Sirinam et al. “Deep fingerprinting: Undermining
website fingerprinting defenses with deep learning”.
In: Proceedings of the 2018 ACM SIGSAC Conference on Computer and Communications Security. 2018,
pp. 1928–1943.

204
Authorized licensed use limited to: Montana State University Library. Downloaded on November 20,2024 at 08:11:11 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
