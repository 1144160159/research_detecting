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
# [148] Privacy-Preserving Asynchronous Federated Learning Framework in Distributed IoT
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
编号：148
题名：Privacy-Preserving Asynchronous Federated Learning Framework in Distributed IoT
年份：2023
DOI：10.1109/jiot.2023.3262546
来源：IEEE Internet of Things Journal
PDF：paper/10.1109_jiot.2023.3262546.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：IoT、车联网、工业互联网与边缘安全
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\148.txt
- 原始字符数：55276
- 本次发送字符数：55276
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 15, 1 AUGUST 2023

13281

Privacy-Preserving Asynchronous Federated
Learning Framework in Distributed IoT
Xinru Yan , Yinbin Miao , Member, IEEE, Xinghua Li ,
Kim-Kwang Raymond Choo , Senior Member, IEEE,
Xiangdong Meng, and Robert H. Deng , Fellow, IEEE

Abstract—To solve the data island issue in the distributed
Internet of Things (IoT) without privacy leakage, privacypreserving federated learning (PPFL) has been extensively
explored in both academic and industrial fields. However, existing PPFL solutions still suffer from a single point of failure
and incur untrusted aggregation results caused by a malicious
central server, and even cause a loss of model accuracy in
an asynchronous setting. To solve these issues, we propose a
privacy-preserving asynchronous federated learning scheme by
using blockchain. Specifically, we use blockchain to address single
points of failure and untrustworthy aggregation results, implement reliable model aggregation utilizing a practical byzantine
fault-tolerant protocol in an asynchronous setting, and leverage differential privacy to improve system robustness. Formal
security analysis and convergence analysis demonstrate that the
proposed scheme is secure and robust, and extensive experiments
demonstrate that our scheme can effectively ensure the accuracy
of the system when compared with state-of-the-art schemes.
Index Terms—Asynchronous training, blockchain, differential
privacy (DP), federated learning (FL).
Manuscript received 24 November 2022; revised 24 February 2023;
accepted 24 March 2023. Date of publication 28 March 2023; date of current
version 25 July 2023. This work was supported in part by the National Natural
Science Foundation of China under Grant 62072361; in part by the Key
Research and Development Program of Shaanxi under Grant 2022GY-019; in
part by the Shaanxi Fundamental Science Research Project for Mathematics
and Physics under Grant 22JSY019; in part by the National Natural Science
Foundation of China under Grant 62125205; in part by the Fellowship pf
China Postdoctoral Science Foundation under Grant 2022T150507; in part
by the Opening Project of Intelligent Policing Key Laboratory of Sichuan
Province under Grant ZNJW2023KFMS002; and in part by the Henan Key
Laboratory of Network Cryptography Technology & State Key Laboratory of
Mathematical Engineering and Advanced Computing under Grant LNCT2020A06. The work of Kim-Kwang Raymond Choo was supported by the Cloud
Technology Endowed Professorship. (Corresponding author: Yinbin Miao.)
Xinru Yan and Yinbin Miao are with the School of Cyber Engineering,
Xidian University, Xi’an 710071, China, also with the Henan Key Laboratory
of Network Cryptography Technology, Zhengzhou 450001, China, and
also with the State Key Laboratory of Mathematical Engineering and
Advanced Computing, Zhengzhou 450001, China (e-mail: yanxinru25@
163.com; ybmiao@xidian.edu.cn).
Xinghua Li is with the State Key Laboratory of Integrated Service
Networks, School of Cyber Engineering, Xidian University, Xi’an 710071,
China, and also with the Engineering Research Center of Big Data
Security, Ministry of Education, Xi’an 710071, China (e-mail: xhli1@
mail.xidian.edu.cn).
Kim-Kwang Raymond Choo is with the Department of Information Systems
and Cyber Security, The University of Texas at San Antonio, San Antonio,
TX 78249 USA (e-mail: raymond.choo@fulbrightmail.org).
Xiangdong Meng is with the Henan Key Laboratory of Network
Cryptography Technology, Zhengzhou 450001, China, and also with the State
Key Laboratory of Mathematical Engineering and Advanced Computing,
Zhengzhou 450001, China (e-mail: xiangdong129@163.com).
Robert H. Deng is with the School of Information Systems, Singapore
Management University, Singapore 178902 (e-mail: robertdeng@smu.edu.sg).
Digital Object Identifier 10.1109/JIOT.2023.3262546

I. I NTRODUCTION
N THE distributed Internet of Things (IoT) environment,
a large amount of data is generated. In order to mine the
value of data, machine learning (ML) has been widely studied. Since a single IoT device has poor ML performance
due to insufficient local data, federated learning (FL) is
proposed to solve data islands and achieve efficient resource
utilization. However, even though FL does not directly leak
local data to the cloud server, the parameters are still subject to inference attacks. Therefore, privacy-preserving FL
(PPFL) [1] has been extensively explored in IoT. However,
existing PPFL solutions still face many issues in real-world
applications.
The first issue is that traditional PPFL solutions still suffer from a single point of failure or untrusted aggregation [2]
caused by a malicious central server. Specifically, once the
central server is attacked, it may cause the system to go down
and fail to operate normally. Even an attacker compromising
the central server can falsify the data, ultimately resulting in
untrusted aggregation results. The multiserver framework can
be deployed in the system to address a single point of failure, but it cannot guarantee that the aggregation results are
credible. Although various techniques are available to solve
the verification problem, such as zero-knowledge proofs [3],
signatures [4], and aggregate accumulators [5], these methods will incur high computation overheads on resource-limited
clients. Now an available solution is to use blockchain [6],
which can solve both issues with one stone. However, the traditional public network still leads to privacy leakage due to
the involvement of nonclient, and even causes fault tolerance
in asynchronous PPFL due to the use of consensus protocols,
such as proof-of-work [7] and proof-of-stake [8]. To overcome the shortcoming of the public blockchain, the consortium
blockchain composed of a small number of nodes can be
deployed in PPFL without the involvement of untrusted nodes.
Unfortunately, there are no asynchronous PPFLs implemented
in the consortium blockchain network.
The second issue is how to achieve the proposed asynchronous PPFL. In a typical PPFL framework, multiple clients
may suffer failures due to different computing powers [9].
The synchronous PPFL architecture needs to wait for delayed
clients to achieve better seek results, otherwise, it will lead
to a loss of model accuracy. For example, when some enterprises’ devices are offline, it can be costly to spend a
lot of time and computing power waiting for the devices

I

c 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
2327-4662 
See https://www.ieee.org/publications/rights/index.html for more information.
Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

13282

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 15, 1 AUGUST 2023

