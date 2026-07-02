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
# [075] CENTIME: A Direct Comprehensive Traffic Features Extraction for Encrypted Traffic Classification
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
编号：075
题名：CENTIME: A Direct Comprehensive Traffic Features Extraction for Encrypted Traffic Classification
年份：2021
DOI：10.1109/icccs52626.2021.9449280
来源：2021 IEEE 6th International Conference on Computer and Communication Systems (ICCCS)
PDF：paper/10.1109_icccs52626.2021.9449280.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 10
已有代码状态：已下载；Traffic-Classification -> source\Traffic-Classification

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\075.txt
- 原始字符数：43960
- 本次发送字符数：43960
- 是否截断：False

代码包：
- 仓库：Traffic-Classification
  - URL：https://github.com/wmn7/Traffic-Classification
  - 状态：downloaded
  - 本地目录：source\Traffic-Classification
  - 顶层结构：.gitignore、.vscode/、LICENSE、README.md、TrafficFlowClassification/、baseline_model/、checkpoint/、data/、doc/、pcaps_size_record.json、statistic_features.json、tool/
  - 主要语言：Python:40、Jupyter:5、JSON:2、YAML:1
  - README 标题：Introduction、Data Preprocessing、Model Train、Introduction、Data Preprocessing、Model Train、Introduction、Data Preprocessing、Model Train
  - README 运行线索：python python -m TrafficFlowClassification preprocess_pipeline；python model = resnet181D(model_path, pretrained=cfg.test.pretrained, num_classes=12, image_width=cfg.train.IMAGE_WIDTH).to(device)；python python -m TrafficFlowClassification train_pipeline；python python -m TrafficFlowClassification preprocess_pipeline；python model = resnet181D(model_path, pretrained=cfg.test.pretrained, num_classes=12, image_width=cfg.train.IMAGE_WIDTH).to(device)；python python -m TrafficFlowClassification train_pipeline；python python -m TrafficFlowClassification preprocess_pipeline；python model = resnet181D(model_path, pretrained=cfg.test.pretrained, num_classes=12, image_width=cfg.train.IMAGE_WIDTH).to(device)
  - 关键文件：{"数据处理入口": ["TrafficFlowClassification/entry/preprocess.py", "TrafficFlowClassification/preprocess/FeaturesCalc.py"], "训练入口": ["TrafficFlowClassification/entry/train.py", "TrafficFlowClassification/train/trainProcess.py"], "评估/测试入口": ["TrafficFlowClassification/preprocess/test_splitTrian.py", "TrafficFlowClassification/train/validateProcess.py", "TrafficFlowClassification/utils/evaluate_tools.py"]}
  - 数据集线索：Tor、VPN、dapt、tor、ustc、vpn

论文正文包开始：
<<<PAPER_TEXT
2021 IEEE the 6th International Conference on Computer and Communication Systems

2021 IEEE 6th International Conference on Computer and Communication Systems (ICCCS) | 978-1-6654-1256-8/21/$31.00 ©2021 IEEE | DOI: 10.1109/ICCCS52626.2021.9449280

CENTIME: A Direct Comprehensive Traffic
Features Extraction for Encrypted Traffic
Classification
Maonan Wang1 , Kangfeng Zheng1,* , Xinyi Ning2 , Yanqing Yang1,3 and Xiujuan Wang4
1

School of Cyberspace Security, Beijing University of Posts and Telecommunications, Beijing, China
1
School of International, Beijing University of Posts and Telecommunications, Beijing, China
3
College of Information Science and Engineering, Xinjiang University, Urumqi, China
4
Faculty of Information Technology, Beijing University of Technology, Beijing, China
e-mail: wangmaonan@bupt.edu.cn, zkf bupt@163.com,
ningxinyi@bupt.edu.cn, qing0991@163.com, xjwang@bjut.edu.cn

Abstract—With the rapid development of the network, encrypted traffic classification plays a vital role in guaranteeing
the quality of network services and ensuring the security of the
network. Recent studies show that machine learning approaches
based on statistical features and raw traffic sessions are effective
for this task. However, the performance of the statistical-based
approaches largely depends on the quality of the features. Experts
need to design different features for different encrypted traffic
classification tasks, which is time-consuming. Meanwhile, the raw
traffic-based approach needs to uniformize the traffic size; this
will cause the loss of information about the overall structure of
the network traffic; for example, we do not know the time from
the first packet to the last packet in a session. This paper proposes
the CENTIME, which can extract comprehensive information
based on ResNet and AutoEncoder to identify encrypted traffic.
ResNet is used to extract information from uniformized traffic,
and AutoEncoder is used to encode statistical features. The
statistical features are used to compensate for the information loss
caused by traffic uniformization. They only need to be designed
once rather than be designed separately for different tasks.
Moreover, the pooling layers are removed, and 1D convolution
layers are used to help CENTIME make more effective use of
raw traffic information. We evaluate the CENTIME on the public
dataset “ISCX VPN-nonVPN”, and the results demonstrate the
CENTIME outperforms the state-of-the-art encrypted traffic
classification methods. More importantly, comprehensive traffic
features generated in the CENTIME can represent different
classes of traffic well.
Index Terms—Encrypted traffic classification, ResNet, AutoEncoder

I. I NTRODUCTION
With the rapid development of the Internet, network traffic
from different applications has risen rapidly. A large amount
of traffic makes it difficult for network operators to guarantee
the quality of services (QoS) [1] and ensure Internet security
[2]. Traffic classification, as one of the necessary technologies
for improving network service and ensuring network security,
This work is supported by the National Key R&D Program of China under
Grant no.2017YFB0802703 and the National Natural Science Foundation of
China under Grant no.61602052.

