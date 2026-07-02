# [572] VarAD: Lightweight High-Resolution Image Anomaly Detection via Visual Autoregressive Modeling

## 1. 基本信息
- 论文：VarAD: Lightweight High-Resolution Image Anomaly Detection via Visual Autoregressive Modeling
- 作者：Yunkang Cao, Haiming Yao, Wei Luo, Weiming Shen
- DOI：10.1109/TII.2024.3523574
- 来源：IEEE Transactions on Industrial Informatics，正文页眉为 Vol. 21, No. 4, April 2025；元数据年份标为 2024，更接近录用/DOI 年份。
- 任务定位：高分辨率工业图像异常检测，和入侵检测、网络异常检测的关系不是应用对象相同，而是共享“正常模式建模、异常偏离打分、长程上下文建模”的方法论。

## 2. 中文翻译与核心摘要
这篇论文的核心是把高分辨率图像异常检测从“重建图像/特征”改写成“预测视觉 token”。模型只用正常图像训练：先用冻结的 DINOv2 提取多层视觉 token，再把二维 token 按多个方向展开成序列，使用 Mamba 做自回归预测；测试时，如果某个位置的真实 token 难以被正常上下文预测，就把预测误差作为异常分数。

作者真正想解决的不是普通 MVTec 256 分辨率上的饱和指标，而是 1024×1024 这类工业检测场景：小缺陷在低分辨率下会被压缩到极少像素，直接降采样会丢失缺陷，滑窗又会切断全局上下文。VarAD 的路线是：保留高分辨率，又避免 Transformer 全局注意力的二次复杂度。

## 3. 论文解决的具体问题
论文针对的是 HRIAD，即 high-resolution image anomaly detection。问题有三层：

- 细粒度缺陷保真：1 mm 级别缺陷在 256×256 下可能只有几个像素，在 1024×1024 下才有足够可检测面积。
- 全局结构需求：某些异常不是局部纹理坏点，而是与整体结构、排列、语义一致性有关；滑窗 patch 检测容易丢掉这种信息。
- 计算可承受性：CNN 瓶颈局部感受野有限，Transformer 瓶颈虽有全局感受野但注意力复杂度随 token 数平方增长，不适合高分辨率直接处理。

## 4. 创新点深度提炼
- 把异常检测形式化为视觉 token 预测，而不是重建输入或比对 memory bank。这个转化使“正常上下文能否预测当前位置”成为异常判据。
- 用 Mamba/选择性状态空间模型替代 Transformer 注意力，在保持长程信息流的同时把序列建模复杂度控制在线性量级。
- 多方向扫描解决自回归序列只能看“前文”的问题：左上到右下、右下到左上、右上到左下、左下到右上共同覆盖不同方向的上下文。
- 多层级 token 兼顾浅层结构与深层语义。论文默认取 DINOv2 ViT-S/14 的第 4、8、12 层。
- 引入轻量 feature adapter 缓解 DINO 自然图像预训练与工业图像之间的域差异，且不破坏冻结 backbone 的通用表征。
- 设计预测步长，故意排除最近邻 token，避免模型只靠局部相邻 token 做“捷径式复制”。

## 5. 科学问题与研究假设
科学问题可以概括为：在高分辨率异常检测中，是否可以用正常视觉 token 的长程可预测性来替代重建或邻域匹配？

论文隐含的研究假设包括：

- 正常样本的视觉 token 序列存在稳定的上下文规律，Mamba 能从正常图像中学习这种规律。
- 异常 token 虽然可能局部纹理相近，但与正常全局上下文不一致，因此预测误差会升高。
- 最近邻 token 过强会导致模型学到局部复制，排除最近邻能迫使模型利用更远上下文。
- DINOv2 token 足够通用，但工业域仍需轻量适配。
- 多方向展开后的预测结果融合，能弥补单向自回归遗漏“未来上下文”的缺陷。

## 6. 科学方法与技术路线
技术路线是“图像 → 多层视觉 token → 多方向序列 → Mamba 预测 → 误差聚合 → 异常图”。

具体来说，输入高分辨率图像后，冻结 DINOv2 提取多层 feature map，并通过 adapter 得到适配后的 token。每一层 token 被展开为四个方向的序列。Mamba 根据前序 token 预测目标 token，但预测时跳过距离最近的若干 token，以增强全局建模。预测得到的 token 再按反向扫描还原到二维空间，多个方向、多层级误差聚合成最终 anomaly map。训练目标是在正常图像上最小化预测 token 与原 token 的差异。

