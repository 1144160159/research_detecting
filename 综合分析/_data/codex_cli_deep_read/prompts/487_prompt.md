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
# [487] MIETT: Multi-Instance Encrypted Traffic Transformer for Encrypted Traffic Classification
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
编号：487
题名：MIETT: Multi-Instance Encrypted Traffic Transformer for Encrypted Traffic Classification
年份：2025
DOI：10.1609/aaai.v39i15.33748
来源：Proceedings of the AAAI Conference on Artificial Intelligence
PDF：paper/10.1609_aaai.v39i15.33748.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 13
已有代码状态：已下载；MIETT -> source\MIETT; Secilia-Cxy/MIETT -> source\MIETT

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\487.txt
- 原始字符数：42657
- 本次发送字符数：42657
- 是否截断：False

代码包：
- 仓库：MIETT
  - URL：https://github.com/SeciliaCxy/MIETT
  - 状态：downloaded
  - 本地目录：source\MIETT
  - 顶层结构：LICENSE、README.md
  - 主要语言：
  - README 标题：(AAAI 2025) MIETT: Multi-Instance Encrypted Traffic Transformer for Encrypted Traffic Classification、(AAAI 2025) MIETT: Multi-Instance Encrypted Traffic Transformer for Encrypted Traffic Classification、(AAAI 2025) MIETT: Multi-Instance Encrypted Traffic Transformer for Encrypted Traffic Classification
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：Tor、tor
- 仓库：Secilia-Cxy/MIETT
  - URL：https://github.com/Secilia-Cxy/MIETT
  - 状态：downloaded
  - 本地目录：source\MIETT
  - 顶层结构：LICENSE、README.md
  - 主要语言：
  - README 标题：(AAAI 2025) MIETT: Multi-Instance Encrypted Traffic Transformer for Encrypted Traffic Classification、(AAAI 2025) MIETT: Multi-Instance Encrypted Traffic Transformer for Encrypted Traffic Classification、(AAAI 2025) MIETT: Multi-Instance Encrypted Traffic Transformer for Encrypted Traffic Classification
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：Tor、tor

论文正文包开始：
<<<PAPER_TEXT
MIETT: Multi-Instance Encrypted Traffic Transformer
for Encrypted Traffic Classification
Xu-Yang Chen* , Lu Han* , De-Chuan Zhan, Han-Jia Ye†

arXiv:2412.15306v1 [cs.CR] 19 Dec 2024

School of Artificial Intelligence, Nanjing University, China
National Key Laboratory for Novel Software Technology, Nanjing University, China
{chenxy, hanlu, zhandc, yehj}@lamda.nju.edu.cn

Abstract
Network traffic includes data transmitted across a network,
such as web browsing and file transfers, and is organized
into packets (small units of data) and flows (sequences of
packets exchanged between two endpoints). Classifying encrypted traffic is essential for detecting security threats and
optimizing network management. Recent advancements have
highlighted the superiority of foundation models in this task,
particularly for their ability to leverage large amounts of unlabeled data and demonstrate strong generalization to unseen data. However, existing methods that focus on tokenlevel relationships fail to capture broader flow patterns, as
tokens, defined as sequences of hexadecimal digits, typically
carry limited semantic information in encrypted traffic. These
flow patterns, which are crucial for traffic classification, arise
from the interactions between packets within a flow, not just
their internal structure. To address this limitation, we propose a Multi-Instance Encrypted Traffic Transformer (MIETT), which adopts a multi-instance approach where each
packet is treated as a distinct instance within a larger bag
representing the entire flow. This enables the model to capture both token-level and packet-level relationships more effectively through Two-Level Attention (TLA) layers, improving the model’s ability to learn complex packet dynamics and
flow patterns. We further enhance the model’s understanding of temporal and flow-specific dynamics by introducing
two novel pre-training tasks: Packet Relative Position Prediction (PRPP) and Flow Contrastive Learning (FCL). After
fine-tuning, MIETT achieves state-of-the-art (SOTA) results
across five datasets, demonstrating its effectiveness in classifying encrypted traffic and understanding complex network
behaviors. Code is available at https://github.com/SeciliaCxy/MIETT.

Introduction
Network traffic refers to the flow of data transmitted between
devices over a network, typically structured into packets,
which are small units sent across the network, and flows,
which are sequences of packets exchanged between two
points. Each packet is composed of two parts: the header
and the payload. The header contains essential information,
* These authors contributed equally.
†

Corresponding Author
Copyright © 2025, Association for the Advancement of Artificial
Intelligence (www.aaai.org). All rights reserved.

Internet

Header <IP version=4 ihl=5 tos=0x0
len=134 id=8194 flags= frag=0 ttl=128
proto=udp chksum=0xc63d
src=131.202.240.87
dst=121.171.102.90 …
Payload (Encrypted)

Packets

Encrypted
Traffic

Classification
Flows

Classifier

Email
90%
Chat
6%
File Transfer 1%
…

Figure 1: Encrypted traffic classification task description.
Raw traffic is first divided into session flows, with each flow
further segmented into a sequence of packets. A packet typically consists of a header and a payload. The task is to classify the type of a given flow.

