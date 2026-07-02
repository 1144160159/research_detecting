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
# [079] Distributed Deep Convolutional Neural Networks for the Internet-of-Things
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
编号：079
题名：Distributed Deep Convolutional Neural Networks for the Internet-of-Things
年份：2021
DOI：10.1109/tc.2021.3062227
来源：IEEE Transactions on Computers
PDF：paper/10.1109_tc.2021.3062227.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：无
相关性：中相关，分数 5
已有代码状态：已下载；distributedCNNs -> source\distributedCNNs

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\079.txt
- 原始字符数：77265
- 本次发送字符数：77265
- 是否截断：False

代码包：
- 仓库：distributedCNNs
  - URL：https://github.com/simdis/distributedCNNs
  - 状态：downloaded
  - 本地目录：source\distributedCNNs
  - 顶层结构：Multi Source Multi CNN-Version To Be Executed.ipynb、README.md、examples/、execute_notebook.py、graph.py、requirements.txt、samples.py
  - 主要语言：Jupyter:5、Python:3
  - README 标题：Distributed Convolutional Neural Networks for the Internet-of-Things、Citation and Contact、Abstract、Installation、`virtualenv`、pip install virtualenv、`conda`、How to use、Distributed Convolutional Neural Networks for the Internet-of-Things、Citation and Contact
  - README 运行线索：python code of the "Distributed Convolutional Neural Networks for the Internet-of-Things" paper.；Python 3.7；pip install virtualenv；pip install -r requirements.txt；conda create --name envname；conda install -n envname --yes $requirement; done < requirements.txt；python script；python execute_notebook.py --num_exps 50 --output_dir <path-to-output-folder>
  - 关键文件：{"依赖环境": ["requirements.txt"]}
  - 数据集线索：ton、tor

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

1

arXiv:1908.01656v2 [cs.LG] 28 Jul 2021

IEEE Copyright Notice
Copyright © 2021 IEEE. Personal use of this material is permitted. Permission from IEEE must be obtained for all
other uses, in any current or future media, including reprinting/republishing this material for advertising or promotional
purposes, creating new collective works, for resale or redistribution to servers or lists, or reuse of any copyrighted
component of this work in other works.

Distributed Deep Convolutional Neural Networks for the Internet-of-Things
Simone Disabato∗
Manuel Roveri∗
Cesare Alippi∗‡
∗ Dipartimento di Elettronica, Informazione e Bioingegneria, Politecnico di Milano, Milan, Italy
‡ Faculty of Informatics, Università della Svizzera Italiana (USI), Lugano, Switzerland.

Published in IEEE Transactions on Computers.
The code of the paper is available at https://github.com/simdis/distributedCNNs.

Please cite as:
S. Disabato, M. Roveri and C. Alippi, "Distributed Deep Convolutional Neural Networks for
the Internet-of-Things," in IEEE Transactions on Computers, vol. 70, no. 8, pp. 1239-1252, 1
Aug. 2021, doi: 10.1109/TC.2021.3062227.

BibTex
@article{disabato2021distributed,
title={Distributed deep convolutional neural networks
for the internet-of-things},
author={Disabato, Simone and Roveri, Manuel and Alippi, Cesare},
journal={IEEE Transactions on Computers},
year={2021},
volume={70},
number={8},
pages={1239-1252},
doi={10.1109/TC.2021.3062227},
publisher={IEEE}
}

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

2

Distributed Deep Convolutional Neural Networks
for the Internet-of-Things
Simone Disabato, Manuel Roveri, Senior Member, IEEE, and Cesare Alippi, Fellow, IEEE
Abstract—Severe constraints on memory and computation characterizing the Internet-of-Things (IoT) units may prevent the execution
of Deep Learning (DL)-based solutions, which typically demand large memory and high processing load. In order to support a real-time
execution of the considered DL model at the IoT unit level, DL solutions must be designed having in mind constraints on memory and
processing capability exposed by the chosen IoT technology. In this paper, we introduce a design methodology aiming at allocating the
execution of Convolutional Neural Networks (CNNs) on a distributed IoT application. Such a methodology is formalized as an
optimization problem where the latency between the data-gathering phase and the subsequent decision-making one is minimized,
within the given constraints on memory and processing load at the units level. The methodology supports multiple sources of data as
well as multiple CNNs in execution on the same IoT system allowing the design of CNN-based applications demanding autonomy, low
decision-latency, and high Quality-of-Service.
Index Terms—Deep Learning, Convolutional Neural Networks, Internet-of-Things.

✦

1

I NTRODUCTION

Deep learning (DL) represents the state-of-the-art in many
recognition/classification applications [1], [2], [3], [4] and
is characterized by processing architectures organized in a
pipeline of layers providing a hierarchical representation [5].
However, such solutions are also characterized by a high
computational load and memory occupation [6], [7], [8]
and, for this reason, their use is mostly restricted to highperformance computing platforms [9], [10], [11].
For this reason, Internet-of-Things (IoT) systems, whose
computational units are mostly constrained by limited processing, memory and energy capacities, have been rarely
considered a viable technological solution for DL. In fact,
currently, IoT units are generally considered as simple datacollectors acquiring and transmitting data to the Cloud for
DL processing [12], with very few solutions (mostly based
on approximation techniques) proposing machine learning
and (most rarely) deep learning for embedded systems [8],
[13], [14]. Unfortunately, the request for a remote processing
to make decisions limits the effectiveness of the system as
the “data production to decision making”-latency might not
satisfy real-time constraints. The system closed-loop stability may even be compromised when remote connectivity
between IoT units and Cloud is unavailable or limited in
bandwidth [15]. Hence, applications requesting a (quasi)
real-time decision/actuation cannot take advantage of remote Cloud-based processing of DL solutions.
The problem of reducing the complexity of DL solutions
to match the technological constraints of IoT systems is
•
•

Simone Disabato and Manuel Roveri are with the Dipartimento di
Elettronica, Informazione e Bioingegneria, Politecnico di Milano, 20133
Milano, Italy. E-mail: {simone.disabato, manuel.roveri}@polimi.it.
Cesare Alippi is with the Dipartimento di Elettronica, Informazione e
Bioingegneria, Politecnico di Milano, 20133 Milano, Italy, and also with
the Università della Svizzera Italiana, 6900 Lugano, Switzerland. E-mail:
cesare.alippi@polimi.it.

becoming more and more relevant from both the scientific
and technological perspective and solutions present in the
literature address such a problem at different levels (i.e., adhoc hardware, approximation techniques, off-loading of DL
and distributed DL). Despite the growing research interest,
the problem of assigning a distributed DL solution on a network of IoT embedded devices is still open in the literature.
In this research direction, this paper introduces a
methodology that receives technological constraints associated with (possibly heterogeneous) IoT units and the DL
trained architectures, and provides the optimal distributed
assignment of the DL computation (layers) to the IoT units
by minimizing the data gathering to decision latency. In
particular, the methodology has been tailored to Convolutional Neural Networks (CNNs), representing the state-ofthe-art in image and video processing. Interestingly, these
CNNs can operate sequentially on the processing pipeline
(all layers are executed up to the final classification) [4],
[16], [17] or can decide the processing path at run-time
(skipping the execution of some layers) according to the
information content brought by the input [18], [19]. Both
cases are considered in the proposed methodology that, in
addition, can be used with multiple CNNs running on the
same network of IoT embedded devices (possibly sharing
processing layers).
With respect to the literature, the main novel aspects of
the proposed methodology can be summarized as:
•

•

•

the methodology is able to take into account communication and computation capabilities as well as
memory constraints of the IoT units;
the methodology can support CNNs whose processing pipeline depends on the specific input image;
multiple CNNs (possibly sharing processing layers)
can be executed on the same network of IoT units.

The proposed methodology has been validated both on simulations and a real-world technological scenario, while the

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

related code is made available to the scientific community1 .
The paper is organized as follows: the related literature is
analysed in Section 2, the research problem is formulated in
Section 3, whereas the proposed methodology is described
in Section 4. Results are detailed in Sections 5 and 6, while
conclusions are drawn in Section 7.

2

R ELATED L ITERATURE

In the related literature, the problem of reducing the computational and memory demand of DL solutions to match the
technological constraints of IoT systems can be addressed
at different levels. At the hardware level, the best technological performances with minimum power consumption
are achieved by ad-hoc hardware computing platforms
for DL as specific processors [20], or configurable FPGA
solutions [21], [22]. As also pointed out by [23], such solutions require high design-skills and cannot be easily reused. Another approach, that has shown a significant drop
in computation time, is the adoption of GPUs [10], [16],
TPUs [24], or neural hardware. However, both custom hardware and GPU/TPU solutions cannot be easily considered
in pervasive IoT systems.
The reduction of DL solutions complexity can be
achieved by considering approximation techniques. Such
an approach allows to reduce the memory and/or computational demand at the expense of a decrease in the
accuracy. [25], [26], [27] proposed compression techniques
on already trained CNNs, by compressing the weights, by
pruning whole or part of layers, and by adopting Huffman
coding. Another approach is the quantization of layers’
weights [28], up to binary weights, also during the training
phase [29], [30], [31]. Similarly, [8] introduced task-dropping
and precision-scaling mechanisms to design applicationspecific approximated CNNs able to be executed in off-theshelf embedded systems, but not in distributed IoT systems.
[32], instead, studied approximation to reduce inference on
pooling and normalization layers. An approach to reduce
the inference time is those of Adaptive Early Exit CNNs [18]
or Gate-Classification CNNs [19], where the classification
output can be provided also at intermediate layers, skipping
the remaining computation.
A different point of view is provided by the off-loading
techniques for distributed computing systems. Here, the
goal is not to reduce DL solutions’ complexity but to move
computationally-intensive processing to high-performing
units of the distributed system. For instance, a framework
to optimally offload code in a pervasive system comprising
mobile units is proposed in [33], by either minimizing the
total communication latency or the overall energy consumption. Differently, [34] proposed a high-level programming
language to design applications meant for Fog-Computing
Sensor Networks able to hide the heterogeneity of computing nodes and their position in space. [35] proposed a lowcomplexity scheduler that increases the throughput in IoT
clusters by relying on tasks duplication and splitting by taking into account communication and computation capabilities, but not IoT units memory constraints. Very few works
present in the literature encompass the code-offloading of
machine learning-based applications in pervasive systems,
1. The code is available at https://github.com/simdis/distributedCNNs.

3

