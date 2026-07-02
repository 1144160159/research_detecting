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
# [819] The TES Framework: Joint Statistical Modeling and Machine Learning for Network KPI Forecasting
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
编号：819
题名：The TES Framework: Joint Statistical Modeling and Machine Learning for Network KPI Forecasting
年份：2025
DOI：10.1109/tnsm.2025.3628788
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2025.3628788.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：时序、日志、KPI 与云原生异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\819.txt
- 原始字符数：84478
- 本次发送字符数：84478
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
350

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

The TES Framework: Joint Statistical Modeling and
Machine Learning for Network KPI Forecasting
Leonardo Lo Schiavo , Genoveva García , Marco Gramaglia , Marco Fiore , Senior Member, IEEE,
Albert Banchs , Senior Member, IEEE, and Xavier Costa-Perez

Abstract—The vision of intelligent networks capable of automatically configuring crucial parameters for tasks such as
resource provisioning, anomaly detection or load balancing
largely hinges upon efficient AI-based algorithms. Time series
forecasting is a fundamental building block for network-oriented
AI and current trends lean towards the systematic adoption of
models based on deep learning approaches. In this paper, we pave
the way for a different strategy for the design of predictors for
mobile network environments, and we propose the Thresholded
Exponential Smoothing (TES) framework, a hybrid Statistical
Modeling and Deep Learning tool that allows for improving
the performance of network Key Performance Indicator (KPI)
forecasting. We adapt our framework to two state-of-the-art deep
learning tools for time series forecasting, based on Recurrent
Neural Networks and Transformer architectures. We experiment
with TES by showcasing its superior support for three practical
network management use cases, i.e., (i) anticipatory allocation
of network resources, (ii) mobile traffic anomaly prediction, and
(iii) mobile traffic load balancing. Our results, derived from
traffic measurements collected in operational mobile networks,
demonstrate that the TES framework can yield substantial
performance gains over current state-of-the-art predictors in the
applications considered.
Received 5 March 2025; revised 21 August 2025; accepted 26 October
2025. Date of publication 4 November 2025; date of current version
29 December 2025. The ORIGAMI project has supported this work, which
has received funding from the Smart Networks and Services Joint Undertaking
(SNS JU) under the European Union’s Horizon Europe research and innovation program under Grant Agreement No. 101139270. It is also co-funded by
the European Union under Grant Agreement No. 101191936 (SUSTAIN-6G).
The views and opinions expressed are solely those of the author(s) and do not
necessarily reflect those of the SUSTAIN-6G consortium parties, the European
Union, or the SNS JU (granting authority). Neither the European Union nor
the granting authority can be held responsible for them. The work of IMDEA
Networks was supported by the 6G-IRONWARE project funded under
grant CNS2023-143870 by MICIU/AEI/10.13039/501100011033 and the EU
NextGenerationEU/PRTR. Finally, the work of A. Banchs has been supported
by the Spanish Ministry of Economic Affairs and Digital Transformation
and the European Union-NextGenerationEU through the UNICO 5G I+D
6G-CLARION project. The associate editor coordinating the review of this
article and approving it for publication was V. Fodor. (Corresponding author:
Leonardo Lo Schiavo.)
Leonardo Lo Schiavo, Genoveva García, and Marco Gramaglia are with
the Telematic Engineering Department, University Carlos III de Madrid,
28911 Madrid, Spain (e-mail: lloschia@pa.uc3m.es; genoveva@pa.uc3m.es;
mgramagl@it.uc3m.es).
Marco Fiore is with the Network Data Science Group, IMDEA Networks
Institute, 28918 Madrid, Spain (e-mail: marco.fiore@imdea.org).
Albert Banchs is with the Telematic Engineering Department, University
Carlos III de Madrid, 28911 Madrid, Spain, and also with the Network Data
Science Group, IMDEA Networks Institute, 28918 Madrid, Spain (e-mail:
albert.banchs@imdea.org).
Xavier Costa-Perez is with the 6G Network Group, NEC Laboratories
Europe GmbH, 69115 Heidelberg, Germany, also with the AI-Driven
Systems Group, I2CAT, 08034 Barcelona, Spain, and also with the
AI-Driven Systems Department, ICREA, 08010 Barcelona, Spain (email: xavier.costa@neclab.eu).
Digital Object Identifier 10.1109/TNSM.2025.3628788

Index Terms—Forecasting, prediction, mobile traffic, network
KPI, network management, neural networks, statistical modeling.

I. I NTRODUCTION
VERY new generation of mobile networks invariably
raises the bar for the performance, reliability, and security
of cellular communication systems. Adhering to such a trend,
6G systems are expected to support diverse classes of services
and do so with near-zero latency, apparent infinite capacity,
and 100% availability, making de-facto the communication
infrastructure fully transparent to applications [1] and turning
6G networks into general-purpose platforms providing smart
connectivity to a plethora of very heterogeneous terminals.
While today’s mobile communication infrastructures are
already extremely tangled architectures that entail significant
challenges in terms of equipment management, traffic engineering, and capacity allocation [2], 6G systems will introduce
several layers of substantial additional complexity [3], [4].
Indeed, meeting the ambitious 6G performance targets will
require instant orchestration of physical resources and Virtual
Network Functions (VNFs) across different network domains,
in concert with user demands and multi-tenancy requirements
that rapidly shift in time.
Machine Learning (ML) and Artificial Intelligence (AI) are
largely regarded as fundamental enablers to realize such a
vision. Integrating AI/ML solutions, supported by a native
network architecture [5], will pave the road towards the
efficient support of various use cases that dramatically enhance
the performance of next-generation systems. Data-driven models have been repeatedly shown to offer enhanced quality
for key network management tasks such as anomaly detection [6], traffic classification [7], resource orchestration [8],
radio access operation [9], and energy saving [10], just to name
a few.
In many of those tasks, anticipatory decision-making is a
very desirable–if not mandatory–feature, making prediction an
essential building block to AI/ML-driven network management [11]. In this context, a plethora of works have proposed
ever more accurate forecasting models [12], [13] and recent
works have also shown how predictors can be tailored to
the downstream network management task by steering their
output [8], [14].
In this work, we focus on forecasting network Key
Performance Indicators (KPIs), such as traffic demands or user
throughput, as one of the cornerstones of future zero-touch

E

c 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
1932-4537 
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

SCHIAVO et al.: THE TES FRAMEWORK: JOINT STATISTICAL MODELING AND MACHINE LEARNING

network management [15]. While traffic prediction was carried out via statistical models until the first decade of the
century [16], [17], AI/ML solutions have nowadays taken a
clear lead and dominate the literature [18], [19], [20], [21].
We depart from the common practice to propose pure AI/MLbased models and explore hybrid approaches where traditional
statistical modeling is combined with deep learning [22].
This hybrid strategy is known to yield resilience to noisy
data and wide excursions in time series of financial data or
weather fluctuations [23], and we show that it can also help
achieve higher prediction accuracy in the presence of realworld mobile traffic data, thus benefiting network management
tasks that build upon such forecasts.
By pioneering the adoption of hybrid predictors using
statistical modeling and ML in the context of anticipatory
network management, our work yields the following main
contributions.
• We introduce for the first time a hybrid model combining
exponential smoothing (ES) with different deep learning models based on Recurrent Neural Network (RNN)
and Transformer architectures, and demonstrate how it
improves quality of the downstream anticipatory network
management tasks, with improvements in the 4%-26%,
20%-40% and 6%-16% range depending on the scenario.
• We update the operation of the state-of-the-art ES-RNN
architecture to cope with unique features of mobile traffic
dynamics; the result is an original Thresholded ES-RNN
(TES-RNN) model, i.e., a general-purpose network traffic
forecasting technique that can be tailored to perform
predictions for different network management functions.
• We apply the same methodology to the Transformer
neural network architecture, understanding the benefits
and trade-offs of the different approaches.
• We apply the proposed models to three practical
zero-touch management use cases, i.e., (i ) capacity allocation, (ii ) anomaly detection, and (iii ) load balancing,
for which we train the models with appropriate loss
functions.
• We evaluate the performance of our solutions against
recent works in the literature, demonstrating in all use
cases above its superior performance with respect to stateof-the-art Deep Neural Network (DNN) architectures.
This provides a substantial update with respect to our
previous work in [24], as we discuss the usage of
Transformer models in this context (to our knowledge,
the first attempt to integrate statistical modeling with
this architecture), improve the threshold selection of the
TES framework through an automatic and generalizable
Reinforcement Learning (RL) algorithm, and add the load
balancing use case to further showcase the adaptability of our
solution.
The paper is structured as follows: we detail the context
of the zero-touch network management and related work in
time series forecasting for networks in Section II. We discuss
the application of hybrid strategies that combine ML and
statistical modeling for forecasting in Section III and present
our proposed TES framework in Section IV. Finally, we
analyze a set of relevant use cases in Section V and their

351

