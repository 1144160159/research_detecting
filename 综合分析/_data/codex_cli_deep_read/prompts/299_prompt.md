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
# [299] Self-Supervised Learning for Time Series Analysis: Taxonomy, Progress, and Prospects
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
编号：299
题名：Self-Supervised Learning for Time Series Analysis: Taxonomy, Progress, and Prospects
年份：2024
DOI：10.1109/tpami.2024.3387317
来源：IEEE Transactions on Pattern Analysis and Machine Intelligence
PDF：paper/10.1109_TPAMI.2024.3387317.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：数据集、基准、综述与开源工具、时序、日志、KPI 与云原生异常检测
相关性：弱相关，分数 1
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\299.txt
- 原始字符数：123750
- 本次发送字符数：123750
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

6775

Self-Supervised Learning for Time Series Analysis:
Taxonomy, Progress, and Prospects
Kexin Zhang , Graduate Student Member, IEEE, Qingsong Wen , Senior Member, IEEE, Chaoli Zhang ,
Rongyao Cai , Graduate Student Member, IEEE, Ming Jin , Yong Liu , Member, IEEE, James Y. Zhang ,
Yuxuan Liang , Member, IEEE, Guansong Pang , Member, IEEE, Dongjin Song , Member, IEEE,
and Shirui Pan , Senior Member, IEEE
(Survey Paper)

Abstract—Self-supervised learning (SSL) has recently achieved
impressive performance on various time series tasks. The most
prominent advantage of SSL is that it reduces the dependence on
labeled data. Based on the pre-training and fine-tuning strategy,
even a small amount of labeled data can achieve high performance.
Compared with many published self-supervised surveys on computer vision and natural language processing, a comprehensive
survey for time series SSL is still missing. To fill this gap, we
review current state-of-the-art SSL methods for time series data
in this article. To this end, we first comprehensively review existing
surveys related to SSL and time series, and then provide a new
taxonomy of existing time series SSL methods by summarizing
them from three perspectives: generative-based, contrastive-based,
and adversarial-based. These methods are further divided into ten
Manuscript received 17 July 2023; revised 23 January 2024; accepted 6
April 2024. Date of publication 10 April 2024; date of current version 5
September 2024. This work was supported in part by the Key R&D Project
of Zhejiang Province under Grant 2024C01172 and in part by the National
Key R&D Program of China under Grant 2021YFB2012300. Recommended
for acceptance by M. Cho. (Corresponding authors: Qingsong Wen; Yong Liu.)
Kexin Zhang is with the Huzhou Institute of Zhejiang University,
Huzhou 313000, China, and also with the College of Control Science
and Engineering, Zhejiang University, Hangzhou 310027, China (e-mail:
zhangkexin@zju.edu.cn).
Qingsong Wen was with Alibaba Group. He is now with Squirrel AI, Bellevue,
WA 98004 USA (e-mail: qingsongedu@gmail.com).
Chaoli Zhang is with the School of Computer Science and Technology, Zhejiang Normal University, Jinhua, Zhejiang 321017, China (e-mail:
chaolizcl@zjnu.edu.cn).
Rongyao Cai and Yong Liu are with the College of Control Science
and Engineering, Zhejiang University, Hangzhou 310027, China (e-mail:
rycai@zju.edu.cn; yongliu@iipc.zju.edu.cn).
Ming Jin is with the Faculty of Information Technology, Monash University,
Clayton, VIC 3800, Australia (e-mail: ming.jin@monash.edu).
James Y. Zhang is with Ant Group, Hangzhou, Zhejiang 310058, China
(e-mail: james.z@antgroup.com).
Yuxuan Liang is with the INTR & DSA Thrust, Hong Kong University of Science and Technology, Clear Water Bay, Hong Kong (e-mail:
yuxliang@outlook.com).
Guansong Pang is with the School of Computing and Information
Systems, Singapore Management University, Singapore 188065 (e-mail:
gspang@smu.edu.sg).
Dongjin Song is with the School of Computing, University of Connecticut,
Storrs, CT 06269 USA (e-mail: dongjin.song@uconn.edu).
Shirui Pan is with the School of Information and Communication
Technology, Griffith University, Southport, Qld 4222, Australia (e-mail:
s.pan@griffith.edu.au).
https://github.com/qingsongedu/Awesome-SSL4TS.
This article has supplementary downloadable material available at
https://doi.org/10.1109/TPAMI.2024.3387317, provided by the authors.
Digital Object Identifier 10.1109/TPAMI.2024.3387317

subcategories with detailed reviews and discussions about their
key intuitions, main frameworks, advantages and disadvantages.
To facilitate the experiments and validation of time series SSL
methods, we also summarize datasets commonly used in time series
forecasting, classification, anomaly detection, and clustering tasks.
Finally, we present the future directions of SSL for time series
analysis.
Index Terms—Deep learning, representation learning, selfsupervised learning, time series analysis.

I. INTRODUCTION
IME series data abound in many real-world scenarios [1],
[2], including human activity recognition [3], industrial
fault diagnosis [4], smart building management [5], and healthcare [6]. The key to most tasks based on time series analysis
is to extract useful and informative features. In recent years,
Deep Learning (DL) has shown impressive performance in
extracting hidden patterns and features of the data. Generally,
the availability of sufficiently large labeled data is one of the
critical factors for a reliable DL-based feature extraction model,
usually referred to as supervised learning. Unfortunately, this
requirement is difficult to meet in some practical scenarios,
particularly for time series data, where obtaining labeled data
is a time-consuming process. As an alternative, Self-Supervised
Learning (SSL) has garnered increasing attention for its labelefficiency and generalization ability, and consequently, many
latest time series modeling methods have been following this
learning paradigm.
SSL is a subset of unsupervised learning that utilizes pretext
tasks to derive supervision signals from unlabeled data. These
pretext tasks are self-generated challenges that the model solves
to learn from the data, thereby creating valuable representations
for downstream tasks. SSL does not require additional manually
labeled data because the supervisory signal is derived from the
data itself. With the help of well-designed pretext tasks, SSL
has recently achieved great success in the domains of Computer
Vision (CV) [7], [8], [9], [10] and Natural Language Processing
(NLP) [11], [12].
With the great success of SSL in CV and NLP, it is appealing
to extend SSL to time series data. However, transferring the
pretext tasks designed for CV/NLP directly to time series data

T

0162-8828 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

6776

Fig. 1.

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

Proposed taxonomy of SSL for time series data.

is non-trivial, and often fails to work in many scenarios. Here
we highlight some typical challenges that arise when applying
SSL to time series data. First, time series data exhibit unique
properties such as seasonality, trend, and frequency domain information [13], [14], [15]. Since most pretext tasks designed for
image or language data do not consider these semantics related
to time series data, they cannot be directly adopted. Second,
some techniques commonly used in SSL, such as data augmentation, need to be specially designed for time series data. For
example, rotation and crop are the commonly used augmentation
techniques for image data [16]. However, these two techniques
may break the temporal dependency of the series data. Third,
most time series data contain multiple dimensions, i.e., multivariate time series. However, useful information usually only
exists in a few dimensions, making it difficult to extract useful
information in time series using SSL methods from other data
types.
To the best of our knowledge, there has yet to be a comprehensive and systematic review of SSL for time series data, in contrast
to the extensive literature on SSL for CV or NLP [17], [18]. The
surveys proposed by Eldele et al. [19] and Deldari et al. [20]
are partly similar to our work. However, these two reviews
only discuss a small part of self-supervised contrastive learning
(SSCL), which requires a more comprehensive literature review.
Furthermore, a summary of benchmark time series datasets
needs to be included, and the potential research directions for
time series SSL are also scarce.
This article provides a review of current state-of-the-art SSL
methods for time series data. We begin by summarizing recent reviews on SSL and time series data and then propose
a new taxonomy from three perspectives: generative-based,
contrastive-based, and adversarial-based. The taxonomy is similar to the one proposed by Liu et al. [21] but specifically
concentrated on time series data. For generative-based methods, we describe three frameworks: autoregressive-based forecasting, auto-encoder-based reconstruction, and diffusion-based

generation. For contrastive-based methods, we divide the existing work into five categories based on how positive and
negative samples are generated, including sampling contrast,
prediction contrast, augmentation contrast, prototype contrast,
and expert knowledge contrast. Then we sort out and summarize the adversarial-based methods based on two target tasks:
time series generation/imputation and auxiliary representation
enhancement. The proposed taxonomy is shown in Fig. 1. We
conclude this work by discussing possible future directions
for time series SSL, including selection and combination of
data augmentation, selection of positive and negative samples
in SSCL, the inductive bias for time series SSL, theoretical
analysis of SSCL, adversarial attacks and robust analysis on
time series, time series domain adaption, pretraining and large
models for time series, time series SSL in collaborative systems,
and benchmark evaluation for time series SSL.
Our main contributions are summarized as follows.
r New taxonomy and comprehensive review: We provide a
new taxonomy and a detailed and up-to-date review of time
series SSL. We divide existing methods into ten categories,
and for each category, we describe the basic frameworks,
mathematical expression, fine-grained classification, detailed comparison, advantages and disadvantages. To the
best of our knowledge, this is the first work to comprehensively and systematically review the existing studies of
SSL for time series data.
r Collection of applications and datasets: We collect resources on time series SSL, including applications and
datasets, and investigate related data sources, characteristics, and corresponding works.
r Abundant future directions: We point out key problems
in this field from both applicative and methodology perspectives, analyze their causes and possible solutions, and
discuss future research directions for time series SSL. We
strongly believe that our efforts will ignite further research
interests in time series SSL.

ZHANG et al.: SSL FOR TIME SERIES ANALYSIS: TAXONOMY, PROGRESS, AND PROSPECTS

The rest of the article is organized as follows. Section II
provides some review literature on SSL and time series data.
Sections III to V describe the generation-based, contrastivebased, and adversarial-based methods, respectively. Section VI
lists some commonly used time series data sets from the application perspective. The quantitative performance comparisons and
discussions are also provided. Section VII discusses promising
directions of time series SSL, and Section VIII concludes the
article.

6777

TABLE I
OVERVIEW OF RECENT SSL SURVEYS ON DIFFERENT MODALITIES

II. RELATED SURVEYS
In this section, the definition of time series data is first introduced, and then several recent reviews on SSL and time series
analysis are scrutinized.
A. Definition of Time Series Data
1) Univariate Time Series: A univariate time series refers
to an ordered sequence of observations or measurements of
the same variable indexed by time. It can be defined as X =
(x0 , x1 , x2 , . . . , xt ), where xi is the point at timestamp i. Most
often, the measurements are made at regular time intervals.
2) Multivariate Time Series: A multivariate time series consists of two or more interrelated variables (or dimensions) that
depend on time. It is a combination of multiple univariate time
series and can be defined as X = [X0 , X1 , X2 , . . . , Xp ], where
p is the number of variables.
3) Multiple Multivariate Time Series: Considering the scenario where distinct sets of multivariate time series are concurrently examined. Analyzing such datasets involves studying
each set independently and exploring the relationships between
different sets. For instance, if we study meteorological data from
different cities, each city’s data forms a multivariate time series,
collectively resulting in multiple multivariate time series. This
can be articulated as X = {X0 , X1 , X2 , . . . , Xn }, where n is
the number of multivariate time series.
B. Surveys on SSL
The surveys on SSL can be categorized by different criteria.
In this paper, we outline three widely used criteria: learning
paradigms, pretext tasks and components/modules.
1) Learning Paradigms: This category focuses on model
architectures and training objectives. The SSL methods can be
roughly divided into the following categories: generative-based,
contrastive-based, and adversarial-based methods. The characteristics and descriptions of the above methods can be found in
Appendix A, available online. Using the learning paradigm as
a taxonomy is arguably the most popular among the existing
SSL surveys, including [20], [22], [23], [24], [25], [26], [27].
However, not all surveys cover the above three categories. The
readers are referred to these surveys for more details. In Table I,
we also provide the data modalities involved in each survey,
which can help readers quickly find the research work closely
related to them.
2) Pretext Tasks: The pretext task serves as a means to learn
informative representations for downstream tasks. Unlike the

learning-paradigm-based criterion, the pretext-task-based criterion is also related to data modality. For example, Ericsson
et al. [28] provides a very comprehensive review of pretext
tasks for multiple modalities, including image, video, text, audio,
time series, and graph. The various self-supervised pretexts
are divided into five broad families: transformation prediction,
masked prediction, instance discrimination, clustering, and contrastive instance discrimination. Jing and Tian [18] summarize
the self-supervised feature learning methods on image and
video data, and four categories are discussed: generation-based,
context-based, free semantic label-based, and cross modalbased, where cross-modal-based methods construct learning
task using RGB frame sequence an optical flow sequence, which
are unique features in the video. Gui et al. [30] explore four
kinds of pretext tasks in computer vision and natural language
processing, including context-based methods, contrastive learning methods, generative algorithms, and contrastive generative
methods. Essentially, the core of the pretext tasks is how to construct pseudo-supervision signals. Generally speaking, ignoring
the differences in data modalities, existing pretext tasks can be

6778

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

roughly summarized into three categories: context prediction,
instance discrimination, and instance generation. The main differences and examples are summarized in Table III. It should be
noted that here we only list some commonly used pretexts tasks,
and some special pretext tasks are not the focus of this article.
The details can be found in Appendix B.2, available online.
3) Components and Modules: The literature categorizing
SSCL methods according to their modules and components
throughout the pipeline is also an important direction. Jaiswal
et al. [17], Le-Khac et al. [29] and Liu et al. [33] sort out the
modules and components required in SSL from different perspectives. Specifically, Liu et al. [33] summarizes the research
progress of self-supervised contrastive learning on medical time
series data. In summary, the pipeline can be divided into four
components: positive and negative samples, pretext task, model
architecture, and training loss.
The basic intuition behind SSCL is to pull positive samples
closer and push negative samples away. Therefore, the first component is to construct positive and negative samples. According
to the suggestions of Le-Khac et al. [29], the main methods can
be divided into the following categories: multisensory signals,
data augmentation, local-global consistency, and temporal consistency. Additional descriptions regarding the characteristics of
these categories can be found in Appendix B.1, available online.
The second component is pretext tasks, which is a selfsupervised task that acts as an important strategy to learn data
representations using pseudo-labels [17]. Pretext tasks have
been summarized and categorized in the previous subsection,
so repeated content will not be introduced again. The details can
be found in Section II-B2 and Appendix B.2, available online.
The third component is model architecture, which determines how positive and negative samples are encoded during
training. The major categories include end-to-end [16], memory bank [34], momentum encoder [35], and clustering [36].
More details of these four architectures are summarized in
Appendix B.3, available online.
The fourth component is training loss. As summarized in [29],
commonly used contrastive loss functions generally include
scoring functions (cosine similarity), energy-based margin functions (pair loss and triplet loss), probabilistic NCE-based functions, and mutual information based functions. More details of
these loss functions are summarized in Appendix B.4, available
online.

