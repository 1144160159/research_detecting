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
# [513] RAGN: Detecting unknown malicious network traffic using a robust adaptive graph neural network
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
编号：513
题名：RAGN: Detecting unknown malicious network traffic using a robust adaptive graph neural network
年份：2025
DOI：10.1016/j.comnet.2025.111184
来源：Computer Networks
PDF：paper/10.1016_j.comnet.2025.111184.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：无
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\513.txt
- 原始字符数：176182
- 本次发送字符数：140042
- 是否截断：True

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Computer Networks 262 (2025) 111184

Contents lists available at ScienceDirect

Computer Networks
journal homepage: www.elsevier.com/locate/comnet

RAGN: Detecting unknown malicious network traffic using a robust adaptive
graph neural network
Ernest Akpaku a , Jinfu Chen a,b
William Leslie Brown-Acquaye c
a

,∗, Mukhtar Ahmed a

, Francis Kwadzo Agbenyegah c ,

School of Computer Science and Communication Engineering, Jiangsu University, Zhenjiang, China

b Jiangsu Key Laboratory of Security Technology for Industrial Cyberspace, Jiangsu University, 301 Xuefu Road, Zhenjiang, 212013, Jiangsu, China
c Department of Information Technology, Ghana Communication Technology University, Accra, Ghana

ARTICLE

INFO

Keywords:
Network security
Dynamic graph
Network anomalies
Robust graphs
Intrusion defense
Edge attention

ABSTRACT
As network environments evolve, detecting unknown malicious network traffic becomes increasingly challenging due to the dynamic and sophisticated nature of modern cyberattacks. Graph Attention Networks
(GATs) have shown promise in modeling complex network interactions but remain vulnerable to adversarial
attacks that exploit weaknesses in the graph structure. In this work, we propose the Robust Adaptive Graph
Neural Network (RAGN), an enhanced GAT-based framework that introduces adaptive attention mechanisms
to improve detection accuracy and robustness against adversarial manipulations in network traffic graphs.
RAGN iteratively adjusts the graph structure and feature space to suppress adversarial perturbations by
assigning lower attention scores to unreliable edges and refining feature representations based on the feature
smoothness regularization principle. To assess the robustness of the proposed RAGN model and compare it
with baseline models, we introduced an effective dynamic graph attack method known as Semantic-Preserving
Adversarial Node Injection (SPAN). We benchmarked its performance against state-of-the-art graph attack
methods, including DICE, DGA, and RWCS. SPAN incrementally injects small batches of malicious nodes,
refining their edges and features to target both the structural and temporal aspects of dynamic graphs. It
preserves semantic integrity, and generates effective yet imperceptible perturbations, providing a rigorous
test of the resilience of graph neural networks. Experiments conducted on four datasets, demonstrate that
RAGN demonstrates robustness against adversarial, and zero-day attacks. It also demonstrates resilience against
targeted, malicious node injection attacks in dynamic network environments. RAGN demonstrated consistent
robustness, with misclassification rates increasing only marginally (by less than 1.2%) even under significant
dynamic changes.

1. Introduction
The detection of unknown malicious network traffic, especially
in the face of adversarial attacks, presents significant challenges in
modern network environments [1]. As networks grow in scale and
complexity, traditional intrusion detection methods struggle to cope
with dynamic and sophisticated threats, including zero-day attacks and
adversarial manipulations designed to evade detection systems [2].
Modern networks face an escalating wave of sophisticated cyberattacks
that exploit their increasing complexity and dynamic nature. Existing
network attack detection approaches often represent network traffic using Euclidean structures, which fail to capture the intricate correlations
between different traffic flows [3]. Graph-based models, particularly
Graph Attention Networks (GATs) [4], have demonstrated potential in

modeling such complex relationships. By leveraging attention mechanisms [5] to weigh the importance of various connections between
network entities, GATs have achieved notable success in node classification and malicious traffic detection. However, GATs and similar
graph neural networks are inherently vulnerable to adversarial attacks,
where an attacker can manipulate the graph structure or features by
introducing deceptive edges or perturbing node characteristics [6].
Most current methods rely on static graph structures, which fail to
account for the dynamic and time-evolving nature of real-world networks. This static nature limits their adaptability to new threats and
changing environments. Adversarial attacks, such as edge manipulation and feature perturbation, significantly degrade the performance
of graph-based models. Existing approaches lack robust mechanisms
to mitigate these adversarial effects, leaving networks vulnerable. For

∗ Corresponding author.

E-mail address: jinfuchen@ujs.edu.cn (J. Chen).
https://doi.org/10.1016/j.comnet.2025.111184
Received 29 October 2024; Received in revised form 23 February 2025; Accepted 2 March 2025
Available online 10 March 2025
1389-1286/© 2025 Elsevier B.V. All rights are reserved, including those for text and data mining, AI training, and similar technologies.

Computer Networks 262 (2025) 111184

E. Akpaku et al.

Fig. 1. Original graphs can be attacked by the negative edges between nodes 1 and 7 with different labels. The update function of node 1 aggregates more negative information
from nodes 7, 9, 10 than positive information from nodes 2, 3, 4.

instance, in traditional GNNs, as shown in Fig. 1, the aggregation
function in GATs process information from various neighbors for a
given node. This aggregated information can be broadly classified into
two categories: positive and negative edges. Positive edges represent
connections between nodes with similar labels, which are beneficial
for accurately updating the node’s feature representation. In contrast,
negative edges represent connections between nodes with differing
labels, which can introduce noise and hinder the feature update process [7]. Adversarial edge attacks exploit this mechanism by either
adding deceptive positive edges or reducing critical negative edges,
disrupting the balance of aggregated information [8]. This imbalance
diminishes the model’s ability to accurately distinguish between benign
and malicious nodes, ultimately undermining its robustness in dynamic
and adversarial network environments.
These adversarial actions significantly degrade the performance of
GATs, particularly when deployed in dynamic environments [9]. Such
actions can either increase the influence of nodes with similar labels
(positive edges) or decrease the influence of nodes with differing labels
(negative edges), severely degrading the GAT’s performance [7]. In
a network traffic graph, nodes represent entities like IP addresses
or devices, and edges represent traffic flows or connections between
these entities. Malicious actors can simulate traffic between entities
that do not typically communicate, creating false connections in the
graph [10]. This can make benign nodes appear malicious or vice
versa, potentially leading to false positives or negatives in threat detection [11]. Conversely, an attacker might remove existing edges from
the graph. For example, severing connections that signify normal interactions between critical network services could hide ongoing malicious
activities that disrupt these usual patterns. These manipulations aim
to alter the ‘‘view’’ that the GAT has over the network, misleading it
about the true nature of the network’s activity [12]. Second, each node
in a network traffic graph can have features like the number of packets,
types of protocols used, or frequency of connections [13]. Adversarial
attacks might involve an attacker changing these features to mask
malicious traffic as normal or make normal activity appear suspicious,
such as altering the volume of traffic or the frequency of connections
to simulate a denial-of-service attack or to hide such an attack among
regular traffic spikes. These feature modifications can undermine the
effectiveness of GATs, as the attention mechanism within the GAT could
assign incorrect importance to altered nodes, leading to flawed threat
assessments.
Specifically, three problems exist, (1) Static Attention Mechanism:
The original GAT applies a fixed attention mechanism that, while effective in learning from graph data, does not dynamically adapt to changes
in the graph’s structure or node features over time [5]. This could be
less effective in environments where adversarial tactics continuously
evolve. (2) Lack of Iterative Refinement: GAT processes the graph
based on the data available at the time of training, without iterative
adjustments post-deployment unless retrained. This static nature makes

it less suitable for environments where network behavior and threats
evolve dynamically, as is common in cybersecurity [8]. (3) Vulnerability to Adversarial Attacks: While GATs are powerful in weighting
the importance of different nodes, they do not inherently distinguish
between manipulations meant to deceive the attention mechanism and
genuine data variations [7]. This makes them potentially vulnerable to
adversarial attacks targeting their attention mechanisms by mimicking
benign characteristics or subtly altering connections.
To address these limitations, we propose the Robust Adaptive Graph
Network (RAGN), an enhanced GAT-based model that introduces key
innovations aimed at improving both detection accuracy and robustness against adversarial attacks. RAGN iteratively adjusts the graph
structure and node features, leveraging dynamic attention mechanisms
to mitigate the impact of adversarial manipulations. The model is
further strengthened through the application of Laplacian regularization, which enforces feature smoothness across the graph and enhances
resilience against adversarial edge and feature perturbations. Our work
proposes defensive strategies that increase the positive effects and
minimize the negative impacts of neighbor relationships in the network
graph. We note that, in many real-world scenarios, not all nodes will
have labels indicating their nature (benign or malicious), especially
in dynamic networks where new nodes (e.g., devices, IP addresses)
frequently appear. Refining the attention mechanism in GATs to weigh
the importance of a node’s features based on the aggregated information from its neighbors, can help in inferring the labels implicitly. We
also note that GATs, by design, weigh nodes based on their relevance
to a task, but if the input data (graph structure or node features)
is manipulated, the attention mechanism may inaccurately prioritize
malicious nodes or connections [14].
As such, we introduce smooth feature representations across the
graph based on Laplacian regularization to reduce the model’s sensitivity to small changes in the graph structure. Also, we introduce an extra
dynamic score to adjust the attention effects for different edges during
the training procedure in response to perceived anomalies or shifts
in network traffic patterns that could indicate adversarial activities.
We aim to design an improved GAT for malicious network traffic
detection while defending against adversarial attacks based on graph
information. Therefore, the key to our approach is the development of
innovative methods to: Distinguish between different types of neighbor
connections without extensive labeling; and design attention scores that
adaptively enhance the robustness of the network against adversarial
manipulations.
Next, we note, that in network traffic analysis, manipulating legitimate entities is challenging, making malicious node injection a
more practical and stealthy attack strategy. Adversaries exploit the
dynamic nature of network environments by adding malicious nodes
that blend into evolving graph structures, making detection difficult.
The performance of Dynamic Graph Neural Networks (DGNNs) depends
heavily on the graph structure at any given time, and adversaries can
2

Computer Networks 262 (2025) 111184

E. Akpaku et al.

disrupt this by targeting optimal moments for attack using periodic
decision strategies.
To address these challenges, we also introduce the SemanticPreserving Adversarial Node Injection (SPAN) method. SPAN leverages
graph vulnerabilities to inject malicious nodes at critical times, selecting targets based on structural fragility, connecting malicious nodes in
batches, and using smoothing functions to mimic legitimate behaviors.
This approach improves attack efficiency and also minimizes detection
risk. Evaluated on dynamic graph datasets, SPAN outperforms existing
attack methods, demonstrating superior efficiency in degrading DGNN
performance. Thus, SPAN provides a powerful and comprehensive
attack framework for evaluating the resilience of GNN-based detection
models against zero-day threats, dynamic challenges, and adversarial
manipulations. The contributions of our method are summarized as
follows:

several limitations remain when it comes to defending against adversarial attacks and detecting unknown malicious traffic . The detection and
defence against malicious network traffic, especially in the presence of
adversarial attacks remains a major concern.
In recent years, the adoption of graph-based models has gained
significant traction [16], as network traffic data naturally forms a
graph structure where entities such as IP addresses, hosts, and devices communicate over edges representing network flows [13]. GNNs,
particularly Graph Convolutional Networks (GCNs) introduced by Kipf
and Welling (2017), revolutionized the field by efficiently propagating
information across graph structures, enabling better generalization to
traffic patterns. GCNs have been employed to detect anomalies in
network traffic by modeling network entities and their interactions as
nodes and edges, respectively [17]. In [18], the E-GraphSAGE model
was introduced. It leverages the inherent structure of graph-based data
to detect and mitigate network-based cyber attacks by capturing both
edge features and topological information. The E-GraphSAGE algorithm
was extensively evaluated on four recent NIDS benchmark datasets.
The results demonstrated that E-GraphSAGE outperformed state-of-theart methods in key classification metrics, showcasing its potential and
robustness. Unlike traditional GCNs that may focus solely on node features, GCN-ETA [11] also considers the relationships between different
flows, such as shared source and destination hosts. Compared to the
bench-marked baselines in the work, the model improved accuracy
rates, AUC, and F1-scores exceeding 98%, along with the capability
to process over 1300 flows per second. In [10], the authors combined GCN with Multi-Head Self-Attention (MHSA) mechanism. The
model addresses several limitations of existing GCN-based methods,
such as incomplete feature descriptions and inadequate traffic correlation mechanisms. MHSA is integrated into the GCN to assign larger
weights to more important features [19]. This enhanced the model’s
ability to focus on critical aspects of the data, improving detection
stability and efficiency. The model showed an improvement of about
2.4% in accuracy, recall, and F1-measure, and about 2.1% in precision
in comparison with other graph-based models.
Graph Attention Networks (GATs), proposed by Veličković et al. [4],
improved upon GCNs by incorporating an attention mechanism that
allows the model to focus on the most relevant neighbors during
message passing. GATs have shown strong potential in network traffic
classification tasks by giving higher importance to influential neighbors. The framework presented in [20] uses GAT and transformer to
model the dependencies between different time series variables. The
authors introduced a new type of graph convolution called Influence
Propagation convolution is introduced to describe the anomaly information flow between network nodes. The results demonstrates that the
proposed framework outperforms baseline alternative state-of-the-art
methods on multiple benchmark datasets, showcasing its effectiveness
in detecting malicious network traffic intrusions. However, despite
their effectiveness, E-GraphSAGE, GCN-MHSA, GCN-ETA, and the many
other GNN-GAT-GCN-based models [21–24] are limited by their inability to handle heterogeneous and dynamic graph structures, often
leading to suboptimal detection of evolving malicious traffic.
The vulnerability of graph-based models to adversarial attacks has
drawn significant attention in recent research. For instance, GCNs and
GATs has shown to be susceptible to adversarial perturbations when
challenged with attack methods such as Nettack [25], RLS2V [26], and
metattack [27]. Meta-attack involve strategically adding or removing
edges in the graph to degrade model performance. Nettack introduces the unnoticeable perturbations on both structures and features.
RLS2V uses reinforcement learning to generate attacks on GNNs. The
metattack parameterized the graph structure and used the gradient
information to attack GAT. In these attacks, malicious actors introduce
perturbations to the graph structure or node features with the aim of
misleading the model and causing incorrect inferences. Such attacks
can take various forms, such as the addition of adversarial nodes

1. We introduce a dynamic attention mechanism that progressively
increases attention scores for edges in GATs, enabling more effective detection and defence against zero-day malicious traffic.
This mechanism differentiates between benign and adversarial
edges based on the feature smoothness assumption, improving
the model’s ability to detect subtle adversarial manipulations.
2. An iterative refinement process is introduced into the training
phase of GATs, allowing continuous adjustment of both the
graph structure and node features. This process optimizes the allocation of attention scores, progressively prioritizing real edges
over adversarial ones, resulting in enhanced model accuracy and
robustness against various attacks.
3. To further strengthen defence against adversarial edges, we
incorporate an extra attention-scoring component that assigns
lower scores to potentially harmful edges, mitigating their impact on the overall model performance.
4. We extended the scope of graph adversarial attacks to dynamic
graph neural networks (DGNNs) by introducing a novel method,
SPAN (Semantic-Preserving Adversarial Node Injection). SPAN
addresses the limitations of previous approaches that were confined to static graph neural networks, offering an effective and
adaptive strategy for attacking dynamic graph environments.
5. Our experimental results on the CICIDS-2018, CTU-13, USTCTFC2016, UJS-IDS2022 datasets demonstrate that RAGN
achieves superior performance in detecting and classifying malicious network traffic, even under various types of adversarial
attacks, including targeted, dynamic node attacks, and random node and edge attacks. RAGN consistently outperforms
state-of-the-art methods across these diverse attack scenarios,
showcasing its robustness and effectiveness in real-world settings.
The remainder of this paper is organized as follows. Section 2 introduces the existing research related to malicious traffic detection and
graph neural networks. In Section 3, we describe our proposed method,
including the steps establishing the graph structure, and constructing
the RAGN method. Section 4 presents the experimental setup details.
Section 5 presents the results with a comparative analysis through
experiments, evaluating our method against state-of-the-art methods.
The paper concludes with Section 6, which summarizes our findings
and outlines directions for future research.
2. Related studies
Graph-based learning techniques, particularly Graph Neural Networks (GNNs), have gained significant attention in recent years for
network intrusion detection and traffic classification. Among these,
Graph Convolutional Networks (GCNs) and Graph Attention Networks
(GATs) have emerged as powerful tools for modeling network traffic
and detecting malicious activities [15]. However, despite their success,
3

Computer Networks 262 (2025) 111184

E. Akpaku et al.