978-0-7381-2604-3/21/$31.00 ©2021 IEEE

has received increased attention from academic and industrial
fields these years [3].
The fastest and most effective approach to identify traffic
is to use the port number [4]. Some well-known Internet
services use the fixed port number, such as the HTTP service
applications usually use port 80 while FTP service applications
use port 21. However, as more and more new applications
avoid using standard registered port numbers, the accuracy of
the port-based approach has declined [5]. The next technology
to classify traffic relies on the payload. This technology is also
known as deep packet inspection (DPI) [6], which focuses on
finding patterns of specific string in traffic packet. In recent
years, as people have gradually paid attention to their privacy,
more and more applications have started to use encrypted
communication when transmitting any data, which has brought
considerable challenges to the above two traditional traffic
classification methods.
To solve these challenges, researchers adopt machine learning and deep learning methods for encrypted traffic classification. According to different inputs, the studies can be
divided into two categories, (1) statistical characteristics-based
approach and (2) raw traffic-based approach. To be specific,
the statistical-based approach assumes that different types of
traffic have unique statistical characteristics. Alshammari et al.
used packet-related features like “packet length”, “delta time
from previously captured packet”, and “IP flags” to identify
the encrypted traffic [7]. The raw traffic-based approach uses
the deep neural network to extract features from network traffic
automatically. For example, Wang et al. proposed an end-toend method based on the one-dimensional convolutional neural
network [8]. This method integrates feature extraction and
classifier into one unified framework. The result shows that
this method can achieve state-of-the-art performance on the
“ISCX VPN-nonVPN” dataset [9].
Although the previous technologies can obtain comparatively high accuracy, there still exits apparent shortcomings
of them. For the statistical-based approach, the performance

490

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:34:09 UTC from IEEE Xplore. Restrictions apply.

of the classification largely depends on the quality of the
features. Experts need to design different features for different
encrypted traffic classification tasks, which is time-consuming
and expensive. The main drawback of the raw traffic-based
approach is that it will cause a loss of information. Most
studies use convolutional neural networks to extract features
from raw encrypted traffic [8], [10], [11]. However, the convolutional neural networks need a fixed-sized input; therefore,
the raw encrypted traffic needs to be uniformized first. This
will cause information loss, especially information about the
overall structure of the network traffic. For example, we cannot
know the number of packets in a session, the time from the
first packet to the last packet in a session, and the minimum
or maximum delta time in a session after uniformizing, which
will reduce the classification performance.
For the sake of solving these limitations, we proposed a
framework named CENTIME. CENTIME can extract comprehensive features from network traffic and use these features to
classify encrypted traffic. There are three parts in CENTIME,
namely data preprocessing, traffic information extraction and
traffic classification. (1) In the part of data preprocessing, we
split the raw traffic by session-packets and then anonymize
them. (2) During the part of traffic information extraction,
we use ResNet [12] to extract features directly from raw
encrypted traffic. Compared with the previous researches, we
removed the pooling layer and used the one-dimensional convolution layer in CENTIME, hoping to extract more valuable
information from the raw traffic. Simultaneously, statistical
information is extracted from raw traffic too. We use AutoEncoder [13] to compress statistical information. This statistical
information is used to compensate for the information loss
caused by traffic trimming. They only need to be designed
once, containing information about the overall structure of the
traffic, rather than be designed separately for different tasks.
Finally, the information extracted by ResNet and encoded by
AutoEncoder are merged to form the comprehensive features.
(3) The comprehensive features are used to classify the encrypted traffic in the last part of CENTIME. To demonstrate
the feasibility of this framework, we perform 21 different
experiments, compared the CENTIME with six state-of-theart methods on the “ISCX VPN-nonVPN” dataset [9]. The
final results show that our proposed framework outperforms
other public methods in encrypted traffic classification.
The major contributions of this paper are as follows:
• We propose a novel framework named CENTIME, which
integrates traffic information extraction and encrypted
traffic classification into one framework. The framework generates comprehensive features based on the
uniformized traffic files and statistical information, then
uses these comprehensive features to classify encrypted
traffic.
• In this framework, we use 1D convolution layers and
remove the pooling layers to make more effective use
of raw traffic information.
• We evaluate our model with the six state-of-the-art
methods on the public dataset “ISCX VPN-nonVPN”.

