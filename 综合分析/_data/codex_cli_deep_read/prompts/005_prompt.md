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
# [005] The Codebreakers: The Comprehensive History of Secret Communication from Ancient Times to the Internet
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
编号：005
题名：The Codebreakers: The Comprehensive History of Secret Communication from Ancient Times to the Internet
年份：1997
DOI：10.2307/20048054
来源：Foreign Affairs
PDF：paper/10.2307_20048054.pdf
已有粗分类：加密流量分类与应用识别
二级关联：无
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\005.txt
- 原始字符数：1076019
- 本次发送字符数：140042
- 是否截断：True

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Some of the things you will learn in THE CODEBREAKERS
• How secret Japanese messages were decoded in Washington hours before Pearl Harbor.
• How German codebreakers helped usher in the Russian Revolution.
• How John F. Kennedy escaped capture in the Pacific because the Japanese failed to solve a
simple cipher.
• How codebreaking determined a presidential election, convicted an underworld syndicate
head, won the battle of Midway, led to cruel Allied defeats in North Africa, and broke up a vast
Nazi spy ring.
• How one American became the world's most famous codebreaker, and another became the
world's greatest.
• How codes and codebreakers operate today within the secret agencies of the U.S. and Russia.
• And incredibly much more.
"For many evenings of gripping reading, no better choice can be made than this book."
—Christian Science Monitor

THE

Codebreakers
The Story of Secret Writing
By DAVID KAHN
(abridged by the author)
A SIGNET BOOK from
NEW AMERICAN LIBRARV
TIMES MIRROR

Copyright © 1967, 1973 by David Kahn
All rights reserved.
No part of this book may be reproduced or transmitted
in any form or by any means, electronic or mechanical,
including photocopying, recording or by any information
storage and retrieval system, without permission in writing
from the publisher. For information address
The Macmillan Company, 866 Third Avenue, New York,
New York 10022.
Library of Congress Catalog Card Number: 63-16109
Crown copyright is acknowledged for the following illustrations
from Great Britain's Public Record Office:
S.P. 53/18, no. 55, the Phelippes forgery,
and P.R.O. 31/11/11, the Bergenroth reconstruction.
Published by arrangement with The Macmillan Company
FIRST PRINTING SECOND PRINTING THIRD PRINTING FOURTH PRINTING FIFTH PRINTING SIXTH PRINTING SEVENTH PRINTING
EIGHTH PRINTING NINTH PRINTING TENTH PRINTING
SIGNET TRADEMARK: REG. TJ.S. PAT. OFF. AND FOREIGN COUNTRIES
REGISTERED TRADEMARK---MARCA REGISTBADA
HECHO EN CHICAGO, U.S.A.

SIGNET, SIGNET CLASSICS, SIGNETTE, MENTOR AND PLUME BOOKS

are published by The New American Library, Inc.,

1301 Avenue of the Americas, New York, New York 10019
FIRST PRINTING, FEBRUARY, 1973
PRINTED IN THE UNITED STATES OF AMERICA

To my Parents
and my Grandmother

Contents
A Note on the Abridged Version
Preface
A Few Words
1. One Day of Magic: I
2. One Day of Magic: II
3. The First 3,000 Years
4. The Rise of the West
5. On the Origin of a Species
6. The Era of the Black Chambers
7. The Contribution of the Dilettantes
8. Room 40
9. A War of Intercepts
10. Two Americans
11. Secrecy for Sale
12. Duel in the Ether: I
13. Duel in the Ether: II
14. Censors, Scramblers, and Spies
15. The Scrutable Orientals

16. PYCCKAJI Kranrojioras
17. N.S.A.
18. Heterogeneous Impulses
19. Ciphers in the Past Tense
20. The Anatomy of Cryptology
Suggestions for Further Reading
Index

A Note on the Abridged Version
MANY PEOPLE have urged me to put out a paperback edition of The Codebreakers. Here it is.

It comprises about a third of the original. This was as big as the publishers and I could make it and still
keep the price within reason.
In cutting the book, I retained mainly stories about how codebreaking has affected history, particularly
in World War II, and major names and stages in the history of cryptology. I eliminated all source notes and
most of the technical matter, as well as material peripheral to strict codebreaking such as biographies, the
invention of secondary cipher systems, and miscellaneous uses of various systems.
I had no space for new material, but I did correct the errors reported to me and updated a few items.
The chapters have been slightly rearranged.
Readers wanting to know more about a specific point should consult the text and notes of the original.
If any reader wishes to offer any corrections or to tell me of his own experiences in this field, I would
be very grateful if he would send them to me.
—D.K.
Windsor Gate
Great Neck, New York

Preface
CODEBREAKING is the most important form of secret intelligence in the world today. It produces much more

and much more trustworthy information than spies, and this intelligence exerts great influence upon the
policies of governments. Yet it has never had a chronicler.
It badly needs one. It has been estimated that cryptanalysis saved a year of war in the Pacific, yet the
histories give it but passing mention. Churchill's great history of World War II has been cleaned of every
single reference to Allied communications intelligence except one (and that based on the American Pearl
Harbor investigation), although Britain thought it vital enough to assign 30,000 people to the work. The
intelligence history of World War II has never been written. All this gives a distorted view of why things
happened. Furthermore, cryptology itself can benefit, like other spheres of human endeavor, from knowing
its major trends, its great men, its errors made and lessons learned.
I have tried in this book to write a serious history of cryptology. It is primarily a report to the public on
the important role that cryptology has played, but it may also orient cryptology with regard to its past and
alert historians to the sub rosa influence of cryptanalysis. The book seeks to cover the entire history of
cryptology. My goal has been twofold: to narrate the development of the various methods of making and
breaking codes and ciphers, and to tell how these methods have affected men.
When I began this book, I, like other well-informed amateurs, knew about all that had been published
on the history of cryptology in books on the subject. How little we really knew! Neither we nor any
professionals realized that many valuable articles lurked in scholarly journals, or had induced any
cryptanalysts to tell their stories for publication, or had tapped the vast treasuries of documentary material,
or had tried to take a long view and ask some questions that now appear basic. I believe it to be true that,
from the point of view of the material previously published in books on cryptology, what is new in this
book is 85 to 90 per cent.
Yet it is not exhaustive. A foolish secrecy still clothes much of World War II cryptology—though I
believe the outlines of the achievements are known—and to tell just that story in full would require a book
the size of this. Even in, say, the 18th century, the unexplored manuscript material is very great.
Nor is this a textbook. I have sketched a few methods of solution. For some readers even this will be too
much; them I advise skip this material. They will not have a full understanding of what is going on, but that
will not cripple their comprehension of the stories. For readers who want more detail on these methods, I
recommend, in the rear of this book, some other works and membership in the American Cryptogram
Association.
In my writing, I have tried to adhere to two principles. One was to use primary sources as much as
possible. Often it could not be done any other way, since nothing had been published on a particular matter.
The other principle was to try to make certain that I did not give cryptology sole and total credit for
winning a battle or making possible a diplomatic coup or whatever happened if, as was usual, other factors
played a role. Narratives which make it appear as if every event in history turned upon the subject under
discussion are not history but journalism. They are especially prevalent in spy stories, and cryptology is not
immune. The only other book-length attempt to survey the history of cryptology, the late Fletcher Pratt's
Secret and Urgent, published in 1939, suffers from a severe case of this special pleading. Pratt writes
thrillingly—perhaps for that very reason—but his failure to consider the other factors, together with his
errors and omissions, his false generalizations based on no evidence, and his unfortunate predilection for
inventing facts vitiate his work as any kind of a history. (Finding this out was disillusioning, for it was this
book, borrowed from the Great Neck Library, that interested me in cryptology.) I think that although trying
to balance the story with the other factors may detract a little from the immediate thrill, it charges it with
authenticity and hence makes for long-lasting interest: for this is how things really happened.
In the same vein, I have not made up any conversations, and my speculations about things not a matter
of record have been marked as such in the notes in the full-length version. I have documented all important
facts, except that in a few cases I have had to respect the wishes of my sources for anonymity.
The original publisher submitted the manuscript to the Department of Defense on March 4, 1966, which
requested three minor deletions—to all of which I acceded—before releasing the manuscript for
publication.
DAVID KAHN

Windsor Gate
Great Neck, New York
Paris

A Few Words
EVERY TRADE has its vocabulary. That of cryptology is simple, but even so a familiarity with its terms
facilitates understanding. A glossary may also serve as a handy reference. The definitions in this one are
informal and ostensive. Exceptions are ignored and the host of minor terms are not defined—the text covers
these when they come up.
The plaintext is the message that will be put into secret form. Usually the plaintext is in the native
tongue of the communicators. The message may be hidden in two basic ways. The methods of
steganography conceal the very existence of the message. Among them are invisible inks and microdots
and arrangements in which, for example, the first letter of each word in an apparently innocuous text spells
out the real message. (When steganography is applied to electrical communications, such as a method that
transmits a long radio message in a single short spurt, it is called transmission security.) The methods of
cryptography, on the other hand, do not conceal the presence of a secret message but render it
unintelligible to outsiders by various transformations of the plaintext.
Two basic transformations exist. In transposition, the letters of the plaintext are jumbled; their normal
order is disarranged. To shuffle secret into ETCRSE is a transposition. In substitution, the letters of the
plaintext are replaced by other letters, or by numbers or symbols. Thus secret might become 19 5 3 18 5 20,
or XIWOXY in a more complicated system. In transposition, the letters retain their identities— the two e's of
secret are still present in ETCRSE—but they lose their positions, while in substitution the letters retain their
positions but lose their identities. Transposition and substitution may be combined.
Substitution systems are much more diverse and important than transposition systems. They rest on the
concept of the cipher alphabet. This is the list of equivalents used to transform the plaintext into the secret
form. A sample cipher alphabet might be:
plaintext letters abcdefghijklm
cipher letters LBQACSRDTOFVM
plaintext letters nopqrstuvwxyz
cipher letters HWIJXGKYUNZEP

This graphically indicates that the letters of the plaintext are to be replaced by the cipher letters beneath
them, and vice versa. Thus, enemy would become CHCME, and swc would reduce to foe. A set of such
correspondences is still called a "cipher alphabet" if the plaintext letters are in mixed order, or even if they
are missing, because cipher letters always imply plaintext letters.
Sometimes such an alphabet will provide multiple substitutes for a letter. Thus plaintext e, for
example, instead of always being replaced by, say, 16, will be replaced by any one of the figures 16, 74, 35,
21. These alternates are called homophones. Sometimes a cipher alphabet will include symbols that mean
nothing and are intended to confuse interceptors; these are called nulls.
As long as only one cipher alphabet is in use, as above, the system is called monoalpbabetic. When,
however, two or more cipher alphabets are employed in some kind of prearranged pattern, the system
becomes polyalphabetic. A simple form of polyalphabetic substitution would be to add another cipher
alphabet under the one given above and then to use the two in rotation, the first alphabet for the first
plaintext letter, the second for the second, the first again for the third plaintext letter, the second for the
fourth, and so on. Modern cipher machines produce polyalphabetic ciphers that employ millions of cipher
alphabets.
Among the systems of substitution, code is distinguished from cipher. A code consists of thousands of
words, phrases, letters, and syllables with the codewords or code-numbers (or, more generally, the
codegroups) that replace these plaintext elements.
plaintext
emplacing
employ
encodeword

enable

DVAP
DVBO
DVCN
DVDM

enabled

DVEL

enabled to

DVFK

This means, of course, that DVDM replaces enable. If the plaintext and the code elements both run in
alphabetical or numerical order, as above, the code is a one-part code, because a single book serves for
both en- and decoding. If, however, the code equivalents stand in mixed order opposite their plaintext
elements, like this
Plaintext

codenumber

shield (for)
shielded
shielding
shift(s)
ship
ships

51648
07510
10983
43144
35732
10762

the code is a two-part code, because a second section, in which the code elements are in regular order, is
required for decoding:
codenumber plaintext

10980
10981
10983
10986
10988
10990

was not
spontaneous (ly)
shielding
April 13
withdrawn from
acknowledge

In a sense, a code comprises a gigantic cipher alphabet, in which the basic plaintext unit is the word or
the phrase; syllables and letters are supplied mainly to spell out words not present in the code. In ciphers,
on the other hand, the basic unit is the letter, sometimes the letter-pair (digraph or bigram), very rarely
larger groups of letters (polygrams). The substitution and transposition systems illustrated above are
ciphers. There is no sharp theoretical dividing line between codes and ciphers; the latter shade into the
former as they grow larger. But in modern practice the differences are usually quite marked. Sometimes the
two are distinguished by saying that ciphers operate on plaintext units of regular length (all single letters or
all groups of, say, three letters), whereas codes operate on plaintext groups of variable length (words,
phrases, individual letters, etc.). A more penetrating and useful distinction is that code operates on
linguistic entities, dividing its raw material into meaningful elements like words and syllables, where as
cipher does not—cipher will split the t from the h in the, for example.
For 450 years, from about 1400 to about 1850, a system that was half a code and half a cipher
dominated cryptography. It usually had a separate cipher alphabet with homophones and a codelike list of
names, words, and syllables. This list, originally just of names, gave the system its name: nomenclator.
Even though late in its life some nomenclators grew larger than some modern codes, such systems are still
called "nomenclators" if they fall within this historical period. An odd characteristic is that nomenclators
were always written on large folded sheets of paper, whereas modern codes are almost invariably in book
or booklet form. The commercial code is a code used in business primarily to save on cable tolls; though
some are compiled for private firms, many others are sold to the public and therefore provide no real
secrecy.
Most ciphers employ a key, which specifies such things as the arrangement of letters within a cipher
alphabet, or the pattern of shuffling in a transposition, or the settings on a cipher machine. If a word or
phrase or number serves as the key, it is naturally called the keyword or keyphrase or keynumber. Keys
exist within a general system and control that system's variable elements. For example, if a polyalphabetic
cipher provides 26 cipher alphabets, a keyword might define the half dozen or so that are to be used in a
particular message.
Codewords or codenumbers can be subjected to transposition or substitution just like any other group
of letters or numbers—the transforming processes do not ask that the texts given to them be intelligible.
Code that has not yet undergone such a process—called superencipherment —or which has been

deciphered from it is called placode, a shortening of "plain code." Code that has been transformed is called
encicode, from "enciphered code."
To pass a plaintext through these transformations is to encipher or encode it, as the case may be. What
comes out of the transformation is the ciphertext or the codetext. The final secret message, wrapped up
and sent, is the cryptogram. (The term "ciphertext" emphasizes the result of encipherment more, while
"cryptogram" emphasizes the fact of transmission more; it is analogous to "telegram.") To decipher or
decode is for the persons legitimately possessing the key and system to reverse the transformations and
bare the original message. It contrasts with cryptanalyze, in which persons who do not possess the key or
system— a third party, the "enemy"—break down or solve the cryptogram. The difference is, of course,
crucial. Before about 1920, when the word cryptanalysis was coined to mean the methods of breaking
codes and ciphers, "decipher" and "decode" served in both senses (and occasionally still do), and in
quotations where they are used in the sense of solve, they are retained if they will not confuse. Sometimes
cryptanalysis is called codebreaking; this includes solving ciphers. The original intelligible text that
emerges from either decipherment or cryptanalysis is again called plaintext. Messages sent without
encipherment are cleartext or in clear, though they are sometimes called in plain language.
Cryptology is the science that embraces cryptography and cryptanalysis, but the term "cryptology"
sometimes loosely designates the entire dual field of both rendering signals secure and extracting
information from them. This broader field has grown to include many new areas; it encompasses, for
example, means to deprive the enemy of information obtainable by studying the traffic patterns of radio
messages, and means of obtaining information from radar emissions. An outline of this larger field, with its
opposing parts placed opposite one another, and with a few of the methods of each part given in
parentheses, would be:
SIGNAL SECURITY

SIGNAL INTELLIGENCE

Communication Security
Steganography (invisible inks, open
codes, messages in hollow heels)
and Transmission Security (spurt
radio systems)
Traffic Security (call-sign changes,
dummy messages, radio silence)

Communication Intelligence
Interception and Direction-Finding

Cryptography (codes and ciphers,
ciphony, cifax)

Cryptanalysis

Traffic Analysis (direction-finding
fixes, message-flow studies, radiofingerprinting)

