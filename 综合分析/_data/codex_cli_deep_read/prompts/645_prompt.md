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
# [645] Developing A Domain-Specific LLM for Optical Networks: A Reinforcement Learning-Based Fine-Tuning Framework
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
编号：645
题名：Developing A Domain-Specific LLM for Optical Networks: A Reinforcement Learning-Based Fine-Tuning Framework
年份：2026
DOI：10.1109/tnsm.2026.3676522
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2026.3676522.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：无
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\645.txt
- 原始字符数：102174
- 本次发送字符数：102174
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

3655

Developing A Domain-Specific LLM for Optical
Networks: A Reinforcement Learning-Based
Fine-Tuning Framework
Yanli Liu , Yue Pang, Yidi Wang , Graduate Student Member, IEEE, Shengnan Li , Jin Li , Min Zhang,
and Danshi Wang , Senior Member, IEEE
Abstract—Optical networks serve as the backbone of modern
communication infrastructure, where efficient operation and
maintenance (O&M) are essential for ensuring reliable and
high-speed data services. However, traditional network O&M
face persistent challenges, including high labor costs, delayed
response time, and difficulties in processing massive and complex
network data. Although large language models (LLMs) have
demonstrated strong capabilities in text understanding, generation, and reasoning, their direct application in optical network
O&M is limited by domain-specific knowledge barriers, inherent reasoning biases, and insufficient performance in complex
multi-step tasks. To address this issue, this study develops a
domain-adaptation and system-implementation framework that
applies two established reinforcement learning-based fine-tuning
methods (RLHF and ReFT) to construct domain-specialized
LLMs for optical network O&M tasks. In the context of log
analysis, RLHF achieves improvements of 1.64 points in accuracy,
1.02 points in content richness, and a notable 10-point increase
in interactivity over supervised fine-tuning. In alarm localization,
ReFT achieves accuracy improvements of 2%–13% across four
reasoning tasks. The extensive tests not only demonstrate the
practical value of RL-based fine-tuning in enhancing alignment
and reasoning for domain-specific applications, but also provides
a practical methodology and implementation reference for applying reinforcement learning-based LLM adaptation in optical
network O&M environments.
Index Terms—Large language model, reinforcement learning
from human feedback, reinforced fine-tuning, optical networks.

I. I NTRODUCTION
PTICAL networks constitute the backbone of modern
communication infrastructure, where efficient operation
and maintenance (O&M) play a critical role in ensuring
high-speed data transmission, reliable service delivery, and

O

Received 6 January 2026; revised 16 March 2026; accepted 17 March 2026.
Date of publication 23 March 2026; date of current version 31 March 2026.
This work supported in part by the National Natural Science Foundation of
China under Grant U24B20133 and Grant 62522104. The associate editor
coordinating the review of this article and approving it for publication was E.
Nowroozi. (Corresponding author: Danshi Wang.)
Yanli Liu, Yidi Wang, Shengnan Li, Min Zhang, and Danshi Wang
are with the State Key Laboratory of Information Photonics and Optical
Communications, Beijing University of Posts and Telecommunications,
Beijing
100876,
China
(e-mail:
yanli liu@bupt.edu.cn;
wangyidi@bupt.edu.cn; shengnanli@bupt.edu.cn; mzhang@bupt.edu.cn;
danshi wang@bupt.edu.cn).
Yue Pang is with the Cloud Network Operating System Research
and Development Center, China Telecom, Beijing 102299, China (e-mail:
pangy18@chinatelecom.cn).
Digital Object Identifier 10.1109/TNSM.2026.3676522
Jin Li is with the School of Optoelectronic Science and Engineering, South China Normal University, Guangzhou 510006, China (e-mail:
lijin930629@163.com).
Digital Object Identifier 10.1109/TNSM.2026.3676522

secure network environments [1]. However, traditional optical
network O&M paradigms still rely heavily on human expertise
and manual operations, leading to high labor costs, complex
data analysis processes, and delayed fault response [2], [3],
[4]. As optical networks continue to scale in size and complexity, these limitations increasingly hinder the realization of
intelligent, autonomous, and efficient network management.
In recent years, the rapid development of generative artificial intelligence (GenAI) has brought large language models
(LLMs), such as ChatGPT [5] and LLaMA [6], [7], to the
forefront of artificial intelligence research. Benefiting from
large-scale pretraining, LLMs exhibit strong capabilities in
natural language understanding, text generation, and complex
reasoning [8]. These models have demonstrated remarkable
success across a wide range of real-world applications. For
example, in code review tasks, LLMs are capable of automatically generating review comments, assisting engineers
in understanding code logic, identifying potential defects,
and suggesting revisions, thereby improving development efficiency and code quality [9]. In network intrusion detection,
LLMs have been leveraged to analyze traffic patterns and
abnormal behaviors, infer attack paths, and generate interpretable security reports and response strategies, enhancing
both detection accuracy and system explainability [10]. These
achievements highlight the strong generalization ability and
task adaptability of LLMs, suggesting their potential to support
intelligent O&M in optical networks.
Motivated by these successes, researchers have begun to
explore the application of LLMs to optical network O&M
tasks, including quality-of-transmission (QoT) estimation and
optimization [11], simulation assistance [12], and automated
network control [13], [14], [15], [16]. Despite their promising performance, directly deploying general-purpose LLMs
in optical network scenarios remains challenging. Optical
networks are highly specialized systems that demand extreme
robustness, reliability, and domain-specific reasoning. In practice, LLMs often suffer from domain knowledge gaps [17],
inherent reasoning biases [18], and task-specific constraints
[19], which limit their effectiveness in professional O&M
applications. These challenges underscore the necessity of
adapting LLMs to the optical network domain.
To bridge the gap between general-purpose LLMs and
domain-specific optical network tasks, model adaptation
techniques are required. Among existing approaches, reinforcement learning (RL)-based fine-tuning has emerged as a
particularly promising direction. Unlike conventional super-

1932-4537 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

3656

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

vised learning, RL-based methods enable models to optimize
their behavior through interaction with reward signals, allowing them to go beyond simple imitation of labeled data.
By incorporating rule-based or human preference-based feedback, RL-based fine-tuning can enhance alignment with expert
intent, reduce hallucinations, and improve reasoning consistency. These properties are especially desirable for complex
optical network O&M tasks, such as log analysis and alarm
root cause localization, which involve multi-step reasoning and
high interpretability requirements.
In this paper, RL-based fine-tuning techniques are applied
to address complex and professional tasks in optical networks,
and a dual-strategy adaptive framework is constructed to
support LLM-based network log analysis and alarm localization. The framework leverages established reinforcement
learning approaches to enhance the domain adaptability of
LLMs for optical network operation and maintenance tasks.
Through empirical analysis and validation on two representative case studies, this work demonstrates how reinforcement
learning can be effectively integrated into LLMs in optical
network scenarios and provides practical insights for applying
RL-based methods in optical networks and related domains.
The main contributions of this work include:
1) The implementation processes and applicable scenarios
of typical RL techniques in LLMs are summarized,
providing practical guidance for domain specialization.
2) RLHF is applied to enhance the alignment between
optical network log analysis outputs and human intent.
Task accuracy of 9.09 points, richness of 7.2 points, and
interactivity of 10 points are achieved by the final model.
Compared with the SFT model, the accuracy of the
preference model is improved by 1.64 points, richness is
increased by 1.02 points, and interactivity is increased
by 10 points.
3) ReFT is employed to improve LLM performance in
complex reasoning tasks related to network RCL.
The results show that accuracy in all four tasks was
improved: the task of extracting topological relationships
of real-time alarms was completed with 98% accuracy,
an increase of 2%; the task of extracting alarm propagation of real-time alarms was completed with 99%
accuracy, an increase of 13%; the generation of the
alarm event matrix was achieved with 99% accuracy,
an increase of 5%; and the identification of root alarms
was achieved with 96% accuracy, an increase of 6%.
4) An in-depth analysis of the validation outcomes is
conducted, and key challenges and practical insights
are summarized, providing valuable guidance for the
application of RL-based fine-tuning to LLM.
The remainder of this paper is organized as follows. Section II reviews related work on LLM applications in optical
network O&M and existing domain adaptation techniques,
with a focus on supervised and reinforcement learning-based
fine-tuning methods. Section III presents the principles and
overall framework of the proposed dual-strategy reinforcement
learning adaptation approach, including RLHF and ReFT.
Section IV describes the two representative tasks considered
in this study, namely log analysis and alarm root cause

localization, along with their corresponding reinforcement
learning strategies. Section V details the implementation settings, datasets, hyperparameter configurations, and evaluation
metrics. Section VI provides performance evaluation and
performance analysis for both tasks. Finally, Section VII
concludes the paper and discusses future research directions.
II. R ELATE W ORK
A. LLM Applications in Optical Network O&M
With the increasing maturity of large language models,
several studies have investigated their application to optical
network O&M tasks. Existing works have explored the use of
LLMs for quality-of-transmission estimation and optimization
[11], network simulation assistance [12], and automated control and decision-making [13], [14], [15], [16]. These studies
demonstrate that LLMs can effectively leverage textual and
structured information to support network management tasks.
However, most existing approaches rely on directly applying
pretrained or lightly adapted models, which often struggle
with domain-specific constraints, complex operational rules,
and high reliability requirements intrinsic to optical networks.
B. Domain Adaptation Techniques for LLMs
To improve LLM performance in specialized domains,
three primary adaptation strategies have been widely studied:
external augmentation, prompt engineering, and model finetuning [20], [21], [22]. External augmentation enables LLMs
to access external knowledge bases or tools, offering flexibility
and extensibility. However, its effectiveness strongly depends
on retrieval accuracy and knowledge coverage, and frequent
external queries may introduce significant latency [23]. Prompt
engineering aims to elicit task-specific behavior by carefully
designing instructions and examples. While effective for simple tasks, this approach often exhibits limited reasoning depth
and requires long input prompts, which are constrained by the
model’s context window [24]. This limitation is particularly
pronounced in optical network tasks that involve detailed
operational rules, network topology, and resource allocation
strategies.
Model fine-tuning adjusts the internal parameters of LLMs
to better capture domain-specific patterns and reasoning processes. Compared with external augmentation and prompt
engineering, fine-tuning generally achieves stronger domain
adaptation, albeit at the cost of additional training effort and
computational resources.
C. Supervised and Reinforcement Learning-Based
Fine-Tuning
Among fine-tuning approaches, supervised fine-tuning
(SFT) has been widely adopted due to its simplicity and
effectiveness. By learning from expert-labeled data, SFT can
significantly improve LLM performance on specific tasks
[25]. In optical network O&M, SFT has been applied to
tasks such as log analysis and alarm root cause localization
[26], [27]. However, existing studies reveal notable limitations. SFT-trained models often fail to fully capture expert

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

3657

Fig. 1. Optical network operation and maintenance process based on (a) logs and (b) alarms analysis under dual strategies.

