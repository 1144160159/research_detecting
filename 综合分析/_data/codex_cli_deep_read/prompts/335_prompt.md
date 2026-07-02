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
# [335] A Dual-Discriminator Generative Adversarial Network for Anomaly Detection
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
编号：335
题名：A Dual-Discriminator Generative Adversarial Network for Anomaly Detection
年份：2025
DOI：10.1109/tnnls.2025.3585978
来源：IEEE Transactions on Neural Networks and Learning Systems
PDF：paper/10.1109_TNNLS.2025.3585978.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\335.txt
- 原始字符数：57633
- 本次发送字符数：57633
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

19285

A Dual-Discriminator Generative Adversarial
Network for Anomaly Detection
Da Ding, Youquan Wang , Haicheng Tao, Member, IEEE, Jia Wu , Senior Member, IEEE, and Jie Cao
Abstract—Multivariate time series anomaly detection has
shown potential in various fields, such as finance, aerospace, and
security. The fuzzy definition of data anomalies, the complexity
of data patterns, and the scarcity of abnormal data samples
pose significant challenges to anomaly detection. Researchers
have extensively employed autoencoders (AEs) and generative
adversarial networks (GANs) in studying time series anomaly
detection methods. However, relying on reconstruction error,
the AE-based anomaly detection algorithm needs more effective
regularization methods, rendering it susceptible to the problem of
overfitting. Meanwhile, GAN-based anomaly detection algorithms
require high-quality training data, significantly impacting their
practical deployment. We propose a novel GAN based on a dualdiscriminator structure to address these issues. The model first
processes the data with the generator to obtain the reconstruction
error and then calculates pseudo-labels to divide the data into two
categories. One data category is input into the first discriminator,
where a minor loss between the data and its reconstructed
counterpart is better. The other data category is input into the
second discriminator, where a larger loss between the data and
its reconstructed counterpart is better. Through this process, the
model can effectively constrain the generator, retaining information on normal data during data reconstruction while discarding
information on abnormal data. After conducting experiments on
multiple benchmark datasets, the proposed GAN based on a
dual-discriminator structure achieved good results in anomaly
detection, outperforming several advanced methods. Additionally,
the model also performed well in practical transformer data.
Index Terms—Anomaly detection, dual-discriminator structure, generative adversarial networks (GANs), industrial applications, pseudo-labels.

Received 28 September 2023; revised 14 June 2024, 3 November 2024, 17
March 2025, and 25 May 2025; accepted 26 June 2025. Date of publication
5 September 2025; date of current version 9 October 2025. This work was
supported in part by the Key Research and Development Projects of Jiangsu
Province under Grant BE2020001-1; in part by the Fundamental Research
Projects on Cutting-Edge Leading Technologies in Jiangsu Province under
Grant BK20202011 and Grant BK20192004C; in part by the National Natural
Science Foundation of China (NSFC) under Grant 72172057; in part by
the 2023 Nanjing International/Hong Kong, Macao, and Taiwan Science and
Technology Cooperation Program (Joint Research) under Grant 202308010;
and in part by the Key Scientific Research and Innovation Projects of
Nanjing University of Finance and Economies under Grant XKYC2202303.
(Corresponding author: Jie Cao.)
Da Ding is with the College of Computer Science and Software
Engineering, Hohai University, Nanjing, Jiangsu 211100, China (e-mail:
dingda1996@hhu.edu.cn).
Youquan Wang and Haicheng Tao are with the School of Computer
and Artificial Intelligence, Nanjing University of Finance and Economics, Nanjing, Jiangsu 210023, China (e-mail: youq.wang@gmail.com;
haicheng.tao@gmail.com).
Jia Wu is with the School of Computing, Macquarie University, Sydney,
NSW 2113, Australia (e-mail: jia.wu@mq.edu.au).
Jie Cao is with the School of Management, Hefei University of Technology,
Hefei, Anhui 230009, China (e-mail: cao jie@hfut.edu.cn).
This article has supplementary downloadable material available at
https://doi.org/10.1109/TNNLS.2025.3585978, provided by the authors.
Digital Object Identifier 10.1109/TNNLS.2025.3585978

I. I NTRODUCTION
N RECENT years, the proliferation of the Internet of
Things (IoT) technology has driven the development of
smart grids [1], [2] and intelligent transportation systems [3],
[4]. As shown in Fig. 1, a large amount of system operation
data is collected by deploying sensors and actuators. Accurately and timely identifying abnormal information within
this data is crucial for taking corrective measures, addressing
issues, and minimizing economic losses and human casualties
[5]. Therefore, anomaly detection has emerged as a critical
research area, aiming to precisely and promptly locate anomalous patterns within the collected information. As depicted in
Fig. 2, an anomaly is a deviation from a pattern recognized
by human cognition, resulting in a perceptual change (e.g.,
appearance corruption, style change, blurring, or occlusion) or
a semantic change (e.g., class change or inversion behavior)
to the pattern. Anomalies in time series are usually divided
into point anomalies and collective anomalies; as illustrated
in Fig. 2(a), a point anomaly is a type of anomaly when
the data of a single point exceed the range of normal data
distribution. Collective anomaly, as shown in Fig. 2(b), is
a set of continuous data point sequences as a whole that
is considered anomalous even though individual data points
may not be anomalous. Threshold-based judgment is the most
straightforward approach to anomaly detection, which proves
feasible when applied to individual time series. However,
as the number of collection devices and detection targets
increases, along with the exponential growth in collected data
volume and dimensionality, the interdependencies among the
data become more intricate. Consequently, the threshold-based
method becomes ineffective, necessitating the development
of novel approaches to address this challenge. Hence, this
study proposes an effective method for anomaly detection in
multivariate time series data to address the aforementioned
challenges.
IoT has provided abundant data for the advancement of
deep learning. Concurrently, deep learning has offered numerous methods for detecting anomalies in IoT data [6], [7],
[8]. For instance, clustering algorithms treat data that deviate from cluster centers as anomalies, while classification
algorithms identify data that do not conform to distribution
patterns as anomalies. However, these methods either fail
to find the correlations among time series data or require
additional information about anomalous data, rendering them
unsuitable for high-dimensional data and large-scale series
anomaly detection. Moreover, to handle large amounts of
data, supervised methods necessitate the laborious task of
effectively labeling the data, requiring substantial resources.
Consequently, unsupervised methods have garnered significant

I

2162-237X © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

19286

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

Fig. 1. Comprehensive transformer anomaly detection system.

Fig. 2. Difference between univariate time series and multivariate time
series in anomaly detection. (a) Univariate time series with point anomaly.
(b) Multivariate time series with collective anomalies.

