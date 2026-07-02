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
# [769] OIPR: Evaluation for Time-Series Anomaly Detection Inspired by Operator Interest
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
编号：769
题名：OIPR: Evaluation for Time-Series Anomaly Detection Inspired by Operator Interest
年份：2025
DOI：10.1109/tdsc.2025.3638405
来源：IEEE Transactions on Dependable and Secure Computing
PDF：paper/10.1109_TDSC.2025.3638405.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 10
已有代码状态：已下载；OIPR -> source\OIPR

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\769.txt
- 原始字符数：61671
- 本次发送字符数：61671
- 是否截断：False

代码包：
- 仓库：OIPR
  - URL：https://github.com/weatherjyh/OIPR
  - 状态：downloaded
  - 本地目录：source\OIPR
  - 顶层结构：.gitignore、OIPR.py、README.md、adversary_algorithms.py、config.yaml、datasets/、evaluation_methods.py、test_exp.py
  - 主要语言：Python:4、YAML:1
  - README 标题：OIPR、OIPR、OIPR
  - README 运行线索：
  - 关键文件：{"评估/测试入口": ["evaluation_methods.py", "test_exp.py"], "配置文件": ["config.yaml"]}
  - 数据集线索：dapt、tor

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

3571

OIPR: Evaluation for Time-Series Anomaly
Detection Inspired by Operator Interest
Yuhan Jing , Jingyu Wang, Senior Member, IEEE, Lei Zhang , Haifeng Sun , Senior Member, IEEE,
Bo He , Member, IEEE, Zirui Zhuang , Member, IEEE, Chengsen Wang , Qi Qi , Senior Member, IEEE,
and Jianxin Liao , Senior Member, IEEE

Abstract—With the growing adoption of time-series anomaly
detection (TAD) technology, numerous studies have employed deep
learning-based detectors to analyze time-series data in the fields of
Internet services, industrial systems, and sensors. The selection and
optimization of anomaly detectors strongly rely on the availability
of an effective evaluation for TAD performance. Since anomalies in
time-series data often manifest as a sequence of points, conventional
metrics that solely consider the detection of individual points are
inadequate. Existing TAD evaluators typically employ point-based
or event-based metrics to capture the temporal context. However,
point-based evaluators tend to overestimate detectors that excel
only in detecting long anomalies, while event-based evaluators are
susceptible to being misled by fragmented detection results. To
address these limitations, we propose OIPR (Operator Interestbased Precision and Recall metrics), a novel TAD evaluator with
area-based metrics. It models the process of operators receiving
detector alarms and handling anomalies, utilizing area under the
operator interest curve to evaluate TAD performance. Furthermore, we build a special scenario dataset to compare the characteristics of different evaluators. Through experiments conducted
on the special scenario dataset and five real-world datasets, we
demonstrate the remarkable performance of OIPR in extreme and
complex scenarios. It achieves a balance between point and event
perspectives, overcoming their primary limitations and offering
applicability to broader situations.

Received 10 February 2025; revised 15 November 2025; accepted 20 November 2025. Date of publication 27 November 2025; date of current version 12
March 2026. This work was supported in part by the National Key R&D Program
of China under Grant 2024YFE0200800, in part by the National Natural Science
Foundation of China under Grant 62471055, Grant U23B2001, Grant 62321001,
Grant 62401080, Grant 62101064, Grant 62171057, Grant 62201072, and Grant
62071067, in part by the High-Quality Development Project of the MIIT under
Grant 2440STCZB2584, in part by the Ministry of Education and China Mobile
Joint Fund under Grant MCM20200202 and Grant MCM20180101, in part by
the China Postdoctoral Science Foundation under Grant 2023TQ0039, Grant
2024M750257, and Grant GZC20230320, in part by the Fundamental Research
Funds for the Central Universities under Grant 2024PTB-004, and in part by
the 2025 Education and Teaching Reform Project Funding at Beijing University
of Posts and Telecommunications under Grant 2025YZ005. (Yuhan Jing and
Jingyu Wang contributed equally to this work.) (Corresponding authors: Lei
Zhang; Bo He.)
Yuhan Jing, Jingyu Wang, Haifeng Sun, Bo He, Zirui Zhuang, Chengsen
Wang, Qi Qi, and Jianxin Liao are with the State Key Laboratory of
Networking and Switching Technology, Beijing University of Posts and
Telecommunications, Beijing 100876, China (e-mail: jingyh@bupt.edu.cn;
wangjingyu@bupt.edu.cn; hfsun@bupt.edu.cn; hebo@bupt.edu.cn; zhuang
zirui@bupt.edu.cn; cswang@bupt.edu.cn; qiqi8266@bupt.edu.cn; liaojx
@bupt.edu.cn).
Lei Zhang is with China United Network Communications Company Ltd.,
Beijing 100033, China (e-mail: zhangl83@chinaunicom.cn).
The implementation of the proposed evaluator and the special scenario dataset
are available at https://github.com/weatherjyh/OIPR.
Digital Object Identifier 10.1109/TDSC.2025.3638405

Index Terms—Time-series, anomaly detection, evaluation,
precision and recall.

I. INTRODUCTION
IME-SERIES anomaly detection (TAD) [1], [2], [3] refers
to the detection of a series of points with temporal continuity to identify time points or ranges that deviate from normal
patterns. TAD is of significant importance in various fields,
including fault detection and troubleshooting in industrial systems [4], [5], Internet services [6], [7], [8], sensors [9], [10], [11],
[12]. Detectors used for anomaly detection can be supervised or
unsupervised, with their performance typically evaluated using
manually annotated labels. Operators compare the detector output with the ground truth labels and calculate one or more metrics
to evaluate TAD performance. In the context of binary classification, classical point-wise metrics (PW) such as precision,
recall, receiver operating characteristic (ROC) curve, and area
under the ROC curve (AUROC) are commonly employed for
performance evaluation of general anomaly detection tasks [13],
[14]. In point-wise metrics, precision indicates the proportion
of correctly identified positive points among all points predicted
as positive, while recall represents the proportion of accurately
predicted positive points relative to the total number of actual
positive points.
However, due to the continuity of time-series data, large
Internet companies commonly employ event-based metrics for
data analysis. For instance, within MAXIMO,1 the enterprise
asset management system of IBM, the metrics of mean time
to repair (MTTR) and mean time between failure (MTBF) are
essential for assessing the availability and reliability of the
system. They focus on capturing the frequency, duration, and
recovery of each failure, signifying that ongoing events, rather
than isolated time points, are regarded as the fundamental unit in
maintenance operations. Therefore, researchers have recognized
that the classical PW metrics are inadequate for TAD evaluation,
as they treat each time point as an individual unit, failing to
account for the temporal continuity of anomaly events. In recent
years, improved TAD evaluators [15], [16], [17] have been
proposed that take into account the continuity of time-series,
which can be broadly classified into two categories: point-based
and event-based evaluators. Point-based evaluators treat each
anomaly point as equal, with specific predicted points adjusted

T

1 https://www.ibm.com/topics/mttr

1545-5971 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

3572

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

Fig. 1. An example highlighting the distinction between point-based and
event-based perspectives, comparing three different detectors d1 , d2 , and d3
for the same ground truth.

TABLE I
EVALUATION RESULTS (PRECISION/RECALL/F1-SCORE) OF THE EXAMPLE IN
FIG. 1 USING PA, TAPR, AND OIPR(OURS), RESPECTIVELY

