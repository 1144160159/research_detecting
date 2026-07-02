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
# [583] A Federated and Incremental Network Intrusion Detection System for IoT Emerging Threats
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
编号：583
题名：A Federated and Incremental Network Intrusion Detection System for IoT Emerging Threats
年份：2026
DOI：10.1109/tnsm.2026.3675031
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2026.3675031.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：联邦学习、隐私保护与分布式协同、IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 15
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\583.txt
- 原始字符数：77004
- 本次发送字符数：77004
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

3865

A Federated and Incremental Network Intrusion
Detection System for IoT Emerging Threats
Raffaele Carillo , Francesco Cerasuolo , Giampaolo Bovenzi , Domenico Ciuonzo , Senior Member, IEEE,
and Antonio Pescapé , Senior Member, IEEE

Abstract—Ensuring network security is increasingly challenging, especially in the Internet of Things (IoT) domain, where
threats are diverse, rapidly evolving, and often device-specific.
Hence, Network Intrusion Detection Systems (NIDSs) require
(i) being trained on network traffic gathered in different
collection points to cover the attack traffic heterogeneity,
(ii) continuously learning emerging threats (viz., 0-day attacks),
and (iii) be able to take attack countermeasures as soon as
possible.In this work, we aim to improve Artificial Intelligence
(AI)-based NIDS design & maintenance by integrating Federated Learning (FL) and Class Incremental Learning (CIL).
Specifically, we devise a Federated Class Incremental Learning
(FCIL) framework–suited for early-detection settings—that supports decentralized and continual model updates, investigating
the non-trivial intersection of FL algorithms with state-of-the-art
CIL techniques to enable scalable, privacy-preserving training in
highly non-IID environments. We evaluate FCIL on three IoT
datasets across different client scenarios to assess its ability to
learn new threats and retain prior knowledge. The experiments
assess potential key challenges in generalization and few-sample
training, and compare NIDS performance to monolithic and
centralized baselines.
Index Terms—Network intrusion detection systems, Internet
of Things, federated learning, class incremental learning,
0-day attacks.

I. I NTRODUCTION
YBER-ATTACKS have increased rapidly in the last few
years, reaching an impressive number of 600 million of
attacks performed daily [1], highlighting the urgent need for
service providers to adopt a more proactive role in ensuring
the integrity, confidentiality, and availability of data across
digital infrastructures. In this scenario, NIDSs are central to
securing modern networks, shifting from static, signaturebased methods to adaptive approaches powered by Machine
Learning (ML) and Deep Learning (DL) techniques [2]. This
need is even more pronounced in the IoT domain, where
resource-constrained and heterogeneous devices increase the
attack surface. For instance, IoT nodes are often hijacked into
botnets for large-scale DDoS attacks (e.g., Mirai) [3], or run
outdated firmware that enables persistent exploitation [4].
However, AI-based NIDS cannot easily adapt to emerging
(0-day) attacks, as updating them requires training-from-

C

Received 10 August 2025; revised 23 January 2026; accepted 13 March
2026. Date of publication 17 March 2026; date of current version
13 April 2026. The associate editor coordinating the review of this article
and approving it for publication was N. Stakhanova. (Corresponding author:
Francesco Cerasuolo.)
The authors are with the Department of Electrical Engineering and Information Technologies (DIETI), University of Naples Federico II, 80138 Naples,
Italy (e-mail: francesco.cerasuolo@unina.it).
Digital Object Identifier 10.1109/TNSM.2026.3675031

scratch, which is both storage- and computation-intensive [5].
Moreover, while cross-network data sharing could enhance
NIDS by broadening threat coverage, it raises serious privacy concerns, making it impractical in most real-world
scenarios involving user data. Notably, recent studies have
investigated either CIL or FL for NIDS, but largely in isolation: CIL approaches typically assume centralized access
to all traffic data, while FL ones usually consider a fixed
and pre-defined set of attack classes. Only a limited number
of works explore their integration, and those that do often
focus on simplified scenarios such as binary detection tasks,
overlapping classes, or post-hoc analysis. Consequently, the
problem of incrementally learning new, client-specific attack
classes from decentralized, non-IID data in an early-detection
setting remains largely unaddressed.
In this work, we propose a FCIL framework for NIDS
that simultaneously addresses the challenges of incremental learning and decentralized training. By integrating CIL,
the system can continuously incorporate new attack classes
without forgetting previously learned threats, while FL
enables collaborative model training across distributed clients,
ensuring scalability and preserving data privacy. This combination allows our NIDS to adapt in real time to emerging
threats in heterogeneous network environments [6], [7],
[8].
Combining FL and CIL for designing NIDS poses unique
and still largely unaddressed challenges. First, the non-IID
nature of client data means new attack classes may emerge
only on specific clients, leading to imbalanced updates and
poor generalization. Second, catastrophic forgetting is intensified, as clients may observe only new classes, causing the
global model to overwrite knowledge of previously learned
attacks. Third, the stability–plasticity dilemma becomes even
more pronounced, as each client must not only retain previously learned classes while learning new (local) ones, but also
integrate new disjoint attack classes from other clients.
Hence, the contributions of this work are the following:
• we formalize and study a realistic FCIL problem for
NIDS, where early detection, client-specific novel attacks,
and non-IID decentralized data jointly coexist, a setting
that has not been systematically addressed in prior work;
• we provide a comprehensive analysis of how stateof-the-art (SOTA) CIL strategies behave in federated
environments, revealing non-trivial interactions with
different aggregation schemes (FedAvg, FedProx, and
FedDyn) and limitations, absent in centralized setups;

© 2026 The Authors. This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 License.
For more information, see https://creativecommons.org/licenses/by-nc-nd/4.0/

3866

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

TABLE I
S TUDIES P ROPOSING CIL AND / OR FL T ECHNIQUES FOR NIDS F ROM 2022 O NWARDS IN C HRONOLOGICAL O RDER

• we investigate realistic federated configurations with
varying numbers of clients (i.e., 2 and 5), each introducing a single, disjoint novel attack, thereby explicitly
stressing FCIL-designed NIDS under severe class imbalance and client heterogeneity;
• we evaluate FCIL-designed NIDS in real-world scenarios, assessing its ability to (i) generalize across networks
and (ii) learn effectively from a limited number of
samples.

The rest of the paper is organized as follows. The studies
dealing with CIL and FL for NIDS are reviewed in Sec. II.
Then, Sec. III describes the FCIL procedure. The experimental
setup and results are reported in Sec. IV and V, respectively.
Lastly, Sec. VI concludes our work, highlighting also future
directions of our research.
II. R ELATED W ORKS
In this section, we review the use of CIL and FL in the
context of NIDS. First, we discuss approaches that apply CIL
to NIDS in Sec. II-A, followed by an overview of FL-based

CARILLO et al.: FEDERATED AND INCREMENTAL NETWORK INTRUSION DETECTION SYSTEM

methods in Sec. II-B. Then, we examine recent efforts that
integrate both paradigms—CIL and FL—for NIDS (Sec. II-C).
Finally, Sec. II-D positions our work within this landscape.
A summary of the reviewed literature is provided in Table I.
A. Incremental Learning for NIDS
In this section, we review the literature on CIL applied to
NIDS, focusing on approaches that adapt existing intrusion
detectors to counter emerging attack types and anomalies.
In the literature, CIL approaches are divided into three main
families based on model expansions [31]: (i) ”fine-tuning,
expanding the model head and updating the entire model
with the incremental training set; (ii) ”fixed-representation,
expanding the model head and freezing parts of the pre-trained
model (viz., backbone and/or old head), definitively training
the non-frozen parts; (iii) ”model-growth, adding new models
or layers to accommodate new knowledge.
All the reviewed works are from the fine-tuning family,
except for I2 RNN [11] and SPCIL [14], which employ modelgrowth solutions. Notably, the fixed-representation family
remains largely unexplored for network intrusion detection
tasks, as freezing the base model may undermine the plasticity
required to learn new patterns (see column “CIL Approach”
in Tab. I for further details).
As for incremental episodes (column “CIL Increments”),
most of the reviewed works adopt multi-class increments—i.e.,
adding more new classes per episode—while only [11], [15]
explore the single-class addition scenario, which more closely
mirrors real-world deployment with new attacks typically
appearing individually over time.
Reviewed work deals with the Multi-class Misuse Detection
(mMD) task—i.e., distinguishing among benign and all the
attack classes—, while Binary Misuse Detection (bMD)—i.e.,
differentiating benign and malicious traffic—is also considered
in [16]. In addition, Cerasuolo et al. [15] decompose the intrusion detection process into two sequential tasks: a bMD task
and an Attack Classification (AC) task—i.e., categorization of
malicious traffic into different attack types.
Crucially, most of these studies focus on post-mortem
detection—that is, they do not perform early detection (see
column “Early Detection”)—typically relying on statistics
computed over the entire traffic object (see column “Input
Data”). In contrast, a subset of works avoid (handcrafted)
feature summarization, using raw fields from packet headers
or payloads as direct inputs to the model. These approaches
typically leverage only the first N p packets of a flow to build
NIDS that support early-stage decisions and enable timely,
proactive response to threats.
B. Federated Learning for NIDS
In this section, we review the literature on FL applied
to NIDS. FL allows NIDS to be trained on decentralized
attack data, preserving privacy and minimizing malicious
traffic transmission. This is especially valuable for sensitive or
large-scale data, enabling collaborative and privacy-preserving
training [8]. In the literature, two main FL families are commonly distinguished based on how data is distributed among

