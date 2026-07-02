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
# [405] Drift-oriented Self-evolving Encrypted Traffic Application Classification for Actual Network Environment
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
编号：405
题名：Drift-oriented Self-evolving Encrypted Traffic Application Classification for Actual Network Environment
年份：2025
DOI：10.48550/arXiv.2501.04246
来源：arXiv preprint
PDF：paper/10.48550_arXiv.2501.04246.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\405.txt
- 原始字符数：37528
- 本次发送字符数：37528
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

1

Drift-oriented Self-evolving Encrypted Traffic
Application Classification for Actual Network
Environment

arXiv:2501.04246v1 [cs.NI] 8 Jan 2025

Zihan Chen, Member, IEEE, Guang Cheng, Member, IEEE, Jinhui Li, Tian Qin, Yuyang Zhou, Member, IEEE,
Xing Luan

Abstract—Encrypted traffic classification technology is a crucial decision-making information source for network management and security protection. It has the advantages of excellent
response timeliness, large-scale data bearing, and cross-timeand-space analysis. The existing research on encrypted traffic
classification has gradually transitioned from the closed world
to the open world, and many classifier optimization and feature
engineering schemes have been proposed. However, encrypted
traffic classification has yet to be effectively applied to the actual
network environment. The main reason is that applications on the
Internet are constantly updated, including function adjustment
and version change, which brings severe feature concept drift,
resulting in rapid failure of the classifier. Hence, the entire model
must be retrained only past very fast time, with unacceptable
labeled sample constructing and model training cost. To solve
this problem, we deeply study the characteristics of Internet
application updates, associate them with feature concept drift,
and then propose self-evolving encrypted traffic classification.
We propose a feature concept drift determination method and a
drift-oriented self-evolving fine-tuning method based on the Laida
criterion to adapt to all applications that are likely to be updated.
In the case of no exact label samples, the classifier evolves through
fully fine-tuning continuously, and the time interval between
two necessary retraining is greatly extended to be applied to
the actual network environment. Experiments show that our
approach significantly improves the classification performance
of the original classifier on the following stage dataset of the
following months (9% improvement on F1-score) without any
hard-to-acquire labeled sample. Under the current experimental
environment, the life of the classifier is extended to more than
eight months.
Index Terms—Encrypted traffic classification, Concept drift,
Self-evolving fine-tuning architecture, Windowed multi-threshold
accumulation measurement

I. I NTRODUCTION

W

ITH the rise of network security and privacy protection awareness, the encryption of network traffic
has become an inevitable trend [1]. In the backbone network
environment with Tbps bandwidth, more than 95% of traffic
is encrypted, and some Internet services have reached almost
100% encrypted [2]. To solve the problem of encrypted traffic
not being matched in plaintext to support network management
and security [3], relevant research on encrypted traffic classification has been produced. Encrypted traffic classification aims
The authors are with the School of Cyber Science and Engineering,
Southeast University, Nanjing 210096, China; Purple Mountain Laboratories,
Nanjing 211111, China; Jiangsu Province Engineering Research Center of
Security for Ubiquitous Network, Nanjing 211189, China.

