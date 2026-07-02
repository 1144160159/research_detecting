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
# [198] CoopGBFS: A Federated Learning and Game-Theoretic-Based Approach for Personalized Security, Recommendation in 5G Beyond IoT Environments for Consumer Electronics
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
编号：198
题名：CoopGBFS: A Federated Learning and Game-Theoretic-Based Approach for Personalized Security, Recommendation in 5G Beyond IoT Environments for Consumer Electronics
年份：2023
DOI：10.1109/tce.2023.3305508
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2023.3305508.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：联邦学习、隐私保护与分布式协同
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\198.txt
- 原始字符数：42488
- 本次发送字符数：42488
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2648

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

CoopGBFS: A Federated Learning and
Game-Theoretic-Based Approach for Personalized
Security, Recommendation in 5G Beyond IoT
Environments for Consumer Electronics
Muhammad Shafiq , Senior Member, IEEE, Rahul Yadav,
Abdul Rehman Javed , Graduate Student Member, IEEE, and Syed Agha Hussnain Mohsan

Abstract—In 5G IoT for consumer electronics security
recommendation systems, Machine Learning (ML) based
Federated Learning (FL) methods plays an important for the
detection of cyberattacks. For this objective, several different models for effective feature selection and recommendation
systems are presented in the literature. However, presented models prone to misclassify 5G Internet of Things (IoT) malicious
traffic due to inappropriate feature recommendation system. To
address the issue, In this paper, firstly, an Automatic Data set
Generator (ADG) method is proposed and then designed ADG
algorithm for the effective features set dataset. Then based on
proposed ADG algorithm we proposed a new recommendation
model CoopGBFS, based on cooperative game theory, federated
learning and correlations with algorithm accuracy to address the
problem. Finally, based on proposed CoopGBFS method an algorithm named CoopGBFS is developed and designed to select and
recommend effective features set for 5G IoT network security.
For the proposed approach evaluation, Bot-IoT dataset and four
well-known ML algorithms are utilized. However, from the result
analysis, it is cleared that the presented method is efficient for
5G IoT malicious traffic detection features recommendation for
Consumer Electronics.
Index Terms—CoopGBFS, recommendation system, 5G
IoT network, cyberattacks detection, federated learning, for
consumer electronics.

I. I NTRODUCTION

R

ECENTLY, 5G IoT technology received much
importance, specially in Consumer Electronics, and

Manuscript received 30 April 2023; revised 20 July 2023; accepted
12 August 2023. Date of publication 15 August 2023; date of current version
26 April 2024. This work was supported by the National Natural Science
Foundation of China under Grant 62250410365. (Corresponding author:
Muhammad Shafiq.)
Muhammad Shafiq is with the Department of Cyberspace Institute of
Advanced Technology, Guangzhou University, Guangzhou 510006, China
(e-mail: srsshafiq@gmail.com).
Rahul Yadav is with the College of Computer Science and Technology,
Harbin Engineering University, Harbin 150009, China (e-mail: rahul@
hrbeu.edu.cn).
Abdul Rehman Javed is with the Department of Electrical and Computer
Engineering, Lebanese American University, Byblos 1102 2801, Lebanon
(e-mail: abdulrehmanjaved@ieee.org).
Syed Agha Hussnain Mohsan is with the Optical Communications
Laboratory, Ocean College, Zhejiang University, Zhoushan 316021, China
(e-mail: hassnainagha@zju.edu.cn).
Digital Object Identifier 10.1109/TCE.2023.3305508

its growth is increasing every minute due to its efficient
performance results. Moreover, by introducing this technology,
life becomes very comfortable due to easy accessibility. In
the initial stage of IoT technology Consumer Electronics, the
administrator can only install it in small offices and homes,
then gradually, this technology extended and grew up very
rapidly. Then to save time and control everything efficiently,
the technology is integrated into industries for more reliability.
Now the result is that IoT in consumer electronics has become
a very important part of our life [1]. At the end of this year,
the interconnected IoT network consumer electronics will
be expected 27.1 billion, which is expected that globally,
3.5 IoT consumer electronics devices per person. However,
this is a profound change in IoT consumer electronics
technology. It is fascinating that this technology is expending
very fast, but due to this development, cyber-attacks are
also gaining popularity and becoming an emerging issue.
Nevertheless, to overcome cyber-attacks problems and protect
their personal information and unauthorized access, several
researchers in the research community endeavor hard and
present several different efficient models. However, for this
purpose, the researchers try and present effective Machine
Learning (ML) based cybersecurity systems models on
overcoming rising cyber-attacks issues in 5G IoT network
security [2], [3].
In 2017, Denial of Service (DDoS) malicious attacks
became the most spreading and growing attacks and got
much attention [4]. Similarly, in a report issued by Kaspersky
Lab, the cyber-attacks in IoT networks in 2017 is much
increased compared to cyber-attacks in 2013. However, most
attacks were in 2017 are DDoS and Botnet attacks, which
is very harmful compared to other cyber-attacks. However,
to overcome these attacks, an effective intrusion detection
system is necessary to develop. For this reason, to address
the above problem, Anderson 1980 design and presented the
first Intrusion Detection System (IDS) [5]. Similarly, in 1987,
D. E. Denning introduces a new intrusion detection model
capable of detecting harmful intrusion. However, their model
is based on a hypothesis and real-time intrusion detection, the
primary purpose of his proposed system is identifying malicious traffic. Nonetheless, recently the most rising security

