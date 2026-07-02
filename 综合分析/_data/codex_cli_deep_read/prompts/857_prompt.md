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
# [857] M3S-UPD: Efficient Multi-Stage Self-Supervised Learning for Fine-Grained Encrypted Traffic Classification With Unknown Pattern Discovery
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
编号：857
题名：M3S-UPD: Efficient Multi-Stage Self-Supervised Learning for Fine-Grained Encrypted Traffic Classification With Unknown Pattern Discovery
年份：2025
DOI：10.48550/arXiv.2505.21462
来源：未识别
PDF：paper/10.48550_arXiv.2505.21462.pdf
已有粗分类：加密流量分类与应用识别
二级关联：无
相关性：强相关，分数 16
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\857.txt
- 原始字符数：129389
- 本次发送字符数：129389
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                      1




                                             M3S-UPD: Efficient Multi-Stage Self-Supervised
                                              Learning for Fine-Grained Encrypted Traffic
                                             Classification with Unknown Pattern Discovery
                                                           Yali Yuan, Yu Huang, Xingjian Zeng, Hantao Mei, and Guang Cheng*, Member, IEEE



                                            Abstract—The growing complexity of encrypted network traf-                       and malicious traffic classification can be formulated as
                                         fic presents dual challenges for modern network management: ac-                     unknown traffic detection tasks.
arXiv:2505.21462v1 [cs.CR] 27 May 2025




                                         curate multiclass classification of known applications and reliable
                                         detection of unknown traffic patterns. Although deep learning                  Existing Machine Learning (ML) and Deep Learning (DL)-
                                         models show promise in controlled environments, their real-world               based ETC methods have proven their effectiveness on the
                                         deployment is hindered by data scarcity, concept drift, and opera-             two tasks in laboratory settings. These methods focus on
                                         tional constraints. This paper proposes M3S-UPD, a novel Multi-
                                         Stage Self-Supervised Unknown-aware Packet Detection frame-                    efficient, accurate, and robust encrypted traffic classification
                                         work that synergistically integrates semi-supervised learning                  by leveraging the powerful feature extraction and learning
                                         with representation analysis. Our approach eliminates artificial               capabilities of DL-based classifiers. Although these methods
                                         segregation between classification and detection tasks through                 demonstrate notable classification performance, some practical
                                         a four-phase iterative process: 1) probabilistic embedding gen-                issues remain to be discussed.
                                         eration, 2) clustering-based structure discovery, 3) distribution-
                                         aligned outlier identification, and 4) confidence-aware model                  1) Data Scarcity. Obtaining abundant labeled encrypted traffic
                                         updating. Key innovations include a self-supervised unknown                       is challenging in the online learning context. The insuffi-
                                         detection mechanism that requires neither synthetic samples nor
                                         prior knowledge, and a continuous learning architecture that is                   ciency of training data can lead to limited performance of
                                         resistant to performance degradation. Experimental results show                   classifier. However, most DL-based models designed for
                                         that M3S-UPD not only outperforms existing methods on the few-                    ETC are trained in a supervised manner, with an unrealistic
                                         shot encrypted traffic classification task, but also simultaneously               assumption that substantial labeled training data can be
                                         achieves competitive performance on the zero-shot unknown                         obtained at a low cost (in terms of time and manpower).
                                         traffic discovery task.
                                                                                                                           Such scarcity in training dataset popes great difficulties
                                           Index Terms—Encrypted network traffic, multistage self-                         to the actual application of DL-based models for online
                                         supervised learning, unknown pattern discovery                                    encrypted traffic classification.
                                                                                                                        2) Concept Drifting. Learning classifiers from real-world traf-
                                                                   I. I NTRODUCTION                                        fic encounters the change in distribution and characteristics
                                                                                                                           of traffic, whose hidden data contexts and labels may vary
                                            Nowadays, a vast number of network applications that em-                       and become unknown to the model. Such phenomenon is
                                         ploy encrypted traffic for communication continuously emerge,                     known as concept drifting. In online traffic classification,
                                         leading to an increasingly complicated and diverse network                        the fluctuation of traffic labels is a common and challenging
                                         environment. The expanding types of traffic, coupled with                         type of concept drifting. The varying labels of online
                                         the deployment of encryption methods for privacy preserving,                      traffic not only demands the classifier to be updatable, but
                                         pose challenges to network management and censorship. This                        also efficiency in model training and deploying, which is
                                         not only further underscores the critical role of encrypted                       challenging for DL-based models with significant training
                                         traffic classification, but also elevates practical demands on                    costs. Such issues become increasingly pressing with the
                                         its applications.                                                                 continuous growth in the types of network traffic.
                                            From an application-oriented perspective, encrypted traffic                 3) Model Limitations. Existing ETC techniques achieve com-
                                         classification (ETC) can be divided into two sub-tasks:                           mendable performance in specific laboratory settings, yet
                                            • The multi-classification task aimed at identifying various                   still exhibit limitations in a real-world scenario. To address
                                               traffic types. For example, controlling the quality of                      challenges such as data scarcity and concept drifting,
                                               service (QoS) and allocating network resources require                      data augmentation techniques and self-paced learning are
                                               accurate and robust traffic classification.                                 employed to generate pseudo-labels for unlabeled data and
                                            • The detection task focused on discovering unknown traf-                      simulate the distribution of unknown traffic. However, these
                                               fic that has not been observed by the classifier. In prac-                  methods face multiple practical challenges. GAN-based
                                               tical network management scenarios, intrusion detection                     methods leverage the easily-obtained unlabeled traffic data
                                                                                                                           to boost classification performance, but their heavily relies
                                           Yali Yuan, Yu Huang, Xingjian Zeng, Hantao Mei, and Guang Cheng (the            on the selection of hyper-parameters may limit the general
                                         corresponding author) are with the School of Cyber Science and Engineering,
                                         Southeast University, Nanjing 211189, China. (Corresponding author’s e-mail:      application in real-time and ever-changing online network
                                         chengguang@seu.edu.cn).                                                           environments. Models that leverage self-supervised mech-
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                             2



    anism enlarge the labeled training set and detect unknown        are identified as unknown traffic. The model is then updated
    traffic based on model-learning results and sample verifica-     on the expanded dataset and proceeds to the next training step.
    tion, but potentially suffer from low confidence of pseudo          To conclude, this paper mainly contributes in three aspects:
    labels, unreliable verification of samples, and potential           • We propose a novel self-supervised training framework,
    update inaccuracies.                                                   M3S-UPD, for encrypted traffic classification in a limited
   Overall, multi-class traffic classification and unknown traffic         labeled training data scenario, which poses a challenge
detection are comprehensive tasks faced with numerous chal-                for existing DL-based methods. By gradually expanding
lenges stemming from model limitations and intrinsic prop-                 labeled training data with highly confident pseudo-labels
erties of real-world traffic. These challenges require models              of unlabeled traffic, the performance of the initially
to possess strong learning capabilities, efficient updates, and            suboptimal model is incrementally improved.
convenient deployment. Furthermore, though always studied               • We enable the classification model for known traffic
separately by existing approaches, the multi-classification task           categories to detect unknown traffic classes without any
and detection task of online encrypted traffic are strongly                prior knowledge and data augmentation. Through con-
interconnected for the following reasons. First of all, they               sistency analysis of embedding-level spatial distribution
are both classification problems, only with different classify-            and model-level predicted outcomes, samples with dis-
ing outcomes. Second, the superior performance of classifier               crepancies between clustering patterns and classification
for both tasks relies on the comprehensive understanding of                probabilities are accurately and efficiently identified as
training data and the good transferability on acquired knowl-              unknown traffic.
edge, which indicates the similar inherent properties of the            • We conduct comprehensive experiments to evaluate our
two different application-oriented tasks. Finally, in an open-             proposed method on two public experimental datasets.
world online context, traffic continuously flowing towards                 The proposed M3S-UPD demonstrates competitive per-
the classifier inevitably contains unseen categories, which                formance compared to state-of-the-art methods with lim-
indicates a reasonable and feasible application scenario for               ited training data in both closed world and open world
detecting unknown traffic while classifying the known ones.                settings. Furthermore, extensive experiments incorporat-
The inherent correlations of encrypted traffic classification and          ing moderate expert knowledge show that M3S-UPD
unknown traffic discovery imply a possible unified approach                achieves fine-grained traffic classification and effectively
for addressing these two tasks simultaneously.                             adapts to frequently updated datasets, where unknown
   Based on the above considerations, we propose a self-                   traffic classes are continuously identified, labeled, and
supervised training framework for encrypted traffic classifi-              added.
cation and unknown traffic detection under the condition of             The remainder of the paper is structured as follows: Sec-
limited labeled training data in this paper. Starting with a         tion II reviews related literature. Section III defines the prob-
suboptimal classification model trained on limited labeled data,     lem and outlines three key challenges. Section IV introduces
which cannot identify unknown traffic, the proposed training         our self-supervised learning framework for online encrypted
framework aims at incrementally boosting the original model’s        traffic classification and unknown traffic discovery. Section V
performance and gradually achieving accurate unknown traffic         details the results of our evaluation. Section VI offers the
detection via reasonable utilization of unlabeled traffic data.      conclusion of the study.
   Instead of using data augmentation methods to synthesize
unknown traffic samples for training the model, the proposed
                                                                                          II. R ELATED W ORK
