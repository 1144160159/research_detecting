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
# [752] Multilingual Cyber Threat Detection in Tweets/X Using ML, DL, and LLM: A Comparative Analysis
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
编号：752
题名：Multilingual Cyber Threat Detection in Tweets/X Using ML, DL, and LLM: A Comparative Analysis
年份：2025
DOI：10.1109/tcss.2025.3623021
来源：IEEE Transactions on Computational Social Systems
PDF：paper/10.1109_tcss.2025.3623021.pdf
已有粗分类：恶意流量、暗网与攻击检测
二级关联：无
相关性：中相关，分数 7
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\752.txt
- 原始字符数：76412
- 本次发送字符数：76412
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1758

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 13, NO. 2, APRIL 2026

Multilingual Cyber Threat Detection in Tweets/X
Using ML, DL, and LLM: A Comparative Analysis
Saydul Akbar Murad , Ashim Dahal , and Nick Rahimi

Abstract—Cyber threat detection has become an important
area of focus in the digital age of today due to the growing
spread of fake information and harmful content on social media
platforms such as Twitter (now “X”). These cyber threats, often
disguised within tweets, pose significant risks to individuals,
communities, and even nations, emphasizing the need for effective
detection systems. While previous research has explored tweetbased threats, much of the work is limited to specific languages,
domains, or locations or relies on single-model approaches,
reducing their applicability to diverse real-world scenarios. To
address these gaps, our study focuses on multilingual tweet
cyber threat detection using a variety of advanced models.
The research was conducted in three stages: 1) we collected
and labeled tweet datasets in four languages—English, Chinese,
Russian, and Arabic—employing both manual and polarity-based
labeling methods to ensure high-quality annotations; 2) each
dataset was analyzed individually using ML and DL models to
assess their performance on distinct languages; and 3) finally,
we combined all four datasets into a single multilingual dataset
and applied deep learning (DL) and large language model
(LLM) architectures to evaluate their efficacy in identifying cyber
threats across various languages. Our results show that among
machine learning models, random forest (RF) attained the highest
performance, and the bidirectional long short-term memory (BiLSTM) architecture consistently surpassed other DL and LLM
architectures across all datasets. These findings underline the
effectiveness of Bi-LSTM in multilingual cyber threat detection.
Index Terms—Accuracy, deep learning (DL), large language
model (LLM), loss, machine learning (ML), Tweet/X data.

I. INTRODUCTION

S

OCIAL networks have emerged as a global focal point,
functioning as platforms for the dissemination of opinions, ideas, marketing, and several other activities [1]. These
platforms offer customers rapid, complimentary, and readily
available tools to fulfill their varied requirements. Social net-

Received 12 February 2025; revised 9 June 2025 and 21 July 2025; accepted
15 October 2025. Date of publication 6 November 2025; date of current
version 3 April 2026. (Corresponding author: Nick Rahimi.)
The authors are with the School of Computing Sciences and Computer Engineering, University of Southern Mississippi, Hattiesburg, MS
39406 USA (e-mail: saydulakbar.murad@usm.edu; ashim.dahal@usm.edu;
nick.rahimi@usm.edu).
Digital Object Identifier 10.1109/TCSS.2025.3623021

works efficiently fulfill user needs, resulting in a continuing
rise in account registrations. Users continuously express their
opinions on subjects of interest, rendering social networks a
vibrant arena for communication and engagement. Twitter, now
renamed as “X,” is recognized as one of the most prominent
and impactful social networks. Tweets have emerged as a significant data source for many users, including manufacturers,
celebrities, healthcare experts, politicians, and researchers [2].
The extensive information dissemination on Twitter makes it a
significant asset for activities such as cyber threat identification,
sentiment analysis, and predictive modeling, underscoring the
influence of social networks in contemporary society.
With the increase of social media, cyber threats have become an increasing concern, affecting both individuals and
organizations in different ways [3], [4]. Threats come in various forms, such as online harassment, phishing scams, misinformation, and direct threats, using anonymity and etc. [5].
Some threats are sent privately through messages that target
specific people, while others are made public. The goal is
spreading fear among people or manipulating public opinion
[6]. These types of cyberbullying can affect human life, leading
to emotional distress, misinformation can create chaos or ruin
reputations, and phishing scams can cause financial losses [7].
As social media is increasingly embedded in our daily lives,
we need an effective system to identify and mitigate these
threats, ensuring a safer and more secure digital platform for
everyone.
In recent years, cyber threats based on tweets have become a growing concern, especially through the exploitation
of public tweets [6]. Such threats can result in serious consequences, often leading to public unrest or even community
violence [8]. Fake or misleading tweets can sometimes incite
mobs, creating panic and chaos in society [7]. On a broader
level, such tweets can exacerbate group differences, inciting
hostility along cultural, religious, or ideological lines [9]. In
many instances, aggressive or misleading tweets have instigated
diplomatic conflicts between nations, thereby straining international relations [10]. The rapid dissemination of harmful content
on platforms such as Twitter underlines the urgent necessity
to address these challenges and protect societal and global
stability.
Many researchers are actively working on detecting cyber
threats in tweets, using advanced AI techniques such as ML
[11], DL [12], and other novel approaches. Although significant
progress has been made, there are still several limitations in

2329-924X © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

MURAD et al.: MULTILINGUAL CYBER THREAT DETECTION IN TWEETS/X USING ML, DL, AND LLM

the current body of research. One major issue is that most of
the research concentrates on a single language [13]. But everyday tweets are coming in different languages. This languagespecific focus limits the scalability and applicability of the models in addressing threats in different linguistic contexts. Some
researchers worked on multilingual tweet datasets, but mostly
their approaches involve developing separate models for each
language [14]. This approach may be effective for small-scale
investigations, but it becomes wasteful and impractical when
used for big datasets comprising multiple languages. To address
the diversity of cyber threats on social media, it is important
to develop a generalized model capable of classifying tweets
across multiple languages effectively.
Another challenge is performance. Many researchers are
struggling to deliver robust results, particularly when handling
complex datasets with diverse linguistic [15]. Moreover, the absence of thorough comparisons among various architectures—
such as ML, DL, and LLM-based models—makes it difficult to
identify the most effective approach for tackling cyber threats
in tweets [16]. Without such comparisons, it is ambiguous
which approaches provide the optimal equilibrium of accuracy,
scalability, and flexibility. Considering these limitations, it is
important to develop a unified, generalized model to handle
multilingual tweet datasets. Additionally, a thorough evaluation
of different model architectures is essential to understand their
strengths and weaknesses to build more efficient and reliable
systems. Addressing these gaps will not only advance the field
of cyber threat identification but also foster a safer, more secure
online world.
To address the limitations of previous research, we focused on identifying cyber-threats in tweet data across multiple languages. Our study employed in two different ways.
In the first approach, we applied ML and DL models separately to each language dataset—English, Chinese, Russian, and Arabic—to evaluate their performance on individual datasets. In the second approach, we combined all four
language datasets into a unified, multilingual dataset and used
DL and LLMs for classification. The threat identification task
involved multiclass categorization for English, Chinese, and
Russian tweets, while the Arabic dataset was treated as a binary
classification problem. In the single-language analysis, both
ML and DL models demonstrated strong performance, effectively identifying threats within individual datasets. However,
when working with the combined dataset, the performance
of the models was less satisfactory, with results falling short
of expectations. As this project is ongoing, we are actively
working to improve the performance of the models on the
combined dataset. The contributions of our research are as
follows.
1) We independently collected four diverse datasets of
tweets containing potential cyber threats, covering English, Chinese, Russian, and Arabic, to ensure a comprehensive and multilingual analysis.
2) The datasets were labeled using a combination of manual
annotation and polarity-based methods, specifically designed to identify cyber threat-related content, with crossvalidation to ensure high accuracy.

1759

3) Experiments were conducted in two approaches:
analyzing each dataset individually to evaluate model
performance on single-language tweet threat detection
and combining all datasets for a multilingual tweet threat
analysis.
4) We employed three modeling techniques—ML, DL, and
LLMs—to thoroughly compare their effectiveness in detecting tweet threats across diverse datasets.
These contributions address gaps in previous research and
provide a robust framework for tweet classification across
languages.
The remainder of this research article is organized as follows. Section II provides an overview of related work, highlighting key studies and comparing them with our approach.
Section III outlines the methodology, detailing the data preprocessing steps, the models used, and the performance metrics
employed in the analysis. Section IV presents and discusses the
experimental results. Finally, Section V concludes the article by
summarizing the findings and discussing potential directions for
future work.
II. LITERATURE REVIEW
This section reviews the current state-of-the-art (SOTA) research on multilingual threat detection on Twitter/X. Although
ML, DL, and LLMs have widely reached the depths of multiple disciplines and achieved commendable results, multilingual
threat detection ceases to remain one of them. This gap is particularly concerning given the current rising prevalence of crosscountry cyber threats and social media based cyber attacks.
Rehan et al. [17] claimed to be one of the first to offer
multilingual threatening text detection on Twitter with LLMs.
They achieved this by first translating English text into their
Urdu corpus and then working on the Urdu language with
their AI implementation. The authors fine-tuned RoBERTa with
1313 English and 2400 Urdu samples. The sample of English
threats is highly skewed with only 128 nonthreat messages out
of the given 1313 samples. The authors also chose standard
ML algorithms such as support vector machine (SVM), logistic regression (LR), random forest (RF), convolutional neural
networks (CNN), bidirectional long short-term memory (BiLSTM) with RoBERTa and Word2Vec approaches to test their
approach. Although they have shown exceptional results with
over 91.89% accuracy, the definition of multilingual classification for the papers includes just English and Urdu. Our article
overcomes this shortcoming by providing a more quantifiable
and diverse approach that can work in English, Arabic, Russian,
and Chinese; all of which, according to the CIA’s The World
Factbook [18], are in the top 10 most-spoken first languages
around the world. This limitation in detecting multiple language
to detect cyber threat can lead to catastrophic cyber attack
vectors where the exploiters simply make use of the standing
language and its essence barriers.
Apart from this, there exists very little literature on multilanguage threat detection on Twitter tweets specifically. However,
there are some related research works in the field which indirectly address the theme of this article. Tundis et al. [19] provide