methods, pattern mixing, generative models, and decomposition
methods. Moreover, both [45] and [46] empirically compare different data augmentation methods for time series classification
tasks. [48] systematically reviews transformer schemes for time
series modeling from two perspectives: network structure and
applications. Liu et al. [33] provide a comprehensive summary
of the various augmentations applied to medical time series
data, the architectures of pre-training encoders, the types of
fine-tuning classifiers and clusters, and the popular contrastive
loss functions. The taxonomies proposed by Eldele et al. [19],
Deldari et al. [20] and Liu et al. [33] are somewhat similar
to our proposed taxonomy, i.e., three taxonomies involve time
series self-supervised contrastive learning methods. However,
our taxonomy provides more detailed categories and more literature in the contrastive-based approach. Although the taxonomy
proposed by Liu et al. [33] also focuses on time series data.
They emphasize discussion of medical time series data, while
we focus more on general time series SSL. More importantly, in
addition to contrastive-based approaches, we also thoroughly
review a large set of literature for the generative-based and
adversarial-based approaches.
III. GENERATIVE-BASED METHODS
In this category, the pretext task is to generate the expected
data based on a given view of the data. In the context of time
series modeling, the commonly used pretext tasks include using
the past series to forecast the future windows or specific time
stamps, using the encoder and decoder to reconstruct the input,
and forecasting the unseen part of the masked time series.
This section sorts out the existing self-supervised representation
learning methods in time series modeling from the perspectives
of autoregressive-based forecasting, autoencoder-based reconstruction, and diffusion-based generation. It should be noted that
the autoencoder-based reconstruction task is also viewed as an
unsupervised framework. In the context of SSL, we mainly use
the reconstruction task as a pretext task, and the final goal is
to obtain the representations through autoencoder models. The
illustration of the generative-based SSL for time series is shown
in Fig. 2. In Appendix C.1–C.3, available online, the main advantages and disadvantages of three generative-based submethods
are summarized. Furthermore, the direct comparison of the three
methods is shown in Appendix C.4, available online.
A. Autoregressive-Based Forecasting

C. Surveys on Time Series Data
The surveys on time series data can be roughly divided into
two categories. The first category focuses on different tasks, such
as classification [37], [38], forecasting [39], [40], [41], [42], and
anomaly detection [43], [44]. These surveys comprehensively
sort out the existing methods for each task. The second category
focuses on the key components of time series modeling based
on deep neural networks, such as data augmentation [33], [45],
[46], [47], model structure [33], [48], [49]. [45] proposed a
new taxonomy that divides the existing data augmentation techniques into basic and advanced approaches. [46] also provides
a taxonomy and outlines four families: transformation-based

Given the current time step t, the goal of an autoregressivebased forecasting (ARF) task is to forecast K future horizons
based on t historical time steps, which can be expressed as:


(1)
x̂[t+1:t+K] = f x[1:t] ,
where x̂[t+1:t+K] represents the target window, and K represents
the length of the target window. When K = 1, (1) is a single-step
forecasting model, and it is a multi-step forecasting model when
K > 1. x[1:t] represents the input series before time t (including
t), which is usually used as the input of the model. f (·) represents
the forecasting model. The learning objective is to minimize the
distance between the predicted target window and the ground

ZHANG et al.: SSL FOR TIME SERIES ANALYSIS: TAXONOMY, PROGRESS, AND PROSPECTS

6779

normalizing flow (GANF) is another graph-based approach that
can model the conditional dependencies among constituent time
series [57]. In order to choose a more appropriate model in
building time series SSL task, we further give the advantages and
disadvantages of these three commonly used models. The details
can be found in Appendix D, available online. Unlike the above
methods, SSTSC [58] proposes a temporal relation learning
prediction task based on the “Past-Anchor-Future” strategy as
a self-supervised pretext task. Instead of directly forecasting
the values of the future time windows, SSTSC predicts the
relationships of the time windows, which can fully mine the
temporal relationship in the data.
B. Autoencoder-Based Reconstruction
The autoencoder is an unsupervised artificial neural network
composed of an encoder and a decoder [59]. The encoder maps
the input x to the representation z, and then the decoder remaps the representation z back to the input. The output of the
decoder is defined as the reconstructed input x̃. The process can
be expressed as:
Fig. 2.

Three categories of generative-based SSL for time series data.

truth, thus the loss function can be defined as:


L = D x̂[t+1:t+K] , x[t+1:t+K] ,

z = E(x), x̃ = D(z),

(2)

where D(·) represents the distance between the predicted future window x̂[t+1:t+K] and the ground-truth future window
x[t+1:t+K] , usually measured by the mean square error (MSE),
i.e.,
L=

K
1 

K

x̂[t+k] − x[t+k]

2

.

(3)

k=1

In the time series modeling with autoregressive-based forecasting task as a pretext task, Recurrent neural networks (RNNs)
are widely used thanks to their strong capability in spatiotemporal dynamic behavior modeling or sequence prediction [41],
[42], [50], [51]. Therefore, it is also naturally applied in the
pretext task based on autoregressive forecasting. THOC [52]
constructs a self-supervised pretext task for multi-resolution
single-step forecasting called Temporal Self-Supervision (TSS).
TSS takes the L-layer dilated RNN with skip-connection structure as the model. By setting skip length, it can ensure that the
forecasting tasks can be performed with different resolutions
at the same time. In addition to RNNs, the forecasting models
based on Convolutional neural networks (CNNs) also have been
developed [53]. Moreover, STraTS [54] first encodes the time
series data into triple representations to avoid the limitations of
using basic RNN and CNN in modeling irregular and sparse time
series data and then builds the transformer-based forecasting
model for modeling multivariate medical clinical time series.
Graph-based time series forecasting methods can also be used
as a self-supervised pretext task. Compared with RNNs and
CNNs, Graph Neural Networks (GNNs) can better capture the
correlation among variables and constituent in multivariate time
series data, such as GDN [55] and GTS [56]. Graph-augmented

(4)

where E(·) and D(·) represent the encoder and decoder, respectively. The difference between the original input x and the
reconstructed input x̃ is called the reconstruction error, and
the goal of the self-supervised pretext task using autoencoder
structure is to minimize the error between x and x̃, i.e.,
L = x − x̃2 .

(5)

The model structure of (4) is defined as the basic autoencoder
(BAE). Most BAE-based methods jointly train the encoder E(·)
and the decoder D(·). Then removing the decoder D(·) and
leaving only the encoder E(·) that is used as a feature extractor,
and the representation z is used for downstream tasks [60], [61],
[62], [63]. For example, TimeNet [61], PT-LSTM-SAE [62],
and Autowarp [60] all use RNN to build a sequence autoencoder
model including encoder and decoder, which tries to reconstruct
the input series. Once the model is learned, the encoder is used
as a feature extractor to obtain an embedded representation of
time series samples, which can help downstream tasks, such
as classification and forecasting, achieve better performance.
Zhang et al. [64] build a CNN-based autoencoder model and
keep the encoder as a feature extractor after minimizing (5). The
experimental results show that using the encoded representation
is better than directly using the original time series data in
industrial fault detection tasks.
However, the representations obtained by (5) are sometimes
task-agnostic. Therefore, it is feasible to introduce additional
training constraints based on (5). Abdulaal et al. [63] focus
on the complex asynchronous multivariate time series data and
introduce the spectral analysis in the autoencoder model. The
synchronous representation of the time series is extracted by
learning the phase information in the data, which is eventually
used for the anomaly detection task. DTCR [65] is a temporal clustering-friendly representation learning model. It introduces K-means constraints in the reconstruction task, making

6780

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

the learned representation more friendly to clustering tasks.
USAD [66] uses an encoder and two decoders to build an autoencoder model and introduces adversarial training based on (5) to
enhance the representation ability of the model. FuSAGNet [67]
introduces graph learning on the sparse autoencoder to model
relationships in multivariate time series explicitly.
Denoising autoencoder (DAE) is another widely used approach, which is based on the addition of noise to the input
series to corrupt the data, and then followed by the reconstruction
task [68]. DAE can be formulated as:
xn = T (x), Z = E(xn ), x̃ = D(z),

(6)

where T indicates the operation that adds noise. The learning
objective of a DAE is the same as that of a BAE, which is
to minimize the difference between x and x̃. In time series
modeling, more than one method can add noise to the input,
such as adding Gaussian noise [69], [70] and randomly setting
some time steps to zero [71], [72].
Mask autoencoder (MAE) is a structure widely used in language models and vision models in recent years [11], [73]. The
core idea behind MAE is that in the pre-training phase, the model
first masks part of the input and then tries to predict the masked
part through the unmasked part. Unlike BAE and DAE, the loss
of MAE is only computed on the masked part. MAE can be
formulated as:
xm = M(x), z = E(xm ), x̃ = D(z),

(7)

L = M(x − x̃2 ),

(8)

where M(·) represents the mask operation, and Xm represents
the masked input. In language models, since the input is usually
a sentence, the mask operation masks some words in a sentence
or replaces them with other words. In vision models, the mask
operation will mask the pixels or patches in an image. For time
series data, a feasible operation is to mask part of the time steps
and then use the unmasked part to predict the masked time steps.
Existing masking methods for time series data can be divided
into three categories: time-step-wise masking, segment-wise
masking, and variable-wise masking.
The time-step-wise masking randomly selects a certain proportion of time-steps in the series to mask, so the fine-grained information is easier to capture, but it is difficult to learn contextual
semantic information in time series. The segment-wise masking
randomly selects segments to mask, which allows the model to
pay more attention to slow features in the time series, such as
trends or high-level semantic information. STEP [74] divided the
series into multiple non-overlapping segments of equal length
and then randomly selected a certain proportion of the segments
for masking. Moreover, STEP pointed out two advantages of
using segment-wise masking: the ability to capture semantic
information and reduce the input length to the encoder. Different
from STEP, Zerveas et al. [75] performed a more complex masking operation on the time series, i.e., the multivariate time series
was randomly divided into multiple non-overlapping segments
of unequal length on each variable. Variable-wise masking was
introduced by Chauhan et al. [76], who defined a new time series
forecasting task called variable subset forecast (VSF). In VSF,

the time series samples used for training and inference have
different dimensions or variables, which may be caused by the
absence of some sensor data. This new forecasting task brings
the feasibility of self-supervised learning based on variable-wise
masking. Unlike random masking, TARNet [77] considers the
pre-trained model based on the masking strategy irrelevant to the
downstream task, which leads to sub-optimal representations.
TARNet uses self-attention score distribution from downstream
task training to determine the time steps that require masking.
Variational autoencoder (VAE) is a model based on variational
inference [78], [79]. The encoder encodes the input x to the probability distribution P (z|x) instead of the explicit representation
z. When the decoder is used to reconstruct the input, a vector
generated by sampling from the distribution P (z|x) will be used
as input to the decoder. The process can be expressed as:
P (z|x) = E(x), z = S(P (z|x)), x̃ = D(z),

(9)

where S(·) represents the sampling operation. Unlike (5), the
loss function of a VAE includes two terms: the reconstruction
item and the regularization item, i.e.,
L = x − x̃2 + KL(N (μ, δ), N (0, I)),

(10)

where KL(·) represents the Kullback-Leibler divergence. The
role of the regularization term is to ensure that the learned
distribution P (z|x) is close to the standard normal distribution,
thereby regulating the representation of the latent space. The
representation learning method based on VAE can model the
distribution of each time step to better capture the complex
spatiotemporal dependencies and provide better interpretability
in time series modeling tasks. For example, InterFusion [80]
is a hierarchical VAE that models inter-variable and temporal
dependencies in time series data. OmniAnomaly [81] combines
VAE and Planar Normalizing Flow to propose an interpretable
time series anomaly detection algorithm. In order to better capture the dependencies between different variables in multivariate
time series, GRELEN [82] and VGCRN [83] introduce the graph
structure and in VAE. In addition to modeling on regular time
series, the methods based on VAE have made progress in sparse
and irregular time series data representation learning, such as
mTANs [84], P-VAE [85] and HetVAE [86]. The latest work
attempts to extract seasonal and trend representations in time
series data based on VAE. LaST [87] is a disentangled variational
inference framework with mutual information constraints. It
separates seasonal and trend representations in the latent space
to achieve accurate time series forecasting.
C. Diffusion-Based Generation
As a new kind of deep generative model, diffusion models
have achieved great success recently in many fields, including
image synthesis, video generation, speech generation, bioinformatics, and natural language processing due to their powerful
generating ability [88], [89], [90], [91], [92]. The key design of
the diffusion model contains two inverse processes: the forward
process of injecting random noise to destruct data and the
reverse process of sample generation from noise distribution
(usually normal distribution). The intuition is that if the forward

ZHANG et al.: SSL FOR TIME SERIES ANALYSIS: TAXONOMY, PROGRESS, AND PROSPECTS

process is done step-by-step with a transition kernel between
any two adjacent states, then the reverse process can follow a
reverse state transition operation to generate samples from noise
(the final state of the forward process). However, it is usually
not easy to formulate the reverse transition kernel, and thus
diffusion models learn to approximate the kernel by deep neural
networks. Nowadays, there are mainly three basic formulations
of diffusion models: denoising diffusion probabilistic models
(DDPMs) [88], [93], score matching diffusion models [94], [95],
and score SDEs [96], [97].
For DDPMs, the forward and reverse processes are two
Markov chains: a forward chain that adds random noise to
data and a reverse chain that transforms noise back into data.
Formally, denote the data distribution as x0 ∼ q(x0 ), the forward Markov process gradually adds Gaussian noise to the
data according to transition kernel q(xt |xt−1 ). It generates a
sequence of random variables x1 , x2 , . . . , xT . Thus the joint
distribution of x1 , x2 , . . . , xT conditioned on x0 is
q(x1 , x2 , . . . , xT |x0 ) =

T


q(xt |xt−1 ).

(11)

t=1

For simplicity of calculation, the transition kernel is usually set
as
 

q(xt |xt−1 ) = N xt ; 1 − βt xt−1 , βt I ,
(12)
where β1 , β2 , . . . , βT is a variance schedule of the forward
process (usually chosen βt ∈ (0, 1) ahead of model training)
and p(xT ) = N (xT ; 0, I). Similarly, the joint distribution of
the reverse process is
pθ (x0 , x1 , . . . , xT ) = p(xT )

T


pθ (xt−1 |xt ),

(13)