Experimental results show that our method has a good
performance on classification; it achieves an f1-score of
0.99 in encrypted traffic classification. Besides, all the
relevant experimental data, such as training data, the code
for training, fine-tuned models and detailed experiment
results are published on GitHub1 .
The rest of the paper is organized as follows. Section II
summarizes the related work on traffic classification. Section
III describes the CENTIME framework, including three parts,
data preprocess, traffic information extraction and traffic classification. Section IV covers the experiment setup, evaluation
metrics, baseline methods and experiments results. Finally,
section V provides the conclusion and future studies that can
be engaged in.
II. R ELATED W ORK
Traffic classification technologies have developed fast over
time. There have been two traditional methods for classifying
network traffic: “port-based” and “content-based” [5]. Among
all these mature methods, deep packet inspection (DPI) is
considered one of the most reliable method [6]. DPI will not
only use the information in the packet headers (such as the port
number), but also use the payload of the traffic to classify
the network traffic. More specifically, DPI uses a signature
database containing information from some labelled packets to
identify the traffic. However, with the increased use of HTTPS
and other encryption methods like VPNs, the classification
accuracy based on DPI gradually decreases. We cannot decrypt
the payload; therefore, we cannot classify the network traffic
by using pattern matching to search for particular keywords
in the payload.
In order to classify encrypted traffic, the statistical-based
method is proposed. Most of the research based on traffic statistical features uses traditional machine learning algorithms,
such as decision tree or support vector machine (SVM).
For example, [14] presents a statistical classifier based on a
combination of k-nearest neighbour (K-NN) and k-means that
allows real-time classification of encrypted traffic. Alshammari
et al. use C4.5 [15] and AdaBoost [16] to unveil encrypted
application based on statistical flow feature [7]. Agrawal et al.
use five supervised ML algorithms, such as Naive Bayes Tree
and NaiveBayes, to identify P2P traffic based on statistical features like the port number [17]. Alshammari et al. also employ
statistical network traffic flow feature to identify encrypted
VoIP application in network traffic [18]. Vlăduţu et al. propose
a new technique by combining unsupervised algorithms (Kmeans, Expectation maximization) and supervised algorithms
(Decision tree) to classify Internet traffic [19]. Vu et al.
generate fake network traffic with the Synthetic Minority Oversampling Technique (SMOTE) [20] and modify the cost function to address the imbalanced encrypted traffic classification
problem based on statistical characteristics [21]. However, the
performance of these models heavily depends on the quality

491

1 https://github.com/wmn7/Traffic-Classification

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:34:09 UTC from IEEE Xplore. Restrictions apply.

Data Preprocessing

Traffic Information
Extraction

Encrypted Traffic
Classification

Information from Uniformized Traffic

Preprocess
Raw Traffic

1. Traffic Split
2. Traffic Clean

1. Trim Traffic File
2. Image Gneration
3. Extract Feature by ResNet
Information from Statistics

Traffic Classification
1. Generate Comprehensive
Feature
2. Predict Traffic

Predict Labels

1. Calculate 26 Statistical
Features
2. Encode these by AE

Fig. 1: Overview of the Structure of CENTIME.

of the human-engineered features, which significantly limits
the generalizability of the statistical-based method.
Recently, deep learning methods have been widely used
in encrypted traffic classification. The neural networks can
automatically extract features from the traffic payload, increasing the generalization of the model. Wang et al. propose
an end-to-end framework based on the convolution neural
network, which combines feature extraction, feature selection,
and classifier into one system [8]. Song et al. used a text
convolutional neural network to extract critical features for
traffic classification [10]. [22] proposes a session-packetsbased encrypted network traffic classification model using
capsule neural networks (CapsNet), which can learn the spatial
characteristics from network traffic well [23]. Shapira et al.
transformed the basic flow data into a picture and then used
image classification deep learning techniques to classify encrypted traffic [24]. Lotfollahi et al. proposed a scheme called
“Deep Packet”, which uses 1D-CNN and stacked autoencoder
(SAE) to extract features and make predictions [25].

TABLE I: Introduction to 12 Classes of Traffic in the “ISCX
VPN-nonVPN” Dataset

Non-VPN/VPN

Traffic Type

Total Size

non-VPN

Email
Chat
Streaming
File Transfer
P2P
VoIP

13 MB
29.5 MB
1.53 GB
17.3 GB
96.8 MB
4.48 GB

VPN

VPN-Email
VPN-Chat
VPN-Streaming
VPN-File Transfer
VPN-P2P
VPN-VoIP

7.8 MB
27.6 MB
1.37 GB
279 MB
358 MB
360 MB

III. T HE P ROPOSED M ETHOD
In this section, we propose a framework named CENTIME,
which is based on ResNet and AutoEncoder. As shown in
“Fig. 1”, CENTIME consists of three parts: data preprocessing,
traffic information extraction and traffic classification. During
the data preprocessing phase, we split raw traffic by sessionpackets, and then delete MAC and IP address. During the
phase of traffic information extraction, 26 statistical features
are calculated from raw traffic. After that, we uniformize the
raw traffic and then use ResNet to extract information from
the traffic. During the classification phase, we combine the
information from uniformized traffic and statistical features
to generate comprehensive features and use these features to
classify encrypted traffic. Dataset is also introduced in this
section.
A. Dataset
The most critical thing in deep learning is to have a
large number of datasets to avoid overfitting. However, there
are relatively few datasets in the field of encrypted traffic

classification. There are only some datasets generated in
the process of encrypted traffic identification research. For
example, UMass2 provides datasets related to Tor traffic [26]
and HTTPS traffic [27]. The “Campus” dataset is used to
identify different encryption algorithms [28].
Draper-Gil et al. proposed the “ISCX VPN-nonVPN”
dataset in 2016 [9]. There are 14 classes of traffic files, which
captured from different applications (i.e., Skype, BitTorrent),
in the “ISCX VPN-non VPN” dataset, including seven classes
of regular (non-VPN) traffic and seven classes of VPN traffic.
Because the “ISCX VPN-nonVPN” dataset includes rich types
of applications, it is widely used in the encrypted traffic
research field. The experiments in this paper are also based
on the “ISCX VPN-nonVPN” dataset.
In the ”ISCX VPN-nonVPN” dataset, the authors do not
give the labels to the traffic files but only give each traffic file
a brief description. This leads to some ambiguous traffic files.

492

2 http://traces.cs.umass.edu/index.php/Network/Network

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:34:09 UTC from IEEE Xplore. Restrictions apply.

(a) Size Distribution of Sessions

(b) Percentage of Session Size in each Interval

Fig. 2: Analysis of Session Size