3867

clients: (i) horizontal (or homogeneous) FL, where clients
share the same feature space but each possesses a different
set of data samples; and (ii) vertical (or heterogeneous) FL,
in which clients hold different features corresponding to the
same sample set [32]. Additionally, FL can be classified by
the network dimensions into (i) cross-device and (ii) crosssilo settings. The former involves many personal devices
with unstable connections and variable data, while the latter
features fewer entities—e.g., organizations—with more stable,
high-bandwidth links and less frequent communication [33].
Furthermore, client data can be characterized as either independently and identically distributed (IID) or non-IID. In the
former setting, data across clients is statistically consistent and
independent. Conversely, in the latter case, data samples are
interdependent and drawn from different distributions, often
reflecting the inherent heterogeneity among clients [33].
Among the reviewed literature, all works deal with horizontal FL, sharing feature space while having a disjoint sample
space. Moreover, all the works implement a cross-device setup,
with local training performed on edge devices, and deal with
classes and samples shared among clients, resulting in data
distributions that are only partially non-IID (column “DC”).
As for FL algorithm (column “FL approach”), the majority
of works leverage FedAvg [17], [18], [19], [21], [22]. Additionally, other works propose minor modifications to FedAvg,
such as incorporating weighted averaging schemes and client
selection based on contribution significance [20], while others
adopt more sophisticated FL algorithms, such as FedProx [21].
Interestingly, Rey et al. [17] investigate techniques to defend
against adversarial clients aiming to poison the global model.
Finally, all the revised studies address the mMD task
employing (supervised) DL models [18], [19], [20], [22],
except for [17] and [21] leveraging the (unsupervised)
AutoEncoders (AEs) to perform the Anomaly Detection (AD)
task—that is, training only on the benign class and recognizing
attacks as anomalies or out-of-distribution samples.
C. Federated Incremental Learning for NIDS
In this section, we review existing work that integrates
incremental expansion of NIDS (i.e., CIL) with decentralized
training approaches (i.e., FL), namely, FCIL. Notably, all
these studies focus on a multi-class addition (column “CIL
Setup”)—only [28] addresses single-class addition—and consider non-disjoint classes among clients (column “DC”).
Among these studies, most adopt CIL approaches which
are baselines in network-related tasks, except for SOINN-RBF
[23]— leveraging self-organizing incremental neural networks
(SOINN) in conjunction with Radial Basis Function (RBF),
incrementally mapping the original input into a higherdimensional space.
Regarding the FL strategy, most employ FedAvg either in
its original form or with minor adaptations, as seen in [25],
[27], [29]. Notably, Jin et al. [25] leverage class prototypes
and importance factors for client models in the aggregation
process. On the other hand, Mao et al. [27] and Quyen et al.
[29] weight each client model during FedAvg aggregation
according to the size of its training dataset. In addition,
several studies adopt alternative FL aggregation algorithms as

3868

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

performance baselines for comparison, including FedSI [28],
CMFL [23], FedSpace [28], GLFC [26], [28], FCIL [28],
FedProto [28], FedProx [30], SCAFFOLD [30], FedMD [30],
FedDF [30], and FedGKT [30], or define new approaches,
such as EvoFedIDS [28] or Fed-SOINN [23].
As for the detection task, the majority focus on supervised
misuse detection—either bMD [23], [24], [28] or mMD [25],
[26], [29]. Notably, Jin et al. [25] detect both known and zeroday intrusions and continuously adapt to emerging threats, but
also perform mMD to discriminate among known classes.
D. Literature Gap & Positioning
In this work, we deal with incremental and decentralized
NIDS to tackle the evolving nature of cyber-attacks and
associated privacy concerns. Differently from previous works
considering only CIL [9], [10], [11], [12], [13], [14], [15],
[16] or FL [18], [19], [20], [21], [22] separately, which either
assume centralized data availability or a fixed and closed set of
attack classes, we explore how NIDS can continuously learn
in a decentralized fashion.
Equally important, in contrast with existing literature on
FCIL for NIDS [23], [24], [25], [27], [28], [29], which mostly
assumes full-traffic or post-mortem analysis and overlooks the
constraints of timely intrusion response, we consider an earlydetection setup and investigate the mMD task, along with its
decoupled counterpart bMD, followed by the AC task. Separating bMD and AC decouples detection from classification
performance. Unlike mMD, this distinction reveals whether
a system can only detect threats and correctly identify them
separately, enabling a clearer assessment of its capabilities.
Furthermore, in order to support low-resource environments,
we adopt neither model-growth approaches (e.g. DER)—
given their increasing storage and communication costs,
which are particularly detrimental in federated settings —,
nor baseline approaches for network-related tasks (i.e., FT,
EWC, iCaRL, and WA), which have been shown to be noneffective for network traffic data [34]. Conversely, we focus on
cutting-edge CIL approaches from fine-tuning family, such as
iCaRL+ [35], BiC [36] and BiC+ [37], MEMENTO [38] and
MEMENTO+ [37], in their decentralized flavor. This choice is
motivated by the lightweight nature of fine-tuning approaches,
which impose minimal storage and communication overhead
when compared to model-growth solutions.
To account for non-IID and unbalanced attack distributions, we move beyond the de facto standard FedAvg and
include FedProx and FedDyn, which explicitly handle client
heterogeneity and update stability, enabling a more realistic
evaluation of CIL–FL integration.
Further, most prior FCIL studies assume overlapping attack
classes or the simultaneous introduction of multiple classes,
which mitigates class imbalance and simplifies aggregation.
In contrast, we consider a more general scenario in which
each client introduces a single, distinct novel attack, resulting
in client-specific attack distributions—i.e., no class overlap
between clients. Moreover, we consider the addition of a
single attack (class) per client—a more challenging scenario
than those considered in prior work, due to the pronounced

imbalance between new and existing classes [34]. Additionally, adding a single attack per client reflects realistic scenarios
where new attacks emerge sparsely and unevenly across the
network. Lastly, we assess scalability by varying the number
of clients in federated networks, evaluating how the resulting
FCIL NIDS handles real-world challenges like cross-network
generalization and limited data availability.
III. M ETHODOLOGY
We begin by presenting the core methodologies behind
CIL (Sec. III-A) and FL (Sec. III-B). Then, we introduce the
NIDS-focused unified framework for FCIL (Sec. III-C), which
integrates the key principles of both paradigms.
A. Class Incremental Learning
In this work, we adopt the CIL paradigm within
DL architectures. To provide context, we first introduce the notation about data and fundamental concepts
underlying both approaches. Notably, the training dataset
(D={(x1 , y1 ), . . ., (xN , yN )}) is composed of N input samples,
where each sample (e.g., a biflow) xn ∈ X is labeled as benign
traffic or attack class (i.e., yn ∈ K = 1, 2, 3, . . .).
Considering a generic DL architecture, it is composed of
two parts: a backbone, in charge of the feature extraction
φ : X → V obtaining from the input (x) its latent space
representation v (viz., feature vector); a head, transforming
feature vectors into logits h(φ(x)) = o(x) ∈ O. Then, logits
are converted into class probabilities via the usual softmax
activation function, defined as


|K|
X

softmax(x) k = pk (x; K) = eok (x) /
eo j (x) ,

(1)

j=1

and predictions are obtained as ŷ , argmaxk∈K {pk (x; K)}.
The incremental NIDS aims to train a set of parameters
θ to learn a function γ : X → K, with γ(x) = ŷ ∈ K
representing the predicted label for input x (i.e., legitimate
traffic or a specific attack type).
The CIL problem can be formulated as follows: at each
episode, a set of new classes Knew is introduced, along with
a labeled dataset Dnew . The goal is to update an existing
NIDS—previously trained on Dold —to integrate knowledge
from Knew while preserving its ability to recognize the previously learned classes Kold , thereby enabling discrimination
over the complete class set (Kall = Kold ∪ Knew ). Some CIL
methods additionally exploit a subset of samples from the old
classes, retained in memory, to reinforce prior knowledge during incremental updates. In such cases, training is performed
on the combined dataset Dmem ∪ Dnew [39].
In the following, the CIL approaches employed in this
work are presented. Specifically, we consider approaches from
fine-tuning family, as they offer the highest scalability without increasing the resource demand. [31]. Notably, all these
approaches are considered as a baseline for the incremental
process—i.e., FT-Mem—or have proven to be effective for
network traffic classification [34], [35], [38] or adaptive NIDS
task [15]. They utilize an exemplar memory and often employ

CARILLO et al.: FEDERATED AND INCREMENTAL NETWORK INTRUSION DETECTION SYSTEM

