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
# [294] SaRLog: Semantic-Aware Robust Log Anomaly Detection via BERT-Augmented Contrastive Learning
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
编号：294
题名：SaRLog: Semantic-Aware Robust Log Anomaly Detection via BERT-Augmented Contrastive Learning
年份：2024
DOI：10.1109/jiot.2024.3386183
来源：IEEE Internet of Things Journal
PDF：paper/10.1109_JIOT.2024.3386183.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：时序、日志、KPI 与云原生异常检测、入侵检测与网络异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\294.txt
- 原始字符数：46502
- 本次发送字符数：46502
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE INTERNET OF THINGS JOURNAL, VOL. 11, NO. 13, 1 JULY 2024

23727

SaRLog: Semantic-Aware Robust Log Anomaly
Detection via BERT-Augmented
Contrastive Learning
Lelisa Adeba Jilcha , Deuk-Hun Kim , and Jin Kwak , Member, IEEE

Abstract—Numerous deep learning-based methods have been
developed to address the intricacies of anomaly detection tasks
within system logs, presenting two significant challenges. First,
balancing model complexity with the capacity to generate semantically meaningful representations for the downstream detection
model, is a delicate task. Second, these methods generally depend
on extensive labeled data for effective training. Despite efforts
to address these challenges separately, a comprehensive solution
that efficiently tackles both issues simultaneously are lacking. In
response, we introduce Semantic-aware Robust Log (SaRLog),
a comprehensive solution designed to overcome the limitations
of existing methods by leveraging the contextual semantic
information extraction capability of bidirectional encoder representations from transformers (BERTs) and the few-shot learning
capability of the Siamese network. The Siamese network, featured
with contractive loss, is implemented on top of a custom domainspecific fine-tuned BERT. Our comparative analysis validates
SaRLog’s effectiveness against established baseline methods,
demonstrating F1 score improvement of up to 31.2% and 46.7%
on BGL and Thunderbird data sets, respectively. Moreover,
additional experimental analysis aimed at evaluating the few-shot
learning capability highlights the robustness and generalization
efficiency of SaRLog. Thus, by overcoming data set variability
and improving model generalization, SaRLog advances log
anomaly detection, thereby effectively handling complex log data
challenges.
Index Terms—Anomaly detection, bidirectional encoder representations from transformer (BERT), contrastive loss, Internet
of Things (IoT), log preprocessing, pretrained language model
(PLM), Siamese network.

I. I NTRODUCTION

W

ITHIN the contemporary landscape marked by the
convergence of the Internet of Things (IoT) and cloud

Manuscript received 12 February 2024; revised 22 March 2024; accepted
3 April 2024. Date of publication 8 April 2024; date of current version
26 June 2024. This work was supported in part by the National Research
Foundation of Korea (NRF) Grant funded by the Korean Government (MSIT)
under Grant 2021R1A2C2011391, and in part by the Institute of Information
and Communications Technology Planning and Evaluation (IITP) Grant
funded by the Korea Government (MSIT) through Development of Security by
Design and Security Management Technology in Smart Factory under Grant
2021-0-01806. (Corresponding author: Jin Kwak.)
Lelisa Adeba Jilcha is with ISAA Laboratory, Department of AI
Convergence Network, Ajou University, Suwon 16499, South Korea (e-mail:
jilchalelisa@ajou.ac.kr).
Deuk-Hun Kim is with ISAA Laboratory, Institute for Computing and
Informatics Research, Ajou University, Suwon 16499, South Korea (e-mail:
dhkim.isaa@gmail.com).
Jin Kwak is with the Department of Cybersecurity, Ajou University, Suwon
16499, South Korea (e-mail: security@ajou.ac.kr).
Digital Object Identifier 10.1109/JIOT.2024.3386183

computing [1], log anomaly detection has emerged as pivotal
for maintaining the integrity and security of complex, distributed systems [2]. With connected IoT devices projected to
number 55.7 billion by 2025 potentially generating approximately 80 zettabytes of data [3], the efficient management,
analysis, and interpretation of log data becomes critical to
guarantee that interconnected systems operate reliably and
securely. Automated log anomaly detection systems, particularly those powered by deep learning technologies, are
essential tools, offering a swift and sophisticated means for
identifying and addressing potential threats and anomalies
within vast networks [4]. This technological synergy enhances
the precision and speed at which anomalies are detected,
significantly reducing the risk of system failures and cybersecurity threats.
Log messages, often denoted as logs, are semi-structured
records of events occurring within a system, application,
or device [5], [6]. These records, generated to capture
information about the system’s behavior, errors, warnings,
and other relevant activities, are crucial for detecting security
breaches, software errors, system faults, and performance
issues [3]. At the core of the log message is an unstructured statement, formulated during the software development
process, comprising constant and variable parameters [6].
The constant part discloses the event template, while the
variable parts contain parameters that convey dynamic runtime
information.
A central aspect shared among existing log anomaly detection methodologies is log parsing [7], [8], [9], a technique
that translates each log message into its specific static event
template with associated variable parameters. This is followed by the construction of log sequences [8], [10], [11]
and the transformation of these sequences into vector representations [11], [12], [13], which are subsequently fed into
downstream anomaly detection models. Previous studies predominantly utilized static embedding techniques, such as
word2vec and FastText for constructing vector representations [8], [11], [14]. However, these methods often neglect
the semantic information inherent in raw log messages, thus
decreasing the detection system’s robustness. Recent studies
indicate a shift toward using pretrained language models
(PLMs), such as bidirectional encoder representations from
transformers (BERTs) and generative pretrained transformers
(GPTs) for generating representation vectors for the downstream detection task [11], [12], [13]. This shift highlights

