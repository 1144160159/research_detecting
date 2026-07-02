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
# [325] WF-Transformer: Learning Temporal Features for Accurate Anonymous Traffic Identification by Using Transformer Networks
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
编号：325
题名：WF-Transformer: Learning Temporal Features for Accurate Anonymous Traffic Identification by Using Transformer Networks
年份：2023
DOI：10.1109/tifs.2023.3318966
来源：IEEE Transactions on Information Forensics and Security
PDF：paper/10.1109_TIFS.2023.3318966.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测、时序、日志、KPI 与云原生异常检测
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\325.txt
- 原始字符数：73253
- 本次发送字符数：73253
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
30

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

WF-Transformer: Learning Temporal Features for
Accurate Anonymous Traffic Identification by
Using Transformer Networks
Qiang Zhou , Liangmin Wang , Member, IEEE, Huijuan Zhu , Member, IEEE, Tong Lu,
and Victor S. Sheng , Senior Member, IEEE
Abstract— Website Fingerprinting (WF) is a network traffic
mining technique for anonymous traffic identification, which
enables a local adversary to identify the target website that an
anonymous network user is browsing. WF attacks based on
deep convolutional neural networks (CNN) get the state-of-the-art
anonymous traffic classification performance. However, due to the
locality restriction of CNN architecture for feature extraction on
sequence data, these methods ignore the temporal feature extraction in the anonymous traffic analysis. In this paper, we present
Website Fingerprinting Transformer (WF-Transformer), a novel
anonymous network traffic analysis method that leverages Transformer networks for temporal feature extraction of traffic traces
and improves the classification performance of Tor encrypted
traffic. The architecture of WF-Transformer is specially designed
for traffic trace processing and can classify anonymous traffic effectively. Furthermore, we evaluate the performance of
WF-Transformer in both closed-world and open-world scenarios.
In the closed-world scenario, WF-Transformer attains 99.1%
accuracy on Tor traffic without defenses, better than stateor-the-art attacks, and archives 92.1% accuracy on the traces
defended by WTF-PAD method. In the open-world scenario, WFTransformer has better precision and recall on both defended
and non-defended traces. Furthermore, WF-Transformer with a
short input length (2000 cells) outperforms the DF method with
a long input length (5000 cells).
Index Terms— Website fingerprinting, traffic
encrypted communication, transformer networks.

analysis,

I. I NTRODUCTION

W

ITH the development of Internet, privacy disclosure
of network users is an urgent problem for network

Manuscript received 17 December 2022; revised 23 June
2023 and 1 September 2023; accepted 11 September 2023. Date of publication
25 September 2023; date of current version 16 November 2023. This work
was supported in part by the National Natural Science Foundation of China
under Grant 62372105 and Grant 62272204, in part by the Leading-Edge
Technology Program of the Jiangsu Natural Science Foundation under Grant
BK20202001, and in part by the Natural Science Foundation of the Jiangsu
Higher Education Institutions of China under Grant 23KJB520004. The
associate editor coordinating the review of this manuscript and approving
it for publication was Dr. Grigorios Loukides. (Corresponding authors:
Qiang Zhou; Liangmin Wang.)
Qiang Zhou, Huijuan Zhu, and Tong Lu are with the School of Computer Science and Communication Technology, Jiangsu University, Zhenjiang
212013, China (e-mail: zhouqiang@ujs.edu.cn; huijuanzhu@ujs.edu.cn;
lutong@stmail.ujs.edu.cn).
Liangmin Wang is with the School of Cyber Space and Security Engineering, Southeast University, Nanjing 211189, China (e-mail:
liangmin@seu.edu.cn).
Victor S. Sheng is with the Department of Computer Science, Texas Tech
University, Lubbock, TX 79409 USA (e-mail: victor.sheng@ttu.edu).
Digital Object Identifier 10.1109/TIFS.2023.3318966

security. Last decades, several anonymous communication systems have been designed and developed for the users‘ privacy
protection [1]. Tor (or The Onion Router) is a popular low
latency anonymous network, and has more than three million
daily users [2]. Latest studies have shown traffic mining
algorithm called Website Fingerprinting (WF) technique can
destroy the anonymity of the Tor [3]. Since the different add-in
and content of different websites, there is a specific pattern
of traffic encrypted through an anonymous network system,
which can be used for determining the destination of the target
website based on the collected traces [4], [5], [6], [7], [8], [9].
Network attackers eavesdrop and collect the network traffic
passively when a user visits the target website. WF attackers
use the features that are calculated from the network traffic
traces, such as packet rates [10], directions of packets [7] and
inter-arrive time [11], and then a classifier is trained for the
classification of anonymous traces.
The pioneering WF attacks are mainly focusing on the handcrafting feature extraction of the anonymous traces and the
selection of classifiers [10], [11], [12], [13], [14]. Wang et al.
utilize several traffic features, such as packet direction, packet
size, and burst number, and then a k-NN classifier is trained for
the prediction of target traces [11]. Panchenko et al. propose
a WF attack method named CUMUL [13], which calculates a
novel feature set with a cumulative behavioral representation
of the collected traffic traces and utilizes Support Vector
Machine (SVM) as the classifier. Hayes et al. propose a
k-FP method for WF attack [14], which utilizes a random
forest to rank the importance of different traffic features
and then uses k-NN classifier to predict the labels of target
traffic traces. These three WF attack methods achieve about
91% classification accuracy for Tor anonymous traffic trace
classification in the closed-world setting.
With the development of WF attack methods, several
defense methods have been proposed [15], [16], [17], [18],
[19], [20]. Dyer et al. propose a WF defense method named
BuFLO [15], which pads a large number of dummy packets
into normal traffic traces to protect users’ privacy. Cai et al.
improve the BuFLO defense method and propose TAMARAW
[16]. TAMARAW sets a hyperparameter to restrict the number
of the padded dummy packets during the transmission process,
but the bandwidth overhead and the latency are still too high
to be implemented in a real network scenario. Juarez et al.
propose a lightweight defense method named WTF-PAD

1556-6021 © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

ZHOU et al.: WF-TRANSFORMER: LEARNING TEMPORAL FEATURES

[17], and the strategy of the WTF-PAD is that it only pads
dummy packets into the gaps between the real packets, which
decreases the bandwidth overhead efficiently, and has no delay.
However, with the development of deep learning techniques
[21], [22], [23], [24], [25], traffic data mining methods that
based on CNN network architecture and its variants are used
for traffic analysis [26], [27]. WF attacks based on deep
convolutional neural networks have been proposed [7], [28],
and existing defenses that padding dummy packets into normal
trace based on the statistical information of traces fail to
counter deep WF attacks [7], [29], [30]. Rimmer et al. test
multiple deep frameworks to classify the anonymous traffic
and get better performance than existing non-deep WF attack
methods [29]. Sirinam et al. utilize a more sophisticated
convolutional neural network to construct a deep WF model
called DF, and DF only uses the direction of the packets as
the input of the model. Both of the deep WF attack methods
achieve more than 96% classification accuracy [7].
Although the latest deep WF attack methods based on CNN
architecture have obtained a lot of progress in anonymous
traffic classification [7], [30], the design of existing deep WF
attacks based on CNN fails to extract the temporal feature of
the traces, which can be seen as the long-term dependence
among the cells of traffic traces. For example, one request is
sent to the server by the client, the response of the current
request may not be send back to the client immediately due
to the response of the former request is transmitting, and the
current request has been delayed, so the local features extract
by CNN fail to represent the patterns of the traces. CNN only
focuses on the local features of the traffic and fails to capture
the long-term dependence among the packets in a traffic trace,
which can make the discriminative patterns of the traffic traces
be ignored, and reduce the performance of the deep model on
the classification of anonymous traffic.
To tackle this problem, we present a novel anonymous
trace classification model called Website Fingerprinting Transformer (WF-Transformer). Unlike the existing deep WF attack
models, WF-Transformer utilizes Transformer network [24] to
extract the temporal feature of the traffic traces. Furthermore,
we propose a more sophisticated design on the network
architecture of Transformer and the corresponding optimization function, and make the proposed WF-Transformer more
suitable for processing traffic trace data. To demonstrate the
effectiveness and superiority of WF-Transformer, we conduct
extensive experiments on a public dataset and evaluate the performance of our method in both closed-world and open-world
scenarios. Considering the existing WF defense methods,
we also conduct experiments to show the effectiveness of our
method against WF defenses. To sum up, the contributions of
this paper can be summarized as follows:
1) We present WF-Transformer, a novel WF attack based
on Transformer network. To the best of our knowledge,
WF-Transformer is the first WF attack that utilizes
Transformer network to extract the temporal feature of
the traffic traces for traffic classification, and yields a
better performance than state-of-the-art CNN-based WF
attacks.

