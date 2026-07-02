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
# [291] Review of Accident Detection Methods Using Dashcam Videos for Autonomous Driving Vehicles
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
编号：291
题名：Review of Accident Detection Methods Using Dashcam Videos for Autonomous Driving Vehicles
年份：2024
DOI：10.1109/tits.2024.3354852
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2024.3354852.pdf
已有粗分类：数据集、基准、综述与开源工具
二级关联：IoT、车联网、工业互联网与边缘安全、多媒体、医学、遥感与视频异常检测
相关性：弱相关，分数 
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\291.txt
- 原始字符数：103434
- 本次发送字符数：103434
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
8356

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

Review of Accident Detection Methods Using
Dashcam Videos for Autonomous
Driving Vehicles
Arash Rocky , Graduate Student Member, IEEE, Qingming Jonathan Wu , Senior Member, IEEE,
and Wandong Zhang, Member, IEEE

Abstract— The need for a reliable system to detect high-risk
incidents in complex settings like roadways, which are infrequent
but potentially dangerous, has arisen due to the occurrence of
rare hazardous events. This system would empower self-driving
cars to function autonomously over extended periods without
human involvement. Among these hazardous occurrences, accidents have received the least attention due to their rarity and
diverse nature. Recently, dashboard cameras (dashcams) have
gained recognition in academic circles as a cost-effective and
accessible solution to enhance the safety of autonomous vehicles
when handling accidents, since they are now commonly found in
most vehicles. This review presents the progression of concepts in
this domain, tracing its development from early ideas to cuttingedge techniques. It categorizes these approaches into supervised,
self-supervised, and unsupervised learning. Furthermore, the
review thoroughly examines evaluation criteria and available
datasets, providing a comprehensive comparison of the strengths
and limitations of different methods. Ultimately, the review
proposes potential avenues for future research in this field.
Index Terms— Accident detection, autonomous vehicles, deep
learning, traffic anomaly detection, dashcam videos.

I. I NTRODUCTION

I

N THE context of roads and transportation, human
behaviour is crucial in ensuring road safety, but predicting
it is complicated because it is influenced by interactions with
other road users such as vehicles and pedestrians, as well as
the surrounding environment. According to statistics in [1]
and [2], a significant percentage of accidents are caused
by human error. Therefore, it is essential to comprehend
these interactions to facilitate the transition to Level 3+ of
automation (classified by Society of Automotive Engineers
(SAE) [3]), where autonomous vehicles (AV)s must safely
control all driving functions.
Manuscript received 20 May 2023; revised 21 September 2023 and
11 January 2024; accepted 12 January 2024. Date of publication 31 January
2024; date of current version 1 August 2024. This work was supported in
part by TrustCAV, a Collaborative Research and Training Experience Program
(CREATE) Program of the Natural Sciences and Engineering Research
Council of Canada. The Associate Editor for this article was J. Hemanth.
(Corresponding author: Qingming Jonathan Wu.)
Arash Rocky and Qingming Jonathan Wu are with the Department of Electrical and Computer Engineering, University of Windsor, Windsor, ON N9B
3P4, Canada (e-mail: rocky@uwindsor.ca; jwu@uwindsor.ca).
Wandong Zhang is with the Department of Electrical and Computer
Engineering, Western University, London, ON N6A 3K7, Canada (e-mail:
wzhan893@uwo.ca).
Digital Object Identifier 10.1109/TITS.2024.3354852

Autonomous vehicle systems rely on processing a significant amount of perception data to detect potentially high-risk
situations, such as object detection, classification, and localization. However, this data can be incomplete, uncertain,
or noisy, making it challenging to achieve early and robust
detection of potential accidents. The complexity of the driving
domain–including an infinite number of unusual scenarios and
unseen context–adds to the difficulty of hazardous event detection of autonomous vehicles [4], [5], [6], [7]. Furthermore, as it
is impractical to manually define all risky situations, a flexible
framework is crucial for accommodating the ever-evolving
driving environment.
A. Term Clarification: Difference Between Dashcam, Front
Camera and Rear Camera
A dashboard camera (commonly referred to as a dashcam),
a front camera and a rear camera are devices used for
capturing video footage, but they serve different purposes and
are typically used in different contexts with respect to their
purpose, location, application and functionality.
From one perspective, dashcam is specifically designed to
record video footage (such as road incidents, accidents, and
the surrounding traffic) continuously from the perspective of
a vehicle’s dashboard or windshield in motion. In contrast,
front camera is a general term that can refer to any camera
positioned on the front of a device or object and is not
limited to vehicles as it can be found on various devices
such as smartphones, laptops and security systems. Therefore,
front camera on a smartphone can be used for selfies and
video calls, it is used for video conferencing on a laptop,
and in security systems, it can capture video footage of an
area for surveillance purposes. Considering the rear camera’s
perspective, it is primarily used to assist drivers when reversing
or parking by providing a view of the area behind the vehicle
to help the driver avoid obstacles and ensuring safety while
backing up. These types of cameras are mainly mounted near
the license plate or on the rear bumper and have a narrower
field of view.
B. Why Using Dashcams for Accident Detection?
As the most risky situation for autonomous vehicles, the
detection and anticipation of accidents is still a grey area
in both industry and academics. Perhaps the biggest hurdle

1558-0016 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

ROCKY et al.: REVIEW OF ACCIDENT DETECTION METHODS USING DASHCAM VIDEOS

Fig. 1. Dashcams are reasonably-priced, widely accessible, easy to install,
occupying limited space and while they are not blocking driver’s vision, yet
they record the most important moments. (Source: thinkwarestore.com and
pioneerelectronics.com).

in overcoming this issue is lack of sizeable real dataset
of accidents providing information from all state-of-the-art
sensors, including lidars due to high price of such sensors
and rareness nature of accidents. Having said that, dashboard
cameras (dashcams), in contrary to other sensors, have become
widely available in recent years installed in almost every car
(Figure 1). This unique advantage of their availability in cars
has helped dashcams to be present recording many accidental
scenes and their database has ever been growing. As deep
learning models have always shown improvement by providing
larger dataset and considering the chance of sensory fusion
of dashcam dataset, there is no doubt that dashcam based
models will become more reliable and overall decision-making
of autonomous vehicles in accident scenarios will improve
significantly.
C. Challenges and Promising Future of Dashcams
In recent years, scholars have been working towards tackling
the problem of accidents by creating hazard-predicting techniques that rely on dashboard cameras [8]. While their study
can be regarded as the fundamental framework for employing
dashcams in accident detection and anticipation, the process
of identifying an accident itself proves to be exceptionally
demanding due to the dynamic background [9]. This dynamic
background stands in stark contrast to surveillance cameras
with static backgrounds, creating complexity in distinguishing between hazardous events and regular scenes. Given the
outlined problem, the objective of this paper is to aggregate
all pertinent research within the realm of traffic accident
detection (TAD) through dashcams. This paper intends to
construct a comprehensive evolutionary survey of TAD, with
the goal of expediting research efforts aimed at surmounting
present obstacles. The attainment of a dependable and robust
method for dashcam-based TAD could substantially enhance
the affordability of the overall autonomous vehicle system.
Such an achievement would mark a significant advancement
in the widespread manufacturing of autonomous vehicles.
D. Dashcam Models: From Hazardous Incident Detection to
General Anomaly Detection With a Focus on Accidents
Typically, dashcam models employ a hybrid deep learning framework that merges convolutional neural networks
(CNNs) and recurrent neural networks (RNNs) to identify
potential hazards in videos recorded by dashcams, serving as
a shared foundation. These methods involve parsing images
using a CNN to extract appearance features and localizing

8357

objects. The extracted spatial features are subsequently fed
into an RNN to capture temporal patterns and understand
how these spatial features evolve over time. For instance,
[10] used Mask R-CNN for semantic segmentation and then
used a CNN-LSTM network to classify dangerous lane change
detection based on the frame overlays with these masks.
Additionally, [11] proposed a risk assessment method based
on the impact of any risky object on drivers’ behaviour. Using
a cause-and-effect approach, the risk of identified objects
is assessed with a two-step framework that determines the
reaction of the driver (effect) based on the risky object (cause).
However, unguided deep learning models can train spurious
patterns [12], and CNN models may fail to extract unobservable contextual relations in their features, as shown by studies
of [13] and [14]. In their recent study, [15] proposes that when
it comes to detecting high-risk incidents, such as accidents
or abnormalities, the primary challenges lie in addressing
the issues of imbalanced distribution and diverse anomaly
classes. As discussed in the above studies, the primary goal
of hazardous incident detection is to identify and respond to
events that pose a threat to safety or the environment. These
incidents can include accidents, emergencies, or any situation
that may lead to harm.
Looking from broader perspective, accident detection is a
kind of anomaly detection in the context of dashcam videos
that can be applied in various domains to recognize deviations
from regular patterns. This involves identifying comparatively
straightforward visual anomalies, such as abrupt movements in
a specific area of the video frame or the presence of visual artifacts or objects that were not included in the training dataset.
Contrary to that simple visual anomaly perspective, driving
scenes are considered with continuous movement, and anomalies are frequently defined by intricate interactions among
participants in traffic which show a significant imbalance
between normal driving scenes and accident scenes. To tackle
these challenges, various methods have been suggested, which
can be categorized into three primary types: video-based,
segment-based, and frame-based detection approaches.
1) Video-Based Accident Detection: In video-based
approaches, the whole video is given as input for TAD. These
methods are generally divided into conventional/classical
classifier and reconstruction error-based models. Conventional
classifiers operate under the assumption that all normal
instances belong to a single category, while reconstruction
error-based models rely on the premise that abnormal
samples will exhibit higher reconstruction errors compared
to normal samples. One-class classification, as described in
prior works [16], [17], [18], refers to methods that construct
a multidimensional representation for normal data, with
the objective of making that representation as compact as
possible. During the testing phase, any data points that
fall outside the learned multidimensional representation are
flagged as anomalous. The deficiency of such classifiers is
their need to have features extracted separately [19]. To make
an end-to-end video-based approach, some literature came up
with reconstruction error-based models that extract a feature
map from input video and distinguish an accident/abnormal
video from a normal video based on their reconstruction

8358

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

error (large error for abnormal video and small error for
normal video). These methods can further be divided into
Generative adversarial network (GAN) based, such as [20] and
Autoencoder based networks, such as [21]. Having said that,
in facing dashcam accident videos, which have imbalanced
distribution and contain dynamic, complex backgrounds,
video-based approaches cannot cater to the need of TAD.
2) Segment-Based Accident Detection: Looking at accident
detection from segment-based categories such as in [23] and
[24], these techniques were developed to tackle the challenge
of imbalanced distribution in traffic accident detection using
a weakly-supervised framework that incorporates Multiple
Instance Learning (MIL) principles. In the segment-based
TAD, each video is separated into clips where an anomalous
video can have normal clips before and after the anomalous
clip of that video. Using class labels of anomaly and normal
for the whole video instead of each video segment/clip,
in their research, authors aim to directly learn the anomaly
score for each video segment, with the goal of reducing
the time needed for manual annotation of each segment.
To implement their idea, in their study [24], first video
segments are fed to MIL, extracting segment features, and
then a 3D convolutional network is applied to them. Each
segment receives an anomaly score from which the anomaly
segment is determined. Reference [23] developed this idea by
introducing the optical flow of each segment as a segment
feature and applying attention to the MIL method which
improved the overall performance. A more intricate approach
was proposed in [25], which involves a dual branch network
consisting of a spatial-temporal dynamic subnetwork and an
interconnected dynamic subnetwork, both of which are trained
using MIL techniques. While the former network is fed with
the video segments, the latter has the input of feature maps that
represent the interaction of pedestrians and the surrounding
environment. More completely, [26] introduced the location
of the anomaly to segment-based literature. Although such
segment-based methods can be useful in the detection and
localization of TAD, they cannot deal with multiple anomalies
in a complex scene.
3) Frame-Based Accident Detection: In frame-based
approaches like [27] and [28], the current frame is constructed
using the previous frames and the anomaly is detected as
the discrepancy in reconstruction between the generated current frame and the original frame. While such frame-based
approaches can accurately determine the spatial and temporal location of abnormalities, they are still time-consuming,
same as video-based and segment-based methods. Framebased methods same as video-based methods fall into two
main categories: Classifiers and Reconstruction Error-based
methods, where classifiers have been used in supervised learning [15], [29]. As the dominant category in the literature of
frame-based approaches, reconstruction-based methods require
image or frame generation in networks, these can be broadly
classified into two subcategories: 1) Autoencoder networks
[30], [31], [32], [33] and 2) Generative adversarial networks
(GANs) [34]. Autoencoder networks take input frames and
compress them into a condensed representation, referred to
as a “bottleneck” or latent vector, which contains fewer