to account for the temporal context. Meanwhile, event-based
evaluators evaluate TAD performance based on anomaly events,
regardless of their durations. To illustrate the distinctions between the point-based and event-based evaluators, we present
an example in Fig. 1, where three different detectors are applied
to the same ground truth gt. Detector d1 detects the longest
anomaly event a1 using one complete prediction event p1 ; detector d2 detects two shorter anomaly events, a2 and a3 ; detector
d3 detects a1 using 3 fragmented prediction events (p6 , p7 , p8 ).
Additionally, each of d1 , d2 , and d3 contains one false positive
event, which are p2 , p5 , and p9 , respectively.
The evaluation results of the example in Fig. 1 using different
evaluators are shown in Table I. In these results, the PA evaluator [18], a typical representative of point-based evaluators,
considers d1 and d3 much superior to d2 . This indicates that
point-based evaluators focus only on the number of anomaly
points rather than the number of anomaly events. In contrast,
event-based evaluators, such as TaPR [19], treat each anomaly
event as equivalent. In terms of recall, it assesses that d3 performs
slightly worse than d1 , due to its incomplete coverage of event
a1 . d2 is considered superior because it detects more anomaly
events. However, in terms of precision, TaPR yields counterintuitive results: it regards d3 as having up to 3 correctly detected
events, thus giving d3 a significantly higher precision than
d1 (0.75vs. 0.5). The characteristic of precision misleading of
event-based evaluators regarding fragmented prediction events
proves that merely focusing on event equivalence may lead to
distorted evaluation conclusions.
To overcome the above limitations of point-based and eventbased evaluators, we propose a novel TAD performance evaluator, named OIPR (Operator Interest-based Precision and Recall
metrics). In the example shown in Fig. 1, OIPR’s evaluation
results indicate that d1 (which detects more anomaly points)
and d2 (which detects more anomaly events) are two competitive
detectors, with d1 holding only a slight advantage. Meanwhile,
OIPR is not affected by the precision misleading caused by
fragmented prediction events and therefore regards d1 and d3
to have similar performance. This perspective of balancing

duration and quantity enables OIPR to be applicable to a wider
range of practical scenarios. Additionally, we provide an artificial dataset containing nine special scenarios to analyze the
characteristics of different evaluators under diverse boundary
conditions. Experiments are also conducted on five real-world
datasets to investigate the efficacy of different evaluators in
complex practical scenarios.
The main contributions of this work are as follows:
r We propose a novel TAD evaluator that models the dynamic changes in operator interest while monitoring the
time-series data and responding to detector alarms in
real-world scenarios. It addresses the challenges posed by
long anomaly events and fragmented detection results, and
innovatively calculates precision and recall using the area
under the operator interest curve.
r We establish a special scenario dataset that allows for a
comprehensive analysis of characteristics of various TAD
evaluators under diverse boundary conditions. This dataset
serves as a valuable research material for future investigations of TAD performance evaluation.
r We conduct experiments on five real-world datasets using
both representative and adversary detectors. The results
indicate that OIPR outperforms the baseline evaluators, exhibiting fewer limitations and greater applicability across
a variety of real-world scenarios.
II. RELATED WORK
A. Time-Series Anomaly Detection
Anomalies in time-series datasets come from various sources,
resulting in distinct anomaly characteristics. For instance, external attacks can lead to service interruptions, often shown
as abrupt time-series fluctuations [20]. Additionally, hardware
failures, such as hard drive failures or network device outages, can cause a significant decline in system performance,
resulting in sustained deterioration of associated indicators [21].
Furthermore, the deployment or changes of services can induce variations in the corresponding key performance indicators
(KPIs) over time, potentially triggering a series of consecutive or
intermittent anomaly points [22]. In terms of duration, anomalies
can manifest at specific time points or persist across a sequence
of consecutive time points [23]. The latter is referred to as an
anomaly event that encompasses multiple anomaly points.
Typical techniques for TAD encompass a range of approaches,
including statistical [24], machine learning [25], and deep learning [18], [26] algorithms. Time-series data are generally collected at regular intervals from various agents or sensors, with
each time point representing a distinct sample. The detection
results generated by the anomaly detector maintain the same
discreteness and sampling frequency as the input data. After the
process of detection, the discrete results can be systematically
organized into prediction events based on temporal continuity,
and compared with the ground truth labels to evaluate the performance of TAD. However, establishing a reliable mapping
between the ground truth anomaly events and the detection
results presents notable challenges. Specifically, temporal factors such as incorrect insertions, deletions, fragmentation, and
merging [27] introduce significant ambiguities into the mapping

JING et al.: OIPR: EVALUATION FOR TIME-SERIES ANOMALY DETECTION INSPIRED BY OPERATOR INTEREST

relationships, thereby complicating the evaluation of TAD performance.
B. Existing TAD Evaluators
Classical PW evaluator using point-based precision/recall
(P/R) metrics has been employed in the evaluation of
conventional TAD tasks [13], [14]. However, recent studies have
underscored the significance of considering the temporal continuity inherent in time-series data, leading to the development of
specialized evaluators. The PA evaluator was initially introduced
in [18], which operates on the premise that if at least one point
within an anomaly event is detected, the entire anomaly event
is deemed successfully identified. Based on this, the evaluator
of PA% K [15] was proposed, which stipulates that a minimum
proportion of points must be detected within a ground truth event
to be classified as successfully detected. Both PA and PA% K
calculate their precision and recall metrics (P/R) based on the
number of anomaly points, similar to PW.
Different from point-based evaluators, event-based evaluators
treat each continuous anomaly interval (i.e., anomaly event) as a
single unit. The RP/RR evaluator [16] introduced factors of existence, size, position, and cardinality for the detection of anomaly
events, supporting customizable functions or parameters for
each factor. Meanwhile, TaPR [19] addressed the challenge of
ambiguous labeling by evaluating each ground truth event or
prediction event through a combination of detection scores and
portion scores. Both RP/RR and TaPR regarded each ground
truth event as equally significant, irrespective of its duration.
This principle is similarly applied to prediction events. Subsequently, the precision and recall metrics are averaged across the
ground truth or prediction events. Another event-based evaluator, the affiliation metrics (AM) [23], provided an alternative
perspective in which each ground truth event is considered equal,
but the predicted results are assigned, measured in points, to the
affiliation zone of the nearest ground truth event. The metrics of
precision and recall are then averaged across the ground truth
events.
C. Summary
Depending on specific focuses and assumptions, the aforementioned point-based and event-based evaluators will probably
generate misleading results in certain extreme scenarios. These
scenarios are typically characterized by long anomaly events or
fragmented detection results, which restricts the applicability
of evaluators [28]. In this study, we propose a comprehensive
TAD evaluator based on the operator interest to aid operators
in selecting more effective detectors for practical applications,
and demonstrate its robust performance on the special scenario
dataset and five real-world datasets.
III. MOTIVATION
A. Problem Formulation
The problem of TAD and its evaluation can be formally
articulated as follows: Given a time-series spanning T time
points, denoted as x = {x0 , x1 , . . ., xT −1 }, the corresponding

3573