framework does not rely on any prior knowledge of unknown
traffic and achieves a unified classification of known/unknown       A. Traffic Classification on Encrypted Traffic
traffic through multiple training steps, each consisting of four        Traffic Classification (TC) pertains to the task of associating
stages. In the model preparing stage, a recently updated             user traffic with the applications, services, and software gen-
classification model is used for generating classification prob-     erating them. This is widely employed for various purposes,
ability distribution and data embeddings for unlabeled traffic.      including quality-of-service (QoS) [1], [2] , network manage-
Subsequently, in the embedding clustering stage, data embed-         ment [3], [4], and intrusion detection and defenses [5]. Over
dings of unlabeled traffic is clustered and divided to distinct      the past decades, numerous TC methods have been proposed,
categories, representing the spatial distribution of unlabeled       such as port-based and deep packet inspection (DPI) methods
traffic in the embedding space. Later, the unlabeled traffic         [6] that utilize default port numbers and application signatures.
data in different clusters are aligned with known classes of         However, these methods have become less effective due to
the training set in the spatial distribution aligning stage,         the proliferation of network address translation (NAT) [7] and
and assigned with corresponding auxiliary labels. Samples            packet encryption [8].
fail to align will be initially classified as potential unknown         Many machine learning methods have been introduced to
traffic. Finally, a consistency-check between classification         build traffic classifiers by extracting implicit patterns. AlSabah
probabilities and aligning outcomes of unlabeled traffic is          et al. [9] extracted features like circuit lifetime, data trans-
conducted for reliable model updates. The training dataset           ferred, cell inter-arrival times, and the number of cells sent
is expanded with unlabeled samples with highly confident             recently. They utilized Naı̈ve Bayes, Bayesian Networks, and
pseudo-labels, while unlabeled traffic samples that fail to align    Decision Trees to classify browser, P2P, and media traf-
and have abnormally low predicted classification probabilities       fic. Cuzzocrea et al. [10] employed Mann-Whitney test and
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                    3



Kolmogorov-Smirnov test to verify the significant difference          further discuss trigger times for model updates in [21] ,
between the distribution of Tor traffic and normal traffic            based on classification output instability, enhancing the update
features. Subsequently, they used machine learning algorithms         framework’s performance. Current model updates often rely
to classify seven Tor traffic types. Montieri et al. [11] extended    on inferring unknown traffic from existing knowledge, facing
Tor traffic classification to the application level. Xu et al. [12]   challenges of initial dataset comprehensiveness and potential
transformed packet sequences into paths for the classification        update inaccuracies.
of multiple encrypted traffic data. Some research utilized KNN
and SVM algorithms to identify websites of traffic, known as          C. Few-Shot Traffic Classification
Website Fingerprinting [13], [14] .
                                                                         Due to the challenge of obtaining abundant encrypted
   In recent years, scholars have introduced deep learning for
                                                                      training data, several studies are dedicated to addressing the
encrypted traffic classification. Liu et al. [15] input the packet
                                                                      sparsity issue in training datasets. Wang et al[24] . assessed
length sequence into a model using encoders, decoders, and
                                                                      the minimum training set needed to achieve high-performance
RNN to extract features and achieve TLS traffic classification.
                                                                      website fingerprinting. Remarkably, their research demon-
Wang et al. [3] conducted fast traffic classification with a
                                                                      strated that a mere 6,800 samples could maintain highly
Temporal Convolutional Network (TCN). Specifically, fast
                                                                      accurate recognition for 100 websites. Sirinam et al[25] .
classification was performed for flows accurately classified
                                                                      introduced Triplet, a method that initially learns traffic dis-
with only the first few packets, while complex flows were
                                                                      tribution knowledge from a substantial amount of non-target
analyzed in detail. Their method enables efficient encrypted
                                                                      traffic. Subsequently, it utilizes a small number of target traffic
traffic classification by extracting the payload length of packets
                                                                      samples to train the target classifier, achieving website identifi-
and constructing a TCN classifier. Zhao et al. [16] considered
                                                                      cation with only 5 samples. Oh et al[26] . leveraged generative
the flow sequence as a graph, constructing the graph structure
                                                                      adversarial networks to generate a substantial amount of ”fake”
with feature vectors including application and time. They then
                                                                      data from a limited set of training samples, aiding in training
extracted features using four residual graph neural network
                                                                      deep neural network classifiers. Zhou et al[27] . proposed
(ResGCN) modules and a 3-layer multilayer perceptron to
                                                                      a website fingerprinting attack method capable of updating
achieve traffic classification. Several research building on deep
                                                                      the classifier with a small number of new samples. This
learning, introduced new mechanisms such as the self-attention
                                                                      approach maps samples to the deep learning feature space,
mechanism, multi-level self-attention, transformer, and en-
                                                                      clusters data samples based on training labels, and aligns the
semble learning mechanism to further improve classification
                                                                      clustering center of new samples with that of training samples,
performance [2], [17], [18], [19] . Although these methods
                                                                      facilitating classifier updates. Hu et al[28] . designed an
have shown high performance on experimental datasets, it’s
                                                                      attribute-based zero-shot encrypted traffic classification frame-
important to note that these models are fixed and cannot
                                                                      work. They used a Temporal Convolutional Network (TCN)-
recognize classes that have not been learned.
                                                                      based feature embedding model and a Simple Recurrent Unit
                                                                      (SRU)-based attribute embedding model to transform traffic
B. Model Update of Traffic Classifiers                                into joint embeddings of attribute values. The framework em-
   To tackle the challenge of model inflexibility, several studies    ploys a Generative Adversarial Network (GAN)-based feature
aim to enhance the model’s ability to generalize, enabling it         generation model for recognizing unknown classes. While
to recognize samples it hasn’t encountered during training.           small sample learning significantly reduces training costs,
Ede et. al., [20] . devised a semi-supervised encrypted traffic       some challenges persist, including reliance on knowledge from
classification system. They clustered traffic of different ap-        the original training set for judgments and learning from
plication types into distinct clusters based on time, device,         newly arrived samples, leading to verification difficulties and
and destination features, constructing an app fingerprint for         potential update inaccuracies.
traffic classification. Being unsupervised, their method can
identify apps not explicitly trained. Fu et al[21] . similarly                           III. P ROBLEM D EFINITION
employed unsupervised learning for identifying unknown traf-             This section defines the problem scenario of traffic
fic. They transformed interaction patterns between long and           multi-class classification and unknown traffic identification
short flows into graph structural features, detecting encrypted       when only limited training data is available. Let D =
malicious traffic by analyzing graph connectivity and sparsity.       {(x1 , y1 ), (x2 , y2 ), . . . , (xn , yn )} be the training dataset that
Lifelong machine learning empowers models to continuously             contains M known traffic classes, i.e., yi ∈ C = {l1 , l2 , .., lM }
accumulate new knowledge, saving classifier training costs            where xi represents the input feature vector corresponding to
and mitigating concept drift. Attarian et al[22] . proposed           training sample in traffic class yi and C is the set of labels for
AdaWFPA, an adaptive online website traffic recognition               known traffic categories. The classifier trained on dataset D
method. Upon the arrival of new training samples, the model           with scarce data potentially suffers from limited performance
predicts, compares with true labels, and updates based on the         on mapping input vector xi to the traffic label yi while lacking
results. Zhang et al[23] . introduced a self-updating model           the ability to identify unknown traffic patterns.
framework that judges unknown class packets based on the                 At time t, suppose the classifier F t has completed its
classifier’s results, compares them with existing knowledge,          training on the previous dataset Dt−1 with known label
and annotates to form a new dataset for updates. The authors          set C t−1 . For the incoming traffic flows N t = K t ∪ U t ,
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                  4



K t represents the set of traffic with known labels and U t            labeled training data with high confidence for model updates,
represents the set of traffic whose labels haven’t appeared in         enabling accurate known traffic classification with facilitating
the known label set C t−1 . The classifier’s task is to predict the    unknown traffic detection after a fixed number of training
specific classes of the traffic samples from K t , i.e., mapping       steps. Accordingly, a training framework consisting of four
the input vectors from K t to certain labels in C t−1 and to find      stages is presented.
any traffic categories that have not appeared in Dt−1 from N t ,          In the first stage, the model trained in the previous step takes
i.e., distinguish the traffic in U t from those in K t .               unlabeled traffic as input to generate classification probabilities
   To move on, the classifier needs to be updated in time for          and data embeddings. Subsequently, these embeddings are
classifying traffic and identifying unknown categories in the          used to generate embedding-space clusters that reflect the spa-
coming traffic flows at t + 1.′ To ′ be specific, a new training       tial distribution of unlabeled traffic. By calculating distances
dataset Dt = {Dt−1 ∪ K t |K t ∈ K t } is required for                  between these embedding clusters and each known class in
updating the classifier F t . If possible, incorporating expert        the training dataset, unlabeled traffic is temporarily aligned
knowledge can further enlarge training dataset by labeling             with a specific known class, receiving corresponding auxiliary
the previously unknown traffic categories and merge them to            labels. Finally, a consistency check is performed between
the known label set C t . In this′ way,′ the ′ training dataset
                                                          ′
                                                                  is   the classification probabilities distribution and the cluster-
expanded as Dt = {Dt−1 ∪ K t ∪ U t |K t ∈ K t , U t ∈ U t }.           level auxiliary labels to ensure reliable model updates. The
   At this point, three subproblems emerge as we wish for the          labeled training data is supplemented with samples whose aux-
