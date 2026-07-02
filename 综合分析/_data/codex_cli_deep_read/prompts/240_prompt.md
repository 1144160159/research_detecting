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
# [240] Guest Editorial Introduction to the Special Section on Open Radio Access Networks: Architecture, Challenges, Opportunities, and Use Cases in Vehicular Networks
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
编号：240
题名：Guest Editorial Introduction to the Special Section on Open Radio Access Networks: Architecture, Challenges, Opportunities, and Use Cases in Vehicular Networks
年份：2024
DOI：10.1109/tvt.2024.3399470
来源：IEEE Transactions on Vehicular Technology
PDF：paper/10.1109_TVT.2024.3399470.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：无
相关性：中相关，分数 7
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\240.txt
- 原始字符数：18775
- 本次发送字符数：18775
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 73, NO. 7, JULY 2024

9221

Guest Editorial
Introduction to the Special Section on Open Radio
Access Networks: Architecture, Challenges,
Opportunities, and Use Cases in Vehicular Networks
ELLULAR vehicle-to-everything (C-V2X) was introduced to support autonomous driving through 5G and beyond networks. C-V2X leverages cellular network infrastructure
to integrate vehicle-to-network, vehicle-to-pedestrian, vehicleto-infrastructure, and vehicle-to-vehicle communications. It
has been suggested that Open RAN can be used to achieve the
latency requirements essential to realize C-V2X as it achieves
real-time optimization through the use of AI in Near real-time
RAN Intelligence Controller (Near-RT RIC). The Open RAN
will allow the access to historical traffic data or acquisition of
data from vehicles. The data will then be transferred to Near-RT
RIC for detecting network anomalies while maintaining reliable
communication, which is essential for realizing autonomous
driving. Open RAN also supports non-real-time RAN intelligent
controller (Non-RT RIC) that allows more complex ML workflows such as policy-based feature extraction and optimization
to guide vehicles when real-time acquisition is not available.
Open RAN provides support for edge cloud, i.e. Open Cloud
that helps to interface the Near-RT RIC with Open RAN central
unit’s user and control plane. Together, the Open RAN and
C-V2X are considered to be the key-enabling technologies for
achieving low-latency in autonomous vehicular communication
networks. The issue attracted over 100 high-quality submissions
from all over the world, among which 12 original contributions
were eventually selected for publication. The novelty and key
contributions of these articles are summarized as follows.
The study by Houran et al. under the title, “Intelligent Reflecting Surfaces Assisted Cellular V2X based Open RAN
Communications”, proposed a method to improve data transmission in cellular vehicle-to-everything communication using
Open RAN and intelligent reflecting surfaces (IRS). The system utilizes clustering and a trellis search algorithm to select
the optimal IRS configuration to maximize signal strength between the base station and vehicles. Simulation results show
this method outperforms existing techniques in multi-hop IRS
communication.
The study by Kumar et al., under the title, “Secure Data Dissemination Scheme for Digital Twin Empowered Vehicular Networks in Open RAN”, presnted a new framework called STIoV is

C

Date of current version 16 July 2024.
Digital Object Identifier 10.1109/TVT.2024.3399470

proposed to secure communication in IoV networks using Open
RANs. STIoV addresses challenges like unverified transactions
and data tampering through mutual authentication, reputation
scoring, digital twins, and intrusion detection. Evaluations show
STIoV’s effectiveness compared to existing solutions..
The research proposed a framework for managing UAVs in
WSNs for smart agriculture. The framework uses multi-agent
deep reinforcement learning to schedule tasks, plan trajectories,
and share resources among UAVs. This approach aims to minimize energy consumption and network latency while collecting
data from sensor nodes. Simulation results show significant improvement over existing methods, the study by Betalo et al. under the title, “Multi-agent Deep Reinforcement Learning-based
Task Scheduling and Resource Sharing for O-RAN-empowered
Multi-UAV-assisted Wireless Sensor Networks”.
The study by Sun et al. proposed a a new framework called
Distilling for Sparse-Meta-transfer Learning (DSML) to address
the challenge of limited labeled data in Open RAN-based Cellular Vehicle-to-Everything (CV2x) systems. DSML combines
meta-transfer learning with knowledge distillation and sparseMAML techniques to improve generalization capability and reduce catastrophic forgetting. The proposed method outperforms
existing approaches in univariate time series classification tasks,
making it suitable for CV2x applications.
The study by Cui et al. under the title, “O-RAN Slicing for
Multi-Service Resource Allocation in Vehicular Networks”, discussed traditional resource allocation struggles with the growing
variety of V2X applications with different needs. This paper
proposes a new multi-service strategy for Open RAN-based
V2X. It splits resource allocation into two steps: allocating
resources between service types and scheduling resources within
each type. This allows for specialized scheduling for real-time
and non-real-time services, improving both service quality and
data transmission rates compared to existing methods.
The study by Cao et al. under the title, “Efficient Resource
Allocation of Slicing Services in Softwarized Space-AerialGround Integrated Networks for Seamless and Open Access
Services”, proposes a framework called Slice-Soft-SAGIN for
managing resources in future 6 G networks that integrate
space, aerial, and ground networks. Traditional networks offer
limited 2D coverage. 6 G with network softwarization (NetSoft) allows flexible resource allocation and service creation.

