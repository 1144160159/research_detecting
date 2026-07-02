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
# [516] Reconciling Attribute and Structural Anomalies for Improved Graph Anomaly Detection
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
编号：516
题名：Reconciling Attribute and Structural Anomalies for Improved Graph Anomaly Detection
年份：2025
DOI：10.1109/tnnls.2025.3561172
来源：IEEE Transactions on Neural Networks and Learning Systems
PDF：paper/10.1109_TNNLS.2025.3561172.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\516.txt
- 原始字符数：77970
- 本次发送字符数：77970
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

16661

Reconciling Attribute and Structural Anomalies for
Improved Graph Anomaly Detection
Chunjing Xiao , Jiahui Lu, Xovee Xu, Fan Zhou , Member, IEEE, Tianshu Xie , Wei Lu, and Lifeng Xu

Abstract—Graph anomaly detection is critical in domains
such as healthcare and economics, where identifying deviations
can prevent substantial losses. Existing unsupervised approaches
strive to learn a single model capable of detecting both attribute
and structural anomalies. However, they confront the tug-ofwar problem between two distinct types of anomalies, resulting
in suboptimal performance. This work presents TripleAD, a
mutual distillation-based triple-channel graph anomaly detection
framework. It includes three estimation modules to identify the
attribute, structural, and mixed anomalies while mitigating the
interference between different types of anomalies. In the first
channel, we design a multiscale attribute estimation module to
capture extensive node interactions and ameliorate the oversmoothing issue. To better identify structural anomalies, we
introduce a link-enhanced structure estimation module in the
second channel that facilitates information flow to topologically isolated nodes. The third channel is powered by an
attribute-mixed curvature, a new indicator that encapsulates both
attribute and structural information for discriminating mixed
anomalies. Moreover, a mutual distillation strategy is introduced to encourage communication and collaboration between
the three channels. Extensive experiments demonstrate the
effectiveness of the proposed TripleAD model against strong
baselines.
Index Terms—Attribute anomaly, graph anomaly detection,
graph neural network, mutual distillation, structural anomaly.

A

I. I NTRODUCTION
S THE Internet rapidly evolves, a growing array of
anomalies is causing significant disruptions and losses

Received 28 May 2024; revised 15 January 2025; accepted 7 April 2025.
Date of publication 30 April 2025; date of current version 4 September 2025.
This work was supported in part by the National Natural Science Foundation
of China under Grant 62176043 and Grant 62072077, in part by Henan
Province Science and Technology Development Plan Project under Grant
252102210096 and Grant 242102210065, in part by the Key Research and
Development Program of Henan Province under Grant 251111211300, and
in part by the Key Project of Henan Provincial Department of Education for
Colleges and Universities under Grant 25A520044. (Corresponding authors:
Wei Lu; Lifeng Xu.)
Chunjing Xiao and Jiahui Lu are with the School of Computer and
Information Engineering, Henan University, Kaifeng 475004, China (e-mail:
chunjingxiao@gmail.com; lujh@henu.edu.cn).
Xovee Xu and Fan Zhou are with the School of Information and
Software Engineering, University of Electronic Science and Technology of China, Chengdu 610054, China (e-mail: xovee@std.uestc.edu.cn;
fan.zhou@uestc.edu.cn).
Tianshu Xie is with the Yangtze Delta Region Institute (Quzhou),
University of Electronic Science and Technology of China, Quzhou
324000, China, and also with Quzhou Affiliated Hospital of Wenzhou
Medical University, Quzhou People’s Hospital, Quzhou 324000, China
(e-mail: tianshuxie@std.uestc.edu.cn).
Wei Lu and Lifeng Xu are with Quzhou Affiliated Hospital of Wenzhou Medical University, Quzhou People’s Hospital, Quzhou 324000, China
(e-mail: luwei@wmu.edu.cn; qz1109@wmu.edu.cn).
Digital Object Identifier 10.1109/TNNLS.2025.3561172

[1], [2]. In social welfare, fraudulent medical insurance claims
burden healthcare systems [3], [4]. In economic systems,
financial fraud harms businesses, investors, and consumers [5],
[6]. On social media, fake news distorts public perception,
triggering panic and confusion [7], [8]. By modeling entities as
nodes and their interactions as edges, graph anomaly detection
identifies fraudulent or abnormal nodes deviating from the
norm [9], [10], offering valuable applications to address these
security and economic threats.
In real-world scenarios, graph anomalies primarily manifest in three forms: attribute anomalies, structural anomalies,
and mixed attribute-structural anomalies [11], [12]. The
attribute anomalies usually have a normal neighborhood topology but abnormal node attributes [13], whereas structural
anomalies display normal node attributes but possess an
atypical neighborhood topology. Mixed anomalies are characterized by irregularities in both attributes and structure.
Since collecting ground-truth anomaly node labels is prohibitively expensive, the main challenge of graph anomaly
detection lies in identifying anomalies in an unsupervised
manner [14].
To address this challenge, existing efforts have been devoted
to designing unsupervised graph neural networks (GNNs)
for graph anomaly detection, which primarily fall into two
categories: reconstruction-based methods [15], [16], [17]
and contrast-based methods [18], [19], [20]. Reconstructionbased methods focus on learning node representations by
reconstructing node attributes and structure and identifying
anomalies through reconstruction errors. On the other hand,
contrast-based methods aim to learn distinguishable node representations by discriminating the agreements between nodes
and their neighborhoods.
Nevertheless, a significant limitation of current methods is
their reliance on a single, unified model to detect both attribute
and structural anomalies. Specifically, identifying different
types of anomalies at the same time may lead to a “tugof-war” problem, where the optimization for one anomaly
type may interfere with or diminish the optimization of the
other, ultimately degrading overall performance. Given that
attribute anomalies and structural anomalies represent inherently different types of data, the endeavor to learn distinct
representations using a single model can readily induce interference between the two tasks [21], [22]. Recent studies also
highlighted the interference between attributes and structure
as a key factor in the performance decline of GNNs [23],
[24]. An illustration of this interference problem is depicted
in Fig. 1.

2162-237X © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

16662

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

Fig. 1. Tug-of-war problem between different anomalies. (a) Single-model
fsin is faced with the tug-of-war issue when detecting attribute and structural
anomalies simultaneously. When simultaneously detecting both anomalies, fsin
has to compromise the performance of both tasks. (b) This problem can be
addressed by using three dedicated channels for different types of anomalies.

Inspired by the divide-and-conquer strategy widely applied
in vision [25], [26] and natural language understanding [22],
[27], we propose to decompose the graph anomaly detection
into three subtasks to overcome the “tug-of-war” problem.
Specifically, we propose a novel triple-channel graph anomaly
detection (TripleAD) framework powered by mutual distillation. In TripleAD, we design three distinct channels to
identify the attribute, structural, and mixed anomalies, respectively. Moreover, these channels engage in mutual cooperation
through teacher-student distillation, enhancing training effectiveness and interchannel learning. This strategy not only
mitigates the interference problem but also improves the
detection performance for different types of anomalies.
1) Attribute Channel: This channel employs a multiscale
attribute estimation module to reconstruct a target node’s
masked attributes using its neighbors’ attribute and
structural information. By facilitating attribute propagation across multiple scales, it effectively captures
extensive node interactions for attribute reconstruction.
The attribute channel relieves the over-smoothing issue
inherent in the multilayer message passing of GNNs and
boosts the detection of attribute anomalies.
2) Structure Channel: We corrupt a target node’s structure by masking its edges and try to reconstruct the
masked edges utilizing both attribute and neighborhood
information. We devise a link-enhanced structure estimation module that generates an enhanced graph to
promote information propagation to the isolated nodes.
This channel encourages node information sharing and
improves the detection of structural anomalies.
3) Mixed Channel: We propose a curvature-based mixture estimation module, which introduces a new
indicator—attribute-mixed curvature—to encapsulate
both attribute and structural information for detecting
mixed anomalies. The dual-focus indicator simultaneously considers the strength of pairwise node connections and the degree of attribute similarity. By
reconstructing the attribute-mixed curvature, the mixed
channel captures anomalous patterns in both node
attributes and structure, facilitating the detection of
mixed anomalies.

