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
# [140] Heterogeneous Domain Adaptation for IoT Intrusion Detection: A Geometric Graph Alignment Approach
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
编号：140
题名：Heterogeneous Domain Adaptation for IoT Intrusion Detection: A Geometric Graph Alignment Approach
年份：2023
DOI：10.1109/JIOT.2023.3239872
来源：IEEE Internet of Things Journal
PDF：paper/10.1109_JIOT.2023.3239872.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、图学习、知识图谱与威胁情报
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\140.txt
- 原始字符数：67562
- 本次发送字符数：67562
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
10764

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 12, 15 JUNE 2023

Heterogeneous Domain Adaptation for IoT Intrusion
Detection: A Geometric Graph Alignment Approach
Jiashu Wu , Graduate Student Member, IEEE, Hao Dai , Graduate Student Member, IEEE,
Yang Wang , Member, IEEE, Kejiang Ye , Member, IEEE, and Chengzhong Xu , Fellow, IEEE

Abstract—Data scarcity hinders the usability of datadependent algorithms when tackling IoT intrusion detection
(IID). To address this, we utilize the data-rich network intrusion detection (NID) domain to facilitate more accurate intrusion
detection for IID domains. In this article, a geometric graph
alignment (GGA) approach is leveraged to mask the geometric
heterogeneities between domains for better intrusion knowledge
transfer. Specifically, each intrusion domain is formulated as a
graph where vertices and edges represent intrusion categories and
category-wise inter-relationships, respectively. The overall shape
is preserved via a confused discriminator incapable to identify
adjacency matrices between different intrusion domain graphs. A
rotation avoidance mechanism and a center point matching mechanism are used to avoid graph misalignment due to rotation and
symmetry, respectively. Besides, category-wise semantic knowledge is transferred to act as vertex-level alignment. To exploit the
target data, a pseudo-label (PL) election mechanism that jointly
considers network prediction, geometric property, and neighborhood information is used to produce fine-grained PL assignment.
Upon aligning the intrusion graphs geometrically from different granularities, the transferred intrusion knowledge can boost
IID performance. Comprehensive experiments on several intrusion data sets demonstrate state-of-the-art performance of the
GGA approach and validate the usefulness of GGA-constituting
components.
Index Terms—Domain adaptation (DA), geometric graph alignment (GGA), Internet of Things (IoT), intrusion detection,
pseudo-label election.

I. I NTRODUCTION
NTERNET of Things (IoT) devices become indispensable
for various real-world applications and innovatively transform several fields such as healthcare [1], [2], etc. However,

I

Manuscript received 19 November 2022; revised 5 January 2023; accepted
23 January 2023. Date of publication 26 January 2023; date of current version
7 June 2023. This work was supported in part by the Third Xinjiang Scientific
Expedition Program under Grant 2021xjkk1300; in part by the Science
and Technology Development Fund of Macao SAR (FDCT) under Grant
1058No.0015/2019/AKP; and in part by the Chinese Academy of Sciences
President’s International Fellowship Initiative under Grant 2023VTA0001.
(Corresponding author: Yang Wang.)
Jiashu Wu and Hao Dai are with the Shenzhen Institute of Advanced
Technology, Chinese Academy of Sciences, Shenzhen 518055, China, and
also with the University of Chinese Academy of Sciences, Beijing 100049,
China (e-mail: wujiashu21@mails.ucas.ac.cn; daihao19@mails.ucas.ac.cn).
Yang Wang and Kejiang Ye are with the Shenzhen Institute of Advanced
Technology, Chinese Academy of Sciences, Shenzhen 518055, China (e-mail:
yang.wang1@siat.ac.cn; kj.ye@siat.ac.cn).
Chengzhong Xu is with the State Key Laboratory of IoT for Smart City,
Faculty of Science and Technology, University of Macau, Macau, China
(e-mail: czxu@um.edu.mo).
Digital Object Identifier 10.1109/JIOT.2023.3239872

the limited power and computational capability of IoT devices
hinder the applicability of powerful security mechanisms,
together with relatively infrequent maintenance, making IoT
vulnerable to malicious intrusions. Therefore, to keep the IoT
infrastructure safe, an effective IoT intrusion detection (IID)
system is vital. To advance the intrusion detection techniques,
several research directions become popular. Dietz et al. [3]
proposed to automatically scan IoT devices for predefined vulnerability patterns, and isolated suspicious devices to block the
botnet spreading. McDermott et al. [4] tackled the problem
via deep recurrent neural network (RNN) and achieved satisfying detection performance. However, these efforts required
either a thorough intrusion pattern repository, or abundant
labeled training data, which is expensive to collect and timeconsuming to annotate, and is, especially, difficult for IoT due
to factors such as data privacy concerns, the frequent emergence of new IoT things, etc. Therefore, the data scarcity of
IoT hinders the usability of these rules or the data-dependent
methods.
Considering that the Internet intrusion data is richer than IoT
domains, and they share several similar intrusion categories,
several domain adaptation-based (DA) methods were proposed
to treat the network intrusion (NI) as the source domain and
transfer rich intrusion knowledge to facilitate the data-scarce
target IoT intrusion (II) domains. By achieving domaininvariant alignment, the transferred intrusion knowledge can
facilitate more accurate IID. For instance, Ning et al. [5]
presented a Laddernet-based DA solution to improve the
intrusion classification accuracy and secure the industrial IoT
infrastructures. Hu et al. [6] studied a deep subdomain adaptation network with an attention mechanism and focused on
distribution alignment between domains via local maximum
mean discrepancy. Methods such as [7] and [8] proposed to
achieve intrusion domain alignment by aligning the graph
learning results. Efforts such as [9], [10], and [11] attempted
to explore unlabeled target domain via directly predicted,
threshold selected, or softly assigned pseudo-labels (PLs),
respectively, to facilitate better intrusion knowledge transfer.
Despite their success, they left some deficiencies that
need to be addressed. Previous DA-based ID methods didn’t
tackle the problem from a geometric graph perspective and
failed to explore unlabeled target domain via geometric and
neighborhood-aware PLs. The ignorance of intrinsic geometric properties in domain graphs and the under-explored target
domain can result in coarse-grained alignment. Although some
graph-based DA methods were proposed, they did not attempt

c 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
2327-4662 
See https://www.ieee.org/publications/rights/index.html for more information.
Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

WU et al.: HETEROGENEOUS DOMAIN ADAPTATION FOR IoT INTRUSION DETECTION

Fig. 1.

General motivation of the GGA approach.

Fig. 2.

Overview of the GGA mechanism.

graph alignment from a pure geometric perspective, leaving the
geometric properties under-explored. Despite some methods
can partially convey the geometric properties through graph
embedding, however, the embedding learning is highly datadependent which is challenging for IoT scenarios. Besides,
although there were some traditional PL-based DA methods, their isolated PL assignment strategy failed to leverage
the geometric and neighborhood information between labels,
which may produce error-prone PLs and mislead the intrusion
knowledge transfer.
To address these limitations and achieve more fine-grained
intrusion knowledge transfer, following the motivation illustrated in Figs. 1 and 2, we propose a geometric graph alignment (GGA) approach that works under the semi-supervised
heterogeneous DA (HDA) setting, i.e., the target is scarcelylabeled and significant source-target heterogeneities exist, such
as having diverse feature spaces, following different distributions, etc. To positively exploit the unlabeled target domain, we
utilize a PL election (PLE) mechanism. To prevent the errorprone PL from misleading the model, the geometric property
is considered to eliminate confident but incorrect PLs based on
their geometric relationship with each category. Besides, the
PLE consults the neighborhood label information when assigning PLs to avoid near-boundary ambiguous PLs, which cannot
be fulfilled by traditional isolated PL assignment strategies. By
jointly considering the network prediction, the geometric property, and the neighborhood information, the PLE can boost
pseudo-label accuracy and, hence, lead to positive intrusion
knowledge transfer.
The GGA then formulates each domain as a graph, where
vertices and edges represent intrusion categories and their
inter-relationships. As illustrated in Fig. 2, enforcing a perfect

