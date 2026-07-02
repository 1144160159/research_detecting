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
# [241] Guest Editorial: Special Issue on Graph Learning
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
编号：241
题名：Guest Editorial: Special Issue on Graph Learning
年份：2024
DOI：10.1109/tnnls.2024.3427528
来源：IEEE Transactions on Neural Networks and Learning Systems
PDF：paper/10.1109_TNNLS.2024.3427528.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：无
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\241.txt
- 原始字符数：22661
- 本次发送字符数：22661
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
11630

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 9, SEPTEMBER 2024

Guest Editorial:
Special Issue on Graph Learning

G

RAPH learning represents a dynamic and rapidly
advancing field at the intersection of graph theory (also
known as network science), machine learning, and artificial
intelligence. Its unique ability to model complex relationships
and interactions in a scalable and efficient manner makes
it a cornerstone for scientific and technological advancements across diverse domains. Graph learning techniques
have yielded groundbreaking progress in tackling real-world
challenges, from anomaly detection and recommender systems
to smart surveillance, traffic forecasting, disease control, and
drug discovery. Despite its rapid emergence and successes, the
field faces challenges in areas, such as fundamental theory
and models, algorithms and methods, supporting tools and
platforms, and real-world deployment and engineering.
This Special Issue on graph learning of IEEE
T RANSACTIONS ON N EURAL N ETWORKS AND L EARNING
S YSTEMS aims to capture the cutting-edge research in this
fascinating domain. With over 350 submissions and a rigorous
review process, we present 21 impactful works highlighting
key topics that are pushing the boundaries of graph learning.
We hope that the contributions within will inspire further
innovation and collaboration, propelling the field towards
new and exciting frontiers.

ultimately improving our understanding of complex biological
systems.
GNNs are powerful tools, but they often require a lot
of labeled data for training, which can be expensive and
time-consuming to obtain. In [A3], Ding et al. tackle this
challenge in the context of semi-supervised learning, where
only a small amount of labeled data is available. Existing
methods struggle to capture complex relationships in graphs
with limited labels. The authors propose a novel framework,
augmented graph self-training (AGST), designed to enhance
robustness in low-data contexts by incorporating structural
and semantic augmentation modules. Their evaluations on
semi-supervised node classification tasks highlight AGST’s
superior performance in scenarios with limited labeled data,
showcasing its potential for sustainable graph learning.
Classifying rare data points accurately is a major hurdle in
machine learning, as models often favor the majority class.
In [A4], Ganaie et al. tackle this challenge by proposing
GE-IFRVFL-CIL, a novel model that integrates graph embedding to preserve dataset topology and intuitionistic fuzzy
theory to handle data uncertainty. By incorporating a novel
weighting mechanism, GE-IFRVFL-CIL effectively addresses
class imbalance, demonstrating superior performance on the
Alzheimer’s Disease Neuroimaging Initiative (ADNI) dataset.

A. Graph Learning Foundations and Methodologies
In [A1], Li et al. address the unique challenges posed
by heterophilous graphs. Traditional graph neural network
(GNN) models often struggle with these graphs due to their
inherent differences from homophilous graphs, necessitating
more complex aggregation methods beyond the typical onehop neighborhood. This paper presents an innovative approach
through the development of Haar-type graph framelets, which
are designed with properties such as permutation equivariance,
efficiency, and sparsity to enhance deep learning tasks on
graphs. The authors introduce a graph framelet neural network
model, namely PEGFAN, which utilizes these graph framelets
to achieve superior performance.
In [A2], Zhang and Kabuka propose MARML, a novel
method for learning network representations in complex, layered data (often seen in biological systems). Current methods
struggle to capture interactions between different types of
entities within these multilayer networks. MARML addresses
this by incorporating recurring motif patterns, alongside standard node attributes and network structure information. This
allows the MARML to capture higher order connections across
different hierarchies. The authors demonstrate the effectiveness
of MARML through link prediction and differentiation tasks,
Digital Object Identifier 10.1109/TNNLS.2024.3427528

