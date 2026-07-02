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
# [372] BDIP: An Efficient Big Data-Driven Information Processing Framework and Its Application in DDoS Attack Detection
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
编号：372
题名：BDIP: An Efficient Big Data-Driven Information Processing Framework and Its Application in DDoS Attack Detection
年份：2024
DOI：10.1109/tnsm.2024.3464729
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2024.3464729.pdf
已有粗分类：恶意流量、暗网与攻击检测
二级关联：无
相关性：强相关，分数 14
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\372.txt
- 原始字符数：57833
- 本次发送字符数：57833
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
284

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

BDIP: An Efficient Big Data-Driven Information
Processing Framework and Its Application
in DDoS Attack Detection
Qiyuan Fan , Xue Li , Puming Wang , Xin Jin, Shaowen Yao , Shengfa Miao, Member, IEEE,
Sizhang Li , Min An, and Jing Xu
Abstract—With the rapid advancement of 5G communication
technology in the era of big data, massive terminal devices
connected to the Internet have dramatically increased the scale
of network, generating a large amount of high-dimensional and
heterogeneous information. This not only enhances the difficulty
of information processing in the network, but also poses a
severe challenge to data storage and calculation, which has
become a big data problem to be solved urgently. To cope
with it, this paper proposes an efficient information processing
framework and applies it to Distributed Denial of Service (DDoS)
attack detection. Overall, three major highlights are made: (i)
Tensor is used to represent multi-modal information in largescale networks; (ii) A novel denoising algorithm based on tensor
train(TT) decomposition is proposed, focused on optimizing both
computation and correlation; (iii) A big data-driven information
processing framework is developed, which includes information
preprocessing, denoising and classification. Results in case study
indicate that the framework can achieve an accuracy of 99.19%,
all while maintaining the great storage advantage, well speedup
ratio and strong computing capabilities under the same computational complexity. It can also be generalized to other network
data processing scenarios.
Index Terms—Tensor networks, TT decomposition, storage efficiency, information processing, DDoS attack detection,
machine learning.

I. I NTRODUCTION
N RECENT years, 5G communication technology has provided mobile devices with on demand, flexible, manageable
system resources and services, greatly facilitating people’s lives.
However, this has also led to a significant increase in the scale
of information networks and a more complex network structure,
which not only brings challenges for information processing
but also creates many opportunities for network attacks [1].

I

Received 20 February 2024; revised 3 July 2024; accepted 8 September
2024. Date of publication 20 September 2024; date of current version
14 March 2025. This work was supported in part by the National Nature
Science Foundation of China under Project 62166047; in part by the Yunnan
International Joint Laboratory of Natural Rubber Intelligent Monitor and
Digital Applications under Grant 202403AP140001; in part by the Xingdian
Talent Support Program under Grant YNWR-QNBJ-2019-270; and in part by
The 15th Graduate Research Innovation Project of Yunnan University under
Grant KC-23234593. The associate editor coordinating the review of this
article and approving it for publication was Y.-D. Lin. (Corresponding author:
Puming Wang.)
Qiyuan Fan and Jing Xu are with the School of Software, Yunnan
University, Kunming, China
Xue Li is with the School of Electronic Information Engineering, Henan
Institute of Technology, Xinxiang 453002, China.
Puming Wang, Xin Jin, Shaowen Yao, Shengfa Miao, Sizhang Li, and
Min An are with the School of Software, Yunnan University, Kunming
650091, China (e-mail: pumingwang@gmail.com).
Digital Object Identifier 10.1109/TNSM.2024.3464729

Common network attacks include Distributed Denial of
Service (DDoS), wrapping attack, malware injection attack,
launch malicious Virtual Machine (VM) and VM Escape. It
is DDoS that has become one of the most notorious attack
among them, since its purpose is to first consume system
resources, then cause network overloading, and eventually
stop providing normal services. To make matters worse, the
number of DDoS attacks has increased sharply over the
past few years [2], resulting in a great deal of important
information cannot be processed timely. In addition, individuals and countries are increasingly dependent on the Internet
and network computing, hence, it is urgent to find out an
effective information processing framework to detect DDoS
attacks.
Actually, in the era of big data, how to represent information
in the huge and complex network has become the first major
challenge in detecting DDoS attacks, and it has been proved
that tensor can represent large-scale high-dimensional data
well and fuse heterogeneous data effectively [3]. In this
paper, tensor is used to represent datasets. After that, when
we train the processing model, datasets are always noisefree by default, but collecting and labelling data manually
in reality will inevitably introduce noise into datasets, so
that the quality of datasets will be reduced and negatively
affecting the results [4]. Thus, efficient denoising for datasets
is a crucial step. Data processing method based on tensor
train (TT) decomposition has the characteristics of easy
dimension reduction, strong computing capabilities and great
storage advantage, making it an ideal choice for denoising
large-scale datasets. However, traditional TT decomposition is
computation-intensive and overlooks the correlation between
data, either of which can affect the model to achieve
the optimal result. To address this issue, we propose an
improved TT decomposition for denoising, which can solve
the above problems by tensor low-rank approximation and
reuse, respectively. Additionally, researchers have proposed
many classification models and the model based on machine
learning (ML) has become the most popular one because of
its good effect and lightweight structure. Thus, Light Gradient
Boosting Machine (LightGBM) proposed recently can be a
nice choice. Comparing with other models, it can offer lower
memory consumption, stronger computing capabilities and the
ability to process data in parallel, naturally conforming to
the improved TT decomposition and large-scale information
processing scenario.

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1932-4537 
See https://www.ieee.org/publications/rights/index.html for more information.

FAN et al.: EFFICIENT BDIP FRAMEWORK AND ITS APPLICATION IN DDoS ATTACK DETECTION

On the whole, the primary highlights can be outlined in the
following manner:
• We propose the improved and efficient TT(IETT)
decomposition algorithm for data denoising;
• We propose to combine IETT denoising and LightGBM
classification in a distributed parallel environment,
seamlessly leveraging the strengths of both approaches;
• We propose a big data-driven framework for information
processing and apply it to DDoS attack detection.
The remainder of paper is structured as below. Related work
is recalled in Section II, and some preliminary knowledge
is introduced in the next section. After that, an efficient and
improved TT decomposition based framework for information
processing is proposed in Section IV. Section V describes
the case study by applying the framework to DDoS attack
detection. Summary and future work are given in Section VI.
II. R ELATED W ORK
Detecting DDoS attack detection is a vital application for
the information processing framework. Therefore, numerous
R&D teams have conducted research in this area, trying to
detect and deal with it timely. Broadly, processing frameworks
are classified into three main categories: statistic model, ML
model, hybrid model.
A. Statistic Model
In terms of traffic characteristics, DDoS attack is different
from normal network, and entropy is a statistical method to
measure information uncertainty. Therefore, methods based on
statistic models can identify possible indicators by analyzing
shifts in entropy.
Anderson [5] proposed the intrusion detection as early as
1980. Denning [6] designed the IDS model 6 years later, which
laid an important foundation for the subsequent research on
information processing, especially the DDoS attack detection.
Bhuyan et al. [7] proposed the use of partial rank correlation for detecting high-rate and low-rate DDoS attacks,
where results were highly reliant on threshold selection.
Çakmakçı et al. [8] created a dictionary that quantifies genuine
normal traffic along with its characteristics, and the detection
index was determined by calculating the distance between a
member of the dictionary distribution and a suspicious vector.
In conclusion, a notable limitation of these models is the
requirement to establish a suitable threshold for detection
entropy, as simply observing traffic attributes is inadequate to
differentiate between normal and abnormal traffic.
B. Machine Learning Model
The core function of ML and deep learning (DL) models is
to correctly categorize traffic datasets.
In the field of ML, Barradas et al. [9] proposed FlowLens,
a machine learning system for traffic classification in security network applications. It introduces a memory-efficient
representation called flow marker. By using a profiler in
the control plane, FlowLens generates application-specific
markers that optimize resource consumption and classification
accuracy. Wang et al. [10] proposed to combine sequential
feature selection with Multi Layer Perceptron(MLP) to obtain

