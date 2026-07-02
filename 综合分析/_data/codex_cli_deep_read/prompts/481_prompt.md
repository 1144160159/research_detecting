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
# [481] LSTM Neural Networks Anomaly Detection for Biotic and Abiotic Early Stress Detection on Tomato Plants
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
编号：481
题名：LSTM Neural Networks Anomaly Detection for Biotic and Abiotic Early Stress Detection on Tomato Plants
年份：2025
DOI：10.1109/tafe.2025.3605825
来源：IEEE Transactions on AgriFood Electronics
PDF：paper/10.1109_TAFE.2025.3605825.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\481.txt
- 原始字符数：40549
- 本次发送字符数：40549
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
348

IEEE TRANSACTIONS ON AGRIFOOD ELECTRONICS, VOL. 3, NO. 2, SEPTEMBER/OCTOBER 2025

LSTM Neural Networks Anomaly Detection for
Biotic and Abiotic Early Stress Detection on
Tomato Plants
Federico Cum , Member, IEEE, Luca Alfarano, Massimo Pugliese , Danilo Demarchi , Senior Member, IEEE,
and Umberto Garlando , Member, IEEE

Abstract—This study explores time series anomaly detection
using a long short-term memory (LSTM) neural network to identify
abnormal plant conditions—both biotic and abiotic—by analyzing
a stem frequency parameter. This parameter, closely linked to plant
stem conductivity, serves as a novel indicator of plant hydration and
overall physiological status. Four independent experiments were
conducted between 28 May 2024, and 16 December 2024, and 20
tomato plants were maintained under different conditions (healthy,
biotic, and abiotic stress) to assess physiological differences and
develop models for early symptom detection. We used samples from
healthy plants to train an LSTM neural network to predict stem
frequency values 24 h ahead. The trained model was then used
to forecast the behavior of stressed plants, and an anomaly was
flagged whenever the predicted values significantly deviated from
the measured ones. Our LSTM-based anomaly detection model
successfully detected water stress conditions several days before
visible symptoms appeared. However, the algorithm struggled to
distinguish early signs of Fusarium infection. Despite this limitation, in most cases, the model provided early warnings of biotic
stress before any visual symptoms were evident. Future research
will focus on expanding the dataset to enhance the model’s ability
to differentiate between various types of plant stress. This article
builds upon the work presented at CAFE 2024 Cum et al., 2024,
utilizing the same experimental setup but exploring a completely
different approach for the early identification of stress symptoms
in tomato plants.
Index Terms—Drought, food security, Fusarium wilt, plant
abiotic stress, smart agriculture.