10765

GGA can have each intrusion category and their interrelationships well aligned between domains. First, with the
help of the PLE, the GGA performs a graph-level shapekeeping via a confused discriminator which is incapable to
distinguish weighted adjacency matrices (WAMs) between
intrusion domain graphs. Upon aligning the graph shapes, a
center point matching mechanism and a rotation avoidance
mechanism avoid graph misalignment caused by symmetry
and graph rotation, respectively. Finally, the GGA will perform
a vertex-level matching by preserving categorical correlation
knowledge between domains, which equivalently aligns the
graph vertex of each intrusion category between domains.
Holistically, they form a graph alignment framework from general to specific level from a geometric perspective. The GGA
can robustly transfer the enriched intrusion knowledge from
the NI domain to facilitate more accurate intrusion detection
in the II domain and, hence, secure IoT infrastructures. GGA’s
motivation has been illustrated in Figs. 1 and 2.
In summary, the contributions of this article are threefold.
1) We propose to transfer enriched intrusion knowledge
from the NI domain to facilitate more accurate intrusion
detection for data-scarce IoT domains and formulate it
as a semi-supervised HDA problem.
2) To our best knowledge, we are the pioneer to tackle this
HDA problem from a pure GGA perspective with the help
of the PLE mechanism. Rather than using isolated coarsegrained PL strategies, the PLE makes fine-grained PL
assignment by jointly considering geometric and neighborhood information to filter confident but geometrically
incorrect PLs and near-boundary ambiguous PLs. The
GGA then aligns domain graphs geometrically through
four mechanisms, holistically forming a graph alignment
framework from graph to vertex granularity.
3) We conduct comprehensive experiments of several tasks
on five widely used intrusion detection data sets to verify the superior performance achieved by the GGA, and
show the usefulness of its constituting components.
The remainder of this article is organized as follows.
Section II presents related works by categories and demonstrates the research opportunities of the GGA method.
Section III provides model preliminaries, graph formulations,
and the GGA model architecture. The detailed GGA and
pseudo-label election mechanism are explained in Section IV.
Section V presents experimental setups and result analyzes.
The last section concludes this article. For better readability,
an acronym table, and a notation table have been presented in
the Appendix section.
II. R ELATED W ORK
IID3 Methods: The IID has drawn wide research attention to secure IoT infrastructures. The rule-based IID methods
were initially popular. Dietz et al. [3] performed automatic
scanning of neighboring IoT devices for known vulnerability patterns and temporarily isolated detected compromised
devices. Jun and Chi [12] proposed to filter security violations
via complex event processing, which required a sophisticated rule repository. On the other hand, machine learning

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

10766

techniques were also widely used for IID. Anthi et al. [13]
presented a three-layer intrusion detector that worked under
a supervised fashion for smart home settings. Shukla [14]
tackled the problem via a hybrid two-stage mechanism that
combined K-means clustering and decision trees. On the
deep learning perspective, models, such as feedforward neural
network, deep autoencoder, and BiLSTM RNN, were utilized
to work on the IID problem by [4], [15], and [16], respectively. However, these methods either needed a sophisticated
intrusion pattern repository, which requires substantial expertise to build and can hardly be complete and up-to-date or
required abundant amount of fully labeled data for training,
which is labor-intensive to annotate. Hence, it naturally leads
to the DA-based methods which can comfortably work under
challenging data-scarce IID scenarios.
DA and Intrusion Detection: DA leverages source domain
knowledge to facilitate better learning for data-scarce target
domains, and, hence, is suitable to tackle the intrusion detection for the data-scarce IoT domain. Vu et al. [17] utilized
two autoencoders on source and target data set and forced
the alignment of the bottleneck layers. Later, Ning [5] leveraged the Laddernet to tackle IID under a semi-supervised
setting. Hu et al. [6] presented a deep subdomain adaptation
network with attention mechanism that performed intrusion
knowledge transfer by minimizing local maximum mean discrepancy. However, these methods did not use PL assignments
to exploit unlabeled target domain and failed to perform DA
via a geometric graph-based approach, hence, did not preserve
geometric properties during intrusion knowledge transfer. On
the other hand, Chen et al. [18] tackled the intrusion domain
alignment problem via transfer neural tree (TNT), a unified framework that combined feature mapping, adaptation,
and classification. A generalized joint distribution adaptation
(G-JDA) approach was presented [9] to learn a pair of feature
projectors to eliminate the marginal and conditional distribution divergence. Yao et al. [19] proposed the DDA method
that applied an adaptive classifier to reduce distribution divergence and enlarge interclass divergence. The TNT, G-JDA,
and DDA applied direct prediction as PLs for unlabeled target instances and completely ignored the label neighborhood
information. Yao et al. [11] put forward the STN, a conditional
distribution alignment strategy with the help of a soft-label
paradigm. Singh et al. [20] presented the STAR framework,
which emphasized unlabeled target instances based on the distance with closest class prototypes during intrusion domain
alignment. Saito et al. [21] achieved intrusion knowledge
transfer by optimizing the minimax loss on the domain conditional entropy (MME). It utilized unlabeled target data
based on a threshold-based strategy. The APE [22] method
chose to alleviate intradomain discrepancy via three procedures, namely, Attraction, Perturbation, and Exploration. From
a clustering-based perspective, Li et al. [10] proposed crossdomain adaptive clustering (CDAC) to tackle the DA problem.
In MME, APE, and CDAC, unlabeled target instances will
be pseudo-labeled based on a threshold strategy. However,
when assigning PLs, these method either failed to jointly
consider geometric properties or assigned PLs in an isolated
manner that ignored the relationships between pseudo-labeled

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 12, 15 JUNE 2023

instances and their neighboring labeled instances, compromising accurate intrusion knowledge transfer. Some methods also
required a manual threshold set based on prior experience and
was not generalizable between tasks.
Tackling intrusion domain alignment from a graph perspective is also feasible. For example, the WCGN method matched
domains via graph learning [7], [8] to benefit the domain
alignment. Pilanci and Vural [23] proposed a graph base alignment method by transferring the graph spectrum information.
However, although these embedding-related methods can partially convey the geometric information of domains, learning a good embedding is highly data-dependent, hindering
their applicability. Besides, none of these graph-based methods solved the graph matching problem from a pure GGA
perspective, which left a void to be filled.
Our method tackles the HDA problem from a pure geometric graph perspective, which jointly considers several levels
of geometric property matching. The GGA method does not
require a huge amount of data for graph embedding learning
and enjoys a relatively low complexity. Besides, we utilize
a PLE mechanism which jointly accounts for the geometric properties and the neighborhood information, so that the
confident but wrong PL prediction that violates geometric
properties and near-boundary ambiguous PLs can be avoided
for positive transfer. Finally, we utilize the GGA method to
facilitate more accurate intrusion detection for the data-scarce
IoT domain.
III. M ODEL P RELIMINARY AND A RCHITECTURE
A. Model Preliminary
The GGA method works under a semi-supervised HDA
setting. It involves a source NI domain formulated as follows:
DS = {XS , YN } = {(xSi , ySi )}, i ∈ [1, nS ]
xSi ∈ RdS , ySi ∈ [1, K]

(1)

where the source NI domain contains nS traffic records with
their corresponding intrusion label. Each record is represented
using dS features, and there are K categories. Similarly, the
target II domain are defined as follows:
DTL = {XTL , YTL } = {(xTLi , yTLi )}, i ∈ [1, nTL ]


DTU = {XTU } = xTUj , j ∈ [1, nTU ]
DT = DTL ∪ DTU , xTLi , xTUj ∈ RdT , yTLi ∈ [1, K]
nT = nTL + nTU , nTL  nTU .

(2)

Under the semi-supervised setting, the target domain is
scarcely labeled, i.e., nTL  nTU . The source and target
domain present heterogeneities, such as belonging to different
feature spaces, i.e., dS = dT .
B. Graph Formulation
To perform the GGA, we formulate each intrusion domain
as a graph, i.e., GX = <VX , EX >, X ∈ {S, T}. Both domains
share K intrusion categories, therefore, each graph has K vertices, the vertex Vi is the centroid of the category i, denoted

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