31

Fig. 1.

Demo of website fingerprinting attack.

2) We propose a more sophisticated design of Transformer
network for traffic analysis and corresponding optimization function. WF-Transformer shows two main
advantages. One is its shorter input than CNN-based
methods, which allows an adversary to save time in
traffic collection. The other is its fast convergence, which
helps to get a robust model.
3) We evaluate the effectiveness of WF-Transformer on
the public Tor dataset for both closed-world and openworld settings, and we also show the performance
of WF-Transformer on non-defended and defended
traces. Compared with the state-of-the-art methods, WFTransformer outperforms existing methods in terms of
classification accuracy in closed-world setting, TPR,
FPR, Precision and Recall for open-world setting.
4) We conduct experiments to show the information leakage of features extracted by WF-Transformer and
CNN-based model, respectively, and reveal the impact
of the Transformer architecture on feature extraction.
The study indicates that WF-Transformer can utilize
shorter traces to learn more information from traces than
CNN-based models with the help of extracted temporal
features, demonstrating the superiority and effectiveness
of Transformer architecture used for traffic analysis.
The rest of the paper is organized as follows. The threat
model about WF attacks is introduced in Section II. Related
works are shown in Section III. Preliminary knowledge
about Transformer network is introduced in Section IV. The
proposed method is shown in Section V. The evaluation
setting and experiment results are shown in Section VI and
Section VII, respectively. In Section VIII, we show different information leakage for different models. In Section IX,
we give some discussion about our proposed method, and we
conclude our work in Section X.
II. T HREAT M ODEL
Tor network is a popular low-latency anonymous system,
and encrypted packets are transmitted in Tor with multiple
proxies to protect the users’ privacy. Figure 1 shows the WF
attack scenario, and we can find that attackers are located
between the client and the entry node of Tor, and record the
traffic traces passively during the user is browsing the target
websites with Tor. Generally, the sequence of the packets
and time stamps of the trace can be collected, and several
handcrafting trace features can be calculated and the classifier
can be trained for the identification of the anonymous trace.
We formalize the WF attack scenario in this part. Generally,
WF attackers are located between the client and the entry node

32

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

of the Tor, and they can only record the transmitted packets
passively, which means that attackers can not drop, modify,
decrypt or delay the packets. Furthermore, the transmitted
packets are encrypted with different secret keys in different
proxy nodes of Tor. The plaintext information and IP of the
packets are invisible to attackers without packet decryption.
For the attacker, we assume that the identity of the client is
known by the attacker, and the goal of the attacker is to identify
the target websites that the user visits.
Closed-World and Open-World Scenario: To evaluate the performance of WF attack, there are two settings,
the closed-world setting and the open-world setting. For the
closed-world setting, the network users is assumed that they
can only access a finite set of websites, and the attacker
monitors these websites, and the classification of the anonymous trace is a supervised learning problem. However, this
assumption is considered unrealistic, because of the large
number of websites in the real-world that can be visited by
network users. Furthermore, the traffic traces collected by
attackers are limited under this setting. For the open-world
setting, which is more practical, Tor users can visit a large
number of websites while the attacker can only record a
limited of website traces. For a collected trace, attackers need
to identify whether the traffic is under monitored. If it is
monitored, similar to the closed-world setting, a classification
model is trained to identify the target website. The open-world
setting is a more complex problem compared with closedworld setting, the number of unmonitored websites is assumed
much greater than that of the monitored websites in closedworld setting.
III. R ELATED W ORKS
In this section, we give some surveys on the latest process
of WF attack. Considering the influence of WF defenses, the
related works are introduced in two parts, WF attacks and WF
defenses.
A. WF Attacks
With the wide application of anonymous network, lots
of WF attack methods have been proposed [7], [11], [13],
[14], [30], [31], [32], [33]. The pioneering attacks are mainly
non-deep WF attack methods, which extract the handcrafting
features from the collected traffic traces based on human
knowledge. Packet direction, packet rates and inter-arrive time
of packets are commonly used handcrafting features, and a
classifier is trained on these features to identify the target
websites of the traffic traces. Existing non-deep WF attack
methods aim at trace feature extraction and classifier selection,
and KNN and SVM are commonly used classifiers [11], [13],
[14], and these WF attack methods achieve 91% classification
accuracy in the closed-world setting.
Deep WF attacks aim at utilizing deep neural networks
for anonymous trace extraction automatically. Rimmer et al.
propose automated website fingerprinting (AWF) which utilizes deep neural networks to identify Tor traffic automatically
rather than manually engineering [29]. AWF has tried a lot
of state-of-the-art deep networks, such as SDAE, CNN, and

LSTM. With the help of deep learning techniques, AWF
achieves 96% classification accuracy on Tor traffic in closedworld setting. Sirinam et al.propose Deep Fingerprinting (DF)
to classify the anonymous traffic [7]. DF utilizes a CNN
network with a sophisticated design. DF only uses the direction
of packets as inputs, and an end-to-end training manner is
used for the training of the model. In closed-world setting,
DF can obtain 98% classification accuracy on non-defended
Tor traffic. As for the Tor traffic defended by WTF-PAD
method, DF can still achieve over 90% classification accuracy.
Bhat et al. propose Var-CNN method [30], which utilizes
deep techniques for large amounts of traffic classification.
Unlike prior deep WF attacks, VarCNN utilizes time stamp
and packet direction as network inputs, and obtains over
98% classification accuracy on Tor traffic [30]. Wang et al.
ensemble multiple CNN-based networks for the classification
of anonymous traffic [34], and get better performance in openworld scenario.
B. WF Defenses
With the development of WF attacks, several WF defenses
have been proposed [15], [17], [35], [36]. The prior defense
methods pad dummy packets into normal traces based on
statistical information of the Tor traffic to disturb the WF
attack classifiers. However, existing defenses, BuFLO [15] and
TAMARAW [16], pad too many dummy packets into normal
traces and cause high bandwidth overhead, and this makes
them impractical.
Several lightweight defenses have been proposed [17], [35],
[37]. Juarez et al. propose Website Traffic Fingerprinting Protection with Adaptive Defense (WTF-PAD), and WTF-PAD
builds a histogram of packet time from the collected Tor traces.
By sampling packet time from the histogram, WTF-PAD only
pads dummy packets into the gaps of the normal trace, which
reduces the bandwidth overhead. However, WF attacks based
on deep learning techniques, such as DF method, still can
classify the traffic traces defended by WTF-PAD. Gong et al.
propose a lightweight defense called FRONT [35]. FRONT
only pads the front portion of Tor traces, which is a feature-rich
part of a traffic trace. With similar bandwidth overhead,
FRONT gets better performance than WTF-PAD.
Deep classifiers are vulnerable to adversarial examples
[38], [39], and several WF defense methods based on adversarial training manners are proposed for against deep WF
attacks. Rahman et al. propose Mockingbird method for WF
defense, which generates traces by moving the traffic traces
randomly and not following more predictable gradients [40].
Abusnaina et al. propose a Deep Fingerprinting Defender
(DFD) against deep WF attacks. DFD injects dummy packets
within every burst of Tor traces to generate adversarial traffic
traces [41].
IV. P RELIMINARY
Our proposed WF-Transformer utilizes a Transformer network for the traffic temporal feature extraction, rather than
commonly used CNN network, which fails to catch the temporal features and the long-range dependence of the traffic

ZHOU et al.: WF-TRANSFORMER: LEARNING TEMPORAL FEATURES

33

trace. In this section, we give some introduction about the
Transformer network.
Transformer network is designed with a self-attention mechanism, which is first applied to the field of natural language
processing (NLP) [24], [42], [43]. Recently, Transformer network has been applied for computer vision tasks, which is
dominant by CNN network previously [25]. Generally, Transformer network contains two parts, an encoder and a decoder.
Transformer with encoder-decoder architecture is suitable for
machine translation tasks in NLP. For sequence classification
tasks, we only need the encoder part of Transformer, and the
decoder part can be replaced with a classifier.
The input sequence can be set X = (x1 , x2 , . . . , xn ). The
embedding of the Transformer network is used to extract the
features from the original traffic traces, and obtain the vector
matrix representation Z of the features. Z can be calculated
as follows:
Z = WE X

(1)