attention in the industry [9], [10], [11]. A commonly used
approach in unsupervised anomaly detection is to map data
into a low-dimensional space and then map the data in the
low-dimensional space back to a high-dimensional space. This
process allows normal data to retain information during the
reconstruction phase while causing anomalous data to lose
information. By employing appropriate reconstruction techniques, precise data reconstruction can be achieved, resulting
in significant reconstruction errors for anomalous data. This
approach enables cost-effective and highly accurate anomaly
detection [12].
Anomaly detection involves the handling of nonlinear
data with complex temporal correlations; thus, deep learning methods are used in this field. Generative adversarial
networks (GANs) have emerged as promising techniques for
unsupervised anomaly detection. The pioneering work of
Goodfellow et al. [13] introduced GANs, which simultaneously train a generator and a discriminator. The generator
aims to encode synthetic data based on the original data, while
the discriminator distinguishes between samples of generated
data and samples of original data. Recent work in anomaly
detection has also explored the use of adversarial training [11],
[14], [15], [16]. The AnoGAN method, proposed by Schlegl
et al. [14], addresses the challenge of unsupervised anomaly
detection. It utilizes deep convolutional learning to capture
the characteristics of normal images and introduces a novel
scoring scheme for mapping them to the latent space. However,
this approach has high computational complexity. Zenati et al.
[17] developed a bidirectional GAN (BiGAN) model, which
showed improved performance in mapping images to the
latent space compared to prior work. We propose a novel
GAN architecture called TadGAN [18] that uses an autoencoder (AE) with an L2 objective function to reconstruct time
series and evaluate errors to identify anomalies. TadGAN is
trained on clean training sets, i.e., sets containing only normal
samples. To address the impact of polluted data, the author
proposes FGANmoraly [10], which filters out possible abnormal sample discriminators with pseudo-labels before training.
However, this approach may lead to false positives and result
in wastage of resources. Motivated by the aforementioned
research contributions, this article presents a more comprehensive approach that effectively learns both the generator and
the discriminator while making optimal use of the available
data and minimizing the impact of contaminated data on the
model.
This article proposes the novel dual-discriminator GAN
(DDGAN) for anomaly detection. The main goal is to train a
generator that can accurately reconstruct data while enlarging
the reconstruction error between abnormal data and reconstructed abnormal data. Our approach involves the following
key components.
1) Given the intrinsic temporal characteristics and intricate
correlations present in multitime series data, we employ

DING et al.: DUAL-DISCRIMINATOR GENERATIVE ADVERSARIAL NETWORK FOR ANOMALY DETECTION

an LSTM-based AE to facilitate the reconstruction of
such data.
2) Considering the specific data requirements of GAN
networks, we propose a dual safeguard mechanism consisting of a filter and a dynamic dictionary, which aims
to mitigate the potential introduction of contaminated
data.
3) To fully exploit the available data, we design two
discriminators: one that receives normal data labeled as
0 and another that receives anomalous data stored in the
dynamic dictionary.
4) We propose a new training loss function that considers
the constraints imposed by the two discriminators on the
AE to achieve more accurate data reconstruction.
The remainder of the article is organized as follows. Section II
presents an overview of related research in the field of anomaly
detection. Section III presents the relevant definitions used in
this article. Section IV provides a more detailed exposition of
the DDGAN model. Section V explains how the model is used
for anomaly detection and presents the experimental results.
Section VI summarizes the principal findings of this article
and proposes potential avenues for future research.
II. R ELATED W ORK
In recent years, the increase in data types, changes in
application scenarios, and diversification of anomaly types
have posed greater demands on anomaly data detection. The
simplest method for anomaly detection involves thresholdbased judgments [19]. However, with the growing complexity
of interdata correlations and the diversification of data types,
this straightforward approach is no longer applicable to the
current complex environment of anomaly data detection. Consequently, researchers have shifted their focus to the study of
unsupervised anomaly detection methods. These methods can
be categorized into one-class classification, nearest neighborbased algorithms, and reconstruction-based methods [20]. This
article provides a detailed investigation and research on these
methods.
Currently, research on anomaly data detection methods
based on one-class classification has been extensively conducted. One-class detection entails learning the discriminative
boundary of normal data, considering any value deviating
from the data boundary as an anomaly. Classical algorithms
include one-class SVM [8], [21] and isolation forest [22].
Ruff et al. [23] introduced a deep support vector method based
on deep learning and one-class classification, where the model
is trained by optimizing the objectives of anomaly detection.
Miao et al. [24] introduced distributed online OCSVM, a
distributed online one-class classification method capable of
detecting anomaly data in distributed data. However, the aforementioned methods exhibit subpar performance when applied
to high-dimensional data.
Nearest neighbor-based algorithms identify objects as
anomaly data by measuring the distances between different
entities, considering objects that are far from other data points
as anomalies. The nearest neighbor-based algorithms can be
further categorized into distance- and density-based methods.
Distance-based methods define the neighbors of an object

19287

using a given radius and determine the anomaly score based
on the number of neighbors [25]. On the other hand, densitybased methods detect anomaly data based on the density of
neighbors surrounding an object. Mahela et al. [26] proposed
a network anomaly detection method based on fuzzy clustering, while Xing et al. [27] presented K-means clustering
and weighted K-nearest neighbor regression-based algorithm
to detect anomaly footprints of transmission line. Parwez
et al. [28] introduced K-means clustering and hierarchical
clustering to analyze anomalous behavior of mobile wireless
networks. However, the implementation of nearest neighborbased methods requires prior knowledge regarding the duration
and quantity of anomalies while also disregarding the temporal
dimension of interrelationships among time series data.
The reconstruction-based methods involve mapping the
original data to high-dimensional or low-dimensional space
using a constructed model and then evaluating data anomalies based on the error between the reconstructed data and
the original data. However, this method may need more
information when mapping abnormal data to low-dimensional
space, leading to inaccurate reconstruction and larger errors.
Principal component analysis (PCA) is a classic algorithm
of this type, but it is limited to linear data and requires
a Gaussian distribution. Several methods such as AE [29],
[30], and variational long short-term memory (VLSTM) [31]
have been proposed to address the above limitation. These
methods lack effective regularization and may suffer from
overfitting, resulting in poor performance [32]. GAN introduces adversarial regularization to alleviate overfitting, but this
approach assumes an uncontaminated training set, and it fails
to effectively model the data distribution when a significant
amount of contaminated data is present in the training set
[13]. To avoid capturing the distribution of anomalous data,
the model employs a filtering mechanism on the discriminator
using pseudo-labels for potential anomalous samples before
training. However, this approach can lead to data waste and
the possibility of mislabeled instances due to the utilization of
pseudo-labels, resulting in suboptimal performance.
III. P RELIMINARIES
Definition 1 (Multivariate Time Series): The dataset
D = {D1 , D2 , . . ., DN } consists of N sequential data
instances, each Di having a fixed length of K, noted as
Di = {xi1 , xi2 , . . ., xiK }. The time intervals between consecutive
data points are uniform, ranging from seconds to hours.
Definition 2 (Reconstruction): Reconstruction involves
mapping the original data D into a low-dimensional space
and then mapping it back into a high-dimensional space. The
original data are denoted as D = {D1 , D2 , . . ., DN }, Di =
{xi1 , xi2 , . . ., xiK }, while the data representation after reconstruction is denoted as D̂ = {D̂1 , D̂2 , . . ., D̂N }, D̂i = { x̂i1 , x̂i2 ,
. . ., x̂iK }.
Definition 3 (Reconstruction Error): The reconstruction
error quantifies the distance between the input data DN and the
reconstructed data D̂N , and it will be mathematically expressed
as
eN = DN − D̂N .

