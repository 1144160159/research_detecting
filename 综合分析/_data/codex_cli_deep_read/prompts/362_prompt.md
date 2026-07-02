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
# [362] An Unsupervised Learning Approach for Pavement Distress Diagnosis via Siamese Networks
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
编号：362
题名：An Unsupervised Learning Approach for Pavement Distress Diagnosis via Siamese Networks
年份：2024
DOI：10.1109/tits.2024.3500030
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2024.3500030.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：无
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\362.txt
- 原始字符数：59335
- 本次发送字符数：59335
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1876

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 2, FEBRUARY 2025

An Unsupervised Learning Approach for Pavement
Distress Diagnosis via Siamese Networks
Ruiqi Ren , Peixin Shi , Pengjiao Jia, and Jinwoo Kim

Abstract— Accurate, automated diagnosis of pavement distress
is essential for effective roadway maintenance but presents
considerable challenges. Supervised learning methods are constrained by limited labeled data, while existing unsupervised
representation learning approaches are difficult to capture the
fine-grained details needed for precise pixel-level segmentation
in pavement images with similar backgrounds. To address
these limitations, we propose a novel unsupervised approach
for pavement distress segmentation that employs a new pretext task within Siamese networks. Our method integrates an
explicit prediction head and a high-dimensional cross-entropy
loss, enabling implicit class labeling and enhancing fine-grained
recognition of distress patterns. Additionally, vision transformers
are employed to leverage self-attention mechanisms, facilitating
accurate segmentation of foreground distress regions. Experimental results demonstrate that our approach outperforms existing
unsupervised representation learning and anomaly detection
methods. Notably, when used to pre-train backbone networks
such as ResNet-50, our method yields higher accuracy and
faster convergence on downstream supervised tasks compared
to pre-training on the labeled ImageNet dataset. The proposed
method holds promise for advancing pavement maintenance
decision-making and enhancing the performance of traditional
supervised deep learning models.
Index Terms— Pavement distress, unsupervised deep learning,
Siamese networks, vision transformers.

I. I NTRODUCTION
CCURATE automatic pavement distress diagnosis is
crucial for efficient roadway maintenance while faces
significant challenges [1]. Manual pavement distress diagnosis
and maintenance often disrupt road traffic and cost significant
labors and time [2]. As a corollary, pavement management
must navigate a fine balance between maintenance costs,
potential serviceability losses, and structural health preservation [3]. In recent decades, the emergence of fast, economical,
and automated pavement distress detection technology has
provided an effective solution for pavement management.
Integrating a pavement distress diagnosis system onto an
inspection vehicle enables automatic diagnoses without disrupting traffic and saves cost [4].

A

Received 19 December 2023; revised 7 July 2024 and 30 October 2024;
accepted 7 November 2024. Date of publication 27 November 2024; date of
current version 4 February 2025. This work was supported by the National
Natural Science Foundation of China under Grant 52278405. The Associate
Editor for this article was Y. Hou. (Corresponding author: Peixin Shi.)
Ruiqi Ren, Peixin Shi, and Pengjiao Jia are with the School of
Rail Transportation, Soochow University, Suzhou 215000, China (e-mail:
20204046002@stu.suda.edu.cn; pxshi@suda.edu.cn).
Jinwoo Kim is with the Department of Civil and Environmental Engineering,
Hanyang University, Seoul 04763, South Korea.
Digital Object Identifier 10.1109/TITS.2024.3500030

A commonly used pavement distress diagnosis system typically includes a remote sensing module for digital image
acquisition, a global positioning system (GPS), and a digital
image analysis system for recognition and segmentation. The
early image analysis system heavily relies on hand-crafted
features, including texture, gradient, and shape descriptors,
to identify various distress types [5], [6], [7]. These traditional
feature extraction methods have limited generalization capabilities, struggling to accommodate the diverse and complex
nature of pavement images. Moreover, designing hand-crafted
features is time-consuming, requiring meticulous engineering
efforts. There is a pressing need for advanced pavement distress diagnosis techniques that can overcome these limitations
and offer more robust, efficient solutions.
In recent years, deep learning has emerged as a promising solution for pavement distress diagnosis [8], [9], [10],
[11], [12]. Compared to traditional methods, deep learning
is data-driven and can learn to automatically extract relevant
features. It eliminates the requirement for laborious manual
feature engineering, making it more generalized and suitable
for a wide range of diagnosis tasks. Deep learning-based
methods represented by supervised learning train a network to
recognize pavement distress by feeding it images with manual
labels. By sampling different distresses, a deep learning network can be trained to identify cracks, potholes, rutting, and
other pavement distresses with high accuracy. However, one
of the major challenges of supervised learning is the availability of labeled data. Insufficient data may lead to network
overfitting while manual labeling is very labor-intensive.
Deep representation learning offers a novel technique to
mitigate the reliance on manual annotations. Mainstream
approaches can be broadly categorized into generative learning
and contrastive learning. Generative learning leverages the
redundant characteristics of image information, allowing for
the generation of complete images from a subset of this
data, thereby facilitating the extraction of deep representations inherent within the images [13], [14], [15], [16].
Contrastive learning focuses on maximizing the mutual information between different views of the same image, commonly
employing Siamese networks [17], [18], [19]. Theoretically,
the ability to learn deep representations from pavement images
holds the promise of extracting robust distress features without the necessity for manual annotations. However, practical
applications reveal several significant challenges. First, distress objects often exhibit unique characteristics, frequently
presenting elongated shapes. Consequently, when employing

1558-0016 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

REN et al.: UNSUPERVISED LEARNING APPROACH FOR PAVEMENT DISTRESS DIAGNOSIS VIA SIAMESE NETWORKS

Fig. 1.

1877

Training schema of unsupervised siamese networks for pavement distress diagnosis (SiapaveNet).

generative learning architectures with limited information,
there is a substantial risk of overlooking critical foreground
distress targets, which undermines the learning of robust features; Second, the existing pretext tasks designed for Siamese
networks, which are based on the similarity or difference of
images within batches, encounter difficulties when applied
to pavement images that possess similar backgrounds and
small objects; Last, achieving unsupervised distress segmentation through deep representation learning remains a complex
challenge that necessitates further exploration. Effectively
addressing these limitations is crucial for unlocking the full
potential of unsupervised methods in pavement distress segmentation applications.
To address this issue, this study investigates the feasibility
of applying unsupervised learning to learn representations
directly from unlabeled pavement images. We propose a
novel solution for pavement distress diagnosis, which utilizes a predicting classification-based Siamese network with
cross-entropy loss and high-dimensional output to provide
implicit class labels (SiapaveNet), as illustrated in Figure 1.
It utilizes the self-attention mechanism of Vision Transformers
(ViTs) to achieve pixel-level segmentation. The proposed
framework can be employed to train commonly used backbone
networks such as ResNet-50 [20], and the performance is
superior to ImageNet pre-trained backbone networks. It is
an innovative exploration of fully unsupervised pixel-level
pavement distress diagnosis and may serve as a baseline for
future research in this field.
II. R ELATED W ORK
Currently, deep learning is probably the most prevalent and
potent technique for pavement distress diagnosis. This section
provides an overview of existing deep learning-based methods
that may be used for pavement distress diagnosis to highlight
the significance and potential of the proposed method.
A. Crack Segmentation
Cracking is the most common form of pavement distress
and crack segmentation has received intensive attention in
academia. Most existing approaches employ CNNs such as
U-Net [21] or Fully Convolutional Networks (FCNs) [22] and