For example, “Facebook video.pcap” can be either belong
to “Browser” or “Streaming”. Therefore, we removed these
ambiguous traffic files in this paper, and the final “ISCX VPNnonVPN” dataset has 12 classes. “Table. I” introduces the
detailed content of these 12 classes.
Chat
Chat

Email
Email

File Transfer
File Transfer

B. Data Pre-processing
Before extracting information from the traffic, we need to
perform data preprocessing first. There are two steps of data
preprocessing in the CENTIME framework, traffic split and
traffic clean.
Traffic Split. In this step, we divide the continuous traffic into multiply discrete traffic units. The continuous raw
traffic P contains the different size of packets pi , that is
P = {p1 , p2 , · · · , pN }. N represents the number of packets
in raw traffic P . A single packet pi is defined as (1),
pi = (xi , ti , bi ),

P2P
P2P

Streaming
Streaming

VoIP
VoIP

VPN-Chat
VPN-Chat

(a) Visualization of non-VPN Traffic
VPN-Email
VPN-Email

VPN-File
VPN-File

VPN-P2P
VPN-P2P

VPN-Streaming
VPN-Streaming

VPN-VoIP
VPN-VoIP

(b) Visualization of VPN Traffic

Fig. 3: Visualization of Encrypted Traffic (784 bytes)

(1)

where xi is the five-tuple, source IP, source port, destination
IP, destination port, and transport-level protocol. ti is the start
time of the packet, and bi is the byte length of the packet.
Session and flow are two common ways to split the traffic.
A flow Pf low is a group of traffic that has the same five-tuple,
which can be defined as (2).
Pf low = {p1 = (x1 , t1 , b1 ), · · · , pn = (xn , tn , bn )},

(2)

where x1 = · · · = xn and t1 < · · · < tn . The session
is very similar to flow, but the source IP and destination IP
can be interchanged [29]. We split the traffic into session in
this paper because Wang et al. found that the session contains
more interaction information than flow and is more suitable
for encrypted traffic classification [8].
Traffic Clean. After splitting the traffic into the session, we
delete their IP address and MAC address by masking related
strings with 0x00. Each traffic class has a unique IP address in
the “ISCX VPN-nonVPN” dataset; therefore, the model may
overfit if the IP address and MAC address are not deleted.
Empty files and duplicate files are also removed during traffic
clean.

493

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:34:09 UTC from IEEE Xplore. Restrictions apply.

C. Traffic Information Extraction
Our framework CENTIME can generate comprehensive
traffic features from the raw traffic. The comprehensive features are composed of two parts: the statistical information of
the raw traffic and the uniformized traffic information.
Information from Statistics (IFS). Before uniformizing
the traffic, we extract statistical features from it firstly. These
features can retain information on the overall structure of the
traffic. In this paper, we extract 26 statistical features, such
as “Num pkts” (the number of packets in a session), “Avg
syn flag” (the average of packets of with syn flag active in
a session), and “Duration window flow” (the time from the
first packet to the last packet in a session), etc. The detailed
information of these 26 extracted features can be seen in
[30]. After calculating the 26 statistical features, the min-max
normalization method is used to normalize data. That is,
xnew =

x − xmin
.
xmax − xmin

(3)

After the normalization process, all statistical features are
converted to a range [0, 1]. The AutoEncoder is used to encode
these 26 statistical features and extract effective information
from them.
Information from Uniformized Traffic (INUIT). In this
step, we use ResNet to extract information directly from
the raw traffic. Using ResNet needs a fixed-sized input, so
we uniformize the raw traffic to the same size. Suppose we
uniformize the raw traffic Si into N bytes. If the the size of
Si is larger than N bytes, only the first N bytes are retained;
otherwise, 0x00 will be added at the end of the traffic.
“Fig. 2a” shows the size distribution of the session in the
“ISCX VPN-nonVPN” dataset. It can be seen that most of
the session size is less than 1000 bytes. In this paper, the raw
traffic is uniformized into 784 bytes, 1024 bytes, and 4096
bytes (N = 784, 1024, 4096), respectively. All the experiments
in this paper are based on these three types of traffic data. As
shown in “Fig. 2b”, the session size in the range of [0, 784]
bytes accounted for 84% of the traffic, while only 3% of the
session size was in the range of [784, 1024] bytes. A total of
93% of the session size is between [0, 4096] bytes.
After all the traffic is uniformized, each byte in the session
corresponds to the grey-scale pixel value; for example, 0x00
means black, and 0xff means white. As shown in “Fig. 3”,
the 784 bytes session can be converted into a 28*28 matrix.
“Fig. 3a” shows the visualization of all non-VPN traffic
classes, and “Fig. 3b” shows the visualization of the VPN
traffic. It can be seen that patterns are different for different
traffic classes, while amony the same class of traffic, their
patterns are similar. Therefore, there is reason to presume that
ResNet can extract valid information from uniformized traffic.
D. Encrypted Traffic Classification (ERIC)
After the “Traffic Information Extraction” process, we got
the information from two parts: the information obtained from
the statistical features through the AutoEncoder Vstatistics ,
and the uniformized traffic information extracted by the

