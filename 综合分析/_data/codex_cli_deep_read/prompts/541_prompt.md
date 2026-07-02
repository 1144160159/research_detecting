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
# [541] Self-Supervised Masked Graph Autoencoder for Hyperspectral Anomaly Detection
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
编号：541
题名：Self-Supervised Masked Graph Autoencoder for Hyperspectral Anomaly Detection
年份：2025
DOI：10.1109/tip.2025.3620091
来源：IEEE Transactions on Image Processing
PDF：paper/10.1109_TIP.2025.3620091.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\541.txt
- 原始字符数：74160
- 本次发送字符数：74160
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
6714

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Self-Supervised Masked Graph Autoencoder for
Hyperspectral Anomaly Detection
Bing Tu , Senior Member, IEEE, Baoliang He, Student Member, IEEE, Yan He, Member, IEEE,
Tao Zhou , Student Member, IEEE, Bo Liu , Member, IEEE, Jun Li , Fellow, IEEE,
and Antonio Plaza , Fellow, IEEE

Abstract—Hyperspectral image anomaly detection faces the
challenge of difficulty in annotating anomalous targets.
Autoencoder(AE)-based methods are widely used due to their
excellent image reconstruction capability. However, traditional
grid-based image representation methods struggle to capture
long-range dependencies and model non-Euclidean structures.
To address these issues, this paper proposes a self-supervised
Masked Graph AutoEncoder (MGAE) for hyperspectral anomaly
detection. MGAE utilizes a Graph Attention Network (GAT)
autoencoder to reconstruct the background of hyperspectral
images and identifies anomalies by comparing the reconstructed
features with the original features. Specifically, we constructs a
topological graph structure of the hyperspectral image, which
is then input into the GAT autoencoder for reconstruction,
leveraging the multi-head attention mechanism to learn spatial
and spectral features. To prevent the decoder from learning
trivial solutions, we introduce a re-masking strategy that randomly masks both the input features and hidden representations
during training, forcing the model to learn and reconstruct
features under limited information, thereby improving detection
performance. Additionally, the proposed loss function with graph
Laplacian regularization (Twice Loss) minimizes variations in
feature representations, leading to more consistent background
reconstruction. Experimental results on several real-world hyperspectral datasets demonstrate that MGAE outperforms existing
methods.

I. I NTRODUCTION

H

YPERSPECTRAL imaging differs from traditional
remote sensing technologies by providing simultaneous
information on the radiance, geometry, and spectrum of ground
objects [1], [2]. The nearly continuous spectral information
provided by Hyperspectral Images (HSI) conveys a powerful
ability to distinguish the subtle spectral differences between
ground objects, leading to the widespread application of hyperspectral technology in various fields [3], [4]. Target detection,
a key research area in HSI, can be categorized into spectral
matching detection and anomaly detection based on the need
for prior information. The former employs prior information
of the target spectral signal for spectral matching, while the
latter does not require any prior information about the targets
and identifies anomalous targets based on spectral differences.
In practical applications, acquiring prior spectral information
of targets is often challenging [5], [6], [7]. Consequently,
anomaly detection is highly practical and fundamental in HSI
processing.
In recent years, numerous algorithms for hyperspectral
anomaly detection (HAD) have been developed and can be
typically divided into two categories:

Index Terms—Anomaly detection, autoencoder, graph attention network, re-masking strategy, twice loss.

1) Statistics-Based:
Received 24 January 2025; revised 5 August 2025 and 14 September 2025;
accepted 30 September 2025. Date of publication 16 October 2025; date of
current version 24 October 2025. This work was supported in part by the
National Natural Science Foundation of China under Grant 62535010, Grant
62271200, and Grant 62375083; and in part by the Start-Up Foundation
for Introducing Talent of Nanjing University of Information Science and
Technology (NUIST) under Grant 2023r091. The associate editor coordinating
the review of this article and approving it for publication was Prof. Zhiyuan
Zha. (Corresponding author: Bing Tu.)
Bing Tu, Baoliang He, Yan He, and Bo Liu are with the Institute of Optics
and Electronics, the State Key Laboratory Cultivation Base of Atmospheric
Optoelectronic Detection and Information Fusion, Jiangsu International
Joint Laboratory on Meteorological Photonics and Optoelectronic Detection, and Jiangsu Engineering Research Center for Intelligent Optoelectronic
Sensing Technology of Atmosphere, Nanjing University of Information Science and Technology, Nanjing 210044, China (e-mail: tubing@nuist.edu.cn;
baoliang he@163.com; 975861884@qq.com; bo@nuist.edu.cn).
Tao Zhou is with the School of Electronic Information and Electrical Engineering, Anhui Jianzhu University, Hefei 230601, China (e-mail:
zhoutao@stu.ahjzu.edu.cn).
Jun Li is with the Faculty of Computer Science, China University of
Geosciences, Wuhan 430074, China (e-mail: lijuncug@cug.edu.cn).
Antonio Plaza is with the Hyperspectral Computing Laboratory, Department
of Technology of Computers and Communications, Escuela Politécnica,
University of Extremadura, 10003 Cáceres, Spain (e-mail: aplaza@unex.es).
Digital Object Identifier 10.1109/TIP.2025.3620091

Such methods operate under the core premise that the
background adheres to a specific statistical distribution, while
anomalous targets deviate significantly from these statistical
characteristics. The Reed-Xiaoli (RX) [8] detector is a representative statistically-based method. It quantifies the anomaly
degree of a test pixel by computing the Mahalanobis distance
using the global mean and covariance matrix, under the
assumption that the background follows a multivariate Gaussian distribution. However, backgrounds are often complex and
heterogeneous in real-world scenarios, rendering the Gaussian distribution assumption unreliable and constraining its
background suppression capability. To address this limitation,
the Local RX (LRX) [9] estimates local statistics within a
sliding window; the Segmented RX (SRX) [10] partitions the
background into homogeneous categories via clustering; and
the Kernel RX (K-RX) [11] enhances separability between
background and anomalies by mapping the original data into a
high-dimensional feature space via kernel functions. Additionally, other statistically-based methods have been developed.
For instance, Lin et al. [12] proposed a dual-dictionary

1941-0042 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

TU et al.: SELF-SUPERVISED MASKED GRAPH AUTOENCODER FOR HYPERSPECTRAL ANOMALY DETECTION

construction method via two-stage complementary decisions
(DDC-TSCD). Schweizer and Moura [13] introduced an
anomaly detector based on Gaussian-Markov random fields
(MRF). Diverging from these approaches, recent research
addressing background suppression has primarily focused on
low-rank and sparse matrix decomposition frameworks [14],
[15]. Ren et al. [16] proposed a non-local and deep priorbased anomaly detection method (NLDPAD). Wang et al. [17]
proposed an anomaly detection framework based on Tensor
Low-Rank and Sparse Representation (TLRSP).
2) Non-Statistics-Based:
Unlike statistically-based approaches, non-statistical methods abandon assumptions about background distributions
and instead develop alternative frameworks encompassing
machine learning-based, representation learning-based, and
deep learning-based techniques. Within machine learningbased approaches, these can be categorized into distance-based
methods, isolation-based models and clustering-based detectors. A representative distance-based approach is the Support
Vector Data Description (SVDD) anomaly detection method
[18], which defines a novel detection statistic using a decision
rule derived from the computation of a minimal enclosing hypersphere to discriminate anomalies. Graph-theoretic
methods also fall within the distance-based category, leveraging topological relationships between pixels for anomaly
identification. The Topological Anomaly Detection (TAD)
algorithm stands as the first graph-based method for HAD,
notably pioneering the application of graph structures in
this field [19]. In TAD, the topological connection density between a test pixel and background components on
the graph determines its anomaly status. Xu et al. [20]
presented a systematic review of machine learning-driven
HAD methods, and underscored the insight that while graphstructured models are capable of capturing spatial-spectral
correlations within hyperspectral data, traditional graph-based
approaches face challenges in dynamically differentiating the
relative importance of neighboring nodes. Li et al. [21]
developed a kernelized Isolation Forest (iForest) detector that
projects the original data into a kernel space, where anomalies
exhibit higher separability from the background. Recently,
representation learning-based approaches have gained significant traction in HAD. Jiao et al. [22] presented a method
integrating intrinsic image decomposition with background
subtraction. This technique fuses a reflectance-weighted map
derived from intrinsic decomposition with an anomaly probability map generated through background subtraction to
produce the final detection result. Deep learning techniques
have demonstrated significant impact across diverse domains,
with their rapid advancement offering novel paradigms for
HAD. Wang et al. [23] proposed a sliding dual-windowheuristic reconstruction network (DirectNet) for HAD, which
suppresses anomalous interference during the reconstruction
process through a sliding dual-window mechanism, thereby
amplifying the reconstruction errors of anomalous targets. In
subsequent work, Wang et al. [24] developed a pixel-shuffled
undersampling blind-spot reconstruction network (PDBSNet),

