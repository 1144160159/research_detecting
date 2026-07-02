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
# [567] TrafficLLM: Enhancing Large Language Models for Network Traffic Analysis with Generic Traffic Representation
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
编号：567
题名：TrafficLLM: Enhancing Large Language Models for Network Traffic Analysis with Generic Traffic Representation
年份：2025
DOI：10.48550/arXiv.2504.04222
来源：arXiv preprint
PDF：paper/10.48550_arXiv.2504.04222.pdf
已有粗分类：网络流量监测、测量与工具
二级关联：无
相关性：强相关，分数 10
已有代码状态：已下载；TrafficLLM -> source\TrafficLLM

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\567.txt
- 原始字符数：101834
- 本次发送字符数：101834
- 是否截断：False

代码包：
- 仓库：TrafficLLM
  - URL：https://github.com/ZGC-LLM-Safety/TrafficLLM
  - 状态：downloaded
  - 本地目录：source\TrafficLLM
  - 顶层结构：.gitattributes、.idea/、Adapt2GLM4/、EA-PEFT/、README.md、agent/、config.json、dual-stage-tuning/、evaluation.py、images/、inference.py、llm/、models/、preprocess/、requirements.txt、tokenization/、trafficllm_server.py、trafficllm_server_text.py、tutorials/
  - 主要语言：Python:77、Shell:5、JSON:4、YAML:2、Jupyter:2
  - README 标题：TrafficLLM: Enhancing Large Language Models for Network Traffic Analysis with Robust Traffic Represe、News、Brief Introduction、TrafficLLM Datasets、Instruction Datasets、Traffic Datasets、Getting Started、Table of Contents:、1. Environment Preparation <a href='#all_catelogue'>[Back to Top]</a>、Clone our TrafficLLM
  - README 运行线索：conda create -n trafficllm python=3.9；conda activate trafficllm；pip install -r requirements.txt；pip install rouge_chinese nltk jieba datasets；python preprocess_dataset.py --input /Your/Raw/Dataset/Path --dataset_name /Your/Raw/Dataset/Name --traffic_task detection --granularity packet --output_path /Y；python traffic_tokenizer.py；python ea-peft.py --model_name /Your/Base/Model/Path --tuning_data /Your/New/Dataset/Path --adaptation_task update --task_name MTD；python evaluation.py --model_name /Your/Base/Model/Path --traffic_task detection --test_file datasets/ustc-tfc-2016/ustc-tfc-2016_detection_packet_test.json --l
  - 关键文件：{"依赖环境": ["requirements.txt", "Adapt2GLM4/FT/requirements.txt", "llm/llama-recipes/requirements.txt"], "推理/演示入口": ["inference.py", "Adapt2GLM4/FT/infer.sh", "Adapt2GLM4/FT/inference.py", "dual-stage-tuning/main.py", "llm/llama-recipes/inference/inference.py"], "数据处理入口": ["Adapt2GLM4/Preprocess.py", "llm/llama-recipes/configs/datasets.py", "llm/llama-recipes/preprocess/preprocess_dataset.py", "llm/llama-recipes/preprocess/preprocess_pretrain.py", "llm/llama-recipes/preprocess/preprocess_utils.py", "llm/llama-recipes/traffic_preprocess/preprocess_dataset.py", "llm/llama-recipes/traffic_preprocess/preprocess_utils.py", "llm/llama-recipes/utils/dataset_utils.py", "preprocess/preprocess_dataset.py", "preprocess/preprocess_utils.py"], "模型定义": ["llm/llama-recipes/inference/model_utils.py"], "训练入口": ["Adapt2GLM4/FT/train.sh", "dual-stage-tuning/trainer.py", "dual-stage-tuning/trainer_seq2seq.py", "llm/llama-recipes/training_script.py", "llm/llama-recipes/configs/training.py", "llm/llama-recipes/utils/train_utils.py"], "评估/测试入口": ["evaluation.py", "llm/llama-recipes/inference/evaluation.py"], "配置文件": ["config.json", "llm/llama-recipes/utils/config_utils.py", "tutorials/config.json"]}
  - 数据集线索：DAPT、ISCX、Quic、TOR、Tor、USTC、VPN、cert、dapt、iscx、nsl、quic

论文正文包开始：
<<<PAPER_TEXT
1

TrafficLLM: Enhancing Large Language Models for Network Traffic
Analysis with Generic Traffic Representation

arXiv:2504.04222v2 [cs.LG] 15 Apr 2025

Tianyu Cui , Xinjie Lin , Sijia Li, Miao Chen, Qilei Yin, Qi Li, Senior Member, IEEE,
and Ke Xu, Fellow, IEEE

Abstract—Machine learning (ML) powered network traffic
analysis has been widely used for the purpose of threat detection.
Unfortunately, their generalization across different tasks and unseen data is very limited. Large language models (LLMs), known
for their strong generalization capabilities, have shown promising
performance in various domains. However, their application to
the traffic analysis domain is limited due to significantly different
characteristics of network traffic. To address the issue, in this
paper, we propose TrafficLLM, which introduces a dual-stage
fine-tuning framework to learn generic traffic representation
from heterogeneous raw traffic data. The framework uses trafficdomain tokenization, dual-stage tuning pipeline, and extensible
adaptation to help LLM release generalization ability on dynamic
traffic analysis tasks, such that it enables traffic detection and
traffic generation across a wide range of downstream tasks. We
evaluate TrafficLLM across 10 distinct scenarios and 229 types of
traffic. TrafficLLM achieves F1-scores of 0.9875 and 0.9483, with
up to 80.12% and 33.92% better performance than existing detection and generation methods. It also shows strong generalization
on unseen traffic with an 18.6% performance improvement. We
further evaluate TrafficLLM in real-world scenarios. The results
confirm that TrafficLLM is easy to scale and achieves accurate
detection performance on enterprise traffic.
Index Terms—Large language models, network traffic analysis,
intrusion detection systems.

I. I NTRODUCTION

N

ETWORK traffic is the cornerstone of the Internet,
carrying all interactions and transfers within the network. However, as networking techniques evolve, attackers
can leverage network traffic to conduct various malicious
activities, such as fishing [1], malware campaigns [2], web
attacks [3], and exploiting vulnerabilities [4]. Considerable
enterprises have recognized the importance of analyzing traffic
data to detect threats, investigate incidents, and monitor environments [5], [6]. This has facilitated the development of many
sophisticated network traffic analyzers (NTA) and security information and event management (SIEM) solutions, e.g., Cisco
Secure Network Analytics [7] and Rapid7 InsightIDR [8].
Existing work has achieved great improvement in many tasks,
such as encrypted application classification [9], website fingerprinting [10], and malicious traffic detection [11].
In recent years, machine learning (ML) based methods [12]–
[14] have been proposed due to their strong representationTianyu Cui, Xinjie Lin, Sijia Li, Miao Chen, and Qilei Yin are
with the Zhongguancun Laboratory, Beijing, 100093, China (email: cuity@zgclab.edu.cn; linxj@zgclab.edu.cn; lisj@zgclab.edu.cn;
chenm@zgclab.edu.cn; yinql@zgclab.edu.cn).
Qi Li and Ke Xu are with the Zhongguancun Laboratory, Beijing 100093,
China, and also with the Tsinghua University, Beijing, 100094, China (e-mail:
qli01@tsinghua.edu.cn; xuke@tsinghua.edu.cn).

learning abilities for diverse traffic patterns. Despite their
promising potential, ML-based methods still suffer from the
following limitations, leading to low generalization of existing
ML-based models: (i) Generalization across various tasks.
In each sub-field of traffic analysis tasks, existing methods
usually learn with handcrafted features and supervised labels
to develop complicated ML models for specific tasks [15],
[16]. These task-specific models are hardly shared across
different tasks due to the specialized handcrafted features or
model designs. The development costs will be considerable
in covering various tasks. (ii) Generalization to unseen data.
ML-based methods are widely criticized for their inability to
handle unseen data [11]. These models are usually forced
to learn known patterns in the high-quality labeled datasets.
When faced with unseen data scenarios like concept drift [17]
and zero-day attacks [18], ML models often achieve poor
performance due to low generalization.
Thus, it is vital to develop a more generic model to enhance generalization of ML models across different tasks and
data distributions [16], [19]. Recently large language models
(LLMs) [20]–[24] have shown outstanding performance in
many complex tasks [25]. Thanks to their pattern mining, generalization to unseen data, and reproducibility across different
tasks, LLMs could release remarkable capabilities in various
downstream tasks [26], which inspired multiple high-level
views to develop specialized large-scale models for network
traffic analysis. For instance, LLMs’ pattern mining and reasoning ability can be utilized to learn generic representations
behind IP attributes, flags, timings, and datagram lengths in
traffic data. Moreover, the generalization ability allows LLMs
to adapt to diverse network environments and attack scenarios.
Therefore, LLM could serve as a more powerful ML model to
provide traffic representation with strong generalization ability.
However, it is non-trivial to utilize LLMs for network traffic
analysis. First, the traffic data contains considerable heterogeneous meta-information (i.e., protocol fields in packets and
flows) for pattern learning, which is significantly different
from the natural language. This input modality gap from the
plain text makes it difficult for native LLMs to process the
traffic data [21], [23], which further prevents LLMs from
generalizing to traffic data of different network scenarios.
Second, different downstream tasks involve diverse domain
knowledge and traffic patterns (e.g., botnet traffic and Tor
network traffic). Jointly learning the multi-type task-specific
instruction semantics and traffic data can confuse LLM, leading to poor generalization across different tasks [19], [27].
Third, the traffic domain often faces environment drift like

2

application updates and attack changes [3]. Unfortunately,
LLM adaptation is extremely time-consuming due to the
large model size. The high costs to update models for new
environment generalization make LLM impractical in realworld scenarios.
To overcome these challenges, we propose TrafficLLM, a
dual-stage fine-tuning framework for all open-sourced LLMs
to learn generic traffic representation from expert instructions
and raw traffic data, helping LLMs acquire extensive domain
knowledge to enhance the generalization across diverse traffic
analysis tasks and unseen scenarios. TrafficLLM implements
three core designs: (i) Traffic-domain tokenization: To mitigate the input modality gap between traffic and language,
TrafficLLM is equipped with a traffic-domain tokenization
mechanism to extend LLM’s native tokenizers. It helps LLM
generalize to different types of traffic data and achieves
efficiency improvement by reducing token length. (ii) Dualstage tuning pipeline: TrafficLLM implements a dual-stage
tuning pipeline to conduct multimodal learning with text and
traffic data. This pipeline helps LLM accurately understand
the instruction text of security experts and achieve effective
traffic pattern learning in different downstream tasks, forming
generic representations across different tasks. (iii) Extensible
adaptation with parameter-effective fine-tuning (EA-PEFT):
To facilitate LLM’s generalization to new environments, TrafficLLM employs extensible adaptation using parameter-effective
fine-tuning (PEFT) technique [28]. EA-PEFT splits different
traffic representation abilities into various PEFT models, which
helps TrafficLLM preserve existing capabilities and upgrade
the model on new network environments.
We build TrafficLLM prototype to achieve generic traffic
representation on ten downstream tasks, which supports traffic
analysis for different applications (e.g., mobile apps, websites,
and malware), protocols (e.g., HTTP, TLS1.3, and DoH),
network environments (e.g., VPN, Tor, and botnet), and threats
(e.g., web attacks and APT attacks). TrafficLLM builds generic
representation for two key abilities, i.e., traffic detection and
traffic generation ability, to assist traffic analyst in their daily
attack detection and red teaming work, with 5.90%-80.12%
and 3.07%-33.92% of performance improvement over existing
ML methods. We further evaluate TrafficLLM on unseen environments and real-world scenarios. TrafficLLM shows stronger
generalization compared to existing ML models.
Contributions. Our contributions can be shown as follows:
• We develop TrafficLLM, a dual-stage fine-tuning framework
learning with extensive expert instruction and raw traffic
data, which helps LLM obtain generic traffic representation
from the domain knowledge to achieve strong generalization
across diverse traffic analysis tasks.
• We build TrafficLLM with three core techniques to overcome the challenges of using LLMs in the traffic domain.
TrafficLLM employs traffic-domain tokenization to mitigate
the modality gap and generalize to heterogeneous data, dualstage tuning pipeline to conduct multimodal learning across
diverse tasks, and EA-PEFT to realize generalization to new
environments.
• We construct the first large-scale traffic-domain LLM adap-

TABLE I
T HE BASIC INFORMATION AND MODEL CAPABILITIES OF CURRENT
MAINSTREAM LLM S AND TRAFFIC - DOMAIN PLM S . (” ” = HAS THE
ABILITY. ”○” = DOESN ’ T HAVE THE ABILITY. ”○␣” = HAS THE BASIC
ABILITY BUT STILL HAS SHORTCOMINGS )
Basic Information
Model

Model Capability

Model
Size

Open
Source

Traffic
Detection

Traffic
Generation

Llama3 [29]
Gemini1.5 [30]
Claude3 [31]
Mistral Large 2 [32]
GPT-4 [21]
GLM-4 [24]
Baichuan4 [33]

8B/70B
Unk.
Unk.
Unk.
Unk.
9B/130B
53B

Yes
No
No
No
No
Yes
Yes

○
○
○
○
○
○
○

