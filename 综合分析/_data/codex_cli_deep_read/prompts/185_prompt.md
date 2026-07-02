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
# [185] CaCo: Attributed Network Anomaly Detection via Canonical Correlation Analysis
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
编号：185
题名：CaCo: Attributed Network Anomaly Detection via Canonical Correlation Analysis
年份：2023
DOI：10.1109/tii.2023.3266406
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2023.3266406.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\185.txt
- 原始字符数：42571
- 本次发送字符数：42571
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 1, JANUARY 2024

461

CaCo: Attributed Network Anomaly Detection
via Canonical Correlation Analysis
Ruidong Wang , Fengbin Zhang , Xunhua Huang , Chongrui Tian, Liang Xi ,
and Haoyi Fan , Member, IEEE

Abstract—Capturing the complex interaction between
the node attribute and the network structure is important
for attributed network embedding and anomaly detection.
However, there are few methods to explicitly model the
correlation between these two views of the node attribute
and the network structure. In this article, we propose an
attributed network anomaly detection (CaCo) method based
on the canonical correlation analysis, which assumes that
there should be a strong correlation between the attribute
and structure features of normal nodes, and a weak correlation one between those abnormal nodes, in the attributed
networks. Consequently, a joint learning mechanism is designed in CaCo to explicitly measure the correlation between two views in the latent space. Specifically, the backbone of a weight-sharing graph convolutional network is
employed to encode the node feature from two views of
attribute and structure in the latent space, respectively.
Then, a Kullback–Leibler divergence regularization is used
to align the distributions of the two views. Finally, the parameters of CaCo are optimized by maximizing the correlation between attribute and structure features of normal
nodes in the training phase, and anomalies can be detected by measuring the correlation between two views in
the testing phase. Extensive experiments on six real-world
datasets demonstrate the effectiveness of the proposed
method compared to the state-of-the-art techniques.
Index Terms—Anomaly detection, attributed network embedding, canonical correlation analysis (CCA), graph neural networks (GNNs).

I. INTRODUCTION
TTRIBUTED networks are typical graph data whose
nodes represent entities and links indicate the relationship
between entities [1], [2]. In recent years, a lot of researchers

A

Manuscript received 31 January 2023; accepted 28 March 2023. Date
of publication 11 April 2023; date of current version 11 December 2023.
This work was supported in part by the Key Project of Colleges and
Universities of Henan Province under Grant 23A52002 and in part by the
Science and Technology Innovation 2030-“New Generation of Artificial
Intelligence” Major Project under Grant 2021ZD0111000. Paper no. TII23-0324. (Corresponding authors: Fengbin Zhang; Haoyi Fan.)
Ruidong Wang, Fengbin Zhang, Xunhua Huang, Chongrui Tian, and
Liang Xi are with the School of Computer Science and Technology,
Harbin University of Science and Technology, Harbin 150080, China (email: iswangrd@gmail.com; zhangfengbin@hrbust.edu.cn; 1820410060
@stu.hrbust.edu.cn; 191040004@stu.hrbust.edu.cn; xiliang@hrbust.
edu.cn).
Haoyi Fan is with the School of Computer and Artificial Intelligence, Zhengzhou University, Zhengzhou 450001, China (e-mail: fanhaoyi@zzu.edu.cn).
Color versions of one or more figures in this article are available at
https://doi.org/10.1109/TII.2023.3266406.
Digital Object Identifier 10.1109/TII.2023.3266406

have focused on graph analysis, such as node classification,
link prediction, and anomaly detection [1], [3], [4]. Among
them, attributed network anomaly detection is an important
problem worth studying, which aims to detect nodes whose
behavior is different from the majority of nodes. However, in
attributed networks, anomalies are diverse owing to the complex
interaction of network structure and node attributes. Due to
the impact of network structure and node attributes of graph
learning, traditional anomaly detection methods [5], [6] are
unable to capture the complete information of the graph for
attributed network anomaly detection.
Recently, various methods of attributed network anomaly
detection have been proposed. Most of them focus on learning the node representation in the latent space, and detecting
the anomalous nodes by the reconstruction error or traditional
anomaly detection methods [7], [8]. Shallow methods [9], [10]
utilize shallow mechanisms to capture the interactions between
network structure and node attributes, which cannot fully address the challenges of high-dimensional feature computation.
Graph neural networks (GNNs)-based methods [11], [12], [13],
[14] leverage the advantages of the graph convolutional neural
network on graph data to extract the low-dimensional node
embedding and detect the anomalous nodes by one-class methods or reconstruction errors. Besides, some methods based on
self-supervised learning (SSL) [15], [16], [17] learn data representations by maximizing the information from the two data
augmentations of the inputs and using the data representations
for downstream tasks.
Although existing methods have achieved considerable performance in attributed network anomaly detection, they still
have some limitations. Some methods such as two-step-based
methods [18] and graph autoencoder-based methods [11], [12]
are designed to learn the graph embedding rather than detecting anomalous nodes, which is not the target of the anomaly
detection task. Some methods focus on capturing the interactions between network structures and node attributes in two
different latent spaces, rather than mining abnormal patterns in
the attributed networks [10], [13]. Moreover, some SSL-based
methods capture local and global relationships through data
augmentation, which ignores the correlations between network
structures and node attributes in the latent space [15], [17].
To overcome the abovementioned limitations, in this article, we propose a canonical correlation analysis (CCA)-based
method for attributed network anomaly detection (CaCo). The
motivation of CaCo is shown in Fig. 1. We assume that there