c 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1558-4127 
See https://www.ieee.org/publications/rights/index.html for more information.

SHAFIQ et al.: CoopGBFS: A FL AND GAME-THEORETIC-BASED APPROACH FOR PERSONALIZED SECURITY

attacks are man-in-the-middle harmful threats with (DDoS)
attacks [6], [7]
Recently, in our previous work [3], [8], we studied and
addressed the problem of effective feature selection and
presented numerous effective feature selection approaches.
Furthermore, we used well-known machine learning (ML)
algorithms to overcome feature selection and identify cyberattack traffic flows. However, in our studies, we showed that
selection of more features could lead to computational complexity and affect the performance of the proposed approach
or accuracy results. For instance, the selection of more than
ten feature sets can slow the presented model or slow the
ML algorithms process. Hence, the selection of efficient features for the identification of malicious attack traffic in 5G IoT
consumer electronics network environments using machine
learning algorithms and the federated learning technique is
a crucial and emerging issue [9].
To overcome the problem of effective feature selection and
recommendation for identifying cyber-attacks in IoT networks,
in this paper, we proposed a new framework and algorithms
by using well-known machine learning algorithms and an
open-access dataset in order to achieve improved performance
outcomes. Nonetheless, the key contributions are discussed in
the paper are:
• To tickle the issues associated with feature selection
and security recommendation system problems in 5G
IoT network for consumer electronics malicious traffic
flow. In this manuscript, we introduce a novel framework
model named CoopGBFS based on cooperative game theory to accurately deal with the above problem and achieve
promising performance results.
• Then based on the proposed method, correlations with
algorithm accuracy are applied to address the problem
accurately. Firstly, a novel feature ranking method correlation is applied for the ranking of features, and then
based on correlation, an algorithm is applied in order
to achieve improved performance outcomes in 5G IoT
networks.
• Subsequently, the cooperative Shapley value is employed
by leveraging cooperative game theory. A considerable
number of scholars within the academic research community have employed game theory as a means to address
decision-making challenges, yielding highly favourable
outcomes. Therefore, cooperative game theory was also
employed to rank the features in the context of detecting
cyber-attacks in the 5G IoT network, utilising machine
learning algorithms.
• Afterwards, leveraging the cooperative shapely value of
game theory and correlation, researchers have devised
an algorithm called CoopGBFS. This algorithm aims to
effectively determine the optimal feature set for identifying IoT network traffic. The algorithm being proposed
is based on the wrapper technique, which is employed
to prioritise the most effective feature. This technique
offers an adequate quantity of data for the detection of
malicious network traffic within the framework of the
Internet of Things (IoT). The methodology proposed in
this study entails the utilisation of the Bot-IoT dataset and

2649

the evaluation of four well-established machine learning
algorithms.
• In the end, we reached a conclusion and subsequently
presented a set of promising features that possess sufficient information to effectively detect cyber-attacks in
IoT consumer electronics network environments. These
features were identified using a technique grounded in
cooperative game theory. Based on the examination of
the empirical findings, it is evident that the chosen set
of features possesses discriminative capability and contains sufficient information to effectively detect instances
of cyber-attacks within IoT networks.
The paper is structured into the subsequent sections: The subsequent section provides an introduction to the works that
have been reviewed. Next, the present study is exemplified in
Section III. Section IV delves into the discourse surrounding
the evaluation methods. Section IV of the document delves into
the examination and evaluation of the subject matter, encompassing both discourse and analysis. Section V encompasses
the presentation of the conclusion and future work.

