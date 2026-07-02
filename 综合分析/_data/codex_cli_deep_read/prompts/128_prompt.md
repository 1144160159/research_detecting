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
# [128] Darknet traffic detection and characterization with models based on decision trees and neural networks
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
编号：128
题名：Darknet traffic detection and characterization with models based on decision trees and neural networks
年份：2023
DOI：10.1016/j.iswa.2023.200199
来源：Intelligent Systems with Applications
PDF：paper/10.1016_j.iswa.2023.200199.pdf
已有粗分类：恶意流量、暗网与攻击检测
二级关联：无
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\128.txt
- 原始字符数：52225
- 本次发送字符数：52225
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Intelligent Systems with Applications 18 (2023) 200199

Contents lists available at ScienceDirect

Intelligent Systems with Applications
journal homepage: www.journals.elsevier.com/intelligent-systems-with-applications

Darknet traﬃc detection and characterization with models based on
decision trees and neural networks ✩
Mateus Coutinho Marim a , Paulo Vitor Barbosa Ramos a , Alex B. Vieira a , Antonino Galletta b ,
Massimo Villari b , Roberto M. de Oliveira a , Edelberto Franco Silva a,∗
a
b

Graduate Program in Computer Science (PPGCC), Department of Computer Science, Federal University of Juiz de Fora (UFJF), Juiz de Fora, MG, Brazil
Universita degli Studi di Messina, MIFT Department, Viale F. Stagno D’Alcontres 31, 98166, Messina, Italy

A R T I C L E

I N F O

A B S T R A C T

Keywords:
Traﬃc classiﬁcation
Darknet
Security
Deep web
Neural networks
Benchmark

The Darknet is a set of networks and technologies, having as fundamental principles anonymity and security. In
many cases, they are associated with illicit activities, opening space for malware traﬃc and attacks to legitimate
services. To prevent Darknet misuse is necessary to classify and characterize its existing traﬃc. In this paper, we
characterize and classify the real Darknet traﬃc available from the CIC-Darknet2020 dataset. In that sense,
we performed the feature extraction and grouped the possible subnets with an n-gram approach. Furthermore,
we evaluated the relevance of the best features selected by the Recursive Feature Elimination method for the
problem. Our results indicate that simple models, like Decision Trees and Random Forests, reach an accuracy
above 99% on traﬃc classiﬁcation. Our methodology represents a gain of up to 13% in comparison with the
state-of-the-art.

1. Introduction

digital content. In a general way, the objective of the Darknet is to carry
out secure communication between peers, preserving the conﬁdentiality and completeness of their interactions and keeping the anonymous
sharing nature. With this, the Darknet becomes a secure repository for
any individual to establish activities regardless of their nature, ensuring
the advantage of diﬃcult traceability.
As these properties from the Darknet are highly used for malicious
purposes, the malicious traﬃc from the Darknet is potentially dangerous for computer networks. So, the classiﬁcation of the traﬃc origin
and categorization of the type of application in these cryptographic
situations is one way to prevent damage from Darknet traﬃc, and it
is one of the objectives of the study of the Traﬃc Classiﬁcation problem. The objective of determining certain classes analyzing the data
traﬃc, i.e., checking connection duration patterns, information about
the origin and destination of this data, connected ports, and the type
of application related to the analyzed ﬂow is useful for many security
applications. For instance, in intrusion detection, Quality of Service management in scalability, preventing the spread of malware or (Parchekani
et al.) service attacks. The methods available in the literature vary and

Internet presents a diversiﬁed niche segregated by the level of availability and anonymity of the services. One of the Internet layers is the
Surface Web, this reduced part is the one widely available by search
indexers and commonly used by users looking for so-called common
services and applications. The Deep Web, a set generally “encrypted”
and sought after by those looking for peculiar services, makes available
the results not indexed by conventional search engines. This set has
its principles based on the continuous change of hosting and establishing connections through secure peers, Peer-to-Peer (P2P). the Darknet
is a subset of the Deep Web that expands these principles and further
restricts peer connection (Mirea et al., 2019).
Darknet demonstrates the highest level of security techniques to
ensure the anonymity of groups and service providers, preserving the
identity of the subjects involved in the relationships. Examples include
selling products on the black market, negotiating services, and exchanging information. Although these are some of the activities that are on
the side of illegality, Darknet demonstrates a heterogeneous network
established on principles founded on privacy in the midst of sharing

✩
This work has been partially supported by the Department for drug policies of the Presidency of the Council of Ministers (Italian Government) through the
project InstradaME (CUP F49I20000100001) and the National Operational Programme Metropolitan Cities 2014-2020(PON METRO) through the project MeSm@rt
(CUP F41I18000230006).
* Corresponding author.
E-mail addresses: angalletta@unime.it (A. Galletta), mvillari@unime.it (M. Villari), edelberto@ice.ufjf.br (R.M. de Oliveira).