their variants for crack segmentation. For example, Yang et al.
[23] proposed a U-Net variant with a pyramid and hierarchical boosting network for pavement crack segmentation.
Xiang et al. [24] combined super-resolution image reconstruction with U-Net segmentation to enhance the accuracy
of low-pixel microcracks, while Zhang et al. [25] designed
a non-symmetric U-Net architecture with a discriminator to
effectively segment small cracks. Recently, transformer-based
methods have emerged as the state-of-the-art for fine crack
segmentation, highlighting the potential of transformers in this
field [26]. While current research efforts are mainly focused
on improving the accuracy of pavement distress segmentation
through supervised learning, there has been very limited work
on completely unsupervised approaches. This research aims to
explore unsupervised pavement distress diagnosis as an alternative, which has the potential to complement and enhance
existing supervised learning solutions.
B. Anomaly Detection
Anomaly detection techniques, commonly utilized for identifying human diseases and industrial defects, can also be
adapted to detect pavement distress, which serves as an
anomaly on healthy surfaces. While these methods often
employ unsupervised or semi-supervised approaches due to
the unpredictable nature of anomalies [27], [28], [29], they still
rely on weak labels, limiting their effectiveness. Solutions typically involve transforming abnormal images into normal ones
for comparative analysis [30] and using various unsupervised
techniques such as convolutional autoencoders [31], vector
quantized variational autoencoders (VQ-VAE), autoregressive
transformers [32], and FastFlow [33]. Recent advancements,
such as the Learning Disentangled Priors (LDP) [34],
which combines model-driven low-rank representation with
data-driven deep learning, have improved anomaly detection
capabilities by effectively modeling both background and
anomalies through explicit and implicit priors. However, the
non-standardized nature of pavement distress images and
the influence of diverse field conditions present significant
challenges that necessitate the exploration of fully unsupervised feature extraction methods without reliance on weak
labels.

1878

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 2, FEBRUARY 2025

C. Unsupervised Representation Learning
Unsupervised representation learning enables deep neural
networks to be trained on large unlabeled visual datasets,
enhancing their ability to transfer knowledge to specific tasks.
One approach involves generative learning methods, which
extract information from images by masking most regions and
using the visible parts to reconstruct the hidden areas. For
instance, Zhou et al. effectively applied Masked Autoencoders
(MAE) for medical imaging tasks [15], while Sun et al.
introduced RingMo [35], which trains the remote sensing
foundation model using masked image modeling. Hong et al.
introduced SpectralGPT [16], a 3D generative pretrained
transformer specifically designed for spectral remote sensing
images, optimizing the analysis of complex datasets. While
this technique has been adapted for fields like remote sensing
and medical imaging, it faces challenges in pavement distress
images, where small targets may be obscured by similar
backgrounds, leading to inadequate reconstruction. Another
common approach is the use of Siamese networks, which aim
to place similar inputs close together in a shared embedding
space [36], [37], [38]. Dufumier et al. advanced this approach
by incorporating proxy metadata into their contrastive learning
framework [39], enhancing positive sampling and improving classification tasks in 3D brain MRI scans. Similarly,
Wang et al. proposed TransPath [19], a hybrid model that
utilizes self-supervised learning on unlabeled histopathological
images, achieving superior performance in downstream classification tasks. However, there is no clear agreement on the
best implementation practices, with some methods focusing
on predicting outcomes and others on comparing similarities
and differences between inputs. In data-limited areas such
as pavement distress diagnosis, it is crucial to thoroughly
evaluate and choose the most effective unsupervised methods.
Integrating deep learning visual explanation methods such as
Grad-CAM [40], Ablation-CAM [41], and Score-CAM [42]
presents opportunities for enabling pixel-level distress diagnosis via unsupervised learning. However, challenges remain,
including whether such methods can achieve fine-grained
segmentation for uniquely shaped distresses and whether comparatively small pavement datasets can sufficiently leverage
the potential of unsupervised learning. This study investigates
these challenges and explores potential solutions.
III. P ROPOSED A PPROACH
This section describes how the proposed prediction-based
Siamese network works and how does it achieve unsupervised
pixel-level pavement distress diagnosis.
A. Forward Propagation and Loss Functions
The network architecture, as shown in Figure 1, first extracts
an image x from the dataset X , and obtains two different
views v and v ′ through different data augmentation methods t
and t ′ , respectively. Then, v and v ′ are processed similarly.
They are first represented by the backbone network (e.g.,
ResNet or ViT), and then projected by MLP layers. The
difference is that branch 1 of the Siamese network will not
update the parameters through back propagation, but through

the momentum encoder. Then branch 2 network will predict
the output of branch 1 network by a predictor. The loss
function between the resulting vector z 1 = g( f (v1 )) and
p2 = q(g( f (v2 ))) is cross-entropy:
L(z 1 , p2 ) = − p2 log z 1

(1)

After each input of a pair of images, the network updates
constantly. To ensure the efficacy of the proposed approach,
the Siamese network is treated as a mutual binary classification
problem, i.e., to determine if the image input by the Siamese
network is augmented by the same image. Therefore, the
output vector is softmax processed, modifying Equation (1)
as follows:
L(softmax(z 1 ), softmax( p2 ))

(2)

Since branch 1 no longer uses backpropagation to update
its parameters, its gradient is no longer calculated. Therefore,
Equation (1) can be expressed as:
L(z 1 , stopgrad( p2 ))

(3)

Furthermore, a centering operation for the parameters of
branch 1 is applied, which is a bias term c added to the
network: g1 ( f (v)) ← g1 ( f (v)) + c. The center c is updated
with an exponential moving average:
B

1 X
N1 (xi )
c ← mc + (1 − m)
B

(4)

i=1

