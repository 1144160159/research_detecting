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
# [250] Large-Scale Visual Language Model Boosted by Contrast Domain Adaptation for Intelligent Industrial Visual Monitoring
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
编号：250
题名：Large-Scale Visual Language Model Boosted by Contrast Domain Adaptation for Intelligent Industrial Visual Monitoring
年份：2024
DOI：10.1109/tii.2024.3441638
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2024.3441638.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：无
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\250.txt
- 原始字符数：49898
- 本次发送字符数：49898
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
14114

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 12, DECEMBER 2024

Large-Scale Visual Language Model Boosted by
Contrast Domain Adaptation for Intelligent
Industrial Visual Monitoring
Huan Wang , Chenxi Li , and Yan-Fu Li , Senior Member, IEEE

Abstract—Industrial visual monitoring (IVM) is crucial in
enhancing the reliability and efficiency of manufacturing
processes. Recently, large vision-language models (LVLMs)
have demonstrated remarkable semantic understanding
and natural language interaction capabilities, which provide a novel solution to IVM. However, LVLMs pretrained
on common domains lack specific knowledge for IVM scenarios, causing insufficient adaptation to industrial image
patterns and specialized textual corpora. In this article,
we deeply studied the adaptation of LVLMs to IVM and
proposed DefectGLM. First, we proposed the first largescale multimodal wafer dataset as a reliable data basis
for model domain generalization. Second, this model employs low-rank adaptation–based contrast visual adaptation to align with industrial image patterns and utilizes
vision-language instruction tuning for professional knowledge alignment. DefectGLM is the first large-model-based
wafer image recognition model, and can accurately identify 36 types of wafer defects and provide appropriate text
descriptions. DefectGLM provides a new solution for the
development of industrial large models.
Index Terms—Defect detection, industrial visual monitoring (IVM), large vision-language model (LVLM), semiconductor manufacturing.

I. INTRODUCTION
N MODERN industry, the manufacturing process tends to
be more sophisticated and complex, which raises higher
requirements against automation, reliability, and safety [1], [2],
[3], [4]. To this end, industrial visual monitoring (IVM) aims
to integrate advanced visual sensors and artificial intelligence
technologies to oversee and optimize various facets ranging

I

Received 28 February 2024; revised 14 July 2024; accepted 28 July
2024. Date of publication 5 September 2024; date of current version
5 December 2024. This work was supported in part by the Beijing
Municipal Natural Science Foundation-Rail Transit Joint Research Program under Grant L231020, and in part by the National Natural Science
Foundation of China under a key project Grant 71731008. Paper no. TII24-0906. (Huan Wang and Chenxi Li contributed equally to this work.)
(Corresponding author: Yan-Fu Li.)
Huan Wang and Yan-Fu Li are with the Department of Industrial Engineering, Tsinghua University, Beijing 100084, China (e-mail:
huan-wan21@mails.tsinghua.edu.cn; liyanfu@tsinghua.edu.cn).
Chenxi Li is with the Glasgow College, University of Electronic Science and Technology of China, Chengdu 611731, China.
Color versions of one or more figures in this article are available at
https://doi.org/10.1109/TII.2024.3441638.
Digital Object Identifier 10.1109/TII.2024.3441638

from production lines to critical infrastructure. An effective IVM
method is capable of identifying potential issues, discovering
surface anomalies, and recognizing defection patterns [5], [6],
[7]. The introduction of IVM enables predictive maintenance
and optimization of resource utilization, which shows an important area of applied study.
In recent years, as an efficient data-driven approach, deep
learning methods have attracted the attention of researchers,
demonstrating excellent application potential in practical monitoring scenarios. It generally trains a neural network with
industrial monitoring data, so that the model can identify the
anomalies or defection patterns in an end-to-end manner. Convolutional neural networks (CNNs), one of the popular network architectures in computer vision, can extract visual features using
convolution kernels capable of recognizing complex, multilevel
patterns. Many advanced variants of CNNs have been proposed
recently to tackle more complex tasks, e.g., AlexNet [8], VGG
[9], ResNet [10], and DenseNet [11]. Additionally, the appearance of transformer architecture also leads to a breakthrough
in visual pattern recognition. Methods like Vision Transformer
(ViT) [12] and Swin-Transformer [13] introduced attention
mechanisms to extract features that are most relevant to an image
while suppressing irrelevant details.
These data-driven approaches have achieved great success in
IVM scenarios like anomaly detection and defect recognition.
However, they still face some limitations in further practical application. The out-of-distribution problems are the first
concern against classic deep learning methods. When facing
practical scenarios where the data distribution is diverse and
complex, these methods trained on small datasets typically face
generalization problems [14]. Second, classic deep learning
methods are sensitive and unrobust to image noise, which could
affect the final diagnosis performance [15]. Finally, these classic
vision methods can only output discrete and probability-oriented
results, which lack sufficient human interaction.
More recently, the pretrained large language models (LLMs)
like ChatGPT, LLaMA [16], and ChatGLM [17] have demonstrated powerful comprehension and dialogue ability to natural
language. These LLMs are pretrained with enormous textual
data from the Internet and possess a degree of world knowledge
from text modality. Besides the language modality, the emergence of the pretrained large vision-language models (LVLMs)
has bridged the modality gap across information between images

1551-3203 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

WANG et al.: LARGE-SCALE VISUAL LANGUAGE MODEL BOOSTED BY CONTRAST DOMAIN ADAPTATION FOR INTELLIGENT IVM

Fig. 1. Difference between existing vision methods and LVLMs in wafer
defect recognition scenarios. The vision methods can only output discrete diagnosis results. DefectGLM is an agent that allows for both wafer
image and textual instruction input, which can generate recognition
results in natural language.