https://doi.org/10.1016/j.iswa.2023.200199
Received 13 September 2022; Received in revised form 26 December 2022; Accepted 9 February 2023
Available online 17 February 2023
2667-3053/© 2023 The Author(s). Published by Elsevier Ltd. This is an open access article under the CC BY-NC-ND license (http://creativecommons.org/licenses/bync-nd/4.0/).

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

may be linked to the analysis of ports and payload or inserting statistical
inferences to classify the record under analysis (Medeiros et al., 2019).
It is possible to ﬁnd few eﬀorts to detect and characterize Darknet
traﬃc using Deep Learning (DL), such as Deep Image Learning (Gurdip
Kaur & Habibi Lashkari, 2020), there are notable eﬀorts to identify trafﬁc from the same set using traditional machine learning techniques.
This demonstrates that state-of-the-art is being developed for complex
systems, but there is still the need for studies evaluating the eﬃciency
of simpler models.
In this regard, the present work approaches the traﬃc classiﬁcation problem of Darknet using a representative database – the CICDarknet2020 (Gurdip Kaur & Habibi Lashkari, 2020). The main contributions and results of our work can be summarized as follows:

et al., 2020) and (Montieri et al., 2020), can be cited, focusing on the
correlation between privacy-preserving and traﬃc classiﬁcation.
Recently, in work published by Gurdip Kaur and Habibi Lashkari
(2020), a database was made available that is the union of the other two
mentioned above, called CIC-Darknet2020. This work performs the classiﬁcation of applications from Surface Web and Darknet, respectively,
which is deﬁned as the benign origin and Darknet. In this case, the Darknet traﬃc was encrypted using VPN and Tor. In addition to publishing
the database, the author presented an accuracy of 92% for identifying
the origin of the traﬃc and 86% for its categorization in their classiﬁcation model using deep neural networks, using a technique called
Deep Image Learning. Something important to note is that although the
database provides information about the traﬃc source and destination
Internet Protocol (IP)s, it is not possible to detect its real origin. It occurs since the traﬃc that passes through Tor makes its way through
intermediary networks in order to hide the user’s real location. As for
the traﬃc coming from VPNs, the detection of the origin is not possible
because they are fake IPs or bogons.
In Draper-Gil et al. (2016), the authors address the classiﬁcation of
the traﬃc via VPN on the dataset ISCXVPN2016 in two stages with the
usage of neural networks. The ﬁrst, using MLP as the activation function for the second stage, a Recurrent Neural Network to identify the six
classes employed by the dataset. Establishing two application categorization scenarios, the authors use the K-Nearest Neighbors (KNN) and
C4.5 DT models for the task. They present an accuracy above 80%, emphasizing the C4.5, which had better precision measurement results.
In Lotfollahi et al. (2020), using the same dataset, the author
presents the Deep Packet framework approach for the traﬃc classiﬁcation
problem. The framework comprises two deep learning methods, a convolutional neural network, and an autoencoder, both for the classiﬁcation
and characterization tasks. With accuracy and precision results above
90%, the work played an important role in supporting other methods
besides the one used to solve the problem. In Crotti et al. (2007) authors propose alternative approaches for the classiﬁcation problem by
using ports, not recommended as it has low classiﬁcation rates, payload inspection, and the use of a statistical approach. It demonstrates
an accuracy of around 91% for the classiﬁcation of Hypertext Transfer
Protocol (HTTP), Post Oﬃce Protocol (POP3), and Simple Mail Transfer Protocol (SMTP) protocols and 87% for File Transfer Protocol (FTP),
Internet Message Access Protocol (IMAP), Secure Shell (SSH), and TELNET Protocol (TELNET).
The works of (Lotfollahi et al., 2020) and (Draper-Gil et al., 2016),
although they have contributed to the categorization of the application by traﬃc, are not focused on data from Darknet. Gurdip Kaur and
Habibi Lashkari (2020) addresses categorization with deep learning in
two layers, the ﬁrst related to origin classiﬁcation and the second in
relation to traﬃc coming from Darknet, checking the attributes of the
dataset most important for ranking. Even with an accuracy of 86% for
the problem, the authors do not compare it with simpler classiﬁcation
models.
Diﬀerent from the aforementioned works, our proposal uses simple
and easy-to-apply models, such as DT, RF, and MLP, in order to compare
the results of the traﬃc origin classiﬁcation models with the categorization of the application of data from Darknet. Furthermore, we verify
the inﬂuence of the creation of new attributes by comparing the models to verify whether there is a signiﬁcant diﬀerence in performance.
Through this comparison, the models used, although simple, allowed
results close to 100% of overall accuracy, unlike the Deep Learning
models found in state-of-the-art. Thus, the database provided by Gurdip Kaur and Habibi Lashkari (2020) is chosen to achieve the proposed
objectives, expanding it with new features, inserting information on the
source and destination IP addresses, dividing them into n-grams (Wress-

• Higher-performing machine learning models to the traﬃc classiﬁcation area in Darknet, with an improvement of up to 13% concerning the state-of-the-art. Furthermore, we have shown that complex
models are not always necessary for the addressed tasks;
• Is shown the importance of careful analysis and preprocessing of
the attributes to identify how data quality can be improved and,
consequently, the performance of the models created with them;
• From the analysis of the existing ﬁelds, new features are created
aiming for the best performance of the traﬃc origin detection and
the characterization of the application;
• We analyze the results of the models created with the Decision
Tree (DT), Random Forest (RF), and Multilayer Perceptron (MLP)
to verify their applicability in the proposed problems and to compare them through the McNemar statistical test to determine the
existence of a statistically signiﬁcant diﬀerence between them;
• Finally, we also perform a feature selection process with the algorithm Recursive Feature Elimination to analyze the features’ relevance in their respective tasks. The validation resulted in an accuracy of 99.89% for the traﬃc source classiﬁcation task using
only 30 attributes. For the application categorization task, with 50
attributes, the resulting accuracy was 98.62%, indicating that removing a signiﬁcant part of these characteristics does not aﬀect
the overall performance.
The remainder of this article is structured as follows: works related to traﬃc classiﬁcation using diﬀerent approaches are discussed
in Section 2. Section 3 describes the dataset used for classiﬁcation and
characterization of traﬃc on Darknet, and describes the pre-processing
steps that we adopted to improve the quality of the data used in the
training of models. In addition, we also describe the extracted attributes
based on those existing in the dataset. The creation and performance
analysis of the DT, RF, and MLP, models are described in Section 4. In
addition, we also perform a model selection by estimating their performance and comparing them with statistical tests in Section 5, and we
perform a feature selection to analyze the importance of attributes in
traﬃc classiﬁcation tasks. Finally, the conclusions and future work of
this article are presented in Section 6.
2. Related work
Before showing diﬀerent solutions to the Traﬃc Classiﬁcation problem, it is necessary to understand the deﬁnition of the problem, which
consists of using traﬃc data between sender and receiver to classify and
categorize the application used. One of the main challenges is to carry
out this task using encrypted data, an approach made in two databases
provided by the University of New Brunswick, the ISCXVPN2016 (DraperGil et al., 2016) and ISCXTor2016 (Lashkari et al., 2017), which, respectively, provide traﬃc over networks using Virtual Private Network
(VPN) and The Onion Router (Tor).1 Other related works, like (Bovenzi

1

https://www.torproject.org/.
2

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

Table 1
Related work summary.
Proposal

Dataset

Attributes

ML/DL

Acc.

Gurdip Kaur and Habibi Lashkari (2020)

CIC-Darknet2020

VPN, Tor

Deep Image Learning

86%

Draper-Gil et al. (2016)

ISCXVPN2016

VPN

MLP, KNN, C4.5

80%

Lotfollahi et al. (2020)

ISCXVPN2016

All

CNN + AutoEnconder

90%

Crotti et al. (2007)

CIC-Darknet2020

HTTP, POP3, SMTP, FTP, IMAP, SSH, TELNET

Statistical

91%

This work

CIC-Darknet2020

All + n-grams

DT, RF, MLP

99.89%

negger et al., 2013), and manipulating the original records.2 These
changes and comparisons allow the evolution of both the base and the
highlighted theme (Table 1).
3. Dataset and methodology
3.1. Dataset
The CIC-Darknet2020 dataset is utilized for the development of
classiﬁcation models. It has records of traﬃc from the surface web and
from both the datasets ISCXTor2016 and ISCXVPN2016 (Gurdip Kaur
& Habibi Lashkari, 2020), containing Tor and VPN traﬃc data, respectively. CIC-Darknet2020 considers as Darknet traﬃc the data that
comes from Tor and VPN networks. The dataset establishes two classiﬁcation tasks related to the traﬃc classiﬁcation problem. The ﬁrst task
is the origin detection of the traﬃc, in which the classes are Benign,
representing surface web traﬃc, and Darknet. Fig. 1 shows the data
distribution regarding the traﬃc origin. The other task is the characterization of the traﬃc in 8 labels. These labels are the applications
that originate the traﬃc, being them: browsing, email, chat, audiostreaming, video-streaming, ﬁle-transfer, VoIP (Voice Over IP), and P2P
(Peer-to-Peer).
The dataset has a variety of ﬁelds for analysis, bringing information
about the origin and destination IPs, ports, duration of packet traﬃc,
and other related measures. There are 141.528 records, of which 24.310
come from the Darknet and 117.218 were from benign networks. This
proportion diﬀerence comes from the fact that the services found on the
Darknet are not indexed by search engines. Besides, they need special
applications, like Tor, to access them (Gurdip Kaur & Habibi Lashkari,
2020). Fig. 2 shows the distribution of the applications that originate
the traﬃc. It is clear that streaming, audio, and chat applications are
the most common for data from Darknet, while for benign networks,
they are the minority.

Fig. 1. Distribution by the data source.

3.2.1. Labels correction
The dataset comes with duplicate labels on both label types made
available by the dataset. Through label inspection, it is possible to observe a lack of standardization on label names and redundancy. To
approach this issue, we standardize the names by choosing one of the
duplicates. For example, records with the labels AUDIO-STREAMING
(capital letters) were replaced by Audio-Streaming.
3.2.2. Features encoding
Most machine learning models only work on numeric data. However, frequently datasets include categorical variables representing, as
the name says, categories or labels. Unlike numerical variables, values
on a categorical variable can not be ordered; that is, its magnitude is not
relevant to the task in question. The categories usually are not numeric;
therefore, it’s necessary to apply an encoding method to transform them
into numbers. One of the possibilities is the simple mapping from each
category to integers; however, the resulting numbers can turn out to be
orderable between them, something that is not desirable for category
values (Zheng & Casari, 2018).
The value of a subnet regarding another is irrelevant to the problem,
so features corresponding to IP addresses on the dataset are examples
of categorical variables. Since the value of a subnet does not necessarily
indicate the origin of the traﬃc or its generating application. The concept of n-grams models approaches the problem of IP address encoding
with a more generic mapping. Initially, these models were proposed for
natural language processing and currently are the dominant representation in many detection systems (Wressnegger et al., 2013).
One of the possible applications of n-gram models is the direct capture of IP address subnets. The RFC 950 (Mogul et al., 1985) deﬁnes a
3-level interpretation model for internet addresses, where the highest
level represents the internet as a whole, the level below are the individual networks, and the last level represents the subnets that are useful
for networks belonging to moderately large organizations. Thus, each
of these IP addresses interpretation levels can be represented with the
utilization of unigrams, bigrams, and trigrams models, in an attempt to
capture the traﬃc subnet of origin.

3.2. Data preparation
The performance of data-based models is greatly aﬀected by the
quality of the data used during their creation. This challenge increases
when using large datasets from the real world, which usually has
quality-related problems due to missing, inconsistent data. There are
several reasons for the low quality of datasets in the real world, which
can be caused by human or computer error, incorrect data submitted
by users, and faulty data collection instruments, among other problems
that may occur. Data pre-processing techniques aim to improve data
quality and may improve the eﬃciency of subsequent processes (Han
et al., 2011). The following subsections present the pre-processing techniques applied in this paper to improve the learning eﬃciency and the
accuracy of machine learning models in the tasks of detection and characterization of Darknet traﬃc.

2 CIC-Darknet2020 Internet Traﬃc dataset (Gurdip Kaur & Habibi Lashkari,
2020) records bi-directional ﬂows represented by a ﬂow-id and its attributes,
e.g., IP Address, Src Port.

3

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

Fig. 2. Occurrence probability of the traﬃc related to service.

Fig. 3. Feature encoding with One Hot Encoding.

purpose, we applied the standard scaling method to all features. This
technique works by subtracting the feature mean from values and scaling them, so the features have a unitary variance (Zheng & Casari,
2018).

Table 2
IPs addresses division in grams example.
IP

Unigram

Bigram

Trigram

172.168.15.14

172

172 168

172 168 15

182.170.224.79

182

170 224

182 170 224

3.2.3. Feature extraction
The dataset provides information about the origin and destination
IP addresses, enabling the extraction of more features related to the
network traﬃc. One of the possibilities is the application of one-hot
encoding. However, the usage of n-grams can help in decreasing the
percentage of false positives on predictions. Hence, the dataset was
extended using the IP addresses, fragmenting them into unigrams, bigrams, and trigrams. Furthermore, were used information from hosting,
geolocation, and bogons (false addresses), between other features with
the aid of the IpInfo library.
Another feature extracted was the time that the traﬃc data capture
started from the traﬃc timestamp. Fig. 4 shows the relationship between
the capture time for both labels related to the origin of the traﬃc using TCPDump and Wireshark. It is possible to verify that two diﬀerent
patterns take place in the traﬃc generation behavior for each label, being possible to observe that these patterns on traﬃc time can be used
by the models in the learning phase, making the traﬃc time a relevant
feature for traﬃc classiﬁcation.
Besides being possible to see the timetable distinction, this time relation allows seeing when there is a high probability of utilization of
each network. For the Benign network, can be observed a high traﬃc
density between 7 am, and 12 am, with some peaks at dawn. On the
Darknet traﬃc side, the traﬃc distribution is sparser, having a high utilization peak at dawn and two smaller peaks in the afternoon. These
relations are almost an exclusive disjunction; that is, there is a considerable probability of not having high traﬃc on the Darknet at the same
time of Benign networks, which allows smoother learning of these patterns on classiﬁcation models.

Table 2 exemplify the division of the IP addresses in grams, allowing
us to observe how the process is similar to what the subnet mask does
for subnet identiﬁcation but, as we do not have access to the subnet
masks, we use the grams for each possible interpretation level. With
these new attributes, a machine learning model can be able to learn the
most common preﬁxes or subnets for a traﬃc type as a piece of relevant
information for new traﬃc predictions.
The ﬁrst encoding is applied to the unigrams, bigrams, and trigrams
created from the IP addresses. We used the hashing encoding technique
to create 100 new features named with the preﬁx 𝑐𝑜𝑙_ followed by the
attribute ID generated by the method. As noted by Weinberger et al.
(2009), the hashing encoding technique enables attributes encoding regarding one hot encoding. One hot encoding does categorical feature
encoding by transforming each of the categories into new binary features indicating if that category belongs to the corresponding dataset
example, as shown in Fig. 3. This could lead to a large number of new
features depending on the number of unique categories on a categorical
variable. On the other hand, the hashing encoding has the disadvantage
that the new features can not be easily interpreted as the generated features can not be mapped back to their original values. Furthermore, as
we could extract the country of origin from the network addresses, this
information is used as a feature for model training after applying an
ordinal encoding transformation.
One of the most important transformations applied to data is feature scaling. Generally, few machine learning models have good performance with features with diﬀerent scales. Therefore, it is necessary
to transform feature values to have the same numeric range. For this
4

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

Fig. 4. Traﬃc density in a given hour.

𝑟𝑒𝑐𝑎𝑙𝑙 =

𝑇𝑃
𝑇𝑃 + 𝐹𝑁

(2)

• F-score: can be viewed as a weighted average of the precision and
recall. It reaches its best value at one and the worst at zero. Both
precision and recall have the same contribution to the F-score.
𝐹 − 𝑠𝑐𝑜𝑟𝑒 =

3.3. Model evaluation
With the variety of classiﬁcation models available, metrics are
needed to assess their performance in a given task so that it is possible to choose the best model. This process is called model selection.
Two common methods for accuracy assessment are the holdout and the
random subsampling methods. The holdout method works by randomly
partitioning two independent sets, training and a test set, and the accuracy is deﬁned as the number of hits on the test set. The random
subsampling is similar to the holdout method, but the holdout method
is repeated k times, and the accuracy is the average of the accuracies
obtained in each iteration (Han et al., 2011).
To estimate the accuracy of the models, stratiﬁed k-fold crossvalidation is used where the k-fold has 𝑘 = 10. This method divides the
data into k groups of approximately equal size and distribution of labels, where the ﬁrst 𝑓 𝑜𝑙𝑑 is used as the validation set, and the method
is trained on the remaining 𝑘 − 1 folds. Unlike the holdout and random
subsampling methods, here, each sample is used the same number of
times for training and once for testing. Accuracy with k-fold is deﬁned as
the average accuracy of all training and validation pairs combinations;
Fig. 5 illustrates the procedure. Precision, recall and F-score (Géron,
2019) are used as metrics in both classiﬁcation tasks. The equations
of the evaluation metrics used are listed below, where TP, TN, FP, and
FN are the classiﬁcation of true positives, true negatives, false positives,
and false negatives, respectively.

4. Evaluation
The evaluated models are based on decision trees and a simple neural network selected due to their simplicity and ease of interpretation.
In addition, it conducts a selection of characteristics to estimate the
importance of attributes according to their inﬂuence on classiﬁcation.
Next, the chosen models (Géron, 2019) are brieﬂy described.
• Decision Trees (DT): non-parametric supervised learning models
that can be used for classiﬁcation and regression. It works by learning simple decision rules inferred from the data to predict the target
variable. They are simple models to understand and interpret, and
the generated trees can be visualized. Some advantages of decision
trees are: Simple to understand and interpret, and possible to be
visualized. Non-require data normalization or hard work for data
preparation. Its cost is logarithmic in the number of data points
used to train the tree. Moreover, it is considered easy to interpret
and explain by a boolean logic supported by a white-box model.
However, the disadvantages of decision trees include the following: DT can create over-complex trees that do not generalize the
data well. This is called overﬁtting. It can be unstable, considering its small variations in the data might result in a completely
diﬀerent tree being generated. By the way, it is possible to mitigate almost all of these problems. Fig. 6 presents a DT with green

• Precision: can be thought of as a measure of exactness, i.e., the
percentage of examples labeled as positive are actually such;
𝑇𝑃
𝑇𝑃 + 𝐹𝑃

(3)

One of the ways to approach the model selection problem is by selecting the model with fewer errors using k-fold. However, k-fold only
provides an estimate of the error in the actual population of the future data. Although the model errors appear to be diﬀerent between
them, this diﬀerence may not be statistically signiﬁcant. To determine
whether the diﬀerence in the error means it is statistically signiﬁcant,
we need to employ a statistical signiﬁcance test. Thus, we can state that
the means cannot vary outside a conﬁdence interval with future samples (Han et al., 2011).
The choice of the statistical test must be made carefully, to avoid
misinterpretation of the models. In (Dietterich, 1998), ﬁve commonly
used statistical tests are compared with the objective of determining
the one with the slightest error of the type I, that is, the one with the
most negligible probability of detecting a diﬀerence when it does not
exist. The authors conclude that for algorithms that can be executed
only once, the use of the McNemar test is recommended. However, for
algorithms that can be executed ten times, they recommend the 5x2 cv
test (cross-validation)) as it has the smallest error of type I.

