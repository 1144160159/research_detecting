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
# [207] Detecting Intentional AIS Shutdown in Open Sea Maritime Surveillance Using Self-Supervised Deep Learning
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
编号：207
题名：Detecting Intentional AIS Shutdown in Open Sea Maritime Surveillance Using Self-Supervised Deep Learning
年份：2023
DOI：10.1109/tits.2023.3322690
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2023.3322690.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：多媒体、医学、遥感与视频异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\207.txt
- 原始字符数：65607
- 本次发送字符数：65607
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1166

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 2, FEBRUARY 2024

Detecting Intentional AIS Shutdown in Open
Sea Maritime Surveillance Using
Self-Supervised Deep Learning
Pierre Bernabé , Arnaud Gotlieb, Bruno Legeard, Dusica Marijan ,
Frank Olaf Sem-Jacobsen, and Helge Spieker

Abstract— In maritime traffic surveillance, detecting illegal
activities, such as illegal fishing or transshipment of illicit
products is a crucial task of the coastal administration. In the
open sea, one has to rely on Automatic Identification System
(AIS) message transmitted by on-board transponders, which are
captured by surveillance satellites. However, insincere vessels
often intentionally shut down their AIS transponders to hide
illegal activities. In the open sea, it is very challenging to
differentiate intentional AIS shutdowns from missing reception
due to protocol limitations, bad weather conditions or restricting
satellite positions. This paper presents a novel approach for
the detection of abnormal AIS missing reception based on
self-supervised deep learning techniques and transformer models.
Using historical data, the trained model predicts if a message
should be received in the upcoming minute or not. Afterwards,
the model reports on detected anomalies by comparing the
prediction with what actually happens. Our method can process
AIS messages in real-time, in particular, more than 500 Millions
AIS messages per month, corresponding to the trajectories of
more than 60 000 ships. The method is evaluated on 1-year
of real-world data coming from four Norwegian surveillance
satellites. Using related research results, we validated our method
by rediscovering already detected intentional AIS shutdowns.
Index Terms— Automatic identification systems (AISs), maritime surveillance, self-supervised machine learning, transformer
models, AIS shutdown, anomaly detection.

I. I NTRODUCTION

V

ESSEL Traffic Service (VTS) aims at monitoring and
controlling the activities of vessels in dedicated maritime
areas. The general objectives of VTS include identifying and
guiding ships, helping vessels to prevent collisions, launching
Manuscript received 15 September 2021; revised 22 February 2022,
28 June 2022, 6 November 2022, and 25 February 2023; accepted 7 September
2023. Date of publication 17 October 2023; date of current version 2 February
2024. This work was supported in part by the Norwegian Research Council
(RCN) TSAR Project [Experimental Infrastructure to Explore Exascale Calculus (eX3)] under Contract 287893 and Contract 270053. The Associate Editor
for this article was B. Singh. (Corresponding author: Pierre Bernabé.)
Pierre Bernabé is with the Simula Research Laboratory, 0164 Oslo,
Norway, and also with the Institut FEMTO-ST, Université de Bourgogne
Franche-Comté, 25030 Besançon, France (e-mail: pierbernabe@simula.no).
Arnaud Gotlieb, Dusica Marijan, and Helge Spieker are with the Simula
Research Laboratory, 0164 Oslo, Norway (e-mail: arnaud@simula.no;
dusica@simula.no; helge@simula.no).
Bruno Legeard is with the Institut FEMTO-ST, Université de Bourgogne
Franche-Comté, 25030 Besançon, France (e-mail: bruno.legeard@femto-st.fr).
Frank Olaf Sem-Jacobsen is with Statsat AS, 0212 Oslo, Norway (e-mail:
Frank.Sem-Jacobsen@statsat.no).
Digital Object Identifier 10.1109/TITS.2023.3322690

rescue missions at sea, or more generally, regulating the
maritime traffic. In addition, modern VTS systems also support
the detection of illegal activities such as piracy, fishing in
protected zones, intrusion into economic exclusion zones,
transshipment of narcotics, degassing at sea, etc. Most of the
time, the detection of these illegal activities rely solely on
the visual observation of vessels, manual analysis of collected
data, and coastal administration officers’ intuition based on
their long-term experience [1].
Among the sources of maritime surveillance information,
Automatic Identification System (AIS) messages play an
essential role. At sea, passenger ships or ships of sufficient
tonnage must transmit their identity, their position, their direction and speed, and additional information up to every two
seconds [2]. These messages are captured by various means,
such as beacons at sea, coastal base stations, and satellites
dedicated to observing maritime traffic. However, it happens
that the transmission of AIS messages is absent for some
vessels. It can be due to a failure of the AIS transponder,
but it may also correspond to its intentional shutdown.
Actually, shutting down the AIS transmission is a
simple action used by (a few) vessel captains to silently
perform illegal actions at sea. For example, in order to
fish in a prohibited area located in the open sea, a vessel
can stay invisible by intentionally shutting down the AIS
transponder [3] during fishing. For instance, Oceana [4] reports
that, from 2018 to 2021, it’s no less than 600 000 hours by
800 fishing ships that occurred in an illegal fishing zone close
to the Argentina’s national waters by using this technique.
Noticeably, Agnew et al. [5] estimate that a total loss between
$10 billion and $23.5 billion can be imputed annually to
illegal and unreported fishing activities worldwide, which
shows that this problem has a huge economic impact. Desai
and Shambaugh [6] further emphasize the negative impact of
illegal fishing on local fishing industries and its destruction
of the corresponding ecosystem and the environment.
The problem is considered serious by the coastal administration all around the world and for prohibited maritime areas
close to the coast (typically within a 20km-zone from the
coast), different sources of information (e.g., radars, human
visual control from ships or land stations) can be efficiently
combined to automatically detect illegal activities. However,
when vessels transit at long distance from any coast in

1558-0016 © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

BERNABÉ et al.: DETECTING INTENTIONAL AIS SHUTDOWN IN OPEN SEA MARITIME SURVEILLANCE