and texts. LVLMs demonstrate a series of advantages, including
image semantic understanding, noise robustness, and language
interaction capabilities. Therefore, the emergence of LVLMs
offered a novel opportunity for creating an IVM agent that can
effectively recognize defection patterns and generate diagnosis
responses for operators in natural language. The difference between classic deep learning methods and LVLMs is highlighted
in Fig. 1. However, LVLMs pretrained on common-knowledge
domains are short of proven to be insufficient in obtaining
professional domain knowledge for IVM scenarios. Specifically, the absence of domain knowledge includes two aspects.
First, LVLMs lack the adaptation of industrial image patterns
in specific scenarios. Industrial images have discrepant data
distributions and vision patterns compared to common images,
which may lead to unsatisfactory image modeling performance
in IVM tasks. Second, LVLMs lack alignment with professional
knowledge, as the jargon and concepts in IVM scenarios are
highly specialized. Consequently, the model may fail to follow
instructions and generate the expected diagnostic responses.
Therefore, these biases from discrepant vision patterns and
different text corpora could cause knowledge absence in LVLMs,
resulting in undesirable performance when directly utilized in
professional IVM scenarios.
To tackle the knowledge absence problem, we explore adapting LVLMs to professional IVM scenarios and propose DefectGLM, a novel vision-language IVM solution. In this article,
we proposed the first large-scale multimodal wafer dataset as a
reliable data basis for model domain generalization. Moreover,
DefectGLM introduces a simple yet effective two-stage adaptation strategy to compensate for the absence of professional
domain knowledge. Specifically, we employ low-rank adaptation (LoRA)–based contrast visual adaptation in the first stage,
which enables DefectGLM to adapt specific visual patterns and
improve the industrial image modeling capability. Furthermore,
a visual language instruction tuning is introduced in the second
stage to align DefectGLM to professional domain knowledge,
which enhances the instruction-following ability to generate satisfactory diagnosis responses. We utilize the proposed strategy
to fine-tune our DefectGLM with the presented dataset, which
successfully adapts LVLMs into professional IVM scenarios.

14115

The contributions of this article are summarized as follows.
1) This article explores an efficient application of LVLMs
to professional IVM tasks, which tackles the problem of
lacking specific domain knowledge within LVLMs in two
aspects, including discrepant industrial image patterns
and different professional domain knowledge.
2) This article introduces DefectGLM, a novel two-stage
adaptation strategy for LVLMs in IVM. It utilizes LoRAbased contrast visual adaptation and vision-language instruction tuning to enhance defect pattern recognition and
professional knowledge alignment. DefectGLM achieves
over 99% accuracy in wafer defect recognition, demonstrating state-of-the-art performance.
3) The presented multimodal wafer dataset and our DefectGLM will be released for facilitating related IVM
research.
The rest of this article is organized as follows. Section II
discusses the related work. Section III introduces the proposed
DefectGLM method. In Section IV, the experiment results and
discussions will be detailed. Finally, Section V concludes this
article.
II. RELATED WORKS
A. Deep Learning Based IVM Methods
Recently, many deep learning approaches have been utilized
to process and recognize the defect and anomaly pattern in IVM
scenarios. CNN is a well-known architecture, which is widely
applied in IVM. Wang et al. [18] developed a deformable CNN
architecture to extract high-qualified features within the wafer
maps for defect pattern recognition. Staar et al. [19] constructed
a triplet CNN to inspect industrial surface anomalies. Kim et
al. [20] used a CNN-based shot detector to recognize wafer
defect objects, which can further localize the defect information.
Yu and Liu [21] employed a convolutional autoencoder for
wafer defect detection with a novel 2-D principal component
convolution kernel. Napoletano et al. [22] introduced a CNN,
self-similarity-based method, and scanning electron microscope
to detect and localize the anomalies in nanofibrous materials.
More recently, other deep learning architectures, e.g., transformers have attracted attention in IVM scenarios. Nafi et al.
[23] trained a Swin-Transformer with mixed-type wafer data
and achieved great performance in defect recognition. Mishra et
al. [24] presented a transformer-based Gaussian mixture density
network to capture the anomaly patterns within the industrial
images. Hsu et al. [25] combined the ViT and a novel cluster
method to analyze wafer map defects. There are still some
methods that use U-Net or autoencoder architecture to solve
IVM problems. These methods achieved significant success but
also faced some problems of generalization, robustness, and
interpretability.
B. Large Vision-Language Models
While LLMs have demonstrated powerful performance in
many NLP tasks, LVLMs have further extended their abilities into the vision-language modality. Li et al. [26] proposed

14116

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 12, DECEMBER 2024

