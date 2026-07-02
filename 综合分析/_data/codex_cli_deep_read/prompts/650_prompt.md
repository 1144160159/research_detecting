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
# [650] DSecO: Domain Name System (DNS) Data as a Knowledge Graph for Enhanced Security Analysis
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
编号：650
题名：DSecO: Domain Name System (DNS) Data as a Knowledge Graph for Enhanced Security Analysis
年份：2025
DOI：10.1109/ton.2025.3598374
来源：IEEE Transactions on Networking
PDF：paper/10.1109_TON.2025.3598374.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：无
相关性：弱相关，分数 4
已有代码状态：已下载；dns-graph -> source\dns-graph

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\650.txt
- 原始字符数：75942
- 本次发送字符数：75942
- 是否截断：False

代码包：
- 仓库：dns-graph
  - URL：https://github.com/abhisek/dns-graph
  - 状态：downloaded
  - 本地目录：source\dns-graph
  - 顶层结构：.gitignore、LICENSE、README.md、app/、docs/
  - 主要语言：JavaScript:5、JSON:2
  - README 标题：DNS Graph、Why and What、How To、Neo4j can be run as a docker container easily、Requirements、DNS Data Import、Graph Query、Contribution、DNS Graph、Why and What
  - README 运行线索：docker container easily；docker run -d -p 7474:7474 -p 7687:7687 -v；docker container easily；docker run -d -p 7474:7474 -p 7687:7687 -v；docker container easily；docker run -d -p 7474:7474 -p 7687:7687 -v
  - 关键文件：{"依赖环境": ["app/package-lock.json", "app/package.json"]}
  - 数据集线索：tor

论文正文包开始：
<<<PAPER_TEXT
370

IEEE TRANSACTIONS ON NETWORKING, VOL. 34, 2026

DSecO: Domain Name System (DNS) Data as a
Knowledge Graph for Enhanced Security Analysis
Didier Bringer

and Lionel Tailhardat

Abstract—Managing Domain Name System (DNS) records
presents challenges in terms of consistency and tracking over
time, which can have operational impacts, particularly on cybersecurity. In this paper, we explore the use of ontologies and
knowledge graphs to facilitate DNS system audit activities. We
define nine key use cases derived from real DNS operations data
of a large-scale telco company and demonstrate how querying
and inference techniques can address these use cases using an
RDF knowledge graph structured by the DSecO vocabulary, an
open-source ontology available at https://w3id.org/dseco. Overall,
we demonstrate the feasibility of providing a unified view of DNS
records and the practicality of explainable and shareable DNS
administration rules for extended analysis and informed decisionmaking by NetOps and SecOps teams regarding DNS records.

Listing 1 Example of DNS records with a CNAME clause:
CNAME allows one domain name to alias another for address
redirection. For instance, when a user attempts to access
www.example.org, the operating system converts it to
203.0.113.1, enabling the browser to connect to the server
with this IP address and retrieve the requested page.

Index Terms—DNS audit, network operations, cybersecurity,
ontologies, knowledge graphs, semantic web, AXFR, domain
hijacking.

removed for a complete cleanup when www.example.org
is no longer in use. It is noteworthy that the CNAME of
CNAME pattern (known as a CNAME chain) – although not
recommended1 – can still be found in many DNS records.2
Stale DNS records can also pose cybersecurity risks. For
example, DNS record chains that include a DNS record part
of a bankrupt Web agency’s DNS zone can lead to a “domain
hijacking”, as hackers could purchase the agency’s domain
name and receive requests made to www.example.org.
This can result in credential leaks, as the user’s Web browser
may send cookies to the hackers’ server. While HTTPS and
HSTS [20] help reduce this risk, it remains high due to
automated and free Certificate Authorities (CAs) like Let’s
Encrypt.3 Indeed, hackers can obtain valid certificates in
someone else’s name and succeed the identity verification
challenge by simply placing a nonce file on the target server
they control.4
These examples highlight the numerous rules needed to
analyze DNS records, which can be tedious and error-prone
when done manually within a given organization, especially
for medium to large-sized companies with thousands to tens
of thousands of records and complex interconnections.
Automating DNS record analysis can enhance operational
efficiency, prevent incomplete cleanups and security vulnerabilities, and improve overall DNS service performance by
reducing lookup operations [6]. However, challenges in data
integration and knowledge representation arise due to the
sharing of DNS data across different zone owners and heterogeneous systems. Indeed, providing a unified view of DNS

I. I NTRODUCTION
N THE Internet, a primary address such as
www.example.org – referred to as a fully qualified
domain name, or FQDN [13, §2.3.5] – must resolve to
one or more final IP addresses (either IPv4, IPv6, or both).
The FQDN to IP lookup is a key mechanism, commonly
implemented using a Domain Name System (DNS) [40], to
determine how to connect to network services (e.g. the host
serving Web pages for www.example.org). Organizations
managing large-scale networks, such as international
corporations or Internet service providers, may utilize the
DNS CNAME (Canonical Name) [40, §3.3.1] functionality
(Listing 1), for example to handle the complexity and constant
evolution of the network infrastructures and services they
operate by defining generic addresses. However, this constant
evolution also requires ongoing adjustments of DNS records
by NetOps and SecOps teams, both to ensure the proper
functioning of services and to prevent cybersecurity issues.
For instance, the CNAME example of Listing 1 summarizes as a rule chain akin to www.example.org−−−−−−→
CN AM E
www.example.myotherzone.org −
→ 203.0.113.1,
A
where www.example.myotherzone.org should be

O

Received 14 January 2025; revised 3 July 2025; accepted 8 August 2025;
approved by IEEE T RANSACTIONS ON N ETWORKING Editor E. Bertino. Date
of publication 11 September 2025; date of current version 30 December 2025.
This work was supported in part by the Orange - Fonds d’Innovation pour
la Sécurité (FSI) led by Jean Marc Blanco. (Corresponding author: Lionel
Tailhardat.)
The authors are with Orange Company, 92449 Issy-les-Moulineaux, France
(e-mail: lionel.tailhardat@orange.com).
Digital Object Identifier 10.1109/TON.2025.3598374

1 CNAME chains increase DNS server load, cause name resolution delays
[6], and expand the trusted computing base (TCB), posing security risks [45].
2 Particularly in CDNs to improve content delivery efficiency [50].
3 https://letsencrypt.org/
4 CAA DNS records [42] can mitigate this.

2998-4157 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

BRINGER AND TAILHARDAT: DSecO: DNS DATA AS A KNOWLEDGE GRAPH FOR ENHANCED SECURITY ANALYSIS