performance evaluation in Section VI, before concluding in
Section VII.
II. R ELATED W ORK
Relying on a precise time-series forecasting algorithm is
a fundamental building block for many autonomous network
management and operation solutions [25]. Indeed, the quality
of the prediction plays a role in the overall performance of
the autonomous network management algorithm: with a more
precise forecast, the decision taken can guarantee a better
outcome. In the following, we revise the state-of-the-art solutions for autonomous and zero-touch network management,
with a focus on anticipatory networking. Finally, we explore
the works in the field of joint statistical modeling and ML,
which is the solution we adopt in this paper to improve the
forecasting quality of pure DNN models.
Network Intelligence for zero-touch management.
Handling the escalating complexity of Beyond 5G (B5G)
networks with traditional human-in-the-loop approaches will
not be possible anymore. Instead, it is expected that current
management models will be replaced by zero-touch network
and service management technologies, which fully automate
the network operation and are presently being standardized [26]. As a result of this transition, the success of B5G
will vastly depend on the quality of the Network Intelligence
(NI) that will run at schedulers, controllers, and orchestrators
across network domains, de-facto managing the zero-touch
infrastructure.
Following a popular trend in many research and engineering domains, AI models relying on DNN architectures
are regarded as a promising approach for the design of NI
solutions. Indeed, AI models have proven remarkably effective
at solving complex network operation tasks, and they thrive
on the large amount of control and traffic data available within
network architectures [27].
Forecasting for anticipatory networking. Many NI solutions build upon anticipatory networking principles and aim
at proactively optimizing network configurations with respect
to upcoming traffic conditions rather than to the current
state [11]. The prominence of anticipatory NI makes predicting
future network states a fundamental task for the effective
operation of B5G systems. Forecasting is in fact a manifold problem in networking environments, where different
applications require accurate future projections of diverse
metrics, including computational resources [28], capacity
requirements [14], or sheer traffic volumes [12], possibly
separated by mobile service [13].
Similarly to what happens for other aspects of NI design,
DNN models have lately been established as the prevailing
approach to developing the predictors that will support proactive decisions by NI solutions. In the past few years, a fairly
large body of works has explored varied DNN architectures,
which target diverse forecasting objectives, and are typically
proven to yield improved accuracy over legacy statistical
models.
Joint statistical modeling and DNN. While current stateof-the-art predictors in the networking domain invariably

352

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

rely on deep learning, very recent results from the ML
community suggest that hybrid engines that integrate statistical
modeling and DNN can, in fact, substantially outperform pure
DNN approaches in time series forecasting tasks. The very
first model of this kind comfortably won the renowned M4
Competition, a challenge for data scientists to develop ever
more accurate time series predictors [23]. It did so by beating
a variety of statistical and ML benchmarks, as well as 48
competitor solutions, across 100,000 experiments.
The aforementioned engine combines a classical ES statistical model with a RNN architecture, hence it is named
ES-RNN [22]. It is a true hybrid predictor since the parameters
of the ES model are optimized concurrently with the RNN
weights using unified gradient descent. Thanks to this joint
training, the ES-RNN model represents a leap forward with
respect to previous attempts at mixing different statistical
and/or ML methods: unlike simple combination [29] or ensemble [30] strategies used to date, this technique takes full
advantage of the strengths of statistical and ML methods, while
mitigating their respective limitations.
III. H YBRID N ETWORK KPI P REDICTION W ITH M ACHINE
L EARNING AND S TATISTICAL M ODELING
The hybrid prediction approach proposed in this paper
builds upon the innovative design principles first introduced
by the recent ES-RNN engine [22], which is presented
in Section III-A. The considered ES-RNN predictor has
limitations when confronted with real-world mobile traffic
dynamics, as discussed in Section III-B. Our proposed hybrid
methodology enhances the structure proposed in [22] and
solves such issues by enhancing the original engine with
an automatically learned threshold parameter, as detailed in
Section IV-B.
A. ES-RNN and Joint SGD Optimization
ES-RNN is a truly hybrid forecasting model for time series
that mixes statistical modeling, i.e., ES, and ML, i.e., RNN.
We consider the GPU implementation of ES-RNN [31] as the
basis for our study: this variant presents a first pre-processing
layer for adaptive and local normalization of input time series
using ES formulas, followed by a neural network architecture
that processes the normalized data and provides forecasts over
a customizable time horizon.
The original ES-RNN may adopt a variety of ES expressions, depending on the temporal features of the target data.
In networking settings, 24-hour circadian rhythms are known
to dominate the fluctuations of mobile data traffic [32], hence
we opted for a Holt linear non-seasonal ES formula [33],
which is the recommended expression for time series with
daily periodicity [22]. At each time step t, the non-seasonal
ES updates a normalization coefficient lt (called level) as
lt = ωyt + (1 − ω)lt−1 ,

(1)

where ω ∈ [0, 1] is the exponential smoothing parameter, and
yt represents the value of the input time series at time step t.
The level lt is used for data normalization. At a given
time step t, all values in the input window [t−tI , t] of size

I and in the output interval [t+1, t+tO ] of size O are
divided by lt . During training, the normalized input window
is fed to the RNN, whose (normalized) forecast is compared
with the normalized output window using a loss function. In
testing, or when running the model in production systems,
de-normalization is performed by multiplying the normalized
values forecasted in the prediction horizon O by the level lt .
The major novelty of the ES-RNN model is that the smoothing parameter ω is treated as a system variable that is learned
together with the weights of the subsequent RNN architecture.
In other words, the stochastic gradient descent (SGD) process,
normally used to fit the RNN weights, backpropagates in
this case before the neural network input layer, and into
the preceding ES model, where it updates ω. In this way, a
single SGD allows for jointly optimizing the parameters of the
statistical model and the neural network, adapting them all to
the characteristics of the target time series.
The SGD optimization of ω operated by ES-RNN results
in a level lt that is dynamically adapted to the input data. In
turn, this enables a so-called local and adaptive normalization,
which (i) ensures that all portions of the time series are equally
important to the ensuing neural network training process,
and (ii) suitably smooths the ML input so that the neural
network can concentrate on predicting actual trends, without
overfitting on spurious patterns [22]. Thus, this normalization
helps forecast time series with severe fluctuations, like those
observed in mobile networks. This is not the case with
traditional global normalization of all values to the same [0, 1]
interval, which does not yield input smoothing and makes it
hard for the RNN to learn to predict small values.
B. Limitations of Hybrid Predictors With Network KPIs
The ES-RNN model is intended to operate on a time
series with strictly positive values of comparable magnitude.
However, this assumption is often violated in the mobile
networking context, where KPIs observed at the radio access
and edge network elements are highly irregular and bursty,
with continued inactivity periods that lead to a possibly
significant presence of zero or near-zero values and severe
underutilization of the network. This consideration holds
for both voice [34] and data [32] traffic, especially when
predictions target demands generated by individual users or at
single base stations.
These characteristics of mobile traffic dynamics determine
levels lt computed with (1) that are at times equal to zero,
or close to that value. In the case of zero-level values, ES
normalization is simply not possible, as it would involve
a division by zero. In the case of values close to zero,
value discontinuities between the input and output windows
yield normalized outputs that are not numerically comparable
with (and in fact much higher than) the values predicted by
the neural network; the loss function returns then inflated
costs that hinder the quality of the learning process. Figure 1
illustrates the latter problem in a practical scenario. Plot
(a) portrays the real-world demand generated by Instagram
at one base station for several hours: the inconsistent nature
of the traffic, with a long period of very low or no activity,

SCHIAVO et al.: THE TES FRAMEWORK: JOINT STATISTICAL MODELING AND MACHINE LEARNING

Fig. 1. Example of problematic prediction of real-world mobile traffic by
ES-RNN. (a) Instagram demand at one BS. (b) The same demand is compared
to the prediction generated by ES-RNN trained with a Mean Squared Error
(MSE) loss function, using an input window of size I = 6 and an output
window of size O = 1.

353

This architecture consists of encoder and decoder layers,
which enable the model to focus on relevant parts of the
input sequence dynamically. The parallel processing capability
significantly accelerates training and inference times, making
Transformers suitable for large-scale time series datasets.
We corroborated this fact in a set of training experiments
that we executed for the experimental evaluation detailed in
Section VI, where we compare the time elapsed for training
and the retained loss on the same training data, for the RNN
and Transformer architectures. Pure transformer-based solutions could be trained generally one order of magnitude faster
(less than 1s vs. tens of seconds) than RNN solutions. The
advantages in training time that the Transformer architecture
has are beneficial for the automatic thresholding feature that
we propose in this work. See Table IV for more details.
B. Improved Statistical Modeling

is evident. Plot (b) shows how, when a traffic peak occurs
after such a sequence of low-traffic time steps, the network
starts predicting amplified values largely above the real traffic
demand.
IV. TES F RAMEWORK
Motivated by the analysis performed in Section III, we propose a hybrid methodology for the forecasting of time series
for network management purposes. The methodology is composed of (i) a module that introduces the statistical modeling
part through ES, and (ii) a dynamic thresholding (T) module
that counters the problem discussed in Section III-B, building
hence our TES framework. The overall framework is depicted
in Figure 2.
A. Neural Network Predictors
One of the goals of our work is to demonstrate the wide
applicability of the TES approach, independently of the model
used for the actual forecasting of the time series. We consider
hence two models for time forecasting: the Recurrent Neural
Network already used in [24] and a Transformer architecture [35], whose capabilities in time series forecasting have
been recently studied.
1) RNN: RNNs are a class of neural networks designed
for processing sequential data, making them particularly
well-suited for time series forecasting. Unlike traditional
feedforward neural networks, RNNs possess an internal state
that allows them to retain information from previous inputs,
enabling the modeling of temporal dependencies. This ability
to maintain a memory of past observations makes RNNs
effective in capturing patterns and trends over time, a very
good feature for accurate time series prediction.
2) Transformer: Initially introduced for natural language
processing tasks, the transformer architecture [36], [37] has
been used for time series forecasting [38], [39], [40] due to
its ability to handle long-range dependencies and parallelize
computation. Unlike RNNs, Transformers do not rely on
sequential data processing; instead, they employ self-attention
mechanisms to weigh the importance of different time steps,
capturing complex patterns and relationships within the data.