BLIP-2, which used a learnable querying transformer to bridge
the modality gap between vision and language. Liu et al. [27]
introduced LLaVA, which is trained with instruction tuning,
which incorporates a learnable projection matrix to convert
visual features into the language embedding space. Zhu et al.
[28] proposed a MiniGPT4 that utilizes a linear projection to
align visual representation with an LLM named Vicuna. Du
et al. [17] presented VisualGLM, which utilized the BLIP-2
framework to connect pretrained ViT and ChatGLM, and it
was trained with 300M image-text data. These methods demonstrate remarkable capabilities in handling multimodality tasks.
The work using vision-language models and contrastive learning with DefectGLM for IVM addresses the gap in adapting
LVLMs to specialized industrial scenarios. Ranasingh et al.
[29] enhanced vision-language representations by integrating
perceptual grouping principles, improving feature alignment
and robustness. Gao et al. [30] proposed a pyramid architecture for hierarchical feature alignment, capturing various levels
of detail and significantly outperforming existing models in
vision-language tasks. Luo et al. [31] introduced contrastive
learning and denoising mechanisms to improve the alignment of
video frames and textual descriptions, boosting performance on
video-language benchmarks. Unlike the general enhancements
presented in the earlier works, DefectGLM focuses specifically
on IVM, a crucial area for enhancing manufacturing process
reliability and efficiency.
However, these models pretrained with common data, may
lack specific knowledge in the professional domain, leading to
undesirable performance when simply applied to IVM scenarios.
To adapt LVLMs to professional tasks, we introduce a novel
two-stage adaptation method and propose DefectGLM as a novel
vision-language solution for defect recognition.
C. Parameter Efficient Fine-Tuning
To adapt a large-scale model to a specific downstream task,
parameter-efficient fine-tuning (PEFT) methods are considered a
more efficient solution compared to full fine-tuning. PEFT introduces only a few learnable parameters during fine-tuning, significantly reducing computation costs. Recently, Houlsby et al. [32]
proposed adapter tuning, which adds learnable adapter modules
to the network architecture to adapt to new tasks. This method
reduces fine-tuning costs but increases network depth. Subsequently, Hu et al. [33] introduced LoRA to build a learnable lowrank matrix parallelly in the model, which avoids the increase of
network depth. Additionally, Yin et al. [34] employed the tiny
adapter with low-rank synthesis to improve the adapter tuning
performance. Besides, Dettmers et al. [35] utilized quantization
mechanics to optimize the LoRA approach, reducing memory
usage without sacrificing performance. Different from the above
methods, this study focuses on the generalization and adaptation
of multimodal large models to industrial fields and proposes a
two-stage adaptation strategy. This strategy uses LoRA-based
contrast visual adaptation and visual language instruction tuning
methods, which optimize the visual representation module and
language generation module to achieve the best understanding
of industrial data, and finally comprehensively align the visual

module and language model to achieve an accurate understanding of industrial image data.
III. METHODOLOGY
DefectGLM represents an innovative vision-language
solution for addressing IVM tasks by analyzing defect patterns
and providing natural language interactions for operators.
To tackle the absence of specialized domain knowledge
within LVLMs, we propose a two-stage adaptation strategy,
comprising contrast visual adaptation and vision-language
instruction tuning. The primary objective of contrast
visual adaptation is to compensate for the visual pattern
gap between Internet common images and professional
industrial images. This is achieved by utilizing LoRA
adapters and contrastive representation techniques, which
enhance the industrial image modeling capability of the
DefectGLM. Vision-language instruction tuning aims to align
the LVLMs to professional domain knowledge so that the
DefectGLM can comprehend specific instructions and therefore
generate expected instruction-following responses. In our
implementation, we use a pretrained ViT as the visual encoder
and a pretrained ChatGLM-6B as the LLM text decoder. We
utilize the proposed two-stage adaptation method to fine-tune
the pretrained model on a multimodal wafer defect dataset.
The generation process of the dataset will be detailed in
Section III-D. The DefectGLM can analyze industrial defect
patterns and generate instruction-following responses.
A. Network Architecture
The network architecture of the proposed DefectGLM is
shown in Fig. 2. Mainly, DefectGLM consists of three parts, a
visual encoder for processing vision modality, a querying transformer for bridging the modality gap, and a language decoder
for processing and generating language modality. Specifically,
the visual encoder uses a pretrained ViT to extract visual representation from the defect patterns. The ViT contains a convolutional projection layer and stacked multihead attention blocks
to convert industrial images into patch tokens and then extract
multilevel features. The querying transformer is an intermediate
module designed to project extracted visual information into
language embedding spaces. This lightweight transformer takes
the learned tokens as queries and the extracted visual features
as keys and values to perform a cross-attention mechanism,
which captures text-related visual information from the visual
features. Its primary function is to align visual semantics with
their corresponding linguistic counterparts, projecting the visual
features from a dimensionality of 768 to 409, making them
suitable for input into LLMs. For language modality, the language decoder utilizes a novel LLM, i.e., ChatGLM-6B that
is pretrained on an enormous text corpus and is capable of
understanding and generating natural language. The details of
the network architecture are summarized in Table I.
In the fine-tuning process, we freeze all the parameters of
the pretrained image encoder and language decoder to reduce
training costs and prevent catastrophic forgetting of pretrained
knowledge. Furthermore, we plug LoRA into the frozen ViT and

WANG et al.: LARGE-SCALE VISUAL LANGUAGE MODEL BOOSTED BY CONTRAST DOMAIN ADAPTATION FOR INTELLIGENT IVM

14117

Fig. 2. Network architecture of the DefectGLM. DefectGLM consists of a pretrained ViT as a visual encoder for extracting wafer visual features, a
coupled querying transformer for mapping visual features into the language embedding space, and a ChatGLM as an LLM decoder for generating
instruction-following responses.

TABLE I
MODEL ARCHITECTURE DETAILS

given one weight matrix W0 ∈ Rd×k and input matrix x ∈ Rb×d ,
the forward result constrained by LoRA is W0 x + BAx, where
B ∈ Rd×r and A ∈ Rr×k are two low-rank decomposition matrices, and the rank parameter satisfies r  min(d, k). For
the self-attention mechanism in the pretrained ViT, first given
three weight matrices, query, key, and value Wq ∈ RdHidden ×dk ,
Wk ∈ RdHidden ×dk , and Wv ∈ RdHidden ×dv , the attention output is
computed as
Q = Wq x + Bq Aq x ; K = Wk x + Bk Ak x ;

ChatGLM as the learnable parameter matrixes. We only update
the LoRA parameters when adapting LVLMs to IVM tasks. The
utilization of LoRA can help visual adaptation of specific pattern
representations for ViT and language instruction understanding
for ChatGLM.
B. LoRA-Based Contrast Visual Domain Adaptation
The visual encoder of the proposed DefectGLM is a ViT
backbone that is pretrained with huge image data in the commonknowledge domain. However, the direct utilization of freezing
ViT in IVM tasks will lead to undesirable performance, which
may be caused by discrepant visual patterns in specific industrial
scenarios. The pretrained ViT is capable of processing common
images but still lacks adaptation of professional visual patterns
in industrial scenarios. Therefore, it is essential to perform
visual pattern adaptation to the pretrained visual encoder for
better extracting industrial image representations to that improve
the image modeling capability. The process of contrast visual
adaptation is shown in Fig. 3(a).
Here, we utilize the contrastive representation and PEFT
strategy LoRA to adapt the pretrained visual encoder to professional IVM tasks. LoRA uses trainable rank decomposition
matrixes that can be inserted into any self-attention layers for
the pretrained ViT to adapt downstream works. Specifically,