4) Mutual Distillation: We propose a mutual distillation
module to promote knowledge exchange between different channels. It incorporates a triplet distillation loss
to harness the complementary strengths of the attribute,
structural, and mixed channels. For the attribute and
structure estimation modules, we treat each other as
teacher and student and distill knowledge from the
teacher to the student. For the mixture estimation module, we consider both attribute and structure estimation
modules as teachers to guide the reconstruction of the
attribute-mixed curvature. This strategy facilitates a rich
knowledge transfer, enhancing the detection capabilities.
Our contributions are summarized as follows.
1) We propose a new TripleAD framework, which contains
three distinct estimation modules for detecting attribute,
structure, and mixed anomalies, mitigating the crossanomaly interference.
2) We design a multiscale attribute estimation module,
leveraging augmented views at varying propagation
scales to alleviate GNN over-smoothing and boost
attribute anomaly detection.
3) We devise a link-enhanced structure estimation module,
which generates an enhanced graph to enable effective
message passing to isolated nodes and enhances structure anomaly detection.
4) We propose a curvature-based mixture estimation module, which introduces an attribute-mixed curvature to
express the mixture of attribute and structure information
for mixed anomaly detection.
5) We present a mutual distillation module to prompt
knowledge exchange between three anomaly detection
channels via teacher-student distillation.
Extensive experiments demonstrate the effectiveness of the
proposed TripleAD framework in comparison to strong baselines.
II. P RELIMINARIES
A. Problem Statement
Now, we formalize the graph anomaly detection task. For
an attributed graph G = (V, E, X), where V = {v1 , v2 , . . . , vN }
is a collection of nodes, E = {e1 , e2 , . . . , e M } is a set of edges,
and X = {x1 , x2 , . . . , xN } is the attribute matrix of N nodes. We
have the adjacency matrix A ∈ RN×N containing the structural
information of both V and E, where Ai j = 1 means there
exists an edge between nodes vi and v j ; otherwise, Ai j = 0. In
this context, the task of a graph anomaly detection model is to
rank all the nodes based on computed anomaly scores, thereby
placing nodes with significant deviations from the majority of
reference nodes at higher positions.
B. Graph Curvature
Graph curvature quantifies the strength of interaction and
overlap between the neighbors of a pair of nodes [28], [29],
[30]. Given a pair of nodes (vi , v j ), its curvature is defined as
follows:

W mi , m j
(1)
κ(i, j) = 1 −
dist(i, j)

XIAO et al.: RECONCILING ATTRIBUTE AND STRUCTURAL ANOMALIES

16663

Fig. 2. Curvature distributions on CiteSeer. Normal-normal pairs (left)
exhibit higher curvature values compared to normal-abnormal pairs (right),
highlighting the potential of curvature as an indicator for anomaly detection.

where dist(, ) is the graph distance between vi and v j and W(, )
refers to the Wasserstein distance between the two probability
distributions, that is, the minimum average traveling distance
via any transportation plan. mi and m j denote the probability
distribution of node vi and node v j , respectively. For node
vi with degree k, its probability distribution is computed as
follows:
8
ˆ
if x = i
<α,
(2)
mi [x] = (1 − α)/k, if x ∈ N (i)
ˆ
:
0,
otherwise
where x = 1, . . . , N indicates the component index of the
distribution vector, α is a coefficient within [0, 1], and N (i)
denotes the neighbors of vi .
In general, the graph curvatures of pairwise nodes with
the same category tend to be higher than those with different
categories. This is because nodes with the same category are
inclined to share more interactions (i.e., common neighbors)
[29], [31]. Correspondingly, normal-normal node pairs will
have larger curvature values than normal-abnormal node pairs.
Also, compared to other structural measures (e.g., common
neighbor number and personalized PageRank), graph curvature
can effectively capture abnormal connections between different
communities [31], aligning well with the anomaly characteristics for anomaly detection. Hence, curvature can serve as a
potential indicator for anomaly detection.
To demonstrate its effectiveness, we visualize the normalized curvature distributions of normal-normal and normalabnormal pairs on the CiteSeer dataset. As depicted in Fig. 2,
it is evident that normal-normal pairs tend to exhibit higher
curvature values, primarily concentrated between 0.4 and 0.8.
Conversely, normal-abnormal pairs exhibit lower curvatures,
with the majority falling between 0.27 and 0.4. This observation supports the utilization of graph curvature as an effective
metric for distinguishing anomalous nodes.
III. M ETHODOLOGY
We begin by providing an overview of TripleAD and
subsequently present the details of the three channels designed
for detecting attribute, structural, and mixed anomalies. At last,
we illustrate the processes of interchannel mutual distillation
and model training.
A. Overview of the TripleAD Model
We propose a mutual distillation-based TripleAD framework
to address the interference problem between the detection

Fig. 3. Overview of the TripleAD framework. The three channels,
the multiscale attribute (left), the link-enhanced structure (right), and the
curvature-based mixture (middle) estimation modules, are designed to identify
anomalies from attribute, structural, and mixed perspectives, respectively.
Furthermore, these modules interact and collaborate through our designed
mutual distillation mechanism to ensure robust anomaly detection.

of attribute and structural anomalies. As shown in Fig. 3,
TripleAD is composed of three channels: the multiscale
attribute estimation module (left channel), the link-enhanced
structure estimation module (right channel), and the curvaturebased mixture estimation module (middle channel). These
three channels distinguish anomalies from attribute, structural,
and mixed perspectives. Moreover, a mutual distillation strategy is proposed to promote communication and collaboration
between the three channels. We note that the three channels are sequentially optimized (attribute→structure→mixture)
such that they will not interfere with each other and thus the
“tug-of-war” dilemma is circumvented. This sequential optimization allows each module to focus on learning the optimal
parameters for its specific task (i.e., detecting a particular type
of anomaly), effectively avoiding interference from other tasks.
Before the model training, the structure module is pretrained
for mutual distillation.
The multiscale attribute estimation module takes the graph
with masked attributes as input and produces the reconstructed
attributes. To capture both global (long-range interactions) and
local information without the over-smoothing problem, this
module generates multiple augmented views based on different
feature propagation scales. Then, the augmented views are
embedded into representations using the encoder network. At
last, these representations are combined with the attention
mechanism and fed into the decoder to reconstruct the node
attributes.

16664

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

The link-enhanced structure estimation module takes the
graph with masked structure as input and produces the reconstructed structure. To enable information propagation on the
target node which is isolated after masking its edges, this
module first connects nodes sharing similar semantics to
generate an enhanced graph. Then, the original and enhanced
graphs are fed into the graph diffusion-based propagation and
MLP-based transformation to compute node representations.
Also, the consistency loss between these two graphs is applied
to enhance the model performance. At last, the representations
are combined and fed into the decoder to reconstruct the
structure.
The curvature-based mixture estimation module takes a
graph with the attribute-mixed curvature as input and produces
the reconstructed attribute-mixed curvature. To efficiently capture both attribute and structure information, this module
introduces the attribute-mixed curvature to reflect both the
strength of the structural connection and the attribute similarity
degree. Furthermore, this module reconstructs the attributemixed curvature to identify mixed anomalies.
The mutual distillation scheme connects three
channels—the attribute-, structure-, and curvature-based
mixture modules—to further boost their performance.
This scheme employs the triplet distillation loss based on
aligning intermediate representations between three channels,
prompting one to help the other for final anomaly detection.
The attribute estimation module is promoted by regarding
itself as the student and the structure module as the teacher.
Then, the structure module is advocated by swapping their
roles. Finally, the curvature-based mixture module is advanced
by regarding the other two modules as the teachers. Hence,
the anomalies are determined by combining the attribute and
structure detection results.
B. Multiscale Attribute Estimation
An attribute-anomalous node typically exhibits a normal
neighboring topology but has abnormal attributes [13]. Therefore, for a target node, we propose to mask its attributes
and utilize its neighbors’ attributes and topology to estimate
(reconstruct) the target node’s masked attributes. The attribute
anomalies are then identified based on the reconstruction error.
Similar to reconstruction-based methods [5], [15], we
consider nodes with a bigger reconstruction error as
anomalies—the rationale behind this assumption is that the
model is better at memorizing the characteristics of the majority normal node. Hence, we need to accurately reconstruct the
attributes for normal nodes, but not for anomalies. Following
this idea, global information (i.e., long-range node interactions) is highly desired for effective attribute reconstruction.
The reason is that the number of normal nodes is much larger
than the number of anomalies. Considering long-range node
interactions means that more normal nodes are taken into
account for the attribute estimation. This can let the estimated
attributes be close to the normal ones but distant from the
anomalies, leading to better detection results.
However, directly stacking multiple GNN layers for learning
global graph information will not only result in information distortion caused by the over-smoothing issue but also

introduce additional training burdens that hamper the model
training efficacy [32], [33]. To this end, we design a multiscale
attribute estimation module that can capture complex and rich
node interactions without suffering the over-smoothing issue.
Unlike conventional GNNs, our module involves propagating
features through multiple scales and using an attention mechanism to combine the extracted information. Based on the
different attention scores for each-hop neighbor, our module
can capture attribute information from different-hop neighbors
to estimate the masked node attributes.
To capture the attribute information of the L-hop neighbors,
we perform feature propagation with different scales to generL
ate L feature matrices {X̄(l) }l=1
. Each is generated as follows:
X̄(l) = (1 − α)ĀX(l−1) + αX

(3)

where α is a restart probability and X(0) = X is the attribute
matrix. Ā = D̃−(1/2) ÃD̃−(1/2) is the normalized adjacency
matrix, where Ã = A + I and D̃ is P
the diagonal matrix of Ã
with the diagonal element as D̃i,i = j Ãi, j . Here, the masked
attributes of the target node are initiated as the average of
its neighboring node attributes. Subsequently, we obtain the
augmented feature matrix X̄(l) by an encoder network

Z(l) = ReLU X̄(l) W1
(4)
where Z(l) ∈ RN×h is the representation of N nodes in the
lth scale and W1 is a learnable parameter matrix shared for
the encoding of the feature matrix. Here, {Z(l) }l=1 is learned
from a local view to capture the attribute information from
L
neighboring nodes, while {Z(l) }l=2 is learned from a set of
high-order views to capture augmented attribute information of
l-hop distant nodes.
Through multiscale feature propagation, we now have L
L
L
feature representations {Z(l) }l=1
from {X̄(l) }l=1
. Considering the
difference between different hop nodes, we utilize the attention
mechanism to learn the representation importance


