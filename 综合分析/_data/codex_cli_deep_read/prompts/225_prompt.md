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
# [225] Federated Learning-Assisted Distributed Intrusion Detection Using Mesh Satellite Nets for Autonomous Vehicle Protection
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
编号：225
题名：Federated Learning-Assisted Distributed Intrusion Detection Using Mesh Satellite Nets for Autonomous Vehicle Protection
年份：2023
DOI：10.1109/tce.2023.3318727
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2023.3318727.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：联邦学习、隐私保护与分布式协同、IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\225.txt
- 原始字符数：41656
- 本次发送字符数：41656
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
854

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Federated Learning-Assisted Distributed Intrusion
Detection Using Mesh Satellite Nets for
Autonomous Vehicle Protection
Muna Al-Hawawreh, Member, IEEE, and M. Shamim Hossain , Senior Member, IEEE

Abstract—The widespread use of intelligent consumer electronics, specifically autonomous vehicles, has exponentially increased.
The key enablers of this pervasive are the Internet of Things
(IoT), Artificial Intelligence (AI), and Satellite communications,
which provide consumers with highly precise and reliable selfdriving vehicles. However, autonomous vehicles come also with
significant cybersecurity concerns. Attackers can easily use satellite links to launch cyberattacks against autonomous vehicles.
An Intrusion Detection System (IDS) is one of the most effective
mechanisms for providing secure autonomous vehicles. However,
existing IDSs based on machine and deep learning train their
models in a centralized server, which uploads data or parameters to the central server for training. This structure of IDS
has challenges with vehicle mobility, brings processing delays,
and increases privacy and security risks, affecting vehicles’
performance. Therefore, for the first time, this paper proposes
a new federated learning-assisted distributed IDS using a mesh
satellite net to protect autonomous vehicles. We construct a local
model using a deep neural network. Then, we provide a mesh
federated learning approach that keeps model training local and
lets satellites exchange their parameters in a privacy-preserving
way. The simulation results show that our proposed model works
well while keeping the computation cost reasonable.
Index Terms—Consumer electronics, autonomous vehicles,
LEO satellite, federated learning, intrusion detection.

I. I NTRODUCTION
ITH the unprecedented deployment of Internet of
Things (IoT) technologies and the advent of satellite
communications and 5G/6G cellular networks, the digitization of consumer electronics has exponentially increased. One
of these intelligent consumer electronics is autonomous vehicles [1], where the idea of self-driving vehicles sharing the
road has recently become a reality. High-precision satellites
offer the accuracy, ubiquitous connectivity, and reliability that
vehicles need to be self-driving [2]. Hundreds of satellites in
Low Earth orbit (LEO) and Geostationary Orbit (GEO) work

W

Manuscript received 6 February 2023; revised 5 July 2023; accepted 21
September 2023. Date of publication 25 September 2023; date of current version 26 April 2024. The authors extend their appreciation to the Deputyship for
Research & Innovation, Ministry of Education in Saudi Arabia for funding this
research (IFKSURC-1-0305). (Corresponding author: M. Shamim Hossain.)
Muna Al-Hawawreh is with the School of Information Technology, Deakin
University (Geelong Waurn Ponds Campus), Waurn Ponds, VIC 3216,
Australia (e-mail: muna.alhawawreh@deakin.edu.au).
M. Shamim Hossain is with the Research Chair of Pervasive and Mobile
Computing and the Department of Software Engineering, College of Computer
and Information Sciences, King Saud University, Riyadh 11543, Saudi Arabia
(e-mail: mshossain@ksu.edu.sa).
Digital Object Identifier 10.1109/TCE.2023.3318727

together to form satellite constellations, which alter the static
topology of traditional terrestrial networks entirely and allow
for flexible, autonomous vehicles deployment [3], [4]. LEO
satellites are the most dominant and increasingly used to connect directly with autonomous vehicles as they operate in a
lower orbit with less latency and provide wideband Internet
access [5], leading to global coverage, low signal delay times,
and low signal loss. This provides consumers with safer and
more accurate autonomous vehicles than ever in remote or
low-connectivity areas [6].
However, one of the key concerns associated with
autonomous vehicles is cybersecurity [7]. Attackers could
code and make their own keys to get into the car or tamper with the vehicle’s critical parts, such as engines. Recent
demonstrations have shown that attackers could use malware to control the vehicle via LEO satellites and issue
remote commands to unlock it, disable the alarm system, and
start the vehicle engine [8]. Therefore, techniques to protect
autonomous vehicles and cybersecurity solutions applied in
the autonomous vehicles-satellite networks should be updated
to reflect the significant advancements in attacker capabilities
and the characteristics of the autonomous vehicles and LEO
satellites [9], [10]. Intrusion Detection System (IDS) is considered one of the critical parts of the first line of defence in
any cybersecurity framework [9], [11].
Classical machine learning algorithms, such as decision
tree, random forest, and support vector machine [12], [13]
and other common Deep Learning (DL) algorithms, such as
a Recurrent Neural Network(RNN), have been widely used
to build IDSs for satellite communications with intelligent
consumer electronics [14]. Among various DL algorithms,
Deep Neural Networks (DNN) seem to have many potentials [15]. DNN-based models for detecting cyber-attacks
in autonomous vehicles [16] were also proposed, which
can accurately differentiate between benign/normal and malicious traffic. However, IDS-based on DL necessitate powerful
computing capabilities in autonomous vehicles. Not to mention that training models with higher complexities on an
autonomous vehicle can take time and effort. This centralized training task in the autonomous vehicle or even edge
server places a computational load on the central node, which
attackers can also compromise [17], [18], making implementing these centralized IDS on the autonomous vehicles
or edge server impractical. Therefore, training deep and
machine learning model to protect autonomous vehicles while