such as routing details, source and destination addresses, and
packet length, while the payload carries the actual data being
transmitted, which may be encrypted for security purposes.
Traffic classification, the process of identifying and categorizing network traffic, is crucial for both network management and cybersecurity. It allows network administrators
to ensure Quality of Service (QoS), optimize bandwidth and
detect malicious activities, thus maintaining network security and efficiency. The overview of encrypted traffic classification task is provided in Figure 1.
However, the increasing prevalence of encryption has
made traditional classification methods, such as port-based
and statistics-based approaches, less effective. The advent of
deep learning (DL) brought significant improvements, with
payload-based methods using models like CNNs to automatically extract features from raw data. Despite their success,
these methods rely heavily on large amounts of labeled data,
which can be difficult to obtain.
Recently, foundation models have emerged as a powerful alternative, pre-trained on large volumes of unlabeled
data and fine-tuned for specific tasks. PERT (He, Yang, and
Chen 2020) employs a BERT-based model with a Masked
Language Modeling (MLM) task to pre-train a packetlevel encoder, but this approach primarily focuses on tokenlevel relationships within individual packets, overlooking
the broader context of inter-packet relationships. ET-BERT

(Lin et al. 2022) addresses this limitation by introducing
the Same-origin BURST Prediction (SBP) task, which determines whether one packet follows another within the same
flow. While this method accounts for adjacent packet relationships, it still falls short of capturing the full complexity of flow-level interactions and the broader context across
multiple packet segments. YaTC (Zhao et al. 2023) takes
a different approach by tokenizing traffic data into patches
and using a Masked Auto-Encoder (MAE) for pre-training a
token-level encoder within a flow. However, focusing solely
on token dependencies is less effective due to the low semantic information in encrypted traffic tokens. This approach
tends to overlook the broader patterns and relationships that
exist between entire packets within a traffic flow. Instead,
learning packet representations that capture these packet patterns proves to be more robust. Given that each packet can
be viewed as a distinct instance carrying unique information within a flow, it is crucial to effectively model the relationships between packets to achieve a comprehensive flow
representation. To address this, we propose a Multi-Instance
Encrypted Traffic Transformer (MIETT) with Two-Level
Attention (TLA) layers that capture both token-level and
packet-level relationships. To further enhance the model’s
ability to capture temporal and flow-specific dynamics, we
introduce two novel pre-training tasks: Packet Relative Position Prediction (PRPP) and Flow Contrastive Learning
(FCL). The PRPP task is designed to help the model understand the sequential relationships between packets within a
flow by predicting their relative positions, thereby enabling
a more accurate representation of the flow’s structure. Meanwhile, the FCL task focuses on distinguishing packets from
the same flow and those from different flows by learning
robust representations that emphasize intra-flow similarities
and inter-flow differences.
Building on the robust representations learned during pretraining, the model is then fully fine-tuned on the specific
classification task. During this stage, both the packet encoder and the flow encoder are jointly optimized to adapt the
model to the task at hand. Across experiments conducted on
five datasets, MIETT consistently demonstrates competitive
or superior performance compared to existing methods. In
conclusion, this paper presents several key contributions to
the field of encrypted traffic classification:
• We propose a novel Multi-Instance Encrypted Traffic Transformer (MIETT) architecture, which introduces
Two-Level Attention (TLA) layers to effectively capture
both token-level and packet-level relationships within
traffic flows.
• We introduce two innovative pre-training tasks, Packet
Relative Position Prediction (PRPP) and Flow Contrastive Learning (FCL). The PRPP task enhances the
model’s understanding of the sequential order of packets
within a flow, while the FCL task improves the model’s
ability to differentiate between packets from the same
flow and those from different flows.
• We provide extensive empirical validation of the proposed MIETT model on multiple datasets, showing that
our approach outperforms existing methods in terms of

accuracy and F1-score.

Related work
Encrypted traffic classification is an essential research area
in network security. As encryption becomes more prevalent, traditional traffic analysis methods that inspect packet
payloads have become less effective. Researchers now focus on methods to classify encrypted traffic without accessing its content directly. These methods can be divided into
three types: port-based methods, statistics-based methods,
and payload-based methods.
Port-based Methods. Port-based traffic classification, one
of the oldest methods, relies on associating port numbers
in TCP/UDP headers with well-known IANA port numbers. Although it is fast and simple, the method’s accuracy
has declined due to port obfuscation, dynamic port assignments, network address translation (NAT), and other techniques (Moore and Papagiannaki 2005).
Statistics-based Methods. Statistics-based methods for
encrypted traffic classification leverage features independent
of payloads, such as packet sizes, timing, and flow duration, to analyze and categorize traffic. Wang et al. computed entropy from packet payloads to classify eight traffic
classes, using an SVM algorithm to select features (Wang
et al. 2011). Similarly, Korczynski and Duda focused on
packet sizes, timing, and communication patterns for classifying traffic in encrypted tunnels (Korczyński and Duda
2012). However, these methods are based on manually designed features and are now outdated due to advancements
in encryption protocols, changes in traffic patterns, and the
use of traffic obfuscation techniques.
Payload-based DL Methods. Payload-based methods
usually leverage deep learning to analyze raw packet data,
eliminating the need for manually designed features. These
approaches have significantly advanced encrypted traffic
classification by automatically extracting discriminative features. Deep Packet (Lotfollahi et al. 2020) employs a CNN
within a framework that includes a stacked autoencoder
and convolutional neural network to classify network traffic. TSCRNN (Lin, Xu, and Gao 2021) utilizes CNN to
extract abstract spatial features and introduces a stacked
bidirectional LSTM to learn temporal characteristics. BiLSTM ATTN (Yao et al. 2019) combines attention mechanisms with LSTM networks for enhanced encrypted traffic
classification. Though these methods can automatically extract features, they heavily rely on labeled data, which is often difficult to obtain in large quantities for training.
Payload-based Foundation Models. In recent years, pretrained foundation models have become popular for addressing this issue. These models are pre-trained on large amounts
of unlabeled data and fine-tuned on downstream labeled
tasks. PERT (He, Yang, and Chen 2020) and ET-BERT (Lin
et al. 2022) tokenize traffic data using a vocabulary. PERT
employs a Masked Language Model (MLM) pre-training
task, while ET-BERT utilizes a modified MLM and Next
Sentence Prediction (NSP) task. Additionally, YaTC (Zhao

Anonymize

Separate
Packets
Packet-based
Splitting

Anonymized
Packet
Hex Form

263dd0…758d

Session Flow
Flow-based
Splitting

Hexadecimal
Datagram
Tokenization

263d 3d11 … 8592
929c 9c10 … 758d

PCAP Trace

Tokens

Figure 2: Data preprocessing. The raw traffic (PCAP trace)
is first split into session flows and then further divided into
individual packets. To protect data privacy, each packet is
anonymized by masking the source and destination IP addresses and port numbers (replacing them with 0). The
packet is then converted to its hexadecimal form, which is
tokenized using a bi-gram model.

et al. 2023), a vision model adaptation, tokenizes traffic data
into patches and uses a Mask Auto-Encoder (MAE) for pretraining. However, these approaches do not adequately consider the unique structure of traffic flows and the relationships between packets. To address these limitations, we introduce the Multi-Instance Encrypted Traffic Transformer
(MIETT) architecture, which leverages novel Packet Relative Position Prediction (PRPP) and Flow Contrastive Learning (FCL) tasks to better capture the complexities of traffic
flows.