e.g., [36] where the classification/pattern recognition tasks
of a wearable device are partially offloaded to other computing units (e.g., mobile phones). Similarly to our vision,
here the priority in the offloading is to move code at first to
the closest mobile devices and, then, if needed, to the Cloud.
The problem of distributing DL solutions has been recently addressed in the field of edge and fog computing. [37]
introduced a distributed framework for CNNs operating in
edge computing platforms, with the possibility of distributing the CNNs computation, mostly restricted to the Cloud,
also to edge or local devices. Unfortunately, the usage of the
Cloud is predominant in this work. In [15], [37] emerged the
need to completely re-design the DL solutions to take into
account hardware and physical constraints at application
design-time, to make IoT systems a viable technological
solution for DL. Such an approach is considered in some
recent works addressing the problem of distributing machine/deep learning solutions onto a network of IoT/Edge
devices [14], [38], [39], [40], [41]. In particular, [14] organizes
the computation tasks by partitioning the convolutional
layers vertically, with the possibility of sharing the computed features among parallel tasks. [40], instead, proposed
a dynamic scheduler to assign the layers to edge units and
reduce the communication data by relying on autoencoders.
Unfortunately, almost all these solutions rely on approximations of the original ML or DL solution to match the
hardware and physical constraints of the devices. In addition, the processing pipelines of the machine/deep learning
solutions introduced in these works are fixed at design-time,
hence not being able to modify their execution at run-time
according to the information content brought by the input.
Finally, the proposed solutions are not meant to be executed
on low-power embedded systems (e.g., STM32 or Arduino).

3

P ROBLEM F ORMULATION

The IoT system comprises a set of C data-acquisition units
{s1 , . . . , sC } mounting cameras and providing the images to
be classified by the C CNNs (each CNN processes data coming from one data-acquisition unit), a set NN = {1, . . . , N }
of N possibly heterogeneous IoT units implementing code
execution, and one target unit f receiving all the C CNNs’
outcomes to make a decision or activate a reaction. Without
any loss of generality, the C data-acquisition units are
assumed to only acquire images and do not participate in
the computation. The i-th IoT unit i ∈ NN is characterized
by its own constraints w.r.t. maximum memory capacity m̄i
and available computation c¯i .
The IoT system is modeled as a graph G(V, E) of nodes
V = {NN ∪ {s1 , . . . , sC , f }} and arcs E . An arc ei1 ,i2
between unit i1 and i2 exists in E if i2 is within the range
of the transmission technology the IoT unit i1 is equipped
with2 . Let di1 ,i2 , for each i1 , i2 ∈ V , be the hop-distance
between units i1 and i2 of V defined as the number of hops
(communication steps), data need to take to reach i2 from i1 .
In other terms, distance di1 ,i2 is the shortest communication
2. All the units in V are assumed to share the same transmission
technology with a fixed transmission data-rate. If the IoT units i1 and
i2 adopt two different transmission technologies such that i2 is within
the transmission range of i1 , but i1 is not inside the one of i2 , then
di1 ,i2 = 1 6= di2 ,i1 (loss of symmetry property).

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

