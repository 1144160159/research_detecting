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
# [465] IAD-GPT: Advancing Visual Knowledge in Multimodal Large Language Model for Industrial Anomaly Detection
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
编号：465
题名：IAD-GPT: Advancing Visual Knowledge in Multimodal Large Language Model for Industrial Anomaly Detection
年份：2025
DOI：10.1109/tim.2025.3635334
来源：IEEE Transactions on Instrumentation and Measurement
PDF：paper/10.1109_TIM.2025.3635334.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：弱相关，分数 3
已有代码状态：候选不可访问；IADGPT

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\465.txt
- 原始字符数：57076
- 本次发送字符数：57076
- 是否截断：False

代码包：
- 仓库：IADGPT
  - URL：https://github.com/LiZeWen1225/IADGPT
  - 状态：failed
  - 本地目录：source\IADGPT
  - 顶层结构：
  - 主要语言：
  - README 标题：
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

5049512

IAD-GPT: Advancing Visual Knowledge
in Multimodal Large Language Model
for Industrial Anomaly Detection
Zewen Li , Zitong Yu , Senior Member, IEEE, Qilang Ye , Weicheng Xie , Member, IEEE, Wei Zhuo ,
and Linlin Shen , Senior Member, IEEE
Abstract—The robust causal capability of multimodal large
language models (MLLMs) holds the potential of detecting defective objects in industrial anomaly detection (IAD). However, most
traditional IAD methods lack the ability to provide multiturn
human–machine dialogs and detailed descriptions, such as the
color of objects, the shape of an anomaly, or specific types of
anomalies. At the same time, methods based on large pretrained
models have not fully stimulated the ability of large models
in anomaly detection tasks. In this article, we explore the
combination of rich text semantics with both image-level and
pixel-level information from images and propose IAD-GPT, a
novel paradigm based on MLLMs for IAD. We employ abnormal
prompt generator (APG) to generate detailed anomaly prompts
for specific objects. These specific prompts from the large
language model (LLM) are used to activate the detection and
segmentation functions of the pretrained visual-language model
(i.e., CLIP). To enhance the visual grounding ability of MLLMs,
we propose text-guided enhancer (TGE), wherein image features
interact with normal and abnormal text prompts to dynamically
select enhancement pathways, which enables language models
to focus on the specific aspects of visual data, enhancing their
ability to accurately interpret and respond to anomalies within
images. Moreover, we design a multimask fusion (MMF) module
Received 13 July 2025; revised 18 September 2025; accepted 7 October
2025. Date of publication 20 November 2025; date of current version
3 December 2025. This work was supported in part by the National Natural Science Foundation of China under Grant 62276170, Grant 62306061,
Grant 62576076, and Grant 82261138629; in part by the Open Fund of
National Engineering Laboratory for Big Data System Computing Technology under Grant SZU-BDSC-OF2024-02; in part by Guangdong Basic
and Applied Basic Research Foundation under Grant 2023A1515140037;
in part by Guangdong–Macau Science and Technology Innovation Joint
Foundation under Grant 2024A0505090003; in part by Guangdong Provincial
Key Laboratory under Grant 2023B1212060076; and in part by Shenzhen
Science and Technology Program under Grant JCYJ20240813141807010. The
Associate Editor coordinating the review process was Dr. Vincenzo Gallo.
(Corresponding authors: Zitong Yu; Linlin Shen.)
Zewen Li is with the School of Computer Science and Software Engineering, Shenzhen University, Shenzhen 518060, China, and also with the School
of Computing and Information Technology, Great Bay University, Dongguan
523000, China.
Zitong Yu is with the School of Computing and Information Technology,
Great Bay University, Dongguan 523000, China, and also with the Guangdong
Provincial Key Laboratory of Intelligent Information Processing and Shenzhen
Key Laboratory of Media Security, Shenzhen University, Shenzhen 518060,
China (e-mail: zitong.yu@ieee.org).
Qilang Ye is with the College of Computer Science, Nankai University,
Tianjin 300071, China.
Weicheng Xie and Linlin Shen are with the School of Computer Science
and Software Engineering, Shenzhen University, Shenzhen 518060, China
(e-mail: LLshen@szu.edu.cn).
Wei Zhuo is with the School of Artificial Intelligence, Guangdong
Provincial Key Laboratory of Intelligent Information Processing, and the
National Engineering Laboratory of Big Data System Computing Technology,
Shenzhen University, Shenzhen 518060, China.
Digital Object Identifier 10.1109/TIM.2025.3635334

to incorporate mask as expert knowledge, which enhances the
LLM’s perception of pixel-level anomalies. Extensive experiments
on MVTec-AD and VisA datasets demonstrate our state-of-the-art
performance on self-supervised and few-shot anomaly detection
and segmentation tasks, such as MVTec-AD and VisA datasets.
The codes are available at https://github.com/LiZeWen1225/IADGPT
Index Terms—Few-shot anomaly detection, multimodal large
language model (MLLM), self-supervised anomaly detection.

I. I NTRODUCTION

T

HE goal of industrial anomaly detection (IAD) tasks is to
identify defects in general objects that differ from normal
patterns, such as scratches on leather, damaged capsules,
and so on. The application of anomaly detection in industry
ensures the smooth progress of production processes and plays
a crucial role in monitoring, maintaining, and optimizing
industrial production processes.
The research on IAD tasks [1], [2], [3], [4], [5], [6],
[7] is constantly developing and making good progress.
Current mainstream methods [2], [3], [5], [6], [7] for
IAD include feature embedding-based methods [2], [3], [5]
and reconstruction-based methods [6], [7]. However, traditional IAD methods are currently limited to providing
anomaly detection and segmentation results for objects. These
approaches all rely on manually setting thresholds and lack
the capability to offer detailed insights into the nature and
specifics of detected defects. Meanwhile, image-text matching is often used to detect anomalies in large pretrained
model-based approaches like WinCLIP [8], which uses a
compositional prompt ensemble based on text templates using
generic descriptions of normal/abnormal as text. This has
been followed by other researchers in subsequent studies
[2], [9], [10], but the method does not fully activate the
capability of the large pretrained model. Filo [11], [12]
proposes an adaptively learned fine-grained description that
leverages domain-specific knowledge to introduce detailed
anomaly descriptions, replacing generic normal and abnormal
descriptions. Research progress on large language models
(LLMs) has been rapid recently. Due to their excellent language understanding and reasoning abilities after large-scale
data training, LLMs, such as ChatGPT [13] and Llama [14],
have proven their ability to perform translation, paraphrasing,
and instruction following tasks in zero sample tasks. In the
research of multimodal LLMs (MLLMs) [15], [16], [17], it

1557-9662 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

5049512

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

