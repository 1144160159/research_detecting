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
# [111] Markov‐GAN: Markov image enhancement method for malicious encrypted traffic classification
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
编号：111
题名：Markov‐GAN: Markov image enhancement method for malicious encrypted traffic classification
年份：2022
DOI：10.1049/ise2.12071
来源：IET Information Security
PDF：paper/10.1049_ise2.12071.pdf
已有粗分类：加密流量分类与应用识别
二级关联：恶意流量、暗网与攻击检测、多媒体、医学、遥感与视频异常检测
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\111.txt
- 原始字符数：65475
- 本次发送字符数：65475
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Received: 27 August 2021
DOI: 10.1049/ise2.12071

- Revised: 9 April 2022

Accepted: 7 June 2022

ORIGINAL RESEARCH

-

IET Information Security

Markov‐GAN: Markov image enhancement method for
malicious encrypted traffic classification
Zhangguo Tang1,2
| Junfeng Wang3 | Baoguo Yuan3 | Huanzhou Li2 |
Jian Zhang2 | Han Wang2
1

School of Cyber Science and Engineering, Sichuan
University, Chengdu, China

2

School of Physics and Electronic Engineering,
Sichuan Normal University, Chengdu, China

3

College of Computer Science, Sichuan University,
Chengdu, China
Correspondence

Junfeng Wang, College of Computer Science,
Sichuan University, Chengdu 610065, China.
Email: wangjf@scu.edu.cn
Funding information
Basic Research Program of China, Grant/Award
Number: 2019‐JCJQ‐ZD‐113; National Key
Research and Development Program, Grant/Award
Numbers: 2018YFB0804503, 2019QY1400;
National Natural Science Foundation of China,
Grant/Award Numbers: U1836103, U20A20161

Abstract
The rapidly growing encrypted traffic hides a large number of malicious behaviours. The
difficulty of collecting and labelling encrypted traffic makes the class distribution of
dataset seriously imbalanced, which leads to the poor generalisation ability of the classification model. To solve this problem, a new representation learning method in
encrypted traffic and its diversity enhancement model are proposed, which uses the diversity of images to represent the diversity of traffic samples. First, the encrypted traffic is
transformed into Markov images. Then, a diversity maximisation Markov‐GAN based on
the Simpson index is designed to generate new Markov images. Finally, the balanced
Markov image set is sent to the CNN for classification. Experimental results show that
the proposed method can predict the whole dataset space with only a few original
samples. And the classification accuracies under different imbalance degrees are significantly improved, all of which are over 90%. The enhanced Markov image set can
effectively alleviate performance generalisation deviation caused by different network
depths. Even an ordinary CNN has almost the same classification effect as VGG13 and
VGG16. Compared with other data enhancement methods, the Markov‐GAN only needs
to balance the transform domain dataset, which is lightweight, easy to train and has
stronger amplification ability.
KEYWORDS
class imbalance, generalisation ability, malicious encrypted traffic, Markov image, Markov‐GAN, representation
learning

1 | INTRODUCTION
With the promotion of global industrial digital transformation
and the development of mobile network and IoT, a large
number of network services and applications use encryption
technology as a priority method to ensure information security
[1]. Gartner predicted in 2019 that 80% of website traffic will
be encrypted [2]. Traffic encryption not only protects privacy
but also allows malicious behaviour to escape the supervision
of traditional security detection technology. More than 70% of
malware activities use some type of encryption to hide malware
transmission, control command activity and data leakage [3].
New Zscaler threat research reveals the emerging techniques

-

and impacted industries behind a 260‐percent spike in attacks
using encrypted channels to bypass legacy security controls [4].
Cyren [5] also found that the attacks of ransomware using
encrypted traffic have increased by 5 times, and each major
ransomware family has spread through HTTPS. In the field of
mobile applications, malicious APPs generally use encrypted
traffic (such as HTTPS) to transmit network data to avoid
detection. More than 30% of SSL‐based attacks deceived
trusted cloud providers such as Dropbox, Google, Microsoft
and Amazon to distribute malware through encrypted channels, which has become more and more complex in avoiding
detection [6]. Therefore, how to effectively identify malicious
traffic has become an important challenge to network security.

This is an open access article under the terms of the Creative Commons Attribution‐NonCommercial‐NoDerivs License, which permits use and distribution in any medium, provided the
original work is properly cited, the use is non‐commercial and no modifications or adaptations are made.
© 2022 The Authors. IET Information Security published by John Wiley & Sons Ltd on behalf of The Institution of Engineering and Technology.
442

IET Inf. Secur. 2022;16:442–458.

wileyonlinelibrary.com/journal/ise2

- 443

TANG ET AL.

There are two difficult problems in the identification and
classification of encrypted traffic. On the one hand, the
characteristics of encrypted traffic have changed or hidden,
which makes the traditional traffic detection technology
difficult to extract and represent effectively. In order to solve
this problem, deep learning methods have been continuously
introduced, such as RNN [7], GAN [8], CNN [9], KNN [10]
and LSTM [11]. These methods focus on continuously
improving the representation learning of malicious features in
encrypted traffic: either construct the feature engineering of
encrypted traffic, such as spatio‐temporal features, head features, load features, statistical features etc. [1, 12] or transform the traffic with different fineness into transform
domain forms such as image [13], matrix [14] or N‐gram
[15]. However, the effects of these encrypted traffic representation learning methods are limited to specific datasets,
and there are problems with preprocessing distortion and
difficult migration.
On the other hand, the existing malicious encrypted traffic
datasets have the class imbalance problem of ‘fat‐tail distribution’, which leads to insufficient training and seriously affects the accuracy and generalisation effect of classification.
For the datasets applied in some typical papers, the number of
samples varies greatly between different categories. For
example, in the dataset used by Wang [16], the maximum
training sample is 60,000, while the minimum is only 298. H. F.
Alan [17] found that the recognition accuracy of the models
trained by imbalanced datasets decreased by more than 21%
when applied. In order to solve this problem, semi‐supervised
method [18, 19], unsupervised method [13] and generative
method [20] are mainly proposed. Among them, semi‐
supervised uses a large number of easily available unlabelled
encrypted traffic and a small number of artificially labelled
encrypted traffic to form a dataset. The generation method
generally uses the GAN model [8] to fill the weak samples in
the encrypted traffic dataset, and the model learnt on the filled
dataset has a higher accuracy. However, these methods not
only need labelled data but also consider the matching problem
between the original dataset and the labelled dataset. Different
datasets have different features, which leads to the reduction of
model accuracy and generalisation ability.
In summary, there is neither a unified representation
method for encrypted traffic nor a sufficient and balanced
public label dataset [1, 12]. In order to solve the normalised
representation of encrypted traffic and the generalisation of
classification under the condition of imbalanced class distribution, a malicious encrypted traffic classification method
based on Markov image feature transformation and enhancement is proposed. The input is the original encrypted traffic
session, which is transformed into a normalised Markov image.
Then, through Markov‐GAN based on maximising population
diversity, new and more Markov images are generated. The
enhanced and balanced image set is sent to the CNN for
recognition and multi‐classification. Compared with the traditional encrypted traffic representation methods [10, 21, 22] and
data enhancement methods [8, 19, 20, 23], our method has
higher classification accuracy, stronger amplification ability and

