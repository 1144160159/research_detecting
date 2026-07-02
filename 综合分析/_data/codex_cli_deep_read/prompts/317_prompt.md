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
# [317] TS-DP: An Efficient Data Processing Algorithm for Distribution Digital Twin Grid for Industry 5.0
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
编号：317
题名：TS-DP: An Efficient Data Processing Algorithm for Distribution Digital Twin Grid for Industry 5.0
年份：2023
DOI：10.1109/tce.2023.3332099
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_tce.2023.3332099.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：无
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\317.txt
- 原始字符数：56450
- 本次发送字符数：56450
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

1983

TS-DP: An Efficient Data Processing Algorithm for
Distribution Digital Twin Grid for Industry 5.0
Lijun Xiao , Dezhi Han , Member, IEEE, Ce Yang , Jiahong Cai , Wei Liang , Senior Member, IEEE,
and Kuan-Ching Li , Senior Member, IEEE

Abstract—As known, the smart Grid is an essential scenario
for Industry 5.0. With its rapid development, the huge number
of sensors and smart devices widely used in the industrial field
generate significant amounts of data that sharply increase. Facing
the power grid environment with a high amount of data, it is
easy to cause abnormal conditions in the power grid system
and even cause the system to collapse abruptly. To tackle this
problem, we simulate a layered digital twin power grid model,
using the comparative learning method to process the time series
in the power grid and select the positive and negative time
series samples using a new slider. In the extended Convolution
Neural Network (CNN), we use the Atrous Convolution model,
limiting the receptive field and concentrating more data close
to the dimension of the model. The time series and process
classification tasks are predicted on Electricity Transformer
Temperature (ETT), electricity, and University of California,
Riverside (UCR) data sets, and experimental results show that
the proposed method reduces the error rate of 4.38% and 5.21%
in the prediction task and improves the accuracy of 8.39% and
12.73% in the classification task, indications to control the power
grid model more accurately, predicting the power grid operation
in the future, and take corresponding measures in time.
Index Terms—Contrastive learning, digital twin (DT), industry
5.0, smart grid, time series.

I. I NTRODUCTION
ITH the growing demand for renewable energy,
the smart grid is a crucial application of Industry
5.0 [1], [2], effectively integrating power system resources
and communication infrastructure resources to meet the power
consumption needs of users during different periods, as shown
in Figure 1 the power Internet of Things (IoT) architecture
diagram, with the efficient operation of energy and market
and the efficient use of system resources. The power IoT
architecture mainly includes the perception layer, network

W

Manuscript received 22 September 2023; accepted 15 October 2023.
Date of publication 16 November 2023; date of current version
26 April 2024. This work was supported by the Top-Notch Innovative
Talent Training Program for Graduate Students of Shanghai Maritime
University under Grant 2023YBR019. (Lijun Xiao and Dezhi Han are co-first
authors.) (Corresponding authors: Wei Liang; Kuan-Ching Li.)
Lijun Xiao and Dezhi Han are with the College of Information Engineering,
Shanghai Maritime University, Shanghai 200135, China.
Ce Yang, Jiahong Cai, and Wei Liang are with the School of Computer
Science and Engineering and the Hunan Key Laboratory for Service
Computing and Novel Software Technology, Hunan University of Science and
Technology, Xiangtan 411201, China. (e-mail: wliang@hnust.edu.cn).
Kuan-Ching Li is with the Department of Computer Science and
Information Engineering, Providence University, Taichung 43301, Taiwan
(e-mail: kuancli@pu.edu.tw).
Digital Object Identifier 10.1109/TCE.2023.3332099

Fig. 1.

Grid architecture diagram.