○
○
○
○
○
○
○

ET-BERT [16]
PERT [34]
netFound [19]
NetGPT [35]
Lens [36]

0.1B
0.04B
0.2B
0.1B
0.25B

Yes
Yes
No
No
No

TrafficLLM

6B/12B

Yes

Language
Processing

○
○
○
○␣
○␣

○
○
○
○
○

tation dataset for future research. To the best of our knowledge, we have collected the largest LLM tuning dataset for
the traffic domain to date, which includes ≈ 0.4M samples
consisting of instruction text and traffic data supervised by
experts and AI assistants.
• We conduct extensive experiments on various downstream
tasks to demonstrate the superiority of TrafficLLM. TrafficLLM achieves better performance with generic representation compared to 15 state-of-the-art traffic detection or
generation methods. Moreover, TrafficLLM obtains strong
generalization on unseen data and real-world settings.
Website demo and datasets. We provide TrafficLLM’s
demo, source codes and all the tuning datasets at
https://github.com/ZGC-LLM-Safety/TrafficLLM.
II. P ROBLEM S TATEMENT & T HREAT M ODEL
A. Problem Statement
Investigation on Existing LLMs. We survey existing LLM’s
capabilities for network traffic analysis. Due to the difficulty of
processing traffic data, we have not witnessed the deployment
of the foundation model for network traffic analysis in the
industry. As of December 2024, we have compiled the model
capabilities of the current mainstream LLMs in Table I.
Although the existing LLMs have initially possessed certain
knowledge in the network security field [26], the majority of
them can not accomplish traffic analysis tasks due to the lack
of capabilities for traffic processing. Most LLMs lack insights
from traffic data learning. They can only respond to basic
instructions with inaccurate conclusions. To overcome the
problem, a series of works like ET-BERT [16] and PERT [34]
have been developed in recent years to process traffic data
with pre-trained language models (PLMs) [26], aiming to build
effective traffic detection and generation capabilities. However,
they have several shortcomings:
• High development cost. These approaches mainly utilize
pre-training techniques [37], which has a high training time
and resource cost. Compared with fine-tuning, they can not
inherit existing LLMs’ abilities, which is less practical.
• Limited model size. These models are usually smaller than
1B. Strictly speaking, they are not part of LLMs [26]. These

3

Fig. 1. Native LLM’s limitation to handle traffic data with default tokenization
and tuning strategies. Left and Middle: LLM is ineffective and inaccurate in
loading traffic data with language tokens directly. Right: LLM suffers from
learning multi-type semantics and traffic data at the same stage.

Fig. 2. The adaptation costs of LLM’s retraining to update traffic detection
capabilities on new scenarios. TrafficLLM employs EA-PEFT to reduce the
cost by using multiple external parameters to encapsulate different capabilities.

models may lose LLM’s surprising emergent abilities [38]
with strong generalization that can not be present in small
models.
• Narrow scenarios. These efforts only train on traffic
datasets. They fall short in handling natural language, rendering them incapable of following instructions and conducting complex traffic analysis tasks [39], requiring a high
user threshold.
• Defective abilities. These methods have shortcomings in
traffic detection and generation. They do not have the
generalization abilities to detect traffic on unseen data [11].
Moreover, they can only generate 5-tuples of packets and
flows, whose practical uses are very limited [35], [36].
In this paper, we aim to exploit LLM to facilitate the work
of network traffic analysis with strong generalization across
different tasks. Given the language instructions that involve
diverse domain knowledge and the traffic data that contains
multi-type benign or malicious traffic, an adapted LLM in the
traffic domain is expected to learn generic traffic representation
with its accuracy and generalization in pattern learning. Note
that all work can be completed through dialogue with the
generic model, which reduces the operational threshold and
development costs for security practitioners. However, the
characteristics of the traffic domain leave three challenges to
realizing LLM’s generalization on traffic analysis tasks.
Challenge 1: Generalization to heterogeneous input of
traffic data. Traffic data consists of structured metadata in
packets and flows (e.g., IPs and ports). However, most LLMs
are considered as the specialized model for processing plain
text, which has a huge gap from the traffic data. Before being
fed into LLM, the text is converted into language tokens
using a standard tokenizer [21], [23]. These tokenizers are
usually trained on large-scale text corpora with tokenization
algorithms like WordPiece and Byte-Pair Encoding (BPE),
which rarely see heterogeneous traffic data. Consequently,
LLM may fail to directly transform traffic data into textual

formats and load them with default tokenization.
To give an instance, we adapt Llama2-7B [23] to conduct
the malware traffic detection (MTD) [40] task with its native
tokenizer. First, it is not effective to split traffic information
as the input. As shown in Figure 1 (left), the default tokenizer
will produce many redundancies when processing metadata in
TLS packets. It may reduce the efficiency of LLMs in realistic
traffic analysis work. Second, the transformed tokens are not
performed well to ensure detection accuracy. In Figure 1
(middle), the performance of native LLM is not remarkable
on the MTD task (only 79.5% of accuracy on USTC-TFC
2016 dataset [40]) since the unsuitable tokenization split key
features incorrectly, leading to the failure to capture distinct
patterns between benign and malicious traffic.
Challenge 2: Generalization across different tasks with
multimodal learning. Network traffic analysis covers a wide
range of specific tasks, including detecting and generating
attack traffic in different scenarios (e.g., the MTD task). It
involves diverse task-specific knowledge in the instruction
to prompt LLM to conduct different work. Moreover, these
downstream tasks usually point to different network environments, which involve representations learned from multitype traffic meta-information (e.g., packet lengths in encrypted
application classification (EAC) [41] and HTTP request headers in web attack detection (WAD) [3]). These complexities
of instructions and traffic patterns can easily confuse LLM
when facing multimodal learning [19], [27]. As depicted in
Figure 1 (right), we directly mix the training data of three
traffic detection tasks (i.e., MTD, EAC, and WAD tasks) and
train Llama2 with the default tuning strategy. Llama2 only
reaches 10.2% of average accuracy, indicating the difficulty
for LLM to learn with multimodal across different tasks.
Challenge 3: Generalization to new environments with
model update. The adaptation cost of LLM is quite expensive
as it requires training large-scale parameters with extensive
datasets [20], [21]. However, many traffic analysis tasks often
need to update the model’s traffic representation to struggle
with dynamic scenarios, which are raised by the application
version updates (e.g., concept drift [17]) and attack method
changes (e.g., APT attacks [42]). The high adaptation costs
of LLMs prevent the update of traffic representations on new
scenarios. As shown in Figure 2, we measure Llama2-7B’s
adaptation overhead on 5 NIVIDA A100-80GB GPUs for
traffic detection tasks. Traditional retraining methods consume
78.5GB GPU memory and 126.7h to adapt to new environments for one epoch, which is unacceptable in real-world
dynamic scenarios.
B. Threat Model
Our purpose is to develop an LLM for traffic representation,
which can be leveraged to construct traffic detection and
generation methods to replace traditional ML-based methods
that can be integrated into existing sophisticated network
traffic analyzers (NTA) [7] and security information and event
management (SIEM) systems [43], which are widely deployed
in Security Operation Centers (SOCs) to analyze abnormal
events based on traffic mirroring and logs. Different from

4

NLP

Traﬃc Mirror

0000 0000 0000
0212 0212 0212

Benign / Malicious
Traﬃc Data

First
Adaptation

[ eos ]

Language Traﬃc
Tokens Tokens

2. Dual-Stage Tuning Pipeline
Parameter-Eﬃcient
Fine-Tuning (PEFT)
Tuned

NLP

MTD

+

Large Language
Models (LLMs)

+

Llama

P-tuning v2

Traﬃc Pattern Learning

Text Learning
+

MTD

WAD

…

BND

NLP1

MTD

WAD1

…

BND

NLP2

MTD

WAD2

…

BND

Updating

Updating

WAD
BND

Web Attack
Detection Model
Botnet
Detection Model

Malicious

Benign

0000
0212

0000
0212

Traﬃc Detection

Task Understanding Task-specific Traﬃc Learning
New Scenario
Adaptation

0000 0000 0000
0212 0212 0212

…

_
_
_

Ip.len 1360

_
_
_

[ cls ]

_
_
_

…

_
_
_

[ cls ] Given the

_
_
_

Traﬃc-domain Tokenizer

Security
Experts

_
_
_

[ eos ]

1. Traﬃc-Domain Tokenization
Traﬃc Analysis
Instruction

Natural Language
Processing Model
Malware Traﬃc
Detection Model

ChatGLM

+
Frozen

Generated
Samples
0000 Red Teaming
0212

ML-based IDS

Traﬃc Generation

3. Extensible Adaptation with PEFT

Fig. 3. The overall framework of TrafficLLM. TrafficLLM employs three core techniques: traffic-domain tokenization to process instructions and traffic data,
dual-stage tuning pipeline to learn text semantics and traffic patterns across different tasks, extensible adaptation with parameter-effective fine-tune to update
model parameters for new scenario adaptation.

the threat model of the existing ML-based traffic detection
and generation studies [9], [44], TrafficLLM aims to develop
LLM-based model to adapt to different tasks, which is more
generalized than specific ML models. TrafficLLM can be
directly driven by instructions from experts. It achieves generic
traffic representation using domain knowledge to extract taskrelated traffic patterns from raw traffic based on instructions.
Leveraging LLM’s pattern learning and generalization abilities, we develop TrafficLLM to build the centralized traffic
analysis solution, which can achieve the following goals:
• Attack detection. TrafficLLM establishes comprehensive
traffic detection capabilities to process and analyze diverse
benign and malicious traffic. Learning with a variety of
heterogeneous traffic data, TrafficLLM can extract generic
traffic representation from raw traffic to identify benign
and malicious categories [9], [45], or realize more finegrained classification (e.g., application types in encrypted
application classification (EAC) [16], [41] and network
types in botnet detection (BND) [46]).
• Attack synthesis. TrafficLLM can generate attack samples
to facilitate red teaming and enhance the robustness of
network-based IDSes (NIDS) [47] when lacking the highquality traffic data in practical scenarios. Different from
existing ML-based traffic generation studies [35], [36], [44],
TrafficLLM can generate a wide range of target traffic with
.pcap format based on LLM’s strong memorization. It can
help security practitioners simulate traffic attacks to measure
the vulnerability of systems and build robust IDSes through
data augmentation.
III. D ESIGN OF T RAFFIC LLM
A. Overall Framework
We develop TrafficLLM, which captures generic traffic
representation from diverse traffic-domain instruction text and
raw traffic data through a dual-stage fine-tuning framework,
aiming to release LLM’s strong generalization across diverse
traffic analysis tasks. TrafficLLM overcomes the challenges of
applying LLM in traffic analysis. It builds domain knowledge
by training with extensive expert instructions and traffic data.

Driven by expert instructions, TrafficLLM automatically extracts task-related traffic patterns from raw packets and flows,
forming the generic representation across different tasks. We
present the architecture overview of TrafficLLM in Figure 3.
TrafficLLM designs three modules:
Traffic-Domain Tokenization. To overcome the modality
gap between natural language and heterogeneous traffic data,
TrafficLLM employs traffic-domain tokenization to process the
diverse input of traffic detection and generation tasks for representation learning. This mechanism effectively extends LLM’s
native tokenizer by training the specialized tokenization model
on large-scale traffic-domain corpora (Section III-B).
Dual-Stage Tuning Pipeline. TrafficLLM designs a dual-stage
tuning pipeline to achieve LLM’s generic representation learning across different traffic-domain tasks. The pipeline trains
LLM to understand instructions and learn task-related traffic
patterns at different stages, which builds upon TrafficLLM’s
domain knowledge to learn traffic representations for diverse
traffic detection and generation tasks (Section III-C).
Extensible Adaptation with Parameter-Effective FineTuning (EA-PEFT). To adapt LLM for generalization to
new traffic environments, TrafficLLM proposes an extensible
adaptation with parameter-effective fine-tuning (EA-PEFT) to
update model parameters with low overhead. The technique
splits model capabilities in different PEFT models, which
helps minimize the adaptation costs on dynamic scenarios
raised by traffic pattern changes (Section III-D).
B. Traffic-Domain Tokenization
TrafficLLM utilizes traffic-domain tokenization to encode
original inputs of traffic analysis tasks and makes them learnable for LLMs. We extract tuning data from raw traffic to train
the specialized tokenizer, which effectively extends LLM’s
native tokenizer. The principle of traffic-domain tokenization
is to map the natural language and traffic data into the same
feature space, supporting LLM in accepting heterogeneous
traffic data to build the representation.
Tuning Data Extraction. To help LLMs reduce the modality
gap and make them feasible to handle traffic data across

5