0018-9545 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

9222

Slice-Soft-SAGIN allocates resources across different network
types (ground, aerial, satellite) and considers both wireless and
wired resources to optimize service delivery for various network slices. The framework’s effectiveness is verified through
evaluations.
The study by Raja et al. under the title, “UGEN: UAV
and GAN-aided Ensemble Network for Post-Disaster Survivor Detection through ORAN”, proposed a deep-learning and
blockchain enabled secure data processing framework for an
edge-enabled green and connected autonomous vehicles. In
the proposed scheme, the blockchain ensures the reliability
of the vehicles added into the network and the deep learning
model is used to detect the intruders in the edge computing
environment.
The study by Dalgitsis et al.. under the title, “Cloud-native
orchestration framework for network slice federation across
administrative domains in 5 G/6 G mobile networks” proposes
with advancements in C-V2X and edge computing, network
slicing is crucial for guaranteeing performance in connected
vehicles. However, maintaining network slices as vehicles move
between operators is a challenge. This paper proposes a new
framework for network slice federation that allows operators
to share resources and maintain consistent slice service for
vehicles. The approach is validated through a cloud-native experimental platform showing successful federation and the impact
of operator strategies on performance.
The proposed work by Amponis et al. discuss improvements
to the QUIC protocol for better data transfer in C-V2X communication using aerial drones. Standard QUIC struggles with frequent network changes in these scenarios. The proposed method
adjusts data transfer based on real-time channel conditions,
improving performance for C-V2X applications in Open RAN.
This paves the way for reliable low-latency communication for
autonomous vehicles and future vehicular services.
El Houda et al. proposes a new framework that combines federated learning and deep reinforcement learning to address these
limitations. The approach enables distributed training on local
data while achieving high accuracy and efficiency in jamming
attack detection for Open RAN
Linsalata et al. proposes a new architecture to improve communication between vehicles (V2X) using Open RAN (ORAN). Traditional RANs lack the flexibility for V2X, but
O-RAN offers a solution. The challenge is integrating them
seamlessly. This architecture uses a separate low-frequency
O-RAN control plane to manage high-frequency V2X communication between autonomous vehicles. Simulations show
this approach improves reliability by up to 60% for V2X
communication.

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 73, NO. 7, JULY 2024

The research work presented by Sroka et al. addresses challenges in communication between vehicles (V2X) due to varying
service needs and network changes. It proposes Open Radio
Access Network (O-RAN) as a solution. O-RAN uses RAN
Intelligent Controllers (RICs) to intelligently manage resources
for V2X. By leveraging O-RAN’s flexibility and special traffic
information, the study shows optimized traffic management and
resource allocation in V2X scenarios, making O-RAN a good
fit for future V2X communication.
KAPAL DEV, Guest Editor
Department of Computer Science
Munster Technological University, Bishopstown
T12P928, Ireland
kapal.dev@ieee.org
CHIH-LIN I, Guest Editor
China Mobile Research Institute
China
icl@chinamobile.com

VUK MAROJEVIC, Guest Editor
Electrical and Computer Engineering
Starkville, MS 39762 USA
vuk.marojevic@ece.msstate.edu

SUNDER ALI KHOWAJA, Guest Editor
Faculty of Engineering and Technology
University of Sindh, Jamshoro 76080
Pakistan
sandar.ali@usindh.edu.pk

SHAO-YU LIEN, Guest Editor
National Chung Cheng University
Chiayi 621301, Taiwan
sylien@ccu.edu.tw

YUE WANG, Guest Editor
Samsung Electronics R&D Institute
Staines TW18 4QE, U.K.
yue2.wang@samsung.com

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 73, NO. 7, JULY 2024

9223

