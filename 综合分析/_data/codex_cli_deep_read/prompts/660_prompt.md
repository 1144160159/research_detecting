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
# [660] Efficient Malicious Encrypted Traffic Detection via Multi-Scale Convolution-Augmented Transformer: The NetFlowClassifier Approach
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
编号：660
题名：Efficient Malicious Encrypted Traffic Detection via Multi-Scale Convolution-Augmented Transformer: The NetFlowClassifier Approach
年份：2026
DOI：10.1109/iccece69169.2026.11399795
来源：2026 6th International Conference on Consumer Electronics and Computer Engineering (ICCECE)
PDF：paper/10.1109_ICCECE69169.2026.11399795.pdf
已有粗分类：加密流量分类与应用识别
二级关联：恶意流量、暗网与攻击检测、网络流量监测、测量与工具
相关性：强相关，分数 17
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\660.txt
- 原始字符数：24970
- 本次发送字符数：24970
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2026 6th International Conference on Consumer Electronics and Computer Engineering (ICCECE) | 979-8-3315-8108-4/26/$31.00 ©2026 IEEE | DOI: 10.1109/ICCECE69169.2026.11399795

2026 6th International Conference on Consumer Electronics and Computer Engineering (ICCECE)

Efficient Malicious Encrypted Traffic Detection via
Multi-Scale Convolution-Augmented Transformer:
The NetFlowClassifier Approach
Zongbao Wang
State Grid Gansu Electric Power
Company Electric Power
Research Institute
Lanzhou, China

Juan Fu
State Grid Gansu Electric Power
Company Electric Power
Research Institute
Lanzhou, China

Zhili Ma
State Grid Gansu Electric Power
Company Electric Power
Research Institute
Lanzhou, China

Zhiru Li*
State Grid Gansu Electric Power
Company Electric Power
Research Institute
Lanzhou, China
*Corresponding author:
xiaozhi531@163.com

Mingming Xiang
State Grid Gansu Electric Power
Company Electric Power
Research Institute
Lanzhou, China

proportion of advanced cyber attacks are now delivered through
encrypted channels, making malicious encrypted traffic
detection a critical challenge for network security monitoring.

Abstract—With the widespread adoption of encryption
technologies, an increasing proportion of Internet traffic is
encrypted, which fundamentally weakens traditional traffic
inspection mechanisms. Existing port-based and payload-based
detection methods have become ineffective, while approaches
relying on handcrafted features suffer from limited discriminative
capability and poor generalization. To address the problem of
malicious encrypted traffic identification, this paper proposes a
lightweight hybrid model named NetFlowClassifier, together with
a targeted data preprocessing pipeline. An encrypted traffic
dataset is first constructed from CSE-CIC-IDS2018 for binary
classification of benign and malicious flows. The proposed model
integrates multi-scale depthwise separable convolution and an
improved Transformer encoder to jointly capture local
discriminative patterns and long-range dependencies. In addition,
learnable feature position encoding and attention-weighted
pooling are introduced to enhance feature representation.
Experimental results show that NetFlowClassifier achieves an F1score of 0.9661, outperforming baseline CNN and Transformer
models by 1.8%–3.2%. With 11.2 million parameters and a
throughput of 128 samples per second, the model effectively
balances detection accuracy and computational efficiency. These
results demonstrate the effectiveness of the proposed approach for
malicious encrypted traffic detection in modern network
environments.

