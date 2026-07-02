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
# [071] AEFETA: Encrypted traffic classification framework based on self-learning of feature
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
编号：071
题名：AEFETA: Encrypted traffic classification framework based on self-learning of feature
年份：2021
DOI：10.1109/icsp51882.2021.9408973
来源：2021 6th International Conference on Intelligent Computing and Signal Processing (ICSP)
PDF：paper/10.1109_icsp51882.2021.9408973.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\071.txt
- 原始字符数：22324
- 本次发送字符数：22324
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2021 6th International Conference on Intelligent Computing and Signal Processing (ICSP) | 978-1-6654-0413-6/20/$31.00 ©2021 IEEE | DOI: 10.1109/ICSP51882.2021.9408973

2021 IEEE 6th International Conference on Intelligent Computing and Signal Processing (ICSP 2021)

AEFETA: Encrypted traffic classification framework
based on self-learning of feature
*Jingru Yang
Information Engineering University
Zhengzhou, China
* Corresponding author: yangjingru9601@163.com

Yuanbo Guo
Information Engineering University
Zhengzhou, China

Abstract—This paper proposes an end-to-end framework
based on feature self-learning, AEFETA, to handle the task of
encrypted network traffic classification. In the AEFETA, we
propose a data preprocessing method based on the structure
information of the network traffic, and at the same time, a
lightweight deep learning model combined with an attention
mechanism also be proposed in this framework. We can convert
the raw pcap file into a file with the data type that can be input to
the deep neural network through data preprocessing, and then,
automatically extract the spatial-temporal features perform
classification tasks. AEFETA framework achieved a recall of 0.98
and precision of 0.97 in the encrypted traffic classification task,
meanwhile, we find the best data format through experimental
comparison.

random forests [3] are used to train and test feature
vectors. Statistics-based methods can effectively
identify unknown categories, but how to extract
effective features is an issue worthy of research. At
the same time, fixed features are easy to be attacked
is also an ongoing problem.
⚫

Keyword-deep learning; attention; end-to-end framework

I. Introduction
Due to the increasing awareness of user privacy protection
and the scalability and ease of operation of traffic encryption
technology, encrypted traffic accounts for an increasing
proportion in the real world. Whether to use a secure
encryption protocol has become an important indicator for
evaluating a website. Google uses HTTPS as a reference
factor for search engine ranking. According to Netmarketshare
data[1], as of October 2019, the proportion of global encrypted
traffic has exceeded 90%. How to accurately identify
encrypted traffic has become the hardest challenge of our time.
The current traffic classification technology can be divided
into the following three categories:
⚫

⚫

At present, deep learning technology has a wide range of
applications in the field of text recognition. It can abstract and
extract the features of samples layer by layer through the
multi-layer neural network structure and the adjustment of a
large number of parameters. Network traffic data has
hierarchical features similar to text (network traffic data:
sessions, packets, bytes; text data: paragraphs, sentences,
words). Therefore, To solve the problem of difficulty in
feature selection and fixed features easily targeted by attackers,
this article focuses on the common method of text
classification, deep learning, to research encrypted network
traffic classification task. The main contributions of this article
are as follows:

Fingerprint-based approach. Traffic classification
through port number and DPI(deep packet inspection)
is collectively referred to as a fingerprint-based
method. The port-based classifier is too old and is no
longer used. The DPI-based classifier is currently the
main method in the industry, which analyzes the
payload fields for traffic classification. However, it
cannot identify unknown categories. In the encrypted
traffic classification task, it can only obtain
information from unencrypted data such as the
protocol packet header, which is difficult to complete
the classification task.
Statistics-based approach. This method usually uses
flow statistics, packet statistics, or behavior statistics
to classify. After feature extraction, machine learning
algorithms such as support vector machines [2] and

978-1-6654-0413-6/21/$31.00 ©2021 IEEE

Deep-learning-based approach [4]. The method based
on deep learning is a research hotspot that has
appeared in the field of traffic classification in recent
years. [5] proposes to use CNN to learn the feature of
network traffic to achieve end-to-end traffic
classification. This way can avoid a lot of feature
engineering, but, because deep learning is a
data-driven method, the collection of a dataset in each
sub-field of traffic classification is difficult. data
imbalances in the existing dataset influence
classification results.