285

a feedback mechanism for abnormal traffic detection based on
dynamic perception.
In the field of DL, Doriguzzi-Corin et al. [11] tried to
enhance the deployment stability. They employed deep CNNs
in resource-limited environments, which achieved the efficient
information processing. Apruzzese et al. [12] introduced a
approach to pragmatic evaluations, suggesting a shift towards
assessing the values prioritized by real-world industrial operators who implement intrusion detection systems. It is worth
noting that there is currently a lack of empirical data regarding
the evaluation of intrusion detection systems.
Generally speaking, most ML based models require large
datasets to train, which increases the consumption of computing and storage resources.
C. Hybrid Model
In contrast to traditional information processing algorithms,
the hybrid model is able to combine the advantages of multiple
algorithms, enabling more effective intrusion detection.
Dehkordi et al. [13] introduces an effective SDN-based
DDoS detection method using machine learning and statistical
analysis. Results demonstrate its superior in accuracy and false
positive rates. Swamy et al. [14] presented Taurus, a data plane
architecture employing custom hardware and parallel pattern
abstraction for per-packet MapReduce operations. It accelerates machine learning inference and showcases performance
benefits in data center networks. Wichtlhuber et al. [15]
describes a hybrid system called IXP Scrubber, which detects
and filters DDoS traffic at Internet exchange points (IXPs)
by constantly learning the DDoS traffic characteristics of
neighboring autonomous systems. It uses black hole traffic as
training data and combines it with machine learning models
for classification, while using rule mining and interpretability
techniques to improve interpretability and controllability
Overall, both statistic and machine learning models struggle
to effectively manage information in complex networks. While
a few hybrid models may yield relatively positive results,
they are generally inefficient and consume a sum of storage
space. Therefore, to address these issue, an efficient big datadriven hybrid model based on tensor is proposed, offering high
detection accuracy and low memory consumption.
III. P RELIMINARIES
Some preliminaries are introduced in the section.
Section III-A introduce notations used throughout the
following sections. The concept of tensor algebra are
introduced in Section III-B, and Section III-C describes the
data model.
A. Notations
Based on the established notation conventions [16], we
denote lowercase letters, bold lowercase letters, bold uppercase
letters and calligraphic uppercase letters as scalars, vectors,
matrices and tensors. Moreover, we use XT to express the
transpose matrix, X[i,:] to represent all elements in row i, X[i,j ]
to denote the element of row i column j. Furthermore, subarry
spanning from row i to j is expressed as X[i:j ,:] , sets of real
numbers are denoted as R, a K-mode tensor is represented

286

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

TABLE I
N OTATIONS

Fig. 1.

Fig. 2.

Matricization of a three-dimensional tensor X.

Fig. 3.

(a) Smoothing in Y direction, (b) Smoothing in X direction.

(a) Lateral slices (b) Frontal slices (c) Horizontal slices.

as X ∈ RI1 ×···×IK , containing N =

K

i=1

Ik elements. All

mathematical symbols are listed in Table I.
B. Tensor Algebra

According to the relevant knowledge of tensor, the preprocessing and decomposition of tensor can be defined as follows:
Definition 1 (Slices): Slicing tensors means extracting
higher-dimensional tensors along a certain dimension to get
lower-dimensional tensors. In the case of a three-dimensional
tensor X ∈ RI1 ×I2 ×I3 , if you let I1 and I2 dimensions vary
and fix the I3 dimension, you will get a two-dimensional
matrix X ∈ RI1 ×I2 . Hence, X[:,j ,:] , X[:,:,k ] and X[i,:,:]
shown in Fig. 1 represent the slices from lateral, frontal and
horizontal.
Definition 2 (Matricization): Matrixization is to unfold a
tensor along the k-th dimension and represent it as a series
of matrices. Fig. 2 shows the process of matrixization with
a three-dimensional tensor X ∈ RI1 ×I2 ×I3 as an example, and X(1) ∈ RI1 ×(I2 ×I3 ) , X(2) ∈ RI2 ×(I3 ×I1 ) and
X(3) ∈ RI3 ×(I1 ×I2 ) are the corresponding matrices under
three modes.
Definition 3 (Spatial Smoothing): Firstly, matrix X ∈
sub
RP ×Q can be split into LP submatrices X(lp ) ∈ RP ×Q
sub
along rows and LQ submatrices X(lq ) ∈ RQ ×P along
columns, where P sub = P − LP + 1, lp ∈ {1, 2, . . . , LP } and
Q sub = Q − LQ + 1, lq ∈ {1, 2, . . . , LQ }. Then, the spatial
smoothing preprocessing scheme [17] is applied in each matrix
for p = 1, . . . , P and q = 1, . . . , Q. After that, we can express

(L )

the Pth-mode and Qth-mode smoothing matrix as XSSP,P and
(L )

XSSQ,Q :



sub
(L )
XSSP,P = X(1) , . . . , X(LP ) ∈ RP ×(Q×LP ) ,


sub
( LQ )
XSS ,Q = X(1) , . . . , X(LQ ) ∈ RQ ×(P ×LQ ) .

(1)

Based on equation (1), the smoothing process of matrix
X ∈ RM1 ×M2 is illustrated in Fig. 3. Smoothing can be
(L )
in either the X direction or the Y direction, and XSS1,1 =
(1)

(L )

sub

[X1 , . . . , X1 1 ] ∈ RP1 ×(P1 ×L1 ) represents the spatial
(L )
(1)
(L )
smoothing matrix in X direction, XSS2,2 = [X2 , . . . , X2 2 ] ∈
sub

RQ2 ×(Q2 ×L2 ) represents the spatial smoothing matrix in Y
direction.
Definition 4 (Tensor Product): The tensor product Z of
three-dimensional tensors X ∈ RI1 ×I2 ×I3 and Y ∈ RI2 ×I4 ×I3
is defined as follows,

Z = X ∗ Y ∈ Rn1 ×n4 ×n3 ,
n2

Z[i,j ,:] =
X[i,k ,:]  Y[k ,j ,:] .
k =1

(2)

FAN et al.: EFFICIENT BDIP FRAMEWORK AND ITS APPLICATION IN DDoS ATTACK DETECTION

287

Fig. 4. TT decomposition of an N-dimensional tensor [18]. Firstly, the original tensor is transformed into a matrix. Subsequently, the SVD algorithm is
applied to derive the left singular matrix U, the right singular matrix VT , and the singular value matrix S. This process is carried out in a loop, and finally
all the core tensors G1 , G2 , . . . , GN are obtained.

Definition 5 (Tensor Train Decomposition): It is the TT
decomposition [19] that has become one of the most representative tensor decomposition algorithm. On account of
its unique form of data storage, it has been widely used in
clustering, denoising and prediction.
Fig. 4 illustrates the process of TT decomposition. Its main
task is to decompose an N-dimensional tensor into N − 2
three-dimensional tensors located at intermediate and two
matrices located at both sides. Thus, the TT decomposition of
X ∈ RI1 ×I2 ×···×In ×···IN can be written as follows,