dimensions but retains crucial features. This latent vector
is then used by the decoder to produce approximate future
images or frames. Despite its usefulness, autoencoders are
susceptible to overfitting and the vanishing gradient problem,
which are common issues in neural networks [35].
On the other hand, GANs aim to generate synthetic data that
closely resembles real data, achieved through a training process involving adversarial learning between the generator and
discriminator. To address the issue of detecting anomalies, [36]
proposed a framework for predicting frames that incorporate
standard spatial constraints based on intensity and gradient,
as well as a temporal constraint based on motion. Their criteria
for detecting anomalies are based on the consistency of the
optical flow between the predicted frames and the ground truth
frames. Consequently, this integration of spatial and motion
constraints helps distinguish anomalies from normal events
as anomalous scenes cannot become predicted based on the
learned pattern. Figure 2 shows a distinction between normal
and anomalous scene. As discussed, even a frame prediction
method is of high computational cost. Recently, state-of-theart methods suggested object-based prediction [22] and later
in more complex methods, researchers have introduced object
and scene interaction features [37] and applied ensemble
of methods [37], [38]. The summary of the whole TAD
categorization is depicted in Figure 3.
E. Purpose and Contribution of This Survey
While some studies like [39] provide a broad picture of
solving the problem of risky incident detection with graphbased methods, this study tries to provide a comprehensive
evolution of literature that has led to state-of-the-art methods in TAD using dashcams. Furthermore, in addition to
the mentioned categories of TAD–comprising video-based,
segment-based, or frame-based–same as all deep learning
subjects– according to the usage of dataset labels, methods
can also be divided into supervised, unsupervised, selfsupervised and other in-between approaches. Regardless of
their approach within the label-based categories (Unsupervised, self-supervised, supervised, or any mixed versions),
or content-based categories (video-based, segment-based or
frame-based methods), as they will be discussed in details
in this study, all TAD methods are formed upon object
detection, object tracking and spatial-temporal features that are
extracted from the whole frames or objects and their motion
(Figure 4).
With the general overview of dashcams and accident detection provided in this section, the rest of this paper tries to
discuss about strengths and weaknesses of available TAD
methods using dashcams in the literature that led to four
state-of-the-art methods: [22], [37], [38] all of which are
frame-based, error reconstruction-based models with the GAN
architecture, while the model of [15] is also considered framebased, but classifier based method. To keep the consistency in
this survey, the sections are provided according to chronicle
of publications and each section discusses the evolution of
methods on that category. As a result, the rest of this paper
is organized as follows: Section II elaborate on Unsupervised

ROCKY et al.: REVIEW OF ACCIDENT DETECTION METHODS USING DASHCAM VIDEOS

8359

Fig. 2. This figure shows an example of how a normal scene turns into an anomalous scene. In the first sampled frame (from right) the truck is crossing the
intersection from right to left with orange direction and the car is passing in the direction of yellow arrow (TAD evaluation curve shows low values). However,
in the second sampled frame when accident has taken place although truck is still following the orange direction, the car not only has been deviated toward
red curved arrow from its yellow direction but also has been deformed (highlighted with red oval). Such deviations from normal motions and deformations
of objects’ appearance make a scene anomalous, which is reflected in the TAD curve. As can be seen in third frame, the anomaly has intensified with the
additional deviation of truck from its orange path and change of appearance in the frame with car’s part being separated in the air (TAD curve shows even
higher values). Adapted from [8] and [22].

Fig. 3. Summary of Traffic Accident Detection Methods. (It should be noted that TAD methods under “Segment-based methods” category have specifically
applied the method “MIL+3D-CNN” and they are differentiated based on the input of the method.)

video-based Traffic Accident Detection (TAD) methods [22],
[38] and all relevant literature. Section III discusses about
where Self-Supervised video-based methods stem from to deal
with TAD [37], [40]. The supervised frame-based learning
methods, [15], [29], are discussed in Section IV. Next, in the V
an in-detail explanation of the available dataset is presented.
Section VI provides the applied evaluation metrics in TAD.

Then comes the discussion and comparison of the state-ofthe-art methods in VII, followed by discussions on future
works in VIII. Finally, the conclusion of this study is delivered
in IX. Overall, the contribution of this survey can be succinctly
outlined in the following way:
1) This paper presents the evolution of all available
dashcam-based TAD methods in the literature

8360

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

Fig. 4.

The actual procedure of Traffic Accident Detection methods. Adapted from [8] and [22].

2) All catered and applied dataset in dashcam-based TAD
methods whether publicly available or been of limited
access are discussed and compared in detail.
3) Then comes the pros and cons of evaluation metrics in
dashcam-based TAD methods.
4) Finally, the comparison, strengths and weaknesses of
the state-of-the-art dashcam-based TAD methods and
possible future directions are discussed, accordingly.
II. U NSUPERVISED T RAFFIC ACCIDENT D ETECTION
From a general perspective, unsupervised machine learning
methods are considered as those methods that during the
training, the model is not given any output label. In the context
of TAD, unsupervised methods are those whose dataset videos
are not having the label “accident” or “non-accident/normal”.
Going into more detail, some datasets have not just labelled
videos, but they have a reach annotation per frame, such
as DoTA [38] (There is a thorough explanation of different
datasets in section V). The mindset behind unsupervised
methods of TAD is that labelling all videos/frames can be
so time-consuming and any method that relies on and is
trained with labels would not be able to generalize well and
would not be able to detect any new accident type. With
this perspective, researchers considered the unsupervised TAD
as a type of anomaly detection in which the model learns
to be trained with non-accident events and recognize any
abnormal event as an accident. However, anomaly detection
has been mainly applied to surveillance camera datasets, which
have a static background and applying those methods for
accident detection with dashcam datasets which have dynamic
background can be challenging. To deal with this challenge,
researchers of [22] tried to generalize the idea of anomaly
detection in videos based on future frame prediction which
was initially suggested in [36]. In fact, the accident detection
method of [22] is a combination of anomaly detection in [36]

based on future object localization in [9] and tracking objects
method introduced in [41].
A. Fundamentals of Unsupervised TAD
The core structure of [22] relies on the foundational
design of AnoPred [36]. AnoPred, in turn, takes advantage of both spatial and motion constraints. Within the
AnoPred framework, the spatial constraint emerges through an
encoder that captures both intensity (reflecting pixel likeness,
i.e., L I nt = nor m 2 (It , Iˆt )) and gradient features (preserving edges)
from predicted and ground truth frames, i.e.,
P
L Grad (pixel-wise gradient(It , Iˆt )). These features are then
measured using the l2 and l1 distance metric, respectively.
Regarding the motion constraint, the comparison between predicted and ground truth frames is facilitated by Flownet [42],
i.e., L Flow = nor m 1 (Flownet(It , Iˆt )). This component
extracts optical flow information from frames and is subject
to penalization through the Least Square GAN module (L Disc
Eq. 1, L Gen Eq. 2, PI is the set of patch indexes in image Iˆ(t+1)
and PS is Patch Score function that produces an scalar value
for each patch). As a result, the final loss function of [36] can
be considered the Eq. 1 as the discriminator loss and Eq. 3 as
the total generator loss function. The ultimate comparison of
their architectural performance is quantified using peak signalto-noise ratio (PSNR) [43].
L Disc (It+1 , Iˆt+1 )

X 1
2 1 
2
ˆ
ˆ
=
PS(i, j) ( I(t+1) ) − 1 + PS(i, j) ( I(t+1) )
2
2
(i, j)∈P I

(1)
L Gen ( Iˆt+1 )

X 1
2
=
PS(i, j) ( Iˆ(t+1) ) − 1
2
(i, j)∈P I

(2)

ROCKY et al.: REVIEW OF ACCIDENT DETECTION METHODS USING DASHCAM VIDEOS

8361

L G (It , It+1 , Iˆt+1 )
X
=

accommodated the dynamic nature of dashcam video back grounds, i.e., adapting surveillance camera anomaly detection

λi L i (It , It+1 , Iˆt+1 )+λGen L Gen ( Iˆ(t+1) )
methods from [36] to dashcams, but also transformed the
(i, j)∈{I nt,Grad,Flow}
problem of accident detection. They shifted from a one-class
(3) classification paradigm, which relies on meticulously labeled
training datasets and confines anomaly identification to preTo make this backbone architecture (AnoPred) adapted defined categories, to a reconstruction error-based model.
with TAD application, authors of [22] conducted a research In essence, their method focused on predicting future object
in [9] that predicts future location of vehicles in the scenes locations within the scene. If the anticipated positions of
instead of predicting the whole frame, which is computation- scene objects significantly deviated from their actual positions
ally more efficient. Delving further into the specifics, within due to abrupt changes in object speed or position, the scene
the context of [9], a combination of dense optical flow (to was considered anomalous–indicating a potential accident.
capture motion-related information) and vehicle localization To enhance the effectiveness of their approach in rapidly
(to extract alterations in appearance) is employed. This fusion moving driving contexts, they restricted predictions to objects
is utilized to predict the forthcoming positions of observed within bounding boxes (X t = [Ctx , Cty , ωt , h t ], observed
vehicles in dashcam videos. However, given that one of object’s bounding box) rather than the entire frame, also
the major challenges within the dashcam dataset involves forecasting their trajectories. Additionally, leveraging insights
obscured scene participants, an object tracking strategy known from their prior work in [9], the researchers integrated the
as DeepSort [41] is also implemented. This technique aims to movement of the camera within the ego-vehicle with the
ensure consistent optical flow in the presence of occlusions. positioning of other objects in the scene. This integration was
Indeed, in the TAD (Traffic Anomaly Detection) approach, not reflected in the anticipation of future bounding box positions
only [22] but also [37], [38], and [44] all incorporate Deep- for the current frame. Elaborating further, information from
Sort [41]. DeepSort, an extension of the Simple Online and the bounding boxes in the current frame (It ) and optical flow
Real-Time Tracking (SORT) method [45], addresses the issue data, extracted through a region-of-interest pooling (RoIPool)
of unstable identity tracking in SORT. SORT often encounters operation, were separately encoded. In other words, observed
difficulties in maintaining consistent object identities due to image evidence Ot which is a relative motion vector that is
frequent identity changes and resulting uncertainties during expanded from each bounding box (Ot = R O I Pool(It , X t )).
prolonged occlusions. In contrast, DeepSort [41] operates in The resulting hidden states were then input into a location
two phases: an offline step, where each object’s evaluation decoder to forecast the future positions of the bounding boxes.
metric is computed, and an online phase, where these metrics With this localization technique established, the researchers
guide object tracking. According to this method, if a tracked aimed to identify accidents by detecting significant deviaobject is lost or obscured, a Kalman filter predicts potential tions in the trajectories and locations of objects from their
object positions in subsequent frames within a limited time ground truth frames. While their approach seemed theoretiwindow (age) based on proximity to the lost object. If no cally sound, it encountered challenges in accurately identifying
plausible match is found, the object is considered to have accidents due to the dynamic background introduced by the
left the scene, and its track is terminated. Moreover, when ego-car. Among the three evaluation metrics proposed in
new object tracks emerge, they undergo evaluation against their approach, one particularly effective measure involved
existing tracks. Only if deemed genuinely new are they computing the maximum standard deviation (STD) across all
assigned reliable metrics; otherwise, they are removed after predicted bounding boxes for each object within a frame,
three consecutive frames. In the context of [9], the application based on its previous frames. Taking an average of these STD
of the DeepSort [41] object tracking technique on bounding values across all objects’ bounding boxes provided a means
boxes leads to the encoding of depth and distance attributes to gauge the presence of anomalies or accidents in the scene.
of vehicles from the viewpoint. Simultaneously, by encoding The summary of their method is as follows:
dense optical flow, alterations in vehicles’ dimensions, appear
initialize,
if i ∈ C and i ∈
/ D