α(1) , . . . , α(L) = Attention Z(1) , . . . , Z(L)
(5)
where α(l) ∈ RN×1 is the attention values of Z(l) . Furthermore,
for a target node vi with the l-top feature representation
1×h
z(l)
(i.e., the ith row of Z(l) ), we compute its attention
i ∈R
scores as follows:


T
Z (l)T
X
ω(l)
=
q
·
tanh
W
z
+
W
x
(6)
i
i
i
0

0

where WZ ∈ Rh ×h and WX ∈ Rh ×d are the weight matrices, xi
0
represents the attribute vector of the target node, and q ∈ Rh ×1
is the shared attention vector. The final attention weight of the
target node vi is obtained by normalizing the attention values
ω(l)
i with Softmax function as follows:
 
 X
 
(l)
(l)
α(l)
=
softmax
ω
=
exp
ω
exp
ω(l)
. (7)
i
i
i
i
l

α(l)
i

Larger
implies that the target node vi tends to favor
the attribute information of the lth hop nodes. Let α(l) =
diag([α(l)
i ]), we have the final representation Z by combining
the representations at different scales
X
Z=
α(l) Z(l) .
(8)
l

XIAO et al.: RECONCILING ATTRIBUTE AND STRUCTURAL ANOMALIES

16665

Then, we decode the feature representation Z into node
attributes. Similar to the works [34], [35], we leverage a simple
fully connected (FC) layer to reconstruct the attributes
X̂ = ReLU (ZW2 + b)

(9)

where W2 is a learnable parameter matrix and b is the corresponding bias term. At last, we calculate the reconstruction
loss by comparing the estimated attribute matrix with the
unmasked one Xreal
Lattr = kXreal − X̂k2F .

(10)

C. Link-Enhanced Structure Estimation
Structural anomalies generally have abnormal connections
with other nodes while possessing normal attributes [13].
Therefore, for a target node, we mask its links (edges) and
assume its attributes are known while the edges are unknown.
Then, we estimate (reconstruct) its structure and further discriminate structure anomalies based on the reconstruction
errors of node links. Notably, when we reconstruct node
structure, the parameters of the attribute channel are frozen
such that the training of the structure estimation module is
not interfered with by the attribute reconstruction.
In the masked graph, the target node becomes isolated after
link masking. During training, the isolated nodes cannot obtain
knowledge from their neighboring nodes, which may weaken
detection performance [36]. To address this issue, we connect
nodes sharing similar attribute semantics to generate a linkenhanced graph, which allows information propagation to the
isolated nodes. Both the original graph and the proposed linkenhanced graph are used to enhance the node representation
learning. The learned representations can effectively capture
the neighboring information and enhance structure estimation.
In particular, we employ the k-nearest neighbor (kNN) graph
as the link-enhanced graph, where the isolated node is linked
to semantic-similar nodes. In the link-enhanced graph, each
isolated node has at least k neighbors. The kNN graph A0 is
constructed by using the propagated feature X̄
(


1, vt ∈ S X̄i , k or vi ∈ S X̄t , k
0
Ati =
(11)
0, otherwise
where S(X̄t , k) is the set of k nodes with the highest similarity
to X̄t . Here, the propagated feature X̄ is computed based on
the masked graph using graph diffusion propagation [see (14)].
Having the link-enhanced graph, we utilize graph diffusion
followed by transformation to compute the node representations via two steps: graph-based diffusion propagation and
FC-based transformation. Assuming Ā and Ā0 denote the
normalized adjacency matrices of the masked and enhanced
graphs, respectively, graph diffusion propagation for both
graphs can be expressed as follows:
X(t+1) = (1 − β)ĀX(t) + βX

(12)

= (1 − β)Ā X + βX

(13)

X

0(t+1)

0

(t)

where X = X and β ∈ (0,1] is a restart probability. After T
iterations, we have propagated feature matrices
(0)

X̄ = X(T ) ,

X̄0 = X0(T ) .

(14)

Then, we utilize two FC layers to map X̄ and X̄0 to the
intermediate representations H2 and H02 , respectively. The
transformation of the masked and enhanced graphs is written
as follows:

H1 = FC1 X̄; W3 , H2 = FC2 (H1 ; W4 )
(15)


H01 = FC1 X̄0 ; W3 , H02 = FC2 H01 ; W4
(16)
where W3 and W4 are learnable parameter matrices.
At last, we combine the representations H2 and H02 from
both graphs to estimate the adjacency matrix Â

Â = fd AGG H2 , H02
(17)
where fd (·) is the reconstruction function that estimates the
adjacency matrix by performing similarity or the inner product between node representations and AGG(·) denotes the
aggregation function such as concatenation. We minimize the
reconstruction error Ladj of the estimated adjacency matrix
with the realistic one
Ladj = kAreal − Âk2F .

(18)

However, this reconstruction objective has a notable limitation. Since the masked and link-enhanced graphs share
model parameters, the learned node representations (especially
for the isolated nodes) may be significantly different due to
the difference in the input structure. Hence, we introduce
a consistency alignment loss, which promotes the semantic
consistency between the two graphs
Lcons = kH1 − H01 k2F .

(19)

This loss encourages the consistency between the original
view and link-enhanced view, helping the model extract more
relevant information w.r.t. the isolated nodes.
During training, we combine the two losses as the overall
objective of the structure estimation, with γ a weighting
coefficient
Lstr = Ladj + γLcons .
(20)
D. Curvature-Based Mixture Estimation
Mixed anomalies display characteristics that are anomalous
w.r.t. both attributes and structure in a mixed manner [12],
[14]. To distinguish mixed anomalies, we design a new indicator, termed attribute-mixed curvature, to reflect the mixed
nature of attributes and structure, and then we reconstruct this
indicator and discriminate mixed anomalies according to the
reconstruction error.
The rationale behind this new indicator for detecting mixed
anomalies is due to the following reasons.
1) Graph curvature is indicative of significant disparities
between normal nodes and anomalies. It quantifies the
interaction or strength of the overlap between pairs of
connected nodes [28], [29], [30]. As confirmed in [31],
node pairs with the same category tend to exhibit higher
curvature values, attributing to a greater number of
shared neighbors, whereas node pairs with different categories display lower curvature values. In the context of
anomaly detection, given that neighbors of both normal
and abnormal nodes are predominantly normal (owing

16666

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

to the higher prevalence of normal nodes), abnormal
nodes tend to have lower curvature values due to less
overlap with their neighbors (referring to Section II-B
for empirical analysis). Therefore, measuring curvature
allows for the differentiation of abnormal nodes.
2) Incorporating node attributes into the curvature calculation can strengthen its effectiveness in distinguishing
mixed anomalies. We incorporate the attribute similarity degree into the curvature. Node pairs with
higher attribute similarity are assigned greater curvature
values—this assignment is relatively higher for normal
nodes and lower for abnormal nodes since normal nodes
tend to have higher similarity with their neighbors,
which are dominated by normal nodes, while anomalous
nodes have lower similarity. Consequently, this consideration decreases the curvature values of anomalies,
facilitating their detection.
1) Computing Attribute-Mixed Curvature: We compute the
attribute-mixed curvature κ(i, j) for node pair (vi , v j ) as follows:


κ(i, j) = 1 − W m̂i( j) , m̂ j(i) /d(i, j)
(21)
where d(, ) is the graph distance between vi and v j and
W(, ) refers to the Wasserstein distance between the two
distributions. m̂i( j) is defined as a probability distribution
vector of node vi to v j . When calculating m̂i( j) , instead of
considering all the neighbors equally, we divide the neighbors
into two groups—common and uncommon neighbors—and
use different strategies for them
8
δ,
if x = i
ˆ
ˆ


ˆ
0
ˆ
S
1
ˆ
ij
ˆ
ˆ
< 1 − δ + |N ∩ N | k , if x ∈ Ni ∩ N j
i
j

(22)
m̂i( j) [x] = 
S0i j
1
ˆ
ˆ
ˆ
,
if
x
∈
N
−
N
1
−
δ
−
i
j
ˆ
ˆ
|Ni − N j | k
ˆ
ˆ
:
0,
otherwise
where x = 1, . . . , N is the index of the distribution vector m̂i( j) ,
δ ∈ [0, 1] is a coefficient, and Ni ∩ N j represents the common
neighbor set of vi and v j , while Ni −N j refers to the difference
between the neighbor sets of vi and v j . S0i j = Si j /(1 − δ) is the
normalized attribute similarity between vi and v j .
2) Updating Adjacent Matrix: Furthermore, we normalize
the curvature values from 0 to 1 using a monotonically
increasing sigmoid function: κ0 (i, j) = 1/(1+exp(−κ(i, j)). The
normalized curvature values are adopted to update the adjacent
matrix for reconstruction. The original adjacent matrix Ai j is
updated to Ci j
8
ˆ
if i = j
<1,
Ci j = κ0 (i, j), if Ai j = 1
(23)
ˆ
:
0,
otherwise.
3) Reconstructing Attribute-Mixed Curvature: Based on the
updated adjacent matrix and the attribute matrix, we use the
GCN [37] as the encoder to embed nodes into representations
for reconstructing the attribute-mixed curvature values. Specifically, multiple GCN layers are adopted to aggregate node

representations. Here, the lth layer representation is obtained
by the forward encoding process

