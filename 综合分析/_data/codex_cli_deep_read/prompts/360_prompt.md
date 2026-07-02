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
# [360] ALAD: A New Unsupervised Time Series Anomaly Detection Paradigm Based on Activation Learning
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
编号：360
题名：ALAD: A New Unsupervised Time Series Anomaly Detection Paradigm Based on Activation Learning
年份：2024
DOI：10.1109/tbdata.2024.3453762
来源：IEEE Transactions on Big Data
PDF：paper/10.1109_TBDATA.2024.3453762.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测、时序、日志、KPI 与云原生异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\360.txt
- 原始字符数：61338
- 本次发送字符数：61338
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON BIG DATA, VOL. 11, NO. 3, MAY/JUNE 2025

1285

ALAD: A New Unsupervised Time Series Anomaly
Detection Paradigm Based on Activation Learning
Fengqian Ding , Bo Li, Xianye Ben , Senior Member, IEEE, Jia Zhao , and Hongchao Zhou

Abstract—Time series anomaly detection has been received
growing interest in industrial and academic communities due to its
substantial theoretical value and practical significance in reality.
Recent advanced methods for time series anomaly detection are
based on deep learning techniques, since they have shown their
superiority in some specific situations. However, most existing
deep learning-based anomaly detection methods require predefined, specific tasks of reconstruction or prediction, necessitating
task-specific loss functions. Designing such anomaly-aware loss
functions poses a significant challenge due to the ambiguity in
defining ground-truth anomalies. Moreover, these methods often rely on complex network architectures that tend to lead to
over-generalization, resulting in even abnormal data being well
reconstructed or fitted. To mitigate this situation, grounded in
activation learning theory, we propose a novel unsupervised time
series anomaly detection paradigm termed ALAD. ALAD utilizes a
straightforward fully connected network architecture, measuring
the typicality of input patterns through the sum of the squared
output. Despite its simplicity, ALAD achieves competitive performance compared to state-of-the-art models trained using backpropagation. By utilizing various real-world and synthetic datasets,
experimental results have confirmed the effectiveness and feasibility of the proposed paradigm. This work also demonstrates that
biologically-plausible local learning can sometimes outperform
backpropagation in real-world scenarios.
Index Terms—Anomaly detection, time series
biologically-plausible learning, unsupervised learning.

analysis,

I. INTRODUCTION
ITH the rapid developing of modern technologies, data
from various fields such as finance, economics and finance are recorded as time series data, and thus there is a growing
interest in modeling and exploring time series data. Wherein,

W

Received 23 May 2023; revised 13 July 2024; accepted 22 August 2024.
Date of publication 3 September 2024; date of current version 15 May 2025.
This work was supported in part by the the National Key Research and Development Program of China under Grant 2021YFB2800300, in part by the
National Natural Science Foundation of China under Grant 62322111 and
Grant 62271289, in part by the Natural Science Fund for Outstanding Young
Scholars of Shandong Province under Grant ZR2022YQ60, in part by the
Research Fund for the Taishan Scholar Project of Shandong Province under
Grant tsqn202306064, in part by Shenzhen Science and Technology Program
under Grant JCYJ20230807094000001, in part by Jinan “20 Terms of New
Universities” Funding Project under Grant 202333035, and in part by the Fundamental Research Funds for the Central Universities under Grant 2022JC017.
Recommended for acceptance by S. Ma. (Corresponding authors: Hongchao
Zhou; Xianye Ben.)
The authors are with the School of Information Science and Engineering,
Shandong University, Qingdao 266237, China (e-mail: wygtsmile1020
@gmail.com; 202212656@sdu.edu.cn; benxianye@gmail.com; zhaojia
@sdu.edu.cn; hongchao@sdu.edu.cn).
Digital Object Identifier 10.1109/TBDATA.2024.3453762

time series anomaly detection as the classic problem has been
widely studied by researchers, which has provided necessary
technique guarantees for diversified application scenarios, such
as industrial Internet, Internet of Things and distributed computing, etc [1], [2], [3]. Effective anomaly detection in time series
data can enhance the robustness, reliability, and performance of
various systems and processes by providing insights into underlying patterns and trends. This can inform decision-making,
optimize resource allocation, and lead to increased efficiency,
reduced costs, and improved overall functionality [4].
Time series anomaly detection is the process of identifying
unusual, unexpected patterns or behaviors in time series data.
It involves developing models that can automatically detect unusual patterns or events in time series data, which may be caused
by various factors such as errors in data collection, changes in the
underlying system dynamics, or external disturbances. Most of
the existing advanced anomaly detection methods are based on
deep learning models, which typically adopt reconstruction or
forecasting-based models and perform anomaly detection based
on the deviation errors between real values and reconstruction
or forecasting results [5]. For reconstruction-based models, the
autoencoder architecture is usually applied. For instance, Kieu
et al. [6] proposed an RNN-based autoencoder framework for
time series anomaly detection, since recurrent neural network
had been shown to be effective for time series modeling. Li et
al. [7] present a temporal convolutional network autoencoder,
and performed anomaly detection based on the reconstruction
error. For forecasting-based models, Deng et al. [8] applied a
graph neural network as the predictor, and used the deviation
between the predicted value and the true value as the anomaly
criterion. Wu et al. [9] proposed a long short-term memory
(LSTM) based anomaly detection method, which was built
on normal time series and detected anomalies by utilizing the
predictive error for the Gaussian Naive Bayes model.
Although these deep learning-based models have shown their
superiority in some specific situations, they inherently suffer
from the limitations associated with the following techniquespecific challenges. First, these methods generally assume the
models will fail to reconstruct or forecast the anomalous samples, since they are trained only using normal samples. However,
this assumption does not always holds in time series data, since
these methods mainly focus on the quality of reconstruction
or forecasting. This may leads to an over-generalization [10]
of model, thus it would cause even abnormal data to be well
reconstructed or fitted [11]. Second, these tailored anomaly
detection models are typically more complicated than the

2332-7790 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

1286