WU et al.: HETEROGENEOUS DOMAIN ADAPTATION FOR IoT INTRUSION DETECTION

Fig. 3.

10767

Architecture of the GGA method.

as follows:

level. The motivation is to align the domain graphs in a finegrained manner, such that the shared classifier C yields the
best intrusion detection accuracy for unlabeled target domain.

ni

VXi =

X
1 
xXj , i ∈ [1, K], X ∈ {S, T}
i
nX j=1

(3)
IV. GGA A LGORITHM

where ni

is the number of records under category i. Both
graphs are formulated as a complete graph, the weight of edge
j
E<VXi , VX > is set to be the Euclidean distance between verj
tex VXi and VX . The corresponding WAMs are denoted as MS
and MT .
C. Model Architecture and Overview
The architecture of the GGA method has been shown in
Fig. 3. Each intrusion domain has a feature projector that maps
features into a common feature subspace with dimension dC .
The feature projector is defined as follows:

ES (xi ), if xi ∈ XS
f (xi ) =
ET (xi ), if xi ∈ XT = XTL ∪ XTU
f (xi ) ∈ RdC .

(4)

The GGA method will then utilize the PLE mechanism to
assign fine-grained PLs to unlabeled target data and avoid
error-prone PLs to mitigate negative transfer. To perform GGA
between these heterogeneous domains, the WAM of the source
data, the labeled target data, and the combination of labeled
and pseudo-labeled target data will be generated to confuse the
discriminator D. Highly similar WAMs indicate well-aligned
intrusion categories and the fine preservation of category-wise
interrelations and is equivalent with a perfect geometric graph
shape keeping. By fusing three WAMs, the geometric shape
of domain graphs are aligned, meanwhile, the labeled and
pseudo-labeled target data will be better fused together. After
keeping the shape, the domain graphs can still misalign due
to rotation and symmetry, which are mitigated by the rotation
avoidance mechanism and the center point matching. Besides,
categorical correlations yielded by the shared classifier C will
be preserved between domains, which acts as a vertex-level
alignment mechanism. Holistically, the GGA approach aligns
the domain graphs from general shape level to specific vertex

In this section, we will first introduce the PLE mechanism which facilitates better target participation during the
GGA process. Then, the GGA process and its constituting
components will be explained.
A. Pseudo-Label Election Mechanism
Assigning PLs to unlabeled target data can excavate its
potentials during intrusion knowledge transfer. However, erroneous PL assignment may mislead the model toward negative
transfer. Traditional efforts mainly assigned PL to instances
in an isolated manner, without considering the relationship
between labels, and suffered from issues such as confident
but geometrically-inconsistent PLs and near-support ambiguous PLs. Therefore, we utilize the PLE mechanism to mitigate
these issues as much as possible. The PLE jointly considers the
voting of NN prediction, the geometric properties, and neighborhood information. A PL assignment will only be made for
an instance if these three votes reach a consensus. When producing the geometric property-based PL, the category of the
most Cosine-similar labeled data centroid μiS+TL will be utilized as PLG for each unlabeled target instance and is defined
as follows:

(k)
i
PLiG = argmax COS μS+TL , xTU
k

(k)
μS+TL =

1



xi
(k)
(k)
nS + nTL
(k)
(k)
xi ∈X ∪X
S

(5)

TL

i , X (k)
where PLiG denotes the geometric-based PL for the xTU
S

denotes source instances from category k. If the NN-prediction
yields a confident PL prediction but is inconsistent with the
geometric similarity property, then such confident but contradictory PL will be rejected, as illustrated in Fig. 4(b). Besides,
the PLE will also consult the neighborhood information when
assigning PLs. If the K-nearest neighborhood around an unlabeled target instance cannot reach a majority agreement or

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

10768

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 12, 15 JUNE 2023

(a)

(b)

(c)

(d)

Fig. 4. Illustration of the PLE. (a) Original feature. (b) Avoid geometrically inconsistent PL via geometric disagreement. (c) Near-boundary ambiguous PL
assignment avoidable via neighborhood disagreement. (d) PLE’s assignment.

Fig. 5.

Illustration of the GGA method.

reach an agreement against the NN prediction or the geometric
vote, then such assignment will also be rejected. This is useful,
especially when deciding the PL for near-boundary unlabeled
instances, as illustrated in Fig. 4(c). Since the neighborhood
can be harder to reach an agreement near the boundary due to
ambiguity, the PLE can effectively get rid of near-boundary
PLs which are more likely to be erroneous. Overall, the PLE
will only assign confident PLs with probabilistic, geometric,
and neighborhood soundness, which can significantly boost
the PL accuracy and, therefore, lead to positive intrusion
knowledge transfer.
B. Geometric Graph Alignment
The GGA method has been illustrated in Fig. 5. It will perform GGA from the general graph granularity to the specific
vertex granularity, i.e., the shape keeping via confused discriminator (purple step), rotation avoidance mechanism (gray
step), center point matching against symmetry (pink step), and
the vertex-level alignment via semantic preservation (orange
step).
Shape Keeping: First, the GGA with align the graph shape
via a confused discriminator. We define the Same Shape Rule
as follows.
Definition 1 (Same Shape Rule): Both GS and GT have their
shape aligned with each other if and only if the WAMs MS
and MT are the same.
Specifically, with the help from the PLE, the GGA will
construct three WAMs: 1) the source WAM MS ; 2) the labeled
target WAM MTL ; and 3) a WAM based on both labeled and

pseudo-labeled target data MTL+PL . These WAMs will then
be flattened and feed into the discriminator D, a single-layer
neural network that tries to distinguish the origin of the input
WAM. The source domain WAM MS is assigned with domain
label 1, while target domain WAMs are assigned with domain
label 0. The shape keeping loss LSK is defined as follows:
LSK = log(D(MS ))

1
+
2

(1 − log(D(M))).

(6)

M∈{MTL ,MTL+PL }

The source and target projector will try to minimize the LSK
and let the discriminator D to be unable to distinguish the origin of the input WAMs, while the discriminator will try to stay
unconfused. Upon this minimax game reaches an equilibrium,
both GS and GT will have their shape aligned as indicated in
Fig. 5 (Mid), and the labeled and pseudo-labeled target data
will be better fused together.
Rotation Avoidance Against Rotated Misalignment: As
indicated in Fig. 5 (Mid), graph rotation can still cause
domain graph misalignment, even though the shape is aligned.
Therefore, to further align the domain graphs geometrically,
we define the Same Angle Rule as follows:
Definition 2 (Same Angle Rule): For graph GS and GT , the
Same Angle Rule holds if ∀i ∈ [1, K], 1 − COS(VSi , VTi ) = 0.
The GGA method will keep the Same Angle Rule holding
by minimizing the rotation loss, defined as follows:
LR =

K




1 − COS VSi , VTi .

(7)

i=1

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

WU et al.: HETEROGENEOUS DOMAIN ADAPTATION FOR IoT INTRUSION DETECTION

By minimizing LR , graph misalignment caused by rotation will
be prevented since the categorize-wise vertex angle is enforced
to be 0◦ .
Centre Point Matching Against Symmetric Misalignment: As
shown in the pink-boxed example in Fig. 5 (Mid), upon fixing
the graph shape and enforcing the Same Angle Rule, symmetry
can still cause misalignment. Therefore, we further define the
Same Centre Rule as follows:
Definition 3 (Same Centre Rule): For graph GS and GT ,
the Same Centre Rule holds if μS = μT , μX =
X
XX i , X ∈ {S, T}.
(1/nX ) ni=1
We minimize the centre point matching loss as follows:
LCP = ||μS − μT ||2 .

(8)