II. R ELATED W ORKS
This section aims to examine and highlight the existing literature on the detection of cyber-attacks or malicious traffic
flow in the network environment of IoT consumer electronics. In our previous research conducted in [3], we presented
several different effective models for effective feature selection
and effective network traffic detection, such as IM flow classification and malicious Bot-IoT attacks detection. Nonetheless,
it is proved in several studies that feature selection is an fundamental step of ML [10]. The primary objective of efficient
feature selection is to identify a set of features that possess
discriminative capabilities in detecting cyber-attacks, while
simultaneously eliminating redundant features from a larger
pool for utilisation in machine learning algorithms. Although
redundant features are a sign of features that are insufficiently informative for the detection of cyber-attacks in IoT
consumer electronics network environments, they are also a
sign of features that are failing to meet the needs of the IoT
industry. In order to address the challenge of efficient feature
selection, numerous researchers have made significant efforts
and put forth effective models, such as: in 2018 Egea et al.
in [11] studied and reviewed several proposed effective feature selection techniques. The techniques that they reviewed
in their studies are based on correlation measurement. Based
on the reviews technique, they introduced a new technique
called Fast Based Correlation Features (FCBF) to enhance the
performance and select effective features in the industrial environment. After that, the researchers made a modification to the
initially proposed technique, which resulted in the introduction
of the FCBFiP technique. Similarly, Meidan et al. (2018) [12]
conducted a study on the detection of cyber-attacks in the
context of IoT networks. Their research focused on the identification of malicious attacks in 5G IoT networks that originate
from IoT devices. In their study, they empirically evaluate their
proposed adversarial cyber-attack detection method.

2650

Fig. 1.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Fig. 2.

Real Time Detector in 5G Based IoT Network.

Fig. 3.

Proposed CoopGBFS Recommendation Model.

Proposed Dataset Generator Algorithm (DGA).

Similarly, several models in the research community
presented many effective ML models for the identification
and performance improvement and achieved effective results.
Thus, from the above reviews related to robust feature for
IoT traffic identification, It is evident that this topic can be
thoroughly investigated, wherein effective features can be chosen to sufficiently convey information for the detection of
detrimental environmental flows.
The proposed algorithm that generate data set for the
proposed model is shown in Fig. 1 in detail. The 5G IoT
Network and detection method is shown in Fig. 2 in details.
While proposed framework is shown in Fig. 3
III. P ROPOSED C OOP GBFS M ETHOD
In this particular section, the presented framework
CoopGBFS explains and tries to demonstrate the step-by-step
process in detail to overcome the issue related to the selection of features for cyber-attacks 5G Internet of Things traffic
identification in 5G IoT consumer electronics [13] network
environments as shown in Fig. 3 The essential part of the feature selection process is to rank effective features that have
more information for the harmful identification and remove
a redundant feature. In order to achieve this objective, we
initially employed a novel correlation technique to prioritise

the influential features and eliminate the superfluous features
from the trace traffic dataset. Once the process of ranking and
selecting the optimal feature set has been completed, a widely
recognised algorithm is employed to determine the feature
that provides the most informative content for the identification of malicious traffic. Then, based on the above-explained
technique, the redundant features are removed, and effective
features are selected. The primary purpose of applying the
algorithm is to remove unwanted features that are not applicable or don’t have discriminative power to identify malicious
attacks in 5G IoT consumer electronics network environment.
Nevertheless, the utilisation of cooperative Shapley values
has proven to be effective for the purpose of selection. In conclusion, the CoopGBFS algorithm is introduced as a means to
determine a proficient set of features for the classification of
network traffic in 5G IoT, utilising the cooperative Shapley
value. The algorithm under consideration relies on the filter
method to prioritise the efficient features that possess significant potential for identifying traffic in the context of 5G

SHAFIQ et al.: CoopGBFS: A FL AND GAME-THEORETIC-BASED APPROACH FOR PERSONALIZED SECURITY

network. The methodology proposed in this study entails the
utilisation of the Bot-IoT dataset and the evaluation of four
well-established machine learning algorithms. Nevertheless,
the examination of the empirical findings illustrates that the
suggested methodology proves to be efficacious in the detection of malevolent network activity within the realm of 5G
Internet of Things (IoT). In order to facilitate comprehension
and provide a systematic approach, the subsequent section
elucidates the comprehensive methodology of the proposed
framework.
A. Feature Selection
This section introduced the applied metrics are discussed
in detail. The detailed metrics are discussed in the following
subsection.
1) Correlations Based Metric: In this subsection, we
applied the Person Moment Correlation method to solve the
effective feature selection problem or rank the most effective
features in the 5G IoT consumer electronics network environment. To remove redundant features and rank effective
features correlation technique is the best choice. The technique
is useful for the identification of the relationship between features and target features in a dataset. In 1889, R. E. Fancher
proposed this technique [14]. After sixteen years, researcher K
Pearson updated the technique with the name Person Product
Moment Correlation. However, the main purpose of updating this technique is to identify the relationship among class
attributes or features. The updated technique is based on statistical analysis, which ranks attributes of a class. Here attributes
indicate the features of the class. For instance, let A and B
features, then to find out the correlation between A and B, the
following formula can be used.
Covariance(A, B)
(1)
CX,Y =
σx σy