classifier to continuously handle online traffic in a sustained,       iliary labels match with the highest classification probabilities.
robust and effective manner:                                           Meanwhile, unlabeled traffic that fails to align and exhibits low
                                                                       classification probabilities is identified as unknown traffic. If
  1) Limited training data. Obtaining substantial training data
                                                                       necessary, these detected unknown traffic can be labeled with
      can be unrealistic due to the challenges of data labeling
                                                                       the assistance of expert knowledge and added to the training
      When only limited training data is available, classifiers
                                                                       set for further fine-grained traffic classification.
      may struggle to effectively manage the continuous in-
      flux of online traffic. Therefore, it is crucial to develop
      strategies for gradually expanding Dt enhance model              A. Model Preparing
      performance.                                                        As we consider a realistic scenario where only limited la-
  2) Detection of unknown traffic. The classifier F t is trained       beled traffic data is available, existing DL-based traffic classifi-
      on dataset Dt−1 with a known traffic label set C t−1 ,           cation methods with intrinsic data-intensive training processes
      making the transfer of this acquired knowledge to un-            become inapplicable. Therefore, based on the self-supervised
      known traffic a considerable challenges. It is essential         learning paradigm, we aim to conduct high-confidence ex-
      to devise methods for recognizing new traffic patterns           pansion of labeled training data for model updates to realize
      by leveraging insights gained from the locally labeled           accurate known traffic classification with further unknown
      training data.                                                   traffic discovery by exploiting sample classification probability
  3) Reliable model updates. Enabling the model to achieve             distribution and data embedding characteristics.
      incremental known traffic classification as well as effec-          In the training pipeline guided by such idea, only a small
      tive unknown traffic detection performance necessitates          amount of labeled data is available at the beginning. We aim
      reliable model updates throughout the training process.          to initially train a weak model then gradually boost its perfor-
      On one hand, ensuring high confidence in newly assigned          mance on known traffic multi-classification and unknown traf-
      labels when utilizing unlabeled traffic to expand the            fic detection. During the training process, the model receives
      labeled dataset poses challenges due to potential biases         data samples with labels as inputs and maps raw features
      from the model’s self-learning. On the other hand, the           to known classes’ classification distribution by minimizing
      lack of prior knowledge about unknown traffic compli-            standard cross-entropy loss:
      cates the effective transfer of knowledge acquired from                                              N
      known traffic data to achieve accurate and low false-                                            1 X           ′
                                                                                            Ls (X) =         H(yi , yi ),               (1)
      positive unknown traffic detection. Additionally, employ-                                        N i=1
      ing data augmentation techniques such as GANs to simu-                            ′
                                                                       where yi and yi respectively refers to the ground-truth label
      late unknown traffic training data results in high training
                                                                       and predicted label of input data sample.
      costs, potentially inaccurate data estimates, and unstable
                                                                          Once finishing loss minimization on labeled training data,
      model performance.
                                                                       the model can generate classification probabilities and data
                                                                       embeddings of given input traffic. Data embeddings are vec-
                          IV. M ETHOD                                  tors generated by transforming the original raw data inputs
   This section provides a detailed introduction to the proposed       into lower-dimensional representations for the model. With
framework (as shown in Fig. 1) designed to address these three         optimized model network parameters, the input traffic data
subproblems. With only scarce labeled data to learn from, a            can be transformed into lower-dimensional embeddings that
classification model with constrained performance is trained,          well capture the inner characteristics of traffic sequences. By
temporarily failing to identify unknown traffic. Leveraging            applying linear transformation on these embeddings, a raw
the self-supervised learning paradigm, we aim to expand the            classification score vector of each class z = [z1 , z2 , . . . , zK ]
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                                      5



                                                                        ① Model Preparing                                      ② Embedding Clustering
  Training traffic                         Trained Model
                                                            Classifying each
                                                           unlabeled traffic                                                  Clustering
    Labeled data
                                                                                 Classification
                                                                               probabilities of               Embeddings of                 Embedding
   Unlabeled data            Extract traffic embeddings                        unlabeled traffic            unlabeled traffic               clusters
               Updating model with
             expanding training set
Classification tasks                               ④ Reliable Model Update                                      ③ Spatial Distribution Aligning
                                                       Consistency                       Alignment result                                  Embedding space
             Class 1                                      check                                                               Known
 Closed ··· ···                                                                                                              classes
 world                                      Known                                       Auxiliary                  Label 1
             Class M                       traffic
                                                                                          labels
                                         EXPERT
                                       KNOWLEDGE                                                                   Label 2             R
             Unknown 1
   Open                                LABELING            +
          ··· ···                         Detected
                                                                                        Potential                   ···       ···                   ···
  world                                                              Unlabeled           unknown
                                          unknown                                                                                      R
             Unknown N                                                traffic            traffic                   Label K
                                          traffic
           Class M+1


                                                       Fig. 1: Overview of the proposed method.


is produced and later normalized with a softmax function to                         number of clusters may result in suboptimal clustering out-
generate final classification probabilities distribution:                           comes that inaccurately describes the spatial distribution of
                                                                                    data. Henceforth, DBSCAN is chosen for clustering traffic data
                      ezi
             σ(z)i = PK                   for i = 1, . . . , K             (2)      embeddings due to its property of automatically determining
                                  zj
                          j=1 e                                                     the number of clusters.
To some extent, the maximum classification probability of
input traffic sample reflects the confidence that it belongs to                     C. Spatial Distribution Aligning
according known class.                                                                 To reliably label unlabeled data in a self-supervised manner
                                                                                    for expanding training dataset, traffic data embeddings are
B. Embedding Clustering                                                             temporarily mapped to a certain known traffic class in the
                                                                                    training set by an aligning mechanism with corresponding
   To tackle with limited training data, clustering technique                       auxiliary labels. For a unlabeled traffic embedding cluster
is utilized for aiding traffic labeling from an embedding                           ui and embeddings of a class in the training dataset km ,
perspective. After generating data embeddings of unlabeled                          the distance between these two data embedding segments is
traffic with trained model, a clustering process is conducted                       computed as:
to divide unlabeled traffic into different cluster categories in
the embedding space, instead of the original input space. Data                                              d(ui , km ) = ||vi − µm ||2 ,                    (3)
embeddings are high-level features generated by a trained
                                                                                    where vi and µm represents the centroids of unlabeled em-
model with a specific architecture and optimized parameters,
                                                                                    bedding cluster ui and labeled data embedding of class m
which are utilized to derive the final predicted probability
                                                                                    respectively.
distribution. Therefore, the spatial distribution of embeddings
                                                                                        By calculating such pair-wise distances between each cluster
obtained by the clustering process is highly related to the
                                                                                    in unlabeled traffic embeddings and each class in labeled traffic
predicted probability distribution of the model, and the two can
                                                                                    embeddings, the auxiliary labels yei of unlabeled traffic data in
be integrated to expand labeled training data while detecting
                                                                                    cluster ui is determined as follows.
unknown traffic with high confidence.                                                      
   Specifically, unlike previous researches that apply K-Means                             P otential unknown           if arg min d(ui , km ) ≥ t
                                                                                                                               m
clustering algorithm, unlabeled traffic data is divided into dif-                    yei =
ferent clusters with regard to density distribution by DBSCAN.                              arg min d(ui , km )                       otherwise,
                                                                                                   m
K-Means algorithm relies on manually selected hyperparam-                                                                                        (4)
eter for specifying the number of clusters, which is difficult                      where t is a distance threshold. Any clusters of unlabeled traf-
to determine based on prior knowledge in the process of real-                       fic data embeddings with a minimum distance from all known
world traffic classification. In real-world traffic classification                  classes exceeding a certain threshold t is considered potential
scenario, expert knowledge can be cooperated to identify                            unknown traffic and will be excluded from alignment with any
and label newly discovered traffic for updating local dataset,                      known class labels in the training dataset. Otherwise, samples
resulting in dynamically varying sample labels of training data.                    within the clusters of unlabeled traffic data embeddings will
Considering fine-grained traffic classification and continuous                      be temporarily assigned the label of the known class that is
model updates, clustering unlabeled traffic into a predefined                       closest to them.
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                               6



D. Reliable Model Update                                              classification confidence, and the top ttop and bottom tbottom
   In the final stage of the training framework, the current          samples, with the highest and lowest confidence, respectively,
model undergoes reliable updates, which consist of incremen-          are selected as candidates for consistency checks. Other unla-
tal improvements in two performance aspects:                          beled samples, with confidence scores falling in the middle of
                                                                      the distribution, are not processed further as they do not exhibit
  • Classification performance on known traffic. Due to the           a clear known/unknown distinction in the model’s predictions,
    limited amount of data used for training, the initial model       and are deferred for checking in the next training iteration.
    exhibits constrained performance in classifying known                The underlying motivation for such consistency checks
    traffic. To address this, the unlabeled traffic in the training   stems from the idea that the model’s prediction confidence to
    data is reliably labeled based on the model’s learning            some extent reflects whether a traffic data sample belongs to a
    outcomes and the distribution patterns of traffic data            known class or not. This is because the model is never trained
    embeddings. These newly labeled samples are then added            with unknown traffic during updates, leading to a lack of
    to the training set to update the model. During the sub-          strong classification ability for unknown traffic. As a result, the
    sequent training process, the classification performance          lower the prediction confidence for an unlabeled sample, the
    of the model will improve incrementally as the labeled            higher the likelihood that it belongs to an unknown class, while
    dataset continues to expand.                                      higher prediction confidence suggests that the sample is likely
  • Detection performance on unknown traffic. Unlike pre-
                                                                      associated with a known class. By incorporating knowledge of
    vious methods that leverage complex and challenging-              the data embedding distribution, bias that may arise from this
    to-train adversarial generative networks to construct un-         self-learning judgment is greatly mitigated by the alignment
    known traffic samples for model training, the detection of        results of the unlabeled traffic data. Furthermore, taking into
    unknown traffic achieved in the proposed framework is             account real-world unknown traffic detection scenarios, the
    an efficient and low-overhead consequence of the model’s          proposed framework allows for the introduction of expert
    reliable updates. Rather than enabling the model to clas-         knowledge to label unknown traffic identified during the train-
    sify unknown traffic by learning from synthetic samples,          ing process. This enables the expansion of the local training set
    the detection capability of the proposed framework arises         with new traffic categories, facilitating continuous fine-grained
    from the consistency check between the model’s learning           model updates to adapt to complex network environments and
    outcomes and the distribution of unlabeled traffic data           the ongoing emergence of new traffic types.
    embeddings.