ground truth labels are represented as y = {y0 , y1 , . . ., yT −1 },
where yt ∈ {0, 1} denotes whether the time-series is anomalous
(1) or not (0) at time point t. For a specific anomaly detector, the
detection results are denoted as ŷ = {ŷ0 , ŷ1 , . . ., ŷT −1 }.
The classical PW evaluator evaluates the TAD performance
by calculating three primary metrics: precision (P), recall (R),
and f1-score (F1). These metrics are defined as follows:
TP
2·P ·R
TP
, R=
, F1 =
, (1)
TP + FP
TP + FN
P +R
where TP, FP, and FN represent the number of true positive,
false positive, and false negative points, respectively. Other
specialized TAD evaluators typically adopt the P/R format, with
different solutions for precision and recall metrics. Finally, the
f1-score metric is calculated as outlined in (1).
P =

B. Limitations of Existing Evaluators
1) Long Anomaly Effect: As a distinctive binary classification task, TAD prompts researchers to develop specialized evaluators that take into account the temporal continuity of events.
In this context, the existence detection of a greater number of
anomaly events, rather than detecting more individual anomaly
points, has become the primary consideration for operators.
However, in point-based evaluators, the significance attributed
to anomaly events is proportional to the number of points they
encompass. As a result, a limited number of long anomalies
can overshadow the influence of a larger quantity of shorter
anomalies in the final evaluation outcomes. To demonstrate the
impact of the long anomaly effect, we employ two straightforward adversary detectors, one of which is designated as the
first point detector, denoted as df p . It is specifically designed
to identify only the initial point of each ground truth event.
During periods without any ground truth anomalies, the output
of df p consistently remains at 0. While the first point detector
successfully identifies the existence of every anomaly event, it
lacks the ability to discern the durations of these anomalies.
Another adversary detector, referred to as the long anomaly
detector dl (L), is designed to identify the ground truth events
within a given time-series that have a duration of at least L.
Specifically, dl (L) correctly detects all points that fall within
the long ground truth events, while producing an output of 0
for all other time points. Although the long anomaly detector is
effective in identifying anomaly events with long durations, it
fails to detect the other shorter events.
For demonstration purposes, we extract a slice from the SMD
dataset [2], using both df p and dl for anomaly detection, as
illustrated in Fig. 2. Among them, df p accurately reports the
occurrence of all thirteen anomaly events, which is significant
for operators. In contrast, dl detects only three of these anomaly
events. If it is deployed for fault detection in a service, operators
will miss the opportunity to recognize these short anomaly
events. Within the point-based evaluators, PW and PA% K fail to
reflect this risk. As demonstrated in Table II, dl achieves a high
f1-score of 0.848 using both evaluators, while df p attains a significantly low f1-score of 0.371. This discrepancy arises because
dl detects a greater number of anomaly points compared to df p .
In contrast, PA exhibits a distinct behavior of overestimation. It

3574

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

Fig. 2. A demonstration scenario which displays 5 adversary detectors, including the first point detector df p , the long anomaly detector dl , the dispersed
disturbance detector ddisp , the aggregated disturbance detector daggr , and the continuous disturbance detector dcont .

TABLE II
F1-SCORES OF THE DEMONSTRATION IN FIG. 2 USING DIFFERENT
EVALUATORS. BOLD TEXT MEANS THE HIGHEST F1-SCORE IN EACH GROUP

adjusts the detection result of df p to an ideal detector (whose
outputs perfectly match the ground truth), even though it does
not actually detect the duration of any event comprising more
than one point.
Event-based evaluators, such as RP/RR, TaPR, and AM, are
not impacted by the long anomaly effect. Their evaluation results
for the detectors primarily depend on the number of anomaly
events they detect, and df p is evaluated to be much better than
dl , as demonstrated in Table II.
2) Fragmentation Effect: Although using an event-based
evaluator can avoid the impact of the long anomaly effect,
we have observed another misleading phenomenon, called the
fragmentation effect, which stems from the discrete nature of
the detection results. In instances where a ground truth event
comprises a series of points, the detector is likely to identify
only a subset of points that exhibit significant deviations from
the normal pattern [15]. Consequently, a contiguous event can
be fragmented into multiple events in the detection results. The
fragmentation effect leads to an increase in the number of true
positive events, despite the fact that the successful detection is
confined to a single original contiguous event. This phenomenon
can also arise when the detector experiences a short-term, onetime disturbance, such as during a service deployment or change.
In such cases, the detector is prone to generating a high frequency
of false positive points, leading to multiple fragmented false
positive events that originate from the same underlying cause.
To empirically illustrate the fragmentation effect, we introduce
three specific disturbances to the ideal detector, as depicted in
Fig. 2:
Dispersed disturbance detector ddisp : To simulate the interference induced by random noise, we generate a set of FP

points, constituting 1% of the entire time-series, which are then
randomly inserted throughout the detection results.
Aggregated disturbance detector daggr : To simulate the shortterm, intermittent disturbances associated with the deployment
or change of the service, we randomly introduce a set of FP
points, comprising 1% of the entire time-series, into the initial
3% of the detection results.
Continuous disturbance detector dcont : The initial 3% of the
detection results is configured to a value of 1 to simulate a
short-term, continuous disturbance scenario resulting from the
deployment or change of service.
In the above three cases, both daggr and dcont require operators to monitor system status for a period following initialization.
During subsequent long-term operation, the detector is highly
reliable. In contrast, ddisp poses a significant challenge for
operators due to its persistent and recurrent generation of false
alarms, which ultimately results in resource wastage. As a result,
ddisp leads to a more significant decrease in the practical utility
of the detector.
As illustrated in Table II, the point-based evaluators, namely
PW, PA, and PA% K, consider dcont as the worst-performing
detector due to its highest number of false positive points,
without taking into account that these points originate from the
same anomaly event. In contrast, the event-based evaluators,
RP/RR and TaPR, suggest that both daggr and ddisp exhibit
similar poor performance, even though all false positive points
in daggr are concentrated within a limited period following
initialization. Another evaluator that is partially event-based,
AM, remains unaffected by the fragmentation effect due to its
exclusive adoption of an event-based perspective for the ground
truth, rather than for the detection results.
C. Towards Universal TAD Evaluation
By means of the adversary detectors and demonstration outlined in the last section, we have elucidated the limitations of
point-based and event-based evaluators. In pursuit of developing
a more universally applicable TAD evaluator, we have established two primary objectives:
Existence detection reward: The key difference between TAD
and conventional binary classification tasks lies in the continuity
of events. A universally applicable TAD evaluator should possess the capability to reward the existence detection of ground

JING et al.: OIPR: EVALUATION FOR TIME-SERIES ANOMALY DETECTION INSPIRED BY OPERATOR INTEREST

3575

Algorithm 1: Online Calculation Process of the Operator
Interest Curve for the Detection Results.
Input: the detection results ŷ = {ŷ0 , ŷ1 , . . . , ŷT −1 }, and
the pre-configured parameters ldis , lobs and bdur .
Output: the operator interest Iˆ for the detection results ŷ.
(T +lobs ) zeros

1:
2:
3:
4:
5:
6:
7:
8:
9:
10:
11:
12:
13:
14:
15:
16:
17:
18:
19:
20:
21:
22:
23:
24:
25:
26:




Iˆ ← {0, 0, . . . , 0}
pstart ← −lobs − 1
pend ← −lobs − 1
t←0
while t < T do
if ŷt = 1 then
if t − pend > lobs then
pstart ← t
end if
Iˆt ← ω(t − pstart )
pend ← t
else
if t − pend ≤ lobs then
Iˆt ← ω(t − pstart ) · γ(t − pend )
end if
end if
t←t+1
end while
while t < T + lobs do
if t − pend ≤ lobs then
Iˆt ← ω(t − pstart ) · γ(t − pend )
end if
t←t+1
end while
Iˆ ← {Iˆ0 , Iˆ1 , . . . , IˆT −1+lobs }
returnIˆ

Fig. 3. An example of the operator interest curve for an individual continuous
anomaly event.

In computer science, LSTM [30] implements similar attenuation
logic via gating mechanisms. Transformer [31] achieves attention attenuation through scaled dot production: computes the
input sequence correlation similarity, converts this to attention
weights, and forms a data-driven dynamic attenuation process.
In this paper, we propose the operator interest curve to simulate
the attention changes of operators when monitoring anomaly
alarms, which consists of three phases: (i) Discovery phase:
The operator receives alarms and confirms the presence of an
anomaly; (ii) Duration phase: Alarms persist and the operator
takes responsive measures; (iii) Observation phase: The anomaly
is resolved through maintenance (with the alarms ceased), and
the operator continues monitoring to ensure fault recovery.
Based on the operator interest curve, we further propose a
TAD evaluator, which offers an existence detection reward and
enables the merging of potentially fragmented events.
IV. METHODOLOGY
A. Operator Interest Curve

truth events. Specifically, the first point to detect the existence
of an anomaly event should receive a higher reward than using
the classical PW evaluator.
Fragments Merging: Given that time points serve as the
fundamental units for the collection of time-series data, the
detection results inherently exhibit a discrete nature. Therefore,
a universal TAD evaluator should take into account the potential merging of fragmented events and effectively differentiate
between dispersed and aggregated anomaly points.
In addition to the above two objectives, it is also advisable
for a universal evaluator to incorporate several other beneficial
characteristics, such as addressing ambiguous labeling [19] and
providing early detection reward [16]. Further exploration of
evaluator characteristics will be discussed in the context of
special scenario dataset experiments in Section IV.
To develop a more universally applicable TAD evaluator, we
draw inspiration from the dynamic attention behavior of operators during the monitoring of anomaly alarms. In the 1960 s,
American psychologist A. M. Treisman proposed the attention
selection theory and the attention attenuation model [29], which
posits that unattended information is not completely blocked;
instead, its intensity is reduced through an attenuation device.

In this section, we outline the methodology employed to
derive the operator interest curve for TAD, which captures the
dynamics of operators in discovering and handling anomalies.
To construct the operator interest curve, we propose a set of
functions, denoted as Φ(i), which characterize the phases of discovery, duration, and observation associated with an individual
anomaly event:
⎧
ω(i), 0 ≤ i < ldis + ldur
⎪
⎪
⎨
ω(ldis + ldur ) × γ(i − ldis − ldur + 1),
, (2)
Φ(i) =
ldis + ldur ≤ i < ldis + ldur + lobs
⎪
⎪
⎩
0, i ≥ ldis + ldur + lobs
where i represents the distance from the current point to the
initial point of the anomaly event. ldis , ldur and lobs represent
the lengths of the discovery, duration, and observation phases,
respectively. The discovery phase and the duration phase of the
anomaly event are characterized by a shared continuous interest
function ω(·), while γ(·) represents the operator interest for
the observation phase. In Fig. 3, we present an example of the
operator interest curve for a continuous event: starting from the
first anomaly point reported by the detector, Φ(i) jumps from 0
to 1. This indicates that the operator devotes the highest level of
interest to the newly detected anomaly event; then, the level of

3576

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

interest decreases within the length of the discovery phase until
transitioning to the duration phase, signifying that the operator
shifts from receiving alarm information to conducting anomaly
troubleshooting. During the duration phase, the operator maintains interest in the anomaly event and conducts troubleshooting.
Thus, the value of Φ(i) remains nearly unchanged with only a
slight decrease. Finally, when the anomaly event is resolved and
the detector stops reporting alarms, the monitoring enters the
observation phase. At this stage, Φ(i) decreases continuously
from its value at the end of the duration phase until it reaches
0, indicating that the operator continues to monitor the system
for a period after the alarm ceases to ensure the recovery of the
anomaly event.
As a default approach, we employ a reversed and scaled
sigmoid function for ω(·):
ω(i) =

1, i = 0
bdur +(1−bdur )×

1−sigmoid( l 10 i−5)
dis

1−sigmoid(−5)

, i>0

,

(3)

where sigmoid(x) = 1+e1( −x) . The operator interest decreases
from 1 to near bdur throughout the discovery phase and remains
nearly constant at bdur during the duration phase. Here, bdur
denotes the lower boundary of operator interest for the discovery
and duration phases. The rate of decrease is determined by the
configuration of ldis , which is set by default to 1/4 of the average
length of ground truth events, rounded up to the nearest integer.
The interest function for the observation phase, γ(i), is calculated according to (4):
⎧
⎪
⎨1, i = 0
1−sigmoid( l 10 i−5)
obs
γ(i) =
(4)
, 0 < i ≤ lobs .
⎪
⎩ 1−sigmoid(−5)
0, i > lobs
The rate of decline is determined by the parameter lobs ,
where a shorter lobs leads to a more rapid reduction during the
observation phase. Typically, the default value of lobs is set to
the average length of ground truth events.

Fig. 4.
events.

An example of the operator interest curve for fragmented anomaly

the anticipated troubleshooting process of the ideal detector and
serves as a benchmark for evaluation.
C. Precision and Recall Metrics in OIPR
The precision and recall metrics in OIPR are derived using
the operator interest curves. In this work, conventional number
of true positive points is replaced with the true positive area
T Poi , which measures the overlapping area between the operator
interest curve of the ground truth, I, and that of the detection
ˆ Likewise, the number of predicted positive points
results, I.
ˆ Therefore, the values for true
is replaced as the area under I.
positive area T Poi and false positive area F Poi in OIPR are
defined as:
(5)

ˆ − T Poi ,
F Poi = AUC(I)

(6)

where AUC(·) refers to the computation of the area under a
specific curve, while min(·) indicates the selection of the smaller
value between two time-series at each time point to generate
a new sequence. Subsequently, the precision metric in OIPR,
denoted as Poi , is defined as:
Poi =

B. Merging Fragmented Anomaly Events
In the previous section, we introduced the operator interest
curve for an individual continuous anomaly event. However,
it is essential to recognize that the prediction events can be
fragmented. To address this issue, we propose a forward process
for the online calculation of the operator interest curve, which
is detailed in Algorithm 1.
Fig. 4 presents an example of the operator interest curve for
fragmented anomaly events. Temporary interruptions in reporting anomaly points result in a decline in the operator interest,
though it does not drop to 0 immediately. If new anomaly points
are reported within lobs , the fragmented anomaly events are
merged. Conversely, if a new anomaly point is reported after the
end of the last observation phase, it is classified as the initiation
of a distinct individual anomaly event.
Using the same methodology as outlined in Algorithm 1, we
derive the operator interest curve of the ground truth labels,
ˆ While the ground truth labels are not affected by
denoted as I.
the fragmentation effect, its operator interest curve represents

ˆ ,
T Poi = AUC min(I, I)

