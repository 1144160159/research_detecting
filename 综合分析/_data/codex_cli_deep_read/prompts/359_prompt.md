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
# [359] Adversarial Transformer-Based Anomaly Detection for Multivariate Time Series
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
编号：359
题名：Adversarial Transformer-Based Anomaly Detection for Multivariate Time Series
年份：2024
DOI：10.1109/tii.2024.3507211
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2024.3507211.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\359.txt
- 原始字符数：49794
- 本次发送字符数：49794
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 3, MARCH 2025

2471

Adversarial Transformer-Based Anomaly
Detection for Multivariate Time Series
Xinying Yu , Kejun Zhang , Yaqi Liu , Bing Zou , Jun Wang, Wenbin Wang, and Rong Qian

Abstract—Anomaly detection in multivariate time series
is crucial to monitor system status, such as fault detection
in industrial systems. However, detecting anomalies in multivariate time series is challenging due to few labels, complex spatiotemporal correlations, and ultrafast detecting
demands. Existing anomaly detection methods rarely address these challenges simultaneously. Herein, we design
an adversarial transformers-based unsupervised anomaly
detection model (ATUAD). In ATUAD, a Transformer-based
encoder–decoder is constructed to learn sequence features, and adversarial training is adopted to amplify
mild anomalies and enhance the robustness. Besides, we
propose a peak-over-threshold-based dynamic threshold
mechanism to improve the anomaly detection performance
of ATUAD by automatically determining the threshold. In
addition, we provide an anomaly explanation method to
help ATUAD pinpoint root causes for anomalies. Comparison experiments, ablation studies, and overhead analysis
on public datasets show that ATUAD can outperform the
state-of-the-art baseline methods.
Index Terms—Adversarial training, anomaly detection,
multivariate time series, self-attention, transformer.

I. INTRODUCTION
HE proliferation of Internet of Things (IoT) devices leads
to a large amount of real-time data with more complexity
generated across cyber-physical systems [1]. This kind of data
consists of several variables (or features), which change over
time and are known as multivariate time-series data. IoT applications, such as smart factories or supply chain systems [2],
typically adopt multivariate time series to monitor system status. However, harsh natural environments, sensors’ hardware
problems, or network attacks may result in anomalous data. A
general definition of an anomaly within the context of IoT is the
measurable consequences of an unexpected change in the state

T

Received 16 November 2023; revised 26 March 2024 and 3 September 2024; accepted 9 November 2024. Date of publication 13 December
2024; date of current version 5 March 2025. This work was supported
in part by BUPT Excellent Ph.D. Students Foundation under Grant
CX2023221 and in part by the Fundamental Research Funds for the
Central Universities under Grant 3282023012 and Grant 3282023033.
Paper no. TII-23-4563. (Corresponding author: Kejun Zhang.)
Xinying Yu, Kejun Zhang, and Wenbin Wang are with the School of Cyberspace Security, Beijing University of Posts and Telecommunications,
Beijing 102206, China (e-mail: xinying_334@bupt.edu.cn; nybsftbk@
126.com; lalalaouye@163.com).
Yaqi Liu, Bing Zou, Jun Wang, and Rong Qian are with the Department of Cyberspace Security, Beijing Electronic Science and Technology Institute, Beijing 100070, China (e-mail: liuyaqi@besti.edu.cn; bingbingliang@126.com; william_jun576@163.com; rqian@besti.edu.cn).
Digital Object Identifier 10.1109/TII.2024.3507211

of a system that is outside of its local or global norm [3]. The
anomalous data can affect the correctness of IoT application
decisions, reduce the quality of IoT services, and cause economic losses. Therefore, it becomes a material issue to detect
anomalous data for core tasks in IoT.
Anomaly detection usually involves the identification of novel
or unexpected observations or sequences within the captured
data. Unfortunately, anomaly detection in multivariate timeseries data is more arduous because of the complex spatiotemporal correlations and ultrafast detection demands. Moreover,
there is no shortage of mild anomalies close to normality in
multivariate time series with few or no labels, which complicates
anomaly detection. Therefore, it is paramount to investigate
unsupervised anomaly detection for multivariate time series.
To detect anomalies in multivariate time series, numerous
deep learning-based unsupervised anomaly detection algorithms
have been proposed [4]. The most representative deep learning
methods include convolutional neural networks (CNNs) [5],
[6], recurrent neural networks (RNNs) [7], and generative adversarial networks (GANs) [8], [9]. Researchers often subtly
combine CNNs and RNNs to construct more effective anomaly
detection models. However, recurrent models, such as LSTMs,
are known to be computationally expensive, and CNNs fail to
capture long-distance features, which are unsuitable for environments requiring high computational efficiency (e.g., IoT) [10].
GAN-based anomaly detection methods train both generators
and discriminators in an adversarial manner and use the trained
discriminators as anomaly detectors. Regrettably, GAN is prone
to problems, such as pattern collapse and nonconvergence during
the training process [11].
Recent studies have shown the powerful capacity of Transformers to enhance sequence modeling and decrease computational overheads [12]. The Transformer is a network architecture
eschewing recurrence and convolutions and instead depending
solely on attention mechanisms [13]. Besides, the Transformer
can process long sequences in parallel, and its accuracy and
training time are almost unaffected by the sequence length [14].
However, using only the simple Transformer-based encoder–
decoder model leans toward neglecting anomalies if they are
relatively verge on normality. The adversarial training of GAN
can magnify the reconstruction error of anomalous data, helping
the Transformer model to identify mild anomalies while gaining
stability. Thus, we jointly consider Transformer and adversarial training to implement anomaly detection and diagnosis for
multivariate time series.

1941-0050 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

2472

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 3, MARCH 2025