For a given unlabeled traffic data sample, the model outputs the                    V. E XPERIMENTAL E VALUATION
predicted classification probabilities for each known class. The
highest prediction probability can be considered an estimate of       A. Dataset and Experimental Setup
the model’s prediction confidence. In self-supervised learning           In this section, we conduct extensive experiments to demon-
methods based on self-labeling, assigning labels corresponding        strate the efficacy of our proposed M3S-UPD in traffic
to the highest predicted probabilities to unlabeled samples is        classification. Our experiments utilize the widely recognized
a common approach for expanding the training set. However,            Tor public dataset, ISCXTor2016 [29], curated by Lashkari
such approach potentially suffer from biases in the model’s           and a Tor dataset that we collected ourselves, TDTor. The
self-learning process, leading to newly labeled samples with          ISCXTor dataset comprises over 8000 Tor samples spanning
low confidence, which ultimately results in inaccurate model          8 traffic types: VoIP, P2P, FILE-Transfer, Browsing, Video,
updates and suboptimal performance. Therefore, a consistency          Mail, Audio, and Chat amounting to a total size of 22.8 GB
check between the confidence of unlabeled traffic data and its        with 85 PCAP files. The Tor dataset we collected comprises
corresponding aligning outcomes is introduced for guarantee-          over 12000 Tor samples spanning 7 traffic types. We removed
ing reliable self-labeling.                                           File-Transfer traffic because this type of traffic is not common
   For successfully aligned unlabeled data, a sample will only        in Tor [30]. The distributions of ISCXTor and TDTor are
be added to the training set under the corresponding known            presented in Table I and Table II, respectively. It can be
traffic class if its auxiliary label matches the label assigned       observed that TDTor exhibits a more balanced distribution
by the model to its highest predicted classification probabil-        compared to ISCXTor. The evaluation is conducted under a
ity. While focusing on high-confidence unlabeled samples to           realistic scenario where the attacker has only partial samples
achieve growth in the labeled dataset, efficient identification       from certain categories for model training but needs to identify
of unknown traffic is achieved through the consistency check          samples from all categories, including unknown traffic. The
between low-confidence samples and their alignment results.           original datasets ISCXTor and TDTor were partitioned into
For those samples that fail to align and are considered potential     training, validation, and test sets with a ratio of 6:2:2. To
unknown traffic, if their confidence, represented by the model’s      investigate the effectiveness of our proposed method in various
highest predicted classification probability, falls within the        scenarios of known/unknown attacks detection, we constructed
lowest range of the overall unlabeled data distribution, these        two scenarios with two data settings for both datasets as shown
samples are identified as belonging to the unknown traffic            in Table III.
class.                                                                   • No-Expert: This scenario evaluates the recognition ability
   To improve the efficiency and effectiveness of the con-                  of the model without introducing expert knowledge. In
sistency check, the unlabeled data is sorted by the model’s                 this scenario, all non-known classes are categorized into
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                          7



    unknown classes. In this scenario, initially only 30% of             attacks and a SVM based anomaly detection model
    each known class is selected for model training.                     identifying whether this classification is correct or not.
  • With-Expert: This scenario evaluates the complete recog-          • EVM, as known as Extreme Value Machine, is novel
    nition capability of our proposed model, which continu-              open-set designed classifier that supports variable band-
    ously learns knowledge from new classes by introducing               width incremental learning. This method utilize the EVM
    expert knowledge. In this scenario, initially only 30% of            for intrusion detection and measure the open set recog-
    each known class is selected for model training.                     nition performance of identifying known and unknown
  • Setting1: We select three types as known classes and other           classes.
    types as unknown classes. For the known classes, we               We first demonstrated the classification performance of the
    select 30% of the total samples as training samples. This      above four data settings on the ISCXTor and TDTor dataset
    scenario explores the model’s recognition ability when         in Section V-B to evaluate the effectiveness of our proposed
    only a few known classes are available.                        method for traffic classification, particularly its ability to
  • Setting2: We select five types as known classes and other      handle unknown traffic. Subsequently, in Section V-C, we
    types as unknown classes. For the known classes, we            compare our method with multiple SOTA methods to evaluate
    select 30% of the total samples as training samples. This      its effectiveness. Finally, we conducted ablation experiments
    scenario explores the model’s recognition ability when         in Sections V-D and V-E, discussing the impact of the pro-
    most known classes are available and only a few unknown        portion of pre-knowledge and training samples on recognition
    traffic classes are unavailable.                               performance, as well as the extent to which NDM improves
                                                                   recognition ability in different models.
                Category         Count    Percentage
                Audio             1026        7.1%
                Browsing          2645       18.2%                 B. Performance Evaluation of Our M3S-UPD method
                Chat               485        3.3%
                FILE-Transfer     1663       11.5%
                                                                      We first present the classification results of our proposed
                Mail               497        3.4%                 M3S-UPD method in four experiment setting, in term of
                P2P               2139       14.7%                 normalized confusion matrix. Fig. 2 presents the classification
                Video             1529       10.5%
                VOIP              4524       31.2%
                                                                   results of our method on ISCXTor and TDTor datasets, without
                                                                   the use of expert knowledge. The raws of the confusion
                Total            12808       100%
                                                                   matrix indicate the ground truth flow labels, and the columns
    TABLE I: Category Distribution in ISCXTor Dataset              indicate the predicted labels. The elements on the diagonal
                                                                   of the confusion matrix represent the classification accuracy,
                                                                   while the other elements represent the classification error rate.
                  Category      Count    Percentage                The darker the color on the diagonal line, the better the
                  Audio         1474        5.4%                   classification result. From the diagonal elements in Fig. 2a,
                  Broswer       5000       18.3%                   we can see that our method achieves a high classification
                  Mail          5000       18.3%                   accuracy of no less than 83% for all known classes in the
                  Message       3597       13.1%
                  P2P           5000       18.3%                   absence of expert knowledge on ISCXTor. Also, the classifier
                  Video         2314        8.4%                   recognizes most of the unknown traffic despite the fact that
                  VOIP          5000       18.3%                   it has never learned it. Similarly, as shown in Fig 2b, our
                  Total         27385      100%                    method achieving an accuracy of no less than 90% for all
                                                                   known classes on TDTor. This proves the validity of our
     TABLE II: Category Distribution in TDTor Dataset              spatial distribution alignment process. Although the classifier
                                                                   does not learn any knowledge about the unknown traffic,
   Consequently, we have two scenarios named no Expert             we greatly ensure the high confidence classification results
and with Expert, and four new datasets named by ISCXTor            for the known traffic by evaluating the sample clustering
setting1, ISCXTor setting2, TDTor setting1 and TDTor set-          results and the confidence level of model classification results
ting2. We selected several state-of-the-art (SOTA) methods         during the consistency check process, thus identifying the
as evaluation baselines due to their strong performance in         unknown traffic. Beyond this, we note that when the number
previous work. which are referred as CVAE-EVT [31], Cls-           of known classes increases, the model’s ability to recognize
Anomaly [31] and EVM [32].                                         unknown traffic decreases. This is because the increase in the
   • CVAE-EVT proposes an intelligent intrusion detection          number of known classes increases the model complexity and
      method which can classifying known attacks as well           therefore the difficulty of consistency checking. Nevertheless,
      as inferring unknown ones. It enables high-performance       we achieve high classification accuracy for all known classes.
      hierarchical attacks detection by minimizing the empirical      Fig. 3a shows the performance of our method for setting1
      risk and open-set risk.                                      and setting2 where the number of known classes are 3 and
   • Cls-Anomaly proposes an anomaly detection model               5, and the samples that fail in consistency check are labeled
      which assemble a classification model and an anomaly         by introducing the Expert Knowledge on ISCXTor. As can
      detection model. A random forest-based classification        be observed from the left panel (depicted in blue) that all
      model classifying a flow as benign or one of known           known classes (i.e., those classes with training samples) obtain
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                   8



                                                  TABLE III: Experimental data settings.
                        Setting1 no Expert              Setting 1 no Expert           Setting2 with Expert        Setting 2 with Expert
                     Known           Unknown         Known            Unknown         Known         Unknown       Known          Unknown
                      VOIP           Browsing         VOIP            Browsing      VOIP, Video     Browsing    VOIP, Video      Browsing
      ISCXTor          P2P          Video, Mail        P2P           Video, Mail     P2P, Chat        Mail       P2P, Chat         Mail
                  FILE-Transfer     Audio, Chat   FILE-Transfer     Audio, Chat    FILE-Transfer      Audio    FILE-Transfer      Audio
                     Browser           VoIP          Browser            VoIP          Browser         Video       Browser         Video
       TDTor          Mail           Message          Mail            Message        Mail, P2P        Audio      Mail, P2P        Aduio
                       P2P         Video, Audio        P2P          Video, Audio   VoIP, Message               VoIP, Message