where B is the batch size, and N1 is the Siamese network 1,
m is a rate parameter. The pseudo-code implementation of
SiapaveNet is in Algorithm 1.
B. Avoiding Collapse
1) Momentum Encoder: SiapaveNet incorporates the use of
momentum encoders in branch 1 of the networks. The momentum encoder, introduced by [36], is a type of moving average
encoder that smoothens the data representations in contrastive
learning algorithms by employing exponential moving average
over multiple mini-batches of the data representations during
the training phase, instead of updating each representation
after every mini-batch. This mechanism reduces variance and
prevents overfitting. The utilization of momentum encoders in
SiapaveNet ensures stability and contributes to the final output
result. SiapaveNet employs three networks, f , g, and q, which
all make use of the momentum encoder, as summarized by the
following equation:
θt = αθt−1 + (1 − α)θt

(5)

where θ is the network parameter, t represents the iteration
step, and α is the smoothing parameter that controls the
moving average of the momentum encoder.
2) Stop-Gradient: The stop-gradient technique, commonly
utilized in conjunction with the momentum encoder, helps
in optimizing network by blocking gradients from flowing
through certain parts of the network during backpropagation.
This helps prevent overfitting and stabilize the training process
by preventing updates to positive example representations and

REN et al.: UNSUPERVISED LEARNING APPROACH FOR PAVEMENT DISTRESS DIAGNOSIS VIA SIAMESE NETWORKS

Algorithm 1 SiapaveNet Pseudo-Code, PyTorch-Like
# f: backbone
# g: projection mlp
# q: prediction mlp
# tpp, tpz: temperature parameters
# C: center
# load a minibatch x with n samples
for x in SiapaveN et:
v1, v2 = aug(x), aug(x) # random augmentation
y1, y2 = f(v1), f(v2) # representations
z1, z2 = g(y1), g(y2) # projections
p2 = q(z2) # predictions
L(p2, z1).backward() # loss and back-propagate
update(f, h) # SGD update
def L(p, z):
z = z.detach() # stop-gradient
p = softmax(p / tpp, dim=1)
z = softmax((z - C) / tpz, dim=1) # centering
# cross entropy
return - (p * log(z)).sum(dim=1).mean()

smoothing data representations through exponential moving
average, respectively. It is first introduced in by He et al. [36],
and the irreplaceable role of stop-gradient has been widely
recognized, as demonstrated by Chen and He [38]. SiapaveNet
also employs this optimization strategy for ensuring consistency across mini-batches and mitigating overfitting.
3) Centering: Inspired by SwAV [43], SiapaveNet employs
clustering centers to smooth the output. The clustering centers
serve as prototypes to represent clusters of similar data examples. This study calculates the average of the output of each
batch of branch 1 as the center. This center affects the output
of branch 1 as a bias term. It can be regarded as self-adaption
normalization process. The specific operation of centering has
been explained in Section III-A and Equation (5).
4) Batch Normalization: Batch normalization is widely
acknowledged as a pivotal aspect to avoid collapse, as discussed by [37]. It is a normalization technique applied to
the activations of neural networks, which helps mitigate the
internal covariate shift, i.e., the changes in activation distribution caused by weight updates during the training phase.
This technique stabilizes the training process and reduces the
sensitivity of the network to the initial weight values. However,
it can lead to a loss of discriminative information between
image pairs. This study shows its impact in Section V.
C. Unsupervised Distress Segmentation
To achieve unsupervised segmentation of pavement distress, the proposed method utilizes a ViT backbone network
(Figure 1), which is a transformer based architecture for
image classification tasks, proposed in the seminal work of

1879

Dosovitskiy et al. [44]. The architecture is designed to handle
large-scale image data by transforming the input image into
a sequence of fixed-length vectors, which are then processed
by a Transformer network. Self-attention block is a key component of the Transformer architecture, which enables ViT to
capture global information from the image input. Self-attention
is implemented by computing attention scores between all
vector tokens in the sequence, which can be represented
mathematically as:


QK T
V
(6)
Attention(Q, K , V ) = softmax √
dk
where Q, K , and V are the query, key, and value matrices,
respectively, and dk is the dimension of the key vectors. The
attention scores are then used to weigh the value vectors and
generate the output. This mechanism allows the network to
attend to different regions of the image and effectively capture long-range dependencies. By combining the self-attention
mechanism with the transformer architecture, ViT has achieved
state-of-the-art results on several benchmark datasets, demonstrating its effectiveness in large-scale image classification
tasks. In the proposed method, the attention mechanism of
ViT is aimed to utilize to segment pavement distress without
manual labeling. Specifically, the ViT is trained to attend to the
foreground of the input image, i.e., pavement distress, by calculating the attention score of each patch of the input image.
Later experimental chapters will demonstrate the effectiveness
of this approach.
D. Implement Details
1) Evaluation: The evaluation metrics utilized by SiapaveNet include mean Dice (mDice), mean Intersection over
Union (mIoU), mean Pixel Accuracy (mPA). These metrics
are commonly used to evaluate the performance of image
segmentation models, providing a comprehensive assessment
of the model accuracy and precision in classifying image
pixels. The mDice is defined as the average Dice coefficient
over all classes, mIoU is the average Intersection over Union
over all classes, and mPA is the average Pixel Accuracy over
all classes, calculated as:
PC
2 i=1
|GTi ∩ Pr edi |
m Dice =
(7)
(|GTi | + |Pr edi |)/C
PC
|GTi ∩ Pr edi |
m I oU = i=1
(8)
|GTi ∪ Pr edi |/C
PC
|GTi ∩ Pr edi |
m P A = i=1
(9)
|GTi |/C
where C is the number of classes, GTi is the set of ground
truth pixels for class i, and Pr edi is the set of predicted
pixels for class i. The Dice coefficient measures the overlap
between the predicted and ground truth segments, with a value
of 1 indicating perfect agreement.
Mean Average Precision (mAP) is used as an evaluation
metric to assess the performance of downstream tasks. The
mAP metric calculates the average performance of a detection
system across multiple object classes by computing precision
and recall values for each class and averaging the results.

1880

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 2, FEBRUARY 2025

TABLE I
C OMPARISON OF S IAPAVE N ET W ITH E XITING M ETHODS
ON C OPAVE DATASET

Fig. 2.

Examples of pavement distress images following Pre-processing.