X(i1 , . . . , in , . . . , iN ) = G1 (1, i1 , :)G2 (2, i2 , :) · · · Gn (:, in , :)
, . . . GN (:, iN , 1),
(3)
where Gn ∈ RXn−1 ×In ×Xn is the core tensor and G1 ∈
R1×I1 ×X1 , GN ∈ RXN −1×IN ×1 are the head and tail matrix.
Besides, this process can also be obtained by N − 1
times singular value decomposition (SVD) [18]. So the first
dimension of X can also be represented in the following
manner,

X = U1 ∗ S1 ∗ VT
1 + E1 ,

(4)

where U1 and V1 are orthogonal tensors, S1 is the diagonal
tensor, E1 consists of singular values from other dimensions.
To relate SVD and TT decomposition, S1 ∗ VT
1 is regarded
as M1 for better representing the correlation of TT cores.
Therefore, combining with equation (3) and Fig. 5, equation (4) is able to reformulate as follows,

X=

T1

t1 =1



G1 (1, i1 , t1 )M1 t1 i2 , i3 , . . . , iN + E1 ,

(5)

where T1 denotes the rank of first TT core, G1 (1, :, :) = U1 ,
t1 i2 means concatenating the t1 and i2 of M1 .
C. Data Model
With the blooming development of 5G communication
technology and the Internet, data in the network can presents
the following characteristics that need to be noted in intrusion
detection:
• Large-Scale: In the age of Internet, the Web can generate
an immense number of gigabytes of traffic data in mere

Fig. 5. A three-dimensional tensor data model X. It can be divided into a
noise-free tensor X0 and a noisy tensor X1 .

seconds, covering a broad spectrum of everyday activities. Consequently, the detection system must swiftly and
precisely handle these vast quantities of information;
• Heterogeneous: Typically, network traffic data is produced and gathered from various locations and origins,
manifesting in both structured formats (like databases)
and unstructured formats (like videos) [20]. Therefore,
the framework must have the ability to identify data of
diverse types;
• Multi-Modal: Each instance of traffic data encompasses
a range of details, including IP address, time stamp,
network protocol, and etc. Thus, it is essential to integrate these into a multi-modal dataset during processing,
thereby leveraging the full spectrum of available features.
In order to effectively accommodate these characteristics, tensor, as the multi-dimensional extension of matrix,
is employed to represent datasets in our work. Different to
matrices, tensors enable a natural utilization of the multi-order
properties inherent in network datasets, which helps to capture
complex relationships between characteristics and retain the
correlation between modals [3]. Therefore, considering the
noise that inevitably exists in datasets, the three-dimensional
datasets X shown in Fig. 5 can be divided into a noise-free
tensor X0 and a noisy tensor X1 :

X = X0 + X1 ,

(6)

Thus, we need to reduce the influence of noisy tensor X1
to noisy tensor X0 when processing datasets X.
IV. T HE P ROPOSED B IG DATA -D RIVEN I NFORMATION
P ROCESSING F RAMEWORK
This section illustrates the proposed big data-driven
information processing framework (BDIP) from three aspects.

288

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

Fig. 6. The proposed DDoS attack detection framework and it can be divided into three parts: (a) Data Preprocessing, (b) Data Denoising, (c) Data Classifying.

As shown in Fig. 6, BDIP consists of three parts. Firstly,
Fig. 6(a) introduces data preprocessing, which makes the
messy initial datasets computable; then, Fig. 6(b) introduces
data denoising, which removes the unnecessary noise to
improve the accuracy of processing; finally, Fig. 6(c) introduces data classification, which classifies normal and abnormal
traffic information to get the final result.
A. Data Preprocessing
Datasets preprocessing is beneficial for the following
denoising and classifying, so a series of methods are introduced in the subsection.
1) Delete Meaningless Words: The first step is to delete
some meaningless words so as not to interfere with subsequent
works. For example, words like NAN, INF, IND will be
removed.
2) Convert Strings Into Numeric Values: Then, certain
types of strings must be transformed into numeric values.
For instance, categorical labels such as ‘yes’ and ‘no’ are
able to convert into ‘1’ and ‘0’, respectively. This conversion
preserves the semantic meaning of the labels, conserves
storage space, and enhances computational efficiency.
3) Feature Selection: Considering that there are plenty of
features in network datasets, and a portion of them have little
impact on the framework, thus we only need to select the more
important features which can simplify the calculation without
affecting the results.
4) Cross Validation: K-fold cross validation can divide
datasets into K blocks, one of which is selected each time as
the testing set, and the rest K − 1 blocks as the training set.
After K times, each block is tested once and trained K − 1
times, and the result will take the mean of K times. In this
way, it can effectively avoid overfitting.
Additionally, according to Maranhão et al. [21], the value
of K is usually chosen as 5 or 10 to better represent entire

datasets. Given the considerable size of the datasets in our
study, optimal detection results can still be achieved with a
reduced K. Therefore, we opt K = 5 for a better efficiency of
the framework.
5) Standardization: The final step of the data preprocessing
is standardization. It can adjust the scale of feature values
between [0, 1], while maintaining a portion of the original
distribution of the anomalous data caused by DDoS attacks.
Hence, this could potentially enhance the precision of the
model and expedite its convergence rate. The equation of
standardization is shown as follows,


X[p,q] − mean X[:,q]

,
(7)
nom X[p,q] =
std X[:,q]
where std (X[:,q] ) is the standard deviation, mean(X[:,q] )
represents the mean value of X[:,q] .
B. Data Denoising
Some supervised learning algorithms make a specific
assumption on noise distribution (such as Gaussian distribution), but generally, they do not assume that the dataset
is completely noise-free. Additionally, the origins of data,
the collection methodologies, the subjectivity in the labeling process and various other elements may also introduce
noise to datasets. Therefore, it becomes imperative to implement denoising techniques. In this subsection, datasets will
be denoised by smoothing reconstruction of space and TT
decomposition.
1) Tensor Space Smooth and Reconstruction: The tensor
space smooth and reconstruction is an expansion of the matrix
smoothing technique described in Section III, requiring us
(L)
to broaden the approach accordingly. Smooth matrix XSS is
(L
)
assembled from a sequence of submatrices X i , enabling
the extraction of spatial smoothing subtensors X(lk ) . This

FAN et al.: EFFICIENT BDIP FRAMEWORK AND ITS APPLICATION IN DDoS ATTACK DETECTION

289

is accomplished by applying smoothing to a K-dimensional
tensor residing in X ∈ RI1 ×I2 ×···×IK specifically along its
K − th dimension,
sub ×

X(lk ) ∈ RNk

i=k Ni

= X[:,...,lk :lk +N sub ,...,:] ,
k

(8)

where X[:,...,lk :lk +N sub ,...,:] represents the subtensor interk

cepted by X ∈ RN1 ×···×NK along the K − th dimension,
lk ∈ {1, 2, . . . , Lk }, Nksub = Nk − Lk + 1, and Lk denotes
the number of blocks along the K − th dimension, in which
k ∈ {1, 2, . . . , K }. Moreover, if we continuously smooth these
subtensors X(lk ) along the second dimension, we will get a
(K + 1)-dimensional tensor,