Electronic Security
Electronic Intelligence
Emission Security (shifting of raElectronic Reconnaissance (eavesdar frequencies)
dropping on radar emissions)
Counter-Countermeasures ("lookCountermeasures (jamming, false
ing-through" jammed radar) radar echoes)

This book employs certain typographic conventions for simplicity and economy. Plaintext is always set
lower case; when it occurs in the running text (as opposed to its occurrence in the diagrams), it is also in
italics. Cipher-text or codetext is set in SMALL CAPS in the text, keys in LARGE CAPS. They are
distinguished in the diagrams by labels. Cleartext and translations of foreign-language plaintext are in
roman within quotation marks. The sound of a letter or syllable or word, as distinguished from its written
form, is placed within diagonals, according to the convention widely followed in linguistics; thus /t/ refers
to the unvoiced stop normally represented by that letter and not to the graphic symbol t.
D. K.

1. One Day of Magic: I
AT 1:28 on the morning of December 7, 1941, the big ear of the Navy's

radio station on Bainbridge Island near Seattle trembled to vibrations in

the ether. A message was coming through on the Tokyo-Washington
circuit. It was addressed to the Japanese embassy, and Bainbridge
reached up and snared it as it flashed overhead. The message was short,
and its radiotelegraph transmission took only nine minutes. Bainbridge
had it all by 1:37.
The station's personnel punched the intercepted message on a
teletype tape, dialed a number on the teletypewriter exchange, and when
the connection had been made, fed the tape into a mechanical
transmitter that gobbled it up at 60 words per minute.
The intercept reappeared on a page-printer in Room 1649 of the Navy
Department building on Constitution Avenue in Washington, D.C. What
went on in this room, tucked for security's sake at the end of the first
deck's sixth wing, was one of the most closely guarded secrets of the
American government. For it was in here—and in a similar War
Department room in the Munitions Building next door—that the United
States peered into the most confidential thoughts and plans of its
possible enemies by shredding the coded wrappings of their dispatches.
Room 1649 housed OP-20-GY, the cryptanalytic section of the Navy's
cryptologic organization, OP-20-G. The page-printer stood beside the
desk of the GY watch officer. It rapped out the intercept in an original and
a carbon copy on yellow and pink teletype paper just like news on a city
room wireservice ticker. The watch officer, Lieutenant (j.g.) Francis M.
Brotherhood, U.S.N.R., a curly-haired, brown-eyed six-footer, saw
immediately from indicators that the message bore for the guidance of
Japanese code clerks that it was in the top Japanese cryptographic
system.
This was an extremely complicated machine cipher which American
cryptanalysts called PURPLE. Led by William F. Friedman, Chief
Cryptanalyst of the Army Signal Corps, a team of codebreakers had
solved Japan's enciphered dispatches, deduced the nature of the
mechanism that would effect those letter transformations, and
painstakingly built up an apparatus that cryptographically duplicated
the Japanese machine. The Signal Corps had then constructed several
additional PURPLE machines, using a hodgepodge of manufactured parts,
and had given one to the Navy. Its three components rested now on a
table in Room 1649: an electric typewriter for input; the cryptographic
assembly proper, consisting of a plugboard, four electric coding rings,
and associated wires and switches, set on a wooden frame; and a
printing unit for output. To this precious contraption, worth quite
literally more than its weight in gold, Brotherhood carried the intercept.
He flicked the switches to the key of December 7. This was a
rearrangement, according to a pattern ascertained months ago, of the
key of December 1, which OP-20-QY had recovered. Brotherhood typed

out the coded message. Electric impulses raced through the maze of
wires, reversing the intricate enciphering process. In a few minutes, he
had the plaintext before him.
It was in Japanese. Brotherhood had taken some of the orientation
courses in that difficult language that the Navy gave to assist its
cryptanalysts. He was in no sense a translator, however, and none was
on duty next door in OP-20-GZ, the translating section. He put a red
priority sticker on the decode and hand-carried it to the Signal
Intelligence Service, the Army counterpart of OP-20-O, where he knew
that a translator was on overnight duty. Leaving it there, he returned to
OP-20-G. By now it was after 5 a.m. in Washington—the message having
lost three hours as it passed through three time zones in crossing the
continent.
The S.I.S translator rendered the Japanse as: "Will the Ambassador
please submit to the United States Government (if possible to the
Secretary of State) our reply to the United States at 1:00 p.m. on the 7th,
your time." The —"reply" referred to had been transmitted by Tokyo in 14
parts over the past 18½ hours, and Brotherhood had only recently
decrypted the 14th part on the PURPLE machine. It had come out in the
English in which Tokyo had framed it, and its ominous final sentence
read: "The Japanese Government regrets to have to notify hereby the
American Government that in view of the attitude of the American
Government it cannot but consider that it is impossible to reach an
agreement through further negotiations." Brotherhood had set it by for
distribution early in the morning.
The translation of the message directing delivery at one o'clock had
not yet come back from S.I.S. when Brotherhood was relieved at 7 a.m.,
and he told his relief, Lieutenant (j.g.) Alfred V. Pering, about it. Half an
hour later, Lieutenant Commander Alwin D. Kramer, the Japaneselanguage expert who headed GZ and delivered the intercepts, arrived. He
saw at once that the all-important conclusion of the long Japanese
diplomatic note had come in since he had distributed the 13 previous
parts the night before. He prepared a smooth copy from the rough decode
and had his clerical assistant, Chief Yeoman H. L. Bryant, type up the
usual 14 copies. Twelve of these were distributed by Kramer and his
opposite number in S.I.S. to the President, the secretaries of State, War,
and Navy, and a handful of top-ranking Army and Navy officers. The two
others were file copies. This decode was part of a whole series of
Japanese intercepts, which had long ago been given a collective
codename, partly for security, partly for ease of reference, by a previous
director of naval intelligence, Rear Admiral Walter S. Anderson. Inspired,
no doubt, by the mysterious daily production of the information and by
the aura of sorcery and the occult that has always enveloped cryptology,
he called it MAGIC.

When Bryant had finished, Kramer sent S.I.S. its seven copies, and at
8 o'clock took a copy to his superior, Captain Arthur H. McCollum, head
of the Far Eastern Section of the Office of Naval Intelligence.
From: Tokyo
To:

Washington

December 7, 1941
Purple (Urgent - Very Important)
#907.

To be handled in goverment code.
Re: my #902a.

Will the Ambaagador please submit to the United States
Government (If possible to the Secretary of State) our reply to
the United States at 1:00 p.m. on the 7th, your time.
a - JD-1:7143 - text of Japanese reply.
MAGIC'S solution of the Japanese one o'clock delivery message

He then busied himself in his office, working on intercepted traffic,
until 9:30, when he left to deliver the 14th part of Tokyo's reply to
Admiral Harold F. Stark, the Chief of Naval Operations, to the White
House, and to Frank Knox, the Secretary of the Navy. Knox was meeting
at 10 a.m. that Sunday morning in the State Department with Secretary
of War Henry L. Stimson and Secretary of State Cordell Hull to discuss
the critical nature of the American negotiations with Japan, which, they
knew from the previous 13 parts, had virtually reached an impasse.
Kramer returned to his office about 10:20, where the translation of the
message referring to the one o'clock delivery had arrived from S.I.S. while
he was on his rounds.
Its import crashed in upon him at once. It called for the rupture of
Japan's negotiations with the United States by a certain deadline. The
hour set for the Japanese ambassadors to deliver the notification—1 p.m.
on a Sunday—was highly unusual. And, as Kramer had quickly
ascertained by drawing a navigator's time circle, 1 p.m. in Washington
meant 7:30 a.m. in Hawaii and a couple of hours before dawn in the
tense Far East around Malaya, which Japan had been threatening with
ships and troops.
Kramer immediately directed Bryant to insert the one o'clock message
into the reddish-brown looseleaf cardboard folders in which the MAGIC
intercepts were bound. He included several other intercepts, adding one

at the last minute, then slipped the folders into the leather briefcases,
zipped these shut, and snapped their padlocks. Within ten minutes he
was on his way.
He went first to Admiral Stark's office, where a conference was in
session, and indicated to McCollum, who took the intercept from him,
the nature of the message and the significance of its timing. McCollum
grasped it at once and disappeared into Stark's office. Kramer wheeled
and hurried down the passageway. He emerged from the Navy
Department building and turned right on Constitution Avenue, heading
for the meeting in the State Department four blocks away. The urgency of
the situation washed over him again, and he began to move on the
double.
This moment, with Kramer running through the empty streets of
Washington bearing his crucial intercept, an hour before sleepy code
clerks at the Japanese embassy had even deciphered it and an hour
before the Japanese planes roared off the carrier flight decks on their
treacherous mission, is perhaps the finest hour in the history of
cryptology. Kramer ran while an unconcerned nation slept late, ignored
aggression in the hope that it would go away, begged the hollow gods of
isolationism for peace, and refused to entertain—except humorously—the
possibility that the little yellow men of Japan would dare attack the
mighty United States. The American cryptanalytic organization swept
through this miasma of apathy to reach a peak of alertness and
accomplishment unmatched on that day of infamy by any other agency
in the United States. That is its great achievement, and its glory.
Kramer's sprint symbolizes it.
Why, then, did it not prevent Pearl Harbor? Because Japan never sent
any message saying anything like "We will attack Pearl Harbor." It was
therefore impossible for the cryptanalysts to solve one. Messages had
been intercepted and read in plenty dealing with Japanese interest in
warship movements into and out of Pearl Harbor, but these were
evaluated by responsible intelligence officers as on a par with the many
messages dealing with American warships in other ports and the Panama
Canal. The causes of the Pearl Harbor disaster are many and complex,
but no one has ever laid any of whatever blame there may be at the doors
of OP-20-G or S.I.S. On the contrary, the Congressional committee that
investigated the attack praised them for fulfilling their duty in a manner
that "merits the highest commendation."
As the climax of war rushed near, the two agencies— together the
most efficient and successful codebreaking organization that had ever
existed—scaled heights of accomplishment greater than any they had
ever achieved. The Congressional committee, seeking the responsibility

for the disaster, exposed their activity on almost a minute-by-minute
basis. For the first time in history, it photographed in fine-grained detail
the operation of a modern code-breaking organization at a moment of
crisis. This is that film. It depicts OP-20-G and S.I.S. in the 24 hours
preceding the Pearl Harbor attack, with the events of the past as
prologue. It is the story of one day of MAGIC.
The two American cryptanalytic agencies had not sprung full-blown
into being like Athena from the brow of Zeus. The Navy had been solving
at least the simpler Japanese diplomatic and naval codes in Rooms 1649
and 2646 on the "deck" above since the 1920s. The Army's
cryptanalytical work during the 1920s was centered in the so-called
American Black Chamber under Herbert O. Yardley, who had organized
it as a cryptologic section of military intelligence in World War I. It was
maintained in secrecy in New York jointly by the War and State
departments, and perhaps its greatest achievement was its 1920 solution
of Japanese diplomatic codes. At the same time, the Army's cryptologic
research and code-compiling functions were handled by William
Friedman, then as later a civilian employee of the Signal Corps. In 1929,
Henry L. Stimson, then Secretary of State, withdrew State Department
support from the Black Chamber on ethical grounds, dissolving it. The
Army decided to consolidate and enlarge its codemaking and
codebreaking activities. Accordingly, it created the Signal Intelligence
Service, with Friedman as chief, and, in 1930, hired three junior
cryptanalysts and two clerks.
The following year, a Japanese general suddenly occupied Manchuria
and set up a puppet Manchu emperor, and the government of the island
empire of Nippon fell into the hands of the militarists. Their avarice for
power, their desire to enrich their have-not nation, their hatred for white
Occidental civilization, started them on a decade-long march of conquest.
They withdrew from the League of Nations. They began beefing up the
Army. They denounced the naval disarmament treaties and began an
almost frantic ship-building race. Nor did they neglect, as part of their
war-making capital, their cryptographic assets. In 1934, their Navy
purchased a commercial German cipher machine called the Enigma; that
same year, the Foreign Office adopted it, and it evolved into the most
secret Japanese system of cryptography. A variety of other cryptosystems
supplemented it. The War, Navy, and Foreign ministries shared the
superenciphered numerical HATO code for intercommunication. Each
ministry also had its own hierarchy of codes. The Foreign Office, for
example, employed four main systems, each for a specific level of
security, as well as some additional miscellaneous ones.
Meanwhile, the modern-style shoguns speared into defenseless China,
sank the American gunboat Panay, raped Nanking, molested American

hospitals and missions in China, and raged at American embargoes on
oil and steel scrap. It became increasingly evident that Nippon's march of
aggression would eventually collide with American rectitude. The
mounting curve of tension was matched by the rising output of the
American cryptanalytic agencies. A trickle of MAGIC in 1936 had become a
stream in 1940. Credit for this belongs largely to Major General Joseph
O. Mauborgne, who became Chief Signal Officer in October, 1937.
Mauborgne had long been interested in cryptology. In 1914, as a
young first lieutenant, he achieved the first recorded solution of a cipher
known as the Playfair, then used by the British as their field cipher. He
described his technique in a 19-page pamphlet that was the first
publication on cryptology issued by the United States government. In
World War I, he put together several cryptographic elements to create the
only theoretically unbreakable cipher, and promoted the first automatic
cipher machine, with which the unbreakable cipher was associated.
When he became head of the Signal Corps, he immediately set about
augmenting the important cryptanalytic activities. He established the
S.I.S. as an independent division reporting directly to him, enlarged its
functions, set up branches, started correspondence courses, added
intercept facilities, increased its budget, and put on more men. In 1939,
when war broke out in Europe, S.I.S. was the first agency in the War
Department to receive more funds, personnel, and space. Perhaps most
important of all, Mauborgne's intense interest inspired his men to
outstanding accomplishments. More and more codes were broken, and
as the international situation stimulated an increasing flow of intercepts,
the MAGIC intelligence approached flood stage.
Mauborgne retired in September, 1941, leaving an expanded
organization running with smooth efficiency. By then the Japanese had
completed the basic outline for a dawn attack on Pearl Harbor. The plan
had been conceived in the fertile brain of Admiral Isoroku Yamamoto,
Commander-in-Chief Combined Fleet, Imperial Japanese Navy. Early in
the year, he had ordered a study of the operation, contending that "If we
have war with the United States, we will have no hope of winning unless
the United States fleet in Hawaiian waters can be destroyed." By May
1941, studies had shown the feasibility of a surprise air attack, statistics
had been gathered, and operational planning was under way.
In the middle of that month, the U.S. Navy took an important step in
the radio intelligence field. It detached a 43-year-old lieutenant
commander from his intelligence berth aboard U.S.S. Indianapolis and
assigned him to reorganize and strengthen the radio intelligence unit at
Pearl Harbor. The officer was Joseph John Rochefort, the only man in the
Navy with expertise in three closely related and urgently needed fields:
cryptanalysis, radio, and the Japanese language. Rochefort, who had
begun his career as an enlisted man, had headed the Navy's

cryptographic section from 1925 to 1927. Two years later, a married man
with a child, he was sent, because of his outstanding abilities, as a
language student to Japan, a hard post to which ordinarily only bachelor
officers were sent. This three-year tour was followed by half a year in
naval intelligence; most of the next eight years were spent at sea.
Finally, in June of 1941, Rochefort took over the command of what
was then known as the Radio Unit of the 14th Naval District in Hawaii.
To disguise its functions he renamed it the Combat Intelligence Unit. His
mission was to find out, through communications intelligence, as much
as possible about the dispositions and operations of the Japanese Navy.
To this end he was to cryptanalyze all minor and one of the two major
Japanese naval crypto-systems.
His chief target was the flag officers' system, the Japanese Navy's
most difficult and the one in which it encased its most secret
information. From about 1926 to the end of November, 1940, previous
editions had provided the U.S. Navy with much of its information on the
Japanese Navy. But the new version—a four-character code with a
transposition superencipherment—was stoutly resisting the best efforts
of the Navy's most skilled cryptanalysts, and Rochefort was urged to
concentrate on it. The other major system, the main fleet cryptographic
system, the most widely used, comprised a code with five digit codenumbers to which were added a key of other numbers to complicate the
system. The Navy called it the "five numeral system," or, more formally,
JN25b—the JN for "Japanese Navy," the 25 an identifying number, the b
for the second (and current) edition. Navy cryptanalytic units in
Washington and the Philippines were working on this code. Rochefort's
unit did not attack this but did attack the eight or ten lesser codes
dealing with personnel, engineering, administration, weather, fleet
exercises.
But cryptanalysis was only part of the unit's task. The great majority
of its 100 officers and men worked on two other aspects of radio
intelligence—direction-finding and traffic analysis.
Direction-finding locates radio transmitters. Since radio signals are
heard best when the receiver points at the transmitter, sensitive
antennas can find the direction from which a signal is coming by
swinging until they hear it at its loudest. If two direction-finders take
bearings like that on a signal and a control center draws the lines of
direction on a map, the point at which they cross marks the position of
the transmitter. Such a fix can tell quite precisely where, for example, a
ship is operating. Successive fixes can plot its course and speed.
To exploit this source of information, the Navy in 1937 established the
Mid-Pacific Strategic Direction-Finder Net. By 1941, high-frequency
direction-finders curved in a gigantic arc from Cavite in the Philippines

through Guam, Samoa, Midway, and Hawaii to Dutch Harbor, Alaska.
The 60 or 70 officers and men who staffed these outposts reported their
bearings to Hawaii, where Rochefort's unit translated them into fixes. For
example, on October 16, the ship with call-sign KUNA 1 was located at
10.7 degrees north latitude, 166.7 degrees east longitude—or within
Japan's mandated islands.
These findings did not serve merely to keep an eye on the day-to-day
locations of Japanese warships. They also formed the basis of the even
more fruitful technique of traffic analysis. Traffic analysis deduces the
lines of command of military or naval forces by ascertaining which radios
talk to which. And since military operations are usually accompanied by
an increase in communications, traffic analysis can infer the imminence
of such operations by watching the volume of traffic. When combined
with direction-finding, it can often approximate the where and when of a
planned movement.
Radio intelligence thus maintains a long-range, invisible, and
continuous surveillance of fleet movements and organization, providing a
wealth of information at a low cost. Of course it has its limitations. A
change of the call-signs of radio transmitters can hinder it. The sending
of fictitious messages can befuddle it. Radio silences can deafen it. But it
cannot be wholly prevented except by unacceptable restrictions on
communications. Hence the Navy relied increasingly on it for its
information on Japanese naval activities as security tightened in Japan
during 1941, and almost exclusively after July, when the President's
trade-freezing order deprived the Navy of all visual observations of
Japanese ships not on the China coast.
It was in July that a Japanese tactic set up a radio pattern that was
later to deceive the Combat Intelligence Unit. The Nipponese militarists
had decided to take advantage of France's defeat and occupy French
Indochina. The Naval preparations for the successful grab were clearly
indicated in the radio traffic, which went through the usual three stages
that preceded major Japanese operations. First appeared a heavy flurry
of messages. The Commander-in-Chief Combined Fleet busily originated
traffic, talking with many commands to the south, thereby indicating the
probable direction of his advance. Then came a realignment of forces. In
the lingo of the tranalysis people, certain chickens (fleet units) no longer
had their old mothers (fleet commanders). Call-sign NOTA 4, which
usually communicated with OYO 8, now talked mostly with ORU 6.
Accompanying this was a considerable confusion in the routing of
messages, with frequent retransmissions caused by the regrouping:
Admiral z not here; try Second Fleet. Then followed the third phase: radio
silence. The task force was now under way. Messages would be
addressed to it, but none would emanate from it.
During all this, however, not only were no messages heard from the

aircraft carriers, none were sent to them, either. This blank condition
exceeded radio silence, which suppresses traffic in only one direction—
from the mobile force—not in both. American intelligence reasoned that
the carriers were standing by in home waters as a covering force in case
of counterattack, and that communications both to and from them were
not heard because they were being sent out by short-range, low-powered
transmissions that died away before reaching American receivers. Such a
blank condition had obtained in a similar tactical situation in February.
American intelligence had drawn the same conclusions then and had
been proven right. Events soon confirmed the July assessment as well.
Twice, then, a complete blank of carrier communications combined with
indications of a strong southward thrust had meant the presence of the
carriers in Empire waters. But what happened in February and July was
not necessarily what would happen in December.
During the summer and fall of 1941, the pressure of events molded
America's two cryptanalytic agencies closer and closer to the form they
were to have on December 7. The Signal Intelligence Service, which had
181 officers, enlisted men, and civilians in Washington and 150 at
intercept stations in the field on Pearl Harbor Day, had been headed
since March by Lieutenant Colonel Rex W. Minckler, a career Signal
Corps officer. Friedman served as his chief technical assistant. S.I.S.
comprised the Signal Intelligence School, which trained Regular Army
and Reserve officers in cryptology, the 2nd Signal Service Company,
which staffed the intercept posts, and four Washington sections of the
S.I.S. proper: the A, or administrative, which also operated the tabulating
machinery; the B, or cryptanalytic; the c, or cryptographic, which
prepared new U.S. Army systems, studied the current systems for
security, and monitored Army traffic for security violations; and the D, or
laboratory, which concocted secret inks and tested suspected
documents.
The B section, under Major Harold S. Doud, a West Point graduate,
had as its mission the solution of the military and diplomatic systems
not only of Japan but of other countries. In this it apparently achieved at
least a fair success, though no Japanese military systems—the chief of
which was a code employing four-digit codenum-bers—were readable by
December 7 because of a paucity of material. Doud's technical assistant
was a civilian, Frank B. Rowlett, one of the three original junior
cryptanalysts hired in 1930. The military man in charge of Japanese
diplomatic solutions was Major Eric Svensson.
The Navy's official designation of OP-20-G indicated that the agency
was the G section of the 20th division of OPNAV, the Office of the Chief of
Naval Operations, the Navy's headquarters establishment. The 20th
division was the Office of Naval Communications, and the G section was

the Communication Security Section. This carefully chosen name
masked its cryptanalytic activities, though its duties did include U. S.
Navy cryptography.
Its chief was Commander Laurence F. Safford, 48, a tall, blond
Annapolis graduate who was the Navy's chief expert in cryptology. In
January, 1924, he had become the officer in charge of the newly created
research desk in the Navy's Code and Signal Section. Here he founded
the Navy's communication-intelligence organization. After sea duty from
1926 to 1929, he returned to cryptologic activities for three more years,
when sea duty was again made necessary by the "Manchu" laws, which
required officers of the Army and Navy to serve in the field or at sea to
win promotion. He took command of OP-20-G in 1936. One of his
principal accomplishments before the outbreak of war was the
establishment of the Mid-Pacific Strategic Direction-Finder Net and of a
similar net for the Atlantic, where it was to play a role of immense
importance in the Battle of the Atlantic against the U-boats.
Safford's organization enjoyed broad cryptologic functions. It printed
new editions of codes and ciphers and distributed them, and contracted
with manufacturers for cipher machines. It developed new systems for
the Navy. It comprehended such subsections as GI, which wrote reports
based on radio intelligence from the field units, and GL, a record-keeping
and historical-research group. But its main interest centered on
cryptanalysis.
This activity was distributed among units in Washington, Hawaii, and
the Philippines. Only Washington attacked foreign diplomatic systems
and naval codes used in the Atlantic theater (primarily German).
Rochefort had primary responsibility for the Japanese naval systems.
The Philippines chipped away at JN25 and did some diplomatic
deciphering, with keys provided by Washington. That unit, which like
Rochefort's was attached for administrative purposes to the local naval
district (the 16th), was installed in a tunnel of the island fortress of
Corregidor. It was equipped with 26 radio receivers, apparatus for
intercepting both high- and low-speed transmissions, a directionfinder,
and tabulating machinery. Lieutenant Rudolph J. Fabian, 33, an
Annapolis graduate who had had three years of radio intelligence
experience in Washington and the Philippines, commanded. The 7
officers and 19 men in his cryptanalytic group exchanged possible
recoveries of JN25b codegroups with Washington and with a British
group in Singapore; each group also had a liaison man with the other.
Of the Navy's total radio-intelligence establishment of about 700
officers and men, two thirds were engaged in intercept or directionfinding activities and one third— including most of the 80 officers—in
cryptanalysis and translation. Safford sized up the personnel of his three
units this way: Pearl Harbor had some of the best officers, most of whom

had four or five years of radio intelligence experience; the crew at
Corregidor, which in general had only two or three years' experience, was
"young, enthusiastic, and capable"; Washington—responsible for both
overall supervision and training—had some of the most experienced
personnel, with more than ten years' experience, and many of the least:
90 per cent of the unit had less than a year's experience.
Under Safford in the three subsections most closely involved with
cryptanalysis were Lieutenant Commanders George W. Welker of GX, the
intercept and direction-finding subsection, Lee W. Parke of GY, the
cryptanalytical subsection, and Kramer of GZ, the translation and
dissemination subsection. GY attacked new systems and recovered new
keys for solved systems, such as PURPLE. But while it made the initial
breaks in code solutions, the detailed recovery of codegroups (which was
primarily a linguistic problem as compared to the more mathematical
cipher solutions) was left to GZ. Four officers in GY, assisted by chief petty
officers, stood round-the-clock watches. Senior watch officer was
Lieutenant (j.g.) George W. Lynn; the others were Lieutenants (j.g.)
Brotherhood, Pering, and Allan A. Murray. GY had others on its staff,
such as girl typists who also did the simple deciphering of some
diplomatic messages after the watch officers and other cryptanalysts had
found the keys.
Kramer was in an odd position. Though he worked in OP-20-GZ, he
was formally attached to OP-16-F2—the Far Eastern Section of the Office
of Naval Intelligence. This arrangement was intended in part to throw off
the Japanese, who might have inferred some measure of success in
codebreaking if a Japanese-language officer like Kramer were assigned to
communications, in part to have an officer with a broad intelligence
background distribute MAGIC so that he could answer the recipients'
questions. Kramer, 38, who had studied in Japan from 1931 to 1934,
had had two tours in O.N.I, proper before being assigned full time to GZ
in June, 1940. An Annapolis graduate, chess fan, and rifle marksman,
he lived in a world in which everything had one right way to be done. He
chose his words with almost finicky exactness (one of his favorites was
"precise"); he kept his pencil mustache trimmed to a hair; he filed his
papers tidily; he often studied his MAGIC intercepts several times over
before delivering them. Included in this philosophy was his duty. He
performed it with great responsibility, intelligence, and dedication.
The first task of OP-20-G and of S.I.S. was to obtain intercepts. And in
peacetime America that was not easy.
Section 605 of the Federal Communications Act of 1934, which
prohibits wiretaps, also prohibits the interception of messages between
foreign countries and the United States and territories. General Malin

Craig, Chief of Staff from 1937 to 1939, was acutely aware of this, and
his attitude dampened efforts to intercept the Japanese diplomatic
messages coming into America. But after General George C. Marshall
succeeded to Craig's post, the exigencies of national defense relegated
that problem in his mind to the status of a legalistic quibble. The cryptanalytic agencies pressed ahead in their intercept programs. The extreme
secrecy in which they were cloaked helped them avoid detection. They
concentrated on radio messages, since the cable companies, fully
cognizant of the legal restrictions, in general refused to turn over any
foreign communications to them. Consequently, 95 per cent of the
intercepts were radio messages. The remainder was split between cable
intercepts and photographs of messages on file at a few cooperative cable
offices.
To pluck the messages from the airwaves, the Navy relied mainly on
its listening posts at Bainbridge Island in Puget Sound; Winter Harbor,
Maine; Cheltenham, Maryland; Heeia, Oahu; and Corregidor and to a
lesser degree on stations at Guam; Imperial Beach, California;
Amagansett, Long Island and Jupiter, Florida. Each station was assigned
certain frequencies to cover. Bainbridge Island, which was called Station
S, copied solid the schedule of Japanese government messages between
Tokyo and San Francisco. Its two sound recorders guarded the
radiotelephone band of that circuit; presumably it was equipped to
unscramble the relatively simple sound inversion that then provided
privacy from casual eavesdropping. Diplomatic messages were
transmitted almost exclusively by commercial radio using roman letters.
The naval radiograms, however, employed the special Morse code devised
for kata kana, a syllabic script of Japanese. The Navy picked these up
with operators trained in Japanese Morse and recorded them on a
special typewriter that it had developed for the roman-letter equivalents
of the kana characters. The Army's stations, called Monitor Posts, were:
No. 1, Fort Hancock, New Jersey; No. 2, San Francisco; No. 3, Fort Sam
Houston, San Antonio; No. 4, Panama; No. 5, Fort Shafter, Honolulu; No.
6, Fort Mills, Manila; No. 7, Fort Hunt, Virginia; No. 9, Rio de Janeiro.
At first both services airmailed messages from their intercept posts to
Washington. But this proved too slow. The Pan-American Clipper, which
carried Army intercepts from Hawaii to the mainland, departed only once
a week on the average, and weather sometimes caused cancellations,
forcing messages to be sent by ship. As late as the week before Pearl
Harbor, two Army intercepts from Rio did not reach Washington for
eleven days. Such delays compelled the Navy to install teletypewriter
service in 1941 between Washington and its intercept stations in the
continental U.S. The station would perforate a batch of intercepts onto a
teleptype tape, connect with Washington through a teletypewriter
exchange, and run the tape through mechanically at 60 words per
minute, cutting toll charges to one third the cost of manually sending

each message individually. Outlying stations of both the Army and Navy
picked out Japanese messages bearing certain indicators, enciphered the
Japanese cryptograms in an American system, and radioed them to
Washington. The reencipherment was to keep the Japanese from
knowing of the extensive American cryptanalytic effort. Only the three
top Japanese systems were involved in this expensive radio
retransmission: PURPLE, RED (a machine system that antedated PURPLE,
which had supplanted it at major embassies, but that was still in use for
legations such as Vladivostok), and the J series of enciphered codes. The
Army did not install a teletype for intercepts from its continental posts
until the afternoon of December 6, 1941; the first messages (from San
Francisco) were received in the early morning hours of December 7.
The intercept services missed little. Of the 227 messages pertaining to
Japanese-American negotiations sent between Tokyo and Washington
from March to December, 1941, all but four were picked up.
In Honolulu, where a large Japanese population produced nightmares
of antlike espionage and potential sabotage, the 14th Naval District's
intelligence officer, Captain Irving S. Mayfield, had long sought to obtain
copies of the cablegrams of Consul General Nagao Kita. If Rochefort's
unit could solve these, Mayfield figured, he might know better which
Japanese to shadow and what information they sought.
His intuitions were sound. On March 27, 1941, not two weeks after
Mayfield himself took up his duties, a young ensign of the Imperial
Japanese Navy, 25-year-old Takeo Yoshikawa, who had steeped himself
in information about the American Navy, arrived in Honolulu to serve as
Japan's only military espionage agent covering Pearl Harbor. Under the
cover-name "Tadasi Morimura," he was assigned to the consulate as a
secretary. He promptly made himself obnoxious—and drew suspicion
upon himself within the consulate staff—by coming to work late or not at
all, getting drunk frequently, having women in his quarters overnight,
and even insulting the consul himself on occasion. But he managed to
tour the islands, and within a month was sending such messages as:
"Warships observed at anchor on the llth [of May, 1941] in Pearl Harbor
were as follows: Battleships, 11: Colorado, West Virginia, California,
Tennessee. . . ." These were sent in the consulate's diplomatic systems,
not in naval code.
But Mayfield's hopes of peering into these secret activities through the
window of a broken code were stymied by the refusal of the cable offices
to violate the statute against interception. So when David Sarnoff,
president of the Radio Corporation of America, vacationed in Hawaii,
Mayfield spoke to him. It was subsequently arranged that thenceforth
R.C.A.'s Japanese consulate messages would be quietly given to the
naval authorities. But the consulate rotated its business among the
several cable companies in Honolulu, and R.C.A.'s turn was not due until

December 1.
In Washington, however, intercepts overwhelmed GY and S.I.S. The
tiny staff of cryptanalysts simply could not cope with all of them
expeditiously. This difficulty was resolved in two ways.
One was to cut out duplication of effort. At first, both services solved
all their Japanese diplomatic intercepts. But beginning more than a year
before Pearl Harbor, messages originating in Tokyo on odd-numbered
days of the month were handled by the Navy, those on even days, by the
Army. Each began breaking the messages sent in from its own intercept
stations until it reached the Tokyo date of origin; it would then retain
them or send them over as the dates indicated. The cryptanalysts utilized
the extra time to attack as-yet-unbroken systems and to clean up
backlogs.
The other method was to concentrate on the important intercepts and
let the others slide, at least until the important ones were completed. But
how can a cryptanalyst tell which messages are important until he has
solved them? He cannot, but he can assume that messages sent in the
more secret systems are the more important. All dispatches cannot be
transmitted in a single system because the huge volume of traffic would
enable cryptanalysts to break it too quickly. Hence most nations set up a
hierarchy of systems, reserving the top ones for their vital needs.
Japan was no exception. Though her Foreign Office employed an
almost bewildering variety of different codes, resorting, from time to time,
to the Yokohama Specie Bank's private code, a Chinese ideographic code
list, and codes bearing kata kana names, such as TA, JI, or HEN, it relied
in the main on four systems. American cryptanalysts ranked these on
four levels according to the inherent difficulty of their solution and the
messages that they generally carried. Intercepts were then solved in the
order of this priority schedule.
Simplest of all, and hence the lowest in rank and last to be read
(excluding plain language), was the LA code, so called from the indicator
group LA that preceded its codetexts. LA did little more than put kata
kana into roman letters for telegraphic transmission and to secure some
abbreviation for cable economy. Thus the kana for ki was replaced by the
code form CI, the kana for to by IF, the two-kana combination of ka + n by
CE. Its two-letter codewords, all of either vowel-consonant or consonantvowel form and including such as ZO for 4, were supplemented by a list
of four-letter codewords, such as TUVE for dollars, SISA for ryoji ("consul"),
and XYGY for Yokohama. A very typical LA message is serial 01250 from
the Foreign Minister to Kita, dated December 4, which begins in
translation: "The following has been authorized as the year-end bonus for
employee typists of your office." This sort of code is generally called a

"passport code" because it usually serves for messages covering the
administrative routine of a mission, such as issuance of passports and
visas. LA was a particularly simple one to solve, partly because it had
been in effect since 1925, partly because of the regularities in its
construction. For example, all kana that ended in e had as code
equivalents groups beginning with A (ke = AC, se = AD), and all that began
with k had code equivalents beginning or ending with C. Identification of
one kana would thus suggest the identification of others.
One rung up the cryptographic ladder was the system known to the
Japanese as Oite and to American code-breakers as PA-K2. The PA part
was a two- and four-letter code similar to the LA, though much more
extensive and with codegroups disarranged. The K2 part was a
transposition based on a keynumber. The letters from the PA encoding
were written under this keynumber from right to left and then copied out
in mixed order, taking first the letter under number 1, then the letter
under number 2, until the row was completed. The process was repeated
for successive rows.
For example, on December 4 Yoshikawa wired the Foreign Minister
that "At 1 o'clock on the 4th a light cruiser of the Honolulu class hastily
departed—Morimura." In romaji (the roman-letter version of the kata
kana) this became 4th gogo 1 kei jun (honoruru) kata hyaku shutsu ko—
morimura. In PA, with the parentheses getting their own codegroups (OQ
and UQ), it assumed this form: BYDH DOST JE YO IA OQ GU RA HY HY UQ VI LA YJ
AY EC TY FI BANL, with FI indicating use four-letter code. (The code clerk
made two errors. After encoding kata by VI, he encoded an extra ta into
LA and an unnecessary re into TY.) This was then written under the
keynumber from right to left, with an extra letter I as a null to complete
the final five-letter group:
10 15 11 16 2 8 1 5 17 3 7 13 19 4 18 6 12 9 14
B