where W E is the embedding matrix, and different W E represents different embedding manners.
Behind each block of the Transformer network, there is a
layer normalization operation, which is used for the output
of the corresponding block, and the outputs are converted
to a mean value of 1, and a variance of 0 by the layer
normalization.
In the NLP field, the position of different element in a
sequence is important for the meaning of a sentence. However, due to the parallelization processing of the Transformer,
position embedding is conducted to preserve the position information of a sequence. For a sequence, the position embedding
can be calculated as follows:
pos
)
(2)
P E( pos, 2i) = sin(
2i
10000 dmodel
pos
)
(3)
P E( pos, 2i + 1) = cos(
2i
10000 dmodel
where pos is the position of the corresponding element in
a sequence, dmodel is the word embedding length, and i ∈
[1, 2, . . . , dmodel − 1]. When i is an odd number, position
embedding is calculated with equation 2, otherwise using
equation 3. With the word embedding and position embedding,
the composition is obtained by adding the word embedding
and position embedding element by element.
The multi-head attention mechanism is an important part
of Transformer network, which focuses on key information of
the sequence, like a human intuitively. Transformer network
utilizes a multi-head attention mechanism to weigh the important features of the sequence. For the embedded features Z ,
we can get Q, K , and V by linear transform as follows.
Q = Wq Z
K = Wk Z
V = Wv Z

(4)
(5)
(6)

where Q, K , V are query, key and value respectively. Wq ,
Wk , Wv are initialized randomly and updated in the training
procedure.

According the attention mechanism, we can get the attention
weight as follows.
QK T
Attention(Q, K , V ) = so f tmax( √ )V
dk

(7)

where dk is used for scaling.
V. T HE P ROPOSED M ETHOD
In this section, we first introduce the inputs of our proposed
WF-Transformer. Subsequently, we present the architecture of
the model and the optimization procedure of our method.
A. The Inputs of WF-Transformer
Generally, Transformer networks are used for NLP, and the
input of the Transformer is a sequence, which is processed
from the original sentences. As for the traffic traces, the
traffic traces collected by network attackers mainly contain
the the time stamp of the packets, packet number and packet
size and packet directions. Prior study in WF attacks shows
that features extracted from the lengths of traces in each
direction are important for the success of WF attack. However,
Sirinam et al. prove that using packet length as a feature does
not provide significant attack accuracy improvement [7]. Their
proposed DF attack method abandons the packet size and the
time stamps, and only utilizes the packet direction as the input
of the deep neural network.
Similar to other deep WF attack methods, we only utilize
the packet directions as the inputs of the WF-Transformer. The
directions of the packets can be extracted from the collected
traces easily, and we use +1 to represent the outgoing packet,
while −1 is used to represent the incoming packet, and then
the input sequence can be donated as X = [x1 , x2 , . . . , xn ],
where xi ∈ {−1, +1}, and i ∈ {1, 2, . . . , n}, n is the number
of packets in a trace sequence. The length of the sequence is
important for the speed and classification accuracy of the Tor
traces, and the sequence length of other deep WF methods
[7], [30] are generally set to 5000. In fact, with the help of
the Transformer network in temporal feature extraction, WFTransformer can achieve comparable performance with shorter
trace compared with the state-of-the-art deep WF attacks, and
the superiority of our proposed method will be shown in the
following part.
B. The Architecture of WF-Transformer
Since the CNN focuses on the local property of the sequence
and ignores the long-term dependence among the elements in a
sequence, CNN has drawbacks in processing time series data,
while the Tor trace is a typical time series sequence. In this
paper, our proposed WF-Transformer utilizes Transformer
network to extract the temporal features of the Tor traces.
To make the proposed model suitable for the traffic traces,
we conduct sophisticated design on the Transformer network,
and we will introduce the design of our model in the following
part.
In Figure 2, the architecture of the proposed
WF-Transformer network is shown in detail. After the
embedding of the inputs, a layer norm operation is conducted,

34

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

Fig. 2.

The architecture of the proposed WF-Transformer.

and then is the multi-head attention module, a one-dimension
convolutional network layer with Gaussian Error Linear Unit
(GELU) activation function is used for the processing of the
embedded features, and the Q, K , V are calculated with
corresponding equations (4)(5)(6).
Absolute position embedding is introduced as above, which
utilizes a sine or cosine function to generate the position code,
and this position embedding fails to distinguish the relationship among multiple elements. In the multi-head attention
part of our proposed WF-Transformer, we utilize the relative
position embedding manner to show the relative position
relationship among different packets in a trace. The multi-head
attention with relative position embedding can be calculated
as follows:
Attention(Q, K , V ) = so f tmax(

Q(K T + A K )
)(V + A V )
√
dk
(8)

∗
For ai,∗ j ∈ A∗ , ∗ represents K or V , ai,∗ j = Wcli
p( j−i,k) , and
K
cli p(x, k) = max(−k, min(k, x)), k = j − i. ai, j and ai,V j can
represent the relative position information of element i and
element j, and this information only related with the position
i and j.
Furthermore, we utilize short-cut connection [23] among
different layers and dropout function after the GELU activation
function to avoid overfitting. In the forward layers, we utilize
four convolutional layers, and each with GELU activation.
As for the classifier, we utilize a fully-connected layer to
classify the Tor trace for our WF-Transformer model.
In this section, we describe the optimization of the proposed
WF-Transformer. We use W F T to represent the Transformer
feature extractor, and Cls to represent the classifier. Given
the input X = {x1 , x2 , . . . , xm } and ground-truth labels for
corresponding samples Y = {y1 , y2 , . . . , ym } for training
set, where m is the number of the samples. C denotes the
number of the trace categories. Then we can get the predicted
probability ŷi for the input xi as follows:

ŷi = so f tmax(Cls(W F T (xi )))

(9)

We choose multi-classification cross-entropy loss function
with a smooth coefficient s for our model, and the loss function

can be calculated as follows:
|X | C
|X | C

s XX
1 − s XX
yic log( ŷic ) −
log ŷic
loss = −
|X |
|X |
i=1 c=1
i=1 c=1
(10)
where yic and ŷic denote the ground-truth label c and probability of the sample xi classified to category c, respectively.
The smooth coefficient is determined by varying s in the range
of {0, 0.001, 0.005, 0.01, 0.5} in the experiments, and we set
s = 0.005 for the proposed model by a grid search manner.
VI. E XPERIMENTAL E VALUATION
In this section, we conduct extensive experiments to
demonstrate the effectiveness and superiority of our proposed
method. As far as we know, our proposed WF-Transformer is
the first work that utilizes Transformer network for temporal
feature extraction of anonymous traffic traces, and we compare
WF-Transformer with the state-of-the-art WF attacks on public
Tor traffic datasets on both closed-world and open-world
setting.
A. Dataset
We utilize the open-source dataset which is collected by
Sirinam et al. [7] to evaluate our method. The dataset contains two parts, Closed-world dataset and Open-world dataset,
which is collected with a tor-browser-crawler tool on Tor
Browser Bundle version 7.0.6. DF dataset is the latest public
dataset for the evaluation of deep WF attacks, which contains
95000 traces while Wang‘s dataset only contains 9000 traces
in the closed-world setting, so DF dataset is more suitable for
the training and evaluation of deep WF attack models.
1) Closed-World Dataset: This part of dataset collects Tor
traffic traces by visiting the homepage of each top Alexa
100 websites 1250 times. This dataset is generated in a campus
environment by using ten low-end machines. These machines
visit target websites with sequential and ordered methodology
in a round-robin manner. The dataset is preprocessed after the
crawler finishes by only recording the websites that have over
1000 visits. The closed-world dataset contains 95 websites
with 1000 visits for the closed-world evaluations. For closedworld evaluation, the training set contains 76000 traces, while
the testing set contains 9500 traces.

ZHOU et al.: WF-TRANSFORMER: LEARNING TEMPORAL FEATURES

35

TABLE I
H YPERPARAMETER S ELECTION FOR WF-T RANSFORMER

TABLE II
T HE D ETAILS OF DF DATASET