源码中这一逻辑主要落在 `model/VarAD/anomaly_mamba.py` 和 `model/VarAD/vssm.py`：前者组织 tokenizer、VSSM 分支、损失和异常图，后者实现 CrossScan、CrossMerge、BOS token、`pred_next_n` 位移预测和选择性扫描模块。

## 7. 实验设计与实验步骤
1. 数据：公开数据集包括 MVTec AD、VisA、BTAD、DTD-Synthetic，共 42 类，正常训练样本 15,287 张，测试正常 2,237 张、异常 3,695 张；另有私有按钮检测数据集，4 类，1024×1024，包含位置不齐、光照变化、背景干扰。
2. 预处理：论文统一 resize 到 1024×1024，并用 ImageNet 均值方差归一化；mask 最近邻 resize。源码中 `trainer.py` 做 `Resize + CenterCrop + Normalize`，DINO 模型会把输入尺寸调整为 14 的倍数，例如 `--image_size 1024` 会变为 1022。
3. 模型：默认 DINOv2 ViT-S/14，取第 4、8、12 层，通道数 384；adapter 默认线性 1×1 卷积残差；Mamba/VSSM 负责四向序列预测。
4. 基线：PFM、RD4AD、PatchCore、CDO、PyramidFlow、MSFlow、AMI-Net、PNPT，覆盖 CNN、memory bank、flow、Transformer 重建/修复类方法。
5. 训练：无监督一类训练，只用正常样本；AdamW，学习率 5e-4，batch size 2，10 epochs。源码入口是 `main.py`，训练循环在 `model/VarAD/trainer.py`。
6. 指标：像素级 AUROC、max-F1、AP；图像级 AUROC/F1/AP 也报告。论文明确未使用 PRO 作为主指标，因为高分辨率下计算开销较大；源码 `tool/metrics.py` 保留了可选 PRO。
7. 消融/敏感性：扫描方向、预测步长 `m`、adapter 类型、token 层级组合、backbone 类型、输入分辨率、复杂度。
8. 结果核查：应同时核对表格指标、异常热力图、分辨率曲线和复杂度图；只看 AUROC 不够，因为小缺陷定位更依赖 max-F1/AP 和可视化。

## 8. 关键结果、结论与证据
- 像素级结果中，VarAD 在四个公开数据集上达到 97.7%、98.5%、97.8%、98.8% AUROC，是论文报告的最佳整体表现。
- 在 BTAD 和 DTD-Synthetic 上，VarAD 的 max-F1 相比第二名 CDO 分别提升 6.5% 和 5.0%，说明它不只是提升排序指标，也改善了阈值后定位质量。
- 高分辨率趋势是论文的重要证据：许多传统方法从 256 到 1024 分辨率性能下降，而 VarAD 更稳定，部分 max-F1/AP 随分辨率提高还略有改善。
- 复杂度方面，VarAD 10 epochs 收敛约 389 秒，报告推理速度约 8.0 FPS；比 Transformer 类方法更适合高分辨率场景。
- 私有按钮数据上，VarAD 达到 96.8% AUROC、36.0% max-F1、30.8% AP，相比 CDO 分别高 0.1%、5.4%、4.6%，说明在更接近真实工业噪声的场景中仍有优势。
- 图像级结果不是全面碾压：MSFlow 和 CDO 在 MVTec AD、VisA 上较强，VarAD 主要在 BTAD、DTD-Synthetic 图像级指标领先。这说明 VarAD 的优势更集中在像素级定位和高分辨率稳定性。

## 9. 局限性与待解决问题
- 论文未来工作也承认：需要扩展到多类别同时异常检测，并提升图像级异常检测能力。
- 方法依赖高质量视觉 tokenizer；消融显示 backbone 对结果影响显著，DINOv2-B 更强但速度下降到约 3.8 FPS，轻量与性能存在权衡。
- 预测步长有全局/局部取舍：步长太小容易局部复制，太大又损失局部细节。
- 私有按钮数据没有在当前代码仓库中看到完整数据 loader，只在可视化/分析脚本注释中出现 button 线索，复现实验会受限。
- 当前正文包标记为未截断，因此本文理解不受正文截断影响；但表格具体逐项数值在纯文本中不如 PDF 清晰，若要写正式综述，仍建议回到 PDF 核对表 II、表 III、表 VI 的完整数值。
- 代码环境存在复现风险：`init.sh` 引用 `./VMamba`，但当前顶层目录未见该文件夹；`dino/model.py` 中 DINOv2 使用硬编码本地路径 `/home/anyad/.cache/...`；`vssm.py` 依赖 `selective_scan_cuda*` 扩展。

## 10. 与本项目的关系
与入侵检测/网络异常检测的关系属于“中相关”。它不是网络流量论文，但方法思想有迁移价值：