1760

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 13, NO. 2, APRIL 2026

a multilanguage approach towards identification of suspicious
users on social network platforms. Although their approach also
relies on using platforms such as Google Translate, Yandex,
and Bing Translate, the authors deduce a similarity score. The
authors do not mention a general formula to calculate the similarity score, but we can deduce it to the following from their
examples:
SNmax = maxSimilarity

n

i=1
n

i=1
n


(R1i × S1i )
(R2i × S2i )
(R3i × S3i )


(1)

i=1

where Sij ∈ [0, 1], i and j ∈ {1, 2, 3}, is the similarity score of
all tweets between the three service providers, (i.e., S12 denotes
similarity between service 1 and service 2) and Rij ∈ 0, 1 is
the binary indication that gives if the similarity score of Sij is
associated with the service or not.
From evaluation of (1), it can be evident that the function
grows exponentially as i and j grow, i.e., adding more service
translators for languages that may not be best performed by
the given three translators. We again argue for the need of a
language-dependent corpus system because some essence of the
original message could be lost within translation. Furthermore,
the authors only apply naive approaches such as bag of words
(BoW) alongside bi-gram and tri-gram versions of N-gram
technique. This provides a more statistical analysis of whether
the profile of some users could be dangerous or not rather than
a prediction with a finely labeled dataset and advanced ML and
DL algorithms. We overcome this drawback by using a finely
labeled dataset which gives robust prediction against tweets that
contain cyber threats.
In other similar works, Chiril et al. [20] comparatively studied and experimented with several methods and models to detect
multilingual hate speech towards multiple targets. Their dataset
contains 13 071 English and 3085 French tweets classified into
hate and nonhate tweets towards immigrants and women. They
achieve precision of 0.78 and 0.66 in the two tasks, respectively.
The authors, however, do not train on more variety or advanced
techniques like LLMs or GRUs. The benefit of not implementing a translation layer for multilanguage system can be observed
in this study as even with simple techniques like dimensionality
reduction and singular value decomposition the authors were
able to get good results in their dataset. Hussein et al. [21] did
multiclass classification of tweets on Threat (8280), business
(2331), irrelevant (6598), and Unknown (4159); number of
samples in brackets. They experimented with SVM, random
forest (RF), logistic regression (LR), decision tree (DT), naive
bayes (NB), and K-nearest-neighbor (KNN) algorithms and
got the best result with RF classification with a precision of
74 and accuracy of 67. Similar to the previous literature, we
conclude we could use more advanced methods and models to
bridge the research gap presented by the findings of this article
as well.

In the context of analyzing text for cybersecurity threats,
cyberbullying or hate speech by using SoTA LLMs, Kmainasi
et al. [22] fine-tuned Llama to LlamaLens which is a multilingual LLM for analyzing news and social media content. Their
dataset contains 2.7 million samples and over 222 labels, all of
which is an amalgamation of 103 dataset consisting multiple
social media post, news article, political debates and transcripts.
Out of the three languages tested: English, Hindi and Arabic,
cyberbullying was the only common category of interest in all
three languages where the authors gained accuracy of 90.07,
60.90, and 86.30, respectively. Hindi and Arabic had two common hate speech categories. Offensive speech was yet another
common category in all three of them, but the definition of
the term itself could be ambiguous. Miah et al. [23] worked
with ensemble learning of transformer and LLM for multilingual sentiment analysis. Although they work on five languages:
Arabic, Chinese, English, French, and Italian, their method
depends upon a translation layer as that of [17], [19]. The author’s ensemble consisted of Twitter-Roberta-Base-SentimentLatest, bert-base-multilingual-uncased-sentiment, and GPT-3
and produced an accuracy of 86% on all languages. Although
the authors argue that sentiment analysis is possible through
translation to English given their ensemble method achieved
the accuracy, but it is not the effective way to do so. We show
that by using a language specific corpus and model we can
handle nuanced information within the language like slang,
irony, and sarcasm away from the actual threats present in the
dataset.
Hirdi et al. [24] utilized different BERT based method to
detect offensive behavior on low resource language Bengali.
They trained XLM-RoBERTa-base with 44 000 comments from
social media platforms and gained an accuracy of 83.54%. This
accuracy is lower than [23], but the authors worked with a
different language with not as many resource for accurate translation and also accounted for Banglish which is a combination
of Bengali and English; either Bengali written in romanized English form or a mix of both language into a single sentence. This
practice of writing is common in many foreign language system
which do not use the roman alphabet as English alphabets can
be used to produce similar sounds as the other characters in
Arabic, Chinese, Devanagari, and Bengali scripts [25], [26],
[14]. The authors divided the remarks in the 44 000 comments
into one of five categories: sexual, not bully, troll, religious,
and threat. The authors employed technique to translate English
words in a Bengali text to Bengali to fit for this corpus which
is a better approach than translating the entire text from one
language into another. The author’s work in the Bengali language is commendable. Their work highlights the importance
of language understanding by constructing methodology for
Bengali which is not written in the roman alphabet and use the
finer details observed to determine the level of threat present
in the given tweet/post. We do argue that their approach could
be expanded to cover bases for multiple languages which our
research touches upon.
Table I shows a detailed comparison between our work and
previous research. Our work contributes to the existing literature by providing a deeper analysis of tweet classification for

MURAD et al.: MULTILINGUAL CYBER THREAT DETECTION IN TWEETS/X USING ML, DL, AND LLM

1761

TABLE I
SUMMARY OF MULTILINGUAL THREAT DETECTION/ANALYSIS STUDIES
Study

Data Source
Tweet FB IG

Number of
Classes

[17]
[19]
[20]





✗



✗

✗

2
2
2

[21]



✗

✗

4

[22]
[23]
[24]
Our work







✗

✗

✗
✗
✗
✗

Multi
3
5
Multi

ML
SVM, LR, RF
BoW, NGram
SVD
SVM, RF
LR, DT, NB
✗
✗
✗
LR, DT, RF

Models Used
DL

LLM

Acc.

Metrics
Prec. Rec.

F1

CNN, BiLSTM
✗
BERT

RoBERTa
✗
✗






✗



✗



✗
✗

English, Urdu
Multilingual
English, French

✗

✗





✗

✗

English

✗
BERT
✗
RNN, LSTM, GRU

LLaMA
RoBERTa, GPT-3
XLM-RoBERTa
XLM-RoBERTa






✗
✗
✗


✗
✗
✗


✗
✗
✗
✗

English, Hindi, Arabic
Multi-lingual
Bengali
English, Russian, Chinese, Arabic

Content Language

Note: Abbreviations: X = Twitter, FB = Facebook, IG = Instagram, ML = machine learning (SVM = support vector machine, LR = logistic regression, RF = random forest,
DT = decision tree, NB = naive bayes, BoW = bag of words, NGram = N-gram, SVD = singular value decomposition), DL = deep learning (CNN = convolutional neural
network, BiLSTM = bidirectional long short-term memory, BERT = bidirectional encoder representations from transformers, XLM-RoBERTa = Cross-lingual RoBERTa),
LLM = large language model (GPT-3 = generative pretrained transformer 3).

Fig. 1.

Workflow of the tweet data classification process.

safer online interactions. We offer a comprehensive evaluation
of various ML, DL, and LLM algorithms across four of the top
five most spoken languages, enhancing our understanding of
cyber threat detection.
III. IMPLEMENTATION DETAILS
In this section, we briefly discuss the working procedure of
this research. We started by discussing the data, including its
source and the process of labeling it. Next, we explained how we
processed the data, which included steps such as data cleaning,
removing stopwords, and tokenization. After processing, we
encoded the tokenized data and applied various techniques to
the dataset. Finally, we concluded the section by describing
the different parameters considered to measure the performance

of the models. Fig. 1 provides a visual representation of our
working procedure.
A. Data Collection and Labeling
For this research, we collected the dataset in 2021 from
the Tweet/X platform, focusing on tweets in four languages:
English, Arabic, Russian, and Chinese. The data was collected
without any specific geographical focus or topic constraints,
ensuring a broad and diverse representation of content across
different languages. The aim was to capture a wide range of
tweets to evaluate cyber threat detection in a multilingual context. Initially, the collected data was unlabeled, and the objective
was to classify the tweets into three categories: threat, neutral,
and nonthreat. We defined these categories as follows.