B. Graph Contrastive Learning
In [A5], Niu et al. shed light on limitations of current
methods for hard negative mining in graph contrastive learning
(GCL). While hard negative mining has proven effective
in enhancing contrastive learning on various data types, its
application to graphs has been hindered by issues such as
oversmooth representations and non-independent and identically distributed (non-IID) data characteristics. This paper
proposes an innovative method leveraging collective affinity
information to identify hard negatives effectively in GCL.
By integrating uncertainty measures into the loss functions,
the approach enhances the discriminative power of learned
graph representations, yielding substantial improvements in
graph and node classification tasks across diverse datasets.
Knowledge graphs (KGs) are never complete. In [A6],
Zeng et al. address critical challenges in enhancing the
completeness of KGs through alignment techniques. Previous methods often focus solely on entity matching, neglecting relations and relying heavily on labeled data, which is
scarce in practice. This paper introduces a versatile framework combining relation-enhanced active instance selection
and cross-view contrastive learning to simultaneously align
entities and relations under limited supervision. By selecting informative instances guided by relations and leveraging

2162-237X © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 9, SEPTEMBER 2024

cross-view representations, the proposed framework significantly improves alignment performance across various KG
pairs, showcasing its effectiveness in augmenting KG completeness efficiently.
In [A7], Wu et al. introduce MotifCC, a novel GCL
framework for community detection in complex networks.
Traditional community detection methods often focus on
lower order structures, overlooking higher order connectivity
patterns crucial to understanding network dynamics. MotifCC
addresses this gap by leveraging motifs to construct a higher
order network and employing contrastive learning to integrate
diverse node, edge, and structural information effectively.
By enhancing the fusion of higher and lower order features,
MotifCC achieves superior community detection performance,
demonstrated through extensive experiments on real-world
datasets.
C. Graph Neural Networks
In [A8], Liu et al. address crucial challenges in GNNs
when the underlying graph structure is unknown. Recent
methods jointly learn the structure and GNN parameters but
often assume a constant curvature for the embedding space
(Euclidean or hyperbolic), leading to obfuscatory nodes that
are poorly embedded and close to multiple categories. This
paper introduces JSGL, a novel approach that first identifies
and refines Euclidean obfuscatory nodes before refining their
graph topology in hyperbolic space. The experimental results
demonstrate JSGL’s superiority over baseline methods, showcasing its effectiveness in improving GNN performance by
addressing complex embedding space dynamics.
Accurately reconstructing time-varying graph signals is
challenging. Traditional methods relying on smoothness
assumptions and convex optimizations often face limitations
in accurately capturing complex spatio-temporal dependencies.
To address this issue, Castro-Correa et al. [A9] propose a novel
approach using Gegenbauer-based graph convolutional operators. The proposed Gegenbauer-based time GNN (GegenGNN)
enhances reconstruction accuracy through an encoder–decoder
architecture and a dedicated loss function incorporating both
fidelity to ground truth and signal smoothness properties.
Experiments underscore GegenGNN’s efficacy in recovering
time-varying graph signals.
In [A10], Zhang et al. introduce a novel approach for
solving complex optimization problems such as constraint
satisfaction problems and combinatorial optimization
problems. Traditional methods rely on branching heuristics,
which can be problem-specific but complex, or general
but potentially suboptimal. This work bridges the gap by
introducing a solver framework that utilizes GNNs. The
framework achieves competitive results on two NP-hard
problems: the (minimum) dominating-clique problem and the
edge-clique-cover problem.
D. Learning on Temporal, Spatial, and Complex Graphs
Temporal graphs, where connections change over time, are
becoming a popular area of study. While existing methods
achieve good results, they often lack transparency—we cannot

11631