conventional neural network models. Furthermore, the core
algorithm for training deep learning-based anomaly detection
methods is backpropagation (BP), which requires predefining a
task-specsific loss function between the outputs of network and
expectations. However, designing anomaly-aware loss functions
poses significant challenges due to the ambiguity of defining
ground-truth anomalies [12]. Additionally, the training procedure for these elaborate models demands additional resources for
gradient computations and storage, which limits their applicability in resource-limited scenarios. Third, the training data from
real-world sources are often unbalanced with limited labeled
anomalies, and most of them exhibit diverse or even unseen
patterns that are not known as a priori. Due to these constraints,
how to develop a new paradigm for time series anomaly detection
is still an open problem.
In this work, we address the challenging problems of time
series anomaly detection by developing a simple yet promising architecture termed ALAD (Activation Learning based
Anomaly Detection). It does not rely on complicated network
architectures or any additional mechanisms, such as contrastive
learning [13], [14] or adversarial learning [15], yet can achieve
promising unsupervised time series anomaly detection performance simply by a fully connected network architecture.
ALAD is built upon the core of activation learning [16], a
new learning paradigm we have recently proposed for neural
networks training. Quiet different from BP, activation learning
relies on an improved Hebbian learning rules [17] to induce
local competition among neurons for network training, thus it
does not require predefining a task-specific loss function or any
feedback of error signals. As a result, it can not only facilitate
eliminating the burden of designing complicated anomaly-aware
learning objectives, but also achieve neural networks training with biological plausibility and computational efficiencies.
More importantly, in activation learning, common input patterns
can be learned more and activated more. The output activation
value can reflect the relative typicality of the data in the whole
data set. In time series anomaly detection, the aim is to mine
anomalous temporal patterns, i.e., patterns that rarely or never
occur. Correspondingly, the mechanism of activation learning
facilitates the intuitive understanding of anomalies based on the
activation values, thus it motivates us to apply activation learning
to time series anomaly detection.
The proposed method shows advantages from both theoretical
and practical perspectives. Theoretically, it does not rely on
BP or task-specific loss functions and provides an intuitive and
effective way to interpret detected anomalies based on activation
values, offering a solution for designing novel anomaly detection models. Practically, our approach establishes criteria for
identifying anomalies based on statistical distribution, avoiding
the ambiguity of manually defined anomalies. Additionally, our
method employs a simple network architecture and updates
parameters via forward propagation, requiring less storage for
intermediate results, making it more efficient and suitable for
various practical applications. Overall, the main contributions
of this work can be summarized as follows:
r A new unsupervised time series anomaly detection
paradigm based on activation learning is proposed. This

IEEE TRANSACTIONS ON BIG DATA, VOL. 11, NO. 3, MAY/JUNE 2025

is the first biologically plausible algorithm trained neural
network for time series anomaly detection to the best of
our knowledge.
r ALAD dose not rely on BP training, complicated network
structures, or tailored anomaly-aware learning objectives.
A simple fully connected network architecture and local
learning rules are all that is needed to achieve competitive
anomaly detection performance.
r By utilizing various synthetic and real-world time series
anomaly datasets, experimental results have illustrated the
effectiveness and feasibility of the proposed paradigm.
More importantly, this work has also demonstrated that
biologically plausible algorithm trained models can outperform BP in certain scenarios.
The rest of this paper is organized as follows. Section II
presents the related work, including the anomaly detection in
time series and Hebbian learning. Section III covers the preliminary work. Section IV introduces the framework of the proposed
method. The experimental results and discussion are given in
Section V, followed by the conclusion and future work.
II. RELATED WORK
A. Anomaly Detection in Time Series
Anomaly detection in time series is an emerging topic in data
mining and machine learning communities. Various anomaly
detection methods have been proposed and shown their superiority in some specific situations, which mainly can be divided
into statistical-based methods, machine learning-based methods
and deep learning-based methods.
1) Statistical-based Methods: Statistical-based methods generally utilize traditional statistical algorithms to identify anomalies. For example, Auto-Regressive Integrated Moving Average
(ARIMA) is one of the widely used tools to analyze time series
data, a series of ARIMA-based methods have been proposed to
exploit the temporal pattern of time series data and perform
anomaly detection [18]. Additionally, methods that rely on
statistical distribution assumptions and those based on distance
measurements are also prevalent, offering different approaches
to identifying deviations from normal patterns [19], [20]. However, real-world time series data generally exhibit volatile characteristics due to various internal/external factors, and these
classical methods intrinsically lack the capability of capturing
the temporal dependencies among time series data [21].
2) Machine Learning-based Methods: Machine learningbased methods apply modern techniques to detect anomalies.
For instance, Isolation Forest (IF) [22] relies on an ensemble of
isolation trees, which recursively randomly partitions the dataset
to find isolated anomalies. Local Outlier Factor (LOF) [23] is
a density-based anomaly detection algorithm, which performs
anomaly detection by judging on the density between data points
with their neighbors. Ji et al. [24] developed a hybrid model
that projected multivariate time series into a lower-dimensional
space to facilitate anomaly detection. Hu et al. [25] introduced
a computational framework for identifying discords in multivariate time series using a recurrence plot analysis, alongside a
strategy for efficient pairwise distance comparisons.

DING et al.: ALAD: A NEW UNSUPERVISED TIME SERIES ANOMALY DETECTION PARADIGM BASED ON ACTIVATION LEARNING

3) Deep Learning-based Methods: Nowadays, a series of
studies have demonstrated the effectiveness of deep learningbased methods in time series anomaly detection [26]. Generally, deep learning-based methods are divided into two
categories: forecasting-based and reconstruction-based methods [27]. Forecasting-based methods perform anomaly detection based on deviations between predicted results and actual
values, typically using models based on LSTM [28], TCN [7],
and Transformer [29]. Reconstruction-based methods typically employ autoencoders (AE) [30], variational autoencoders
(VAE) [31], and their variants [32] to learn latent representations
from normal data. These methods conduct anomaly detection
by comparing reconstruction errors between the reconstructed
and actual samples, operating under the assumption that the
models would fail to accurately reconstruct unseen abnormal
samples. However, these assumptions do not always hold. For
instance, these models often rely on complicated architectures
and focus predominantly on reconstruction or prediction quality,
potentially causing even abnormal data to be well reconstructed
or fitted due to ignored inconsistencies in latent representations.
Moreover, the fundamental algorithm for training these deep
learning-based methods is BP, which not only requires predefined loss functions for error propagation but also demands additional resources for gradient computations and storage. Overall,
there remains an open need for designing more innovative solutions to expand the application scenarios of time series anomaly
detection.
B. Unsupervised Anomaly Detection Methods
In the landscape of anomaly detection, supervised and unsupervised methods are widely utilized. Supervised anomaly
detection relies on labeled datasets to train models that can
distinguish between normal and anomalous patterns. In contrast,
unsupervised anomaly detection methods do not require labeled
data, focusing instead on learning the normal patterns from the
data and identifying deviations as anomalies. This lack of dependence on labeled data makes unsupervised methods particularly
significant, as they are more adaptable to a variety of real-world
applications where labeling is impractical or impossible [33].
Unsupervised anomaly detection methods generally leverage
various architectures, including autoencoders, graph neural networks, and Transformers, to detect anomalies by learning normal
data patterns and identifying deviations without the need for labeled data [34]. For example, Unsupervised Anomaly Detection
(USAD) [35] adopts an autoencoder architecture within an adversarial training framework, which amplifies the reconstruction
error of anomalies and contributes to anomaly detection. Graph
Deviation Network (GDN) [8] combines a structure learning
module with a graph neural network and uses forecasting deviations as anomaly scores. TranAD [36], a state-of-the-art anomaly
detection method, is based on the Transformer architecture and
uses a Transformer encoder and self-conditioning mechanism
to achieve representation learning and perform anomaly detection. OmniAnomaly [37] learns robust representations from
time series using a stochastic recurrent neural network, reconstructs the input data from these representations, and uses the

