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
# [493] Multi-task encrypted network traffic classification based on feature extraction
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
编号：493
题名：Multi-task encrypted network traffic classification based on feature extraction
年份：2025
DOI：10.1145/3723890.3723893
来源：Proceedings of the 2025 4th International Conference on Cryptography, Network Security and Communication Technology
PDF：paper/10.1145_3723890.3723893.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\493.txt
- 原始字符数：18607
- 本次发送字符数：18607
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Multi-task encrypted network traffic classification based on
feature extraction
Yiran Yu∗

Xin Guan

Electronics and Information Engineering School
Liaoning Technical University
Huludao, Liaoning, China
1804658920@qq.com

Electronics and Information Engineering School
Liaoning Technical University
Huludao, Liaoning, China
2918267944@qq.com

Abstract

or the designated port number and employ rules or feature sets to
differentiate between various forms of network traffic. As a result,
this approach has a low classification accuracy and is unable to
identify complex protocols and extremely covert attack traffic. Two
of the more important responsibilities in network traffic categorization are traffic characterization and application identification.
The majority of current solutions for these two tasks typically use
a single-task processing paradigm. While this method can partially satisfy the categorization requirements, it tends to lead to an
increase in the complexity of network management in practice.
This research suggests a multi-task encrypted network traffic
categorization approach based on Transformer-1DCNN-ECA to
overcome the aforementioned issues. The model increases the effectiveness of encrypted traffic categorization and allows simultaneous
multi-task learning by enabling application identification and traffic
characterization on the ISCX VPN-nonVON dataset.

Aiming to address the issue of traditional encrypted network traffic identification models’ shortcomings in feature extraction and
the use of separate models for traffic characterization and application identification in encrypted traffic classification, which makes
network management more difficult. Here, a Transformer-1DCNNECA-based multi-task encrypted traffic categorization model is
suggested. First, the dataset is cut, filled, and normalized to increase the classification accuracy; next, the Transformer model’s
multi-head attention mechanism is used to capture long-distance
feature dependencies and finish extracting global feature information; finally, 1DCNN is used to extract local features; Lastly, the
network becomes more focused on important features with the
addition of a lightweight ECA module, which enhances model performance and enables multi-task encrypted traffic categorization.
The average accuracy of this model on ISCX VPN-nonVPN dataset
for traffic feature and application identification classification is
97.97% and 98.27%, which is better than other models.

2

CCS Concepts

Deep learning algorithms have improved results in computer vision,
image processing, and other fields due to the rapid development of
artificial intelligence and big data. Researchers studying encrypted
network traffic have also started working with encrypted traffic
data that has various representations and have started using deep
learning models to automatically extract features to achieve detection and classification. Although it circumvents the drawbacks
of conventional DPI-based techniques for handling scenarios like
packet ordering, Dias et al.’s [1] novel approach for traffic categorization and identification using the ML method still has certain
restrictions. This approach combines K-means and KNN.An traffic
classification model based on LTSM and BERT was proposed by Shi
et al.[2] It achieves good classification accuracy, but the packet class
imbalance issue is still a common one that could cause the model’s
performance to deteriorate. Lin et al [3] , proposed a Bidirectional
Encoder Representation (BERT) for Convolutional Neural Network
Transformers. This classification model improves the accuracy of
classification but at a higher computational cost and time spent.
While multi-task classification models have not received much attention, the aforementioned issues emerge for single-task encrypted
traffic categorization. To achieve more accurate and efficient multitask encrypted traffic classification, this paper suggests a deep
learning model-based encrypted traffic classification by examining
the issues and models of single-task and multi-task encrypted traffic
classification. The model is comparatively faster and less costly to
compute, and it uses Transformer-1DCNN-ECA to obtain feature
information.

• Security and privacy → Human and societal aspects of security
and privacy; Usability in security and privacy.

Keywords
Encrypted network traffic classification, Multitasking, Feature extraction, Transformer, 1DCNN, ECA
ACM Reference Format:
Yiran Yu and Xin Guan. 2025. Multi-task encrypted network traffic classification based on feature extraction. In 2025 4th International Conference
on Cryptography, Network Security and Communication Technology (CNSCT
2025), January 17–19, 2025, Zhengzhou, China. ACM, New York, NY, USA,
5 pages. https://doi.org/10.1145/3723890.3723893

1

RELATED WORKS

INTRODUCTION

Some network administrators are confronted with the challenge
of classifying and handling encrypted traffic as its use grows in
popularity. Conventional techniques based on port number and
protocol type typically rely on the protocol’s plaintext information
∗ Corresponding author