layer, platform layer, and application layer. With the rapid
development of power IoT technology, the number of sensors
and nodes in it has increased rapidly, whilst the amount of
data has risen sharply, which is prone to problems such as
data leakage and excessive data load. In recent years, there
have been many cases at home and abroad. For example,
in March 2019, hackers exploited a known vulnerability in
Cisco’s firewall to launch a Denial of Service (DoS) attack
against a renewable energy utility in Utah, USA, forcing the
device to reboot multiple times, causing the group’s control
center and The communication between the field devices at its
various sites is interrupted [3]. In June 2020, hackers extorted
14 million from Brazil-based electricity company Light SA
to redeem the use of servers and the hacker’s ransomware
Sodinokibi ransomware. At the same time, the researchers
(also found that the software can enhance privileges by taking
advantage of the 32-bit and 64-bit vulnerabilities of cve2018-8453 vulnerability in Windows win32k components.
The existence of this vulnerability will pose a huge security
risk to the power IoT [4]. The existing physical power grid
model cannot predict the situation in the future and take
corresponding measures.
Therefore, it is urgent to adopt a model that combines
physical and virtual power grids, and the digital twin distribution network model is suitable for this scenario [5]. As a
multi-dimensional and multi-attribute simulation technology,
digital twin technology uses sensor data, network communication architecture, entity attributes, and other characteristics
to model the actions and states of physical entities and
integrates physical entity models and twins through interactive

c 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1558-4127 
See https://www.ieee.org/publications/rights/index.html for more information.

1984

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

channels. The model is mapped and connected in real-time,
and the physical system interacts with the virtual space in realtime to form a closed-loop [6]. The digital twin power grid
model can predict the system state in the future, simulate the
countermeasures to be taken on the virtual power grid, and
feedback to the physical power grid according to the execution
results of the virtual power grid so that the hidden dangers
such as data leakage and overloading of data in the system are
discovered as soon as possible, the resulting property losses
and personnel losses are minimized, and the safety, reliability,
power quality, and transmission efficiency of the power grid
system are effectively guaranteed [7].
There are many sensors in the power IoT, and the data of
each interrelated sensor affect each other. When a sensor is
attacked or the sensor crashes, the data of the sensor will not be
available until the sensor returns to normal. How to accurately
predict the data of single or multiple sensors based on the
connections and characteristics of each interrelated sensor has
become a challenge in the data management of the power IoT.
We simulate a digital twin power grid model to solve
the abovementioned problems, including hierarchical physical
distribution network entities, a data interaction layer, and a
digital twin power distribution network. In the model, we
use the contrastive learning method. We propose a new data
perturbation method to select positive and negative samples.
The obtained hidden layer vector is sent to the decoder
for time series reconstruction through the input projection
layer and timestamp masking. We performed UniVariate and
MultiVariate time series prediction and classification tasks on
multiple datasets, and this paper has high time series prediction
accuracy and classification accuracy.
The remainder of this work is organized as follows:
Section II introduces the research status of the digital twin
power grid and sensor data prediction technology, Section III
introduces the digital twin power grid architecture adopted,
and Section IV shows the sensor data prediction algorithm. Experimental results and data analysis are depicted
in Section V, and finally, the full text is summarized in
Section VI, including directions for future work.

grid development, realizing the “digital twin” of “physical
power grid” and “online power grid”, supporting the highquality development of power grid business. Pan et al. [10]
combined digital twin technology with power systems and
applied it to other services such as grid optimization design,
grid fault simulation and simulation, virtual power plants, and
smart device monitoring. Danilczyk et al. [11] proposed a
framework for adapting digital twin technology to microgrid
security applications, in which digital twin technology is able
to update and improve simulation using real-time bidirectional
coupling between simulation and physical systems, resulting
in more Well applied to physical systems. Ma et al. [12]
realized the interaction between the physical engineering site
and the virtual engineering model based on the digital twin
technology, improving planning accuracy and coordination. In
system infrastructure and IoT applications, Borth et al. [13]
discusses the challenges of many tasks related to digital twins
and the strategies and architectures for these tasks. From
the perspectives of standardized description, knowledge reuse,
and data integration, Jiang et al. [5] proposed a digital twin
(DTB)-oriented digital portal (DP) model, which supports
the construction of DTBs from equipment units to complex
systems. Ahmadi et al. [14] proposed a scheme to use digital
twin technology at the equipment and system level of electrified railway power systems (ERPS). By analyzing the security
risks and characteristics of edge computing, Sun et al. [15]
constructed a power grid digital twin security control model
including an application layer, function layer, model layer,
data layer, and physical layer based on the security protection
architecture of edge computing, so as to Make sure all aspects
of the grid are under control. Aiming at problems such as
power outages, damage to sensitive equipment, and power
grids that cannot maintain normal operation, Sleiti et al. [16]
proposed a method using deep learning algorithms and a vector
autoregressive model to predict the dynamic system model of
digital twin technology, which effectively solves the problem.
Anomaly detection for power plant data.

II. R ELATED W ORK

The wireless sensor layout is a key link in the construction
of the energy Internet and an important support for the
power grid’s digital, networked, and intelligent development.
During the power grid’s operation, the power data analysis
and prediction improve the smart grid’s effective utilization. Kumar Gilbert et al. [17] proposed a new method for
security data prediction in wireless sensor networks, which
uses a Toeplitz matrix-based time series trust model (TSTM)
and a trust-based autoregressive (TAR) process to Better
performance in data prediction and Compressed Sensing (CS)
based aggregation and reconstruction. Reference [18] proposed
a deep long short-term memory (DLSTM) network-based
RUL prediction method using multiple sensor time-series
signals. The model fuses multi-sensor monitoring signals for
accurate RUL prediction, which can discover hidden longterm dependencies between sensor time-series signals through
a deep learning structure, improving data prediction accuracy. Reference [19] developed a single-stage detector and

As an essential technology to promote the social economy, the power industry has gradually become the focus of
academia on the information processing method in the smart
grid. During the operation of the power grid, data analysis and
processing can effectively improve the data support for power
dispatching, but the existing methods cannot predict the data
of power grid sensors well in the future. For such, we propose
in this work an efficient grid sensor data prediction method.
A. Digital Twin Power Grid
The Digital Twin (DT) Power Grid is the mirror image of
the physical power grid system based on sensors in the digital
space. Jia et al. [8] introduced the concept of digital twins
and discussed the construction and application of digital twin
technology in the power grid. Yz and Wang [9] introduced the
research and application of digital twin technology in power

B. Sensor Data Prediction Method

XIAO et al.: TS-DP: AN EFFICIENT DATA PROCESSING ALGORITHM FOR DISTRIBUTION DT GRID FOR INDUSTRY 5.0

predictor that utilizes 3D point clouds produced by LiDAR
sensors and a dynamic map of the environment, achieving
better accuracy and saving computation. To extract generalized
features and latent relationships in power load-related edgesensing data, Liu et al. [20] proposed a power-load forecasting
scheme based on edge-sensing data-imaging conversion (DIC)
to improve the smart city and social forecasting precision.
Darvishi et al. [21] proposed a real-time generalized machine
learning architecture for sensor-based validation based on
a series of neural network estimators and classifiers. Ren
and Cao [22] proposed a method to process Computational
Fluid Dynamics data using the LLVM method to generate
further a low-dimensional database for ANN predictions
using monitored concentrations from different sensor layouts
(i.e., location and number) for a series of ANN predicts
the input and improves the accuracy of data prediction.
Aiming at the problems of multi-party sensor data sharing and
privacy protection, and realizing cross-organizational traffic
data fusion and prediction, Wang et al. [23] proposed an
accurate traffic prediction method based on LSH (localitysensitive hashing). Feasibility of prediction accuracy and
efficiency while maintaining the privacy of sensor data.
Balogun et al. [24] preprocessed some data from IoT sensors,
such as weather and traffic data corresponding to time, and
used these data to develop a machine learning prediction model
for NO2 pollution concentration. Bodenstedt and Wagner [25]
proposed a context-aware method based on a convolutional
neural network that can analyze the intervention workflow
online and automatically predict the remaining duration,
improving the prediction accuracy of online surgery duration.
Yang et al. [26] proposed a digital twin-driven composite fault
diagnosis method by combining virtual and real data, which is
extremely effective for composite faults in subsea production
control systems.
C. Sensor Data Synchronization Method
Sensor networks perform complex monitoring and sensing
tasks collaboratively through various integrated micro-sensors.
However, due to the unpredictability and imperfect measurability of message delays in the IoT environment, the
data synchronization problem of sensor nodes has caused
researchers and scholars’ attention. Sguazza et al. [27]
proposed an offline data-driven synchronization solution,
which can process data of different nature and sample at
different frequencies, which not only solves the problem of
data synchronization but also solves the problem of clock drift
caused by Data time alignment problem. Since the clock will
be skewed, Skiadopoulos et al. [28] propose a lightweight
synchronization algorithm for wireless sensors, which solves
the problem of time skew and corresponding variance in harsh
environments such as IoT systems. Due to the local clock
synchronization problem of wireless sensor network nodes,
Chalapathi et al. [29] proposed a time synchronization protocol
called Efficient Simple Time Synchronization Algorithm (ESATS) for cluster-based wireless sensor networks. Volume and
energy consumption are significantly reduced. Xu et al. [30]
designed a data set synchronization protocol for wireless

Fig. 2.

1985

Digital twin grid model.

sensor networks, which uses a sleep mechanism to save
energy and optimize energy consumption. Since data and
energy consumption can be minimized in wireless sensor
networks, Palanisamy et al. [31] proposed a Multi-Sensor Data
Synchronization Scheduling (MSDSS) framework for efficient
scheduling at the receivers of heterogeneous sensor networks
data aggregation. Due to the lack of spatial and temporal
synchronization of roadside sensors due to different in-vehicle
devices, Du et al. [32] proposed a novel spatiotemporal
synchronization method for asynchronous roadside mmWave
radar cameras for sensor fusion, which utilizes scene. The
feature extraction of lane line corners to pre-calibrate the
camera solves the problem of spatiotemporal synchronization of roadside sensors. Aiming at the dataset analysis
problem of multiple sensor systems in synchronizing the
Internet of Vehicles, Ishiwatari et al. [33] proposed a method
for synchronizing video data with acceleration data from onboard sensors of a moving vehicle, which uses image features
to detect synchronization point and then match it with the
corresponding point in the acceleration data. Since the data
of IoT devices are all sent to cloud storage, Wang et al. [34]
proposed a new architecture for data synchronization based
on fog computing, aiming at the privacy and security issues
that may arise in this process. Offloading to the fog server can
ensure data privacy and security.
III. G RID D IGITAL T WIN
This section constructs the digital twin distribution network
model, as shown in Figure 2. Firstly, a hierarchical distribution network entity is established, including distribution
network distributed generation, static var compensator, energy
storage model, and distribution network hierarchical model,
which provides real-time data for the data interaction layer
and completes the dynamic adjustment of the relationship
between physical entities. Secondly, the data interaction layer
is constructed, which is mainly divided into a data transmission
module and a data perception module. According to the
data interaction layer mapping, the distribution network entity
model is transmitted to the digital twin, the digital twin model
is constructed, the data of the physical distribution network
is fully explored and extracted, the data characteristics of
the power system are extracted, and the results processed in
the virtual distribution network are fed back to the physical

1986

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

distribution network through the data interaction layer. The
physical distribution network executes better strategies according to the results.
A. Hierarchical Distribution Grid Entities
The power transmission network or power plant outputs
power to the distribution network, and the distribution network
distributes electricity energy to various users utilizing step-bystep distribution. The distribution network is mainly composed
of equipment such as cables, towers, overhead lines, power
sources [35], reactive power compensators [36], and energy
storage models [37], combined with a hierarchical topology
model [38]. Model key equipment in a hierarchical distribution network for digital twinning of the physical entities of
the distribution network. Provide real-time real data for the
data interaction layer, record the event occurrence process,
complete the dynamic adjustment of the relationship between
physical entities, and execute the latest feedback instructions
in the digital twin through the data interaction layer.
1) Distributed Power Supply in the Distribution Network:
In this module, we use the micro-turbine as a representative to analyze the characteristics of distributed power in
the distribution network. The Micro Gas Turbine (MGT) is
connected to the distribution network, and the active and
reactive power output can be adjusted independently using
the inverter multiplexing method. Among them, the inverter
capacity still limits the active and reactive power output of
MTG. Pmax (MGT) and Pmin (MGT) are the upper and lower
limits of the MGT active power output, S(MGT) is the inverter
capacity, Pmax (MGT) and Pmin (MGT) are the upper and lower
limits of the MGT ramp rate, and Pj,t (MGT) is the active
power output of the jth MGT in the t period, and Qj,t (MGT)
is the reactive power of the jth MGT in the t period. The MGT
model is expressed as follows:
Pmin (MGT) ≤ Pj,t (MGT) ≤ Pmax (MGT) (1)
pmin (MGT) ≤ Pj,t (MGT) − Pj,t−1 (MGT) ≤ pmax (MGT) (2)
P2j,t (MGT) + Q2j,t (MGT) ≤ S2 (MGT)