Multi-Instance Encrypted Traffic Transformer
In the task of encrypted traffic classification, we are provided
with raw network traffic (PCAP traces) as input, and the objective is to classify it into categories, such as VPN services
(e.g., P2P, streaming, email) and applications. In this section, we first outline the preprocessing steps that transform
the raw data into a multi-instance traffic representation. We
then introduce our Multi-Instance Encrypted Traffic Transformer (MIETT) architecture, which is specifically designed
to handle and classify this traffic data efficiently.

MIETT Encoder
This section details the process of representing multiinstance traffic data for use in the Multi-Instance Encrypted
Traffic Transformer (MIETT) architecture. The process involves three key steps: tokenization of the raw data, representation of individual packets, and the aggregation of these
packet representations into a unified flow representation.
Tokenization. The hexadecimal sequence of the flow is
obtained through the data preprocessing steps outlined in

Figure 2. Following ET-BERT (Lin et al. 2022), we encode
the hexadecimal sequence using a bi-gram model, where
each unit consists of two consecutive bytes. We then utilize
Byte-Pair Encoding (BPE) for token representation, with token units ranging from 0 to 65535 and a maximum dictionary size of 65536. For training, we also incorporate special
tokens, including [CLS], [PAD], and [MASK].
Packet Representation. Each packet begins with a [CLS]
token, followed by tokens extracted from the packet’s content, which includes a header containing meta-features and
an encrypted payload. The embedding of each token is obtained by combining two parts: position embedding, which
indicates the token’s position within the packet, and value
embedding. To ensure efficient information utilization and
avoid excessive focus on long packets, the packet length is
standardized to a fixed size of 128. Packets shorter than 128
tokens are padded with [PAD] tokens at the end.
Flow Representation. The flow representation consists of
multiple packet representations, which are stacked to form a
matrix X ∈ RN ×L×d , where N is the number of packets,
L is the packet length, and d is the embedding dimension.
This multi-instance representation, as opposed to the previous method employed by ET-BERT of directly concatenating packets, allows for more effective modeling of the
relationships between packets and better captures the organizational structure of flows.

MIETT Architecture
The flow representation, a 2D map of tokens, can be flattened into a 1D sequence for input into a standard transformer, as done in ViT (Dosovitskiy et al. 2021) and
YaTC (Zhao et al. 2023) during pre-training and fine-tuning.
However, this approach introduces two issues: (1) Flattening the sequence loses temporal information, such as
packet order, potentially overlooking important dependencies. While 2D position embeddings could indicate temporal
relationships, they are inflexible and may fail in scenarios
like packet loss. (2) The computational complexity, which
is O(N 2 L2 d), increases significantly with the inclusion of
more packets due to the extended sequence length. To address these concerns, we introduce the Two-Level Attention (TLA) layer to preserve temporal structure and maintain
computational efficiency.
Overall Architecture. The Multi-Instance Encrypted
Traffic Transformer (MIETT) begins by embedding the tokens as described in the MIETT Encoder section. Following
this, the flow representation is processed through M TLA
layers. Finally, the embeddings of the [CLS] tokens from all
the packets are utilized for pre-training or fine-tuning tasks.
The overall architecture of MIETT can be found in Figure 3.
Two-Level Attention (TLA) Layer. The TLA layer captures both intra-packet and inter-packet dependencies to enhance the model’s understanding of complex traffic flows. It
operates in two stages: Packet Attention and Flow Attention.
In the Packet Attention stage, Multi-Head Self-Attention
(MHSA) is applied within individual packets to identify dependencies between tokens, ensuring the model understands

Two-Level Attention
transpose
packet

×𝑀
transpose

[CLS]

packet

Flow
Attention

Packet
Attention

packet
packet

original order:

Figure 3: Overall architecture of the Multi-Instancepacket
Encrypted
Traffic Transformer (MIETT). After passing through the MIETT
packet packet
encoder, the flow representation is processed by M Two-Level Attention (TLA) layers, each comprising a packet attention
mechanism and a flow attention mechanism.
flow
flow
[MASK]

packet

task samples:
packet

packet

packet

packet