c 2024 The Authors. This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 License.

For more information, see https://creativecommons.org/licenses/by-nc-nd/4.0/

23728

IEEE INTERNET OF THINGS JOURNAL, VOL. 11, NO. 13, 1 JULY 2024

the importance of capturing semantic contextual information
present in log data, a crucial element in improving the
performance of log-based anomaly detection systems.
Nonetheless, these off-the-shelf PLMs present certain limitations when applied to domain-specific tasks such as intrusion
detection [15], [16]. The primary challenge stems from their
limited understanding of specialized terminologies within the
domain. Section III discusses this issue in the context of
log anomaly detection. Moreover, the diverse distributional
and structural characteristics of log data across different
data sets (Section III), combined with the challenges of
acquiring sufficient training data [17], emphasize the necessity
for developing robust detection systems capable of reliably
managing both environmental and data drift, thus ensuring
their effectiveness across various contexts and data sets.
In response, we introduce a contrastive learning-based log
anomaly detection method named Semantic-aware Robust Log
(SaRLog) anomaly detection, leveraging a domain-specific
fine-tuned PLM and a custom Siamese network.
The key contributions of this work lie in the innovative approach to addressing two critical challenges. First,
the proposed model effectively balances the model’s overall
complexity and efficient representation, combining contextual semantic representations’ capability of a domain-specific
pretrained BERT-based language model with the few-shot
learning capability of a Siamese architecture. Second, the
use of contractive loss and a fine-tuned domain-specific representation model enhances adaptability to rare and subtle
anomalies, thereby reducing dependence on extensive labeled
data sets. Furthermore, through rigorous experimental analysis
on the BGL and Thunderbird data sets, SaRLog demonstrated
superior performance compared to baseline methods, achieving remarkable F1-scores of 0.9880 and 0.9993, respectively.
By addressing the challenges posed by data set variability
and enhancing model generalization, SaRLog contributes to
the advancement of anomaly detection solutions capable of
effectively navigating the complexities of diverse log data.
This article is structured as follows. Section II reviews
prior studies on common approaches in log anomaly detection,
covering log parsing, representation, and detection. Section III
addresses challenges in pretraining language models on log
data and examines the potential advantages of domain-specific
PLMs. Section IV presents technical details of the proposed
model, including preprocessing, context-aware semantic representation, and contrastive learning-based detection. Evaluation
results and comparisons with baseline methods are discussed
in Section V. Limitations and future research directions are
outlined in Section VI. Finally, Section VII offers concluding
remarks.
II. R ELATED W ORKS
Several existing log-based anomaly detection approaches
rely on effective log parsing methods [18], [19], [20],
[21] to extract structured event templates from raw log
data [7], [8], [9]. IPLOM [18] utilizes hierarchical clustering
alongside heuristic strategies, such as grouping by log length
and word position, and employing word mapping relationships

to enhance parsing accuracy. Similarly, SLCT [19] introduces a clustering algorithm that identifies frequent words
in log content, facilitating parsing through frequency-based
clustering. Drain [20] employs a method that leverages natural
language processing (NLP) to filter out irrelevant variables and
constructs parse trees based on the length of log messages, thus
enabling structured log template parsing. Spell [21] presents a
streaming-based parsing technique using the longest common
subsequence, enabling the extraction of structured log templates and their parameters. However, these techniques often
rely on predefined templates or patterns to parse logs, making
them less adaptable when faced with diverse and evolving log
data. Additionally, they may struggle with handling noisy or
incomplete logs, which can lead to inaccurate parsing results.
Moreover, log anomaly detection necessitates the efficient
representation of log messages, where either raw log messages
or parsed log sequences are transformed into meaningful
representation vectors. Various methods employing different neural network-based representation techniques, including
static and contextual embeddings, have been proposed.
Inspired by word2vec, static log representation methods, such
as logkey2vec [7] and Template2Vec [8] have been widely
adopted. However, these methods do not fully exploit the
rich contextual semantic information embedded within log
messages. Consequently, recent studies [11], [12], [13] have
emphasized the use of semantic and context-aware representation models, such as GPT, BERT, and RoBERTa.
Conversely, prior studies underscore the significance
of capturing temporal dependencies within log messages
for downstream detection tasks, given that anomalies are
often discerned by analyzing sequences of log events [22].
Various techniques have been developed, including
CNN-based [7], [9], [23], RNN-based [8], [10], [23], and
attention-based [8], [11], [12], [13] approaches. DeepLog [10]
utilizes LSTM to model temporal dependency for log entrylevel online anomaly detection. LogAnomaly [8] proposes
an attention-based LSTM combined with template2vector.
LogRobust [11] employs Bi-LSTM and attention mechanisms to extract bidirectional dependencies. Furthermore,
PLELog [14] and LogAT [23] tackle log anomaly detection
through semi-supervised and transfer learning, respectively,
aiming to alleviate the need for extensive manually labeled
data. However, a key limitation of these studies is their reliance
on static representation methods, which may compromise
the capture of nuanced semantic information, particularly in
complex log structures.
Furthermore, NeuralLog [12] and LAnoBERT [13] aim
to enhance robustness and generalizability in log anomaly
detection utilizing the BERT-based representation approach.
However, exploiting contextual semantic information embedded in log messages often involves complex models such
as transformers for downstream detection tasks [12], aiming to process the high-dimensional vector output of the
representation model. Despite the advantages of improved
semantic understanding, the risk of memorization is a significant concern when using complex models, such as BERT and
transformers in combination. Memorization refers to a model
learning the specifics and noise in the training data to the

