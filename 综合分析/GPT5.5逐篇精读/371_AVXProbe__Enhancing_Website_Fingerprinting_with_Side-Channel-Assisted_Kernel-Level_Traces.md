# [371] AVXProbe: Enhancing Website Fingerprinting with Side-Channel-Assisted Kernel-Level Traces

## 1. 基本信息

- 论文：AVXProbe: Enhancing Website Fingerprinting with Side-Channel-Assisted Kernel-Level Traces
- 作者：Suryeon Kim, Seung Ho Na, Jaehan Kim, Seungwon Shin, Hyunwoo Choi
- 会议：ACM Asia CCS 2025
- DOI：10.1145/3708821.3710819
- 主题归类：加密流量分类与应用识别 / 网站指纹识别 / 微架构侧信道
- 本地 PDF：`paper/10.1145_3708821.3710819.pdf`
- 正文包：`综合分析_data/full_text_cache_plain/371.txt`
- 正文截断情况：未截断
- 代码状态：未发现该论文对应的本地开源代码

## 2. 中文翻译与核心摘要

这篇论文提出 AVXProbe：一种不直接看网络包、也不扫描整个 LLC 缓存占用，而是利用 AVX masked load/store 指令在内核模块地址空间中探测 TLB、cache、memory 访问状态的网站指纹攻击。

传统网站指纹攻击多依赖加密流量的包长、方向、时序；后来的侧信道攻击则利用 LLC cache occupancy、系统中断、CPU 频率、功耗等。AVXProbe 的核心转向是：浏览器加载网页时会触发网络、渲染、加密、文件系统、声卡、电源/温度管理等内核路径，不同网站会留下不同的内核模块级微架构访问痕迹。攻击者通过非特权 native code 执行 AVX masked operation，测量访问内核模块地址的时间，从而采集每个模块的时序特征，再用 SVM 分类访问的网站。

关键效果是：在 Chrome + Intel Alder Lake 上，100 个网站闭集分类达到 97.7% accuracy；在 Firefox + AMD Zen+ 上达到 96.6%；Tor Browser 上 Top-1 为 74.5%，Top-5 达到 95.25%。更重要的是，在数据量大幅压缩时仍然强：Chrome 场景下 3.2 秒采集、每站点 8 个训练样本仍接近 90%，明显强于 Loop-Counting、DF-SCA、SegScope 等侧信道基线。

## 3. 论文解决的具体问题

论文瞄准的问题不是“如何从网络流量中识别网站”，而是更隐蔽也更贴近本机攻击模型的问题：

当网络侧指纹被加密、缓存、本地响应缓存或流量混淆削弱后，攻击者能否仅凭本机微架构侧信道识别用户访问的网站？

已有 cache occupancy 攻击虽然有效，但它监控整个 LLC，信号粗、噪声大、容易受其他程序干扰，因此通常需要较多样本和较长采集时间。AVXProbe 试图解决两个具体痛点：

1. 降低侧信道采集噪声：不再扫整个 LLC，而是只探测加载的内核模块地址空间。
2. 降低攻击数据需求：在较短页面加载时间、较少训练样本下仍保持高分类准确率。

论文实际回答的是：网站加载过程触发的内核模块活动是否有足够稳定、可区分的模式，能够成为网站指纹特征。

## 4. 创新点深度提炼

第一，攻击对象从“全局缓存占用”转向“内核模块级地址空间”。

这比 cache occupancy 更细。作者认为网页加载并不是单纯网络行为，而是网络栈、GPU/DRM 渲染、加密、文件系统、功耗管理等内核路径的组合行为。AVXProbe 把这些内核模块当作观测单元，使特征更贴近浏览器实际执行链路。

第二，复用 AVX-TSCHA 作为网站指纹采集原语。

AVX masked operations 在 mask 为零时可以抑制非法地址访问异常，同时访问时间仍泄露映射状态和 TLB 状态。论文把这一原本用于 KASLR/内核活动探测的能力，改造成网站指纹采集器。

第三，采集的不只是 TLB，而是 TLB、cache、memory 的层级访问时间。

正文中观察到大致三类时间分布：约 170 cycles、208 cycles、288 cycles，分别对应更快的 TLB 命中、cache 命中和内存访问。也就是说，特征不是单点二值状态，而是带有层级信息的模块访问剖面。

第四，引入内核模块功能组消融分析。