1551-3203 © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

462

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 1, JANUARY 2024

Fig. 1. Motivation of the proposed method. There should be a strong
correlation between the attribute and structure feature for normal nodes,
and weak correlation ones for abnormal nodes, in the attributed network.

should be a strong correlation between the attribute and structure
features of normal nodes, and a weak correlation between those
of abnormal nodes, in the attributed network. Therefore, CaCo is
designed to learn a correlation measurement function between
network structure distribution and node attribute distribution,
and the abnormal nodes are detected based on the measured
correlation scores. Specifically, in CaCo, the backbone of a
weight-sharing graph convolutional network is employed to
encode the node feature from two views of attribute and structure
in the latent space, respectively. Then, a Kullback–Leibler (KL)
divergence regularization is used to align the distributions of
the two views. Finally, the parameters of CaCo are optimized
by maximizing the correlation between attribute and structure
features of normal nodes in the training phase, and anomalies can
be detected by measuring the correlation between two views in
the testing phase. Experimental results on six real-world datasets
show that CaCo outperforms state-of-the-art techniques, which
demonstrates the effectiveness of the proposed method.
The main contributions of this article are outlined as follows.
1) We redefine anomaly detection on attributed networks as
a correlation metric problem between the attribute and
structure of nodes and propose a framework of CCAbased attributed network anomaly detection, which explicitly models the correlation between these two views
of node attribute and network structure.
2) We propose a correlation measurement method of the
attribute and structure on attributed networks for anomaly
detection, which aligns the distribution of attribute features and structure features of normal nodes in the latent
space.
3) We conduct extensive experiments on multiple real-world
datasets, and the results show that the proposed method
achieves state of the art in the anomaly detection task of
attributed networks.
II. RELATED WORKS
A. Traditional Anomaly Detection
Traditional anomaly detection is the task of detecting outliers
for Euclidean structural data, such as tabular data or images.
The existing methods can be divided into two main categories.
First, one-class-classification-based methods [5], [6] attempt to
learn a compact hyperplane or hypersphere to wrap the normal
data, and data located outside the hyperplane or the hypersphere

are defined as outliers. Typical methods such as OC-SVM and
SVDD [6] try to fit a hyperplane or hypersphere to separate the
normal and abnormal data points. Second, the reconstructionbased approach assumes that anomaly data cannot be effectively
reconstructed from a compressed low-dimensional vector space.
For example, autoencoder-based methods [4], [7], [19] utilize
the reconstruction error to detect the outliers. Although these
methods have been successfully applied in anomaly detection,
they do not generalize well to non-Euclidean graph data, which
leaves the problem of anomaly detection on attributed networks
still an open problem.
B. Attributed Network Anomaly Detection
Attributed network anomaly detection aims to find nodes
whose patterns are significantly different from others. Existing
graph anomaly detection methods can be divided into three
categories [13]: 1) only structure- or attribute-based methods,
2) residual-analysis-based methods, and 3) GNN-based methods. The only structure- or attribute-based methods [18], [20]
detect anomaly nodes by considering the structure information
or node attribute information. These methods ignore the information of graphs, which makes them unable to achieve excellent
performance. The residual-analysis-based methods [9], [10] utilize shallow mechanisms to capture the interaction between the
network structure and node attributes to the local community.
That make cannot capture the complete information of attributed
networks. The GNN-based methods [13], [21], [22], [23] construct a graph autoencoder that uses both structure information
and node attribute information by simultaneously reconstructing
the attribute and structure and detects anomalies by one-class
methods [6] or reconstruction errors. Besides, graph SSL-based
methods [15], [24] transform graph data such as randomly
masking certain information or randomly sampling subgraphs
to generate input data and utilize GNNs to learn the graph
embedding for anomaly detection. Although these methods have
achieved significant applications in attributed network anomaly
detection, they cannot achieve better performance by ignoring
the correlation between network structure and node attributes or
ignoring the effect of noise in the graph data.
C. Canonical Correlation Analysis
CCA [25], [26] is a method that aims to find the linear
transformation for measuring the relationship between two
vectors. Give two vectors X1 and X2 , the correlation ρ =
T
b
1 X2
√ T a ΣX√
is maximized by optimizing the objecT
a ΣX 1 X 1 a

b ΣX 2 X 2 b

tive
max aT ΣX1 X2 b, s.t. aT ΣX1 X1 a = bT ΣX2 X2 b = I.
a,b

(1)