1287

reconstruction probabilities to identify anomalies. Li et al. [38]
introduced a prototype-oriented unsupervised anomaly detection method for multivariate time series, enhancing adaptability through a probabilistic framework that utilizes transferable
prototypes. These methods amplify reconstruction errors or use
robust representations to identify anomalies, showcasing the
adaptability of unsupervised approaches in handling complex
datasets.
Compared to existing unsupervised methods, ALAD demonstrates several advantages. It leverages activation learning to utilize the global information of the dataset for estimating statistical
aspects of time series patterns, offering an intuitive interpretation of anomalies based on activation values. This approach
eliminates the need for predefined task-specific loss functions
and reduces resource usage by avoiding gradient computations
and storage. Furthermore, by not relying on backpropagation,
ALAD aligns more closely with biologically plausible models
of learning, providing a more efficient and scalable alternative
in real-world settings.
C. Hebbian Learning
Hebbian learning is a biologically plausible and ecologically
valid learning mechanism, which follows the principle of ‘units
that fire together, wire together’ [39]. In the literature, there
are several researchers have attempted to develop Hebbian-like
mechanisms for training neural networks and as an alternative
to BP, since it can address the biological implausibility of BP
while not require any feedback of error signal, thus mitigated the
computational inefficiencies in BP. Hebbian learning is used for
neural network training by changing the strength of the synapses
between neurons, i.e., the connection weights. Formally, given
a synapse of weight wij connecting neuron ai in layer l and
neuron aj in layer l + 1, the rule of vanilla Hebbian learning
can be defined by
l
Δwij
= ηali al+1
j ,

(1)

denote the activation values of pre-synaptic
where ali and al+1
j
neuron and post-synaptic neuron, respectively, and η is the
learning rate. The core idea of Hebbian learning is that connection weight wij should be associated with both pre-synaptic
and post-synaptic neurons. When both of the two neurons are
activated at the same time, the connection weight between them
should be strengthened, while when the two neurons are in
opposite states, the connection weight should be weakened.
Recently, motivated by Hebbian learning rules, Krotov and
Hopfiled [40] proposed a learning algorithm for training neural
network, which leveraged the global inhibition in hidden layers
and was capable of learning lower-layer early representations
that facilitated the training of high-layer weights with a regular
backpropagation algorithm on various tasks. HebbNet [41] was
an improved Hebbian learning based neural network, which
applied an activation threshold and gradient sparsity into the
Hebbian learning rules. Similar to the training procedure designed by Krotov and Hopfiled, the first layer weights in HebbNet were learnt in an unsupervised manner by the proposed
Hebbian learning rules, and the weights between hidden and

1288

IEEE TRANSACTIONS ON BIG DATA, VOL. 11, NO. 3, MAY/JUNE 2025

output layer were learnt by BP. HebbNet achieved comparable
performance to Krotov and Hopfiled, while simplifying the training procedure. SoftHebb [42] combined a soft winner-takes-all
strategy with Hebbian learning rule to minimize cross-entropy,
which was proved to be capable of increasing learning speed
and higher robustness to noise and adversarial attacks. Grounded
on SoftHebb, Adrien et al. [43] presented multilayer SoftHebb,
which achieved depth in Hebbian learning and was verified to
realize promising performance on difficult tasks with relatively
high efficiency.
However, there are very few attempts to further improve the
effectiveness of Hebbian learning in training neural networks.
Besides, existing approaches only adopt Hebbian learning-based
methods to solve image classification tasks while not applying
Hebbian learning to other specific scenarios. Thus, the potential
of Hebbian learning-based methods has been underestimated. In
this work, we proposed a Hebbian learning-improved method for
time series anomaly detection, which broadens the applications
scenarios of Hebbian learning algorithms and also demonstrates
that biologically plausible algorithm trained models can outperform BP in certain scenarios.
III. PRELIMINARIES

B. Problem Statement
Given a time series data S = {x1 , x2 , . . . , xT } with length
T , each point xt is collected at a specific timestamp t. For
time series anomaly detection, historical data are beneficial
to understand the contextual relationships of an observation
xt . Therefore, like most methods [35], [37], a lookback window with size n is applied to convert time series data into
a sequences of sliding windows, and each window is used to
calculate the anomaly result, rather than just xt . At a time step
t, the input time series data in window Xt can be represented
as Xt = [xt−n+1 , xt−n+2 , . . . , xt ]T . The task of time series
anomaly detection is to assign a binary label yt ∈ {0, 1} to
indicate whether timestamp t is anomalous or not.
IV. METHOD

A. Activation Learning Rules
In the vanailla Hebbain learning, the rule in (1) is not stable
since the weights may grow unboundedly. A series of modified
rules have been proposed to improve Hebbian learning in terms
of convergence, which typically introduce additional constraints
or restrictions [17], [44], but this reduces the biological plausibility. Moreover, such rules are used to train a single neuron
and are not applicable to the training of multiple neurons in
a layer. Therefore, by introducing a competition mechanism
within neurons and among neurons into Hebbian learning, we
develop the activation learning rule in [16], which can work with
the training of multiple neurons in a layer:



l+1
l+1 l
l
l
ak wik .
ai −
(2)
Δwij = ηaj
k


l
In the learning rule, al+1
= r alr wrj
denotes the result of
j
feedforward
propagation
to
neuron
j
from
the previous layer.

l
The term k al+1
k wik represents the internal feedback from
all the neurons in layer l + 1, which forces the neurons in
layer l + 1 to compete with neuron j to fire. To understand this
l+1
l
and wik
are all positive
phenomenon, assuming that al+1
j , ak
l+1
variables, and if ak is activated, then the connection weight
l+1
l+1 l
wij
is weakened by a strength of ηal+1
j ak wik . After iterative
training, certain weights tend to activate more for specific input
patterns. This mechanism we call local competition, since it
raises local competitions within and among neurons.
The weight matrix w of each layer can converge to an asymptotically stable solution after a sufficient number of training steps
by learning rule (2), which takes the form of
Cw − wwT Cw = 0,

where C = E{xxT } is the covariance matrix of inputs. For
the number of receiving neurons m = 1, there are two stable
solutions of w, corresponding to v and −v, where v is the
eigenvector corresponding to the largest eigenvalue of C. For
m > 1, there are infinite number of stable solutions, and the
specific stable solution depends on the initial value of weight
and the training samples.

(3)

