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
# [056] Encrypted Traffic Classification Using Graph Convolutional Networks
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
编号：056
题名：Encrypted Traffic Classification Using Graph Convolutional Networks
年份：2020
DOI：10.1007/978-3-030-65390-3_17
来源：Lecture Notes in Computer Science
PDF：paper/10.1007_978-3-030-65390-3_17.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测、图学习、知识图谱与威胁情报
相关性：强相关，分数 14
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\056.txt
- 原始字符数：11894
- 本次发送字符数：11894
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
ETCNet: Encrypted Traffic Classification using Siamese
Convolutional Networks
Lu Xu

Daihui Dou

H. Jonathan Chao

New York University
New York, USA
lx643@nyu.edu

New York University
New York, USA
dd2956@nyu.edu

New York University
New York, USA
chao@nyu.edu

ABSTRACT

that are sensitive to delay or packet loss, achieving better network
performance and users’ quality of experience (QoE). Moreover, traffic classification can also distinguish malware traffic from normal
traffic [6] to enhance network security.
An encrypted Internet protocol, HTTP2, has been widely used
by most top websites in the world [3]. According to [2], the usage
of HTTP2 for the websites has reached 43.6%. Just last year alone,
the adoption of HTTP2 increased by nearly 10%. The popularity
of HTTP2 shows the necessity of developing an effective traffic
classification scheme for encrypted packet streams. However, the
shift has created tremendous difficulty for traffic classification, because the information in packet payload is no longer available for
inspection.
While researchers are using machine learning to perform traffic classification, it has been very challenging for them to devise
effective algorithms due to the lack of available datasets to train
and evaluate their algorithms. Unlike many other machine learning
problems, such as computer vision (CV) and natural language processing (NLP), network traffic contains users’ personal information,
making it not always collectable. Moreover, because of the sensitivity of personal data, researchers in the network community have
the concern of sharing the real users’ data even after they manage
to collect them, making it very difficult, if not impossible, for the
network community to collaboratively form a large dataset. What’s
more, the contents of Internet traffic tends to change quickly, rendering the collected dataset obsolete quickly and requiring a new
effort of collecting them again.
To meet the need of classifying traffic and overcoming the problem of lacking datasets, we introduce ETCNet, a classification model
based on Siamese convolutional networks (to be discussed in Section II), which only needs a small dataset to train the model while
achieving high classification accuracy on encrypted Internet traffic. Heuristically, the model converts a multi-class classification
problem to a binary classification problem, which reduces the problem difficulty and the datasets needed. The Siamese convolutional
network takes a pair of traffic flows as input and produces an intermediate feature, capturing the level of similarity of the two flows. A
classifier is then used to produce a binary label, indicating whether
the two flows belong to the same application. To ensure the robustness of the model, not being influenced by spoofed identification
or port numbers, the model only uses the encrypted payload of
the packet stream. A detailed description of the feature selection is
discussed in Section III.
To evaluate the ETCNet’s prediction accuracy, we created a
dataset via mocking the users’ browsing behavior. As shown in Tab.
1, eight of the world’s top one hundred applications [1] are chosen
and all the applications use the HTTP2 protocol. We recorded the

As more and more Internet traffic is encrypted, classifying their
flows for the usage in application-aware networking (AAN) and
application-network integration (ANI) becomes increasingly important and challenging. Traditional deep packet inspection approaches
are no longer capable of identifying the encrypted packet streams,
and hence new traffic classification methods based on machine
learning have recently been explored by several researchers. One
major challenge of using machine learning to classify encrypted
traffic is lacking real datasets. Collecting Internet traffic may leak
users’ sensitive information, which prohibits the network community from sharing the datasets they collected. In this poster, we
propose ETCNet which is a model based on Siamese convolutional
network to solve this issue. Our evaluation for the ETCNet shows
that it can achieve high accuracy by only using 40 flows of each
application to train it.

CCS CONCEPTS
· Networks → Packet classification; Network monitoring; · Security and privacy → Cryptanalysis and other attacks.

KEYWORDS
encrypted traffic classification, siamese convolutional network, machine learning
ACM Reference Format:
Lu Xu, Daihui Dou, and H. Jonathan Chao. 2020. ETCNet: Encrypted Traffic Classification using Siamese Convolutional Networks. In Workshop on
Network Application Integration/CoDesign (NAI’20), August 14, 2020, Virtual
Event, USA. ACM, New York, NY, USA, 3 pages. https://doi.org/10.1145/
3405672.3409492

1

INTRODUCTION

Internet traffic classification has become an important research
area in recent years [5]. The ability to categorize traffic to its application is critical for application-aware networking (AAN) and
application-network integration (ANI). By classifying each flow’s
application in real-time, routers or middleboxes are able to apply
different scheduling or buffer management strategies to the flows
Permission to make digital or hard copies of all or part of this work for personal or
classroom use is granted without fee provided that copies are not made or distributed
for profit or commercial advantage and that copies bear this notice and the full citation
on the first page. Copyrights for components of this work owned by others than the
author(s) must be honored. Abstracting with credit is permitted. To copy otherwise, or
republish, to post on servers or to redistribute to lists, requires prior specific permission
and/or a fee. Request permissions from permissions@acm.org.
NAI’20, August 14, 2020, Virtual Event, USA
© 2020 Copyright held by the owner/author(s). Publication rights licensed to ACM.
ACM ISBN 978-1-4503-8044-7/20/08. . . $15.00
https://doi.org/10.1145/3405672.3409492

51

NAI’20, August 14, 2020, Virtual Event, USA

Xu, et al.

Table 1: The applications collected in our dataset
Reddit
Instagram