c 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1558-4127 
See https://www.ieee.org/publications/rights/index.html for more information.

AL-HAWAWREH AND HOSSAIN: FL-ASSISTED DISTRIBUTED INTRUSION DETECTION USING MESH SATELLITE NETS

not leaking the privacy of training data is still a critical
problem.
Several approaches proposed in the literature showed that
Federated Learning (FL) could deliver training tasks to intelligent consumer electronics, in particular, autonomous vehicles
in the intrusion detection field, without leaking training data
privacy [11]. All autonomous vehicle nodes can build a global
model without revealing the data. In traditional FL, each node
synchronously shares its parameters with a central server,
aggregating them and producing new parameters that are sent
back to the connected participants/nodes [19]. After the model
aggregation, a key issue is with the safe storage of the global
model and the parameters at the edge/cloud server. The centralized server often has some risks of tampering, privacy leakage,
and single point of failure [17], [20]. In addition, these existing
and traditional FL models for IDSs inherit the same drawbacks and limitations of client-server network architecture
in terms of scalability, efficient performance, limited vehicle
resources, latency and bandwidth, making them inefficient for
autonomous vehicles.
Therefore, we suggest using satellite nodes to build IDS for
autonomous vehicles. Specifically, we propose a new paradigm
that distributes the intrusion detection tasks among a group of
LEO satellites in a mesh architecture (Mesh Satellite Nets)
instead of sending all parameters or data to a central server or
deploying the detection models in the vehicle. This integrates
efficient training and asynchronous model sharing among
satellite nodes in a mesh network by federated deep learning to
ensure reliable and resilient detection systems. By leveraging
satellite-based monitoring, cyber-attacks against autonomous
vehicles can be quickly and early detected, improving safety
and security. The proposed model collaboratively and automatically detects the attacks in a privacy-preserving manner.
The main contributions are as follows:
1) We propose a FL-assisted distributed IDS using a satellite mesh net for protecting the autonomous vehicle
against cyber attacks. The proposed model provides
more robustness and better privacy and security. To the
best of our knowledge, this is the first paper to present
an FL-based IDS in a mesh architecture using satellites
for intelligent electronic consumers (i.e., autonomous
vehicles).
2) We present a new learning framework that employs FL
and DNN to enable collaborative mesh learning for LEO
satellites and enhance attack detection in autonomous
vehicles.
3) We perform many experiments using three intrusion
datasets to determine the efficiency of our proposed
model.
4) The performance of the proposed model has been evaluated and compared with existing FL-based IDSs using
many performance metrics.
The remainder of this work is organized as follows.
Section II presents the related work, and Section III provides the system model and architecture. Section IV introduces
the proposed federated learning-assisted distributed intrusion
detection using a mesh satellite net. Experimental evaluation
is introduced in Section V. Section VI concludes the work.

855

II. R ELATED W ORK
Mesh satellite net-based FL-oriented communication, one
of the main enablers for AI-enabled human-centric consumer applications, has the potential to offer advanced vehicle
protection services. Intelligent autonomous vehicles that are
human-centric and use the FL intrusion detection approach
can improve consumers’ safety and are crucial for protecting
consumers or drivers in dangerous environments. Therefore,
researchers have recently focused on developing IDS-based
on FL to detect attacks against human-centric consumer applications. For example, Liu et al. [11] presented an FL model
for protecting vehicular edge computing against attacks. They
used DL to power many detection models distributed at the
vehicular edge and the base station layers. In the study of [21],
the authors used the client-server FL with software-defined
network architecture to secure vehicles in the IoT environment.
In related work, Yang et al. [22] used the client-server FL
and ConvLSTM algorithm with a node selection mechanism
for autonomous vehicles. The experimental results showed
the effectiveness of their proposed frameworks in terms of
attack detection rate. Abou El Houda et al. [20] proposed
a detection model for protecting IoT applications using FL
and Game theory. The authors used the non-cooperative game
to ensure the provisioning of the required virtual resources
to deal with the detected attack. Li et al. [3] developed a
distributed network IDS for protecting satellite-terrestrial integrated networks from DDoS attacks using a CNN and FL
approach. While Yazdinejad et al. [23] used the FL and clusterbased machine learning algorithms for anomaly detection in
blockchain-based IoT systems. However, all the models mentioned above are based on client-server architecture. Privacy
and security issues still exist as they use a central server
for parameter aggregation, and this server could become a
bottleneck for the whole network with increasing the number of connected nodes. In addition, the robustness, latency,
bandwidth, and scalability of client-server FL architecture are
challenging, especially for autonomous vehicles which connect
directly with the LEO satellites.
Many collaborative-based IDS are worth mentioning here
to understand the current status of all significant IDSs for
mesh architecture. For example, Arshad et al. [24] proposed
a collaborative approach by correlating the events generated by multiple intrusion detection models deployed in edge
nodes and routers. The proposed approach mainly depended
on statistics and threshold for correlating these events collected in a central server, making them highly vulnerable
to false alarms and single-point failure issues. Similarly,
Wu et al. [25] presented a “Paradise”, a new real-time distributed IDS for IoT systems. They exploited the critical
features of provenance graphs to analyze the dependency of
events generated by multiple IDSs and construct new vectors.
In addition, a Cerebellar Model Articulation Controller-based
IDS (CMACIDS) was proposed by Kumar et al. [26]. In
their proposed IDS, the authors used reinforcement learning and b-spline fit for learning and system adaptability.
Their proposed model was evaluated and obtained a good
precision of attack detection. Although these models mitigate
the drawbacks of client-server architecture, they suffer from