2) Dataset and Other Details: Two datasets are used to
evaluate the pavement distress segmentation capability of the
proposed method. One is the continuous pavement images
dataset(copave dataset). It comprises of 1,000 large pavement
images, acquired via a pavement inspection vehicle. As a preprocessing step, these images are cropped into 88,088 smaller
images of size 256 × 256 pixels each. These images contain various forms of pavement distress, including transverse
cracks, longitudinal cracks, oblique cracks, alligator cracks,
potholes, and other forms, as shown in Figure 2. Another is the
pavementscapes dataset [45], we do the same pre-processing
to ensure a comparable results. An A40 GPU is employed for
the experiments, with a batch size of 64. AdamW is utilized
as the optimization and the learning rate is set to 0.0005. The
momentum parameter is set to 0.996.
IV. E XPERIMENT AND R ESULTS
In this section, two main outcomes of the proposed
approach, known as SiapaveNet, are presented. These include
pavement distress segmentation and transfer learning on
downstream tasks. To this end, the SiapaveNet framework
is firstly employed to train a ViT network, utilizing its
self-attention mechanism for unsupervised segmentation. Subsequently, the SiapaveNet framework is utilized to train a
ResNet-50 backbone, using it as a pre-trained network for
completing downstream tasks. Notably, the training process
in the SiapaveNet approach is fully unsupervised.
A. Pavement Distress Segmentation
1) Baselines: A comprehensive evaluation of the proposed SiapaveNet method was conducted in comparison
to several state-of-the-art unsupervised and semi-supervised
techniques with potential applications for pavement distress segmentation. As few pavement distress diagnosis
approaches are based on unsupervised or semi-supervised
learning, a set of methods demonstrating promising results
in fields like human disease detection, industrial defect identification, and other cutting-edge unsupervised representation
learning were selected. These included f-Anogan [27], FastFlow [33], GANormaly [29], MAE(Masked Autoencoders)
[13] and BEIT(Bidirectional Encoder representations from
Image Transformers) [14]. f-AnoGAN, GANormally, and FastFlow are anomaly detection methods that consider only normal

data during training, with an auto-encoder reconstructing
images. When abnormal images are input, the auto-encoder
cannot reconstruct anomalous regions, enabling their detection.
For this experiment, these baselines utilized only normal
pavement images during training. Conversely, MAE and BEIT
are unsupervised representation learning approaches that learn
effective image representations from unlabeled data. MAE
randomly masks out patches of the input image and is
trained to reconstruct the original unmasked image. BEIT
is a Transformer-based approach that learns representations
by predicting both the masked image patches and the visual
tokens obtained by performing various image transformations.
2) Results on Copave Dataset: Table I and Figure 3 demonstrate the superior performance of the proposed method for
pavement distress segmentation. It outperforms most unsupervised and semi-supervised methods, while requiring less
manual labeling effort. The method achieves an mDice of
0.523, mIoU of 0.366, and mPA of 0.807. Both mDice and
mIoU provide a balanced evaluation by considering the overlap
between the predicted and ground truth masks, with mDice
being more sensitive to instances with small areas, while mIoU
can be more influenced by instances with larger areas. Meanwhile, mPA computes the ratio of correctly classified pixels
averaged across instances, which may overestimate performance for small targets due to the dominance of background
pixels. In Table I, FastFlow obtains the highest mPA, but it
only assumes that the image does not contain pavement distress, and its effect is obviously inferior to that of SiapaveNet.
Figure 3 provides further visual evidence of the effectiveness
of the proposed method in achieving accurate pixel-level
pavement distress diagnosis. SiapaveNet can accurately locate
the distress pixels and differentiate pavement distress from the
background. While other anomaly detection schemes such as
f-AnoGAN and GANormaly can obtain the basic contour of
pavement distress, they are weaker than SiapaveNet across
various metrics. MAE and BEIT are deep representation learning methods using the same backbone network structure and
self-attention mechanism as the proposed method for segmentation. BEIT has shown better performance than other anomaly
detection schemes but weaker than the proposed SiapaveNet.
However, the masking patches and reconstructing of MAE
may not be well-suited for small pavement distress instances,
resulting in bad performance and weaker than most baselines.
These results suggest that the proposed SiapaveNet method is
a highly effective approach for pavement distress segmentation
and presents a viable alternative for semi-supervised anomaly
detection methods.

REN et al.: UNSUPERVISED LEARNING APPROACH FOR PAVEMENT DISTRESS DIAGNOSIS VIA SIAMESE NETWORKS

Fig. 3.

Comparative analysis of SiapaveNet with existing approaches for pavement distress segmentation.

Fig. 4.

Comparison of Self-attention methods with visual explanation methods for pavement distress segmentation.

Compared with anomaly detection methods, SiapaveNet
is an unsupervised approach, which do not use image-level
labels. As a result, it cannot segment pavement distress via
converting abnormal images into normal ones. SiapaveNet
uses a self-attention visualization scheme. It is compared
with other visual explanation techniques in Figure 4, including Grad-CAM and its variants. It is observed that the
self-attention visualization scheme more accurately segments
pavement distress when ViT is used as the backbone network of SiapaveNet. To investigate the performance of CNNs
without self-attention heads, experiments are conducted using
ResNet-50 and show regions of interest using Grad-CAM,
as illustrated in the last column of Figure 4. The results
indicate that CNNs can only focus on more obscure ranges,
highlighting the advantages of self-attention and ViT.

1881

Figure 5 displays the specific attention of different selfattention head. The brightness of the color serves as the
score of the attention head for that patch. The observations reveal that not all self-attention heads can accurately
focus on the foreground object (i.e., the pavement distress).
Specifically, self-attention head 0 and 3 show more attention
to the foreground object, while self-attention head 4 shows
more attention to the background (i.e., the pavement). Selfattention head 1, 2 and 3 are ambiguous. This pattern is
observed in all test images, leading to use self-attention
head 3 as the primary tool for segmenting pavement distress. This finding specifically addresses the second challenge
raised earlier, which is how to extract pavement distress
characteristics and distinguish foreground objects from the
background.

1882

Fig. 5.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 2, FEBRUARY 2025

Visualization of Self-attention mechanism in pavement distress segmentation.

TABLE II
C OMPARISON OF S IAPAVE N ET W ITH E XITING M ETHODS ON
PAVEMENTSCAPES DATASET

3) Results on Pavementscapes Dataset: We also evaluated
SiapaveNet against other methods using the pavementscapes
dataset. The results are presented in Table II. Our proposed
method outperforms other approaches across two evaluation
metrics, demonstrating its advanced capabilities. Notably,
traditional anomaly detection methods require manual classification of normal data, as the current dataset contains few
images of normal pavement. This process typically involves
manually labeling and training a deep learning classifier, which
may not perfectly capture the normal class. While we strive
to exclude distress images from the training data, manual
screening of large datasets is impractical, highlighting the
advantage of our proposed fully unsupervised learning scheme.
The results in Table II align with those in Table I, underscoring the consistency of the superior performance across
different datasets. Existing anomaly detection methods continue to perform poorly on this dataset, while BEIT achieves
the second-highest segmentation accuracy after our proposed
SiapaveNet.
B. Transfer Learning on Downstream Tasks
1) Tasks and Datasets: This section presents the outcomes
of finetuning a pre-trained ResNet-50, acquired from the unsupervised SiapaveNet framework, on three distinct downstream