(l−1)
H(l)
W(l−1)
(24)
c = σ LHc
where σ(·) is a nonlinear activation function, H(0)
= X,
c
and W(l−1) denotes the lth learnable parameter matrix. L
refers to the symmetrically normalized Laplacian matrix L =
D̃−1/2
CD̃−1/2
, where D̃c is the degree matrix of C. The
c
c
attribute-mixed curvature is reconstructed by the obtained
representation


(L) T
Ĉ = f H(L)
(25)
c · Hc
where f (·) denotes the FC layers for reconstructing attributemixed curvature. At last, we compute the reconstruction error
by comparing the reconstructed curvature and the original one
Lmix = kC − Ĉk2F .

(26)

E. Mutual Distillation and Model Optimization
Now we have the three channels, that is, the attribute,
structure, and mixture estimation modules. These modules
are highly correlated and complementary as they try to learn
the representations of the same node from different aspects.
Correspondingly, one module can be boosted by receiving
knowledge from another module. Hence, we argue that a
teacher-student distillation is beneficial for knowledge transferring between different modules. However, general distillation
methods focus on minimizing the difference between the
teacher and the student [38], [39]. However, our multichannel
method requires learning node representations that belong to
the same category but also with some differences. Inspired
by [40], [41], we propose to employ the triplet loss of
metric learning to embed the knowledge of the teacher in
the output space of the student and simultaneously clarify
the difference between their outputs. This scheme enables the
triple channels to mutually enhance each other to improve the
overall detection performance.
Specifically, to enhance the attribute estimation module, we
consider it as the student and the structure module as the
teacher. Then, we select an anchor sample xa , a positive x p ,
and a negative xn to form a triplet (xa , x p , xn ). Here, anchor
xa and positive x p are the representations of the same node
from the student and the teacher, respectively, and negative
xn is a randomly selected sample that differs from the node
of xa . Based on this triplet, the mutual distillation scheme
learns representations such that the anchor-to-positive distance
is relatively closer than that of the anchor-to-negative. As a
result, this objective can encourage the representations of the
same node from both modules to be close but also keep some
differences, meeting the requirement of the two modules with
different goals and distilling knowledge from one module to
enhance another.
The triplet distillation loss Ldattr is defined as follows:

X

2
Ldattr =
max 0, t x p − s (xa ) 2
(a,p,n)∈Ω

− kt (xn ) − s (xa )k22 + m



(27)

XIAO et al.: RECONCILING ATTRIBUTE AND STRUCTURAL ANOMALIES

where t(·) and s(·) denote outputs of the teacher and the
student, respectively, and m is a hyperparameter that defines
how far away the dissimilarities should be. Ω is an index set
representing each corresponding anchor, positive, and negative. Since we are training the student model, the weight of
the teacher model is frozen.
For the attribute module, the final training objective is the
combination of the reconstruction loss and the distillation loss
d
Lfin
attr = η1 Lattr + η2 Lattr

Lastly, to advocate the curvature module, we consider both
attribute and structure modules as the teachers to guide the
reconstruction of the attribute-mixed curvatures. Similar to
str
(27), the distillation losses, Lattr
mix and Lmix , are obtained when
regarding the attribute and structure modules as the teachers,
respectively. The final distillation loss for the curvature-based
mixture estimation module is

attr
str
(30)
Lfin
mix = η1 Lmix + η2 Lmix + Lmix .
F. Anomaly Scores
Similar to existing works [17], [42], we distinguish anomalies from normal ones according to the reconstruction error,
that is, the larger the reconstruction error, the more likely
the objects are anomalies. This is because the anomalies
fail to conform to the patterns of the majority and hence
cannot be accurately reconstructed. For a given node vi , we
compute its attribute, structure, and attribute-mixed curvature
reconstruction errors as follows:
2

str

AS (vi ) = Ai − Âi

2

mix

2
C0i − Ĉ0i

AS

(vi ) =

TABLE I
D ESCRIPTIVE S TATISTICS OF DATASETS

(28)

where η1 and η2 are the balancing hyperparameters.
Likewise, to boost the link-enhanced structure estimation,
we swap the roles of the two modules, that is, the attribute
module as the teacher and the structure module as the student. The distillation loss for the structure estimation module,
denoted as Ldstr , is derived similar to (27). Consequently, the
final training objective for the structure estimation module is
the combination of the reconstruction loss and the distillation
loss
d
Lfin
(29)
str = η1 Lstr + η2 Lstr .

ASattr (vi ) = Xi − X̂i

16667

(31)
(32)
(33)

where C0i and Ĉ0i , respectively, denote the original and reconstructed node attribute-mixed curvatures, which are computed
by averaging the attribute-mixed curvatures (i.e., Ci j and Ĉi j )
of node pairs involving this node.
After combining these three types of reconstruction errors,
the final anomaly score of node vi is calculated as follows:
AS(vi ) = λ1 · ASattr (vi ) + λ2 · ASstr (vi ) + λ3 · ASmix (vi ) (34)
where λ1 , λ2 , and λ3 are three balance hyperparameters. The
anomalous nodes are distinguished by the anomaly scores, that
is, nodes with higher scores are more likely to be anomalies.

TABLE II
H YPERPARAMETER S EARCH S PACE

IV. E XPERIMENT
In this section, we carry out performance evaluations to
demonstrate the efficacy of TripleAD for graph anomaly
detection, as well as the ablation study and sensitivity analysis.
A. Experimental Settings
1) Datasets: We conduct experiments on two types of
datasets, whose details are shown in Table I. We split the
datasets into training, validation, and test sets with a ratio of
6:2:2, and hyperparameters are tuned based on the validation
set.
1) Ground-Truth Anomaly Graphs: Amazon [5] is a copurchase network and YelpChi [43] is a transaction
network, both of which have ground-truth labels of the
anomalies and contain the three types of anomalies.
2) Injected Anomaly Graphs: CiteSeer [13] and ACM
[44] are two citation networks, and Flickr [15] is a
social network, with injected anomaly labels. Attribute,
structural, and mixed anomalies are injected into
these three datasets using injection ways of previous
studies [13], [15].
2) Baselines: We compare our model TripleAD with various baselines from three major categories.
1) Traditional Methods: AMEN [45], Radar [11], and
ANOMALOUS [46] employ shallow traditional techniques to implement anomaly detection.
2) Reconstruction-Based Approaches: DOMINANT [15],
AnomalyDAE [47], ALARM [17], ComGA [5], ADAGAD [48], and GAD-NR [49] perform anomaly detection via the autoencoder-based reconstruction technique.
3) Contrast-Based Methods: CoLA [13], Sub-CR [19],
GRADATE [20], and FedCAD [50] conduct anomaly
detection through contrastive learning.
3) Experimental Setup: We sequentially optimize attribute,
structure, and mixture estimation modules, which prevents
interference between the loss functions of the three modules

16668

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

TABLE III
P ERFORMANCE C OMPARISON B ETWEEN T RIPLE AD AND BASELINES ON THE F IVE DATASETS

and ensures that each module learns effectively. For all experiments, we use grid search to find the optimal hyperparameters,
such as the learning rate and number of epochs. The grid
search range for these parameters is shown in Table II.
Note that for the YelpChi dataset, we utilize sparse matrices
instead of dense matrices whenever possible to mitigate outof-memory issues. For other baselines, we retain the settings
described in the corresponding papers to report optimized
results.
B. Anomaly Detection Results
We report the anomaly detection results of TripleAD and the
baselines in Table III. We use widely used anomaly detection
metrics including the AUC-ROC (AROC) curve, AUC-PR
(APR) curve, and Macro F1 score (F1). Specifically, we have
the following observations.
First, the TripleAD model demonstrates superior detection performance across all evaluated datasets, outperforming
the baseline models in every metric. This improvement is
attributed to our model’s unique approach of learning three
distinct representations, enhanced through a mutual distillation
scheme. This strategy effectively mitigates the challenges associated with the interference between attributes and structure
while specifically addressing the detection of mixed anomalies.
Second, the reconstruction-based methods (e.g., ADA-GAD
and GAD-NR) show good performance compared to the
traditional methods. This indicates their effectiveness in capturing anomalous patterns from high-dimensional attributes
and complex structures. However, our method significantly
outperforms them by employing the triple-channel strategy.
Note that AnomalyDAE, which adopts two modules to compute attribute and structural representations, displays inferior
performance compared to our model. The main reason is that
it fails to mitigate the interference, as it concatenates both
representations to simultaneously identify different anomalies
in the same way.

Fig. 4. Performance with different components.

Third, the contrast-based methods (e.g., GRADATE and
FedCAD) exhibit remarkable performance. These approaches,
in particular, leverage the unsupervised contrastive learning
and achieve excellent detection performances. However, a
notable limitation of these methods is their reliance on a
singular model for detecting both attribute and structural
anomalies, which may result in modality interference. In
contrast, TripleAD outperforms these methods in nontrivial
margins, validating our motivation for adopting a triplechannel strategy to alleviate the interference between attribute
anomaly detection and structure anomaly detection. In addition, we calculate the runtime of our model, showing that its
speed is competitive with existing methods and is well-suited
for large-scale datasets.
C. Ablation Study
We ablate four important components in TripleAD by
removing one of them from the entire model: 1) in TripleADAttr, we remove the multiscale attribute estimation module;
2) in TripleAD-Struct, we remove the link-enhanced structure estimation module; 3) in TripleAD-Mix, we remove
the curvature-based mixture estimation module; and 4) in
TripleAD-MD, we remove the mutual distillation scheme.
As shown in Fig. 4, removing any of the three estimation
modules (i.e., TripleAD-Attr, TripleAD-Struct, or TripleADMix) results in performance degradation, which indicates that