online. Timestamp-based FL schemes [10] can be exploited
to address the asynchronous problem, but cannot provide privacy protection. Existing asynchronous PPFL schemes use
secure multiparty computation (SMC) [11] or homomorphic
encryption (HE) [12] mechanisms to protect privacy but incur
high communication costs and computation costs, respectively.
Thus, how to achieve an efficient asynchronous PPFL is still
the problem we want to solve.
As mentioned above, we propose a privacy-preserving asynchronous FL framework in distributed IoT. Specifically, we use
the blockchain to avoid single points of failure and guarantee
the correctness of aggregation results. Furthermore, we use
the practical Byzantine fault tolerant (PBFT) protocol [13] to
guarantee the accuracy and reliability of asynchronous aggregation. Considering the lightweight blockchain architecture,
we use differential privacy (DP) [14] to protect the local
model and achieve efficient asynchronous aggregation. The
main contributions of our work are as follows.
1) We propose a centerless DP-based PPFL with
blockchain architecture. Specifically, we use the
blockchain to prevent aggregators from malicious modifications or attempting to infer private information of
clients during aggregation and utilize DP to prevent
privacy breaches due to curious attempts.
2) We use asynchronous mechanisms to prevent system heterogeneity. The asynchronous training is accomplished
by using PBFT to improve the trust in the system itself
and the feasibility of practical applications.
3) Formal security analysis and convergence analysis prove
that our scheme is secure and robust, and extensive
experiments demonstrate that our scheme can effectively
ensure the accuracy of the system when compared with
state-of-the-art schemes.
The remainder of this article is organized as follows.
Sections II and III describe the related work and techniques,
respectively. In Section IV, we outline the system model,
problem definition, threat model, and design goals of our
scheme. Section V describes the details of our schemes. Then,
we analyze the security and performance of the scheme in
Sections VI and VII, respectively. Finally, we conclude this
article and give a brief overview of future work.
II. R ELATED W ORK
McMahan et al. [15] proposed the classical synchronized
Federated Averaging algorithms (FedAvg), which not only
uses synchronization to schedule clients but also utilizes
weighted averaging to update client gradients to form a
global model. However, even if an FL does not directly
leak local data to cloud servers, parameters are still subject to inference attacks. Therefore, researches on PPFL
are very necessary. Fang and Qian [16] proposed a multiparty privacy-preserving ML framework, which uses HE
encrypted gradients to protect the security of private data
and uses a packing method to reduce transpose and rotation
operations in matrix-vector multiplication. Furthermore, SMC
techniques enable privacy-preserving model aggregation for an
FL but incur high communication overhead and low scalability. To solve this problem, Kanagavelu et al. [17] developed

a two-stage mechanism, first electing a small committee and
then providing model aggregation services for more participants through the committee. As each client’s performance
varies, the client may not complete local updates in time or
even experience downtime, which eventually leads to delays.
To eliminate the defect of the synchronous algorithm and
prevent some situations of unpredictable clients, asynchronous
training [18] has been extensively explored. For example,
Zhou et al. [19] proposed a time-triggered FL algorithm
over wireless networks, which uses the greedy search algorithm to solve the problem of user selection and bandwidth
optimization. Two PPFL schemes, DeepPAR and DeepDPA,
were proposed by Zhang et al. [20]. DeepPAR inherently preserves the secrecy of dynamic updates while protecting the
input privacy of each participant. Meanwhile, DeepDPA can
guarantee the backward secrecy of group participants in a
lightweight manner. These schemes are all implemented under
the centralized architecture. However, the stability of traditional centralized PPFL schemes cannot be guaranteed due to
factors, such as the low-reliability [21] or biases [22] of the
cloud service providers, which makes the servers vulnerable
to poisoning attacks [23].
To solve the above problems, endowing an FL with a
blockchain can ensure distributed data sharing without revealing privacy [24], and effectively optimize the security of PPFL.
Lu et al. [25] designed a blockchain-authorized secure datasharing PPFL structure, which reduces the risk of data leakage
and protects privacy through distributed multiparty contribution data. Awan et al. [26] proposed a blockchain-based PPFL
framework, which utilizes HE to perform gradient aggregation
on private data to protect the model. Li et al. [1] designed
a PPFL framework by using SMC, single-mask mechanism,
and chained-communication mechanism to achieve practical
privacy protection with low communication cost and without
affecting the accuracy and convergence speed of the training
model. To solve the synchronous problem, Liu et al. [27],
respectively, proposed advanced FedBlock and FedAC models of distributed and an asynchronous FL frameworks to
improve the robustness of the system. However, these schemes
do not address the privacy issues of Blockchain-enabled FL.
Lu et al. [28] proposed a hybrid blockchain architecture, which
uses deep reinforcement learning for node selection and an
asynchronous FL to improve the security and reliability of
model parameters. Feng et al. [29] used a novel entropy weight
approach to evaluate the participation level and proportion
of local models trained in devices scheme. The energy consumption and local model update efficiency are balanced by
adjusting the local training and communication delays, and
optimizing the block generation rate.
However, the above solutions cannot ensure the accuracy
and security of asynchronous PPFL in consortium blockchain.
Therefore, we propose a privacy-preserving asynchronous FL
framework in distributed IoT. The comparison of our scheme
with the above schemes is shown in Table I.
III. P RELIMINARIES
In this section, we describe the related technologies involved
in our scheme, including an FL, a blockchain, and a DP.

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

YAN et al.: PRIVACY-PRESERVING ASYNCHRONOUS FEDERATED LEARNING FRAMEWORK

TABLE I
C OMPARATIVE S UMMARY B ETWEEN O UR
S CHEMES AND P REVIOUS S CHEMES

13283

difficulty of mining and is calculated by
Target = Target ×

ta
te

(3)

where ta is the actual time consumed to mine 2016 mines
and te is the theoretical time consumed. Nonce is the random value to ensure that the hash value Hi of Bi ’s block
head matches Target by changing the Nonce value (Hi ≤
Target). Previous_block_hash stores the hash Hi−1 of the
previous block head. Merkle_root_hash represents the transaction messages with the use of tree structure. The tree leaf
nodes store the transactions Tx = {Tx0 , Tx1 , Tx2 , Tx3 }. It is
worth noticing that Txj is the transaction with the serial number j, and is hashed to get Hj . After that, the neighboring
nodes are hashed in turn until the root node H0123 is generated
(H0123 = Hash(H01 + H23 )).
C. Differential Privacy
DP [14] allows analysts to learn aggregate information about
the data without access to the original private user data.
Definition 1 [(ε, δ)−DP [30]]: For two adjacent data sets
D1 and D2 that differ by only one record, given a randomized
algorithm K, the output result is R ⊆ R. If K and R satisfy
the following:
Pr[K(D1 ) ∈ R] ≤ exp(ε)Pr[K(D2 ) ∈ R] + δ

Fig. 1.

Blockchain structure.

A. Federated Learning
Let C = {C1 , C2 , . . . , Cn } be n clients and D =
{D1 , D2 , . . . , Dn } be corresponding data sets, the overall goal
of FL is to obtain an optimal global model w∗ . Given the
global model wt of the tth epoch, the client Ci (i ∈ [1, n])
updates its local model wiτ by
wiτ = wt − λ ∗ ∇l(wt ; Di )

(1)

where τ is the timestamp of Ci , λ is the learning rate, and
∇l(wt ; Di ) is the loss function of the training model. After
that, Ci uploads wiτ to the central server. Then, the central
server receives the local models {w1τ , w2τ , . . . , wnτ } returned by
C, and aggregates them to update the global model wt+1 with
a weighted average algorithm defined by
1 i
wτ .
n
n

