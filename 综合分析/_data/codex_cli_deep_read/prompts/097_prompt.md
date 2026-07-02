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
# [097] An Efficient Approach for Encrypted Traffic Classification using CNN and Bidirectional GRU
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
编号：097
题名：An Efficient Approach for Encrypted Traffic Classification using CNN and Bidirectional GRU
年份：2022
DOI：10.1109/iccece54139.2022.9712708
来源：2022 2nd International Conference on Consumer Electronics and Computer Engineering (ICCECE)
PDF：paper/10.1109_iccece54139.2022.9712708.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 15
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\097.txt
- 原始字符数：28653
- 本次发送字符数：28653
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2022 2nd International Conference on Consumer Electronics and Computer Engineering (ICCECE)

2022 2nd International Conference on Consumer Electronics and Computer Engineering (ICCECE) | 978-1-6654-0886-8/22/$31.00 ©2022 IEEE | DOI: 10.1109/ICCECE54139.2022.9712708

An Efficient Approach for Encrypted Traffic
Classification using CNN and Bidirectional GRU
ChengYuan Lin
Department of Automation
Xiamen University
Xiamen, China
18859272172@163.com

BaiHua Chen
Department of Automation
Xiamen University
Xiamen, China
bhchenxmu@hotmail.com

WeiYao Lan*
Department of Automation
Xiamen University
Xiamen, China
wylan@xmu.edu.cn
*Weiyao Lan is the corresponding author.
Abstract—With the rapid development of the Internet, the
amount and types of network traffic have increased dramatically
in tandem. Therefore, precise network traffic classification has
become an essential aspect of network management. Furthermore,
as user privacy and data encryption requirements have grown,
more encrypted traffic has evolved. Because of the wide variety of
encryption techniques and methodologies, network traffic
categorization has become extremely challenging. Traditional
traffic classification methods have been unable to meet the
demand for classification accuracy. In this study, we propose a
network structure that combines CNN and Bi-GRU to learn the
temporal and spatial features of encrypted traffic data. We utilize
the public dataset ISCX VPN-nonVPN to evaluate the effect of our
model, and we use accuracy, recall, and F1 score as criteria. Finally,
our model had a classification accuracy of 93.1%, with a recall rate
of 93.7% and an F1 score of 93.6%. We also discussed about the
differences between Bi-GRU and LSTM in terms of model
parameter scale and time efficiency. Experiments show that BiGRU has the greatest classification effect and efficiency.
Keywords: Deep Learning; Network Traffic Classification; CNN;
Bi-GRU

I.
INTRODUCTION
With the rapid development of Internet communication
technology in recent years, the network has become an integral
element of people's work and lives. People's requirements have
gotten more diverse and varied as the Internet has grown,
resulting in additional application situations and developmental
direction. The perception and monitoring of Internet traffic has
become increasingly critical in such an environment. In today's
network management system, network traffic categorization is
a critical responsibility. The main goal is to predict the network
data flow protocol and application type. Traffic categorization
activities are crucial to network management and service
quality with the fast development of high-throughput traffic
demand. Hence, network traffic classification has aroused
significant interest in academia and industry, and an increasing
number of academics are paying attention to it.

