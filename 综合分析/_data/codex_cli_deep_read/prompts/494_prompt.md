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
# [494] Multi-View Intrusion Detection Framework Using Deep Learning and Knowledge Graphs
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
编号：494
题名：Multi-View Intrusion Detection Framework Using Deep Learning and Knowledge Graphs
年份：2025
DOI：10.3390/info16050377
来源：Information
PDF：paper/10.3390_info16050377.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：图学习、知识图谱与威胁情报、其他AI安全与跨域异常检测
相关性：强相关，分数 14
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\494.txt
- 原始字符数：79257
- 本次发送字符数：79257
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
information
Article

Multi-View Intrusion Detection Framework Using Deep
Learning and Knowledge Graphs
Min Li 1,2 , Yuansong Qiao 1
1

2

*

Academic Editor: Jian Tang
Received: 12 March 2025
Revised: 24 April 2025
Accepted: 27 April 2025
Published: 1 May 2025
Citation: Li, M.; Qiao, Y.; Lee, B.
Multi-View Intrusion Detection
Framework Using Deep Learning and
Knowledge Graphs. Information 2025,
16, 377. https://doi.org/10.3390/
info16050377
Copyright: © 2025 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license

and Brian Lee 1, *
Software Research Institute, Technological University of the Shannon: Midlands Midwest, University Road,
N37 HD68 Athlone, Ireland; a00278508@student.tus.ie (M.L.); yuansong.qiao@tus.ie (Y.Q.)
School of Artificial Intelligence, Jingchu University of Technology, No. 33 Xiangshan Road,
Jingmen 448000, China
Correspondence: brian.lee@tus.ie

Abstract: Traditional intrusion detection systems (IDSs) rely on static rules and onedimensional features, and they have difficulty dealing with zero-day attacks and highly
concealed threats; furthermore, mainstream deep learning models cannot capture the correlation between multiple views of attacks due to their single perspective. This paper
proposes a knowledge graph-enhanced multi-view deep learning framework, considering
the strategy of integrating network traffic, host behavior, and semantic relationships; and
evaluates the impact of the secondary fusion strategy on feature fusion to identify the
optimal multi-view model configuration. The primary objective is to verify the superiority
of multi-view feature fusion technology and determine whether incorporating knowledge
graphs (KGs) can further enhance model performance. First, we introduce the knowledge
graph (KG) as one of the feature views and neural networks as additional views, forming a multi-view feature fusion strategy that emphasizes the integration of spatial and
relational features. The KG represents relational features combined with spatial features
extracted by neural networks, enabling a more comprehensive representation of attack
patterns through the synergy of both feature types. Secondly, based on this foundation,
we propose a two-level fusion strategy. During the representation learning of spatial
features, primary fusion is performed of each view, followed by secondary fusion with
relational features from KG, thereby deepening and broadening feature integration. These
strategies for understanding and deploying the multi-view concept improve the model’s
expressive power and detection performance and also demonstrate strong generalization
and robustness across three datasets, including TON_IoT and UNSW-NB15, marking a contribution of this study. After experimental evaluation, the F1 scores of multi-view models
outperformed single-view models across all three datasets. Specifically, the F1 score of
the multi-view approach (Model 6) improved by 10.57% on the TON_IoT Network+Win10
dataset compared with the best single-view model. In contrast, improvements of 5.53%
and 3.21% were observed on the TON_IoT network and UNSW-NB15 datasets. In terms of
feature fusion strategies, the secondary fusion strategy (Model 6) outperformed primary
fusion (Model 5). Furthermore, incorporating KG-based relational features as a separate
view improved model performance, a finding validated by ablation studies. Experimental
results show that the deep fusion strategy of multi-dimensional data overcomes the limitations of traditional single-view models, enables collaborative multi-dimensional analysis
of network attack behaviors, and significantly enhances detection capabilities in complex
attack scenarios. This approach establishes a scalable multimodal analysis framework
for intelligent cybersecurity, advancing intrusion detection beyond traditional rule-based
methods toward semantic understanding.

(https://creativecommons.org/
licenses/by/4.0/).

Information 2025, 16, 377

https://doi.org/10.3390/info16050377

Information 2025, 16, 377

2 of 27

Keywords: deep multi-view learning (DMVL); anomaly detection; knowledge graph (KG)

1. Introduction
In recent years, intrusion detection systems (IDSs) have emerged as a critical security
defense mechanism, effectively identifying and mitigating malicious intrusions [1,2]. These
systems can be broadly categorized into network intrusion detection systems (NIDSs)
and host-based intrusion detection systems (HIDSs). Specifically, the primary task of an
NIDS is to continuously monitor network activity and determine, in real time, whether
an alert should be triggered for the system administrator, while an HIDS focuses on
analyzing logs, system behaviors, and file integrity to detect suspicious activities. Despite
their widespread adoption, traditional IDS exhibit critical drawbacks such as high false
positive/false negative rates, computational overhead, and reliance on domain knowledge.
A robust IDS, whether it be network- or host-based, must be able to automatically identify
attack behaviors or potential threats concealed within monitored data, ensuring stable and
efficient operation of systems within both network and host environments. To enhance
protection against cyber threats, researchers have focused on developing more sophisticated
feature extraction techniques and efficient detection models.
In the early stages of the Internet, network attacks were relatively limited in scope
and could often be countered effectively through port-based detection mechanisms and
firewall technology [3]. However, as network behaviors have become increasingly intricate,
involving various communication protocols and varied user activities, traditional portbased and rule-based detection methods have shown significant limitations. Port-based
detection fails against port-hopping attacks due to its reliance on static port mappings, while
rule-based systems suffer from labor-intensive signature updates, resulting in unsustainable
maintenance overheads and inadequate protection against zero-day attacks, including
polymorphic malware. These methods also struggle to extract precise features and suffer
from high false positive rates when dealing with massive data flows and sophisticated
attack patterns characteristic of modern networks [4]. Furthermore, traditional anomaly
detection approaches are increasingly inadequate in addressing the complexity of new
and evolving attack scenarios due to their limited capabilities in feature extraction and
model development.
However, anomaly detection methods typically suffer from a high false positive rate,
which limits their reliability [4]. To solve this problem, this study uses deep learning
techniques to enhance the intelligence of anomaly detection systems, ultimately improving
the precision of network intrusion detection.
Traditional deep learning models either use single-dimensional traffic features or
simple neural networks. These approaches are generally inadequate for capturing the
intricate relationships within multi-source heterogeneous data, resulting in feature omission
and insufficient detection accuracy. To overcome these challenges, some studies have
increasingly focused on multi-view learning, aiming to capture effective features from
heterogeneous data in a more comprehensive manner. Multi-view models enable a detailed
representation of network behaviors by integrating information from various sources. For
example, network traffic data can be observed from various perspectives, with features
extracted and subsequently fused. Combining network traffic features with host-level
activity data allows for a more nuanced depiction of an attacker’s behavior, including
attempts to traverse network boundaries. This integrative approach ultimately enhances
the effectiveness and comprehensiveness of intrusion detection systems.

Information 2025, 16, 377

3 of 27

In multi-view models, deep learning techniques are often employed to unilaterally
extract features (such as spatial or relational characteristics). For instance, convolutional
neural networks (CNNs) are frequently used to capture spatial features, while recurrent
neural networks (RNNs) are effective at modeling local temporal relationships [5,6]. However, these approaches tend to fall short of fully exploring the global complementarity
inherent amongst different views. In this context, the current study proposes incorporating
KG as an additional feature view to facilitate the integration of spatial and relational features. KG provides a structured framework by linking entities and events, thereby enabling
a systematic representation of network traffic data [7]. Within network intrusion detection,
KG is particularly useful for describing the complex associations between network entities
(e.g., IP addresses, ports, hosts), enriching the model’s comprehension of semantic context,
and ultimately enhancing the ability of multi-view models to identify latent threats [8].
The primary objective of this study is to verify the superiority of multi-view features
fusion technology in intrusion detection and to determine whether incorporating KGs can
further improve model performance. Moreover, the study evaluates the impact of first-level
and second-level fusion strategies on feature integration to identify the optimal multi-view
model configuration.
The main contributions of this paper are summarized as follows:
(1)

(2)

(3)

Multi-view features fusion to enhance anomaly detection: This study presents a
multi-view data fusion framework that integrates host data and network traffic data
to improve anomaly detection performance. The robustness and generalizability of
the proposed model were evaluated using the TON_IoT and UNSW-NB15 datasets.
Diversified model evaluation for intrusion detection: This study conducted a
comprehensive evaluation of both single-view models (CNN, LSTM, CNN+attention
LSTM) and multi-view fusion models ((KG+CNN)+attention LSTM, (KG+MultiCNNs)+attention LSTM). The results highlight the advantages of multi-view fusion in
enhancing detection accuracy and reliability over traditional single-view approaches.
Optimization of multi-view fusion strategies and the role of KG: This study assessed the impact of one-level and two-level fusion strategies on model performance
under consistent experimental conditions. Through ablation studies, the contribution of KG to feature fusion and anomaly detection was validated, emphasizing the
pivotal role of KG in boosting the effectiveness of multi-view models.