is found that other modal information can be mapped to the
feature space of LLMs through fine-tuning. LLM can also
understand the information contained in other modalities and
make explanations for it. AnomalyGPT [2] is the first to
introduce LLMs into IAD and proposes the task of anomaly
perception in MLLMs (APMLLMs). MLLMs for anomaly
detection eliminate the problem of manually setting thresholds
in traditional methods and make the results of IAD and localization more interpretable. However, AnomalyGPT simply
fine-tunes image features into LLM through a linear layer,
feeds predicted masks as expert knowledge into LLM, and
finally allows LLM to make judgments on image anomalies.
In this article, we propose IAD-GPT, which is designed
to enhance the efficiency and accuracy of anomaly detection
in industrial quality inspection. This method not only supports multiturn human–machine dialogs, allowing operators to
delve into potential anomalies through interactive questionand-answer (QA) sessions, but also leverages advanced LLMs
to directly analyze anomalies within images without relying
on preset threshold values for anomaly detection. Traditional
anomaly detection methods typically employ fixed threshold
standards: if the detected anomaly value exceeds a certain
threshold, the image is flagged as containing an anomaly;
otherwise, it is considered normal. In contrast, our approach
offers greater flexibility and adaptability by making precise
judgments based on specific contexts and using LLMs to
directly output intuitive results. Consequently, this method
holds significant potential for practical application in production environments, providing a novel perspective and solution
for industrial quality inspection.
Fig. 1 shows the difference between our IAD-GPT and
previous research. To address the issue of insufficient stimulation of large pretrained model segmentation ability in the
compositional prompt ensemble method [8], we employ APG
to extend and enrich the semantic content of text prompts.
These prompts are used to activate the detection and segmentation capabilities of a pretrained visual-language model,
i.e., CLIP [18]. Specifically, we leverage GPT’s existing
knowledge of most objects in the text domain and use a
QA format to generate possible anomaly categories for each
object class. These generated texts will serve as one of the
key factors in identifying anomalies. To enable the LLM to
fully perceive image information, we designed two modules
at the image level and pixel level, respectively: text-guided
enhancer (TGE) and multimask fusion (MMF). TGE enhances
the LLM’s anomaly perception capability at the image level by
interacting image features with normal/abnormal text prompts
to achieve dynamic path selection. Meanwhile, the MMF uses
the differences in image–text features across multiple levels to
further improve the LLM’s anomaly perception capability at
pixel level.
Our contributions are summarized as follows.
1) We introduce a novel framework named IAD-GPT,
via leveraging rich visual knowledge for IAD. Compared with previous IAD methods, IAD-GPT enhances
the capability to perceive anomalies beyond traditional
approaches.

Fig. 1. Comparison between our IAD-GPT, traditional IAD methods, and
AnomalyGPT. (a) Traditional methods use separate models for different
classes and provide anomaly scores only. (b) Unified methods manage to
accomplish anomaly detection for various classes with a unified framework.
(c) AnomalyGPT, based on the settings in (b), enhances the pixel-level visual
knowledge of MLLMs to perceive anomalies. (d) IAD-GPT provides GPTgenerated abnormal text to improve localization capabilities and enhances
image-level and pixel-level visual knowledge to achieve better anomaly
recognition by MLLMs.

2) We employ APG to generate detailed anomaly prompts
for specific objects. These prompts are utilized to
activate the detection and segmentation capabilities
of pretrained visual-language models via incorporating rich semantic information can significantly enhance
the performance of large pretrained models in IAD
tasks.
3) For the task of APMLLM, we design a multiscale feature
enhancement approach. At image level, we develop
TGE to dynamically select enhancement paths for image
features. At pixel level, we introduce MMF, which leverages differences in image–text features across multiple
levels to improve the LLM’s ability to perceive the
location of anomalies.
4) We achieve the state-of-the-art performance on MVTecAD and VisA for self-supervised/few-shot anomaly
detection and segmentation tasks. Compared to the baselines, IAD-GPT shows superior performance in anomaly
detection and localization on images within a selfsupervised learning setting, outperforming the few-shot
setting.
The remainder of this article is organized as follows. Section II reviews the related works. In Section III, we describe
the proposed approach in detail. Section IV presents the
ablation studies and comparison experiments with the state-of-

LI et al.: IAD-GPT: ADVANCING VISUAL KNOWLEDGE IN MLLM FOR INDUSTRIAL ANOMALY DETECTION

the-art methods. Finally, Section V provides the conclusions
and outlines directions for future work.
II. R ELATED W ORK
A. Industrial Anomaly Detection
IAD is mainly divided into reconstruction-based methods
and feature embedding-based methods.
Reconstruction-based methods [1], [4], [6], [7], [19], [20],
[21] rely on using only normal data when training the model,
learning the feature distribution of normal data to reconstruct
normal features. In the test phase, the trained model reconstructs the query data to obtain the normal feature of the
query image and then compares the difference between the
reconstructed image features and the original query image
features to achieve the detection and location of anomalies.
RealNet [7] uses a diffusion model with controllable strength
to synthesize abnormal data and training the reconstruction
network with abnormal data that are more similar to real-world
anomalies.
Feature embedding-based [3], [5], [22], [23], [24], [25],
[26], [27] methods often use networks trained on ImageNet
[28] to extract features from images. The representation of
abnormal areas in the image’s feature space is usually far
away from normal feature clusters, and anomaly detection
is achieved through the obvious distance between them in
the feature space. For example, PatchCore [5] constructs
a memory bank storing representative patch features from
normal images to detect anomalies in industrial settings without needing any examples of defects. It employs locally
aware patch features aggregated from intermediate feature
hierarchies of a pretrained network, ensuring spatial resolution and generality. To manage the size of the memory
bank and maintain performance, PatchCore applies a coreset
subsampling mechanism that selects a subset of features for
efficient nearest neighbor computations. However, networks
pretrained on general datasets often lack expertise in the field
of IAD. Migrating general pretrained networks to specific
IAD downstream tasks can make the model perform better.
In SimpleNet [3], a two-layer adapter is used to transfer the
features extracted from the pretrained network to the domain,
synthesize abnormal data in the feature space, and then train
a simple discriminator to achieve excellent anomaly detection
results.
Previous studies on IAD have mainly focused on “one
model for one class,” and there is little research on unified
anomaly detection models. UniAD [6] is a model specifically
used for unified anomaly detection. UniAD uses learnable
query and neighbor masking attention to prevent the model
from taking shortcuts, thereby building a more robust unified
anomaly detection model. DiAD [29] leverages advanced
diffusion models to enhance the reconstruction and localization
of anomalies across various classes. By incorporating learnable
query and neighbor masking attention mechanisms in UniAD,
DiAD prevents shortcut learning, thereby building a more
robust model. With the powerful capabilities of pretrained
visual-language models, such as CLIP, unified IAD models
have more research potential. WinCLIP [8] uses the characteristics of CLIP to align images and texts and uses CLIP