6715

which imposes elevated reconstruction errors on anomalous
pixels to enable detection.
In this article, we implement HAD through a self-supervised
masked graph autoencoder. Our approach falls within the
non-statistical methodology category. Although grounded in
graph theory, it should not be characterized solely as distancebased since its core mechanism relies on autoencoder (AE)
architecture. Initially proposed by Baldi in 2006 [25], AE
constitutes a powerful unsupervised learning model capable
of autonomously learning intrinsic data structures and patterns
without manual feature engineering. Subsequent variants –
including deep autoencoders and convolutional autoencoders –
have significantly enhanced representation capacity through
multi-layered neural frameworks. These advancements have
established AE’s efficacy in image processing, data compression, and feature learning tasks, demonstrating unique
advantages for HAD applications in complex scenarios. Emoto
and Matsuoka [26] integrated tensor robust principal component analysis (TRPCA) with autoencoder adversarial networks
to learn nonlinear low-dimensional representations of spectral
features in background regions. Wang et al. [27]proposed a
frequency-to-spectral mapping generative adversarial network
(GAN) for HAD. This network maps raw spectra to the
fractional Fourier domain, transforms the anomaly identification task into a mapping task, and leverages reconstruction
errors to distinguish between backgrounds and anomalies.
Wu et al. [28] proposed a lightweight unsupervised crossimage HAD method (VJDNet), which utilizes variational
autoencoders (VAE) to learn global and local discriminative features of anomalies. Zhao et al. [29] proposed two
cascaded autoencoders with adaptive pixel-level attention
modules (CAPNet) for HAD. Through cascaded autoencoders,
discriminative high-level semantic features can be effectively
extracted, enhancing the difference between anomalies and the
background. The core advantage of AE lies in its precise
reconstruction capability for normal data. For data points
deviating from a normal distribution, AE often fails to achieve
effective reconstruction, thereby producing significant reconstruction errors.
In this article, we employ a re-masking strategy to prevent the decoder from learning trivial mapping relationships.
As a fundamental technique in computer science, masking selectively processes data through binary patterns –
enabling suppression of irrelevant information and enhancement of salient features. Background suppression was primarily achieved indirectly through statistical methods prior to
2010. For instance, the Reed-Xiaoli (RX) algorithm implicitly
masks distribution-conforming pixels by assuming Gaussian
background distributions and leveraging covariance matrices, yet remains constrained by rigid statistical assumptions
and linear modeling capabilities. With the rise of deep
learning, masking strategies have gained increased attention. Sun et al. [30] proposed Contrastive Self-Supervised
Background Reconstruction (CSSBR) for HAD, which constructs a self-supervised pretraining model through pixel and
patch-level masking combined with dual-attention networks.
This framework learns generalized background representations without requiring annotated samples. Wang et al. [31]

6716

introduced a fourier conditional masking with Mixed Attention (FCMMA) method, where conditional masks (CMASK)
suppress high-frequency anomaly components while preserving low-frequency background information in the frequency
domain, thereby optimizing detection performance. In their
subsequent research, Wang et al. [32]further proposed a
non-local and local feature-coupled self-supervised network
(NL2Net) for HAD. This network incorporates masked convolution to strengthen the focus on background features, thereby
effectively addressing the non-local self-similarity issue in
HSI. Su et al. [33] utilized latent binary masks to separate anomalies from backgrounds, reconstructing backgrounds
while suppressing anomalies via separation loss functions.
The recently proposed hyperspectral foundation model HyperSIGMA [34] pinpoints the core bottleneck of traditional
models to be their inadequate general feature representation
capability, most methods are limited to specific scenarios
(e.g., single homogeneous backgrounds) and exhibit significant
performance degradation in complex heterogeneous scenes,
primarily due to insufficient modeling of feature correlations.
While HyperSIGMA enables robust feature extraction in complex scenes via multimodal fusion and self-supervised masked
learning, its design as a general foundation model means
it lacks optimization for the balance between background
reconstruction and anomaly discrimination. Notably, this latter
shortcoming is critical to background consistency modeling in
HAD. Therefore, within an unsupervised framework, developing an approach to integrate graph structures with masked
learning for accurate background reconstruction and efficient
anomaly discrimination in complex scenes remains a pressing
open challenge in the field.
To address these issues, this study proposes a selfsupervised masked graph autoencoder (MGAE) for HAD. This
method utilizes a graph attention network (GAT) to construct
an autoencoder. By reconstructing the hyperspectral image
background and comparing the reconstructed features with the
original features to identify anomalies, it effectively captures
the spatial-spectral dependencies and non-Euclidean structure
of the hyperspectral data. Specifically, the MGAE first constructs the topological graph structure of the hyperspectral
image and feeds it into the GAT autoencoder for reconstruction. Leveraging a multi-head attention mechanism [35], [36],
[37], the MGAE learns both spatial and spectral features,
overcoming the limitations of traditional grid representations,
which struggle to model long-range dependencies. Secondly, a
re-masking strategy is introduced, as shown in Fig. 1. During
training, the input features and hidden representations are
randomly masked, forcing the model to learn and reconstruct
features with limited information [38], [39], avoiding the issue
noted in [20] that the decoder of self-supervised autoencoders
is prone to trivial solutions and suffers from reconstruction
error averaging. Furthermore, a loss function (Twice Loss)
with graph Laplacian regularization is designed to achieve
more consistent background reconstruction by minimizing
changes in feature representations. At the same time, it
imposes minimal constraints on anomalous regions to prevent
them from being reconstructed, achieving a balance between

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 1. Comparison between original input and masked input. The original
input may lead to simple identity mapping, causing the model to ignore
anomalies due to uniformly low reconstruction error. Masking forces the
model to reconstruct the masked areas based on unmasked nodes, focusing
more on learning background features.

local consistency and global information preservation. The
main contributions of our work can be summarized as follows:
• By integrating GAT into the anomaly detection task, its
multi-head attention mechanism can dynamically assign
weights to neighborhood nodes, flexibly modeling complex relationships between pixels, enhancing sensitivity
to key areas and suppressing noise interference. This
effectively captures the spatial-spectral dependency of
hyperspectral data, and improves the detection capability
of anomalies of different scales and shapes.
• By performing double random masking on the input
features and hidden representations, the model is forced to
learn and reconstruct features under limited information,
avoiding the problem of reconstruction error averaging caused by the decoder learning a simple mapping
relationship. This significantly improves the model’s generalization ability and adaptability to data incompleteness,
and demonstrates more stable detection performance on
real datasets.
• A Twice Loss is proposed that combines reconstruction
loss and graph Laplacian smoothing loss. It achieves
local consistency of background reconstruction and global
information preservation by minimizing feature representation changes, while imposing minimum constraints on
abnormal areas to prevent them from being reconstructed,
thus balancing background modeling accuracy and abnormality recognition sensitivity.
The paper is organized as follows: Section II introduces
the KNN algorithm for graph construction, the GAT model
and masking strategy. Section III details the proposed method,
including the GAT-based autoencoder, the re-masking strategy, and the Twice Loss function. Section IV demonstrates
the method’s effectiveness through experiments on real HSI.
Finally, Section V summarizes the work and discusses future
research directions.
II. R ELATED W ORK
Graph structures are a powerful form of data representation
capable of flexibly depicting irregular and non-Euclidean spatial relationships. However, due to the variable node degrees

TU et al.: SELF-SUPERVISED MASKED GRAPH AUTOENCODER FOR HYPERSPECTRAL ANOMALY DETECTION

Fig. 2. Graph construction from image, with different node and edge types
and related information.

6717

into a graph structure, the edge set E is constructed via
the K-nearest neighbor algorithm. The K-Nearest Neighbors
(KNN) algorithm is a method used to construct edges based on
spectral characteristic similarity, it utilizes a defined distance
metric (typically Euclidean distance) to find the k-nearest
neighbors for each data point, i.e., each pixel in the image. In
hyperspectral images, each pixel contains spectral data from
multiple bands, forming a high-dimensional feature space.
KNN evaluates and identifies the most similar neighbors in this
feature space. By using each pixel’s spectral data as a feature
vector and calculating the Euclidean distances between every
pair of pixels, the k closest neighbors are identified. Edges
are then constructed in the graph based on the connections
between each pixel and its k-nearest neighbors, thus indicating
spectral similarity. The formula can be expressed as:
r
Xb=1
(xib − x jb )2
(1)
dspec (pi , p j ) =
b

B. Graph Attention Networks

Fig. 3. Graph constructed with various K values for the central pixel in
Airport-I image.