856

Fig. 1.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

A mesh satellite net and the threat against autonomous vehicles.

security and privacy challenges that need further studies to
secure.
The above discussion shows several intrusion detection
models in the literature, each of which has pros and cons.
However, this paper proposes a mesh satellite net-based FLassisted distributed intrusion detection for autonomous vehicle
protection. Our proposed model differs from what has been
presented in the literature 1) it presents the idea of protecting autonomous vehicles using satellite nodes and distributing
intrusion detection tasks among these nodes, and 2) it presents
a mesh architecture for exchanging training DL model parameters in a privacy-preserving manner.

III. P ROPOSED M ESH S ATELLITE N ET
FOR AUTONOMOUS V EHICLES
The proposed mesh satellite net for the autonomous vehicles’ network and the attacker activities against connected
vehicles through satellites are illustrated in Figure 1. The
system consists of many connected autonomous vehicles that
use LEO satellites in their communications and navigation.
The LEO satellites form a mesh network (mesh satellite net)
and exchange their training parameters asynchronously in the
FL approach. In the attack scenario, attackers could exploit
the direct satellite communication links to communicate with
LEO satellites, create a backdoor and inject malware into
the autonomous vehicle. The injected malware communicates
back with the compromised PC, which acts as a command
& control server in the traffic control office (to avoid detection). With IDS based on mesh architecture and FL, each LEO
satellite node can quickly detect attacks against connected
autonomous vehicles as it depends on its local aggregation

model and without needing to communicate with a central
server.
Also, other satellite nodes can easily and quickly learn about
the attacks that their peers and autonomous vehicles face in
the mesh architecture. Thus, in our proposed model, each node
(i.e., LEO satellite) can get a trained intrusion detection model
from other connected nodes in the mesh satellite net. It also
acts as an IDS and uses the newly collected data from connected autonomous vehicles to further train and update its
local model. Then, the node aggregates the network models of
multiple nodes to update their current detection model. Each
LEO satellite node communicates asynchronously with other
network models. It should be noted that each LEO satellite
node in the autonomous vehicle network has only one IDS
model and aggregates the received network models with its
local model.
To ensure the privacy of the local data of each connected
node in the network, each satellite node uses its own intrusion
detection data to train its local model and then aggregates the
parameters of other trained models in the network without
disclosing local data, thereby ensuring the privacy and security of their data. Our proposed model is fully decentralized
and distributed as multiple LEO satellites in mesh architecture
aggregate and update their network models asynchronously.
IV. P ROPOSED M ESH S ATELLITE N ET-BASED F EDERATED
L EARNING I NTRUSION D ETECTION M ODEL
A. Mesh Federated Learning Model
Federated learning is used to train the DL-based intrusion
detection model (i.e., DNN) as described in Algorithm 1. The
LEO satellite nodes (V) are the training nodes and aggregators

AL-HAWAWREH AND HOSSAIN: FL-ASSISTED DISTRIBUTED INTRUSION DETECTION USING MESH SATELLITE NETS

857

Algorithm 1 Mesh Federated Learning Procedure

Algorithm 2 Collaborative DNN Learning Procedure

Data: Initial model parameters (e.g., i, Di , Wi , m, Ai|j , μ)
Result: Global model
for k ≤ K − 1 do
Update parameters for each node i
for i ∈ m do
Calculate wk+1
using
i
 Equation (5)

k
k 2
Calculate inf Ex
i∈V qi (Wi ) + j∈M(i) ρ/2||Ai|j wi + Aj|i wj ||2

Data: Initial DNN parameters
Result: Trained DNN
for epoch ∈ Epoch_max do
Call Model.train()
for i, Di ∈ training_data do
Calculate optimizer.zero_grad()
Calculate output = Model(input)
Calculate Li (w) using Equation (10)
Calculate optimizer.zero_grad()
Calculate Model.backward()
Calculate Optimizer.step()
Calculate Optimizer.update()
end
end

wi |i∈V

for i ∈ m do
Select randomly j ∈ M(i)
,
yk+1
Pull (wk+1
j
j|i ) from j