path between units i1 and i2 within the graph G. Following
the definition of shortest path in a graph, if no path between
unit i1 and i2 exists, then di1 ,i2 = +∞. We also assume that
no isolated node exists, i.e., di1 ,i2 < ∞, for each i1 , i2 ∈ V .
Let Mu , for each u ∈ NC = {1, . . . , C}, be the number
of layers characterizing the u-th CNN. Each layer j of CNN
u, for each j ∈ {1, . . . , Mu } and u ∈ NC , is characterized
by a given memory demand mu,j and computation cu,j .
More specifically, the memory complexity mu,j (in Bytes)
is defined as the number of weights that layer j of CNN
u has to store multiplied by the size of the data type
used to represent those parameters (typically the floatingpoint type occupying 4 Bytes), while the computational
load cu,j is measured as the number of multiplications to
be executed by that layer [8]. Let Ku,j , for each u ∈ NC
and j ∈ {1, . . . , Mu }, be the memory occupation of the
intermediate representation transmitted from layer j to the
subsequent layer j+1 of CNN u, and Ku,s and Ku,Mu be the
memory occupation of the input image of CNN u transmitted from source su to the unit executing the first layer of the
u-th CNN and the final classification provided by layer Mu
sent to the target unit f , respectively. In particular, Ku,Mu is
either the classification label or the posterior probability of
the classes resulting from the softmax layer.
When the processing path of a CNN depends on the
information content, such as in Adaptive [18] or GateClassification CNNs [19], classification completes as soon
as enough confidence is achieved (the execution of the
remaining layers is aborted). To achieve this goal, EarlyExit CNNs (EX-CNNs) are endowed with intermediate exit
points, creating multiple paths within the CNNs each of
which is characterized by a probability of being traversed.
More formally, given a Mu -layer EX-CNN, let pu,j ∈ [0, 1] be
the probability that the j -th layer of the u-th CNN processes
the input image3 and let gu,j ∈ [0, 1], for each u ∈ NC and
j ∈ {1, . . . , Mu }, be the probability that the computation
ends at layer j of the u-th CNN is
(
pu,j − pu,j+1
if j < Mu
gu,j =
PMu −1
.
(1)
1 − v=1
gu,v if j = Mu
The addressed problem is the optimal placement of the C
CNNs layers on the N IoT units to minimize the latency in
transmitting decisions about the images gathered by the C
sources to the target unit f .

4

T HE P ROPOSED M ETHODOLOGY

This section introduces the proposed methodology for the
optimal placement of CNNs on the IoT system. Such a
methodology has been reformulated as a decision-making
latency minimization optimization problem aiming at optimally assigning the layers of the C CNNs to the N IoT units.
This optimization problem relies on the CN M variables
αu,i,j defined as:
(
1 if IoT unit i executes layer j of CNN u
αu,i,j =
, (2)
0 otherwise
for each u ∈ NC , for each i ∈ NN and for each j ∈ NM =
{1, . . . , M }, being M = max{M1 , . . . , Mu } the maximum
3. The probabilities pu,j s can be estimated during CNN learning.

4

number of layers among the considered C CNNs (i.e., the
maximum depth of all CNNs).
Without loss of generality, the distances di1 ,i2 , for each
i1 , i2 ∈ V , can be precomputed, allowing us to define
an integer quadratic optimization problem on variables
αu,i,j s. As detailed in Section 3, {s1 , . . . , sC } and f do
not participate in the optimization problem since their task
is to acquire images and receive the final classification,
respectively. This assumption can be easily removed by
considering additional IoT computing units in the same
positions of si s and f .
The objective function to be minimized models the latency in making a decision by the C CNNs placed on the IoT
units, defined as the time occurring between images acquisition by sensor unit su s (size Ku,s ) and final classifications
Ku,Mu s are transmitted to unit f :
N M−1
N X
C X
X
X

αu,i,j · αu,k,j+1 · pu,j+1 ·

u=1 i=1 k=1 j=1

+

Ku,j
· di,k
ρ

N
X
(p)
ti + ts + tf ,

(3)

i=1

such that
M
C X
X

∀i ∈ NN

αu,i,j ≤ L

(4)

αu,i,j · mu,j ≤ m̄i

(5)

αu,i,j · cu,j ≤ c̄i

(6)

u=1 j=1

M
C X
X

∀i ∈ NN

u=1 j=1

M
C X
X

∀i ∈ NN

u=1 j=1
N
X

∀u ∈ NC , ∀j ∈ NM

αu,i,j =

i=1

(

1 if j ≤ Mu
0 otherwise

(7)

and where

ts =
(p)

ti

=

N
C X
X

u=1 i=1
M
C X
X

αu,i,1 · pu,1 ·

Ku,s
· ds,i
ρ

(8)

αu,i,j · pu,j ·

cu,j
ei

(9)

u=1 j=1

tf =

M
N X
C X
X

u=1 i=1 j=1

αu,i,j · gu,j ·

Ku,Mu
· di,f
ρ

(10)

The objective function in Eq. (3) comprises four different
components of the latency:
(i) The source time ts , defined in Eq. (8), required to
transmit the images from the sources su s to the IoT units
executing the first layer of the CNNs. Although the first
layer is always reached, i.e., pu,1 = 1 for each u ∈ NC , the
term pu,1 has been added to Eq. (8) to provide homogeneity
in the formalization.
(ii) The transmission time of intermediate representations among the IoT units processing the CNN layers.
More precisely, the transmission time of the intermediate
representation of the j -th layer of the u-th CNN from unit i
to k is
Ku,j
· di,k ,
(11)
ρ

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

5

where ρ is the data-rate of the considered transmission
technology and di,k is the hop-distance between unit i and
k as defined in Section 3. In Eq. (3) the transmission time
is weighted by the probability pu,j+1 that layer j + 1 is
executed right after layer j .
(p)
(iii) The processing time ti of the CNN layers on the
IoT units. Specifically, the processing time of layer j of
CNN u on the i-th IoT unit is approximated as the ratio
between the computational demand cu,j that layer requires
and the number of multiplications ei the IoT unit i is able
to carry out in one second4 . In Eq. (9), the processing time is
weighted by the probability pu,j that the layer j of CNN u
is executed.
(iv) The sink time tf required to transmit the final
classification Ku,Mu , for each u ∈ NC , from the IoT units
taking these decisions to the target unit f . It is noteworthy to
point out that Eq. (10) takes into account all feasible output
paths from node i to the target unit f , suitably weighted by
the probability gu,j that the classification is made at layer j
of CNN u in execution on IoT unit i.
The constraint in Eq. (4) ensures that each IoT unit
contains at most L layers, being L an additional userdefined model hyper-parameter. In particular, when L = 1,
at most one layer can be assigned to an IoT unit, while
L > 1 implies that up to L layers (also belonging to
different CNNs) can be assigned to a particular IoT unit.
The constraints in Eq. (5) and (6) are meant to take into
account the technological limits about memory usage and
computational load characterizing each IoT unit. Finally,
the constraint in Eq. (7) ensures that each layer j , for each
j ∈ NM , is assigned to exactly one node and, at the same
time, manages the possibility that the C CNNs might be
characterized by a different number Mu ≤ M of layers, for
each u ∈ NC . In fact, in those cases (i.e., when Mu < M ),
the unneeded αu,i,j s are set to 0.
When the j1 -th layer of CNN u1 and the j2 -th layer of
CNN u2 are shared between the two CNNs, the following
constraint is added to the optimization problem

∀i ∈ NN

αu1 ,i,j1 = αu2 ,i,j2 ,

If a layer is shared among k CNNs, the Eqs. (13), (14),
and (15) need to take into account k−1 out of the k variables
corresponding to the shared layer.
The considered class of optimization problems, i.e., the
integer quadratic programs, is NP-complete. More specifically, since the αu,i,j s are binary variables, it is possible
to convert it to a binary linear program, which is one
of Karp’s 21 NP-complete problems [42]. In the proposed
methodology, the optimization problem is solved through
the Gurobi solver5 .
The optimization problem outcome is the optimal placement αu,i,j s of the C CNNs’ layers to the N IoT units
minimizing the delay in making a classification. In the event
that the optimization provides more than one solution, the
optimal placement is any feasible solution with minimal latency. In the rest of this section, the methodology is tailored
to three specific configurations of the DL solution, followed
by some comments about the open points.
4.1 The configuration with a single CNN
The presence of a single CNN (C = 1) allows us to rely on
N M binary variables αi,j , determining whether layer j of
the CNN is assigned to unit i of the IoT system.
(
1 if IoT unit i executes CNN layer j
αi,j =
,
(16)
0 otherwise
for each i ∈ NN and j ∈ NM . The objective function in
Eq. (3) modelling the latency in making a decision to be
minimized is reformulated as:
N M−1
N X
X
X
i=1 k=i j=1

∀i ∈ NN

M
X

∀i ∈ NN

∀i ∈ NN

∀i ∈ NN

(18)

αi,j · mj ≤ m̄i ,

(19)

αi,j · cj ≤ c̄i ,

(20)

αi,j = 1,

(21)

αi,1 ·

Ks
· ds,i ,
ρ

(22)

αi,j ·

cj
,
ei

(23)

KM
· di,f ,
ρ

(24)

M
X

∀i ∈ NN

(12)

j=1

M
X

∀i ∈ NN

j=1

N
X

∀j ∈ NM

i=1

αu,i,j ≤ L + αu2 ,i,j2 ,

(13)

while

αu,i,j · mu,j ≤ m̄i + αu2 ,i,j2 · mu2 ,j2 ,

ts =

u=1 j=1

M
C X
X

αi,j ≤ L,

j=1

u=1 j=1

M
C X
X

N
X
Kj
(p)
ti + ts + tf . (17)
· di,k +
ρ
i=1

Then, the constraints in Eqs. (4), (5), (6) and (7) become:

to ensure that the shared layer is placed on the same IoT
unit. In addition, the constraints on the maximum number
of layers placed on a IoT unit - Eq. (4) - and the memory
usage and computational load constraints - Eqs (5) and (6) are modified as follows to count the shared layer only once:
M
C X
X

αi,j · αk,j+1 ·

(14)

(p)

ti

=

N
X

i=1
M
X
j=1

αu,i,j · cu,j ≤ c̄i + αu2 ,i,j2 · cu2 ,j2 . (15)

u=1 j=1

4. The ei s encompass the number of available cores, the type of
pipeline such cores implement to approach one operation per clock
cycle, the presence or not of a GPU allowing to parallelize CNN
operations (e.g., the convolutions) and all the delays resulting from
the processing system and memory management.

tf =

N
X
i=1

αi,M ·

5. The solver is able to find a solution with a error less than 2% with
respect to the optimal placement in less than 2 seconds and a negligible
memory occupation in all the considered IoT scenarios described in
Section 5.

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021
(L1) 5x5 conv, 32
2x2 max-pool, /2

I

(L2) 5x5 conv, 64
2x2 max-pool, /2

6
(L3) FC 384

(L4) FC 192

(L5) FC 10

(a) The architecture of the considered 5-layer CNN, where I is the input image.
n08

n08
n03

n07

n03

n07

s, f

s, f

n06

n06

n09

n11

n05

n05

L1

n01

n01

n04

n04

L2

n02

n10

n10

(b) An example of IoT system with STM32H7 (circles) and Raspberry 3B+ (squares). The source s and the sink f share the same
IoT unit. The dotted circle refers to the transmission range, equal
for all the IoT units.
L1
L2
L3
L4
L5

L5

n09

n11

L4

L3

n02

(c) An example of the methodology outcome where the layers
L1,. . . , L5 of the 5-layer CNN in Figure 1a are placed on the IoT
units of the system shown in Figure 1b, when setting L = 1.

n01

n02

n03

n04

n05

n06

n07

n08

n09

n10

n11

0
0
0
1
0

0
0
0
0
0

0
0
0
0
0

0
0
1
0
0

1
0
0
0
0

0
0
0
0
1

0
0
0
0
0

0
0
0
0
0

0
0
0
0
0

0
1
0
0
0

0
0
0
0
0

(d) The variables αu,i,j s representing the methodology outcome for the solution shown in Figure 1c, with u = 1.

Fig. 1: The methodology is applied to a 5-layer CNN (i.e., C = 1).
account for the transmission time between the source s
and the IoT unit running the first layer of the CNN, the
processing time on all unit is, and the transmission time
between the unit running the M -th layer of the CNN and
the sink f , respectively.
In this configuration, the methodology has been applied
to the 5-layer CNN described in Figure 1a, characterized
by M = 5 layers and whose details are in Table 2a. The
considered IoT system is the one described in Figure 1b
comprising N = 11 IoT units and being s and f the same
unit. The IoT units belong to two different technological
families, i.e., STM32H7 (round nodes) and Raspberry Pi 3B+
(squared nodes), whose memory m̄i and computational c̄i
constraints are detailed in Table 3. An example of the optimization problem outcome in this technological scenario
with L = 1 is given in Figure 1c, whose corresponding
αi,j s are detailed in Figure 1d. In the optimal placement,
involving three STM32H7 units (nodes n05 , n01 , and n06 )
and two Raspberry Pi 3B+ (nodes n10 , and n04 ), the layer
L3 of the CNN has been assigned to a Raspberry Pi 3B+ IoT
unit (i.e., n04 ) since its execution on STM32H7 would violate
the memory constraint.
4.2 The configuration with a single early-exit CNN
This configuration refers to the case where a single EX-CNN
(C = 1) has to be placed on the IoT system. Here, the pu,j s
and gu,j s are simplified as pj and gj , for each j ∈ NM ,
defining the probabilities that layer j is executed and that
the final classification is made at layer j (i.e., the direct path
from j to the sink is traversed), respectively.
More specifically, the problem variables are simplified
into N M binary variables αi,j defined in Eq. (16). Instead,

the pu,j s and gu,j s are simplified as pj and gj , for each j ∈
NM , as detailed in Section 4.2.
The objective function modelling the latency in decision
making defined in Eq (3) is tailored as follow:
N M−1
N X
X
X

N
X
Kj
(p)
ti + ts + tf ,
· di,k +
ρ
i=1 k=i j=1
i=1
(25)
with constraints as in Eqs. (18), (19), (20), and (21), and
(p)
where the source time ts , the processing time ti , and the
sink time tf have been modified as follows:

αi,j · αk,j+1 · pj+1 ·

ts =
(p)

ti

=

N
X

i=1
M
X

αi,1 · p1 ·

Ks
· ds,i ,
ρ

(26)

αi,j · pj ·

cj
,
ei

(27)

j=1

tf =

M
N X
X
i=1 j=1

αi,j · gj ·

KM
· di,f .
ρ

(28)

A 6-layer EX-CNN is shown, as an example, in Figure 2a
and detailed in Section 5.1–Table 2a, where M = 6 and the
Early Exit is at layer j = 2, with a probability ν = 0.99
of taking the final classification. Hence, p1 = p2 = 1 and
p3 = p4 = p5 = 0.01, with the gj s different from zero only
at the Early-Exit (g2 = 0.99) and the last layer (g6 = 0.01).
In Figure 2, the proposed methodology is applied to this
CNN and the IoT system already described in Figure 1b. The
methodology outcome is particularly interesting showing
that the Early-Exit layer (j = 2), being particularly demanding in terms of memory, is assigned to the Raspberry Pi 3B+
n04 unit. When enough confidence is achieved at Early-Exit

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

7

(j = 2), the decision is directly sent from n04 to the sink f
through n06 . Otherwise, the processing is forwarded from
n04 to n01 to complete the processing up to n08 .
4.3 The configuration with multiple CNNs
An interesting application scenario is the one with multiple
CNNs, either without or with shared processing layers. EXCNNs have not been considered here, hence pu,j = 1, for
each u ∈ NC and j ∈ {1, . . . , Mu }.
In this configuration, the objective function modelling
the latency in decision making becomes:
N M−1
N X
C X
X
X

N
X
Ku,j
(p)
ti +ts +tf ,
·di,k +
ρ
u=1 i=1 k=i j=1
i=1
(29)
with constraints defined in Eqs. (4), (5), (6) and (7), and
(p)
where the source time ts , the processing time ti , and the
sink time tf are modified as follow:

(p)
ti =

tf =

N
C X
X

u=1 i=1
M
C X
X

αu,i,1 ·

Ku,s
· ds,i ,
ρ

(30)
(31)

N
C X
X

(32)

αu,i,Mu ·

Ku,Mu
· di,f .
ρ

Finally, to deal with shared layers, the constraint defined
in Eq. (12) is introduced per each shared layer, whereas the
constraints in Eqs. (4), (5), and (6) are modified accordingly,
as detailed in Section 4 with Eqs. (13), (14), and (15). As an
example, it is provided the complete extension to deal with
the two first shared layers for the case shown in Figure 3b.
The additional constraints are defined in Eqs. (38) and (39)
to ensure that the shared layers j = 1 and j = 2 (of CNNs
u = 1 and u = 2) are assigned to the same node i. Then, the
Eqs. (4), (5), and (6) are modified as follow:
M
C X
X

αu,i,j ≤ L + α1,i,1 + α1,i,2 ,

(33)

αu,i,j · mu,j ≤ m̄i + m̂,

(34)

αu,i,j · cu,j ≤ c̄i + ĉ.

(35)

m̂ = α1,i,1 · m1,1 + α1,i,2 · m1,2
ĉ = α1,i,1 · c1,1 + α1,i,2 · c1,2

(36)

u=1 j=1

M
C X
X

u=1 j=1

∀i ∈ NN

M
C X
X

α1,i,1 = α2,i,1 ,
α1,i,2 = α2,i,2 ,

(38)
(39)

and the constraints Eq. (13), (14) and (15) have to be
redefined accordingly. The methodology outcome in this
scenario is interesting showing that common layers L1 and
L2 have been placed in IoT units n06 and n01 , respectively,
while, after n01 , the processing takes two different paths.
4.4 Open Points

cu,j
αu,i,j ·
,
ei
u=1 j=1

u=1 i=1

∀i ∈ NN

∀i ∈ NN
∀i ∈ NN

αu,i,j ·αu,k,j+1 ·

ts =

∀i ∈ NN

common processing layers, operating in the IoT system
depicted in Figure 1b and with L = 1. Interestingly, the outcome of the methodology, depicted in Figure 3a, shows that
the placement of both CNNs represent the optimal solution
of the single-CNN configuration. Moreover, the methodology has been applied to the case where the convolutional
layers L1 and L2 are shared between the two CNNs. This
solution is inspired by the transfer learning paradigm where
two CNNs might share low-level representation processing
layers, while high-level ones are specific for each CNN. As
described in Section 4, the following constraints need to be
added to the optimization problem:

u=1 j=1

where
(37)

It is noteworthy to point out that there is no difference
in defining Eqs. (33), (34), and (35) with the variables of the
CNN u = 2, instead of those of CNN u = 1, as done here.
It is indeed sufficient to relax the constraints with k − 1
variables out of k , where k represents the number of CNNs
a layer is shared among, in order to count that shared layer
only once.
The proposed methodology has been applied to two
instances of the 5-layer CNN described in Figure 1a without

Currently, the proposed methodology neither takes into
account the energy status of IoT units nor network failures [43]. The energy status can be managed by introducing
a constraint for each IoT unit depending on the remaining
energy value, e.g., forcing the variables α·,i,· s of a lowenergy node i to zero or introducing penalties for assigning
a layer to those nodes. The network failures could be managed by modifying the transmission time defined in Eq. (11)
as (1 + ξ i,j ) · Ku,j /ρ · di,k taking into account a probability
of retransmission ξ i,j for each pair of nodes (i, j).
It is noteworthy to point out that, thanks to the transfer
learning paradigm, the hierarchy of layers of the CNNs
can be considered as general feature extractors [44]. For
this reason, the deployed CNNs can be easily reconfigured to address a different image-classification problem by
replacing only upper layers. Moreover, this optimization
phase can be scheduled periodically or when needed to
manage variations in the IoT network configuration (e.g.,
due to the removal or insertion of IoT units). This is a
crucial aspect in the scenario of mobile IoT units, a case
that is not considered in this paper. In fact, thanks to the
transfer learning approach and by periodically recomputing
the CNN allocation, the methodology could be applied to
units changing their position in the environments they are
operating in.

5

E XPERIMENTAL R ESULTS

The proposed methodology has been validated on five
CNNs and four families of off-the-shelf IoT devices in a
synthetic scenario of distributed image classification for the
control of a critical area (e.g., recognition of the presence of
target objects in a given area through image classification).
The monitored area is assumed to be a 30m square and the
positions of the IoT units as well as those of the sources su s
and the sink f are randomly selected following a uniform
distribution. The hyper-parameter L, setting the maximum
number of CNN layers per IoT unit, ranges from 1 to 5.

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

I

(L1) 5x5 conv, 64
2x2 max-pool, /2

p1 = 1.00, g1 = 0.00

(L2, GC)
FC 384,192,10

p2 = 1.00, g2 = 0.99

8

L6

n08

L5

n03

n07
s, f

ν = 0.01
(L3) 5x5 conv, 64
2x2 max-pool, /2
ν = 0.99

n06
n09

n11

p3 = 0.01, g3 = 0.00

n05

n01

p4 = 0.01, g4 = 0.00

(L4) FC 384
(L5) FC 192
(L6) FC 10

p5 = 0.01, g5 = 0.00

n04

p6 = 0.01, g6 = 0.01

(a) The 6-layer EX-CNN archicture with its pi s and gi s, for each
i ∈ NN . I is the input image.

L3

GC
n02

n10

y

L4

L1

(b) The methodology outcome on the 6-layer EX-CNN on the IoT
system shown in Figure 1b.

Fig. 2: The methodology applied to a 6-layer EX-CNN, with L = 1. Note that dn04 ,f = 2, thus n04 requires an intermediate
hop, i.e., the node n06 , to send the final classification.
L12
n07

L52

n08
n03

L11

L22

n03

n07

s, f

s, f

n06
n09

n06
n11

L32

n09

n11
n05

L51
n01

L31

n04

n10

L41

L42

L1

L52

L21
n05

n08

L32

L51
n01 L2

2

L4

n02

(a) The methodology outcome, with no shared layer between the
two 5-layer CNNs (shown in Figure 1a).

L41

n04

n10

L31

n02

(b) The methodology outcome, with the first two layer shared
between the two 5-layer CNNs.

Fig. 3: The methodology applied to two 5-layer CNNs and the IoT system in Figure 1b with L = 1.
The rest of the section is organized as follows. Section 5.1
details the considered CNNs, Section 5.2 describes the families of considered off-the-shelf IoT units and their transmission technologies, and Section 5.3 describes the figure of
merit. Sections 5.4 and 5.5 describe the experimental results
in two different IoT systems.
5.1 The considered CNNs
The first two CNNs are the 5-layer CNN and the 6-layer
EX-CNN shown in Figures 1a and 2a, respectively. These
two CNNs, whose values of mj s, cj s, and Kj s are detailed
in Table 2a, receive in input a 28x28 RGB image and have
the following processing layers: two convolutional (with
64 5x5 filters) followed by a 2x2 maximum pooling with
stride 2, and three fully-connected layers with 384, 192 and
10 neurons, respectively. In the 6-layer EX-CNN, the EarlyExit is after the first pooling layer and is composed by three
fully-connected layers with 384, 192 and 10 neurons.
The third CNN is the AlexNet [16], whose details are
given in Table 2b. Such CNN works on 227x227 RGB images
and is endowed with 5 convolutional layers (with 96 11x11,
256 5x5, 384 3x3, 384 3x3 and 256 3x3 filters, respectively)
and 3 fully-connected layers with 4096, 4096 and 2 neurons.
In addition, 3x3 maximum pooling layers with stride 2

are present after the first, second and fifth convolutional
layers. An Early-Exit variant of the AlexNet [19] has been
considered where the Early-Exit is placed after the second
maximum pooling layer and is composed of three fullyconnected layers with 128, 64 and 2 neurons, respectively.
The fifth considered CNN is the ResNet 101 [4], whose
details are given in Table 1. This CNN works on 224x224
RGB images and is composed by a sequence of Bottleneck
blocks (i.e., a sequence of a 1x1 convolution, a 3x3 convolution, and a 1x1 convolution with 4 times filters w.r.t to the
other two convolutions) of increasing number of filters. The
last two layers are an average pooling and a fully-connected.
In all the considered CNNs, the ReLUs, the batch normalization, and the softmax layers have not been explicitly
mentioned since they have no parameter to store and negligible computational demands.
5.2 The considered IoT Units
In this experimental section we considered four families of
IoT units, whose technological details are given in Table 3:
the STM32H7, a simple IoT unit endowed with a 400 MHzCortex M7 and 1 MB of RAM; the Raspberry Pi 3B+, a more
powerful IoT units endowed with a 1.4GHz 64-bit quad-core
processor and 1GB of RAM; the OrangePi Zero, endowed

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

TABLE 1: The memory demand mj , the computational load
cj , and the memory Kj required to store the intermediate
representations of the ResNet 101 [4], with a 4B data type.
When there are two values for mj and cj in repeated sequence of layers, the former one refers to the first repetition,
the latter to all the subsequent repetitions.
Layer (j )

mj (KB)

cj (106 mult.)

Kj (KB)

-

-

602.12

s

Source (Im. 224x224x3)

11
12

7x7 conv, 64, /2
3x3 max pool, /2

37.63
-

118.01
1.81

3 211.26
802.82



1x1 conv, 64
3x 3x3 conv, 64

1x1 conv, 256

16.38–65.54
147.46
65.54

12.85–51.38
115.61
51.38

802.82
802.82
3 211.26

2

3

4

786.43

616.56

3 211.26



1x1 conv, 128
4x 3x3 conv, 128

1x1 conv, 512

131.07–262.14
65.54
262.14

25.69–51.38
115.61
51.38

401.41
401.41
1 605.63

2228.2

757.86

1 605.63



1x1 conv, 256

524.29–1 048.58
2 359.30
1 048.58

25.69–51.38
115.61
51.38

200.71
200.71
800.82

21 757.95

950.53

800.82

1 048.58
2 359.30
1 048.58

51.38
115.61
51.38

200.71
200.71
800.82

5x 3x3 conv, 256

1x1 conv, 1024



1x1 conv, 256
5,6,7 6x 3x3 conv, 256

1x1 conv, 1024

8

91
92



1x1 conv, 512
3x 3x3 conv, 512

1x1 conv, 2048

26 738.69

1 156.06

800.82

2 097.15–4 194.30
9 437.18
4 194.30

25.69–51.38
115.61
51.38

100.35
200.71
800.82

51 380.22

629.41

800.82

8 388.61

0.10
2.08

8.19
4

7x7 avg pool
fc 1000

with a 800MHz to 1.2GHz quad-core Cortex-A7 and 256 MB
of RAM; and the BeagleBone AI having a 1.5GHz dual-core
ARM Cortex–A15 and 1GB of RAM.
The maximum memory usage m̄i s has been defined
as half of the available RAM memory, i.e., 512KB for the
STM32H7, 128MB for the OrangePi Zero, and 512MB for
the both the BeagleBone AI and the Raspberry Pi3B+. The
number of multiplications per second ei s has been defined
as a tenth of the clock cycles (per number of cores). Hence,
e = 40 for the STM32H7, e = 300 for the BeagleBone AI (150
per core), e = 480 for the OrangePi Zero (120 per core, if we
consider the maximum frequency of 1.2GHz), and e = 560
for the Raspberry 3B+ (140 per core). The constraints on the
computational load c̄i s have not been considered since they
are application-specific.
The transmission technologies the IoT units are
equipped with are the Wi-Fi 4 (standard IEEE 802.11n)
and Wi-Fi HaLow (standard IEEE 802.11n). The transmission
range is dt = 7.5m (a tenth of the minimum indoor range).
The Wi-Fi 4 data-rate is ρ = 72.2 Mb/s, that corresponds
to the single-antenna scenario with 64-QAM modulation
on the 20 MHz channel [45], whereas the Wi-Fi HaLow
one is ρ = 7.2 Mb/s with a single-antenna and 64-QAM
modulation on the 2 MHz channel [46].
5.3 Figures of Merit
The proposed methodology is evaluated on the “data production to decision making”-latency t defined as the time
between image acquisition and classification reception at f .
To further clarify the effects of data communication and

9

TABLE 2: The memory demand mj , the computational load
cj , and the memory Kj required to store the intermediate
representations of four (EX–)CNNs, with a 4B data type and
the Early-Exit layer marked with an asterisk. In that layer,
Kj represents the dimensions of the representation sent to
the layer j + 1 when the classification is not taken at layer j .
(a) The 5-layer CNN and the 6-layer EX-CNN.
Layer (j )
s

Source (Im. 28x28x3)

11
12

5x5 conv, 64
2x2 pool, /2

mj (KB)

cj (106 mult.)

Kj (KB)

-

-

9.41

19.20
-

3.76
0.05

200.70
50.18

2*

gc1 (fc 384,192,10)

19 570.18

4.89

50.18

31
32

5x5 conv, 64
2x2 pool, /2

409.60
-

20.07
0.01

50.18
12.54

4
5
6

fc 384
fc 192
fc 10

4 816.90
294.91
7.68

1.20
0.07
2 · 10−3

1.54
0.77
0.04

(b) The AlexNet [16] and its Early-Exit version [19].
Layer (j )

mj (KB)

cj (106 mult.)

Kj (KB)

s

Source (Im. 227x227x3)

-

-

618.35

11
12

11x11 conv, 96, /4
3x3 pool, /2

139.78
-

105.42
0.31

1161.60
279.94

21
22

5x5 conv, 256
3x3 pool, /2

1 229.82
-

223.95
0.39

746.50
173.06

3*

gc1(fc 128,64,2)

22185.22

5.55

173.06

4
5
61
62

3x3 conv, 384
3x3 conv, 384
3x3 conv, 256
3x3 pool, /2

3 540.48
2 655.74
1 770.50
-

149.52
112.14
74.76
0.08

259.58
259.58
173.06
36.86

7
8

fc 4096
fc 4096, 2

151 011.39
67 158.02

37.75
16.78

16.38
0.01

computation, t is split into the transmission tt and the
processing tp terms. The former term refers to the sum of
all transmission times (from a source to IoT units, between
IoT units, or from IoT units to the target unit f ); the latter
sums the processing times on the IoT units. These terms
are computed as defined in Section 4, whereas additional
sources of delays, such as transmission handshakes or repeated transmissions (due to failures) have been neglected.
For each setting, transmission technology, and configuration, the evaluated figure of metric is the mean ± standard
deviation of each latency term, i.e., t, tt , and tp , computed
on 500 randomly generated IoT systems. It is noteworthy
to point out that the accuracy has not been considered as a
metric since the proposed method does not introduce any
approximation w.r.t the original CNN, hence there is no
accuracy loss due to placement of the CNN layers.
5.4 The First IoT System: 30 IoT Units and Two Technological Families
The first IoT system comprises N = 30 IoT units belonging
to two technological families, i.e., the STM32H7 and the
Raspberry Pi 3B+, with three settings for the IoT units
partitioning, i.e., 10%–90%, 50%–50% and 90%–10%.
5.4.1 Single-CNN Configuration
This configuration encompasses a single CNN, either with
or without an Early-Exit, to be placed on the considered IoT

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

TABLE 3: The maximum memory usage m̄i (defined as half
of the available RAM), and the million (106 ) multiplications
per second ei s (defined as a tenth of the clock cycles performed in one second) of a few off-the-shelf IoT units.

S1
B1
O1
R1

Node (i)

m̄i (KB)

ei (106 mult.)

STM32H7
BeagleBone AI
OrangePi Zero
Raspberry Pi 3B+

512
524 288
131 072
524 288

40
360
480
560

system. The methodology is tested with L ∈ {1, 2, 3, 4} and
compared to the Cloud approximation (L = 5, referred to as
L = C ), where all the computation can be placed on a single
node, i.e., it can be seen as an approximation of sending data
directly to the Cloud and then receiving back the result.
The results are shown in Table 4, in the partition setting
50%–50%. Interesting results arise. First of all, the expected
processing time tp is significantly reduced when the Early
Exit is employed, as expected and studied in [18], [19]
for both the considered CNNs6 . In the case of 6-layer EXCNN, the Early-Exit allows to save about 75-84% (45 to
80% with Wi-Fi HaLoW) of the latency t, whereas on the
AlexNet 34 to 50%. After that, with Wi-Fi 4 transmission
technology the transmission latency tt is significantly lower
than the processing one tp , thus it is reasonable to assume
that the achieved tp is the minimum feasible in this IoT
system. However, with Wi-Fi HaLow, the minimum experimental latency (tp = 44.93ms for the 5-layer CNN and
tp = 1257.71ms for the AlexNet) cannot be achieved and,
in particular, the AlexNet processing with L = 1 requires
more than 3 seconds (instead of 1.46s with the Wi-Fi 4
transmission technology), a latency that might be unfeasible
in many real applications. The third crucial comment is
about the L = C case. The latency t of this case and those of
corresponding ones having L ≥ 2 (L > 2 with Wi-Fi HaLow)
are almost equal (10% increment with L = 1)and Wi-Fi
4), showing the capability of the proposed methodology
of distributing the CNN computation among units with
negligible latency increments.
5.4.2 Multi-CNN Configuration
In this configuration, two 5-layer CNNs have to be placed
on the considered IoT system, with and without the first
two layers shared. Results are presented in Table 5, for all
the configurations and transmission technologies. Several
comments arise. At first, in the configurations 90%–10%,
the methodology has to often rely on STM32H7 nodes,
hence the processing time is significantly increased (the
computation capability e of a Raspberry is 14 times greater
than that of an STM32H7). This result is even more evident
when there are shared layers since the methodology can
place less computation on STM32H7s.
The Wi-Fi 4 guarantees transmission latencies tt s negligible w.r.t. the processing time tp , that represents more than
85% of latency t (up to 96-99% with L ≥ 2). Interestingly,
the processing time is always equal to 89.9ms, that is the
experimental minimum achievable value in this IoT system.
6. The latency t and its terms tt and tp , are defined as an expected
value with EX-CNNs, by weighting their values up to each layer j of
CNN u with the probability gu,j of providing the classification.

10

This consideration is no longer valid with the Wi-Fi HaLow,
where the two terms are comparable, especially when
L = 1. The methodology cannot indeed always achieve the
minimum experimental processing latency, but sometimes it
has to rely on nearby STM32H7 units, as highlighted by the
non-null standard deviation of the tp , in the configurations
with at least 50% of Raspberry Pi 3B+ units. Interestingly,
despite the data-rate of the Wi-Fi 4 is ten times greater than
that of Wi-Fi HaLow, the latency t in the harsher case with
90% of STM32H7 units is similar for both the transmission
technologies, with a maximum increment of 20% with L = 1
and no shared layers.
Finally, in all cases with L ≥ 2 (L > 2 with Wi-Fi HaLow)
the total latency t is comparable to the case (L = 5), as
in Single-CNN configuration (Section 5.4.1). It is crucial to
point out the importance of this result because distributing
the CNN processing on various IoT units with a negligible
increment in latency t will allow defining a pipeline in
processing sequence of images. Indeed, when a unit has
carried out the processing of CNN layers is designed to and
sent the computed representation to the subsequent node,
it is ready to operate on the next image, as in processor
pipelines. Hence, the throughput of CNN processing can be
significantly increased by processing images in a pipeline,
with bottleneck the IoT unit responsible for the highest
processing time.
5.5 The Second IoT System: 50 IoT Units and Three
Technological Families
A second IoT system is considered with N = 50 units
belonging to three different technological families equipped
with the Wi-Fi 4 transmission technology and partitioned as
follows: 45% of OrangePi Zero, 45% of BeagleBone AI, and
10% of Raspberry Pi 3B+. An example of this IoT system
is shown in Figure 4a, where the OrangePi Zero units are
represented by a circle, the BeagleBone AI units by a square,
the Raspberry Pi 3B+ units by a diamond, the sources by an
asterisk, and the target unit by a circled cross.
The scenario is interesting because the most powerful
IoT units in terms of both memory and computation capabilities, i.e., the Raspberry Pi 3B+, are just a few (about
5 in each simulated IoT system), whereas the remaining
IoT units are characterized by contrasting peculiarities: on
one hand the BeagleBone AI units have the same memory
capability of the Raspberry Pi 3B+ but only 54% of the
computation one; on the other hand the OrangePi Zero have
almost the same computation capability of the Raspberry Pi
3B+ (85%, 160% if compared to BeagleBone AI), but only
a fourth of the memory capability. It is worth noting that
both the Raspberry Pi 3B+ and BeagleBone AI can store
all the layers of the considered CNNs, whereas being the
OrangePi Zero units with 128 MB of RAM they cannot store
all the layers of the ResNet and the (EX–)AlexNet CNNs. As
a consequence, balancing between the faster OrangePi Zero
units (in terms of computation capability) and the slower
but with higher memory capacity BeagleBone AI units is
expected in this IoT system (at least after all the Raspberry
Pi 3B+ units have been considered, if enough closer).
In addition to the figures of merit presented in Section 5.3, the number of considered nodes ηx is taken into

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

11

TABLE 4: Single-(EX–)CNN configuration results with N = 30 STM32H7 and Raspberry Pi 3B+ units in the 50%-50%
scenario. The figure of merit (mean ± std) is the latency t, i.e., the transmission time tt plus the processing time tp .
(a) The results with the Wi-Fi 4 as adopted transmission technology.
Latency t (ms)

tt

tp

t = tt + tp

L

tt

tp

t = tt + tp

1
2
3
4

7.49 ± 0.36
1.78 ± 0.21
0.48 ± 0.14
0.37 ± 0.11

44.93 ± 0.00
44.93 ± 0.00
44.93 ± 0.00
44.93 ± 0.00

52.42 ± 0.36
46.71 ± 0.21
45.41 ± 0.14
45.30 ± 0.11

1
2
3
4

203.06 ± 36.85
127.81 ± 28.49
98.75 ± 26.63
95.82 ± 26.54

1257.71 ± 0.00
1257.71 ± 0.00
1257.71 ± 0.00
1257.71 ± 0.00

1460.77 ± 36.85
1385.52 ± 28.49
1356.46 ± 26.63
1353.53 ± 26.54

C

0.28 ± 0.11

44.93 ± 0.00

45.21 ± 0.11

C

72.49 ± 24.08

1257.71 ± 0.00

1330.20 ± 24.08

1
2
3
4

5.87 ± 0.27
0.34 ± 0.10
0.29 ± 0.10
0.28 ± 0.10

7.27 ± 0.00
7.27 ± 0.00
7.27 ± 0.00
7.27 ± 0.00

13.14 ± 0.27
7.61 ± 0.10
7.57 ± 0.10
7.55 ± 0.10

1
2
3
4

129.42 ± 28.29
93.70 ± 24.49
72.10 ± 22.08
72.07 ± 22.08

598.92 ± 81.81
596.19 ± 0.00
596.19 ± 0.00
596.19 ± 0.00

728.35 ± 86.17
689.89 ± 24.49
668.29 ± 22.08
668.26 ± 22.08

C

0.28 ± 0.10

7.27 ± 0.00

7.55 ± 0.10

C

71.84 ± 22.07

596.19 ± 0.00

668.03 ± 22.07

AlexNet

L

EX-AlexNet

6-layer EX-CNN

5-layer CNN

Latency t (ms)

(b) The results with the Wi-Fi HaLow as adopted transmission technology.
Latency t (ms)

tp

t = tt + tp

L

1
2
3
4

74.82 ± 3.94
17.75 ± 2.08
4.49 ± 0.89
3.64 ± 0.87

45.16 ± 0.57
44.93 ± 0.00
45.08 ± 0.46
44.93 ± 0.00

119.98 ± 4.06
62.68 ± 2.08
49.57 ± 1.03
48.57 ± 0.87

1
2
3
4

C

2.80 ± 0.88

44.93 ± 0.00

47.73 ± 0.88

1
2
3
4

58.72 ± 2.47
3.53 ± 1.15
3.04 ± 1.10
2.90 ± 1.10

7.27 ± 0.01
7.27 ± 0.00
7.27 ± 0.00
7.27 ± 0.00

65.99 ± 2.47
10.80 ± 1.15
10.31 ± 1.10
10.17 ± 1.10

C

2.88 ± 1.10

7.27 ± 0.00

10.16 ± 1.10

AlexNet

tt

EX-AlexNet

6-layer EX-CNN

5-layer CNN

Latency t (ms)
L

tt

tp

t = tt + tp

2042.48 ± 401.64 1265.89 ± 141.47
1298.23 ± 332.66 1263.16 ± 115.58
1009.79 ± 334.87 1260.44 ± 81.77
976.71 ± 317.48 1263.16 ± 115.58

3308.37 ± 432.91
2561.39 ± 361.81
2270.22 ± 351.10
2239.87 ± 348.56

C

750.02 ± 322.44

1260.44 ± 81.77

2010.46 ± 339.52

1
2
3
4

1304.74 ± 310.87
947.04 ± 258.12
728.19 ± 221.12
727.87 ± 221.10

598.93 ± 81.91
596.19 ± 0.00
596.19 ± 0.00
596.19 ± 0.00

1903.66 ± 324.56
1543.23 ± 258.12
1324.38 ± 221.12
1324.06 ± 221.10

C

725.53 ± 220.95

596.19 ± 0.00

1321.72 ± 220.95

5.5.2 Multi-CNN Configuration

can be placed on the same IoT unit due to L = M 7 . Several
comments arise. First of all, the latency t of 1 AlexNet is
higher than that in the IoT system comprising only Raspberry Pi 3B+ and STM32H7 (see Section 5.4): this is justified
by the fact that in this IoT system the probability that an
IoT unit is a Raspberry is 10%, instead of 50%, and both the
OrangePi Zero and the BeagleBone AI units have a smaller
computation capability.
Second, the latency t of 3 AlexNet is close to that
with 1 AlexNet multiplied by 3. In fact, the difference in
percentage ranges from 0.6% to 3.5% (L = C to L = 1)8 .
When 4 AlexNet CNNs are employed, the range is slightly
higher, i.e., 1 to 5% on the same values of L. This result is
very interesting, showing the effectiveness of the proposed
methodology in placing the CNNs in the given IoT system.
Moreover, by observing the values of ηR , ηO , ηB it is clear
that whenever possible the methodology relies on the fastest
units, as expected by the fact that the transmission latency tt
is, in all the cases, significantly smaller than the processing
tp one. Finally, as commented in Section 5.4.2, the latency t
with L = 1 and L = 2 is close to that with L = C , with
an increment ranging from 13% to 18%, and from 6% to 9%,
with 1 and 4 AlexNet CNNs, respectively, allowing us to

In this bunch of experiments, 1, 3, or 4 AlexNet CNNs have
to be placed in the IoT system. It is worth noting that in the
latter case, when L = 1, 32 nodes out of 50 have to be used,
allowing us to in-depth analyze the best placements.
The results are shown in Table 7, with the hyperparameter L ranging from 1 to 4 and the case L = C
simulating the Cloud, i.e., when all the layers of a CNN

7. It is worth nothing that with L = C , the layers of an (EX–)AlexNet
CNN can be placed on a single node if and only if Raspberry Pi 3B+ or
BeagleBone AI IoT units are employed. If an OrangePi unit is selected
by the methodology, at least another IoT unit has to be considered to
place all the layers, also in this configuration.
8. The error percentage between the latency t3A of placing 3 AlexNet
CNNs and the latency tA of placing 1 AlexNet multiplied by 3 is
computed as follows: (t3A − 3 · tA )/t3A .

account, where x is a technological family of IoT units, i.e.
x can be R, O, or B , representing the Raspberry Pi 3B+, the
OrangePi Zero, and the BeagleBone AI units, respectively.
5.5.1 Single-CNN Configuration
In this configuration, 1 ResNet CNN has to be placed in this
IoT system.
The results are shown in Table 6. The processing latency
tp of a ResNet CNN is extremely high but proportional
to the number of operations required by such CNN to
process a single image, i.e., about 7.5 times than those of
the AlexNet. The methodology indeed does not encompass
any optimization in processing the convolutions or any
other optimization unless one re-compute the number of
required operations accordingly. Since the latency t is almost
only composed by the processing tp (97 to 99% of t), the
methodology relies only on the IoT units having the highest
computation capability, as highlighted by the values of ηB
that are close to zero in almost all the cases.

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

12

TABLE 5: The multi CNN configuration results with N = 30 STM32H7 and Raspberry Pi 3B+ units and two 5-layer CNNs,
in the three scenarios, with the Wi-Fi 4 and Wi-Fi Halow transmission technologies. The figure of merit (mean ± std) is the
latency t, i.e., the transmission time tt plus the processing time tp and is summed over all the CNNs.
(a) The results with the Wi-Fi 4 as adopted transmission technology.
10 – 90 Latency t (ms)

50 – 50 Latency t (ms)

90 – 10 Latency t (ms)

tt

tp

t = tt + tp

tt

tp

t = tt + tp

tt

tp

t = tt + tp

1
2
No shared
3
layers
4
5

14.7 ± 0.3
3.4 ± 0.1
0.9 ± 0.1
0.7 ± 0.1
0.5 ± 0.1

89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0

104.6 ± 0.3
93.3 ± 0.1
90.7 ± 0.1
90.6 ± 0.1
90.4 ± 0.1

15.6 ± 1.1
3.8 ± 0.6
1.1 ± 0.4
0.8 ± 0.3
0.7 ± 0.3

89.9 ± 0.1
89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0

105.4 ± 1.1
93.6 ± 0.6
90.9 ± 0.4
90.7 ± 0.3
90.5 ± 0.3

19.4 ± 5.5
10.2 ± 5.0
4.0 ± 2.9
4.0 ± 4.5
3.0 ± 2.8

634.4 ± 417.0
317.1 ± 401.5
198.0 ± 240.0
119.8 ± 67.0
105.1 ± 34.1

653.8 ± 413.6
327.3 ± 399.7
201.9 ± 242.4
123.7 ± 71.2
108.1 ± 36.6

1
2
3
4
5

14.6 ± 0.1
3.4 ± 0.1
2.0 ± 0.0
0.8 ± 0.0
0.8 ± 0.0

89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0

104.5 ± 0.1
93.3 ± 0.1
91.9 ± 0.0
90.7 ± 0.0
90.6 ± 0.0

15.4 ± 1.2
3.7 ± 0.5
2.2 ± 0.4
0.9 ± 0.3
0.8 ± 0.2

89.9 ± 0.1
89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0
89.9 ± 0.0

105.3 ± 1.2
93.5 ± 0.5
92.1 ± 0.4
90.8 ± 0.3
90.7 ± 0.2

23.4 ± 9.0
9.6 ± 8.6
7.1 ± 5.2
2.3 ± 1.6
2.0 ± 1.4

452.8 ± 470.8
250.6 ± 389.8
115.9 ± 63.1
90.5 ± 1.3
90.2 ± 0.6

476.2 ± 467.4
260.2 ± 388.0
122.9 ± 65.8
92.8 ± 2.2
92.2 ± 1.7

L

First two
layers
shared

(b) The results with the Wi-Fi HaLow as adopted transmission technology.
10 – 90 Latency t (ms)

50 – 50 Latency t (ms)

90 – 10 Latency t (ms)

tt

tp

t = tt + tp

tt

tp

t = tt + tp

tt

tp

t = tt + tp

1
2
No shared
3
layers
4
5

147.2 ± 2.3
34.5 ± 1.5
8.8 ± 1.2
7.0 ± 1.0
5.3 ± 0.9

89.9 ± 0.3
89.9 ± 0.0
89.9 ± 0.3
89.9 ± 0.0
89.9 ± 0.0

237.2 ± 2.3
124.4 ± 1.5
98.8 ± 1.3
96.9 ± 1.0
95.2 ± 0.9

154.4 ± 11.5
37.4 ± 5.3
9.9 ± 2.7
8.1 ± 2.6
6.4 ± 2.7

91.2 ± 6.1
90.0 ± 0.6
90.4 ± 0.9
89.9 ± 0.0
89.9 ± 0.0

245.6 ± 14.1
127.4 ± 5.4
100.3 ± 3.0
98.0 ± 2.6
96.3 ± 2.7

187.0 ± 41.4
95.3 ± 44.4
32.9 ± 28.8
37.5 ± 42.6
28.6 ± 27.0

624.6 ± 416.9
301.7 ± 383.1
188.1 ± 228.8
116.6 ± 64.0
103.5 ± 32.6

811.6 ± 394.1
397.0 ± 372.3
221.0 ± 254.2
154.1 ± 105.1
132.1 ± 57.2

1
2
3
4
5

146.6 ± 1.6
34.1 ± 0.7
20.4 ± 0.7
8.4 ± 0.3
7.6 ± 0.3

89.9 ± 0.3
89.9 ± 0.2
89.9 ± 0.2
89.9 ± 0.2
89.9 ± 0.2

236.5 ± 1.7
124.0 ± 0.8
110.3 ± 0.7
98.3 ± 0.4
97.5 ± 0.3

152.3 ± 9.8
36.0 ± 4.3
21.9 ± 3.9
9.0 ± 2.2
8.2 ± 2.2

90.7 ± 1.2
90.2 ± 0.9
90.1 ± 0.6
90.2 ± 0.9
90.0 ± 0.5

243.1 ± 10.1
126.2 ± 4.5
112.1 ± 4.0
99.2 ± 2.4
98.2 ± 2.2

223.7 ± 63.6
85.4 ± 72.2
65.3 ± 46.3
17.9 ± 14.1
17.1 ± 14.1

454.4 ± 459.1
252.5 ± 389.8
117.0 ± 62.8
92.1 ± 1.5
91.0 ± 0.7

678.0 ± 434.8
338.0 ± 381.7
182.3 ± 97.5
110.0 ± 14.4
108.0 ± 14.2

L

First two
layers
shared

TABLE 6: The single CNN configuration results with N = 50 OrangePi Zero, BeagleBone AI, and Raspberry Pi 3B+
units (with probability 45%-45%-10%) and 1 ResNet CNN. The figures of merit (mean ± std) are the latency t, i.e., the
transmission time tt plus the processing time tp , and the number η of IoT units used.
Latency t (ms)

Node usage η

L

tt

tp

t = tt + tp

ηR

ηO

ηB

1
2
3
4

361.85 ± 60.77
249.47 ± 69.22
183.34 ± 87.14
138.99 ± 85.02

12059.62 ± 430.32
11723.26 ± 319.91
11645.13 ± 259.90
11620.58 ± 236.18

12421.47 ± 406.82
11972.72 ± 313.71
11828.47 ± 267.93
11759.57 ± 252.58

4.92 ± 1.84
3.59 ± 0.90
2.80 ± 0.55
2.14 ± 0.50

4.05 ± 1.84
1.49 ± 0.95
0.55 ± 0.86
0.88 ± 0.55

0.03 ± 0.17
0.01 ± 0.10
0.00 ± 0.06
0.00 ± 0.07

C

127.85 ± 94.81

11602.91 ± 215.07

11730.76 ± 237.14

0.99 ± 0.11

0.08 ± 0.34

0.00 ± 0.00

define processing pipelines in the considered IoT system, to
further reduce the latency t.
In Table 8, the same IoT scenario is investigated with
1, 3, and 4 EX-AlexNet to be placed. The latency t and its
components tp and tt are defined as an expected value, by
weighting the latency of each possible path within the EXCNN by its probability. The mean numbers of nodes used
ηR , ηO , and ηB are instead computed on the longest path
within the EX-CNN.
The trend in the results is analogous to the case with
AlexNet CNNs, with smaller errors. The difference in percentage between placing 3 and 4 EX-AlexNet and 1 EXAlexNet multiplied by 3 and 4 ranges from 0.2% to 2.5%
and from 0.4% to 3.7% (L = C to L = 1), respectively.
Interestingly, the values of ηB are higher in this group
of experiments, showing that the methodology more often
relies on closer BeagleBone AI units to place part of the EXAlexNet computation, reasonably on the less probable path.
The OrangePi Zero units are more often used in this scenario
as well.

6

P ORTING A CNN TO A REAL I OT S YSTEM

The methodology has been also applied to the placement
of the 5-layer CNN described in Section 4.1 and depicted
in Fig. 1(a) on a real technological scenario comprising
two STM32H7s and one Raspberry Pi 3B+. The transmission
technology is the Wi-Fi 4 and the connectivity is provided
locally by the GL.iNet GL-MT300N-V2 router. The goal of
this experiment is to compare the figures of merit t, tt , and
tp of the CNN placement provided by the methodology
with those of the real CNN placement in the considered
technological scenario. With L = 4 and the nodes equally
spaced (each at distance 1 from each other), the methodology assigned the first four layers of the CNN to the
Raspberry and the fifth layer to one of the two STM32H7s.
The measured transmission and processing times, shown
in Table 9, are particularly interesting, showing that the
experimental transmission time tt is almost equal to the
methodology estimation, whereas the experimental processing time tp is 30% larger. This is justified by the fact the
model considered only the multiplications. In particular, the

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

13

TABLE 7: The multi CNN configuration results with N = 50 OrangePi Zero, BeagleBone AI, and Raspberry Pi 3B+ units
(with probability 45%-45%-10%) and 1 to 4 AlexNet (A) CNNs. The figures of merit (mean ± std) are the latency t, i.e., the
transmission time tt plus the processing time tp , and the number η of IoT units used.
Latency t (ms)

1 AlexNet

3 AlexNet

4 AlexNet

Node usage η

L

tt

tp

t = tt + tp

ηR

ηO

ηB

1
2
3
4

206.22 ± 26.04
151.25 ± 30.93
125.55 ± 33.97
119.76 ± 34.24

1 390.95 ± 54.58
1 344.36 ± 56.70
1 328.63 ± 51.73
1 323.49 ± 47.45

1 597.17 ± 54.33
1 495.61 ± 60.89
1 454.19 ± 62.16
1 443.25 ± 59.89

3.97 ± 1.51
3.00 ± 0.87
2.47 ± 0.63
1.96 ± 0.50

4.01 ± 1.48
1.43 ± 1.08
0.64 ± 0.74
0.51 ± 0.73

0.02 ± 0.15
0.01 ± 0.12
0.01 ± 0.12
0.01 ± 0.09

C

97.88 ± 39.57

1 311.71 ± 44.03

1 409.58 ± 66.63

1.00 ± 0.11

0.17 ± 0.45

0.01 ± 0.09

1
2
3
4

578.58 ± 50.35
410.26 ± 43.87
350.06 ± 45.97
349.40 ± 54.44

4 390.39±104.53
4 211.45±148.26
4 108.70±154.98
4 035.36±146.02

4 968.97±119.87
4 621.71±142.12
4 458.76±152.25
4 384.76±147.68

5.07 ± 2.01
5.05 ± 1.97
4.84 ± 1.71
4.46 ± 1.34

17.89±1.72
7.72 ± 1.95
4.65 ± 1.98
3.13 ± 1.86

1.05 ± 1.24
0.11 ± 0.38
0.04 ± 0.26
0.04 ± 0.26

C

306.24 ± 76.75

3 947.47±106.77

4 253.71±144.39

2.86 ± 0.46

0.90 ± 1.33

0.02 ± 0.21

1
2
3
4

772.23 ± 54.88
521.34 ± 36.80
437.76 ± 50.07
441.12 ± 59.81

5 960.88±138.87
5 718.77±181.19
5 572.27±206.36
5 458.45±213.15

6 733.11±156.94
6 240.11±175.43
6 010.03±196.11
5 899.57±201.50

5.22 ± 2.20
5.22 ± 2.20
5.17 ± 2.12
4.99 ± 1.85

21.73±2.80
11.62±2.20
7.47 ± 2.34
5.25 ± 2.36

5.04 ± 2.99
0.19 ± 0.55
0.07 ± 0.40
0.10 ± 0.38

C

401.83 ± 77.75

5 288.65±150.73

5 690.48±183.33

3.64 ± 0.74

1.81 ± 1.93

0.04 ± 0.30

TABLE 8: The multi CNN configuration results with N = 50 OrangePi Zero, BeagleBone AI, and Raspberry Pi 3B+ units
(with probability 45%-45%-10%) and 1 to 4 EX-AlexNet CNNs. The figures of merit (mean ± std) are the latency t, i.e., the
transmission time tt plus the processing time tp , and the number η of IoT units used.
Latency t (ms)

1 AlexNet

3 AlexNet

4 AlexNet

Node usage η

L

tt

tp

t = tt + tp

ηR

ηO

ηB

1
2
3
4

117.54 ± 17.66
93.87 ± 24.95
77.03 ± 25.44
74.56 ± 24.62

666.38 ± 33.56
643.84 ± 34.46
641.06 ± 34.80
640.61 ± 33.94

783.92 ± 36.27
737.71 ± 40.10
718.09 ± 41.04
715.17 ± 40.58

4.08 ± 1.46
3.09 ± 0.82
2.66 ± 0.58
1.98 ± 0.49

3.79 ± 1.45
1.51 ± 1.00
0.44 ± 0.67
0.44 ± 0.71

0.13 ± 0.34
0.07 ± 0.25
0.02 ± 0.13
0.00 ± 0.06

C

68.15 ± 24.14

639.05 ± 34.41

707.20 ± 42.28

1.00 ± 0.06

0.24 ± 0.49

0.01 ± 0.08

1
2
3
4

335.42 ± 21.31
268.92 ± 38.28
222.56 ± 39.05
222.98 ± 39.87

2 078.03 ± 54.60
1989.59 ± 72.05
1971.77 ± 75.12
1946.47 ± 73.10

2 413.45 ± 59.52
2258.52 ± 72.76
2194.33 ± 75.51
2169.45 ± 76.50

4.95 ± 2.08
4.91 ± 2.03
4.79 ± 1.90
4.37 ± 1.43

17.26±1.72
8.36 ± 1.82
4.84 ± 2.22
3.37 ± 2.00

1.79 ± 1.29
0.55 ± 0.78
0.17 ± 0.59
0.11 ± 0.36

C

211.27 ± 42.69

1914.79 ± 64.03

2126.06 ± 75.80

2.87 ± 0.51

1.08 ± 1.36

0.03 ± 0.17

1
2
3
4

452.33 ± 29.81
346.37 ± 43.73
284.80 ± 46.16
289.94 ± 44.66

2803.39 ± 67.85
2689.37 ± 94.61
2666.04 ± 100.07
2619.44 ± 103.84

3255.73 ± 78.62
3035.74 ± 93.17
2950.84 ± 96.52
2909.38 ± 102.62

4.95 ± 2.17
4.95 ± 2.17
4.93 ± 2.13
4.79 ± 1.89

21.52±2.72
12.39±1.79
8.07 ± 2.15
5.59 ± 2.24

5.53 ± 2.56
1.19 ± 1.35
0.72 ± 1.05
0.25 ± 0.68

C

281.67 ± 50.74

2558.70 ± 98.07

2840.36 ± 105.54

3.63 ± 0.95

1.86 ± 2.12

0.12 ± 0.51

first four layers on Raspberry Pi 3B+ took 68.29 ms instead
of 44.93 ms, whereas the fifth layer on STM32H7 176 µs (32
µs with code optimization) instead of 50 µs.
It is worth nothing that the measured processing time
tp of the AlexNet on the Raspberry Pi 3B+ (median over
100 runs) is 1119.47 ms, whereas the one provided by the
methodology is 1257.71 ms, showing that the approximation
given in Section 4 well describe this technological scenario.

TABLE 9: Experimental benchmark results with equally
spaced nodes and a 5-layer CNN. The figure of merit is the
latency t (transmission tt plus processing tp ).

7

deal with communications failures and mobile units as well
as improve the performance by exploiting the resources that
are made available by early-exit mechanisms.

C ONCLUSIONS

The aim of this paper was to introduce a novel effective
methodology for the optimal placement of CNNs on IoT
systems. Such a methodology is general enough to be applied to multiple sources of data and multiple CNNs operating in the same IoT system and has been formalized as
an optimization problem where the latency between image
acquisitions and the decision making is minimized. Future
works will encompass the extension of the methodology
with dynamic scheduling and routing algorithms for IoT to

L

Case

Wi-Fi 4 Latency (ms)
tt

4

tp

t = tt + tp

Model

0.37

44.98

45.35

Experimental

0.42

68.47

68.89

R EFERENCES
[1]

Z. Zhang, J. Geiger, J. Pohjalainen, A. E.-D. Mousa, W. Jin, and
B. Schuller, “Deep learning for environmentally robust speech
recognition: An overview of recent developments,” ACM Transactions on Intelligent Systems and Technology (TIST), vol. 9, no. 5, pp.
1–28, 2018.

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

14

(a) The IoT system.

(b) The outcome with L = 1 and 3 EX-A.

(c) The outcome with L = 2 and 3 EX-A.

(d) The outcome with L = 1 and 3 A.

(e) The outcome with L = 2 and 3 A.

(f) The outcome with L = C and 3 (EX–)A.

Fig. 4: An example of the methodology outcome on a IoT system comprising N = 50 IoT units, i.e. Raspberry Pi 3B+,
OrangePi Zero, and BeagleBone AI (10%, 45%, and 45% the probability of each kind of unit) and three (EX–)AlexNet CNNs
to be placed. The sources are indicated by a star, whereas the target unit by a circled cross. The transmission range is
indicated only for the sources and the target and is equal for all nodes. When EX–AlexNet CNNs (EX–A) are employed,
the path with probability 0.772 is indicated by the thicker line, whereas the full path continues with the thin one.

R. D. Hof, “10 breaktrough technologies 2013: Deep learning,” MIT
Technology Review, 2013.
[3] C. Szegedy, W. Liu, Y. Jia, P. Sermanet, S. Reed, D. Anguelov,
D. Erhan, V. Vanhoucke, and A. Rabinovich, “Going deeper with
convolutions,” in Proceedings of the IEEE conference on computer
vision and pattern recognition, 2015, pp. 1–9.
[4] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in The IEEE Conference on Computer Vision and
Pattern Recognition (CVPR), June 2016.
[5] Y. LeCun, Y. Bengio, and G. Hinton, “Deep learning,” nature, vol.
521, no. 7553, pp. 436–444, 2015.
[6] K. Simonyan and A. Zisserman, “Very deep convolutional
networks for large-scale image recognition,” arXiv preprint
arXiv:1409.1556, 2014.
[7] K. He and J. Sun, “Convolutional neural networks at constrained
time cost,” in Proceedings of the IEEE conference on computer vision
and pattern recognition, 2015, pp. 5353–5360.
[8] C. Alippi, S. Disabato, and M. Roveri, “Moving convolutional
neural networks to embedded systems: the alexnet and vgg-16
case,” in 2018 17th ACM/IEEE International Conference on Information Processing in Sensor Networks (IPSN). IEEE, 2018, pp. 212–223.
[9] J. Dean, G. Corrado, R. Monga, K. Chen, M. Devin, M. Mao,
M. Ranzato, A. Senior, P. Tucker, K. Yang et al., “Large scale
distributed deep networks,” in Advances in neural information processing systems, 2012, pp. 1223–1231.
[10] H. Cui, H. Zhang, G. R. Ganger, P. B. Gibbons, and E. P. Xing,
“Geeps: Scalable deep learning on distributed gpus with a gpuspecialized parameter server,” in Proceedings of the Eleventh European Conference on Computer Systems, 2016, pp. 1–16.
[11] C. Hardy, E. Le Merrer, and B. Sericola, “Distributed deep learning
on edge-devices: feasibility via adaptive compression,” in 2017
[2]

IEEE 16th International Symposium on Network Computing and Applications (NCA). IEEE, 2017, pp. 1–8.
[12] M. Mohammadi, A. Al-Fuqaha, S. Sorour, and M. Guizani, “Deep
learning for iot big data and streaming analytics: A survey,” IEEE
Communications Surveys & Tutorials, vol. 20, no. 4, pp. 2923–2960,
2018.
[13] S. Disabato and M. Roveri, “Incremental on-device tiny machine
learning,” in Proceedings of the 2nd International Workshop on Challenges in Artificial Intelligence and Machine Learning for Internet of
Things, 2020, pp. 7–13.
[14] Z. Zhao, K. M. Barijough, and A. Gerstlauer, “Deepthings: Distributed adaptive deep learning inference on resource-constrained
iot edge clusters,” IEEE Transactions on Computer-Aided Design of
Integrated Circuits and Systems, vol. 37, no. 11, pp. 2348–2359, 2018.
[15] C. Alippi and M. Roveri, “The (not) far-away path to smart cyberphysical systems: An information-centric framework,” Computer,
vol. 50, no. 4, pp. 38–47, 2017.
[16] A. Krizhevsky, I. Sutskever, and G. E. Hinton, “ImageNet classification with deep convolutional neural networks,” in Proceedings
of the 25th International Conference on Neural Information Processing
Systems - Volume 1, ser. NIPS ’12, vol. 1. Curran Associates Inc.,
2012, pp. 1097–1105.
[17] J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, “You Only
Look Once: Unified, Real-Time Object Detection,” in 2016 IEEE
Conference on Computer Vision and Pattern Recognition (CVPR), ser.
CPVR ’16. IEEE, jun 2016, pp. 779–788.
[18] T. Bolukbasi, J. Wang, O. Dekel, and V. Saligrama, “Adaptive
neural networks for efficient inference,” in Proceedings of the 34th
International Conference on Machine Learning-Volume 70, 2017, pp.
527–536.
[19] S. Disabato and M. Roveri, “Reducing the computation load of
convolutional neural networks through gate classification,” in

IEEE TRANSACTIONS ON COMPUTERS, VOL. 70, NO. 8, AUGUST 2021

2018 International Joint Conference on Neural Networks (IJCNN).
IEEE, 2018, pp. 1–8.
[20] B. Moons, R. Uytterhoeven, W. Dehaene, and M. Verhelst, “14.5
envision: A 0.26-to-10tops/w subword-parallel dynamic-voltageaccuracy-frequency-scalable convolutional neural network processor in 28nm fdsoi,” in 2017 IEEE International Solid-State Circuits
Conference (ISSCC). IEEE, 2017, pp. 246–247.
[21] C. Zhang, P. Li, G. Sun, Y. Guan, B. Xiao, and J. Cong, “Optimizing fpga-based accelerator design for deep convolutional neural
networks,” in Proceedings of the 2015 ACM/SIGDA International
Symposium on Field-Programmable Gate Arrays, 2015, pp. 161–170.
[22] N. Suda, V. Chandra, G. Dasika, A. Mohanty, Y. Ma, S. Vrudhula,
J.-s. Seo, and Y. Cao, “Throughput-optimized opencl-based fpga
accelerator for large-scale convolutional neural networks,” in Proceedings of the 2016 ACM/SIGDA International Symposium on FieldProgrammable Gate Arrays, 2016, pp. 16–25.
[23] L. Cavigelli and L. Benini, “Origami: A 803-gop/s/w convolutional network accelerator,” IEEE Transactions on Circuits and
Systems for Video Technology, vol. 27, no. 11, pp. 2461–2475, 2016.
[24] G.-Y. Wei, D. Brooks et al., “Benchmarking tpu, gpu, and cpu
platforms for deep learning,” arXiv preprint arXiv:1907.10701, 2019.
[25] S. Han, H. Mao, and W. J. Dally, “Deep compression: Compressing
deep neural networks with pruning, trained quantization and
huffman coding,” arXiv preprint arXiv:1510.00149, 2015.
[26] Y. He, X. Zhang, and J. Sun, “Channel pruning for accelerating
very deep neural networks,” in The IEEE International Conference
on Computer Vision (ICCV), Oct 2017.
[27] S. Lin, R. Ji, C. Chen, D. Tao, and J. Luo, “Holistic cnn compression
via low-rank decomposition with knowledge transfer,” IEEE transactions on pattern analysis and machine intelligence, vol. 41, no. 12, pp.
2889–2905, 2018.
[28] Z. Cai, X. He, J. Sun, and N. Vasconcelos, “Deep learning with
low precision by half-wave gaussian quantization,” in Proceedings
of the IEEE Conference on Computer Vision and Pattern Recognition,
2017, pp. 5918–5926.
[29] E. L. Denton, W. Zaremba, J. Bruna, Y. LeCun, and R. Fergus,
“Exploiting linear structure within convolutional networks for
efficient evaluation,” in Advances in Neural Information Processing
Systems, 2014, pp. 1269–1277.
[30] M. Courbariaux, Y. Bengio, and J.-P. David, “Binaryconnect: Training deep neural networks with binary weights during propagations,” in Advances in neural information processing systems, 2015,
pp. 3123–3131.
[31] M. Rastegari, V. Ordonez, J. Redmon, and A. Farhadi, “Xnornet: Imagenet classification using binary convolutional neural
networks,” in European conference on computer vision. Springer,
2016, pp. 525–542.
[32] D. Li, X. Wang, and D. Kong, “Deeprebirth: Accelerating deep
neural network execution on mobile devices,” in Thirty-second
AAAI conference on artificial intelligence, 2018.
[33] C. Shi, V. Lakafosis, M. H. Ammar, and E. W. Zegura, “Serendipity: Enabling remote computing among intermittently connected
mobile devices,” in Proceedings of the Thirteenth ACM International
Symposium on Mobile Ad Hoc Networking and Computing, ser. MobiHoc ’12. New York, NY, USA: ACM, 2012, pp. 145–154.
[34] K. Hong, D. Lillethun, U. Ramachandran, B. Ottenwälder, and
B. Koldehofe, “Mobile fog: A programming model for large-scale
applications on the internet of things,” in Proceedings of the Second
ACM SIGCOMM Workshop on Mobile Cloud Computing, ser. MCC
’13. New York, NY, USA: ACM, 2013, pp. 15–20.
[35] D. Hu and B. Krishnamachari, “Throughput optimized scheduler
for dispersed computing systems,” in 2019 7th IEEE International
Conference on Mobile Cloud Computing, Services, and Engineering
(MobileCloud). IEEE, 2019, pp. 76–84.
[36] Z. Cheng, P. Li, J. Wang, and S. Guo, “Just-in-time code offloading
for wearable computing,” IEEE Transactions on Emerging Topics in
Computing, vol. 3, no. 1, pp. 74–83, 2015.
[37] S. Teerapittayanon, B. McDanel, and H.-T. Kung, “Distributed
deep neural networks over the cloud, the edge and end devices,”
in 2017 IEEE 37th International Conference on Distributed Computing
Systems (ICDCS). IEEE, 2017, pp. 328–339.
[38] K. Bhardwaj, C.-Y. Lin, A. Sartor, and R. Marculescu, “Memoryand communication-aware model compression for distributed
deep learning inference on iot,” ACM Transactions on Embedded
Computing Systems (TECS), vol. 18, no. 5s, pp. 1–22, 2019.
[39] J. Chen, K. Li, Q. Deng, K. Li, and S. Y. Philip, “Distributed deep

15

learning model for intelligent video surveillance systems with
edge computing,” IEEE Transactions on Industrial Informatics, 2019.
[40] D. Hu and B. Krishnamachari, “Fast and accurate streaming cnn
inference via communication compression on the edge,” in 2020
IEEE/ACM Fifth International Conference on Internet-of-Things Design
and Implementation (IoTDI). IEEE, 2020, pp. 157–163.
[41] Z. Tao and Q. Li, “esgd: Communication efficient distributed deep
learning on the edge,” in {USENIX} Workshop on Hot Topics in Edge
Computing (HotEdge 18), 2018.
[42] R. M. Karp, “Reducibility among combinatorial problems,” in
Complexity of computer computations. Springer, 1972, pp. 85–103.
[43] L. Farhan, S. T. Shukur, A. E. Alissa, M. Alrweg, U. Raza, and
R. Kharel, “A survey on the challenges and opportunities of the
internet of things (iot),” in 2017 Eleventh International Conference on
Sensing Technology (ICST). IEEE, 2017, pp. 1–5.
[44] J. Yosinski, J. Clune, Y. Bengio, and H. Lipson, “How transferable
are features in deep neural networks?” in Advances in neural
information processing systems, 2014, pp. 3320–3328.
[45] Y. Xiao, “Ieee 802.11 n: enhancements for higher throughput in
wireless lans,” IEEE Wireless Communications, vol. 12, no. 6, pp.
82–91, 2005.
[46] T. Adame, A. Bel, B. Bellalta, J. Barcelo, and M. Oliver, “Ieee 802.11
ah: the wifi approach for m2m communications,” IEEE Wireless
Communications, vol. 21, no. 6, pp. 144–152, 2014.
PAPER_TEXT