understand how they adapt to new information. This is a major
hurdle in scientific fields where interpretability is crucial.
To address this issue, Peng et al. [A11] propose PiECL, a
novel approach that combines physics-informed algorithms
with continual learning principles to enhance explainability in
temporal graphs. By quantifying data disturbance over time,
PiECL provides transparent insights into the learning process,
crucial for applications in chemistry, biomedicine, and beyond.
The experimental results showcase the potential of PiECL to
advance explainable temporal graph learning across diverse
scientific domains.
Accurate forecasting is crucial for various applications using
geo-distributed sensor networks, such as traffic prediction
or pollution monitoring. Traditional methods struggle with
the multivariate nature of data and spatio-temporal autocorrelation, often leading to suboptimal accuracy. In [A12],
Altieri et al. proposes GAP-LSTM, a novel forecasting method
that integrates graph convolution, attention-based long shortterm memory (LSTM), 2-D convolution, and latent memory states. By synergistically leveraging these techniques,
GAP-LSTM effectively captures complex spatio-temporal
relationships across multiple nodes, thus improving forecasting
accuracy in domains such as traffic, energy, and pollution.
While significant progress has been made in deep graph
networks (DGNs), there is a pressing need to make DGNs
suitable for predictive tasks on dynamic, real-world systems
of interconnected entities. Gravina and Bacciu [A13] provide a
comprehensive survey of recent advancements in learning temporal and spatial information, offering an in-depth overview
of the current state of the art in dynamic graph learning.
In addition, they conduct a rigorous performance comparison
of popular approaches on node- and edge-level tasks, establishing a robust baseline for evaluating new architectures and
methods.
E. Graph Learning for Anomaly Detection and Classification
Identifying anomalies in complex, interconnected data,
such as multivariate time series, is crucial in various fields.
Traditional methods often fall short in capturing nonlinear relationships and pairwise correlations among variables.
In [A14], Zheng et al. propose a novel method, CST-GL, which
leverages a correlation learning module to explicitly capture
these correlations. By developing a spatio-temporal GNN,
CST-GL encodes complex spatial dependencies and longrange temporal patterns using graph convolution networks and
dilated convolutions. Extensive experiments validate CST-GL’s
effectiveness, showcasing its potential for early and accurate
anomaly detection.
With the rise of Internet-of-Things (IoT) devices, efficiently detecting anomalies in their massive data streams
becomes crucial, especially for resource-constrained devices.
Zhou et al. [A15] present RG-GLD, a novel graph learning model that combines GNN with knowledge distillation
to enable lightweight anomaly detection across IoT communication networks. The innovative graph network reconstruction strategy treats data communications as nodes in a
directed graph, facilitating efficient and secure graph representation learning. Utilizing graph attention networks and

11632

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 9, SEPTEMBER 2024

multilayer perceptron techniques, RG-GLD effectively fuses
structural and traffic features for enhanced anomaly detection
in resource-limited IoT environments.
In [A16], Sun et al. tackle the challenge of classifying
multilabel time series data, where data points have multiple
relevant labels and the distribution of these labels is uneven.
Existing methods struggle to capture the complex relationships between labels and address imbalanced data effectively.
This research proposes a novel framework, DGAAE-MT, that
leverages a dynamic graph attention autoencoder to model
label relevance accurately. By employing a dual-sampling
strategy and cooperative training, the framework enhances
classification accuracy across all label frequencies.
F. Graph Learning Applications in Specific Domains
In [A17], Tang et al. deal with the complexities of analyzing electronic health records (EHRs) for precise healthcare
decisions. Traditional federated graph learning methods face
challenges due to the non-IID nature of EHRs, leading to data
imbalance and reduced decision-making effectiveness. The
proposed graph learning framework (called PEARL) addresses
these issues by employing disease diagnostic code attention
and admission record attention to extract patient embeddings. Integrating self-supervised learning within a federated
framework, PEARL enhances disease prediction accuracy.
In addition, a differential privacy scheme ensures data privacy.
Through experiments on real-world datasets, PEARL demonstrates superior performance compared to existing methods.
In the field of drug discovery and material science, creating
new molecules is crucial. Traditional generative models have
focused on either 2-D bonding graphs or 3-D geometries, but
not both simultaneously, limiting their effectiveness. In [A18],
Huang et al. address this gap by proposing JODO, a novel
diffusion model that considers both 2-D and 3-D aspects to
generate complete molecules. Utilizing a diffusion graph transformer, JODO captures the relationships between molecular
graphs and geometries, demonstrating superior performance
in inverse molecule design and molecular graph generation on
the QM9 and GEOM-Drugs datasets.
Inferring answers from multimodal contexts in textbook
question answering (TQA) is not always easy. Traditional
methods focus on intramodal semantics, neglecting the crucial intermodal relationships between text and diagrams.
Zhang et al. [A19] address this challenge by introducing
IMR-HGN, an intermodal relation-aware heterogeneous graph
network that aggregates different modalities while learning
features rather than representing them independently. Experiments demonstrate that IMR-HGN outperforms existing methods, paving the way for more informative TQA systems.
Accurately counting objects in images and videos is a
growing area of research, but background noise can hinder
performance. Guo et al. [A20] propose a novel group and
graph attention network (GGANet) to tackle this challenge.
GGANet leverages an encoder–decoder architecture, integrating a group channel attention (GCA) module and a learnable
graph attention (LGA) module. The GCA module assigns
attention factors to subfeatures, while the LGA module treats
the feature map as a graph, representing diverse features as