a high-performance classification of no less than 83%. In                 curacy for P2P traffic not falling below 60% in setting1,
different settings, the model always obtains high accuracy for            and exceeding 78% across all categories in setting2. This
VoIP, P2P and File-transfer traffic, no less than 96%. Also,              underscores the significant impact that the order of known
by introducing expert knowledge, the model could recognize                classes has on recognition outcomes. When the classifier is
all unknown classes. We can see that the accuracy of the add              pre-trained on classes that are difficult to recognize, the M3S-
classes is not high although the consistency check process can            UPD is sufficiently capable of identifying unknown classes.
recognize many unknown classes when the number of known                   This highlights the critical role of using known classes to
classes is small on ISCXTor. In setting 1, where only VoIP,               train the classifier. Furthermore, it is noteworthy that P2P
P2P and File-transfer traffic are involved in initial training, the       traffic, which is the most readily recognized as a known
model successfully learns Video, Browsing and Mail traffic,               class (with accuracy exceeding 99%), achieves an accuracy
obtaining accuracy of 97%, 60% and 61%. However, the model                of only 60% and 89% when treated as an unknown class in
seems to easily misclassify Chat as Mail traffic and Audio as             setting1 and setting2, respectively. In contrast, FILE traffic is
Browsing traffic. Things comes different when more classes                consistently recognized with very high accuracy (exceeding
are known. In setting 2, VoIP, P2P, File Transfer, Video and              97%) regardless of its status as a known or unknown class.
Chat traffic are involved in the training of the initial model.           This suggests that FILE traffic is distinctly separable from
During the model iteration, M3S-UPD successfully discovers                other traffic types, rendering it easily recognizable as an
the remaining Browsing, Mail and Audio traffic and by in-                 unknown class and readily learnable.
troducing expert knowledge, M3S-UPD correctly labels these                   Fig 4 illustrates the performance of our method on TDTor
traffic and updates the original model with accuracy of 70%,              under the two settings, with expert knowledge incorporated. It
69% and 47%, which is a substantial improvement compared                  can be observed that our method consistently maintains a high
to setting 1 for all unknown categories. This demonstrates                accuracy, with the accuracy for all known classes being no
the effectiveness of our proposed M3S-UPD approach for                    less than 97% and for all unknown classes no less than 80%.
unknown traffic discovery and new class learning. Also, we                This contrasts with the situation in ISCXTor, where even when
note that the model in setting 2 hardly misclassifies Chat traffic        the model has not learned information about easily confusable
as Mail traffic due to the knowledge of Chat traffic learned              classes, our method still performs well in distinguishing them
during initial training. At the same time, the results of this            when expert knowledge is incorporated. This can be attributed
experiment to some extent indicate that the initial model has             to the more balanced class distribution in TDTor compared
different recognition abilities for different traffic flows, and if       to ISCXTor, which suggests that, under a balanced class
it can learn traffic flows of easily confusing classes during the         distribution, our model is capable of accurately identifying
initial training, the M3S-UPD will significantly improve the              each class, even those that are inherently prone to confusion.
recognition ability in the subsequent updates.

   In the experiments detailed within the blue confusion ma-              C. Performance comparisons with state-of-art benchmarks
trices, we consistently selected the class with the largest                  To showcase the advanced capabilities of our proposed
sample size as the known classes. This approach operates                  method, we conducted a comparative analysis against a range
under the assumption that unknown classes are invariably                  of state-of-the-art techniques. Given that these techniques lack
minority classes. Under this known class configuration, our               consistency checking and the integration of expert knowledge
methodology demonstrated high accuracy for known classes                  processes, we focused solely on their ability to recognize un-
but exhibited poor recognition performance for individual                 known traffic. Table IV and Table V present the classification
unknown classes. It is important to note that the difficulty of           results for the ISCXTor and TDTor datasets under Setting
recognizing different classes in the original dataset varies, with        1 and Setting 2, respectively, excluding the introduction of
some classes being inherently more challenging to identify.               expert knowledge. Our proposed method surpasses the other
To mitigate the influence of the known class configuration                benchmarks in terms of accuracy, precision, recall, and false
on recognition outcomes, we redefined the known classes                   positive rate (FPR), achieving an accuracy of 94.69% in ISCX-
by designating those that are more challenging to recognize               Tor Setting 1, 84.56% in ISCXTor Setting 2, 94.28% in TDTor
as the known classes. The right side (depicted in orange)                 Setting 1, and 91.49% in TDTor Setting 2, underscoring its
of Fig 3b illustrates the recognition outcomes following the              efficacy in distinguishing between known and unknown traffic.
reclassification of known classes. The results indicate a marked          EVM outperforms the other baselines in Setting 1, achieving
improvement in classification accuracy, with the lowest ac-               a maximum accuracy of 81.87% on ISCXTor and 72.41% on
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                                                                               9




                                                 VOIP 0.97               0.01 0.02                                                           BROWSER 0.97                                0.03
     VOIP     0.96                   0.04                                                       BROWSER     0.96                     0.04
                                                                                          0.8                                                                                                     0.8
                                                  P2P        0.97        0.01                                                                      MAIL        0.93 0.01            0.01 0.05
      P2P             0.92           0.08        FILE               0.97 0.02             0.6      MAIL              0.93    0.01    0.06          P2P                0.96               0.04     0.6



                                                VIDEO        0.08        0.83 0.05 0.04                                                            VOIP 0.01                 0.96        0.03
     FILE                    0.91    0.09                                                 0.4
                                                                                                    P2P                      0.93    0.07                                                         0.4


                                                CHAT 0.02           0.04 0.05 0.83 0.06                                                      MESSAGE           0.01                 0.90 0.09
                                                                                          0.2                                                                                                     0.2
 UNKNOWN              0.03   0.01    0.96    UNKNOWN 0.02           0.05 0.13 0.19 0.61
                                                                                                UNKNOWN     0.02     0.01    0.02    0.95    UNKNOWN 0.03                    0.25        0.72
                IP


                      P


                              E



                                        N




                                                       IP
                                                                   P
                                                                   E
                                                                EO

                                                         UN T

                                                                  N




                                                                                                                 R

                                                                                                                     IL


                                                                                                                             P



                                                                                                                                        N




                                                                                                                                                            MA R
                                                                                                                                                               IL
                                                                                                                                                                P
                                                                                                                                                               IP

                                                                                                                                                      UN AGE

                                                                                                                                                                N
                                                                 A
                     P2




                                                               P2




                                                                                                                            P2




                                                                                                                                                             P2
                             FIL




                                                               FIL




                                                                                                              SE




                                                                                                                                                             SE
                                     OW




                                                              OW




                                                                                                                                     OW




                                                                                                                                                           OW
                                                                                                                     MA
             VO




                                                    VO




                                                                                                                                                            VO
                                                             CH
                                                            VID




                                                                                                           OW




                                                                                                                                                        OW




                                                                                                                                                          SS
                                    KN




                                                           KN




                                                                                                                                    KN




                                                                                                                                                        KN
                                                                                                                                                       ME
                                                                                                          BR




                                                                                                                                                     BR
                                    UN




                                                                                                                                    UN
                                    (a) ISCXTor                                                                                      (b) TDTor
                                            Fig. 2: Confusion matrix in setting1 and setting2 without expert.




                       (a) Most classes as known classes                                                  (b) The hardest class to recognize as a known classes
            Fig. 3: Confusion matrix for ICSXTor dataset in setting1 and setting2 with expert for different known classes.



 BROWSER 0.99                                                                         0.01 BROWSER 0.99                                                                  0.01

            MAIL              0.97 0.01                       0.02                                    MAIL                  0.97 0.01               0.02                                        0.8


             P2P                         0.99                 0.01                                         P2P              0.01 0.99
                                                                                                                                                                                                0.6

            VOIP 0.02                            0.92                      0.03 0.02                  VOIP 0.01                     0.01 0.94                  0.03 0.02
                                                                                                                                                                                                0.4
  MESSAGE                     0.02                            0.98                              MESSAGE                     0.01 0.01               0.98

      VIDEO 0.02                                 0.09                      0.81 0.08                VIDEO 0.02                              0.10               0.82 0.07                        0.2

      AUDIO 0.05                                 0.03                      0.10 0.82                AUDIO 0.05                              0.03               0.12 0.80
                          R




                                                         VID E




                                                                                                                       VIDGE
                         IL
                          P
                         IP


                                                             EO
                                                            DIO




                                                                                                                         MAER
                                                                                                                            IL
                                                                                                                             P
                                                                                                                     ME IP


                                                                                                                       AU O
                                                                                                                          DIO
                       P2




                                                                                                                          P2
                                                            AG
                       SE




                                                                                                                           E
                      MA


                      VO




                                                                                                                         VO
                                                                                                                          S




                                                                                                                          A
                                                         AU
                     OW




                                                                                                               OW
                                                         SS




                                                                                                                       SS
                                                        ME
               BR




                                                                                                            BR




                                     Fig. 4: Confusion matrix for TDTor in setting1 and setting2 with expert


TDTor, due to its ability to efficiently learn class boundaries                                 a pronounced decrease in performance in Setting 2 compared
with fewer known categories. Its use of Extreme Value Theory                                    to the CVAE-EVT and Cls-Anomaly methods, while EVM
(EVT) allows it to accurately identify known classes and                                        also performs worse overall than both in Setting 2. This
reject unknown ones, enhancing classification performance in                                    discrepancy may be attributed to the CVAE-EVT and Cls-
a setting with fewer classes. Notably, our method experiences                                   Anomaly utilize a two-stage hierarchical detection framework
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                        10



designed to enhance overall recognition performance by min-          class, M3S-UPD attains an accuracy of approximately 83.29%.
imizing the false alarm rate of benign traffic, which is more        Similarly, in Fig 7, when utilizing a single known class,
effective in Setting 2 where there are more known categories         M3S-UPD achieves an accuracy of 98.13%, when employing
and a larger sample size, thereby enhancing overall accuracy.        six known classes, the accuracy is 90.54%. As the number
Nonetheless, it is noteworthy that our method demonstrates           of known classes increases, the accuracy decreases because
superior recognition of unknown traffic compared to all other        more known classes result in more classification tasks and
methods.                                                             decision boundaries. This increased complexity makes it more
   To further investigate the traffic classification capabilities    challenging for the model to distinguish between categories.
of our method compared to these state-of-the-art techniques          However, as the number of known classes increases, the
across various scenarios, we present in Fig 5 the classification     accuracy of our method does not significantly decrease, this
performance of these methods with varying proportions of             demonstrates M3S-UPD’s capability to accurately recognize
training samples from known classes in different settings            known classes.
across two datasets. Our findings reveal that the proposed              In the ”With Expert Knowledge” scenario depicted in Fig 6,
M3S-UPD method consistently outperforms the other methods            M3S-UPD achieves an accuracy of 71.43% on the ICSXTor,
in both accuracy and precision of unknown traffic as the             necessitating 47.24% of expert knowledge when the number of
proportion of known samples increases. In all four figures, it is    known classes is one. When employing seven known classes,
evident that our method consistently achieves superior classi-       M3S-UPD registers an accuracy of 87.93%, with only 8.58%
fication performance compared to CVAE-EVT, Cls-Anomaly,              of expert knowledge required for the unclassified categories.
and EVM when utilizing more than 10% of the known sample             As shown in Fig 7, M3S-UPD demonstrates similar perfor-
proportion. This outcome substantiates the effectiveness of our      mance on the TDTor dataset, achieving an accuracy of 63.65%
method in identifying unknown traffic.                               when the number of known classes is one, requiring 40.14% of
   Moreover, classifier performance exhibits a gradual im-           expert knowledge. When the number of known classes is six,