sub
(L )
XSSk,k ∈ RNk ×Lk × i=k Ni = X(1) , . . . , X(Lk ) . (9)
Generally speaking, the tensor smooth algorithm strengthens
the non-singularity of datasets, providing a theoretical foundation for subsequent decomposition and classification. However,
during practical computation, the subtensors that result from
smoothing operations conducted in various dimensions may
vary in size. Consequently, it is necessary to reconstruct
these subtensors to ensure consistency and compatibility. For
instance, the K-dimensional tensor X ∈ RN1 ×N2 ×···×NK
is able to partition into NK subtensors along its K − th
dimension,
⎤
⎡
X[:,...,1,...,:]
..
⎥
⎢
⎥
⎢
.
⎥
⎢
⎥
X
(10)
X=⎢
⎢ [:,...,k ,...,:] ⎥
⎥
⎢
.
..
⎦
⎣

X[:,...,NK ,...,:]

in which K ∈ {1, 2, . . . , NK }. Furthermore, it is necessary to
reconstruct subtensors through the equation:
l

X[:,...,k ,...,:] =

K
1 
(i)
X[:,...,k −i+1,...,:] ,
lk

(11)

i=1

in which lk denotes the number of smoothing times and 0 ≤
k − i + 1 ≤ NKsub .
To be specific, if tensor X ∈ R3×3×3 is smoothed
(3)
along the second dimension, the smooth tensor XSS ,2 =
[X(1) , X(2) , X(3) ] can be obtained. Based on equation (11),
we can denote its reconstruction result X ,
⎤
⎡
(1)
X[:,1,:]
⎥
⎢

⎥
⎢
1 × X(1) + X(2)
⎥
⎢
2
[:,2,:]
[:,1,:]
⎥
⎢

⎥
⎢1
(1)
(2)
(3)

(12)
X = ⎢ 3 × X[:,3,:] + X[:,2,:] + X[:,1,:] ⎥
⎥
⎢

⎥
⎢
(2)
(3)
1 × X
+ X[:,2,:]
⎥
⎢
2
[:,3,:]
⎦
⎣
(3)
X[:,3,:]
2) IETT: Improved and Efficient TT Decomposition: It is
TT decomposition that has become a significant method for
data denoising. However, when in large-scale, multi-modal
information processing scenarios, it will usually produce a
amount of computation and it can not maintain the correlation

Fig. 7.

Description of MDL principle for TT ranks.

between different modes of data. Hence, we can improve TT
decomposition from these two aspects, respectively.
On the one hand, TT rank plays an important role in
TT decomposition, low TT ranks can effectively reduce the
computation and data feature loss. Thus, we use Minimum
Description Length (MDL) principle to get an approximate
low TT rank. Based on Wax and Kailath [22], we can get the
following equation,
 n

1/(n−t) L(n−t)
MDL(t) =

1
t(2n − t)logL − log
2

rank (X) = argmin (MDL(t)),

k =t+1 σk
1 n
k =t+1 σk
n−t

t

,

(13)

where the number of eigenvalues is expressed by n, σk denotes
the eigenvalue, L represents the length of datasets, k ∈
{1, 2, . . . , n}, σ1 > σ2 > · · · > σn .
Taking a group of sinusoidal function as an example, 20dB
zero mean white Gaussian noise is added for denoising by
TT decomposition. According to equation (13), Fig. 7(a)
depicts the variation of the MDL-value across various kvalues, revealing that the MDL attains its lowest value when
k = 4. Fig. 7(b) illustrates the change in singular values in
conjunction with the TT rank, we can still find that singular
value reach a high value only when 0 ≤ rank ≤ 4. This
observation is in agreement with the findings presented in Fig.
7(a). Additionally, singular value can provide useful characteristic information for denoising while TT decomposition can
be realized by multiple singular value decomposition, so we
truncate the first four sets of singular values in this paper.
On the other hand, traditional TT decomposition can
decompose a huge high-dimensional tensor into a series of
three-dimensional tensors and matrices, but the correlation
between them is not guaranteed. According to Section III,
a TT decomposition can be completed by multiple SVDS
while SVD have the ability to preserve the correlation between
different modes. On this basis, we propose the reuse of
tensors. Specifically, after each decomposition, we retain the
orthogonal tensor U as the core tensor, the tensor product of
another orthogonal tensor VT and the diagonal tensor S is
used as the input for the next decomposition.
(1)
(1)
(1)
(2)
(2)
Taking the tensor X ∈ RL1 ×L2 ×···×LN ×L1 ×L2 ×···
(2)
(n)
(n)
(n)
×LN ×···×L1 ×L2 ×···×IN as an example. Firstly, we use
(1) (1)
(1)
TT decomposition on dimension L1 , L2 , . . . , LN to obtain
X1 ,

X1 = U(1) ∗ S(1) ∗ VT
(1) ,

(14)

290

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

Fig. 8. The process of Improved and Efficient Tensor Train Decomposition(IETT). Firstly, estimating the TT rank of the tensor and applying IETT on each
modal I1 , I2 , . . . , IN . Secondly, getting the reuse tensor for the next round of IETT. Finally, obtaining the core tensors: G1 , G2 , . . . , GN .
(1)
(1)
(1)
(n)
(n)
(n)
where S(1) ∈ RL1 ×L2 ×···×LN ×···×L1 ×L2 ×···×LN rep(2)

(2)

(2)

L1 ×L2 ×···×LN ×···
resents the diagonal tensor, VT
(1) ∈ R
(n)
(n)
(n)
(1)
(1)
(1)
L ×L2 ×···×LN denote
×L1 ×L2 ×···×LN and U
(1) ∈ R 1
the orthogonal tensors. Thus, the core tensor G1 is able to

Hence, we can
(3) (3)
(3)
L1 , L2 , . . . , LN ,

(15)

In the subsequent decomposition, tensor X2 is derived from
the product of tensors S(1) , VT
(1) ,

X2 = S(1) ∗ VT
(1) .
Hence, we can
(2) (2)
(2)
L1 , L2 , . . . , LN ,

(16)

X2

decompose

on

X2 = U(2) ∗ S(2) ∗ VT
(2) ,
where S(2) ∈ R
(n)

· · · × L1

(1) (2)
(3) (3)
(3)
(1) (2)
(1) (2)
L1 L1 ×L2 L2 ×··· ×LN LN ×L1 L2 ×···×LN ×

(n)

× L2

(n)

× · · · × LN

represents the diagonal

(3)
(3)
(3)
(n)
(n)
(n)
L1 ×L2 ×···×LN ×···×L1 ×L2 ×···×LN
tensor, VT
(2) ∈ R
(1) (2)

(1) (2)

(1) (2)

and U(2)
∈ RL1 L1 ×L2 L2 ×···×LN LN denote the
orthogonal tensors. Thus, the core tensor G2 is able to acquire,

G2 = U(2) .

(18)

In a similar way, tensor X3 is derived from the product of
tensors S(2) , VT
(2) ,

X3 = S(2) ∗ VT
(2) .

(19)

on

dimension

Gn−1 = U(n−1) .

(20)

Ultimately, after n iterations of decomposition, tensor Xn
is derived from the product of tensors S(n−1) , VT
(n−1) ,

Xn = S(n−1) ∗ VT
(n−1) ,

dimension

(17)

X3

X3 = U(3) ∗ S(3) ∗ VT
(3) .
,...
,...
X(n−1) = U(n−1) ∗ S(n−1) ∗ VT
(n−1) .

acquire,

G1 = U(1) .

decompose

where S(n−1)

(1) (2)
×LN LN ···

(n−1)

LN

(1) (2)

(n−1)

∈ RL1 L1 ···L1
(n) (n)

× L1 L2

(n)

· · · LN
(n)

(21)
(1) (2)

represents

(n)

(n−1)

×L2 L2 ···L2

(n)

the

×···

diagonal