1762

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 13, NO. 2, APRIL 2026

TABLE II
DISTRIBUTION OF ANNOTATED TWEETS BY CLASS
ACROSS LANGUAGES
Lang.
Class

English

Arabic

Chinese

Russian

1416
842
313

418
1605

452
841
754

106
129
902

Neutral
Nonthreat
Threat

1) Threat: We defined “threat” tweets as those containing
malicious intent to harm or cause distress, such as direct
threats or harassment.
2) Nonthreat: We categorized “nonthreat” tweets as clearly
benign, positive, or harmless informational content with
no malicious intent.
3) Neutral: We classified “neutral” tweets as those lacking
clear malicious intent or strong positive/negative sentiment; they are not harmful but also not explicitly benign.
We have made the dataset publicly available, and it is included with the source of this article. Table II summarizes the
distribution of tweets classified as neutral, nonthreat, and threat
for the four languages.
We employed two labeling approaches to annotate the
dataset. The first approach was manual annotation, where four
students, each proficient in one of the four languages, assisted
in classifying the tweets into the predefined categories. This
ensured linguistic nuances were considered during the labeling
process.
The second approach is polarity-based classification. Polarity
(P ) measures the sentiment of a tweet and was calculated as
follows.
Given a tweet T consisting of n words w1 , w2 , . . . , wn , the
Polarity of the tweet is calculated as follows:
n
s (wi )
(2)
P (T ) = i=1
n
where P (T ) is the polarity of the tweet. s (wi ) represents the
sentiment score of the ith word in the tweet. This score is
positive for positive words, negative for negative words, and
zero for neutral words. n is the total number of words in the
tweet.
To classify tweets based on their polarity.
1) Threat: P (T ) ≤ −0.5
2) Neutral: −0.5 < P (T ) < 0.5
3) Nonthreat: P (T ) ≥ 0.5
The polarity-based labeling approach yielded results that
were largely consistent with the manual labeling. However, in
certain instances, discrepancies were observed between the two
methods. In such cases, we prioritized the manual labeling as
the final annotation, given its reliability and context-sensitive
accuracy. This combined approach ensured the dataset was
comprehensively and accurately labeled.
B. Data Preprocessing
In the data preprocessing stage, we began by cleaning unnecessary data to enhance the quality of the dataset and improve the

performance of the classification models. In the preprocessing
phase, before proceeding to the main code, we manually removed meaningless sentences and irrelevant information. This
process was carried out by native annotators, who ensured that
linguistic variations, such as slang, code-switching, and emojis,
were appropriately handled. Following this, we removed stopwords from the tweets in all four languages (English, Arabic,
Russian, and Chinese). Additionally, stemming was performed
to reduce words to their root forms, ensuring consistency and
further simplifying the data. Finally, the cleaned text data was
tokenized, breaking the tweets into individual words or subwords, and padding was applied to standardize the input length.
These steps prepared the data for model training, ensuring compatibility and optimal input representation for the subsequent
stages of analysis.
1) Data Cleaning: After labeling the datasets, our first objective was to clean the data to ensure it was suitable for analysis. Many tweets contained sentences that lacked meaningful
context, so we removed such sentences. As part of the manual
annotation and quality control process, annotators identified
and removed tweets that lacked meaningful context, such as
those consisting only of URLs or user mentions with no other
decipherable text, tweets containing only random characters,
or content that was entirely indecipherable or irrelevant to the
study’s scope. Additionally, we eliminated URLs, mentions,
hashtags, punctuation, and special characters using regular expressions (Regex).
We denote the labeled dataset as follows:
X l = {(t1 , y1 ) , (t2 , y2 ) , . . . , (tn , yn )}

(3)

where ti represents the ith tweet. yi is the corresponding label
for ti , where yi ∈ { threat, neutral, nonthreat }.
The cleaning process transforms each tweet ti into a cleaned
version ti by applying the following operations: a) removal of
irrelevant or nonsensical sentences; and b) removal of URLs,
mentions, hashtags, punctuation, and special characters via
Regex.
The cleaned dataset is represented as follows:
Xcl = {(t1 , y1 ) , (t2 , y2 ) , . . . , (tn , yn )}

(4)

where ti is the cleaned version of ti . This ensures that the
l
retains the labels yi while improving the quality
dataset Xclean
and relevance of the tweets ti .
2) Remove Stopwords and Stemming: After completing the
data cleaning process, we proceeded to remove stopwords from
the tweets in all four languages. Stopwords, which are common words that do not significantly contribute to the semantic
meaning of the text. These were eliminated to reduce noise and
enhance the quality of the dataset. This step can be expressed
mathematically as follows:
ti = RemoveStopwords (ti )
where ti is the cleaned tweet from the previous stage. ti is the
tweet after removing stopwords. RemoveStopwords represents
the stopword removal function applied to the cleaned tweet.

MURAD et al.: MULTILINGUAL CYBER THREAT DETECTION IN TWEETS/X USING ML, DL, AND LLM

After removing stopwords, stemming was applied to reduce
words to their root or base forms, further standardizing the text.
This transformation is represented as follows:

1763

where t
i is the tweet after stemming. Stem (·) represents the
stemming function.
The resulting dataset after these transformations is represented as follows:

4) Handling Class Imbalance: After analyzing the class
distribution in our dataset (Table II), we find that the dataset
classes are not balanced, with the “neutral” and “nonthreat”
classes being underrepresented compared to the “threat” class.
To address this imbalance and ensure that our model does not
develop a bias toward the majority class, we employed the
synthetic minority over-sampling technique (SMOTE). SMOTE
works by generating synthetic samples for the minority class to
balance the class distribution. We can represent the generation
of synthetic instances as follows:



Xsl = {(t
1 , y1 ) , (t2 , y2 ) , . . . , (tn , yn )} .

T̂i = Ti + λ(Tj − Ti ).


t
i = Stem. (ti )

(5)

This ensures that the processed tweets t
i retain their associated labels yi , making the dataset ready for tokenization and
further preparation for model training.
3) Tokenization and Padding: The final steps of our data
preprocessing pipeline were tokenization and padding, essential processes for preparing the text data for machine learning
models.
a) Tokenization: Tokenization involves breaking down
the text into smaller units and converting these units into numerical values. For this research, we set a vocabulary limit
of max_words = 5000, meaning we only retained the 5000
most frequent words in the dataset. Words outside this vocabulary were replaced with a special token indicating “out of
vocabulary.”
Mathematically, we can represent a preprocessed tweet t
i as
a tokenized sequence
Ti = Tokenize(t
i ).

(6)

Here t
i is the cleaned tweet after stopword removal and
stemming. Ti = {w1 , w2 , . . . , wk } is the sequence of tokenized
words. Each token wj is an integer index ranging from 1 to
max_words, corresponding to its place in the vocabulary.
b) Padding: Since tweets can vary in length, padding
ensures consistency by standardizing the length of all tokenized
sequences to maxlen = 500. If a sequence is shorter than 500
tokens, zeros are added (padding). If it is longer, it is truncated
to the first 500 tokens.
The padded version of a tokenized tweet Ti is as follows:
Pi = Pad(Ti , maxlen)

(7)

where Ti is the tokenized tweet, Pi = {p1 , p2 , . . . , pmaxlen } is
the padded sequence, pj = wj for j ≤ k, and pj = 0 for j > k
when the sequence is shorter than 500 tokens.
After tokenization and padding, the final dataset is represented as follows:
Xtl = {(P1 , y1 ), (P2 , y2 ), . . . , (Pn , yn )}

(8)

where Pi is the padded sequence of the ith tweet and yi is the
corresponding label.
This standardized approach significantly improved the data
quality and ensured compatibility with the subsequent analytical processes.

(9)

Here, T̂i represents the synthetic tokenized instance for the
minority class, Ti is a tokenized instance from the minority
class, Tj is a randomly selected tokenized neighbor of Ti ,
and λ is a random value between 0 and 1 that controls the
interpolation between the two instances. This allows for the
generation of new, plausible instances that enhance the minority
class’s presence in the dataset. By applying SMOTE, we were
able to balance the class distribution, ensuring that each class
had an equal opportunity to contribute to the model training.
C. Text Encoding
After preprocessing, the next step was encoding the text
data into numerical vector representations using Word2Vec.
Word2Vec transforms words into dense, continuous vector
spaces where semantically similar words have closer representations.
To handle the unique characteristics of each language, we
used different pretrained word embedding models tailored to
the linguistic features of English, Chinese, Russian, and Arabic.
1) English: We used GoogleNews-vectors-negative300.bin,
a model trained on a vast corpus of news data, which effectively captures the semantics and syntax of the English
language.
2) Chinese: For Chinese, we relied on GloVe’s 840B corpus
(300-dimensional vectors), which is well-suited for the
intricacies of Chinese morphology and character-level
meaning.
3) Russian: A custom-trained Word2Vec model,
tweets_model.w2v, was used for Russian, ensuring that
it captures the unique slang and informal expressions
commonly found in Russian tweets.
4) Arabic: For Arabic, we trained a Word2Vec model on
our own dataset to better account for the language’s rootbased structure, dialectal variations, and unique syntactic
features.
By using language-specific models, we ensured that the embeddings could capture the cultural and linguistic nuances of
each language, enhancing the effectiveness of our multilingual
cyber threat detection approach.
D. Word2Vec Representation
 in a dEach word w in a tweet t