This paradigm shift has significantly weakened traditional
traffic
inspection
techniques,
including
port-based
classification and Deep Packet Inspection (DPI) [1]. Port-based
methods rely on fixed port numbers and are easily bypassed by
dynamic port hopping and protocol obfuscation, while DPI
becomes ineffective when payload contents are fully encrypted.
To address this challenge, early studies introduced handcrafted
statistical features combined with traditional machine learning
models, such as SVM and Random Forest. However, these
approaches heavily depend on domain expertise and exhibit
limited generalization capability to emerging encryption
protocols and novel attack patterns.
With the emergence of deep learning, convolutional neural
networks were introduced to realize end-to-end encrypted
traffic classification, with Deep Packet [2] as a representative
model. Although CNN-based methods can effectively capture
local discriminative patterns, their fixed receptive fields restrict
the modeling of long-range dependencies in encrypted traffic
sequences. Transformer-based architectures have further
improved global feature modeling ability, yet their high
computational complexity and insufficient focus on finegrained malicious characteristics limit practical deployment,
especially in resource-constrained network environments.
Moreover, many existing studies are evaluated on outdated
datasets that fail to reflect modern encrypted attack scenarios,
reducing their applicability to real-world networks. In contrast,
the CSE-CIC-IDS2018 dataset includes diverse encrypted
traffic and contemporary attack types, highlighting the need for
more robust and adaptive classification models.

Keywords—Malicious encrypted traffic identification; Binary
classification; Multi-scale depthwise separable convolution;
Transformer; Attention-weighted pooling

I. INTRODUCTION
The rapid adoption of end-to-end encryption and Virtual
Private Network technologies has fundamentally reshaped
modern network communications. While encryption effectively
protects user privacy and data integrity, it also provides a
favorable environment for malicious activities, such as
ransomware propagation, data exfiltration, and botnet
command-and-control communications. An increasing

979-8-3315-8108-4/26/$31.00 ©2026 IEEE

To address these limitations, this paper proposes
NetFlowClassifier, a lightweight hybrid deep learning model

104

Authorized licensed use limited to: National Institute of Technology- Delhi. Downloaded on May 18,2026 at 09:53:54 UTC from IEEE Xplore. Restrictions apply.

for binary classification of encrypted traffic. The main
contributions of this paper can be summarized as follows:

effectively, but require reshaping one-dimensional traffic
sequences into two-dimensional representations, resulting in
increased computational overhead and limited capability in
modeling long-range dependencies. To explicitly model
temporal correlations among packets, LSTM-based models have
been applied to encrypted traffic classification tasks [4].
Although they demonstrate strong performance, these models
suffer from poor parallelism, long training time, and gradient
degradation on long sequences.

• A targeted preprocessing pipeline for CSE-CIC-IDS2018
is designed to filter encrypted flows, normalize 78dimensional traffic features, and eliminate redundant
header noise, thereby enhancing discriminative pattern
retention and reducing data heterogeneity.
• A novel hybrid architecture is proposed, integrating
multi-scale depthwise separable convolution with an
improved Transformer encoder, augmented by learnable
feature position encoding and attention-weighted pooling
to jointly model local and long-range dependencies.

Transformer-based architectures have recently been
introduced to model global dependencies in encrypted traffic
through self-attention mechanisms [5]. While these models
achieve competitive accuracy, their large parameter scale and
high computational complexity significantly limit their
deployment in resource-constrained network devices. Hybrid
architectures that combine convolutional local feature extraction
with Transformer-based global modeling have also been
explored for encrypted traffic classification [6]. In addition,
multi-scale feature extraction strategies and graph neural
network based flow modeling have been applied to further
enhance encrypted traffic identification performance [7] [8].

• A lightweight yet high-performance design is achieved,
with 11.2 million parameters and a throughput of 128
samples per second, enabling efficient deployment in
resource-constrained edge environments.
II. RELATED WORK
Early encrypted traffic classification mainly relied on rulebased techniques such as Deep Packet Inspection and port-based
mapping, which identify applications through protocol
semantics and fixed handshake fields. However, with the
evolution of encryption mechanisms and evasion strategies,
these approaches have gradually lost effectiveness. The
widespread adoption of TLS 1.3, QUIC, and HTTP/3 conceals
key handshake features, while port hopping and protocol
obfuscation further reduce detection reliability. Consequently,
existing rule-based systems show limited adaptability to
emerging encrypted protocols and modern malicious traffic.