better generalisation effect. The main contributions of this
paper are summarised as follows.
� An encrypted traffic representation method based on a
Markov image is proposed, which is the first time in the
traffic field. The high‐dimensional spatio‐temporal features
of the original encrypted traffic are represented as Markov
images with low‐rank structure, which realises the unified
representation learning of encrypted traffic datasets with
different specifications. This method does not need to slice
and fill the encrypted traffic artificially and reduces the
preprocessing distortion. Compared with the traditional grey
image, the Markov image is lighter and more friendly to the
classification model.
� A Markov‐GAN based on the compression coding loss
function and Simpson exponent is designed. The Markov‐
GAN not only enhances the texture quality and diversity
of Markov images but also uses as few original traffic
samples as possible to adaptively expand and balance the
image dataset, so as to realise the prediction of the sample
space of the whole original dataset.
Experiments have been conducted on multiple encrypted
traffic datasets and various imbalance degrees of datasets. In
terms of classification accuracy, the proposed method has
better effect. The accuracy of multiple datasets exceeds 99%,
which is higher than that of similar work. In terms of data
enhancement, the dataset is artificially set to a variety of
imbalance degrees, and the classification accuracy after
enhancement is significantly improved, all of which are over
90%. In terms of generalisation ability, the accuracy of the
proposed method on three different datasets is more than
97%, and the accuracy difference between models such as
ordinary CNN, VGG13 and VGG16 is only 0.15%. In addition, in terms of performance, compared with grey image, the
Markov image does not need segmentation and filling. It has
richer texture and lighter weight. The maximum decrease in
image size of the same length flow is 98.1%. Experimental
results show that the proposed method not only obtains higher
classification accuracy but also greatly improves the generalisation ability under imbalanced conditions.
The remainder of this paper is structured as follows: Section 2 reviews the related work of malicious encrypted traffic
classification. Then Section 3 details the method of malicious
encrypted traffic classification based on the Markov image
enhanced by the Markov‐GAN and CNN. Experimental
evaluation is given in Section 4. Finally, Section 5 concludes
this paper.

2 | RELATED WORK
The essence of malicious encryption traffic classification is to
learn the feature distribution of data. The stronger the ability
of feature compression (dimensionality reduction), the better
the accuracy and generalisation effect of classification [24].
Under the condition of imbalanced class distribution, there are

444

-

two main dimensions to improve the generalisation ability of
deep learning, namely, the representation learning of encrypted
traffic and the data enhancement of samples.

2.1 | Representation learning based on
feature engineering and transform domain
method
2.1.1 | Method based on feature engineering
The method based on feature engineering is to construct useful
data features through prior knowledge. The feature engineering
of encrypted traffic mainly includes space‐time features [10, 25],
head features [26], load features [26] and statistical features [27].
Ivan et al. [11] constructed the feature engineering of encrypted
traffic, extracted 40 data features of 4 categories, and obtained
94.87% accuracy by using the LSTM classification method.
Wang [28] gave six statistical features of TLS (upload byte,
download byte size etc.) and four statistical features of HTTPS
stream (user agent, request URL etc.). Gil et al. [10] proposed a
set of time‐related VPN traffic features, such as packet length,
transmission time interval, direction etc. Hu et al. [29] constructed the traffic features of the whole session according to
the length, arrival time interval and packet text distribution of
the first 150 data packets of the TLS session. Anderson et al.
[30] extracted the features of 18 types of malicious encrypted
traffic from the text information of encryption protocol
packets, including encryption suite, compression function,
supported version and other parameters and achieved an accuracy of 90.3%. Nychis et al. [31] studied the distribution of
encrypted traffic header features and behaviour features based
on entropy and pointed out that it is more effective to use time
series to construct feature engineering.
The feature engineering of encrypted traffic directly affects
the classification accuracy and generalisation effect [32].
Although it has achieved high accuracy in a specific experimental dataset, this method heavily relies on artificial prior
knowledge and the dimension of feature extraction is limited,
which leads to over‐fitting of classification model and poor
generalisation ability.

2.1.2 | Transform domain method based on
feature self‐learning
In order to solve the problem of difficult feature extraction of
encrypted traffic data and enhance the ability of representation
learning and generalisation, a transform domain method based
on feature self‐learning is proposed, that is, the neural network
automatically learns the useful features hidden in the data.
Feature self‐learning based on traffic image transformation: Wang [21] first proposed an encrypted traffic
classification method based on traffic image conversion. The
first 784 bytes of traffic are converted into grey image, and
the image data features are learnt by a two‐dimensional CNN.
The accuracy is 99.17% on the USTC‐TFC2016 dataset. Guo

TANG ET AL.

[13] used the first 1521 bytes of the traffic session as the
feature vector and converted it into a 39 � 39 grey image.
The average accuracy of 92.92% is obtained by using a two‐
dimensional convolutional neural network. Bazuhair et al. [26]
used Perlin noise to encode the given connection features
into images and trained a deep learning model of connection
stream for two classification. The accuracy rate on the CTU‐
13 dataset has reached 97%.
Feature self‐learning based on traffic conversion to Markov
chain: Korczynski [22] first proposed an encrypted traffic
classification method based on a Markov chain. The SSL/TLS
transmission message sequence is abstracted as a time‐varying
Markov random process. The SSL/TLS message is modelled
by the Markov chain, and the true positive rate is 97%. This
work has been improved by other researchers [14, 33].
Considering the two‐way communication process of encrypted
session, an encrypted traffic classification method based on the
perceptible attribute of a second‐order Markov chain is proposed, which further improves the detection effect.
Feature self‐learning based on transforming traffic into
vector: Cheng et al. [9] extracted the first 1000 bytes of the
traffic session payload as the feature vector and used skip‐gram
to embed words with a dimension of 300 in each byte of the
feature vector to form a new feature vector. The accuracy of
91.03% is obtained by using a one‐dimensional convolutional
neural network. Wang et al. [15] took the text content of the
header of the data packet as a fixed length sentence vector, in
which the byte information is regarded as a word, and used the
long‐term and short‐term memory neural network model to
learn the temporal relationship between bytes, with an accuracy
of 97.2% on the Mirai‐RGU dataset. In addition, Wang et al.
[35] proposed a traffic feature vector synthesis method based
on a stack automatic encoder, which can classify and identify
the applications of encrypted traffic.
The transform domain method based on feature self‐
learning does not need to extract data features manually and
has good portability. But the shortcomings are also obvious. For
example, it is necessary to slice, intercept and fill traffic data.
Most of these processes are based on experience and have natural information loss. In addition, it is difficult to normalise the
traffic to grey image. The size of the picture depends heavily on
the length of the traffic, which affects the generalisation performance and training efficiency. The Markov chain is difficult
to directly input the learning model, and it is difficult to train.

2.2 | Dataset balancing method based on
data enhancement
This method uses the existing samples to generate more
samples and expands the weak samples to eliminate the
imbalance of the dataset, so as to improve the generalisation
performance of the model. At present, there are mainly semi‐
supervised [18] and unsupervised [13] methods. Japkowicz
et al. [36] pointed out that imbalanced class distribution would
hinder the performance of standard classifiers, and then proposed two dataset balancing methods: RUS and ROS. Chawla

- 445

TANG ET AL.

[37] proposed a method combining over‐sampling and under‐
sampling of a few classes to obtain better classification results.
Rezaei [19] combined a large amount of unlabelled traffic data
and a small amount of artificially labelled traffic data to form a
training dataset for pretraining and retraining, respectively, and
the accuracy was improved to 84.53%. Grolman [38] instantiates a small number of marked encrypted traffic in the
source configuration and generalises it to different configurations, which can identify user operations in different unmarked
target configurations.
The more novel idea is the generative model. The advantages of the GAN are used for data enhancement, and its
generalisation ability is reflected in high fidelity and diversity.
Vu et al. [8] used the AC‐GAN to fill the weak samples in the
dataset, and many algorithms such as SVM, DT and RF have
obtained higher recognition accuracy on the dataset filled
successively. Wang [20] used the CGAN to generate encrypted
traffic to supplement the samples of vulnerable categories, so
as to balance the traffic dataset. Compared with the original
traffic dataset, the detection rate is further improved by 1.54%.
Further work transformed the GAN discriminator into a
classifier SGAN [23], supplemented a small number of labelled
samples, and formed a new balanced dataset.
Although these data enhancement methods have achieved
certain results, compared with generating images, the GAN
needs to ensure its activity and aggressiveness to generate
encrypted traffic, which is difficult, and its availability cannot
be guaranteed. The generation method based on some
encrypted traffic is also difficult to be generalised to other
encryption protocols, and its universality is poor. More
importantly, compared with the huge sample space of the
original encrypted traffic, the amplification ability and effect of
directly generating traffic are very limited.
Table 1 gives a simple comparison of existing solutions,
mainly focussing on two indicators: dataset imbalance and
generalisation ability. As shown in Table 1, the method based
on feature engineering has large workload and poor portability.
The method based on transform domain does not need to
extract features manually, but the preprocessing distortion is
large. Data enhancement methods can effectively balance
datasets, but the current methods enhance the original traffic,
which has huge overhead and limited effect. Therefore, this
paper proposes a new transform domain method, which uses
the Markov image with low‐rank structure to perform unified
representation learning on malicious encrypted traffic. The
Markov‐GAN is used to generate images instead of generating
original traffic, and the indirect balance of the original dataset
is realised by enhancing the diversity of images.
TABLE 1