provement as the proportion of known samples increases. This         the accuracy increases to 95.52%, with only 23.82% of expert
trend can be attributed to the fact that a higher proportion         knowledge needed. This demonstrates M3S-UPD’s proficiency
of known samples enables the initial classifier to acquire           in seamlessly integrating expert knowledge while simultane-
more comprehensive knowledge of the samples. Additionally,           ously acquiring profound insights across various categories,
we observe that in Figures 5a and 5c, 30% of the training            ultimately leading to the accurate classification of samples.
samples suffice for the classifier to attain stable classification   An upward trajectory in accuracy and precision is observed
performance. Conversely, in Figures 5b and 5d, 50% of the            alongside a reduction in the need for expert knowledge as the
training samples are necessary for the classifier’s performance      number of known categories increases. This phenomenon can
to approach its maximum potential. This observation suggests         be attributed to the model’s adeptness in assimilating traffic
that when there are more original training categories, a greater     knowledge from the identified categories. Notably, when three
number of initial samples is required for the original classifier    known categories are used for initial model training, M3S-
to acquire sufficient classification knowledge.                      UPD achieves an accuracy of 81.97% on ICSXTor, with the
                                                                     proportion of expert knowledge required decreasing from over
                                                                     47% to 33%. Similarly, on the TDTor, M3S-UPD achieves an
D. Classification Performance with Different Number and              accuracy of 94.72%, with the proportion of expert knowledge
proportion of Known Classes                                          decreasing from 40.14% to 29.62%. Subsequently, a marginal
    The experiment conducted has highlighted the efficacy of         decline in the necessity for expert knowledge is observed as
our methodology in discerning unidentified network traffic           the number of known categories increases. This suggests that a
even with a limited knowledge base. To evaluate how the              minimum of three known categories is required for M3S-UPD
volume of pre-existing knowledge influences the performance          to effectively harvest traffic knowledge from the identified
of our method, we examined the effects of varying the number         categories.
of known and unknown classes used for training on the                   We aimed to evaluate the impact of the number of samples
identification results.                                              used in training the initial model on the final classification
    Fig 6 illustrates the identification outcomes, including met-    performance of the classifier. Fig 8a and Fig 8b illustrates
rics such as Accuracy, False Positive Rate (FPR), and the pro-       the accuracy and False Positive Rate (FPR) as the proportion
portion of expert knowledge introduced, across different quan-       of samples from the initial known classes is increased across
tities of known class types, while maintaining a constant train-     different settings for ISCXTor and TDTor, respectively. It is
ing set size of 30% within our comprehensive framework. Sim-         evident that accuracy gradually improves with an increase in
ilarly, Fig 7 shows the corresponding identification outcomes        training samples across various settings. Without the intro-
on TDTor under the same conditions. A notable increase in            duction of expert knowledge, the accuracy of Setting 1 and
the accuracy of the Network Discovery Method (M3S-UPD)               Setting 2 rises from 85.28% to 97.24% and from 78.63%
is observed as the number of known classes increases. In             to 94.38%, respectively, as the percentage of known samples
the ”Without Expert Knowledge” scenario depicted in Fig 6,           increases from 10% to 90%. Similarly, on the TDTor dataset,
when utilizing a single known class, M3S-UPD achieves an             the accuracy of Setting 1 increases from 94.49% to 96.20%,
accuracy of 95.99%. In contrast, when employing seven known          and the accuracy of Setting 2 rises from 85.9% to 95.49% as
classes, thereby reducing the scenario to a single unknown           the percentage of known samples increases from 10% to 90%.
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                                                                                                                                                                                                                                  11




                    Fig. 5: Classification Results of different methods when varying the proportion of known classes in different settings.
                                                                                                                & 9 $ (  ( 9 7                                   & O V  $ Q R P D O \                                    ( 9 0                          2 X U  0 H W K R G
                       

                       
 $ F F X U D F \




                                                                                                    3 U H F L V L R Q
                       




                                                                                                                                                                                              5 H F D O O




                                                                                                                                                                                                                                                                                  ) 3 5
                       

                       

                        
                                                                                                                                                                                                                                                                                                
                                        . Q R Z Q  V D P S O H  S U R S R U W L R Q V                                           . Q R Z Q  V D P S O H  S U R S R U W L R Q V                                     . Q R Z Q  V D P S O H  S U R S R U W L R Q V                               . Q R Z Q  V D P S O H  S U R S R U W L R Q V
                                                                                                                                                               (a) ISCXTor setting1

                                                                                                                & 9 $ (  ( 9 7                                   & O V  $ Q R P D O \                                    ( 9 0                          2 X U  0 H W K R G
                       

                       
 $ F F X U D F \




                                                                                                    3 U H F L V L R Q




                       
                                                                                                                                                                                              5 H F D O O




                                                                                                                                                                                                                                                                                  ) 3 5
                       

                       

                        
                                                                                                                                                                                                                                                                                                
                                        . Q R Z Q  V D P S O H  S U R S R U W L R Q V                                           . Q R Z Q  V D P S O H  S U R S R U W L R Q V                                     . Q R Z Q  V D P S O H  S U R S R U W L R Q V                               . Q R Z Q  V D P S O H  S U R S R U W L R Q V
                                                                                                                                                               (b) ISCXTor setting2

                                                                                                                & 9 $ (  ( 9 7                                   & O V  $ Q R P D O \                                    ( 9 0                          2 X U  0 H W K R G
                       

                       
 $ F F X U D F \




                                                                                                    3 U H F L V L R Q




                       
                                                                                                                                                                                              5 H F D O O




                                                                                                                                                                                                                                                                                  ) 3 5


                       

                       

                        
                                                                                                                                                                                                                                                                                                
                                        . Q R Z Q  V D P S O H  S U R S R U W L R Q V                                           . Q R Z Q  V D P S O H  S U R S R U W L R Q V                                     . Q R Z Q  V D P S O H  S U R S R U W L R Q V                               . Q R Z Q  V D P S O H  S U R S R U W L R Q V
                                                                                                                                                                  (c) TDTor setting1

                                                                                                                & 9 $ (  ( 9 7                                   & O V  $ Q R P D O \                                    ( 9 0                          2 X U  0 H W K R G
                       

                       
 $ F F X U D F \




                                                                                                    3 U H F L V L R Q




                       
                                                                                                                                                                                              5 H F D O O




                                                                                                                                                                                                                                                                                  ) 3 5




                       

                       

                        
                                                                                                                                                                                                                                                                                                
                                        . Q R Z Q  V D P S O H  S U R S R U W L R Q V                                           . Q R Z Q  V D P S O H  S U R S R U W L R Q V                                     . Q R Z Q  V D P S O H  S U R S R U W L R Q V                               . Q R Z Q  V D P S O H  S U R S R U W L R Q V
                                                                                                                                                                  (d) TDTor setting2
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                                                                                                        12



                                                                      TABLE IV: Comparison of different methods for different setting on ISCXTor.
                                                                                                                    setting1 no expert                                                setting2 no expert
                                                                                                accuracy            precision     recall                           FPR     accuracy   precision     recall    FPR
                                                             CVAE-EVT                            0.7381              0.7030      0.5665                           0.1009    0.7650     0.6365      0.6079    0.0512
                                                             Cls-Anomaly                         0.7991              0.7790      0.8256                           0.0645    0.7791     0.6878      0.6443    0.0476
                                                                 EVM                             0.8187              0.8145      0.8046                           0.0673    0.7733     0.7064      0.7710    0.0432
                                                             Our Method                          0.9469              0.9480      0.9365                           0.0204    0.8456     0.7812      0.8619    0.0289

                                                                           TABLE V: Comparison of different methods for different setting on TDTor.
                                                                                                                    setting1 no expert                                                setting2 no expert
                                                                                                accuracy            precision     recall                           FPR     accuracy   precision     recall    FPR
                                                             CVAE-EVT                            0.6903              0.7152      0.7416                           0.1100    0.8187     0.7009      0.7901    0.0367
                                                             Cls-Anomaly                         0.7175              0.7475      0.7912                           0.0961    0.8008     0.8119      0.7842    0.0395
                                                                 EVM                             0.7241              0.7794      0.6697                           0.1158    0.7442     0.6951      0.7211    0.0517
                                                             Our Method                          0.9428              0.9471      0.9409                           0.0222    0.9149     0.9146      0.9067    0.0169



                   
                                     : L W K R X W  N Q R Z O H G J H                                     : L W K  N Q R Z O H G J H                             E. Classification Performance with Different Number of Un-
                                                                                                                                                                   known Classes
                                                                                                                                                                   We sought to assess the impact of varying numbers of
                                                                                                                                           $ F F X U D F \      unknown classes on categorization. Fig 9 displays the accuracy
 0 H W U L F




                                                                              $ F F X U D F \
                                                                                                                                              ) 3 5                and False Positive Rate (FPR) as the number of unknown
                                                                              ) 3 5
                                                                                                                                           N Q R Z O H G J H
                                                                                                                                                                   classes changes across different settings for two datasets.
                                                                                                                                                                To ensure the effectiveness of the initial training, we use 3
                                                                                                                                                                   known classes for both datasets and 30% known samples for
                                                                                                                                                                 each known class to train the initial classifiers. It is evident
                                                                                                                                             
                                1 X P E H U  R I  N Q R Z Q  F O D V V H V                      1 X P E H U  R I  N Q R Z Q  F O D V V H V                   that with a fixed number of known classes, increasing the
                                                                                                                                                                   number of unknown classes results in a gradual decline in
Fig. 6: Accuracy, FPR and proportion of expert knowledge of                                                                                                        overall accuracy. This phenomenon occurs in both datasets.
varying number of known classes on ISCXTor.                                                                                                                        For ISCXTor dataset, when the number of known classes is
                                                                                                                                                                   three, and no expert knowledge is introduced, increasing the
                                                                                                                                                                   number of unknown classes from 1 to 5 leads to a slight
                   
                                     : L W K R X W  N Q R Z O H G J H                                     : L W K  N Q R Z O H G J H
                                                                                                                                                                   decrease in accuracy from 95.99% to 94.69%. In contrast,
                   
                                                                                                                                                                   when expert knowledge is incorporated, the accuracy decreases
                                                                                                                                                                   from 97.51% to 81.97%, indicating a noticeable drop. For
                                                                                                                                           $ F F X U D F \      TDTor dataset, the accuracy decrease from 96% to 94.28%
 0 H W U L F




                                                                                                                                              ) 3 5
                                                                                                                                              N Q R Z O H G J H    and 99.35% to 94.72%, separately. We observe that even
                   
                                                                                                                                                                   with an increase in the number of unknown classes, there
                                  $ F F X U D F \                                                                                                               is only a slight decrease in overall recognition accuracy.
                                     ) 3 5                                                                                                                         This phenomenon likely results from the enriched knowledge
                    
                                                                                                                                                       base to which the initial model is exposed, allowing for
                                1 X P E H U  R I  N Q R Z Q  F O D V V H V                      1 X P E H U  R I  N Q R Z Q  F O D V V H V                   more precise judgments on unknown categories. When expert
Fig. 7: Accuracy, FPR and proportion of expert knowledge of                                                                                                        knowledge is introduced to achieve fine-grained classification,
varying number of known classes on TDTor.                                                                                                                          the increase in the number of unknown classes results in a
                                                                                                                                                                   slightly more pronounced decrease in accuracy due to the
                                                                                                                                                                   heightened recognition granularity. This underscores M3S-
                                                                                                                                                                   UPD’s ability to effectively integrate expert knowledge in
With the inclusion of expert knowledge, the accuracies for                                                                                                         identifying unknown network traffic, with the precision of the
Setting 1 and Setting 2 are 81.97% and 86.73%, respectively,                                                                                                       initial training data being a crucial determinant of the quality
when using a 30% proportion of known samples. On the                                                                                                               of the final identification outcomes.
TDTor dataset, the accuracies for Setting 1 and Setting 2
are 94.69% and 94.98%, respectively, when using a 10%
                                                                                                                                                                                           VI. C ONCLUSION
proportion of known samples. Beyond this point, increasing
the proportion of training samples does not lead to a significant                                                                                                     This paper presents M3S-UPD, a novel self-supervised
improvement in accuracy. This indicates that our proposed                                                                                                          training framework designed to address the challenges of
M3S-UPD method can effectively extract knowledge from                                                                                                              encrypted traffic classification and unknown traffic detection
existing samples and accurately identify unknown classes.                                                                                                          under limited labeled data conditions. By leveraging unlabeled
Additionally, by incorporating expert knowledge, our method                                                                                                        traffic data through iterative model refinement, our framework
can label uncertain samples, thereby achieving stable traffic                                                                                                      incrementally improves classification performance while si-
classification.                                                                                                                                                    multaneously identifying unknown traffic without relying on
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                                                                                                                                                                                         13




                                                           Fig. 8: Accuracy and FPR of varying proportion of known classes in different settings.
                                                                                                                                                  $ F F X U D F \                      ) 3 5
                       
                                      V H W W L Q J   : L W K R X W  N Q R Z O H G J H                 V H W W L Q J   : L W K R X W  N Q R Z O H G J H                        V H W W L Q J   : L W K  N Q R Z O H G J H                       V H W W L Q J   : L W K  N Q R Z O H G J H

                       

                       
 0 H W U L F  




                       

                       

                        
                                                                                                                                                                                                
                                     3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V               3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V                   3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V               3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V
                                                                                                                                                    (a) ISCXTor

                                                                                                                                                  $ F F X U D F \                      ) 3 5
                       
                                      V H W W L Q J   : L W K R X W  N Q R Z O H G J H                 V H W W L Q J   : L W K R X W  N Q R Z O H G J H                        V H W W L Q J   : L W K  N Q R Z O H G J H                       V H W W L Q J   : L W K  N Q R Z O H G J H

                       

                       
 0 H W U L F  




                       

                       

                        
                                                                                                                                                                                                
                                     3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V               3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V                   3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V               3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V
                                                                                                                                                      (b) TDTor




                                                         Fig. 9: Accuracy and FPR of varying the number of unknown classes for different settings.
                                                                                                                                                   $ F F X U D F \                    ) 3 5
                       
                                       V H W W L Q J   : L W K R X W  N Q R Z O H G J H                 V H W W L Q J   : L W K R X W  N Q R Z O H G J H                       V H W W L Q J   : L W K  N Q R Z O H G J H                       V H W W L Q J   : L W K  N Q R Z O H G J H

                       

                       
 0 H W U L F  




                       

                       

                        
                                                                                                                                                                                                                                                                                               
                                     3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V               3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V                   3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V               3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V
                                                                                                                                                    (a) ISCXTor

                                                                                                                                                   $ F F X U D F \                    ) 3 5
                       
                                       V H W W L Q J   : L W K R X W  N Q R Z O H G J H                 V H W W L Q J   : L W K R X W  N Q R Z O H G J H                       V H W W L Q J   : L W K  N Q R Z O H G J H                       V H W W L Q J   : L W K  N Q R Z O H G J H

                       

                       
 0 H W U L F  




                       

                       

                        
                                                                                                                                                                                                                                                                                                   
                                     3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V               3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V                   3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V               3 U R S R U W L R Q  R I  N Q R Z Q  V D P S O H V
                                                                                                                                                      (b) TDTor
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                                    14