(3)

2) Static Var Compensator (SVC): At present, the SVC
method with fast response speed and high stability is mainly
the TSC (Thyristor Switched Capacitor) + TCR (Thyristor
Controlled Reactor) model, through which the switching of
groups can be realized, and the TCR method can be used
for branch coordination. And can carry out continuous adjust◦
◦
ments of reactive power. Among them, α(90 ≤ a ≤ 180 )
is the trigger delay angle of the thyristor, U is the voltage of
the connection point of the SVC, BC is the fundamental susceptance of the TSC, and BL (α) is the equivalent fundamental
susceptance of the TCR.
BC = ωC
2(π − a) + sin 2α
BL (α) =
π ωL
π ω2 LC − 2(π − a) − sin 2α
B(SVC) =
π ωL
Q(SVC) = [BC − BL (α)]U 2 = B2SVC U

(4)
(5)
(6)
(7)

SVC uses thyristors to control capacitors, reactance elements,
and other equipments, mainly by adjusting the TSG situation,
changing the reactive power data QSVC of the SVC system,
and finally controlling the bus voltage within a reasonable
range, and continuously adjusting.
3) Energy Storage Model: The energy storage model set
in this paper fully considers the individual capacity, state of
charge (SOC), power and other factors, the energy storage
individual q, the rated capacity Contentq of the individual q,
and Content is the total amount of energy storage individuals
q

in the system. The adaptive filling function of the input
(output) power of the energy storage individual q is as follows:
 
p sq =

Contentq Pq,rat Aq edq f (sq )

 
Content × Pq,rat + Aq0 edi f (sq )

(8)

p

Among them, Pq,rat is the rated power of the individual energy
storage, Aq is the adaptive factor of the individual energy
storage, and dq is the automatic distribution coefficient of
the individual. According to the state of charge and state of
discharge, the adaptive charge-discharge function of the energy
storage individual q is selected.
 

 
dq (sshc + smin )/2 − Pq
p sq ch arg e = Contentq Pq Aq exp
smin − smin
 


dq −(sshc + smin )/2 − Pq
× Pq,rat + Aq0
(9)
Content
smin − smin
p
 

dq sq − (smid + sshd )/2
p(sq )disch arg e = Contentq Pq,rat Aq exp
smin − smin

 
 
dq sq − (smid + sshd )/2
× Pq,rat + Aq0 e
(10)
Content
smax − smid
p

Among them, p(sq )ch arg e and p(sq )disch arg e are the chargedischarge functions in the charge and discharge states,
respectively.
4) Layered Model of Distribution Network: For nodes in
the distribution network, we use the adjacency matrix to
represent. The layered model of the distribution network takes
a node as the core node, is layered according to the path
length between other nodes and this node, and defines the
layered identification matrix of the distribution network. The
identification matrix is as follows:
⎧ l
l
⎨ gi,j , gi,j = 1i = j, l = 1, . . . , N − 1
(11)
ideni,j = 0gli,j = 1i = j, l = 1, . . . , N − 1
⎩
0, i = j,l = 1, . . . , N − 1
where gli,j represents the path length l from node i to node j
⎧


