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
# [158] A Lightweight Pipeline Edge Detection Model Based on Heterogeneous Knowledge Distillation
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
编号：158
题名：A Lightweight Pipeline Edge Detection Model Based on Heterogeneous Knowledge Distillation
年份：2024
DOI：10.1109/tcsii.2024.3439361
来源：IEEE Transactions on Circuits and Systems II: Express Briefs
PDF：paper/10.1109_TCSII.2024.3439361.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：无
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\158.txt
- 原始字符数：28092
- 本次发送字符数：28092
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS—II: EXPRESS BRIEFS, VOL. 71, NO. 12, DECEMBER 2024

5059

A Lightweight Pipeline Edge Detection Model
Based on Heterogeneous Knowledge Distillation
Chengyuan Zhu , Yanyun Pu , Zhuoling Lyu , Aonan Wu, Kaixiang Yang , Member, IEEE,
and Qinmin Yang , Senior Member, IEEE

Abstract—The pipeline safety warning system (PSEW) is
an important guarantee for the safe transportation of energy
pipelines. Given the constraints of deploying detection models
at resource-limited pipeline stations, there is a compelling need
to develop efficient, lightweight models suitable for edge device
applications. This brief introduces an adaptive heterogeneous
model knowledge distillation network (AHKDnet) for edge
deployment of pipeline network detection models. The global
information and long-distance dependency relationships from the
ViT-based teacher network are transferred to the CNN-based
shallow student network. We introduce the learnable modulation parameters to optimize target information enhancement,
reducing the impact of irrelevant information. By embedding
the model selection at each stage of knowledge distillation, the
performance collapse of student models caused by misleading
cross-architecture knowledge is avoided, and model convergence
is accelerated. Experiments on three actual scene datasets of
pipeline networks show that AHKDnet outperforms the stateof-the-art KD methods and has strong generalization ability.
Notably, AHKDnet enhances the recognition performance of
shallow student networks by an average of 10%, highlighting its
efficacy and potential for practical applications. Our method can
provide a new reference for edge deployment of PSEW.
Index Terms—Pipeline network safety, knowledge distillation,
heterogeneous model, lightweight, distributed optical fiber.

I. I NTRODUCTION

P

IPELINE transportation is one of the essential modes
of energy transportation, especially for oil and gas

Manuscript received 8 April 2024; revised 21 June 2024; accepted
2 August 2024. Date of publication 6 August 2024; date of current version
26 November 2024. This work was supported in part by the National
Natural Science Foundation of China under Grant U21A20478 and Grant
62106224; in part by the Zhejiang Provincial Nature Science Foundation of
China under Grant LZ21F030004; and in part by the Guangzhou Science
and Technology Plan Project under Grant 2024A04J3749. This brief was
recommended by Associate Editor J. Chen. (Corresponding authors: Kaixiang
Yang; Qinmin Yang.)
Chengyuan Zhu and Qinmin Yang are with the College of Control
Science and Engineering, Zhejiang University, Hangzhou 310007,
Zhejiang, China, and also with the Huzhou Institute, Zhejiang University,
Huzhou 313000, Zhejiang, China (e-mail: zhuchengyuan517@zju.edu.cn;
qmyang@zju.edu.cn).
Yanyun Pu is with the College of Control Science and Engineering,
Zhejiang University, Hangzhou 310007, Zhejiang, China (e-mail: yanyun23@
zju.edu.cn).
Zhuoling Lyu and Aonan Wu are with the College of Engineers, Zhejiang
University, Hangzhou 310007, Zhejiang, China (e-mail: zhuolinglyu@
zju.edu.cn; 22360173@zju.edu.cn).
Kaixiang Yang is with the College of Computer Science and Engineering,
South China University of Technology, Guangzhou 510006, Guangdong,
China (e-mail: yangkx@scut.edu.cn).
Color versions of one or more figures in this article are available at
https://doi.org/10.1109/TCSII.2024.3439361.
Digital Object Identifier 10.1109/TCSII.2024.3439361