the open sea, the maritime surveillance can only rely on
satellite AIS data. For instance, in the past ten years, the
Norwegian Coastal Administration has been using satellites to
capture AIS messages outside the areas covered by the base
stations. Statsat AS, the company in charge of managing these
satellites on behalf of the Norwegian government, drives the
AISSat-{1, 2}1 and NorSat-{1, 2, 3}2 satellites which supervise AIS transmissions. These satellites are inclined at 97◦
and are positioned in Sun-synchronous polar orbit at an orbital
height of 600-650 km, such that they shift to cover all latitudes
with each rotation around the earth.
While these satellites ensure a broad coverage of the earth,
it happens that some AIS messages remain unseen due to
weather perturbations or reception conflicts. Also, the selected
polar orbit leads to a better coverage of the poles rather than
the equator. Hence, to human eyes, while reconstructing the
trajectory of a single ship, it is common to have missing AIS
messages on the trajectory, but for a given ship trajectory,
distinguishing missing AIS messages reception due to an
AIS transponder shutdown from acceptable causes is almost
impossible. In order to distinguish both cases, we refer to
abnormal missing AIS message reception for the former case
and as ordinary missing AIS message reception for the latter.
Even though the number of messages that can be processed
by the satellites is artificially limited, the volume of collected
AIS messages is still considerable. In a single day, the
Norwegian satellites can collect more than 4 million AIS messages (e.g., on 15/01/2020, there were 4,862,628 messages).
Due to the high volume, only a restricted proportion of AIS
messages can actually be manually explored. To the best of our
knowledge, there exists no dataset annotated by operators that
differentiate intentional AIS shutdown from ordinary missing
AIS message reception. It is therefore not possible to train
models to directly detect these issues. For any alerting system
to be actionable (i.e. sending out assets to investigate) the
system needs to detect intentional AIS shutdown in near
real-time. Prompt delivery of alerts ensures that the coastal
administration can follow up on the alert while the illegal
activity is performed. The large datasets, seemingly unpredictable nature of data gathering, and timeliness requirements,
make it very challenging to detect intentional AIS shutdowns
in the open sea and to propose an alerting system that can
work in near real-time.
This paper proposes a deep learning-based approach to
detect intentional AIS shutdowns in open sea. Our method uses
self-supervision techniques to cope with the problem related
to distinguishing ordinary from abnormal missing AIS message reception (which are witnesses of likely intentional AIS
shutdown). Self-supervision means to extract pseudo-labels
from the unlabelled data set [7]. Our method is generally an
unsupervised task, but as pseudo-labels can be derived from
the dataset itself using self-supervision techniques, it allows
us to eventually train the model in a supervised manner.
By training a multi-layer neural network model with autolabelled data that learn the missing AIS messages’ normality,
1 https://eoportal.org/web/eoportal/satellite-missions/a/aissat-1-2
2 https://eoportal.org/web/eoportal/satellite-missions/n/norsat-1-2

1167

we design a model that can process AIS messages in real-time
and alert the coastal administration on suspicious ship trajectories containing possible intentional AIS shutdowns. More
precisely, the results presented in this article revolve around
three distinct contributions:
1) We provide a self-supervised deep-learning methodology to detect abnormal missing AIS reception in the
open sea. Our methodology is based on unlabelled
world-covering satellite-collected AIS data, which has
not been annotated by operators;
2) Our methodology is designed for live surveillance of
vessels. It exploits raw monthly data containing up to
500 million vessel messages corresponding to more than
60,000 unique vessels. Our DL model can be exploited
in real-time to ease the decision-making process of the
coastal administration;
3) We demonstrate through experimental results the effectiveness of our methodology, as well as its robustness
in varying scenarios and configurations. In particular,
the use of the state-of-the-art transformer deep learning
model architecture benefits us with greater precision in
the data analysis.
The rest of this paper is organized as follows: Section II
reviews previous work on the usage of Machine Learning in
the maritime surveillance. We introduce our methodology with
a general overview in Section III, before detailing how raw
data are handled in Section IV. Section V presents our methodology in depth as well as the architecture of our deep learning
model and its training regime. In Section VI, we evaluate the
methodology in experiments along three research questions,
and conclude with a discussion in Section VII.
II. E XISTING M ETHODS IN M ARITIME
T RAFFIC S URVEILLANCE
Intentional shutdown of the AIS transponder to hide illegal
fishing or illicit cargo transfer is a common illegal activity in
maritime domain, and several methods have been proposed to
detect intentional AIS shutdown. We review these methods in
Section II-A. Then, in Section II-B, we present the methods
processing satellite AIS data using machine learning.
A. AIS Shutdown Detection
In [8] and [9], Mazzarella et al. design a method to compute
the probability of receiving an AIS message depending on the
distance to the base station. For that, the signal strength to the
base station is used to create a probability map. Also, in [10],
Shahir et al. draw a probability distributions for suspected dark
fishing. In [11], Kontopoulos et al. identify AIS switch-off in
near real-time by analysing large streams of AIS messages
received from terrestrial base stations. The method relies on
the high-quality of the data coming from these sources by
predicting precisely when AIS messages are expected for a
given ship trajectory in a given cell from a coverage network.
In [12], Singh and Heymann propose to detect AIS switch-off
in a labelled dataset extracted from a single base station using
a multi-class artificial neural network, that can additionally
determine if anomalies are due to power outage. The dataset is

1168

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 2, FEBRUARY 2024

composed of 132 352 messages, corresponding to 133 distinct
vessels. These three solutions have proved to achieve excellent
results when using high-quality AIS datasets, but they are
limited to only detecting intentional AIS shutdown of vessels
located in the neighbourhood of base stations. They have
not been experimented yet when using satellite-based AIS
datasets, which is the only source of AIS available in the
open sea. Besides, by using only ground-based AIS message
streams, they cannot detect vessels having their AIS already
switched off which penetrate into a surveillance zone. Therefore, it seems complementary to combine these methods with
solutions adapted for the open sea able to process satellite data.
In this context, AIS missing reception is influenced by the spatial and temporal coverage of the satellites, as well as potential
signal collisions and weather conditions. These elements make
satellite-based datasets very fragmented, with irregular missing
reception from a few minutes to several hours. Moreover,
when considering trajectories located in the neighbourhood
of base stations, the signal coverage of satellites is very poor
as compared to the signal from beacons, which makes any
comparison or generalisation very difficult. In [13], Ford et al.
propose a Generalised Additive Model (GAM), adapted to the
open sea, which captures space-time variations in AIS gaps
during transmissions. The model aims at detecting abnormal
AIS missing reception and the overall approach shows good
results for an area located between the Australian and Indonesian EEZ border. Interestingly, the approach uses the frequency
of transmissions of other vessels to compute the probability of
(not) receiving a message. It renders the method more accurate
when considering highly dense traffic zones. However, the
confidence level of the method starts at a very low level and
increases over time because it is based on a probability map.
Hence, the solution is well-suited for post-mortem analysis,
i.e., analysis of the traffic several hours after it actually happened. In [14], Weimerskirch et al. use GPS data provided by
GPS transponder attached on Albatross birds to track fishing
vessels. This solution is original and works in real-time, but it
is limited to specific areas where albatross birds live and follow
fishing vessels. In [15], d’Afflisio et al. propose a procedure
based on the Ornstein-Uhlenbeck mean-reverting stochastic
process to detect anomalous deviations from standard maritime
routes hidden behind AIS Shutdown. This solution cannot be
adapted to fishing vessels that have unpredictable trajectories.
It also requires to wait for the re-connection to determine the
abnormality. In [16], Park et al. make the correlation between
the vessel lights at night captured with satellite images and the
reported AIS messages received from these ships. Using this
correlation, the authors discovered a dark fleet fishing illegally
in North Korean waters, estimated to be worth $440 million.
However, the generalisation of this solution is unfortunately
impossible as the vessel lights are usually turned off during
the day. While the two last presented solutions are original
and useful for evaluating the negative impact of illegal fishing
activities, they cannot easily be generalised and cannot offer
a robust solution to the problem of automatic intentional AIS
shutdown detection. Using hidden information channels for
detecting illegal activities is appealing, however, the only