ance, and motion at the per-pixel level are extracted. During

 (i)
X
,
if
i
∈
C
and
i
∈
D
decoding, temporal bounding boxes are predicted in relation
t
T r ck[i].X t =

to their previous frames, extrapolating their path. To account
if
i
∈
/
C
and
i
∈
D

 T r ck[i].Ŷ(t−1) ,
for the ego-vehicle’s motion in predicting future bounding
and T r ck[i].Age <A
boxes, a frame-by-frame camera coordinate transformation is
(4)
calculated.
T r ck[i].Ŷt = F O L(T r ck[i].X t , Ot , E t )
(5)
N

B. Unsupervised TAD: The Baseline
Drawing inspiration from their object localization technique outlined in [9], the researchers in [22] introduced
an unsupervised methodology for analyzing dashcam videos
without the need for labeled data, named Future Object
Localization based TAD (FOL-TAD). Their approach not only

F O L − Max ST D =

1 X
(i)
max STDδj=1 (Ŷt,t− j )
{C x ,C y ,ω,h}
N

(6)

i=1

C. Unsupervised TAD: The State-of-the-Art
In a later examination by Yao et al. [38], the importance
of pinpointing the anomaly’s location within the frame or

8362

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

identifying the involved road participants in practical driving
assistance applications was emphasized. This was in contrast to earlier methods that utilized dashboard cameras [8],
[46], [47] to identify anomalous frames. In [38], researchers
aimed to not only detect anomalous events but also localize
anomalies within frames or identify anomalous road participants. On one hand, prior unsupervised video anomaly
detection (VAD) methods that operated on a frame-by-frame
basis [36], [48], [49], [50], [51], [52] struggled to predict
or reconstruct frames from rapidly moving dashcam videos.
Conversely, object-centric frame-based approaches like the one
presented in [22] heavily relied on object tracking techniques
to determine object motion in the scene, which still encountered challenges with occlusions. In response, the researchers
in [38] proposed a synthesis of their previous object-based
method from [22], specifically the STD-based FOL, with
the frame-based approach of [36], which is called FOLEnsemble. Their ensemble-based FOL computed an average
anomaly score by mapping the object-based anomaly score
from [22] to a pixel-level anomaly score, similar to the
approach in [36]. Furthermore, the study [38] introduced a
comprehensive traffic VAD dataset called Detection of Traffic
Anomaly (DoTA). This dataset included annotations for temporal, spatial, and categorical information, making it useful not
only for anomaly detection but also for action recognition and
online action detection (discussed in section V). Additionally,
the researchers introduced a novel spatiotemporal evaluation
metric for VAD, known as STAUC, which offered several
advantages over traditional evaluation metrics (discussed in
section VI). It is worth noting that although methods in
unsupervised TAD are free of any accident/normal labels for
frames or clips, the preprocessing step of object detection,
which is not considered as part of TAD methods, still use
bounding boxes’ annotation for detecting objects.
III. T RAFFIC ACCIDENT D ETECTION VIA
S ELF -S UPERVISED L EARNING
A. Unsupervised vs Self-Supervised TAD: The Difference
Since both unsupervised and self-supervised learning are
techniques that do not rely on labeled data, this section first
starts with providing a distinguishing explanation of these two
methods. The fundamental contrast between self-supervised
learning and unsupervised learning lies in the manner they
generate learning signals. In self-supervised learning, the
model generates its own signals for learning from the available
data, whereas unsupervised learning focuses on identifying
patterns or structure within data without explicit labels or
guidance, such as exact location of objects, light intensity and
exact color [53]. It is important to recognize that distinguishing
between these two concepts can occasionally be nuanced, and
the boundary between them might not always be precisely
defined. Moreover, certain techniques could belong to both
categories, as they utilize a blend of self-generated signals and
unsupervised exploration of data. In the context of TAD, such
feature labels are extracted from appearance and motion within
objects’ bounding boxes and also from the whole frame. What
can make these features more reliable is to extract independent

ones by using similarity graph such as in [37] and using
them in ensemble way [37]. Due to the lack of application of
anomaly detection concepts in dashcam videos and even usage
of unsupervised and self-supervised methods, studies of [54]
suggested an unsupervised baseline to fill this gap. Inspired
by their research, the initial idea of self-supervised learning in
Traffic Accident Detection (TAD) was first introduced in [40]
which was then evolved into [37].
B. Fundamentals of Self-Supervised TAD
As the only accident detection study on trucks’ footage,
the scholars from [54] introduced a comprehensive compilation of truck dashcam videos named RetroTrucks, which
constitutes a curated dataset featuring various instances of
both regular and accidental truck driving scenarios. They
employed two techniques, namely one-class classification
and reconstruction-based anomaly detection, using existing
static-camera datasets as well as the RetroTrucks dataset. Utilizing the Support Vector Data Description (SVDD) technique
proposed by [17] and the inflated 3D convnet (I3D) introduced
by [55], they demonstrated that one-class classification struggles to generalize effectively across a diverse range of normal
scenarios, as evidenced by conventional datasets like [50]
and [56]. However, in the context of their reconstructionbased approach, they established an autoencoder based on
the I3D architecture. An investigation into cases of failure
unveiled that the reconstruction-based method outperforms the
one-class classification method in identifying anomalies that
showcase new visual characteristics. However, sole usage of
such a reconstruction based method is not efficient enough
to detect anomalies that involve complex object interactions.
Consequently, in order to enhance the detection of such
object-related anomalies within the scene, by drawing inspiration from [57], the researchers introduced an additional parallel
feature extraction process. This process incorporates region
proposal network (RPN) and RoIAlign modules [58], [59] to
capture these interdependencies, forming a similarity graph.
This graph evolves over time through the utilization of a
graph convolutional network (GCN) module. The inclusion
of this supplementary module yielded improvements in both
the one-class classification and reconstruction-based methods,
as demonstrated by their findings.
C. Self-Supervised TAD: The Baseline
Drawing inspiration from the research conducted by [36]
and [34], the investigation presented in [40] introduced a
self-supervised technique rooted in Generative Adversarial
Networks (GANs), which combines frame and object prediction. In contrast to the approaches taken by [9] and [22], which
exclusively rely on object optical flow, the work of [40] took
a progressive stride by not only considering object movements
based on optical flow (utilizing the Flownet 2.0 network [60]),
but also by predicting object positions using spatial attributes.
These spatial features were derived through Mask-RCNN and
indexed using DeepSORT. By harnessing the spatial characteristics of both objects and frames, the authors aimed to leverage
abrupt changes in the background as a meaningful cue for

ROCKY et al.: REVIEW OF ACCIDENT DETECTION METHODS USING DASHCAM VIDEOS

accident detection. In essence, the approach proposed by [40]
integrates both the global background context across frames
and the localized consistency in object motion and appearance.
The ultimate goal was to identify accidents through deviations
in frame predictions, object locations, and object attributes.
The effectiveness of their method was evaluated on the Honda
Egocentric View Intersection (HEV-I) dataset as well as the
A3D dataset.
D. Self-Supervised TAD: The State-of-the-Art
Building upon their earlier research detailed in [40],
the scholars in [37] extended their TAD model, called
Self-Supervised Consistency (SSC), to encompass various
triggers of anomalies, including anomaly in spatial change
(frame prediction), motion patterns (object detection and
trajectory), and overall scene context (spatiotemporal interactions between objects), which creates a multi-task model.
More precisely, the frame prediction module consists of a
pair of encoders (enc) designed to extract spatial features
from frames (Z t = enc(I1 , . . . , It )) and the video’s optical
flow tensor (utilizing the Flownet 2.0 [60], i.e., m 1:(t−1) =
enc(Flownet2(I1 , . . . , It ))). Subsequently, these two sets of
features are input into a decoder (dec) to generate anticipated future frames ( Iˆ(t+1) = dec(m t + Z t ) and m t =
ConvL ST M(m 1:(t−1) )). In their module for predicting future
object localization, the researchers in [37] adopted the principles of the multi-object tracker DeepSort [41]. They proposed
an adaptation of this technique by implementing a reverse
application to address instances of incomplete or inaccurate
object detections. Subsequently, the states of the objects are
extracted through the utilization of the ROI pooling operator (R O I p). Ultimately, a fully-connected decoder (FC) is
employed to calculate the forthcoming positions of objects in
the next frame, Ŷ(t+1) , as follows:


 1:NT