records, potentially linked to network infrastructure and business data, is essential for informed decision-making by NetOps
and SecOps teams for both DNS administration tasks and
day-to-day monitoring of the networks behavior. Additionally,
establishing explainable and shareable DNS administration
rules is crucial to ensure a clear understanding of their
execution and mutual agreement among zone owners.
In this work, we hypothesize that an explicit graph representation could reflect the chaining nature of DNS records and
provides formal guarantees for various use cases. To tackle
the above-mentioned challenges, we propose the “DNS-KG”
approach, which involves building an RDF knowledge graph
[1] from heterogeneous DNS data within an organization to
facilitate cross-zone analysis of DNS records. The graph is
structured by DSecO, a lightweight ontology we have implemented in RDFS [9] / OWL [54] to enable a query-based audit
approach of DNS data and facilitate connections to third-party
knowledge bases for broader inference cases, such as linking
DNS configuration to Cyber Threat Intelligence (CTI) data
[24], [56]. We formalize nine DNS administration use cases
based on interviews with DNS operation experts from Orange
– a leading international network infrastructure and service
provider – and implement them as SPARQL queries [55] to
evaluate the query-based audit approach on both generated
and real-world data. The DSecO implementation, evaluation
dataset, and the associated documentation are available as open
source at https://w3id.org/dseco. Overall, we demonstrate the
feasibility of providing a unified view of DNS records and the
practicality of explainable and shareable DNS administration
rules for extended analysis and informed decision-making by
NetOps and SecOps teams regarding DNS records.
The remainder of this paper is organized as follows. In
Section II, we review related work, focusing on DNS-related
security methods and tools, as well as semantic models for
knowledge representation. In Section III, we provide details
of the DNS-KG approach with a deep dive into the use case
definitions, domain modeling with DSecO, and knowledge
graph construction and exploitation for DNS records audit. In
Section IV, we present the experiments conducted and their
results on the DNS-KG approach, including running SPARQL
queries related to the use case definitions. Finally, we conclude
and outline some future work in Section V.
II. R ELATED W ORK
Various studies have explored DNS-related security methods
and tools to detect vulnerabilities or malfunctions due to noncompliance or discrepancies in DNS, using either a glass-box
or closed-box strategy on medium to large-scale systems (e.g.
academic or corporate networks, the Internet).5 However, few
studies examine this field through the lenses of knowledge
representation and reasoning (KRR) and linked open data
principles [1], even though several existing semantic models
could be applied for explicit representation and reasoning on
DNS configurations (e.g. UCO [56] and ICAS [31], further
5 Glass-box testing analyzes a system’s internal workings with full access
to its source code, focusing on identifying vulnerabilities, while closed-box
testing evaluates functionality from an external perspective, simulating user
interactions without knowledge of the internal code.

371

discussed below). Thus, there is an opportunity to bridge DNSrelated security methods and tools with semantic models. In
the following paragraphs, we review existing works on these
two aspects and then conclude with the positioning of our
DNS-KG proposal.
a) Glass-box methods & tools: GRooT [50] and Heracles
[25] are two methods aiming at verifying DNS configurations,
with GRooT apparently the first formal approach in this field
of study. Both methods are able to capture the entirety of
DNS behavior within a graph representation (a DNS configuration interpretation graph), encompassing the transformation
of DNS zone files into graphs to enhance the consistency
verification process. This verification can be performed as
either a self-check or a cross-check. In GRooT, users can
implement new analysis cases as C++ functions, ensuring high
performance in processing the interpretation graph. However,
developing additional use cases (e.g. identifying risky or
useless DNS entries) requires abstraction and programming
skills from SecOps teams. Additionally, the specific data
structure of the interpretation graph and the static nature of
analysis functions make it difficult to extend graph data with
external sources or incorporate new data objects at runtime
for non-monotonic reasoning. In the same vein as GRooT and
Heracles, Moura et al. [18] developed and open-sourced the
CycleHunter framework to analyze data from DNS zone files.
Their work addresses a specific issue in DNS records: cyclic
dependencies, highlighting the significant associated risk (i.e.
a potential collapse of the entire Internet), which they refer to
as a TsuNAME, and proposing methods for its remediation.
Regarding tools, the dns-graph6 project (a small GitHub
project with no updates since 2018) introduces a database
model for HOST, MX, DOMAIN and NS records but does
not take CNAME records into account. The overall approach
involves populating a Neo4J7 graph database with data and
subsequently execute queries. Another interesting project is
PowerDNS8 which implements a DNS system that can integrate a database backend and provide an API, facilitating
queries compared to traditional file-based DNS systems. However, it only queries zones under its delegation.
b) Closedbox methods & tools: Ramasubramanian et al.
[45] surveyed nearly 600’000 Web server names to establish
a dependency graph of authoritative name servers. For a
given Web server name, they highlighted that a larger Trusted
Computing Base (TCB) increases risk, as compromising any
name server within the delegation graph can jeopardize the
name. They also compiled known vulnerabilities of public
name servers to perform a risk assessment. While this study
provides a valuable overview of name system vulnerabilities,
it does not provide details about how the data was stored.
Also on the topic of trust, Daiping et al. [8] demonstrated
that subdomains inherit the trust of their apex domains, which
is particularly valuable for illicit online activities. Indeed, the
theft of Fully Qualified Domain Names (FQDNs) through IP
hijacking or domain hijacking – cases tackled by our DNS6 https://github.com/abhisek/dns-graph
7 https://neo4j.com/
8 https://github.com/PowerDNS/pdns

372

KG approach – can lead to a variety of serious and detrimental
consequences for the brand that owns the domain.
More focused on DNS record management, the authors of
[7], [15], [17], and [26] all highlight the often-overlooked
severity of dangling or stale DNS records. Since they operate
in a closed-box manner, they use passive DNS traffic data
or brute force techniques to identify domains, followed by
live testing to ascertain DNS responses. They all conclude
that maintaining one’s DNS properly over time is essential
for security. In [44], DNS configuration updates are also
discussed through the study of orphan and abandoned records
in the Top-Level Domains (TLDs) zone file. The conclusion
remains consistent across this body of work: mitigating related
cybersecurity risks involves the process of cleaning areas.
Finally, regarding tools, the DNSDumpster9 project is a
free online solution for DNS reconnaissance and domain
information gathering. It offers insights into a domain’s DNS
records, identifies (some of the) subdomains, and visually
represents the domain’s DNS structure. It is commonly used
by security professionals and researchers for network analysis
and vulnerability assessments. Focusing more on facilitating
navigation and analysis of the Internet data space through
semantic integration of various data sources, Fontugne et al.
[46] have developed and open-sourced the Internet Yellow
Pages (IYP) project, which integrates 46 publicly available
datasets into a Neo4j database. The project is designed to be
community-driven, allowing dataset curation and data model
evolution with provenance metadata (e.g. data source, collection date, update date).
c) Semantic models: In this paragraph, we briefly describe
works involving semantic models in the form of RDFS/OWL
ontologies. In direct relation to the field of cybersecurity,
UCO [56] is a popular community-developed ontology built
around the cyber security domain, covering a wide range
of important concepts such as agents, resources, or actions.
Original motivations for this work were knowledge discovery
and After Action Report (AAR) annotation tasks. The ICAS
ontology [31] closely resembles UCO in both structure and
intent: a lengthy enumeration of objects that are more or less
related and grouped by discourse domain for networking and
cybersecurity. Although ICAS has interesting concepts and
relationships to represent DNS configuration data, its structure
seems overcomplicated and no example of implementation in
a knowledge graph is available. Further, it is no longer maintained. Similar to the idea of leveraging CTI data in ontologies
like UCO and ICAS, the authors in [5] propose an anomaly
detection system that utilizes a combination of a SWRLbased [19] inference rule set and SPARQL queries to classify
and provide guidance on various situations. Although this
work has been evaluated on sensor data and does not directly
relate to DNS configuration data, the principles developed for
situation classification using reasoning can be generalized to
other application domains. In a similar vein, authors in [24]
introduce the ICS-SEC ontology to enable threat intelligence
exploration, as well as vulnerability assessment and remediation use cases to the field of Industrial Control Systems (ICSs).

IEEE TRANSACTIONS ON NETWORKING, VOL. 34, 2026

To achieve this, an ICS-SEC knowledge graph is constructed
by aggregating several well-known security databases and data
models, such as ATT&CK10 and NVD.11 Like the work in
[5], the proposed solution does not directly relate to DNS
configuration data, but principles and technique for situation
classification can generalize to side application domains.
Still in relation to cybersecurity, but focusing on software,
Taghavi asserts in [37] that the rapid increase in vulnerabilities
across various types of assets has rendered the synthesis of
this knowledge inherently more challenging. In this context,
knowledge graphs and their accompanying technology stack
have been advocated as a viable solution for modeling, integrating, and facilitating interoperability among diverse data
sources. We note that, surprisingly, Taghavi does not leverage
the Software Bill of Materials (SBOM)12 inventory to model
the dependencies between components. Further, Taghavi did
not made available any open source ontology from his work.
Going a same line of thoughts, Alqahtani et al. introduced
SECONT and MAVON [53], ontologies covering software
artifacts and ontologies for software vulnerability databases.
Another work, the Software Evolution Ontologies (SEON)
[35], enables to bootstrap a modeling of GitLab activities, and
thereby track code quality evolution over time, however no
direct link to the analysis of vulnerabilities is available through
SEON.
Finally, in relation to representing network infrastructures,
the DevOpsInfra [39] ontology describes sets of computing
resources and how they are allocated for hosting services.
However, the ontology mostly focuses on the provisioning
activity and concepts are missing for risk assessment and
a finer grain description of the network topology. In close
relation, NORIA-O [30] allows to describe an infrastructure,
its events, and diagnosis and repair actions performed during
incident management. NORIA-O connects to UCO, enabling
reasoning about network topology and cybersecurity aspects
simultaneously; however, it does not include concepts or
relationships for DNS data.
d) Dns-KG positioning: The work presented in our
DSecO paper globally aligns with the high-level objectives of
the related works studied above, in that the DNS-KG approach
aims to provide a method and tools for risk assessment and
remediation for network service infrastructures heavily relying
on DNS. For instance, several studies propose defining and
executing assessment cases in a glass-box manner on a graphbased representation of DNS configurations (e.g. GRooT [50],
Heracles [25], CycleHunter [18], and dns-graph).
However, works such as GRooT and Heracles conduct
analyses to identify inconsistencies by deducing DNS behavior
based on the subtleties of the domain’s RFCs as interpretation
rules, whereas DNS-KG focuses on analyzing the DNS “tree”
itself to detect both risky and redundant entries, capturing
CNAME and A records in a straightforward manner, without
considering Time to Live (TTL) values or additional features.
For example, TTL is a concept that refers to the duration
10 https://attack.mitre.org/
11 https://nvd.nist.gov/

9 https://dnsdumpster.com/

12 https://www.cisa.gov/sbom

BRINGER AND TAILHARDAT: DSecO: DNS DATA AS A KNOWLEDGE GRAPH FOR ENHANCED SECURITY ANALYSIS