n
i=1 (ai − a) bi − b

(2)
C= 

2
n
2 n
b
−
a)
−
b
(a
i
i
i=1
i=1
In equation (1), CA, B indicates the relationship among
attributes or simply the correlation coefficient, While covariance is (A, B). Whereas ab indicates the standard deviation
for features A and B. However, the above explanation is for
a simple correlation relationship, while Eq. (2). can be used
for two set attributes correlation coefficient evaluation. For the
two sets of attributes correlations coefficient, we used Eq. (2).
For instance, if A and B are sets of features, then a1, b2, c3,
then the correlation among features is very strong. Likewise,
if the value of the C coefficient is minus one (−1), the correlation between features is weak, not strong. While if there is
zero value of C, then there is no relationship between features
of classes. Thus, it is clear from the explanation of the correlation coefficient that this technique is useful for the feature
selection and ranking in the high dimensional dataset. Thus,
the effectiveness of the feature of classes can be analyzed by
using Eq. (3) as follows:


kavg corrfc
(3)
Corr = 


k + k(k − 1)avg corrff

2651

In Eq. (3), Corr indicates the correlation coefficient of the final
value and the relationship between features of classes. At the
same time, Kavg(corrfc) is the average of correlations of features. Similarly, K indicates the number of features set and
while Avg(corrff) refers to average relationships among class
features. As discussed in the previous section that applying the
correlation coefficient technique is essential for effective feature selection. However, here are some factors before using the
correlation coefficient technique for the effective feature selection for malicious IoT network traffic flow identification using
the machine learning method. If the correlation between features is strong and the correlation coefficient between features
and classes is week, then it’s mean the correlation is week.
Likewise, if the correlation between the feature and classes is
strong, then it’s known as strong correlations.
2) Accuracy (ACC) Wrapper Based Metric: As discussed
in the previous subsection, the most critical part of the identification process is selecting effective IoT malicious traffic
identification features. Unfortunately, it is challenging for a
network administrator to determine the outmost feature for
Machine Learning (ML) classifiers. To overcome this problem,
we used the wrapper technique based on algorithm accuracy
(ACC). The accuracy (ACC) wrapper technique effectively
ranks effective features when there is a high-dimensional
dataset. As we are interested in ranking, the feature gives
enough information to identify cyber-attacks traffics in IoT
networks. Thus we adopted the accuracy (ACC) wrapper technique for this study. The highest values of the ACC metric
indicate the feature is robust and could achieve effective
performance results. On the other hand, if the ACC metric value is not high, then the classification performance
results will not be effective. Thus, applying the ACC wrapperbased metric is vital for ranking features in order to achieve
improved performance outcomes in IoT network malicious
traffic identification using ML algorithms.
3) Cooperative Game Theory: Game theory is a branch
of mathematics and is widely applied in the economic field
due to better performance results [15]. Due to game theory,
a competitive situation can be understood in which decisionmakers interact. Therefore, game theory has been applied in
many areas such as economics, war, computer science, and
business [16]. However, recently game theory has become
scorching top in the field of computer science. In cooperative
game theory, the main and most necessary part is the coalition. “Coalitions are the set of players as N = 1,2,3, . . . , n
and the coalition is a subset of players, N used for a binding
agreement. Similarly, any subset of N, including N itself, can
form a coalition [17]. More in-depth, a coalition game is a
pair of (N, V), where N is a finite set of players, indexed by
I:2. . . .n arrow R associate with each coalition K subset N a
real-valued payoff v(k) satisfying v(0) = 0”.
Recently in game theory, Shapley’s value got much attention, specifically in computer science. Shapley first introduced
the Shapley value. Then, due to its promising results for coalitions in game theory, the technique got much attention and
adopted. The cooperative Shapley value is very effective for
the ranking problem. This paper adopted cooperative Shapley
value in game theory to overcome effective features selection

2652

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

cyber-attacks traffic in IoT consumer electronics network environment. In cooperative game theory [18], we need players and
coalitions as:
N = {1, . . . , .n}

(4)

Colitions = S ⊆ N

(5)

and

Then we need a characteristic functions. Actually the characteristics function game G by a pair (N,V), Where,
V : 2N −→ IR

(6)

Here Eq. (6) is the characteristics function which maps each
coalitions S⊆ N real number V(S). Then we can assume pair
distribution as: 1. Efficiency, 2. Null Players, 3. Symmetry
and 4. Additivity Then the cooperative shapely value will be
G = (N,V), the shapely value of a player i ∈ N is given by
1  G
 (i)
(7)
φi (G) =
|N|!
π ∈N