The standard CCA and its variants are widely used for multiview learning [26], which uses linear projections to learn the
feature embedding and utilizes the CCA objective to learn the
correlation between different views. However, these models are
linear in the sense. For learning the nonlinear embedding, DeepCCA [25], [27] presents the use of deep neural networks to learn

WANG et al.: CACO: ATTRIBUTED NETWORK ANOMALY DETECTION VIA CANONICAL CORRELATION ANALYSIS

Fig. 2.

463

Illustration of the proposed framework CaCo.

the nonlinear projections of different views. The use of exact
decorrelation operations in those methods makes them achieve
suboptimal optimization. Unlike these methods, Soft-CCA [28]
considers the decorrelation constraint as a term of loss and
optimizes it jointly with other terms, and the objective of Soft
CCA is


max T r PθT1 (X1 ) Pθ2 (X2 )
θ1,θ2

s.t. PθT1 (X1 ) Pθ1 (X1 ) = PθT2 (X2 ) Pθ2 (X2 ) = I

(2)

where I is the identity matrix, and (2) can be rewritten as
min ||Pθ1 (X1 ) − Pθ2 (X2 ) ||2F

θ1,θ2

+ λ (LSDL (Pθ1 (X1 )) + LSDL (Pθ2 (X2 )))

(3)

where Pθ1 and Pθ2 are the neural networks used to learn the
representations of the two views. ||Pθ1 (X1 ) − Pθ2 (X2 )||2F is
used to maximize the correlation between the two views, and
LSDL is used to minimize the distance between Pθi (Xi ) and the
identity matrix.
III. METHOD
In this section, we describe the proposed CaCo method, as
shown in Fig. 2. CaCo consists of three parts: 1) a weight-sharing
GCN, 2) a distribution alignment objective, and 3) a CCA-based
objective. At first, in order to learn the distribution of the network
structure and node attributes of attributed networks, we input the
original graph G = {A, X} and the identity graph G  = {A, I}
into the weight-sharing GCN, and output the mean and variance
vectors of the network structure and node attributes. After that,
to align the distributions of the network structure and node
attributes, we use the KL divergence to pull the distributions of
the two views to the same prior distribution. Finally, we sample
the network structure embedding and node embedding from
the learned distribution and maximize the correlation of normal
nodes on the network structure distribution and node attribute
distribution by using the CCA-based objective. Specifically, the
anomaly scores of each node are defined as the correlations
between network structure and node attributes, and the node

with a strong correlation between two views will be defined as
a normal node.
A. Weight-Sharing Encoder
The weight-sharing encoder is designed to learn the correlation distribution of the network structure and node attributes.
Specifically, CaCo has two different inputs: 1) the original graph
G = {A, X} and 2) the identity graph G  = {A, I}, which are
utilized for learning the distribution of the network structure and
node attributes.
To learn the structure information, the original graph G =
{A, X} is input to the weight-sharing encoder to learn the
network structure information of the attributed network


1
1
(4)
GCN (H, A|W ) = ϕ (D)− 2 A(D)− 2 HW
where D is the diagonal degree matrix of the network G, H =
X is the node attributes, and A is the adjacency matrix of the
attributed network.
To extract node semantic information, identity aggregation
is designed to learn node attribute information. We utilize the
identity graph G  = {A, I} input to the weight-sharing encoder
GCN (X, I|W ) = ϕ (IXW )

(5)

where I is the identity graph, which makes the semantic information and network structure information of each node more
similar by transferring the learned semantic information to all
node features. W in (4) and (5) is the trainable shared weight.
ϕ is the activation function, such as RELU(•) = max(0, •).
B. Distribution Alignment
After the weight-sharing GCN, the network structure distribution q(Zh |H, A) and node attribute distribution q(Zf |X, I)
are learned by
q (Z|X, A) =

N


q (zi |X, A)

(6)

i=0


 
q (zi |X, A) = N zi |μi , diag σ 2

(7)

464

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 1, JANUARY 2024

where μ is the mean vectors and σ is the variance vectors. Z is
the embedding sampled from the distributions of the two views.
For the network structure distribution, μh and σ h are the mean
and variance vectors of the structure, respectively, and Zh is the
network embedding
μ = GCNμ (H, A|W )

(8)

σ = GCNσ (H, A|W )

(9)

μh and σ h are the mean and variance vectors of the network
structure distribution, respectively. Similarly, μf and σ f are the
mean and variance vectors of the node attributes, respectively.
Then, we align the learned distributions of the two views on
attributed networks. Since it is difficult to align the two distributions directly, in this section, we utilize the KL divergence
to pull the distribution q(Zh |X, A) and q(Zf |X, I) to the prior
distribution p
Lkl = −KL [q(Zh |X, A)||p(Zh )] − KL [q(Zf |X, I)||p(Zf )] .
(10)
In this article, we use the Gaussian distribution as the prior
distribution p [22], [23].
C. CCA-Based Objective
The CCA-based objective aims to learn the correlation between network structure distribution and node attribute distribution. First, we sample the structure embedding Zh and the
node attribute embedding Zf from the distribution of network
structure q(Zh |X, A) and the distribution of node attributes
q(Zf |X, I), and normalize the node embedding of the two views
as follows:
Zh − μ (Zh )
Zh =
1
σ (Zh ) ∗ N 2
Zf =