wt+1 =

(2)

i=1

B. Blockchain
Blockchain is a distributed shared ledger that stores all
transactions in the network [6]. Fig. 1 shows the blockchain
structure. For a block Bi with index i, Timestamp records the
generation time of Bi . Target is negatively correlated with the

(4)

the algorithm is said to conform to (ε, δ) − DP, where δ is the
relaxation term and ε is the privacy budget.
Definition 2 (Laplace Mechanism [31]): Given data set D
and query function f (x), f (x) is the sensitivity of f (x), the
random algorithm K needs to satisfy


f (x)
(5)
K(D) = f (D) + Y, Y ∼ Lap 0,
ε
where ε is the privacy budget and Y is the randomly generated
Laplacian noise.
IV. P ROBLEM F ORMULATION
In this section, we introduce the system model, problem
definition, threat model, and design goals of our scheme.
A. System Model
We consider the consortium blockchain scenario. The
system model of our scheme consists of three entities, namely,
clients, blockchain, and primary node. The role of each entity
is shown as follows.
1) Clients: Clients in the consortium blockchain need to
both complete local model updates and participate in
PBFT consensus to complete global model aggregation.
2) Blockchain: Blockchain uses an asynchronous mechanism to invoke the local model uploaded by clients to
complete the aggregation.
3) Primary Node: The primary node acted by a client needs
to trigger a new epoch of aggregation task at regular
intervals with a timestamp and sends this aggregation
result to all clients.

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

13284

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 15, 1 AUGUST 2023

C. Threat Model

Fig. 2. System model of our basic scheme (In the tth epoch, Ci is the
primary node and Cn drops out, at which point the red model of Cn stored
in the blockchain is the expired model wnτ , where τ is the timestamp of Cn
and τ ≤ t).

Our scheme is executed in the following steps. In the tth
epoch global iteration, the primary node Ci (i ∈ [1, n]) sends
the global model wt to all clients C = {C1 , C2 , . . . , Cn }
(step ①). The online client Cj (j = {1, 2, . . . , n}\{i}) uses
wt to update the local model and adds noise to it in the
j
t epoch of communication, resulting in wτ , where τ is
j
the timestamp of Cj (step ②). Cj upload parameter wτ to
the blockchain. Note that the red Cn in Fig. 2 is offline
(step ③). Ci initiates the (t + 1)th epoch aggregation request
to the blockchain network (step ④). In the aggregation, the
expired models of the delayed clients (the red model pattern
in Fig. 2) are aggregated with the (t + 1)th local models uploaded of the online clients to get the aggregation
result wt+1 (step ⑤). Nodes in the network feed back wt+1 to
Ci (step ⑥).

In this article, the client is considered to be “honest but
curious” [32]. Under this assumption, the client will honestly perform local model updating and upload the right result
to the blockchain but may be curious about other clients’
high-quality data, thereby posing a threat to the security
of the data. In this article, the blockchain network in this
article is considered to be fully trustworthy, which means
that all clients recognize the results of global model aggregation performed in the blockchain network. The potential
threats caused by clients and the central server are shown
as follows.
1) Leakage of Data Privacy: Each client honestly runs
the agreed protocol but is curious about the sensitive information contained by other clients. Therefore,
the client may try to infer other clients’ private data,
resulting in data leakage.
2) Single Point of Failure: Most of the existing FL schemes
rely on the central server for aggregation. However, if
the server is maliciously attacked, the aggregation result
of the final training is prone to error, resulting in the
failure of the FL training.
3) Reduction of Model Accuracy: In the actual deployment
of an FL, the clients cannot timely feedback or even
forced to appear offline phenomenon, as devices on each
client have certain differences in computing, communication, and storage hardware and software. Whether
waiting for the offline clients to go online or aggregating the online clients’ model will cause the loss of model
accuracy.
D. Design Goals

B. Problem Definition
The traditional PPFL undergoes a total of T epochs of
updates, with n clients and a central server trained collaboratively. The overall goal is to form an optimal global model
w∗ . For the tth global iteration, the client set C uploads the
local model set {w1τ , w2τ , . . . , wnτ }, where τ is the timestamp
of C. Then, the central server aggregates these local models
to update wt+1 . If the central server goes down, the aggregation stops. Even if the central server is compromised by
an attacker, resulting in some models wt being tampered with
(wt = wt ) and eventually causing the aggregation result w∗ to
be untrusted.
In the case of synchronous training of multiple data sources,
if m clients (m < n) are dropped due to network instability or poor computing powers (as shown in Fig. 2 with red
Cn ), only n − m clients can communicate with the aggregator. We let N be the set of online clients, J be the
set of uploaded local models of N , and Q be the set of
delayed clients. In this case, if the aggregator has to wait for
Q to get online and then update wt+1 , it will incur higher
latency and communication overhead. Conversely, if we give
up waiting for Q and only aggregate J , then, the accuracy of
wt+1 accuracy will be drastically reduced, which leads to the
incorrect w∗ .

By analyzing the above threat model and system model and
combining the problems existing in the current research, we
need to achieve the following functions and objectives.
1) Privacy Protection: Our scheme should implement DP,
and add Laplacian noise to the updated local model to
disturb the training parameters and ensure that the data
privacy is not leaked.
2) Asynchronous Training: Our scheme should implement
the asynchronous setting, trying to improve the training
efficiency and prevent the waste of resources caused by
system heterogeneity.
3) Decentralized Architecture: Our scheme should implement blockchain to build a decentralized FL system to
prevent malicious cloud servers, thereby improving the
security of training and ensuring the credibility of the
system.
4) Model Accuracy: Our scheme should ensure model
reliability, the obtained well-trained model is correctly
aggregated from multiple local training models and not
tampered with.
V. D ESIGN OF O UR S CHEME
In this section, we describe how our scheme works. First, we
give the technical overview of the scheme and then elaborate

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

YAN et al.: PRIVACY-PRESERVING ASYNCHRONOUS FEDERATED LEARNING FRAMEWORK

TABLE II
N OTATIONS AND D ESCRIPTIONS

on the implementation. In addition, Table II gives the notation
definitions in this article.

Algorithm 1: Privacy-Preserving Asynchronous FL
Framework in Distributed IoT
Input: n, w0 , T, L, C, N , Q, J , Time.
Output: w∗ .
1 Ci initialize w0 ;
2 for each t ∈ [0, T] do
3
N ← ∅, Q ← ∅, J ← ∅;
4
Scheduler:
5
Ci downloads (wt , t) from Blockchain;
6
Ci sends (wt , t) to C;
7
while time ≤ Time do
8
for Cj ∈ C in parallel do
9
Local training in Algorithm 2:
j
10
(wτ , τ ) ← LocalUpdate (wt , t, L);
j
11
Cj sends (wτ , τ ) to the blockchain;
12
Add Cj to online clients set N ;
j
13
Add wτ to normal local model set J ;
14
15