intent, leading to incomplete analyses, hallucinated network
parameters, or missing recommendations. Moreover, their reasoning accuracy remains insufficient for complex multi-step
tasks.
To address these limitations, reinforcement learning-based
fine-tuning has gained increasing attention [28], [29]. Reinforcement Learning from Human Feedback (RLHF) utilizes
a reward model trained on human preferences to guide policy updates, improving alignment with human intent and
reducing hallucinations [30]. Reinforced Fine-Tuning (ReFT),
in contrast, directly leverages environment feedback without
preference-labeled data, demonstrating strong improvements
in multi-step reasoning and decision-making capabilities [31].
These advances indicate that RL-based fine-tuning offers a
powerful mechanism for enhancing alignment, robustness,
and reasoning performance of LLMs in domain-specific
applications.
III. P RINCIPLE AND F RAMEWORK
In optical network O&M, two representative and tightly
coupled tasks are considered in this work: log analysis and
alarm root cause localization.
Log analysis focuses on interpreting raw operational logs
generated by heterogeneous network devices, with the goal
of resolving ambiguous semantics, normalizing domainspecific terminology, and enriching contextual information
related to network states and events. Alarm root cause
localization, on the other hand, aims to identify the underlying faults responsible for observed alarm patterns by
reasoning over network topology and alarm propagation
relationships.
In practical O&M scenarios, these two tasks are not
performed independently but are naturally organized as a tasklevel workflow. Log analysis typically serves as the entry point
of the O&M process, where raw logs are first transformed
into structured and semantically clarified representations. This

process provides a coherent understanding of network behavior
and supports preliminary anomaly identification, as illustrated
in Fig. 1(a).
Building upon the clarified semantics obtained from log
analysis, alarm root cause localization further integrates
network topology information and alarm propagation dependencies to infer potential fault propagation paths. As a result,
alarm localization inherently relies on the outputs of log analysis, forming a sequential O&M workflow in which higher-level
reasoning and decision-making are grounded in prior semantic
understanding rather than performed in isolation, as shown in
Fig. 1(b).
To adapt LLMs to this continuous and dependency-aware
operational workflow, RL–based fine-tuning is introduced at
different stages of the pipeline using two established techniques: RLHF and ReFT. RLHF is applied at the log analysis
stage to enhance domain semantic alignment, operational
preference modeling, and context-aware interpretation of raw
logs, enabling the generation of structured and semantically
consistent representations (Fig. 1(a)). Subsequently, ReFT is
employed at the alarm localization stage to improve inference
consistency and multi-step logical reasoning for topologyaware analysis and alarm propagation inference. Although
RLHF and ReFT target different optimization objectives and
are implemented independently, they together form a logically
ordered adaptive strategy that reflects the inherent sequence of
optical network O&M tasks.
From an implementation perspective, both RLHF and ReFT
follow a unified reinforcement learning based fine-tuning
paradigm. Specifically, they share a common three-stage
training pipeline consisting of supervised fine-tuning (SFT),
reward model construction, and policy optimization, as shown
in Fig. 2. In the remainder of this section, we provide a
detailed description of the technical principles and implementation details of these two methods within the proposed
framework.

3658

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 2. Three-stage implementation process of RLHF and ReFT: The framework consists of three sequential stages. (a) Supervised Fine-Tuning: Fine-tunes
the base model on labeled data. (b) Reward Model: In RLHF, a reward model is trained based on human preference data to score model outputs, while
in ReFT, a handcrafted reward function is designed to directly evaluate responses. (c) Policy Optimization: Optimizes the model policy via reinforcement
learning, guided by the reward model or reward function.

A. Supervised Fine-Tuning
SFT refers to the process of fine-tuning a pre-trained LLM
on a labeled dataset tailored to specific downstream tasks,
thereby enhancing the model’s adaptability to solve related
problems [32], as shown in Fig. 2 (a). In this context, we
consider an LLM parameterized by θ. Let x and y denote
the model’s input and the corresponding output label, thereby
forming the SFT dataset DSF T = {xi , yi }N
i=1 , where N
represents the number of samples in the SFT dataset. In theory,
the goal of SFT is to adjust the model parameters so that the
model generates a response similar to the label with a higher
probability. Therefore, the training objective of SFT can be
formally expressed as [33]:
LSF T (θ) = −Ex,y∼DSF T [log pθ (y|x)]

(1)

where pθ (y|x) represents the model’s predicted probability of
the correct label y given the input x.
B. Reward Model
The reward model plays a pivotal role in providing feedback
on the actions of the model in RL algorithms, as shown
in Fig. 2(b). In RLHF, an explicit reward model is trained
based on human labelers’ preferences, enabling the model to
assign higher rewards to responses that better align with human
expectations. In ReFT, although no explicit reward model is

trained, a task-specific reward function or evaluation mechanism is constructed to assess whether the model’s outputs
match predefined correct answers in mathematical reasoning
tasks. In this sense, both RLHF and ReFT involve forms
of task-oriented modeling to guide fine-tuning, ensuring that
the model’s behavior aligns with either human preferences or
established task standards.
1) Reward Modeling of RLHF: In RLHF, the first step in
training a reward model is to collect preference data from
a group of human labelers. Different responses to the same
questions are then sampled from various model baselines [34]
and presented to the human labelers for ranking. The resulting
data is transformed into a set of prompt-chosen-rejected trios
(i)
(i)
1
and can be denoted as DReward = {x(i) , ychosen , yrejected }N
i=1 ,
where the chosen response is preferred over the rejected
response for training and the N1 is the number of samples
in the reward dataset.
In theory, training the reward model is based on the BradleyTerry model [35], which is used to estimate the probability that
pairwise comparison i < j is true, as calculated:
P (i > j) =

eβi
eβi + eβj

(2)

where eβi and eβj represent the probabilities assigned to
individuals i and j respectively.

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

3659

The reward model should assign a higher score to the
preferred response than to the rejected one. Therefore, the
objective function of training the reward model is:

The term Ât denotes the advantage estimate, which is
introduced to reduce variance in policy gradient estimation.
A value-function baseline Vφ (st ) is employed, yielding
At = Qt − Vφ (st ).

LReward (θ) = −E(x,ychosen ,yrejected )∼DReward
[log(σ(rθ (x, ychosen ) − rθ (x, yrejected )))]

(3)

In practice, the reward model is typically implemented
either by appending a linear layer to predict a single logit
or by removing the final decoding layers and replacing them
with a linear layer.
2) Reward Function of ReFT: In the reward function of
ReFT, the reward values indicate whether the final answer is
correct. Accordingly, the reward function is designed to compare model-generated answers with the corresponding golden
answers. To achieve this, it is essential to construct a dataset
consisting of (question, golden answer) pairs, denoted as (x,
y). When generating outputs for the corresponding inputs x in
the model, the answers y ∗ are extracted and compared with the
golden answers y, based on the dataset’s predefined format.
C. Proximal Policy Optimization
Proximal Policy Optimization (PPO) is a typical off-policy
Actor-critic RL algorithm [36]. A common approach is to
choose the SFT model as the initial policy in PPO, denoted as
πSF T (y|x). A new dataset only concludes prompt needs to be
2
prepared as DP P O = {xi }N
i=1 , among them, N2 represents the
number of datasets in PPO. In the process of training, a batch
of data is fed into the Actor model, which generates a sequence
of input-output pairs (x, y). The reward model then assigns a
reward value r (x, y) to each pair. Subsequently, optimization
iterations are carried out with the aim of obtaining higher
reward values. Therefore, the objective of PPO training is to
maximize the following objective function:
L(πφRL ) = −Ex∼DRL ,y∼πRL (y|x) [r(x, y)
− λ · DKL (πφRL (y|x)||π SF T (y|x))]

πθ (at | st )
.
πθold (at | st )

In practice, the advantage is computed using Generalized
Advantage Estimation (GAE), where the temporal-difference
residual is defined as
δt = rt + γVφ (st+1 ) − Vφ (st ),

(8)

and the resulting advantage estimate is
X
Ât =
l = 0∞ (γλ)l δt+l .

(9)

For numerical stability, the advantages are normalized
within each mini-batch before being substituted into the
clipped objective, thereby completing the policy update procedure
In summary, RLHF is particularly effective in capturing
implicit human preferences by learning a reward model from
human feedback, which serves as a proxy for subjective
quality. This model guides policy optimization to improve
naturalness and alignment with human intent. In contrast,
ReFT directly defines reward functions based on task-specific
rules or correctness criteria, offering greater transparency and
control. While RLHF learns the reward signal from data, ReFT
designs it explicitly—highlighting a key difference in their
underlying principles and making them suitable for different
types of tasks.
IV. TASKS D ESCRIPTION
In this section, we evaluate the effectiveness of the dualstrateg adaptation framework by studying two representative
tasks in optical networks: optical network log analysis and
alarm root cause localization.
A. Log Analysis Task Based on RLHF

(4)

where πφRL (y|x) is the learned RL policy with parameters ϕ,
the Kullback-Leibler (KL) regularization [37] is to prevent
the new model from deviating too far from the original initial
model, to avoid mode collapse, β  0 is the regularization
parameter is to control the deviation of the new model from
the reference model, as shown in Fig. 2 (c).
Among Equation (4) is intended to present a conceptual
formulation of the PPO optimization objective, rather than a
full description of all implementation details.
To explicitly characterize the optimization process, the PPO
objective can be expressed in its clipped surrogate form as
h

i
Lclip (θ) = Et min rt (θ)Ât , clip(rt (θ), 1 − , 1 + )Ât
(5)
where the probability ratio between the updated policy and the
reference policy is defined as
rt (θ) =

(7)

(6)

Task Requirements:: optical network logs are valuable
data resources generated by network devices and links during
operation, recording network activities, events, status changes,
and abnormal conditions. The logs can be used to track network behavior, monitor operational status, and ensure system
security [38]. Due to their high-frequency generation, log
analysis is significant for network status monitoring, fault diagnosis, and anomaly detection, supporting daily network O&M.
Therefore, fully leveraging optical network logs is essential
for supporting daily O&M, ensuring network stability, and
enhancing operational efficiency. In our previous work [26],
anomaly analysis of logs was achieved through supervised
fine-tuning of the LLaMA-2-7B-chat model using optical network log data, which effectively explained key information in
anomaly event descriptions and generated actionable insights.
The model’s performance was evaluated across three critical
dimensions: correctness, usability, and fluency. However, our
analysis revealed a significant limitation − the generated
content frequently exhibited inaccuracies that deviated from
the original log information. This highlights the need for more
effective fine-tuning techniques.

3660

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 3. The implementation process of the log analysis task based on RLHF consists of three stages. (a) Supervised Fine-Tuning: The base model is fine-tuned
on labeled log data to learn domain-specific patterns and anomaly detection capabilities. (b) Reward Modeling: Human feedback is collected by ranking
model-generated log analysis results, and a reward model is trained to predict these preference scores. (c) Policy Optimization: Using the PPO algorithm,
the model policy is optimized with guidance from the reward model, encouraging it to generate more accurate, informative, and human-aligned log analysis
outputs.