The remainder of this paper is organized as follows: Section 2 provides background
information and reviews related work in the field of network intrusion detection. Section 3
presents the proposed methodology in detail, including the design of the model and
the construction of the KG. Section 4 outlines the preparation steps for the experiments,
including a brief description of the TON_IoT network, TON_IoT network+Win10, and
UNSW-NB15 datasets used in the study, as well as data preprocessing procedures for the
experimental evaluation and integration of the multi-view framework. Section 5 details the
experimental setup and results, including the deployment of single-view and multi-view
models as well as ablation experiments. Finally, Section 6 summarizes the experimental
conclusions and discusses the practical application value of the proposed model.

2. Related Work
In line with the focus of this study, we provide a concise review of related work in
the areas of intrusion detection systems based on single-view and multi-view models and
cybersecurity KGs.
In the field of intrusion detection, the current mainstream methods are based on
machine learning (ML) or deep learning (DL). For example, k-nearest neighbor (KNN) [9]
and support vector machine (SVM) [10] have shown considerable success in addressing

Information 2025, 16, 377

4 of 27

classification and clustering tasks using well-known datasets like KDD99, NSL-KDD,
and DARPA, following a single-view strategy. However, these datasets are now largely
considered obsolete, as they contain overly simplistic attack patterns that do not accurately
reflect the complexity of today’s network environments [11].
To address the limitations inherent in single-view intrusion detection systems, multiview models have been developed to fuse and embed data from multiple perspectives into
a shared latent space, thereby facilitating the extraction of richer and more informative
representations. One representative traditional approach is canonical correlation analysis
(CCA) [12] which, while offering some capability in fusing data, is limited in capturing
high-order interactions across heterogeneous data sources. In response to these limitations,
a variety of deep learning-based architectures have emerged, including multimodal deep
Boltzmann machines [13], multimodal deep autoencoders [14], and multimodal recurrent
neural networks [15]. The crux of multi-view representation learning lies in its ability
to model intricate dependencies and interactions between multiple data views. This
representation learning method has shown its superiority in other studies. For example,
Peng et al. [16] proposed a deep multi-view framework that leverages multi-view learning
in combination with graph convolutional networks (GCNs) to tackle anomaly detection in
attributed networks. Comparative experiments indicated that this framework outperforms
a range of existing baseline models, including both traditional single-view and multiview methods, demonstrating the effectiveness of the multi-view approach in complex
network settings.
As a security-specific KG, the cybersecurity KG comprises nodes and edges that form
an extensive security semantic network, enabling the modeling of various real-world
attack and defense scenarios. Beyond information extraction (IE) [17,18], cybersecurity
KG presents several advantages, such as entity disambiguation [19], enabling the effective
extraction and integration of knowledge from heterogeneous data from multi-sources.
Furthermore, cybersecurity KG facilitates the structured representation of cybersecurity
knowledge, capturing relationships between entities, and visualizing this information
graphically, which provides an efficient and highly intuitive means of comprehension [20].
In addition to the intrusion detection methods discussed in [21], KGs have demonstrated constructive potential in supporting intrusion detection efforts. Yang et al. [22]
proposed a DDoS detection method based on KG technology, extracting key feature pairs
related to network attacks through semantic feature analysis and co-occurrence calculations,
effectively capturing semantic relationships between traffic characteristics. In their work,
the KG is used to represent the communication processes between hosts. By integrating
multi-view feature fusion, they combined features extracted from the knowledge graph
with statistical analysis features, enabling efficient detection and classification of threats.
Garrido et al. [23] applied machine learning techniques to KG to detect anomalous activities
in industrial automation systems that integrate IT and OT components. Xiao et al. [24]
proposed a KG embedding method to predict intra-type and inter-type relationships among
software security entities, thereby assisting analysts in enriching software security knowledge by identifying previously unknown relationships. However, it should be noted
that the cybersecurity KG described by Xiao et al. [24] is not open-source, restricting
access to its underlying details. The KG part of this study is constructed by integrating
three main sources of knowledge: host-level information, network-level observations (e.g.,
inter-host connections), and application-level observations (e.g. data access events) [25].
This approach aims to create a comprehensive cybersecurity KG that facilitates a better
understanding of network behaviors.

Information 2025, 16, 377

5 of 27

Upon reviewing current research on single-view models, multi-view models, and KG
within the domain of network security for intrusion detection, it becomes evident that
most existing methods tend to rely on a single technical paradigm. In the related studies
mentioned above, either independent traditional neural network models or isolated KGs
were used. While these techniques have achieved noteworthy results in their respective
domains, Garrido et al. [23] mentioned that traditional IDS detects events independently
and lacks a holistic view of complex attack patterns. At the same time, it is noted that
the knowledge graph method may be combined with the traditional intrusion detection
system (IDS) in the future, but no specific implementation path has been given. Even
when single-technology neural network models are enhanced using multi-view fusion
techniques, the fusion is often restricted to the extension of spatial features, failing to
fully harness the comprehensive potential of multi-source information. Likewise, while
KGs effectively capture the relational characteristics between network entities, they are
unable to comprehensively represent and integrate spatial features. Feature representation
in intrusion detection is inherently multi-dimensional, encompassing spatial, relational,
and temporal aspects; however, current approaches struggle to effectively integrate these
diverse features.
In response to these limitations, our study advances the concept of multi-view models
at two distinct levels. First, we fuse KGs and neural network as different views to achieve
effective integration of multi-view features. This multi-view features fusion strategy emphasizes the combination of spatial and relational features—representing relational characteristics through KG and integrating them with spatial features extracted by neural networks.
This synergistic integration provides a more comprehensive representation of attack patterns, thus significantly enhancing the accuracy and robustness of intrusion detection.
Building on this foundation, we introduce a two-level fusion strategy. At the first level,
spatial features are fused within each view, followed by a second-level fusion that integrates
these features with the relational information captured in the KG. This hierarchical fusion
enhances both the depth and breadth of feature integration, resulting in richer, more expressive feature representations. The proposed two-level fusion strategy not only improves the
model’s detection performance but also demonstrates superior generalization and robustness across multiple datasets (such as TON_IoT and UNSW-NB15). These contributions
represent a key highlight of the study, offering a novel approach to tackling the challenges
associated with multi-dimensional feature representation in network intrusion detection.

3. Methodology
3.1. Overview
This study has two objectives: (i) to determine whether a multi-view fusion-based
model outperforms single-view models in intrusion detection within network security; and
(ii) to assess whether incorporating a KG as an additional feature view can enhance the
multi-view model’s performance. The following sections outline the approaches used in
the study to achieve its goals.
Baseline Analysis of Single-View Models: To establish baselines for our multiview framework, we developed three distinct single-view models, each with a different
architecture: CNN, LSTM, and a hybrid model that combines CNN with attention-based
LSTM. These single-view models were chosen mainly because the multi-view fusion model
is designed based on these single-view models. Such a comparison helps to verify the
effectiveness and contribution of the fusion strategy from an experimental perspective.
These single-view models serve as baseline comparisons, and we use them to evaluate the
effectiveness of our multi-view fusion strategies.

Information 2025, 16, 377

6 of 27