The main objective of cooperative Shapley value is to measure the distribution of the power. In simple words, it is
used to measure the voting game player’s distribution. We
can adopt cooperative Shapley value and rank and effective
weight features in our proposed technique through this base.
The cooperative Shapley value is very effective and efficient
to find out the feature importance when several features for
identification attack traffic. However, we also adopted this
technique in this paper for effective selection and recommendation by using Shapley value as discussed in the following
with a detailed explanation. The Cooperative Shapley value
can be denoted by (φi (v)),

|k|!(n − |k| − 1)!
i (k)x
φi (v) =
(8)
k!

Fig. 4.

Coalition 1.

Fig. 5.

Proposed CoopGBFS Algorithm A.

k⊂N

Similarly, in the Eq. (9) n is the number of players and sum
over all subset K of N, where there no player i.
i (k) = v(k ∪ i) − v(k)
Likewise, Eq. (6) represent ψ(ij)





ψ(ij) = 1, I fj ; class|fi > I fj ; class 0





1, I fj ; class|fi > I fj ; class
ψ(ij) =
2, else

(9)

(10)
(11)

Similarly, to redefine the above equation definitions as


|k|
1, I(k; class; fi ) ≥ 0 and
fj ∈k ψ(ij) ≥
(k) =
2 (12)
0, else
However, the Coalitions of each players for each features
are shown in Fig. 4.
Then the final result of shapley value are shown in Fig. 7.
B. Proposed Algorithm
This section presents our proposed effective feature selection technique named CoopGBFS to identify harmful traffic.

1) CoopGBFS Algorithm: In this subsection, we explained
the proposed CoopGBFS algorithm-based cooperative game
theory. The objective of the proposed algorithm is to select
effective features for the identification of malicious attacks in
IoT networks using a machine learning algorithm, as shown in
Fig. 5 and 6. For the better understanding the proposed algorithm his two part “A” and “B” As discussed in the previous
section, the proposed algorithm objective is to select the best
features set from the given several features. For this objective, the proposed algorithm is divided into three phases, as
shown in Fig. 8. In the first phase, the features set is supplied,

SHAFIQ et al.: CoopGBFS: A FL AND GAME-THEORETIC-BASED APPROACH FOR PERSONALIZED SECURITY

2653

not high enough, then the algorithm control transfer to remove
otherwise forward to Swrapper step.
Let  be the dataset, and let  be the set of input features.
We begin by loading the dataset  and initializing :
 = load_dataset()

(13)

 = input_featuress et()

(14)

We then enter a loop to iteratively select a subset of features:
while_true_do

(15)

Within each iteration of the loop, we first calculate the
number of features in the current set :
ν = count_features()

(16)

We then calculate the weight accuracy of each feature in 
with respect to the dataset :
ω = calculate_weight_accuracy(, )
Fig. 6.

Proposed CoopGBFS Algorithm B.

Using the weights ω, we compute the Shapley value of each
feature, taking into account the cooperative effect of features
in :
= calculate_coalition(ω)
φ = apply_cooperative_shapley_value( )

Fig. 7.

Cooperative Shapley Values.

Confusion Matrix.

and then it counted to calculate the number of features is
available. After calculation, the weight accuracy is calculated.
Here, accuracy is calculated after applying the correlation
coefficient technique, and the weight is indicated the accuracy of a feature. After calculating accuracy, the algorithm
transfer control to the second phase, in which the coalition
of counted accuracy feature is calculated. As discussed in the
previous section, coalitions are essential in cooperative game
theory, especially in the cooperative Shapley value technique.
Then cooperative Shapley value is applied based on coalition
values of features. Finally, in the third phase, the wrapper technique is used based on the cooperative Shapley value to rank
the best feature for the identification of malicious attacks in
IoT consumer electronics network environments. The proposed
algorithm will select effective features and remove the redundant features. Similarly, if the values of selected features are

(18)
(19)

We then apply a wrapper technique to select a subset of
features ρ from the original set :
ρ= wrapper_technique() ρ=wrapper_technique( ). We
select the most effective features from ρ:
φ=select_effective_features(ρ). If the selected features in
meet some criterion, we display the results and terminate the algorithm: if check_selected_features( ) then
display_results( ) return end if. If the selected features do not
meet the criterion, we remove the unselected features from ρ
to obtain a new set of input features ρ :
ρ = remove_unselected_features( )

Fig. 8.

(17)

(20)

If ρ is empty, we display the current selected features and
terminate the algorithm: If ρ is empty then display_results( )
then return and end if statements. Finally, we update  with
ρ and continue to the next iteration: =ρ end while =ρ
statement.
IV. E VALUATION M ETHODOLOGY
In this section, the detailed evaluation methodology is
discussed, and the dataset used to evaluate our proposed technique is examined as follows subsection. Firstly, the dataset is
discussed, and then later performance evaluation metrics are
discussed.
2) Data Set: This subsection includes the dataset that is
conducted for this study. For this objective, a Bot-IoT dataset
is utilized for the proposed approach evaluation. In 2018,
Koroniotis et al. [17] and Van der Elzen et al. [19] developed
the Bot-IoT dataset to identify Bot-IoT malicious traffic flow
in IoT networks. However, the dataset that was produced comprises IoT traffic, Bot-IoT traffic, regular traffic, and several
attack traffic types that are frequently utilised in botnet assaults