As introduced in Section III-B, deep learning models suffer
from noisy data with zeros. For these reasons, we introduce
a thresholded version of the two models discussed below,
following the framework in Figure 2.
1) TES-RNN: To address the shortcomings of the original
ES-RNN, we introduce the Thresholded ES-RNN (TES-RNN)
model. Our solution employs a threshold τ to bound the
minimum value of lt , which is then updated at each time step
t as
lt = max{τ, ωyt + (1 − ω)lt−1 }.

(2)

The enhancement in (2) is simple yet effective in solving
the issues observed for ES-RNN. A representative example
is provided in Figure 1(b): TES-RNN does not suffer from
inflated predictions and correctly anticipates the growing
traffic.
2) ES-Transformer and TES-Transformer: To improve the
performance of the original Transformer model, we adopt
equation (1) to introduce the ES-Transformer model with an
unbounded adaptive normalization of the inputs. However,
similar shortcomings observed for ES-RNN are also observed
for ES-Transformer. Therefore, we introduce a Thresholded
ES-Transformer (TES-Transformer) model to address those
limitations. TES-Transformer adopts a conditional two-stage
normalization scheme: in the first stage, a normalization
coefficient lt is computed as in equation (1) to normalize the
values in the input window [t−tI , t]. Then, a threshold τ
is used to scale the maximum value of the normalized input
window to get a second-stage normalization coefficient ltmax
as
ltmax = τ · max λ(t).
[t−tI ,t]

(3)

In the second conditional stage, if ltmax is bigger than a
guard value δ, then ltmax is used to further normalize the
input window to avoid the training artifacts of the original
Transformer and ES-Transformer models.
C. Effect of ES and TES Normalization
The effect of the normalization discussed in Section III-A,
attained by applying equations (1), (2) and/or (3) depending

354

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

Fig. 2. The architecture. The traffic Λ observed over the past I time steps is input to the TES component for a local and adaptive normalization of
non-negligible traffic above τ . The resulting traffic λ is fed to the model of choice, which outputs a forecast θ of traffic within a horizon of O time steps.
During training, the loss computed from θ is used to learn the threshold hyperparameter τ of the TES block in an AutoML style via a Reinforcement Learning
algorithm.
TABLE I
T RAINING T IME OVER 20 E POCHS AND N ORMALIZED MSE OF
F ORECASTING M ODELS P REDICTING FACEBOOK T IME S ERIES

Fig. 3.

Input values with different kinds of normalization.

on the model, can be observed in Figure 3, which shows
training inputs over two consecutive days. While the global
normalization scales all the input values to the same [0, 1]
interval, the other normalizations yield better input smoothing and ease the prediction task for small values, i.e., low
overnight traffic values. The benefits of the latter normalization
on the forecasting performance will be discussed in detail in
Section VI.
D. Comparative Analysis and Impact of Stationarity
To select the best internal design for the TES framework, we conducted a preliminary comparison of recent
forecasting models based on Transformer and linear
architectures, including Informer [35], Autoformer [41],

pure Transformer [36], N-BEATS (Neural Basis Expansion
Analysis for Time Series) [42], and D-Linear [43]. As shown
in Table I, although Informer and Autoformer yielded a
slightly lower normalized MSE, the Transformer offered a
much shorter training time, a critical parameter given the
complexity introduced by the TES framework for, e.g., finding
the best τ . Importantly, TES compensates for the modest
accuracy gap of the pure Transformer, improving the final
performance as will be shown later in Section VI.
Another important aspect we take into account while
designing the internal model of the TES framework is the
impact of the stationarity of the input time series, which
has been discussed in the literature [44], [45], [46] as an
important metric for assessing the complexity of forecasting
problems. Following these works in the literature, we evaluated
the stationarity of the traffic time series using Augmented

SCHIAVO et al.: THE TES FRAMEWORK: JOINT STATISTICAL MODELING AND MACHINE LEARNING

Fig. 4.

355

Distribution of Instagram time series over 2 individual days (leftmost plots) and 2 consecutive weeks (rightmost plots).

Dickey-Fuller (ADF) tests and statistical moments (mean, variance, skewness, and kurtosis). We found two different patterns:
daily data showed non-stationarity, with varying statistics and
ADF p-values above 0.05, while weekly aggregation revealed
stationary behavior, as illustrated in Figure 4. To assess the
robustness of our model, we trained the pure Transformer
model over temporally ordered weekly data (stationary) and
shuffled individual days (non-stationary). The performance
analysis, summarized in Table II, yields comparable accuracy
in both setups, showing that these models generalize well
across time shifts even for the non-stationary case, showing
how the model copes well with complex problems. The results
of Tables I and II are obtained using the time series of popular
services that will be introduced in Section VI, where we train
our models in larger stationary scenarios.
The results we presented in this section show that the TES
framework is general in nature, without any noticeable bias
on the kind of input data (e.g., stationary or not), and can be
applied to forecasting models beyond Transformers.

TABLE II
S YMMETRIC M EAN A BSOLUTE P ERCENTAGE E RROR (SMAPE)
B ETWEEN S TATIONARY AND N ON -S TATIONARY T RAINING

E. Parametrization of the Hyperparameter τ
The result in Figure 1(b) is not obvious to achieve. In
particular, the threshold τ is challenging to configure, as
it introduces an interesting trade-off. Generally, a threshold
closer to the traffic peak ensures higher robustness to the
problem of time series discontinuities highlighted above.
However, it also triggers a global normalization to level τ more
often, raising the issue of model insensitivity to low values
below the threshold that the local and adaptive normalization
aims at solving. Conversely, thresholds closer to the smallest
possible level tend to preserve the desirable properties of
the fine-tuned ES normalization but incur more often the
issues related to discontinuous data. These problems, which
are independent of the actual deep learning model used for
forecasting, require an automatic algorithm for the correct
setting of the τ .
There is no one-size-fits-all solution to the trade-off above,
and the best value of τ depends on the nature of the traffic time
series that is relevant to the target networking functionality.
Therefore, τ also needs to be adjusted to the settings of the
considered task. Notably, τ is a hyperparameter for the TES
models, as it steers the overall system behavior. To ensure a
smooth operation, it is highly desirable that the setting of τ
does not require human intervention, but is fully automated
and generalizable. The setup at hand calls for an Automated

Fig. 5.

Architecture of the soft actor-critic algorithm.

Machine Learning (or AutoML) approach, since our goal is to
automate the design of complex neural network models [47].
For this task, while in an earlier version of the framework [24] we used a Golden-Section search algorithm based
on convex loss functions [48], we now propose a more generalizable approach based on a RL algorithm that automatically
selects the best τ value. We resort to a soft actor-critic deep
RL algorithm to maximize an arbitrary reward function while
exploring as randomly as possible the space of possible τ
(action) values at training time through an entropy component.
The critic neural network estimates the effect of selecting
a given τ value for a state s, which captures the nature of
the traffic time series and is represented by its mean μ and
standard deviation σ. Such an effect is estimated using an
instantaneous reward function, which is the additive inverse
of the prediction loss obtained by forecasting the time series
with state s using the selected τ . Leveraging the estimates
of the critic for a given state s, the actor outputs the best τ
from a discrete action space with 20 possible values in the
range [0.05, 1] with step 0.05. The architecture of the soft
actor-critic algorithm is depicted in Figure 5.

356

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

V. A PPLICATION U SE C ASES
As discussed in Section I, forecasting future network
KPIs is a cornerstone task for many networking problems,
including admission control [49], capacity allocation [14],
handovers [50] and power management [51], among others,
which involve different operation time scales [8]. The TES
architecture described in Section IV-B is general-purpose and
agnostic to the specific networking application: it can be
trained to support different NI instances, e.g., by combining
it with a suitable loss function that allows optimizing the
model for a given prediction task. Next, we present two
practical anticipatory networking use cases where the TES
framework can be used as the forecasting model, which also
sets the ground for the experimental evaluation conducted in
Section VI.
A. Use Case I: Capacity Allocation for Network Slicing
A first use case of interest for forecasting in anticipatory
networking is that of capacity allocation, i.e., reserving the
resources needed to meet the upcoming demand for a given
service. This functionality is especially relevant in network
slicing settings, where (sets of) services run in different slices,
and the operator needs to dedicate sufficient resources to
each slice, in agreement with the load generated by the
corresponding service(s) [49].
The anticipatory NI in charge of capacity allocation to slices
must rely on so-called capacity forecasting, i.e., predicting the
minimum capacity sufficient to accommodate the future slice
traffic. We highlight that capacity forecasting is a fairly unique
problem, where sheer accuracy is not the most relevant metric.
Instead, the prediction must stay above the actual load with
a very high probability, because underestimation determines
the allocation of insufficient capacity to slices, hence service
disruption on the user side. Underprovisioning also triggers
violations of the Service Level Agreement (SLA) between
the slice tenant and the network operator, which thus incurs
substantial economic penalties. Clearly, this must be avoided
without allocating exceedingly large amounts of unnecessary
resources, which also has a cost for the operator.
The problem of capacity forecasting has recently received
attention, with the proposal of dedicated predictors [8], [14].
These models rely on a loss function that drives the learning
process to capture the actual cost of incurring SLA violations
against that of overprovisioning the slice capacity. Specifically,
the function handles negative and positive errors differently,
to reflect the different costs they entail in the context of
virtualized communication networks, as follows.
• A constant penalty β is associated with each negative
error, which causes an SLA violation during the predicted time interval. β can be customized to the desired
behavior: for instance, higher values may be used when
reliability is paramount (e.g., for slices serving ultrareliable low-latency communications or URLLC), and
lower penalties can be applied for slices with more
relaxed requirements.
• A monotonically increasing cost is attributed to positive
errors, which imply the allocation of excess resources.