JILCHA et al.: SaRLog: ANOMALY DETECTION VIA BERT-AUGMENTED CONTRASTIVE LEARNING

23729

TABLE I
D ISTRIBUTION OF THE T OP 10 W ORDS IN BGL AND T HUNDERBIRD DATA S ETS

extent that it adversely affects the model’s performance on
new, unseen data, compromising its generalization ability [24].
Hence, in this study, we propose an innovative approach that
efficiently addresses the aforementioned challenges.
III. S IGNIFICANCE OF D OMAIN -S PECIFIC L ANGUAGE
M ODEL IN L OG A NOMALY D ETECTION
Recent studies highlight the widespread adoption of BERT
and its variants for generating contextual and semantically
meaningful representations for log-based anomaly detection
tasks [11], [12], [13]. BERT is a transformer encoder-based
language model pretrained on a massive corpus of publicly available text data [25]. Given a sequence of input
tokens {xiT }ni=1 , the objective of BERT with masked language
modeling is to maximize the probability of predicting the
T and xT ,
masked tokens xiT given the surrounding context x<i
>i
as shown in the following:
P(x) = argMaxθ

n


P(xi |x<i , x>i θ )

(1)

i=1

where θ is the model’s parameters and n is sequence length.
Furthermore, BERT employs a multihead attention mechanism to enhance the training [25]. Given a sequence of
input tokens xT = {x1T , x2T , . . . , xnT }, where n is the sequence
length, the self-attention mechanism of BERT computes the
attention scores between all pairs of tokens using multiple sets
of Query (Q), Key (K), and Value (V) matrices, as shown in
(2). The self-attention mechanism is subsequently applied h
times, where h is the number of attention heads, with different
learned projection matrices and the outputs of each attention
head are concatenated and linearly transformed to obtain the
final vector. This enables BERT to capture diverse contextual
information, learn richer representations, mitigate overfitting,
and achieve better generalization on downstream NLP tasks,
such as text classification [26], named entity recognition [27],
and sentiment analysis [28]


QK T
V
(2)
Attention(Q, K.V) = SoftMax √
dk

where Q is a query matrix with dimension (n × dQ ), K is
a key matrix with dimension (n × dk ), V is a value matrix
with dimension (n × dv ), and d is the dimensionality of the
corresponding vector.
Although BERT and BERT-based PLMs have shown
impressive capabilities in various NLP tasks, their application to log-based anomaly detection presents significant
challenges [29]. Their primary limitation is that, being inherently generic, they may lack the domain-specific knowledge
essential for understanding specialized terminology found in
system logs [30]. The unique vocabulary, error codes, and
contextually relevant terms typical of system logs may not be
fully captured, leading to a suboptimal semantic representation
of log entries. For instance, terms, such as thread, driver,
kernel, and key may hold different meanings in general English
compared with their usage within log messages, illustrating
the difficulty in achieving accurate word comprehension within
the distinct linguistic context of system logs.
Moreover, system log data sets are characterized by sparsity
and comparatively short sentence lengths. Table I demonstrates the distribution of the top ten words in two publicly
available data sets, BGL and Thunderbird, following the text
cleaning process. The total counts of unique words in BGL for
normal and anomaly samples are 769 and 209, respectively,
whereas for the Thunderbird data set, these counts are 3002
and 65. Despite this, the top ten most frequent words in
the normal samples of the BGL and Thunderbird data sets
account for 50.6% and 39.65% of the total occurrences in their
corresponding class for each data set, respectively. Similarly,
the top ten most frequent words in the anomalous sample of the
BGL and Thunderbird data sets constitute 64.54% and 60.32%
of the overall anomalous samples of each data set, respectively.
Nonetheless, these data sets show minimal commonality in the
most frequent terms, with kernel being the sole term to appear
in the normal samples of both.
The observed statistical information highlights the potential
challenges associated with pretraining language models, such
as BERT [25], on system log data sets. These challenges fall
into two main categories. The first is that the limited context
provided by the small vocabulary size undermines the model’s

23730

Fig. 1.

IEEE INTERNET OF THINGS JOURNAL, VOL. 11, NO. 13, 1 JULY 2024

Overall architecture of the proposed model.