for which DNS data is considered valid, and because DNSKG collects data directly from zone files rather than from
an authoritative DNS server, TTL is not applicable at all
as it would be in a closed-box approach. In our glassbox methodology, entries possess an infinite TTL, remaining
valid as long as they exist in the zone file. Despite these
differences in approaches, GRooT and Heracles do have points
of convergence with DNS-KG in that their research has already
contributed one use case in this paper (see uc_loop in
Section III-A), which is a scenario likely to occur over time.
While we acknowledge that the DNS-KG structured by
DSecO (Section III-B) does not capture all DNS features, we
believe it is sufficient for DNS operations and administration
use cases, starting with the nine defined with SecOps experts
in Section III-A. For example, although DSecO currently does
not implement NS records – such as for preventing TsuNAME
attacks [18] – it does include the CNAME concept, which allows
the analysis of CNAME chains and the detection of CNAMEbased cyclic dependencies, among other things. It should
be noted that the decision to implement specific concepts
generally depends on the objectives of the projects studied,
such as IYP [46], which, for example, chose not to include
non-resolvable CNAMEs. Furthermore, DSecO can easily be
extended with new concepts (e.g. a NS concept to materialize
records already at hand in DNS zone dumps) and by linking
the DNS-KG to other knowledge bases based on linkedopen data principles (e.g. by adding vulnerability information
about CTI informations [5], [45]; network informations [46];
SBOM information [37], [53]) to broaden the scope of risk
assessment inference, thereby refining the risk categorization
and remediation.
The DNS-KG approach also aligns with the need to clean
DNS configurations regarding cybersecurity risks, as proposed
by Borgolte et al. [26] and in [17]. However, while these works
emphasize systematizing DNS operations using public data,
the DNS-KG proposal adopts a glass-box strategy to secure
dangling records on managed systems, including zones not
directly under our control (unlike PowerDNS), provided we
have access to the configuration data in some form.
Finally, we also observe that, compared to works such
as GRooT, Heracles, dns-graph, and IYP, the DNS-KG
approach brings a no-code approach to the field by leveraging
RDF/RDFS/OWL syntax and vocabularies for the knowledge
graphs and the DSecO ontology. For example, while knowledge graph construction and DNS assessment use cases could
be implemented using programming languages (e.g. scriptbased data integration and Cypher13 queries in IYP, C++
functions in GRooT), the DNS-KG approach aims to enable
users to build the graph using a declarative data integration
approach (making it portable and logically auditable) by
utilizing the RDF Mapping Language (RML) [3] vocabulary
and performing assessments through SPARQL [55] queries.14
We also opted for RDF knowledge graphs, rather than labeled
property graphs (LPGs) (as in [18], [46], and dns-graph).
LPGs are oriented towards performance and flexibility for simple relationships and rich properties, whereas RDF knowledge
graphs facilitate handling heterogeneous data and emphasize
semantics and reasoning for complex relationships and interconnected knowledge, thanks to shared explicit knowledge
representations [1]. Furthermore – in contrast with [37] and
[45] – our work clearly articulates the approach to data storage
and the methods of processing it, and is fully open-source.
Overall, we note that the DNS-KG approach addresses a gap
in the aforementioned related works by providing explainable
risk assessment over DNS configuration data and being open to
including all data objects and relationships pertinent to security
concerns (such as machines, Docker images, CaaS,15 PaaS,16
HTTP L7, organizations, CVEs,17 CPEs,18 and more).
III. M ETHODOLOGY —T HE DNS-KG A PPROACH
In this section, we introduce our DNS-KG approach to
facilitate DNS administration operations – such as the cleanup
of outdated records or those that pose cybersecurity risks –
by leveraging an explicit representation of DNS record data
as a knowledge graph. We assume that this representation
can capture the chaining nature of DNS records and provide
formal guarantees for various use cases through graph traversal
and subsumption based on an ontology (i.e. the explicit
representation of a discourse domain through concepts and
relationships). Figure 1 summarizes the DNS-KG approach.
First, in Section III-A, we focus on operation support by
identifying and formalizing nine key DNS administration use
cases based on the analysis of DNS administration operations
with SecOps experts from Orange. We use a Behavior-Driven
Development (BDD) methodology to describe these use cases
in natural language, making them suitable for automated
data processing. Next, in Section III-B, we introduce the
DSecO vocabulary, an open-source RDFS/OWL ontology that
structures DNS-related data from various sources and enables
reasoning related to the identified use cases. In Section III-C,
we detail the data processing pipeline for constructing the
knowledge graph using a no-code approach, and how it is
queried by translating use cases into SPARQL queries to
identify and classify potential non-compliance in DNS data.
We present the related experiments and results in Section IV.
A. Use Cases Definition
To provide more detail about the analysis to be performed,
we conducted a survey of DNS administration operations with
a panel of SecOps experts from Orange. This panel consists
of 12 operations specialists from the security department, who
collectively represent over 20 years of experience managing
more than 20’000 DNS records for Orange. Based on this
survey, we define the following nine use cases, that will
serve as a reference for the utilization of the knowledge
graph developed in Section III-C. For each use case, we
provide a brief description of the situation to monitor, and
its formalization in Gherkin syntax [51]. The names of the
15 Container as a Service.

13 Cypher is the query language for Neo4J.

16 Platform as a Service.

14 SPARQL is a standardized, widely used query language for RDF in both

17 CVEs: Common Vulnerabilities & Exposures.

academia and industry.

373

18 CPE: Common Platform Enumeration.

374

IEEE TRANSACTIONS ON NETWORKING, VOL. 34, 2026

Fig. 1. The DNS-KG approach. This diagram outlines our approach as a workflow for DNS configuration assessment and correction, based on the definition of
assessment use cases (upper-left branch) and DNS configuration data of managed zones represented as a knowledge graph (lower-left branch). The knowledge
graph construction step leverages a set of data transformation rules – using the RML vocabulary [3] – applied to DNS configuration data dumps from managed
zones, and subnet/AS number (ASN) relationship dumps from the BGPKIT public API [38]. The use case descriptions are formalized in Gherkin syntax [51].
DNS administration teams are responsible for correcting configurations, guided by inferences from the RDF knowledge graph (DNS-KG) through SPARQL
queries that represent the use cases (UC Query).

items hereunder are the names of the queries utilized later
in Section III-C and Section IV in the form of unit tests.
The use cases are grouped according to the goals they aim
to achieve: configuration cleanup (a, b, c, d), information
on the DNS data (e, f), and vulnerability analysis (g, h,
i). The Gherkin clause Then indicates the nature of the
operational response to be provided and the implicit level of
risk.
1) [a)]uc complete cleanup: In the case of a public zone
and internal zones, entries within the internal zone
should not exist unless their corresponding entries in
the public zone are also present.

Listing 3 The uc_complete_cleanup_not_resolving
Gherkin model.

Listing 4 The uc_loop Gherkin model.

Listing 2 The uc_complete_cleanup Gherkin model.

2) [b)]uc complete cleanup not resolving: In the case of
a public zone and internal zones, entries within the
internal zone should not exist unless their corresponding
entries in the public zone are also present. As we also
check the last A record, these entries are not resolving
thus easier to decide to remove.
c) uc loop: This use case derives from the Heracles [25]
and TsuNAME [18] works. It is useful for detecting
loops in DNS. For example, although cyclic dependencies based on CNAMEs are said not to trigger a
“TsuNAME” [18, §4.3], we have learned that they pose
operational risks and cause service disruptions; thus,
such loops should be fixed.

d) uc ultimately do not resolve to an ip address: An
entry on example.org “A” points to “B” that points
to “C” (A → B → C); if C is removed, A is not
resolving anymore, thus it should be removed because
it is a useless link. Such cases happen when NetOps
are migrating a service, they may forget to clean the
DNS entry.
Listing 5 The uc_ultimately_do_not_resolve_to_
an_IP_address Gherkin model.

3) [e)]uc entries using our cdn: Questions a manager
might ask to understand the percentage of migration to
a CDN solution, for example.

BRINGER AND TAILHARDAT: DSecO: DNS DATA AS A KNOWLEDGE GRAPH FOR ENHANCED SECURITY ANALYSIS

Listing 6 The uc_entries_using_our_CDN Gherkin
model.

f) uc resolving to a single ip address: Depending on
your architecture, you may wish to identify the entries
that resolve to a single IP address. If you are not utilizing
a Virtual IP (VIP),19 it may be beneficial to recognize
that these entries are not redundant.
Listing 7 The uc_resolving_to_a_single_IP
_address Gherkin model.

g) uc domain hijacking: An entry on example.org
directs to a Web agency; if the Web agency goes
bankrupt, the domain may become available for purchase. A black-hat hacker might attempt to buy it
and thus receiving the traffic. The hacker may take
advantage of the domain name for phishing activities or
potentially for distributing code to clients or the loading
of JavaScript scripts. Alternatively, the hacker could
create a webpage on this domain that redirects users
to a site mimicking the appearance of example.org,
using their own certificate, in an attempt to deceive
users into entering their credentials. However, there
exists a potentially more perilous scenario in which
a hacker generates an SSL certificate in the name
of example.org, utilizing certificate providers that
authenticate the identity of the domain owner merely
by requesting a nonce file to be placed on the website.
Nevertheless, the risk of domain hijacking – an “Acquire
Infrastructure: Domains”20 technique as per MITRE
ATT&CK – may be reduced due to the widespread use
of HTTPS and HSTS [20] as well as CAA DNS records
[42]. Identifying these domains is crucial for security,
as indicated by the action “Then it should be monitored
closely” in Listing 8. This means that NetOps/SecOps
must manage the risk of domain hijacking by obtaining
guarantees from the provider or thorough pentesting.
h) uc ip hijacking: An entry on example.org directs
to an IP address that is outside the company’s subnet
and belongs to another Internet Service Provider (ISP).
A black-hat hacker might attempt to obtain the same
IP by purchasing services from that ISP. Borgolte et al.
[26] call these “IP address use-after-free vulnerabilities”
19 VIP: an IP address not tied to a specific physical interface, used for load