to use the remaining information disclosure not covered by
encryption network protocols to classify or identify descriptive
labels such as services, applications, and behaviors underneath
encrypted traffic from a macro perspective without deciphering
[4].
The existing research on encrypted traffic classification
mainly focuses on deep learning frameworks and open-world
environments, including classifier optimization and encrypted
traffic feature engineering. Classifier optimization mainly focuses on deep learning model fusion, graph neural networks
that are more suitable for expressing the interactive features of
traffic, and the introduction of the latest large language models.
These studies can better mine the distinguishing information
in the features to better approximate the upper limit of
the classification effect. Unlikely, the feature engineering of
encrypted traffic enhances the initial adaptability of features
from the perspective of increasing the upper limit of theoretical
information gain in feature space to increase the classification
performance.
However, compared with the closed-world environment,
although unknown applications and incomplete sample coverage are considered in the open-world environment, the
application update in the actual network environment should
be considered. By studying the encrypted traffic at the border
of the provincial backbone network, we find that the network
application is constantly updated. In addition, the network
environment is constantly changing, resulting in the new
encrypted traffic sample features being inconsistent with those
of the original samples in the same category. The changes are
time-persistent, continuously decreasing the trained model’s
classification effect. This phenomenon is called the concept
drift of encrypted traffic [5]. Although encrypted traffic feature
engineering can improve the initial tolerance of the method
to concept drift, the concept drift is spawned very fast [6],
resulting in the rapid failure of the classifier. The cost of
retraining a new encrypted traffic classifier is really high
due to the massive calculation and elusive labeled sample
acquirement [7]. Repeated retraining in a short period is
unacceptable in terms of computing power cost, and there is
not enough time to collect enough samples. As a result, the
encrypted traffic classification method has been challenging to
apply in the actual network environment.
To solve the above problems, we propose the self-evolving
encrypted traffic classification, which aims to resist the continuous failure of the model caused by the irresistible feature

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

concept drift through the model’s catch-up self-evolving. First,
we study the factors that cause feature concept drift in an
actual network environment, and from its universality, we
propose a drift-oriented self-evolving architecture. We propose a windowed multi-threshold accumulation measurement
method to solve the problem of concept drift determination
in this architecture. For the self-evolving of the classifier, we
introduce the Laida criterion to retrieve and label samples with
high enough Softmax confidence in the label-free prediction
process, and rely on such samples (named silver samples)
to conduct Fully Fine-Tuning (FFT), and finally significantly
extend the time interval between two necessary retraining, to
achieve the self-evolving encrypted traffic classification.
The main contributions of this paper are as follows:
• For the first time, we pay direct attention to concept drift
in encrypted traffic classification in a actual network environment, investigate its causes, and propose windowed
multi-threshold accumulation measurement method to
determine whether concept drift occurs in the current
classifier.
• We propose the self-evolving encrypted traffic classification for the first time. Aiming at the different degrees of
feature concept drift that may exist in all applications,
we introduce the Laida criterion and propose a driftoriented self-evolving fine-tuning method based on the
high-confidence silver samples continuously recovered in
the classification process, which significantly extends the
effective life cycle of the model (The current dataset can
prove to extend to 8 months, which may be longer.),
diluting the long-term deployment costs of encrypted
traffic classifications.
The structure of this paper is as follows. Section II introduces the latest research in encrypted traffic classification.
In Section III, we analyze the source of concept drift in a
actual network environment and introduce the Laida criterion
to gather silver samples. Section IV focuses on two key links in
the drift-oriented self-evolving fine-tuning of encrypted traffic.
In Section V, experiments on self-evolving classification are
carried out. Finally, the paper is summarized in Section VI.
II. R ELATED W ORK
Current research in encrypted traffic classification can be
divided into two parts: deep learning classifier optimization
and anti-concept drift feature engineering.
With the development of neural networks and deep learning technology, some researchers began using deep learning
methods to classify encrypted traffic. The most significant
advantages of deep learning are that it does not need to rely on
prior expert knowledge of feature engineering, its end-to-end
learning features can directly feed raw encrypted traffic into
the neural network for training and classification, and neural
networks have better generalization ability than traditional
machine learning methods.
The latest research on deep learning classifier optimization
focuses on the fusion of tensor-based models (I2 RNN [8])
and the introduction of graph neural network models [9]. The
advantage of tensor-based model fusion is that in the case

2