and the unordered nature of neighboring nodes in graphs,
traditional deep learning techniques are not directly applicable
to graph data. Before the advent of GCN, feature extraction
in graphs primarily relied on manually designed features
or rule-based methods. The emergence of GCN ingeniously
combined graph theory with Convolutional Neural Network
(CNN), utilizing spectral and spatial convolution techniques
to efficiently model graph data. The spectral convolution
approach is based on the graph Fourier transform, which
processes graph signals by converting them to the frequency
domain. In contrast, spatial convolution updates node information through the aggregation of neighborhood information and
feature transformation. In this paper, we construct the graph
structure using the K-Nearest Neighbors (KNN) algorithm
[40], [41], [42] and employ the GAT for learning node features.
In this section, we will introduce the foundational knowledge
used in this paper.
A. Preliminaries
The graph structure is composed of a finite and non-empty
set of vertices and a set of edges between vertices, typically
represented as G = (V, E). Here, G denotes a graph, V is
the set of vertices of graph G, and E is the set of edges of
graph G. Unlike image data that relies on a fixed grid structure,
graph data can more flexibly represent the complex spatial and
spectral relationships in hyperspectral data. By establishing
adjacency relationships, the graph structure effectively captures both local and global similarities between pixels, making
it particularly suitable for dealing with sparse features and nonuniform distributions in hyperspectral data. Therefore, in this
paper, we choose to construct graph data to perform anomaly
detection tasks for HSI.To convert hyperspectral image data

The rise of graph neural networks (GNN) has provided a
new paradigm for modeling the structure of hyperspectral data.
Graph Attention Networks (GAT), in particular, overcome the
limitations of traditional graph convolutional networks (GCN)
by introducing an attention mechanism, becoming a valuable
tool for processing non-Euclidean data. Early graph-based
HAD methods attempted to capture inter-pixel relationships,
but suffered from significant limitations. The emergence of
GCN has promoted the integration of graph structures with
deep learning. GCN aggregates information through weighted
averaging of neighborhood features, has shown potential in
modeling hyperspectral spatial-spectral relationships. However, it relies on the homogeneous graph assumption, assuming
that all nodes and edges are of the same type, making it
difficult to handle the heterogeneous structure prevalent in
hyperspectral data. Feature aggregation relies on predefined
fixed weights, failing to dynamically capture complex internode relationships and making them susceptible to noise.
Simple weighted averaging operations struggle to distinguish
the importance of neighboring nodes, diluting key features
sensitive to anomalies. Subsequent improvements, such as
dynamic graph models and multi-scale feature extraction, have
alleviated these issues to some extent, but remain limited in
their ability to model node relationships, and their performance
on sparse or heterogeneous graphs remains suboptimal.
In contrast, GAT dynamically assigns node weights through
an attention mechanism, providing a more flexible solution
for HAD.It eliminates the need to rely on graph homogeneity
assumptions and automatically distinguishes the importance
of neighboring nodes by learning attention coefficients, effectively handling heterogeneous scenes with mixed feature
types in hyperspectral data. The multi-head attention mechanism extracts node features from multiple perspectives,
enhancing the ability to capture anomalies of varying scales
and spectral characteristics. Dynamic adjustment of attention
weights enables the model to adaptively suppress interference
from noisy nodes, improving sensitivity to subtle anomalies
[43], [44], [45].

6718

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 4. The proposed MGAE-based HAD flow chart. First, the input hyperspectral image is constructed as a spatial topological graph using the KNN algorithm.
Subsequently, a preliminary masking operation is performed on the node features, and the masked graph data is input into the GAT encoder. At the encoder
output layer, a re-masking strategy is used to mask the hidden layer representations twice. The processed features are then passed through the GAT decoder to
reconstruct the original spectral features. Finally, a dual loss function is used to jointly optimize the reconstruction error and the graph structure smoothness
constraint to output the anomaly detection result graph.

The MGAE proposed in this study further expands the application of GAT in HAD. Unlike methods that rely solely on
GAT for feature aggregation, MGAE combines GAT with an
autoencoder architecture to reconstruct background through an
“encode-decode” process. A re-masking strategy is introduced
to force the model to learn more robust feature representations, avoiding the “trivial mapping” problem that traditional
GAT often falls prey to. Furthermore, by constraining feature
smoothness through a graph Laplacian regularization loss, the
topological relationships captured by GAT are more consistent with the spatial continuity of hyperspectral data, further
improving the separability of background and anomalies. This
design not only retains GAT’s ability to model complex
relationships but also enhances the stability and accuracy of
detection through self-supervised learning and regularization
mechanisms.
C. Masking Strategy
Masking is a technique that precisely controls specific bits
of target data through binary bitwise operations. Its core
approach involves extracting, modifying, filtering, or flipping
specific bits in the target data using a binary sequence of the
same length as the target data through bitwise operations such
as AND, OR, and XOR. It is widely used in tasks such as
classification, anomaly detection, and background suppression
to achieve refined control over binary data.
This study introduces a re-masking strategy that applies
double AND operations to deeply couple the masking process
with graph topology. This shifts the model’s background
learning from “individual pixel features” to “neighborhood
correlation patterns”. Ultimately, anomalous nodes exhibit
elevated reconstruction errors due to violations of background

correlation patterns, enabling effective discrimination between
anomalies and background. This design not only ensures
the core capability of the mask operation to “selectively
retain key information” but also breaks through the traditional
mask’s dependence on linear relationships and static scenes
through graph structure guidance, and significantly improves
the robustness of HAD.
III. P ROPOSED M ETHODOLOGY
In this section, we initially outline our approach. Subsequently, we elaborate on the implementation specifics of each
element of our method.

A. GAT-Based Autoencoder
Our proposed anomaly detection method consists of three
main steps: topology graph generation, re-masking operation,
and graph autoencoder reconstruction based on GAT. The
overall architecture of MGAE is shown in Fig. 4.
First, we load the three-dimensional HSI as a node feature
matrix x, where each pixel in the image is treated as a node.
To capture the spatial relationships between pixels, adjacency
information is constructed using the KNN algorithm. This step
creates a topology graph, which represents the connectivity
between neighboring pixels based on their feature similarities.
The adjacency matrix reflects the inherent spatial and spectral
dependencies in hyperspectral data, which is crucial for capturing the correlations between different spectral bands and
pixels in the image. It can be expressed with the following
formula:
E = KNN(x, x, k)

(2)

TU et al.: SELF-SUPERVISED MASKED GRAPH AUTOENCODER FOR HYPERSPECTRAL ANOMALY DETECTION

Fig. 5. Random masking operation in the re-masking process.

where E is the set of edges and k is the parameter in the KNN
algorithm that specifies the number of nearest neighbor nodes
each node should connect to.
Subsequently, an initial masking operation is applied to the
node feature matrix x, where a random subset of features is set
to zero. The masked feature matrix, along with the adjacency
matrix, is then fed into a GAT-based encoder consisting of
multiple GATConv layers. The encoder learns to capture spatial and spectral dependencies through a multi-head attention
mechanism. Each attention head independently computes the
attention coefficients ai j , representing the relationship strength
between node i and node j. The encoder aggregates the node
features based on these attention coefficients, producing a new
node feature representation. This process retains inter-node
relationships while combining spatial and spectral information.
The encoder outputs the latent representation rep, with dimensions nhead × dhidden , where nhead is the number of attention
heads and dhidden is the hidden feature dimension. This latent
representation captures node relationships and feature information, serving as the basis for the subsequent reconstruction
process. A second masking operation is applied to the encoder
output as part of our proposed re-masking strategy, which
helps the model learn more robust feature representations by
reconstructing the missing parts of the data.
xmasked = x

M1

(3)

rep = Encoder(xmasked , E)

(4)

repremasked = rep

M2

(5)

where the symbol denotes element-wise multiplication, and
M1 and M2 are the initial mask matrix and the re-mask matrix,
respectively. The masked positions are set to 0, while all other
positions are set to 1.
The re-masked rep is then passed to the GAT-based decoder,
which reconstructs the node feature matrix x̂. The decoder
attempts to recover the original features of the nodes based
on the encoded and re-masked representation. The output of
this stage is an approximation of the original hyperspectral
data, which is compared to the actual data during training to
compute the reconstruction loss.
x̂ = Decoder(repremasked , E)

(6)

B. Re-Masking Strategy
The proposed re-masking strategy is applied at the data
input stage and the encoder output stage. The masking method
is shown in the Fig.5. Its design principle is as follows:

6719