V = Wv x + Bv Av x


QK T
Attention (Q, K, V ) = soft max √
V
dk

(1)
(2)

where Q, K, and V are three matrices modified by the LoRA
constraint, dk is the dimension of the hidden representation.
In the visual adaptation process, we freeze all the parameters
of pretrained ViT and only train the LoRA adapter that only
requires much fewer parameters.
To adapt the pretrained ViT to specific visual patterns in
the industrial monitoring scenarios, we employ contrastive representation as a self-supervised visual adaptation approach in
DefectGLM. The introduction of contrastive representation can
force the pretrained visual encoder to adapt specific visual
patterns in a self-supervised manner and extract more transferable representations for the following language modality process. Specifically, suppose we have an industrial image dataset
X = {xi , y i }ni=1 that has a total of n image-label pairs. We
perform random augmentation to each image and therefore
n
obtain an augmented dataset Xaug = {xaug
i , yi }i=1 as the positive
example for the corresponding industrial image xi . Then, both
the datasets are fed into the ViT that is modified with LoRA
and augmented
to obtain the original representation {zi }batchsize
i=1
from
the
final
output
layer. For each
representation {zjaug }batchsize
j=1

14118

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 12, DECEMBER 2024

Fig. 3. Two-stage adaptation strategy, including contrast visual adaptation and vision-language instruction tuning. DefectGLM freezes most of the
parameters and only updates LoRA parameters during fine-tuning. (a) First stage. (b) Second stage.

representation pair, the InfoNCE contrastive representation loss
can be computed as follows:
 
 
exp s zi , ziaug /τ
(3)
Lr = − log batchsize
 
 
exp s zi , zjaug /τ
j
where τ is a temperature threshold (0.1 in this case) and s(·, ·) is
the cosine similarity score for each pair given as


s zi , zjaug =

zi · zjaug

 zi  zjaug 

.

(4)

Additionally, the presented dataset includes ground-truth
labels that can be utilized. So, the classification loss is introduced
to boost the modeling capability of DefectGLM. Classification
loss can assist contrastive loss to learn more category discriminative features, which alleviates the separation of false-negative
samples caused by contrastive loss. The classification loss uses
a cross-entropy function, which can be derived as
Lc = −

batchsize


yi log (p (xi ))

(5)

i=1

where p(xi ) ∈ R1×c is the predicted probability vector and yi is
the one-hot vector. Therefore, the final training goal of the first
stage can be the sum of the contrastive adaptation loss and the
classification loss.
C. Vision-Language Instruction Tuning
The primary goal of the DefectGLM is to accept industrial
visual images and generate concise and reliable natural language
responses about diagnosis results. To make the pretrained LLM
comprehend the specific task instructions and output desirable
language responses based on given industrial images, we employ
a vision-language instruction tuning strategy on a generated

image-text dataset to align the domain knowledge for improving
the instruction-following capability.
As shown in Fig. 3(b), vision-language instruction tuning
leverages a generated image-text dataset as a supervised signal
to guide the model to generate expected diagnosis answers based
on input industrial images and instruction prompts. Specifically,
suppose the industrial visual imagesXv = {xi }ni=1 are first fed
into the visual encoder ViT fv (·), which obtains the visual
representationZv = fv (Xv ). Then, the querying transformer
fq (·) is applied to align the visual representation that is semantic
important into the language embedding spaces. Thus, we obtain
the output visual tokens Tv = fq (Zv ). Then, we concatenate the
visual tokens with instruction prompt tokens Tq that are obtained
by the language embedding layer. We utilize the concatenated
multimodal tokens [Tv ;Tq ] that contain the information of visual
images and language instruction as the input of ChatGLM, and
therefore predict the text outputyi = [yi,1 , yi,2 , . . . yi,T ]. The
autoregressive loss function is utilized here, which can be represented by the negative sum of the predicted probability of yi,t+1
given previously predicted text tokensyi,1···t . The computation
is shown as follows:
L=−

Ti
batchsize
 
i=1

log [p (yi,t+1 | [Tv :Tq ] , yi,1···t , Φ)]

(6)

t=1

where Ti is the sequence length of the ith output and Φ is
the parameters of the ChatGLM-6B. The autoregressive loss
function can make predicted answers close to the ground truth
and therefore improve the response performance.
D. Industrial Image and Text Dataset
We utilize the open-source mixed-type wafer dataset published by Wang et al. [18]. The wafer maps are obtained using
test probes for each die to test the electrical performance. The

WANG et al.: LARGE-SCALE VISUAL LANGUAGE MODEL BOOSTED BY CONTRAST DOMAIN ADAPTATION FOR INTELLIGENT IVM

14119

The defective dies form a ring structure in this wafer map.
The templates consist of two parts: the first gives the diagnosis
results, and the second describes the defective patterns illustrated
in the wafer images. The generation of text descriptions can also
be assisted by ChatGPT or other LLMs.
E. Application Procedure of DefectGLM
The detailed procedure of DefectGLM for fine-tuning LVLMs
into a professional IVM scenario is shown in this section. The
procedure consists of two stages summarized as follows.
Stage I: Contrast visual adaptation
This part includes the following four steps.

Fig. 4. Mixed-type wafer images with RGB standard. (a) Single defective patterns. (b) Mixed-type defective patterns.