resources [1]. Due to the long distance of pipeline transportation, various disruptive events (such as mechanical excavation,
construction, human activities, etc.) may occur in an open
environment, posing a threat to the safety of pipelines. In
2022, the Nord Stream natural gas pipeline suffered external
damage and leakage, resulting in multiple explosions. The oil
pipeline in Kansas, USA, leaked over 14000 barrels of crude
oil, causing significant economic losses and environmental
pollution. Thus, it is beneficial to conduct intrusion detection
around pipelines to promptly recognize such hazardous events
and implement corresponding measures. In recent years, the
pipeline safety early warning (PSEW) system based on distributed optical fiber sensing (DOFS) technology has become
an important technology for preventing pipeline damage and
ensuring energy transportation [2]. It employs communication
optical cables along the pipeline as a sensor array, recognizing signal types through signal processing and Artificial
Intelligence (AI) algorithms. Subsequently, early warning and
verification of hazardous events are conducted. DOFS has
extensive application prospects in energy, industry and other
fields due to its continuous monitoring, high resolution, and
low cost.
The key to the PSEW system is the fast and accurate
intrusion detection algorithm. Therefore, effective and reliable feature extraction and recognition network for damage
events comes to play and has received notable attention [3].
In previous studies [4], [5], threshold-based and statistical
machine learning methods were used for signal processing
and intrusion event recognition in the single environment.
At present, deep learning methods have become the mainstream method of recognition algorithms to address the impact
of more complex environments and background noise in
the field of DOFS [6], [7]. Yang et al. proposed a realtime action recognition method for long-distance PSEW
systems [1]. The system can quickly identify and locate
third-party damage events by calculating two complementary
features and constructing a novel action recognition deep
learning network. Wu et al. proposed a two-level multitask learning (MTL) enhanced smart fiber-optical distributed
acoustic sensing (sDAS) system to simultaneously realize
ground event recognition and localization [8]. These studies
fully confirm that the combination of new intelligent sensors
and AI effectively improves the intelligence and safe operation
of pipelines [9], [10].
However, there are still some challenges in the actual
deployment of pipeline networks. It is usually necessary to
deploy multiple devices in stations or valve chambers along the

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1549-7747 
See https://www.ieee.org/publications/rights/index.html for more information.

5060

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS—II: EXPRESS BRIEFS, VOL. 71, NO. 12, DECEMBER 2024

pipeline to achieve comprehensive coverage of monitoring due
to the long transportation distance of pipelines. Stations often
have limited computing power and storage resources, which
affect the size and processing speed of deep learning models.
Currently, many studies [11], [12] aim to test deep models
on a single device without considering the global deployment
of pipeline networks. Our previous research [13], [14] also
found that the performance of using vision transformer (ViT)
structural models for classification after image encoding of
time series signals is better than that of CNN-based structural
models, which can improve the recognition performance of
PSEW systems. Nevertheless, models based on ViT structure require larger data and more parameters, while CNN
structure models have relatively lower computational complexity. Consequently, it is necessary to compress model to
balance the performance and time cost in pipeline network
applications.
To achieve the goal of deploying efficient lightweight
models at the edge, we propose an adaptive heterogeneous
model knowledge distillation network architecture, AHKDnet
that simultaneously uses a responses-based and features-based
distillation method for model learning in logits space. To
combine the advantages of ViT structure and CNN structure,
the ViT-based model is regarded as the teacher network,
while the CNN-based model serves as the student network,
enabling the student model to learn the global information
and long-distance dependency relationships extracted by the
teacher model. This also makes the CNN model strengthen the
learning of position information, compensating for the spatial
information loss during convolution and pooling processes.
Therefore, it is necessary to project the features extracted
from heterogeneous models into a unified spatial alignment
for knowledge distillation (KD). Moreover, we add learnable
modulation parameter and model selection at each stage of KD
to ensure the effectiveness of knowledge transfer. Enhancing
target information can help improve the learning effectiveness
of student models on teacher models, and alleviate the impact
of target class soft labels when teacher models provide under
prediction. Model selection can accelerate the convergence
speed of student models by judging the using/not using KD.
Our major contributions are summarized as follows:
1) We propose an adaptive heterogeneous knowledge distillation network (AHKDnet) for limited edge deployment
of pipeline intrusion detection models. Compared with
the deep learning framework without KD, it can not only
improve the recognition accuracy of student model, but
also reduce the actual deployment requirements.
2) Considering the differences of target class distribution in
heterogeneous models, we have improved the modulation
parameters that can learn to optimize target information
enhancement in the loss function, further reducing the
impact of irrelevant information in logits space.
3) We introduce the mechanism of model selection based
on threshold in the feature distillation of intermediate
layers. It can limit the performance collapse caused
by misleading cross-architecture knowledge, thus optimizing the effectiveness of KD in each stage of the
model.

Fig. 1. (a) The diagram of PSEW deployed in the pipeline network, (b) The
deployment strategy of edge detection models in pipeline networks.

Fig. 2.