Twitter
Wikipedia

Spotify
Amazon

2.1

Facebook
Stackoverflow

packets passing through the Network Interface Card (NIC) while
the mocked user is browsing those applications. We tested our
model on the dataset which achieves an accuracy of 92%.
The main contributions of our work are summarized as follows:
• Our proposed ETCNet model for encrypted traffic classification is able to classify packet stream’s applications by using
a very small training dataset (e.g., only 40 flows for each
application).
• We collected our own dataset for HTTP2 flows, more than
1500 flows for each application. We filtered raw Internet
traffic and stored each flow to an individual file so that the
dataset can be easily used by other researchers without much
pre-processing needed. We have uploaded our dataset on
Google Drive 1 .

2.2

3000 Nodes

Conv.

3 EVALUATION
3.1 Implementation Details

Pooling.

To evaluate the approach we proposed, we trained and test our
model on the dataset we collected. We only use 40 flows for each
application to show the effectiveness of our model even with a small
dataset. For each training batch, we randomly selected 200 input
vector pairs for training. Half of the input vector pairs have their
two traffic flows belonging to the same applications. The other 100
input vector pairs have their two traffic flows belonging to different
applications. We also generate 20 pairs for the test set in each
epoch. We run the training processing for 50 epochs. Finally, we
generate 200 pairs of flows as a validation set to evaluate the model
after training. The input vector is accumulated by concatenating
the encrypted packet payload of a flow. If a flow does not contain
sufficient byte streams, we append zeros to the end of the vector.
We add 6 consecutive numbers of "FF" between any two payloads to
serve as a boundary between them. This pattern of 6 "FF" is chosen
because it never appears in any packet payloads. With a trade-off
of accuracy and efficiency, an input vector size of 3000-bytes is
chosen.

Y(0/1)

Dense

I2
3000B

F2
100
Nodes
Application prediction component
Siamese neural encoder component

Figure 1: The proposed Siamese Convolutional Network
model. The model takes two feature vectors and outputs a
binary result.

2

Application Prediction Component

Vector 𝐹 1 and 𝐹 2 from the previous component are concatenated to
form a one-dimensional vector in this component. The concatenated
vector has a size of 200 Bytes. The two fully connected dense layers
are cascaded. The first layer has 100 nodes for each result vector
from the Siamese neural encoder component. The second layer has
1 node. The first layer has ReLU as non-linearity. The second layer
has Sigmoid as non-linearity.

F1
100
Nodes

I1
3000B

Siamese Neural Encoder Component

This component takes the feature vectors of two encrypted HTTP2
traffic flows as input. This encoder component contains two Siamese
networks that share the same weights and biases. Each network
starts with a layer of 3000 neuron nodes to take the input feature vectors 𝐼 1 and 𝐼 2 . They are connected with fully connected
one-dimensional convolutional layers respectively. The first convolutional layer has 64 filters with a kernel size of 3. The second
convolutional layer has 32 filters with a kernel size of 3. Both layers have ReLU [4] as non-linearity. A Max-Pooling layer is added
after convolutional layers to combine and reduce the spatial size of
the low dimensional representation. The Siamese neural encoder
component flattens the result of the Max-Pooling layer and outputs
two vectors, 𝐹 1 and 𝐹 2 , representing a low dimensional feature of
the two input flows.

DESIGN

Our model consists of two parts, as shown in Fig. 1, a Siamese neural
encoder component and an Application prediction component. The
model takes two flows of encrypted HTTP2 traffic as an input and
determines whether or not they belong to the same application.
Our objective is to use the Siamese neural encoder component to
obtain a low dimensional representation of the two input traffic
flows. Then the Application prediction component will suggest
whether or not the two flows belong to the same application.

3.2

Preliminary Results

We performed an experiment based on the architecture and parameter we discussed above. The test was run on the Intel(R) Xeon(R)
CPU E5-2690 v4 @ 2.60GHz CPU, 16GB Memory ,and a GeForce
GTX 1080 Graphics Processing Unit. On the dataset we collected,
our approach obtained a 92% accuracy using only 40 flows for each
application. The time spent on testing each flow is 5ms on average.
This computation time is much smaller than the duration of a whole
traffic flow, which is typically longer than 1s.

1 https://drive.google.com/open?id=1CHKcWotJg_jjE2HH6g-Z1lfr1RBBy0LO

52

ETCNet: Encrypted Traffic Classification using Siamese Convolutional Networks

NAI’20, August 14, 2020, Virtual Event, USA

REFERENCES

[4] Vinod Nair and Geoffrey E. Hinton. 2010. Rectified Linear Units Improve Restricted
Boltzmann Machines. In ICML. 807ś814. https://icml.cc/Conferences/2010/papers/
432.pdf
[5] S. Rezaei and X. Liu. 2019. Deep Learning for Encrypted Traffic Classification: An
Overview. IEEE Communications Magazine 57, 5 (2019), 76ś81.
[6] T. Shapira and Y. Shavitt. 2019. FlowPic: Encrypted Internet Traffic Classification
is as Easy as Image Recognition. In IEEE INFOCOM 2019 - IEEE Conference on
Computer Communications Workshops (INFOCOM WKSHPS). 680ś687.

[1] Alexa 2020. Alexa - Top sites. Retrieved March 31, 2020 from https://www.alexa.
com/topsites
[2] HTTP/2 2020. Usage statistics of HTTP/2 for websites. Retrieved April 3, 2020 from
https://w3techs.com/technologies/details/ce-http2
[3] HTTPS 2020. HTTPS encryption on the web. Retrieved March 30, 2020 from
https://transparencyreport.google.com/https/overview

53
PAPER_TEXT