In recent years, with the fast development in demand for
protecting transmission data and user privacy, an increasing
number of apps and protocols have begun to send data using
encryption technologies, and the share of encrypted traffic in
the network has grown dramatically. Various encryption
mechanisms are now in use on the network. SSH, IPsec, TLS,
and other encryption protocols were introduced in [1]. It is
challenging to create a generic categorization system due to the
variances in protocols and encryption techniques. The
categorization of traffic poses significant difficulties.
Traditional traffic categorization approaches such as port-based
and deep packet inspection can’t tackle this sort of problem well
since encrypted communication is no longer in plaintext. At the
moment, machine learning methods are primarily used to solve
the problem of encrypted traffic classification, but this type of
method requires the extraction of characteristics from network
data streams, which means that developing an encrypted traffic
classification system based on machine learning requires a
significant amount of labor and domain knowledge. Migration
and large-scale applications are tough to achieve. It is vital to
re-extract features and train classifiers as new traffic kinds
occur. Furthermore, owing to the limits of the machine learning
model, the quality of the picked features typically impacts the
classifier's ultimate effect, resulting in low classification
accuracy. Deep learning, on the other hand, has advanced
significantly in recent years, and an increasing number of
academics have successfully implemented it in their specialties.
This has also resulted in fresh concepts and solutions for the
problem of classified encrypted traffic.
Therefore, this study provides a deep learning-based
solution for encrypting traffic categorization. The network
employs a hybrid paradigm that combines CNN and Bi-GRU.
A bidirectional GRU network is known as Bi-GRU. The spatial
features of data are learned using a one-dimensional CNN.
GRU, being a kind of recurrent neural network, inherits the
benefits of LSTM while also having a simpler structure, making
it more effective in network training. The network can learn the
forward and backward features, and our model can learn the

978-1-6654-0886-8/22/$31.00 ©2022 IEEE
368

Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:22:02 UTC from IEEE Xplore. Restrictions apply.

spatial and temporal properties of the traffic data, by using BiGRU to receive the output after convolution.

efficient network is critical, this research offers a network
model based on a CNN and Bi-GRU combination.

The remainder of this article is structured in the following
manner. Section II discusses related work. Section III describes
the design and implementation of the proposed method. Section
IV mainly convers evaluation methods and experimental results.
Section V presents conclusions and future work.

III. METHOLOGY

II.

A.

Dataset
Owing to the majority of the dataset utilized in the articles
are inconsistent, they often employ private dataset for network
traffic categorization tasks. As a result, utilizing universal
criteria to compare models and algorithms is problematic.
Therefore, we used the publicly available ISCX VPN-nonVPN
dataset, which was generated by the University of New
Brunswick team. This dataset includes 26GB of encrypted
traffic data in pcap and pcapng formats. The flow features of
the dataset may be split into 14 categories, according to their
paper's description, including Browse, Email, Chat and so on.
However, due to the dataset's homogeneity, it's hard to tell the
difference between the Browser and Streaming categories.
Finally, we used [8]'s approach to divide the traffic data into 12
categories, six of which are VPN categories and others are not.
Table I lists the specific category and size information.

RELATED WORK

The existing approaches for encrypted traffic classification
are classified from several viewpoints of the characteristics and
models. Machine learning-based approaches and deep learningbased methods are the most often utilized methods nowadays.
A.

Machine learning based methods
Velen et al. [1] studied papers on the classification of
encrypted traffic between 2005 and 2015, and the research
shows that before deep learning is widely used, payload-based
and feature-based network classification methods are the main
methods of encrypted traffic classification. Sun et al. [2]
proposed an encrypted traffic classification method based on
the naive bayes method. They used a hybrid method based on
signature and statistical analysis and achieved a classification
accuracy of more than 99%. Arndt [3] examined the impact of
C4.5, k-means, and a multi-objective genetic algorithm on
network traffic categorization. According to the study, C4.5
performs better in the categorization effect. In [4, 5], the support
vector machine is used to classify applications. Among these
methods, the feature selection method requires manual
extraction of features for each category. This method
necessitates extensive prior knowledge of the area, resulting in
the model's weak generalization skills and inability to migrate
to new settings.

TABLE I.
Traffic Type

Content

Size

Chat

ICQ, AIM, Skype, Facebook
and Hangouts

29.5M

VPN-Chat
Email
VPN-Email
File
VPN-File
Streaming

B.