balancing, failover, or redundancy in networking.
20 https://attack.mitre.org/techniques/T1583/001/. Includes domain takeover.

375

Listing 8 The uc_domain_hijacking Gherkin model.

and MITRE ATT&CK categorizes them under “Acquire
Infrastructure: Server”.21
IP hijacking may permit the attacker to obtain a valid
certificate for the domain, but even once the domain RR
is fixed, it may lead to a security risk as the hacker can
use the SSL certificate in a man-in-the-middle attacks in
a closed network, such as a coffee shop [26].
Listing 9 The uc_ip_hijacking Gherkin model.

i) uc ip hijacking filter: This use case derives from the
uc ip hijacking, connecting the AS, subnet, and organizational units concepts to filter the results more strictly.
We assume that a list of friendly AS organizations
is available, enabling to focus on other AS (i.e. nonfriendly organizations are to be scrutinized).
Listing 10 The uc_ip_hijacking_filter Gherkin
model.

B. Domain Modeling With DSecO
In relation to RFC 1035, which describes the details of
the domain system and protocol (see particularly [40, §3]),
we identify the essential concepts and relationships from
the above Gherkin models (Listings 2 to 10) to establish
the necessary terminology for the DNS-KG. For example,
analyzing the uc complete cleanup case of Listing 2 leads
us to the following axiomatisation (Eq. 1) as a first approach:

ToRemove ≡ FQDNend u managedBy.ORGint u
¬ FQDNtop
u linkedTo+ .FQDNend

u managedBy.ORGtop

(1)

We choose to implement this terminology in the form of
an RDFS/OWL ontology to address knowledge representation
21 https://attack.mitre.org/techniques/T1583/004/

376

IEEE TRANSACTIONS ON NETWORKING, VOL. 34, 2026

Fig. 2. The DSecO ontology. This diagram provides an overview of the ontology using the Chowlk notation [49]. The base namespace is dseco, which
URI is https://w3id.org/dseco/ontology/. Additional namespaces are: observable = https://ontology.unifiedcyberontology.org/uco/observable/, org = http://
www.w3.org/ns/org#, owl = http://www.w3.org/2002/07/owl#, and xsd = http://www.w3.org/2001/XMLSchema#. The shaded forms highlight the concepts
and properties of third-party vocabularies reused in DSecO, while the others are defined by DSecO.

and reasoning (KRR) challenges, particularly regarding the
management of heterogeneous data sources (e.g. data fetched
from various DNS sources, combined with data from BGPKIT
[38] for subnet/AS number (ASN) [22] relationships, and
internal databases for zone ownership) and ensuring linked
and interoperable data representation (e.g. associating DNSKG entities with cyber threat intelligence [24], [37], [56]
knowledge graphs or LDAP22 directory data [48]). In terms of
ontology design principles, we also have considered the RFCs
as a normative information source for the rules of transforming
DNS configuration data into a knowledge graph representation;
the principle here is to prioritize understanding among users by
adhering as closely as possible to the standard to minimize data
wrangling and interpretation efforts back and forth between the
DNS-KG and the source data. To further enhance usability,
we also considered essential to hide the complexity of the
use cases-related SPARQL queries (Section III-C), making the
DNS-KG system more accessible. Additionally, minimizing
graph traversal times is crucial for improving performance
(e.g. for closure calculus on CNAME chains).
As a result, we have implemented the DSecO conceptual
model which – for its release v1.6.1 – consists of two classes
(FQDN, ZONE), eight objects properties (hasAS, hasOrgu,
is_A_to, is_AAAA_to, is_CNAME_of, is_in_zone,
is_part_of, managedBy) fully mapped to the RFC 1035,
and four data type properties. These elements are defined in the
dseco namespace. The ontology connects to the well-known
ORG [10] and UCO [56] vocabularies, thereby enabling
connections of the DNS-KG to third-party knowledge bases
and adhering to Linked Open Terms (LOT) principles [32].
The DSecO expressivity is ALU RF (D) as per Protégé 5.1.23
Figure 2 gives an overview of the ontology. Its implementation
is directly available online at https://w3id.org/dseco/ontology/
using an ontology browser, and its documentation at https://
w3id.org/dseco/doc/.
In this paragraph, we introduce the DSecO concepts and
properties. We define the dseco:FQDN class for representing
fully qualified domain names (e.g. www.example.org) as
individuals, with domain names attached as strings via the
dseco:hasName property (e.g. for text-based searches).
22 LDAP: Lightweight Directory Access Protocol.
23 https://protege.stanford.edu/

The dseco:is_CNAME_of property links FQDN entities
to represent FQDN aliases – typically expressed as DNS
CNAME records, as shown in Listing 1. FQDN to IP reasoning
is supported by the dseco:is_A_to property, which
ranges to the UCO observable:IPv4Address class
used to describe DNS A records [40, §3.4.1], such as
www.example.myotherzone.org. A 203.0.113.1
in Listing 1. Reusing the UCO observable:IPAddress
class within DSecO facilitates interoperability of the
DNS-KG with third-party CTI-related knowledge bases.
Similarly, we define the dseco:is_AAAA_to property
with range observable:IPv6Address. From UCO,
we also reuse the observable:NetworkSubnet
class, and define the dseco:hasAS property with
range observable:AutonomousSystem to represent
that a subnet is declared by an AS. Similarly,
we define the dseco:is_part_of property to
enable
representing
observable:IPAddress
to
observable:NetworkSubnet
relationships.
Using
transitivity of dseco:hasAS and dseco:is_part_of,
we enable reasoning on observable:IPAddress to AS
relationships. Finally, we define the dseco:ZONE class to
enable reasoning about FQDNs of the same zone using the
dseco:is_in_zone property. The dseco:hasAS,
dseco:is_part_of,
and
dseco:is_in_zone
properties were introduced to address gaps in UCO and
support the DNS-KG use cases in Section III-A. For
instance, these properties facilitate zone-based assessment,
such as the uc complete cleanup case in Listing 2, by
linking dseco:ZONE entities to organizational units
in charge of the zone via the dseco:managedBy
property. To represent organizational units, we reuse
the org:OrganizationalUnit class from the ORG
vocabulary.
C. Knowledge Graph Construction & Exploitation
In this work, we refer to the UNIX philosophy [16],
[33] as guideline for designing the DNS-KG data processing
architecture, which aims to achieve the audit and correction of
DNS records in a timely manner while minimizing the need
for specific or additional codebases and storage resources. For
instance, using ontologies is a way to write the minimum
amount of code by leveraging declarative techniques and

BRINGER AND TAILHARDAT: DSecO: DNS DATA AS A KNOWLEDGE GRAPH FOR ENHANCED SECURITY ANALYSIS