i was mapped to a vector w
dimensional space, where d is the embedding size (300 in this

1764

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 13, NO. 2, APRIL 2026

case). Mathematically, for a tweet t
i = {w1 , w2 , . . . , wk }, the
Word2Vec embeddings create a sequence of word vectors.
Ei = {w
 1, w
 2, . . . , w
 k },

w
 j ∈ Rd .

(10)

1) Aggregating Word Embeddings: As ML models typically
require fixed-length inputs, the sequence of word embeddings
for a tweet Ei was aggregated into a single vector. Common
aggregation techniques include.
Mean pooling: Taking the average of all word vectors
1
Ti =
k

k


w
j.

j=1

Max pooling: Taking the maximum value across each dimension of the word vectors
Ti = max(w
 1, w
 2, . . . , w
 k ).

P (yi = 1|Ti ) =

Here, Ti ∈ Rd represents the encoded tweet as a fixed-length
vector.
2) Passing Encoded Data to the Model: Once encoded, the
tweet representations Ti were used as input to the classification model. The final dataset after encoding is represented as
follows:
l
Xen
= {(T1 , y1 ), (T2 , y2 ), . . . , (Tn , yn )}.

1) Language-Specific Classification: In the experiment, we
used ML and DL models for each language—English, Chinese,
Russian, and Arabic. The primary goal was to evaluate the performance of those models when trained and tested exclusively
on data from a single language. To achieve this, we employed
three ML models and three DL architectures, and we compared
the results between the models.
a) ML classifier: For training the ML models, we utilized
80% of the dataset, while the remaining 20% was reserved for
testing. Each algorithm was carefully configured with hyperparameters optimized for the classification task. In the following,
we detail the three ML algorithms employed:
Logistic regression (LR): The LR model maps the input features Ti to probabilities using a sigmoid function. The predicted
probability of a label yi is given by

(11)

where Ti is the vector representation of the ith tweet, yi is the
corresponding label.
These embeddings preserve semantic information and ensure
that the text data is represented in a numerical format suitable
for training machine learning or deep learning models. The
use of language-specific pretrained models further enhanced the
quality of the encoded representations by leveraging linguistic
and contextual knowledge inherent in each model.
E. Classifier
To analyze the dataset, we employed three distinct types of
models: ML, DL, and LLMs. For our ML approach, we utilized
logistic regression (LR) for its efficiency and interpretability
as a linear baseline, decision tree (DT) to capture nonlinear
patterns, and random forest (RF) for its robustness and high
performance as an ensemble method. In the DL category, essential for sequential text data, we designed architectures using long short-term memory (LSTM) and gated recurrent unit
(GRU) networks, chosen for their established ability to learn
long-range dependencies while mitigating vanishing gradient
issues. Crucially, we implemented these as bidirectional LSTMs
(Bi-LSTMs) and Bi-GRUs. This bidirectional approach was
selected because processing sequences in both forward and
backward directions enables the models to build a richer contextual understanding of each token by considering its entire
surrounding sequence, which is well-documented to enhance
performance on complex natural language processing tasks like
classification. These carefully selected ML and DL models,
alongside LLMs, allowed for a multifaceted assessment of the
dataset.

1

(12)
1 + e−(w  Ti +b)
where w
 is the weight vector, b is the bias term.
We trained the LR model with a maximum of 1000 iterations
(max_iterations = 1000) to ensure convergence.
Decision tree (DT): The decision tree algorithm partitions
the feature space Ti into regions by recursively splitting the data
based on features that maximize information gain or minimize
Gini impurity. The decision rule at each node can be expressed
as follows:

1if Tij ≤ threshold

f (Ti ) =
(13)
0otherwise
where Tij is the jth feature of Ti and threshold is the splitting
value determined during training.
Random Forest (RF): Random forest is an ensemble algorithm that builds multiple decision trees (DT1 , DT2 , . . . , DTM )
on random subsets of the data and features. The final prediction
is obtained by majority voting


(14)
f (Ti ) = mode DT1 (Ti ), DT2 (Ti ), . . . , DTM (Ti )
where M is the number of trees in the forest, and DTm (Ti ) is
the prediction of the mth tree.
l
=
Each algorithm was trained on the encoded dataset Xencoded
{(T1 , y1 ), (T2 , y2 ), . . . , (Tn , yn )}, where Ti represents the encoded tweet and yi the corresponding label. By using distinct
approaches such as linear modeling (LR), hierarchical splits
(DT), and ensemble learning (RF), we ensured diverse perspectives in analyzing and classifying the dataset.
b) DL classifier: We employed three distinct DL architectures Bi-RNN, Bi-LSTM, and Bi-GRU to analyze the dataset.
Each architecture was designed and tested independently to
evaluate its performance and identify the most effective model.
Additionally, we meticulously tuned the hyperparameters of
each architecture to achieve optimal results. To select the optimal hyperparameters, such as learning rate, batch size, and
dropout, we employed a combination of grid search and random
search techniques. These methods helped systematically explore different configurations and identify the best-performing
settings for each model. A brief overview of these models and

MURAD et al.: MULTILINGUAL CYBER THREAT DETECTION IN TWEETS/X USING ML, DL, AND LLM

Fig. 2.

1765

Workflow of the tweet data classification process.

their configurations, as used in our experiments, is presented in
Fig. 2. Below, we provide detailed descriptions of the models
and configurations used in our experiments.
Bi-RNF: The top architecture in Fig. 2 defines the RNF
models, which begin with a word embedding layer common to
all other architectures. The word embedding layer transforms
the input tokens into dense vectors of dimension d = 300, with
a maximum sequence length of 100. The embedding layer is
initialized with pretrained embeddings.
The first layer after embedding is a Bi-RNN with different
units like 32, 64, 128, configured to return sequences. This layer
captures temporal dependencies in both forward and backward
directions. Mathematically, the output of this layer is as follows:
HBiRNN = BiRNN(E)
where E is the embedding matrix for a sequence, and HBiRNN
represents the bidirectional output.
Following the Bi-RNN layer, the output is passed through
a dense layer with different neurons and a ReLU activation
function
D1 = ReLU(WDense1 HBiRNN + bDense1 )
where WDense1 and bDense1 are the weights and biases of the
dense layer.
To prevent overfitting, a dropout layer with a rate of 0.4 is
applied
D1drop = Dropout(D1 , 0.4).
This process is repeated for subsequent layers, including a
bidirectional GRU (Bi-GRU) and a bidirectional LSTM (BiLSTM), interspersed with dense layers (with varying neuron
counts such as 32, 64, and 128) and dropout layers. Each bidirectional layer captures sequential patterns, and the dense layers

act as feature transformation layers, enhancing the learning
capacity.
The output from the final dense layer is passed to another
dense layer with num_classes neurons and a softmax activation
function, producing a probability distribution for multiclass
classification
P (y|T ) = Softmax(WOutput HDense + bOutput ).

(15)

Here, WOutput and bOutput are the weights and biases of the
final dense layer, HDense is the output from the last dense layer,
and P (y|T ) represents the predicted probabilities.
The model was compiled using the Adam optimizer with a
learning rate of 0.005 and sparse categorical cross-entropy as
the loss function. The architecture ensures a robust framework
for processing sequential data, using bidirectional layers to
capture comprehensive context and dense layers to enhance
representational power.
Bi-LSTM: The second architecture in Fig. 2 is the Bi-LSTM
model, which also begins with the same word embedding layer
as the Bi-RNF architecture, transforming input sequences into
dense vectors of dimension d = 300. The first layer after embedding is a Bi-LSTM with 32 neurons, configured to return
sequences. For a sequence E from the embedding layer, the
output of this layer is as follows:
HBiLSTM1 = BiLSTM(E).
Following the Bi-LSTM layer, the output is passed through
a dense layer with different neurons and a ReLU activation
function
D1 = ReLU(WDense1 HBiLSTM1 + bDense1 )

1766

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 13, NO. 2, APRIL 2026

where WDense1 and bDense1 are the weights and biases of the
dense layer. To prevent overfitting, a dropout layer with a rate
of 0.4 is applied
D1drop = Dropout(D1 , 0.4).
This process is repeated for two other Bi-LSTM layers, each
configured to return sequences, followed by dense layers with
different neuron counts (e.g., 128) and dropout layers. The
output for the second Bi-LSTM layer is as follows:

To alleviate overfitting, a dropout layer is applied with rate
0.4
D1drop = Dropout(D1 , 0.4).
The architecture contains more bidirectional GRU layers,
each designed to process the output from the previous layer,
using differing neuron counts (e.g., 64 and 32). Regarding the
second Bi-GRU layer
HBiGRU2 = BiGRU(D1drop ).

HBiLSTM2 = BiLSTM(D1drop ).
The subsequent dense and dropout layers are applied as
follows:

Upon passing the third Bi-GRU layer, designed to output a
singular sequence instead of a whole sequence

D2 = ReLU(WDense2 HBiLSTM2 + bDense2 )

HBiGRU3 = BiGRU(HBiGRU2 ).