Deep learning based methods
With the rapid development of deep learning, researchers
have started to apply deep learning technology to implement
encrypted traffic classification. Rezaei et al. [6] summarized
different models for network traffic classification, of which
convolutional neural networks are the most widely used. Wang
et al. [7] was the first to apply CNN to network traffic
classification. They proposed different traffic representation
methods, among which session and all layers achieved the best
results. Besides, they proposed using one-dimensional
convolution neural networks to create an end-to-end encrypted
traffic classification method [8]. They have an accuracy rate of
86.6% in the public dataset ISCX VPN-nonVPN [9] traffic
classification. They also proposed in [10] that the HAST-IDS
algorithm combined with CNN and LSTM be used to the
DARPA1998 and ISCX2012 datasets, with 99 percent accuracy.
Lotfollahi et al. [11] compares the classification results of onedimensional CNN and stacked auto-encoders (SAEs), and
experiments show that one-dimensional convolution is better.
In [12, 13], they all advocated using an attention mechanism
and a recurrent neural network to achieve traffic categorization.
Although CNN is commonly used in these deep learning
approaches, but CNN may not be able to learn the data's
temporal properties. LSTM has succeeded with sequence data,
however due to the complexity of the classification problem, it
may be restricted by memory. Therefore, a lightweight and

ISCX VPN-NONVPN DATASET

VPN-Streaming
VoIP
VPN-VoIP
Torrent
VPN-Torrent

Email, Gmail ( SMPT, POP3,
IMAP )
Skype, FTPS and SFTP

27.6M
13M
7.8M
17.3G
279M

Vimeo, Youtube, Netflix,
Spotify

1.53G

Facebook, Skype and
Hangouts voice calls

4.48G

uTorrent, Bittorrent

1.37G

360M
96.8M
358M

B.

CNN Model
Convolutional neural networks have had a lot of success in
a variety of domains, including speech recognition, picture
recognition, natural language processing and others. CNN
extracts feature by convolution and then lowers the order of
magnitude of network parameters through convolutional weight
sharing and pooling. CNN bypasses the difficult feature
extraction method since it can successfully learn features from
a large amount of data. Considering network traffic data is
structured sequence data, we use CNN as part of our model to
learn the spatial properties of the traffic data. The CNN
hierarchy is as follows:
1) Input: Let 𝑥 be the L-dimensional data of one of the
session data including n packets, where ⨁ is the concatenation
operator, and input data 𝑥 may be written in series as
𝑥 ,𝑥 ,…,𝑥 .
369

Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:22:02 UTC from IEEE Xplore. Restrictions apply.

𝑥:

𝑥 ⨁𝑥 ⨁ … ⨁𝑥

1

𝑅

2) Convolution operation: The convolution operation
actually applies the convolution kernel 𝑤 to the sequence data.
Where 𝑤 denotes the weight of the h-byte traffic data and 𝑏
denotes the deviation term.
𝑐

𝑓 𝑤⋅𝑥:

𝑏

𝑐 ,𝑐 ,…,𝑐

ℎ

ℎ

6

tanh 𝑊𝑥

𝑟 ⨀𝑈ℎ

7

The outputs of the update gate and the reset gate must be
mixed in the final phase.
ℎ

3

max 𝑐

𝑈

where ⨀ represents an element-wise multiplication symbol.

2

𝑧 ⨀ℎ

1

𝑧 ⨀ℎ

8

The state of a unidirectional neural network structure is
always output from front to back. Bidirectional GRU is a neural
network model made up of unidirectional and opposing GRUs,
the output of which is dictated by the states of these two GRUs.
A framework like this can collect more detailed and precise
information. Therefore, our network employs a bidirectional
⃖ is the forward output of GRU and ℎ⃗ is
GRU. Assuming ℎ
the backward output of GRU, then BiGRU's output may be
represented as:

3) Pooling operation: The pooling operation can minimize
the dimensionality of the feature map, reducing the amount of
parameters ultimately transferred to the fully connected layer
and increasing computation performance while avoiding
overfitting. Finally, we use the maximum pooling approach.
𝑐̂

𝑥

The output will employ the reset gate to save important
information in the past, and its calculation expression is:

The final feature map formed after the convolution kernel
passes through each flow data window is:
𝑐

𝜎 𝑊

4

C. GRU Model
Recurrent neural networks are mostly used to learn the
temporal properties of network traffic sequences. LSTM [14]
and GRU [15] are two extensively utilized recurrent neural
networks. To simulate long-term context and other interactions,
LSTM employs a gating mechanism that allows the recurrent
neural network to not only recall prior information, but also to
selectively forget certain unimportant information. GRU may
be thought of as an LSTM. It is a version that addresses the issue
of disappearing gradients while preserving long-term sequence
information. More than that, the parameters are less and training
time of GRU during training are quicker than LSTM, which is
why we use GRU as part of our network.

ℎ

⃖
ℎ⃗ , ℎ

9

D. Network Structure

1) Update gate: The update gate assists the model in
determining how much information from the past should be
given to the future, or how much information from the previous
and current time steps should be passed on. This is quite
powerful since the model may choose to replicate all previous
information to minimise the danger of disappearing gradients.
𝑍

𝜎 𝑊

𝑥

𝑈

ℎ

Figure 1.

5

Network structure

Given that network traffic data is organized and has
temporal characteristics, we perform network traffic
classification tasks using a framework that combines
convolutional neural networks and recurrent neural networks.
Figure 1 depicts our neural network structure diagram.

Where 𝑥 is the t-th time step's input vector, that is, the t-th
component of the input sequence 𝑥 that will be linearly
transformed (multiply by the weight matrix 𝑊 ). ℎ
preserves information from the previous time step 𝑡 1 and
also performs the linear transformation. The update gate
combines these two pieces of information and feeds them into
the sigmoid activation function, compressing the activation
result to a value between 0 and 1.

As shown in Figure 1, the input data is initially sent through
a one-dimensional convolutional neural network. The
convolutional layer has 32 filters, a convolution kernel width of
3, a step size of 1, and padding of 1. The next convolution layer
has 64 filters, a convolution kernel with a step size of 2, and the
rest is the same as the first layer of convolution. The ReLU
activation function is present in all convolutional layers.

2) Reset gate: The reset gate primarily decides how much
past information must be erased.

370

Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:22:02 UTC from IEEE Xplore. Restrictions apply.

Because each data packet's dimensionality is quite high, each
convolution is followed by a maximum pooling operation with
a width of 2 and a step size of 2 to minimize the data
dimensionality. The spatial properties of the data are retrieved
after convolution. The network data is context-sensitive since it
has temporal properties. Bi-GRU is a network structure that
learns the timing characteristics of data packets in order to
determine the forward direction of network traffic as well as
backward information. Bi-GRU learns temporal characteristics,
transfers them to a fully connected network, and then outputs
the final category through a Softmax layer. It's worth
mentioning that after the convolution and recurrent neural
networks, a dropout layer is linked, with a dropout rate of 0.2.
This step prevents the network from being overfit.
IV. EXPERIMENT
A.

Data Preprocessing
Data preprocessing is necessary for the ISCX VPN nonVPN dataset since it comprises the actual flow data, which is
kept in packets. The following are the particular steps:

Figure 2.

The number of different classes of data

3) Data representation: The data packet is made up of a
byte array with a data range of [0, 255] for each byte. As a result,
we should first normalize these values and translate them to the
range [0, 1]. After finishing data normalization, we transform
the data into a N * L matrix format, where N indicates the
number of data packets contained in each session, and L
represents each packet's first L bytes of data. If a data packet's
length is less than L bytes, the data must be filled with 0 to L
bytes. If the data packet's length exceeds L bytes, the surplus
data must be trimmed.

