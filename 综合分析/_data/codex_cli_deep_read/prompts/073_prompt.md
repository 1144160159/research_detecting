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
# [073] CADE: Detecting and Explaining Concept Drift Samples for Security Applications
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
编号：073
题名：CADE: Detecting and Explaining Concept Drift Samples for Security Applications
年份：2021
DOI：无
来源：30th USENIX Security Symposium
PDF：paper/CADE%20-%20Detecting%20and%20Explaining%20Concept%20Drift%20Samples%20for%20Security%20Applications.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：无
相关性：弱相关，分数 
已有代码状态：已下载；CADE -> source\CADE

正文包信息：
- 正文来源：未找到全文缓存
- 原始字符数：0
- 本次发送字符数：0
- 是否截断：False

代码包：
- 仓库：CADE
  - URL：https://github.com/whyisyoung/CADE
  - 状态：downloaded
  - 本地目录：source\CADE
  - 顶层结构：.gitignore、IDS_data_preprocess/、LICENSE、README.md、USENIX_21_drifting_Supplementary_Materials.pdf、average_all_detection_results.py、cade/、data/、evaluate_explanation_by_distance.py、fig/、main.py、models/、pure_ae_fig/、pure_ae_reports/、reports/、requirements-tensorflow-cpu.txt、run_boundary_exp_drebin_fakedoc.sh、run_boundary_exp_ids_infiltration.sh、run_cade_exp_drebin_fakedoc.sh、run_cade_exp_ids_infiltration.sh、run_drebin_cade.sh、run_drebin_pure_ae.sh、run_ids_cade.sh、run_ids_pure_ae.sh、setup.py
  - 主要语言：Python:19、Shell:9
  - README 标题：CADE: Contrastive Autoencoder for Drifting detection and Explanation、1. Installation、you may also try pyenv and virtualenv to create the virtual environment, here we use Anaconda、2. Configuration、3. Usage、4. Examples、4.1 Drift detection、After the shell script finished running、0 means using CADE, while 1 means using Vanilla AE、After the shell script finished running
  - README 运行线索：Python 3.6.5 or 3.6.8 virtual environment (other Python 3.6 or above versions might also work but didn't test).；bash pip install -r requirements-tensorflow-cpu.txt；python setup.py install；bash module load cuda-toolkit/9.0 # other versions might also work but didn't test；conda conda create -n cade-gpu python=3.6.8；conda activate cade-gpu；pip install scipy==1.3.3；pip install numpy==1.16.1
  - 关键文件：{"依赖环境": ["requirements-tensorflow-cpu.txt", "setup.py"], "推理/演示入口": ["main.py", "run_boundary_exp_drebin_fakedoc.sh", "run_boundary_exp_ids_infiltration.sh", "run_cade_exp_drebin_fakedoc.sh", "run_cade_exp_ids_infiltration.sh", "run_drebin_cade.sh", "run_drebin_pure_ae.sh", "run_ids_cade.sh", "run_ids_pure_ae.sh"], "评估/测试入口": ["evaluate_explanation_by_distance.py", "cade/evaluate.py"], "配置文件": ["cade/config.py"]}
  - 数据集线索：ton、tor

论文正文包开始：
<<<PAPER_TEXT

PAPER_TEXT