D2drop = Dropout(D2 , 0.4).

Finally, the model employs a dense layer including
num_classes neurons, utilizing a softmax activation function
to provide output probabilities for multiclass classification

The final Bi-LSTM layer is set to return a single sequence
instead of a complete sequence
HBiLSTM3 = BiLSTM(D2drop ).
Before generating the output, the architecture implements a
final dropout layer with a rate of 0.4
drop
HBiLSTM3
= Dropout(HBiLSTM3 , 0.4).

The output layer comprises a dense layer with num_classes
neurons and employs a softmax activation function for multiclass classification
drop
P (y|T ) = Softmax(WOutput HBiLSTM3
+ bOutput )

(16)

where WOutput and bOutput denote the weights and biases of the
output layer, while P (y|T ) denotes the projected probability
distribution for the classes. This architecture uses the sequential
learning capabilities of three Bi-LSTM layers, interspersed with
dense and dropout layers, to extract contextual information and
deliver accurate multiclass predictions.
Bidirectional gated recurrent unit (Bi-GRU): The final architecture in Fig. 2 is the Bi-GRU model, which closely follows
the structure of the Bi-LSTM architecture described earlier. The
primary difference lies in replacing the Bi-LSTM layers with
Bi-GRU layers. GRU is a simplified variant of LSTM that uses
fewer parameters while maintaining similar performance for
sequence modeling tasks.
The Bi-GRU model starts with the same word embedding
layer, where input tokens are transformed into dense vectors
of dimension d = 300. The first layer after embedding is a BiGRU with 128 neurons, configured to return sequences. For a
sequence E from the embedding layer, the output of the initial
Bi-GRU layer is as follows:
HBiGRU1 = BiGRU(E).
This is followed by a dense layer with 32 neurons and a ReLU
activation function
D1 = ReLU(WDense1 HBiGRU1 + bDense1 ).

P (y|T ) = Softmax(WOutput HBiGRU3 + bOutput ).

(17)

This design effectively captures sequential dependencies
through the gating mechanism of GRUs, while demonstrating
greater computational efficiency than Bi-LSTM.
2) Multiclass Classifier: Before implementing the multiclass classification models, we combined datasets from all four
languages—English, Chinese, Russian, and Arabic—into a single unified dataset. Each dataset was processed independently
up to the embedding stage, ensuring that the word embeddings
were created separately for each language while maintaining
a consistent embedding dimension across all datasets. After
generating embeddings, we merged the four embedded datasets
into one.
It is worth noting that the datasets for English, Chinese, and
Russian contained three class labels (threat, neutral, nonthreat),
while the Arabic dataset included only two labels (threat and
nonthreat). Despite this difference, we preserved the same embedding dimension across all datasets to ensure uniformity and
compatibility during the model training process. This unified,
multilingual dataset provided the foundation for training and
evaluating the multiclass classification models, including the
LLM-based classifiers.
a) DL classifier: For the multiclass classification task,
we utilized two distinct DL architectures: LSTM and GRU.
The architecture of those models is same that we already discussed earlier. To maximize efficiency and improve outcomes,
we modified the hyperparameters to better align with the integrated multilingual dataset. This process involved iteratively
modifying key aspects of the model, such as the number of
recurrent layers, the quantity of neurons within these layers,
and the dropout rates used for regularization. These adjustments
were made to better align the model’s capacity and learning
dynamics with the increased complexity and diversity presented
by the combined linguistic data. This methodology enabled us
to evaluate the efficacy of these models while modifying them to
address the complexities of multiclass classification in various
languages.

MURAD et al.: MULTILINGUAL CYBER THREAT DETECTION IN TWEETS/X USING ML, DL, AND LLM

b) LLM classifier: For the multiclass classification
task, we also used an LLM architecture, specifically XLMRoBERTa. The objective was to evaluate its performance in
comparison to the DL architectures, such as LSTM and GRU.
The technique utilized the strong multilingual capabilities of
XLM-RoBERTa, which was pretrained on a vast corpus of
text in many languages, rendering it very appropriate for the
integrated multilingual dataset.
The LLM architecture begins with tokenization via the XLMRoBERTa tokenizer, transforming input text into numerical representations while maintaining uniformity in sequence length
by padding and truncation. For a dataset D = {t1 , t2 , . . . , tn },
the tokenized input is represented as follows:
T = Tokenize(D, max_len)
where max_len = 100 is the maximum sequence length.
The tokenized data T is then passed to the XLM-RoBERTa
model, which outputs the last hidden state H
H = XLM-RoBERTa(T ).
Here, H is a tensor of size (n, max_len, d), where d is the
hidden state dimension of the model. To reduce this tensor to
a fixed-size vector for each input sequence, we apply a global
average pooling operation
P = GlobalAveragePooling(H).
The pooled output P serves as the input to a series of dense
layers. The first dense layer transforms P with 128 neurons and
ReLU activation
D1 = ReLU(W1 P + b1 ).
Dropout is applied after each dense layer to mitigate
overfitting
D1drop = Dropout(D1 , 0.4).
This process continues for two more dense layers with 64 and
32 neurons, respectively, each followed by dropout layers. The
final dense layer, configured with num_classes neurons and a
softmax activation function, produces the output probabilities
P (y|T ) = Softmax(WOutput D3drop + bOutput )

(18)

where P (y|T ) represents the probability distribution over the
class labels for the input text.
The model was trained with a learning rate of 0.0005, a batch
size of 16, and for 50 epochs. It was evaluated using sparse
categorical cross-entropy loss and accuracy metrics.
F. Performance Analysis
To evaluate the performance of all models, we considered
different parameters, including loss, accuracy, precision, recall,
and F1-score. These metrics provide a comprehensive view of
models performance for all four tweet datasets English, Chinese, Russian, and Arabic. Each metric takes a specific aspect
of the models’ performance, allowing for a detailed comparison
of their strengths and limitations. The mathematical definitions

1767

of these performance metrics are presented in Fig. 1. These
equations form the foundation for our analysis, illustrating how
the metrics were calculated to ensure consistent and accurate
evaluation of the models.
IV. RESULT
In this experiment, we utilized ML, DL, and LLM techniques
to analyze tweet threats in four different languages: English,
Chinese, Russian, and Arabic. We completed the experiment in
two different ways. In the first approach, we applied ML and
DL models to each language dataset separately; that’s allowed
us to evaluate performance on individual datasets. In the second
approach, we combined all four datasets into a single multilingual dataset and utilized DL and LLM models to assess their
performance.
A. English Data Analysis
Table III presents a comprehensive comparison between the
performance of machine learning (ML) and deep learning (DL)
models for English tweet threat detection, categorized into
threat (Th), neutral (Neu), and nonthreat (Non-Th). Among
the ML models, RF outperformed both LR and DT across all
metrics. Specifically, RF achieved the highest accuracy (86%)
and F1-score weighted average (FWA) (87%) among the ML
models, highlighting its superior ability to handle structured
data. Additionally, RF showed the best performance in precision
and recall, particularly excelling in the Threat category with a
precision of 0.89% and in the nonthreat category with a recall
of 0.85%. On the other hand, LR performed the worst, with the
lowest overall accuracy (47%) and FWA (47%).
In contrast, the DL models demonstrated competitive performance, especially in capturing sequential patterns in text
data. Bi-LSTM was the best-performing DL model, achieving an accuracy of 72% and FWA of 72%. While Bi-GRU
showed strong performance in precision for the Threat category
(0.87), it lagged behind RF in overall metrics. Bi-GRU followed
closely with an accuracy of 67% and an FWA of 66%, while BiRNF underperformed, with an accuracy of only 28%. Despite
these variations, RF still maintained a slight edge over the DL
models, particularly in terms of the weighted F1-score and
overall classification robustness.
Fig. 3 illustrates the performance of GRU, LSTM, and
RNF—in a multiclass classification task where Class 0 is neutral, Class 1 is threat and Class 2 is nonthreat. Each plot displays
the true positive rate (TPR) against the false positive rate (FPR)
for individual classes, along with their corresponding area under
the curve (AUC) scores. The dashed line representing “Random
Chance” (AUC = 0.50) serves as a baseline for comparison
across all models. Notably, the LSTM model demonstrates superior overall performance, with AUC scores of 0.86 for neutral
(Class 0), 0.92 for threat (Class 1), and 0.85 for nonthreat (Class
2). The GRU model also performs well, achieving AUCs of
0.80 for neutral, 0.90 for threat, and 0.77 for nonthreat. In
contrast, the RNF model exhibits performance equivalent to
random chance for all classes, with AUC scores of 0.50 for
neutral, threat, and nonthreat.

1768

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 13, NO. 2, APRIL 2026

TABLE III
PERFORMANCE COMPARISON OF ML AND DL MODELS FOR ENGLISH CYBER TWEET THREAT DETECTION

Model

ML

LR
DT
RF

DL

Bi-RNF
Bi-LSTM
Bi-GRU

Params (K)

23.89
27.65
26.05

Precision Per Category
in %

Recall Per Category
in %

F1-Score Per Category
in %

Th

Neu

Non-Th

Th

Neu

Non-Th

Th

Neu

Non-Th

0.40
0.77
0.89

0.48
0.80
0.84