⚫

A new classification framework AEFETA is proposed.
Use deep learning technology to automatically learn
the temporal and spatial features of network traffic,
and identify encrypted network traffic from a global
perspective. The classification framework does not
rely on any prior knowledge about the protocol and
topology, nor does it require manual feature selection.

⚫

an attention-based spatiotemporal feature extraction
algorithm is proposed. Given the different degree of
importance distribution of each session and each
packet information, the algorithm uses the attention
mechanism [6] to weight the extracted features
according to the importance, thereby improving the
classification accuracy.

876

Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:28:08 UTC from IEEE Xplore. Restrictions apply.

⚫

A data processing method is proposed. We use
experimental comparison to find the data
representation with the best classification effect.

LSTM model (HABBiLSTM) based on a hierarchical
attention mechanism to introduce attention to the traffic
classification task for the first time, and achieved good
classification results.

Ⅱ. Related work
Encrypted traffic refers to the traffic generated by the
encryption algorithm transmitted during the communication
process. [13-15] conducted related research on encryption and
unencrypted, and proposed various methods for traffic
identification, which achieved good results. However, as the
demand for traffic analysis increases, only identifying whether
the traffic is encrypted cannot meet the requirements. The
current research on encrypted traffic classification is mainly
divided into two categories: anomaly identification and
application service identification. Among them, abnormal
identification is to identify malicious traffic such as DDoS and
Botnet. Application service identification is to identify the
type of service to which encrypted traffic belongs, such as
Browning, Streaming, Chat, etc.

Although the deep learning method based on feature
self-learning can realize effective end-to-end traffic
classification, data processing and model construction still
need more research.
Ⅲ. Methodology
In this work, we developed a framework, AEFETA, that
comprises two parts, data processing, and a deep learning
model.

A. anomaly identification
Although data encryption can effectively deal with
man-in-the-middle attacks to protect data, it can also pose new
security threats and risks. Cyren[7] found that 37% of
malware uses HTTPS, and every major ransomware family
has spread through HTTPS. Therefore, it is urgent to detect
encrypted malicious traffic. [8-10] proposed a variety of
methods to identify malware traffic using machine learning
methods. For the TLS protocol, Cisco [11-12] used logistic
regression and ten-fold cross-validation to identify encrypted
malicious traffic, with an accuracy of over 90%. Ivan et al. [16]
analyzed and summarized 40 data characteristics in 4
categories, and used LSTM and 5-fold cross-validation to
detect malware and phishing software signatures. Frantisek et
al. [17] compared the four machine learning methods of
XGBoost, Random Forest, Neural Network, and SVM for the
detection of TLS encrypted malicious traffic, and concluded
that the XGBoost and Random Forest methods are more
effective. Zeng et al. [22] proposed a DFR model, which slices
the original data according to 900 bytes and converts it into a
30×30 two-dimensional matrix, and then uses the three-layer
structure of CNN, LSTM, and SAE for traffic identification.
B. application service identification
Certain network management tasks require fine-grained
identification of service types for encrypted traffic. For
example, the use of social networking sites is not allowed in
certain exams, but applications such as web pages and videos
are not restricted. [18] compared three P2P traffic
identification methods, including identification methods based
on ports, application layer signatures, and flow statistics. [20]
proposed a method called Skype. Hunter's method recognizes
Skype traffic in real- time. This method can effectively
identify signaling services and data services (such as voice,
video, and file transmission) through a strategy based on a
combination of signature and stream statistical characteristics.
[21] Divide the conversation into 784-byte slices, convert
them into grayscale images, and enter CNN for classification.
Experiments show that the effect of using 1D-CNN is better
than 2D-CNN. [23] proposed a deep packet framework
combining 1D-CNN and SAE. [19] proposed a bidirectional

A. data processing
This paper uses the original pcap format file as input data
and completes the data preprocessing through the process of
Figure 1 to obtain a set of data, which directly input to the
model.