tensor, VT
∈ RL1 ×L2 ×···×LN and U(2)
(2)
(1) (2)
(n−1)
(1) (2)
(n−1)
(1) (2)
(n−1)
×L2 L2 ···L2
×···×LN LN ···LN
RL1 L1 ···L1

∈

denote orthogonal tensors. Thus, the last core tensor Gn can
be acquired,

Gn = X(n) .

(22)

According to Fig. 4, equation (13) to equation (22) and
related knowledge in Section III, we propose an improved
and efficient TT decomposition algorithm(IETT) by combining
low TT ranks based on MDL principle and the tensor reuse
method as shown in Algorithm 1 and Fig. 8.

FAN et al.: EFFICIENT BDIP FRAMEWORK AND ITS APPLICATION IN DDoS ATTACK DETECTION

Algorithm 1 Algorithm of IETT
Input: An
(N × n)-dimensional

291

Algorithm 2 Algorithm of LIPD
tensor

X

∈

(1)
(1)
(1)
(2)
(2)
(2)
(n)
(n)
(n)
L
×L2 ×···×L
×L1 ×L2 ×···×L
×···×L1 ×L2 ×···×I
N
N
N
R 1

;
Accuracy of the decomposition ε.
Output: A series of TT cores G1 , G2 , · · · , GN that satisfied
||Gj − Hj ||F ≤ ε||Gj ||F , where Hj is an approximate of
Gj and j ∈ 1, 2, . . . , N .
1: Initialize M1 = X, R0 = 1;
2: for i = 1 to n − 1 do
3:
Estimate the TT rank according to equation (13): Ri =
MDL(Mi )
4:
Compute Ri -Truncated SVD according to Fig.8:
≤
Mi = U(i) S(i) VT
(i) + E(i) , where ||E(i) ||F
√ ε ||X ||F
n−1
5:
Compute the TT core according to equation (14) to
equation (22): Gi = reshape(U(i) , [Ri−1 , Li , Ri ])
T
6:
Compute M̂ = S(i) V(i)
Update
the
new
tensor:
Mi+1
=
7:
reshape(M̂ , [Ri−1 Li , Li+1 , · · · , Ln ])
8: end for
9: Gn = Mn
10: Return H with new TT cores: G1 , G2 , · · · , Gn

3) Large-Scale
Information
Processing
Denoising
Algorithm: Combining tensor smooth and reconstruction with
IETT, a large-scale information processing denoising (LIPD)
algorithm is presented in Algorithm 2, the elaboration of this
process is shown as follows:
• Algorithm 2, Line 1:
Datasets X ∈ RM ×N is folded into a (K + 1)dimensional tensor X ∈ RM ×N1 ×···×NK , where N1 ×
· · · × NK = N ;
• Algorithm 2, Line 4 ∼ 6:
According to equation (8), tensor X[m,:,...,:] ∈
k − th dimension, and
RN1 ×···×NK is smoothed in the
sub 
(l )
Lk subtensors Xmk ∈ RNk × i=k Ni are obtained;
• Algorithm 2, Line 7:
According to equation
 (9), the smoothing tensor
(Lk )
Nksub ×Lk × i=k Ni
Xm,SS
∈
R
can be obtained;
,k
• Algorithm 2, Line 8:
(Lk )
Smoothing tensor Xm,SS
,k is denoised by IETT, and the
calculating method is given in Algorithm 1;
• Algorithm 2, Line 9:
According to equation (10) and equation (11), denoising
(Lk )
tensor X̂m,SS ,k is used to reconstruct and update tensor
X[m,:,...,:] . Then, X[m,:,...,:] is denoised in the dimension
of (k + 1) − th.
Lines 4 ∼ 9 will repeat until all dimensions are updated.
• Algorithm 2, Line 11:
When the loop is finished, tensor X[m,:,...,:] is denoised
by IETT for the last time.
Lines 4 ∼ 11 will iterate until the denoising of the entire
datasets is completed.
• Algorithm 2, Line 13:

Input: Matrix X ∈ RM ×N ;
Max number of subarrays Lk ∈ {L1 , . . . , LK }.
Output: Denoised matrix X̂ ∈ RM ×N .
1: Fold
matrix
X ∈ RM ×N
into
tensor
M
×N
×···×N
1
K
X∈R
;
2: for m = 1 to M do
3:
for k = 1 to K do
4:
for lk = 0 to Lk do
(l )
5:
Xmk = X[m,:,...,lk :lk +N sub ,...,:]
k
end for
6:
(Lk )
(1)
(Lk )
7:
Xm,SS ,k = [Xm , · · · , Xm ]
8:

(L )

IETT

(L )

k
k
Xm,SS
,k −−−−→ X̂m,SS ,k

(Lk )

Update X[m,:,...,:] by X̂m,SS ,k
end for
IETT
11:
X[m,:,...,:] −−−−→ X̂[m,:,...,:]
12: end for
13: Unfold
tensor X̂ ∈ RM ×N1 ×···×NK
M
×N
.
X̂ ∈ R
9:
10:

into

matrix

Finally, the denoised tensor X̂ ∈ RM ×N1 ×···×NK is
unfolded into the matrix X̂ ∈ RM ×N .
After preprocessing and denoising, the noise of datasets is
extremely attenuated, which is of great help to classify.
C. Data Classification
LightGBM [23] is an efficient gradient boosting decision
tree (GBDT) based framework that enables high accuracy,
low memory consumption and fast speed through distributed
computing when classifying large-scale datasets. These characteristics, especially in terms of memory advantages, fit
seamlessly with IETT and have become significant reasons for
choosing LightGBM.
V. C ASE S TUDY
In this section, the proposed framework BDIP will be
applied to large-scale DDoS attack detection scenarios and
verified by a series of experiments. Section V-A describes the
background of DDoS attack detection, and datasets used in
experiments is illustrated in Section V-B. Section V-C lists
experimental evaluation metrics, and the last subsection introduces the contrast experiments and results analysis.
A. Background Description
We applied BDIP to DDoS attack detection to verify the
effectiveness of the framework. Fig. 9 shows a typical DDoS
attack scenario where devices including large servers, personal
computers, etc. are attacked as puppet machines (PM) to
further attack infrastructures that connected to the Internet.
PM refer to the compromised devices controlled by attackers.
Once that happens, attackers will instruct PM to send massive
attack packets to critical network components, resulting in
initial partial denial of service and finally complete denial
of service, which can make a huge trouble on information

292

Fig. 9.

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

A typical DDoS attack scenario.

processing. Therefore, it is meaningful to detect DDoS attacks
in large-scale network timely.

TABLE II
F EATURES U TILIZED IN CIC-DD O S2019