A. Technical Overview
Traditional PPFL solutions suffer from a single point
of failure and untrusted aggregation caused by malicious
central servers. Li et al. [1] and Awan et al. [26],
can address the above issues, but they incur high communication overheads and cannot solve the asynchronous
problem.
We use the consortium blockchain to complete the global
model updates, in which n nodes participate in the training
as clients C = {C1 , C2 , . . . , Cn }. The solution can tolerate up
to f byzantine nodes that do not complete aggregation tasks
properly (f = [(n − 1)3]), but we need to guarantee that the
size of Q is less than f (|Q| ≤ f ). To avoid the dropout
issue, we use the PBFT protocol to complete the aggregation. Specifically, the primary node Ci (i ∈ [1, n]) initiates the
(t + 1)th aggregation request mt+1 with the timestamp action.
After that, Ci computes and broadcasts the pre-prepare mesPp
sage mt+1,i to the whole network. Then, each online node
Pp
Cj ∈ N (j = i) receives and processes mt+1,i , and then
broadcasts the prepare message mPt+1,j to the blockchain
network. Cj needs to ensure that it receives at least 2f + 1
legitimate messages {mPt+1,1 , mPt+1,2 , . . . , mPt+1,2f +1 }, and then
packages these messages before sending commit message
mC
t+1,j . Meanwhile, Cj starts to calculate mt+1 using an
asynchronous mechanism after receiving at least 2f + 1 legitC
C
imate messages {mC
t+1,1 , mt+1,2 , . . . , mt+1,2f +1 }. Specifically,
for the expiration model of the delayed client Ck (Ck ∈
Q) stored in the blockchain, its tth epoch weight value
βtk can be determined by the function S(·). After that, Cj
sends a reply message mRt+1,j to Ci . Ci receives f + 1
consistent messages {mRt+1,1 , mRt+1,2 , . . . , mRt+1,f +1 } to successfully obtain wt+1 . To eliminate the huge overhead in the
network, DP makes it possible to protect the privacy security of lightweight blockchains. In the local training phase,
N updates the set of local models J and uses the DP technology to add noise Y to it before uploading J . Therefore, we
propose a privacy-preserving asynchronous FL framework in
distributed IoT.

13285

16
17
18
19
20
21

if |J | == n then
break;
Q ← C − N;
Model aggregation in Algorithm 3:
(wt+1 , t + 1) ← Aggregation (J , N , Q, β, wt , t);
t ← t + 1;
w∗ ← wt ;
return w∗ .

B. Privacy-Preserving Asynchronous Federated Learning
Framework in Distributed IoT
Based on the description of the program process, we
divide the workflow of our scheme into three parts:
1) scheduler; 2) local training; and 3) model aggregation.
The scheduler and model aggregation are performed asynchronously, which means that the threads on both sides are
nonblocking. It is worth noticing that this method is very
beneficial to the case of heterogeneous devices in practical applications. The algorithm of our scheme is shown in
Algorithm 1. Initially, the primary node Ci in the blockchain
initializes a global model w0 and then obtains an optimized
global model w∗ after completing T epochs of aggregations.
Scheduler: The primary node Ci triggers the training task
at regular intervals. Ci first fetches the tth epoch global model
wt from the blockchain, and then sends (wt , t) to the client
set C and starts the timing. When the time reaches Time, the
model aggregation is still forced to start even if the set Q is
not all online yet. Of course, if C is all completed with local
model updates, then, the model aggregation starts (line 18).
The Time value is related to the timestamp difference t − τ .
Local Training: We describe the task of the local training in
Algorithm 2. After the client Cj receives the global model and
its corresponding timestamp (wt , t) pushed by the blockchain
through Ci (line 1), then Cj uses this SGD algorithm to update
j
the local model wτ with completing L iterations. Cj first ranj
domly selects samples zτ,l in the data set Dj (line 5), and then
j
starts iterative training wτ,l , where g(·; ·) is the loss function

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

13286

Algorithm 2: LocalUpdate()
Input: wt , t, L.
j
Output: wτ , τ .
1 Receive (wt , t) from Ci ; //Scheduler ;
j
2 τ ← t, wτ,0 ← wt ;
3 Update local model:
4 for local iteration l ∈ [1, L] do
j
5
Randomly sample zτ,l ∼ Dj ;
j
j
j
j
6
wτ,l ← wτ,l−1 − λ ∗ ∇g(wτ,l−1 ; zτ,l );
DP protection:
j
j
8 wτ +1 ← wτ + Y; // See the Eq. 7;
9 τ ← τ + 1;
j
10 return (wτ , τ ).
7

(line 6). To speed up the convergence and ensure that the
local model is closer to the global model, we define the loss
function by


 ζ j

w − wt 2
(6)
g wjτ ; zjτ = f wjτ ; zjτ +
2 τ
where f (·; ·) is the local function and ζ is regularization
weight [10]. To avoid user privacy leakage caused by reverse
inferences of curious clients, DP can be used to further protect
model data by
 s
j
(7)
Y ∼ Lap 0, , wτ +1 = wjτ + Y
ε
where s is sensitivity, ε is privacy budget, and Y is randomly
j
generated Laplacian noise (line 8). Finally, the model wτ with
noise and its timestamp τ are pushed to the blockchain.
Model Aggregation: Model aggregation is performed by
the blockchain network after completing local training for the
tth epoch, which is illustrated in Algorithm 3. Specifically, the
primary node Ci initiates (t + 1)th epoch aggregation request
mt+1 under the action of the fixed timestamp Time, where
o, t, andσi denote opration, timestamp and the signature of
Ci , respectively, (line 1). Then, Ci starts the PBFT consensus, which consists of three phases, including Pre-prepare,
Prepare, and Commit. When starting the Pre-prepare phase,
Pp
Ci calculates and sends a pre-prepare message mt+1,i to
the network, where v, n, and d denote view, series number, and the digest for mt+1 , respectively, (lines 2–4). After
that, the Prepare phase starts and the other backup nodes
Pp
need to check the validity of the received message mt+1,i .
Specifically, Cj needs to ensure that σi and d are correct and
to judge whether the current view is v, and then checks if
a message with the same v and n but different d received.
If all pass, it means the message is legal. After that, the
node needs to change its status to pre-prepared, then calculates and broadcasts the prepare message mPt+1,j to the whole
network, where j is the ID of online backup node (lines 6–
10). Finally, it comes to the Commit phase, Cj first needs
to judge whether the received prepare message from other
clients is legal. The verification method is similar to that
in the Prepare phase, which requires inspection of n, d, v,
and signature. Different from the above checks, Cj needs to

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 15, 1 AUGUST 2023

make sure that it gets at least 2f + 1 such legitimate messages {mPt+1,1 , mPt+1,2 , . . . , mPt+1,2f +1 }. Then, it calculates and
broadcasts the commit message mC
t+1,j , and changes its state
to prepared (lines 11–15). After obtaining sufficient legitC
C
imate commit messages {mC
t+1,1 , mt+1,2 , . . . , mt+1,2f +1 }, Cj
then changes its state to committed. Similarly, the inspection
contents of n, d, v, and signatures are similar to that of the
Commit phase(lines 16 and 17). At this time, the node needs
to perform the mt+1 , which is the (t +1)th epoch global model
aggregation. For the normal local model wkτ (k ∈ N ) uploaded
by the online client, the weight βtk is set to 1 (line 19). For the
delayed local model wkτ (k ∈ Q) of the disconnected client,
the function S(·) can be used to determine the weight βtk by
S(t − τ ) =