To address this issue, the RLHF is implemented to enhance
output precision. In addition, we further investigate LLM’s
application-specific requirements in optical network O&M scenarios. In general, the effectiveness of log analysis is directly
correlated with the comprehensiveness and level of detail in its
outputs. Therefore, we introduce additional preference designs,
firstly emphasizing two key aspects of content richness:
(1) clear and accessible analysis of log background, sources,
and content; (2) in-depth, multi-dimensional recommendations
for abnormal log resolution. Secondly, to enhance humanmachine interaction for network operators, the system’s
original direct expression style is transformed into a more
dynamic and flexible narrative form, thereby improving its
practicality in real-world operational scenarios. The implementation process of the verification comprises three main steps,
as shown in Fig. 3. In the first step, the model is fine-tuned on
log-labeled data via SFT. Next, multiple SFT models are used
to collect human preference data, based on which a reward
model is trained. In the final step, the reward model guides
the optimization of the SFT model through RL, resulting in a
preference-aligned model.

Human preference dataset: the first step in reward modeling is to construct a high-quality dataset of human preferences,
as shown in Fig. 3 (b). For the task requirements of log
analysis, we adopt the following process to collect human
preference datasets.
Firstly, we randomly sampled a subset of the SFT dataset
and processed it using various model baselines, which correspond to the different epochs of SFT training. In addition,
when the model generates sampling replies, we employ the
Diverse Beam Search decoding method [39] with a beam budget set to 4 and repeatability and diversity penalty parameters
both set to 1.5. This approach ensures diverse and high-quality
responses, and the higher the quality of the preference dataset,
the more advantageous it is for improving the accuracy of the
trained reward model.
Secondly, the collected responses were evaluated by domain
experts with the Zhongjin [40] annotation tool, following
a set of a unified set of criteria: accuracy, richness, and
interactivity. Manual improvements were applied to enhance
its interactivity, making the output more engaging and
informative.

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

3661

Thirdly, for each log analysis instance, only the top
four ranked responses were retained, with richness gradually
decreasing from the first to the fourth. The top three responses
were required to maintain both accuracy and interactivity,
whereas the fourth response was intentionally left with potential inaccuracies while retaining its original style. This design
choice was made to ensure that the constructed preference
pairs (chosen, rejected) differ clearly in at least one evaluation
metric, strengthening the consistency and reliability of the
preference signal.
By structuring the dataset in this way, this methodology
provides a robust foundation for training reward models,
emphasizing discernible differences in response quality. Such
an approach enhances the model’s ability to learn fine-grained
preferences, ultimately enhancing performance on log-analysis
tasks.
Model selection: during the SFT stage, to ensure continuity,
the same base model (LLaMA-2-7b-chat) is selected for study.
Subsequently, the trained LLM is then used as the initial policy
for the PPO.
For the reward model, instead of initializing it directly
from the base model, we choose to initialize it using an SFT
model during the reward modeling stage. Furthermore, to evaluate the performance of the reward model, we consider two
dimensions: 1) the static discriminative ability of the reward
model, which is mainly measured by calculating the preference
difference between the ‘chosen’ and ‘rejected’ responses in the
test set, that is r(x, ychosen ) − r(x, yrejected ). Specifically, it
includes two aspects: a) accuracy, the proportion of samples
with positive statistical reward differences. A higher proportion
indicates better accuracy in distinguishing good from poor
samples. b) Distinguishing strength, calculating the mean of
reward differences for all samples. The larger the mean, the
stronger the sensitivity and discriminative power of the model
to quality differences [41]. 2) The dynamic guidance ability
of the reward model, which mainly evaluates the actual effectiveness of the reward model in guiding policy optimization
in PPO training, as shown in Fig. 3 (c).

alarm sequence from the inherent network topology adjacency
matrix of physical links. The second step is to generate the
alarm event alarm propagation relationship adjacency matrix,
which needs to extract the alarm events appearing in the realtime alarm sequence from the inherent alarm events. The
third step is to use the matrices obtained above to construct
the alarm event propagation matrix, and the last step is to
use the alarm event propagation matrix to convert it into the
propagation relationship between the network element and the
alarm to determine the root alarm.
In our previous study, we fine-tuned four LLMs using CoT
data, with each model focusing on a specific step of the alarm
analysis process. To further improve task accuracy, the ReFT
technique is introduced in this work. The sequential workflow
of the verification is illustrated in Fig. 4.
RCL of alarm CoT data construction. Building a suitable CoT dataset can maximize the understanding of the
model and the learning of the algorithm. By utilizing the
powerful generation capability of LLM (GPT-4o) to generate
CoT data, the performance of small models (LLaMA-3-8BInstruct) in complex reasoning and step-by-step thinking can
be fully stimulated. Therefore, when generating datasets for
each task, as shown in Fig. 4 (a), experts first guide GPT-4o
to automatically generate CoT training data containing detailed
inference processes through fast engineering methods, and
then use topology information and alarm sequence information
in the real network to design appropriate instructions and input
information for each task, expanding the CoT data into a
training dataset in the form of {instruction, input, output} to
fine tune the small model (LLaMA-3-8B-Instruct).
Rule-based reward function: due to the relatively fixed
output format designed for each task in this study, it is often
only necessary to verify whether the result in the last inference
step of generating the response is consistent with the expected
result when verifying whether the output response is consistent
with the expected result.
Based on this feature, this study designed a rule-based
reward function to systematically evaluate the correctness
of generated responses. According to an analysis of outputs
produced by the alarm SFT baseline model, the generated
responses can be categorized into three types: (1) correct
alarm analysis obtained through reasonable logical reasoning,
(2) incorrect alarm analysis caused by flawed reasoning, and
(3) responses in which the reasoning process or final analysis
is incomplete. Correspondingly, reward values of 1.0, 0.1,
and 0.0 are assigned to these three cases, respectively, as
shown in Fig. 4(b). This hierarchical reward mechanism refines
the evaluation criteria for generation quality, strengthens the
model’s ability to generate correct responses, and enhances
robustness [42]. In addition, the asymmetric non-negative
reward design was adopted based on empirical observations of
training stability. Compared with symmetric reward structures
with negative penalties, which tend to produce predominantly negative advantages during early PPO training due
to the limited initial accuracy of the SFT model, the proposed reward scheme provides denser learning signals and
leads to more stable policy updates and improved training
efficiency.

B. Alarm Root Cause Localization Task Based on ReFT
Task requirements: in optical network O&M, alarms serve
as essential mechanisms for detecting and indicating network
faults or abnormalities. As network scale and complexity
grow, the volume of alarms generated during failures increases
significantly, with each device or link potentially triggering
alarms to signal potential issues and prompt operator intervention. The challenge lies not only in handling large volumes of
alarms but also in accurately identifying the true root-cause
alarms. Timely and precise RCL is critical for maintaining
network stability and ensuring continuous, reliable service
delivery. Based on the previous work [27], we collected the
real optical transport network (OTN) alarm data and leveraged
the relationship between network topology and alarm events to
fine-tune the LLM to achieve alarm root cause localization. We
divide the implementation into four steps based on the principle of root cause localization. The first step is to generate the
alarm event network topology adjacency matrix, which needs
to extract the network elements appearing in the real-time

3662

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 4. The implementation process of the root alarm localization task based on ReFT involves two stages. (a) Supervised Fine-Tuning: The base language
model is fine-tuned on labeled alarm data to capture domain-specific patterns. (b) Reward Modeling and Policy Optimization: Custom reward functions are
designed based on response feedback to evaluate the model’s outputs, and the model policy is then optimized using the PPO algorithm guided by these reward
functions to improve localization performance.

V. I MPLEMENTATION D ETAILS AND
E VALUATION M ETRICS
A. Log Analysis Task
1) Dataset: The dataset of network logs is collected from
a practical telecommunication network, which is composed of
both switch logs and OTN logs provided by the operator from
2023.10.31 to 2023.11.2. The number and content of switch
logs are rich and easy to obtain. Its addition provides more
abundant and effective training data, and its similar format and
syntax features help in analyzing optical network logs. Then,
the collected logs are annotated by domain experts, who refer
to technical manuals and other references to provide labels for
log parsing, anomaly detection and classification, and anomaly
analysis. The dataset used for log parsing, anomaly detection,
and classification consists of 4,975 records.
Since anomaly analysis aims at event-level reasoning rather
than long-term temporal trend modeling, one sample per
abnormal log template was retained to construct the fine-tuning
dataset for anomaly analysis. This approach ensures coverage
of diverse anomaly types and semantic patterns while avoiding
redundant normal-operation logs. The resulting dataset consists of 609 records, which is divided into a 90% training
set and a 10% testing set in the SFT stage. The short-term,
high-density nature of the dataset is conducive to capturing the

structural distribution and semantic characteristics of abnormal
events for model fine-tuning.
In addition, due to the stronger openness, subjectivity,
and diverse output space of log analysis tasks, RLHF can
effectively optimize the response quality of such open tasks.
However, log parsing and anomaly detection are high-certainty
tasks, and the benefits brought by RLHF are limited. Therefore, in this paper, we mainly focus on the study of log analysis
tasks.
In the reward modeling stage, the reward dataset comprises
1,800 comparison pairs. During training, 1,500 pairs were used
as the training set, while the remaining 300 pairs were reserved
for testing. Additionally, we collected 3,505 unlabeled data
samples from the optical network to construct the PPO dataset,
which does not require expert annotation and facilitates optimization iterations.
From a token-level perspective, the datasets used in the SFT,
reward modeling, and PPO stages exhibit moderate and wellcontrolled sequence lengths. In the SFT stage, each sample
consists of a fixed instruction (37 tokens), a templated log
input (7–72 tokens), and a fault analysis output (19–343
tokens), totaling approximately 66k training tokens and 6.3k
test tokens. The reward modeling stage includes 1,800 preference pairs with broader response-length distributions, resulting
in approximately 539k training tokens and 107k test tokens.

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

3663

For PPO training, 3,505 unannotated log samples with lengths
ranging from 61 to 205 tokens are used, contributing about
316k training tokens. All statistics are computed using the
LLaMA-2-7B-chat tokenizer.