Fig.1. The process of data preprocessing

Step 1: Session generation. Session generation refers to
splitting a piece of the original file into multiple files, each of
which is a session. We use the segmentation tool in the
USTC-TK2016 toolset to complete this step.
Step 2: File removal. This step removes the empty files
and UDP files.
Step 3: Paket truncate. In this step we remove 16 bytes
packet header, 34 bytes link layer and network layer
information, and, the 4 bytes port number information in the
transport layer. We think this information is not important or
even disturbing. The120 bytes after these 54 bytes as useful
data.
Step 4: Paket trimming. This step saves the first 4 packets
with the application layer。
B. deep learning model
Our deep learning model for encrypted traffic
classification is composed of CNNs and BiLSTM with
attention mechanism. Since the location of the data packet
header information is fixed, we think it has certain spatial
characteristics; the process of key exchange in the early stage
of the data stream also maps the behavior pattern of a data
stream. Therefore, this article automatically extraction of
spatio-temporal characteristics of network traffic data to
classify traffic. Since each data packet in the data stream is of
different importance, we introduce the attention mechanism
into our deep learning model (Figure 2).
The algorithm1 is describe the architecture of deep

877
Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:28:08 UTC from IEEE Xplore. Restrictions apply.

learning model in the AEFETA. This process is mainly divided
into four layers: spatial feature learning layer, temporal feature
learning layer, attention layer, and output layer. It should be
noted that the model input is an n*m size matrix, and the
output is the predicted category.

been widely used in tasks such as text classification. In the
temporal feature learning layer of the model, we use BiLSTM
to complete the learning of temporal features. Specific steps
are as follows:

1) Spatial feature learning layer

The vector sequence [h1,h2,…,hn] of the data packet is
sequentially inputted into the BiLSTM to learn the temporal

Since different convolution kernels will learn different

features to obtain the vector

.

The data packet vector sequence is input in the reverse
order [hn,hn-1,…,h1] into the learning temporal feature of the
LSTM to obtain the vector
⚫

Splicing

and

.

get the output vector vi.

3) Attention layer
The attention mechanism is widely used in deep learning
tasks with Encoder-Decoder structure such as image
processing and speech recognition. Its core goal is to find out
more critical information for the current task from a large
amount of information. In the attention layer of the model, we
perform a weighted summation on the output vector vi of the
upper layer to obtain the feature vector c:
(1)

Fig.2.deep learning model

Among them, the calculation formula of αi is:
(2)
u is the random initialization vector for subsequent
training, and the formula for calculating ui is:
(3)
4) Output layer
In the field of deep learning, softmax is a commonly used
classification function, especially in multiclassification
scenarios. Softmax maps some inputs to functions between 0-1
and normalizes the final prediction vector to ensure that the
sum is 1. In the output layer of the model, we use softmax as
the classifier of the model. Since encrypted traffic recognition
is a multi-classification problem with the imbalance of
categories, we choose cross-entropy as the loss function of the
model.

spatial features, applications in the field of computer vision
have shown that CNN using different convolution kernels
connected will get better spatial features. In the spatial feature
learning layer of the model, we use two CNN with different
convolution kernel sizes to complete spatial feature learning.
The specific steps are as follows:
Convert each data packet into one-hot encoding form, and
convert the one-dimensional array into a matrix pi of m*256
sizes.
⚫

Input pi into two convolutional neural networks with
different convolution filters to learn the spatial
characteristics of the data packet. The output vectors
of the two neural networks are hi1 and hi2
respectively.

⚫

splicing hi1 and hi2 to obtain the packet vector hi.

Ⅳ. Experiments and Discussion
The hardware and software configuration of the
experiment is as follows. The software framework is Keras
and TensorFlow, running on the Ubuntu operating system. In
terms of experimental hardware, a 64-core 256G cpu is used.
Besides, an Nvidia GeForce RTX 2080Ti gpu is used as a
training accelerator. Table1 describes the architectures of the
deep learning model.

2) Temporal feature learning layer
BiLSTM can learn contextual information better and has
878
Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:28:08 UTC from IEEE Xplore. Restrictions apply.