NT
1:N T
Ŷ(t+1)
= FC enc X 1:t
+ enc R O I p(m t , (X 1:t
)
(7)
1:Nt
In which X (1:t)
are bounding boxes of N T objects in time
series frames of 1 to t.
Furthermore, by recapping previous works, it was observed
that frame prediction-based TAD techniques, such as the
approach presented in [36], can be susceptible to rapid camera movements and significant shifts in illumination during
normal driving, leading to imprecise predictions. Conversely,
trajectory-based TAD methods, exemplified by [22], identify
accidents through deviations in the variance of object trajectories. Thus, To handle scenarios where accident-involved
entities enter the scene within a very limited timeframe,
and rendering trajectory prediction is ineffective, researchers
in [37] introduced a novel visual scene context (VSC) feature
as another aspect to their multi-task model of TAD. To extract
VSC features, first background of object bounding boxes
are removed by Deformable Convolution Neural Network
(D-CNN) [61]. Then, ROIAlign [59] is applied to extract
objects’ features and the rearranged (transposed) of these
features are called embedding features (Rt ). Next, inspired
from the study of [54], embedding features and similarity

8363

matrix of these features (St ) are fed as nodes to GCN to create
the final VSC features (gt ) Eq. 8.



1:Nt
R(t+1) = Rearrange ROIAlign DCNN(X (t+1) , I(t+1) )
g(t+1) = GCN(R(t+1) , S(t+1) )

(8)

1:Nt
where X (t+1)
and I(t+1) are predicted object location and predicted frame at time (t+1). To acquire the most efficient VSC
features, and inspired by [36], they adapted GAN method, for
which similar loss functions to that of Eqs. 1-3 were applied.
Finally, accident detection in the method of [37] is fulfilled
through an efficient fusion of these modules following by the
smoothing filter of Savitzky-Golay filter [62].

IV. T RAFFIC ACCIDENT D ETECTION W ITH
S UPERVISED L EARNING
In this section, the methods that addressed the problem
of accident detection by using accident annotated dataset are
discussed. While [29] tried to deal with this problem by
calculating the movement parameters of overlapped vehicles,
[15] tried to provide a real-time accident detection method.
Although their results can be superior in comparison to
unsupervised or self-supervised ones, such methods may not
be the future direction of TAD due to the realistic fact
that not all videos with different types of accidents can be
labeled. That being said, the techniques that have been used
within each method can cite some ideas to be applied to any
unsupervised/self-supervised methods.

A. Basic Supervised TAD
Establishing their supervised method on motion characteristics, researchers in [29] developed their accident detection
method on acceleration, trajectory and angular variation of
cars, named Movement (motion) Parameters method. To attain
these key variables, they employ Mask R-CNN [59] for vehicle
detection and employ the centroid tracking algorithm [63] to
establish vehicle trajectories. According to their methodology,
for an accident to occur, the bounding boxes of vehicles should
exhibit overlap and align within the same lane, which they
accomplish through the application of Aggarwal’s lane detection technique [64]. Subsequently, they compute the Euclidean
distance between centroids of vehicles in consecutive frames,
which yields the trajectory parameter. This parameter is then
used to determine the angle of trajectories between intersecting
vehicles, indicating an unusual angle. Moreover, by utilizing
the Lucas-Kanade method [65], they compute the pixel-based
speed of vehicles within the scene, consequently deriving the
absolute speed and change of acceleration for each vehicle.
This information aids in identifying any abnormal change in
acceleration. Their approach also detects anomalous trajectories by considering the temporal angle of a vehicle’s trajectory.
Ultimately, an accident occurrence is determined through a
weighted function that combines these three aforementioned
parameters.

8364

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

B. Supervised TAD: The State-of-the-Art
As one of the state-of-the-art methods in TAD, the study
of [15] provides a real-time method that suits Vehicular
Ad hoc Networks (VANET) environment called Coarse-toFine clustering. Their frame-based supervised method first
conducts coarse detection to find all probable accident frames,
and then, determine the actual accident frames through the
fine detection stage. In their coarse detection stage, [15]
extracts motion features using Histogram of Optical Flow
(HOF) features [27] using 15 consecutive frames and form a
temporal ordinal features of frames (V = {v1 , v2 , . . . , vm } =
H O F(I1 , I2 , . . . , IT ), m = T − 15 and T refer to Total
frames) along with their labels (L = {l1 , l2 , . . . , lm }). To prepare these temporal features for later clustering, they applied
a two-stage subnetwork neural node (SNN) structure as a
feature representation, called refinement SNN(R-SNN)([66]).
In its first stage (preprocessing), feature vectors of different feature extraction methods are normalized and aligned
consecutively into a super-state vector. Next, in the second
stage (Width-growth), first an R-SNN is initialized, and then
additional R-SNNs are concatenated, iteratively. The origin
of SNN technique has initially emerged from Network-innetwork (NIN) concept of [67] in which every single node
in a hidden layer is replaced by a neural network itself, called
the subnetwork. This technique tries to alleviate the problem
of over-fitting and getting stuck in local minimums of Deep
Neural Networks (DNNs) models. This problem especially
occurs when DNN models try to process a small-scale dataset
which are dependent on the backpropagation (BP) learning.
Leveraging the utility of R-SNN as a feature representation
method [66], the researchers in [15] compress the temporal
attributes into a more streamlined feature matrix. This matrix
(AcN = R − S N N {V, L}), encompassing frame features and
labels, undergoes clustering through a graph-based approach
named self-representation constrained low-rank representation
(SRLRR) [64], [68]. Subsequently, by employing the normalized cut (Ncut) method [69], potential frames (SCoar se ) with
accidents are identified Eq. (9).




SCoar se = N cut a f f init y S R L R R(AcN )
(9)
Moving on to the fine detection phase, the process unfolds
as follows: Initially, Faster-RCNN (FRCNN) [58] is applied
to these potential frames to identify objects within each
frame. This involves utilizing both the log-likelihood of object
detection and the regression loss pertaining to their positions in
the frame. Following that, in conjunction with the established
objects in the frames, the feature vectors extracted from the
final convolutional layer of Faster-RCNN are sorted in two
ways: one based on their spatial placement in the frame and
the other according to the sizes of their bounding boxes, i.e.,
obj
obj
{Fi−sp , Fi−sz } = F RC N N (si ∈ SCoar se ) and obj ∈ {1 : N T }
where N T is the total detected objected in one of Coarse
Frames. These grouped feature vectors, accompanied by their
obj
respective bounding boxes (X i ), are individually fed into
the R-SNN framework introduced in [66], resulting in the
generation of efficient encoded features presented as a matrix,
sp
obj
obj
(i.e., Ai1 = R S N N (Fi , X i ) and Ai2 = R S N N (Fisz , X i )).

Finally, the two resultant matrices are merged (Concat)
into a comprehensive feature representation. With the aid
of accident/non-accident labels provided (li ) in the DoTA
dataset [15], a supervised classification is executed using the
Support Vector Machine (SVM) algorithm Eq. (10).


(10)
S Fine = SV Mi∈Coar se Concat (Ai1 , Ai2 ), li
V. DATASET
In this section, the evolution of dataset that has been introduced in the TAD literature is discussed. It is worth noting that
since all accident detection and accident anticipation methods
are mainly applying frame-based techniques, many of them
provide the number of frames instead of length of videos as the
information of each dataset video. In the upcoming discussion,
we will explore how Figure 5 illustrates the annotation method
used in the majority of publicly accessible datasets. In a
general context, as it is shown in the figure 5, the difference
between datasets comes from the length of their trimmed
clips, their before and within and after accident intervals and
most importantly their approach toward annotation. While
in some datasets have only annotated accident objects from
beginning to the end of clip, others have done the opposite by
just annotating frames as normal/accidental and some have
the annotation of both frames and objects. The amount of
information that has been provided in each annotation also
varies. In the following each of the available TAD dashcam
dataset in the literature will be discussed in details.
A. SA
As the baseline of accident anticipation and inspiring for
accident detection, [8] introduced the very first dashcam
dataset, namely Street Accidents (SA)– also known as Dashcam Accident Dataset (DAD). They collected a variety type
of accidents from Youtube recorded in six major cities in
Taiwan with quality of (1280 × 720 p in resolution). In their
dataset, the temporal annotation in each video frame comprises type of objects, bounding box of objects and flag
them as accidental/non-accidental object through the course of
time. More specifically, their annotation determines accidental
objects from beginning to the end of video (not the beginning
and the end of accidental frames). With overall number of
678 accident videos, they used less than 10% of videos for
training object detector. As a result, from the rest (620 videos),
1,750 clips were sampled (35% accident positive), where each
clip consists of 100 frames (4 seconds, i.e., 25 frame per
second (fps)), and in those containing accident, clips were
trimmed to have accident at last 10 frames. Their purpose
on the clip trimming approach was to apply prior frames for
accident anticipation and they further randomly divided these
clips into a quarter for testing and the rest for training.
B. CCD
In another accident anticipation approach, Studies of [70]
collected more accidental dashcam videos (in comparison to
SA) from YouTube (1280 × 720 p in resolution) and is named

ROCKY et al.: REVIEW OF ACCIDENT DETECTION METHODS USING DASHCAM VIDEOS

8365

Fig. 5. First row: In SA (DAD) [8], accidental objects are flagged from beginning to the end of clip regardless of accident time, where red boxes are accidental
objects and green boxes are uninvolved objects in the scene (annotation does not include accidental frames). Second row: In CCD [70], only accidental frames
are annotated (not the accidental objects), where red boundaries are accidental frames and green boundaries are considered as normal frames. Third row: In
DADA [71], frames are annotated in the intervals of before crush-object appearance (normal scene), before accident (crush-objects in the scene), accident
interval and after accident frames (DADA has not released bounding boxes’ information. N.B., their annotation considers frames as accidental from the
appearance of collision objects in the scene, which are determined with red boundaries, while frames of before crush-object appearance and after accident are
colored with green as normal frames). Row fourth: In DoTA [38], frames are divided into before accident (labeled as normal (green border), accident interval
(red border) and after accident (green border). Based on annotator discretion frames are labeled accidental when accident is foreseeable, and bound boxes for
non-accidental objects are not provided.

Car Crash Dataset (CCD). Their temporal annotation has
a binary label, i.e., accidental frames are labeled 1 during
the time interval of collision. Additionally, their annotation
comprises the starting point of the trimmed clip in the original
video, Youtube ID of that original video, time of recording
(day/night), weather condition of footage and the involvement
of ego-vehicle. It is worth noting that on their released
version of annotation, [70] did not provide bounding box
information of objects in video frames. Besides, in contrary to
SA [8], CCD’s annotation only determines accidental frames
(not the accidental objects in the scene), and based on this
released annotation, there is no information about objects in
the scene. In their trimmed videos with 50 frames (5 second
length, 10 fps), the occurrence of accident is randomly placed
in last 2 seconds, generating overall 1,500 accidental video
clips, which is half of the number of normal videos and
the normal videos themselves are catered from BDD100K
dataset [72]. Overall, the CCD comprises 4,500 video clips
in which the ratio of testing videos is a quarter of that of
training ones.
C. DADA
As another available dashcam dataset, authors of [71] introduced their dataset named DADA, consisting 2,000 videos

(14-second length) with the resolution of 1456 × 660 (30 fps).
According to the purpose of their research, [71] wanted to
add additional information to dashcam dataset using driver’s
attention. Therefore, different from datasets like SA [8] AND
CCD [70] that were trimming frames to assign accident
interval within last ten frames for accident anticipation, videos
catered by [71] contain before and after accident intervals
along with the accidental interval. In contrast with [8] and [70],
in addition to objects’ bounding boxes in each video frame
which are not released in their available dataset), they created
a visualized map of crash-object locations. The term “crashobject” in their study is defined as object involved in accident,
and the accident interval in their study is started when half of
crash-object appears in the scene and is ended when anomaly
in the scene is over (normal movements of objects). According
to their definition, in accidental clips, frames are flagged as
accidental from the point that objects involve in collision
appear in the scene. Moreover, their spatial object annotation
does not include non-accidental objects in the scene. The
DADA is categorized in 54 type of videos based on accident
participants and they were further classified into two large
sets, ego-car involved and ego-car uninvolved. Later, authors
of [71] released their whole dataset in [47], where they called
it DADA-2000.

8366

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

D. CST-S3D
Recently, based on the study of [73], the DADA-2000, [71]
and [47], has four commonly occurring mismatch annotations,
which consists of labeling uninvolved ego-car as involved one,
wrong category annotation, providing video games instead of
real accident clips, and annotating accident video as normal.
Their assessment also suggests that DADA-2000 contains only
520 videos of ego-car involved and 493 videos of ego-car
uninvolved (overall of 1,013 annotated videos). With respect
to shortages in DADA-2000 and owing to the insight of [73]
where they suggests that safety of a vehicle stems from
preventing ego-car involved incidents, [73] only re-annotates
those videos of DADA-2000 where ego-car was involved.
To strengthen the safety of their model, they also consider
near-miss incidents as accident in their re-annotation. Furthermore, they suggested that there is no clarity to define before
accident interval for ego-car involved accidents. As a result,
in their re-annotation, they merged the whole time interval
of before, within and after accident intervals of DADA-2000
into an incident interval and considered a two-second interval
transient period, before considering a normal time interval.
E. A3D
Next, in [22], AnAn Accident Detection (A3D) was introduced as the very first dashcam dataset that was introduced
for TAD and was collected (with 10 frames per second) with
similar number of dashcam accident videos from Youtube
to that of CCD [70] and with different number of frames
in each clip. In opposite to CCD that determines accidental
frames in each clip according to the interval that the collision
has happened, in A3D of [22], the start point of accident
interval is considered when accident is inevitable (which
depends on three human annotators’ consensus), not when
the collision takes place, and the end point is defined (same
as DADA [47], [71]) when scene is no longer anomalous
(normal movement of objects). A3D annotation also includes
start and end times of clip from original video, original video
name, labels for accidental and normal frames, whether the
ego-vehicle is involved, and whether ego-vehicle is the only
vehicle involved in accident. Notably, A3D does not have
any bounding box information of vehicles. Besides, although
videos have been collected in different weather conditions, different road environment (urban/countryside) and with different
road participants, (unlike CCD [70], SA [8]) the dataset’s
annotation does not provide any information in this regard.
Following the instruction suggested in their github showed
failure to download A3D due to unavailable Youtube links.
F. HEV-I
Before introducing their FOL-TAD in [22], researchers of
that study focused on considering ego-vehicle’s motion on
predicting future location and dimensions of vehicles in the
scene [9]. In their study, a non-accidental dataset was introduced, called Honda Egocentric View-Intersection (HEV-I).
Recorded with the rate of 10 fps in San Francisco, U.S., HEV-I
consists of 230 videos with 1280×640 p resolution of different
lengths (10)-60 seconds), and is catered for distinguishing

