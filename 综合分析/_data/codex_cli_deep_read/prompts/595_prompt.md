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
# [595] Adaptive Federated Reinforcement Learning With Temporal Hybrid Deep Model for Consumer Internet of Vehicles Intrusion Detection
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
编号：595
题名：Adaptive Federated Reinforcement Learning With Temporal Hybrid Deep Model for Consumer Internet of Vehicles Intrusion Detection
年份：2025
DOI：10.1109/tce.2025.3634753
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3634753.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、时序、日志、KPI 与云原生异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\595.txt
- 原始字符数：52249
- 本次发送字符数：52249
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2036

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

Adaptive Federated Reinforcement Learning With
Temporal Hybrid Deep Model for Consumer
Internet of Vehicles Intrusion Detection
Hamad Naeem , Amjad Alsirhani , Faeiz M. Alserhani , Maha M. Althobaiti , and Eatedal Alabdulkreem

Abstract— Consumer devices that are integrated into the Internet of Vehicles (IoV) systems are becoming more susceptible to
the sophisticated intrusion attacks, which are a major threat to
user safety and the overall integrity of the system. Federated
Learning (FL) has been a prominent technique for collaborative training models while maintaining the confidentiality of
sensitive information. In addition, conventional FL-based IDS
approaches have problems to handle non-identical IID (IID) data
distributions across clients, and usually use a fixed aggregation
method like FedAvg and FedProx, which has poor adaptability
to changeable client behaviors. To tackle these limitations, this
research proposes an adaptive federated learning framework by
preprocessing IoVs network traffic through standardization and
IID (independent and identical distributed) distribution of data
among clients. A Temporal Hybrid Deep Model (CNN-LSTMAttention) is trained on each client locally (starting from the
global model). After training, client models and performance
metrics are updated to a central server, where a Reinforcement
Learning (RL) agent based on Deep Q-Network (DQN) optimally
decides aggregation weights based on client Q-values, which
maximizes global accuracy as a reward. Iterative aggregation
greatly improves intrusion detection performance, with detection
accuracies of 99.85% and 95.18% on the benchmark datasets
CICIOV2024 and CICEVSE2024, respectively. The proposed
method makes it possible to develop a lightweight, edgedeployable intrusion detection system for consumer IoV device
like telematics and electric car chargers. By leveraging federated
learning, the approach provides real-time, privacy-preserving
protection.
Received 16 August 2025; revised 8 October 2025 and 30 October 2025;
accepted 16 November 2025. Date of publication 19 November 2025;
date of current version 25 March 2026. This work was supported by
the Deanship of Scientific Research, Vice Presidency for Graduate Studies and Scientific Research, King Faisal University, Saudi Arabia [Grant
No. KFU253849]. The work of Eatedal Alabdulkreem was supported by
the Princess Nourah bint Abdulrahman University Researchers Supporting
Project, Princess Nourah bint Abdulrahman University, Riyadh, Saudi Arabia,
under Grant PNURSP2025R161. (Corresponding author: Hamad Naeem.)
Hamad Naeem is with the Department of Computer Science, College of
Computer Sciences and Information Technology, King Faisal University, AlAhsa 31982, Saudi Arabia (e-mail: haazaam@kfu.edu.sa).
Amjad Alsirhani is with the Department of Computer Science, College of
Computer and Information Sciences, Jouf University, Sakakah, Al Jouf 72388,
Saudi Arabia (e-mail: amjadalsirhani@ju.edu.sa).
Faeiz M. Alserhani is with the Department of Computer Engineering and
Networks, College of Computer and Information Sciences, Jouf University,
Sakakah, Al Jouf 72388, Saudi Arabia (e-mail: fmserhani@ju.edu.sa).
Maha M. Althobaiti is with the Department of Computer Science, College
of Computing and Information Technology, Taif University, Taif 21944,
Saudi Arabia (e-mail: Maha_m@tu.edu.sa).
Eatedal Alabdulkreem is with the Department of Computer Sciences,
College of Computer and Information Sciences, Princess Nourah bint Abdulrahman University, P.O. Box 84428, Riyadh 11671, Saudi Arabia (e-mail:
eaalabdulkareem@pnu.edu.sa).
Digital Object Identifier 10.1109/TCE.2025.3634753

Index Terms— Federated learning, Internet of Vehicles, intrusion detection system, reinforcement learning, cybersecurity.

I. I NTRODUCTION

C

ONSUMER-ORIENTED cybersecurity attacks on the
Internet of Vehicles (IoV) have become a growing concern as IoV technologies are improving and increasingly filling
the day-to-day lives of individuals in attempts to create greater
convenience, safety and driving experience to the end user.
Recent studies have shown that the threats to consumers are
increasing. These include data breaches, unauthorized access,
spoofing, denial of service (DoS) and ransomware, all of which
directly damage consumer trust and lower the adoption of IoV.
These threats demonstrate how important it is to have strong
security measures in place to protect consumers as well as
ensure sure that IoV applications keep on growing.
The Internet of Vehicles (IoV) is an integral component of
the Internet of Things (IoT), and is causing a revolution in
transportation by allowing vehicles, infrastructure and personal
gadgets to connect to each other in new ways. Advanced
sensor technologies built into cars and roadside devices now
generate an extensive amount of data, which is supporting
innovative applications which make transportation more efficient and improve the user experience [1]. Both government
and industry leaders all over the world are advocating for the
use of intelligent transportation systems (ITS) fueled by IoV.
These systems can be used for real time traffic monitoring,
self-driving cars, automated toll collection and comprehensive
vehicle to everything (V2X) communications [2], [3], [4].
The consumer plays an important role in this scenario as the
success and the social impact of IoV rely heavily on trust and
engagement by the end user.
The deployment of fifth generation (5G) cellular networks
has accelerated the possibilities of IoV further by adding
greater reliability, higher throughput, lower latency and ubiquitous connectivity, which are necessary for smooth and real
time IoV services [5], [6]. These technological advances
have increased the Internet of Things (IoT) reach, and it
has extended its reach to other areas like smart homes,
health monitoring, and, importantly, consumer-based Intelligent Transportation Systems (ITS) solutions.
One of the things that makes IoV stand out is that it allows
several different types of communications, including the
following: vehicle-to-vehicle (V2V), vehicle-to-infrastructure