Received 28 February 2025; revised 12 July 2025; accepted 21 August 2025.
Date of publication 25 September 2025; date of current version 10 October
2025. This work was supported in part by the Agritech National Research
Center and received funding from the European Union Next-GenerationEU
(PIANO NAZIONALE DI RIPRESA E RESILIENZA (PNRR) – MISSIONE
4 COMPONENTE 2, INVESTIMENTO 1.4 – D.D. 1032 17/06/2022, under
Grant CN00000022, Mission 4 - Component 2 - Investment 3.1 - Call for
tender No. n. 3264 of 28/12/2021 of Italian Ministry, in part by the European
Union – NextGenerationEU under Grant IR0000027, Concession Decree No.
128 of 21/06/2022 adopted, Project title: iENTRANCE. This manuscript reflects
only the authors’ views and opinions, neither the European Union nor the
European Commission can be considered responsible for them. This article was
recommended by Associate Editor L. Dong. (Corresponding author: Federico
Cum.)
Federico Cum, Danilo Demarchi, and Umberto Garlando are with
the Department of Electronics and Telecommunications (DET), Politecnico di Torino, 10129 Torino, Italy (e-mail: federico.cum@polito.it; umberto.garlando@polito.it).
Luca Alfarano and Massimo Pugliese are with the Department of Agricultural, Forest, and Food Sciences (DISAFA), Università di Torino, 10095
Grugliasco(Torino), Italy.
Digital Object Identifier 10.1109/TAFE.2025.3605825

I. RESEARCH CONTEXT AND INTRODUCTION
GRICULTURE is deeply influenced by various environmental factors that affect crop growth and productivity.
Plant stresses can be divided into two main categories: biotic and
abiotic stress. Biotic stresses are caused by living organisms,
such as pests, diseases, and weeds, which can significantly
reduce crop yields and quality [2], [3]. On the other hand,
abiotic stresses arise from nonliving environmental factors, such
as drought, salinity, extreme temperatures, and nutrient deficiencies [4]. The interplay of these stressors, combined with
challenges related to global warming and increased food demand
due to overpopulation, poses a significant risk to food security. In
this scenario, smart agriculture is a promising solution to overcome such problems. Plant yield is deeply influenced by external
conditions that may cause plant stress (such as heat extremes and
water scarcity) or biotic causes, such as pests and pathogens. In
this context, efficient resource management and proactive monitoring of plants are crucial to guarantee better food production
and more efficient resource management. Recent advancements
in machine learning have introduced powerful techniques that
can significantly enhance the agricultural sector’s productivity
and efficiency. For example, Barradas et al. [5] used reflectance
spectroscopy on leaves and different machine learning models to
automatically detect drought conditions in Arabidopsis thaliana.
Deep learning techniques are widely used in literature to detect
pests and diseases [6]. Picon et al. [7] used state-of-the-art convolutional neural networks to detect visual symptoms of diseases
on different crop types. In the context of plant stress detection,
stem electrical impedance is emerging as a novel and promising
parameter. Various researchers have highlighted its potential in
recent studies. For instance, Garlando et al. [8] demonstrated
significant differences in stem impedance measurements when
tobacco plants were exposed to varying watering conditions.
Furthermore, studies such as those by the authors in [9] and [10]
have explored stem electrical impedance as a feature for binary
classifiers capable of detecting general stress in plants. Another
interesting application for stem impedance measurements is
detecting iron deficiency in tomato plants, as highlighted by
Hamed et al. [11], which provided promising results.
This study aims to identify biotic and abiotic stress symptoms
in tomato plants using stem frequency, a parameter able to
provide insights into plant hydration and overall health before

A

2771-9529 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

CUM et al.: LSTM NEURAL NETWORKS ANOMALY DETECTION FOR BIOTIC AND ABIOTIC EARLY STRESS DETECTION ON TOMATO PLANTS

the visible symptoms appear on the plant (such as wilting or
yellow leaves). The research focuses on two types of plant stress:
abiotic stress, induced by water deprivation, and biotic stress,
caused by infection with the pathogenic fungus Fusarium oxysporum. Tomato is one of the most widely grown plants producing
nongrain products with a worldwide production exceeding 180
million tonnes [12] worldwide, and pathogens such as Fusarium
pose significant challenges in tomato production worldwide,
leading to a substantial decrease in production, for example,
it is estimated that in India Tomato production reduced by 45%
due to Fusarium wilt [13], the primary disease caused by this
pathogen. Fusarium oxysporum is primarily transmitted through
infected soil, plant debris, contaminated seeds, irrigation water,
root-to-root contact, and farm equipment, allowing spread in
agricultural environments. This disease leads to different visible
symptoms, such as progressive leaf yellowing, wilting, and
necrosis of vascular tissues. Moreover, the infection blocks
xylem vessels, preventing water transport and causing plant
wilting, leading to the death of the plant. Biotic stresses such
as Fusarium wilt, combined with the increasingly frequent heat
waves and droughts caused by global warming, make early
identification of the problem imperative to prevent significant
production losses.
This study employs an anomaly detection approach [14]
to detect stress-related anomalies. Anomaly detection includes
various processes and algorithms for identifying patterns or data
that significantly deviate from expected behavior. It is widely
used in fields such as network security, fraud detection, and
predictive maintenance, with statistical methods and machine
learning being extensively employed to enhance the efficiency
and accuracy of these anomaly detection systems, but many
applications can be found in the growing field of smart agriculture [15]. In this context, long short-term memory (LSTM)
neural networks are widely used to predict the expected behavior
of a series of data [16]. The key idea in this article is to predict
the expected behavior of a plant parameter, the stem frequency.
If it deviates, the algorithm can detect abnormal behavior.
Plants maintained under optimal conditions are used to train
an LSTM neural network, which models the expected behavior
of stem frequency in healthy plants. The trained model predicts
stem frequency values for the following day at the same hour.
These predicted values are then compared to actual measurements: an anomaly is flagged if the prediction error exceeds a
predefined threshold or the exact value falls below a domain
knowledge-based threshold.
This article is an extension of the work conducted in [1].
In particular, a larger dataset is constructed, and a completely
different analysis is performed.
This research article is organized as follows.
1) Section II details the experimental setup for data collection
and plant management.
2) Section III describes the methodology for data preprocessing and the algorithms employed.
3) Section IV presents and analyzes the results.
4) Section V concludes the article and outlines the key findings and implications.

349