1
2(t−τ )

(8)

where t is the current global epoch and τ is the timestamp used
by the delayed client (line 21). When the timestamp difference
of t − τ is large, the corresponding value of βtk can be reduced
by S(·), thereby reducing the error caused by the lag. Then,
Cj accumulates the weight values of all local models to get
βt (line 22). And, the global model wt+1 of (t + 1)th epoch is
aggregated by (9) (line 23)
wt+1 =

n

βk
t

k=1

βt

∗ wkτ .

(9)

After completing model aggregation, the node Cj sends a reply
message mRt+1,j to Ci , where r is the processed global model
result wt+1 (line 24). Ci completes the aggregation task for
the (t + 1)th epoch, once it has received f + 1 consistent reply
messages {mRt+1,1 , mRt+1,2 , . . . , mRt+1,f +1 } (line 25).
VI. S ECURITY A NALYSIS
In this section, we introduce the convergence analysis and
security analysis of our scheme. In the convergence analysis,
it can be concluded that the scheme can successfully converge to the critical point after completing T epochs of global
update. The security analysis is described from three aspects:
1) privacy; 2) availability; and 3) credibility.
A. Convergence Analysis
Definition 3 (ι-Smooth): Let the smoothness parameter ι >
0, the function f is ι-smooth, and if for ∀x, y
ι
y − x 2.
(10)
f (y) − f (x) − ∇f (x), y − x ≤
2
Definition 4 (μ-Strongly Convex): Let constant μ > 0, the
function f is μ-strongly convex, and if for ∀x, y
μ
f (y) − f (x) − ∇f (x), y − x ≥
(11)
y − x 2.
2
Theorem 1: Assume that the function F is ι-smooth and
μ-strongly convex, the bound of the timestamp difference
is A = max(t − τ ), and the imbalance ratio of local training is η = (L1 /L0 ), where L0 and L1 are, respectively,
the minimum and the maximum numbers of local training
iterations. For ∀w ∈ Rd , we have V1 ≥ ∇f (wiτ ; ziτ ) 2 ,
V2 ≥ ∇g(wiτ ; ziτ ) 2 . Let ϕ > 0 and ζ > μ, (ζ 2 −

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

YAN et al.: PRIVACY-PRESERVING ASYNCHRONOUS FEDERATED LEARNING FRAMEWORK

According to Definition 4, we have

Algorithm 3: Aggregation()
Input: J , N , Q, β, wt , t.
Output: wt+1 , t + 1.
1 Ci initiates the request mt+1 = request, o, tσ ;
i
2 Pre-prepare phase:
3 Ci calculates pre-prepare message
Pp
mt+1,i = pre-prepare, v, n, dσi , mt+1 ;
Pp
4 Ci broadcasts the mt+1,i to the whole network;
5 for Cj ∈ N in parallel do
6
Prepare phase:
Pp
7
Receive and verifie the mt+1,i ;
8
Change state to pre-prepared;
9
Calculate prepare message
mPt+1,j = prepare, v, n, d, jσj ;
10
Broadcast the mPt+1,j to the whole network;
11
Commit phase:
12
Receive at least 2f + 1 valid mPt+1 ;
13
Change state to prepared;
14
Calculate commit messgae
mC
t+1,j = commit, v, n, d, jσj ;
15
Broadcast the mC
t+1,j to the whole network;
16
Receive at least 2f + 1 valid mC
t+1 ;
17
Change state to committed;
18
for k ∈ J do
19
βtk ← 1; //Set the weight of N ;
20
21
22
23
24

F(wτ ) − F(wt−1 )

ι
≤ ∇F(wt−1 ) wτ − wt−1 + wτ − wt−1 2
2


≤ βλAL1 O V1 V2 + β 2 λ2 A2 L1 2 O(V2 ).

l=0

Then, we have


E F(wt ) − F(wt−1 )



≤ E βG wτ,L + (1 − β)G(wt−1 ) − F(wt−1 )



 βζ
 
2
wτ,L − wt−1
≤ E β F wτ,L − F(wt−1 ) +
2



≤ βE F wτ,L − F(wt−1 ) + βζ λ2 A2 L12 O(V2 )
L−1

 2
E ∇F wτ,l
+ βλ2 ζ L13 O(V2 )
≤ −βλϕ
l=0

βt ← nk=1 βtk ;
wt+1 ← nk=1 (βtk /βt ∗ wkτ ); // Aggregation;
Send reply message mRt+1,j = reply, v, t, i, j, rσj to
Ci ;

wt+1 ← Ci receives at least f + 1 valid mRt+1 ;
26 return (wt+1 , t + 1).
25

[ζ /2]) wτ,l−1 − wτ 2 ≥ (1 + 2ζ + ϕ)V2 [10]. After completing T epochs of aggregations, our scheme converges to a
critical point w∗
t=0

≤

E F(w0 ) − F(w∗ )


+ O

βλϕTL0


β 2 ληA2 L1
ϕ




+O



ληL12
ϕ




+O


ληA2 L1
+O
.
ϕ

(14)

Let ∀l ∈ [L], then we can get


 
E F wτ,l − F w∗



  ιλ2 
 2
≤ G wτ,l−1 − F w∗ +
E ∇g wτ,l−1

2


− λE ∇G wτ,l−1 , ∇g wτ,l−1


  ι + ζ L12 2
 2

λ V2 − λϕ ∇F wτ,l−1
≤ F wτ,l−1 − F w∗ +
2



 
 2

≤ F wτ,l−1 − F w∗ + λ2 O ζ L12 V2 − λϕ ∇F wτ,l−1


L−1

 2
≤ λ2 O ζ L13 V2 − λϕ
E ∇F wτ,l .
(15)

for k ∈ Q do
βtk ← S(t − τ ); //Set the weight of Q;

T−1
  2
min E ∇F w∗

13287

βηA
ϕ

(16)

Let Lt be the number of iterations for local model updates
in the tth iteration, then we can get
Lt −1

 2
E ∇F wτ,l
l=0

E F(wt−1 ) − F(wt )
λL3
+ 1 O(V2 )
≤
βλϕ
ϕ

 2

β + 1 λA2 L12
βAL1 
O(V2 ) +
O V1 V2 . (17)
+
ϕ
ϕ
After completing T epochs of aggregations, we have

T−1 
min E ∇F(wt ) 2
t=0



≤
(12)

Proof: We assume that in the tth epoch, the client Ci
uploads the local model and its timestamp (wiτ , τ ), L is the
iteration number of Ci ’s local training (L0 ≤ L ≤ L1 ). Let
A = max(t − τ ) and ignore i for convenience, then we can get
wτ − wt−1
≤ (wτ − wτ +1 ) + · · · + (wt−1 − wt−1 )
 
≤ βλAL1 O V2 .

+ βλ2 A2 L12 O(V2 ) + β 3 λ2 A2 L12 O(V2 )


+ β 2 λAL1 O V1 V2 .