Y

D

H D

O S T

J E Y O

I A

O Q

G U

R

A

H

Y

H Y

U Q V

I L A Y

J A

Y E

G T

Y

F

I B

A N

L

I

Transcribed line by line according to the numbers (s under 1 first, D
under 2 second, etc.), prefixed with system indicator GIGIG and key
indicator AUDOB, the message number, and the telegraphic abbreviation
of Sikuyu ("urgent"), the message (with three more errors: the Y under 13
became the J in CJYHH, the F under 2 became the E in IYJIE, and the T
under 9 became the i in AUIAY) became the one actually sent over Kita's
name:
GAIMUDAIJIN TOKIO
SIKYU 02500 GIGIG AUDOB SDEAT QYOUB DGORY HJOIQ YLAVE

AUIAY CJYHH IYJIE ALBIN
KITA
PA-K2 did not pose much of a problem to experienced American
cryptanalysts. ROchefort estimated that his unit could crack a PA-K2
message in from six hours to six days, with three days a good average.
The transposition was vulnerable because each line was shuffled
identically; the cryptanalyst could slice a cryptogram into groups of 15 or
17 or 19 and anagram these simultaneously until the predominant
vowel-consonant alternation appeared on all lines; the underlying code
could then be solved by assuming that the most frequent codegroups
represented the most frequent kana (i, followed by ma, shi, o, etc.) and
filling out the skeleton words that resulted. Since the system had
remained in use for several years, this reconstruction had long been
accomplished by the Washington agencies. Hence solution involved only
unraveling any new transposition and, with luck, might take only a few
hours. It could also take a few days. Primarily because of PA-K2's
deferred position in the priority list, an average of two to four days
elapsed between interception and translation.
The code clerk in Honolulu enveloped Yoshikawa's final messages in
PA-K2 only because higher-level codes had been destroyed December 2
on orders from Tokyo. Normally, espionage reports of shipping
movements and military activities, sent routinely by Japanese consuls
from their posts all over the world, were framed on that next level of
secrecy. Here prevailed a succession of codes called TSU by the Japanese
and the J series by Americans. These were even more extensive and more
thoroughly disarranged than PA, and they were transposed by a system of
far greater complexity than the rather simple and vulnerable K2.
Furthermore, the code and the transposition were changed at frequent
intervals. Thus J17-K6 was replaced on March 1 by J18-K8, and that in
turn by J19-K9 on August 1.
The transposition was the real stumbling block. Like the K2, it used a
keynumber, but it differed in being copied off vertically instead of
horizontally, and in having a pattern of holes in the transposition blocks.
These holes were left blank when the code groups are inscribed into the
block. For example, letting the alphabet from A to Y serve as the code
message:
[CodeBreakers 020.jpg]
The letters were transcribed in columns in the order of the
keynumbers, skipping over the blanks: BJMV EHKT NW CGORX AFILQU DPSY.