wafer map only contains three different values with 52 × 52
size, in which 0 denotes a blank plot, 1 presents a normal die,
and 2 is a broken die. To adapt the dataset to the input of LVLM,
these wafer maps are converted to the standard RGB images
with 224 × 224 size as the input of the visual encoder. The
wafer RGB images are shown in Fig. 4. Fig. 4 shows some
examples of the single and mixed-type defection patterns. The
dataset encompasses 36 distinct defect patterns, including 7
single-type defects, 13 two-mixed type defects, 12 three-mixed
type defects, and 4 four-mixed type defects. The single-type
defects indicate that only one defect pattern occurs in the wafer
map. We considered seven single defect patterns in our study:
Normal, Center (C), Donut (D), Edge_Loc (EL), Edge_Ring
(ER), Loc (L), and Scratch (S). The “Normal” pattern signifies
no defects, whereas C denotes a central circular defect. D is
characterized by a circular ring-like defect, EL indicates a local
defect region near the wafer’s edge, ER represents a ring defect
pattern near the edge, L represents a localized defect region, and
S denotes a long strip-like defect.
In addition to these 7 single-type defects, multiple defect
patterns may occur in one wafer map, which is a combination of multiple single-type defects. For two-mixed type defects, we considered 13 classes: C + EL, C + ER, C + L, C + S,
D + EL, D + ER, D + L, D + S, EL + L, EL + S, ER + L, ER + S,
and L + S. These two-mixed type defects feature two single
defect patterns in the wafer map. Additionally, we considered three mixed-type defects and four mixed-type defects,
including C + EL + L, C + EL + S, C + ER + L, C + ER + S,
C + L + S, D + EL + L, D + EL + S, D + ER + L, D + ER + S,
D + L + S, EL + L + S, ER + L + S for three mixed-type defects, and C + L + EL + S, C + L + ER + S, D + L + EL + S, and
D + L + ER + S for four mixed-type defects.
For text alignment, we first construct a hard prompt as the
instruction for all text input, such as What is the defect in this
wafer map? Then, since the industrial dataset generally lacks text
annotations, the description templates are utilized to generate the
text label of each wafer image. For instance, “Donut” defect.

Step 1: Collect the wafer maps for each defection pattern to
generate a fine-tuning dataset.
Step 2: Preprocess the collected wafer maps and generate another
augmented dataset.
Step 3: Both original and augmented wafer images are used as
the ViT inputs for representation extraction.
Step 4: Use extracted representations to fine-tune LoRA in ViT
with contrastive and classification learning.
Stage II: Vision language instruction tuning
This part includes the following five steps.
Step 1: Generate a visual instruction dataset with wafer images
and text templates.
Step 2: Input the wafer images into the pretrained ViT to extract
visual representations.
Step 3: The extracted visual representations are used as input
for the querying transformer to project them into the language
embedding space.
Step 4: The projected representation is concatenated with the
token embeddings of language instruction, and then used as
input for ChatGLM.
Step 5: The outputs of the ChatGLM and the text labels are
utilized to fine-tune the LoRA parameters.
By employing the two-stage adaptation strategy, the DefectGLM can be adapted to professional industrial monitoring tasks.
IV. EXPERIMENTS
A. Experiment Setting
1) Dataset: The experiments were conducted on a diverse
wafer dataset comprising 36 distinct categories of defective
patterns [18]. To maintain data balance, we allocated 800 wafer
images from each category for the training dataset, while reserving 100 wafer images for validation and 50 for testing purposes.
In total, our dataset is comprised of 34 200 wafer images, which
were utilized for both training and assessing the performance of
each method.
2) Evaluation Metric: To evaluate the performance of different models, several evaluation metrics are utilized. Since
wafer defection recognition is a classification task, we follow
the classic setting of multiclass classification, including mean
accuracy, precision, and F1-score to evaluate the defect recognition performance of the model.

14120

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 12, DECEMBER 2024

TABLE II
DEFECT RECOGNITION RESULTS OF LORA SENSITIVITY STUDIES

3) Implementation Details: We use the pretrained ViT as
the visual encoder of the backbone and utilize the pretrained
ChatGLM-6B as the text decoder. We plug the ViT LoRA (VL)
at 0, 13, 26, and 38 layers and ChatGLM LoRA (CL) at 0, 19,
and 27 layers as the trainable parameters for fine-tuning. The
fine-tuning process was conducted on two NVIDIA A40 GPUs
throughout 4500 iterations for each stage, resulting in a total of
9000 iterations. The learning rate was set at 1e-3 and a batch
size of 32 was employed. To enhance the stability of the training
process, we utilized a warm-up phase of 0.2 and implemented
a cosine learning rate decay strategy. It is important to note
that all pretrained models remained frozen during the training
process, and only the LoRA parameters will be updated. This
strategy was employed to ensure effective knowledge transfer
while fine-tuning the model using wafer images and instructional
data.

B. LoRA Sensitivity Results
This section aims to investigate the affection of the rank
number of the LoRA adapter in industrial monitoring scenarios.
The LoRA rank will directly affect the number of trainable
parameters in the DefectGLM, resulting in different adaptation
performances on specific scenarios. A larger LoRA rank can lead
to more trainable parameters to enable more volume for learning new knowledge but it also requires more training samples
and times for convergence. Therefore, investigating the optimal
value of LoRA rank is essential for applying LVLMs to specific
scenarios. The number of LoRA ranks in the ViT and ChatGLM
varies from 8 to 128 to adapt the wafer defect recognition task.
We record the number of trainable parameters and the percentage
of parameter reduction compared to the full-fine-tuning. The
parameter changes and final recognition results under different
LoRA rank settings are drawn in Table II.
According to Table II, it is obvious that using LoRA can
significantly reduce the total number of trainable parameters by
up to 99.98%. The results show that LoRA is efficient in saving
memory and computational resources during the fine-tuning
process.
Table II shows that the DefectGLM performs best when the
LoRA rank is 16 and the corresponding trainable parameters are
1.59 M. We also observe that the performance will first increase
and then decrease as increasing the value of the LoRA rank. This
could be caused by the small size of the wafer defection dataset,
which cannot provide enough training samples for adapting