(1)

19288

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

Fig. 3. Data D are passed through an encoder and decoder in the generator to obtain reconstructed data G(D). Based on the reconstruction error E between
D and the reconstructed data G(D), the filter calculates pseudo-labels for the data. The data with a pseudo-label of 0 are fed into the discriminator DN , while
the data with a pseudo-label of 1 undergo further updates in the dynamic dictionary and serve as input for the discriminator DA . The discriminators are
subsequently trained using these refined samples.

Problem Statement: By performing a transformation on
the original data, denoted as D = {D1 , D2 , . . ., DN } and
Di = {xi1 , xi2 , . . ., xiK }, where N represents the sampling time,
anomaly detection assigns a label y ∈ {0, 1} (0 for normal and
1 for abnormal) to each data point at a given sampling time.
Reconstructing the inputted original data as D̂={D̂1 , D̂2 , . . .,
D̂N } and D̂i = { x̂i1 , x̂i2 , . . ., x̂iK }. The anomaly score of the data
is calculated by computing the reconstruction error between
the input data D and the reconstructed data D̂. Based on this
anomaly score, a determination is made regarding whether the
original data is anomalous or not.
IV. M ETHODOLOGY
In this section, more details on the implementation of the
DDGAN will be presented.
A. Overview of the Proposed Model
This section will provide a detailed description of the
DDGAN, which comprises two main parts: training and detection. The architecture of DDGAN is depicted in Fig. 3, and
it consists of a generator, a filter, a dynamic dictionary, and
two discriminators. X and D represent the feature space and
latent vector space, respectively. The generator G first maps
the observations into latent vector space and then reconstructs
them into the feature space
fen : X → D
fde : D → X .

(2)

Specifically, the encoder is an LSTM network, while the
decoder is symmetric to the encoder.

On the other hand, the discriminators, denoted by DA and
DN , are trained based on the original data and reconstructed
data, respectively. The original data are labeled as real, and the
reconstructed data are labeled as fake to train discriminator DA
and discriminator DN . The discrimination mappings fdisA and
fdisD are
fdisA : X → [0, 1]
fdisD : X → [0, 1] .

(3)

The discriminator utilizes a ladder feed-forward network to
accept time series data and produce results. Prior to inputting
the data into the discriminator DN , a pseudo-label filter is
utilized to remove significant abnormal data from the original
and reconstructed data. Additionally, a dynamic dictionary
is employed to store the most conspicuous portion of the
filtered abnormal data, which is subsequently inputted into the
discriminator DA . This process enables effective training of the
generator under the dual constraints of discriminators DA and
DN .
B. Pseudo-Labels
GANs can learn the underlying distribution of training data
and generate samples that follow that distribution. However,
the exclusive training of GAN models on normal data results in
limited diversity in generated samples, as the absence of exposure to abnormal samples during training restricts the model’s
ability to generate diverse samples. Similarly, training GANs
on abnormal data only leads to the generation of abnormal
samples while being ineffective in generating normal samples
due to the lack of training on normal data. Furthermore,

DING et al.: DUAL-DISCRIMINATOR GENERATIVE ADVERSARIAL NETWORK FOR ANOMALY DETECTION

the inclusion of abnormal samples in the training set may
introduce errors in the learned data distribution, leading to
reduced accuracy in data detection.
A method involving the use of pseudo-labeling and dynamic
arrays is proposed to filter and optimize the input to the
discriminator. Pseudo-labeling allows discriminator DN to
receive “pseudo-normal data” as input, while dynamic arrays
enable discriminator DA to receive “pseudo-abnormal data” as
input. By leveraging pseudo-labeling and dynamic arrays, the
vision of training the discriminator on a single type of data is
achieved, overcoming the challenges of obtaining normal or
abnormal samples in practical applications.
Furthermore, a reconstruction method is adopted to calculate
the distance between normal and abnormal data distributions.
This method aims to minimize the error loss between normal
data and reconstructed data while increasing the error loss
between abnormal data and reconstructed data. This approach
allows for the generation of abnormal samples while maintaining the fidelity of normal samples, thus addressing the
limitations of GANs in generating diverse samples from both
normal and abnormal data distributions. The specific process
is presented in Algorithm 1. The original data D = {D1 , D2 ,
. . ., DN }, and Di = {xi1 , xi2 , . . ., xiK } is input into G to obtain
reconstructed data D̂={D̂1 , D̂2 , . . ., D̂N }, D̂i = { x̂i1 , x̂i2 , . . ., x̂iK }.
Based on Equation (1), the error E = {e1 , e2 , . . . , eN } based on
define between the original data D and the reconstructed data
G(D) can be expressed as
ew = Dw − D̂w .

(4)

The mean and variance of E are represented by M(E) and
V(E), respectively, enabling the calculation of the z-score zw
zw =

(ew − M (E))
.
V (E)

(5)

Based on this z-score, the probability of x being anomalous is
designed as
P (Dw ) = σ (zw ) .

(6)

As shown in Equation (6), if the error ew is equal to the mean
M(E) or the z-score zw equals 0, the probability of the data
P(Dw ) being labeled as anomalous is 0.5. If the error ew is
greater than the mean M(E), the probability of the data P(Dw )
being labeled as anomalous is greater than 0.5. Conversely, if
the error ew is smaller than the mean M(E), the probability of
the data P(Dw ) being labeled as anomalous is smaller than
0.5. This approach provides a robust method for detecting
anomalous data.
During the initial training phase, the model may need to
acquire more information to represent the latent information
of the data accurately. Therefore, the same parameters are
set for all data in the initial stage. In the subsequent phase,
an impact factor θ is introduced to influence the anomaly
probability; the factor θ should be consistent for all data under
the initial conditions, showing more influence with the increase
of training. Therefore, the factor θ is defined as
θ =1−

1
S epoch

(7)

19289

