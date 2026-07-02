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
# [032] Handbook of Applied Cryptography
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
编号：032
题名：Handbook of Applied Cryptography
年份：2018
DOI：10.1201/9781439821916
来源：未识别
PDF：paper/10.1201_9781439821916.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：基础理论、密码协议与安全机制
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\032.txt
- 原始字符数：2398462
- 本次发送字符数：140043
- 是否截断：True

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
HANDBOOK of

APPLIED
CRYPTOGRAPHY

Alfred J. Menezes
Paul C. van Oorschot
Scott A. Vanstone

Foreword
by R.L. Rivest
As we draw near to closing out the twentieth century, we see quite clearly that the
information-processing and telecommunications revolutions now underway will
continue vigorously into the twenty-first. We interact and transact by directing flocks
of digital packets towards each other through cyberspace, carrying love notes, digital
cash, and secret corporate documents. Our personal and economic lives rely more and
more on our ability to let such ethereal carrier pigeons mediate at a distance what we
used to do with face-to-face meetings, paper documents, and a firm handshake.
Unfortunately, the technical wizardry enabling remote collaborations is founded on
broadcasting everything as sequences of zeros and ones that one's own dog wouldn't
recognize. What is to distinguish a digital dollar when it is as easily reproducible as the
spoken word? How do we converse privately when every syllable is bounced off a
satellite and smeared over an entire continent? How should a bank know that it really is
Bill Gates requesting from his laptop in Fiji a transfer of $10,000,000,000 to another
bank? Fortunately, the magical mathematics of cryptography can help. Cryptography
provides techniques for keeping information secret, for determining that information
has not been tampered with, and for determining who authored pieces of information.
Cryptography is fascinating because of the close ties it forges between theory and
practice, and because today's practical applications of cryptography are pervasive and
critical components of our information-based society. Information-protection protocols
designed on theoretical foundations one year appear in products and standards
documents the next. Conversely, new theoretical developments sometimes mean that
last year's proposal has a previously unsuspected weakness. While the theory is
advancing vigorously, there are as yet few true guarantees; the security of many
proposals depends on unproven (if plausible) assumptions. The theoretical work refines
and improves the practice, while the practice challenges and inspires the theoretical
work. When a system is "broken," our knowledge improves, and next year's system is
improved to repair the defect. (One is reminded of the long and intriguing battle
between the designers of bank vaults and their opponents.)
Cryptography is also fascinating because of its game-like adversarial nature. A good
cryptographer rapidly changes sides back and forth in his or her thinking, from attacker
to defender and back. Just as in a game of chess, sequences of moves and countermoves must be considered until the current situation is understood. Unlike chess
players, cryptographers must also consider all the ways an adversary might try to gain
by breaking the rules or violating expectations. (Does it matter if she measures how
long I am computing? Does it matter if her "random" number isn't one?)
The current volume is a major contribution to the field of cryptography. It is a rigorous
encyclopedia of known techniques, with an emphasis on those that are both (believed to
be) secure and practically useful. It presents in a coherent manner most of the important
cryptographic tools one needs to implement secure cryptographic systems, and explains
many of the cryptographic principles and protocols of existing systems. The topics
covered range from low-level considerations such as random-number generation and
efficient modular exponentiation algorithms and medium-level items such as publickey signature techniques, to higher-level topics such as zero-knowledge protocols. This

book's excellent organization and style allow it to serve well as both a self-contained
tutorial and an indispensable desk reference.
In documenting the state of a fast-moving field, the authors have done incredibly well
at providing error-free comprehensive content that is up-to-date. Indeed, many of the
chapters, such as those on hash functions or key-establishment protocols, break new
ground in both their content and their unified presentations. In the trade-off between
comprehensive coverage and exhaustive treatment of individual items, the authors have
chosen to write simply and directly, and thus efficiently, allowing each element to be
explained together with their important details, caveats, and comparisons.
While motivated by practical applications, the authors have clearly written a book that
will be of as much interest to researchers and students as it is to practitioners, by
including ample discussion of the underlying mathematics and associated theoretical
considerations. The essential mathematical techniques and requisite notions are
presented crisply and clearly, with illustrative examples. The insightful historical notes
and extensive bibliography make this book a superb stepping-stone to the literature. (I
was very pleasantly surprised to find an appendix with complete programs for the
CRYPTO and EUROCRYPT conferences!)
It is a pleasure to have been asked to provide the foreword for this book. I am happy to
congratulate the authors on their accomplishment, and to inform the reader that he/she
is looking at a landmark in the development of the field.
Ronald L. Rivest
Webster Professor of Electrical Engineering and Computer Science
Massachusetts Institute of Technology
June 1996

Preface
This book is intended as a reference for professional cryptographers, presenting the
techniques and algorithms of greatest interest to the current practitioner, along with the supporting motivation and background material. It also provides a comprehensive source from
which to learn cryptography, serving both students and instructors. In addition, the rigorous treatment, breadth, and extensive bibliographic material should make it an important
reference for research professionals.
Our goal was to assimilate the existing cryptographic knowledge of industrial interest
into one consistent, self-contained volume accessible to engineers in practice, to computer
scientists and mathematicians in academia, and to motivated non-specialists with a strong
desire to learn cryptography. Such a task is beyond the scope of each of the following: research papers, which by nature focus on narrow topics using very specialized (and often
non-standard) terminology; survey papers, which typically address, at most, a small number of major topics at a high level; and (regretably also) most books, due to the fact that
many book authors lack either practical experience or familiarity with the research literature or both. Our intent was to provide a detailed presentation of those areas of cryptography which we have found to be of greatest practical utility in our own industrial experience,
while maintaining a sufficiently formal approach to be suitable both as a trustworthy reference for those whose primary interest is further research, and to provide a solid foundation
for students and others first learning the subject.
Throughout each chapter, we emphasize the relationship between various aspects of
cryptography. Background sections commence most chapters, providing a framework and
perspective for the techniques which follow. Computer source code (e.g. C code) for algorithms has been intentionally omitted, in favor of algorithms specified in sufficient detail to
allow direct implementation without consulting secondary references. We believe this style
of presentation allows a better understanding of how algorithms actually work, while at the
same time avoiding low-level implementation-specific constructs (which some readers will
invariably be unfamiliar with) of various currently-popular programming languages.
The presentation also strongly delineates what has been established as fact (by mathematical arguments) from what is simply current conjecture. To avoid obscuring the very
applied nature of the subject, rigorous proofs of correctness are in most cases omitted; however, references given in the Notes section at the end of each chapter indicate the original
or recommended sources for these results. The trailing Notes sections also provide information (quite detailed in places) on various additional techniques not addressed in the main
text, and provide a survey of research activities and theoretical results; references again indicate where readers may pursue particular aspects in greater depth. Needless to say, many
results, and indeed some entire research areas, have been given far less attention than they
warrant, or have been omitted entirely due to lack of space; we apologize in advance for
such major omissions, and hope that the most significant of these are brought to our attention.
To provide an integrated treatment of cryptography spanning foundational motivation
through concrete implementation, it is useful to consider a hierarchy of thought ranging
from conceptual ideas and end-user services, down to the tools necessary to complete actual implementations. Table 1 depicts the hierarchical structure around which this book is
organized. Corresponding to this, Figure 1 illustrates how these hierarchical levels map
xxiii

xxiv

Preface

Information Security Objectives
Confidentiality
Data integrity
Authentication (entity and data origin)
Non-repudiation
Cryptographic functions
Encryption
Chapters 6, 7, 8
Message authentication and data integrity techniques Chapter 9
Identification/entity authentication techniques
Chapter 10
Digital signatures
Chapter 11
Cryptographic building blocks
Stream ciphers
Chapter 6
Block ciphers (symmetric-key)
Chapter 7
Public-key encryption
Chapter 8
One-way hash functions (unkeyed)
Chapter 9
Message authentication codes
Chapter 9
Signature schemes (public-key, symmetric-key)
Chapter 11
Utilities
Public-key parameter generation
Chapter 4
Pseudorandom bit generation
Chapter 5
Efficient algorithms for discrete arithmetic
Chapter 14
Foundations
Introduction to cryptography
Chapter 1
Mathematical background
Chapter 2
Complexity and analysis of underlying problems
Chapter 3
Infrastructure techniques and commercial aspects
Key establishment protocols
Chapter 12
Key installation and key management
Chapter 13
Cryptographic patents
Chapter 15
Cryptographic standards
Chapter 15
Table 1: Hierarchical levels of applied cryptography.

onto the various chapters, and their inter-dependence.
Table 2 lists the chapters of the book, along with the primary author(s) of each who
should be contacted by readers with comments on specific chapters. Each chapter was written to provide a self-contained treatment of one major topic. Collectively, however, the
chapters have been designed and carefully integrated to be entirely complementary with
respect to definitions, terminology, and notation. Furthermore, there is essentially no duplication of material across chapters; instead, appropriate cross-chapter references are provided where relevant.
While it is not intended that this book be read linearly from front to back, the material
has been arranged so that doing so has some merit. Two primary goals motivated by the
“handbook” nature of this project were to allow easy access to stand-alone results, and to allow results and algorithms to be easily referenced (e.g., for discussion or subsequent crossreference). To facilitate the ease of accessing and referencing results, items have been categorized and numbered to a large extent, with the followingclasses of items jointlynumbered
consecutively in each chapter: Definitions, Examples, Facts, Notes, Remarks, Algorithms,
Protocols, and Mechanisms. In more traditional treatments, Facts are usually identified as
propositions, lemmas, or theorems. We use numbered Notes for additional technical points,

Figure 1: Roadmap of the book.

signatures

Chapter 13

standards

Chapter 15

Chapter 2

math
background
key management

patents and

Chapter 1

introduction

Chapter 12

Chapter 3

establishment of secret keys

Chapter 14

Chapter 11

signatures
(symmetric-key)

public-key

Chapter 11

(public-key)

Chapter 11

digital
signatures

non-repudiation

security foundations

Chapter 4

Chapter 5

Chapter 9

public-key
parameters

Chapter 9

(keyed)

random
number
generation

Chapter 8

hash functions

(unkeyed)

Chapter 10

identification

hash functions

Chapter 9

message
authentication

authentication

efficient

Chapter 7

Chapter 6

encryption
(public-key)

data integrity

implementation

block ciphers
(symmetric-key)

Chapter 9

Chapters 6,7,8

stream ciphers

data integrity
techniques

encryption

confidentiality

Preface
xxv

xxvi

Preface

Chapter
1.
2.
3.
4.
5.
6.
7.
8.
9.
10.
11.
12.
13.
14.
15.
—

Overview of Cryptography
Mathematical Background
Number-Theoretic Reference Problems
Public-Key Parameters
Pseudorandom Bits and Sequences
Stream Ciphers
Block Ciphers
Public-Key Encryption
Hash Functions and Data Integrity
Identification and Entity Authentication
Digital Signatures
Key Establishment Protocols
Key Management Techniques
Efficient Implementation
Patents and Standards
Overall organization

Primary Author
AJM PVO SAV
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*

Table 2: Primary authors of each chapter.

while numbered Remarks identify non-technical (often non-rigorous) comments, observations, and opinions. Algorithms, Protocols and Mechanisms refer to techniques involving
a series of steps. Examples, Notes, and Remarks generally begin with parenthetical summary titles to allow faster access, by indicating the nature of the content so that the entire
item itself need not be read in order to determine this. The use of a large number of small
subsections is also intended to enhance the handbook nature and accessibility to results.
Regarding the partitioning of subject areas into chapters, we have used what we call a
functional organization (based on functions of interest to end-users). For example, all items
related to entity authentication are addressed in one chapter. An alternative would have been
what may be called an academic organization, under which perhaps, all protocols based on
zero-knowledge concepts (including both a subset of entity authentication protocols and
signature schemes) might be covered in one chapter. We believe that a functional organization is more convenient to the practitioner, who is more likely to be interested in options
available for an entity authentication protocol (Chapter 10) or a signature scheme (Chapter
11), than to be seeking a zero-knowledge protocol with unspecified end-purpose.
In the front matter, a top-level Table of Contents (giving chapter numbers and titles
only) is provided, as well as a detailed Table of Contents (down to the level of subsections,
e.g., x5.1.1). This is followed by a List of Figures, and a List of Tables. At the start of each
chapter, a brief Table of Contents (specifying section number and titles only, e.g., x5.1, x5.2)
is also given for convenience.
At the end of the book, we have included a list of papers presented at each of the Crypto,
Eurocrypt, Asiacrypt/Auscrypt and Fast Software Encryption conferences to date, as well
as a list of all papers published in the Journal of Cryptology up to Volume 9. These are
in addition to the References section, each entry of which is cited at least once in the body
of the handbook. Almost all of these references have been verified for correctness in their
exact titles, volume and page numbers, etc. Finally, an extensive Index prepared by the
authors is included. The Index begins with a List of Symbols.
Our intention was not to introduce a collection of new techniques and protocols, but

Preface

xxvii

rather to selectively present techniques from those currently available in the public domain.
Such a consolidation of the literature is necessary from time to time. The fact that many
good books in this field include essentially no more than what is covered here in Chapters
7, 8 and 11 (indeed, these might serve as an introductory course along with Chapter 1) illustrates that the field has grown tremendously in the past 15 years. The mathematical foundation presented in Chapters 2 and 3 is hard to find in one volume, and missing from most
cryptography texts. The material in Chapter 4 on generation of public-key parameters, and
in Chapter 14 on efficient implementations, while well-known to a small body of specialists
and available in the scattered literature, has previously not been available in general texts.
The material in Chapters 5 and 6 on pseudorandom number generation and stream ciphers
is also often absent (many texts focus entirely on block ciphers), or approached only from
a theoretical viewpoint. Hash functions (Chapter 9) and identification protocols (Chapter
10) have only recently been studied in depth as specialized topics on their own, and along
with Chapter 12 on key establishment protocols, it is hard to find consolidated treatments
of these now-mainstream topics. Key management techniques as presented in Chapter 13
have traditionally not been given much attention by cryptographers, but are of great importance in practice. A focused treatment of cryptographic patents and a concise summary of
cryptographic standards, as presented in Chapter 15, are also long overdue.
In most cases (with some historical exceptions), where algorithms are known to be insecure, we have chosen to leave out specification of their details, because most such techniques are of little practical interest. Essentially all of the algorithms included have been
verified for correctness by independent implementation, confirming the test vectors specified.
Acknowledgements
This project would not have been possible without the tremendous efforts put forth by our
peers who have taken the time to read endless drafts and provide us with technical corrections, constructive feedback, and countless suggestions. In particular, the advice of our Advisory Editors has been invaluable, and it is impossible to attribute individualcredit for their
many suggestions throughout this book. Among our Advisory Editors, we would particularly like to thank:
Mihir Bellare
Burt Kaliski
Chris Mitchell
Gus Simmons
Yacov Yacobi

Don Coppersmith
Peter Landrock
Tatsuaki Okamoto
Miles Smid

Dorothy Denning
Arjen Lenstra
Bart Preneel
Jacques Stern

Walter Fumy
Ueli Maurer
Ron Rivest
Mike Wiener

In addition, we gratefully acknowledge the exceptionally large number of additional individuals who have helped improve the quality of this volume, by providing highly appreciated feedback and guidance on various matters. These individuals include:
Carlisle Adams
Simon Blackburn
Colin Boyd
Ed Dawson
Whit Diffie
Luis Encinas
Shuhong Gao
Jovan Golić

Rich Ankney
Ian Blake
Jörgen Brandt
Peter de Rooij
Hans Dobbertin
Warwick Ford
Will Gilbert
Dieter Gollmann

Tom Berson
Antoon Bosselaers
Mike Burmester
Yvo Desmedt
Carl Ellison
Amparo Fuster
Marc Girault
Li Gong

xxviii

Preface

Carrie Grant
Darrel Hankerson
Mike Just
Neal Koblitz
Evangelos Kranakis
Xuejia Lai
S. Mike Matyas
Mike Mosca
Volker Müeller
Kaisa Nyberg
Walter Penzhorn
Leon Pintsov
Matt Robshaw
Rainer Rueppel
Jeff Shallit
Andrea Vanstone
Jerry Veeh
Robert Zuccherato

Blake Greenlee
Anwar Hasan
Andy Klapper
Çetin Koç
David Kravitz
Charles Lam
Willi Meier
Tim Moses
David Naccache
Andrew Odlyzko
Birgit Pfitzmann
Fred Piper
Peter Rodney
Mahmoud Salmasizadeh
Jon Sorenson
Serge Vaudenay
Fausto Vitini

Helen Gustafson
Don Johnson
Lars Knudsen
Judy Koeller
Hugo Krawczyk
Alan Ling
Peter Montgomery
Serge Mister
James Nechvatal
Richard Outerbridge
Kevin Phelps
Carl Pomerance
Phil Rogaway
Roger Schlafly
Doug Stinson
Klaus Vedder
Lisa Yin

We apologize to those whose names have inadvertently escaped this list. Special thanks are
due to Carrie Grant, Darrel Hankerson, Judy Koeller, Charles Lam, and Andrea Vanstone.
Their hard work contributed greatly to the quality of this book, and it was truly a pleasure
working with them. Thanks also to the folks at CRC Press, including Tia Atchison, Gary
Bennett, Susie Carlisle, Nora Konopka, Mary Kugler, Amy Morrell, Tim Pletscher, Bob
Stern, and Wayne Yuhasz. The second author would like to thank his colleagues past and
present at Nortel Secure Networks (Bell-Northern Research), many of whom are mentioned
above, for their contributions on this project, and in particular Brian O’Higgins for his encouragement and support; all views expressed, however, are entirely that of the author. The
third author would also like to acknowledge the support of the Natural Sciences and Engineering Research Council.
Any errors that remain are, of course, entirely our own. We would be grateful if readers
who spot errors, missing references or credits, or incorrectly attributed results would contact
us with details. It is our hope that this volume facilitates further advancement of the field,
and that we have helped play a small part in this.

Alfred J. Menezes
Paul C. van Oorschot
Scott A. Vanstone
August, 1996

Table of Contents
List of Tables
List of Figures
Foreword by R.L. Rivest
Preface

xv
xix
xxi
xxiii

1 Overview of Cryptography
1.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
1.2 Information security and cryptography : : : : : : : : : : : : : : : : : :
1.3 Background on functions : : : : : : : : : : : : : : : : : : : : : : : : :
1.3.1 Functions (1-1, one-way, trapdoor one-way) : : : : : : : : : : : :
1.3.2 Permutations : : : : : : : : : : : : : : : : : : : : : : : : : : : :
1.3.3 Involutions : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
1.4 Basic terminology and concepts : : : : : : : : : : : : : : : : : : : : : :
1.5 Symmetric-key encryption : : : : : : : : : : : : : : : : : : : : : : : :
1.5.1 Overview of block ciphers and stream ciphers : : : : : : : : : : :
1.5.2 Substitution ciphers and transposition ciphers : : : : : : : : : : :
1.5.3 Composition of ciphers : : : : : : : : : : : : : : : : : : : : : :
1.5.4 Stream ciphers : : : : : : : : : : : : : : : : : : : : : : : : : : :
1.5.5 The key space : : : : : : : : : : : : : : : : : : : : : : : : : : :
1.6 Digital signatures : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
1.7 Authentication and identification : : : : : : : : : : : : : : : : : : : : :
1.7.1 Identification : : : : : : : : : : : : : : : : : : : : : : : : : : : :
1.7.2 Data origin authentication : : : : : : : : : : : : : : : : : : : : :
1.8 Public-key cryptography : : : : : : : : : : : : : : : : : : : : : : : : :
1.8.1 Public-key encryption : : : : : : : : : : : : : : : : : : : : : : :
1.8.2 The necessity of authentication in public-key systems : : : : : : :
1.8.3 Digital signatures from reversible public-key encryption : : : : : :
1.8.4 Symmetric-key vs. public-key cryptography : : : : : : : : : : : :
1.9 Hash functions : : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
1.10 Protocols and mechanisms : : : : : : : : : : : : : : : : : : : : : : : : :
1.11 Key establishment, management, and certification : : : : : : : : : : : : :
1.11.1 Key management through symmetric-key techniques : : : : : : :
1.11.2 Key management through public-key techniques : : : : : : : : : :
1.11.3 Trusted third parties and public-key certificates : : : : : : : : : :
1.12 Pseudorandom numbers and sequences : : : : : : : : : : : : : : : : : :
1.13 Classes of attacks and security models : : : : : : : : : : : : : : : : : :
1.13.1 Attacks on encryption schemes : : : : : : : : : : : : : : : : : :
1.13.2 Attacks on protocols : : : : : : : : : : : : : : : : : : : : : : : :
1.13.3 Models for evaluating security : : : : : : : : : : : : : : : : : : :
1.13.4 Perspective for computational security : : : : : : : : : : : : : : :
1.14 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : :

v

1
1
2
6
6
10
10
11
15
15
17
19
20
21
22
24
24
25
25
25
27
28
31
33
33
35
36
37
39
39
41
41
42
42
44
45

vi

Table of Contents

2 Mathematical Background
2.1 Probability theory : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.1.1 Basic definitions : : : : : : : : : : : : : : : : : : : : : : : : : :
2.1.2 Conditional probability : : : : : : : : : : : : : : : : : : : : : :
2.1.3 Random variables : : : : : : : : : : : : : : : : : : : : : : : : :
2.1.4 Binomial distribution : : : : : : : : : : : : : : : : : : : : : : :
2.1.5 Birthday attacks : : : : : : : : : : : : : : : : : : : : : : : : : :
2.1.6 Random mappings : : : : : : : : : : : : : : : : : : : : : : : : :
2.2 Information theory : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.2.1 Entropy : : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.2.2 Mutual information : : : : : : : : : : : : : : : : : : : : : : : :
2.3 Complexity theory : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.3.1 Basic definitions : : : : : : : : : : : : : : : : : : : : : : : : : :
2.3.2 Asymptotic notation : : : : : : : : : : : : : : : : : : : : : : : :
2.3.3 Complexity classes : : : : : : : : : : : : : : : : : : : : : : : : :
2.3.4 Randomized algorithms : : : : : : : : : : : : : : : : : : : : : :
2.4 Number theory : : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.4.1 The integers : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.4.2 Algorithms in
: : : : : : : : : : : : : : : : : : : : : : : : : :
2.4.3 The integers modulo n : : : : : : : : : : : : : : : : : : : : : : :
2.4.4 Algorithms in n : : : : : : : : : : : : : : : : : : : : : : : : :
2.4.5 The Legendre and Jacobi symbols : : : : : : : : : : : : : : : : :
2.4.6 Blum integers : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.5 Abstract algebra : : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.5.1 Groups : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.5.2 Rings : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.5.3 Fields : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.5.4 Polynomial rings : : : : : : : : : : : : : : : : : : : : : : : : : :
2.5.5 Vector spaces : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.6 Finite fields : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : :
2.6.1 Basic properties : : : : : : : : : : : : : : : : : : : : : : : : : :
2.6.2 The Euclidean algorithm for polynomials : : : : : : : : : : : : :
2.6.3 Arithmetic of polynomials : : : : : : : : : : : : : : : : : : : : :
2.7 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : :

Z
Z

49
50
50
51
51
52
53
54
56
56
57
57
57
58
59
62
63
63
66
67
71
72
74
75
75
76
77
78
79
80
80
81
83
85

3 Number-Theoretic Reference Problems
87
3.1 Introduction and overview : : : : : : : : : : : : : : : : : : : : : : : : : 87
3.2 The integer factorization problem : : : : : : : : : : : : : : : : : : : : : 89
3.2.1 Trial division : : : : : : : : : : : : : : : : : : : : : : : : : : : : 90
3.2.2 Pollard’s rho factoring algorithm : : : : : : : : : : : : : : : : : : 91
3.2.3 Pollard’s p ; 1 factoring algorithm : : : : : : : : : : : : : : : : 92
3.2.4 Elliptic curve factoring : : : : : : : : : : : : : : : : : : : : : : : 94
3.2.5 Random square factoring methods : : : : : : : : : : : : : : : : : 94
3.2.6 Quadratic sieve factoring : : : : : : : : : : : : : : : : : : : : : : 95
3.2.7 Number field sieve factoring : : : : : : : : : : : : : : : : : : : : 98
3.3 The RSA problem : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 98
3.4 The quadratic residuosity problem : : : : : : : : : : : : : : : : : : : : : 99
3.5 Computing square roots in n : : : : : : : : : : : : : : : : : : : : : : : 99
3.5.1 Case (i): n prime : : : : : : : : : : : : : : : : : : : : : : : : : : 100
3.5.2 Case (ii): n composite : : : : : : : : : : : : : : : : : : : : : : : 101

Z

Table of Contents

vii

3.6

The discrete logarithm problem : : : : : : : : : : : : : : : : : : : : : : 103
3.6.1 Exhaustive search : : : : : : : : : : : : : : : : : : : : : : : : : 104
3.6.2 Baby-step giant-step algorithm : : : : : : : : : : : : : : : : : : : 104
3.6.3 Pollard’s rho algorithm for logarithms : : : : : : : : : : : : : : : 106
3.6.4 Pohlig-Hellman algorithm : : : : : : : : : : : : : : : : : : : : : 107
3.6.5 Index-calculus algorithm : : : : : : : : : : : : : : : : : : : : : : 109
3.6.6 Discrete logarithm problem in subgroups of p : : : : : : : : : : 113
3.7 The Diffie-Hellman problem : : : : : : : : : : : : : : : : : : : : : : : 113
3.8 Composite moduli : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 114
3.9 Computing individual bits : : : : : : : : : : : : : : : : : : : : : : : : : 114
3.9.1 The discrete logarithm problem in p — individual bits : : : : : : 116
3.9.2 The RSA problem — individual bits : : : : : : : : : : : : : : : : 116
3.9.3 The Rabin problem — individual bits : : : : : : : : : : : : : : : 117
3.10 The subset sum problem : : : : : : : : : : : : : : : : : : : : : : : : : : 117
3.10.1 The L3 -lattice basis reduction algorithm : : : : : : : : : : : : : : 118
3.10.2 Solving subset sum problems of low density : : : : : : : : : : : : 120
3.10.3 Simultaneous diophantine approximation : : : : : : : : : : : : : 121
3.11 Factoring polynomials over finite fields : : : : : : : : : : : : : : : : : : 122
3.11.1 Square-free factorization : : : : : : : : : : : : : : : : : : : : : : 123
3.11.2 Berlekamp’s Q-matrix algorithm : : : : : : : : : : : : : : : : : : 124
3.12 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 125

Z

Z

4 Public-Key Parameters
133
4.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 133
4.1.1 Generating large prime numbers naively : : : : : : : : : : : : : : 134
4.1.2 Distribution of prime numbers : : : : : : : : : : : : : : : : : : : 134
4.2 Probabilistic primality tests : : : : : : : : : : : : : : : : : : : : : : : : 135
4.2.1 Fermat’s test : : : : : : : : : : : : : : : : : : : : : : : : : : : : 136
4.2.2 Solovay-Strassen test : : : : : : : : : : : : : : : : : : : : : : : 137
4.2.3 Miller-Rabin test : : : : : : : : : : : : : : : : : : : : : : : : : : 138
4.2.4 Comparison: Fermat, Solovay-Strassen, and Miller-Rabin : : : : : 140
4.3 (True) Primality tests : : : : : : : : : : : : : : : : : : : : : : : : : : : 142
4.3.1 Testing Mersenne numbers : : : : : : : : : : : : : : : : : : : : : 142
4.3.2 Primality testing using the factorization of n ; 1 : : : : : : : : : 143
4.3.3 Jacobi sum test : : : : : : : : : : : : : : : : : : : : : : : : : : : 144
4.3.4 Tests using elliptic curves : : : : : : : : : : : : : : : : : : : : : 145
4.4 Prime number generation : : : : : : : : : : : : : : : : : : : : : : : : : 145
4.4.1 Random search for probable primes : : : : : : : : : : : : : : : : 145
4.4.2 Strong primes : : : : : : : : : : : : : : : : : : : : : : : : : : : 149
4.4.3 NIST method for generating DSA primes : : : : : : : : : : : : : 150
4.4.4 Constructive techniques for provable primes : : : : : : : : : : : : 152
4.5 Irreducible polynomials over p : : : : : : : : : : : : : : : : : : : : : : 154
4.5.1 Irreducible polynomials : : : : : : : : : : : : : : : : : : : : : : 154
4.5.2 Irreducible trinomials : : : : : : : : : : : : : : : : : : : : : : : 157
4.5.3 Primitive polynomials : : : : : : : : : : : : : : : : : : : : : : : 157
4.6 Generators and elements of high order : : : : : : : : : : : : : : : : : : 160
4.6.1 Selecting a prime p and generator of p : : : : : : : : : : : : : : 164
4.7 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 165

Z

Z

viii

Table of Contents

5 Pseudorandom Bits and Sequences
169
5.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 169
5.1.1 Background and Classification : : : : : : : : : : : : : : : : : : : 170
5.2 Random bit generation : : : : : : : : : : : : : : : : : : : : : : : : : : 171
5.3 Pseudorandom bit generation : : : : : : : : : : : : : : : : : : : : : : : 173
5.3.1 ANSI X9.17 generator : : : : : : : : : : : : : : : : : : : : : : : 173
5.3.2 FIPS 186 generator : : : : : : : : : : : : : : : : : : : : : : : : : 174
5.4 Statistical tests : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 175
5.4.1 The normal and chi-square distributions : : : : : : : : : : : : : : 176
5.4.2 Hypothesis testing : : : : : : : : : : : : : : : : : : : : : : : : : 179
5.4.3 Golomb’s randomness postulates : : : : : : : : : : : : : : : : : : 180
5.4.4 Five basic tests : : : : : : : : : : : : : : : : : : : : : : : : : : : 181
5.4.5 Maurer’s universal statistical test : : : : : : : : : : : : : : : : : 183
5.5 Cryptographically secure pseudorandom bit generation : : : : : : : : : : 185
5.5.1 RSA pseudorandom bit generator : : : : : : : : : : : : : : : : : 185
5.5.2 Blum-Blum-Shub pseudorandom bit generator : : : : : : : : : : : 186
5.6 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 187
6 Stream Ciphers
191
6.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 191
6.1.1 Classification : : : : : : : : : : : : : : : : : : : : : : : : : : : 192
6.2 Feedback shift registers : : : : : : : : : : : : : : : : : : : : : : : : : : 195
6.2.1 Linear feedback shift registers : : : : : : : : : : : : : : : : : : : 195
6.2.2 Linear complexity : : : : : : : : : : : : : : : : : : : : : : : : : 198
6.2.3 Berlekamp-Massey algorithm : : : : : : : : : : : : : : : : : : : 200
6.2.4 Nonlinear feedback shift registers : : : : : : : : : : : : : : : : : 202
6.3 Stream ciphers based on LFSRs : : : : : : : : : : : : : : : : : : : : : : 203
6.3.1 Nonlinear combination generators : : : : : : : : : : : : : : : : : 205
6.3.2 Nonlinear filter generators : : : : : : : : : : : : : : : : : : : : : 208
6.3.3 Clock-controlled generators : : : : : : : : : : : : : : : : : : : : 209
6.4 Other stream ciphers : : : : : : : : : : : : : : : : : : : : : : : : : : : : 212
6.4.1 SEAL : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 213
6.5 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 216
7 Block Ciphers
223
7.1 Introduction and overview : : : : : : : : : : : : : : : : : : : : : : : : : 223
7.2 Background and general concepts : : : : : : : : : : : : : : : : : : : : : 224
7.2.1 Introduction to block ciphers : : : : : : : : : : : : : : : : : : : : 224
7.2.2 Modes of operation : : : : : : : : : : : : : : : : : : : : : : : : 228
7.2.3 Exhaustive key search and multiple encryption : : : : : : : : : : 233
7.3 Classical ciphers and historical development : : : : : : : : : : : : : : : 237
7.3.1 Transposition ciphers (background) : : : : : : : : : : : : : : : : 238
7.3.2 Substitution ciphers (background) : : : : : : : : : : : : : : : : : 238
7.3.3 Polyalphabetic substitutions and Vigenère ciphers (historical) : : : 241
7.3.4 Polyalphabetic cipher machines and rotors (historical) : : : : : : : 242
7.3.5 Cryptanalysis of classical ciphers (historical) : : : : : : : : : : : 245
7.4 DES : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 250
7.4.1 Product ciphers and Feistel ciphers : : : : : : : : : : : : : : : : : 250
7.4.2 DES algorithm : : : : : : : : : : : : : : : : : : : : : : : : : : : 252
7.4.3 DES properties and strength : : : : : : : : : : : : : : : : : : : : 256

Table of Contents

7.5
7.6
7.7

7.8

ix

FEAL : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 259
IDEA : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 263
SAFER, RC5, and other block ciphers : : : : : : : : : : : : : : : : : : : 266
7.7.1 SAFER : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 266
7.7.2 RC5 : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 269
7.7.3 Other block ciphers : : : : : : : : : : : : : : : : : : : : : : : : 270
Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 271

8 Public-Key Encryption
283
8.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 283
8.1.1 Basic principles : : : : : : : : : : : : : : : : : : : : : : : : : : 284
8.2 RSA public-key encryption : : : : : : : : : : : : : : : : : : : : : : : : 285
8.2.1 Description : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 286
8.2.2 Security of RSA : : : : : : : : : : : : : : : : : : : : : : : : : : 287
8.2.3 RSA encryption in practice : : : : : : : : : : : : : : : : : : : : 290
8.3 Rabin public-key encryption : : : : : : : : : : : : : : : : : : : : : : : : 292
8.4 ElGamal public-key encryption : : : : : : : : : : : : : : : : : : : : : : 294
8.4.1 Basic ElGamal encryption : : : : : : : : : : : : : : : : : : : : : 294
8.4.2 Generalized ElGamal encryption : : : : : : : : : : : : : : : : : : 297
8.5 McEliece public-key encryption : : : : : : : : : : : : : : : : : : : : : : 298
8.6 Knapsack public-key encryption : : : : : : : : : : : : : : : : : : : : : : 300
8.6.1 Merkle-Hellman knapsack encryption : : : : : : : : : : : : : : : 300
8.6.2 Chor-Rivest knapsack encryption : : : : : : : : : : : : : : : : : 302
8.7 Probabilistic public-key encryption : : : : : : : : : : : : : : : : : : : : 306
8.7.1 Goldwasser-Micali probabilistic encryption : : : : : : : : : : : : 307
8.7.2 Blum-Goldwasser probabilistic encryption : : : : : : : : : : : : : 308
8.7.3 Plaintext-aware encryption : : : : : : : : : : : : : : : : : : : : : 311
8.8 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 312
9 Hash Functions and Data Integrity
321
9.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 321
9.2 Classification and framework : : : : : : : : : : : : : : : : : : : : : : : 322
9.2.1 General classification : : : : : : : : : : : : : : : : : : : : : : : 322
9.2.2 Basic properties and definitions : : : : : : : : : : : : : : : : : : 323
9.2.3 Hash properties required for specific applications : : : : : : : : : 327
9.2.4 One-way functions and compression functions : : : : : : : : : : : 327
9.2.5 Relationships between properties : : : : : : : : : : : : : : : : : 329
9.2.6 Other hash function properties and applications : : : : : : : : : : 330
9.3 Basic constructions and general results : : : : : : : : : : : : : : : : : : 332
9.3.1 General model for iterated hash functions : : : : : : : : : : : : : 332
9.3.2 General constructions and extensions : : : : : : : : : : : : : : : 333
9.3.3 Formatting and initialization details : : : : : : : : : : : : : : : : 334
9.3.4 Security objectives and basic attacks : : : : : : : : : : : : : : : : 335
9.3.5 Bitsizes required for practical security : : : : : : : : : : : : : : : 337
9.4 Unkeyed hash functions (MDCs) : : : : : : : : : : : : : : : : : : : : : 338
9.4.1 Hash functions based on block ciphers : : : : : : : : : : : : : : : 338
9.4.2 Customized hash functions based on MD4 : : : : : : : : : : : : : 343
9.4.3 Hash functions based on modular arithmetic : : : : : : : : : : : : 351
9.5 Keyed hash functions (MACs) : : : : : : : : : : : : : : : : : : : : : : 352
9.5.1 MACs based on block ciphers : : : : : : : : : : : : : : : : : : : 353

x

Table of Contents

9.6

9.7

9.8

9.5.2 Constructing MACs from MDCs : : : : : : : : : : : : : : : : : : 354
9.5.3 Customized MACs : : : : : : : : : : : : : : : : : : : : : : : : : 356
9.5.4 MACs for stream ciphers : : : : : : : : : : : : : : : : : : : : : 358
Data integrity and message authentication : : : : : : : : : : : : : : : : : 359
9.6.1 Background and definitions : : : : : : : : : : : : : : : : : : : : 359
9.6.2 Non-malicious vs. malicious threats to data integrity : : : : : : : : 362
9.6.3 Data integrity using a MAC alone : : : : : : : : : : : : : : : : : 364
9.6.4 Data integrity using an MDC and an authentic channel : : : : : : 364
9.6.5 Data integrity combined with encryption : : : : : : : : : : : : : : 364
Advanced attacks on hash functions : : : : : : : : : : : : : : : : : : : : 368
9.7.1 Birthday attacks : : : : : : : : : : : : : : : : : : : : : : : : : : 369
9.7.2 Pseudo-collisions and compression function attacks : : : : : : : : 371
9.7.3 Chaining attacks : : : : : : : : : : : : : : : : : : : : : : : : : : 373
9.7.4 Attacks based on properties of underlying cipher : : : : : : : : : 375
Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 376

10 Identification and Entity Authentication
385
10.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 385
10.1.1 Identification objectives and applications : : : : : : : : : : : : : 386
10.1.2 Properties of identification protocols : : : : : : : : : : : : : : : : 387
10.2 Passwords (weak authentication) : : : : : : : : : : : : : : : : : : : : : 388
10.2.1 Fixed password schemes: techniques : : : : : : : : : : : : : : : 389
10.2.2 Fixed password schemes: attacks : : : : : : : : : : : : : : : : : 391
10.2.3 Case study – UNIX passwords : : : : : : : : : : : : : : : : : : : 393
10.2.4 PINs and passkeys : : : : : : : : : : : : : : : : : : : : : : : : : 394
10.2.5 One-time passwords (towards strong authentication) : : : : : : : : 395
10.3 Challenge-response identification (strong authentication) : : : : : : : : : 397
10.3.1 Background on time-variant parameters : : : : : : : : : : : : : : 397
10.3.2 Challenge-response by symmetric-key techniques : : : : : : : : : 400
10.3.3 Challenge-response by public-key techniques : : : : : : : : : : : 403
10.4 Customized and zero-knowledge identification protocols : : : : : : : : : 405
10.4.1 Overview of zero-knowledge concepts : : : : : : : : : : : : : : : 405
10.4.2 Feige-Fiat-Shamir identification protocol : : : : : : : : : : : : : 410
10.4.3 GQ identification protocol : : : : : : : : : : : : : : : : : : : : : 412
10.4.4 Schnorr identification protocol : : : : : : : : : : : : : : : : : : : 414
10.4.5 Comparison: Fiat-Shamir, GQ, and Schnorr : : : : : : : : : : : : 416
10.5 Attacks on identification protocols : : : : : : : : : : : : : : : : : : : : 417
10.6 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 420
11 Digital Signatures
425
11.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 425
11.2 A framework for digital signature mechanisms : : : : : : : : : : : : : : 426
11.2.1 Basic definitions : : : : : : : : : : : : : : : : : : : : : : : : : : 426
11.2.2 Digital signature schemes with appendix : : : : : : : : : : : : : : 428
11.2.3 Digital signature schemes with message recovery : : : : : : : : : 430
11.2.4 Types of attacks on signature schemes : : : : : : : : : : : : : : : 432
11.3 RSA and related signature schemes : : : : : : : : : : : : : : : : : : : : 433
11.3.1 The RSA signature scheme : : : : : : : : : : : : : : : : : : : : 433
11.3.2 Possible attacks on RSA signatures : : : : : : : : : : : : : : : : 434
11.3.3 RSA signatures in practice : : : : : : : : : : : : : : : : : : : : : 435

Table of Contents

11.4

11.5

11.6

11.7

11.8

11.9

xi

11.3.4 The Rabin public-key signature scheme : : : : : : : : : : : : : : 438
11.3.5 ISO/IEC 9796 formatting : : : : : : : : : : : : : : : : : : : : : 442
11.3.6 PKCS #1 formatting : : : : : : : : : : : : : : : : : : : : : : : : 445
Fiat-Shamir signature schemes : : : : : : : : : : : : : : : : : : : : : : 447
11.4.1 Feige-Fiat-Shamir signature scheme : : : : : : : : : : : : : : : : 447
11.4.2 GQ signature scheme : : : : : : : : : : : : : : : : : : : : : : : 450
The DSA and related signature schemes : : : : : : : : : : : : : : : : : : 451
11.5.1 The Digital Signature Algorithm (DSA) : : : : : : : : : : : : : : 452
11.5.2 The ElGamal signature scheme : : : : : : : : : : : : : : : : : : 454
11.5.3 The Schnorr signature scheme : : : : : : : : : : : : : : : : : : : 459
11.5.4 The ElGamal signature scheme with message recovery : : : : : : 460
One-time digital signatures : : : : : : : : : : : : : : : : : : : : : : : : 462
11.6.1 The Rabin one-time signature scheme : : : : : : : : : : : : : : : 462
11.6.2 The Merkle one-time signature scheme : : : : : : : : : : : : : : 464
11.6.3 Authentication trees and one-time signatures : : : : : : : : : : : : 466
11.6.4 The GMR one-time signature scheme : : : : : : : : : : : : : : : 468
Other signature schemes : : : : : : : : : : : : : : : : : : : : : : : : : : 471
11.7.1 Arbitrated digital signatures : : : : : : : : : : : : : : : : : : : : 472
11.7.2 ESIGN : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 473
Signatures with additional functionality : : : : : : : : : : : : : : : : : : 474
11.8.1 Blind signature schemes : : : : : : : : : : : : : : : : : : : : : : 475
11.8.2 Undeniable signature schemes : : : : : : : : : : : : : : : : : : : 476
11.8.3 Fail-stop signature schemes : : : : : : : : : : : : : : : : : : : : 478
Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 481

12 Key Establishment Protocols
489
12.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 489
12.2 Classification and framework : : : : : : : : : : : : : : : : : : : : : : : 490
12.2.1 General classification and fundamental concepts : : : : : : : : : : 490
12.2.2 Objectives and properties : : : : : : : : : : : : : : : : : : : : : 493
12.2.3 Assumptions and adversaries in key establishment protocols : : : : 495
12.3 Key transport based on symmetric encryption : : : : : : : : : : : : : : : 497
12.3.1 Symmetric key transport and derivation without a server : : : : : 497
12.3.2 Kerberos and related server-based protocols : : : : : : : : : : : : 500
12.4 Key agreement based on symmetric techniques : : : : : : : : : : : : : : 505
12.5 Key transport based on public-key encryption : : : : : : : : : : : : : : : 506
12.5.1 Key transport using PK encryption without signatures : : : : : : : 507
12.5.2 Protocols combining PK encryption and signatures : : : : : : : : 509
12.5.3 Hybrid key transport protocols using PK encryption : : : : : : : : 512
12.6 Key agreement based on asymmetric techniques : : : : : : : : : : : : : 515
12.6.1 Diffie-Hellman and related key agreement protocols : : : : : : : : 515
12.6.2 Implicitly-certified public keys : : : : : : : : : : : : : : : : : : : 520
12.6.3 Diffie-Hellman protocols using implicitly-certified keys : : : : : : 522
12.7 Secret sharing : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 524
12.7.1 Simple shared control schemes : : : : : : : : : : : : : : : : : : : 524
12.7.2 Threshold schemes : : : : : : : : : : : : : : : : : : : : : : : : : 525
12.7.3 Generalized secret sharing : : : : : : : : : : : : : : : : : : : : : 526
12.8 Conference keying : : : : : : : : : : : : : : : : : : : : : : : : : : : : 528
12.9 Analysis of key establishment protocols : : : : : : : : : : : : : : : : : : 530
12.9.1 Attack strategies and classic protocol flaws : : : : : : : : : : : : 530

xii

Table of Contents

12.9.2 Analysis objectives and methods : : : : : : : : : : : : : : : : : : 532
12.10 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 534
13 Key Management Techniques
543
13.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 543
13.2 Background and basic concepts : : : : : : : : : : : : : : : : : : : : : : 544
13.2.1 Classifying keys by algorithm type and intended use : : : : : : : : 544
13.2.2 Key management objectives, threats, and policy : : : : : : : : : : 545
13.2.3 Simple key establishment models : : : : : : : : : : : : : : : : : 546
13.2.4 Roles of third parties : : : : : : : : : : : : : : : : : : : : : : : : 547
13.2.5 Tradeoffs among key establishment protocols : : : : : : : : : : : 550
13.3 Techniques for distributing confidential keys : : : : : : : : : : : : : : : 551
13.3.1 Key layering and cryptoperiods : : : : : : : : : : : : : : : : : : 551
13.3.2 Key translation centers and symmetric-key certificates : : : : : : : 553
13.4 Techniques for distributing public keys : : : : : : : : : : : : : : : : : : 555
13.4.1 Authentication trees : : : : : : : : : : : : : : : : : : : : : : : : 556
13.4.2 Public-key certificates : : : : : : : : : : : : : : : : : : : : : : : 559
13.4.3 Identity-based systems : : : : : : : : : : : : : : : : : : : : : : : 561
13.4.4 Implicitly-certified public keys : : : : : : : : : : : : : : : : : : : 562
13.4.5 Comparison of techniques for distributing public keys : : : : : : : 563
13.5 Techniques for controlling key usage : : : : : : : : : : : : : : : : : : : 567
13.5.1 Key separation and constraints on key usage : : : : : : : : : : : : 567
13.5.2 Techniques for controlling use of symmetric keys : : : : : : : : : 568
13.6 Key management involving multiple domains : : : : : : : : : : : : : : : 570
13.6.1 Trust between two domains : : : : : : : : : : : : : : : : : : : : 570
13.6.2 Trust models involving multiple certification authorities : : : : : : 572
13.6.3 Certificate distribution and revocation : : : : : : : : : : : : : : : 576
13.7 Key life cycle issues : : : : : : : : : : : : : : : : : : : : : : : : : : : : 577
13.7.1 Lifetime protection requirements : : : : : : : : : : : : : : : : : : 578
13.7.2 Key management life cycle : : : : : : : : : : : : : : : : : : : : 578
13.8 Advanced trusted third party services : : : : : : : : : : : : : : : : : : : 581
13.8.1 Trusted timestamping service : : : : : : : : : : : : : : : : : : : 581
13.8.2 Non-repudiation and notarization of digital signatures : : : : : : : 582
13.8.3 Key escrow : : : : : : : : : : : : : : : : : : : : : : : : : : : : 584
13.9 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 586
14 Efficient Implementation
591
14.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 591
14.2 Multiple-precision integer arithmetic : : : : : : : : : : : : : : : : : : : 592
14.2.1 Radix representation : : : : : : : : : : : : : : : : : : : : : : : : 592
14.2.2 Addition and subtraction : : : : : : : : : : : : : : : : : : : : : : 594
14.2.3 Multiplication : : : : : : : : : : : : : : : : : : : : : : : : : : : 595
14.2.4 Squaring : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 596
14.2.5 Division : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 598
14.3 Multiple-precision modular arithmetic : : : : : : : : : : : : : : : : : : : 599
14.3.1 Classical modular multiplication : : : : : : : : : : : : : : : : : : 600
14.3.2 Montgomery reduction : : : : : : : : : : : : : : : : : : : : : : : 600
14.3.3 Barrett reduction : : : : : : : : : : : : : : : : : : : : : : : : : : 603
14.3.4 Reduction methods for moduli of special form : : : : : : : : : : : 605
14.4 Greatest common divisor algorithms : : : : : : : : : : : : : : : : : : : 606

Table of Contents

14.5

14.6

14.7

14.8

xiii

14.4.1 Binary gcd algorithm : : : : : : : : : : : : : : : : : : : : : : : : 606
14.4.2 Lehmer’s gcd algorithm : : : : : : : : : : : : : : : : : : : : : : 607
14.4.3 Binary extended gcd algorithm : : : : : : : : : : : : : : : : : : : 608
Chinese remainder theorem for integers : : : : : : : : : : : : : : : : : : 610
14.5.1 Residue number systems : : : : : : : : : : : : : : : : : : : : : : 611
14.5.2 Garner’s algorithm : : : : : : : : : : : : : : : : : : : : : : : : : 612
Exponentiation : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 613
14.6.1 Techniques for general exponentiation : : : : : : : : : : : : : : : 614
14.6.2 Fixed-exponent exponentiation algorithms : : : : : : : : : : : : : 620
14.6.3 Fixed-base exponentiation algorithms : : : : : : : : : : : : : : : 623
Exponent recoding : : : : : : : : : : : : : : : : : : : : : : : : : : : : 627
14.7.1 Signed-digit representation : : : : : : : : : : : : : : : : : : : : : 627
14.7.2 String-replacement representation : : : : : : : : : : : : : : : : : 628
Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 630

15 Patents and Standards
635
15.1 Introduction : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : : 635
15.2 Patents on cryptographic techniques : : : : : : : : : : : : : : : : : : : : 635
15.2.1 Five fundamental patents : : : : : : : : : : : : : : : : : : : : : : 636
15.2.2 Ten prominent patents : : : : : : : : : : : : : : : : : : : : : : : 638
15.2.3 Ten selected patents : : : : : : : : : : : : : : : : : : : : : : : : 641
15.2.4 Ordering and acquiring patents : : : : : : : : : : : : : : : : : : : 645
15.3 Cryptographic standards : : : : : : : : : : : : : : : : : : : : : : : : : : 645
15.3.1 International standards – cryptographic techniques : : : : : : : : : 645
15.3.2 Banking security standards (ANSI, ISO) : : : : : : : : : : : : : : 648
15.3.3 International security architectures and frameworks : : : : : : : : 653
15.3.4 U.S. government standards (FIPS) : : : : : : : : : : : : : : : : : 654
15.3.5 Internet standards and RFCs : : : : : : : : : : : : : : : : : : : : 655
15.3.6 De facto standards : : : : : : : : : : : : : : : : : : : : : : : : : 656
15.3.7 Ordering and acquiring standards : : : : : : : : : : : : : : : : : 656
15.4 Notes and further references : : : : : : : : : : : : : : : : : : : : : : : : 657
A Bibliography of Papers from Selected Cryptographic Forums
663
A.1 Asiacrypt/Auscrypt Proceedings : : : : : : : : : : : : : : : : : : : : : : 663
A.2 Crypto Proceedings : : : : : : : : : : : : : : : : : : : : : : : : : : : : 667
A.3 Eurocrypt Proceedings : : : : : : : : : : : : : : : : : : : : : : : : : : 684
A.4 Fast Software Encryption Proceedings : : : : : : : : : : : : : : : : : : 698
A.5 Journal of Cryptology papers : : : : : : : : : : : : : : : : : : : : : : : 700
References
Index

703
755

Chapter

1

Overview of Cryptography

Contents in Brief
1.1
1.2
1.3
1.4
1.5
1.6
1.7
1.8
1.9
1.10
1.11
1.12
1.13
1.14

Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
Information security and cryptography . . . . . . . . . . . . . .
Background on functions . . . . . . . . . . . . . . . . . . . . . .
Basic terminology and concepts . . . . . . . . . . . . . . . . . . .
Symmetric-key encryption . . . . . . . . . . . . . . . . . . . . .
Digital signatures . . . . . . . . . . . . . . . . . . . . . . . . . .
Authentication and identification . . . . . . . . . . . . . . . . . .
Public-key cryptography . . . . . . . . . . . . . . . . . . . . . .
Hash functions . . . . . . . . . . . . . . . . . . . . . . . . . . .
Protocols and mechanisms . . . . . . . . . . . . . . . . . . . . .
Key establishment, management, and certification . . . . . . . . .
Pseudorandom numbers and sequences . . . . . . . . . . . . . .
Classes of attacks and security models . . . . . . . . . . . . . . .
Notes and further references . . . . . . . . . . . . . . . . . . . .

1
2
6
11
15
22
24
25
33
33
35
39
41
45

1.1 Introduction
Cryptography has a long and fascinating history. The most complete non-technical account
of the subject is Kahn’s The Codebreakers. This book traces cryptography from its initial
and limited use by the Egyptians some 4000 years ago, to the twentieth century where it
played a crucial role in the outcome of both world wars. Completed in 1963, Kahn’s book
covers those aspects of the history which were most significant (up to that time) to the development of the subject. The predominant practitioners of the art were those associated with
the military, the diplomatic service and government in general. Cryptography was used as
a tool to protect national secrets and strategies.
The proliferation of computers and communications systems in the 1960s brought with
it a demand from the private sector for means to protect information in digital form and to
provide security services. Beginning with the work of Feistel at IBM in the early 1970s and
culminating in 1977 with the adoption as a U.S. Federal Information Processing Standard
for encrypting unclassified information, DES, the Data Encryption Standard, is the most
well-known cryptographic mechanism in history. It remains the standard means for securing electronic commerce for many financial institutions around the world.
The most striking development in the history of cryptography came in 1976 when Diffie
and Hellman published New Directions in Cryptography. This paper introduced the revolutionary concept of public-key cryptography and also provided a new and ingenious method
1

2

Ch. 1 Overview of Cryptography

for key exchange, the security of which is based on the intractability of the discrete logarithm problem. Although the authors had no practical realization of a public-key encryption scheme at the time, the idea was clear and it generated extensive interest and activity
in the cryptographic community. In 1978 Rivest, Shamir, and Adleman discovered the first
practical public-key encryption and signature scheme, now referred to as RSA. The RSA
scheme is based on another hard mathematical problem, the intractability of factoring large
integers. This application of a hard mathematical problem to cryptography revitalized efforts to find more efficient methods to factor. The 1980s saw major advances in this area
but none which rendered the RSA system insecure. Another class of powerful and practical
public-key schemes was found by ElGamal in 1985. These are also based on the discrete
logarithm problem.
One of the most significant contributions provided by public-key cryptography is the
digital signature. In 1991 the first international standard for digital signatures (ISO/IEC
9796) was adopted. It is based on the RSA public-key scheme. In 1994 the U.S. Government adopted the Digital Signature Standard, a mechanism based on the ElGamal publickey scheme.
The search for new public-key schemes, improvements to existing cryptographic mechanisms, and proofs of security continues at a rapid pace. Various standards and infrastructures involving cryptography are being put in place. Security products are being developed
to address the security needs of an information intensive society.
The purpose of this book is to give an up-to-date treatise of the principles, techniques,
and algorithms of interest in cryptographic practice. Emphasis has been placed on those
aspects which are most practical and applied. The reader will be made aware of the basic
issues and pointed to specific related research in the literature where more indepth discussions can be found. Due to the volume of material which is covered, most results will be
stated without proofs. This also serves the purpose of not obscuring the very applied nature
of the subject. This book is intended for both implementers and researchers. It describes
algorithms, systems, and their interactions.
Chapter 1 is a tutorial on the many and various aspects of cryptography. It does not
attempt to convey all of the details and subtleties inherent to the subject. Its purpose is to
introduce the basic issues and principles and to point the reader to appropriate chapters in the
book for more comprehensive treatments. Specific techniques are avoided in this chapter.

1.2 Information security and cryptography
The concept of information will be taken to be an understood quantity. To introduce cryptography, an understanding of issues related to information security in general is necessary.
Information security manifests itself in many ways according to the situation and requirement. Regardless of who is involved, to one degree or another, all parties to a transaction
must have confidence that certain objectives associated with information security have been
met. Some of these objectives are listed in Table 1.1.
Over the centuries, an elaborate set of protocols and mechanisms has been created to
deal with information security issues when the information is conveyed by physical documents. Often the objectives of information security cannot solely be achieved through
mathematical algorithms and protocols alone, but require procedural techniques and abidance of laws to achieve the desired result. For example, privacy of letters is provided by
sealed envelopes delivered by an accepted mail service. The physical security of the envelope is, for practical necessity, limited and so laws are enacted which make it a criminal

§1.2 Information security and cryptography

privacy
or confidentiality
data integrity
entity authentication
or identification
message
authentication
signature
authorization
validation
access control
certification
timestamping
witnessing
receipt
confirmation
ownership
anonymity
non-repudiation
revocation

3

keeping information secret from all but those who are authorized to see it.
ensuring information has not been altered by unauthorized or
unknown means.
corroboration of the identity of an entity (e.g., a person, a
computer terminal, a credit card, etc.).
corroborating the source of information; also known as data
origin authentication.
a means to bind information to an entity.
conveyance, to another entity, of official sanction to do or be
something.
a means to provide timeliness of authorization to use or manipulate information or resources.
restricting access to resources to privileged entities.
endorsement of information by a trusted entity.
recording the time of creation or existence of information.
verifying the creation or existence of information by an entity
other than the creator.
acknowledgement that information has been received.
acknowledgement that services have been provided.
a means to provide an entity with the legal right to use or
transfer a resource to others.
concealing the identity of an entity involved in some process.
preventing the denial of previous commitments or actions.
retraction of certification or authorization.

Table 1.1: Some information security objectives.

offense to open mail for which one is not authorized. It is sometimes the case that security
is achieved not through the information itself but through the physical document recording
it. For example, paper currency requires special inks and material to prevent counterfeiting.
Conceptually, the way information is recorded has not changed dramatically over time.
Whereas information was typically stored and transmitted on paper, much of it now resides on magnetic media and is transmitted via telecommunications systems, some wireless. What has changed dramatically is the ability to copy and alter information. One can
make thousands of identical copies of a piece of information stored electronically and each
is indistinguishable from the original. With information on paper, this is much more difficult. What is needed then for a society where information is mostly stored and transmitted
in electronic form is a means to ensure information security which is independent of the
physical medium recording or conveying it and such that the objectives of information security rely solely on digital information itself.
One of the fundamental tools used in information security is the signature. It is a building block for many other services such as non-repudiation, data origin authentication, identification, and witnessing, to mention a few. Having learned the basics in writing, an individual is taught how to produce a handwritten signature for the purpose of identification.
At contract age the signature evolves to take on a very integral part of the person’s identity.
This signature is intended to be unique to the individual and serve as a means to identify,
authorize, and validate. With electronic information the concept of a signature needs to be

4

Ch. 1 Overview of Cryptography

redressed; it cannot simply be something unique to the signer and independent of the information signed. Electronic replication of it is so simple that appending a signature to a
document not signed by the originator of the signature is almost a triviality.
Analogues of the “paper protocols” currently in use are required. Hopefully these new
electronic based protocols are at least as good as those they replace. There is a unique opportunity for society to introduce new and more efficient ways of ensuring information security. Much can be learned from the evolution of the paper based system, mimicking those
aspects which have served us well and removing the inefficiencies.
Achieving information security in an electronic society requires a vast array of technical and legal skills. There is, however, no guarantee that all of the information security objectives deemed necessary can be adequately met. The technical means is provided through
cryptography.
1.1 Definition Cryptography is the study of mathematical techniques related to aspects of information security such as confidentiality, data integrity, entity authentication, and data origin authentication.
Cryptography is not the only means of providing information security, but rather one set of
techniques.
Cryptographic goals
Of all the information security objectives listed in Table 1.1, the following four form a
framework upon which the others will be derived: (1) privacy or confidentiality (§1.5, §1.8);
(2) data integrity (§1.9); (3) authentication (§1.7); and (4) non-repudiation (§1.6).
1. Confidentiality is a service used to keep the content of information from all but those
authorized to have it. Secrecy is a term synonymous with confidentiality and privacy.
There are numerous approaches to providing confidentiality, ranging from physical
protection to mathematical algorithms which render data unintelligible.
2. Data integrity is a service which addresses the unauthorized alteration of data. To
assure data integrity, one must have the ability to detect data manipulation by unauthorized parties. Data manipulation includes such things as insertion, deletion, and
substitution.
3. Authentication is a service related to identification. This function applies to both entities and information itself. Two parties entering into a communication should identify
each other. Information delivered over a channel should be authenticated as to origin,
date of origin, data content, time sent, etc. For these reasons this aspect of cryptography is usually subdivided into two major classes: entity authentication and data
origin authentication. Data origin authentication implicitly provides data integrity
(for if a message is modified, the source has changed).
4. Non-repudiation is a service which prevents an entity from denying previous commitments or actions. When disputes arise due to an entity denying that certain actions
were taken, a means to resolve the situation is necessary. For example, one entity
may authorize the purchase of property by another entity and later deny such authorization was granted. A procedure involving a trusted third party is needed to resolve
the dispute.
A fundamental goal of cryptography is to adequately address these four areas in both
theory and practice. Cryptography is about the prevention and detection of cheating and
other malicious activities.
This book describes a number of basic cryptographic tools (primitives) used to provide
information security. Examples of primitives include encryption schemes (§1.5 and §1.8),

§1.2 Information security and cryptography

5

hash functions (§1.9), and digital signature schemes (§1.6). Figure 1.1 provides a schematic
listing of the primitives considered and how they relate. Many of these will be briefly introduced in this chapter, with detailed discussion left to later chapters. These primitives should
Arbitrary length
hash functions
Unkeyed
Primitives

One-way permutations

Random sequences
Block
ciphers
Symmetric-key
ciphers
Arbitrary length
hash functions (MACs)
Security
Primitives

Stream
ciphers

Symmetric-key
Primitives
Signatures

Pseudorandom
sequences
Identification primitives

Public-key
ciphers

Public-key
Primitives

Signatures

Identification primitives

Figure 1.1: A taxonomy of cryptographic primitives.

be evaluated with respect to various criteria such as:
1. level of security. This is usually difficult to quantify. Often it is given in terms of the
number of operations required (using the best methods currently known) to defeat the
intended objective. Typically the level of security is defined by an upper bound on
the amount of work necessary to defeat the objective. This is sometimes called the
work factor (see §1.13.4).
2. functionality. Primitives will need to be combined to meet various information security objectives. Which primitives are most effective for a given objective will be
determined by the basic properties of the primitives.
3. methods of operation. Primitives, when applied in various ways and with various inputs, will typically exhibit different characteristics; thus, one primitive could provide

6

Ch. 1 Overview of Cryptography

very different functionality depending on its mode of operation or usage.
4. performance. This refers to the efficiency of a primitive in a particular mode of operation. (For example, an encryption algorithm may be rated by the number of bits
per second which it can encrypt.)
5. ease of implementation. This refers to the difficulty of realizing the primitive in a
practical instantiation. This might include the complexity of implementing the primitive in either a software or hardware environment.
The relative importance of various criteria is very much dependent on the application
and resources available. For example, in an environment where computing power is limited
one may have to trade off a very high level of security for better performance of the system
as a whole.
Cryptography, over the ages, has been an art practised by many who have devised ad
hoc techniques to meet some of the information security requirements. The last twenty
years have been a period of transition as the discipline moved from an art to a science. There
are now several international scientific conferences devoted exclusively to cryptography
and also an international scientific organization, the International Association for Cryptologic Research (IACR), aimed at fostering research in the area.
This book is about cryptography: the theory, the practice, and the standards.

1.3 Background on functions
While this book is not a treatise on abstract mathematics, a familiarity with basic mathematical concepts will prove to be useful. One concept which is absolutely fundamental to
cryptography is that of a function in the mathematical sense. A function is alternately referred to as a mapping or a transformation.

1.3.1 Functions (1-1, one-way, trapdoor one-way)
A set consists of distinct objects which are called elements of the set. For example, a set X
might consist of the elements a, b, c, and this is denoted X = {a, b, c}.
1.2 Definition A function is defined by two sets X and Y and a rule f which assigns to each
element in X precisely one element in Y . The set X is called the domain of the function
and Y the codomain. If x is an element of X (usually written x ∈ X) the image of x is the
element in Y which the rule f associates with x; the image y of x is denoted by y = f (x).
Standard notation for a function f from set X to set Y is f : X −→ Y . If y ∈ Y , then a
preimage of y is an element x ∈ X for which f (x) = y. The set of all elements in Y which
have at least one preimage is called the image of f , denoted Im(f ).
1.3 Example (function) Consider the sets X = {a, b, c}, Y = {1, 2, 3, 4}, and the rule f
from X to Y defined as f (a) = 2, f (b) = 4, f (c) = 1. Figure 1.2 shows a schematic of
the sets X, Y and the function f . The preimage of the element 2 is a. The image of f is
{1, 2, 4}.

Thinking of a function in terms of the schematic (sometimes called a functional diagram) given in Figure 1.2, each element in the domain X has precisely one arrowed line
originating from it. Each element in the codomain Y can have any number of arrowed lines
incident to it (including zero lines).

§1.3 Background on functions

7

f

1

a
2

X

Y

b
3
c
4

Figure 1.2: A function f from a set X of three elements to a set Y of four elements.

Often only the domain X and the rule f are given and the codomain is assumed to be
the image of f . This point is illustrated with two examples.
1.4 Example (function) Take X = {1, 2, 3, . . . , 10} and let f be the rule that for each x ∈ X,
f (x) = rx , where rx is the remainder when x2 is divided by 11. Explicitly then
f (1) = 1 f (2) = 4 f (3) = 9 f (4) = 5 f (5) = 3
f (6) = 3 f (7) = 5 f (8) = 9 f (9) = 4 f (10) = 1.
The image of f is the set Y = {1, 3, 4, 5, 9}.



1.5 Example (function) Take X = {1, 2, 3, . . . , 1050 } and let f be the rule f (x) = rx , where
rx is the remainder when x2 is divided by 1050 + 1 for all x ∈ X. Here it is not feasible
to write down f explicitly as in Example 1.4, but nonetheless the function is completely
specified by the domain and the mathematical description of the rule f .

(i) 1-1 functions
1.6 Definition A function (or transformation) is 1 − 1 (one-to-one) if each element in the
codomain Y is the image of at most one element in the domain X.
1.7 Definition A function (or transformation) is onto if each element in the codomain Y is
the image of at least one element in the domain. Equivalently, a function f : X −→ Y is
onto if Im(f ) = Y .
1.8 Definition If a function f : X −→ Y is 1−1 and Im(f ) = Y , then f is called a bijection.
1.9 Fact If f : X −→ Y is 1 − 1 then f : X −→ Im(f ) is a bijection. In particular, if
f : X −→ Y is 1 − 1, and X and Y are finite sets of the same size, then f is a bijection.
In terms of the schematic representation, if f is a bijection, then each element in Y
has exactly one arrowed line incident with it. The functions described in Examples 1.3 and
1.4 are not bijections. In Example 1.3 the element 3 is not the image of any element in the
domain. In Example 1.4 each element in the codomain has two preimages.
1.10 Definition If f is a bijection from X to Y then it is a simple matter to define a bijection g
from Y to X as follows: for each y ∈ Y define g(y) = x where x ∈ X and f (x) = y. This
function g obtained from f is called the inverse function of f and is denoted by g = f −1 .

8

Ch. 1 Overview of Cryptography

f

X

g

a

1

1

a

b

2

2

b

c

3

3

c

d

4

4

d

e

5

5

e

Y

Y

X

Figure 1.3: A bijection f and its inverse g = f −1 .

1.11 Example (inverse function) Let X = {a, b, c, d, e}, and Y = {1, 2, 3, 4, 5}, and consider
the rule f given by the arrowed edges in Figure 1.3. f is a bijection and its inverse g is
formed simply by reversing the arrows on the edges. The domain of g is Y and the codomain
is X.

Note that if f is a bijection, then so is f −1 . In cryptography bijections are used as
the tool for encrypting messages and the inverse transformations are used to decrypt. This
will be made clearer in §1.4 when some basic terminology is introduced. Notice that if the
transformations were not bijections then it would not be possible to always decrypt to a
unique message.
(ii) One-way functions
There are certain types of functions which play significant roles in cryptography. At the
expense of rigor, an intuitive definition of a one-way function is given.
1.12 Definition A function f from a set X to a set Y is called a one-way function if f (x) is
“easy” to compute for all x ∈ X but for “essentially all” elements y ∈ Im(f ) it is “computationally infeasible” to find any x ∈ X such that f (x) = y.
1.13 Note (clarification of terms in Definition 1.12)
(i) A rigorous definition of the terms “easy” and “computationally infeasible” is necessary but would detract from the simple idea that is being conveyed. For the purpose
of this chapter, the intuitive meaning will suffice.
(ii) The phrase “for essentially all elements in Y ” refers to the fact that there are a few
values y ∈ Y for which it is easy to find an x ∈ X such that y = f (x). For example,
one may compute y = f (x) for a small number of x values and then for these, the
inverse is known by table look-up. An alternate way to describe this property of a
one-way function is the following: for a random y ∈ Im(f ) it is computationally
infeasible to find any x ∈ X such that f (x) = y.
The concept of a one-way function is illustrated through the following examples.
1.14 Example (one-way function) Take X = {1, 2, 3, . . . , 16} and define f (x) = rx for all
x ∈ X where rx is the remainder when 3x is divided by 17. Explicitly,
x
f (x)

1 2 3 4 5 6 7 8 9 10 11
3 9 10 13 5 15 11 16 14 8 7

12 13 14 15 16
4 12 2 6 1

Given a number between 1 and 16, it is relatively easy to find the image of it under f . However, given a number such as 7, without having the table in front of you, it is harder to find

§1.3 Background on functions

9

x given that f (x) = 7. Of course, if the number you are given is 3 then it is clear that x = 1
is what you need; but for most of the elements in the codomain it is not that easy.

One must keep in mind that this is an example which uses very small numbers; the
important point here is that there is a difference in the amount of work to compute f (x)
and the amount of work to find x given f (x). Even for very large numbers, f (x) can be
computed efficiently using the repeated square-and-multiply algorithm (Algorithm 2.143),
whereas the process of finding x from f (x) is much harder.
1.15 Example (one-way function) A prime number is a positive integer greater than 1 whose
only positive integer divisors are 1 and itself. Select primes p = 48611, q = 53993, form
n = pq = 2624653723, and let X = {1, 2, 3, . . . , n − 1}. Define a function f on X
by f (x) = rx for each x ∈ X, where rx is the remainder when x3 is divided by n. For
instance, f (2489991) = 1981394214 since 24899913 = 5881949859 · n + 1981394214.
Computing f (x) is a relatively simple thing to do, but to reverse the procedure is much more
difficult; that is, given a remainder to find the value x which was originally cubed (raised
to the third power). This procedure is referred to as the computation of a modular cube root
with modulus n. If the factors of n are unknown and large, this is a difficult problem; however, if the factors p and q of n are known then there is an efficient algorithm for computing
modular cube roots. (See §8.2.2(i) for details.)

Example 1.15 leads one to consider another type of function which will prove to be
fundamental in later developments.
(iii) Trapdoor one-way functions
1.16 Definition A trapdoor one-way function is a one-way function f : X −→ Y with the
additional property that given some extra information (called the trapdoor information) it
becomes feasible to find for any given y ∈ Im(f ), an x ∈ X such that f (x) = y.
Example 1.15 illustrates the concept of a trapdoor one-way function. With the additional information of the factors of n = 2624653723 (namely, p = 48611 and q = 53993,
each of which is five decimal digits long) it becomes much easier to invert the function.
The factors of 2624653723 are large enough that finding them by hand computation would
be difficult. Of course, any reasonable computer program could find the factors relatively
quickly. If, on the other hand, one selects p and q to be very large distinct prime numbers
(each having about 100 decimal digits) then, by today’s standards, it is a difficult problem,
even with the most powerful computers, to deduce p and q simply from n. This is the wellknown integer factorization problem (see §3.2) and a source of many trapdoor one-way
functions.
It remains to be rigorously established whether there actually are any (true) one-way
functions. That is to say, no one has yet definitively proved the existence of such functions under reasonable (and rigorous) definitions of “easy” and “computationally infeasible”. Since the existence of one-way functions is still unknown, the existence of trapdoor
one-way functions is also unknown. However, there are a number of good candidates for
one-way and trapdoor one-way functions. Many of these are discussed in this book, with
emphasis given to those which are practical.
One-way and trapdoor one-way functions are the basis for public-key cryptography
(discussed in §1.8). The importance of these concepts will become clearer when their application to cryptographic techniques is considered. It will be worthwhile to keep the abstract
concepts of this section in mind as concrete methods are presented.

10

Ch. 1 Overview of Cryptography

1.3.2 Permutations
Permutations are functions which are often used in various cryptographic constructs.
1.17 Definition Let S be a finite set of elements. A permutation p on S is a bijection (Definition 1.8) from S to itself (i.e., p : S −→ S).
1.18 Example (permutation) Let S = {1, 2, 3, 4, 5}. A permutation p : S −→ S is defined as
follows:
p(1) = 3, p(2) = 5, p(3) = 4, p(4) = 2, p(5) = 1.
A permutation can be described in various ways. It can be displayed as above or as an array:


1 2 3 4 5
p=
,
(1.1)
3 5 4 2 1
where the top row in the array is the domain and the bottom row is the image under the
mapping p. Of course, other representations are possible.

Since permutations are bijections, they have inverses. If a permutation is written as an
array (see 1.1), its inverse is easily found by interchanging the rows in the array and reordering the elements in the new top row if desired (the bottom row
would have to be reordered

1 2 3 4 5
−1
correspondingly). The inverse of p in Example 1.18 is p =
.
5 4 1 3 2
1.19 Example (permutation) Let X be the set of integers {0, 1, 2, . . . , pq − 1} where p and q
are distinct large primes (for example, p and q are each about 100 decimal digits long), and
suppose that neither p−1 nor q −1 is divisible by 3. Then the function p(x

[...正文过长，此处由批处理脚本仅做上下文截断；请在结论中说明该限制...]

ction, 202
algebraic normal form of, 205
correlation immune, 207
nonlinear order of, 205
BPP, 63
Break-backward protection, 496
Brickell-McCurley identification protocol, 423
Broadcast encryption, 528
Bucket hashing, 382
Burmester-Desmedt conference keying, 528
Burst error, 363

C
CA, see Certification authority (CA)
CA-certificate, 572
Caesar cipher, 239
CALEA, 590
Capability (access control), 570
Capstone chip, 589
Cardinality of a set, 49
Carmichael number, 137
Carry-save adder, 630
Cartesian product, 49
Cascade cipher, 234, 237
Cascade generator
m-sequence, 221
p-cycle, 220
Cascading hash functions, 334
CAST block cipher, 281
patent, 659
CBC, see Cipher-block chaining mode

Index

CBC-MAC, 353–354, 367
ANSI X9.9 standard, 650
ANSI X9.19 standard, 650
FIPS 113 standard, 654
ISO 8731-1 standard, 652
ISO 9807 standard, 652
ISO/IEC 9797 standard, 646
Cellular automata stream cipher, 222
Certificate
ANSI X9.45 standard, 651
ANSI X9.55 standard, 651
ANSI X9.57 standard, 651
caching, 576
chain, 572
directory, 549
pull model, 576
push model, 576
forward, 575
on-line, 576
public-key, see Public-key certificate
reverse, 575
revocation, 566, 576–577
RFC 1422, 655
secret-key, see Secret-key certificate
symmetric-key, see Symmetric-key certificate
X.509 standard, 660
Certificate of primality, 166
Certificate revocation list (CRL), 576–577
Certification, 3
path, 572
policy, 576
topology, 572
Certification authority (CA), 491, 548, 556, 559
Certificational attack, 236
Certificational weakness, 285
CFB, see Cipher feedback mode
CFB-64 MAC, 650
Challenge, 397, 409
Challenge-response identification, 397–405, 420–
421
public-key, 403–405
ISO/IEC 9798-3, 404–405
modified Needham-Schroeder, 404
X.509, 404
symmetric-key, 400–403
ISO/IEC 9798-2, 401–402
SKID2, 402
SKID3, 402
Channel, 13
physically secure, 13
secure, 13
secured, 13
unsecured, 13
Characteristic of a field, 77

Index

Chaum’s blind signature protocol, 475
Chaum-van Antwerpen undeniable signature scheme, 476–478
disavowal protocol, 477
key generation, 476
security of, 478
signature generation, 476
Chebyshev’s inequality, 52
Checksum, 362, 367–368
Chi-square (χ2 ) distribution, 177–179
degrees of freedom, 177
mean of, 177
variance of, 177
Chinese remainder theorem (CRT), 68
Garner’s algorithm, 612–613
Gauss’s algorithm, 68
Chipcard, 387, 424
Chor-Rivest public-key encryption, 302–306, 318
attacks on, 318
decryption algorithm, 303
encryption algorithm, 303
key generation, 303
recommended parameter sizes, 305
security of, 305
Chosen-ciphertext attack, 41, 226, 285
adaptive, 285
indifferent, 285
Chosen-message attack, 433
directed, 482
generic, 482
Chosen-plaintext attack, 41, 226
Cipher, 12
see also Encryption
Cipher-block chaining mode (CBC), 230
integrity of IV in, 230
use in public-key encryption, 285
Cipher feedback mode (CFB), 231
as a stream cipher, 233
ISO variant of, 231
Cipher machine, 242–245
Jefferson cylinder, 243
rotor-based machine, 243–245, 276
Enigma, 245
Hagelin M-209, 245
Hebern, 244
Wheatstone disc, 274
Ciphertext, 11
Ciphertext-only attack, 41, 225
Ciphertext space, 11
Claimant, 385, 386
Classical cipher, 237–250, 273–276
cipher machines, see Cipher machine
cryptanalysis, 245–250, 275–276
index of coincidence, 248

759

Kasiski’s method, 248
measure of roughness, 249
polyalphabetic substitution cipher, see Polyalphabetic substitution cipher
substitution cipher, see Substitution cipher
transposition cipher, see Transposition cipher
Classical modular multiplication, 600
Classical occupancy problem, 53
Claw-resistant (claw-free), 376, 468
Clipper chip, 584, 589
key escrow, 584
law enforcement access field (LEAF), 584
Clipper key escrow, 654
Clock-controlled generator, 209–212
co-NP, 60
Codebook, 240
Codomain of a function, 6, 50
Collision, 321
pseudo-collision, 371
Collision resistance, 324, 325
Collision resistant hash function (CRHF), 325
Combining function, 205
Common modulus attack on RSA, 289
Commutative ring, 77
Complementation property of DES, 256–257
Complete function, 277
Complexity classes, 59–62
BPP, 63
co-NP, 60
NP, 60
NP-complete, 61
NP-hard, 62
NPC, 61
P, 60
RP, 63
ZPP, 63
Complexity measure
2-adic span, 218
linear complexity, 198–201
maximum order complexity, 217
Turing-Kolmogorov-Chaitin complexity, 217
Ziv-Lempel complexity, 217
Complexity of attacks on a block cipher, 225–227
active complexity, 226
attack complexity, 226
data complexity, 226
passive complexity, 226
processing complexity, 226
storage complexity, 226
Complexity theory, 57–63
Complexity-theoretic security, 43
Compliant, 532
Composite integer, 64
Composition of functions, 19

760

Computation-resistance (MAC), 325
Computational problems
computationally equivalent, 88
polytime reduction, 88
Computational security, 43, 226
Computational zero-knowledge protocol, 407
Computationally equivalent decision problems, 61
COMSET, 421, 536
Conditional entropy, 56
Conditional probability, 51
Conditional transinformation, 57
Conference keying, 528–529, 540
Blundo’s conference KDS bound, 529
Burmester-Desmedt, 528
definition of, 528
Confidentiality, 3, 4, 12
Confirmation, 3
Confounder, 418
Confusion, 20
Congruences
integers, 67
polynomials, 79
Conjugate gradient method, 129
Connection polynomial of an LFSR, 196, 204
known versus secret, 204
sparse versus dense, 205
Constrained linear equations problem, 423
Continued fraction factoring algorithm, 126
Continuous random variable, 176
Control vector, 569
patent, 639, 658
Conventional encryption, 15
Coprime, 64
Correcting-block chaining attack, 373
Correlated, 172
Correlation attack, 206, 218
Correlation immunity, 207, 218
Counter mode, 233
CRC-based MAC, 359
Credential, 501
CRHF, see Collision resistant hash function
Cross-certificate (CA-certificate), 572
Cross-certificate pair, 573
CRT, see Chinese remainder theorem
Cryptanalysis, 15
Cryptanalyst, 15
Cryptographic check value, 363
Cryptographic primitives, 4
taxonomy of, 5
Cryptographically secure pseudorandom bit generator (CSPRBG), 185–187
Blum-Blum-Shub generator, 186–187
Blum-Micali generator, 189
definition of, 171

Index

Micali-Schnorr generator, 186
modified-Rabin generator, 190
RSA generator, 185–186
Cryptography
definition of, 4
goals of, 4
CRYPTOKI, 656
Cryptology, 15
Cryptoperiod of a key, 553
Cryptosystem, 15
Cut-and-choose protocol, 410, 421
Cycle of a periodic sequence, 180
Cyclic group, 69, 76
generator of, 76
Cyclic redundancy code (CRC), 363
Cyclic register, 220
Cycling attacks on RSA, 289, 313

D
Data Authentication Algorithm (DAA), 654
Data Encryption Standard, see DES block cipher
Data integrity, 3, 4, 33, 359–368, 383
Data key, 552
Data origin authentication, 3, 4, 25, 359–368, 491
Davies-Meyer hash function, 341
de Bruijn FSR, 203
de Bruijn sequence, 203
De-skewing, 172
DEA, 649
Decimated subsequence, 211
Decision problems, 60
computationally equivalent, 61
polytime reduction, 61
Decryption, 11
Decryption exponent for RSA, 286
Decryption function, 11
DECT, 586
Degrees of freedom, 177
Delay element
of an FSR, 202
of an LFSR, 195
Delayed-carry adder, 630
Density of a knapsack set, 120
Derivative of a polynomial, 123
DES block cipher, 250–259, 276–278
ANSI X3.92 standard, 649
attacks on
differential cryptanalysis, 258–259
exhaustive key search, 233–234, 272
linear cryptanalysis, 258–259
complementation property, 256–257
decryption algorithm, 255
DESX, 273
double DES, see Double DES

Index

encryption algorithm, 253
expansion permutation, 252
FIPS 46 standard, 654
initial permutation (IP), 252, 277
key schedule
decryption, 256
encryption, 255
modes of operation, see Block cipher, modes
of operation
patent, 636
permuted choices (PC1, PC2), 252
properties and strengths, 256–259
round, 252
S-box, 252
semi-weak key, 257
anti-fixed point of, 257
test vectors, 256
triple-DES, 273
weak key, 257
fixed point of, 257
Designated confirmer signature, 487
Deterministic, 306
Deterministic algorithm, 62
Dickson polynomial, 314
Dickson scheme, 314
Dictionary attack, 42
Difference of sets, 49
Differential chaining attack, 375
Differential cryptanalysis
of block ciphers, 258, 271, 278–280
Differential-linear cryptanalysis, 271
Diffie-Hellman key agreement, 515–520, 522–524
ANSI X9.42 standard, 651
composite modulus, 537
patent, 637
Diffie-Hellman problem, 113–114
composite moduli, 114, 131
generalized, 113
Diffie-Lamport one-time signature scheme, 485
Diffusion, 20
Digital envelope, 550
Digital fingerprint, 321
Digital signature, see Signature
Digital Signature Algorithm (DSA), 452–454, 483
ANSI X9.30-1 standard, 651
FIPS 186 standard, 655
key generation, 452
patent, 640, 658
security of, 453
signature generation, 452
signature verification, 453
use and throw coupons, 483
Dimension of a vector space, 80
Dirichlet theorem, 135

761

Disavowal protocol, 477
Discrete Fourier Transform (DFT), 631
Discrete logarithms, 103–113
baby-step giant-step algorithm, 104–106
composite moduli, 114
exhaustive search, 104
for class groups, 130
for elliptic curves, 130
for hyperelliptic curves, 130
function field sieve, 129
generalized problem, 103
heuristic running time, 129
in subgroups of Z∗p , 113
index-calculus algorithms, 109–112
lambda method, 128
number field sieve, 128
Pohlig-Hellman algorithm, 107–109
Pollard’s rho algorithm, 106–107
problem definition, 103
rigorously analyzed algorithms, 129
security of individual bits, 116
Divisible electronic coin, 487
Division
of integers, 63
of polynomials, 79
Division algorithm
for integers, 64
for polynomials, 78
Dixon’s algorithm, 95, 127
DNA computer, 130
Domain of a function, 6, 50
Double DES, 235
Double spending, 487
Double-length MDC, 339
DSA, see Digital Signature Algorithm
Dynamic key establishment, 491
Dynamic secret sharing scheme, 527

E
E-D-E triple encryption, 235, 272
E-E-E triple encryption, 272
Eavesdropper, 13, 495
ECA, see Elliptic curve factoring algorithm
ECB, see Electronic codebook mode
Effective key size, 224
Electronic cash
divisible, 487
untraceable, 487
Electronic codebook mode (ECB), 228–230
ElGamal key agreement, 517
ElGamal public-key encryption, 294–298
generalized
decryption algorithm, 297
encryption algorithm, 297

762

key generation, 297
in Z∗p
decryption algorithm, 295
encryption algorithm, 295
key generation, 294
recommended parameter sizes, 296
security of, 296
ElGamal signature scheme, 454–459, 484
generalized
key generation, 458
signature generation, 458
signature verification, 458
in Z∗p
key generation, 454
security of, 455–456
signature generation, 454
signature verification, 454
signature verification, 618
variants of, 457
Elliptic curve
discrete logarithm problem, 130
ElGamal public-key encryption, 297
in public-key cryptography, 316
patents, 659
RSA analogue, 315
supersingular curve, 130, 316
Elliptic curve factoring algorithm (ECA), 94, 125
implementation reports, 126
Elliptic curve primality proving algorithm, 145
Encrypted key exchange (EKE), 538
Encryption, 11
see also Block cipher
see also Public-key encryption
see also Stream cipher
Encryption exponent for RSA, 286
Encryption function, 11
Encryption scheme, 12
breakable, 14
Enemy, 13, 495
Enigma, 245, 276
Entity, 13
Entity authentication, 3, 386, 491
ANSI X9.26 standard, 651
FIPS 196 standard, 655
ISO 11131 standard, 652
ISO/IEC 9798 standard, 401–402, 404–405, 421,
647
see also Identification
Entropy, 56–57, 246
Ephemeral secret, 494
Equivalence class, 68, 79
Equivocation, 56
Error-correcting code, 298, 363, 506
Escrowed Encryption Standard (EES)

Index

FIPS 185, 654
ESIGN signature scheme, 473–474, 486
key generation, 473
patent, 638, 658
security of, 474
signature generation, 473
signature verification, 473
Euclidean algorithm
for integers, 66
for polynomials, 81–83
Euler liar, 138
Euler phi function (φ), 65
Euler pseudoprime, 138
Euler witness, 137
Euler’s criterion, 137
Euler’s theorem, 69
Exclusive-or (XOR), 20
Exhaustive key search, 14, 233–234, 272
Existential forgery, 30, 326, 432
exp (exponential function), 50
Expected running time, 63
Explicit authentication, 492
Exponent array, 617
Exponent recoding, see Exponentiation
Exponential-time algorithm, 59
Exponentiation, 613–629, 633–634
addition chains, 621
exponent recoding, 627–629
signed-digit representation, 627–628
string-replacement representation, 628–
629
fixed-base comb method, 625–627
fixed-base Euclidean method, 624–625
fixed-base windowing method, 623–624
left-to-right binary method, 615
left-to-right k-ary method, 615
modified left-to-right k-ary method, 616
Montgomery method, 619–620
repeated square-and-multiply algorithm, 71,
84
right-to-left binary method, 614
simultaneous multiple, 617–618
sliding-window method, 616
vector-addition chains, 622–623
Extendable secret sharing scheme, 526
Extended Euclidean algorithm
for integers, 67
for polynomials, 82
Extended Riemann Hypothesis (ERH), 165
Extension field, 77
Extractor, 406

F
Factor base, 94, 109

Index

Factoring integers, see Integer factorization
Factoring polynomials, see Polynomial factorization
Fail-stop signature scheme, 478–481, 488
Heijst-Pedersen, 478–481
Fair blind signature scheme, 487
Fair cryptosystems, 640–641, 658
for Diffie-Hellman key agreement, 641
patent, 640
FEAL block cipher, 259–262, 278–279
attacks on, 278–279
FEAL decryption algorithm, 261
FEAL-8 encryption algorithm, 261
FEAL-8 key schedule, 261
FEAL-N, 262
FEAL-NX, 262
patent, 639
test vectors, 262
Feedback shift register (FSR), 195–203
de Bruijn, 203
definition of, 202
delay element of, 202
feedback bit of, 202
feedback function of, 202
Feedback with carry shift register (FCSR), 217–
218, 222
initial state of, 202
linear feedback shift register, see Linear feedback shift register (LFSR)
non-singular, 203
nonlinear feedback shift register, 202
output sequence of, 202
stage of, 202
Feedback with carry shift register (FCSR), 217–218,
222
Feige-Fiat-Shamir identification protocol, 410–412,
422
Feige-Fiat-Shamir signature scheme, 447–449, 483
identity-based modification, 449
key generation, 447
security of, 448
signature generation, 448
signature verification, 448
Feistel cipher, 251, 276
Fermat liar, 136
Fermat number, 143, 166
Fermat witness, 136
Fermat’s primality test, 136
Fermat’s theorem, 69
Fiat-Shamir identification protocol
basic version, 408
patent, 638, 658
Fiat-Shamir signature scheme, 483
patent, 638, 658

763

Field, 77
characteristic of, 77
definition of, 77
extension field of, 77
finite, see Finite field
subfield of, 77
Filtering function, 208
Finite field, 80–85
definition of, 80
order of, 80
polynomial basis, 83
FIPS, 654–655, 661
ordering and acquiring, 656
FIPS 186 pseudorandom bit generator, 174–175
FISH stream cipher, 222
Fixed-point chaining attack, 374
Floyd’s cycle-finding algorithm, 91, 125
Forced delay attack, 417
Formal methods, 534, 541
Forward certificate, 575
Forward error correction, 363
Forward search attack, 34, 42, 288, 420
Fractionation, 276
Frequency distribution
of English digrams, 247
of single English characters, 247
Frequency test, 181
Fresh key, 494
Function, 6–10, 50
bijection, 7
composition of, 19
definition of, 6
injective, 46
inverse, 7
involution, 10
one-to-one, 7
one-way, 8
onto, 7
permutation, 10
surjective, 46
trapdoor one-way, 9
Function field sieve, 129
Functional diagram, 6
Functional graph, 54
component size, 55
cycle length, 55
predecessors size, 55
rho-length, 55
tail length, 55
tree size, 55
Functionally trusted third party, 39

G
Gap of a sequence, 180

764

Garner’s algorithm, 612–613
Gauss’s algorithm, 68
Gaussian integer method, 128
gcd, see Greatest common divisor
Geffe generator, 206
General-purpose factoring algorithm, 90
Generator
of a cyclic group, 76, 160
algorithm for finding, 163
of F∗q , 81
of F∗2m , 163
of Z∗n , 69
of Z∗p , 164
algorithm for selecting, 164
Generator matrix, 506
Girault self-certified public key, 522
GMR one-time signature scheme, 468–471, 486
authentication tree, 470
key generation, 469
security of, 470
signature generation, 469
signature verification, 469
GOAL stream cipher, 219
Goldwasser-Kilian primality test, 166
Goldwasser-Micali probabilistic public-key encryption, 307–308
decryption algorithm, 307
encryption algorithm, 307
key generation, 307
security of, 308
Golomb’s randomness postulates, 180
Goppa code, 299, 317
Gordon’s algorithm for strong prime generation, 150
GOST block cipher, 282
GQ identification protocol, 412–414, 422
patent, 639, 658
GQ signature scheme, 450–451
key generation, 450
message recovery variant, 451
patent, 639, 658
security of, 451
signature generation, 450
signature verification, 450
Grandmaster postal-chess problem, 418
Greatest common divisor
binary extended gcd algorithm, 608–610, 632
binary gcd algorithm, 606–607, 632
Euclidean algorithm, 66
Lehmer’s gcd algorithm, 607–608, 632
of integers, 64
of polynomials, 81
Group, 75–76
cyclic, 76
definition of, 75

Index

of units, 77
order of, 75
subgroup of, 76
Group signature, 488
GSM, 586
GSS-API, 655, 661
Günther’s implicitly-certified public key, 521
Günther’s key agreement, 522

H
Hagelin M-209, 245, 276
Hamming weight, 105
Handwritten signature, 23
Hard predicate, 115
Hash function, 33, 321–383
alternate terminology, 325, 371
applications, 321–322, 330–331
attacks, 368–375
birthday, 369–371
chaining, 373–375
Pseudo-collisions, 371–373
based on block ciphers, 338–343
Abreast Davies-Meyer, 380
Davies-Meyer, 341
Matyas-Meyer-Oseas, 341
MDC-2, 342
MDC-4, 343
Merkle’s DES-based hash, 338, 339, 378
Miyaguchi-Preneel, 341
N-Hash, 380
Tandem Davies-Meyer, 380
based on modular arithmetic, 351–352
MASH-1, 352
MASH-2, 352
cascading, 334
collision resistant (CRHF), 325
customized, 343–351
HAVAL, 379
MD2, 380
MD4, 346
MD5, 347
RIPEMD, 380
RIPEMD-128, 339, 380
RIPEMD-160, 339, 350
Secure Hash Algorithm (SHA-1), 348
Snefru, 380
definition of, 322
ideal security, 336
initialization value (IV), 335
MD-strengthening, see MD-strengthening
Merkle’s meta-method, 333
one-way (OWHF), 325
padding, 334–335
properties of

Index

2nd-preimage resistance, 323
collision resistance, 324
compression, 322
ease of computation, 322
local one-wayness, 331
near-collision resistance, 331
non-correlation, 331
partial-preimage resistance, 331
preimage resistance, 323
strong collision resistance, 324
weak collision resistance, 324
r-collision resistant, 424
strong one-way, 325
universal classes of, 376
universal one-way, 377
weak one-way, 325
Hash-code, 321
Hash-result, 321
Hash-value, 33, 321
HAVAL hash function, 379
Heijst-Pedersen fail-stop signature scheme, 478–481
key generation, 478
proof-of-forgery algorithm, 481
signature generation, 479
signature verification, 479
Hellman-Merkle patent, 637, 658
Heuristic security, 43, 533
High-order digit, 593
Hill cipher, 240, 274
Historical work factor, 44
HMAC, 355
Homomorphic property of RSA, 289
Homophonic substitution cipher, 17, 240
Hybrid protocol, 512
Hyperelliptic curve
discrete logarithm problem, 130
ElGamal public-key encryption, 297
Hypothesis testing, 179–180

I
IC card, 387
IDEA block cipher, 263–265, 279–280
attacks on, 279–280
decryption algorithm, 264
encryption algorithm, 264
key schedule, 264
patent, 640, 658
test vectors, 265
weak keys, 279
Ideal secret sharing scheme, 526, 527
Identification, 3, 24–25, 385–424
applications of, 387
attacks on, 417–420, 424
chosen-text, 417

765

forced delay, 417
impersonation, 417
interleaving, 417
local, 419
non-interactive, 419
off-line, 419
pre-play, 397, 398
reflection, 417
remote, 419
replay, 417
challenge-response, see Challenge-response
identification
mutual, 387
passwords, see Passwords (weak
authentication)
questionnaire-based, 420
relation to signatures, 388
unilateral, 387
zero-knowledge, see Zero-knowledge identification
see also Entity authentication
Identification Friend or Foe (IFF) system, 421
Identity verification, 385
Identity-based key establishment, 493
Identity-based system, 538, 561–562, 587
IDUP, 661
IEEE P1363 standard, 660
IETF, 655
Image of a function, 6, 50
Impersonation, 27, 42, 386, 417
Impersonator, 495
Implicit key authentication, see Key authentication
Implicitly-certified public key, 520–522, 562–563,
588
Diffie-Hellman using, 522–524
identity-based, 563
of Girault, 522
of Günther, 521
self-certified, 563
Imprint, 321
Improved PES (IPES), 279
In-line trusted third party, 547
Incremental hashing, 378
Independent events, 51
Index of coincidence, 248, 275
Index-calculus algorithm, 109–112, 128
Gaussian integer method, 128
in F2m , 111
implementation reports, 128
in Zp , 110
implementation reports, 128
linear sieve, 128
residue list sieve, 128
Information dispersal algorithm (IDA), 539

766

Information rate, 527
Information security, 2
objectives of, 3
Information security service, 14
breaking of, 15
Information theory, 56–57
Initial state
of an FSR, 202
of an LFSR, 196
Injective function, 46, 50
Inner product, 118
Input size, 58
Insider, 496
one-time, 496
permanent, 496
Integer, 49
multiple-precision, 593
negative
signed-magnitude representation, 593
two’s complement representation, 594
single-precision, 593
Integer arithmetic, see Multiple-precision integer
arithmetic
Integer factorization, 89–98
continued fraction algorithm, 126
Dixon’s algorithm, 95, 127
elliptic curve algorithm, 94
general number field sieve, 98
general-purpose algorithms, 90
heuristic running times, 127
multiple polynomial quadratic sieve, 97
Pollard’s p − 1 algorithm, 92–93
Pollard’s rho algorithm, 91–92
problem definition, 89
quadratic sieve algorithm, 95–97
random square methods, 94–98
special number field sieve, 98
special-purpose algorithms, 90
trial division, 90–91
Integers modulo n, 67–71
Integrity check value (ICV), 363
Interactive proof system, 406
Arthur-Merlin games, 421
completeness, 406
soundness, 406
Interleaving attack, 42, 417, 531, 540
Interloper, 13
Internal vertex, 557
Internet security standards, 655–656, 661
Intersection of sets, 49
Intruder, 13, 495
Intruder-in-the-middle attack, 530, 540
Inverse function, 7
Inversion attack on stream ciphers, 219

Index

Involution, 10
Irreducible polynomial, 78, 154–160
algorithm for generating, 156
algorithm for testing, 155
number of, 155
primitive polynomial, see Primitive
polynomial
trinomials, 157
ISO standards, see ISO/IEC standards
ISO/IEC 9796, 442–444, 482–483
ISO/IEC standards, 645–648, 651–653, 660–661
committee draft (CD), 645
draft international standard (DIS), 645
ordering and acquiring, 656
working draft (WD), 645
Isomorphic, 81, 104
Iterated block cipher, 251
ITU, 653

J
Jacobi sum primality test, 144, 166
Jacobi symbol, 73
computing, 73
Jefferson cylinder, 243, 274
Joint entropy, 56
JTC1, 645

K
Karatsuba-Ofman multiplication, 630
Kasiski’s method, 248, 275
KDC, see Key distribution center (KDC)
Kerberos authentication protocol, 401, 501–502,
535–536
RFC 1510, 656
Kerckhoffs’ assumption, 225
Kerckhoffs’ desiderata, 14
Key, 11
archival, 580
backup, 580
cryptoperiod of, 553
data, 552
de-registration, 580
derived, 568
destruction, 580
fresh, 494
generator, 549
installation, 579
key-encrypting, 552
key-transport, 552
layering, 551–553
long-term, 553
master, 551
notarization, 568
offsetting, 568
private, 27, 544

Index

public, 27, 544
public-key vs. symmetric-key, 31–32, 551
recovery, 580
registration, 579
revocation, 566, 580
secret, 544
separation, 567
short-term, 553
symmetric, 544
terminal, 552
update, 580
variant, 568
Key access server, 549
Key agreement, 34, 35, 505–506, 515–524, 536–
538
Blom’s key pre-distribution system, 506
definition of, 490
Diffie-Hellman, 516
ElGamal, 517
encrypted key exchange (EKE), 538
Günther, 522
MTI/A0, 517–519
relation to key transport, 491
Station-to-station (STS), 519
Key authentication, 492
Key clustering attack on block ciphers, 281
Key confirmation, 492
Key control, 494
Key derivation, 490, 498
Key distribution
confidential keys, 551–555
key layering, 551–553
key translation center, 553–554
symmetric-key certificates, 554–555
public keys, 555–566
authentication trees, 556–559
certificates, 559–561
identity-based, 561–562
implicitly-certified, 562–563
Key distribution center (KDC), 491, 500, 547
Key distribution pattern, 536
Key distribution problem, 16, 546
Key distribution system (KDS), 505
Blom’s KDS bound, 505
security against coalitions, 505
Key escrow, 584–586
agent, 550, 584
Clipper, 584
Key establishment, 489–541
analysis of, 530–534, 540–541
attacks on
interleaving, 531
intruder-in-the-middle, 530
misplaced trust in server, 531

767

reflection, 530
authenticated, 492, 493
compliant, 532
definition of, 35, 490
identity-based, 493
key agreement, see Key agreement
key transport, see Key transport
message-independent, 493
operational, 532
resilient, 532
simplified classification, 491
Key life cycle, 577–581
key states, 580
Key management, 36–38, 543–590
ANSI X9.17 standard, 650
ANSI X9.24 standard, 650
ANSI X9.28 standard, 651
ANSI X9.42 standard, 651
centralized, 546
controlling key usage, 567–570
definition of, 35, 544
ISO 8732 standard, 652
ISO 10202-7 standard, 652
ISO 11166 standard, 652
ISO 11568 standard, 653
ISO/IEC 11770 standard, 647
key agreement, see Key agreement
key distribution, see Key distribution
key establishment, see Key establishment
key life cycle, 577–581
key transport, see Key transport
Key management facility, 549
Key notarization, 568
patent, 642, 658
Key pair, 12
Key pre-distribution scheme, 540
definition of, 490
Key server, 549
Key space, 11, 21, 224
Key tag, 568
Key translation center (KTC), 491, 500, 547, 553
Key transport, 35, 497–504, 506–515, 535–536
AKEP1, 499
AKEP2, 499
Beller-Yacobi (2-pass), 514
Beller-Yacobi (4-pass), 513
COMSET, 536
definition of, 490
Kerberos, 501–502
Needham-Schroeder public-key, 508
Needham-Schroeder shared-key, 503
Otway-Rees protocol, 504
relation to key agreement, 491
Shamir’s no-key protocol, 500

768

X.509 three-way, 512
X.509 two-way, 511
Key update, 490
Keyed hash function, see Message authentication
code (MAC)
Keying material, 544
Keying relationship, 544
Keystream, 20, 193, 194
Keystream generator, 21, 194
Khafre block cipher, 271
attacks on, 281
patent, 644
Khufu block cipher, 271
attacks on, 281
patent, 644
Knapsack generator, 209, 220
Knapsack problem, 131
Knapsack public-key encryption, 300–306
Chor-Rivest, 302–306
Merkle Hellman, 300–302
Knapsack set, 117
density of, 120
Known-key attack, 42, 496, 534
Known-key triangle attack, 538
Known-message attack, 432
Known-plaintext attack, 41, 225
KryptoKnight, 535, 541
KTC, see Key translation center (KTC)

L

L3 -lattice basis reduction algorithm, 118–120, 131
Lagrange’s theorem, 76
Lambda method for discrete logarithms, 128
Lamport’s one-time-password scheme, 396
Lanczos method, 129
Lattice, 118
dimension of, 118
reduced basis, 118
Lattice basis reduction algorithm, 118–120, 131, 317
Law of large numbers, 52
Law of quadratic reciprocity, 72
lcm, see Least common multiple
Leading coefficient, 78
LEAF, 584–585
Leaf of a binary tree, 557
Least common multiple, 64
Least significant digit, 593
Legendre symbol, 72
computing, 73
Lehmer’s gcd algorithm, 607–608, 632
Length of a vector, 118
Liar, 135
Euler, 138
Fermat, 136

Index

strong, 139
Life cycle, see Key life cycle
Linear code, 506
Linear combination, 80
Linear complexity, 198–201
algorithm for computing, see BerlekampMassey algorithm
of a finite sequence, 198
of a random periodic sequence, 199
of a random sequence, 198
of an infinite sequence, 198
profile, 199
Linear complexity profile, 199–200
algorithm for computing, 201
limitations of, 200
of a random sequence, 199
Linear congruential generator, 170, 187
multivariate congruential generator, 187
truncated, 187
Linear consistency attack, 219–220
Linear cryptanalysis
of block ciphers, 258, 271, 278, 280
of stream ciphers, 219
Linear feedback shift register (LFSR), 195–201
connection polynomial of, 196
definition of, 195
delay element of, 195
feedback bit of, 196
initial state of, 196
maximum-length, 197
non-singular, 196
output sequence of, 195
stage of, 195
Linear sieve, 128
Linear syndrome attack, 218
Linear system (solving large), 129
Linearly dependent, 80
Linearly independent, 80
LION block cipher, 282
Little-endian, 344
Little-o notation, 59
Lock-in, 221
Logarithm, 49
LOKI block cipher, 281
LOKI’89, 281
LOKI’91, 270, 281
Long-term key, 553
Low-order digit, 593
Luby-Rackoff block cipher, 282
LUC cryptosystem, 314
LUCDIF, 316
LUCELG, 316
Lucas-Lehmer primality test, 142
Lucifer block cipher, 276

Index

patent, 641, 659

M

m-sequence, 197
MAC, see Message authentication code (MAC)
Manipulation detection code, see Modification detection code
Mapping, 6, 50
Markov cipher, 280
MASH-1 hash function, 352
ISO/IEC 10118-4 standard, 647
MASH-2 hash function, 352
ISO/IEC 10118-4 standard, 647
Master key, 551
Matyas-Meyer-Oseas hash function, 341
ISO/IEC 10118-2 standard, 647
Maurer’s algorithm for provable prime generation,
153, 167
Maurer’s universal statistical test, 183–185, 189
Maximum order complexity, 217
Maximum-length LFSR, 197
Maximum-rank-distance (MRD) code, 317
McEliece public-key encryption, 298–299, 317
decryption algorithm, 299
encryption algorithm, 299
key generation, 298
recommended parameter sizes, 299
security of, 299
MD-strengthening, 334, 335, 337
MD2 hash function, 380
RFC 1319, 655
MD4 hash function, 346
RFC 1320, 655
MD5 hash function, 347
RFC 1321, 655
MD5-MAC, 358
MDC, see Modification detection code
MDC-2 hash function, 342
ISO/IEC 10118-2 standard, 647
patent, 639
MDC-4 hash function, 343
patent, 639
MDS code, 281, 506
Mean, 51
Measure of roughness, 249
Mechanism, 34
Meet-in-the-middle attack
on double DES, 235
on double encryption, 235
time-memory tradeoff, 236
on multiple encryption
time-memory tradeoff, 236
Meet-in-the-middle chaining attack, 374
Merkle channel, 48

769

Merkle one-time signature scheme, 464–466, 485
authentication tree, 466
key generation, 464
patent, 643
security of, 465
signature generation, 465
signature verification, 465
Merkle puzzle scheme, 47, 537
Merkle’s DES-based hash function, 338, 339, 378
Merkle’s meta-method for hashing, 333
Merkle-Hellman knapsack encryption, 300–302,
317–318
basic
decryption algorithm, 301
encryption algorithm, 301
key generation, 300
multiple-iterated
key generation, 302
patent, 637
security of, 302
Mersenne number, 142
Mersenne prime, 142, 143, 160
Message authentication, see Data origin authentication
Message authentication code (MAC), 33, 323,
352–359, 381–383
applications of, 323, 330
based on block ciphers, 353–354
CBC-MAC, see CBC-MAC
CFB-64 MAC, 650
RIPE-MAC, see RIPE-MAC
birthday attack on, 352
customized, 356–358
bucket hashing, 382
MD5-MAC, 358
Message Authenticator Algorithm
(MAA), 356
definition, 325
for stream ciphers, 358–359
CRC-based, 359
Lai-Rueppel-Woollven scheme, 383
Taylor’s scheme, 383
from MDCs, 354–355
envelope method with padding, 355
hash-based MAC, 355
HMAC, 355
secret prefix method, 355
secret suffix method, 355
XOR MAC, 382
ISO 8730 standard, 652
ISO 9807 standard, 652
properties of
compression, 325
computation-resistance, 325

770

ease of computation, 325
key non-recovery, 325
retail MAC, 650
types of attack
adaptive chosen-text, 326
chosen-text, 326
known-text, 326
types of forgery
existential, 326
selective, 326
see also CBC-MAC
Message authentication tag system, 376
Message Authenticator Algorithm (MAA), 356
ISO 8731-2 standard, 652
Message concealing in RSA, 290, 313
Message digest, 321
Message integrity code (MIC), 323
Message space, 11
Message-independent key establishment, 493
Micali-Schnorr pseudorandom bit generator, 186
Miller-Rabin primality test, 139, 165
MIME, 656, 661
Minimum disclosure proof, 421
Minimum polynomial, 156
Mips year, 126
MISSI, 590
Mixed-radix representation, 611, 630
Mixing algebraic systems, 279
Miyaguchi-Preneel hash function, 341
Möbius function, 154
mod notation, 64
Modes of operation
multiple modes, see Multiple encryption, modes
of operation
single modes, see Block cipher, modes of operation
Modification detection code (MDC), 33, 323, 324
Modified-Rabin pseudorandom bit generator, 190
Modified-Rabin signature scheme, 439–442, 482
key generation, 440
security of, 441
signature generation, 440
signature verification, 440
Modular arithmetic, see Multiple-precision modular arithmetic
Modular exponentiation, see Exponentiation
Modular reduction, 599
Barrett, 603–605, 631
Montgomery, 600–602, 631
special moduli, 605–606
Modular representation, see Mixed-radix representation
Modulus, 67
Monic polynomial, 78

Index

Mono-alphabetic substitution cipher, see Substitution cipher
Monobit test, 181
Monotone access structure, 527
Montgomery exponentiation, 619–620
Montgomery multiplication, 602–603
Montgomery reduction, 600–602, 631
MOSS, 656
RFC 1848, 656
Most significant digit, 593
MTI protocols, 518, 537
MTI/A0 key agreement, 517–519, 537
Goss variant, 537
patent, 644, 659
Multi-secret threshold scheme, 527
Multiple encryption, 234–237
definition of, 234
double encryption, 234
modes of operation, 237
triple-inner-CBC mode, 237
triple-outer-CBC mode, 237
triple encryption, 235
E-D-E, 235
two-key triple-encryption, 235
Multiple polynomial quadratic sieve, 97
Multiple-precision integer, 593
Multiple-precision integer arithmetic, 592–599
addition, 594–595
division, 598–599
normalization, 599
gcd, see Greatest common divisor
multiplication, 595–596
discrete Fourier transform (DFT), 631
Karatsuba-Ofman, 630
squaring, 596–597
subtraction, 594–595
Multiple-precision modular arithmetic, 599–606
addition, 600
exponentiation, see Exponentiation
inversion, 610
multiplication
classical, 600
Montgomery multiplication, 602–603
reduction, 599
Barrett, 603–605, 631
Montgomery, 600–602, 631
special moduli, 605–606
subtraction, 600
Multiplexer generator, 220
Multiplicative group
of Zn , 69
of a finite field, 81
Multiplicative inverse, 68
computing, 71, 84, 610

Index

Multiplicative property in RSA, 288, 435, 482
Multiplicity of a factor, 122
Multispeed inner-product generator, 220
Multivariate polynomial congruential generator,
187
Mutual authentication, 387, 402, 405, 494
Mutual information, 57
Mutually exclusive events, 51

N
N-Hash function, 380
Name server, 549
Needham-Schroeder public-key, 508, 536
Needham-Schroeder shared-key, 401, 503, 535
Next-bit test, 171
Next-discrepancy, 200
Nibble, 443
NIST, 654
Noise diode, 40
Non-interactive protocol, 493
Non-interactive ZK proof, 424
Non-malleable encryption, 311, 319
Non-repudiation, 3, 4, 582–584
ISO/IEC 13888 standard, 648
Non-singular
FSR, 203
LFSR, 196
Nonce, 397, 497
Nonlinear combination generator, 205–208
combining function of, 205
Nonlinear feedback shift register, see Feedback shift
register (FSR)
Nonlinear filter generator, 208–209
filtering function, 208
Nonlinear order, 205
Normal basis, 168
exponentiation, 642
multiplication, 642
patents, 642–643, 659
Normal distribution, 176–177
mean of, 176
standard, 176
variance of, 176
Normal polynomial, 168
Normalization, 599
Notarized key, 569
Notary
agent, 550
seal, 569
service, 582
NP, 60
NP-complete, 61
NP-hard, 62
NPC, 61

771

Number field sieve
for discrete logarithms, 128
for integer factorization, 98, 126
implementation reports, 126, 127
general number field sieve, 98
special number field sieve, 98, 126
Number theory, 63–75
Nyberg-Rueppel signature scheme, 460–462, 485
security of, 461
signature generation, 461
signature verification, 461

O
Object identifier (OID), 660
OFB, see Output feedback mode
Off-line trusted third party, 548
Ohta-Okamoto identification protocol, 422
On-line certificate, 576
On-line trusted third party, 547
On-line/off-line signature, 486
patent, 644
One-key encryption, 15
One-sided statistical test, 179
One-time insider, 496
One-time pad, 21, 192–193, 274
patent, 657
One-time password scheme, 395–397
One-time signature scheme, 462–471
Diffie-Lamport, 485
GMR, 468–471
Merkle, 464–466
Rabin, 462–464
validation parameters, 462
One-to-one function, 7–8, 50
One-way cipher, 377
One-way function, 8–9, 327
DES-based, 190, 328
exponentiation modulo a prime, 115, 329
multiplication of large primes, 329
Rabin function, 115
RSA function, 115
One-way hash function (OWHF), 325
One-way permutation, 115, 328
Onto function, 7, 50
Open Systems Interconnection (OSI), 653, 660
Operational, 532
Opponent, 13, 495
see also Attacker
Optimal normal basis, 168, 659
Oracle, 88
Order
generating element of maximum order in Z∗n ,
163
of Z∗n , 69

772

of a finite field, 80
of a group, 75
of a group element, 76, 160
algorithm for determining, 162
of an element in Z∗n , 69
Otway-Rees protocol, 504, 536
Output feedback mode (OFB), 232–233
as a stream cipher, 233
changing IV in, 232
counter mode, 233
feedback size, 233
Outsider, 496
OWHF, see One-way hash function
Ownership, 3

P
P, 60
Palindromic keys of DES, 257
Party, 13
Passcode generator, 402
Passive adversary, 15
Passive attack, 41, 495
Passkey, 395
Passphrase, 390
Passwords (weak authentication), 388–397, 420
aging, 390
attacks on, 391–393
dictionary, 392
exhaustive search, 391
password-guessing, 392
pre-play, 397
replay, 391
encrypted password file, 389
entropy, 392
generator, 387
one-time, 395–397
Lamport’s scheme, 396
passkey, 395
passphrase, 390
personal identification number (PIN), 394
rules, 389
salting, 390
stored password file, 389
UNIX , 393–394
Patents, 635–645, 657–659
ordering and acquiring, 645
priority date, 636
validity period, 636
PEM, see Privacy Enhanced Mail (PEM)
Pepin’s primality test, 166
Perceptrons problem, 423
Perfect forward secrecy, 496, 534
Perfect power
testing for, 89

Index

Perfect secrecy, 42, 227, 307
Perfect secret sharing scheme, 526, 527
Perfect zero-knowledge protocol, 407
Period of a periodic sequence, 180
Periodic sequence, 180
autocorrelation function of, 180
cycle of, 180
period of, 180
Permanent insider, 496
Permutation, 10, 50
Permutation polynomial, 314
Permuted kernel problem, 423
Personal Identification Number (PIN)
ANSI X9.8 standard, 649
ISO 9564 standard, 652
PGP, see Pretty Good Privacy (PGP)
Phi function (φ), 65
Photuris, 661
Physically secure channel, 13
PIKE stream cipher, 222
PIN, see Passwords (weak authentication), see Personal Identification Number (PIN)
PKCS standards, 656, 661
ordering and acquiring, 657
PKCS #1, 445–447, 483
Plaintext, 11
Plaintext-aware encryption scheme, 311–312
Playfair cipher, 239, 274
Pless generator, 218
PN-sequence, 181
Pocklington’s theorem, 144
Pohlig-Hellman algorithm, 107–109, 128
Pohlig-Hellman cipher, 271
patent, 642, 659
Poker test, 182, 188
Policy Certification Authority (PCA), 589
Pollard’s p − 1 algorithm, 92–93, 125
Pollard’s rho algorithm
for discrete logarithms, 106–107, 128
for factoring, 91–92, 125
Polyalphabetic substitution cipher, 18, 241–242,
273–274
auto-key cipher, 242
Beaufort cipher, 241
cipher machine, see Cipher machine
PURPLE cipher, 276
Vigenère cipher
auto-key, 242
compound, 241
full, 242
running-key, 242
simple, 18, 241
single mixed alphabet, 242
Polygram substitution cipher, 239

Index

Polynomial, 78
irreducible, 78
leading coefficient of, 78
Polynomial basis, 83
Polynomial factorization, 122–124, 132
Berlekamp’s Q-matrix algorithm, 124
square-free factorization, 123
Polynomial-time algorithm, 59
Polynomial-time indistinguishability, 318
Polynomial-time statistical test, 171
Polynomially security public-key encryption, 306
Polytime reduction, 61, 88
Practical security, 43
Pre-play attack, 397, 398
Pre-positioned secret sharing scheme, 527
Precision, 593
Preimage, 6, 50
Preimage resistance, 323
Pretty Good Privacy (PGP), 661
Primality proving algorithm, see Primality test, true
primality test
Primality test
probabilistic primality test, 135–142
comparison, 140–142
Fermat’s test, 136
Miller-Rabin test, 139
Solovay-Strassen test, 138
true primality test, 142–145
Atkin’s test, 145
Goldwasser-Kilian test, 166
Jacobi sum test, 144
Lucas-Lehmer test, 142
Pepin’s test, 166
Prime number, 9, 64
Prime number generation, 145–154
algorithms
Gordon’s algorithm, 150
Maurer’s algorithm, 153
NIST method, 151
random search, 146
DSA primes, 150–152
incremental search, 148
provable primes, 152–154
random search, 145–149
strong primes, 149–150
Prime number theorem, 64
Primitive element, see Generator
Primitive normal polynomial, 168
Primitive polynomial, 157–160
algorithm for generating, 160
algorithm for testing, 157
definition of, 84
Primitives, 4
Principal, 495

773

Principal square root, 74
Privacy, see Confidentiality
Privacy Enhanced Mail (PEM), 588, 655
RFCs 1421–1424, 655
Private key, 26, 27, 544
Private-key certificate, see Symmetric-key certificate
Private-key encryption, 15
Probabilistic public-key encryption, 306–312,
318–319
Blum-Goldwasser, 308–311
Goldwasser-Micali, 307–308
security level
polynomially secure, 306
semantically secure, 306
Probability, 50
Probability density function, 176
Probability distribution, 50
Probability theory, 50–55
Probable prime, 136
Product cipher, 20, 251
Proof of knowledge, 406, 421, 422
Proposed Encryption Standard (PES), 279
Protection lifetime, 553, 578
Protocol
authentication, 493
cut-and-choose, 410, 421
definition of, 33, 490
failure of, 34
hybrid, 512
identification, see Identification
key establishment, see Key establishment
message-independent, 493
non-interactive, 493
witness hiding, 423
zero-knowledge, 405–417
Provable prime, 134, 142
Provable security, 43, 533
Prover, 386
Pseudo-collision, 371
Pseudo-Hadamard transform, 266
Pseudo-noise sequence, 181
Pseudoprime, 136
Euler, 138
strong, 139
Pseudorandom bit generator (PRBG), 173–175
ANSI X9.17, 173
definition of, 170
FIPS 186, 174–175
linear congruential generator, 170, 187
Pseudorandom bit sequence, 170
Pseudorandom function, 331
Pseudorandom sequences, 39–41
Pseudosquares modulo n, 74, 99, 308

774

Public key, 26, 27, 544
compared vs. symmetric-key, 31–32, 551
implicitly-certified, 520–522
Public-key certificate, 39, 559–561, 587
data part, 559
distinguished name, 559
signature part, 559
Public-key encryption, 25–27, 283–319
advantages of, 31
disadvantages of, 32
ElGamal, 294–298
knapsack, 300–306
Chor-Rivest, 302–306
Merkle-Hellman, 300–302
LUC, see LUC cryptosystem
McEliece, 298–299
non-malleable, 311
plaintext-aware, 311–312
probabilistic, 306–312
Blum-Goldwasser, 308–311
Goldwasser-Micali, 307–308
Rabin, 292–294
reversible, 28
RSA, 285–291
types of attacks, 285
Williams, 315
PURPLE cipher, 276
Puzzle system, 376, 537

Q
Quadratic congruential generator, 187
Quadratic non-residues, 70
Quadratic residues, 70
Quadratic residuosity problem, 99, 127, 307
Quadratic sieve factoring algorithm, 95–97, 126
implementation reports, 126
Quantum computer, 130
Quantum cryptography, 48, 535
Quotient, 64, 78

R
Rabin one-time signature scheme, 462–464
key generation, 463
resolution of disputes, 463
signature generation, 463
signature verification, 463
Rabin public-key encryption, 292–294, 315
decryption algorithm, 292
encryption algorithm, 292
key generation, 292
security of, 293
use of redundancy, 293
Rabin signature scheme, 438–442, 482
ISO/IEC 9796, 442–444
key generation, 438

Index

signature generation, 438
signature verification, 439
use of redundancy, 439
Rabin’s information dispersal algorithm (IDA),
539
RACE/RIPE project, 421, 536
Radix representation, 592–593
base b, 592
binary, 592
high-order digit, 593
least significant digit, 593
low-order digit, 593
mixed, 611, 630
most significant digit, 593
precision, 593
radix b, 592
Ramp schemes, see Secret sharing
Random bit generator, 39–41, 171–173
cryptographically secure pseudorandom bit
generator, see Cryptographically secure pseudorandom bit generator
(CSPRBG)
definition of, 170
hardware techniques, 172
pseudorandom bit generator, see Pseudorandom bit generator (PRBG)
software techniques, 172
Random cipher, 225
Random cipher model, 246
Random function, 190
poly-random, 190
Random mappings model, 54
Random oracle model, 316
Random square methods, 94–98
Random variable, 51
continuous, 176
entropy of, 56
expected value of, 51
mean of, 51
standard deviation of, 51
variance of, 51
Randomized algorithm, 62–63
Randomized DES (RDES) block cipher, 278
Randomized encryption, 225, 296, 306
Randomized stream cipher, 216
Range of a function, 46
Rate of an iterated hash function, 340
Rational numbers, 49
RC2 block cipher, 282
RC4 stream cipher, 222, 282
RC5 block cipher, 269–270, 280–281
attacks on, 280–281
decryption algorithm, 270
encryption algorithm, 270

Index

key schedule, 270
patent, 659
test vectors, 270
weak keys, 281
Real number, 49
Real-time, 385
Reblocking problem in RSA, 435–436, 482
Receipt, 3
Receiver, 13
Reduced basis, 118
Redundancy, 29, 431
of English, 245
Reflection attack, 417, 530, 540
Registration authority, 549
Related-key attack on block ciphers, 281
Relatively prime, 64
Remainder, 64, 78
Replay attack, 42, 417
Requests for Comments, see RFCs
Residue list sieve, 128
Resilient key establishment protocol, 532
Response, 409
Retail banking, 648
Retail MAC, 650
Reverse certificate, 575
Reversible public-key encryption scheme, 28
Revocation, 3
RFCs, 655–656
ordering and acquiring, 657
Ring, 76–77
commutative, 77
definition of, 76
group of units, 77
polynomial, 78–79
Rip van Winkle cipher, 216
RIPE-MAC, 354, 381
RIPEMD hash function, 380
RIPEMD-128 hash function, 339, 380
RIPEMD-160 hash function, 339, 350
ISO/IEC 10118-3 standard, 647
Root vertex, 557
Rotor-based machine, see Cipher machine
Round function, 251
Round of a product cipher, 20
RP, 63
RSA-129 number, 126, 130
RSA problem, 98–99, 127, 287
security of individual bits, 116
RSA pseudorandom bit generator, 185–186
RSA public-key encryption, 285–291, 312–315
decryption algorithm, 286, 611, 613
decryption exponent, 286
elliptic curve analogue, 315
encryption algorithm, 286

775

encryption exponent, 286
key generation, 286
modulus, 286
patent, 638
prime selection, 290
recommended modulus size, 290
security of, 287–290
adaptive chosen-ciphertext attack, 289,
313
common modulus attack, 289
cycling attacks, 289, 313
forward search attack, 288
message concealing, 290, 313
multiplicative properties, 288
polynomially related plaintext, 313
relation to factoring, 287
small decryption exponent, 288
small encryption exponent, 288, 291, 313
unbalanced, 314
RSA signature scheme, 433–438, 482
ANSI X9.31-1 standard, 651
bandwidth efficiency, 437
ISO/IEC 9796, 442–444
key generation, 434
patent, 638
PKCS #1, 445–447
reblocking problem, 435–436, 482
redundancy function, 437
security of, 434–435
signature generation, 434, 613
signature verification, 434
Run of a sequence, 180
Running key generator, 194
Runs test, 182, 188

S
S/MIME, 661
Safe prime, 537
algorithm for generating, 164
definition of, 164
SAFER block cipher, 266–269, 280
attacks on, 280
SAFER K-64 decryption algorithm, 269
SAFER K-64 encryption algorithm, 268
SAFER K-64 key schedule, 268
SAFER K-128, 280
SAFER SK-64 key schedule, 268
SK-128, 280
test vectors, 269
Salt, 288, 390
Schnorr identification protocol, 414–416, 422
patent, 639
Schnorr signature scheme, 459–460, 484
Brickell-McCurley variant, 484

776

Okamoto variant, 484
patent, 639
signature generation, 459
signature verification, 460
SEAL stream cipher, 213–216
implementation report, 222
patent, 222
test vectors, 215
Sealed authenticator, 361
Sealed key, 568
2nd-preimage resistance, 323, 325
Secrecy, see Confidentiality
Secret broadcasting scheme, 540
Secret key, 544
Secret-key certificate, 588
Secret sharing, 524–528, 538–540
access structure, 526
authorized subset, 527
dynamic, 527
extendable, 526
generalized, 526–528
ideal, 527
information rate, 527
multi-secret threshold, 527
perfect, 526, 527
pre-positioned, 527
ramp schemes, 539
shared control schemes, 524–525
threshold scheme, 525–526
verifiable, 527
visual cryptography, 539
with disenrollment, 528
Secure channel, 13
Secure Hash Algorithm (SHA-1), 348
ANSI X9.30-2 standard, 651
FIPS 180-1 standard, 654
ISO/IEC 10118-3 standard, 647
Secured channel, 13
Security domain, 570
Security policy, 545
Seed, 21, 170
Selective forgery, 326, 432
Self-shrinking generator, 221
Self-synchronizing stream cipher, 194–195
Semantically secure public-key encryption, 306
Semi-weak keys of DES, 257
Sender, 13
Sequence
block of, 180
de Bruijn, 203
gap of, 180
m-sequence, 197
periodic, 180
pn-sequence, 181

Index

pseudo-noise, 181
run of, 180
Sequence numbers, 399
Serial test, 181, 188
Session key, 36, 494
Session key establishment, 491
SHA-1, see Secure Hash Algorithm (SHA-1)
Shadow, 538
Shamir’s no-key protocol, 500, 535
Shamir’s threshold scheme, 526, 539
Shared control schemes, 524–525
Shares, 524–528, 538
SHARK block cipher, 281
Shift cipher, 239
Short-term key, 553
Shrinking generator, 211–212
implementation report, 221
Sieving, 97
Signature, 3, 22–23, 28–30, 425–488
arbitrated, 472–473
blind, see Blind signature scheme
designated confirmer, 487
deterministic, 427
Diffie-Lamport, 485
Digital Signature Algorithm (DSA), 452–454
ElGamal, 454–459
ESIGN, 473–474
fail-stop, see Fail-stop signature scheme
Feige-Fiat-Shamir, 447–449
framework, 426–433
generation algorithm, 426
GMR, 468–471
GQ, 450–451
group, 488
handwritten, 23
Merkle one-time, 464–466
modified-Rabin, 439–442
Nyberg-Rueppel, 460–462
on-line/off-line, 486
Ong-Schnorr-Shamir (OSS), 482, 486
Rabin, 438–442
Rabin one-time, 462–464
randomized, 427
relation to identification, 388
resolution of disputes, 30
RSA, 433–438
Schnorr, 459–460
strongly equivalent, 485
types of attacks, 432
undeniable, see Undeniable signature scheme
verification algorithm, 426
with appendix, 481
framework, 428–430
ISO/IEC 14888 standard, 648

Index

PKCS #1, 445–447
with message recovery, 29
framework, 430–432
ISO/IEC 9796 standard, 442–444, 646,
660
with redundancy, 29
Signature notarization, 583
Signature space, 427
Signature stripping, 510
Signed-digit representation, 627–628
Signed-magnitude representation, 593
Signer, 23
Significance level, 179
Signing transformation, 22
Simple substitution cipher, see Mono-alphabetic substitution cipher
Simulator, 407
Simultaneous diophantine approximation, 121–122
algorithm for, 122
unusually good, 121
Simultaneous multiple exponentiation, 617
Simultaneously secure bits, 115
Single-key encryption, 15
Single-length MDC, 339
Single-precision integer, 593
Singleton bound, 506
SKEME, 661
SKID2 identification protocol, 402, 421
SKID3 identification protocol, 402, 421
SKIP, 661
SKIPJACK block cipher, 282, 654
Sliding-window exponentiation, 616
Small decryption exponent in RSA, 288
Small encryption exponent in RSA, 288, 291, 313
Smart card, 387
ISO 10202 standard, 652
Smooth
integer, 92
polynomial, 112
Snefru hash function, 380
8 × 32 S-boxes, 281
Solovay-Strassen primality test, 138, 165
Span, 80
Sparse linear equations, 129
conjugate gradient method, 129
Lanczos method, 129
Wiedemann algorithm, 129
Special-purpose factoring algorithm, 90
SPKM, 656, 661
Split-knowledge scheme, 525
Splitting an integer, 89
Spread spectrum, 45
Square roots, 99–102
composite modulus, 101–102, 127

777

prime modulus, 100–101, 127
SQROOT problem, 101
Square-free factorization, 123
algorithm for, 123, 132
Square-free integer, 137
Square-free polynomial, 123
Stage
of an FSR, 202
of an LFSR, 195
Standard deviation, 51
Standard normal distribution, 176
Standards, 645–657, 660–661
ANSI, 648–651
FIPS, 654–655
IEEE, 660
Internet, 655–656
ISO/IEC, 645–648, 651–653
PKCS, 656
RFC, 655–656
X.509, 653
Station-to-station (STS) key agreement, 519, 538
Statistical test, 175–185, 188–189
autocorrelation test, 182
frequency test, 181
hypothesis, 179
Maurer’s universal statistical test, 183–185,
189
one-sided test, 179
poker test, 182
polynomial-time, 171
runs test, 182
serial test, 181
significance level, 179
two-sided test, 180
Statistical zero-knowledge protocol, 424
Steganography, 46
Step-1/step-2 generator, 220
Stirling numbers, 53
Stirling’s formula, 59
Stop-and-go generator, 220
Stream cipher, 20–21, 191–222
A5, 222
attacks on
correlation attack, 206, 218
inversion attack, 219
linear consistency attack, 219–220
linear cryptanalysis, 219
linear syndrome attack, 218
lock-in, 221
cellular automata, 222
classification, 192–195
clock-controlled generator, 209–212
alternating step generator, 209–211
m-sequence cascade, 221

778

p-cycle cascade, 220
self-shrinking generator, 221
shrinking generator, 211–212
step-1/step-2 generator, 220
stop-and-go generator, 220
comparison with block ciphers, 192
FISH, 222
GOAL, 219
initial state, 193, 194
keystream, 193, 194
next-state function, 193
nonlinear combination generator, 205–208
Geffe generator, 206
multiplexer generator, 220
multispeed inner-product generator, 220
Pless generator, 218
summation generator, 207
nonlinear filter generator, 208–209
knapsack generator, 209
one-time pad, 192–193
output function, 193, 194
PIKE, 222
randomized stream cipher, 216
RC4, 222
Rip van Winkle cipher, 216
SEAL, 213–216
self-synchronizing stream cipher, 194–195
synchronous stream cipher, 193–194
Strict avalanche criterion (SAC), 277
String-replacement representation, 628–629
Strong collision resistance, 324
Strong equivalent signature schemes, 485
Strong liar, 139
Strong one-way hash function, 325
Strong prime, 149–150
algorithm for generating, 150
definition of, 149, 291
Hellman-Bach patent, 643
usage in RSA, 291
Strong pseudoprime, 139
Strong pseudoprime test, see Miller-Rabin primality test
Strong witness, 139
Subexponential-time algorithm, 60
Subfield, 77
Subgroup, 76
Subliminal channel, 485
broadband, 485
narrowband, 485
Subset sum problem, 61, 117–122, 190
meet-in-the-middle algorithm, 118
naive algorithm, 117
superincreasing, 300
using L3 algorithm, 120

Index

Subspace of a vector space, 80
Substitution cipher, 17–18, 238–241
homophonic, 17, 240
mono-alphabetic, 17, 239
affine cipher, 239
Caesar cipher, 239
shift cipher, 239
unicity distance of, 247
polyalphabetic, 18
polygram, 239
Hill cipher, 240
Playfair cipher, 239
Substitution-permutation (SP) network, 251
Summation generator, 207, 218
Superincreasing subset sum problem, 300
algorithm for solving, 300
Superuser, 389
Surjective function, 46, 50
SWIFT, 586
Symmetric cryptographic system, 544
Symmetric key, 544
compared vs. public-key, 31–32, 551
Symmetric-key certificate, 554–555, 587
Symmetric-key encryption, 15–21
advantages of, 31
block cipher, 223–282
definition of, 15
disadvantages of, 31
stream cipher, 191–222
Synchronous stream cipher, 193–194
binary additive stream cipher, 194
Syndrome decoding problem, 190, 423

T
Tapper, 13
TEA block cipher, 282
TEMPEST, 45
Teraflop, 44
Terminal key, 552
Test vectors
DES, 256
FEAL, 262
IDEA, 265
MD4, 345
MD5, 345
MD5-MAC, 358
RC5, 270
RIPEMD-160, 345
SAFER, 269
SHA-1, 345
3-WAY block cipher, 281
Threshold cryptography, 534
Threshold scheme, 525–526
Blakley, 538

Index

Shamir, 526, 539
Ticket, 501, 570, 586
Time-memory tradeoff, 236, 273
Time-variant parameter, 362, 397–400, 497
nonce, 397
random numbers, 398–399
sequence numbers, 399
timestamps, 399–400
Timestamp, 3, 399–400, 420, 581–582
agent, 550
Toeplitz matrix, 382
Transaction authentication, 362
Transformation, 6
Transinformation, 57
Transposition cipher, 18, 238
compound, 238
simple, 18, 238
unicity distance of, 246
Trapdoor one-way function, 9, 26
Trapdoor predicate, 318
Tree authentication, 376
patent, 637
Trinomial, 154
Triple encryption, 235–237, 272
Triple-DES, 272, 651
ANSI X9.52 standard, 651
Triple-inner-CBC mode, 237
Triple-outer-CBC mode, 237
Truncated differential analysis, 271, 280
Trust model, 572
centralized, 573
directed graph, 575
distributed, 575
hierarchy with reverse certificates, 575
rooted chain, 573
separate domains, 573
strict hierarchical, 573
Trusted server, 491
Trusted third party (TTP), 30, 36, 491, 547–550,
581–584
authentication server, 549
certificate directory, 549
certification authority (CA), 548
functionally trusted, 39
in-line, 547
KDC, see Key distribution center (KDC)
key access server, 549
key escrow agent, 550
key generator, 549
key management facility, 549
key server, 549
KTC, see Key translation center (KTC)
name server, 549
notary agent, 550

779

off-line, 548
on-line, 547
registration authority, 549
timestamp agent, 550
unconditionally trusted, 39
TTP, see Trusted third party (TTP)
Turing-Kolmogorov-Chaitin complexity, 217
Two’s complement representation, 594
2-adic span, 218
Two-bit test, 181
Two-key triple-encryption, 235
chosen-plaintext attack on, 236
known-plaintext attack on, 237
Two-sided statistical test, 180
Type I error, 179
Type II error, 179

U
Unbalanced RSA, 314
Unblinding function, 475
Unconcealed message, 290
Unconditional security, see Perfect secrecy, 533
Unconditionally trusted third party, 39
Undeniable signature scheme, 476–478, 487–488
Chaum-van Antwerpen, 476–478
confirmer, 487
Unicity distance
definition of, 246
known-plaintext, 235
of a cascade cipher, 272
of a mono-alphabetic substitution cipher, 247
of a transposition cipher, 246
Unilateral authentication, 387, 401–402, 405, 494
Union of sets, 49
Unique factorization domain, 81
Unit, 68, 77, 103, 114
Universal classes of hash function, 376
Universal exponent, 287
Universal forgery, 482
Universal one-way hash function, 377
Universal statistical test, see Maurer’s universal
statistical test
UNIX passwords, 393–394
Unsecured channel, 13
Unusually good simultaneous diophantine approximation, 121, 317
Userid, 388

V
Validation, 3
Validation parameters, 462
Variance, 51
Vector space, 79–80
dimension of, 80
standard basis, 80

780

subspace of, 80
Vector-addition chains, 622–623
Verifiable secret sharing, 527, 539
Verification algorithm, 426
Verification transformation, 22
Verifier, 23, 385, 386
Vernam cipher, see One-time pad
Vigenère cipher, see Polyalphabetic substitution cipher
Visual cryptography, 539

W
WAKE block cipher, 282
Weak collision resistance, 324
Weak keys of DES, 257
Weak one-way hash function, 325
Wheatstone disc, 274
Wholesale banking, 648
Wiedemann algorithm, 129
Williams’ public-key encryption, 315
Witness, 135, 409
Euler, 137
Fermat, 136
strong, 139
Witness hiding protocol, 423
Witness indistinguishability, 423
Witnessing, 3
Work factor, 44
historical, 44
Worst-case running time, 58
Wyner’s wire-tap channel, 535

X
X.509 authentication protocol, 536
three-way, 512
two-way, 511
X.509 certificate, 587
X.509 standard, 653
XOR, see Exclusive-or

Y
Yuval’s birthday attack, 369

Z
Zero-knowledge identification, 405–417, 421–424
Brickell-McCurley, 423
comparison of protocols, 416–417
constrained linear equations problem, 423
extended Fiat-Shamir, 422
Feige-Fiat-Shamir, 410–412
Fiat-Shamir (basic version), 408
Fischer-Micali-Rackoff, 422
GQ, 412–414
Ohta-Okamoto, 422
permuted kernel problem, 423

Index

Schnorr, 414–416
syndrome decoding problem, 423
Zero-knowledge protocol, 405–417, 421–424
auxiliary-input, 423
black-box simulation, 423
challenge, 409
completeness, 406
computational, 407
extracting secret, 406
for possession of discrete log, 422
parallel version, 412
perfect, 407
proof of knowledge, 406, 421, 422
proof of membership, 421
response, 409
simulator, 407
soundness, 406
statistical, 424
witness, 409
Ziv-Lempel complexity, 217
Zp -operation, 82
ZPP, 63
PAPER_TEXT