of Large Language Models (LLM), with a small volume, it
can play the advantages of different model architectures to
construct a model with better capability, which is an essential
basis for the encrypted traffic classification. To some extent,
the graph neural network uses packet interactivity in the
process of encrypted traffic transmission. It is superior to the
tensor neural network in terms of accuracy at the cost of more
calculations. However, in approaching the theoretical optimal
effect, both of them also pay a considerable performance cost.
Although some studies began to explore the explainability
[10], there is still a problem of unexplainable features [11] and
the results of automatic feature selection are only sometimes
preferred, mainly due to the non-high-dimensional optimization of features and the neglect of structural features.
On the other hand, some studies focused on anti-concept
drift feature engineering to improve the upper limit of the
model’s initial classification accuracy. At present, the most
representative studies focus on length sequence features, such
as packet length sequence features [12], multi-flow length
sequence features [7], and packet length path signature features
[3].
In summary, with the support of feature engineering, the enhanced length sequence features can resist concept drift better
than other features. However, these features are still static, and
no matter how good the feature is, it will gradually become
invalid with the continuous update of massive applications.
Static classifiers cannot keep up with the feature concept drift
caused by application updates and cannot be used in an actual
network environment.
III. C ONTINUOUS S AMPLE ACQUISITION UNDER
C ONCEPT D RIFT
A. The Negative Impact of Actual Network Environment on
Existing Encrypted Traffic Classification Methods
The concept drift of encrypted traffic features refers to the
phenomenon where the representation of a feature changes
arbitrarily without any change in the input (still belonging
to the same feature category). It is due to the self-change
or external influence on the target being classified over time.
Therefore, the sources of the concept drift in encrypted traffic
features are various variable factors in the actual network
environment. From the perspective of encrypted traffic, it can
be broadly categorized into feature concept drift caused by
changes in protocol headers and protocol bodies.
Changes in protocol headers are mainly shown in encryption
transport protocols and application layer protocols, which are
covered/encrypted. On the Internet, the most typical example
of the former is the TLS-1.3 protocol, while the latter is the
HTTP-2.0 protocol. QUIC, as a transport layer protocol with
built-in encryption capabilities, combines the two types of
changes. The core impact comes from the network protocol
itself.
Changes in protocol bodies are more diverse, including
changes in the transmitted data and network environment.
For example, changes in the transmitted data come directly
from application updates, including data-side and functionalside updates. Differently, changes in the network environment

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

3

TABLE I
T HE NEGATIVE IMPACTS OF PROTOCOLS AND THE ENVIRONMENT ON THE CLASSIFICATION OF ENCRYPTED TRAFFIC APPLICATIONS
Influencing Factors

Factor Name
TLS-1.3
HTTP-2.0

Protocol
QUIC

Environment

Multi-protocol Application
Rapid Updates of Applications
Application Homogenization Competition
User Habit Difference
Computational Ocean and LLM

Specific Negative Impacts
Undetermined start of flow for an application behavior
Concept drift to TLS-1.2 statistical features
Flow-level feature confusion due to multiplexing
Hidden application layer header length shorten continuously with access
The classifier for HTTPS traffic becomes invalid directly
QUIC is constantly updated rapidly, so the features are constantly disturbed
More complex multiplexing, interactivity features interference
The highly-precised single protocol classifier fails
Features are constantly changes, new functions, new features
Overlapping functions of applications, increasing feature confusion
Spatially inconsistent traffic features of the same application
Dramatically increasing the speed of function update and new application generate

are more extensive, including changes in hardware models,
network configurations, spatial locations, and other humanselected changes, as well as changes caused by technological
updates and iterations in related fields. We have summarized
these two types of changes in Table I below.
In summary, if we want to implement self-evolving encrypted traffic application classification, we need to consider
all of the above. However, since feature concept drift is
uncontrollable and difficult to predict (especially in the case
of a large number of categories), the concept drift happening
must be determined.
B. Laida Criterion and Silver Samples
When the drift representation accumulates to a certain
extent, we will consider that the model is no longer effective
in the current network environment and urgently needs finetuning (even if some categories still have acceptable classification effects). The prerequisite for fine-tuning is that there are
some new labeled samples, but the cost of collecting labeled
samples through controllable end devices is very high and
cannot guarantee the coverage of after-concept-drift samples.
On the other hand, the traffic throughput of the analysis point
is much higher than that of an end device. The single-slot edge
network traffic processing device at the edge of the backbone
network has a peak of about 400 Gbps throughput, and the
entire device can reach up to 25.6 Tbps. On the contrary, the
peak throughput of a controllable end device is only about
100 Mbps, and the average labeled sample traffic collection
throughput is less than 10 Mbps. Hence, we must obtain new
labeled samples directly at the analysis point.
However, the analysis point cannot obtain samples with
completely real labels; that is, the result obtained by the
classification method may not be 100% correct due to the
nature of deep learning.
In mathematical statistics, the Laida criterion refers to the
interval calculation based on the standard deviation probability
when it is assumed that a dataset is approximately normally
distributed and only has random errors. For encrypted traffic
classification, the Softmax function can convert the parameter
value of the neural network’s penultimate layer into the confidence distribution of the category. Although the classification
of a certain application can meet the sufficient measurement
condition, the confidence distribution of the category may not