the internal structure of each packet. For MHSA, the key,
√
×
query, andpacket
value are all set to the input sequence, with the
𝑆 , pkt
𝑆 , flow (Xpkt
X̂flow
(3)
·j = LayerNorm(X
·j + MHSA
·j ))
output being
an
enriched
sequence
representation.
packet
packet
packet
packet packet
flow
flow
flow
positive X̂
pair: + MLP(
negative
pair:))
In the Flow Attention stage, MHSA is used across packet
X·j = LayerNorm(
X̂·j
(4)
·j
×
packets from
√
packets from
packet at each position to capture dependencies berepresentations
the same flow
different flows
tween tokens across different packets. This two-stage
ap- packet packet
packet
packet
Training Tasks
proach effectively models the hierarchical structure of trafThis section
× outlines the training tasks designed to improve
√
fic flows by combining detailed packet-level insights with
the model’s ability to classify encrypted network traffic. The
broader inter-packet relationships.
pre-training
three Learning
tasks: Masked
Flow PreFlow Contrastive
(FCL) Task
Packet Relative
Position
(PRPP) Taskphase includes
Flowsignificantly
Prediction (MFP)
Task
ThisMasked
method
improves
the model’s
ability
to Prediction
diction
(MFP),
Packet
Relative
Position
Prediction
(PRPP),
(c)
capture complex(a)dependencies but also introduces compu-(b)
and
Flow
Contrastive
Learning
(FCL).
These
tasks
help
tational complexity. The MHSA in Packet Attention has a
the model capture flow dependencies, predict packet order,
complexity of O(L2 d) per packet, while Flow Attention has
and differentiate flow-level features. After pre-training, the
a complexity of O(N 2 d) per position, resulting in an overmodel is fine-tuned for traffic flow classification, optimizing
2
2
all complexity of O(N L d + LN d). For default values of
it for the final task.
L = 128 and N = 5, our method is approximately 4.8 times
more efficient than flattening the sequence to 1D and feeding
Pre-Training tasks
it into a standard transformer.
The model we propose consists of several Two-Level AtPacket Attention. In the first stage of the TLA layer, we
tention (TLA) layers, designed to effectively capture both
focus on the intra-packet relationships by performing Multipacket-level and flow-level information within traffic flows.
Head Self-Attention (MHSA) within individual packets. Let
During the pre-training stage, We utilize a pre-trained ETX ∈ RN ×L×d be the flow representation, where N is the
BERT checkpoint for the packet attention, which is kept
number of packets, L is the packet length, and d is the emfrozen during training, while the flow attention is trained
bedding dimension.
to learn the overall structure and dependencies within the
For each packet Xi ∈ RL×d , we apply self-attention
flows. This design allows our model to leverage established
to capture the dependencies between the tokens within the
packet-level features while focusing on improving flowpacket. The process is as follows:
level understanding. The general view of our proposed 3 pretraining tasks can be found in Figure 4.
pkt
pkt
X̂i = LayerNorm(Xi + MHSA (Xi ))
(1)
Masked Flow Prediction (MFP) Task. The Masked Flow
pkt
pkt
Xpkt
(2)
i = LayerNorm(X̂i + MLP(X̂i ))
Prediction (MFP) task is aimed at enhancing the model’s
ability to handle incomplete information within a traffic
Flow Attention. In the second stage of the TLA layer, we
flow. In this task, 15% of the tokens within a flow are ranfocus on the inter-packet relationships by performing multidomly masked, and the model is tasked with predicting the
head self-attention (MHSA) across the packet representaoriginal content of these masked tokens using the context
packet
tions at each position within the packets. Let X
∈
provided by the unmasked tokens. By training the flow enRN ×L×d be the updated flow representation after the packet
coder to infer the missing tokens, the model learns to capture
attention stage.
the underlying structure and dependencies within the traffic
For each position j (where j ∈ 1, 2, . . . , L) within the
flow.
packets, we gather the token representations across all packets, resulting in a matrix Xpacket
∈ RN ×d , where N is the
·j
number of packets. We apply self-attention to these matrices
to capture the dependencies between tokens across different
packets. The process is as follows:

Packet Relative Position Prediction (PRPP) Task. The
Packet Relative Position Prediction (PRPP) task is designed
to predict the relative order of packets within a flow, based
on the embeddings of the [CLS] tokens extracted from each

Attention

Attention

packet
packet

original order:
packet

packet

packet

flow
[MASK]

flow

task samples:

packet

packet

packet

packet

packet

√

packet
packet

packet

×

packet

packet

√

packet
packet

packet

packet

𝑆

,

positive pair:
packets from
the same flow

×

,

negative pair:
packets from
different flows

packet

×

√
Masked Flow Prediction (MFP) Task

𝑆

packet

Packet Relative Position Prediction (PRPP) Task

Flow Contrastive Learning (FCL) Task

(b)

(c)

(a)

Figure 4: Overview of pre-training tasks. (a) Masked Flow Prediction (MFP) Task: The model is tasked with predicting the
original content of masked tokens using the context provided by the unmasked tokens. (b) Packet Relative Position Prediction
(PRPP) Task: The model’s objective is to determine, for each pair of packets (i, j), whether packet i precedes packet j. (c) Flow
Contrastive Learning (FCL) Task: The goal is to ensure that packets within the same flow (positive pairs) are more similar in
the embedding space, while packets from different flows (negative pairs) are less similar.
packet. This task helps the model understand the sequential relationships between packets, which is critical for accurately modeling traffic flows.
Given an output flow representation with N packets, let
Opkt ∈ RN ×d represent the embeddings of the [CLS] tokens from all packets in the flow, where d is the embedding
dimension. The task is to determine, for each pair of packets
(i, j), whether packet i comes before packet j.
Firstly, a linear transformation is applied followed by an
activation function and layer normalization to [CLS] tokens:
P = LayerNorm(GELU(Opkt W1 + b1 ))

(5)

where W1 ∈ Rd×d and b1 ∈ Rd are learnable parameters.
P ∈ RN ×d .
Then, the predicted relative position of packets (i, j) is
computed as follows:
ẑij = Softmax((Pi − Pj )W2 + b2 )
d×2

(6)

2

where W2 ∈ R
and b2 ∈ R are learnable parameters,
and ẑij ∈ R2 gives the probability that packet i comes before or after packet j.
The ground truth labels zij ∈ {0, 1} are based on the original order of packets:

1 if packet i comes before packet j
zij =
(7)
0 otherwise
Finally, the PRPP loss LPRPP is calculated using crossentropy between the predicted labels and the ground truth:
X
LPRPP = −
zij log(ẑij ) + (1 − zij ) log(1 − ẑij ) (8)
i,j,i̸=j

Flow Contrastive Learning (FCL) Task. The Flow Contrastive Learning (FCL) task enhances the model’s ability
to differentiate between traffic flows by learning robust representations. The objective is to ensure that packets within
the same flow (positive pairs) are more similar in the embedding space, while packets from different flows (negative
pairs) are less similar. Notably, both positive and negative
pairs are constructed using identical packet positions within
their respective flows, maintaining consistency in the comparisons.
Given a batch of output flow representations, let Oflow ∈
RBS×N ×d represent the embeddings of the [CLS] tokens
from all packets in the flows within the batch, where BS
denotes the batch size, N the number of packets per flow,
and d the embedding dimension.
First, a multi-layer perceptron (MLP) is applied to each
[CLS] token:
C = LayerNorm(GELU(Oflow W3 + b3 ))
C = CW4 + b4

(9)
(10)

where W3 ∈ Rd×d , b3 ∈ Rd , W4 ∈ Rd×d , and b4 ∈ Rd
are learnable parameters. C ∈ RBS×N ×d .
Next, the similarity between two packets is computed using cosine similarity:
Si1 j1 ,i2 j2 =

CTi1 j1 Ci2 j2
∥Ci1 j1 ∥∥Ci2 j2 ∥

(11)

where i1 , i2 represent the flow IDs within the batch, and
j1 , j2 denote the packet positions within the flow. Cij ∈ Rd .
Finally, the contrastive loss is computed using the similar-

ISCXVPN 2016

ISCXTor 2016

AC

F1

AC

Datanet
Fs-Net
BiLSTM ATTN
DeepPacket
TSCRNN

69.18%
29.30%
0.57%
69.18%
69.18%

13.63%
33.67%
3.13%
13.63%
13.63%

Methods

CrossPlatform (Android) CrossPlatform (iOS)

F1

CICIoT 2023

AC

F1

AC

F1

9.45%
7.08%
0.45%
4.84%
2.43%

1.53%
4.11%
0.04%
0.04%
0.24%

4.81%
10.94%
0.29%
4.81%
2.84%

0.05%
6.38%
0.01%
0.05%
0.51%

2.50% 0.81%
66.80% 54.81%
5.79% 4.66%
34.35% 8.52%
2.50% 0.81%

YaTC
ET-BERT

78.05% 70.83% 97.39% 85.12% 91.61%
74.62% 71.10% 95.71% 80.29% 84.63%

82.28%
67.70%

75.31%
77.05%

69.57%
74.26%

86.18% 73.16%
88.09% 83.29%

MIETT (ours)

76.07% 77.86%

82.36%

79.63%

75.03%

88.53% 82.48%

49.81% 9.50%
82.03% 63.54%
88.33% 55.54%
49.81% 9.50%
44.70% 13.40%

96.60% 82.15% 93.00%

AC

F1

Table 1: Performance comparisons on encrypted traffic classification tasks. We denote the best and second-best results with
bold and underline.
ity matrix S:
LFCL = −

Dataset

X

log

i1 ,j1 ,j2
j1 ̸=j2

exp(Si1 j1 ,i1 j2 )
P
exp(Si1 j1 ,i1 j2 ) +
exp(Si1 j1 ,i2 j2 )
i2 ̸=i1

(12)
where i1 , i2 ∈ [1, BS] represent the flow IDs in the batch,
j1 , j2 ∈ [1, N ] denote the packet positions within the flow.
Conclusion. Overall, the final loss during the pre-train
stage is the weighted sum of the above 3 losses:
Lpt = LMPF + αLPRPP + βLFCL

#Flow

Task

#Label

ISCXVPN 2016

311,390 VPN Service

6

ISCXTor 2016

55,523

Tor Service

7

CrossPlatform (Android) 66,346

Application

212

Application

196

CICIoT Dataset 2023 1,163,495 IoT Attack

7

Cross Platform (iOS)

34,912

Table 2: The statistical information of 5 different datasets.

(13)

where α and β are hyperparameters.

Fine-Tuning Task
The objective of the fine-tuning task is to classify a given
flow into a specific class. After processing the flow through
several TLA layers, we obtain a flow representation by extracting the embeddings of the [CLS] tokens from all packets. These embeddings, representing each packet, are then
aggregated using mean pooling to form a comprehensive
representation of the entire flow. This mean-pooled flow
representation is passed through a multi-layer perceptron
(MLP) to produce the final classification output, indicating
the predicted class of the traffic flow.
During this stage, the entire model, including both the
packet encoder (previously frozen during pre-training) and
the flow encoder, is fine-tuned. The fine-tuning process optimizes the model by minimizing the cross-entropy loss:
X
Lft = −
yc log(ŷc )
(14)
c

where yc is the true label, and ŷc is the predicted probability
for class c.

Experiments
Experiment Setup
Datasets and Benchmarks. For the encrypted traffic classification task, we evaluate our method on five

datasets: ISCXVPN 2016 (Draper-Gil et al. 2016), ISCXTor 2016 (Lashkari et al. 2017), and the CrossPlatform (Van Ede et al. 2020) dataset, which includes two
subsets (Android and iOS), as well as the CIC IoT Dataset
2023 (Neto et al. 2023). We utilize data preprocessed by Netbench (Qian et al. 2024). The data used for pre-training consists of the training sets from all five datasets in Netbench,
without labels. The dataset statistics and descriptions of the
fine-tuning tasks are detailed in Table 2. The data is split into
training, validation, and test sets with a ratio of 8:1:1.
Compared Methods. We compare our method against 7
payload-based approaches, including deep learning methods
such as Datanet (Wang et al. 2018), Fs-Net (Liu et al. 2019),
BiLSTM ATTN (Yao et al. 2019), DeepPacket (Lotfollahi
et al. 2020), TSCRNN (Lin, Xu, and Gao 2021), as well
as foundation models like ET-BERT (Lin et al. 2022) and
YaTC (Zhao et al. 2023).
Implementation Details. During the pre-training stage,
we set the training steps to 150,000 and randomly select five
of the first ten packets for training. The masking ratio for
the Masked Flow Prediction (MFP) task is set to 15%. The
weights for the Packet Relative Position Prediction (PRPP)
and MFP tasks are both set to 0.2. In the fine-tuning stage,
we train for 30 epochs using the first five packets. For both
stages, the packet length (L) is set to 128, the number of
packets (N ) is set to 5, the embedding dimension (d) is set
to 768, and the number of Two-Level Attention (TLA) layers is set to 12. The learning rate is set to 2 × 10−5 , and the

Methods

CrossPlatform (Android) CrossPlatform (iOS)
AC

from scratch 88.08%
w/o PRPP 90.79%
w/o FCL
91.90%
Ours
93.00%

F1
73.62%
79.02%
81.60%
82.36%

AC

F1

71.63% 63.43%
78.96% 74.35%
79.46% 74.80%
79.63% 75.03%

Table 3: Impact of Pre-Training Tasks.
Methods

CrossPlatform (Android) CrossPlatform (iOS)
AC

w/o pkt attn 62.19%
w/o flow attn 91.85%
TLA (ours) 93.00%

F1
28.59%
80.77%
82.36%

AC

Figure 5: Impact of the Number of Packets.

F1

55.58% 39.93%
79.11% 72.46%
79.63% 75.03%

Table 4: Impact of TLA components, where ’pkt attn’ refers
to packet attention and ’flow attn’ refers to flow attention.

Methods

CrossPlatform (Android) CrossPlatform (iOS)
AC

header only 78.77%
payload only 72.46%
All
93.00%

F1
64.98%
65.80%
82.36%

AC

F1

52.96% 41.66%
63.82% 55.30%
79.63% 75.03%

Table 5: Impact of the Component of Packets.
AdamW optimizer is used. All experiments are conducted
on a server with two NVIDIA RTX A6000 GPUs.

Main Results
The primary metrics for comparison are Accuracy and F1Score. Accuracy measures the proportion of correct predictions, while F1-Score balances precision and recall. Table 1 presents the performance comparison of various models on encrypted traffic classification tasks, with baseline
results sourced from NetBench (Qian et al. 2024). The results clearly indicate that traditional deep learning methods,
such as DataNet, DeepPacket, FS-Net, TSCRNN, and BiLSTM ATTN, struggle to generalize effectively to new tasks,
particularly on complex datasets. These models frequently
exhibit a bias toward dominant classes, resulting in consistently low F1-scores, especially on datasets like CrossPlatform (Android) and CrossPlatform (iOS).
In contrast, our MIETT model demonstrates significant
improvements in both accuracy and F1-scores across the
board, showcasing its superior capability to handle the
complexities of encrypted traffic. Notably, MIETT consistently achieves competitive or superior performance compared to existing methods. For instance, in the CrossPlatform (Android) dataset, MIETT outperforms ET-BERT with
an 8.27% increase in accuracy and a 14.66% increase in F1score, highlighting the effectiveness of the flow attention.

Prediction (PRPP) and Flow Contrastive Learning (FCL)
further boosts the model’s performance.
Impact of TLA Components. TLA captures intra- and
inter-packet dependencies, efficiently handling the challenges of modeling token-to-token relations across packets.
Table 1 shows that ET-BERT, using only token-level attention, performs worse. As shown in Table 4, results on CrossPlatform(Android) shows removing flow attention raises error rates by 16.4%, and using token-mean embeddings for
packets lowers accuracy to 62.19%, underscoring the importance of both attentions.

Ablation Study

Impact of the Number of Packets. Figure 5 shows the
impact of packet count. On the left, we observe that as
more packets provide additional information, the F1 score
increases, confirming our expectations. However, on the
CrossPlatform (Android) dataset, using just one packet outperforms using three, with 91.79% accuracy, higher than all
baseline models using five packets. This suggests that in
some datasets, the initial packets may contain the most critical information, and adding more packets may not always
improve performance. If packet relationships are not effectively modeled, it could even harm performance. In this case,
the reason our model did not perform well may be due to the
discrepancy between the pre-training stage, where five packets were used, and the fine-tuning stage, where only three
were used, leading to a mismatch in distribution.

Impact of Pre-Training Tasks. Table 3 presents an ablation study that compares different versions of the pretraining tasks on the CrossPlatform (Android) and CrossPlatform (iOS) datasets to evaluate the contributions of specific tasks. The baseline model (”from scratch”) shows decent performance, indicating that pre-training is important
and can significantly enhance the model’s ability to generalize to new tasks. As the results demonstrate, incorporating
specific pre-training tasks such as Packet Relative Position

Impact of the Component of Packets. Table 5 highlights
the advantages of payload-based methods in traffic classification. When using only the packet header, the model’s
performance is significantly lower, showing that the header
lacks sufficient information for accurate classification. However, when focusing on the payload, which contains the actual data, the model’s F1-scores improve, especially on complex datasets like Cross Platform (iOS). This demonstrates
that payload-based methods are more effective in capturing

the essential characteristics of traffic, making them superior
for encrypted traffic classification. Combining both header
and payload yields the best results.

Conclusion
In this paper, we introduced MIETT to address challenges in
encrypted traffic classification. The model uses TLA layers
to capture both token-level and packet-level relationships.
Through novel pre-training strategies, MIETT effectively
learns temporal and flow-specific dynamics. Our experiments demonstrate that MIETT outperforms existing methods, achieving superior results across five datasets.

Acknowledgments
This work is partially supported by the National Science
and Technology Major Project (2022ZD0114805), NSFC
(62376118), Key Program of Jiangsu Science Foundation
(BK20243012), Collaborative Innovation Center of Novel
Software Technology and Industrialization.

References
Dosovitskiy, A.; Beyer, L.; Kolesnikov, A.; Weissenborn,
D.; Zhai, X.; Unterthiner, T.; Dehghani, M.; Minderer, M.;
Heigold, G.; Gelly, S.; Uszkoreit, J.; and Houlsby, N. 2021.
An Image is Worth 16x16 Words: Transformers for Image
Recognition at Scale. In 9th International Conference on
Learning Representations, ICLR 2021, Virtual Event, Austria, May 3-7, 2021. OpenReview.net.
Draper-Gil, G.; Lashkari, A. H.; Mamun, M. S. I.; and Ghorbani, A. A. 2016. Characterization of encrypted and vpn
traffic using time-related. In Proceedings of the 2nd international conference on information systems security and privacy (ICISSP), 407–414.
He, H. Y.; Yang, Z. G.; and Chen, X. N. 2020. PERT:
Payload Encoding Representation from Transformer for Encrypted Traffic Classification. In 2020 ITU Kaleidoscope:
Industry-Driven Digital Transformation, Kaleidoscope, Ha
Noi, Vietnam, December 7-11, 2020, 1–8. IEEE.
Korczyński, M.; and Duda, A. 2012. Classifying service
flows in the encrypted skype traffic. In 2012 IEEE International Conference on Communications (ICC), 1064–1068.
IEEE.
Lashkari, A. H.; Gil, G. D.; Mamun, M. S. I.; and Ghorbani,
A. A. 2017. Characterization of tor traffic using time based
features. In International Conference on Information Systems Security and Privacy, volume 2, 253–262. SciTePress.
Lin, K.; Xu, X.; and Gao, H. 2021. TSCRNN: A novel
classification scheme of encrypted traffic based on flow spatiotemporal features for efficient management of IIoT. Computer Networks, 190: 107974.
Lin, X.; Xiong, G.; Gou, G.; Li, Z.; Shi, J.; and Yu, J. 2022.
ET-BERT: A Contextualized Datagram Representation with
Pre-training Transformers for Encrypted Traffic Classification. In WWW ’22: The ACM Web Conference 2022, Virtual
Event, Lyon, France, April 25 - 29, 2022, 633–642. ACM.

Liu, C.; He, L.; Xiong, G.; Cao, Z.; and Li, Z. 2019. Fs-net:
A flow sequence network for encrypted traffic classification.
In IEEE INFOCOM 2019-IEEE Conference On Computer
Communications, 1171–1179. IEEE.
Lotfollahi, M.; Jafari Siavoshani, M.; Shirali Hossein Zade,
R.; and Saberian, M. 2020. Deep packet: A novel approach
for encrypted traffic classification using deep learning. Soft
Computing, 24(3): 1999–2012.
Moore, A. W.; and Papagiannaki, K. 2005. Toward the accurate identification of network applications. In International
workshop on passive and active network measurement, 41–
54. Springer.
Neto, E. C. P.; Dadkhah, S.; Ferreira, R.; Zohourian, A.; Lu,
R.; and Ghorbani, A. A. 2023. CICIoT2023: A real-time
dataset and benchmark for large-scale attacks in IoT environment. Sensors, 23(13): 5941.
Qian, C.; Li, X.; Wang, Q.; Zhou, G.; and Shao, H. 2024.
NetBench: A Large-Scale and Comprehensive Network
Traffic Benchmark Dataset for Foundation Models. In 2024
IEEE International Workshop on Foundation Models for
Cyber-Physical Systems & Internet of Things (FMSys), 20–
25. IEEE Computer Society.
Van Ede, T.; Bortolameotti, R.; Continella, A.; Ren, J.;
Dubois, D. J.; Lindorfer, M.; Choffnes, D.; Van Steen, M.;
and Peter, A. 2020. Flowprint: Semi-supervised mobile-app
fingerprinting on encrypted network traffic. In Network and
distributed system security symposium (NDSS), volume 27.
Wang, P.; Ye, F.; Chen, X.; and Qian, Y. 2018. Datanet: Deep
learning based encrypted network traffic classification in sdn
home gateway. IEEE Access, 6: 55380–55391.
Wang, Y.; Zhang, Z.; Guo, L.; and Li, S. 2011. Using entropy to classify traffic more deeply. In 2011 IEEE Sixth
International Conference on Networking, Architecture, and
Storage, 45–52. IEEE.
Yao, H.; Liu, C.; Zhang, P.; Wu, S.; Jiang, C.; and Yu, S.
2019. Identification of encrypted traffic through attention
mechanism based long short term memory. IEEE transactions on big data, 8(1): 241–252.
Zhao, R.; Zhan, M.; Deng, X.; Wang, Y.; Wang, Y.; Gui, G.;
and Xue, Z. 2023. Yet Another Traffic Classifier: A Masked
Autoencoder Based Traffic Transformer with Multi-Level
Flow Representation. In Thirty-Seventh AAAI Conference on
Artificial Intelligence, AAAI 2023, 5420–5427. AAAI Press.

Appendix
We provide details omitted in the main paper.

Pseudo Code
As described in the main section, we introduce a new architecture called the Multi-Instance Encrypted Traffic Transformer (MIETT), along with two novel pre-training tasks:
the Packet Relative Position Prediction (PRPP) Task and
the Flow Contrastive Learning (FCL) Task. Additionally,
the fine-tuning task is presented. Below are their respective
pseudocode implementations.

Algorithm 4: Fine-Tuning Task

Algorithm 1: MIETT Encoder
Require: Raw traffic flow tokens Xraw ∈ RB×N ×L , where
B is the batch size, N is the number of packets, and
L is the packet length. Position embedding function
Position Emb : {0, 1, . . . , L − 1} → Rd , which maps
each position to a d-dimensional embedding. Value embedding function Value Emb : {0, 1, . . . , Vocab size −
1} → Rd , which maps each token value to a ddimensional embedding.
1: X = Position Emb(Xraw ) + Value Emb(Xraw )
2: for l = 1 . . . M do
3:
X = LayerNorm(X + MHSApkt (X))
▷ Packet
Attention, X ∈ RB×N ×L×d
4:
X = LayerNorm(X + MLP(X))
5:
X = XT
6:
X = LayerNorm(X + MHSAflow (X))
▷ Flow
Attention, X ∈ RB×L×N ×d
7:
X = LayerNorm(X + MLP(X))
8:
X = XT
9: end for
10: Return X
Algorithm 2: PRPP Task
Require: X ∈ RB×N ×L×d is the output from the MIETT
Encoder, where B is the batch size, N is the number of
packets, L is the packet length, and d is the dimension
of embedding. W1 ∈ Rd×d , W2 ∈ Rd×2 and b1 ∈
Rd , b2 ∈ R2 are learnable parameters.
1: XCLS = X:,:,0,:
▷ XCLS ∈ RB×N ×d
2: P = LayerNorm(GELU(XCLS W1 + b1 ))
▷
P ∈ RB×N ×d
3: for each pair of packets (i, j) do
4:
ẑij = Softmax((P:,i,: − P:,j,: )W2 + b2 )
▷
ẑij ∈ RB×2
5: end for
P
6: LPRPP = − i,j,i̸=j I(i < j) log(ẑij )+I(i > j) log(1−
ẑij )
7: Return LPRPP
Algorithm 3: FCL Task
Require: X ∈ RB×N ×L×d is the output from the MIETT
Encoder, where B is the batch size, N is the number of
packets, L is the packet length, and d is the dimension
of embedding.
1: XCLS = X:,:,0,:
▷ XCLS ∈ RB×N ×d
2: C = MLP(XCLS )
▷ C ∈ RB×N ×d
3: for each pair of packets (i1 j1 , i2 j2 ) where i1 , i2 ∈
[1, B] and j1 , j2 ∈ [1, N ] do
CT

Ci j

Si1 j1 ,i2 j2 = ∥Ci ij1 j1∥∥C2i 2j ∥
▷ Cosine similarity
1 1
2 2
5: end for P
exp(Si j ,i j2 )
6: LFCL = − i1 ,j1 ,j2 log exp(Si j ,i j )+ 1P1 1exp(S
i j ,i j )

4:

j1 ̸=j2

7: Return LFCL

1 1

1 2

i2 ̸=i1

1 1

2 2

Require: X ∈ RB×N ×L×d is the output from the MIETT
Encoder, where B is the batch size, N is the number of
packets, L is the packet length, and d is the dimension
of embedding.
1: XCLS = X:,:,0,:
▷ XCLS ∈ RB×N ×d
2: Xmean = MeanPooling(XCLS )
▷ Xmean ∈ RB×d
3: ŷ = MLP(Xmean )
▷ ŷ ∈ RB×C , where C is the
number of
Pclasses
4: Lft = − c yc log(ŷc )
5: Return Lft

Implementation Details.
During the pre-training stage, we set the training steps to
150,000 and randomly select five of the first ten packets for
training. The masking ratio for the Masked Flow Prediction
(MFP) task is set to 15%. The weights for the Packet Relative Position Prediction (PRPP) and Flow Contrastive Learning (FCL) tasks are both set to 0.2. In the fine-tuning stage,
we train for 30 epochs using the first five packets.
For both stages, the packet length (L) is set to 128, the
number of packets (N ) is set to 5, the embedding dimension
(d) is set to 768, and the number of Two-Level Attention
(TLA) layers is set to 12. The learning rate is set to 2 ×
10−5 , and the AdamW optimizer is used. All experiments
are conducted on a server with two NVIDIA RTX A6000
GPUs. The PyTorch version is 2.3.0, and the random seed
is fixed at 0 for reproducibility. Pre-processed hexadecimal
data are provided by Netbench (Qian et al. 2024), so we do
not need to handle raw traffic data.
PAPER_TEXT