t=1

where θ is the model parameters and pθ (xt−1 |xt ) =
N (xt−1 ; μθ (xt , t), θ (xt , t)). The key to achieving the success of sample generating is training the parameters θ to match
the actual reverse process, that is, minimizing the KullbackLeibler divergence between the two joint distributions. Thus,
according to Jensen’s inequality, the training loss is
KL(q(x1 , x2 , . . . , xT )||pθ (x0 , x1 , . . . , xT ))
≥ E[− log pθ (x0 )] + const.

(14)

For score-based diffusion models, the key idea is to perturb
data with a sequence of Gaussian noise and then jointly estimate
the score functions for all noisy data distributions by training a
deep neural network conditioned on noise levels. The motivation
of the idea is that, in many situations, it is easier to model and
estimate the score function than the original probability density
function. Langevin dynamics is one of the proper techniques.
With a step size α > 0, the number of iterations T , and an initial
sample x0 , Langevin dynamics iteratively does the following
estimation to gain a close approximation of p(x)
√
xt ← xt−1 + α∇x log p(xt−1 ) + 2αz t , 1 ≤ t ≤ T, (15)
where z t ∼ N (0, I). However, the score function is inaccurate
without the training data, and Langevin dynamics may not

6781

converge correctly. Thus, the key approach (NCSN, a noiseconditional score network), perturbing data with a noise sequence and jointly estimating the score function for all the
noisy data with a deep neural network conditioned on noise
levels, is proposed [94]. Training and sampling are decoupled in
score-based generative models, which inspires different choices
in such two processes [95].
For score SDEs, the diffusion operation is processed according to the stochastic differential equation (SDE) [97]:
dx = f (x, t)dt + g(t)dw,

(16)

where f (x, t) and g(t) are diffusion function and drift function
of the SDE, respectively, and w is a standard Wiener process.
Different from DDPMs and SGMs, Score SDEs generalize the
diffusion process to the case of infinite time steps. Fortunately,
DDPMs and SGMs also can be formulated with corresponding
SDEs. For DDPMs, the SDE is

1
(17)
dx = − β(t)xdt + β(t)dw,
2
where β( Tt ) = T βt when T goes to infinity; for SGMs, the SDE
is
dx =

d[δ(t)2 ]
dw,
dt

(18)

where δ( Tt ) = δt as T goes to infinity. With any diffusion process
in the form of (16), the reverse process can be gained by solving
the following SDE:
dx = [f (x, t) − g(t)2 ∇x log qt (x)]dt + g(t)dw,

(19)

where w is a standard Wiener process when time flows reversely
and dt is an infinitesimal time step. Besides that, the existence
of an ordinary differential equation, which is also called the
probability flow ODE, is defined as follows.
1
(20)
dx = [f (x, t) − g(t)2 ∇x log qt (x)]dt.
2
The trajectories of the probability flow ODE have the same
marginals as the reverse-time SDE. Once the score function at
each time step is known, the reverse SDE can be solved with
various numerical techniques. Similar objective is designed with
SGMs.
Diffusion models have also been applied in time series analysis recently. We briefly summarize them based on the designed
architectures and the main diffusion techniques used. Conditional score-based diffusion models for imputation (CSDI) [98]
were proposed for time series imputation task. CSDI utilizes
score-based diffusion models conditioned on observed data. In
time series forecasting tasks, TimeGrad [99] takes an RNN
conditioned diffusion probabilistic model at some time step
to depict the fixed forward process and the learned reverse
process. D3 VAE [100] is a bidirectional variational auto-encoder
(BVAE) equipped with diffusion, denoise, and disentanglement.
In D3 VAE, the coupled diffusion process augments the input
time series and output time series simultaneously. ImDiffusion [101] combines imputation and diffusion models for time
series anomaly detection. SSSD [102] combines diffusion models and structured state space models for time series imputation

6782

Fig. 3.

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

Five categories of contrastive-based SSL for time series data.

and forecasting tasks. DiffLoad [103] proposes a diffusion-based
structure for electrical load probabilistic forecasting by considering both epistemic and aleatoric uncertainties. DiffSTG [104]
presents the first shot to predict the evolution of spatio-temporal
graphs using DDPMs.
IV. CONTRASTIVE-BASED METHODS
Contrastive learning is a widely used self-supervised learning
strategy, showing a strong learning ability in computer vision
and natural language processing. Unlike discriminative models
that learn a mapping rule to true labels and generative models
that try to reconstruct inputs, contrastive-based methods aim to
learn data representations by contrasting between positive and
negative samples. Specifically, positive samples should have
similar representations, while negative samples have different
representations. Therefore, the selection of positive samples
and negative samples is very important to contrastive-based
methods. This section sorts out and summarizes the existing
contrastive-based methods in time series modeling according to
the selection of positive and negative samples. The illustration
of the contrastive-based SSL for time series is shown in Fig. 3.
In Appendix E.1–E.5, available online, the main advantages
and disadvantages of five contrastive-based submethods are
summarized.
A. Sampling Contrast
Sampling contrast follows a widely used assumption in time
series analysis that two neighboring time windows or time
stamps have a high degree of similarity, so positive and negative
samples are directly sampled from the raw time series, as shown
in Fig. 3(a). Specifically, given a time window (or a timestamp)
as an anchor, its nearby window (or the time stamp) is more
likely to be similar (small distance), and the distant window (or
the time stamp) should be less similar (large distance). The term
“similar” indicates that two windows (or two-time stamps) have
more common patterns, such as the same amplitude, the same
periodicity, and the same trend.

As mentioned in [105], suppose one anchor xref , one positive sample xpos , and K negative samples xneg
k , k∈1,2,...,K are
chosen, we expect to assimilate xref and xpos and to distinguish
between xref and xneg
k , i.e.,
L = − log(S(xref , xpos )) −

K


log(−S(xref , xneg
k )), (21)

k=1

where S(·) denotes the similarity of the two representations.
However, due to the non-stationary characteristics of most time
series data, it is still a challenge to choose the correct positive
and negative samples based on contextual information in time
series data. Temporal neighborhood coding (TNC) was recently
proposed to deal with this problem [106]. TNC uses augmented
Dickey-Fuller (ADF) statistical test to determine the stationary
region and introduces positive-unlabeled (PU) learning to handle
the problem of sampling bias by treating negative samples as
unknown samples and then assigning weights to these samples.
The learning objective is extended to
L = − Expos [∈N log S(xref , xpos )]
− Exneg ∈Ñ [(1 − w) × log −S(xref , xneg )
+ w × log S(xref , xneg )],

(22)

where w is the probability of sampling false negative samples, N denotes the neighboring area, and Ñ denotes the nonneighboring area. Supervised contrastive learning (SCL) [107]
effectively addresses sampling bias, so introducing the supervised signal to identify positive and negative samples is a feasible
solution. Neighborhood contrastive learning (NCL) is a recent
time series modeling method that combines context sampling
and the supervised signal to generate positive and negative
samples [108]. NCL assumes that if two samples share some
predefined attributes, then they are considered to share the same
neighboring area.

ZHANG et al.: SSL FOR TIME SERIES ANALYSIS: TAXONOMY, PROGRESS, AND PROSPECTS

B. Prediction Contrast
In this category, prediction tasks that use the context (present)
to predict the target (future information) are considered selfsupervised pretext tasks, and the goal is to maximally preserve
the mutual information of the context and the target. Contrastive predictive coding (CPC) proposed by [109] provides
a contrastive learning framework to perform the prediction task
using InfoNCE loss. As shown in Fig. 3(b), the context ct and
the sample from p(xt+k |ct ) constructs positive pairs, and the
samples from the ‘proposal’ distribution p(xt+k ) are negative
samples. The learning objective is as follows:
L = −E log
X

fk (xt+k , ct )
,
xj ∈X fk (xj , ct )

(23)