In this article, an adversarial transformer-based unsupervised
anomaly detection model (ATUAD) is developed to deal with
the complex spatiotemporal correlations and mild anomalies
undetected issues in multivariate time series and fast detection
demands in modern applications. Specifically, we construct
a Transformer-based encoder–decoder architecture associated
with an adversarial training framework to capture long-distance
contextual information while alleviating the omission of mild
anomalies. Further, we propose a peak-over-threshold (POT)
method-based dynamic threshold (PDT) mechanism and introduce it into ATUAD to determine the threshold for detecting
anomalies. Then, we conduct an anomaly explanation on the
detected anomalous windows to help pinpoint anomaly root
causes. By performing extensive experiments, we corroborate
that ATUAD outperforms most baselines under diversified metrics. The main contributions are as follows.
1) A novel ATUAD is proposed for multivariate time series.
Specifically, in our ATUAD, a shared encoder-different
decoder branch is elaborately designed in a transformer
style to form two transformer blocks. ATUAD executes
reconstruction training by minimizing the reconstruction
errors.
2) An adversarial training is designed by integrating with
our carefully devised transformer blocks. ATUAD executes adversarial training across two transformer blocks,
and one block maximizes reconstruction errors while the
other minimizes ones. The adversely trained transformer
networks oblige ATUAD to improve detecting accuracy
while gaining stability.
3) A PDT is proposed to choose the threshold. PDT improves
the streaming POT (SPOT) and learns a global threshold
from the anomaly scores to detect anomalous windows,
which supplies the benefit of being able to update the
threshold automatically. Further, an anomaly explanation
method is provided to help ATUAD pinpoint anomaly root
causes. Extensive experiments on public datasets verify
the effectiveness of ATUAD in detecting performance and
training efficiency.
The rest of this article is organized as follows. Section II
overviews the works related to the anomaly detection of multivariate time series. Section III constructs the ATUAD and
elaborates on the process of anomaly inference. Section IV
analyzes the experimental results of ATUAD and the baseline
methods. Finally, Section V concludes this article.
II. RELATED WORK
Deep learning methods have a strong ability to handle nonlinearity in temporal correlation and have achieved remarkable
results in many time-series anomaly detection methods.
In pursuit of higher detection accuracy, many time series anomaly detection efforts have applied recurrent neural
networks. Zhang et al. [15] proposed MSCRED, which employs
a multiscale convolutional encoder–decoder and a temporal
attention-based convLSTM for anomaly detection and diagnosis
in multivariate time series. MSCRED achieves anomaly detecting, anomaly root identifying, and anomaly severity reflecting,

which effectively help system operators perform timely system
diagnosis and repair. However, the model uses a given anomaly
threshold for detection, which makes the model less applicable
and less general. Su et al. [16] proposed OmniAnomaly, a
stochastic recurrent neural network for multivariate time series
anomaly detection. OmniAnomaly learns a robust representation
of data using techniques, such as stochastic variable connection
and planar normalizing flow, and identifies anomalies based on
reconstruction probabilities. The method achieves remarkable
anomaly detection performance and anomaly interpretation accuracy, but at the cost of high training time. MAD-GAN [17] is
an unsupervised multivariate anomaly detection method based
on generative adversarial networks. The generators and discriminators of GANs use LSTM to capture the temporal correlation in
time series distributions. However, the model is computationally
expensive and cannot effectively model large sequences.
Subsequently, research scholars have increasingly emphasized the inference efficiency of anomaly detection methods.
Zong et al. [18] proposed DAGMM, an unsupervised anomaly
detection model combining a deep autoencoder and a Gaussian
mixture model. The deep autoencoder compresses the data
points into a low-dimensional representation and inputs the
Gaussian mixture model to evaluate the density of the representation. However, the model targets multivariate variables rather
than multivariate time series, ignoring the inherent time dependence of the time series. Audibert et al. [11] proposed USAD, a
multivariate time series unsupervised anomaly detection method
based on autoencoder and adversarial training. USAD processes
sequence data through an autoencoder with two decoders and an
adversarial training framework, and determines anomalies based
on reconstruction errors. Compared with prior art, USAD can
significantly reduce training time. However, both the encoder
and decoder in the model use fully connected neural networks,
which sometimes cannot extract sequence features effectively.
The transformer architecture is favored by more and more
researchers, which provides a new direction for time series anomaly detection. Chen et al. [10] proposed GTA, a
Transformer-based framework for anomaly detection that uses
the introduced connection learning policy to automatically learn
sensor dependencies. Also, an influence propagation graph convolution is applied to simulate the information flow among the
sensors in the graph. They claimed that the inference speed of the
multibranch attention technique is improved without sacrificing
model performance. Tuli et al. [14] proposed Transformerbased anomaly detection and diagnosis (TranAD). TranAD uses
the attention-based Transformer encoder–decoder framework,
focuses score-based self-adjustment, and adversarial training
to reconstruct time-series data, achieving superior detection
performance and training efficiency on multiple datasets. Xu
et al. [19] proposed TGAN-AD, a transformer-based GAN
method for anomaly detection, whose generator aids in extracting contextual features of time-series data, and discriminator
assists in determining abnormal data. They measure the anomalies by calculating both the reconstruction loss of the generator
and the discrimination loss of the discriminator. Li et al. [20]
proposed a dilated convolutional transformer-based GAN (DCTGAN) to solve the problems of time series anomaly detection.

YU et al.: ADVERSARIAL TRANSFORMER-BASED ANOMALY DETECTION FOR MULTIVARIATE TIME SERIES

Fig. 1.

2473

Data formulation of the multivariate time series.