This would be sent in the usual five-letter groups.
The first step in solving a columnar transposition like this, but
without blanks, is to cut the cryptogram into the approximately equal
segments that the cryptanalyst believes represent the columns of the
original block. The blanks vastly increase the difficulty of this essential
first step because they vary the length of the column segments. The
second step is to reconstruct the block by trying one segment next to the
other until a codeword-like pattern appears. Here again the blanks, by
introducing gaps in unknown places between the letters of the segments,
greatly hinder the cryptanalyst.
The problems of solving such a system are illustrated by the fact that
J18-K8 was not broken until more than a month after its introduction.
The cryptanalysts had to make a fresh analysis for each pattern of
blanks and each transposition key. The key changed daily, the blankpattern three times a month. Hence J19-K9 solutions were frequently
delayed. The key and pattern for November 18 were not recovered until
December 3; those for November 28, not until December 7. On the other
hand, solution was sometimes effected within a day or two. Success
usually depended on the quantity of intercepts in a given key. About 10
or 15 per cent of J19-K9 keys were never solved.
This situation contrasts with that of PURPLE, the most secret Japanese
system, in which all but 2 or 3 per cent of keys were recovered and in
which most messages were solved within hours. Did the Japanese err in
assessing the security of their systems? Yes and no. PURPLE was easier to
keep up with once it was solved, but it was a much more difficult system
to break in the first place than J19-K9. The solution of the PURPLE
machine was, in fact, the greatest feat of cryptanalysis the world had yet
known.
The cipher machine that Americans knew as PURPLE bore the
resounding official Japanese title of 97-shiki O-bun In-ji-ki. This meant
Alphabetical Typewriter '97, the '97 an abbreviation for the year 2597 of
the Japanese calendar, which corresponds to 1937. The Japanese
usually referred to it simply as "the machine" or as "J,"1 the name given
it by the Imperial Japanese Navy, which had adapted it from the German
Enigma cipher machine and then had lent it to the Foreign Ministry,
which, in turn, had further modified it. Its operating parts were housed
in a drawer-sized box between two big black electrically operated
Underwood typewriters, which were connected to it by 26 wires plugged
into a row of sockets called a plugboard. To encipher a message, the
cipher clerk would consult the thick YU GO book of machine keys, plug in
the wire connections according to the key for the day, turn the four disks
in the box so the numbers on their edges were those directed by the YU

GO, and type out the plaintext. His machine would record that plaintext

while the other, getting the electric impulses after the coding box had
twisted them through devious paths, would print out the cipher-text.
Deciphering was the same, though the machine irritatingly printed the
plaintext in the five-letter groups of the ciphertext input.
The Alphabetical Typewriter worked on roman letters, not kata kana.
Hence it could encipher English as well as romaji—and also roman-letter
codetexts, like those of the J codes. Since the machine could not
encipher numerals or punctuation, the code clerk first transformed them
into three-letter codewords, given in a small code list, and enciphered
these. The receiving clerk would restore the punctuation, paragraphing,
and so on, when typing up a finished copy of the decode.
The coding wheels and plugboards produced a cipher of great
difficulty. The more a cipher deviates from the simple form in which one
ciphertext letter invariably replaces the same plaintext letter, the harder
it is to break. A cipher might replace a given plaintext letter by five
different ciphertext letters in rotation, for example. But the Alphabetical
Typewriter produced a substitution series hundreds of thousands of
letters long. Its coding wheels, stepping a space—or two, or three, or
four—after every letter or so, did not return to their original positions to
re-create the same series of paths, and hence the same sequence of
substitutes, until hundreds of thousands of letters had been enciphered.
The task of the cryptanalysts consisted primarily of reconstructing the
wiring and switches of the coding wheels—a task made more
burdensome by the daily change of plugboard connections. Once this
was done, the cryptanalyst still had to determine the starting position at
the coding wheels for each day's messages. But this was a comparatively
simple secondary job.
American cryptanalysts knew none of these details when the
Japanese Foreign Office installed the Alphabetical Typewriter in its major
embassies in the late 1930s. How, then, did they solve it? Where did they
begin? How did they even know that a new machine was in service, since
the Japanese government did not announce it?
The PURPLE machine supplanted the RED machine,2 which American
cryptanalysts had solved, and so probably their first clue to the new
machine was the disconcerting discovery that they could no longer read
the important Japanese messages. At the same time, they observed new
indicators for the PURPLE system. Clues to the system's nature came from
such characteristics of its ciphertext as the frequency of letters, the
percentage of blanks (letters that did not appear in a given message), and
the nature and number of repetitions. Perhaps the codebreakers also
assumed that the new machine comprised essentially a more
complicated and improved version of the one it replaced. In this they
were right.

Their first essays at breaking into the cipher both accompanied and
supplemented their attempts to determine the type of cipher. Their
previous success with the RED machine and with the lesser systems had
given them insight into the Japanese diplomatic forms of address,
favorite phrases, and style (paragraphs were often numbered, for
example). These provided the cryptanalysts with probable words—words
likely to be in the plaintext— that would help in breaking the cipher.
Opening and closing formulas, such as "I have the honor to inform Your
Excellency" and "Re your telegram," constituted virtual cribs. Newspaper
stories suggested the subject matter of intercepts. The State Department
sometimes made public the full texts of diplomatic notes from Japan to
the American government, in effect handing the cryptanalysts the
plaintext (or its translation) of an entire dispatch. (State reportedly did
not pass the texts of confidential notes to the cryptanalysts, though this
would have helped them considerably and was done by other foreign
ministries.) Japan's Foreign Office often had to circulate the same text to
several embassies, not all of which had a PURPLE machine, and a code
clerk might have inadvertently encoded some cables in PURPLE, some in
other systems— which the cryptanalysts could read. A comparison of
times of dispatch and length, and voilá!—another crib to a cryptogram.
Errors were, as always, a fruitful source of clues. As late as November,
1941, the Manila legation repeated a telegram "because of a mistake on
the plugboard." How much more common must errors have been when
the code clerks were just learning to handle the machine! The sending of
the identical text in two different keys produces "isomorphic"
cryptograms that yield exceedingly valuable information on the
composition of the cipher.
The cryptanalysts of S.I.S. and OP-20-G, then, matched these
assumed plaintexts to their ciphertexts and looked for regularities from
which they could derive a pattern of encipherment. This kind of work,
particularly in the early stages of a difficult cryptanalysis, is perhaps the
most excruciating, exasperating, agonizing mental process known to
man. Hour after hour, day after day, sometimes month after month, the
cryptanalyst tortures his brain to find some relationship between the
letters that hangs together, does not dead-end in self-contradiction, and
leads to additional valid results.
The codebreakers attacking the new Japanese mechanism went just
so far—and for months could not push on further. As William Friedman
recalled, "When the PURPLE system was first introduced it presented an
extremely difficult problem on which the Chief Signal Officer [Mauborgne]
asked us to direct our best efforts. After work by my associates when we
were making very slow progress, the Chief Signal Officer asked me
personally to take a hand. I had been engaged largely in administrative
duties up to that time, so at his request I dropped everything else that I
could and began to work with the group."

Lighting his way with some of the methods that he himself had
developed, he led the cryptanalysts through the murky PURPLE
shadowland. He assigned teams to test various hypotheses. Some
prospected fruitlessly, their only result a demonstration that success lay
in another direction. Others found bits and pieces that seemed to make
sense. (OP-20-G cooperated in this work, with Harry L. Clark making
especially valuable contributions, but S.I.S. did most of it.) Friedman and
the other codebreakers began to segregate the ciphertext letters into
cycles representing the rotation of the coding wheels—gingerly at first,
then faster and faster as the evidence accumulated. The polyalphabetic
class of ciphers, to which PURPLE belonged, is based ultimately upon an
alphabet table, usually 26 letters by 26. To reconstruct the PURPLE tables,
the cryptanalysts employed both direct and indirect symmetry of
position— names only slightly less forbidden than the methods they
denote. Errors, caused perhaps by garbled interceptions or simple
mistakes in the cryptanalysis, jarred these delicate analyses and delayed
the work. But slowly it progressed. A cryptanalyst, brooding sphinxlike
over the cross-ruled paper on his desk, would glimpse the skeleton of a
pattern in a few scattered letters; he tried fitting a fragment from another
recovery into it; he tested the new values that resulted and found that
they produced acceptable plaintext; he incorporated his essay into the
over-all solution and pressed on. Experts in Japanese filled in missing
letters; mathematicians tied in one cycle with another and both to the
tables. Every weapon of cryptanalytic science—which in the stratospheric
realm of this solution drew heavily upon mathematics, using group
theory, congruences, Poisson distributions—was thrown into the fray.
Eventually the solution reached the point where the cryptanalysts had
a pretty good pencil-and-paper analog of the PURPLE machine. S.I.S. then
constructed a mechanism that would do automatically what the
cryptanalysts could do manually with their tables and cycles. They
assembled it out of ordinary hardware and easily available pieces of
communication equipment, such as the selector switches used for
telephones. It was hardly a beautiful piece of machinery, and when not
running just right it spewed sparks and made loud whirring noises.
Though the Americans never saw the 97-shiki O-bun In-ji-ki, their
contraption bore a surprising physical resemblance to it, and of course
exactly duplicated it cryptographically.
S.I.S. handed in its first complete PURPLE solution in August of 1940,
after 18 or 20 months of the most intensive analysis. In looking back on
the effort that culminated in this, the outstanding cryptanalytic success
in the whole history of secret writing up to its time, Friedman would say
generously:
Naturally this was a collaborative, cooperative effort on the part

of all the people concerned. No one person is responsible for the
solution, nor is there any single person to whom the major share of
credit should go. As I say, it was a team, and it was only by very
closely coordinated teamwork that we were able to solve it, which
we did. It represents an achievement of the Army cryptanalytic
bureau that, so far as I know, has not been duplicated elsewhere,
because we definitely know that the British cryptanalytic service
and the German cryptanalytic service were baffled in their
attempts and they never did solve it.
Friedman, was, despite his partial disclaimer, the captain of that
team. The solution had taken a terrific toll. The restless turning of the
mind tormented by a puzzle, the preoccupation at meals, the insomnia,
the sudden wakening at midnight, the pressure to succeed because
failure could have national consequences, the despair of the long weeks
when the problem seemed insoluble, the repeated dashings of uplifted
hopes, the mental shocks, the tension and the frustration and the
urgency and the secrecy all converged and hammered furiously upon his
skull. He collapsed in December. After three and a half months in Walter
Reed General Hospital recovering from the nervous breakdown, he
returned to S.I.S. on shortened hours, working at first in the more
relaxed area of cryptosecurity. By the time of Pearl Harbor he was again
able to do some cryptanalysis, this time of German systems.
OP-20-G contributed importantly to the ease and speed of daily PURPLE
solutions when 27-year-old Lieutenant (j.g.) Francis A. Raven discovered
the key to the keys. After a number of PURPLE messages has been solved,
Raven observed that the daily keys within each of the three ten-day
periods of a month appeared to be related. He soon found that the
Japanese simply shuffled the first day's key to form the keys for the next
nine days, and that the nine shuffling patterns were the same in all the
ten-day periods. Raven's discovery enabled the cryptanalysts to predict
the keys for nine out of ten days. The cryptanalysts still had to solve for
the first day's key by straightforward analysis, but this task and its
delays were eliminated for the rest of the period. Furthermore, knowledge
of the shuffles enabled the codebreakers to read all the traffic of a period
even though they could solve only one of the daily keys.
This fine piece of work, on the shoulders of the tremendous initial
Friedman-S.I.S. effort, resulted in the paradoxical situation of Americans
reading the most difficult Japanese diplomatic system more quickly and
easily than some lower-grade systems. They also became very facile in
reading two-step systems in which PURPLE superenciphered an already
coded message. The Japanese did this from time to time to provide extra
security, usually with the CA code, the personal code of an ambassador or
head of mission. A year after S.I.S. handed in its first PURPLE solution, the