Multi-View Features Fusion Strategy Evaluation: The multi-view fusion approach
employed in this study integrates host-based features and network traffic data through a
spatial and relational lens. More concretely, our methodology involves the fusion of spatial
features extracted through a CNN with relational features derived from a KG. We explored
two distinct fusion strategies:
Fusion Strategy 1— This approach integrates features extracted from both the KG and the
CNN, thereby combining relational and spatial characteristics into a unified representation.
Fusion Strategy 2—This approach extends the multi-view learning capability by integrating multiple CNN modules with the KG to achieve a layered, hierarchical fusion. On
the one hand, the CNN module extracts local features of each perspective in multi-view
fusion, reflecting the spatial features of different perspectives. On the other hand, KG
provides explicit relational features from a global perspective. The associations, constraints,
and logical relationships between entities are integrated into the feature expression. This
makes up for the important features that are missed due to the associations between local
features. This two-layer fusion mechanism not only effectively combines local spatial
features with global relational features, but also makes up for the shortcomings of a single
perspective in feature expression; KG can help to make up for the missing information
between local features and more comprehensively explores the synergy between spatial
features and relational features.
KG Ablation Experiment: To assess the contribution of relational features from KG
in our multi-view fusion strategy, we performed ablation experiments. By comparing
the performance of the complete model—including the KG component—with a variant
excluding this component, we observed the impact of KG-based features on the overall
effectiveness of feature fusion and anomaly detection.
To validate the robustness of our models and to assess their generalizability across
heterogeneous network and host environments, we conducted experiments utilizing three
distinct datasets: TON_IoT network+Win10, TON_IoT network, and UNSW-NB15. These
datasets allow for a comprehensive evaluation of the proposed models, ensuring that their
efficacy can be demonstrated under varied and complex network security scenarios.
3.2. Model Design
In this section, we introduce the design structure of all the models used in the experiment. To simplify the naming, each model is numbered.
Model 1: CNN. In this study, a single-view CNN is utilized to process three raw
datasets directly without involving traditional feature engineering techniques. This singleview CNN serves as a baseline for comparison with the more advanced multi-view CNN
model that will be introduced later. The CNN follows a conventional architecture, comprising an input layer, convolutional layers, pooling layers, and fully connected layers [26,27].
Model 2: LSTM. LSTM is a specialized recurrent neural network (RNN) designed to
address the vanishing and exploding gradient issues in traditional RNNs during long-term
dependency tasks. The LSTM model architecture in this study consists of an input layer,
an LSTM layer, fully connected layers, and an output layer. The LSTM layer, through its
memory cells (cell states), input gate, forget gate, and output gate, effectively captures
complex temporal dependencies present in network traffic analysis. This study employs
a single-view LSTM model, which means it only receives input from a single feature
space [26,27].

Information 2025, 16, 377

7 of 27

Model 3: CNN+Attn-Based LSTM. This model integrates CNN, LSTM, and attention
mechanisms to effectively capture both spatial and temporal features inherent in network
traffic data. Initially, a CNN is utilized to process the complete feature set from all datasets,
uncovering local dependencies and essential patterns in the data. This single-view model
establishes a foundational benchmark for comparison against more sophisticated multiview frameworks that incorporate KG for enriched feature representation. The spatial
features derived from CNN are subsequently passed to an LSTM layer, enabling the
model to learn the temporal relationships embedded in the data sequences. To improve
the model’s ability to highlight key temporal dependencies, an attention mechanism is
integrated. Finally, a classification layer leverages these enhanced features to classify
network traffic data. By combining spatial and temporal insights, this architecture is well
equipped to capture complex patterns and dependencies that distinguish between typical
and atypical network behaviors.
Model 4: multi-CNNs+Attn-Based LSTM. The model introduced in this section employs a multi-convolutional network structure during the feature extraction phase to better
capture the diversity of different feature spaces. This is another baseline framework. Later,
a multi-view framework will be built based on this baseline framework by adding multiple
views of KG. Specifically, the model initially divides each dataset into multiple subsets,
with each subset passing through an independent convolutional layer to extract spatial
features from various perspectives. This multi-perspective convolutional structure enables
the model to capture more diverse feature expressions, thereby providing a comprehensive understanding of the complex feature space. Once the spatial features are extracted,
they are fused and fed into an LSTM layer equipped with an attention mechanism. This
configuration is intended to learn temporal dependencies while emphasizing the most
significant features. Ultimately, the fused features are classified by a fully connected layer
to determine whether the network traffic is normal or anomalous.
Model 5: (KG+CNN)+Attn-Based LSTM. The proposed multi-view KG+CNN+attention

LSTM model in this study effectively facilitates the comprehensive detection of network
traffic anomalies through multi-stage feature extraction and fusion. The framework, aside
from data preprocessing, is composed of four components: feature extraction through
two complementary models (KG+CNN), view pooling, attention-based modeling, and
final classification.
Initially, during the data preprocessing stage, data cleaning and feature encoding
are conducted on each dataset to ensure data quality, uniformity, and reliability. In the
subsequent feature extraction stage, relational features are derived from KG, while spatial
features are captured using CNN. The KG is employed to reveal intricate inter-feature
relationships, whereas the CNN is utilized to extract significant local patterns present in
the network traffic. This strategy integrates spatial and relational features in the fusion
layer to achieve a more comprehensive feature representation .
Ffused = σ (W1 · [FCNN ∥FKG ]),

(1)

Here, FCNN ∈ Rd1 denotes the spatial features extracted by the CNN module, and
FKG ∈ Rd2 denotes the relational features derived from the KG.
Figure 1 shows the details of the framework based on the TON_IoT network and
UNSW-NB15 datasets. Among them, the process of generating KG is further shown
in Figure 2.

Information 2025, 16, 377

8 of 27

Figure 1. (KG+CNN)+attention LSTM multi-view model based on the TON_IOT network
(UNSW-NB15).

Figure 2. Construction of the KG based on the TON_IOT network (UNSW-NB15).

For the combined TON_IoT network and Win10 dataset, the feature extraction approach involves some notable adjustments, primarily concerning the CNN-based feature
extraction process. Figure 3 shows the framework details based on the TON_IoT network+Win10 combined dataset. Also, the KG process framework as a part of the model is
further illustrated in Figure 4.

Figure 3. (KG+CNN)+attention LSTM multi-view model based on TON_IOT network+Win10.

Figure 4. Construction of the KG based on TON_IOT network+Win10.

Information 2025, 16, 377

9 of 27

The model processes the TON_IoT network and Win10 sub-datasets independently
and then merges the features in the fusion layer of CNN (Step 2: Feature Extract). The
combined CNN features are then further integrated with the relational features derived
from KG (Step 3: Multi-View Fusion). This fused feature representation is then passed to
the LSTM layer equipped with an attention mechanism (Step 4), which aims to capture
temporal patterns while emphasizing key features. Finally, the fully connected classification
layer is used to determine whether network traffic is normal or anomalous. This collaborative mechanism allows the model to effectively leverage the multi-view information
from different datasets, thereby enhancing the accuracy and robustness of network traffic
anomaly detection.
Model 6: (KG+multi-CNN)+Attn-Based LSTM. This model further extends the multiview learning framework, aiming to better manage data diversity and complexity, thus
enhancing network traffic anomaly detection performance. Here, the feature extraction
stage is different. This model implements a two-level fusion approach. In the first level,
the dataset is divided into several subsets from different perspectives (See Section 4.2 for
details on multi-view subsets), and each subset is processed independently by convolutional
layers. These extracted features are then integrated through view pooling, which ensures
comprehensive utilization of the feature expressions from each perspective. In parallel,
relational features are extracted from the KG. The following is the expression of the first
(i )

level fusion (local spatial features). For N CNN modules (multi-view), let FCNN be the
features from the i-th CNN. These are first fused via weighted aggregation:
N

Flocal = ∑ αi FCNN ,
(i )

(2)

i =1

where αi is an attention weight for the i-th view, learned via:
(i )

αi =

exp(v T FCNN )
( j)

T
∑N
j=1 exp( v FCNN )

,

(3)

with v as a learnable vector.
In the second level, the fusion process integrates these spatial features with the relational features derived from KG, thereby enriching the overall feature representation.
The resulting fused features are subsequently input into an LSTM layer with an attention
mechanism. During the classification stage, the fully connected layer is used to classify
the fused features, determining whether the network traffic is normal or anomalous. The
following is the expression of second-level fusion (global relational+local features). The
local features Flocal are integrated with KG features FKG via:
Ffused = σ (W2 · [Flocal ∥ FKG ]),

(4)

The structure of the model is shown in Figures 5 and 6. The focus is on how to improve
the detection performance through the synergy of multi-CNN modules and KG. The KG
process framework as part of the model is shown in Figures 2 and 4, respectively.

Information 2025, 16, 377

10 of 27

Figure 5. (KG+multi-CNNs)+attention LSTM multi-view model based on the TON_IOT network
(UNSW-NB15).

Figure 6. (KG+multi-CNNs)+attention LSTM multi-view model based on TON_IOT network+Win10.

3.3. Construction of the KG
This section provides a detailed explanation of an alternative feature fusion approach—one that is based on the KG. The KG aims to enrich the level of data representation
by extracting relational features, thereby enhancing the model’s capability to identify complex interactions. Therefore, as part of another fusion strategy, we construct a global KG to
extract these relational features.
Depending on the characteristics of the different datasets, the construction process
of the KG varies slightly. Figure 2 illustrates the construction process for the TON_IoT
network and UNSW-NB15 datasets, while Figure 4 details the construction process for the
combined TON_IoT network and Win10 dataset.
First, it is essential to understand some foundational definitions related to KG construction. The KG serves as structured semantic frameworks that effectively represent various
concepts and the relationships connecting them within the real world [28]. Formally, a KG
G can be described as G = ( E, R, T ), where G is a labeled, directed multi-graph. In this
context, E = {e1 , e2 , . . . , e| E| } represents the set of entities, while R = {r1 , r2 , . . . , r| R| } represents the set of relationships. The sizes of these sets are denoted by | E| and | R|, respectively.