Enforcing the Same Centre Rule brings threefold advantages:
First, the graph misalignment caused by symmetry can be
prevented; Then, it boosts data participation during the intrusion knowledge transfer to fully excavate the potentials in all
data, irrespective of whether a PL is assigned or not; Finally,
despite its computational simplicity, it can boost the intrusion
detection performance as indicated by the experiments.
Vertex-Level Alignment via Semantic Preservation: The
above three steps focus on the overall graph level, in this step,
we shift our focus to the vertex granularity. Each vertex in
the domain graph represents an intrusion category centroid,
during prediction, it presents a unique probabilistic categorywise correlation. Use object as an example, a laptop should
be highly similar with other laptops, somewhat similar with a
TV screen, and very dissimilar with a bike, irrespective of its
domain origin. By enforcing the corresponding vertices from
both domain graphs to preserve the correlation semantic, it
in turn forces vertex-level alignment between domain graphs.
Specifically, for source category k, its correlation semantic is
defined as follows:
1 
C(f (xi ))
(9)
softmax
q(k) = (k)
T
n
(k)
S

xi ∈XS

(i)

where XS denotes category i source instances, C and f denote
the shared classifier and the feature projector, respectively, T
is a temperature hyperparameter that controls the correlation
semantic smoothness. Similarly, the correlation semantic of
each labeled target instance is defined as follows:
pi = softmax(C(f (xi ))), xi ∈ XTL .

(10)

To perform the semantic preservation, we minimize the vertexlevel alignment loss as follows:


1
q(yi ) log(pi ).
LVS = −
(11)
nTL
(xi ,yi )∈(XTL ,YTL )

Together with the supervision provided by the labeled target
instances, the final vertex-level alignment loss is defined as
follows:

1−α
LV =
Lce (C(f (xi )), yi )
nTL
(xi ,yi )∈(XTL ,YTL )

+ αLVS

(12)

10769

where Lce denotes cross entropy loss. By minimizing the
vertex-level alignment loss LV , it will enforce vertices in the
same category from different graphs to align with each other.
Otherwise, the correlation semantic will fail to be preserved.
GGA Theorem: The GGA forms the above mechanism into
a holistic framework and can align two domain graphs with
theoretical guarantee. We state the GGA Theorem as follows.
Theorem 1 (GGA Theorem): Given graph GS and GT , if the
Same Shape Rule, the Same Angle Rule, and the Same Centre
Rule hold simultaneously, then GS and GT must exactly align
with each other.
The proof of the GGA Theorem is as follows.
Proof: We prove the GGA Theorem by induction with
the help of contradiction.
Case 1: Both GS and GT have two vertices. Given that the
Same Angle Rule holds, both graphs must be parallel with
each other. Given that the Same Shape Rule holds, it enforces
the only edge in both graphs to have equal length. Therefore,
it is trivial to conclude that these two graphs are the same.
Case k: Both GS and GT have k vertices. The aforementioned three rules hold and GS and GT are aligned. We add an
additional vertex to GS and GT separately. Without breaking
any of the aforementioned three rules, the new graph GS and
GT also align with each other.
Proof Case k by Contradiction: Since under Case k, the prerequisite states that GS and GT align with each other, therefore,
we simply denote both of them as GX .
Case k1: If GX is asymmetric regarding any line, then it is
trivial that there is no possible strategy to add point differently
to GX to get GX and GX without violating the Same Centre
Rule.
Case k2: If GX is symmetric regarding a symmetric axis, to
stick to the Same Shape Rule and the Same Angle Rule, the
only possible strategy to add VSk+1 and VTk+1 is as follows: the
line crossing VSk+1 and VTk+1 should also cross-origin (Same
Angle Rule) and the center point of the symmetric axis (Same
Shape Rule). However, if we add VSk+1 and VTk+1 differently,
then they must be symmetric regarding the graph symmetric
axis, which violates the Same Centre Rule for the graphs.
Given that the GGA theorem holds, the constituting components of the GGA method can achieve a fine-grained GGA
with theoretical guarantee and benefit intrusion knowledge
transfer.
C. Overall Optimization Objective
Finally, the source labels provide supervision during the
training process with supervision loss defined as follows:

1
Lce (c(f (xi )), yi ). (13)
LSUP (XS , YS ) =
nS
(xi ,yi )∈(XS ,YS )

Overall, the optimization objective of GGA is as follows:
min max(LSUP + γ LSK + ηLR + λLCP + LV )

C,ES ,ET

D

(14)

where γ , η, and λ are hyperparameters controlling the influence of loss components during optimization. During initial
training stages, both domain graphs may suffer from immature shape, therefore, the γ is set to a relatively low value

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

10770

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 12, 15 JUNE 2023

to emphasize other components such as vertex-wise semantic
alignment, etc. As the training progresses, the γ will grow
linearly to gradually emphasize the importance of shape keeping. To form the optimization into an end-to-end procedure, we
follow [24] to apply the gradient reversal layer for the discriminator and optimize the model using the Adam gradient descent.
Upon the equilibrium of the above minimax game is reached,
the network training concludes, and the domain graphs can
be aligned in a fine-grained manner, which facilitates more
accurate intrusion detection for the target IoT domain.
V. E XPERIMENT
A. Experimental Data Sets
During experiments, we utilize five representative and
comprehensive intrusion detection data sets, which include
three NI data sets: 1) NSL-KDD; 2) UNSW-NB15; and
3) CICIDS2017, and two II data sets: 1) UNSW-BOTIOT and
2) UNSW-TONIOT.
NI Data Set: NSL-KDD The NSL-KDD data set [25] was
released in 2009, which addressed issues of the prior data set
KDD CUP99 [26] such as having lots of redundant records.
The NSL-KDD data set contains benign traffic with four types
of intrusions, such as probing attack, Denial-of-Service (DoS)
attack, etc. Following [13], we reasonably utilize 20% of the
data set. Each traffic record in the data set is represented using
41 features. We follow Harb et al. [27] to use the top 31 most
informative features as the feature representation. The data set
is denoted as K.
NI Data Set: UNSW-NB15: The UNSW-NB15 data set [28]
was created by UNSW in 2015 using the IXIA PerfectStorm
tool, which aimed to address the data quality issue and out-ofdate incomprehensive network flow issue observed in previous
data sets. The data set contains ten traffic categories, including
normal traffic, DoS attacks, reconnaissance attacks, etc. We
utilize 2700 traffic records, which follows the data set magnitude in [29]. The data set is represented using 49 features, we
perform preprocessing to remove four features having value 0
for nearly all records. The data set is denoted as N.
NI Data Set: CICIDS2017: The CICIDS2017 data set [30]
was released in 2017, which served as one of the most upto-date NI data sets with modern attack patterns. The data set
has seven types of intrusions with benign traffic, represented
in 77-D features. We utilize the 20% portion of the data set
provided by the data set creator to perform the model training
and testing. During preprocessing, we perform data deduplication and categorical-numerical entries conversion. Following
Stiawan et al. [31], we use features with top 40 information
gain as the feature space of the data set and denote the data
set as C.
II Data Set (UNSW-BOTIOT): The UNSW-BOTIOT data
set [32] was released in 2017 by UNSW, which presented
up-to-date modern attack scenarios captured based on a realistic testbed environment. The testbed environment deployed
IoT devices, such as weather station, smart fridges, etc.,
and utilized MQTT protocol, a lightweight IoT communication protocol commonly used in realistic IoT scenarios. The
data set quality has been carefully addressed, and the attack