3 | THE PROPOSED METHOD
The general framework of the proposed method is shown in
Figure 1. It is divided into three specific stages: Markov image
conversion, image enhancement based on the Markov‐GAN
and encrypted traffic classification training.
Phase 1: The dataset Pcap file stores the original
encrypted traffic. Relevant experimental studies show that
session is a more robust traffic representation form [13, 21].
On the one hand, converting sessions into images does not
destroy the basic information of traffic. On the other hand,
the accuracy of session‐based classification is generally higher
than that of flow‐based classification. Therefore, it is necessary to split the original Pcap file by session and divide the
encrypted traffic dataset into different numbers and types of
Pcap sub‐files. The size of the subfile varies with the length
of the session. Then, according to the Markov image conversion algorithm, each traffic session is converted into a
Markov image.
Phase 2: This step is the key to solve the problem of
dataset imbalance. Because the class distribution of the original
traffic dataset is imbalanced, the converted ‘original Markov
image set’ inherits the imbalanced characteristic. Therefore, the
function of this stage is to use the proposed Markov‐GAN to
generate more new pictures and enhance the diversity of the
‘original Markov image set’. Then, a ‘new balanced Markov
image set’ is obtained for the later depth learning model to
train. It is worth emphasising that it is not the original traffic
that is generated, enhanced and balanced, but its transformed
domain image.
Phase 3. In this stage, a variety of different CNNs are used
as classification models to evaluate the performance of the
‘new balanced Markov image set’, which is used as training set.
The ‘original Markov image set’ is used as a test set to test the
classification effect, generation quality and balance ability of
the proposed model.

3.1 | Representation learning of malicious
encrypted traffic based on Markov images
Different encrypted traffic sessions have different probability
of message state transition. This random process has Markov
characteristics and can be used to characterise the temporal and
spatial characteristics of encrypted traffic [22, 33]. The specific
details of Markov transformation process have been discussed
in the relevant literature [34]. For convenience, a visual Markov
process of a four byte session sequence is given here. The

Comparison of classification methods under class imbalance

Method

Dataset

Features

Classification techniques

Weakness

Ref. [10, 11, 28–30]

Imbalance

Feature engineering

SVM, DT, RF

Difficult and poor generalisation ability

Ref. [9, 14, 15, 21]

Imbalance

Transform domain

CNN, LSTM

Relying on experience and large distortion

Ref. [18, 19, 35–37]

Artificial balance

Feature engineering

Semi‐supervised and unsupervised
method, ROS, Smote

Time consuming and poor portability

Ref. [8, 20, 23]

Machine generated balance

Traffic

GAN + CNN

Complex and poor universality

446

-

FIGURE 1

TANG ET AL.

Markov image enhancement method for malicious encrypted traffic classification

session is taken from the ISCXVPN2016 dataset, as shown in
Figure 2.
The conversation in the figure forms a transition probability sequence from beginning to end. It is cumbersome to
calculate the Markov chain matrix directly, and it is difficult to
input it directly into the classification model. Therefore, a
representation method based on the Markov image is proposed. The state transition of encrypted traffic message is
indirectly represented by the conversion between each byte in
the corresponding Pcap file, and the transition probability
matrix is encoded into the corresponding Markov image. This
method has the characteristics of low dimension and scale
invariance, that is, the session of traffic with variable lengths
can be transformed into a fixed length data format through a
Markov image structure. In addition, because this method does
not need traffic slicing and filling, the information loss caused
by feature extraction is minimised.
The specific method is to first split the original stream into
multiple independent Pcap files according to the session. Then,
the traffic file is read in binary mode and converted into byte
values (0–255) with one byte as a unit. The random process of
byte stream converted from encrypted traffic can be expressed as:
Bi ; i ∈ f0; 1; ::::; N − 1g

FIGURE 2

A visual Markov process of a four byte session sequence

2

p0;0
6 p1;0
PðX 2 jX 1 Þ ¼ 6
4⋮
p255;0

⋯
⋯
px1 ;x2
⋯

3
p0;255
p1;255 7
7
5
⋮
p255;255

ð2Þ

Where Px1,x2 are the transition probabilities, and x1 and x2
are the actual values of X1 and X2, respectively, that is x1,
x2 ∈ {0,1,...,255}. The calculation formula of Px1,x2 is as
follows:

ð1Þ

Where, N is the byte length of encrypted traffic, and Bi is
the value of the ith byte, Bi ∈ {0,1,....,255}.
Then, calculate the transition probability of two adjacent
bytes X1 and X2, that is, the probability P(X2|X1) that X2
appears after X1:

p0;1
p1;1
⋮
p255;1

P x1 ;x2 ¼

Pðx1 ; x2 Þ
PðX 2 jX 1 Þ
� �
¼ P255
�
Pðx1 Þ
j¼0 P X j X 1

ð3Þ

After obtaining the transition probability matrix, take every
two adjacent byte values as the coordinate points in the 256 �
256 size image, and its transition probability value is the value

- 447

TANG ET AL.

of the pixel point; then the matrix can be image encoded to
obtain the Markov image. The Markov image is based on the
ASCII code corresponding to each byte in the Pcap file, and its
range is 0–255. Therefore, the maximum number of transition
probabilities can be obtained is 65,536. Therefore, the size of
Markov graph is fixed, which is a 256 � 256 transition probability matrix obtained from formula (2).
Because the sessions of the same class of traffic have
similar transition probability, the Markov images of the same
class are homologous in probability. The process of converting
traffic into the Markov image is shown in algorithm 1 and
Figure 3, respectively:

Algorithm 1 Convert encrypted traffic into Markov
image
• Input:
Network traffic(Pcap);
• Output:
Markov image(Mi);
1: For Pcap in {1,2,...,n} do
2: Get network traffic quintuple content
3: Calculate transition probability
between contents
4: Estimate transfer probability Px1,x2
5: Generate transition probability matrix
P(X2|X1)
6: Image coding of transition probability
matrix → Mi
7: End For
8: Return Mi

3.2 | Generation model based on Markov‐
GAN
3.2.1 | Architecture and process of the Markov‐
GAN model
The framework of the Markov‐GAN model is shown in
Figure 4, including generator G, discriminator D, the DBSCAN
clustering network and ‘original Markov image set’. Among
them, the DBSCAN clustering network clusters the generated
Markov images for the calculation of regularisation terms. The
generator and discriminator realise the enhancement and balance of samples by synthesising gradient optimisation and diversity mechanism. The basic process is that after the noise
enters the generator G, a series of new Markov image countermeasure samples are generated, and the discriminator D
performs ‘true and false discrimination’ based on the ‘original
Markov image set’ template. At the same time, the corresponding the Simpson index is calculated by the DBSCAN
clustering network, and the diversity loss function is obtained
for back propagation. Legal and appropriate new Markov images are updated to the ‘original Markov image set’, and the
‘new balanced Markov image set’ is output.