a composite loss function to guide the training process, with
an optional bias correction layer to prevent task-recency bias.
FT-Mem—Fine-Tuning with Memory [34]: built on top
of Fine-Tuning (FT) approach [40], it stores a small part of
old classes samples—selected with herding strategy—and use
them in the incremental training (viz., D = Dnew ∪ Dmem ) to
reduce catastrophic forgetting, by refreshing old knowledge.
iCaRL+—Incremental Classifier and Representation
Learning Plus [35]: it adapts iCaRL to network traffic, incorporating both rehearsal strategy (through herding selection)
and a composite loss function with equally weighted classification and Knowledge Distillation (KD) terms (λclass = λdist = 1).
Differently from iCaRL employing a Nearest Mean Classifier,
iCaRL+ leverage a model head that dynamically expands and
activates through the softmax function.
BiC—Bias Correction [36]: it introduces an additional
layer—parametrized with α and β—to correct new classes
logits to reduce the task recency and sample biases towards
new classes. The incremental training is led by a composite
loss function with classification and KD terms (weighted by
λclass = |Knew |/|Kall | and λdist = 1 − λclass , respectively). BiC
retains a balanced small set of biflows—also called correction
set—composed of dP% · Nold e for each old and new class,
where Nold represents the number of old samples for each
Kold .1 Therefore, the additional layer is trained on this dataset
(viz., correction set) to determine the two parameters with both
backbone and head frozen.
MEMENTO—distill augMented knowlEdge, sMooth nEw
iNformation, and recTify bOth [38]: built upon BiC, it
is defined depending on the scenario considered. Notably,
for few-class increments, MEMENTO introduces a series of
enhancements for improving network traffic classification performance. These include (i) biflow augmentation techniques
using static traffic primitives applied to the IAT—viz., jittering

 

IAT jit , iat1 · · · iatN p + ρ1 · · · ρN p ,
where ρi ∼ N (µ, σ), i = 1, . . . , NP , and translating

 

IATtra = iat1 · · · iat N p + ρ · · · ρ ,
where ρ ∼ N (µ, σ)—, (ii) the construction of a balanced validation set from exemplars memory to lead incremental training
across tasks, and (iii) the use of a higher temperature in the
classification loss to encourage softer probability distributions
and reduce overconfidence. Last but not least, MEMENTO
applies (iv) output smoothing during knowledge distillation to
better handle biflows belonging to newly-introduced classes.
B. Federated Learning
In a typical FL setup, a network of M clients c1 , c2 , . . ., c M
collaboratively trains a shared model. During each communication round r, mth client first updates its local model θrm
using its private dataset Dm , tailoring the training to its task.
Once local training is complete, clients send their updated
1 The number of per-class biflows in the correction set is limited by the old
classes, which are fewer in memory than the new-class biflows of the current
episode.

3869

model parameters to a central federated server, which coordinates the training process. The server aggregates the received
models to produce an updated global model that captures the
collective knowledge of all clients. This global model is then
redistributed to the clients, who resume local training based
on the aggregated update. This process is iteratively repeated
for R communication rounds.
In this work, we consider a cross-silo FL setting, i.e.,
a federated network with a small number of clients representing different organizations or geographical collection
points. Each client corresponds to a group of IoT devices
(e.g., gateways, edge nodes, or administrative domains) rather
than individual constrained sensors, and clients collaboratively
train a global NIDS; while each client observes traffic from
different attack classes (non-IID), all employ the same feature
space (horizontal FL). Communication is therefore limited to
exchanging model updates, whose size—on the order of a few
MB per round for our architecture—is compatible with NBIoT, LTE-M, and typical edge/cloud backhaul links assumed
in cross-silo IoT and industrial deployments [41]. Supporting
fully constrained end devices would instead require additional
mechanisms such as model compression or hierarchical FL.
In the experiments, we leverage different FL approaches to
aggregate models from different federated clients. In detail,
we employ three approaches, described in the following.
Notably, we exclude some approaches from our analysis as
they compute and share local prototypes across the federation, introducing significant computational and communication
overhead—e.g., FedProK [42], LGA [43].
Federated Averaging (FedAvg) [44]: each client performs
local model update by minimizing its own loss function Fm (θ),
yielding updated parameters θrm = arg minθ Fm (θ). These
locally-updated models are then transmitted to a central server,
which computes the global model by averaging the collected
client parameters.
M
1 X r
θm
(2)
θr =
M
m=1