Therefore, the cost is proportional to the amount
of (unnecessarily) provisioned capacity. Typically, the
expenditure is assumed to grow linearly with the overprovisioned capacity, with a fixed rate γ of cost per surplus
capacity.
The configuration of the two costs can be, in fact, controlled
by a single parameter α = β/γ, which represents the amount
of overprovisioned capacity that the operator is willing to
deploy to avoid committing an SLA violation. Formally, for a
given prediction error x , the loss function that abides by the
specifications above is expressed as
⎧
⎨ α − · x if x ≤ 0
(4)
L(x ) = α − 1 x
if 0 < x ≤ α
⎩
x− α
if x > α,
where steep slopes (implemented with a small positive )
ensure differentiability over the whole x domain [14].
The parameter α serves as a knob to steer the operational
point of the system towards higher expenses in deployed
resources but reduced chances of SLA violations, or viceversa. As a result, the loss function in (4) can be parametrized
to the specifications of different network infrastructure locations (e.g., reflecting the higher cost of deploying resources
at the network edge than at the core), resource types (e.g.,
capturing the fact that radio resources are sensibly more
expensive than CPU resources), and SLA strategies (e.g.,
expressing the higher fees for violations affecting slices of
critical services).
B. Use Case II: Anomaly Detection in Mobile Service Traffic
The second use case we study is an anticipatory anomaly
detection framework, where the NI must trigger an alarm when
an abnormal future traffic load is expected for a specific mobile
service. The anomaly detection problem is summarized in
Figure 6(a). The predictor module is in charge of producing
a probability distribution of the traffic demand that the target
service will generate in the next time slot. Such a probabilistic prediction is compared against a reference interval that
encompasses the expected range of normal traffic values in
the following time slot. Then, if the probability of the anticipated traffic being outside the reference interval is beyond a
threshold, an alarm is raised. This allows the associated NI
to perform some preventive actions, such as those detailed in
the 3GPP TS 23.288 [52] technical specification under the
“Abnormal behavior” analytics, which capture anomalies such
as unexpected large rate flows generated by terminals.
We consider a simple yet practical implementation1 of the
approach above that is commonly adopted in many fields, also
outside networking [53]. First, it is worth noting that the output
of the forecasting algorithm shall not be a scalar but a probability distribution of the future traffic load. This type of output
is implicit in certain types of models like Bayesian Neural
Networks, which are, however, computationally expensive and
not suited for resource-constrained network environments.
1 Our goal is not to propose a novel anomaly detection algorithm, but to
compare the effectiveness of different forecasting models in supporting such
a task. Therefore, we are not interested in developing a complex algorithm for
anomaly detection, and using a baseline solution is sufficient for our purpose.

SCHIAVO et al.: THE TES FRAMEWORK: JOINT STATISTICAL MODELING AND MACHINE LEARNING

357

•

Fig. 6.
Anomaly forecasting use case. (left) Representation of the
anomaly forecasting problem. (right) Explanation of the operation of anomaly
detection.

In order to generate a probabilistic forecast with a generic
neural network, we resort to recent findings in uncertainty
modeling [54]: specifically, by activating dropout layers in the
predictor during the inference phase and performing a Monte
Carlo test, the neural network returns a set of values that have
been shown to closely approximate the probabilistic result of a
deep Gaussian process implemented with a Bayesian network.
The anomaly detection algorithm then operates on the
empirical Probability Density Function (PDF) fp of the predicted traffic values for each decision interval, as illustrated
in Figure 6(b). First, the upper and lower limits that mark
the boundaries between regular and anomalous values are
computed as xl,h = R ± ΔA , where R is a configurable
reference value. From these two values, the probability of
a future anomaly is empirically calculated
 as PA = 1 −
(Fp (xh ) − Fp (xl )), where Fp (x ) =
k <x fp (k ) is the
Cumulative Distribution Function (CDF) of the anticipated
traffic. Finally, an alarm is triggered if PA > τA . The
parameters R, ΔA , and τA control the sensitivity of the
algorithm. In our experiments, we set the reference values for
the estimated load in the next prediction step R as the average
of the last three load values, ΔA = 0.9 · R, and τA = 0.9.
In other words, we trigger an alert when the model forecasts
future traffic with a 90% probability to fall outside a range
±90% of the reference value.
The correctness of the anticipatory anomaly detection can
be determined by checking whether the actual traffic falls into
the xl,h interval or not, and computing precision and recall
scores. Clearly, a higher accuracy in the probabilistic traffic
forecast, denoted by a lower variance around a value closer to
the true one, yields better performance: a MSE loss function
is thus a sensible choice for this use case.
C. Use Case III: Anticipatory Load Balancing
Load balancing aims at equally splitting the load among
different entities and is another networking functionality for
which forecasting is critical. Indeed, anticipatory load balancing can be applied at different levels, including the following.
• Load balancing at edge clouds. In edge cloud facilities,
e.g., for Cloud Radio Access Network (C-RAN), it is
desirable to associate base stations with data centers in
such a way that the future traffic load channeled to each
data center is balanced, and no data center will suffer
congestion and reduced performance.

Load balancing for network slicing. Under slicing
models, network entities must run dedicated, customized VNFs to serve the traffic associated with each
slice. Operators then have to map slices to network
nodes, ensuring that the upcoming VNF load is evenly
shared across the latter, to optimize the global system
performance.
• Load balancing at base stations. In the presence of
increasingly dense network deployments, users are offered
an increased choice of candidate base stations for
association. Forecasting allows operators to make informed
decisions on new user associations and equalize the charge
across base stations to ensure service continuity.
Independent of the problem variant, anticipatory load balancing requires a prediction of future traffic that is as accurate
as possible. In this case, whether the prediction falls above
or below the actual load is irrelevant: any deviation of the
prediction from the actual demand causes an imbalance in
the resulting load that only depends on the error magnitude,
hence a negative error is not more harmful than a positive
one. For the purpose of evaluation, we focus on the third
problem above, i.e., load balancing at base stations. This
type of task is run in modern networks, for instance, by the
Policy Control Function (PCF) through the User Equipment
(UE) Route Selection Policy (RSP) [55]. The PCF assigns
an incoming UE to a Protocol Data Unit (PDU) session or
network slice, once the UE is activated. The availability of
an accurate prediction of future traffic at each base station
allows the NI deployed at the PCF to drive the assignment
in a way that the ensuing load is leveled across the radio
access infrastructure. As mentioned above, this type of load
balancing requires a traditional mobile traffic forecasting
model to operate in an anticipatory fashion. We thus rely
on a conventional loss function that weights equally negative
and positive errors, i.e., the MSE. Based on the traffic load
predicted with this loss function, a load balancer performs the
corresponding mapping to equalize the (expected) load at the
different entities. In the case of load balancing at base stations,
forecasting is naturally performed on traffic loads at the base
station level; then, the load balancing NI engine running at
the PCF manages each association request by assigning the
soliciting UE to the base station with the lowest forecasted
load.
VI. P ERFORMANCE E VALUATION
We assess the performance of the proposed TES framework
in the two use cases set out in Section V, hinging on real-world
mobile traffic measurement data collected in an operational
network. Specifically, we consider mobile data traffic time
series recorded at more than 400 4G/LTE base stations that
provide coverage to millions of subscribers in a metropolitan
area.2 The data was collected in the production infrastructure
of a major operator during 11 continuous weeks, by passive
probes tapping at interfaces of the Gateway GPRS Support
2 Due to confidentiality reasons, we cannot disclose the identity of the
operator, the target geographical region, or the absolute volumes of traffic
captured in the data. We thus either normalize the traffic values or report them
without the scaling factor that would reveal their order of magnitude.

358

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

TABLE III
S UMMARY OF E XPERIMENTAL S ETTINGS

Node (GGSN) and Packet Data Network Gateway (PDNG) in
configurable intervals ranging from 5 to 15 minutes.
The measurement probes leverage Deep Packet Inspection
(DPI) to extract protocol information from packets in
the GPRS Tunneling Protocol user plane (GTP-U). Such
information is then fed to proprietary classifiers developed
by the operator to determine the service associated with each
session. As a result, the time series we use in our evaluation
describes the traffic generated by individual popular services.
All time series have the finest temporal granularity allowed
by our dataset, which is 5 minutes. This temporal granularity is
compatible with the requirements of the three target use cases,
since (i ) the reconfiguration periodicity of slice resources
allowed by modern Virtual Infrastructure Managers (VIM) is
in the order of minutes [56], and (ii ) anticipating anomalies or
(iii ) balancing load by several minutes is largely sufficient to
plan and enact countermeasures. Therefore, a prediction of the
traffic in the next 5-minute time step (i.e., a point forecast of
the time series) is aligned with the use cases, and we consider
an output window size O = 1 in all our experiments. Also, we
use an input window size of I = 6 time steps to feed the model
(corresponding to a history of 30 minutes), and we employ
8, 2, and 1 different weeks of traffic for training, validation,
and testing, respectively. The guard value for TES-Transformer
second-stage normalization is δ = 0.001. All the experimental
settings are summarized in Table III: training, validation, and
test sets include both on-peak and off-peak behavior, following
a night-day, weekday-weekend pattern [57].
As a final remark, we highlight that our study observes
high privacy and ethical standards: (i ) the network operator
conducted the data collection abiding by applicable regulations
at national and international levels; (ii ) the competent national
privacy agency and the data protection officer of the operator
authorized the data processing; and, (iii ) the time series we
accessed for the purpose of this work solely describe traffic
aggregated at individual base stations over large sets of users,
and do not contain personal subscriber information.