1) Data segmentation: We separate the original flow data
and the huge data file into little files based on session in this
stage. The flow data is segmented by source port, source IP,
destination port, destination IP, and transport layer protocol.
However, flow data is only in one direction., but flow data in
both directions is included in the session. As a consequence, the
session has additional details about both persons involved in the
contact. The raw traffic data comprises 310457 session data
once data segmentation is done.
2) Remove useless information: Each data packet is made
up of TCP/IP protocol, and the data link layer information isn't
particularly useful for later categorization, thus the data link
layer data can be removed. HTTPS and QUIC are the most often
used protocols for encrypted transmission. There are also other
irrelevant data packets that should be eliminated, such as DNS
protocol and others. Furthermore, because the dataset will
employ numerous fixed IP addresses or ports to gather related
category data during the collection process, it is extremely
possible that one IP will collect a specific category of data,
which will introduce additional information into the model that
must be deleted. The number of session data is shown in Figure
2. After eliminating unnecessary data packets, there are
46,986 session data in total.

B.

Evaluation
1) Experiment environment: PyTorch was chosen as the
deep learning framework for our experiment since it enables
GPU execution and is easier to implement. As a result, PyTorch
is used for all of the training and testing in this experiment. The
experimental environment is Windows 10 version 20H2 with an
AMD Ryzen 5 3600 3.60GHz CPU, 16GB of RAM, and an
Nvidia GeForce GTX 1650 graphics card (4GB).
The ISCX VPN-nonVPN dataset was utilized in the
experiment. As previously stated, we have a total of 46,986
sample data. We randomly shuffle the data set and then divide
it into training, validation, and test sets in an 8:1:1 ratio. The
training and validation sets are primarily utilized for model
training, whereas the test set is used to evaluate the model once
model training is done.
The model's parameters are as previously stated. The
parameters that must be learned are primarily the CNN and BiGRU parameters, as well as the weight parameters of the fully
connected layer and the output layer. The learning rate, the
number of data packets contained in each sample N, the number
of bytes contained in each data packet L, and the batch size of
the model are all hyperparameters that must be specified. In the
experiment, we set the starting learning rate to 0.001 and utilize
the Adam optimization technique as the backpropagation
optimization algorithm. According to [16], the first few data
packets of each flow may be used to complete the classification,
hence the experiment took N to be 5, 10, 20, and L to be 64,
128, 256, 512, or 1024. The experimental results reveal that the
test set has the greatest influence when N is 5 and L is 1024.
371

Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:22:02 UTC from IEEE Xplore. Restrictions apply.

Therefore, the number of data packets N is 5 and the number of
bytes is 512. The batch size of the model is set to 64. Table II
depicts the model's detailed structure.
TABLE II.

CNN + LSTM

0.934

CNN + Bi-LSTM

0.932

CNN + GRU

0.928

CNN + Bi-GRU

0.931

DETAILS OF DEEP LEARNING NETWORK MODELS

Model

Architecture Detail

CNN + LSTM

CNN + Bi-LSTM

CNN + GRU

CNN + BiGRU

Conv1d(5, 32, 3, 1, 1)-ReLU()-MaxPool(2, 2)Conv1d(32, 64, 3, 2, 1)-ReLU()-MaxPool(2, 2)Dropout(0.2)-LSTM(256)-LSTM(128)Dropout(0.2)-FC(64)-FC(12)
Conv1d(5, 32, 3, 1, 1)-ReLU()-MaxPool(2, 2)Conv1d(32, 64, 3, 2, 1)-ReLU()-MaxPool(2, 2)Dropout(0.2)-Bi-LSTM(128)-Dropout(0.2)-FC(64)FC(12)
Conv1d(5, 32, 3, 1, 1)-ReLU()-MaxPool(2, 2)Conv1d(32, 64, 3, 2, 1)-ReLU()-MaxPool(2, 2)Dropout(0.2)-GRU(256)-GRU(128)-Dropout(0.2)FC(64)-FC(12)
Conv1d(5, 32, 3, 1, 1)-ReLU()-MaxPool(2, 2)Conv1d(32, 64, 3, 2, 1)-ReLU()-MaxPool(2, 2)Dropout(0.2)-Bi-GRU(128)-Dropout(0.2)-FC(64)FC(12)