ykj|i + (1 − θ )
zki|j
Calculate 
zk+1
i|j = (θ

end
end
end

for other network models. These LEO satellite nodes collect
data from connected autonomous vehicles. The dataset vector of (ith) node Vi (i ∈ 1, 2, . . . , m), (m is the number of
connected nodes in the mesh satellite network), is defined as
(Di ). The weight vector trained on (Di ) is represented by (wi ).
When training node’s network model, we seek to minimize
the sum of local-node costs while keeping the model parameters the same across all connected nodes. This optimization
problem can be formulated in Equation (1) and is subject to
Ai|j wi + Aj|i wj = 0, (i ∈ V, j ∈ M(i)), where M(i) is the number of LEO satellite nodes connected with node (i) which is
similar for the whole other connected LEO satellite nodes in
our model (i.e., M(i) = m), and Ai|j ∈ R is the constraint
parameter for the edge between two nodes (i, j).

Fi (Wi )
(1)
inf
wi |i∈V i∈V

Because each step of the statistic gradient can be interpreted
as minimizing a local quadratic function qki with Lipschitz
continuous gradient, and the DNN is continuously differentiable, the new value for weight parameters can be calculated
using Equation (2) (where μ is a condition that forms the
step size). Also, the previous cost function can be reformulated in Equation (3) as a linearly constrained expectation
minimization problem which is also subject to Ai|j wi +Aj|i wj =
0, (i ∈ V, j ∈ M(i)) [27]. To find a robust solution to this constrained minimization problem, we also use the Augmented
Lagrangian method with ρ > 0.

 

(2)
= argmin qki (wi ) = wki − 1/μFi wki
wk+1
i
w
⎡ i
⎤


inf Ex ⎣
qki (Wi ) +
ρ/2||Ai|j wi + Aj|i wkj ||22 ⎦ (3)
wi |i∈V

i∈V

j∈M(i)

However, as we have a lifted dual-variable, i.e., λi|j and λj|i
associated with the connected nodes that enable asynchronous
and peer-to-peer communication in mesh architecture, the cost
function in Equation (3) is also reformulated to support this
communication and the learning process among nodes in the
mesh satellite net (as described in Equation (4) [27]). Where
(ι(1−P) (λ)) is an indicator function that forces (λi|j ) and (λj|i )
to be identical and the permutation matrix (P) enables the
lifted dual variables between satellite nodes. Also, (f k )∗ is

the convex
 conjugate [27] of sum over the local-node cost
f k (w) = i∈V fik (wi ) = qk (w).
 ∗


(4)
inf Ex f k AT λ + ι(1−P) (λ)
λ

However, to reduce the loss function and update each node
in the training process, the new weight parameter of the node
after receiving the network models can be calculated using
Equation (5) and Equation (6) [17], [27].
 

k
wki
wk+1
=
μw
−
F
i
i
i
⎛
⎞

 
T
k
k
+⎝
τi|j Ai|j
zi|j + ρwj ⎠
j∈N(i)

⎛

 ⎝μ +





⎞

diag τi|j + ρ|M(i)|⎠

(5)

j∈M(i)




yk+1
zki|j − 2Ai|j wk+1
i
i|j = 

(6)

Each pair of LEO satellite nodes exchanges and updates
its variables/parameters per around (R) updates for each connected node in the mesh net (using a pull protocol). These
) and dual variable (
yk+1
parameters include weights (wk+1
j
j|i ).
It also use these values to calculate the new value of (
zk+1
i|j )
using Equation (7)


k
k
(7)

zk+1
=
θ
y
+
(1
−
θ
)
z
i|j
i|j
i|j
B. Collaborative Mesh Satellite Learning
A Deep Neural Network (DNN) algorithm is selected to
accomplish the classification task of intrusion detection while
protecting data privacy. DNN is a feedforward neural network
that consists of an input layer, many hidden layers and one
output layer. The input layer maps the multiple inputs (Di ) to
a single output. Assuming (Xi ) is the input samples of data
owner (Di ), a simple DNN model (i.e., input, one hidden, and
output layers) can be expressed as the hypothesis h(Xi , w),
and trained locally by the data owner (Di ) as described in
Algorithm 2.
h(Xi , w) = FC1(FC2(FC3(Xi , wF C3), wF C2), wF C1) (8)
where FC1(∗), FC2(∗), and FC3(∗) stand for the three fully
connected layers and (w∗) is the parameters of the DNN

858

Fig. 2.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Training and communication among LEO satellite nodes based on FL in the autonomous vehicle environment.

layers. The output of h(Xi , w) is calculated using a softmax
classifier as described in Equation (9).
Ypred = softmax(h(Xi , w))

(9)

Moreover, we use the negative log-likelihood as a cost
function as the proposed model has many attack types. It is
computed over a batch of collected observations (B) for data
owner Di using Equation (10).
⎧
⎫
⎬

B 
B
cat
⎨
 

T
T
i
LI (w) = −1/B
Y i = P log ewp X n /
ewp X
⎩
⎭
q=1 p=1

q=1

(10)
Each connected LEO satellite node pulls the network
models and then uses the data collected from connected
autonomous vehicles to perform local learning to train
its local model. The weight wk+1
and dual variable 
yk+1
i
i|j
are calculated under the specified data and then this node
exchanges and pulls these parameters at random time (k)
,
yk+1
from other network nodes wk+1
j
j|i . It should be noted
that only the encrypted parameters are exchanged among the
connected LEO satellite nodes. Figure 2 shows the training
and parameter sharing process among the connected LEO
satellite nodes in the mesh architecture.
V. E XPERIMENTAL E VALUATION
A. Model Evaluation
The third-party library Pytorch was used for the implementation and system model’s simulation on the high-performance
computer (National Computational Infrastructure (NCI)Australia) [28]. The datasets used in this experiment include

X-IIoTID [29] and Ton-IoT datasets [30] as they represent
the modern network traffic and system activities of consumer
electronics, including autonomous vehicles in the era of IoT.
Also, we use the NSL-KDD [31] as a benchmark dataset for
intrusion detection. The X-IIoTID includes more than 421,400
records for normal data and provides 399,417 attack records,
which correspond to various new and critical attacks. The
TON-IoT dataset consists of 300000 records for normal traffic and 161044 for attacks. The NSL-KDD dataset consists
of 77,054 normal and 71460 attack records. The datasets are
divided into two forms: 1) The IID data, where data is evenly
distributed among the LEO satellite nodes (i.e., they have the
same number of classes), 2) The non-IID, where the data is distributed differently, and each LEO satellite node has different
data records and classes.
The experiments tested many performance metrics, including loss, accuracy (Acc), precision (P), recall (R), and
F1-Score (F1). The experimental parameters were selected
based on many experiments where they achieved the best
performance (as listed in Table I). We also choose to test 3,
5, and 7 nodes, similar to most studies in the literature. In
addition, we evaluate the performance of our proposed model
compared with the centralized DNN, where the entire training
data is in a central server (e.g., a ground station). We start by
assessing the effectiveness of the proposed model’s learning.
The proposed model’s training process is examined by observing how the loss decreases during the aggregation process of
the network model. Figures 3 and 4 show the value of loss during the training of both models using IID and non-IID data for
NSL-KDD, Ton-IoT, and X-IIoTID datasets, respectively. It is
clear that both models tended to converge and reduce the loss
with an increasing number of epochs, and both models are