where S epoch is the function about the current iteration and
satisfies the following:
(
1, if n = 1
S epoch =
(8)
∞, if n → ∞.
Combining Equation (6) and Equation (8), we can get the
following:
P (xw ) = σ (zw ∗ θ)



(ew − M (E))
1
.
=σ
∗ 1−
V (E)
S epoch

(9)

C. Dynamic Dictionary and Data Augmentation
By constraining z-score zw with the impact factor, the
anomaly probability of the data can change with the iterations.
At initialization, all data are assigned the same anomaly
probability. As the training progresses, data are assigned
different anomaly probabilities, resulting in different anomaly
labels. Data labeled 0 are marked as “pseudo-normal data,”
while data labeled 1 are marked as “pseudo-anomalous data.”
The “pseudo-normal data” and “pseudo-anomalous data” are
expressed as
n
o
Dd0 = Dd10 , Dd20 , . . . , Ddt 0
˚
Ddt 0 = xd10t , xd20t , . . . , xdK0t
n
o
Dd1 = Dd11 , Dd21 , . . . , Ddk 1
˚
Ddk 1 = xd11k , xd21k , . . . , xdK1k
w = t + k.

(10)

During this phase, assigning pseudo-labels to the data can
achieve the classification of normal and abnormal data. While
“pseudo-normal data” are normal data as much as possible, it
cannot be guaranteed that “pseudo-abnormal data” are necessarily abnormal data. This can lead to disastrous consequences
for the discriminator DA , which is specifically trained to detect
abnormal data; it is necessary to reextract the abnormal data
from the discriminator DA . Here, a dynamic dictionary Dd
is introduced. As mentioned earlier, the error ew is greater
than the mean M(E), and the probability of the data P(xw )
being labeled as anomalous is greater than 0.5. Therefore,
the dynamic dictionary is sorted based on the reconstruction
error, and data with the top L largest errors are considered as
real abnormal data and used for training the discriminator DA .
Then, the dynamic dictionary Dd can be obtained as follows:
˚
Dd = Dd1 , Dd2 , . . . , DdL .
(11)
This forces the discriminator DA to learn to distinguish real
abnormal data, thereby improving its ability to recognize
abnormal data.
During each iteration, the discriminator DA is updated
using L real anomalous data from the dynamic dictionary and
reconstructed anomalous data
n
o
Dd = TOPL Dd1 , Dd2 , . . . , DdL , Dd11k , Dd21k , . . . , Ddk 1k
˚
= Dd1 , Dd2 , . . . , DdL .
(12)
Through this iterative process, the generator G and the discriminator DA engage in a game of optimization, continually

19290

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

between normal and reconstructed data and increasing the
distance between anomaly and reconstructed data. To achieve
this goal, we employ different loss functions for DA and
DN . For discriminator DN , which takes normal data and their
corresponding reconstructions as inputs, we design its loss
function to gradually reduce the distance between normal and
reconstructed data via backpropagation after each iteration of
training


LN = BCEloss Dd0 + BCEloss G Dd0
t
 

i
1 Xh
li log Ddi 0 + (1 − li ) log 1 − Ddi 0
=−
t
i=1

Fig. 4. Data augmentation model. Data stored in the dynamic dictionary (left)
ed after data augmentation (right).
and D

improving their performance and achieving the recognition and
generation of anomalous data. Eventually, at the end of the
training, the generator G will be able to encode anomalous
data, and the discriminator DA will accurately identify anomalous data and save it in the dynamic dictionary for use in the
next training cycle.
Data augmentation can increase the quantity and quality
of data in situations where data is scarce. This article adopts
a random mask data augmentation method that follows a
geometric distribution, as shown in Fig. 4, where black represents the masked state denoted by 0 and color represents the
unmasked state denoted by 1. Given the mask ratio r and mask
length lm , p st :st+1 represents the noise transition probability
from time t to t + 1, and the complete transition matrix can
be expressed as


p0:0 p0:1
P=
p1:0 p1:1
3
2
1
r
1
·
1−
6
lm 1 − r 7 .
(13)
= 4 1 lm
1
r 5
1−
·
lm
lm 1 − r
Positive sample pairs are obtained by randomly applying
two independent masking operations to each dimension. M is a
binary noise mask matrix that follows a geometric distribution:
ed = Dd ⊗ M
D

(14)

ed represents the transformed multidimensional time
where D
series after data augmentation
 
ed · D
ed+ /$
exp cos D
(15)
Lcon = − log PS
 
ed edi /$
i=0 exp cos D · D
ed+ denotes the positive pairs and S represents the
where D
total number of samples.
D. Dual-Discriminator
In this section, we propose novel designs for the discriminators DA and DN with the aim of reducing the distance

t
  

 i
1 Xh
li log G Ddi 0 +(1 − li ) log 1−G Ddi 0
.
−
t
i=1
(16)

However, the original data are marked as real, and the reconstructed data are marked as fake; then, the original data are
labeled as 1 and the reconstructed data are labeled as 0. The
loss of discriminator DN can be defined as


LN = BCEloss Dd0 + BCEloss G Dd0
t

 i
1 X h  d0 
log Di + log 1 − G Ddi 0
.
(17)
=−
t
i=1

For discriminator DA , which takes anomaly data Dd and their
corresponding reconstructions as inputs, we design its loss
function to further increase the distance between anomaly and
reconstructed data after each iteration of training


ed − BCEloss G D
ed
LA = BCEloss D
t


1 X
edi + (1 − li ) log 1 − D
edi
=−
li log D
L
i=1
t



1 X
edi + (1 − li ) log 1 − G D
edi
li log G D
.
+
L
i=1
(18)
Similar to discriminator DN , the original data are labeled as
1 and the reconstructed data are labeled as 0; the loss of
discriminator DA can be expressed as


ed + BCEloss D
ed
LA = BCEloss D
t

=−



1 X
edi − log 1 − G D
edi
log D
.
L

(19)

i=1

Through the training of discriminators DA and DN , we are
able to simultaneously reduce the distance between normal and
reconstructed data and increase the distance between anomaly
and reconstructed data.
E. Adaptive Weighted
This section proposes a novel training function based on
reconstruction error for anomaly detection, which requires
precise reconstruction of data to retain normal information
while discarding anomaly information, to reduce the distance
between normal and reconstructed data, and to expand the
distance between anomaly and reconstructed data. To achieve

DING et al.: DUAL-DISCRIMINATOR GENERATIVE ADVERSARIAL NETWORK FOR ANOMALY DETECTION

this, we redesign the training function to differentiate the
contributions of normal and anomaly data to the loss function.
The function is formulated as
t


1 X d0
Di − D̂di 0 ∗ 1 − ydi 0
Lre =
w
−

i=1
k
X

∗



1 − ydi 1

1
w

t
X

!
Ddi 0 − D̂di 0

(20)

i=1

where w is the total amount of all data and yi is the true
label of Di , meaning that only true data will contribute to
the reconstruction loss. However, in an unsupervised learning
scenario, labels are unavailable, and it is impossible to separate
normal samples from abnormal ones. To solve this problem, we propose a new reconstruction objective specifically
designed for the anomaly detection task
e−zi
δi = Pw −z
a
a=1 e

(21)

where the reconstruction error is larger than the average, and
the data will receive smaller weights; the reconstruction error
is smaller than the average, and the data will receive larger
weights. Smaller reconstruction errors correspond to larger
weights, and larger reconstruction errors correspond to smaller
weights. We also introduce a balancing factor, with the final
weight being

Pw
e−zi
1 a=1 e−za + S epoch − 1 · e−zi
δi = Pw −z ·
(22)
a
N
S epoch · e−zi
a=1 e
where N is a normalization factor. At the initial State, the
weights and the contribution to the loss function are equal.
As the epoch increases, the weights will gradually approach
Equation (21). Ultimately, Equation (20) is approximated by
Lre =

w
X

Di − D̂i · δi .

(23)

i=1

The reconstruction loss function of Equation (23) allows
DDGAN to focus more on fitting the data.
F. Model Training
Given a training dataset T = {x1 , x2 , x3 , . . . , xT }, this article
proposes an alternate training approach for a generator and two
discriminators, DA and DN , where the training loss functions
for discriminators DA and DN are defined in Equation (19) and
Equation (17), respectively. Unlike traditional GANs, where
only an adversarial loss function is used to train the Generator,
this article utilizes both discriminators DA and DN and obtains
their respective adversarial loss functions. By combining these
two adversarial loss functions, a double discriminator-based
adversarial loss function is derived, as shown in the following:
LaDN = −

(24)

i=1

Lad = LaDN + LaDA
" T
#
T
X
1 X
=−
log DN [G (xi )] −
log DA [G (xi )] . (25)
T
i=1



i=1

=

T

1X
LaDA =
log DA [G (xi )]
T

i=1

Ddi 1 − D̂di 1

19291

Algorithm 1 Pseudo-Label Generation Algorithm
Require: Sequence data D = {D1 , D2 , . . . , DN }
Ensure: Pseudo-labels l = {l1 , l2 , . . . , lN }
1: D ← G(D) .Apply graph-based model G(·) for representation or reconstruction
2: Compute error ei for each Di using 4
3: for each sample Di do
4:
Compute probability P(Di ) using 9
5:
Sample η ∼ Uniform(0, 1)
6:
if η > P(Di ) then
7:
Set pseudo-label li ← 0
8:
else
9:
Set pseudo-label li ← 1
10:
end if
11: end for
12: return l
Algorithm 2 Adversarial Training Algorithm
Require: Fragmented training data T = {x1 , x2 , . . . , xT }, test
data X = {(x1t , . . . , xit )}, max epochs P, adversarial loss
rate ν
Ensure: Trained Generator G, Discriminators DA , DN
1: Initialize weights of G, DA , and DN
2: for each epoch from 1 to P do
3:
for each fragment index κ from 1 to n do
4:
DN receives Dd0 from Equation 10
5:
Compute loss LN via Equation 17
6:
Update DN using LN
7:
DA receives Dd from Equation 12
8:
Compute loss LA via Equation 19
9:
Update DA using LA
10:
end for
11:
Compute Lcon via Equation 15
12:
Compute Lre via Equation 23
13:
Compute Ldgan via Equation 26
14:
Update Generator G with combined loss
15: end for
16: for each test fragment xit in X do
17:
Generate reconstruction: x̂it = G(xit )
18:
Computepreconstruction score:
19:
score = (xit − x̂it )2
20: end for

T

However, the double discriminator-based adversarial loss
function ignores the temporal correlation of time series data.
Therefore, this article combines Equation (23) and Equation
(25) to obtain the generator’s loss function, as shown in the
following:

i=1

Ldgan = Lre + ϑ · Lad + ςLcon

1X
log DN [G (xi )]
T

(26)

19292

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

TABLE I
DATASETS

TABLE II
AVERAGE P RECISION , R ECALL , F1-S CORE , AND AUC OF D IFFERENT
M ETHODS ON S IX P UBLIC DATASETS

where ϑ is used to adjust the weight of Lad and ς is used to
adjust the weight with Lcon . The specific training process is
presented in Algorithm 2.

R measures the proportion of true positive samples among
all positive samples, and it is calculated as
TP
(28)
TP + FN
where FN is the number of false negatives.
F1 is the harmonic mean of P and R, and it is calculated
as
P∗R
F1 = 2 ∗
.
(29)
P+R
R=

V. E XPERIMENTAL R ESULTS
This section conducts extensive experiments to evaluate
the effectiveness of DDGAN, with additional experimental
results and analyses provided in the Appendixes (see the
Supplementary Material).
A. Experimental Setup

B. Tasking Setting

1) Public Datasets and Baselines: We evaluate our method
on six public datasets: MSL [33] (NASA’s Mars rover mission
data), SMAP [34] (soil moisture satellite data), SMD [35]
(server performance metrics), SWaT [36] (water treatment
ICS data), WADI [37] (water distribution network simulation),
and PSM [38] (eBay’s server metrics). Details of the dataset
information are shown in Table I. These datasets cover diverse
domains, including space exploration, environmental monitoring, industrial systems, and cloud computing, providing
comprehensive benchmarks for anomaly detection.
For comparison, we select seven state-of-the-art unsupervised anomaly detection methods: USAD [39] (adversarial AEs), OmniAnomaly [35] (stochastic RNN), TranAD
[40] (transformer-based), GDN [41] (graph neural network), BeatGAN [9] (beat-aware GAN), FGANomaly [10]
(pseudo-label enhanced GANomaly), and Anomaly Transformer [42] (self-attention based). These baselines represent
major technical directions in time series anomaly detection,
including reconstruction-based, GAN-based, and attentionbased approaches.
2) Evaluation Metrics: We adopt precision (P), recall (R),
F1-score (F1), and the area under the precision–recall curve
(AUC) to evaluate the performance. These metrics are defined
as follows: P measures the proportion of true positive samples
among all samples, and it is calculated as