tasks related to pavement distress diagnosis, namely pavement
crack semantic segmentation, object detection, and instance
segmentation. The pavement crack semantic segmentation task
entails segmenting cracks from pavement, while the object
detection task focuses on locating cracks on pavement. The
instance segmentation task aims to locate and roughly segment
the cracks on pavement.
These tasks are illustrated in Figure 6. To evaluate the performance of the proposed method, three different datasets are
used for each task: dataset I for semantic segmentation [23],
dataset II for object detection [46], and dataset III for instance
segmentation [47]. These datasets consist of 1896, 1538, and
133 images, respectively with dimensions of 640 × 360,
1612 × 1947, and 480 × 320. They are different from the
dataset used in pre-training.
2) Results: The evaluations presented in Figures 7, 8, and 9
demonstrate the effectiveness of the proposed approach in the
downstream tasks of semantic segmentation, object detection,
and instance segmentation. The metrics used for semantic
segmentation are mIoU, while mAP is used for both object
detection and instance segmentation. The results indicate that
the proposed method outperforms the training-from-scratch
method in terms of both convergence speed and accuracy in all
three tasks. When compared to networks pre-trained on labels
and a larger dataset such as ImageNet, the proposed approach
demonstrates a faster convergence speed and comparable
accuracy in semantic segmentation and instance segmentation,
while slightly lower performance in object detection. This
discrepancy in performance may be attributed to the larger
image size and increased information content of the dataset
used for object detection.
V. A BLATION S TUDY
This section presents the results of comprehensive ablation
experiments that investigate the impact of different settings
on the performance of SiapaveNet. The aim is to analyze the

REN et al.: UNSUPERVISED LEARNING APPROACH FOR PAVEMENT DISTRESS DIAGNOSIS VIA SIAMESE NETWORKS

Fig. 6.
Exploring three downstream tasks for pavement distress diagnosis: (a) Semantic segmentation, (b) Object detection, and (c) Instance
segmentation.

Fig. 7.

Semantic segmentation evaluation.

significance of each component of the system and how they
affect its overall performance.
A. Comparison With Similar Methods
Our primary objective is to investigate the potential of
unsupervised representation learning for pavement distress
segmentation. Previously, we demonstrated that our proposed
scheme outperforms generative learning models such as MAE

Fig. 8.

Object detection evaluation.

Fig. 9.

Instance segmentation evaluation.

1883

and BEiT. In this section, we compare various Siamese network methods that are conceptually similar to our proposed
approach, as illustrated in Figure 10. Specifically, we examine:
(1) MoCov3 [17]. It employs a prediction head and the
InfoNCE loss to compare the outputs of the Siamese network
branches;
(2) BYOL [37]. It utilizes a prediction head and the mean
squared error (MSE) loss to regress the output of one Siamese
network branch to the other;
(3) SimSiam [38]. It uses a prediction head and the negative
cosine similarity (NCS) loss, without a momentum encoder,
to measure the similarity between the output vectors of the
Siamese network branches;
(4) DINO [18]. It directly predicts the output of one Siamese
network branch from the other under cross entropy (CE) loss
without employing a prediction head;
(5) SiapaveNet (Ours). It incorporates a prediction head to
predict a vector from one branch of the Siamese network based
on the other branch under CE loss.
The results demonstrate that employing a prediction head
(predictor) combined with a cross-entropy loss function for the
classification task achieves the most effective performance as
shown in Table III. The proposed SiapaveNet method outperforms similar schemes across all evaluation metrics. Existing
self-supervised learning methods face limitations in pavement
distress detection tasks due to the subtle differences between

1884

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 2, FEBRUARY 2025

of probability distributions. While this enables complex relationship capture, its symmetric branch structure may limit
fine-grained feature separation. Our proposed SiapaveNet
addresses these challenges by employing an explicit prediction
head architecture with cross-entropy loss and high-dimensional
output. This approach provides implicit class labels and
detailed gradient information, enabling more detailed representation of subtle distress patterns. The cross-entropy loss
encourages the model to distinguish between different distress
classes, even when visually similar. The asymmetric Siamese
structure, combined with the prediction task, facilitates learning of invariant features while maintaining sensitivity to
fine-grained differences.
B. Different Settings on Predictor
1) Number of MLP Layers: One crucial hyperparameter
of the multi-layer perceptron (MLP) used as the predictor is
the number of layers. This section evaluates the influence of
MLP depth on the performance of the model while keeping
the previously determined optimal settings fixed. The results,
presented in Table IV, indicate that the best performance is
achieved when employing a 3-layer MLP as the predictor.
2) Output Dimension: Another crucial parameter is the
output dimension of the MLP prediction head, especially when
combined with the cross-entropy loss function. As demonstrated in Table V, a larger output dimension enables the model
to learn more detailed information, but at the cost of increased
computational overhead.
3) Batch Normalization: While previous study [37] suggests that batch normalization is crucial for maintaining model
stability and enhancing performance, our findings indicate that
excluding batch normalization from the prediction head yields
better results for the proposed model, as shown in Table VI.
C. Loss Functions

Fig. 10. Training pipeline of different methods: (a) MoCo v3, (b) BYOL,
(c) SimSiam, (d) DINO, and (e) SiapaveNet(ours).

foreground objects and consistent backgrounds. MoCo v3
employs the InfoNCE loss, a contrastive learning function
that maximizes mutual information between different views
of the same image while minimizing it for different images.
However, this approach struggles to capture fine-grained distinctions when images within a batch are highly similar. BYOL
uses a regression-based loss, predicting the consistency of the
output from other branch, which may lack the detail needed
for distinguishing subtle distress. The NCS loss in SimSiam,
focusing on feature vector similarity, potentially provides
insufficient supervision for subtle foreground differences.
DINO utilizes high-dimensional outputs and implicit labels
via softmax for cross-entropy loss, allowing direct comparison

As mentioned earlier, the results demonstrate that classification tasks employing a combination of a prediction head
(predictor) and a cross-entropy loss function yield the most
effective performance. However, the results also compare
the differences between various networks. In this section,
we utilize the exact same network architecture to evaluate
the impact of the loss function on the results. Specifically,
we compare three commonly used loss functions: InfoNCE
loss, negative cosine similarity (NCS) loss, and cross-entropy
(CE) loss. Interestingly, when we fixed the optimal settings
obtained in the previous section, only the CE loss and NCS
loss enabled the model to function properly as shown in
Table VII. InfoNCE failed to decrease the loss, resulting
in a collapse of the self-supervised mapping. This collapse
manifested as each image patch exhibiting the same value,
indicating a failure in learning meaningful representations.
D. Centering
Centering is an important technique that ensures stable
convergence of the network. For the predicting classification
task of the proposed method, it is necessary to maintain sufficient stability in the predicted network. In fact, the predicted