ability to capture rich contextual information, potentially
leading to suboptimal representation. The second challenge is
the skewed vocabulary coverage caused by the dominance of a
few frequent words, which may limit exposure to less common
vocabulary during pretraining, adversely affecting the model’s
ability to generalize to new words. To address this issue,
either fine-tuning models on a large corpus of log data sets
from diverse sources or utilizing pretrained models specifically
adapted to relevant target domains, such as cybersecurity is
necessary. Such approaches can enhance the model’s ability
to grasp the nuances of language and terminology present in
system logs, thereby improving performance and generalization across different log data sets.
IV. P ROPOSED M ETHOD (S A RL OG )
To enhance anomaly detection in system logs, we present
SaRLog, a method that combines domain-specific PLMs for
semantic and context-aware feature extraction with a Siamese
network employing contrastive loss for effective similarity
learning. This section provides an in-depth overview of
SaRLog’s operation, covering preprocessing, representation,
and detection procedures. Fig. 1 illustrates the overall architecture of the proposed approach.
A. Preprocessing
The preprocessing stage encompasses a text cleaning and
tokenization phase. During the cleaning phase, raw log messages are sanitized and standardized by removing irrelevant
features. The input text x undergoes a series of operations
xclean = Cleantext(x) to improve its quality prior to tokenization. This converts all characters to lowercase, removing
HTML tags, special characters, punctuation, and numerical values. For example, a raw log message, “APPREAD
1117885521 2005.06.04 R13-M1-N8-I:J18-U11 2005-06-0404.45.21.913685 R13-M1-N8-I:J18-U11 RAS APP FATAL
ciod: failed to read message prefix on control stream
(CioStream socket to 172.16.96.116:35646”, is transformed
into “appread ras app fatal ciod failed to read message prefix
on control stream ciostream socket to.”

The cleaned text, xclean , is then subjected to tokenization,
ensuring the input is devoid of noise and primed for the
extraction of semantically rich representations. We utilize
a custom tokenizer algorithm, as proposed in [15], which
segments lengthy words into smaller tokens to better manage
out-of-vocabulary (OOV) words. This tokenizer, based on the
byte pair encoding (BPE) method [31], is tailored for handling
OOV and domain-specific terms within the cybersecurity field.
This adaptation is critical for efficient log-based anomaly
detection due to potential vocabulary overlaps between system
log messages and cybersecurity texts [22]. Terms related to
network configurations, user authentication, and system events
often indicate security incidents within system logs.
Subsequently, special tokens for classification [CLS] and
separation [SEP] will be added to the resulting sequence of
tokens. The sequence is then adjusted to a uniform length
of 512 through padding or truncation, and an attention mask
is created to identify the elements within the sequence that
require attention. The final product of the preprocessing stage
is a token sequence xT = {[CLS], x1T , x2T , . . . , xTn , [SEP]},
where T denotes a token, and n represents the sequence length,
fixed at 512.
B. Context-Aware Semantic Representation
This step involves mapping the sequence of input tokens
to numerical vectors, with a deliberate emphasis on ensuring
that these vectors accurately encapsulate the semantic and
contextual nuances inherent in the respective tokens. As
discussed in Section III, BERT models pretrained on general
English text face challenges in accurately capturing the unique
linguistic context of system logs [29], [30]. To address this, we
employ SecureBERT [15], a domain-specific model that has
been fine-tuned on a substantial corpus of cybersecurity text.
SecureBERT features 12 hidden layers, each with an output
dimension of 768, 12 attention layers, and a feed-forward
network size of 2048, with an input size of 512.
For a given sequence of input tokens {xiT }ni=1 , the objective
of the representation model is to produce a contextual and
semantical embedding vector xe = {x1e , x2e , . . . , xen } ∈ Rd ,
where e represents embedding, n is the sequence length, and

JILCHA et al.: SaRLog: ANOMALY DETECTION VIA BERT-AUGMENTED CONTRASTIVE LEARNING

d is the dimensionality of each embedding vector, set at 768.
In our study, we specifically leveraged the word embeddings
output by the last encoder layer to produce a comprehensive
representation, xr , for a given log message. We adopted a
straightforward aggregation method, specifically, calculating
the arithmetic mean of the resulting word embeddings {xie }ni=1
across all words in the log message, as shown in (3). This
aggregation approach enables the distillation of semantic
information from individual word embeddings into a unified
representation for the entire log message, thereby enhancing
the effectiveness of the subsequent anomaly detection task
1 e
xi
n
n

xr =

(3)

i=1

where xr is the final representation vector, n is the sequence
length, and xie is the word embedding for the ith word in the
log message.
C. Contrastive Learning-Based Detection
Given a pair of input vectors x1r and x2r , encapsulating rich
semantic information captured by the representation model,
and a Siamese network with a shared trainable parameter θ ,
the training objective is to optimize θ such that the similarity
metric S(xr1 , x1r ) identifies patterns indicative of the similarity
or dissimilarity between the two vectors. The Siamese network
consists of two identical fully connected neural networks.
Each network had an input size of 768, corresponding to
the embedding dimension of the representation model, and
included two hidden layers of sizes 64 and 32 with ReLU
activation functions, culminating in an output layer of size
1. For implementation, a single network was constructed
and utilized sequentially for both pairs of input data. To
avoid confusion, we refer to these as subnetworks 1 and 2,
respectively. Each subnetwork is represented by the embedding
function fθ (x1r ) = E(x1r , θ ) and fθ (x2r ) = E(x2r , θ ), where
E denotes embedding, and θ denotes the shared trainable
parameter, Fig. 1. The similarity metric S computes the geometric relationship between numerical vectors derived from
the embedding functions, as shown in (4). Furthermore, a
multiplexer module, acting as a pooling layer, was designed
that efficiently presents input pairs to the network, along with
corresponding labels indicating their similarity or dissimilarity,
as shown in Fig. 1

  
 

(4)
S x1r , x2r = sim fθ x1r , fθ x2r .
A contrastive loss function, as formulated in (5), was
employed to refine the training objective, optimizing the model
to reduce the distance between embeddings of similar inputs
while increasing the distance between embeddings of dissimilar inputs. Throughout the training process, the parameter θ
is updated concurrently for both subnetworks, ensuring the
acquisition of discriminative features. These features enable
the network to generate efficient embeddings for both inputs.
The Euclidean distance d between the two embeddings is
calculated, and the contrastive loss is then determined based
on a margin parameter m and the Euclidean distance d,
as expressed in (5). The margin parameter m establishes

23731

a threshold delineating the proximity or disparity required
between the embeddings of similar and dissimilar samples
1
1
∗ d2 + y ∗ ∗ max(0, m − d)2 (5)
2
2
where y is the binary label, 1 for similar inputs with 0 for
dissimilar inputs, and d is the Euclidian distance between the
embeddings of x1 and x2 .
The right-hand side of (5) is designed to minimize the distance between embeddings of similar pairs, imposing penalties
for larger distances, thus fostering proximity. Conversely, the
left side of the equation motivates the embeddings of dissimilar
pairs to maintain a separation of at least m. If the distance d
exceeds m, further adjustment for that pair is unnecessary, as
the loss becomes zero. During the training phase, the objective
is to reduce the aggregate contrastive loss across all input pairs
within the training data set, as expressed in (6). In the testing
phase, each sample from the test data set is compared with
a reference data point from the normal samples. A sample
is anomalous if the distance between the two pairs surpasses
the predefined margin parameter m; otherwise, it is deemed
normal
L(y, d) = (1 − y) ∗

1
L(yi di )
N
N

J=

(6)

i=1

where N is the total number of pairs in the training data set,
with yi and di , respectively, corresponding to the binary label
and the distance for the ith pair.
V. E XPERIMENTAL A NALYSIS
The experimental analysis, performed on the BGL and
Thunderbird data sets, showcases the superior performance
of the proposed approach (SaRLog) compared to baseline
methods. This section provides an in-depth assessment of
the model’s performance across several dimensions, including the efficacy of the representation model, the model’s
performance in few-shot learning scenarios, and its comparative performance against baseline models.
A. Experimental Setting
The experimental analysis utilized Visual Studio Code
alongside the PyTorch framework for machine learning tasks
and Python 3.11 for coding and experimentation. The experiments were conducted on a high-performance workstation
equipped with a 64-bit Ubuntu 22.04.3 LTS OS, powered
by an Intel Xeon Gold 5122 CPU @ 3.60 GHz with 8
cores, 128 GB of RAM, and an NVIDIA Quadro P5000
GPU. The training phase spanned ten epochs, incorporating a 20% dropout rate, using the Adam optimizer with
a learning rate of 0.01, and binary cross-entropy with logits (BCEWithLogitsLoss) served as the loss function. The
task of log anomaly detection was approached as a binary
classification problem, with the model’s performance being
assessed via precision, recall, and the F1-score. Precision =
(TP/TP + FP ), Recall = (TP/TP + FN), and F1 −
score = 2([Precision ∗ Recall]/[Precision + Recall]) ,
where TP = true positive, FP = false Positive, and FN = false

23732

IEEE INTERNET OF THINGS JOURNAL, VOL. 11, NO. 13, 1 JULY 2024

TABLE II
S TATISTICAL I NFORMATION OF THE DATA S ETS

negative. These measures provide a quantifiable evaluation
of the proposed model’s effectiveness and facilitate a fair
comparison with baseline methods.
B. Data Sets
The proposed model’s performance and its comparison with
prior approaches were evaluated using two publicly available
data sets: 1) BGL and 2) Thunderbird [6]. This section introduces these data sets and relevant statistical information,
contributing to an understanding of their scope and the context
of the experimental analysis. Additionally, Table II presents
detailed statistical data pertaining to the portions of the data
set utilized for training and testing.
The BGL data set originates from a supercomputing system
and comprises 4 747 963 log messages that were collected
by the Lawrence Livermore National Laboratory (LLNL) [6].
Each message within this data set has been manually classified
as either normal or anomalous, with 348 460 identified as
anomalous. Similarly, the Thunderbird data set [6] includes
a total of 44 841 030 entries, consisting of 41 592 791 alerts
and 3 248 239 nonalerts. This data set was sourced from the
Thunderbird supercomputer system at the Sandia National
Laboratories (SNL). The detailed presentation of these data
sets provides researchers with a foundation for understanding
the experimental setup and the basis for a fair comparison with
existing methods.
C. Comparative Analysis: Proposed Model Versus Baseline
Methods
We conducted a comparative analysis to evaluate the
performance of SaRLog against established baseline methods, with the objective of determining its performance in
accomplishing the target task. The proposed model exhibited
remarkable achievement across both data sets, achieving an
F1-score of 0.988 on BGL and 0.999 on Thunderbird. These
outcomes signify substantial enhancements over the baseline
methods, marking improvements of up to 31.2% and 46.7%,
respectively, as shown in Table III.
Although NeuralLog [12] achieves a performance level
comparable to SaRLog with an F1-score of 0.985 on the
BGL data set, it marginally lags on the Thunderbird data
set, with an F1-score of 0.964, which is 3.5% lower.
LogAnomaly [8] and LogRobust [11] exhibit considerable
fluctuations in performance between the two data sets.
Specifically, LogAnomaly’s F1-score shows a sharp decline
of 28.9% when transitioning from BGL to Thunderbird,
whereas LogRobust’s F1-score maintains relative stability,