The structure diagram of DAS system.

The remainder of this brief is as follows. Section II
introduces the structure of PSEW system and its application
in smart pipeline network. Section III provides a detailed
explanation to AHKDnet. Section IV shows the experimental results to demonstrate the superior performance of the
proposed model. In Section V, this brief is summarized.
II. PSEW S YSTEM FOR S MART P IPELINE N ETWORK
PSEW system is an important component of smart pipeline
network, which can achieve intelligent perception and dynamic
monitoring of pipelines. At present, PSEW mainly consists of
distributed optical fiber acoustic sensing (DAS) system and
unmanned aerial vehicle inspection system. Among them, the
DAS system utilizes the high sensitivity of coherent Rayleigh
scattering in optical fiber, which can perceive environmental
vibration and acoustic field at long distances with high
spatiotemporal resolution. However, the monitoring range of
a single device is limited, usually within 50km.
As shown in Fig. 1 (a), multiple devices need to be installed
in the station or valve chamber of the pipeline network to
achieve continuous monitoring of the pipeline. The DAS
system is connected to the sensing fibers laid parallel to the
pipeline, continuously monitoring the external acoustic signals
of the pipeline. Fig. 1 (b) shows the deployment strategy of our
lightweight edge detection model for cloud-edge collaborative.
By training a powerful teacher network in the cloud for KD,
the performance of the student network deployed by edge
devices can be improved.
The structure of DAS system is shown in Fig. 2. The system
uses narrow linewidth laser (NLL). The beam is modulated
into narrow-band pulsed light by an acousto-optic modulator
(AOM). The pulsed light is amplified by an erbium-doped fiber
amplifier (EDFA) and filtered. The modulated pulsed light
enters the sensing fiber through the coupler and circulator.
The sensing fiber is disturbed by piezoelectric ceramics (PZT)
to generate Rayleigh backscattered light signal. The optical

ZHU et al.: LIGHTWEIGHT PIPELINE EDGE DETECTION MODEL

Fig. 3.

5061

The architecture of AHKDnet.

signal is converted by photodetector (PD) and triggered by an
arbitrary waveform generator (AWG) to collect the signal on
the data acquisition (DAQ). Finally, the signal is processed
through the warning model deployed on the upper computer.
III. M ETHODOLOGY
Knowledge distillation (KD), as a model compression
method, has broad application prospects in industry [15]. KD
optimizes the student model by minimizing the difference in
output between the teacher model and the student model, typically using soft labels as the training objective for the student
model. KD aims to extract knowledge from higher accuracy
teacher networks to improve the performance of lightweight
student networks [16]. To integrate the advantages of different
architecture models, we propose the AHKDnet method based
on the OFA-KD framework [17] to improve the performance
of heterogeneous model knowledge distillation in pipeline
network scenario. OFA-KD projects intermediate features into
an aligned latent space, causing specific architecture related
information to be discarded. It significantly improves the distillation performance between heterogeneous system structures.
Fig. 1 illustrates the framework of AHKDnet. Gramian angle
field (GAF) is applied to transform the 30s DAS raw signal
into 2D image as model input [13]. The structure of the model
consists of heterogeneous KD mechanism, the optimization
target enhancement with learnable parameters and the feature
distillation of intermediate layers with model selection.
A. Heterogeneous Knowledge Distillation Mechanism
The ViT-based models have more advantages in event
classification of complex environmental signals, while the
CNN-based models have relatively lower computational complexity. The ViT-based models can simultaneously consider
both global and local feature extraction in different layers
due to the role of self-attention mechanism. The CNN-based
models follow a feature extraction process from local to global,
making it difficult for shallow networks to retain more refined
local spatial information. Previous studies have demonstrated
the feature mismatch caused by representation differences
between heterogeneous models by calculating their centered
kernel alignment (CKA) [17]. CKA is a feature similarity

measurement allowing cross-architecture comparison achievable, as it can work with inputs having different dimensions.
To achieve heterogeneous model KD of intermediate layer
features, the intermediate layer features are transferred to an
aligned logits space and matched with the final output (logits)
of the teacher network.
DHSIC (K, L)
(1)
CKA(K, L) = √
DHSIC (K, K) DHSIC (L, L)
1
DHSIC (K, L) =
tr(KHLH)
(2)
(n − 1)2
where DHSIC denotes the Hilbert-Schmidt independence criterion. K and L represent Gram matrices of the features. H is
the centering matrix. The tr() represents the trace of a matrix.
B. Learnable Optimization Target Enhancement
Heterogeneous models have inherent differences in learning abilities and preferences due to their different inductive
biases [17]. To enhance the information of target class, we
added a learnable parameter related to the target class to
participate in learning optimization at each stage, achieving
adaptive enhancement of the target information. The difference
from fixed modulation parameters is that it updates the values
of each stage based on gradient contributions. The amount of
information affected by the teacher network varies due to the
changes in the receptive field of the CNN model at different
stages. There are differences in the optimal fixed parameters
for different teacher models, and the most suitable value for
each stage is also different. The loss function is defined as.
α γ̂