REN et al.: UNSUPERVISED LEARNING APPROACH FOR PAVEMENT DISTRESS DIAGNOSIS VIA SIAMESE NETWORKS

1885

TABLE III
C OMPARISON W ITH OTHER S IMILAR M ETHODS

TABLE IV
C OMPARISON OF D IFFERENT N UMBER OF MLP L AYERS

TABLE V
C OMPARISON OF D IFFERENT O UTPUT D IMENSION

Fig. 11.
Comparison of loss convergence between SGD and AdamW
optimizers.

TABLE VI
C OMPARISON ON BATCH N ORMALIZATION

TABLE VII
C OMPARISON OF D IFFERENT L OSS F UNCTIONS

TABLE VIII
C OMPARISON ON C ENTERING

decoupled weight decay (AdamW) optimizer. The results show
that the model does not converge when trained using SGD,
as evidenced by the non-decreasing trend in the loss curve
shown in Figure 11. This suggests that the choice of optimization algorithm has a significant impact on the performance of
the SiapaveNet. Compared to SGD, AdamW is found to be
more effective in optimizing the SiapaveNet, as indicated by
the decrease in loss over the course of training. This outcome
is consistent with the findings of prior studies [48], [49],
which have shown that Adam and its variants such as AdamW
and AMSGrad can outperform SGD in the training of visual
representations. This difference in performance is attributed
to the nature of the ViT network, which has been shown to
be less prone to overfitting. The faster convergence of the
network with AdamW may therefore be a result of its ability
to reduce the loss more effectively in such a scenario. This
hypothesis is further supported by the successful convergence
of the ResNet-50 when trained with SGD, as presented in
Section IV-B.2.
VI. D ISCUSSION

network utilizes stop-gradient and centering techniques, and
its parameters are updated through the momentum encoder.
This configuration significantly enhances performance of the
model, as evidenced by the results presented in Table VIII.
E. Optimizer
This section aims to evaluate the performance of the
proposed SiapaveNet when trained using stochastic gradient descent (SGD) and adaptive moment estimation with

Unsupervised deep learning represents a promising direction
for the future advancement of pavement distress diagnosis.
It has achieved significant success in natural language processing, general computer vision, and other fields due to
the scarcity of labeled data compared to the vast amount of
unlabeled data available. For the task of pavement distress
diagnosis, unsupervised learning is a critical tool to address
the challenge of expensive and limited labeling of pavement
distress types. This study makes an exploratory effort to assess
the potential and limitations of unsupervised pavement distress
diagnosis.

1886

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 2, FEBRUARY 2025

An important aspect of this study is the effects of different techniques on the stable convergence and performance
of unsupervised pavement distress diagnosis methods. The
unique shape of the pavement distress object makes ensuring
stable convergence a difficult problem. Technically, we aim
to identify specific measures within the Siamese network
framework to achieve better pavement distress segmentation
performance. Comprehensive ablation experiments demonstrate that employing a predicting classification task using
a prediction head and cross-entropy loss function is more
suitable for this task compared to other existing methods.
We posit that ensuring stable variation in the predicted branch
while maintaining flexibility in the predicting branch is a
crucial element. This could explain why the predicting branch
requires a prediction head, needs to be updated by backpropagation without batch normalization, while the predicted
branch should be kept as stable as possible, updated with a
momentum encoder, and incorporate stop-gradient and centering techniques. Besides, we speculate that a larger output
dimension of the prediction head incentivizes the network to
learn more detailed information. We hypothesize that if the
classification task merely requires determining whether the
predicting branch belongs to the same class as the predicted
branch, the network may easily converge to suboptimal solutions or learn shortcut strategies. In addition, it is observed
that the AdamW optimizer performs better when training ViT
networks, while the SGD optimizer performs better when
training CNN networks, similar to supervised learning. These
findings provide valuable insights for future unsupervised
pavement distress diagnosis methods.
It is a significant advantage that the unsupervised
learning-based approach can identify rare types of distress that
are difficult to label beforehand, when faced with a small
sample of tasks [27], [29], [30]. In addition, unsupervised
learning may have a greater advantage when dealing with tasks
with limited samples. The experimental results show that when
trained with only 133 images over 5 epochs, the accuracy
of the unsupervised pre-training model is more than double
that of the supervised pre-training model commonly used in
the field. Several studies [17], [36] have suggested that the
distribution of unsupervised and supervised learning differs
significantly, with unsupervised learning having the ability to
identify distinct clusters or patterns, which is advantageous
when dealing with the unusual form of pavement distress. This
may also explain the results of the semantic segmentation task,
as shown in Figure 7. When faced with the object detection
task in Figure 8, our results are not as good as those obtained
using the supervised pre-training model based on ImageNet.
The large pixel size of the dataset for this task (nearly 50 times
that of the pre-training image), the substantial difference
between the object detection and the object segmentation task,
and the presence of a specific target, pavement irrigation
sewing, in the target dataset may be contributing factors.
The dataset used in this study comprises pavement images
captured by continuous sections, totaling 88,000 small images,
which represents a significant improvement over previous
methods in terms of the number of images that can be processed. However, there is still a considerable gap compared to