ˆ
T Poi
AUC(min(I, I))
.
=
ˆ
T Poi + F Poi
AUC(I)

(7)

Using a similar methodology, we transform the ground truth
positive points to the area under I. Thus, the false negative area
F Noi is calculated as follows:
F Noi = AUC(I) − T Poi .

(8)

The recall metric in OIPR, denoted as Roi , is defined as:
Roi =

ˆ
T Poi
AUC(min(I, I))
.
=
T Poi + F Noi
AUC(I)

(9)

In addition, we present a visual illustration in Fig. 5 to demonstrate the AUC calculation range in OIPR, with areas for T Poi ,
F Poi , and F Noi indicated separately.
V. EXPERIMENTS
A. Experimental Setup
Baseline TAD evaluators: We conducted a comparative analysis against six baseline evaluators and OIPR in the context

JING et al.: OIPR: EVALUATION FOR TIME-SERIES ANOMALY DETECTION INSPIRED BY OPERATOR INTEREST

3577

TABLE IV
DESCRIPTIONS OF REAL-WORLD DATASETS

Fig. 5. Visualization of the overlapping area of operator curves, corresponding
to T Poi , F Poi , and F Noi .

TABLE III
PARAMETERS EMPLOYED IN THE EXPERIMENTS. La MEANS THE AVERAGE
LENGTH OF THE GROUND TRUTH EVENTS WITHIN THE DATASET

spacecraft telemetry, web services, water treatment, environmental sensors, city traffic, and real production data.
Descriptions for each dataset are listed in Table IV.
B. Experimental Results

of TAD evaluation. The baselines include three point-based
evaluators: the classical point-wise evaluator PW, the point
adjustment evaluator PA [18], and the top-k point adjustment
evaluator PA% K [15]. In addition, three event-based evaluators
are also included: the range-based TAD evaluator RP/RR [16],
the time-series aware evaluator TaPR [19], and the affiliation
evaluator AM [23]. The parameters employed for experiments
are summarized in Table III.
Datasets: The experiments are conducted on a special scenario dataset and five real-world datasets.
r Special scenario dataset. We have constructed an artificial
dataset consisting of 24 evaluator-sensitive cases specifically designed for the evaluation of TAD. These cases are
categorized into 9 distinct scenarios, each crafted to emphasize one or two evaluator characteristics. By leveraging
the special scenario dataset, we can effectively demonstrate
the limitations of various evaluators in a clear and concise
manner.
r Real-world datasets. The real-world datasets we used for
experiments consists of data among various fields, such as

1) Experimental Results on the Special Scenario Dataset:
In this section, we present several significant qualitative conclusions derived from experiments on the special scenario dataset,
with the results shown in Table V. The evaluator characteristics involved in these qualitative conclusions include the existence detection reward and fragments merging mentioned in
Section III-C, as well as several additional ones:
r Overlapping proportion awareness: For a specific ground
truth event, a detector that identifies a greater proportion
of anomaly points within it should be awarded a higher
recall reward. This characteristic encourages the detector
to identify as many points as possible within a single
ground truth event, thereby improving the accuracy of event
duration reporting.
r Addressing ambiguous labels: The manual labeling process introduces ambiguity in defining anomaly event
boundaries, resulting in anomalies affecting points before
or after the ground truth event. Detecting these ambiguous points indicates a partial success in identifying the
anomaly. Consequently, evaluators that address ambiguous
labels should reward recall for these points.
r Early detection reward: It encourages detectors to identify
anomalies early in the occurrence of the ground truth
events, thereby improving the detection timeliness.
r Fragmentation misleading in precision: This misleading
characteristic is present in several event-based evaluators.
Detectors identifying a ground truth event through multiple
fragmented events can achieve higher precision scores
than those detect using a complete event. This discrepancy

3578

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

TABLE V
QUALITATIVE CONCLUSIONS DERIVED FROM EXPERIMENTS ON THE SPECIAL SCENARIO DATASET. BENEFICIAL CHARACTERISTICS OF THE EVALUATOR ARE
MARKED WITH (PRESENT) AND × (ABSENT). MISLEADING CHARACTERISTICS ARE INDICATED BY ◦ (PRESENT) AND - (ABSENT)

Fig. 6.

Demonstrations of TAD results on several real-world datasets.

primarily arises from the misleading increase in the count
of true positive events.
r Long anomaly misleading: This misleading characteristic is present in most point-based evaluators, where the
significance of long anomalies far surpasses that of short
anomalies. Consequently, detectors that identify more
short anomalies may be outperformed by those that focus
solely on long anomalies, hindering the detection of a more
diverse range of anomalies.
r Sparse anomaly misleading: A pitfall observed in the AM
evaluator. The f1-score is overestimated due to the mapping
from long absolute distance to limited relative precision
and recall distances.
A comprehensive introduction and detailed experimental results pertaining to the special scenario dataset are presented in
Appendix A, available online. Among the above characteristics,
OIPR effectively incorporates all beneficial factors while minimizing potential misleading influences. Compared to baseline
point-based and event-based evaluators, it offers enhanced universality and reduces deficiencies in extreme scenarios.
2) Experimental Results on Real-World Datasets: First, we
obtain the TAD results of three advanced detectors, Autoformer [39], DLinear [40], and Timesnet [41], on all real-world

datasets. These results are evaluated using different evaluators
and ranked by f1-score, as presented in Table VI. Inappropriate
evaluators may affect the ranking of detectors due to either the
lack of beneficial characteristics or the presence of misleading
ones. In Table VI, we uniformly mark the relevant characteristics where inappropriate evaluators yield misleadingly overestimated rankings. Corresponding demonstrations are provided
in the four subplots of Fig. 6. Point-based evaluators (PW, PA,
PA% K) are mainly affected by the characteristic of long anomaly
misleading, thus overestimating the ranking of Timesnet on the
MSL, SMAP, PSM, and SWaT datasets. In these experiments,
Timesnet generates more FP points than the other two detectors,
severely compromising its detection performance, as shown in
Fig. 6(a) and (c). Point-based evaluators fail to attach sufficient
importance to this flaw and instead prioritize the detection of
long anomaly events, thereby leading to an overestimated ranking of Timesnet. On the IOPS dataset, Autoformer misses more
anomaly events than DLinear, as shown in Fig. 6(b). However,
due to the lack of existence detection reward, the PW and PA% K
evaluators do not prominently reflect these missed detections in
the recall metric, resulting in the overestimated ranking of Autoformer. Moreover, the lack of fragment merging characteristic of
event-based evaluators (RP/RR, TaPR, and AM) was evident on

JING et al.: OIPR: EVALUATION FOR TIME-SERIES ANOMALY DETECTION INSPIRED BY OPERATOR INTEREST

3579

TABLE VI
EXPERIMENTAL RESULTS OF ADVANCED DETECTORS AUTOFORMER, DLINEAR AND TIMESNET ON REAL-WORLD DATASETS, EVALUATED BY BASELINE
EVALUATORS AND OIPR. EVALUATION METRICS ARE PRESENTED IN THE PRECISION/RECALL/F1-SCORE FORMAT. BOLD TEXT INDICATES THE HIGHEST
F1-SCORE AND UNDERLINED TEXT REPRESENTS THE SECOND-HIGHEST F1-SCORE