conform to the normal distribution, depending on the nature of
the classifier, especially in the case of multi-classification. The
gradient saddle point on the side of the category in question
may not be symmetrical.
Nicely, due to the arbitrary direction of concept drift, we
can assume that the scope of concept drift at the next time
point conforms to the normal distribution. Therefore, we
can extend the assumption that the change in the Softmax
function’s confidence in a certain category is consistent with
the normal distribution, so we can use the Laida criterion as the
verification standard. Samples with positive offset that exceed
this range will be regarded as effective fine-tuning samples,
which are named silver samples in this paper (as opposed
to deterministic labeled samples in the normal construction of
label datasets, which are called gold samples). Therefore, the
confidence standard of the silver sample was selected as 0.997
(3 σ); that is, if the maximum value of Softmax confidence of
the current sample classification result is higher than 0.997,
it is regarded as a silver sample, which will be used for the
subsequent round of fine-tuning.
IV. D RIFT- ORIENTED E NCRYPTED T RAFFIC
S ELF - EVOLVING F INE - TUNING
With the development of time, the features reflected by all
application samples may change compared with the original
sample features of this category, resulting in the inevitability of
concept drift. However, simultaneously, the degree and cycle
of different application updates or version iterations are not
aligned, which leads to uncontrollable concept drift. Therefore,
drift-oriented self-evolving is proposed in this paper, which
aims to continuously fine-tune the model according to the
concept drift of a particular category without considering the
specific classification target.
A. Concept Drift Determination based on Windowed Multithreshold Accumulation Measurement
At a macro level, the self-evolving encrypted traffic application classification plays a crucial role in maintaining the
overall accuracy. This process is reflected in the fact that
the accuracy of each category needs to be improved, and the
more the category with concept drift, the more it needs to be
improved.

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

Due to the arbitrariness of concept drift in all directions and
the continuity of application updates, the classifier intuitively
feels that the current sample features are ”similar enough but
not very similar” to the features during training, which is
reflected in the decline of classification confidence. It is worth
noting that for classifiers, a decline in classification confidence
is a necessary condition for concept drift to have an impact.
Therefore, judging concept drift only by the appearance of
classification confidence decline is wrong.
In order to make better use of classification confidence
decline to judge concept drift, we propose a concept drift
determination method based on windowed multi-threshold
accumulation measurement to determine whether a specific
category or the whole classifier have concept drift (whether it
needs to be fine-tuned).
The purpose of determining whether concept drift occurs in
a certain category is that the update cycle of some applications
is concise, and the degree of concept drift per unit time is
much higher than that of other categories. Although it has little
impact on the model’s overall accuracy, it is invalid for this
category. Hence, the overall classifier’s determination is that
most categories are invalid to a certain extent, so the results
obtained by the model do not have a good reference value.
Therefore, according to the theory in Section III, we set
multiple thresholds for each category and the overall model,
respectively, and there are different scores for reaching different thresholds. By calculating the accumulative score of the
new classified sample in the current time window, we can
determine whether the category or the whole model needs to
be fine-tuned, as shown in Figure 1.
In particular, since the concept drift determination should
not affect the standard classification of encrypted traffic, it
is impossible to constantly slide to calculate whether concept drift occurs in a specific time slice (otherwise, it will
bring huge polling performance overhead). Since the overall
accuracy decline of the model comes from the accumulation
of class accuracy decline, we will carry out the number of
accumulative times when the confidence is too low for the
samples of a certain class (assumed as class A) for the first
time, and the lower the threshold, the more times will be
accumulated. If the accumulative number of measurements
in the current time window reaches the judgment threshold,
it is regarded as the happening of concept drift. A more
severe concept drift is considered to have occurred if a lower
decision threshold is reached. Subsequent fine-tuning can be
done depending on the degree of conceptual drift in the current
category.
Suppose the single class of the current model has only slight
concept drift at worst. Still, many classes already have concept
drift (usually in the model after long-term use, which is also
determined by accumulation measurement). In that case, the
entire model must be fine-tuned to adapt to the current feature
representation distribution.
B. Drift-oriented Self-evolving Fine-tuning
Compared with the task specialization of an LLM, the initial
model in the self-evolving lifecycle can be regarded as a pretraining process and the subsequent evolution process as a