Zf − μ (Zf )
1

σ (Zf ) ∗ N 2

.

(11)

Then, from (3), CaCo maximizes the correlation between the two
view distributions by minimizing the invariance of the network
structure embedding Zh and the node attribute embedding Zf .
The invariance loss Linv is defined as
Linv = ||Zh − Zf ||2F .

(12)

To avoid collapsed solutions, the following decorrelation Ldco
loss is proposed to ensure that the individual dimensions of the
features are uncorrelated




Ldco = ||ZhT Zh − I||2F + ||ZfT Zf − I||2F .

(13)

The CCA-based objective is defined as follows:
LCCA = Linv + λ ∗ Ldco

(14)

where λ is the tradeoff between the two terms.

Algorithm 1: CaCo.
Require:
Attributed network G = {A, X}; Identity graph
G = {A, I}; weight-sharing encoder f ; the prior
distribution p and the hyperparameter λ of CCA-based
objective.
1: for epoch = 1 to T do
2: Generate the network structure distribution
q(Zh |H, A) via (4) and (6) and generate the node
attribute distribution q(Zf |X, I) via (5) and (6).
3: Align the distribution of network structure and node
attribute via (10).
4: Sample the network structure embedding Zh and node
embedding Zf from the distribution of network
structure q(Zh |H, A) and node attributes q(Zf |X, I).
5: Normalize the network structure embedding Zh and
node embedding Zf by (11).
6: Input the normalized network structure embedding Zh
and node attribute embedding Zf into CCA-objective,
and update the CaCo with its stochastic gradient by
(15).
7: end for
8: Compute the correlation between network structure
embedding Zh and node embedding Zf via (12) and
detect the anomaly by it.
9: return f .

and node attribute distribution
L = LCCA + LKL .

Unlike other methods, the anomaly score of CaCo is defined
as the correlation of two views. A strong correlation between
the network structure and the node attribute is determined as
normal; otherwise, it is determined as abnormal. The algorithm
of CaCo is described as follows.
IV. EXPERIMENTS
A. Datasets
To evaluate the effectiveness of CaCo, we tested the CaCo
methods on six public datasets, including four citation benchmark datasets (Cora, Citeseer, Pubmed, and ACM) and two
social benchmark datasets (Flickr, BlogCatalog). Table I shows
the statistics of these datasets. The details of these datasets are
as follows.
1) Citation Networks: Cora, Citeseer, Pubmed,1 and ACM
are four publicly used citation network benchmark
datasets with scientific publications as nodes and the citation links between these scientific publications as edges.
2) Social Networks: BlogCatalog and Flickr2 are two typical
social network benchmark datasets, where users of social

D. Loss Function and Anomaly Score
The training objective of CaCo is to optimize the CCA-based
loss and the KL divergence of the network structure distribution

(15)

1 [Online]. Available: http://linqs.cs.umd.edu/projects/projects/lbc
2 [Online]. Available: http://socialcomputing.asu.edu/pages/datasets

WANG et al.: CACO: ATTRIBUTED NETWORK ANOMALY DETECTION VIA CANONICAL CORRELATION ANALYSIS

TABLE I
STATISTICS OF SIX DATASETS

465

are evaluated under five different random seeds and the mean
performance and the mean variance were reported as the final
results. In the experiments, CaCo is implemented using Pytorch3
and Deep Graph Library.4 All experiments were conducted on an
Ubuntu 16.04 Server with 128 GB of RAM, Intel(R)-Xeon(R)Gold-5220R(2.20 GHz), and a GeForce RTX 3090 Graphics
Card with 24 GB of RAM.
C. Experimental Results

websites are represented as nodes and the following relationships between users are represented as edges.
Based on previous studies on these datasets [13], [14], we
chose one of the classes as the normal class and the remaining
classes as the anomalous class. In our experiments, we randomly
sampled only 60% of the normal nodes for training, and the
remaining 15% and 25% randomly selected the same number of
anomalous nodes for validation and testing, respectively.
B. Experimental Settings
In this section, we introduce the settings of our experiments
including baselines, experimental design, and metrics.
1) Baseline: We compared the proposed model CaCo
with four types of baselines. First, the traditional one-class
classification-based methods include OC-SVM [5] and DeepSVDD [8], which detect the anomaly by a learned hypersphere containing normal data. In this article, we learn the
hypersphere on the network structure and node attributes, respectively. Second, graph-embedding-based methods such as
DeepWalk [20], GAE [21], ARGA [22], Dominant [11], and
ComGA [29] employ graph learning methods to extract graph
information and use the reconstruction errors to detect the
anomaly. Third, one-class GNN-based methods include OCGNN [13] (OC-GCN, OC-SAGE) and Dual-SVDAE [14],
which combine the powerful representation capabilities of
GNNs along with the classical one-class objective to conduct anomaly detection on graph structure data. Fourth, graph
SSL-based methods include CCA-SSG [15], which utilizes
CCA to optimize the feature-level objective and Conad [30],
which integrates the anomaly knowledge into the Siamese GNN
encoder by contrastive loss and detects anomaly nodes via
reconstruction errors.
2) Experimental Design and Metric: In the experiments,
CaCo is trained with 500 iterations on all datasets and optimized by Adam with a learning rate of 0.001. The embedding
dimension is set to 64 and the layers of GNN are set to 2 for all
datasets. The hyperparameter λ is set to 1 for all datasets. For the
baseline methods, we use the publicly available implementations
from the original papers and set the parameters by grid search.
To measure the performance of CaCo with baselines, similar to
the previous studies [13], [14], in this article, we employ the
widely used AUC score and AP score as metrics. All methods