TABLE III
ABLATION RESULTS OF DIFFERENT COMPONENTS OF EACH COMPONENT

more LoRA parameters. Thus, we use a LoRA rank of 16 in
the ViT and ChatGLM as the final solution of the proposed
DefectGLM.
C. Ablation Results
In this section, we conduct ablation studies to verify the
effectiveness of each component in the proposed DefectGLM.
We investigate the influence of adjusting vision parameters and
the effectiveness of the proposed visual representation adaptation. We only retain CL to perform language instruction tuning
and eliminate VL to verify if the LVLMs can obtain desirable
performance using pure language techniques without vision
adjustments. Then, we continue to explore how the contrast
visual adaptation learning loss influences the recognition result.
All the ablation studies are conducted with the LoRA rank of
16 for a fair comparison. Notably, Lc and Lr are specifically
designed to improve the vision encoder, so we only conduct
ablation experiments for Lc or Lr when VL is present.
Table III presents the recognition performance results obtained from the ablation studies. These ablation results highlight
several pivotal factors for adapting LVLMs to the complex
domain of professional industrial monitoring scenarios. First,
the comparison between the first and third rows in Table III,
shows that only adjusting language parameters is insufficient
for adapting LVLMs. The possible reason could be the absence
of visual knowledge within the visual encoder, so it is essential
to conduct visual pattern adaptation to adapt specific industrial
image patterns. By comparing the second row and the first
row, it is further verified the importance of adjusting the vision
encoder to adapt industrial image patterns. We found that the
accuracy of the third row is 97.44%, which demonstrates that
using both CL and VL can help to improve model performance.
Then, we investigate how contrast-representation learning and
supervised learning contribute to adapting the vision encoder.
By comparing the second row and the fourth row, it is obvious that contrast learning provides an efficient solution for
the vision encoder to learn defect pattern-related representation. The comparison between the second row and the fifth
row shows that supervised learning can also enforce the vision
encoder to learn category-discriminative representations. Both
these learned representations can contribute to improving the

WANG et al.: LARGE-SCALE VISUAL LANGUAGE MODEL BOOSTED BY CONTRAST DOMAIN ADAPTATION FOR INTELLIGENT IVM

14121

TABLE IV
DEFECT RECOGNITION RESULTS OF COMPARISON STUDIES

answer quality of LLMs. Notably, the accuracy results of the
fourth row and the seventh row are the same, which the possible
reason is that the model may met a performance bottleneck
when approaching an accuracy of 98.9%. Finally, the final row
achieved the best performance, which shows the classification
task can further boost the contrastive training. The possible
reason could be that using classification loss can alleviate the
separation of negative samples caused by contrast learning. This
result shows that contrast representation loss and classification
loss are complementary learning approaches that can learn more
comprehensive representations of LLMs.
D. Comparison Results
In this section, we conduct comparative studies utilizing
the mixed-type wafer dataset in conjunction with other wellestablished vision methods, including VGG19 [7], ResNet18
and ResNet50 [10], DenseNet [11], ViT [12], Swin-Transformer
[13], Swin-Transformer V2 [36], and ConvNeXt [37]. To adapt
these methods to the task at hand, we replace their final layers
with initialized linear classifiers to facilitate the classification
of defect patterns. Subsequently, we select the model with the
highest validation performance and assess its defect recognition
capabilities on the test dataset.
The results of wafer recognition on the testing dataset are
presented in Table IV. Our proposed method consistently outperforms other approaches for all mixed wafer defects, achieving
a remarkable overall accuracy exceeding 99.0%. Notably, the
convolution-based methods (such as VGG, ResNet, DenseNet,
and ConvNeXt) generally exhibit superior performance compared to the transformer-based methods (such as ViT and SwinTransformer). This disparity can be attributed to the fact that
transformer models typically require a more extensive amount of
training data to converge and achieve satisfactory performance.
This requirement is often challenging to meet in scenarios involving small wafer datasets. This finding underscores the robust
generalization capabilities of DefectGLM, which prove effective
even in cases with limited dataset sizes.
Additionally, Table IV also compared the trainable parameters
and inference time of the different methods. We use one NVIDIA
A40 (48 GB) GPU with an Intel Xeon Platinum 8358P CPU to
evaluate the average inference time for each image in the test
dataset. Our proposed DefectGLM stands out as a considerably

larger model than the classic vision models, boasting a total
parameter count of 7.2 billion. However, it is essential to note
that only 1.59 M parameters require updating during the training
process, a significantly smaller number than other models.
The results given in Table IV show that the convolutional
and ViT methods achieve the quickest inference times, which
are beneficial because of their small parameter sizes and high
parallel architecture. Although DenseNet has fewer parameters,
its inference time is significantly longer, because it has larger
feature maps with more channels that increase computational demands during convolutional operations. Additionally, the SwinTransformer’s shifting-window attention mechanism, designed
to capture hierarchical information, adds to its computational
complexity and increases the inference time. DefectGLM exhibits the slowest inference time, which is caused by extensively
higher parameter size and recursive text generation mechanism.
As a vision-and-language model, DefectGLM generates the text
by recursively predicting the next token, which the recursive
mechanism naturally slows down the inference speed.
To mitigate the issue of slow inference time and enhance
efficiency in real-world applications, several strategies can be
employed. First, applying quantization techniques to convert the
model to INT8 or even INT4 data types can conserve computational resources. Second, utilizing batch inference can speed up
the process. Third, model pruning can be used to eliminate redundant parameters, simplifying the model and thereby reducing
computational complexity and improving inference speed.
E. Qualitative Results
The examples shown in Fig. 5 showcase the practical application of DefectGLM in wafer defect recognition. We can see
that DefectGLM demonstrates high generalization to different
text prompts and can generate expected answers. In contrast
to previous methods that are limited to providing classification results and lack substantial user interaction, DefectGLM
offers a comprehensive language-vision solution for IVM scenarios. Notably, wafer defect recognition is only one case of
the DefectGLM; the proposed method can also be utilized in
other scenarios, such as anomaly detection. The advantages
of DefectGLM can be summarized as follows. First, DefectGLM leverages the powerful instruction-following and image
semantic understanding capabilities of pretrained LVLMs, thus