1558-4127 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

NAEEM et al.: ADAPTIVE FEDERATED REINFORCEMENT LEARNING WITH TEMPORAL HYBRID DEEP MODEL

(V2I), vehicle-to-pedestrian (V2P), and vehicle-to-network
(V2N) interactions. These modes of communication work
in combination with each other to make things safer, more
efficient and comfortable for users. They often use advanced
machine learning and artificial intelligence to improve service
delivery.
As attacks on consumers become more sophisticated,
modern research focuses on creating robust authentication
protocols, secure communication frameworks, and smart intrusion detection systems that deal with the unique issues that
consumer IoV environments face. Privacy, security and data
integrity are important to ensure consumer confidence to
ensure the full benefits of IoV adoption for society.
Two important problems of federated learning in 5G enabled
Consumer Internet of Vehicles (IoV) environment such as
non-identically and independently distributed (Non-IID) data
across client devices because of which model performance
and convergence problem occur [7]. Additionally, static aggregation methods like FedAvg and FedProx are not highly
adaptable to variability in client capabilities and network
dynamics and thus, they fail to be effective in real life
consumer-centric IoV applications [8]. This study has the
following contributions for solving the challenges that exist
in current federated learning solutions:
• A federated learning framework is proposed for detecting
malicious activity in 5G-enabled Consumer Internet of
Vehicles (IoV). It is designed specifically to deal with
non-IID data distribution and overcome the problems with
static aggregating approaches like FedAvg and FedProx.
• The framework applies a Temporal Hybrid Deep Model
(CNN-LSTM-Attention) to train each client locally, initializing the weights from the global model. A Deep
Q-Network (DQN) agent based on reinforcement learning
is additionally employed at the server to dynamically
assign aggregation weights to each client based on their
Q-values, which optimizes global model updates.
• Extensive experiments on the CICIoV2024 [9] and
CICEVSE2024 [10] attack detection datasets validate the
framework’s effectiveness, with findings exhibiting superior performance compared to typical federated learning
baselines in IoV intrusion detection scenarios.
The structure of the paper is as follows: Section II reviews
related work, Section III explains the proposed method,
Section IV discusses about the outcomes, and Section V
concludes.
II. R ELATED W ORK
The Internet of Things (IoT) industry is growing quickly,
and this shift is closely related to the adoption of 6G networks,
resulting in security challenges more severe [11]. IoT technologies have significantly transformed the networking and
communication landscape [12]. Generally, definitions of the
Internet of Things (IoT) and the Internet of automobiles (IoV)
refer to physical entities that are connected to each other,
including sensors and automobiles. However, there can be
different interpretations [13]. The concept of IoT/IoV now
covers everything from local networks to large networks, such

Fig. 1.
(IoVs).

2037

Applications of Federated Learning (FL) in Internet of Vehicles

as LANs and the emerging 6G infrastructure. This change
is mainly because 5G can’t handle the high demands from
emerging IoT and IoV applications [14]. As more devices
connect to the Internet of Things (IoT) and Internet of Vehicles
(IoV) systems, the amount of network traffic continues to
expand. These technologies enhance daily life and industrial
processes better, but they are also witnessing more malware
threats at all the levels and throughout the entire network’s
life cycle [15]. Since it was first introduced, federated learning
has drawn a lot of attention for its ability to solve problems
related to data privacy, communication overhead, and client
data variability [16]. Federated reinforcement learning (FRL)
is a method that combines edge computing with distributed
deep learning. Its aim is to enable urban sensing systems run
more efficiently [17]. Recent studies show that decentralized
data stored on devices may assist in identify IoT-related threats
directly at the edge layer [18]. This approach applies Federated
Learning (FL) as its main method, therefore there is no need
for moving sensitive data offsite for processing [19]. FL not
only speeds up model training on edge devices by keeping
data local, but it also greatly improves data security. The
emergence of the fourth industrial revolution and progress
in communication technologies have driven the adoption of
digital twins (DT), federated learning (FL), and the Industrial
Internet of Things (IIoT). However, implementing DT and FL
in IoV remains challenging. Recent studies have examined
applications of IoT, IoV, and the Internet of Drones (IoD) for
digital transformation (DT) and federated learning (FL) [20].
Federated learning (FL) has been extensively explored for
improving Internet of Vehicles (IoV) applications. Previous
research has examined FL across various fields, including
to Autonomous Aerial Vehicles (AAVs), autonomous driving
systems, and electric automobile networks [21]. Additional
research has addressed areas like vehicle selection, resource
optimization, and traffic flow prediction. Other topics include
map management, content caching, vehicle positioning, and
estimating parking spaces [22], as illustrated in Fig. 1. Vehicles
are typically unwilling to send their raw local data straight
to roadside units (RSUs) because they have concerns about
privacy and security. In this situation, federated learning (FL)
is a good way to do vehicular edge computing (VEC) since
it lets cars communicate only their model parameters with
adjacent RSUs instead of sensitive local data. This approach

2038

Fig. 2.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

Adaptive federated learning for 5G-enabled consumer internet of vehicles intrusion detection.

makes FL a good choice for machine learning problems
in vehicular networks [23]. Collaboration among Vehicle-toEverything (V2X) nodes is essential for building effective
machine learning-based attack detection models in 5G and
beyond vehicular networks [24].
Federated learning in IoV environments faces various challenges, like non-IID data distribution among clients, limited
adaptability of static aggregation methods and vulnerability
to underperforming or malicious participants. Additional challenges involve making it scalable as the number of clients and
data increase and maintaining computational and communication efficiency. These things can make it so that the models
do not converge as easily, are not accurate, and are not as
strong in real life scenarios. Our proposed solution solves
these problems by adopting a reinforcement learning-based
(DQN) adaptive aggregation technique that assigns different
weights to clients based on their performance. This method
lowers communication overhead while increasing accuracy,
robustness, and scalability when combined with multi-head
attention and a hybrid CNN-LSTM model.
III. A DAPTIVE F EDERATED L EARNING FOR 5G- E NABLED
C ONSUMER I NTERNET OF V EHICLES I NTRUSION
D ETECTION
This work tackles two major issues in the context of federated learning for 5G enabled Consumer Internet of Vehicles
(IoV) networks namely: 1) non-IID data distribution among
clients and 2) the lack of adaptability of the static aggregation techniques like FedAvx and FedProx. The proposed
framework preprocesses IoV network traffic, standardizes and

