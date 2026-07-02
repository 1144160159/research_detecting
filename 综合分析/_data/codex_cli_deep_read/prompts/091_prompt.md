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
# [091] tCLD-Net: A Transfer Learning Internet Encrypted Traffic Classification Scheme Based on Convolution Neural Network and Long Short-Term Memory Network
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
编号：091
题名：tCLD-Net: A Transfer Learning Internet Encrypted Traffic Classification Scheme Based on Convolution Neural Network and Long Short-Term Memory Network
年份：2021
DOI：10.1109/ccci52664.2021.9583214
来源：2021 International Conference on Communications, Computing, Cybersecurity, and Informatics (CCCI)
PDF：paper/10.1109_ccci52664.2021.9583214.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\091.txt
- 原始字符数：22940
- 本次发送字符数：22940
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2021 International Conference on Communications, Computing, Cybersecurity, and Informatics (CCCI) | 978-1-6654-3208-5/21/$31.00 ©2021 IEEE | DOI: 10.1109/CCCI52664.2021.9583214

tCLD-Net: A Transfer Learning Internet Encrypted
Traffic Classification Scheme Based on Convolution
Neural Network and Long Short-Term Memory
Network
Xinyi Hu1 ∗† , *Chunxiang Gu2 ∗† , Yihang Chen3 ∗ and Fushan Wei4 ∗† ∗ State Key Laboratory of Mathematical
Engineering and Advanced Computing, Zhengzhou, China
† Henan Key Laboratory of Network Cryptography Technology, Zhengzhou, China
Email: 1 huxinyi.1994@foxmail.com, 2 gcx5209@126.com, 3 cyhpaper@163.com, 4 weifs831020@163.com

Abstract—The Internet is about to enter the era of full encryption. Traditional traffic c lassification me thods on ly wo rk we ll in
non-encrypted environments. How to identify the specific types of
network encrypted traffic i n a n e ncrypted e nvironment without
decryption is one of the foundations for maintaining cyberspace
security. Traffic c lassification ba sed on ma chine le arning relies
heavily on the prior knowledge of experts to construct feature
sets. Although traffic c lassification ba sed on de ep le arning can
reduce human intervention, it requires a large amount of labeled
data for parameter determination. This paper proposes a tCLDNet model that combines transfer learning and deep learning. It
can be trained on a small amount of labeled data to distinguish
network encrypted traffic w ith a h igh a ccuracy. I t p re-trains a
CLD-Net model in the source domain data set, and fixes the
parameters of the convolutional neural network module in it,
and trains and tests it in the target domain data set. In order to
verify the effectiveness of the tCLD-Net model, we use the ISCX
public data set to conduct experiments. The results show that
our proposed model can complete 100 epoches training in 208
seconds when the training set only occupies 20% of the target
domain. And achieve a classification a ccuracy r ate a bout 86%.
This is 4% higher than the model without pre-training, and the
training time is only one third of the model without pre-training.
Index Terms—Deep Learning, Transfer Learning, Pre-training,
Internet Traffic, E ncrypted Traffic, Tr affic Classification

I. I NTRODUCTION
Network traffic c lassification an d id entification is an important foundation for network monitoring and management,
and it is also one of the key technologies for maintaining cyberspace security. However, with the development of network
encryption, the existing port-based and deep packet inspectionbased technologies are difficult to identify and classify network
traffic, w hich c auses d ifficulties in tr affic rev iew. Researchers
began to consider introducing machine learning technology
into the field of traffic analysis. According to prior experience,
feature engineering is carried out, feature set is constructed,
and then the feature set is input into the machine learning
classifier f or c lassification an d identification.
Since traditional machine learning methods need to manually construct feature sets, the quality of the feature set

