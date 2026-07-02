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
# [066] Practical evaluation of encrypted traffic classification based on a combined method of entropy estimation and neural networks
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
编号：066
题名：Practical evaluation of encrypted traffic classification based on a combined method of entropy estimation and neural networks
年份：2019
DOI：10.4218/etrij.2019-0190
来源：ETRI Journal
PDF：paper/10.4218_etrij.2019-0190.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\066.txt
- 原始字符数：47641
- 本次发送字符数：47641
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Received: 19 April 2019

|

Revised: 6 September 2019

DOI: 10.4218/etrij.2019-0190

|

Accepted: 1 October 2019

F E AT U R E D A RT I C L E

Practical evaluation of encrypted traffic classification based on a
combined method of entropy estimation and neural networks
Kun Zhou1,2

| Wenyong Wang1 | Chenhuang Wu1,3

1

School of Computer Science and
Engineering, University of Electronic
Science and Technology of China, Sichuan,
China
2

Institute of Computer Applications, China
Academy of Engineering Physics (CAEP),
Sichuan, China
3

Putian University, Fujian, China

Correspondence
Wenyong Wang and Kun Zhou, School
of Computer Science and Engineering,
University of Electronic Science and
Technology of China, Sichuan, China.
Email: wangwy@uestc.edu.cn (W. W.) and
zhoukun@std.uestc.edu.cn (K. Z.)
Funding information
This work was partially supported by
National Science Foundation of China with
the Grant Number: 2018YFB08040505

1

|

| Teng Hu1,2

Encrypted traffic classification plays a vital role in cybersecurity as network traffic
encryption becomes prevalent. First, we briefly introduce three traffic encryption
mechanisms: IPsec, SSL/TLS, and SRTP. After evaluating the performances of support vector machine, random forest, naïve Bayes, and logistic regression for traffic
classification, we propose the combined approach of entropy estimation and artificial
neural networks. First, network traffic is classified as encrypted or plaintext with
entropy estimation. Encrypted traffic is then further classified using neural networks.
We propose using traffic packet’s sizes, packet's inter-arrival time, and direction as
the neural network's input. Our combined approach was evaluated with the dataset
obtained from the Canadian Institute for Cybersecurity. Results show an improved
precision (from 1 to 7 percentage points), and some application classification metrics
improved nearly by 30 percentage points.
KEYWORDS
deep neural networks, encrypted traffic classification, entropy estimation, PCA

IN T RO D U C T ION

Research on traffic classification has become more challenging than ever, as the innovative applications and mechanisms to conceal the nature of traffic develop and mature
rapidly. The accuracy and efficiency of traffic classification
methods have attracted great research interest from academia
and industry. For example, encrypted Voice over IP network
(VoIP) traffic flow needs to be correctly picked out and labeled with appropriate transmission priorities—because of
its time-delay sensitive nature—to preserve the quality of service (QoS). Old-fashioned strategies such as packet's header
and payload inspection failed to discriminate traffic, because
content checking on encrypted traffic was unsuccessful.

Some inspiring methods based on the statistical behavior of
traffic flow have been proposed. Although these methods
achieved high accuracies in differentiating non-encrypted
traffic flows, encrypted traffic classification is still in its initial development.
IP packets transmitted in plaintext can be easily recovered
by network sniffer tools such as Wireshark. Thus, to ensure
communication confidentiality, encryption methods must be
employed, and that is becoming a fast-growing trend.
IPsec virtual private network (VPN), transport layer security (TLS)/secure socket layer (SSL), and secure real-time
transport protocol (SRTP) dedicated to encrypted VoIP are
three major protocols for encrypted network traffic. We selected the IPsec protocol to brief the principles and approaches