DCT-GAN utilizes several generators and a single discriminator
to alleviate the mode collapse problem. Each generator consists
of a dilated convolutional neural network and a Transformer
block to obtain fine-grained and coarse-grained information
about the time series. The experiments on the NAB dataset show
that DCT-GAN is more accurate and stable than most other
methods. Despite their effectiveness, they are few to consider
the temporal dependency, mild abnormalities, and inference
efficiency, simultaneously. Therefore, we propose ATUAD to
cope with the above problems and improve the precision and
efficiency of anomaly detection with low computational cost.
III. ATUAD MODEL
A. Problem Statement
In this article, the training data (i.e., multivariate time series)
X = {x1 , x2 , . . ., xN } ∈ Rk×N are composed of the measurement data of k sensors over N consecutive timestamps. As
shown in Fig. 1, the observation xt ∈ Rk at any timestamp t
is a k-dimensional vector representing the measurement data of
k sensors, and xit denotes the value of the ith sensor Si at the
timestamp t. Particularly, the univariate time series X ∈ Rk×N
(k = 1) is a special case in the multivariate setting, where xt
is a scalar. Similar to previous unsupervised anomaly detection works, this article only models sequence on normal data
(without anomalies) and detects anomalies on test data (with
anomalies). To model the dependence between the observation
xt and the historical ones, we consider a slide time window Wt =
{xt−L+1 , . . ., xt } of length L, both for training and testing. Instead of using the original multivariate time series X, a sequence
of windows W = {W1 , . . ., WT } serves as the model’s input.
We utilize the replication padding [19] to maintain each window
length as L, i.e., Wt = {x1 , . . ., xt , . . ., xt } when t < L. Our
model takes as inputs Wtrain = {W1 , . . ., WT } for training and
Ŵtest = {Ŵ1 , . . ., ŴT̂ } for testing and assigns a binary label for
each testing window Ŵt to indicate an anomaly or not based on
the global threshold and the window’s anomaly score. We now
formalize the two problems of anomaly detection and diagnosis.
Anomaly detection: Given testing data Ŵtest = {Ŵ1 , . . .,
ŴT̂ }, predict binary labels y = {y1 , . . ., yT̂ }, where yt ∈ {0, 1}
indicates whether the window Ŵt at timestamp t is anomalous
(yt = 1) or not (yt = 0).

Fig. 2. Overall architecture of ATUAD. In the visualization of ATUAD’s
architecture with one encoder layer and two decoder layers, three components form two transformer blocks by sharing the same Encoder. The
encoder encodes the concatenation of the input window and the position
encoding and projects it to a latent variable, which then undergoes two
decoders to generate reconstructions. The two transformer blocks are
trained in an adversarial way, where Transformer1 seeks to fool Transformer2, and Transformer2 aims to distinguish the input reconstructed
by Transformer1 from the real data.

Anomaly diagnosis: Given the above detection results y =
{y1 , . . ., yT̂ }, recognize the sensors most likely responsible for
the anomalies within the anomalous window Ŵt .
B. Overall Architecture of ATUAD
Transformer is a popular deep learning model that has been
widely used in natural language processing and sequence modeling tasks due to the superior capability of multihead attention
mechanism in long-distance dependencies capturing. Fig. 2
shows the architecture of the neural network used in our model.
For simplicity, we use E, D1 , D2 , and W to symbolize the
Encoder, Decoder1, Decoder2, and Wt , separately. The model’s
specifics are implemented below.
ATUAD design: The classical transformer-based encoder–
decoder model is designed to excel at reconstructing normal
data while failing to do so for anomalous data that deviates from
the learned distribution, thus detecting anomalous data based on
the noticeable deviations. However, if the anomalous data are

2474

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 3, MARCH 2025

relatively close to normality, the transformer-based encoder–
decoder model tends to miss the anomalous data. Therefore, the
model should be able to recognize whether the input data does
not contain anomalies before conducting a good reconstruction.
Given that GAN models perform well in the characterization
tasks of determining whether the input data is abnormal, we
introduce a GAN-like style adversarial training method in the
transformer-based encoder–decoder model to detect anomalies.
As portrayed in Fig. 2, we concatenate position encoding with
a training window to obtain the input I for the transformer encoder, which projects I into an attention matrix Z. Next, the two
transformer decoders reconstruct the input using the attention
matrix separately. The specific operations of the transformer
encoder are as follows:
I = W ⊕ PE

(1)

I1 = LayerNorm(I + MultiHeadAtt(I, I, I))

(2)

Z = LayerNorm(I1 + Feedforword(I1 ))

(3)

where P E, ⊕, and + denote position encoding, concatenation
operation, and matrix addition, separately. MultiHeadAtt() denotes the multihead self-attention mechanism, Feedforword()
represents the fully connected feedforward network, and
LayerNorm() denotes the residual connection and layer normalization operations. The transformer encoder generates attention
weights by processing all dimensions of the time window in
parallel to capture the temporal trends in the input sequence,
which significantly improves the model’s training time. The
attention matrix output from the encoder is used as the key
and value of the encoder–decoder attention layer in transformer
decoders, thus assisting the decoders to focus on the sequence’s
appropriate position. The specific operations of the transformer
decoders are as follows:
I2 = Mask(MultiHeadAtt(I, I, I))

(4)

I3 = LayerNorm(I2 + I)

(5)

I4 = LayerNorm(I3 + EncDecAtt(I3 , Z, Z))

(6)

Qi = Sigmoid(Feedforword(I4 )).

(7)

For time-series data, the decoder’s output at timestamp t should
depend only on the outputs before t, but not on the data at future
timestamps. Therefore, the multihead attention mechanism in
the decoders uses a sequence mask to hide the data at subsequent
positions. Sigmoid function is used to normalize the reconstructions to match the preprocessed input window. Eventually,
the ATUAD model generates two reconstruction windows Qi
(i ∈ {1, 2}) using the input window W .
C. Two-Phase Adversarial Training
The model’s training consists of two phases: the reconstruction training and the adversarial training. First, the two
transformer blocks are trained to learn to reconstruct the normal data as much as possible. Second, the two transformer
blocks are trained in an adversarial way. Specifically, Transformer1 (Encoder+Decoder1) refeeds the reconstruction Q1
from phase 1 into the model, attempting to deceive Transformer2

(Encoder+Decoder2), while Transformer2 learns to distinguish
whether the data is from the input window W or Transformer1’s
reconstruction.
Phase 1—Reconstruction training: The intent of phase 1 is
to generate an approximate reconstruction of the input window
by training two transformer blocks. The reconstruction error of
each block is defined as the L2 norm of input window W and
reconstruction Qi
L1 = W − Q1 2

(8)

L2 = W − Q2 2 .

(9)