prior knowledge or synthetic data augmentation. The key inno-                   [10] A. Cuzzocrea, F. Martinelli, F. Mercaldo, and G. V. Vercelli, “Tor traffic
vation lies in the integration of embedding clustering, spatial                      analysis and detection via machine learning techniques,” 2017 IEEE
                                                                                     International Conference on Big Data (Big Data), pp. 4474–4480, 2017.
distribution alignment, and consistency-based pseudo-labeling,                  [11] A. Montieri, D. Ciuonzo, G. Aceto, and A. Pescapé, “Anonymity
which enables the model to distinguish between known and                             services tor, i2p, jondonym: Classifying in the dark (web),” IEEE
unknown traffic categories effectively. Experimental results                         Transactions on Dependable and Secure Computing, vol. 17, no. 3, pp.
                                                                                     662–675, 2020.
on public datasets demonstrate that M3S-UPD achieves com-                       [12] S. Xu, G. Geng, X. Jin, D. Liu, and J. Weng, “Seeing traffic paths:
petitive performance compared to state-of-the-art methods in                         Encrypted traffic classification with path signature features,” IEEE Trans.
both closed-world and open-world scenarios. The framework’s                          Inf. Forensics Secur., vol. 17, pp. 2166–2181, 2022.
                                                                                [13] A. Panchenko, F. Lanze, J. Pennekamp, T. Engel, A. Zinnen, M. Henze,
ability to adapt to concept drifting and continuously update                         and K. Wehrle, “Website fingerprinting at internet scale,” in 23rd Annual
its knowledge base makes it particularly suitable for real-                          Network and Distributed System Security Symposium, NDSS 2016, San
world network environments where traffic patterns evolve                             Diego, California, USA, February 21-24, 2016. The Internet Society,
                                                                                     2016.
dynamically. The success of M3S-UPD highlights several
                                                                                [14] G. Cherubin, R. Jansen, and C. Troncoso, “Online website fingerprinting:
important directions for future research in encrypted traffic                        Evaluating website fingerprinting attacks on tor in the real world,” in
analysis. Firstly, the potential integration of more advanced                        USENIX Security Symposium, 2022.
clustering techniques could enhance the framework’s ability to                  [15] C. Liu, L. He, G. Xiong, Z. Cao, and Z. Li, “Fs-net: A flow sequence
                                                                                     network for encrypted traffic classification,” in 2019 IEEE Conference
discern subtle differences between traffic categories. Besides,                      on Computer Communications, INFOCOM 2019, Paris, France, April
the development of more efficient model update mechanisms                            29 - May 2, 2019. IEEE, 2019, pp. 1171–1179.
could further reduce the computational overhead associated                      [16] R. Zhao, X. Deng, Y. Wang, L. Chen, M. Liu, Z. Xue, and
                                                                                     Y. Wang, “Flow sequence-based anonymity network traffic identification
with continuous learning in real-time network environments.                          with residual graph convolutional networks,” 2022 IEEE/ACM 30th
                                                                                     International Symposium on Quality of Service (IWQoS), pp. 1–
                                                                                     10, 2022. [Online]. Available: https://api.semanticscholar.org/CorpusID:
                         ACKNOWLEDGMENT                                              250317945
  This work was supported in part by the National Key                           [17] R. Zhao, M. Zhan, X. Deng, Y. Wang, Y. Wang, G. Gui, and
                                                                                     Z. Xue, “Yet another traffic classifier: A masked autoencoder