1) Masked Feature Reconstruction: When the mask dimension exceeds the input dimension, ordinary autoencoders
tend to learn meaningless “identity functions”, making the
encoded representation useless. This problem is particularly
prominent in graph data with small node feature dimensions, and existing graph autoencoders often ignore this
problem. Inspired by denoising autoencoders which avoid
trivial solutions by deliberately corrupting the input, we use
masked autoencoders as the basic framework of MGAE. In
our method, a portion of nodes is randomly selected and
their features are replaced with zero. The resulting masked
feature matrix defines the characteristics of each node as
follows:
(
0,
vi ∈ e
V
x̃i =
(7)
xi ,
vi < e
V
The goal of MGAE is to reconstruct masked node features
using partially observed node signals and an input adjacency
matrix. By randomly selecting a subset of nodes, setting their
features to zero, and performing uniform random sampling
without replacement, the mask distribution is balanced (preventing all nodes’ neighbors from being completely masked or
visible). Finally, the masked node features are reconstructed
using the partially observed node signals and the input adjacency matrix. In graph autoencoders, nodes rely on neighbor
information to optimize their features, and this sampling
strategy effectively maintains this balance.
2) GAE Decoder With Re-Mask Decoding: The decoder
needs to map the latent code back to the input features, and its
design is related to the semantic complexity of the input. For
graph data, traditional graph autoencoders often use non-neural
network decoders or basic multi-layer perceptrons, which has
limited expressive power. This results in the latent code being
highly similar to the input features, making it difficult to
form a compressed and information-rich representation. To
address this, MGAE uses a more expressive single-layer graph
attention network as the decoder. This reconstructs features
based on node neighborhood information rather than relying
solely on the nodes themselves, enabling the encoder to learn
more abstract latent representations.
To further advance compressed representation learning, we
introduce a re-masking technique: the masked node indices
are reset to zero again at the latent code level to simulate
additional noise. This forces the masked nodes to reconstruct
their input features using the latent representations of their
unmasked neighbors. The re-masked latent code is defined as:
(
0,
hi ∈ e
V
h̃i =
(8)
hi ,
hi < e
V
C. Twice Loss
Our framework employs a dual loss function named Twice
Loss, as illustrated in the Fig. 6. Subsequently, we will
elaborate on the conceptual design of the loss function.
1) Reconstruction Loss: We use the squared L2 norm to
calculate the loss, which imposes a greater penalty on larger
errors. This means that if some pixels have larger differences,

6720

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

smoother reconstruction effect, while the anomalous areas,
due to weaker connectivity in the graph structure, are less
constrained by the model in their reconstruction, which helps
enhance the identification and detection of anomalous areas.
The smoothness loss not only improves the accuracy of background reconstruction but also enhances anomaly detection
sensitivity by reducing over-reconstruction in anomalous areas.
3) Twice Loss: In summary, we define the loss function L
for MGAE as follows:
L = α · Lrec + (1 − α) · Lsmooth


= α · ||X 0 − X||22 + (1 − α) · abs Tr(Z T LZ) · 0.00001 (11)
Fig. 6. The implementation of the proposed twice loss.

their contribution to the loss will also be greater, and the
model will work harder to reduce these differences. This
characteristic makes the squared L2 norm suitable for image
reconstruction tasks that are sensitive to global errors.
Lrec = kX 0 − Xk22

(9)

where Lrec is the reconstruction loss, which measures the
difference between the input X and the reconstructed output X 0 .
The goal is to minimize this loss, making the reconstructed X 0
as close as possible to the input. X 0 denotes the reconstructed
output, i.e., the result obtained after the reconstruction network
model processes the input, representing the hyperspectral
image data that the model tries to restore; X represents the
input data, i.e., the original image data, which serves as the
“ground truth” for the model during reconstruction. We hope
that X 0 can be as close as possible to X.
2) Smooth Loss: Although the traditional reconstruction
loss effectively measures the difference between the input
and output images, it treats all pixels ‘equally’ without
considering the local structural relationships between pixels
(features). This approach may lead the model to reconstruct
all areas (including anomalous regions) to the same extent
in HAD, thereby affecting the detection performance. To
further enhance the network’s effectiveness in reconstructing
the background of hyperspectral images and to utilize the local
structural information in the data, we introduce a quadratic loss
based on graph Laplacian regularization.


L smooth = abs Tr(Z T LZ) · 0.00001
(10)
where Z represents the feature representation output by the
model, L is the graph Laplacian matrix, and L smooth is the
smoothness loss, also referred to as the second loss. The graph
Laplacian matrix L, defined through the graph’s adjacency
matrix and degree matrix, captures the local relationships
between pixels or features in the data. The primary purpose of
regularization is to guide the model to maintain consistency
in features during the training process, especially in the
background areas, ensuring that the reconstruction between
adjacent pixels remains smooth and consistent. The factor of
0.00001 is multiplied to balance the magnitudes of the two
terms, ensuring the effectiveness of the loss function.
By minimizing the smoothness loss, the model reduces the
differences among adjacent feature points in high-dimensional
space. This means that the background areas will exhibit a

where Lrec is the reconstruction loss, L smooth is the smoothness
loss, and α is a hyperparameter. α controls the strength of
the graph Laplacian smoothness loss. By adjusting α, we can
flexibly balance the trade-off between smoothness in background reconstruction and sensitivity in anomaly detection.
When α is large, the model emphasizes local smoothness more
in the reconstruction process, which is suitable for optimizing
background areas; when α is small, the model handles feature
changes in anomalous areas more flexibly, avoiding excessive
smoothing of anomalous areas.
D. Anomaly Scores
Anomalies are measured by the difference (diff ) between the
reconstructed and original node feature matrices. The L2 norm
and Mahalanobis distance are computed from this difference
and combined with weights to produce a comprehensive
anomaly score, which serves as the final detection result. Their
definitions are as follows:
1) L2 Norm: Measures the Euclidean distance between
the original data and the reconstructed data. The calculation
formula for scores l2 is shown as follows:
diff = x − x̂
scores l2 =

(12)

d
X

(diffi j )2

(13)

j=1

where diff represents the difference between the original
feature matrix x and the reconstructed feature matrix x̂. x is the
original feature matrix, x̂ is the reconstructed feature matrix,
i is the node index, j is the feature dimension, and d is the
total number of features.
2) Mahalanobis Distance: Incorporating the covariance
matrix, it measures the deviation of node features from the
global distribution. The calculation formula for scores ma is
shown as follows:
Σ = Cov(diff)
Σ

(14)

= (Cov(diff))
n
1X
µ=
diffi
n

−1

−1

(15)
(16)

i=1

scores ma = diag (diff − µ) · Σ−1 · (diff − µ)>



(17)

where Σ represents the covariance matrix of the differences
diff, and Σ−1 is its inverse, normalizing distances by accounting
for feature correlations. µ is the mean vector of diff, and n

TU et al.: SELF-SUPERVISED MASKED GRAPH AUTOENCODER FOR HYPERSPECTRAL ANOMALY DETECTION

Algorithm 1 Proposed MGAE for Hyperspectral Anomaly
Detection

is the number of nodes. Finally, diag(·) extracts the diagonal
elements, yielding the Mahalanobis distance scores for each
node.
We use λ to combine scores l2 and scores ma with
weighting, resulting in a method for calculating anomaly
scores. The formula is as follows:
Anomaly Scores = λ · scores l2 + (1 − λ) · scores ma. (18)
During training, λ is set to 0.85 to focus on the model’s
reconstruction error. During testing, λ is set to 0.5, equally
weighting the L2 norm and Mahalanobis distance. The L2 norm
captures pointwise feature deviations, while the Mahalanobis
distance detects global distribution anomalies, resulting in a
more comprehensive anomaly score for detection.
IV. E XPERIMENTS
In order to verify the detection performance of our proposed
method, a series of contrast tests are set up in this section.
A. Experimental Datasets
In this article, the proposed method is evaluated on six real
hyperspectral data sets captured at different scenes, which are
listed as follows.
1) BEACH-I: The first hyperspectral data set was acquired
by the Raster Object-oriented Sensor Image System
(ROSIS-03) sensor covering the Pavia. This scene covers
area of 100×100 pixels with 224 spectral channels in
wavelengths ranging from 370 to 2510 nm. In the experiments, a total of 102 bands are used after removing

6721