witnessing only a 9.6% reduction, albeit starting from a
lower performance benchmark. Furthermore, PLELog [14]
lags behind SARLog on both data sets. SARLog shows a
0.6% F1-score improvement over PLELog for the BGL data
set and a 13.4% improvement for the Thunderbird data set.
These numerical differences highlight the proposed method’s
robustness and dependability in anomaly detection tasks across
diverse data sets.
D. Performance of the Detection Head
In our exploration of different architectures for anomaly
detection, we observed a remarkable difference in training
loss convergence rates between the Siamese network and
a multilayer fully connected network, both configured with
an equivalent level of model complexity regarding trainable
parameters. Specifically, the Siamese network attained convergence within the initial four epochs, as depicted in Fig. 2(b),
whereas the fully connected network required at least 150
epochs to reach a similar state of convergence, as shown
in Fig. 2(a). This result validates the expected decrease in
computational complexity and training time associated with
utilizing similarity-based learning approaches.
E. Performance of the Representation Model
BERT, renowned for its capacity to grasp contextualized
representations and nuanced features, affords a profound
comprehension of the input data (Section III). Nonetheless, its
generated embeddings may not always exhibit the distinct separability requisite for anomaly detection in specific contexts.
This characteristic of BERT embeddings can be attributed
to the model’s sophisticated architecture and its method of
learning contextualized representations, which could lead to
overlapping embedding spaces, as illustrated in Fig. 3(a). In
contrast, the custom Siamese network, specifically tailored
to discern similarity relationships, produces a more discernible embedding structure when applied in conjunction with
BERT’s output, as demonstrated in Fig. 3(b). Consequently,
this approach simplifies the classification process through the
application of straightforward distance metrics, such as cosine
or Euclidean distance.
Additionally, empirical analyses were conducted to examine
the impact of different representation architectures on the
effectiveness of the downstream detection task. Table IV
presents the outcomes of model performance employing different representation architectures. The findings highlight the
promising performance of domain-specific PLMs, underscoring their efficacy in enhancing the accuracy and efficiency in
anomaly detection tasks.
Among the examined embedding architectures, Word2vec
demonstrated the lowest performance, yielding an F1-score
of 0.885 on BGL and 0.873 on Thunderbird. This outcome
suggests its comparatively limited effectiveness compared
with more advanced models. GPT-2 exhibits a noteworthy
improvement in performance, particularly on the Thunderbird
data set, achieving an F1-score of 0.971. BERT delivered
strong results on BGL, attaining an F1-score of 0.963.