4

fine-tuning process of the model. However, the target dataset
is derived from the silver samples continuously obtained in the
classification process, and fine-tuning is constantly occurring.
Therefore, in view of this paper’s self-evolving scenario,
we propose drift-oriented self-evolving fine-tuning. It is worth
noting that ”drift-oriented” means that we will not specifically
study the feature changes of a certain category during the
whole lifecycle of the model but let the classifier directly be
fine-tuned when there is a concept drift. This adaptability to
concept drift is also the meaning of ’self’ in self-evolving, and
it ensures the model’s accuracy over time.
It’s crucial to understand that, in the context of encrypted traffic classification, self-evolving is inherently modelindependent. This means that any deep learning model capable
of fine-tuning can be seamlessly integrated into the selfevolving fine-tuning architecture, providing a high level of
flexibility and adaptability. Unlike sequence classification in
NLP, where Transformer are typically used, encrypted traffic
classification requires models that can maintain high throughput network requirements. Therefore, for the classification
model to be fine-tuned, we have chosen LS-LSTM [7] from
previous research to demonstrate the enhancement potential of
our proposed method.
Since the target model does not necessarily have the ability
to adapt to prefixes, we chose FFT over other methods.
V. E XPERIMENT E VALUATION
A. Dataset and Experimental Environment
Since the current public dataset cannot effectively support
the research of self-evolving encrypted traffic classification,
we conducted traffic sample collection in the actual network
environment of Jiangsu Province (in order to ensure privacy,
the specific information about traffic collection personnel, device model, and account is not disclosed) from September 27,
2023, to July 16, 2024. It includes the traffic of various Internet
applications and web pages, mainly multimedia-related traffic,
a total of 372 GB (the content are relatively stable and can
better reflect the concept drift of traffic features). The silver
sample dataset still uses 80% of the samples as training and
20% as test samples as primitive datasets.
It is worth noting that to reflect the changes in application
characteristics, we deliberately selected six applications with
large user and traffic volumes. As shown in Table II, silver
samples were calculated only for the first and second finetuning stages (the number is determined by the actual experimental results). In contrast, the long-span third classification
stage’s samples had a more extended period than the previous
two. In order to reflect the continuity of the traffic label
sample, we did not divide the data strictly according to
the date. However, we carried out proportional segmentation
according to the continuity of the time axis according to the
sample size. At the same time, we directly used datasets with
a highly uneven number distribution to reflect the differences
in the sample size distribution of different applications in
actual network environments. Datasets will be published at
https://data.iptas.edu.cn/web/tbps after a strict privacy audit.
Since the determination of concept drift is a simple statistical process of sample classification confidence results, the

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

5

Fig. 1. Conceptual drift determination process diagram based on windowed multi-threshold accumulation measurement
TABLE II
S TATISTICS OF THE DATASETS ( PRESENT BY FLOW COUNT )
Application
Bilibili
Douyin
MGTV
Youku
QQ Music
IQiYi
Total