Phase 2—Adversarial training: In the second phase, the transformer encoder recompresses the reconstruction generated by
Transformer1, and then the recompressed result will be decoded
again by Decoder2. In this phase, the objective of Transformer1
is to fool Transformer2 by minimizing the deviation between
the input window W and the reconstruction Q3 . The objective
of Transformer2 is to distinguish W from Q1 by maximizing
the difference between W and Q3 . It is worth noting that
Transformer2 of our model does not strictly play the role of
the discriminator of GAN. The output of Transformer2 in Phase
2 is not a scalar but a reconstruction of the result generated from
Transformer1 in Phase 1. The training goals of the model in
phase 2 are as follows:
L1 = + W − Q3 2

(10)

L2 = − W − Q3 2 .

(11)

Two phases training: The objective function of each transformer
block contains two components, the reconstruction loss and the
adversarial loss. Transformer1 minimizes the reconstruction error between the input window W and the reconstruction Q1 and
minimizes the adversarial error between W and Q3 . Similar to
Transformer1, Transformer2 minimizes the reconstruction error
between the input window W and the reconstruction Q2 , while
maximizing the adversarial error between W and Q3 . Unlike
GANs training the discriminator while fixing the generator, we
use an evolutionary scheme for each transformer block that
combines the reconstruction loss and the adversarial loss to train
two blocks simultaneously


1
1
(12)
L1 = W − Q1 2 + 1 −
W − Q3 2
n
n


1
1
(13)
L2 = W − Q2 2 − 1 −
W − Q3 2
n
n
where n denotes the training epoch. Algorithm 1 summarizes the
complete training process of the ATUAD model. The proportion
of reconstruction loss and adversarial loss in the objective function varies with the training epoch. Initially, the weight of the
reconstruction loss is high, which ensures stable training when
the outputs of the decoders are poor reconstructions of the input
windows. With poor reconstructions, the model training of the
second phase would be unreliable. To this end, the weight of
the adversarial loss is low in the inception to avoid destabilizing model training. As the reconstructions approach the input
windows, the adversarial loss weight increases gradually. The

YU et al.: ADVERSARIAL TRANSFORMER-BASED ANOMALY DETECTION FOR MULTIVARIATE TIME SERIES

Algorithm 1: Training Algorithm of ATUAD.
Input: Training epochs N ; Sequence of training
windows Wtrain = {W1 , . . ., WT }
Output: The trained model ATUAD
E, D1 , D2 ← Initialize weights
n←1
do
for t = 1 to T do
Zt ← E(Wt ); Q1 ← D1 (Zt )
Q2 ← D2 (Zt ); Q3 ← D2 (E(Q1 ))
L1 ← n1 Wt − Q1 2 + (1 − n1 )Wt − Q3 2
L2 ← n1 Wt − Q2 2 − (1 − n1 )Wt − Q3 2
E, D1 , D2 ← Update weights using L1 , L2
end for
n←n+1
while n < N

Algorithm 2: Peaks-Over-Threshold (POT).
procedure POT(X1 , . . ., Xn ; q)
θ ← SetInitialThreshold(X1 , . . ., Xn )
Yθ ← {Xi − θ|Xi > θ} // Yθ is a set of peaks
γ̂, σ̂ ← Grimshaw(Yθ )
zq ← CalcThreshold(q, γ̂, σ̂, n, Nθ , θ)
return zq , θ
end procedure

adversarial training of the transformer-based encoder–decoder
architecture enables ATUAD to learn how to magnify the reconstruction error of input windows with anomalies and tend
to achieve stability compared to GAN architectures, helping to
reduce the risks of overfitting and nonconvergence.
D. POT-Based Dynamic Threshold Mechanism
Extreme value theory (EVT) is a statistical theory whose
objective is to discover the laws of extreme events (e.g., the
law of daily temperature maxima) [21]. Such laws of extreme
events are also called Extreme Value Distributions. For most
distributions, the probability decreases as the event approaches
an extreme value, i.e., P (X > x) → 0 as x increases. The function F (x) = P (X > x) designates the “tail” of the probability
distribution of X. It is possible to evaluate the probability of a
potential extreme event by fitting the extreme value distribution
to the tail of the input distribution. In particular, given a probability q, we can calculate a threshold zq such that P (X > zq ) < q.
One way to fit the tail of the distribution is the peak-overthreshold (POT) approach, also called the second theorem in
EVT [21]. The basic idea of POT is to fit the tail of the probability
distribution using the generalized Pareto distribution (GPD), as
shown in the following:

F θ (x) = P (X − θ > x|X > θ) ∼

1+

γx
σ(θ)

− γ1

.

2475

(14)

Equation (14) shows that the excess over an initial threshold θ,
written as X − θ, satisfies the GPD with a shape parameter γ
and a scale parameter σ. After obtaining estimates γ̂ and σ̂ by
maximum likelihood estimate and Grimshaw method [22], the
threshold zq can be calculated through the following equation:
 

−γ̂
qn
σ̂
zq ≃ θ +
−1
(15)
γ̂
Nθ
where the risk value q is the given probability. n denotes the
number of observations X1 , . . ., Xn . Nθ is the number of peaks

Algorithm 3: POT-Based Dynamic Threshold Mechanism.
procedure PDT(X1 , . . ., Xn , Xn+1 , . . ., Xm ; q)
Yθ ← ∅; TH ← ∅
zq , θ ← P OT (X1 , . . ., Xn ; q)
u←n
for n < i ≤ m do
if Xi > θ then
Y i ← Xi − θ
Add Yi in Yθ
Nθ ← Nθ + 1
u←u+1
γ̂, σ̂ ← Grimshaw(Yθ )
zq ← CalcThreshold(q, γ̂, σ̂, u, Nθ , θ)
else
u←u+1
end if
Add zq in TH
end for
T h ← CalcAverage(TH)
return T h
end procedure