diversity has been improved. The data set contains four categories, including normal traffic, DoS attacks, information theft
attacks, etc. Following [29], we utilize 10 000 data records.
The original data set utilizes a 46-D feature space. We follow
the data set creator’s advice to use top 10 most informative
features as the feature space. The data set is denoted as B.
II Data Set (UNSW-TONIOT): The UNSW-TONIOT data
set [33] serves as one of the latest II data sets [34], released
in 2021. It reflects modern IoT standards, protocols, and is captured on modern testbed consists of seven types of IoT devices,
such as smart fridge, modbus sensor, GPS tracker, etc. The
data set covers seven types of intrusions, including scanning
attacks, DoS attacks, etc. Heterogeneities present between IoT
devices as the features captured by each type of IoT device
have their own feature dimension. Following [29], [35], we utilize around 10% of the data set, and select the weather meter
and GPS tracker as the IoT devices used during experiments,
which are denoted as W and G, respectively.
Comprehensiveness of Data Sets: The data sets we utilized
are representative and comprehensive to verify the effectiveness of the proposed method. First, these data sets are widely
recognized and widely adopted by the research community
to testify intrusion detection effectiveness with thousands of
citations. Second, these data sets are developed and released
in recent years, some of them are release in 2021, therefore,
they can reflect current intrusion trends and methods. Finally,
these data sets are captured on realistic testbeds with largescale real IoT devices, and the sufficiency of the testbed is
recognized by the research community. Hence, these data sets
are representative with guaranteed comprehensiveness.
B. Shared Intrusion
The NI data sets and the II data sets can have at most
eight shared categories that can be transferred as intrusion
knowledge, such as DoS attack, password attack, backdoor
attack, etc. These shared intrusion categories account for
100%, 54.9%, 100%, 100%, and 98.3% the amount of records
in NSL-KDD, UNSW-NB15, CICIDS2017, UNSW-BOTIOT,
and UNSW-TONIOT data set, respectively. Therefore, transferring intrusion knowledge with wide coverage can effectively
detect most modern intrusions targeting the IoT domain.
C. Implementation Details
We implement the GGA method using the PyTorch deep
learning framework. Following [11], [36], feature projectors
are two-layer neural networks using LeakyReLu [37] as their
activation function. Both the shared classifier and the discriminator are implemented as single-layer neural networks.
The hyperparameter setting is fixed during all experiments
as follows: α = 0.1, γmin = 0.01, γmax = 0.1, η = 0.01,
λ = 0.01, dC = 3, T = 5, and #neighbour = 4. Note
that γ will increase linearly from γmin to γmax as the training progresses. To emphasize the target data scarcity, we set
nTL : nTU = 1 : 50 as the default ratio. We also conduct the
parameter sensitivity analyses to verify the stable and robust
performance of the GGA method. Following [29], [38], we

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

WU et al.: HETEROGENEOUS DOMAIN ADAPTATION FOR IoT INTRUSION DETECTION

10771

TABLE I
I NTRUSION D ETECTION ACCURACY U NDER D EFAULT DATA S CARCITY R ATIO nTL : nTU = 1 : 50

use unlabeled target prediction accuracy as our major evaluation metric, and also use the category-weighted precision
(P), recall (R), F1-score (F), and Area under the ROC Curve
(A) [39], [40] to evaluate the GGA performance. Specifically,
we define true positive TP(k) as the number of category k
intrusions being corrected identified, similar for true negative TN(k) , false positive FP(k) , and false negative FN(k) . The
mathematical definitions of evaluation metrics are as follows:

K 
(k) + TN(k)
k=1 TP
Accuracy =
(15)
nTU
K
(k)

|XTU
|
TP(k)
Precision =
·
nTU TP(k) + FP(k)
k=1
=
Recall =

K

|X (k) |
TU

k=1
K

k=1

=
F1 =

nTU

TU

k=1

(16)

(k)
|XTU
|
TP(k)
·
nTU TP(k) + FN(k)

K

|X (k) |
k=1
K


· Precision(k)

nTU

· Recall(k)

(17)

(k)
|XTU
| 2 · Precision(k) · Recall(k)
·
. (18)
nTU
Precision(k) + Recall(k)

Besides, metrics A (AUC) represents the area under the ROC
curve, a curve plotting the TP rate and the FP rate.

pseudo-label strategy using geometric property as a reference, however, the neighborhood information is still
ignored. Besides, STN utilizes a soft-label strategy, lacking emphasize on confident predictions. The GGA is the
only method that jointly considers both the geometric
property and neighborhood information, while avoiding
hard-to-set threshold.
2) From the domain alignment perspective, these baselines
apply diverse techniques, such as CDAC’s adversarial adaptive clustering, MME’s alternated conditional
entropy minimization, STN’s joint distribution matching, etc. However, these methods fail to explicitly
conduct domain alignment from a geometric graph
perspective. To our best knowledge, there lacks a similar pure geometric-based graph baseline method, the
WCGN is a comparable state-of-the-art graph method
based on graph learning framework. However, since a
proper graph learning requires both sufficient data and
a high complexity, it is challenging under the datascarce and computationally constrained IoT scenario.
Conversely, the GGA performs knowledge transfer via a
GGA perspective. It fills the void of previous methods,
avoids heavy data dependency, and has a relatively low
complexity.
Therefore, these state-of-the-art baseline methods are representative and can be used to verify the superiority of the GGA
method from different perspectives.

D. State-of-the-Art Baselines

E. Performance Evaluation

We utilize nine state-of-the-art comparing methods, including TNT [18], MME [21], STN [11], APE [22], DDAS,
DDAC [19], WCGN [7], [8], CDAC [10], and STAR [20]. All
of them are from top-tier conferences and journals, and eight
of them are proposed between 2019 and 2021. We summarize
their differences with GGA as follows.
1) From the pseudo-labeling perspective, the DDAC,
DDAS, WCGN, and TNT utilize predicted hard pseudo
label for target instances and ignore both the geometric property and neighborhood information. On the
other hand, MME, CDAC, and APE involve thresholdbased pseudo-label strategy. However, setting thresholds properly requires expertise experience and has
compromised flexibility. Both APE and STAR apply

Performance Analysis Under Default Data Scarcity Ratio:
We analyze the performance against state-of-the-art counterparts under the default target data scarcity ratio. As indicated
in Table I, the GGA clearly outperforms all comparing methods by at least 4.2%. The best-performed comparing method
WCGN utilizes graph learning framework, however, it does not
perform well under the data-scarce IoT scenario, its PL assignment strategy also lacks consideration of geometric properties
and assigns PL in an isolated manner. Hence, it is natural to
observe a performance boost achieved by the GGA.
Performance Analysis Under Diverse Data Scarcity Ratios:
To verify the effectiveness and robustness of the GGA under
varied target data scarcities, we vary the data scarcity ratio
nTL : nTU between 1 : 10 and 1 : 100. Following [5], [11], [36],

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

10772

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 12, 15 JUNE 2023

TABLE II
I NTRUSION D ETECTION ACCURACY U NDER VARIED nTL : nTU R ATIOS

TABLE III
I NTRUSION D ETECTION P ERFORMANCE U SING VARIOUS E VALUATION M ETRICS U NDER D EFAULT DATA S CARCITY

the 1 : 100 case is enough to represent an extreme datascarce setting. We randomly pick three tasks and present
their performance in Table II. As we can observe, the GGA
achieves the best intrusion detection performance among all
three tasks under all data scarcity settings. It yields a 4.36%
and 8.29% overall average performance increase compared
with the best and second best-performed methods WCGN
and STN. Moreover, under the extreme data scarcity case, the
performance boost achieved by GGA reaches 4.6% and 8.63%
compared with the best and second best-performed counterpart
WCGN and DDAC, and only presents a 0.87% drop compared
with the performance under the 1 : 50 case, which further verifies the superiority and robustness of the GGA when working
under diverse data scarcity conditions.
Performance Analysis Using Diverse Evaluation Metrics:
To further verify the effectiveness of the GGA method using
evaluation metrics other than accuracy, we randomly select
two tasks and record the performance using another four evaluation metrics, and present the result in Table III. We observe
GGA achieves superior performance on all evaluation metrics. Specifically, the highest precision indicates that most of
the flagged malicious decisions made by GGA are correct.
The highest recall means the GGA can flag most amount of
intrusions among all malicious traffic. As a harmonic mean
of precision and recall, the highest F1-score indicates that the
GGA can balance properly between flagging malicious actions
and avoiding triggering false alarms. Finally, the highest AUC
shows the GGA can effectively distinguish malicious intrusions from normal traffic. Together, these evaluation metrics
verify the effectiveness of the GGA method and its real-world
usability in terms of false alarm avoidance.