⎪
⎪ Layer1 , di,j = d1,1 , d1,2 , . . . , d1,N 
⎪
⎨ Layer2 , di,j I = d2,1 , d2,2 , . . . , d2,N
(12)
..
⎪
.
⎪
⎪


⎩
LayerN , di,j IN−1 = dN,1 , dN,2 , . . . , dN,N
B. Data Interaction Layer
The data interaction layer is mainly divided into a data
transmission module [39] and a data perception module. As

XIAO et al.: TS-DP: AN EFFICIENT DATA PROCESSING ALGORITHM FOR DISTRIBUTION DT GRID FOR INDUSTRY 5.0

the data transmission channel of the physical entities and
twins of the distribution network, the data transmission module
can effectively acquire, transmit, and coordinate information.
The data perception module can sense the data of sensors,
collectors, meters, and other equipment according to different
power grid scenarios and needs and share the resources
of the whole system through the collected data. The main
data sensing operations include: installing signal collectors
on transmission equipment, installing protection measurement
and control devices on power equipment at all levels, and
installing sensors on terminal ring network cabinet equipment.
The physical distribution network entity has incoming data
packets in the finite domain , and the data transmission
model fuses each broadcast data packet into a linear representation of the original data packet. M = {m1 , m2 , . . . , mn }
represents the set of n original data packets, and Di represents
the linear combination of all data packets:
n

Di =

mi ρj,i

(13)

1987

represents the average value at a time, and σwin represents the
standard deviation at time TD. At the time i, Vari > Vart +
θ σwin indicates that the data fluctuation is greater than the
set threshold, and θ indicates the threshold parameter, which
needs to be corrected for the data in the TD time.
C. Digital Twin Mapping Networks
According to the data interaction layer mapping, the physical model of the distribution network is transferred to the
digital twin, the data of the physical distribution network
is fully explored and extracted, and then the data of the
physical distribution network is detected, identified, classified,
repaired, etc. The operation, processing the related business
of the distribution network in the virtual distribution network,
extracting the data characteristics of the power system, and
feeding back the results processed in the virtual distribution
network to the physical distribution network through the
data interaction layer, and the physical distribution network
according to the results. Implement better strategies.

i=1

Among them, ρj,i represents the random network coding coefficient of the data packet sent by node J in .
Extracting the encoding vector {K1 , K2 , . . . , Kn } from the
encoded message Di , a node with M encoded messages
e1 , e2 , . . . , eM solves the system of linear equations, which
can be expressed as:
MtM×1 = QM×n χn×1

(14)

Among them, all embedded coding vectors form a matrix
QM×n . If the rank of the Q matrix is not less than n, it
means that the digital twin model successfully receives the data
transmitted by the physical entity of the distribution network.
According to the real environment and usage requirements
of the distribution network, we deploy sensing nodes in
important parts of the distribution network, collect sensor
data that may affect the normal operation of the distribution network, and build a relationship database between the
operating environment of the distribution network and the
status of key sensors. We use the data perception method
based on Moving Variance to compare the data of the same
node in different time windows through variance. When the
comparison result exceeds the set threshold, it means that the
data fluctuates greatly in the two-time windows. The dataaware approach can be expressed as:
TD = te − ts
k+win
Si
St = i=k
win 
k+win−1
Vart =
Vart =
σwin =

Si − Si
win − 1
 te
i=ts Vari

(15)
(16)


i=k

TD + 1
2
 te 
i=ts Vari − Vari

(17)
(18)

(19)
win − 1
Among them, win represents the size of the time window
used, St is the average value of the data in the window, Vart

IV. TS-DP: G ENERAL S ENSOR DATA
P ROCESSING A LGORITHMS
This section describes the sensor data processing algorithm
in the digital twin grid model for predicting future grid
sensor data. The most common method in machine learning
is supervised learning. Using the supervised learning method,
we can get a set of labeled data (X, Y), that is, feature-label
pairs, and the main task is to learn the relationship between
features and label pairs. Model training using the supervised
learning method requires running a large amount of data, and
the process of labeling data for millions of data will consume
a lot of computing power and time. The model trained by
the supervised learning method is very good at solving the
current task, but because the network of supervised learning
only focuses on the good representation of X and the (X, Y)
relationship, it cannot represent a general model for learning X,
and cannot well generalize the model to related fields.
Self-supervised learning, a subcategory of supervised learning, is also suitable for learning (X, Y) label (X, Y)pairs, but
without the need for manual labeling of the dataset. The basic
idea of self-supervised learning is to hide a certain part of the
input data, and then use the hidden part to observe its value
of the hidden part. Using self-supervised learning can lead to
a more general range of models that can be fine-tuned for
downstream tasks. Self-supervised learning usually requires us
to consider the loss function of the supervised process. We do
not pay much attention to the final performance of the task.
More attention is focused on the intermediate data representations in the learning process. For these representations, we
hope to cover more abundant semantics and can improve the
performance of downstream tasks.
This paper improves the model depicted in [40], performs
perturbation processing on the collected data, and selects
positive and negative sample data. Then the original data is
sent to the encoder, the input time series is mapped to a highdimensional latent vector through the input projection layer,
and a random timestamp is selected to mask the latent vector

1988

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Algorithm 1 Data Perturbation Method With Half of the
Positive and Negative Samples
1: sections = input_data //Crop training data according to
preset maximum processing length
2: for i <= section do
3:
if input_date[x,y] == NaN then //If there are empty
values, fill with the mean of the current column
4:
input_date[x, y] = mean(input_date[y])
5:
train_data=joint_as_dimation_0input_date[section]
//The input data is cut into equal parts of sections, and
the data is spliced according to the 0-dimension to
obtain the training data
6:
crop_random=random(low=0,hight=size(train_data))
//pick any point
7:
crop_left = random(0,random)
8:
crop_right = crop_left + crop_random //middle overlapping box
9:
crop_eleft = max(crop_left - crop_l-2×crop_left,0)
10:
crop_eright=min(2×crop_right+crop_l,size(
train_data))
11:
out1 = train_data[crop_eleft,crop_right] //get two
slices
12:
out2 = train_data[crop_left,crop_eright]