The performance of the proposed model was evaluated quantitatively by comparing it with the state-of-the-art methods. The
results of all methods on six datasets are shown in Table II, and
the results of each method on six datasets by treating each class
as a normal class are shown in Fig. 3.
In the experimental results, our proposed framework CaCo
achieves the best performance on six datasets. CaCo obtains a
significant improvement of 5.90% on AUC and 6.43% on AP
compared to the best results in the baseline. The main reason
is that CaCo captures the distributional relationships on node
attribute and network structure. In comparison with the traditional anomaly detection methods, OCSVM and Deep-SVDD
perform worse than the other methods. The reason is that they
cannot simultaneously capture the information of node attributes
and complex network structures. The performance of graphembedding-based methods is not satisfactory, because they effectively measure the anomaly via a single aspect (reconstruction
error). For the method ComGA, it uses the community-aware
method to learn the node embedding, which can be more easily
separated in the latent space. However, it uses reconstruction
error as anomaly score, which makes it impossible to detect
abnormal nodes similar to normal nodes. The one-class GNNbased methods, such as OC-GCN and Dual-SVDAE, do not
show competitive performance, even though they are designed
for graph structure feature extraction and hypersphere learning
for anomaly detection. This lies in the inability of the one-class
method to measure abnormal nodes whose latent space is similar
to the normal nodes. Graph self-supervised methods, such as
Conad, perform worse than CaCo, due to the fact that it learns
the graph embedding using prior human knowledge for data
augmentation and cannot include all exception patterns. This
makes it unable to detect anomaly nodes that have similar
patterns to normal nodes. Unlike other baselines, CaCo aims
to capture the correlations between network structure and node
attributes, and when a node is abnormal, the network embedding
will be different from the node attribute embedding while other
baselines aim to learn the representation of nodes in the latent
space, ignoring the relationship between network structure and
node attributes. This is the core idea of CaCo, and the results
proved it. Besides, the distribution alignment makes CaCo capture the different information between network structure and
node attributes, and we can obtain the same conclusion in the
ablation study.
3 [Online]. Available: https://pytorch.org/
4 [Online]. Available: https://www.dgl.ai/

466

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 1, JANUARY 2024

TABLE II
ANOMALY DETECTION PERFORMANCE

Fig. 3 shows the AUC scores of all methods by considering
each node class as a normal class on the six datasets. From the
results, we find that CaCo performs more effectively and robustly
than the other baselines. This is due to the CaCo capturing
network structure and node attribute information jointly by
aggregating node identities using identity graphs, weight sharing
GCN to map network structure and node attribute information
to the same distribution. In particular, the performance of the
baseline methods is worse than that of the other classes in
the “7” class of Cora, the “1” class of Citeseer, and the “5”
class of BlogCatalog datasets. The main reason behind this may
be the relatively small size of these classes in these datasets,
respectively. The “7” class of Cora is only 12.96%, the “1” class
of Citeseer is only 7.35%, and the “2” class of BlogCatalog
is only 14.95%, which makes these methods unable to have
enough training for those classes to distinguish them from others.
Unlike the baseline methods, CaCo has the weight-sharing GCN
encoder and identity graph for learning the information about
the network structure and node attribute of normal nodes, which

helps CaCo to capture the complete semantic information of
normal data. Besides, the correlation of two views as anomaly
scores helps CaCo to effectively distinguish normal classes from
other classes.
D. Parameter Study
In this section, we study the impact of different dimensions of node embedding, and the number of layers of the
weight-sharing encoder, with the results being run on the Cora
dataset, as shown in Fig. 4. We can notice that CaCo performs
stably at the different dimensions of node embedding. This
is due to the fact that CaCo captures key information about
the network structure and node attributes used for anomaly
detection. We also see that the performance of CaCo is stable
as the number of layers increases due to the weight-sharing
encoder using the identity graph as inputs, which enables
CaCo to retain more node information in the feature learning
process.

WANG et al.: CACO: ATTRIBUTED NETWORK ANOMALY DETECTION VIA CANONICAL CORRELATION ANALYSIS

467