source of reliable information available in open waters is
satellite-captured AIS data.
In summary, existing analysis methods for detecting AIS
switch-off are mostly based on high-quality data coming from
base stations, or on probability maps which are relevant only
for post-mortem analysis, or else on hidden channels that
cannot be generalised. In contrast, our work focuses on near
real-time prediction in the open sea based on satellite data
that are highly irregular and impacted by the position of the
satellites, the number of vessel in the area, the weather and
more. In that respect, it is complementary to other methods.
Also, it is worth noticing that shared labelled datasets for
detecting intentional AIS shutdowns do not exist, which makes
fair comparison between different methods very difficult.
B. Machine Learning Applied to AIS
The major challenge with AIS messages received by a fleet
of surveillance satellites is that they contain irregular patterns
and missing data. Also, AIS data captured by satellites is noisy
because there can be errors in the information entered by
vessel captains, or AIS transponders can be of low quality
or damaged. Previous work that processes AIS data automatically has focused on detecting anomalies from predicted ship
trajectories, trajectory reconstruction, collision avoidance and
future traffic evaluation.
Among existing techniques, the usage of probabilistic models of ships’ behaviour from historical AIS data has been
proposed. For instance, the exploitation of Gaussian mixture models (GMMs) [17], grid-based methods [18], Markov
models [19] or hierarchical neural networks [20] have led
to significant advances in terms of trajectory reconstruction,
trajectory prediction and anomaly detection. Other work has
also focused on enriching vessel information from radar
and visual tracking [21]. For detecting anomalies in AIS
message transmission, reconstructing the trajectory of vessels
just before the loss of the signal is crucial. Arguedas et al.
use graph-based methods to create a promising lightweight
representation of vessel trajectories [22]. Nguyen et al. in [23]
and [24] use a representation that regularises the frequency of
messages by completing a dataset with artificially generated
missing messages. Interestingly, this approach deals with noisy
data and allows datasets to be used for training models for
multitasking learning. However, the datasets do not come
from satellites but from beacons at sea. As a limitation, such
an artificially completed datasets cannot be used to detect
intentional AIS shutdown because the missing messages have
been re-introduced for the purpose of regularisation [23], [24].
Other approaches include using ship-tracking probability
maps, such as those created by Skauen [25], to estimate the
probability of receiving (or not receiving) a satellite-based AIS
message in a given time frame. However, these maps estimate
the probability of re-detecting an already detected ship, which
implies that one needs to wait a significant amount of time
before any action is triggered.
In contrast to these works, we propose to train a
self-supervised model for a given vessel, in order to build

BERNABÉ et al.: DETECTING INTENTIONAL AIS SHUTDOWN IN OPEN SEA MARITIME SURVEILLANCE

Fig. 1.

1169

Overview and data flow of our self-supervised learning method for the detection of abnormal missing AIS reception.

a representation that considers the previous messages and
the gap between them, as explained in Section IV-D. This
allows us to propose a method that reveals suspicious cases
of intentional AIS shutdowns as soon as a vessel’s signal
disappears.
III. M ETHOD OVERVIEW
Before giving an in-depth presentation of our selfsupervised method, we introduce a high-level overview of its
different components and their connection, as shown in Fig. 1.
The diagram highlights three distinct processes, namely, Data
Collection, Data Processing and Self-Supervised Training and
Operation, and their workflow. First, during Data Collection, the satellite operator collects and stores AIS data from
geo-marine observation satellites. In the context of this work,
the Norwegian Coastal Administration has provided us access
to the AIS data collected by the Norwegian state operator
Statsat AS during 2020, which corresponds to approximately
4 billion messages. As part of the Data Processing and SelfSupervised Training process, the collected data is first prepared
and processed into a dataset, including the enrichment with
self-supervision labelling information. As said above, the
main issue is to distinguish ordinary vs. abnormal missing
AIS reception. For this purpose, we have used the following
artefact for implementing our self-supervised training method
with the collected data. For a given ship in the open sea,
given a window of w successive AIS messages (typically
25 messages, but other window sizes can be considered) and
a time frame τ (typically, 10 minutes), one can train a model
that predicts if an AIS message is expected to be received
in the next time frame τ . This model will then be useful to
compare its prediction with the actual observation performed
in near real-time (i.e., using the same time frame τ ) regarding
the reception of the expected AIS message. Fig.2 illustrates
this principle by considering a window of w = 3 messages.
Red-flagged trajectories indicate that no message is expected
within τ while green-flagged trajectories indicate the opposite.
During Operation, by using the trained model with the
auto-labelled dataset and a logical decision module that analyses real-time observations streamed from the surveillance
satellites, it becomes possible to classify ordinary versus
abnormal missing AIS reception. Every collected vessel trajectory is again preprocessed into the machine learning model

Fig. 2.
Auto-labelling of trajectories: Green flags indicate trajectories
expecting an AIS message in the next time frame τ , while red flags indicate
trajectories without an AIS message.

input format, although in this context without the addition of
self-supervision information that is only necessary for training
purposes. Based on the time frame τ , the logical decision
module then classifies the vessel trajectory as either abnormal,
highlighting a risk of intentional AIS shutdown, or as ordinary.
In the first case, a specific alert can be escalated to an operator
or a downstream system for further investigation, while in the
second case issues no alert.
IV. DATA P ROCESSING
A. Automatic Identification System (AIS)
According to AIS technical specifications [26], messages
are composed of static and dynamic information. Static fields
include, amongst others, international standard vessel identifiers, i.e., MMSI,3 IMO ship identification number, vessel
name and call sign, ship dimensions and vessel type. These
static elements, which are entered manually by the vessel
captains into the AIS transponder, are automatically transmitted on a broadcast channel every 6 minutes. Also, AIS
transponders send dynamic information every 2 to 10 seconds
depending on the vessel’s speed, or every 3 minutes if the
vessel is at anchor. The dynamic information includes navigation status, e.g., “at anchor” or “fishing”, vessel position in
terms of latitude (lat) and longitude (lon), vessel speed over
ground, its direction relative to the north pole, its true heading
relative to the magnetic north pole and the timestamp when
the message was sent. There are currently 27 different AIS
3 Maritime Mobile Service Identity.

1170

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 2, FEBRUARY 2024

TABLE I
OVERVIEW OF S ATELLITE AIS DATA C OLLECTION

1t and TD allow having a better precision on the temporal
dimension than that given by the timestamp t,
• 1D V and 1D H improve understanding of position over
small distances,
• D P allows filtering the relevant samples (more information on this point in Section IV-D).
Thus, the vector of characteristics corresponding to a message
takes the following form:
•

m = [t, lat, lon, s, 1t, 1DV , 1D H , D P , TD ]
message types. Of these message types, we only consider the
subset that contains the dynamic information, i.e., message
types 1, 2, 3, 18 and 19. Typical AIS transponders have a
range of about 20 to 40 km. The limitation of this range is
due to the curvature of the earth and the height at which the
antenna is installed on ships. For vessels too far away from
the coast or other AIS observers, AIS satellites collect and
forward the messages.
B. Data Collection
One challenge with AIS data collection is that the radio
access scheme defined in the standard creates only 2200
available time slots every minute for each of the 2 channels and
receivers can be easily overwhelmed by large AIS reception
footprints [25]. Due to the growing number of AIS transponders and the expansion of the satellite reception area, message
collisions can occur and lead to vessel disappearance [27].
Our satellite-based AIS dataset, provided by the Norwegian
Coastal Administration and collected by Statsat, consists of
4 050 019 441 AIS messages from all over the world, which
corresponds to the messages collected for the year 2020 (see
Table I). Technical issues on the satellite during the original
data collection can explain the difference in the number of
messages per month. However, we did not notice any bias in
the data or any effect on our experimental results as a result
of this difference.
C. Feature Extraction
From each message of the AIS dataset, we select relevant
characteristics, namely position (lat, lon), the timestamp (t),
and speed (s). Also, we enrich the characteristics with 1t
the time difference compared to the preceding message from
the same ship, 1DV the difference in meters on the latitude
with the preceding message from the same ship, 1D H the
difference in meters on the longitude, D P the distance to
the port, TD the second of the day (between 0 and 86 399).
We have chosen to split the relative distance with the previous
message between 1D H and 1DV to keep the direction of
movement.
It is worth noticing that:
• The distance 1D V , 1D H , D P are computed with the
Haversine formula.4
4 The distance of the arc on a sphere is not as precise as the Vincenty
formulas in geodesy since the earth is not a perfect sphere, but its computation
has the advantage of being vectorisable, which is necessary in the case where
the dataset contains a very large number of trajectories.