reusing open-source models from the community. Furthermore, the use cases in Section III-A suggest that a fundamental
goal of this work is to answer queries without the need
for a backend (e.g. a lambda architecture to feed a graph
database [29])24 or frontend (e.g. a graphical user interface
combining data rendering and anomaly detection tools [28]),
but to only focus on ontologies and inferences. Therefore, in
what follows, we provide the details of a two-fold process: a
knowledge graph construction step (i.e. instantiate the DSecO
ontology in a simple text file through data wrangling of many
managed DNS zones and other sources) followed by a DNS
configuration assessment step (i.e. inferring on the resulting
knowledge graph by querying directly on the corresponding
text file and discard the file once finished). Overall, we assume
that no memory or long-term retention of the data is required
for the current DNS-KG objectives, but the use cases results
(e.g. “UC #1 Inference Response” in Figure 1) and their
explicability (i.e. the intrinsic explainability of the inference
process based on the DSecO ontology and the logical form of
the use case queries) are essential.
a) Knowledge graph construction: For this step, we consider a declarative data transformation approach to enable a
knowledge graph construction process that is easily auditable,
extensible, and platform-independent. We leverage the RML
[3] vocabulary to implement a set of data transformation rules
(i.e. TriplesMaps) for DNS configuration dumps of managed
zones gathered from the technical ecosystem at Orange, and
subnet/AS relationships dumps gathered from the BGPKIT
public API.25 Listings 11 & 12 provide an example of such
transformation rule for the BGPKIT source and resulting
knowledge graph, respectively.
Given the potential severe consequences of incorrect DNS
modifications (e.g. deleting the wrong DNS entry can disrupt
services), we employ a version control system for the transformation rules and adopt a CI/CD26 approach for knowledge
graph construction. This includes calling an RML engine (like
RMLMapper27 or BURP [14]), applying software engineering
practices such as unit testing with SPARQL queries for posterior validation of the construction process at the knowledge
graph level, and automated documentation generation using
Ontopsy [36] for visual inspection of RDF models.
The resulting knowledge graph is saved to a file for further
processing, including syntax and structure validation (which
was mentioned earlier under the term “unit test”), enrichment
with SPARQL UPDATE queries (Listings 13 and 14), and
inference with a combination of SPARQL UPDATE, ASK,
and SELECT queries (further discussed below as the DNS
configuration assessment step).
Regarding unit tests, we implement a set of tests following
the BDD approach by defining test cases in Gherkin linked to
SPARQL queries (Listings 15 and 16 for execution by the

24 A first approach for the DNS-KG work was to use a Neo4J database
(https://neo4j.com/), but it led to writing specific code and design a specific
data model, thus distancing us from the community.
25 BGPKIT, pfx2as: https://data.bgpkit.com/pfx2as
26 CI/CD: Continuous Integration/Continuous Delivery.
27 https://github.com/RMLio/rmlmapper-java

377

Listing 11 Snippet of data transformation rules using the
RML vocabulary to materialize AS & subnet entities and relationships from a BGPKIT dump. An adhoc dseco:hasAS
property is used to assert subnet/AS relationships before
joining with DNS configuration entities from other sources
and filtering out irrelevant AS & subnet entities.

Listing 12 Example of triple generated for the BPGKIT source
from the RML in Listing 11.

Listing 13 Example of a SPARQL enrichment query
that inserts dseco:isinOurSubnet facts based on
observable:IPAddress entities being part of specific
subnets.

Listing 14 Example of a SPARQL enrichment query that
inserts mykg:FQDN_resolving facts in the knowledge
graph based on the transitive closure of a CNAME chain using
a property path.

378

CI/CD automation during each code and knowledge graph
construction process update.
This involves creating baseline datasets and corresponding
knowledge graphs for each test case. We use the behave
library28 to parse unit tests and verify expected results. We
also implement LibOntology, a Python package that facilitates ontology-related operations from the command line
(e.g. querying, updating, validating, converting, and reasoning). The LibOntology code is available as open source at
https://w3id.org/dseco/tools/libontology, along with its documentation.

IEEE TRANSACTIONS ON NETWORKING, VOL. 34, 2026

Listing 17 Example of an assessment case SPARQL query for
uc_ip_hijacking related to the Gherkin model in Listing
9.

Listing 15 Example of a unit test in Gherkin syntax to validate
the knowledge graph construction step for the dseco:ZONE
concepts against a baseline dataset.

Listing 16 Example of a unit test SPARQL query to validate
the knowledge graph construction process in relation to the
Gherkin model in Listing 15.

knowledge graph after data wrangling using the query in
Listing 13.
Assessment queries may also require knowledge
beyond the data wrangling domain, such as the
uc_domain_hijacking example in Listing 18, which uses
organizational units responsible for DNS zones. To achieve
this, we incorporate a Domain Specific Individuals knowledge
base (Figure 1) during the knowledge graph construction step
by concatenating a flat knowledge graph file. For instance,
this includes detailed entities like mykg:ORGU_HQ and
mykg:ORGU_Affiliate (Listing 18), facilitating the
execution of uc_domain_hijacking.
Listing 18 Example of a assessment case SPARQL query for
uc_domain_hijacking in relation to the Gherkin model
in Listing 8.

b) DNS configuration assessment: We approach decision
making on the DNS configuration as a classification task
over the knowledge graph entities. We specifically consider
that the DNS & Network Configuration Update actions (Figure 1) resulting from the assessment process (i.e. configuration
cleanup, information, and vulnerability analysis as outlined in
Section III-A) are defined based on the existence of entities
that meet the axiomatic criteria for each use case.
We observe that the aforementioned testing framework
developed for the knowledge graph construction step aligns
with the goals of DNS configuration assessment. Therefore,
we consider reusing the same toolset and coupling each use
case Gherkin model from Section III-A with its translation into
SPARQL queries to run on the resulting knowledge graph.29
For example, uc_ip_hijacking in Listing 9 translates as
the SPARQL query in Listing 17.
Assessment queries may require knowledge graph enrichment, such as the uc_ip_hijacking example in Listing 17
which identifies if a given IP address belongs to a collection of
managed subnets. To achieve this, we add ad-hoc statements
during the knowledge graph construction step via SPARQL
UPDATE queries to benefit multiple use cases. For instance,
dseco:isinOurSubnet statements are inserted into the
28 https://github.com/behave/behave
29 Queries for the use cases in Section III-A are available open-source at
https://w3id.org/dseco/

Overall, this approach enables the decoupling of the ontology and assessment queries from the application context,
allowing each DNS-KG user to customize the assessment
process by adding, updating, or removing use cases and
domain-specific individuals. We foresee that by applying these
principles (i.e. graph enrichment, knowledge base concatenation, assessment parametrization), the DNS-KG could not
only identify inconsistencies and non-compliances but also
mitigate risks through a what-if approach by incorporating fictive entities (e.g. potential misconfigurations or cybersecurity

BRINGER AND TAILHARDAT: DSecO: DNS DATA AS A KNOWLEDGE GRAPH FOR ENHANCED SECURITY ANALYSIS

TABLE I
DNS-KG DATASET S TATISTICS

379

Listing 19 Base DNS-KG file with import statement for the
DSecO vocabulary.

validate the DNS-KG file syntax through LibOntology (i.e.
using the libontology-validate method); 4)configure
a filesystem using the queries/<UseCaseName>/
scheme to store Gherkin models (Section III-A) and
assessment SPARQL queries according to the set of
Listing 20 Command line for knowledge graph construction
and processing logs, highlighting three data sources (bgpkit,
data, and janus), twelve RML rule files (each implementing one TripleMap), and the number of individuals
generated by each rule set for the real-world dataset.

vulnerabilities) to explore use cases and understand associated
risks, in accordance with the method proposed in [52], thereby
facilitating proactive risk management.
IV. E XPERIMENTS
In this section, we present the experiments conducted to
evaluate the DNS-KG approach as defined in Section III. We
begin by presenting the experimental setup in Section IV-A,
which involves executing the knowledge graph construction
and DNS configuration assessment steps on a toy example
dataset and a real-world dataset based on Orange data.
We then present the results of these executions (in terms of
execution time and statistics on the queries) in Section IV-B,
followed by a discussion of these results in Section IV-C. The
queries used for these experiments and the generated dataset
are available at https://w3id.org/dseco/. Due to confidentiality,
the real-world dataset is not made public. Table I summarizes
the characteristics of the two datasets, and Table II summarizes
the results of the DNS configuration assessment step for both
the toy example and real-world dataset.
A. Experimental Setup
Whether for the toy example dataset or the real-world
dataset, we performed the knowledge graph construction
and DNS configuration assessment steps as follows: 1) in a
dedicated GitLab project, we initiate a base DNS-KG graph
file that imports the DSecO vocabulary (Listing 19); 2) start
the data wrangling process (Listing 20), which loops over a
set of sources (bgpkit, data, janus) and for each source
loops over RML mappings and concatenates the resulting set
of triples to the aforementioned base DNS-KG graph file; 3)

use cases to run; 5) enrich the DNS-KG using a set of
SPARQL UPDATE queries (e.g. Listings 13 & 14) through
LibOntology (i.e. using the libontology-update
method); 6) run the use cases against the DNS-KG file using
a Bash for loop30 to automatically discover implemented
queries/<UseCaseName>/test.sparql SPARQL
queries and call these through LibOntology (i.e. using the
libontology-query method embedded into a Bash time
command31 to measure the query execution time); 7) save the
output and execution time of each assessment SPARQL query
into separate text files and make them available for further
analysis (e.g. identification of misconfiguration patterns in
the dataset w.r.t. query responses, statistical comparison
of the query execution times w.r.t. query complexity [23],
and DNS and network misconfiguration remediation by
NetOps/SecOps); 8) to establish a baseline for query
execution times, we repeat steps #6 and #7 using a semantic
graph database (i.e. a local GraphDB32 instance) by loading
30 https://www.gnu.org/software/bash/
31 https://www.gnu.org/software/time/
32 https://graphdb.ontotext.com/

380

IEEE TRANSACTIONS ON NETWORKING, VOL. 34, 2026

TABLE II
Q UERY E XECUTION T IME

the DNS-KG file into the database and running the queries
against its SPARQL endpoint.
B. Results
The results presented below – particularly the timing
measures – stem from the execution of the methods and
tools described in Section IV-A on a MacBook M1 Pro
2021 (32 Gbyte RAM) test machine. Table I summarizes,
for each dataset (i.e. toy example & real-world), the
characteristics of the DNS-KG resulting from the knowledge
graph construction step on which the DNS configuration
assessment step was conducted. It includes the number of
entities per class and the number of instantiated properties,
grouped into facts derived from data transformation (e.g.
dseco:FQDN, dseco:hasName) and those computed (e.g.
mykg:FQDN_resolving,
dseco:isinOurSubnet).
Similarly, Table II reports on the execution time of the
different queries for the DNS configuration assessment step.
We break down the results for each dataset below.
a) Toy example dataset: The dataset consists of 43 DNS
records and contains 31 hand-crafted non-compliances.33
The execution of the libontology-validate
step takes tvalidate
=
0.10 s. The execution of
the libontology-query step takes an average
t̄query = 0.16 s per SPARQL query (this amounts to a
total of tqueries = 1.40 s for the entire process using a
sequential execution scheme),34 with correct detection of all
31 non-compliant configuration cases. Executing the same
queries on the GraphDB SPARQL endpoint results in a
consistent tquery = 0.10 s per query and also allows for the
detection of all non-conformities. files.
b) Real-world dataset: For this dataset, 300 375 DNS
records were used for constructing the DNS-KG, with 40 000
of these records being internally managed (ORGint in Eq. 1)
and 210 000 from affiliates (ORGtop in Eq. 1). The knowledge
graph construction step (i.e. data fetching & RML-based data
transformation) takes twrangling = 43 s. The resulting knowledge graph is roughly 10 Mbyte in size. The execution of the
libontology-validate step takes tvalidate = 4.90 s.
The execution of the libontology-query shows a total
33 Non-compliances
details
are
available
online
in
https://w3id.org/dseco/evaluation/dseco-<release>/
queries/uc_<name>/test.csv
34 Parallel execution of SPARQL queries is possible, enabling shorter overall
assessment times.