Xi − θ, where Xi > θ. Algorithm 2 summarizes the POT approach to determine the threshold zq .
SPOT [21] is a streaming anomaly detection method that
applies the POT model and dynamic thresholds to detect anomalies in streaming data (Xi )i>0 . The threshold updates of SPOT
only deal with the peak cases without considering the anomaly
cases. The small peak set will make the model more variable
(high variance). Inspired by the dynamic updating of thresholds
in SPOT, we develop a PDT, which omits the anomaly detection process in SPOT and brings the anomaly cases into the
scope of threshold updates to obtain a precise threshold that
could effectively distinguish the actual anomalies from benign
samples. Initially, we conduct the POT approach on the first n
observations to reach initial thresholds zq and θ. Then, we update
zq based on the magnitude between the next observed values and
θ. If a value exceeds θ, we will include the corresponding peak
in the peak set and update zq . Finally, we add all the thresholds
zq to the threshold set and treat the mean as the global threshold.
Algorithm 3 describes the PDT mechanism.
E. Anomaly Inference
Anomaly detection: The preprocessed test data are fed into
the trained ATUAD model for anomaly detection. The anomaly

2476

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 3, MARCH 2025

detection process also executes two phases and finally obtains
a pair of outputs (Q̂1 , Q̂3 ). As a new testing window (say Ŵt )
arrives, the model calculates its anomaly score as follows:
ŝt =

1
1
Ŵt − Q̂1 2 + Ŵt − Q̂3 2
2
2

(16)

where ŝt ∈ RL×k contains the anomaly score of each dimension
at each timestamp in the test window. We use the proposed
PDT mechanism to learn the global threshold Th of the anomaly
scores
Th = PDT(s1 , . . ., sT , ŝ1 , . . ., ŝT̂ ; q)

(17)

where {s1 , . . ., sT } is the set of anomaly scores of the training
windows, which is used in the POT step in Algorithm 3 to obtain
the initial threshold zq . ŝ1 , . . ., ŝT̂ is the set of anomaly scores of
the testing windows, which is used to obtain the global threshold
T h in Algorithm 3. Since the POT algorithm requires the first
input to be a univariate sequence, we transform st (t = 1, . . ., T )
or ŝt (t = 1, . . ., T̂ ) into a scalar representing the mean of the
anomaly scores of the tth time window. If the score of the test
window Ŵt is higher than the global threshold, the window will
be declared as anomalous, i.e., yt = 1.
Anomaly diagnosis: To pinpoint the specific sensors leading
to anomalies, we calculate the residual matrix of the abnormal
testing window and its reconstruction window
ΔŴ = Ŵt − Q̂3 .

(18)

For each dimension ΔŴ i = {ΔŴ1i , . . ., ΔŴLi } (ΔŴ i ∈
RL , i = 1, . . ., k) in the residual matrix, the local threshold is
calculated by using the POT algorithm
thi = POT(ΔŴ i , q).

Algorithm 4: Detection Algorithm of ATUAD.
Input: The trained model; risk value q; Sequence of
training windows Wtrain = {W1 , . . ., WT }; Sequence
of testing windows Ŵtest = {Ŵ1 , . . ., ŴT̂ }
Output: Labels y = {y1 , . . ., yT̂ }
for t = 1 to T do
Q1 ← D1 (E(Wt )); Q3 ← D2 (E(Q1 ))
st ← 21 Wt − Q1 2 + 21 Wt − Q3 2
end for
for t = 1 to T̂ do
Q̂1 ← D1 (E(Ŵt )); Q̂3 ← D2 (E(Q̂1 ))
ŝt ← 21 Ŵt − Q̂1 2 + 21 Ŵt − Q̂3 2
end for
T h ← P DT (s1 , . . ., sT , ŝ1 , . . ., ŝT̂ ; q)
for t = 1 to T̂ do
if ŝt > T h then
yt ← 1; ΔŴ ← Ŵt − Q̂3 
for i = 1 to k do
thi ← P OT (ΔŴ i , q)
if ΔŴli > thi then
sensor i is abnormal at time l
end for
else
yt ← 0
end for
return y = {y1 , . . ., yT̂ }
TABLE I
DATASET INFORMATION

(19)

It indicates that the sensor i has caused abnormal data at timestamp l if there is a difference ΔŴli in ΔŴ i higher than the
local threshold thi . A longer sequence of consecutive scores in
ΔŴ i higher than the local threshold indicates a longer anomaly
duration and a higher anomaly severity level. Algorithm 4
summarizes the anomaly detection and diagnosis process of the
ATUAD model.
IV. EXPERIMENTS
A. Experimental Setup
Datasets: The datasets adopted in the experiment include
MIT-BIH Supraventricular Arrhythmia Dataset (MBA) [24],
Soil Moisture Active Passive Dataset (SMAP) [25], Secure Water Treatment Dataset (SWaT) [27], Water Distribution Dataset
(WADI) [28], Mars Science Laboratory Dataset (MSL) [26],
and Server Machine Dataset (SMD) [16], which are commonly
used in multivariate anomaly detection. I summarizes the characteristics of each dataset. We abandon Yahoo and Numenta
datasets due to the flaws, such as mislabeled ground truth and
run-to-failure bias reported in [23].
Training setting: We train all models employing PyTorch1.8.0 on a Ubuntu 18.04 system with configuration RTX 4090
GPU. Our model has one transformer encoder layer and two
transformer decoder layers. For time series reconstructing, we

set the window size to ten frames with a batch size of 128. The
number of heads in multihead attention is consistent with the
dimensionality of the dataset. We utilize the dropout strategy
to prevent overfitting with a dropout rate of 0.1. In addition, we
train the models using the AdamW optimizer with a corresponding learning rate for each dataset. Compared with Adam, the
weight decay of AdamW achieves decoupling and better results.
Table II shows the hyperparameters used in our ATUAD model.
Table III gives the hyperparameters of baselines used in our
experiment.
B. Performance Analysis
Anomaly detection results comparing with baselines: To
demonstrate the anomaly detection performance, we compared our model with six state-of-the-art methods, namely,
MSCRED [15], OmniAnomaly [16], DAGMM [18], MADGAN [17], USAD [11], and TranAD [14]. Table IV shows the
results of all models on six datasets. From Table IV, we can
conclude that, except for the SWaT dataset, our ATUAD achieves