Fig. 5. K-fold illustration with k = 5 (Fedotenkova, 2016).

𝑝𝑟𝑒𝑐𝑖𝑠𝑖𝑜𝑛 =

2 × (𝑝𝑟𝑒𝑐𝑖𝑠𝑖𝑜𝑛 × 𝑟𝑒𝑐𝑎𝑙𝑙)
𝑝𝑟𝑒𝑐𝑖𝑠𝑖𝑜𝑛 + 𝑟𝑒𝑐𝑎𝑙𝑙

(1)

• Recall: is a measure of completeness, i.e., the percentage of positive
samples labeled as such, the same as sensitivity;
5

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

Table 3
Models evaluation metrics summary.
Precision

Recall

F-score

10-fold

DT

0.9964

0.9971

0.9967

99.89%

RF

0.9987

0.9947

0.9967

99.9%

MLP

0.9992

0.9915

0.9953

99.84%

Table 4
Confusion matrix labels.

Fig. 6. Typical architecture of a DT model.

nodes selected by the decision tree algorithm based on boolean
logic. The entropy concept is used by DT, where the 𝑝+ is the probability of a positive class, in contrast to the 𝑝− probability of a
negative class in a subset of the training example, as is possible to
see on 𝐸(𝑆) = −𝑝(+) 𝑙𝑜𝑔𝑝(+) − 𝑝(−) 𝑙𝑜𝑔𝑝(−) .
• Random Forest (RF): is a ensemble model that uses DTs as weak classiﬁers in order to generate a robust classiﬁer. The RF trains each of
the DTs with the Bagging technique to generate a classiﬁer with better performance than its individual components. RFs are frequently
used as “black box” models in computational intelligence solutions.
They generate reasonable predictions across a wide range of data
while requiring trim conﬁguration. However, RFs, in general, are
more complex compared to DTs. In this case, RF is an excellent
way to conduct more extensive experiments with more data, even
losing the comfortable model interpretability oﬀered by DT. Fig. 7
shows a set of DTs used to create the RF model.
• Multilayer Perceptron (MLP): is a class of feedforward artiﬁcial neural networks (ANN). It is composed of an Input layer, one or more
layers of perceptrons, also called Hidden layers, and an Output
layer responsible for the ﬁnal classiﬁcation. Except for the input
layer, every MLP node is a perceptron model and a non-linear activation function. Fig. 8 shows the architecture of an MLP. Its advantages are adaptive learning, a huge number of possible applications,
and do not assume the underlying probability density functions
or other probabilistic information about the pattern classes under
consideration compared to other probability-based models. But, its
disadvantages can be mentioned by the hidden layers with a nonconvex loss function where more than one local minimum exists.
Therefore, diﬀerent random weight initializations can lead to different validation accuracy and require tuning several hyperparameters, such as hidden neurons, layers, and iterations. To conclude,
MLP is sensitive to feature scaling. Keeping it in mind, the MLP can
be a good neural network for any problem, mainly for temporal
series.