process duration of tqueries = 65.76 s using a sequential
execution scheme (i.e. average t̄query = 65.76/9 ≃ 7.3 s per
SPARQL query).35 Over 547 non-compliances were reported
and subsequently forwarded to a SecOps team through a ticketing system for further analysis and remediation.36 Among
these non-compliances, the top three use cases in terms of
operational complexity for carrying out the remediations and
associated cybersecurity risks break down as follows:
• uc_complete_cleanup: a total of 347 noncompliances were directly remediated with the
elimination of redundant or incorrect DNS records
in less than two days of work, as they relate to internally
managed records and SecOps has high confidence in the
remediation actions based on the use case definition.
• uc_domain_hijacking: at least 100 noncompliances related to the front-facing records were
reviewed by experts, as the question posed involves
identifying entries that pass through an intermediate
organizational unit. Two were then remediated by
triggering remediation operations with third-party teams
managing these records. Another non-compliance,
similar to the NS case described in [4], was also detected
using this use case and corrected promptly.
• uc_ip_hijacking: in the same way as for
uc_domain_hijacking, at least 100 noncompliances were reviewed, of which one was
remediated through the intervention of third-party
teams.
C. Discussion
From the results presented in the previous paragraph, the
detection of 100% of cases in the toy example dataset
demonstrates the effectiveness of the proposed architecture.
Additionally, the handling of over 547 non-compliance reports
in the real-world dataset, along with the rapid identification
of 350 cases needing remediation, confirms the operational
relevance of the DNS-KG approach proposal.
We note that before the implementation of the DNS-KG
proposal, the DNS configuration assessment (i.e. auditing and
cleaning tasks) was rarely conducted in such depth, if at all,
by the involved SecOps team. This allows us to conclude that
the overall DNS-KG approach improves operational efficiency
35 As for the toy example, parallel execution of SPARQL queries is possible,
enabling shorter overall assessment times.
36 Specific cases are undisclosed to protect Orange’s interests.

BRINGER AND TAILHARDAT: DSecO: DNS DATA AS A KNOWLEDGE GRAPH FOR ENHANCED SECURITY ANALYSIS

(from nearly infinite operation time to approximately 1.5 days
for internally managed records) by instilling confidence in the
corrective actions to be carried out over a large number of
records. Beyond operational efficiency, we also assessed learning and adoption among the SecOps team. Using the DSecO
online resources – notably the ontology documentation with
examples and the RML & SPARQL constructs – operation
engineers built their knowledge graph and ran queries within
a few hours. Although creating SPARQL queries from scratch
was initially challenging, Gherkin models and their connection
to existing queries enabled quick adaptation for user-defined
use cases. Furthermore, we observed that every instance of
non-compliance detected could be transformed into unit tests
for DSecO, as part of a continuous improvement cycle, thereby
strengthening confidence in the solution.
The
operational
complexity
observed
in
the
case
of
the
real-world
dataset
(i.e.
remediating
uc_complete_cleanup
versus
uc_domain_hijacking
and
uc_ip_hijacking)
raises questions about the scope of the knowledge graph
construction (KGC) step (i.e. are we missing some external
data that could help provide a more reliable diagnosis? is the
KGC step accurate regarding real-world data?) in relation
to the “almost zero doubt” goal for DNS configuration
assessment. Therefore, integrating additional non-managed
data & auditable KGC with data quality checks should be
further explored.
We also note that, based on the execution times in Table II,
the DNS-KG approach, while not real-time (focused on producing easily comprehensible and explainable results), exhibits
highly variable query execution durations for both LibOntology and GraphDB, with similar trends observed for both.
To begin with, comparing the timings of LibOntology and
GraphDB questions about the principle of minimizing the need
for specific or additional codebases and storage resources,
as discussed in Section III-C, and provides an indication
of the proportion and actual duration of query execution
time within the process. Indeed, with GraphDB, the initial
loading time of the graph is bypassed in the measurements
in Table II since the graph is loaded once at the beginning
of the process, whereas LibOntology requires loading the
graph into memory for each query execution. Taking this
further, comparing measurements across the use cases also
raises questions about the relationship between the size of
the DNS-KG (Table I), the formulation of use cases into
SPARQL queries (i.e. could the queries be rewritten for
lower algorithmic complexity? [23], [47]), and the inference
techniques used (e.g. would SHACL or SWRL be more efficient
regarding the expressiveness expected by the use cases? [2],
[5]). For example, the use case uc_ip_hijacking involves
adding dseco:isinOurSubnet true facts using a
SPARQL VALUE statement (Listing 13). Similarly, the
uc_entries_using_our_CDN implementation currently
combines a FILTER statement with a regular expression to match a dseco:hasName value pattern on a
dseco:is_CNAME_of property path. While functional, this
can be optimized for processing performance (time complexity
is O(n) for VALUE & FILTER statements and O(n) for

381

DFA-compiled regular expression against a string [47]) and
thoroughness (keeping subnet entities and FQDN name values
updated). Incorporating network topology data into the knowledge graph could improve network element selection efficiency
for the uc_entries_using_our_CDN case through graph
traversal and reduce regex reliance, though it would require
linking DSecO to third-party vocabularies to accommodate
new data objects (e.g. [30], [39]).
V. C ONCLUSION AND F UTURE W ORK
In this work, we aimed to simplify Domain Name System
(DNS) administration, particularly in systems where DNS
configuration information includes a large number of records,
originates from heterogeneous sources, and is managed by
different organizational units.
We initially hypothesized that an explicit graph representation could reflect the chaining nature of DNS records
and provide formal guarantees, notably in terms of a shared
understanding of the unified view of DNS records among
stakeholders, while also establishing actionable, explainable,
and shareable DNS administration rules.
Based on this idea, we proposed the “DNS-KG” approach,
which firstly involved conducting an analysis of DNS administration operations with SecOps experts from Orange. This
first step allowed us to define nine key use cases and formalize
them using a Behavior-Driven Development (BDD) approach.
The resulting structuring of the use cases proved beneficial
for establishing consensus among the experts and facilitating
the translation of the use cases into actionable rules. We
focused on auditing DNS records from diverse data sources
by creating an RDF knowledge graph structured with the
DSecO vocabulary, an open-source RDFS/OWL ontology we
implemented and make available at https://w3id.org/dseco.
This implementation derives from the use cases defined with
the SecOps experts and adheres to DNS standards defined
in RFCs. We used a declarative approach based on the
RML vocabulary for knowledge graph construction. DNS
configuration assessment is performed with SPARQL queries
corresponding to the nine use cases. The evaluation on a
toy example dataset confirmed the effective functioning of
the proposed DNS-KG approach. Similarly, the evaluation on
a real-world dataset highlighted the relevance of the DNSKG approach in an industrial setting, enabling SecOps teams
to confidently identify and resolve numerous non-compliant
DNS configurations. It also indicated that the inference process performance during the DNS-KG assessment step could
be enhanced by reducing the computational complexity of
SPARQL queries through the incorporation of additional data
during knowledge graph construction, rather than relying on
SPARQL FILTER statements.
Based on these insights, we are considering future work
along three axes. A first focus area is the extension of the
use cases. This can be achieved by conducting interviews
with a broader range of NetOps and SecOps experts, reviewing RFCs for configuration rules (e.g. RFC 1912 [6] on
common DNS operational and configuration errors), examining research papers for configuration corner cases (e.g. the
“zombie awakening” [15], TCB [45], and TsuNAME [12]

382

IEEE TRANSACTIONS ON NETWORKING, VOL. 34, 2026

concepts), and analyzing incident tickets in relation to DNSKG graph patterns [27]. Another approach is to tag DNS-KG
assessment cases with STIX/DRM [5] concepts or MITRE
ATT&CK techniques37 to create a reusable rule catalog based
on community-shared concepts. This tagging could also support downstream decision systems, such as ticketing systems,
where risk calculus, remediation prioritization, and causal
reasoning (e.g. on network reachability/connectivity incidents)
could be assessed through the DNS-KG.
A second focus is the extension of the input data range
and DSecO vocabulary. Indeed, we recognize that adding use
cases involves broadening the DSecO inference scope and
integrating more data sources (e.g. network topology, details
of Docker instances, CVEs) for knowledge graph construction.
This entails extending the DSecO ontology with new concepts
and relationships, such as NS, CAA, TXT, DNAME, NSEC3,
RRSIG, MX, and other DNS record types. It may also involve
strenghtening the linking of DSecO to other vocabularies (e.g.
UCO [56] & D3FEND [41] for cyber threat intelligence;
NORIA-O [30] & SEON [35] for information system topology
and operations; HTTPinRDF [21] for L7 details). For instance,
reasoning about HTTP redirect responses [43] as a graph
within a DNS-KG instance could assist NetOps & SecOps
in tracing the causes of network service performance issues
or cyberattacks. Similarly, “what if scenarios” reasoning on
potential service impact of changing an IP address or CNAME
could also assist NetOps & SecOps before planned network
changes.
Finally, a third focus area is the improvement of the technical
aspects of DNS-KG. Leveraging data provenance [34], [46] at
the DNS-KG level could help monitor data quality and inferences, increasing trust in the graph’s exploitation. In cases of
incomplete DNS data, inserting blank nodes to ensure use case
functionality is a potential solution to explore. Additionally,
investigating stream processing for the DNS-KG approach –
with RML rules for graph construction and SPARQL queries
remaining unchanged thanks to already existing tools [11],
[29] – may enable real-time applications. Although the current
use cases do not require stream processing, this could facilitate
higher-level use cases in network change or fault management. In a similar vein, integrating the DNS-KG approach
into Infrastructure-as-Code systems may prevent risky DNS
deployments, such as fast-failing CI/CD pipelines responsible
for DNS configuration. Lastly, improving graph enrichment
and assessment query performance might involve comparing
the execution time of current DNS-KG SPARQL queries
with their SWRL [5] and SHACL [2] equivalents. Since
SWRL performance degrades with increased dependencies [2],
this comparison can help establish an indicator for expected
expressiveness in DNS-KG use cases and guide the selection
of preferred inference techniques.
ACKNOWLEDGMENT
The authors would like to thank Maxime Jerome and DaoLam Trinh-Huu-Phap for their support on preparatory work
and for providing access to specific datasets. They appreciate
37 https://attack.mitre.org/techniques/enterprise/