II. EXPERIMENTAL SETUP
In this study, 20 tomato plants (Solanum lycopersicum),
initially three weeks old, were transplanted into 3.6 liter pots.
The plants were kept in a greenhouse under natural light, where
the average temperature during the day was 25 ◦ C and the
temperature at night was 18 ◦ C. Relative air humidity averaged
56% during the day and 61% at night.
Different experiments were conducted, in particular, as follows.
1) Experiment 1: From 28 May 2024 to 4 July 2024.
2) Experiment 2: From 22 July 2024 to 14 September 2024.
3) Experiment 3: From 21 September 2024 to 21 October
2024.
4) Experiment 4: From 24 October 2024 to 16 December
2024.
Irrigation was carried out by filling the saucer pots, and
artificial infection was induced by adding 5 g/l of Fusarium
sample to the soil after the first week of measurements.
In total, 20 plants were analyzed under different conditions
as follows.
1) Eight plants (Healthy condition): Regular watering, no
fungal infection.
2) Eight plants (Drought condition): Complete water deprivation, no fungal infection.
3) Four plants (Fusarium infection): Regular watering, artificially infected with the Fusarium fungus.
The plants were monitored during all the experiment period
annotating the start of visible symptoms due to the applied
stressors.
A. Sensors Measurements
The plants were monitored using the system developed in [17].
The sensors are based on a relaxation oscillator, where the plant
stem is part of the circuit. Variations in stem conductivity cause
shifts in oscillator frequency, which is continuously measured
by an STM32WL55JC1 microcontroller. The recorded data
are transmitted wirelessly via the LoRa protocol over the free
ISM band (868 MHz in Europe). This approach can be seen
as an indirect measurement of the stem electrical conductivity,
which can give useful insights about plant hydration conditions
and its overall health. In a first approximation, a more hydrated
plant offers a higher conductivity hence a bigger stem frequency,
and vice versa. Two surgical needles were used as electrodes to
ensure proper electrical contact, positioned 2-cm apart. Their
small size was necessary due to the reduced diameter of the
plant’s stems, and their biocompatibility ensured minimal physiological impact on the subjects.
An illustration of electrode placement is shown in Fig. 1.
In addition to the stem frequency measurement system, soil
water potential [18] was measured to assess the hydration status
of the plant’s surroundings [19] helping the learning algorithms
to discriminate biotic and abiotic stress. For this purpose, the
watermark sensor [20] was selected. This sensor operates on
a resistive principle, where changes in soil water content alter its electrical resistance. The same method used for stem

350

IEEE TRANSACTIONS ON AGRIFOOD ELECTRONICS, VOL. 3, NO. 2, SEPTEMBER/OCTOBER 2025

baseline stem frequency was computed for each tomato plant
by averaging measurements taken at a sampling rate of one
acquisition every 60 min. This resulted in a total of 168 samples
per plant during first week of acquisition. Table I presents the
baseline values for different plants.
After acquiring the baseline, two features were extracted from
the stem frequency parameter as follows.
r Relative frequency change (RFC): The relative variation in
stem frequency concerning the initial baseline, calculated
as follows:
RFCk =

StemFreq[k] − Baseline
Baseline

.

(1)

r Stem frequency slope (first order difference): The rate of
change of the relative frequency variation during 1 h, since
one sample is recorded every hour the result is the difference between two consecutive stem frequency samples
Slope =
Fig. 1. Sensor connection with 3-D-printed support for precise needles positioning.

frequency measurement was applied to read the watermark
sensor: a relaxation oscillator, implemented using an LMC555
timer, generates a square wave whose frequency depends on the
sensor’s resistance. As soil moisture levels vary, the watermark
sensor’s resistance changes accordingly, leading to a measurable
shift in oscillation frequency.
Overall, throughout the acquisition period, a total of 42 053
samples were collected across all experiments.
III. METHODOLOGY
This section provides a detailed description of the methods
used in this research. In particular, the data preprocessing step
and the statistical tests conducted to evaluate the relevance of
the selected features and the algorithms employed for anomaly
detection are outlined.
A. Data Preprocessing
The data acquired across all experiments underwent a preprocessing step, as is standard in a typical machine learning pipeline.
The first crucial aspect to consider is the intrinsic variability among different plants. During previous studies, individual
plants exhibited different baseline stem frequency values, likely
attributable to inter-plant variability in stem conductivity [1].
Such variability may be considered a between-subject difference
in the same way for human patients
To account for this, the initial preprocessing step involved
establishing a baseline value for each plant. The first week of
data acquisition was designated as a calibration period under
the assumption that all plants were healthy during this time.
Stem frequency measurements collected during this period were
averaged to determine a baseline value for each plant. The

StemFreq[k] − StemFreq[k−1]
One sample

.

(2)

In addition, a normalization step is applied to the soil water
potential measurement. Since the employed sensor is reliable
in a range from 0 to –200 kPa, the SWP measurement was
normalized as follows:
SWPnorm =

SWP
.
200 kPa

(3)