Initials

Label

Initials

AS

Audio Streaming

P

Label
P2P

B

Browsing

FT

File Transfer

VS

Video Streaming

C

Chat

V

VOIP

E

Email

traﬃc detection. It is possible to observe that, for both classes, the vast
majority of them are correctly classiﬁed. Through the confusion matrices of Fig. 9 it is possible to see that for the class Darknet, there is a
percentage of 0.45% wrongly classiﬁed as Benign, and for the opposite,
0.02%. In an application in which the correct detection of Darknet trafﬁc is more important, MLP is the most suitable as it has a lower number
of false positives among the analyzed models.
The Table 3 summarizes the metric values of each model in the classiﬁcation between the labels Benign and Darknet, with the values in bold
as the best results obtained for comparison between the models. Furthermore, the model achieved an accuracy of 99.89% in 10-fold and
good generalization, thus better results than the literature, where Gurdip Kaur and Habibi Lashkari (2020) achieved an accuracy of 94% in
the detection of Darknet traﬃc.
4.2. Darknet traﬃc characterization
Fig. 11 lists, in polar coordinates, the complement values of the precision, recall, F-score, and also the classiﬁcation error for the DT models,
RF and MLP respectively, for traﬃc characterization. The complements
of these metrics were presented to provide better visualization. It is
possible to verify that only the class Browsing had a discrepant distance
from the maximum value of the metrics. In addition, among all models,
DT had the best results in all metrics, while MLP and RF had worse values in more labels, in addition to Browsing, RF also had worse results in
relation to Video-Streaming, while MLP had worse results on P2P, Email,
Video-Streaming and Browsing tags. The confusion matrices of Figs. 10a,
10b, and 10c, respectively corresponding to DT, RF, and MLP, and the
acronyms of the rows and columns correspond to the Table 4 labels, it
is evident that the common errors are related to traﬃc with Chat and
Audio-Streaming labels, which may indicate that there is some similarity
in the traﬃc corresponding to these labels, which can cause confusion
in the models.
Fig. 11d shows the errors obtained by the models in the classiﬁcation of each type of service associated with the traﬃcs, making it
evident that the classes that obtained more signiﬁcant classiﬁcation errors are those least represented in the dataset. RF and MLP attenuated
the errors of these classes. Therefore, they are more suitable models for
traﬃc classiﬁcation, assuming that the addition of new examples follows the same training set probability distribution and that the traﬃc
corresponding to these labels is not of great importance for the application of the model. We obtained a minor classiﬁcation error with the
DT even in classes with less representation. So, the model proposed by
Gurdip Kaur and Habibi Lashkari (2020) using deep learning obtained
an overall accuracy of 86% against 99.03% of our DT’s model. Considering it, we achieved an improvement of 13.03%, which may indicate
that the problem of characterization of Darknet traﬃc is better solved