B. Root Cause Localization Task
1) Dataset: We collected 296,134 alarm records from a
practical OTN over a period of 40 consecutive days and
extracted 4,430 fault-related records for verification. These
verification records include 378 single-root cause scenarios,
177 dual-root cause scenarios, and 76 triple-root cause scenarios. During the training phase, 400 fault scenarios were
randomly selected from a total of 631, while 50 scenarios were
used to evaluate each task during the testing phase. Then we
constructed 6,000 CoT training samples for each of the four
tasks involved in alarm localization, which were used in the
overall model training process.
From a token-level perspective, the datasets used in the
SFT and PPO stages exhibit moderate and well-controlled
sequence lengths across different tasks. In the SFT stage,
Task 1–4 samples consist of instructions (ranging from
45 to 747 tokens), inputs (12–957 tokens), and outputs
(116–2,062 tokens), resulting in total training tokens ranging
from approximately 68k to 290k and test tokens from 480
to 60k. For PPO training, prompts composed of instructions and inputs have lengths ranging from 185 to 784
tokens, contributing between 1.4M and 2.8M training tokens.
All statistics are computed using the LLaMA-3-8B-Instruct
tokenizer.
2) Hyperparameter Setting: In this study, the LLaMA38b-Instruct is used as our base model for fine-tuning. During
the training process, we developed a ReFT-based enhanced
model for four alarm tasks: topology relation extraction (Task
1), alarm propagation relation extraction (Task 2), alarm event
matrix generation (Task 3), and RCL of fault events (Task 4).
For the SFT pipeline, the LoRA attention dimension was
set to 8, with a scaling alpha parameter of 32 and a dropout
probability of 0.1 applied to the LoRA layers. The taskspecific hyperparameters included a batch size of 4, gradient
accumulation steps of 4, a learning rate of 1e-4, and a training
duration of 2 epochs.
In the policy optimization stage, all tasks were configured
with a batch size of 16 and a maximum generation length of
1024 tokens. Each batch underwent four PPO epochs, using
one minibatch per epoch. The remaining hyperparameters
were set as follows: Task 1 used 8 gradient accumulation
steps, a learning rate of 2e-6, and a β value of 0.1. Task
2 employed 4 gradient accumulation steps, a learning rate
of 2e-6, and a β value of 0.03. Task 3 adopted 8 gradient
accumulation steps, a higher learning rate of 5e-6, and a β
value of 0.15. Task 4 followed the same settings as Task 1,
with 8 gradient accumulation steps, a learning rate of 2e-6,
and a β value of 0.1. Among them, we evaluated β values
of 0.005, 0.01, 0.03, 0.05, 0.1, and 0.2, and observed that the
range 0.03–0.2 consistently yields stable performance, among
which the final values were selected in combination with other
PPO hyperparameters to ensure balanced policy stability and
reward dynamics.
The entire model fine-tuning process for the four alarm
localization tasks was performed using three NVIDIA H20
96GB GPUs.
3) Evaluation Metrics: To evaluate the performance of the
ReFT algorithm on this task, we adopted accuracy as the

2) Hyperparameter Setting: In this study, the LLaMA27b-chat is used as our base model for fine-tuning and the
optimal training parameters for the RLHF and SFT models
were determined through an iterative process of validation
and performance benchmarking. The Low-Rank Adaptation
(LoRA) [43] technique was used for fine-tuning throughout
the entire training process.
For the SFT baseline, the LoRA attention dimension was
set to 8, with a scaling alpha parameter of 32 and a dropout
probability of 0.1 applied to the LoRA layers. The taskspecific hyperparameters included a batch size of 4, gradient
accumulation steps of 4, a learning rate of 1e-4, and a training
duration of 3 epochs.
During the reward modeling phase, the batch size was
configured to 4, with gradient accumulation steps set to 2 and
a learning rate of 1e-5. The model was trained for 2 epochs,
resulting in a reward model optimally suited for the task. After
verification, this model achieved an accuracy of 95.33% on the
test set.
In the PPO phase, we adapted the implementation of relevant algorithms from the Transformer Reinforcement Learning
(TRL) framework [39]. The batch size was set to 16, with a
learning rate of 1.5e-5 and gradient accumulation steps of 8.
The maximum generation length was fixed at 512 tokens. Each
batch was trained over four PPO epochs, using one minibatch
per epoch. The KL divergence coefficient β was set to 0.1. The
model was trained for a total of 108 steps, and the checkpoint
achieving the best validation performance was selected for
subsequent analysis. All other hyperparameters were kept at
their default values.
The device used in this study is an NVIDIA H20 96GB
GPU. In the specific setup, both the SFT and reward modeling
stages are trained using a single GPU, while in the PPO training stage, dual GPU parallel computing is used to accelerate
the training process.
3) Evaluation Metrics: To evaluate the model’s performance, we introduced three key metrics: accuracy, interactivity, and richness. For each metric, experts assigned a score
ranging from 1 to 10 based on its definition and relevance to
the task requirements.
Accuracy: the generated output should accurately reflect
the log data, ensuring that analysis and recommendations are
correct, feasible, and logically sound. It must avoid irrelevant
or contradictory information and align with actual operational
needs.
Interactivity: the content should embody interactive design
principles, dynamically adjusting to user inputs and contextual
changes to provide personalized and practical responses.
Richness: while ensuring that all information is accurate and reliable, the log analysis should be thoroughly
detailed, providing as many relevant insights and feasible solutions as possible to support decision-making and operational
practicality.

3664

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 5. The results of PPO training in the RLHF-based log analysis task, including (a) the mean reward curve, (b) the KL divergence curve, (c) the value
loss curve, (d) the policy loss curve, (e) the total loss curve.

primary evaluation metric. For this indicator, the score will
be taken between 0-1.
Accuracy: measured by manually evaluating the consistency
between each inference step in the model-generated response
for each task and the corresponding reference answer. In this
evaluation, any errors in key characters or numerical values
are regarded as incorrect results.
VI. D EMONSTRATIONS AND R ESULTS
To validate the effectiveness of the proposed methodologies, this section conducts a comprehensive analysis of the
performance improvements in log analysis tasks implemented
through the RLHF method. In parallel, we evaluate the
improvement in the accuracy of CoT alarm tasks achieved
by adopting ReFT technology. Additionally, we explore the
influence of different reward models and PPO initial policies
on the overall performance of RLHF.
A. The Results of the Log Analysis Task Based on RLHF
In this section, we demonstrate the training of log analysis
tasks in the RLHF stage and the performance comparison with
the training in the SFT stage.
Firstly, the mean reward curve demonstrated a continuous
upward trend throughout the entire training process, as shown
in Fig. 5 (a). This indicates that the PPO algorithm effectively
optimizes the policy, resulting in higher rewards for LLM

in the task. The fluctuation of the curve reflects that the
model gradually achieves a balance between exploration and
exploitation under the guidance of the reward model. In
addition, the fluctuation of the KL divergence curve, as shown
in Fig. 5 (b), with a peak of about 20, indicates significant
differences between the new policy and the previous policy.
Given that our task requires a substantial deviation from the
initial policy while avoiding pattern collapse, this change in
the training curve is expected and considered acceptable.
In addition, to further illustrate the stability of PPO training, we report the evolution of key optimization metrics in
Fig. 5(c)–(e), which respectively present the value loss, policy
loss, and total loss during PPO updates. Despite the relatively small number of update steps, all three losses remain
within bounded and stable ranges throughout training, without
exhibiting monotonic increase, divergence, or collapse. Specifically, the value loss gradually decreases and oscillates within a
narrow interval, indicating stable fitting of the value function to
the advantage estimates. Meanwhile, the policy loss fluctuates
symmetrically around zero due to the clipped PPO objective,
reflecting normal stochastic policy updates without gradient
instability. The total loss remains well balanced, demonstrating effective coordination among policy optimization, value
learning, and entropy regularization.
As an enhanced version of the SFT model, the preference
model has achieved an accuracy improvement of 1.64 points
and a richness increase of 1.08 points compared to the SFT

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

3665

Fig. 6. Performance comparison between the SFT model and the preference
model in the RLHF-based log analysis task.

Fig. 8. Training loss curve of the SFT model during the RLHF-based log
analysis task.

Fig. 7. Response comparison between the SFT model and the RLHF model
in the RLHF-based log analysis task.

model. In addition, interactivity showed the most substantial
improvement, with an increase of 10 points, underscoring
the key role of RLHF training in enhancing user interaction.
This enhancement ensures that the model’s output aligns
more closely with human communication patterns, rather than
merely providing static answers, as shown in Fig. 6.
It is worth noting that an inherent trade-off exists between
richness and accuracy. The increase in richness means that
the generated log analysis outputs provide more detailed
background information, potential causes of anomalies, and
additional solutions, as shown in Fig. 7. This increase in
richness occasionally affects accuracy, as the model might
introduce speculative or irrelevant information, thereby affecting the overall reliability of the analysis.
To address this trade-off, RLHF uses reward modeling to
balance richness and accuracy. Specifically, during the PPO
training phase, the model learns human-annotation preferences
to expand the amount of information generated while maintaining the accuracy of key content. The evaluation results

indicate that although the richness increased by 1.02, it did
not significantly affect the overall improvement in accuracy.
This discovery indicates that the RLHF mechanism effectively
guides the model to generate more comprehensive outputs
while maintaining a high level of correctness.
In addition, to better understand these improvements, it
is essential to understand the differences between the two
training stages. In the log analysis task, the training data in
the SFT stage mainly focuses on identifying the root cause
of abnormal logs and providing direct solutions. Due to the
imitative nature of SFT training, the model outputs tend to
closely resemble the original labeled examples. However, by
combining preferences for accuracy, richness, and interactivity,
the performance of LLM can be further enhanced. In the
process of RL, the model effectively integrates human-labeled
data, its intrinsic abilities, and human preferences.
In summary, these results indicate that RLHF training
improved the accuracy score of LLM in log analysis tasks
from 7.45 to 9.09, richness from 6.18 points to 7.2 points, and
interactivity from 0 points to 10 points. This demonstrates that
RLHF enhanced the alignment between the model’s output and
human intent while mitigating the hallucination problem.
B. The Influence of Different Initial Policies Based on RLHF
In RLHF, the initial policy selection of the PPO algorithm
markedly influences the final model performance. To evaluate
its impact, we selected SFT models trained for 3, 6, and 10
epochs, respectively, as the initial policy for PPO under the
same training parameters. The corresponding SFT loss curves
are presented in Fig. 8 to highlight the differences among these
epochs.
Then, under the same reward model and PPO training
parameters, the three initial policies exhibited distinct behaviors. The policy trained for 3 epochs exhibited faster reward
growth and achieved a higher final return, whereas training
for 10 epochs resulted in slower reward improvement and a
lower final return, as shown in Fig. 9(a), suggesting potential
overfitting with increased training epochs. This pattern aligns
with the KL-divergence trend in Fig. 9 (b). The policy with

3666

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 9. Comparison of the following metrics during PPO training for log analysis tasks using different initial policies, i.e., SFT models trained for 3, 6, and
10 epochs: (a) mean reward, (b) KL divergence, (c) return, and (d) policy entropy.