5049512

for IAD tasks. Specifically, WinCLIP calculates the similarity
between multiscale image features and text features representing normal/abnormal features, thereby realizing the detection
of abnormal areas. AnomalyGPT [2] uses ImageBind [30] to
train a simple decoder to align the feature space of images
and texts to achieve IAD. By employing generalized objectagnostic text prompt templates, AnomalyCLIP [10] learns
embeddings for normality and abnormality, further enhanced
by global and local context optimizations to better understand
anomaly semantics. AdaCLIP [9] enhances the performance
of the CLIP model in zero-shot anomaly detection (ZSAD) by
utilizing hybrid learnable prompts and emphasizes the importance of optimizing cues for detecting anomalies in individual
images. FiLo [11] enhances the perception of anomalies in
ZSAD tasks through fine-grained descriptions and high-quality
localization with position enhancement.
Previous studies utilize the powerful capabilities of large
pretrained models but do not fully stimulate the large pretrained models to locate anomalies at the pixel level. In this
article, based on LLM and the prior knowledge of the large
pretrained model, we generate possible abnormal attributes
for the categories that may be encountered in the unified
anomaly detection process. The specific prompts fully stimulate the capabilities of the large pretrained model, and we
have achieved excellent results.
B. Multimodal LLM
With the significant progress of LLMs, such as ChatGPT
and GPT-4 [13], many studies have attempted to explore other
modes based on LLMs, connecting pretrained visual-language
models of different modalities into end-to-end trainable models, also known as MLLMs. Due to the excellent language
understanding and reasoning abilities of LLMs after largescale data training, such as Qwen [31] and Llama [14],
they have demonstrated their ability to perform translation,
paraphrasing, and instruction following tasks in zero reference
tasks. Models, such as MiniGPT-4 [17], Llava [16], and
InstructBLIP [32], all employ fine-tuning techniques [33],
[34], [35] to construct MLLMs. MiniGPT-4 [17] uses frozen
Qformer and image encoder for image feature extraction based
on BLIP2 [36] and trains a simple linear layer to align visual
modalities into the LLM. Llava [16] is similar in architecture
to MiniGPT-4, but through more diverse data and fine-tuning
strategies at different stages, Llava is able to complete more
complex reasoning. InstructBLIP [32] has conducted a comprehensive and systematic study on the fine-tuning of visual
language instructions. The InstructBLIP model benefits from
adopting a balanced sampling strategy to synchronize learning
progress across datasets, enabling it to achieve excellent zero
sample performance on various visual language tasks. The
abovementioned multimodal big language models mainly use
visual encoders pretrained on roughly aligned image text pairs,
resulting in insufficient extraction and inference of visual
knowledge. Therefore, more research work [15], [37], [38],
[39], [40], [41] related to multimodal alignment is proposed.
To address this issue, LION [39] designed a multigranularity
fusion visual aggregator and used image labels as advanced
semantic visual information, enabling LION to have more

5049512

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 2. Overview of IAD-GPT. APG provides category specific text prompts for decoder. TGE and MMF provide image-level visual information and pixel-level
expert knowledge to LLMs, respectively.

advanced overall and fine-grained visual perception capabilities. In addition to provide visual information as an input
only to LLM, methods, such as LLaMA adapter [40], [42],
multimodal GPT, and Otter [15], also fuse multimodal information with intermediate features in LLMs to achieve the
understanding of multimodal information by LLMs. CAT [41],
[43] designed a clue aggregator to aggregate clues related to
problems in dynamic audio-visual scenes, targeting rich and
complex dynamic audio-visual compositions. This enriches
the detailed knowledge required for learning, enabling CAT
to learn clues related to problems and directly engage in
action-based audio-visual reasoning. CAT outperforms other
MLLMs in multimodal tasks, especially audio-visual question
answering tasks.
MLLMs are trained on large-scale general datasets, which
limits their capability to specifically perceive anomalies. To
overcome this challenge, we introduce a method that utilizes
image-level visual information and pixel-level expert knowledge. By integrating these rich sources of information, our
approach significantly enhances the ability of MLLMs to
perceive anomalies, thereby improving their performance in
the APMLLM task.
III. M ETHODOLOGY
Fig. 2 illustrates the architecture of IAD-GPT. Given a query
image x ∈ RH×W×C , the visual features Fimg ∈ R1×C1 extracted
by the image encoder are passed through TGE to obtain the
image embedding Eimg ∈ R1×Cemb , which is then fed into the
LLM.
Our method is experimentally validated in two distinct
settings: a self-supervised setting, where the model learns from
data with only normal samples, and a few-shot setting, which
challenges the model to generalize from a very limited number
of normal samples. In self-supervised setting, the patch-level
features extracted by intermediate layers of image encoder are
fed into the decoder together with text features that expand

anomaly prompts with APG to generate pixel-level anomaly
localization results. In few-shot setting, the patch-level features
from normal samples are stored in memory banks and the
localization result can be obtained by calculating the distance
between query patches and their most similar counterparts in
the memory bank. The localization result is subsequently transformed into prompt embeddings Efusion ∈ RL1 ×Cemb through the
MMF module, serving as a part of the LLM input. The LLM
detects anomalies and identifies their locations by leveraging
the image input Eimg , prompt embedding Efusion , and userprovided text, thereby generating a response for the user.
A. Abnormal Prompt Generator
We design abnormal prompt generator (APG) to expand
anomaly prompts to achieve more powerful segmentation
capabilities. Specifically, we first prompt the LLM with the
query: “describe in a paragraph what an abnormal image
of {Co } may looks like?” with the given class Co , and we
extract potential abnormal attributes ATTRa from the answer
generated by LLM. ATTRa = {k1 , k2 , . . . , ki } includes several
potential abnormal keywords ki for Co . For each potential
abnormal keyword ki , we continue the QA session to generate
a class-keyword abnormal prompt T ki . T apg = {T k1 , T k2 , . . . , T ki }
contain all potential class-keyword abnormal prompts generated by multiple rounds of dialog. For example, for leather
objects, LLM is used to answer the relevant abnormal categories, including irregular texture, tears, cracks, and so on.
Then, LLM is asked to generate corresponding text for each
abnormal category, such as “Cracks: An abnormal leather may
have cracks in the surface, indicating dryness, age, or poor
quality.”
Fig. 3 shows the process of using APG to generate specific anomaly categories for leather and converting them
into text prompts. We not only simply expand the anomaly
categories into fixed format text but also let the LLM infer
the characteristics of the object based on its own and generate

LI et al.: IAD-GPT: ADVANCING VISUAL KNOWLEDGE IN MLLM FOR INDUSTRIAL ANOMALY DETECTION