In this section, we first introduce how activation values are
utilized for anomaly detection. Subsequently, we detail the
network architecture that we have adopted. Finally, we describe
the manner of training and inference.
A. Activation Value for Input Typicality Estimation
Given a layer trained by the above learning rule (2), if the
input strength of al 2 is fixed, a more common input pattern
will induce a higher activation al+1 2 , which means that the
output strength of activation can be used to estimate the typicality
of the input pattern, i.e., how probable the input pattern is. To
further explain the phenomenon, assume that the number of
receiving neurons in next layer m is smaller than the input
dimension and V represents the vector space spanned from
the eigenvectors v1 , v2 , . . ., vm . Wherein, V is called typical
space, which is a convex and compact area shaped by multiple
layers, and it contains majority of the common inputs, thus the
distance between it and a input sample can be used to measure
the typicality of the input. Fig. 1 visually demonstrates how the
output activation values are used to measure the typicality of the
time series patterns.
Given the input vector of a layer al , the distance between it
and the typical space can be expressed as


l
alT vi 2 .
(4)
d(a , V ) = al 2 −
i

More importantly, from the stable solutions described in [16],
it is derived that the squared norm of the output activation,
al+1 2 , tends to be upper bounded by
al 2 − d2 (al , V ).

(5)

DING et al.: ALAD: A NEW UNSUPERVISED TIME SERIES ANOMALY DETECTION PARADIGM BASED ON ACTIVATION LEARNING

Fig. 1. The output activation measures the typicality of the time series pattern,
and anomalous patterns will be far from the typical space, leading to smaller
activation values.

In particular, when w = [v1 , v2 , . . ., vm ], al+1 2 converges
to al 2 − d2 (al , V ). Consequently, when the magnitude of the
input al 2 is fixed, the output activation al+1 2 can be used to
measure the distance between the input al and the typical space
V . It should be noted that although only the case that m is less
than the input dimension is discussed, the above conclusion still
holds for generic m.
Overall, the aforementioned useful insights in activation
learning motivate us to apply it to time series anomaly detection.
Specifically, in realistic time series data, anomalous patterns
generally rarely or never occur, which causes difficulties in
establishing anomaly rules manually. Fortuitously, the mechanism of activation learning is capable of leveraging the global
information of the dataset to estimate the statistical aspects of the
time series patterns, and it further provides an intuitive way to
interpret the detected anomalies based on the activation values.
B. Network Architecture
In this subsection, the designed network architecture is presented. To incorporate the mechanism of activation learning,
we design a simple but tailored architecture based on a fully
connected network, as shown in Fig. 2.
Specifically, the original time series data are first transformed
into sliding windows for keeping the contextual relationships,
and then fed into the ALAD. In the bottom-up network structure
of ALAD, the sliding windows are first fed to a norm layer,
which transforms the input data into a unit vector to fix the input
magnitude. Then, following is a fully connected network with
multiple hidden layers. In order to cascade multiple layers in a
network, the input and output magnitudes of each layer need to
be maintained consistent to control the activation output, i.e.,
x2 = f (x)2 . Therefore, the following form of nonlinear
function is adopted here as the activation function
f (x) = β(|x| − |x|),

As mentioned previously, the output of a layer trained by the
learning rule (2) is prone to generating higher activation value
on a more probable pattern. In order to output a scalar value
for evaluating directly whether the input pattern is abnormal or
not, an output activation layer is deployed on the top of ALAD,
which performs  · 22 operation on the output of the last hidden
layer.
By employing multiple layers with specific nonlinear activation functions, ALAD constructs a compact typical space
that effectively captures the probability distribution of input
patterns. In time series anomaly detection, this is crucial because
anomalous patterns often have a low probability of occurrence or
may not appear in the training dataset at all. During the training
phase, this approach ensures that anomalous patterns are situated
far from the typical space, resulting in smaller activation values.
These values serve as a critical metric for identifying anomalies,
as they signify substantial deviations from expected patterns.
ALAD enhances anomaly detection by leveraging activation
learning to effectively utilize global dataset information, facilitating intuitive interpretations of anomalies through activation
values and statistical insights, thereby alleviating the ambiguity in defining ground-truth anomalies. The method employs
a simple network architecture, consisting of just a few fully
connected layers, and it does not require the definition of a
global task-specific loss function, thereby minimizing resource
demands such as gradient computations and storage. Additionally, its simplified structure also enables potential integrations
with advanced deep learning models, offering opportunities for
model initialization and combining with pretrained models.
C. Model Training
Activation learning adopts local Hebbian learning rules to
update the synaptic weights. Therefore, the training of ALAD
with a multi-layer network structure is conducted in a bottom-up
unsupervised manner. The training process of ALAD is summarized in Algorithm 1. Specifically, the weight matrix of the
network is first initialized from a normal distribution with zero
mean and small variance. Then, input data is normalized to unit
vector before being fed into the network. Subsequently, forward
propagation is performed and the weight matrixes are trained
layer by layer by learning rule. This process is repeated until the
specified epochs.
The above training method can also be applied to batch-wise
training manner. Specifically, in each training epoch, the training
samples are divided into multiple mini-batches fed into the
network for training the weights through feedforward and local
feedback, such that the weights of the multi-layer network can
be updated layer by layer with each batch. Given a batch of
samples, the learning rule (2) can be modified as

(6)

which serves to de-mean the absolute value of the input x, and
β is a coefficient used to rescale x2 = f (x)2 . It should
be noted that any nonlinear function that does not change the
magnitude of the input can be considered as a candidate for the
activation function.

1289

l
=
Δwij

B

η  l+1
aj(b)
B
b=1


ali(b) −


k


l
al+1
k(b) wik

,

(7)

where B denotes the batch size, b represents the index of samples
in a batch, and η is the learning rate.

1290

IEEE TRANSACTIONS ON BIG DATA, VOL. 11, NO. 3, MAY/JUNE 2025

Fig. 2. The framework of ALAD. The upper subfigure of the framework shows the sliding windowing of the original time series. The lower subfigure shows how
ALAD works and the network architecture details.

D. Anomaly Inference
The inference phase of ALAD is summaried in Algorithm 2.
During the inference phase, the data Xt in the sliding window is
fed into the trained model, and then being normalized to a unit
vector. Then, the output of the last hidden layer is obtained via
layer by layer forward propagation. Subsequently, the activation
value of Xt is derived by  · 22 operation. In the mechanism of
activation learning, the more common patterns induce larger
activation values, while the rarer patterns induce smaller activation values, thus for intuitiveness, 1 − Act(Xt ) is used to
indicate the anomaly score of input data. If the anomaly score of
input data is greater than a certain threshold μ, it is anomalous,
otherwise, it is normal. In this work, similar to [22], [23],
the threshold value is obtained through grid search. Notably,
our model’s output activation values reflect the distribution of
data patterns in the training set, enabling anomaly detection by
identifying anomalously low activation values during testing.
Thus, in practical scenarios, even in the absence of anomaly
samples, we can determine the threshold μ by setting it at various
percentiles within normal data, such as the 95th percentile. This
threshold can be further adjusted based on the specific definition
of anomalies or prior knowledge relevant to the application
context.