A trajectory E is a temporal sequence of T successive
messages from a ship E = [m 1 , m 2 , . . . , m T ]. It corresponds
to the trajectory of a ship’s motion in a time window. Also,
note that there is no constraint on the maximum values of 1t
and 1D, between two successive messages within a trajectory.
D. Dataset Creation
A total of 500 000 trajectories has been extracted for each
month, creating 12 datasets, equally balanced between two
classes: 1. trajectories including a message received within
the time frame; 2. trajectories without any message received
within the time frame Fig. 3 shows the distribution of the
samples on the surface of the globe for January 2020. For the
selection of trajectories in the dataset, we set two conditions:
1) The AIS vessel trajectory history must consist of at
least 50 messages to exclude vessels not sufficiently
represented over the entire year of the dataset. This
corresponds to about a 1-minute history for a moving
vessel. Indeed, these trajectories are too short for any
relevant generalisation by the model;
2) The ship’s loss of reception must be at more than
5 kilometres from a port (D P > 5km). This eliminates
examples of intentional (legal) AIS shutdown that take
place in ports. It is also relatively easy for the coastal
administration to control vessels without AIS transmission in ports. To determine the distance to the nearest
port, we calculate the distance of the arc between two
points on a sphere with a database of nearly 30 000 ports
compiled by the organisation Global Fishing Watch.5
The datasets used for training, validation, and testing of the
model are separated by date, e.g., train on the January data
with 10% of the February data for validation, and then test on
the rest of the February data. Another alternative is to separate
by ships, i.e., train on one group of vessels and test on another,
but the temporal separation has the advantage of being closer
to the operational use of the model, since the objective is
to make predictions based on past data to predict upcoming
missing AIS reception. A further alternative would be to split
by geographical regions, but this would either require a strong
regional generalization or result in a highly region-specific
model, whereas we aim for a globally applicable model.
Therefore, the model will be trained according to the described
separation by date.
Table II shows the range of duration and distance between
two consecutive messages along with the total duration and
5 https://globalfishingwatch.org/datasets-and-code/anchorages/

BERNABÉ et al.: DETECTING INTENTIONAL AIS SHUTDOWN IN OPEN SEA MARITIME SURVEILLANCE

1171

Fig. 3. Distribution of January’s samples over the surface of the globe. Each point shows the location of the most recent message and whether the next
message will be received within 10 minutes.

TABLE II
S TATISTICS FOR JAN . 2020 DATASET (500 K T RAJECTORIES ) S HOW A
W IDE VARIETY OF T RAJECTORY C HARACTERISTICS . (1d = D IST.
B ETWEEN M ESSAGES , 1t = T IME B ETWEEN
M ESSAGES , 6d = T RAJECTORY L ENGTH AND
6t = T RAJECTORY D URATION )

distance trajectories. We observe the dataset to be heterogeneous with strongly varying time spans and distances between
messages as well as drastically different trajectories, explained
both by different vessel types and irregularities in AIS reception and therefore potentially long gaps between messages.
Noticeably, 1% of the messages are sent with a time-interval
of 1s or less, which is abnormal w.r.t. AIS protocol. In fact, our
data is noisy and the noise is mostly due to inappropriate reuse
of MMSI numbers. Skauen et al. estimate than in between
0.5% to 2% of the MMSI numbers are reused [25], [28].
V. T RAJECTORY P REPROCESSING AND S ELF -S UPERVISED
M ACHINE L EARNING M ODEL
Fig. 4 shows an overview of the architecture of the deep
learning model. Firstly, the preprocessing step encodes and
normalizes the input trajectory E to simultaneously handle
long distances between two messages and to maintain sufficient precision for those messages having only few seconds
of difference. It also allows us to dissociate the trajectory from
the absolute time and position toward a generic representation.
Secondly, the two output vectors of the preprocessing step are
transferred to the deep learning model that is trained to classify
whether a message should be received or not.

Fig. 4. Model architecture: The relative vessel trajectory is encoded via
a transformer network and forms together with the most recent position a
representation vector for classification.

A. Trajectory Preprocessing
The preprocessing block in the Fig. 4 is essential to
our approach. Following the feature extraction describe in
Section IV-C, the input trajectory E is divided into two vectors,

1172

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 2, FEBRUARY 2024

VH the history of AIS messages which contains the information relating to the previous message and VL the most
recent position. Then VH and VL go through a normalization
layer N . The input is divided to have an encoding that
considers the possible small distances that can be found
between two messages while maintaining very high precision
on the starting position of missing AIS reception.
1) Message History: To represent the message history
VH generically, the normalization layer N first removes the
absolute position in latitude and longitude and the absolute
time represented by the timestamp. Instead, the representation
only considers the time and distance differences relative to
the previous message. Since the model is supposed to work
in relation the most recent received message of a vessel’s
trajectory we can therefore create a relative representation
space and work time-independently. In addition, the second of
the day SD is added to strengthen the detection of temporal
patterns. A cyclic normalisation NC (Eq. 1) is applied to cyclic
fields such as the SD , a linear normalisation NL (Eq. 2) is
applied to limit values such as speed V. For 1t, 1DV and
1D H , a logarithm is applied (Eq. 3).



 
2π(x − min x)
2π(x − min x)
, cos
NC = sin
max x − min x
max x − min x
(1)
(x − min x)
(2)
NL =
max x − min x
N (VH ) = [log(1t), log(1DV ), log(1D H ),
NC (SD ), NL (V)]
(3)
N (VP ) = [NL (lat Deg ), NC (lat Min ), NC (lat Sec ),
NC (lon Deg ), NC (lon Min ), NC (lon Sec ), . . . ]
(4)
2) Most Recent Position: The vector N (VP ) consists of
11 values allowing the model to have maximum precision on
the position of the vessel at the most recent message received.
N decomposes latitude and longitude into Degree-MinuteSecond and then normalises them cyclically to maintain
continuity (Eq. 4), for example, when a ship passes longitude
180 at −180.
B. Model Architecture
Our method to detect the abnormal missing AIS reception
is based on transformer models, a deep learning architecture.
Transformer models have demonstrated compelling results in
the field of Natural Language Processing (NLP) [29] and the
field of computer vision [30]. The suitability of the transformer
architecture for dealing with sequential data makes it a good
candidate for the analysis of time series. In the context of AIS,
the message history can be seen as a time series [31], [32].
The transformer architecture is a variant of self-attention
networks [33] for processing sequential data, however it does
not involve a recurrent network architecture [34]. This is
possible due to the multi-head self-attention [35] mechanism,
that allows it to attend and weight multiple parts of the
sequence differently in parallel. Thereby, it allows to model