Kapal Dev (Senior Member, IEEE) received the Ph.D. degree from Politecnico di Milano, Milan,
Italy, in 2019. He is currently an Assistant Lecturer with the Department of Computer Science,
Munster Technological University (MTU), Ireland, and formerly he was Senior Researcher with
the same University. He was a Postdoctoral Research Fellow with the CONNECT Centre, School
of Computer Science and Statistics, Trinity College Dublin, Dublin, Ireland. He was a 5G Junior
Consultant and Engineer with Altran Italia S.p.A, Milan, Italy on 5G use cases. He worked
for OCEANS Network as Head of Projects funded by the European Commission. His research
interests include wireless communication networks, blockchain, and artificial intelligence. He
was awarded the Ph.D. degree by Politecnico di Milano, in 2019 under the prestigious fellowship
of Erasmus Mundus funded by the European Commission. He was the recipient of IEEE ComSoc
EMEA Outstanding Young Researcher 2022 for promising research activities for the benefit of
the Society. He was the recipient of The Tom Brazil Excellence in Research Award 2023 from
SFI Funded CONNECT Research centre. He was the recipient of 2022 Irish Research Council
Research Ally Prize for his mentoring/supervison services. He is among the top 45 researchers/scientist selected as a member of the
Global Young Academy (GYA) 2024 in the world. He was also the recipient of the Best workshop Paper Award at the prestigious
IEEE WCNC 2024 conference, IEEE ComSoc Excellent Reviewer Award from IEEE TRANSACTIONS ON NETWORK SCIENCE AND
ENGINEERING journal in 2022. He recently delivered invited talk on Unlocking the Future: Exploring the Enchanting Possibilities
of 6 G under IEEE ComSoc Distinguish Speaker Program at MUET, Jamshoro, Pakistan. He is very active in leading successful
projects as Principal Investigator under Horizon Europe MSCA Staff exchange, Erasmus + International Credit Mobility (ICM),
Capacity Building for Higher Education, and H2020 CO-FUND projects and won over 1.2 million Euros funding in total. He is a
Funded Investigator at one of top European research centres– CONNECT, Trinity College Dublin funded by Science Foundation.

Chih-Lin I (Fellow, IEEE) received the Ph.D. degree in electrical engineering from Stanford
University, Stanford, CA, USA. She is currently the CMCC Chief Scientist of wireless technologies. She has authored or coauthored more than 200 papers in scientific journals, book
chapters, and conferences and holds more than 100 patents. She is the co-author of the book
Green and Software-defined Wireless Networks: From Theory to Practice and has also co-edited
two books: Ultra-Dense Networks–Principles and Applications and 5G Networks–Fundamental
Requirements, Enabling Technologies, and Operations Management. Her research focuses on
ICDT deep convergence: From green & soft to open & smart. She was the recipient of the
2005 IEEE ComSoc Stephen Rice Prize, 2018 IEEE ComSoc Fred W. Ellersick Prize, the 7th
IEEE Asia-Pacific Outstanding Paper Award, and 2015 IEEE Industrial Innovation Award for
Leadership and Innovation in Next-Generation Cellular Wireless Networks. She is the Chair of
O-RAN Technical Steering Committee and an O-RAN Executive Committee Member, the Chair
of FuTURE 5G/6G SIG, the Chair of WAIA (Wireless AI Alliance) Executive Committee, an
Executive Board Member of GreenTouch, a Network Operator Council Founding Member of ETSI NFV, a Steering Board Member
and Vice Chair of WWRF, a Steering Committee Member and the Publication Chair of IEEE 5G and Future Networks Initiatives, the
Founding Chair of IEEE WCNC Steering Committee, the Director of IEEE ComSoc Meetings and Conferences Board, the Senior
Editor of IEEE TRANSACTIONS ON GREEN COMMUNICATIONS AND NETWORKING, an Area Editor for IEEE/ACM TRANSACTIONS
ON NETWORKING, Executive Co-chair of IEEE Globecom 2020, IEEE WCNC 2007, IEEE WOCC 2004 and 2000, a member of
IEEE ComSoc SDB, SPC, and CSCN-SC, and a Scientific Advisory Board Member of Singapore NRF. She is a Fellow of WWRF.

9224

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 73, NO. 7, JULY 2024