XIAO et al.: RECONCILING ATTRIBUTE AND STRUCTURAL ANOMALIES

Fig. 5. F1-scores using the unified scheme and separate scheme.

Fig. 6. Example of the necessity for mitigating the interference between
attribute and structural anomalies. (a) Structure anomaly degree is diluted due
to the interference of normal attributes. (b) Structure anomaly degree is more
prominent without attribute interference.

16669

Fig. 7. Sensitivity analysis for k and γ (AUC).

further investigated the performance of models trained on one
type of anomaly (e.g., attribute anomalies) when applied to
detect another type of anomaly (e.g., structural anomalies).
The results indicate that the detection performance in such
cases is suboptimal. These highlight that the unified scheme is
susceptible to mutual interference, leading to degraded performance. In contrast, the separate scheme effectively mitigates
the “tug-of-war” dilemma, improving overall performance.
E. Sensitivity Analysis

these modules are beneficial for accurately detecting anomalies in graphs. Besides, the variant TripleAD-MD does not
perform the mutual distillation and ignores the knowledge
transfer between the three modules. Lacking guidance from
the structure (resp. attribute) estimation module, the attribute
(resp. structure) module generates suboptimal intermediate
representations, leading to decreased performance. The same
explanation applies to the mixture module. Notably, TripleAD
consistently surpasses all its variants, underlining the efficacy
of our designed attribute, structure, and mixture modules in
conjunction with the mutual distillation scheme.
D. Unified Versus Separate
To evaluate the effectiveness of our three-channel solution
in mitigating the “tug-of-war” problem, we compare the detection performance of a unified model versus separate models.
Specifically, we assess both approaches using two representative baselines: the reconstruction-based DOMINANT [15] and
the contrast-based CoLA [13], along with the curvature-based
mixture estimation module in our model. Under the unified
scheme, the model is trained and evaluated on both attribute
and structural anomalies. Under the separate scheme, each
model is trained and evaluated first on attribute anomalies and
then on structural anomalies.
Fig. 5 reports the F1 scores of the three methods across five
datasets. Notably, the separate scheme consistently surpasses
the unified scheme, particularly in datasets with explicitly
labeled attribute and structural anomalies (CiteSeer, ACM, and
Flickr). In addition, we illustrate the impact of each scheme on
anomaly degrees in Fig. 6. These results are computed using
DOMINANT on the CiteSeer dataset. When using the unified
model to identify both types of anomalies, the structural
anomaly degree is decreased due to the influences of normal
attributes [see Fig. 6(a)]. Conversely, the structural anomaly
degree is significantly increased when using the separate
model to distinguish structural anomalies [see Fig. 6(b)]. We

1) Neighbor Number k and Weighting Coefficient γ: Here,
we alter the selected neighbor number k [see (11)] and
weighting coefficient γ [see (20)] and report their influences
on performance for all the datasets in Fig. 7. Our observations
yield the following insights: 1) too large or too small values
of k generally undermine performance. Since k determines the
degree of neighboring nodes connected to the target node,
a small k can hinder the model from capturing complex
information in the graph, and a large k might introduce noises
into the learning process; and 2) it can be observed that
when the value of γ is excessively high, the proportion of the
alignment loss significantly surpasses that of the reconstruction
loss, leading to a decline in anomaly detection performance.
This is because, while the model aligns the intermediate
representations of the two graphs, it loses its ability to conduct
effective structural estimation based on the reconstruction loss.
2) Balancing Parameters η1 and η2 : We here discuss the
parameters η1 and η2 in the loss function [(28)–(30)]. As
shown in Fig. 8, for a given η1 , setting η2 to 0 results in the
worst performance across all datasets. This observation highlights the importance of our designed distillation loss. Setting
a higher value of η1 generally improves the performance. Conversely, an excessively large value of η2 is counterproductive,
emphasizing too much on the distillation loss will obscure
the difference between these three modules and make the
corresponding reconstruction an extremely challenging task.
3) Triplet Loss Parameter m: We experiment with the
parameter m in the triplet loss [see (27)] to determine suitable
distances for anchor-positive and anchor-negative pairs in the
triplet loss during training. For the five datasets we employed,
we maintained consistent parameter settings while varying the
values of m. We report the values of the AROC curve on the
five datasets in Fig. 9. As shown, a lower value of m leads to
a poor detection performance. The reason behind this is that a
lower value will force the teacher and student estimation modules to be more consistent, which diminishes the advantages of
our triple-channel strategy. On the other hand, a larger value of

16670

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

Fig. 8. Effects of balancing parameters η1 and η2 on the five datasets in terms of AUC.

Fig. 9. Hyperparameter m w.r.t. AUC.

m does not necessarily lead to better performance. This means
that the appropriate difference between the teacher and student
estimation modules is required to achieve optimal detection
results.
V. D ISCUSSION
A. Divide-and-Conquer Strategy
Our proposed model is inspired by the divide-and-conquer
strategy, which has a wide range of applications in natural
language processing (NLP) [22], [51] and computer vision
[25], [26]. Nevertheless, this strategy is rarely applied to
graph learning. We first discuss the existing applications of the
divide-and-conquer strategy and the limitations of this strategy
when applied to graph learning. At last, we discuss its potential
for graph anomaly detection.
1) Existing Applications of Divide and Conquer: The
divide-and-conquer approach is a foundational strategy in
computational algorithms. It aims to divide the input space
into several parts and construct different modules for each part.
These modules are then combined into a unified model [52].
This strategy not only simplifies complex problems but also
enhances the efficiency and effectiveness of the solutions. It
has been widely adopted in various fields, including NLP and
visual learning. For NLP, researchers primarily integrate the
mixture-of-experts (MoEs)—which is based on the divide-andconquer strategy—for building models such as large language
models (LLMs) [22], [51]. They decompose the language
model into several functions, where each “expert” learns on
a different input space, effectively enhancing the performance
of downstream tasks. For vision learning, the image is parsed
by different components, each of which is trained following a
divide-and-conquer learning principle [25], [26].

2) Challenges for Applying It to Graph Learning: Despite
its success, the divide-and-conquer strategy, including the
MOE algorithm, has been rarely explored in the domain of
graph learning. The main challenges can be attributed to
the following two aspects: 1) the focus of graph learning is
to aggregate node attributes along with graph topology for
obtaining node representations [4], [53]; on the other hand,
the divide-and-conquer strategy divides the model or data into
different parts, conflicting with the idea of graph learning;
and 2) dividing graph data into different subgraphs may lead
to information loss, disrupted graph topology, and decreased
graph learning performance [54].
3) Divide-and-Conquer on Graph Anomaly Detection: To
the best of our knowledge, the divide-and-conquer strategy has
not been explored for graph learning. However, we found that
it is feasible to apply this strategy to graph anomaly detection:
the anomalies can be grouped into three types: attribute,
structural, and mixed anomalies [13], [14]. Then, the detection
of these three types of anomalies can be handled separately.
Hence, we introduce the divide-and-conquer strategy into our
designed framework and decompose the detection tasks into
three distinct channels. Each channel is designed to detect a
specific type of anomalies and a mutual distillation module is
proposed to encourage knowledge transfer among channels.

B. Relation to GNNs
We now discuss the relation of our proposed multiscale
feature propagation in the attribute estimation module to the
iterative propagation in conventional GNNs.
1) Iterative Propagation in Conventional GNNs: As illustrated in Fig. 10(a), given the adjacency matrix A and
corresponding feature matrix X, the conventional GNNs compute intermediate representations by iteratively performing
propagation/aggregation and transformation
Z(l) = GNN(l) A, Z(l−1)

= σ ĀZ(l−1) W(l)


(35)

where l ∈ [1, L], Z(0) = X, Z = ZL represents the final
learned intermediate representation from the GNNs, σ(·) is a
nonlinear activation function, such as ReLU, and W(l) denotes
the learnable matrix of each GNN(l) layer.
2) Multiscale Feature Propagation: From Fig. 10(b), it
can be observed that the multiscale feature propagation performs propagation at different scales, generating L propagation

XIAO et al.: RECONCILING ATTRIBUTE AND STRUCTURAL ANOMALIES

16671

is O(Nhd). In the mixture module, the predominant computational cost arises from defining the probability distribution
of nodes and computing the attribute-mixed curvatures, and
their respective time complexities are O(N 2 d) and O(|E|N 2 ),
respectively, where |E| is the number of edges.
VI. R ELATED W ORKS
A. Graph Anomaly Detection

Fig. 10. Relation of the iterative propagation in GNNs and the multiscale
feature propagation in the proposed module. (a) Iteration propagation. (b) Multiscale feature propagation.

L
matrices {X̄(l) }l=1
. Each matrix X(l) aggregates features from a
one-hop neighbors

X̄(l) = (1 − α)ĀX(l−1) + αX

(36)