TABLE VII
EXPERIMENTAL RESULTS OF THE FIRST POINT DETECTOR df p AND THE LONG ANOMALY DETECTOR dl , EVALUATED BY BASELINE EVALUATORS AND OIPR.
EVALUATION METRICS ARE PRESENTED IN THE PRECISION/RECALL/F1-SCORE FORMAT. BOLD TEXT INDICATES THE HIGHEST F1-SCORE AND UNDERLINED
TEXT REPRESENTS THE SECOND-HIGHEST F1-SCORE

the SWaT dataset: these evaluators neglect that the fragmented
and scattered FP points in Timesnet’s detection results have
obscured the TP points (see Fig. 6(c)), thus overestimating its
ranking. Besides, the AM evaluator considers the FP points
relatively close to the ground truth anomaly events beneficial
rather than detrimental to the f1-score (i.e., the characteristic
of sparse anomaly misleading), which results in its ranking
deviations across most datasets. Finally, by incorporating all

beneficial characteristics and avoiding misleading ones, OIPR
attains the most rational evaluation ranking across all real-world
datasets, without any of the four aforementioned misoverestimation phenomena.
In the second group of experiments, we compare two adversary detectors dl and df p across the MSL, SMAP, PSM, SMD
and SWaT datasets to analyze the impact of the long anomaly
effect, as shown in Table VII. Two point-based evaluators, PW

3580

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

TABLE VIII
EXPERIMENTAL RESULTS OF THE DISPERSED DISTURBANCE DETECTOR ddisp , THE AGGREGATED DISTURBANCE DETECTOR daggr , AND THE CONTINUOUS
DISTURBANCE DETECTOR dcont . EVALUATION METRICS ARE PRESENTED IN THE PRECISION/RECALL/F1-SCORE FORMAT. BOLD TEXT INDICATES THE HIGHEST
F1-SCORE AND UNDERLINED TEXT REPRESENTS THE SECOND-HIGHEST F1-SCORE

and PA% K, are significantly affected due to the lack of existence
detection reward and the presence of long anomaly misleading,
and they favor dl over df p across all five datasets. Due to the
lack of overlapping proportion awareness, PA incorrectly regards
df p as ideal and consistently overestimates its f1-score as 1.
The event-based evaluators (RP/RR, TaPR, and AM) completely
eliminate the impact of the long anomaly misleading, and prefer
df p to dl on all datasets. As for OIPR, it mitigates rather than
fully eliminates this impact, thereby deems df p superior on
MSL and SMD while favoring dl on SMAP, PSM, and SWaT.
We argue this confirms OIPR as the only evaluator sensitive
to striking a balance between the detection of longer and more
anomalies. The underlying rationale is that when all anomaly
events are relatively short in duration, the total number of events
becomes a critical factor, suggesting that a detector capable of
identifying all anomalies suffices. In contrast, for anomalies with
drastically prolonged durations (e.g., the SWaT dataset, where
the longest anomaly lasts 10 hours and the shortest merely 100
seconds), assigning greater importance to the former is more
reasonable than treating these two events as entirely equivalent.
We discuss the threshold of long/short anomalies in Appendix C,
available online, and present the parameter sensitivity analysis
in Appendix D, available online.
In the third group of experiments, we compare three adversary
detectors ddisp , daggr , and dcont to assess the impact of the
fragmentation effect, as shown in Table VIII. To this end, we
introduce a metric called the ratio of normal intervals containing
FP points, denoted as RN , which quantifies the proportion of
normal intervals contaminated by FP points relative to the total
number of normal intervals. A normal interval is defined as a
non-anomalous interval between two adjacent anomaly events
in the ground truth. The RN values and other statistical data for
experiments are presented in Table IX. A higher RN means operators are more likely to face disturbances induced by false alarms
during routine operations. Notably, ddisp yields an extremely

TABLE IX
ADDITIONAL STATISTICS FOR THE REAL-WORLD DATASETS. RN REPRESENTS
THE RATIO OF CONTAMINATED NORMAL INTERVALS

high RN , as it causes a substantial number of contaminated
normal intervals. However, all point-based evaluators (PW, PA,
and PA% K) erroneously judge ddisp as satisfactory due to the
presence of long anomaly misleading. Additionally, daggr has
the same low RN as dcont , indicating few contaminated normal
intervals and that the two detectors deliver comparable, solid
performance. Nevertheless, RP/RR and TaPR lack the beneficial
characteristic of fragment merging, thereby misjudging daggr
as underperforming. Besides, the sparse anomaly misleading
characteristic causes the AM evaluator to erroneously rate ddisp
favorably. Ultimately, only OIPR successfully identifies ddisp
as a subpar detector and recognizes daggr and dcont as highperforming ones, as it takes into account the actual distribution
of discrete FP points.
VI. DISCUSSION
In this work, the proposed OIPR is characterized as an “areabased” TAD evaluator. To investigate its correlations and distinctions from existing point-based and event-based evaluators, we
introduce two specific custom configurations of OIPR, which

JING et al.: OIPR: EVALUATION FOR TIME-SERIES ANOMALY DETECTION INSPIRED BY OPERATOR INTEREST

can be interpreted as point-based and event-based evaluators,
respectively.
Zero observation phase. In this configuration, we set lobs =
0 in Algorithm 1, indicating that there is no observation phase
associated with the anomaly points. As a result, the operator
interest in each anomaly point does not extend to the subsequent
time point. It is evident that, in such a scenario, the operator
interest curve of the ground truth and that of the detection results
can be calculated as:
I = y, Î = ŷ.

(10)

Hence, OIPR degenerates into a point-based evaluator, which
is essentially equivalent to the classical PW evaluator.
Strict occurrence detection evaluator. By setting ldis = 0,
bdur = 0, and lobs = 1 in Algorithm 1, OIPR can be converted into a distinctive event-based evaluator: here, a predicted
anomaly event is classified as a TP event only when its initial
point coincides with the initial point of a ground truth event.
Conversely, any ground truth event whose initial point does
not align with that of a prediction event is classified as an FN
event, while any prediction event whose initial point does not
correspond to that of a ground truth event is categorized as an FP
event. Although this evaluator may appear excessively stringent,
it effectively demonstrates that OIPR can be transformed into
an event-based evaluator through specific parameter configurations.
Through the specific configurations discussed above, it can
be observed that OIPR lies between the point-based and eventbased evaluators. It employs the observation phase to mitigate
the long anomaly effect and to merge potential fragmented
events. Additionally, the use of area in calculating the evaluation
metrics enables OIPR to effectively bridge the gap between
point-based and event-based perspectives, thereby enhancing its
versatility and applicability.

VII. CONCLUSION
Given the key role of TAD in data analysis, numerous studies
have focused on improving anomaly detector performance to
identify anomalous behaviors and potential system faults. When
evaluating these detectors, selecting an appropriate evaluator is
critical: it helps operators choose optimal detectors and avoids
misleading researchers into suboptimal optimization. In this
work, we developed a novel TAD evaluator, OIPR, which is
inspired by the interest of operators in monitoring KPIs and
associated detectors. Compared with existing evaluators, OIPR
has fewer limitations, adapts to diverse scenarios, and allows
for smooth transitions between point-based and event-based
paradigms via custom configuration to balance the two perspectives. We also introduced a special scenario dataset, which is
carefully designed to highlight the characteristics and limitations
of different evaluators. The superiority of OIPR is verified
through experiments on the special scenario dataset alongside
several real-world datasets.