1

T L
t -1


T
t=1 Lt t=1 l=0


 2
∇F wτ,l


 2
β + 1 λA2 TL12
E[F(w0 ) − F(wT )]
+
O(V2 )
βλϕTL0
ϕTL0

λTL13
βATL1 
O(V2 ) +
O V1 V2
+
ϕTL0
ϕTL0





∗
E F(w0 ) − F(w )
ληL12
βηA
≤
+O
+O
βλϕTL0
ϕ
ϕ



 2
2
2
ληA L1
β ληA L1
+O
.
(18)
+ O
ϕ
ϕ

≤

(13)

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

13288

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 15, 1 AUGUST 2023

B. Security Analysis
1) Privacy: In FL, each client is independent of the other
and may be curious about the parameters during learning
interactions, so as to reverse reasoning to obtain the privacy
information of other clients. Therefore, to protect the training
parameters, this scheme adds randomly generated Laplacian
noise to the local model of each client by using DP. Laplace
is a continuous distribution and is shown by


|w − μ|
1
exp −
(19)
f (w|μ, b ) =
2b
b

TABLE III
PARAMETER D ESCRIPTIONS

TABLE IV
U NDER THE T HREE DATA S ETS , THE I NFLUENCE OF D IFFERENT ζ
VALUES ON THE T EST ACCURACY

where μ is the position parameter, b is the scale parameter,
its mathematical expectation is μ, and variance is 2b2 . The
concrete visible (5) based on Laplacian DP, where f (D) represents the query function, K(D) is the result of confusion after
adding Laplacian noise to f (D), thus, Y satisfies ε-DP.
Proof: We use Laplace to achieve DP
Pr[K(D1 ) = t]
Pr[K(D2 ) = t]
 

 
k  


i ε 2f exp −ε ti − f (D1 )i f
= k  
 

 


i ε 2f exp −ε ti − f (D2 )i f
⎛ 



 ⎞
ε − ki ti − f (D1 )i  − ki ti − f (D2 )i 
⎠
= exp⎝
f


ε f (D1 ) − f (D2 ) 1
≤ exp
f
= exp(ε).
(20)
2) Availability: FL is usually trained by synchronous
scheduling, that is, the server can update the global model
only after all clients complete local updates. However, in actual
deployment, the uneven performance of each client needs to
be balanced, which leads to a waste of computing resources
and time and low learning efficiency. In addition, the security and accuracy of the system will be greatly reduced if
a client fails to return results in a timely manner. Therefore,
this scheme uses an asynchronous scheduling mode to improve
training efficiency while ensuring system security and model
accuracy.
3) Credibility: The traditional FL solutions rely on a cloud
server, but the stability of this server cannot be guaranteed
and its credibility is low, which forces the global model to
be limited, resulting in the weak credibility of the system.
Therefore, this scheme proposes to use blockchain to replace
traditional cloud servers and integrate untrusted clients to
cooperate and train together, which aims to form a safe and
reliable decentralized ledger.
VII. E XPERIMENTS A NALYSIS
In this section, we use MNIST, Fashion-MNIST, and Cifar10 data sets to benchmark and analyze our scheme.
A. Experimental Setting
The test benchmark of the scheme is MNIST [9], FashionMNIST [33], and Cifar-10 data sets. Among them, the MNIST

data set is widely used in the original FL [15] assessment
and contains ten categories of handwritten images, while the
fashion-MNIST data set contains ten categories of clothing
images. Both data sets contain training 60 000 training samples and 10 000 testing samples. Cifar-10 data set contains
ten categories of RGB color images, and the data set contains
50 000 training samples and 10 000 testing samples.
In each epoch of training, we choose all clients to participate in the training, but there may be someone clients
offline as Byzantine nodes. Our experimental parameters are
shown in Table III, where α represents the percentage of
Byzantine nodes in total nodes at each training epoch, denoted
by BN in Figs. 3–5. This means that at most α×n clients are
Byzantine nodes in each training epoch. Second, we simulate asynchronous scenarios in real applications by randomly
determining the timestamp value t − τ .
B. Comparative Analysis
Based on MNIST, Fashion-MNIST, and Cifar-10 data sets,
we set the classical synchronous optimized FL algorithms,
such as FedAvg [15], the Fedavg-based privacy protection
and offline situation DropPPFL, and the FedProx [34] as
comparison schemes, to evaluate the accuracy of our scheme.
1) MNIST: In Fig. 3(a), we measure the effect of different ζ values {1, 0.1, 0.01, 0.001, 0.0001} on the results of our
scheme (n = 20, t − τ ≤ 4, α = 0.2), and combined with
Table IV, it can be found from the results produced by the
nonoptimal ζ value are within the tolerable range, which the
difference is less than 0.2%. Therefore, even if the optimal ζ
value is not found in practice, our scheme can still achieve satisfactory results. In Fig. 3(b), we compare FedAvg, FedProx,
and DropPPFL with our Scheme. It can be intuitively concluded that offline clients not only slow down the convergence
speed and deteriorate the robustness, but also reduce the accuracy of the model by nearly 10%. In the case of t − τ ≤ 4,
Fig. 3(c) and (d) tests the influence of different α values
{0.1, 0.2, 0.3} on the accuracy of our scheme and FedProx
when n = 10 and n = 20, respectively. We can find that

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

YAN et al.: PRIVACY-PRESERVING ASYNCHRONOUS FEDERATED LEARNING FRAMEWORK

13289

TABLE V
U NDER THE T HREE DATA S ETS , THE I MPACT OF D IFFERENT N UMBERS OF C LIENTS , D IFFERENT P ERCENT
OF B YZANTINE N ODES A ND D IFFERENT T IMESTAMP D IFFERENCES ON T EST ACCURACY

Fig. 3. MNIST test results. (a) n = 20, t − τ ≤ 4, (b) n = 20, t − τ ≤ 4,
(c) t − τ ≤ 4, n = 10. (d) t − τ ≤ 4, n = 20. (e) t − τ ≤ 8, n = 10. (f) t − τ
≤ 8, n = 20.

with the increase of α, the convergence speed of our scheme
slows down, and the range of line jitter becomes larger, but
the accuracy loss is within the allowable range. As the number of clients increases, the number of epochs required for
the schemes to reach convergence increases by 40, but it does
not affect the final test accuracy of the scheme. Similarly, in
the case of t − τ ≤ 8, the effects of different numbers of
clients and different α on our scheme and FedProx are tested
again, as shown in Fig. 3(e) and (f). We give the test accuracy

Fig. 4. FMNIST test results. (a) n = 20, t − τ ≤ 4, (b) n = 20, t − τ ≤ 4,
(c) t − τ ≤ 4, n = 10. (d) t − τ ≤ 4, n = 20. (e) t − τ ≤ 8, n = 10. (f) t − τ
≤ 8, n = 20.

of Fig. 3(c)–(f) in Table V, from which we can find that the
accuracy of the scheme has a little impact with the increase
of the time stamp difference, and even better than that under
the same parameter configuration in some tests t − τ ≤ 4 case
(such as α = 0.1).
2) Fashion-MNIST: In Fig. 4(a), the effects of different
ζ values {1, 0.1, 0.01, 0.001, 0.0001} on the accuracy of
FedProx and our scheme are mainly shown (n = 20, t − τ ≤
4, α = 0.2). Also, combining Table IV shows that we do not

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