This is an Open Access article distributed under the term of Korea Open Government License (KOGL) Type 4: Source Indication + Commercial Use Prohibition + Change
Prohibition (http://www.kogl.or.kr/info/licenseTypeEn.do).
1225-6463/$ © 2019 ETRI
ETRI Journal. 2020;42(3):311–323. ﻿ 

wileyonlinelibrary.com/journal/etrij

| 311

|   

for traffic encryption. IPsec can be deployed to enable VoIP
communication confidentiality at the IP network level. Some
research concluded that a cryptographic engine could bring
large overhead for voice traffic and was not perfect for VoIP
encryption. This hot topic is worthy of investigation not only
for its omnipresence in real-life VoIP scenarios but also for
its academic value. Widely used in HTTPS Web traffic, TLS/
SSL is undoubtedly one of the most important encryption
mechanisms for packet transmission, as the NSS lab predicts
that 75% of global web traffic will be encrypted by 2019.
We investigated and evaluated numerous flow features for
encrypted traffic classification using four traditional machine
learning methods—support vector machines (SVM), random forest (RF), naïve Bayes, and logistic regression—and
a neural network (NN). An entropy-based method was used
to first distinguish encrypted from non-encrypted traffic. For
encrypted traffic, based on the results from the first phase, we
designed a NN using three types of packet discriminators—
packet length, inter-arrival time (IAT), and direction (forward
and backward)—as input-layer parameters. For non-encrypted traffic, we employed principal component analysis
(PCA) to cut dimensions by half to achieve high efficiency of
classification while maintaining a certain degree of accuracy.
Contributions we made in this study are as follows:
• We investigated three network traffic encryption mechanisms to prepare for classification analysis and evaluation.
• Four traditional machine learning methods and a neural
network were evaluated for network traffic classification.
• We proposed a combined approach to distinguish the encrypted traffic from the plaintext traffic using information
entropy and a neural network, and we achieved improved
results.
The remainder of the article is structured as follows.
Section 2 describes related research. In Section 3, we cover
our methodology with an emphasis on machine learning
techniques, features, and datasets. Section 4 presents evaluation methods and results. Section 5 concludes the article and
discusses future work.

2

|

R ELATE D WO R K

Some research demonstrated the feasibility of inferring the
encrypted packets without decryption from the information
leakage or the so-called “side-channel.” Attacks by traffic
analysis usually materialize at the application or transport/
network level for traditional methods. General traffic analysis is based on application/traffic flow-level features, such
as correlation statistics between flows at the transceiver
ends, which is especially the case for encrypted traffic,
because the packet content inspection methods fail before

ZHOU et al.

encryption. VoIP service provider, Skype, protects users’
privacy by applying mechanisms such as stronger encryption, proprietary protocols, unknown codecs, dynamic path
selection, and the constant packet rate. However, researchers have demonstrated how to compromise users’ privacy
according to a novel traffic analysis attack that extracted
application-level features from VoIP call traces. In an interesting study, Wright and others [1] suggested that VoIP
packets compressed with variable bit rate (VBR) encoding schemes and encrypted with a fixed-length cipher were
susceptible to the attacks of using only the packet length
feature to infer the spoken language of the encrypted conversation. Wright and others [2] showed possibilities of
spotting the phrases within encrypted VoIP calls under
specific circumstances. The article proposed profile hidden
Markov models (pHMM) to model the packet sequences
for the given phrases. Results indicated an average accuracy of 50% (greater than 90% for some phrases).
Traffic features are critical to the identification and classification of encrypted VoIP traffic for NNs. Anderson and
others [3] introduced a complex set of observable data features and showed that these features could be exercised to
detect malware communication while preserving the privacy
of benign users. Wright and others [4] investigated the extent
to which average application protocols could be differentiated with features such as packet size, timing, and direction
that remained unchanged after encryption. The accuracy of
their traffic classifier was greater than 80% for most protocols. Sherry and others [5] inspected the packet directly in
the encrypted traffic. This article elaborated on the approach
through an original protocol and encryption scheme.
Sun and others [6] focused on the inference of sensitive
information from encrypted network connections with packet
sizes and timing. Liberatore and Levine [7] reported their
findings of identifying web pages encapsulated in encrypted
HTTPs using only the number and size of the encrypted packets. Similarly, Schuster and others [8] proposed a method to
spot videos played over an encrypted network channel using
the total size of the packets transmitted in a short-time window.
Packet inter-arrival times have been studied to infer keystrokes
within SSH sessions [9]. Entropy estimation for real-time
encrypted traffic identification [10] presented the approach.
Results indicated that the encrypted VoIP traffic was detected
correctly with a precision greater than 94%. Moore and others [11] made an impressive contribution by proposing more
than 200 flow features for further analysis. Velan and others
[12] compared the feature-based classification methods and
pointed out their weaknesses and strengths. Daniel and others
[13] evaluated three machine learning techniques—k-means
clustering algorithm, MOGA, and C4.5—and concluded that
C4.5 was the fastest. Nguyen and others [14] surveyed 18 significant works published from 2004 to 2007 and categorized
them according to machine learning algorithms and primary

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

312

contributions. An inspiring result by Zhang and others [15] was
that traffic classification performance could still be enhanced
drastically even with very few training samples. Finamore and
others [16] proposed KISS, an Internet classification engine,
which achieved very good results with the average true positive rate of 99.6% and 98.1% for the worst case.
Traffic encryption has also gained research interest from
the industry. IEEE industry connections established the
security subgroup on encrypted traffic inspection (ETI),
which aims to standardize an accepted way of traffic inspection, on top of encrypted transport standards. The group
also covers requirements for traffic inspection mechanisms
based on different use cases and explores proofs of concepts
of implementations. Network giant Cisco's latest networking gear, encrypted traffic analytics (ETA) [17] unleashed in
2017, provides advanced traffic analytics including machine
learning to identify encrypted network threats.

3
3.1

|

M ET H OD O LO GY

|

Entropy-based methods

Shannon's entropy theory measures information uncertainty.
Given m possible events A1, …, Am with probabilities of occurrence p1, …, pm, entropy H is defined by (1).

H =−

∑m
i=1

( )
pi log pi .

(1)

Equal probabilities have the maximum value of entropy.
Unpredictable behavior means uncertainties and, thus, increases entropy. An appropriate estimator for the entropy is
needed for small datasets, but entropy estimation based on
a small sample becomes harder [18], especially for N < m.
Motivated by the problems of estimating the entropy with
small length N, Olivain and Goubault-Larrecq [19] presented
the N-truncated entropy method. The N-truncated entropy
HN(p) is defined as for words w of length N using a maximum
likelihood estimator (MLE) to estimate the entropy. Average
MLE estimates the number of words to formulate HN(p). If
pi = 1/m for all i (where p follows the uniform distribution U),
then HN(U) can be computed by (2).

| 313

works for the empirical evaluation
test. Paninski [20] con√
cluded that at least N > m samples were needed for the
uniformity test. Inspired by the aforementioned methods, we
propose the following information entropy-based algorithm.
Using the traffic sniffer tool's data processing functionality, we selected randomly 64 bytes in TCP protocol contents
(TLSv1.2 for encrypted traffic) from the experimental pcap
files (ISCX-VPN-NonVPN-2016) to compute the entropy.
We used Monte Carlo pseudorandom sequence to mimic the
encrypted traffic and compared it with the experiment data.
See Algorithm 1 in Table 1 for entropy estimation details.

3.2

|

Artificial neural networks

The research demonstrated the efficacy of artificial neural
networks, especially the deep learning technologies [21], in
traffic classification. Computational power, such as graphical processing units (GPUs) and Google's tensor processing
unit (TPU), grows exponentially, and a deep NNs design and
training have become more feasible. There are reports that
NN architectures such as multilayer perceptrons (MLP), convolutional neural networks (CNN), recurrent neural networks
(RNN), autoencoders, and generative adversarial networks
(GAN) have all been used for traffic classification. In this
article, we used a traditional NN with three layers (input, hidden, and output layer) to evaluate our combined approach.

h(1) = 𝜎(W (1) x),
h(2) = ReLu(W (2) x),
h(3) = 𝜎(W (3) h(1) ),
y = 𝜎(W (3) h(1) + W (5) h(2) ⋅
TABLE 1

Algorithm using entropy-based methods

Algorithm 1 Distinguish encrypted traffic from plaintext traffic
using entropy-based methods
1. Generate Monte Carlo pseudorandom sequence between 0 and
256 with the length of 64 bytes for 10 000 times; for example, (a3
b4 f1 23 48 90 ab 34…), where “a3” stands for one character.
2. Using (2) to calculate HN (U), where N = 64, m = 256, and Ni
stands for the frequency of character i, and HN (U) represents the
average information entropy using the MLE method.

[(
) (m
)]
∑
∑ ni
ni
N
1
×
− log
HN (U) =
mN n +⋯+n =N
N
N
n1 + ⋯ + n m
i=1
1
m
(
)
N
N!
where
=
.
n1 ! ⋯ n m !
n1 + ⋯ + n m

3. Collect and save the experimental pcap dataset using the sniffer
tool's functionality.

We used MLE as an unbiased estimator of HN. The estimated value of similarity to HN(U) reflects how much it resembled the uniform distribution. A Monte Carlo method for
estimating HN(U) with corresponding confidence intervals

6. Calculate average variance, 𝜎 = ki=1 (Hi (p) − Hu (p) )2 ∕ (k − 1),
determine encryption = true if actual information entropy
value falls within three times confidence range, otherwise
encryption = false.

(2)

(3)

4. Select randomly 64 bytes protocol contents in 100 TCP flow data
and store them into 100*64 dataset matrix (test dataset matrix);
5. For every row of the test dataset matrix, calculate information
entropy for every character using (1), that is Hk(P).
∑

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

  

ZHOU et al.

|   

ZHOU et al.

The NN architecture is shown in Figure 1.
The NN uses modular backpropagation algorithms, linear
module plus softmax (activation function), and cross-entropy
(loss function). The basic principle for each module was to
(i) calculate “forward_pass,” “backward_pass,” and “para_
gradients,” (ii) chain together “forward_pass” and “backward_pass,” (iii) compute “para_gradients,” and (iv) apply
gradients and iterate. For the NN, online stochastic gradient
descent (SGD) was used to construct our model. See Table 2
for the main modular processes.
We proposed a combined approach to distinguish the encrypted and plaintext traffic and then to further classify the
encrypted traffic into eight types of applications. The NN is comprised of three layers: the input layer has 23 neurons for 23 traffic
features, the hidden layer has 100 neurons, and the output layer
has eight neurons for eight classes (which are VoIP, audio streaming, browsing, chat, email, file transfer, P2P, and video streaming). Figure 2 depicts the high-level workflow of our approach.

3.3

|

Dataset

The dataset from the Canada Institute for Cybersecurity is
widely used by researchers worldwide. It includes network
h(1)

3.4 | Methods for encrypted and nonencrypted traffic classification

Output: Y

h(3)

W(3)

W(4)

Input: X

W(1)

W(5)
h(2)
(2)

W

(A)
W(1)

X

Linear

W(3)

Sigmoid

Linear

W(4)

Linear

ReLu

W(2)

Sigmoid

Linear

SUM

traffic such as IDS, Tor/Non-Tor, VPN/Non-VPN, and an
Android malware dataset. For this study, we selected two
relevant traffic datasets, “ISCX-Tor/Non-Tor” and “ISCX
VPN/Non-VPN.” These two datasets store captured traffic
packets in the pcap format files, which we can open with
Wireshark to inspect the packet details. The CSV files are
traffic flow statistics typically used for supervised learning
with assigned training labels. For “ISCX VPN-NonVPN”
datasets, packets are captured over virtual private network
(VPN) sessions, which are generally considered to be encrypted. The “ISCX-Tor/Non-Tor” dataset is generated by
the Tor browser. The basic principle for Tor is to build encrypted connections in a way that no individuals ever know
the complete path. Complex port obfuscation algorithms also
improve the privacy and anonymity of Tor traffic. As the
complete datasets were very huge and diversified, we chose
the aforementioned two datasets for our experiments. VPNNonVPN datasets were used to classify the encrypted and
non-encrypted traffic, while Tor/Non-Tor was for application classification. We separated the training and test sets (no
validation set) using random sampling. About 2000 packets
randomly selected from the original dataset were used to feed
to the NN. The repeat times for the train/test were set to 10.
The training set size was 90% and 10% was for the test set.

Sigmoid

Y

Linear

W(5)

(B)

F I G U R E 1 (A) Traditional neural network representation and
(B) neural network computational graph

We investigated correlations between the 23 different statistic features and the target class. The following figures
show the density distribution of the features “duration”
and “total_fiat” with class type (VPN/Non-VPN), respectively. There were two spikes for “duration” of Non-VPN
and one spike for “total_fiat” of Non-VPN. The differences
between the two types of distributions were obvious, which
indicated these two features could be used for classification. Figure 3 demonstrates the distribution of the two selected features.
We selected VPN/Non-VPN dataset and studied the distribution of every feature and class type. The heat map for
the dataset and box plot for the two chosen statistic features
(duration, total_fiat) are illustrated in Figure 4.
Heat map represents data in the matrix with changing colors.
Darker colors mean the larger data. Some features showed they
might be useful for classification. Box plot depicts the numeric
data value of “duration” and “total_fiat” through quartiles.
We ranked the top 10 among 23 features using three metrics: information gain (IG), Gini decrease, and χ2. IG for a
specified attribute is defined using Shannon entropy H(T).
IG(T, a) = H(T) –H(T | a) is the difference between the a
priori Shannon entropy H(T) of the training set and the conditional entropy H(T | a). The mean decrease in Gini coefficient

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

314

TABLE 2

and processes

Neural network modular

Modular

| 315

Processes
forward_pass: Y = Wx + b;
= 𝜕LW
backward_pass: 𝜕L
𝜕x ( 𝜕y )
T T 𝜕L 𝜕L
𝜕L
para_gradients: 𝜕w= 𝜕L
x ; 𝜕b= 𝜕y
𝜕y

forward_pass: Y = ReLu(x);
𝜕L
= (yi > 0)
backward_pass: 𝜕x
i

Y = Softmax(x); yn=∑e exm
xn

m

forward_pass: Y = L
= Cross_entropy(p, x); Y
∑
= − pi logxi
i

𝜕L pi
backward_pass: 𝜕x
=𝜕x
i

i

Parameters

C = 1.0, ε = 0.1
Kernel: Sigmoid, tanh(auto x*y + 0.0)
Numerical tolerance: 0.0003
Iteration limt: 2000

S
V
M

Parameters

Dataset1
Encrypted
traffic

Random
Forest

Dataset2
Non-encrypted
traffic

Entropy
Methods

Number of trees: 10
Maximal number of features: unlimited
Maximal tree depth: unlimited
Sop splitting nodes with maximum instances: 5

Parameters

Neural
Network

Hidden layers: 100
Activation : ReLu
Solver: Adam
Alpha: 0.002
Max iterations: 10 000
Replicable training: True

Performance
Comparison
Reports

Naive Bayes

Logistical
regression

FIGURE 2

Parameters
Regularization: Lasso (L1), C = 50

Combined
Approach

Workflow of the combined approach

measures each variable's contributions to the homogeneity of
the nodes from scale 0 (homogeneous) to 1 (heterogeneous).
Chi-squared test calculates the difference between the distribution of plaintext and decrypted ciphertext. A lower value of
the test means a higher probability of successful decryption.
Figure 5 illustrates the results of the top 10 rankings.

3.5

|

Methods for application classification

Dataset ISCX-Tor-Non-tor2017 was used for the classification
of different types of applications. We use eight applications and
23 features (see Table A1 in Appendix for definitions). The distribution of application type with frequency and probabilities is

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

  

ZHOU et al.

ZHOU et al.

22

Non-VPN

20

VPN

18
Density (x1e – 09)

16
14
12
10
8
6
4
2
0
–60

–40

–20

0

20

40
60
80
100
Duration (x1e + 06)

120

140

160

180

(A)
200

Non-VPN

180

VPN

Density (x1e – 09)

160
140
120
100
80
60
40
20
0
0

20

40
60
80
Total_fiat (x1e + 06)

100

120

(B)

FIGURE 5

Input data features ranking by relevance: top 10

We first employed principal component analysis (PCA)
to preprocess this type of dataset. This method efficiently reduces the dimensions while retaining the variance of the data
and, thus, reduces the sizes of input layer. The dataset contains 23 features. After PCA processing, 10 principal components were computed at the variance greater than 98%. We
selected the top 10 principal components to preserve the data
variance at 0.984 (Figure 7).
After analyzing 23 features using PCA, we found that half
of the features could be dropped to improve efficiency while
preserving accuracy at a variance of 98.4%. Figure 8 demonstrates the top 10 principal components.

F I G U R E 3 (A) Distribution for feature “duration” and Class and
(B) distribution for feature “total_fiat” and Class

4

shown as a bar chart and freeviz in Figure 6. Freeviz shows that
points in the same class are attracted to each other, whereas
points in different classes repel each other.

Numerous machine learning approaches have been proposed
for traffic classification. Gil and others [22] adopted features
such as the flow's duration, bps, and inter-arrival time for both

|

RESULTS AND DISCUSSIO N

Non-VPN: 46818642.11 ± 54947389.61

1207.00

119245457.00

2382589.00
VPN: 57964317.31 ± 54677146.24

59867085.00

273.00

0000000

0

20000000

40000000

60000000

118650591.00

80000000

100000000

120000000

140000000

80000000

100000000

120000000

140000000

(A)
Non-VPN: 2065364.213063 ± 8716373.265607

165.324800 18341.850000

146863.200000

VPN: 3199439.452356 ± 9271798.636702

103.500000 348513.650000

20000000

0

1261536.500000

20000000

40000000

60000000

(B)

(C)

F I G U R E 4 (A) Feature “duration” at student’ t: 3.453 (p = 0.001), (B) feature “max_fiat” at student’ t: 2.095 (p = 0.037), and (C) heat map
for 23 data features

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

|   

316

FIGURE 8

(A)
1.0

160
140

0.8
120
0.6

80
0.4

60

Frequency

Frequency

100

40
0.2
20
0

0
No
Selected

(B)

F I G U R E 6 (A) Freeviz for different application distribution and
(B) application distribution with frequency (left) and probabilities
(right)

directions to characterize the network traffic. They experimented using k-nearest neighbor (kNN) and C4.5 decision tree
algorithms and achieved approximately 92% and 88% recall,
respectively, for the VPN-tunneled dataset. Yamansavascilar

0.984

1.0

Proportion of variance

0.8

0.6

0.4

0

0.014

1

3

5

7

9

11

13

15

17

Principal Components

FIGURE 7

PCA analysis of 23 data features

19

21

23

Top 10 features using the PCA method

and others [23] selected 111 discriminators for 14 classes of
applications and achieved an accuracy of 94% with k-NN algorithm. However, in their report, they did not mention the
specific details of their implementation, and the results need
to be revalidated by independent third parties to increase their
credibility.
SVM [24] is used for data classification and regression.
RF [25] mainly constructs decision trees to achieve the same
functions as SVM does. Naïve Bayes model [26] is derived
from applying Bayes’ theorem with strong independence assumptions between the features. Logistic regression models
the probability of output in terms of input and can be used
for classification. Aceto and others [27,28] proposed many
novel approaches to classify mobile applications. In the
study by G. Aceto et al and others [29], their results showed
that three anonymity networks (Tor, I2P, and JonDonym)
can be easily distinguished with an accuracy of 99.99%.
Taylor [30] studied smartphone apps from the encrypted
traffic and achieved more than 99% accuracy. Rezaei and
others [31] presented commonly used deep learning methods and their applications in traffic classification tasks.
Lotfollahi and others [32] proposed a “deep packet” scheme
to identify encrypted traffic and distinguish between VPN
and non-VPN network traffic. Aceto and others [33] presented an inspiring contribution to encrypted TC: they used
several state-of-the-art deep learning techniques to set a
framework for comparisons and a performance evaluation
workbench. They concluded that although DL had open issues and pitfalls, it was viable for the traffic classification.
Our method of entropy estimation for encrypted or non-encrypted traffic achieved an average accuracy of 98%. Dataset VPN
stands for encrypted and non-VPN for plaintext (See Table 3).
The test results showed that the RF outperformed the NN by
a small margin. We consider that this is because the RF parameters (such as “fixed random seeds” and hyperparameters) happened to be well set. NN has also many important parameters
TABLE 3

0.2

| 317

Metrics for entropy methods
Non-VPN

VPN

∑

Non-VPN

97.7%

1.0%

1651

VPN

2.3%

99%

348

∑

1686

313

1999

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

  

ZHOU et al.

|   

ZHOU et al.

of NN, we could not conclude that RF outperformed the NN
methods, and it was highly possible that fine-tuning of the parameters of NN could produce better results.

1.0

TP rate (sensitivity)

0.8

|

4.1

0.6

0.4

0.2

SVM
Random Forest
Naive Bayes
Logistic Regression
Neural Network

0
0

0.2

0.4
0.6
FP rate (1-specificity)

0.8

1.0

Encrypted traffic classification

We compared traditional machine learning methods with
our combined approach for classification using the same
dataset, NN, and parameters. The following two ROC
curves (Figure 9) representing the FP rate for “VPN” and
“Non-VPN,” respectively, demonstrated the traditional machine learning methods used to distinguish encrypted from
plaintext traffic. These traffic traces were directly classified
without using the entropy method.

(A)
1.0

1.0
0.8
TP rate (sensitivity)

TP rate (sensitivity)

0.8

0.6

0.4

0.6

0.4

0.2

0.2

SVM
Random Forest
Naive Bayes
Logistic Regression
Neural Network

0
0

0.2

0.4

0.6

0.8

SVM
Random Forest
Naive Bayes
Logistic Regression
Neural Network

0
0

0.2

1.0

0.4

0.6

0.8

1.0

FP rate (1-specificity)

(A)

FP rate (1-specificity)

(B)
1.0

FIGURE 9

(A) FP rate for Non-VPN class using traditional
methods. (B) FP rate for VPN class using traditional methods

TABLE 4

Metrics using the traditional methods

Method

AUC

F1

Precision

Recall

SVM

0.500

0.274

0.657

0.270

Random forest

0.933

0.915

0.916

0.919

Neural network

0.819

0.846

0.858

0.868

Naïve Bayes

0.779

0.768

0.809

0.746

Logistic regression

0.717

0.787

0.792

0.830

TP rate (sensitivity)

0.8

0.6

0.4

0.2

SVM
Random Forest
Naive Bayes
Logistic Regression
Neural Network

0
0

to set, and we simply used the combination of ReLU activation function, Adam solver, regularization alpha = 0.002, and
maximum 10 000 iterations, and the results were close to RF.
Because we did not exhaust the combinations of the parameters

0.2

0.4

0.6

0.8

1.0

FP rate (1-specificity)

(B)

F I G U R E 1 0 (A) FP rate for Non-VPN class using our combined
approach. (B) FP rate for VPN class using our combined approach

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

318

TABLE 5

Metrics of our proposed methods

Method

AUC

F1

Precision

Recall

SVM

0.443

0.564

0.714

0.505

Random forest

0.986

0.971

0.971

0.971

Neural network

0.947

0.925

0.929

0.930

Naïve Bayes

0.784

0.769

0.811

0.751

Logistic regression

0.732

0.794

0.807

0.836

Metrics in Table 4 summarize the two kinds of class type
results using five different methods with four criteria using
the traditional approach.
Note that recall (Rc), precision (Pr), and F1 score (F1)
are important metrics for classification performance. These
metrics are calculated as (4).

2TP
,
F1 =
2TP + FP + FN
TP
Precision =
,
TP + FP
TP
.
Recall =
TP + FN

(4)

AUC represents the area the ROC curve occupies. The xaxis stands for the cumulative distribution of the false-alarm
TABLE 6

Metrics for different classes
of applications using traditional methods

FIGURE 11

Matrix for different
application types using traditional methods

TP Rate

FP Rate

| 319

probability (FP rate) and the y-axis for the cumulative distribution of the detection probability (TP rate). Using our combined approach, we obtained the following results of the ROC
curve for the two class types (“VPN” and “Non-VPN”). The
same traffic traces were tested with our combined approach.
They were first distinguished as encrypted or non-encrypted
and then further classified if encrypted. Two kinds of class type
results using our combined approach are summarized in Figure
10 and Table 5.
To compare the traditional and our combined approach, the
same parameters as in “cross-validation” were used. We concluded that all five methods’ performances have been improved,
from 1 percentage point for the naïve Bayes method to 7 percentage points for the NN.

4.2

|

Application of traffic classification

As stated in the methodology section, we used Tor/non-Tor
dataset as plaintext traffic classified by the first stage of the entropy method to classify applications. Results in Table 6 were
obtained by using traditional machine learning methods, and
the confusion matrix (Figure 11) was specifically for NNs.
Metrics in Table 7 were for our combined approach, and
the confusion matrix (Figure 12) was also for the same NN.
Precision

Recall

F1

ROC Area

Class

0.963

0.040

0.939

0.963

0.951

0.968

VoIP

0.357

0.020

0.385

0.357

0.370

0.672

Audio

0.306

0.050

0.367

0.306

0.333

0.661

Browsing

0.571

0.065

0.500

0.571

0.533

0.803

Chat

0.478

0.023

0.550

0.478

0.512

0.735

Email

0.740

0.041

0.712

0.740

0.725

0.870

FTP

0.500

0.007

0.625

0.500

0.556

0.742

P2P

0.636

0.083

0.636

0.636

0.636

0.813

Video

0.719

0.049

0.713

0.719

0.715

0.855

Weighted Avg.

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

  

ZHOU et al.

|   

ZHOU et al.

TP Rate

FP Rate

Precision

Recall

F1

ROC Area

Class

0.994

0.004

0.994

0.994

0.994

1.000

VoIP

0.857

0.008

0.800

0.857

0.828

0.997

Audio

0.889

0.013

0.865

0.889

0.877

0.993

Browsing

0.976

0.011

0.911

0.976

0.943

0.997

Chat

0.826

0.000

1.000

0.826

0.905

0.996

Email

0.940

0.003

0.979

0.940

0.959

0.999

File-Transfer

0.800

0.000

1.000

0.800

0.889

0.998

P2P

0.974

0.015

0.938

0.974

0.955

0.995

Video

0.954

0.007

0.956

0.954

0.954

0.998

Weighted Avg.

TABLE 7

Metrics for different classes
of applications using our combined methods

FIGURE 12

Matrix for different
application types using our combined
approach

The criteria of the TP rate, FP rate, precision, and recall
for classification have been greatly improved, with some metrics nearly 30 percentage points up, which proved the effectiveness of our approach in traffic applications.

5

|

CO NC LU SION S

We analyzed the computational complexities for the combined approach. For training a NN, we analyzed the time
complexity that has three layers with i, j, and k nodes, respectively, with n training examples and m epochs. The
result was O(mn × (ij + jk)). For the SVM problem, the
computational complexity was on the order of n3 (n is the
size of the training dataset). RF is an ensemble model of
decision trees. The time complexity for building one decision tree is O(v × n log(n)), where n is the number of
records and v is the number of variables. Therefore, for a
RF with ntree number of trees, the complexity would be
O(ntree × v × n log(n)). For naïve Bayes, it is O(N × d),
where N is the number of training examples, and d stands
for the dimensionality of the features. For logistic regression, computational complexity with gradient-based optimization is O(f × c × s × e), with f features, c classes, s
samples, and e epochs. Complexity for entropy estimation

is at the same scale as naïve Bayes. The overall complexity
of the combined approach is the maximum of all the aforementioned methods.
Finally, we concluded that our combined approach outperformed all the other naïve machine learning methods on
the “ISCX VPN-NonVPN/ISCX-Tor-NonTor-2017” traffic
dataset in the traffic classification. We envisage that our
work can be viewed as a fusion of machine learning, especially deep learning, with traffic classification issues.
Although deep learning methods for traffic classification
were proposed and reported with high accuracy, open issues still exist: for example, features or models may be
non-representative, or the approach may only work for a
particular dataset. Moreover, our approach has only been
studied on certain types of traffic. A comprehensive study
of new encryption protocols, such as TLS 1.3, has not been
conducted yet.
ACKNOWLEDGMENTS
The author would like to thank all the anonymous reviewers for valuable suggestions and the Canadian Institute for
Cybersecurity for the datasets.
CONFLICT OF INTEREST
The author and co-authors have no conflict of interest to declare.

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

320

ORCID
Kun Zhou https://orcid.org/0000-0002-7926-6017
Chenhuang Wu
https://orcid.org/0000-0001-8002-7630
Teng Hu
https://orcid.org/0000-0002-8624-0210
R E F E R E NC E S

1. C. V. Wright et al., Language identification of encrypted VoIP traffic:
Alejandra y Roberto or Alice and Bob?, in Proc. USENIX Security
Symp. USENIX Security Symp., Moston, MA, USA, Aug. 2007,
Article no. 4.
2. C. V. Wright et al., Spot me if you can: Uncovering spoken phrases
in encrypted VoIP conversations, in IEEE Symp. Security Privacy,
Oakland, CA, USA, May 2008, pp. 35–49, https​://doi.org/10.1109/
SP.2008.21.
3. B. Anderson, S. Paul, and D. McGrew, Deciphering malware's
use of TLS without decryption, arXiv, 2016. https​
://arxiv.org/
abs/1607.01639​.
4. C. V. Wright, F. Monrose, and G. M. Masson, On inferring application protocol behaviors in encrypted network traffic, J. Mach.
Learning Research 7 (2006), 2745–2769.
5. J. Sherry et al., BlindBox: Deep Packet Inspection over Encrypted
Traffic, in Proc. ACM Conf. Special Interest Group Data Commun.,
London, UK, Aug. 2015, pp. 213–226.
6. Q. Sun et al., Statistical identification of encrypted web browsing
traffic, in Proc.IEEE Symp. Security Privacy Berkeley, CA, USA,
May 2002, pp. 1–12.
7. M. Liberatore and B. N. Levine, Inferring the source of encrypted
HTTP connections, in Porc. ACM Confe. Comput. Commun.
Security, Alexandria, VA, USA, 2006, pp. 255–263.
8. R. Schuster, V. Shmatikov, and E. Tromer, Beauty and the burst:
Remote identification of encrypted video streams, in Proc.USENIX
Security Symp., Vancuver, Canada, 2017, pp. 1357–1374.
9. D. X. Son, D. Wagne, and X. Tian, Timing analysis of keystrokes
and timing attacks on SSH, in Proc. USENIX Security Symp.,
Washington, DC, USA, Aug. 2001, Article no. 25.
10. P. Dorfinger, G. Panholzer, and W. John, Entropy estimation for
real-time encrypted traffic identification, in Proc. Int. Workshop
Traffic Monitoring Analysis, Vienna, Austria, 2011, pp. 164–171.
https​://doi.org/10.1007/978-3-642-20305-3_14.
11. A. Moore, D. Zuev, and M. Crogan, Discriminators for use in flowbased classification, Department of Computer Science Research
Reports; RR-05-13, 2005.
12. P. Velan et al., A survey of methods for encrypted traffic classification and analysis, Int. J. Netw. Manag. 25 (2015), 1–24.
13. D. J. Arndt and A. N. Zincir-Heywood, A comparison of three
machine learning techniques for encrypted network traffic
analysis, in IEEE Symp. Computat. Intell. Security Defense
Applicat. Paris, France, Apr. 2011, https​
://doi.org/10.1109/
CISDA.2011.5945941.
14. T. T. Nguyen and G. Armitage, A survey of techniques for Internet
traffic classification using machine learning, IEEE Commun.
Surveys Tutor. 10 (2008), 56–76. https​
://doi.org/10.1109/
SURV.2008.080406.

  

| 321

15. J. Zhang et al., Network traffic classification using correlation information, IEEE Trans. Parallel Distrib. Syst. 24 (2012), 104–117.
https​://doi.org/10.1109/TPDS.2012.98.
16. A. Finamore et al., KISS: Stochastic packet inspection classifier for
UDP traffic, IEEE/ACM Trans. Netw. 18 (2010), 1505–1515. https​
://doi.org/10.1109/TNET.2010.2044046.
17. B. Anderson, S. Paul, and D. McGrew, Deciphering malware’s use
of TLS, [without decryption] J. Comput. Virology Hacking Techn.
14 (2018), 195–211.
18. J. A. Bonachela, H. Hinrichsen, and M. A. Munoz, Entropy estimates of small data sets, J. Phys. A: Math. Theor. 41 (2008), 1–9.
19. J. Goubault-Larrecq and J. Olivain, Detecting Subverted
Cryptographic Protocols by Entropy Checking, Research Report
LSV-06-13, 2006, INRIA Futurs projet SECSI.
20. L. Paninski, Estimation of entropy and mutual information, Neural
Computation, Neural Comput. 15 (2003), 1191–1253.
21. M. Lotfollahi et al., Deep Packet: A novel approach for encrypted
traffic classification using deep learning, Soft Comput. (2019),
1–14, https​://doi.org/10.1007/s00500-019-04030-2.
22. G. D. Gil et al., Characterization of encrypted and VPN traffic using time-related features, in Proc. Int. Conf. Inform. Syst.
Security Privacy, 2016 pp. 407–414, https​://doi.org/10.5220/00057​
40704​070414.
23. B. Yamansavascilar et al., Application identification via network
traffic classification, in Proc. Int. Conf. Comput., Netw. Commun.,
Santa Clara, CA, USA, Jan. 2017, https​://doi.org/10.1109/ICCNC.
2017.7876241.
24. B.-H. Asa et al., Support vector clustering, J. Mach. Learn.
Research 2 (2001), 125–137.
25. T. K. Ho et al., The random subspace method for constructing decision
forests, IEEE Trans. Pattern Anal. Mach. Intell. 20 (1998), 832–844.
26. I. Rish, An empirical study of the naive Bayes classifier, IJCAI
Workshop Empirical Methods AI 3 (2001), 41–46.
27. G. Aceto et al., Multi-classification approaches for classifying mobile app traffic, J. Netw. Comput. Applicat. 103 (2018),
131–145.
28. G. Aceto et al., Mobile encrypted traffic classification using deep
learning: Experimental evaluation, lessons learned, and challenges, IEEE Trans. Netw. Service Manag. 16 (2019), 445–458.
29. G. Aceto et al., Anonymity services Tor, I2P, JonDonym:
Classifying in the Dark (Web), IEEE Trans. Dependable Secure
Comput. (2018), Early Access.
30. V. F. Taylor et al., Appscanner: Automatic fingerprinting of smartphone apps from encrypted network traffic, in Proc. IEEE Eur.
Symp. Security Privacy (EuroS&P), Saarbrucken, Germany, Mar.
2016, pp. 439–454.
31. S. Rezaei and X. Liu, Deep learning for encrypted traffic classification: An overview, IEEE Commun. mag. 57(2019), 76–81.
32. M. Lotfollahi et al., Deep packet: A novel approach for encrypted traffic classification using deep learning, Springer, Berlin
Heidelberg, Soft Computing, 2019, pp. 1–14.
33. G. Aceto et al., Mobile encrypted traffic classification using deep
learning, in Proc. Netw. Traffic Measurement Analysis Conf.,
Vienna, Austria, June 2018, pp. 1–8.

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

ZHOU et al.

|   

AUTHOR BIOGRAPHIES
Kun Zhou received his BS degree in
information
engineering
from
Southwest Normal University, China, in
2000, and his MS degree in computer
applications from the School of
Electronic
Engineering,
Beijing
University
of
Posts
and
Telecommunications, China, in 2006.
From 2000 to 2003 and from 2006 to 2016, he worked for
the Institute of Computer Applications, China Academy of
Engineering Physics, where he is now a senior research engineer. He is now pursuing his doctorate in computer science
at the University of Electronic Science and Technology of
China. His research interests are cybersecurity-related issues
with artificial intelligence technologies, such as machine
learning and deep learning.
Wenyong Wang received a BS degree
in computer science from BeiHang
University, Beijing, China, in 1988, and
MS and PhD degrees from the University
of Electronic Science and Technology
(UESTC), Chengdu, China, in 1991 and
2011, respectively. He has been the pro
fessor and supervisor for PhD students
in computer science and engineering. He served as a director
of the Information Center of UESTC and chairman of the
UESTC-Dongguan Information Engineering Research
Institute since 2003. He holds many academic titles, such as
an IEEE member, senior member of the Chinese Computer
Federation, director of China Internet Association, and
member of China Next-Generation Internet Committee of
Experts. He is now a visiting professor at Macau University
of Technology. His main research interests include computer
networks, next-generation Internet, software-defined networking, software engineering, and artificial intelligence.

ZHOU et al.

Chenhuang Wu received his BS degree in mathematics from Minnan
Normal University, China, in 2007.
Since then, he has been with the School
of Mathematics and Finance, Putian
University. Currently, he is an associate professor at Putian University and
is pursuing his doctorate at the
University of Electronic Science and Technology of
China. His research interests include elliptic curve cryp
tography and digital signatures.
Teng Hu received his BS degree from
Sichuan University in 2011 and his MS
degree from Beijing University of Posts
and Telecommunications in 2014.
Currently, he is a Ph.D. candidate in
the School of Computer Science and
Engineering, University of Electronic
Science and Technology of China,
Chengdu. His research interests include cyber-security,
big-data security, and blockchain security.

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

322

| 323

APPENDIX A

TABLE A1

Definitions for ISCX VPN-Non-VPN dataset's 23 features

No

Feature

Definitions

1

duration

Flow transmitting time

2

total_fiat

Total inter-arrival time for forward communication

3

total_biat

Total inter-arrival time for backward communication

4

min_fiat

Minimum packet inter-arrival time for forward communication

5

min_biat

Minimum packet inter-arrival time for backward communication

6

max_fiat

Maximum packet inter-arrival time for forward communication

7

max_biat

Maximum packet inter-arrival time for backward communication

8

mean_fiat

Mean of inter-arrival time for forward communication

9

mean_biat

Mean of inter-arrival time for backward communication

10

flowPktsPerSecond

Flow packets per second, pps

11

flowBytesPerSecond

Flow bytes per second, Bps

12

min_flowiat

Minimum flow inter-arrival time

13

max_flowiat

Maximum flow inter-arrival time

14

mean_flowiat

Mean of flow inter-arrival time

15

std_flowiat

Standard deviation of flow inter-arrival time

16

min_active

Minimum flow active time

17

mean_active

Mean of flow active time

18

max_active

Maximum of flow active time

19

std_active

Standard deviation of flow active time

20

min_idle

Minimum flow idle time

21

max_idle

Maximum flow idle time

22

mean_idle

Mean of flow idle time

23

std_idle

Standard deviation of flow idle time

22337326, 2020, 3, Downloaded from https://onlinelibrary.wiley.com/doi/10.4218/etrij.2019-0190 by CochraneChina, Wiley Online Library on [18/08/2025]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

  

ZHOU et al.
PAPER_TEXT