to generate a context view. We use the representation learning
method to use the learned hidden layer vector, use the decoder
to map the hidden layer vector back to the input vector,
reconstruct, and achieve the purpose of data dimensionality
reduction and include more semantic features.
In the data perturbation module, we use the method of
two sliders to select positive and negative samples. The two
sliders represent two time periods [x1 , x2 ] and [y1 , y2 ], 0 <
x1 ≤ x2 ≤ y1 ≤ y2 ≤ Time, and Time represents the
length of the time series. We use a new data perturbation
method, that is, [x1 , x2 ], the length of [x1 , y1 ] and [y1 , y2 ]
are consistent, we take [x1 , y1 ] as a positive sample, [x1 , x2 ]
and [y1 , y2 ] as a negative sample, and perform two positive
and negative samples in the two time periods of [y1 , y2 ] and
[y1 , y2 ] study comparison. The data perturbation method is
shown in Algorithm 1. First, the training data is cropped by
the preset maximum processing length. If there is a null value
in the input data, the mean value of the column is used to fill
in, and then the cropped data is processed, etc. The training
data is obtained by splicing according to dimension 0, a period
of time sequence is randomly selected from the training data,
and the data perturbation method is executed.
In the encoder, we use atrous convolution as an extended
CNN, adopting an atrous convolution that is more inclined to
the same dimension data, as shown in Figure 3. In the first five
layers, the dilation of the Atrous Convolution is continuously
increased to enlarge the receptive field. The last five layers
of convolution stop expanding and lock the dilation number
to 2; that is, in the later stage of feature extraction, we pay
more attention to the same dimension as our data reduce
the interference of other dimension data on model training.
Since we limit the receptive field of Atrous convolution, we
have higher accuracy in univariate prediction, and when the

Fig. 3.

Atrous convolution.

Algorithm 2 Prefer Atrous Convolution for Data of the Same
Dimension
1: input_data[]= train_data[]
2: feature_extractor[]=DilatedConvEncoder(
input_data_dimation, out_channels,kernel_size,dilation)
3: if input_Data_type = multivar
4:
for i <= DilatedConvd eep do
5:
if i > 5
6:
dilation = 2
7:
else
8:
2i //Dilation=2 for more than 5 layers of Dilated
convolution
9:
10:
11:
12:

for i <= DilatedConvd eep do
dilation = 2i
return feature_extractor[] //return feature matrix

data dimension is smaller and can achieve better classification
accuracy in most datasets with smaller data dimensions, such
as Algorithm 2 shown.
In this section, a general sensor data processing algorithm
is constructed. We use the contrastive learning method to
construct positive and negative samples through a special data
perturbation method. The perturbed data is sent to the encoder,
and the input projection layer is mapped to high-dimensional
data. Then pass in the Atrous Convolution layer. Since the
change of the Atrous Convolution is limited, this layer pays
more attention to the data of the same dimension, to reduce
the interference caused by the data of other dimensions to the
model training.
V. E XPERIMENT AND D ISCUSSION
All experimentations in this work are performed on a
server equipped with one Intel CORE i9-11990K CPU, 64G
memory, and one NVIDIA T4 GPU accelerator card, installed
with CUDA version 11.3, Python 3.8, and PyTorch 1.8.2,
Max threads and batch size configuration set to 8 on each
dataset.

XIAO et al.: TS-DP: AN EFFICIENT DATA PROCESSING ALGORITHM FOR DISTRIBUTION DT GRID FOR INDUSTRY 5.0

1989

TABLE I
R ESULTS OF U NIVARIATE T IME S ERIES F ORECASTING BY D IFFERENT M ETHODS

Fig. 4.
Results of Univariate predictions performed by multiple
methods on different datasets. Caption: Figure 4(a) shows the MSE results
of Univariate prediction in ETTm1, Figure 4(b) shows the MAE results
of Univariate prediction in ETTm1, Figure 4(c) shows the MSE results of
Univariate prediction in Electric, Figure 4(d) Represents the MAE result of
Univariate prediction in Electric.

The datasets used include:
• ETT data set [41]: divided into multiple sub-datasets
ETTh1, ETTh2, and ETTm1, mainly related to parameters such as oil temperature and six power load
characteristics, which can be predicted by the relevant
data.
• Electricity dataset [42]: is used for research in areas such
as electric load forecasting and energy market analysis.

The dataset records electric load data for the power
system over a period of time, usually sampled at hourly
or 15-minute intervals.
• UCR dataset [43]: is the “Imagnet” of the time series
field, containing time series data from many different
domains and applications. Each dataset contains a series
of time series samples with corresponding labels.
We perform time series prediction tasks in ETT and
Electricity datasets and time series classification tasks in UCR
datasets.
We use the following methods for comparison in data
prediction experiments:
• TS2Vec [40]: is a universal framework for learning
representations of time series in an arbitrary semantic
level.
• Informer [41]: Beyond Efficient Transformer for Long
Sequence Time-Series Forecasting.
• LogTrans [44]: improved the prediction accuracy of time
series with limited memory budget.
• N-BEATS [45]: Neural basis expansion analysis for
interpretable time series forecasting.
• TCN [46]: is a sequence modeling benchmarks and
Temporal Convolutional Networks.
• LSTnet [47]: is a Long- and Short-term Time-series
network.
• StemGNN [48]: is a Spectral temporal graph neural
network for multivariate time-series forecasting.
The following methods are used for comparison in
data classification experiments: TS2Vec [40], T-Loss [49],
TNC [50], TSTCC [51], DTW [52], TST [53].
The accuracy of the model is usually measured using mean
square error (L2 loss) MSE and mean absolute value error

1990

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

TABLE II
R ESULTS OF M ULTIVARIATE T IME S ERIES F ORECASTING BY D IFFERENT M ETHODS

(also known as an L1 loss) MAE. MSE is less sensitive to
outliers than MAE and can be used to evaluate the global
accuracy of the model, while MAE can better reflect individual
outliers. The formula is as follows:
MSE =
MAE =

1
m
1
m

i=1
m
i=1


2
yi − ŷi

(20)



 yi − ŷi 

(21)

m

We employ atrous convolutions that prefer samedimensional data, as shown in Algorithm 2. In the first five
layers, the dilation of the Atrous Convolution is continuously
increased to increase the receptive field. The last five layers of
convolution stop expanding and lock the dilation number to 2.
That is, in the later stage of feature extraction, we pay more
attention to the same dimension as ourselves. Data to reduce
the interference of other dimension data on model training.
As shown in Table I and Table II, we conducted time series
prediction experiments on the ETT and the Electricity datasets,
then compared them with the current state-of-the-art methods.
Since we limit the receptive field of the atrous convolution,
the Higher accuracy when making univariate forecasts and
when data dimensions are smaller.
Figure 4 and Figure 5 show the Univariate and MultiVariate
prediction results of Our Model and TS2Vec, LogTrans, NBEATS, and TCN methods on the ETTh1, ETTm1, and
Electricity datasets. With the increase of H, our method still
maintains a low value in terms of MAE and MSE, indicating
that the method in this paper has higher accuracy for prediction
on ETTh1, ETTm1, and Electricity datasets.
Due to the reduced receptive field, our method can achieve
better classification accuracy in most datasets with smaller
data dimensions. Figure 6 shows the accurate scores of Ours,
TS2Vec, T-Loss, TNC, TS-TCC, TST, and DTW methods for