Fig. 6.
PL accuracy under default data scarcity ratio between ablated
experiments.

Intrusion Detection Performance Summary: We verify the
GGA has the best performance on all tasks when evaluated
using all metrics. Therefore, it is sufficient to indicate that

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

WU et al.: HETEROGENEOUS DOMAIN ADAPTATION FOR IoT INTRUSION DETECTION

Fig. 7.
PL accuracy under default data scarcity ratio within a single
experiment that utilizes full PLE.

the GGA method can accurately flag malicious traffic while
not causing severe false alarms. The best F1-score and AUC
score performance also verify the GGA has the best ability to
distinguish benign traffic and different intrusions. Having such
capability promotes the real-world usefulness of GGA when
performing effective intrusion detection.
F. Pseudo-Label Accuracy Analysis
To justify the efficacy of the PLE mechanism, we perform
PL accuracy analysis in three ways: 1) analyze the PL accuracy
between ablated experiments under default data scarcity ratio;
2) analyze the PL accuracy of different PLE configurations in
a single full PLE setting under default data scarcity ratio; and
3) perform 2) under varied data scarcity ratios to verify the
robustness of the PLE.
The results on two randomly selected tasks for case 1) has
been illustrated in Fig. 6. Note that N, G, and K represent NN

Fig. 8.

10773

Within-experiment PL accuracy under varied data scarcity ratios.

prediction vote, geometric property vote, and neighborhood
vote, respectively. The height of each bar represents percentage
of unlabeled target data being pseudo-labeled, and red–green
color and the value written on each bar indicates the accuracy
of PL assignment. As we can observe, using the full PLE
yields advantages in threefold.
1) The full PLE achieves the highest PL accuracy during all training stages. During the beginning stage, to
avoid blindly generating a vast amount of false PLs and
mislead the alignment process, the full PLE can even
temporarily generate no PLs, since generating PL blindly
can only deteriorate the alignment process.
2) The full PLE can reach a relatively high PL accuracy
around 86.6%–90% even at the intermediate training
stage, which guides the aligning process positively by
fully exploiting the unlabeled target data.
3) The full PLE eventually achieves a PL accuracy around
92.5%–96.2%, which indicates the superiority of PLE on

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

10774

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 12, 15 JUNE 2023

TABLE IV
A BLATION S TUDY G ROUP A: I NTRUSION D ETECTION ACCURACY OF GGA W ITH A BLATED GGA C OMPONENTS

TABLE V
A BLATION S TUDY G ROUP B: I NTRUSION D ETECTION ACCURACY OF GGA W ITH A BLATED PLE C OMPONENTS

accurate PL assignment. Although the full PLE may not
generate the highest amount of PLs, however, the accuracy matters more than the amount, as indicated by the
superior performance achieved by the full PLE during
the ablation study.
Besides the PL accuracy analysis performed between
ablated experiments, we also perform the PL accuracy analysis within a single full PLE experiment under three randomly
picked tasks. As indicated in Fig. 7, the within-experiment
performances also comply with the advantages summarized
above. The full PLE can stably achieve the highest PL assignment accuracy during all training stages. During each stage,
ablating any PLE-constituting component will cause the PL
accuracy to drop significantly. This result further verifies the
usability of all components considered in the PLE.
To demonstrate the robustness of the PLE under varied
data scarcities, the within-experiment PL accuracy is analyzed
under varied data scarcity ratios, as indicated in Fig. 8. Under
a relatively low-data scarcity case, the PLE can achieve a
99.06% PL accuracy during the final training stage. Even
under the extreme data scarcity case, the PL accuracy only
drops by 4.27% compared with the 1 : 10 case, which
demonstrates that under varied data scarcities, the PLE can
work robustly to generate accurate PL assignment and benefit
positive intrusion knowledge transfer during the GGA process.
G. Ablation Study
We further investigate the efficacy of GGA’s constituting
components. Ablation group A has the corresponding GGA
components in (14) being turned off. Ablation group B has
different PLE voters being ablated. Ablation group C compares
GGA with the method that uses the direct vertex Euclidean
distance alignment as an alternative, which is defined as follows:
min

K 

i

VAi − VBi

2

(A,B)

(A, B) ∈ {(S, TL + PL), (S, S + TL + PL)
(TL + PL, S + TL + PL)}

(19)

TABLE VI
A BLATION S TUDY G ROUP C: I NTRUSION D ETECTION ACCURACY OF
M ETHODS W ITH D IFFERENT G RAPH A LIGNMENT M ECHANISMS

where S + TL + PL stands for combining instances from the
source, labeled-target, and pseudo-labeled target domains.
As indicated in Tables IV–VI, the full GGA outperforms all
its ablated counterparts by 3.4% on average, verifying positive
contributions made by all constituting components toward a
fine-grained GGA. In ablation group A, the rotation avoidance
mechanism is the best performance contributor with 4.9% of
performance boost, followed by the centre matching, shapekeeping mechanism and vertex-level semantic preservation. In
ablation group B, the results verify that all three voting components are indispensable. The performance will drop by 3.3% on
average without any one of them. Finally, in ablation group C,
a 2.8% performance reduction is observed by the Euclidean
distance-based pure vertex alignment procedure. It is natural to
observe since there are huge heterogeneities between domains,
therefore, pure vertex-level distance-based alignment may not
be strong enough to enforce a fine-grained graph alignment,
which results in degraded intrusion knowledge transfer. By
jointly considering several granularities from shape keeping to
vertex-level alignment, the GGA can facilitate a finer alignment
and an enhanced intrusion detection performance.
H. Hypothesis Testing for Ablation Study
To verify the statistical significance of the contributions
made by each constituting component, i.e., the performance
boost is not observed randomly by chance, we perform significance T-test on three randomly selected tasks. As illustrated
in Fig. 9, the gray shaded area denotes the significant threshold

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

WU et al.: HETEROGENEOUS DOMAIN ADAPTATION FOR IoT INTRUSION DETECTION

(a)

(b)

10775

(c)

Fig. 9. Significance T-tests on three randomly selected tasks have been performed to verify the statistical soundness of the contributions from different
constituting components of the GGA. The gray shaded area denotes the significant threshold − log(0.05). Among each dimension, the wider the coverage is
the more significant the contribution is on that ablated component. (a) K→B. (b) N→G. (c) C→W.

Fig. 10. Parameter sensitivity analysis of the GGA method for hyperparameters α, γ , η, λ, and # neighbour under their corresponding reasonable range. As
shown in the legend, the solid and dashed horizontal lines indicate the best-comparing method and the best-performed GGA ablated counterpart under each
task, respectively.

− log(0.05). Among each dimension, the wider the coverage
is, the more significant the contribution is on that ablated component. As we can see from Fig. 9, the colored area has wider
coverage than the gray shaded area among all dimensions,
which indicates that the contributions made by all constituting components have statistical soundness. Therefore, all
proposed components are indispensable for GGA to achieve a
fine-grained intrusion knowledge transfer via graph alignment.

TABLE VII
C OMPARISON ON T RAINING T IME P ER E POCH (S ECOND )

TABLE VIII
C OMPARISON ON I NFERENCE T IME P ER I NSTANCE
(M ICROSECOND = 10−6 S ECOND )

I. Parameter Sensitivity
The parameter sensitivity of the GGA method has been
illustrated in Fig. 10. The GGA shows relatively stable
performance under these hyperparameter ranges without
showing severe fluctuations. Besides, the GGA outperforms the best-performed comparing method under nearly
all hyperparameter ranges. Additionally, the GGA constantly
shows superior performance than its best-ablated counterpart.
Therefore, we verify that the GGA method is robust on varied
hyperparameter settings.
Besides, during all experiments, only a fixed set of hyperparameters is used to tackle diverse data domains. The GGA can
constantly show satisfying performance without the need to
perform time-consuming hyperparameter resetting. Therefore,
it further demonstrates the robustness of GGA on hyperparameters and its usefulness when tackling diverse intrusion
data domains.
J. Computational Efficiency
Finally, to verify the computational efficiency of the GGA
method, we measure both the training time per epoch and
inference time per instance and make comparison between two