(3)
log psc − λE ptc log psc
Lossahkd = − 1 + ptc
where ptc and psc represent the prediction probability of the
predicted class for the teacher model and the student model,
respectively. ptc and psc are the probability of the target
class for the student model and the teacher model. α is
used to control the learning rate of γ̂ . γ̂ denotes learnable
modulating parameter to achieve learnable optimization of
target information enhancement. α and γ̂ adjust the differences
in learning ability and preferences of heterogeneous models
based on the probability of target class soft labels provided by
the teacher model. λ is a hyperparameter controls the trade-off
between one-hot label and soft label.

5062

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS—II: EXPRESS BRIEFS, VOL. 71, NO. 12, DECEMBER 2024

TABLE I
C OMPREHENSIVE C OMPARISON R ESULTS OF D IFFERENT M ODELS AND D ISTILLERS

C. Adaptive Model Selection With KD
We introduce a model selection mechanism to ensure the
gain effect of KD [18]. Specifically, the effect with KD on
model convergence can be determined by adding the threshold
to optimize the update speed of gradients in the model. We
train an additional local model in parallel at each stage, which
update gradients through heterogeneous model distillation
and update gradients without KD learning, respectively. By
calculating the gain of gradient descent on model convergence,
the stage model with a greater contribution is selected to
use the next round of training using the model. Thus, it
suppresses the performance collapse of student models caused
by misleading heterogeneous knowledge and improve the
convergence performance of student model.
 2
 
 j 
j
j
Gj = gkd  + 2 gi gkd
Gj ≥ ξj , the model with KD;
Gj < ξj , the model without KD.

(4)
(5)

where Gj is the performance gain by using the KD method at
j
j
stage j. gkd and gi represent gradients with and without KD
at stage j, respectively. ξj denotes the threshold of the model
contribution at stage j. If Gj ≥ ξj , the sum of the step size of
gradient has a positive contribution to the local model update.
Then, the local model for the next training round should use
KD. On the contrary, there is no need to learn through KD.
IV. E XPERIMENTS
The experimental data is collected from DOFS signals in
actual scenes of natural gas pipelines in Zhejiang Province,
including three kinds of DOFS datasets with different sizes,
types and scenes. We select three types of events on each
pipeline, including intrusion events, interference events, and
environmental noise. Each type has 1000 samples, totaling
9000 samples. The system sampling frequency is 4Hz, and
the sample signal length is 30s, with a total of 120 sampling
points. In paper [14], a more detailed introduction is provided
to the datasets. We convert the original signals into 2D images
by the image encoding method of Gramian Angular Field
(GAF), and unify the resolution of images to 224x224. It can
preserve the complete information of the signal and maintain
its dependence on time. The CNN-based models are trained
using the SGD optimizer with an initialized learning rate of
0.05, while other ViT-based models are trained using the Adam
optimizer (set β1 = 0.9, β2 = 0.99). All experiments are
trained for 100 epochs using 5-fold cross validation.

AHKDnet is compared with previous KD methods, including KD [19], RKD [20], DKD [21], DIST [22], and
OFA [17]. We employ ViT-based teacher networks, including
ViT-B [23], Swin-B [24], and PipelineADVinT [14], as well
as CNN-based shallow student networks, ResNet18 [25] and
EfficientNet-B0 [26]. Moreover, we compared the performance
improvement of student networks on two directions of heterogeneous knowledge distillation, from ViT to CNN and from
CNN to ViT. The performance improvement of the proposed
method was experimentally validated on three datasets. The
accuracy (ACC) is used as an indicator to evaluate the
performance of each model. The higher the accuracy, the
stronger the recognition performance of the model, as shown
below.
ACC =

TP + TN
TP + TN + FP + FN

(6)

