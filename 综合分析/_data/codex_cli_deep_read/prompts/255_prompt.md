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
# [255] MAG: A Novel Approach for Effective Anomaly Detection in Spacecraft Telemetry Data
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
编号：255
题名：MAG: A Novel Approach for Effective Anomaly Detection in Spacecraft Telemetry Data
年份：2023
DOI：10.1109/tii.2023.3314852
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2023.3314852.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测
相关性：弱相关，分数 2
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\255.txt
- 原始字符数：41863
- 本次发送字符数：41863
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 3, MARCH 2024

3891

MAG: A Novel Approach for Effective Anomaly
Detection in Spacecraft Telemetry Data
Bing Yu , Student Member, IEEE, Yang Yu , Senior Member, IEEE, Jiakai Xu , Gang Xiang ,
and Zhiming Yang , Senior Member, IEEE

Abstract—Anomaly detection is a crucial matter to ensure the spacecraft stability. During the spacecraft operation, sensors and controllers generate a large volume of
multidimensional time series telemetry data with long periodicity, and one key point to detect the anomaly inside
the spacecraft timely and precisely is to extract essential
features from the sheer amount of telemetry data. However, great challenges exist owing to the complex coupling
relationships and the temporal characteristics inside the
telemetry data. To address this issue, we propose a novel
approach called maximum information coefficient attention
graph network (MAG). The basic frame is a graph neural
network, which utilizes embedding vectors to describe the
intrinsic properties of each dimension, correlation analysis to investigate long-term dependencies, an attention
mechanism to determine short-term interactions among dimensions, and long short term memory (LSTM) to extract
temporal features. The fusion of these modules through a
graph neural network results in the construction of the MAG
model, allowing for a comprehensive analysis of complex
variable relationships and temporal characteristics leading to successful detection of various types of anomalies.
Since telemetry data has heterogeneous characteristics,
we adapt the loss function and design an unsupervised
anomaly scoring method suitable for MAG. To verify the
effectiveness of the proposed algorithm, we conducted experiments using two publicly and two new available spacecraft telemetry datasets, and the results demonstrate that
our algorithm is more efficient and accurate in detecting
spacecraft data anomalies than several other state-of-theart methods.
Index Terms—Anomaly detection, anomaly score, graph
neural network (GNN), multivariate time series, spacecraft
telemetry data.

Manuscript received 20 July 2023; revised 29 August 2023; accepted
6 September 2023. Date of publication 3 October 2023; date of current
version 23 February 2024. This work was supported in part by the
National Natural Science Foundation of China under Grant 62071150.
Paper no. TII-23-2687. (Corresponding author: Zhiming Yang.)
Bing Yu, Yang Yu, Jiakai Xu, and Zhiming Yang are with the School
of Electronics and Information Engineering, Harbin Institute of Technology, Harbin 150001, China (e-mail: yubing_hit@163.com; yuyanghit
@hit.edu.cn; 22B905048@stu.hit.edu.cn; yangzm@hit.edu.cn).
Gang Xiang is with the Department of System Engineering, Beijing
Aerospace Automatic Control Institute, Beijing 100854, China (e-mail:
Hit-xianggang@163.com).
Color versions of one or more figures in this article are available at
https://doi.org/10.1109/TII.2023.3314852.
Digital Object Identifier 10.1109/TII.2023.3314852

I. INTRODUCTION
NSURING the safety of spacecraft systems holds immense
importance due to their complexity and magnitude [1]. In
particular, even a minor malfunction can result in catastrophic
destruction of the spacecraft. Hence, early detection of anomalous behavior in the spacecraft system during the development
of a fault becomes critical to prevent it from exacerbating into a
catastrophic failure.
Due to the complexity of dimension interrelationships and
high-dimensional nature of spacecraft telemetry data, traditional
modeling techniques encounter challenges in anomaly detection.
As a result, data-driven methods that rely on telemetry data
have gained significant attraction [2]. Given that anomalies are
usually rare and few in number, unsupervised learning solely
using normal telemetry data to uncover inherent patterns holds
greater value. The key to anomaly detection using only normal telemetry data lies in extracting essential characteristics
of spacecraft normal operation states from multidimensional
time series data. However, due to the complex interrelationships
and temporal characteristics of telemetry data, this presents a
significant challenge.
In response to this challenge, numerous scholars have proposed various classic unsupervised anomaly detection models that have demonstrated excellent performance in various fields. These include local outlier factor (LOF) [3], oneclass support vector machine (OC-SVM) [4], and support
vector data description (SVDD) [5], etc. [6]. Moreover, conventional machine learning methods are insufficient to address the challenge of handling high-dimensional and largescale data. As artificial intelligence has developed, deep learning has increasingly addressed this issue [7]. For instance,
Su et al. [8] and Song et al. [9] proposed anomaly detection methods based on the GRU-VAE and ST-GAN, respectively. These methods exhibited solid performance on publicly
available datasets.
However, those previously mentioned are primarily designed
for Euclidean domain data with translational invariance, while
the telemetry data are better mapped to non-Euclidean domain
data, such as graph structures [10]. For this reason, graph neural
networks are well suited for telemetry data, where graph nodes
represent the features of variables within the detection window,
and graph edges describe the correlations between dimensions.
Indeed, Deng et al. [11] proposed a bias score-based anomaly
detection algorithm, and Xie et al. [12] suggested an anomaly