datasets in other fields such as the COCO dataset [50], which
contains 330,000 images. Our work makes efforts to expand
the dataset by using common data augmentation methods. And
it is demonstrated that using artificially generated data with
weak labels is possible to expand datasets according to recent
studies [18], [51], [52]. This may be an effective solution and
our future research direction.
Although pixel-level unsupervised deep learning is not yet
fully mature for direct application in real-world pavement
distress diagnosis projects due to its current limitations, it has
shown promising potential for improving downstream tasks.
Furthermore, even with limited evaluation, it can provide valuable insights for decision-making in pavement maintenance
systems without relying on time-consuming manual labeling.
Moving forward, larger and more comprehensive datasets,
advanced data augmentation techniques, and more powerful
models are expected to significantly enhance the accuracy of
pixel-level unsupervised deep learning in pavement distress
diagnosis.
VII. C ONCLUSION
This study proposes a novel self-supervised approach for
pixel-level pavement distress diagnosis, effectively addressing the challenges of extracting fine-grained features in
complex and similar backgrounds. By employing a prediction task with an explicit prediction head and integrating
ViTs with self-attention mechanisms, the method enables
precise distress segmentation without the need for labeled
data. Extensive experimental results demonstrate the superior performance of this approach over existing unsupervised
representation learning and anomaly detection baselines. Furthermore, as a pre-training strategy, the proposed method
significantly enhances the accuracy and convergence speed of
backbone networks in downstream pavement distress diagnosis
tasks compared to conventional supervised pre-training on
ImageNet. This approach offers a promising pathway for
improving pavement maintenance decision-making through
reliable unsupervised distress detection. It facilitates more
effective identification and prioritization of repair needs,
thereby extending infrastructure longevity and reducing maintenance costs.
R EFERENCES
[1] T. F. Fwa, W. T. Chan, and K. Z. Hoque, “Multiobjective optimization for
pavement maintenance programming,” J. Transp. Eng., vol. 126, no. 5,
pp. 367–374, Sep. 2000.
[2] C. Torres-Machi, E. Pellicer, V. Yepes, and A. Chamorro, “Towards a
sustainable optimization of pavement maintenance programs under budgetary restrictions,” J. Cleaner Prod., vol. 148, pp. 90–102, Apr. 2017.
[3] W. Chen and M. Zheng, “Multi-objective optimization for pavement
maintenance and rehabilitation decision-making: A critical review
and future directions,” Autom. Construct., vol. 130, Oct. 2021,
Art. no. 103840.
[4] K. C. Wang and W. Gong, “Real-time automated survey system of
pavement cracking in parallel environment,” J. Infrastruct. Syst., vol. 11,
no. 3, pp. 154–164, Sep. 2005.
[5] L. Ying and E. Salari, “Beamlet transform-based technique for pavement
crack detection and classification,” Comput.-Aided Civil Infrastruct.
Eng., vol. 25, no. 8, pp. 572–580, Nov. 2010.
[6] Q. Zou, Y. Cao, Q. Li, Q. Mao, and S. Wang, “CrackTree: Automatic
crack detection from pavement images,” Pattern Recognit. Lett., vol. 33,
no. 3, pp. 227–238, Feb. 2012.

REN et al.: UNSUPERVISED LEARNING APPROACH FOR PAVEMENT DISTRESS DIAGNOSIS VIA SIAMESE NETWORKS

[7] A. Cubero-Fernandez, F. J. Rodriguez-Lozano, R. Villatoro, J. Olivares,
and J. M. Palomares, “Efficient pavement crack detection and classification,” EURASIP J. Image Video Process., vol. 2017, no. 1, pp. 1–11,
Dec. 2017.
[8] Y. Hou et al., “MobileCrack: Object classification in asphalt pavements
using an adaptive lightweight deep learning,” J. Transp. Eng., Part B,
Pavements, vol. 147, no. 1, Mar. 2021, Art. no. 04020092.
[9] Z. Qu, C. Cao, L. Liu, and D.-Y. Zhou, “A deeply supervised convolutional neural network for pavement crack detection with multiscale
feature fusion,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 9,
pp. 4890–4899, Sep. 2022.
[10] Z.-X. Lan and X.-M. Dong, “MiniCrack: A simple but efficient convolutional neural network for pixel-level narrow crack detection,” Comput.
Ind., vol. 141, Oct. 2022, Art. no. 103698.
[11] H. Yao, Y. Liu, X. Li, Z. You, Y. Feng, and W. Lu, “A detection
method for pavement cracks combining object detection and attention mechanism,” IEEE Trans. Intell. Transp. Syst., vol. 23, no. 11,
pp. 22179–22189, May 2022.
[12] H. Yao, Y. Liu, H. Lv, J. Huyan, Z. You, and Y. Hou, “Encoder–
decoder with pyramid region attention for pixel-level pavement crack
recognition,” Computer-Aided Civil Infrastructure Eng., vol. 39, no. 10,
pp. 1490–1506, May 2024.
[13] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 16000–16009.
[14] H. Bao, L. Dong, S. Piao, and F. Wei, “BEiT: BERT pre-training of
image transformers,” 2021, arXiv:2106.08254.
[15] L. Zhou, H. Liu, J. Bae, J. He, D. Samaras, and P. Prasanna, “Self
pre-training with masked autoencoders for medical image classification
and segmentation,” in Proc. IEEE 20th Int. Symp. Biomed. Imag. (ISBI),
Apr. 2023, pp. 1–6.
[16] D. Hong et al., “SpectralGPT: Spectral remote sensing foundation
model,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 46, no. 8,
pp. 5227–5244, Aug. 2024.
[17] X. Chen, S. Xie, and K. He, “An empirical study of training selfsupervised vision transformers,” in Proc. IEEE/CVF Int. Conf. Comput.
Vis. (ICCV), Oct. 2021, pp. 9640–9649.
[18] M. Caron et al., “Emerging properties in self-supervised vision transformers,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021,
pp. 9650–9660.
[19] X. Wang et al., “TransPath: Transformer-based self-supervised learning
for histopathological image classification,” in Proc. Int. Conf. Med.
Image Comput. Comput.-Assist. Intervent., 2021, pp. 186–195.
[20] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.
[21] O. Ronneberger, P. Fischer, and T. Brox, “U-Net: Convolutional networks for biomedical image segmentation,” in Proc. 18th Int. Conf.
Med. Image Comput. Comput.-Assist. Intervent., vol. 9351. Cham,
Switzerland: Springer, 2015, pp. 234–241.
[22] J. Long, E. Shelhamer, and T. Darrell, “Fully convolutional networks
for semantic segmentation,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2015, pp. 3431–3440.
[23] F. Yang, L. Zhang, S. Yu, D. Prokhorov, X. Mei, and H. Ling, “Feature
pyramid and hierarchical boosting network for pavement crack detection,” IEEE Trans. Intell. Transp. Syst., vol. 21, no. 4, pp. 1525–1535,
Apr. 2020.
[24] C. Xiang, W. Wang, L. Deng, P. Shi, and X. Kong, “Crack detection
algorithm for concrete structures based on super-resolution reconstruction and segmentation network,” Autom. Construction, vol. 140,
Aug. 2022, Art. no. 104346.
[25] K. Zhang, Y. Zhang, and H.-D. Cheng, “CrackGAN: Pavement crack
detection using partially accurate ground truths based on generative
adversarial learning,” IEEE Trans. Intell. Transp. Syst., vol. 22, no. 2,
pp. 1306–1319, Feb. 2021.
[26] H. Liu, X. Miao, C. Mertz, C. Xu, and H. Kong, “CrackFormer: Transformer network for fine-grained crack detection,” in Proc. IEEE/CVF
Int. Conf. Comput. Vis. (ICCV), Oct. 2021, pp. 3783–3792.
[27] T. Schlegl, P. Seeböck, S. M. Waldstein, G. Langs, and U. SchmidtErfurth, “F-AnoGAN: Fast unsupervised anomaly detection with
generative adversarial networks,” Med. Image Anal., vol. 54, pp. 30–44,
May 2019.
[28] J. Huang, C. Li, Y. Lin, and S. Lian, “Unsupervised industrial
anomaly detection via pattern generative and contrastive networks,”
2022, arXiv:2207.09792.