Information 2025, 16, 377

11 of 27

The facts represented within the KG are encoded as triples T = {(e, r, e′ ) | e, e′ ∈ E, r ∈ R},
which detail a specific relationship r linking the head entity e to the tail entity e′ . Within
a knowledge base, these facts are typically expressed in the form of triples like <entity,
relationship, entity> or <concept, attribute, value> [25].
In this study, the construction of a KG mainly involves creating nodes and edges.
Nodes represent the fundamental units within a KG and typically denote features or
entities. In the scenario of network traffic analysis, nodes can be network features (such as
traffic type and timestamp) or system features (such as Windows features). Edges represent
the relationships between nodes. By effectively constructing nodes and edges, the KG
can provide a comprehensive and enriched feature representation, thereby supporting
subsequent feature fusion and anomaly detection. For the ontology design of the knowledge
graph (KG), this study employs edge generation rules based on domain-driven feature
classification and statistical constraints. Regarding semantic definitions, the approach
relies on feature naming and dataset classification to directly represent domain semantics
(see Section 4.1). The statistical analysis of edge relationships is not solely based on cooccurrence but also incorporates domain knowledge (see Algorithms 1 and 2). For the
KG, we chose to use features as nodes and build edges based on co-occurrence because it
lets us uncover meaningful relationships directly from the data without hardcoding them.
Binarizing the edges keeps the graph simple and easier to work with. Grouping features by
their source adds clarity to the structure and makes it easier to align with other parts of the
model, like the CNN-based spatial features.
Feature extraction using the KG is divided into two steps: KG construction and
knowledge extraction. The construction of the KG occurs during the data collection and
preprocessing phase, where input data are loaded and feature identification is performed,
including the extraction of both categorical and numerical features. Categorical features are
encoded, and numerical features are normalized to ensure comparability across different
feature types on a unified scale. Key features are identified through an evaluation of feature
importance, followed by binarization to improve the model’s ability to handle discrete
data effectively. The co-occurrence relationships are obtained by binarizing the feature
matrix and performing matrix multiplication (‘X.T @ X’), where each element represents the
number of times two features appear together within the same window. To ensure that the
graph structure remains sparse and meaningful, a threshold is applied to the co-occurrence
count or frequency, retaining only high-frequency feature pairs as edges in the KG. The
importance of nodes in the graph is further quantified using eigenvector centrality, which
supports subsequent model processing.
In the case of the TON_IoT network and Win10 combined dataset, which integrates
two distinct data sources, it is necessary to add nodes and edges to these two sub-datasets
separately when constructing the KG. Moreover, the KG must capture not only intra-source
feature correlations but also inter-source interactions, adding complexity to the calculation
of co-occurrence relationships between feature pairs. In the subsequent knowledge extraction and representation stage, node centrality is calculated to identify key nodes, which
generally correspond to important features in network traffic analysis. The multi-level
analysis of nodes and edges enables the resulting KG to effectively represent the intricate
interactive relationships among features, supporting comprehensive feature fusion and
anomaly detection.
The construction process of the KG is shown in Figure 2 (based on the TON_IoT
network and UNSW-NB15 datasets) and Figure 4 (based on the combined TON_IoT network+Win10 dataset), covering the initialization of nodes, the generation of edges, and
the calculation of the correlation of high co-occurrence features. Through these steps, the

Information 2025, 16, 377

12 of 27

KG effectively characterizes the relationships among network traffic features, laying the
groundwork for the subsequent implementation of multi-view feature fusion.
Algorithm 1 provides a detailed description of the KG construction process for the combined TON_IoT network and Win10 dataset, while Algorithm 2 outlines the construction
process for the TON_IoT network and UNSW-NB15 datasets.
Algorithm 1 KG Construction Based on TON_IoT network and Windows10 Dataset.
Require: Network dataset binary_ f eatures_network_d f ,
Windows dataset binary_ f eatures_windows_d f
Ensure: KG G, Critical features tensors.
1. Initialize an empty graph G using NetworkX.
2. Add feature columns from each dataset as nodes in G with corresponding dataset
attributes.
3. For each dataset, add edges based on feature co-occurrence:
Function ADD _ EDGES _ FROM _ COOCCURRENCE(d f , G, dataset_name, threshold):
Convert d f to boolean matrix using threshold.
Compute co-occurrence matrix via boolean dot product.
Add edges for feature pairs with non-zero co-occurrence.
End Function
Call ADD _ EDGES _ FROM _ COOCCURRENCE on both datasets.
4. Compute eigenvector centrality for all nodes.
5. Determine number of critical features to select from each dataset.
6. Sort nodes by centrality and select top features per dataset.
7. Convert selected feature names to tensor format:
Function STRING _ TO _ TENSOR( f eature_list):
Convert strings to hashed tensor values.
End Function
Apply STRING _ TO _ TENSOR on selected features.
8. Visualize graph G using spring layout with node styling by centrality.
9. Return graph G and critical feature tensors.
Algorithm 2 KG Construction Based on TON_IOT Network Dataset (UNSW-NB15 Dataset).
Require: Training dataset train_d f , Testing dataset test_d f
Ensure: Preprocessed datasets, Feature co-occurrence KG G
1. Load training and testing datasets.
2. Detect numeric and categorical columns.
3. Encode categorical features using label encoding on combined unique values.
4. Normalize numeric features using MinMaxScaler fitted on training data.
5. Extract X_train and y_train from training dataset.
6. Compute mutual information between features and labels to select top k features.
7. Build co-occurrence matrix:
Binarize top features, compute co-occurrence counts for each feature pair.
8. Construct graph G:
Add feature nodes and edges for pairs with co-occurrence above threshold.
9. Visualize graph G with Kamada-Kawai layout, color/size based on edge weights.
10. Return preprocessed datasets and knowledge graph G.

4. Preparation for the Experiment
4.1. Data Set
In recent years, various datasets for intrusion detection have emerged for evaluating network security systems. However, many older datasets, such as NSL-KDD, do
not accurately reflect the characteristics of modern, complex network attacks. Consequently, newer datasets have gained attention, including the CAIDA dataset [29], the ISCX
dataset [30], CICIDS 2017 [31], the UNSW-NB15 dataset, and the TON_IoT, etc. [32,33].
In our study, we utilize three datasets—UNSW-NB15, TON_IoT network, and TON_IoT

Information 2025, 16, 377

13 of 27

network+Win10—for experimental deployment. The UNSW-NB15 dataset focuses on simulating traditional network environments, while the TON_IoT dataset emphasizes attacks
on Internet of Things (IoT) devices and complex modern network environments. We also
know that network data focus on external traffic characteristics, while host data focus more
on internal activities and resource usage. Some malware may disguise itself as normal
network traffic but behave abnormally in host behavior (such as attempting to modify
critical system files). Therefore, we also deployed the experiment on a comprehensive data
set that combines network activity data sets with host activity data sets, thereby trying to
improve the model’s ability to detect complex attacks.
(1)

(2)

TON_IoT dataset: The dataset includes data on both normal operations and various
intrusion events, aiming to closely simulate network behaviors observed in practical
environments. In this study, we selected two types of data for combination: one is
network traffic data, and the other is a dataset combining network traffic data and
Windows data.
UNSW-NB15 dataset: The UNSW-NB15 dataset includes 2,540,044 records captured
through an IXIA traffic generator. Following data cleaning and preprocessing, portions of the data were released as two distinct .csv files: the UNSW_NB15_training-set
and the UNSW_NB15_test-set.

4.2. Multi-View Framework Integration
In this study, a multi-view framework was developed for each dataset to achieve
effective multi-view feature fusion. The two recommended multi-view models are the
simple model (CNN attention-based LSTM) and the complex model (multi-CNNs attentionbased LSTM). The complex model involves dividing each dataset into multiple subsets
via secondary feature fusion, extracting features from each subset independently, and
subsequently combining them to achieve enhanced feature representation.
Tables 1–3 illustrate the details of the three datasets being divided into independent
subsets. Notably, as TON_IoT network+Win10 is a combination of two datasets, when
processing multiple views, the two datasets are divided into subsets for processing.
Table 1. Multi-view feature description of TON_IoT+Win10.
View Category

Features

Type

Processor Activity

Processor_DPC_Rate, Processor_pct_Idle_Time, etc.
Network
I/Current
Bandwidth,
Network
I/Packets/sec, etc.
Process_Pool_Paged Bytes, Process_IO Read
Ops/sec, etc.
LogicalDisk(_Total)/Avg. Disk Bytes/Write, etc.
Memory/Pool Paged Bytes, Memory/Pool Nonpaged Bytes, etc.