both long-term and short-term dependencies within the input
sequence [36].
We specifically use the encoder part of the transformer
model to extract a general fixed-size representation vector,
that can be used in a generic way for different applications
in maritime surveillance, here for the detection of abnormal
missing AIS reception. More specifically, the model consists
of two transformer blocks, following on the model of [35],
to encode a variable-length input sequence VH together with
a positional encoding into the first part of the representation
vector R. Choosing 64 as the size of the representation
vector R results from a tradeoff between the model complexity
and an attempt to prevent the classical overfitting risk and has
been determined through preliminary experiments.
This first part is concatenated with the second input, the
most recent position VL , into the overall fixed-size representation vector. This vector is then processed by the final,
task-specific subnetwork. Here, this subnetwork consists of
three dense layers of respective size (100, 50, 50) with ReLu
activation and 10% dropout and a final layer to classify
whether a message should be received within the given time
frame.
C. Detection of Abnormal Missing AIS Message Reception
Given a ship trajectory and a time frame τ , the model is
trained to predict whether an AIS message from the vessel
shall be received or not, within τ . Using this model, it becomes
possible to classify ship trajectories as ordinary or abnormal in
near real-time. More precisely, there are four distinct situations
for a given trajectory:
1) If the model predicts that no AIS message is expected
and no message is actually received during the time
frame τ , then the trajectory can safely be classified as
ordinary. The model has correctly learnt that the ship
has an ordinary AIS disconnection due to any acceptable
cause (i.e., reception conflict, loss of satellite coverage,
etc.);
2) If the model predicts no AIS message and a message
is actually received within τ , then there is a prediction
error in the model. The trajectory can be safely classified
as model error;
3) If the model predicts that an AIS message shall be
received within τ and a message is actually received,
then the trajectory can safely be classified as ordinary;
4) If the model predicts that an AIS message is expected
within τ and no message is actually received, then the
trajectory can be classified as abnormal. These latter
cases are the most interesting for the coastal administration, whom can then proceed to a detailed analysis of the
ship trajectory in order to confirm or denial the abnormal
missing AIS reception. In this case, the complete vessel
AIS history is reported.
During operation, only the missing AIS reception that exceed
the time frame are analysed. This is corresponding to the
cases 1) and 4) Note that having a prediction model with high
precision is crucial here to avoid the production of too many
false negatives or false positives. The detailed examination of
a ship trajectory takes time and there is a challenge to report

BERNABÉ et al.: DETECTING INTENTIONAL AIS SHUTDOWN IN OPEN SEA MARITIME SURVEILLANCE

only suspicious trajectories which are likely to correspond
to actual intentional AIS shutdown. Note also that the time
frame must be exhausted in order to classify ship trajectory.
Besides justifying the terminology “near real-time”, it also
justifies the selection of a value for τ which is compatible
with current practices of the coastal administration. Indeed,
it will be useless to classify ship trajectories as suspicious
after a long time like 24 hours.
VI. E XPERIMENTAL E VALUATION
In this section, we evaluate the capabilities and robustness
of the proposed model. For that, we examine different configurations of the trained models, such as their architecture
and the training set size, the selection of the most appropriate
time-horizon for improving the detection of missing AIS
messages. More precisely, we investigate these three research
questions:
RQ1 Is the method effective enough to detect abnormal AIS
shutdown?
RQ2 How stable is the model over time, and is it affected by
dataset shift?
RQ3 How robust is the model and its effectiveness to configuration changes, i.e., changes in training set size,
message window size, model architecture, or predicted
time horizon?
A. Experimental Setup
In our experiments, the batch size B is equal to 128, the
message window size W is 25 and the representation vector
size R is 64 (see Fig. 4). With these hyperparameter values,
the model M has a total of 470 821 trainable parameters. For
model training, the dataset contains 200 000 trajectories with
10 minutes time horizon labels. The model is trained over a
maximum of 200 epochs with each 1562 batches with early
stopping once the validation loss converged. All training is performed with the configuration described above, unless stated
otherwise. Section VI-D compares the results for the most
impactful hyperparameters. All our experiments are run on an
NVIDIA DGX-2 with an Intel Xeon Platinum 8168 CPU with
2.7 GHz and 24 cores, using one NVIDIA Tesla V100 graphics
card.6 One epoch of model training takes approximately 17s.
We have evaluated the model stability by running each model
prediction five times with different initial random models.
As said in Section IV-D, the one-year dataset is separated into
12 time-windows, one per month.
Evaluation Metrics. Three metrics are used to compare
the models: 1) the accuracy (Eq. 5), which measures the
overall capability of the model to predict whether a message
should be received or not; 2) the positive predictive value
(Eq. 6), or precision, focuses on the model capability to predict
whether it is normal to not receive a message or not; and 3) the
negative predictive value (Eq. 7), which focuses on the error
made by the model when it predicts that we should not receive
a message, but we receive one.
6 Provided by the eX3 research infrastructure: https://www.ex3.simula.no/

1173

TABLE III
RQ1: C ONFUSION M ATRIX ( IN %), ON 4.5M T RAJECTORIES OF
V ESSELS D ISAPPEARING M ORE T HAN 10 M INUTES

Formally speaking,
TP +TN
T P + FP + T N + FN
(5)
TP
Positive predictive value (PPV) =
(6)
T P + FP
TN
(7)
Negative predictive value (NPV) =
T N + FN
where TP stands for True Positive, TN for True Negative,
FP for False Positive and TN for False Negative.
Accuracy =

B. RQ1: Model Effectiveness
There are no datasets for evaluating our model precisely
on the task of detecting voluntary AIS shutdown. Therefore,
we have reversed the question into predicting whether a
message is received within a time frame or not in order to
train a model in a self-supervised manner.
Therefore, it is important to note that the model accuracy
corresponds to the prediction of message reception within a
time frame and not the prediction of voluntary AIS shutdown.
For this particular task, the combination of the model and
the encoder presented in this paper has shown the high
accuracy between 99.5% and 99.8%. Table III shows the confusion matrix for prediction results of 4 500 000 trajectories.
False negative (F. neg.) means that the model predicted a
non-reception of a message, while the message is received;
False positive (F. pos.) means that the model predicted a
reception of a message, while the message is not received.
The 0.04% of detected false negatives can only be caused
by a model error. On the other hand, the 0.2% false positives
can either be due to a model error or an anomaly. In our
results, 8868 of trajectories are returned as anomalies out
of 2 250 000 trajectories that are annotated as missing AIS
messages. However, there is no precise way to evaluate and
filter the proportion of accurate missing AIS receptions among
the 8868 of total model predictions for a full year covering
the whole globe. We discuss model errors in Sec.VI-F.
C. RQ2: Model Stability Over Time & Dataset Shift
The second research question addresses the model stability
over time and possible effects of dataset shift [37]. A trained
model has potentially the highest accuracy for trajectories
that are close in time to the period covered by the training
data, since it is expected to be most similar to the data
within the training set, i.e., it is from a similar distribution.
However, over time this distribution might change, e.g., due to