This work is licensed under a Creative Commons Attribution International 4.0 License.
CNSCT 2025, Zhengzhou, China
© 2025 Copyright held by the owner/author(s).
ACM ISBN 979-8-4007-1262-3/2025/01
https://doi.org/10.1145/3723890.3723893

11

CNSCT 2025, January 17–19, 2025, Zhengzhou, China

Yiran Yu and Xin Guan

Figure 1: The model’s general framework.

3

CLASSIFICATION METHODOLOGY OF THIS
PAPER
3.1 Modeling Framework

and fall within the range of [0, 1].The model’s initial input data
format is the 1500-byte sequence that has been handled in this way.

3.3

The general framework diagram for the Transformer-1DCNN-ECA
multi-task encrypted traffic classification model presented in this
paper is displayed in Figure 1. To achieve the extraction of global
information, the raw encrypted traffic data is first used as the model
input following preprocessing; second, the Transformer encoder’s
input is subjected to a summation operation using word list coding
and position coding; the result is then input into the multi-head
attention layer and produced through the feed-forward network,
where residual connectivity and layer normalization operations
are performed between the layers;The output data is once more
subjected to a one-dimensional convolutional layer for the extraction of local features, followed by the ECA attention module for
the extraction of key feature information, the Flatten layer for the
one-dimensionalization of the multidimensional data, the Softmax
classifier for the multi-task encrypted traffic classification, and the
output of the results.

3.2

Transformer Encoder Block

After preprocessing, the traffic data is fed into the Transformer
encoder[4] . The Transformer model encodes the input data, which
is a sequence. A positional encoding layer is added to address the
issue of positional information in the sequence by appending a
corresponding positional vector to each position. The following
formula is used to determine the position encoding.



(2s)

= 𝑠𝑖𝑛 𝑖/100002s/d
 pi



(1)
(2s)

 pi+1 = 𝑐𝑜𝑠 𝑖/100002s/d

where i is the time step; s is the number of dimensions; and d
denotes the dimensionality of the model.
The encoder and decoder are the two components that make
up the Transformer’s structure. In this work, we use the encoder,
which is mostly utilized for feature extraction. A crucial component
of the feature extraction method is the Multi-Head Attention layer,
which allows each attention head to acquire distinct weights and
capture information in several representation subspaces. The singlehead self-attention module, which maps the input sequence into a
query matrix Q, a key-value matrix K, and a value matrix V, where
Q, K, and V∈ 𝑅𝑛∗𝑑𝑘 , and then linearly transforms and connects
the outputs of multiple heads to realize the extraction of global
feature information. The corresponding computational formulas
are displayed below.
!
QKT
Attention = soft max p
V
(2)
dk

Data Pre-processing

(1) The Ethernet header is first eliminated during the preprocessing
stage because the ISCX VPN-nonVPN dataset is recorded at the data
link layer and the physical link information it contains is useless
for identifying applications or traffic types and may lead to model
overfitting issues, Then the IP address in the IP header is changed
to 0.0.0.0;
(2) The two protocols, TCP and UDP, therefore have different
header lengths in the transport layer; the TCP protocol typically
has a header length of 20 bytes, while the UDP protocol has a header
length of 8 bytes. To make the lengths equal, you must add 0 at the
end of the UDP protocol header;
(3) Furthermore, Packets that execute the three-way TCP handshake and exclude any substantive data, such as DNS, ACK, SYN,
and FIN packets, predominantly utilized in service protocols, were
removed.
(4) Lastly, 0 bytes to 1500 bytes are added to the end of each
packet to guarantee consistency of the model input data. Each byte
value is divided by 255 to ensure the input values are normalized

MultiHead (Q, K, V) = Concat (Head1, Head2, ..., Headh ) W (3)


Q
V
Headi = Attention QWi , KWK
i , VWi

(4)

p
where dk denotes the channel dimension and dk is the scaling factor.In this paper, we choose h = 6, i.e., it consists of 6 self-attention
mechanisms.

12

Multi-task encrypted network traffic classification based on feature extraction

CNSCT 2025, January 17–19, 2025, Zhengzhou, China

Figure 2: ECA structure diagram.
Table 1: Traffic Type Label, Application Label and Auxiliary Task Label Information.
task1: Traffic type

task2: Application

task3: Auxiliary task

Email,File Transfer,
Chat,Torrent,Streaming,Voip,
VPN:Email,VPN:Chat,VPN:Streaming,
VPN:File Transfer,
VPN:Voip,VPN:Torrent