B. LSTM and Anomaly Detection
LSTM neural networks are recurrent neural networks (RNNs)
designed to handle sequential data, making them suitable for
time series prediction. The LSTM addresses the problem of
the vanishing gradients affecting traditional RNNs. The LSTM
neural network comprises a cell and three gates: the input,
output, and forgets gates. The cell can store information over
time intervals, and the gates manage the data flow in and out. The
forget gate is responsible for deciding which past information
is irrelevant; hence, it is discarded. Similarly, the input gate
decides which new information the network has to use. This
selective process allows LSTMs to maintain long-term memory
and predict across multiple time steps ahead. In this work, we
decided to use LSTM networks to learn the temporal pattern of
stem frequency for a healthy plant. Then, the network is applied
to unseen stressed plants, and anomalies are flagged whenever
the predicted behavior deviates from the actual one. More details
about the network will be provided in Section IV-B.
IV. RESULTS AND DISCUSSION
A. Explorative Data Analysis
An example of the collected data for different plant conditions
is shown in Fig. 2 where three out of the 20 analyzed plants are
presented. The top three plots display the relative stem frequency
change concerning each plant’s initial calibration frequency. The
bottom three plots present the corresponding soil water potential
data The green background indicates when plant is not showing

CUM et al.: LSTM NEURAL NETWORKS ANOMALY DETECTION FOR BIOTIC AND ABIOTIC EARLY STRESS DETECTION ON TOMATO PLANTS

351

TABLE I
BASELINE FREQUENCY VALUES FOR EACH PLANT

Fig. 2. Example of stem frequency relative change under different conditions. The blue line shows the relative changes in stem frequency, while the red line
indicates the corresponding soil water potential. Green background areas denote periods with no visible plant stress symptoms. In contrast, red backgrounds indicate
visible stress symptoms (due to drought or Fusarium infection) from left to right: healthy, Fusarium-infected, and drought-stressed plants.

any visible symptom of stress, e.g., drought (abiotic) or Fusarium
(biotic).
Upon visual inspection, each tomato plant in Fig. 2 exhibits
an initial increase in stem frequency, suggesting a reduction
in stem conductivity—likely due to increased stem diameter
(analogous to a larger wire having lower resistance and conducting more). In healthy plants (left most plots in Fig. 2), this
increase continues until it reaches a plateau, stabilizing except
for natural day–night variations [21]. In contrast, plants under
drought stress (an example is shown in Fig. 2, right-most plots)
initially follow a similar increasing trend but then decline in
stem frequency before the first visible symptoms appear (e.g.,
wilting, yellowing leaves). This decrease suggests a decrease in
stem conductivity, as observed in [21]. Similarly, plants infected
(an example is shown in Fig. 2, central plots) with the Fusarium
pathogen also exhibit an initial increase in stem frequency,
followed by a decreasing trend. However, this decline is less
pronounced compared to drought-stressed plants. The trend
becomes more evident after the first visible symptoms appear,

likely due to the progressive occlusion of vascular tissues by the
Fusarium pathogen, which worsens over time as the infection
spreads.
To better understand the distribution of data for the different
plant conditions, the stem frequency features (RFC and stem
frequency slope) are represented on the boxplots of Fig. 3.
Boxplots represent the distribution of a dataset using five key
statistics: minimum (lower end of the left whisker), first quartile
(bottom edge of the box), median (line inside the box), third
quartile (top edge of the box), and maximum (upper end of
the right whisker), with the possibility of highlighting outliers,
which are values that fall outside the so-called “whiskers” (the
horizontal lines).
Different consideration can be done for the different plots as
follows.
r RFC (leftmost boxplot): Plants with symptoms exhibit a
slightly lower median RFC than healthy plants. However,
the interquartile ranges of both groups overlap significantly, suggesting substantial variability in stem frequency

352

IEEE TRANSACTIONS ON AGRIFOOD ELECTRONICS, VOL. 3, NO. 2, SEPTEMBER/OCTOBER 2025

Fig. 3.

Boxplot for the different stem frequency features.

and consequently, in stem conductivity, when the plant is
subjected to stress.
r Frequency slope (rightmost plot): The median frequency
slope values are comparable between symptomatic and
nonsymptomatic plants. However, symptomatic plants display a broader range and many outliers, indicating sudden
fluctuations in stem frequency trends, which may correspond to stress-induced physiological changes.
B. Forecasting and Anomalies
Plants are divided into training and test datasets based on
their condition: healthy plants are used for training, while plants
experiencing stress are assigned to the test dataset. The input
to the LSTM neural network consists of 24 time steps of the
selected features
Xt = [xt−23 , xt−22 , .., xt ]

(4)