V. EXPERIMENTS
A. Datasets
We use synthetic datasets and real-world datasets for the
performance evaluation of all the methods. The descriptions of
these datasets are as follows:
Synthetic Datasets: We apply the synthesizing strategy
from [45] to inject anomalies into time series, which provide
a general and unified synthetic criterion for generating various
anomalies from different applications. Wherein, 24 synthetic
univariate time series data are generated, which contain six types
of anomalies covering point-wise and pattern-wise anomalies,
including global, contextual, shapelet, seasonal, trend and mixture anomalies. Specifically, the synthetic univariate time series
are generated with sinusoidal wave and each series has a length
of 2000. The first half of the data is used as training data and the
rest is used as test data with different proportions of anomalies
injected. Each type of anomalies is manipulated with different
ratio 0.05, 0.1, 0.15 and 0.2.
Real-World Datasets: We use four publicly available datasets
collected from real-world application scenarios. These include
CPU usage data from an Amazon server (Service), real-time
traffic data from the Twin Cities Metro area in Minnesota
(Traffic) [46], internal bleeding data derived from arterial blood

DING et al.: ALAD: A NEW UNSUPERVISED TIME SERIES ANOMALY DETECTION PARADIGM BASED ON ACTIVATION LEARNING

Algorithm 2: Algorithm for Anomaly Inference.
Input: The set of test data X = {X1 , X2 , . . . , XT },
threshold μ.
Output: The label yt of Xt .
1: Load the trained model with weight matrixes
∗
.
W1∗ , W2∗ , . . . , WL
2: for all t = 1, 2, . . . , T do
3: //normalize input
4: A0 ← N orm(Xt )
5: for all l = 1, . . . , L do
6:
//forward pass
7:
Al = f (Wl∗T Al−1 )
8: end for
9: //calculate the output activation of Xt
10: Act(Xt ) ← AL 22
11: if (1 − Act(Xt )) > μ then
12:
yt =“Anomalous”
13: else
14:
yt =“Normal”
15: end if
16: end for

Algorithm 1: Algorithm for Training ALAD.
Input: The set of training data X = {X1 , X2 , . . . , XT },
learning rate η, epochs E.
Output: L layers of trained weight matrixes
∗
.
W1∗ , W2∗ , . . . , WL
1: Random initialize L layers of weight matrixes
W1 , W2 , . . . , WL from a normal distribution of zero
mean and small variance.
2: while e < E do
3: for all t = 1, 2, . . . , T do
4:
//normalize input
5:
A0 ← N orm(Xt )
6:
for all l = 1, . . . , L do
7:
//forward pass
8:
Al = WlT Al−1
9:
//use learning rule to train weights layer by layer
10:
ΔWl ← (Al−1 − Wl Al )ATl
11:
Wl ← Wl − ηΔWl
12:
Al ← f (Al )
13:
end for
14: end for
15: e ← e + 1
16: end while
∗
.
17: return W1∗ , W2∗ , . . . , WL

F 1 score =

pressure measurements in pigs (Bleeding) [47], and a subset
of the UCR dataset, which includes data from various natural
sources [48]. The characteristics of real-world datasets are summarized in Table II.
B. Experimental Settings
Comparison Methods. We make a comparative study
of the proposed method with nine representative methods,
including IF [22], LOF [23], AE [30], USAD [35], DAGMM
[49], GDN [8], TranAD [36], DCdetector [48] and AnomalyBERT [50]. For each comparison method, we use grid search to
select anomaly thresholds for different datasets separately.
Datasets Configuration. To maintain consistency, all methods
use a sliding window of size 5, with overlapping windows for
the real dataset and non-overlapping windows for the synthetic
dataset. For the real-world dataset, we use the same dataset division proportion as [36]. For the synthetic dataset, all methods are
trained on the unmanipulated data and tested on the manipulated
data.
Evaluation Metrics. To measure and evaluate the performance
of the proposed method, similar to previous studies [36], three
common metrics, Recall, Precision and F1 score are employed
to compare the performance of different models, these metrics
are derived:
TP
TP + FP
TP
Recall =
TP + FN

P recision =

1291

(8)
(9)

2 · P recision · Recall
P recision + Recall

(10)

where T P is the True Positives, F P is the False Positives, and
F N is the False Negatives. In actual cases, anomalies typically
last for a period of time and thus form a continuous segment of
anomalies. Therefore, we do not care about point-by-point evaluation, but use a point-adjust evaluation approach [51], which is
widely used in the evaluation of anomaly detection tasks [36],
[52]. Specifically, for a continuous segment of anomalies, if one
of the observations from the ground truth is correctly identified,
then all anomalies in the segment are viewed to be correctly
detected, and observations outside the ground truth anomaly
segment are treated as normal.
C. Experimental Results on Real-World Datasets
In this subsection, experiments on real-world datasets are
conducted to evaluate the performance of ALAD. The experimental results are shown in Table I, where three metrics are
calculated, and P, R, F1 respectively represent the Precision,
Recall, F1 score. For these metrics, a higher value indicates a
better performance. Specifically, the best F1 scores are bolded,
and in particular, the average F1 scores are also provided for the
Traffic, Bleeding and UCR datasets.
From the experimental results, one can find that ALAD has
achieved competitive performance than comparison methods
on most datasets. In particularly, ALAD has realized the best
average F1 scores on Bleeding, Traffic and UCR datasets. Machine learning-based methods, like IF and LOF achieve worst
performance, since they are both unsupervised methods that
consider each instance as an individual, thus they are susceptible
to noisy and perturbed data. USAD, DAGMM and TranAD
are recent representative reconstruction-based methods, they

1292

IEEE TRANSACTIONS ON BIG DATA, VOL. 11, NO. 3, MAY/JUNE 2025

TABLE I
EXPERIMENTAL RESULTS FOR ALAD WITH COMPARISON METHODS ON REAL-WORLD DATASETS

TABLE II
REAL-WORLD DATASET STATISTICS

only use local window as input for reconstruction, and cannot
fully utilize the global information of the entire dataset. Moreover, reconstruction-based methods mainly focus on the quality
of instance reconstruction, thus even abnormal data could be
well reconstructed. Forecasting-based methods, like GDN, tries
to predict the values based on historical data, and performs
anomaly detection according to the forecasting errors. However,
real-world time series data are inherently unpredictable due

to various internal/external factors. Thus, normal observations
would be easily mistaken detected by GDN and cause a false
positive. DCdetector and AnomalyBERT are state-of-the-art
methods that have achieved commendable results, but DCdetector’s reliance on dual attention contrastive learning may not
adapt well to datasets where anomaly signatures are subtle and
highly variable, leading to less effective anomaly discrimination. Similarly, AnomalyBERT’s dependency on self-supervised
learning with predefined synthetic outliers can limit its ability to
generalize across real-world datasets that exhibit highly diverse
and unforeseen anomaly patterns. More importantly, real-world
time series data are generally composed of a large of number
of short-term behaviors with various temporal patterns. The
more common patterns can be learned more and activated more,
while the anomalous patterns that exhibit distinct characteristics
cannot be activated, thus, in ALAD the global information of
dataset can be fully utilized.
In addition, from the experimental results, one can find that
most methods achieve higher Recall but lower Precision. The
reason behind this is that realistic anomalous patterns generally exhibit relatively distinct patterns, so that most methods can handle the detection of most anomalies, thus achieve
high recall. However, time series data in realistic scenarios are