AIM Chat,Facebook,Email,
Netfix,SCP,Skype,SFTP,
FTPS,ICQ,Hangouts,Gmail,
Youtube,Voipbuster,
Spotify,Torrent,Vimeo,Tor

All_file Transfer,
All_Email,All_Chat
All_voip,All_Torrent,
All_Streaming

3.4

1DCNN Block

4.2

Even though the encrypted traffic data information has undergone
global feature extraction after going via the Transformer encoding
module, it may still have relatively low classification accuracy if it is
produced directly. To compensate for this and carry out more finegrained feature extraction, the CNN module—which is more sensitive to local feature extraction—must be added. Since encrypted
communication is regarded as sequential data and the 1DCNN module is more suited for traffic categorization than 2DCNN, 1DCNN
was selected in this instance.
Three convolutional layers, two maximum pooling layers, and
one dropout layer make up the 1DCNN module. Each convolutional
layer has a batch normalization layer to normalize the data, which
can effectively prevent gradient vanishing and gradient explosion
and increase the network’s stability. With a value of 0.5, the final Dropout layer can be somewhat more successful in reducing
overfitting to produce the regularization effect.

3.5

Experiment Dataset

The publicly available ISCX VPN-nonVPN encrypted traffic dataset
is chosen for the experiments, in multi-task encrypted traffic categorization, here the dataset will be reclassified into 12 traffic type
labels and 17 application labels, at the same time, a simple auxiliary
task can improve its categorization accuracy when performing a
complex task, therefore, an auxiliary task is introduced here, which
does not distinguish between encrypted traffic and normal traffic,
but only categorized by type. Table 1 displays the labeling data for
the three tasks.

4.3

Evaluation Metrics

In statistical classification, four often used measures are precision,
accuracy, F1-score and recall . Here, accuracy, F1-score, and recall are selected as assessment criteria for traffic categorization
to more thoroughly assess the Transformer-1DCNN-ECA multitasking model. The following formula is used to determine these
metrics.
TN + TP
Accuracy =
(5)
TP + FP + TN + FN
TP
Presion =
(6)
TP + FP
TP
Recall =
(7)
FN + TP
2 × Pr esion × Recall
F1 =
(8)
Pr esion + Recall
where TP represents true positive, FP signifies false positive, TN
stands for true negative, and FN denotes false negative.

ECA Block

Following the extraction of data information using 1DCNN, an effective and lightweight ECA is introduced to reduce the computational
complexity and number of parameters, improve the network’s ability to pay attention to the encrypted traffic data, and highlight the
important features of the traffic data while suppressing redundant
information by adaptively adjusting the weights of each channel.In
Figure 2, the ECA structure is displayed.

4 EXPERIMENT AND RESULT ANALYSIS
4.1 Experimental Environment

4.4

Analysis of Experimental Results

4.4.1 Ablation Experiment. The model architecture of this paper is
Transformer-1DCNN-ECA, and The Transformer model[4] is used
as a baseline model to analyze the role of different modules by
comparing other models. The results are shown in Table 2 and
Figure 3.

The software framework used for the experimental platform is
Python 3.12, Cuda 12.1, and the experimental model training library
is PyTorch 2.3.0, running under the ubuntu22.04 system environment, with 48GB of RAM, an Intel(R) Xeon (R) Platinum 8352 CPU,
and an RTX 3080x2 GPU ( 20GB).

13

CNSCT 2025, January 17–19, 2025, Zhengzhou, China

Yiran Yu and Xin Guan

Table 2: Ablation experiment results for each model for classification on auxiliary tasks, application identification, and flow
characterization.
Model
Baseline
+1DCNN
+ECA
+1DCNN+ECA

Acc

Tra.
F1

Recall

Acc

App.
F1

Recall

Acc

Aux.
F1

Recall

0.9599
0.9618
0.9657
0.9797

0.9590
0.9610
0.9655
0.9796

0.9544
0.9619
0.9611
0.9760

0.9727
0.9749
0.9748
0.9827

0.9727
0.9745
0.9744
0.9824

0.9718
0.9758
0.9755
0.9832

0.9689
0.9713
0.9714
0.9790

0.9686
0.9710
0.9711
0.9789

0.9650
0.9699
0.9697
0.9780

Figure 3: (a) (b) (c) (d) (e) (f) (g) (g) (h) (i) are F1-score, Recall and Accuracy classification plots of each model on each categories
of traffic characteristics, application identification and auxiliary tasks, respectively
According to the findings of the ablation experiment, the suggested model outperforms the benchmark model by roughly 2% in
terms of accuracy, F1-score, and recall. Thus, this paper’s suggested
model can fully utilize the Transformer and 1D-CNN block features
to extract information related to long distance from traffic data,
extract local detail information, and then use the ECA features for
multi-task classification of encrypted traffic.