E

1551-3203 © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

3892

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 3, MARCH 2024

detection method that combines wavelet transform and graph
neural networks, both with commendable performance on industrial datasets.
Nonetheless, these methods above are not entirely suitable
for our problem. In the case of complex, multidimensional, and
time-sensitive telemetry data, it is vital to accurately capture
the intrinsic and temporal characteristics of each variable within
each detection window, while extensively examining their intricate nonlinear interdependencies. Furthermore, telemetry data
characterize long-period properties, making methods that rely
solely on short-term windows for extracting correlation capabilities insufficient. Moreover, telemetry data obtained from spacecraft systems contain two heterogeneous data types: analog and
state variables (analog variables are continuous and state variables are binary), which render a single loss function inadequate.
Based on the above analysis, this article proposes a novel
graph neural network framework. The inherent and temporal
characteristics of each variable are represented as nodes, while
the long-term association analysis and attention within the shortterm window are depicted as edges. Ultimately, the entirety of
the graph structure undergoes updates to finalize the anomaly
detection process. The main contributions and advantages of
our work are as follows.
1) This article aims to represent the effective features in the
telemetry data detection window from three angles: by
utilizing embedding vectors to describe the properties of
each dimension, demonstrating the relationships between
dimensions using graph structures, extracting temporal
features using LSTM, and fusing the various components
via a graph neural network.
2) To account for telemetry data’s long periodicity, this
article uses maximum information coefficient (MIC) to
investigate the long-term relationships of variables, an
attention mechanism to capture the short-term associations of windows, and ultimately combines both methods
to construct edges in the graph that represent the associations.
3) This article tackles the heterogeneity of telemetry data
along with the feature of edge fusion construction and puts
forward a novel loss function. Additionally, a threshold
score appropriate for the network structure is devised.
The rest of this article is organized as follows. Section II describes the problem of spacecraft system telemetry data anomaly
detection. Section III presents the overall framework of our
approach to anomaly detection. Section IV describes the proposed maximum information coefficient attention graph network
(MAG) algorithm in detail. The experimental results are reported
in Section V. Finally, Section VI concludes the article.
II. PROBLEM DESCRIPTION
The types of spacecraft telemetry data can be classified into
analog variables (e.g., piezoelectric voltages, acceleration quantities) and state variables (e.g., module control commands).
Anomalies are typically indicated as either outliers or subseries
of multiple telemetry variables in the telemetry data, encompassing point anomalies, shapelet anomalies, trend anomalies,

Fig. 1. Illustrative examples of anomalies in spacecraft telemetry data.
(a) Telemetry analog variables. (b) Telemetry of analog variables and
state variables.

contextual anomalies, and multiset anomalies. In Fig. 1(a),
there are inconsistencies in the periods among the variables.
Variable 1, in particular, exhibits a longer period that may
exceed the window length used for detection. This feature also
highlights the inadequacy of analyzing correlation solely within
the length of the detected time window. Thus, it is imperative to
conduct association analysis of the entire sequence. The anomaly
consisting of analog variables and state variables is shown in
Fig. 1(b). State 1 to State 4 are commands sent or received by the
console. During the anomaly interval, trend anomalies and point
anomalies were observed for the analog variables, which were
obtained by ground testers actively entering incorrect module
commands.
The method for achieving real-time anomaly detection involves utilizing sliding window data to make real-time predictions for multivariate time series, and then determining whether
the prediction results deviate excessively from the observed
values. If the deviation is too large, the prediction is deemed
to be anomalous. Defining X = {x(1) , x(2) , . . . , x(T ) } as the
original time series with time span T , x̂(T +1) as the forecast

YU et al.: MAG: A NOVEL APPROACH FOR EFFECTIVE ANOMALY DETECTION IN SPACECRAFT TELEMETRY DATA

3893

3) Graph Aggregation: The correlation coefficient matrix
and attention coefficient matrix are integrated as edges,
while the time feature nodes and embedding vectors are
incorporated as node features to construct a graph. Subsequently, the entire network is aggregated and updated
through iterative processes.
4) Anomaly Evaluation: Ultimately, the MAG network predicts the next variable value and compares it with the
observed value, generating an error score. This score is
then used to determine the presence of abnormalities.
IV. DETAILS OF THE PROPOSED METHOD
A. Data Preprocessing

Fig. 2.

Overview of the proposed framework.

value of this time series at the moment T + 1 after the model,
and x(T +1) as the true telemetry value at the moment T + 1,
then whether it is anomalous can be expressed by



 (T +1)