FIGURE 3
image

Schematic diagram of traffic conversion to the Markov

In addition, in order to balance the fidelity and diversity
of the generated samples, the Markov‐GAN abandoned the
traditional cross entropy loss function and replaced it with a

448

-

FIGURE 4

TANG ET AL.

Framework of Markov‐GAN

classification oriented diversity maximisation loss function
and obtained stronger countermeasure samples by designing
regularisation constraints. Specific improvements are as
follows.

In the above formulae, the first item on the right of the
equal sign ensures that the generated samples are as real as
possible with high fidelity. The second is to ensure that the
generated samples have different characteristics as far as
possible, that is, the greatest diversity.

3.2.2 | Diversity maximisation loss function
based on compression coding

Coding length loss function
Due to the strong randomness of the conversion of malicious
encrypted traffic file bytes in high‐dimensional space, the
converted Markov image texture is special and difficult to be
accurately quantified by the cross‐entropy loss function.
In order to ensure the fidelity of the generated samples,
considering the physical significance of the transition probability of adjacent fields, a coding length function (CLF) is
proposed to measure the degree of information compression.
This function has the ability of image compression representation and can guide the Markov‐GAN to generate new Markov images with family homology and texture similarity, so as
to improve the game level between the discriminator and
generator. The coding length function is a data compression
representation method proposed in combination with rate
distortion theory, as shown in formula (6):

The Markov‐GAN needs to finely control the trade‐off between sample fidelity and diversity. The traditional GAN
usually measures loss by maximising similarity, but it is
difficult to define similarity when it is applied to data with
high‐dimensional degraded distribution such as encrypted
traffic. The classification and clustering task is a data
compression mechanism, that is, to find the low rank structure of high‐dimensional targets [37]. The generalisation
ability can also be regarded as the information compression
ability of the classification model to some extent [24]. The
GAN network can be well adapted to such compression
scenarios, but the generated samples have the problem of
homogeneous pattern collapse. Therefore, a new measurement parameter and loss function are designed for classification task, that is, the coding length loss function with the
Simpson index as regularisation term. The loss functions of
the Markov‐GAN discriminator and generator are shown in
formulae (4) and (5), respectively.
Ld−loss ¼ Ex�PT ag Lðx; εÞ
− Ex�P g Lðx; εÞ − λ½SPI − α�2
� �
Lg −loss ¼ Ex�P T ag L x; ε − λ½SPI − α�2

ð4Þ

ð5Þ

�
�
�
�
mþD
D
T
Lðx; εÞ ¼
log det l þ 2 XX
2
mε

ð6Þ

Where m and D are the size of the data, respectively,
corresponding to the length and width of the Markov image. I
is the upper network residual, and X is the image tensor. ε is a
constraint constant parameter used to determine the
compression accuracy, which is generally 0.000,001. The whole
coding length function can maximise the space occupied by its
expression while making the samples of the same structure

- 449

TANG ET AL.

close, that is, the sample expression ability is the largest. At the
same time, when the sample expression between different
structure data is optimal, the overall sample set has the
maximum coding length.

Regular term based on the Simpson index
The Simpson index is a biological index used to measure species diversity in communities [39]. It is used here to evaluate the
species richness of the generated Markov images. In order to
enhance the diversity of generated samples and maximise the
range of each type of data, the Simpson index is taken as the
regular term of loss function, as shown in equation (7).
SPI ¼ 1 −

n
X

Pi

ð7Þ

i¼1

Where, Pi represents the probability that a class is selected
in an encrypted traffic dataset, and its calculation method is
shown in formula (8).
Pi ¼

Number of individuals in a group
Total number of individuals in the community

ð8Þ

The entire loss function is back propagated by initialising
the α parameter (generally no more than 1), and the SPI regularisation constraint is made to make the value as close to α as
possible, so as to guide the generator G to generate the Markov
image with the maximum type to achieve enhancement and
balance the goal.

parameters(C); Simpson index(spi); Height
and width of data(D,m); Control parameters
(ε); Constant(∂); Identity(I);
1: while θg has not converged do
2: For I = 1,…,m Do
3: Markov image x ~ Pdata(x); Noise sample
z ~ P(z);
4: Interpolation sampling of samples G(z);
5: Coding Length Function(CLF)L(x,ε)=
(D + m/2)logdet(I + D/mε2XXΤ)
6: Loss function of generator and
discriminator: // Use CLF and SPI to realise
the GAN loss function
7:Ld_loss = Ex � Pdata L(x,ε)−Ex � Pg L(x,ε)
−λ[spi−∂]2
8:Lg_loss = Ex � Pg L(x,ε)−λ[spi−∂]2
9: Update discriminator parametersθd and
generator parameters θg:
10:While D and G doesn't converge do
11:
While C clustering is complete do
12:
spi←spi(C((G(z)),θ)) // Simpson
index is calculated by clustering network
13:
θd←α⋅Adam(b1,b2,Δθd(Ld_loss))
14:
Then
15:
θg←α⋅Adam(b1,b2,Δθg(Lg_loss))
16:
End
17:End
18:End While

4 | EXPERIMENTAL EVALUATION
3.2.3 | Training algorithm of the Markov‐GAN

4.1 | The datasets and evaluation indicators

The generator G and the discriminator D of the Markov‐GAN
use a 5‐layer deconvolutional neural network and a 5‐layer
convolutional neural network, respectively. The first four
layers of generator G use the Leaky‐Relu function as the
activation function, and the last layer uses the tanh activation
function. The discriminator D uses the Leaky‐Relu function as
its activation function, and its output layer is a Dense layer with
an output node of 1 to judge the ‘true’ and ‘false’ of the
generated Markov image. Based on the results of DBSCAN
clustering, the Simpson index and the corresponding loss
function are calculated. At the same time, the Adam optimiser
is used to update the model parameters and weights by alternately training discriminator D and generator G until Nash
equilibrium is reached. The specific training process of
Markov‐GAN is shown in algorithm 2.

4.1.1 | Original dataset

Algorithm 2 Markov-GAN, our proposed algorithm
• Input: learning rate (α) = 0.01;
beta_1 = 0.9; beta_2 = 0.999; batch size (m);
• Output: generator parameters (θg);
discriminator parameters(θd); Classifier

The experiment was conducted on several typical original
encrypted datasets, as shown in Table 4.1, Table 4.2, and
Table 4.3 for details. These datasets cover multiple types of
encrypted traffic, and all have the problem of imbalanced class
distribution, which can be used to test the enhancement ability,
generalisation ability and classification accuracy of the proposed
model. The first is the USTC‐TFC2016 (Part I) dataset [21],
which contains 10 kinds of malware traffic from public websites
collected from real network environment from 2011 to 2015
[40]. The proportion of various samples in the dataset is
extremely uneven. For example, the number of sessions of
Htbot and Tinba malicious encryption traffic accounts for only
2.78% and 3.71%, respectively, while Cridex and Geodo account
for 26.24% and 18.10%, respectively. The second is the USTC‐
TFC2016 dataset (Part II), which contains 10 types of normal
traffic and can be used for encrypted traffic classification of
different application types. Among them, there are only 2990
Facetime streams and 11,506 FTP streams, which vary greatly.
The third is the ISCXVPN2016 dataset [10], including 15
different VPN encryption applications. The number of samples

450

-

TANG ET AL.

in many categories is far lower than the average, and the degree
of imbalance is very large. Based on these original public datasets, three kinds of experiments are given, including enhancement and balance ability experiment, accuracy comparison
experiment and representation and generalisation ability
experiment.

TABLE 2

Markov‐GAN structure and parameters

Markov‐GAN

Layer

Generator

Input

96

Dense

1024

Dense

2048

Dense
Discriminator

4.1.2 | Performance metrics

Accuracy ¼

TP þ TN
TP þ TN þ FP þ FN