As suggested in this research, the model outperforms other popular models on both tasks, as the above table demonstrates.

5

CONCLUSION

This paper establishes a multi-task encrypted traffic classification
model based on Transformer-1DCNN-ECA to address the issues
of inadequate extracted feature information and complex network
traffic management of traditional traffic classification methods. The
model’s performance for multi-task encrypted traffic classification
is improved by first using the Transformer model’s coding part to
extract global features, then using 1DCNN for the extracted global
features to achieve a fine-grained portrayal of local features, and
finally using the ECA model for important feature extraction. By

4.4.2 Comparison Experiments. The model in this research is compared with six related working models for comparative studies
to further validate the model’s efficacy. Table 3 displays the findings of the comparison tests of F1-score and Recall with six other
popular deep learning models on the dataset for 12 traffic-type
classifications and 17 application-type classifications.

14

Multi-task encrypted network traffic classification based on feature extraction

CNSCT 2025, January 17–19, 2025, Zhengzhou, China

Table 3: Accuracy, F1-score, and Recall Results Comparison for Various Models.
Methods on ISCX VPN-non VPN
1DCNN[5]

SAE[5]
MTC[6]
TSCRNN[7]
CNN+GRU[8]
RBRN[9]
Transformer-1DCNN-ECA

Acc

Tra.
F1

Recall

Acc

App.
F1

Recall

0.9329
0.9200
0.9787
0.9722
0.9797

0.9377
0.9200
0.9794
0.9260
0.9721
0.9796

0.9306
0.9200
0.9754
0.9260
0.9733
0.9760

0.9758
0.9500
0.9825
0.9611
0.9827

0.9785
0.9500
0.9825
0.9608
0.9824

0.9745
0.9500
0.9830
0.9832

conducting ablation studies on the ISCX VPN-nonVPN dataset, the
influence of each sub-module within the model on the experimental
results is elucidated, and it is also illustrated that the proposed
model exhibits superior classification capabilities. In conclusion,
comparative experiments reveal that the proposed model surpasses
other established related works in terms of Recall, Accuracy and
F1-score metrics on the dataset.

in Proc. of the ACM Web Conf. 2022, UK, pp. 633–642, 2022.
[4] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones et al., “Attention is all you
need,” Advances in Neural Information Processing Systems, vol. 30, pp. 5998–6008,
2017.
[5] M. Lotfollahi, M. J. Siavoshani, R. S. H. Zade, and M. Saberian, “Deep packet:
a novel approach for encrypted traffic classification using deep learning,” Soft
Computing, vol. 24, no. 3, pp. 1999-2012, Feb, 2020.
[6] K. Y. Wang, J. Gao, and X. Y. Lei, “MTC: A Multi-Task Model for Encrypted Network
Traffic Classification Based on Transformer and 1D-CNN,” Intelligent Automation
and Soft Computing, vol. 37, no. 1, pp. 619-638, 2023.
[7] K. Lin, X. Xu and H. Gao, “TSCRNN: A novel classification scheme of encrypted
traffic based on flow spatiotemporal features for efficient management of IIoT,”
Computer Networks, vol. 190, pp. 107974, 2021.
[8] C. Dong,C. Zhang,Z. Lu, B. Liu andB. Jiang, “CETAnalytics: Comprehensive
effective traffic information analytics for encrypted traffic classification,” Computer
Networks, vol. 176, pp. 107258, 2020.
[9] W. Zheng, C. Gou, L. Yan and S. Mo, “Learning to classify: A flow-based relation
network for encrypted traffic classification,” in Proc. of the Web Conf. 2020, New
York, NY, USA, pp. 13–22, 2020.

References
[1] K. L. Dias, M. A. Pongelupe, W. M. Caminhas, and L. de Errico, “An innovative
approach for real-time network traffic classification,” Computer Networks, vol.
158, pp. 143-157, Jul, 2019.
[2] Z. L. Shi, N. Luktarhan, Y. Y. Song, and H. X. Yin, “TSFN: A Novel Malicious Traffic
Classification Method Using BERT and LSTM,” Entropy, vol. 25, pp. 1-15, May,
2023.
[3] X. Lin, G. Xiong, G. Gou, Z. Li, J. Shi et al., “ET-BERT: A contextualized datagram
representation with Pre-training transformers for encrypted traffic classification,”

15
PAPER_TEXT