In experiments, the sliding window width is uniformly set
to 150. The model is trained using the Adam optimizer with a
learning rate of 1e−4 . The RNN encoder has an RNN hidden
dim of 50, and the decoder consists of multiple linear layers
with a hidden dim of 50. The hyperparameter is set to 0.5. The
training was conducted in a Windows environment equipped
with a 2.50-GHz 12th Gen Intel1 Core2 i5-12400F CPU and an
8-GB NVIDIA GeForce RTX 3060 GPU. The training dataset
is divided into a training set and a validation set in a 7:3 ratio to
obtain the optimal model and avoid overfitting or underfitting.
As the model is considered an unsupervised learning model,
it cannot directly adjust hyperparameters based on the F1score on the validation set as in supervised learning. To avoid
reliance on predetermined thresholds, we can search for all
possible thresholds to determine the normality and abnormality of observed values and select the optimal F1-score as
the performance metric for model evaluation. We obtain the
anomaly scores in the test set and evaluate them individually
as thresholds. Finally, the threshold yielding the best F1-score
is selected as the final result. Then, we conducted multiple
experiments based on the final selected model and used the
mean and variance of the multiple experiments as the final
results of the model.

TP
P=
TP + FP

We conducted an extensive evaluation of DDGAN in six
datasets, comparing its performance with multiple baseline