Fig. 3. Evaluation performance of CaCo and baselines by taking each class of nodes as a normal class on six datasets. The abscissa represents
the classes and the ordinate represents the AUC score.

TABLE III
ABLATION STUDY OF CACO

Fig. 4. Impact of different dimensions of embedding and the number
of layers for weight sharing encoder on the Cora dataset.

E. Ablation Study
In this section, we compare CaCo with three variants on six
datasets to study the different modules of CaCo used for anomaly
detection. The variants are defined as follows.
1) wo-dis: This variant replaces distribution learning with
feature learning to learn the correlation between network
structure and node attributes.
2) wo-Linv : This variant studies the effectiveness of the
invariant term by removing it from the loss function.
3) wo-Ldco : Similar to wo-Linv , this variant studies the effectiveness of the decorrelation term by removing it from
the loss function.
The results of the ablation study are shown in Table III. We can
see that wo-dis performs worse than the others because learning
the correlation between attribute distribution and structure distribution captures information about nodes that are not present in
the training set while the distribution learning module captures
key information for anomaly detection.

For wo-Linv , we found that using only the decorrelation term
does not yield good results on Flickr and BlogCatalog, but
has good performance on the first four datasets, as shown in
Fig. 5. Specifically, for the first four datasets, the distribution
of anomaly scores have a clear dividing line, which means that
those datasets are themselves strongly correlated with normal

468

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 1, JANUARY 2024

TABLE IV
COMPUTATION ANALYSIS FOR CACO WITH OTHER METHODS

Fig. 5.

Fig. 6.

Correlation score of wo-Linv on six datasets.

Result of different values of tradeoff hyperparameter λ.

points and weakly correlated with abnormal points after optimization with the decorrelation term, but this is not the case
for the Flickr and BlogCatalog datasets. Thus, for the first four
datasets, CaCo can also perform well without the invariant term.
For the Flickr and BlogCatalog datasets, CaCo needs to further
optimize the invariant term.
For wo-Ldco , it performs worse than the other algorithms, because, without decorrelation terms, CaCo will achieve collapsed
solutions [15]. As shown in Fig. 6, we also study the impact of the
decorrelation term on anomaly detection by setting the tradeoff
hyperparameter λ from 10−5 to 100. We discovered that when
λ is too small, the decorrelation term does not work, allowing
CaCo to get collapsed solutions. When the value of λ is too large,
we notice that the performance of CaCo is degraded, especially
on Flickr and BlogCatalog. This is because the invariant term
will be neglected. Therefore, the value of the hyperparameter λ
is associated with the correlation between network embedding
and node embedding. From Fig. 6, a value of the hyperparameter
λ in [0.1,1] can achieve the optimal performance. This means
that the performance of CaCo benefits from the invariance term.
In contrast to wo-Ldco , CaCo utilizes the decorrelation term to
prevent solution collapse. Above all, the results demonstrate that
the modules of CaCo can be used for attributed network anomaly
detection.
F. Computational Analysis
In this section, we compare the complexity of CaCo with
other baselines, as shown in Table IV. We have compared the

number of parameters and FLOPs of CaCo with other baselines.
We can find that the number of parameters and FLOPs is smaller
than most baselines. The reason is that CaCo uses only l-layers
GCN as an encoder, a light-weighted network for graph data,
which is simpler and more effective to operate compared to other
networks such as GraphSAGE. For ComGA, it first learns the
node embedding of the community, which makes it necessary
to design more modules and greatly increases the number of
parameters. In addition, for GAE, dominant, and dual-SVDAE,
the dual-encoder or decoder also requires a new network module,
which makes them require more parameters and computations.
CCA-SSG and Conad are similar to CaCo, except that they use
l-layers GCN to capture the information of attributed networks,
which makes them reduce the number of parameters and computations.
G. Visualization
In this section, we visualize the embedding and correlation
scores class “1” of six datasets. Fig. 7 visualizes the node
embedding of the test nodes learned by ARGA, Dual-SVDAE,
and CaCo, respectively, with blue points representing normal
nodes and orange points representing the abnormal nodes. We
can see that CaCo, which separates normal nodes from abnormal nodes, is better than the above methods. The reason
is that CaCo aligns the distribution of network structures and
node attributes in the latent space and utilizes the correlation
between the distributions of two views as an objective to detect
the anomaly. Furthermore, we notice that the distribution of
nodes in the latent space is not as tight as other methods,
which is due to the fact that CaCo focuses on the separation
of normal and abnormal nodes, rather than methods such as
OC-GNN and Dual-SVDAE that focus on learning a compact
hypersphere of normal nodes to separate normal nodes from
abnormal nodes. Fig. 8 shows the correlation scores of the
six datasets, we can find that the anomaly nodes have smaller
correlation values while the normal nodes have larger correlation
values. The results indicate the effectiveness of the proposed
CaCo.

WANG et al.: CACO: ATTRIBUTED NETWORK ANOMALY DETECTION VIA CANONICAL CORRELATION ANALYSIS

469