the water-absorption bands. The spatial resolution is
approximately 1.3m.
2) BEACH-II: The second hyperspectral data set was
acquired by the AVIRIS sensor covering the Bay
Chamoagne. This scene covers area of 100×100 pixels
with 188 spectral channels in wavelengths ranging from
370 to 2510 nm. The spatial resolution is approximately
4.4m.
3) HYDICE: The third hyperspectral dataset, acquired by
the AVIRIS sensor, covers an urban area in California.
The scene has a pixel size of 100 × 100 pixels, an
unknown wavelength range, 205 spectral channels, and
an anomaly ratio of 0.91%. The spatial resolution is
1 meter.
4) Gainesville: The fourth hyperspectral dataset, acquired
by the AVIRIS sensor, covers the Gainesville area. This
scene has a pixel size of 100 × 100 pixels, an unknown
wavelength range, 191 spectral channels, and 0.52%
anomaly ratio. The spatial resolution is 3.5 meters.
5) Gulfport: The fifth hyperspectral dataset, acquired by the
AVIRIS sensor, covers the Gulfport area. This scene has
a pixel size of 100 × 100 pixels, an unknown wavelength
range, 191 spectral channels, and an anomaly ratio of
0.60%. The spatial resolution is 3.4 meters.
6) Los Angeles: The sixth hyperspectral dataset, acquired
by the AVIRIS sensor, covers the Los Angeles area.
This scene has a pixel size of 100 × 100 pixels, an
unknown wavelength range, 205 spectral channels, and
an anomaly ratio of 0.87%. The spatial resolution is 7.1
meters. The image and ground truth of this dataset are
shown respectively in Fig. 7 (a) and (b).
B. Comparison Algorithms and Evaluation Criteria
1) Comparison Method: This paper compares the proposed
MGAE algorithm with six existing HAD algorithms, including
RX [8], LRX [9], LSMAD [46], FrFE [47], BockNet [48],
PUNNet [49] and PDBSNet [24]. The RX algorithm is a
classic method based on statistical modeling, while LRX
is a localized version of the RX algorithm. LSMAD is a
representative method based on low-rank and sparse matrix
decomposition. The experimental parameter initial rank l0 is
set to a value matching 0.6 times the number of bands in the
HSI, and the initial number of mixed Gaussian noise K is
set to 4. FrFE is a complex method based on the fractional
Fourier transform and entropy principles that enhances HAD
by optimizing signal enhancement and noise suppression.
BockNet is a self-supervised blind-block reconstruction network with a guard window. It uses the blind-block (inner
window) to protect central pixels and only leverages outer
window information to predict central pixels, thus increasing
the reconstruction error of anomalous pixels. PUNNet is an
anomaly detection method using a global feature injection
blind-spot network. PDBSNet employs a pixel-reorganized
downsampling blind-spot reconstruction mechanism, where
the center pixel is masked as the blind spot and its spectral
information is reconstructed from the surrounding neighborhood. RX, LRX, and FrFE are non-parametric techniques. For
BockNet, we employ the parameters reported in its original

6722

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 7. Pseudo-color images and ground-truth maps of the six selected datasets. (a) Pseudo-color images. (b) Ground-truth maps.
TABLE I
AUC VALUES OF THE C OMPARISON A LGORITHMS AND O UR P ROPOSED A LGORITHM ON THE S IX S ELECTED DATASETS

paper. PUNNet utilizes kernel sizes of (1, 4, 5, 5, 5, 4).
PDBSNet is configured with kernel sizes ((4, 4), (5, 5), (5,
5), (5, 5), (4, 4), (5, 5)). Our algorithm has two parameters, k
and α. In the comparative experiments, we used the optimal
parameters selected through experimentation. The specific
parameter analysis will be discussed in detail in the later
section on parameter analysis.
2) Evaluation Criteria: Based on the real data provided
in Fig. 7, we can deeply evaluate the performance of each
detector with the help of 3D ROC curves and 2 ROC curves.
By analyzing the three corresponding 2D ROC curves – the
relationship between detection rate Pd and false alarm rate
P f , detection rate Pd and threshold τ, and false alarm rate P f
and threshold τ – we can clearly understand the performance
differences of different anomaly detectors in the relationship
among Pd , P f , and threshold τ.
C. Comparison Experiments and Detection Performance
We conducted comparison experiments of our algorithm
with others on six datasets, and the detection results are shown
in Fig. 8. The AUC values of each algorithm are listed in
Table I. We will analyze the strengths and weaknesses of each
algorithm and their detection performance.
1) 2D ROC: The Fig. 9 illustrates the True Positive Rate
(TPR) performance curves of multiple anomaly detection

algorithms across six hyperspectral datasets versus the decision threshold τ. The vertical axis quantifies the algorithms’
anomaly detection capability (TPR), while the horizontal axis
determines the anomaly/background classification boundary.
The curves exhibit a general trend of increasing TPR with
decreasing threshold, but reveal distinct performance characteristics across algorithms and datasets.The MGAE algorithm
consistently exhibits steeper performance curves across all
datasets, rapidly approaching a TPR of 1 at low thresholds
(τ < 0.2) – for instance, achieving TPR > 0.95 on the BEACH1 dataset. This behavior indicates exceptional sensitivity to
subtle anomalies and significant robustness to threshold selection. In contrast, traditional algorithms (e.g., RX, LRX) display
flatter, lower curves, requiring substantially higher thresholds (τ > 0.4) to approach MGAE’s TPR performance,
demonstrating pronounced parameter dependence.MGAE’s
performance advantage is most distinct in homogeneous scenes
like BEACH. Under the complex background of HYDIC,
MGAE maintains a clear lead over methods such as BockNet
and PUNNet. On the Gainesville and Gulfport datasets, while
PUNNet approaches MGAE’s performance within mid-range
thresholds (0.2 ∼ 0.5), it fails to match MGAE’s effectiveness
at low thresholds (τ < 0.2). For the spectrally confounded
Los Angeles scene, all algorithms exhibit marginally reduced
peak TPR. However, MGAE sustains its superior performance,

TU et al.: SELF-SUPERVISED MASKED GRAPH AUTOENCODER FOR HYPERSPECTRAL ANOMALY DETECTION

6723

Fig. 8. Label maps of the selected datasets and anomaly maps of all methods. (a) BEACH-I. (b) BEACH-II. (c) HYDICE. (d) Gainesville. (e) Gulfport.
(f) Los Angeles.

confirming robustness in challenging environments. Collectively, these curves demonstrate MGAE’s high detection
accuracy and scene adaptability across an extended threshold
range, significantly outperforming other algorithms.
2) 3D ROC: The Fig. 10 presents the 3D ROC performance of eight anomaly detection algorithms across six
hyperspectral datasets, jointly evaluating false positive rate
(FPR), decision threshold (τ), and true positive rate (TPR)
to characterize detection trade-offs. MGAE demonstrates significant advantages across all scenarios: on homogeneous
backgrounds (e.g., BEACH-I) with FPR < 0.3 and τ ∈
[0.2, 0.6], it sustains TPR > 0.9, surpassing RX (TPR < 0.7)
and LRX (TPR < 0.6) by 30 − 50 percentage points. Under
complex environments like HYDICE (urban heterogeneity)
and Los Angeles (spectral confusion), MGAE achieves higher
TPR at equivalent FPR through relaxed thresholds (τ reduced
by 0.1−0.2), significantly outperforming deep learning counterparts (BockNet, PDBSNet). This superiority stems from
MGAE’s graph-structural hyperspectral modeling: graph attention mechanisms capture spectral-spatial correlations while
dual-mask loss suppresses background interference, maintaining dynamic high-detection/low-FPR balance across wide
threshold ranges. In contrast, traditional methods (e.g., RX,
limited by Gaussian assumptions) and deep approaches (e.g.,

PUNNet, prone to local overfitting) exhibit flatter curves
requiring strict thresholds (τ < 0.2) or high FPR tolerance
(> 0.4) to approach MGAE’s performance, validating its
robustness in complex hyperspectral scenarios.
3) Box Plot: The Fig. 11 displays boxplots comparing
anomaly detection scores (green) and background scores
(red) across methods, revealing MGAE’s consistent superiority. In BEACH-I, it achieves near-maximal anomaly scores
with minimal background interference, effectively handling
spectral variability. While experiencing a slight decline in
BEACH-II, it maintains competitive robustness across beach
environments. MGAE dominates in HYDICE (complex urban
areas) and Gainesville, demonstrating cross-dataset stability,
and excels in Gulfport’s airport scene with optimal anomalybackground separation. For the spectrally confounded Los
Angeles dataset, MGAE sustains exceptional anomaly detection with suppressed background. Crucially, MGAE markedly
outperforms traditional methods (RX/LRX/LSMAD) in challenging environments featuring diverse anomalies, while its
sustained low background scores confirm precise spectral
discrimination—addressing hyperspectral imaging’s fundamental challenge of anomaly-background separation.
4) Summary: As evidenced by Fig. 8 and Table I, MGAE
achieves superior AUC values across all datasets, consistently

6724

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 9. 2D ROC curves of all methods for the six datasets.

Fig. 10. 3D ROC curves of all methods for the six datasets.

outperforming comparative methods. Corroborated by ROC
characteristics, MGAE maintains higher true positive rates and

lower false positive rates than traditional approaches (e.g., RX,
LSMAD) in every operational environment. This demonstrates