Fig. 5. Results of Multivariate predictions by multiple methods on different
datasets. Figure 5(a) shows the MSE results of Multivariate prediction
at ETTh1, Figure 5(b) shows the MAE results of Multivariate prediction
at ETTh1, Figure 5(c) shows the MSE results of Multivariate prediction at
ETTm1, and Figure 5(d) represents the MAE result of Multivariate prediction
at ETTm1.

data classification on 10 UCR. Compared with other methods,
the method in this paper has the highest score in most UCR
datasets except BeetleFly, PLAID, and Car, and the ranking
in BeetleFly, PLAID, and Car datasets is not the highest, but
it also achieves a relatively high score.
As can be seen from Figure 7, our loss curve has significantly smaller fluctuations than ts2vec, and can also converge
quickly. The fluctuation range of the Loss curve is often related
to three factors: batch size, learning rate, and whether the data
passed to the model for learning is what the model needs. In
order to exclude the influence of other factors, we reproduced
ts2vec on Nvidia T4 GPU with a consistent batch size set to

XIAO et al.: TS-DP: AN EFFICIENT DATA PROCESSING ALGORITHM FOR DISTRIBUTION DT GRID FOR INDUSTRY 5.0

1991

Fig. 6. Accuracy comparison of different methods for data classification on 10 UCR datasets. Caption: dataset1 represents BeetleFly, dataset2 represents
PickupGestureWiimoteZ, dataset3 represents Rock, dataset4 represents PLAID, dataset5 represents Car, dataset6 represents Herring, dataset7 represents Beef,
dataset8 represents PigAirwayPressure, dataset9 represents PigCVP, and dataset10 represents RefrigerationDevices.

Fig. 7. In this work, the proposed method is compared with the TS2Vec method for the prediction and training of Univariate and Multivariate loss values on
different datasets. Figures 7(a), (b), and (c) show the comparison of Loss values for model training on the ETTh1, ETTh2, and ETTm1 datasets, respectively,
while Figures 7(d), (e), and (f) show the comparison of Loss values for model training on ETTh1, ETTh2, and ETTm1 datasets, respectively.

8 and a learning rate set to 0.001. Every time we perturb the
data, we ensure that the ratio of positive and negative samples
is 1 to 1, which makes the model update more necessary when
we input the training data so that our loss can be smoothly
attenuated with a smaller fluctuation range. This means that
our data perturbation method is more robust in the face of
more unevenly distributed data.
The experimental results show that the proposed method
better affects time series prediction tasks and classification

tasks and can handle time series better. Since we limit
the expansion speed of atrous convolution, we have higher
accuracy in univariate prediction and when the data dimension
is smaller. In the prediction task, our method improves the
Univariate prediction of the dataset Electricity by 5.21%.
The dataset ETTm1 improved by 4.38% for Multivariate
prediction. We performed the time series classification task on
the UCR dataset, which improved by 12.73% on the dataset
PigAirwayPressure and 8.39% on the dataset Beef.

1992

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

VI. E NGINEERING A PPLICATIONS
Digital Twin (DT) technology is a virtual modeling-based
technology that creates a virtual copy of the power system in
a computer to simulate and optimize the entire power system.
In this work, DT technology is used to simulate the operation
of the power system and optimize the stability and safety of a
power system. The algorithms proposed in this research have
suitable engineering applications for power grid fault diagnosis
and prediction, intelligent dispatching, and control, which are
detailed next.
• In fault diagnosis and prediction: digital twin technology
can identify faults in the power system and predict
possible future faults by analyzing and processing the data
of the power system. In this investigation, we use digital
twin technology to diagnose faults in the power system
and predict the possible effects of faults on the power
system.
• In terms of intelligent scheduling and control: digital
twin technology can provide intelligent scheduling and
management of the power system based on real-time
data to optimize operational efficiency and energy saving.
In this investigation, we use digital twin technology to
optimize the load distribution of the power system and
improve the energy utilization efficiency of the power
system.
VII. C ONCLUSION AND F UTURE W ORK
To solve the issue of the surge of data in the power grid
model leading to a significant increase in system risk, we
combined the Atrous Convolution method with the simulation
of the digital twin power grid and adopted a new positive
and negative sample selection method. Additionally, time
series prediction and classification tasks are performed on
ETT, electricity, and UCR datasets. Experimental results show
that the algorithm proposed reduces the error rate by 4.38%
and 5.21% in the prediction task and improves the accuracy
by 8.39% and 12.73% in the classification task, which can
forecast the power grid operation, and warns of potentially
dangerous situations, assisting in ensuring the stable operation
of the power grid system.
The key issue of the proposed prediction method is to
forecast the data set in its next steps. Anomaly detection and
processing has always been a significant task of time series,
though it has not been involved in this work. Currently, most
models are trained offline using a large amount of historical
data in the smart grids field, which may not be applicable
to real-time online anomaly detection and also leads to the
problem of lack of data in the initial stage of collecting data
for real-time detection. In future directions, we will conduct
in-depth research on anomaly detection methods.
R EFERENCES
[1] Y. Liu, X. Yang, W. Wen, and M. Xia, “Smarter grid in the 5G era:
Integrating power Internet of Things with cyber physical system,” Front.
Commun. Netw., vol. 2, p. 23, Jun. 2021.
[2] I. Vaccari, E. Cambiaso, and M. Aiello, “Evaluating security of lowpower Internet of Things networks,” Int. J. Comput. Digit. Syst., vol. 8,
no. 2, pp. 101–114, 2019.