Number

Network Activity
Process Activity
Disk Activity
Memory Activity

Number
Number
Number
Number

The data categories are segmented based on the nature of the data and the specific types
of information they capture during the inspection of network traffic. This segmentation is
also applied to one-level fusion in the framework with two-level fusion. This idea supports
the application of “multi-view feature fusion” in various modes.

Information 2025, 16, 377

14 of 27

Table 2. Multi-view feature description of UNSW-NB15.

Features

View Category

Network Traffic
Temporal
Protocol and Service
Security

Type

num_spkts,
num_dpkts,
num_sbytes, etc.
num_dur, num_sinpkt,
num_dinpkt, etc.
cat_proto_3pc,
cat_proto_a/n, etc.
num_sttl, num_dttl,
num_sloss, etc.

Numerical
Numerical
Categorical
Numerical

cat_state_CON,
cat_state_ECO, etc.

Connection

Mixed (Mostly Numerical)

Table 3. Multi-view feature description of the TON_IoT network.
No.

Feature Category

Feature Name

No.

Feature Category

Feature Name

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21

Intrinsic
Intrinsic
Intrinsic
Intrinsic
Intrinsic
Intrinsic
Intrinsic
Intrinsic
Intrinsic
Intrinsic
Intrinsic
Content
Content
Content
Content
Content
Content
Content
Content
Content
Content

src_ip
src_port
dst_ip
dst_port
proto
src_bytes
dst_bytes
src_pkts
dst_pkts
src_ip_bytes
dst_ip_bytes
service
dns_query
dns_class
dns_type
dns_rcode
dns_AA
dns_RD
dns_RA
dns_rejected
ssl_version

22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43

Content
Content
Content
Content
Content
Content
Content
Content
Content
Content
Content
Content
Content
Content
Content
Time-based
Time-based
Host-based
Host-based
Host-based
Host-based
Host-based

ssl_cipher
ssl_resumed
ssl_established
ssl_subject
ssl_issuer
http_method
http_uri
http_referrer
http_version
http_request_body_len
http_response_body_len
http_status_code
http_user_agent
http_orig_mime_types
http_resp_mime_types
network_ts
duration
conn_state
missed_bytes
weird_name
weird_addl
weird_notice

5. Experiment and Results
5.1. Experiment Outline
In this section, the validation of the proposed multi-view fusion strategy for anomaly
detection was undertaken through a series of comprehensive experiments, detailed as
follows; then, all results are shown in Tables 4–8.
Table 4. Comparison of single-view and multi-view models based on the TON_IoT network+Win10
dataset.
Model Number

Model Type

Model Name

TON_IoT Network+Win10 (F1)

Model 1
Model 2
Model 3
Model 5
Model 6

Single-view
Single-view
Single-view
Multi-view
Multi-view

CNN
LSTM
CNN+Attn-Based LSTM
(KG+CNN)+Attn-Based LSTM
(KG+multi-CNNs)+Attn-Based LSTM

0.815
0.726
0.87
0.95
0.96

Information 2025, 16, 377

15 of 27

Table 5. The number of nodes and edges in the KG based on the three datasets.

Datesets

TON_IoT Network

TON_IoT Network+Win10

UNSW-NB15

Nodes
Edges

43
696

170
10,894

43
874

Table 6. Comparison of single-view and multi-view models based on the TON_IoT network dataset.
Model Type

Model Number

Model Name

TON_IoT Network (F1)

Single-view

Model 1
Model 2
Model 3

CNN [26,34]
LSTM [26,32]
CNN+Attn-Based LSTM

0.7892/0.9111
0.8383/0.922
0.93

Multi-view

Model 5
Model 6

(KG+CNN)+Attn-Based LSTM
(KG+multi-CNNs)+Attn-Based LSTM

0.96
0.963

Table 7. Comparison of single-view and multi-view models based on the UNSW-NB15 dataset.

Model Number

Model Type

Model Name

UNSW-NB15 (F1)

Model 1
Model 2
Model 3
Model 5
Model 6

Single-view
Single-view
Single-view
Multi-view
Multi-view

CNN [27]
LSTM [27]
CNN+Attn-Based LSTM
(KG+CNN)+Attn-Based LSTM
(KG+multi-CNNs)+Attn-Based LSTM

0.717
0.811
0.814
0.821
0.837

Table 8. Ablation study results based on KG.
F1 Score
Model Name and Model Number

CNN+Attn LSTM (Model 3)
(KG+CNN)+Attn-Based LSTM (Model 5)
Multi-CNNs+Attn-Based LSTM (Model 4)
(KG+Multi-CNNs)+Attn-Based LSTM
(Model 6)

TON_IoT

UNSW-NB15

Network

Network+Win10

0.93
0.96
0.94

0.87
0.95
0.924

0.814
0.821
0.82

0.963

0.96

0.837

5.1.1. Comparative Analysis of Baseline (Single-View) and Multi-View Models
In this analysis, we assessed the performance of the proposed multi-view models
against the baseline single-view models. The results reveal that the multi-view models
(KG+CNN and KG+multi-CNNs) demonstrate a significant improvement in anomaly
detection accuracy by integrating relational and spatial features, thus outperforming the
single-view models. This enhancement underscores the value of a multi-view approach in
capturing complex feature interactions.
5.1.2. Comparison of Multi-View Fusion Strategies
To identify the most effective fusion strategy, we investigated two distinct multi-view
fusion methodologies: KG+CNN and KG+multi-CNNs. Under consistent experimental
conditions, these models comprehensively incorporate both host and network traffic characteristics, integrating spatial and relational information through one-level fusion (KG+CNN,
Figures 1 and 3) and two-level fusion (KG+multi-CNNs, Figures 5 and 6), respectively. This
comparative analysis aimed to discern which fusion strategy yields optimal performance
across diverse datasets and anomaly detection tasks.

Information 2025, 16, 377

16 of 27

5.1.3. Ablation Study on KG Contribution
In previous experiments, we only used multiple views based on spatial features but
ignored the relationship between features. This is also one of the main motivations of
this study. A pivotal component of this research is the incorporation of relational features
through the KG.
5.1.4. Generalization Evaluation Across Different Datasets
To further assess the generalizability of all proposed models across various network
and host environments, ablation experiments on KGs are also included. we conducted the
aforementioned experiments using three datasets: TON_IoT network+Win10, TON_IoT
network, and UNSW-NB15. The F1 score served as the primary evaluation metric, with
average values being computed over 10 repeated training iterations to ensure a robust and
reliable performance evaluation.
All experiments were conducted on a computer equipped with an AMD Ryzen 7
5800U CPU (8 cores, 16 threads, 1.9–4.4 GHz) with integrated AMD Radeon Graphics, and
additional hardware was provided by SRI, Center for High Performance Computing at
Technological University of the Shannon, Midlands Midwest.
The software stack included: operating system: Windows 10 Pro (64-bit); Python:
3.8.10 (Anaconda distribution); deep learning framework: PyTorch 1.12.1; supporting
libraries: scikit-learn 1.0.2, pandas 1.4.3, NetworkX 2.6.3.
5.2. Deployment of Single-View Models
This section describes the detailed deployment of experiments based on three singleview models (CNN, attention-based LSTM, and CNN+LSTM). The structure of the model
has been introduced in the model design section of Section 3 (Sections 3.1–3.3).
5.2.1. Experimental Deployment Based on the TON_IoT Network+Win10 Dataset
Model 1: CNN. The dataset employed in this study comprises two components: network traffic data (Network) and host behavior data (Windows 10). To enable the effective
integration of features from different sources, these two datasets were merged by concatenating them along the feature dimension, allowing the model to simultaneously leverage
the complementary information inherent in each data source. Various preprocessing procedures were applied to standardize the datasets. For example: non-numeric features are
encoded by LabelEncoder, and numeric features are standardized by StandardScaler.The
architecture of the proposed CNN model consists of two convolutional layers containing
32 and 64 filters, respectively, each employing a convolutional kernel of size (3, 3). BatchNormalization layers were utilized after each convolutional layer to accelerate convergence
and stabilize training, followed by MaxPooling layers to reduce spatial dimensions and
control overfitting. The final classification was carried out through a flattened layer followed by two fully connected layers. The model was compiled using the Adam optimizer
(lr = 0.0005) and trained for 20 epochs, with a batch size of 32, optimizing for efficiency and
generalizability.
Model 2: LSTM. The preprocessing approach adopted for the LSTM model mirrors
that of Model 1, ensuring consistency across experiments. The LSTM model architecture
comprises a single LSTM layer with an output dimensionality of 128, followed by a fully
connected layer to perform the final classification. An attention mechanism was incorporated after the LSTM layer to enhance the model’s ability to focus on key temporal
features, thereby improving the overall representation of the feature set. During the training phase, the model was optimized using the Adam optimizer (lr = 0.001) and trained