A. Forecasting for Capacity Allocation
We set the capacity allocation use case presented in
Section V-A in a network core Cloud scenario, where a
data center runs VNFs for the traffic generated in the whole
target region by three traffic-intensive mobile applications,
i.e., Facebook, Instagram, and Snapchat. Each such service is
assigned a dedicated network slice, and the NI responsible for
capacity allocation at the data center must reserve in advance
enough resources to accommodate the future demand of single
slices.

Fig. 7. Additional capacity allocation cost caused by state-of-the-art models
(INFOCOM19, RNN, Transformer, and ES-RNN, in blue), and the proposed
in this paper (ES-Transformer and TES models, in red) prediction errors.
Results refer to three slices assigned to specific services at a network core
data center, with parameter α = 3.

To address this problem, we train the models used in
TES with the appropriate loss function in (4) and compare our hybrid solution against the following four relevant
benchmarks:
• INFOCOM19 [14] is the predictor designed by the study
that first introduced the problem of capacity forecasting
and proposed the loss function in (4). It relies on a DNN
architecture fed with a 3D tensor of the spatiotemporal
mobile data traffic and uses convolutional layers to capture geographical correlations in the demands. This is the
state-of-the-art forecasting model for capacity allocation.
• ES-RNN [22] is the GPU implementation of the original
ES-RNN approach presented in Section III-A. For the
sake of fairness, ES-RNN is trained with the loss in (4).
• RNN uses the same RNN architecture of ES-RNN, but
relies on a global normalization for the input data, thus
without any of the optimizations proposed in this work
and in [22]. This benchmark is useful for understanding
how statistical modeling favors prediction accuracy. We
also train this benchmark with the loss function in (4).
• Transformer uses the model first introduced in [58],
which is also the basis of our ES-Transformer and TESTransformer models. For this baseline model, we use the
loss function in (4) as well.
1) Overall Capacity Forecasting Performance: We start by
comparing the total costs incurred by the operator when
supporting capacity allocation with the different forecasting
models, in Figure 7. In order to make these values interpretable, all costs are normalized to the (unavoidable) cost
of the minimum resources needed to accommodate the exact
demand for each service. In other words, costs are expressed
as the percent excess over a baseline given by an oracle that
makes a perfect prediction. In each case, the figure also tells
apart the fraction of the cost resulting from the two sources
of penalty, i.e., resource overprovisioning and SLA violations.
We group results into state-of-the-art approaches (blue bars
in Figure 7) and our three proposals: ES-Transformer, TESRNN, and TES-Transformer.
The key observation is that our approaches consistently
outperform the benchmarks, with gains over the second-best

SCHIAVO et al.: THE TES FRAMEWORK: JOINT STATISTICAL MODELING AND MACHINE LEARNING

Fig. 8.
Time series of the real traffic generated by the Facebook slice
and of the relative capacity predictions of the different forecasting models.
(top) Weekly time series, with highlighted time intervals for close-in analysis.
(middle) Zoomed view of the 3:00-7:00 interval of Tuesday. (bottom) Zoomed
view of the 12:00-16:00 interval of Friday. Whenever present, SLA violation
periods are marked as red-shaded areas in the plots.

solution that range between 4% and 26%. The different
TES approaches yield distinctive results. In general, the ES
approach, with or without the τ selection, improves the
performance of the state-of-the-art algorithms. For instance,
TES-RNN steadily guarantees very low SLA violation probabilities, which is a desirable feature for the operator. And,
it does so by causing an overprovisioning that is lower than
or comparable to that produced by the other predictors. These
are very encouraging findings, as one of the benchmarks is
the state-of-the-art model designed for capacity forecasting.
Interestingly, ES-RNN yields an allocation of unnecessary
resources close to that of TES but incurs much more frequent

359

SLA violations. Transformer, in both the ES and TES configurations, improves the performance of the pure Transformer
counterpart for all the services, although TES-Transformer
incurs a higher SLA violation rate due to its aggressive
forecasting. INFOCOM19, RNN, and Transformer, when compared to TES, induce a substantially higher overprovisioning
that often helps limit SLA violations, at the expense of an
overall higher expenditure.
2) In-Depth Analysis of One Prediction Instance: To gain
an additional understanding of the behaviors of the forecasting
models presented above, we detail a representative case of
capacity prediction in Figure 8. The plots show the time
series of the real traffic in the Facebook slice, as well as the
corresponding capacity allocation foreseen by each predictor.
Plot (a) portrays the traffic dynamics over a full week and
underscores how all models follow well the long-timescale
fluctuations of the demands, such as low overnight traffic
or different activity peaks during daylight. Plots (b) and
(c) present a close-in view of two specific 3-hour periods,
which are evidenced by vertical shades in plot (a). The zoom
magnifies how TES and ES-RNN help dimension a capacity
that is closer to the real demand than that anticipated by
INFOCOM19 and RNN, especially in low traffic conditions.
Plot (b) also exemplifies the reason for the poor performance
of ES-RNN in terms of high SLA violations: when used in
combination with the loss function in (4), the model has issues
in anticipating small variances in the traffic fluctuations, which
causes the capacity forecast to come too close to the future
demand. The result is frequent underprovisioning: for instance,
ES-RNN assigns insufficient resources to the Facebook slice
in multiple periods in the considered example, highlighted
by the red intervals on the abscissa in the figure. Instead,
ES-Transformer and TES models forecast a smoother capacity
curve that stays above minor fluctuations, and hence yield a
resource provisioning similar to ES-RNN but while avoiding
numerous SLA violations.
3) Control of SLA Violations: The results presented before
are for one specific value of the parameter α that controls the
equilibrium of overprovisioning and SLA violation risk in the
loss function in (4). By varying the parameter, the operator
shall be able to steer the capacity forecast to favor one source
of cost over the other, as explained in Section V-A.
Figure 9 illustrates the capability of each model to enforce
the desired control above by trading off overprovisioning cost
with SLA violations cost. The plot shows, for the case of
the Facebook slice, the normalized cost determined by each
predictor, as α sweeps values from 1 (relatively low SLA
violation cost) to 5 (high SLA violation cost). We observe that
TES-Transformer and TES-RNN yield the best performance
in all settings. Also, TES-RNN keeps the overall cost low by
progressively decreasing the occurrence of SLA violations as
α grows, which is exactly the desired behavior. INFOCOM19
and RNN can also achieve this result, however, at a cost
in terms of overprovisioning that is almost twice that of
TES-RNN. ES-RNN is instead unable to modulate the SLA
violation cost, which in fact surprisingly grows with α.
The reason for the counter-intuitive ES-RNN performance
can be explained by the breakdown of the two cost sources,

360

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

benchmarks. ES-RNN allows staying at low overprovisioning
levels as well, but SLA violation rates cannot be controlled
even with very aggressive α settings, as discussed before. In
contrast, both INFOCOM19 and RNN can limit SLA violation
rates, but without a clear (and relatively high) bound on the
minimum overprovisioning costs achievable. As a result, the
proposed models bring the best of the other models: for any
possible operating point of INFOCOM19, ES-RNN, or RNN,
we can choose an α that improves cost on both dimensions.
B. Forecasting for Anomaly Detection
Fig. 9. Additional capacity allocation and SLA costs of INFOCOM19, RNN,
Transformer, ES-RNN, ES-Transformer, and TES models versus α and for
the Facebook slice.

Fig. 10. Limits in terms of SLA violations and overprovisioning costs that
can be attained by ES models, TES models, and the chosen benchmarks for
the Facebook slice.

in Figure 10. The plot illustrates, for each case in Figure 9:
(i ) on the ordinate, the overprovisioning, still expressed as the
added cost over that of the optimal oracle; and, (ii ) on the
abscissa, the SLA violations, measured as the percentage of
5-minute time steps during which the allocated resources are
insufficient to serve the slice demand. The trends are consistent
across all models, and higher values of α always entail fewer
violations, as one would expect. However, while TES models,
INFOCOM19, and RNN can rapidly bring underprovisioning
cases down to zero when α surges, the ES-RNN model is
much less sensitive to the parameter. Specifically, this predictor
reduces SLA violations at a slower pace than the rate at which
α increases: by looking at the extreme cases in the plot,
ES-RNN lowers violations by just one-third when α grows
20-fold. As α represents the cost of one SLA violation, the
cut in the number of occurrences is insufficient to compensate
for the higher penalty of each infraction, which explains the
growing trend of the SLA violation cost under ES-RNN in
Figure 9.
More generally, Figure 10 gives a clear view of the operating points of each forecasting method. ES-Transformer and
TES models offer the best options to the operator, as their
configurations simultaneously provide fewer SLA violations
and lower overprovisioning costs than the state-of-the-art