FedProx (FedProx) [45]: built upon FedAvg, it is based
on the assumption that clients may have very different data
distributions and may not converge when using FedAvg. For
these reasons, FedProx adds a proximal term to the local
(viz. client) objective function to keep local updates closer
to the global model. At each communication round r, client
m computes updated parameters as θrm = arg minθ Lm (θ) by
minimizing the following augmented objective function:
µ
2
Lm (θ) = Fm (θ) +
θ − θr−1 ,
(3)
2
where Fm (·) is the standard local loss on client m, and µ
controls the strength of the regularization term. The squared
`2 -norm keeps each client’s model close to the previous global
parameters θr−1 , enhancing robustness to data heterogeneity.
Server aggregation is then performed analogously as FedAvg.
FedDyn [46]: it aims to improve the communication efficiency of FedAvg by dynamically modifying the client
objective with a penalty term so that when model parameters
converge, they do so in stationary points of the global empirical loss. In particular, the linear and quadratic penalty terms

3870

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 1. Visual representation of the overall proposal. Each client incrementally trains its local NIDS, including new attacks, and simultaneously participates
in the federated network’s collaborative information exchange. This process converges to a global NIDS, then distributed across all clients, to perform (binary
and multiclass) misuse detection and attack classification.

minima are consistent with the global loss stationary point.
The penalty term is based on the local and server models,
namely:
α
2
θ − θr−1 , (4)
Lm (θ) = Fm (θ) − h∇Fm (θr−1
m ), θi +
2
where the first term represents the standard local empirical
loss (e.g., cross-entropy); the second term (h∇Fm (θr−1
m ), θi)
subtracts a linear approximation based on past gradients to
compensate for bias in the client distribution; and the third
2
term, α2 θ − θr−1 , encourages the local model to stay close
to the previous global model θr−1 , similar to FedProx. Server
aggregation is performed similarly to FedAvg and FedProx.
C. Federated Class Incremental Learning
In the FCIL setup, each client incrementally introduces a
new set of classes, with the objective of training a global
NIDS capable of accurately classifying both previously learned
and newly introduced classes across all clients. The overall
procedure is depicted in Fig. 1.
Formally, at the generic (incremental) episode, mth client
in the federated network adds a set of new classes Kmnew . The
FCIL procedure begins with a base model—trained on previously seen classes Kold during an earlier federated (possibly
incremental) iteration—which is then distributed to all clients
joining the network. Accordingly, all the clients start the incremental process from the same model, effectively representing
a scenario where clients can join the network asynchronously
and require a synchronization step. In a federated setting,
m client performs local training for a fixed number of epochs
before synchronizing with the server and other clients across
R communication rounds.
In the FCIL context, the goal is to update an existing
NIDS—previously
trained on Dold —to integrate knowledge
S ˚ new M
new
from K̄ ,
Km m=1 (i.e. the set of new classes from all
the involved clients) while preserving its ability to recognize
the previously learned classes Kold . Hence, discrimination
capabilities of the updated NIDS are required to be over the
complete class set Kall = Kold ∪ K̄new .

Despite the generality of the above FCIL formulation (and
of the proposed solutions), in this work we are concerned
with the case where each client introduces a distinct set
of new classes, i.e. Kmnew ∩ Kmnew
= ∅, for m , m0 . This
0
setting poses a significant challenge, as it leads to an extreme
form of non-independent and identically distributed (non-IID)
data distribution among the clients, who must also mitigate
catastrophic forgetting as they learn new classes.
On the top of that, integrating CIL into a federated setting
introduces specific design challenges. While simpler finetuning methods can be directly federated, those including
post-training techniques like bias correction [36], [38] require
tailored solutions. In this work, we leverage two different
solutions [37] which capitalize FL framework.
In the first one, all clients share the same bias layer for new
classes K̄new , similar to BiC-based solutions in a centralized
setting. Each client updates this layer using its own data
(Dmem ∪ Dmnew ), the server averages the clients’ parameters
(αnew
m , βm ) to compute the global correction, and sent the
averaged correction to all clients for the next round:


oold (x)

ō(x) = 1 P M
(5)
new new
(x) + βm · 1|K̄new |
m=1 αm o
M
In the second approach, each client maintains a personalized
bias layer for its new classes. At each round, client cm updates
only its local parameters (αnew
m , βm ) and shares them with
the server. The server stacks all client-specific corrections to
support classification across all new classes:
2
3
oold (x)
6 αnew onew + β1 · 1|Knew | 7
1
6 1 1
7
ō(x) = 6
(6)
7
..
4
5
.
new
new
αnew
M oM + β M · 1|K M |

M
The set of all correction parameters (αnew
m , βm )m=1 are sent back
to all clients for next round. We denote the averaged variant
by A, and the client-specific one by A+ .
We note that the proposed FCIL framework does not
incur additional asymptotic computational overhead compared to standard FL. The overall complexity is dominated

CARILLO et al.: FEDERATED AND INCREMENTAL NETWORK INTRUSION DETECTION SYSTEM

3871

Fig. 2. Biflows distributions for the IoT datasets employed. Green bars represent the benign class across all three datasets. Sankey diagrams show specific
attacks per category, with colored circles indicating the datasets that contain each attack.

by local training 
at each client and can be expressed as
PM
R
E
N
P
, where M is the number of clients, R
O
m
m=1
the number of communication rounds, E the number of local
training epochs, Nm the number of training samples at client m
(i.e., the size of Dmem ∪ Dmnew ), and P the number of trainable model parameters. The server-side aggregation of client
parameters has linear complexity with respect to the number of
clients and parameters, i.e. O(MP) per communication round.
We emphasize that the additional components introduced by
the FCIL framework—such as shared or client-specific bias
layers for incremental class correction—do not affect the
asymptotic complexity. Their cost is negligible compared to
the standard local training, since the number of parameters in
these layers is small relative to the full model.
IV. E XPERIMENTAL S ETUP
In this section, we describe the datasets leveraged for
the experiments (Sec. IV-A), along with the DL architecture
employed (Sec. IV-B). Then, we present the upperbound
considered for experiments (Sec. IV-C), introduce the FCIL
scenarios evaluated in this work (Sec. IV-D), and the metrics
to quantify NIDS capability to recognize and classify attacks
(Sec. IV-E).
A. Network Traffic of Cyber-Attacks
Datasets. For the experiments, we leverage 3 datasets
including IoT datasets, collected from 2019 onward—i.e.,
TON IoT [47], IoT-NID [48], and Edge-IIoTset [49].
They originally include five categories of attack [49]:
(i) ”(Distributed) Denial of Service—(D)DoS— which
includes attacks aiming at causing service disruptions;
(ii) ”Info Gathering, which covers attacks focused on
obtaining information from the victim; (iii) ”Man-in-theMiddle—MITM—addressing attacks involving the interception of communication; (iv) ”Injection, targeting the exploitation of vulnerabilities in applications or systems to introduce

malicious data or code; (v) ”Malware, covering uncategorized
attacks.
Within this category, various sub-categories can be identified based on the specific type of attack or the protocol
involved [16]. For instance, in the DoS category, most
datasets (except TON IoT) include UDP floods, while
HTTP and SYN floods are common across all. TON IoT
uniquely has a generic TCP flood; ACK and ICMP floods
are specific to IoT-NID and Edge-IIoTset, respectively.
Info gathering attacks mostly involve various scans: port
(Edge-IIoTset, IoT-NID, TON IoT), OS (IoT-NID,
Edge-IIoTset), vulnerability (Edge-IIoTset), and host
(IoT-NID). MITM attacks include ARP spoofing across
datasets, with ICMP and DHCP spoofing in TON IoT
and DNS spoofing in Edge-IIoTset. Injection attacks
cover SQL, XSS (TON IoT, Edge-IIoTset), and HTTP
injection (Edge-IIoTset). Lastly, malware includes bruteforce attempts on HTTP (TON IoT, Edge-IIoTset),
telnet (IoT-NID), FTP (TON IoT), plus backdoors and
ransomware in TON IoT and Edge-IIoTset. Concerning the physical testbed, IoT-NID leverages smart
devices and general-purpose hardware, while TON IoT and
Edge-IIoTset use hybrid setups with both physical and
emulated devices.
To ensure consistent labeling across all datasets, we
apply a rule-based preprocessing approach that refines
label granularity. The labeling scheme follows a standardized format of category-type(-subtype), promoting interpretability and structure. Defined categories
include dos (denial-of-service), infog (information gathering), mitm (man-in-the-middle), inject (injection),
and malwr (malware) [16]. Furthermore, the majority classes of all three datasets are subjected to random sampling to achieve a biflow number ranging from
10k to 100k. Notably, when analyzing the most and least
represented attack classes, the imbalance ratios—i.e., the ratio

3872

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

between the number of biflows of the most populous class
over the least one—are 400, 700, and 340 for TON IoT,
Edge-IIoTset, and IoT-NID, respectively. This indicates
a significant class imbalance—or skewness in the biflow
distribution—that persists even after undersampling, although
it has been partially mitigated. The distributions of the biflows,
resulting from the relabeling procedure, for the three considered datasets are shown in Fig. 2.2
DL Input. In this work, we consider 6 per-packet characteristics, i.e. Payload Length (PL), Inter Arrival Time (IAT),
Packet Direction (DIR), TCP Window Size (WIN), TCP Flags
(FLG), and Time To Live (TTL). To clarify, PL indicates
the packet length, IAT refers to the time interval between
successive packets, DIR denotes packet direction (0 for downstream, 1 for upstream), WIN represents the TCP window size
(set to 0 for UDP packets), FLG stands for the TCP flags
converted into a binary representation (ranging in [0, 255]),
and TTL means how many routers (hops) a packet can pass
through before being discarded. Fields such as IP addresses
and ports are deliberately excluded from the model’s training
to prevent unwarranted bias [50]. In the following experiments,
we use different feature sets: base—composed of PL, IAT,
DIR, and WIN—and extended—adding also FLG and TTL.
The latter features—i.e., TTL and FLG—have been shown to
carry valuable information for distinguishing between benign
and malicious traffic [51], and we aim to evaluate their utility
for intrusion detection in a FCIL setting when focusing on the
IoT ecosystem.
Last but not least, to support early detection of malicious
traffic, we extract features from the first N packets of each
biflow. Prior work [50], [52] has demonstrated that analyzing
per-packet features from just the initial 10 packets yields
strong classification results, with only marginal improvements
when incorporating the entire biflow [53]. Therefore, time
series data comprising the selected features from the first
10 packets of each biflow are extracted. For shorter biflows,
zero-padding is applied to keep the sequence length consistent.
B. DL Model Architecture
We use a 2D-CNN architecture—originally introduced in
[54] and widely adopted for both network Traffic Classification
(TC) [50] and intrusion detection [15]— with modifications
to support incremental learning. Importantly, our approach is
model-agnostic and can be integrated with other DL architectures without requiring structural changes.
The 2D-CNN is composed of two convolutional layers
(Conv2D) followed by pooling and normalization operations,
with a final Dense layer providing the classifier output
(i.e., a confidence vector). The architecture has 540k trainable
parameters and is fed with a (matrix-arranged) input x of
packets × fields for each biflow.
At each incremental step, the backbone of the network
remains structurally unchanged—i.e., no architectural modifications are introduced—while the head is expanded with
2 We leverage bidirectional flows (viz., biflows) as the traffic object. It
encompasses all packets that share the same quintuple (src ip, dst ip,
src port, dst port, and L4 proto), with interchangeable src and
dst.

TABLE II
FCIL S CENARIOS FOR THE T HREE D IFFERENT DATASETS ,
D ETAILED IN THE N UMBER OF Kold , Knew , AND C LIENTS

neurons for new attacks introduced that episode by federated
clients. Incremental training begins with the weights obtained
from the previous incremental episode—i.e., the base model
weights (θ0avg ) for the initial one. At the end of each episode,
all clients synchronize to a common model distributed by the
federated server.
Additionally, to assess the effectiveness of our solution
across a distinct DL architecture, we evaluate a hybrid model
combining 2D-CNN and LSTM layers—denoted HYBRID in
the following sections [54]. The network operates on the same
input representation used by the 2D-CNN.
C. Upper Bound Approaches
To recap, FCIL introduces the incremental learning
paradigm into a federated setup. Therefore, to measure separately the performance loss introduced by each challenge—i.e.,
decentralized data and need to update NIDS to cope with
evolving threats—, we consider two different upper bounds:
(i) Scratch, meaning that the model is trained from-scratch
with all the data in a centralized fashion and no incremental
learning, and (ii) centralized CIL, which involves an incremental training performed in a centralized setup—i.e., the new
classes of the considered scenario are added on a single client.
While Scratch uses all the data at a single point to
perform training from scratch, centralized CIL assumes that
each client has access to Dmem for old classes along with the
traffic data for the new classes it intends to add.
D. FCIL Scenarios
For the experiments, we define different federated incremental scenarios. In detail, a scenario is compactly referred to as
h|Kold | + |Knew |, N i where |Kold | and |Knew | are the number of
old and new classes, respectively, and N the number of clients
in the federated network. Furthermore, in both scenarios S 1 /S 2
we assume that each federated client observes a (different)
new attack at a given time and cooperates with other clients
to incorporate all the attacks seen by the group (i.e. in such
a case it holds |Knew | = N ). Additionally, all clients in
the federated network adhere to a common agreement on
the number of communication rounds (R) to be performed.
In each communication round, clients transmit their locally
trained models to the server, which aggregates them into a
global model and redistributes it to all clients.
The FCIL scenarios used for the experiments are reported in
Tab. II, detailing for each dataset the number of old and new

CARILLO et al.: FEDERATED AND INCREMENTAL NETWORK INTRUSION DETECTION SYSTEM

3873

classes and the number of clients in the federated network.
We consider federations of 2 and 5 clients, modeling realistic
cross-silo settings in which groups of IoT devices (e.g., organizations or edge clusters) collaboratively train without sharing
raw data, rather than large-scale cross-device FL. Across all
scenarios, Kold always includes the benign class, whereas
Knew contains only attack classes, reflecting the decentralized
emergence of new attacks.
E. Evaluation Metrics
In this work, we evaluate federated and incremental NIDS
from two complementary perspectives: (i) their ability to
classify network traffic by identifying both benign device
activity and specific attack types, and (ii) their effectiveness
in distinguishing legitimate traffic from malicious traffic.
To assess attack detection and recognition capabilities, we
leverage F1 Score (briefly, F1) as performance metric [34].
It is computed as the harmonic mean of the per-class precision
and recall and then we obtain its macro version by averaging
the per-class metrics over all the classes, namely
1 X 2 · Precisioni · Recalli
,
(7)
F1 Score(θ, K) =
Precisioni + Recalli
|K|
i∈K

where K denotes the generic class set and θ a generic model
(learned from-scratch or in federated incremental fashion).
To focus on NIDS detection capabilities, we use the partial
area under the curve (pAUC), which emphasizes performance
at low False Positive Rate (FPR). The pAUC is defined as:
Z pu
TPR(fpr) dfpr
(8)
pAUC =
p`