an epoch of 3 shows a large and rapid policy adjustment (high
KL value), while the policy with an epoch of 10 shows smaller
fluctuations, reflecting greater stability.
To verify the above conclusion, we further analyzed the
variation curve of policy entropy, as shown in Fig. 9 (d). In
theory, entropy values more intuitively reflect the exploratory
nature of the policy. Higher entropy values indicate greater
output diversity, while a lower entropy value indicates a more
fixed output pattern. The results show that the initial policy
entropy decreases as the number of SFT epochs increases: it
is highest at epoch 3, lower at epoch 6, and lowest at epoch 10.
This suggests that extended SFT training leads to overfitting
on expert data and reduced exploratory behavior. The return
curves in Fig. 9 (c) support this observation: the initial policy
at epoch 3 achieves higher returns, while that at epoch 10
struggles to improve.
In addition, we evaluated the performance of different
initial policies and preference models trained through PPO
on the test set using specified evaluation metrics, as shown in
Fig. 10.
We first analyze the performance of SFT models with
different epochs on three indicators. The results shows that
accuracy improves with the increase of SFT epochs, while
richness shows a decreasing trend. This is because accuracy
measures the consistency between generated content and logs,

Fig. 10. Performance evaluation results of preference models based on
different initial policies (SFT models trained for 3, 6, and 10 epochs) and
training stages (SFT and PPO stages).

while richness, to some extent, evaluates the completeness of
the log background, reasons, and recommendations. As SFT
training deepens, the model tends to improve accuracy at the
cost of reducing richness. Because the SFT stage does not
incorporate interactivity, the interactivity score for all SFT
models is 0.

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

3667

Fig. 11. Training process comparison between initializing the reward model with the base model and initializing the reward model with the SFT model in
the RLHF-based log analysis task, including (a) accuracy curve. (b) training loss curve. (c) training global steps curve.

Secondly, by comparing the metrics of content generated
by the SFT model and the preference model, we can conclude
that regardless of the initial policy epoch of 3, 6, or 10, the
PPO-trained preference model outperforms the SFT model
in terms of generation quality, validating the effectiveness
of the method. However, there are significant differences
in the improvement of the different epoch models: when
epoch is 3, accuracy increase by 16.4%, richness increases by
10.2%, and interactivity increases by 100%; When epoch is 6,
accuracy increased by 9.1%, richness increased by 6.8%, and
interactivity increased by 16.4%; When epoch is 10, accuracy
increased by 10.9%, richness only increased by 2.5%, and
interactivity did not improve. These results further confirm that
models trained with fewer epochs possess greater plasticity
in PPO training, especially when significant adjustments are
needed. In this test, models trained for 3 epochs were able to
achieve more significant performance improvements.
To summarize, for domain adaptation, initializing PPO from
a lower-epoch SFT checkpoint yields higher RLHF returns
than using a higher-epoch SFT model, once basic domain
knowledge has been learned. This is because excessive SFT
training tends to overfit the model to static annotations, reducing policy entropy and limiting exploration during subsequent
PPO optimization, which leads to premature convergence.
C. The Influence of Different Reward Models Based on
RLHF
The prediction accuracy of the reward model plays a
pivotal role in determining the quality of the reward signal
during the PPO iteration process, thereby influencing both the
direction and effectiveness of policy updates. Consequently,
the performance of the reward model is a key factor in
successful preference alignment and in enhancing the overall
effectiveness of the PPO algorithm [44].
Moreover, downstream PPO training exhibits smooth
KL divergence growth and stable entropy instead of policy collapse, providing indirect evidence that the learned
reward signal is not overly specific to the training
preferences.
Based on these considerations, we further investigate the
selection strategy of the reward model from two perspectives:
1) Impact of Reward Model Initialization on Performance,
which compares initializing the reward model from a base
model (i.e., LLaMA-2-chat-7B) versus an SFT model; and

Fig. 12. Comparison of reward margins on the test set for reward models
initialized from the SFT model and the Base model in the RLHF-based log
analysis task.

2) Epoch Selection for SFT-Based Reward Models, which
examines how different training stages of the SFT model affect
downstream reward modeling performance.
1) Impact of Reward Model Initialization on Performance:
To ensure a fair comparison, we trained both the base and
SFT models under identical settings on the same preference
dataset and evaluated them at epoch 2. The training loss and
validation accuracy curves across 2 epochs are presented in
Fig. 11. Results indicate that, benefiting from prior fine-tuning
on log analysis tasks, the reward model initialized with the
SFT model achieves lower loss and higher accuracy in the
early training phase of training. As training progresses, it
consistently outperforms the reward model initialized from the
base model.
We first evaluated the accuracy of two reward models on
the test set, both of which were 95.3%, and presented their
margin distributions on the test set, as shown in Fig. 12.
The results show that the reward model initialized with the
SFT model exhibits a margin distribution concentrated in
higher value ranges compared to that initialized with the base
model. This indicates that SFT-based initialization improves
the model’s ability to distinguish between preferred and nonpreferred responses.

3668

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 13. Comparison of the following metrics for the reward model initialized with the base model versus the SFT model during PPO training in the
RLHF-based log analysis task: (a) mean reward, (b) KL divergence, (c) return, and (d) policy entropy.

Under the same PPO initial policy and parameters, the
first batch of data is usually generated by the initial policy,
so the initial generation is consistent. However, due to the
distinct scoring criteria of the two reward models, as shown in
Fig. 13 (a). The reward model initialized with the SFT
model applies stricter evaluation, leading to lower initial
rewards. Combined with the margin distribution findings, this
further confirms the base-initialized reward model’s weaker
discrimination. The KL divergence curve is steadier with
the base-initialized model, while the SFT-initialized model
triggers sharper adjustments, indicating more active policy
updates.
In addition, in the evaluation of the policy entropy curve,
as shown in Fig. 13 (d), it can be observed that under the
guidance of the reward model initialized with the base model,
the overall policy entropy shows a certain upward trend, while
under the guidance of the reward model initialized with the
SFT model, the policy entropy continues to decrease. This
phenomenon indicates that:
The reward model initialized with the base model demonstrates a stronger capacity for exploration guidance. In the
PPO training process, the observed increase in policy entropy
indicates that the policy distribution gradually becomes more
uniform, and the model retains a high degree of uncertainty for
various behaviors during the generation process, continuously
exploring the policy space. This phenomenon indicates that

the reward signal provided by the reward model initialized by
the base model is more diverse, failing to converge the policy
too quickly and instead encouraging diversity in the policy.
The reward model initialized with SFT model tends to
facilitate rapid policy convergence. The continuous decrease
in policy entropy means that the model gradually reduces
its exploration of different generative policies and begins to
focus on certain specific patterns or fixed expressions. This
is related to the language pattern preference introduced by
the reward model initialized with SFT during the SFT stage,
which causes the PPO algorithm to converge more quickly
toward deterministic decisions under the guidance of SFT
reward signals, narrowing the strategy space and decreasing
exploratory value.
However, based on the analysis of the final generated
content, although the reward model initialized with the base
model maintained a high policy entropy and obtained higher
mean rewards (as shown in Fig. 13 (a)) and returns (as shown
in Fig. 13 (d)), a pattern preference ending in ellipsis appeared,
as shown in Fig. 14, indicating that under the guidance of the
reward model initialized with the base model, a higher risk
of reward hacking [45], exchanging low-quality exploration
and generation for higher rewards. Under the guidance of
the reward model modeled by SFT, policies enable more
accurate and targeted policy adjustments to better suit human
preferences, as shown in Fig. 15.

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

Fig. 14. The final content generated by the preference model guided by the
reward model initialized with the base model in the RLHF-based log analysis
task.

Fig. 15. Comparison of the performance indicators of the final preference
models guided by reward models initialized from the SFT model and the Base
model in the RLHF-based log analysis task.

Fig. 16. Comparison of the reward margins on the test set for reward models
trained for different epochs (i.e., 2, 3, and 4 epochs) in the RLHF-based log
analysis task.

The reward model initialized with the SFT model is more
able to clarify the direction of human preference changes
compared to the reward model initialized with the Base model,
and can accurately guide during the PPO training process.
2) Epoch Selection for SFT-Based Reward Models: This
section investigates the impact of reward models at different
stages of training on the final preference model, with the SFT

3669

model used as the initial reward model. The training loss curve
of the specific reward model is shown in Fig. 11 (b). This study
selects reward models with training epochs of 2, 3, and 4 for
comparison, aiming to analyze the impact of training depth on
final performance. First, the reward margin metric on the test
set was used to compare the reward models from different
epochs in order to evaluate their discriminative ability. The
results are shown in Fig. 16.
We observe that as the training deepens, the reward margin
distribution on the test set gradually shifts toward higher
values, indicating an increasing preference for high-quality
samples and a trend toward stable, consistent scoring, as shown
in Fig. 17. Additionally, the reward models trained for 2, 3,
and 4 epochs achieve test set accuracies of 95.3%, 97.7%, and
97%, respectively.
Then, using the same PPO initial policy and PPO training
parameters, we obtained the PPO training curves, as shown
in Fig. 17. In the mean reward curve, the reward models at
epoch 2 and epoch 3 exhibit high consistency in guiding PPO
policy updates. Their initial and final convergence values are
relatively close. Combined with the evaluation of the final
generated metrics (seen in Fig. 18), this indicates that their
preferences are largely consistent.
In addition, the reward model at epoch 4 starts from a
lower initial value, indicating a stronger ability to differentiate
low-quality text, as shown in Fig. 17 (a). In early training
(before 80 steps), the reward curves of PPO policies guided
by all reward models were basically consistent. However, at
approximately 80 steps, the reward from the epoch-4 model
increased sharply, accompanied by a sharp increase in KL
divergence and a sharp decrease in policy entropy. The policy
gradually converged to a fixed-template generation mode, as
shown in Fig. 19, indicating that the reward model at epoch
4 was influenced by more extreme optimization objectives.
Moreover, during the evolution of policy entropy, although
there are fluctuations in the three curves, they all exhibit an
overall downward trend, which is consistent with the training
stability goal of PPO. It is worth noting that in the policy
entropy curve, the final entropy value under the epoch 2
configuration always falls between those of epoch 3 and epoch
4, indicating a non-monotonic pattern. Based on the evaluation
of the final generated indicators, as shown in Fig. 18, we
can conclude that under the guidance of the reward model
at epoch 3, the improvement in richness is better than that
of the reward model at epoch 2. The optimization objectives
during PPO training are more diverse, tending to generate
longer and more varied content. As a result, the final entropy
is slightly higher than that under epoch 2. However, in the
epoch 4 configuration, all responses in the test set ended with
“The first” and failed to generate complete outputs, resulting
in a lower final entropy value. Due to this result, the specific
evaluation of the preference model guided by the reward model
is not shown in Fig. 18.
Overall, as the training level of the reward model deepens,
the reward signal may become more comprehensive, but it
may also bring more extreme update signals. Therefore, the
selection of specific rounds still needs to be balanced based
on the evaluation indicators of different tasks.

3670

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 17. Comparison of PPO training performance under reward models from different training epochs (i.e., 2, 3, and 4 epochs) in the RLHF-based log
analysis task, showing: (a) mean reward, (b) KL divergence, (c) return, and (d) policy entropy curves.

Fig. 19. The final performance of the preference model guided by the reward
model at epoch 4 in the RLHF-based log analysis task.