However, a disadvantage of the models used is that they cannot be
trained online. In other words, they cannot learn from a new example unless the model is retrained with all the previous data and the
new examples. All experiments were done with the sklearn library, in
the Python programming language, on a computer with a Intel Core i57200U processor with 4 2.5 GHz cores, 20 GB of RAM, and the Ubuntu
20.04 operating system. Each one of the models were trained keeping
the default parameters deﬁned by sklearn.
4.1. Darknet traﬃc detection
In Figs. 9a, 9b, and 9c corresponding to the DT, RF, and MLP models it is possible to observe the models confusion matrices on the task of
6

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

Fig. 7. Typical architecture of an RF model.
Table 5
10-10-fold estimated accuracy for darknet traﬃc
detection and characterization.
DT

RF

MLP

Detection

99.905

99.907

99.837

Characterization

99.154

98.754

97.731

Table 6
p-values for traﬃc detection and characterization models
comparison.

Fig. 8. Typical architecture of an MLP model (Géron, 2019).

DT vs RF

DT vs MLP

MLP vs RF

Detection

0.095

0.286

0.389

Characterization

0.013

0

0.001

performance of the models, it is necessary to run the 5x2 cv to see if
these results are statistically signiﬁcant.
Figs. 12a and 12b summarize the accuracy of the models in the detection and characterization tasks of Darknet traﬃc in boxplots. It is
evident that in both classiﬁcation tasks, the DT obtained better results.
We also observed that the MLP had a greater variance in the estimates
than the other models. To verify whether the diﬀerence in the accuracy
estimates of the models is statistically signiﬁcant, we conduct statistical
tests.
As a null hypothesis for the statistical tests, we consider that the
models do not signiﬁcantly diﬀer. We also assume that the conﬁdence
margin for the statistical test result is 95%. If the p-value is less than
the 𝛼 threshold of 0.05, the value used as a convention (Dahiru, 2008),
then the null hypothesis is rejected, and there is a statistically signiﬁcant diﬀerence between the compared models. Table 6 the p-values are
summarized by comparing the models from 2 to 2 to see if there is any
diﬀerence between them. The results indicate that there is no statistically signiﬁcant diﬀerence between the models for detecting darknet
traﬃc, while all models for characterization have a statistically signiﬁcant diﬀerence between them.
Despite the results favoring DT as the best model for both classiﬁcation tasks, essential points must be considered. The DT is a model that
does not allow us to update it after its training. Every time a sample or
a set of them arrives, it is necessary to retrain the entire model to consider the new samples. As the problem of interest consists of data that
can come as a stream, it would be interesting to update the model as
new samples appear. This type of update is called online learning. Thus,