Research and Development Program of China (Grant No.                                 based traffic transformer with multi-level flow representation,” in
2023YFB3106700) under the Young Scientists Program, in                               AAAI Conference on Artificial Intelligence, 2023. [Online]. Available:
part by Natural Science Foundation of Jiangsu Province (Grant                        https://api.semanticscholar.org/CorpusID:259716837
                                                                                [18] X. Deng, Q. Yin, Z. Liu, X. Zhao, Q. Li, M. Xu, K. Xu, and
No. SBK2023041256), and in part by the National Natural                              J. Wu, “Robust multi-tab website fingerprinting attacks in the wild,”
Science Foundation of China (Grant No. 62302097).                                    2023 IEEE Symposium on Security and Privacy (SP), pp. 1005–1022,
                                                                                     2023. [Online]. Available: https://api.semanticscholar.org/CorpusID:
                                                                                     260002990
                             R EFERENCES                                        [19] Y. Wang, H. Xu, Z. Guo, Z. Qin, and K. Ren, “snwf: Website fingerprint-
 [1] D. Barradas, N. Santos, L. Rodrigues, S. Signorello, F. M. V. Ramos,            ing attack by ensembling the snapshot of deep learning,” IEEE Trans.
     and A. Madeira, “Flowlens: Enabling efficient flow classification for           Inf. Forensics Secur., vol. 17, pp. 1214–1226, 2022.
     ml-based network security applications,” Proceedings 2021 Network          [20] T. van Ede, R. Bortolameotti, A. Continella, J. Ren, D. J. Dubois,
     and Distributed System Security Symposium, 2021. [Online]. Available:           M. Lindorfer, D. R. Choffnes, M. van Steen, and A. Peter, “Flowprint:
     https://api.semanticscholar.org/CorpusID:231590874                              Semi-supervised mobile-app fingerprinting on encrypted network
 [2] X. chun Yun, Y. Wang, Y. Zhang, C. Zhao, and Z. Zhao, “Encrypted                traffic,” Proceedings 2020 Network and Distributed System Security
     tls traffic classification on cloud platforms,” IEEE/ACM Transactions           Symposium, 2020. [Online]. Available: https://api.semanticscholar.org/
     on Networking, vol. 31, pp. 164–177, 2023. [Online]. Available:                 CorpusID:211265114
     https://api.semanticscholar.org/CorpusID:250705780                         [21] C. Fu, Q. Li, and K. Xu, “Detecting unknown encrypted malicious
 [3] Y. Wang, H. S. He, Y. K. Lai, and A. X. Liu, “A two-phase approach              traffic in real time via flow interaction graph analysis,” ArXiv, vol.
     to fast and accurate classification of encrypted traffic,” IEEE/ACM             abs/2301.13686, 2023. [Online]. Available: https://api.semanticscholar.
     Transactions on Networking, vol. 31, pp. 1071–1086, 2023.                       org/CorpusID:256415981
 [4] J. Li, S. Wu, H. Zhou, X. Luo, T. Wang, Y. Liu, and X. Ma, “Packet-level   [22] R. Attarian, L. Abdi, and S. Hashemi, “Adawfpa: Adaptive online
     open-world app fingerprinting on wireless traffic,” Proceedings 2022            website fingerprinting attack for tor anonymous network: A stream-wise
     Network and Distributed System Security Symposium, 2022. [Online].              paradigm,” Comput. Commun., vol. 148, pp. 74–85, 2019. [Online].
     Available: https://api.semanticscholar.org/CorpusID:248224842                   Available: https://api.semanticscholar.org/CorpusID:203704356
 [5] C. Fu, Q. Li, M. Shen, and K. Xu, “Frequency domain feature                [23] J. Zhang, F. Li, F. Ye, and H. Wu, “Autonomous unknown-
     based robust malicious traffic detection,” IEEE/ACM Transactions                application filtering and labeling for dl-based traffic classifier
     on Networking, vol. 31, pp. 452–467, 2023. [Online]. Available:                 update,” IEEE INFOCOM 2020 - IEEE Conference on Computer
     https://api.semanticscholar.org/CorpusID:251459863                              Communications, pp. 397–405, 2020. [Online]. Available: https:
 [6] X. Bai, Y. Zhang, and X. Niu, “Traffic identification of tor and                //api.semanticscholar.org/CorpusID:211132760
     web-mix,” 2008 Eighth International Conference on Intelligent Systems      [24] T. Wang and I. Goldberg, “On realistically attacking tor with website
     Design and Applications, vol. 1, pp. 548–551, 2008. [Online]. Available:        fingerprinting,” Proceedings on Privacy Enhancing Technologies, vol.
     https://api.semanticscholar.org/CorpusID:11519694                               2016, pp. 21 – 36, 2016. [Online]. Available: https://api.semanticscholar.
 [7] D. C. Sicker, P. Ohm, and D. Grunwald, “Legal issues                            org/CorpusID:26413501
     surrounding monitoring during network research,” in ACM/SIGCOMM            [25] P. Sirinam, N. Mathews, M. S. Rahman, and M. Wright, “Triplet
     Internet Measurement Conference, 2007. [Online]. Available:                     fingerprinting: More practical and portable website fingerprinting with
     https://api.semanticscholar.org/CorpusID:17998633                               n-shot learning,” in Proceedings of the 2019 ACM SIGSAC Conference
 [8] M. Finsterbusch, C. Richter, E. Rocha, J.-A. Müller, and K. Hanssgen,          on Computer and Communications Security, ser. CCS ’19. New York,
     “A survey of payload-based traffic classification approaches,” IEEE             NY, USA: Association for Computing Machinery, 2019, p. 1131–1148.
     Communications Surveys & Tutorials, vol. 16, pp. 1135–1156, 2014.               [Online]. Available: https://doi.org/10.1145/3319535.3354217
     [Online]. Available: https://api.semanticscholar.org/CorpusID:20792087     [26] S. E. Oh, N. Mathews, M. S. Rahman, M. K. Wright, and N. Hopper,
 [9] M. AlSabah, K. S. Bauer, and I. Goldberg, “Enhancing tor’s perfor-              “Gandalf: Gan for data-limited fingerprinting,” Proceedings on Privacy
     mance using real-time traffic classification,” in the ACM Conference on         Enhancing Technologies, vol. 2021, pp. 305 – 322, 2021. [Online].
     Computer and Communications Security, CCS’12, Raleigh, NC, USA,                 Available: https://api.semanticscholar.org/CorpusID:231779670
     October 16-18, 2012, T. Yu, G. Danezis, and V. D. Gligor, Eds. ACM,        [27] Q. Zhou, L. Wang, H. Zhu, and T. Lu, “Few-shot website fingerprinting
     2012, pp. 73–84.                                                                attack with cluster adaptation,” Comput. Networks, vol. 229, p. 109780,
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015                                                                                                     15



     2023. [Online]. Available: https://api.semanticscholar.org/CorpusID:                                   Hantao Mei is currently pursuing his Ph.D. degree
     258297158                                                                                              with the School of Cyber Science and Engineering,
[28] Y. Hu, G. Cheng, W. Chen, and B. Jiang, “Attribute-based zero-                                         Southeast University, Nanjing, China. His current re-
     shot learning for encrypted traffic classification,” IEEE Transactions                                 search interests include anonymous communication,
     on Network and Service Management, vol. 19, pp. 4583–4599,                                             traffic analysis, and network measurement.
     2022. [Online]. Available: https://api.semanticscholar.org/CorpusID:
     249717931
[29] A. H. Lashkari, G. D. Gil, M. S. I. Mamun, and A. A. Ghorbani,
     “Characterization of tor traffic using time based features,” in Interna-
     tional Conference on Information Systems Security and Privacy, vol. 2.
     SciTePress, 2017, pp. 253–262.
[30] A. Chaabane, P. Manils, and M. A. Kaafar, “Digging into anonymous
     traffic: A deep analysis of the tor anonymizing network,” in 2010 fourth
     international conference on network and system security. IEEE, 2010,
     pp. 167–174.
[31] J. Yang, X. Chen, S. Chen, X. Jiang, and X. Tan, “Conditional variational                             Guang Cheng received the B.S. degree in Traffic
     auto-encoder and extreme value theory aided two-stage learning ap-                                    Engineering from Southeast University in 1994, the
     proach for intelligent fine-grained known/unknown intrusion detection,”                               M.S. degree in Computer Application from Hefei
     IEEE Transactions on Information Forensics and Security, vol. 16, pp.                                 University of Technology in 2000, and the Ph.D.
     3538–3553, 2021.                                                                                      degree in Computer Network from Southeast Univer-
[32] J. Henrydoss, S. Cruz, E. M. Rudd, M. Gunther, and T. E. Boult, “In-                                  sity in 2003. He is a Full Professor in the School of
     cremental open set intrusion recognition using extreme value machine,”                                Cyber Science and Engineering, Southeast Univer-
     in 2017 16th IEEE International Conference on Machine Learning and                                    sity, Nanjing, China. He has authored or coauthored
     Applications (ICMLA). IEEE, 2017, pp. 1089–1093.                                                      seven monographs and more than 100 technical pa-
                                                                                                           pers, including top journals and top conferences. His
                                                                                                           research interests include network security, network
                                                                                   measurement, and traffic behavior analysis. He is a Member of IEEE and a
                                                                                   Senior Member of CCF.



                         Yali Yuan received her Ph.D. degree from Göttingen
                         University (Göttingen, Germany) in 2018. Dr. Yuan
                         joined the School of Cyber Science and Engineer-
                         ing, Southeast University (Nanjing, China), as an
                         associate professor in 2021. Her research interests
                         include network traffic security analysis, network
                         attack and defense, as well as privacy protection.




                         Yu Huang is currently an intern at the School of
                         Cyber Science and Engineering, Southeast Univer-
                         sity, Nanjing, China. His current research interests
                         include fuzz testing, traffic analysis, and static code
                         analysis.




                         Xingjian Zeng (Student Member, IEEE) is currently
                         pursuing the B.S. degree with the School of Cyber
                         Science and Engineering, Southeast University, Nan-
                         jing, China. His current research interests include in-
                         formation security, traffic analysis, and data mining.
PAPER_TEXT