Information 2025, 16, 377

17 of 27

for 20 epochs, using a batch size of 32, and a validation set ratio of 20% was employed to
evaluate generalization capabilities during training.
Model 3: CNN+Attn-Based LSTM. In this hybrid model, spatial features are first
extracted using a convolutional layer and subsequently passed to an LSTM layer for
temporal feature extraction, with the LSTM layer being set to a hidden dimensionality of
128. An attention mechanism is added after the LSTM output. Finally, classification is
performed through the fully connected layer, and the probability value is output using the
Sigmoid activation function. The CNN model is a one-dimensional convolution layer that
uses 32 filters and a convolution kernel size of three to extract spatial features. The kernel
size of the maximum pooling layer (MaxPooling) is two, and the stride is two.
5.2.2. Experimental Deployment Based on the TON_IoT Network and UNSW-NB15 Dataset
Model 1: CNN. To verify the effectiveness of our proposed method, we compared
the experimental results with the related methods in the reference [26,34]. Zhong Cao [26]
implemented a single CNN model based on the TON_IoT network dataset. Asadullah
Momand [34] compared ABCNN with traditional CNN when verifying the effectiveness
of intrusion detection based on the TON_IoT network dataset. We also use them as the
baseline model in this study to compare with our work. In a cited study [27], J. Vimal
Rosyu used CNN as the baseline model to conduct intrusion detection experiments using
the UNSW-NB15 dataset.
Model 2: LSTM. Zhong Cao [26] also introduced a single long short-term memory
network (attention-based LSTM) model base on the TON_IoT network dataset enhanced
by an attention mechanism. Raisa Abedin Disha [32] studied the impact of feature selection
on model performance and used LSTM to process the ToN_IoT network dataset to solve
the timing dependency problem in network intrusion detection. On the other hand, The
attention-based LSTM model proposed in reference [27] was also employed to effectively
capture the temporal dependencies present in network traffic data. Experiments conducted
on the UNSW-NB15 dataset are revealed. Here, we use their experiments as a baseline
model to compare with our subsequent experiments.
Model 3: CNN+Attn-Based LSTM. Building upon both datasets, a hybrid CNN and
LSTM deep learning model was designed in this study for network traffic classification.
The convolutional component of the model uses a kernel size of three for feature extraction,
followed by a max pooling layer with a size of two for downsampling. The extracted
features are then fed into a unidirectional LSTM module comprising 32 hidden units, which
is responsible for capturing temporal dependencies. Finally, the binary classification task
is completed through a fully connected layer. This integration aims to capitalize on the
strengths of both CNNs and LSTMs—namely, spatial feature extraction and temporal
pattern learning.
5.3. Deployment of Multi-View Models
Two multi-view models are recommended in this study, which perform one-layer
fusion and two-layer fusion, respectively.
5.3.1. Experimental Deployment Based on the TON_IoT Network+Win10 Dataset
Model 5: (KG+CNN)+Attn-Based LSTM. This framework fuses the features extracted
from KG and CNN, respectively, and further processes them through the long shortterm memory network (LSTM) with an attention mechanism to achieve efficient feature
extraction and classification (Figure 3). Given that the dataset is composed of network
traffic and host data from the TON_IoT network and Windows 10 datasets, independent
feature extraction processes were constructed for each data source. Specifically, during the
construction of the comprehensive KG (Figure 4), nodes and edges were created for each

Information 2025, 16, 377

18 of 27

data subset independently. Nodes represent individual features, while edges denote feature
pairs that co-occur based on specified threshold conditions. To digitize these co-occurrence
relationships, binarization operations were applied, and edges were added both within
the same dataset and across datasets according to predefined co-occurrence thresholds.
The comprehensive KG thus constructed contains nodes derived from both the network
dataset and the Windows dataset, with edges being formed through the calculation of
co-occurrence relationships between feature pairs. Table 5 summarizes the number of nodes
and edges created during KG construction process for this combined dataset.
For feature extraction, eigenvector centrality was utilized to identify the key features
within each dataset. The main reason is that this method can quantify the importance
of nodes in the global structure of KG and directly reflect the influence of features in the
relationship network. Other methods, such as PCA, may destroy the interpretability of KG
entity relationships and fail to preserve topological constraints. RFE has high computational
cost, which is not suitable for our application scenario. Subsequently, features with the
highest centrality scores were selected for the subsequent fusion process to ensure that
the most influential features contribute to the model. The primary model parameters are
configured as follows: A one-dimensional CNN (with an output channel size of 32 and a
kernel size of 3) is applied to each dataset to extract 50-dimensional features. The LSTM
layer uses a single-layer architecture with an attention mechanism, consisting of 128 hidden
units. For training, the batch size was set to 16, and the learning rate was initialized at
0.0005. And the learning rate is optimized by the ReduceLROnPlateau scheduler.
The constructed comprehensive KG is shown in Figure 7. To distinguish nodes and
edges corresponding to different data subsets, distinct color schemes were employed, as
shown in Figure 8. Specifically, pink represents intra-dataset relationships, while orange
represents inter-dataset relationships.
Model 6: (KG+multi-CNNs)+Attn-Based LSTM. This framework implements a
secondary feature fusion process based on the initial fusion structure. Specifically, the
whole process includes two levels of fusion (Figure 6).
In the first level, the TON_IoT network dataset and the Windows 10 dataset are each
partitioned into multiple subsets (multi-views), with each subset undergoing independent
feature extraction via distinct CNN units. Each CNN unit consists of a convolutional
layer (with a kernel size of three and an output channel size of 32) followed by a fully
connected layer. This step achieves the first fusion by integrating feature representations
from different perspectives of the dataset.
In the second level of fusion, the multi-view features obtained from the first fusion
are further combined with the critical relational features extracted from the KG to form a
comprehensive feature representation. This dual-stage fusion aims to leverage both spatial
characteristics captured through CNNs and relational information provided by KG, thereby
enhancing the overall feature representation for anomaly detection.
The LSTM model within this framework is configured with 64 hidden units. Training
is conducted using a binary cross-entropy loss function (BCEWithLogitsLoss), with the
Adam optimizer being employed at a learning rate of 0.001. Table 5 provides the details
of the nodes and edges generated during KG construction for the three datasets, offering
insights into the underlying data relationships captured during feature fusion.

Information 2025, 16, 377

19 of 27

Figure 7. Knowledge graph based on the TON_IoT network and Windows 10.

The results are shown in Table 4, which is summarized in one table together with the
single-view results obtained in Section 5.2.1 (TON_IoT network+Win10 dataset).

Information 2025, 16, 377

20 of 27

Figure 8. KG-built different datasets with different colors based on TON_IoT network+window10.

5.3.2. Experimental Deployment Based on TON_IoT Network and UNSW-NB15 Dataset
Within the multi-view framework, two distinct fusion models were deployed for the
two datasets: Model 5 (Figure 3) and Model 6 (Figure 5). Both models extract relational
features through the construction of KG (Figure 2), which are subsequently fused with
spatial features obtained from convolutional layers.
Model 5 represents a one-level fusion framework within the multi-view architecture.
Specifically, its CNN module utilizes a one-dimensional convolutional layer (with a convolution kernel size of 3 × 3) and a fully connected layer to extract spatial features, which are
then fused with the relational features extracted from KG.
Model 6 implements a two-level fusion approach. Its feature extraction is completed by
a multi-view CNN. Each view’s CNN module consists of 64 filters with 3 × 3 convolutional

Information 2025, 16, 377

21 of 27

kernels. The multi-view CNN outputs are fused with KG features, resulting in a more
comprehensive feature representation.
For the LSTM component, The number of LSTM hidden units varies according to
the dataset: for the TON_IoT dataset, the hidden layer consists of 128 units, while for the
UNSW-NB15 dataset, it consists of 500 units. During training, both models employed the
BCEWithLogitsLoss as the loss function and utilized the Adam optimizer (lr = 0.0001) with
a batch size of 128.
Table 2 presents the number of nodes and edges created during the KG construction
for the two datasets. The experimental results are provided in Tables 6 and 7, which
are summarized alongside the single-view results discussed in Section 5.2.2 (TON_IoT
network and UNSW-NB15 dataset). Furthermore, the KG constructed from the UNSWNB15 dataset is depicted in Figure 9, while Figure 10 illustrates the KG derived from the
TON_IoT network.

Figure 9. Knowledge graph built based on the NSW-NB15 dataset.

Figure 10. KG built base on the TON_IoT network.

Information 2025, 16, 377

22 of 27