5049512

B. Text-Guided Enhancer
PandaGPT [44] uses a simple linear layer to align the feature
space of the image encoder and LLM. However, PandaGPT
has not been trained for data in the field of industrial
anomalies, resulting in PandaGPT being unable to identify
anomalies during IAD. Inspired by the mixture-of-experts
(MoE) architecture [45], we propose the text-guided enhancer
(TGE) module, in which a similar structure is designed to
enhance image-level features. However, unlike the traditional
MoE approach that employs a router, we dynamically control
feature enhancement for each individual image through the
interaction between Fimg and Fwin


We = Softmax Attn Fimg Linear (Fwin )T
(3)

Fig. 3. Example of APG for leather. We improve the stability of LLMgenerated prompts by designing an QA session and providing illustrative
examples.

where Fwin is the text embedding extracted by text encoder
from T win . We use a linear layer to align Fwin and image-level
image feature Fimg . The enhanced image-level feature of Fimg
after self-attention is used as expert input, We is used as the
weight of expert aggregation, and the result Eimg ∈ R1×Cemb
after expert aggregation is fed to LLM as image-level feature
input
L2
X

(4)
Eimg =
Wei × Experti Fimg
i=0

appropriate text prompts. WinCLIP [8] introduces a twoclass design method in text prompts to help CLIP locate
the abnormal region, which categorizes the text prompts into
normal prompts T n and abnormal prompts T a , and we define
text prompts similar to WinCLIP as T win = {T n , T a }. When
training the image decoder, we use T win and T apg as our text
prompts T text = {T win , T apg }, and we then extract the text
embeddings Ftext ∈ RL2 ×C2 using the pretrained CLIP model
and align the patch-level image features Fpatch ∈ RH×W×C3
with the text embeddings Ftext through a simple linear layer.
The anomaly score is calculated by the similarity between the
patch feature Fpatch and text embeddings Ftext . The localization
result M ∈ RH×W can be obtained as follows:
!
4
X
 T 
l
(1)
M = Unsample
Softmax Linear Fpatch Ftext
l=1

where l represents the number of layers. Similar to AnomalyGPT, we do not specifically select the image features of
different layers for mask generation. The reason is that image
features have different effects on anomaly extraction in shallow
and deep layers. In previous studies, it has been found that
fusing shallow and deep features helps us generate masks
more accurately. For multilayer masks, we sum them up and
calculate the average to obtain the final predicted mask, which
is then achieved through upsampling.
For few-shot IAD, we utilize the same image encoder to
extract patch-level features from normal samples and store
them in memory banks Bl ∈ RN×C3 . For patch-level features
F lpatch ∈ RH×W×C3 , the IAD localization results under the fewshot setting can be expressed as follows:
!
4 


X
l
lT
M = Unsample
1 − Max Fpatch · B
.
(2)
l=1

where L2 indicates the number of categories of T win , and
Experti denotes the ith expert. Our experts are composed of a
combination of an attention block and a feed-forward neural
network.
C. Multimask Fusion
To utilize the masks generated by the decoder as expert
knowledge and maintain semantic consistency between the
LLM and the decoder output, we introduce a MMF method,
which converts the localization results Mi (i = 1, 2, 3, 4) into a
prompt embedding Efusion . As shown in the left side of Fig. 2,
MMF consists of multiple convolutional neural networks and
trainable base prompt embeddings Ebase ∈ RL3 ×Cemb . Our
convolutional neural network is designed to consist of multiple
general convolutional layers, followed by depthwise separable
convolutions. We refer to this network as mask convolution
block (MCB). The MCB converts localization result Mi into
prompt embeddings Edeci ∈ RL1 ×C3 and then concatenates
multiple Edeci in the channel dimension to obtain an embedding Efusion ∈ RL1 ×Cemb that fuses multilayer information.
Expert knowledge Eexpert = {Efusion , Ebase } ∈ R(L1 +L3 )×Cemb
concatenates Ebase and Efusion in the length dimension and
ultimately inputs them into the LLM
Edeci = MCB (Mi )
Efusion = Concat

˚


4
Edeci i=1 .

(5)
(6)

D. Data for Training
We use the NSA [46] method for training. The NSA method
advances the CutPaste [47] technique by integrating the Poisson image editing [48] approach to mitigate the discontinuity

5049512

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 4. Visualization comparison of anomaly image generation results between NSA and CutPaste methods. Red box indicates abnormal area.

caused by pasting image segments. In the domain of IAD,
the CutPaste [47] is a prevalent method used for generating
simulated anomaly images. This approach involves randomly
cropping a block region from an image and pasting it onto
a random location within the same or another image, thereby
creating a simulated anomalous portion. While this method
significantly enhances the performance of IAD models, it
often results in noticeable discontinuities due to the abrupt
insertion. To address these visual inconsistencies, the Poisson
image editing method [48] seamlessly integrates an object
from one image into another by solving Poisson partial
differential equations, thereby reducing visible artifacts from
direct pasting. Fig. 4 presents a visual comparison between the
image results generated by the NSA method and the original
CutPaste method, clearly illustrating the improvement of the
NSA method in mitigating discontinuities.
In order to prevent overfitting of LLM, we use the LLM
to enrich our target prompt before training LLM. For normal images, our response is designed as “No, there are no
abnormalities in the image.” For abnormal images, we first
generate different answer templates through LLM and define
the position information of anomalies as position. Every time
training data are generated, one of the answer templates will
be selected and the position will be filled in as the answer, such
as “yes, the anomaly is visible at {position}” or “yes, there is
an anomaly in the image; it’s at the {position}”, and so on.
For position information of anomalies position, we divide the
image into a grid of 3×3 distinct regions to facilitate the LLM
to answer the positions of anomalies, as shown in Fig. 5.
E. Loss Functions
To train our IAD-GPT, we primarily employed three loss
functions: cross-entropy loss, focal loss [49], and dice loss
[50]. The latter two are primarily utilized to enhance the pixellevel localization accuracy of the decoder. We only use crossentropy loss when not training the decoder and use all three
losses when training the decoder.
Cross-entropy loss is a widely used loss function for training classification models. It quantifies the difference between
the predicted probability distribution and the true distribution
(often represented as one-hot encoded labels). The LLM is

Fig. 5. Illustration of generating abnormal prompts and a 3×3 grid of images
for LLM to answer abnormal locations. We first input the answer template
into LLM to generate diversified answers to improve the diversity and stability
of model training and then randomly select a template and fill the location
information of the generated abnormal image into the answer.

trained with cross-entropy loss, which quantifies the difference
between the text sequence generated by the model and the
target text sequence
Lc = −

n
X

yilog (pi )

(7)

i=1