different tasks, TrafficLLM directly extracts training data from
raw traffic for generic traffic representation. The purpose of
using raw traffic is to release the generalization of TrafficLLM
in different scenarios, different from the traditional ML-based
methods that heavily rely on predefined features. Rather than
select for certain features, TrafficLLM leverages the whole
meta-information in the packets to learn the important features
without human guidance. It helps TrafficLLM obtain strong
generalization across different scenarios.
To facilitate LLMs acquire domain knowledge to learn
traffic representations across different tasks, TrafficLLM employs instruction-learning [39] to build tuning data templates
and adapt LLMs to the traffic-domain semantic space. These
instructions can guide LLM to automatically extract taskrelated patterns in the traffic data to build representations.
Then, we utilize Tshark to extract protocol fields in different
packet layers. These meta-information are organized by pairs
including the field name and the corresponding value (e.g.,
tcp.srcport: 443). To indicate the beginning of traffic
data, we define an indicator token <packet> in the context.
Each packet data is started with this special indicator to form
the flow data. This instruction-learning design helps LLM
obtain domain knowledge to capture valuable semantics for
pattern learning across different tasks. Finally, TrafficLLM
combines traffic analysis instructions and the extracted traffic
data to build the tuning data. The examples of TrafficLLM’s
tuning data are shown as follows.
Traffic Detection Tuning Data Example
Instruction: Given the following traffic data that contains protocol fields, traffic features, and payloads.
Please conduct the Malicious Traffic Detection task
to determine which application category the encrypted
benign or malicious traffic belongs to.
¡packet¿: ip.len: 1360, ip.proto: 6, tcp.srcport: 443,
tcp.dstport: 56603, tcp.len: 1308, tcp.window size: ...
Output: Zeus .
Traffic Generation Tuning Data Example
Instruction: Based on the protocol fields, traffic
features, and payloads of traffic in your knowledge.
Please generate a packet of Skype traffic .
Output: Skype.pcap (ip.src: 1.2.102.211, ip.dst:
1.1.210.113, tcp.srcport:443, tcp.dstport: 27567, raw:
1021ac5010000021ac50200000800450002aeea10400
0200632f2010266d30101...).
Tokenizer Training. After extracting the tuning data, we
build a specialized traffic-domain tokenizer to form the input
traffic tokens. We use the BPE method to train the specialized
tokenizer on the large-scale tuning data. Since native LLM
has hardly ever seen traffic data, it can be considered as
an extension to the existing tokenizer. Table II shows an
example of tokenization of TrafficLLM and an open-sourced
LLM ChatGLM2 [24]. Tokenizers of existing LLMs tend to

TABLE II
T HE TOKENIZATION OF T RAFFIC LLM’ S TOKENIZER ON THE TRAFFIC
DATA COMPARED TO C HAT GLM2’ S TOKENIZER .
Default tokenization:

ip

x

7

0

ip

0
.

8

.

1

,

0

0

src

:

2

.

5
t

cp

1
1
2

.

0

0

0

:

,

ip

.

che

cks

um

ip

.

che

cks

um

.

status

:

2

,

.

2

.

1

,

ip

.

d

:

1

9

9

,

port

:

7

3

,

.

0

.

3

6

:

4

TrafficLLM tokenization:

ip

.

proto

000017

a

checksum

2.15,

ip

.

st

proto
7

port

7,

d

.
a

ip
dst

:

.

198.52.

5

st

:

t

cp

.

src

4

3

,

t ... [Token length : 1405]

:

6,

.

status

200.39,

tcp

ip
:

.

.

4

3

0

checksum

:

0

2,

ip

.

:

10.0.

srcport

:

43731,

src

dstport

x
:

443, ... [Token length : 690]