TU et al.: SELF-SUPERVISED MASKED GRAPH AUTOENCODER FOR HYPERSPECTRAL ANOMALY DETECTION

6725

Fig. 11. Box plots of all methods for the six datasets.
TABLE II
AUC VALUES OF A BLATION E XPERIMENTS ON S IX DATASETS

precise anomaly discrimination with minimal false alarms —
a critical advantage for real-world deployment. The 3D performance evolution further confirms MGAE’s stability and
adaptability across threshold configurations. Collectively, these
cross-dataset analyses validate MGAE’s robust efficacy for
HAD.
D. Ablation Study
This section analyzes the effectiveness of the proposed
re-masking strategy and twice loss strategy. Using a traditional Graph Attention Network (GAT) as the baseline
framework, the proposed MGAE incorporates an innovative
re-masking strategy that mitigates decoder-induced reconstruction error averaging by preventing simplistic mapping
relationships. Concurrently, a twice loss strategy is introduced to balance background modeling accuracy and anomaly
detection sensitivity. Table II compares the AUC performance
of the three models across six datasets. The re-masking
strategy alone provides modest improvements over the baseline GAT, as background information loss during re-masking

Fig. 12. The impact of parameter k selection on the AUC values changes in
the results of the experimental dataset.

can introduce false anomalies, while random masking uncertainty may reconstruct anomalies—increasing false positive
rates. The twice loss strategy addresses these limitations
by preserving global background context while minimizing
constraints on anomalies to suppress their reconstruction.

6726

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 13. The variation curve of AUC values in the experimental dataset results caused by different parameters α.

Consequently, MGAE integrating both strategies achieves significant enhancement in HAD capability.
E. Parameter Analysis
In this section, we analyze the influence of the parameters
k and α on the detection performance of the proposed MGAE
method.
1) Parameter k: The parameter k is critical in the MGAE
method as it defines the number of nearest neighbors considered during the anomaly detection process. This parameter’s
influence on the detection performance is profound, as it
directly affects both the sensitivity and specificity of the
method. As shown in Fig. 12, our analysis of six datasets with
varying k-values from 11 to 101 has demonstrated the critical
role of k in the performance of the MGAE method. The sensitivity and specificity of anomaly detection are significantly
influenced by the choice of k, affecting the overall accuracy
and reliability of the method.To determine the optimal k value,
we analyze the AUC values for different k-values on each
dataset. The data revealed that datasets such as BEACH-I
consistently performed well across a broad range of k-values
(maintaining AUC between 0.99 and 0.98), indicating robustness to the choice of k. In contrast, datasets like Gainesville
exhibited substantial fluctuations in performance (AUC rising
from 0.96 to 0.98), highlighting a sensitivity to k-value selection. For instance, the Gainesville dataset showed improved
performance as k increased from 11 to 101, peaking at k = 101
with the highest AUC value of 0.98. This suggests that a higher
k-value may be necessary to capture the broader context within
this particular dataset, reducing noise and minimizing false
positives. Complex urban environments (HYDICE, Los Angeles) require k ≥ 71 to stabilize performance (> 0.97 AUC) by
suppressing outlier-induced false positives, whereas structured

scenes (Gulfport) achieve peak discrimination at moderate
k-values (51-71, AUC 0.97) through balanced spatial-spectral
modeling. This demonstrates that optimal k is intrinsically
linked to scene heterogeneity.
2) Parameter α: The parameter α controls the proportion of
reconstruction loss and smoothness loss in our proposed Twice
Loss. In order to make the effect of parameter A more intuitive,
we set the value of k in the parameter experiment. Fig. 13
illustrates the impact of parameter α on the Area Under the
Receiver Operating Characteristic (ROC) curve (AUC) values
across different datasets.
The Fig. 13 and Table III demonstrate the critical influence of the loss-balancing parameter α on MGAE’s AUC
performance across hyperspectral datasets. For beach environments, BEACH-I exhibits monotonic AUC improvement
with increasing α, stabilizing near α = 0.3 and peaking
at 0.9987 (α = 0.8); BEACH-II maintains stable performance despite minor fluctuations at α = 0.2, achieving
dual maxima of 0.9946 at α = 0.6 and 0.9. Urban and
mixed scenes show distinct patterns: Gainesville displays
rapid AUC escalation beyond α = 0.3, stabilizing at its
peak 0.9748 (α = 0.5), while Los Angeles manifests gradual improvement culminating at maximum AUC (α = 0.9).
Crucially, when α = 1 (pure reconstruction loss without
smoothness regularization), HYDICE and Gulfport attain their
highest AUC values - indicating smoothness loss provides
negligible benefit for these specific environments. These findings establish α’s dual role in HAD: 1) Optimizing the
reconstruction-smoothness tradeoff enhances model efficiency,
and 2) Enabling scene-specific performance customization
through spectral-characteristic-adaptive loss balancing. This
tradeoff underscores α’s critical function in tailoring detection
precision to diverse operational scenarios while maintaining
computational effectiveness.

TU et al.: SELF-SUPERVISED MASKED GRAPH AUTOENCODER FOR HYPERSPECTRAL ANOMALY DETECTION

6727

TABLE III
T HE S ELECTION OF PARAMETER α AND THE I MPACT OF D IFFERENT α VALUES ON THE AUC OF E XPERIMENTAL R ESULTS ACROSS S IX DATASETS

TABLE IV
I NFERENCE T IME OF D IFFERENT D ETECTION M ETHOD S ON S IX DATASETS

F. Comparison of Inference Times
The Table IV reports the inference times of various comparison methods across six datasets. Except for BockNet,
PUNNet, PDBSNet, and our MGAE (implemented using the
PyTorch framework), all other methods were coded in MATLAB 2021b. The five traditional physics-driven methods (RX,
LRX, LAMAD, FrFE) exhibit significantly longer inference
times across most datasets compared to their deep learningbased counterparts. Although MGAE involves graph structure
construction and graph attention-based feature aggregation —
introducing marginal computational overhead — it consistently achieves the shortest inference time across all datasets,
notably outperforming BockNet and PDBSNet by an order
of magnitude in efficiency. This result underscores MGAE’s
superior balance between model complexity and computational
efficiency.
V. C ONCLUSION
In this article, we introduce Masked Graph Autoencoder
(MGAE), a pioneering approach designed for HAD. This innovative method leverages graph neural networks (GNN) to learn
graph representations unsupervised. At the core of MGAE’s
strategy is the reconstruction of masked node features, which
is a significant departure from traditional approaches. Unlike

conventional Graph Autoencoders (GAE) that utilize multilayer perceptrons (MLP) for decoding, we implement a
re-mask decoding strategy using GNN to enhance the capability of MGAE. Additionally, within the GNN framework, we
integrate the Laplacian matrix with the reconstructed feature
matrix. This integration is crucial as it significantly boosts the
model’s sensitivity to topological variations and irregularities
within the data structure. Such an approach allows for the
effective capture of nuanced anomaly patterns by leveraging
the inherent graph structure encoded by the Laplacian matrix,
thereby augmenting the detection capabilities of our model.
By incorporating these advanced graph-based insights, MGAE
demonstrates an ability to outperform conventional methods,
particularly in detecting subtle and complex anomalies in
hyperspectral images. This advancement establishes MGAE
as a potent tool in the hyperspectral imaging field, providing
enhanced accuracy and reliability in anomaly detection.
The experimental results on six real HSIs demonstrate that
our approach outperforms other state-of-the-art HAD methods.
Future work will focus on integrating spatial information into
the MGAE framework to enhance anomaly detection by leveraging both spectral and spatial features. Additionally, optimizing model parameters adaptively and exploring more refined
weight definitions between graph nodes will be pursued to
improve sensitivity to subtle anomalies. Finally, incorporating

6728

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

advanced learning techniques like self-supervised learning
could further boost generalization across diverse hyperspectral
datasets, pushing the boundaries of detection accuracy.
R EFERENCES
[1]