Another critical issue concerns dataset timeliness. Most
existing studies are evaluated on outdated datasets that lack
modern encrypted protocols and sufficient encrypted malicious
samples, which fails to reflect current network environments
dominated by QUIC, TLS 1.3, and ECH traffic. Recently, largescale pre-trained and foundation models have emerged as a
promising research direction for improving generalization across
diverse encrypted traffic scenarios [9].
These observations motivate the design of a more efficient
and adaptive classification framework, which will be introduced
in the following section.

To overcome the rigidity of rule-based methods, early
learning-based approaches introduced handcrafted statistical
features combined with traditional machine learning models [3].
These features include entropy, packet size distribution, interarrival time, and flow-level attributes, and achieved promising
performance on early benchmark datasets. Nevertheless, this
paradigm suffers from three inherent limitations: feature design
is highly dependent on domain expertise, handcrafted features
are insufficient to represent dynamic malicious behaviors, and
model generalization across heterogeneous datasets is poor.

III. METHODOLOGY
A. Model Architecture Overview
To address the insufficient multi-scale feature representation
and inefficient long-range dependency modeling in encrypted
traffic classification, we propose NetFlowClassifier, a
lightweight hybrid framework that integrates structured feature
embedding, multi-scale local feature extraction, and global
dependency modeling in an end-to-end manner.

Deep learning techniques become a dominant paradigm by
enabling automatic feature extraction. Convolutional neural
network based models capture local byte-level patterns

Fig. 1. Overall architecture of the proposed NetFlowClassifier.

105
Authorized licensed use limited to: National Institute of Technology- Delhi. Downloaded on May 18,2026 at 09:53:54 UTC from IEEE Xplore. Restrictions apply.

As illustrated in Fig. 1, the model follows an embedding–
enhancement–sequence
modeling–adaptive
pooling–
classification pipeline. Given 78-dimensional structured
NetFlow features, NetFlowClassifier sequentially applies a
multi-scale convolution module, a stacked Transformer encoder,
and an attention-weighted pooling layer to obtain discriminative
global representations for malicious/benign classification. The
hybrid design enables the model to jointly capture fine-grained
local patterns and long-range feature dependencies while
maintaining lightweight characteristics suitable for edge
deployment.

expand the feature space and capture complex non-linear
relationships, followed by dual dropout layers to prevent
overfitting. The sequential encoding process of the four stacked
layers progressively refines feature representations, building on
multi-scale local features and attention-based global
dependencies to model complex relationships such as
correlations between TLS handshake features and subsequent
data transmission patterns. The attention mechanism is defined
as:
Attention(Q h , K h , V h ) = Softmax(

B. Data Preprocessing Module
To construct a high-quality encrypted traffic dataset, a
targeted preprocessing pipeline is designed based on CSE-CICIDS2018. Encrypted flows are first filtered using protocol and
port-based rules. Redundant, non-numeric, and privacysensitive fields are removed, and all features are normalized
into the range of [0, 1].

Q h K hT
16

)V h

(1)

To mitigate severe class imbalance, a batch-based SMOTE
strategy is adopted to synthesize minority-class samples,
yielding a balanced dataset suitable for supervised training. This
preprocessing process ensures that discriminative encrypted
malicious patterns are retained while reducing data
heterogeneity.
C. Multi-Scale Depthwise Separable Convolution Module
To capture local discriminative patterns of different
granularities, a MultiScaleConvBlock is designed using
depthwise separable convolution for computational efficiency.
Four parallel depthwise convolution kernels with sizes 3, 5, 7,
and 9 are applied to extract multi-scale local features, followed
by pointwise convolution for channel fusion. Residual
connections and normalization are employed to stabilize
training.

Fig. 2. Internal Structure Schematic of the Transformer Encoder in the
NetFlowClassifier Model.