ResNet Vraw pcap . The two parts of information are merged
to form comprehensive traffic features V . We believe that
the comprehensive traffic features V include information both
from uniformized traffic and statistics of traffic. Then we
use the features V to classify encrypted traffic by using a
fully connected neural network. “Fig. 4a” shows the whole
process of “Traffic Information Extraction” and “Encrypted
Traffic Classification”. ResNet is used to extract information
from uniformized traffic. As shown in “Fig. 4a”, there are
four ResLayers in the ResNet; each ResLayer contains two
ResBlock. The structure of ResBlock can be seen in “Fig. 4b”.
The output channel of the convolution layer in the same
ResLayer is the same.
The main parameters of the models in CENTIME are
described in “Table. II”. There are two points to note in
the CENTIME framework, (1) 1D convolution layer is used
because the traffic data is sequence data. The performance of
the 1D convolution layer and 2D convolution layer will be
compared in section IV. (2) The pooling layer is removed in
the framework. The function of the pooling layer is to reduce
the spatial size of the input to reduce the number of parameters
in the network. However, the uniformized traffic size is not
large in this experiment, so we removed the pooling layer to
retain more helpful information. The performance of the model
with the pooling layer and without the pooling layer will also
be compared in section IV.
TABLE II: Main Parameters of the CENTIME
Layer

Operation

Input

Filter

Output

INUIT

Conv-1
ResLayer-1
ResLayer-2
ResLayer-3
ResLayer-4
Avg-Pooling
Flatten

conv1d * 1
conv1d * 4
conv1d * 4
conv1d * 4
conv1d * 4
Avg Pooling
faltten

1*784
32*784
32*784
64*364
128*182
256*91
256*1

1*9
1*3
1*3
1*3
1*3
-

32*784
32*784
64*364
128*182
256*91
256*1
256

IFS

Auto-Encoder-1
Auto-Encoder-2
Auto-Encoder-3
AutoEncoder-4

fully-connected
fully-connected
fully-connected
fully-connected

26
18
9
18

-

18
9
18
26

ERIC

Fully-connected-1
Fully-connected-2
Fully-connected-3

fully-connected
fully-connected
sotfmax

256+9
100
30

-

100
30
12

IV. E XPERIMENT
A. Experiment Setup
All the experiments are conducted on Ubuntu 16.04 64bit
OS. The hardware of the sever is Inter (R) Xeon (R) E5-2650
2.2 GHz with 32GB of memory. An Nvidia GTX1080Ti 11GB
GPU is used as the accelerator.
We use PyTorch [31] to build all the neural networks in this
paper. We randomly sampled 90% of the data as the training
data, and the rest is the test data. The mini-batch size is 256.
The initial learning rate is 0.001 and decay of 0.9 per 25
epochs. Adam optimizer [32], which inherits from RMSProp

494

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:34:09 UTC from IEEE Xplore. Restrictions apply.

Information from Statistics

Encrypted Traffic Classification
Min Reconstruction Error

Information from Statistics

Encrypted Traffic Classification
Information from Statistics

Min Reconstruction Error
Decode

Encode

Vstatistics

Decode

Information from Statistics
Encode

F

Vstatistics
...

...

...

...

...

...

...

...

...

F

...

...

...

...

...

...

...

...

...

Comprehensive
Feature, V
. .
. .

ResLayer 4

ResLayer 3

ResLayer 2

ResBlock

ResBlock

Conv1D

...

Vraw_pcap

...

Kernel Size, 3
Output Channel, 32

....

ResLayer 4

ResLayer 3

ResLayer 2

ResBlock

Information from Uniformed Traffic

ResLayer 1

Information from
Uniformed Traffic

...

Conv1D

F

ResBlock

Flatten

Predicted Results

Predicted Results

...

. .
. .
....

Flatten
F

Traffic Matrix
• [28×28×1]
• [32×32×1]
• [64×64×1]

Vraw_pcap

Kernel Size, 3
Output Channel, 32

Traffic Matrix
• [28×28×1]
• [32×32×1]
• [64×64×1]

Comprehensive
Feature, V

Information from
Uniformized Traffic

ResLayer 1

Information from Uniformized Traffic
(a) The Process of “Traffic Information Extraction” and “Encrypted Traffic Classification”

Convolution 1D

Batch Norm 1D

ReLU

Convolution 1D

Batch Norm 1D
ReLU

(b) Structure of ResBlock

Convolution 1D
Norm 1D of the
ReLU
1D
Batch
Norm 1D
Fig. 4:Batch
The Architecture
EncryptedConvolution
Traffic Classification
Model

and AdaGrad [33], is used to train the deep neural networks
in this paper. The total training time is 150 epochs in each
experiment. All the detailed configurations can be found in
“traffic classification.yaml” on our shared Github repository1 .
B. Baseline Models
Three baseline methods are included to verify the performance of CENTIME.
CNN1D, CNN1D method uses 1D convolution layers to
extract features from the traffic files directly and then use these
features to classify encrypted traffic.
CNN2D, CNN2D method is very similar to CNN1D, except
that 2D convolution layers are used for feature extraction. The

ReLU
network structure of CNN1D and CNN2D can be seen in [8].
At the same time, the above two baseline methods will include
two forms, with and without pooling layers.
ResNet, the third baseline method uses ResNet to extract
information from network traffic. The structure of ResNet here
is the same as the structure in “Information from Uniformized
Traffic” in CENTIME.
More detailed information on the above three baseline
models can be referred to the GitHub1 .

C. Evaluation Metric
In our experiment, four evaluation metrics are used to
evaluate the performance of our model, that is, accuracy

495

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:34:09 UTC from IEEE Xplore. Restrictions apply.

TABLE III: Result of CENTIME Compared with Baseline Method for Encrypted Traffic Classification

CNN1D-Pooling
CNN1D-noPooling
CNN2D-Pooling
CNN2D-noPooling
ResNet1D
ResNet2D
CENTIME

Acc
0.9398
0.9778
0.9313
0.9347
0.9913
0.9770
0.9979