The accuracy of the model integrated with CNN and RNN
may be increased by roughly 2%, as shown in Table III. The
result of combining CNN and LSTM is the best, whereas CNN
and Bi-GRU is just 0.3% less effective. According to the
findings of the experiments, this combination approach can
learn more information in encrypted traffic categorization,
making it a useful technique.

2) Evaluation metrics: Network traffic classification is
fundamentally a multi-classification task, and there are an
increasing number of evaluation criteria of classification result,
the most frequent of which is accuracy. In addition to the
accuracy rate, this paper utilizes the precision rate, recall rate,
and F1 score as model evaluation indicators. Assuming N is the
total number of samples, 𝑇𝑃 is the number of original category
c and predicted as c, 𝐹𝑃 is the number of actual categories that
are not category c but the predicted category is category c, 𝑇𝑁
means the actual category is not c and the predicted category is
not c, and 𝐹𝑁 means the actual category is c but the expected
category is the number of other categories. As a result, the four
evaluation indications listed above can be written as follows:
𝐴𝑐𝑐𝑢𝑟𝑎𝑐𝑦
𝑅

∑ 𝑇𝑃
,𝑃
𝑁

𝑇𝑃
, 𝐹1
𝑇𝑃 𝐹𝑁

𝑇𝑃
𝑇𝑃

𝐹𝑃

2∗𝑃 ∗𝑅
𝑃 𝑅

One-dim CNN

0.866

Deep Packet

0.898

Attention Based LSTM

0.912

The F1 score comparison of 4 models

TABLE IV.

Accuracy
0.800

Figure 4.

11

THE ACCURACY OF DIFFERENT MODELS

C4.5

The recall comparison of 4 models

10

C. Experimental Result Analysis
It is difficult to compare the algorithms in other articles due
to changes in the data collection and experimental setting
applied in the study. As a consequence, we chose [8, 11, 12] for
comparison, which employed the same dataset as this paper,
and the results of the experiment are displayed in Table III.
TABLE III.

Figure 3.

THE COMPARISON OF EFFICIENCY
weights

Training time(ms)

Test time(ms)

CNN + LSTM

4672k

212

40.6

CNN + Bi-LSTM

4468k

179

36.0

CNN + GRU

3508k

185

36.3

CNN + BiGRU

3387k

166

35.0

The comparisons in Figures 3 and 4 are mostly between
different CNN and RNN combinations. GRU's recall and F1
score are tiny in comparison to LSTM, with the exception of the
Torrent category, and the other categories are similar or even

372

Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:22:02 UTC from IEEE Xplore. Restrictions apply.

greater. Table IV shows that using a bidirectional RNN is
superior than using a unidirectional RNN in terms of model
parameters and operating efficiency, with Bi-GRU having the
shortest parameter scale and the best operational efficiency. The
accuracy of the Bi-GRU model is somewhat lower than that of
the LSTM model, but the network parameters are 27% lower
and the time efficiency is 13.8% quicker. Due to the vast
volume of network traffic data, this time benefit will be more
apparent in the real-world network environment. As a result, the
high criteria for precision in industrial production may be
relaxed, and the adoption of Bi-GRU instead of LSTM can
drastically cut manufacturing costs.