2) Open-World Dataset: This part of the dataset collects
the Alexa top 5000 websites excluding the first 100 websites
used in closed-world dataset. The collection procedure is the
same as the closed-world collection procedure. For open-world
dataset collection, each homepage of the websites is only
visited once, and the corrupted visits which have been collected in closed-world dataset are discarded. The webpages
that are blank pages, access denied pages, CAPTCHA pages
and timeout error pages are removed, and the final open-world
dataset contains 40,716 traffic traces. For open-world evaluation, the training set contains 96000 traces, while the testing
set contains 29500 traces. More details can refer to Table II.
B. Experiment Details
Our proposed WF-Transformer method is used for website
fingerprinting attacks with a novel deep network architecture.
Compared with existing deep website fingerprinting attack
methods which utilize CNN as the feature extractor, the proposed WF-Transformer utilizes Transformer which contains
lots of improvements for traffic trace feature extraction.
Our implementation of WF-Transformer model uses Pytorch
framework [44], and we utilize RTX 3090 to accelerate the
model training. We utilize AdamW [45] as an optimizer to
train the WF-Transformer networks, the learning rate is set
as 3e−4 at the beginning with a dynamic change mechanism.
The learning rate is 3e−4 in the first 30 epochs, and then set
as 3e−5 for the following 10 epochs. The batch size is set

to 16, and we utilize the dropout layer after each activation
layer and set the rate as 0.5, and the training epochs are set
to 40 for all the attacks. The input of the WF-Transformer is
the direction of each packet in the traffic trace. Furthermore,
we give hyper-parameter search ranges and the selected values
in Table I.
C. Experiment Setup
To evaluate the performance of our proposed WFTransformer, we compare it with several state-of-the-art WF
attacks. We choose three attacks, CUMUL [13], AWF [29]
and DF [7] as benchmarks to show the performance of our
proposed attacks. CUMUL is a non-deep WF attack, AWF
and DF are deep WF attacks with different designs of CNN
networks, and they are two kinds of representative existing
WF methods. Specifically, we follow the network setting of
AWF [29], AWF is an LSTM/CNN hybrid architecture in our
experiment evaluations, which is built by five convolutional
layers, one LSTM layer and a fully-connected layer.
To evaluate the performance of our proposed WFTransformer comprehensively, we choose four defenses,
TAMARAW [16], WTF-PAD [17], FRONT [35] and Mockingbird [40] as competitors to our proposed attacks. TAMARAW
is a heavyweight regularization defense with high latency and
data overhead, while WTF-PAD is a lightweight obfuscation
defense, which is developed by Tor project. FRONT is a
new lightweight defense which pads dummy packets into

36

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

the front part of the traces. Mockingbird generates adversarial traces to confuse the classifiers. In our experiments,
we follow the original settings that provided in the papers
and perform parameter tuning on the candidate parameters and
find the optimal parameters. Specifically, Mockingbird utilizes
the trace burst as the input, so we transform the burst of the
generated adversarial trace to the direction of each packet for
the evaluation of WF attacks.
We conduct the experiments on both closed-world and
open-world settings. In closed-world setting, the classification
accuracy is used for the evaluation of the attack methods.
In open-world setting, we calculate the corresponding TPR,
FPR and precision-recall curves to show the performance of
different methods.
D. Evaluation Metrics
We use the prediction probability output by the classifier
to classify target traces. If a monitored trace has a prediction
probability greater than a certain threshold, we will record
it as True Positive (TP), or False Negative (FN) otherwise.
Similarly, if an unmonitored trace is correctly classified, it will
be considered True Negative (TN), or False Positive (FP)
otherwise.
For closed-world scenario, classification accuracy is used
for the evaluation of WF attacks. For open-world scenario,
True Positive Rate (TPR) and False Positive Rate (FPR)
are used. Furthermore, Precision-Recall curves are used for
further study of the WF attacks for open-world setting. As for
closed-world setting, the classification accuracy is calculated
by N ACC /N AL L , where N AL L is the number of the all traffic
traces, and N ACC denotes the number that correct classifications. TPR is calculated by T P/(T P + F N ) and FPR
equals to F P/F P + T N . Precision and recall are defined as
T P/(T P + F P) and T P/T P + F N , respectively.
VII. E XPERIMENT R ESULTS
In this section, we show the experiment results of our
WF-Transformer for both closed-world setting and open-world
setting.
A. Closed-World Evaluation on Non-Defended Traces
We evaluate the performance of the WF-Transformer in
the closed-world scenario on the non-defended traces, which
only utilizes website traces from the closed-world dataset
with no WF defenses. For baseline methods, we compare WF-Transformer with CUMUL, AWF and DF attacks.
As mentioned ahead, WF-Transformer is designed for the temporal feature extraction of the traffic traces. In the evaluation
phase, unlike the setting in the prior attacks, we vary the length
of the input trace and show the superiority of the proposed
WF-Transformer.
Table III shows the classification accuracy results of different WF attacks, and we repeat each anonymous trace
classification task five times. Both average classification accuracy and standard deviation are reported for each anonymous
trace classification task. In table III, we show the results of
different lengths of inputs for each WF attack. Generally, the

length of inputs in prior deep WF attacks is set to 5000, such
as AWF and DF attacks. However, the longer the inputs, the
higher the model computation cost is, and the practicality of
the model can be reduced, since attackers need to collect more
traffic traces, which needs more time. The length of the inputs
is set in the range of [1000, 2000, 3000, 4000, 5000] for each
attack.
According to Table III, WF-Transformer attains 99.1%
classification with the input length 5000, which is significantly
better than the other attacks with different input lengths,
significantly. Furthermore, we can find that the classification
accuracy is improved with the length of the inputs increased.
Compared with CUMUL, which is a non-deep WF attack
method, our WF-Transformer outperforms CUMUL in all
input length settings, significantly.
Compared with deep WF attacks, such as AWF and DF
methods, WF-Transformer can still obtain better performance
than them, especially for the short input length setting. In our
experiment, AWF utilizes the CNN/LSTM hybrid architecture
for the model building, which is the same as the corresponding
hyperparameter setting for the AWF. We can observe that
the classification accuracy of AWF is lower than that of
our WF-Transformer, even when the input length is set to
5000, and the classification accuracy of AWF (95.5%) is
poorer than the performance of WF-Transformer with input
length 1000. Though AWF model contains LSTM network
to extract temporal features of the traces, the performance
of AWF is still inferior to our proposed WF-Transformer,
which demonstrates the superiority of the WF-Transformer
in trace temporal feature extraction. DF has a more complex
network architecture than AWF, and gets better performance
than AWF, but the performance of DF is still inferior to WFTransformer. When the input length of the WF-Transformer
is set as 2000, WF-Transformer gets better classification
than DF with input length 5000 (98.7% vs 98.3%), which
demonstrates the effectiveness and superiority of our proposed
WF-Transformer for anonymous trace classification in closedworld scenario. Furthermore, based on the given average
classification accuracy and standard deviation, a t-test [46]
can be conducted to each anonymous trace classification result,
there is high confidence that our WF-Transformer significantly
outperforms DF for corresponding input trace length. For the
case that WF-Transformer with input length 5000 and DF
with input length, the classification accuracy of our proposed
WF-Transformer is significantly higher than that of DF.
B. Closed-World Evaluation on Defended Traces
In this section, we test the performance of the proposed
WF-Transformer on the defended traces. As mentioned in
section III, WF defenses pad dummy packets into the normal traces to change the pattern of the anonymous traces,
so that the performance of WF attack model in classifying
defended traces is reduced. In this part, we select TAMARAW
[16], WTF-PAD [17], FRONT [35] and Mockingbird [40] to
evaluate the performance of WF attack under the defended
traces. TAMARAW is a heavyweight defense that pads dummy
packets into traces at fixed speed and length, which causes

ZHOU et al.: WF-TRANSFORMER: LEARNING TEMPORAL FEATURES

37

TABLE III
C LASSIFICATION ACCURACY (%) ON N ON -D EFENDED T RACES FOR S TATE - OF - THE -A RT ATTACKS IN THE C LOSED -W ORLD S ETTING