B. DDoS Attack Datasets
To validate the experimental results, we employ the
recently established datasets CIC-DDoS2019 and NLS-KDD
for assessing performance metrics.
1) CIC-DDoS2019: CIC-DDoS2019 [24], which was
developed by Cyber Security Research Laboratory of
Concordia University, contains millions of network traffic data
with 87 features. However, before the experiment, we will
delete features that have little contribution to classification,
including IP information, protocol type, time stamp and
irrelevant identifier. After that, we will get 64 features
shown in Table II. In order to express the feature name
conveniently, we adopt the following abbreviations: FC
symbolizes Flag-Count, PL symbolizes Packet-Length, SB
symbolizes Subflow-Bwd, SF symbolizes Subflow-Fwd, TL
symbolizes Total-Length, FPL, BPL symbolize Fwd-PacketLength, Bwd-Packet-Length and FlI, FwI, BI symbolize
Flow-IAT, Fwd-IAT, Bwd-IAT.
In addition, 40,000 traffic will be randomly selected from
CIC-DDoS2019 as the experimental datasets. Considering that
DDoS attacks do not occur as frequently as normal traffic, we
will select 8,000 abnormal traffic and 32,000 normal traffic.
More details are shown in Table III.
2) NSL-KDD: NLS-KDD [25] is also a widely used dataset
in DDoS attack detection. Similar to CIC-DDoS2019, we
delete 5 of 41 features before using it, and for the sake of
avoiding overfitting, we increase the proportion of abnormal
traffic to 40% while randomly selecting. Specific instructions
are given in Table IV, Table V and we use DH to represent
Dist-Host.
3) Feature Grouping: To optimize the utilization of
tensors, we need to group the features extracted from the
two datasets before experiment. To be specific, we try
to put as many highly correlated features in the same
small tensor as possible, so that they can be denoised and
classified on the same computing core. For example, when
processing CIC-DDoS2019, we are supposed to place the
features “Fwd-Packet-Length-Max, Fwd-Packet-Length-Min,
Fwd-Packet-Length-Avg, Fwd-Packet-Length-Std-Dev” and
“Bwd-Packet-Length-Max, Bwd-Packet-Length-Min, BwdPacket-Length-Avg, Bwd-Packet-Length-Std-Dev” in two

different tensors, because the former set of features pertains to
“Forward Traffic”, while the latter set pertains to “Backward
Traffic”.
C. Evaluation Metrics
Some metrics will be introduced in this subsection. They are
considered as macro-averaged, so they all have values between
0 and 1. In addition, we use TP, FN, FP, TN represents True
Positive, False Negative, False Positive and True Negative,
respectively.
1) The equation of Accuracy (Acc) is as follows:
Acc =

TP + TN
.
TP + FN + FP + TN

(23)

FAN et al.: EFFICIENT BDIP FRAMEWORK AND ITS APPLICATION IN DDoS ATTACK DETECTION

TABLE III
T HE T YPES OF T RAFFIC AND THE N UMBER OF I NSTANCES U SED IN
CIC-DD O S2019

TABLE IV
F EATURES U TILIZED IN NSL-KDD

S=
(24)

3) The equation of Recall (Rec) is as follows:
Rec =

TP
.
TP + FN

(25)

4) The equation of F1-Score is as follows::
F1 − Score =

2 · Precision · Recall
.
Precision + Recall

TABLE V
T HE T YPES OF T RAFFIC AND THE N UMBER OF I NSTANCES
U SED IN NLS-KDD

based on different classification algorithms. Finally, we asses
the comprehensive performance against other frameworks.
1) Determination of Experimental Parameters: In order to
achieve the optimal detection results, we need to set the suitable parameters before experiments. Firstly, for initial datasets
CIC-DDoS2019 and NSL-KDD, they will be expressed as
X ∈ RM ×N , where M is the total number of data, N is the
feature number of datasets. And in the algorithm of LIPD, both
datasets will be folded into the three-dimensional tensor X ∈
RM ×N1 ×N2 , in which N = N1 × N2 , N1 = N2 = 8 of CICDDoS2019, N1 = N2 = 6 of NSL-KDD. Secondly, 5-fold
cross validation is used to make training sets and testing sets.
Finally, experiments are conducted in the distributed parallel
environment. Thus, a suitable speedup needs to be selected. As
the key performance indicator in parallel computing, speedup
is calculated by dividing the execution time of a sequential
program by that of its parallel version. The formula for this
assessment is presented below:

2) The equation of Precision (Pre) is as follows:
TP
Pre =
.
TP + FP

293

(26)

D. Contrast Experiments
In this subsection, a group of contrast experiments are
carried out to evaluate the performance of BDIP under
different conditions. Firstly, we determine the experimental
parameters and explain their rationality. Secondly, we consider
the performance under different signal-to-noise ratio (SNR).
After that, we give the classification results based on different
denoising algorithms. Then, we show the detection results

Ts
,
Tp

(27)

where S represents speedup, execution times for the serial and
parallel versions of a program are denoted by Ts and Tp .
Therefore, the increase in the number of computing cores
can decrease the computing time and enhance the speedup,
but it may also raise other costs such as the communication
between computing cores and synchronization wait. Hence,
the speedup curve does not increase linearly, its growth rate
slow down gradually and will appear the inflection point. In
order for our model to be widely used, especially for individual
users who do not have many computing resources, we need
to choose an optimal speedup. Fig. 10(a) illustrates how the
speedup of BDIP varies with the number of computing cores.
We can find that speedup increases very fast when the number
of cores is less than 5, and becomes very slow when the cores
is greater than 5. Overall consideration, we choose the speedup
of 5 to balance computation cost and speed.
Fig. 11(b) explains this in more detail. We observe how
speedup changes by adjusting the tensor scale of the input

294

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

Fig. 10. The choice of Speedup: (a) Speedup varies with the number of
computing cores. (b) Speedup varies with the number of features used in each
dimension.

datasets. Taking CIC-DDoS2019 as an example, it is first
represented as a set of four-dimensional tensors with 64 traffic
data of each dimension. Then, we adjust the scale of each
dimension, and finally use the BDIP framework to process it in
parallel with 5 computing cores. Results shown in Fig. 10(b)
indicates that as the data scale increases of each dimension,
the speedup also increases. In conclusion, BDIP is naturally a
DDoS attack detection framework suitable for big data.
2) Different SNR: As the initial level of noise in datasets
is unknown, it can first be assumed as noise-free [4]. Then
zero-mean white Gaussian noise is introduced into datasets
through the supervised manner. This allows us to assess the
performance of frameworks across a range of −10dB to 10dB
by evaluating SNRout . The equation is as follows,


X2 2F
SNRout = 10 · log10
(dB ),
(28)
X2 − X0 2F
where X2 denotes the denoised data, | · |F represents the
Frobenius norm.
In order to ensure the effectiveness, we have chosen a mix
of established and contemporary frameworks for comparison
with BDIP on CIC-DDoS2019. Specifically, we include the
traditional methods of SVD [26] and HOSVD [27], alongside
the more recent MUDE [21] and TSSD [28], which have
demonstrated promising outcomes. In addition, we choose
L1 = L2 = 2 in Algorithm 2. The result is shown in
Fig. 11, it can be found that SNRin ≈ SNRout without any
denoising. Moreover, all denoised datasets are superior to the
original one, and HOSVD should perform better than SVD,
because SVD processes data from the matrix perspective but
HOSVD uses tensor structures to perform SVD on higher
dimension. Furthermore, HOSVD and SVD perform denoising
across the entire dataset X ∈ RM ×N , while recently proposed
MUDE, TSSD and BDIP target the denoising of individual
data instances X[m,:,:] ∈ RN1 ×N2 , which can reduce the noise
more effectively. Experiments demonstrate BDIP outperforms
other methods by efficiently preserving data characteristics and
capitalizing on the strengths of tensor.
3) Different Denoising Algorithm: Our assessment of
LIPD’s denoising efficacy is conducted by comparing it
with SVD, HOSVD, MUDE, and TSSD under uniform SNR
conditions set at 0dB, with LightGBM serving as the classification algorithm. Experiments are visualized in Fig. 12 and
Fig. 13, which depict the fluctuation of evaluation metrics

Fig. 11.

SNRout with SNRin for tensor X ∈ RN1 ×N2 ×M .