DING et al.: ALAD: A NEW UNSUPERVISED TIME SERIES ANOMALY DETECTION PARADIGM BASED ON ACTIVATION LEARNING

Fig. 3.

1293

Experimental results on synthetic datasets.

inevitably disturbed by high noises, uncertainties, etc. These
realistic sophisticated compositions would considerably affect
the performance of detection precision. Even so, ALAD still
achieves competitive performance compared with the state-ofthe-arts. It should be noted that ALAD does not use BP, meaning
it does not rely on any anomaly-specific learning objectives,
which makes the method more versatile for anomaly detection
tasks. Additionally, ALAD employs a straightforward, fully
connected network architecture without complex mechanisms,
suggesting significant potential for further enhancements.
D. Experimental Results on Synthetic Datasets
The experimental results on synthetic datasets are demonstrated in Fig. 3, where the F1 scores of each method in different
ratios of anomalies are summarized. First, Fig. 3 demonstrates
that ALAD achieves better results than other comparison methods. In particular, ALAD exhibits a competitive performance in
detecting collective types of anomalies. To be specific, collective
anomalies are defined as a collection of related data instances
that is anomalous with respect to the entire dataset [45]. Accordingly, kinds of related data instances are fed into ALAD in the
form of sliding windows, thus the contextual relationships can be
fully utilized for activation learning. In this way, compared with
the anomalies caused by individual points, anomalous patterns
in a sequence of consecutive points are more likely to induce
larger responses. In addition, it can also be found that collective
trend anomalies are more challenging for ALAD. The reason
behind this is that a norm layer is first applied in the structure
of ALAD, which may damage the performance for identifying

trend anomalies when the window size is not appropriately set.
Even though, ALAD still achieves better performance than the
other methods. The main reason for the promising performance
achieved by ALAD on synthetic data is that ALAD is trained on
the training set without injected anomalies, which is facilitated to
learn the normal patterns, thus the unseen abnormal patterns will
be reflected more timely and accurately during the evaluation
phase.
E. Case Study
To show the performance of ALAD in capturing the anomalous patterns of time series data intuitively, four cases of
visualization of anomaly detection results are shown in
Fig. 5. From the visualizations, one can see that ALAD achieves
high precision and recall. ALAD aims at learning the statistical
distribution of the input patterns, and it is capable of generating anomaly scores based on the rarity of patterns in training
data, which means that ALAD dose not require the hypothesis
of pollution-free training set like existing reconstruction-based
methods, thus it has more practical significance. Moreover, it can
also be seen from the figures that ALAD raises different magnitudes of anomaly scores according to the anomalous degree of
the input pattern, which is useful to distinguish the severity of
anomalies in practical scenarios.
To visualize the statistical distribution of the samples learned
by ALAD from an intuitive perspective, we add a hidden layer
with 3 nodes after the last hidden layer in the network structure,
which facilitates showing the distribution of different input
patterns in 3D space. Specifically, ALAD is trained on the

1294

IEEE TRANSACTIONS ON BIG DATA, VOL. 11, NO. 3, MAY/JUNE 2025

Fig. 4. Hyperparameters analysis for (a) the number of units, (b) the number
of layers, and (c) the window size.

training set, then tested on a selected time series containing
anomalous data and the results of the last hidden layer are
visualized by projection into the 3D space. The results of the
visualization on the collective global, point global, Bleeding_1
and Bleeding_2 datasets are shown in Fig. 6, where each black
point denotes a normal sample and each red point denotes an
abnormal sample. From the visualization results, it can be seen

Fig. 5. Four cases of visualization of anomaly detection results on (a) service,
(b) bleeding_1, (c) collective global anomalies, and (d) collective seasonal
anomalies.

DING et al.: ALAD: A NEW UNSUPERVISED TIME SERIES ANOMALY DETECTION PARADIGM BASED ON ACTIVATION LEARNING

1295

Fig. 6. Four cases of visualization of the learned statistical distribution results for (a) collective global anomalies, (b) point global anomalies, (c) bleeding_1, and
(d) bleeding_2.

that the normal samples are concentrated on the arc, while the
abnormal samples are scattered in the interior of the arc. The
reason for this phenomenon is that, given a fixed strength of the
input samples, normal samples usually have stronger activation
values, i.e., L2 norm, causing them to be scattered on arcs farther
from the center of the circle. The abnormal samples, in contrast,
have lower activation values, so they are closer to the center of the
arc. Consequently, the anomalous patterns are well distinguished
from the normal patterns.
F. Analysis of Hyperparameters
The influences of three hyperparameters, i.e., the number of
layers, the number of units per layer, and the window size,
may impact performance. Therefore, the Traffic_1 and Traffic_2
datasets are used for analysis. Specifically, the number of units
discussed ranges from {8, 16, 32, 64, 128}, the number of layers
from 1 to 5, and the window sizes from {3, 5, 10, 15, 20}. When
analyzing the effectiveness of one hyperparameter, the others

are kept unchanged. From the visualizations in Fig. 4, one can
observe that different combinations have varying effects on the
model’s performance. Specifically, with an increase in hidden
units given a fixed depth, the F1 score of ALAD first increases
and then decreases. Similar observations can also be found in
the analysis of the number of layers. This phenomenon can be
attributed to the fact that smaller hidden units or fewer layers
result in a simpler network structure, thus the model is incapable
of learning effectively from data. Conversely, higher numbers of
hidden units and layers may lead to a more complicated network
structure, making the model susceptible to noise and harder to
optimize. The discussion on window size indicates that different
window sizes also have an impact on the experimental results.
This occurs because if the window size is set too large, it becomes
difficult to capture subtle anomalies, whereas a window size that
is too small may not effectively detect anomalies that manifest
over longer trends. Overall, since different time series data may
exhibit different temporal characteristics, the combination of
hyperparameters suitable for one dataset may not be appropriate

1296

IEEE TRANSACTIONS ON BIG DATA, VOL. 11, NO. 3, MAY/JUNE 2025