AL-HAWAWREH AND HOSSAIN: FL-ASSISTED DISTRIBUTED INTRUSION DETECTION USING MESH SATELLITE NETS

859

TABLE I
PARAMETERS OF P ROPOSED M ODEL

Fig. 3.

Fig. 4.

Fig. 5.

Accuracy in the case of IID data distribution.

Fig. 6.

Accuracy in the case of non-IID data distribution.

Loss in the case of IID data distribution.

Loss in the case of non-IID data distribution.

equivalent in their loss values. Notably, the proposed model
performs well with non-IID data and performs better than the
centralized one, particularly for the NSL-KDD and TON-IoT
datasets.
The experiment tested the accuracy of models under different epochs. Figures 5 and 6 show that the accuracy increases
with the increasing number of epochs. When the epoch is in
the range of 15-50, the accuracy slightly increases, and the
models start reaching convergence. While for the TON-IoT
dataset, the increase is not apparent between 15-50 epochs,
it quickly reaches convergence in both figures and for both
IID and non-IID data. This is because TON-IoT is an easy
dataset and can be understood quickly. Overall, the proposed
model performed stably for the non-IID data (as described in
Figure 6) and the same results are obtained for IID and for all
datasets. The convergence-curve behavior, i.e., accuracy and
loss curves, did not significantly change with data distribution
among LEO satellite nodes. Therefore, the proposed algorithm is robust against non-IID and IID data, demonstrating

its capabilities in dealing with the mobility and heterogeneous
data of autonomous vehicles.
Table II shows the detailed performance of the proposed
model in terms of Acc, P, R, and F1 under a different number of LEO satellite nodes (i.e., 3, 5, and 7) and for IID data
distribution of X-IIoTID, TON-IoT, and NSL-KDD datasets.
It can be easily seen that when the number of nodes =3,
all LEO satellite nodes (i.e., 1, 2, 3) have approximately the
same values for performance metrics and for all datasets. We
also obtained the same observation in our experiments with
5 and 7 nodes, where all nodes have identical performance.
Also, as the number of LEO satellite nodes increases from
3 to 7, the performance of each model in each node generally improves for the X-IIoTID dataset. For instance, from 3
to 7 nodes, it increased from 96.24% to 97.52%, 97.31% to
98.03%, 96.24% to 97.52%, and 96.74% to 97.70% for Acc, P,
R, and F1, respectively. However, the experiments with TONIoT dataset show that the proposed model achieved the best
performance when the number of LEO satellite nodes is 3,
and the performance decreases when the number of nodes
increases. For example, when the number of LEO satellite
nodes is 3, all nodes achieved 100% for all performance metrics. Also, the performance with 5 and 7 LEO satellite nodes
ranges between 99.97% to 99.98% for all metrics.
Table III also presents the numerical results of all considered intrusion detection models with non-IID data and varying
datasets under a different number of nodes (i.e., 3, 5, and 7).
The proposed model generally has a good performance with