论文不只报告准确率，还把 127 个内核模块按功能分成 Bus、Crypto、Filesystem、Render、HID、Misc、Network、Power/Temp、Sound、Data 十组，系统分析哪些组合对分类最关键。结果显示不是单一模块决定效果，而是 Sound + Power/Temp、Sound + Power/Temp + Crypto 等组合产生较强协同。

第五，在小数据条件下的鲁棒性是论文最有说服力的部分。

很多侧信道论文在充足采样下准确率很高，但现实攻击中采集窗口和样本数受限。AVXProbe 在 3.2 秒、8 个训练样本/网站时仍接近 90%，这是它相对基线最核心的优势。

## 5. 科学问题与研究假设

论文显式提出三个研究问题，可归纳为三组科学假设。

RQ1：额外的微架构信息是否能增强 cache-based 网站指纹性能？

假设是：网页加载涉及内核空间活动，内核模块地址空间中的 TLB/cache 状态比整个 LLC 更有信息密度。

RQ2：与已有侧信道攻击相比，AVXProbe 提取的数据是否更“强”？

假设是：模块级采集减少无关噪声，因此在缩短采集时间、减少训练样本时，性能下降会比 Loop-Counting、DF-SCA、SegScope 更慢。

RQ3：不同内核模块组合如何影响攻击效果？

假设是：与网页加载强相关的模块组，例如渲染、加密、网络、电源/温度、声音，会比无关模块携带更多分类信息；并且多个功能组之间存在协同，而非单模块独立决定分类。

## 6. 科学方法与技术路线

AVXProbe 的技术路线可以拆成五步。

1. 发现加载的内核模块地址  
   攻击者利用 AVX masked operation 的异常抑制和 mapped/unmapped 区分能力，扫描内核模块地址空间，识别当前加载的模块区域。

2. 与浏览器同逻辑核运行  
   攻击模型要求攻击进程和浏览器进程运行在同一 logical core。论文使用 `taskset` 固定进程，增强侧信道可观测性。

3. 页面加载期间探测模块地址  
   对每个内核模块按 1 KiB 间隔访问地址，测量执行时间。访问时间由 `rdtscp` 前后包围 `vmaskmovp` 得到。

4. 控制模块大小偏置  
   不同模块大小差异很大，例如 Nvidia 模块可达几十 MiB，而小模块只有数 KiB。论文没有按模块大小自然采样，而是固定每个模块采集相同数量 trace；小模块重复访问，大模块取固定数量间隔点。

5. 训练 SVM 分类器  
   每次网站访问形成一个模块级 timing trace 向量，标签为网站类别。由于每类样本少，作者选择 SVM，而不是深度学习模型，以降低小样本过拟合风险。

核心伪代码逻辑是：遍历模块地址，`mfence` 后读时间戳，执行 masked AVX memory operation，再读时间戳，记录差值。为了避免顺序访问触发硬件预取，访问顺序会随机化；为了避免小模块一直留在 TLB 中，采集过程中还周期性驱逐 TLB entries。

## 7. 实验设计与实验步骤

可复核流程如下。

数据：

- 目标网站：Alexa Top 100，附录列出 100 个网站。
- 浏览器：Chrome 112、Firefox 112、Tor Browser 12，均无扩展。
- 系统：Ubuntu 20.04 LTS，Linux kernel 5.15.0。
- CPU：
  - Intel Alder Lake i5-12400F
  - Intel Rocket Lake i7-11700K
  - AMD Zen+ Ryzen 5 2600

预处理：

- 先探测已加载内核模块，确定模块地址范围。
- 对每个模块固定采集相同数量 trace，默认 500 traces/module。
- 地址访问按 1 KiB 间隔，随机化探测顺序。
- 周期性 flush TLB，降低小模块重复访问造成的 TLB 常驻偏置。
- 单次样本的维度约等于 `模块数 × 每模块 traces`，例如 Alder Lake 上 127 × 500 = 63,500 traces。

模型/基线：

- 主模型：SVM。
- 对比方法：
  - Loop-Counting
  - DF-SCA
  - SegScope
- 基线保持原论文方法和分类器设定，统一调整到相近采集时长和样本数。

训练：

- 每个网站采集有限 measurement。
- 数据按 80% 训练、20% 测试划分。
- 小数据实验中逐步减少训练样本数，例如每站点 16、14、12、10、8 个训练样本。

指标：

- 主指标：Top-1 accuracy。
- Tor Browser 额外报告 Top-5 accuracy，因为 Tor 路由不稳定使 Top-1 更难。

消融/敏感性：