(27)

where TP is the number of true positives and FP is the number
of false positives.

C. Overview Performance

1 Registered trademark.
2 Trademarked.

DING et al.: DUAL-DISCRIMINATOR GENERATIVE ADVERSARIAL NETWORK FOR ANOMALY DETECTION

19293

TABLE III
P ERFORMANCE OF E IGHT U NSUPERVISED A NOMALY D ETECTION M ETHODS C OMPARED TO DDGAN ACROSS S IX P UBLIC DATASETS . I T S HOWS
P RECISION , R ECALL , F1-S CORE , AND AUC FOR E ACH M ETHOD , W ITH THE B EST R ESULTS H IGHLIGHTED IN B OLD

TABLE IV
P RECISION , R ECALL , AND F1-S CORES P ERFORMANCE OF LSTM-AE, LSTM-DN , LSTM-DA , DD GAN, D D GAN, AND DDGAN IN F OUR P UBLIC
DATASETS

methods. As shown in Table II, DDGAN significantly outperformed eight other unsupervised anomaly detection methods
across these six public datasets, demonstrating its exceptional performance in unsupervised anomaly detection tasks.
Table III also provides a detailed comparison of DDGAN and
other baseline models on public datasets. In the MSL dataset,
our method achieved an AUC score of 91.92%, surpassing all
baselines by an improvement of 2.46%. Although the F1-score
was not the highest, it still exhibited suboptimal performance.
In the PSM dataset, DDGAN excelled in accuracy, F1, and
AUC metrics, with an impressive increase of 2.03% in the
F1-score over the baseline, achieving an AUC of 98.88%, a
6% improvement. Despite a slightly lower recall compared
to USAD, our recall rate remained high at 98.51%. On the
SWAT dataset, DDGAN achieved the best results across recall,
F1-score, and AUC, with a recall improvement of 3.04%
over the baseline. For the WADI dataset, our method also

demonstrated outstanding performance in recall, F1-score,
and AUC, successfully achieving a perfect recall rate and
a 7.31% increase in F1-score compared to baseline. In the
SMD dataset, DDGAN exhibited excellent performance across
all evaluation metrics, achieving an accuracy of 99.96%,
a recall rate of 100.00%, an F1-score of 99.97%, and an
AUC of 99.97%, highlighting its significant advantages over
other methods. However, in the SMAP dataset, our method
performed poorly. This was primarily due to the emphasis
on temporal relationships while failing to adequately consider
intersensor correlations, which resulted in unsatisfactory accuracy and recall rates. Nonetheless, the AUC metric still reached
optimal levels, while the F1-score achieved suboptimal results.
In summary, our method demonstrated superior performance
across most datasets, outperforming several baseline methods
across various evaluation metrics, underscoring the practicality and effectiveness of unsupervised anomaly detection

19294

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

tasks. It is crucial to note that the pseudo-label generation
in this study relies on a reconstruction error-based dynamic
dictionary screening mechanism, theoretically grounded in the
core hypothesis that “normal samples exhibit significantly
lower reconstruction errors than anomalies.” However, this
mechanism shows high sensitivity to data distributions: in scenarios with severe class imbalance, fixed-capacity dictionaries
easily lead to insufficient representation of normal samples,
thereby generating pseudo-label noise. Additionally, the mean
squared error (mse) used for reconstruction error calculation
has inherent limitations, resulting in inadequate sensitivity to
localized subtle anomalies.
Fig. 5. Mean values achieved by different methods under various parameter
configurations.

D. Ablation Study
DDGAN demonstrates significant improvements over most
baseline models. This section presents ablation experiments
designed to validate the effectiveness of various modules,
structures, and methods within the algorithm. Specifically,
we compared DDGAN with five other models: LSTM-AE,
LSTM-DN , LSTM-DA , and ddGAN. LSTM-AE represents a
conventional LSTM-based AE, while LSTM-DN integrates a
discriminator trained on normal data into the LSTM-based AE
and LSTM-DA employs a discriminator trained on anomalous
data. The ddGAN model combines an LSTM-based AE trained
exclusively on anomalous data but excludes the dynamic
dictionary. The distinction between DdGAN and DDGAN lies
in the absence of data augmentation in the dynamic dictionary
component. The ablation experiments were conducted on four
public datasets: MSL, SMAP, SWaT, and SMD. Table IV
presents the results of the ablation experiments. It is evident
that DDGAN outperforms LSTM-AE, LSTM-DN , LSTM-DA ,
ddGAN, and DdGAN across the four public datasets, particularly excelling in recall and F1-score, indicating that DDGAN
possesses stronger generalization capabilities in unsupervised
anomaly detection tasks. Furthermore, the results in Table IV
indicate that both single-discriminator (handling normal or
anomalous data) and dual-discriminator architectures contribute to enhancing anomaly detection performance. Notably,
the discriminators for normal and anomalous data show significant improvements across all datasets when compared
to the traditional LSTM-AE, highlighting the effectiveness
of integrating LSTM-AE with GANs for anomaly detection
tasks. The results from ddGAN and DdGAN demonstrate
the benefits of incorporating a dynamic dictionary for storing
anomalous data to train the anomaly discriminator. DDGAN’s
inclusion of data augmentation within the dynamic dictionary addresses the challenge of anomalous data scarcity,
and the results suggest that this approach is effective in
improving model performance. The aforementioned ablation
experiments reveal that the combination of the normal data
discriminator and the anomalous data discriminator, along
with components such as the dynamic dictionary and data
augmentation, enhances anomaly detection performance. The
dynamic dictionary serves as an auxiliary component for
storing limited anomalous data, playing a crucial role during
the training process. Meanwhile, the data augmentation component alleviates the issue of data imbalance by enhancing the

anomalous data, thereby addressing the scarcity of such data.
Overall, the ablation study results indicate that improvements
to the model from different perspectives effectively enhance
anomaly detection capabilities and performance, and these
enhancements are not mutually exclusive.
E. Parameter Sensitivity
This section investigates the impact of selecting different
S epoch strategies on the performance of the model. We explore
the choices of S epoch from a set of [log, N, n log, n2 ]. We
examine various S epoch strategies and present their effects on
the model’s mean values in Fig. 5. It is observed that, in
most cases, employing n2 strategies leads to improved performance. All four strategies exhibit a monotonically increasing
trend, albeit with varying rates of increase as the number of
epochs progresses. Strategy n2 notably demonstrates the highest increase in both optimal and mean values. These findings
underscore the appropriateness of the research approach based
on reconstruction error. By adopting strategy n2 for anomaly
detection, the model effectively accentuates the discrepancy
between abnormal and reconstructed data, thereby yielding
a substantial enhancement in the effectiveness of anomaly
detection through reconstruction error analysis.
VI. C ONCLUSION
This study addresses the data dependency and overfitting
challenges of GANs in multivariate time series anomaly
detection by proposing a dynamic dictionary-based GAN
(DDGAN) framework. The methodological innovation lies in
the synergistic integration of a pseudo-label filtering mechanism and a dynamic dictionary optimization strategy, which
collaboratively establishes a representation system for normal
and abnormal samples. Specifically, the dynamic dictionary
enables adaptive storage of anomalous samples based on
reconstruction error thresholds, while the pseudo-label mechanism iteratively refines the screening accuracy of normal data.
Notably, the method may encounter challenges in scenarios
with class imbalance due to dictionary capacity constraints that
could compromise normal pattern characterization. Compared
to existing approaches, the core breakthroughs include the
dual-discriminator architecture design and the joint optimization mechanism of dynamic weight loss functions, which