and the output of the network is the value of relative stem
frequency change for the next day yt = xt+24 . Each plant’s data
are segmented into sequences using a sliding window approach.
For the training dataset, which includes eight plants, we obtained
a total of 473 sequences per plant, with each sequence consisting
of 24 samples (24 hours).
For training and validation, the leave-one-group-out (LOGO)
technique [22] is employed. In each iteration, all but one plant
from the training dataset is used for training, while the excluded
plant is used for validation. This process allows for performance
evaluation and hyperparameter tuning. After completing this
step, the final model is trained on the entire training and validation samples and then evaluated on the test plants belonging to
the stress groups (drought and Fusarium) which are completely
unseen from the model.
The trained model is used to predict stem frequency values
24 hours ahead, which are then compared to the actual measured
values. An anomaly is flagged if:

1) the prediction error exceeds a predefined threshold (either upward or downward), which accounts for variations in stem frequency that may be fast, but of high
value;
2) the actual value remains consistently lower (even for a
small amount) than the predicted one from the network
for 12 consecutive time steps (equivalent to 12 h).
The second criterion is introduced to capture cases where the
model correctly predicts a gradual decline in frequency. In such
scenarios, the difference between predicted and actual values
may remain below the threshold defined in the first condition,
and anomalies would otherwise go undetected. This policy ensures that sustained negative deviations, even if subtle, are still
flagged as potential anomalies since, based on prior knowledge,
such behavior does not indicate good plant health [21], [17].
Plants exhibiting low or negative RFC (i.e., a decrease compared to their baseline) are likely experiencing growth issues.
In contrast, healthy plants typically show an initial increase in
stem frequency, followed by stabilization at a specific value. In
our case, we set the prolonged threshold value to –0.05 of RFC,
indicating a reduction of 5% compared to the initial condition of
the plant. A higher threshold (15%) is set for anomalies in which
the actual frequency value is higher than the predicted ones, since
higher stem frequencies (hence higher stem conductivity) are
usually associated with better plant hydration and activity [17],
[21].
The employed network was a single-layer LSTM neural network with one hidden layer with 20 neurons. The input LSTM
layer processes the input sequence, capturing temporal patterns
across time steps. It outputs a sequence of hidden states, one
for each time step in the input. Then, the last hidden state of
the LSTM is passed to a fully connected layer to output the
prediction. The training was performed during 60 epochs, with
a batch size 32 and a learning rate of 0.01. The employed loss
function is Pytorch’s mean squared error loss. The results for
training and validation losses for one of the plants during the
LOGO procedure are reported in Fig. 4.

CUM et al.: LSTM NEURAL NETWORKS ANOMALY DETECTION FOR BIOTIC AND ABIOTIC EARLY STRESS DETECTION ON TOMATO PLANTS

Fig. 4.

353

Training and validation loss over epochs for LSTM network.

Fig. 6. Results of LSTM predictions for a plant under biotic Fusarium stress,
highlighting detected anomalies. The blue dashed line represents the actual
measured values, the orange line shows the network’s predicted values, and
the red markers indicate detected anomalies.

Fig. 5. Results of LSTM predictions for a plant under drought stress, highlighting detected anomalies. The blue dashed line represents the actual measured
values, the orange line shows the network’s predicted values, and the red markers
indicate detected anomalies.

After the training, process the LSTM model was used on
symptom plants according to the anomaly detection policy selected.
Fig. 5–7 suggest that the network is able to capture patterns
that approximate the plant’s behavior. However, at a certain point
(Fig. 5), the actual values deviate markedly from the training
examples, leading to an increased prediction error and the detection of an anomaly. Notably, some anomalies are detected
even before visible symptoms appear in the plant (Fig. 5). This
highlights the potential of using stem frequency, combined with
anomaly detection techniques, for early detection of drought
stress in plants.
Fig. 6 presents the results obtained for a Fusarium-infected
plant. In this case, the anomaly detection was less effective
compared to drought stress. While the algorithm successfully
identifies a sudden shift in the RFC before the first visible

Fig. 7. LSTM prediction results for a healthy plant, illustrating detected
anomalies. The blue dashed line represents the actual measured values, the
orange line corresponds to the network’s predicted values, and the red markers
indicate detected anomalies.

symptoms appear, it fails to consistently flag most of the samples
collected when the plant is under stress. As a result, many stressrelated data points are not correctly classified as anomalies.
The training was repeated while leaving out a plant in healthy
condition to validate the anomaly detection approach further.
In doing so, we ensured the procedure did not incorrectly flag
false anomalies. The results of this experiment are presented in

354

IEEE TRANSACTIONS ON AGRIFOOD ELECTRONICS, VOL. 3, NO. 2, SEPTEMBER/OCTOBER 2025

TABLE II
ANOMALY DETECTION METRICS FOR EACH PLANT, GROUPED BY CONDITION
(DROUGHT OR FUSARIUM)