where l ∈ [1, L], X0 = X, α ∈ (0,1] is the restart probability,
and Ā is the normalized adjacency matrix. Then, the propL
agation matrices {X̄(l) }l=1
are encoded by a parameter-shared
encoder to obtain L intermediate representations

Z(l) = σ X̄(l) W
(37)
where W is the learnable matrix whose parameters are
shared with the encoder. Then, the intermediate representations
L
{Z(l) }l=1
are combined to generate the final representation Z by
sum operation weighted by the attention score α(l)
X
Z=
α(l) Z(l) .
(38)
Compared to the iterative propagation in traditional GNNs,
the multiscale feature propagation we designed broadens the
scope of feature propagation while decreasing its depth. While,
unlike traditional GNNs where multiple iterations are required,
our model performs each step only once and therefore, reducing the parameters introduced by multiple GNN layers. It not
only increases the efficiency of model training but also avoids
the over-smoothing issue caused by deep GNNs.
C. Complexity Analysis
The primary computational overheads of TripleAD lie are
in three aspects: the multiscale attribute, the link-enhanced
structure, and the curvature-based mixture estimation modules.
The time complexity of the propagation in the attribute module
is O(NLd), where N is the number of nodes, L is the number
of propagation scales, and d is the representation dimension.
During the training of attribute estimation, the combination
of L representations through the attention mechanism incurs a
complexity of O(L2 hd), where h is the dimension of Z(l) . In
the structure module, the complexities of the preprocessing for
the masked graph and the enhanced graph are O(NT d) and
O(NkT d), respectively, where k is the number of neighbors
in the kNN graph and T is the number of iterations. In the
training of structure estimation, the time complexity per epoch

Initial efforts in graph anomaly detection utilized shallow
techniques to identify anomalous patterns. These approaches
include ego-graph [45], residual analysis [11], CUR decomposition [46], and clustering methods [55]. However, these
methods suffer from issues such as network sparsity and
data nonlinearity, which limit their ability to capture complex
interrelations among nodes in graphs. Due to the advancements
of deep graph learning [56], [57], [58], many deep models
have been proposed and achieved considerable success. Some
of these models leverage labeled data as supervision signals
to identify anomalies [59], [60], [61]. However, due to the
difficulty of collecting anomalous labels, a greater emphasis
has been placed on unsupervised approaches, which fall into
two groups: reconstruction-based and contrast-based methods.
The reconstruction-based approaches focus on reconstructing node attributes and structure and utilizing the reconstruction errors to identify anomalous nodes [15], [48]. For
example, DOMINANT [15] employs an autoencoder framework to learn node representations through the reconstruction
of both attribute and structural information. Based on this
framework, graph convolutional networks (GCNs) and deep
attention mechanisms have been introduced for graph anomaly
detection [16], [62]. Furthermore, ComGA [5] exploits graph
community structure and AnomMAN [63] learns diverse data
distributions from multiple perspectives for reconstruction.
Moreover, AnomalyDAE [47] learns two separate representations for attribute and structure and combine the learned
representations to enhance reconstruction.
The contrast-based methods, on the other hand, learn nodelevel and subgraph-level representations and then adopt level
agreements to detect anomalies [64], [65]. For example, CoLA
[13] introduces contrastive learning to detect anomalies by
contrasting nodes with their neighborhoods. ANEMONE [66]
performs patch-level and context-level contrastive learning,
facilitating anomaly detection through statistical analyses of
contrastive scores. Sub-CR [19] conducts intra-view and interview contrastive learning and then integrates both modules
based on attribute reconstruction. GRADATE [20] constructs
a multiview contrastive network that includes node-subgraph,
node-node, and subgraph-subgraph comparisons, combining
diverse anomaly information to compute node anomaly scores.
The differences between existing unsupervised anomaly
detection methods and our TripleAD are summarized in
Table IV. Existing deep learning models do not adequately
resolve the interference (or “tug-of-war”) between attribute
and structural representation learning. Note that AnomalyDAE
[47] tries to learn attribute and structural representations in
different channels. However, they concatenate the distinct representations to simultaneously detect both types of anomalies,

16672

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

TABLE IV
C OMPARISON OF R ELATED W ORKS

[55]

three different but collaborated representations for detecting
attribute, structural, and mixed anomalies, respectively. In
terms of the attribute channel, we designed a multiscale
attribute estimation module, which explores multiple augmented views based on different feature propagation scales
to alleviate the over-smoothing issue in traditional GNNs
and advocate attribute anomaly detection. In terms of the
structure channel, we devised a structure estimation module
that generates a link-enhanced graph to promote information
sharing to the isolated nodes and boost structure anomaly
detection. In terms of the mixture channel, we presented a
curvature-based mixture estimation module, which introduces
a new attribute-mixed curvature to reflect the attribute and
structure information for mixed anomaly detection. Besides,
we proposed a mutual distillation strategy that employs a
teacher-student distillation to exchange knowledge from the
three channels and refine learned node representations. Extensive experiments demonstrated that the proposed TripleAD
can alleviate the mutual interference problem and improve
anomaly detection performance.
R EFERENCES
[1]

which cannot avoid the interference between attribute and
structure anomaly detection.
B. Graph Imputation
Our model masks a part of attributes or edges and then
estimates the masked values, aligning closely with graph imputation. There are two main graph imputation tasks: attribute
imputation and structural imputation. Attribute imputation
focuses on recovering missing attributes within graphs [67]. In
this aspect, SAT [68] introduces a feature-structure distribution matching mechanism for attribute imputation. HGNN-AC
[69] employs topological embeddings to improve attribute
completion. ITR [70] utilizes structural information for initial
imputation, subsequently refining the imputed latent variables
using existing attribute and structural information. Additionally, GNN-based autoencoder and Gaussian mixture model
have been introduced to fill missing attributes [71], [72], [73].
Structural imputation (also called link prediction) aims to
infer missing links in a graph [74], [75]. The mainstream
way is to learn representations for the nodes at either end
of a potential link and then combine these representations
to compute link existence probability [76]. Based on this
idea, NBFNet [77] and LLP [78] utilize a GNN-based
encoder to learn node representations and then employ a
decoder to predict link existence. Furthermore, counterfactual
learning, self-supervised learning, and reinforcement learning are introduced to improve link prediction performance
[79], [80], [81].
VII. C ONCLUSION
In this article, we presented a novel mutual distillationbased (TripleAD) framework. It can effectively relieve the
interference between attributes and structure by learning

Y. Liu et al., “Generalized video anomaly event detection: Systematic
taxonomy and comparison of deep models,” ACM Comput. Surveys,
vol. 56, no. 7, pp. 1–38, Jul. 2024.
[2] K. Zhang et al., “Self-supervised learning for time series analysis:
Taxonomy, progress, and prospects,” IEEE Trans. Pattern Anal. Mach.
Intell., vol. 46, no. 10, pp. 6775–6794, Oct. 2024.
[3] J. Ma et al., “Fighting against organized fraudsters using risk diffusionbased parallel graph neural network,” in Proc. Int. Joint Conf. Artif.
Intell., Aug. 2023, pp. 6138–6146.
[4] Z. Wu, S. Pan, F. Chen, G. Long, C. Zhang, and S. Y. Philip, “A
comprehensive survey on graph neural networks,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 32, no. 1, pp. 4–24, Mar. 2020.
[5] X. Luo et al., “ComGA: Community-aware attributed graph anomaly
detection,” in Proc. 15th ACM Int. Conf. Web Search Data Mining, Feb.
2022, pp. 657–665.
[6] B. Branco, P. Abreu, A. S. Gomes, M. S. C. Almeida, J. T. Ascensão,
and P. Bizarro, “Interleaved sequence RNNs for fraud detection,” in
Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining,
Aug. 2020, pp. 3101–3109.
[7] V.-H. Nguyen, K. Sugiyama, P. Nakov, and M.-Y. Kan, “FANG: Leveraging social context for fake news detection using graph representation,”
in Proc. 29th ACM Int. Conf. Inf. Knowl. Manage., Oct. 2020,
pp. 1165–1174.
[8] W. Yu, W. Cheng, C. C. Aggarwal, K. Zhang, H. Chen, and W. Wang,
“NetWalk: A flexible deep embedding approach for anomaly detection
in dynamic networks,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discovery Data Mining, Jul. 2018, pp. 2672–2681.
[9] K. Liu et al., “BOND: Benchmarking unsupervised outlier node detection on static attributed graphs,” in Proc. Adv. Neural Inf. Process. Syst.,
Jan. 2022, pp. 27021–27035.
[10] C. Xiao, S. Pang, X. Xu, X. Li, G. Trajcevski, and F. Zhou,
“Counterfactual data augmentation with denoising diffusion for graph
anomaly detection,” IEEE Trans. Computat. Social Syst., vol. 11, no. 6,
pp. 7555–7567, Dec. 2024.
[11] J. Li, H. Dani, X. Hu, and H. Liu, “Radar: Residual analysis for anomaly
detection in attributed networks,” in Proc. Int. Joint Conf. Artif. Intell.,
2017, pp. 2152–2158.
[12] M. Zhu and H. Zhu, “MixedAD: A scalable algorithm for detecting
mixed anomalies in attributed graphs,” in Proc. AAAI Conf. Artif. Intell.,
vol. 34, Apr. 2020, pp. 1274–1281.
[13] Y. Liu, Z. Li, S. Pan, C. Gong, C. Zhou, and G. Karypis,
“Anomaly detection on attributed networks via contrastive selfsupervised learning,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33,
no. 6, pp. 2378–2392, Jun. 2022.
[14] X. Ma et al., “A comprehensive survey on graph anomaly detection
with deep learning,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12,
pp. 12012–12038, Dec. 2021.