784 Bytes
Pr
Re
0.9397
0.9398
0.9779
0.9778
0.9312
0.9313
0.9350
0.9347
0.9914
0.9913
0.9772
0.9770
0.9981
0.9979

F1
0.9397
0.9778
0.9312
0.9348
0.9913
0.9771
0.9980

1024 Bytes
Pr
Re
0.9522
0.9523
0.9766
0.9765
0.9364
0.9366
0.9612
0.9612
0.9910
0.9909
0.9741
0.9742
0.9973
0.9972

Acc
0.9523
0.9765
0.9366
0.9612
0.9909
0.9742
0.9972

(Acc), precision (Pr), recall (Re), and F1-score (F1 ). Accuracy
(Acc ∈ [0, 1]) means the proportion of correct predictions
among the total number of the dataset. We use accuracy
to evaluate the overall performance of the model. Precision
(Pr ∈ [0, 1]) means the percentage of the relevant results.
Recall (Re ∈ [0, 1]) means the percentage of total results
correctly classified by the model. F-measure (F1 ∈ [0, 1]) can
measure precision and recall at the same time. We calculate
the harmonic mean of precision and recall to get the F1 . F1
can be defined as (4),
F1 =

2 ∗ Recall ∗ Precision
Recall + Precision

(4)

D. Experiment Results and Analysis
To verify the effectiveness and performance of CENTIME,
we perform 21 experiments with different models and different
uniformized sizes for encrypted traffic classification task on
the “ISCX VPN-nonVPN” dataset. The experimental results,
including accuracy, precision, recall and average F-measure,
are shown in the following “Table. III”. These 21 experiments
are mainly used to illustrate the following three problems, (1)
the impact of the different uniformized sizes of the traffic files
on the final result. (2) the impact of the pooling layer on the
final performance. (3) comparing the effects of 1D convolution
layers and 2D convolution layers on the results.
Comparison of Different Uniformized Sizes: In section
III-C, all traffic files are uniformized into the same sizes. We
use different uniformized sizes of traffic to classify encrypted
traffic and compare the final results. As shown in “Table. III”,
only the performances on “CNN1D-Pooling” and “CNN2DPooling” improve when the traffic size increases from 784
bytes to 1024 bytes, while the performances of other models
have decreased. Similarly, when the traffic size increases
from 1024 bytes to 4096 bytes, the accuracy of most models
decreases too. This result is reasonable. As shown in “Fig. 2”,
most of the session sizes are around 784 bytes. If the raw traffic
is uniformized to 4096 bytes, a large amount of 0x00 needs
to be added at the end of the traffic file. Therefore, the data
will contain much invalid information, which can decrease the
performance of the models.
Comparison of With and Without Pooling Layer: As
shown in “Table. III”, from “CNN1D-Pooling” to “CNN1DnoPooling”, the accuracy of the model has increased significantly. For example, when the traffic size is 784 bytes,

F1
0.9521
0.9765
0.9365
0.9611
0.9909
0.9741
0.9973

Acc
0.9525
0.9697
0.9161
0.9301
0.9934
0.9717
0.9977

4096 Bytes
Pr
Re
0.9529
0.9525
0.9696
0.9697
0.9169
0.9161
0.9309
0.9301
0.9935
0.9934
0.9718
0.9717
0.9979
0.9977

F1
0.9526
0.9696
0.9162
0.9303
0.9934
0.9716
0.9979

the accuracy increases 4% when removing the pooling layer.
Similarly, in the case of 2D models (like “CNN2D-Pooling”
and “CNN2D-noPooling”), the performances of models are
also improved significantly when not using pooling layers. The
main reason is that when removing the pooling layer, the raw
traffic can retain more helpful information and help the model
make a judgment.
Comparison of 1D Convolution Layer and 2D Convolution Layer: It can be seen from “Table. III” that the accuracy
of the models with the 1D convolution layer is higher than
the models with the 2D convolution layer. For example, the
accuracy of “ResNet1D” is 2% higher than “ResNet2D” when
the session size is 784 bytes. It proves that the 1D convolution
layer is more suitable for encrypted traffic classification than
the 2D convolution layer. This conclusion is similar to Wang’s
work [8].
In summary, only increasing the traffic file size cannot
significantly improve the performance of the models. In this
paper, it is sufficient to uniformize the traffic size to 784
bytes. However, removing the pooling layer and using 1D
convolution layer can significantly improve the performance
of the model. Therefore, we use “ResNet1D” and remove the
pooling layer in CENTIME. Besides, CENTIME uses statistical features to add information about the overall structure
of the traffic. This makes accuracy and F1 of CENTIME
improved a little bit compared with “ResNet1D”.
TABLE IV: Result of the CENTIME Comparing with Stateof-the-art Models
Classifier

Accuracy

Precision

Recall

F1

FlowPic [24]
CNN1D [8]
Deep Packet-CNN [25]
Deep Packet-SAE [25]
CNN+LSTM [34]
SPCaps [22]
CENTIME

0.88
0.997

0.85
0.94
0.92
0.91
0.993
0.998

0.86
0.93
0.92
0.91
0.993
0.997

0.86
0.93
0.92
0.91
0.993
0.998

To further evaluate the performance of the CENTIME, we
compare our framework with other state-of-the-art models.
“Table. IV” shows the accuracy of CENTIME is as high as
99.7% on the “ISCX VPN-nonVPN” dataset. In summary,
compared with the other six methods, CENTIME achieves the
highest overall accuracy, precision, recall and F1 .

496

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:34:09 UTC from IEEE Xplore. Restrictions apply.