Fig. 7. T-SNE visualization of node embedding derived by different models on six datasets. Blue points represent the normal nodes and orange
points represent the abnormal nodes respectively. (a) ARGA. (b) Dual-SVDAE. (c) CaCo.

datasets demonstrate the effectiveness of the proposed method
compared to the state-of-the-art techniques. In the future, we
will focus on the correlation between the global and the local
nodes to detect the anomaly points.
REFERENCES

Fig. 8.

Correlation score of CaCo on six datasets.

V. CONCLUSION
In this article, we propose a CCA-based method for attributed
network anomaly detection (CaCo), which captures the correlation between node attributes and the network structure of
attributed networks for anomaly detection. Specifically, CaCo
designs weight-sharing GCN as an encoder to learn the distribution network structure and node attributes, and we align them
to a sharing latent space via KL divergence. Then, the CCA
objective is designed to maximize the correlation of normal
nodes in terms of network structure and node attributes, and the
anomaly score is defined as the correlation of two views to detect
the anomaly points. Extensive experiments on six real-world

[1] C. Zhang, X. Wu, W. Yan, L. Wang, and L. Zhang, “Attribute-aware graph
recurrent networks for scholarly friend recommendation based on internet
of scholars in scholarly Big Data,” IEEE Trans. Ind. Informat., vol. 16,
no. 4, pp. 2707–2715, Apr. 2020.
[2] Y. Wang, H. Sun, Y. Zhao, W. Zhou, and S. Zhu, “A heterogeneous
graph embedding framework for location-based social network analysis
in smart cities,” IEEE Trans. Ind. Informat., vol. 16, no. 4, pp. 2747–2755,
Apr. 2020.
[3] L. Rui, Y. Zhu, Z. Gao, and X. Qiu, “CLPM: A cooperative link prediction
model for industrial Internet of Things using partitioned stacked denoising
autoencoder,” IEEE Trans. Ind. Informat., vol. 17, no. 5, pp. 3620–3629,
May 2021.
[4] H. Fan, F. Zhang, R. Wang, L. Xi, and Z. Li, “Correlation-aware deep
generative model for unsupervised anomaly detection,” in Proc. PacificAsia Conf. Knowl. Discov. Data Mining, 2020, pp. 688–700.
[5] P. Nader, P. Honeine, and P. Beauseroy, “lp -norms in one-class classification for intrusion detection in SCADA systems,” IEEE Trans. Ind.
Informat., vol. 10, no. 4, pp. 2308–2317, Nov. 2014.
[6] L. Ruff et al., “Deep one-class classification,” in Proc. Int. Conf. Mach.
Learn., 2018, pp. 4393–4402.
[7] C. Zhou and R. C. Paffenroth, “Anomaly detection with robust deep
autoencoders,” in Proc. 23rd ACM SIGKDD Int. Conf. Knowl. Discov.
Data Mining, 2017, pp. 665–674.
[8] B. Perozzi, R. Al-Rfou, and S. Skiena, “Deepwalk: Online learning of
social representations,” in Proc. 20th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, 2014, pp. 701–710.
[9] J. Li, H. Dani, X. Hu, and H. Liu, “Radar: Residual analysis for anomaly
detection in attributed networks,” in Proc. Int. Joint Conf. Artif. Intell.,
2017, pp. 2152–2158.

470

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 1, JANUARY 2024