Y. Liu, “Development of hyperspectral imaging remote sensing
technology,” Nat. Remote Sens. Bull., vol. 25, no. 1, pp. 439–459, 2021.
[2] R. J. Chu, N. Richard, H. Chatoux, C. Fernandez-Maloigne, and
J. Y. Hardeberg, “Hyperspectral texture metrology based on joint probability of spectral and spatial distribution,” IEEE Trans. Image Process.,
vol. 30, pp. 4341–4356, 2021.
[3] B. Yang, Z. Wang, X. Liu, L. Fang, and L. Liu, “Reciprocal
transformation-based joint deep and broad learning for change detection
with heterogeneous images,” IEEE Trans. Geosci. Remote Sens., vol. 62,
2024, Art. no. 4413414.
[4] B. Yang, Y. Mao, L. Liu, X. Liu, Y. Ma, and J. Li, “From trained
to untrained: A novel change detection framework using randomly
initialized models with spatial–channel augmentation for hyperspectral
images,” IEEE Trans. Geosci. Remote Sens., vol. 61, 2023, Art. no.
4402214.
[5] C.-I. Chang, “Hyperspectral target detection: Hypothesis testing, signalto-noise ratio, and spectral angle theories,” IEEE Trans. Geosci. Remote
Sens., vol. 60, 2022, Art. no. 5505223.
[6] N. M. Nasrabadi, “Hyperspectral target detection: An overview of
current and future challenges,” IEEE Signal Process. Mag., vol. 31,
no. 1, pp. 34–44, Jan. 2014.
[7] J. Dai, C. Deng, W. Wang, and X. Liu, “Low-rank and sparse tensor
recovery for hyperspectral anomaly detection,” in Proc. IEEE Int.
Geosci. Remote Sens. Symp. (IGARSS), Jul. 2017, pp. 1141–1144.
[8] I. S. Reed and X. Yu, “Adaptive multiple-band CFAR detection of an
optical pattern with unknown spectral distribution,” IEEE Trans. Acoust.,
Speech, Signal Process., vol. 38, no. 10, pp. 1760–1770, Oct. 1990.
[9] J. M. Molero, E. M. Garzon, I. Garcia, and A. Plaza, “Analysis and
optimizations of global and local versions of the RX algorithm for
anomaly detection in hyperspectral data,” IEEE J. Sel. Topics Appl.
Earth Observ. Remote Sens., vol. 6, no. 2, pp. 801–814, Apr. 2013.
[10] A. V. Kanaev and J. Murray-Krezan, “Segmentation adaptive RX: An
algorithm for spectral anomaly detection in a variety of measuredradiance conditions,” Proc. SPIE, vol. 7695, Mar. 2010, Art. no. 769505.
[11] H. Kwon and N. M. Nasrabadi, “Kernel RX-algorithm: A nonlinear
anomaly detector for hyperspectral imagery,” IEEE Trans. Geosci.
Remote Sens., vol. 43, no. 2, pp. 388–397, Feb. 2005.
[12] S. Lin, M. Zhang, X. Cheng, L. Wang, M. Xu, and H. Wang,
“Hyperspectral anomaly detection via dual dictionaries construction
guided by two-stage complementary decision,” Remote Sens., vol. 14,
no. 8, p. 1784, Apr. 2022.
[13] S. M. Schweizer and J. M. F. Moura, “Hyperspectral imagery: Clutter
adaptation in anomaly detection,” IEEE Trans. Inf. Theory, vol. 46,
no. 5, pp. 1855–1871, May 2000.
[14] Z. Zha, B. Wen, X. Yuan, S. Ravishankar, J. Zhou, and C. Zhu, “Learning
nonlocal sparse and low-rank models for image compressive sensing:
Nonlocal sparse and low-rank modeling,” IEEE Signal Process. Mag.,
vol. 40, no. 1, pp. 32–44, Jan. 2023.
[15] Z. Zha, B. Wen, X. Yuan, J. Zhou, and C. Zhu, “Image restoration
via reconciliation of group sparsity and low-rank models,” IEEE Trans.
Image Process., vol. 30, pp. 5223–5238, 2021.
[16] L. Ren, D. Wang, L. Gao, M. Wang, and M. Huang, “Nonlocal and
deep priors for hyperspectral anomaly detection,” IEEE Trans. Geosci.
Remote Sens., vol. 63, 2025, Art. no. 5520415.
[17] M. Wang, Q. Wang, D. Hong, S. K. Roy, and J. Chanussot, “Learning
tensor low-rank representation for hyperspectral anomaly detection,”
IEEE Trans. Cybern., vol. 53, no. 1, pp. 679–691, Jan. 2023.
[18] A. Banerjee, P. Burlina, and C. Diehl, “A support vector method
for anomaly detection in hyperspectral imagery,” IEEE Trans. Geosci.
Remote Sens., vol. 44, no. 8, pp. 2282–2291, Aug. 2006.
[19] W. Basener, E. J. Ientilucci, and D. W. Messinger, “Anomaly detection
using topology,” Proc. SPIE, vol. 6565, Feb. 2007, Art. no. 65650J, doi:
10.1117/12.745429.
[20] Y. Xu, L. Zhang, B. Du, and L. Zhang, “Hyperspectral anomaly detection
based on machine learning: An overview,” IEEE J. Sel. Topics Appl.
Earth Observ. Remote Sens., vol. 15, pp. 3351–3364, 2022.
[21] S. Li, K. Zhang, P. Duan, and X. Kang, “Hyperspectral anomaly
detection with kernel isolation forest,” IEEE Trans. Geosci. Remote
Sens., vol. 58, no. 1, pp. 319–329, Jan. 2020.

[22] J. Jiao, L. Xiao, and C. Wang, “Hyperspectral anomaly detection based
on intrinsic image decomposition and background subtraction,” IEEE
Access, vol. 13, pp. 15723–15738, 2025.
[23] D. Wang, L. Zhuang, L. Gao, X. Sun, X. Zhao, and A. Plaza, “Sliding
dual-window-inspired reconstruction network for hyperspectral anomaly
detection,” IEEE Trans. Geosci. Remote Sens., vol. 62, 2024, Art. no.
5504115.
[24] D. Wang, L. Zhuang, L. Gao, X. Sun, M. Huang, and A. J. Plaza,
“PDBSNet: Pixel-shuffle downsampling blind-spot reconstruction network for hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote
Sens., vol. 61, May 2023, Art. no. 5511914.
[25] P. Baldi, “Autoencoders, unsupervised learning and deep architectures,”
in Proc. Int. Conf. Unsupervised Transf. Learn. Workshop, 2011,
pp. 37–50.
[26] A. Emoto and R. Matsuoka, “Unsupervised anomaly detection in
hyperspectral imaging: Integrating tensor robust principal component
analysis with autoencoding adversarial networks,” IEEE Access, vol. 13,
pp. 21422–21433, 2025.
[27] D. Wang, L. Gao, Y. Qu, X. Sun, and W. Liao, “Frequency-to-spectrum
mapping GAN for semisupervised hyperspectral anomaly detection,”
CAAI Trans. Intell. Technol., vol. 8, no. 4, pp. 1258–1273, Dec. 2023,
doi: 10.1049/cit2.12154.
[28] S. Wu et al., “VJDNet: A simple variational joint discrimination network for cross-image hyperspectral anomaly detection,” Remote Sens.,
vol. 17, no. 14, p. 2438, Jul. 2025.
[29] Z. Zhao et al., “Hyperspectral anomaly detection via cascaded convolutional autoencoders with adaptive pixel-level attention,” Expert Syst.
Appl., vol. 279, Jun. 2025, Art. no. 127366.
[30] X. Sun, Y. Zhang, Y. Dong, and B. Du, “Contrastive self-supervised
learning-based background reconstruction for hyperspectral anomaly
detection,” IEEE Trans. Geosci. Remote Sens., vol. 63, 2025, Art. no.
5504312.
[31] X. Wang et al., “FCMMA: Fourier conditional mask-based mixed
attention method for hyperspectral anomaly detection,” IEEE Trans.
Geosci. Remote Sens., vol. 63, 2025, Art. no. 5507012.
[32] D. Wang, L. Ren, X. Sun, L. Gao, and J. Chanussot, “Nonlocal and
local feature-coupled self-supervised network for hyperspectral anomaly
detection,” IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens.,
vol. 18, pp. 6981–6993, 2025.
[33] X. Su, X. Shen, H. Liu, L. Chen, G. Vivone, and X. Zhou, “Toward
model-independent separative training for deep hyperspectral anomaly
detection with mask guidance,” IEEE J. Sel. Topics Appl. Earth Observ.
Remote Sens., vol. 18, pp. 15412–15426, 2025.
[34] D. Wang et al., “HyperSIGMA: Hyperspectral intelligence comprehension foundation model,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 47, no. 8, pp. 6427–6444, Aug. 2025.
[35] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Lió, and
Y. Bengio, “Graph attention networks,” 2017, arXiv:1710.10903.
[36] S. Brody, U. Alon, and E. Yahav, “How attentive are graph attention
networks?,” 2021, arXiv:2105.14491.
[37] Y. Dong, Q. Liu, B. Du, and L. Zhang, “Weighted feature fusion of
convolutional neural network and graph attention network for hyperspectral image classification,” IEEE Trans. Image Process., vol. 31,
pp. 1559–1572, 2022.
[38] R. Walsh, I. Osman, and M. S. Shehata, “Masked embedding modeling
with rapid domain adjustment for few-shot image classification,” IEEE
Trans. Image Process., vol. 32, pp. 4907–4920, 2023.
[39] J. Zhu, H. Ma, J. Chen, and J. Yuan, “High-quality and diverse fewshot image generation via masked discrimination,” IEEE Trans. Image
Process., vol. 33, pp. 2950–2965, 2024.
[40] E. Fix and J. L. Hodges, “Discriminatory analysis—Nonparametric
discrimination: Consistency properties,” Int. Stat. Rev., vol. 57,
p. 238, Jan. 1989. [Online]. Available: https://api.semanticscholar.org/
CorpusID:120323383
[41] T. M. Cover and P. E. Hart, “Nearest neighbor pattern classification,”
IEEE Trans. Inf. Theory, vol. IT-13, no. 1, pp. 21–27, Jan. 1967.
[42] S. T. Roweis and L. K. Saul, “Nonlinear dimensionality reduction by
locally linear embedding,” Science, vol. 290, no. 5500, pp. 2323–2326,
Dec. 2000. [Online]. Available: https://api.semanticscholar.org/
CorpusID:5987139
[43] T. Takikawa, D. Acuna, V. Jampani, and S. Fidler, “Gated-SCNN: Gated
shape CNNs for semantic segmentation,” 2019, arXiv:1907.05740.
[44] C. Ding, S. Sun, and J. Zhao, “MST-GAT: A multimodal
spatial–temporal graph attention network for time series anomaly
detection,” Inf. Fusion, vol. 89, pp. 527–536, Jan. 2023, doi: 10.1016/
j.inffus.2022.08.011.

