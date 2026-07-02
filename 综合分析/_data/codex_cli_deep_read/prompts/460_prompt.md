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
# [460] Guest Editorial of the Special Section on Advances in Neural Computing-Enabled Device Health Management for Consumer Technology
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
编号：460
题名：Guest Editorial of the Special Section on Advances in Neural Computing-Enabled Device Health Management for Consumer Technology
年份：2025
DOI：10.1109/tce.2025.3595513
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3595513.pdf
已有粗分类：加密流量分类与应用识别
二级关联：无
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\460.txt
- 原始字符数：9709
- 本次发送字符数：9709
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

10651

Guest Editorial of the Special Section on Advances
in Neural Computing-Enabled Device Health
Management for Consumer Technology
ONSUMER technology has undergone an evolution from
simple manually operated devices to complex intelligent
systems that integrate seamlessly into daily life. The rapid
proliferation and integration of consumer technology in our
daily lives has brought about the need for more elaborative
development of health management systems to ensure device
reliability, resilience, and longevity. Unexpected failures of
consumer technology, including both hardware and software,
can lead to significant inconvenience in daily lives and work,
financial costs, health and safety risks for users, increased
warranty and repair costs, brand reputation damage, and legal
issues for manufacturers.
Challenges remain to realize highly adaptive, weaksupervision, efficient, and secure intelligence for consumer
technology health management. Neural computing-enabled
methods are increasingly being widely applied throughout different aspects of consumer technology. The learning
paradigm of neural computing-enabled methods has evolved
rapidly in recent years, from supervised learning, and
semi-supervised learning to unsupervised and self-supervised
learning. Therefore, breakthroughs have been witnessed
in various regression, classification, model updating and
optimization tasks, supported by different kinds of data such
as numeric sensor values, images, speech signals, texts, etc.
Advanced neural computing-enabled techniques, incorporated
with optimization, control theory, reliability and resilience
modeling, etc. are expected to form advanced health management methods for consumer electronics to avoid unexpected
failure, extend the life span, and reduce costs for consumers
and manufacturers.
Based on the above premises, this Special Section on
Advances in Neural Computing-enabled Device Health
Management for Consumer Technology focusing on consumer electronics health management, such as early anomaly
detection, fault diagnosis, remaining useful life (RUL)
prediction, predictive maintenance, usage recommendation,
reliability modeling, resilience analysis, personalized usage
pattern recommendation, etc. enabled by advanced neural
computing-enabled techniques. The Special Section was organized by several representative of the Technical Committees
of IEEE Consumer Technology Society in these areas
(https://ctsoc.ieee.org/technical.html). Overall, 14 submissions
were received spanning different consumer electronic (CE)

C

Digital Object Identifier 10.1109/TCE.2025.3595513

domains, which were prescreened and reviewed by experts in
the fields. At the end of the review process, 2 papers were
ultimately accepted.
The work in [A1] focuses on safety to protect patients
from potential risks in clinical trials using healthcare consumer electronics. Serious adverse events (SAEs) in clinical
trials may pose significant safety threats to patients and
incur substantial economic losses. To predict and prevent
SAEs, a universal dataset for Serious Adverse Events
prediction (SerAE) is built by aggregating trial protocol,
drug, and disease information from multiple data sources.
The dataset encompasses 10,643 clinical trials, 4,512 diseases, and 2,563 drugs. Furthermore, an Event-aware Dual
Representation model with mixture-of-Expert (EDRE) for serious adverse event prediction is proposed to achieve universal
prediction of SAEs. The experiments on SerAE demonstrate that EDRE significantly enhances the performance
in predicting SAEs compared to state-of-the-art baseline
models.
In [A2], a novel backbone network, referred to as multiscale
convolutional reservoir computing (MCRC), is proposed to
learn features in multiple time-scales for Li-ion battery
RUL prediction based on only previous capacity measurements. Li-ion batteries are widely employed as power
sources for consumer electronics, whose degradation is
complex and contains temporal dependencies in different timescales. The proposed MCRC employs convolutional filters
to extract multiscale temporal features, whose multiscale
sustained dependence are further captured by multiple reservoir layers. Benchmark and in-house experiments show
that the proposed MCRC can accurately predict RUL of
Li-ion batteries, outperforming other state-of-the-art backbone
networks.
In general, the above research topics include neural
networks, data modeling and prediction for health management. All of them focus on neural computing-enabled
technologies on consumer electronics.
A PPENDIX : R ELATED A RTICLES
[A1] B. Kan et al., “An event-aware dual representation model with mixtureof-experts for serious adverse events prediction in clinical trials,” IEEE
Trans. Consum. Electron., vol. 71, no. 2, pp. 3337–3346, May 2025,
doi: 10.1109/TCE.2025.3572452.
[A2] C. Li, G. Guo, and Z. Pu, “Multiscale convolutional reservoir computing for remaining useful life prediction of li-ion batteries,” IEEE
Trans. Consum. Electron., vol. 71, no. 2, pp. 3347–3356, May 2025,
doi: 10.1109/TCE.2025.3570594.

c 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
1558-4127 
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

10652

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

Y U WANG, Guest Editor
Department of Mechanical Engineering
Xi’an Jiaotong University
Xi’an 710049, China
E-mail: ywang95@xjtu.edu.cn

B IN Z HANG, Guest Editor
Department of Electrical Engineering
University of South Carolina
Columbia, SC 29208 USA
E-mail: zhangbin@cec.sc.edu

Z HE YANG, Guest Editor
Department of Mechanical Engineering
Dongguan University of Technology
Dongguan 523808, China
E-mail: yangz@dgut.edu.cn

YANXIA S UN, Guest Editor
Department of Electrical and Electronic Engineering Science
University of Johannesburg
Johannesburg 2092, South Africa
E-mail: ysun@uj.ac.za

Yu Wang (Senior Member, IEEE) received the B.Eng. degree in mechanical design and
manufacturing automation in 2005, the M.Eng. degree in manufacturing engineering and
automation in 2008, and the Ph.D. degree in systems engineering and engineering management
in 2014. From 2016 to 2018, he was a Postdoctoral Research Fellow with the Department of
Mechanical Engineering, University of California at Berkeley, Berkeley, CA, USA. His current
research interests include data mining, machine learning, reliability modeling and assessment, fault
prognostics, and health management. He has published over 100 technical papers in related fields.
He was the Program Co-Chair of several top conferences, including the International Conference
on Neural Computing for Advance Applications. He is currently an Associate Editor of the IEEE
ACCESS.

Zhe Yang (Member, IEEE) received the B.E. degree in measurement and control and instrument
and the M.Sc. degree in mechanical engineering from Xi’an Jiaotong University, Xi’an, China, in
2012 and 2015, respectively, and the Ph.D. degree in energy and nuclear science and technology
from the Politecnico di Milano, Milan, Italy, in 2020. From 2020 to 2022, he was a Postdoctoral
Research Fellow with the Department of Mechanical Engineering, Xi’an Jiaotong University,
Xi’an, China. Since 2022, he has been with the Dongguan University of Technology, Dongguan,
China, where he is currently an Associate Professor of Industrial Engineering with the School
of Mechanical Engineering. His research interests include prognostics and health management
of industrial equipment, machine learning, combinatorial optimization, and intelligent monitoring
systems.

Bin Zhang (Senior Member, IEEE) received the B.E. and M.E. degrees in mechanical
engineering from the Nanjing University of Science and Technology, Nanjing, China, in 1993 and
1999, respectively, and the Ph.D. degree in electrical engineering from Nanyang Technological
University, Singapore, in 2007. He is currently an Associate Professor with the Department of
Electrical Engineering, University of South Carolina, Columbia, SC, USA. He was with Research
and Development, General Motors, Detroit, MI, USA; Impact Technologies, Rochester, NY, USA;
and the Georgia Institute of Technology, Atlanta, GA, USA. His current research interests include
prognostics and health management, intelligent systems and controls, and their applications to
various engineering systems. He is currently an Associate Editor of IEEE T RANSACTIONS ON
AUTOMATION S CIENCE AND E NGINEERING and Neurocomputing.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS

10653

Yanxia Sun (Senior Member, IEEE) received the D.Tech. degree in electrical engineering from
the Tshwane University of Technology, South Africa, and the Ph.D. degree in computer science
from University Paris-EST, France, in 2012. She is currently a Professor with the Department
of Electrical and Electronic Engineering Science, University of Johannesburg, South Africa. Her
research interests are deeply rooted in the development of nature-inspired optimization algorithms,
multiobjective evolutionary optimization, and the application of deep learning in health and
engineering. Her contributions to her field are recognized globally, marked by her inclusion in
the World’s Top 2% Scientists by citations in 2023. Her leadership extends beyond teaching
and research; she actively participates in academic and industry collaborations, contributing to
advancements in engineering education and practice internationally.
PAPER_TEXT