14122

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 12, DECEMBER 2024

Fig. 5.

Qualitative examples of the DefectGLM.

Fig. 6.

Comparison results with other LVLM-powered VQA models.

achieving excellent defect pattern recognition performance in
IVM scenarios. Second, the DefectGLM can follow prompt
instructions and generate concise and clear instruction-following
responses, which allows more human interaction with operators.
Finally, the DefectGLM represents a novel technique solution
path that integrates LVLMs into intelligent IVM tasks.
Additionally, to compare our DefectGLM with other LVLMpowered vision question-answering models, we conducted an
experiment to evaluate their answer quality against a wafer map
with a central defect. We select MiniGPT-4 7B [28] and LLaVA
v1.5 13B [27] as the comparison methods and evaluate the
answer from diagnosis correctness and pattern understanding,
which the results are shown in Fig. 6. From Fig. 6, MiniGPT-4
shows some ability to recognize the circular defect patterns but
outputs an incorrect diagnosis. LLaVA’s answer identifies both
center and edge defects, correctly recognizing the central black
spot in the wafer map, but incorrectly identifying an edge defect
that does not exist. Finally, our proposed DefectGLM provides
the correct diagnosis and pattern description, demonstrating the
effectiveness of the proposed two-stage fine-tuning strategy.

knowledge absence in LVLMs. The strategy compensated for the
knowledge absence in two aspects. First, the LoRA-based contrast visual adaptation allowed the model to adapt specific industrial visual patterns, thus reducing the knowledge gap between
common images and industrial images. Second, vision-language
instruction tuning aligned the model to a specific knowledge
domain and enhanced its instruction-following ability.
By utilizing the proposed adaptation strategy to pretrained
LVLMs on a multimodal wafer defect dataset, a novel visionlanguage method, DefectGLM, was proposed. The proposed
DefectGLM was specialized for IVM scenarios, which could
recognize defect patterns and generate instruction-following
responses. After evaluation, the DefectGLM showcased remarkable wafer defect recognition performance, which obtained an
accuracy of over 99.0%. In our future work, we will widely
validate the performance of the proposed method on other general multimodal model structures to extend its applications and
values. Finally, to facilitate the IVM research, we will release
our DefectGLM and the dataset.
REFERENCES

V. CONCLUSION
In this article, we undertook a comprehensive exploration
to efficiently adapt pretrained LVLMs to meet the demands of
professional IVM scenarios. We introduced an effective twostage adaptation strategy to address the challenge of domain

[1] S. Yin, S. X. Ding, X. Xie, and H. Luo, “A review on basic data-driven
approaches for industrial process monitoring,” IEEE Trans. Ind. Electron.,
vol. 61, no. 11, pp. 6418–6428, Nov. 2014.
[2] S. Yin, H. Gao, and O. Kaynak, “Data-driven control and process monitoring for industrial applications—Part II,” IEEE Trans. Ind. Electron.,
vol. 62, no. 1, pp. 583–586, Jan. 2015.

WANG et al.: LARGE-SCALE VISUAL LANGUAGE MODEL BOOSTED BY CONTRAST DOMAIN ADAPTATION FOR INTELLIGENT IVM

[3] X. Kong and Z. Ge, “Deep learning of latent variable models for industrial process monitoring,” IEEE Trans. Ind. Inform., vol. 18, no. 10,
pp. 6778–6788, Oct. 2022.
[4] W. Lu and X. Yan, “Deep double supervised embedding neural network
enhancing class separation for visual high-dimensional industrial process
monitoring,” IEEE Trans. Ind. Inform., vol. 17, no. 9, pp. 6357–6367,
Sep. 2021.
[5] L. Qi, Y. Yang, X. Zhou, W. Rafique, and J. Ma, “Fast anomaly identification based on multiaspect data streams for intelligent intrusion detection
toward secure Industry 4.0,” IEEE Trans. Ind. Inform., vol. 18, no. 9,
pp. 6503–6511, Sep. 2022.
[6] D. Tabernik, S. Šela, J. Skvarč, and D. Skočaj, “Segmentation-based deeplearning approach for surface-defect detection,” J. Intell. Manuf., vol. 31,
no. 3, pp. 759–776, Mar. 2020.
[7] J. Yu and J. Liu, “Multiple granularities generative adversarial network
for recognition of wafer map defects,” IEEE Trans. Ind. Inform., vol. 18,
no. 3, pp. 1674–1683, Mar. 2022.
[8] A. Krizhevsky, I. Sutskever, and G. E. Hinton, “ImageNet classification
with deep convolutional neural networks,” Commun. ACM, vol. 60, no. 6,
pp. 87–90, Jun. 2017, doi: 10.1145/3065386.
[9] K. Simonyan and A. Zisserman, “Very deep convolutional networks for
large-scale image recognition,” 2023, arXiv:1409.1556.
[10] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image
recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2016,
pp. 770–778.
[11] G. Huang, Z. Liu, L. Van Der Maaten, and K. Q. Weinberger, “Densely
connected convolutional networks,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit., 2017, pp. 2261–2269.
[12] A. Dosovitskiy et al., “An image is worth 16x16 words: Transformers for
image recognition at scale,” 2021, arXiv:2010.11929.
[13] Z. Liu et al., “Swin transformer: Hierarchical vision transformer using
shifted windows,” in Proc. IEEE/CVF Int. Conf. Comput. Vis., 2021,
pp. 9992–10002.
[14] G. Pang, L. Cao, and C. Aggarwal, “Deep learning for anomaly detection:
Challenges, methods, and opportunities,” in Proc. 14th ACM Int. Conf.
Web Search Data Mining, 2021, pp. 1127–1130.
[15] N. Akhtar and A. Mian, “Threat of adversarial attacks on deep learning in
computer vision: A survey,” IEEE Access, vol. 6, pp. 14410–14430, 2018.
[16] H. Touvron et al., “LLaMA: Open and efficient foundation language
models,” 2023, arXiv:2302.13971.
[17] Z. Du et al., “GLM: General language model pretraining with autoregressive blank infilling,” in Proc. 60th Annu. Meeting Assoc. Comput.
Linguistics, 2022, pp. 320–335.
[18] J. Wang, C. Xu, Z. Yang, J. Zhang, and X. Li, “Deformable convolutional
networks for efficient mixed-type wafer defect pattern recognition,” IEEE
Trans. Semicond. Manuf., vol. 33, no. 4, pp. 587–596, Nov. 2020.
[19] B. Staar, M. Lütjen, and M. Freitag, “Anomaly detection with convolutional neural networks for industrial surface inspection,” Procedia CIRP,
vol. 79, pp. 484–489, Jan. 2019.
[20] T. S. Kim, J. W. Lee, W. K. Lee, and S. Y. Sohn, “Novel method for
detection of mixed-type defect patterns in wafer maps based on a single
shot detector algorithm,” J. Intell. Manuf., vol. 33, no. 6, pp. 1715–1724,
Aug. 2022.