cryptanalysts solved a message enciphered in "the highest type of secret
classification used by the Japanese Foreign Office." The message was
first enciphered in CA; this was then juggled according to the K9
transposition (normally used with the J19 code), and the transposed
codetext was then enciphered on the PURPLE machine. The solution,
which on the basis of the number of combinations involved might have
been expected to take geologic eons, was completed in just four days.
The intercepts ordinarily needed to be translated, and translation was
the bottleneck of the MAGIC production line. Interpreters of Japanese were
even scarcer than expert cryptanalysts. Security precluded employing
Nisei or any but the most trustworthy Americans. Through prodigious
efforts in 1941 the Navy doubled its GZ translation staff —to six. These
included three whom Kramer called "the most highly skilled Occidentals
in the Japanese language in the world."
But ability in standard Japanese alone did not suffice. Each
translator had to have at least a year's experience in telegraphic
Japanese as well before he could be trusted to come through with the
correct interpretation of a dispatch. This is because telegraphic Japanese
is virtually a language within a language, and, as McCollum, himself a
Japanese-language officer, explained, "the so-called translator in this
type of stuff almost has to be a cryptographer himself. You understand
that these things come out in the form of syllables, and it is how you
group your syllables that you make your words. There is no punctuation.
"Now, without the Chinese ideograph to read from, it is most difficult
to group these things together. That is, any two sounds grouped together
to make a word may mean a variety of things. For instance, 'ba' may
mean horses or fields, old women, or my hand, all depending on the
ideographs with which it is

[...正文过长，此处由批处理脚本仅做上下文截断；请在结论中说明该限制...]

t names, they say "B as in baby, not v as in Victor." For
the greater the redundancy, the easier it becomes to detect mistakes. If a
language consisted only of alternations of consonants and vowels, any
deviation from that pattern would flag an error.
This detection of errors is the first step toward their correction. And in
this correction redundancy again plays the central role. After the
recipient of "endividual" has hunted through his memory and his
dictionary and found that it does not exist in English, he brings up the
sequence "individual," which does exist, from his store of prior
information about English, and corrects his message. If the reader of a
business letter sees the sequence "rhe company," he will recognize "rhe"
as a nonword, will remember that the rules of English often call for a
similar-appearing group of letters, "the," before a noun like "company,"
will perhaps consider that r is near t on the typewriter keyboard, and
then will conclude that "rhe" should be "the."
This process is a first cousin to cryptanalysis.
For cryptanalysts bring to bear in their solutions the same prior
knowledge of rules and spelling and phonetic preferences (that is,
redundancy) that the ordinary reader does to correct a typographical
error. What laymen do with accidental errors, cryptanalysts do with
deliberate deformations. Of course a cryptogram is immensely more
involved and obscure than an isolated misprint, but it has an underlying
regularity that the single random error does not, and

this structure assists and confirms the successive "corrections" that
constitute a cryptanalysis.
But how does the cryptanalyst begin in the first place? In correcting a
typographical error, all the redundant elements lie in plain view, ready
for use. With a cryptogram, they are obscured. The cryptanalyst begins
by breaking these elements down to their atomic form—letters. He then
compares them to the redundant elements of a language that have been
reduced to the same common denominator. In order words, he takes a
frequency count of the letters of the cryptogram and matches it against a
frequency count of the letters of the assumed plaintext language. (These
counts must sometimes be modified by the conditions of the cipher. In
polyalphabetics, a count must be made for each alphabet; in digraphics,
the count must be of pairs. If the cryptogram is in code, the atomic forms
are words, but the same principle applies.)
Having done this, how can the cryptanalyst be confident that the
cryptogram's plaintext will have approximately the same frequencies as
those of plaintext in general? Why won't the differences in subjects of
discussion, in vocabulary, in expression, upset the frequencies? Because
the redundant elements of language far outweigh the variable ones. The
75 per cent redundancy in English overwhelms the 25 per cent of "free
will"—though this 25 per cent does keep frequency counts from matching
one another exactly. The redundant elements in any text converge to
make its frequency table. The need in any English text to use "the"
frequently ensures that h will be a high-frequency letter. English's
preference for alveolar consonants will make n, t, r, s, d, and / all highor medium-frequency letters. The language's aversion to p and k keeps
their frequencies low. These redundant elements are fixed and
predetermined—necessarily so, if communication is to take place—and
hence they stabilize the frequency tables that reflect them.
Shannon's insight, his great contribution to cryptology, lay in pointing
out that redundancy furnishes the ground for cryptanalysis. "In . . . the
majority of ciphers," he wrote, "it is only the existence of redundancy
in.the original messages that makes a solution possible." This is the very
basis of codebreaking. Shannon has here given an explanation for the
constancy of letter frequency, and hence for the phenomena that depend
on it, such as cryptanalysis. He has thus made possible, for the first time, a fundamental
understanding of the process of cryptogram solution.
From this insight flow several corollaries. It follows that the lower the
redundancy, the more difficult it is to solve a cryptogram. Shannon's own
two extremes of redundancy illustrate this. The last few words of
Finnegans Wake are these: "End here. Us then. Finn, against! Take.
Bussoftlee, mememormee! Till thousendsthee. Lps. The keys to. Given! A
way a lone a last a loved a long the." This would interpose distinctly more
difficulties to a cryptanalyst than a portion of the New Testament in
Basic English: "And the disciples were full of wonder at his words. But
Jesus said to them again, Children, how hard it is for those who put faith
in wealth to come into the kingdom of God!"
The problem of low redundancy arises in practice with a vengeance
when the cryptanalyst is faced with enciphered code. To strip the
encipherment from encicode, the cryptanalyst must solve a cryptogram
whose plaintext consists of codewords and which may look like
KKDYWUKJTPLKJE. . . . This is of very low redundancy because of the more
even use of letters, the greater freedom in combining them, the
suppression of frequencies by the use of homophones, and so on. But the
unavoidable repetitions of orders and reports, the pressure of the
redundancy of the language pent within the vessel of the code, and the
engineering of codewords so that garbles can be corrected—all these give
the underlying codetext a fibrous enough texture for the cryptanalyst to
grasp it for solution.
These considerations suggest that reducing the redundancy will
hinder cryptanalysis. Shannon himself prescribes operating on the
plaintext "with a transducer which removes all redundancies. . . . The
fact that the vowels in a passage can be omitted without essential loss
suggests a simple way of greatly improving almost any ciphering system.
First delete all vowels, or as much of the message as possible without
running the risk of multiple reconstructions, and then encipher the
residue." Experts who have attacked cryptograms from whose plaintexts
only the letter e has been eliminated have found that the difficulty of
solution increased noticeably. Reducing redundancy is especially
effective because it robs the cryptanalyst of one of his chief tools for
attack instead of just bolstering the wall of secrecy. Cryptographers of
the Italian Renaissance

did this when they ordered cipher clerks to drop the second letter of a
doublet, as the second / in sigillo.
Such techniques rely upon the cipher clerks' knowledge of their
language to supply the suppressed elements of redundancy.
Abbreviations likewise may have such low redundancy, may require such
an extensive furnishing of information, as bn for battalion, that they may
not only make plaintexts harder to solve, but may themselves function as
a rough form of cryptography. Two gossips, for example, may refer to a
third party by her initials. They hope that no one within hearing will have
sufficient knowledge of the contextual situation to restore the eliminated
portion of the name. Much of the Masonic ritual is printed in that form:
"Do u declr, upn ur honr, tt u r promptd to. . . ."
Another corollary is that more text is needed to solve a lowredundancy cryptogram than one with a high-redundancy plaintext.
Shannon has managed to quantify the amount of material needed to
achieve a unique and unambiguous solution when the plaintext has a
known degree of redundancy. He calls the number of letters the "unicity
distance" (or "unicity point"), and he calculates it by means of a rather
complicated formula. This formula naturally differs for different ciphers,
but it always includes the redundancy as one of its terms. In his original
paper, in which he considered the redundancy of English at only 50 per
cent, Shannon found the unicity point for monoalphabetic substitution
at 27 letters, for polyalphabetics with known alphabets at twice the
period length, for those with unknown alphabets at 53 times the period
length, for transposition at the keylength times the logarithm of the
keylength factorial.
Shannon has also viewed cryptology from a couple of other
perspectives, which, while not as useful as information theory, are
enlightening. The first, in fact, is a kind of corollary to the informationtheory view.
"From the point of view of the cryptanalyst," Shannon wrote, "a
secrecy system is almost identical with a noisy communication system."
In information theory, the term "noise" has a special meaning. Noise is
any unpredictable disturbance that creates transmission errors in any
channel of communication. Examples are static on the radio, "snow" on a
television screen, misprints, background

chatter at a cocktail party, fog, a bad connection on the telephone, a
foreign accent, perhaps even mental preconceptions. Shannon is
suggesting that noise is analogous to encipherment. "The chief
differences in the two cases," he wrote, "are: first, that the operation of
the enciphering transformation is generally of a more complex nature
than the perturbing noise in a channel; and, second, the key for a
secrecy system is usually chosen from a finite set of possibilities while
the noise in a channel is more often continually introduced, in effect
chosen from an infinite set."
When Carl W. Helstrom, author of Statistical Theory of Signal
Detection, was asked whether the techniques of isolating signals from
noise had any relevance to crypt-analysis, he replied: "I suspect that the
analogy between the enciphering rule of 'key' and random noise will not
prove very fruitful. It seems to me more appropriate to regard the
encipherment as a filtering of the original message to produce a
transformed version. The 'filter' is a definite transformation rule, but the
analyst doesn't know what it is. ... The problem is then to discover the
transformation rule, or the nature of the filter, when given the statistics
of the input and output. It is like finding the structure of an electrical
filter by passing random noise through it and measuring the statistical
distributions of the input and output voltages."
Cryptology may also be regarded as a conflict in the sense employed
in The Theory of Games and Economic Behavior by John Von Neumann
and Oskar Morgenstern. As Shannon, who first made the allusion, puts
it: "The situation between the cipher designer and cryptanalyst can be
thought of as a 'game' of a very simple structure; a zero-sum two-person
game with complete information, and just two 'moves.' [A zero-sum game
is one in which one contestant's advances are made at the expense of the
other.] The cipher designer chooses a system for his 'move.' Then the
cryptanalyst is informed of this choice and chooses a method of analysis.
The 'value' of the play is the average work required to break a cryptogram
in the system by the method chosen."
Cryptology is, by definition, a social activity, and so it may be
examined from a sociological point of view. It is secret communication,
and communication is perhaps man's most complex and varied activity.
It encompasses not just

words but gestures, facial expressions, tone of voice, even silence. A
glance can express a tale more sweetly than a rhyme. Basically, all forms
of communication are sets of agreements that certain sounds or signs or
symbols shall stand for certain things. One must be a party to these
preconcerted rules if one wants to communicate.
But all forms of communication are not at all times and all places
known. Those who happen to know one system that others around them
do not can use it for secret communication. Irish troops sent to the
Congo as part of the United Nations force in 1960 spoke Gaelic over the
radio, and the U.N. commander, General Carl von Horn of Sweden, called
it the best code in the Congo. This is a kind of cryptography by default,
depending upon a fortuitous ignorance—a defective cryptography.
Effective cryptography deliberately establishes special rules of
communication that deny information to those who would otherwise
understand the messages.
This withholding of information constitutes the essential element of
that which is called "secrecy." All the manifestations of secrecy—hiding
places, disguises, locked doors— share the basic idea of not
communicating objects or information. Its extreme form is silence (which
conjures up an Orwellian nightmare of the extreme form of
eavesdropping—detection and interpretation of brain waves). An
exhaustive investigation of the concept of secrecy would require, as
Maurits de Vries has pointed out, "a complete examination of the
relations between individuals and be-tweea groups in our society,"
because secrecy is the antithesis of communication, and
communication—as that which makes man a social being—encompasses
all aspects of cultural behavior. Cryptography combines these antitheses
into a single operation; a wag might define it as "noncommunicating
communication."
The relation between cryptography and cryptanalysis is not logically
necessary; it is contingent. One can envision men communicating by
secret means with others not even thinking of prying. But in the real
world, the cryptanalyst —or more accurately the potential cryptanalyst—
comes first. What need for cryptography if no one would eavesdrop? Why
build forts if no one would attack? Thus the assumption that someone
will attempt a cryptanalysis, no matter how tentatively or incompetently,
engenders cryptography.

Experience of the interreaction between cryptography and
cryptanalysis has precipitated out certain practical principles. They all
refer to time, because all practical matters involving mortal men connect
eventually with that one inexorable, irreversible, irretrievable factor.
Time, for the cryptographer, controls a variable relationship. The most
general of the cryptographer's principles deals with the sliding ratio
between speed and security; as the need for speed in communications
increases, the need for security decreases. Early in the planning of a
major operation, messages demand great security because the enemy, if
he could read them, would have time to prepare countermoves. But in
the heat of battle, commanders may use plain language because the
enemy, though he intercepts the messages, may not have time to react
effectively. This principle arranges a nation's cryptosystems in a
hierarchy in which front-line systems are simple and diplomatic systems
secure and more complex. "Of each such system," Friedman wrote, "the
best that can be expected is that the degree of security be great enough
to delay solution by the enemy for such a length of time that when the
solution is finally reached the information thus obtained has lost all its
'short term,' immediate, or operational value, and much of its 'long term,'
research, or historical value."
The paramount requirement for all cryptosystems is reliability. This
means that cryptograms must be decipherable without ambiguity,
without delay, and without error. It implies, for example, that cipher
machines will be sturdy enough to withstand ordinary abuse so that they
will be ready to operate properly when a message comes in. Usually the
simpler the system, the more reliable. The requirement excludes from the
combat zone ciphers of more than two steps. Any encipherer's errors or
garbles should be correctable without having to call for a retransmission.
This bans systems in which a single error garbles the message from the
point of error on, as in autokey ciphers (such systems are said to have an
undesirable error-propagation characteristic). Obviously, if a general
cannot rely upon the validity of messages that come out of his cipher
machines, the cryptosystem is worse than useless.
Secondary requirements for a cryptosystem are security and rapidity.
Which one comes first depends upon the needs of the users. Further
down the scale of importance stands