The second use case we consider is that of anomalous load
detection at base stations introduced in Section V-B. We set
this use case in a virtualized network environment running
an end-to-end network slicing model, where proactive load
anomaly detection is paramount for the timely identification
of undesired situations that could be amended by, e.g., new
network configurations. In such settings, the anomalous load
detection NI operates at the granularity of individual services.
Specifically, we run experiments for slices that each accommodate one of three different services, i.e., Facebook, Instagram,
and Snapchat. For each slice, we consider different base
stations and assess the performance of the anomaly detection
algorithm discussed in Section V-B that relies on forecasting
models of the slice traffic at each such base station.
To support the anomaly detection decision, the proposed
models (ES-Transformer, TES-Transformer, and TES-RNN)
are trained with an MSE loss function, according to the
discussion in Section V-B. With such a loss function, our
models operate as traditional mobile traffic forecasting models;
this steers our choice of benchmark to the following models.
• Long Short-Term Memory (LSTM) is a simple NNbased model made of two fully-interconnected layers that
is not specifically designed for mobile network traffic
forecasting at base station level.
• INFOCOM17 [12] is a popular forecasting technique that
is explicitly designed to predict mobile network traffic
at the level of individual base stations. It leverages a
DNN architecture where both global and local SAE layers
are used to learn spatial features in the data, followed
by LSTM layers that capture temporal correlations. This
benchmark represents the state of the art in point forecast
at the base station level, i.e., the problem at hand; while
other, more recent predictors of mobile traffic volume
have been proposed in the literature, they target different
objectives, such as forecasting over a very long time
horizons [59], or forecasting for the radio access [60].
• ES-RNN, RNN, and Transformer, as discussed in
Section VI-A. In this case, the models are trained with
an MSE loss function.
1) Mobile Traffic Prediction Accuracy: We start our assessment by comparing the sheer accuracy of the proposed models
against the benchmarks in the task of point forecasting mobile
traffic at base stations. We also consider for comparison a
Naive model, which uses the current value of the timeseries to
predict the value of the following timestep. Figure 11 shows
the results for all models and services averaged over five

SCHIAVO et al.: THE TES FRAMEWORK: JOINT STATISTICAL MODELING AND MACHINE LEARNING

361

Rate (FPR), for all the considered τA in the range between
30% and 95%. TES-Transformer, instead, yields intermediate
performance when compared to the other benchmarks.
C. Forecasting for Load Balancing

Fig. 11.
Prediction accuracy in terms of MSE for Naive, LSTM,
INFOCOM17, RNN, Transformer, and TES forecast.

different base stations. We remark that results for the ES
models are not shown because, as extensively explained in
Section IV-B, training such models with an MSE loss function
in the presence of mobile data traffic yields exceedingly high
overestimation (see, e.g., Figure 1). Independent of the test
configuration, TES-RNN yields the most accurate prediction:
the average MSE reduction across all base stations is in
the 20%-40% range, peaking at 55% for the Facebook case
when compared to INFOCOM17 and at 90% for the Snapchat
service in comparison to the Naive model. TES-Transformer
yields performance similar to that of TES-RNN.
2) Anomaly Detection Performance: Having observed the
superior accuracy of TES-RNN mobile traffic prediction, we
investigate how this reflects on the actual performance of
the anomaly detection. We emulate the situation in which
the network analytics function of a mobile network gathers
data from the User Plane Function (UPF) [52] to monitor,
e.g., the excessive usage of the network by a terminal, and
has to generate an alarm if such an event is anticipated
to happen in the near future. We consider for our test a
scenario where different base stations are monitored with the
algorithm introduced in Section V-B. Figure 12(a) shows the
performance of all the benchmarks in terms of F1 Score,
averaged over the five selected base stations, for the three
selected application types. TES-RNN always achieves the best
performance, while competitors provide unbalanced results,
highly depending on the considered application. In particular,
the average F-Score gain of TES-RNN across all services is
in the 0.1-0.15 range, peaking at 0.31 for Snapchat when
compared to ES-Transformer. The baseline ES-RNN and
the proposed ES-Transformer and TES-Transformer almost
always trigger the anomalous load alarm, as the predicted
values are often well above the thresholds (and the real values).
To further corroborate the quality of TES-RNN in this
kind of task, we also evaluate its effectiveness with variable
τA values in Figure 12(b), showing the ROC curve for the
selected benchmarks and proposed models. ES models are
not shown as their highly overestimated forecasts trigger a
huge number of false positives, which explains the poor ES
models performance in Figure 12(a). TES-RNN always yields
the best pairing between the Recall and the False Positive

The third use case we consider for the comparative evaluation is that of anticipatory load balancing at base stations
introduced in Section V-C. As in the use case of Section VI-B,
we also operate in a virtualized network environment running
an end-to-end network slicing model, where strong quality of
service guarantees are met by dedicating resources to different
slices already in the radio access. In such settings, the loadbalancing NI operates at the granularity of individual services,
and we consider three different slices, each accommodating
the three services of Facebook, Instagram, and Snapchat. For
each service, we consider different base stations and evaluate
the performance of a load balancer that leverages forecasting
models of the traffic at the slice for each such base station.
To support the load balancing decision, the proposed models
(TES-RNN and TES-Transformer) are trained with a suitable
MSE loss function, according to the discussion in Section V-C.
With such a loss function, also for this use case, we choose as
benchmarks the model LSTM and INFOCOM17 [12], as well
as the Naive model already presented in Section VI-B1. To
investigate the performance of a load balancer, we consider the
case of UE association performance. We emulate a UE initial
attachment or handover scenario in a dense deployment where
multiple base stations may offer similar radio channel quality.
A prominent criterion for UE association is the expected load
that each base station will experience in the following minutes;
in a sliced scenario, this becomes the demand generated by
a specific service at each candidate base station. To balance
the load across base stations, the soliciting UE should be
assigned to the base station with the lowest forecasted traffic
for the requested slice. As discussed in Section V-C, such
functionality is part of the 5G standard, and would run in
the load balancing NI engine at the PCF. We consider for
our tests a load balancer that, in the presence of a slice
association request that can be possibly satisfied by two base
stations, selects the one with the lowest anticipated load for
the requested slice in the following 5 minutes. The decision
is thus driven by the per-service traffic forecast performed by
the evaluated models.
Figure 13 shows the accuracy of the load balancer, i.e., the
fraction of UE association requests that are correctly directed
to the base station with the lowest load on a specific slice
in the following timestep. Decisions based on TES-RNN and
TES-Transformer predictions have an average accuracy close
to 70%, which is a decent performance for the very high
variance of traffic at 5-minute timescales. This is also 6%-16%,
15%-27%, and 13%-24% higher than the accuracy granted
respectively by INFOCOM17, LSTM, and the Naive model.
D. Complexity
We conclude by analyzing the complexity of the proposed
solutions, in terms of average training time over the same
number of epochs and memory usage for experiments running

362

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

Fig. 12. Comparing LSTM, INFOCOM17, RNN, Transformer, ES, and TES models. (left) F1 Scores obtained with the algorithm discussed in Section V-B,
and (right) Receiver Operating Characteristic (ROC) Curve for the Facebook service, for different τA thresholds. Subplots do not show results for the Naive
model due to the deterministic nature of its forecasts.

all the models are trained with the same MSE loss function.
Overall, TES-RNN and TES-Transformer can be trained as
fast as the respective less optimized models (i.e., ES-RNN
and RNN for the recurrent neural network architecture, and
ES-Transformer and Transformer) while guaranteeing the
advantages in the forecasting performance. This is obtained
with no additional burden on the memory of the GPU in which
the models run. The results reported in Table V show that
all the considered models require around 1400MiB, which
represents only 3.4% of the total memory of the A100 GPU.
VII. C ONCLUSION
Fig. 13.

Load balancing accuracy.
TABLE IV
T RAINING T IME OF THE B ENCHMARKS , IN M INUTES

TABLE V
GPU M EMORY U SAGE OF THE B ENCHMARKS , IN M I B

on an NVIDIA A100 GPU. The results for the first metric
are reported in Table IV: in the first use case, Transformer
models required on average lower training times than the
equivalent RNN models, while yielding similar performance
as observed at the beginning of Section VI. In particular, the
high-performing TES-Transformer model required an average
of 2.45 minutes per capacity allocation experiment, which is
in the order of the average training time of the less-performing
RNN model (2.85 min) but faster than the equivalent TESRNN model with a mean of 5.1 minutes per run. Similar
considerations apply to the second and third use cases, where

In this paper, we explored the potential of statistical
modeling for anticipatory traffic management using deep
learning. By avoiding high average-to-peak ratios in the input
training data ES allows a more efficient forecast of the traffic
time series. In this paper, we propose the TES framework,3
that effectively improves the normalization of bursty time
series through a factor τ and couple it to two different
neural network architectures based on RNNs and Transformer
architectures, to prove the solution flexibility. We benchmarked
both TES-RNN and TES-Transformer on three relevant use
cases for network management: capacity allocation, anomaly
detection, and load balancing. In the three scenarios, our
solutions achieve performance gains with respect to state-ofthe-art benchmarks in the order of, respectively, 4%-26%,
20%-40%, and 6%-16% range depending on the scenario. This
paper demonstrates the advantages of the TES framework in
time series forecasting, showing how it outperforms state-ofthe-art baselines. Our results prove that a hybrid approach can
enhance even advanced AI/ML solutions, paving the way for
future research that could extend the framework to models
beyond RNNs or Transformers. While we highlight these benefits, the challenge of understanding the limited performance
of forecasting techniques on network traffic remains a separate
research effort beyond the scope of this work.
3 The code of the TES framework is publicly accessible at the following
link: https://doi.org/10.5281/zenodo.16045349.

SCHIAVO et al.: THE TES FRAMEWORK: JOINT STATISTICAL MODELING AND MACHINE LEARNING