860

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

TABLE II
T HE P ERFORMANCE OF O UR P ROPOSED M ODEL ON IID DATA

TABLE III
T HE P ERFORMANCE OF O UR P ROPOSED M ODEL ON N ON -IID DATA

all datasets and nodes. Importantly, it has stable performance
and is similar to the IID data. The experiments with X-IIoTID
show that accuracy ranges from 97.27% to 97.96%, and from
97.53% to 98.01%, 97.27% to 97.96%, 97.11% to 97.92%
for P, R, and F1, respectively. With the TON-IoT dataset, the
Acc and R range from 98.67% to 99.99%, 99.38% to 99.99%,
and from 98.63% to 99.99% for P and F1, respectively. Also,
the results of the NSL-KDD dataset range from 94.27% to
95.66% for Acc and R while 96.07% to 96.75% and 94.95%
to 96.02% for P and F1, respectively.
The detection rates for the different attacks and three
datasets are shown in Figure 7(a), 7(b), and 7(c). The results
include the detection rate for each attack under centralized,
IID, and Non-IID data distribution. It can be seen that the
performance of our proposed model in classifying different
types of attacks in the TON-IoT dataset is approximately
identical. This is mainly because of the distinguishable features of each attack in this dataset. For NSL-KDD, the attack
detection was a bit challenging due to the minor classes and
lack of the appropriate number of attack observations for the
training model appropriately. However, most importantly, we
can observe that the detection rate of attacks is relatively

TABLE IV
AVERAGE P ROCESSING T IME (S ECONDS ) P ER E POCH AND N ODE

high for the three datasets, proving our proposed model’s
efficiency.
B. Time Complexity Analysis
We calculated the average processing time, including the
time of training, transferring, exchanging and updating parameters. Each node exchanges its parameters 220 communication
rounds, with 11000 total communication rounds. Table IV
shows the calculated value for three datasets. As described in
the Table, the average processing time (seconds) per epoch and
node is varied between the number of LEO satellite nodes and
the data distribution (i.e., IID or non-IID). More specifically,
the value of average processing increases with the number

AL-HAWAWREH AND HOSSAIN: FL-ASSISTED DISTRIBUTED INTRUSION DETECTION USING MESH SATELLITE NETS

Fig. 7.

861

Detection rate of different attack type.

TABLE V
P ERFORMANCE C OMPARISON W ITH AVAILABLE W ORKS

of connected nodes (i.e., 3, 5, 7). It ranges from 23.31 to
32.23 seconds for X-IIoTID, 12.84 to 18.85 seconds for TONIoT, and 4.92 to 7.88 seconds for NSL-KDD datasets. Also,
the average processing time for non-IID data is less than for
IID for three datasets. The model seems to learn quickly when
it has less number of classes. In addition, because of its small
size, the NSL-KDD dataset has the least average processing time. Overall, the proposed model consumes a reasonable
amount of time, irrespective of the data size and distribution, which makes it suitable for detecting attacks against
autonomous vehicles quickly and without any overhead on
LEO satellites.

C. Comparison With Available Works
This subsection explores other works comparable to our
model and evaluates their accuracy and detection rate/recall
performance. We selected L-MGVN [32] and FedCNNMLP [19] using the NSL-KDD dataset in this comparison.
Table V shows that our proposed model achieves high accuracy and recall compared with other models. Both FL-MGVN
and FedCNN-MLP have low-performance detecting attacks,
ranging from 57.10% to 66.88%. This is because FedCNNMLP and FL-MGVN models use client-server FL, where
the average of parameters of selected connected nodes (not
all) is calculated in the server to create a global model,
and the selected connected nodes upload their models synchronously. Thus, choosing specific nodes in the training
process for the global model could lead to not learning about
all attacks. These client-server FL models also have some
risks of tampering, privacy leakage, and a single point of
failure on the server side. It also has scalability, flexibility, and

cost limitations in autonomous vehicles, making them unsuitable for consumer electronics (i.e., vehicles) and even satellite
networks. All these weaknesses of the existing models have
been resolved in our proposed model using a mesh satellite net
architecture.
Our proposed model is fully decentralized and employs
a mesh architecture without a centralized server or a need
to select participants to provide better flexibility. It can
handle heterogeneous data efficiently, as demonstrated in
non-IID experiments. It is also able to detect malicious behavior and identify its type efficiently. However, our proposed
model has some limitations associated with trust in the connected nodes, necessitating blockchain implementation. Also,
selecting the best DNN structure is challenging and may
affect the detection model performance. This limitation could
be solved using evolutionary algorithms such as a genetic
algorithm.

VI. C ONCLUSION AND F UTURE W ORK
Autonomous vehicles are one of the recent advances in intelligent consumer electronics. While this advent of technology
has provided more efficient infrastructure and increased road
safety, it has also come with challenges associated with cybersecurity. Therefore, this paper proposed a new detection model
that uses a mesh satellite net architecture and asynchronous
FL to identify cyber-attacks against autonomous vehicles. Our
proposed model mainly focuses on enabling distributed intelligence and decision-making related to attack detection for
autonomous vehicles using LEO satellite nodes securely and
reliably. Its performance was evaluated using three datasets
(including IID and non-IID), demonstrating its efficiency in
attack detection.
In future work, we will focus on improving the model
performance and studying the effect of implementing the
blockchain in the communication and exchange of parameters
among LEO satellites on the model performance. We also plan
to test the model in a simulated environment of autonomous
vehicles communicating with LEO satellites and investigate its
performance in such a setup.