XIAO et al.: RECONCILING ATTRIBUTE AND STRUCTURAL ANOMALIES

[15] K. Ding, J. Li, R. Bhanushali, and H. Liu, “Deep anomaly detection on
attributed networks,” in Proc. IEEE Int. Conf. Data Min. (ICDM), Sep.
2019, pp. 594–602.
[16] L. Huang et al., “Hybrid-order anomaly detection on attributed
networks,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12,
pp. 12249–12263, Dec. 2021.
[17] Z. Peng, M. Luo, J. Li, L. Xue, and Q. Zheng, “A deep multi-view
framework for anomaly detection on attributed networks,” IEEE Trans.
Knowl. Data Eng., vol. 34, no. 6, pp. 2539–2552, Jun. 2022.
[18] Y. Zheng, M. Jin, Y. Liu, L. Chi, K. T. Phan, and Y. P. Chen, “Generative
and contrastive self-supervised learning for graph anomaly detection,”
IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12220–12233, Dec.
2021.
[19] J. Zhang, S. Wang, and S. Chen, “Reconstruction enhanced multi-view
contrastive learning for anomaly detection on attributed networks,” in
Proc. 31st Int. Joint Conf. Artif. Intell. (IJCAI), 2022, pp. 2376–2382.
[20] J. Duan et al., “Graph anomaly detection via multi-scale contrastive
learning networks with augmented view,” in Proc. AAAI Conf. Artif.
Intell., vol. 37, Jun. 2023, pp. 7459–7467.
[21] R. Hadsell, D. Rao, A. A. Rusu, and R. Pascanu, “Embracing change:
Continual learning in deep neural networks,” Trends Cogn. Sci., vol. 24,
no. 12, pp. 1028–1040, Dec. 2020.
[22] Z. Chen et al., “Octavius: Mitigating task interference in MLLMs via
MoE,” in Proc. Int. Conf. Learn. Represent., Jan. 2023.
[23] L. Yang et al., “Graph neural networks beyond compromise between
attribute and topology,” in Proc. ACM Web Conf., Apr. 2022,
pp. 1127–1135.
[24] X. Wang, M. Zhu, D. Bo, P. Cui, C. Shi, and J. Pei, “AM-GCN:
Adaptive multi-channel graph convolutional networks,” in Proc. 26th
ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining, Aug. 2020,
pp. 1243–1253.
[25] Y. Tian, O. J. Henaff, and A. Van Den Oord, “Divide and contrast: Selfsupervised learning from uncurated data,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis. (ICCV), Oct. 2021, pp. 10063–10074.
[26] P. Wei et al., “Component divide-and-conquer for real-world image
super-resolution,” in Proc. Eur. Conf. Comput. Vis. Cham, Switzerland:
Springer, 2020, pp. 101–117.
[27] A. Gidiotis and G. Tsoumakas, “A divide-and-conquer approach to the
summarization of long documents,” IEEE/ACM Trans. Audio, Speech,
Languages Process., vol. 28, pp. 3029–3040, 2020.
[28] Y. Ollivier, “Ricci curvature of Markov chains on metric spaces,”
J. Funct. Anal., vol. 256, no. 3, pp. 810–864, Feb. 2009.
[29] Z. Ye, K. S. Liu, T. Ma, J. Gao, and C. Chen, “Curvature graph network,”
in Proc. Int. Conf. Learn. Represent., Apr. 2020.
[30] X. Guo, Q. Tian, W. Zhang, W. Wang, and P. Jiao, “Learning stochastic
equivalence based on discrete ricci curvature,” in Proc. Thirtieth Int.
Joint Conf. Artif. Intell., Aug. 2021, pp. 1456–1462.
[31] H. Li, J. Cao, J. Zhu, Y. Liu, Q. Zhu, and G. Wu, “Curvature graph
neural network,” Inf. Sci., vol. 592, pp. 50–66, May 2022.
[32] D. Chen, Y. Lin, W. Li, P. Li, J. Zhou, and X. Sun, “Measuring and
relieving the over-smoothing problem for graph neural networks from
the topological view,” in Proc. AAAI Conf. Artif. Intell., 2020, vol. 34,
no. 4, pp. 3438–3445.
[33] K. Ding, Y.-C. Wang, S. Yan, and H. Liu, “Eliciting structural and
semantic global knowledge in unsupervised graph contrastive learning,”
in Proc. AAAI Conf. Artif. Intell., vol. 37, Jun. 2023, pp. 7378–7386.
[34] Y. Xie, X. Zhao, and S. Ji, “Self-supervised representation learning via
latent graph prediction,” in Proc. Int. Conferenceon Mach. Learn., Jan.
2022, pp. 24460–24477.
[35] C. Xiao, X. Xu, Y. Lei, K. Zhang, S. Liu, and F. Zhou, “Counterfactual
graph learning for anomaly detection on attributed networks,” IEEE
Trans. Knowl. Data Eng., vol. 35, no. 10, pp. 10540–10553, Oct. 2023.
[36] Y. Liu, K. Ding, J. Wang, V. Lee, H. Liu, and S. Pan, “Learning
strong graph neural networks with weak information,” in Proc. 29th
ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug. 2023,
pp. 1559–1571.
[37] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” in Proc. Int. Conf. Learn. Represent., 2017.
[38] J. P. Gou, B. S. Yu, S. J. Maybank, and D. C. Tao, “Knowledge distillation: A survey,” Int. J. Comput. Vis., vol. 129, no. 31, pp. 1789–1819,
Jul. 2021.
[39] Y. Tian, S. Pei, X. Zhang, C. Zhang, and N. V. Chawla, “Knowledge
distillation on graphs: A survey,” ACM Comput. Surv., vol. 57, no. 8,
pp. 1–16, Aug. 2025.
[40] H. Oki, M. Abe, J. Miyao, and T. Kurita, “Triplet loss for knowledge
distillation,” in Proc. Int. Joint Conf. Neural Netw. (IJCNN), Jul. 2020,
pp. 1–7.

16673