I
the requirement of economy. This rules out any system that requires
several men to encipher, makes the ciphertext more than twice as long as
the plaintext, or is too complicated or expensive to manufacture or
distribute.
In addition to these general requirements, military and diplomatic
cryptosystems must meet two specific ones— both first enunciated by
Kerckhoffs. The first rests upon the almost universal employment of
telegraphy or radio-telegraphy for military and diplomatic
communications. No system is acceptable whose cryptogram characters
cannot be sent in Morse code; excluded are squares, angles, crosses, or
other designs. The second rests upon a working assumption of military
cryptography: that the enemy knows in general how a cipher works.
Secrecy must depend upon the keys used. No method is acceptable that
does not accede to this requirement, that does not provide for both a
general system and specific keys.
For the cryptanalyst, time's demands remain fixed. Always at his back
he hears time's winged chariot hurrying near. He seeks to get out his
solutions as quickly as possible. It is probably true that a message will
always have some historical value, but that is small comfort to a
commander who does not get a cryptanalysis that would have warned
him of an enemy attack until after the attack is under way. The factors
that affect the time required to solve cryptograms—aside from external
factors, like the speed of sending the intercepts back to the
cryptanalyst— are the strength of the system, the soundness of the
regulations for its use, how closely the cipher clerks follow those
regulations, the volume of text, the size and skill of the cryptanalytic
organization, and the amount and character of collateral information.
Bringing skill into the picture raises the question of whether
cryptanalysis is a science or an art. It is both. On the one hand,
cryptanalysis—or, more properly in this context, cryptanalytics—is an
organized body of knowledge. It studies and controls phenomena. Its
whole spirit is scientific, but that of an applied science, like engineering.
On the other hand, cryptanalysis—here meaning the steps performed in
solution—clearly depends upon personal ability. Some cryptanalysts are
better than others. In this sense, cryptanalysis is an art. So, in this
sense, is any human activity that demands a certain aptitude for its
superior practice. Yardley said that outstanding cryptanalysts were gifted with "cipher brains," and rather glamorized the
faculty, but in fact "cipher brains" are just the cryptologic manifestation
of a general characteristic— talent in a given field. Who possesses "cipher
brains" and why, however, raise complicated questions.
Human knowledge not only cannot answer them now, it does not even
understand how the mind performs the basic psychological operation of
cryptanalysis—pattern recognition. How the brain can supply the
missing letters to a fragment of plaintext which it has never before seen
resembles such problems as how one can read words in a handwriting
one has never seen or recognize a piece of music as Mozart's even though
one has never heard it before. These problems remain among the still
unsolved ones of psychology and biochemistry, as convoluted as the
cerebral cortex and molecular chains which may hold the answer.
If the psychological roots of cryptology remain obscure, the biological
roots are clear. Those roots reach back through the eons to the first
protozoa struggling for life in the warm seas of the primordial earth. For
cryptography and cryptanalysis, though they are highly sophisticated
technologies, retain at their inmost cores, like chromosomes that
determine their heredity, the most primitive of functions.
Cryptography is protection. It is to that extension of modern man—
communications—what the carapace is to the turtle, ink to the squid,
camouflage to the chameleon. Cryptanalysis corresponds to the senses.
Like the ear of the bat, the chemical sensitivity of an amoeba, the eye of
an eagle, it collects information about the outside world. The objective is
self-preservation. This is the first law of life, as imperative for a body
politic as for an individual organism. And if biological evolution
demonstrates anything, it is that intelligence best secures that goal.
Knowledge is power. In an atmosphere of competition, it may exist in two
modes: mine and mine enemy's. All organisms attempt to maximize the
former and minimize the latter. Cryptography and cryptanalysis
exemplify the two modes. Cryptography seeks to conserve in exclusivity a
nation's store of knowledge, cryptanalysis to increase that store. But
knowledge alone is not power. To have any effect it must be linked to
physical force. Cryptology, like the services of supply and transportation
and administration, aids the fighting troops that constitute a main
element of

national power. Nations use that power to advance their political and
social goals. Cryptography and cryptanalysis are means to those ends.
And that is their position in the ultimate scheme of things.
Even when the ends that they serve are purely defensive in regard to
other nations, there exists a difference in morality between the means of
cryptanalysis and such means as armies and navies. The latter are
honest and above-board, open deterrents to aggression; they are like
strong men armed. Cryptanalysis is itself an aggression— often a
preventive one, to be sure—but still an aggression, a trespass. Moreover,
it is surreptitious, snooping, sneaking; it makes its government
hypocritical. It is the very opposite of all that is best in mankind. It
shatters the highest ethical precept: to do unto others as we would have
others do unto us.
Is it, then, ever morally justified? It is. A single act can be both moral
and immoral, depending on circumstances. Killing is permissible in selfdefense. So is cryptanalysis. In war, of course, cryptanalysis can look like
a positive good, especially when it saves lives. Even in peace,
cryptanalysis may be a form of self-defense. It can warn of hostile intent
and enable the government to preserve life and liberty, without which
there is no doing to others of any kind. But when a nation is not
threatened, it is wrong for it to violate another's dignity by clandestine
pryings into its messages, just as it is wrong to indiscriminately tap
telephone lines or invade the privacy of a man's castle. That is why it is
indefensible for the United States to read the messages of friendly
nations like Norway, Britain, or Peru.
Even when justified, cryptanalysis remains an evil, and it goes against
the American grain. Ever since July 4, 1776, the United States has stood
for morality and integrity, in international affairs as in domestic, in the
Fourteen Points as in the Emancipation Proclamation. It is this stand
that, in large measure, makes America great. Cryptanalysis therefore
poses a much greater problem for the United States than for other
nations. It perhaps reflects this concern that the United States places her
national crypt-analytic agency within the Defense Department, where it
belongs in ethical terms, while Great Britain puts hers in the Foreign
Office, where it belongs in a practical way.
Only once has cryptanalysis been treated as the sin

against morality that it is: in 1929, before Hitler and the Japanese
militarists, with no nations potentially dangerous to the United States
and self-preservation not at issue, Henry L. Stimson closed Yardley's
Black Chamber. Even though it was done at a time when the United
States could afford it, the decision was a profoundly moral one, and it
marched in the center rank of American belief. Was it soft-headed,
unrealistic? No. Idealism is the ultimate realism. Ideas of truth and
justice always eventually triumph. Mankind can learn. America's whole
history shows this, as does humanity's ascent from barbarism. The
growth of wisdom and morality—urged on in these present times by the
very real danger of total annihilation—may some day lead mankind to
beat its swords into plowshares. When it does, it will no longer need
cryptanalysis, and will dismantle organizations like N.S.A. and the SpetsOtdel. Their nonexistence then will testify to a true peace on earth. And
may such be their glorious destiny!

Suggestions for Further Reading
IF YOU ENJOYED reading about codes and ciphers and want to learn more about them, the following list may

guide you. It includes only works in print in English; libraries will have others.
First, of course, is the unabridged version of this book. Though it adds but little to the individual episodes
as printed here, it enriches the background with other stories and technical details, and cites sources. It is
published under the same title by the Macmillan Company, 866 Third Avenue, New York, New York
10022, 1164 pages, $17.50.
To solve cryptograms, join the American Cryptogram Association. This worldwide organization of
mutually helpful amateur cryptologists publishes a small magazine every other month with cryptograms for
solution and articles on how to solve them. Dues are $3.00 a year; the treasurer is Miss Edna Bickley, 312a
West Jackson, Mexico, Missouri 65265.
Two books describe the standard cipher systems and how to solve them. Abraham Sinkov's Elementary
Crypt-analysis (Random House, 1968, 189 pages) is very clear and effectively relates the techniques to the
underlying mathematics. Helen F. Gaines's Cryptanalysis (1939, reprinted Dover, 1956, 237 pages) covers
more ground but is less understandable.
Other works deal with aspects of the subject. Barbara W. Tuchman recounts the political effects of the most
important cryptogram solution in history in The Zimmermann Telegram (1958, reprinted Macmillan, 1966,
244 pages). Ladislas Farago's The Broken Seal (Random House, 1967, 441 pages) tells about the
development, theft, and solution of Japanese cryptosystems before Pearl Harbor. William F. and Elizebeth
S. Friedman's The Shakespearean Ciphers Examined (Cambridge University Press, 1957, 303 pages) is a
witty expose of the kooks who "decipher" false authorship claims of Francis Bacon from Shakespeare's
plays. And Raymond T. Bond has collected sixteen of the
458

better short stories involving a cryptogram, including those by Poe, A. Conan Doyle, Agatha Christie, and
O. Henry, in his Famous Stories of Code and Cipher (1947, reprinted Collier Books, 1965, 383 pages).
For youngsters, the following are the best of the many books in print: Sam and Beryl Epstein, The First
Book of Codes and Ciphers (Franklin Watts, 1956, 62 pages), for grammar-school ages; Herbert S. Zim,
Codes arid Secret Writing (William Morrow, 1948, 154 pages), for the junior high school level; and James
Raymond Wolfe, Secret Writing: The Craft of the Cryptographer (McGraw-Hill, 1970, 192 pages), for the
high school level.

Index
0075 code/134, 137, 139, 140, Ame, C., 248
142, 143, 145, 148 13040 code, 137, 143, 144, 148,171
A-3 scrambler, 294-298
Abbasi, A., 374
ABC Code, 278

Abel, R., 371-372, 376
Acme Code, 278
ADFGVX system, 158-164, 167,

442
ADFGX, 158-161, 165 "Adventure of the Dancing

Men, The," 416-420 Advertisements, personal, in
newspapers, 414-416 A.E.F. See American Expeditionary Force A.F.S.A. See Armed Forces
Security Agency Akin, S. B., 320 Aktiebolaget Cryptograph, 211 Aktiebolaget
Cryptoteknik,
211
Albert, A. A., 440 Alberti, L. B., 90-95, 98 All-purpose cipher, 401-402 Alphabet cipher, xii Alphabetical
Typewriter (cipher machine.) See
PURPLE Amateurs, 388-389, 402-408
See also inventors
American Black Chamber. See Black Chamber
American Black Chamber, The, 179-181

American Cryptogram Association, 410, 411-412
American Expeditionary Force, 156-157
American Indian languages, 289-290
American Telephone and Telegraph Company, 193-199, 202-203, 294, 295, 409
Amjadi, M., 374
AN-103, 325
Anderson, W. S., 3, 340
Ango Kenkku Han, 322
Arabs, 80-82
Argenti, G. B., 86
Arisue, S., 328
Armed Forces Security Agency, 379-380
Army Security Agency, 15, 319,381
Artha-sastra, 71

A.S.A. See Army Security Agency
Atbash, 72-73, 292
Atlantic, Battle of, 244-245, 268-272
Atlantis, 243

Atlas computer, 394
A. T. & T. See American Telephone and Telegraph Company
461

Atterbury, F., 107-108 Augustus Caesar, 77 Australia, 266 Austria, 128-129
See also Dechiffrierdienst; Geheime Kabinets-Kanzlei
black chamber, 104 Austria-Hungary, 128 Authenticators, 315 Autokeys, 97-98, 409, 453 Automated
cryptography, 197 "Automatic cryptography,"
198
B section, 245-246 Babbage, C., 406, 415 Babington, A., 87-89, 417 Babylonia. See Mesopotamia Bacon, Sir
Francis, 166, 430,
432, 458 Bacon, R., 430-432, 434-435,
436
Bacon-Shakespeare controversy, 184-185 BAMS code, 243, 325 Band-shift, 292-293 Band-splitting, 293, 294
Baudot code, 195 Barber, R. T., 337 Barne, L, 412 Barne, W., 412 Baudot code, 194-195, 261 Baudot, J. M. E.,
195 Bazna, E., 228 B-Dienst, 241-245, 264, 268 Belaso, G. B., 96-98 Bell, Edward, 146-147 Bell Telephone
Laboratories,
443 Bentley's Complete Phrase
Code, 278 Beobachtung-Dienst, 241-245,
264, 268
Bergenroth, G. A., 424-^28 Bernstorfi, J. H. A., von, 134153 passim Berthold, H. A., 156-157
Bestuzhev-Ryumin, A., 341 Beurling, A., 258, 261-262,
663
Bible, 72-73 Bibo, Major, 230-231 Bigram, definition, xiii Bird, J. M., 435 BLACK code, 249, 254 Black
chambers, 104-106,109, 274, 341
American, 6, 173-179, 191,
192, 457
Bletchley Park, 263-264 Boki, G. L, 359-360, 362 Bond, R. T., 549 Book cipher, 186-187 Bratton, R. S., 30
Braune Blatter, 225 Breon, W., 279-280, 286 Brooke-Hunt, G. L., 172 Brotherhood, F. M., 1-2, 11 BROWN code,
323 Browne, Sir Thomas, 432 Bryant, H. L., 2-3, 4, 47 Bullock, F. W., 317 Bureau du Chiflre, 159 Burke, J. P.,
390 Busch, H., 271 Business codes, 422-423 Byrne, J. F., 408-410
C-36, 212 Cabinet Noir, 111 Cablegrams. See Commercial
codes Cables, German transatlantic,
cutting of, 129 Caesar alphabet, 77 Caesar, J., 77 Caesar substitution, 77, 95,
292, 354, 414, 415 Canada, 183, 266 Canaris, W., 249 Carbonari, 419 Cardano, G., 146 Cardano grille, 281, 283
Cartier, F., 159 Cave, R., 46

Cavendish-Bentinck, V. F. W.,
266
C.B., 319-320, 322 Censorship, U.S., 274-289 Central Intelligence Agency, 378, 379, 382, 383, 384, 398
Chamber analysis, 166, 257 Chaocipher, 409, 410 Chase, P. E., 121-122 Chaucer, G., 171 Checkerboard, 76,
121-122, 186, 343, 357-359, 368, 369, 376 See also ADFGVX; Straddling
checkerboard
Chetardie, Marquis de la, 341 Chiffrierabteilung, 233-237 CHI-HE, 309 Childs, J. R., 172 China, 71, 281 Church
registers, 312 Churchill, W. L. S., 131-132,
244, 267-268,297-298 C.I.A. See Central Intelligence
Agency
Ciano, G., 248, 249 Cicero, operation, 228-230 Ciphers, xii, xiii-xiv all-purpose, 401-402 See also codes;
Monoalpha-betic substitution; Poly-alphabetic substitution; Transposition
Cipher alphabet See Alphabets Cipher devices cipher reel
See cipher disks; cipher machines; grilles; multiplex system; skytale Cipher disks, 92-94, 403 Cipher machines,
167, 339,
401, 402, 453
See also A.T.&T.; Cipher disks; csp-642; Enigma; Hagelin machine; Jefferson cipher; M-94; M-134; M-138; M209; PURPLE; Siemens & Halske; SIGABA;
SIGTOT; Wanderer Werke Ciphertext, definition, xiv Ciphony, 291-298 Clark, H. L., 24 Clausen, H., 379
Clausen, M. G. F., 368-369 Cleartext, definition, xv Cleaves, H., 223 Code, 71, 112, 126, 167, 173-176, 216,
219, 259, 290-291, 330-331, 354, 356, 362-363 commercial, xiv, 111, 130,
278
definition, xii-xiv enciphered. See Enciphered
code
one-part, defined, xiii solution of, 139-140, 143144, 218-219, 223 two-part, defined, xiii See also 0075; BROWN; KRU; LA; under individual names Code and
Cipher Compilation
Section, 191 Code and Signal Section, 12,
192, 207, 302
Codebreaking, definition, xv Codegroups, definition, xii-xiii Codenames, 266-268 See also under individual
codenames
Codenumbers, definition, xii Codetext, definition, xiv Codewords, definition, xii Coincidence, theory of, 189
Collins, S. W., 286 Combat Intelligence Unit, 8,
10,12,16,35,300-314 Communications intelligence,
xv Communications Intelligence
Summary, 37
Communications security, xv "Communication Theory of Secrecy Systems," 443-444

464

Ititi

Computers and tabulators,
393-395
COMSEC, 387-390 Consolidated Exporters Corporation, 421-422 COPEK, 30,45,303,311 Coral Sea, Battle of, 304-305,
310
Corbiere, A., 107 Corderman,W. P., 317 Cory, Mr., 33 Council of Ten, 83 Craig, M., 14 Cramer, G., 413 Cryptanalysis
as a physical science, 440442 becomes a major element of
intelligence, 165 becomes most important element of intelligence, 339-340
becomes specialized, 166 coining of term, 190 contrasted with cryptography, 154, 410, 439-441, 452, 455 definition,
xv linquistic bases of, 81-82 machines for. See Robot cryptanalysts; Computers and tabulators mathematization of, 339
methods of, 441-442 physical nature of, 440 pleasure of, 410-411 science or art, 454—455 time element in, 453-454
See also Cryptanalytics;
Cryptology Cryptanalytics, 454 Cryptanalyze, definition, xv Cryptogram, definition, xiv Cryptogram, The, 411
Cryptography as noise, 450-451 contrasted with crypt analysis, 154, 410, 439-441, 452, 455
definition, xi hierarchy of systems, 17 machines for. See Cipher
machines
mathematical nature of, 440 mechanization of, 339 pleasure of, 410 practical principles, 453-454 spontaneous origins
of, 77 time element in, 453-454 See also Cryptology; Cryptophony; Steganography Cryptology Arabs create, 80 as a black art, 79 biological roots of, 455 definition, xv future of,
400-402 game theory, 451 literacy's effect, 77 morality of, 178 ontology of, 455-456 permanent embassies' effect,
83
psychological bases of, 455 radio's effect, 153-155 sociology of, 451-452 telegraph's effect, 111-114,
154-155 U.S. takes world lead in,
191 West takes lead over East
in, 92 World War I's effect, 165167 World War IPs effect, 338340 See also Cryptography;
Cryptanalysis
Cryptophony, definition, 291 csp-642, 326 Cuneiform cryptography, 72
Dahlerus, B., 214-215 Dalgarno, G., 437-438 Damm, A. G., 210-212, 256, 339