where TP, FP, FN, TN represent true positives, false positive,
false negative and true negative respectively.
The comparative experimental results between the proposed
method and previous work indicate that AHKDnet has superior
performance in Table I. Overall, it can improve the accuracy
of the original student model by approximately 10%. When the
performance of teacher and student networks is enhanced, the
distillation effect is also better. PipelineADVinT/EfficientNetB0 improves by 11.79% compared to the original student
model, reaching 89.48%. However, the improvement effect
is limited compared to the improved OFA model, with the
accuracy increase of approximately 1%. After checking the
misclassified samples, it was found that improvements in
the OFA model can only be effective when special samples are
prone to misleading. This may play a crucial role for practical
applications in real-time signal recognition. Moreover, it can
be seen from the number of parameter and FLOPs that the
proposed method can significantly improve the recognition
ability of student models with small parameter quantities,
while reducing computational costs.
Fig. 4 (a) indicates that ViT-based is more suitable as
the teacher network in pipeline scenarios. Compared with
CNN-based teacher networks, it can significantly improve
the performance of trained student networks. On the one
hand, it is due to the limited performance of shallow ViT
models as student networks. On the other hand, the global
information obtained by the ViT model of attention mechanism
can be transmitted to the CNN model to compensate for the
missing feature information during the convolution process.
As shown in Fig. 4 (b), the test results on three datasets
show that the proposed method can improve the average

ZHU et al.: LIGHTWEIGHT PIPELINE EDGE DETECTION MODEL

Fig. 4. (a) Test accuracy curves in different KD directions, (b) Experimental
comparison of the proposed methods on different pipelines.

recognition accuracy of the model by 10%, which has strong
generalization ability and stable improvement on lightweight
student networks.
V. C ONCLUSION
This brief proposed an adaptive heterogeneous model
knowledge distillation network for the pipeline network
deployed detection models at the edge. The proposed
method effectively improves the recognition performance of
lightweight CNN-based models by projecting logits space
for heterogeneous model knowledge distillation. We introduce
learnable modulation parameter and model selection at each
stage of knowledge distillation for target information enhancement and the effectiveness of knowledge transfer. Experiments
on several pipelines have confirmed the superiority of the
proposed method. Experimental results show that the accuracy
of AHKDnet is 10% higher than that of the original student
model, and about 1% higher than that of SOTA KD method.
R EFERENCES
[1] Y. Yang, Y. Li, T. Zhang, Y. Zhou, and H. Zhang, “Early safety
warnings for long-distance pipelines: A distributed optical fiber sensor
machine learning approach,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 14991–14999.
[2] Z. Lyu, C. Zhu, Y. Pu, Z. Chen, K. Yang, and Q. Yang, “Two-stage
intrusion events recognition for vibration signals from distributed optical
fiber sensors,” IEEE Trans. Instrum. Meas., vol. 73, pp. 1–10, Nov. 2024.
[3] M. Ding, Z. Lin, C. H. Lee, C. H. Tan, and W. Huang, “A multiscale channel attention network for prostate segmentation,” IEEE Trans.
Circuits Syst. II, Exp. Briefs, vol. 70, no. 5, pp. 1754–1758, May 2023.
[4] J. Tejedor, J. Macias-Guarasa, H. F. Martins, S. Martin-Lopez, and
M. Gonzalez-Herraez, “A contextual GMM-HMM smart fiber optic
surveillance system for pipeline integrity threat detection,” J. Lightw.
Technol., vol. 37, no. 18, pp. 4514–4522, Sep. 2019.
[5] H. Meng, S. Wang, C. Gao, and F. Liu, “Research on recognition method
of railway perimeter intrusions based on φ-OTDR optical fiber sensing
technology,” IEEE Sensors J., vol. 21, no. 8, pp. 9852–9859, Apr. 2021.
[6] C. Zhu, Y. Pu, Y. Yang, Z. Lyu, C. Li, and Q. Yang, “Localizing and
tracking of in-pipe inspection robots based on distributed optical fiber
sensing,” Adv. Eng. Inform., vol. 60, Apr. 2024, Art. no. 102424.

5063