R EFERENCES
[1] M. Giordani, M. Polese, M. Mezzavilla, S. Rangan, and M. Zorzi,
“Toward 6G networks: Use cases and technologies,” IEEE Wireless
Commun. Mag., vol. 58, no. 3, pp. 55–61, Mar. 2020.
[2] R. Govindan, I. Minei, M. Kallahalla, B. Koley, and A. Vahdat, “Evolve
or Die: High-availability design principles drawn from Googles network
infrastructure,” in Proc. ACM SIGCOMM Conf., 2016, pp. 58–72.
[Online]. Available: https://doi.org/10.1145/2934872.2934891
[3] W. Wu et al., “AI-native network slicing for 6G networks,” IEEE
Wireless Commun., vol. 29, no. 1, pp. 96–103, Feb. 2022.
[4] F. Rezazadeh, H. Chergui, L. Alonso, and C. Verikoukis, “SliceOps:
Explainable MLOps for streamlined automation-native 6G networks,”
IEEE Wireless Commun., vol. 31, no. 5, pp. 224–230, Oct. 2024.
[5] L. E. Chatzieleftheriou et al., “Network intelligence in action: The
DAEMON perspective,” in Proc. Eur. Conf. Netw. Commun. 6G Summit,
Antwerp, Belgium, Jun. 2024, pp. 1–6.
[6] M. Milani, D. Bega, M. Gramaglia, P. Serrano, and C. Mannweiler,
“ATELIER: Service tailored and limited-trust network analytics
using cooperative learning,” IEEE Open J. Commun. Soc., vol. 5,
pp. 3315–3330, 2024.
[7] A. T.-J. Akem, M. Gucciardo, and M. Fiore, “Flowrest: Practical flowlevel inference in programmable switches with random forests,” in Proc.
IEEE Conf. Comput. Commun., 2023, pp. 1–10.
[8] D. Bega, M. Gramaglia, M. Fiore, A. Banchs, and X. Costa-Perez,
“AZTEC: Anticipatory capacity allocation for zero-touch network slicing,” in Proc. IEEE Conf. Comput. Commun., 2020, pp. 794–803.
[9] L. L. Schiavo et al., “CloudRIC: Open radio access network (O-RAN)
virtualization with shared heterogeneous computing,” in Proc. 30th
Annu. Int. Conf. Mobile Comput. Netw., 2024, pp. 558–572. [Online].
Available: https://doi.org/10.1145/3636534.3649381
[10] J. A. Ayala-Romero, A. Garcia-Saavedra, X. Costa-Perez, and
G. Iosifidis, “EdgeBOL: Automating energy-savings for mobile edge
AI,” in Proc. 17th Int. Conf. Emerg. Netw. Exp. Technol., 2021,
pp. 397–410. [Online]. Available: https://doi.org/10.1145/3485983.
3494849
[11] N. Bui, M. Cesana, S. A. Hosseini, Q. Liao, I. Malanchini, and
J. Widmer, “A survey of anticipatory mobile networking: Context-based
classification, prediction methodologies, and optimization techniques,”
IEEE Commun. Surveys Tuts., vol. 19, no. 3, pp. 1790–1821, 3rd Quart.,
2017.
[12] J. Wang et al., “Spatiotemporal modeling and prediction in cellular
networks: A big data enabled deep learning approach,” in Proc. IEEE
Int. Conf. Comput. Commun. (IEEE INFOCOM), Atlanta, GA, USA,
May 2017, pp. 1–9.
[13] C. Zhang, M. Fiore, and P. Patras, “Multi-service mobile traffic forecasting via convolutional long short-term memories,” in Proc. IEEE Int.
Symp. Meas. Netw. (IEEE M&N), Catania, Italy, Jun. 2019, pp. 1–6.
[14] D. Bega, M. Gramaglia, M. Fiore, A. Banchs, and X. Costa-Perez,
“DeepCog: Cognitive network management in sliced 5G networks with
deep learning,” in Proc. IEEE INFOCOM, Paris, France, Apr. 2019,
pp. 280–288.
[15] E. Coronado et al., “Zero touch management: A survey of
network automation solutions for 5G and 6G networks,” IEEE IEEE
Commun. Surveys Tuts., vol. 24, no. 4, pp. 2535–2578, 4th Quart.,
2022.
[16] Q. Y. Ding, X. F. Wang, X. Y. Zhang, and Z. Q. Sun,
“Forecasting traffic volume with space-time ARIMA model,” in
Advanced Manufacturing Technology (Advanced Materials Research),
vol. 156. Wollerau, Switzerland: Trans Tech Publications Ltd., 2011,
pp. 979–983.
[17] D. Zhou, S. Chen, and S. Dong, “Network traffic prediction based on
ARFIMA model,” 2013, arXiv:1302.6324.
[18] C. Zhang, H. Zhang, J. Qiao, D. Yuan, and M. Zhang, “Deep transfer
learning for intelligent cellular traffic prediction based on cross-domain
big data,” IEEE J. Sel. Areas Commun., vol. 37, no. 6, pp. 1389–1401,
Jun. 2019.
[19] L. Yu et al., “STEP: A spatio-temporal fine-granular user traffic
prediction system for cellular networks,” IEEE Trans. Mobile Comput.,
vol. 20, no. 12, pp. 3453–3466, Dec. 2021.
[20] N. Zhao, A. Wu, Y. Pei, Y.-C. Liang, and D. Niyato, “Spatial-temporal
aggregation graph convolution network for efficient mobile cellular
traffic prediction,” IEEE Commun. Lett., vol. 26, no. 3, pp. 587–591,
Mar. 2022.
[21] Y. Yao, B. Gu, Z. Su, and M. Guizani, “MVSTGN: A multi-view spatialtemporal graph network for cellular traffic prediction,” IEEE Trans.
Mobile Comput., vol. 22, no. 5, pp. 2837–2849, May 2023.

363

[22] S. Smyl, “A hybrid method of exponential smoothing and recurrent
neural networks for time series forecasting,” Int. J. Forecast., vol. 36,
no. 1, pp. 75–85, 2020. [Online]. Available: http://www.sciencedirect.
com/science/article/pii/S0169207019301153
[23] S. Makridakis, E. Spiliotis, and V. Assimakopoulos, “The M4
Competition: 100,000 time series and 61 forecasting methods,” Int. J.
Forecast., vol. 36, no. 1, pp. 54–74, 2020. [Online]. Available: http://
www.sciencedirect.com/science/article/pii/S0169207019301128
[24] L. Lo Schiavo, M. Fiore, M. Gramaglia, A. Banchs, and X. Costa-Perez,
“Forecasting for network management with joint statistical modelling
and machine learning,” in Proc. IEEE 23rd Int. Symp. World Wireless,
Mobile Multimedia Netw. (WoWMoM), 2022, pp. 60–69.
[25] D. Bega, M. Gramaglia, R. Perez, M. Fiore, A. Banchs, and
X. Costa-Pérez, “AI-based autonomous control, management, and
orchestration in 5G: From standards to algorithms,” IEEE Netw., vol. 34,
no. 6, pp. 14–20, Nov. 2020.
[26] “ZSM scenarios and key requirements,” Eur. Telecommun. Stand. Inst.
(ETSI), Sophia Antipolis, France, document ETSI ISG ZSM 001,
Oct. 2018.
[27] C. Zhang, P. Patras, and H. Haddadi, “Deep learning in mobile and
wireless networking: A survey,” IEEE Commun. Surveys Tuts., vol. 21,
no. 3, pp. 2224–2287, 3rd Quart., 2019.
[28] J. X. Salvat, L. Zanzi, A. Garcia-Saavedra, V. Sciancalepore, and
X. Costa-Pérez, “Overbooking network slices through yield-driven endto-end orchestration,” in Proc. 14th Int. Conf. Emerg. Netw. Exp.
Technol. (ACM CoNEXT), Heraklion, Greece, Dec. 2018, pp. 353–365.
[29] R. T. Clemen, “Combining forecasts: A review and annotated
bibliography,” Int. J. Forecast., vol. 5, no. 4, pp. 559–583,
1989. [Online]. Available: http://www.sciencedirect.com/science/article/
pii/0169207089900125
[30] O. Sagi and L. Rokach, “Ensemble learning: A survey,” WIREs Data
Min. Knowl. Disc., vol. 8, no. 4, 2018, Art. no. e1249. [Online].
Available: https://onlinelibrary.wiley.com/doi/abs/10.1002/widm.1249
[31] A. Redd, K. Khin, and A. Marini, “Fast ES-RNN: A GPU implementation of the ES-RNN algorithm,” Jul. 2019, arXiv:1907.03329.
[32] C. Marquez, M. Gramaglia, M. Fiore, A. Banchs, and Z. Smoreda,
“Identifying common periodicities in mobile service demands with
spectral analysis,” in Proc. IEEE MedComNet, Arona, Italy, Jun. 2020,
pp. 1–8.
[33] R. Hyndman, A. Koehler, J. Ord, and R. Snyder, Forecasting With
Exponential Smoothing: The State Space Approach. Cham, Switzerland:
Springer, 2008.
[34] B. Cici, E. Alimpertis, A. Ihler, and A. Markopoulou, “Cell-to-cell
activity prediction for smart cities,” in Proc. IEEE Conf. Comput.
Commun. Workshops (INFOCOM WKSHPS), 2016, pp. 903–908.
[35] H. Zhou et al., “Informer: Beyond efficient transformer for long
sequence time-series forecasting,” in Proc. AAAI Conf. Artif. Intell.,
vol. 35, May 2021, pp. 11106–11115. [Online]. Available: https://ojs.
aaai.org/index.php/AAAI/article/view/17325
[36] A. Vaswani et al., “Attention is all you need,” in Proc. 31st Int. Conf.
Neural Inf. Process. Syst., 2017, pp. 6000–6010.
[37] R. E. Turner, “An introduction to transformers,” 2024,
arXiv:2304.10557.
[38] Y. Hu, Y. Zhou, J. Song, L. Xu, and X. Zhou, “Citywide mobile
traffic forecasting using spatial-temporal downsampling transformer
neural networks,” IEEE Trans. Netw. Service Manag., vol. 20, no. 1,
pp. 152–165, Mar. 2023.
[39] Q. Liu, J. Li, and Z. Lu, “ST-Tran: Spatial-temporal transformer for
cellular traffic prediction,” IEEE Commun. Lett., vol. 25, no. 10,
pp. 3325–3329, Oct. 2021.
[40] B. Gu, J. Zhan, S. Gong, W. Liu, Z. Su, and M. Guizani, “A spatialtemporal transformer network for city-level cellular traffic analysis
and prediction,” IEEE Trans. Wireless Commun., vol. 22, no. 12,
pp. 9412–9423, Dec. 2023.
[41] H. Wu, J. Xu, J. Wang, and M. Long, “AutoFormer: Decomposition
transformers with auto-correlation for long-term series forecasting,” in
Proc. Adv. Neural Inf. Process. Syst., vol. 34, 2021, pp. 22419–22430.
[42] B. N. Oreshkin, D. Carpov, N. Chapados, and Y. Bengio, “N-BEATS:
Neural basis expansion analysis for interpretable time series forecasting,”
2020, arXiv:1905.10437.
[43] “DLinear model documentation—Darts: Time series made easy,” 2023.
[Online]. Available: https://unit8co.github.io/darts/generated_api/darts.
models.forecasting.dlinear.html
[44] Y. Ge, Y. Zhang, K. Shi, and H. Li, “A moment cross predictor for
non-stationary mobile traffic forecasting,” in Proc. IEEE/CIC Int. Conf.
Communi. China (ICCC), 2024, pp. 2059–2064.