(1)
− x̂(T +1)  > τ
x
where  •  denotes the rule to calculate the deviation between
x̂(T +1) and x(T +1) , τ is a predefined anomaly threshold. The
larger the deviation between x̂(T +1) and x(T +1) , the higher the
anomaly probability of x(T +1) . As shown by the anomalies of
the data in Fig. 1, the key to problem is to find the temporal and
variable correlations of the data. We propose the model MAG
to solve this problem and predict x̂(T +1) , and propose a new
formula to find the threshold τ .
III. PROPOSED FRAMEWORK
The proposed MAG framework aims to capture the correlation
and temporal characteristics among telemetry data variables,
integrating them into a graph. Subsequently, the framework
utilizes the aggregated updates from the graph to predict future
variable outcomes and detect anomalies by comparing them with
the observed values.
The overall structure of the proposed framework is shown in
Fig. 2. It consists of the following four main parts.
1) Variable Correlation Analysis: The telemetry data obtained from the spacecraft system are analyzed using the
MIC algorithm to obtain the correlation coefficient matrix, reflecting the correlations between variables during
normal working conditions.
2) Temporal Analysis and Attention Mechanism: The data
are subjected to sliding window segmentation. LSTM
is employed to extract temporal features from the windowed time series, while employing embedding vectors
to capture the inherent attributes of each dimension. The
attention mechanism is utilized to obtain the attention
coefficient matrix.