Trialog38 for helping them initiate this work, and also would
like to express their gratitude to Antoine Cawet for his dedication and efforts in implementing and improving the DSecO
Project. They would also like to thank Yoan Chabot for reviewing and providing feedback on the preliminary version of this
article and IEEE/ACM T RANSACTIONS ON N ETWORKING
editorial committee and reviewers for their detailed analysis
and recommendations for improving the article.
R EFERENCES
[1]

A. Hogan et al., “Knowledge graphs,” ACM Comput. Surv., vol. 54,
no. 4, pp. 1–37, May 2022, doi: 10.1145/3447772.
[2] A. Guittoum, F. Aı̈ssaoui, S. Bolle, F. Boyer, and N. De Palma, “Inferring
threatening IoT dependencies using semantic digital twins toward
collaborative IoT device management,” in Proc. 38th ACM/SIGAPP
Symp. Appl. Comput., Mar. 2023, pp. 1732–1741, doi: 10.1145/
3555776.3578573.
[3] A. Dimou, “RML: A generic language for integrated rdf mappings of
heterogeneous data,” in Proc. Workshop Linked Data Web, LDOW CoLocated 23rd Int. World Wide Web Conf. (WWW), vol. 1184, 2014.
[4] B. Krebs. (2025). MasterCard DNS Error Went Unnoticed for Years.
[Online]. Available: https://krebsonsecurity.com/2025/01/mastercarddns-error-went-unnoticed-for-years/
[5] C. Sánchez-Zas, V. A. Villagrá, M. Vega-Barbas, X. Larriva-Novo,
J. I. Moreno, and J. Berrocal, “Ontology-based approach to realtime risk management and cyber-situational awareness,” Future Gener.
Comput. Syst., vol. 141, pp. 462–472, Apr. 2023, doi: 10.1016/
j.future.2022.12.006.
[6] D. Barr, Common DNS Operational and Configuration Errors, document
RFC 1912, 1996, doi: 10.17487/RFC1912.
[7] D. Liu, S. Hao, and H. Wang, “All your DNS records point to U.S.:
Understanding the security threats of dangling DNS records,” in Proc.
ACM SIGSAC Conf. Comput. Commun. Secur., New York, NY, USA,
Oct. 2016, pp. 1414–1425, doi: 10.1145/2976749.2978387.
[8] D. Liu, Z. Li, K. Du, H. Wang, B. Liu, and H. Duan, “Don’t let one
rotten apple spoil the whole barrel: Towards automated detection of
shadowed domains,” in Proc. ACM SIGSAC Conf. Comput. Commun.
Secur., New York, NY, USA, Oct. 2017, pp. 537–552, doi: 10.1145/
3133956.3134049.
[9] D. Brickley and R. V. Guha. (2014). RDF Schema 1.1. W3C. [Online].
Available: https://www.w3.org/TR/rdf-schema/
[10] D. Reynolds. (2014). The Organization Ontology. W3C Recommendation, W3C. [Online]. Available: https://www.w3.org/TR/vocab-org/
[11] D. F. Barbieri, D. Braga, S. Ceri, E. Della Valle, and M. Grossniklaus, “C-SPARQL: SPARQL for continuous querying,” in Proc. 18th
Int. Conf. World Wide Web, Apr. 2009, pp. 1061–1062, doi: 10.1145/
1526709.1526856.
[12] D. Kontokostas et al., “Test-driven evaluation of linked data quality,”
in Proc. 23rd Int. Conf. World Wide Web, Apr. 2014, pp. 747–758, doi:
10.1145/2566486.2568002.
[13] J. C. Klensin, Simple Mail Transfer Protocol, document RFC 5321,
2008, doi: 10.17487/RFC5321.
[14] D. Van Assche and C. Debruyne, “BURPing through RML test cases,”
in Proc. 5th Int. Workshop Knowl. Graph Construct. Co-Located With
21st Extended, Semantic Web Conf. (ESWC), vol. 3718, Hersonissos,
Greece, May 27, 2024.
[15] E. Alowaisheq, S. Tang, Z. Wang, F. Alharbi, X. Liao, and X. Wang,
“Zombie awakening: Stealthy hijacking of active domains through DNS
hosting referral,” in Proc. ACM SIGSAC Conf. Comput. Commun.
Secur., New York, NY, USA, Oct. 2020, pp. 1307–1322, doi: 10.1145/
3372297.3417864.
[16] E. S. Raymond, The Art of UNIX Programming: With Contributions
From Thirteen UNIX Pioneers, Including its Inventor, Ken Thompson
(Addison-Wesley Professional Computing Series). Reading, MA, USA:
Addison-Wesley, 2008.
[17] G. Akiwate et al., “Retroactive identification of targeted DNS infrastructure hijacking,” in Proc. 22nd ACM Internet Meas. Conf., Oct. 2022,
pp. 14–32, doi: 10.1145/3517745.3561425.
[18] G. C. M. Moura, S. Castro, J. Heidemann, and W. Hardaker,
“TsuNAME: Exploiting misconfiguration and vulnerability to DDoS
DNS,” in Proc. 21st ACM Internet Meas. Conf., Nov. 2021, pp. 398–418,
doi: 10.1145/3487552.3487824.
38 https://www.trialog.com/

BRINGER AND TAILHARDAT: DSecO: DNS DATA AS A KNOWLEDGE GRAPH FOR ENHANCED SECURITY ANALYSIS