where n is the number of tokens, yi is the true label for token
i, and pi is the predicted probability for token i.
Focal Loss is an optimized loss function specifically tailored for addressing class imbalance in classification tasks,
particularly within the realm of object detection. The loss function incorporates a modulating factor (γ) that tunes down the
effect of well-classified instances on the total loss, alongside an

LI et al.: IAD-GPT: ADVANCING VISUAL KNOWLEDGE IN MLLM FOR INDUSTRIAL ANOMALY DETECTION

5049512

IV. E XPERIMENT
A. Datasets

Fig. 6. Training strategy of IAD-GPT.

optional balancing factor (α) to further adjust for the disparity
between classes. By doing so, focal loss enhances the model’s
recall on minority classes while maintaining precision
n

1X
αt (1 − pt )γ log (pt )
Lf = −
n

(8)

i=1

where n = H × W represents the total number of pixels and pt
is the probability of belonging to the true category predicted
by the model. In this article, pt is the probability of being
predicted as an anomaly.
Dice loss is a performance metric turned loss function
widely used in segmentation tasks to evaluate and optimize
the overlap between the predicted segmentation mask and the
ground truth. It measures the similarity between two samples
by calculating the ratio of twice the area of intersection to
the sum of the areas of the two samples. The function is
particularly effective in scenarios with class imbalance due
to its focus on the proportion of correctly predicted pixels
relative to the total number of pixels in the target class. By
minimizing dice loss during training, models are encouraged
to produce segmentation outputs that have high spatial overlap
with the true object boundaries, making it especially valuable
for medical image analysis and other applications requiring
precise boundary delineation
P
2 ni=1 pt (1 − pt )
(9)
Ld = − Pn 2 Pn
2
i=1 pt +
i=1 (1 − pt )
where pt represents the probability of being predicted as an
anomaly
Ltotal = λc · Lc + λ f · L f + λd · Ld
(10)
where λ f and λd are set to 1 in stage 2 to supervise the training
of the decoder. In all other stages, these coefficients are set to
0. In contrast, the cross-entropy loss is utilized throughout all
training stages, and accordingly, λc is set to 1 across all stages.
This staged learning strategy enables the model to focus on
different components of the loss function at each stage, leading
to a more stable and effective training process. Further details
of this training protocol are illustrated in Fig. 6.

Our experiments are based on MVTec-AD [51] and VisA
[52] datasets. Both benchmarks have diverse subsets of different objects, e.g., capsules and leather. In the realm of IAD,
MVTec-AD stands out as a widely recognized benchmark. It
contains 15 distinct categories, with a total of 3629 training
images and 1725 testing images. The images within this
dataset exhibit resolutions ranging from 700 × 700 to 1024 ×
1024 pixels, offering a diverse array of visual data for model
training. The recently introduced VisA dataset adds to the
resources available for IAD research. Spanning 12 categories,
it features 9621 normal images and 1200 anomalous images,
with an approximate resolution of 1500 × 1000 pixels.
Following previous IAD methodologies, only the normal
data from these two datasets are utilized during the training
phase. To address the limitation of insufficient anomalous
data and enable effective model training, synthetic anomalous
images are generated and incorporated into the training process.
B. Evaluation Metrics
Following traditional IAD methods, we employ the area
under the receiver operating characteristic (AUROC) as our
evaluation metric for both detection and localization, which
is expressed as image-level AUROC (I-AUROC) and pixellevel AUROC (P-AUROC). With the deployment of LLM, the
existing methods allow determining the presence of anomalies
without the need to manually set thresholds. We utilize imagelevel accuracy to evaluate the performance of our IAD-GPT.
C. Implementation Details
We use ImageBind-Huge [30] as a frozen image encoder
to extract image features and Vicuna-7B [54] as LLM for
reasoning, connect them through with TGE. Then, we initialize
our IAD-GPT using pretrained parameters from PandaGPT
[44]. We layered the training into three stages, which are stage
one to train TGE, stage two to train visual-guided decoder
and MMF, and stage three to train TGE and MMF jointly. At
different training stages, we used the same 50 epochs on two
V100 GPUs with a learning rate of 0.0005 and a batch size
of 16.
Our training strategy is shown in Fig. 6. In the first stage,
we do not input the mask information generated by the
expert model but only train the model to better recognize the
anomalous features at the image level. In the second stage, we
freeze TGE on the basis of the first stage and then train visualguided decoder and MMF, which initially aligns the pixel-level
anomalous features of the mask to the feature space of the
LLM. Finally, in the third stage, we freeze the visual-guided
decoder and jointly train TGE and MMF to achieve a better
understanding of image-level and pixel-level anomalies in the
LLM.
We initialize the image as 224 × 224 and similar to AnomalyGPT [2], without specifying a particular level select the
intermediate features of the 8th, 16th, 24th, and 32th layers

5049512

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

TABLE I
Q UANTITATIVE R ESULTS (I MAGE -L EVEL AUROC /P IXEL -L EVEL AUROC /ACCURACY ) OF S ELF -S UPERVISED A NOMALY D ETECTION TASKS ON M VTEC A D DATASET. W E U SE B OLD AND U NDERLINE IN THE AVERAGE I NDEX TO I NDICATE THE B EST AND S UBOPTIMAL R ESULTS , R ESPECTIVELY

from the image encoder as input to the decoder. Linear warmup and a one-cycle cosine learning rate decay strategy are
applied. For image augmentation, the NSA [46] method is
adopted, with key parameters configured as follows: Poisson
image editing is implemented in normal clone mode to achieve
smooth edge fusion between synthetic anomalous patches and
the original image background; pixel values at the edges of
patch masks are set to zero to suppress visible fusion artifacts;
and the fusion center is defined as the geometric midpoint
of the target pasting region in the destination image, ensuring alignment between the anomalous patch and surrounding
image content. We perform alternating training using both the
pretraining data of PandaGPT and our anomaly image-text
data. Only TGE, visual-guided decoder, and MMF perform
parameter updates at the corresponding stage, while the rest
of the parameters remain frozen.
D. Self-Supervised IAD
In the setting of self-supervised training with a large number
of normal samples, given that our method trains a single model
on samples from all classes within a dataset, we selected
AnomalyGPT [2], which is trained under the same setup, as a
baseline for comparison. Additionally, we compare our model
with Draem [19], PatchCore [5], SimpleNet [3], UniAD [6],
and DiAD [29] using the same unified setting. The results
in the MVTec-AD dataset are presented in Table I. Our proposed method, IAD-GPT, demonstrates superior performance
compared to the existing methods in most categories. We
have achieved the state-of-the-art performance across multiple
metrics. For Image-AUROC and Pixel-AUROC, we achieve
improvements of 0.3% and 4.2%, respectively, compared
to AnomalyGPT. In the task of anomaly segmentation, we
demonstrated a significant improvement over AnomalyGPT,