high bandwidth overhead and delay. WTF-PAD and FRONT
are lightweight defenses. According to the experiment in
the closed-world setting, WF-Transformer can utilize short
inputs to get better classification accuracy than other methods,
so evaluating performance on the traces defended by FRONT
is necessary for our proposed WF-Transformer. Mockingbird
is a new defense that based on adversarial examples, we test
the performance of our proposed WF-Transformer on the
traces defended by Mockingbird.
We follow the setting of TAMARAW in the original paper,
and padding dummy packets into the traces with fixed IAT. For
WTF-PAD defense, we use an open-source defended dataset.
For FRONT defense, since there is no time stamp in our
dataset, and we follow the setting of the original paper [35]
and calculate the percentage of packets in the traces, and we
only pad dummy packets into first 50% of the traces to get
the traces defended by FRONT.
Since the classification accuracy of WF-Transformer with
input length 2000 on non-defended traces has reached 98.5%,
which is higher than other WF attacks, the following evaluation of WF-Transformer on defended traces is based on
the input length 2000, and for other WF attacks, the input
length is set to 5000 as the original paper. In our experiment
settings, the defended traces are also used for the training of
the attack models, and we evaluate the classification accuracy
on test traces. For Mockingbird [40], we utilize AWF network
as the detector, and the experiment set follows the case I in
the original paper [40], which is more realistic.
We show the defense performance in Table IV, and both
the classification accuracy on defended traces and bandwidth
overhead are listed in the table. TAMARAW is a heavyweight
defense, and the bandwidth overhead is 403% in our experiments, and holds up well with less than 15% classification
accuracy among all the WF attacks. Though TAMARAW
gets good performance in defending the WF attacks, it is
not practical in real anonymous networks due to the high
bandwidth overhead and delay.
For WTF-PAD defense, the classification accuracy of
CUMUL and AWF is reduced from over 90% to less than
65%, which shows significant defense performance. However, DF can still realize over 90% classification accuracy
on WTF-PAD defended traces (98.3% for non-defended
traces), and the experiment result demonstrates that WTF-PAD
fails to resist the DF attack. Furthermore, the proposed
WF-Transformer obtains 92.1% classification accuracy on
defended traces, which shows that WTF-APD defended
traces fail to confuse the WF-Transformer classifier. In our

experiment, the bandwidth overhead of WTF-PAD is 67%,
and there is no delay for WTF-PAD defense due to the dummy
packets being padded into the gaps between normal packets.
In Table IV, we can observe that FRONT defense can reduce
the classification accuracy of all the WF attacks, and the
accuracy of CUMUL is reduced from 95.5% to 44.2%. For
AWF and DF defenses, FRONT still gets good performance
in confusing deep classification models, and the classification
accuracy is lower than 72% on the defended traces. According
to the FRONT paper [35], the trace pattern information is
gathered in the head part of the traces, padding dummy packets
into the front part of the traces rather than the whole trace
can reduce the bandwidth overhead and confuse traffic pattern
information efficiently. Since the feature-rich part is confused,
the attack performance is reduced. For Mockingbird defense,
WF-Transformer gets 56.2% classification accuracy on the
traces defended by Mockingbird, which is higher than other
WF attacks. The experiments on defended traces show that
our WF-Transformer can get better performance on defended
traces than state-of-the-art methods.
Our proposed WF-Transformer gets better attack performance than AWF and DF attacks, though only using 2000 cells
in a trace. WF-Transformer can extract the temporal feature of
the traces, and the classification accuracy of WF-Transformer
is reduced from 98.5% on non-defended traces to 82.4% on
traces defended by FRONT, which gets the smallest drop
compared with other WF attacks.
Furthermore, we show the training process of the
WF-Transformer in undefended traces in a closed-world
setting. Since DF is a state-of-the-art deep WF attack,
we compare our method with DF to show the convergence
performance. As shown in Figure 3, we show the DF method
with 5000 input length and our proposed WF-Transformer
with two kinds of input length, 2000 and 5000, respectively.
Figure 3(a) shows changes in the training and test loss
during training epochs. WF-Transformer method has lower
training and test loss value than DF method, and we can
find that the test loss value of our proposed WF-Transformer
is almost unchanged after 5 epochs, while the loss of DF
remains unchanged after 10 epochs, which means that our
proposed WF-Transformer converges faster than DF methods.
Furthermore, WF-Transformer with input length 5000 has a
lower loss than WF-Transformer with length 2000 for the
training and test procedure.
In Figure 3(b), we show the classification accuracy of DF
and WF-Transformer during training epochs. Our proposed
WF-Transformer obtains over 90% classification accuracy,

38

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

TABLE IV
C LASSIFICATION ACCURACY (%) ON D EFENDED T RACES IN THE C LOSED -W ORLD S ETTING

Fig. 3. The loss value and classification accuracy change for DF and WF-Transformer in closed-world setting. (WFT denotes WF-Transformer, the number
represents the input length.)

while DF gets about 76% classification accuracy in the first
epoch, and the classification accuracy of WF-Transformer
is higher than that of DF for each training epoch, consistently. The classification accuracy of WF-Transformer has little
change after 5 epochs, while the accuracy for DF remains
stable after 15 epochs, which shows that WF-Transformer has
better convergence than DF. Furthermore, since we update the
learning rate dynamically in the training, the loss and accuracy
curves of WF-Transformer are smoother than that of DF.
C. Open-World Evaluation
WF attacks used in the open-world scenario are more
realistic, in which attackers not only classify the anonymous
traces based on the limited monitored sites, but also need to
distinguish whether the trace comes from a monitored site or
an unmonitored one. For the evaluation of the WF attacks in
the open-world setting, we chose the true positive rate (TPR)
and false positive rate (FPR), and we also show PrecisionRecall (PR) curves, which is commonly used in prior works
[7], [44].
In our open-world evaluation, the output of the model is
the prediction probability of each category. Previous studies
have provided a Standard Model for the evaluation of WF
in the open-world setting [7], in which the attackers can utilize
the unmonitored traces to train the classifier, and this can
help the WF attack model classify monitored and unmonitored
traces correctly. The evaluation of the standard model is similar
to that in the closed-world setting, the difference is that we

add an extra category to the classifier for the classification of
the unmonitored website traces. Generally, if the prediction
probability of a monitored trace is greater than a threshold,
the trace is considered a true positive. The different thresholds
are used for different WF attacks, which are selected to realize
high TPR and low FPR.
For the evaluation in the standard model, we investigate
the impact of more training data on the performance of the
classifiers in the open-world scenario by varying the number
of unmonitored traces, and we compare the performance
of our proposed WF-Transformer with other state-of-the-art
WF attacks on non-defended traces. In our standard model,
the training set contains all the monitored traces(900 traces
for each 95 monitored websites). In the test phase, all the
monitored traces and 20000 unmonitored traces are included
in the test set, and the unmonitored traces are randomly
selected from the unmonitored traces set that is not used for
training.
As shown in Figure 4, we show the influence of the unmonitored traces used for the training on the WF attacks in openworld setting. For the evaluation of WF-Transformer, we show
the results on two settings, the input length is 2000 and
5000, respectively, and the amounts of the unmonitored
traces vary in the range {1000, 5000, 10000, 15000, 20000},
Figure 4 (a) and (c) show the TPR and FPR of the baseline
methods and the proposed WF-Transformer with input length
2000, and Figure 4 (b) and (d) show the TPR and FPR of
the baseline methods and the proposed WF-Transformer with
input length 5000.

ZHOU et al.: WF-TRANSFORMER: LEARNING TEMPORAL FEATURES

39

Fig. 4.
The impact of the amount of unmonitored training data on TPR and FPR (Non-defended dataset) in open-world setting. (WF-T represents“WF-Transformer”. 2000 and 5000 represent the input length for WF-Transformer, respectively.)

Fig. 5. Precision-Recall curves in the open-world setting. (Up: the input length of the traces for WF-Transformer is set to 2000. Down: the input length of
the traces for WF-Transformer is set to 5000.)

Compared with the baseline methods, WF-Transformer gets
the best performance in both TPR and FPR metrics. For
the input length in 2000, WF-Transformer gets consistently
best performance on both TPR and FPR, and the TPR is
0.965, while FPR is 0.007 for 20000 unmonitored traces.
For the input length in 5000, WF-Transformer still gets best
performance than the other baseline methods, and the TPR
is 0.969 and the FPR is 0.007 for 20000 unmonitored traces.
According to our experiments, AWF gets the lowest TPR and
highest FPR, which is a bad performance on unmonitored
traces, and this be attributed to the architecture of the networks, which has fewer layers than DF. WF-Transformer and
other baseline methods have the same FPR trend with the training size increasing, while our proposed WF-Transformer has
higher TPR than other baseline methods over all the training
sizes, which demonstrates the effectiveness and superiority of
the proposed WF-Transformer.
For the evaluation of the unmonitored traces in the openworld scenario, we conduct experiments on the traces defended
by WTF-PAD and FRONT methods. Furthermore, we also
conduct experiments on the non-defended traces for comparison. According to Figure 4 (c) and (d), the FPR drops with