1174

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 2, FEBRUARY 2024

TABLE IV
RQ2: S TABILITY OF THE M ODEL ( IN %). S MALL S EASONAL E FFECTS T HROUGHOUT THE Y EAR , BUT THE M ODEL I S G ENERALLY S TABLE

seasonal effects. To investigate the general stability of the
model over time and a potential negative impact from dataset
shift, we perform two evaluations:
1) We train the model on one month and evaluate it on the
next month, e.g., training on January and evaluation on
February, repeated for all months of the year;
2) We train the model once on the January dataset and
evaluate its accuracy on the other months of the year.
The results are shown in Table IV. We observe a small
dataset shift, as indicated by the slightly lower accuracy of the
fixed model trained on the January data. For each individual
month this difference in accuracy is not more than 0.15%
and in the average over the year not more than 0.08%. The
variation in accuracy is accounted for by seasonal effects. The
largest accuracy differences occur in the summer months, i.e.,
June to September, whereas towards the end of the year the
accuracy gap is closer or even non-existent in December.
We conclude from this experiment that the model is generally stable and that there is no need for frequent re-training.
Since the encoding of the vessel trajectory works on relative
time and position information, there is no strong dependency
or link to the absolute time of the training data, but just
the vessel traffic patterns, which are subject to seasonal
adjustments. However, it is advisable to consider a training
dataset that spans multiple months or seasons of data to further
improve the model stability.
D. RQ3: Model Robustness to Configuration Changes
As previously introduced, our model allows to be adjusted
through a number of configuration decisions and parameters.
Those include both parameters that affect the operation in
maritime surveillance, i.e., the horizon of time during which
an AIS message is expected, and technical decisions, i.e.,
the dataset size used for training or the model architecture.
To analyse the robustness of the model, we vary each of these
parameters individually to identify the sensibility of the overall
model to this parameter.
1) Dataset Size: As the first parameter, we vary the dataset
size used for training from 10k to 500k trajectories of each
25 messages. As shown in Table V, the training benefits from
more data, but the effect diminishes after 100 000, while the
training time continues to increase approximately linearly.
We therefore select a dataset size for our experiments of
200 000 to balance accuracy and training cost.
2) Window Size: The window size controls how much of
a vessel’s history the model receives as input. Fig. 5 shows
that some history is relevant to identify vessel behaviour,
but that the effect saturates and a higher window size only
increases model complexity but reduces the accuracy. For our
experiments, we selected a window size of 25 messages, which

TABLE V
RQ3: ACCURACY BY DATASET S IZE

Fig. 5. RQ3: Accuracy for different model architectures and message window
sizes.

showed the best accuracy. However, it should be noted that
the window size is likely to be specific for the surveillance
application, e.g., for other applications such as detecting
missing AIS reception, a larger window size can be more
beneficial.
3) Model Architecture: In this experiment, we vary
the model architecture and alternatively select a standard
feed-forward neural network and a transformer model without
AIS message encoding. The feed-forward neural network
consists of 5 layers with 10/20/25/20/10 neurons, selected
by hyperparameter search. Since the input layer needs to be
adjusted for each input size, we opt to test it with one input
message, as the most naive baseline, and 25 input messages,
as selected for our main architecture.
The results are again shown in Fig. 5. While the naive
baseline is not competitive, it highlights the necessity of
considering a multi-message window size. For the direct
comparison of all three architectures, the feed-forward neural
network achieves an accuracy of 96.82%, which exceeds
the 90.86% accuracy of the transformer without the custom
encoding, whereas the full model achieves 99.65% accuracy.
This result underlines the importance of the dedicated message
encoding in combination with the transformer architecture.
4) Horizon of Time: The horizon of time parameter is
closely linked to the model’s operational use, as it defines the
threshold after which the missing reception of AIS messages is

BERNABÉ et al.: DETECTING INTENTIONAL AIS SHUTDOWN IN OPEN SEA MARITIME SURVEILLANCE

1175

an inherent delay in processing and detecting intentional AIS
shutdown events.
F. Discussion

Fig. 6. RQ3: Comparison of five different time horizons. Total messages
received after each threshold from the whole February data with 138 million
messages and accuracy for the model trained with a subset of 200,000
trajectories.

deemed interesting or relevant. We evaluate five time horizons:
1, 5, 10, 30, and 60 minutes. The model is both trained and
tested with these time horizons.
The results are shown in Fig. 6 with no major difference in
accuracy between the different time horizons. Therefore, it is
the choice of the operator between a shorter reaction time with
a potentially higher number of misclassifications as anomalies
versus a longer reaction time and lower risk of misclassifications. Even if the accuracy is high, the quantity of missing
messages is significant too, and a small prediction error can
represent a large number. If we compare the examples over the
threshold value in our dataset, the number of missing messages
with a time horizon of 1 minute exceeds those with a time
horizon of 60 minutes by a factor of 10. After discussions
with domain experts, we fixed the horizon of time for our
experiments to 10 minutes. This balances both the number of
potential false alerts and the reaction time, which is still short
in the context of satellite-based maritime surveillance.

E. Near-Real Time Detection
Detecting intentional AIS shutdown is highly relevant for
maritime surveillance monitoring and any alerting system has
to react to potential anomalies in (near) real-time. Technically,
by using the hardware components mentioned in Section VI-A,
our implementation processes 5 400 000 samples in
409 seconds, i.e., in less than 7 minutes. It corresponds
to a processing rate of 13 191 predictions per second,
a significantly higher rate than the rate of messages collected
per second by the four satellites used in our experiment.
These satellites gather approximately 100 to 150 messages
per second, with only a subset of these messages being
potential cases of intentional AIS shutdowns.
In practice, real-time detection of intentional AIS shutdown
is subject to certain limitations. One of these limitations is the
selection of time-horizon. In order to reduce the number of
false positives, it is necessary to wait for a user-selected timehorizon, which has been optimally evaluated to 10 minutes
in our experiments. Another aspect that affects real-time
detection, independent of our solution, is the method by which
the data is collected. The AISSat and NorSat constellations use
the Svalbard ground station in Norway to collect data on all
15 of the satellites’ polar orbital passes each day. In the worstcase scenario, the data is collected 96 minutes later, causing