demonstrating that APG is effective in promoting large pretrained models to perceive anomalous features at the patch
level. Among multiple multicategory anomaly detection models, our anomaly detection and localization capabilities are the
best, reaching 97.7% and 97.3%. In the task of APMLLM, our
accuracy rate reaches 94.8%, representing a relative improvement of 1.5% compared to AnomalyGPT.
E. Few-Shot IAD
We compare our work with prior few-shot IAD methods,
selecting SPADE [53], PatchCore [5], WinCLIP [8], and
AnomalyGPT as the baselines. The results are presented in
Table II. Across both datasets, our method performs competitively in the IAD and APMLLM tasks and notably outperforms
AnomalyGPT in the setting of 1-shot and 2-shot and achieves
the state-of-the-art performance. Compared to AnomalyGPT,
our method achieves better performance on Mvtec-AD and
VisA for most metrics. In the one-shot and two-shot setting of the Mvtec-AD, the accuracy of IAD-GPT is 89.5%
±1.2% and 79.1% ±0.9%, which improves by 3.4% and 1.7%
over AnomalyGPT. In other settings, IAD-GPT also achieves
competitive results. This indicates that our multiscale feature
enhancement approach effectively improves the LLM’s ability
to perceive anomalies.
In the few-shot in-context learning setting, the localization
performance of the model is slightly lower than that of the
self-supervised setting due to limited normal references. Our
proposed use of TGE and MMF to provide multiscale anomaly
perception for LLMs, which promotes the performance of
LLMs in the APMLLM task. Notably, AnomalyGPT exhibits
weaker anomaly localization capabilities in a self-supervised
setting compared to the abilities of the model in a fewshot learning setting without training. This indicates that

LI et al.: IAD-GPT: ADVANCING VISUAL KNOWLEDGE IN MLLM FOR INDUSTRIAL ANOMALY DETECTION

5049512

TABLE II
F EW-S HOT IAD R ESULTS ON M VTEC -A D AND V ISA DATASETS . R ESULTS A RE L ISTED AS THE AVERAGE OF F IVE RUNS AND THE B EST-P ERFORMING
M ETHOD I S IN B OLD . T HE R ESULTS FOR S PADE , PATCHCORE , AND W INCLIP A RE R EPORTED F ROM [8]

Fig. 7. Qualitative evaluation of IAD-GPT on MVTec-AD. Input images from different categories (first row), corresponding ground truth annotations (second
row), anomaly detection results predicted by IAD-GPT (third row), and prediction results using heatmaps (fourth row).

AnomalyGPT does not fully leverage the capabilities of large
pretrained models. However, our proposed APG effectively
compensates for this shortcoming. IAD-GPT achieves an
anomaly localization performance of 97.3% P-AUROC in the
self-supervised setting, surpassing the best result of 96.2% in
the few-shot setting.
F. Qualitative Examples
The visualization results of IAD-GPT on the MVTec-AD
dataset can be seen in Fig. 7. It can be seen that IADGPT effectively identifies anomalies of different categories and
has good perceptual ability in pixel-level anomaly localization. Regardless of the scale of the anomaly, whether it be
large scratches or small pokes, IAD-GPT demonstrates high

accuracy in both detection and localization. Fig. 8 illustrates
the performance of our IAD-GPT in self-supervised anomaly
detection. Our model can not only indicate the existence
of anomalies, accurately locate their locations, and provide
pixel-level localization results but also answer the specific
categories of anomalies that may exist, which is a capability
that AnomalyGPT does not possess. Users can engage in
multiturn conversations related to the image content, including
but not limited to asking IAD-GPT whether the image contains
anomalies or requesting specific descriptions about the image.
G. Ablation Study
To evaluate the effectiveness of each proposed module,
extensive ablation experiments were conducted on the MVTec-

5049512

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

TABLE VI
A BLATION OF T RAIN STRATEGY

TABLE VII
C OMPARISON OF I MAGE AUGMENTATION M ETHODS

Fig. 8. Qualitative example of IAD-GPT on MVTec-AD. Anomaly categories
are computing from the similarity between Fimg and Fapg .
TABLE III
A BLATION OF TGE IN D IFFERENT FRAMEWORKS . ACC . D ENOTES ACCU RACY (%)

TABLE IV
A BLATION S TUDY ON THE I NTEGRATION OF E XPERT K NOWLEDGE I NTO
LLM

TABLE V
C OMPARISON OF P ROMPT L EARNER F ROM A NOMALY GPT AND MMF
F ROM IAD-GPT ON T HROUGHPUT ( IMGS / S ), PARAMETERS (M),
FLOP S (G), AND ACCURACY (%)

AD dataset. Our study primarily focuses on three key aspects:
the TGE, the integration of expert knowledge, and the multistage training strategy. The main results are summarized in
Tables III–VII. All analyses are based on self-supervised training and testing protocols applied to the MVTec-AD dataset.

1) Impact of TGE: To demonstrate the effectiveness of the
TGE in enhancing visual information, we train the model
for anomaly perception using only the TGE. As shown in
Table III, compared to PandaGPT, our approach achieves a
performance improvement of 10.1%. To further validate the
applicability of the TGE across different frameworks, we also
conducted ablation studies on AnomalyGPT. The experimental
results confirm that the TGE consistently improves the model’s
ability to perceive anomalies at the image level, thereby
enabling better performance on APMLLM task in both IADGPT and AnomalyGPT.
2) Impact of Expert Knowledge: To demonstrate the impact
of the expert knowledge incorporated via APG and MMF, we
compare the performance of AnomalyGPT with our method
after integrating expert knowledge. As shown in Table IV,
APG consistently improves both anomaly detection and localization across different frameworks, indicating that APG is
effective in promoting large pretrained models to perceive
anomalous features at the patch level.
To enable the LLM to better comprehend and utilize the
expert knowledge, we propose the MMF module. Unlike the
prompt learner used in AnomalyGPT, MMF fully exploits
multilevel expert knowledge during the prompting process.
In Table V, we compare the efficiency of MMF and the
prompt learner. MMF achieves superior performance in terms
of throughput and parameter count, reaching 114.2 imgs/s
and 10.2M parameters, compared to 97.8 imgs/s and 107.4M
parameters for the prompt learner. However, due to the additional overhead of processing multilayer expert knowledge,
MMF incurs a higher computational cost, as reflected by
its significantly larger FLOPs. In terms of accuracy, IADGPT achieves 94.8%, outperforming AnomalyGPT’s 93.3%,
demonstrating the effectiveness of our design.
3) Impact of Training Strategy: To evaluate the effectiveness of the multistage training strategy, we present its
impact on IAD-GPT in Table VI. Without multistage training, our method still outperforms AnomalyGPT across all
evaluation metrics. The incorporation of multistage training
further enhances IAD-GPT’s ability to perceive anomalies
in APMLLM task, leading to improved performance in both
detection and localization.