[41] F. Boutros, N. Damer, F. Kirchbuchner, and A. Kuijper, “Self-restrained
triplet loss for accurate masked face recognition,” Pattern Recognit.,
vol. 124, Apr. 2022, Art. no. 108473.
[42] H. Tong and C.-Y. Lin, “Non-negative residual matrix factorization with
application to graph anomaly detection,” in Proc. SIAM Int. Conf. Data
Mining, Apr. 2011, pp. 143–153.
[43] J. Tang, J. Li, Z. Gao, and J. Li, “Rethinking graph neural networks for anomaly detection,” in Proc. Int. Conf. Mach. Learn., 2022,
pp. 21076–21089.
[44] K. Ding, J. Li, N. Agarwal, and H. Liu, “Inductive anomaly detection
on attributed networks,” in Proc. 29th Int. Joint Conf. Artif. Intell., Jul.
2020, pp. 1288–1294.
[45] B. Perozzi and L. Akoglu, “Scalable anomaly ranking of attributed
neighborhoods,” in Proc. SIAM Int. Conf. Data Min., 2016, pp. 207–215.
[46] Z. Peng, M. Luo, J. Li, H. Liu, and Q. Zheng, “ANOMALOUS: A joint
modeling approach for anomaly detection on attributed networks,” in
Proc. Int. Joint Conf. Artif. Intell. (IJCAI), 2018, pp. 3513–3519.
[47] H. Fan, F. Zhang, and Z. Li, “Anomalydae: Dual autoencoder for
anomaly detection on attributed networks,” in Proc. IEEE Int. Conf.
Acoust., Speech Signal Process. (ICASSP), May 2020, pp. 5685–5689.
[48] J. He, Q. Xu, Y. Jiang, Z. Wang, and Q. Huang, “ADA-GAD: Anomalydenoised autoencoders for graph anomaly detection,” in Proc. AAAI
Conf. Artif. Intell., Mar. 2024, vol. 38, no. 8, pp. 8481–8489.
[49] A. Roy et al., “GAD-NR: Graph anomaly detection via neighborhood
reconstruction,” in Proc. 17th ACM Int. Conf. Web Search Data Mining,
Mar. 2024, pp. 576–585.
[50] X. Kong et al., “Federated graph anomaly detection via contrastive
self-supervised learning,” IEEE Trans. Neural Netw. Learn. Syst., early
access, Jun. 20, 2024, doi: 10.1109/TNNLS.2024.3414326.
[51] W. Chen et al., “Lifelong language pretraining with distributionspecialized experts,” in Proc. Int. Conf. Mach. Learn., Jan. 2023,
pp. 5383–5395.
[52] Y. Pan, R. Xia, J. Yin, and N. Liu, “A divide-and-conquer method for
scalable robust multitask learning,” IEEE Trans. Neural Netw. Learn.
Syst., vol. 26, no. 12, pp. 3163–3175, Dec. 2015.
[53] F. Xia et al., “Graph learning: A survey,” IEEE Trans. Artif. Intell.,
vol. 2, no. 2, pp. 109–127, Apr. 2021.
[54] N. Lee, J. Lee, and C. Park, “Augmentation-free self-supervised learning
on graphs,” in Proc. AAAI, 2022, vol. 36, no. 7, pp. 7372–7380.
[55] N. Liu, X. Huang, and X. Hu, “Accelerated local anomaly detection
via resolving attributed networks,” in Proc. 26th Int. Joint Conf. Artif.
Intell., Aug. 2017, pp. 2337–2343.
[56] H. Wu et al., “High-order proximity and relation analysis for crossnetwork heterogeneous node classification,” Mach. Learn., vol. 113,
no. 9, pp. 6247–6272, 2024.
[57] Y. Mo et al., “Multiplex graph representation learning via dual correlation reduction,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12,
pp. 12814–12827, Dec. 2023.
[58] W. Yu, W. Cheng, C. Aggarwal, B. Zong, H. Chen, and W. Wang, “Selfattentive attributed network embedding through adversarial learning,” in
Proc. IEEE Int. Conf. Data Mining (ICDM), Nov. 2019, pp. 758–767.
[59] Y. Gao, X. Wang, X. He, Z. Liu, H. Feng, and Y. Zhang, “Addressing
heterophily in graph anomaly detection: A perspective of graph
spectrum,” in Proc. ACM Web Conf., Apr. 2023, pp. 1528–1538.
[60] C. Xiao, S. Pang, W. Tai, Y. Huang, G. Trajcevski, and F. Zhou,
“Motif-consistent counterfactuals with adversarial refinement for graphlevel anomaly detection,” in Proc. 30th ACM SIGKDD Conf. Knowl.
Discovery Data Mining, Aug. 2024, pp. 3518–3526.
[61] Y. Gao, X. Wang, X. He, Z. Liu, H. Feng, and Y. Zhang, “Alleviating
structural distribution shift in graph anomaly detection,” in Proc. 16th
ACM Int. Conf. Web Search Data Mining, Feb. 2023, pp. 357–365.
[62] M. Shao, Y. Lin, Q. Peng, J. Zhao, Z. Pei, and Y. Sun, “Learning graph
deep autoencoder for anomaly detection in multi-attributed networks,”
Knowl.-Based Syst., vol. 260, Jan. 2023, Art. no. 110084.
[63] L.-H. Chen et al., “AnomMAN: Detect anomalies on multi-view
attributed networks,” Inf. Sci., vol. 628, pp. 1–21, May 2023.
[64] J. Duan, B. Xiao, S. Wang, H. Zhou, and X. Liu, “ARISE:
Graph anomaly detection on attributed networks via substructure
awareness,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 12,
pp. 18172–18185, Dec. 2024.
[65] J. Hu et al., “SAMCL: Subgraph-aligned multiview contrastive learning
for graph anomaly detection,” IEEE Trans. Neural Netw. Learn. Syst.,
vol. 36, no. 1, pp. 1664–1676, Jan. 2025.
[66] M. Jin, Y. Liu, Y. Zheng, L. Chi, Y.-F. Li, and S. Pan, “ANEMONE:
Graph anomaly detection with multi-scale contrastive learning,” in Proc.
30th ACM Int. Conf. Inf. Knowl. Manage., Oct. 2021, pp. 3122–3126.

16674

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

[67] K. Ding, Z. Xu, H. Tong, and H. Liu, “Data augmentation for deep
graph learning: A survey,” ACM SIGKDD Explor. Newslett., vol. 24,
no. 2, pp. 61–77, 2022.
[68] X. Chen, S. Chen, J. Yao, H. Zheng, Y. Zhang, and I. W. Tsang,
“Learning on attribute-missing graphs,” IEEE Trans. Pattern Anal.
Mach. Intell., vol. 44, no. 2, pp. 740–757, Feb. 2022.
[69] D. Jin, C. Huo, C. Liang, and L. Yang, “Heterogeneous graph neural
network via attribute completion,” in Proc. Web Conf., Apr. 2021,
pp. 391–400.
[70] W. Tu et al., “Initializing then refining: A simple graph attribute
imputation network,” in Proc. 31st Int. Joint Conf. Artif. Intell., 2022,
pp. 3494–3500.
[71] I. Spinelli, S. Scardapane, and A. Uncini, “Missing data imputation
with adversarially-trained graph convolutional networks,” Neural Netw.,
vol. 129, pp. 249–260, Sep. 2020.
[72] H. Taguchi, X. Liu, and T. Murata, “Graph convolutional networks
for graphs containing missing features,” Future Gener. Comput. Syst.,
vol. 117, pp. 155–168, Apr. 2021.
[73] Z. Gao et al., “Handling missing data via max-entropy regularized graph
autoencoder,” in Proc. AAAI Conf. Artif. Intell., vol. 37, Jun. 2023,
pp. 7651–7659.
[74] Q. Tan et al., “S2GAE: Self-supervised graph autoencoders are generalizable learners with graph masking,” in Proc. 16th ACM Int. Conf. Web
Search Data Mining, Feb. 2023, pp. 787–795.
[75] L. Wang et al., “Inductive and unsupervised representation learning on
graph structured objects,” in Proc. Int. Conf. Learn. Represent., Apr.
2020.
[76] S. Yun, S. Kim, J. Lee, J. Kang, and H. J. Kim, “Neo-GNNs: Neighborhood overlap-aware graph neural networks for link prediction,” in Proc.
Adv. Neural Inf. Process. Syst., Jan. 2022, pp. 13683–13694.
[77] Z. Zhu, Z. Zhang, L.-P. Xhonneux, and J. Tang, “Neural bellmanford networks: A general graph neural network framework for link
prediction,” in Proc. Adv. Neural Inf. Process. Syst., Jan. 2021,
pp. 29476–29490.
[78] Z. Guo et al., “Linkless link prediction via relational distillation,” in
Proc. Int. Conf. Mach. Learn., Jan. 2022, pp. 12012–12033.
[79] T. Zhao, G. Liu, D. Wang, W. Yu, and M. Jiang, “Learning from
counterfactual links for link prediction,” in Proc. Int. Conf. Mach.
Learn., Jan. 2021, pp. 26911–26926.
[80] M. Liu et al., “Self-supervised temporal graph learning with temporal
and structural intensity alignment,” IEEE Trans. Neural Netw. Learn.
Syst., vol. 36, no. 4, pp. 6355–6367, Apr. 2025.
[81] L. Wang et al., “Learning robust representations with graph denoising
policy network,” in Proc. IEEE Int. Conf. Data Mining (ICDM), Nov.
2019, pp. 1378–1383.

Xovee Xu received the B.S. and M.S. degrees in
software engineering from the University of Electronic Science and Technology of China (UESTC),
Chengdu, China, in 2018 and 2021, respectively,
where he is currently pursuing the Ph.D. degree in
computer science.
His research interests include social network data
mining and knowledge discovery, primarily focusing on information diffusion in networks, human
behavior understanding, and spatial-temporal data
modeling.

Fan Zhou (Member, IEEE) received the B.S.
degree in computer science from Sichuan University,
Chengdu, China, in 2003, and the M.S. and Ph.D.
degrees from the University of Electronic Science
and Technology of China (UESTC), Chengdu, in
2006 and 2012, respectively.
He is currently a Professor with the School
of Information and Software Engineering, UESTC.
His research interests include machine learning,
spatiotemporal data management, graph learning,
recommender systems, and social network data
mining.

Tianshu Xie received the M.S. degree in computer
technology from the University of Electronic Science and Technology of China (UESTC), Chengdu,
China, in 2021, where he is currently pursuing the
Ph.D. degree.
His current research interests include artificial
intelligence and computer vision.

Wei Lu received the bachelor’s degree in clinical
medicine from Wenzhou Medical University, Wenzhou, China, in 2000.
He is currently a Chief Physician at Quzhou
People’s Hospital, Quzhou, China. His research
focuses on advancing interdisciplinary medicalengineering integration in vascular surgery, with
an emphasis on anomaly detection in vascular
pathology, data-driven clinical decision-making, and
technological innovation for optimized patient care
outcomes.

Chunjing Xiao received the Ph.D. degree in computer software and theory from the University
of Electronic Science and Technology of China,
Chengdu, China, in 2013.
He was a Visiting Scholar with Northwestern University, Evanston, IL, USA, and University College
London, London, U.K. He is currently an Associate
Professor with the School of Computer and Information Engineering, Henan University, Kaifeng, China.
His current research interests include anomaly detection, graph learning, and the Internet of Things.

Lifeng Xu received the bachelor’s degree in clinical
laboratory diagnostics from Wenzhou Medical University, Wenzhou, China, in 2004.
He is currently a Senior Technician at Quzhou
Third People’s Hospital, Quzhou, China, and also
a Professor at Zhejiang Chinese Medical University, Hangzhou, China. His research focuses on
microbial testing, antimicrobial resistance mechanisms, integration of artificial intelligence in medical
diagnostics, anomaly detection in microbial resistance patterns, and intelligent healthcare system

Jiahui Lu received the B.E. degree from the
School of Computer Engineering, Shangqiu University, Shangqiu, China, in 2022. She is currently
pursuing the M.S. degree with the School of
Computer and Information Engineering, Henan University, Kaifeng, China.
Her current research interests include anomaly
detection, data analytics, and social network
data mining.
development.
PAPER_TEXT