splits the data and distributes it IID-wise among clients.
Each client learns a Temporal Hybrid Deep Model (CNNLSTM-Attention), based on its local data, with global weights.
After each round, the clients send their trained weights and
performance metrics to the server and a Deep Q-Network
(DQN) agent is used to adaptively assign the aggregation
weights based on client Q values. The softmax normalized
weights update the global model which is re distributed to
clients for the next round. This iterative process using global
accuracy as a reward optimizes aggregation and intrusion
detection performance strength for Internet of Vehicles. Fig. 2
shows the proposed adaptive federated learning framework for
secure IoV intrusion detection based on reinforcement learning
aggregation.
A. Data Preprocessing
The data preprocessing stage is important to ensure that the
raw IoV network data is clean, structured, and suitable for
intrusion detection using deep learning models. The first step
is to gather the raw network information from the Internet
of Vehicles (IoV) environment, which includes information
about communication between vehicles, roadside units and IoT
infrastructure. This raw data, typically in the form of packet
capture (PCAP) files or logs, is parsed to extract useful features
and converted to a structured feature matrix that can be used
for analysis.
After the parsing is done, there might be irrelevant or noisy
data in the dataset, such as incomplete data or duplicate flows
or corrupted packets. The unwanted items are filtered in order
to obtain a clean dataset. The network flows are then created

NAEEM et al.: ADAPTIVE FEDERATED REINFORCEMENT LEARNING WITH TEMPORAL HYBRID DEEP MODEL

from the cleaned data, where the flows aggregate packets or
events with common properties like source or destination IP,
protocol, session or time window.
Next, the mean and the standard deviation of each feature
in the dataset is scaled to have a mean of zero and a standard
deviation of one, an important step in effective neural network
training. For each feature vector x, standardization is carried
out as follows:
x′ =

x −µ
σ

(1)

where µ and σ are the mean and standard deviation of
the feature respectively. This is performed for each feature
dimension and we finish with a standardized feature matrix.
The standardized dataset is then divided into subsets for
training and testing so that it allows for proper validation
of the model and prevents overfitting, with usually 80% of
the data being used for training and 20% being used for
testing. After these preprocessing steps, processed data is then
ready for IID data distribution between federated learning
clients.
B. Client-Level IID Data Partitioning in Federated Learning
One of the main challenges of Federated Learning (FL)
is the availability of non-identically and independently distributed (non-IID) data across the participating clients. In real
world scenarios in FL, each client collects information from
its own individual environment, leading to a lot of diversity
in local data distributions and the risk of divergence in the
local models. This data heterogeneity can significantly reduce
the effectiveness of federated aggregation strategies and hinder
overall model performance, especially in critical applications
such as the Internet of Vehicles (IoV). To overcome this, the
proposed framework includes data preprocessing that ensures
the allocation of client-level IID (independent and identically
distributed) data in order to have a more balanced and representative data set for each client’s training locally. The
workflow is random shuffling of indices of the whole data
and equally dividing the data between the clients. Specifically,
given a dataset D with |D| samples for N clients then number
of samples per clients is defined as


|D|
S=
,
(2)
N
where S is the number of samples allocated in each client.
After generating a random permutation π of the dataset
indices, each client i is allocated a segment given by
Di = Dπ( j) | j = i S, . . . , (i + 1)S − 1,

(3)

Ensuring that the subset of data is similar to the global
distribution across all clients in order to achieve a realistic
simulation of an IID setting for federated training. By enhancing uniformity of the client level data, this enhances greater
stability and fairness of the global aggregation of the model,
reduces inter client bias, and supports a better evaluation of
federated learning algorithms.

2039

C. Client Side Temporal Hybrid Deep Model Training
In the proposed federated learning framework for secure
intrusion detection in IoV environments, the client side training is an important step in the process which leverages a
powerful deep learning model allowing to learn local data
patterns without the loss of privacy. Once data preprocessing
and IID distribution are completed, each client node is given
a divided data set as well as a copy of the global model
weights which ensures the training begins with a standard
initialization. Each client then starts local training based on
a Temporal Hybrid Deep Model of a Convolutional Neural
Network (CNN), Long Short-Term Memory (LSTM) Network
and Multi-Head Attention mechanism. The major goal of this
stage is to optimize the local model parameters, θk , for each
client k, by minimizing the loss function using the client’s
local dataset (X k , yk ):
|X |

θk∗ = arg min
θ

k
1 X
L( f θ (xi ), yi )
|X k |

(4)

i=1

Here, f θ is the deep model, and L is the classification crossentropy loss. Stochastic gradient descent (SGD) or an adaptive
optimizer is applied each time to update the model of each
client during training. After each round of communication,
the local prediction results, e.g. accuracy, precision, recall,
confusion matrix elements are calculated and reported. At the
completion of local training, the updated model weights and
local performance metrics are sent back to the federated server.
This process is repeated for a number of rounds, with each
round starting from the updated global model, and therefore,
each round improving the ability of the model to generalize
over all the data of the clients.
The Temporal Hybrid Deep Model is a composite model
that tries to extract and combine short term and long term
temporal dependencies within IoV network data, which is
often highly sequential and structured. The model takes as
input the sequence X ∈ Rs×d , where s is the length of the
sequence and d is the dimension of features.
1) TCN Pathway: One branch goes through stacked 1D
convolutional layers (Conv1D), each one has kernel size 3 and
ReLU activation, which is responsible for capturing local
temporal patterns:
(l−1)
(l)
h(l)
conv = ReLU(Conv1D(hconv , Wconv ))

(5)

where l indexes the convolutional layer. Dropout is applied
for regularization. A Global Average Pooling layer follows,
aggregating features across time:
s

htcn =

1 X (L)
hconv [t]
s