Fig. 18. Comparison of the performance of the final preference models
guided by reward models at different epochs (i.e., 2, 3, and 4 epochs) in the
RLHF-based log analysis task.

D. Evaluation of SFT and RLHF on LLaMA-3-8B-Instruct
In the original analysis, LLaMA-2-7B-chat-hf was adopted
as the base model to construct the SFT and RL framework.
To further evaluate the generality of the proposed method
on stronger foundation models, additional analyses were conducted using LLaMA-3-8B-Instruct as the base model. In

these analyses, the same preference dataset and reward model
used in the previous analysis were retained to ensure a fair
comparison.
Specifically, PPO-based reinforcement learning optimization was performed on the LLaMA-3 model using the
constructed preference model as the reward signal. The training dynamics are illustrated in Fig. 20, which shows the
evolution of the KL divergence and the average reward score
during training. As shown in the figure, the mean reward
score increases steadily from negative values in the early
stage to stable positive values in later iterations, indicating

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

3671

Fig. 20. RLHF training dynamics with LLaMA-3: (a) mean reward curve; (b) KL divergence curve.

Fig. 21. Performance comparison between the LLaMA-SFT model and the
preference model.

that the policy gradually learns to generate responses that
better align with the preference model. Meanwhile, the KL
divergence remains within a controllable range throughout
the training process without exhibiting abrupt divergence or
collapse. Although moderate fluctuations occur due to the
stochastic nature of policy optimization, the overall trend
remains stable, demonstrating that the PPO training process
maintains a balanced trade-off between reward maximization
and policy constraint.
After RL optimization, the model was evaluated using three
qualitative metrics, namely Accuracy, Richness, and Interactivity, which assess the correctness of diagnostic conclusions, the
completeness of reasoning content, and the ability to provide
interactive explanations. The evaluation results are shown in
Fig. 21. The LLaMA-3-based SFT model achieves scores of
8.32, 7.05, and 4.63 on Accuracy, Richness, and Interactivity,
respectively. After applying preference-based reinforcement
learning, the optimized model improves to 9.48, 8.12, and
10.00 on the corresponding metrics. The corresponding results
using LLaMA-2 as the base model, shown in Fig. 6, are
slightly lower across all three metrics. These results suggest
that a stronger base model can improve diagnostic accuracy,
while RL further enhances reasoning richness and interactivity.

In addition, a representative generation example is presented in Fig. 22 to illustrate the qualitative improvements
introduced by the preference optimization. Compared with
the SFT model, the RLHF-optimized model provides more
precise explanations for logging events and clearer guidance
for troubleshooting. While the SFT output only offers a general
description of RSPAN (Remote Switched Port Analyzer) or
mirror configuration issues and suggests checking the configuration, the RLHF output specifies potential causes, such as
incorrect mirror settings or software bugs. It also provides
actionable steps, including verifying and reconfiguring the
mirror session, upgrading firmware if necessary. Furthermore,
the RLHF output encourages follow-up interaction, which
aligns better with human preferences.
In summary, compared with LLaMA-2, LLaMA-3 achieves
higher scores across all evaluation metrics, confirming that a
stronger base model generally improves performance. However, additional studies show that, despite its strong general
language capabilities, LLaMA-3 still faces domain-specific
challenges, such as accurately handling specialized knowledge
and reasoning within the optical network domain. Applying
RLHF in this context still effectively enhances the model’s
alignment with the preference dataset and improves taskspecific reasoning performance.
E. The Results of the Alarm Task Based on ReFT
In this section, we evaluate the effectiveness of the proposed
method across four distinct alarm tasks by independently
training a model for each of the four tasks and recording the
variations in mean reward and KL divergence during training,
as shown in Fig. 23.
Overall, the results demonstrate consistent and stable training behavior across all tasks. In Task 1, the mean reward
showed noticeable fluctuations in the early phase but gradually
increased and stabilized around 0.8, while the KL divergence
first rose and then declined, indicating active exploration
followed by convergence to a stable policy. In Task 2, the
mean reward remained at a relatively high and stable level
throughout training, suggesting that the model was able to
acquire an effective policy early on. The KL divergence in

3672

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 22. Comparison of generated responses of the SFT model and the
preference-optimized model.

this task increased moderately during the initial phase, reached
a peak around mid-training, and subsequently decreased to a
stable level, reflecting effective control over policy shifts.
Similar trends were observed for tasks 3 and 4. In Task
3, the mean reward steadily increased with slight fluctuations
before stabilizing above 0.9, while the KL divergence fluctuated greatly throughout the training process and eventually
stabilized at a lower value. In Task 4, the mean reward
also showed a gradual upward trend, with fluctuations in
early training gradually smoothing out. The KL divergence
followed a pattern of initial increase, reaching a mid-training
peak before decreasing to a lower, stable level. These results
collectively suggest that the proposed method can maintain
a balance between reward maximization and policy stability
across varied task settings, validating its generalization capability and robustness.
In addition, we introduce accuracy indicators to evaluate the
performance of domain-adapted LLM in alarm analysis tasks.
Considering the strict requirements for fault tolerance in alarm
tasks, only when the model output is completely consistent
with the ground truth, it is considered correct during manual
evaluation. In this evaluation, any errors in key characters or
numerical values are regarded as incorrect results.
The accuracy for all four tasks improves steadily across
the two training stages, as shown in Fig. 24. The SFT model
achieved an accuracy rate of 86% to 96% on four tasks, but
there is still an accuracy bottleneck. The ReFT can further
improve performance for all four tasks (accuracies >96%),
especially in task 2, extracting fault event alarm propagation
relationships, and task 3, generating fault event adjacency
matrices, with an accuracy rate of 99%, providing strong
support for the landing application of LLMs in alarm analysis
scenarios.
In terms of improvements in content generation, since the
tasks share common issues and enhancements, we take Task 4
as a representative case for detailed analysis. In the SFT stage,
the response of the model to alarm analysis tasks mainly manifests as two problems: incomplete content generation, where
some responses only include partial reasoning steps or analysis

conclusions, and fail to fully cover the entire reasoning process
and final conclusions; the reasoning errors in the reasoning
steps and processes, such as incorrect logical deduction, matrix
generation, and incorrect RCL results, as shown in Fig. 25.
In contrast, after entering the ReFT stage, the responses of
model not only achieved more complete and coherent content
generation, but also effectively corrected logical errors within
the reasoning process, even when supervision was applied
solely to the final results. This ultimately led to a significant
improvement in the overall accuracy and reliability of the
model’s responses. This phenomenon can be attributed to the
implicit alignment effect of RLHF, where models are guided
to generate reasoning chains that are more likely to lead to
correct final outcomes.
The tasks have been successfully improved through the
implementation of ReFT technology, which further indicates
that in RL-based fine-tuning, although only the correctness of the final analysis results is directly supervised,
the reward function implicitly encourages the generation of
logically reasonable and human-preferred intermediate reasoning steps. Through iterative reward-guided optimization,
the model gradually learns to generate inference processes
that conform to expected patterns, as incorrect intermediate
steps often result in lower rewards due to incorrect final
outcomes.
In summary, the demonstration results indicate that ReFT
training substantially enhanced the performance of the LLM in
alarm tasks, with accuracy improvements from 96% to 98%
for Task 1, 86% to 99% for Task 2, 94% to 99% for Task
3, and 90% to 96% for Task 4. These findings validate the
effectiveness of the ReFT-enhanced LLM for alarm analysis
and demonstrate its promising potential for the development of
specialized LLMs in future automatic optical network systems.
F. ReFT Training Based on Multi-Task Mixture
Although the above studies design task-specific reward
functions for individual tasks, this does not imply that the
proposed approach is limited to single-task fine-tuning. In
fact, the same framework can be naturally extended to multitask scenarios. To demonstrate this capability, we conduct an
additional study in which the four subtasks involved in the
root alarm localization problem are jointly incorporated into a
unified reinforcement fine-tuning process.
Specifically, during the SFT stage, data from the four related
tasks are combined to form a joint training set for supervised
fine-tuning. During reward construction, task-specific reward
functions are integrated into a unified reward framework,
with the applied reward determined by the task context of
each sample. In the reinforcement fine-tuning stage, rather
than fully merging PPO datasets across tasks, we sample
6,000 mixed instances according to a fixed ratio of Task 1:
Task 2: Task 3: Task 4 = 1:1:1:3. The total number of
training instances is fixed to 6,000 to balance training stability
and computational efficiency, while ensuring sufficient task
diversity for effective reinforcement learning.
The training dynamics of the mixed multi-task ReFT process are illustrated, as shown in Fig. 26. The mean reward
exhibits a clear upward trend and gradually stabilizes after

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

3673

Fig. 23. Mean reward curve and KL divergence curve during the PPO optimization process for (a) Task-1, (b) Task-2, (c) Task-3, and (d) Task-4 in the
ReFT-based alarm task.

Fig. 24. Comparison of accuracy between the SFT model and the
ReFT-enhanced model.

This behavior implies that the PPO updates effectively balance
exploration and policy regularization, preventing excessive
deviation from the pretrained distribution while still enabling
meaningful policy improvement. The smooth decay of KL
divergence also indicates the absence of policy collapse, even
when multiple task-specific rewards are jointly optimized.
In addition, it can be observed that the used ReFT
framework consistently improves performance across all four
subtasks compared with the SFT-only baseline as shown in
Fig. 27. Specifically, ReFT yields absolute accuracy gains of
2%, 6%, 13%, and 6% on Task 1–Task 4, respectively. Notably,
the improvement is more pronounced on Task 3 and Task
2, which involve higher reasoning complexity and stronger
dependency on contextual alarm semantics. This indicates that
the unified reward-driven optimization can effectively enhance
the model’s decision boundaries beyond what is achievable
through supervised learning alone.

approximately 60 steps, indicating that the policy consistently
aligns better with the integrated reward objectives across
different tasks, as shown in Fig. 26 (a). Despite the inherent
heterogeneity among subtasks, no oscillatory or divergent
behavior is observed, suggesting that the mixed-task training
strategy remai ns stable under the proposed sampling scheme.
Meanwhile, the KL divergence between the updated policy
and the reference model decreases steadily and remains within
a controlled range throughout training as shown in Fig. 26 (b).

Overall, these results demonstrate that the proposed framework can successfully generalize from single-task to multitask reinforcement fine-tuning. By integrating task-aware
reward functions and carefully controlling the mixed-task
sampling ratio, the model not only achieves consistent accuracy improvements across all subtasks but also maintains
stable and interpretable training dynamics. This confirms the
practicality of the proposed approach for complex real-world
alarm analysis scenarios involving multiple interrelated tasks.

3674

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 25. Performance improvements of the ReFT enhanced model compared with the SFT model, illustrated using Task 4 as an example.

Fig. 26. Training process of Mixed Multi-Task ReFT: (a) the mean reward curve, (b) the KL divergence curve.