where fk (·) is the density ratio that preserves the mutual information of ct and xt+k [109], and it can be estimated by a simple
log-bilinear model:
T
Wk ct ).
fk (xt+k , ct ) = exp(zt+k

(24)

It can be seen that CPC does not directly predict future
observations xt+k . Instead, it tries to preserve the mutual information of ct and xt+k . This allows the model to capture
the “slow features” that span multiple time steps. Following the
architecture of CPC, LNT [110], TRL-CPC [111], TS-CP2 [112],
and Skip-Step CPC [113] were proposed. LNT and TRL-CPC
use the same structure as the original CPC [109] to build a
representation learning model, and the purpose is to capture the
local semantics across the time to detect the anomaly points.
TS-CP2 and Skip-Step CPC replace the autoregressive model
in the original CPC structure with TCN [114], which improves
feature learning ability and computational efficiency. Moreover,
Skip-Step CPC points out that adjusting the distance between
context representation ct and xt+k can construct different positive pairs, which leads to different results in time series anomaly
detection.
In addition to the basic contextual prediction tasks mentioned
before, some more complex prediction tasks were constructed
and proved useful. CMLF [115] transforms time series into
coarse-grained and fine-grained representations and proposes
a multi-granularity prediction task. This allows the model to
represent the time series at different scales. TS-TCC [116] and
its extended version CA-TCC [117] designed a cross prediction
task, which uses the context of xT 1 to predict the target in xT 2 ,
and vice versa uses the context of xT 2 to predict the target
in xT 1 .
C. Augmentation Contrast
Augmentation contrast is one of the most widely used contrastive frameworks, as shown in Fig. 3(c). Most methods utilize
data augmentation techniques to generate different views of
an input sample and then learn representations by maximizing
the similarity of the views that come from the same sample
and minimizing the similarity of the views that come from the
different samples. SimCLR [16] is a very typical multi-view
invariance-based representation learning framework, which has

6783

been used in many subsequent methods. The objective function
based on this framework is:
exp (sim (z 1 , z 2 ) /τ )
,
(25)
L = − log 2 N
k=1 [k=1] exp (sim (z 1 , z k ) /τ )
where τ is temperature parameter, sim(·) represents the similarity between two representation vectors, and zk represents
the training samples in a batch. It can be considered that in
the feature learning framework based on multi-view invariance,
the core is to obtain different views of the input samples.
When handling images in computer vision, commonly used
data augmentation methods include cropping, scaling, adding
noise, rotation, and resizing [16]. However, compared with
augmentation methods for images, the augmentation methods
for time series needs to consider both temporal and variable
dependencies.
Since time series data can be converted to frequency domain
representations through Fourier transform, the augmentation
method can be developed from the time and frequency domains.
In the time domain, TS-TCC [116] and its extended version
CA-TCC [117] designed two time series data augmentation techniques, one is strong augmentation (permutation-and-jitter), and
the other is weak augmentation (jitter-and-scale). TS2Vec [118]
generates different views through masking operations that randomly mask out some time steps. Generally speaking, there is
no one-size-fits-all answer to the choice of data augmentation
methods. Therefore, some works comprehensively compare and
study the augmentation methods and further evaluate the performance on different tasks [45], [119], [120], [121]. All the
above methods only need a single time series sample in the
augmentation operation, while Mixing-up [122] fuses two time
series samples to generate a newly augmented view, while the
pretext task is to correctly predict the proportion of two original
time series samples in augmented view.
Data augmentation in the frequency domain is also feasible
for time series data. CoST [123] is a disentangled seasonal-trend
representation learning method, which uses fast Fourier transform to convert different augmented views into amplitude and
phase representations, and then uses (25) to train the model.
BTSF [124] is a contrastive-based method based on a timefrequency fusion strategy, which first generates an augmented
view in the time domain through the dropout operation and
then generates another augmented view in the frequency domain through Fourier transform. Finally, the bilinear temporalspectral fusion mechanism is used to achieve the fusion of
time-frequency information. However, CoST and BTSF do not
modify the frequency representation, while TF-C [125] directly
augments the time series data through frequency perturbations,
which has achieved better performance than TS2Vec [118] and
TS-TCC [116]. Specifically, TF-C implements three augmentation strategies: low- versus high-band perturbations, singleversus multi-component perturbations, and random versus distributional perturbations.
In addition to the above methods, many view generation methods are closely related to downstream tasks. Recently, DCdetector [126] proposes a dual attention contrastive representation
framework for time series anomaly detection. The in-patch and

6784

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

patch-wise representations are designed to gain two views of
the input samples, as normal samples behave differently from
abnormal ones in such two views. TimeCLR [127] proposed
DTW augmentation, which can not only simulate phase shifts
and amplitude changes but also retain the structure and characteristics of the time series. CLOCS [128] is a self-supervised pretraining method for medical and physiological signals, which
uses multi-view invariance contrast in the three perspectives
of time, space, and patient to promote higher similarity of
representations from the same source. CLUDA [129] introduces
multi-view invariance contrast in the time series domain adaptation problem, which captures the contextual representation of
time series data through intra-domain and inter-domain contrast.
MTFCC [130] is another view generation method based on
multi-scale characteristics, which samples time series samples
at multiple scales and considers that the views from the same
sample have similar representations, even if their scales are
different. Methods for constructing multiple contrastive views
based on multi-granularity or multi-scale augmentations also
include MRLF [131], CMLF [115], and SSLAPP [132].
D. Prototype Contrast
The contrastive learning framework based on (23) and (25)
is essentially an instance discrimination task, which encourages samples to form a uniform distribution in the feature
space [133]. However, the real data distribution should satisfy
that the samples of the same class are more concentrated in
a cluster, while the distance between different clusters should
be farther. SCL [107] is an ideal solution when real labels are
available, but this is difficult to implement in practice, especially
for time series data. Therefore, introducing clustering constraints
into existing contrastive learning frameworks is an alternative,
such as CC [134], PCL [135], and SwAV [36]. PCL and SwAV
contrast the samples with the constructed prototypes, i.e., the
cluster centers, which reduces the computation and encourages
the samples to present a cluster-friendly distribution in the
feature space. An illustration of prototype contrast is shown in
Fig. 3(d).
In time series modeling based on prototypes contrast,
ShapeNet [136] takes shapelets as input and constructs a clusterlevel triplet loss, which considers the distance between the
anchor and multiple positive (negative) samples as well as
the distance between positive (negative) samples. ShapeNet is
an implicit prototype contrast because it does not introduce
explicit prototypes (cluster centers) during the training phase.
TapNet [137] and DVSL [138] are explicit prototypes contrast because explicit prototypes are introduced. TapNet introduces a learnable prototype for each predefined class and
classifies the input time series sample according to the distance between the sample and each class prototype. DVSL
defines virtual sequences, which have the same function as
prototypes, i.e., minimize the distance between samples and
virtual sequences, but maximize the distance between virtual
sequences. MHCCL [139] proposes a hierarchical clustering
based on the upward masking strategy and a contrastive pairs
selection strategy based on the downward masking strategy. In

the upward mask strategy, MHCCL believes that outliers greatly
impact prototypes, so these outliers should be removed when
updating prototypes. The downward masking strategy, in turn,
uses the clustering results to select positive and negative samples,
i.e., samples belonging to the same prototype are regarded as true
positive samples, and samples belonging to different prototypes
are regarded as true negative samples.
E. Expert Knowledge Contrast
Expert knowledge contrast is a relatively new representation
learning framework. Generally speaking, this modeling framework incorporates expert prior knowledge or information into
deep neural networks to guide model training [140], [141]. In the
contrastive learning framework, prior knowledge can help the
model choose the correct positive and negative samples during
training. An example of expert knowledge contrast is shown in
Fig. 3(e).
Here we sort out three typical works of expert knowledge
contrast for time series data. Shi et al. [142] used the DTW
distance of time series samples as prior information and believed
that two samples with a small DTW distance have a higher
similarity. Specifically, given the anchor xref and the other two
samples xi and xj , the DTW distance between xref and the
other two samples is calculated first, then the sample with a
small distance from xref is considered as the positive sample of
xref . This selection process is defined as




1, DTW xref , xi ≥ DTW xref , xj
label =
. (26)
0, otherwise
Based on pair-loss, ExpCLR [143] introduces expert features
of time series data to obtain more informative representations.
Given two input samples xi and xj and corresponding representations fi and fj , ExpCLR defines the normalized distance
between two samples:
sij = 1 −

fi − fj 2
,
max fk − fl  2

(27)

where fk and fl are the two representation vectors with the
largest distance among all samples. Compared with the original
pair-loss, the distance between samples xi and xj is changed
from a discrete value (0 and 1) to a continuous value sij ,
which enables the model to learn more accurately about the
relationship between samples, thus thereby enhancing the representation ability of the model. In addition to the above two works,
SleepPriorCL [144] was proposed to alleviate the sampling
bias problem faced by (25). Like ExpCLR, SleepPriorCL also
introduces prior features to ensure the model can identify correct
positive and negative samples.
Actually, introducing more prior knowledge in contrastivebased SSL can help the model extract better representations.
The trend of this family of methods can be summarized from
two perspectives: (i) Addressing sampling bias. Sampling bias
is caused by inappropriate selection of positive and negative
samples, so introducing prior knowledge useful for selecting
positive and negative samples can deal with this problem, such
as a clustering-based negative sample detection algorithm [145]

ZHANG et al.: SSL FOR TIME SERIES ANALYSIS: TAXONOMY, PROGRESS, AND PROSPECTS

6785

the main advantages and disadvantages of two adversarial-based
submethods are summarized. Furthermore, the main differences
in characteristics and limitations between the adversarial-based
methods and the previous two methods (generative-based and
contrastive-based) are shown in Appendix G, available online.
A. Time Series Generation and Imputation

Fig. 4.

Three categories of adversarial-based SSL for time series data.

and sample identification strategy based on real labels [107],
[108]. (ii) Addressing representation bias. Representation bias
means that the extracted representations cannot be guaranteed to
be strongly related to the downstream task. The essential reason
is that there may be a big difference between the goals of the
pretext task and the downstream task. An interesting trend is
to fuse semi-supervised learning and contrastive-based SSL to
guide the training of the encoder through a small amount of
labeled data [146], [147].
V. ADVERSARIAL-BASED METHODS
Adversarial-based self-supervised representation learning
methods utilize generative adversarial networks (GANs) to
construct pretext tasks. GAN contains a generator G and a
discriminator D. The generator G is responsible for generating
synthetic data similar to real data, while the discriminator D is
responsible for determining whether the generated data is real
data or synthetic data. Therefore, the goal of the generator is
to maximize the decision failure rate of the discriminator, and
the goal of the discriminator is to minimize its failure rate [49],
[148]. The generator G and the discriminator D are a mutual
game relationship, so the learning objective is:
L = Ex∼Pdata (x) [log D(x)] + Ez∼Pz (z) [log(1 − D(G(z)))].
(28)
According to the final task, the existing adversarial-based representation learning methods can be divided into time series generation and imputation, and auxiliary representation enhancement. The illustration of the adversarial-based SSL for time
series is shown in Fig. 4. In Appendix F.1–F.2, available online,

The generator in the GAN can generate synthetic data close
to the real data, so adversarial representation learning has a
wide range of applications in the data generation field [149],
especially in image generation [150], [151], [152], [153]. In
recent years, many scholars have also explored the potential
of generative representation learning in time series generation
and imputation, such as C-RNN-GAN [154], TimeGAN [155],
TTS-GAN [156], and E 2 GAN [157]. It should be emphasized
that although Brophy et al. [49] have reviewed the GAN-based
time series generation methods in the latest survey, it differs
from the proposed taxonomy. We sort out the two aspects of
complete time series generation and missing value imputation,
while Brophy et al. sorted out from the perspective of discrete
and continuous time series modeling.
Complete time series generation refers to generating a new
time series that does not exist in the existing data set. The new
sample can be a univariate or multivariate time series. C-RNNGAN [154] is an early method of generating time series samples
using GAN. The generator is an RNN, and the discriminator
is a bidirectional RNN. RNN-based structures can capture the
dynamic dependencies in multiple time steps but ignore the
static features of the data. TimeGAN [155] is an improved time
series generation framework that combines the basic GAN with
the autoregressive model, allowing the preservation of temporal
dynamic characteristics of the series. TimeGAN also emphasizes
that static features and temporal characteristics are crucial to the
generation task.
Some recently proposed methods consider more complex time
series generative tasks [156], [158], [159], [160]. For example,
COSCI-GAN [158] is a time series generation framework that
considers the correlation between each dimension of the multivariate time series. It includes Channel GANs and Central Discriminator. Channel GANs are responsible for generating data
in each dimension independently, while Central Discriminator
is responsible for determining whether the correlation between
different dimensions of the generated series is the same as the
raw series. PSA-GAN [159] is a framework for long-time series
generation and introduces a self-attention mechanism. It further
presents Context-FID, a new metric for evaluating the quality
of generated series. Li et al. [156] explored the generation of
time series data with irregular spatiotemporal relationships and
proposed TTS-GAN, which uses a Transformer instead of an
RNN to build the discriminator and the generator and treats the
time series data as image data of height one.
Different from generating a new time series, the task of time
series imputation refers to that given a non-complete time series
sample (for example, the data of some time steps is missing),
and the missing values need to be filled based on the contextual
information. Luo et al. [161] treat the problem of missing value
imputation as a data generation task and then use GAN to learn

6786

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

the distribution of the training data set. In order to better capture
the dynamic characteristics of the series, the GRUI module was
proposed. The GRUI uses the time-lag matrix to record the timelag information between effective values of incomplete time
series data, which follow the unknown non-uniform distribution
and are very helpful for analyzing the dynamic characteristics
of the series. The GRUI module was also further used in E
2
GAN [157]. SSGAN [162] is a semi-supervised framework
for time series data imputation, which includes a generative
network, a discriminative network, and a classification network.
Unlike previous frameworks, SSGAN’s classification network
makes full use of label information, which helps the model
achieve more accurate imputations.

TABLE II
SUMMARY OF TIME SERIES APPLICATIONS AND WIDELY USED DATASETS

B. Auxiliary Representation Enhancement
In addition to generation and interpolation tasks, an
adversarial-based representation learning strategy can be added
to existing learning frameworks as additional auxiliary learning
modules, which we call adversarial-based auxiliary representation enhancement. The auxiliary representation enhancement
aims to promote the model to learn more informative representations for downstream tasks by adding adversarial-based learning
strategies. It can be defined as:
L = Lbase + Ladv ,

(29)

where Lbase is the basic learning objective and Ladv is the
additional adversarial-based learning objective. It should be
noted that when Ladv is not available, the model can still extract
representations from the data, so Ladv is regarded as an auxiliary
learning objective.
USAD [66] is a time series anomaly detection framework
that includes two BAE models, and two BAE are defined as
AE1 and AE2 , respectively. The core idea behind USAD is to
amplify the reconstruction error by adversarial training between
two BAEs. In USAD, AE1 is regarded as the generator, and
AE2 is regarded as the discriminator. The auxiliary goal is to
use AE2 to distinguish real data from reconstructed data from
AE1 , and train AE1 to deceive AE2 , the whole process can be
expressed as:
Ladv = min max W − AE2 (AE1 (W ))2 ,
AE1 AE2

(30)

where W is the real input series. Similar to USAD, AnomalyTrans [163] also uses an adversarial strategy to amplify the
anomaly score of anomalies. But unlike (30), which uses reconstruction error, AnomalyTrans defines prior-association and
series-association and then uses the Kulback-Leibler divergence
to measure the error of the two associations.
DUBCNs [164] and CRLI [165] are used for series retrieval
and clustering tasks, respectively. Both methods adopt RNNbased BAE as the model, and the clustering-based loss and
adversarial-based loss are added to the basic reconstruction loss,
i.e.,
L = Lmse + λ1 Lcluster + λ2 Ladv .

(31)

where λ1 and λ2 are the weight coefficients of the auxiliary
objective.

The adversarial-based strategy is also effective in other time
series modeling tasks. For example, introducing adversarial
training in time series forecasting can improve the accuracy
and capture long-term repeated patterns, such as AST [166] and
ACT [167]. BeatGAN [168] introduces adversarial representation learning in the abnormal beat detection task of ECG data
and provides an interpretable detection framework. In modeling
behavior data, Activity2vec [169] uses adversarial-based training to model target invariance and enhance the representation
ability of the model in different behavior stages.
VI. APPLICATIONS AND DATASETS
SSL has many applications across different time series tasks.
This section summarizes the most widely used datasets and
representative references according to the application area, including anomaly detection, forecasting, classification, and clustering. As shown in Table II, we provide useful information,
including dataset name, dimension, size, source, and useful
comments. For each task, we summarize from the following
aspects: task description, related methods, evaluation metrics,
examples, and task flow. Due to space limitations, relevant
descriptions of evaluation metrics, examples, and task flow
can be found in Appendix H, available online. In addition, we
provide performance comparison results of different methods on
the same dataset and further summarize the correlation between
methods and tasks, the details can also be found in Appendix I,
available online.
A. Anomaly Detection

r Task description: The anomaly detection problem for time
series is usually formulated as identifying outlier time

ZHANG et al.: SSL FOR TIME SERIES ANALYSIS: TAXONOMY, PROGRESS, AND PROSPECTS

points or unexpected time sequences relative to some norm
or usual signal.
r Related methods: Most time series anomaly detection
methods are constructed under an unsupervised learning framework because obtaining labels for anomalous
data is challenging. Autoregressive-based forecasting and
autoencoder-based reconstruction are the most commonly
used modeling strategies. To be concrete, THOC [52]
and GDN [55] employ autoregressive-based forecasting
SSL framework, which assumes that anomalous sequences
or time points are not predictable. RANSynCoders [63],
USAD [66], AnomalyTrans [163], and DAEMON [184]
employ autoencoder-based reconstruction SSL framework.
Furthermore, VGCRN [83] and FuSAGNet [67] combine
two frameworks to achieve more robust and accurate results. It is beneficial to introduce an adversarial-based
SSL, which can further amplify the difference between
normal and anomalous data, such as USAD [66] and DAEMON [184].
B. Forecasting

r Task description: Time series forecasting is the process of
analyzing time series data using statistics and modeling to
make predictions of future windows or time points.
r Related methods: The pretext task based on autoregressivebased forecasting is essentially a time series forecasting task. Therefore, various models based on forecasting
tasks are proposed, such as Pyraformer [185], FilM [15],
Quatformer [186], Informer [173], Triformer [187], Scaleformer [188], Crossformer [189], and Timesnet [190].
Moreover, we found that decomposing the series (seasonality and trend) and then learning and forecasting on
the decomposed components will help improve the final
forecasting accuracy, such as MICN [191] and CoST [123].
Besides, introducing an adversarial SSL is viable when
missing values are in the series. For example, LGnet [192]
introduces adversarial training to enhance the modeling of
global temporal distribution, which mitigates the impact of
missing values on forecasting accuracy.
C. Classification and Clustering

r Task description: The goal of classification and clustering
tasks is similar, i.e., to identify the real category to which
a certain time series sample belongs.
r Related methods: Contrastive-based SSL methods are the
most suitable choice for these two tasks since the core
of contrastive learning is identifying positive and negative
samples. Specifically, TS-TCC [116] introduces temporal
contrast and contextual contrast in order to obtain more
robust representations. TS2Vec [118] and MHCCL [139]
perform a hierarchical contrastive learning strategy over
augmented views, which enables robust representations.
Similar to anomaly detection and prediction tasks, an
adversarial-based SSL strategy can also be introduced into
classification and clustering tasks. DTCR [65] propose a
fake-sample generation strategy to assist the encoder in
obtaining more expressive representations.

6787

VII. DISCUSSION AND FUTURE DIRECTIONS
In this section, we point out some critical problems in current
studies and outline several research directions worthy of further
investigation.
A. Selection and Combination of Data Augmentation
Data augmentation is one of the effective methods to generate augmented views in SSCL [47], [193]. The widely used
methods for time series data include jitter, scaling, rotation,
permutation, and warping [45], [119], [120], [121], [194]. In
SimCLR [16], nine different augmentation methods for image
data were discussed. The experiments show that “no single
transformation suffices to learn good representations” and “the
composition of random cropping and random color distortion is
the most effective augmentation method”. This naturally raises
the question of which one or composition of data augmentation
methods is optimal for time series. Recently, Um et al. [195]
show that the combination of three basic augmentation methods
(permutation, rotation, and time warping) is better than that of a
single method and achieves the best performance in time series
classification task. Iwana et al. [121] evaluate twelve time series
data augmentation methods on 128 time series classification
datasets with six different types of neural networks. Different
evaluation frameworks give different recommendations and results. Therefore, an interesting direction is to construct a reasonable evaluation framework for time series data augmentation
methods, then further select the optimal method or combination
strategy.
B. Inductive Bias for Time Series SSL
Existing SSL methods often pursue an entirely data-driven
modeling approach. However, introducing reasonable inductive
bias or prior is helpful for many deep neural networks-based
modeling tasks [140], [196], [197]. On the one hand, although a
purely data-driven model can be easily extended to various tasks,
it requires much data to train it. On the other hand, time series
data usually has some available characteristics, such as seasonal,
periodic, trend, and frequency domain biases [198], [199], [200].
Thus one future direction is to consider more effective ways
to induce inductive biases into time series SSL based on the
understanding of time series data and characteristics of specific
tasks.
C. SSL for Irregular and Sparse Time Series
Irregular and sparse time series also widely exist in various
scenarios. This data is measured at irregular time intervals, and
not all the variables are available for each sample [201]. The
straightforward approach to deal with irregular and sparse time
series data is to use interpolation algorithms to estimate missing values [161], [162], [202]. However, interpolation-based
models add undesirable noise and extra overhead to the model
which usually worsens as the time series become increasingly
sparse [54]. Moreover, irregular and sparse time series data is
often expensive to obtain sufficient labeled data, which motivates
us to build time series analysis models based on SSL in various

6788

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

tasks. Therefore, building SSL models directly on irregular
and sparse time series data without interpolation is a valuable
direction.
D. Pretraining and Large Models for Time Series
Nowadays, many large language models have shown their
powerful perception and learning capability for many different
tasks. A similar phenomenon also appears in computational
vision [203]. It is naturally an interesting question, how about
the time series analysis field? As far as we know, there is limited
work on pretraining models in large-scale time series. Exploring
the potentiality of pretraining and large time series models is a
promising direction.
E. Adversarial Attacks and Robust Analysis on Time Series
With the widespread use of deep neural networks in time
series forecasting, classification, and anomaly detection, the
vulnerability and robustness of deep models under adversarial
have become a significant concern [204], [205], [206], [207]. In
the field of time series forecasting, Liu et al. [205] study the indirect and sparse adversarial attacks on multivariate probabilistic
forecasting models for time series forecasting and propose two
defense mechanisms: randomized smoothing and mini-max defense. Wu et al. [206] propose an attack strategy for generating
an adversarial time series by adding malicious perturbations to
the original time series to deteriorate the performance of time
series prediction models. Zhuo et al. [208] summarize and compare various recent and typical adversarial attack and defense
methods for fault classifiers in data-driven fault detection and
classification systems, including white-box attack (FGSM [209],
IGSM [210], C & W attack [211], DeepFool [212]) and gray-box
and black-box attack (UAP [213], SPSA [214], Random noise).
The research on adversarial attacks and defenses against time
series data is a worthwhile direction, but there is much less
literature on this topic. Existing studies mainly involve forecasting and classification tasks. However, the impact of adversarial
examples on time series self-supervised pre-training tasks is still
unknown.
F. Benchmark Evaluation for Time Series SSL
SSL has many applications in time series classification, forecasting, clustering, and anomaly detection. However, most current research seeks to achieve the best performance on specific
tasks and needs more discussion and evaluation of the selfsupervised technique. One interesting direction is to pay more
attention to SSL, analyze its properties in time series modeling
tasks, and give reliable benchmark evaluation.
G. Time Series SSL in Collaborative Systems
Distributed systems have been widely deployed in many
scenarios, including intelligent control systems, wireless sensor networks, network file systems, etc. On the one hand, an
appropriate collaborative learning strategy is fundamental in
these systems, as users can train their own local models without
sharing their private local data and circumventing the relevant
privacy policy [215]. On the other hand, time series data is

also widely distributed in various places in the system, and
obtaining sufficient labeled data is also difficult, so time series
SSL has great deployment potential [216], [217]. In recent
years, federated learning has been the most popular collaborative
learning framework and has been used successfully in various
applications. Combining time series self-supervised learning
and federated learning is a valuable research direction that
can provide additional modeling tools for modern distributed
systems.
VIII. CONCLUSION
This article concentrates on time series SSL methods
and provides a new taxonomy. We categorize the existing methods into three broad categories according to their
learning paradigms: generative-based, contrastive-based, and
adversarial-based. Moreover, we sort out all methods into
ten detailed subcategories: autoregressive-based forecasting,
autoencoder-based reconstruction, diffusion-based generation,
sampling contrast, prediction contrast, augmentation contrast,
prototypes contrast, expert knowledge contrast, generation and
imputation, and auxiliary representation enhancement. We also
provide useful information about applications and widely used
time series datasets. Finally, multiple future directions are summarized. We believe this review fills the gap in time series SSL
and ignites further research interests in SSL for time series data.
REFERENCES
[1] Q. Wen, L. Yang, T. Zhou, and L. Sun, “Robust time series analysis and
applications: An industrial perspective,” in Proc. 28th ACM SIGKDD
Conf. Knowl. Discov. Data Mining, 2022, pp. 4836–4837.
[2] P. Esling and C. Agon, “Time-series data mining,” ACM Comput. Surv.,
vol. 45, no. 1, pp. 1–34, 2012.
[3] J. B. Yang, M. N. Nguyen, P. P. San, X. L. Li, and S. Krishnaswamy,
“Deep convolutional neural networks on multichannel time series for
human activity recognition,” in Proc. 24th Int. Conf. Artif. Intell., 2015,
pp. 3995–4001.
[4] K. Zhang, Y. Liu, Y. Gu, X. Ruan, and J. Wang, “Multiple-timescale
feature learning strategy for valve stiction detection based on convolutional neural network,” IEEE/ASME Trans. Mechatronics, vol. 27, no. 3,
pp. 1478–1488, Jun. 2022.
[5] S. Li, D. Hong, and H. Wang, “Relation inference among sensor time
series in smart buildings with metric learning,” in Proc. AAAI Conf. Artif.
Intell., 2020, pp. 4683–4690.
[6] Y. Xu, S. Biswal, S. R. Deshpande, K. O. Maher, and J. Sun, “RAIM:
Recurrent attentive and intensive model of multimodal patient monitoring
data,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2018, pp. 2565–2573.
[7] S. Gidaris, P. Singh, and N. Komodakis, “Unsupervised representation
learning by predicting image rotations,” in Proc. Int. Conf. Learn. Representations, 2018, pp. 1–16.
[8] R. Zhang, P. Isola, and A. A. Efros, “Split-brain autoencoders: Unsupervised learning by cross-channel prediction,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit., 2017, pp. 645–654.
[9] A. Dosovitskiy, J. T. Springenberg, M. Riedmiller, and T. Brox,
“Discriminative unsupervised feature learning with convolutional neural networks,” in Proc. Adv. Neural Inf. Process. Syst., 2014,
pp. 766–774.
[10] Y. Tian, D. Krishnan, and P. Isola, “Contrastive multiview coding,” in
Proc. Eur. Conf. Comput. Vis., Cham, 2020, pp. 776–794.
[11] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training
of deep bidirectional transformers for language understanding,” in Proc.
Conf. North Amer. Chapter Assoc. Comput. Linguistics: Hum. Lang.
Technol., Minneapolis, Minnesota, 2019, pp. 4171–4186.
[12] T. Gao, X. Yao, and D. Chen, “SimCSE: Simple contrastive learning
of sentence embeddings,” in Proc. Empirical Methods Natural Lang.
Process., 2021, pp. 6894–6910.

ZHANG et al.: SSL FOR TIME SERIES ANALYSIS: TAXONOMY, PROGRESS, AND PROSPECTS

[13] R. B. Cleveland, W. S. Cleveland, J. E. McRae, and I. Terpenning,
“STL: A seasonal-trend decomposition,” J. Official Stat., vol. 6, no. 1,
pp. 3–73, 1990.
[14] Q. Wen, Z. Zhang, Y. Li, and L. Sun, “Fast RobustSTL: Efficient
and robust seasonal-trend decomposition for time series with complex
patterns,” in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2020, pp. 2203–2213.
[15] T. Zhou et al., “Film: Frequency improved legendre memory model for
long-term time series forecasting,” in Proc. Adv. Neural Inf. Process.
Syst., pp. 12677–12690, 2022.
[16] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, “A simple framework
for contrastive learning of visual representations,” in Proc. 37th Int. Conf.
Mach. Learn., 2020, pp. 1597–1607.
[17] A. Jaiswal, A. R. Babu, M. Z. Zadeh, D. Banerjee, and F. Makedon,
“A survey on contrastive self-supervised learning,” Technologies, vol. 9,
no. 1, pp. 1–22, 2021.
[18] L. Jing and Y. Tian, “Self-supervised visual feature learning with deep
neural networks: A survey,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 43, no. 11, pp. 4037–4058, Nov. 2021.
[19] E. Eldele, M. Ragab, Z. Chen, M. Wu, C.-K. Kwoh, and X. Li,
“Label-efficient time series representation learning: A review,” 2023,
arXiv:2302.06433.
[20] S. Deldari, H. Xue, A. Saeed, J. He, D. V. Smith, and F. D. Salim,
“Beyond just vision: A review on self-supervised representation learning
on multimodal and temporal data,” 2022, arXiv:2206.02353.
[21] X. Liu et al., “Self-supervised learning: Generative or contrastive,” IEEE
Trans. Knowl. Data Eng., vol. 35, no. 1, pp. 857–876, Jan. 2023.
[22] Y. Bengio, A. Courville, and P. Vincent, “Representation learning: A
review and new perspectives,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 35, no. 8, pp. 1798–1828, Aug. 2013.
[23] S. Liu et al., “Audio self-supervised learning: A survey,” Patterns, vol. 3,
no. 12, 2022, Art. no. 100616.
[24] A. Mohamed et al., “Self-supervised speech representation learning: A
review,” IEEE J. Sel. Topics Signal Process., vol. 16, no. 6, pp. 1179–
1210, Oct. 2022.
[25] Y. Liu et al., “Graph self-supervised learning: A survey,” IEEE Trans.
Knowl. Data Eng., vol. 35, no. 6, pp. 5879–5900, Jun. 2023.
[26] Y. Xie, Z. Xu, J. Zhang, Z. Wang, and S. Ji, “Self-supervised learning
of graph neural networks: A unified review,” IEEE Trans. Pattern Anal.
Mach. Intell., vol. 45, no. 2, pp. 2412–2429, Feb. 2023.
[27] X. Qiu, T. Sun, Y. Xu, Y. Shao, N. Dai, and X. Huang, “Pre-trained models
for natural language processing: A survey,” Sci. China Technol. vol. 63,
pp. 1872–1897, 2020.
[28] L. Ericsson, H. Gouk, C. C. Loy, and T. M. Hospedales, “Self-supervised
representation learning: Introduction, advances, and challenges,” IEEE
Signal Process. Mag., vol. 39, no. 3, pp. 42–62, May 2022.
[29] P. H. Le-Khac, G. Healy, and A. F. Smeaton, “Contrastive representation learning: A framework and review,” IEEE Access, vol. 8,
pp. 193907–193934, 2020.
[30] J. Gui et al., “A survey on self-supervised learning: Algorithms, applications, and future trends,” 2023, arXiv:2301.05712.
[31] S. Latif, R. Rana, S. Khalifa, R. Jurdak, J. Qadir, and B. W. Schuller,
“Deep representation learning in speech processing: Challenges, recent
advances, and future trends,” 2020, arXiv: 2001.00378.
[32] L. Wu, H. Lin, C. Tan, Z. Gao, and S. Z. Li, “Self-supervised learning on
graphs: Contrastive, generative,or predictive,” IEEE Trans. Knowl. Data
Eng., vol. 35, no. 4, pp. 4216–4235, Apr. 2023.
[33] Z. Liu, A. Alavi, M. Li, and X. Zhang, “Self-supervised contrastive
learning for medical time series: A systematic review,” Sensors, vol. 23,
no. 9, 2023, Art. no. 4221.
[34] I. Misra and L. van der Maaten, “Self-supervised learning of pretextinvariant representations,” in IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Seattle, WA, USA, 2020, pp. 6706–6716.
[35] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum contrast for
unsupervised visual representation learning,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2020, pp. 9726–9735.
[36] M. Caron, I. Misra, J. Mairal, P. Goyal, P. Bojanowski, and A. Joulin,
“Unsupervised learning of visual features by contrasting cluster assignments,” in Proc. 34th Int. Conf. Neural Inf. Process. Syst., Red Hook,
NY, USA, 2020, pp. 9912–9924.
[37] A. Abanda, U. Mori, and J. A. Lozaono, “A review on distance
based time series classification,” Data Mining Knowl. Discov., vol. 33,
pp. 378–412, 2019.
[38] H. I. Fawaz, G. Forestier, J. Weber, L. Idoumghar, and P.-A. Muller,
“Deep learning for time series classification: A review,” Data Mining
Knowl. Discov., vol. 33, pp. 917–963, 2019.

6789

[39] B. Lim and S. Zohren, “Time-series forecasting with deep learning: A
survey,” Philos. Trans. Roy. Soc. A: Math., Phys. Eng. Sci., vol. 379,
no. 2194, Feb. 2021, Art. no. 20200209.
[40] O. B. Sezer, M. U. Gudelek, and A. M. Ozbayoglu, “Financial time
series forecasting with deep learning : A systematic literature review:
2005–2019,” Appl. Soft Comput., vol. 90, 2020, Art. no. 106181.
[41] Z. Liu, Z. Zhu, J. Gao, and C. Xu, “Forecast methods for time series data:
A survey,” IEEE Access, vol. 9, pp. 91896–91912, 2021.
[42] K. Benidis et al., “Deep learning for time series forecasting: Tutorial and
literature survey,” ACM Comput. Surv., vol. 55, no. 6, pp. 1–36, Dec.
2022.
[43] A. Blázquez-García, A. Conde, U. Mori, and J. A. Lozano, “A review
on outlier/anomaly detection in time series data,” ACM Comput. Surv.,
vol. 54, no. 3, pp. 1–33, Apr. 2021.
[44] A. A. Cook, G. Mısırlı, and Z. Fan, “Anomaly detection for IoT timeseries data: A survey,” IEEE Internet Things J., vol. 7, no. 7, pp. 6481–
6494, Jul. 2020.
[45] Q. Wen et al., “Time series data augmentation for deep learning: A
survey,” in Proc. 13th Int. Joint Conf. Artif. Intell., 2021, pp. 4653–4660.
[46] B. K. Iwana and S. Uchida, “An empirical survey of
data
augmentation
for
time
series
classification
with
neural networks,” PLoS ONE, vol. 16, no. 7, 2021,
Art. no. e0254841.
[47] G. Iglesias, E. Talavera, Á. González-Prieto, A. Mozo, and S. GómezCanaval, “Data augmentation techniques in time series domain: A
survey and taxonomy,” Neural Comput. Appl., vol. 35, no. 14,
pp. 10123–10145, 2023.
[48] Q. Wen et al., “Transformers in time series: A survey,” in Proc. Int. Joint
Conf. Artif. Intell., 2023, pp. 6778–6786.
[49] E. Brophy, Z. Wang, Q. She, and T. Ward, “Generative adversarial
networks in time series: A systematic literature review,” ACM Comput.
Surv., vol. 55, no. 10, pp. 1–31, Feb. 2023.
[50] M. Schirmer, M. Eltayeb, S. Lessmann, and M. Rudolph, “Modeling
irregular time series with continuous recurrent units,” in Proc. 39th Int.
Conf. Mach. Learn., vol. 162, pp. 19388–19405, 2022.
[51] Q. Tan et al., “DATA-GRU: Dual-attention time-aware gated recurrent
unit for irregular multivariate time series,” in Proc. AAAI Conf. Artif.
Intell., 2020, pp. 930–937.
[52] L. Shen, Z. Li, and J. Kwok, “Timeseries anomaly detection using temporal hierarchical one-class network,” in Proc. Adv. Neural Inf. Process.
Syst., 2020, pp. 13016–13026.
[53] S. Jawed, J. Grabocka, and L. Schmidt-Thieme, “Self-supervised learning
for semi-supervised time series classification,” in Proc. Adv. Knowl.
Discov. Data Mining, Cham, 2020, pp. 499–511.
[54] S. Tipirneni and C. K. Reddy, “Self-supervised transformer for sparse
and irregularly sampled multivariate clinical time-series,” ACM Trans.
Knowl. Discov. Data, vol. 16, no. 6, pp. 1–17, Jul. 2022.
[55] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 4027–4035.
[56] C. Shang, J. Chen, and J. Bi, “Discrete graph structure learning for forecasting multiple time series,” in Proc. Int. Conf. Learn. Representations,
2021, pp. 1–14.
[57] E. Dai and J. Chen, “Graph-augmented normalizing flows for anomaly
detection of multiple time series,” in Proc. Int. Conf. Learn. Representations, 2022, pp. 1–16.
[58] L. Xi, Z. Yun, H. Liu, R. Wang, X. Huang, and H. Fan, “Semi-supervised
time series classification model with self-supervised learning,” Eng. Appl.
Artif. Intell., vol. 116, 2022, Art. no. 105331.
[59] P. Baldi, “Autoencoders, unsupervised learning, and deep architectures,”
in Proc. ICML Workshop Unsupervised Transfer Learn., Bellevue,
Washington, USA, 2012, pp. 37–49.
[60] A. Abid and J. Zou, “Autowarp: Learning a warping distance from
unlabeled time series using sequence autoencoders,” in Proc. 32nd
Int. Conf. Neural Inf. Process. Syst., Red Hook, NY, USA, 2018,
pp. 10568–10578.
[61] P. Malhotra, V. TV, L. Vig, P. Agarwal, and G. Shroff, “TimeNet:
Pre-trained deep recurrent neural network for time series classification,”
2017, arXiv: 1706.08838.
[62] A. Sagheer and M. Kotb, “Unsupervised pre-training of a deep LSTMbased stacked autoencoder for multivariate time series forecasting problems,” Sci. Rep., vol. 9, 2019, Art. no. 19038.
[63] A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to asynchronous multivariate time series anomaly detection and localization,”
in Proc. 27th ACM SIGKDD Conf. Knowl. Discov. Data Mining, New
York, NY, USA, 2021, pp. 2485–2494.

6790

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

[64] K. Zhang and Y. Liu, “Unsupervised feature learning with data augmentation for control valve stiction detection,” in Proc. IEEE 10th Data Driven
Control Learn. Syst. Conf., 2021, pp. 1385–1390.
[65] Q. Ma, J. Zheng, S. Li, and G. W. Cottrell, “Learning representations for
time series clustering,” in Proc. Adv. Neural Inf. Process. Syst., 2019.
[66] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,” in
Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 3395–3404.
[67] S. Han and S. S. Woo, “Learning sparse latent graph representations
for anomaly detection in multivariate time series,” in Proc. 28th ACM
SIGKDD Conf. Knowl. Discov. Data Mining, New York, NY, USA, 2022,
pp. 2977–2986.
[68] P. Vincent, H. Larochelle, Y. Bengio, and P.-A. Manzagol, “Extracting and composing robust features with denoising autoencoders,” in
Proc. 25th Int. Conf. Mach. Learn., New York, NY, USA, 2008,
pp. 1096–1103.
[69] G. Jiang, P. Xie, H. He, and J. Yan, “Wind turbine fault detection using a
denoising autoencoder with temporal information,” IEEE/ASME Trans.
Mechatronics, vol. 23, no. 1, pp. 89–100, Feb. 2018.
[70] J. Zhang and P. Yin, “Multivariate time series missing data imputation
using recurrent denoising autoencoder,” in Proc. IEEE Int. Conf. Bioinf.
Biomed., 2019, pp. 760–764.
[71] Z. Zheng, Z. Zhang, L. Wang, and X. Luo, “Denoising temporal convolutional recurrent autoencoders for time series classification,” Inf. Sci.,
vol. 588, pp. 159–173, 2022.
[72] J. Li, Z. Struzik, L. Zhang, and A. Cichocki, “Feature learning from
incomplete EEG with denoising autoencoder,” Neurocomputing, vol. 165,
pp. 23–31, 2015.
[73] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2022, pp. 15979–15988.
[74] Z. Shao, Z. Zhang, F. Wang, and Y. Xu, “Pre-training enhanced spatialtemporal graph neural network for multivariate time series forecasting,”
in Proc. 28th ACM SIGKDD Conf. Knowl. Discov. Data Mining, New
York, NY, USA, 2022, pp. 1567–1577.
[75] G. Zerveas, S. Jayaraman, D. Patel, A. Bhamidipaty, and C. Eickhoff, “A
transformer-based framework for multivariate time series representation
learning,” in Proc. 27th ACM SIGKDD Conf. Knowl. Discov. Data
Mining, 2021, pp. 2114–2124.
[76] J. Chauhan, A. Raghuveer, R. Saket, J. Nandy, and B. Ravindran, “Multivariate time series forecasting on variable subsets,” in Proc. 28th ACM
SIGKDD Conf. Knowl. Discov. Data Mining, New York, NY, USA, 2022,
pp. 76–86.
[77] R. R. Chowdhury, X. Zhang, J. Shang, R. K. Gupta, and D. Hong,
“TARNet: Task-aware reconstruction for time-series transformer,” in
Proc. 28th ACM SIGKDD Conf. Knowl. Discov. Data Mining, New York,
NY, USA, 2022, pp. 212–220.
[78] D. P. Kingma and M. Welling, “Auto-encoding variational bayes,” in
Proc. 2nd Int. Conf. Learn. Representations, Banff, AB, Canada, 2014,
pp. 1–14.
[79] P. DiederikKingma and M. Welling, “An introduction to variational
autoencoders,” 2019, arXiv: 1906.02691.
[80] Z. Li et al., “Multivariate time series anomaly detection and interpretation
using hierarchical inter-metric and temporal embedding,” in Proc. 27th
ACM SIGKDD Conf. Knowl. Discov. Data Mining, 2021, pp. 3220–3230.
[81] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 2828–2837.
[82] W. Zhang, C. Zhang, and F. Tsung, “GRELEN: Multivariate time series
anomaly detection from the perspective of graph relational learning,” in
Proc. 31st Int. Joint Conf. Artif. Intell., 2022, pp. 2390–2397.
[83] W. Chen, L. Tian, B. Chen, L. Dai, Z. Duan, and M. Zhou, “Deep
variational graph convolutional recurrent network for multivariate time
series anomaly detection,” in Proc. 39th Int. Conf. Mach. Learn., 2022,
pp. 3621–3633.
[84] S. N. Shukla and B. M. Marlin, “Multi-time attention networks for irregularly sampled time series,” in Proc. Int. Conf. Learn. Representations,
2021.
[85] S. C.-X. Li and B. Marlin, “Learning from irregularly-sampled time
series: A missing data perspective,” in Proc. 37th Int. Conf. Mach. Learn.,
2020, pp. 5937–5946.
[86] S. N. Shukla and B. M. Marlin, “Heteroscedastic temporal variational
autoencoder for irregularly sampled time series,” in Proc. Int. Conf.
Learn. Representations, 2022, pp. 1–20.

[87] Z. Wang, X. Xu, G. Trajcevski, W. Zhang, T. Zhong, and F. Zhou, “Learning latent seasonal-trend representations for time series forecasting,” in
Proc. Adv. Neural Inf. Process. Syst., 2022, pp. 1–13.
[88] J. Ho, A. Jain, and P. Abbeel, “Denoising diffusion probabilistic models,”
in Proc. Adv. Neural Inf. Process. Syst., 2020, pp. 6840–6851.
[89] P. Dhariwal and A. Nichol, “Diffusion models beat gans on image
synthesis,” in Proc. Adv. Neural Inf. Process. Syst., 2021, pp. 8780–8794.
[90] L. Yang et al., “Diffusion models: A comprehensive survey of methods
and applications,” Comput. Surv., vol. 56, no. 4, pp. 1–39, Nov. 2023.
[91] H. Cao, C. Tan, Z. Gao, G. Chen, P.-A. Heng, and S. Z. Li, “A survey on
generative diffusion model,” 2022, arXiv:2209.02646.
[92] C. Luo, “Understanding diffusion models: A unified perspective,”
2022, arXiv:2208.11970.
[93] J. Sohl-Dickstein, E. Weiss, N. Maheswaranathan, and S. Ganguli, “Deep
unsupervised learning using nonequilibrium thermodynamics,” in Proc.
Int. Conf. Mach. Learn., 2015, pp. 2256–2265.
[94] Y. Song and S. Ermon, “Generative modeling by estimating gradients
of the data distribution,” in Proc. Adv. Neural Inf. Process. Syst., 2019,
pp. 11918–11930.
[95] Y. Song and S. Ermon, “Improved techniques for training score-based
generative models,” in Proc. Adv. Neural Inf. Process. Syst., 2020,
pp. 12438–12448.
[96] Y. Song, C. Durkan, I. Murray, and S. Ermon, “Maximum likelihood
training of score-based diffusion models,” in Proc. Adv. Neural Inf.
Process. Syst., 2021, pp. 1415–1428.
[97] Y. Song, J. Sohl-Dickstein, D. P. Kingma, A. Kumar, S. Ermon, and
B. Poole, “Score-based generative modeling through stochastic differential equations,” in Proc. Int. Conf. Learn. Representations, 2021, pp. 1–36.
[98] Y. Tashiro, J. Song, Y. Song, and S. Ermon, “CSDI: Conditional scorebased diffusion models for probabilistic time series imputation,” in Proc.
Adv. Neural Inf. Process. Syst., 2021, pp. 24804–24816.
[99] K. Rasul, C. Seward, I. Schuster, and R. Vollgraf, “Autoregressive denoising diffusion models for multivariate probabilistic time series forecasting,” in Proc. Int. Conf. Mach. Learn., PMLR, 2021, pp. 8857–8868.
[100] Y. Li, X. Lu, Y. Wang, and D. Dou, “Generative time series forecasting
with diffusion, denoise, and disentanglement,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2022, pp. 1–14.
[101] Y. Chen et al., “ImDiffusion: Imputed diffusion models for multivariate
time series anomaly detection,” Proc. VLDB Endow., vol. 17, no. 3,
pp. 359–372, Nov. 2023.
[102] J. L. Alcaraz and N. Strodthoff, “Diffusion-based time series imputation
and forecasting with structured state space models,” Trans. Mach. Learn.
Res., pp. 1–36, 2022.
[103] Z. Wang, Q. Wen, C. Zhang, L. Sun, and Y. Wang, “Diffload: Uncertainty quantification in load forecasting with diffusion model,”
2023, arXiv:2306.01001.
[104] H. Wen et al., “DiffSTG: Probabilistic spatio-temporal graph forecasting
with denoising diffusion models,” in Proc. 31st ACM Int. Conf. Adv.
Geographic Inf. Syst., pp. 1–12, 2023.
[105] J.-Y. Franceschi, A. Dieuleveut, and M. Jaggi, “Unsupervised scalable
representation learning for multivariate time series,” in Proc. Adv. Neural
Inf. Process. Syst., 2019, pp. 4650–4661.
[106] S. Tonekaboni, D. Eytan, and A. Goldenberg, “Unsupervised representation learning for time series with temporal neighborhood coding,” in
Proc. Int. Conf. Learn. Representations, 2021, pp. 1–17.
[107] P. Khosla et al., “Supervised contrastive learning,” in Proc. Adv. Neural
Inf. Process. Syst., 2020, pp. 18661–18673.
[108] H. Yèche, G. Dresdner, F. Locatello, M. Hüser, and G. Rätsch, “Neighborhood contrastive learning applied to online patient monitoring,” in
Proc. 38th Int. Conf. Mach. Learn., 2021, pp. 11964–11974.
[109] A. van den Oord, Y. Li, and O. Vinyals, “Representation learning with
contrastive predictive coding,” 2018, arXiv: 1807.03748.
[110] T. Schneider et al., “Detecting anomalies within time series using local
neural transformations,” 2022, arXiv:2202.03944.
[111] T. Pranavan, T. Sim, A. Ambikapathi, and S. Ramasamy, “Contrastive
predictive coding for anomaly detection in multi-variate time series data,”
2022, arXiv:2202.03639.
[112] S. Deldari, D. V. Smith, H. Xue, and F. D. Salim, “Time series change
point detection with self-supervised contrastive predictive coding,” in
Proc. Web Conf., New York, NY, USA, 2021, pp. 3124–3135.
[113] K. Zhang, Q. Wen, C. Zhang, L. Sun, and Y. Liu, “Time series anomaly
detection using skip-step contrastive predictive coding,” in Proc. NeurIPS
Workshop: Self-Supervised Learn. - Theory Pract., 2022, pp. 1–9.
[114] S. Bai, J. Z. Kolter, and V. Koltun, “An empirical evaluation of
generic convolutional and recurrent networks for sequence modeling,”
2018, arXiv: 1803.01271.

ZHANG et al.: SSL FOR TIME SERIES ANALYSIS: TAXONOMY, PROGRESS, AND PROSPECTS

[115] M. Hou et al., “Stock trend prediction with multi-granularity data: A
contrastive learning approach with adaptive fusion,” in Proc. 30th ACM
Int. Conf. Inf. Knowl. Manage., 2021, pp. 700–709.
[116] E. Eldele et al., “Time-series representation learning via temporal and
contextual contrasting,” in Proc. 13th Int. Joint Conf. Artif. Intell., 2021,
pp. 2352–2359.
[117] E. Eldele et al., “Self-supervised contrastive representation learning for
semi-supervised time-series classification,” IEEE Trans. Pattern Anal.
Mach. Intell., vol. 45, no. 12, pp. 15604–15618, Dec. 2023.
[118] Z. Yue et al., “TS2Vec: Towards universal representation of time series,”
in Proc. AAAI Conf. Artif. Intell., 2022, pp. 8980–8987.
[119] J. Pöppelbaum, G. S. Chadha, and A. Schwung, “Contrastive learning
based self-supervised time-series analysis,” Appl. Soft Comput., vol. 117,
2022, Art. no. 108397.
[120] T. Peng, C. Shen, S. Sun, and D. Wang, “Fault feature extractor based
on bootstrap your own latent and data augmentation algorithm for unlabeled vibration signals,” IEEE Trans. Ind. Electron., vol. 69, no. 9,
pp. 9547–9555, Sep. 2022.
[121] B. K. Iwana and S. Uchida, “An empirical survey of data augmentation
for time series classification with neural networks,” PLoS One, vol. 16,
no. 7, Jul. 2021, Art. no. e0254841.
[122] K. Wickstrøm, M. Kampffmeyer, K. Øyvind Mikalsen, and R. Jenssen,
“Mixing up contrastive learning: Self-supervised representation learning for time series,” Pattern Recognit. Lett., vol. 155, pp. 54–61,
2022.
[123] G. Woo, C. Liu, D. Sahoo, A. Kumar, and S. Hoi, “CoST: Contrastive learning of disentangled seasonal-trend representations for time
series forecasting,” in Proc. Int. Conf. Learn. Representations, 2022,
pp. 1–18.
[124] L. Yang and S. Hong, “Unsupervised time-series representation learning
with iterative bilinear temporal-spectral fusion,” in Proc. 39th Int. Conf.
Mach. Learn., 2022, pp. 25038–25054.
[125] X. Zhang, Z. Zhao, T. Tsiligkaridis and, and M. Zitnik, “Self-supervised
contrastive pre-training for time series via time-frequency consistency,”
in Proc. Neural Inf. Process. Syst., 2022, pp. 3988–4003.
[126] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “DCdetector: Dual
attention contrastive representation learning for time series anomaly
detection,” in Proc. 29th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, Long Beach, CA, 2023, pp. 3033–3045.
[127] X. Yang, Z. Zhang, and R. Cui, ”TimeCLR: A self-supervised contrastive
learning framework for univariate time series representation,” Knowl.Based Syst., vol. 245, 2022, Art. no. 108606.
[128] D. Kiyasseh, T. Zhu, and D. A. Clifton, “CLOCS: Contrastive learning of
cardiac signals across space, time, and patients,” in Proc. 38th Int. Conf.
Mach. Learn.2021, pp. 5606–5615.
[129] Y. Ozyurt, S. Feuerriegel, and C. Zhang, “Contrastive learning for unsupervised domain adaptation of time series,” in Proc. Int. Conf. Learn.
Representations, 2023, pp. 1–40.
[130] K. Zhang, Y. Liu, Y. Gu, J. Wang, and X. Ruan, “Valve stiction detection using multitimescale feature consistent constraint for time-series
data,” IEEE/ASME Trans. Mechatronics, vol. 28, no. 3, pp. 1488–1499,
Jun. 2023.
[131] M. Hou et al., “Multi-granularity residual learning with confidence
estimation for time series prediction,” in Proc. ACM Web Conf., 2022,
pp. 112–121.
[132] H. Lee, E. Seong, and D.-K. Chae, “Self-supervised learning with
attention-based latent signal augmentation for sleep staging with limited labeled data,” in Proc. 31st Int. Joint Conf. Artif. Intell., 2022,
pp. 3868–3876.
[133] T. Wang and P. Isola, “Understanding contrastive representation learning
through alignment and uniformity on the hypersphere,” in Proc. 37th Int.
Conf. Mach. Learn., 2020, pp. 9929–9939.
[134] Y. Li, P. Hu, Z. Liu, D. Peng, J. T. Zhou, and X. Peng, “Contrastive
clustering,” in Proc. AAAI Conf. Artif. Intell., 2021, pp. 8547–8555.
[135] J. Li, P. Zhou, C. Xiong, and S. Hoi, “Prototypical contrastive learning of
unsupervised representations,” in Proc. Int. Conf. Learn. Representations,
2021, pp. 1–16.
[136] G. Li et al., “ShapeNet: A shapelet-neural network approach for multivariate time series classification,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 8375–8383.
[137] X. Zhang, Y. Gao, J. Lin, and C.-T. Lu, “TapNet: Multivariate time series
classification with attentional prototypical network,” in Proc. AAAI Conf.
Artif. Intell., 2020, pp. 6845–6852.
[138] A. Dorle, F. Li, W. Song, and S. Li, “Learning discriminative virtual sequences for time series classification,” in Proc. 29th ACM
Int. Conf. Inf. Knowl. Manage., New York, NY, USA, 2020,
pp. 2001–2004.

6791

[139] Q. Meng, H. Qian, Y. Liu, L. Cui, Y. Xu, and Z. Shen, “MHCCL:
Masked hierarchical cluster-wise contrastive learning for multivariate
time series,” in Proc. AAAI Conf. Artif. Intell., 2023, pp. 9153–9161.
[140] X. Wu, L. Xiao, Y. Sun, J. Zhang, T. Ma, and L. He, “A survey of humanin-the-loop for machine learning,” Future Gener. Comput. Syst., vol. 135,
pp. 364–381, 2022.
[141] Y. Chen and D. Zhang, “Integration of knowledge and data in machine
learning,” 2022, arXiv:2202.10337v2.
[142] P. Shi, W. Ye, and Z. Qin, “Self-supervised pre-training for time series
classification,” in Proc. Int. Joint Conf. Neural Netw., 2021, pp. 1–8.
[143] M. T. Nonnenmacher, L. Oldenburg, I. Steinwart, and D. Reeb, “Utilizing
expert features for contrastive learning of time-series representations,” in
Proc. 39th Int. Conf. Mach. Learn., 2022, pp. 16969–16989.
[144] H. Zhang, J. Wang, Q. Xiao, J. Deng, and Y. Lin, “SleepPriorCL: Contrastive representation learning with prior knowledge-based positive mining and adaptive temperature for sleep staging,” 2021, arXiv:2110.09966.
[145] T.-S. Chen, W.-C. Hung, H.-Y. Tseng, S.-Y. Chien, and M.-H. Yang,
“Incremental false negative detection for contrastive learning,” in Proc.
Int. Conf. Learn. Representations, 2022, pp. 1–18.
[146] K. Zhang, R. Cai, and Y. Liu, “Industrial fault detection using contrastive
representation learning on time-series data,” IFAC-PapersOnLine,
vol. 56, no. 2, pp. 3197–3202, 2023.
[147] Y. Zhang, X. Zhang, J. Li, R. C. Qiu, H. Xu, and Q. Tian, “Semisupervised contrastive learning with similarity co-calibration,” IEEE
Trans. Multimedia, vol. 25, pp. 1749–1759, 2023.
[148] I. Goodfellow et al., “Generative adversarial nets,” in Proc. Adv. Neural
Inf. Process. Syst., 2014, pp. 2672–2680.
[149] Z. Wang, Q. She, and T. E. Ward, “Generative adversarial networks in
computer vision: A survey and taxonomy,” ACM Comput. Surv., vol. 54,
no. 2, Feb. 2021, Art. no. 37.
[150] P. Isola, J.-Y. Zhu, T. Zhou, and A. A. Efros, “Image-to-image translation
with conditional adversarial networks,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit., 2017, pp. 5967–5976.
[151] J.-Y. Zhu, T. Park, P. Isola, and A. A. Efros, “Unpaired image-to-image
translation using cycle-consistent adversarial networks,” in Proc. IEEE
Int. Conf. Comput. Vis., 2017, pp. 2242–2251.
[152] A. Brock, J. Donahue, and K. Simonyan, “Large scale GAN training
for high fidelity natural image synthesis,” in Proc. Int. Conf. Learn.
Representations, 2019, pp. 1–35.
[153] T. Karras, S. Laine, and T. Aila, “A style-based generator architecture
for generative adversarial networks,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit., 2019, pp. 4396–4405.
[154] O. Mogren, “C-RNN-GAN: Continuous recurrent neural networks with
adversarial training,” 2016, arXiv:1611.09904.
[155] J. Yoon, D. Jarrett, and M. van der Schaar, “Time-Series Generative
Adversarial Networks,” in Proc. Int. Conf. Neural Inf. Process. Syst.,
Red Hook, NY, USA, 2019, pp. 5509–5519.
[156] X. Li, V. Metsis, H. Wang, and A. H. H. Ngu, “TTS-GAN: A transformerbased time-series generative adversarial network,” in Proc. Artif. Intell.
Med.: 20th Int. Conf. Artif. Intell. Med., Halifax, NS, Canada, Heidelberg,
2022, pp. 133–143.
[157] Y. Luo, Y. Zhang, X. Cai, and X. Yuan, “E 2 gan: End-to-end generative
adversarial network for multivariate time series imputation,” in Proc. 28th
Int. Joint Conf. Artif. Intell., 2019, pp. 3094–3100.
[158] A. Seyfi, J.-F. Rajotte, and R. T. Ng, “Generating multivariate time series
with Common source coordinated GAN (COSCI-GAN),” in Proc. Adv.
Neural Inf. Process. Syst., 2022.
[159] P. Jeha et al., “PSA-: Progressive self attention GANs for synthetic time
series,” in Proc. Int. Conf. Learn. Representations, 2022, pp. 1–20.
[160] J. Jeon, J. Kim, H. Song, S. Cho, and N. Park, “GT-GAN: General purpose
time series synthesis with generative adversarial networks,” in Proc. Adv.
Neural Inf. Process. Syst., 2022, pp. 1–12.
[161] Y. Luo, X. Cai, Y. Zhang, J. Xu, and Y. Xiaojie, “Multivariate time series
imputation with generative adversarial networks,” in Proc. Adv. Neural
Inf. Process. Syst., 2018, pp. 1603–1614.
[162] X. Miao, Y. Wu, J. Wang, Y. Gao, X. Mao, and J. Yin, “Generative semisupervised learning for multivariate time series imputation,” in Proc.
AAAI Conf. Artif. Intell., 2021, pp. 8983–8991.
[163] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int. Conf.
Learn. Representations, 2022, pp. 1–20.
[164] D. Zhu et al., “Deep unsupervised binary coding networks for multivariate time series retrieval,” in Proc. AAAI Conf. Artif. Intell., 2020,
pp. 1403–1411.
[165] Q. Ma, C. Chen, S. Li, and G. W. Cottrell, “Learning representations
for incomplete time series clustering,” in Proc. AAAI Conf. Artif. Intell.,
2021, pp. 8837–8846.

6792

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

[166] S. Wu, X. Xiao, Q. Ding, P. Zhao, Y. Wei, and J. Huang, “Adversarial sparse transformer for time series forecasting,” in Proc. 34th
Int. Conf. Neural Inf. Process. Syst., Red Hook, NY, USA, 2020,
pp. 17105–17115.
[167] Y. Li, H. Wang, J. Li, C. Liu, and J. Tan, “ACT: Adversarial convolutional
transformer for time series forecasting,” in Proc. Int. Joint Conf. Neural
Netw., 2022, pp. 1–8.
[168] B. Zhou, S. Liu, B. Hooi, X. Cheng, and J. Ye, “BeatGAN: Anomalous
rhythm detection using adversarially generated time series,” in Proc. 28th
Int. Joint Conf. Artif. Intell., 2019, pp. 4433–4439.
[169] K. Aggarwal, S. Joty, L. Fernandez-Luque, and J. Srivastava, “Adversarial unsupervised representation learning for activity time-series,” in Proc.
AAAI Conf. Artif. Intell., 2019, pp. 834–841.
[170] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding,” in Proc. 24th ACM SIGKDD Int.
Conf. Knowl. Discov. Data Mining, New York, NY, USA, 2018,
pp. 387–395.
[171] J. Goh, S. Adepu, K. N. Junejo, and A. Mathur, “A dataset to support
research in the design of secure water treatment systems,” in Proc. Crit.
Inf. Infrastructures Secur.: 11th Int. Conf., Paris, France, 10–12, 2016,
Springer, 2017, pp. 88–99.
[172] C. M. Ahmed, V. R. Palleti, and A. P. Mathur, “Wadi: A water distribution
testbed for research in the design of secure cyber physical systems,” in
Proc. 3rd Int. Workshop Cyber- Phys. Syst. Smart Water Netw., New York,
NY, USA, 2017, pp. 25–28.
[173] H. Zhou et al., “Informer: Beyond efficient transformer for long sequence time-series forecasting,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 11106–11115.
[174] European Commission’s STETIS program, “30 years of european
wind generation,” 2017. [Online]. Available: https://www.kaggle.com/
datasets/sohier/30-years-of-european-wind-generation
[175] UCI Machine Learning Repository, “Electricityloaddiagrams20112014
data set,” 2011. [Online]. Available: https://archive.ics.uci.edu/ml/
datasets/ElectricityLoadDiagrams20112014
[176] Centers for Disease Control and Prevention, 2020. “National, regional,
and state level outpatient illness and viral surveillance,” [Online]. Available: https://gis.cdc.gov/grasp/fluview/fluportaldashboard.html
[177] Max-Planck-Institut fur Biogeochemie, Jena, “Weather data set,” 2019.
[Online]. Available: https://www.bgc-jena.mpg.de/wetter/
[178] California Department of Transportation, “Traffic data set,” 2018. [Online]. Available: http://pems.dot.ca.gov/
[179] G. Lai, W.-C. Chang, Y. Yang, and H. Liu, “Modeling long- and shortterm temporal patterns with deep neural networks,” in Proc. 41st Int.
ACM SIGIR Conf. Res. Develop. Inf. Retrieval, New York, NY, USA,
2018, pp. 95–104.
[180] National Renewable Energy Laboratory, “Solar power data for integration studies,” [Online]. Available: 2006https://www.nrel.gov/grid/solarpower-data.html
[181] D. Anguita, A. Ghio, L. Oneto, X. Parra, and J. L. Reyes-Ortiz, “A public
domain dataset for human activity recognition using smartphones,” in
Proc. Eur. Symp. Artif. Neural Netw., 2013, pp. 1–14.
[182] H. A. Dau et al., “The UCR time series archive,” IEEE/CAA J. Automatica
Sinica, vol. 6, no. 6, pp. 1293–1305, Nov. 2019.
[183] A. Bagnall et al., “The UEA multivariate time series classification archive,
2018,” 2018, arXiv: 1811.00075.
[184] X. Chen, L. Deng, Y. Zhao, and K. Zheng, “Adversarial autoencoder for
unsupervised time series anomaly detection and interpretation,” in Proc.
16th ACM Int. Conf. Web Search Data Mining, New York, NY, USA,
2023, pp. 267–275.
[185] S. Liu et al., “Pyraformer: Low-complexity pyramidal attention for longrange time series modeling and forecasting,” in Proc. Int. Conf. Learn.
Representations, 2022, pp. 1–20.
[186] W. Chen, W. Wang, B. Peng, Q. Wen, T. Zhou, and L. Sun, “Learning
to rotate: Quaternion transformer for complicated periodical time series
forecasting,” in Proc. 28th ACM SIGKDD Conf. Knowl. Discov. Data
Mining, New York, NY, USA, 2022, pp. 146–156.
[187] R.-G. Cirstea, C. Guo, B. Yang, T. Kieu, X. Dong, and S. Pan, “Triformer:
Triangular, variable-specific attentions for long sequence multivariate
time series forecasting,” in Proc. 31st Int. Joint Conf. Artif. Intell., 2022,
pp. 1994–2001.
[188] M. A. Shabani, A. H. Abdi, L. Meng, and T. Sylvain, “Scaleformer:
Iterative multi-scale refining transformers for time series forecasting,” in
Proc. Int. Conf. Learn. Representations, 2023, pp. 1–23.
[189] Y. Zhang and J. Yan, “Crossformer: Transformer utilizing crossdimension dependency for multivariate time series forecasting,” in Proc.
Int. Conf. Learn. Representations, 2023, pp. 1–21.

[190] H. Wu, T. Hu, Y. Liu, H. Zhou, J. Wang, and M. Long, “Timesnet:
Temporal 2d-variation modeling for general time series analysis,” in Proc.
Int. Conf. Learn. Representations, 2023, pp. 1–23.
[191] H. Wang, J. Peng, F. Huang, J. Wang, J. Chen, and Y. Xiao,
“MICN: Multi-scale local and global context modeling for long-term
series forecasting,” in Proc. Int. Conf. Learn. Representations, 2023,
pp. 1–22.
[192] X. Tang, H. Yao, Y. Sun, C. Aggarwal, P. Mitra, and S. Wang, “Joint
modeling of local and global temporal dynamics for multivariate time
series forecasting with missing values,” in Proc. AAAI Conf. Artif. Intell.,
2020, pp. 5956–5963.
[193] X. Wang, K. Wang, and S. Lian, “A survey on face data augmentation
for the training of deep neural networks,” Neural Comput. Appl., vol. 32,
no. 19, pp. 15503–15531, Oct. 2020.
[194] J. Gao, X. Song, Q. Wen, P. Wang, L. Sun, and H. Xu, “RobustTAD:
Robust time series anomaly detection via decomposition and convolutional neural networks,” in Proc. KDD Workshop Mining Learn. Time
Ser., 2020, pp. 1–6.
[195] T. T. Um et al., “Data augmentation of wearable sensor data for parkinson’s disease monitoring using convolutional neural networks,” in Proc.
19th ACM Int. Conf. Multimodal Interaction, New York, NY, USA, 2017,
pp. 216–220.
[196] C. Deng, X. Ji, C. Rainey, J. Zhang, and W. Lu, “Integrating machine learning with human knowledge,” iScience, vol. 23, no. 11, 2020,
Art. no. 101656.
[197] Y. Chen and D. Zhang, “Integration of knowledge and data in machine
learning,” 2022, arXiv:2202.10337.
[198] Q. Wen, J. Gao, X. Song, L. Sun, H. Xu, and S. Zhu, “RobustSTL: A
robust seasonal-trend decomposition algorithm for long time series,” in
Proc. AAAI Conf. Artif. Intell., 2019, pp. 5409–5416.
[199] Q. Wen, K. He, L. Sun, Y. Zhang, M. Ke, and H. Xu, “RobustPeriod:
Robust time-frequency mining for multiple periodicity detection,” in
Proc. Int. Conf. Manage. Data, 2021, pp. 2328–2337.
[200] T. Zhou, Z. Ma, Q. Wen, X. Wang, L. Sun, and R. Jin, “FEDformer:
Frequency enhanced decomposed transformer for long-term series forecasting,” in Proc. 39th Int. Conf. Mach. Learn., 2022, pp. 27268–27286.
[201] S. N. Shukla and B. M. Marlin, “A survey on principles, models and methods for learning from irregularly sampled time series: From discretization
to attention and invariance,” 2020, arXiv: 2012.00168.
[202] Y. Wu et al., “Dynamic gaussian mixture based deep generative model
for robust forecasting on sparse multivariate time series,” in Proc. AAAI
Conf. Artif. Intell., 2021, pp. 651–659.
[203] A. Kirillov et al., “Segment anything,” 2023, arXiv:2304.02643.
[204] C. Szegedy et al., “Intriguing properties of neural networks,” in Proc. Int.
Conf. Learn. Representations, 2014, pp. 1–10.
[205] L. Liu, Y. Park, T. N. Hoang, H. Hasson, and L. Huan, “Robust multivariate time-series forecasting: Adversarial attacks and defense mechanisms,” in Proc. Int. Conf. Learn. Representations, 2023, pp. 1–18.
[206] T. Wu, X. Wang, S. Qiao, X. Xian, Y. Liu, and L. Zhang, “Small
perturbations are enough: Adversarial attacks on time series prediction,”
Inf. Sci., vol. 587, pp. 794–812, 2022.
[207] F. Karim, S. Majumdar, and H. Darabi, “Adversarial attacks on time
series,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 43, no. 10, pp. 3309–
3320, Oct. 2021.
[208] Y. Zhuo, Z. Yin, and Z. Ge, “Attack and defense: Adversarial security
of data-driven FDC systems,” IEEE Trans. Ind. Informat., vol. 19, no. 1,
pp. 5–19, Jan. 2023.
[209] J. Goodfellow, J. Shlens, and C. Szegedy, “Explaining and harnessing
adversarial examples,” in Proc. Int. Conf. Learn. Representations, 2015,
pp. 1–11.
[210] K. Lee, J. Kim, S. Chong, and J. Shin, “Making stochastic neural networks
from deterministic ones,” in Proc. Int. Conf. Learn. Representations,
2017, pp. 1–16.
[211] N. Carlini and D. Wagner, “Towards evaluating the robustness of neural
networks,” in Proc. IEEE Symp. Secur. Privacy, 2017, pp. 39–57.
[212] S.-M. Moosavi-Dezfooli, A. Fawzi, and P. Frossard, “DeepFool: A simple
and accurate method to fool deep neural networks,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit., 2016, pp. 2574–2582.
[213] S.-M. Moosavi-Dezfooli, A. Fawzi, O. Fawzi, and P. Frossard, “Universal
adversarial perturbations,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., 2017, pp. 86–94.
[214] J. Uesato, B. O’Donoghue, P. Kohli, and A. van den Oord, “Adversarial
risk and the dangers of evaluating against weak attacks,” in Proc. 35th
Int. Conf. Mach. Learn., 2018, pp. 5025–5034.
[215] J. Li, L. Lyu, D. Iso, C. Chakrabarti, and M. Spranger, “Moco SFL:
Enabling cross-client collaborative self-supervised learning,” in Proc.
Int. Conf. Learn. Representations, 2023.

ZHANG et al.: SSL FOR TIME SERIES ANALYSIS: TAXONOMY, PROGRESS, AND PROSPECTS

[216] Z. Zhang, Z. Zhao, and Z. Lin, “Unsupervised representation learning
from pre-trained diffusion probabilistic models,” in Proc. Adv. Neural
Inf. Process. Syst., 2022, pp. 1–14.
[217] S. Sørbø and M. Ruocco, “Navigating the metric maze: A taxonomy of
evaluation metrics for anomaly detection in time series,” Data Mining
Knowl. Discov., vol. 38, pp. 1–42, 2023.

Kexin Zhang (Graduate Student Member, IEEE) received the BS and the MS degrees in engineering from
the China University of Geosciences, Wuhan, China,
in 2016 and 2019, respectively, and the PhD degree in
control engineering and science from Zhejiang University, Hangzhou, China, in 2023. His major research
interests include intelligent time series analysis, deep
learning, data-driven industrial fault diagnosis, and
artificial intelligence security.

Qingsong Wen (Senior Member, IEEE) received the
MS and PhD degrees in electrical and computer engineering from the Georgia Institute of Technology,
Atlanta, USA. He is the head of AI Research &
Chief Scientist, Squirrel Ai Learning. Previously, he
worked with Alibaba, Qualcomm, and Marvell. He
has published more than 100 top-ranked AI conference and journal papers, had multiple Oral/Spotlight
Papers at NeurIPS/ICLR, had multiple Most Influential Papers at IJCAI, received multiple IAAI Deployed
Application Awards at AAAI, and won First Place
of SP Grand Challenge at ICASSP. Currently, he serves as Organizer/co-chair
of Workshop on AI for Time Series (AI4TS @ KDD, ICDM, SDM, AAAI,
IJCAI) and Workshop on AI for Education (AI4EDU @ KDD, CAI). He also
serves as associate editor for Neurocomputing, associate editor for IEEE Signal
Processing Letters, guest editor for Applied Energy, and guest editor for IEEE
Internet of Things Journal. His research interests include AI for time series, AI
for education, and general machine learning.

Chaoli Zhang received the BS degree in information
security from Nankai University, China, in 2015, and
the PhD degree in computer science and engineering
from Shanghai Jiao Tong University, China, in 2020.
She is currently a lecturer with the School of Computer Science and Technology, Zhejiang Normal University. She engaged in research at Alibaba DAMO
Academy for nearly three years. Her research interests
include time series analysis, algorithmic game theory
and mechanism design, networking. She won the
gold prize of ICASSP-SPGC root cause analysis for
wireless network fault localization 2022. She was the recipient of Google Anita
Borg Scholarship 2014 and AAAI/IAAI innovative deployed application award
2023.

Rongyao Cai (Graduate Student Member, IEEE) received the BS degress in chemical engineering from
the Zhejiang University of Technology, Hangzhou,
China, in 2022. He is working toward the MS degree in control engineering with the College of Control Science and Engineering, Zhejiang University,
Hangzhou, China. His major research interests include data mining, machine learning on industrial
time-series data.

6793

Ming Jin received the BEng degree from the Hebei
University of Technology, Tianjin, China, in 2017,
and the MInfTech degree from the University of
Melbourne, Melbourne, Australia, in 2019. He is
currently working toward the PhD degree in computer science with Monash University, Melbourne,
Australia. His research focuses on graph neural networks (GNNs), time series analysis, data mining, and
machine learning.

Yong Liu (Member, IEEE) received the BS degree
in computer science and engineering and the PhD
degree in computer science from Zhejiang University,
Hangzhou, China, in 2001 and 2007, respectively. He
is currently a professor with the Institute of Cyber
Systems and Control, Department of Control Science and Engineering, Zhejiang University. He has
authored or co-authored more than 30 research papers
in machine learning, computer vision, information
fusion, and robotics. His current research interests include machine learning, robotics vision, information
processing, and granular computing.
James Y. Zhang received the bachelor’s and master’s degrees from Zhejiang University, China, in
1997 and 2000, respectively, and the PhD degree in
electrical engineering from the University of Ottawa,
Canada, in 2006. He is the managing director of AI
Forecast and Strategy Platform of Ant Group. Prior
to his employment with Ant Group, he worked on
finance-related AI with Bloomberg, spearheaded the
creation of Bloomberg’s GPU computation farm and
participated in the establishment of the AI branch of
Bloomberg Labs. His industrial experience of startups
and larger corporations spans various disciplines, such as image processing,
natural language processing, time series analysis, high-speed hardware development, optical networks, operations research, biometrics, and financial systems,
with extensive patents and publications.
Yuxuan Liang (Member, IEEE) received the PhD
degree from the National University of Singapore.
He is currently an assistant professor with Intelligent
Transportation Thrust, also affiliated with Data Science and Analytics Thrust, Hong Kong University of
Science and Technology (Guangzhou). He is working on the research, development, and innovation of
spatio-temporal data mining and AI, with a broad
range of applications in smart cities. He published
more than 50 peer-reviewed papers in refereed journals and conferences, such as IEEE Transactions on
Pattern Analysis and Machine Intelligence, IEEE Transactions on Knowledge
and Data Engineering, AI Journal, IEEE Transactions on Mobile Computing,
KDD, WWW, NeurIPS, and ICLR. Three of them were selected as the most
influential IJCAI/KDD papers. He received The 23rd China Patent Excellence
Award, in 2022.
Guansong Pang (Member, IEEE) received the PhD
degree from the University of Technology Sydney,
Australia, in 2019. He is a tenure-track assistant professor of computer science with the School of Computing and Information Systems, Singapore Management University (SMU), Singapore. Before joining
SMU, he was a research fellow with the Australian
Institute for Machine Learning (AIML). His research
interests lie in machine learning techniques and their
applications, with a focus on handling abnormal and
unknown data.

6794

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 46, NO. 10, OCTOBER 2024

Dongjin Song (Member, IEEE) received the PhD
degree from the University of California San Diego
(UCSD), in 2016. Currently, he is an assistant professor with the School of Computing, University of
Connecticut (UConn). His research interests include
machine learning, deep learning, data mining, and
related applications for time series data and graph representation learning. Papers describing his research
have been published at top-tier data science and artificial intelligence conferences, such as NeurIPS,
ICML, ICLR, KDD, ICDM, SDM, AAAI, IJCAI,
CVPR, ICCV, etc. He has co-organized AI for Time Series (AI4TS) workshop at
IJCAI 2022, 2023 and the Mining and Learning from Time Series workshop at
KDD 2022, 2023. He has also served as senior PC for AAAI, IJCAI, and CIKM.
He won the UConn Research Excellence Research (REP) Award in 2021. His
research has been funded by NSF, USDA, Morgan Stanley, NEC Labs America,
Travelers, etc.

Shirui Pan (Senior Member, IEEE) received the PhD
degree in computer science from the University of
Technology Sydney (UTS), Ultimo, NSW, Australia.
He is a professor with the School of Information
and Communication Technology, Griffith University,
Australia. Prior to this, he was a senior lecturer with
the Faculty of IT, Monash University. His research
interests include data mining and machine learning.
To date, he has published more than 100 research
papers in top-tier journals and conferences, including
IEEE Transactions on Pattern Analysis and Machine
Intelligence, IEEE Transactions on Knowledge and Data Engineering, IEEE
Transactions on Neural Networks and Learning Systems, ICML, NeurIPS,
and KDD. His research has attracted more than 20 000 citations. His research
received the 2024 CIS IEEE TNNLS Oustanding Paper Award and the 2020
IEEE ICDM Best Student Paper Award. He is recognized as one of the AI 2000
AAAI/IJCAI Most Influential Scholars in Australia (2021). He is an ARC Future
fellow and a fellow of Queensland Academy of Arts and Sciences (FQA).
PAPER_TEXT