Vuk Marojevic (Senior Member, IEEE) received the M.S. degree in electrical engineering from
the University of Hannover, Hanover, Germany, and the Ph.D. degree in electrical engineering
from Barcelona Tech (UPC), Spain. He is currently an Associate Professor with Electrical and
Computer Engineering, Mississippi State University, Starkville, MS, USA. He is a Principal
Investigator of the U.S. National Science Foundation projects AERPAW and Open Artificial
Intelligence Cellular (OAIC). His research interests include mobile communications, software
radios, spectrum sharing, wireless testbeds and testing, and wireless security with application to
mission-critical communications, open radio access network (O-RAN), and unmanned aircraft
systems. He is an Associate Editor for IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY and
the IEEE Vehicular Technology Magazine. Dr. Marojevic is an expert in open-source software for
software radios, radios built in software. He was one of the first to undertake the complex endeavor
to implement the 4G cellular protocol in software and make the software open and operational
with commercial off-the-shelf software radio hardware. This was the foundation of srsRAN.
He has managed large-scale wireless research testbeds and co-designed AERPAW. He is currently leading a multi-university
U.S. NSF Project that is developing OAIC: Prototyping Artificial Intelligence-Enabled Control and Testing Systems for Cellular
Communications Research.

Sunder Ali Khowaja received the Ph.D. degree in industrial and information systems engineering
from the Hankuk University of Foreign Studies, Seoul, South Korea. He was a Postdoctoral
Research Fellow with the Department of Mechatronics Engineering, Korea Polytechnic University, Siheung, South Korea. He is currently an Assistant Professor and the Founding Chairman
with the Department of Telecommunication Engineering, Faculty of Engineering and Technology,
University of Sindh, Jamshoro, Pakistan. He has more than 14 years of academic and industrial
experience in different multi-national companies and educational institutions. He has been
included in the top ten spots for two of the competitions announced at CVPR 2022, while he
secure top 3rd position in UG+ Atmospheric Turbulence Mitigation Challenge at CVPR 2022.
His research interests include deep learning, artificial intelligence, data analytics, and process
mining for emerging communication and computer vision technologies.

Shao-Yu Lien (Senior Member, IEEE) received the B.S. degree from National Taiwan Ocean
University, Keelung, Taiwan, in 2004, the M.S. degree from National Cheng Kung University,
Tainan City, Taiwan, in 2006, and the Ph.D. degree from National Taiwan University, Taipei,
Taiwan, in 2011. He was with National Formosa University, Huwei, Taiwan, as an Assistant
Professor and Associate Professor from 2013 to 2017, and he is currently with National Chung
Cheng University, Chiayi, Taiwan, as an Associate Professor. Dr. Lien is also the technical
Director of the Smart System Institute, Institute for Information Industry, since 2020. His research
interests include configurable networks, cyber-physical systems, radio access networks and robotic
networks. Dr. Lien was the recipient of a number of prestigious research recognitions, including
IEEE Tainan Section Best Young Professional Member Award 2019, IEEE Communications
Society Asia-Pacific Outstanding Paper Award 2014, Scopus Young Researcher Award (issued
by Elsevier) 2014, URSI AP-RASC 2013 Young Scientist Award, and IEEE ICC 2010 Best Paper
Award. Dr. Lien is the Guest Editor of IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS
AND NETWORKING in 2019, and the Guest Editor of Wireless Communications and Mobile Computing (WCMC) in 2017. In the
meantime, Dr. Lien was also the leading organizer of several technical workshops in IEEE VTC-Spring 2015, IEEE GLOBECOM
2015, Qshine 2015 and 2016, and IEEE PIMRC 2017, IEEE GLOBECOM 2019, and IEEE ICC 2020. He has also been a 3GPP
standardization delegate since 2009 for LTE, LTE-A, LTE Pro, and 5GNR. In this role, he has contributed to more than 70 technical
documents and patents in collaboration with HTC Corporation, Institute for Information Industry (III), Industrial Technology
Research Institute (ITRI), and Huawei.

IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 73, NO. 7, JULY 2024

9225

Yue Wang (Senior Member, IEEE) received the Ph.D. degree from the University of Victoria,
Victoria, BC, Canada. She is currently a Principal 5G Researcher with Samsung Electronics
R&D Institute U.K. Prior to joining Samsung, she worked in the U.S. and U.K. on a number of
technical subjects in wireless communications research and standards. She has coauthored more
than 40 papers and is a Co-Inventor of more than 20 patents. Her current research focuses on
AI for 5G, with topics spanning extensively on the application of AI in communications systems
and networks for 5G and beyond. She is the Samsung delegate to ETSI ISG ENI (Experiential
Networked Intelligence), and the Secretary and Rapporteur of ENI. She also sits on the Industry
Advisory Board of two universities and is the Industry Supervisor of a five-year research program,
all in the area of AI for 5G and beyond. She has been a Senior Member of IEEE since 2012.
PAPER_TEXT