862

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

R EFERENCES
[1] J. Georgy, A. Noureldin, and C. Goodall, “Vehicle navigator
using a mixture particle filter for inertial sensors/odometer/mapdata/
GPSintegration,” IEEE Trans. Consum. Electron., vol. 58, no. 2,
pp. 544–552, May 2012.
[2] D. Parekh et al., “A review on autonomous vehicles: Progress, methods
and challenges,” Electronics, vol. 11, no. 14, p. 2162, 2022.
[3] C. Li, L. Zhu, M. Luglio, Z. Luo, and Z. Zhang, “Research on satellite
network security mechanism based on blockchain technology,” in Proc.
IEEE Int. Symp. Netw. Comput. Commun. (ISNCC), 2021, pp. 1–6.
[4] C.-Y. Yang, J.-F. J. Yao, C.-E. Yen, and M.-S. Hwang, “Overview on
physical layer security in low earth orbit (LEO) satellite system,” in
Proc. IEEE Int. Conf. Consum. Electron. (ICCE-TW), 2021, pp. 1–2.
[5] H. Guo, J. Li, J. Liu, N. Tian, and N. Kato, “A survey on space-airground-sea integrated network security in 6G,” IEEE Commun. Surveys
Tuts., vol. 24, no. 1, pp. 53–87, 1st Quart., 2021.
[6] S. Kuutti, S. Fallah, K. Katsaros, M. Dianati, F. Mccullough, and
A. Mouzakitis, “A survey of the state-of-the-art localization techniques
and their potentials for autonomous vehicle applications,” IEEE Internet
Things J., vol. 5, no. 2, pp. 829–846, Apr. 2018.
[7] S. McLachlan, B. Schafer, K. Dube, E. Kyrimi, and N. Fenton,
“Tempting the fate of the furious: Cyber security and autonomous cars,”
Int. Rev. Law Comput. Technol., vol. 36, no. 2, pp. 181–201, 2022.
[8] T. Pultarova, “News-cyber security-hacking behind third of London’s
car theft [news briefing],” Eng. Technol., vol. 9, no. 9, p. 10, 2014.
[9] L. Yang, A. Shami, G. Stevens, and S. De Rusett, “LCCDE: A decisionbased ensemble framework for intrusion detection in the Internet of
Vehicles,” in Proc. IEEE Global Commun. Conf. (GLOBECOM), 2022,
pp. 3545–3550.
[10] A. R. Mahlous, “Cyber security challenges in self-driving cars,” Comput.
Fraud Security, vol. 2022, no. 7, pp. 1–8, 2022.
[11] H. Liu et al., “Blockchain and federated learning for collaborative intrusion detection in vehicular edge computing,” IEEE Trans. Veh. Technol.,
vol. 70, no. 6, pp. 6073–6084, Jun. 2021.
[12] Y. Goh, D. Jung, G. Hwang, and J.-M. Chung, “Consumer electronics
product manufacturing time reduction and optimization using AI-based
PCB and VLSI circuit designing,” IEEE Trans. Consum. Electron.,
vol. 69, no. 3, pp. 240–249, Aug. 2023.
[13] R. Gundu and M. Maleki, “Securing CAN bus in connected and
autonomous vehicles using supervised machine learning approaches,”
in Proc. IEEE Int. Conf. Electron. Inf. Technol. (eIT), 2022, pp. 42–46.
[14] S. Dasgupta, M. Rahman, M. Islam, and M. Chowdhury, “A sensor fusion-based GNSS spoofing attack detection framework for
autonomous vehicles,” IEEE Trans. Intell. Transp. Syst., vol. 23, no. 12,
pp. 23559–23572, Dec. 2022.
[15] P. Dixit and S. Silakari, “Deep learning algorithms for cybersecurity
applications: A technological and status review,” Comput. Sci. Rev.,
vol. 39, Feb. 2021, Art. no. 100317.
[16] S. Almutlaq, A. Derhab, M. M. Hassan, and K. Kaur, “Two-stage
intrusion detection system in intelligent transportation systems
using rule extraction methods from deep neural networks,”
IEEE Trans. Intell. Transp. Syst., early access, Sep. 8, 2022,
doi: 10.1109/TITS.2022.3202869.
[17] M. Al-Hawawreh, E. Sitnikova, and N. Aboutorab, “Asynchronous peerto-peer federated capability-based targeted ransomware detection model
for Industrial IoT,” IEEE Access, vol. 9, pp. 148738–148755, 2021.
[18] Y. Yang et al., “ASTREAM: Data-stream-driven scalable anomaly detection with accuracy guarantee in IIoT environment,” IEEE Trans. Netw.
Sci. Eng., vol. 10, no. 5, pp. 3007–3016, Sep./Oct. 2023.
[19] W. Liu et al., “Intrusion detection for maritime transportation systems
with batch federated aggregation,” IEEE Trans. Intell. Transp. Syst.,
vol. 24, no. 2, pp. 2503–2514, Feb. 2023.
[20] Z. Abou El Houda, B. Brik, A. Ksentini, L. Khoukhi, and M. Guizani,
“When federated learning meets game theory: A cooperative framework to secure IIoT applications on edge computing,” IEEE Trans. Ind.
Informat., vol. 18, no. 11, pp. 7988–7997, Nov. 2022.
[21] A. Hbaieb, S. Ayed, and L. Chaari, “Federated learning based IDS
approach for the IoV,” in Proc. 17th Int. Conf. Availability Rel. Security,
2022, pp. 1–6.