G. Retrieval-Augmented Baselines and Task-Specific
Performance Analysis
To quantitatively evaluate the effectiveness of RL-based
fine-tuning, we compare the proposed RLHF–ReFT framework with strong non-RL baselines on two representative
tasks: log analysis and alarm localization. All models are
evaluated using the same backbone LLM, identical training
and test splits, and consistent inference settings to ensure a fair
comparison. The baselines include supervised fine-tuning with
carefully designed task-specific prompts (SFT), supervised
fine-tuning augmented with retrieval-augmented generation
[20] (SFT+RAG), and the proposed RLHF–ReFT framework.
For the RAG-based baseline, semantically similar historical
cases are retrieved and appended to the input context without
introducing explicit causal or structural constraints.

1) Log Analysis Task: Prompt-engineered SFT already provides a strong baseline for the log analysis task, indicating that
careful prompt design can effectively guide the model toward
correct interpretation of log semantics, as shown in Fig. 28.
Incorporating retrieval further improves factual accuracy, as
SFT+RAG benefits from direct exposure to relevant historical
cases.
However, both SFT and SFT+RAG exhibit limited improvements in response richness and interactivity. This suggests
that while supervised objectives and retrieval mechanisms
can enhance surface-level correctness, they are less effective
in consistently enforcing structured reasoning processes and
professional diagnostic behaviors. In contrast, the RLHF-based
model achieves the best performance across all evaluation
metrics. By explicitly optimizing task-level reward signals

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

3675

Fig. 27. Comparison of Accuracy Between the SFT Model and the
ReFT-Enhanced Model During Mixed Training.

high root cause localization accuracy, the SFT+RAG baseline suffers a substantial performance drop, despite retrieving
semantically similar alarm cases. This counterintuitive result
indicates that naı̈ve retrieval based on semantic similarity
may introduce misleading correlations, causing the model to
confuse root alarms with downstream or chain alarms.
Cause localization inherently requires reasoning over causal
propagation and structural dependencies, rather than surfacelevel semantic similarity. Retrieved examples that are textually
similar but structurally irrelevant may bias the model
toward incorrect inference paths. In contrast, the proposed
RLHF–ReFT framework achieves the highest accuracy, suggesting that RL-based fine-tuning is better suited for capturing
causal and propagation relationships by directly optimizing
task-specific correctness signals.
Importantly, these results do not suggest that retrievalaugmented generation is ineffective in general. Instead, they
highlight that RAG is not well-suited for alarm localization
tasks when retrieval lacks causal or topological constraints,
whereas RL-based fine-tuning provides a more appropriate
alignment mechanism for such reasoning-intensive scenarios.
Overall, these quantitative results demonstrate that prompt
engineering and RAG can serve as useful auxiliary techniques, particularly for log analysis tasks. However, they are
insufficient on their own for aligning model behavior with
domain-specific reasoning and decision-making requirements
across tasks. By explicitly optimizing task-level reward signals, RL-based fine-tuning encourages valid reasoning paths
while suppressing spurious patterns introduced by retrieved
cases, leading to more robust and reliable performance.

Fig. 28. Comparison of SFT, RAG, and RLHF Results of Log task.

Fig. 29. Comparison of SFT, RAG, and ReFT Results of Alarm task.

that encode correctness, reasoning quality, and response style,
RLHF–ReFT enables more effective alignment with domainspecific decision criteria, resulting in more informative and
interactive outputs.
2) Root Cause Localization Task: A different and more
revealing trend is observed in the alarm localization task, as
shown in Fig. 29. While the SFT (Prompt) model attains

VII. D ISCUSSION AND F UTURE W ORK
Although the results demonstrate the effectiveness and engineering feasibility of RL-based fine-tuning in optical network
O&M scenarios, it is also important to situate these findings
within the broader landscape of existing AI-based O&M solutions and to discuss remaining limitations and future research
directions.
Traditional AI-based O&M solutions, such as knowledge
graph systems and deep learning classifiers, typically rely
on predefined rules, structured schemas, or fixed feature
representations [46]. While these methods perform well on
common and well-defined fault patterns, they often struggle to generalize to heterogeneous log formats and long-tail
or previously unseen faults, which are prevalent in realworld optical network environments. In contrast, LLM-based
approaches can directly process raw or semi-structured logs
and perform semantic understanding and reasoning [21], [47],
enabling more robust fault diagnosis and root-cause analysis
under complex and uncertain conditions. This fundamental
difference partly explains the empirical advantages observed
in our studies.
Beyond diagnostic accuracy, LLM-based O&M approaches
also provide unique benefits in terms of human–machine
interaction and system adaptability. By supporting natural
language–based, human-in-the-loop analysis, LLMs allow
operators to iteratively refine diagnostic results and better align

3676

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

TABLE I
C OMPARISON OF LLM S AND T RADITIONAL O&M M ETHODS

model behavior with real operational workflows [48]. Moreover, LLMs significantly reduce adaptation costs in dynamic
network environments where concept drift and cold-start issues
are common by enabling prompt-level adaptation or few-shot
learning [49], rather than requiring costly retraining or manual
knowledge graph updates. These properties make LLM-based
solutions more practical and scalable for evolving optical
networks.
Despite these advantages, several limitations remain and
motivate future research.
A. Data Dependency and Generalization
The framework relies on high-quality human preference data
for RLHF and large-scale structured alarm data for ReFT, both
of which require substantial expert involvement for annotation
or validation. This data dependency may limit scalability and
rapid adaptation in scenarios with scarce labeled data. Future
work will explore weakly supervised or semi-automatic preference construction methods, such as leveraging structural log
features, historical remediation records, or rule-based systems.
In addition, transfer learning and cross-scenario data reuse
strategies may further enhance model generalization across
heterogeneous network environments.

B. Computational Overhead and Deployment Scalability
RLHF and ReFT introduce higher computational costs than
supervised fine-tuning due to reward modeling and PPObased optimization. While sufficient GPU resources were
available in this study, frequent RL-based updates may
be impractical in resource-constrained or latency-sensitive
deployment environments. Future research may focus on
lightweight RL fine-tuning strategies, including reduced PPO
update frequency, partial parameter freezing, and localized
policy optimization. Combining parameter-efficient fine-tuning
(PRFT) with reward distillation or offline RL paradigms may
also improve deployment scalability.
C. Task Coverage and Method Generality
The proposed framework is validated on two representative
tasks, log analysis and alar root cause localization, with taskspecific reward designs and reasoning workflows. Extending
the framework to more complex O&M scenarios, such as QoT
estimation or multi-root-cause fault analysis [50], may require
additional reward and hyperparameter tuning. Future work will
investigate task-aware and hierarchical reward designs, as well
as multi-task RL fine-tuning strategies, to improve adaptability
and generality across diverse optical network tasks.

LIU et al.: DEVELOPING A DOMAIN-SPECIFIC LLM FOR OPTICAL NETWORKS

To help readers quickly understand the strengths and weaknesses of different approaches, we have summarized the above
analysis in Table I. This table presents the applicability, performance, and limitations of traditional AI-based O&M methods
and RL-based fine-tuning approaches in optical network log
analysis and alarm localization tasks, providing an intuitive
reference for subsequent discussion and method selection.
Beyond the limitations discussed above, reinforcement
learning techniques for large language models are evolving
rapidly. In this work, reinforcement fine-tuning is implemented
using PPO, as it has been widely adopted in early RLHF
and ReFT frameworks and serves as a standard optimization
approach in LLM alignment studies. This choice ensures
methodological consistency with prior work. Nevertheless,
recent studies have also proposed new reinforcement optimization methods, such as Group Relative Policy Optimization
(GRPO) [51]. Future work will investigate the applicability of
these emerging methods in optical network O&M scenarios,
as well as explore more scalable reward construction mechanisms to further enhance the practicality of LLM-based O&M
systems.
VIII. C ONCLUSION
This paper proposes a domain-adaptation methodology in
which existing RLHF and ReFT techniques are employed to
fine-tune LLMs, enabling them to perform optical network
O&M tasks effectively. Taking log analysis and alarm localization, two key tasks in optical network O&M, as examples, the
implementation details of RLHF and ReFT were analyzed, and
the final task performance was evaluated. The results showed
that after RLHF fine-tuning, the consistency between log analysis tasks and expert intentions was significantly improved,
with an accuracy score above 9 and an interactivity score above
10. Although the richness score was slightly lower, it still
outperformed that of supervised fine-tuning. For alarm-related
tasks, the minimum accuracy also reaches 96%. In addition,
we also analyzed and evaluated the selection of initial policies
in the PPO stage and the selection of reward models involved
in the implementation details of RLHF. These studies were
based on specific task requirements and had certain limitations.
Future work can include a more comprehensive analysis by
incorporating additional evaluation metrics. We hope that
this method of strengthening and fine-tuning LLMs can contribute to the professionalization of LLMs in a specialized
domain.
ACKNOWLEDGMENT
The authors would like to thank China Telecom for providing the operational data used in this study. They also sincerely
appreciate the valuable guidance and insights from senior
experts, which were instrumental to this work.
R EFERENCES
[1]

D. Wang, Y. Wang, X. Jiang, Y. Zhang, Y. Pang, and M. Zhang,
“When large language models meet optical networks: Paving the way
for automation,” Electronics, vol. 13, no. 13, p. 2529, Jun. 2024.

3677

[2]