Fig. 5: Visualizations of 12 Types of Encrypted Traffic Data.
E. Visualization of Comprehensive Features
CENTIME can generate comprehensive traffic features
based on uniformized traffic files and statistical information.
In order to explore the property of the comprehensive features
extracted by CENTIME, we use t-SNE [35] to embed the
high dimension features into a lower dimension. As shown in
“Fig. 5”, the comprehensive traffic features are projected into
2D space. Different colours and different shapes in “Fig. 5”
represent different classes of traffic. It can be seen from
“Fig. 5” that the same classes of traffic cluster in similar
positions, while different classes are far away from each other.
For VPN and non-VPN data, VPN data mainly cluster on the
right side of the figure, such as “VPN P2P” and “VPN Chat”.
However, non-VPN data mainly cluster on the left side, such
as “FT” and “VoIP”. This shows that comprehensive traffic
features can represent the characteristics of different classes of
traffic well. Therefore, when CENTIME uses these features to
identify encrypted traffic, it can achieve superior performance.
V. C ONCLUSION AND F UTURE W ORK
Nowadays, encrypted traffic classification is receiving more
and more attention from both academic and industrial fields.
The current popular methods can be divided into two categories, (1) statistical characteristics-based methods and (2)
raw traffic-based methods. However, statistical characteristicsbased methods need to design different features for different
classification tasks, and using raw traffic-based methods will
cause loss of information. Therefore, a new framework called
CENTIME is proposed in this paper, which can generate
comprehensive traffic features from traffic files and use these
features to classify encrypted traffic.
In CENTIME, ResNet is used to extract information directly
from uniformized traffic. At the same time, 26 statistics are
extracted from traffic files and then encode by AutoEncoder.
Finally, the information extracted by ResNet and encoded
by AutoEncoder are merged to form comprehensive traffic
features. We use these comprehensive features to classify
encrypted traffic, and the results show that the CENTIME
yields significant improvements against the other six public
methods. Besides, by projecting the features to low dimension,
we found that the comprehensive traffic features can represent
various traffic types well.

There is still room for improvement in this work. Firstly,
the “ISCX VPN-nonVPN” dataset is imbalanced. For example,
the amount of traffic “VoIP” is far more than other classes of
traffic. Sampling or modifying the loss function can be used
to solve the imbalanced problem and improve the performance
of models. Secondly, 26 statistics need to be extracted in the
CENTIME; it will be more time-consuming than the methods
only using deep learning.
Notwithstanding these limitations, this study offers valuable insight into extracting comprehensive traffic features.
Additionally, the experiments in this paper have proved that
using the 1D convolution layer and removing the pooling
layer can achieve better performance on the encrypted traffic
classification task. In the future, more work needs to focus on
identifying encrypted traffic under the imbalance dataset and
making the framework work in real-time.
ACKNOWLEDGMENT
The authors would like to appreciate Jiaying Liao, Willy
Øverland, for their insightful comments and helpful suggestions.
Maonan Wang would also like to thank his parents, Ling
Wang, and Jianfang Jiang, and his girlfriend, Yuting Zhou for
their love and support.
R EFERENCES
[1] K. Park and W. Willinger, Sele-Similar network traffic and performance
evaluation. Wiley & Son, 2000.
[2] S. Garfinkel, G. Spafford, and A. Schwartz, Practical UNIX and Internet
security. ” O’Reilly Media, Inc.”, 2003.
[3] S. Valenti, D. Rossi, A. Dainotti, A. Pescapè, A. Finamore, and M. Mellia, “Reviewing traffic classification,” in Data Traffic Monitoring and
Analysis. Springer, 2013, pp. 123–147.
[4] P. Schneider, “Tcp/ip traffic classification based on port numbers,”
Division Of Applied Sciences, Cambridge, MA, vol. 2138, no. 5, 1996.
[5] S. Rezaei and X. Liu, “Deep learning for encrypted traffic classification:
An overview,” IEEE communications magazine, vol. 57, no. 5, pp. 76–
81, 2019.
[6] T. AbuHmed, A. Mohaisen, and D. Nyang, “A survey on deep
packet inspection for intrusion detection systems,” arXiv preprint
arXiv:0803.0037, 2008.
[7] R. Alshammari and A. N. Zincir-Heywood, “Can encrypted traffic be
identified without port numbers, ip addresses and payload inspection?”
Computer networks, vol. 55, no. 6, pp. 1326–1350, 2011.
[8] W. Wang, M. Zhu, J. Wang, X. Zeng, and Z. Yang, “End-to-end
encrypted traffic classification with one-dimensional convolution neural
networks,” in 2017 IEEE International Conference on Intelligence and
Security Informatics (ISI). IEEE, 2017, pp. 43–48.
[9] G. Draper-Gil, A. H. Lashkari, M. S. I. Mamun, and A. A. Ghorbani,
“Characterization of encrypted and vpn traffic using time-related,” in
Proceedings of the 2nd international conference on information systems
security and privacy (ICISSP), 2016, pp. 407–414.
[10] M. Song, J. Ran, and S. Li, “Encrypted traffic classification based
on text convolution neural networks,” in 2019 IEEE 7th International
Conference on Computer Science and Network Technology (ICCSNT).
IEEE, 2019, pp. 432–436.
[11] P. Wang, X. Song, Z. Deng, H. Xie, and C. Wang, “An improved
deep learning based intrusion detection method,” in 2019 IEEE 5th
International Conference on Computer and Communications (ICCC).
IEEE, 2019, pp. 2092–2096.
[12] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image
recognition,” in Proceedings of the IEEE conference on computer vision
and pattern recognition, 2016, pp. 770–778.
[13] G. E. Hinton and R. R. Salakhutdinov, “Reducing the dimensionality of
data with neural networks,” science, vol. 313, no. 5786, pp. 504–507,
2006.