the size of the unmonitored trace increasing in the training,
and the FPR is lowest when the size is set to 20000. In the
evaluation of the defended traces, we set the number of
the unmonitored trace to 20000 and provide Precision-Recall
curves of different WF attacks to show the diagnostic ability
when the discrimination threshold varies. In the experiment
setting, the training set contains all the monitored traces and
20000 unmonitored traces, while the test set contains the monitored set and 20000 unmonitored traces (each unmonitored
website has one trace).
We conduct extensive experiments in an open-world setting to show the precision-recall curves in the non-defended,
defended by WTF-PAD and defended by FRONT traces. The
precision-recall curve shows the trade-off between precision
and recall for different thresholds. A high area under the curve
represents both high recall and high precision, where high
precision relates to a low false positive rate, and high recall
relates to a low false negative rate. Since the dataset we used is
an imbalanced dataset [7], PR curves can be used to show the
performance of the classifier. As shown in Figure 5, we show
the PR curves in the open-world settings under different input
length settings for WF-Transformer, in which the input length

40

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

for CUMUL, AWF, and DF is set to 5000 as their original
paper, while the input length for WF-Transformer is set to
2000 and 5000, respectively.
The up row in Figure 5 shows the PR curves of the
CUMUL, AWF, DF and WF-Transformer with input length
2000 on the defended traces, and we can observe that
WF-Transformer still outperforms other WF attacks in all the
defense settings. For non-defended traces, the PR curves of
DF and WF-Transformer are in the top right-hand corner,
which means that both DF and WF-Transformer are effective
for different thresholds, and the performance of DF and
WF-Transformer are close to each other in the non-defended
traces. The precision for CUMUL and AWF is high, while the
recall covers a wide range, which means that these attacks
miss many monitored traces. For the traces defended by
WTF-PAD, the performance of all the attacks is reduced.
According to the Figure 5(b), CUMUL and AWF get bad
performance for the traces defended by WTF-PAD, while our
proposed WF-Transformer outperforms all other WF attacks,
including DF attacks. For traces defended by FRONT, our
proposed WF-Transformer still gets the best performance than
other attacks, and for high precision, WF-Transformer gets a
precision of 0.968 and recall of 0.711. For high recall, WFTransformer gets 0.720 precision and 0.956 recall. With the
input length set to 2000, WF-Transformer gets best performance than other WF attacks, which set the input length of
the trace to 5000.
In Figure 5 (d) and (h), we show the performance of
WF-Transformer on traces defended by Mockingbird method.
Mockingbird is a new defense that generates adversarial
traces to mislead the classifiers to a selected wrong target
category [40], and makes the performance of WF attack
decrease. For traces defended by Mockingbird, our proposed
WF-Transformer gets the best performance than other attacks,
and for high precision, WF-Transformer gets a precision of
0.562 and a recall of 0.391. For high recall, WF-Transformer
gets 0.425 precision and 0.911 recall. The area under the PR
curve of WF-Transformer is larger than other WF attacks,
which means that WF-Transformer has better anonymous trace
classification performance. In Figure 5 (d), WF-Transformer
with the input length set to 2000 still gets the best performance
than other WF attacks which the input length of the trace is
set to 5000.
The down row in Figure 5 shows the PR curves of the
CUMUL, AWF, DF and WF-Transformer with input length
5000 on the defended traces. With more information delivered
to WF-Transformer model, our proposed method gets better
performance than other WF attacks and WF-Transformer with
input length 2000. WF-Transformer can utilize short trace
(2000) to train the model and get better performance than other
deep attacks trained on long traces (5000) in both closed-world
and open-world settings.
VIII. M EASURING I NFORMATION L EAKAGE FOR
E XTRACTED F EATURES
In this section, we give more evidence to show the superiority of our proposed WF-Transformer in extracting trace
features. As we claimed that our proposed WF-Transformer

can learn the temporal features of the traces, which is ignored
by the CNN-based deep WF attacks. There are several studies
about the information leakage measurement for website fingerprinting [47], [48], and the information leakage measurement
can be used to estimate how much information leaks from
systems.
We utilize WeFDE (Website Fingerprint Density
Estimation) [48] to measure the information leakage of
the features extracted by DF and our proposed WFTransformer. According to WeFDE, the information leakage
can be calculated as I (F; W ) = H (W ) − H (W |F), where F
is the trace fingerprinting, and W is the website information,
and I (F; W ) is the amount of the information that an
attacker can learn form F about W , and H (⋆) is entropy
function. Since WeFDE is specially designed for quantifying
the information leakage from WF defenses [48], we measure
information leakage of the features extracted from the traces
defended by WTF-PAD.
We utilize the features which are before the classifier of
WF-Transformer and DF as inputs of WeFDE, and implement
the source code1 to calculate the information leakage.
According to our experiment, the information leakage of
features extracted by DF (input length 5000) is 7.2 bits,
while the information leakage of features extracted by
WF-Transformer is 7.7 bits (input length 2000) and 7.9 bits
(input length 5000). The higher of the information leakage, the
more information is extracted from the traces. The experiment
result demonstrates that our proposed WF-Transformer can
learn more information from the anonymous traces than the
CNN-based model, which validates the superiority of our
proposed method.
IX. D ISCUSSION
To the best of our knowledge, WF-Transformer is the first
work that uses Transformer network for WF attack tasks.
According to the experiment results above, our proposed
WF-Transformer obtains the best performance than several
state-of-the-art WF attacks on both closed-world and openworld settings. Furthermore, we conduct extensive experiments
to show the model robust on the defended anonymous traces,
and the experiment results demonstrate the effectiveness and
superiority of our proposed method.
As we have claimed that our proposed WF-Transformer
can extract the temporal feature of the traces with the help
of the Transformer network, WF-Transformer can learn the
long-term dependence among the trace cells, while the CNN
network focuses on the local features with a slide window
and ignores the dependence between the front cells and the
latter cells in the traces, and Transformer architecture has
advantages in analyzing trace data. Though the proposed
WF-Transformer obtains convincing results in WF attack,
we give some consideration to the limitation of our proposed
method, and the discussion mainly focuses on the training
costs.
We test the processing time for the WF attacks with different
deep networks. For simplicity, we compare the processing time
1 https://github.com/s0irrlor7m/InfoLeakWebsiteFingerprint

ZHOU et al.: WF-TRANSFORMER: LEARNING TEMPORAL FEATURES

TABLE V
T HE C OMPUTING T IME FOR D IFFERENT D EEP WF
ATTACKS . (S ECOND /T RACE )

of our proposed WF-Transformer with DF attack, which is a
state-of-the-art attack based on CNN architecture. Based on
the DF original code, we reproduce the DF with Pytorch
framework, and WF-Transformer is realized with Pytorch,
equally. Both of them use GPU acceleration with NVIDIA
GTX 3090 with 24 GB of GPU memory. For the input
length of 2000, DF requires 0.0026 seconds for each trace,
while WF-Transformer requires 0.0070 seconds for each trace.
For the input length of 5000, the processing time for each
trace has small increase, and requires 0.0027 seconds, while
WF-Transformer requires 0.019 seconds. According to the
comparison, the time consumption for WF-Transformer is
higher than DF method, which is based on CNN architecture. The comparison of computing time is shown in the
table V.
The performance of WF-Transformer with a 2000 input
length is better than DF with an input length of 5000, the
processing time of WF-Transformer for each trace is about
7 times that of DF. Considering the whole attack procedure,
collecting only 2000 cells is easier and time-saving than
collecting 5000 cells for a website, so the increased time
consumption in classification can be tolerated. According to
convergence analysis in Figure 3, WF-Transformer converges
faster than DF, which can decrease the training time and
improve deployment efficiency in real networks. Furthermore, Transformer architecture has been extensively studied
in multiple fields, such as NLP [24]and CV [25]. Lots of
optimization on Transformer architecture has been proposed,
such as Swin-Transformer [25], so it is promising to improve
the efficiency of WF-Transformer to decrease the time cost
in processing traces, and make our proposed method more
efficient.
X. C ONCLUSION
In this paper, we present a novel deep WF attack, called
Website Fingerprinting Transformer (WF-Transformer), which
utilizes Transformer network to extract the temporal feature of
the anonymous traffic traces, and trains the model in an end-toend manner. Unlike existing deep WF attacks based on CNN
architecture that only focus on the local dependence of the
traces, WF-Transformer can learn the long-term dependence
among the trace cells. We conduct extensive experiments to
validate the effectiveness of our proposed method in both
closed-world and open-world settings. According to our experiments, WF-Transformer outperforms other Bstate-of-the-art
WF attacks in both closed-world and open-world setting,
and the performance of WF-Transformer with input length
2000 outperforms that of DF with input length 5000 due to
Transformer network can capture the temporal feature from

41