[3] M. S. Express. “Brazilian power company hit by ransomware
attack.” 2020. [Online]. Available: https://t.cj.sina.com.cn/articles/view/
2950093642/afd6db4a00100rqe6
[4] AQNIU. “A U.S. power system was attacked by a firewall vulnerability
and the operation was interrupted.” 2019. [Online]. Available: https://
www.sohu.com/a/340509510_490113
[5] Z. Jiang, H. Lv, Y. Li, and Y. Guo,
“A novel application architecture of digital twin in smart grid,” J.
Ambient Intell. Humanized Comput., vol. 13, pp. 3819–3835, Aug. 2022.
[6] C. Qian, X. Liu, C. Ripley, M. Qian, F. Liang, and W. Yu, “Digital
twin—Cyber replica of physical things: Architecture, applications and
future research directions,” Future Internet, vol. 14, no. 2, p. 64, 2022.
[7] N. Tzanis, N. Andriopoulos, A. Magklaras, E. Mylonas, and A. Birbas,
“A hybrid cyber physical digital twin approach for smart grid fault
prediction,” in Proc. IEEE Conf. Ind. Cyberphys. Syst. (ICPS), 2020,
pp. 393–397.
[8] M. Jia, C. Shen, Y. Chen, S. Huang, and Y. Xiang, “Digital twin of the
energy Internet and its application,” Glob. Energy Interconnect., vol. 3,
no. 1, pp. 1–13, 2020.
[9] H. Yz and L. Wang, “Application and development prospect of digital
twin technology in aerospace,” IFAC-PapersOnLine, vol. 53, no. 5,
pp. 732–737, 2020.
[10] H. Pan, Z. Dou, Y. Cai, W. Li, and D. Han, “Digital twin and its
application in power system,” in Proc. 5th Int. Conf. Power Renew.
Energy (ICPRE), 2020, pp. 21–26.
[11] W. Danilczyk, Y. Sun, and H. He, “ANGEL: An intelligent digital twin
framework for microgrid security,” in Proc. North Amer. Power Symp.
(NAPS), 2019, pp. 1–6.
[12] L. Ma, L. Zhou, X. Zhang, C. Xiong, X. Liao, and L. Sun, “Research
on power grid infrastructure project intelligent management platform
based on digital twin technology,” in Proc. IEEE 2nd Int. Conf. Power
Electron. Comput. Appl. (ICPECA), 2022, pp. 1122–1128.
[13] M. Borth, J. Verriet, and G. Muller, “Digital twin strategies for SoS 4
challenges and 4 architecture setups for digital twins of SoS,” in Proc.
14th Annu. Conf. Syst. Syst. Eng. (SoSE), 2019, pp. 164–169.
[14] M. Ahmadi, H. J. Kaleybar, M. Brenna, F. Castelli-Dezza, and
M. S. Carmeli, “Adapting digital twin technology in electric railway
power systems,” in Proc. 12th Power Electron. Drive Syst. Technol. Conf.
(PEDSTC), 2021, pp. 1–6.
[15] Y. Sun, X. Xu, R. Qiang, and Q. Yuan, “Research on security management and control of power grid digital twin based on edge computing,”
in Proc. 2nd Int. Seminar Artif. Intell. Netw. Inf. Technol. (AINIT), 2021,
pp. 606–610.
[16] A. K. Sleiti, J. S. Kapat, and L. Vesely, “Digital twin in energy
industry: Proposed robust digital twin for power plant and other complex capital-intensive large engineering systems,” Energy Rep., vol. 8,
pp. 3704–3726, Nov. 2022.
[17] E. P. Kumar Gilbert, B. Kaliaperumal, E. B. Rajsingh, and M. Lydia,
“Trust based data prediction, aggregation and reconstruction using
compressed sensing for clustered wireless sensor networks,” Comput.
Elect. Eng., vol. 72, pp. 894–909, Nov. 2018.
[18] J. Wu, K. Hu, Y. Cheng, H. Zhu, X. Shao, and Y. Wang, “Data-driven
remaining useful life prediction via multiple sensor signals and deep long
short-term memory neural network,” ISA Trans., vol. 97, pp. 241–250,
Feb. 2020.
[19] S. Casas, W. Luo, and R. Urtasun, “Intentnet: Learning to predict
intention from raw sensor data,” in Proc. Conf. Robot Learn., 2018,
pp. 947–956.
[20] X. Liu, Z. Xiao, R. Zhu, J. Wang, L. Liu, and M. Ma, “Edge sensing
data-imaging conversion scheme of load forecasting in smart grid,”
Sustain. Cities Soc., vol. 62, Nov. 2020, Art. no. 102363.
[21] H. Darvishi, D. Ciuonzo, and P. S. Rossi, “A machine-learning architecture for sensor fault detection, isolation, and accommodation in digital
twins,” IEEE Sensors J., vol. 23, no. 3, pp. 2522–2538, Feb. 2023.
[22] J. Ren and S.-J. Cao, “Incorporating online monitoring data into
fast prediction models towards the development of artificial intelligent ventilation systems,” Sustain. Cities Soc., vol. 47, May 2019,
Art. no. 101498.
[23] F. Wang et al., “Privacy-aware traffic flow prediction based on multiparty sensor data with zero trust in smart city,” ACM Trans. Internet
Technol., vol. 23, no. 3, pp. 1–19, 2022.
[24] H. Balogun, H. Alaka, and C. N. Egwim, “Boruta-grid-search least
square support vector machine for NO2 pollution prediction using big
data analytics and IoT emission sensors,” Appl. Comput. Inform., vol. 16,
pp. 1–13, Aug. 2021.

XIAO et al.: TS-DP: AN EFFICIENT DATA PROCESSING ALGORITHM FOR DISTRIBUTION DT GRID FOR INDUSTRY 5.0