497

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:34:09 UTC from IEEE Xplore. Restrictions apply.

[14] R. Bar-Yanai, M. Langberg, D. Peleg, and L. Roditty, “Realtime
classification for encrypted traffic,” in International Symposium on
Experimental Algorithms. Springer, 2010, pp. 373–385.
[15] J. R. Quinlan et al., “Bagging, boosting, and c4. 5,” in Aaai/iaai, Vol.
1, 1996, pp. 725–730.
[16] T. Hastie, S. Rosset, J. Zhu, and H. Zou, “Multi-class adaboost,”
Statistics and its Interface, vol. 2, no. 3, pp. 349–360, 2009.
[17] S. Agrawal and B. S. Sohi, “Feature optimization and performance
evaluation of machine learning algorithms for identification of p2p
traffic,” Journal of Advances in Information Technology, vol. 3, no. 2,
pp. 107–114, 2012.
[18] R. Alshammari and A. N. Zincir-Heywood, “How robust can a machine
learning approach be for classifying encrypted voip?” Journal of Network and Systems Management, vol. 23, no. 4, pp. 830–869, 2015.
[19] A. Vlăduţu, D. Comăneci, and C. Dobre, “Internet traffic classification
based on flows’ statistical properties with machine learning,” International Journal of Network Management, vol. 27, no. 3, p. e1929, 2017.
[20] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, “Smote:
synthetic minority over-sampling technique,” Journal of artificial intelligence research, vol. 16, pp. 321–357, 2002.
[21] L. Vu, D. Van Tra, and Q. U. Nguyen, “Learning from imbalanced
data for encrypted traffic identification problem,” in Proceedings of the
Seventh Symposium on Information and Communication Technology,
2016, pp. 147–152.
[22] S. Cui, B. Jiang, Z. Cai, Z. Lu, S. Liu, and J. Liu, “A session-packetsbased encrypted traffic classification using capsule neural networks,”
in 2019 IEEE 21st International Conference on High Performance
Computing and Communications; IEEE 17th International Conference
on Smart City; IEEE 5th International Conference on Data Science and
Systems (HPCC/SmartCity/DSS). IEEE, 2019, pp. 429–436.
[23] S. Sabour, N. Frosst, and G. E. Hinton, “Dynamic routing between
capsules,” arXiv preprint arXiv:1710.09829, 2017.
[24] T. Shapira and Y. Shavitt, “Flowpic: Encrypted internet traffic classification is as easy as image recognition,” in IEEE INFOCOM 2019IEEE Conference on Computer Communications Workshops (INFOCOM
WKSHPS). IEEE, 2019, pp. 680–687.
[25] M. Lotfollahi, M. J. Siavoshani, R. S. H. Zade, and M. Saberian, “Deep
packet: A novel approach for encrypted traffic classification using deep
learning,” Soft Computing, vol. 24, no. 3, pp. 1999–2012, 2020.
[26] M. Nasr, A. Bahramali, and A. Houmansadr, “Deepcorr: Strong flow
correlation attacks on tor using deep learning,” in Proceedings of the
2018 ACM SIGSAC Conference on Computer and Communications
Security, 2018, pp. 1962–1976.
[27] G. D. Bissias, M. Liberatore, D. Jensen, and B. N. Levine, “Privacy
vulnerabilities in encrypted http streams,” in International Workshop on
Privacy Enhancing Technologies. Springer, 2005, pp. 1–11.
[28] L. Bernaille and R. Teixeira, “Early recognition of encrypted applications,” in International Conference on Passive and Active Network
Measurement. Springer, 2007, pp. 165–175.
[29] W. Wang, M. Zhu, X. Zeng, X. Ye, and Y. Sheng, “Malware traffic
classification using convolutional neural network for representation
learning,” in 2017 International Conference on Information Networking
(ICOIN). IEEE, 2017, pp. 712–717.
[30] M. Wang, K. Zheng, D. Luo, Y. Yang, and X. Wang, “An encrypted
traffic classification framework based on convolutional neural networks
and stacked autoencoders,” in 2020 IEEE 6th International Conference
on Computer and Communications (ICCC). IEEE, 2020, pp. 634–641.
[31] A. Paszke, S. Gross, S. Chintala, G. Chanan, E. Yang, Z. DeVito, Z. Lin,
A. Desmaison, L. Antiga, and A. Lerer, “Automatic differentiation in
pytorch,” 2017.
[32] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
arXiv preprint arXiv:1412.6980, 2014.
[33] M. C. Mukkamala and M. Hein, “Variants of rmsprop and adagrad
with logarithmic regret bounds,” in International Conference on Machine
Learning. PMLR, 2017, pp. 2545–2553.
[34] Z. Zou, J. Ge, H. Zheng, Y. Wu, C. Han, and Z. Yao, “Encrypted
traffic classification with a convolutional long short-term memory neural network,” in 2018 IEEE 20th International Conference on High
Performance Computing and Communications; IEEE 16th International
Conference on Smart City; IEEE 4th International Conference on Data
Science and Systems (HPCC/SmartCity/DSS). IEEE, 2018, pp. 329–
334.
[35] L. v. d. Maaten and G. Hinton, “Visualizing data using t-sne,” Journal
of machine learning research, vol. 9, no. Nov, pp. 2579–2605, 2008.

498

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:34:09 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