corresponding to the CIC-DDoS2019 and NSL-KDD datasets,
respectively. It is observed that the performance of all frameworks improves with an increasing proportion of the datasets,
as this allows for a richer set of features to be presented to
the classification algorithm. Additionally, HOSVD generally
outperforms SVD across most scenarios, due to its more
pronounced denoising capabilities in higher dimensions and its
ability to conduct multiple SVDs simultaneously, thereby compensating for the shortcomings of machine learning classifiers.
LIPD, in most evaluation metrics, is either slightly superior
or comparable to MUDE and TSSD, with the exception of
memory consumption. This is attributed to the significant
advantages of IETT-based frameworks over SVD-based ones
in high-dimensional contexts, which is crucial for detecting
DDoS attacks in large-scale and heterogeneous networks.
4) Different Classification Algorithm: We evaluate the
impact of various classification algorithms on experimental
outcomes, with all tests performed at an SNR level of 0dB
and denoising carried out via the IETT method. In this
comparison, we analyze the performance of LightGBM in
contrast to Logistic Regression (LR), SVM (Support Vector
Machine), MLP (Multi Layer Perceptron), XGBoost [29],
and CatBoost [30] on two datasets. The findings, depicted
in Fig. 14 and Fig. 15, indicate that LR generally delivers
the least favorable results across all metrics, despite its quick
execution time. Conversely, LightGBM exhibits the most
impressive performance, particularly with extensive datasets,
aligning perfectly with the IETT framework.
5) Comparison With Related Frameworks: Lastly, we have
chosen a number of pertinent frameworks for a comparative
evaluation against BDIP, focusing on their detection capabilities on NSL-KDD. To align with the prevailing practices
where the majority of related studies utilize noise-free datasets,
we have set the SNR at a high level of 35dB to replicate a
low-noise environment. The comparative results are detailed
in Table VI. Our proposed BDIP framework outperforms the
others in terms of accuracy. While TBF may show the highest
F1-Score, it comes with a significantly higher false alarm rate.
MMNR delivers a performance close to our method, if the
consumption of memory is not a critical factor, owing to its
tensor-based approach similar to ours.

FAN et al.: EFFICIENT BDIP FRAMEWORK AND ITS APPLICATION IN DDoS ATTACK DETECTION

Fig. 12.

Performance Comparison of Different Denoising Algorithms on CIC-DDoS2019.

Fig. 13.

Performance Comparison of Different Denoising Algorithms on NSL-KDD.

VI. C ONCLUSION
In this study, we introduce an efficient information processing framework known as BDIP, which is designed to handle
big data challenges and has been implemented for the detection
of Distributed Denial of Service attacks. The framework is

295

comprised of three main components: preprocessing, denoising, classification. Highlight is the proposal of IETT and LIPD.
They can effectively denoise through smooth reconstruction
of tensor space, which not only provides clean datasets
for LightGBM to classify, but also enhances the computing

296

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

Fig. 14.

Performance Comparison of Different Classification Algorithms on CIC-DDoS2019.

Fig. 15.

Performance Comparison of Different Classification Algorithms on NSL-KDD.

power and greatly reduces the consumption of storage. The
subsequent contrast experiments have proved its effectiveness
from several aspects. Compared with previous works, the
tensor-based framework can better process large-scale highdimensional information, while BDIP are naturally suitable

for these scenarios, thus improving the detection accuracy and
preventing the occurrence of dimensional disasters.
As for future work, we intend to do further research
on distributed computing, a optimal speedup ratio can
greatly improve the experimental efficiency. Additionally,

FAN et al.: EFFICIENT BDIP FRAMEWORK AND ITS APPLICATION IN DDoS ATTACK DETECTION

297

TABLE VI
C OMPARISON OF D IFFERENT DD O S ATTACK D ETECTION F RAMEWORKS

auto-generating data-plane pipelines [33] are also worth considering. It offers network operators a straightforward means to
convey their requirements to compilers, removing the manual
task of fine-tuning hyperparameters and managing diverse
network data plane and topological demands, thus enhancing
the efficiency of intrusion detection.
R EFERENCES
[1] B. Coelho and A. Schaeffer-Filho, “BACKORDERS: Using random
forests to detect DDoS attacks in programmable data planes,” in Proc.
5th Int. Workshop P4 Europe, 2022, pp. 1–7.
[2] M. Mittal, K. Kumar, and S. Behal, “DDoS-AT-2022: A distributed
denial of service attack dataset for evaluating DDoS defense system,”
in Proc. Indian Nat. Sci. Acad., 2023, pp. 1–19.
[3] P. Wang, L. T. Yang, J. Li, X. Li, and X. Zhou, “RM2 T2 C: Retrospective
multivariate Multistep transition tensor chain model for user mobility pattern prediction,” IEEE Trans. Ind. Informat., vol. 18, no. 10,
pp. 6991–6999, Oct. 2020.
[4] J. A. Sáez, M. Galar, J. Luengo, and F. Herrera, “Tackling the problem of
classification with noisy data using multiple classifier systems: Analysis
of the performance and robustness,” Inf. Sci., vol. 247, pp. 1–20,
Jun. 2013.
[5] J. P. Anderson, Computer Security Threat Monitoring and Surveillance,
James P, Anderson Co., Fort Washington, PA, USA, 1980.
[6] D. E. Denning, “An intrusion-detection model,” IEEE Trans. Softw. Eng.,
vol. SE-13, no. 2, pp. 222–232, Feb. 1987.
[7] M. H. Bhuyan, A. Kalwar, A. Goswami, D. Bhattacharyya, and J. Kalita,
“Low-rate and high-rate distributed DoS attack detection using partial
rank correlation,” in Proc. 5th Int. Conf. Commun. Syst. Netw. Technol.,
2015, pp. 706–710.
[8] S. D. Çakmakçı, T. Kemmerich, T. Ahmed, and N. Baykal, “Online
DDoS attack detection using Mahalanobis distance and kernel-based
learning algorithm,” J. Netw. Comput. Appl., vol. 168, Oct. 2020,
Art. no. 102756.
[9] D. Barradas, N. Santos, L. Rodrigues, S. Signorello, F. M. Ramos, and
A. Madeira, “FlowLens: Enabling efficient flow classification for MLbased network security applications,” in Proc. NDSS, 2021, pp. 1–18.
[10] M. Wang, Y. Lu, and J. Qin, “A dynamic MLP-based DDoS attack detection method using feature selection and feedback,” Comput. Security.,
vol. 88, Jan. 2020, Art. no. 101645.
[11] R. Doriguzzi-Corin, S. Millar, S. Scott-Hayward, J. Martinez-del Rincon,
and D. Siracusa, “LUCID: A practical, lightweight deep learning
solution for DDoS attack detection,” IEEE Trans. Netw. Service Manag.,
vol. 17, no. 2, pp. 876–889, Jun. 2020.
[12] G. Apruzzese, P. Laskov, and J. Schneider, “SoK: Pragmatic assessment of machine learning for network intrusion detection,” 2023,
arXiv:2305.00550.
[13] A. B. Dehkordi, M. Soltanaghaei, and F. Z. Boroujeni, “The
DDoS attacks detection through machine learning and statistical methods in SDN,” J. Supercomput., vol. 77, pp. 2383–2415,
Mar. 2021.
[14] T. Swamy, A. Rucker, M. Shahbaz, I. Gaur, and K. Olukotun,
“Taurus: A data plane architecture for per-packet ML,” in Proc. 27th
ACM Int. Conf. Archit. Support Program. Lang. Oper. Syst., 2022,
pp. 1099–1114.