ð9Þ

TP
TP þ FP

ð10Þ

TP
TP þ FN

ð11Þ

Precision ¼
Recall ¼

TABLE 3

ð12Þ

Tanh

65,536
(256,256)

Relu

512

Dense

256

Dense

1

Note: (1) Other parameters: batch_size = 128; learn_rate = 0.001; epochs = 100, (2)
Generator Optimisation algorithm parameters: optimiser:Adam, beta_1 = 0.9;
beta_2 = 0.999, (3) Discriminator Optimisation algorithm parameters: optimiser:Adam,
beta_1 = 0.9; beta_2 = 0.999, and (4) input noise size: 256 � 256.

CNN structure and parameters

Model

Layer

CNN

Conv 0

Rate

Activation

Filters

F ⋅ size

Strides

Relu

20

5

(2,2)

(2,2)

(2,2)

4

(2,2)

(2,2)

(2,2)

Pool 0
Conv1

Precision � Recall
F1 Score ¼ 2 �
Precision þ Recall

Shape

Input
Dense

In order to evaluate the performance indicators under imbalanced datasets from multiple dimensions, a set of performance
indicators are used for comprehensive evaluation, including
accuracy, precision, recall and F1 score, which are defined as
follows.

Activation

Relu

Pool 1

40

Flatten

Among them, TP and FP are the number of samples
correctly and incorrectly classified as wrong, respectively.
Correspondingly, TN and FN are the number of samples
correctly and incorrectly classified as correct, respectively.

Dense
Dropout
Dense

Relu
0.3
Arg_max

Note: (1) Other parameters: batch_size = 128; learning_rate = 0.001; epochs = 50 and
(2) Optimisation algorithm parameters: optimiser: Adam, beta_1 = 0.9; beta_2 = 0.999.

4.1.3 | Experimental platform and model
structure parameters
The proposed model is trained, tested and used in the
Windows environment. The configuration parameters are
Intel I7‐10,875H CPU 5.1 GHz, 32 GB RAM and external
GPU (NVIDIA GeForce RTX 2070S). The relevant code
is developed in Python language based on TensorFlow 2.0
framework.
The parameters of the Markov‐GAN and CNN models
used in this paper are shown in Table 2 and Table 3, respectively. DBSCAN Clustering algorithm's eps is 2.4 and min_samples is 20.

4.2 | Experimental results and analysis
4.2.1 | Dataset sample enhancement and balance
experiment
Data set conversion and balance.

First, the original encrypted traffic dataset in the form of
flow is transformed into a session form, and the traffic is
converted into Markov image one‐to‐one in the unit of session
to obtain the ‘original Markov image set’. The image set was
used as validation and test set in subsequent experiments.
Second, according to the imbalance of the original dataset, the
weak samples of the ‘original Markov image set’ are generated,
amplified and balanced based on the Markov‐GAN to obtain a
‘new balanced Markov image set’, which is used as a training set
in subsequent experiments. Table 4, Table 5 and Table 6 show
the situation before and after the balance of the three datasets.
It is worth noting that the proposed method balances the
converted Markov image set rather than the traffic of the
original data set. In addition, the Markov‐GAN has a strong
generation ability, which can be amplified and balanced to
varying degrees in different proportions. Limited to space, only
the minimum equilibrium proportion when the accuracy
improvement reaches saturation under experimental conditions
is given in the tables.

- 451

TANG ET AL.

T A B L E 4 USTC‐TFC2016 (Part I) data
generation and balance

New balanced Markov image
set

Original dataset
Malicious type

Flow

Session

Proportion of sessions

Image

Proportion of image

Cridex

90,087

60,058

26.24%

15,000

10.00%

Geodo

42,087

41,418

18.10%

15,000

10.00%

Htbot

12,734

6367

2.78%

15,000

10.00%

Miuref

26,962

13,481

5.89%

15,000

10.00%

Neris

69,825

36,751

16.59%

15,000

10.00%

Nsis‐ay

12,138

6069

2.65%

15,000

10.00%

Shifu

19,268

9634

4.21%

15,000

10.00%

Tinba

17,008

8504

3.71%

15,000

10.00%

Virut

71,200

35,600

15.56%

15,000

10.00%

Zeus

21,940

10,970

4.79%

15,000

10.00%

Total

383,249

228,852

100%

150,000

100%

T A B L E 5 USTC‐TFC2016 (Part II) data
generation and balance

New balanced Markov
image set

Original dataset
Application type

Flow

Session

Proportion of sessions

Image

Proportion of image

BitTorrent

7535

3767

16.03%

10,000

10.00%

Facetime

2990

2990

6.76%

10,000

10.00%

FTP

11,506

5753

13.01%

10,000

10.00%

Gmail

11,477

5723

12.95%

10,000

10.00%

MySQL

11,385

5692

12.86%

10,000

10.00%

Outlook

7467

3733

8.44%

10,000

10.00%

Skype

6028

3014

6.81%

10,000

10.00%

SMB

11,543

5770

13.05%

10,000

10.00%

Weibo

11,510

5755

13.02%

10,000

10.00%

WorldOfWarcraft

11,559

5779

13.07%

10,000

10.00%

Total

93,000

44,209

100%

100,000

100%

4.3 | Experiment on generation quality and
diversity of Markov images
In order to test the texture quality and diversity of the new
Markov image generated by the Markov‐GAN, based on the
USTC‐TFC2016 (Part I) dataset, the comparison between the
converted part of the original Markov image and the generated
Markov image is given. Figure 5a shows the original Markov
image of Cridex class, and b,c,d are the generated new Markov
images. Figure 6 shows different types of Markov images
generated.
It can be seen that, on the one hand, the Markov images
generated in the same class have similar texture distribution
with the original Markov images, that is, they have intra‐class
similarity and diversity. On the other hand, the generated
Markov images of different classes have significant inter‐class
differences, and their texture feature distributions are very

different. It can be seen that the coding loss function of the
Markov‐GAN and Simpson diversity index can work effectively. While ensuring the good fidelity of the generated image,
it can enhance the diversity and greatly expand the number of
effective samples.

5 | CLASSIFICATION ACCURACY AND
COMPARATIVE EXPERIMENT
5.1 | Effects of different imbalance degrees
and generalisation degrees on accuracy
In order to further explore the relationship between the
amount of generated samples and the imbalance degree of
dataset and classification accuracy, two quantitative parameters,
imbalance degree and generalisation degree, are proposed.

452

-

TANG ET AL.

New balancedMarkov image
set

Original dataset
Application type

Flow

Session

Proportion of sessions

Image

Proportion of image

AIM_chat

4869

4823

4.29%

10,000

6.67%

Email

4417

4417

3.93%

10,000

6.67%

Facebook

5527

2763

2.46%

10,000

6.67%

Gmail

7329

3664

3.26%

10,000

6.67%

Hangouts

7587

3793

3.37%

10,000

6.67%

ICQ

4243

3946

3.51%

10,000

6.67%

Netflix

51,932

15,966

14.19%

10,000

6.67%

SCPdown

15,390

7695

6.84%

10,000

6.67%

SFTPdown

4729

2364

2.11%

10,000

6.67%

Skype

4607

2303

2.05%

10,000

6.67%

Spotify

14,442

7221

6.42%

10,000

6.67%

TorTwitter

14,654

7327

6.51%

10,000

6.67%

Vimeo

18,755

9377

8.34%

10,000

6.67%

Voipbuster

35,469

29,456

26.19%

10,000

6.67%

Youtube

12,738

7369

6.55%

10,000

6.67%

Total

206,688

112,484

100%

150,000

100%

The imbalance degree is defined as the average of the
absolute value of the difference between the size of each type
of sample and the average of the total sample size, as shown in
Equation (13):
P
UD ¼

jX − μj
N

ð13Þ