In this study, we achieved excellent accuracy in predicting whether we should receive an AIS message within a
specific time frame. The key elements contributing to this
high accuracy are the combination of transformer model
with the encoding, and the size of the auto-labelled dataset.
However, detecting intentional AIS shutdown with high accuracy remains a challenging task, mainly because labelled
datasets with ground-truth information do not exist. The
approach we present in this paper deals with this problem,
but we still need to take two limitations into account, which
are not unique to the detection of intentional AIS shutdown but
common among the setting of limited labelled data in machine
learning. First, to cope with the absence of a labelled dataset,
our model is trained in a self-supervised manner with autolabelled data to predict when the next AIS message shall be
received from a given vessel. If there is a divergence between
the prediction and the real-time available information, then
an alert is reported. Even though we predict next message
reception with a very high accuracy, the model does not
provide guarantees on the accuracy to detect intentional AIS
shutdown. The availability of a labelled dataset would aid in
the training of a model with even higher accuracy, although
this would incur high cost to create the dataset in the first
place. Second, the effectiveness of our method mirrors the
diversity of the training dataset and the capability of the
model to generalise from patterns observed during training.
In our context, if an illegal activity is mimicking the most
standard vessel behaviour perfectly, it will be highly difficult
to detect. Similarly, if the behaviour is entirely different
from anything seen during training, although this is likely
to be detected as an anomaly in a AIS processing pipeline.
In order to investigate the possible materialisation of these
issues, we analysed 8868 trajectories detected as potential
anomalies, such as described in Section VI-B. By grouping
multiple vessels which present the same anomaly, we were
able to detect suspicious patterns. Among these clusters of
anomalous trajectories one of them particularly caught our
attention. It corresponds to a cluster of around 50 fishing
vessels shutting down their AIS transponders repeatedly, next
to Argentina’s Exclusive Economic Zone (in between 10 to
20 times over the year 2020). Signal loss can last for multiple
days before a vessel reappears again close to the border of the
zone. From the AIS-message based trajectory, it is observable
that these vessels go to anchor in Montevideo, Uruguay, before
and after going to the Argentina border where they disappear.
The alert triggered by our model was later confirmed in a
2021 report by Oceana [4].
VII. C ONCLUSION
Intentional AIS shutdowns are performed to hide illegal activities in open sea, where vessel traffic systems can
only rely on satellite AIS. In this article, we have presented a method for finding suspicious ship trajectories

1176

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 2, FEBRUARY 2024

containing intentional AIS shutdown in near-real-time using
self-supervised deep learning based on the analysis of satellite
AIS data only. The model is trained to detect abnormal
missing AIS message reception without requiring the provision
of a labelled dataset, which would be costly and laborintensive. The training process is instead designed to use
a self-supervision technique, where the transformer neural
network is trained with auto-labelled training data, that is
generated from raw AIS data.
Our experimental evaluation shows that the method can
predict expected AIS message reception with 99.5% accuracy
on previously unseen test data. Additional experiments further
underline the robustness of the method under different configurations as well as its stability over longer time periods,
avoiding the need for continuous re-training. Finally, we were
able to reproduce real-world reports of intentional AIS shutdown using our method.
For future work, we foresee two possible directions to
reduce model errors. First, we envision incorporating feedback
from the coast guard administration on reported abnormal
trajectories to discard false positives and enhance the quality
of auto-labeled training data (i.e., by discarding trajectories
with ordinary AIS shutdowns which are wrongly reported as
suspicious by the model). Second, our model’s performance
could be further improved by adding contextual information
from both micro- and macro-level data sources. Specifically,
this could involve examining the behavior of nearby ships,
integrating additional VHF Data Exchange System data, and
incorporating optical or infrared satellite imagery for more
targeted investigations. Moreover, the inclusion of macro-level
factors like weather conditions, sea currents, and vessel density
could offer a comprehensive understanding of AIS behavior,
thereby improving model robustness.
ACKNOWLEDGMENT
Satellite AIS data used for model development and testing has been made available courteously by its owner, the
Norwegian Coastal Administration (Kystverket).
R EFERENCES
[1] M. Riveiro, G. Pallotta, and M. Vespe, “Maritime anomaly detection: A
review,” WIREs Data Mining Knowl. Discovery, vol. 8, no. 5, Sep. 2018,
Art. no. e1266.
[2] “Revised guidelines for the onboard operational use of shipborne automatic identification systems (AIS),” IMO, Int. Maritime Org. (IMO),
London, U.K., Tech. Rep. Resolution A.1106(29), 2015.
[3] L. Malarky and B. Lowell, “Avoiding detection: Global case studies of
possible AIS avoidance,” OCEANA, Washington, DC, USA, Tech. Rep.,
Mar. 2018. [Online]. Available: https://oceana.org/publications/
reports/avoiding-detection-global-case-studies-possible-ais-avoidance
[4] P. Mustain, “Now you see me, now you don’t: Vanishing vessels
along Argentina’s waters,” OCEANA, Washington, DC, USA,
Tech. Rep., Jun. 2021. [Online]. Available: https://usa.oceana.org/
publications/reports/oceana-finds-hundreds-vessels-vanishing-alongargentinas-waters, doi: 10.5281/zenodo.4893397.
[5] D. J. Agnew et al., “Estimating the worldwide extent of illegal fishing,”
PLoS ONE, vol. 4, no. 2, Feb. 2009, Art. no. e4570.
[6] R. M. Desai and G. E. Shambaugh, “Measuring the global impact of
destructive and illegal fishing on maritime piracy: A spatial analysis,”
PLoS ONE, vol. 16, no. 2, Feb. 2021, Art. no. e0246835.
[7] L. Ericsson, H. Gouk, C. C. Loy, and T. M. Hospedales, “Self-supervised
representation learning: Introduction, advances, and challenges,” IEEE
Signal Process. Mag., vol. 39, no. 3, pp. 42–62, May 2022.