JILCHA et al.: SaRLog: ANOMALY DETECTION VIA BERT-AUGMENTED CONTRASTIVE LEARNING

23733

TABLE III
P ERFORMANCE OF S A L OG AGAINST BASELINE M ETHODS

Fig. 2.
Loss curve trajectory. (a) When using a fully connected neural
network-based head and trained for 250 epochs. (b) When using Siamese
network head and trained only for 10 epochs.

Conversely, RoBERTa and SecureBERT emerge as standout
performers, particularly on the Thunderbird data set, where
they both achieved nearly perfect F1-score of 0.999. This
indicates that these embeddings offer a more nuanced representation, substantially enhancing the model’s capacity for
generalization and accurate predictions across diverse data

Fig. 3.
PCA illustration of the representation vector. (a) BERT hidden
layer and (b) output layer of siamese network.

sets. On the BGL data set, RoBERTa and SecureBERT also
exhibit robust performance, with F1-scores of 0.973 and
0.988, respectively, further affirming their superiority within

23734

IEEE INTERNET OF THINGS JOURNAL, VOL. 11, NO. 13, 1 JULY 2024

TABLE IV
P ERFORMANCE OF S A RL OG W HEN U SING D IFFERENT
E MBEDDING A RCHITECTURE

(a)

(b)
Fig. 4. Few-shot performance of SaRLog. Trained on the BGL data set
and tested on the Thunderbird data set (orange). Trained on Thunderbird and
tested on BGL (blue).

the proposed architecture. Overall, SecureBERT consistently
outperforms other architectures on both data sets, positioning it
as a potentially effective embedding architecture among those
considered in the evaluation.

Fig. 5. Zero-shot performance of SaRLog. (a) Trained on the Thunderbird
data set and tested on the BGL data set and (b) trained on BGL and tested
on Thunderbird.

of examples from the BGL data set and testing on the BGLtest data set, it achieves a slightly higher F1-score of 0.933.
These results highlight the model’s capacity to generalize and
perform effectively with a limited number of examples from
a different domain, highlighting its adaptability in few-shot
learning scenarios.

F. Few-Shot Learning Performance of SaRLog
This section discusses the few-shot performance of the
model in two distinct scenarios. The evaluation entails training
the model on one data set and subsequently conducting testing
on an entirely new data set, following retraining the model
with only a few examples from the new data set. Fig. 4
shows the performance outcomes, where “TB-BGL” denotes
training on Thunderbird and testing on BGL, while “BGL-TB”
signifies the reverse scenario.
In the first scenario, where the model initially undergoes
training on the BGL data set, followed by retraining on a
subset of examples from the Thunderbird-training data set,
and ultimately testing on the Thunderbird-testing data set,
it achieves an F1 score of 0.871. Conversely, in the second
scenario, where the model is exclusively trained and tested on
the Thunderbird data set, followed by retraining with a subset

VI. D ISCUSSION
The proposed model, SaRLog, demonstrates superior
performance when compared with baseline methods in both
full-training and few-shot learning scenarios. However, when
subjected to the zero-shot learning setting, where the model is
trained on one data set and tested on an entirely different one,
a significant drop in performance is observed, as illustrated in
Fig. 5. This decline can be attributed to structural and distributional variations among log data sets (discussed in Section III),
which introduce ambiguity during the representation phase.
Notably, the decrease in F1-score from 0.988 to 0.184 when
trained on BGL and tested on Thunderbird [Fig. 5(b)], and
vice versa from 0.999 to 0.134 [Fig. 5(a)], highlights the
substantial impact of environment drift on model performance.
However, the incorporation of domain-specific PLMs such as