directly affects the effect of the classifier. In order to reduce
manual intervention, researchers use deep learning technology
to automatically perform feature learning and classification. As
the representative of deep learning technology, artificial neural
network is regarded as an end-to-end model. Researchers
only need to input the raw flows, or simply process the raw
flows, and then input them into the neural network, the neural
network will directly output the results that researchers want.
However, deep learning models require a large amount
of high-quality labeled data, and in the real environment,
there are often only a small amount of labeled data or even
unlabeled data. A small amount of data cannot be solved by
deep learning because there are too many parameters and the
number of samples cannot support it to learn well, which can
easily lead to overfitting of the model. Transfer learning can
transfer knowledge from existing data to help future learning.
The goal of transfer learning is to use knowledge learned from
one environment to help learning tasks in a new environment.
Considering that data or tasks are related, this paper combines
deep learning and transfer learning to propose the tCLD-Net
model for network encryption traffic classification. The model
that has been trained on the source domain is used as a pretraining model and passed to the target domain for training and
testing. This can speed up the optimization of the learning
efficiency of the model, reduce the amount of sample data
required, and reduce training costs.
The rest of the paper is organized as follows. Section 2
summarizes related work. Section 3 describes the problem
definition and introduces the proposed model. Section 4 gives
the data set and experimental results. Section 5 summarizes
the paper and discusses future work.
II. R ELATED W ORK
A. Traffic Analysis Using Deep Learning
Researches on the use of deep learning for traffic analysis
began to appear in 2015 [1], and has developed rapidly in
recent years [2]–[4], [6].
In 2018, Tong et al. [2] proposed a new technology of
traffic classification based on convolutional neural network

978-1-6654-3208-5/21/$31.00 © 2021 IEEE
Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:31:41 UTC from IEEE Xplore. Restrictions apply.

for Google’s QUIC protocol (Quick UDP Internet Connection
protocol). This method can distinguish Google Hangout Chat,
Google Hangout Voice Call, YouTube, File Transfer and
Google Play Music with a micro average F1-score of 99.24%.
In 2019, Aceto et al. [3] proposed a multimode deep
learning framework for encrypted traffic classification, which
can utilize the heterogeneity of traffic data to overcome the
existing single-mode deep learning-based traffic classification
performance limitation, and verified it on the artificially generated mobile encrypted traffic dataset.
In 2020, Bu et al. [4] proposed a neural network model
with a deeply parallel network-in-network (NIN) structure to
classify encrypted network traffic. The experimental results
on the public dataset ISCX VPN-nonVPN [5] (Virtual Private
Network) show that compared with the traditional Convolution
Neural Network (CNN), the NIN model can achieve a better
balance between classification accuracy and model complexity.
In 2021, Hu et al. [6] proposed a network encryption traffic
classification model CLD-Net. The model combines CNN and
Long Short-Term Memory (LSTM) network to perform neural
network feature learning from both statistics and time series,
and changes the number of channels to make the model more
suitable for the reorganized data structure, thereby improving
classification performance. CLD-Net has higher accuracy than
other methods when encrypting traffic classification for public
network traffic data, and the average accuracy of the eightclass is 92.89%.
B. Traffic Analysis Using Transfer Learning
Transfer learning can eliminate the assumption that the
training set and the test set must be independent and identically
distributed. Therefore, as deep learning is developing in the
field of traffic analysis, researchers have also begun to use
transfer learning for traffic analysis [7], [9], [11]–[14].
In 2018, Sun et al. [7] introduced transfer learning to the
task of traffic classification. The maximum entropy model
Maxent is used as the basic classifier, and TrAdaBoost [8]
transfer learning model is selected. The comparison with
traditional machine learning method shows that the proposed
method can inprove overall performanced.
In 2019, Niu et al. [11] proposed a network intrusion detection method based on transfer component analysis. Through
domain adaptation, differently distributed data sets are mapped
to the same subspace. The model uses the basic classifier in
the shared subspace for training and detects new traffic data
generated from different domains.
In 2020, Han et al. [12] transferred the pre-trained language
model with language data to the network traffic classification
problem, then fine-tune the model with labeled network traffic.
This method has faster convergence speed, higher accuracy
rate and lower false positive rate.
In 2021, Dhillon et al. [13], [14] used various deep learning
methods to build a network intrusion detection system (NIDS),
and used deep transfer learning technology to further improve
the program to make it effective in the real environment. The
knowledge learned by the model in the source domain with a
large number of computing and data resources is transferred

to the target domain with sparse availability. The experimental
results on the public dataset USNW-15 show that this method
can improve the overall effectiveness of the intrusion detection
system (IDS) in the real environment.
III. P ROPOSED M ETHODOLOGY
Before the data is input to the model, the raw data must be
preprocessed. See Algorithm 1 for details. The preprocessing
procedure mainly includes 5 steps:
1) Lines 2-4 are traffic split. According to the size of
the flow, the raw data in the data set are randomly
spli into flow fragments containing 10 consecutive data
packets, and the training set and the test set are divided
proportionally.
2) Line 7 is traffic cleaning, only read the payload part of
the packet, and the uniform length is 256 bytes.
3) Lines 8-10 are traffic reorganization, where the 256byte payload is divided into different bytes and then
reorganized.
4) Line 11 is traffic conversion. The 5 sequences after step
2 and step 3 are converted to decimal by byte to obtain
a grayscale image.
5) Lines 15-19 are insertion time interval. According to
the length of the arrival time interval of two adjacent
packets, with 1 second as the limit, a matrix of all 1s is
selected as the time interval information.
After the preprocessing, the obtained data packet matrices
are input into the model. In this paper, we combine the CLDNet model [9] with transfer learning to obtain an improved
tCLD-Net model, as shown in Figure 1.