with simpler and easier-to-interpret models without the need to resort
to more complex models and that demands more computing resources.
However, in applications where it is necessary to update the model as
new examples arrive, MLP is the most suitable model as it is the only
one that allows online learning.
5. Evaluation
5.1. Model evaluation
As the models trained in this paper can be run ten times, we chose
5x2 cv as the test for model selection. In 5x2 cv, there are ﬁve executions of cross-validation with 2 folds. In each execution, the data is
randomly partitioned into two sets of approximately equal size, where
each of the models is trained on one set and tested on the other. After the results are generated, a paired student’s t test is performed to
generate the ﬁnal statistics (Dietterich, 1998).
Table 5 summarizes the accuracies estimated by the 10-10-fold with
all models for the traﬃc detection and characterization tasks. The accuracies are estimated as the average of the accuracies obtained in all
10-fold runs. As it is possible to observe, all models obtained very
similar results for traﬃc detection. For the characterization, the decision tree had better results than the random forest and the multilayer
perceptron. However, although there are noticeable diﬀerences in the
7

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

Fig. 9. Confusion matrices of Darknet traﬃc detection.
Table 7
Summary of attribute selection results.

Table 8
Characterization.

# attributes

Final validation

10-fold

Attribute

Relevance

Detection

28

99.95%

99.91%

col_91

0.7628

Characterization

73

99.12%

98.94%

col_49

0.1205

Bwd Init Win Bytes

0.0418