E. Feature Enhancement and Classification Module
The classification module integrates learnable feature
position encoding, attention-weighted pooling, and a
hierarchical classification head, combined with advanced
training strategies to convert high-dimensional sequence
features into discriminative class probabilities. The
FeaturePositionEncoding module, tailored for 78-dimensional
structured features, introduces a trainable position embedding
matrix and a feature importance scaling vector to dynamically
adjust the weight of each feature dimension, enabling the model
to learn the semantic importance of different feature positions
and emphasize discriminative indicators. The AttentionPooling
module replaces traditional mean pooling with a two-layer
neural network to compute attention weights for each of the 78
feature positions, prioritizing high-contribution features through
softmax normalization and weighted summation to generate a
compact 128-dimensional global feature vector. The hierarchical
classification head adopts three linear layers with multi-layer
normalization and GELU activation, progressively compressing
feature dimensions while stabilizing feature distribution and
capturing complex decision boundaries. To improve model
robustness and training stability, a custom LabelSmoothingLoss
function replaces standard cross-entropy loss, the AdamW
optimizer with weight decay mitigates overfitting, and a
CosineAnnealingLR scheduler decays the learning rate from
0.0005 to 1e-6 over 50 epochs to balance exploration and
convergence.

This module enables the model to capture both fine-grained
and coarse-grained encrypted traffic patterns while significantly
reducing computational complexity compared to standard
convolution.
D. Transformer Encoder Module
To strengthen long-range dependency modeling while
controlling computational cost, the NetFlowClassifier adopts a
stacked Transformer encoder architecture with four layers and
multiple optimizations, including pre-normalization, reinforced
residual connections, and 8-head attention mechanisms. Fig. 2
illustrates the structure of the Transformer encoder in the
NetFlowClassifier Model.
The Multi Head Attention module adopts a TransformerXL-style pre-normalization strategy, applying layer
normalization before attention computation to stabilize deep
network training, with an input dimension of 128 and 8 attention
heads to balance feature resolution and efficiency. The multihead mechanism partitions the feature space into subspaces,
enabling simultaneous attention to different dependency types,
while residual connections preserve low-level features by
directly adding the attention output to the original input. The
Feed_Forward module incorporates a "pre-normalization +
bottleneck layer" structure, with a hidden dimension of 512 to

F. Algorithm Description of NetFlowClassifier
To improve the clarity and reproducibility of the proposed
framework, this subsection summarizes the overall training and

106
Authorized licensed use limited to: National Institute of Technology- Delhi. Downloaded on May 18,2026 at 09:53:54 UTC from IEEE Xplore. Restrictions apply.

set to 0.0005, and the AdamW optimizer was adopted with
weight decay of 0.01 and betas (0.9, 0.999) to suppress
overfitting; a CosineAnnealingLR learning rate scheduler was
applied to dynamically adjust the learning rate, with the
minimum learning rate decayed to 1e-6 over the training period
to facilitate late-stage convergence.

inference procedure of NetFlowClassifier in the form of pseudocode. The algorithm describes how structured NetFlow features
are embedded, enhanced by multi-scale convolution, encoded by
the Transformer layers, aggregated through attention-weighted
pooling, and finally mapped to classification results. It explicitly
illustrates the execution order of key modules and the data flow
among them, facilitating reproducibility and practical
implementation.The Fig.3 shows the algorithm description of
NetFlowClassifier.

A dropout rate of 0.15 was uniformly applied to key modules
(embedding layer, multi-head attention, FFN, and classification
head) to enhance model generalization, and label smoothing
with a smoothing factor of 0.1 was introduced to the crossentropy loss function to alleviate over-confidence in hard labels.
To prevent overfitting, an early stopping strategy was
implemented with a patience of 7 epochs: if the validation
accuracy did not improve by more than 1e-6 for 7 consecutive
epochs, training was terminated early, and the model checkpoint
with the highest validation accuracy was saved. Additionally, all
feature inputs were normalized to the range [0,1] before feeding
into the model, and the position encoding module adopted
learnable parameterization to adapt to the structural
characteristics of NetFlow features.
C. Baseline Models and Metrics
To evaluate the effectiveness of NetFlowClassifier, three
representative baselines are selected:
• SVM: Traditional machine learning model using original
NetFlow features.
• Basic1DCNN: Single-scale convolution-based model
focusing on local feature extraction.
• ResNet_Model: Residual 1D-CNN model enhancing
feature propagation.