designed to disrupt the graph’s normal patterns and introduce anomalies. Attackers may tamper with the edges between nodes, altering
the graph’s connectivity either by inserting or removing edges, or by
changing their weights [28]. This manipulation of edges can effectively
disrupt the flow of information across the graph, undermining the
GNN’s ability to learn accurate representations of the data.
In addition to these direct modifications, attackers can also alter
the features associated with individual nodes, effectively changing the
input presented to the GNN and skewing its output towards incorrect
conclusions [29]. More sophisticated structural changes can be implemented, such as the creation of clusters of malicious nodes or the
isolation of certain nodes, which can significantly impact the graph’s
properties and the GNN’s capacity to learn from the graph structure.
These attacks highlight the vulnerability of GNNs to manipulations of
their underlying graph structure and emphasize the need for robust
defence mechanisms to safeguard against such threats.
To address these adversarial challenges, several defence mechanisms have been proposed. In [30], for instance, the authors argued
that future IDS should track how attacks evolve across system layers by
adopting attack graphs to overcome the limitations of current IDS that
are unable to identify unseen attacks and access particular programs
to confirm attacks [31]. An attack graph-based intrusion detection
approach is proposed and a few challenges to the realization of their
proposal are identified [32]. With two use cases, they showcase how
to apply their approach. Overall, a conceptual overview of why and
how attack graphs should be used for the next generation of IDS is
presented. The authors evaluated their proposed approach through two
case studies: attacks on file retrieval, such as Time-of-Check to Time-ofUse (TOCTOU) attacks, and attacks propagated among processes, such
as attacks on Shellshock vulnerabilities. The concept is implemented
in [21] where the GNN-IDS is proposed. In GNN-IDS, an attack graph
and real-time measurement mechanisms that represent static and dynamic attributes of computer networks, respectively, are incorporated
and associated to represent complex computer networks. The authors
demonstrate the robustness of GNN-IDS against adversarial attacks by
evaluating the model’s performance on datasets with added Gaussian
noise, simulating changes in network conditions.
The results show that GNN models produce fewer false positives
than traditional models, indicating their effectiveness in avoiding detection evasions. However, the method is not tested in defending against
targeted and non-targeted attacks, particularly in scenarios where the
graph structure is heavily perturbed. Another method is TCGNN [33]
which transforms network packets into an undirected graph, and then
adopts a two-layer GCN with three different aggregation strategies
(Mean, Attention, and LSTM). Adversarial attacks would need to alter
these multiple features to be effective, which is more complex than
attacking models that rely on a single type of feature. The results show
that TCGNN can identify unknown network packets with an extremely
high accuracy rate over the existing packet-grained traffic classification
methods. EdgeTorrent [23] defends against adversarial attacks by leveraging real-time temporal graph representations, adversarial training,
and a streaming architecture that enables rapid adaptation and detection of anomalies. According to the authors, EdgeTorrent is the first
IDS to perfectly classify the StreamSpot dataset, which includes various
types of network traffic, indicating its robustness against various forms
of adversarial evasion techniques.
Despite these advancements, none of these works focus on the
robustness principle of GAT’s aggregation function. In typical GATs,
the aggregation function collects information from neighboring nodes
to update the feature representation of the central node. Generally, the
information aggregated by GAT can be classified into two categories:
(1) information from neighboring nodes with the same label, which
is beneficial for updating positive edges, and (2) information from
neighboring nodes with different labels, which has a negative impact
on the node’s feature update. In adversarial scenarios, attackers can
manipulate these relationships by adding additional positive edges or

reducing negative edges, thereby disrupting the balance of information
aggregation. This manipulation, as shown in Table 3, can mislead the
model into increasing the influence of harmful neighbors or decreasing
the weight of beneficial ones. Similarly, adversarial feature attacks can
degrade the node’s feature information by tampering with nodes of
the same label, making it harder for the model to distinguish between
benign and malicious entities.
The primary gap in these existing approaches is their inability to dynamically adjust to adversarial changes in both the graph structure and
feature space. Most models employ static attention mechanisms that
cannot distinguish between benign and adversarial edges effectively,
nor can they adjust in real-time to adversarial manipulations [34].
Furthermore, they lack iterative refinement processes that allow the
model to adapt to evolving attack strategies. To address these limitations, RAGN introduces a dynamic attention mechanism that adjusts
edge scores based on both the structure and features of the graph,
coupled with iterative refinement during training. This ensures that
the model can continuously prioritize real edges over adversarial ones
and enhance detection accuracy, even under adversarial conditions
such as zero-day attacks. By incorporating these innovations, RAGN
offers a significant improvement in both detection accuracy and robustness compared to the aforementioned models. In addition, RAGN
also adjusts the influence of both positive and negative neighbors by
applying a dynamic attention mechanism to the edges, based on an extra attention score computed using a feature smoothness regularization
mechanism. This dynamic attention score is generated progressively
and plays a critical role in improving the model’s robustness for detecting and defending against unknown malicious network traffic. Next,
RAGN refines the node features to suppress feature noise, which can be
exploited by attackers to make malicious traffic appear benign. This
step ensures that the model remains effective in identifying hidden
patterns within dynamic and evolving network environments, even in
the presence of adversarial noise. The dynamic attention score is then
applied to the edges, adjusting the importance of connections between
nodes. This score is generated using the adjusted edge weights and
helps mitigate the impact of adversarial attacks. Specifically, RAGN reduces the influence of adversarial edges (malicious traffic connections)
by assigning lower attention to them, while giving higher attention to
reliable, benign connections. This iterative refinement of both the edge
weights and the node features enhances the model’s ability to detect
unknown malicious traffic while remaining robust against adversarial
manipulations.
3. Preliminaries
This section outlines the theoretical motivations, provides a analysis, and delves into the foundational theory of Graph Attention Networks (GAT) that underpin our study.
3.1. Notations
Let  = (, ) be a graph representing the network traffic, with
 being the set of vertices (network entities) and  being the set of
edges (interactions between entities). Each graph can be represented
by the adjacency matrix of the graph 𝐀 ∈ R𝑁×𝑁 where 𝐴𝑖𝑗 indicates
the presence of an interaction from entity 𝑖 to entity 𝑗. Let 𝐗 ∈ R𝑁×𝐷
be the feature matrix, where each row represents the features of an
entity and 𝐷 is the number of features. The label matrix is expressed as
𝐘 ∈ R𝑁×𝐾 where each row represents the labels (benign or malicious)
of an entity and 𝐾 is the number of label categories. For Neighborhood
and Aggregation, we let  (𝑣𝑖 ) be the set of neighbors of entity 𝑣𝑖 ,
representing direct interactions. 𝐀(𝑘) as the 𝑘th power of the adjacency matrix 𝐀, representing 𝑘-hop neighborhood interactions. For the
attention Mechanism, 𝑒𝑖𝑗 represents the attention coefficient between
entities 𝑣𝑖 and 𝑣𝑗 , capturing the importance of one entity’s features to
another. The feature matrix after 𝑙th layer of attention mechanism is
4

Computer Networks 262 (2025) 111184

E. Akpaku et al.

𝐇(𝑙) ∈ R𝑁×𝑀 𝑇 where 𝑀 is the dimension of the output space. For
̃ is the dynamically adjusted adjacency
dynamic Graph Adjustment, 𝐀
matrix, incorporating robustness against adversarial attacks. While 𝑠𝑖𝑗 is
the similarity score between entities 𝑣𝑖 and 𝑣𝑗 , used to update the graph
structure. The perturbation matrix representing adversarial edge additions or deletions is expressed as 𝛥𝐀 for adversarial attacks. Let 𝛥𝐗 be
the perturbation matrix representing adversarial feature modifications.
On optimization and Learning 𝛩 is the set of model parameters to be
learned. (𝛩) is the loss function that depends on the model parameters
𝛩. adv is the adversarial loss component, focusing on robustness. We
consider a semi-supervised node classification problem, where only a
subset of nodes 𝑙 ⊂  are labeled with labels 𝑙 .

Table 1
GAT accuracy on synthetic graphs with varying positive to negative edge ratios.
𝐸1

𝐸2

𝐸1 ∕𝐸2

GAT accuracy (%)

0.01
0.01
0.01
0.01

5,982
10,894
15,504
20,354

5,224
5,770
7,076
5,634

1.22
2.05
2.91
3.99

53.60
81.25
96.37
99.88

This section serves to (1) define the baseline capabilities of GAT,
(2) identify its limitations in dynamic and adversarial settings, (3)
establish the need for enhancements, and (4) lay the groundwork for a
comparative evaluation with the proposed RAGN model. As discussed
in Section 2 (related studies), GATs exhibit limitations that can hinder their effectiveness, particularly under adversarial conditions. For
instance, in Fig. 1, the aggregation function consolidates information
from various neighboring nodes for node 1. This aggregated information can typically be categorized into two types. The first type is the
information from neighbors that share the same label, which aids in
updating the node’s feature information, and these connections are
referred to as positive edges. The second type consists of information
from neighboring nodes with differing labels, which can hinder the
process of updating node features, and these are called negative edges.
Adversarial edge attacks can either introduce more positive edges or
reduce the negative edges, thus affecting the balance between these
two types of aggregated data. Similarly, adversarial feature attacks can
degrade the quality of information from nodes that share the same
label.
To explore these limitations, we conducted empirical analyses using
both synthetic and open datasets, investigating how the ratio of positive
to negative edges (𝐸1 ∕𝐸2 ) influences GAT’s performance. We employed
the Stochastic Block Model (SBM) [35] to generate synthetic graphs,
allowing precise control over intra-class and inter-class connection
probabilities. This control was essential for manipulating the 𝐸1 ∕𝐸2
ratio and observing its impact on GAT’s performance. For graph construction, we created 𝑁 = 1000 nodes, equally divided into two classes
with class 1 representing benign network entities and class 2 representing malicious network entities, for the edge formation intra-class
connection probability (𝑃𝑖 ) is defined as the probability that two nodes
within the same class are connected. Inter-class connection probability
(𝑃𝑖𝑖 ) is also defined as the probability that two nodes from different
classes are connected. By varying 𝑃𝑖 while keeping 𝑃𝑖𝑖 constant, we
manipulated the 𝐸1 ∕𝐸2 ratio to create graphs with different proportions
of positive and negative edges. Specifically, we set 𝑃𝑖𝑖 = 0.01 and
increased 𝑃𝑖 from 0.02 to 0.08. We generated four synthetic graphs
with varying 𝐸1 ∕𝐸2 ratios and evaluated GAT’s performance on each.
For each graph, 10% of the nodes were used for training and another
10% for testing. Table 1 presents the parameters and results for each
synthetic graph.
As observed, when the 𝐸1 ∕𝐸2 ratio is close to 1 (Graph 1), GAT’s
accuracy is around 50%, similar to random guessing. This indicates that
when the number of positive and negative edges is nearly equal, GAT
struggles to make accurate classifications. However, as 𝑃𝑖 increases and
the 𝐸1 ∕𝐸2 ratio rises, GAT’s accuracy improves significantly. In Graph
4, where 𝐸1 ∕𝐸2 ≈ 4, the model achieves near-perfect accuracy.
To validate our findings, we conducted experiments on four network
traffic datasets: CICIDS-2018, CTU-13, USTC-TFC2016. These datasets
inherently possess different 𝐸1 ∕𝐸2 ratios due to the nature of network

𝑢∈ (𝑣)

where 𝜎 is a non-linear activation function;  (𝑣) is the set of neighbors
(𝑘)
of node 𝑣; 𝛼𝑢𝑣
is the attention coefficient for the edge connecting nodes
𝑢 and 𝑣 at layer 𝑘; 𝐖(𝑘) ∈ R𝑑𝑘+1 ×𝑑𝑘 is the learnable weight matrix
for layer 𝑘; 𝐱𝑢(𝑘) ∈ R𝑑𝑘 is the feature vector of node 𝑢 at layer 𝑘. The
(𝑘)
attention coefficient 𝛼𝑢𝑣
determines the relative importance of node 𝑢’s
information to node 𝑣. It is computed using:
(
( [
]))
exp LeakyReLU 𝐚⊤ 𝐖(𝑘) 𝐱𝑢(𝑘) ∥ 𝐖(𝑘) 𝐱𝑣(𝑘)
(𝑘)
𝛼𝑢𝑣
= ∑
(2)
(
( [
])) ,
⊤ 𝐖(𝑘) 𝐱(𝑘) ∥ 𝐖(𝑘) 𝐱(𝑘)
𝑣
𝑤
𝑤∈ (𝑣) exp LeakyReLU 𝐚
where: 𝐚 ∈ R2𝑑𝑘 is a learnable vector that determines the attention
mechanism, ∥ denotes concatenation of feature vectors, and LeakyReLU
introduces non-linearity for better representation of feature interactions. The softmax normalization ensures that the attention scores
(𝑘)
𝛼𝑢𝑣
are non-negative and sum to one for all neighbors of node 𝑣,
ensuring stability. To enhance the model’s expressiveness, GAT employs
multi-head attention, where multiple independent attention mechanisms compute attention scores. The features computed by each attention head are then concatenated to form the final node representation.
At layer 𝑘 + 1, the updated feature of node 𝑣 is:
(
)
∑
𝑀
(𝑘+1)
(𝑘,𝑚) (𝑘,𝑚) (𝑘)
𝐱𝑣
= ∥𝑚=1 𝜎
𝛼𝑢𝑣 𝐖
𝐱𝑢
(3)
𝑢∈ (𝑣)

where 𝑀 is the number of attention heads, ∥ denotes concatenation,
(𝑘,𝑚)
and 𝛼𝑢𝑣
and 𝐖(𝑘,𝑚) are the attention scores and weight matrices for
the 𝑚th head, respectively.
Multi-head attention improves the robustness and generalization
of the model by aggregating information from multiple perspectives,
allowing the model to capture diverse patterns in node relationships.
The learnable parameters of GAT are collectively denoted by 𝛩 =
{𝐖(1) , … , 𝐖(𝐿) , 𝐚}. Given a classification task, the model learns a function 𝑓GAT ∶ R𝑁×𝑑 → R𝑁×𝐶 , where 𝐶 is the number of classes.
The classification probabilities for labeled nodes are predicted using a
cross-entropy loss:
(
)
𝑌𝑣,𝑐 log 𝑓GAT (𝐴, 𝑋)𝑣 [𝑐] ,

𝑃𝑖𝑖

0.02
0.04
0.06
0.08

3.3. Motivation

Graph Attention Networks (GAT) update the features of a node by
aggregating information from its neighbors, using dynamically computed attention scores to assign varying importance to different edges.
This mechanism allows GAT to effectively capture task-specific dependencies in graph structures, even in heterogeneous and noisy environments. In GAT, the updated feature of a node 𝑣 at layer 𝑘+1, denoted as
𝐱𝑣(𝑘+1) , is computed by aggregating information from its neighbors  (𝑣),
(𝑘)
weighted by learned attention scores 𝛼𝑢𝑣
. The operation is expressed as:
(
)
∑
(𝑘) (𝑘) (𝑘)
𝐱𝑣(𝑘+1) = 𝜎
𝛼𝑢𝑣
𝐖 𝐱𝑢
,
(1)

𝐶
∑ ∑

𝑃𝑖

1
2
3
4

GAT enables the model to capture the relative importance of different
edges dynamically, improving its performance on heterogeneous and
noisy graphs. Multi-head attention further enhances robustness and
expressiveness by leveraging multiple perspectives, making GAT highly
effective for graph-based learning tasks.

3.2. Graph Attention Network (GAT)

GAT (𝛩, 𝐴, 𝑋, 𝑌 ) = −

Graph

(4)

𝑣∈𝐿 𝑐=1

where 𝐿 is the set of labeled nodes, 𝑌𝑣,𝑐 is a binary indicator of
whether node 𝑣 belongs to class 𝑐, and 𝑓GAT (𝐴, 𝑋)𝑣 [𝑐] is the predicted
probability of node 𝑣 being in class 𝑐. The attention mechanism in
5

Computer Networks 262 (2025) 111184

E. Akpaku et al.
Table 2
GAT accuracy on real-world datasets with different positive to negative edge ratios.
Dataset

𝐸1

𝐸2

𝐸1 ∕𝐸2

GAT accuracy (%)

CICIDS-2018
CTU-13
USTC-TFC2016

10,687
25,402
30,278

5,986
6,934
3,150

4.10
2.79
9.61

83.97
75.26
96.33

Stability of the attention mechanism. The dynamic attention mechanism
in RAGN plays a crucial role in adapting the model’s focus based on
the evolving structure of the graph. In dynamic environments, such as
adversarial settings, it is essential that the model remains stable under
minor fluctuations in the graph’s topology or node features. Stability
ensures that small perturbations do not cause disproportionate changes
in the model’s outputs, which is crucial for maintaining performance
consistency in the presence of noise or minor data variations.

Table 3
GAT accuracy on CICIDS-2018 under different perturbation rates.
Perturbation rate (%)

𝐸1

𝐸2

𝐸1 ∕𝐸2

GAT accuracy (%)

0
5
10
15
20
25

10,152
10,232
9,864
10,453
10,358
10,862

1,986
2,412
2,840
3,332
3,852
4,240

4.10
3.41
2.92
2.49
2.13
1.95

83.97
80.44
75.61
69.78
59.94
54.78

Proposition 1. The attention coefficients in RAGN are stable under perturbations to node features and graph topology, a crucial property for
maintaining performance in adversarial settings.
(𝑘)
Proof. Consider the attention score 𝛼𝑢𝑣
for a graph edge (𝑢, 𝑣) in the 𝑘th
attention layer, computed as shown in Eq. (3). where 𝑊 is the weight
matrix, ℎ𝑢 and ℎ𝑣 are the feature vectors for nodes 𝑢 and 𝑣, 𝑎 is a shared
attention vector, and 𝑢 denotes the neighbors of node 𝑢. Now, assume
a small perturbation 𝛥ℎ𝑣 is applied to the feature vector ℎ𝑣 . The change
(𝑘)
in 𝛼𝑢𝑣
can be approximated using a first-order Taylor expansion:

interactions they represent. We constructed graphs from these datasets
by representing network entities (e.g., IP addresses, devices) as nodes
and interactions (e.g., communication events) as edges. Classes were
defined based on the labeling of traffic as benign or malicious. Table 2
summarizes the results from these datasets.
The results mirror the trends observed in the synthetic data. Datasets
with higher 𝐸1 ∕𝐸2 ratios, such as USTC-TFC2016, exhibit higher GAT
accuracies. This consistency reinforces the conclusion that the proportion of positive to negative edges is a critical factor influencing GAT’s
performance. We further assessed GAT’s robustness under adversarial
conditions by simulating attacks on the CICIDS-2018 dataset. We manipulated the 𝐸1 ∕𝐸2 ratio by adding edges between nodes of different
classes (increasing 𝐸2 ) and removing edges between nodes of the same
class (decreasing 𝐸1 ). Adversarial perturbations were introduced using
the RWCS (Random Walk Column Sum attack) method [36].
Table 3 shows the effect of increasing perturbation rates on GAT’s
performance. As the perturbation rate increased, the 𝐸1 ∕𝐸2 ratio decreased, and GAT’s accuracy declined significantly. At a 25% perturbation rate, the accuracy dropped to approximately 55%, highlighting
GAT’s vulnerability to adversarial manipulation of the graph structure.
These experiments reveal key limitations of GAT in malicious network traffic detection. First, GAT’s performance is highly sensitive to
the 𝐸1 ∕𝐸2 ratio. A lower ratio, indicative of more negative edges,
leads to substantial degradation in accuracy. Second, GAT’s attention
mechanism does not effectively differentiate between positive (intraclass) and negative (inter-class) edges, resulting in the aggregation
of misleading information from malicious nodes. Third, GAT lacks
mechanisms to assess the reliability of edges, making it susceptible to
adversarial perturbations that alter the graph structure and mislead
the attention mechanism. Our empirical analysis demonstrates that
GAT’s performance in malicious network traffic detection is significantly affected by the proportion of positive to negative edges in the
graph. Adversarial attacks that manipulate the 𝐸1 ∕𝐸2 ratio can severely
degrade the model’s accuracy. The subsequent sections will delve into
the architectural details of RAGN and present empirical evaluations
showcasing its effectiveness compared to traditional GAT models.

(𝑘)
𝛥𝛼𝑢𝑣
≈

(𝑘)
𝜕𝛼𝑢𝑣
𝛥ℎ𝑣
𝜕ℎ𝑣
(𝑘)

The partial derivative

𝜕𝛼𝑢𝑣
𝜕ℎ𝑣

is bounded by the norms of 𝑎 and 𝑊 (𝑘) ,

(𝑘)
ensuring that changes in 𝛼𝑢𝑣
are proportional to and bounded by
‖𝛥ℎ𝑣 ‖. This proves that the attention coefficients remain stable under
small perturbations, as the changes in attention scores are linearly
proportional to the perturbation in node features, preventing large
fluctuations in the model’s output.

Convergence of the dynamic adjustment. For RAGN to be effective, the
iterative process of updating adjacency matrices and node features
must converge to a stable configuration. Convergence ensures that
the model reaches a state where further updates do not significantly
alter its behavior, providing reliability and consistency in predictions.
The iterative process enables the model to gradually refine the graph
structure and focus on the most relevant features, which is particularly
important in adversarial settings.
Proposition 2. The iterative process for updating adjacency matrices and
node features in RAGN converges to a stable state, enhancing the model’s
reliability.

Proof. Consider the iterative update rule for the adjacency matrix 𝐴
with a learning rate 𝜂:
𝐴(𝑡+1) = 𝐴(𝑡) − 𝜂∇𝐴 (𝐴, 𝑋)
where (𝐴, 𝑋) is the loss function that includes a regularization term,
such as Laplacian regularization, that promotes smooth feature transitions across edges. The gradient ∇𝐴 (𝐴, 𝑋) measures the impact of
changes in 𝐴 on the model’s performance.
To prove convergence, we assume that the gradient ∇𝐴 (𝐴, 𝑋) is
Lipschitz continuous, i.e., there exists a constant 𝐿 such that:

3.4. Theoretical analysis

‖∇𝐴 (𝐴1 , 𝑋) − ∇𝐴 (𝐴2 , 𝑋)‖ ≤ 𝐿‖𝐴1 − 𝐴2 ‖
In this section, we delve into the theoretical underpinnings of the
RAGN framework, which builds upon GAT by introducing a dynamic
attention mechanism and a revised adjacency matrix. These mechanisms are designed to address the challenges posed by adversarial
perturbations in graph-structured data, particularly in the context of
network traffic analysis. Our approach incorporates both graph theory
principles and neural network operations on graphs, focusing on the
role of node features, graph topology, and the iterative refinement of
the adjacency matrix to enhance robustness.

This assumption ensures that the sequence {𝐴(𝑡) } is bounded and contractive. By the Banach Fixed-Point Theorem, since the sequence is
contractive, it converges to a fixed point 𝐴∗ , where:
∇𝐴 (𝐴∗ , 𝑋) = 0
Thus, the adjacency matrix 𝐴 converges to a stable configuration 𝐴∗ ,
where further updates do not significantly alter the graph structure, and
the model achieves optimal performance.
6

Computer Networks 262 (2025) 111184

E. Akpaku et al.

Derivation and iterative adjustment of the revised adjacency matrix. The
revised adjacency matrix 𝐴̄ plays a pivotal role in optimizing the graph
structure for adversarial robustness. To address potential adversarial
perturbations in the graph, the adjacency matrix is adjusted iteratively
to reflect the most relevant nodes and edges while minimizing the
influence of irrelevant or malicious changes.
Proposition 3. The revised adjacency matrix 𝐴̄ is adjusted iteratively to
improve robustness to adversarial perturbations.
Derivation: The adjustment of the adjacency matrix is performed
by adding an update term 𝛥𝐴(𝑡) to the original adjacency matrix 𝐴, as
follows:
𝐴̄ (𝑡) = 𝐴 + 𝛥𝐴(𝑡)
At each iteration 𝑡, the update term 𝛥𝐴(𝑡) is computed using the gradient
of the loss function with respect to 𝐴:
𝛥𝐴(𝑡) = 𝛼 ⋅ ∇𝐴 (𝐴, 𝑋)
where 𝛼 is a learning rate. The gradient ∇𝐴 (𝐴, 𝑋) incorporates a Laplacian regularization term that ensures smooth feature transitions across
edges and prevents abrupt changes in graph structure. This iterative
refinement process ensures that the adjacency matrix 𝐴̄ evolves towards
a configuration that maximizes the model’s robustness to adversarial
perturbations while maintaining graph structure integrity.

Fig. 2. RAGN-based malicious traffic detection roadmap.

overall workflow of the proposed RAGN method is illustrated in Fig.
2. RAGN introduces several key innovations. First, it incorporates an
additional attention mechanism that considers edge reliability, assigning higher weights to positive edges and diminishing the influence of
negative ones. Second, it employs an iterative optimization process to
refine the graph structure, reducing 𝐸2 and reinforcing 𝐸1 . It further
encourages connected nodes to have similar feature representations,
aiding in distinguishing between benign and malicious entities.
Initially, standard preprocessing operations such as data segmentation, filtering, and normalization are performed on the raw network
traffic data. This prepares the data for graph construction, where
nodes represent network entities like IP addresses or devices, and
edges represent interactions or traffic flows between these entities.
Each node is initialized with features derived from the network data,
encapsulating essential behavioral characteristics. In traditional GATs,
attention scores are computed based solely on node features and the
labels of neighboring nodes, as noted by Hu et al. [33]. The graph
structure determines the choice of neighbors but does not influence the
adjustment of attention scores. This limitation becomes significant in
the presence of adversarial attacks, where attackers may add negative
edges or remove positive edges to manipulate neighbor aggregation,
thus degrading the model’s performance. To overcome this challenge,
RAGN introduces a dynamic adaptive attention mechanism that recalibrates attention scores in real-time, not only based on node features but
also incorporating changes in the graph structure. By revising the aggregation function and inserting an extra attention score, RAGN effectively
reduces the influence of adversarial edges. Intuitively, this mechanism
assigns smaller attention scores to negative edges by utilizing prior
information and continuous analysis to discern and mitigate the impact
of malicious manipulations. This adjustment is crucial because the
proper attention score is related not only to the structure 𝐴 but also
to the features 𝑋.
Furthermore, RAGN continuously adjusts both the graph structure
and node features to generate this extra attention score, enhancing the
model’s robustness against adversarial attacks. This dynamic adaptation
allows RAGN to remain sensitive to both the contextual relevance and
reliability of node connections, improving its ability to withstand and
respond to sophisticated adversarial strategies that aim to deceive the
attention mechanism. After adjusting the attention mechanisms, RAGN
employs a self-attention aggregation mechanism to synthesize insights
across the network, producing a comprehensive representation that
supports global analysis. This aggregated information is then fed into a
softmax classification layer, which categorizes the network’s condition

Robustness to edge perturbations. Adversarial environments often involve deliberate perturbations, such as the addition or removal of
edges, to mislead the model. Ensuring that RAGN is robust to such
perturbations is essential for maintaining accuracy and reliability under
potential adversarial attacks.
Proposition 4. RAGN is robust to adversarial perturbations such as edge
additions or deletions, ensuring that such modifications have minimal impact
on attention scores and subsequent node classifications.
Proof. When adversarial perturbations modify the graph structure by
adding or deleting edges, the dynamic attention mechanism recalibrates
the attention coefficients 𝛼𝑢𝑣 by adjusting the weights assigned to each
edge. The recalibration rule is given by:
′
𝛼𝑢𝑣
= 𝛼𝑢𝑣 × 𝜎(−𝛽 ⋅ 𝑑(𝑢, 𝑣))

where 𝑑(𝑢, 𝑣) measures the deviation of the edge (𝑢, 𝑣) from its expected
weight, and 𝜎 is a sigmoid function scaled by 𝛽, a parameter that
controls sensitivity to changes. The function 𝑑(𝑢, 𝑣) quantifies the deviation from normal edge patterns, and the sigmoid function ensures that
edges that deviate significantly from the expected structure have their
weights reduced, minimizing their impact on the attention scores. This
recalibration ensures that the attention mechanism remains stable and
resilient to adversarial modifications, as unexpected or deceptive edges
are down-weighted, allowing the model to focus on the most relevant
parts of the graph. In Section 3.3, we present empirical evidence that
supports the theoretical enhancements introduced in RAGN. Our experimental results demonstrate that RAGN outperforms baseline models,
such as GAT, in terms of both adversarial robustness and generalization
to unseen attacks. This alignment between theoretical analysis and
practical improvements underscores the efficacy of our approach in
dynamic and adversarial environments.
3.5. The RAGN framework
To address the limitations of existing Graph Attention Networks in
handling dynamic network environments and sophisticated adversarial
threats, we propose a Robust Adaptive Graph Network (RAGN). This
approach revises the traditional attention mechanisms in GATs to enhance the detection and defence against malicious network traffic. The
7

Computer Networks 262 (2025) 111184

E. Akpaku et al.

Fig. 3. Structure of the robust graph attention network framework.
Note: Schematic diagram of RAGN for a one-step iteration process. During one iteration, structure and feature are modified based on regularization first. Then, the modified
structure is used to revise the attention score and the modified feature is used for nodes’ information aggregation. Finally, the parameters of RAGN are updated based on the
labeled nodes’ loss function and the algorithm enters into the next iteration.

and identifies potential threats based on the overall network state.
Each detected threat triggers a tailored response strategy, ranging from
alerts to automated defensive actions, depending on the severity and
nature of the identified threat. Feedback from these actions is utilized to
continuously refine and update the model, enhancing its effectiveness
and adaptability. Compared to existing methods, RAGN significantly
improves upon traditional GATs by:

The original adjacency matrix 𝐴 is defined such that 𝐴[𝑖][𝑗] = 1 if
there is an edge between nodes 𝑖 and 𝑗, and 𝐴[𝑖][𝑗] = 0 otherwise. This
binary setup, while straightforward, often fails to capture the nuanced
interactions in complex data landscapes, particularly under adversarial
conditions.
To address these challenges, we define an objective function that
incorporates both structural fidelity and feature smoothness:
̄ = ‖𝐴 − 𝐴‖
̄ 2 + 𝛼 ⋅ tr(𝑋̄ 𝑇 𝐿𝑋)
̄
 (𝐴)
𝐹

1. Extending the attention mechanism to adjust scores based on
both node features and graph structure, addressing the limitations where the graph structure previously did not influence
attention adjustments.
2. Introducing an extra attention scoring component specifically
designed to mitigate the effects of adversarial edges by assigning
them lower attention scores.
3. Continuously refining the graph structure and node features to
generate adaptive attention scores that reduce the impact of
adversarial manipulations.

(5)

̄ 2 measures the Frobenius norm, emphasizing minimal
Here, ‖𝐴 − 𝐴‖
𝐹
deviation from the original matrix 𝐴 to maintain structural integrity.
̄ where 𝐿 = 𝐷 − 𝐴̄ is the Laplacian matrix and 𝐷 is
The term tr(𝑋̄ 𝑇 𝐿𝑋),
̄ promotes feature homogeneity among
the diagonal degree matrix of 𝐴,
̄ incorconnected nodes. The formulation of the objective function  (𝐴)
̄ 2 , ensuring minimal deviaporates both the structural fidelity ‖𝐴 − 𝐴‖
𝐹
tion from the observed data, and the feature-based regularization term
̄ The balance between these terms determines the trade𝛼 ⋅ tr(𝑋̄ 𝑇 𝐿𝑋).
off between adhering to the observed network structure and adapting to
new insights derived from node features. The selection of the Frobenius
norm and trace function is theoretically motivated by their properties in matrix analysis, providing a balance between simplicity and
effectiveness in capturing matrix deviations and alignments.
The feature smoothness assumption underlying the Laplacian regularization suggests that connected nodes should exhibit similar features.
̄
This principle is essential in guiding the adaptive adjustments to 𝐴,
ensuring that connections in 𝐴̄ are strengthened between nodes with

Through these enhancements, RAGN provides a more robust and accurate system for detecting and defending against malicious network
traffic, effectively addressing the challenges posed by dynamic and adversarial network environments. By integrating these innovative mechanisms, RAGN sets a new standard in network security technologies,
offering a resilient and adaptable approach to safeguarding complex
network infrastructures against evolving cyber threats. In Fig. 3, we
show the schematic diagram of RAGN for a one-step iteration process.
During one iteration, structure and feature are modified based on
regularization first. Then, the modified structure is used to revise the
attention score and the modified feature is used for nodes’ information
aggregation. Finally, the revised feature matrix, parameters, and graph
structure are updated based on the labeled nodes’ loss function and the
algorithm enters into the next iteration.

similar features and weakened between those with dissimilar features.
The use of the Laplacian matrix 𝐿 in the objective function to promote
feature smoothness across the graph leverages the Laplacian’s proper̄
ties in capturing the graph’s structure. The quadratic form tr(𝑋̄ 𝑇 𝐿𝑋)
minimizes the difference in features between directly connected nodes,
effectively regularizing the learning process to favor smooth feature
variations along the edges of the graph. This approach is underpinned
by the theory of semi-supervised learning on graphs, where smoothness
is a desired property for label propagation.
The iterative refinement of 𝐴̄ employs a gradient descent algorithm,
̄
where at each step, 𝐴̄ is adjusted to reduce the objective function  (𝐴):

3.6. Graph structure and node feature optimization
The original adjacency matrix 𝐴 in GATs model the graph structure
in a straightforward binary manner, representing the presence or absence of edges. The limitation of this representation is its inability to
capture the strength or quality of connections, particularly critical in
analyzing network traffic, where not all connections contribute equally
to the network’s functionality. This limitation motivates the need for
a matrix 𝐴̄ that reflects the existence of links and also their relevance
based on node features and network dynamics.
To optimize the structure of the graph, we first introduces a revised
̄ which adjusts the original adjacency matrix 𝐴
adjacency matrix 𝐴,
iteratively to enhance the robustness and reliability of GATs. In scenarios involving noise or adversarial attacks, the original graph structure
represented by 𝐴 may not accurately reflect the true underlying relationships among nodes, potentially degrading the model’s performance.

̄
𝐴̄ ← 𝐴̄ − 𝜂∇𝐴̄  (𝐴)

(6)

̄ represents the gradient of the objective function with
Here, ∇𝐴̄  (𝐴)
̄ and 𝜂 is the learning rate, determining the step size in
respect to 𝐴,
the gradient descent. The iterative refinement process using gradient
descent for updating 𝐴̄ and 𝑋̄ is rooted in optimization theory. The
̄ and ∇𝑋̄ are calculated to guide the update steps to
gradients ∇𝐴̄  (𝐴)
ensure each iteration moves towards a local minimum of the objective
function. The use of gradient descent is justified by its effectiveness
in handling large-scale data and its ability to converge to optimal
solutions.
8

Computer Networks 262 (2025) 111184

E. Akpaku et al.