Fig. 1. The tCLD-Net model structure. The upper layer is the pre-training
process, and the lower layer is the transfer process.

The pre-training process is performed in the source domain
using the CLD-Net model. The CLD-Net model includes a
CNN module, an LSTM module, and a Dense module. The
CNN module contains 10 1D-CNNs (one-dimensional CNNs),
each CNN contains 4 convolutional layers, and the last 3
convolutional layers are connected to a maximum pooling
layer. The LSTM module contains 10 LSTMs. The Dense
module contains 3 fully connected layers. After the source
domain data is preprocessed, it is converted into a grayscale image format, and the CNN’s ability to process image
data is used to automatically learn features. After passing
through the LSTM module, the ability of LSTM to process

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:31:41 UTC from IEEE Xplore. Restrictions apply.

Algorithm 1 Preprocessing Algorithm.
Input: Raw dataset D; Number of traffic classes C;
Output: Packet matrices set P;
1: for each i ∈ [1, C] do
2:
Randomly select N consecutive 10 packets in D;
3:
10 consecutive packets consist a flow F , that is, the number of F is N ;
4:
Randomly divide the F into a training set F train and a testing set F test in proportion;
5:
for each j ∈ [1, N ] do
6:
for each packet p ∈ F do
7:
Trim p and uniform length of 256 bytes, p → payload p256 = (b1 , b2 , · · · , b8×256 );
8:
256 bytes are divided into 64 bytes, 32 bytes, 16 bytes and 8 bytes to get the packet sequence p256 → pα =
α
α
α
(bα
1,1 , · · · , b1,α×8 , · · · , b 256 ,1 , · · · , b 256 ,8α );
α
α
9:
Separate 256 bytes by the length of 1 byte;
10:
Extract each group of the same bits in turn as the recombined part to obtain recombination sequence pα →
α
α
α
p̂α = (bα
1,1 , · · · , b 256 ,1 , · · · , b1,8α , · · · , b 256 ,8α );
α
α
11:
Generate the grayscale image format to get the packet matrix, p̂α → P , P T = (p256 , p̂64 , p̂32 , p̂16 , p̂8 );
12:
end for;
13:
end for;
14:
for m = 1 to 10N − 1 do
15:
Count the time interval of Pm and Pm+1 ;
16:
if the time interval between Pm and Pm+1 < 1s then
17:
Input Pm+1 after Pm to the model;
18:
else


1 ··· 1


19:
Add P0 =  ... . . . ... 
between Pm and Pm+1 ;
1

···

1

20:
end if
21:
end for;
22: end for;
23: return Packet matrices set P;

5×256

long stream data is used to continue the feature mapping.
Finally, through the Dense module, the fully connected layers
are used to perform feature dimensionality reduction, and the
final classification results are output. After pre-training for 100
epochs, the pre-trained model is obtained. See Algorithm 2 for
the specific pre-training algorithm.
Fix the parameters of the CNN module in the pre-trained
model, and transfer the model to the target domain to continue
training and testing. After the transfer, the intersection of the
target domain data and the source domain data is an empty
set, and the amount of target domain data is reduced. During
the 100 epoches training process, fine-tune the parameters
of the LSTM module and the Dense module. Finally, the
classification results are predicted in the test set of the target
domain, and the results are evaluated.
IV. E XPERIMENT

TABLE I
DATA CLASSES AND DATA VOLUME OF THE SOURCE AND TARGET
DOMAINS .

Data classes

Number of flows

Source Dataset
facebook-audio,
facebook-chat,
facebook-video,
vpn-facebook-audio,
vpn-facebook-chat
4059

Target Dataset
hangout-chat,
hangout-audio,
vpn-hangout-audio
6590

The experiment uses a total of 8 classes of data, 5 classes
are selected as the source domain data, and the remaining 3
classes are used as the target domain data. See Table 1 for
details. Among them, the target domain data randomly selects
20%, 40%, 60%, 80% of the data as the training set, and the
rest as the test set.