YU et al.: ADVERSARIAL TRANSFORMER-BASED ANOMALY DETECTION FOR MULTIVARIATE TIME SERIES

TABLE II
HYPERPARAMETERS OF OUR MODEL

Fig. 3.

Average performance of all models.

better F1 scores than other methods across all datasets. USAD
realizes the best F1 score on the SWaT dataset, and the F1 score
of our model is close to that of USAD. Furthermore, the performance of our ATUAD is improved on most datasets, especially
on the WADI dataset, with an improvement of approximately
9% and 10% in P and F 1 compared to the optimal baseline,
respectively. Fig. 3 portrays the average performance of all
models on six datasets. As shown in Fig. 3, the average precision
(P ∗ ) and the average F1 score (F 1∗ ) of our ATUAD exceed
those of other models. Specifically, our ATUAD achieves an
improvement of up to 2.47% in P ∗ and 2.19% in F 1∗ compared
to the optimal baseline, but the average recall (R∗ ) is 1.23%
lower than that of DAGMM.
DAGMM [18] reaches high performance on short datasets like
MBA and SMAP. However, DAGMM performs poorly on large
sequence datasets, such as WADI, since it ignores the inherent
temporal dependence in multivariate time series. The temporal
dependence is paramount for the time-series data since the
observations are dependent. Therefore, the temporal information
in historical data is essential for reconstructing or predicting the
time series. In our ATUAD, the multivariate time-series data are
transformed into a sequence of windows to hold the temporal
information. Furthermore, ATUAD uses transformer blocks as
the feature extractor to model the serial data. Consequently, ATUAD performs well on the longer sequence of high-dimensional
datasets.

2477

MSCRED [15] and OmniAnomaly [16] take as input the
observation sequences and consider LSTM or GRU recurrent
neural networks to capture the temporal information in the
sequential observations, achieving high F1 scores on MBA and
MSL. However, such methods identify anomalies merely by
reconstructing, thus failing to detect slight outliers closer to normal data in datasets like SMD. Our ATUAD utilizes adversarial
training to boost the deviation and has a high detection sensitivity
for anomalous data with mild anomalies.
MAD-GAN [17] adopts adversarial training to reconstruct the
original time series, so it performs better than MSCRED on the
SMD dataset with mild anomalies. Nevertheless, MAD-GAN
also uses RNNs as the basic framework, which restricts the
modeling capability over the long-term sequence. Our ATUAD
applies the powerful multihead attention mechanism to learn
the sequence features in a parallel fashion, achieving swift calculation efficiency and the capability of capturing long-distance
context information.
USAD [11] uses an autoencoder framework with an adversarial style to achieve 94.95% and 94.47% F1 scores on SMD and
MBA, respectively, but performs mediocrely on other datasets,
especially on the high-dimensional and unbalanced datasets,
such as WADI. This is because USAD simply uses linear
transformations to encode and decode the data, which speeds
up the training but neglects the temporal correlation within the
multivariate time-series data.
TranAD [14] extracts multimodal features leveraging focus score-based self-conditioning and gains stability using
adversarial training. It outperforms other models on SWaT and
SMD. However, the F1 score of TranAD on the WADI dataset
is 49.51%, which is lower than the F1 score of 59.16% achieved
by our ATUAD. This improvement can be attributed to the
input window and adversarial training. The input windows fed
into ATUAD contain richer temporal information than that of
TranAD, facilitating the learning of time series features. Specifically, ATUAD takes as input the data of a complete batch of time
windows to its decoders for aiding temporal attention, while just
one local contextual window is fed into the TranAD’s Window
Encoder. In addition, ATUAD conducts adversarial training
using the reconstruction of the input directly instead of a sparse
focus score matrix used in TranAD. Therefore, our ATUAD
has an advantage in obtaining the temporal trend of long-term
sequences and achieves better results even on high-dimensional
and unbalanced datasets.
Root cause identification results: To further analyze the effectiveness of ATUAD, Fig. 4 presents a case study of anomaly
diagnosis in the SMD dataset. In Fig. 4(a), the red dashed
line represents the global threshold, and the areas highlighted
by blue rectangles portray the anomalous fragments in SMD.
ATUAD declares the sequences with anomaly scores exceeding
the threshold as abnormal sequences. As depicted in Fig. 4(a),
multitudinous abnormal sequences in the SMD testing dataset
have scores higher than the threshold, which indicates that
ATUAD can pinpoint the actual positives with false positives
that are not excessive.
The purple matrix in Fig. 4(b) represents the residual matrix
between the input sequence and the reconstructed sequence.

2478

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 3, MARCH 2025

TABLE III
HYPERPARAMETERS OF BASELINES

TABLE IV
PERFORMANCE COMPARISON OF ALL MODELS

The red rectangle represents the abnormal events detected by
the model. Anomalous events refer to which indicators or
dimensions of the detected entity are abnormal in which period.
The longer red rectangle represents the longer duration of the
abnormality of this indicator, which means higher severity level
of the anomaly. In Fig. 4(b), the indicator d1 in the first residual
matrix is abnormal at more than 30 consecutive timestamps.
It is more likely to occur as a seriously anomalous event. The
operator can quickly troubleshoot and fix the root cause of the
abnormality based on this information.
In the first anomaly area of the SMD testing dataset, the true
anomaly root causes include seven dimensions of 1, 9, 10, and
12–15, while the anomaly root causes detected by ATUAD are
d1, d9, d10, d12–d15, and d23 dimensions. In the last anomaly
region, the actual anomaly root causes contain four dimensions
of 9, 13, 14, and 15, while the anomaly root causes detected by
ATUAD are d9, d11, d12, d13, d14, d15, and d23 dimensions.
This case indicates that ATUAD can pinpoint 57.10%–87.50%
of root causes for anomalies.
C. Ablation Studies

Fig. 4. Case study of anomaly diagnosis. (a) Anomaly score. (b) Abnormal windows.