D. Wang, C. Zhang, W. Chen, H. Yang, M. Zhang, and A. P. T. Lau,
“A review of machine learning-based failure management in optical
networks,” Sci. China Inf. Sci., vol. 65, no. 11, Nov. 2022, Art. no.
211302.
[3] P. Jing, Y. Han, J. Sun, T. Lin, and Y. Hu, “AutoRoot: A novel fault
localization schema of multi-dimensional root causes,” in Proc. IEEE
Wireless Commun. Netw. Conf. (WCNC), Mar./Apr. 2021, pp. 1–7.
[4] Y. Meng et al., “Localizing failure root causes in a microservice through
causality inference,” in Proc. IEEE/ACM 28th Int. Symp. Quality Service
(IWQoS), Jun. 2020, pp. 1–10.
[5] OpenAI. ChatGPT. Accessed: Jun. 9, 2025. [Online]. Available: https://
openai.com/blog/chatgpt
[6] H. Touvron et al., “Llama 2: Open foundation and fine-tuned chat
models,” 2023, arXiv:2307.09288.
[7] A. Grattafiori et al., “The llama 3 herd of models,” 2024,
arXiv:2407.21783.
[8] J. Yang et al., “Harnessing the power of LLMs in practice: A survey on
ChatGPT and beyond,” ACM Trans. Knowl. Discovery Data, vol. 18,
no. 6, pp. 1–32, Jul. 2024.
[9] J. Lu, L. Yu, X. Li, L. Yang, and C. Zuo, “LLaMA-reviewer: Advancing
code review automation with large language models through parameterefficient fine-tuning,” IEEE Trans. Softw. Reliab. Eng., vol. 34, no. 10,
pp. 647–658, Oct. 2023.
[10] Y. A. Farrukh, S. Wali, I. Khan, and N. D. Bastian, “XG-NID: Dualmodality network intrusion detection using a heterogeneous graph neural
network and large language model,” Expert Syst. Appl., vol. 287, Aug.
2025, Art. no. 128089.
[11] Y. Song et al., “Synergistic interplay of large language model and digital
twin for autonomous optical networks: Field demonstrations,” IEEE
Commun. Mag., vol. 63, no. 6, pp. 90–96, Jun. 2025.
[12] X. Jiang et al., “OptiComm-GPT: A GPT-based versatile research
assistant for optical fiber communication systems,” Opt. Exp., vol. 32,
no. 12, pp. 20776–20796, Jun. 2024.
[13] R. Vilalta et al., “Applying digital twins to optical networks with
cloud-native SDN controllers,” IEEE Commun. Mag., vol. 61, no. 12,
pp. 128–134, Dec. 2023.
[14] N. Di Cicco, M. Ibrahimi, S. Troia, F. Musumeci, and M. Tornatore,
“Open implementation of a large language model pipeline for automated
configuration of software-defined optical networks,” in Proc. 50th Eur.
Conf. Opt. Commun. (ECOC), Sep. 2024, pp. 1591–1594.
[15] Y. Zhang et al., “Generative AI-driven hierarchical multi-agent framework for zero-touch optical networks,” IEEE Commun. Mag., vol. 64,
no. 1, pp. 24–31, Jan. 2026.
[16] C. Wang, N. Yoshikane, C. Zhang, Y. Wakayama, D. Soma, and
T. Tsuritani, “LLM-centric transport network configuration management
framework and demonstration,” in Proc. Opt. Fiber Commun. Conf.
(OFC), 2025, p. M3A.4.
[17] A. Afzal, J. Vladika, D. Braun, and F. Matthes, “Challenges in domainspecific abstractive summarization and how to overcome them,” 2023,
arXiv:2307.00963.
[18] O. Macmillan-Scott and M. Musolesi, “(Ir)rationality and cognitive
biases in large language models,” Roy. Soc. Open Sci., vol. 11, no. 6,
Jun. 2024, Art. no. 240255.
[19] C. Ling et al., “Domain specialization as the key to make large language
models disruptive: A comprehensive survey,” 2023, arXiv:2305.18703.
[20] P. Lewis et al., “Retrieval-augmented generation for knowledge-intensive
NLP tasks,” in Proc. Adv. Neural Inf. Process. Syst., vol. 33, 2020,
pp. 9459–9474.
[21] T. B. Brown et al., “Language models are few-shot learners,” in Proc.
NIPS, 2020, pp. 1877–1901.
[22] A. Radford, K. Narasimhan, T. Salimans, and I. Sutskever, “Improving
language understanding by generative pre-training,” OpenAI, San Francisco, CA, USA, Tech. Rep., 2018.
[23] Y. Gao et al., “Retrieval-augmented generation for large language
models: A survey,” 2023, arXiv:2312.10997.
[24] I. Beltagy, M. E. Peters, and A. Cohan, “Longformer: The longdocument transformer,” 2020, arXiv:2004.05150.
[25] S. Zhang et al., “Instruction tuning for large language models: A survey,”
2023, arXiv:2308.10792.
[26] Y. Pang et al., “Large language model-based optical network log analysis
using LLaMA2 with instruction tuning,” J. Opt. Commun. Netw., vol. 16,
no. 11, pp. 1116–1132, Nov. 2024, doi: 10.1364/jocn.527874.
[27] Y. Wang et al., “Graph structure-enhanced large language model for optical network fault diagnosis: An explainable alarm root cause localization
approach,” IEEE Internet Things J., vol. 12, no. 15, pp. 31493–31510,
Aug. 2025, doi: 10.1109/JIOT.2025.3573056.

3678

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

[28] D. Guo et al., “DeepSeek-r1: Incentivizing reasoning capability in LLMs
via reinforcement learning,” 2025, arXiv:2501.12948.
[29] T. Kaufmann, P. Weng, V. Bengs, and E. Hüllermeier, “A survey of
reinforcement learning from human feedback,” 2023, arXiv:2312.14925.
[30] L. Ouyang et al., “Training language models to follow instructions with
human feedback,” in Proc. Adv. Neural Inf. Process. Syst. (NIPS), 2022,
pp. 27730–27744.
[31] Z. Sun et al., “Aligning large multimodal models with factually augmented RLHF,” 2023, arXiv:2309.14525.
[32] L. Wang et al., “Parameter-efficient fine-tuning in large language models:
A survey of methodologies,” Artif. Intell. Rev., vol. 58, no. 8, p. 227,
May 2025.
[33] Z. Chen, Y. Deng, H. Yuan, K. Ji, and Q. Gu, “Self-play fine-tuning
converts weak language models to strong language models,” 2024,
arXiv:2401.01335.
[34] N. Stiennon et al., “Learning to summarize with human
feedback,” in Proc. Adv. Neural Inf. Process. Syst., vol. 33, 2020,
pp. 3008–3021.
[35] R. A. Bradley and M. E. Terry, “Rank analysis of incomplete block
designs: I. the method of paired comparisons,” Biometrika, vol. 39,
no. 3/4, pp. 324–345, Dec. 1952.
[36] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov,
“Proximal policy optimization algorithms,” 2017, arXiv:1707.06347.
[37] S. Kullback and R. A. Leibler, “On information and sufficiency,” Ann.
Math. Statist., vol. 22, no. 1, pp. 79–86, 1951.
[38] L. Velasco et al., “Monitoring and data analytics for optical networking:
Benefits, architectures, and use cases,” IEEE Netw., vol. 33, no. 6,
pp. 100–108, Nov. 2019.
[39] L. von Werra et al. (2020). TRL: Transformer Reinforcement Learning.
[Online]. Available: https://github.com/huggingface/trl
[40] S. Yang et al., “Zhongjing: Enhancing the Chinese medical capabilities
of large language model through expert feedback and real-world multiturn dialogue,” in Proc. AAAI Conf. Artif. Intell., vol. 38, no. 17,
pp. 19368–19376, Mar. 2024.
[41] B. Qin, D. Feng, and X. Yang, “Towards understanding the influence of reward margin on preference model performance,” 2024,
arXiv:2404.04932.
[42] M. Riedmiller et al., “Learning by playing solving sparse reward tasks
from scratch,” in Proc. 35th Int. Conf. Mach. Learn. (ICML), 2018,
pp. 4344–4353.
[43] E. J. Hu et al., “LoRa: Low-rank adaptation of large language models,”
in Proc. ICLR, 2022, vol. 1, no. 2, p. 3.
[44] B. Wang et al., “Secrets of RLHF in large language models Part II:
Reward modeling,” 2024, arXiv:2401.06080.
[45] L. Gao, J. Schulman, and J. Hilton, “Scaling laws for reward
model overoptimization,” in Proc. Int. Conf. Mach. Learn., vol. 2023,
pp. 10835–10866.
[46] A. Hogan et al., “Knowledge graphs,” ACM Comput. Surv., vol. 54,
no. 4, pp. 1–37, 2021.
[47] M. Bosma et al., “Chain-of-thought prompting elicits reasoning in large
language models,” in Proc. Adv. Neural Inf. Process. Syst., vol. 35, 2022,
pp. 24824–24837.
[48] S. Amershi et al., “Guidelines for human-AI interaction,” AI Mag.,
vol. 40, no. 4, pp. 3–15, Dec. 2019.
[49] P. Liu, W. Yuan, J. Fu, Z. Jiang, H. Hayashi, and G. Neubig, “Pretrain, prompt, and predict: A systematic survey of prompting methods
in natural language processing,” ACM Comput. Surv., vol. 55, no. 9,
pp. 1–35, Sep. 2023.
[50] J. Mata et al., “Artificial intelligence (AI) methods in optical networks: A
comprehensive survey,” Opt. Switching Netw., vol. 28, pp. 43–57, Apr.
2018.
[51] Z. Shao et al., “DeepSeekMath: Pushing the limits of mathematical
reasoning in open language models,” 2024, arXiv:2402.03300.

Yanli Liu is currently pursuing the M.S. degree with Beijing University
of Posts and Telecommunications, Beijing, China. Her research interests
focus on domain-adaptive large language models, optical communications,
and networking.

Yue Pang received the Ph.D. degree from Beijing University of Posts and
Telecommunications (BUPT) in 2025. She is currently with China Telecom,
where her work focuses on network large models and agents. Her research
interests include LLM, digital twin, and optical networks.

Yidi Wang (Graduate Student Member, IEEE) is currently pursuing the Ph.D.
degree with Beijing University of Posts and Telecommunications, Beijing,
China. His research interests include automated operation and maintenance of
optical transport network, intelligent fault analysis, digital twin, and generative
AI.

Shengnan Li received the M.S. degree from Beijing University of Posts
and Telecommunications (BUPT), Beijing, China, in 2022. He is currently
pursuing the Ph.D. degree with the School of Electronic Engineering, BUPT.
His research interests focus on optical performance monitoring, digital twin of
optical networks, and AI Agents for intelligent optical network management.

Jin Li received the Ph.D. degree from Beijing University of Posts and
Telecommunications (BUPT), Beijing, China, in 2020. He was a Researcher
with Purple Mountain Laboratories, Nanjing, China, from 2020 to 2022. He
was a Post-Doctoral Researcher with the Institute of Information Photonics
and Optical Communications, BUPT, from 2022 to 2025. He is currently a
Researcher with School of Optoelectronic Science and Engineering, South
China Normal University, Guangzhou, China. His research interests include
network slicing, fixed-mobile convergence networks, and LEO satellite networks.

Min Zhang received the Ph.D. degree in optical communications from
Beijing University of Posts and Telecommunications (BUPT), China. He
is currently a Professor with BUPT, the Deputy Director of the Sate Key
Laboratory of Information Photonics and Optical Communications, and the
Deputy Dean of the School of Optoelectronic Information. He holds 45
China patents. He has authored or co-authored more than 300 technical
papers in international journals and conferences, and 12 books in the areas
of optical communications. His current research interests include optical
communication systems and networks, optical signal processing, and optical
wireless communications.

Danshi Wang (Senior Member, IEEE) received the Ph.D. degree in electromagnetic field and microwave technology from Beijing University of Posts
and Telecommunications (BUPT), in 2016. He is currently a Professor with
the State Key Laboratory of Information Photonics and Optical Communications (IPOC), BUPT. He has proposed and verified a series of AI-driven
communication and network technology solutions, which has been applied
in telecom operator and internet service provider. He has authored or coauthored over 200 technical papers in international journals and conference,
including invited talks in ECOC/OFC. He has held and participated in multiple
funded research grants, including the National Key Research and Development
Program of China, the National Natural Science Foundation of China, and
the Fundamental Research Funds for the Central Universities. His research
interests include intelligent communications and networks, semantic optical
communications, digital twin networks, and AI for science.
PAPER_TEXT