(6)

t=1

where L is the last convolutional layer.
2) LSTM Pathway: Simultaneously, the input sequence
is fed into an LSTM layer, which models long-term
dependencies:
hlstm = LSTM(X )

(7)

A dense layer is used to further transform the LSTM output.

2040

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

3) Feature Concatenation and Attention: The outputs of the
TCN and LSTM paths are concatenated:
hconcat = Concat([htcn , hlstm ])

(8)

This combined feature vector is reshaped as required and
passed through a Multi-Head Attention mechanism, which
learns interdependencies between temporal features:
hattn = MultiHeadAttn(hconcat )

(9)

4) Classification Head: The attention output is flattened and
passed through one or more dense layers with ReLU activation
to produce the final class predictions. The output layer uses a
softmax function for multi-class classification:
ŷ = softmax(Wout hfinal + bout )

(10)

where hfinal is the flattened attention output.
In Fig. 3, using TCNs and LSTMs together for IoV traffic
takes use of their distinct strengths. TCNs (causal, dilated convolutions) get fine-grained, local patterns across long effective
receptive fields with stable, parallelizable training. LSTMs,
on the other hand, get order-sensitive, long-horizon dependencies with non-stationary context. Combining both and
re-weighting important timesteps with multi-head attention
creates more distinct temporal characteristics, which lowers
false alarms and makes the system more stable against jitter
and packet loss. In practice, the hybrid is good for edge
deployment and provides quicker, more reliable federated
convergence than either component alone. Algorithm 1 summarizes the procedural workflow described in this section.
It trains each client’s model by starting with the current global
weights, fitting it to local data for E epochs, and producing
updated local parameters. After training, it calculates and
sends back the client’s local weights, as well as the accuracy
and loss, for aggregation and monitoring.

Algorithm 2 Global Model RL-Based Weights Aggregation
Input: τ ′ : total federated rounds, wi : local model
weights, A: local accuracies
Output: wτ : updated global model weights(GMU)
initialization;
0
1 Initialize global model weights w ;
′
for each round τ = 1 to τ do
2
Form state vector: sτ ← r eshape(Aτ );
3
Predict Q-values: Q τ ← agent. pr edict (sτ );
4
Compute Softmax weights: wτR L ← softmax(Q τ );
PK
5
w τ ← i=1
wi · w τR L [i];
6
Set global model weights: wg ← wτ ;
7
Evaluate wg on test data (X test , ytest );
8
Compute metrics: Accuracy, ROC AUC, Precision,
Recall, F1-Score, Loss;
9
Compute reward rτ from global accuracy;
10
Observe next state sτ +1 ← r eshape(Aτ );
11
Store transition:
agent.remember(sτ , arg max Q τ , rτ , sτ +1 , done);
if agent.memory size > batch size then
12
agent.replay(batch size);
13
14

Save checkpoint: wg → roundτ .ckpt;
Track and store performance metrics in history
arrays;
return w τ as final GMU

Algorithm 1 Local Model Training Process
Input: Rounds R, Client data Di = (X i , yi ), Global
weights wg
Output: Local weights wi , Performance metrics
for each round r = 1 to R do
for each client i = 1 to N do
Initialize local model Mi with weights wg ;
Train Mi on (X i , yi ) for E epochs;
Obtain updated local weights wi ;
Compute local accuracy and loss;
return local weights, accuracy, loss

D. Server Side Adaptive Aggregation Using Reinforcement
Learning
A key issue in FL is the lack of flexibility of traditional
static aggregation methods, such as FedAvg and FedProx,
which use static or heuristic weights for the aggregation of
client’s updates irrespective of their individual contributions to
the overall task across rounds. These conventional approaches
are generally not capable of dynamically adapting to the

Fig. 3. Integrated temporal convolutional and LSTM network with attention
mechanism.

cases of heterogeneous distributions of client data or changing
local performance and thus, the global model accuracy is

NAEEM et al.: ADAPTIVE FEDERATED REINFORCEMENT LEARNING WITH TEMPORAL HYBRID DEEP MODEL

suboptimal and convergence speed is slower. To overcome
such limitation, in this paper, we propose a reinforcement
learning-based adaptive aggregation strategy that allows for the
dynamic optimization of the aggregation weights according to
the real time feedback of the performance of client models.
In the proposed federated learning framework for secure IoV
intrusion detection, the server side adaptive aggregation uses
reinforcement learning (RL) to intelligently and dynamically
combine the model updates from multiple clients. Once the
locally trained model weights and associated performance
metrics (e.g. accuracies or losses) are received from all participating clients, the central federated server will trigger the
adaptive aggregation process. The server keeps these local
weights and instead of static aggregation techniques such as
FedAvg, uses a Deep Q-Network (DQN) agent to find the
optimal aggregation weights for each client in each communication round.
In particular, having collected local accuracies (or any other
utility metric of choice), the server creates a state vector st
that encodes performance measures for the current round:
st = [a1t , a2t , . . . , a tK ]

(11)

where akt is the accuracy of client k in round t, and K is the
number of clients.
The DQN agent receives this state vector and predicts a
set of Q-values for each client, which are the expected future
rewards (e.g., global accuracy improvement) when assigning
different aggregation weights:
Q(st , a) = E[Rt+1 + γ max Q(st+1 , a ′ ) | st , a]
a′

(12)

Here, Rt+1 is the immediate reward (global accuracy after
aggregation), γ is the discount factor, a is an action (choices
of weights of aggregation), and a ′ represents possible future
actions.
Based on the predicted Q-values, the server uses a softmax
function to transform these values to adaptive aggregation
weights for each client:
exp(Q(st , ak ))
wkt = P K
j=1 exp(Q(st , a j ))

(13)

where wkt is the weight assigned to client k in round t.
The global model is then updated as a weighted average of
local models:
t
θglobal
=

K
X

wkt · θkt

(14)

k=1

where θkt are the local model parameters from client k.
After aggregation, global model is evaluated by the server
on the validation set to compute the global accuracy which
is used as the reward signal for the DQN agent. The
experiences (state, action, reward, next state) are stored for
replay and the DQN agent is periodically updated so as
to enhance future aggregation policies. This cycle repeats
in each round, enabling the system to continually adapt
the importance given to each client based on observed
contributions to global performance. For clarity and reproducibility, we summarize the DQN aggregator design below:

2041

TABLE I
C LASS D ISTRIBUTION IN CICI OV2024 AND CICEVSE2024 DATASETS


K
State: st = atk , ltk , n kt , 1atk , 1ltk k=1 (per-client accuracy,
loss, normalized samples, and first-order deltas; size K × d).
Action/weights:
DQN outputs qt ∈ R K ; wt = softmax(qt )
P k
k
with
k wt = 1, wt ≥ 0 (optional clipping wmin =
0.02, wmax = 0.60). Reward: rt+1 = Acct+1 − Acct −
k ) − β∥w − u∥2 ; (abl.: r
λ Vark (at+1
t
t+1 = Acct+1 ). Network:
2
MLP (LayerNorm+ReLU, 128 → 64, output K ); target net,
replay; Huber loss; Adam (1 × 10−3 ); γ = 0.95; ε-greedy
ε : 0.30 → 0.05. Static global averaging utilizes fixed or
size-based weights, whereas global server in proposed strategy
uses a DQN (reinforcement-learning) approach to assign client
weights adaptively each round based on objective performance
feedback from held out assessments (such as accuracy or
loss).Updates that are strong and dependable are given greater
weight, whereas updates that are noisy or low-quality are given
less weight. This makes the global model more stable when
there are non-IID data, stragglers, and changes in distribution.
This data driven weighting keeps convergence stable and
speeds it up, lowers round-to-round fluctuations, and stops
any one client with a skewed or uneven data distribution from
dominating. In practice, this leads to better and more constant
global accuracy and quicker recovery when conditions change,
which is better than static global averaging. Algorithm 2
summarizes the procedural workflow described in this section.
Construct a state from client accuracies, the reinforcement
learning agent estimates Q-values, softmax-normalized into
aggregation weights to update global parameters. Evaluate the
global model, compute reward, perform experience replay, log
metrics, and output the final GMU.
IV. R ESULTS AND D ISCUSSIONS
A. Dataset Collection
This study employs two established datasets, CICIoV20241
[9] and CICEVSE20242 [10], to comprehensively assess the
proposed methodology. Table I shows the class distribution in
both datasets. The CICIoV2024 dataset serves as an extensive
benchmark for cybersecurity research in Internet of Vehicles
(IoV) environments. It features a wide spectrum of cyberattack
scenarios performed on a 2019 Ford vehicle, with all Electronic Control Units (ECUs) included. The dataset is organized
into several attack categories, including Denial-of-Service
1 https://www.unb.ca/cic/datasets/iov-dataset-2024.html
2 https://www.unb.ca/cic/datasets/evse-dataset-2024.html

2042

Fig. 4.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

Comparison of accuracy trends for various client counts and datasets: (a,b) CICEVSE2024 and (c,d) CICIOV2024.

(DoS), GAS, RPM, SPEED, and STEERING WHEEL, as well
as benign samples. Specifically, CICIoV2024 contains 8,055
benign instances with multiple attack classes including 8,378
DoS samples, 8,215 GAS attack samples, 8,068 RPM attacks,
9,041 SPEED attacks and 9,464 STEERING WHEEL attacks.
This gives a total of 51,221 data points. Each sample is given
in binary, decimal, and hexadecimal formats and can be analyzed in detail and with great perspective. The CICEVSE2024
dataset focuses on the electric vehicle charging infrastructure
and covers the benign and the attack scenarios. It reflects
the vulnerabilities of the electric vehicle chargers in idle
and active charging states, capturing various network and
host-based attacks such as reconnaissance, DoS, backdoor,
and cryptojacking. In terms of the class distribution, we have
CICEVSE2024 which consists of 14,364 benign samples and
100,935 attack samples, for a total of 115,299 records. Prior
to experimentation, both datasets go through rigorous pre
processing in order to select only the most relevant and noise
free features to be used for model development and evaluation.
The dataset was then divided, 80% being used for the training
and the remaining 20% being used for testing in the intrusion
detection experiments.
B. Performance Metrics
To have a thorough assessment of the proposed approach,
we accounted for multiple rounds and also varied the number
of clients. Precision, recall, F-measure, and accuracy were
used as the evaluation measures. The metrics were calculated
based on the number of True Positives (TP), False Positives
(FP), True Negatives (TN) and False Negatives (FN). The
resulting performance equations are given in Equations 15-18.
Pr ecision =

TP
(T P + F P)

(15)

FP
(F P + T N )
(2 ∗ T P)
F − measur e =
(2T P + F P + F N )
(T P + T N )
Accuracy =
(T P + T N + F P + F N )
Recall =

(16)
(17)
(18)

The proposed federated learning framework was created in
PyCharm using Keras and evaluated on a computing environment with an NVIDIA GeForce RTX 2060 (8 GB) and 32 GB
of RAM.
C. Performance Analysis and Comparisons
The dynamic accuracy curves in Fig. 4 clearly demonstrate
that the proposed strategy achieves rapid and stable accuracy improvements for both the global and client models in
5-client and 7-client scenarios using the CICEVSE2024
dataset. All models converge quickly and reach high accuracy
values, highlighting the overall effectiveness of the approach
for IoV intrusion detection. This pattern highlights the strong
learning capacity and stability imparted by the temporal hybrid
deep model, which leverages the complementary strengths of
TCN and LSTM with attention mechanisms to capture both
short-term and long-term dependencies in client data. The
close alignment of client curves and the global model further
indicates the balanced generalization across all participants
and efficient knowledge integration through federated aggregation. The smooth and consistently high accuracy of the global
model in both settings validates the adaptive reinforcement
learning-based aggregation, which dynamically weighs and
combines local updates from heterogeneous clients, thus minimizing divergence and ensuring robust global performance
even as the number of clients increases. Notably, as more
clients participate (in the 7-client case), the overall trend

NAEEM et al.: ADAPTIVE FEDERATED REINFORCEMENT LEARNING WITH TEMPORAL HYBRID DEEP MODEL

2043

TABLE II
P ERFORMANCE C OMPARISON FOR D IFFERENT N UMBERS OF C LIENTS U SING CICEVSE2024 DATASET

TABLE III
P ERFORMANCE C OMPARISON FOR D IFFERENT N UMBERS OF C LIENTS U SING CICIOV2024 DATASET

TABLE IV
G LOBAL M ODEL M AXIMUM AND M INIMUM ACCURACY (%) FOR D IFFERENT C LIENTS U SING CICIOV2024 AND CICEVSE2024 DATASETS

of accuracy remains high, confirming the scalability and
adaptability of the proposed methodology without sacrificing
convergence speed or stability. Table II indicates that the
proposed method achieves consistently high attack detection,
with F1-scores of 97.21%, 97.26%, and 97.11% for 3, 5, and
7 clients, respectively. For the benign class, F1-scores are
79.91%, 79.83%, and 78.76% on the same settings. The results
obtained show the good and robust intrusion detection performance of the framework, in particular for attack detection,
even when the number of clients grows.
The dynamic accuracy curves Fig. 4 show the effectiveness
of proposed strategy on CICIOV2024 dataset. For the 3-client
and 5-client models, it is shown that all client models and
the global model have very fast and stable convergence in
the accuracy, reaching values above 99% in a short time.
Comparing the curves of each client and the global model,
we can see that the temporal hybrid deep model has a good
ability to support resilient local training, and the adaptive
reinforcement learning aggregation plays an optimal role in
integrating client updates. This fact gives high and stable
accuracy even if the number of clients is increased that shows
the consistency and scalability of the approach. Table III
also supports this finding, showing perfect precision, recall,
and F1-scores across all attack families and for each client
configuration. For example, in the 3-client case, benign traffic
achieves a precision of 99.63%, recall of 99.69%, and F1-score
of 99.66%, while DOS, GAS, RPM, SPEED, and STEERING
WHEEL classes also report metrics above 99.8% in almost
all cases. Similarly, in the 5-client and 7-client settings,

the results remain consistently high across all classes, with
only minimal variations. These outstanding metrics confirm
that the proposed framework can effectively and accurately
detect both benign and attack classes across a diverse set of
intrusion types, demonstrating not only strong convergence
in training but also excellent generalization in distributed,
real-world IoV environments. Even though client-level IID
partitioning is applied, the benign class has a slightly smaller
F1 score. This is primarily due to dataset-level class priors
and feature similarity with low-intensity attacks, leading to
more benign misclassifications. Simple, non-intrusive fixes
like class-weighted loss, small benign oversampling in minibatches, or post-hoc threshold calibration using ROC/PR can
reduce this difference even smaller without changing the
originally proposed federated methodology.
The loss curves in Fig. 5 clearly show that both the client
and global model losses decrease rapidly and converge to low
values as training progresses. This rapid and stable reduction demonstrates the effectiveness of the Temporal Hybrid
Deep Model in extracting useful temporal features at each
client, allowing for efficient local training. At the same time,
the adaptive reinforcement learning aggregation consistently
aligns the global loss curve with those of the clients, ensuring optimal global convergence and minimizing divergence.
The close alignment between client and global loss curves
highlights the strong collaboration and robust optimization
achieved through this federated strategy. Table IV shows that
the global model achieves high maximum accuracies across
all client settings, with values ranging from 99.85% to 99.57%

2044

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

TABLE V
ROUND -W ISE G LOBAL M ODEL A DAPTIVE AGGREGATION P ERFORMANCE (CICIOV2024, 3 C LIENTS )

Fig. 5.

Comparison of loss curves for various client configurations and datasets: (a,b) CICEVSE2024 and (c,d) CICIOV2024.

for CICIOV2024 and 95.18% to 94.90% for CICEVSE2024,
while minimum accuracies remain above 93.17% and 87.07%,
respectively. These results reflect the strong and consistent
performance of the proposed framework in delivering reliable accuracy for intrusion detection, even as the number of
clients increases. These findings show an optimal precision for
curated datasets. However, we predict that accuracy will go
downward somewhat under noisier real-world IoV conditions.
This will be lessened by proposed DQN-driven aggregation,
which automatically reduces the impact of unreliable client
updates.
The results in Fig. 6, along with Table V and Table VI,
show that RL based adaptive aggregation enables the global
model to consistently match or exceed the accuracy of individual clients across rounds. This way, it guarantees speedy
and stable improvements in the global model metrics like
accuracy, precision, recall, and F1 score and it has shown
a high degree of synchronization and successful integration

of client knowledge. The obtained results demonstrate the
efficacy of the proposed scheme in providing high performance
and reliable intrusion detection in various federated IoV environments. Fig. 6 illustrates the result of client’s local model
accuracy change curve against the federated rounds, compared
to the global model accuracy. Fig. 6(a) shows results for the
CICIoV2024 dataset, and Fig. 6 (b) shows results for the
CICEVSE2024 dataset with five participating clients. In both
cases, the global model accuracy after the second round is very
close to the client models and converges in the later rounds,
demonstrating that the aggregation step is able to maintain
client knowledge while not reducing the overall performance.
Fig. 7 shows very high accuracy for intrusion detection by the
proposed framework with very few misclassifications in all
classes for the CICIOV2024 (3-clients) and CICEVSE2024
(5-clients) datasets. The true positive rate is high and the false
positive as well as false negative is low in each confusion
matrix, which indicates that the system is reliable and robust in

NAEEM et al.: ADAPTIVE FEDERATED REINFORCEMENT LEARNING WITH TEMPORAL HYBRID DEEP MODEL

Fig. 6.

Accuracy comparison of clients and aggregated global model per round for (a) CICIOV2024 and (b) CICEVSE2024 datasets.

Fig. 7.

Confusion matrix for intrusion detection using (a) CICIOV2024 dataset with 3-clients and (b) CICEVSE2024 dataset with 5-clients.

2045

TABLE VI
ROUND -W ISE G LOBAL M ODEL A DAPTIVE AGGREGATION P ERFORMANCE (CICEVSE2024, 5 C LIENTS )

both multi class and binary cases, and most of the predictions
are along the diagonal of the confusion matrices, respectively.
Fig. 8 and Fig. 9 clearly show that the IID data distribution
scheme leads to higher and more stable accuracy for both
the global model and individual clients compared to the
non-IID setting. In Fig. 8, the IID curve rises sharply and
converges smoothly to a higher accuracy, while the non-IID
curve remains flatter with noticeable fluctuations and slower

improvement across rounds. Table VIII show that the IID data
distribution scheme leads to higher and more stable accuracy
for both the global model and individual clients compared
to the non-IID setting in and Table VII. When averaged
over 15 rounds, IID increases accuracy by 3.84 percentage
points, ROC–AUC by 22.89 percentage points, precision by
5.52 percentage points, and F1-score by 1.93 percentage
points. Recall stays extremely high in both settings. IID also

2046

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

TABLE VII
C LASSIFICATION P ERFORMANCE W ITHOUT IID BASED DATA D ISTRIBUTION S CHEME (CICEVSE2024, 5 C LIENTS )

TABLE VIII
C LASSIFICATION P ERFORMANCE W ITH IID BASED DATA D ISTRIBUTION S CHEME (CICEVSE2024, 5 C LIENTS )

TABLE IX
C OMPARISON OF AGGREGATION M ETHODS FOR C LASSIFICATION P ERFORMANCE (CICEVSE2024, 5 C LIENTS )

Fig. 8. Global model accuracy comparison: IID VS Non-IID data distribution
scheme (CICEVSE2024 dataset,5-clients).

converges more smoothly with less round to round fluctuation,
which shows that balanced partitions lead to more stable

and discriminative federated learning performance. The bar
graphs in Fig. 9 show that IID partitions provide increasingly greater and higher accuracies throughout rounds for all
five clients. Non-IID partitions provide lower accuracies that
exhibit more variability across clients and often achieve a
plateau earlier. This ongoing gap between IID and Non-IID
shows how data heterogeneity affects the stability of learning.
Non-IID settings still have more round-to-round variation,
even with Reinforcement-based aggregate. Adaptive weighting
is helpful, but it doesn’t completely make up for uneven client
distributions. When IID settings are used, clients are more
closely aligned, which means that generalization is stronger
and more balanced. In general, balanced data allocation (with
adaptive aggregation) speeds up convergence and enhances
end-of-round performance in a Federated learning intrusion
detection system. Fig. 10 and Table IX collectively show

NAEEM et al.: ADAPTIVE FEDERATED REINFORCEMENT LEARNING WITH TEMPORAL HYBRID DEEP MODEL

Fig. 9.

2047

Client wise accuracy comparison: IID VS Non-IID data distribution scheme (CICEVSE2024 dataset).

detection. Third, the design is ready for edge use with consumer IoV devices such as telematics and electric vehicle
chargers.
V. C ONCLUSION

Fig. 10. Global model accuracy comparison for various aggregation methods
(CICEVSE2024, 5- clients).
TABLE X
P ERFORMANCE C OMPARISON OF THE P ROPOSED M ODEL W ITH
E XISTING T ECHNIQUES

that RL-based adaptive aggregation consistently outperforms
both FedAvg and FedProx across all classification metrics
using the CICEVSE2024 dataset with 5 clients. The RL-based
method achieves the highest accuracy (93.23%), F1-score
(96.25%), and strong precision and recall, while also delivering steady improvements throughout the rounds as seen in the
figure. This demonstrates that reinforcement learning-based
aggregation enables more effective and stable global model
learning in federated environments compared to conventional
aggregation approaches. To assess the effectiveness of the
proposed scheme, its performance was benchmarked against
established approaches, namely FED-IDS [25], DL-IDS [26],
and DL-LeeNET [27]. Experimental results on vehicle-based
IDS datasets demonstrate that the proposed model outperforms
these existing methods. According to Table X, the proposed
model achieves higher accuracy. Our approach has three clear
benefits over current federated learning based IDS solutions.
First, an adaptive aggregator based on DQN learns client
weights for each round from performance feedback. The result
renders the system more speed up when clients are not IID
and stable convergence. Second, a temporal hybrid encoder
(CNN–LSTM–Attention) models both short and long range
dependencies in CAN and EVSE traffic for better intrusion

This paper presented an adaptive federated learning framework to address the security challenges faced by consumer
electronics in Internet of Vehicles (IoV) environments, particularly targeting the limitations of traditional FL-based
intrusion detection approaches with non-IID data and static
aggregation methods like FedAvg and FedProx. By standardizing and distributing IoV network data IID-wise among
clients, our method ensures consistent and privacy-preserving
model training. Each client employs a Temporal Hybrid Deep
Model (CNN-LSTM-Attention) initialized from the global
model, enhancing the extraction of complex temporal and
spatial patterns. A Deep Q-Network (DQN)-based Reinforcement Learning (RL) agent at the server dynamically
determines aggregation weights based on client Q-values,
adaptively optimizing the global model. Extensive experiments
on CICIOV2024 and CICEVSE2024 dataset demonstrate significant gains, and the detection accuracy are 99.85% and
95.18%, respectively. The results show the robustness and
flexibility of the proposed framework for IoV security in the
real world. The research does not examine privacy primitives.
Future work will explore how to handle clients who only
participate a few times, which will make deployments even
more reliable in the real world. It will also empower secure
aggregation, differential privacy, and adversarial-robust training to make it more robust in real world deployments.
R EFERENCES
[1] L.-L. Wang, J.-S. Gui, X.-H. Deng, F. Zeng, and Z.-F. Kuang, “Routing
algorithm based on vehicle position analysis for Internet of Vehicles,”
IEEE Internet Things J., vol. 7, no. 12, pp. 11701–11712, Dec. 2020.
[2] P. Gope and B. Sikdar, “An efficient privacy-preserving authentication
scheme for energy internet-based vehicle-to-grid communication,” IEEE
Trans. Smart Grid, vol. 10, no. 6, pp. 6607–6618, Nov. 2019.
[3] U. Z. A. Hamid, H. Zamzuri, and D. K. Limbu, “Internet of vehicle
(IoV) applications in expediting the implementation of smart highway
of autonomous vehicle: A survey,” in Performability Internet Things.
Cham, Switzerland: Springer, 2018, pp. 137–157.
[4] N. Hussain, P. Rani, N. Kumar, and M. G. Chaudhary, “A deep
comprehensive research architecture, characteristics, challenges, issues,
and benefits of routing protocol for vehicular ad-hoc networks,” Int. J.
Distrib. Syst. Technol., vol. 13, no. 8, pp. 1–23, Sep. 2022.
[5] N. Hassan, K.-L.-A. Yau, and C. Wu, “Edge computing in 5G: A review,”
IEEE Access, vol. 7, pp. 127276–127289, 2019.
[6] I. A. Alablani and M. A. Arafah, “Enhancing 5G small cell selection:
A neural network and IoV-based approach,” Sensors, vol. 21, no. 19,
p. 6361, Sep. 2021.

2048

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

[7] Y. Zhao, M. Li, L. Lai, N. Suda, D. Civin, and V. Chandra, “Federated
learning with non-IID data,” 2018, arXiv:1806.00582.
[8] L. Tian, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and
V. Smith, “Federated optimization in heterogeneous networks,” in Proc.
Mach. Learn. Syst., 2018, pp. 429–450.
[9] E. C. P. Neto et al., “CICIoV2024: Advancing realistic IDS approaches
against DoS and spoofing attack in IoV CAN bus,” in Proc. Int. Conf.
Cyber Secur., vol. 26, 2024, Paper 101209.
[10] E. D. Buedi, A. A. Ghorbani, S. Dadkhah, and R. L. Ferreira, “Enhancing ev charging station security using a multi-dimensional dataset:
CICEVSE2024,” in Proc. Int. Conf. Smart Grid Electr. Vehicles, 2024,
pp. 171–190.
[11] B. Bhola et al., “Quality-enabled decentralized dynamic IoT platform
with scalable resources integration,” IET Commun., vol. 19, no. 1,
pp. 2111–2121, Jan. 2025.
[12] A. H. Mohd Aman, E. Yadegaridehkordi, Z. S. Attarbashi, R. Hassan,
and Y.-J. Park, “A survey on trend and classification of Internet of Things
reviews,” IEEE Access, vol. 8, pp. 111763–111782, 2020.
[13] M. R. Mahmood, M. A. Matin, P. Sarigiannidis, and S. K. Goudos,
“A comprehensive review on artificial intelligence/machine learning
algorithms for empowering the future IoT toward 6G era,” IEEE Access,
vol. 10, pp. 87535–87562, 2022.
[14] J. H. Kim, “6G and Internet of Things: A survey,” J. Manage. Analytics,
vol. 8, no. 2, pp. 316–332, Apr. 2021.
[15] K. Peng, M. Li, H. Huang, C. Wang, S. Wan, and K.-K.-R. Choo,
“Security challenges and opportunities for smart contracts in Internet of Things: A survey,” IEEE Internet Things J., vol. 8, no. 15,
pp. 12004–12020, Aug. 2021.
[16] S. K. Lo, Q. Lu, C. Wang, H.-Y. Paik, and L. Zhu, “A systematic
literature review on federated machine learning: From a software engineering perspective,” ACM Comput. Surveys, vol. 54, no. 5, pp. 1–39,
Jun. 2022.
[17] B. Hu, Y. Gao, L. Liu, and H. Ma, “Federated region-learning: An edge
computing based framework for urban environment sensing,” in Proc.
IEEE Global Commun. Conf. (GLOBECOM), Dec. 2018, pp. 1–7.

[18] C. Regan, M. Nasajpour, R. M. Parizi, S. Pouriyeh, A. Dehghantanha,
and K.-K.-R. Choo, “Federated IoT attack detection using decentralized
edge data,” Mach. Learn. Appl., vol. 8, Jun. 2022, Art. no. 100263.
[19] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. Y. Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. 20th Int. Conf. Artif. Intell. Statist., vol. 54, 2017,
pp. 1273–1282.
[20] S. Jamil, M. Rahman, and Fawad, “A comprehensive survey of digital
twins and federated learning for industrial Internet of Things (IIoT),
Internet of Vehicles (IoV) and Internet of Drones (IoD),” Appl. Syst.
Innov., vol. 5, no. 3, p. 56, Jun. 2022.
[21] Y. M. Saputra, D. N. Nguyen, D. T. Hoang, T. X. Vu, E. Dutkiewicz, and
S. Chatzinotas, “Federated learning meets contract theory: Economicefficiency framework for electric vehicle networks,” IEEE Trans. Mobile
Comput., vol. 21, no. 8, pp. 2803–2817, Aug. 2022.
[22] X. Huang, P. Li, R. Yu, Y. Wu, K. Xie, and S. Xie, “FedParking: A
federated learning based parking space estimation with parked vehicle
assisted edge computing,” IEEE Trans. Veh. Technol., vol. 70, no. 9,
pp. 9355–9368, Sep. 2021.
[23] Q. Wu, S. Wang, P. Fan, and P. Fan, “Deep reinforcement learning
based vehicle selection for asynchronous federated learning enabled
vehicular edge computing,” in Proc. Int. Congr. Commun., 2023,
pp. 3–26.
[24] A. Boualouache, B. Brik, S.-M. Senouci, and T. Engel, “On-demand
security framework for 5GB vehicular networks,” IEEE Internet Things
Mag., vol. 6, no. 2, pp. 26–31, Jun. 2023.
[25] P. Rani et al., “Federated learning-based misbehavior detection for
the 5G-enabled Internet of Vehicles,” IEEE Trans. Consum. Electron.,
vol. 70, no. 2, pp. 4656–4664, May 2024.
[26] D. Javeed, T. Gao, P. Kumar, and A. Jolfaei, “An explainable and resilient
intrusion detection system for industry 5.0,” IEEE Trans. Consum.
Electron., vol. 70, no. 1, pp. 1342–1350, Feb. 2024.
[27] P. Suman et al., “An improved deep learning-based intrusion detection
for reliable communication in VANET,” IEEE Trans. Consum. Electron.,
vol. 71, no. 1, pp. 209–217, Feb. 2025.
PAPER_TEXT