Where, UD is the imbalance degree, Xi is the number of
samples of each class, μ is the average value of all samples, and
N is the total number of samples.
Generalisation degree is defined as the ratio of the total
number of samples (including converted and generated) after
balance to the converted original sample size, as shown in
Equation (14):
GD ¼

Original þ Generated
Original

ð14Þ

Where GD is the generalisation degree, Original is the
original sample size obtained by conversion, and Generated is
the generated sample size.
The experiment was conducted in three dimensions:
imbalance degree, generalisation degree and accuracy. Based on
the USTC‐TFC2016 (Part I) dataset, the number of samples of
the most vulnerable category is taken as the generalisation base,
that is, 5000 only. At the same time, five imbalance degrees are
artificially set, which are 0%, 20%, 40%, 60% and 80%. For
example, 0% means that the dataset is balanced, that is, 500
samples for each class. Then, the generated quantity is

T A B L E 6 ISCXVPN2016 data
generation and balance

generalised to different degrees while keeping the imbalance
degree unchanged. Finally, the converted ‘original Markov image
set’ is used for verification and test, and their classification accuracy is counted, respectively. The results are shown in Figure 7.
It can be seen that under the same total sample size, the
classification accuracy increases gradually with the imbalance
degree from high to low, which indicates that the balanced
dataset improves the classification effect. At the same time,
under the same imbalance degree, the accuracy will increase
significantly with the increase of generalisation degree of
generated samples, and the optimal accuracy all exceed 90%. It
should be noted that the improvement of accuracy is saturated,
that is, when the generalisation degree increases to a certain
extent, the classification effect will not be improved. This
critical point can be used to guide the selection of generalisation degree, which is also the basis for selecting corresponding
balance quantities in Table 4.1, Table 4.2 and Table 4.3. The
experimental results show that by indirectly enhancing and
balancing datasets, the Markov‐GAN can be applied to datasets of multiple types and multiple degrees of imbalance. While
significantly improving the classification accuracy, it greatly
reduces the dependence and requirements on the quantity and
quality of original datasets. A small number of original samples
can make a good prediction of the whole dataset.

5.2 | Comparison with other data
enhancement methods
In order to compare the data enhancement and balance effects
of different generation models, the accuracy rate, recall rate

- 453

TANG ET AL.

FIGURE 7
accuracy

FIGURE 5

Markov image sample of Cridex class

FIGURE 6

Markov image samples of different classes

and F1 score are compared with the FLOWGAN [23].
Different from the Markov‐GAN, the FLOWGAN generates
encrypted traffic and expands and balances the original traffic
dataset. Based on ISCXVPN2016 and the dataset enhanced by
the FLOWGAN and Markov‐GAN, respectively, the experimental data of corresponding classification effect are shown in
Table 7.

Influence of imbalance and generalisation degree on

It can be seen that the weak class of the original dataset
before balancing, such as AIM_chat and voipbuster, have poor
classification results. After using the GAN method for data
enhancement, the classification rates of all 15 classes have
increased to a high level, especially the weak class. For example,
all corresponding indicators of the AIM_chat category have
risen by nearly 30%. Compared with the FLOWGAN, the
average values of the three indicators of the Markov‐GAN
have further increased, all exceed 99%. The experiment
shows that compared with the method of simply expanding the
number of samples, the Markov‐GAN also considers the fidelity and diversity of the generated samples, which makes the
classification effect reach a higher level.
In order to further compare the ability of different data
enhancement methods to improve classification accuracy, the
related work is divided into three groups: original sample
balance based on artificial, machine‐based original sample
generation and balancing and machine‐based transform
domain sample generation and balance. The experimental results are shown in Table 8.
It can be seen from the table that compared with other
classification methods that do not use enhancement techniques, such as feature extraction‐based, cost‐sensitive, and
image transformation‐based classification techniques, the
method proposed in this paper using the Markov‐GAN for
data augmentation and then classification is more effective.
Compared with the other two data enhancement methods, the
accuracy and accuracy growth obtained by the Markov‐GAN
are higher. More importantly, the classification effect of the
ordinary CNN is equivalent to that of complex models such as
VGG13 and VGG16, all of which are maintained at more than
99.6%. It shows that the image set enhanced by the Markov‐
GAN is more friendly to the model and can effectively alleviate the performance generalisation deviation caused by
different network depths.

454

-

TABLE 7

TANG ET AL.

Comparison of classification results of the original dataset, FLOWGAN dataset, and Markov‐GAN dataset
Original dataset

FLOWGAN dataset

Markov‐GAN dataset

Class

Precision

Recall

F1_Score

Precision

Recall

F1_Score

Precision

Recall

F1_Score

AIM_chat

0.6987

0.5558

0.6191

0.9818

0.9496

0.9654

0.9913

0.9604

0.9756

Email

0.9655

0.9801

0.9728

1.0000

0.9930

0.9965

0.9944

0.9921

0.9932

Facebook

0.8313

0.6698

0.7419

0.9883

0.9798

0.9840

0.9893

0.9801

0.9847

Gmail

0.9392

0.9245

0.9318

0.9821

0.9860

0.9840

0.9871

0.9868

0.9869

Hangouts

0.6915

0.9282

0.7926

0.9879

0.9911

0.9895

0.9892

0.9910

0.9900

ICQ

0.7673

0.7280

0.7471

0.9394

0.9876

0.9629

0.9916

0.9965

0.9940

Netfilx

0.9734

0.9973

0.9852

0.9965

0.9938

0.9951

0.9946

0.9971

0.9952

Scpdown

0.9721

0.9997

0.9857

0.9997

1.0000

0.9998

1.0000

0.9996

0.9992

Sftpdown

0.9647

0.8299

0.8922

0.9978

0.9983

0.9980

0.9976

0.9982

0.9979

Skype

0.8949

0.8937

0.8943

0.9957

0.9922

0.9939

0.9889

0.9931

0.9910

Spotify

0.912 4

0.9866

0.9480

0.9970

0.9882

0.9925

0.9923

0.9934

0.9928

torTwitter

0.9934

0.9993

0.9963

0.9985

0.9993

0.9989

1.0000

0.9987

0.9993

Vimeo

0.9650

0.9945

0.9795

0.9852

0.9963

0.9894

0.9899

0.9946

0.9982

Voipbuster

0.8967

0.9928

0.9423

0.9982

0.9905

0.9943

0.9942

0.9956

0.9949

Youtube

0.9566

0.9997

0.9777

0.9982

0.9995

0.9988

0.9987

1.0000

0.9993

Average

0.8948

0.8987

0.8938

0.9898

0.9897

0.9895

0.9933

0.9918

0.9925

TABLE 8

Comparison with other methods

Technical route

Paper

Classification method

Balance model

Accuracy

Accuracy growth

Unenhanced classification methods

[42]

Multilayer perceptron

———

0.9372

———

[43]

CSCNN

———

0.9790

———

[21]

CNN

———

0.9917

———

[18]

CNN

Semi‐supervised

0.9850

0.0040

[20]

CNN

ROS

0.9889

0.0092

[20]

CNN

Smote

0.9769

−0.0028

[20]

CNN

PacketCGAN

0.9951

0.0154

[8]

RF

AC‐GAN

0.9989

0.0011

[23]

MLP

FLOWGAN

0.9910

0.0915

Ours

CNN

Markov‐GAN

0.9960

0.0965

Ours

VGG13 [41]

Markov‐GAN

0.9975

0.0980

Ours

VGG16 [41]

Markov‐GAN

0.9962

0.0967

Original sample balance‐based on artificial

Machine‐based original sample generation and balancing

Machine‐based transform domain sample generation and balance

5.3 | REPRESENTATION AND
GENERALISATION ABILITY
EXPERIMENT
5.3.1 | Representation ability experiment of
different transform domain methods
In order to test the performance of different representation
learning methods of encrypted traffic, the Markov image and
grey image are used for comparison test under the same