3581

REFERENCES
[1] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time series
anomaly detection with association discrepancy,” in Proc. 10th Int. Conf.
Learn. Representations, 2022, pp. 1–20.
[2] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, Anchorage, AK, 2019, pp. 2828–2837.
[3] S. Dou, K. Yang, Y. Jiao, C. Qiu, and K. Ren, “Anomaly detection in
event-triggered traffic time series via similarity learning,” IEEE Trans.
Dependable Secur. Comput., vol. 22, no. 2, pp. 888–902, Mar./Apr. 2025.
[4] F. Jin, H. Wu, Y. Liu, J. Zhao, and W. Wang, “Varying-scale hca-dbscanbased anomaly detection method for multi-dimensional energy data in steel
industry,” Inf. Sci., vol. 647, 2023, Art. no. 119479.
[5] D. Velásquez et al., “A hybrid machine-learning ensemble for anomaly detection in real-time industry 4.0 systems,” IEEE Access, vol. 10, pp. 72024–
72036, Jul. 2022.
[6] D. Tang, S. Wang, B. Liu, W. Jin, and J. Zhang, “GASF-IPP: Detection and
mitigation of LDoS attack in SDN,” IEEE Trans. Serv. Comput., vol. 16,
no. 5, pp. 3373–3384, Sep./Oct. 2023.
[7] Y. Jing et al., “Diner: Interpretable anomaly detection for seasonal time
series in web services,” IEEE Trans. Serv. Comput., vol. 17, no. 5, pp. 2248–
2260, Sep./Oct. 2024.
[8] S. Zhang et al., “Efficient KPI anomaly detection through transfer learning
for large-scale web services,” IEEE J. Sel. Areas Commun., vol. 40, no. 8,
pp. 2440–2455, Aug. 2022.
[9] G. Sivapalan, K. K. Nundy, A. P. James, B. Cardiff, and D. John, “Interpretable rule mining for real-time ECG anomaly detection in IoT edge
sensors,” IEEE Internet Things J., vol. 10, no. 15, pp. 13095–13108,
Aug. 2023.
[10] T. P. Q. Nguyen et al., “Time-series anomaly detection using dynamic
programming based longest common subsequence on sensor data,” Expert
Syst. Appl., vol. 213, no. Part, Mar. 2023, Art. no. 118902.
[11] S. Xie, L. Li, and Y. Zhu, “Anomaly detection for multivariate time series
in IoT using discrete wavelet decomposition and dual graph attention
networks,” Comput. Secur., vol. 146, 2024, Art. no. 104075.
[12] Y. Zhang, Y. Chen, J. Wang, and Z. Pan, “Unsupervised deep anomaly
detection for multi-sensor time-series signals,” IEEE Trans. Knowl. Data
Eng., vol. 35, no. 2, pp. 2118–2132, Feb. 2023.
[13] V. Jacob and Y. Diao, “Unsupervised anomaly detection in multivariate
time series across heterogeneous domains,” in Proc. VLDB Endow., vol. 18,
no. 6, pp. 1691–1704, Feb. 2025.
[14] W. Wang, Z. Yue, and B. Zheng, “Streaming time series subsequence
anomaly detection: A glance and focus approach,” in Proc. VLDB Endow.,
vol. 18, no. 6, pp. 1892–1904, Feb. 2025.
[15] S. Kim, K. Choi, H. Choi, B. Lee, and S. Yoon, “Towards a rigorous
evaluation of time-series anomaly detection,” in Proc. 36th AAAI Conf.
Artif. Intell., California, USA, 2022, pp. 7194–7201.
[16] N. Tatbul, T. J. Lee, S. Zdonik, M. Alam, and J. Gottschlich, “Precision and
recall for time series,” in Proc. Adv. Neural Inf. Process. Syst. 31: Annu.
Conf. Neural Inf. Process. Syst., Montréal, Canada, 2018, pp. 1924–1934.
[17] J. Paparrizos, P. Boniol, T. Palpanas, R. Tsay, A. J. Elmore, and
M. J. Franklin, “Volume under the surface: A new accuracy evaluation
measure for time-series anomaly detection,” in Proc. VLDB Endow.,
vol. 15, no. 11, pp. 2774–2787, Sep. 2022.
[18] Y. Xu et al., “Unsupervised anomaly detection via variational auto-encoder
for seasonal KPIs in web applications,” in Proc. 2018 World Wide Web
Conf. World Wide Web, Lyon, France, Apr. 2018, pp. 187–196.
[19] W. Hwang, J. Yun, J. Kim, and H. Kim, “Time-series aware precision and
recall for anomaly detection: Considering variety of detection result and
addressing ambiguous labeling,” in Proc. 28th ACM Int. Conf. Inf. Knowl.
Manage., Beijing, China, 2019, pp. 2241–2244.
[20] W. G. Gadallah, H. M. Ibrahim, and N. M. Omar, “A deep learning
technique to detect distributed denial of service attacks in software-defined
networks,” Comput. Secur., vol. 137, 2024, Art. no. 103588.
[21] J. Ahmed and R. C. Green, “Cost aware LSTM model for predicting hard
disk drive failures based on extremely imbalanced s. m. a.r.t. sensors data,”
Eng. Appl. Artif. Intell., vol. 127, no. Part B, 2024, Art. no. 107339.
[22] N. Zhao et al., “Identifying bad software changes via multimodal anomaly
detection for online service systems,” in Proc. 29th ACM Joint Eur. Softw.
Eng. Conf. Symp. Found. Softw. Eng., Athens, Greece, 2021, pp. 527–539.
[23] A. Huet, J. M. Navarro, and D. Rossi, “Local evaluation of time series
anomaly detection algorithms,” in Proc. 28th ACM SIGKDD Conf. Knowl.
Discov. Data Mining, Washington, DC, 2022, pp. 635–645.

3582

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