where p` = 0 and pu = 0.01, i.e., we compute the area under
the ROC—defined by True Positive Rate (TPR)—up to 1%
FPR, ensuring relevance for real-world NIDS conditions.
To obtain insights into both catastrophic forgetting and
intransigence phenomena (due to the incremental learning
process), we break down both the considered metrics by the
subset of classes Kold , Knew , and Kall , obtaining for a generic
metric X the following sub-metrics: X old , X new , and X all .
To quantify a model’s gap from upper bound approaches,
we define drop from scratch (Drop-Scratch) and drop from
CIL (Drop-CIL) metrics measuring the difference in F1 and
PAUC between FCIL NIDS and the upper bounds.

Fig. 3. FCIL performance on TON IoT in the S1 scenario with the base
feature set. Different line styles distinguish approaches according to the
mitigation strategies employed.

rate of 0.1, a learning rate decay factor of 3, and a minimum
learning rate of 10−4 . For memory-based CIL approaches,
25 biflows per each Kold are selected [38]. In our experiments,
we explore various synchronization frequencies by setting
R = {4, 10, 20, 40, 100, 200}. Each client conducts a total of
200 local training epochs, sharing its model with the server
every E = 200/R epochs. For each configuration, we test
10 seeds, corresponding to 10 distinct (7 ÷ 3) train-test splits.
Results are shown as the average across the incremental runs
using 10 different seeds, each adding different new classes.
The rest framework leverages NumPy4 and Pandas5 for data
management and pre-processing, PyTorch6 for training and
evaluating NIDS, and Matplotlib7 and Seaborn8 to plot results.

F. Implementation Details
In this section, we provide the implementation details for
the FCIL framework used in this work. Specifically, we
extend a Python-based framework—i.e., FACIL3 — to handle
federated learning training. In detail, we devise a federated
server responsible for aggregating the models and coordinating
and communicating with the clients during the local training
procedure CIL. Additionally, we modify this framework to
train multiple clients simultaneously, with each adding a new
attack. The hyperparameters used for the training phase are the
following: 200 epochs with patience of 20, an initial learning

V. E XPERIMENTAL R ESULTS
We begin by analyzing performance in a few-client setting,
optimizing FCIL along two axes: feature set and FL algorithm
(Sec. V-A). Then, we scale to a larger number of clients
(Sec. V-B), compare FCIL with training from scratch and
centralized CIL (Sec. V-C). Furthermore, we evaluate the
4 https://numpy.org/
5 https://pandas.pydata.org/
6 https://pytorch.org/
7 https://matplotlib.org/

3 https://github.com/mmasana/FACIL

8 https://seaborn.pydata.org/

3874

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

TABLE III
FCIL P ERFORMANCE ON TON IoT IN THE S1 S CENARIO W ITH E XPANDED F EATURE S ET. R ESULTS A RE S HOWN AS THE D IFFERENCE OF F1 W. R . T.
THE BASE F EATURE S ET. F URTHERMORE , T HEY A RE B ROKEN D OWN BY THE N UMBER OF S YNCHRONIZATION ROUNDS P ERFORMED AND THE
S ET OF C LASSES . G REEN B OLDFACE T EXT I NDICATES I MPROVEMENT OVER THE BASE S ET OF F EATURES , W HILE R ED O NE R EFERS TO
D ECAY IN P ERFORMANCE . G RAY BACKGROUND H IGHLIGHTS FOR E ACH A PPROACH THE R AT W HICH THE B EST I MPROVEMENT
OVER THE BASE F EATURE S ET I S O BTAINED , W HILE THE G REEN O NES H IGHLIGHT THE
B EST A PPROACH AND THE B EST R FOR THE C ONSIDERED S ETUP

generalizability of our FCIL solution across different DL
architectures (Sec. V-D) and examine the impact of IID attack
data among clients (Sec. V-E). Lastly, we assess real-world
applicability, focusing on cross-network generalization and
few-sample learning (Sec. V-F).
A. Few-Client Scenario
Hereinafter, we evaluate FCIL performance in the S1 scenario using TON IoT. Each paragraph answers a key research
question, stated as its title.
How effective is FedAvg with a base set of features?
In response, we evaluate all CIL methods combined with
FedAvg—using base feature set as input (viz., PL, IAT, DIR,
and WIN). Results in Fig. 3 show that performance on Kall
closely mirrors that of Kold , largely due to the imbalanced
scenario with 10 base classes and only 2 new ones (attacks).
Performance trends vary across methods, depending on
their CIL-focused mitigation strategies. Using only rehearsal
(i.e., FT-Mem), F1 generally improves with more rounds,
peaking at R = 200 (i.e., 65% F1all ). In contrast, iCaRL+
(combining rehearsal and distillation) reaches its best performance earlier, at R = 40 (≈54% F1all /F1old and ≈50% F1new ).
As FT-Mem, iCaRL+ struggles at low R but benefits from
higher rounds.
CIL methods using all three mitigation strategies behave
differently. Their performance on Kold drops as R increases.
For Knew , outcomes depend on the bias correction strategy: (i)
BiC—i.e., with a single shared correction layer for all new
classes—achieve peak F1new scores at R = 20 (≈56%) and
(ii) BiC+ reaches its highest F1new (≈ 64%) at R = 10.
MEMENTO behaves like BiC, peaking at R = 40. But
MEMENTO+ follows a different pattern: performance steadily
rises with more rounds, reaching its best F1new (≈ 71%) at
R=200.

Does expanded feature set boost performance? Then, we
evaluate the impact of using an expanded feature set. The
results are reported in Tab. III, highlighting the performance
improvement in green (resp. decay in red) obtained using the
expanded set of features over the base one.
Generally speaking, performance on Kold highly benefits
from the use of the expanded set of features, with FT-Mem
obtaining the highest gain w.r.t. all the other approaches.
Notably, it improves at most by ≈14% at R=20. Performance
trends on Kall closely reflect those observed for old classes.
On the other hand, Knew presents more unstable trends.
Specifically, FT-Mem, BiC, and BiC+ demonstrate a generally
positive trend across almost all synchronization values, with
improvements of up to 15%. In contrast, MEMENTO and
MEMENTO+ experience a critical drop at R=40, losing 16%
and 8%, respectively, compared to the base feature set.
It is worth noting that iCaRL+ exhibits a distinctive
trend. Its performance improves steadily by up to ≈ 8%
as the synchronization value increases to R = 20, but
beyond this point, it experiences a sharp decline, dropping to around −18%. This behavior may stem from the
iCaRL+ loss becoming less effective at higher synchronization intervals, potentially causing forgetting or training
instability.

What is the impact of different FL algorithms on performance? Lastly, we evaluate the performance of different
FL algorithms, focusing on the top-2 CIL approaches—i.e.,
BiC+ and MEMENTO+ —and using the expanded feature set as input. Results of this analysis are shown in
Fig. 4.
Notably, FedProx shows significant improvements over
FedAvg for both BiC+ and MEMENTO+ , especially with
a low number of synchronizations. As R increases, performance of FedAvg and FedProx converges with both scoring
between 74% and 76% F1all for BiC+ and MEMENTO+ ,

CARILLO et al.: FEDERATED AND INCREMENTAL NETWORK INTRUSION DETECTION SYSTEM

3875

TABLE IV
FCIL P ERFORMANCE ON TON IoT IN THE S2 S CENARIO U SING THE
E XPANDED F EATURE S ET. F OR E ACH C OMBINATION , THE R ESULTS
H IGHLIGHT THE B EST S YNCHRONIZATION VALUE , C ORRESPOND ING TO THE H IGHEST ACHIEVED F1all

Fig. 4. Comparison of different FL approaches for TON IoT with expanded
feature set in the S1 scenario.

respectively. Performance convergence is due to the improvement of FedAvg over FedProx on Kold with higher R, while
FedProx delivers better performance on Knew , especially
with MEMENTO+ . However, both approaches exhibit a declining trend on Kold and Knew performance as R increases.
On the other hand, FedDyn shows lower performance for
low R, while obtaining the highest F1 for R ≥ 20. This
behavior can be attributed to the dynamic regularization in
FedDyn, which corrects for client drift by incorporating a
linear term related to the global model. Similar to FedAvg,
as R increases, FedDyn shows improved F1old , peaking at
R = 20, and F1new , with best value occurring at R = 100
(resp. R = 20) for MEMENTO+ (resp. BiC+ ).

B. Many-Client Scenario
In this section, we evaluate FCIL approaches in the S2
scenario for the TON IoT dataset with the expanded feature
set. Table IV reports the best trade-off achieved for each
combination of CIL and FL at specific values of R. It is worth

noting that having more clients with new classes makes this
scenario more challenging, as more knowledge needs to be
integrated into the model at each synchronization. Overall, a
few synchronization rounds significantly hinder new knowledge acquisition, highlighting the need for frequent updates
as client number and new classes grow.
While no strict trends emerge, F1new generally increases
and F1old decreases as R grows. Similar to S1 , FedDyn
performs notably worse at R = {4, 10}, whereas FedProx
consistently leads at higher R, followed by FedDyn. Notably,
FedProx preserves old knowledge comparably to FedAvg
and FedDyn, while achieving better F1new , making it the best
trade-off among the three.

C. Wrap-up of Results: In this section, we compare the
performance of the top-performer FCIL approach against the
upper bound Scratch baseline and centralized CIL training.
Specifically, we evaluate performance in solving two relevant
NIDS tasks: (i) bMD—i.e., distinguishing among legitimate
and malicious traffic (all attacks as one class); (ii) AC—i.e.,
fine-grained classification of malicious traffic into different
attack types. Table V summarizes the results for the two
scenarios, across all three evaluated datasets and the corresponding tasks discussed above.
Considering scenario S1 , the best FCIL approach
(i.e., MEMENTO+ with FedProx at R
=
10)
consistently outperforms the best centralized CIL method
(i.e., MEMENTO) across bMD/AC tasks for both TON IoT
and Edge-IIoTset datasets. However, despite these
improvements, our solution still lags behind the Scratch
baseline, with performance gaps reaching up to 3% in bMD
and 8% in AC. In contrast, for the IoT-NID dataset, the
CIL method slightly outperforms the FCIL one, showing
improvements of + 1% in PAUCAll and + 2% in F1all for AC.
Moreover, the gap between our method and Scratch is even
more pronounced for IoT-NID, with differences of up to 15%

3876

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

TABLE V
S UMMARY OF P ERFORMANCE FOR THE B EST FCIL A PPROACH —I N C ENTRALIZED AND D ISTRIBUTED FASHION — AND S C R A T C H , ACROSS S CENARIOS
( I . E ., S 1 AND S 2 ) AND DATASETS ( I . E ., TON IoT, IoT-NID, AND Edge-IIoTset).P ERFORMANCE I S R EPORTED AS A BSOLUTE VALUE AND
D ROP W. R . T. S C R A T C H AND CIL A PPROACHES . R ED ( RESP. G REEN ) T EXT H IGHLIGHTS THE G AP
( RESP. I MPROVEMENT ) C OMPARED TO U PPER B OUNDS ( I . E ., S C R A T C H AND CIL)

TABLE VI
M ULTICLASS M ISUSE D ETECTION P ERFORMANCE FOR THE B EST FCIL
A PPROACH , O BTAINED U SING THE HYBRID A RCHITECTURE [54],
C OMPARED BY U PPER B OUNDS — I . E ., S C R A T C H , AND CIL

in AC. The ROC curves in Fig. 5 reveal a notable decline
in TPR for the bMD task when compared to the Scratch
baseline—particularly at low false positive rates (FPR≤1%).
This drop affects both CIL and FCIL approaches, which
exhibit comparable patterns. The degradation is especially
severe for Knew , as reflected in the steeper decline of the ROC
curves at low FPR values. Notably, MEMENTO+ consistently
outperforms MEMENTO, achieving higher TPR across both
Kold and Kall for equivalent FPR thresholds.
In scenario S2 , we observe a greater ability of the FCIL
approach to retain previously learned knowledge compared
to the CIL counterpart, as reflected in consistently higher
performance across all class-level metrics. However, FCIL
shows notable difficulty in incorporating new attack classes,

with significant performance drops relative to CIL—reaching
up to 13% for Edge-IIoTset in the AC task. Increasing the
number of clients further degrades performance for both FCIL
and CIL, while also amplifying the gap to the Scratch baseline. For TON IoT and Edge-IIoTset, the performance
drops nearly double, peaking at 32% in DropF1New and 17% in
DropF1All . In contrast, for IoT-NID, the degradation remains
comparable to that observed in S1 , with the DropF1New in the
AC task even slightly lower than in the previous scenario.

D. Generalization Across DL Architectures
To assess the architecture-independent nature of our solution, we evaluate the mMD performance for TON IoT when
using the HYBRID network. Table VI shows results both for
few-client (S1 ) and many-client (S2 ) scenarios, additionally
comparing FCIL with upperbound approaches—namely, CIL
and Scratch.
Results are consistent with those reported in Tab. V for
TON IoT. Notably, the FCIL approach consistently outper-

CARILLO et al.: FEDERATED AND INCREMENTAL NETWORK INTRUSION DETECTION SYSTEM

Fig. 5. ROC curves for (a) Scratch, (b) MEMENTO, and (c) MEMENTO+
in the S1 scenario on the TON IoT dataset. Curves are averaged across all
the seeds. The x-axis is displayed in a symlog scale for improved visibility.

forms centralized CIL when using the HYBRID architecture.
In the S1 scenario, FCIL yields improvements of 5% F1 on
previously seen classes and 12% F1 on new classes, for an
overall gain of + 7% in F1all . Similarly, in S2 , FCIL better
retains prior knowledge (+ 12% F1) and incorporates new
classes more effectively (+ 8% F1), resulting in an average
performance increase of 11% F1 over centralized CIL.
Despite these advantages, FCIL remains below the ideal
Scratch reference, particularly as the number of clients
grows. In S1 , it incurs a DropF1New of 16% and a DropF1Old
of 5%, whereas in S2 these losses rise to 12% and 28%,
corresponding to F1all reductions of 7% and 16%, respectively.

E. NIDS Under New IID Data
In this section, we evaluate the performance of FCIL
NIDS under an IID data, focusing on a few-client scenario
where both clients encounter the same two novel attacks, but
with distinct biflows. Results of this analysis are reported in
Fig. 6 for the different FL algorithms, along with the best
FCIL configuration in the non-IID setup in which each client
encounters a disjoint new attack, obtained in Sec. V-A.
Similarly to the non-IID configuration, best results are
yielded also in the IID setup with low R, then performance decreases when the communication rate exceeds
a given threshold. This behavior suggests that, under

3877

Fig. 6. Comparison of different FL approaches for TON IoT on new IID
data, alongside the best non-IID configuration.

IID conditions, additional communication rounds provide
diminishing returns once the models have sufficiently
converged.
Comparing FL approaches, FedProx and FedDyn consistently outperform FedAvg across most settings. This indicates
that regularization-based approaches remain beneficial even
when client data are IID. Notably, FedDyn generally achieves
the best or near-best performance for intermediate values
of R (i.e., R = 20), highlighting its robustness in maintaining
previously-learned knowledge, while FedProx turns out to
be the best with low R—namely, R = 4.
Across all methods, performance on the Knew split is
systematically lower than on Kold , regardless of R. This gap
reflects the inherent difficulty of CIL (even in the absence of
data heterogeneity) and suggests that catastrophic interference
with newly-introduced attacks remains a central challenge.
Nevertheless, moving from a non-IID to an IID setting
yields a substantial benefit for learning new classes, with the
best IID configuration—i.e., FedProx at R = 4—improves
performance on Knew by ≈ 10% F1 compared to the best
non-IID result—i.e., FedProx at R = 10. This highlights
the impact of data distribution on plasticity and confirms
that data homogeneity significantly alleviates, though does
not eliminate, the challenges associated with incremental class
acquisition.

3878

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

TABLE VII
B INARY D ETECTION C APABILITIES IN S1 AS PAUC All FOR E ACH
hsource, T argeti PAIR FOR THE B EST FCIL S OLUTION AND THE B EST
CIL O NE ( IN BRACKETS ). G REEN BACKGROUND H IGHLIGHTS
THE PAIRS FOR W HICH source = target

F. NIDS in the Wild: Practical Challenges
In this section, we analyze some practical challenges
of NIDS when deployed in real-world scenarios: (i) capability of generalizing across networks and (ii) ability to
detect 0-day attacks with only a limited number of biflows
available.
How well do FCIL NIDS generalize across diverse
networks? In response, we separately evaluate the detection
and classification performance of the best-performing FCIL
model when deployed across different networks, and compare
it with the best CIL model under the same conditions. Specifically, we report the results for the bMD task in Tab. VII,
while Fig. 7 shows the AC performance when FCIL NIDS
is trained on TON IoT and tested with network traffic from
Edge-IIoTset and IoT-NID. Other combinations are not
shown for brevity.
Specifically, Tab. VII clearly shows a decline in detection
performance when the NIDS is evaluated on a different
network from the one it was trained on. While intradataset models achieve ≥ 92% PAUCAll , performance drops
significantly in cross-dataset setup—reaching at most 75%
PAUCAll (for hTON IoT,Edge−IIoTset i), with other
cases falling below 60% PAUCAll . In most of the combinations, the FCIL approach outperforms the CIL baseline in
both intra-dataset and cross-dataset scenarios, likely due to
the decentralized training and different client-specific data
distributions.
Similarly, the overall performance on the AC task
remains unsatisfactory. We observe distinct behavioral patterns between the FCIL and CIL NIDS (see Fig. 7).
Specifically, when using TON IoT as the source dataset
and Edge-IIoTset as the target, the FCIL setup shows a
clear bias toward certain attack classes—such as dos-http,
inject-sql, and malwr-backd-tcp—which are also
the most frequent in the source dataset (Fig. 7a).
In contrast, the CIL setup exhibits even more pronounced bias, particularly toward the dos-tcp and
malwr-brutef-http classes (Fig. 7b). When IoT-NID
is used as the target dataset, the trend reverses. Both
approaches show a clear prediction bias toward specific attack
classes—such as dos-tcp-syn, infog-scan-port,
malwr-ransomware, and mitm-arpspoof (Fig. 7c).
The CIL setup displays a similar bias, though it is
less pronounced compared to the FCIL counterpart (Fig.
7d). Similar results are observed across the other datasets
and scenarios; their confusion matrices are omitted for
brevity.

Fig. 7. Confusion matrices for NIDS trained on TON IoT (source dataset)
and evaluated on Edge-IIoTset (top row) and IoT-NID (bottom row) in
S1 . Gray-shaded rows and columns indicate classes that are absent in the
target or source dataset.

Can FCIL NIDS detect new 0-day attacks with just a
few samples? In this analysis, we assess the ability of a FCIL
NIDS to incorporate new attacks while retaining knowledge
of previously learned ones, under a scenario characterized
by a scarcity of new attack samples. Specifically, we constrain the number of biflows available for each new attack
class to fixed values: 15, 25, 50, 100, 200. For this analysis,
we select for the few-shot training the seed that yields the
best FCIL performance in the full-data setup (+ inf). For
each setting, samples are randomly drawn from the complete
dataset corresponding to that class. To ensure robustness and
variability in sample selection, each experiment is repeated
10 times, with results expressed as the average across the
repetitions.
Figure 8 compares the performance obtained by the best
FCIL solution—under few-shot conditions (15 to 200 samples)

CARILLO et al.: FEDERATED AND INCREMENTAL NETWORK INTRUSION DETECTION SYSTEM

Fig. 8.
Performance under few-shot conditions (ranging from
15 to 200 samples) and with all samples (+∞) for the best FCIL
method and Scratch, in both few-client and many-client scenarios using
the best seed.

and full data (+ inf)—and Scratch for the three considered datasets in the few- and many-client scenarios. In S1 ,
performance on Kold is only slightly impacted by limited
sample availability. Interestingly, performance on Knew is often
comparable to—or even better than—the full-sample setting,
except for Edge-IIoTset, where a notable drop is observed
as samples decrease. This may be due to higher sample
variability or greater overlap in new attack fingerprints for
the selected seed in Edge-IIoTset.
Similarly, in S2 , Kold performance remains consistent
between the two different settings. However, classification
on Knew improves for IoT-NID and Edge-IIoTset, while
TON IoT scores similarly to the full-sample setting.

data across deployments could improve detection coverage,
privacy concerns make this approach impractical.
In this work, we bridge the gap between CIL—enabling
continuous learning—and FL—leveraging distributed data for
training—by proposing FCIL, combining both approaches to
design an adaptable, collaboratively trained NIDS. Our results
show that FCIL methods effectively retain prior knowledge,
especially leveraging TCP flags and time-to-live as input, but
face challenges integrating new attacks.
Overall, MEMENTO+ combined with FedProx achieves the
best results in both few- and many-client settings. In the
former, fewer synchronization rounds (R = 10) suffice for
integrating new classes, while larger networks require more
rounds (R = 100) to accommodate new knowledge. Under
these conditions, MEMENTO+ attains 79% and 75% F1all in the
few- and many-client scenarios on TON IoT, respectively.
Generally speaking, FCIL shows advantages over CIL in
smaller networks, though it does not reach the performance of
training-from-scratch. As the number of clients grows, FCIL
better preserves existing knowledge but faces increased difficulty in learning new attacks, leading to larger performance
drops.
In addition, we evaluate the NIDS in a real-world
deployment scenario, assessing both their (i) generalization
capabilities and (ii) their ability to learn from limited samples.
Notably, deploying a NIDS in a different network environment significantly reduces its detection and classification
performance. However, the FCIL NIDS consistently outperforms its CIL counterpart, demonstrating greater resilience
to network shifts. On the other hand, in few-shot settings,
FCIL NIDS achieves performance comparable to the full-data
scenario—obtaining similar performance on old classes and
sometimes even outperforming it on new ones.
Our future directions include (a) enhancing CIL approaches
for better integration of new attacks in federated settings,
(b) advancing personalization to balance local adaptation
with global knowledge, (c) strengthening privacy protections,
(d) reducing communication overhead, (e) improving robustness against adversarial threats, and ( f ) including federated
domain-incremental learning.
R EFERENCES
[1]

[2]
[3]

VI. C ONCLUSION
Guaranteeing security is particularly challenging in IoT
environments, where diverse devices continuously collect and
exchange data. In this domain, ML- and DL-based NIDS
are crucial for defending against cyberattacks. However, the
dynamic nature of IoT networks—characterized by frequent
device churn and heterogeneity—leads to a broader and more
exposed attack surface. New attacks may emerge frequently,
making NIDS models quickly outdated and requiring the
ability to learn new threats incrementally. Furthermore, attack
traffic can vary significantly across networks. While sharing

3879

[4]
[5]
[6]
[7]
[8]

(2024). Microsoft Digital Defense Report: 600 Million Cyberattacks
Per Day Around the Globe. [Online]. Available: https://
news.microsoft.com/en-cee/2024/11/29/microsoft-digital-defensereport-600-million-cyberattacks-per-day-around-the-globe/
Cisco Systems.(2024). Detecting Zero-Days With SnortML. [Online].
Available: https://www.cisco.com/c/en/us/products/collateral/security/
firewalls/detecting-zero-days-with-snortml-wp.html
M. Antonakakis et al., “Understanding the Mirai botnet,” in Proc. 26th
USENIX Secur. Symp. (USENIX Security), 2017, pp. 1093–1110.
B. Zhao et al., “A large-scale empirical analysis of the vulnerabilities
introduced by third-party components in IoT firmware,” in Proc. 31st
ACM SIGSOFT Int. Symp. Softw. Test. Anal., Jul. 2022, pp. 442–454.
G. Apruzzese, L. Pajola, and M. Conti, “The cross-evaluation of machine
learning-based network intrusion detection systems,” IEEE Trans. Netw.
Service Manage., vol. 19, no. 4, pp. 5152–5169, Dec. 2022.
S. Agrawal et al., “Federated learning for intrusion detection system: Concepts, challenges and future directions,” Comput. Commun.,
vol. 195, pp. 346–361, Nov. 2022.
E. M. Campos et al., “Evaluating federated learning for intrusion
detection in Internet of Things: Review and challenges,” Comput. Netw.,
vol. 203, Feb. 2022, Art. no. 108661.
H. Zhang, J. Ye, W. Huang, X. Liu, and J. Gu, “Survey of federated
learning in intrusion detection,” J. Parallel Distrib. Comput., vol. 195,
Jan. 2024, Art. no. 104976.

3880

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

[9]

[32] Q. Li et al., “A survey on federated learning systems: Vision, hype and
reality for data privacy and protection,” IEEE Trans. Knowl. Data Eng.,
vol. 35, no. 4, pp. 3347–3366, Apr. 2023.
[33] P. Kairouz and H. B. McMahan, “Advances and open problems in
federated learning,” Found. Trends Mach. Learn., vol. 14, nos. 1–2,
pp. 1–210, Jun. 2021.
[34] G. Bovenzi et al., “Benchmarking class incremental learning in deep
learning traffic classification,” IEEE Trans. Netw. Service Manage.,
vol. 21, no. 1, pp. 51–69, Feb. 2024.
[35] G. Bovenzi et al., “A first look at class incremental learning in deep
learning mobile traffic classification,” 2021, arXiv:2107.04464.
[36] Y. Wu et al., “Large scale incremental learning,” in Proc. CVPR, 2019,
pp. 374–382.
[37] R. Carillo, F. Cerasuolo, G. Bovenzi, D. Ciuonzo, and A. Pescapè,
“Explainable federated class incremental learning for encrypted network
traffic classification,” Comput. Netw., vol. 269, Sep. 2025, Art. no.
111448.
[38] F. Cerasuolo et al., “MEMENTO: A novel approach for class incremental
learning of encrypted traffic,” Comput. Netw., vol. 245, May 2024, Art.
no. 110374.
[39] D.-W. Zhou, Q. Wang, Z. Qi, H.-J. Ye, D. Zhan, and Z. Liu, “Classincremental learning: A survey,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 46, no. 12, pp. 9851–9873, Jul. 2024.
[40] J. Zhang, F. Li, F. Ye, and H. Wu, “Autonomous unknown-application
filtering and labeling for DL-based traffic classifier update,” in Proc.
IEEE Conf. Comput. Commun., Jul. 2020, pp. 397–405.
[41] H. Chen, S. Huang, D. Zhang, M. Xiao, M. Skoglund, and H. V. Poor,
“Federated learning over wireless IoT networks with optimized communication and resources,” IEEE Internet Things J., vol. 9, no. 17,
pp. 16592–16605, Sep. 2022.
[42] X. Gao, X. Yang, H. Yu, Y. Kang, and T. Li, “Fedprok: Trustworthy
federated class-incremental learning via prototypical feature knowledge
transfer,” in Proc. CVPR, 2024, pp. 4205–4214.
[43] J. Dong, H. Li, Y. Cong, G. Sun, Y. Zhang, and L. Van Gool, “No
one left behind: Real-world federated class-incremental learning,” IEEE
Trans. Pattern Anal. Mach. Intell., vol. 46, no. 4, pp. 2054–2070, Apr.
2024.
[44] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. Y. Arcas,
“Communication-efficient learning of deep networks from decentralized data,” in Proc. 20th Int. Conf. Artif. Intell. Statist., vol. 54,
A. Singh and J.Zhu., Eds., Fort Lauderdale, FL, USA, 2017,
pp. 1273–1282.
[45] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith,
“Federated optimization in heterogeneous networks,” in Proc. 3rd Mach.
Learn. Syst. Conf., 2020, pp. 429–450.
[46] D. A. E. Acar, Y. Zhao, R. M. Navarro, M. Mattina, P. N. Whatmough,
and V. Saligrama, “Federated learning based on dynamic regularization,”
2021, arXiv:2111.04263.
[47] T. Booij, I. Chiscop, E. Meeuwissen, N. Moustafa, and F. Den
Hartog, “Ton IoT: The role of heterogeneity and the need for
standardization of features and attack types in IoT network intrusion datasets,” IEEE Internet Things J., vol. 9, no. 1, pp. 485–496,
Jan. 2022.
[48] H. Kang et al., “IoT network intrusion dataset,” IEEE dataport, Tech.
Rep., 2019, doi: 10.21227/q70p-q449.
[49] M. A. Ferrag, O. Friha, D. Hamouda, L. Maglaras, and
H. Janicke, “Edge-IIoTset: A new comprehensive realistic cyber
security dataset of IoT and IIoT applications for centralized
and federated learning,” IEEE Access, vol. 10, pp. 40281–40306,
2022.
[50] G. Aceto, D. Ciuonzo, A. Montieri, and A. Pescape, “Mobile encrypted
traffic classification using deep learning: Experimental evaluation,
lessons learned, and challenges,” IEEE Trans. Netw. Service Manage.,
vol. 16, no. 2, pp. 445–458, Jun. 2019.
[51] W. John and S. Tafvelin, “Analysis of internet backbone traffic and
header anomalies observed,” in Proc. 7th ACM SIGCOMM Conf.
Internet Meas., Oct. 2007, pp. 111–116.
[52] L. Peng, B. Yang, and Y. Chen, “Effective packet number for early stage
internet traffic identification,” Neurocomputing, vol. 156, pp. 252–267,
May 2015.
[53] M. Wang, N. Yang, and N. Weng, “Exploring the impact of early
detection on DL-based NIDSs models,” in Proc. IEEE 14th Annu.
Ubiquitous Comput., Electron. Mobile Commun. Conf. (UEMCON), Oct.
2023, pp. 0684–0691.
[54] M. Lopez-Martin, B. Carro, A. Sanchez-Esguevillas, and J. Lloret,
“Network traffic classifier with convolutional and recurrent neural networks for Internet of Things,” IEEE Access, vol. 5, pp. 18042–18050,
2017.

M. Data and M. Aritsugi, “An incremental learning algorithm on
imbalanced data for network intrusion detection systems,” in Proc. 10th
Int. Conf. Comput. Commun. Manage., Jul. 2022, pp. 191–199.
[10] C. Oikonomou, I. Iliopoulos, D. Ioannidis, and D. Tzovaras, “A multiclass intrusion detection system based on continual learning,” in Proc.
IEEE Int. Conf. Cyber Secur. Resilience (CSR), Jul. 2023, pp. 86–91.
[11] Z. Song et al., “Iˆ{2} RNN: An incremental and interpretable recurrent neural network for encrypted traffic classification,” IEEE Trans.
Dependable Secure Comput., early access, Feb. 28, 2024, doi: 10.1109/
TDSC.2023.3245411.
[12] L. Du, Z. Gu, Y. Wang, L. Wang, and Y. Jia, “A few-shot classincremental learning method for network intrusion detection,” IEEE
Trans. Netw. Service Manage., vol. 21, no. 2, pp. 2389–2401, Apr. 2024.
[13] Y. Wang and S. Cao, “A two-stage class incremental learning approach
for network intrusion detection,” in Proc. GLOBECOM - IEEE Global
Commun. Conf., Dec. 2024, pp. 2353–2358.
[14] X. Xu et al., “Advancing malware detection in network traffic with
self-paced class incremental learning,” IEEE Internet Things J., vol. 11,
no. 12, pp. 21816–21826, Jun. 2024.
[15] F. Cerasuolo, G. Bovenzi, D. Ciuonzo, and A. Pescapè, “Attack-adaptive
network intrusion detection systems for IoT networks through class
incremental learning,” Comput. Netw., vol. 263, May 2025, Art. no.
111228.
[16] F. Cerasuolo, G. Bovenzi, D. Ciuonzo, and A. Pescapè, “Adaptable,
incremental, and explainable network intrusion detection systems for
Internet of Things,” Eng. Appl. Artif. Intell., vol. 144, Mar. 2025, Art.
no. 110143.
[17] V. Rey, P. M. S. Sánchez, A. H. Celdrán, and G. Bovet, “Federated
learning for malware detection in IoT devices,” Comput. Netw., vol. 204,
Feb. 2022, Art. no. 108693.
[18] Z. Tang, H. Hu, and C. Xu, “A federated learning method for network intrusion detection,” Concurrency Comput., Pract. Exper., vol. 34,
no. 10, p. 6812, May 2022.
[19] O. Friha, M. A. Ferrag, L. Shu, L. Maglaras, K.-K.-R. Choo, and
M. Nafaa, “FELIDS: Federated learning-based intrusion detection system for agricultural Internet of Things,” J. Parallel Distrib. Comput.,
vol. 165, pp. 17–31, Jul. 2022.
[20] J. Li, X. Tong, J. Liu, and L. Cheng, “An efficient federated learning
system for network intrusion detection,” IEEE Syst. J., vol. 17, no. 2,
pp. 2455–2464, Jun. 2023.
[21] M. J. Idrissi et al., “Fed-ANIDS: Federated learning for anomaly-based
network intrusion detection systems,” Expert Syst. Appl., vol. 234, Dec.
2023, Art. no. 121000.
[22] M. H. Bhavsar, Y. B. Bekele, K. Roy, J. C. Kelly, and D. Limbrick, “FLIDS: Federated learning-based intrusion detection system using edge
devices for transportation IoT,” IEEE Access, vol. 12, pp. 52215–52226,
2024.
[23] M.-Y. Zhu, Z. Chen, K.-F. Chen, N. Lv, and Y. Zhong, “Attention-based
federated incremental learning for traffic classification in the Internet of
Things,” Comput. Commun., vol. 185, pp. 168–175, Mar. 2022.
[24] R. R. dos Santos, E. K. Viegas, A. O. Santin, and P. Tedeschi,
“Federated learning for reliable model updates in network-based intrusion detection,” Comput. Secur., vol. 133, Oct. 2023, Art. no. 103413.
[25] D. Jin, S. Chen, H. He, X. Jiang, S. Cheng, and J. Yang, “Federated
incremental learning based evolvable intrusion detection system for zeroday attacks,” IEEE Netw., vol. 37, no. 1, pp. 125–132, Jan. 2023.
[26] Z. Jin, J. Zhou, B. Li, X. Wu, and C. Duan, “FL-IIDS: A novel federated
learning-based incremental intrusion detection system,” Future Gener.
Comput. Syst., vol. 151, pp. 57–70, Feb. 2024.
[27] J. Mao, Z. Wei, B. Li, R. Zhang, and L. Song, “Toward ever-evolution
network threats: A hierarchical federated class-incremental learning
approach for network intrusion detection in IIoT,” IEEE Internet Things
J., vol. 11, no. 18, pp. 29864–29877, Sep. 2024.
[28] Z. Zhang et al., “Federated continual representation learning for evolutionary distributed intrusion detection in industrial Internet of Things,”
Eng. Appl. Artif. Intell., vol. 135, Sep. 2024, Art. no. 108826.
[29] N. H. Quyen, N. V. Hoang, P. T. Duy, and V.-H. Pham, “FI-IDS: A federated incremental learning approach for intrusion detection system,” in
Proc. Int. Conf. Adv. Technol. Commun. (ATC), Oct. 2024, pp. 432–437.
[30] H. A. Tran, H. T. T. Binh, and A. Mellouk, “Federated learning for
network traffic classification: A knowledge consolidation approach,”
IEEE Trans. Netw. Sci. Eng., vol. 13, pp. 797–814, Jul. 2026.
[31] M. Masana, X. Liu, B. Twardowski, M. Menta, A. D. Bagdanov, and
J. van de Weijer, “Class-incremental learning: Survey and performance
evaluation on image classification,” IEEE Trans. Pattern Anal. Mach.
Intell., vol. 45, no. 5, pp. 5513–5533, May 2023.

Open Access funding provided by ‘Università degli Studi di Napoli Federico II’ within the CRUI CARE Agreement
PAPER_TEXT