Dancing Men cipher, 416-420 Dasch, G., 285 Dato, L., 91 David, A. L., 271 Deceptions and dummy traffic,
36-37
Dechiffrierdienst, 350, 356 Decipher, definition, xv Decode, definition, xv Decipherers, British, 107-111
Deciphering Branch, 109-111 Deductive solutions, 441-442 Dee, J., 431-432 De Grey, N., 134-135, 138,
140-141, 149, 265 Department of Communication, 263-264, 265-266 De-Scrambler, 293 Deubner, L., 351352, 353,
355
Deutsche Reichspost, 295-298 De Vries, Marquis, 440, 452 Dewey, Godfrey, 445 Digraph, definition, xiii
Digraphic substitution, 118121, 228 Direction-finding, xvi, 9, 132,
269-270
Disk, cipher. See Cipher disks Donitz, K., 237, 241 Doolittle, J., 307 Double transposition, 238 Doud, H. S., 11
Doyle, A. C., 416-420 Draemel, M. F., 207, 306 Dulles, A. W., 379, 398-399 Dulles, J. F., 399 Dummies. See
Fake messages;
Nulls
Dunning, M. J., 46 Dyer, T. H., 45, 300-303, 312,
330, 333
Eckhardt, H. von, 143, 149150, 171
Edgers, D., 27, 47 Eisenhower, D. D., 274 Electric Code Machine, 207
Electronic security, xv Elements of Cryptanalysis,

191
Encicode, definition, xiv Encipher, definition, xiv Enciphered code, 175, 216, 219, 221, 230, 362-363, 367,
422-423, 449 definition, xiv invention of, 94 solution of, 131-132 See also J codes PA-K2;
Schliisselheft Encode, definition, xiv England, 86-90, 106-11, 129, 177, 224, 248, 239, 242-245, 395, 398
See also Bletchley Park; Decipherers; Deciphering Branch; Department of Communications; M.I. 1 (b); M.I. 8
Enigma, 6, 21, 210, 211, 237,
238, 240, 271, 367 Eno, A. L., 194 Epsilon Eridani Epstein, S. and B., 458 "Erring Siamese," 77-78 Euler, L.,
406 Evans, A. R., 328 Ewing, Sir Alfred, 129-132, 133
F and p inks, 169-170
Fabian, R. J., 12, 26, 37, 301, 302,308,312
Fabyan, G., 184, 185, 433
Fake messages, 246-247
Fallacy of key size, 407
Family codes, 283
Farago, L., 458
Federal Bureau of Investigation, 276, 286, 287, 372, 378
Federal Communications Commission, 34, 42
Feely, J. M., 436-437
Fellers, B. F., 250-254 passim

Fellgiebel, E., 232-233, 236237
Fenner, W., 235 Fernmeldeaufklarung, 238,
253-254 Field ciphers
origin of, 112-113,166
principles of, 126-127, 453454
Figl, A., 128, 227-231 passim Fingerprinting apparatus,
radio, 386 Finland, 258, 364 Finnegan, J., 310 "Fists" of radiotelegraphers,
31 Five-numeral system. See JN25 Five-Power Treaty, 176, 177,
181
Flag officers' system, 8,45, 301 Fleet Radio Unit, Pacific
Fleet. See FRUPAC Fletcher, F. J., 304 Foote, A., 368-369 Forschungsamt, 215, 224-226,
227, 228, 230, 232 Forschungsanstalt, 295-298 Fractionating ciphers, 121-122
See also ADFGVX France, 83-86, 101-104, 106, 110, 111, 172, 224, 260-261, 341, 395, 397, 398
See also Bureau de Chiffre;
Service du Chiffre Franz, W., 236 Freemasons' cipher, 413-414 Frequency of letters, analysis
of, 81-83, 91, 167, 339,
441-442
Frequency counts, 81-82 Friedman, E. S., 185, 458
rumrunning solutions, 420422 Friedman, W. F., 183-192
and Yardley, 179, 183
as teacher, 190
at Riverbank Laboratories, 185-187, 190
Baconian studies, 184-185
characteristics, 183-184
contributions to cryptology, 339
early life, 183-185
Hindu solutions, 186-187
in G.2 A.6, 188
in Signal Corps Code & Cipher Compilation Section, 190-192
in S.I.S., 6, 192
Index of Coincidence, 189, 190
interest in cryptology, 185
inventions, 190
nervous breakdown, 26
Pletts machine solution, 187
PURPLE solution, 1-2, 11, 24-25, 191, 213
Voynich manuscript, 437
writings, 188-190, 458 Friedrichs, A., 217, 219, 223,
221 FRUPAC, 311-312, 314-315,
331-333 Fuchs, K., 371 Funkaufklarungsdienst, 240241
0.2 A.6 155-157, 189 Gaines, H. F., 458 Gallery, D. V., 270-271 Gallup, E. W., 185 Gamba, V., 246 Game
theory, 451 Gamma epsilon, 133 Gamma u, 133 Gardner, N., 275 Gaussin, J., 197 Geheime Kabinets-Kanzlei,
104-106, 111 General system, xvi, 127 Geometrical systems, 281, 283 Germany, 129, 134-153, 156-161, 177,
237-245, 261-

Germany (continued)
263, 271, 364-365, 366-367
0075 (German code), 134, 137, 139, 140, 142, 143, 145, 148 13040 (German code), 137,
143, 144, 148 Reichsicherheitschauptamt,
226-231 Wehrmachtnachrichtenverbindungen, 232-233 See also 0075; 13040; B-Dienst; Chiffrierabteil-ung; Forschungsanstalt; Forschungsamt;
Funkauf-klarungsdienst; OKH; OKL; OKM; OKW; Pers z; S.D.; Sonderdienst Dahlem
Gestapo, 225, 226 Gherardi, L., 248-249 Gifford, G., 87-88 Glavnoye, Razvedyvatelnoye Upravlenie, (G. R. U.)
368 Goggins, W. B., 315 "Gold-Bug, The," 388, 416 Gorgo, 75 Goring H., 215, 224-225,
227
GRAY code, 322, 333 Great Britain. See England Greece, ancient, 73-76 Grille, Cardano, 281, 283 G. R. U.
See Glavnoye Razvedyvatelnoye Upravlenie
Guitard, M., 159, 163-164 Gusev, 361 Gyld6n, O., 256 Gylden, Y., 256-258, 259
Hagelin, B. C. W., 210-214,
339
Hagelin machines, 210-214, 237, 400, 406, 422
See also M-209 Hague Convention articles of
war, 43

Hall, W. R., 133-134, 141-142, 146
Hamilton, V. N., 397
Hancock, C. B., 340
HARUNA, 39, 40, 41, 67
HATO code, 6, 38
Hayhanen, R., 376
Hebern, E. H., 191, 193, 206-210, 339
Hebern Electric Code Inc., 207-210
Hebrew ciphers, 72-73
Heeresnachrichtenwesens, 237
Helstrom, C. W., 451
"Hermit metamorphosing letters," 78
Herodotus, 74-75
Hieroglyphic cryptography, 68-70
Hill, L. S., 339
Himmler, H., 225, 226-227
Hindenburg, P. von, 346, 347, 352
Hindus' ciphers, 186-188
Hira gana, 310
Historians, 423-428
Hitchings, O. J., 301
Hitler, A., 210, 223-224, 225, 229, 296
Hitt, P., 199, 203, 409
H.N.W. See Heeresnachrichtenwesens
Hoffmann, A. B., 351
Hoffmann, E., 216
Hollerith tabulating machines, 318
Holmes, W. I., 306, 331
Holmes, S., 416-420
Holtwick, J. S., Jr., 22, 305
Roman, W. B., 403
Homer, 73-74
Homophones, xii, 80
Hoover, H., 177-178
Hoover, J. E., 287
Hornbeck, S. K., 181
Homer, E. W., 289
Hottl, W., 227-231, 248
Houdini, H., 411
House, E. M., 137-138, 168

Huffduff, 269-270
Hull, C., 4, 29, 32, 33, 46
Hungary, 230-231
See also Austria-Hungary Huttenhain, E., 236
1.1., 332
I.B.M. See International Business Machines Corporation
Ibn ad Duraihim, 80-81
I.D., 132
Identification-friend-or-foe system, (I.F.F.), 390
Iliad, 73-74
Index of Concidence and Its Applications in Cryptography, 189, 190
India, 71-72
Indian languages, 289
Indians, American, 289-290
Inductive solutions, 411-442
Information theory, 442-450
moo DENPO, 33-34, 56
Institute for Defense Analyses, 387, 389-390
Intelligence Bulletins, MAGIC, 28-29
Interception, xv, 13-15 154155, 391-392
See also Mail opening; Traffic volume; Wiretapping
International Business Machines Corporation, 394 Machines, 300, 302, 305, 308, 318, 320, 326, 332-333
International Code Machine Company, 207
International Communication Laboratories, 203
International Telephone and Telegraph 203
Inventors, 388-389, 402-408
Inversion, 292
Inverter, 292, 294
Invisible inks, 169-170, 275, 276, 284-287
Isomorphic cryptograms, 23 Italy
Servizio Informazione Militaire, 246-248 Servizio Informazione Segreto, 245-246 See also B section; Sezione
5; Sezione 6; Venice Ito, S., 46
j series of Japanese diplomatic codes, 15, 19-20, 39, 220 J19, 39
Ja, 175
Janssen, H. P. M., 282
Japan, 1-68, 173-175, 266, 273-274, 301, 303, 307, 310-311, 322, 330, 332
See also Ango Kenkyu Han; Tokumu Han
"Japanese Diplomatic Secrets," 181
Jargon code, 281-282
Jefferson cipher, 114-116,
191, 222
See also csp-642; M-94; M-138
Jerdan, W., 404
JN25, 8, 12, 45, 301, 303, 307, 311-312, 314, 332
jN25b, 8, 12, 303, 307
JN25c, 303, 311
Johnson, L. B., 400
Joyce, James, 408-410, 444-445
jp, 176
Kakimoto, G., 325 Kama-sutra, 72 Kameyama, K., 30, 46 Kasiski examination, 199-200 Kasiski, F. W., 122-124
Kasiski solution, 198, 199-200 Kata kana, 173-174, 310 Kautilya, 71

Keitel, W., 233 Kempf, S., 233 Kennedy, J. F., 328-330 Kerckhoffs, 124-125, 126128, 454 Kerckhoffs superimposition,
127-128, 200, 205 Kesselring, A., 238, 239 Kettler, H., 233 Keys
definition, xiv
general system, 127
generation of, 401-402
orgin of, 96-97
See also Autokeys; Running
keys
Keynumber, definition, xiv Keyphrase, definition, xiv Keyphrase cipher, xiv Keyword, definition, xiv
Kharkevich, 361 Khnumhotep II, 69 King, E. J., 307 Kinsey, A. C., 413 Kircher, A., 430 Kita, N., 16
Knatchbull-Hugessen, Sir
Hughe, 228 Knights of the Golden Circle,
413
Knispel, H. K., 271 Knox, F., 4 Koch, H. A., 210 Kowalefsky, J., 175, 322 Kramer, A. D., 3, 4, 13, 47-48, 5455
See also OP-20-G Kraus, H. P., 428, 439 Kripo, 226 Krivosh, R., 361-362 Krivosh, V., 361-362 Kroger, H. and
P., 372 KRU codes, 155-156 Krug, H. G., 218 Kühn, B. J. O., 39, 47, 66-67 Kullback, S., 192, 318, 329,
385 Kunze, W., 216, 218, 223224, 301, 339
LA, 17-18, 38, 40, 45, 46 Langlotz, E., 216 Lanphier, T. G., Jr., 336-337 Lansing, R. L., 148-149 Lasers, 402
Lasswell, A. B., 46, 334 Layton, E. T., 36-37, 308-309, 311
LEB KAMAI, 72

Lesson, J., 412
Letter frequency, 442, 446,
448 See also Frequency analysis
Letters of the alphabet, characteristics of, 81-82, 91
Lexicography, 81
Lexington, 304

Literature of cryptology, 416420, 457-458 American, 189, 190
Livesey, F., 172, 175
"Lucy" network, 368, 370
Ludendorff, E., 161-164, 346-347, 352-354
Ludwig, K. F., 276
Luftnachrichten, 240
Luning, H. A., 276
Lynn, G. W., 13
M-94, 191
M-134, 317
M-138, 222, 254, 323
M-209, 213, 214, 238-239,
317, 338, 363 MacArthur, D., 30, 303 McCollum, A. H., 3, 4 Mackay Radio & Telegraph
Company, 53 Mackensen, A. von, 158, 352354 Mackensen, H. G. von, 248,
249
Magdeburg, 131 MAGIC, 3, 393
distribution, 28-29
importance of, 29-30
translation, 27-28

470

THE CODEBREAKERS

MAGIC (continued)
See also J codes; PURPLE;

OP-20-o; S.I.S. Magic, 79, 84, 86 Magnus, A. von, 150 Mail opening, 104, 108-109 Manly, J. M., 169, 171, 179,
433, 435-436, 438 Mannerheim, C., 363 Marci, J. M., 430 Marshall, G. C., 14, 28-29,
30, 57, 58-61, 312-314 Martin, W. H., 390-391, 396397
Mara code, 331 Mary, Queen of Scots, 86-90,
417
Masking system, 293 Masons, 413 "Mathematical Theory of
Communication, A," 443444 Mathematics, 339, 440, 442
See also Statistics Mauborgne, J. O., 198-199, 301
as Chief Signal Officer, 7, 24
cryptologic highlights, 7
invents unbreakable cipher,
198-199
May, A. N., 371 Mayfield, I. S., 16, 40 Mellenthin, F. W. von, 365,
366
Menet Khufu, 68 Mesopotamia, 72 Mexican microdot ring, 288 Meyer, A., 207 M.I. l(b), 172, 187, 264 M.I. 8 (Great
Britian), 264 Mi-8 (U.S.), 168-173 Microdot, 287-289 Middle Ages, 78-79 Mid-Pacific Strategic Direction-Finder Net, 9, 11 Midway, Battle of, 309-310,
311-314 Minckler, R. W., 11
Mitchell, B. F., 390-391,
396-397
Mitchell, J. W., 336 Mobasheri, J., 374-376 Monalphabetic substitution, 77-79, 406, 407, 412, 413, 417, 444-445
definition, vii
solution of, 81-83
See also Atbash; Caesar substitution; Checkerboard
Montdidier, Battle of, 164 Montgomery, B., 256 Montgomery, W., 134-135,
138-139, 263
Moorman, F., 156, 157, 409 Morehouse, L. P., 197-198 Moreo, J. de, 84-85 Morgenstern, O., 451 Morikawa, H., 322,
325 Morimura, T. See Yoshikawa,
T.
Morse code, 454 Morse, S. F. B., Ill Moyzisch, L. C., 229 Muller, H. K., 221 Multiplex systems. See CSP642; Jefferson cipher; M-94;
M-138
Multiplexing, 194 Murphy, R., 221-222 Murray, A. A., 13 Music, 301 Myzskowski, E., 403
Nachrichten-Verbindungswesen, 240 Napoleon, 342 National Puzzlers League, 411 National Security Agency, 378-400
budget, 383-384
building, 381-382
cryptanalysis, 392-398
duties, 380-381
founding, 380