13290

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 15, 1 AUGUST 2023

α values {0.1, 0.2, 0.3} on the accuracy of our scheme and
FedProx when n = 10 and n = 20, respectively. And, the test
accuracy is given in Table V. Similar to the FMNIST, Cifar10 can cope well with the problem of dropped clients when
the number of clients increases. And, it can be found that our
scheme is better than t − τ ≤ 8 when dealing with t − τ ≤ 4.
VIII. C ONCLUSION
In this article, we use blockchain instead of a cloud server to
design an asynchronous PPFL without disclosing the privacy
of client data. We evaluate our scheme based on three different
data sets. The results show that our scheme is able to address
the lack of precision and low security. However, the efficiency
of consensus urgently needs to be improved. In future work,
we will also consider how to reduce the time consumption of
PPFL in distributed IoT, in addition to improving the accuracy
of training results.
R EFERENCES

Fig. 5. Cifar-10 test results. (a) n = 20, t − τ ≤ 4, (b) n = 20, t − τ ≤ 4,
(c) t − τ ≤ 4, n = 10. (d) t − τ ≤ 4, n = 20. (e) t − τ ≤ 8, n = 10. (f) t − τ
≤ 8, n = 20.

have to struggle with the optimal value of ζ . In Fig. 4(b), it
can be found that the accuracy of the DropPPFL is reduced by
nearly 15% compared with our scheme. In the case of t−τ ≤ 4
and t − τ ≤ 8, Fig. 4(c)–(f), respectively, tested our scheme
and FedProx with different α values {0.1, 0.2, 0.3} under the
number of clients 10 and 20 The effect on protocol accuracy
and test accuracies are given in Table V. We can find that with
the increase of α, the line jitter of the scheme becomes larger
but it does not affect the final test accuracy of the scheme.
However, in the case of n = 20, the stability of the scheme
will be better than that of n = 10, that is, when the percent
of Byzantine nodes increases, the larger n is, the smaller the
impact will be.
3) Cifar-10: We test Cifar-10 similarly to the above two
data sets. In Fig. 5(a) and Table IV, the effects of different ζ values {1, 0.1, 0.01, 0.001, 0.0001} on the accuracy of
FedProx and our scheme are mainly shown (n = 20, t − τ ≤
4, α = 0.2). It can be found that FedProx has the highest accuracy when ζ = 0.01 and our scheme has the highest accuracy
when ζ = 0.001. Also, we do not have to worry about the
optimal value of ζ . In Fig. 5(b), it can be found that dropped
clients slow down the convergence speed of all schemes. In
addition, the accuracy of the DropPPFL model is reduced by
nearly 8% compared with our scheme. In the case of t −τ ≤ 4
and t − τ ≤ 8, Fig. 5(c)–(f) tests the influence of different

[1] Y. Li, Y. Zhou, A. Jolfaei, D. Yu, G. Xu, and X. Zheng, “Privacypreserving federated learning framework based on chained secure multiparty computing,” IEEE Internet Things J., vol. 8, no. 8, pp. 6178–6186,
Apr. 2021.
[2] Y. Qu et al., “Decentralized privacy using blockchain-enabled federated learning in fog computing,” IEEE Internet Things J., vol. 7, no. 6,
pp. 5171–5183, Jun. 2020.
[3] J. Zhang, Z. Fang, Y. Zhang, and D. Song, “Zero knowledge proofs for
decision tree predictions and accuracy,” in Proc. ACM SIGSAC Conf.
Comput. Commun. Security (CCS), 2020, pp. 2039–2053.
[4] J. Camenisch, M. Drijvers, A. Lehmann, G. Neven, and P. Towa,
“Short threshold dynamic group signatures,” in Proc. Int. Conf. Security
Cryptogr. Netw. (SCN), 2020, pp. 401–423.
[5] D. Boneh, B. Bünz, and B. Fisch, “Batching techniques for accumulators
with applications to IOPs and stateless blockchains,” in Proc. Annu. Int.
Cryptol. Conf. (CRYPTO), 2019, pp. 561–586.
[6] Z. Peng, C. Xu, H. Wang, J. Huang, J. Xu, and X. Chu, “P2 Btrace: Privacy-preserving blockchain-based contact tracing to combat pandemics,” in Proc. Int. Conf. Manag. Data (SIGMOD), 2021,
pp. 2389–2393.
[7] P. Szalachowski, D. Reijsbergen, I. Homoliak, and S. Sun, “Strongchain:
Transparent and collaborative proof-of-work consensus,” in Proc.
USENIX Security Symp. (USENIX Security), 2019, pp. 819–836.
[8] P. Gaži, A. Kiayias, and D. Zindros, “Proof-of-stake sidechains,” in Proc.
IEEE Symp. Security Privacy (SP), 2019, pp. 139–156.
[9] Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner, “Gradient-based learning applied to document recognition,” Proc. IEEE, vol. 86, no. 11,
pp. 2278–2324, Nov. 1998.
[10] C. Xie, S. Koyejo, and I. Gupta, “Asynchronous federated optimization,”
2019, arXiv:1903.03934.
[11] P. Mohassel and Y. Zhang, “SecureML: A system for scalable privacypreserving machine learning,” in Proc. IEEE Symp. Security Privacy
(SP), 2017, pp. 19–38.
[12] C. Zhang, S. Li, J. Xia, W. Wang, F. Yan, and Y. Liu, “BatchCrypt:
Efficient homomorphic encryption for cross-silo federated learning,” in
Proc. USENIX Conf. Usenix Annu. Tech. Conf. (USENIX ATC), 2020,
pp. 493–506.
[13] X. Xu, D. Zhu, X. Yang, S. Wang, L. Qi, and W. Dou, “Concurrent practical Byzantine fault tolerance for integration of blockchain and supply
chain,” ACM Trans. Internet Technol., vol. 21, no. 1, pp. 1–17, 2021.
[14] C. Dwork, “Differential privacy: A survey of results,” in Proc. Int. Conf.
Theory Appl. Models Comput. (TAMC), 2008, pp. 1–19.
[15] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. Y. Arcas,
“Communication-efficient learning of deep networks from decentralized data,” in Proc. Int. Conf. Artif. Intell. Stat. (AISTATS), 2017,
pp. 1273–1282.
[16] H. Fang and Q. Qian, “Privacy preserving machine learning with homomorphic encryption and federated learning,” Future Internet, vol. 13,
no. 4, p. 94, 2021.

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.

YAN et al.: PRIVACY-PRESERVING ASYNCHRONOUS FEDERATED LEARNING FRAMEWORK