in the context in which real-time traﬃc analysis is needed, MLP is the
best as it is the only one used in this work that allows an online update.
5.2. Feature importance analysis
Feature selection algorithms aim to select, according to some criterion, a subset from the original set of problem attributes by removing
irrelevant or redundant attributes in order to maintain the same, or
nearly the same, results (Villela et al., 2011). As the models analyzed in
this work already have almost optimal performance, selecting attributes
mainly reduces the computational cost of the model. This process also
aids us on the analyzes the most critical attributes of the problem.
In this work, we use the Recursive Feature Elimination (RFE)
method that works by recursively removing a ﬁxed number of attributes
and retraining the model. We used stratiﬁed cross-validation with 10fold to assess the quality of the subsets generated by the RFE. Thus, the
subset with the highest accuracy and the lowest number of attributes
is selected at the end of the execution. Due to the results, we show
in Section 5.1, we decided to use the Random Forest model as the internal classiﬁer of the RFE. Another reason for using RF is that it also
allows knowing the importance of attributes, called Gini importance,
after training the model. Thus, after selecting the features, we also analyze the essential attributes considering the new attributes inserted in
the dataset. As the purpose of this work is not to classify the traﬃc in
real-time, there is no problem in keeping attributes that can only be
obtained at the end of the ﬂow, such as the Flow Duration.
Due to the random nature of RFE, each run may generate a subset of
diﬀerent attributes. Consequently, The resulting subset should be concol_24

0.0408

Idle Min

0.0141

col_96

0.0034

Idle Std

0.0021

col_45

0.0018

hour

0.0017

Average Packet Size

0.0015

Flow IAT Std

0.0011

col_1

0.0009

Idle Mean

0.0009

Flow IAT Min

0.0008

Fwd Packet Length Max

0.0008

FIN Flag Count

0.0007

Src Port

0.0006

FWD Init Win Bytes

0.0006

Fwd IAT Total

0.0005

Flow Duration

0.0004

col_71

0.0004

Fwd Packets/s

0.0004

sidered an approximation of the optimal subset of attributes. In Table 7
we summarize the results. The attributes were selected based on the
10-fold, and a validation set was also separated with 33% of the samples with stratiﬁed random sampling. It is possible to see that there was
a signiﬁcant reduction in the number of attributes of the dataset without any loss in classiﬁcation accuracy in both tasks. In the ﬁrst one, for
8

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

Fig. 10. Models confusion matrix for Darknet traﬃc detection.

instance, we obtained a reduction of 83% of the total attributes, and in
the traﬃc characterization, the number of attributes is reduced by 72%.
Tables 8 and 9 show the twenty-two most important attributes in
the sets selected by RFE in both classiﬁcation tasks. It is evident that in
both sets, the attributes inserted by data pre-processing are in the ﬁrst
place concerning their importance for the models’ classiﬁcation. As we
can see, some of the new features have higher ranks than the original
features, for example, the features col_91 and col_ 76 have, respectively, relevances of 0.7628 and 0.4287 in their respective tasks. This
indicates that the new attributes may encode pieces of information that
are relevant to their tasks and that it is more advantageous to process
the attributes than to remove them when they do not appear to be relevant, as done in Gurdip Kaur and Habibi Lashkari (2020).

performed a feature selection process with the RFE algorithm. We veriﬁed that the newly generated features are relevant for the prediction
of the models. This makes it evident that, in some cases, it is preferable
to process features that, at ﬁrst sight, have little relevance instead of
just removing them. Furthermore, it was possible to obtain a signiﬁcant
reduction in the number of attributes of the original dataset without
losing prediction performance.
It is evident that simple machine learning algorithms, such as decision tree-based ones, are good candidates for obtaining competitive
results for real-world problems. In this work, we observed that DT, RF,
and MLP obtained a result up to 13% higher than the model presented
in Gurdip Kaur and Habibi Lashkari (2020), in addition to its eﬃciency
being improved with a careful pre-processing of existing attributes.
Through McNemar’s statistical test, it was possible to observe that all
models obtained equivalent performance for the traﬃc detection task.
However, for the traﬃc characterization, the best model was the DT,
and the MLP had the worst performance concerning the unbalanced
labels in the dataset. Although MLP has the worst performance, it is the
most suitable for applications that need to analyze traﬃc in real-time as
it can be updated as new examples arrive. In future work, it is necessary
to analyze techniques to improve the performance of MLP concerning
unbalanced labels through methods, for example, that generate artiﬁcial
data for the minority classes.
As future research directions are possible to conduct experiments
to classify ﬂows inside cryptographic tunnels. A candidate to help in
this way is the framework presented by Bovenzi et al. (2020). Another
way is to involve Deep Packet Inspection (DPI) as enrichment for data
analysis.

6. Conclusion
In this work, we approach the problems of detection and characterization of traﬃc coming from Darknet through the use of learning
models based on decision trees, being DT, RF, and MLP capable of classifying new records of traﬃc with an accuracy greater than 97% for
each of the classiﬁcation tasks.
New features were also extracted from the original dataset by searching for information on the source and destination IPs of the traﬃc and
encoding them with hashing encoding. Another feature generated was
the time when the traﬃc occurred by the timestamp included in the
dataset. Our initial analysis showed the potential to contribute to the
eﬃciency of the trained models due to the trend of occurrence of internet traﬃc common and Darknet, at diﬀerent times. Finally, we also
9

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

Fig. 11. Evaluation metrics for the models in polar coordinates.

Fig. 12. Boxplot of accuracies estimated by 10-10-fold.

7. List of acronyms
DL
DPI
DT

FTP
HTTP
IMAP
IP
KNN

Deep Learning . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
Deep Packet Inspection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
Decision Tree . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
10

File Transfer Protocol . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
Hypertext Transfer Protocol . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .2
Internet Message Access Protocol . . . . . . . . . . . . . . . . . . . . . . . . . . 2
Internet Protocol . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .2
K-Nearest Neighbors . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2

Intelligent Systems with Applications 18 (2023) 200199

M. Coutinho Marim, P.V.B. Ramos, A.B. Vieira et al.

Data availability

Table 9
Traﬃc detection.

MLP
P2P
POP3
RF
RFE
SMTP
SSH
TELNET
Tor
VPN

Attribute

Relevance

col_76

0.4287

hour

0.1455

Bwd Packet Length Min

0.1262

Idle Max

0.0517

Fwd Header Length

0.0338

Idle Min

0.0335

col_58

0.0312

Packet Length Max