vehicles in the scene with a continuous dynamic background.
Due to fast-paced vehicles in the scene and limited point of
view, [9] divided videos into two-second clips in which the
location and dimensions of viewed vehicles in the second half
are calculated according to assessment in first half using their
trajectories.
G. DoTA
To address the issue of Youtube video URL lost and provide
a richer dashcam video dataset, researchers of [22] introduced
a new dataset called Detection of Traffic Anomaly (DoTA)
in [38] which is an extension to their previous dataset (A3D).
In comparison with older dataset, DoTA not only consists
of more than 3 times the number of videos with previous
mentioned annotation information (A3D), but also provides
start and end of anomaly frames with labeling all frames
(binary and with name tag), number of frames, day/night
label, determining accident type (with considering ego-vehicle
involved in all categories), bounding boxes of objects and
optical flow of the objects in each clip. Same as A3D [22],
in DoTA [38] no annotation is provided for different weather
conditions, though dataset provides variety of the weather. All
videos have been provided with 10 fps due to avoid repetition
of information in close frames (even though original videos
were 30 fps). Same as DADA [71], DoTA [38], based on their
provided spatio-temporal annotation, has separated the time
intervals of videos into before accident, accident and after
accident, although they provided different preference on the
beginning of accident. More precisely in DoTA [38] frames are
considered accidental/anomalous when accident is inevitable
and ends when anomalous objects become stationary in the
scene or have left the scene. While they claimed such a start
annotation is for the purpose of early accident anticipation, the
term “inevitable” makes the decision on the start of anomaly
arbitrary. N.B., only accidental objects are annotated.
H. CTA
Inspired by vehicles’ history report of accidents catered
by police department in [74], researchers in [75] created a
video dataset called Causality in Traffic Accident (CTA) to
analyze this purpose. Collecting almost 2,000 accident videos
from Youtube (mainly dashcam footage and few surveillance
cameras), [75] determined shot boundaries using FFmpeg
(with manual justification) to label causal and effect frames.
More precisely, in CTA annotation, an effect’s start time is
when a vehicle first experiences physical damage, and its end
time is when there is no longer any activity related to the
event happening to the objects involved. On the other hand,
frames are labeled causal when any road participant shows
anomalous behaviour and it ends at frame when scene becomes
normal, though in actual cases cause’s end frame is considered
as beginning of effect frames.
I. NIDB
Instead of collecting accident footage, researchers in [76]
gathered over 6,000 near-miss traffic incident database (NIDB)

ROCKY et al.: REVIEW OF ACCIDENT DETECTION METHODS USING DASHCAM VIDEOS

8367

from more than 100 taxis using a dashcam recording system
that is triggered to record for 15 seconds when speed reduction
rate, in an abrupt braking, exceeds half of gravity force
equivalency. With overall of seven categories, they divided
incidents into high/low pedestrian, high/low bicycle, high/low
vehicle and normal clips, where normal implies none of
the mentioned incidents has happened. According to their
approach, high incident is when probability of accident was
high and it required serious reaction of driver, while for low
incidents, the scenario is opposite and system is required to
give just an alarm.

B. Area Under ROC Curve (AUC)

J. STAG

C. Accident Detection Rate and False Alarm Rate

In order to evaluate and refine their Spatio-Temporal Action
Graph (STAG) approach, researchers in [46] created the
Collision dataset. With average duration of 40 seconds, this
dataset comprises ego-vehicle’s accidents (about 750 videos)
and near-miss incident (60 videos) that requires evasive action
of the driver to prevent a crash. The Collision dataset was
collected using dashcam which was triggered with Inertial
Measuring Unit (IMU) and gyroscope readings, though distinguishing of accident and near-miss records were fulfilled
by human annotator. To avoid duplication and examine few
shot methods, they also applied a 5 fps filter to provide a
low-rate dataset too. regardless of frame rate, each accidental
or near-miss video was divided into three equal segments, with
only one segment of accidental videos being positive.

As a way of assessing the performance of VAD, [29]
suggested to use Accident Detection Rate (ADR) which is
the ratio of truly detected accidents to the total number of
accidents, i.e, ADR is actually parameter named Recall in the
literature or TPR. Additionally, they applied False Alarm Rate
(FAR) for comparison, which determines the ratio that system
gives false alarm in comparison to total alarms that have been
sounded. FAR is precisely FPR.

K. RetroTruck
In contrary to all mentioned dashcam dataset in literature,
[54] collected more than 470 dashcam footage (25 fps) of
trucks with different duration (7 seconds to 2 minutes) from
YouTube, called RetroTruck. Overall, all anomalous videos
include ego-vehicle–comprising collision, near-misses, lane
crossing incidents, rollover crashes– and they constitute less
than 50% of dataset, where only 25% of these anomalous
videos have temporal binary label (normal/anomalous) for the
purpose of testing. Notably, although dataset is gathered from
different weather and time of day, their annotation does not
provide any information in this regard.
VI. E VALUATION M ETRICS
As discussed in the Future Frame Prediction II, to distinguish an anomaly from normal event in a video, the first
step is to calculate the similarity of predicted frame and
corresponding ground truth frame using PSNR. Then, all
PSNR values of consecutive frames in a video are mapped to
range [0, 1] (Normalization [43]), which are called anomaly
score. All TAD methods use this anomaly score to provide
their evaluation metrics.
A. Qualitative Analysis
As the research of [47], [71] have been conducted in
studying the driver’s attention in predicting and detection
accidents, the qualitative analysis has always been part of all
VAD studies to give an intuitive understanding of each method
and how their approach tries to detect accident within time
frame.

Being one of the most popular evaluation metrics in the
anomaly detection literature, [48], [50], [77], [78], in the
concept of VAD, after calculation of the anomaly score in each
frame of a video, the temporal concatenation of these scores
form the Receiver Operation Characterstic (ROC) curve. Area
Under Curve (AUC), in this context, determines the location of
possible accident through time interval. The higher the value of
AUC, the better suggested model distinguishes accident from
non-accident/normal events.

D. Time Metrics
While all the state-of-the-art methods use the AUC as
one of their evaluation metric, the Coarse-to-Fine clustering
approach [15] also suggested the comparison of methods with
regards to Number of Parameters, Training Time and Average
Detection Time, as a way to show compliance of different
approaches to VANET environment.
E. Success Rate (SR) Curve
In addition to AUC, inspired by object tracking methods
such as [79], the study of [37] also suggested to compare
accident detection methods’ performance using Success rate
curve, which relies on bounding box. The overlap score,
a
denoted by S = rrtt ∩r
∪ra , is defined as the ratio of the number
of pixels in the intersection of the tracked bounding box and
the ground truth bounding box to the number of pixels in
their union. The intersection and union are represented by
∩ and ∪, respectively, and | · | denotes the cardinality or
number of pixels in a region. To evaluate the performance of
tracking algorithms, the number of frames with overlap greater
than the specified threshold t0 is counted over a sequence of
frames. The success plot displays the success ratio of frames
at different thresholds ranging from 0 to 1. Assessing the
tracker’s performance based on a single success rate value
at a particular threshold, such as t0 = 0.5, may not be a fair
complete representation. Therefore, the area under the curve
(AUC) of each success plot is utilized to rank the tracking
algorithms. This metric provides a comprehensive comparison
of the method’s adaptability across various driving scenarios.
F. Average Precision (AP) and Mean Average Precision
(mAP)
To make their evaluation more complete, [37] also applied
Average Precision (AP) [80]. The AP (average precision) is
a measure of how accurately a detection model identifies

8368

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

TABLE I
S UMMARY OF C OMPARISON B ETWEEN A LL DASHCAM V IDEO DATASETS

accidents. It is calculated by averaging the precision scores of
all testing videos. Precision is the ratio of correctly identified
accident frames to all detected accident frames, which include
both true positives and false positives. The detection method
determines the positive and negative labels of detected frames
using a pre-defined threshold. In this study, frames with an
occurrence degree of traffic accidents greater than 0.5 are
labeled as positive, and those with lower degree are labeled
as negative.
G. Anomaly-to-Accident (A2A)
based on their temporal annotation of dataset, study of [37]
introduced a metric that can be used for future accident
anticipation studies. According to their definition, a temporal
window called anomaly-to-accident (A2A) for each video
sequence is started when the accident participant appears in
the scene and as a result A2A can help predict accident by
detecting anomalous object or behaviour before collision.
H. Spatial-Temporal Area Under Curve (STAUC) Metric
Being critique of efficacy of AUC, the study of [38]
suggested a novel metric called Spatial-Temporal Area Under

Curve (STAUC). By their account [38], due to being averaged score in each frame, AUC dismisses providing any
information/ accuracy of accident/anomaly region localization
on the spatial axes, which is a fundamental need to assess
the performance of VAD. By comparing the corresponding
score map of true positive frames by applying different VAD
methods, researchers of [38] showed that although AUC of
different methods are similar, their corresponding maps are
different, which advises that these methods’ performance are
considered the same from AUC point of view. This cause,
brought them to introduce new metric, called STAUC. Inspired
by the MVTec Anomaly Detection (MVTec AD) method
of [81], The initial proposal was to compute a scalar known as
the True Anomalous Region Rate (TARR), which is defined as
the fraction of the anomaly score that corresponds to the union
of all annotated bounding boxes relative to all the pixels in the
frame at each time frame. This scalar was intended to indicate
the proportion of the anomaly score that is present within the
actual anomalous region. Initially, TARR was formulated for
anomaly score maps that covered an entire frame. However,
since object-based video anomaly detection (VAD) methods
compute anomalies for individual objects, the concept of

ROCKY et al.: REVIEW OF ACCIDENT DETECTION METHODS USING DASHCAM VIDEOS