JILCHA et al.: SaRLog: ANOMALY DETECTION VIA BERT-AUGMENTED CONTRASTIVE LEARNING

SecureBERT yields a slight improvement in performance in
both cases, emphasizing the advantages of leveraging domainspecific representations.
To address these challenges fully, future research should prioritize customizing the tokenization process to accommodate
domain-specific vocabulary and exploring subtle features that
may be common across data sets. Additionally, robust domain
adaptation methods should be explored to enhance the model’s
capacity to generalize to unseen data distributions. These
endeavors will contribute to the development of more resilient
anomaly detection models capable of effectively handling
variations in environment and data set characteristics.
VII. C ONCLUSION
This study addresses significant challenges in anomaly
detection within system logs, with a particular emphasis on
striking the delicate balance between model complexity and
semantic representation efficacy, while reducing the reliance
on extensive labeled data. Despite individual efforts to tackle
these challenges, a comprehensive solution has remained
elusive. The proposed method, SaRLog, bridges this gap by
leveraging the semantic information extraction capabilities of
BERT and the few-shot learning ability of a Siamese network.
Through rigorous experimental analysis conducted on the
BGL and Thunderbird data sets, SaRLog established its superiority when compared with state-of-the-art methods. It achieved
remarkable F1-scores of 0.9880 and 0.9993, respectively, on
these data sets. The few-shot learning capability of SaRLog
highlights its adaptability and robustness, positioning it as a
promising approach for anomaly detection in dynamic and
evolving environments. Future research endeavors will be
directed toward devising strategies to mitigate the impact
of structural and distributional variations in log data sets
and exploring robust domain adaptation methods to enhance
model generalization, particularly in the zero-shot learning
paradigm. These endeavors will contribute to the advancement
of anomaly detection solutions that effectively address the
challenges posed by diverse and dynamic characteristics of log
data.
R EFERENCES
[1] M. A. Razzaque, M. Milojevic-Jevric, A. Palade, and S. Clarke,
“Middleware for Internet of Things: A survey,” IEEE Internet Things
J., vol. 3, no. 1, pp. 70–95, Feb. 2016.
[2] A. A. Cook, G. Mısırlı, and Z. Fan, “Anomaly detection for IoT
time-series data: A survey,” IEEE Internet Things J., vol. 7, no. 7,
pp. 6481–6494, Jul. 2020.
[3] J. Lou, Q. Fu, S. Yang, Y. Xu, and J. Li, “Mining invariants from
console logs for system problem detection,” in Proc. USENIX Annu.
Techn. Conf., 2010, p. 24.
[4] J. Hojlo (Int. Data Corp., Needham, MA, USA). Future of Industry
Ecosystems: Shared Data and Insights, Jan. 2021. [Online]. Available:
https://blogs.idc.com/2021/01/06/future-of-industry-ecosystems-shareddata-and-insights
[5] A. Oliner and J. Stearley, “What supercomputers say: A study of five
system logs,” in Proc. 37th Annu. IEEE/IFIP Int. Conf. Dependable Syst.
Netw., 2007, pp. 575–584.
[6] S. He, J. Zhu, P. He, J. Liu, and M. R. Lyu, “Loghub: A large
collection of system log datasets towards automated log analytics,” 2020,
arXiv:2008.06448.

23735