classification model. Based on USTC‐TFC2016 (Part I), 1000
Markov images of each type generated and balanced are used
as training set samples, and 100 images of each type are
extracted from the converted ‘original Markov image set’ as
test set samples. Accordingly, an equal amount of grey image is
converted, generated and balanced. Several comparison results
based on the two images are obtained in the experiment. The
confusion matrix of classification is shown in Figure 8, and the
three indexes of precision, recall and F1 score are shown in
Table 9 and Figure 9, respectively.

- 455

TANG ET AL.

FIGURE 8

Confusion matrix based on Markov image and grey image (a) Method based on Markov image and (b) method based on grey image

T A B L E 9 Comparison of precision,
recall and F1 score of two transform domain
methods

Method based on Markov image

Method based on grey image

Malicious type

Precision

Recall

F1 score

Precision

Recall

F1 score

Cridex

1

1

1

0.970

1

0.985

Geodo

0.990

0.990

0.990

0.950

0.950

0.950

Htbot

0.990

1

1

0.888

0.950

0.918

Miuref

1

1

1

1

1

1

Neris

0.980

0.980

0.980

0.949

0.940

0.944

Nsis‐ay

0.980

1

0.990

0.989

0.920

0.953

Shifu

1

1

1

0.990

1

0.995

Tinba

1

1

1

0.980

1

0.990

Virut

1

1

1

1

1

1

Zeus

1

1

1

1

1

1

Average value

0.994

0.997

0.996

0.972

0.976

0.974

As can be seen from Figure 8, both the method based on
the Markov image and the method based on the grey image
have high classification accuracy. In contrast, the former has
better results, with eight out of 10 categories achieving 100%
classification accuracy. Table 9 and Figure 9 give detailed
evidence from three indicators of precision, recall and F1
score. It shows that the Markov image not only has no
preprocessing distortion such as traffic slicing and filling, but
also integrates more feature information such as the timing
relationship between adjacent bytes, so it has stronger representation ability.

images and grey images, respectively. The statistical results of
image file size are shown in Table 10.
It can be seen that compared with the grey image, the
maximum decrease of the Markov image is more than 70%, the
maximum is 98%, and it is always maintained at a low level.
The size of grey image will increase with the increase of traffic,
and the picture specification cannot be naturally unified.
Markov image conversion does not need to slice and fill the
traffic artificially, and the image specifications are naturally
unified (256 � 256), so it has good universality and can be
expressed uniformly across datasets.

5.3.2 | Performance comparison of different
transform domain characterisation methods

5.3.3 | Migration experiments across different
datasets

10,000 Pcap traffic packets of different sizes are randomly
selected from the three datasets and converted into Markov

In order to evaluate the portability of the proposed method,
classification experiments were carried out on the CNN using

456

-

TANG ET AL.

FIGURE 9

Comparison of F1 score of two transform domain methods

T A B L E 10

statistical comparison of Markov image and grey image size

Dataset

Flow size

Markov image size

Grey image size

Maximum decrease

USTC‐TFC2016 (Part I)

1–10 KB

3.37–18.2 KB

2.02–6.48 KB

97.5%

10–100 KB

12.7–18.2 KB

6.48–63 KB

100‐925 KB

6.25–12.7 KB

63‐517 KB

925 KB+

———

———

1–10 KB

4.2–17 KB

2.21–5.97 KB

10‐95 KB

10.8–17 KB

5.97–58.1 KB

95 KB+

———

———

1–10kB

4.83–18.5 KB

1.98–5.06 KB

10–100kB

11.2–18.5 KB

5.06–63 KB

100–1000 KB

5.67–11.2 KB

63‐616 KB

1000 KB+

5.67–11.2 KB

616 KB+

USTC‐TFC2016 (Part II)

ISCXVPN2016

the balanced datasets in Table 4, Table 5 and Table 6. The
average values of precision, recall and F1 score are shown in
Table 11. The data show that the proposed method not only
achieves high scores on three different datasets but also has
very little performance difference between them. It shows that
the transformation domain enhancement and balance method
based on the Markov‐GAN has good generalisation ability for
heterogeneous datasets.

6 | CONCLUSION
The quantity and quality problems of malicious encrypted
traffic datasets result in the low accuracy and weak generalisation ability of the deep learning classification model. In

T A B L E 11
datasets

70.7%

98.1%

Performance of the Markov‐GAN method in different

Dataset

Precision

Recall

F1_Score

USTC‐TFC2016 (part I)

0.996

0.997

0.996

USTC‐TFC2016 (part II)

0.982

0.964

0.972

ISCXVPN2016

0.9933

0.9918

0.9925

order to solve the classification problem under the condition
of imbalanced class distribution, two studies are done in this
paper. On the one hand, a new encrypted traffic representation learning is proposed, that is, the image diversity of low
rank feature space is used to represent the sample diversity of

- 457

TANG ET AL.

high‐dimensional traffic space, which realised the unified
expression across datasets. Experiments show that compared
with grey image and other transform domain methods, the
Markov image has stronger representation ability, lighter
weight and smaller size and is more friendly to the model.
On the other hand, in order to balance the Markov image
dataset, a Markov‐GAN enhancement model is proposed,
which can automatically generate new Markov images with
rich texture, high discrimination and good diversity. Experiments show that compared with other dataset balancing
methods, we obtain higher classification accuracy with less
original sample size by balancing Markov image sets, and all
of them exceed 90%. Moreover, for different datasets and
different depth learning networks, the performance generalisation deviation of the proposed method is greatly reduced.
Compared with other methods that directly enhance the
original traffic samples, such as PacketCGAN and AC‐GAN,
the Markov‐GAN is not only lighter and easier to train but
also has stronger sample amplification ability and generalisation ability.
ACK NOW L ED GE ME N T S
This work was supported in part by the National Key Research
and Development Program under Grant 2018YFB0804503
and Grant 2019QY1400, in part by the National Natural Science Foundation of China under Grant U20A20161 and Grant
U1836103, and in part by the Basic Research Program of China
under Grant 2019‐JCJQ‐ZD‐113.
CON FL I CT OF I NT E R ES T
The authors declare that they have no conflicts of interest.
DATA AVA IL AB I LI T Y STA T E ME N T
Research data are not shared.
P ERMIS SI ON T O R EP ROD U CE M AT E R IA L S
F ROM O TH ER S OU RC ES
None.
O RC ID
Zhangguo Tang

https://orcid.org/0000-0001-6405-8445

RE F ERE N CES
1. Rezaei, S., Liu, X.: Deep learning for encrypted traffic classification: an
overview. IEEE Commun. Mag. 57(5), 76–81 (2019)
2. Cisco, G.S.: ETA – Provides Solution for Detecting Malware in
Encrypted Traffic [EB]. 2018‐01‐14/2021‐07‐16 http://gbhackers.com/
cisco‐eta‐encrypted‐traffic/
3. Cisco, C.: Encrypted Traffic Analytics White paper[R/OL]. (2021‐05)[2021‐
05‐20] https://www.cisco.com/c/en/us/solutions/collateral/enterprise‐
networks/enterprise‐network‐security/nb‐09‐encrytd‐traf‐anlytcs‐wp‐cte‐
en.pdf
4. Security, H.N.: Encryption‐based Threats Grow by 260% in 2020[R/
OL]. (2020‐11‐11)[2021‐06‐19] https://www.helpnetsecurity.com/2020/
11/11/encryption‐based‐threats‐grow‐2020/
5. Magnúsardóttir, A.: Malware Is Moving Heavily to HTTPS [EB].
https://www.cyren.com/blog/articles/over‐one‐third‐of‐malware‐uses‐
https, 2017‐06‐07/2021‐04‐16