5.4. Deployment of Ablation Experiments
In the proposed multi-view fusion strategy, a KG is introduced to extract relational
features, thereby enhancing the model’s ability to capture complex feature relationships.
To evaluate the impact of incorporating KGs on the performance of fusion strategies in
both simple models (CNN-LSTM) and complex models (Multi-CNN-LSTM), we designed
and conducted ablation experiments. Specifically, the ablation studies were carried out
using the frameworks of the two recommended multi-view fusion strategies. The models
compared are as follows:
Model 3 (without KG) vs. Model 5 (with KG): these comparisons were conducted to
investigate the effect of KG integration on the simple CNN-attention LSTM architecture.
Model 4 (without KG) vs. Model 6 (with KG): these comparisons were aimed at
assessing the contribution of the KG in more complex, multi-view fusion scenarios.
The architectural details of these four models are provided in Section 3, while the corresponding experimental deployment parameters are discussed in Section 5, Sections 2 and 3.
In this section, we focus solely on presenting and analyzing the ablation experiment results
to provide an intuitive understanding of the impact of the KG integration (see Table 8).
From the experimental results presented in Table 8, it is evident that the models
incorporating the KG (Models 5 and 6) demonstrated improvements in F1 scores across
all datasets. This observation further substantiates the important role of KG in capturing
complex relationships among data and enhancing feature fusion. Notably, in the context
of multi-view feature processing (Model 6), the integration of KG led to the optimization
of the model’s overall performance. These findings underscore the efficacy of KG in
providing richer relational information, thereby facilitating a more comprehensive feature
representation that ultimately enhances the model’s ability to detect anomalies.

6. Conclusions
6.1. Experimental Conclusion Analysis
In alignment with the objectives of this study, this section presents a comprehensive
comparison between multi-view fusion and single-view approaches in anomaly detection,
as well as a comparison of fusion strategies. Particular emphasis is placed on verifying the
effectiveness of incorporating KG as one of the views in the multi-view fusion framework.
A thorough evaluation of the results from multiple perspectives is undertaken to ensure
a robust understanding of the contributions of different methodologies. This section will
provide a detailed analysis based on all the deployed experimental results.
6.1.1. F1 Score Analysis
1.

Advantages of Multi-View Models

Across the three datasets, the F1 score of the multi-view model is higher than that of the
single-view model. As presented in Table 4, within the TON_IoT network+Win10 dataset,
the recommended multi-view approach (Model 6) achieved an F1 score of 0.962, representing a 7% improvement over the best-performing single-view model, which achieved an F1
score of 0.9.
The aforementioned experimental results were further corroborated using two additional datasets. As illustrated in Tables 6 and 7, the highest F1 scores obtained by the
multi-view model (Model 6) for the TON_IoT network dataset and the UNSW-NB15 dataset
were 0.973 and 0.837, respectively, indicating substantial improvements in both cases.
2.

Comparison of Feature Fusion Strategies

Information 2025, 16, 377

23 of 27

The investigation into feature fusion strategies focused on two multi-view frameworks:
(1) identifying the optimal fusion framework; and (2) evaluating the importance of KGbased relational features within the fusion strategy.
As depicted in Tables 4–7, the two-level fusion framework (Model 6) outperformed
the primary fusion approach (Model 5). For instance, in Table 4, the F1 score of Model 6
for the TON_IoT network dataset was 0.973, representing an improvement over Model 5,
which achieved an F1 score of 0.96. Similarly, the results presented in Tables 6 and 7 further
reinforce the superiority of the two-level fusion strategy over the one-level fusion strategy.
The ablation experiment results presented in Table 8 further confirm the significance
of incorporating KG-based relational features as an independent view in the fusion process,
enhancing model performance. This enhancement is attributed to the effective use of
complementary information from different sources, thereby enriching the representation
of input features. For example, in the TON_IoT network+Win10 dataset, The F1 scores
were 0.95 for Model 5 and 0.965 for Model 6, respectively—both outperforming the models
that did not incorporate KG. These findings were similarly validated across the other two
datasets (TON_IoT network dataset and UNSW-NB15 dataset).
6.1.2. ANOVA Summary Analysis
An analysis of variance (ANOVA) test was used to determine differences in mean F1
scores between multiple groups. In Figure 11, a violin plot combined with a honeycomb
plot is used to illustrate the distribution of F1 scores for different models. In these plots,
the width of the violin plot represents the density of data points, with the wider portion
representing higher density. Each black dot represents the F1 score of a single experiment.
The results of the ANOVA test allow us to draw conclusions from three aspects:
1.

Superiority of Multi-View Models

Across the three datasets, multi-view models—particularly Model 6—demonstrated
superior performance in terms of higher F1 scores and reduced fluctuations. The F1 scores
of the single-view models (Model 1 and Model 2) were notably lower than those of the multiview models, underscoring that multi-view fusion enhances the generalization capability
of the models across different datasets.
2.

Comparison of Feature Fusion Strategies

The two-level fusion (Model 6) strategy outperformed the one-level fusion strategy
(Model 5), as evidenced by both higher F1 scores and greater concentration of score distribution. This result highlights the effectiveness of the two-level fusion approach in
synthesizing richer and more informative feature representations.
3.

Summary of Model Distribution Characteristics

Model 6 not only exhibited superior mean F1 scores compared with other models but
also demonstrated smaller variance, indicating more stable performance. The comparison
in the ablation experiments (Model 3 vs. Model 5, Model 4 vs. Model 6) is illustrated in
Figure 11. The models without KG features showed more dispersed distributions, thereby
validating the performance gains achieved by incorporating KG features. Importantly, this
performance improvement was consistent across all datasets.
Overall, the violin plots provide a visual summary of the significance and stability
of the multi-view models, two-level fusion strategies, and KG-based feature fusion in
enhancing model performance. The consistent results across different datasets further
reinforce the robustness and effectiveness of these approaches.

Information 2025, 16, 377

24 of 27

(a)

(b)

(c)
Figure 11. ANOVA test method based on three datasets: (a) TON_IoT network and Windows,
(b) TON_IoT network, (c) UNSW-NB15.

Information 2025, 16, 377

25 of 27

6.2. Practical Application Value of the Model in Network Intrusion Detection
The practical application value of the proposed model can be demonstrated through
several key aspects, as verified by the recommended approach in this study.
Firstly, the multi-view model effectively reduces false positives and false negatives
when dealing with complex and diverse attack scenarios, thereby enhancing the reliability
and robustness of intrusion detection systems. By integrating multiple perspectives of
data, the model is better equipped to capture the nuances of both normal and anomalous
behavior patterns, minimizing misclassification.
Secondly, the two-level fusion approach employed in the multi-source data fusion
strategy enables a more comprehensive integration of the complementary information from
each view. Its approach captures different layers of information, facilitating a richer feature
representation.
The third aspect is the contribution of KG features. The KG helps the model better
understand the complex relationships between network entities.
Although the proposed multi-view intrusion detection framework shows great potential, it still has some limitations. First, the framework assumes that the multi-view
data input is relatively stable, which may not always hold true in dynamic or resourceconstrained real-time environments. Second, the two-stage fusion imposes additional
computational overhead. Third, building and maintaining an up-to-date knowledge graph
in real time remains a challenging task.
In future work, we can improve in different areas based on the multi-view intrusion
detection framework proposed in this study. From a technical perspective of DL, we can
integrate cutting-edge deep learning progress from three directions, namely multimodal
deep representation learning, knowledge reasoning enhanced by graph neural networks,
and adaptive detection, to further improve system performance. From the perspective
of its application in real-time intrusion detection scenarios, there is real-time multiview data processing capability; real-time application value of the two-stage data fusion
mechanism; and real-time auxiliary value of KG features. In addition, there are also
cross-domain fusion research directions, such as migrating the multimodal adversarial
training framework in medical imaging to network intrusion detection, building dynamic
spatiotemporal graph neural networks, etc.
Author Contributions: M.L.: Conceptualization of this study, methodology, code, validation,
writing—original draft, visualization. Y.Q.: conceptualization of this study, supervision. B.L.: funding
acquisition, conceptualization of this study, methodology, writing—review and editing, supervision.
All authors have read and agreed to the published version of the manuscript.
Funding: This publication has emanated from research conducted with the financial support of the
Technological University of the Shannon under the President Doctoral Scholarship 2021; and the
Horizon Europe Framework Program (HORIZON), under the grant agreement 101119681, Resilmesh.
Institutional Review Board Statement: Not applicable.
Informed Consent Statement: Not applicable.
Data Availability Statement: The dataset used in this study is free and publicly available on the
Internet. We can obtain the TON IoT dataset and UNSW-NB15 dataset through the following link:
https://research.unsw.edu.au/projects/toniot-datasets (accessed on 11 March 2025).
Conflicts of Interest: The authors declare that they have no known competing financial interests or
personal relationships that could have appeared to influence the work reported in this paper.