best-performed baseline counterparts. The results are presented
in Tables VII and VIII. As we can observe, the GGA achieves
the best training and inference efficiency. Specifically, the
GGA trains 31 times and 6.67% faster than DDAC and
WCGN, respectively. Besides, the GGA also achieves the
fastest inference speed, which outperforms the best-performed
counterpart WCGN by 15.79%. Hence, it verifies the efficiency of the GGA, making it suitable to be used under
computationally-constrained IoT scenarios.
VI. C ONCLUSION
In this article, we utilize the knowledge-rich NI domain
to facilitate accurate intrusion detection for the data-scarce
IoT domain. We tackle this HDA problem through a GGA
approach. First, a PLE mechanism is employed to exploit
the unlabeled target instances, which jointly considers the
network prediction, geometric property, and neighborhood

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

10776

IEEE INTERNET OF THINGS JOURNAL, VOL. 10, NO. 12, 15 JUNE 2023

TABLE IX
ACRONYM TABLE

caused by rotation and symmetry, respectively. Additionally,
the vertex-level semantic is preserved to facilitate a more
fine-grained graph alignment. By forming these mechanisms
into a holistic whole, the GGA method can align intrusion
graphs in a fine-grained manner, which benefits the intrusion
knowledge transfer between domains. Comprehensive experiments demonstrate the state-of-the-art performance of the
GGA method. Insight analysis also verifies the usefulness of
each constituting component of the GGA method.
A PPENDIX

TABLE X
N OTATION TABLE

Acronym Table: For better readability, we provide the following acronym table for reference. Note that all acronyms
are defined in the main text as well as at the first time they
are introduced.
Notation Table: We provide a notation table for better
readability.
R EFERENCES

information to boost the PL assignment accuracy. The PLE
avoids geometrically diverged confident but wrong PLs and
near-boundary ambiguous PLs. Then, both intrusion domains
are formulated as graphs, with the GGA performed using four
mechanisms, from general graph granularity to vertex-level
alignment. Specifically, the graph shape is kept via a confused discriminator that is incapable to distinguish the origin
of WAMs. Besides, the rotation avoidance mechanism and the
center point matching mechanism avoid graph misalignment

[1] M. N. Bhuiyan, M. M. Rahman, M. M. Billah, and D. Saha, “Internet
of Things (IoT): A review of its enabling technologies in healthcare
applications, standards protocols, security, and market opportunities,”
IEEE Internet Things J., vol. 8, no. 13, pp. 10474–10498, Jul. 2021.
[2] J. Wu et al., “Joint semantic transfer network for IoT intrusion
detection,” IEEE Internet Things J., early access, Nov. 1, 2022,
doi: 10.1109/JIOT.2022.3218339.
[3] C. Dietz et al., “IoT-botnet detection and isolation by access routers,”
in Proc. 9th Int. Conf. Netw. Future (NOF), 2018, pp. 88–95.
[4] C. D. McDermott, F. Majdani, and A. V. Petrovski, “Botnet detection
in the Internet of Things using deep learning approaches,” in Proc. Int.
Joint Conf. Neural Netw. (IJCNN), 2018, pp. 1–8.
[5] J. Ning et al., “Malware traffic classification using domain adaptation and ladder network for secure industrial Internet of Things,” IEEE
Internet Things J., vol. 9, no. 18, pp. 17058–17069, Sep. 2022.
[6] X. Hu, C. Zhu, G. Cheng, R. Li, H. Wu, and J. Gong, “A deep subdomain
adaptation network with attention mechanism for malware variant traffic
identification at an IoT edge gateway,” IEEE Internet Things J., early
access, Mar. 21, 2022, doi: 10.1109/JIOT.2022.3160755.
[7] Z. Wang, Y. Luo, Z. Huang, and M. Baktashmotlagh, “Prototypematching graph network for heterogeneous domain adaptation,” in Proc.
28th ACM Int. Conf. Multimedia, 2020, pp. 2104–2112.
[8] L. Wang, C. Huang, W. Ma, X. Cao, and S. Vosoughi, “Graph embedding
via diffusion-wavelets-based node feature distribution characterization,”
in Proc. 30th ACM Int. Conf. Inf. Knowl. Manag., 2021, pp. 3478–3482.
[9] Y.-T. Hsieh, S.-Y. Tao, Y.-H. H. Tsai, Y.-R. Yeh, and Y.-C. F. Wang,
“Recognizing heterogeneous cross-domain data via generalized joint distribution adaptation,” in Proc. IEEE Int. Conf. Multimedia Expo (ICME),
2016, pp. 1–6.
[10] J. Li, G. Li, Y. Shi, and Y. Yu, “Cross-domain adaptive clustering for
semi-supervised domain adaptation,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit., 2021, pp. 2505–2514.
[11] Y. Yao, Y. Zhang, X. Li, and Y. Ye, “Heterogeneous domain adaptation
via soft transfer network,” in Proc. 27th ACM Int. Conf. Multimedia,
2019, pp. 1578–1586.
[12] C. Jun and C. Chi, “Design of complex event-processing IDS in Internet
of Things,” in Proc. 6th Int. Conf. Meas. Technol. Mechatronics Autom.,
2014, pp. 226–229.
[13] E. Anthi, L. Williams, M. Słowińska, G. Theodorakopoulos, and
P. Burnap, “A supervised intrusion detection system for smart home
IoT devices,” IEEE Internet Things J., vol. 6, no. 5, pp. 9042–9053,
Oct. 2019.
[14] P. Shukla, “ML-IDS: A machine learning approach to detect wormhole
attacks in Internet of Things,” in Proc. Intell. Syst. Conf. (IntelliSys),
2017, pp. 234–240.
[15] M. Ge, X. Fu, N. Syed, Z. Baig, G. Teo, and A. Robles-Kelly, “Deep
learning-based intrusion detection for IoT networks,” in Proc. IEEE 24th
Pac. Rim Int. Symp. Depend. Comput. (PRDC), 2019, pp. 256–265.
[16] Y. Meidan et al., “N-BaIoT—Network-based detection of IoT botnet
attacks using deep autoencoders,” IEEE Pervasive Comput., vol. 17,
no. 3, pp. 12–22, Jul.–Sep. 2018.

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.

WU et al.: HETEROGENEOUS DOMAIN ADAPTATION FOR IoT INTRUSION DETECTION