6. He, G., et al.: Mobile app identification for encrypted network flows
by traffic correlation. Int. J. Distributed Sens. Netw. 14(12),
1550147718817292 (2018). https://doi.org/10.1177/1550147718817292
7. Meghdouri, F., Zseby, T., Iglesias, F.: Analysis of lightweight feature
vectors for attack detection in network traffic. Appl. Sci. 8(11), 2196
(2018). https://doi.org/10.3390/app8112196
8. Vu, L., Bui, C.T., Nguyen, Q.U.: A deep learning based method for
handling imbalanced problem in network traffic classification. In: Proceedings of the Eighth International Symposium on Information and
Communication Technology, pp. 333–339 (2017)
9. Cheng, H., Xie, J., Chen, L.: CNN‐based encrypted C&C communication
traffic identification method. Comput. Eng. (2019)
10. Lashkari, A.H., et al.: Characterization of encrypted and VPN traffic
using time‐related features. In: The International Conference on Information Systems Security and Privacy. (ICISSP) (2016)
11. Torroledo, I., Camacho, L.D., Bahnsen, A.C.: Hunting malicious TLS
certificates with deep neural networks. In: Proceedings of the 11th
ACM Workshop on Artificial Intelligence and Security, pp. 64–73
(2018)
12. Zeng, Y., et al.: Research on malicious traffic identification technology in
encrypted traffic (in Chinese). J. Xidian Univ. 48(03), 170–187 (2021)
13. Guo, L., et al.: Deep learning‐based real‐time VPN encrypted traffic
identification methods. J. R. Time Image. Process. 17(1), 103–114 (2020)
14. Meng, S., et al.: Classification of encrypted traffic with second‐order
Markov chains and application attribute bigrams. IEEE Trans. Inf. Forensics Secur. 12(8), 1830–1843, https://doi.org/10.1109/tifs.2017.
2692682, (2017)
15. wang, R.H., et al.: An LSTM‐based deep learning approach for classifying
malicious traffic at the packet level. Appl. Sci. 9(16), 3414 (2019). https://
doi.org/10.3390/app9163414
16. Wei, W., et al.: End‐to‐end encrypted traffic classification with one‐
dimensional convolution neural networks. In: IEEE International Conference on Intelligence and Security Informatics. (ISI) (2017)
17. Alan, H.F., Kaur, J.: Can android applications Be identified using only
TCP/IP headers of their launch time traffic? In: Acm Conference on
Security & Privacy in Wireless & Mobile Networks, 61–66 (2016)
18. Iliyasu, A.S., Deng, H.: Semi‐supervised encrypted traffic classification
with deep convolutional generative adversarial networks. IEEE Access.
8, 118–126 (2020). https://doi.org/10.1109/access.2019.2962106
19. Rezaei, S., Liu, X.: How to Achieve High Classification Accuracy with
Just a Few Labels: A Semi‐supervised Approach Using Sampled Packets
(2018)
20. Wang, P., et al.: PacketCGAN: Exploratory Study of Class Imbalance for
Encrypted Traffic Classification Using CGAN (2019)
21. Wei, W., et al.: Malware traffic classification using convolutional neural
network for representation learning. In: International Conference on
Information Networking. (ICOIN) (2017)
22. Korczynski, M., Duda, A.: Markov chain fingerprinting to classify
encrypted traffic. In: IEEE INFOCOM 2014‐IEEE Conference on
Computer Communications, pp. 781–789. IEEE (2014)
23. Wang, Z.X., et al.: FLOWGAN: Unbalanced network encrypted traffic
identification method based on GAN. In: IEEE Intl Conf on Parallel &
Distributed Processing with Applications, Big Data & Cloud Computing,
Sustainable Computing & Communications, Social Computing &
Networking. (ISPA/BDCloud/SocialCom/SustainCom) (2019)
24. Lu, X., et al.: Dynamics Generalization via Information Bottleneck in
Deep Reinforcement Learning. arXiv preprint arXiv:2008.00614 (2020)
25. Lotfollahi, M., et al.: Deep packet: a novel approach for encrypted traffic
classification using deep learning. Soft Comput. (3), 1999–2012 (2017).
https://doi.org/10.1007/s00500‐019‐04030‐2
26. Bazuhair, W., Lee, W.: Detecting malign encrypted network traffic using
Perlin noise and convolutional neural network. In: 2020 10th Annual
Computing and Communication Workshop and Conference. (CCWC)
(2020)
27. Burnap, P., et al.: Malware classification using self organising feature maps
and machine activity data ‐ ScienceDirect. Comput. Secur. 73, 399–410
(2018)

458

-

28. Wang, S., et al.: TrafficAV: an effective and explainable detection
of mobile malware behavior using network traffic. In: IEEE/
ACM 24th International Symposium on Quality of Service (IWQoS)
(2016)
29. Hu, B., et al.: Malicious traffic detection combining features of packet
payload and stream fingerprint (in Chinese). Comput. Eng. 46(11),
163–169 (2020)
30. Anderson, B., Paul, S., Mcgrew, D.: Deciphering malware's use of
TLS (without decryption). J. Comput. Virol. Hacking. Tech. 14(1), 1–17
(2016)
31. Nychis, G., et al.: An empirical evaluation of entropy‐based traffic
anomaly detection. In: Proceedings of the 8th ACM SIGCOMM Conference on Internet Measurement, pp. 151–156 (2008)
32. Fang, J.: Research on malicious TLS traffic identification based on hybrid
neural network. In: 2020 International Conference on Advance in
Ambient Computing and Intelligence. (ICAACI) (2020)
33. Gong, G.L., Yi, J.K., Zhang, Y.C.: Encrypted traffic classification on
length‐ware constrained clustering (in Chinese). J. Chongqing Univ.
Technol. Nat. Sci. 35(5), 9 (2021)
34. Yuan, B., et al.: Byte‐level malware classification based on markov images
and deep learning. Comput. Secur. 92, 101740 (2020). https://doi.org/
10.1016/j.cose.2020.101740
35. Wang, P., Chen, X.: SAE‐based Encrypted Traffic Identification Method.
Computer Engineering (2018)
36. Japkowicz, N.: Learning from imbalanced data sets: a comparison of
various strategies. In: Aaai Workshop on Learning from Imbalanced Data
Sets. 68, 10–15 (2000)
37. Chawla, N.V., et al.: SMOTE: synthetic minority over‐sampling technique.
J. Artif. Intell. Res. 16, 321–357 (2002). https://doi.org/10.1613/jair.953

TANG ET AL.

38. Grolman, E., et al.: Transfer learning for user action identication in
mobile apps via encrypted trafc analysis. IEEE Intell. Syst. (2), 40–53
(2018). https://doi.org/10.1109/mis.2018.111145120
39. Casquilho, J.P.: On the weighted Gini–Simpson index: estimating feasible
weights using the optimal point and discussing a link with possibility
theory. Soft Comput. (22), 1–8 (2020). https://doi.org/10.1007/s00500‐
020‐05011‐6
40. University, C.: The Stratosphere IPS Project Dataset [EB]. https://
stratosphereips.org/category/dataset.html, 2016/2021‐05‐23
41. Simonyan, K., Zisserman, A.: Very Deep Convolutional Networks for
Large‐Scale Image Recognition. Computer Science (2014)
42. Miller, S., Curran, K., Lunney, T.: Multilayer perceptron neural network
for detection of encrypted VPN network traffic. In: International Conference on Cyber Situational Awareness, Data Analytics and Assessment
(Cyber SA), pp. 1–8. IEEE (2018)
43. Soleymanpour, S., Sadr, H., Beheshti, H.: An efficient deep learning
method for encrypted traffic classification on the web. In: 2020 6th International Conference on Web Research (ICWR), pp. 209–216. IEEE
(2020)

How to cite this article: Tang, Z., et al.: Markov‐
GAN: Markov image enhancement method for
malicious encrypted traffic classification. IET Inf. Secur.
16(6), 442–458 (2022). https://doi.org/10.1049/ise2.
12071
PAPER_TEXT