A. Dataset
This paper uses the public data set ISCX VPN 2016 [5], and
selects the traffic data of the two social software Facebook and
Hangout as the experimental data. Facebook traffic includes
three applications: chat, audio, and video, Hangout traffic includes two applications: chat and audio. And the traffic of each
specific application can use VPN for protocol-encapsulated
network traffic, or just ordinary network traffic nonVPN.

B. Experiment Results
The experiment selects 4 models for training and testing of
the target domain. They are: model without pre-training, CLDNet pre-training model with fixed CNN module parameters,
CLD-Net pre-training model with fixed CNN module parameters and LSTM module parameters , CLD-Net pre-training
model without fixed parameters. The experiment chooses clas-

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:31:41 UTC from IEEE Xplore. Restrictions apply.

Algorithm 2 Pre-training Algorithm.
Input: Source dataset DS ; Number of traffic classes CS ; Number of epoches Epo;
Output: Pre-trained model;
1: Preprocess DS using Alogrithm 1 to obtain packet matrices set;
2: for n ∈ [1, Epo] do
3:
for each P in Packet matrices set do
4:
Let P T = (x1 , x2 , x3 , x4 , x5 );
5:
for each x ∈ P do
1
6:
Let W is the weight, B is the bias, the output of the first convolutional layer is Out1ij = Relu(Convij
), where
P
3
1
0
0
0
Convij = m=1 Wm,j xi+m−1,j + Bj ;
2
2
7:
The output of the second convolutional layer is Out2ij = Relu(maxr≤3 (Convi×1+r,j
)), where Convij
=
PM
1
1
1
W
x
+
B
;
m,j i+m−1,j
j
m=1
8:
The third and forth layers are the same as the second layer, the output of CNN module output is Out4ij =
4
)); // CNN module;
Relu(maxr≤3 (Convi×1+r,j
9:
end for;
10:
Let Xt (the input of LSTM at time t) pass through the forget gate F (t) = sigmoid(WfT St−1 + UfT Xt + Bf ) and
output gate O(t) = sigmoid(WoT St−1 + UoT Xt + Bo ), where U is the weight matrix of hidden state, Ct−1 is the cell
state at the previous time, St−1 is the hidden state;
11:
The cell state at time t is Ct = Ct−1 ∗ F (t) + I(t) ∗ R(t), the output of the LSTM module is the hidden state at
time t, St = tanh(Ct ) ∗ O(t); // LSTM module;
12:
Set the output of the first fully connected layer to half of the input;
13:
Add a Dropout layer after the second Dense layer, and remove the training unit from the network according to a
certain probability to prevent overfitting;
14:
Add a Softmax classifier after the third Dense layer, the data is divided into CS classes; // Dense module;
15:
end for;
16: end for;
17: return Pre-trained model;

sification accuracy and training time as the basis for evaluating
the model.

Fig. 3. Accuracy of the 2 models with and without transfer learning based
on 20%, 40%, 60%, 80% random samples for training on target domain.
Fig. 2. Accuracy curve of 4 different models based on 20% random samples
on target domain.

It can be seen from Figure 2 that when the training set is
20%, the training speed is slow, and the starting point accuracy
is low. It is gradually improved by continuous iteration, and
the highest accuracy rate can reach 82%. The CLD-Net pretraining model with fixed CNN module parameters and LSTM
module parameters has a high starting point, but it can hardly
be improved because of too many fixed parameters. The CLD-

Net pre-training model without fixed parameters has a high
starting point, but the training speed is slow, and later all
parameters are fine-tuned, which will overfit because of too
small training set. The best effect is the CLD-Net pre-training
model with fixed CNN module parameters. The starting point
is high, and because there are few parameters need to be finetuned, the training speed is fast, and accuracy rate 86% can
be quickly achieved.
It can be seen from Figure 3 that when the training set

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:31:41 UTC from IEEE Xplore. Restrictions apply.

is 20%, there is a large gap between the model without pretraining and the CLD-Net pre-training model with fixed CNN
module parameters, which is about 4%. When the training
set is 40%, the gap is not much, about 1.6%. Eventually, as
the size of the training set becomes larger, the advantages of
transfer learning will gradually disappear.

Fig. 4. Training time of 3 different models based on 20% random samples
on target domain.

It can be seen from Figure 4 that the training time of model
without pre-training is 584.1 seconds. The training time of the
CLD-Net pre-training model without fixed parameters is 604.1
seconds. The training time of the CLD-Net pre-training model
with fixed CNN module parameters is 208.4 seconds.
Therefore, transfer learning can effectively improve the
classification accuracy and greatly reduce the amount of data
required for training. When the training set is reduced to 20%,
the CLD-Net pre-training model with fixed CNN module parameters can not only achieve a higher classification accuracy,
but also requires a shorter training time, which is the best
among the four models.

ACKNOWLEDGMENT
This work was supported in part by the National Natural
Science Foundation of China under Grant 61772548.
R EFERENCES
[1] Z. Wang, “The applications of deep learning on traffic identification,”
BlackHat USA, vol. 24, pp. 1–10, 2015.
[2] V. Tong, H. A. Tran, S. Souihi, A. Mellouk, “A Novel QUIC Traffic
Classifier Based on Convolutional Neural Networks,” IEEE Global
Communications Conference (GLOBECOM), pp. 1–6, 2018.
[3] G. Aceto, D. Ciuonzo, A. Montieri, A. Pescapé, “MIMETIC: Mobile encrypted traffic classification using multimodal deep learning,” Computer
Networks, vol. 165, 2019.
[4] Z. Bu, B. Zhou, P. Cheng, K. Zhang, Z. Ling, “Encrypted Network
Traffic Classification Using Deep and Parallel Network-in-Network
Models,” IEEE Access, vol. 8, pp. 132950–132959, 2020.
[5] G. Draper-Gil, A. H. Lashkari, M. S. I. Mamun, A. A. Ghorbani,
“Characterization of Encrypted and VPN Traffic using Time-related
Features,” Information Systems Security and Privacy (ICISSP), 2016.
[6] X. Hu, C. Gu, F. Wei, “CLD-Net: A Network Combining CNN and
LSTM for Internet Encrypted Traffic Classification,” Security and Communication Networks, vol. 2021, 2021.
[7] G. Sun, L. Liang, T. Chen, F. Xiao, F. Lang, “Network traffic classification based on transfer learning,” Computers and Electrical Engineering,
vol. 69, pp. 920–927, 2018.
[8] W. Dai, Q. Yang, G. Xue, Y. Yu, “Boosting for transfer learning,”
International Conference on Machine Learning (ICML), pp. 193–200,
2007.
[9] S. Taheri, M. Salem, J. Yuan, “Leveraging Image Representation of
Network Traffic Data and Transfer Learning in Botnet Detection,” Big
Data Cognitive Computing, vol. 2, pp. 37–52, 2018.
[10] S. Garcı́a, M. Grill, J. Stiborek, A. Zunino, “An empirical comparison
of botnet detection methods,” Computer Security, vol. 45, pp. 100–123,
2014.
[11] J. Niu, Y. Zhang, D. Liu, D. Guo, Y. Teng, “Abnormal Network Traffic
Detection Based on Transfer Component Analysis,” IEEE International
Conference on Communications Workshops (ICC Workshops), pp. 1–6,
2019.
[12] L. Han, X. Zeng, L. Song, “A Novel Transfer Learning Based on Albert
For Malicious Network Traffic Classification,” International Journal of
Innovative Computing, Information and Control,vol. 16, pp. 2103–2119,
2020.
[13] H. Dhillon, A. Haque, “Towards Network Traffic Monitoring Using
Deep Transfer Learning,” IEEE 19th International Conference on Trust,
Security and Privacy in Computing and Communications (TrustCom),
pp. 1089–1096, 2020.
[14] H. Dhillon, “Building Effective Network Security Frameworks using
Deep Transfer Learning Techniques,” Electronic Thesis and Dissertation
Repository, 2021.

V. C ONCLUSION
In this paper, we propose a network encryption traffic
classification model based on transfer learning and deep learning. Compared with the traffic classification method based
solely on deep learning, this model does not require a large
amount of labeled data for training. In this model, through
pre-training and fixing the parameters of the CNN module,
the classification accuracy can be effectively improved and
the training time can be greatly reduced. The experimental
results on the public data set show that when the training set
only accounts for 20% of the data set, the performance of the
tCLD-Net model is significantly improved compared to the
model without pre-training.
In future work, we can consider using the pre-trained model
in the unlabeled data set to further fit the actual network
environment. In addition, how to eliminate the impact of the
unbalanced data set is also a future research direction.

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 01:31:41 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