[19] I. Horrocks, P. F. Patel-Schneider, H. Boley, S. Tabet, B. Grosof, and
M. Dean, “SWRL: A semantic web rule language combining OWL and
RuleML,” Nat. Res. Council Canada, Netw. Inference, Stanford Univ.,
Stanford, CA, USA, W3C Member Submission, Tech. Rep. SUBMSWRL-20040521, 2004.
[20] J. Hodges, C. Jackson, and A. Barth, HTTP Strict Transport Security
(HSTS), document RFC 6797, 2012, doi: 10.17487/RFC6797.
[21] J. Koch, C. A. Velasco, and P. Ackermann. (2017). HTTP Vocabulary in
RDF 1.0. W3C Working Group Note, W3C. [Online]. Available: https://
www.w3.org/TR/HTTP-in-RDF10
[22] J. A. Hawkinson and T. J. Bates, Guidelines for Creation, Selection,
and Registration of an Autonomous System (AS), document RFC 1930,
1996, doi: 10.17487/RFC1930.
[23] J. Pérez, M. Arenas, and C. Gutierrez, “Semantics and complexity of
SPARQL,” ACM Trans. Database Syst., vol. 34, no. 3, pp. 1–45, Aug.
2009, doi: 10.1145/1567274.1567278.
[24] K. Kurniawan, E. Kiesling, D. Winkler, and A. Ekelhart, “The ICS-SEC
KG: An integrated cybersecurity resource for industrial control systems,”
in The Semantic Web—ISWC 2024. Cham, Switzerland: Springer, 2025,
doi: 10.1007/978-3-031-77847-6 9.
[25] K. Hu, H. Du, and Y. Wang, “Heracles: A novel state-based distributed verification framework for DNS configurations,” in Proc.
SIGCOMM Workshop Formal Methods Aided Netw. Operation, Aug.
2024, pp. 27–32, doi: 10.1145/3672199.3673890.
[26] K. Borgolte, T. Fiebig, S. Hao, C. Kruegel, and G. Vigna, “Cloud
strife: Mitigating the security risks of domain-validated certificates,”
in Proc. Netw. Distrib. Syst. Secur. Symp., 2018, doi: 10.14722/
ndss.2018.23327. [Online]. Available: https://www.ndss-symposium.org/
ndss2018/acceptedpapers/
[27] L. Tailhardat, R. Troncy, and Y. Chabot, “Leveraging knowledge graphs
for classifying incident situations in ICT systems,” in Proc. 18th
Int. Conf. Availability, Rel. Secur., Aug. 2023, pp. 1–9, doi: 10.1145/
3600160.3604991.
[28] L. Tailhardat, Y. Chabot, A. Py, and P. Guillemette, “NORIA UI:
Efficient incident management on large-scale ICT systems represented
as knowledge graphs,” in Proc. 19th Int. Conf. Availability, Rel. Secur.,
Jul. 2024, pp. 1–10.
[29] L. Tailhardat, Y. Chabot, and R. Troncy, “Designing NORIA: A
knowledge graph-based platform for anomaly detection and incident
management in ICT systems,” in Proc. 4th Int. Workshop Knowl. Graph
Construct. (KGCW), vol. 3471, 2023, pp. 1–16.
[30] L. Tailhardat, Y. Chabot, and R. Troncy, “NORIA-O: An ontology for
anomaly detection and incident management in ICT systems,” in Proc.
Semantic Web 21st Int. Conf. (ESWC), Hersonissos, Greece, May 2024,
pp. 21–39, doi: 10.1007/978-3-031-60635-9 2.
[31] M. B. Salem and C. Wacek, “Enabling new technologies for cyber
security defense with the ICAS cyber security ontology,” in Proc. 10th
Conf. Semantic Technol. Intell., Defense, Secur., Fairfax VA, USA, 2015,
pp. 1–8.
[32] M. Poveda-Villalón, A. Fernández-Izquierdo, M. Fernández-López, and
R. Garcı́a-Castro, “LOT: An industrial oriented ontology engineering
framework,” Eng. Appl. Artif. Intell., vol. 111, May 2022, Art. no.
104755, doi: 10.1016/j.engappai.2022.104755.
[33] M. D. McIlroy, E. N. Pinson, and B. A. Tague, “UNIX time-sharing
system: Foreword,” Bell Syst. Tech. J., vol. 57, no. 6, pp. 1899–1904,
Jul. 1978. [Online]. Available: http://archive.org/details/bstj57-6-1899
[34] M. Herschel, R. Diestelkämper, and H. Ben Lahmar, “A survey on
provenance: What for? What form? What from?,” VLDB J., vol. 26,
no. 6, pp. 881–906, Dec. 2017, doi: 10.1007/s00778-017-0486-1.
[35] M. Würsch, G. Ghezzi, M. Hert, G. Reif, and H. C. Gall, “SEON:
A pyramid of ontologies for software evolution and its applications,”
Computing, vol. 94, no. 11, pp. 857–885, Nov. 2012, doi: 10.1007/
s00607-012-0204-1.
[36] M. Pasin. (2017). Ontopsy: Python Library and Command-Line Interface
for Inspecting and Visualizing RDF Models. [Online]. Available: https://
github.com/lambdamusic/ontospy
[37] M. Taghavi, “A knowledge graph to represent software vulnerabilities,”
M.S. thesis, Dept. Comput. Sci. Softw. Eng., Concordia Univ.,
Montreal, QC, Canada, 2023. [Online]. Available: https://
spectrum.library.concordia.ca/id/eprint/991794/
[38] M. Zhang. (2021). Bgpkit. [Online]. Available: https://bgpkit.com/
[39] O. Corcho et al., “A high-level ontology network for ICT
infrastructures,” in Proc. 20th Int. Semantic Web Conf. (ISWC), 2021,
doi: 10.1007/978-3-030-88361-4 26.
[40] P. Mockapetris, Domain Names–Implementation and Specification, document RFC 1035, 1987, doi: 10.17487/RFC1035.

383

[41] P. E. Kaloroumakis and M. J. Smith, “Toward a knowledge graph
of cybersecurity countermeasures,” MITRE Corporation, McLean, VA,
USA, Tech. Rep. D3FEND Paper, 2021.
[42] P. Hallam-Baker, R. Stradling, and J. Hoffman-Andrews, DNS Certification Authority Authorization (CAA) Resource Record, document RFC
8659, 2019, doi: 10.17487/RFC8659.
[43] R. Fielding, M. Nottingham, and J. Reschke, HTTP Semantics, document
RFC 9110, 2022, doi: 10.17487/RFC9110.
[44] R. Sommese, M. Jonker, R. van Rijswijk-Deij, A. Dainotti,
K. C. Claffy, and A. Sperotto, “The forgotten side of DNS: Orphan
and abandoned records,” in Proc. IEEE Eur. Symp. Secur. Privacy
Workshops (EuroS&PW), Sep. 2020, pp. 538–543, doi: 10.1109/
EUROSPW51379.2020.00079.
[45] V. Ramasubramanian and E. G. Sirer, “Perils of transitive trust in the
domain name system,” in Proc. 5th ACM SIGCOMM Conf. Internet
Meas. (IMC), 2005, p. 1, doi: 10.1145/1330107.1330152.
[46] R. Fontugne, M. Tashiro, R. Sommese, M. Jonker, Z. S. Bischof, and
E. Aben, “The wisdom of the measurement crowd: Building the internet
yellow pages a knowledge graph for the internet,” in Proc. ACM Internet
Meas. Conf., Nov. 2024, pp. 183–198, doi: 10.1145/3646547.3688444.
[47] Russ Cox.(2007). Regular Expression Matching Can Be Simple and Fast.
[Online]. Available: https://swtch.com/∼rsc/regexp/regexp1.html
[48] S. Dietzold, “Generating RDF models from LDAP directories,” in Proc.
SFSW Workshop Scripting Semantic Web, vol. 135, 2005, pp. 1–7.
[49] S. Chvez-Feria, R. Garca-Castro, and M. Poveda-Villaln, “Chowlk:
From UML-based ontology conceptualizations to OWL,” in Semantic
Web, vol. 13261. Cham, Switzerland: Springer, 2022, pp. 338–352, doi:
10.1007/978-3-031-06981-9 20.
[50] S. K. R. Kakarla, R. Beckett, B. Arzani, T. Millstein, and G. Varghese,
“GRooT: Proactive verification of DNS configurations,” in Proc. Annu.
Conf. ACM Special Interest Group Data Commun. Appl., Technol.,
Architectures, Protocols Comput. Commun., New York, NY, USA, Jul.
2020, pp. 310–328, doi: 10.1145/3387514.3405871.
[51] (2019). SmartBear Software: Gherkin Syntax. [Online]. Available:
https://cucumber.io/docs/gherkin/
[52] S. Wu, Y. Zhang, and W. Cao, “Network security assessment
using a semantic reasoning and graph based approach,” Comput. Electr. Eng., vol. 64, pp. 96–109, Nov. 2017, doi: 10.1016/
j.compeleceng.2017.02.001.
[53] S. S. Alqahtani, E. E. Eghan, and J. Rilling, “Tracing known security
vulnerabilities in software repositories—A semantic web enabled modeling approach,” Sci. Comput. Program., vol. 121, pp. 153–175, Jun.
2016, doi: 10.1016/j.scico.2016.01.005.
[54] W3C OWL Working Group. (2012). OWL 2 Web Ontology Language.
W3C. [Online]. Available: https://www.w3.org/TR/owl2-overview/
[55] W3C SPARQL Working Group. (2013). SPARQL 1.1. W3C. [Online].
Available: https://www.w3.org/TR/sparql11-overview/
[56] Z. Syed, A. Padia, M. L. Mathews, T. Finin, and A. Joshi, “UCO: A
unified cybersecurity ontology,” in Proc. AAAI Workshop Artif. Intell.
Cyber Secur., 2016, pp. 195–202.

Didier Bringer received the Engineering degree in computer science from
Polytech Montpellier, ISIM, France, in 1995, and the another Engineering
degree in cybersecurity and formal knowledge representation from the Conservatoire National des Arts et Métiers (CNAM), France, in 2022. Currently,
he is a full-time Cybersecurity Engineer with Orange Company, France.
Prior to specializing in cybersecurity, he was a System Engineer and the
IT Platform Manager for various companies. His research interests include
system vulnerability analysis, risk management, case-based reasoning, and
knowledge capture.

Lionel Tailhardat received the M.Sc. degree in telecommunication networks
and broadband technologies from the Conservatoire National des Arts et
Métiers (CNAM), France, in 2018, and the Ph.D. degree in data science and
knowledge engineering from EURECOM, Sorbonne University, France, in
2024. Currently, he is a full-time Researcher with Orange Research. Prior
to pursuing research, he held various positions in network operations and
monitoring system architecture. His research interests include distributed and
dynamic systems, data science and graph theory, coding schemes, and highperformance computing.
PAPER_TEXT