0.57
0.73
0.86

0.54
0.78
0.91

0.46
0.77
0.85

0.43
0.75
0.85

0.46
0.78
0.90

0.47
0.78
0.85

0.28
0.64
0.87

0.00
0.76
0.71

0.00
0.73
0.58

1.00
0.65
0.37

0.00
0.85
0.85

0.00
0.64
0.73

0.44
0.65
0.52

0.00
0.80
0.77

Accuracy

PMA

RMA

FMA

PWA

RWA

FWA

0.49
0.74
0.85

0.47
0.76
0.86

0.48
0.77
0.87

0.48
0.77
0.87

0.47
0.77
0.87

0.49
0.77
0.86

0.47
0.76
0.86

0.47
0.76
0.86

0.00
0.69
0.65

0.28
0.72
0.67

0.09
0.71
0.72

0.33
0.71
0.65

0.15
0.71
0.65

0.08
0.72
0.71

0.28
0.72
0.67

0.13
0.72
0.66

Note: Abbreviations: ML = machine learning, DL = deep learning, LR = logistic regression, DT = decision tree, RF = random forest, Bi-RNF = bidirectional recurrent
neural framework, Bi-LSTM = bidirectional long short-term memory, Bi-GRU = bidirectional gated recurrent unit, Th = threat, Neu = neutral, Non-Th = nonthreat,
PMA = precision macro average, RMA = recall macro average, FMA = F1-score macro average, PWA = precision weighted average, RWA = recall weighted average,
and FWA = F1-score weighted average. Bold values are represent the best performance for each column.

(a)

(b)

(c)

Fig. 3. Multiclass ROC curves for the LSTM, GRU, and RNF models, evaluated on the English dataset, illustrating the true positive rate (TPR) against the
false positive rate (FPR) for each class. Each curve displays its corresponding AUC score, with a baseline representing “Random chance” for comparison.
(a) LSTM ROC curve for English tweets. (b) GRU ROC curve for English tweets. (c) RNF ROC curve for English tweets.

B. Chinese Data Analysis
Table IV presents a comparison of ML and DL models for
identifying threats in Chinese tweets. Among the ML models,
RF outperformed others, with an accuracy of 86% and an FWA
of 86%. RF demonstrated consistently high precision and recall
across all categories, particularly excelling in Threat detection
with a precision of 0.89 and a recall of 0.87. DT followed
closely with an accuracy of 78% and an FWA of 78%, while LR)
showed limited performance with an accuracy of just 56% and
an FWA of 56%. These lower scores highlight LR’s challenges
in handling the complex patterns present in the Chinese tweet
dataset.
In contrast, the DL models generally performed better than
ML counterparts across most metrics, showcasing their ability
to capture sequential dependencies and contextual nuances. BiLSTM achieved the highest accuracy (86%) and FWA (86%)
of all models, excelling in Threat detection with a precision
of 0.88 and a recall of 0.88. Bi-GRU closely followed with
an accuracy of 85% and an FWA of 84%, while Bi-RNF also
achieved an accuracy of 82% and an FWA of 82%. The DL
models consistently surpassed the ML models in PMA, RMA,
and FMA, demonstrating superior classification capabilities.
These results underscore the enhanced performance of DL models, particularly Bi-LSTM, in categorizing Chinese tweets with
greater accuracy and reliability.

Fig. 4 illustrates the performance of the LSTM, RNF, and
GRU models, respectively, on a Chinese tweet dataset. The
LSTM model demonstrates strong performance, with AUC
scores of 0.95 for neutral tweets (Class 0), 0.94 for threat tweets
(Class 1), and 0.95 for nonthreat tweets (Class 2). Similarly, the
GRU model achieves high performance, with AUC scores of
0.96 for neutral tweets (Class 0), 0.92 for threat tweets (Class
1), and 0.94 for nonthreat tweets (Class 2). The RNF model also
shows robust performance, with AUC scores of 0.94 for neutral
tweets (Class 0), 0.88 for threat tweets (Class 1), and 0.93 for
nonthreat tweets (Class 2). Overall, these results indicate that all
three models—LSTM, GRU, and RNF—perform significantly
better than random chance.
C. Russian Data Analysis
Table V describes the performance comparison between ML
and DL models for Russian tweet threat detection. The results
show a detailed perspective on the models’ effectiveness in
handling this dataset. For ML models, RF emerged as the best
performer, achieving the highest accuracy of 95% and an FWA
of 95%. RF also exhibited excellent precision and recall for the
nonthreat category, achieving perfect scores in precision (96%)
and recall (99%), demonstrating its strength in identifying nonthreatening tweets. DT followed RF in performance, with an
accuracy of 89% and an FWA of 89%. DT showed balanced

MURAD et al.: MULTILINGUAL CYBER THREAT DETECTION IN TWEETS/X USING ML, DL, AND LLM

1769

TABLE IV
PERFORMANCE COMPARISON OF ML AND DL MODELS FOR CHINESE CYBER TWEET THREAT DETECTION

Model

ML

LR
DT
RF

DL

Bi-RNF
Bi-LSTM
Bi-GRU

Params (K)

12.78
15.42
14.43

Precision Per Category
in %

Recall Per Category
in %

F1-Score Per Category
in %

Th

Neu

Non-Th

Th

Neu

Non-Th

Th

Neu

Non-Th

0.53
0.79
0.89

0.60
0.76
0.79

0.60
0.78
0.90

0.58
0.84
0.87

0.74
0.70
0.92

0.41
0.80
0.78

0.55
0.81
0.88

0.66
0.73
0.85

0.94
0.88
0.93

0.73
0.80
0.75

0.83
0.90
0.88

0.84
0.89
0.86

0.82
0.85
0.89

0.81
0.84
0.78

0.88
0.88
0.89

0.77
0.82
0.81

Accuracy

PMA

RMA

FMA

PWA

RWA

FWA

0.48
0.79
0.84

0.57
0.78
0.86

0.57
0.78
0.86

0.57
0.78
0.86

0.57
0.78
0.86

0.57
0.78
0.86

0.57
0.78
0.86

0.56
0.78
0.86

0.82
0.87
0.83

0.82
0.86
0.84

0.83
0.86
0.85

0.82
0.86
0.84

0.83
0.86
0.84

0.83
0.86
0.85

0.82
0.86
0.84

0.82
0.86
0.84

Note: Abbreviations: ML = machine learning, DL = deep learning, LR = logistic regression, DT = decision tree, RF = random forest, Bi-RNF = bidirectional recurrent
neural framework, Bi-LSTM = bidirectional long short-term memory, Bi-GRU = bidirectional gated recurrent unit, Th = threat, Neu = neutral, Non-Th = nonthreat,
PMA = precision macro average, RMA = recall macro average, FMA = F1-score macro average, PWA = precision weighted average, RWA = recall weighted average,
and FWA = F1-score weighted average. Bold values are represent the best performance for each column.

(a)

(b)

(c)

Fig. 4. Multiclass ROC curves for the LSTM, GRU, and RNF models, evaluated on the Chinese dataset, illustrating the true positive rate (TPR) against the
false positive rate (FPR) for each class. Each curve displays its corresponding AUC score, with a baseline representing “Random chance” for comparison.
(a) LSTM ROC curve for Chinese tweets. (b) GRU ROC curve for Chinese tweets. (c) RNF ROC curve for Chinese tweets.

TABLE V
PERFORMANCE COMPARISON OF ML AND DL MODELS FOR RUSSIAN CYBER TWEET THREAT DETECTION

Model

ML

LR
DT
RF

DL

Bi-RNF
Bi-LSTM
Bi-GRU

Params (K)

12.53
15.72
12.82

Precision Per Category
in %

Recall Per Category
in %

F1-Score Per Category
in %

Accuracy

PMA

RMA

FMA

PWA

RWA

FWA

Th

Neu

Non-Th

Th

Neu

Non-Th

Th

Neu

Non-Th

0.41
0.88
0.96

0.67
0.88
0.93

0.59
0.92
0.96

0.26
0.85
0.91

0.82
0.90
0.96

0.70
0.95
0.99

0.32
0.87
0.94

0.74
0.89
0.95

0.64
0.93
0.97

0.58
0.89
0.95

0.56
0.90
0.95

0.59
0.90
0.95

0.57
0.90
0.95

0.55
0.89
0.95

0.58
0.89
0.95

0.55
0.89
0.95

0.65
0.81
0.79

0.81
0.86
0.86

0.70
0.82
0.79

0.69
0.81
0.79

0.74
0.81
0.82

0.72
0.87
0.83

0.67
0.81
0.79

0.77
0.83
0.84

0.71
0.84
0.81

0.71
0.83
0.81

0.72
0.83
0.81

0.72
0.83
0.81

0.72
0.83
0.81

0.72
0.83
0.81

0.71
0.83
0.81

0.72
0.83
0.81

Note: Abbreviations: ML = machine learning, DL = deep learning, LR = logistic regression, DT = decision tree, RF = random forest, Bi-RNF = bidirectional recurrent
neural framework, Bi-LSTM = bidirectional long short-term memory, Bi-GRU = bidirectional gated recurrent unit, Th = threat, Neu = neutral, Non-Th = nonthreat,
PMA = precision macro average, RMA = recall macro average, FMA = F1-score macro average, PWA = precision weighted average, RWA = recall weighted average,
and FWA = F1-score weighted average. Bold values are represent the best performance for each column.