2654

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

in IoT networks. Furthermore, the realistic testbed, which
includes a labelled feature set, is used for accurate trace development. They initially extracted a small collection of features
for the machine learning technique’s successful performance
outcomes, but later expanded and included more features for
the precise classification of Bot-IoT traffic flow. Attacks traffic, categories, and subcategories, among other things, were
labelled. They divided the Internet of Things testbed into
three sections, including features extraction, network platform,
and forensics analytics. They integrated five IoT devices for
the IoT data in more detail. For instance, an IoT device
that generates weather data, such as the current temperature,
humidity, air pressure, etc., is utilised to provide weather
information. In a similar vein, the second Internet of Things
(IoT) gadget they employed for their research is an IoT-based
refrigerator that automatically generates data on the interior temperature and regulates the temperature. Pseudorandom
general signal-based lights are the third special IoT gadget
that they used for their research. These lights work off of
movement. Based on motion, the smart bulb turns on automatically when there is movement, and it stays off when
there is no movement. The smart IoT door is the fourth one,
and the smart thermostat is the fifth. This gadget is used to
automatically manage and regulate the indoor temperature of
the house.
3) Performance Measurement: For the identification of
performance analysis of the proposed model, performance
analysis is essential. For this objective, numerous researchers
in the research community applied confusion metrics, particularly for machine learning (ML) model performance measurement. Therefore, confusion metrics are the critical metrics
for the performance measurement and based on confusion
metrics. In this paper, we also adopted this technique to
find out the performance analysis of our proposed method.
The graphical representation of confusion metrics is shown
in Fig. 8. However, the graph includes rows and columns.
Rows represent the class samples, and column represents
the classified samples of a class. The most important and
widely used confusion metrics that numerous researchers used
for their proposed technique performance evaluation are discussed below in detail. For our proposed model performance
evaluation, we adopted the following confusion metrics as
follows:
The above showing metrics in the figure are widely applied
for the ML model performance measurement. Based on the
above-explained metrics, several different metrics can be made
for better performance analysis. It is significant to note that
effective machine learning (ML) classifiers always minimize
the FP metrics value and FN metrics values for effective
performance results. However, the metrics that we selected
for this study are explained below:
• Accuracy (ACC): In cyber-attack identification or detection, the accuracy metric is the samples that are correctly
identified in overall classified samples. However, the
detailed explanation of the accuracy can be defined
mathematically below. Therefore, we adopted this accuracy metric for our proposed model to measure the
performance of the model. Furthermore, using this metric

effectiveness of the proposed model can be easily
identified.
(TP + TN)
(21)
Accuracy =
(TP + TN + FP + FN)
• Precision: the precision metric can be defined as Class
X correctly classified sample traffic in all those classified
in Class X. In a simple way, the true positive metrics
divide by true positive and false positive. The mathematical equation that we used for this study is shown
below.
TP
(22)
Precission =
(TP + FP)
• Sensitivity: This metric can be defined as the correctly
identified sample divide by the overall sample. This metric is also known as the recall metric. The mathematical
equation that we used in this study is given below.
TP
(23)
Sensitivity =
(TP + FN)
• Specificity: This metric is a very simple metric that several researchers use for their performance analysis. This
metric indicates that a metric that can identify the negative results is called specificity metric. The mathematical
equation is given below.
TN
(24)
Specificity =
(FP + TN)
Therefore, we applied the above-discussed metrics for our
proposed model performance measurements. The detailed
results analysis of the proposed model is presented in the next
section.
A. Results and Analysis
This section covered the in-depth findings and analysis of
our suggested method, CoopGBFS, for selecting appropriate
features to detect cyberattack traffic flows in IoT consumer
electronics network environments. to use machine learning
(ML) techniques to solve the issue of effective feature selection and determine which feature has discriminative capacity
to appropriately identify cyber-attacks traffic in IoT networks.
In order to identify cyberattack traffic in the IoT network, we
presented the efficient feature selection method CoopGBFS
and efficiently picked five different features. Four well-known
machine learning (ML) algorithms Support Vector Machine
(SVM), Decision Tree (C4.5), Naive Bayes, and Random
Forest (RF) are used for the proposed technique, which makes
use of the CoopGBFS assessment Bot-IoT dataset. With the
help of the useful features set suggested by our feature selection approach and the corresponding performance assessment
metrics of accuracy, precision, sensitivity, and specificity metrics, the four applied ML algorithms show promising results
for identifying cyber-attacks in IoT networks. However, the
outcomes of all used ML algorithms are promising. Similar to
this, using the chosen feature set, the decision tree (C4.5) algorithm produces high accuracy results for detecting cyberattacks
in IoT networks.
Likewise, Random Forest and Naïve Bayes accuracy results
are also very effective using selected features. However, the