TARR was extended to incorporate pseudo-anomaly score
maps. This was achieved by computing the anomaly score of
each pixel as the sum of a 2D Gaussian distribution of scores
that were centered at the pixel’s bounding box. Next, they
defined spatio-temporal true positive rate (STTPR) which is
a ratio of TARR of all true positive predictions to all ground
truth positive frames. In fact, STTPR is a weighted TARR.
From the values of STTPR and false positive rate the plot of
ROC curve is formed which is called Spatial-Temporal ROC
or STROC and the area under this curve is called STAUC.
As the final step and to make their new metric robust against
anomalous region size, they suggested to use an adaptive
N% top anomalous pixels (Nadaptive %) to be used in TARR
computation. This means that for each frame, N is calculated
as the proportion of number of anomalous region pixels to
total number of pixels. The new metric STAUC ≤ AUC in
the case that T A R Rt = 1 ∀t. The summary of all evaluation
metrics has been provided in Table II.
VII. D ISCUSSION AND C OMPARISON
Like every other computer vision problem, as presented
in previous sections, Traffic Accident Detection (TAD) has
been dealt with supervised, unsupervised, and as a newly
introduced approach, self-supervised learning. Regardless of
the approach in each method, all TAD algorithms start with an
object detection method, followed by object tracking technique
and, relying on them, some features are extracted to train a
deep learning model to detect an accident as an anomaly.
A. Comparison of Largest Dataset: DADA and DoTA
Looking into the fundamental details of all mentioned
algorithms, almost every study suggested their own catered
dataset, each of which has been collected and annotated from
mainstream video websites, especially Youtube, and based on
their approach, being annotated accordingly. As a result, any
further study in this field is highly dependant on the way
annotation of dataset has been fulfilled, such as recent attempt
of [73] where they reported wrong annotation of DADA, [71],
and re-annotate part of it for their own research interest.
This means that there is a lack of comprehensive consensus
and protocol in the Intelligent Transportation Systems Society
(ITSS) on TAD dataset annotation which will align all studies
toward complimenting previous ones. (regarding the accuracy
of annotation) and informative dataset with regards to its
temporal, spatial, and categorical annotations of accidents for
frames and objects in the videos, captured from different
countries under different weather and lighting conditions,
appears to be DoTA [38].
B. Dealing With Unreliable Object Detection and Tracking
From the object detection point of view, except the study
of [15] which used Faster-RCNN [58], all other methods [22],
[29], [37], [38], [40], [44] used Mask R-CNN [59]. This
justify the high efficacy of this object detection method. As for
the object tracking, while supervised movement parameters
approach [29] uses centroid tracking [63], all the methods
of [22], [37], [38], [40], and [44] have applied DeepSort [41]

8369

technique (This technique is not utilized in Coarse-to-Fine
method [15]). To alleviate the impact of TAD on unreliable object detection and tracking situation, researchers of
unsupervised approaches tried to apply statistical operators,
FOL-AvgSTD and FOL-MaxSTD variations in [22] and [44]
and the FOL-Ensemble in [38] and [44], when their initial
method faced mis-label objects due to losing some normal
objects in the scene. On the other hand, to deal with unreliable object detection and tracking methods, researchers in
self-supervised method of [37] took further steps in comparison to the unsupervised methods by using the DeepSort
method [41] in backward, extracting visual scene context
feature using GCN, make another ensemble method called
collaborative Multi-Task consistency learning, and finally
smoothing the visual scene context scores using a SavitzkyGolay filter [62]. Despite all the measures that the study of [37]
took in their approach, they still struggled with background
recognition in region of accident’s future frame prediction.
Consequently, their method fails in case of too large or too
small scale objects to be discovered. Their results also down
perform in low intensity environments (nights). This means
that the additional extracted features in [37] has not actually
helped with distinguishing accidental objects from dynamic
background, in comparison of [22].
C. Supervised vs Unsupervised Methods
In terms of comparison between Supervised and Unsupervised accident detection methods, the studies of [15]
showed the superiority of supervised methods, comprising Coarse-to-Fine clustering [15], Fully Connected (FC)
[44], LSTM [82], Encoder-Decoder [83] and TRN [84]
against those unsupervised counterparts such as ConvAE [49],
ConvLSTM [85], AnoPred [36], AnoPred+Mask, FOLAvgSTD+MarginLearning (FOL-AvgSTD+ML) and Ensemble (all in [44]), and FOL-AvgSTD [22]. Their research
justified the effectiveness of methods which take advantage
of motion features (optical flow) in comparison of those who
just consider appearance features. Furthermore, they proved
the superiority of their method due to combining supervised
learning with motion features. Lastly, [15] is the only method
which tries to provide a real-time VANET method by comparing the time and performance with other TAD methods. With
all the strengths that have been mentioned in [15], still there
is a lack of suggestion new feature extraction methods in their
work.
D. Overall Comparison of State-of-the-Art Methods
By and Large, with regards to details of different methods,
the concept of state-of-the-art self-supervised method [37] and
unsupervised method [38] is similar as they extract appearance
and motion features of objects and apply some further processing to reach their final features, which they later apply to train
their accident detection models. By contrast, in supervised
methods, while the approach of [29] is simplistic and cannot
cover many actual accident scenarios, the VANET approach
of [15] is considered more reliable. Despite all mentioned,
what is missing in the state-of-the-art methods of TAD are

8370

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

TABLE II
E VALUATION M ETRICS

influential features that can distinguish foreground accidental
objects from dynamic background of the scene.
E. Introducing Baseline Methods in TAD Comparison Table
As AUC of ROC is the most accepted evaluation metric in
the anomaly detection methods, and consequently in accident
detection field, and while all the state-of-the-art did not apply
their approach on a common dataset, the true comparison
of them requires applying all to the same dataset. Having
said that, contemplating the methods in general, supervised
methods can achieve better results due to having the label
of video frames(accident or no-accident) in comparison to
unsupervised/self-supervised methods, though the unsupervised and self-supervised methods can better generalize their
model for any case out of their available trained dataset.
Therefore, to establish a robust reliable accident detection
method, due to the limitation of available dataset and since it is
unrealistic to have enough sample of each rare accident case,
considering that there are 18 overall classes of accident based
on DoTA dataset, the concentration of future research in this
field would inevitably be in the unsupervised/self-supervised
direction. Since accident detection can be considered as online
binary action detection, labeled with normal and accident
classes, according to [15], [38], and [44], some action detection methods were introduced as a supervised TAD. These
methods include ResNet50 model [89] as their backbone
to extract features and from there four different approaches

were applied, namely FC, LSTM, Encoder-Decoder, and TRN.
The FC model is a three-layer Fully-Connected classification network, while LSTM is a one-layer LSTM to classify
sequential images. As a modified version of LSTM, EncoderDecoder is a model that classify current frames in the encoder
part while in the decoder part future classes are predicted.
As another version of Encoder-Decoder, Temporal recurrent
network (TRN) [88] is having a feedback of future classes
to the encoding part. In [37], another benchmark was used
for comparison with their self-supervised method, namely
DeepMask-FP-TAD[86]. This unsupervised approach utilizes
a deep multi-branch mask network (DMMNet) applies fusion
of features to effectively combine the benefits of optical flow
registering and pixel-level image synthesizing methods. This
results in a more flexible masking network for motion and
appearance fusion in video frame prediction. Specifically, the
mask layer in each branch is employed to adaptively adjust the
magnitude range of estimated optical flow and the weight of
predicted frames by optical flow registering and pixel-level
image synthesizing, respectively. The comparison of TAD
methods has been provided in the Table III.
VIII. F UTURE D IRECTIONS
Despite the mentioned advances, there are still some shortcomings in current methods. As explained in “Section VII Discussion and Comparison”, still state-of-the-art methods
are struggling with having a reliable object detection and

ROCKY et al.: REVIEW OF ACCIDENT DETECTION METHODS USING DASHCAM VIDEOS

8371

TABLE III
C OMPARISON OF ACCIDENT D ETECTION M ETHODS BASED ON T YPES , I NPUTS , O BJECT D ETECTION AND T RACKING ,
AND E VALUATION M ETRICS ON D IFFERENT DATASET

object tracking technique to build their TAD method upon
them. Besides, spatio-temporal localization of anomalies in
driving scenarios can be a helpful way of improving TAD.
Besides, future of the field of accident detection lies within the
unsupervised and self-supervised approaches. Such methods
can be applied to extract the labels of videos directly from
the video scenes and makes the model independent from any
manual labeling of video frames, whether labeling the accidental/normal frame or determining the bounding boxes in each
frame. Another prospect direction is TAD video generation,
which requires powerful computational system. With such
an approach, TAD becomes independent of data collection.
Since occlusion has been one of the main drawbacks in
detection of accidents, this issue should be investigated itself
as a future direction. The real-time detection of accidents is
one of the other aspect to prepare a TAD for real scenario
of autonomous vehicles. For this purpose, models can be
improved to extract features on possible accident scenarios,
instead of continuously computation of features from objects
in the scene. Moreover, as DoTA has classified different
accidents, a possible direction is the fusion of models each
of which is well adapted with limited number of accident
categories and the merged model be able to deal with different
scenarios by activating relevant sub-model. Furthermore, any
TAD method that extracts reliable feature labels to detect
accident can be tried to predict accident too. As another future
direction, understanding different actions that cause accidents
can result in a reliable accident detection/prediction too. All
being said, literature of accident detection and prediction still
lack a cross-modal dataset, in other words, there is not any
dataset that provide accidents and other sources of information
including GPS, LiDAR, radar and connected vehicles dataset
that can help improve the performance of the models.
Additional to the mentioned TAD works and possible future
directions, based on the provided information on tables of
measuring units, available dataset and performance of TAD