364

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

[45] M. Di Mauro, G. Galatro, F. Postiglione, W. Song, and A. Liotta,
“Multivariate time series characterization and forecasting of VoIP traffic
in real mobile networks,” IEEE Trans. Netw. Service Manag., vol. 21,
no. 1, pp. 851–865, Feb. 2024.
[46] K. Wu, J. Lu, F. Lin, Y. Huang, C. Zhan, and L. Sun, “A realistic network
traffic forecasting method based on VMD and LSTM network,” in Proc.
IEEE Int. Symp. Circuits Syst. (ISCAS), 2023, pp. 1–5.
[47] X. He, K. Zhao, and X. Chu, “AutoML: A survey of the state-ofthe-art,” Knowl.-Based Syst., vol. 212, Jan. 2021, Art. no. 106622.
[Online]. Available: https://www.sciencedirect.com/science/article/pii/
S0950705120307516
[48] J. Kiefer, “Sequential minimax search for a maximum,” Proc. Amer.
Math. Soc., vol. 4, no. 3, pp. 502–506, 1953.
[49] V. Sciancalepore, K. Samdanis, X. Costa-Perez, D. Bega, M. Gramaglia,
and A. Banchs, “Mobile traffic forecasting for maximizing 5G network
slicing resource utilization,” in Proc. IEEE INFOCOM, May 2017,
pp. 1–9.
[50] L. Chen, T. Nguyen, D. Yang, M. Nogueira, C. Wang, and D. Zhang,
“Data-driven C-RAN optimization exploiting traffic and mobility
dynamics of mobile users,” IEEE Trans. Mobile Comput., vol. 20, no. 5,
pp. 1773–1788, May 2021.
[51] P. Brand, J. Falk, J. Ah Sue, J. Brendel, R. Hasholzner, and J. Teich,
“Adaptive predictive power management for mobile LTE devices,” IEEE
Trans. Mobile Comput., vol. 20, no. 8, pp. 2518–2535, Aug. 2021.
[52] “Architecture enhancements for 5G system (5GS) to support network
data analytics services (Rel. 17),” 3GPP, Sophia Antipolis, France, Rep.
TS 23.288, Version 17.4, May 2022.
[53] P. J. Rousseeuw and M. Hubert, “Anomaly detection by robust
statistics,” WIREs Data Min. Knowl. Disc., vol. 8, no. 2, 2018,
Art. no. e1236. [Online]. Available: https://wires.onlinelibrary.wiley.
com/doi/abs/10.1002/widm.1236
[54] Y. Gal and Z. Ghahramani, “Dropout as a Bayesian approximation:
Representing model uncertainty in deep learning,” in Proc. 33rd
Int. Conf. Mach. Learn. (ICML), New York, NY, USA, Jun. 2016,
pp. 1050–1059.
[55] “Policy and charging control framework for the 5G System (5GS);
Stage 2,” 3GPP, Sophia Antipolis, France, Rep. TS 23.503, Version 16,
Mar. 2019.
[56] J. G. Herrera and J. F. Botero, “Resource allocation in NFV: A
comprehensive survey,” IEEE Trans. Netw. Service Manag., vol. 13,
no. 3, pp. 518–532, Sep. 2016.
[57] C. Marquez, M. Gramaglia, M. Fiore, A. Banchs, C. Ziemlicki, and
Z. Smoreda, “Not all apps are created equal: Analysis of spatiotemporal
heterogeneity in nationwide mobile service usage,” in Proc. 13th
Int. Conf. Emerg. Netw. Exp. Technol., 2017, pp. 180–186. [Online].
Available: https://doi.org/10.1145/3143361.3143369
[58] O. Guhr, “Transformer time series prediction.” 2024. [Online]. Available:
https://github.com/oliverguhr/transformer-time-series-prediction
[59] C. Zhang and P. Patras, “Long-term mobile traffic forecasting using deep
spatio-temporal neural networks,” in Proc. 18th ACM Int. Symp. Mobile
Ad Hoc Netw. Comput., 2018, pp. 231–240. [Online]. Available: https://
doi.org/10.1145/3209582.3209606
[60] X. Wang et al., “Spatio-temporal analysis and prediction of cellular
traffic in metropolis,” IEEE Trans. Mobile Comput., vol. 18, no. 9,
pp. 2190–2202, Sep. 2019.

Leonardo Lo Schiavo received the Ph.D. degree in
telematic engineering from Universidad Carlos III de
Madrid, in 2025, where he is currently a Postdoctoral
Researcher. His research interests include virtualized
radio access networks, AI-driven network automation, and traffic forecasting.

Genoveva García is a graduate in telecommunication technologies engineering from Universidad
Carlos III de Madrid, where she is currently pursuing
the master’s degree in artificial intelligence.

Marco Gramaglia received the Ph.D. degree in
telematics engineering from Universidad Carlos III
de Madrid. He has contributed extensively to several
research projects at both the European and national
levels. He co-authored more than 100 articles and,
according to Google Scholar, his H-index is 35.
His research interests include network automation,
privacy, and AI-driven resource management.

Marco Fiore (Senior Member, IEEE) received the
M.Sc. degree from the University of Illinois at
Chicago and Politecnico of Torino, the Ph.D. degree
from Politecnico di Torino, and the Habilitation à
Diriger des Recherches degree from Université de
Lyon. He is a Research Professor with IMDEA
Networks Institute, where he leads the Networks
Data Science Group, and a Co-Founder and a CTO
with Net AI. He has held tenured positions with
Institut National des Sciences Appliquées de Lyon
and National Research Council of Italy, and has
been a Visiting Researcher with Rice University, Universitat Politècnica de
Catalunya, and University College London. His research is at the interface
of mobile networks and data science, and has received funding from the
European Commission and national agencies in Spain, France, and Italy, as
well as a number of recognitions that include two best paper awards at IEEE
INFOCOM. He is a Former Marie Curie Fellow and a Royal Society Visiting
Research Fellow and a Senior Member of ACM.
Albert Banchs (Senior Member, IEEE) received
the M.Sc. and Ph.D. degrees from the Polytechnic
University of Catalonia (UPC-BarcelonaTech) in
1997 and 2002, respectively. He is currently a Full
Professor with the University Carlos III of Madrid
(UC3M), and also the Director with the IMDEA
Networks Institute. Before joining UC3M, he was
with ICSI Berkeley in 1997, Telefonica I+D in
1998, and NEC Europe Ltd., from 1998 to 2003.
He was an Academic Guest with ETHZ in 2012,
a Visiting Professor with EPFL in 2015, 2013, and
2018, respectively, and a Fulbright Scholar with The University of Texas
at Austin in 2019. He is the author over 150 publications in international
conferences and journals and is the co-inventor of several patents.
Xavier Costa-Perez received the M.Sc. and Ph.D.
degrees in telecommunications from the Polytechnic
University of Catalonia, Barcelona. He is a ICREA
Research Professor, a Scientific Director with the
i2cat Research Center and a Head of 6G R&D
at NEC Laboratories Europe. His team generates
research results that are regularly published at top
scientific venues, produces innovations that have
received several awards for successful technology transfers, and participates in major European
Commission Research and Development collaborative projects. He has held multiple leadership positions both in industry
and research organizations, such as a Deputy General Manager, a Chief
Researcher, a Technology Board member, and a Scientific Advisory Board
Member. As a standards delegate, he contributed to multiple standardization bodies, such as IEEE 802.11, 802.16, WiFi Alliance, and 3GPP, and
was recognized in several standards as a Top Contributor. He was the
recipient of a national award for the Ph.D. thesis. He has served on the
Organizing Committees of several conferences, including ACM MOBICOM,
IEEE INFOCOM, WCNC, and Greencom, published papers of high impact,
and holds about 100 granted patents. He has served as an Editor for
IEEE T RANSACTIONS ON M OBILE C OMPUTING, IEEE T RANSACTIONS ON
C OMMUNICATIONS, and Computer Communications Journals (Elsevier).
PAPER_TEXT