SHAFIQ et al.: CoopGBFS: A FL AND GAME-THEORETIC-BASED APPROACH FOR PERSONALIZED SECURITY

Fig. 9.

2655

Fig. 10.

Precision Results.

Fig. 11.

Sensitivity Results.

Accuracy Results.

Random Forest ML algorithm is very effective compared to
the Naïve Bayes algorithms accuracy result. Similarly, all the
traffic flows are effectively identified using selected features.
However, OSFpnger and SSR traffic are a bit slow identified
compared to other flow traffic of IoT networks. But overall
identification accuracy is very promising using ML algorithms
and selected feature sets, as shown in Fig. 9. However, all the
attacks and normal traffic flows are accurately classified, but
only OSFpinger are a bit slow classified compared to other
traffic flows, as shown in Fig. 9.
Similarly, in Fig. 10, the precision results of the applied
ML algorithms are shown. The figure shows that UDPDDoS
attacks and Normal traffics are effectively identified compared
to other traffic flows. But it is also clear that SSR is a bit
slow identified than UDPDDoS and Normal traffic flows with
respective precision metrics. However, the SVM algorithm
performance result using selected features set for precision is
not very promising compared to other applied ML algorithms.
But it is also seen that the SVM algorithms performance results
are very promising for Normal and UDPDDoS attacks, respectively 99% and 100%. However, the lowest precision result that
the SVM gives is OSFpinger traffic flow. Naïve Bayes algorithm performance results are also very effective. However, for
Data theft and Keylogging Theft attacks, Its performance result
is not effective compared to other traffic flows. Though, the
overall precision results for the identification of cyber-attacks
are effective. But decision tree (C4.5) ML algorithm gives
a promising performance result compared to other machine
learning algorithms, as shown in Fig. 10.
Likewise, the SVM algorithms give very poor sensitivity
results for sensitivity results compared to other ML algorithms,
as shown in Fig. 11. But on another side, the SVM algorithm
gives very effective sensitivity results for UDPDDoS and SSR
attacks traffic flows. However, the overall sensitivity results of
SVM are not effective compared to other ML algorithms. In
IoT consumer electronics network contexts, the decision tree
C4.5 and Random Forest machine learning algorithms provide effective sensitivity results for identifying cyber-attacks.
In contrast to other network flows, UDPDDoS, TCPDDoD,
and SSR assaults traffic is properly segmented. On the other
hand, as shown in Fig. 11, sensitivity results for detecting

cyber-attacks in the IoT consumer electronics network environment are effective in comparison. Similarly, the specificity
findings of the used ML algorithms are shown in Fig. 12 Once
more, the figure demonstrates that each ML method achieves
distinct performance results that are effective. Even while the
results of all applied ML algorithms are encouraging, the decision tree C4.5 ML algorithm produces the most encouraging
outcomes when compared to other applied ML algorithms in
terms of specificity metrics. In-depth classification of IoT technology traffic flows includes both attacks and regular traffic.
SSR attacks, however, are yielding somewhat subpar findings
in comparison to other traffic flow classification outcomes.
Finally, Fig. 12 refSpecificity Results shows that our suggested
approach successfully chooses robust features for detecting
cyber-attacks in IoT networks.
V. C ONCLUSION
To address security recommendation problem for cyberattacks detection in the 5G IoT consumer electronics network
using ML algorithms with federated learning dateset. A new
framework model named CoopGBFS based on cooperative
game theory and correlations with algorithm accuracy is
proposed. Firstly, an Automatic Data set Generator (ADG)
method is proposed and then based on proposed method
an algorithm named ADG is designed and developed for
the effective features set data set. Then based on proposed

2656

Fig. 12.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Specificity Results.