Partitioning the multivariate telemetry data is imperative
for real-time calculations, which requires the establishment of
real-time calculation detection windows. First, split multivariate
telemetry data Φ ⊂ RT ×N . The data have a total length of
T , consist of N variables, a set of training data is denoted
Φtrain ⊆ RT1 ×N , and a set of test data is denoted Φtest ⊆ RT2 ×N .
Note that all the data points in the training data set must be
normal.
Next, the training dataset Φtrain ⊆ RT1 ×N is segmented into
i
, i = 1, 2, . . . , m} ⊆
a series of subsequences Xtrain = {Xtrain
Sw ×N
i
by a sliding window, where Xtrain
means Xt−sw :t when
R
the window size is set to sw . Given step length st , the number
of subsequences can be calculated by m = (T1 − sw )/st  + 1.
Similarly, the testing dataset Φtest ⊆ RT2 ×N is divided into subj
, j = 1, 2, . . . , n} by a sliding window,
sequences Xtest = {Xtest
where n = (T2 − sw )/st  + 1. For validation purposes, each
point in the test dataset is marked with a binary number (0 for
normal and 1 for abnormal).
B. Variable Correlation Analysis
Due to the inconsistent periodic nature of telemetry variables,
the data detection window cannot cover the entire period. It is
necessary to perform correlation analysis on the original training
data before sliding the data window. The MIC [13] is an effective
method for measuring the correlation between two variables.
For a given training dataset Φtrain ⊆ RT1 ×N , for any two
discrete variables with T1 elements, the MIC values between
A = {ai | i = 1, . . . , T1 } and B = {bi | i = 1, . . . , T1 } can be
obtained by the following equation:

p(a, b)
(2)
p(a, b) log
M I(A, B) =
p(a)p(b)
a∈A b∈B

where p(a, b) is the joint probability density of variables a
and b, and p(a) and p(b) are the marginal probability densities
of variables a and b, respectively, computed by the histogram
estimation method.
For a finite set D = {(ai , bi ), i = 1, . . . , n}, given a grid G,
we can partition the ai values of D into the a bin and the bi
values of D into the b bin. The MIC is given by
M I ∗ (D, x, y) = max M I(D | G)

(3)

MIC(D) =

(4)

max

xy<B(T1 )

{M (D)x,y } .

3894

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 3, MARCH 2024

The maximum information coefficient is the highest normalized M I value obtained in the feature matrix. where ω(1) <
B(T1 ) < O(T11−ε ) and 0 < ε < 1. In general, MIC works well
in practice when B(T1 ) = T10.6 . After the calculation, the MIC
values between N telemetry variables and the correlation matrix M can be obtained. mij denotes the correlation between
telemetry variable i and telemetry variable j, and it has a value
between 0 and 1.
C. MAG Model
During the training phase, each telemetry variable within
a time window exhibits both temporal and intrinsic property
features. Representing the intrinsic properties of each telemetry
variable using embedding vectors enables subsequent feedback,
performance differentiation, and updates. Moreover, the attention mechanism can be employed to express the relationships between variables within the window more effectively. Therefore,
we introduce an embedding vector for each telemetry variable
to represent its features vi ∈ Rd , for i ∈ {1, 2, . . . , N }. These
embeddings are randomly initialized and then trained together
with the rest of the model. The similarity between these embeddings vi represents the intrinsic properties of the telemetry
variables.
In the MAG model, for a subseries combination of Xtrain or
Xtest , define the model input as the historical subseries data
x(t) := [x(t−w) , x(t−w+1) , . . . , x(t−1) ] for a sliding window of
size w at time t. The calculation of the attention coefficient αi,j
is as follows:
 


(t)
(t)
⊕ vi ⊕ W xi
(5)
π(i, j) = ReL U vi ⊕ W xi
αi,j = 

exp(π(i, j))
.
k∈N (i)∪{i} exp(π(i, k))

(6)

After computing the attention coefficient αi,j , it is combined
with the correlation coefficient mij to form each edge eij and
construct adjacency matrix E
eij = αi,j · mij .

(7)

Following the construction of the edges, we employ LSTM
technique to extract temporal association features. x(t) is subjected to LSTM network to extract the temporal features. Temporal features can be extracted through the LSTM network denoted
as


y (t) := y (t−w) , y (t−w+1) , . . . , y (t−1) .
(8)
Finally, a graph neural network is employed to integrate the
temporal and spatial associations within the subsequence. The
constructed graph model utilizes the previously mentioned ei,j
to form the adjacency matrix. The temporal feature y (t) is used
as input for the graph neural network, enabling the aggregation
and update of information from each node and its neighbors,
(t)
ultimately producing the output of node i represented z i as
follows:
⎞
⎛

(t)
(t) (t)
(t) (t)
z i = ReL U ⎝ei,i W i y i +
ei,j W j y j ⎠ (9)
j∈N (i)

(t)

where y i ∈ Rw is the temporal input feature of node i, N (i) =
{j | eij > 0} is the set of neighbors to node i, and W ∈ Rd×w
is the trainable weight matrix of the shared linear transformation
for each node.
From the above feature extractor, we obtain a representation
(t)
(t)
(t)
of all N nodes as {z 1 , . . . , z N }. For each z i , we multiply it
by the proceeding elements of the corresponding time series of
embedding vi (denoted as ◦). Then, we use the results across all
nodes as input to a stacked fully connected layer with output dimension N to predict the vector of telemetry values at time step t


(t)
(t)
.
(10)
x̂(t) = fθ v 1 ◦ z 1 , . . . , v N ◦ z N
The predicted output of the model is denoted as x̂(t) . We
denote the analog variables and state variables described in
(t)
(t)
Section II as xa and xs , respectively. Considering the heterogeneity between these two types, different loss functions
are adopted. The analog variables utilize mean square error,
(t)
minimizing the discrepancy between the predicted output x̂a
(t)
and the observed data xa . On the other hand, for state variables,
binary cross-entropy loss is used. In order to mitigate overfitting
and to ensure appropriate sizing of the final edges within the
sliding window, we introduce a constraint term. This term takes
into account the acyclicity of the corresponding graph [14], and
incorporates the findings of correlation analysis. The final loss
function is as follows:
LMSE =

Na 
2
1 
 (t)
(t) 
x̂ai − xai 
2
Na i=1

Ns 
1 
(t)
(t)
x log x̂si
Ns i=1 si




(t)
(t)
+ 1 − xsi log 1 − x̂si


h(E) = tr eE◦E − tr eM ◦M
c
Ltotal = LMSE + LBCE + λh(E) + |h(E)|2
2

(11)

LBCE = −

(12)
(13)
(14)

where λ and c represent Lagrangian multipliers and penalty parameters, and are solved by augmented Lagrangian method [15].
Ns represents the dimensionality of the state variables, and
Na represents the dimensionality of the analog variables. The
network structure of the MAG is shown in Fig. 3.
D. Abnormal Scores
After the graph structure is acquired by the network, detection
of the anomalies that deviate from normal patterns is the next
step. The model achieves this by computing separate outliers
for each telemetry and then amalgamating them into a solitary
outlier per timestamp. Since our detection algorithm chooses
an MAG-based model, it is also necessary to design outlier
determination rules specifically based on the characteristics of
that model. The anomaly score compares the expected behavior
at moment t with the observed behavior and calculates the error

YU et al.: MAG: A NOVEL APPROACH FOR EFFECTIVE ANOMALY DETECTION IN SPACECRAFT TELEMETRY DATA

Fig. 3.

3895

Overall architecture of the proposed MAG anomaly detection algorithm.

value Err(t) between moment t and the true telemetry value
Err(t) =

Ns 
Na 


1 
1 
 (t)
 (t)
(t) 
(t) 
xsi − x̂si  +
xai − x̂ai  . (15)
Ns i=1
Na i=1

In order to prevent any one telemetry value from producing
a deviation too high above the other telemetry values, we normalize the error value Err(t) for each telemetry value to obtain
a(t).
In the threshold selection part, to avoid introducing additional
hyperparameters, we propose in our experiments a method that is
more computationally convenient. By calculating the deviation
atrain (t) of each timestamp on the training set, we can calculate
the threshold value by the following equation to obtain:
 1

τ = max cv2 (atrain (t) − μ̃)
(16)
cv =

μ̃
σ̃

(17)

where cv is the coefficient of variation, which is a statistical
measure of the degree of variation in the telemetry data. μ̃ and
σ̃ are the median and interquartile range (IQR) of the values
atrain (t), respectively. We use the median and IQR instead of
the mean and standard deviation needed in the coefficient of
variation because they do not assume data distribution and are
more robust to the exception scores of the model. Finally, if the
Err(t) of the test set exceeds any fixed threshold τ , then time t
is marked as an exception.
Many published anomaly detection algorithms [16] use the 3σ
algorithm and the peak over threshold (POT) algorithm to mine
the threshold τ . POT is a threshold mining method using extreme

value theory, which assumes that the peaks in the time series
satisfy the generalized Patoli distribution (GPD). Nonetheless,
the suitability of the POT method may be limited when the
distribution characteristics of the data are at variance with the
GPD. For telemetry data of spacecraft systems, the experiments
in the next section show that our approach is more adaptable.
The process of the MAG-based model algorithm is shown in
Algorithm 1.
V. EXPERIMENTS
A. Datasets and Performance Index
We conducted experiments on two new telemetry datasets
and two public datasets. The two new datasets, SCC-1 and
SCC-2, come from the telemetry data of two different satellite
systems. The two public telemetry datasets are provided by
NASA for the Soil Moisture Active Passive (SMAP) satellite
and the Mars Science Laboratory (MSL) rover [17]. The details
of four datasets are shown in Table I. For these datasets, normal
data points are marked as 0 and outliers are marked as 1. Then,
10% of the training dataset is divided for the validation dataset.
Note that the training dataset contains only normal time series.
We use commonly used metrics to evaluate the performance of
our proposed MAG algorithm, which are Precision, Recall, and
F1 score
TP
TP + FP
TP
Recall =
TP + FN

Precision =

(18)
(19)

3896

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 3, MARCH 2024

Algorithm 1: Calculate MAG-Based Model.
Variable Correlation Analysis:
The training dataset Φtrain is calculated using MIC
analysis to obtain the correlation coefficient matrix M .
Train Stage:
for lth epoch in train epochs do
1. The attention mechanism applied to the fused the
subsequence Xtrain and node embedding vector Vtrain
to obtain attention coefficient matrix Att, which is
combined with M to get edges E.
2. Compute the temporal feature Ytrain of Xtrain .
3. Ytrain and E are fed into the graph neural network for
message passing, node aggregation, and node update to
calculate output Ztrain .
4. Multiply Ztrain and Vtrain point by point to get
X̂train and calculate LM SE and LBCE to get Ltotal .
5. Update the parameters in the neural network by Ltotal .
end for
Threshold Calculation:
i
in Xtrain do
for Xtrain
Utilize the real value x(t) and the trained network to
compute the predicted value x̂(t) and the error Err(t).
end for
Normalize Err(t) to get a(t) and calculate the anomaly
threshold τ .
Testing Stage:
i
in Xtest do
for Xtest
1. Utilize the real value x(t) and the trained network to
compute the predicted value x̂(t) and the error Err(t).
2.The outlier value is obtained by making a difference
comparison with the threshold τ .
end for

2 · Recall · Precision
Recall + Precision

tuning strategy [19], [20]: if a certain time point in a continuous
anomaly segment is detected, all anomalies in that segment are
considered to be correctly detected. Based on the observation
that the time point of the anomaly will raise an alert and further
make the whole segment noticed in realistic applications, this
strategy is reasonable. We implemented our approach and its
variants in PyTorch [21] version 1.9.1 using CUDA 11.6 and
PyTorch Geometric Library [22]. We set the training model to
100 cycles and used 10 as an early stop. To obtain reliable
results and reduce the randomness of the training phase, the
samples were trained and tested ten times separately, and then the
standard deviation of the performance metrics was calculated.
Finally, our algorithm is trained and tested on a server with
Intel(R) Xeon(R) CPU E5-2690 v4 @ 2.60 GHz and NVIDIA
RTX 3090 graphics card.
C. Results and Comparisons

TABLE I
DETAILS OF DATA

F1 =

Fig. 4. Relationship between F1 scores and window length for the four
datasets.

(20)

where T P is the number of predicted actual anomalies, F P is
the number of the false positive samples, and F N is the number
of the false negative samples.
B. Experimental Settings and Platform
In the data preprocessing stage, we set the window size
sw = 50 and the step size st = 1, and then split the original time
series into the desired subsequences. In the network structure,
we set the embedding vector dimension to 128 and set the hidden
layer to 128. We are utilizing the Adam optimizer [18] with a
learning rate of 1 × 10−3 to train the model. We use a widely used

1) Window Size: To determine the appropriate window size
Sw , we conducted experiments on three datasets by selecting a
portion of small datasets. The window sizes were set to 20, 30,
50, 80, 100, 150, and 200.
The F1 scores for the four datasets are depicted in Fig. 4.
Opting for an excessively long window can result in redundant
information, slow response, and increased computational complexity. Conversely, selecting a window length that is too short
will result in an inadequate capture of temporal features, leading
to insufficient stability. The experimental results from the four
small datasets imply that a window length of 50 is optimal.
2) Baseline Comparison: To exhibit the effectiveness of our
proposed algorithm, we conduct a comparative analysis of its
performance with other benchmark unsupervised anomaly detection algorithms. These include deep learning based models such as AnomalyTransformer [19], ST-GAN [9], InterFusion [23], GDN [11], and GRU-VAE [8]; clustering-based techniques such as Deep-SVDD [24]; as well as classical methods
such as OC-SVM [25] and IsolationForest [26]. Notably, STGAN and AnomalyTransformer represent the most sophisticated
deep models. We evaluate the average Precision, Recall, and
F1-score after ten rounds on the SCC-1, SCC-2, SMAP, and