[17] R. Kanagavelu et al., “Two-phase multi-party computation enabled
privacy-preserving federated learning,” in Proc. IEEE/ACM Int. Symp.
Clust. Cloud Internet Comput. (CCGRID), 2020, pp. 410–419.
[18] S. Zheng et al., “Asynchronous stochastic gradient descent with
delay compensation,” in Proc. Int. Conf. Mach. Learn. (ICML), 2017,
pp. 4120–4129.
[19] X. Zhou, Y. Deng, H. Xia, S. Wu, and M. Bennis, “Resource allocation
for time-triggered federated learning over wireless networks,” in Proc.
IEEE Int. Conf. Commun. (ICC), 2022, pp. 2810–2815.
[20] X. Zhang, X. Chen, J. K. Liu, and Y. Xiang, “DeepPAR and deepDPA:
Privacy preserving and asynchronous deep learning for industrial IoT,”
IEEE Trans. Ind. Informat., vol. 16, no. 3, pp. 2081–2090, Mar. 2020.
[21] J. Konečnỳ, H. B. McMahan, F. X. Yu, P. Richtárik, A. T. Suresh, and
D. Bacon, “Federated learning: Strategies for improving communication
efficiency,” 2016, arXiv:1610.05492.
[22] N. Mehrabi, F. Morstatter, N. Saxena, K. Lerman, and A. Galstyan, “A
survey on bias and fairness in machine learning,” ACM Comput. Surv.,
vol. 54, no. 6, pp. 1–35, 2021.
[23] C. Fung, C. J. M. Yoon, and I. Beschastnikh, “Mitigating sybils in
federated learning poisoning,” 2018, arXiv:1808.04866.
[24] W.-M. Lee, Beginning Ethereum Smart Contracts Programming, With
Examples in Python, Solidity and JavaScript. Berkeley, CA, USA:
Apress, 2019.
[25] Y. Lu, X. Huang, Y. Dai, S. Maharjan, and Y. Zhang, “Blockchain and
federated learning for privacy-preserved data sharing in industrial IoT,”
IEEE Trans. Ind. Informat., vol. 16, no. 6, pp. 4177–4186, Jun. 2019.
[26] S. Awan, F. Li, B. Luo, and M. Liu, “Poster: A reliable and accountable
privacy-preserving federated learning framework using the blockchain,”
in Proc. ACM SIGSAC Conf. Comput. Commun. Security (CCS), 2019,
pp. 2561–2563.
[27] Y. Liu, Y. Qu, C. Xu, Z. Hao, and B. Gu, “Blockchain-enabled asynchronous federated learning in edge computing,” Sensors, vol. 21, no. 10,
p. 3335, 2021.
[28] Y. Lu, X. Huang, K. Zhang, S. Maharjan, and Y. Zhang, “Blockchain
empowered asynchronous federated learning for secure data sharing
in Internet of Vehicles,” IEEE Trans. Veh. Technol., vol. 69, no. 4,
pp. 4298–4311, Apr. 2020.
[29] L. Feng, Y. Zhao, S. Guo, X. Qiu, W. Li, and P. Yu, “BAFL: A
blockchain-based asynchronous federated learning framework,” IEEE
Trans. Comput., vol. 71, no. 5, pp. 1092–1103, May 2022.
[30] C. Dwork and A. Roth, “The algorithmic foundations of differential privacy,” Found. Trends Theor. Comput. Sci., vol. 9, nos. 3–4, pp. 211–407,
2014.
[31] C. Dwork, F. McSherry, K. Nissim, and A. Smith, “Calibrating noise
to sensitivity in private data analysis,” in Proc. Theory Cryptogr. Conf.
(TCC), 2006, pp. 265–284.
[32] Q. Yang, Y. Liu, T. Chen, and Y. Tong, “Federated machine learning:
Concept and applications,” ACM Trans. Intell. Syst. Technol., vol. 10,
no. 2, pp. 1–19, 2019.
[33] H. Xiao, K. Rasul, and R. Vollgraf, “Fashion-MNIST: A novel
image dataset for benchmarking machine learning algorithms,” 2017,
arXiv:1708.07747.
[34] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith,
“Federated optimization in heterogeneous networks,” in Proc. Int. Conf.
Mach. Learn. Syst. (MLSys), vol. 2, 2020, pp. 429–450.

Xinru Yan received the B.E. degree from
the Department of Automation and Software
Engineering, Shanxi University, Taiyuan, China, in
2022. She is currently pursuing the M.E degree
with the Department of Cyber Engineering, Xidian
University, Xi’an, China.
Her research interests include information security
and applied cryptography.

13291

Yinbin Miao (Member, IEEE) received the B.E.
degree from the Department of Telecommunication
Engineering, Jilin University, Changchun, China, in
2011, and the Ph.D. degree from the Department of
Telecommunication Engineering, Xidian University,
Xi’an, China, in 2016.
He is also a Postdoctoral Researcher with
Nanyang Technological University, Singapore, from
September 2018 to September 2019, and the City
University of Hong Kong, Hong Kong, from
December 2019 to December 2021. He is currently
an Associate Professor with the Department of Cyber Engineering, Xidian
University. His research interests include information security and applied
cryptography.

Xinghua Li received the M.E. and Ph.D. degrees
in computer science from Xidian University, Xi’an,
China, in 2004 and 2007, respectively.
He is currently a Professor with the School of
Cyber Engineering, Xidian University. His research
interests include wireless networks security, privacy
protection, cloud computing, and security protocol
formal methodology.

Kim-Kwang Raymond Choo (Senior Member,
IEEE) received the Ph.D. degree in information
security from Queensland University of Technology,
Brisbane, QLD, Australia, in 2006.
He currently holds the Cloud Technology
Endowed Professorship with The University of
Texas at San Antonio, San Antonio, TX, USA.
Dr. Choo is the Founding Co-Editor-in-Chief of
ACM Distributed Ledger Technologies: Research
and Practice, Founding Chair of IEEE TEMS
Technical Committee on Blockchain and Distributed
Ledger Technologies, an ACM Distinguished Speaker, and IEEE Computer
Society Distinguished Visitor from 2021 to 2023, and a Web of Science’s
Highly Cited Researcher (Computer Science in 2021, Cross-Field in 2020).
He is also the recipient of the 2019 IEEE Technical Committee on Scalable
Computing Award for Excellence in Scalable Computing (Middle Career
Researcher).

Xiangdong Meng, photograph and biography not available at the time of
publication.

Robert H. Deng (Fellow, IEEE) received the B.E.
degree from the National University of Defence
Technology, Changsha, China, in 1981, and the
M.S. and Ph.D. degrees from Illinois Institute of
Technology, Chicago, IL, USA, in 1983 and 1985,
respectively.
He has been an AXA Chair Professor of
Cybersecurity and a Professor of Information
Systems with the School of Information Systems,
Singapore Management University, Singapore, since
2004. His research interests include data security and
privacy, multimedia security, network, and system security.
Dr. Deng has received the Distinguished Paper Award for NDSS in 2012,
the Best Paper Award for Computational Management Science in 2012, and
the Best Journal Paper Award for IEEE Communications Society in 2017. He
served/is serving on the editorial boards of many international journals, including IEEE T RANSACTIONS ON I NFORMATION F ORENSICS AND S ECURITY
and IEEE T RANSACTIONS ON D EPENDABLE AND S ECURE C OMPUTING.

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:32:35 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