Anomaly detection results comparing with model variants:
To investigate the influence of each component on ATUAD,
we examine three variants of ATUAD. First, we study ATUAD without adversarial loss. We remove the adversarial
training and only consider the reconstruction loss of phase
1, i.e., L1 = W − Q1 2 + W − Q2 2 . Second, to verify the

YU et al.: ADVERSARIAL TRANSFORMER-BASED ANOMALY DETECTION FOR MULTIVARIATE TIME SERIES

Fig. 5.

2479

Performance comparison between ATUAD and variant models. (a) F1-score. (b) AUC score.

TABLE V
COMPARISON OF TRAINING TIME ON ALL DATASETS AND PARAMETER SIZE ON WADI

effectiveness of the POT-based dynamic threshold mechanism, we replace it with the best-F-score threshold selection
method [29]. Finally, we substitute the transformer networks
with feedforward networks for reconstruction to demonstrate
the necessity of a transformer-based structure for modeling
sequences. Fig. 5 draws the comparison results of ATUAD and
its variants in F1 score and AUC. From Fig. 5, we can report the
following conclusions.
ATUAD_Adversarial: After removing the adversarial training, the variant’s performance has declined on most datasets,
especially the WADI dataset, whose F1 score and AUC have decreased by 26% and 12%, respectively. However, censoring the
adversarial training generally has less impact on the performance
of the other datasets, and even the SMD dataset exhibits a slight
improvement in the F1 score and the AUC. These results reflect
that the adversarial training is more suitable for datasets with a
large percentage of mild anomalies (e.g., the WADI dataset) by
amplifying errors to recognize them.
ATUAD_POT: Replacing the POT-based dynamic threshold
mechanism with the best-F-score method resulted in a decrease
in the F1 score and AUC for most datasets, which suggests that
the anomaly detection model with POT can avoid more underreporting and false alarms on the time-series datasets. The tiniest
change is in the WADI dataset, where the F1 score decreased
from 59.16% to 20.27%, while the AUC increased slightly. The
most significant impact was observed on the SMAP and MSL
datasets, with a decrease of approximately 71% and 44% in
the F1 score and AUC, respectively. Therefore, the POT-based
dynamic threshold mechanism positively influences the model’s
performance.
ATUAD_Transformer: Substituting the transformer structure
with a feedforward network, the variant model has an average
decrease of about 10% in the F1-score and 4% in the AUC on

all datasets. The decrease is more pronounced on the MSAP
and MSL datasets, with a decrease of approximately 15% and
28% in the F1 score and approximately 13% and 7% in the AUC,
respectively. These changes demonstrate that the attention-based
transformer is more advantageous in identifying anomalies in
large-scale datasets.
D. Overhead Analysis
This section investigates the complexity of all models on
the given datasets. For this purpose, we measure the average
training time in seconds per epoch and model size (Params)
and record them in Table V. In general, the three models with
the shortest training time are TranAD, DAGMM, and ATUAD,
followed by USAD, while the remaining models have longer
training time, especially MSCRED. Next, we gradually analyze
the reasons for this situation to clarify the effectiveness of our
ATUAD. The training times of MSCRED, OmniAnomaly, and
MAD-GAN are longer than those of TranAD and ATUAD
since the formers use recurrent neural networks for sequential
processing while the later apply parallel computing. DAGMM
and USAD consist of fully connected neural networks whose
training times are generally shorter than those of MSCRED,
OmniAnomaly, and MAD-GAN while still higher than TranAD
and ATUAD over the most datasets. This fully demonstrates the
advantage of using transformer blocks with position encoding
for sequence modeling. ATUAD obtains a lower training time
while keeping a slightly higher parameter size than MSCRED,
OmniAnomaly, MAD-GAN, and USAD. This illustrates that
our ATUAD can effectively accomplish the model training with
less calculation. Furthermore, ATUAD achieves a significantly
lower parameter size while holding a slightly higher training
time than TranAD, which can be explained by the input size

2480

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 21, NO. 3, MARCH 2025

of the whole model and its component. On the one hand, the
input size of the model affects the parameter size. Specifically,
in one iteration, TranAD takes as input a complete batch of time
window sequences and a local contextual window, whereas our
ATUAD only handles the complete batch of window sequences.
As a result, our ATUAD has much fewer parameters (1.35 MB)
than TransAD (5.16 MB). On the other hand, the input size of
the model’s component affects the training time. Concretely, our
ATUAD pushes the complete window sequences as the input
to its Decoder1 and Decoder2 for aiding temporal attention,
while just one local contextual window is fed into TranAD’s
Window Encoder. The outcome is that our ATUAD consumes
more training time while capturing more temporal information.
Consequently, the training efficiency and storage overhead of our
ATUAD is competitive and acceptable compared to the related
baselines.
V. CONCLUSION
Confront the multivariate time series with complex spatiotemporal correlations and the demand for swift anomaly detection
in modern applications, we construct ATUAD, an unsupervised
anomaly detection model based on adversarially trained transformers. ATUAD uses a transformer-based encoder–decoder
framework to reconstruct data in parallel and applies adversarial
training to amplify the deviation of mild anomalies. Besides,
a POT-based dynamic threshold mechanism is utilized in ATUAD to determine a threshold for identifying anomalies. Extensive experiments on six public datasets demonstrated that ATUAD outperforms most state-of-the-art baselines on evaluation
metrics. Despite ATUAD achieving competitive performance in
anomaly detection and training efficiency, centralized anomaly
detection on time-series data in a cloud server may lead to
privacy breaches, limiting the model’s applicability in scenarios
with high privacy protection requirements. Consequently, our
future work will focus on introducing personalized federated
learning and cryptography into our model to make it suitable for
handling sensitive heterogeneous data.
REFERENCES
[1] X. Zhou, Y. Hu, W. Liang, J. Ma, and Q. Jin, “Variational LSTM enhanced
anomaly detection for industrial Big Data,” IEEE Trans. Ind. Informat.,
vol. 17, no. 5, pp. 3469–3477, May 2021.
[2] Z. Jingyu, Z. Siqi, T. Wang, H. C. Chao, and J. Wang, “Blockchain-based
systems and applications: A survey,” J. Internet Technol., vol. 21, no. 1,
pp. 1–14, 2020.
[3] A. A. Cook, G. Misirli, and Z. Fan, “Anomaly detection for IoT time-series
data: A survey,” IEEE Internet Things J., vol. 7, no. 7, pp. 6481–6494,
Jul. 2020.
[4] C. Yin, S. Zhang, J. Wang, and N. N. Xiong, “Anomaly detection based
on convolutional recurrent autoencoder for IoT time series,” IEEE Trans.
Syst., Man, Cybern. Syst., vol. 52, no. 1, pp. 112–122, Jan. 2022.
[5] C. Chen, K. Li, S. G. Teo, X. Zou, K.-C. Li, and Z. Zeng, “Citywide traffic
flow prediction based on multiple gated spatio-temporal convolutional
neural networks,” ACM Trans. Knowl. Discov. From Data, vol. 14, no. 4,
pp. 1–23, 2020.
[6] D. Cao, Z. Chen, and L. Gao, “An improved object detection algorithm
based on multi-scaled and deformable convolutional neural networks,”
Hum.-Centric Comput. Inf. Sci., vol. 10, no. 4, 2020, Art. no. 10.
[7] A. Graves, A. R. Mohamed, and G. E. Hinton, “Speech recognition with
deep recurrent neural networks,” in Proc. 2013 IEEE Int. Conf. Acoust.
Speech Signal Process., 2013, pp. 6645–6649.