the traces, and WF-Transformer with input length 5000 obtain
99.1% classification accuracy for undefended trace, which
is a new state-of-the-art WF result. With the input length
set to 2000 for WF-Transformer, in closed-world evaluation,
WF-Transformer obtains 98.7% classification accuracy for
undefended traces, and reaches 92.1% and 82.4% classification
accuracy for traces defended by WTF-PAD and FRONT
respectively, which is higher than that of DF significantly.
For open-world evaluation, WF-Transformer with 2000 input
length obtains a 0.99 precision and a 0.95 recall for undefended traces, and it attains precision of 0.97, 0.95 and recall
of 0.71, 0.70 for traces defended by WTF-PAD and FRONT,
respectively. For the defense method based on adversarial
examples, WF-Transformer still gets the best classification
performance than existing WF attacks. Furthermore, WFTransformer has better convergence performance than DF, and
these experiments demonstrate the effectiveness and superiority of our proposed WF-Transformer. In the future, we plan
to conduct further research on the design of Transformer
network for processing traffic traces, and get a more efficient
Transformer-based WF model.
R EFERENCES
[1] C. Fachkha and M. Debbabi, “Darknet as a source of cyber intelligence:
Survey, taxonomy, and characterization,” IEEE Commun. Surveys Tuts.,
vol. 18, no. 2, pp. 1197–1227, 2nd Quart., 2016.
[2] Users-Tor Metrics. Accessed: Jun. 10, 2022. [Online]. Available:
https://metrics.torproject.org/userstats-relay-country.html
[3] I. Karunanayake, N. Ahmed, R. Malaney, R. Islam, and S. K. Jha,
“De-anonymisation attacks on Tor: A survey,” IEEE Commun. Surveys
Tuts., vol. 23, no. 4, pp. 2324–2350, 4th Quart., 2021.
[4] A. Panchenko, L. Niessen, A. Zinnen, and T. Engel, “Website fingerprinting in onion routing based anonymization networks,” in Proc.
10th Annu. ACM Workshop Privacy Electron. Soc., Chicago, IL, USA,
Oct. 2011, pp. 103–114.
[5] X. Cai, X. C. Zhang, B. Joshi, and R. Johnson, “Touching from a distance: Website fingerprinting attacks and defenses,” in Proc. ACM Conf.
Comput. Commun. Secur., Raleigh, NC, USA, Oct. 2012, pp. 605–616.
[6] A. Kwon, M. AlSabah, D. Lazar, M. Dacier, and S. Devadas, “Circuit
fingerprinting attacks: Passive deanonymization of Tor hidden services,”
in Proc. 24th USENIX Secur. Symp. (USENIX Security). Washington,
DC, USA: USENIX Association, Aug. 2015, pp. 287–302.
[7] P. Sirinam, M. Imani, M. Juarez, and M. Wright, “Deep fingerprinting: Undermining website fingerprinting defenses with deep learning,”
in Proc. ACM SIGSAC Conf. Comput. Commun. Secur., Oct. 2018,
pp. 1928–1943.
[8] A. Montieri, D. Ciuonzo, G. Bovenzi, V. Persico, and A. Pescapé,
“A dive into the dark web: Hierarchical traffic classification of anonymity
tools,” IEEE Trans. Netw. Sci. Eng., vol. 7, no. 3, pp. 1043–1054,
Jul. 2020.
[9] M. Shen, Y. Liu, L. Zhu, X. Du, and J. Hu, “Fine-grained webpage fingerprinting using only packet length information of encrypted
traffic,” IEEE Trans. Inf. Forensics Security, vol. 16, pp. 2046–2059,
2021.
[10] D. Herrmann, R. Wendolsky, and H. Federrath, “Website fingerprinting:
Attacking popular privacy enhancing technologies with the multinomial Naïve–Bayes classifier,” in Proc. ACM Workshop Cloud Comput.
Secur., R. Sion and D. Song, Eds., Chicago, IL, USA, Nov. 2009,
pp. 31–42.
[11] T. Wang, X. Cai, R. Nithyanand, R. Johnson, and I. Goldberg, “Effective
attacks and provable defenses for website fingerprinting,” in Proc. 23rd
USENIX Secur. Symp. San Diego, CA, USA: USENIX Association,
Aug. 2014, pp. 143–157.
[12] M. Juarez, S. Afroz, G. Acar, C. Díaz, and R. Greenstadt, “A critical
evaluation of website fingerprinting attacks,” in Proc. ACM SIGSAC
Conf. Comput. Commun. Secur., Scottsdale, AZ, USA, Nov. 2014,
pp. 263–274.

42

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

[13] A. Panchenko et al., “Website fingerprinting at internet scale,” in Proc.
Netw. Distrib. Syst. Secur. Symp. San Diego, CA, USA: The Internet
Society, Feb. 2016, pp. 1–15.
[14] J. Hayes and G. Danezis, “k-fingerprinting: A robust scalable website fingerprinting technique,” in Proc. 25th USENIX Secur. Symp.
(USENIX Security). Austin, TX, USA: USENIX Association, Aug. 2016,
pp. 1187–1203.
[15] K. P. Dyer, S. E. Coull, T. Ristenpart, and T. Shrimpton, “Peek-aboo, I still see you: Why efficient traffic analysis countermeasures fail,”
in Proc. IEEE Symp. Secur. Privacy. San Francisco, CA, USA: IEEE
Computer Society, May 2012, pp. 332–346.
[16] X. Cai, R. Nithyanand, T. Wang, R. Johnson, and I. Goldberg, “A systematic approach to developing and evaluating website fingerprinting
defenses,” in Proc. ACM SIGSAC Conf. Comput. Commun. Secur.,
Scottsdale, AZ, USA, Nov. 2014, pp. 227–238.
[17] M. Juárez, M. Imani, M. Perry, C. Díaz, and M. Wright, “Toward
an efficient website fingerprinting defense,” in Computer Security—
ESORICS 2016 (Lecture Notes in Computer Science), vol. 9878.
Heraklion, Greece: Springer, Sep. 2016, pp. 27–46.
[18] T. Wang and I. Goldberg, “Walkie-talkie: An efficient defense against
passive website fingerprinting attacks,” in Proc. 26th USENIX Secur.
Symp. (USENIX Security). Vancouver, BC, Canada: USENIX Association, Aug. 2017, pp. 1375–1390.
[19] D. Lu, S. Bhat, A. Kwon, and S. Devadas, “DynaFlow: An efficient
website fingerprinting defense based on dynamically-adjusting flows,” in
Proc. Workshop Privacy Electron. Soc., Toronto, ON, Canada, Jan. 2018,
pp. 109–113.
[20] N. Papernot, P. McDaniel, S. Jha, M. Fredrikson, Z. B. Celik, and
A. Swami, “The limitations of deep learning in adversarial settings,” in
Proc. IEEE Eur. Symp. Secur. Privacy (EuroSP), Saarbrücken, Germany,
Mar. 2016, pp. 372–387.
[21] Y. LeCun, Y. Bengio, and G. Hinton, “Deep learning,” Nature, vol. 521,
no. 7553, pp. 436–444, 2015.
[22] A. Krizhevsky, I. Sutskever, and G. E. Hinton, “ImageNet classification
with deep convolutional neural networks,” in Proc. Adv. Neural Inf.
Process. Syst., 26th Annu. Conf. Neural Inf. Process. Syst., vol. 25,
Lake Tahoe, NV, USA, Dec. 2012, pp. 1106–1114.
[23] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Las Vegas, NV, USA: IEEE Computer Society, Jun. 2016,
pp. 770–778.
[24] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural
Inf. Process. Syst., 26th Annu. Conf. Neural Inf. Process. Syst., vol. 30,
Long Beach, CA, USA, Dec. 2017, pp. 5998–6008.
[25] Z. Liu et al., “Swin transformer: Hierarchical vision transformer using
shifted windows,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Montreal, QC, Canada, Oct. 2021, pp. 9992–10002.
[26] W. Zeng, C. Lin, K. Liu, J. Lin, and A. K. H. Tung, “Modeling spatial
nonstationarity via deformable convolutions for deep traffic flow prediction,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 3, pp. 2796–2808,
Mar. 2023.
[27] J. Zhang, Y. Zheng, J. Sun, and D. Qi, “Flow prediction
in spatio-temporal networks based on multitask deep learning,”
IEEE Trans. Knowl. Data Eng., vol. 32, no. 3, pp. 468–478,
Mar. 2020.
[28] K. Abe and S. Goto, “Fingerprinting attack on Tor anonymity using deep
learning,” in Proc. Asia–Pacific Adv. Netw., vol. 42, 2016, pp. 15–20.
[29] V. Rimmer, D. Preuveneers, M. Juárez, T. V. Goethem, and W. Joosen,
“Automated website fingerprinting through deep learning,” in Proc.
Netw. Distrib. Syst. Secur. Symp. San Diego, CA, USA: The Internet
Society, Feb. 2018, pp. 1–15.
[30] S. Bhat, D. Lu, A. Kwon, and S. Devadas, “Var-CNN: A dataefficient website fingerprinting attack based on deep learning,”
Proc. Privacy Enhancing Technol., vol. 2019, no. 4, pp. 292–310,
Oct. 2019.
[31] P. Sirinam, N. Mathews, M. S. Rahman, and M. Wright, “Triplet
fingerprinting: More practical and portable website fingerprinting with
N-shot learning,” in Proc. ACM SIGSAC Conf. Comput. Commun. Secur.,
London, U.K., Nov. 2019, pp. 1131–1148.
[32] M. Chen, Y. Wang, H. Xu, and X. Zhu, “Few-shot website fingerprinting
attack,” Comput. Netw., vol. 198, Oct. 2021, Art. no. 108298.
[33] M. Shen, J. Zhang, L. Zhu, K. Xu, and X. Du, “Accurate decentralized application identification via encrypted traffic analysis using
graph neural networks,” IEEE Trans. Inf. Forensics Security, vol. 16,
pp. 2367–2380, 2021.