YU et al.: MAG: A NOVEL APPROACH FOR EFFECTIVE ANOMALY DETECTION IN SPACECRAFT TELEMETRY DATA

3897

TABLE II
QUANTITATIVE RESULTS OF MAG (OURS) ACROSS FOUR REAL TELEMETRY DATASETS. HEREIN, P, R, AND F1 SIGNIFY
THE PRECISION, RECALL, AND F1-SCORE, RESPECTIVELY

TABLE III
RESULTS OF ABLATION AND COMPARISON EXPERIMENTS

MSL datasets. The comparative results of the four algorithms
are showcased in Table II.
According to Table II, our methodology attains the highest
F1 scores across all four datasets, demonstrating optimal
performance in balancing false alarm and missed alarm rates.
Moreover, our approach exhibits the most satisfactory results
in recall rate on the SCC-1 and SMAP datasets, indicating
a minimal likelihood of producing false alarms on these two
datasets.
3) Ablation Comparison: To investigate the necessity of each
component of our method, we gradually excluded and substituted these components and monitored how the model performance degraded. The experimental results are shown in Table III.
To compare the effectiveness of the edge mechanism, we
conducted separate experiments by eliminating either the correlation analysis or attention mechanism. The experiment showed
that the fusion of both mechanisms yielded the most favorable
outcome, as the introduction of the attention mechanism after the
correlation analysis effectively enhances the model’s adaptability. However, solely relying on the attention mechanism and the
data within the window is inadequate for effectively capturing
the extent of correlation and dependency over prolonged periods.