Information 2025, 16, 377

26 of 27

References
1.
2.
3.
4.
5.
6.

7.
8.
9.
10.
11.
12.
13.
14.
15.
16.
17.
18.

19.
20.
21.
22.
23.
24.

25.
26.

Li, L.; Yu, Y.; Bai, S.; Hou, Y.; Chen, X. An effective two-step intrusion detection approach based on binary classification and
k-NN. IEEE Access 2018, 6, 12060–12073. [CrossRef]
Ali, M.H.; Al Mohammed, B.A.D.; Ismail, A.; Zolkipli, M.F. A new intrusion detection system based on fast learning network and
particle swarm optimization. IEEE Access 2018, 6, 20255–20261. [CrossRef]
Dainotti, A.; Gargiulo, F.; Kuncheva, L.I.; Pescapè, A.; Sansone, C. Identification of traffic flows hiding behind TCP Port 80. In
Proceedings of the IEEE International Conference on Communications, Cape Town, South Africa, 23–27 May 2010; pp. 1–6.
Mishra, P.; Varadharajan, V.; Tupakula, U.; Pilli, E.S. A detailed investigation and analysis of using machine learning techniques
for intrusion detection. IEEE Commun. Surv. Tutor. 2019, 21, 686–728. [CrossRef]
Yin, C.; Zhu, Y.; Fei, J.; He, X. A deep learning approach for intrusion detection using recurrent neural networks. IEEE Access
2017, 5, 21954–21961. [CrossRef]
Kim, J.; Kim, J.; Thu, H.L.T.; Kim, H. Long short term memory recurrent neural network classifier for intrusion detection.
In Proceedings of the International Conference on Platform Technology and Service (PlatCon), Jeju, Republic of Korea, 15–17
February 2016; pp. 1–5.
Jia, Y.; Qi, Y.; Shang, H.; Jiang, R.; Li, A. A practical approach to constructing a knowledge graph for cybersecurity. Engineering
2018, 4, 53–60. [CrossRef]
Undercoffer, J.; Pinkston, J.; Joshi, A.; Finin, T. A target-centric ontology for intrusion detection. In IJCAI-03 Workshop on Ontologies
and Distributed Systems; Morgan Kaufmann Publishers: Burlington, MA, USA, 2004; pp. 47–58.
Teng, S.; Wu, N.; Zhu, H.; Teng, L.; Zhang, W. SVM-DT-based adaptive and collaborative intrusion detection. IEEE/CAA J. Autom.
Sin. 2018, 5, 108–118. [CrossRef]
Liu, J.; Xu, L. Improvement of SOM classification algorithm and application effect analysis in intrusion detection. In Recent
Developments in Intelligent Computing, Communication and Devices; Springer: Berlin/Heidelberg, Germany, 2019; pp. 559–565.
Sun, P.; Liu, P.; Li, Q.; Liu, C.; Lu, X.; Hao, R.; Chen, J. DL-IDS: Extracting Features Using CNN-LSTM Hybrid Network for
Intrusion Detection System. Secur. Commun. Netw. 2020, 2020, 8890306. [CrossRef]
Hotelling, H. Relations between two sets of variates. Biometrika 1936, 28, 321–372. [CrossRef]
Srivastava, N.; Salakhutdinov, R.R. Multimodal learning with deep Boltzmann machines. In Proceedings of the International
Conference on Neural Information Processing Systems, Lake Tahoe, NV, USA, 3–6 December 2012; pp. 2222–2230.
Ngiam, J.; Khosla, A.; Kim, M.; Nam, J.; Lee, H.; Ng, A.Y. Multimodal deep learning. In Proceedings of the International
Conference on Machine Learning, Washington, DC, USA, 28 June–2 July 2011; pp. 689–696.
Mao, J.; Xu, W.; Yang, Y.; Wang, J.; Huang, Z.; Yuille, A. Deep captioning with multimodal recurrent neural networks (m-RNN).
arXiv 2014, arXiv:1412.6632.
Peng, Z.; Luo, M.; Li, J.; Xue, L.; Zheng, Q. A deep multi-view framework for anomaly detection on attributed networks. IEEE
Trans. Knowl. Data Eng. 2020, 34, 2539–2552. [CrossRef]
Zhao, J.; Yan, Q.; Li, J.; Shao, M.; He, Z.; Li, B. TIMiner: Automatically extracting and analyzing categorized cyber threat
intelligence from social data. Comput. Secur. 2020, 95, 101867. [CrossRef]
Husari, G.; Al-Shaer, E.; Ahmed, M.; Chu, B.; Niu, X. Ttpdrill: Automatic and accurate extraction of threat actions from
unstructured text of cti sources. In Proceedings of the Annual Computer Security Applications Conference, Orlando, FL, USA,
4–8 December 2017; pp. 103–115.
Bouarroudj, W.; Boufaida, Z.; Bellatreche, L. Named entity disambiguation in short texts over knowledge graphs. Knowl. Inf.
Syst. 2022, 64, 325–351 [CrossRef] [PubMed]
Liu, K.; Wang, F.; Ding, Z.; Liang, S.; Yu, Z.; Zhou, Y. A review of knowledge graph application scenarios in cyber security. arXiv
2022, arXiv:2204.04769.
Jian, S.; Lu, Z.; Du, D.; Jiang, B.; Liu, B.X. Overview of network intrusion detection technology. J. Cyber Secur. 2020, 5, 96–122.
Yang, X.; Peng, G.; Zhang, D.; Lv, Y. An enhanced intrusion detection system for IoT networks based on deep learning and
knowledge graph. Secur. Commun. Netw. 2022, 2022, 4748528. [CrossRef]
Garrido, J.S.; Dold, D.; Frank, J. Machine learning on knowledge graphs for context-aware security monitoring. In Proceedings of
the IEEE International Conference on Cyber Security and Resilience (CSR), Rhodes, Greece, 26–28 July 2021; pp. 55–60.
Xiao, H.; Xing, Z.; Li, X.; Guo, H. Embedding and predicting software security entity relationships: A knowledge graph based
approach. In Proceedings of the International Conference on Neural Information Processing, Sydney, Australia, 12–15 December
2019; pp. 50–63.
Liu, K.; Wang, F.; Ding, Z.; Liang, S.; Yu, Z.; Zhou, Y. Recent Progress of Using Knowledge Graph for Cybersecurity. Electronics
2022, 11, 2287. [CrossRef]
Cao, Z.; Zhao, Z.; Shang, W.; Ai, S.; Shen, S. Using the ToN-IoT dataset to develop a new intrusion detection system for industrial
IoT devices. In Multimedia Tools and Applications; Springer Science & Business Media: Berlin/Heidelberg, Germany, 2024.
[CrossRef]

Information 2025, 16, 377

27.
28.
29.
30.
31.
32.
33.
34.

27 of 27

Rosy, J.V.; Britto, S.; Kumar, R.; Scholar, R. Intrusion Detection On The Unsw-Nb15 Dataset Using Feature Selection And Machine
Learning Techniques. Webology 2021, 18, 6.
Hogan, A.; Blomqvist, E.; Cochez, M.; d’Amato, C.; Melo, G.D.; Gutierrez, C.; Kirrane, S.; Gayo, J.E.L.; Navigli, R.; Neumaier, S.;
et al. Knowledge graphs. Synth. Lect. Data Semant. Knowl. 2021, 12, 1–257.
Hick, P.; Aben, E.; Claffy, K.; Polterock, J. The CAIDA DDoS Attack 2007 Data Set. 2012. Available online: http://www.caida.org
(accessed on 10 July 2015).
Shiravi, A.; Shiravi, H.; Tavallaee, M.; Ghorbani, A. Toward Developing a Systematic Approach to Generate Benchmark Datasets
for Intrusion Detection. Comput. Secur. 2012, 31, 357–374. [CrossRef]
Sharafaldin, I.; Lashkari, A.; Ghorbani, A. Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. In Proceedings of the ICISSP, Madeira, Portugal, 22–24 January 2018; pp. 108–116.
Disha, R.; Waheed, S. Performance Analysis of Machine Learning Models for Intrusion Detection System Using Gini Impuritybased Weighted Random Forest (GIWRF) Feature Selection Technique. Cybersecurity 2022, 5, 1. [CrossRef]
Moustafa, N. ToN_IoT and UNSW15 Datasets. 2022. Available online: https://research.unsw.edu.au/projects/toniot-datasets
(accessed on 3 April 2022).
Momand, A.; Jan, S.U.; Ramzan, N. ABCNN-IDS: Attention-based convolutional neural network for intrusion detection in IoT
networks. Wirel. Pers. Commun. 2024, 136, 1981–2003. [CrossRef]

Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
PAPER_TEXT