1887

[29] S. Akcay, A. Atapour-Abarghouei, and T. P. Breckon, “GANomaly:
Semi-supervised anomaly detection via adversarial training,” in Proc.
14th Asian Conf. Comput. Vis., Dec. 2019, pp. 622–637.
[30] M. M. R. Siddiquee et al., “Learning fixed points in generative adversarial networks: From image-to-image translation to disease detection
and localization,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2019, pp. 191–200.
[31] Y. Shi, J. Yang, and Z. Qi, “Unsupervised anomaly segmentation
via deep feature reconstruction,” Neurocomputing, vol. 424, pp. 9–22,
Feb. 2021.
[32] W. Hugo Lopez Pinaya et al., “Unsupervised brain anomaly detection
and segmentation with transformers,” 2021, arXiv:2102.11650.
[33] J. Yu et al., “FastFlow: Unsupervised anomaly detection and localization
via 2D normalizing flows,” 2021, arXiv:2111.07677.
[34] C. Li, B. Zhang, D. Hong, X. Jia, A. Plaza, and J. Chanussot, “Learning
disentangled priors for hyperspectral anomaly detection: A coupling
model-driven and data-driven paradigm,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 3, no. 1, pp. 1–14, Apr. 2024.
[35] X. Sun et al., “RingMo: A remote sensing foundation model with
masked image modeling,” IEEE Trans. Geosci. Remote Sens., vol. 61,
2022, Art. no. 5612822.
[36] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum
contrast for unsupervised visual representation learning,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020,
pp. 9729–9738.
[37] J.-B. Grill et al., “Bootstrap your own latent-a new approach to selfsupervised learning,” in Proc. 34th Int. Conf. Neural Inf. Process. Syst.,
2020, pp. 21271–21284.
[38] X. Chen and K. He, “Exploring simple Siamese representation learning,”
in Proc. IEEE Comput. Soc. Conf. Comput. Vision Pattern Recognit.,
Jun. 2021, pp. 15750–15758.
[39] B. Dufumier et al., “Contrastive learning with continuous proxy metadata for 3D MRI classification,” in Proc. Int. Conf. Med. Image Comput.
Comput.-Assist. Intervent., 2021, pp. 58–68.
[40] R. R. Selvaraju, M. Cogswell, A. Das, R. Vedantam, D. Parikh, and
D. Batra, “Grad-CAM: Visual explanations from deep networks via
gradient-based localization,” in Proc. IEEE Int. Conf. Comput. Vis.
(ICCV), Oct. 2017, pp. 618–626.
[41] S. Desai and H. G. Ramaswamy, “Ablation-CAM: Visual explanations for deep convolutional network via gradient-free localization,”
in Proc. IEEE Winter Conf. Appl. Comput. Vis. (WACV), Mar. 2020,
pp. 972–980.
[42] H. Wang et al., “Score-CAM: Score-weighted visual explanations for convolutional neural networks,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. Workshops (CVPRW), Jun. 2020,
pp. 24–25.
[43] M. Caron, I. Misra, J. Mairal, P. Goyal, P. Bojanowski, and A. Joulin,
“Unsupervised learning of visual features by contrasting cluster assignments,” in Proc. NIPS, Dec. 2020, pp. 9912–9924.
[44] A. Dosovitskiy et al., “An image is worth 16×16 words: Transformers
for image recognition at scale,” 2020, arXiv:2010.11929.
[45] Z. Tong, T. Ma, J. Huyan, and W. Zhang, “Pavementscapes: A large-scale
hierarchical image dataset for asphalt pavement damage segmentation,”
2022, arXiv:2208.00775.
[46] R. Ren, F. Liu, P. Shi, H. Wang, and Y. Huang, “Preprocessing of crack
recognition: Automatic crack-location method based on deep learning,”
J. Mater. Civil Eng., vol. 35, no. 3, Mar. 2023, Art. no. 04022452.
[47] X. Xu et al., “Crack detection and comparison study based on
faster R-CNN and mask R-CNN,” Sensors, vol. 22, no. 3, p. 1215,
Feb. 2022.
[48] A. Kolesnikov, X. Zhai, and L. Beyer, “Revisiting self-supervised visual
representation learning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2019, pp. 1920–1929.
[49] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, “A simple framework
for contrastive learning of visual representations,” in Proc. 37th Int.
Conf. Mach. Learn., vol. 119, Jul. 2020, pp. 1597–1607.
[50] T. Lin et al., “Microsoft COCO: Common objects in context,” in Proc.
Eur. Conf. Comput. Vis., 2014, pp. 740–755.
[51] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Selfsupervised learning for anomaly detection and localization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 9664–9674.
[52] J. Kim, D. Kim, S. Lee, and S. Chi, “Hybrid DNN training using
both synthetic and real construction images to overcome training data
shortage,” Autom. Construct., vol. 149, May 2023, Art. no. 104771.

1888

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 2, FEBRUARY 2025

Ruiqi Ren received the B.E. degree from Central
South University, Changsha, China. He is currently
pursuing the Ph.D. degree with the School of Rail
Transportation, Soochow University, Suzhou, China.
His research interests include the application of
deep learning and computer vision techniques for
infrastructure health monitoring, with a particular
interest in developing efficient, automated methods
for pavement distress diagnosis, and structural health
assessment.

Peixin Shi received the Ph.D. degree in civil and
environmental engineering from Cornell University.
He is currently a Full Professor with the School
of Rail Transportation, Soochow University. His
research interests include tunneling and underground
space technology, smart infrastructure systems for
underground environments, and lifeline earthquake
engineering.

Pengjiao Jia received the Ph.D. degree in geotechnical engineering from Northeastern University. He is
currently an Associate Professor of geotechnical
engineering with the School of Rail Transportation,
Soochow University (PRC). His research has been
recognized by 56 technical articles and more than ten
patents. His research interests include pipelines and
trenchless technology, pipe jacking, and tunneling.

Jinwoo Kim received the Ph.D. degree in civil
and environmental engineering from Seoul National
University, South Korea. He is currently with
the Department of Civil and Environmental Engineering, Hanyang University, South Korea, as an
Assistant Professor. His long-term goal is to
realize human-centered digitalization and robotic
automation in the construction industry. To this
end, he researches how to leverage and integrate
emerging artificial intelligence and automation technologies with long-established human theories and
knowledge.
PAPER_TEXT