[17] L. Vu, Q. U. Nguyen, D. N. Nguyen, D. T. Hoang, and E. Dutkiewicz,
“Deep transfer learning for IoT attack detection,” IEEE Access, vol. 8,
pp. 107335–107344, 2020.
[18] W.-Y. Chen, T.-M. H. Hsu, Y.-H. H. Tsai, Y.-C. F. Wang, and
M.-S. Chen, “Transfer neural trees for heterogeneous domain adaptation,” in Proc. Eur. Conf. Comput. Vis., 2016, pp. 399–414.
[19] Y. Yao, Y. Zhang, X. Li, and Y. Ye, “Discriminative distribution alignment: A unified framework for heterogeneous domain adaptation,”
Pattern Recognit., vol. 101, May 2020, Art. no. 107165.
[20] A. Singh et al., “Improving semi-supervised domain adaptation using
effective target selection and semantics,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2021, pp. 2709–2718.
[21] K. Saito, D. Kim, S. Sclaroff, T. Darrell, and K. Saenko, “Semisupervised domain adaptation via minimax entropy,” in Proc. IEEE/CVF
Int. Conf. Comput. Vis., 2019, pp. 8050–8058.
[22] T. Kim and C. Kim, “Attract, perturb, and explore: Learning a feature
alignment network for semi-supervised domain adaptation,” in Proc. Eur.
Conf. Comput. Vis., 2020, pp. 591–607.
[23] M. Pilanci and E. Vural, “Domain adaptation on graphs by learning
aligned graph bases,” IEEE Trans. Knowl. Data Eng., vol. 34, no. 2,
pp. 587–600, Feb. 2022.
[24] Y. Ganin and V. Lempitsky, “Unsupervised domain adaptation by backpropagation,” in Proc. Int. Conf. Mach. Learn., 2015, pp. 1180–1189.
[25] M. Tavallaee, E. Bagheri, W. Lu, and A. A. Ghorbani, “A detailed analysis of the KDD CUP 99 data set,” in Proc. IEEE Symp. Comput. Intell.
Security Defense Appl., 2009, pp. 1–6.
[26] S. Hettich, “KDD cup 1999 data,” Data Set, Dept. Inf. Comput. Sci.,
Univ. California, Los Angeles, CA, USA, 1999.
[27] H. M. Harb, A. A. Zaghrot, M. A. Gomaa, and A. S. Desuky, “Selecting
optimal subset of features for intrusion detection systems,” Adv. Comput.
Sci. Technol., vol. 4, no. 2, pp. 179–192, 2011.
[28] N. Moustafa and J. Slay, “UNSW-NB15: A comprehensive data set for
network intrusion detection systems (UNSW-NB15 network data set),”
in Proc. Mil. Commun. Inf. Syst. Conf. (MilCIS), 2015, pp. 1–6.
[29] O. Alkadi, N. Moustafa, B. Turnbull, and K.-K. R. Choo, “A deep
blockchain framework-enabled collaborative intrusion detection for protecting IoT and cloud networks,” IEEE Internet Things J., vol. 8, no. 12,
pp. 9463–9472, Jun. 2021.
[30] I. Sharafaldin, A. H. Lashkari, and A. A. Ghorbani, “Toward generating
a new intrusion detection dataset and intrusion traffic characterization,”
in Proc. ICISSP, vol. 1, 2018, pp. 108–116.
[31] Kurniabudi, D. Stiawan, Darmawijoyo, M. Y. B. Idris, A. M. Bamhdi,
and R. Budiarto, “CICIDS-2017 dataset feature analysis with
information gain for anomaly detection,” IEEE Access, vol. 8,
pp. 132911–132921, 2020.
[32] N. Koroniotis, N. Moustafa, E. Sitnikova, and B. Turnbull, “Towards
the development of realistic botnet dataset in the Internet of Things
for network forensic analytics: Bot-IoT dataset,” Future Gener. Comput.
Syst., vol. 100, pp. 779–796, Nov. 2019.
[33] T. M. Booij, I. Chiscop, E. Meeuwissen, N. Moustafa, and
F. T. H. den Hartog, “ToN_IoT: The role of heterogeneity and the need
for standardization of features and attack types in IoT network intrusion data sets,” IEEE Internet Things J., vol. 9, no. 1, pp. 485–496,
Jan. 2022.
[34] G. Abdelmoumin, D. B. Rawat, and A. Rahman, “On the performance of
machine learning models for anomaly-based intelligent intrusion detection systems for the Internet of Things,” IEEE Internet Things J., vol. 9,
no. 6, pp. 4280–4290, Mar. 2022.
[35] H. Qiu, T. Dong, T. Zhang, J. Lu, G. Memmi, and M. Qiu, “Adversarial
attacks against network intrusion detection in IoT systems,” IEEE
Internet Things J., vol. 8, no. 13, pp. 10327–10335, Jul. 2021.
[36] S. Li, B. Xie, J. Wu, Y. Zhao, C. H. Liu, and Z. Ding, “Simultaneous
semantic alignment network for heterogeneous domain adaptation,” in
Proc. 28th ACM Int. Conf. Multimedia, 2020, pp. 3866–3874.
[37] A. L. Maas, A. Y. Hannun, and A. Y. Ng, “Rectifier nonlinearities
improve neural network acoustic models,” in Proc. ICML, vol. 30, 2013,
p. 3.
[38] J. Li, Z. Zhao, R. Li, and H. Zhang, “AI-based two-stage intrusion detection for software defined IoT networks,” IEEE Internet Things J., vol. 6,
no. 2, pp. 2093–2102, Apr. 2019.
[39] M. A. Ferrag, L. Maglaras, S. Moschoyiannis, and H. Janicke, “Deep
learning for cyber security intrusion detection: Approaches, datasets,
and comparative study,” J. Inf. Security Appl., vol. 50, Feb. 2020,
Art. no. 102419.
[40] S. Zavrak and M. İskefiyeli, “Anomaly-based intrusion detection from
network flow features using variational autoencoder,” IEEE Access,
vol. 8, pp. 108346–108358, 2020.

10777

Jiashu Wu (Graduate Student Member, IEEE)
received the B.Sc. degree in computer science
and financial mathematics and statistics from
The University of Sydney, Camperdown, NSW,
Australia, in 2018, and the M.IT. degree in artificial intelligence from the University of Melbourne,
Parkville, VIC, Australia, in 2020. He is currently
pursuing the Ph.D. degree with Shenzhen Institute
of Advanced Technology, Chinese Academy of
Sciences, Shenzhen, China, and the University of
Chinese Academy of Sciences, Beijing, China.
His research interests include machine learning and cloud computing.
Hao Dai (Graduate Student Member, IEEE)
received the B.S. and M.Sc. degrees in communication and electronic technology from Wuhan
University of Technology, Wuhan, China, in 2015
and 2017, respectively. He is currently pursuing the Ph.D. degree with Shenzhen Institute
of Advanced Technology, Chinese Academy of
Sciences, Shenzhen, China, and the University of
Chinese Academy of Sciences, Beijing, China.
His research interests include mobile edge computing, federated learning and deep reinforcement
learning.
Yang Wang (Member, IEEE) received the B.Sc.
degree in applied mathematics from the Ocean
University of China, Qingdao, China, in 1989, the
M.Sc. degree in computer science from Carlton
University, Ottawa, ON, Canada, in 2001, and
the Ph.D. degree in computer science from the
University of Alberta, Edmonton, AB, Canada, in
2008.
He is currently with the Shenzhen Institutes
of Advanced Technology, Chinese Academy of
Sciences, Beijing, China, as a Professor and as an
Adjunct Professor with Xiamen University, Xiamen, China. His research
interests include service and cloud computing, programming language implementation, and software engineering.
Dr. Wang was an Alberta Industry Research and Development Associate
from 2009 to 2011, and a Canadian Fulbright Scholar from 2014 to 2015.
Kejiang Ye (Member, IEEE) received the B.Sc. and
Ph.D. degrees in computer science from Zhejiang
University, Hangzhou, China, in 2008 and 2013
respectively.
He was also a joint Ph.D. student with
The University of Sydney, Camperdown, NSW,
Australia, from 2012 to 2013. After graduation, he
worked as a Postdoctoral Researcher with Carnegie
Mellon University, Pittsburgh, PA, USA, from 2014
to 2015 and Wayne State University, Detroit, MI,
USA, from 2015 to 2016. He is currently an
Associate Professor with the Shenzhen Institute of Advanced Technology,
Chinese Academy of Science, Beijing, China. His research interests focus
on the performance, energy, and reliability of cloud computing and network
systems.
Chengzhong Xu (Fellow, IEEE) received the Ph.D.
degree from The University of Hong Kong, Hong
Kong, in 1993.
He is currently the Dean of the Faculty of
Science and Technology with the University of
Macau, Macau, China, and the Director with
the Institute of Advanced Computing and Data
Engineering, Shenzhen Institutes of Advanced
Technology, Chinese Academy of Sciences, Beijing,
China. He has published more than 200 papers
in journals and conferences. His research interest
includes parallel and distributed systems, service and cloud computing, and
software engineering.
Dr. Xu serves on a number of journal editorial boards, including IEEE T RANSACTIONS ON C OMPUTERS, IEEE T RANSACTIONS ON
PARALLEL AND D ISTRIBUTED S YSTEMS, IEEE T RANSACTIONS ON
C LOUD C OMPUTING, Journal of Parallel and Distributed Computing, and
China Science Information Sciences.

Authorized licensed use limited to: LNM Institute of Information Technology. Downloaded on June 24,2026 at 07:37:02 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