methods, disunity of current state-of-the-art methods becomes
clear with regards to different definition for annotation, creating different dataset and consequently, providing results
on non-unanimous dataset. Should the challenge of accident
detection and consequently accident anticipation are expected
to solve, it is of utmost important to converge all research
of TAD by introducing related protocols within intelligent
transportation society. Such a general consensus may include
but not limited to agreement on the accurate definition of
accident, accident interval, before and after accident interval,
which all together can determine the interval of each accident
clip for dataset creation. What is more, as accidents are rare to
happen, the field of TAD deeply suffer from a comprehensive
dataset that could provide additional information rather than
the video footage of accident scenes. Such an extra knowledge
can be time, location (suburbs or downtown, highway or local
road, traffic report of road ahead(congested, heavy traffic, light
traffic, free-flowing) and etc.
IX. C ONCLUSION
This study highlights the primary challenges in accident
detection using dashcam videos. Firstly, because of rapid
motion of the ego-car, distinguishing visually reconstructed
current or future RGB frames from normal non-accidental
scenes, that are given to model in training, is difficult. Secondly, all the TAD methods rely on object detection and object
tracking as their fundamental backbone of their algorithms and
those that were applied in TAD methods still down perform in
case of occlusions and sudden appearance change of incidental
objects in the scene. Thirdly, in order to apply TAD algorithms
in real scenarios of autonomous vehicles, they should perform
accurately in real time which has not yet addressed in literature
except in the Coarse-to-Fine clustering method.
As video processing has a high computational cost, based
on the categories provided in Figure 3, all state-of-the-art

8372

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

methods tried to address TAD issue using frame-based techniques. Furthermore, based on the literature, it is clear that
the problem of TAD with numerous types of accident should
be pursued with unsupervised/self-supervised methods, as it
is non-pragmatic to label all TAD videos and build a model
that can generalize to unseen accident types. To address some
of these challenges, Unsupervised Future Object Localization
(FOL-TAD) was introduced a baseline for TAD where accident
was detected by anomaly in accuracy and consistency of
anticipated objects on future frames of the scene. SSC is
considered as a complimented version of that baseline by suggesting a graph-based fusion of objects’ and frame’s features.
To improve their initial baseline method, authors of FOL-TAD
showed an improvement on their method by proposing the
FOL-Ensemble method. Laying emphasis on time efficiency
aspect, Coarse-to-Fine framework was introduced to address
the real-time performance aspect of TAD.
Finally, this study provided all available dataset and evaluation metric in the field and introduced strengths and downsides
of current methods and by suggesting future direction, depicted
an overall road map for TAD.
ACKNOWLEDGMENT
The authors would like to appreciate Dr. Sima Soltanpour
for her review and valuable feedback on this paper.
R EFERENCES
[1] Road Accidents and Safety Statistics, Government United Kingdom,
London, U.K., 2023.
[2] S. Singh, “Critical reasons for crashes investigated in the national motor
vehicle crash causation survey,” Nat. Center Statist. Anal., New Jersey,
NJ, USA, Tech. Rep. DOT HS 812 506, 2015. [Online]. Available:
https://trid.trb.org/view/1507603
[3] On-Road Automated Vehicle Standards Committee: Taxonomy and Definitions for Terms Related to On-Road Motor Vehicle Automated Driving
Systems, Information Report, SAE Int., Warrendale, PA, USA, 2014.
[4] J. Guo, U. Kurup, and M. Shah, “Is it safe to drive? An overview of
factors, metrics, and datasets for driveability assessment in autonomous
driving,” IEEE Trans. Intell. Transp. Syst., vol. 21, no. 8, pp. 3135–3151,
Aug. 2020.
[5] S. Riedmaier, T. Ponn, D. Ludwig, B. Schick, and F. Diermeyer,
“Survey on scenario-based safety assessment of automated vehicles,”
IEEE Access, vol. 8, pp. 87456–87477, 2020.
[6] E. Yurtsever, J. Lambert, A. Carballo, and K. Takeda, “A survey of
autonomous driving: Common practices and emerging technologies,”
IEEE Access, vol. 8, pp. 58443–58469, 2020.
[7] D. Xiao, W. G. Geiger, H. Y. Yatbaz, M. Dianati, and R. Woodman,
“Detecting hazardous events: A framework for automated vehicle safety
systems,” in Proc. IEEE 25th Int. Conf. Intell. Transp. Syst. (ITSC),
Oct. 2022, pp. 641–646.
[8] F.-H. Chan, Y.-T. Chen, Y. Xiang, and M. Sun, “Anticipating accidents in
dashcam videos,” in Proc. 13th Asian Conf. Comput. Vis., Taipei, Taiwan.
Cham, Switzerland: Springer, 2017, pp. 136–153. [Online]. Available:
https://link.springer.com/chapter/10.1007/978-3-319-54190-7_9#citeas
[9] Y. Yao, M. Xu, C. Choi, D. J. Crandall, E. M. Atkins, and B. Dariush,
“Egocentric vision-based future vehicle localization for intelligent driving assistance systems,” in Proc. Int. Conf. Robot. Autom. (ICRA),
May 2019, pp. 9711–9717.
[10] E. Yurtsever et al., “Risky action recognition in lane change video clips
using deep spatiotemporal networks with segmentation mask transfer,” in
Proc. IEEE Intell. Transp. Syst. Conf. (ITSC), Oct. 2019, pp. 3100–3107.
[11] C. Li, S. H. Chan, and Y.-T. Chen, “Who make drivers stop? Towards
driver-centric risk assessment: Risk object identification via causal
inference,” in Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS),
Oct. 2020, pp. 10711–10718.
[12] G. Plumb, M. T. Ribeiro, and A. Talwalkar, “Finding and fixing spurious
patterns with explanations,” 2021, arXiv:2106.02112.

[13] S. Stabinger, D. Peer, J. Piater, and A. Rodríguez-Sánchez, “Evaluating
the progress of deep learning for visual relational concepts,” J. Vis.,
vol. 21, no. 11, p. 8, Oct. 2021.
[14] G. Puebla and J. S. Bowers, “Can deep convolutional neural networks
support relational reasoning in the same-different task?” J. Vis., vol. 22,
no. 10, p. 11, Sep. 2022.
[15] Z. Zhou, X. Dong, Z. Li, K. Yu, C. Ding, and Y. Yang, “Spatio-temporal
feature encoding for traffic accident detection in VANET environment,”
IEEE Trans. Intell. Transp. Syst., vol. 23, no. 10, pp. 19772–19781,
Oct. 2022.
[16] S. S. Khan and M. G. Madden, “One-class classification: Taxonomy
of study and review of techniques,” Knowl. Eng. Rev., vol. 29, no. 3,
pp. 345–374, Jun. 2014.
[17] L. Ruff et al., “Deep one-class classification,” in Proc. Int. Conf. Mach.
Learn., 2018, pp. 4393–4402.
[18] P. Perera and V. M. Patel, “Learning deep features for one-class classification,” IEEE Trans. Image Process., vol. 28, no. 11, pp. 5450–5463,
Nov. 2019.
[19] D. M. J. Tax and R. P. W. Duin, “Support vector data description,” Mach.
Learn., vol. 54, no. 1, pp. 45–66, Jan. 2004.
[20] P. Zheng, S. Yuan, X. Wu, J. Li, and A. Lu, “One-class adversarial nets
for fraud detection,” in Proc. AAAI Conf. Artif. Intell., vol. 33, 2019,
pp. 1286–1293.
[21] M. Sabokrou, M. Khalooei, M. Fathy, and E. Adeli, “Adversarially
learned one-class classifier for novelty detection,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit., Jun. 2018, pp. 3379–3388.
[22] Y. Yao, M. Xu, Y. Wang, D. J. Crandall, and E. M. Atkins, “Unsupervised traffic accident detection in first-person videos,” in Proc. IEEE/RSJ
Int. Conf. Intell. Robots Syst. (IROS), Nov. 2019, pp. 273–280.
[23] Y. Zhu and S. Newsam, “Motion-aware feature for improved video
anomaly detection,” 2019, arXiv:1907.10211.
[24] W. Sultani, C. Chen, and M. Shah, “Real-world anomaly detection in
surveillance videos,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., Jun. 2018, pp. 6479–6488.
[25] S. Lin, H. Yang, X. Tang, T. Shi, and L. Chen, “Social MIL: Interactionaware for crowd anomaly detection,” in Proc. 16th IEEE Int. Conf. Adv.
Video Signal Based Surveill. (AVSS), Sep. 2019, pp. 1–8.
[26] F. Landi, C. G. M. Snoek, and R. Cucchiara, “Anomaly locality in video
surveillance,” 2019, arXiv:1901.10364.
[27] H. Zenati, C. Sheng Foo, B. Lecouat, G. Manek, and
V. R. Chandrasekhar, “Efficient GAN-based anomaly detection,”
2018, arXiv:1802.06222.
[28] T. Schlegl, P. Seeböck, S. M. Waldstein, U. Schmidt-Erfurth,
and G. Langs, “Unsupervised anomaly detection with generative
adversarial networks to guide marker discovery,” in Proc. 25th
Int. Conf. Inf. Process. Med. Imag., Boone, NC, USA. Cham,
Switzerland: Springer, 2017, pp. 146–157. [Online]. Available: https://
link.springer.com/chapter/10.1007/978-3-319-59050-9_12#citeas
[29] D. Chand, S. Gupta, and I. Kavati, “Computer vision based accident
detection for autonomous vehicles,” in Proc. IEEE 17th India Council
Int. Conf. (INDICON), Dec. 2020, pp. 1–6.
[30] Y. S. Chong and Y. H. Tay, “Abnormal event detection in videos using
spatiotemporal autoencoder,” in Proc. 14th Int. Symp. Adv. Neural Netw.,
Hokkaido, Japan. Cham, Switzerland: Springer, 2017, pp. 189–196.
[Online]. Available: https://link.springer.com/chapter/10.1007/978-3319-59081-3_23#citeas
[31] J. An and S. Cho, “Variational autoencoder based anomaly detection using reconstruction probability,” Special Lect. IE, vol. 2, no. 1,
pp. 1–18, Dec. 2015.
[32] Y. Zhao, B. Deng, C. Shen, Y. Liu, H. Lu, and X.-S. Hua, “Spatiotemporal autoencoder for video anomaly detection,” in Proc. 25th ACM
Int. Conf. Multimedia, Oct. 2017, pp. 1933–1941.
[33] D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1705–1714.
[34] I. Goodfellow, “NIPS 2016 tutorial: Generative adversarial networks,”
2017, arXiv:1701.00160.
[35] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A survey,”
ACM Comput. Surv., vol. 41, no. 3, pp. 1–58, Jul. 2009.
[36] W. Liu, W. Luo, D. Lian, and S. Gao, “Future frame prediction for
anomaly detection—A new baseline,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit., Jun. 2018, pp. 6536–6545.
[37] J. Fang, J. Qiao, J. Bai, H. Yu, and J. Xue, “Traffic accident detection via
self-supervised consistency learning in driving scenarios,” IEEE Trans.
Intell. Transp. Syst., vol. 23, no. 7, pp. 9601–9614, Jul. 2022.

ROCKY et al.: REVIEW OF ACCIDENT DETECTION METHODS USING DASHCAM VIDEOS

[38] Y. Yao et al., “DoTA: Unsupervised detection of traffic anomaly in
driving videos,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 45, no. 1,
pp. 444–459, Jan. 2023.
[39] D. Xiao, M. Dianati, W. G. Geiger, and R. Woodman, “Review
of graph-based hazardous event detection methods for autonomous
driving systems,” IEEE Trans. Intell. Transp. Syst., vol. 24, no. 5,
pp. 4697–4715, May 2023.
[40] J. Qiao, J. Fang, D. Yan, and J. Xue, “Driving accident detection by
self-supervised adversarial appearance-motion prediction in first-person
videos,” in Proc. 3rd Int. Conf. Unmanned Syst. (ICUS), Nov. 2020,
pp. 1083–1088.
[41] N. Wojke, A. Bewley, and D. Paulus, “Simple online and realtime
tracking with a deep association metric,” in Proc. IEEE Int. Conf. Image
Process. (ICIP), Sep. 2017, pp. 3645–3649.
[42] A. Dosovitskiy et al., “FlowNet: Learning optical flow with convolutional networks,” in Proc. IEEE Int. Conf. Comput. Vis. (ICCV),
Dec. 2015, pp. 2758–2766.
[43] M. Mathieu, C. Couprie, and Y. LeCun, “Deep multi-scale video
prediction beyond mean square error,” 2015, arXiv:1511.05440.
[44] Y. Yao, X. Wang, M. Xu, Z. Pu, E. Atkins, and D. Crandall, “When,
where, and what? A new dataset for anomaly detection in driving
videos,” 2020, arXiv:2004.03044.
[45] A. Bewley, Z. Ge, L. Ott, F. Ramos, and B. Upcroft, “Simple online
and realtime tracking,” in Proc. IEEE Int. Conf. Image Process. (ICIP),
Sep. 2016, pp. 3464–3468.
[46] R. Herzig et al., “Spatio-temporal action graph networks,” in Proc.
IEEE/CVF Int. Conf. Comput. Vis. Workshop (ICCVW), Oct. 2019,
pp. 2347–2356.
[47] J. Fang, D. Yan, J. Qiao, J. Xue, and H. Yu, “DADA: Driver attention
prediction in driving accident scenarios,” IEEE Trans. Intell. Transp.
Syst., vol. 23, no. 6, pp. 4959–4971, Jun. 2022.
[48] C. Lu, J. Shi, and J. Jia, “Abnormal event detection at 150 FPS
in MATLAB,” in Proc. IEEE Int. Conf. Comput. Vis., Dec. 2013,
pp. 2720–2727.
[49] M. Hasan, J. Choi, J. Neumann, A. K. Roy-Chowdhury, and L. S. Davis,
“Learning temporal regularity in video sequences,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2016, pp. 733–742.
[50] W. Luo, W. Liu, and S. Gao, “A revisit of sparse coding based anomaly
detection in stacked RNN framework,” in Proc. IEEE Int. Conf. Comput.
Vis. (ICCV), Oct. 2017, pp. 341–349.
[51] R. Morais, V. Le, T. Tran, B. Saha, M. Mansour, and S. Venkatesh,
“Learning regularity in skeleton trajectories for anomaly detection in
videos,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2019, pp. 11996–12004.
[52] R. T. Ionescu, F. S. Khan, M.-I. Georgescu, and L. Shao, “Object-centric
auto-encoders and dummy anomalies for abnormal event detection
in video,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2019, pp. 7842–7851.
[53] J. Zbontar, L. Jing, I. Misra, Y. LeCun, and S. Deny, “Barlow Twins:
Self-supervised learning via redundancy reduction,” in Proc. 38th Int.
Conf. Mach. Learn., vol. 139, M. Meila and T. Zhang, Eds., Jul. 2021,
pp. 12310–12320.
[54] S. Haresh, S. Kumar, M. Z. Zia, and Q.-H. Tran, “Towards anomaly
detection in dashcam videos,” in Proc. IEEE Intell. Vehicles Symp. (IV),
Oct. 2020, pp. 1407–1414.
[55] X. Wang, R. Girshick, A. Gupta, and K. He, “Non-local neural
networks,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
Jun. 2018, pp. 7794–7803.
[56] W. Li, V. Mahadevan, and N. Vasconcelos, “Anomaly detection and
localization in crowded scenes,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 36, no. 1, pp. 18–32, Jan. 2014.
[57] X. Wang and A. Gupta, “Videos as space-time region graphs,” in Proc.
Eur. Conf. Comput. Vis. (ECCV), 2018, pp. 399–417.
[58] S. Ren, K. He, R. Girshick, and J. Sun, “Faster R-CNN: Towards realtime object detection with region proposal networks,” in Proc. Adv.
Neural Inf. Process. Syst., vol. 28, 2015, pp. 1–9.
[59] K. He, G. Gkioxari, P. Dollár, and R. Girshick, “Mask R-CNN,” in Proc.
IEEE Int. Conf. Comput. Vis. (ICCV), Oct. 2017, pp. 2961–2969.
[60] E. Ilg, N. Mayer, T. Saikia, M. Keuper, A. Dosovitskiy, and T. Brox,
“FlowNet 2.0: Evolution of optical flow estimation with deep networks,”
in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017,
pp. 2462–2470.
[61] J. Dai et al., “Deformable convolutional networks,” in Proc. IEEE Int.
Conf. Comput. Vis. (ICCV), Oct. 2017, pp. 764–773.
[62] R. W. Schafer, “What is a Savitzky–Golay filter? [Lecture notes],” IEEE
Signal Process. Mag., vol. 28, no. 4, pp. 111–117, Jul. 2011.