[15] M. Wichtlhuber et al., “IXP scrubber: Learning from blackholing traffic
for ML-driven DDoS detection at scale,” in Proc. ACM SIGCOMM
Conf., 2022, pp. 707–722.
[16] T. G. Kolda and B. W. Bader, “Tensor decompositions and applications,”
SIAM Rev., vol. 51, no. 3, pp. 455–500, 2009.
[17] T.-J. Shan, M. Wax, and T. Kailath, “On spatial smoothing for directionof-arrival estimation of coherent signals,” IEEE Trans. Acoust., Speech,
Signal Process., vol. 33, no. 4, pp. 806–811, Aug. 1985.
[18] Q. Fan et al., “IDAD: An improved tensor train based distributed DDoS
attack detection framework and its application in complex networks,”
Future Gener. Comput. Syst., vol. 162, Jan. 2025, Art. no. 107471.
[19] I. V. Oseledets, “Tensor-train decomposition,” SIAM J. Sci. Comput.,
vol. 33, no. 5, pp. 2295–2317, 2011.
[20] R. Fan et al., “A novel multi-modal incremental tensor decomposition for
anomaly detection in large-scale networks,” Inf. Sci., vol. 681, Oct. 2024,
Art. no. 121210.
[21] J. P. A. Maranhão, J. P. C. da Costa, E. Javidi, C. A. B. de Andrade,
and R. T. de Sousa Jr., “Tensor based framework for distributed denial
of service attack detection,” J. Netw. Comput. Appl., vol. 174, Jan. 2021,
Art. no. 102894.
[22] M. Wax and T. Kailath, “Detection of signals by information theoretic
criteria,” IEEE Trans. Acoust., speech, signal Process., vol. 33, no. 2,
pp. 387–392, Apr. 1985.
[23] G. Ke et al., “LightGBM: A highly efficient gradient boosting decision
tree,” in Proc. Adv. Neural Inf. Process. Syst., vol. 30, 2017, pp. 1–9.
[24] I. Sharafaldin, A. H. Lashkari, S. Hakak, and A. A. Ghorbani,
“Developing realistic distributed denial of service (DDoS) attack dataset
and taxonomy,” in Proc. Int. Carnahan Conf. Security. Technol. (ICCST),
2019, pp. 1–8.
[25] M. Tavallaee, E. Bagheri, W. Lu, and A. A. Ghorbani, “A detailed
analysis of the KDD CUP 99 data set,” in Proc. IEEE Symp. Comput.
Intell. Security. Defense Appl., 2009, pp. 1–6.
[26] Q. Guo, C. Zhang, Y. Zhang, and H. Liu, “An efficient SVD-based
method for image denoising,” IEEE Trans. Circuits Syst. Video Technol.,
vol. 26, no. 5, pp. 868–880, May 2016.
[27] A. Rajwade, A. Rangarajan, and A. Banerjee, “Image denoising using
the higher order singular value decomposition,” IEEE Trans. Pattern
Anal. Mach. Intell., vol. 35, no. 4, pp. 849–862, Apr. 2013.
[28] J. Xu, X. Li, P. Wang, X. Jin, and S. Yao, “Multi-modal noise-robust
DDoS attack detection architecture in large-scale networks based on
tensor SVD,” IEEE Trans. Netw. Sci. Eng., vol. 10, no. 1, pp. 152–165,
Jan./Feb. 2023.
[29] T. Chen and C. Guestrin, “XGBoost: A scalable tree boosting system,”
in Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data Min., 2016,
pp. 785–794.
[30] L. Prokhorenkova, G. Gusev, A. Vorobev, A. V. Dorogush, and A. Gulin,
“CatBoost: Unbiased boosting with categorical features,” in Proc. Adv.
Neural Inf. Process. Syst., vol. 31, 2018, pp. 6639–6649.
[31] G. S. Kushwah and S. T. Ali, “Detecting DDoS attacks in cloud
computing using ANN and black hole optimization,” in Proc. 2nd Int.
Conf. Telecommun. Netw. (TEL-NET), 2017, pp. 1–5.
[32] S. M. H. Bamakan, H. Wang, T. Yingjie, and Y. Shi, “An effective
intrusion detection framework based on MCLP/SVM optimized by timevarying chaos particle swarm optimization,” Neurocomputing, vol. 199,
pp. 90–102, Jul. 2016.
[33] T. Swamy, A. Zulfiqar, L. Nardi, M. Shahbaz, and K. Olukotun,
“Homunculus: Auto-generating efficient data-plane ml pipelines for
datacenter networks,” in Proc. 28th ACM Int. Conf. Archit. Support
Program. Lang. Oper. Syst., 2023, pp. 329–342.

298

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

Qiyuan Fan received the B.E. degree in computer
science and technology from the Wuhan University
of Technology, Wuhan, China. He is currently pursuing the master’s degree with the School of Software,
Yunnan University, Kunming, China. His current
research interests include big data, tensor network,
and reinforcement learning.

Xue Li received the B.E. degree in electronic and
information engineering from Zhengzhou University,
Zhengzhou, China, the M.E. degree in control engineering from the Wuhan University of Technology,
Wuhan, China. She is currently a Lecturer with
the School of Electronic Information Engineering,
Henan Institute of Technology, Xinxiang, China. Her
research interests include big data and electronic
information.

Puming Wang received the B.E. degree in communication engineering from Xidian University, Xi’an,
China, the M.E. degree in control engineering from
the Wuhan University of Technology, Wuhan, China,
and the Ph.D. degree from the School of Computer
Science and Technology, Huazhong University of
Science and Technology, Wuhan. He is currently an
Associate Professor with the School of Software,
Yunnan University, Kunming, China. His research
interests include big data, artificial intelligence, and
network security.

Xin Jin received the B.S. degree in electronics
and information engineering from Henan Normal
University, Xinxiang, China, and the Ph.D. degree
in communication and information systems from
Yunnan University, Kunming, China, where he is
currently an Associate Professor with the School
of Software. His research interests include pulse
coupled neural networks theory and its applications,
image processing, information fusion, optimization
algorithm, and bio-informatics.

Shaowen Yao received the B.S. and M.S. degrees
in telecommunication engineering from Yunnan
University, Kunming, China, and the Ph.D. degree in
computer application technology from the University
of Electronic Science and Technology of China,
Chengdu, China. He is currently a Professor with
the School of Software, Yunnan University. His
current research interests include neural network
theory and applications, cloud computing, and big
data computing.

Shengfa Miao (Member, IEEE) received the B.S.
and M.S. degrees in computer science and technology from Lanzhou University, Lanzhou, China,
and the Ph.D. degree in data mining from Leiden
University, Leiden, The Netherlands. He is currently
an Associate Professor with the School of Software,
Yunnan University, Kunming, China. His current
research interests include business risk control structural health monitoring and digital twin.

Sizhang Li received the B.E. degree from the
Internet of Things Engineering, Hunan Institute of
Engineering, Hengyang, China. She is currently
pursuing the master’s degree with the School of
Software, Yunnan University, Kunming, China. Her
current research interests include cloud computing
and big data security.

Min An received the B.S. degree in computer
science and technology from Northwest Minzu
University, Lanzhou, China. He is currently pursuing
the master’s degree with the School of Software,
Yunnan University, Kunming, China. His current
research interests include reinforcement learning,
time series forecasting, block chain technology, and
federated learning.

Jing Xu received the B.E. degree in mechanical
engineering from Hefei University, Hefei, China,
and the M.S. degree from the School of Software,
Yunnan University, Kunming, China. His current
research interests include cloud computing and big
data security.
PAPER_TEXT