vertices and their interactions as edges. This dual-module
approach effectively reduces background noise and improves
counting accuracy.
Recognizing actions from videos using skeletal graphs is
an active area of research, but existing methods require a lot
of labeled data and struggle with missing information such
as absent joints. Huang et al. [A21] present GRA, a novel
approach that addresses these limitations. GRA utilizes selftraining to generate high-quality labels for unlabeled data,
reducing the dependency on large labeled datasets. In addition,
it employs a representation alignment technique to compensate
for missing data points in the skeletal graphs. Evaluations
show that GRA significantly improves action recognition performance, especially in scenarios with limited labeled data and
incomplete skeletal information.
We would like to thank Prof. Yongduan Song, Editor-inChief of IEEE T RANSACTIONS ON N EURAL N ETWORKS
AND L EARNING S YSTEMS , for the opportunity to organize
this Special Issue. We are very grateful to the Editorial
Staff for their support in managing this issue. We also thank
all authors for their submissions and all reviewers for their
diligent work in evaluating these submissions.
F ENG X IA, Guest Editor
School of Computing Technologies
RMIT University
Melbourne, VIC 3000, Australia
e-mail: f.xia@ieee.org
R ENAUD L AMBIOTTE, Guest Editor
Mathematical Institute
University of Oxford
OX2 6GG Oxford, U.K.
e-mail: renaud.lambiotte@maths.ox.ac.uk
N EIL S HAH, Guest Editor
Snap Research
Bellevue, WA 98004 USA
e-mail: nshah@snap.com
H ANGHANG T ONG, Guest Editor
Department of Computer Science
University of Illinois at Urbana–Champaign
Urbana, IL 61801 USA
e-mail: htong@illinois.edu
I RWIN K ING, Guest Editor
Department of Computer Science and Engineering
The Chinese University of Hong Kong
Hong Kong, SAR, China
e-mail: king@cse.cuhk.edu.hk
A PPENDIX : R ELATED A RTICLES
[A1] J. Li, R. Zheng, H. Feng, M. Li, and X. Zhuang, “Permutation
equivariant graph framelets for heterophilous graph learning,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 11634–11648,
Sep. 2024, doi: 10.1109/TNNLS.2024.3370918.

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 9, SEPTEMBER 2024