8373

[63] J. C. Nascimento, A. J. Abrantes, and J. S. Marques, “An algorithm for
centroid-based tracking of moving objects,” in Proc. IEEE Int. Conf.
Acoust., Speech, Signal Processing, vol. 6, Mar. 1999, pp. 3305–3308.
[64] P. Aggarwal, “Detecting lanes with OpenCV and testing on
Indian roads,” Medium, San Francisco, CA, USA, 2016. [Online].
Available: https://medium.com/computer-car/my-lane-detection-projectfor-the-self-driving-car-nanodegree-by-udacity-36a230553bd3
[65] B. D. Lucas and T. Kanade, “An iterative image registration technique
with an application to stereo vision,” in Proc. 7th Int. Joint Conf. Artif.
Intell., vol. 2, 1981, pp. 674–679.
[66] W. Zhang, Q. M. J. Wu, Y. Yang, T. Akilan, and H. Zhang, “A widthgrowth model with subnetwork nodes and refinement structure for
representation learning and image classification,” IEEE Trans. Ind.
Informat., vol. 17, no. 3, pp. 1562–1572, Mar. 2021.
[67] Y. Yang and Q. M. J. Wu, “Features combined from hundreds of
midlayers: Hierarchical networks with subnetwork nodes,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 30, no. 11, pp. 3313–3325, Nov. 2019.
[68] L. Wei, X. Wang, A. Wu, R. Zhou, and C. Zhu, “Robust subspace segmentation by self-representation constrained low-rank representation,”
Neural Process. Lett., vol. 48, no. 3, pp. 1671–1691, Dec. 2018.
[69] J. Shi and J. Malik, “Normalized cuts and image segmentation,”
IEEE Trans. Pattern Anal. Mach. Intell., vol. 22, no. 8, pp. 888–905,
Aug. 2000.
[70] W. Bao, Q. Yu, and Y. Kong, “Uncertainty-based traffic accident
anticipation with spatio-temporal relational learning,” in Proc. 28th ACM
Int. Conf. Multimedia, Oct. 2020, pp. 2682–2690.
[71] J. Fang, D. Yan, J. Qiao, J. Xue, H. Wang, and S. Li, “DADA-2000:
Can driving accident be predicted by driver attention? Analyzed by a
benchmark,” in Proc. IEEE Intell. Transp. Syst. Conf. (ITSC), Oct. 2019,
pp. 4303–4309.
[72] F. Yu et al., “BDD100K: A diverse driving dataset for heterogeneous
multitask learning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2020, pp. 2636–2645.
[73] H. Pradana, M.-S. Dao, and K. Zettsu, “Augmenting ego-vehicle for
traffic near-miss and accident classification dataset using manipulating
conditional style translation,” 2023, arXiv:2301.02726.
[74] W. G. Najm, J. D. Smith, and M. Yanagisawa, “Pre-crash scenario
typology for crash avoidance research,” U.S. Dept. Transp.,
Nat. Highway Traffic Saf. Admin., Washington, DC, USA,
Tech. Rep. DOT HS 810 767, 2007.
[75] T. You and B. Han, “Traffic accident benchmark for causality recognition,” in Proc. 16th Eur. Conf. Comput. Vis. (ECCV), Glasgow, U.K.
Cham, Switzerland: Springer, 2020, pp. 540–556. [Online]. Available:
https://link.springer.com/chapter/10.1007/978-3-030-58571-6_32#citeas
[76] H. Kataoka, T. Suzuki, S. Oikawa, Y. Matsui, and Y. Satoh, “Drive video
analysis for the detection of traffic near-miss incidents,” in Proc. IEEE
Int. Conf. Robot. Autom. (ICRA), May 2018, pp. 3421–3428.
[77] W. Luo, W. Liu, and S. Gao, “Remembering history with convolutional
LSTM for anomaly detection,” in Proc. IEEE Int. Conf. Multimedia
Expo (ICME), Jul. 2017, pp. 439–444.
[78] V. Mahadevan, W. Li, V. Bhalodia, and N. Vasconcelos, “Anomaly
detection in crowded scenes,” in Proc. IEEE Comput. Soc. Conf. Comput.
Vis. Pattern Recognit., Jun. 2010, pp. 1975–1981.
[79] Y. Wu, J. Lim, and M.-H. Yang, “Online object tracking: A benchmark,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., Jun. 2013,
pp. 2411–2418.
[80] J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, “You only look
once: Unified, real-time object detection,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jun. 2016, pp. 779–788.
[81] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec
AD—A comprehensive real-world dataset for unsupervised anomaly
detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2019, pp. 9592–9600.
[82] S. Hochreiter and J. Schmidhuber, “Long short-term memory,” Neural
Comput., vol. 9, no. 8, pp. 1735–1780, Nov. 1997.
[83] C. Zhang et al., “A deep neural network for unsupervised anomaly
detection and diagnosis in multivariate time series data,” in Proc. AAAI
Conf. Artif. Intell., vol. 33, 2019, pp. 1409–1416.
[84] M. Canizo, I. Triguero, A. Conde, and E. Onieva, “Multi-head CNNRNN for multi-time series anomaly detection: An industrial case study,”
Neurocomputing, vol. 363, pp. 246–260, Oct. 2019.
[85] J. R. Medel and A. Savakis, “Anomaly detection in video using
predictive convolutional long short-term memory networks,” 2016,
arXiv:1612.00390.
[86] S. Li, J. Fang, H. Xu, and J. Xue, “Video frame prediction by deep
multi-branch mask network,” IEEE Trans. Circuits Syst. Video Technol.,
vol. 31, no. 4, pp. 1283–1295, Apr. 2021.

8374

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 8, AUGUST 2024

[87] K. Cho et al., “Learning phrase representations using RNN encoder–
decoder for statistical machine translation,” 2014, arXiv:1406.1078.
[88] M. Xu, M. Gao, Y.-T. Chen, L. Davis, and D. Crandall, “Temporal
recurrent networks for online action detection,” in Proc. IEEE/CVF Int.
Conf. Comput. Vis. (ICCV), Oct. 2019, pp. 5532–5541.
[89] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.

Arash Rocky (Graduate Student Member, IEEE)
received the B.Sc. and M.Sc. degrees in electrical engineering-electronics from the Department of
Electrical Engineering, Shahid Chamran University, Ahvaz, Iran, in 2009 and 2013, respectively.
He is currently pursuing the Ph.D. degree with the
Department of Electrical and Computer Engineering, University of Windsor, Windsor, ON, Canada.
His current research interests include image and
video processing, autonomous vehicles, deep neural networks, and their applications on computer
vision. He serves as a reviewer for IEEE T RANSACTIONS ON C IRCUITS
AND S YSTEMS FOR V IDEO T ECHNOLOGY and IEEE T RANSACTIONS ON
C YBERNETICS.

Qingming Jonathan Wu (Senior Member, IEEE)
received the Ph.D. degree in electrical engineering from the University of Wales, Swansea, U.K.,
in 1990.
In 1995, he joined the National Research Council
of Canada, Vancouver, Canada, where he became
a Senior Research Officer and the Group Leader.
He is currently a Professor with the Department of
Electrical and Computer Engineering, University of
Windsor, Windsor, ON, Canada. He has authored
or coauthored more than 300 peer-reviewed articles
in computer vision, image processing, intelligent systems, robotics, and
integrated microsystems. His current research interests include 3-D computer
vision, active video object tracking and extraction, interactive multimedia,
sensor analysis and fusion, and visual sensor networks.
Dr. Wu is a fellow of the Canadian Academy of Engineering. He holds
the Tier 1 Canada Research Chair in automotive sensors and information
systems. He is an Associate Editor of IEEE T RANSACTIONS ON C YBER NETICS , IEEE T RANSACTIONS ON C IRCUITS AND S YSTEMS FOR V IDEO
T ECHNOLOGY, Cognitive Computation, and Neurocomputing. He has served
on technical program committees and international advisory committees for
many prestigious conferences.
Wandong Zhang (Member, IEEE) received the
Ph.D. degree from the Department of Electrical
and Computer Engineering, University of Windsor,
Windsor, ON, Canada, in 2022.
He was a Visiting Master Student with the University of Windsor in 2017 and a Visiting Ph.D. Student
with Lakehead University from 2020 to 2021.
He is currently a Post-Doctoral Fellow with the
Department of Electrical and Computer Engineering,
Western University. His current research interests
include feature learning and representation, deep
neural networks as well as their applications on computer vision, radar image
processing, and remote signal processing.
Dr. Zhang received the Premium Award for Best Paper in Cognitive
Computation and Systems in 2022. He is a reviewer of IEEE T RANSACTIONS
ON C YBERNETICS , IEEE T RANSACTIONS ON I NDUSTRIAL I NFORMATICS ,
IEEE T RANSACTIONS ON C IRCUITS AND S YSTEMS FOR V IDEO T ECHNOL OGY , and Neurocomputing.
PAPER_TEXT