for another, thus it is necessary to choose hyperparameters based
on empirical experience when applying ALAD to a specific
dataset.
VI. CONCLUSION AND FUTURE WORK
In this work, based on activation learning, a new unsupervised
time series anomaly detection paradigm is proposed, which
provides an intuitive and effective way to interpret detected
anomalies based on the activation values. Experimental results
on various real-world and synthetic datasets confirm the promising performance of the proposed method compared with the
state-of-the-art methods. Furthermore, this work has complemented the activity of existing Hebbian-like methods, and also
demonstrated that biologically plausible algorithm can achieve
more promising performance than BP in certain scenarios. In
future work, we plan to extend the capabilities of our method
to adaptive anomaly detection, for example by integrating peak
detection techniques that can dynamically adjust based on the
distribution of activation values, thereby enhancing its practical
value in real-world scenarios. Additionally, as a new paradigm,
our approach holds significant potential for integration with
modern deep learning technologies such as pretrained models and self-supervised learning techniques. Moreover, we are
particularly excited about the potential of activation learning
to facilitate the design of innovative neural network architectures, broadening the application of our method across various
domains.
REFERENCES
[1] L. Cui et al., “Security and privacy-enhanced federated learning for
anomaly detection in IoT infrastructures,” IEEE Trans. Ind. Inform.,
vol. 18, no. 5, pp. 3492–3500, May 2022.
[2] C. Huang, G. Min, Y. Wu, Y. Ying, K. Pei, and Z. Xiang, “Time series
anomaly detection for trustworthy services in cloud computing systems,”
IEEE Trans. Big Data, vol. 8, no. 1, pp. 60–72, Feb. 2022.
[3] L. Erhan et al., “Smart anomaly detection in sensor systems: A multiperspective review,” Inf. Fusion, vol. 67, pp. 64–79, 2021.
[4] M. Zhang, T. Li, Y. Yu, Y. Li, P. Hui, and Y. Zheng, “Urban anomaly
analytics: Description, detection, and prediction,” IEEE Trans. Big Data,
vol. 8, no. 3, pp. 809–826, Jun. 2022.
[5] H. Zhao et al., “Multivariate time-series anomaly detection via graph attention network,” in Proc. IEEE Int. Conf. Data Mining, 2020, pp. 841–850.
[6] T. Kieu, B. Yang, C. Guo, and C. S. Jensen, “Outlier detection for time
series with recurrent autoencoder ensembles,” in Proc. Int. Joint Conf.
Artif. Intell., 2019, pp. 2725–2732.
[7] Z. Li, Y. Sun, L. Yang, Z. Zhao, and X. Chen, “Unsupervised machine
anomaly detection using autoencoder and temporal convolutional network,” IEEE Trans. Instrum. Meas., vol. 71, 2022, Art. no. 3525813.
[8] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 4027–4035.
[9] D. Wu, Z. Jiang, X. Xie, X. Wei, W. Yu, and R. Li, “LSTM learning
with Bayesian and Gaussian processing for anomaly detection in industrial
IoT,” IEEE Trans. Ind. Informat., vol. 16, no. 8, pp. 5244–5253, Aug. 2020.
[10] H. Gao, B. Qiu, R. J. D. Barroso, W. Hussain, Y. Xu, and X. Wang,
“TSMAE: A novel anomaly detection approach for Internet of Things time
series data using memory-augmented autoencoder,” IEEE Trans. Netw. Sci.
Eng., vol. 10, no. 5, pp. 2978–2990, Sep./Oct. 2023.
[11] N. Huyan, D. Quan, X. Zhang, X. Liang, J. Chanussot, and L. Jiao,
“Unsupervised outlier detection using memory and contrastive learning,”
IEEE Trans. Image Process., vol. 31, pp. 6440–6454, 2022.

[12] J. Zhao, F. Deng, J. Zhu, and J. Chen, “Searching density-increasing path
to local density peaks for unsupervised anomaly detection,” IEEE Trans.
Big Data, vol. 9, no. 4, pp. 1198–1209, Aug. 2023.
[13] Y. Zheng, M. Jin, Y. Liu, L. Chi, K. T. Phan, and Y.-P. P. Chen, “Generative and contrastive self-supervised learning for graph anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12220–12233,
Dec. 2023.
[14] M. Li, Y. Zhang, W. Zhang, Y. Chu, Y. Hu, and B. Yin, “Self-supervised
nodes-hyperedges embedding for heterogeneous information network
learning,” IEEE Trans. Big Data, vol. 9, no. 4, pp. 1210–1224, Aug. 2023.
[15] X. Zhang, J. Mu, X. Zhang, H. Liu, L. Zong, and Y. Li, “Deep anomaly
detection with self-supervised learning and adversarial training,” Pattern
Recognit., vol. 121, 2022, Art. no. 108234.
[16] H. Zhou, “Activation learning by local competitions,” 2022. [Online].
Available: https://arxiv.org/abs/2209.13400
[17] K. D. Miller and D. J. MacKay, “The role of constraints in Hebbian
learning,” Neural Computation, vol. 6, no. 1, pp. 100–126, 1994.
[18] X. Jin, Y. Sun, Z. Que, Y. Wang, and T. W. Chow, “Anomaly detection and
fault prognosis for bearings,” IEEE Trans. Instrum. Meas., vol. 65, no. 9,
pp. 2046–2054, Sep. 2016.
[19] F. Angiulli, S. Basta, and C. Pizzuti, “Distance-based detection and
prediction of outliers,” IEEE Trans. Knowl. Data Eng., vol. 18, no. 2,
pp. 145–160, Feb. 2006.
[20] L. Li, J. Yan, Q. Wen, Y. Jin, and X. Yang, “Learning robust deep state
space for unsupervised anomaly detection in contaminated time-series,”
IEEE Trans. Knowl. Data Eng., vol. 35, no. 6, pp. 6058–6072, Jun. 2023.
[21] M. Tang, M. Alazab, and Y. Luo, “Big data for cybersecurity: Vulnerability
disclosure trends and dependencies,” IEEE Trans. Big Data, vol. 5, no. 3,
pp. 317–329, Sep. 2019.
[22] S. Hariri, M. C. Kind, and R. J. Brunner, “Extended isolation forest,” IEEE
Trans. Knowl. Data Eng., vol. 33, no. 4, pp. 1479–1489, Apr. 2021.
[23] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. ACM SIGMOD Int. Conf. Manage.
Data, 2000, pp. 93–104.
[24] Z. Ji, Y. Wang, K. Yan, X. Xie, Y. Xiang, and J. Huang, “A spaceembedding strategy for anomaly detection in multivariate time series,”
Expert Syst. Appl., vol. 206, 2022, Art. no. 117892.
[25] M. Hu, X. Feng, Z. Ji, K. Yan, and S. Zhou, “A novel computational
approach for discord search with local recurrence rates in multivariate
time series,” Inf. Sci., vol. 477, pp. 220–233, 2019.
[26] G. Li and J. J. Jung, “Deep learning for anomaly detection in multivariate
time series: Approaches, applications, and challenges,” Inf. Fusion, vol. 91,
pp. 93–102, 2023.
[27] Y. Zhang, J. Wang, Y. Chen, H. Yu, and T. Qin, “Adaptive memory networks
with self-supervised learning for unsupervised anomaly detection,” IEEE
Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12068–12080, Dec. 2023.
[28] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric
dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, 2018, pp. 387–395.
[29] H. Kang and P. Kang, “Transformer-based multivariate time series
anomaly detection using inter-variable attention mechanism,” Knowl.Based Syst., vol. 290, 2024, Art. no. 111507.
[30] C. C. Aggarwal, “An introduction to outlier analysis,” in Outlier Analysis.
Berlin, Germany: Springer, 2017, pp. 1–34.
[31] L. Li, J. Yan, H. Wang, and Y. Jin, “Anomaly detection of time series with
smoothness-inducing sequential variational auto-encoder,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 32, no. 3, pp. 1177–1191, Mar. 2021.
[32] Y. Yao, J. Ma, and Y. Ye, “Regularizing autoencoders with wavelet transform for sequence anomaly detection,” Pattern Recognit., vol. 134, 2023,
Art. no. 109084.
[33] J. Fan, Z. Wang, H. Wu, D. Sun, J. Wu, and X. Lu, “An adversarial time–
frequency reconstruction network for unsupervised anomaly detection,”
Neural Netw., vol. 168, pp. 44–56, 2023.
[34] R. Bouman, Z. Bukhsh, and T. Heskes, “Unsupervised anomaly detection
algorithms on real-world data: How many do we need?,” J. Mach. Learn.
Res., vol. 25, no. 105, pp. 1–34, 2024.
[35] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,” in
Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 3395–3404.
[36] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” in Proc.
VLDB Endowment, vol. 15, no. 6, pp. 1201–1214, 2022.