- 采集时间敏感性：从默认采集时间逐步缩短到 3.2 秒。
- 训练样本敏感性：固定测试集，减少每站点训练样本。
- 模块组消融：按功能分成 10 组，测试去掉单组、只保留单组、去掉多组组合后的准确率变化。
- 特征离散化实验：把 timing 值压缩为 1/2/3/4 四档，仍能达到接近 80%，说明层级访问状态本身就有分类信息。

结果核查：

- 检查同一网站多次访问的 heatmap 是否相似。
- 检查不同网站在模块组上的访问模式是否有差异。
- 检查误分类样本是否与登录页相似、同源 JavaScript、动态内容等因素相关。
- 检查模块组消融是否与直觉一致，并识别协同组合。

## 8. 关键结果、结论与证据

最强结果来自 Chrome + Intel Alder Lake：

- 100 网站闭集分类，20 measurements/site，8 秒采集，97.7% accuracy。
- 采集缩短到 3.2 秒，仍有 95.5% accuracy。
- 每站点训练样本降到 8 个，仍有 89.25%。

Firefox + AMD Zen+：

- 50 measurements/site，8 秒采集，96.6% accuracy。
- 性能略低于 Alder Lake，论文解释为 Zen+ 加载模块数更少，并且 AMD timestamp counter 分辨率更粗。

Tor Browser：

- Top-1 accuracy 为 74.5%。
- Top-5 accuracy 为 95.25%。
- 说明 AVXProbe 对 Tor 仍有信号，但 Tor 网络路径和加载行为引入了更强不确定性。

与基线对比：

在 3.2 秒采集、16 个训练样本时：

- Loop-Counting：74.50%
- DF-SCA：81.00%
- SegScope：66.50%
- AVXProbe：95.50%

在 3.2 秒采集、8 个训练样本时：

- Loop-Counting：58.00%
- DF-SCA：69.99%
- SegScope：44.80%
- AVXProbe：89.25%

这些结果支持论文主张：模块级内核侧信道比更粗粒度的系统中断、CPU 频率或全局循环计数更抗小样本退化。

模块组结果也很关键：

- 去掉 Sound 后准确率从 97.7% 降到 93.5%，单组剔除中影响最大。
- 只保留 Sound 仍可达 85.7%，比只保留 Network 的 53.0% 强很多。
- 多组组合中，Sound + Power/Temp、Sound + Power/Temp + Crypto 是最显著组合。
- 这说明网页指纹并非只由网络模块产生，浏览器渲染及系统资源管理路径同样泄露网站差异。

## 9. 局限性与待解决问题

第一，实验主要是闭集分类。

攻击者假设用户访问的是 100 个目标网站之一。真实世界中用户可能访问无限多非目标网站，open-world 或 monitored/unmonitored 场景会更难。论文也承认这仍是未来工作。

第二，攻击需要 native code 执行。

由于 JavaScript 和 WebAssembly 当前不支持完整 AVX masked operations，AVXProbe 不能直接在浏览器沙箱内运行。这使攻击模型强于纯网页攻击：攻击者需要本地非特权代码执行能力。

第三，需要与受害浏览器共享逻辑核。

论文使用 `taskset` 让攻击进程和浏览器在同一 logical core。现实中攻击者未必总能控制调度，云环境、多任务桌面环境中的稳定性还需要更多验证。

第四，系统和硬件差异影响很大。

不同 CPU、不同 OS、不同内核模块集合都会改变 trace 维度和分布。Zen+ 上 timestamp 分辨率较粗，Tor 上网络路径不稳定，都会降低效果。论文虽然展示跨 Intel/AMD、Chrome/Firefox/Tor，但规模仍有限。

第五，自动化采集会被网站反爬机制干扰。

正文提到 CAPTCHA、动态登录 URL 等会阻碍 Selenium 自动访问，因此部分网站或行为需要人工处理。这意味着构建大规模训练集并不总是平滑。

第六，防御讨论偏概念，缺少系统量化。

例如增加随机音频、加密随机字符串、动态内容等软件噪声方案，论文主要是建议，没有完整评估防御代价、用户体验影响和分类准确率下降幅度。

第七，因果解释尚不足。

消融能说明哪些模块组“相关”，但还不能证明具体内核函数、网页资源类型和微架构痕迹之间的因果链。作者也把直接辨析每个内核模块的因果影响留给未来工作。

## 10. 与本项目的关系

如果本项目关注“加密流量分类与应用识别”，这篇论文的价值在于拓宽了应用识别的数据源边界。