[22] J. Yang, J. Hu, and T. Yu, “Federated AI-enabled in-vehicle network
intrusion detection for Internet of Vehicles,” Electronics, vol. 11, no. 22,
p. 3658, 2022.
[23] A. Yazdinejad, A. Dehghantanha, R. M. Parizi, M. Hammoudeh,
H. Karimipour, and G. Srivastava, “Block hunter: Federated learning for
cyber threat hunting in blockchain-based IIoT networks,” IEEE Trans.
Ind. Inform., vol. 18, no. 11, pp. 8356–8366, Nov. 2022.
[24] J. Arshad, M. A. Azad, M. M. Abdellatif, M. H. U. Rehman, and
K. Salah, “COLIDE: A collaborative intrusion detection framework for
Internet of Things,” IET Netw., vol. 8, no. 1, pp. 3–14, 2019.
[25] Y. Wu et al., “Paradise: Real-time, generalized, and distributed
provenance-based intrusion detection,” IEEE Trans. Depend. Secure
Comput., vol. 20,no. 2, pp. 1624–1640, Mar./Apr. 2020.
[26] G. Kumar, R. Saha, M. Conti, R. Thomas, T. Devgun, and J. Rodrigues,
“Adaptive intrusion detection in edge computing using cerebellar model
articulation controller and spline fit,” IEEE Trans. Services Comput.,
vol. 16, no. 1, pp. 900–912, Mar./Apr. 2023.
[27] K. Niwa, N. Harada, G. Zhang, and W. B. Kleijn, “Edge-consensus
learning: Deep learning on P2P networks with nonhomogeneous data,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Disc. Data Min., 2020,
pp. 668–678.
[28] “National computational infrastructure.” Accessed: Aug. 2021. [Online].
Available: https://nci.org.au/
[29] M. Al-Hawawreh, E. Sitnikova, and N. Aboutorab, “X-IIoTID:
A connectivity-agnostic and device-agnostic intrusion data set for
Industrial Internet of Things,” IEEE Internet Things J., vol. 9, no. 5,
pp. 3962–3977, Mar. 2022.
[30] M. Sarhan, S. Layeghy, N. Moustafa, and M. Portmann, “Netflow
datasets for machine learning-based network intrusion detection
systems,” in Big Data Technologies and Applications. Heidelberg,
Germany: Springer, 2020, pp. 117–135.
[31] M. Tavallaee, E. Bagheri, W. Lu, and A. A. Ghorbani, “A detailed analysis of the KDD CUP 99 data set,” in Proc. IEEE Symp. Comput. Intell.
Security Defense Appl., 2009, pp. 1–6.
[32] D. Wu, Y. Deng, and M. Li, “FL-MGVN: Federated learning for
anomaly detection using mixed gaussian variational self-encoding
network,” Inf. Process. Manag., vol. 59, no. 2, 2022, Art. no. 102839.

Muna Al-Hawawreh (Member, IEEE) is an Assistant Professor of
Cybersecurity with the School of Information Technology, Deakin University
(Geelong Waurn Ponds Campus), Waurn Ponds, VIC, Australia.

M. Shamim Hossain (Senior Member, IEEE) is currently a Professor with the
Department of Software Engineering, College of Computer and Information
Sciences, King Saud University, Riyadh, Saudi Arabia. He is the Highly Cited
Researcher in the field of Computer Science (Web of Science). He is the Chair
of the IEEE Special Interest Group on Artificial Intelligence for Health with
the IEEE ComSoc eHealth Technical Committee. He is the Symposium Chair
of Selected Areas in Communications (E-Health) with IEEE GLOBECOM
2024. He is the Technical Program Co-Chair of ACM Multimedia 2023. He
is currently the Chair of the Saudi Arabia Section of the Instrumentation
and Measurement Society Chapter. He is on the editorial board of
the IEEE T RANSACTIONS ON I NSTRUMENTATION AND M EASUREMENT,
IEEE T RANSACTIONS ON M ULTIMEDIA, ACM Transactions on Multimedia
Computing, Communications, and Applications, IEEE M ULTIMEDIA, IEEE
N ETWORK, IEEE W IRELESS C OMMUNICATIONS, and Journal of Network
and Computer Applications (Elsevier). He is a Distinguished Member of
ACM. He is an IEEE Distinguished Lecturer.
PAPER_TEXT