International Conference on Intelligence and Security Informatics (ISI).
IEEE, 2017: 43-48.
[9] Draper-Gil G, Lashkari A H, Mamun M S I, et al. Characterization of
encrypted and vpn traffic using time-related[C]//Proceedings of the 2nd
international conference on information systems security and privacy
(ICISSP). 2016: 407-414.
[10] Wang W, Sheng Y, Wang J, et al. HAST-IDS: Learning hierarchical
spatial-temporal features using deep neural networks to improve intrusion
detection[J]. IEEE access, 2017, 6: 1792-1806.
[11] Lotfollahi M, Siavoshani M J, Zade R S H, et al. Deep packet: A novel
approach for encrypted traffic classification using deep learning[J]. Soft
Computing, 2020, 24(3): 1999-2012.
[12] Yao H, Liu C, Zhang P, et al. Identification of encrypted traffic through
attention mechanism based long short term memory[J]. IEEE
Transactions on Big Data, 2019.
[13] Liu X, You J, Wu Y, et al. Attention-based bidirectional GRU networks
for efficient HTTPS traffic classification[J]. Information Sciences, 2020,
541: 297-315.
[14] Hochreiter S, Schmidhuber J. Long short-term memory[J]. Neural
computation, 1997, 9(8): 1735-1780.
[15] Chung J, Gulcehre C, Cho K H, et al. Empirical evaluation of gated
recurrent neural networks on sequence modeling[J]. arXiv preprint
arXiv:1412.3555, 2014.
[16] Vu L, Thuy H V, Nguyen Q U, et al. Time series analysis for encrypted
traffic classification: A deep learning approach[C]//2018 18th
International Symposium on Communications and Information
Technologies (ISCIT). IEEE, 2018: 121-126.

V. CONCLUSION
In this research, we focus on the categorization of encrypted
network traffic, and we suggest a network structure based on
CNN and RNN to accomplish the task. Taking into account the
temporal and spatial characteristics of network traffic data, we
extract the data of the first few packets in the data stream, and
then perform data preprocessing through operations such as
padding, truncation, and normalization. Convolution is used to
learn the spatial characteristics of the data, and Bi-GRU is used
to learn the temporal characteristics of the data, reducing the
parameter scale of the model while ensuring classification
accuracy and increasing classification efficiency. The results of
the experiment reveal that CNN and Bi-GRU considerably
increased classification and classification efficiency, which is a
good notion for dealing with encrypted traffic classification.
In the future, as RNN has some weaknesses in processing
network traffic, it will be restricted mostly by sequence length
and time efficiency. Our main focus will be on developing a
system that can take the place of RNN. Because the attention
mechanism and transformer are becoming increasingly
common in sequence data, including these structures into the
network may have a positive classification impact.
REFERENCES
[1]

[2]

[3]

[4]

[5]

[6]
[7]

[8]

Velan P, Čermák M, Čeleda P, et al. A survey of methods for encrypted
traffic classification and analysis[J]. International Journal of Network
Management, 2015, 25(5): 355-374.
Sun G L, Xue Y, Dong Y, et al. An novel hybrid method for effectively
classifying encrypted traffic[C]//2010 IEEE Global Telecommunications
Conference GLOBECOM 2010. IEEE, 2010: 1-5.
Arndt D J, Zincir-Heywood A N. A comparison of three machine learning
techniques for encrypted network traffic analysis[C]//2011 IEEE
Symposium on Computational Intelligence for Security and Defense
Applications (CISDA). IEEE, 2011: 107-114.
Alshammari R, Zincir-Heywood A N. Machine learning based encrypted
traffic classification: Identifying ssh and skype[C]//2009 IEEE
symposium on computational intelligence for security and defense
applications. IEEE, 2009: 1-8.
Kumano Y, Ata S, Nakamura N, et al. Towards real-time processing for
application identification of encrypted traffic[C]//2014 International
Conference on Computing, Networking and Communications (ICNC).
IEEE, 2014: 136-140.
Rezaei S, Liu X. Deep learning for encrypted traffic classification: An
overview[J]. IEEE communications magazine, 2019, 57(5): 76-81.
Wang W, Zhu M, Zeng X, et al. Malware traffic classification using
convolutional neural network for representation learning[C]//2017
International Conference on Information Networking (ICOIN). IEEE,
2017: 712-717.
Wang W, Zhu M, Wang J, et al. End-to-end encrypted traffic classification
with one-dimensional convolution neural networks[C]//2017 IEEE

373

Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:22:02 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