To ensure 𝐴̄ remains a valid adjacency matrix throughout the optimization process, a projection step  (⋅) is applied, which constrains
each element of 𝐴̄ to stay within [0, 1]. Additionally, regularization
parameters like 𝛼 are tuned to balance the trade-off between structural
fidelity and feature smoothness. The projection steps  and  ensure
that the revised matrices stay within feasible bounds, reflecting valid
adjacency and feature representations. These projections are crucial for
maintaining the physical interpretability and computational stability of
the matrices.
In addition to adjusting the graph structure, RAGN iteratively revises the node features to suppress noise introduced by adversarial
attacks. The objective is to ensure that the node features align with the
revised graph structure, thereby improving the overall robustness. The
feature matrix 𝑋 is updated by minimizing the difference between the
̄ while also enforcing
original features 𝑋 and the revised features 𝑋,
feature smoothness using Laplacian regularization. The optimization
problem for feature adjustment is formulated as:
̄ 2 + 𝛾 tr(𝑋̄ 𝑇 𝐿𝑋)
̄ + 𝜆 𝑅𝐴𝐺𝑁 (𝜃, 𝐴,
̄ 𝑋,
̄ 𝑌𝑝 )
𝑋̄ ∗ = arg min ‖𝑋 − 𝑋‖
2
𝑋̄

aggregate node information using static weights, treating all edges
equally during message passing. This approach is limited because it fails
to account for variations in the importance of edges, leaving the model
vulnerable to adversarial attacks that manipulate graph structure or
node features. Adversarial perturbations, such as the addition, deletion,
or modification of edges, distort the graph’s underlying patterns, misleading the model and degrading its predictive accuracy. To overcome
these limitations, we introduce an attention mechanism to dynamically
assign weights to edges, prioritizing meaningful relationships while
suppressing the influence of irrelevant or noisy connections.
The core of the attention mechanism is the computation of edgespecific attention scores, which reflect the relevance of each edge to the
task at hand. For an edge (𝑖, 𝑗) connecting nodes 𝑖 and 𝑗, the attention
score 𝛼𝑖𝑗 is calculated as:
exp(𝑒𝑖𝑗 )
𝛼𝑖𝑗 = ∑
,
(9)
𝑘∈ (𝑖) exp(𝑒𝑖𝑘 )
where 𝑒𝑖𝑗 is the unnormalized attention coefficient, and  (𝑖) denotes
the set of neighbors of node 𝑖. The softmax function ensures that
the attention scores are normalized, making them interpretable and
ensuring that their sum over all neighbors is equal to one.
The unnormalized coefficient 𝑒𝑖𝑗 is computed using a learnable
mechanism that captures both feature similarity and task-specific relationships. Specifically:
( [
])
𝑒𝑖𝑗 = LeakyReLU 𝑎⊤ 𝑊 𝐹𝑖 ∥ 𝑊 𝐹𝑗 ,
(10)

(7)