0.0245

Flow Duration

0.0158

col_75

0.0142

col_11

0.0128

col_21

0.0112

col_45

0.0107

Src Port

0.0083

Dst Port

0.0078

Flow IAT Max

0.0053

Fwd Seg Size Min

0.0042

Flow IAT Min

0.0039

col_91

0.0037

FWD Init Win Bytes

0.0029

Subﬂow Fwd Bytes

0.0029

Fwd IAT Max

0.0026

Data will be made available on request.
References
Bovenzi, G., Aceto, G., Ciuonzo, D., Persico, V., & Pescapé, A. (2020). A big data-enabled
hierarchical framework for traﬃc classiﬁcation. IEEE Transactions on Network Science
and Engineering, 7(4), 2608–2619. https://doi.org/10.1109/TNSE.2020.3009832.
Crotti, M., Dusi, M., Gringoli, F., & Salgarelli, L. (2007). Traﬃc classiﬁcation through simple statistical ﬁngerprinting. ACM SIGCOMM Computer Communication Review, 37(1),
5–16.
Dahiru, T. (2008). P-value, a true test of statistical signiﬁcance? A cautionary note. Annals
of Ibadan Postgraduate Medicine, 6(1), 21–26.
Dietterich, T. G. (1998). Approximate statistical tests for comparing supervised classiﬁcation learning algorithms. Neural Computation, 10(7), 1895–1923.
Draper-Gil, G., Lashkari, A. H., Mamun, M. S. I., & Ghorbani, A. A. (2016). Characterization of encrypted and vpn traﬃc using time-related. In Proc. of the int. conference on
information systems security and privacy (ICISSP) (pp. 407–414).
Fedotenkova, M. (2016). Extraction of multivariate components in brain signals obtained
during general anesthesia. Ph.D. thesis, Université de Lorraine.
Géron, A. (2019). Hands-on machine learning with Scikit-Learn, Keras, and TensorFlow: Concepts, tools, and techniques to build intelligent systems. O’Reilly Media.
Gurdip Kaur, A. R., & Habibi Lashkari, A. (2020). aDIDarknet: A contemporary approach
to detect and characterize the darknet traﬃc using deep image learning. In 10th
international conference on communication and network security (ICCNS 2020).
Han, J., Pei, J., & Kamber, M. (2011). Data mining: Concepts and techniques. Elsevier.
Lashkari, A. H., Draper-Gil, G., Mamun, M. S. I., & Ghorbani, A. A. (2017). Characterization of tor traﬃc using time based features. In Proc. of the int. conference on information
systems security and privacy (ICISSP) (pp. 253–262).
Lotfollahi, M., Siavoshani, M. J., Zade, R. S. H., & Saberian, M. (2020). Deep packet: A
novel approach for encrypted traﬃc classiﬁcation using deep learning. Soft Computing, 24(3), 1999–2012.
Medeiros, D., Cunha Neto, H., Andreoni Lopez, M., Magalhaes, L., Silva, E., Vieira, A.,
Fernandes, N., & Mattos, D. (2019). Análise de dados em redes sem ﬁo de grande
porte: Processamento em ﬂuxo em tempo real, tendências e desaﬁos. Minicursos do
Simpósio Brasileiro de Redes de Computadores-SBRC, 2019, 142–195.
Mirea, M., Wang, V., & Jung, J. (2019). The not so dark side of the darknet: A qualitative
study. Security Journal, 32(2), 102–118.
Mogul, J., et al. (1985). Internet standard subnetting procedure.
Montieri, A., Ciuonzo, D., Bovenzi, G., Persico, V., & Pescapé, A. (2020). A dive into
the dark web: Hierarchical traﬃc classiﬁcation of anonymity tools. IEEE Transactions
on Network Science and Engineering, 7(3), 1043–1054. https://doi.org/10.1109/TNSE.
2019.2901994.
Parchekani, A., Naghadeh, S. N., & Shah-Mansouri, V. Classiﬁcation of traﬃc using neural
networks by rejecting: A novel approach in classifying vpn traﬃc. arXiv preprint
arXiv:2001.03665.
Villela, S. M., Xavier, A. E., & Neto, R. F. (2011). Seleção de características com busca
ordenada e classiﬁcadores de larga margemCOPPE, programa de engenharia de sistemas e
computação. Universidade Federal do Rio de Janeiro.
Weinberger, K., Dasgupta, A., Langford, J., Smola, A., & Attenberg, J. (2009). Feature
hashing for large scale multitask learning. In Proc. of the 26th annual international
conference on machine learning (pp. 1113–1120).
Wressnegger, C., Schwenk, G., Arp, D., & Rieck, K. (2013). A close look on n-grams in
intrusion detection: Anomaly detection vs. classiﬁcation. In Proc. of the 2013 ACM
workshop on artiﬁcial intelligence and security (pp. 67–76).
Zheng, A., & Casari, A. (2018). Feature engineering for machine learning: Principles and
techniques for data scientists. O’Reilly Media, Inc.

Multilayer Perceptron . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .2
Peer-to-Peer . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
Post Oﬃce Protocol . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .2
Random Forest . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
Recursive Feature Elimination . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
Simple Mail Transfer Protocol . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
Secure Shell . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
TELNET Protocol . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
The Onion Router . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .2
Virtual Private Network . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .2

CRediT authorship contribution statement
Mateus Coutinho Marim: Proposal, experiments and text.
Paulo Vitor Barbosa Ramos: Proposal, experiments, and text.
Alex B. Vieira: Review the methodology, the results of the experiments, and the text.
Edelberto Franco Silva: Review the methodology, the results of the
experiments, and the text.
Roberto M. de Oliveira: Review the methodology and evaluation
conduction.
Declaration of competing interest
The authors declare that they have no known competing ﬁnancial
interests or personal relationships that could have appeared to inﬂuence
the work reported in this paper.

11
PAPER_TEXT