[8] F. Mazzarella, M. Vespe, A. Alessandrini, D. Tarchi, G. Aulicino, and
A. Vollero, “A novel anomaly detection approach to identify intentional AIS on-off switching,” Expert Syst. Appl., vol. 78, pp. 110–123,
Jul. 2017.
[9] F. Mazzarella, M. Vespe, D. Tarchi, G. Aulicino, and A. Vollero, “AIS
reception characterisation for AIS on/off anomaly detection,” in Proc.
19th Int. Conf. Inf. Fusion (FUSION), Jul. 2016, pp. 1867–1873.
[10] A. Y. Shahir, M. A. Tayebi, U. Glässer, T. Charalampous, Z. Zohrevand,
and H. Wehn, “Mining vessel trajectories for illegal fishing detection,” in
Proc. IEEE Int. Conf. Big Data (Big Data), Dec. 2019, pp. 1917–1927.
[11] I. Kontopoulos, K. Chatzikokolakis, D. Zissis, K. Tserpes, and
G. Spiliopoulos, “Real-time maritime anomaly detection: Detecting
intentional AIS switch-off,” Int. J. Big Data Intell., vol. 7, no. 2,
pp. 85–96, 2020.
[12] S. Singh and F. Heymann, “Machine learning-assisted anomaly detection
in maritime navigation using AIS data,” in Proc. IEEE/ION Position,
Location Navigat. Symp. (PLANS), Apr. 2020, pp. 832–838.
[13] J. H. Ford et al., “Detecting suspicious activities at sea based on
anomalies in automatic identification systems transmissions,” PLoS One,
vol. 13, no. 8, 2018, Art. no. e0201640.
[14] H. Weimerskirch et al., “Ocean sentinel albatrosses locate illegal vessels
and provide the first estimate of the extent of nondeclared fishing,” Proc.
Nat. Acad. Sci. USA, vol. 117, no. 6, pp. 3006–3014, Feb. 2020.
[15] E. d’Afflisio, P. Braca, L. M. Millefiori, and P. Willett, “Detecting
anomalous deviations from standard maritime routes using the Ornstein–
Uhlenbeck process,” IEEE Trans. Signal Process., vol. 66, no. 24,
pp. 6474–6487, Dec. 2018.
[16] J. Park et al., “Illuminating dark fishing fleets in North Korea,” Sci. Adv.,
vol. 6, no. 30, Jul. 2020, Art. no. eabb1197.
[17] B. R. Dalsnes, S. Hexeberg, A. L. Flaten, B. H. Eriksen, and
E. F. Brekke, “The neighbor course distribution method with Gaussian
mixture models for AIS-based vessel trajectory prediction,” in Proc. 21st
Int. Conf. Inf. Fusion (FUSION), Jul. 2018, pp. 580–587.
[18] B. Ristic, “Detecting anomalies from a multitarget tracking output,”
IEEE Trans. Aerosp. Electron. Syst., vol. 50, no. 1, pp. 798–803,
Jan. 2014.
[19] N. Fridman, D. Amir, Y. Douchan, and N. Agmon, “Satellite detection of
moving vessels in marine environments,” in Proc. AAAI, vol. 33, 2019,
pp. 9452–9459.
[20] K.-I. Kim and K. Lee, “Deep learning-based caution area traffic prediction with automatic identification system sensor data,” Sensors, vol. 18,
no. 9, p. 3172, Sep. 2018.
[21] D. D. Bloisi, F. Previtali, A. Pennisi, D. Nardi, and M. Fiorini, “Enhancing automatic maritime surveillance systems with visual information,”
IEEE Trans. Intell. Transp. Syst., vol. 18, no. 4, pp. 824–833, Apr. 2017.
[22] V. F. Arguedas, G. Pallotta, and M. Vespe, “Maritime traffic networks:
From historical positioning data to unsupervised maritime traffic monitoring,” IEEE Trans. Intell. Transp. Syst., vol. 19, no. 3, pp. 722–732,
Mar. 2018.
[23] D. Nguyen, R. Vadaine, G. Hajduch, R. Garello, and R. Fablet, “A multitask deep learning architecture for maritime surveillance using AIS data
streams,” in Proc. IEEE 5th Int. Conf. Data Sci. Adv. Anal. (DSAA).
IEEE, Oct. 2018, pp. 331–340.
[24] D. Nguyen, R. Vadaine, G. Hajduch, R. Garello, and R. Fablet,
“GeoTrackNet—A maritime anomaly detector using probabilistic neural
network representation of AIS tracks and a contrario detection,” IEEE
Trans. Intell. Transp. Syst., vol. 23, no. 6, pp. 5655–5667, Jun. 2022.
[25] A. N. Skauen, “Ship tracking results from state-of-the-art space-based
AIS receiver systems for maritime surveillance,” CEAS Space J., vol. 11,
no. 3, pp. 301–316, Sep. 2019.
[26] Technical Characteristics for an Automatic Identification System Using
Time Division Multiple Access in the VHF Maritime Mobile Frequency
Band, document Recommendation ITU-R M.1371-5, ITU-R Radiocommunication Sector of the International Telecommunication Union, 2014.
[Online]. Available: https://www.itu.int/rec/R-REC-M.1371-5-201402-I
[27] T. Eriksen, G. Høye, B. Narheim, and B. J. Meland, “Maritime traffic monitoring using a space-based AIS receiver,” Acta Astronautica,
vol. 58, no. 10, pp. 537–549, May 2006.
[28] A. N. Skauen, “Quantifying the tracking capability of space-based AIS
systems,” Adv. Space Res., vol. 57, no. 2, pp. 527–542, Jan. 2016.
[29] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training
of deep bidirectional transformers for language understanding,” in Proc.
Conf. North Amer. Chapter Assoc. Comput. Linguistics (NAACL), 2019,
pp. 4171–4186.

BERNABÉ et al.: DETECTING INTENTIONAL AIS SHUTDOWN IN OPEN SEA MARITIME SURVEILLANCE

[30] A. Dosovitskiy et al., “An image is worth 16×16 words: Transformers
for image recognition at scale,” in Proc. ICLR, 2020, pp. 1–21.
[31] S. Li et al., “Enhancing the locality and breaking the memory bottleneck
of transformer on time series forecasting,” in Proc. Adv. Neural Inf. Syst.
(NeurIPS), vol. 32, 2019, pp. 1–11.
[32] B. Lim and S. Zohren, “Time-series forecasting with deep learning:
A survey,” Phil. Trans. Roy. Soc. A: Math., Phys. Eng. Sci., vol. 379,
no. 2194, 2021, Art. no. 20200209.
[33] D. Bahdanau, K. Cho, and Y. Bengio, “Neural machine translation by
jointly learning to align and translate,” 2016, arXiv:1409.0473.
[34] S. Hochreiter and J. Schmidhuber, “Long short-term memory,” Neural
Comput., vol. 9, no. 8, pp. 1735–1780, Nov. 1997.
[35] A. Vaswani et al., “Attention is All you Need,” in Proc. Adv. Neural Inf.
Syst. (NeurIPS), 2017, pp. 1–11.
[36] J. Cheng, L. Dong, and M. Lapata, “Long short-term memory-networks
for machine reading,” in Proc. Conf. Empirical Methods Natural Lang.
Process., 2016, pp. 1–11.
[37] J. Quinonero-Candela, M. Sugiyama, A. Schwaighofer, N. D. Lawrence,
M. I. Jordan, and T. G. Dietterich, Eds., Dataset Shift in Machine
Learning (Neural Information Processing Series). Cambridge, MA,
USA: MIT Press, 2008.

Pierre Bernabé is currently pursuing the Ph.D.
degree with the Simula Research Laboratory, Oslo,
Norway. He is also affiliated with University
Bourgogne Franche Comté (UBFC). His current
research interests include the application of machine
learning techniques to support maritime surveillance
by detecting anomalies in AIS communications.

Arnaud Gotlieb is currently the Chief Research Scientist with the Simula Research Laboratory, Norway.
He has coauthored more than 120 publications
in artificial intelligence and software engineering
and developed several tools for testing critical
software systems. His current research interests
include the application of artificial intelligence to the
validation of software-intensive systems and cyberphysical systems, including industrial robotics and
autonomous systems.

1177

Bruno Legeard is currently a Professor with the
Institut FEMTO-ST, UBFC, and the Scientific Advisor and the Co-Founder of Smartesting. He has
more than 20 years of expertise in model-based
testing/model-based security testing (MBT/MBST)
and its introduction in the industry. He is the author
of three books disseminating Model-Based Testing in
the industry and the Practical Model-Based Testing
has more than 1200 citations. His current research
interests include the automation of model-based test
case generation using AI techniques. His research
results in more than 100 scientific and industrial publications based on MBT
and MBST.

Dusica Marijan is currently a Senior Research
Scientist with the Simula Research Laboratory,
Oslo, Norway. Prior to the Simula Research
Laboratory, she was a Senior Software Engineer
with the Consumer Electronics Industry. Her current
research interests include software engineering,
with a focus on improving software quality with
artificial intelligence techniques.

Frank Olaf Sem-Jacobsen was born in Norway
in 1979. He received the Ph.D. degree in computer science from the University of Oslo, Norway,
with a focus on fault tolerance in high-performance
interconnection networks (both intra-datacenter and
on-chip). After a period as a Post-Doctoral Fellow
with Simula Research Laboratory, he joined Space
Norway/Statsat as a Systems Engineer. In this position, he has built the Mission Control Centre used
to control the now five government-owned small
satellites that gather AIS data around the world 24/7.

Helge Spieker is currently a Research Scientist
with the Simula Research Laboratory, Oslo, Norway.
His current research interests include the application
and validation of machine learning and artificial
intelligence techniques.
PAPER_TEXT