Our proposed framework performs well than other
encrypted traffic classification methods in the same dataset.
Table3 shows the comparision results of the[21], [23], and
ours. Figure 3 shows the precision, recall, F1-Score value of
each class of traffic, all three indicators of the streaming label
reach 1.

TABLE1. NEURAL NETWORK ARCHITECTURAL PARAMETERS
Layer

Type

Filters/Neurons/Rate

1

Conv+tanh

128

2

dropout

0.2

3

GlobalMaxPool

/

4

dense

128

5

Conv+tanh

256

6

dropout

0.2

7
8

GlobalMaxPool
dense

9
10

TABLE3. COMPARISON OF DIFFERENT METHODS
Methodology

Ac

Pr

Re

F1

/
128

[21]

0.817

0.855

0.858

0.856

[23]

/

0.97

0.97

0.97

concatenate

/

ours

0.984

0.979

0.980

0.979

dense

64
64

11

Bilstm

12

attention

/

13

dense

6

14

softmax

/

A. Dataset
This article uses the public data set VPN-nonVPN data set
(ISCXVPN2016) [6] to carry out the encrypted traffic
classification experiment proposed in this article. The data set
includes 14 kinds of encrypted traffic (7 kinds of protocol
encapsulated traffic and 7 kinds of conventional encrypted
traffic). This experiment only discusses conventional
encrypted traffic data. Because of the confusion in the
classification of some of the files, for example,
facebook_video and other files can be classified as browser or
streaming, so we ignore these files and divide 61 files into 6
categories, namely: chat, email, file_transfer, p2p, streaming,
voip(Table2 ).

Fig.3. Recall, precision, F1 value of 6-class classifiers

C. discussion
In this section, we discuss the impact of the number of
packets in a session and the length of the packets on the
classification results. Because the larger input format will
greatly reduce the speed of the algorithm, we set the number
of packets in the range of 4-6, and the packet length in the
range of 40-140 for experimentation. We compared the recall
value and accuracy value under different packet lengths and
packet numbers. Through the display of Figure 4 and Figure 5,
we choose 4 and 120 as the number of packets per session and
length of per packet.

TABLE2. ISCXVPN2016
label

File

chat

AIMchat1, aim_chat, facebookchat, hangouts_chat,
ICQchat, icq_chat, skype_chat

email
file_transfer
p2p
streaming
voip

email
skype_file
Torrent01
netflix, spotify, vimeo, youtube
hangouts_audio, voipbuster

B. Evaluation results
In this section, we discuss the results of the AEFETA
framework. Generally speaking, detection accuracy, accuracy
rate, recall rate, and F1 value are the four key indicators for
evaluating encrypted traffic recognition. This article uses the
following criteria to evaluate the classification algorithm:
precision, recall, F1-Score.

Fig.4. The recall value under different packet lengths and packet
numbers

879
Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:28:08 UTC from IEEE Xplore. Restrictions apply.