[7] C. Zhu, Y. Yang, K. Yang, H. Zhang, Q. Yang, and C. L. P. Chen,
“AI-based energy transportation safety: Pipeline radial threat estimation
using intelligent sensing system,” in Proc. AAAI Conf. Artif. Intell., 2024,
pp. 1–9.
[8] H. Wu et al., “Smart fiber-optic distributed acoustic sensing (sDAS) with
multitask learning for time-efficient ground listening applications,” IEEE
Internet Things, vol. 11, no. 5, pp. 8511–8525, Mar. 2024.
[9] C. Zhu, K. Yang, Q. Yang, Y. Pu, and C. L. P. Chen, “A comprehensive
bibliometric analysis of signal processing and pattern recognition based
on distributed optical fiber,” Measurement, vol. 206, pp. 1–17, Jan. 2023.
[10] K. Yang, Z. Yu, W. Chen, Z. Liang, and C. L. P. Chen,
“Solving the imbalanced problem by metric learning and oversampling,” IEEE Trans. Knowl. Data Eng., early access, Jun. 27, 2024,
doi: 10.1109/TKDE.2024.3419834.
[11] H. Wu et al., “One-dimensional CNN-based intelligent recognition of
vibrations in pipeline monitoring with DAS,” J. Lightw. Technol., vol. 37,
no. 17, pp. 4359–4366, Sep. 2019.
[12] W. Chen, K. Yang, Z. Yu, Y. Shi, and C. L. P. Chen, “A survey on imbalanced learning: Latest research, applications and future directions,” Artif.
Intell. Rev., vol. 57, no. 6, pp. 1–51, 2024.
[13] C. Zhu, Y. Pu, K. Yang, Q. Yang, and C. L. P. Chen, “Distributed
optical fiber intrusion detection by image encoding and SwinT in
multi-interference environment of long-distance pipeline,” IEEE Trans.
Instrum. Meas., vol. 72, pp. 1–12, May 2023.
[14] C. Zhu, Y. Pu, K. Yang, Q. Yang, and C. L. P. Chen, “A novel visual
transformer for long-distance pipeline pattern recognition in complex
environment,” IEEE Trans. Artif. Intell., vol. 5, no. 6, pp. 2933–2945,
Jun. 2024.
[15] J. Gou, B. Yu, S. J. Maybank, and D. Tao, “Knowledge distillation: A
survey,” Int. J. Comput. Vis., vol. 129, pp. 1789–1819, Mar. 2021.
[16] C. Zhang, Y. Liao, S. Han, M. Zhang, Z. Wang, and X. Xie,
“Multichannel multidomain-based knowledge distillation algorithm for
sleep staging with single-channel EEG,” IEEE Trans. Circuits Syst. II,
Exp. Briefs, vol. 69, no. 11, pp. 4608–4612, Nov. 2022.
[17] Z. Hao et al., “One-for-all: Bridge the gap between heterogeneous
architectures in knowledge distillation,” in Proc. 37th Adv. Neural Inf.
Process. Syst., 2024, pp. 1–13.
[18] D. Wang, N. Zhang, M. Tao, and X. Chen, “Knowledge selection and
local updating optimization for federated knowledge distillation with
heterogeneous models,” IEEE J. Sel. Topics Signal Process., vol. 17,
no. 1, pp. 82–97, Jan. 2023.
[19] G. Hinton, O. Vinyals, and J. Dean, “Distilling the knowledge in a neural
network,” in Proc. Adv. Neural Inf. Process. Syst., 2015, pp. 1–9.
[20] W. Park, D. Kim, Y. Lu, and M. Cho, “Relational knowledge distillation,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2019,
pp. 3967–3976.
[21] B. Zhao, Q. Cui, R. Song, Y. Qiu, and J. Liang, “Decoupled knowledge
distillation,” in Proc. Conf. Comput. Vis. Pattern Recognit., 2022,
pp. 11953–11962.
[22] T. Huang, S. You, F. Wang, C. Qian, and C. Xu, “Knowledge distillation
from a stronger teacher,” in Proc. Adv. Neural Inf. Process. Syst., 2022,
pp. 33716–33727.
[23] A. Dosovitskiy and L. Beyer, “An image is worth 16x16 words:
Transformers for image recognition at scale,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit., 2021, pp. 770–778.
[24] Z. Liu et al., “Swin transformer: Hierarchical vision transformer
using shifted windows,” in Proc. IEEE Int. Conf. Comput. Vis., 2021,
pp. 10012–10022.
[25] G. Li, Z. Yu, K. Yang, M. Lin, and C. L. P. Chen, “Exploring
feature selection with limited labels: A comprehensive survey of semisupervised and unsupervised approaches,” IEEE Trans. Knowl. Data
Eng., early access, May 7, 2024, doi: 10.1109/TKDE.2024.3397878.
[26] M. Tan and Q. Le, “EfficientNet: Rethinking model scaling for convolutional neural networks,” in Proc. 36th Int. Conf. Mach. Learn, 2019,
pp. 6105–6114.
PAPER_TEXT