LI et al.: IAD-GPT: ADVANCING VISUAL KNOWLEDGE IN MLLM FOR INDUSTRIAL ANOMALY DETECTION

4) Impact of Data Augmentation: We have supplemented
a more detailed comparative ablation experiment focusing
on data augmentation methods, specifically evaluating three
scenarios: training with only the NSA-based augmentation,
training with only the CutPaste augmentation, and training
using a combination of NSA and CutPaste. All experiments
strictly followed the experimental setup in Section IV-C. For
the combination scheme, we randomly selected either NSA
or CutPaste to synthesize anomalous images in each training
iteration before feeding them into the model.
The experimental results in Table VII show that the NSAbased augmentation achieves the best performance in both
anomaly detection and localization tasks. We believe this is
attributed to its ability to generate more realistic anomalous
regions with smoother edge transitions, which helps the model
learn more discriminative normal–abnormal feature differences.
V. C ONCLUSION
In this study, we introduce IAD-GPT, an innovative framework for IAD. IAD-GPT leverages the advanced capabilities
of MLLMs and integrates multiscale visual information
through TGE and MMF. TGE effectively enhances the alignment between image-level visual information and LLMs and
improves LLM’s perception of anomalies by dynamically
selecting enhancement paths for image features. Meanwhile,
the MMF module integrates multilevel localization results as
visual expert knowledge for LLM to enhance its pixel-level
anomaly perception. Our experiments on benchmark datasets,
such as MVTec-AD and VisA, highlight the superior performance of IAD-GPT. IAD-GPT achieves better performance in
APMLLM task by leveraging multiscale visual information.
Furthermore, it fully enhances the capabilities of large pretrained models based on APG to detect and localize image
anomalies. We have improved our performance in anomaly
detection and localization compared to the baseline, and due
to the excellent performance of APG, we have achieved
better anomaly localization performance in the self-supervised
setting than in the few-shot in-context learning setting.
IAD-GPT provides a more comprehensive and robust LLMbased solution for industrial applications. Beyond its technical
contributions, this work also underscores the broader potential
of leveraging MLLMs in industrial domains, opening new
avenues for interactive and explainable artificial intelligence
solutions. Future work will explore the extension of IADGPT to other fields, such as medical anomaly detection
and camouflage object detection. In addition, efforts will be
made to improve its adaptability to more complex industrial
scenarios.
R EFERENCES
[1]

[2]

D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1705–1714.
Z. Gu, B. Zhu, G. Zhu, Y. Chen, M. Tang, and J. Wang, “AnomalyGPT:
Detecting industrial anomalies using large vision-language models,” in
Proc. AAAI Conf. Artif. Intell., 2024, vol. 38, no. 3, pp. 1932–1940.

[3]

5049512

Z. Liu, Y. Zhou, Y. Xu, and Z. Wang, “SimpleNet: A simple network
for image anomaly detection and localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023, pp. 20402–20411.
[4] N.-C. Ristea et al., “Self-supervised predictive convolutional attentive
block for anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2022, pp. 13576–13586.
[5] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler,
“Towards total recall in industrial anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022,
pp. 14298–14308.
[6] Z. You et al., “A unified model for multi-class anomaly detection,” in
Proc. Adv. Neural Inf. Process. Syst., 2022, pp. 4571–4584.
[7] X. Zhang, M. Xu, and X. Zhou, “RealNet: A feature selection network with realistic synthetic anomaly for anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2024,
pp. 16699–16708.
[8] J. Jeong, Y. Zou, T. Kim, D. Zhang, A. Ravichandran, and O. Dabeer,
“WinCLIP: Zero-/few-shot anomaly classification and segmentation,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2023, pp. 19606–19616.
[9] Y. Cao, J. Zhang, L. Frittoli, Y. Cheng, W. Shen, and G. Boracchi,
“AdaCLIP: Adapting CLIP with hybrid learnable prompts for zero-shot
anomaly detection,” in Proc. Eur. Conf. Comput. Vis., 2024, pp. 55–72.
[10] Q. Zhou, G. Pang, Y. Tian, S. He, and J. Chen, “AnomalyCLIP: Objectagnostic prompt learning for zero-shot anomaly detection,” in Proc. 12th
Int. Conf. Learn. Represent., 2023.
[11] Z. Gu et al., “FiLo: Zero-shot anomaly detection by fine-grained
description and high-quality localization,” in Proc. 32nd ACM Int. Conf.
Multimedia, Oct. 2024, pp. 2041–2049.
[12] Z. Gu, B. Zhu, G. Zhu, Y. Chen, M. Tang, and J. Wang, “FiLo++:
Zero-/few-shot anomaly detection by fused fine-grained descriptions and
deformable localization,” 2025, arXiv:2501.10067.
[13] J. Achiam et al., “GPT-4 technical report,” 2023, arXiv:2303.08774.
[14] H. Touvron et al., “LLaMA: Open and efficient foundation language
models,” 2023, arXiv:2302.13971.
[15] B. Li et al., “MIMIC-IT: Multi-modal in-context instruction tuning,”
2023, arXiv:2306.05425.
[16] H. Liu, C. Li, Q. Wu, and Y. J. Lee, “Visual instruction tuning,” in Proc.
Adv. Neural Inf. Process. Syst., 2023.
[17] D. Zhu, J. Chen, X. Shen, X. Li, and M. Elhoseiny, “MiniGPT-4:
Enhancing vision-language understanding with advanced large language
models,” 2023, arXiv:2304.10592.
[18] A. Radford et al., “Learning transferable visual models from natural
language supervision,” in Proc. Int. Conf. Mach. Learn., vol. 139, 2021,
pp. 8748–8763.
[19] V. Zavrtanik, M. Kristan, and D. Skočaj, “Draem—A discriminatively
trained reconstruction embedding for surface anomaly detection,” in
Proc. IEEE/CVF Int. Conf. Comput. Vis., Jun. 2021, pp. 8330–8339.
[20] Y. Cao, H. Yao, W. Luo, and W. Shen, “VarAD: Lightweight highresolution image anomaly detection via visual autoregressive modeling,”
IEEE Trans. Ind. Informat., vol. 21, no. 4, pp. 3246–3255, Apr. 2025.
[21] V. Zavrtanik, M. Kristan, and D. Skočaj, “Reconstruction by inpainting
for visual anomaly detection,” Pattern Recognit., vol. 112, Apr. 2021,
Art. no. 107706.
[22] Y. Liang, Z. Hu, J. Huang, D. Di, A. Su, and L. Fan, “ToCoAD: Twostage contrastive learning for industrial anomaly detection,” IEEE Trans.
Instrum. Meas., vol. 74, pp. 1–9, 2025.
[23] S. Xie, X. Wu, and M. Yu Wang, “Semi-patchcore: A novel two-staged
method for semi-supervised anomaly detection and localization,” IEEE
Trans. Instrum. Meas., vol. 74, pp. 1–12, 2025.
[24] T. Defard, A. Setkov, A. Loesch, and R. Audigier, “PaDiM: A patch distribution modeling framework for anomaly detection and localization,”
in Proc. Int. Conf. Pattern Recognit., 2021, pp. 475–489.
[25] Y. Zhai et al., “Bidirectional feature pyramid Siamese anomaly detection
network with cellular anomaly generation for container marking,” IEEE
Trans. Instrum. Meas., vol. 74, pp. 1–17, 2025.
[26] W. Zhang, H. Shi, J. Qiu, Z. Yu, and J. Li, “EdgeAD: Unsupervised
learning model based on prior knowledge enhanced image anomaly
detection of heavy railway freight cars,” IEEE Trans. Instrum. Meas.,
vol. 74, pp. 1–12, 2025.
[27] Y. Zhou, Z. Huang, D. Zeng, Y. Qu, and Z. Wu, “Dual-branch knowledge distillation via residual features aggregation module for anomaly
segmentation,” IEEE Trans. Instrum. Meas., vol. 74, pp. 1–11, 2025.
[28] J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei, “ImageNet:
A large-scale hierarchical image database,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit., Jun. 2009, pp. 248–255.