Furthermore, we used the Pearson and Spearman methods [27] for comparing correlations. The experimental results
indicate that the MIC outperforms the Pearson and Spearman
correlation coefficients. This discrepancy arises because the
Pearson and Spearman correlation coefficients assume linear
correlation, causing inaccuracies when analyzing nonlinear relationships. On the contrary, MIC does not rely on such assumptions and can accurately capture both linear and nonlinear
correlations over extended periods.
Regarding the temporal relationship analysis, we compared
linear, RNN, and GRU layer connections [28], using ablation
experiments. The findings indicate that employing the network
layer or a linear layer results in less effectiveness, primarily due
to the inability to extract temporal features. In contrast, incorporating layer connections of RNN, GRU, or LSTM yields more
effective findings. Specifically, LSTM, with a more intricate and
robust structure than GRU and RNN, provides better control over
the flow of information and enables the capture of long-term
dependencies. Therefore, LSTM can extract superior temporal
features, resulting in better outcomes.
As for the loss function, we applied the mean squared error
(MSE) and mean absolute error (MAE) [29] and compared

3898

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 3, MARCH 2024

Fig. 5. Illustrative relationship between threshold and F1 score.
(a) MSL dataset. (b) SMAP dataset. (c) SCC-1 dataset. (d) SCC-2
dataset.

them with our method. Experimental findings demonstrate that
employing two mixed loss functions for two different types of
data can significantly enhance the model’s effectiveness.
4) Threshold Comparison: We also evaluated the impact of
the threshold value τ on the F1-score of the four datasets. As
shown in Fig. 5, when the threshold is too small, the Recall
value will be low, resulting in a decreased F1-score. While if
the threshold is set too high, the Precision value will decrease,
causing a drop in F1-score. Therefore, it is crucial to set the
threshold appropriately to ensure the optimal F1-score.
We conducted a comparison between two thresholding methods: 3σ thresholding based on the Gaussian distribution and
extreme value theory thresholding (EVT). The impact of these
thresholds on the F1 scores of the four test datasets is illustrated
in Fig. 5. The results reveal that, as the threshold (τ ) increases,
the F1 score initially reaches its peak and then declines. Our
proposed thresholding method closely approximates the optimal
threshold acquired through exhaustive search, thus demonstrating the effectiveness of our anomaly threshold determination
rule. This is likely because the 3σ thresholding and EVT methods
both assume prior data distributions which are not applicable to
telemetry data. Conversely, our method, which employs formulas utilizing the median and interquartile range, is more robust
and unaffected by the shape of the data distribution.
VI. CONCLUSION
This article proposed a telemetry data anomaly detection
algorithm based on the MAG structural model. Specifically,
the algorithm constructed a graph-structured model that used
embedding vectors to describe the intrinsic properties of each
dimension, correlation analysis to investigate long-term dependencies, an attention mechanism to determine short-term
interactions among dimensions, and LSTM to extract temporal