DING et al.: DUAL-DISCRIMINATOR GENERATIVE ADVERSARIAL NETWORK FOR ANOMALY DETECTION

collectively enhance both normal data reconstruction fidelity
and anomaly discrimination capability. Future research will
prioritize addressing technical bottlenecks in multimodal feature fusion and fine-grained anomaly classification while
exploring adaptive dictionary capacity adjustment strategies to
improve model robustness.
R EFERENCES
[1]

D. Yue, Z. He, and C. Dou, “Cloud-edge collaboration-based distribution
network reconfiguration for voltage preventive control,” IEEE Trans.
Ind. Informat., vol. 19, no. 12, pp. 11542–11552, Dec. 2023.
[2] K. Huang, S. Wu, B. Sun, C. Yang, and W. Gui, “Metric learningbased fault diagnosis and anomaly detection for industrial data with
intraclass variance,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35,
no. 1, pp. 547–558, Jan. 2024.
[3] R. W. Liu, Y. Guo, Y. Lu, K. T. Chui, and B. B. Gupta, “Deep networkenabled haze visibility enhancement for visual IoT-driven intelligent
transportation systems,” IEEE Trans. Ind. Informat., vol. 19, no. 2,
pp. 1581–1591, Feb. 2023.
[4] T. Truong-Huu et al., “An empirical study on unsupervised network
anomaly detection using generative adversarial networks,” in Proc. 1st
ACM Workshop Security Privacy Artif. Intell., 2020, pp. 20–29.
[5] A. Mahmoud and A. Mohammed, “A survey on deep learning for
time-series forecasting,” in Machine Learning and Big Data Analytics
Paradigms: Analysis, Applications and Challenges, 2020, pp. 365–392.
[6] Z. Zhang et al., “Time series anomaly detection for smart grids via
multiple self-supervised tasks learning,” in Proc. IEEE Int. Conf. Knowl.
Graph (ICKG), Nov. 2022, pp. 392–397.
[7] H. Tao et al., “HAN-CAD: Hierarchical attention network for context
anomaly detection in multivariate time series,” World Wide Web, vol. 26,
no. 5, pp. 2785–2800, Sep. 2023.
[8] P. Wu, J. Liu, and F. Shen, “A deep one-class neural network for
anomalous event detection in complex scenes,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 31, no. 7, pp. 2609–2622, Jul. 2020.
[9] B. Zhou, S. Liu, B. Hooi, X. Cheng, and J. Ye, “BeatGAN: Anomalous
rhythm detection using adversarially generated time series,” in Proc.
28th Int. Joint Conf. Artif. Intell., Aug. 2019, pp. 4433–4439.
[10] B. Du, X. Sun, J. Ye, K. Cheng, J. Wang, and L. Sun, “GAN-based
anomaly detection for multivariate time series using polluted training
set,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12208–12219,
Dec. 2023.
[11] A. Garg, W. Zhang, J. Samaran, R. Savitha, and C.-S. Foo, “An evaluation of anomaly detection and diagnosis in multivariate time series,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2508–2517,
Jun. 2022.
[12] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A
survey,” ACM Comput. Surveys (CSUR), vol. 41, no. 3, p. 15, 2009.
[13] I. J. Goodfellow et al., “Generative adversarial nets,” in Proc. 27th Int.
Conf. Neural Inf. Process. Syst. (NIPS), vol. 2. Cambridge, MA, USA:
MIT Press, 2014, pp. 2672–2680.
[14] T. Schlegl, P. Seeböck, S. M. Waldstein, U. Schmidt-Erfurth, and
G. Langs, “Unsupervised anomaly detection with generative adversarial
networks to guide marker discovery,” in Proc. Int. Conf. Inf. Process.
Med. Imag., 2017, pp. 146–157.
[15] Y. Wang, J. Cao, Z. Bu, J. Wu, and Y. Wang, “Dual structural consistency
preserving community detection on social networks,” IEEE Trans.
Knowl. Data Eng., vol. 35, no. 11, pp. 11301–11315, Nov. 2023.
[16] Y. Wang, J. Cao, Z. Bu, and M. Leng, “Temporal dual-attributed network
generation oriented community detection model,” IEEE Trans. Emerg.
Topics Comput., vol. 12, no. 2, pp. 403–418, Apr. 2024.
[17] H. Zenati, C.-S. Foo, B. Lecouat, G. Manek, and V. Chandrasekhar,
“Efficient GAN-based anomaly detection,” in Proc. 35th Int. Conf.
Mach. Learn., 2018, pp. 6094–6103.
[18] A. Geiger, D. Liu, S. Alnegheimish, A. Cuesta-Infante, and K. Veeramachaneni, “TadGAN: Time series anomaly detection using generative
adversarial networks,” in Proc. IEEE Int. Conf. Big Data (Big Data),
Dec. 2020, pp. 33–43.
[19] D. M. Hawkins, Identification of Outliers. London, U.K.: Chapman &
Hall, 1980.
[20] C. Zhou and R. C. Paffenroth, “Anomaly detection with robust deep
autoencoders,” in Proc. 23rd ACM SIGKDD Int. Conf. Knowl. Discovery
Data Mining, Aug. 2017, pp. 665–674.

19295