[34] Y. Wang, H. Xu, Z. Guo, Z. Qin, and K. Ren, “SnWF: Website
fingerprinting attack by ensembling the snapshot of deep learning,” IEEE
Trans. Inf. Forensics Security, vol. 17, pp. 1214–1226, 2022.
[35] J. Gong and T. Wang, “Zero-delay lightweight defenses against website
fingerprinting,” in Proc. 29th USENIX Secur. Symp. (USENIX Security).
Berkeley, CA, USA: USENIX Association, Aug. 2020, pp. 717–734.
[36] W. De la Cadena et al., “TrafficSliver: Fighting website fingerprinting
attacks with traffic splitting,” in Proc. ACM SIGSAC Conf. Comput.
Commun. Secur., USA, Oct. 2020, pp. 1971–1985.
[37] A. Ilyas, S. Santurkar, D. Tsipras, L. Engstrom, B. Tran, and
A. Madry, “Adversarial examples are not bugs, they are features,”
in Proc. Adv. Neural Inf. Process. Syst., Annu. Conf. Neural Inf.
Process. Syst. (NeurIPS), vol. 32, Vancouver, BC, Canada, Dec. 2019,
pp. 125–136.
[38] I. J. Goodfellow, J. Shlens, and C. Szegedy, “Explaining and harnessing
adversarial examples,” in Proc. 3rd Int. Conf. Learn. Represent. (ICLR),
San Diego, CA, USA, May 2015, pp. 1–11.
[39] C. Szegedy et al., “Intriguing properties of neural networks,” in Proc.
2nd Int. Conf. Learn. Represent. (ICLR), Banff, AB, Canada, Apr. 2014,
pp. 1–10.
[40] M. S. Rahman, M. Imani, N. Mathews, and M. Wright, “Mockingbird:
Defending against deep-learning-based website fingerprinting attacks
with adversarial traces,” IEEE Trans. Inf. Forensics Security, vol. 16,
pp. 1594–1609, 2021.
[41] A. Abusnaina, R. Jang, A. Khormali, D. Nyang, and D. Mohaisen,
“DFD: Adversarial learning-based approach to defend against website
fingerprinting,” in Proc. IEEE Conf. Comput. Commun. (IEEE INFOCOM), Toronto, ON, Canada, Jul. 2020, pp. 2459–2468.
[42] J. Ainslie et al., “ETC: Encoding long and structured inputs in transformers,” in Proc. Conf. Empirical Methods Natural Lang. Process.
(EMNLP). Stroudsburg, PA, USA: Association for Computational Linguistics, 2020, pp. 268–284.
[43] Z. Dai, G. Lai, Y. Yang, and Q. Le, “Funnel-transformer: Filtering
out sequential redundancy for efficient language processing,” in Proc.
Adv. Neural Inf. Process. Syst., Annu. Conf. Neural Inf. Process. Syst.
(NeurIPS), vol. 33, Dec. 2020, pp. 4271–4282.
[44] A. Paszke et al., “PyTorch: An imperative style, high-performance deep
learning library,” in Proc. Adv. Neural Inf. Process. Syst., vol. 32. Curran,
2019, pp. 8024–8035.
[45] I. Loshchilov and F. Hutter, “Decoupled weight decay regularization,” in
Proc. 7th Int. Conf. Learn. Represent. (ICLR), New Orleans, LA, USA,
May 2019, pp. 1–19.
[46] W. S. Gosset, “The probable error of a mean,” Biometrika, vol. 6, no. 1,
pp. 1–25, Mar. 1908.
[47] T. Chothia, Y. Kawamoto, and C. Novakovic, “A tool for estimating
information leakage,” in Computer Aided Verification—25th International Conference, CAV 2013, Saint Petersburg, Russia, July 13–19,
2013. Proceedings, vol. 8044. Springer, 2013, pp. 690–695.
[48] S. Li, H. Guo, and N. Hopper, “Measuring information leakage in
website fingerprinting attacks and defenses,” in Proc. ACM SIGSAC
Conf. Comput. Commun. Secur., Toronto, ON, Canada, Oct. 2018,
pp. 1977–1992.

Qiang Zhou received the B.Sc. degree in mathematics and applied mathematics and the Ph.D. degree
in computer science from the Beijing University of
Posts and Telecommunications, Beijing, China, in
2012 and 2021, respectively. Since 2021, he has been
a Lecturer with the School of Computer Science
and Communication Engineering, Jiangsu University. His research interests include encrypted traffic
analysis, network security, and machine learning.

ZHOU et al.: WF-TRANSFORMER: LEARNING TEMPORAL FEATURES

Liangmin Wang (Member, IEEE) received the B.S.
degree in computational mathematics from Jilin University, Changchun, China, in 1999, and the Ph.D.
degree in cryptology from Xidian University, Xi’an,
China, in 2007. He is currently a Full Professor with the School of Cyber Space and Security
Engineering, Southeast University, Nanjing, China.
He has published over 60 technical papers at premium international journals and conferences, such as
IEEE T RANSACTIONS ON I NTELLIGENT T RANS PORTATION S YSTEMS , IEEE T RANSACTIONS ON
V EHICULAR T ECHNOLOGY, the IEEE Global Communications Conference,
and the IEEE Wireless Communications and Networking Conference. His
research interests include data security and privacy. He has served as a TPC
Member for many IEEE conferences, such as IEEE ICC, IEEE HPCC, and
IEEE TrustCOM. He is a member of ACM. He is a Senior Member of the
Chinese Computer Federation. He has been honored as a “Wan-Jiang Scholar”
of Anhui Province since November 2013. He is an Associate Editor of Security
and Communication Networks.

Huijuan Zhu (Member, IEEE) received the master’s degree from the School of Computer Science
and Communication Engineering, Jiangsu University, Zhenjiang, China, in 2010, and the Ph.D. degree
from the School of Computer and Control Engineering, University of Chinese Academy of Sciences,
Beijing, China, in 2017. Since 2018, she has been
an Associate Professor with the School of Computer
Science and Communication Engineering, Jiangsu
University. Her research interests include malware
detection, data mining, deep learning, and pattern
recognition.

43

Tong Lu received the B.Sc. degree in the Internet of
Things engineering from Jiangsu University, Zhenjiang, China, in 2021, where he is currently pursuing
the master’s degree in software engineering. His current research interests include website fingerprinting
defense and machine learning.

Victor S. Sheng (Senior Member, IEEE) received
the master’s degree in computer science from the
University of New Brunswick, Canada, in 2003, and
the Ph.D. degree in computer science from Western University, Ontario, Canada, in 2007. He was
an Associate Research Scientist and a NSERC
Post-Doctoral Fellow in information systems with
the Stern Business School, New York University,
after he obtained the Ph.D. degree. He is currently an
Associate Professor of computer science with Texas
Tech University and the Founding Director of the
Data Analytics Laboratory (DAL). His research interests include data mining,
machine learning, and related applications. He is a Lifetime Member of the
ACM. He received the Test-of-Time Award for research from KDD 2020, the
Best Paper Award Runner-Up from KDD 2008, and the Best Paper Award
from ICDM 2011. He is an area chair and a SPC/PC member of a number of
international conferences. He is a reviewer of several international journals.
PAPER_TEXT