Fig. 3. The algorithm description of NetFlowClassifier.

Performance is evaluated using Accuracy, Precision, Recall,
and F1-score, along with parameter size and inference
throughput to assess deployment efficiency.

IV. EXPERIMENTS
A. Dataset Preparation
This study evaluates NetFlowClassifier on an encrypted
traffic dataset derived from CSE-CIC-IDS2018. Encrypted
flows are first filtered using protocol and port-based rules, and
redundant or non-numeric features are removed. To alleviate
severe class imbalance, a batch-based SMOTE strategy is
applied, resulting in a balanced dataset of 2,659,325 samples,
including 2,005,733 benign and 653,592 malicious flows. The
dataset is then divided into training, validation, and testing
subsets with an 8:1:1 stratified split. Detailed information on the
data partition is presented in Table 1.
TABLE I.

D. Performance Comparison
Table 2 summarizes the performance of all models.
NetFlowClassifier achieves the best overall performance with an
Accuracy of 96.61% and F1-score of 0.9652, outperforming
Basic1DCNN and ResNet_Model by 1.49% and 0.49% in
accuracy, respectively. It also significantly improves malicious
traffic detection capability compared to all baselines.
TABLE II.
Model

DATASET PARTITION OF THE CSE-CIC-IDS2018 ENCRYPTED
TRAFFIC DATASET

Dataset

Training
Set

Validation
Set

Testing Set

Total

CSE-CICIDS2018

2,127,460

265,933

265,932

2,659,325

PERFORMANCE COMPARISON OF DIFFERENT MODELS
Accuracy
(%)

Weighted
Precision

Weighted
Recall

Weighted
F1-score

SVM

85.55

0.8716

0.8555

0.8339

Basic1DCNN

95.12

0.9531

0.9512

0.9515

ResNet_Model

96.12

0.9627

0.9612

0.9601

NetFlowClassifier

96.61

0.9674

0.9661

0.9652

These performance advantages stem from the model's core
innovations: the multi-scale depthwise separable convolution
module captures local discriminative features of varying
granularities; the improved Transformer encoder strengthens the
extraction of long-range feature dependencies; and the learnable

B. Experimental Environment and Hyperparameters Settings
In terms of training hyperparameters, the model was trained
for a total of 50 epochs with a mini-batch size of 128 to balance
gradient stability and training speed. The initial learning rate was

107
Authorized licensed use limited to: National Institute of Technology- Delhi. Downloaded on May 18,2026 at 09:53:54 UTC from IEEE Xplore. Restrictions apply.

feature position encoding and attention-weighted pooling enable
dynamic focus on key malicious indicators.

balance between detection accuracy and deployment efficiency,
making it suitable for resource-constrained edge environments.

Despite its hybrid architecture, the NetFlowClassifier
maintains a lightweight design with only 11.2 million
parameters—achieved through depthwise separable convolution
and optimized Transformer layers. It delivers an inference
throughput of 128 samples per second.

Future work will focus on extending the dataset to include
emerging encrypted protocols and real-world traffic traces,
improving model interpretability through attention visualization
and feature attribution, and further exploring multi-class attack
classification and federated learning frameworks to enhance
privacy preservation and cross-domain generalization.

E. Ablation Experiment
An ablation experiment is conducted by removing the multiscale convolution module while retaining the Transformer
encoder and feature enhancement components. The results of the
ablation experiment are presented in Table 3.
TABLE III.
Model
Transformeronly
NetFlowClas
sifier

ACKNOWLEDGMENT
This work was supported by State Grid Gansu Electric Power
Company under the project “Research on Access, Data
Transmission, and Security Awareness Technologies for
Firefighting Internet of Things Devices” (Project No.
52272225001V).

THE RESULTS OF THE ABLATION EXPERIMENT
Benign
(Precision/
Recall/F1score)
0.9526/0.99
38/0.9728
0.9566/0.99
96/0.9780