[7] S. Lu, X. Wei, Y. Li, and L. Wang, “Detecting anomaly in big data
system logs using convolutional neural network,” in Proc. IEEE 16th Int.
Conf. Dependable Auton. Secur. Comput. 16th Int. Conf. Pervasive Intell.
Comput. 4th Int. Conf. Big Data Intell. Comput. Cyber Sci. Technol.
Cong., 2018, pp. 159–165.
[8] W. Meng et al., “LogAnomaly: Unsupervised detection of sequential
and quantitative anomalies in unstructured logs,” in Proc. 28th Int. Joint
Conf. Artif. Intell., vol. 7, 2019, pp. 4739–4745.
[9] Z. Wang, J. Tian, H. Fang, L. Chen, and J. Qin, “LightLog: A
lightweight temporal convolutional network for log anomaly detection
on the edge,” Comput. Netw., vol. 203, Feb. 2022, Art. no. 108616.
[10] M. Du, F. Li, G. Zheng, and V. Srikumar, “DeepLog: Anomaly detection
and diagnosis from system logs through deep learning,” in Proc. ACM
SIGSAC Conf. Comput. Commun. Secur., 2017, pp. 1285–1298.
[11] X. Zhang et al., “Robust log-based anomaly detection on unstable log
data,” in Proc. 27th ACM Joint Meeting Eur. Softw. Eng. Conf. Symp.
Found. Softw. Eng., 2019, pp. 807–817.
[12] V.-H. Le and H. Zhang, “Log-based anomaly detection without log
parsing,” in Proc. IEEE/ACM 36th Int. Conf. Autom. Softw. Eng., 2021,
pp. 492–504.
[13] Y. Lee, J. Kim, and P. Kang, “LanoBERT: System log anomaly detection
based on BERT masked language model,” 2021, arXiv:2111.09564.
[14] L. Yang et al., “Semi-supervised log-based anomaly detection via
probabilistic label estimation,” in Proc. IEEE/ACM 43rd Int. Conf. Softw.
Eng., 2021, pp. 230–231.
[15] E. Aghaei, X. Niu, W. Shadid, and E. Al-Shaer, “SecureBERT: A
domain-specific language model for cybersecurity,” in Proc. Int. Conf.
Secur. Priv. Commun. Syst., 2022, pp. 39–56.
[16] P. Ranade, A. Piplai, A. Joshi, and T. Finin, “CyBERT: Contextualized
embeddings for the cybersecurity domain,” Proc. IEEE Int. Conf. Big
Data (Big Data), 2021, pp. 3334–3342.
[17] L. Yan, C. Luo, and R. Shao, “Discrete log anomaly detection: A novel
time-aware graph-based link prediction approach,” Inf. Sci, vol. 647,
Nov. 2023, Art. no. 119576.
[18] A. Makanju, A. N. Zincir-Heywood, and E. E. Milios, “Clustering event
logs using iterative partitioning,” Proc. 15th ACM SIGKDD Int. Conf.
Knowl. Discov. Data Min., 2009, pp. 1255–1264.
[19] R. Vaarandi, “A data clustering algorithm for mining patterns from event
logs,” in Proc. IEEE Workshop IP Oper. Manag., 2003, pp. 119–126.
[20] P. He, J. Zhu, Z. Zheng, and M. R. Lyu, “Drain: An online log parsing
approach with fixed depth tree,” in Proc. IEEE Int. Conf. Web Services
(ICWS), 2017, pp. 33–40.
[21] M. Du and F. Li, “Spell: Streaming parsing of system event
logs,” in Proc. IEEE 16th Int. Conf. Data Min., 2016, pp. 859–864.
[22] M. Landauer, F. Skopik, M. Wurzenberger, and A. Rauber, “System
log clustering approaches for cyber security applications: A survey,” Comput. Secur., vol. 92, May 2020, Art. no. 101739.
[23] Y. Xie and K. Yang, “Domain adaptive log anomaly prediction
for hadoop system,” IEEE Internet Things J., vol. 9, no. 20,
pp. 20778–20787, Oct. 2022.
[24] K. Tirumala, A. Markosyan, L. Zettlemoyer, and A. Aghajanyan,
“Memorization without overfitting: Analyzing the training dynamics of
large language models,” in Proc. Adv. Neural Inf. Process. Syst., vol. 35,
2022, pp. 38274–38290.
[25] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT:
Pre-training of deep bidirectional transformers for language understanding,” in Proc. Conf. North Amer. Chapter Assoc. Comput. Linguist.,
2019, pp. 4171–4186.
[26] S. González-Carvajal and E. C. Garrido-Merchán, “Comparing
bert against traditional machine learning text classification,” 2020,
arXiv:2005.13012.
[27] C. Liang et al., “BOND: BERT-assisted open-domain named entity
recognition with distant supervision,” in Proc. 26th ACM SIGKDD Int.
Conf. Knowl. Discov. Data Min., 2020, pp. 1054–1064,
[28] H. Xu, B. Liu, L. Shu, and P. S. Yu, “Bert post-training for review
reading comprehension and aspect-based sentiment analysis,” 2019,
arXiv:1904.02232.
[29] C. Almodovar, F. Sabrina, S. Karimi, and S. Azad, “Can language
models help in system security? Investigating log anomaly detection
using BERT,” in Proc. 20th Annu. Workshop Australas. Lang. Technol.
Assoc., 2022, pp. 139–147.
[30] S. Chen and H. Liao, “BERT-log: Anomaly detection for system logs
based on pre-trained language model,” Appl. Artif. Intell., vol. 36, no. 1,
pp. e2145642-1–e2145642-23, Dec. 2022.
[31] Y. Shibata et al., “Byte pair encoding: A text compression scheme that
accelerates pattern matching,” Dept. Informat., Kyushu Univ., Fukuoka,
Japan, Rep. DOI-TR-161, 1999.

23736

IEEE INTERNET OF THINGS JOURNAL, VOL. 11, NO. 13, 1 JULY 2024

Lelisa Adeba Jilcha received the B.S. degree in
electrical and computer engineering from Arbaminch
University, Arba Minch, Ethiopia, in 2015. He is
currently pursuing the M.Sc./Ph.D. degree in AI
convergence network with Ajou University, Suwon,
South Korea.
He has been working as a Cybersecurity
Researcher and a Supervisor with Information
Network Security Administration, Addis Ababa,
Ethiopia, from 2015 to 2021. His research interests
include deep learning, large language models,
intrusion detection, cloud security, and convergence security.

Deuk-Hun Kim received the B.S. and master’s degrees in information security from
Soonchunhyang University, Asan, South Korea, in
August 2013 and August 2015, respectively, and the
Doctoral degree in computer engineering from Ajou
University, Suwon, South Korea, in August 2021.
He is currently the Postdoctoral Fellow with the
Institute for Computing and Informatics Research,
Ajou University. And, he is interested in application
service security, cloud computing security, and
cryptography protocol.

Jin Kwak (Member, IEEE) received the B.S., M.S.,
and Ph.D. degrees in computer science and engineering from Sungkyunkwan University, Seoul, South
Korea, in 2000, 2003, and 2006, respectively.
He was the Deputy Director of the Ministry
of Information and Communication, Jongno, South
Korea. Also, he was a Professor with the
Department of Information Security Engineering,
Soonchunhyang University, Asan, South Korea. He
is currently a Professor with the Department of
Cyber Security, Ajou University, Suwon, South
Korea. His current research interests include cryptographic protocols, cloud
security, SOAR, and applied security services.
PAPER_TEXT