[11] Anderson, B., Paul, S., Mcgrew, D. (2018) Deciphering malware’s use
of TLS (without decryption). Comput. Virol. Hacking Techn, 14 (3):
195-211.
[12] Blake, A., David, M. (2016) Identifying encrypted malware traffic with
contextual flow data. In: ACM Workshop on Artificial Intelligence and
Security (AISec). 2016: 35-46.
[13] Okad, Y., Ata, S., Nakamura, N., et al. (2011) Comparisons of machine
learning algorithms for application identification of encrypted traffic. In:
10th IEEE International Conference on Machine Learning and
Applications and Workshops. 2011: 358-361.
[14] Zhao, B., Guo, H., Liu, Q. R., et al. (2013) Protocol independent
identification of encrypted traffic based on weighted cumulative sum test.
Journal of Software, 24(6): 1334-1345.
[15] Niu, W.N., Zhuo, Z. L., Zhang, X.S., et al. (2019) A heuristic statistical
testing based approach for encrypted network traffic identification[J].
IEEE Trans. Veh. Technol., 68 (4).
[16] Ivan, T., Luis, D. C., Alejandro, C. B. (2018) Hunting malicious TLS
certificates with deep neural networks. In: The 11th ACM Workshop on
Artificial Intelligence and Security. 2018:64-73.
[17] Frantisek, S., Sebastian, G. (2017) Machine learning for network
HTTPSanalysis. In: BRUCON Conference. 2017:5.
[18] Madhukar, A., Williamson, C. (2006)A longitudinal study of P2P traffic
classification. In: Modeling，Analysis, and Simulation of Computer and
Telecommunication Systems, MASCOTS 2006 179-188.
[19] Chong, L. Traffic classification system based on deep
learning(2019)Adami, D., Callegari, C., Giordano, S., et a1. (2012)
Skype-hunter: a realtime system for the detection and classification of
Skype traffic. International Journal of Communication Systems, 25(3):
386-403.
[20] Adami, D., Callegari, C., Giordano, S.et a1. (2012) Skype—hunter: a
real-time system for the detection and classification of Skype traffic.
International Journal of Communication Systems, 25(3):386-403.
[21] Wang, W., Zhu, M., Wang, J., et al. (2017) End-to-end encrypted traffic
classification with one-dimensional convolution neural networks. In:
IEEE Int Conf Intell Security Informat. 2017:43-48.
[22] Zeng, Y., Gu, H., Wei, W., et al. (2019) Deep-full-range: a deep learning
based network encrypted traffic classification and intrusion detection
framework. IEEE Access, 2019: 1.
[23] Lotfollahi, M., Zade, R.S.H., Siavoshani, M,J., et al.(2017) Deep packet:
a novel approach for encrypted traffic classification using deep learning.
eprint arXiv: 1709.02656.

Fig.5. The accuracy value under different packet lengths and packet
numbers

Ⅴ.

Conclusion

In this paper, we presented a framework, AEFETA, that
automatically extracts features from encrypted traffic for
traffic classification tasks. This paper uses the hierarchical
characteristics of network traffic, draws on the application of
attention mechanism in text classification, and uses deep
learning to directly process the original pcap file to achieve
end-to-end traffic classification. Our experiment was carried
out on vpn-nonvpn and achieved good results. At the same
time, we discussed data processing, which has a particularly
great impact on classification results. What this article is
currently doing is classifying ordinary encrypted traffic. In the
field of malware detection, how to perform malware detection
on encrypted traffic while protecting user privacy (that is,
without decrypting data packets) is a difficult point, it is also a
problem that needs to be research in the next step.
References
[1]
[2]

Netmarketshare. (2019).
Kondo, S., Sato, N. (2007) Botnet traffic detection techniques by C&C
session classification using SVM. In: International Workshop on
Security. 91-104.
[3] LencunE, Y., Bengio, Y., HintonI, G. (2015) Deep learning. Nature,
512:436-444.
[4] Bilge, L., Balzarotti, D., Robertson, W., et al. (2012) Disclosure:
detecting botnet command and control servers through large-scale
net-flow analysis. In: The 28th Annual Computer Security Applications
Conference. 129-138.
[5] Wang, W., Zhu, M., Zeng, X., et al. (2017) Malware traffic classification
using convolutional neural network for representation learning. In: 2017
International Conference on Information Networking (ICOIN). 712-717.
[6] Vaswani, A., Shazeer, N., Parmar, N., et al. (2017) Attention Is All You
Need, arXiv.
[7] Cyren. Malware is moving heavily to HTTPS. https:// www. cyre- n.com
[8] He, G., Xu, B., Zhu, H. (2018) AppFA: a novel approach to detect
malicious Android applications on the network. Security and
Communication Networks, 2018 :1-15.
[9] Shabtai, A., Tenenboim, C.L., Mimran, D., et al. (2014) Mobile malware
detection through analysis of deviations in application network behavior.
Computers & Security, 43:1-18.
[10] Garg, S., Peddoju, S.K., SarjeA, A.K. (2017) Network-based detection
of Android malicious Apps. International Journal of Information
Security,16(4):385-400.

880
Authorized licensed use limited to: Tsinghua University. Downloaded on August 19,2025 at 01:28:08 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