Fig. 7. The trained model can capture the stable upward trend
in relative frequency over time, which is expected due to plant
growth.
Since the testing dataset includes multiple plants, presenting an individual plot for each one is impractical. Therefore,
we evaluated precision and recall for anomaly detection (i.e.,
stress symptoms), with the results summarized in Table II.
This evaluation considers only samples recorded after the first
appearance of symptoms. Symptoms are always present in this
subset, but the model does not always detect them. As a result,
precision remains 1.00 for all plants, as there are no false
positives, i.e., every sample in this period represents a true
anomaly.
However, recall varies significantly across different plants,
meaning that the model’s ability to identify symptomatic cases
correctly is inconsistent in all stress conditions. Most plants
with drought symptoms (1, 2, 3, 14, 15, 16, 18, 19 exhibit
high recall values, indicating that the model effectively captures
drought stress symptoms. Conversely, the algorithm struggles
with Fusarium-affected plants (4, 5, 6, 8), leading to lower recall
values. Since every sample after symptom onset is considered an
anomaly, precision is always 1, making recall the most relevant
metric for evaluating the model’s performance. In this context,
recall directly represents the proportion of actual anomalies that
were correctly identified. The overall recall for drought-stressed
plants is 0.89, while for Fusarium-affected plants, it is 0.49,
highlighting the problems of detecting biotic stress symptoms
compared to abiotic stress.
However, even if symptoms are not always correctly identified
in biotic stress conditions, the early detection of flagged anomalies can serve as an early warning for the future onset of stress
symptoms. The algorithm detects abnormal behavior before
symptoms become visually apparent, providing a valuable tool
for proactive monitoring.
For this reason, we also report in Table III the time point
at which a plant accumulates a certain number of detected
anomalies specifically, 12 h with flagged symptoms.
In most cases, this time threshold is reached before the first
noticeable visible symptoms appear, suggesting that the model
can provide early indications of plant stress even when recall
is not perfect. Particularly interesting are the results for plants

TABLE III
TIME DIFFERENCE BETWEEN THE FIRST DETECTED ANOMALIES AND THE
FIRST VISIBLE SYMPTOMS FOR EACH PLANT

1, 2, and 14 (drought), where anomalies were noticed seven,
four, and six days before the first visible symptoms on the
plant, respectively. For Fusarium, on average the anomalies were
identified one day before visible symptoms but many anomalies
are not identified at all as indicated by the low recall.
V. CONCLUSION AND FUTURE WORKS
In this study, we evaluated the ability of an anomaly detection LSTM model to identify plant stress conditions based on
recorded symptoms. Our results indicate that the model performs
well in detecting drought-induced stress, achieving high recall
and F1-scores across most plants. The overall F1-score for
drought-affected plants was 0.93, making the model effective
in capturing drought-related symptoms. Conversely, the model
struggled with identifying Fusarium-induced stress, with a lower
overall F1-score of 0.65. This suggests that biotic stress symptoms may present more subtle or variable patterns that are harder
to detect using the current approach. Despite the lower recall
for Fusarium, the early detection of anomalous behavior could
serve as a warning signal before visible symptoms appear. By
analyzing the time at which a sufficient number of anomalies
were detected, we found that for most plants, early warnings
were triggered several days before the first visible symptoms.
This highlights the potential of anomaly detection methods as
a proactive monitoring tool for plant health, allowing early
interventions before stress conditions become severe. Future
work should explore refinements in the model, such as incorporating additional physiological and environmental parameters,
to improve sensitivity to biotic stress factors. In addition, testing
the approach on a larger dataset with different plant species
and stress conditions would help assess its generalizability and
robustness.
REFERENCES
[1] F. Cum, L. Alfarano, M. Pugliese, D. Demarchi, and U. Garlando, “Preliminary analysis of biotic and abiotic stress on tomato plants using impedance
measurements and time series clustering,” in Proc. Conf. Agrifood Electron., 2024, pp. 125–129.
[2] R. K. Peterson and L. G. Higley, Biotic stress and yield loss. Boca Raton,
FL, USA: CRC Press, 2000.

CUM et al.: LSTM NEURAL NETWORKS ANOMALY DETECTION FOR BIOTIC AND ABIOTIC EARLY STRESS DETECTION ON TOMATO PLANTS

[3] P. Pandey, V. Irulappan, M. V. Bagavathiannan, and M. SenthilKumar, “Impact of combined abiotic and biotic stresses on plant
growth and avenues for crop improvement by exploiting physiomorphological traits,” Front. Plant Sci., vol. 8, 2017, Art. no. 537. [Online].
Available: https://www.frontiersin.org/journals/plant-science/articles/10.
3389/fpls.2017.00537
[4] R. Kopecká, M. Kameniarová, M. Černý, B. Brzobohatý, and J. Novák,
“Abiotic stress in crop production,” Int. J. Mol. Sci., vol. 24, no. 7, 2023,
Art. no. 6603. [Online]. Available: https://www.mdpi.com/1422-0067/24/
7/6603
[5] A. Barradas et al., “Comparing machine learning methods for classifying
plant drought stress from leaf reflectance spectra in arabidopsis thaliana,”
Appl. Sci., vol. 11, no. 14, 2021, Art. no. 6392. [Online]. Available: https:
//www.mdpi.com/2076-3417/11/14/6392
[6] J. Liu and X. Wang, “Plant diseases and pests detection based on deep
learning: A review,” Plant Methods, vol. 17, 2021, Art. no. 22.
[7] A. Picon, M. Seitz, A. Alvarez-Gila, P. Mohnke, A. Ortiz-Barredo, and J.
Echazarra, “Crop conditional convolutional neural networks for massive
multi-crop plant disease classification over cell phone acquired images
taken on real field conditions,” Comput. Electron. Agriculture, vol. 167,
2019, Art. no. 105093. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S0168169919309329
[8] U. Garlando et al., “Towards optimal green plant irrigation: Watering and
body electrical impedance,” in Proc. IEEE Int. Symp. Circuits Syst., 2020,
pp. 1–5.
[9] F. Cum, S. Calvo, D. Demarchi, and U. Garlando, “Machine learning
models comparison for water stress detection based on stem electrical
impedance measurements,” in Proc. IEEE Conf. AgriFood Electron., 2023,
pp. 108–112.
[10] M. Barezzi, F. Cum, U. Garlando, M. Martina, and D. Demarchi, “On the
impact of the stem electrical impedance in neural network algorithms for
plant monitoring applications,” in Proc. IEEE Workshop Metrol. Agriculture Forestry, 2022, pp. 131–135.
[11] S. Hamed, P. Ibba, A. Altana, P. Lugli, and L. Petti, “Towards tomato
plant iron stress monitoring through bioimpedance and circuit analysis,”
in Proc. IEEE Conf. AgriFood Electron., 2023, pp. 20–24.
[12] Food and Agriculture Organization of the United Nations, “FAOSTAT:
Food and agriculture data,” 2025. Accessed: Feb. 27, 2025. [Online].
Available: https://www.fao.org/faostat/en/#data/QCL
[13] R. McGovern, “Management of tomato diseases caused by fusarium oxysporum,” Crop Protection, vol. 73, pp. 78–92, 2015. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S026121941500071X
[14] B. Lindemann, B. Maschler, N. Sahlab, and M. Weyrich, “A survey on
anomaly detection for technical systems using LSTM networks,” Comput.
Ind., vol. 131, 2021, Art. no. 103498. [Online]. Available: https://www.
sciencedirect.com/science/article/pii/S0166361521001056
[15] C. Catalano, L. Paiano, F. Calabrese, M. Cataldo, L. Mancarella, and
F. Tommasi, “Anomaly detection in smart agriculture systems,” Comput. Ind., vol. 143, 2022, Art. no. 103750. [Online]. Available: https:
//www.sciencedirect.com/science/article/pii/S0166361522001476
[16] A. R. S. Parmezan, V. M. Souza, and G. E. Batista, “Evaluation of
statistical and machine learning models for time series prediction: Identifying the state-of-the-art and the best conditions for the use of each
model,” Inf. Sci., vol. 484, pp. 302–337, 2019. [Online]. Available: https:
//www.sciencedirect.com/science/article/pii/S0020025519300945
[17] S. Calvo, M. Barezzi, D. Demarchi, and U. Garlando, “In-vivo proximal
monitoring system for plant water stress and biological activity based
on stem electrical impedance,” in Proc. 9th Int. Workshop Adv. Sensors
Interfaces, 2023, pp. 80–85.
[18] M. M. Al-Kaisi, R. Lal, K. R. Olson, and B. Lowery, “Chapter 1 - fundamentals and functions of soil environment,” in Soil Health and Intensification of Agroecosytems, M. M. Al-Kaisi and B. Lowery, Eds. Cambridge,
MA, USA: Academic Press, 2017, pp. 1–23. [Online]. Available: https:
//www.sciencedirect.com/science/article/pii/B9780128053171000014
[19] M. Bittelli, “Measuring soil water content: A review,” HortTechnol. Hortte,
vol. 21, no. 3, pp. 293–300, 2011. [Online]. Available: https://journals.
ashs.org/horttech/view/journals/horttech/21/3/article-p293.xml
[20] IRROMETER Company, Inc., “Soil moisture sensors - irrometer,” 2025.
Accessed: Feb. 20, 2025. [Online]. Available: https://www.irrometer.com/
sensors.html

355

[21] U. Garlando et al., “Analysis of in vivo plant stem impedance variations
in relation with external conditions daily cycle,” in Proc. 2021 IEEE Int.
Symp. Circuits Syst., 2021, pp. 1–5.
[22] Scikit-learn Developers, “Leave-one-group-out cross-validation,” 2024.
Accessed: Feb. 26, 2025. [Online]. Available: https://scikit-learn.org/
stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.
html

Federico Cum (Student Member, IEEE) received the
bachelor’s and master’s degrees in electronic engineering in 2019 and 2022, respectively, from Politecnico di Torino, Torino, Italy, where he is currently
working toward the Ph.D. degree in electronic engineering.
His research focuses on the development of IoTbased electronic systems for advanced plant health
monitoring and smart irrigation.

Luca Alfarano received a bachelor’s degree in Agricultural Science and Technology in 2017 and a master’s degree in Agricultural Sciences in 2022, both
from the University of Turin, Department of Agricultural, Forest, and Food Sciences (DISAFA). He is
currently working toward the Ph.D. degree in Plant
Pathology at the same department, conducting research on the recycling of agro-industrial byproducts
to develop new technologies for agriculture, with the
goal of reducing chemical inputs in the sector.

Massimo Pugliese received the Ph.D. degree in Agricultural, Forestry, and Food Sciences in 2012 from the
University of Torino, Torino, Italy.
He is currently an Associate Professor in plant
pathology with the Department of Agricultural, Forest and Food Sciences, University of Torino. He actively collaborates with the Centre of Competence
AGROINNOVA in research activities, technology
Transfer, and in coordinating RD projects. He is
responsible for national and EU projects in the field
of sustainable crop protection and bioeconomy. His
research interests include the use of biofertilizers and suppressive compost
against plant pathogens and their impact on soil microbial communities, modes
of action and efficacy of biological control agents and plant protection products,
and biological control of diseases in horticulture.

356

IEEE TRANSACTIONS ON AGRIFOOD ELECTRONICS, VOL. 3, NO. 2, SEPTEMBER/OCTOBER 2025

Danilo Demarchi (Senior Member, IEEE) received a
master’s degree in Electronic Engineering in 1991 and
a Ph.D. in Electronic Engineering in 1995, both from
Politecnico di Torino, Torino, Italy. He is currently a
Full Professor with the Department of Electronics and
Telecommunications, Politecnico di Torino, Torino,
Italy. He is involved in smart system integration and
IoTs for the agrifood value chain and for biomedical
devices. He was a Visiting Scientist with the Massachusetts Institute of Technology, Cambridge, MA,
USA, in 2018, and Harvard Medical School, Boston,
MA, USA, for the project Smart electronic IoT SysTEms for Rehabilitation
sciences (SISTER). He was a Visiting Professor with EPFL Lausanne, Lausanne,
Switzerland, in 2019 and with Tel Aviv University, Tel Aviv, Israel, from
2018 to 2021. His research focuses on wearable plant sensors. He is also
leading the electronic Life-Oriented iNtelligent Systems (eLiONS), Laboratory
of Politecnico di Torino, and coordinating the Italian Institute of Technology
Microelectronics Group at Politecnico di Torino.
Prof. Demarchi is the Founder and Editor-in-Chief of IEEE TRANSACTIONS
ON AGRIFOOD ELECTRONICS. He is also the Founder and first General-Co-Chair
of the IEEE Conference on AgriFood Electronics – CAFÉ, and Founder and
Chair of the IEEE CAS Special Interest Group on AgriFood Electronics. From
2023 to 2024, he was a Distinguished Lecturer for the IEEE CAS Society. He was
a Member of the IEEE Sensors Council (2020–2023) and the BioCAS Technical
Committee (since 2013). He is or was an Associate Editor for IEEE Open Journal
on Engineering in Medicine and Biology (OJ-EMB). He was a General Chair
of IEEE BioCAS (Biomedical Circuits and Systems) Conference in 2017 in
Torino and Founder of IEEE FoodCAS Workshop (Circuits and Systems for the
FoodChain). He was a TPC Co-Chair of IEEE ICECS 2019, IEEE BioCAS 2021
and 2022 conferences. He was the General Co-Chair of IEEE BioCAS 2023.

Umberto Garlando (Member IEEE) received the
bachelor’s and master’s degrees in electronic Engineering from Politecnico di Torino, Torino, Italy, in
2013 and 2015, respectively, and the Ph.D. degree in
electronic engineering with the VLSILab, Politecnico
di Torino, in 2019.
He is currently with Politecnico di Torino, working
on CAD and EDA tools for FCN (Field coupled
nanocomputing). He worked in the development of
the ToPoliNano framework, focusing on the simulation part. In 2020, he joined the electronic Life Oriented iNtelligent Systems (eLiONS) group (ex MiNES) as a research Associate,
where he works on a fast-growing field such as the smart-systems for agri-food
technology.
PAPER_TEXT