[A2] D. Zhang and M. R. Kabuka, “MARML: Motif-aware deep representation learning in multilayer networks,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 35, no. 9, pp. 11649–11660, Sep. 2024, doi:
10.1109/TNNLS.2023.3341347.
[A3] K. Ding, E. Nouri, G. Zheng, H. Liu, and R. White, “Toward robust
graph semi-supervised learning against extreme data scarcity,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 11661–11670,
Sep. 2024, doi: 10.1109/TNNLS.2024.3351938.
[A4] M. A. Ganaie, M. Sajid, A. K. Malik, and M. Tanveer, “Graph
embedded intuitionistic fuzzy random vector functional link neural
network for class imbalance learning,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 35, no. 9, pp. 11671–11680, Sep. 2024, doi:
10.1109/TNNLS.2024.3353531.
[A5] C. Niu, G. Pang, and L. Chen, “Affinity uncertainty-based hard
negative mining in graph contrastive learning,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 35, no. 9, pp. 11681–11691, Sep. 2024, doi:
10.1109/TNNLS.2023.3339770.
[A6] W. Zeng, X. Zhao, J. Tang, and C. Fan, “Knowledge graph
alignment under scarce supervision: A general framework with
active cross-view contrastive learning,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 35, no. 9, pp. 11692–11705, Sep. 2024, doi:
10.1109/TNNLS.2023.3321900.
[A7] X. Wu, C.-D. Wang, J.-Q. Lin, W.-D. Xi, and P. S. Yu, “Motif-based
contrastive learning for community detection,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 35, no. 9, pp. 11706–11719, Sep. 2024, doi:
10.1109/TNNLS.2024.3367873.
[A8] Z. Liu et al., “Refining Euclidean obfuscatory nodes helps: A jointspace graph learning method for graph neural networks,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 11720–11733, Sep. 2024,
doi: 10.1109/TNNLS.2024.3405898.
[A9] J. A. Castro-Correa, J. H. Giraldo, M. Badiey, and F. D. Malliaros,
“Gegenbauer graph neural networks for time-varying signal reconstruction,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 9,
pp. 11734–11745, Sep. 2024, doi: :10.1109/TNNLS.2024.3381069.
[A10] C. Zhang, Y. Gao, and J. Nastos, “A graph-neural-network-powered
solver framework for graph optimization problems,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 11746–11760, Sep. 2024,
doi: 10.1109/TNNLS.2024.3397926.
[A11] C. Peng, T. Tang, Q. Yin, X. Bai, S. Lim, and C. C. Aggarwal,
“Physics-informed explainable continual learning on graphs,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 11761–11772,
Sep. 2024, doi: 10.1109/TNNLS.2023.3347453.

11633

[A12] M. Altieri, R. Corizzo, and M. Ceci, “GAP-LSTM: Graph-based autocorrelation preserving networks for geo-distributed forecasting,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 11773–11787,
Sep. 2024, doi: 10.1109/TNNLS.2024.3398441.
[A13] A. Gravina and D. Bacciu, “Deep learning for dynamic
graphs: Models and benchmarks,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 35, no. 9, pp. 11788–11801, Sep. 2024, doi:
10.1109/TNNLS.2024.3379735.
[A14] Y. Zheng et al., “Correlation-aware spatial–temporal graph learning
for multivariate time-series anomaly detection,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 35, no. 9, pp. 11802–11816, Sep. 2024, doi:
10.1109/TNNLS.2023.3325667.
[A15] X. Zhou et al., “Reconstructed graph neural network with
knowledge distillation for lightweight anomaly detection,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 9,
pp. 11817–11828, Sep. 2024, doi: 10.1109/TNNLS.2024.
3389714.
[A16] L. Sun, C. Li, Y. Ren, and Y. Zhang, “A multitask dynamic graph
attention autoencoder for imbalanced multilabel time series classification,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 9,
pp. 11829–11842, Sep. 2024, doi: 10.1109/TNNLS.2024.3369064.
[A17] T. Tang et al., “Personalized federated graph learning on
non-IID electronic health records,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 35, no. 9, pp. 11843–11856, Sep. 2024, doi:
10.1109/TNNLS.2024.3370297.
[A18] H. Huang, L. Sun, B. Du, and W. Lv, “Learning joint 2D & 3D
diffusion models for complete molecule generation,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 11857–11871, Sep. 2024,
doi: 10.1109/TNNLS.2024.3416328.
[A19] S. Zhang, Y. Wu, X. Zhang, Z. Feng, L. Wan, and Z. Zhuang,
“Relation-aware heterogeneous graph network for learning intermodal
semantics in textbook question answering,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 35, no. 9, pp. 11872–11883, Sep. 2024, doi:
10.1109/TNNLS.2024.3385436.
[A20] X. Guo, M. Gao, G. Zou, A. Bruno, A. Chehri, and G. Jeon, “Object
counting via group and graph attention network,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 35, no. 9, pp. 11884–11895, Sep. 2024, doi:
10.1109/TNNLS.2023.3336894.
[A21] K.-H. Huang et al., “GRA: Graph representation alignment for
semi-supervised action recognition,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 35, no. 9, pp. 11896–11905, Sep. 2024, doi:
10.1109/TNNLS.2023.3347593.
PAPER_TEXT