features. Finally, by fusing these modules through a graph neural
network, the model effectively integrated the coupling relationships between the dimensions and temporal characteristics of
these sequences, allowing for the successful detection of various
types of anomalies. To determine anomalies, an anomaly score
adapted to the network structure was introduced.
To ascertain the effectiveness and superiority of our proposed
anomaly detection algorithm, we conducted experiments on four
genuine telemetry datasets and compared our approach with
other state-of-the-art algorithms, achieving the optimal results.
Moreover, the ablation experiments provided further evidence
of the effectiveness of our model components. Our proposed
anomaly thresholds showcase superior accuracy and closely
approximate the optimum thresholds when compared to other
widely used techniques.
However, although it does not affect the efficiency of real-time
anomaly detection, the computational cost increased with the increase in data volume during the computation of correlation analysis, warranting optimization of the computational efficiency
of MIC. Additionally, investigating more MAG-based anomaly
detection algorithms for various anomaly types and advancing
into fault diagnosis presented promising research topics.
REFERENCES
[1] J. Marzat, H. Piet-Lahanier, F. Damongeot, and E. Walter, “Model-based
fault diagnosis for aerospace systems: A survey,” Proc. Inst. Mech. Engineers, Part G: J. Aerosp. Eng., vol. 226, no. 10, pp. 1329–1360, 2012.
[2] X. Dai and Z. Gao, “From model, signal to knowledge: A data-driven
perspective of fault detection and diagnosis,” IEEE Trans. Ind. Informat.,
vol. 9, no. 4, pp. 2226–2238, Nov. 2013.
[3] Z. Cheng, C. Zou, and J. Dong, “Outlier detection using isolation forest
and local outlier factor,” in Proc. Conf. Res. Adaptive Convergent Syst.,
2019, pp. 161–168.
[4] S. M. Erfani, S. Rajasegarar, S. Karunasekera, and C. Leckie, “Highdimensional and large-scale anomaly detection using a linear oneclass svm with deep learning,” Pattern Recognit., vol. 58, pp. 121–134,
2016.
[5] J. Yi and S. Yoon, “Patch SVDD: Patch-level SVDD for anomaly detection
and segmentation,” in Proc. Asian Conf. Comput. Vis., 2020, pp. 375–390.
[6] S. Omar, A. Ngadi, and H. H. Jebur, “Machine learning techniques for
anomaly detection: An overview,” Int. J. Comput. Appl., vol. 79, no. 2,
pp. 33–41, 2013.
[7] X. Zhou, Y. Hu, W. Liang, J. Ma, and Q. Jin, “Variational LSTM enhanced
anomaly detection for industrial Big Data,” IEEE Trans. Ind. Informat.,
vol. 17, no. 5, pp. 3469–3477, May 2021.
[8] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 2828–2837.
[9] J. Yu, Y. Song, D. Tang, D. Han, and J. Dai, “Telemetry data-based
spacecraft anomaly detection with spatial-temporal generative adversarial
networks,” IEEE Trans. Instrum. Meas., vol. 70, 2021, Art. no. 3515209.
[10] N. A. Asif et al., “Graph neural network: A comprehensive review on
non-euclidean space,” IEEE Access, vol. 9, pp. 60588–60606, 2021.
[11] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 4027–4035.
[12] L. Xie, D. Pi, X. Zhang, J. Chen, Y. Luo, and W. Yu, “Graph neural
network approach for anomaly detection,” Measurement, vol. 180, 2021,
Art. no. 109546.
[13] J. B. Kinney and G. S. Atwal, “Equitability, mutual information, and
the maximal information coefficient,” Proc. Nat. Acad. Sci., vol. 111,
pp. 3354–3359, 2013.
[14] X. Zheng, B. Aragam, P. Ravikumar, and E. P. Xing, “Dags with no tears:
Continuous optimization for structure learning,” in Proc. Adv. Neural Inf.
Process. Syst., 2018, pp. 9492–9503.

YU et al.: MAG: A NOVEL APPROACH FOR EFFECTIVE ANOMALY DETECTION IN SPACECRAFT TELEMETRY DATA