TU et al.: SELF-SUPERVISED MASKED GRAPH AUTOENCODER FOR HYPERSPECTRAL ANOMALY DETECTION

[45] Y. Dongsheng, K. Ping, and X. Gu, “3D reconstruction based on GAT
from a single image,” in Proc. 17th Int. Comput. Conf. Wavelet Act.
Media Technol. Inf. Process. (ICCWAMTIP), Dec. 2020, pp. 122–125.
[46] L. Li, W. Li, Q. Du, and R. Tao, “Low-rank and sparse decomposition
with mixture of Gaussian for hyperspectral anomaly detection,” IEEE
Trans. Cybern., vol. 51, no. 9, pp. 4363–4372, Sep. 2021.
[47] R. Tao, X. Zhao, W. Li, H.-C. Li, and Q. Du, “Hyperspectral anomaly
detection by fractional Fourier entropy,” IEEE J. Sel. Topics Appl. Earth
Observ. Remote Sens., vol. 12, no. 12, pp. 4920–4929, Dec. 2019.
[48] D. Wang, L. Zhuang, L. Gao, X. Sun, M. Huang, and A. Plaza,
“BockNet: Blind-block reconstruction network with a guard window for
hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote Sens.,
vol. 61, 2023, Art. no. 5531916.
[49] D. Wang, L. Zhuang, L. Gao, X. Sun, and X. Zhao, “Global featureinjected blind-dpot network for hyperspectral anomaly detection,” IEEE
Geosci. Remote Sens. Lett., vol. 21, pp. 1–5, 2024.

Bing Tu (Senior Member, IEEE) received the M.S.
degree in control science and engineering from
Guilin University of Technology, Guilin, China, in
2009, and the Ph.D. degree in mechatronic engineering from Beijing University of Technology, Beijing,
China, in 2013.
From 2015 to 2016, he was a Visiting Researcher
with the Department of Computer Science and Engineering, University of Nevada, Reno, NV, USA,
which was supported by China Scholarship Council.
He is currently a Full Professor with Nanjing University of Information Science and Technology, Nanjing, China. His research
interests include sparse representation, pattern recognition, and analysis in
remote sensing. He is an Associate Editor of IEEE J OURNAL OF S ELECTED
T OPICS IN A PPLIED E ARTH O BSERVATIONS AND R EMOTE S ENSING.

Baoliang He (Student Member, IEEE) received the
B.S. degree in electrical engineering and automation from Henan Polytechnic University, Jiaozuo,
Henan, China, in 2025. He is currently pursuing
the M.S. degree in optical engineering with Nanjing
University of Information Science and Technology, Nanjing, Jiangsu, China. His research interests
include hyperspectral anomaly detection.

Yan He (Member, IEEE) received the Ph.D. degree
in computer science from Hunan University, Changsha, Hunan, China, in 2025. She is currently a
Lecturer with Nanjing University of Information Science and Technology, Nanjing, China. Her research
interests include hyperspectral image processing and
remote sensing image registration.

Tao Zhou (Student Member, IEEE) is currently
pursuing the master’s degree in electronic science
and technology with the School of Electronic and
Information Engineering, Anhui Jianzhu University,
Hefei, Anhui, China.

6729

Bo Liu (Member, IEEE) received the B.S. and
Ph.D. degrees in optical engineering from Beijing
University of Posts and Telecommunications, Beijing, China, in 2008 and 2013, respectively. He is
currently a Professor with the School of Physics
and Optoelectronics, NUIST, China. His research
interests include all-optical signal processing, radio
over fiber, and broadband optical communication.

Jun Li (Fellow, IEEE) received the B.S. degree in
geographic information systems from Hunan Normal
University, Changsha, China, in 2004, the M.E.
degree in remote sensing from Peking University,
Beijing, China, in 2007, and the Ph.D. degree in
electrical engineering from the Instituto de Telecomunica ções, Instituto Superior Técnico (IST),
Universidade Técnica de Lisboa, Lisbon, Portugal,
in 2011.
From 2013 to 2021, she was a Full Professor with
Sun Yat-sen University. Since 2022, she has been
with China University of Geosciences as a Full Professor. She has received
several prestigious funding grants at the national and international levels.
She has authored more than 160 Journal Citation Report (JCR) articles, 60
international conference papers, and a book chapter.
Dr. Li has been serving as the Editor-in-Chief for IEEE J OURNAL
OF S ELECTED T OPICS IN A PPLIED E ARTH O BSERVATIONS AND R EMOTE
S ENSING since 2021.

Antonio Plaza (Fellow, IEEE) received the M.Sc.
and Ph.D. degrees in computer engineering from the
Hyperspectral Computing Laboratory, Department
of Technology of Computers and Communications,
University of Extremadura, Cáceres, Spain, in 1999
and 2002, respectively.
He is currently the Head of the Hyperspectral
Computing Laboratory, Department of Technology
of Computers and Communications, University of
Extremadura. He has authored more than 600 publications, including over 200 JCR journal articles
(over 160 in IEEE journals), 23 book chapters, and around 300 peer-reviewed
conference proceeding papers. His research interests include hyperspectral
data processing and parallel computing of remote sensing data.
Dr. Plaza was an Editorial Board Member of the IEEE Geoscience and
Remote Sensing Newsletter from 2011 to 2012 and IEEE Geoscience and
Remote Sensing Magazine in 2013. He was also a member of the Steering
Committee of IEEE J OURNAL OF S ELECTED T OPICS IN A PPLIED E ARTH
O BSERVATIONS AND R EMOTE S ENSING. He is a fellow of IEEE for contributions to hyperspectral data processing and parallel computing of Earth
observation data. He was a recipient of the recognition of Best Reviewers
of IEEE G EOSCIENCE AND R EMOTE S ENSING L ETTERS in 2009 and the
Best Reviewer of IEEE T RANSACTIONS ON G EOSCIENCE AND R EMOTE
S ENSING in 2010, for which he has served as an Associate Editor from
2007 to 2012. He was also a recipient of the Best Column Award of
IEEE Signal Processing Magazine in 2015, the 2013 Best Paper Award of
IEEE J OURNAL OF S ELECTED T OPICS IN A PPLIED E ARTH O BSERVATIONS
AND R EMOTE S ENSING , and the Most Highly Cited Paper (2005–2010) in
Journal of Parallel and Distributed Computing. He received best paper awards
at the IEEE International Conference on Space Technology and the IEEE
Symposium on Signal Processing and Information Technology. He has served
as the Director of Education Activities for the IEEE Geoscience and Remote
Sensing Society (GRSS) from 2011 to 2012 and the President of Spanish
Chapter of IEEE GRSS from 2012 to 2016. He has reviewed more than 500
manuscripts for over 50 different journals. He has served as the Editor-inChief for IEEE T RANSACTIONS ON G EOSCIENCE AND R EMOTE S ENSING
from 2013 to 2017. He has guest-edited ten special issues on hyperspectral
remote sensing for different journals. He is an Associate Editor of the IEEE
ACCESS (receiving the recognition as an Outstanding Associate Editor of the
journal in 2017). Additional information is available at http://www.umbc.edu/
rssipl/people/aplaza
PAPER_TEXT