[25] S. Bodenstedt and M. Wagner, “Prediction of laparoscopic procedure
duration using unlabeled, multimodal sensor data,” Int. J. Comput. Assist.
Radiol. Surg., vol. 14, no. 6, pp. 1089–1095, 2019.
[26] C. Yang et al., “Digital twin-driven fault diagnosis method for composite
faults by combining virtual and real data,” J. Ind. Inf. Integr., vol. 33,
Jun. 2023, Art. no. 100469.
[27] S. Sguazza et al., “Sensor data synchronization in a IoT environment
for infants motricity measurement,” in Proc. EAI Int. Conf. IoT Technol.
HealthCare, 2019, pp. 3–21.
[28] K. Skiadopoulos et al., “Synchronization of data measurements in
wireless sensor networks for IoT applications,” Ad Hoc Netw., vol. 89,
pp. 47–57, Jun. 2019.
[29] G. Chalapathi, V. Chamola, S. Gurunarayanan, and B. Sikdar,
“E-SATS: An efficient and simple time synchronization protocol for
cluster- based wireless sensor networks,” IEEE Sensors J., vol. 19,
no. 21, pp. 10144–10156, Nov. 2019.
[30] X. Xu, H. Zhang, T. Li, and L. Zhang, “Achieving resilient data
availability in wireless sensor networks,” in Proc. IEEE Int. Conf.
Commun. Workshops (ICC Workshops), 2018, pp. 1–6.
[31] T. Palanisamy, D. Alghazzawi, S. Bhatia, A. A. Malibari, P. Dadheech,
and S. Sengan, “Improved energy based multi-sensor object detection
in wireless sensor networks,” Intell. Autom. Soft Comput, vol. 33, no. 1,
pp. 227–244, 2022.
[32] Y. Du, B. Qin, C. Zhao, Y. Zhu, J. Cao, and Y. Ji, “A novel spatiotemporal synchronization method of roadside asynchronous MMW
radar-camera for sensor fusion,” IEEE Trans. Intell. Transp. Syst.,
vol. 23, no. 11, pp. 22278–22289, Nov. 2022.
[33] Y. Ishiwatari, T. Otsuka, M. Abukawa, and H. Mineno, “A data
synchronization method for a vehicle using multimodal data features,”
Int. J. Informat. Soc., vol. 11, no. 3, pp. 135–147, 2020.
[34] T. Wang, J. Zhou, A. Liu, M. Z. A. Bhuiyan, G. Wang, and W. Jia,
“Fog-based computing and storage offloading for data synchronization
in IoT,” IEEE Internet Things J., vol. 6, no. 3, pp. 4272–4282, Jun.
2019.
[35] L. Chong, “Research on robust active and reactive coordination
optimization of active distribution network distribution,” M.S. thesis,
School Electron. Eng., Xi’an Petroleum Univ., Huyi, Xi’an, China, 2021.
[36] X. Zhou, Y. Zhang, S. Liu, and W. Luo, “New adaptive dynamic
programming voltage control for static var compensator,” Power Syst.
Protect. Control, vol. 46, no. 12, pp. 77–84, Jan. 2018.
[37] P. Ye, S. Liu, D. Guan, and Z. Jiang, “Distributed energy storage
aggregation model and evaluation method based on adaptive equalization
technology,” J. Shanghai Jiaotong Univ., vol. 55, no. 12, pp. 1689–1699,
Dec. 2021.
[38] J. Lin, C. Cao, and B. Zhang, “Optimal algorithm for fault location
of distribution network based on hierarchical topology model,” Relay,
vol. 30, no. 8, pp. 6–9, Jan. 2002.
[39] J. Gong, W. Wu, and H. Junlin, “Vehicle ad hoc network data transmission algorithm in two-way broadcast mode,” Electron. Technol. Appl.,
vol. 44, no. 7, pp. 107–111, 2018.
[40] Z. Yue et al., “TS2Vec: Towards universal representation of time series,”
2021, arXiv:2106.10466.
[41] H. Zhou et al., “Informer: Beyond efficient transformer for
long sequence time-series forecasting,” in Proc. AAAI, 2021,
pp. 11106–11115.
[42] D. Dua et al., “UCI machine learning repository,” 2017. [Online].
Available: https://archive.ics.uci.edu/
[43] H. A. Dau et al., “The UCR time series archive,” IEEE/CAA J.
Automatica Sinica, vol. 6, no. 6, pp. 1293–1305, Nov. 2019.
[44] S. Li et al., “Enhancing the locality and breaking the memory bottleneck
of transformer on time series forecasting,” in Proc. Adv. Neural Inf.
Process. Syst., vol. 32, 2019, pp. 1–44.
[45] B. N. Oreshkin, D. Carpov, N. Chapados, and Y. Bengio, “N-BEATS:
Neural basis expansion analysis for interpretable time series forecasting,”
2019, arXiv:1905.10437.
[46] S. Bai, J. Z. Kolter, and V. Koltun, “An empirical evaluation of generic
convolutional and recurrent networks for sequence modeling,” 2018,
arXiv:1803.01271.
[47] G. Lai, W.-C. Chang, Y. Yang, and H. Liu, “Modeling long-and shortterm temporal patterns with deep neural networks,” in Proc. 41st Int.
ACM SIGIR Conf. Res. Develop. Inf. Retrieval, 2018, pp. 95–104.
[48] D. Cao et al., “Spectral temporal graph neural network for multivariate
time-series forecasting,” in Proc. Adv. Neural Inf. Process. Syst., vol. 33,
2020, pp. 17766–17778.
[49] J.-Y. Franceschi, A. Dieuleveut, and M. Jaggi, “Unsupervised scalable
representation learning for multivariate time series,” in Proc. Adv. Neural
Inf. Process. Syst., vol. 32, 2019, pp. 1–12.

1993

[50] S. Tonekaboni, D. Eytan, and A. Goldenberg, “Unsupervised representation learning for time series with temporal neighborhood coding,” 2021,
arXiv:2106.00750.
[51] E. Eldele et al., “Time-series representation learning via temporal and
contextual contrasting,” 2021, arXiv:2106.14112.
[52] Y. Chen, B. Hu, E. Keogh, and G. E. Batista, “DTW-D: Time series
semi-supervised learning from a single example,” in Proc. 19th ACM
SIGKDD Int. Conf. Knowl. Discov. Data Min., 2013, pp. 383–391.
[53] G. Zerveas, S. Jayaraman, D. Patel, A. Bhamidipaty, and C. Eickhoff, “A
transformer-based framework for multivariate time series representation
learning,” in Proc. 27th ACM SIGKDD Conf. Knowl. Discov. Data Min.,
2021, pp. 2114–2124.

Lijun Xiao received the master’s degree from the
Hunan University of Science and Technology in
2017. She is currently pursuing the Ph.D. degree in
information management and systems with Shanghai
Maritime University. Her main research interests
include blockchain technologies and cloud security.

Dezhi Han (Member, IEEE) received the Ph.D.
degree from the Huazhong University of Science
and Technology. He is currently a Professor with
Shanghai Maritime University. His specific interests
include storage architecture, blockchain technology,
cloud computing security, and cloud storage security
technology.

Ce Yang received the bachelor’s and Ph.D. degrees
from the University of Science and Technology
of China in 2011 and 2017, respectively. He is
currently a Lecturer with the School of Computer
Science and Engineering, Hunan University of
Science and Technology. His research interests
include information security, privacy protection, and
blockchain technology.

Jiahong Cai is currenlty purusing the Ph.D.
degree with the Hunan University of Science and
Technology. He has published several high-quality
peer-reviewed papers in journals and conferences.
His research interests include deep reinforcement
learning, Internet of Vehicles, and blockchain
security.

1994

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Wei Liang (Senior Member, IEEE) received the
Ph.D. degree in computer science and technology from Hunan University in 2013. He was a
Postdoctoral Scholar with Lehigh University from
2014 to 2016. He is currently a Professor with
the School of Computer Science and Engineering,
Hunan University of Science and Technology. His
research interests include intelligent transportation,
security of IoV, blockchain, embedded system and
hardware IP protection, and security management in
wireless sensor networks.

Kuan-Ching Li (Senior Member, IEEE) received
the Ph.D. degree in electrical engineering from the
University of São Paulo, Brazil. He is currently
a Life Distinguished Professor with Providence
University. Besides publications in high-quality conferences and journals, he is a coauthor or co-editor of
more than 50 books published by Taylor & Francis,
Springer, Elsevier, and McGraw-Hill. His research
interests include parallel and distributed computing,
big data, blockchain, and emerging technologies. He
is a Fellow of the IET and a member of the AAAS.
PAPER_TEXT