[15] E. Dai and J. Chen, “Graph-augmented normalizing flows for anomaly detection of multiple time series,” in Proc. Int. Conf. Learn. Representations,
2022, pp. 1–16.
[16] T.-W. Weng et al., “Evaluating the robustness of neural networks: An extreme value theory approach,” in Proc. Int. Conf. Learn. Representations,
2018, pp. 1–18.
[17] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Söderström, “Detecting spacecraft anomalies using LSTMs and nonparametric
dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, 2018, pp. 387–395.
[18] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
in Proc. Int. Conf. Learn. Representations, 2014, pp. 1–15.
[19] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time series
anomaly detection with association discrepancy,” in Proc. Int. Conf. Learn.
Representations, 2021, pp. 1–20.
[20] L. Shen, Z. Li, and J. Kwok, “Timeseries anomaly detection using temporal
hierarchical one-class network,” in Proc. Adv. Neural Inf. Process. Syst.,
2020, pp. 13016–13026.
[21] A. Paszke et al., “PyTorch: An imperative style, high-performance
deep learning library,” in Proc. Adv. Neural Inf. Process. Syst., 2019,
pp. 8026–8037.
[22] M. Fey and J. E. Lenssen, “Fast graph representation learning with PyTorch
geometric,” in Proc. Int. Conf. Learn. Representations Workshop Graphs
Manifolds, 2019, pp. 1–9.
[23] Z. Li et al., “Multivariate time series anomaly detection and interpretation
using hierarchical inter-metric and temporal embedding,” in Proc. 27th
ACM SIGKDD Conf. Knowl. Discov. Data Mining, 2021, pp. 3220–3230.
[24] L. Ruff et al., “Deep one-class classification,” in Proc. Int. Conf. Mach.
Learn., 2018, pp. 4393–4402.
[25] D. M. J. Tax and R. P. W. Duin, “Support vector data description,” Mach.
Learn., vol. 54, pp. 45–66, 2004.
[26] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. IEEE
8th Int. Conf. Data Mining, 2008, pp. 413–422.
[27] R. Eisinga, M. T. Grotenhuis, and B. Pelzer, “The reliability of a two-item
scale: Pearson, Cronbach, or Spearman-Brown?,” Int. J. Public Health,
vol. 58, pp. 637–642, 2013.
[28] A. Sherstinsky, “Fundamentals of recurrent neural network (RNN) and
long short-term memory (LSTM) network,” Physica D: Nonlinear Phenomena, vol. 404, 2018, Art. no. 132306.
[29] D. Chicco, M. J. Warrens, and G. Jurman, “The coefficient of determination
R-squared is more informative than SMAPE, MAE, MAPE, MSE and
RMSE in regression analysis evaluation,” PeerJ Comput. Sci., vol. 7, 2021,
Art. no. e623.

Bing Yu (Student Member, IEEE) received the
B.S. degree in electronics and information technology in 2020 from the Harbin Institute of Technology, Harbin, China, where he is currently
working toward the Ph.D. degree in information
and communication engineering.
His current research interests include fault diagnosis, anomaly detection, and deep learning
algorithms for electronic systems.

3899

Yang Yu (Senior Member, IEEE) received the
B.S., M.S., and Ph.D. degrees in instrument science and technology from the Department of
Automatic Test and Control, Harbin Institute of
Technology, Harbin, China, in 2002, 2004, and
2008, respectively.
She is currently a Professor with the Department of Test and Control Engineering, School
of Electronics and Information Engineering, HIT.
From 2015 to 2016, she was a Visiting Scholar
with Duke University, Durham, NC, USA. She
holds more than 30 granted China patents and has authored more than
50 publications in major journals and conference proceedings on electronic test technology. Her current research interests include automatic
testing, test technology for 3-D ICs, and diagnostic and prognostics for
electronics and electrical systems.
Jiakai Xu was born in Harbin, Heilongjiang
Province, China, in 2000. He received the B.S.
degree in measurement Science and Technology in 2022 from the School of Instrumentation,
Harbin Institute of Technology, Harbin, China,
where he is currently working toward the Ph.D.
degree in information and communication engineering.
His current research interests mainly include
abnormal detection, neural networks, and domain adaptation.

Gang Xiang received the B.Sc. and M.Sc. degrees from the Harbin Institution of Technology,
Harbin, China, in 2009 and 2011, respectively,
both in automatic test and control.
Since 2011, he has been a Senior Engineer
with the Beijing Aerospace Automatic Control
Institute, Beijing, China. His current research interests include deep learning, intelligent control,
fault diagnosis, and PHM.

Zhiming Yang (Senior Member, IEEE) received
the B.S., M.Sc., and Ph.D. degrees in instrument
science and technology from the Department of
Automatic Test and Control, Harbin Institute of
Technology, Harbin, China, in 2002, 2004, and
2009, respectively.
He is currently an Associate Professor with
the Department of Test and Control Engineering, School of Electronics and Information Engineering, HIT. From 2016 to 2017, he was a
Visiting Scholar with Arizona State University,
Tempe, AZ, USA. He holds more than ten granted China patents and
has authored more than 20 publications in major journals and conference proceedings on electronic test technology. His current research interests include automatic test technologies, diagnosis, and fault-tolerant
control approach for electronic systems
PAPER_TEXT