split the field names (e.g., checksum and tcp) since they
have learned less of the traffic-domain languages. In contrast,
TrafficLLM’s tokenizer can retain these field name indicators
based on their appearance frequency in training data. It can
also store the common field values (e.g., window sizes and
flags), helping LLMs learn the numerical meta-information
correctly. Furthermore, due to the accurate tokenization on
traffic data, TrafficLLM can produce shorter packet tokens
with a 699.36 average token length, compared to ChatGLM2’s
1445.04 token length. It helps TrafficLLM obtain faster packet
processing efficiency compared to the native LLMs.
As shown in Figure 1 (left) and (middle), TrafficLLM’s
tokenization is more effective and accurate in loading traffic
data compared to the default tokenization. This mechanism
helps TrafficLLM reach 106% efficiency improvement to process traffic data. TrafficLLM also achieves 17.4% better performance on MTD tasks by using the traffic-domain tokenization.
C. Dual-Stage Tuning Pipeline
TrafficLLM proposes a dual-stage tuning pipeline to help
LLMs acquire domain knowledge to achieve generic representation learning on diverse traffic analysis tasks. The pipeline
can help LLMs obtain two abilities in different stages: (i)
understanding the task-related natural language to determine
which task should be conducted and (ii) learning the taskspecific traffic pattern across different tasks. Guided by expert
instructions, TrafficLLM autonomously extracts task-specific
traffic patterns from encoded inputs, building generic representations across different tasks.
Tuning Objectives. TrafficLLM aims to leverage LLMs’ pattern mining and generalization abilities to learn generic traffic
representations. Based on LLM’s strong memorization coming
from the deep Transformer architecture, these representations
can obtain distinct traffic patterns learned from the metainformation (e.g., lengths, directions, and flags). TrafficLLM
automatically integrates these heterogeneous data and finds
their importance for different tasks (e.g., lengths for encrypted
traffic classification (EAC) [41] and directions for website
fingerprinting (WF) [48]. TrafficLLM uses the generic representations to realize two mainstream tasks, i.e., traffic detection
and traffic generation.
• Traffic detection. Given the security expert’s instruction
S = {s1 , s2 , ..., sm } that contains m language tokens, the
traffic data X = {x0 , x1 , ..., xn } that contains n traffic

6

_
_
_

0000
0212

Language
Tokens
Traﬃc
Tokens

PEFT Model Set

…

[ eos ]

[ cls ] ip.len 1360 ip.proto 6 tcp.srcport 443 tcp.dstport …

[ eos ]

[ cls ] Given the following traﬃc data

PEFT models

Natural Language
Instruction Tuning

LLMs
+
NLP

WAD

Web Attack
Detection

MTD

Malicious Traﬃc
Detection

EAC

Encrypted App
Classification

BND

Botnet
Detection

…

that contains

Task-Specific
Traﬃc Tuning

LLMs
+
MTD

Model_Update(
TraﬃcLLM, Instruction,
Traﬃc_Data, Labels)
Old Task Updating

TraﬃcLLM
Adaptor

Labels
y1

BitTorrent

y2

Nsis-ay

y3

Zeus

y4

Virut

(1)

Traffic generation. Traffic generation can be regarded as
the reversed process of traffic detection tasks. It aims to
input the generation instruction Si to describe the specific
scenario and the traffic category yi ∈ Y = {y0 , y1 , ..., yc }
of the traffic to be generated. TrafficLLM can generate a
synthetic packet X̂i that satisfies the instruction:
X̂i = TrafficLLM((Si , yi )|θ)

(2)

Natural Language Instruction Tuning. In the first stage
of the dual-stage tuning in TrafficLLM, we introduce natural
language instruction tuning to inject the professional task
description text from the field of cybersecurity into LLMs. As
shown in Figure 4, the pipeline forces LLM to understand the
instructions from security experts and predict the task name
ϕi that needs to be performed.
ϕi = TrafficLLMstage1 (Si |θ1 )

(3)

where θ1 is the trainable parameters in the first stage. ϕi is the
downstream task name to be performed. To learn the context of
the security task description, we follow LLM’s autoregressive
objective function to converge the model. Given the human
instruction Si = {s1 , s2 , ..., sm }, TrafficLLM calculates the
probability Pm of token si to model the loss J (θ1 ):
Pm (si |s1 , ..., si−1 ) = softmax(Ws hi−1 )
XX
J (θ1 ) =
logPm (si |s1 , ..., si−1 )

NLP2

MTD

Updating
Model_Insert(TraﬃcLLM,
Instruction, Traﬃc_Data,
Labels, New_Task_Name)
New Task Inserting

WAD1

…

BND

WAD2

…

BND

Updating

NLP1

MTD

WAD

…

BND

NLP2

MTD

WAD

…

BND

Updating

EAC

Adding

…

tokens to describe the traffic meta-information, traffic detection requires the task-related instruction Si and traffic
data Xi (flows or packets) as TrafficLLM’s input (Si , Xi ).
Then, TrafficLLM can identify the ground truth label yi ∈
Y = {y0 , y1 , ..., yc } of the traffic across different traffic
detection tasks (e.g., MTD, WAD, and BND tasks) with its
parameter θ:

•

MTD

Fig. 5. The workflow of the extensible adaptation with parameter-effective
fine-tuning (EA-PEFT) in TrafficLLM.

Fig. 4. Illustration of the dual-stage tuning pipeline to learn natural language
and traffic patterns respectively.

yi = TrafficLLM((Si , Xi )|θ)

NLP1

(4)

i

where Ws is the learning parameter matrix for task understanding. hi−1 denotes the representation encoded in TrafficLLM
with the input of the preceding i − 1 tokens. The natural
language instruction tuning technique plays a crucial role in
accurately matching instruction text with the corresponding
downstream task, thereby enabling LLMs’ domain knowledge
to understand different tasks.

Task-Specific Traffic Tuning. The second stage we propose
is task-specific traffic tuning. After understanding the task,
we force TrafficLLM to learn the traffic pattern under the
downstream tasks. In this stage, we fine-tune LLM using
the training pairs (Xi , yi ) to model the traffic representation
under traffic detection tasks ϕT D and traffic generation tasks
ϕT G . For the specific downstream task ϕi , TrafficLLM trains
the second stage parameters θ2 to predict traffic labels yi or
generate synthetic traffic X̂i :
yi = TrafficLLMstage2 (Xi |(θ2 ; ϕi ∈ ϕT D ))
X̂i = TrafficLLMstage2 (yi |(θ2 ; ϕi ∈ ϕT G ))

(5)

To inject the knowledge of heterogeneous traffic data into
LLMs, TrafficLLM builds and updates the representation of
traffic data Xi = {x1 , x2 , ..., xn }, by learning the context of
traffic packets and flows with the loss function J (θ2 ):
Pn (xi |x1 , ..., xi−1 ) = softmax(Wl hi−1 )
XX
J (θ2 ) =
logPn (xi |x1 , ..., xi−1 )

(6)

i

where Wl is the trainable parameter matrix for traffic representation learning. The task-specific traffic tuning aims to
align the LLMs with various traffic data under different
scenarios, such as VPN and Tor networks, which allows LLMs
to accomplish diverse downstream tasks with these traffic
representations.
As shown in Figure 1 (right), the dual-stage tuning pipeline
helps TrafficLLM achieve 95.0% of average accuracy across
MTD, EAC, and WAD tasks. TrafficLLM has an 84.8%
higher accuracy than directly fine-tuning due to learning text
semantics and task-specific traffic patterns in different stages.
D. Extensible Adaptation with PEFT
To realize LLM’s generalization to new traffic environments,
TrafficLLM employs extensible adaptation with parametereffective fine-tuning (EA-PEFT) to efficiently update representations on dynamic scenarios. The principle of EA-PEFT
is to split traffic representation abilities of different tasks into
various additional parameters, supporting for TrafficLLM to
selectively update parts of capabilities to enable rapid updates
of representations in new environments.
Traffic Domain Adaptation with PEFT. Assume that the
pre-trained LLM’s parameters are θLLM , to adapt to new
environments, traditional retraining methods require training
the full parameters of models, which indicates the parameter
update ∆θ is equal to θLLM , i.e., |∆θ| = |θLLM |. However,

7

the large parameter size of LLM entails huge costs of repeated
retraining in new environments. To address this limitation,
TrafficLLM freezes the parameters of the LLM and tunes
extra parameters to achieve parameter effective fine-tuning
(PEFT) [49]. During the dual-stage tuning, TrafficLLM tunes
additional parameters to respectively build θP EF T0 for task
understanding and θP EF Tϕi for task-specific traffic learning:
θ1 = θLLM + θP EF T0
θ2 = θLLM + θP EF Tϕi

(7)

where θP EF T0 and θP EF Tϕi are the parameter updates ∆θ
in the two stages. This strategy helps TrafficLLM encapsulate
abilities of natural language processing and traffic pattern
learning across different tasks into specialized PEFT models,
which are triggered by instructions from different tasks.
Extensible Adaptation with PEFT Models. Using the PEFT
models trained during traffic domain adaptation, TrafficLLM
employs EA-PEFT to organize these models with an extensible adaptation, which can help TrafficLLM easily adapt
to new environments. Figure 5 shows the overview of EAPEFT’s workflow implemented by Python scripts. In EAPEFT, TrafficLLM adaptor allows flexible operations to update
old models or register new tasks. For instance, When faced
with the traffic update in EAC and WAD tasks raised by client
version upgrade (e.g., App version drift) or attack method
changes (e.g., HTTP request body changes), the adaptor can
call Model_Update to update the specific PEFT models by
providing new EAC or WAD datasets. Moreover, TrafficLLM
can easily add new traffic analysis scenarios. The adaptor
can schedule Model_Insert to train new PEFT models
and insert them in the EA-PEFT framework. Based on these,
TrafficLLM easily scales to a wide range of traffic domain
tasks with the light-wise adaption scheme of EA-PEFT.
As shown in Figure 2, the EA-PEFT technique helps TrafficLLM only need to train 0.62% of parameters when adapting
to new traffic environments, which significantly reduces the
adaptation costs with the reduction of 69.9% GPU memory
and 88.8% training time. TrafficLLM effectively mitigates the
high adaptation cost of retraining methods, facilitating deploy
more traffic analysis tasks in real-world settings.
IV. E XPERIMENT S ETUP & I MPLEMENTATION
In this section, we introduce the experimental setup and
implementation of TrafficLLM, including the implementation,
datasets, baselines, and metrics used in the experiments.
A. Implementation of TrafficLLM
Testbed. We conduct our experiments on a Super GPU server
(super-SYS-420GP-TNR) with 5 NVIDIA A100 80G GPUs,
Ubuntu 18.04.1 (Linux 5.4.0), and 1TB memory. We use
PyTorch 2.0.1 to build the prototype TrafficLLM and deploy
Python scripts to incorporate TrafficLLM adaptor and PEFT
models in the EA-PEFT framework. We employ Llama27B [23] and ChatGLM2-6B [24] as the base LLMs for
most experiments. We choose P-Tuning v2 [28] as the PEFT
method. The storage of each PEFT model is 7.1MB.

Hyper-parameters. During the data pre-processing, we employ a data sampling process for each class to avoid the data
imbalance issue. The maximum number of flows in each class
is 5,000. We set the ratio of training sets, validation sets, and
test sets to 8:1:1. In traffic detection tasks, we followed [16]
to mask the Ethernet layer, IP addresses, and ports to avoid
the bias derived by the sensitive meta-information. During
the training stage, we set the training steps as 20,000; the
initial learning rate is 2 × 10−2 . The maximum source and
target lengths of generation tasks are set as 128 and 3,072,
while detection tasks are 3,072 and 32. During the inference
stage, we set top-p and temperature to 0.70 and 0.90 in traffic
generation, while 0.90 and 0.10 in traffic detection.
B. Datasets & Tasks
To comprehensively evaluate the effectiveness of TrafficLLM, we collect a wide set of traffic datasets and natural
language instructions for LLM adaptation and experiments.
Traffic Datasets. The traffic datasets used in our experiments
are shown in Table III. We use 10 traffic datasets with
different scenarios to collect ≈ 0.4M training data and build
generalization abilities:
• Generalization across different tasks. (i) Traffic detection:
To evaluate the detection performance of TrafficLLM on
various network scenarios, we choose 8 traffic datasets
to measure TrafficLLM’s abilities to detect malicious and
benign traffic. In malicious traffic detection tasks, we introduce malware traffic detection (USTC TFC 2016 [40]),
botnet detection (ISCX Botnet 2014 [46]), malicious DoH
detection (CIC DoHBrw 2020 [50]), and web attack detection (CSIC 2010 [51]) tasks. In fine-grained benign traffic
detection, we employ encrypted VPN detection (ISCX VPN
2016 [52]), Tor behavior detection (ISCX Tor 2016 [53]),
encrypted App classification (CSTNET 2023 [16]), and
website fingerprinting (CW-100 2024 [54]). We use traffic
detection instructions, flows/packets in the traffic datasets,
and the corresponding labels to build the human instructions
Si , traffic data Xi , and the target label yi . (ii) Traffic
generation: To implement the traffic generation capability,
we reuse the traffic datasets mentioned above. We use the
traffic label yi to produce the generation task instructions
Si and sample the packets to form the synthetic packets X̂i .
• Generalization to unseen data. To measure TrafficLLM’s
generalization ability on unseen traffic data, we set up the
concept drift [55] and APT attack detection [42] scenarios,
which are of great concern in the community. We selected
APP-53 2023 [55] and DAPT 2020 [42], two representative
open-sourced datasets containing historical and future-stage
traffic for evaluation.
We choose these datasets to cover various applications (i.e.,
mobile apps, websites, and malware), protocols (i.e., HTTP,
QUIC, TLS1.3, and DoH), network environments (i.e., VPN,
Tor, and botnet), and attacks (i.e., web attacks and APT
attacks) in the traffic. This ensures the variety to evaluate
model robustness across different scenarios.
Natural Language Instructions. We show the details of the
natural language dataset in Table IV. To build the natural

8

TABLE III
T HE DETAIL OF 10 TRAFFIC DATASETS USED TO BUILD THE TRAFFIC ANALYSIS DOWNSTREAM TASKS IN EXPERIMENTS . T RAFFIC LLM USES THE
TRAFFIC DATA AND LABELS OF THESE DATASETS TO BUILD TRAFFIC DETECTION AND GENERATION CAPABILITIES RESPECTIVELY.
Tasks

Abbrev.

Traffic Datasets

Description

#Flows

#Packets

#Labels

Malware Traffic Detection
Botnet Detection
Malicious DoH Detection
Web Attack Detection
APT Attack Detection

MTD
BND
MDD
WAD
AAD

USTC TFC 2016 [40]
ISCX Botnet 2014 [46]
CIC DoHBrw 2020 [50]
CSIC 2010 [51]
DAPT 2020 [42]

10-class malware and 10-class benign Apps
4-class botnets and 1-class benign network
4-class benign DoH and 1-class malicious DoH
1-class Web attack requests and 1-class benign requests
1-class APT attack traffic and 1-class benign traffic

9,853
30,511
545,463
61,000
3,000

97,115
300,000
28,341,000
61,000
10,000

20
5
5
2
2

Encrypted VPN Detection
Tor Behavior Detection
Encrypted App Classification
Website Fingerprinting
Concept Drift

EVD
TBD
EAC
WF
CD

ISCX VPN 2016 [52]
ISCX Tor 2016 [53]
CSTNET 2023 [16]
CW-100 2024 [54]
APP-53 2023 [55]

19-class VPN encrypted App traffic
8-class user behaviors under Tor network
20-class mobile App traffic using TLS encryption
100-class website accessing traffic under Tor
53-class mobile App traffic with concept drift

3,694
3,021
65,128
9,000
133,000

60,000
80,000
602,568
603,072
449,000

14
8
20
100
53

TABLE IV
T HE STATISTIC INFORMATION AND THE TOP WORDS OF THE NATURAL LANGUAGE INSTRUCTIONS WE COLLECT FOR TASK UNDERSTANDING .
Statistics

Value

Statistics

Value

Word

%Hits

Word

%Hits

Word

%Hits

Total words
Total unique words
Total sentences
Total instructions

128,248
1,999
15,238
9,209

Average number of words per instruction
Average number of unique words per instruction
Average number of sentence per instruction
Type Token Ratio (TTR)

15.26
13.92
1.65
1.56

traffic
network
data
field

4.15%
2.58%
1.60%
1.54%

packet
application
IP
botnet

1.01%
0.79%
0.56%
0.49%

software
tunnel
behavior
set

0.48%
0.44%
0.35%
0.33%

language corpus as the human instructions in TrafficLLM, we
invite security experts and college students to provide accurate
task descriptions for each downstream task. Moreover, to
increase the diversity of the context, we use ChatGPT [56] to
rewrite these expert instructions through prompt engineering
and remove similar instructions based on human annotation.
Each instruction is rewritten 20 times at least. Finally, we
collect ≈ 10K text instructions to build the training data.

macro-average area under ROC curve (Macro-AUC), and (vii)
Jensen-Shannon Divergence (JSD). Note that lower JSD and
FP denote better fidelity.
V. E VALUATION
In this section, we evaluate TrafficLLM’s generalization
abilities across different scenarios, including various detection
and generation tasks, unseen scenarios, and real-world settings.

C. Baselines & Evaluation Metrics
Baselines. To compare the performance of TrafficLLM, we
mainly use two types of baselines, including ML-based traffic
detection and generation methods.
• ML-based detection methods. We use state-of-the-art traffic detection methods across different tasks as baselines to
evaluate the traffic detection abilities of TrafficLLM. The
baselines include (i) Statistical Feature Methods: AppScanner [12], CUMUL [13], BIND [14], k-fingerprinting (KFP) [57], and FlowPrint [9]; (ii) Deep Learning Methods: FS-Net [41], Deep Fingerprinting (DF) [48], GraphDApp [58], TSCRNN [59], and Deeppacket [45]; (iii) Pretraining Methods: PERT [34] and ET-BERT [16].
• ML-based generation methods. To evaluate the performance of traffic generation, we compare TrafficLLM to
state-of-the-art ML-based generation methods. The baselines
include (i) The GAN-based IP header trace generation
algorithm: Netshare [44]; (ii) The conditional GANs-based
augmentation method: PacketCGAN [60]; (iii) The CNNGAN-based IP packet generator: PAC-GAN [61]. Note that
the rule-based methods are not in the range since they can
only simulate network characteristics and are difficult to
generate fine-grained packet features with manual configuration (e.g., diverse meta-information in App traffic).
Evaluation Metrics. We use the following metrics to evaluate
TrafficLLM: (i) Precision (PR), (ii) Recall (RC), (iii) F1-score
(F1), (iv) Accuracy (acc), (v) False Positive (FP), (vi) the

A. Generalization across Detection Tasks
We first evaluate whether TrafficLLM can reach robust
detection performance across different scenarios and analyze
the reason for its generalization ability on traffic detection.
Generalization on Different Tasks. Table V and Table VI
present the performance of TrafficLLM on 10 datasets for
various traffic detection tasks. Results indicate that TrafficLLM
can classify all 229 types of traffic with F1-score ranging from
0.9320 to 0.9960. TrafficLLM achieves at most 80.12% better
results than all baselines. Pre-training methods like PERT and
ET-BERT obtained acceptable results with the average F1scores of 0.8128 and 0.9324 since they additionally put the
traffic bytes of pre-trained datasets into the model compared to
prior works. Nevertheless, since TrafficLLM leverages LLM’s
pattern mining and generalization abilities, the performance
outperforms PERT and ET-BERT with an improvement of
9.63% at most on the F1-score metric.
Furthermore, due to the difference between various detection scenarios, most works keep a poor generalization ability
to share their models across different tasks (e.g., FlowPrint
keeps F1-scores ranging from 0.2254 to 0.7015 with a variance
of 3.396%). Results indicate that previous ML-based methods
usually show low generalization due to their dependence on
handcrafted features and predefined model structures. For
instance, Deeppacket gets an F1-score of 0.9503 on the
EVD task (ISCX VPN 2016) but only obtains an F1-score

9

TABLE V
T RAFFIC DETECTION RESULTS ON APP-53 2023, ISCX T OR 2016, ISCX VPN 2016, CSTNET 2023, AND CW-100 2024.
ISCX Tor 2016

Method

ISCX VPN 2016

APP-53 2023

CSTNET 2023

CW-100 2024

PR

RC

F1

PR

RC

F1

PR

RC

F1

PR

RC

F1

PR

RC

F1

AppScanner [12]
CUMUL [13]
BIND [14]
K-FP [57]
FlowPrint [9]

0.7251
0.5672
0.4569▼
0.7035
0.4201▼

0.6512
0.5731▼
0.4385▼
0.6789
0.3789▼

0.6124▼
0.5628
0.4469▼
0.6951
0.3901▼

0.7395
0.6322
0.5067▼
0.6784
0.7084

0.7125
0.6824
0.4975▼
0.6967
0.6608

0.7304
0.6570
0.5008▼
0.6891
0.6888

0.7035
0.5563
0.6566▼
0.5660▼
0.4890▼

0.6957
0.5467▼
0.6456▼
0.5260▼
0.5023▼

0.6980
0.5480▼
0.6502▼
0.5295▼
0.4950▼

0.6481
0.5373
0.7712
0.4172▼
0.2371▼

0.6420
0.5217▼
0.7689
0.3981▼
0.2270▼

0.6467
0.5274▼
0.7691
0.4012▼
0.2254▼

0.6780
0.5623
0.7504
0.5101▼
0.5237▼

0.6825
0.5715▼
0.7489
0.4995▼
0.5227▼

0.6802
0.5697▼
0.7501
0.5010▼
0.5225▼

GraphDApp [58]
FS-Net [41]
DF [48]
TSCRNN [59]
Deeppacket [45]

0.4789▼
0.6283▼
0.6072▼
0.9051
0.7456▼

0.4878▼
0.6274▼
0.6123▼
0.9178
0.7469▼

0.4781▼
0.5916▼
0.6090▼
0.9105
0.7400▼

0.6478
0.7693
0.6296▼
0.9346
0.9467

0.6488
0.7488
0.6051▼
0.9367
0.9508

0.6476
0.7507
0.6139▼
0.9349
0.9503

0.6860
0.8550
0.7689▼
0.7057▼
0.5590▼

0.6450
0.8349
0.7523▼
0.6890▼
0.5489▼

0.6550
0.8376
0.7604▼
0.6995▼
0.5506▼

0.6329
0.8291
0.7729▼
0.7529▼
0.4013▼

0.5965
0.8061
0.7621▼
0.7566▼
0.2965▼

0.6078
0.8195
0.7682▼
0.7558▼
0.3890▼

0.6530
0.4582▼
0.9120
0.8350
0.8243▼

0.6974
0.4781▼
0.9046
0.8210▼
0.8246▼

0.6870
0.4668▼
0.9075
0.8260
0.8244▼

PERT [34]
ET-BERT [16]

0.7480▼
0.9809

0.4952▼
0.9830

0.4874▼
0.9810

0.8573
0.9890

0.7394▼
0.9890

0.7481▼
0.9890

0.8458
0.8540▼

0.8369
0.8494▼

0.8403
0.8506▼

0.8896
0.9581

0.8721
0.9478

0.8771
0.9496

0.8247
0.8670▼

0.8355
0.8650▼

0.8300
0.8660▼

TrafficLLM
0.9810
0.9871
0.9810
0.9960
0.9970
0.9960
0.9325
0.9315
0.9320
0.9678
0.9369
0.9599
0.9370
1 We use
▼ to mark the results of each baseline with a decrease of more than 10% compared to their best results among 5 fine-grained benign traffic detection tasks.

0.9360

0.9366

TABLE VI
T RAFFIC DETECTION RESULTS ON ISCX B OTNET 2014, USTC TFC 2016, D O HB RW 2020, CSIC 2010, AND DAPT 2020.
ISCX Botnet 2014

Method

USTC TFC 2016

CIC DoHBrw 2020

DAPT 2020

CSIC 2010

PR

RC

F1

PR

RC

F1

PR

RC

F1

PR

RC

F1

PR

RC

F1

AppScanner [12]
CUMUL [13]
BIND [14]
K-FP [57]
FlowPrint [9]

0.9021
0.8791
0.6798▼
0.8398
0.5898▼

0.9004
0.8320
0.6489▼
0.8960
0.6309

0.9008
0.8417
0.6582▼
0.8591
0.5967

0.8872
0.6074▼
0.8268
0.6447▼
0.6609▼

0.8910
0.5239▼
0.8014
0.4172▼
0.6596

0.8972
0.5437▼
0.8209
0.3981▼
0.6584

0.7331▼
0.5623▼
0.7137▼
0.7035▼
0.7712

0.7063▼
0.5281▼
0.7003▼
0.6789▼
0.2371▼

0.7106▼
0.5301▼
0.7077▼
0.6951▼
0.2270▼

0.7590▼
0.6509▼
0.7224▼
0.6585▼
0.6960

0.7226▼
0.6486▼
0.7026▼
0.6496▼
0.6894

0.7408▼
0.6492▼
0.7115▼
0.6542▼
0.6935

0.7465▼
0.6905▼
0.7022▼
0.6855▼
0.7025

0.7112▼
0.6870▼
0.7002▼
0.6960▼
0.7009

0.7220▼
0.6894▼
0.7010▼
0.6920▼
0.7015

GraphDApp [58]
FS-Net [41]
DF [48]
TSCRNN [59]
Deeppacket [45]

0.7578
0.7303
0.8267
0.9206
0.9408

0.7598
0.8546
0.8509
0.8976
0.9520

0.7538
0.7876
0.7980
0.8989
0.9496

0.8027
0.5964▼
0.7623
0.9538
0.9369

0.8320
0.7174▼
0.7598
0.9428
0.9292

0.8263
0.6371▼
0.7604
0.9503
0.9338

0.6478▼
0.7123
0.7078▼
0.8837
0.8930

0.6791▼
0.6991▼
0.6986▼
0.8672
0.8977

0.6512▼
0.7053
0.7022▼
0.8695
0.8965

0.8350
0.8056
0.7892
0.8453▼
0.8934

0.8342
0.7783
0.7759
0.8550
0.8924

0.8345
0.7946
0.7805▼
0.8503
0.8930

0.8050
0.6255▼
0.6470▼
0.6480▼
0.6469▼

0.8240
0.6145▼
0.6455▼
0.6326▼
0.6510▼

0.8120
0.6190▼
0.6464▼
0.6370▼
0.6505▼

PERT [34]
ET-BERT [16]

0.9268
0.9503

0.9078
0.9462

0.9096
0.9489

0.9605
0.9930

0.9611
0.9930

0.9574
0.9930

0.9378
0.8927▼

0.9052
0.8674▼

0.8977
0.8467▼

0.8990
0.9450

0.8868
0.9423

0.8960
0.9435

0.8274▼
0.9021

0.7588▼
0.8920▼

0.7685▼
0.8995

TrafficLLM
0.9800
0.9861
0.9800
0.9950
0.9957
0.9950
0.9640
0.9640
0.9639
0.9820
0.9806
0.9810
0.9870
1 We use
▼ to mark the results of each baseline with a performance decrease of more than 10% compared to their best results among 5 malicious traffic detection tasks.

0.9823

0.9845

(a) TrafficLLM on Masked Features (b) Compared to ET-BERT and PERT
Fig. 6. The Macro-AUC of TrafficLLM and baselines with different ratios of
masked features on ISCX Tor 2016.

of 0.3890 on the EAC task (CSTNET 2023). Conversely,
TrafficLLM outperforms existing methods with an average F1score of 0.9875 and a variance of 0.018%, compared to the
pre-trained model ET-BERT’s 0.9324 average F1-score and
0.151% variance.
Robustness against masking features. To understand why
TrafficLLM keeps such generalization ability on traffic detection tasks, we randomly mask partial packet meta-information
in the inference stage to test detection performance. In Figure 6, results indicate that TrafficLLM can obtain a MacroAUC of 0.9171 even when 15% of features missing. However, the performance of pre-trained models ET-BERT and
PERT significantly declines. For instance, for a target FPR
= 1 × 10−1 , while TrafficLLM achieves a TPR of 0.90, both
two baselines provide TPRs less than 0.40. The robustness

(a) 5-Tuples JSD
(b) Destination IP JSD
Fig. 7. JSD between real and synthetic distributions on ISCX Botnet 2014
and USTC TFC 2016 (⇓ JSD is better).

against missing features comes from the pattern reasoning and
generalization abilities inherited from LLMs, while previous
work does not. Using the raw traffic data as inputs, TrafficLLM
does not heavily rely on the partial features. It benefits from the
ability to automatically learn the importance and relationships
of meta-information to the specific task to build generic traffic
representation, helping TrafficLLM release strong generalization across different scenarios.
B. Generalization across Generation Tasks
We evaluate TrafficLLM’s generation ability across different
scenarios and analyze the practicality of the generated traffic.
Distribution Metrics. To evaluate the performance of the
traffic generation capability, we compute the distribution metrics between the real and synthetic distribution of the metainformation in the packets. Figure 7 shows the results on
5-tuples compared to 3 baselines. We find that TrafficLLM

10

TABLE VII
T HE PERFORMANCE OF IDENTIFYING THE 2 K SYNTHETIC AND REAL PACKETS USING THE CLASSIFIERS BUILT FROM THE SAME SIZE OF REAL AND
SYNTHETIC DATA UNDER USTC TFC 2016, ISCX B OTNET 2014, ISCX VPN 2016, AND CSTNET 2023 DATASETS .
Setting1

Method

USTC TFC 2016

ISCX Botnet 2014

ISCX VPN 2016

CSTNET 2023

PR

RC

F1

PR

RC

F1

PR

RC

F1

PR

RC

F1

0.7825
0.7673
0.8178
0.9315

0.7432
0.7925
0.8157
0.8604

0.7453
0.7529
0.8042
0.8354

0.7234
0.8057
0.9021
0.9778

0.7421
0.8245
0.9105
0.9730

0.7256
0.8050
0.9042
0.9727

0.8196
0.8342
0.9859
0.9802

0.7945
0.8454
0.9675
0.9754

0.8204
0.8345
0.9734
0.9779

0.8402
0.8590
0.9314
0.9861

0.8794
0.8881
0.9146
0.9852

0.8571
0.8530
0.9345
0.9852

PAC-GAN [60]
0.6459
0.6375
0.6431
0.6204
0.6079
0.6202
0.8192
0.8023
0.8205
0.7056 0.6859
❷
PacketCGAN [61]
0.6724
0.6458
0.6532
0.7057
0.6894
0.6995
0.8525
0.8678
0.8548
0.6861 0.6404
S-Train
NetShare [44]
0.8521
0.8254
0.8322
0.7974
0.7854
0.8024
0.9045
0.8845
0.8964
0.8420 0.8299
R-Test
TrafficLLM
0.8843
0.8641
0.8589
0.8634
0.8375
0.8334
0.9716
0.9686
0.9688
0.8630
0.8289
1 Setting ❶ uses the real packets to train classifiers to test synthetic packets. Setting ❷ trains with synthetic packets and test on real packets.

0.6980
0.6489
0.8405
0.8340

PAC-GAN [60]
PacketCGAN [61]
NetShare [44]
TrafficLLM

❶
R-Train
S-Test

(a) No Drift

(b) Time Drift

(c) Version Drift

Fig. 9. Concept drift experiments with 1-month time drift and new App
version drift settings on APP-53 2023 datasets.
(a) Source port

(b) Packet length (bytes)

Fig. 8. Source port and packet length CDFs compared with baselines and the
ground truth on ISCX VPN 2016.

is at most 73.76% better than existing methods to degrade
the gap from the real distribution. For different categories of
benign and malicious traffic, TrafficLLM achieves an average
JSD of 0.0179, which is 39.32% better than the state-of-theart traffic generation method NetShare’s 0.0295 average JSD.
For a more detailed analysis, Figure 8 shows the CDFs of the
source port and packet length. Results indicate that existing
GAN-based methods can not capture the distribution well.
TrafficLLM’s memorization advantage from parameter volume
can help restore the field values of the original traffic data.
The results also indicate that TrafficLLM effectively learns
the fine-grained traffic representations to make the distribution
consistent with the ground truth.
Practicality of Synthetic Samples. TrafficLLM can rebuild the packets of raw traffic using the generated metainformation. Furthermore, we consider that the generation
ability of TrafficLLM has two promising applications: (i)
generating packets for security tests and (ii) building classifiers
under few-shot scenarios. First, to verify the quality of the
generated packets, we use 2k traffic traces of real datasets to
build a robust ensemble model based on Multinomial Naive
Bayesian and SGD classifiers to construct a prototype of
ML-based NIDS. Then we use the synthetic traces to test
whether the model can identify these packets. In Table VII,
we find that the generated packets of TrafficLLM can be
identified by the real-world classifier with an average F1score of 0.9483, which is 4.68% better than the state-of-theart method NetShare. It means that TrafficLLM can generate
test samples with extremely high confidence. To measure
the second application of TrafficLLM, we use 2k generated

(a) Stage-2 APT Attacks (b) Stage-3 APT Attacks (c) Stage-4 APT Attacks
Fig. 10. Future stage APT attack detection based on historical stage-1 APT
attack knowledge on DAPT 2020 datasets.

packets to build the classifiers and treat the real packets as
the test sets. Results indicate that TrafficLLM outperforms
baselines on most metrics to detect real-world traffic using
the classifiers built from synthetic data. TrafficLLM can be
applied in data augmentation for benign or malicious traffic
with a 0.8739 average F1-score, which is 3.07%-33.92% better
than baselines.
C. Generalization to Unseen Data
Unlike traditional ML-based methods, a salient property of
TrafficLLM is its generalization abilities on unseen data. We
utilize concept drift and APT attack datasets [42], [55] to set
up unseen data detection scenarios for evaluation.
Time and Version Drift. We evaluate TrafficLLM under concept drift [17] scenarios that the detecting traffic distribution
often shifts from the original training data over time due to
dynamic behaviors (e.g., application updating). In this setting,
we use the APP-53 2023 dataset, including 53-type mobile
App traffic and its drifted traffic with a 1-month time interval
and new App version updates. We train TrafficLLM on the
historical traffic and evaluate its generalization performance
on the no drift, 1-month time interval, and new App version
drift datasets. In Figure 9, TrafficLLM effectively maintains the
detection performance when facing the concept drift scenarios.
It outperforms baselines with 4.3%-11.3% and 6.7%-18.6%

11

(a) Avg. F1-Score

(b) False Positives

Fig. 11. Exploring the influence of the Pre-trained and traffic-domain
knowledge on the generalization ability.

(a) Robustness of Different LLMs

(b) Impact of LLM Parameter Size

Fig. 12. Different types and model sizes of LLM adapted in TrafficLLM.
The generation performance uses the R-Train and S-Test settings (the same
as below).

F1-score under time and version drift respectively. Since
TrafficLLM inherits the strong generalization from LLMs, it
captures the common traffic representations in drifted environments, which ensures the robustness of detecting unseen
drifted traffic.
APT Attack Detection. We then evaluate TrafficLM under
APT attacks [42] that the traffic contains unseen distribution
due to dynamic behavior changes of attackers. We evaluate it on the multi-stage APT attack detection tasks using
the DAPT 2020 dataset [42]. In this setting, the adversary
conducts 4-stage attacks including reconnaissance, foothold
establishment, lateral movement, and data exfiltration in a few
days. We train TrafficLLM with the benign and stage-1 APT
attack traffic and test it on the attacks of future stages. As
shown in Figure 10, results indicate that TrafficLLM achieves
89.3% average F1-score to detect future-stage attack traffic.
Although the attack traffic is extremely different in these stages
(e.g., stage-1 attack mainly aims to identify vulnerabilities
with attack tools, while the stage-4 attack contains the traffic
that downloading files from the victim server using C&C
tunnels), the pattern mining ability of TrafficLLM can differ the
representation of malicious traffic from the benign. This robust
anomaly detection ability helps TrafficLLM achieve better
generalization performance on the dynamic traffic distribution
compared to the three baselines.
Remark on Generalization Ability. To further analyze why
TrafficLLM keeps such generalization ability that traditional
ML-based methods do not have, we investigate the influence
of the capability from native base LLMs and tuned trafficdomain PEFT models. First, we randomly initialize LLM’s
weights to remove the pre-trained knowledge and directly tune
it with traffic datasets. We reuse the same settings of APP53 2023 and DAPT 2020 datasets and report the average F1score and FP. As shown in Figure 11, TrafficLLM dramatically
drops the performance without pre-trained knowledge. This
is because the pre-trained knowledge helps LLM acquire
pattern mining and reasoning abilities through massive corpora
(e.g., planning and calculation [23]), which is also critical
for traffic analysis. Second, we disable the traffic-domain
knowledge by removing PEFT models and directly testing
on the base model. Without any guidance of traffic-domain
knowledge, LLM tends to randomly generate labels, making it
not qualified for the work. However, when using 20% training
data to inject partial traffic-domain knowledge into LLMs,
TrafficLLM acquires great improvement on the unseen traffic
data. The domain knowledge helps LLM effectively activate
the generalization ability on the traffic data, building generic

(a) Traffic Detection (b) Traffic Generation (c) Computation Overhead
Fig. 13. The effectiveness of traffic-domain tokenization, dual-stage tuning
pipeline, and EA-PEFT in TrafficLLM.

traffic representations on unseen traffic.
D. Deep Dive
Adaptability across different LLMs. To verify whether
TraffiLLM is applicable to different LLMs, except for Llama2
and ChatGLM2, we employ additional state-of-the-art LLMs
to build TrafficLLM, which includes Vicuna [62], Mistral [32],
and Gemma [63]. As shown in Figure V-C, results indicate
that the framework of TraffiLLM can be easily applied to all
open-sourced LLMs with strong performance.
Impact of LLM Parameter Size. In Figure V-C, we explore the impact of LLM’s parameter size on traffic detection and generation performance. Although Llama2-13B
and ChatGLM2-12B’s parameter size is almost 2-fold that
of their 7B and 6B versions, the four LLMs achieve similar
performance. The 6B model is enough to outperform existing
ML-based baselines on traffic detection and generation tasks.
Effectiveness of Core Components. To validate the effectiveness of TrafficLLM’s core components, we build three TrafficLLM’s variants by removing the traffic-domain tokenizer (Tokenization), replacing the dual-stage tuning pipeline with
default tuning (- Dual-Stage), and replacing EA-PEFT scheme
with full fine-tuning (- EA-PEFT). As shown in Figure 13,
modifying these components will entail 7.2%-78.7% performance reduction and 927.9% time and 216.2% GPU memory
overhead increase among five LLMs mentioned above, which
indicates the significance of these components.
Overhead Analysis. We investigate TrafficLLM’s computation
overhead on a NVIDA A100-80GB GPU. Training a 6B
model like ChatGLM2-6B requires 23GB GPU memory and
14h training time for a new PEFT model update (involving
20,000 training steps on 50,000 task-specific samples). During
the inference stage, loading TrafficLLM requires 13GB GPU
memory and takes about 0.2s or 10s to generate a predicted
label or a 1000-token synthetic packet. To reduce the overhead,
we consider employing a smaller LLM or using compression
methods [64] can help speed up the adaptation.

12

(a) Evaluation on the ATEC 2023
(b) Enterprise Deployment
Fig. 14. Players’ model performance in the competition and detection
performance under enterprise deployment.

E. Real-World Evaluation
To evaluate the practicality in real-world scenarios, we
opened TrafficLLM’s framework for extensive security practitioners in an LLM competition and deployed TrafficLLM in
a top security company.
Individual Use Evaluation. To investigate TrafficLLM’s effectiveness in research and collect feedback from the community,
we integrate TrafficLLM as a race track on a national LLM
competition1 with 1,901 teams and over 3,000 players from
about 200 institutions from November 2023 to March 2024.
We have united many universities and Internet companies
to develop the competition platform. In this track, players
must use TrafficLLM’s framework with custom instructions
and traffic data to tackle MTD, BND, and EVD tasks. Each
player can train their model and submit it in our scoring system
online. At the end of the competition, we draw up the statistics
for all the players’ scores. As shown in Figure V-E, 58% of
players achieve above 90% accuracy in this competition. Even
24% of player models performed better than 96% Accuracy.
After extensive verification by players during the competition,
TrafficLLM was proven to adapt LLMs with powerful performance easily.
Enterprise Deployment. We deploy TrafficLLM in a security
company that offers signature-based WAF and NIDS services
to hundreds of its enterprise customers. The services are
operated by security specialists to record the daily malware
and Web attacks through manual analysis behind the services.
They generated the ground truth by matching the WAF rules
or manually analyzing the traffic log with abnormal behaviors
(e.g., containing attack payloads). We replay the recorded
traffic that contains 17,556 and 7,083 flows of malware and
Web attack traffic to conduct MTD and WAD tasks using
TrafficLLM. As shown in Figure V-E, TrafficLLM outperforms
baselines by reaching 98.7% and 99.8% F1-scores in the realworld MTD and WAD task. TrafficLLM effectively reduces at
least 69% and 95% of FPs compared to existing ML-based
methods. This is attributed to TrafficLLM’s robust representation learning to differ the pattern of benign and abnormal
traffic, making TrafficLLM release strong generalization in the
real-world scenario.
VI. R ELATED W ORK
Encrypted Traffic Classification. Encrypted traffic classification is a crucial technique for network management and
1 ATEC 2023 Website: https://www.atecup.cn/matchHome/100001

security monitoring. With the inability to inspect the content of
encrypted packets directly, researchers have turned to various
machine-learning algorithms [9], [11], [12] to analyze patterns,
timings, packet sizes, and other metadata to classify traffic.
For instance, Van et al. [9] used semi-supervised methods to
model device, certificate, and statistical features for mobile app
fingerprinting. Taylor et al. [12] utilized packet size to train
traffic classifiers with Random Forest. Fu et al. [11] exploited
flow interaction graphs to distinguish malicious behaviors from
benign traffic. Recent research [16], [34] focused more on
model generalization using pre-trained models. For instance,
Lin et al. [16] leveraged BERT to build the pre-trained model
for multi-type traffic classification tasks. However, existing
works only focus on handling traffic data. Unlike these works,
TrafficLLM jointly learns expert instructions and raw traffic
data, making TrafficLLM more powerful in various traffic
analysis tasks.
Traffic Data Augmentation. Data augmentation has been
widely applied in the few-shot scenarios of traffic analysis to
increase the amount and diversity of traffic data. For example,
Qing et al. [65] utilized distributions of traffic data in the
feature space to augment training data for model training. Jan
et al. [47] generated labeled datasets for botnet detection using
generative models. A bunch of prior works [44], [60], [61]
leveraged Generative Adversarial Nets (GANs) to synthesize
metadata in the traffic. Unlike these works, TrafficLLM can
generate entire packets including accurate headers and synthetic payloads based on traffic representation learning.
VII. C ONCLUSION
In this paper, we develop a powerful framework to adapt
LLMs for network traffic analysis with strong generalization.
TrafficLLM employs three core techniques including trafficdomain tokenization to process instructions and traffic data,
the dual-stage tuning pipeline to learn generic traffic representations with instructions and raw traffic data, and the
EA-PEFT technique to update model parameters for new
scenario adaptation. We evaluate TrafficLLM on 10 opensourced datasets. Extensive experiments indicate that TrafficLLM shows remarkable generalization abilities across different tasks and unseen traffic scenarios compared to existing
ML-based models. We release the source code and datasets to
facilitate future research and hope that TrafficLLM can serve
as the stepping stone for more LLM adaptation designs in the
traffic analysis community.
R EFERENCES
[1] S. Hu, T. Huang, K.-H. Chow, and et al., “Zipzap: Efficient training
of language models for large-scale fraud detection on blockchain,” in
WWW, 2024, pp. 2807–2816.
[2] Z. Fu, M. Liu, Y. Qin, and et al., “Encrypted malware traffic detection
via graph-based network analysis,” in RAID. USENIX Association,
2022, pp. 495–509.
[3] P. Li, Y. Wang, Q. Li, and et al., “Learning from limited heterogeneous
training data: Meta-learning for unsupervised zero-day web attack detection across web domains,” in CCS, 2023, pp. 1020–1034.
[4] G. Pellegrino, M. Johns, S. Koch, and et al., “Deemon: Detecting csrf
with dynamic analysis and property graphs,” in CCS. ACM, 2017, pp.
1757–1771.

13

[5] T. Bujlow, V. Carela-Español, and P. Barlet-Ros, “Independent comparison of popular dpi tools for traffic classification,” Computer Networks,
vol. 76, pp. 75–89, 2015.
[6] H. Shi, H. Li, D. Zhang, and et al., “An efficient feature generation
approach based on deep learning and feature selection techniques for
traffic classification,” Computer Networks, vol. 132, pp. 81–98, 2018.
[7] C. Systems, “Cisco secure network analytics,” https://www.cisco.com/
site/us/en/products/security/security-analytics/secure-network-analytics/
index.html, 2024.
[8] Rapid7, “Insightidr,” https://www.rapid7.com/products/insightidr/, 2024.
[9] T. Van Ede, R. Bortolameotti, A. Continella, and et al., “Flowprint: Semisupervised mobile-app fingerprinting on encrypted network traffic,” in
NDSS, vol. 27. The Internet Society, 2020.
[10] T. Wang, “High precision open-world website fingerprinting,” in SP.
IEEE, 2020, pp. 152–167.
[11] C. Fu, Q. Li, and K. Xu, “Detecting unknown encrypted malicious traffic
in real time via flow interaction graph analysis,” in NDSS. The Internet
Society, 2023.
[12] V. F. Taylor, R. Spolaor, M. Conti, and et al., “Robust smartphone app
identification via encrypted network traffic analysis,” IEEE Transactions
on Information Forensics and Security, vol. 13, no. 1, pp. 63–78, 2017.
[13] A. Panchenko, F. Lanze, J. Pennekamp, and et al., “Website fingerprinting at internet scale.” in NDSS. The Internet Society, 2016.
[14] K. Al-Naami, S. Chandra, A. Mustafa, and et al., “Adaptive encrypted
traffic fingerprinting with bi-directional dependence,” in ACSAC. ACM,
2016, pp. 177–188.
[15] Z. Meng, M. Wang, J. Bai, and et al., “Interpreting deep learning-based
networking systems,” in SIGCOMM. ACM, 2020, pp. 154–171.
[16] X. Lin, G. Xiong, G. Gou, and et al., “Et-bert: A contextualized
datagram representation with pre-training transformers for encrypted
traffic classification,” in WWW. ACM, 2022, pp. 633–642.
[17] L. Yang, W. Guo, Q. Hao, and et al., “{CADE}: Detecting and
explaining concept drift samples for security applications,” in USENIX
Security, 2021, pp. 2327–2344.
[18] R. Tang, Z. Yang, Z. Li, and et al., “Zerowall: Detecting zero-day
web attacks through encoder-decoder recurrent neural networks,” in
INFOCOM. IEEE, 2020, pp. 2479–2488.
[19] S. Guthula, N. Battula, R. Beltiukov, and et al., “netfound: Foundation
model for network security,” arXiv preprint arXiv:2310.17025, 2023.
[20] T. Brown, B. Mann, N. Ryder, and et al., “Language models are few-shot
learners,” in NeurIPS, 2020.
[21] OpenAI, “GPT-4 technical report,” arXiv preprint arXiv:2303.08774,
2023.
[22] H. Touvron, T. Lavril, G. Izacard, and et al., “Llama: Open and efficient
foundation language models,” arXiv preprint arXiv:2302.13971, 2023.
[23] H. Touvron, L. Martin, K. Stone, and et al., “Llama 2: Open foundation
and fine-tuned chat models,” arXiv preprint arXiv:2307.09288, 2023.
[24] A. Zeng, X. Liu, Z. Du, and et al., “GLM-130B: an open bilingual
pre-trained model,” in ICLR, 2023.
[25] J. Wei, X. Wang, D. Schuurmans, and et al., “Chain-of-thought prompting elicits reasoning in large language models,” in NeurIPS, 2022.
[26] W. X. Zhao, K. Zhou, J. Li, and et al., “A survey of large language
models,” arXiv preprint arXiv:2303.18223, 2023.
[27] D. Zhang, Y. Yu, J. Dong, and et al., “Mm-llms: Recent advances
in multimodal large language models,” in ACL.
Association for
Computational Linguistics, 2024, pp. 12 401–12 430.
[28] X. Liu, K. Ji, Y. Fu, and et al., “P-tuning v2: Prompt tuning can be
comparable to fine-tuning universally across scales and tasks,” arXiv
preprint arXiv:2110.07602, 2021.
[29] Meta, “Meta llama 3,” https://llama.meta.com/llama3/, 2024.
[30] Google, “Gemini - google deepmind,” https://deepmind.google/
technologies/gemini/, 2024.
[31] Anthropic, “Claude,” https://claude.ai/, 2024.
[32] A. Q. Jiang, A. Sablayrolles, A. Mensch, and et al., “Mistral 7b,” arXiv
preprint arXiv:2310.06825, 2023.
[33] B. AI, “Baichuan,” https://www.baichuan-ai.com/, 2024.
[34] H. Y. He, Z. G. Yang, and X. N. Chen, “Pert: Payload encoding
representation from transformer for encrypted traffic classification,” in
ITU K. IEEE, 2020, pp. 1–8.
[35] X. Meng, C. Lin, Y. Wang, and et al., “Netgpt: Generative pretrained
transformer for network traffic,” arXiv preprint arXiv:2304.09513, 2023.
[36] Q. Wang, C. Qian, X. Li, and et al., “Lens: A foundation model
for network traffic in cybersecurity,” arXiv preprint arXiv:2402.03646,
2024.
[37] J. Devlin, M. Chang, K. Lee, and et al., “BERT: pre-training of deep
bidirectional transformers for language understanding,” in NAACL-HLT.
Association for Computational Linguistics, 2019, pp. 4171–4186.

[38] J. Wei, Y. Tay, R. Bommasani, and et al., “Emergent abilities of large
language models,” Transaction of Machine Learning Research, 2022.
[39] P. Liu, W. Yuan, J. Fu, and et al., “Pre-train, prompt, and predict: A
systematic survey of prompting methods in natural language processing,”
ACM Computing Surveys, vol. 55, no. 9, pp. 1–35, 2023.
[40] W. Wang, M. Zhu, X. Zeng, and et al., “Malware traffic classification
using convolutional neural network for representation learning,” in
ICOIN. IEEE, 2017, pp. 712–717.
[41] C. Liu, L. He, G. Xiong, and et al., “Fs-net: A flow sequence network
for encrypted traffic classification,” in INFOCOM. IEEE, 2019, pp.
1171–1179.
[42] S. Myneni, A. Chowdhary, A. Sabur, and et al., “Dapt 2020-constructing
a benchmark dataset for advanced persistent threats,” in DMLSD.
Springer, 2020, pp. 138–163.
[43] ArcSight, “Enterprise security manager,” https://www.microfocus.com/
en-us/cyberres/secops/arcsightesm, 2023.
[44] Y. Yin, Z. Lin, M. Jin, and et al., “Practical gan-based synthetic ip
header trace generation using netshare,” in SIGCOMM. ACM, 2022,
pp. 458–472.
[45] M. Lotfollahi, M. Jafari Siavoshani, R. Shirali Hossein Zade, and et al.,
“Deep packet: A novel approach for encrypted traffic classification using
deep learning,” Soft Computing, vol. 24, no. 3, pp. 1999–2012, 2020.
[46] E. B. Beigi, H. H. Jazi, N. Stakhanova, and et al., “Towards effective feature selection in machine learning-based botnet detection approaches,”
in CNS. IEEE, 2014, pp. 247–255.
[47] S. T. Jan, Q. Hao, T. Hu, and et al., “Throwing darts in the dark?
detecting bots with limited data using neural data augmentation,” in SP.
IEEE, 2020, pp. 1190–1206.
[48] P. Sirinam, M. Imani, M. Juarez, and et al., “Deep fingerprinting:
Undermining website fingerprinting defenses with deep learning,” in
CCS. ACM, 2018, pp. 1928–1943.
[49] N. Ding, Y. Qin, G. Yang, and et al., “Parameter-efficient fine-tuning of
large-scale pre-trained language models,” Nature Machine Intelligence,
vol. 5, no. 3, pp. 220–235, 2023.
[50] M. MontazeriShatoori, L. Davidson, G. Kaur, and et al., “Detection
of doh tunnels using time-series classification of encrypted traffic,” in
CyberSciTech. IEEE, 2020, pp. 63–70.
[51] C. . Dataset, “Csic,” http://www.isi.csic.es/dataset/, 2024.
[52] G. D. Gil, A. H. Lashkari, M. Mamun, and et al., “Characterization
of encrypted and vpn traffic using time-related features,” in ICISSP.
SciTePress, 2016, pp. 407–414.
[53] A. H. Lashkari, G. D. Gil, M. S. I. Mamun, and et al., “Characterization
of tor traffic using time based features,” in ICISSP, vol. 2. SciTePress,
2017, pp. 253–262.
[54] X. Zhao, X. Deng, Q. Li, and et al., “Towards fine-grained webpage
fingerprinting at scale,” in CCS 2024. ACM, 2024, pp. 423–436.
[55] M. Jiang, M. Cui, C. Liu, and et al., “Zero-relabelling mobile-app identification over drifted encrypted network traffic,” Computer Networks,
vol. 228, p. 109728, 2023.
[56] OpenAI, “Chatgpt,” https://chat.openai.com/, 2024.
[57] J. Hayes and G. Danezis, “k-fingerprinting: A robust scalable website
fingerprinting technique,” in USENIX Security. USENIX Association,
2016, pp. 1187–1203.
[58] M. Shen, J. Zhang, L. Zhu, and et al., “Accurate decentralized application identification via encrypted traffic analysis using graph neural
networks,” IEEE Transactions on Information Forensics and Security,
vol. 16, pp. 2367–2380, 2021.
[59] K. Lin, X. Xu, and H. Gao, “Tscrnn: A novel classification scheme
of encrypted traffic based on flow spatiotemporal features for efficient
management of iiot,” Computer Networks, vol. 190, p. 107974, 2021.
[60] A. Cheng, “Pac-gan: Packet generation of network traffic using generative adversarial networks,” in IEMCON. IEEE, 2019, pp. 0728–0734.
[61] P. Wang, S. Li, F. Ye, and et al., “Packetcgan: Exploratory study of
class imbalance for encrypted traffic classification using cgan,” in ICC.
IEEE, 2020, pp. 1–7.
[62] W.-L. Chiang, Z. Li, Z. Lin, and et al., “Vicuna: An open-source
chatbot impressing gpt-4 with 90%* chatgpt quality,” March 2023.
[Online]. Available: https://lmsys.org/blog/2023-03-30-vicuna/
[63] G. Team, T. Mesnard, C. Hardin, and et al., “Gemma: Open
models based on gemini research and technology,” arXiv preprint
arXiv:2403.08295, 2024.
[64] C. Xu and J. McAuley, “A survey on model compression and acceleration for pretrained language models,” in AAAI, vol. 37, no. 9, 2023, pp.
10 566–10 575.
[65] Y. Qing, Q. Yin, X. Deng, and et al., “Low-quality training data only?
a robust framework for detecting encrypted malicious network traffic,”
in SP. IEEE, 2023.

14

[66] H. Zhang, L. Yu, X. Xiao, and et al., “TFE-GNN: A temporal fusion
encoder using graph neural networks for fine-grained encrypted traffic
classification,” in WWW. ACM, 2023, pp. 2066–2075.
[67] Docker, “Docker: Accelerated container application development,” https:
//www.docker.com/, 2024.
[68] X. Yang, S. Ruan, Y. Yue, and et al., “Petnet: Plaintext-aware encrypted
traffic detection network for identifying cobalt strike https traffics,”
Computer Networks, vol. 238, p. 110120, 2024.
[69] Scapy, “Scapy community,” https://scapy.net/, 2024.
[70] W. Foundation, “Wireshark - go deep,” https://www.wireshark.org/,
2024.
[71] Z. Ji, N. Lee, R. Frieske, and et al., “Survey of hallucination in natural
language generation,” ACM Computing Survey, vol. 55, no. 12, pp.
248:1–248:38, 2023.

A PPENDIX A
O PEN S CIENCE & E THICAL C ONSIDERATIONS
A. Open Science
To facilitate future research to adapt LLMs in the traffic analysis domain, we release the source code of TrafficLLM and the datasets at https://github.com/ZGC-LLMSafety/TrafficLLM. The dataset consists of over 0.4M tuning
data that include human instructions and traffic features supervised by manual annotation. To the best of our knowledge, this
is the largest LLM adaptation dataset for traffic domain to date.
To enhance the reproducibility of our work, we mainly use
open-sourced datasets and LLMs to conduct the experiments in
this paper. All the original traffic data and LLMs are publicly
available in their released repositories.
B. Ethical Considerations
In this paper, we discuss ethical considerations about dataset
construction, human evaluation, and real-world deployment.
Dataset Construction. We leverage the human instruction and
traffic data to construct the tuning data for LLM adaptation.
The released traffic data are all extracted from the opensourced datasets. For the natural language instruction dataset,
we invite five network security practitioners and students to
generate task-specific instructions with manual annotation and
AI assistance. The instructions are required not including
corporate confidentiality and privacy data. We have submitted
the data review material to our institutional ethics review body
(IRB). Our work has been approved by IRB to ensure ethical
soundness and justification.
Individual Use Evaluation. We evaluate TrafficLLM’s effectiveness with extensive participation of players in the national
LLM competition. All the players have signed an informed
consent agreement to allow us to collect the competition
data. In the competition system, each player is assigned a
model submitter ID. We did not over-explore data involving
personal information and designed a detailed exit mechanism
to remove user records only necessary statistical data used
in our experiments. The released statistical data has been
approved by the competition organizer and IRB.
Enterprise Deployment. The recorded traffic has been
anonymized and only contains necessary meta-information that
is helpful for traffic detection. Any fields containing sensitive
user information have been removed. We do not use the traffic
data to identify individuals. All the traffic data used in the realworld evaluation has been approved by the company’s IRB.

The experiments are conducted in an isolated environment. We
further guarantee that our evaluation process does not disrupt
or harm other hosts or targets.
Instruction Examples of Different Tasks
TBD Task Instruction: The Tor network transmits
traffic through multiple layers of encryption and relay nodes, providing users with online privacy and
anonymity. Please classify the traffic application or
behavior according to the traffic data I provided.
EAC Task Instruction: Hi, I have noticed at home
that my children spend a lot of time online and worry
that they may be exposed to unsafe apps. I have
obtained some network traffic data. Please help to
analyze it to determine which applications the children
are accessing.
MDD Task Instruction: The traffic may be DoH data
generated by an encrypted DNS server. Please help me
determine whether it contains malicious DoH behavior.
WAD Task Instruction: Analyze the pattern characteristics of the Web request data and determine whether
it contains malicious attacks.
BND Task Instruction: The traffic data generated by
the communication between the server and the client
is obviously different from that of the normal network.
The data is shown as follows. Please guess the botnet
type to which this data belongs.
MTD Task Instruction: I have a piece of traffic data
that may be malicious software communication behavior, but I don’t know the specific software type behind
the traffic. Could you provide more information?
EVD Task Instruction: I have used a specific encrypted VPN protocol to transmit the traffic generated
by an application. Please check the application type in
the traffic.
CD Task Instruction: I would like you to help analyze
the following unknown traffic, determine whether there
is a concept drift phenomenon, and identify the type
of the traffic. Please note that the unknown patterns
that may result from version updates require special
attention.

A PPENDIX B
D ETAILS OF LLM I NVESTIGATION
We investigate the capabilities of existing LLMs and earlier
PLMs to achieve the traffic analysis tasks in Section II. For
a more detailed study of existing LLMs, Table VIII shows
examples of 3 state-of-the-art LLMs’ responses to traffic
analysis instructions. We can see that existing LLMs tend
to give random guesses, only descriptions of the traffic data,
or only recommendations of manual steps when receiving 2
types of traffic analysis instructions. For instance, when facing
a traffic detection instruction of EAC or MTD tasks, native
LLM usually generate a random label based on its knowledge
(e.g., Alipay), give a detailed description of the traffic features
(e.g., IP and protocol), and give a recommendation to use

15

TABLE VIII
E XAMPLES OF G EMINI (G EMINI 1.5), C LAUDE (C LAUDE 3 S ONNET ), AND C HAT GPT (GPT-4)’ S RESPONSES TO THE INSTRUCTIONS FOR CONDUCTING
TRAFFIC DETECTION AND TRAFFIC GENERATION TASKS .

Traffic Generation

Traffic Detection

Task

Instruction

Response

❶ Please conduct the ENCRYPTED APP
CLASSIFICATION TASK to determine
which APP category the encrypted traffic
belongs to. The categories include ’Adobe,
Alipay, ..., and Booking’. ¡packet¿: 04d9...
[Encrypted App Classification]

Gemini: Based on the provided traffic
data, the predicted app category is: Alipay.
Explanation: The packet size and structure
may resemble previously observed patterns
associated with Alipay’s protocols ...
[Random Guess]

Claude: The most likely app category for
the provided encrypted traffic is Apple.
The packet data contains patterns and
characteristics that strongly suggest the
traffic is related to Apple services ...
[Random Guess]

ChatGPT: To determine which class
encrypted traffic belongs to based on
packet data, a detailed analysis of
patterns and features within the
encrypted traffic itself is required ...
[Only Recommendations]

❷ The following is a segment of network
traffic data, you need to analyze whether it
is generated by the communication behavior
of malware. If so, please categorize it as
Cridex, Geodo, ..., and Zeus. ¡packet¿: 04...
[Malware Traffic Detection]

Gemini: The provided packet snippet
appears to be a DNS query, but without
additional context and analysis, it’s difficult
to definitively determine if it’s generated
by malware. However, we can examine ...
[Only Description]

Claude: Without additional context or
analysis, it’s difficult to definitively
determine if this specific packet is generated by malware communication behavior.
However, I can provide an overview ...
[Only Description]

ChatGPT: Considering the DNS query
characteristics, and without additional
payload decryption or further traffic
analysis, this packet could be related
to families like Zeus or Shifu ...
[Random Guess]

❶ Based on the protocol of fields, traffic
features, and payloads of different types of
traffic in your knowledge. Please generate
a packet of YouTube with the pcap format.
[Youtube Traffic Generation]

Gemini: Due to the limitations of my
knowledge cutoff and the dynamic nature of
YouTube traffic, I cannot directly generate a
specific packet in hexadecimal format ...
[Only Recommendations]

Claude: Unfortunately, I cannot generate
packet capture (pcap) files or raw network
traffic data. As an AI assistant without
direct access to network devices or the ...
[Only Recommendations]

ChatGPT: IP Header: Source IP: 192.16
8.1.2, Destination IP: 216.58.214.14, Protocol: TCP, TCP Header: Source Port:
49152, Destination Port: 443, Flags: ...
[Random Generation]

❷ I need a packet of Weibo traffic. Based
on Weibo’s traffic feature, please provide
me with a packet of Weibo’s traffic
data with the pcap format.
[Weibo Traffic Generation]

Gemini: Unfortunately, due to limitations
in my capabilities and knowledge cutoff, I
cannot directly generate a pcap file
containing Weibo traffic. However, ...
[Only Recommendations]

Claude: I’m afraid I cannot provide
you with an actual packet capture (pcap)
file containing Weibo traffic data.
As an AI assistant without direct access ...
[Only Recommendations]

ChatGPT: To obtain a real packet of
Weibo’s traffic in PCAP format, you
would typically use a network traffic
capturing tool like Wireshark ...
[Only Recommendations]

Wireshark or other network traffic analyzer. This investigation
demonstrates that existing LLMs still cannot obtain accurate
results for traffic detection and generation.
A PPENDIX C
D ETAILS OF E XPERIMENTAL S ETTINGS
A. Instruction Dataset
The human instructions for LLM adaptation are constructed
by 5 experts in the network security industries and PH.D. students majoring in cybersecurity. They are required to generate
instruction templates using domain knowledge across different
traffic detection and generation tasks and extend the scale
via generative AI assistants. We generate expert instructions
according to the backgrounds of 10 traffic classification tasks
and 229 types of traffic generation tasks. After collecting
professional instructions with extensive traffic-domain knowledge from security experts, we use them as templates for AI
assistants to supplement the instruction dataset. We collect
diverse AI-generated instructions using ChatGPT [56] with a
rewrite instruction like ‘The following is a traffic analysis instruction provided by network security experts. Please consider
different scenarios, security goals, question subjects, writing
styles, and text descriptions. Rewrite the following instructions
and generate 20 new different traffic analysis instructions’. All
the generated instructions have been supervised by manual
annotation. We removed the overlapped text and mistakes. We
released all our collected traffic-domain instructions for future
research. We show instruction examples of partial tasks.
B. Description of Baselines
In this paper, we compare the performance of TrafficLLM
with 15 baselines across different tasks, including state-of-theart traffic detection and generation algorithms.
Traffic Detection. The following provides an overview of the
traffic classification baseline used in our evaluation.

AppScanner [12]. AppScanner is a statistical feature
method using 54 statistical features for smartphone App
identification based on ML models.
• CUMUL [13]. CUMUL extracts packet size, direction,
and ordering features for website fingerprinting on the Tor
network.
• BIND [14]. BIND uses bi-directional burst features for
encrypted traffic fingerprinting in a wide range.
• k-fingerprinting (K-FP) [57]. K-FP extracts the most important features using random forests for large-scale traffic
classification.
• FlowPrint [9]. FlowPrint extracts statistical features for encrypted traffic classification tasks using the semi-supervised
clustering method.
• FS-Net [41]. FS-Net uses RNN models to learn packet
length sequences for traffic classification.
• Deep Fingerprinting (DF) [48]. DF uses deep Convolutional Neural Networks to realize website fingerprinting.
• GraphDApp [58]. GraphDApp extracts traffic interaction
graphs and uses Graph Neural Networks to detect traffic.
• TSCRNN [59]. TSCRNN combines CNN and RNN to
extract abstract features of the flow for traffic classification.
• Deeppacket [45]. Deeppacket uses deep Convolutional Neural Networks to realize encrypted traffic classification.
• PERT [34]. PERT uses a Transformer-based encoder and
pre-training technique to learn traffic representation.
• ET-BERT [16]. ET-BERT pre-trains BERT with large-scale
traffic to realize traffic classification across different tasks.
•

Traffic Generation. We use the following traffic generation
algorithms as the baselines in the experiments.
Netshare [44]. Netshare uses the GAN-based method to
generate IP header traces at a large scale.
• PacketCGAN [60]. PacketCGAN uses conditional GANs
to generate the encrypted traffic using bit vectors.
• PAC-GAN [61]. PAC-GAN uses CNN GAN to encode
packets into images and use them to generate packets.
•

Note that we choose these representative methods to cover a

16

(a) 5-Class packets generated from ISCX Botnet 2014
(b) 10-Class packets generated from CSTNET 2023
Fig. 15. Entropy analysis of synthetic packets on ISCX Botnet 2014 and CSTNET 2023. In each index, a higher entropy score (red) refers to more diverse
nybbles generated; A lower entropy score (blue) refers to more fixed nybbles generated.

TABLE IX
T HE DETAILS OF TRAFFIC DATA IN THE EVALUATION UNDER THE LLM
COMPETITION AND ENTERPRISE DEPLOYMENT.
Experiment

Task

#Flows

#Packet

#Labels

Evaluation on
the LLM Competition

MTD
BND
EVD

2,855
16,930
1,025

9,458
52,278
3,392

20
5
19

Experiment

Task

#Malicious

#Benign

#Labels

Enterprise Deployment

MTD
WAD

17,556
7,083

219,450
215,323

2
2

wide range of traffic detection and generation tasks. To help
all baselines be evaluated reasonably, we use the raw traffic
data for most of datasets and preprocess them following the
baselines’ instructions in their repositories. We contacted the
authors to obtain the datasets that do not open-source their
raw PCAP files. We keep similar setups to prior work [16],
[66] to evaluate baselines on different scenarios.
C. Real-World Evaluation Setup
Individual Use Evaluation Setup. To investigate the effectiveness of deploying TrafficLLM in the community, we
conduct an extensive evaluation of TrafficLLM by integrating
the framework as a track in a national LLM competition. In
this track, we collect the traffic including 20 types of malware,
5 types of botnets, and 19 types of VPN-encrypted Apps in our
experimental environments. The competition requires players
to build traffic-domain LLMs using TrafficLLM’s framework
with strong performance on all 3 tasks. Table IX shows the detail of the competition dataset to evaluate TrafficLLM. As one
of the organizers of the competition, we join the development
of the competition platform. The platform can run the model
image submitted by players and record the score on a realtime ranking web page. Each player is allocated an account
to log in to the fortress machine and access the development
machine to build their models. The players must upload their
Docker [67] images to the cloud environment to load GPU
servers. We use average accuracy (Acc) as the metric and build
the scoring procedures to update player ranking. At the end
of the competition, we analyze the overall performance of all
players to evaluate TrafficLLM’s practicality.
Enterprise Deployment Setup. In the real-world deployment
scenario, we implement TrafficLLM prototype and deploy it

in a top global security company. The company has supported
signature-based WAF and NIDS services for over 20 years.
It has provided security services for 100K+ enterprises. To
evaluate TrafficLLM’s practical performance, we collected
17,556 and 7,083 flows of malware and Web attack traffic
according to WAF rules hitting and manual analysis. The Web
attack traffic contains many attack payloads such as command
injection, which is different from normal user behavior of Web
applications. The malware traffic includes the communication
behavior of malware such as Cobalt Strike [68]. Otherwise,
the traffic that bypasses the rules and is confirmed by the
security engineers is considered benign traffic. Table IX shows
the detailed setting of the dataset. We build TrafficLLM and
its API in an isolated environment with a super GPU server.
We leverage TrafficLLM’s API to conduct MTD and WAD
tasks using its command mode. The security engineers report
F1-scores and false positives to evaluate the performance in
real-world scenarios.

A PPENDIX D
D ETAILS OF E VALUATION
A. Packet Generation
TrafficLLM can rebuild the raw traffic across different scenarios using the representation learned from the tuning stage.
Leveraging the generated fine-grained meta-information, TrafficLLM can be equipped with packet manipulation tools like
Scapy [69] to generate PCAP packets. These synthetic packets
follow standard formats that can be completely readable by
Wireshark [70]. TafficLLM does not directly generate the
Ethernet layer since it often varies depending on the different
types of physical devices at the viewpoints. We use Scapy to
synthesize a default Ethernet layer for every generated packet.
To further analyze the integrity of the generated packets,
Figure 15 shows the entropy analysis results of the packets
generated from ISCX Botnet 2014 and CSTNET 2023. We find
that TrafficLLM can learn fixed field values (e.g., TCP Flags)
effectively and imitate changed field values (e.g., Source and
Destination Port) according to the distribution in the dataset.
Moreover, TrafficLLM can capture the traffic characteristics for
different network scenarios. For instance, TrafficLLM keeps an
average entropy of 0.55 to generate the packet nybbles of the
target botnet (i.e., Virut, Neris, IRC, and RBot), while the
normal network is 0.64 due to the diversity of protocols.

17

(a) LLM Instruction Embeddings
(b) TrafficLLM Instructions
(c) LLM Traffic Embeddings
(d) TrafficLLM Traffic Embeddings
Fig. 16. The hidden state visualization of task instructions and traffic data in ChatGLM2 and TrafficLLM. TrafficLLM can learn better representations under
traffic detection instructions of EVD, BND, and MTD tasks and ISCX Tor 2016 traffic datasets.

TABLE X
T HE TASK UNDERSTANDING ABILITIES OF T RAFFIC LLM AND THE NATIVE
LLM BASED ON INSTRUCTIONS OF DOWNSTREAM TASKS .
Model

(a) RGE and SMS Metrics

(b) Top-p and Temperature

Fig. 17. Left: The ratio of generated errors (RGE) and the similarity of
misclassified samples (SMS) metric; Right: The performance of different topp and temperature.

B. Efficiency Evaluation
Model quantization [64] is a widely used technique to
deploy LLM-based systems in real-world scenarios. To further
evaluate TrafficLLM’s efficiency, we employ INT4 quantization to help TrafficLLM overcome LLM’s computation overhead and reach faster inference speed. We observe that TrafficLLM’s average prediction latency for a sample is 0.1408s,
which is 42% better than no quantization on TrafficLLM
(BF16). TrafficLLM only consumes 8.3GB memory, which is a
3.5-fold decrease. The performance has almost no degradation.
Additionally, we compare TrafficLLM’s inference latency with
existing ML-based models. TrafficLLM incurs lower detection
latency which is 3.51 times lower than that of the existing
method, i.e., FS-Net, which incurs 0.4950s per flow latency.
It is attributed to traffic-domain tokenization and quantization
techniques to achieve a significant reduction on the traffic input
and model overhead.
C. Hallucination Evaluation
LLM is prone to hallucination [71] due to the token generation with word sampling strategies. This may influence the
detection accuracy during the inference. In the hallucination
evaluation experiment, we collect the prediction results from
10 rounds of inference using the same test set. We define
the different responses for the same test sample input as the
generated errors. Figure 17-a shows the ratio of generated
errors in the misclassified samples and the average Jaccard
similarity between the misclassified samples and the dataset of
the misclassified label. Results indicate that 3.9% and 4.7%
of the misclassified output are generated errors on average
when using ChatGLM2 and Llama2 as the foundation model
in TrafficLLM. These misclassified samples usually keep a
high similarity (i.e., 82.4% and 81.5% on average) to the

Task

PR

RC

F1

Acc

Native LLM
(Llama2-7B)

Traffic Detection
Traffic Generation

0.4422
0.5776

0.6650
0.7600

0.5312
0.6564

0.6650
0.7600

TrafficLLM

Traffic Detection
Traffic Generation

0.9910
0.9935

0.9925
0.9960

0.9915
0.9940

0.9925
0.9960

datasets of misclassified labels, which we consider as the
reason for raising the hallucination issues. To address the
problem, Figure 17-b measures the performance of different
Top-p and Temperature parameters setting in the sampling
strategy. A higher Top-p and a lower Temperature parameter
can help the model keep strong confidence when predicting
labels and mitigate the hallucination in traffic detection.
D. Representation Learning
To further indicate the robustness of TrafficLLM on different
datasets, we show TrafficLLM’s robust traffic representation
in the vector space and evaluate its performance by using
different instructions.
Hidden State Visualization. To explain TrafficLLM’s ability
to learn text and traffic data, in Figure 16, we show the
visualization of TrafficLLM’s hidden state representation using T-SNE. Compared to the native LLM, TrafficLLM can
learn more distinguishable representations of different traffic
analysis instructions through instruction tuning. Moreover,
TrafficLLM also learns better traffic representation for each
class due to the task-specific traffic tuning with the specialized
traffic tokens. TrafficLLM’s traffic representations of each type
keep clearer boundaries in the feature space, which ensures
accuracy across different tasks.
Task Understanding. The representation learning ability helps
TrafficLLM correctly understand different task instructions
from security practitioners. In Table X, we compare TrafficLLM’s performance to the native Llama2-7B, which is
required to choose the correct task labels based on the instructions and given options across different detection and generation tasks. Results indicate that TrafficLLM has effectively
acquired the domain knowledge for traffic analysis, achieving
strong task understanding performance (0.9920 average F1score) to conduct different downstream tasks.
PAPER_TEXT