National Security Agency (continued)
organization of, 385-387, 390-391
overseas branches, 382
results, 396-400
security in, 383-385
size, 382 Navahos, 289-290 Naval disarmament, conference for, 176-177 Nebel, F., 161 Neumann, J. von,
451 New York Cipher Society,
410, 412
Newbold, W. R., 433-436 Newspapers, personal advertisements in, 414-415 Nigeria, 77
Nihilist cipher 344, 368 Nimitz, C. W., 303, 304, 310,
311, 312, 334, 335, 337 97-shiki O-bun In-ji-ki, 21, 46
See also PURPLE N.K.V.D., 360, 368 Noise (in information
theory), 450^51 Nomenclators, xiv, 84, 87, 402, 427
death of, 112, 114 Nomura, T., 325 North Africa campaign, 239,
251-256 Norway, 242, 257-258, 259,
264 N.S.A. See National Security
Agency
Nsibidi script, 77 Null, definition, xii Null cipher, 281, 282-283,
293
Oberkommando der Kriegs-marine, 231, 241, 264
Oberkommando der Luftwaffe, 231, 240
Oberkommando der Wehrmacht, 231-237 Oberkommando des Heeres,
231, 237 Occultism, 79 Oda, Lieutenant, 326 Office of Strategic Services,
273
Off-line encipherment, definition, 197
O.G.P.U., 361, 362 Ohnesorge, W., 296-298 Oite. See PA-K2 O.K.H. 231, 237 O.K.L. 231, 240 O.K.M. 231,
241, 264 O.K.W. 321-237 On-line encipherment, 197,
400 138th Radio Intelligence
Company 320-322 One-time pad, 216, 368, 371372, 388 One-time system (tape, pads),
199, 368 OP-16-F2, 13 OP-20-G, 1, 11-12, 13, 23, 26,
28, 193, 266, 269, 301, 303,
315
OP-20-cx, 13 OP-20-GY, 1, 2, 13 OP-20-GZ, 13 Open code, 281-283
ORANGE, 22

Oshima, H., 35, 273-274 O.S.S. See Office of Strategic
Services OVERLORD, 268 Ovid, 414 Ozaki, H., 327
PA-K2, 18-19, 38, 39, 40, 44,
45, 46, 66 Painvin, G. J., 159-165, 172,
301, 442 solution of ADFGX cipher,
159-160, 161, 442 Panin, N. P., 342

Parke, L. W., 13 Parker, R. T., 194, 197, 409 Paschke, A., 216, 218 "Passport code," 18

A "Pats," See microdot

T

Pearl Harbor attack, 1-68 W
378
f!
Pering, A. V., 3, 13
**"
Pers z, 216-224, 230 Personal advertisements, 414415
Peter the Great, 341
,
Petersen, T. C., 438
'%>' Petrov, E., 361 Petrov, V. M., 360-361 Phelippes, T., 86-88, 417 Philippines, U.S.
Navy crypt-analytic unit, 12, 45, 301303
Pictures, encipherment of, 203 Pierce, E. C., 279-280, 286 Pigpen cipher, 413 Placode, definition, xiv Plaintext,
definition, xi, xv Playfair cipher, 7, 118-121,
155, 328-330, 403 Playfair, L., 118, 120-121 Pletts, J. St. V., 187 Plutarch, 76 Poe, E. A., 416 Polk, F. L., 148-149
Pokorny, H., 350-352, 353,
356
Poland, 215
Polyalphabetic substitution, 350, 351, 353, 354
definition, xii
development of, 90-99
eclipse of, 99-100
rebirth of, 113
solution of, 123-124, 127128, 199-200 Polybius square, 76, 121, 343,
403
Polygrams, definition, xiii Polygraphia libri sex, 95 Polyphonic substitution, 415 Porta, G. B., 98
Postal Telegraph Cable Company, 203
Praun, A., 237
Price, B., 277, 279
Prisoners' cipher, 343-344
Private Office, 109
Probable word solutions, 441-442
PROD, 390
Prohibition, 420-422
Protocryptography, 72
PT-109, 328
PURPLE, 1-2, 15, 21-26, 42, 191, 266, 273-274, 315
Puzzle cryptograms, 411
Qalqashandi, 80-81
Rabelais, F., 416
Radar, 310
Radio, 153-165, 402
Radio Corporaation of America, 16, 39-40, 294
Radio intelligence, 9-10
Radio intelligence companies, 272, 320-321
Radio Intelligence Publications, 45
Radiotelephone. See Telephone secrecy
Random key, 199 quasi-random key, 401—402
Raven, F. A., 26, 390
R.C.A. See Radio Corporation of America
RED (Japanese), 15, 22, 23
Redman, J., 312
Redundancy, 444-450
Reichssicherheitshauptamt, 226-231
Rendezvous (film), 181-182
Rennenkampf, P., 345-350 passim
Ribbentrop, J. von, 216, 229
Rickert, E., 171
Rin-spuns, 77

Riverbank Laboratories, 185190 Riverbank Publications, 189190, 198
Robot cryptanalysts, 219, 236 Rochefort, J. J., 8, 37, 45, 300, 302, 303, 311
See also Combat Intelligence Unit Roehm, E., 225 Rogers, J. H., 291 Rohrbach, H., 217, 222 Rome, 77
Rommel, D. C. von, 250-252 Ronge, M., 227 Room 40, 130-133, 172, 263 Room 100, 256 Room 2646, 192
Roos, W. R., 282 Roosevelt, F. D., 29, 48-49,
50-51, 54-55, 57-58, 6263, 67, 295-296, 298 Rossignol, A., 101-104 Rote Kapelle, 368 Rotors, 204-205, 406
machines, 207, 209-210, 400
solution of, 191, 205-206
See also Damm; Enigma; Hebern; Koch; Scherbius Rotscheidt, W., 236 Rowlett, F. B., 11, 192, 400 R.S.H.A.
See Reichssicherheitshauptamt Rumrunners, 420-422 Running keys, 127, 199, 200 Russia, 129, 177, 395
black chambers, 341
Cold war, 371-377
cryptanalysis, 367-368
cryptosystems solved, 350-351, 353-356, 363-367
Czarist, 341-342
diplomatic cryptosystems, 368
military cryptosystems, 350, 351, 353, 354, 355-356, 362-363, 364
spy cryptosystems, 368-369,
371-372, 376-377 World War I, 344-357 World War II, 362-370
s code, 330-331
Safford, L. F., 11-12, 192193, 208, 269, 315 Samsonov, A., 346-349 Sandier, R., 259 Samoff, D., 16 Satake, T., 324, 327 Schapper,
Gottfried, 225 Schauffler, R., 216, 218, 224 Schellenberg, W., 227-228,
230, 298
Scherbius, A., 210, 329 Scherschmidt, H., 216 Schimpf, H., 225 Schlusselheft, 155-157, 159 Schutzstaffel
(S.S.), 225-226 Scientific method, 441 Scramblers, 290-298, 386, 423 S.D. See Sicherheitsdienst SEALION,
operation, 264-265 Secrecy, 452 Secret Office, 109 Seebohm, A., 253, 254 Segerdahl, E. O., 258, 260 Selchow,
K., 216, 218 Semagrams, 281, 283-284 Service du Chiffre, 163 Servizio Informazione Militaire, 246-248 passim Servizio Informazione Segreto, 245
Sezione 5, 246-248 Sezione 6, 246, 247-248 Shakespeare-Bacon controversy, 184-185, 416, 459 Shannon, C. E.,
407, 443-451
passim Shaw, H. R., 279-280, 286
SHESHACH, 72

Shift registers, 402 Shimizu, Lieutenant, 326 Shoho, 304

Shungsky, 361 Siam, 77-78
Sicherheitsdienst, 225-226 Siemens & Halske machine, 237-238, 261-262
SIGABA, 317

Signal Intelligence, xv School, 11
Signal Security, xv
Signal Security Agency, 273, 274, 317-319
SIGTOT, 203
S. I. M. See Servizio Informa-zione Militaire
Sinkov, A., 192, 320, 329, 390
S.I.S. (Signal Intelligence Service), 2, 6,7, 11, 23, 25, 28,40,46,266,316-317
Skeat, W. W., 406
Skytale, 75-76
Smith, E. See Friedman, E. S.
Smith, F. O. J., 111-112
Smith, L. C., & Corona Typewriters, Inc., 214
Sonderdienst Dahlem, 217
Sorge, R., 368
Sorge ring, 368, 369
Soro, G., 83
Soudart, E. A., 159
Soviet Union. See Russia
Spain, 84, 357, 424--427
Speech codes, 289-292
Spets-Otdel, 359-362
Spy cipher, 386-370, 371-327, 373, 376
Square table, 95-96, 99, 100
S.S. See Schutzstaffel
Stark, H. F., 4
Statistics, 189-190, 331, 442 See also mathematics
"Steganographia," 432
Steganograms, 281-289
Steganography, xi, 274-289
Stein, K., 236
Stimson, H. L., 4, 6, 178, 183, 457
Straddling checkerboard, 357-359, 368, 376
Street, G., 39-40
Strip cipher. See CSP-642; M138
Strong, L. C., 437 Subh al-a 'sha, 80 Substitution
basic solution of, 82-83 compared with transposition, 404 definition, xi See also Monoalphabetic substitution;
Polyalpha-betic substitution; Transposition Suetonius, 77 Suez crisis, 398-399 Superencipherment, definition,
xiv
See also Enciphered code Superimposition. See Kerckhoflfs superimposition Svensson, E., 11 Sweden, 210, 256-263, 363364 SYKO, 240, 241
Tableaux, 95-96, 98-99 Tabula recta, 95-96 Tabulators. See computers and
tabulators Tannenberg, Battle of, 348349 T.D.S. See Time-division
scramble
Technical Operational Division, 279-280, 281, 286,
288
Telconia, 129

Telegraph, 111-114, 154-155 Telegraphic Japanese, 27 Telephone secrecy, 289-298, 423
See also Wiretapping Teletype Corporation, 210 Teletypewriter, 193-198, 237238
Terminology, 190-191 Thailand, 77-78

Thiele, F., 233, 236
13040 (German code), 137,
143, 144, 148 Thucydides, 76 Tibet, 77 Time, 453-454 Time-division scramble, 293 Times, The (London), 414415 T.O.D. (Technical Operations
Division), 279-280, 281,
286, 288 (Togo, S., 30, 43^*4, 61 jTojo, H., 30-31, 43 fTokumu Han, 322-327 Tombstones, 412 Tomographic
ciphers, 121-122 Traicte des Chiffres, 98 Traffic analysis, xv, 8-10, 232,
305-306, 321-322, 326327
Traffic volume, 317-318, 407 Transmission security, definition, xi Transposition, 80, 238, 413
compared with substitution, 404
defined, xii
See also Skytale; Substitution
Trithemius, J., 95-97 xsu. See J series Tsukikawa, S., 39 Tuchman, B. W., 458 Turkey, 219, 224, 228-229,
231, 248, 263
U-158, 269
17-505, 270-271
U-boats, 132-133, 243-244,
269-272 Unbreakable cipher, 199-202,
216, 388
Unicity distance, 450 Unicity point, 450 United States, 191, 379
Air Force 389, 400
Army, 15, 389
cryptosystems, security of,

389-390, 402
cryptosystems solved, 110, 221-222, 231, 238-239, 241, 248-256, 325, 332 Navy, 14, 315-316, 381, 389
See also A.F.S.A.; Army Security Agency; Code and Cipher Compilation Section; Code and Signal Section;
Combat Intelligence Unit; Federal Communications Commission; FRUPAC; G.2 A.6; Mi-8; National Security
Agency; OP-20-o; Radio intelligence companies; S.I.S.; Signal Security Agency: T.O.D. Univacs, 394 Uruk, 72
Van Deman, R. H., 168
Vatican, 91, 177, 224
Vatsyayana, 72
Venice, 83
Vernam, G. S., 193-203, 329
system, 193-198, 202-203,
406
Verne, J., 416 Video scramblers, 386 Viete, F., 84-86 Vigenere, B. de, 97-99 Vigenere cipher, 97-100, 403,
406, 415, 440 Vinay, E., 197 Voge, R. G., 331 Voice communications, 289298
Volapuk, 125 _ Volunteer Evaluation Office,
232
von der Osten, Ulrich, 276 von Feilitzen, O., 258 von Neumann, J., 451 Voynich, E., 439

Voynich manuscript, 428439
Voynich, W., 432, 439 Vries, M. de, 440, 452
Waberski, P., 171 Walsingham, Sir Francis, 8689 Wanderer Werke machine,
237
Warburg, C. G., 257 Washington Disarmament
Conference, 175-177 Wave-form modification, 293 Weather-forecast codes, Japanese, 42, 322
Wehrmachtnachrichtenverbindungen, 232-233 Welker, G. W., 13 Wendland, V., 236 Wesemann, 243 Wheatstone, C., 117-118, 121,
415 Wheatstone cryptograph, 118,
187
Wigg, G., 398 Wilkins, J., 438 Willes, E., and family, 106108, 111, 113 Willoughby, C. A., 378 Wilson, Woodrow, 137-138,
140-141, 145, 153, 168 Winds code, 31-32, 34-35,
42-43
Wiretapping, 289 Witzke, L., 171 W.N.V. See Wehrmachtnachrichtenverbindungen Wobble scramble, 293-294 Wolfe, J. R., 458 Women's Army Corps, 313 Woodward, F. C., 45,
300 World War I, 129-167, 168172, 186-188, 344-357
World War H, 1-68, 214-340,
362-370 Wright, W. A., 45, 300, 302,
310-311, 333
"Wurlitzer Organ," 286-287 Yale University, 439 Yamamoto, I., 7, 299-300,
308, 314
assassination, 332-338 Yamanashi, 327 Yamato, 331-332 Yardley, H. O., 167-168,

172-173, 181-183 American Black Chamber,
The, 30, 179-181 characteristics, 167-168 chief of American Black
Chamber, 6, 173-180 chief of Mi-8, 168-172 in China, 182-183, 323 interest in cryptology, 167169
"Japanese Diplomatic Secrets," 181 later life, 182-183 solves Japanese codes, 173177
Voynich manuscript, 433 "Yardley symptom," 168 Yezidis, 77
Yoshikawa, 15, 39, 44-45, 49 YU, 175-176 Yugoslavia, 246-247
Zacharias, E. M., 192-193 Zapp, Prof., 288 Zenith Radio Corporation, 0075 (German code), 134,
137, 139, 140, 142, 143,
145, 148
Ziegenriiger, J., 218-219 Zim, H. S., 458 Zimmermann telegram, 134153, 263 Zipf, G. K., 445

THE HISTORY
OF SECRET CODES—
AND THE MEN WHO HAVE
CREATED AND BROKEN
THEM WITH DRAMATIC
CONSEQUENCES
FOR THE WORLD!
"THRILLING!"
-CINCINNATI ENQUIRER

"A LAVISH, NOTABLE ACHIEVEMENT!"
-THE NEW YORK TIMES

-.-THE CLASSIC IN ITS FIELD!"
-CLIFTON FADIMAN, BOOK-OF-THE-MONTH CLUB NEWS

"Comprehensive and astounding ... utterly fascinating

to anyone interested in political or military history, mathematics, mystery or pure who-dun-it—
Beginning wii
hieroglyphics and ending with computers, David Kahn
has produced an anthology of a hundred detective stories,
one more ingenious than the last, and all real> central
to the fate of armies and kingdoms.
-THE WASHINGTON POST

"SUCH FASCINATION THAT THE READER MAY FIND
HIMSELF NEGLECTING HIS WORK, BEING LATE
TO DINNER, AND UNABLE TO GET TO BED AT A
REASONABLE HOUR."
-NEWSWEEK

SELECTED BY THE BOOK-OF-THE-MONTH CLUB
NEW AMERICAN LIBRARY PUBLISHES SIGNET, SIGNETTE, MENTOR, CLASSIC, PLUMES NAL BOOKS

1
2

Not the same thing as the American name J for the J series of Japanese codes.

Whence, apparently, its codename. In American prewar military and naval parlance, the
codeword ORANGE meant Japan in official papers such as war plans, and even in personal letters
between high-ranking officers. In the 1930s, Lieutenant Jack S. Holtwick, Jr., a Navy cryptanalyst,
built a machine to solve a Japanese diplomatic cipher that was abandoned in 1938. American
cryptanalysts could very naturally have called it the ORANGE machine. As the successors of this
system appeared, each increasingly enigmatic, their American codenames might well have
progressively deepened in hue.
3
This is the literal translation made by Mr. Cory of GZ and given in MAGIC. But Friedman and
others have contended that it does not take into account the Japanese tendency to speak in
circumlocution and by indirection. The spirit of it might better be rendered into English, Friedman
suggested, as "on the brink of catastrophe" or "on the verge of disaster." Kramer conceded that
the words should not be interpreted as mildly as the English seems to indicate, but could imply
"relations are reaching a crisis." The British translated this phrase as "Relations between Japan
and (name of country) are extremely critical."
4
This may be why Rochefort did not simply request the keys from Washington via the special
monitors' channel.
5
The correct plaintexts were simply and, with the extra nd probably an inadvertent repetition, and
China, it must, with the LYL probably a codeword for comma.
PAPER_TEXT