5049512

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

[29] H. He et al., “A diffusion-based framework for multi-class anomaly
detection,” in Proc. AAAI Conf. Artif. Intell., Mar. 2024, pp. 8472–8480.
[30] R. Girdhar et al., “ImageBind one embedding space to bind them all,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2023, pp. 15180–15190.
[31] J. Bai et al., “Qwen technical report,” 2023, arXiv:2309.16609.
[32] W. Dai et al., “InstructBLIP: Towards general-purpose vision-language
models with instruction tuning,” 2023, arXiv:2305.06500.
[33] J. E. Hu et al., “LoRA: Low-rank adaptation of large language models,”
in Proc. ICLR, 2021, p. 3.
[34] R. Zhang, J. Han, C. Liu, A. Zhou, P. Lu, Y. Qiao, H. Li, and P. Gao,
“LLaMA-adapter: Efficient fine-tuning of large language models with
zero-initialized attention,” in Proc. 12th Int. Conf. Learn. Represent.,
2024.
[35] R. Cai, Y. Cui, Z. Yu, X. Lin, C. Chen, and A. Kot, “Rehearsal-free and
efficient continual learning for cross-domain face anti-spoofing,” IEEE
Trans. Pattern Anal. Mach. Intell., vol. 47, no. 12, pp. 11348–11365,
Dec. 2025.
[36] J. Li, D. Li, S. Savarese, and S. C. H. Hoi, “BLIP-2: Bootstrapping language-image pre-training with frozen image encoders and
large language models,” in Proc. Int. Conf. Mach. Learn., 2023,
pp. 19730–19742.
[37] X. Lin et al., “Reliable and balanced transfer learning for generalized
multimodal face anti-spoofing,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 47, no. 9, pp. 7608–7625, Sep. 2025.
[38] X. Xie, Y. Cui, T. Tan, X. Zheng, and Z. Yu, “FusionMamba: Dynamic
feature enhancement for multimodal image fusion with mamba,” Vis.
Intell., vol. 2, no. 1, p. 37, Dec. 2024.
[39] G. Chen, L. Shen, R. Shao, X. Deng, and L. Nie, “Lion: Empowering
multimodal large language model with dual-level visual knowledge,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2024,
pp. 26540–26550.
[40] R. Zhang et al., “LLaMA-adapter: Efficient fine-tuning of language
models with zero-init attention,” 2023, arXiv:2303.16199.
[41] Q. Ye, Z. Yu, R. Shao, X. Xie, P. Torr, and X. Cao, “CAT: Enhancing
multimodal large language model to answer questions in dynamic
audio-visual scenarios,” in Proc. Eur. Conf. Comput. Vis., 2024,
pp. 146–164.

[42] P. Gao et al., “LLaMA-adapter v2: Parameter-efficient visual instruction
model,” 2023, arXiv:2304.15010.
[43] Q. Ye et al., “CAT+: Investigating and enhancing audio-visual understanding in large language models,” IEEE Trans. Pattern Anal. Mach.
Intell., vol. 47, no. 10, pp. 8674–8690, Oct. 2025.
[44] Y. Su, T. Lan, H. Li, J. Xu, Y. Wang, and D. Cai, “PandaGPT: One
model to instruction-follow them all,” 2023, arXiv:2305.16355.
[45] R. A. Jacobs, M. I. Jordan, S. J. Nowlan, and G. E. Hinton, “Adaptive
mixtures of local experts,” Neural Comput., vol. 3, no. 1, pp. 79–87,
Mar. 1991.
[46] H. M. Schlüter, J. Tan, B. Hou, and B. Kainz, “Natural synthetic
anomalies for self-supervised anomaly detection and localization,” in
Proc. Eur. Conf. Comput. Vis. (ECCV), 2022, pp. 474–489.
[47] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Selfsupervised learning for anomaly detection and localization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 9664–9674.
[48] J. M. Di Martino, G. Facciolo, and E. Meinhardt-Llopis, “Poisson image
editing,” Image Process. Line, vol. 6, pp. 300–325, Nov. 2016.
[49] T.-Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, “Focal loss for
dense object detection,” in Proc. IEEE Int. Conf. Comput. Vis. (ICCV),
Oct. 2017, pp. 2999–3007.
[50] F. Milletari, N. Navab, and S.-A. Ahmadi, “V-net: Fully convolutional
neural networks for volumetric medical image segmentation,” in Proc.
4th Int. Conf. 3D Vis. (3DV), Oct. 2016, pp. 565–571.
[51] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec AD—A
comprehensive real-world dataset for unsupervised anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2019, pp. 9584–9592.
[52] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, “Spotthe-difference self-supervised pre-training for anomaly detection and
segmentation,” in Proc. Eur. Conf. Comput. Vis. Springer, 2022,
pp. 392–408.
[53] N. Cohen and Y. Hoshen, “Sub-image anomaly detection with deep
pyramid correspondences,” 2020, arXiv:2005.02357.
[54] W.-L. Chiang et al., “Vicuna: An open-source chatbot impressing GPT-4
with 90% ChatGPT quality,”, vol. 2, no. 3, p. 6, 2023. Accessed: Apr.
14, 2023. [Online]. Available: https://vicuna.lmsys.org
PAPER_TEXT