DING et al.: ALAD: A NEW UNSUPERVISED TIME SERIES ANOMALY DETECTION PARADIGM BASED ON ACTIVATION LEARNING

[37] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 2828–2837.
[38] Y. Li, W. Chen, B. Chen, D. Wang, L. Tian, and M. Zhou, “Prototypeoriented unsupervised anomaly detection for multivariate time series,” in
Proc. Int. Conf. Mach. Learn., 2023, pp. 19 407–19 424.
[39] Y. Munakata and J. Pfaffly, “Hebbian learning and development,” Devlop.
Sci., vol. 7, no. 2, pp. 141–148, 2004.
[40] D. Krotov and J. J. Hopfield, “Unsupervised learning by competing hidden
units,” in Proc. Nat. Acad. Sci. USA, vol. 116, no. 16, pp. 7723–7731, 2019.
[41] M. Gupta, A. Ambikapathi, and S. Ramasamy, “HebbNet: A simplified
hebbian learning framework to do biologically plausible learning,” in Proc.
IEEE Int. Conf. Acoust. Speech Signal Process., 2021, pp. 3115–3119.
[42] T. Moraitis, D. Toichkin, Y. Chua, and Q. Guo, “SoftHebb: Bayesian
inference in unsupervised Hebbian soft winner-take-all networks,”
2021, arXiv:2107.05747.
[43] A. Journé, H. G. Rodriguez, Q. Guo, and T. Moraitis, “Hebbian deep
learning without feedback,” 2022, arXiv:2209.11883.
[44] E. Oja, “Simplified neuron model as a principal component analyzer,” J.
Math. Biol., vol. 15, no. 3, pp. 267–273, 1982.
[45] K.-H. Lai et al., “TODS: An automated time series outlier detection
system,” in Proc. AAAI Conf. Artif. Intell., 2021, pp. 16 060–16 062.
[46] S. Ahmad, A. Lavin, S. Purdy, and Z. Agha, “Unsupervised realtime anomaly detection for streaming data,” Neurocomputing, vol. 262,
pp. 134–147, 2017.
[47] E. Keogh, D. R. Taposh, U. Naik, and A. Agrawal, “Multi-dataset timeseries anomaly detection competition,” in Proc. ACM SIGKDD Int. Conf.
Knowl. Discov. Data Mining, 2021. [Online]. Available: https://compete.
hexagonml.com/practice/competition/39
[48] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “DCdetector: Dual
attention contrastive representation learning for time series anomaly detection,” in Proc. 29th ACM SIGKDD Conf. Knowl. Discov. Data Mining,
2023, pp. 3033–3045.
[49] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representations,
2018.
[50] Y. Jeong, E. Yang, J. H. Ryu, I. Park, and M. Kang, “AnomalyBERT:
Self-supervised transformer for time series anomaly detection using data
degradation scheme,” 2023, arXiv:2305.04468.
[51] H. Xu et al., “Unsupervised anomaly detection via variational auto-encoder
for seasonal KPIs in web applications,” in Proc. World Wide Web Conf.,
2018, pp. 187–196.
[52] Z. Li et al., “Multivariate time series anomaly detection and interpretation
using hierarchical inter-metric and temporal embedding,” in Proc. 27th
ACM SIGKDD Conf. Knowl. Discov. Data Mining, 2021, pp. 3220–3230.

Fengqian Ding received the MS degree from Shandong Normal University, Shandong, China, in 2022.
He is currently working toward the PhD degree with
the School of Information Science and Engineering,
Shandong University, Qingdao, China. His research
interests include application of time series analysis
and machine learning.

Bo Li received the BEng degree from Shandong
University, Shandong, China, in 2022. He is currently
working toward the MSc degree with the School
of Information Science and Engineering, Shandong
University, Qingdao, China. His research interests
include anomaly detection and machine learning.

1297

Xianye Ben (Senior Member, IEEE) received the
PhD degree in pattern recognition and intelligent
system from the College of Automation, Harbin Engineering University, Harbin, China, in 2010. She is
currently working as a full professor with the School
of Information Science and Engineering, Shandong
University, Qingdao, China. She has authored or
coauthored more than 100 papers in major journals
and conferences such as the IEEE Transactions on
Pattern Analysis and Machine Intelligence, IEEE
Transactions on Image Processing, IEEE Transactions on Circuits and Systems for Video Technology, IEEE Transactions on Multimedia, Pattern Recognition, CVPR, etc. Her current research interests include
pattern recognition, image processing, and machine learning. She received the
Excellent Doctorial Dissertation awarded by Harbin Engineering University. She
was also enrolled by the Distinguished Young Scholars Program of Shandong
University and the Shi Qingyun Female Scientists of China Society of Image
Graphics.

Jia Zhao received the BEng and PhD degrees from
Shandong University, Jinan, China, in 2006 and
2011, respectively. He is currently a professor with
the School of Information Science and Engineering,
Shandong University. His research interests include
nanophotonic, chip-scale optical interconnection, and
machine learning.

Hongchao Zhou received the BSc degree in physics
and mathematics and the MSc degree in control science and engineering from Tsinghua University, Beijing, China, in 2006 and 2008, respectively, and the
MSc and PhD degrees in electrical engineering from
the California Institute of Technology, Pasadena, CA,
USA, in 2009 and 2012, respectively. From 2012 to
2015, he was a post-doctoral researcher with the Signals, Information and Algorithms Laboratory, Massachusetts Institute of Technology. He is currently
a professor with the School of Information Science
and Engineering, Shandong University. His current research interests include
information theory, data systems, learning systems, and machine learning. He
was a recipient of the 2013 Charles Wilts Prize for the best doctoral thesis in
electrical engineering with the California Institute of Technology.
PAPER_TEXT