[10] Z. Peng, M. Luo, J. Li, H. Liu, and Q. Zheng, “Anomalous: A joint
modeling approach for anomaly detection on attributed networks,” in Proc.
27th Int. Joint Conf. Artif. Intell., 2018, pp. 3513–3519.
[11] K. Ding, J. Li, R. Bhanushali, and H. Liu, “Deep anomaly detection on
attributed networks,” in Proc. SIAM Int. Conf. Data Mining, 2019, pp. 594–
602.
[12] H. Fan, F. Zhang, and Z. Li, “Anomalydae: Dual autoencoder for anomaly
detection on attributed networks,” in Proc. IEEE Int. Conf. Acoust., Speech,
Signal Process., 2020, pp. 5685–5689.
[13] X. Wang, B. Jin, Y. Du, P. Cui, Y. Tan, and Y. Yang, “One-class graph neural
networks for anomaly detection in attributed networks,” Neural Comput.
Appl., vol. 33, pp. 12073–12085, 2021.
[14] F. Zhang, H. Fan, R. Wang, Z. Li, and T. Liang, “Deep dual support vector
data description for anomaly detection on attributed networks,” Int. J.
Intell. Syst., vol. 37, no. 2, pp. 1509–1528, 2022.
[15] H. Zhang, Q. Wu, J. Yan, D. Wipf, and P. S. Yu, “From canonical
correlation analysis to self-supervised graph neural networks,” Adv. Neural
Inf. Process. Syst., vol. 34, pp. 76–89, 2021.
[16] X. Liu, F. Zhang, H. Liu, and H. Fan, “iTimes: Investigating semisupervised time series classification via irregular time sampling,” IEEE
Trans. Ind. Informat., vol. 19, no. 5, pp. 6930–6938, May 2023.
[17] W. Lu, H. Fan, K. Zeng, Z. Li, and J. Chen, “Self-supervised domain
adaptation for cross-domain fault diagnosis,” Int. J. Intell. Syst., vol. 37,
no. 12, pp. 10903–10923, 2022.
[18] D. Lai, S. Wang, Z. Chong, W. Wu, and C. Nardini, “Task-oriented attributed network embedding by multi-view features,” Knowl.-Based Syst.,
vol. 232, 2021, Art. no. 107448.
[19] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” in Proc. Int. Conf. Learn. Representation, 2017.
[20] B. Perozzi, L. Akoglu, P. I. Sánchez, and E. Müller, “Focused clustering
and outlier detection in large attributed graphs,” in Proc. 20th ACM
SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2014, pp. 1346–1355.
[21] D. Zhu, Y. Ma, and Y. Liu, “Anomaly detection with deep graph autoencoders on attributed networks,” in Proc. IEEE Symp. Comput. Commun.,
2020, pp. 1–6.
[22] S. Pan, R. Hu, G. Long, J. Jiang, L. Yao, and C. Zhang, “Adversarially
regularized graph autoencoder for graph embedding,” in Proc. Int. Joint
Conf. Artif. Intell., 2018, pp. 2609–2615.
[23] H. Fan et al., “Heterogeneous hypergraph variational autoencoder for
link prediction,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 44, no. 8,
pp. 4125–4138, Aug. 2022, doi: 10.1109/TPAMI.2021.3059313.
[24] Y. Liu, Z. Li, S. Pan, C. Gong, C. Zhou, and G. Karypis, “Anomaly
detection on attributed networks via contrastive self-supervised learning,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2378–2392,
Jun. 2022.
[25] G. Andrew, R. Arora, J. Bilmes, and K. Livescu, “Deep canonical correlation analysis,” in Proc. Int. Conf. Mach. Learn., 2013, pp. 1247–1255.
[26] Z. Chen et al., “A just-in-time-learning-aided canonical correlation analysis method for multimode process monitoring and fault detection,” IEEE
Trans. Ind. Electron., vol. 68, no. 6, pp. 5259–5270, Jun. 2021.
[27] X. Xiu, Z. Miao, Y. Yang, and W. Liu, “Deep canonical correlation analysis
using sparsity constrained optimization for nonlinear process monitoring,”
IEEE Trans. Ind. Informat., vol. 18, no. 10, pp. 6690–6699, Oct. 2022.
[28] X. Chang, T. Xiang, and T. M. Hospedales, “Scalable and effective deep
CCA via soft decorrelation,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., 2018, pp. 1488–1497.
[29] X. Luo et al., “ComGA: Community-aware attributed graph anomaly
detection,” in Proc. 15th ACM Int. Conf. Web Search Data Mining, 2022,
pp. 657–665.
[30] Z. Xu, X. Huang, Y. Zhao, Y. Dong, and J. Li, “Contrastive attributed network anomaly detection with data augmentation,” in Proc. Pacific-Asian
Conf. Knowl. Discov. Data Mining, 2022, pp. 444–457.

Fengbin Zhang received the Ph.D. degree in
computer application from Harbin Engineering
University, Harbin, China, in 2005.
He is currently a Supervisor and a Professor
with the Harbin University of Science and Technology, Harbin. His current research interests include network and information security, firewall
technology, and intrusion detection technology.

Ruidong Wang is currently working toward
the Ph.D. degree with the School of Computer
Science and Technology, Harbin University of
Science and Technology, Harbin, China.
During the doctoral study, his research subject is graph anomaly detection. His current research interests include graph data mining, time
series analysis, and anomaly detection.

Haoyi Fan (Member, IEEE) received the Ph.D.
degree in computer application technology from
the Harbin University of Science and Technology, Harbin, China, in 2021.
He is currently an Associate Research Fellow with the School of Computer and Artificial
Intelligence, Zhengzhou University, Zhengzhou.
His current research interests include pattern
recognition, data mining, and deep learning.

Xunhua Huang is currently working toward the
Ph.D. degree with the School of Computer Science and Technology, Harbin University of Science and Technology, Harbin, China.
During the doctoral study, his research subject area is time series analysis. His current research interests include graph data mining, time
series analysis, and anomaly detection.

Chongrui Tian is currently working toward the
Ph.D. degree with the School of Computer
Science and Technology, Harbin University of
Science and Technology, Harbin, China.
He is currently an Associate Professor with
the East University of Heilongjiang, Harbin. During the doctoral study, his research subject area
is intrusion detection technology. His current research interests include network and information security, and intrusion detection technology.

Liang Xi received the Ph.D. degree in computer
applied technology from the Harbin University
of Science and Technology, Harbin, China, in
2012.
He is currently a Professor with the Harbin
University of Science and Technology, Harbin.
His current research interests include artificial
intelligence, network security, machine learning,
etc.
PAPER_TEXT