where 𝛾 is a non-negative parameter controlling the strength of the
feature regularization, 𝜆 is a hyperparameter balancing the regularization and the loss term, and 𝑅𝐴𝐺𝑁 is the RAGN loss function that
incorporates node classification accuracy on the labeled set 𝑌𝑝 . The
̄ 2 ), minimizes the difference between the original
first term (‖𝑋 − 𝑋‖
2
̄ ensuring the updates are not
features 𝑋 and the updated features 𝑋,
̄ smoothens the features across
too drastic. The second term (tr(𝑋̄ 𝑇 𝐿𝑋)),
connected nodes in the graph. It enforces the idea that nodes linked
by edges should have similar features (a key assumption in graphs).
(𝜆𝐿RAGN ) is the loss function that ensures the updated features help
the model classify nodes (e.g., benign vs. malicious). The features are
updated using gradient descent:

′

where 𝐹𝑖 and 𝐹𝑗 are the feature vectors of nodes 𝑖 and 𝑗, 𝑊 ∈ R𝑑 ×𝑑 is
′
a learnable linear transformation matrix, 𝑎 ∈ R2𝑑 is a learnable vector
that projects concatenated node embeddings into the attention space,
and ∥ denotes concatenation. The LeakyReLU activation introduces
non-linearity, enabling the attention mechanism to model complex
interactions between node features.
The computed attention scores are used to refine the adjacency
matrix. The revised adjacency matrix 𝐴̄ is updated iteratively based on
the following gradient descent rule:
𝜕
𝐴̄ (𝑘+1)
= 𝐴̄ (𝑘)
(11)
𝑖𝑗
𝑖𝑗 − 𝜂 ̄ ,
𝜕 𝐴𝑖𝑗

̄ 2 + 𝛾 tr(𝑋̄ 𝑇 𝐿𝑋)
̄ + 𝜆 𝑅𝐴𝐺𝑁 (𝜃, 𝐴,
̄ 𝑋,
̄ 𝑌𝑝 ))) (8)
𝑋̄ ←  (𝑋̄ − 𝜂2 ∇𝑋̄ (‖𝑋 − 𝑋‖
2
where  (⋅) projects the feature matrix onto the valid domain of
features, and 𝜂2 is the learning rate for the feature update. Together,
these terms balance feature preservation, smoothness, and classification
performance. The weights 𝛾 and 𝜆 control the importance of each
aspect. This step updates node features to align them with the revised
graph structure, making them robust and useful for classification. This
two-step process of iteratively adjusting the graph structure and the
feature matrix allows RAGN to progressively enhance the robustness
of GAT against adversarial attacks. The next step involves dynamically
generating attention scores to further mitigate the impact of adversarial
edges. The next step in the RAGN framework involves generating dynamic attention scores that adjust based on the revised graph structure
̄ This step is critical to mitigating the impact of
𝐴̄ and features 𝑋.
adversarial edges by assigning appropriate weights to both positive and
negative edges during the node aggregation process.
The revision of 𝐴 to 𝐴̄ is based on the hypothesis that nodes with
similar features should have stronger connectivity if they contribute
positively to the task (e.g., classification, clustering). This assumption is
rooted in the homophily principle prevalent in scenarios where similar
nodes tend to be more connected. The theoretical justification for enhancing connections based on feature similarity is further supported by
studies in spectral graph theory, which suggest that closely connected
nodes in a graph’s Laplacian eigenspace tend to share similar features
and labels.

where 𝑘 represents the iteration step, 𝜂 is the learning rate, and 𝜕𝜕
𝐴̄ 𝑖𝑗
is the gradient of the loss function  with respect to 𝐴̄ 𝑖𝑗 . This iterative
process ensures that the adjacency matrix dynamically adapts to capture meaningful relationships while mitigating the effects of adversarial
perturbations.
The dynamic attention mechanism employed in our model is designed to enhance adaptability across various network traffic conditions. Traditional attention mechanisms assign pre-defined weights to
different input features, limiting their effectiveness when dealing with
dynamic and evolving network behaviors. In contrast, our approach
utilizes a self-adaptive weighting strategy that enables the model to
focus on the most relevant traffic characteristics at any given time.
This adaptability is particularly beneficial in network environments
where traffic patterns fluctuate due to varying application demands,
congestion levels, or external factors such as network attacks or hardware failures. The mechanism dynamically adjusts its attention weights
based on both spatial and temporal dependencies, allowing it to generalize effectively across different traffic scenarios. Whether the network
experiences stable, bursty, or periodic traffic, the model can reallocate
its focus to capture critical trends and correlations, ensuring robust
performance across diverse conditions. It does not rely on specific
traffic types or predefined rules. Instead, it learns the underlying structure of network flows from raw input data, making it well-suited for
heterogeneous network environments.
In order to achieve this, the attention mechanism in RAGN is
grounded in two theoretical principles: feature smoothness and structural consistency. Feature smoothness assumes that nodes connected by
meaningful edges have similar feature representations. This principle

3.7. Attention mechanism
In traditional GATs, the attention mechanism calculates attention
coefficients 𝛼𝑢𝑣 between neighboring nodes 𝑢 and 𝑣 based solely on
their features. The attention mechanism in RAGN is designed to address
critical challenges in this traditional graph representation learning, particularly in adversarial and dynamic environments. For instance, GNNs
9

Computer Networks 262 (2025) 111184

E. Akpaku et al.

is enforced through a regularization term that penalizes differences in
features between connected nodes:
∑
̄ 𝐹) = 1
𝛹 (𝐴,
𝐴̄ ‖𝐹 − 𝐹𝑗 ‖2 ,
(12)
2 𝑖,𝑗 𝑖𝑗 𝑖

3.8. Optimization process of RAGN
The optimization of RAGN involves iteratively updating the graph
structure, node features, and model parameters to ensure robust performance under adversarial attacks. The overall objective function
combines the regularization terms for both graph structure and features, along with the classification loss on the labeled nodes. The
optimization process follows an alternating minimization approach,
where the graph structure and node features are updated first, followed
by the model parameters. The optimization process of RAGN is driven
by minimizing the following objective function:

where 𝐹𝑖 and 𝐹𝑗 are the feature vectors of nodes 𝑖 and 𝑗. Structural
consistency ensures that the revised adjacency matrix 𝐴̄ aligns with
the original graph structure, preventing excessive deviation. This is
achieved by incorporating the graph Laplacian 𝐿 = 𝐷 − 𝐴, where 𝐷
is the degree matrix, into a structural regularization term:
̄ = Tr(𝐴̄ ⊤ 𝐿𝐴).
̄
𝛷(𝐴)

(13)

̄ 𝑋,
̄ 𝜃) = re (𝐴,
̄ 𝑋)
̄ + 𝜆 RAGN (𝜃, 𝐴,
̄ 𝑋,
̄ 𝑌𝑝 )
total (𝐴,

The overall optimization objective combines these regularization terms
with the task-specific loss:
̄ + 𝜆2 𝛹 (𝐴,
̄ 𝐹 ),
total = task + 𝜆1 𝛷(𝐴)

This equation combines two objectives to optimize the RAGN model
̄ 𝑋)
̄ is the regularization loss that enforces smoothness
where re (𝐴,
̄ 𝑋,
̄ 𝑌𝑝 ) is the
in the graph structure and feature matrix. RAGN (𝜃, 𝐴,
classification loss for the labeled nodes 𝑌𝑝 , using the RAGN parameters
𝜃. 𝜆 is a hyperparameter balancing the regularization and classification
̄ 𝑋),
̄ regularizes the graph structure (𝐴)
̄ and the
loss. The term 𝐿re (𝐴,
̄ ensuring they are smooth and resistant to adversarial
node features (𝑋),
attacks. It penalizes large changes to the graph and features unless they
improve robustness. The 𝜆𝐿RAGN term focuses on improving classification accuracy. It trains the model parameters 𝛩 to correctly classify
labeled nodes (𝑌𝑝 ) based on the updated graph structure and features.
The hyperparameter 𝜆 balances the trade-off between robustness and
classification accuracy. This ensures that RAGN learns to simultaneously protect the graph from adversarial attacks and perform accurate
node classification. The regularization loss re is defined as:

(14)

where 𝜆1 and 𝜆2 are trade-off parameters balancing the contributions
of structural consistency and feature smoothness. In adversarial settings, the attention mechanism significantly enhances robustness. By
assigning lower weights to perturbed edges, it reduces the sensitivity
of the graph embeddings to adversarial perturbations. This robustness
is theoretically supported by the bound on the Frobenius norm of the
perturbed adjacency matrix:
‖𝛥𝐴‖𝐹 ≤ 𝜖,

(15)

where 𝜖 represents the adversarial perturbation budget. By reweighting edges dynamically, the mechanism ensures that 𝛥𝐴 has minimal
impact on the model’s performance. Through these properties, the attention mechanism in RAGN provides a robust, and adaptive framework
for learning from graph-structured data, addressing the challenges of
adversarial perturbations, dynamic graphs, and heterogeneous relationships. The mechanism’s ability to selectively prioritize meaningful
edges while mitigating noise makes it a critical component of the RAGN
model.
In RAGN, the attention score is enhanced by incorporating the revised graph structure 𝐴̄ and generating an additional dynamic attention
score 𝛼̄ 𝑢𝑣 for each edge. The revised attention score 𝛼̄ 𝑢𝑣 is computed as:
𝛼̄ 𝑢𝑣 = 𝑎̄𝑢𝑣 ⋅ 𝛼𝑢𝑣

(19)

̄ 𝑋)
̄ = ‖𝐴 − 𝐴‖
̄ 2 + 𝛽 ‖𝑋 − 𝑋‖
̄ 2 + 𝛼 tr(𝑋̄ 𝑇 𝐿𝑋)
̄
re (𝐴,
2
2

(20)

̄ 2 penalizes the difference between the original adjacency
where ‖𝐴− 𝐴‖
2
̄ ‖𝑋 − 𝑋‖
̄ 2 penalizes the difference
matrix 𝐴 and the revised matrix 𝐴.
2
̄
between the original feature matrix 𝑋 and the revised features 𝑋.
̄ is the Laplacian regularization term that enforces smoothness
tr(𝑋̄ 𝑇 𝐿𝑋)
̄ 𝛼 and 𝛽 are hyperparameters controlin the revised feature matrix 𝑋.
ling the influence of these terms. The optimization procedure alternates
̄ the feature matrix 𝑋,
̄ and the
between updating the graph structure 𝐴,
̄
RAGN parameters 𝜃. The first step is to update the adjacency matrix 𝐴,
keeping the feature matrix 𝑋̄ and the RAGN parameters 𝜃 fixed. This is
̄
achieved by minimizing the regularization loss re with respect to 𝐴:

(16)

Here, 𝑎̄𝑢𝑣 is the revised edge weight obtained from the optimization
̄ which reflects the structural adjustments
of the adjacency matrix 𝐴,
made to mitigate adversarial attacks. The goal is to down-weight the
influence of adversarial edges and amplify the importance of positive
edges. Specifically, 𝑎̄𝑢𝑣 is derived from the structure optimization in
Step 1 and is used to adjust the original attention scores 𝛼𝑢𝑣 . The final
attention score used for aggregation is then:
𝛼̄ 𝑢𝑣
𝛼̂ 𝑢𝑣 = ∑
(17)
̄ 𝑣𝑘
𝑘∈ (𝑣) 𝛼

̄ 2 + 𝛼 tr(𝑋̄ 𝑇 𝐿𝑋)
̄
𝐴̄ ∗ = arg min ‖𝐴 − 𝐴‖
2
𝐴̄

(21)

The update is performed using projected gradient descent, ensuring that
𝐴̄ remains a valid adjacency matrix (i.e., all elements between 0 and
1):
̄ 2 + 𝛼 tr(𝑋̄ 𝑇 𝐿𝑋)))
̄
𝐴̄ ←  (𝐴̄ − 𝜂1 ∇𝐴̄ (‖𝐴 − 𝐴‖
2

(22)

where 𝜂1 is the learning rate for the graph structure update, and  (⋅) is
the projection operator ensuring 𝐴̄ ∈ [0, 1]. Next, the feature matrix 𝑋̄
is updated while holding the graph structure 𝐴̄ and RAGN parameters
𝜃 fixed. The optimization problem for the feature matrix is:

This dynamic attention mechanism ensures that edges identified as
adversarial (i.e., negative edges) receive lower attention scores, while
beneficial edges (positive edges) receive higher attention scores. By iterating this process, RAGN progressively increases the ratio of attention
scores for real edges to adversarial edges, thus improving the overall
robustness of the model. The revised aggregation function for node 𝑣
in layer 𝑘 of RAGN becomes:
(
)
∑
(𝑘)
(𝑘) (𝑘−1)
𝐱𝑣 = 𝜎
𝛼̂ 𝑢𝑣 𝑊 𝐱𝑢
(18)

̄ 2 + 𝛾 tr(𝑋̄ 𝑇 𝐿𝑋)
̄ + 𝜆 RAGN (𝜃, 𝐴,
̄ 𝑋,
̄ 𝑌𝑝 )
𝑋̄ ∗ = arg min ‖𝑋 − 𝑋‖
2
𝑋̄

(23)

The feature matrix is updated using gradient descent:
̄ 2 + 𝛾 tr(𝑋̄ 𝑇 𝐿𝑋)
̄ + 𝜆 RAGN (𝜃, 𝐴,
̄ 𝑋,
̄ 𝑌𝑝 ))) (24)
𝑋̄ ←  (𝑋̄ − 𝜂2 ∇𝑋̄ (‖𝑋 − 𝑋‖
2

𝑢∈ (𝑣)

where 𝜂2 is the learning rate for the feature update, and  (⋅) is the projection operator that ensures 𝑋̄ remains a valid feature matrix. Finally,
the RAGN parameters 𝜃 are updated, keeping the revised graph structure 𝐴̄ and the revised feature matrix 𝑋̄ fixed. The RAGN classification
loss RAGN is minimized to optimize the model parameters:

where 𝛼̂ 𝑢𝑣 is the adjusted attention score, 𝑊 (𝑘) is the weight matrix for
layer 𝑘, and 𝐱𝑢(𝑘−1) is the feature vector of node 𝑢 from the previous
layer. This dynamic attention score generation step completes the
RAGN process, allowing the network to adapt to adversarial attacks
by revising both the structure and the attention mechanism, leading
to more robust node embeddings.

̄ 𝑋,
̄ 𝑌𝑝 )
𝜃 ∗ = arg min RAGN (𝜃, 𝐴,
𝜃

10

(25)

Computer Networks 262 (2025) 111184

E. Akpaku et al.

The parameter update is performed using gradient descent:
̄ 𝑋,
̄ 𝑌𝑝 )
𝜃 ← 𝜃 − 𝜂3 ∇𝜃 RAGN (𝜃, 𝐴,

enhancing the model’s ability to detect anomalous or malicious activity.
The revised adjacency matrix highlights the reliable connections while
reducing the influence of misleading, adversarial edges. Once the adjacency matrix has been revised, the next step is to update the feature
matrix. The goal of this step is to ensure that the node features accurately reflect the true behavior of the network traffic while minimizing
the effects of adversarial noise. In the case of network traffic, these
features may include packet-related data, IP addresses, communication
frequency, or other attributes relevant to distinguishing between benign
and malicious entities. The feature refinement process adjusts the node
features to align with the newly revised graph structure, ensuring
that traffic nodes with similar behavior remain closely related in the
feature space, while nodes representing malicious traffic are more
distinctly separated. This step is critical for suppressing any noise or
perturbations introduced by adversarial actors, enabling the model to
more effectively capture meaningful patterns in the data. After refining
the graph structure and features, the model parameters are updated
to optimize its classification performance. The RAGN model learns to
classify nodes (network entities) as either benign or malicious based
on the revised adjacency matrix and updated feature representations.
This involves training the model to recognize patterns of normal and
malicious behavior within the network traffic graph and to generalize
to unknown malicious activity.
During this step, the model adjusts its parameters to minimize
classification errors on the labeled training data, where certain traffic
entities are known to be either benign or malicious. As the model
parameters are optimized, the model becomes increasingly accurate
at detecting malicious traffic, even when the malicious nodes or interactions have been adversarially manipulated to evade detection.
The training process alternates between these three steps – graph
structure adjustment, feature refinement, and parameter optimization
– over several iterations. With each iteration, the graph structure, node
features, and model parameters are refined to improve the model’s
robustness to adversarial attacks and enhance its classification accuracy. The process continues until a convergence criterion is met, such
as when the changes in the graph, features, and parameters between
iterations become negligible, or when a maximum number of iterations
is reached. By iteratively refining both the structure of the network
and the features of the traffic entities, RAGN progressively enhances
its ability to detect unknown malicious traffic. The final model is
robust to sophisticated adversarial attacks, effectively distinguishing
between normal and malicious network traffic even when malicious
actors attempt to manipulate the graph structure or obfuscate their
traffic behavior. This makes RAGN a powerful tool for network security,
enabling the detection of unknown and evolving threats in network
traffic.

(26)

where 𝜂3 is the learning rate for updating the RAGN parameters. The
̄ 𝑋,
̄ and 𝜃 for a
optimization process alternates between updating 𝐴,
fixed number of iterations or until convergence. The alternating updates ensure that the graph structure and feature matrix progressively
improve, making the model more robust to adversarial attacks. At each
iteration, the graph structure is refined to emphasize positive edges
and reduce the influence of adversarial edges. The feature matrix is
adjusted to align with the revised structure, and the RAGN parameters
are optimized to improve node classification accuracy under adversarial
conditions. The convergence of the process is guaranteed as each step
involves minimizing a convex objective with respect to the current
variable (graph structure, features, or parameters), leading to stable
updates at each iteration.
Algorithm 1 The RAGN Algorithm
1: Input: Graph 𝐺 = (𝑉 , 𝐴, 𝑋), Partially labeled nodes 𝑉𝑝 with labels

𝑌𝑝
2: Parameters: Learning rates 𝜂1 , 𝜂2 , 𝜂3 ; Regularization parameters

𝛼, 𝛽, 𝛾, 𝜆; Max iterations 𝑇1 , 𝑇2
̄
3: Output: Optimized parameters 𝜃 ∗ , Revised adjacency matrix 𝐴,
Revised feature matrix 𝑋̄
4: Initialize 𝐴̄ ← 𝐴, 𝑋̄ ← 𝑋, randomly initialize RAGN parameters 𝜃
5: for 𝑖 = 1 to 𝑇1 do
6:
Graph Structure Update:
(
)
̄ 2 + 𝛼 tr(𝑋̄ 𝑇 𝐿𝑋)
̄
7:
Compute gradient: ∇𝐴̄ = ∇𝐴̄ ‖𝐴 − 𝐴‖
( 2
)
8:
Update adjacency matrix: 𝐴̄ ←  𝐴̄ − 𝜂1 ∇𝐴̄
9:
Feature Matrix Update based on gradient:
(
)
̄ 2 + 𝛾 tr(𝑋̄ 𝑇 𝐿𝑋)
̄ + 𝜆 RAGN (𝜃, 𝐴,
̄ 𝑋,
̄ 𝑌𝑝 )
10:
∇𝑋̄ = ∇𝑋̄ ‖𝑋 − 𝑋‖
2
(
)
11:
Update feature matrix: 𝑋̄ ←  𝑋̄ − 𝜂2 ∇𝑋̄
12:
for 𝑗 = 1 to 𝑇2 do
13:
RAGN Parameter Update:
̄ 𝑋,
̄ 𝑌𝑝 )
14:
Compute gradient: ∇𝜃 = ∇𝜃 RAGN (𝜃, 𝐴,
15:
Update parameters: 𝜃 ← 𝜃 − 𝜂3 ∇𝜃
16:
end for
17: end for
̄ and 𝑋̄
18: Return Optimized 𝜃 ∗ , 𝐴,

3.9. Training process of RAGN
The training process of RAGN for detecting unknown malicious network traffic involves an iterative optimization strategy that alternates
between refining the graph structure, updating the node features, and
optimizing the model parameters. This process aims to strengthen the
model’s ability to distinguish between normal and malicious network
traffic, even in the presence of adversarial efforts to obfuscate malicious
behavior. In the context of network traffic detection, the network
is represented as a graph where nodes correspond to traffic entities
(such as IP addresses, network flows, or devices), and edges represent relationships or interactions between them. The adjacency matrix
encodes these connections, while the feature matrix captures relevant
characteristics of the traffic, such as packet size, source and destination
addresses, or timing information. The first step in the training process is
to revise the graph’s adjacency matrix. This is essential for improving
the model’s resilience to adversarial attacks, where malicious entities
may attempt to manipulate the network structure to disguise their
behavior. RAGN adjusts the adjacency matrix by encouraging stronger
connections between nodes that exhibit similar traffic patterns (such as
normal traffic nodes) and weakening connections that may have been
adversarially manipulated to obscure the nature of the malicious nodes.
This adjustment ensures that the connections in the graph better
reflect the true relationships between entities in the network, thereby

3.10. Overview of proposed adversarial attack method
To evaluate the robustness of the proposed RAGN model and baseline state-of-the-art models, we introduce Semantic-Preserving Adversarial Node Injection (SPAN), a novel adversarial attack method specifically tailored for dynamic graph neural networks. Unlike generalpurpose attacks, SPAN ensures that injected perturbations align with
the semantic integrity of network traffic, preserving natural communication behaviors while effectively disrupting graph structures. This
approach makes the attack not only realistic and domain-relevant but
also effective in exposing model vulnerabilities. Network traffic graphs
are dynamic, evolving over time as 𝐺 = {𝐺0 , 𝐺1 , … , 𝐺𝑇 }, where each
snapshot 𝐺𝑡 = (𝑉𝑡 , 𝐴𝑡 , 𝐹𝑡 ) consists of nodes 𝑉𝑡 (e.g., endpoints or devices), edges 𝐴𝑡 (e.g., communication links), and features 𝐹𝑡 (e.g., traffic
statistics). SPAN operates with the following key objectives:
• Maximizing Model Disruption: SPAN targets vulnerable nodes and
edges to degrade the performance of tasks like node classification
or link prediction.
11

Computer Networks 262 (2025) 111184

E. Akpaku et al.

• Preserving Imperceptibility through semantic alignment: The attack ensures that injected perturbations remain undetected by
anomaly detection systems through semantic alignment.
• Exploiting Temporal and Structural Fragility: By leveraging both
temporal traffic patterns and structural vulnerabilities, SPAN
strategically injects perturbations that align with real-world dynamics.
• Adhering to Budget Constraints: SPAN operates within predefined
limits, such as the number of injected nodes (𝑏), degree budget
(𝑑), and feature range (𝛥𝐹 ), ensuring computational efficiency
and realism.

The graph’s dynamic structure is analyzed across time intervals 𝑇 ,
with the moment of injection 𝐷 = {𝐺𝑇𝑡−2 , 𝐺𝑇𝑡−1 , …} determined by
maximizing structural vulnerability and traffic relevance. The temporal
traffic intensity 𝑔(𝑡) serves as the proportional weight:
traffic(𝑡)
𝑔(𝑡) =
.
(30)
max𝑡 traffic(𝑡)
Injected nodes are strategically connected to nodes in 𝑉𝑡 with high 𝑔(𝑡)
and fragility scores 𝛿𝑣 . Injected edges 𝐸𝑡𝐼 are designed to target nodes
within the 𝑚-hop neighborhood 𝐴𝑚
𝑡 (𝑣) while maintaining realistic communication behaviors. The overall change in the embedding function
due to injected edges is expressed as:
∑
𝛥𝑓𝑚 =
𝑤𝑢,𝑚 ℎ𝑘−1,𝑡
,
(31)
𝑢

The attack involves injecting a set of malicious nodes 𝑉𝑡𝐼 with features
𝐹𝑡𝐼 into 𝐺𝑡 , connecting them to existing nodes 𝑉𝑡 via edges 𝐸𝑡𝐼 . The
resulting perturbed graph 𝐺𝑡′ is represented as:
(
)
( )
𝐴𝑡
𝐸𝑡𝐼
𝐹𝑡
𝐴′𝑡 =
, 𝐹𝑡′ =
.
(27)
𝐼
𝐼
𝑇
(𝐸𝑡 )
𝐴𝑡
𝐹𝑡𝐼

𝑢∈𝐴𝑚
𝑡 (𝑣)

where 𝑤𝑢,𝑚 represents the weights of the affected neighborhood nodes.
By focusing on the temporal traffic patterns and structural fragility of
communication nodes, this method ensures that injected perturbations
align with plausible network behaviors, addressing both structural
disruption and semantic integrity.
During the edge selection phase, the features of malicious nodes
have not been fully determined. Therefore, to maximize the perturbation impact, we focus on maximizing 𝛥𝑓1 , which is expressed as:
∑
∑
′
𝛥𝑓1 =
𝛥𝑤𝑢,1 ℎ0,𝑡
𝑤𝑢,1 ℎ0,𝑡
(32)
𝑢 +
𝑢 ,

[...正文过长，此处由批处理脚本仅做上下文截断；请在结论中说明该限制...]

precision and recall, which
is challenging to achieve in adversarial settings. Additionally, RAGN
demonstrates an exceptionally low False Positive Rate (FPR) of 0.22%
in the original data scenario, with only a slight increase to 0.25% and
0.24% under GraphGAN and SBM attacks, respectively.
Such a robust performance by RAGN not only highlights the model’s
advanced architectural merits but also its practical applicability in
real-world network environments where adaptability and accuracy are
paramount. The ability of RAGN to sustain low false positive rates
across all datasets further asserts its operational efficacy, a crucial
factor for systems deployed in sensitive and critical network infrastructures.

SPAN, a dynamic graph attack we introduced in this study, along with
DICE [44], degattack (DGA) [45], and RWCS [36]. The adversarial
perturbation levels varied from 2% to 25%, aimed at disrupting the
graph structure. The comparative performance, as detailed in Table 5,
illustrates the superior resilience of RAGN across all attack vectors on
the CICIDS-2018 Dataset. Under the DICE attack, all baseline models
exhibited higher misclassification rates as the perturbation ratio increased. However, RAGN consistently outperformed the other models,
maintaining significantly lower misclassification rates at all perturbation levels. For instance, at a 25% perturbation rate, RAGN achieved
a misclassification rate of 7.06%, substantially lower than the next
best model, FedGAT, which recorded 17.02%. This trend was similarly
observed under the DGA attack, where RAGN showcased exceptional
robustness, maintaining a misclassification rate of just 1.16% at 5%
perturbation and 4.88% at 25%, in stark contrast to other models
that approached or exceeded 15%. The RWCS attack further validated
RAGN’s resilience, indicating its capability to effectively counter complex adversarial manipulations. Even at lower perturbation levels of
2%, RAGN recorded the lowest misclassification rate of 1.34%, and
this strong performance was sustained as perturbations increased, with
rates of 3.80% at 20% and 4.40% at 25%. The SPAN attack, targeting

5.3. Detection performance under different adversarial attacks
In this experiment, we evaluated the resilience of the detection
models against four distinct adversarial attack methods. These included
18

Computer Networks 262 (2025) 111184

E. Akpaku et al.
Table 5
Attack performance (misclassification rate) on CICIDS-2018 dataset.
Attack
method

Table 7
Attack performance (misclassification rate) on USTC-TFC2016 dataset.

PTR (%) GCN

GATr

FedGAT EC-GCN TCGNN E-GrSAGE RAGN

DICE

2
5
10
15
20
25

2.05
6.13
10.17
14.10
17.83
21.53

1.98
5.94
9.82
13.56
17.15
20.63

1.89
5.81
9.55
13.03
16.52
19.78

1.94
5.58
9.16
12.42
15.83
18.81

1.84
5.30
8.86
12.05
15.31
18.07

1.81
5.14
8.58
11.43
14.48
17.02

1.22
4.56
5.28
6.10
6.12
7.06

DGA

2
5
10
15
20
25

1.97
5.93
9.50
13.22
16.99
20.64

1.93
5.67
9.19
12.63
16.27
19.63

1.85
5.49
8.86
12.19
15.59
18.72

1.82
5.30
8.58
11.63
14.92
17.65

1.74
5.06
8.27
11.16
14.20
16.65

1.68
4.85
7.95
10.64
13.32
15.59

1.00
1.16
1.88
3.20
3.24
4.88

RWCS

2
5
10
15
20
25

2.12
6.33
10.46
14.59
18.56
22.35

2.06
6.11
10.11
13.97
17.84
21.32

1.97
5.91
9.76
13.34
17.01
20.23

1.90
5.66
9.39
12.78
16.15
19.18

1.81
5.44
9.04
12.09
15.18
17.88

1.73
5.22
8.59
11.47
14.12
16.69

1.34
2.50
2.90
3.72
3.80
4.40

SPAN

2
5
10
15
20
25

2.01
5.98
9.79
13.83
17.95
21.83

1.95
5.71
9.44
13.16
16.88
20.77

1.87
5.55
9.07
12.61
16.17
19.62

1.80
5.40
8.76
12.08
15.31
18.49

1.72
5.12
8.39
11.42
14.38
17.11

1.63
4.88
7.98
10.76
13.30
15.94

1.14
2.12
2.50
3.14
3.40
4.50

Attack
method

Table 6
Attack performance (misclassification rate) on CTU-13 dataset.
Attack
method

PTR (%) GCN

GATr

FedGAT EC-GCN TCGNN E-GrSAGE RAGN

DICE

2
5
10
15
20
25

1.20
3.30
5.36
7.38
9.24
11.10

1.16
3.18
5.14
7.06
8.88
10.60

1.10
3.04
4.98
6.76
8.50
10.08

1.06
2.92
4.76
6.40
8.04
9.50

1.00
2.82
4.58
6.16
7.62
8.84

0.98
2.74
4.38
5.84
7.18
8.16

0.92
2.46
4.08
5.42
6.56
7.50

DGA

2
5
10
15
20
25

1.16
3.18
5.14
7.10
8.94
10.72

1.12
3.06
4.96
6.76
8.52
10.16

1.06
2.96
4.78
6.48
8.08
9.58

1.00
2.84
4.54
6.10
7.58
8.84

0.94
2.70
4.32
5.74
7.04
8.10

0.90
2.58
4.14
5.36
6.48
7.40

0.84
2.36
3.84
4.94
5.96
6.70

RWCS

2
5
10
15
20
25

1.24
3.36
5.42
7.46
9.36
11.24

1.18
3.22
5.20
7.12
8.98
10.66

1.12
3.12
4.96
6.80
8.54
10.00

1.06
2.98
4.72
6.42
8.04
9.26

1.00
2.82
4.50
6.04
7.50
8.48

0.96
2.70
4.24
5.62
6.90
7.80

0.88
2.44
3.94
5.16
6.34
7.12

SPAN

0
5
10
15
20
25

1.18
3.24
5.28
7.36
9.30
11.16

1.14
3.10
5.06
7.02
8.88
10.58

1.08
3.00
4.84
6.70
8.44
9.92

1.02
2.86
4.58
6.32
7.88
9.24

0.96
2.70
4.36
5.88
7.30
8.40

0.92
2.56
4.10
5.46
6.74
7.72

0.86
2.32
3.76
5.04
6.16
6.98

PTR (%) GCN

GATr

FedGAT EC-GCN TCGNN E-GrSAGE RAGN

DICE

2
5
10
15
20
25

1.20
3.75
5.75
8.05
10.35
12.55

1.15
3.37
5.57
7.72
9.87
11.95

1.10
3.25
5.42
7.35
9.35
11.25

1.05
3.17
5.25
7.02
8.80
10.35

1.00
3.05
5.25
6.80
8.275
9.55

0.97
2.95
4.85
6.45
7.70
8.77

0.462
1.3625
2.25
2.95
3.55
3.95

DGA

2
5
10
15
20
25

1.125
3.35
5.625
7.875
10.10
12.30

1.075
3.22
5.40
7.50
9.62
11.62

1.25
3.10
5.20
7.10
9.10
10.85

1.00
3.00
5.00
6.75
8.55
10.02

0.95
2.85
4.75
6.37
7.95
9.125

0.925
2.77
4.57
5.95
7.30
8.35

0.43
1.26
2.13
2.75
3.37
3.76

RWCS

2
5
10
15
20
25

1.25
3.55
5.95
8.75
10.50
12.75

1.20
3.45
5.72
7.85
9.95
12.10

1.15
3.32
5.50
7.52
9.45
11.32

1.07
3.22
5.27
7.10
8.85
10.47

1.25
3.10
5.25
6.65
8.20
9.52

0.95
2.95
4.75
6.15
7.55
8.65

0.45
1.35
2.21
2.85
3.43
3.92

SPAN

2
5
10
15
20
25

1.17
3.50
5.75
8.22
10.45
12.70

1.125
3.35
5.65
7.80
9.90
12.00

1.05
3.25
5.45
7.35
9.35
11.25

1.00
3.10
5.25
6.95
8.75
10.30

0.95
2.97
4.97
6.50
8.25
9.75

0.95
2.85
4.67
6.00
7.37
8.52

0.42
1.31
2.18
2.76
3.37
3.86

outstanding robustness by consistently maintaining lower misclassification rates compared to its counterparts. At a minimal perturbation
rate of 2%, RAGN recorded a misclassification rate of 0.92%, which
remains lower than the other models. As the perturbation rate increased
to 25%, RAGN still outperformed with a rate of 6.56%, while the closest
competitor model, TC-GNN, registered at 7.18%.
Under the DGA attack, the misclassification rates for RAGN started
at an impressively low 0.84% at a 2% perturbation level, gradually
increasing to 5.96% at 25% perturbation. This trend of lower misclassification rates signifies RAGN’s effective handling of complex attack
scenarios. For the RWCS attack, RAGN again demonstrated its effectiveness by starting with a misclassification rate of 0.88% at 2%
perturbation and ending at 6.34% at 25%. This performance is notably
better than the other models, which showed higher susceptibility to
this type of attack. The SPAN attack results further demonstrated the
resilience of RAGN in the dynamic attack environment. At 2% perturbation, RAGN achieved a misclassification rate of 0.86%, escalating only
to 6.98% at the highest perturbation level of 25%. This outperforms
other models by a significant margin, particularly under higher levels
of perturbation.
The evaluation on the USTC-TFC2016 dataset, as summarized in
Table 7, presents a comprehensive assessment of RAGN’s capability to
withstand adversarial conditions when compared to other prominent
models. The assessment was conducted using four different attack
methods: DICE [44], DGA [45], RWCS [36], and SPAN, with perturbation ratios ranging from 2% to 25%. In the context of the DICE
attack, RAGN demonstrated remarkable robustness by maintaining significantly lower misclassification rates across all levels of perturbation.
Notably, at 2% perturbation, the RAGN model achieved a misclassification rate of only 0.462%, and even at the extreme of 25% perturbation,
it upheld a rate of 3.95%, substantially lower than the rates observed
in other models, where misclassification escalated beyond 10%. Under
the DGA attack, RAGN consistently showcased superior performance,
initiating with a misclassification rate of 0.43% at 2% perturbation
and concluding at 3.76% at 25% perturbation. This indicates a resilient performance trend that starkly contrasts with the next best
performing model, E-GSAGE, which concluded at 8.35% at the same
perturbation level. The RWCS attack results further solidified RAGN’s
leading position, starting at 0.45% misclassification at 2% perturbation

dynamic graph structures, posed a considerable challenge; yet, RAGN
demonstrated substantial resilience. Starting from a misclassification
rate of 1.14% at 2% perturbation, RAGN effectively managed the
threat, capping the misclassification rate at 4.50% at the highest perturbation level of 25%. This performance starkly contrasts with other
models, which exhibited higher vulnerabilities under similar attack
conditions.
For the CTU-13 dataset, we further examined the resilience of the
detection models against the same four adversarial attacks as previously
discussed: DICE [44], DGA [45], RWCS [36], and SPAN. The results
depicted in Table 6 clearly illustrate the robust performance of our
RAGN model in comparison to other models across varied levels of
perturbation from 2% to 25%. With the DICE attack, RAGN showed
19

Computer Networks 262 (2025) 111184

E. Akpaku et al.
Table 8
Attack performance (misclassification rate) on UJS-IDS2022 dataset.
Attack
method

PTR (%) GCN

GATr

FedGAT EC-GCN TCGNN E-GrSAGE RAGN

DICE

2
5
10
15
20
25

0.95
2.80
4.50
6.75
8.90
11.00

0.90
2.60
4.35
6.50
8.60
10.75

0.87
2.50
4.20
6.25
8.30
10.50

0.85
2.40
4.05
6.00
8.00
10.25

0.80
2.30
3.95
5.75
7.70
10.00

0.78
2.20
3.85
5.50
7.40
9.75

0.35
1.05
1.78
2.50
3.30
4.00

DGA

2
5
10
15
20
25

0.92
2.65
4.40
6.60
8.75
10.85

0.87
2.55
4.25
6.35
8.45
10.60

0.85
2.45
4.10
6.10
8.15
10.35

0.83
2.35
3.95
5.85
7.85
10.10

0.81
2.25
3.80
5.60
7.55
9.85

0.79
2.15
3.65
5.35
7.25
9.60

0.34
1.00
1.70
2.40
3.20
3.90

RWCS

2
5
10
15
20
25

1.00
3.00
4.95
7.15
9.20
11.25

0.95
2.90
4.80
6.90
8.95
11.00

0.92
2.80
4.65
6.65
8.70
10.75

0.90
2.70
4.50
6.40
8.45
10.50

0.88
2.60
4.35
6.15
8.20
10.25

0.86
2.50
4.20
5.90
7.95
10.00

0.40
1.15
1.90
2.65
3.50
4.25

SPAN

2
5
10
15
20
25

0.97
2.75
4.70
6.85
9.00
11.15

0.92
2.65
4.55
6.60
8.75
10.90

0.90
2.55
4.40
6.35
8.50
10.65

0.88
2.45
4.25
6.10
8.25
10.40

0.86
2.35
4.10
5.85
8.00
10.15

0.84
2.25
3.95
5.60
7.75
9.90

0.38
1.10
1.85
2.60
3.45
4.20

These nodes were initialized with features sampled from the same
distribution as existing nodes in 𝑉𝑡 , ensuring that the new additions
were statistically and semantically consistent with the original dataset.
Simultaneously, existing nodes were removed to mimic device failures
or targeted disruptions.
The removal process followed two strategies: a random selection,
where nodes were chosen uniformly across the graph, and a targeted
selection, where high-degree or high-centrality nodes were prioritized
for removal to amplify the impact on the graph structure. In addition to
node dynamics, edges were also incrementally added and removed. The
newly added edges connected nodes based on the formula of structural
fragility score (see formula (34)), where deg(𝑢) and deg(𝑣) represent
the degrees of the connecting nodes. This scoring mechanism ensured
that newly added edges targeted structurally fragile or underutilized
regions of the graph, thereby introducing meaningful disruptions to its
structure. The edge removal also followed both a random and a targeted
removal approach, which focused on removing connections between
critical nodes or edges with high betweenness centrality to simulate
link disruptions. Temporal consistency was maintained throughout the
experiment to ensure realistic transitions between graph states. Newly
added nodes and edges were integrated into the graph in a manner consistent with the temporal properties of the network, while
removed nodes and edges were excluded dynamically without causing
abrupt disruptions. 10% and 25% perturbations were applied over time
steps of the graph’s total nodes or edges, reflecting gradual network
evolution.
The detection models were then evaluated at each time step on
the evolving graph 𝐺𝑡 without retraining, allowing for an assessment
of its ability to generalize to unseen dynamic changes. The averaged
results over five independent runs are summarized in Fig. 8. On node
perturbation, Figs. 8(c), and 8(d) show the results for the random node
removal approach while Figs. 8(e) and 8(f) show results for targeted
nodes for UJS-IDS2022 and USTC-TFC2016 datasets respectively. The
results present the performance of the detectors across the different
timestamps and at 10% and 25% perturbation rates. The results are
discussed in the following subsections.

and ending at 3.92% at 25%. The consistent low misclassification
rates emphasize RAGN’s effectiveness in neutralizing more complex
adversarial threats. Similarly, for the SPAN attack, RAGN began with
a misclassification rate of 0.42% at 2% perturbation and ended at
3.86% at 25%, maintaining the lowest misclassification rates across all
models. This performance is particularly noteworthy given the dynamic
and sophisticated nature of the SPAN attack, designed to challenge the
adaptability of dynamic graph structures.
For the UJS-IDS2022 dataset, the results illustrated in Table 8 show
that at a 2% perturbation rate, RAGN achieved a misclassification rate
of 0.35%, which is significantly lower than the next best model (EGrSAGE at 0.78%). This trend continues across all perturbation rates,
with RAGN maintaining a lower misclassification rate, culminating
at 4.00% at a 25% perturbation rate, compared to 9.75% for the
least resilient model under the same conditions. These findings shows
the architectural strengths of RAGN, particularly its ability to handle
adversarial modifications more effectively than other tested models.
The lower susceptibility of RAGN to adversarial attacks can be
attributed to its sophisticated integration of node features and dynamic
adaptations to graph structural changes over time. This capability
is crucial for applications in environments where data integrity and
reliability are paramount, such as cybersecurity and network traffic monitoring. The results suggest that further improvements and
optimizations in dynamic graph neural network architectures could
enhance their defense mechanisms against increasingly complex adversarial strategies, thereby bolstering their application in security-critical
systems.

5.4.1. Time-evolving graph node perturbation
For random Node Removal, in the UJS-IDS2022 dataset, at a 10%
perturbation rate, accuracy rates for RAGN are notably higher, maintaining around 95% to 89.6%, and for the USTC-TFC2016 dataset,
RAGN shows similar resilience. At a 25% perturbation rate, RAGN’s
accuracy remains significantly higher than that of baseline models,
staying around 94.6% to 88.6%, as depicted in Figs. 8(c). and 8(d). Under targeted node removal, RAGN demonstrates superior performance
compared to baseline models. In the UJS-IDS2022 dataset, RAGN maintains an accuracy rate of approximately 97.4% to 90.4% at a 10%
perturbation, which only slightly decreases to about 92.9% to 85.9%
at 25% perturbation, as shown in Fig. 8(e). The USTC-TFC2016 dataset
reveals a similar pattern, with RAGN achieving higher accuracy than
the baselines, maintaining 97.4% to 90.4% at 10% perturbation and
around 87.5% to 85% at 25% perturbation, as highlighted in Fig. 8(f).
For node Injection, the scenario of node injection showcases RAGN’s
robustness where, even with new node introductions, it outperforms
baselines significantly. For the UJS-IDS2022 dataset, RAGN maintains
accuracy rates well above 87% at 10% perturbation, and around 94% to
86% at 25% perturbation, as illustrated in Fig. 8(a). The USTC-TFC2016
dataset shows similar trends, where RAGN’s accuracy decreases less
dramatically than that of the baseline models, particularly at higher
perturbation levels, as seen in Fig. 8(b). Across all tests, including
random and targeted node perturbations as well as node injections,
RAGN consistently outperforms baseline models like GCN, GAT, ECGCN, and TC-GNN. RAGN exhibits a more gradual decrease in accuracy
with increasing perturbation rates, demonstrating its robustness and
adaptability. These findings suggest the superiority of RAGN in maintaining high performance under adversarial conditions and indicate
its potential for deployment in critical network environments where
resilience to adversarial attacks is paramount.

5.4. Evaluation in time evolving dynamic environments
This experiment was designed to test the detection models’ adaptability to dynamic graph attacks based on the proposed SPAN attack
method. We used two large-scale proprietary datasets (i.e., the USTCTFC2016 and the UJS-IDS2022 datasets) for this experiment. The experiment began with an unperturbed graph, 𝐺0 = (𝑉0 , 𝐴0 , 𝐹0 ), representing
the baseline network state. At each subsequent time step, the graph
evolved into 𝐺𝑡 = (𝑉𝑡 , 𝐴𝑡 , 𝐹𝑡 ) through structural perturbations and
temporal updates. New nodes were injected into the graph at each time
step, simulating the arrival of devices or endpoints in the network.
20

Computer Networks 262 (2025) 111184

E. Akpaku et al.

Fig. 8. Model performance in different timestamps under different node perturbation rates.

Fig. 9. Model performance at different timestamps under different edge perturbation rates.

reduction, contrasting sharply with the performance dips seen in other
models under the same conditions. This trend continues even under
25% perturbation, where RAGN’s accuracy impressively remains above
85%, as illustrated in Figs. 9(b) and 9(d).
Targeted edge perturbations further demonstrates RAGN’s capabilities in managing strategic disruptions effectively. In the UJS-IDS2022
dataset, despite the aggressive nature of targeted attacks, RAGN’s accuracy only slightly decreases, maintaining a high level of performance
throughout the experiment. This resilience is similarly observed in the
USTC-TFC2016 dataset, where RAGN consistently performs better than
the baseline models, particularly under higher perturbation rates, as
shown in Figs. 9(f) and 9(e). RAGN’s consistent high performance in
both random and targeted edge perturbations highlights its potential
for deployment in critical network environments where robustness
against sophisticated adversarial attacks is paramount.

5.4.2. Time-evolving graph edge perturbation
This experiment evaluated the resilience of the detection models
against edge perturbations across different models revealing distinct
insights into the resilience of RAGN compared to other models when
challenged with the SPAN attack. In the UJS-IDS2022 dataset, RAGN
demonstrates exceptional stability, maintaining high accuracy rates
consistently above 90% across different timestamps at a 10% perturbation rate, and showing minimal performance degradation even as
perturbation increases to 25%. This superior performance is reflected
in both the Edge Injection and Random Edge scenarios, as depicted in
Figs. 9(a) and 9(c), where RAGN significantly outperforms models like
GCN, GAT, and FedGAT.
In the USTC-TFC2016 dataset, RAGN similarly exhibits robust performance, maintaining high accuracy across varying timestamps. At a
10% perturbation rate, RAGN’s accuracy starts high and shows little
21

Computer Networks 262 (2025) 111184

E. Akpaku et al.

Fig. 10. Detection performances under malicious-based node injection and feature generation attack.

This comparative robustness of RAGN may be attributed to its
architectural features or the specific way it processes and integrates
node features, which may provide a buffer against the disruptive effects
of adversarial strategies deployed by dynamic graph attack methods.
Furthermore, models like EC-GCN and EGraphSAGE demonstrate better performance under higher perturbation conditions across different
datasets, suggesting that certain models may have inherent or designedin resistances to specific types of adversarial manipulations used in
SPAN. This resilience could stem from how these models manage node
connectivity and feature integration, which might be less susceptible to
the influence of adversarially injected nodes and their features.

5.5. Malicious node injection attack
In this subsection, we conducted node classification experiments
to assess the effectiveness of the proposed SPAN attack method on
dynamic GNNs. We use RAGN and the baseline models as targets to
evaluate their resilience against malicious node injection at different
perturbation rates. The SPAN method injects malicious nodes at strategically vulnerable times and locations within the network graph to
disrupt traffic analysis. Once the nodes are injected, SPAN generates
adversarial features for these nodes using an optimization function
designed to maximize the disruption to the target model’s normal
operations. By targeting weak points in the network’s structure, SPAN
degrades the performance of systems designed to detect malicious
traffic.
The results in Fig. 10(a) show that for the UJS-IDS2022 dataset,
the accuracy of the baseline models generally decreases from above
80% at a 5% perturbation rate to below 70% at a 25% perturbation
rate. Similar trends are observed across the other datasets, though
the initial and final accuracy levels vary, suggesting that the inherent
characteristics of each dataset – such as the typical patterns of normal
and malicious traffic – affect how susceptible they are to the SPAN
attack.
RAGN, the proposed model in this study, shows relative resilience
compared to the other models. For example, in the UJS-IDS2022
dataset, while other models’ accuracy dips significantly at a 25%
perturbation rate – falling to as low as around 63% – RAGN maintains
over 90%. Similarly, on the USTC-TFC2016 dataset, RAGN’s accuracy
at a 5% perturbation rate begins near 98% and decreases to near 97%
at 25%, which is notably higher than some competing models like
GCN-MHSA and FedGAT which drop to around 65%.

5.6. Targeted label attack
A targeted label attack is defined as a type of adversarial manipulation where the adversary aims to mislead a graph neural network
(GNN) into incorrectly classifying a specific node into a predefined,
erroneous category. This type of attack is more strategic and malicious compared to untargeted attacks because it degrades the overall
performance of the model and also forces specific, deliberate errors
in node classification. In this experiment, we implement the effective
targeted label attack (ETLA) [47] to manipulate graph structures and
test the malicious traffic detection performance of RAGN and the baseline models under this attack condition. The ETLA method launches
attacks by strategically selecting and modifying edges in a graph’s
structure to mislead a graph neural network into classifying a target
node into a specific category. It uses a combination of stratified node
selection, adaptive edge choice strategies, and a temperature-scaled
attack loss function to allocate the attack budget and achieve the
desired misclassification effectively.
22

Computer Networks 262 (2025) 111184

E. Akpaku et al.

Fig. 11. Detection performance under Targeted label attack across Datasets.

From the results in Fig. 11, RAGN maintains an accuracy significantly higher than the baseline models even as the perturbation rate
increases to 25%. For instance, in the UJS-IDS2022 dataset, RAGN
retains an accuracy close to 95% at 25% perturbation, while other
models like TCGNN and FedGAT fall below 60%. Similar trends are
observable in the USTC-TFC2016 dataset, where RAGN outperforms
counterparts with a consistent margin, holding an accuracy above
90%, contrasting sharply with others that drop to near 58%. In more
sensitive datasets like CTU-13 and CICIDS-2018, where adversarial
attacks generally cause a more drastic decline in performance, RAGN
demonstrates its robustness effectively. For example, in the CTU-13
dataset, while the accuracy for models like GraphSAGE and RAGN
dips as perturbations increase, RAGN’s accuracy remains approximately
10% higher than GraphSAGE at a 25% perturbation rate, hovering
around 97% compared to GraphSAGE’s 61%. This pattern repeats in
CICIDS-2018, indicating a strong adaptive capability inherent to RAGN
that mitigates the impact of graph structural changes more efficiently
than other models. The substantial decline in accuracy across baseline
models with increasing perturbation rates highlights the effectiveness
of ETLA’s stratified node selection and adaptive edge choice strategies
in disrupting the graph’s structure. These strategies complicate the task
of accurately classifying nodes for many networks. In contrast, RAGN’s
architecture demonstrates its effectiveness, adaptability, and resilience
in maintaining higher accuracy under similar conditions.

time, CPU utilization, memory consumption, throughput, and accuracy.
The results, as presented in Table 9, demonstrate that the proposed
method maintains computational efficiency while ensuring high accuracy across different network scales. The execution time exhibits a
logarithmic growth pattern as network size increases, confirming that
the method scales efficiently. For smaller networks, such as 100 nodes,
the execution time is 22.60 s, indicating a lightweight and computationally feasible approach. As the network size increases, execution time
rises gradually, reaching 42.62 s for 5000 nodes and 45.83 s for 10,000
nodes. Even for the largest tested network of 100,000 nodes, execution
time remains controlled, ensuring that the method does not impose
excessive processing costs. This trend suggests that the computational
complexity of the method remains manageable, making it suitable for
large-scale applications.
CPU utilization also follows a gradual increase as network size
expands. For 100 nodes, CPU usage is 45.02%, increasing to 80.73%
for 5000 nodes and reaching 92.18% for 10,000 nodes. The observed
increase aligns with expectations, as larger networks require more
processing power. However, the controlled growth ensures that the
approach does not become prohibitively resource-intensive, making
it feasible for real-world deployment. Similarly, memory utilization
follows a predictable increase, starting at 89.54 MB for 100 nodes,
172.07 MB for 5000 nodes, and reaching 189.01 MB for 10,000 nodes.
This controlled growth indicates that while the method demands additional memory as network size increases, it does not introduce severe
memory bottlenecks. Throughput, measured in operations per second,
shows an inverse relationship with execution time. For 100 nodes,
throughput is 44.24 ops/sec, and as network size increases, it declines
slightly to 23.46 ops/sec for 5000 nodes and 21.82 ops/sec for 10,000
nodes. Despite this decline, the results remain well within acceptable

5.7. Scalability analysis
The scalability evaluation of our approach was conducted using
GraphGAN-generated network structures with sizes ranging from 100
to 100,000 nodes. The performance metrics assessed include execution
23

Computer Networks 262 (2025) 111184

E. Akpaku et al.
Table 9
Scalability performance across different network sizes.
Network size

Execution time (s)

CPU utilization (%)

Memory utilization (MB)

Throughput (ops/sec)

Accuracy (%)

100
500
1,000
5,000
10,000

22.60
31.41
34.63
42.62
45.83

45.02
64.47
72.83
80.73
92.18

89.54
121.39
138.77
172.07
189.01

44.24
31.83
28.88
23.46
21.82

98.50
98.38
98.27
98.15
98.03

Table 10
Results of ablation study results.

limits, indicating that the system maintains a high level of efficiency
even at larger scales. The stability of throughput further supports the
scalability of the method, as it does not exhibit significant degradation
that could hinder real-world usability.
Importantly, the accuracy of the method remains consistently high
across all tested network sizes, confirming its robustness in large-scale
scenarios. For 100 nodes, accuracy is 98.50%, and as the network
size increases, accuracy remains relatively stable at 98.27% for 1000
nodes, 98.15% for 5000 nodes, and 98.03% for 10,000 nodes. The
slight variations indicate that even as network complexity grows, the
method maintains strong predictive performance without significant
degradation. This implies that the proposed approach is well-suited for
large-scale network applications. The logarithmic increase in execution
time, coupled with controlled CPU and memory utilization, ensures
that the system can handle increasing network sizes without excessive
computational overhead. Additionally, the stability of throughput and
accuracy further strengthens the feasibility of the method for deployment in real-world scenarios. The findings validate the scalability of
the approach, reinforcing its applicability in large-scale distributed
computing, IoT networks, and high-traffic communication systems.

Ablation type

Dataset

Accuracy
(%)

Misclassification
Rate (%)

Accuracy
(+)

No Dynamic
Attention

CICIDS-2018
CTU-13
USTC-TFC2016
CICIDS-2018
CTU-13
USTC-TFC2016
CICIDS-2018
CTU-13
USTC-TFC2016
CICIDS-2018
CTU-13
USTC-TFC2016

80.5
79.8
82.4
81.1
80.3
83.1
79.2
78.7
81.9
80.7
80.1
82.6

18.2
19.1
16.8
17.5
18.6
15.9
19.4
20.2
17.4
18.0
18.8
16.3

+7.3%
+7.8%
+6.2%
+6.7%
+7.3%
+5.9%
+8.1%
+8.9%
+6.7%
+7.1%
+7.5%
+6.3%

No Feature
Regularization
No Graph Structure
Adjustment
No Extra Edge
Attention

highlighting the importance of distinguishing between benign and adversarial edges. This extra attention mechanism effectively reduces
the impact of adversarial manipulations that attempt to exploit the
model’s reliance on graph edges for node classification. Overall, the full
RAGN model, incorporating all four components, consistently outperformed the ablated versions in terms of both detection accuracy and
robustness to adversarial attacks. The results clearly demonstrate that
the combination of dynamic graph adjustment, feature regularization,
and adaptive attention mechanisms are essential for improving the
model’s performance. Specifically, the RAGN model achieves up to 8%
higher accuracy compared to its ablated counterparts, reinforcing the
effectiveness of the integrated design choices. (See Table 10.)

5.8. Ablation study
The results of the ablation study clearly highlight the contributions
of each component of the RAGN model to its overall robustness and
effectiveness in detecting malicious traffic, particularly in the face of
adversarial attacks. The removal of any one of the four major components – the dynamic attention mechanism, feature regularization,
graph structure adjustment, and extra attention mechanism on edges
– resulted in noticeable declines in performance, both in terms of
accuracy and resilience to adversarial attacks. First, the ablation of the
dynamic attention mechanism resulted in a significant accuracy drop
(approximately 5%–7%) and a corresponding increase in the misclassification rate (by 10%). This confirms that the dynamic recalibration
of attention scores based on real-time graph structure changes is vital
for detecting subtle adversarial modifications to the graph structure.
Without it, the model behaves similarly to static GAT architectures,
which are less capable of adapting to new adversarial tactics.
The removal of feature regularization also led to a performance
drop, with a decline in accuracy by around 4%–6%. The absence of
regularization particularly affected robustness in noisy environments,
where adversarial feature perturbations became more effective. The
increase in the misclassification rate (8%–9%) further supports the
idea that regularization is essential for smoothing out variations between neighboring nodes’ features, making the model more resistant
to feature noise. When the graph structure adjustment component
was removed, the model’s ability to withstand structural perturbations
such as adversarial edge modifications was heavily compromised. The
accuracy dropped by 6%–8%, and the misclassification rate increased
by an average of 9%. This indicates that dynamically updating the
adjacency matrix during training plays a key role in helping the model
recognize and neutralize adversarial edges that could otherwise mislead
the detection system.
The final component, extra attention on the edges, was also shown
to be critical. Its removal caused a drop in accuracy by 5%–7%,
particularly when dealing with adversarial attacks targeting the edges
of the graph. The misclassification rate increased by around 11%,

5.9. Application of RAGN and trade-offs
The Robust Adaptive Graph Network (RAGN) is designed for deployment in environments where the nature of attacks can evolve quickly,
such as enterprise networks, critical infrastructure, and cloud-based
systems. RAGN’s dynamic capabilities make it particularly suitable
for these high-risk settings, where attackers constantly refine their
techniques to evade detection. The model is designed to analyze network traffic by constructing it as a dynamic graph, where entities
like IP addresses, devices, and servers are represented as nodes, and
their interactions (such as data transfers or connection attempts) are
modeled as edges. This approach allows RAGN to capture complex
relationships and dependencies within the network traffic, giving it
a significant advantage over traditional static models. Unlike existing
solutions, RAGN continuously refines both the graph structure and node
features through an iterative process. This enables it to respond effectively to evolving threats, including zero-day attacks and adversarial
manipulations. The iterative attention mechanism dynamically adjusts
the importance of each edge in the graph, allowing RAGN to prioritize
genuine traffic while reducing the influence of adversarial edges. As a
result, the model maintains robustness even when attackers introduce
subtle perturbations intended to deceive the detection system.
RAGN is particularly effective in detecting a wide range of attack
types. For targeted attacks, where adversaries focus on specific nodes,
such as critical servers, RAGN’s dynamic attention mechanism recalibrates the graph to detect these threats, even when attackers attempt
to obscure their activities by modifying traffic patterns. In contrast,
24

Computer Networks 262 (2025) 111184

E. Akpaku et al.

untargeted attacks, such as Distributed Denial of Service (DDoS) attacks, involve overwhelming the network with traffic. RAGN effectively
identifies these large-scale disruptions by analyzing anomalies in the
traffic graph, even when adversaries introduce random perturbations
to evade detection. The model’s robustness extends to random feature
attacks, where an attacker manipulates the characteristics of individual
nodes, such as packet size, connection duration, or protocol type.
RAGN’s use of Laplacian regularization ensures that these feature-level
perturbations are smoothed across the graph, mitigating their impact on
detection accuracy. This ability to filter out random feature noise allows
RAGN to remain highly accurate, even in the presence of adversarial
feature manipulations.
One of RAGN’s key strengths lies in its ability to detect zeroday exploits. These are new, previously unknown vulnerabilities that
attackers exploit before they are patched. RAGN’s iterative refinement
process allows it to detect deviations in network behavior, flagging
novel attack patterns that other models might miss. This adaptability is
crucial for environments where security threats are constantly evolving.
Additionally, RAGN excels in identifying coordinated attacks, such as
brute force and botnet activities, by analyzing repetitive patterns in
the network graph. The model recognizes the repeated connection
attempts typical of brute force attacks, as well as the synchronized
behaviors of botnets, which involve multiple compromised devices
acting in unison. RAGN’s design makes it particularly effective in
dynamic environments, such as cloud-based architectures where nodes
are frequently added or removed. Its ability to adapt in real-time to
changes in the network landscape ensures that it can effectively detect
both emerging and evolving threats. While RAGN’s iterative refinement
process and dynamic attention mechanism introduce a trade-off in
terms of computational complexity, the increased resource consumption is justified in high-risk environments. The iterative refinement
of graph structures and features, coupled with the dynamic attention
mechanism, requires additional computational resources compared to
more traditional models. Another important trade-off is while RAGN
excels in resisting targeted, zero-day attacks, and random attacks, this
adaptability requires a more intricate training process. The iterative
adjustments and attention re-weighting, though highly effective in
enhancing robustness, could pose a challenge in time-sensitive applications or environments with limited computational resources. Therefore,
while RAGN offers superior defense capabilities, organizations must
assess whether their operational environment justifies the increased
complexity and computational demands.
Deploying deep learning-based intrusion detection systems in largescale network environments presents significant privacy challenges,
as data from multiple sources must be processed while ensuring user
confidentiality and system security. In our approach, RAGN constructs
graph-based representations of network traffic, inherently minimizing
exposure to raw packet payloads to mitigate privacy risks. However,
large-scale networks often involve distributed data from various entities, making them vulnerable to data leakage, inference attacks, and
unauthorized access. Future research could explore the integration
of privacy-preserving techniques with RAGN to further enhance security and compliance with privacy regulations. Specifically, incorporating federated learning, data anonymization, differential privacy,
homomorphic encryption, and blockchain-based access control mechanisms could strengthen the privacy protection of RAGN in large-scale
networks.

guided by feature smoothness regularization. These advancements enable RAGN to adapt in real-time to adversarial changes, prioritize reliable connections, and mitigate the impact of adversarial manipulations,
significantly enhancing its robustness and accuracy.
We also proposed the Semantic-Preserving Adversarial Node Injection (SPAN), a benchmark tailored for evaluating the resilience of
dynamic graph neural networks (DGNNs) under adversarial conditions.
By exploiting structural vulnerabilities and leveraging dynamic graph
characteristics, SPAN provides a rigorous evaluation framework for
testing RAGN and other models in realistic attack scenarios.
Our extensive experiments on four real-world datasets – CICIDS2018, CTU-13, USTC-TFC2016, and UJS-IDS2022 – demonstrate that
RAGN consistently outperforms state-of-the-art models such as GCNMHSA, FedGAT, and GATrans across multiple metrics. On UJS-IDS2022,
RAGN achieved a detection accuracy of 98.12% and an F1-score exceeding 97%, while maintaining a false positive rate as low as 0.22%.
These results highlight RAGN’s ability to detect evolving attacks and
adapt to adversarial manipulations. Moreover, RAGN’s performance
improvement is directly tied to its innovations, such as the dynamic
attention mechanism, which enables more effective weighting of edges,
and iterative refinement, which reduces the influence of adversarial
nodes and features. Compared to baseline models that struggle with
feature perturbations or graph structure manipulation, RAGN demonstrates higher resilience and adaptability, achieving significantly lower
misclassification rates even in high-perturbation scenarios. Beyond
malicious traffic detection, RAGN sets a new benchmark for graph
neural networks in high-stakes environments. While our method introduces mechanisms to enhance robustness, future work could explore
hybrid approaches that combine privacy-preserving techniques, realtime streaming architectures, and scalable distributed frameworks to
ensure that intrusion detection remains both effective and practical in
large-scale, high-throughput networks.

6. Conclusion

Acknowledgments

In this study, we introduced the Robust Adaptive Graph Network
(RAGN), a novel framework designed to address critical vulnerabilities
in Graph Attention Networks (GATs) for detecting malicious network
traffic, particularly in dynamic and adversarial environments. RAGN
incorporates key innovations, including a dynamic attention mechanism and iterative refinement of graph structures and node features,

This work was partly supported by the National Natural Science
Foundation of China (NSFC) (Grant nos. 62172194, 62202206 and
U1836116), the Natural Science Foundation of Jiangsu Province, China
(Grant no. BK20220515), the China Postdoctoral Science Foundation
(Grant no. 2021M691310), and Qinglan Project of Jiangsu Province,
China.

CRediT authorship contribution statement
Ernest Akpaku: Writing – review & editing, Writing – original draft,
Visualization, Validation, Methodology, Investigation, Formal analysis,
Data curation, Conceptualization. Jinfu Chen: Writing – review & editing, Supervision, Methodology, Funding acquisition. Mukhtar Ahmed:
Writing – review & editing, Conceptualization. Francis Kwadzo Agbenyegah: Writing – review & editing, Conceptualization. William
Leslie Brown-Acquaye: Writing – review & editing, Conceptualization.
Declaration of competing interest
The authors declare the following financial interests/personal relationships which may be considered as potential competing interests:
Jinfu Chen reports financial support was provided by National Natural
Science Foundation of China. Jinfu Chen reports financial support
was provided by Natural Science Foundation of Jiangsu Province,
China. Jinfu Chen reports financial support was provided by China
Postdoctoral Science Foundation. Jinfu Chen reports financial support
was provided by Qinglan Project of Jiangsu Province, China. If there
are other authors, they declare that they have no known competing
financial interests or personal relationships that could have appeared
to influence the work reported in this paper.

25

Computer Networks 262 (2025) 111184

E. Akpaku et al.

Data availability

[17] Z. Niu, J. Xue, D. Qu, Y. Wang, J. Zheng, H. Zhu, A novel approach based
on adaptive online analysis of encrypted traffic for identifying malware in IIoT,
Inform. Sci. 601 (2022) 162–174, http://dx.doi.org/10.1016/j.ins.2022.04.018,
URL https://www.sciencedirect.com/science/article/pii/S0020025522003565.

Data will be made available on request.

[18] W.W. Lo, S. Layeghy, M. Sarhan, M. Gallagher, M. Portmann, E-GraphSAGE: A
graph neural network based intrusion detection system for IoT, in: NOMS 20222022 IEEE/IFIP Network Operations and Management Symposium, IEEE Press,
2022, pp. 1–9, http://dx.doi.org/10.1109/NOMS54207.2022.9789878.

References
[1] M. Ahmed, J. Chen, E. Akpaku, R.N.A. Sosu, A. Latif, DELM: Deep ensemble
learning model for anomaly detection in malicious network traffic-based adaptive
feature aggregation and network optimization, ACM Trans. Priv. Secur. 27
(4) (2024) http://dx.doi.org/10.1145/3690637, URL https://doi.org/10.1145/
3690637.
[2] W. Wang, Y. Shang, Y. He, Y. Li, J. Liu, BotMark: Automated botnet detection
with hybrid analysis of flow-based and graph-based traffic behaviors, Inform. Sci.
511 (2020) 284–296, http://dx.doi.org/10.1016/j.ins.2019.09.024, URL https:
//www.sciencedirect.com/science/article/pii/S0020025519308758.
[3] L. Zhang, L. Tan, H. Shi, H. Sun, W. Zhang, Malicious traffic classification for IoT
based on graph attention network and long short-term memory network, in: 2023
24st Asia-Pacific Network Operations and Management Symposium, APNOMS,
2023, pp. 54–59.
[4] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, Y. Bengio, Graph
attention networks, 2018, URL https://arxiv.org/abs/1710.10903, arXiv:1710.
10903.
[5] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A.N. Gomez, L.
Kaiser, I. Polosukhin, Attention is all you need, in: Proceedings of the 31st
International Conference on Neural Information Processing Systems, NIPS ’17,
Curran Associates Inc., Red Hook, NY, USA, 2017, pp. 6000–6010.
[6] T. Nandy, R. Md Noor, R. Kolandaisamy, M.Y.I. Idris, S. Bhattacharyya, A review
of security attacks and intrusion detection in the vehicular networks, J. King
Saud Univ. - Comput. Inf. Sci. 36 (2) (2024) 101945, http://dx.doi.org/10.
1016/j.jksuci.2024.101945, URL https://www.sciencedirect.com/science/article/
pii/S131915782400034X.
[7] W. Jin, Y. Ma, X. Liu, X. Tang, S. Wang, J. Tang, Graph structure learning
for robust graph neural networks, in: Proceedings of the 26th ACM SIGKDD
International Conference on Knowledge Discovery & Data Mining, KDD ’20, Association for Computing Machinery, New York, NY, USA, 2020, pp. 66–74, http://
dx.doi.org/10.1145/3394486.3403049, URL https://doi.org/10.1145/3394486.
3403049.
[8] J. Yuan, H. Yu, M. Cao, J. Song, J. Xie, C. Wang, Self-supervised robust
graph neural networks against noisy graphs and noisy labels, Appl. Intell. 53
(21) (2023) 25154–25170, http://dx.doi.org/10.1007/s10489-023-04836-6, URL
https://doi.org/10.1007/s10489-023-04836-6.
[9] Z. Li, F. Yuan, Y. Liu, C. Cao, F. Fang, J. Tan, Heterogeneous graph attention
network for malicious domain detection, in: E. Pimenidis, P. Angelov, C. Jayne,
A. Papaleonidas, M. Aydin (Eds.), Artificial Neural Networks and Machine
Learning – ICANN 2022, Springer Nature Switzerland, Cham, 2022, pp. 506–518.
[10] J. Chen, H. Xie, S. Cai, L. Song, B. Geng, W. Guo, GCN-MHSA: A novel
malicious traffic detection method based on graph convolutional neural network
and multi-head self-attention mechanism, Comput. Secur. 147 (2024) 104083,
http://dx.doi.org/10.1016/j.cose.2024.104083, URL https://www.sciencedirect.
com/science/article/pii/S0167404824003882.
[11] J. Zheng, Z. Zeng, T. Feng, GCN-ETA: High-efficiency encrypted malicious traffic
detection, Secur. Commun. Netw. 2022 (1) (2022) 4274139, http://dx.doi.org/
10.1155/2022/4274139, URL https://onlinelibrary.wiley.com/doi/abs/10.1155/
2022/4274139.
[12] J. Yang, X. Jiang, Y. Lei, W. Liang, Z. Ma, S. Li, MTSecurity: Privacy-preserving
malicious traffic classification using graph neural network and transformer, IEEE
Trans. Netw. Serv. Manag. 21 (3) (2024) 3583–3597, http://dx.doi.org/10.1109/
TNSM.2024.3383851.
[13] F. Zola, L. Segurola-Gil, J. Bruse, M. Galar, R. Orduna-Urrutia, Network traffic analysis through node behaviour classification: A graph-based approach
with temporal dissection and data-level preprocessing, Comput. Secur. 115
(2022) 102632, http://dx.doi.org/10.1016/j.cose.2022.102632, URL https://
www.sciencedirect.com/science/article/pii/S0167404822000311.
[14] S. Chen, B. Lang, H. Liu, Y. Chen, Y. Song, Android malware detection
method based on graph attention networks and deep fusion of multimodal features, Expert Syst. Appl. 237 (2024) 121617, http://dx.doi.org/10.
1016/j.eswa.2023.121617, URL https://www.sciencedirect.com/science/article/
pii/S095741742302119X.
[15] C. Catal, H. Gunduz, A. Ozcan, Malware detection based on graph attention
networks for intelligent transportation systems, Electronics 10 (20) (2021) http:
//dx.doi.org/10.3390/electronics10202534, URL https://www.mdpi.com/20799292/10/20/2534.
[16] X. Han, S. Cui, J. Qin, S. Liu, B. Jiang, C. Dong, Z. Lu, B. Liu, ContraMTD:
An unsupervised malicious network traffic detection method based on contrastive learning, in: Proceedings of the ACM Web Conference 2024, WWW
’24, Association for Computing Machinery, New York, NY, USA, 2024, pp.
1680–1689, http://dx.doi.org/10.1145/3589334.3645479, URL https://doi.org/
10.1145/3589334.3645479.

[19] X. Luo, Y. Li, H. Cheng, L. Yin, AGCN-domain: Detecting malicious domains
with graph convolutional network and attention mechanism, Mathematics 12 (5)
(2024) http://dx.doi.org/10.3390/math12050640, URL https://www.mdpi.com/
2227-7390/12/5/640.
[20] C. Wang, G. Liu, From anomaly detection to classification with graph attention and transformer for multivariate time series, Adv. Eng. Inform. 60
(2024) 102357, http://dx.doi.org/10.1016/j.aei.2024.102357, URL https://www.
sciencedirect.com/science/article/pii/S1474034624000053.
[21] Z. Sun, A.M. Teixeira, S. Toor, GNN-IDS: Graph neural network based intrusion
detection system, in: Proceedings of the 19th International Conference on Availability, Reliability and Security, ARES ’24, Association for Computing Machinery,
New York, NY, USA, 2024, http://dx.doi.org/10.1145/3664476.3664515, URL
https://doi.org/10.1145/3664476.3664515.
[22] R. Abu Bakar, L. De Marinis, F. Cugini, F. Paolucci, FTG-Net-E: A hierarchical
ensemble graph neural network for DDoS attack detection, Comput. Netw. 250
(2024) 110508, http://dx.doi.org/10.1016/j.comnet.2024.110508, URL https://
www.sciencedirect.com/science/article/pii/S1389128624003402.
[23] I.J. King, X. Shu, J. Jang, K. Eykholt, T. Lee, H.H. Huang, EdgeTorrent: Real-time
temporal graph representations for intrusion detection, in: Proceedings of the
26th International Symposium on Research in Attacks, Intrusions and Defenses,
RAID ’23, Association for Computing Machinery, New York, NY, USA, 2023,
pp. 77–91, http://dx.doi.org/10.1145/3607199.3607201, URL https://doi.org/
10.1145/3607199.3607201.
[24] X. Han, S. Liu, J. Liu, B. Jiang, Z. Lu, B. Liu, ECNet: Robust malicious
network traffic detection with multi-view feature and confidence mechanism,
IEEE Trans. Inf. Forensics Secur. 19 (2024) 6871–6885, http://dx.doi.org/10.
1109/TIFS.2024.3426304.
[25] D. Zügner, A. Akbarnejad, S. Günnemann, Adversarial attacks on neural networks for graph data, in: Proceedings of the 24th ACM SIGKDD International
Conference on Knowledge Discovery & Data Mining, KDD ’18, Association for
Computing Machinery, New York, NY, USA, 2018, pp. 2847–2856, http://
dx.doi.org/10.1145/3219819.3220078, URL https://doi.org/10.1145/3219819.
3220078.
[26] H. Dai, H. Li, T. Tian, X. Huang, L. Wang, J. Zhu, L. Song, Adversarial
attack on graph structured data, in: J. Dy, A. Krause (Eds.), Proceedings of
the 35th International Conference on Machine Learning, in: Proceedings of
Machine Learning Research, vol. 80, PMLR, 2018, pp. 1115–1124, URL https:
//proceedings.mlr.press/v80/dai18b.html.
[27] D. Zügner, O. Borchert, A. Akbarnejad, S. Günnemann, Adversarial attacks on
graph neural networks: Perturbations and their patterns, ACM Trans. Knowl.
Discov. Data 14 (5) (2020) http://dx.doi.org/10.1145/3394520, URL https://
doi.org/10.1145/3394520.
[28] X. Yang, S. Ruan, J. Li, Y. Yue, B. Sun, TrafCL: Robust encrypted malicious
traffic detection via contrastive learning, in: Proceedings of the 33rd ACM
International Conference on Information and Knowledge Management, CIKM
’24, Association for Computing Machinery, New York, NY, USA, 2024, pp.
2910–2919, http://dx.doi.org/10.1145/3627673.3679839, URL https://doi.org/
10.1145/3627673.3679839.
[29] L. Zhang, H. Shi, K. Zhang, H. Sun, W. Zhang, GraphMal: A network malicious
traffic identification method based on graph neural network, in: 2023 International Conference on Networking and Network Applications, NaNA, 2023, pp.
262–267, http://dx.doi.org/10.1109/NaNA60121.2023.00051.
[30] F. Capobianco, R. George, K. Huang, T. Jaeger, S. Krishnamurthy, Z. Qian, M.
Payer, P. Yu, Employing attack graphs for intrusion detection, in: Proceedings
of the New Security Paradigms Workshop, NSPW ’19, Association for Computing
Machinery, New York, NY, USA, 2020, pp. 16–30, http://dx.doi.org/10.1145/
3368860.3368862, URL https://doi.org/10.1145/3368860.3368862.
[31] G. Ren, G. Cheng, N. Fu, Accurate encrypted malicious traffic identification via
traffic interaction pattern using graph convolutional network, Appl. Sci. 13 (3)
(2023) http://dx.doi.org/10.3390/app13031483, URL https://www.mdpi.com/
2076-3417/13/3/1483.
[32] Z. Li, X. Cheng, L. Sun, J. Zhang, B. Chen, A hierarchical approach
for advanced persistent threat detection with attention-based graph neural networks, Secur. Commun. Netw. 2021 (1) (2021) 9961342, http://dx.
doi.org/10.1155/2021/9961342, arXiv:https://onlinelibrary.wiley.com/doi/pdf/
10.1155/2021/9961342.
[33] G. Hu, X. Xiao, M. Shen, B. Zhang, X. Yan, Y. Liu, TCGNN: Packet-grained
network traffic classification via graph neural networks, Eng. Appl. Artif. Intell.
123 (2023) 106531, http://dx.doi.org/10.1016/j.engappai.2023.106531, URL
https://www.sciencedirect.com/science/article/pii/S0952197623007157.
26

Computer Networks 262 (2025) 111184

E. Akpaku et al.
[34] S. Zhang, Z. Zhou, D. Li, Y. Zhong, Q. Liu, W. Yang, S. Li, Attributed
heterogeneous graph neural network for malicious domain detection, in: 2021
IEEE 24th International Conference on Computer Supported Cooperative Work
in Design, CSCWD, 2021, pp. 397–403, http://dx.doi.org/10.1109/CSCWD49262.
2021.9437852.
[35] E. Abbe, Community detection and stochastic block models: Recent developments, J. Mach. Learn. Res. 18 (177) (2018) 1–86, URL http://jmlr.org/papers/
v18/16-480.html.
[36] J. Ma, S. Ding, Q. Mei, Towards more practical adversarial attacks on graph
neural networks, in: H. Larochelle, M. Ranzato, R. Hadsell, M. Balcan, H. Lin
(Eds.), Advances in Neural Information Processing Systems, Vol. 33, Curran Associates, Inc., 2020, pp. 4756–4766, URL https://proceedings.neurips.cc/paper_
files/paper/2020/file/32bb90e8976aab5298d5da10fe66f21d-Paper.pdf.
[37] T.N. Kipf, M. Welling, Semi-supervised classification with graph convolutional
networks, 2017, URL https://arxiv.org/abs/1609.02907, arXiv:1609.02907.
[38] M. Wang, L. Yu, D. Zheng, Q. Gan, Y. Gai, Z. Ye, M. Li, J. Zhou, Q. Huang, C. Ma,
Z. Huang, Q. Guo, H. Zhang, H. Lin, J. Zhao, J. Li, A.J. Smola, Z. Zhang, Deep
graph library: Towards efficient and scalable deep learning on graphs, 2019,
CoRR, arXiv:1909.01315, arXiv:1909.01315.
[39] I. Sharafaldin, A.H. Lashkari, A.A. Ghorbani, Toward generating a new intrusion detection dataset and intrusion traffic characterization, in: International
Conference on Information Systems Security and Privacy, 2018, URL https:
//api.semanticscholar.org/CorpusID:4707749.
[40] S. García, M. Grill, J. Stiborek, A. Zunino, An empirical comparison of
botnet detection methods, Comput. Secur. 45 (2014) 100–123, http://dx.doi.
org/10.1016/j.cose.2014.05.011, URL https://www.sciencedirect.com/science/
article/pii/S0167404814000923.
[41] W. Wang, M. Zhu, X. Zeng, X. Ye, Y. Sheng, Malware traffic classification using
convolutional neural network for representation learning, in: 2017 International
Conference on Information Networking, ICOIN, 2017, pp. 712–717, http://dx.
doi.org/10.1109/ICOIN.2017.7899588.
[42] W. Jianping, Q. Guangqiu, W. Chunming, J. Weiwei, J. Jiahe, Federated learning
for network attack detection using attention-based graph neural networks, Sci.
Rep. 14 (1) (2024) 19088.
[43] Z. Diao, G. Xie, X. Wang, R. Ren, X. Meng, G. Zhang, K. Xie, M. Qiao, EC-GCN:
A encrypted traffic classification framework based on multi-scale graph convolution networks, Comput. Netw. 224 (2023) 109614, http://dx.doi.org/10.1016/
j.comnet.2023.109614, URL https://www.sciencedirect.com/science/article/pii/
S1389128623000592.
[44] M. Waniek, T.P. Michalak, T. Rahwan, M. Wooldridge, Hiding individuals and
communities in a social network, Nat. Hum. Behav. 2 (2016) 139–147, URL
https://api.semanticscholar.org/CorpusID:11496208.
[45] Y. Jiang, H. Xia, Adversarial attacks against dynamic graph neural networks via node injection, High- Confid. Comput. 4 (1) (2024) 100185, http:
//dx.doi.org/10.1016/j.hcc.2023.100185, URL https://www.sciencedirect.com/
science/article/pii/S2667295223000831.
[46] H. Wang, J. Wang, J. Wang, M. Zhao, W. Zhang, F. Zhang, X. Xie, M. Guo,
GraphGAN: Graph representation learning with generative adversarial nets, Proc.
the AAAI Conf. Artif. Intell. 32 (1) (2018) http://dx.doi.org/10.1609/aaai.v32i1.
11872, URL https://ojs.aaai.org/index.php/AAAI/article/view/11872.
[47] F. Cao, Q. Chen, H. Ye, An effective targeted label adversarial attack on graph
neural networks by strategically allocating the attack budget, Knowl.-Based
Syst. 293 (2024) 111689, http://dx.doi.org/10.1016/j.knosys.2024.111689, URL
https://www.sciencedirect.com/science/article/pii/S0950705124003241.

Ernest Akpaku holds an M.Phil. in Management Information Systems from the University of Ghana. He is currently
pursuing a Ph.D. in Computer Science and Technology at
the School of Computer Science and Communication Engineering, Jiangsu University, Zhenjiang, China. His research
interests encompass network security, malicious network
traffic detection, vulnerability detection, and deep learning.
Ernest is also a professional member of the Association for
Computing Machinery (ACM).

Jinfu Chen received his Ph.D. degree in Computer Science
and Technology from Huazhong University of Science and
Technology, Wuhan, China, in 2009. He is currently a full
professor at the School of Computer Science and Communication Engineering, Jiangsu University, Zhenjiang, China.
His major research interests include Software Testing, Software Security, and Trusted Software. He has published more
than 80 papers in some famous journals or conferences.

Mukhtar Ahmed received his BSc. degree in Computer
Science from BUITEMS, Pakistan, in 2011, and the MS
degree in Computer Science from ILMA University, Pakistan, in 2021. He is currently pursuing a Ph.D. degree at
the School of Computer Science and Communication Engineering, Jiangsu University, Zhenjiang, China. His research
interests include malicious network detection, network security, deep learning, and cloud security. He is a professional
member of the ACM.

Francis Kwadzo Agbenyegah holds a Ph.D. in Computer
Science from Kwame Nkrumah University of Science and
Technology, Kumasi, Ghana. He is currently pursuing a
Ph.D. in Computer Science and Technology at the School of
Computer Science and Communication Engineering, Jiangsu
University, Zhenjiang, China. His research interests include
software vulnerability prediction and detection, machine
learning, and deep learning. Francis is also a member of
the Internet Society.

William Leslie Brown-Acquaye is a Senior Lecturer and the
Dean of the Faculty of Computing and Information Systems
at Ghana Communication Technology University, Accra,
Ghana. He holds a Ph.D. in Automation and Control from
Tambov State Technical University, Russian Federation.
His research interests include control systems, pervasive
computing, and human-robot interaction.

27
PAPER_TEXT