ADG algorithm we proposed a new recommendation model
CoopGBFS, based on cooperative game theory, federated
learning and correlations with algorithm accuracy to address
the problem. Finally, based on proposed CoopGBFS method
an algorithm named CoopGBFS is developed and designed
to select and recommend effective features set for 5G IoT
network security. Based on the analysis of the experimental
results, it is apparent that the proposed methodology is effective in detecting and recommending a set of features that are
capable of effectively identifying cyber-attack traffic in 5G IoT
networks. The proposed model demonstrates a higher level of
depth and effectiveness, as it incorporates carefully selected
features. The chosen features demonstrate efficacy and provide sufficient information for the detection of cyber-attacks.
Likewise, all of the machine learning algorithms employed
in the study yielded encouraging outcomes in the realm of
cyber-attack detection.
R EFERENCES
[1] L. Teng et al., “FLPK-BiSeNet: Federated learning based on priori
knowledge and bilateral segmentation network for image edge extraction,” IEEE Trans. Netw. Service Manag., vol. 20, no. 2, pp. 1529–1542,
Jun. 2023.
[2] M. Bibi et al., “A novel unsupervised ensemble framework using
concept-based linguistic methods and machine learning for twitter sentiment analysis,” Pattern Recognit. Lett., vol. 158, pp. 80–86, Jun. 2022.

[3] M. Shafiq, X. Yu, A. K. Bashir, H. N. Chaudhry, and D. Wang,
“A machine learning approach for feature selection traffic classification using security analysis,” J. Supercomput., vol. 74, no. 10,
pp. 4867–4892, 2018.
[4] Kaspersky. “Amount of malware targeting smart devices more than
doubled in 2017.” 2021. [Online]. Available: https://www.kaspersky.
com/
[5] J. P. Anderson. “Computer security threat monitoring and surveillance.” 1980. Accessed: Nov. 30, 2008. [Online]. Available:
https://seclab.cs.ucdavis.edu/projects/history/papers/ande80.pdf
[6] X. Du, M. Guizani, Y. Xiao, and H.-H. Chen, “Defending DoS attacks
on broadcast authentication in wireless sensor networks,” in Proc. IEEE
Int. Conf. Commun., 2008, pp. 1653–1657.
[7] L. Wu, X. Du, W. Wang, and B. Lin, “An out-of-band authentication
scheme for Internet of Things using blockchain technology,” in Proc.
Int. Conf. Comput. Netw. Commun. (ICNC), 2018, pp. 769–773.
[8] M. Shafiq, X. Yu, A. A. Laghari, and D. Wang, “Effective feature selection for 5G IM applications traffic classification,” Mobile Inf. Syst.,
vol. 2017, May 2017, Art. no. 6805056.
[9] H. Yuan, W. Morningstar, L. Ning, and K. Singhal, “What do we mean
by generalization in federated learning?” 2021, arXiv:2110.14216.
[10] R. Yadav, I. Sreedevi, and D. Gupta, “Augmentation in performance
and security of WSNs for IoT applications using feature selection and
classification techniques,” Alexandria Eng. J., vol. 65, pp. 461–473,
Feb. 2023.
[11] S. Egea, A. R. Mañez, B. Carro, A. Sánchez-Esguevillas, and J. Lloret,
“Intelligent IoT traffic classification using novel search strategy for fastbased-correlation feature selection in industrial environments,” IEEE
Internet Things J., vol. 5, no. 3, pp. 1616–1624, Jun. 2018.
[12] Y. Meidan et al., “N-BaIoT—Network-based detection of IoT botnet
attacks using deep autoencoders,” IEEE Pervasive Comput., vol. 17,
no. 3, pp. 12–22, Jul.–Sep. 2018.
[13] R. Barbado, O. Araque, and C. A. Iglesias, “A framework for fake review
detection in online consumer electronics retailers,” Inf. Process. Manag.,
vol. 56, no. 4, pp. 1234–1244, 2019.
[14] R. E. Fancher, “Galton on examinations: An unpublished step in
the invention of correlation,” ISIS, vol. 80, no. 3, pp. 446–455,
1989.
[15] J. Chen and Q. Zhu, “Background of game theory and network science,”
in A Game-And Decision-Theoretic Approach to Resilient Interdependent
Network Analysis and Design. Cham, Switzerland: Springer, 2020,
pp. 5–11.
[16] V.-H. Bui, A. Hussain, and W. Su, “A dynamic internal trading price
strategy for networked microgrids: A deep reinforcement learning-based
game-theoretic approach,” IEEE Trans. Smart Grid, vol. 13, no. 5,
pp. 3408–3421, Sep. 2022.
[17] N. Koroniotis, N. Moustafa, E. Sitnikova, and B. Turnbull, “Towards
the development of realistic botnet dataset in the Internet of Things for
network forensic analytics: Bot-IoT dataset,” 2018, arXiv:1811.00701.
[18] C. Contreras, A. Triviño, and J. A. Aguado, “A game-theoretic approach
for the effective distributed coordination of STATCOMs,” IEEE Access,
vol. 11, pp. 27730–27738, 2023.
[19] I. Van der Elzen and J. van Heugten, Techniques for Detecting
Compromised IoT Devices, Univ. Amsterdam, Amsterdam,
The Netherlands, 2017.
PAPER_TEXT