它提示我们：加密流量分类不一定只能看网络侧元数据。即便 TLS、Tor、缓存或流量填充削弱了包级特征，本机侧仍可能通过渲染、网络栈、加密库、设备驱动、功耗管理留下可分类痕迹。

对综述或研究设计有三点启发：

1. 应用识别可以融合网络侧与主机侧信号，例如流量时序 + 系统调用 + 微架构 timing。
2. 防御不能只遮蔽网络包形态，还要考虑浏览器渲染和系统资源使用模式。
3. 小样本鲁棒性值得作为评价维度，而不只是报告大样本闭集 accuracy。

不过它与传统网络异常检测的相关性是“中相关”：技术上属于本机侧信道攻击，不是网络入侵检测或流量异常检测本身；但在“加密应用识别”和“隐私威胁建模”上非常有参考价值。

## 11. 代码对照分析

本地未发现该论文对应的开源代码包，因此无法做真实文件级映射。结合论文方法，如果复现实验，代码通常会分成以下模块：

- 内核模块地址探测  
  对应论文 Step 1：扫描内核模块地址空间，利用 AVX masked operation 区分 mapped/unmapped pages。

- AVX timing 采集器  
  对应 Algorithm 1：实现 `mfence`、`rdtscp`、`vmaskmovp`、访问时间差记录，以及 1 KiB 间隔探测。

- TLB flush / 随机访问控制  
  对应 Step 3 和反预取处理：周期性驱逐 TLB entries，随机化 probe 顺序。

- 浏览器自动化访问  
  论文使用 Selenium，负责打开 Alexa Top 100 网站、控制访问间隔、采集期间同步运行 probe。

- 数据矩阵构建  
  把每次访问转换为 `num_modules × traces_per_module` 的特征向量，并绑定网站标签。

- 分类训练与评估  
  SVM 训练、80/20 划分、Top-1/Top-5 accuracy、不同采集时间和训练样本数实验。

- 消融分析  
  根据内核模块路径把模块划分为 10 个功能组，执行单组去除、单组保留、多组组合去除的 accuracy 对比。

如果后续找到代码，优先检查目录中是否有类似 `probe`, `avx`, `collector`, `selenium`, `svm`, `ablation`, `dataset` 的文件或脚本名。真正关键的源码应当是 AVX 指令 timing 采集器，而不是 SVM 部分，因为分类器本身较常规。

## 12. 本篇精华

1. AVXProbe 的核心不是“更强分类器”，而是“更干净的信息源”：从整个 LLC 转向内核模块级 TLB/cache/memory timing trace。

2. 网站加载会触发网络、渲染、加密、声音、电源/温度等多类内核模块；网站指纹泄露来自这些路径的组合，而非单纯网络栈。

3. AVX masked operation 的异常抑制特性使非特权攻击者可以安全探测内核地址，并从访问时间中读出映射状态和 TLB/cache 状态。

4. 小样本实验是论文最强证据：3.2 秒采集、8 个训练样本/网站仍接近 90%，显著优于 Loop-Counting、DF-SCA、SegScope。

5. Tor 场景 Top-1 明显下降，但 Top-5 很高，说明信号存在，只是 Tor 的加载路径和网络随机性让精确排名更困难。

6. 消融显示 Sound、Power/Temp、Crypto 等非网络模块很重要，防御者不能只关注网络流量混淆。

7. 论文的主要现实限制是 native code、本地同核运行、闭集假设；它更像强本地攻击模型下的隐私威胁，而不是远程网页即可触发的攻击。

8. 对加密流量识别研究而言，它提供了一个重要方向：主机侧微架构痕迹可以补足或绕过网络侧特征。

## 13. 建议精读路线

1. 先读 Introduction 和 Research Goal，抓住三个 RQ：增强 WF、减少数据、模块组贡献。

2. 再读 Section 5，重点理解 AVX masked operation 如何变成 kernel-module trace 采集器。Algorithm 1 是方法核心。

3. 精读 Table 2、Figure 2、Figure 3、Table 3、Table 4，这些结果支撑“少数据仍强”的主张。

4. 继续读 Section 6.4、Table 5、Table 6、Figure 4，理解为什么论文说攻击依赖多模块组合协同。

5. 最后读 Discussion 和 Countermeasures，重点看误分类原因、native code 限制、open-world 局限、AVX/KPTI/噪声防御。

<!-- codex-cli-deep-read: complete -->