- 高分辨率图像中的长 token 序列，可类比网络流、日志、系统调用、包序列中的长上下文建模。
- “只用正常样本训练，测试时看预测误差”与一类入侵检测、工业控制异常检测非常接近。
- Mamba 的线性长序列建模适合高维长序列安全数据，尤其当 Transformer 成本过高时。
- 多方向扫描在网络时序中不能直接照搬，但“改变序列化视角以补足单向上下文”可迁移到双向会话、请求-响应、主机-网络多视角建模。
- 不宜直接把 VarAD 的图像指标解释为网络安全性能；它提供的是跨域异常检测架构启发，而不是 IDS 实证证据。

## 11. 代码对照分析
- 入口与运行：`source\VarAD\main.py` 解析 `--dataset`、`--category`、`--image_size`、`--model`、`--pred_next_n`、`--hierarchies`、`--adapter` 等参数，构造数据集、trainer、训练和评估流程。README 给出的命令是 `python main.py --image_size 512 --model dinov2_vits14`。
- 数据预处理：`dataset\data_preprocess\mvtec.py`、`visa.py`、`btad.py`、`dtd.py` 负责生成 `meta.json`；`dataset\base.py` 根据 `meta.json` 读取图像、mask、类别和异常标签，并在训练时只抽正常样本。
- 数据集封装：`dataset\mvtec.py`、`visa.py`、`btad.py`、`dtd.py` 对应论文四个公开数据集；当前没有正式的 `button.py`，也没有 Quic、Tor、NSL、TON、dapt 这类网络数据集 loader。
- 视觉 tokenizer：`model\VarAD\dino_vision_tokenizer.py` 冻结 DINO/DINOv2，按 `hierarchies=[1,2,3]` 取多层输出，并实现 linear、resblock、lora adapter；`tokenizer_backbones\dino\model.py` 默认取第 4、8、12 层。
- 模型主体：`model\VarAD\anomaly_mamba.py` 中 `AnomalyMamba` 对每个层级建立一个 VSSM 分支，`cal_loss` 聚合层级损失，`cal_am` 生成异常图。
- 四向扫描与预测：`model\VarAD\vssm.py` 的 `CrossScan` 生成 4 个方向序列，`CrossMerge` 还原并融合；`BOS` 和 `pred_next_n` 实现预测位移。论文写的是预测步长 `m`，源码中更直接暴露为 token offset `pred_next_n`。
- 指标：`tool\metrics.py` 计算像素级/图像级 AUROC、max-F1、AP，并保留可选 PRO/AUPRO。
- 论文与源码差异：论文公式用预测 token 与原 token 的 L2 差异表述，源码实际用余弦相似度损失和余弦距离异常图，并对异常图做 `sigma=4` 高斯平滑。

## 12. 本篇精华
- VarAD 的关键贡献不是“又一个重建模型”，而是把异常定位改成正常视觉 token 的自回归可预测性问题。
- 高分辨率异常检测的难点在于小缺陷保真、全局上下文和计算复杂度三者同时满足；VarAD 用 DINO token + Mamba 线性序列建模试图同时解决。
- 多方向扫描是视觉自回归用于异常检测的必要补丁：否则单向预测天然缺少目标 token 后方的上下文。
- 排除最近邻 token 是一个重要设计，防止模型通过局部复制获得低训练误差，却学不到真正有用的全局正常模式。
- Adapter 的作用很大，说明通用视觉特征不能无代价迁移到工业异常检测，轻量域适配是必要环节。
- VarAD 的优势主要体现在像素级高分辨率定位；图像级检测仍不是绝对强项。
- 对网络安全研究的启发在于：用线性长序列模型学习正常上下文，再以预测误差做异常分数，可能比重建全输入更高效。

## 13. 建议精读路线
1. 先读 Introduction 的 HRIAD 动机，抓住为什么降采样和滑窗都不理想。
2. 再看 Fig. 1 和 Fig. 2，把 CNN bottleneck、Transformer bottleneck、VarAD token prediction 的差异画清楚。
3. 精读公式 1 到 10：adapter、多方向扫描、Mamba 预测、误差聚合、训练损失是方法骨架。
4. 重点看消融实验：方向、预测步长、adapter、层级和 backbone，这些决定方法是否真的成立。
5. 最后看复杂度和真实按钮实验，判断它是否具备工业部署意义。
6. 复现实验时先读 `main.py`、`trainer.py`、`anomaly_mamba.py`、`vssm.py`，再处理 DINO 本地路径、VMamba/selective-scan CUDA 扩展和 `DATA_ROOT`。

<!-- codex-cli-deep-read: complete -->