precision and recall for all categories. LR, while achieving reasonable recall for the neutral category (0.82), performed poorly
overall, particularly for the Threat category, with an recall of
only 0.26, resulting in an accuracy of 58% and an FWA of 55%.
In contrast, the DL models demonstrated competitive performance, with Bi-LSTM standing out as the top-performing
DL architecture. Bi-LSTM achieved an accuracy of 83% and
an FWA of 83%. It performed particularly well in the neutral
category, with a precision of 0.88 and recall of 0.81, and also
demonstrated balanced performance across other categories.

Bi-GRU followed closely, achieving an accuracy of 81% and
an FWA of 81%, showing strong performance in the neutral
category but moderate performance for the nonthreat category.
Bi-RNF, while achieving reasonable accuracy (58%), lagged
in overall weighted metrics such as FWA (55%) due to lower
scores in the threat and nonthreat categories. Although RF
demonstrated exceptional precision and recall in managing nonthreat tweets, Bi-LSTM provided a more equitable performance
across all categories, highlighting the robustness of the DL
architecture.

1770

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 13, NO. 2, APRIL 2026

(a)

(b)

(c)

Fig. 5. Multiclass ROC curves for the LSTM, GRU, and RNF models, evaluated on the Russian dataset, illustrating the true positive rate (TPR) against the
false positive rate (FPR) for each class. Each curve displays its corresponding AUC score, with a baseline representing “Random chance” for comparison.
(a) LSTM ROC curve for Russian tweets. (b) GRU ROC curve for Russian tweets. (c) RNF ROC curve for Russian tweets.
TABLE VI
PERFORMANCE COMPARISON OF ML AND DL MODELS FOR ARABIC CYBER TWEET THREAT DETECTION

Model

ML

LR
DT
RF

DL

Bi-RNF
Bi-LSTM
Bi-GRU

Params (K)

11.20
13.37
13.37

Precision Per Category
in %

Recall Per Category
in %

F1-Score Per Category
in %

Th

Non-Th

Th

Non-Th

Th

Non-Th

0.74
0.91
0.95

0.61
0.91
0.94

0.53
0.92
0.94

0.80
0.90
0.95

0.62
0.91
0.95

0.67
0.91
0.91

1.00
0.84
0.84

1.00
0.84
0.84

0.47
0.91
0.91

0.80
0.88
0.88

Accuracy

PMA

RMA

FMA

PWA

RWA

FWA

0.69
0.90
0.95

0.66
0.91
0.95

0.68
0.91
0.95

0.66
0.91
0.95

0.65
0.91
0.95

0.68
0.91
0.95

0.66
0.91
0.95

0.65
0.91
0.95

0.64
0.88
0.88

0.75
0.88
0.88

0.84
0.88
0.88

0.73
0.88
0.88

0.72
0.88
0.88

0.83
0.88
0.88

0.75
0.88
0.88

0.73
0.88
0.88

Note: Abbreviations: ML = machine learning, DL = deep learning, LR = logistic regression, DT = decision tree, RF = random forest, Bi-RNF = bidirectional
recurrent neural framework, Bi-LSTM = bidirectional long short-term memory, Bi-GRU = bidirectional gated recurrent unit, Th = threat, Non-Th = nonthreat, PMA
= precision macro average, RMA = recall macro average, FMA = F1-score macro average, PWA = precision weighted average, RWA = recall weighted average,
and FWA = F1-score weighted average. Bold values are represent the best performance for each column.

Fig. 5 depicts multiclass ROC curves for the GRU, LSTM,
and RNF models used in Russian tweet classification. The GRU
model achieves AUC scores of 0.90, 0.94, and 0.94 for Classes
neutral tweets (Class 0), threat (Class 1), and nonthreat (Class
2), demonstrating strong performance with a high TPR and low
FPR. The LSTM model performs similarly well, with slightly
higher AUC values of 0.91, 0.95, and 0.93 for the respective
classes. In contrast, the RNF model shows a lower overall
performance, particularly for Class 0, with AUC scores of 0.81,
0.91, and 0.91. While the RNF model still effectively classifies
Classes 1 and 2, it underperforms relative to the GRU and
LSTM models, especially for Class 0. These results highlight
the superior classification capability of GRU and LSTM models
in this context.

Fig. 6. ROC curves for the LSTM, GRU, and RNF models, evaluated on
the Arabic dataset, illustrating the true positive rate (TPR) against the false
positive rate (FPR) for each class.

D. Arabic Data Analysis
Table VI illustrates the comparative performance of ML and
DL models in detecting threats in Arabic tweets. Among the
ML models, the RF exhibited the highest overall performance,
attaining an accuracy of 95% and an F1 score of 95%. RF
had good precision for both threat (0.95) and nonthreat (0.94),
alongside the maximum recall for threat (0.94). This equilibrium resulted in an F1-score of 0.95 for threat and 0.95 for
nonthreat, establishing RF as the most dependable ML model
for this dataset. DT followed RF with an accuracy of 91% and an
FWA of 91%, performing well in both categories for precision,

recall and F1-score. LR, on the other hand, struggled with the
Threat category, with a recall of just 0.53 and an F1-score of
0.62, leading to an overall accuracy of 66% and an FWA of 65%.
For the DL models, Bi-LSTM and Bi-GRU both achieved an
accuracy of 88% and an FWA of 88%. They both had strong precision (91%) and F1-score (88%) for the “Threat” category and
balanced performance for “nonthreat” with an F1-score of 88%.
The bidirectional recurrent neural framework (Bi-RNF) model,
while performing reasonably well with a 75% accuracy, showed
a notable imbalance, with a very high recall for “Threat” (100%)

MURAD et al.: MULTILINGUAL CYBER THREAT DETECTION IN TWEETS/X USING ML, DL, AND LLM

1771

TABLE VII
PERFORMANCE COMPARISON OF DL AND LLM MODELS ON THE COMBINED MULTI-LINGUAL TWEET DATASET

Model

Params

Precision Per Category
in %

Recall Per Category
in %

F1-Score Per Category
in %

Th

Ne

Non-Th

Th

Ne

Non-Th

Th

Ne

Non-Th

Train
Accuracy

Validation
Accuracy

Train
Loss

Validation
Loss

DL

Bi-RNF
Bi-LSTM

66.31K
67.81K

0.46
0.70

0.00
0.76

0.00
0.76

1.00
0.77

0.00
0.73

0.00
0.71

0.63
0.77

0.00
0.74

0.00
0.70

0.46
0.97

0.44
0.74

1.05
0.11

1.07
1.4

LLM

XLM-RoBERTa
mT5

27.81M
49.606K

0.46
0.65

0.00
0.56

0.00
0.00

1.00
0.30

0.00
0.91

0.00
0.00

0.63
0.41

0.00
0.70

0.00
0.00

0.46
0.55

0.46
0.54

1.05
1.22

1.06
1.1

Note: Abbreviations: ML = machine learning, LLM = large language model, LR = logistic regression, DT = decision tree, RF = random forest, Bi-RNF = bidirectional
recurrent neural framework, Bi-LSTM = bidirectional long short-term memory, Th = threat, and Non-Th = nonthreat. Bold values are represent the best performance for each
column.

but a low recall for “nonthreat” (47%), leading to a lower FWA
of 73%. Overall, RF model stands out as the top performer
among the ML models. However, DL models, particularly BiLSTM and Bi-GRU, provided consistently strong and balanced
performance across metrics, demonstrating their capability to
handle the complex linguistic patterns.
Fig. 6 illustrates the ROC curves for three deep learning
models—RNN, LSTM, and GRU—used for Arabic tweet classification. The RNF model achieves an AUC of 0.85, indicating
a relatively strong classification performance, though it lags
behind the LSTM and GRU models, both of which have higher
AUC values of 0.95, suggesting superior discrimination ability.
The random chance baseline, represented by an AUC of 0.50,
serves as a reference point, highlighting that all three models
outperform random classification. This figure demonstrates the
effectiveness of LSTM and GRU models for Arabic tweet classification, with RNN still showing competitive performance but
with slightly lower accuracy.
E. Combined Data Analysis
Table VII illustrates the performance of DL and LLM techniques on the combined dataset, which integrates tweet data
from four languages: English, Chinese, Russian, and Arabic.
Among the DL models, Bi-LSTM demonstrated the best overall
performance. It achieved a train accuracy of 97% and a validation accuracy of 74%, with a relatively low train loss (0.11).
The model showed strong recall for all categories, particularly
threat (0.77) and neutral (0.73), as well as a high F1-score for
threat (0.77) and nonthreat (0.74). This indicates that Bi-LSTM
was highly effective at capturing sequential dependencies and
providing balanced classification across categories. In contrast,
Bi-RNF had difficulties in generalization, achieving a validation
accuracy of 44% and a validation loss of 1.07. The model exhibited poor performance in the neutral and nonthreat categories,
achieving an F1-score of 0.00 in both, indicating its deficiencies
in managing intricate multilingual datasets.
The XLM-RoBERTa provide mixed results. Though it excelled in recall for the threat detection (1.00), its performance
in the neutral and nonthreat categories was weaker, with an
F1-score of 0.00 for neutral and nonthreat. Both its train and
validation accuracy were 46%, and its validation loss (1.06)
indicates challenges in generalizing across the multilingual
dataset. These findings emphasize the capabilities of LLMs