[24] Y. Lu, T. V.A. Srinivas, T. Nakamura, M. Imamura, and E. Keogh, “Matrix
profile XXX: MADRID: A hyper-anytime and parameter-free algorithm
to find time series anomalies of all lengths,” in Proc. IEEE Int. Conf. Data
Mining, Shanghai, China, 2023, pp. 1199–1204.
[25] J. Á. Cid-Fuentes, C. Szabo, and K. Falkner, “Adaptive performance
anomaly detection in distributed systems using online SVMs,” IEEE Trans.
Dependable Secur. Comput., vol. 17, no. 5, pp. 928–941, Sep./Oct. 2020.
[26] S. Liu et al., “Time series anomaly detection with adversarial reconstruction networks,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 4, pp. 4293–
4306, Apr. 2023.
[27] J. A. Ward, P. Lukowicz, and H. Gellersen, “Performance metrics for
activity recognition,” ACM Trans. Intell. Syst. Technol., vol. 2, no. 1,
pp. 6:1–6:23, Jan. 2011.
[28] S. Sørbø and M. Ruocco, “Navigating the metric maze: A taxonomy of
evaluation metrics for anomaly detection in time series,” Data Min. Knowl.
Discov., vol. 38, no. 3, pp. 1027–1068, May 2024.
[29] A. M. Treisman, “Verbal cues, language, and meaning in selective attention,” Amer. J. Psychol., vol. 77, no. 2, pp. 206–219, Jun. 1964.
[30] S. Hochreiter and J. Schmidhuber, “Long short-term memory,” Neural
Comput., vol. 9, no. 8, pp. 1735–1780, Nov. 1997.
[31] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural Inf.
Process. Syst. 30: Annu. Conf. Neural Inf. Process. Syst., Long Beach, CA,
USA, 2017, pp. 5998–6008.
[32] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Söderström, “Detecting spacecraft anomalies using LSTMs and nonparametric
dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, London, U.K., 2018, pp. 387–395.
[33] A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to asynchronous multivariate time series anomaly detection and localization,” in
Proc. 27th ACM SIGKDD Conf. Knowl. Discov. Data Mining, Singapore,
2021, pp. 2485–2494.
[34] A. P. Mathur and N. O. Tippenhauer, “Swat: A water treatment testbed
for research and training on ICS security,” in Proc. 2016 Int. Workshop
Cyber- Phys. Syst. Smart Water Netw., Vienna, Austria, 2016, pp. 31–36.
[35] Y. Yao, A. B. Sharma, L. Golubchik, and R. Govindan, “Online anomaly
detection for sensor systems: A simple and efficient approach,” Perform.
Eval., vol. 67, no. 11, pp. 1059–1075, Nov. 2010.
[36] A. Lavin and S. Ahmad, “Evaluating real-time anomaly detection algorithms - the numenta anomaly benchmark,” in Proc. 14th IEEE Int. Conf.
Mach. Learn. Appl., Miami, FL, USA, 2015, pp. 38–44.
[37] J. Paparrizos, Y. Kang, P. Boniol, R. S. Tsay, T. Palpanas, and
M. J. Franklin, “TSB-UAD: An end-to-end benchmark suite for univariate
time-series anomaly detection,” in Proc. VLDB Endow., vol. 15, no. 8,
pp. 1697–1711, Apr. 2022.
[38] N. Laptev and S. Amizadeh, “Online dataset for anomaly detection,”
2015. [Online]. Available: http://webscope.sandbox.yahoo.com/catalog.
php?datatype=s&did=70
[39] H. Wu, J. Xu, J. Wang, and M. Long, “Autoformer: Decomposition
transformers with auto-correlation for long-term series forecasting,” in
Proc. Adv. Neural Inf. Process. Syst. 34: Annu. Conf. Neural Inf. Process.
Syst., 2021, pp. 22419–22430.
[40] A. Zeng, M. Chen, L. Zhang, and Q. Xu, “Are transformers effective
for time series forecasting?,” in Proc. 37th AAAI Conf. Artif. Intell.,
Washington, DC, 2023, pp. 11121–11128.
[41] H. Wu, T. Hu, Y. Liu, H. Zhou, J. Wang, and M. Long, “TimesNet:
Temporal 2D-variation modeling for general time series analysis,” in Proc.
11th Int. Conf. Learn. Representations, Kigali, Rwanda, 2023, pp. 1–23.

Yuhan Jing received the master’s degree from the
Beijing University of Posts and Telecommunications,
China, in 2020. She is currently a doctoral candidate
with the State Key Laboratory of Networking and
Switching Technology, Beijing University of Posts
and Telecommunications. Her research interests include AIOps, Time-series Analysis, Anomaly Detection, and Fault Localization.

Jingyu Wang (Senior Member, IEEE) received the
PhD degree from the Beijing University of Posts and
Telecommunications, Beijing, China, in 2008. He
is currently a tenured professor with the State Key
Laboratory of Networking and Switching Technology, Beijing University of Posts and Telecommunications. He is selected for the Yangtse River Scholar
Award Program by the Ministry of Education. He
has published more than 200 papers in such as the
ToN, TMC, JSAC, NSDI, ASPLOS and so on. His
research interests include broad aspects of Intelligent
Networks, Edge/Cloud Computing, Machine Learning, Self-Driving Network,
IoV/IoT, Knowledge-Defined Network and Intent-Driven Networking.

Lei Zhang received the master’s degree from the
Nanjing University of Posts and Telecommunications, in 2004. She is the technical expert of department of Cloud Network Center, China Unicom, and
the leader of Digital twin Project. Her research interest covers mobile network, Network Management,
AIOps, Digital twin etc.

Haifeng Sun (Senior Member, IEEE) received the
PhD degree from the Beijing University of Posts and
Telecommunications, Beijing, China, in 2017. He is
currently an associate professor with the State Key
Laboratory of Networking and Switching Technology, Beijing University of Posts and elecommunications. His research interests include broad aspects of
AI, NLP, Big Data analysis, object detection, deep
learning and pattern recognition.

Bo He (Member, IEEE) received the PhD degree from
the Beijing University of Posts and Telecommunications, China, in 2023. He is currently an associate
researcher with the State Key Laboratory of Networking and Switching Technology, Beijing University of
Posts and Telecommunications. From 2021 to 2022,
he was a visiting PhD student with the University
of Waterloo, Canada. His research interests include
5G/6G networks, multipath networks, collective communication, transmission control, and deep reinforcement learning.

Zirui Zhuang (Member, IEEE) received the BS and
PhD degrees from the Beijing University of Posts
and Telecommunications, in 2015 and 2020, respectively. He is currently a post-doctoral researcher
with the State Key Laboratory of Networking and
Switching Technology, Beijing University of Posts
and Telecommunications. In 2019, he visited the
Department of Electrical and Computer Engineering,
University of Houston. His research interests involve
network routing and management for nextgeneration
network infrastructures, using machine learning and
artificial intelligence techniques, including deep learning, reinforcement learning, graph representation, multi-agent systems, and Lyapunovbased optimization.

JING et al.: OIPR: EVALUATION FOR TIME-SERIES ANOMALY DETECTION INSPIRED BY OPERATOR INTEREST

Chengsen Wang received the BD degree from the
Beijing University of Posts and Telecommunications,
in 2022. He is currently a doctoral candidate of
State Key Laboratory of Networking and Switching
Technology with the Beijing University of Posts and
Telecommunications. His main research interests include time-series analysis, anomaly detection, and
multimodal learning.

Qi Qi (Senior Member, IEEE) received the PhD
degree from the Beijing University of Posts and
Telecommunications, Beijing, China, in 2010. She is
currently a professor with the State Key Laboratory
of Networking and Switching Technology, Beijing
University of Posts and Telecommunications. She
has authored or co-authored more than 30 papers
in the international journal and is the recipient of
two National Natural Science Foundations of China.
Her research interests include edge computing, cloud
computing, the Internet of Things, ubiquitous services, deep learning, and deep reinforcement learning.

3583

Jianxin Liao (Senior Member, IEEE) received the
PhD degree from the University of Electronics Science and Technology of China, Chengdu, China,
in 1996. He is currently the dean of the Network
Intelligence Research Center and a full professor
with the State Key Laboratory of Networking and
Switching Technology, Beijing University of Posts
and Telecommunications. He has authored or coauthored hundreds of research papers and several books.
He has won several prizes in China for his research
achievements, which include the Premiers Award of
Distinguished Young Scientists from National Natural Science Foundation of
China, in 2005, and the specially invited professor of the Yangtse River Scholar
Award Program by the Ministry of Education, in 2009. His main research
interests include cloud computing, mobile intelligent network, service network
intelligence, networking architectures and protocols, and multimedia communication.
PAPER_TEXT