Initial training
samples
4585
125
1965
4425
47828
2925
61853

1st stage
total samples
4587
123
1963
4427
47830
2923
61853

1st fine-tune *
silver samples
1407
21
159
825
39099
1809
43320

2nd stage
total samples
4587
123
1963
4427
47830
2923
61853

2nd fine-tune *
silver samples
2340
34
371
1096
40542
2304
46687

Final stage
long-span samples
1529
41
656
1477
15944
977
20624

* The silver samples are gathered by the previous one version classifier, which is model-dataset specific.

preliminary experiment found that the threshold is related
to the throughput of current network traffic (that is, to the
total number of samples to be classified). Therefore, we
directly assume that each stage triggers the determination of
concept drift in the following experiments. Therefore, each
classification stage must be self-evolving as it transitions to
the next stage.
B. Encrypted Traffic Classification Effect Diminishing and
Self-evolving Classification Experiment
At the same time, we conducted a diminishing experiment
and a self-evolving experiment on the classification effect of
encrypted traffic. In this experiment, we first compared the
effects of the initial trained model, the fine-tuned model from
initial trained model using the silver samples from the first

stage dataset (Level-1 fine-tuned), and the fine-tuned model
from Level-1 fine-tuned model using the silver samples from
the second stage dataset (Level-2 fine-tuned) on the data subset
in the next stage, respectively. Then we fine-tuned the model
in the current stage and tested the results after fine-tuning.
The epoch of initial training or fine-tuning was 50 rounds, the
batch-size was 500, and the learning-rate was fixed at 0.0025.
We conducted ten rounds of experiments, and each round of
the training set and test set was randomly divided in equal
proportion (80% and 20%). The average results are shown in
Table III.
The following conclusions can be drawn from the experimental results:
1) By comparing the classification performance of each
round of initial training or fine-tuned model in the cur-

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

6

TABLE III
T HE PERFORMANCE OF THE THREE DIFFERENT STAGE MODELS UNDER THEIR OWN STAGE DATASETS , NEXT- STAGE DATASETS , AND FINAL - STAGE
DATASETS

Training F1-score
Testing F1-score
F1-score of Next-stage Samples
F1-score of Final Samples
Silver Sample Percentage in Final Samples

Initial trained LS-LSTM
0.9321
0.9189
0.8960
0.5950
41.66%