for particular tasks while also highlighting the necessity for
additional fine-tuning and domain adaptation when addressing
varied data.
The mT5 model demonstrated balanced performance across
all categories. It achieved a precision of 0.65 for threat, 0.56 for
neutral, and 0.00 for nonthreat. The recall was notably strong
for neutral (0.91) and weaker for threat (0.30) and nonthreat
(0.00). The F1-scores were 0.41 for threat, 0.70 for neutral, and
0.00 for nonthreat. mT5 achieved a train accuracy of 55% and a
validation accuracy of 54%, with a validation loss of 1.1. These
results indicate that mT5 shows promise for neutral category
classification, although it struggles with threat and nonthreat
detection. The model’s performance suggests that while LLMs
can be effective for some tasks, further tuning and adaptation
are necessary for optimal performance across all categories.
V. CONCLUSION AND FUTURE WORK
This work presents a novel multilingual dataset, providing
as a significant resource for research on cyber tweet threat
identification. We performed an extensive examination of these
datasets, both separately and in a unified multilingual configuration. We employed three distinct model architectures—ML, DL,
and LLM—to evaluate the performance of different techniques.
Among the ML models, the RF algorithm exhibited superior
performance, showcasing its efficacy in managing structured
Twitter data. The Bi-LSTM architecture for DL models attained the best accuracy, surpassing all ML and DL models.
Significantly, Bi-LSTM surpassed LLMs in performance on
the integrated dataset, demonstrating its proficiency in capturing sequential patterns and contextual information adeptly.
Although we utilized the LLM architecture (XLM-RoBERTa)
for the integrated dataset, its performance was inferior to that of
Bi-LSTM, indicating the necessity for additional optimization
and fine-tuning of LLMs to fully realize their capabilities in
multilingual cyber tweet threat identification.
In the future, our efforts will concentrate on improving model
performance on integrated datasets by investigating more sophisticated LLM designs and utilizing fine-tuning techniques
specifically designed for multilingual data. Furthermore, we
intend to implement transfer learning techniques to modify
models pretrained on extensive datasets, enhancing their capacity to generalize to smaller and more heterogeneous datasets.
Additionally, we intend to broaden our research to encompass

1772

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 13, NO. 2, APRIL 2026

other languages and domain-specific Twitter datasets, facilitating a more thorough assessment of the suggested techniques’
robustness and flexibility.
DATA AVAILABILITY STATEMENT
The code of this article can be found in this link: https://
github.com/Mmurrad/Tweet-X-Data-Classification.
REFERENCES
[1] A. Sherin, I. J. SelvakumariJeya, and S. Deepa, “Enhanced aquila optimizer combined ensemble bi-LSTM-GRU with fuzzy emotion extractor
for tweet sentiment analysis and classification,” IEEE Access, vol. 12,
pp. 141932–141951, 2024.
[2] T. Elghazaly, A. Mahmoud, and H. A. Hefny, “Political sentiment
analysis using Twitter data,” in Proc. Int. Conf. Internet Things Cloud
Comput., 2016, pp. 1–5.
[3] J. Jia, L. Yang, Y. Wang, and A. Sang, “Hyper attack graph: Constructing
a hypergraph for cyber threat intelligence analysis,” Computers Secur.,
vol. 149, 2025, Art. no. 104194.
[4] F. K. Sufi, “A new computational method for quantification and analysis
of media bias in cybersecurity reporting,” IEEE Trans. Comput. Social
Syst., early access, May 5, 2025, doi: 10.1109/TCSS.2025.3560199.
[5] J. Lyu, A. Song, E. Seo, and G. Kim, “An exploratory analysis of the
DPRK cyber threat landscape using publicly available reports,” Int. J.
Inf. Secur., vol. 24, no. 1, 2025, Art. no. 66.
[6] R. Marinho and R. Holanda, “Automated emerging cyber threat identification and profiling based on natural language processing,” IEEE Access,
vol. 11, pp. 58915–58936, 2023.
[7] N. R. de Oliveira, D. S. Medeiros, and D. M. Mattos, “A sensitive
stylistic approach to identify fake news on social networking,” IEEE
Signal Process. Lett., vol. 27, pp. 1250–1254, 2020.
[8] B. Jamshidi, S. Hakak, and R. Lu, “A self-attention mechanism-based
model for early detection of fake news,” IEEE Trans. Comput. Social
Syst., early access, May 5, 2025, doi: 10.1109/TCSS.2025.3560199.
[9] R. Das, G. Karmakar, and J. Kamruzzaman, “How much I can rely
on you: Measuring trustworthiness of a Twitter user,” IEEE Trans.
Dependable Secure Comput., vol. 18, no. 2, pp. 949–966, Feb. 2019.
[10] J. Y. Nip and C. Sun, “Public diplomacy, propaganda, or what? China’s
communication practices in the South China sea dispute on Twitter,”
J. Public Diplomacy, vol. 2, no. 1, pp. 43–68, 2022.
[11] K. A. Uddin et al., “Machine learning-based screening solution for
covid-19 cases investigation: Socio-demographic and behavioral factors
analysis and covid-19 detection,” Human-Centric Intell. Syst., vol. 3,
no. 4, pp. 441–460, 2023.

[12] B. Amirshahi and S. Lahmiri, “Investigating the effectiveness of Twitter sentiment in cryptocurrency close price prediction by using deep
learning,” Expert Syst., vol. 42, no. 1, 2025, Art. no. e13428.
[13] S. Lu, L. Wei, and H. Liang, “Social media policies as social control
in the newsroom: A case study of the New York Times on Twitter,”
Journalism Stud., vol. 34, pp. 1–19, 2025.
[14] C. A. Ferguson and M. Chowdhury, “The phonemes of Bengali,”
Language, vol. 36, no. 1, pp. 22–59, 1960.
[15] R. Sánchez-Corcuera, A. Zubiaga, and A. Almeida, “Early detection
and prevention of malicious user behavior on Twitter using deep learning
techniques,” IEEE Trans. Comput. Social Syst., vol. 11, no. 5, pp. 6649–
6661, Oct. 2024.
[16] A. Sallah et al., “Fine-tuned understanding: Enhancing social bot detection with transformer-based classification,” IEEE Access, vol. 12, pp.
118250–118269, 2024.
[17] M. Rehan, M. S. I. Malik, and M. M. Jamjoom, “Fine-tuning transformer models using transfer learning for multilingual threatening text
identification,” IEEE Access, vol. 11, pp. 106503–106515, 2023.
[18] Central Intelligence Agency, “The World Factbookvol,” 2024. [Online].
Available: https://www.cia.gov/the-world-factbook/
[19] A. Tundis and M. Mühlhäuser, “A multi-language approach towards
the identification of suspicious users on social networks,” in Proc. Int.
Carnahan Conf. Secur. Technol. (ICCST), 2017, pp. 1–6,
[20] P. Chiril, F. Benamara Zitoune, V. Moriceau, M. Coulomb-Gully, and A.
Kumar, “Multilingual and multitarget hate speech detection in tweets,” in
Actes de la Conférence Sur le Traitement Automatique Des Langues Naturelles (TALN) PFIA in vol. II: Articles Courts, E. Morin, S. Rosset, and
P. Zweigenbaum, Eds. Toulouse, France: ATALA, 7, 2019, pp. 351–360.
[Online]. Available: https://aclanthology.org/2019.jeptalnrecital-court.21
[21] A. Hussein and A. A. Almazroi, “Multiclass classification for cyber
threats detection on twitter,” Comput. Mater. Continua, vol. 77, no. 3,
pp. 3853–3866, 2023. [Online]. Available: http://www.techscience.com/
cmc/v77n3/55024
[22] M. B. Kmainasi, A. E. Shahroor, M. Hasanain, S. R. Laskar, N. Hassan,
and F. Alam, “Llamalens: Specialized multilingual llm for analyzing
news and social media content,” 2024, arXiv:abs/15308. [Online]. Available: https://api.semanticscholar.org/CorpusID:273501813
[23] M. S. U. Miah, M. M. Kabir, T. B. Sarwar, M. Safran, S. Alfarhood,
and M. F. Mridha, “A multimodal approach to cross-lingual sentiment
analysis with ensemble of transformer and LLM,” Sci. Rep., vol. 14,
no. 1, Apr. 2024, Art. no. 9603.
[24] A. T. Hridi, S. Abdullah, M. A. Ibna Hasnath, R. H. Adiba, S. Proma,
and R. M. Rahman, “Identifying threats on social media to spot offensive
behavior,” in Proc. IEEE 12th Int. Conf. Intell. Syst. (IS), 2024, pp. 1–7.
[25] S. H. Kellogg, A Grammar of the Hindi Language., 1972.
[26] J. Vaid and A. Gupta, “Exploring word recognition in a semi-alphabetic
script: The case of devanagari,” Brain Lang., vol. 81, nos. 1–3, pp. 679–
690, 2002.
PAPER_TEXT