[21] C. Cortes and V. Vapnik, “Support-vector networks,” Mach. Learn.,
vol. 20, no. 3, pp. 273–297, 1995.
[22] F. T. Liu, K. M. Ting, and Z. Zhou, “Isolation forest,” Data mining,
vol. 15, no. 4, pp. 413–422, 2008.
[23] L. Ruff et al., “Deep one-class classification,” in Proc. Int. Conf. Mach.
Learn., 2018, pp. 4393–4402.
[24] X. Miao, Y. Liu, H. Zhao, and C. Li, “Distributed online
one-class support vector machine for anomaly detection over
networks,” IEEE Trans. Cybern., vol. 49, no. 4, pp. 1475–1488
, Apr. 2019.
[25] S. Ramaswamy, R. Rastogi, and K. Shim, “Efficient algorithms for
mining outliers from large data sets,” in Proc. ACM SIGMOD Int. Conf.
Manage. Data, May 2000, pp. 427–438.
[26] O. P. Mahela, B. Khan, H. H. Alhelou, and P. Siano, “Power
quality assessment and event detection in distribution network
with wind energy penetration using stockwell transform and fuzzy
clustering,” IEEE Trans. Ind. Informat., vol. 16, no. 11, pp. 6922–6932,
Nov. 2020.
[27] K. Xing, C. Hu, J. Yu, X. Cheng, and F. Zhang, “Mutual
privacy preserving k -Means clustering in social participatory
sensing,” IEEE Trans. Ind. Informat., vol. 13, no. 4, pp. 2066–2076,
Aug. 2017.
[28] M. S. Parwez, D. B. Rawat, and M. Garuba, “Big data analytics for
user-activity analysis and user-anomaly detection in mobile wireless
network,” IEEE Trans. Ind. Informat., vol. 13, no. 4, pp. 2058–2065,
Aug. 2017.
[29] X. Tao, D. Zhang, W. Ma, Z. Hou, Z. Lu, and C. Adak,
“Unsupervised anomaly detection for surface defects with dual-siamese
network,” IEEE Trans. Ind. Informat., vol. 18, no. 11, pp. 7707–7717
, Nov. 2022.
[30] G. Zhu et al., “A multi-task graph neural network with variational graph
auto-encoders for session-based travel packages recommendation,” ACM
Trans. Web, vol. 17, no. 3, pp. 1–30, Aug. 2023.
[31] X. Zhou, Y. Hu, W. Liang, J. Ma, and Q. Jin, “Variational LSTM
enhanced anomaly detection for industrial big data,” IEEE Trans. Ind.
Informat., vol. 17, no. 5, pp. 3469–3477, May 2021.
[32] N. Srivastava, G. E. Hinton, A. Krizhevsky, I. Sutskever, and
R. Salakhutdinov, “Dropout: A simple way to prevent neural networks
from overfitting,” J. Mach. Learn. Res., vol. 15, no. 1, pp. 1929–1958,
2014.
[33] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric
dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discovery Data Mining, Jul. 2018, pp. 387–395.
[34] T. Nakamura, M. Imamura, R. Mercer, and E. Keogh, “MERLIN:
Parameter-free discovery of arbitrary length anomalies in massive time
series archives,” in Proc. IEEE Int. Conf. Data Mining (ICDM), Nov.
2020, pp. 1190–1195.
[35] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Disc. Data
Min., 2019, pp. 2828–2837.
[36] A. P. Mathur and N. O. Tippenhauer, “SWaT: A water treatment
testbed for research and training on ICS security,” in Proc. Int. Workshop Cyber-physical Syst. Smart Water Netw. (CySWater), Apr. 2016
, pp. 31–36.
[37] C. M. Ahmed, V. R. Palleti, and A. P. Mathur, “WADI: A water
distribution testbed for research in the design of secure cyber physical
systems,” in Proc. 3rd Int. Workshop Cyber-Phys. Syst. Smart Water
Netw., Apr. 2017, pp. 25–28.
[38] A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to asynchronous multivariate time series anomaly detection and localization,”
in Proc. 27th ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug.
2021, pp. 2485–2494.
[39] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Disc. Data Min., 2020,
pp. 3395–3404.
[40] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” 2022,
arXiv:2201.07284.
[41] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell. (AAAI),
May 2021, pp. 4027–4035.

19296

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

[42] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer:
Time series anomaly detection with association discrepancy,” 2021,
arXiv:2110.02642.

Da Ding is currently pursuing the Ph.D. degree with
the College of Computer and Information, Hohai
University, Nanjing, China.
His current research interests include anomaly
detection and time series analysis.

Youquan Wang received the Ph.D. degree in
computer application technology from Nanjing University of Science and Technology, Nanjing, China.
He is currently a Lecturer at Jiangsu Provincial
Key Laboratory of E-Business, Nanjing University
of Finance and Economics. His research interests
include deep learning and data mining. He has
authored or co-authored more than 30 refereed journal articles and conference papers in these areas.
Dr. Wang is a member of ACM and CCF.

Haicheng Tao (Member, IEEE) received the Ph.D.
degree in computer science from Nanjing University
of Science and Technology, Nanjing, China.
He is currently a Lecturer with Nanjing University
of Finance and Economics, Nanjing. His research
interests include data mining, machine learning, artificial intelligence, and optimization.

Jia Wu (Senior Member, IEEE) received the Ph.D.
degree in computer science from the University of
Technology Sydney, Ultimo, NSW, Australia.
He is currently an Associate Professor and the
Research Director at the Centre for Applied Artificial Intelligence and the Director of Higher Degree
Research (HDR) at the School of Computing, Macquarie University, Sydney, NSW, Australia. He has
authored or co-authored more than 200 refereed
journal articles and conference papers, including
IEEE T RANSACTIONS ON PATTERN A NALYSIS
AND M ACHINE I NTELLIGENCE (TPAMI), IEEE T RANSACTIONS ON
K NOWLEDGE AND DATA E NGINEERING (TKDE), IEEE T RANSACTIONS
ON C YBERNETICS (TCYB), ACM Transactions on Knowledge Discovery
from Data (TKDD), IEEE T RANSACTIONS ON N EURAL N ETWORKS AND
L EARNING S YSTEMS (TNNLS), IEEE T RANSACTIONS ON M ULTIMEDIA
(TMM), KDD, ICDM, WWW, and NeurIPS. His current research interests
include data mining and machine learning.
Prof. Wu has been serving as the Program Committee Chair/the Demo
Chair/the Contest Chair/the Tutorial Chair/the Publicity Chair/the Program
Committee Chair (Senior) for Prestigious Data Mining and Artificial Intelligence Conferences over ten years, such as KDD, ICDM, WSDM, IJCAI,
AAAI, WWW, NeurIPS, CIKM, and SDM. His research team was a recipient
of the CIKM’22 Best Paper Runner-Up Award, the ICDM’21 Best Student
Paper Award, the SDM’18 Best Paper Award in Data Science Track, the
IJCNN’17 Best Student Paper Award, and the ICDM’14 Best Paper Candidate
Award. He is an Associate Editor of IEEE TNNLS, ACM TKDD, and Neural
Networks.

Jie Cao received the Ph.D. degree in information
science and engineering from Southeast University,
Nanjing, China, in 2002.
He is currently a Professor with the School
of Management, Hefei University of Technology,
Hefei. His main research interests include data mining, deep learning, and business intelligence.
Dr. Cao has been selected in the Program for
New Century Excellent Talents in University and
awarded with the Young and Mid-Aged Expert with
Outstanding Contribution in Jiangsu.
PAPER_TEXT