[8] A. Geiger, D. Liu, S. Alnegheimish, A. Cuesta-Infante, and K. Veeramachaneni, “TADGaN: Time series anomaly detection using generative
adversarial networks,” in Proc. 2020 IEEE Int. Conf. Big Data, 2020,
pp. 33–43.
[9] L. Zhao, Y. Zhang, and Y. Cui, “A multi-scale U-shaped attention networkbased GaN method for single image dehazing,” Hum.-Centric Comput. Inf.
Sci., vol. 11, no. 38, 2021, pp. 562–578.
[10] Z. Chen, D. Chen, Z. Yuan, X. Cheng, and X. Zhang, “Learning graph
structures with transformer for multivariate time-series anomaly detection
in IoT,” IEEE Internet Things J., vol. 9, no. 12, pp. 9179–9189, Jun. 2022.
[11] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,” in
Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 3395–3404.
[12] H. Zhou et al., “Informer: Beyond efficient transformer for long sequence
time-series forecasting,” in Proc. Nat. Conf. Artif. Intell., 2021, vol. 35,
pp. 11106–11115.
[13] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural Inf.
Process. Syst. 30, 2017, vol. 30, pp. 5998–6008.
[14] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” Very
Large Data Bases, vol. 15, pp. 1201–1214, 2022.
[15] C. Zhang et al., “A deep neural network for unsupervised anomaly detection and diagnosis in multivariate time series data,” in Proc. AAAI Conf.
Artif. Intell., 2019, vol. 33, no. 1, pp. 1409–1416.
[16] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 2828–2837.
[17] D. Li, D. Chen, L. Shi, B. Jin, J. Goh, and S.-K. Ng, “Mad-GaN: Multivariate anomaly detection for time series data with generative adversarial
networks,” in Proc. Int. Conf. Artif. Neural Netw., 2019, vol. 11730,
pp. 703–716.
[18] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. 6th Int. Conf. Learn. Representations,
Vancouver, BC, Canada, 2018.
[19] L. Xu et al., “TGAN-AD: Transformer-based GaN for anomaly detection
of time series data,” Appl. Sci., vol. 12, no. 16, pp. 8085–8102, 2022.
[20] Y. Li, X.-J. Peng, J. Zhang, Z. Li, and M. Wen, “DCT-GaN: Dilated
convolutional transformer-based GaN for time series anomaly detection,”
IEEE Trans. Knowl. Data Eng., vol. 35, no. 4, pp. 3632–3644, Apr. 2023.
[21] A. Siffer, P.-A. Fouque, A. Termier, and C. Largouët, “Anomaly detection
in streams with extreme value theory,” in Proc. 23rd ACM Knowl. Discov.
Data Mining, 2017, pp. 1067–1075.
[22] S. D. Grimshaw, “Computing maximum likelihood estimates for the generalized Pareto distribution,” Technometrics, vol. 35, no. 2, pp. 185–191,
1993.
[23] R. Wu and E. J. Keogh, “Current time series anomaly detection benchmarks
are flawed and are creating the illusion of progress,” IEEE Trans. Knowl.
Data Eng., vol. 35, no. 3, pp. 2421–2429, Mar. 2023.
[24] G. B. Moody and R. G. Mark, “The impact of the MIT-BIH arrhythmia database,” IEEE Eng. Med. Biol. Mag., vol. 20, no. 3, pp. 45–50,
May/Jun. 2001.
[25] P. E. O’neill, D. Entekhabi, E. G. Njoku, and K. H. Kellogg, “The NASA
Soil Moisture Active Passive (SMAP) mission: Overview,” in Proc. 2010
IEEE Int. Geosci. Remote Sens. Symp., 2010, pp. 3236–3239.
[26] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Söderström, “Detecting spacecraft anomalies using LSTMs and nonparametric
dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, 2018, pp. 387–395.
[27] A. P. Mathur and N. O. Tippenhauer, “SWaT: A water treatment testbed
for research and training on ICS security,” in Proc. 2016 Int. Workshop
Cyber-Phys. Syst. Smart Water Netw., 2016, pp. 31–36.
[28] C. M. Ahmed, V. R. Palleti, and A. P. Mathur, “WADI: A water distribution
testbed for research in the design of secure cyber physical systems,” in
Proc. 3rd Int. Workshop Cyber- Phys. Syst. Smart Water Netw., 2017,
pp. 25–28.
[29] A. Garg, W. Zhang, J. Samaran, R. Savitha, and C.-S. Foo, “An evaluation
of anomaly detection and diagnosis in multivariate time series,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2508–2517, Jun. 2022.
PAPER_TEXT