rent data subset and the following data subset, concept
drift exists, which is not only reflected in the decline
of the classification confidence of some samples on the
micro level but also in the decline of the F1-score of
the overall dataset on the macro level. Therefore, the
diminishing of the encrypted traffic classification effect
over time is natural.
2) Compared with the initial training model and the two
fine-tuned models, the catastrophic forgetting that often
occurs in the field of NLP does not appear. However,
it can be seen that the training F1-score is constantly
improving, while the classification F1-score of the next
round of data is constantly decreasing. At the same time,
although the silver sample rate of the final test dataset
is increasing (that is, the accuracy of the classification
of the sample is high confidence or the classification of
the sample is firmly wrong), the F1-score even shows a
decline in general. This indicates some overfitting, which
is expected because self-evolving fine-tuning cannot give
the model an infinite lifetime. It can only extend the
lifetime of the model. With second stage experimental
data as a calculation, the life cycle is extended to 8
months (compared to a first-order model with a span of
only 2 months).
3) Comparing the F1-score of the next round of data
classification before fine-tuning with the test F1-score
of the model after fine-tuning, it can be found that selfevolving fine-tuning is effective and can significantly
improve the model’s ability to adapt to new data. It is
worth noting that because the samples of each stage have
a specific span, the fine-tuning sample set actually covers
the data of the current time node (that is, the update
of the application are continuous). Therefore, using the
silver sample as the fine-tuning dataset for self-evolving
is feasible and reasonable.
4) For the long-span third classification samples tested in
the final test, the initial and fine-tuned models performed
poorly and showed a downward trend on the whole.
The main reason is that the feature concept drift of
the long period (up to 3 months with the second stage
dataset) could not be expressed by the current finetuning, especially for some categories with few samples.
The weakness of feature expression activation makes it
more challenging to adapt to changes, so self-evolving
needs to be constantly deployed. On the other hand,
the average F1-score of the Level-2 fine-tuned model
is slightly increased. This may be because the second
stage data is closer to the final data in time (although

Level-1 fine-tuned LS-LSTM
0.9902
0.9619
0.8956
0.5842
56.74%

Level-2 fine-tuned LS-LSTM
0.9960
0.9822
N/A
0.5898
68.20%

still far away), and the features are slightly more similar,
proving the continuity of application updates.
VI. C ONCLUSION
This paper proposes a self-evolving encrypted traffic application classification method for the actual large-scale Internet
environment, which does not need to consider the specific
changes of the actual classification objectives, nor does it need
to restrict the role of the model. It directly relies on the silver
samples accumulated in the prediction process, based on the
concept drift determination through windowed multi-threshold
accumulation measurement, and constantly fine-tuning the
model. Thus, the life cycle of the classification model can
be extended greatly without any real labeled samples and
retraining.
In the subsequent research, the relationship between concept
drift determination and sample size (network traffic throughput) will be further refined first, and the relationship between
the Softmax threshold value of silver sample determination
(currently 0.997 directly) and model/sample needs to be further
studied. In addition, the dataset will be extended to quantify
the extension of the lifecycle and the cost that can be really
reduced.
ACKNOWLEDGMENTS
This paper is supported by the Youth Fund of the National
Natural Science Foundation of China under Grant Number
62402101, the Joint Funds of the National Natural Science
Foundation of China under Grant Number U22B2025, the
Jiangsu Funding Program for Excellent Postdoctoral Talent
under Grant Number 2024ZB494. This paper is part on the
topic of the encrypted traffic classification. Guang Cheng is
the corresponding author.
R EFERENCES
[1] Y. Zeng, Z. Wu, L. Dong, Z. Liu, J. Ma, and Z. Li, “Research
on malicious traffic identification technology in encrypted traffic,”
Xi’an Dianzi Keji Daxue Xuebao/Journal of Xidian University,
vol. 48, no. 3, pp. 170 – 187, 2021. [Online]. Available:
http://dx.doi.org/10.19665/j.issn1001-2400.2021.03.022
[2] Z.-H. Chen, G. Cheng, Z.-H. Xu, K.-Y. Xu, X. Qiu, and D.-D.
Niu, “A survey on internet encrypted traffic detection, classification
and identification,” Jisuanji Xuebao/Chinese Journal of Computers,
vol. 46, no. 5, pp. 1060 – 1085, 2023. [Online]. Available:
http://dx.doi.org/10.11897/SP.J.1016.2023.01060
[3] S. Xu, G. Geng, X. Jin, D. Liu, and J. Weng, “Seeing traffic paths:
Encrypted traffic classification with path signature features,” IEEE
Transactions on Information Forensics and Security, vol. 17, pp. 2166–
2181, 2022.

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

7