Malicious
(Precision/
Recall/F1score)
0.9817/0.84
29/0.9076
0.9997/0.86
31/0.9259

Overall
Accuracy
(%)

Weighted
F1-score

95.74

0.9576

96.61

0.9652

REFERENCES
[1]

[2]

The ablated model shows a noticeable performance
degradation, with overall accuracy decreasing to 95.74% and
weighted F1-score dropping to 0.9576, confirming that multiscale convolution plays a critical role in capturing fine-grained
malicious traffic patterns that cannot be sufficiently modeled by
self-attention alone.

[3]

[4]

V. CONCLUSION
This paper proposes NetFlowClassifier, a lightweight hybrid
deep learning framework for malicious encrypted traffic
identification. By integrating multi-scale depthwise separable
convolution with an improved Transformer encoder, together
with learnable feature position encoding and attention-weighted
pooling, the proposed model effectively addresses the
limitations of existing approaches in multi-scale feature
extraction and long-range dependency modeling.

[5]

[6]
[7]

Experiments conducted on the processed CSE-CIC-IDS2018
encrypted traffic dataset demonstrate that NetFlowClassifier
achieves an F1-score of 0.966, outperforming representative
CNN- and Transformer-based baselines while maintaining a
lightweight architecture with only 11.2 million parameters and
an inference throughput of 128 samples per second. These
results confirm that the proposed model provides a favorable

[8]
[9]

G. Aceto, D. Ciuonzo, A. Montieri and A. Pescapé, "Mobile Encrypted
Traffic Classification Using Deep Learning,"2018 Network Traffic
Measurement and Analysis Conference (TMA), Vienna, Austria, 2018,
pp. 1-8, doi: 10.23919/TMA.2018.8506558.
Lotfollahi, M., Jafari Siavoshani, M., Shirali Hossein Zade, R., &
Saberian, M. (2017). Deep packet: a novel approach for encrypted traffic
classification using deep learning. Soft Computing, 24, 1999 - 2012.
Pathmaperuma, M. H., Rahulamathavan, Y., Dogan, S., & Kondoz, A. M.
(2022). Deep Learning for Encrypted Traffic Classification and Unknown
Data
Detection.
Sensors,
22(19),
7643.
https://doi.org/10.3390/s22197643.
Mei Y, Luktarhan N, Zhao G, Yang X. An Encrypted Traffic
Classification Approach Based on Path Signature Features and LSTM.
Electronics.
2024;
13(15):3060.
https://doi.org/10.3390/electronics13153060.
Lin, X., Xiong, G., Gou, G., Li, Z., Shi, J., & Yu, J. (2022). ET-BERT: A
Contextualized Datagram Representation with Pre-training Transformers
for Encrypted Traffic Classification. WWW 2022 - Proceedings of the
ACM
Web
Conference
2022,
633–642.
https://doi.org/10.1145/3485447.3512217.
Chen, Xu-Yang, et al. "MIETT: Multi-Instance Encrypted Traffic
Transformer for Encrypted Traffic Classification." Proceedings of the
AAAI Conference on Artificial Intelligence. Vol. 39. No. 15. 2025.
Shi Z, Luktarhan N, Song Y, Tian G. BFCN: A Novel Classification
Method of Encrypted Traffic Based on BERT and CNN. Electronics.
2023; 12(3):516. https://doi.org/10.3390/electronics12030516.
Lu B, Luktarhan N, Ding C, Zhang W. ICLSTM: Encrypted Traffic
Service Identification Based on Inception-LSTM Neural Network.
Symmetry. 2021; 13(6):1080. https://doi.org/10.3390/sym13061080.
Zhao, D., Jiang, B., Liu, Y., & Chen, Q. (2025). Language of Network: A
Generative Pre-trained Model for Encrypted Traffic Comprehension.
arXiv preprint arXiv:2505.19482.

108
Authorized licensed use limited to: National Institute of Technology- Delhi. Downloaded on May 18,2026 at 09:53:54 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