14123

[21] J. Yu and J. Liu, “Two-dimensional principal component analysis-based
convolutional autoencoder for wafer map defect detection,” IEEE Trans.
Ind. Electron., vol. 68, no. 9, pp. 8789–8797, Sep. 2021.
[22] P. Napoletano, F. Piccoli, and R. Schettini, “Anomaly detection in nanofibrous materials by CNN-based self-similarity,” Sensors, vol. 18, no. 1,
Jan. 2018, Art. no. 209.
[23] T. Nafi, E. Haque, F. Farhan, and A. Rahman, “High accuracy swin
transformers for image-based wafer map defect detection,” Int. J. Eng.
Manuf., vol. 12, pp. 10–21, Oct. 2022.
[24] P. Mishra, R. Verk, D. Fornasier, C. Piciarelli, and G. L. Foresti, “VTADL: A vision transformer network for image anomaly detection and
localization,” in Proc. IEEE 30th Int. Symp. Ind. Electron., 2021, pp. 1–6.
[25] Y.-M. Hsu, X. Jia, W. Li, and J. Lee, “A novel quality clustering methodology on fab-wide wafer map images in semiconductor manufacturing,”
in Proc. ASME 17th Int. Manuf. Sci. Eng. Conf., 2022, vol. 85819, Paper
V002T06A022.
[26] J. Li, D. Li, S. Savarese, and S. Hoi, “BLIP-2: Bootstrapping languageimage pre-training with frozen image encoders and large language models,” in Proc. Int. Conf. Mach. Learn., 2023.
[27] H. Liu, C. Li, Q. Wu, and Y. J. Lee, “Visual instruction tuning,” in Proc.
Adv. Neural Inf. Process. Syst., 2024, pp. 34892–34916.
[28] D. Zhu, J. Chen, X. Shen, X. Li, and M. Elhoseiny, “MiniGPT-4: Enhancing
vision-language understanding with advanced large language models,”
2023, arXiv:2304. 10592.
[29] K. Ranasinghe, B. McKinzie, S. Ravi, Y. Yang, A. Toshev, and J. Shlens,
“Perceptual grouping in contrastive vision-language models,” in Proc.
IEEE/CVF Int. Conf. Comput. Vis., 2023, pp. 5571–5584.
[30] Y. Gao et al., “PyramidCLIP: Hierarchical feature alignment for visionlanguage model pretraining,” Adv. Neural Inf. Process. Syst., vol. 35,
pp. 35959–35970, Dec. 2022.
[31] J. Luo, Y. Li, Y. Pan, T. Yao, H. Chao, and T. Mei, “CoCo-BERT: Improving video-language pre-training with contrastive cross-modal matching and denoising,” in Proc. 29th ACM Int. Conf. Multimedia, 2021,
pp. 5600–5608.
[32] N. Houlsby et al., “Parameter-efficient transfer learning for NLP,” in Proc.
36th Int. Conf. Mach. Learn., 2019, pp. 2790–2799.
[33] E. J. Hu et al., “LoRA: Low-rank adaptation of large language models,”
2021, arXiv:2106.09685.
[34] D. Yin, Y. Yang, Z. Wang, H. Yu, K. Wei, and X. Sun, “1% vs 100%:
Parameter-efficient low rank adapter for dense predictions,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2023, pp. 20116–20126.
[35] T. Dettmers, A. Pagnoni, A. Holtzman, and L. Zettlemoyer, “QLORA:
Efficient finetuning of quantized LLMs,” Adv. Neural Inf. Process. Syst.,
vol. 36, pp. 10088–10115, 2023.
[36] Z. Liu et al., “Swin transformer V2: Scaling up capacity and resolution,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2022,
pp. 12009–12019.
[37] Z. Liu, H. Mao, C.-Y. Wu, C. Feichtenhofer, T. Darrell, and S. Xie, “A
ConvNet for the 2020s,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2022, pp. 11976–11986.
PAPER_TEXT