[4] M. Shen, K. Ye, X. Liu, L. Zhu, J. Kang, S. Yu, Q. Li, and K. Xu,
“Machine learning-powered encrypted network traffic analysis: A comprehensive survey,” IEEE Communications Surveys & Tutorials, vol. 25,
no. 1, pp. 791–824, 2023.
[5] Z. Chen, G. Cheng, Z. Wei, D. Niu, and N. fu, “Classify traffic rather
than flow: Versatile multi-flow encrypted traffic classification with flow
clustering,” IEEE Transactions on Network and Service Management,
pp. 1–1, 2023.
[6] J. Lu, A. Liu, F. Dong, F. Gu, J. Gama, and G. Zhang, “Learning under
concept drift: A review,” IEEE Transactions on Knowledge and Data
Engineering, vol. 31, no. 12, pp. 2346–2363, 2019.
[7] Z. Chen, G. Cheng, Z. Xu, S. Guo, Y. Zhou, and Y. Zhao,
“Length matters: Scalable fast encrypted internet traffic service
classification based on multiple protocol data unit length sequence
with composite deep learning,” Digital Communications and Networks,
vol. 8, no. 3, pp. 289–302, 2022. [Online]. Available: https:
//www.sciencedirect.com/science/article/pii/S2352864821000699
[8] Z. Song, Z. Zhao, F. Zhang, G. Xiong, G. Cheng, X. Zhao, S. Guo,
and B. Chen, “I 2 rnn: An incremental and interpretable recurrent
neural network for encrypted traffic classification,” IEEE Transactions
on Dependable and Secure Computing, pp. 1–14, 2023.
[9] M. Shen, J. Zhang, L. Zhu, K. Xu, and X. Du, “Accurate decentralized
application identification via encrypted traffic analysis using graph
neural networks,” IEEE Transactions on Information Forensics and
Security, vol. 16, pp. 2367–2380, 2021.
[10] A. Nascita, A. Montieri, G. Aceto, D. Ciuonzo, V. Persico, and
A. Pescapé, “Improving performance, reliability, and feasibility in multimodal multitask traffic classification with xai,” IEEE Transactions on
Network and Service Management, vol. 20, no. 2, pp. 1267–1289, 2023.
[11] M. Shen, Y. Liu, L. Zhu, X. Du, and J. Hu, “Fine-grained webpage
fingerprinting using only packet length information of encrypted traffic,”
IEEE Transactions on Information Forensics and Security, vol. 16, pp.
2046–2059, 2021.
[12] X. Yun, Y. Wang, Y. Zhang, C. Zhao, and Z. Zhao, “Encrypted tls
traffic classification on cloud platforms,” IEEE/ACM Transactions on
Networking, vol. 31, no. 1, pp. 164–177, 2023.

works as a reviewer for multiple Journals such as IEEE IoTJ and the duty
editor of the Journal of Cyberspace.

Zihan Chen obtained his Ph.D. degree in Cyber Security from Southeast
University in 2023 and B.S. degree in Software Engineering from Central
South University in 2017. He is currently working as a postdoc with the School
of Cyber Science and Engineering at Southeast University. His major research
interests include cyber security, encrypted traffic classification, encrypted
traffic feature engineering, and deep learning. He is a Member of IEEE and

Xing Luan received the B.S. degree in computer science and technology
from HoHai University (HHU) in 2023. He is currently a Doctor candidate at
the School of cyber science and engineering, Southeast University, Nanjing,
China. His current research interests include network traffic detection and
VPN traffic.

Guang Cheng received his B.S. degree in Traffic Engineering from Southeast
University in 1994, his M.S. degree in Computer Application from Hefei
University of Technology in 2000, and his Ph.D. degree in Computer Network
from Southeast University in 2003. He is a Full Professor in the School of
Cyber Science and Engineering, Southeast University, Nanjing, China. He has
authored or coauthored seven monographs and more than 100 technical papers,
including top journals and top conferences. His research interests include
network security, network measurement, and traffic behavior analysis. He is
a Member of IEEE and a Senior Member of CCF.

Jinhui Li received his B.S. degree in Cyber Security from Southeast University in 2021. He is currently a Master’s student at the School of Cyber
Science and Engineering, Southeast University. His major research interests
include feature engineering and classification of multimedia traffic, as well as
encrypted traffic classification.

Tian Qin received the B.S. degree in information and computing sciences
from HoHai University (HHU) in 2020. He is currently a Doctor candidate at
the School of cyber science and engineering, Southeast University, Nanjing,
China. His current research interests include network traffic detection and
federated learning.

Yuyang Zhou is currently working as a postdoc with the School of Cyber
Science and Engineering, Southeast University. His major research interests
include moving target defense, Android malware detection, and security
modeling.
PAPER_TEXT
