# GPU 数据集下载记录

记录日期：2026-07-13  
目标目录：`/opt/data/private/wangwt/ParkAttackKE/datasets`

## Mal_TLS2023

- 目录：`datasets/Mal_TLS2023`
- 来源：`https://github.com/gcx-Yuan/BoAu`
- 仓库提交：`b9f0d16de0f8fafbb9720f2cfca316186f50ae1b`
- 原始归档：`data/malicious_TLS.rar`，12,244,983字节
- 解压文件：`data/malicious_TLS.csv`，60,353,279字节
- 数据行数：92,034，不含表头
- 标签列：`Label`
- 类别数：23
- 类别组成：1类 `benign`，18个恶意软件/C2家族，4个 TLS 扫描工具类别，共22个非良性类别
- RAR SHA-256：`af8f4e4ba3cf9dbc39c24f874c197dcd56d9a322efaa74d9aa56dbb0754aa65b`
- CSV SHA-256：`a970379cd573ce371bdd308d8b45a0cb3c0b2c197db952373e8531b5606335bd`

类别包括：Banker、BuerLoader、Caphaw、CobaltStrike、Dridex、Drixed、Dynamer、Panda、PandaZeuS、Qakbot、Shifu、Tiggre、Tor、Totbrick、TrickBot、Upatre、Vawtrak、benign，以及 arachni、burpsuite、golistmero、nessus 等 TLS 扫描类别。

注意：原始 `Label` 位于特征表中部，后面仍有30个序列字段，不能沿用“最后一列为标签”的旧加载假设。

## USTC-TFC2016

- 目录：`datasets/USTC-TFC2016`
- 来源：`https://github.com/yungshenglu/USTC-TFC2016`
- 下载归档：`datasets/_downloads/USTC-TFC2016-master.zip`
- ZIP SHA-256：`dd6c5e32caf00d5d3ddaf965a063a5cf35c8cf01330e77691d6c936db523edf2`
- ZIP 完整性：已通过 `unzip -tq`
- 解压后规模：约4.0GB
- 标签：10类良性应用、10类恶意软件家族
- PCAP 文件数：良性14个、恶意10个
- PCAP 文件头校验：24个通过，异常文件0个
- 内部 7z 完整性：9个归档均通过测试并成功解压

良性类别：BitTorrent、FTP、Facetime、Gmail、MySQL、Outlook、Skype、SMB、Weibo、WorldOfWarcraft。SMB 与 Weibo 由多个 PCAP 分卷组成，实验时必须按应用类别归并，同时以文件编号作为分组切分依据。

恶意类别：Cridex、Geodo、Htbot、Miuref、Neris、Nsis-ay、Shifu、Tinba、Virut、Zeus。

## 解压工具

- 目录：`datasets/_tools/7zip`
- 版本：7-Zip 26.02 Linux x64
- 来源：`https://www.7-zip.org/download.html`
- 用途：解压 Mal_TLS2023 RAR 和 USTC 内部 7z 文件
- 安装方式：数据目录内独立工具，不修改服务器系统包

## 已有数据

目标目录中原先已存在 NF-UNSW-NB15-v2、NF-CSE-CIC-IDS2018-v2、CIC-ToN-IoT、CIC-BoT-IoT、Edge-IIoTset、CICIoT2023、CICIDS2017、CSE-CIC-IDS2018、CIC-DDoS2019、DoHBrw2020、CICAPT-IIoT2024 和 CICDarknet2020 等数据，未重复下载。

## CICIoT2022

- 目录：`datasets/cic/CIC_IOT_Dataset2022`
- 来源：CIC官方认证浏览页冻结的35项清单
- 已验证文件：35
- 已验证总字节：54,912,459,271
- 完整性：逐文件SHA复算通过；tar.gz结构、PCAP魔数、XLSX CRC和文本非空检查通过
- 残留状态：partial 0、symlink 0、错误0
- 当前边界：下载与文件结构准入；RoNeTC论文18类设备映射仍有3类双候选，不能据此声称完整作者原生复现

## PARROT2025_mitmproxy

- 目录：`datasets/PARROT2025_mitmproxy`
- 来源：Zenodo DOI `10.5281/zenodo.16368932`
- 归档：`PARROT2025_mitmproxy.zip`
- 大小：2,844,079,010字节
- MD5：`cbbef965211a3e6080c86114a007fa4f`
- SHA-256：`a086ce3c767338111e3bfb647dd30beb5e0c77f341842fc2aeba20b1633fa180`
- ZIP完整性：通过
- 内容：320个PCAP、320个SSL key文本，共80个Android应用、每应用4次启动流量
- 全量结构审计：80个应用均恰好4次抓取；320个PCAP与320份SSL key一一对应；缺失、孤立和危险路径均为0
- PCAP可解析性：全局头 `320/320` 通过；链路类型统一为Linux cooked v2（linktype 276），时间戳精度统一为微秒
- Inventory SHA-256：`21e044d83c58b17c7ddd5e271eb77ee667879b53d7a5e00ddac0fa99dad25522`
- 审计器/测试/结果SHA-256：`c3a24bab83bb49912e634d89ab08f58da738f71e148c2ee5ad44f407a140812c` / `8fe76a60880240ec1fe039d69f6ccb4a9d4e54de858dc98d54e212a19990adbb` / `7dc3bc2af2043dc244428be7e0bc035083ba1bcee1c6f1204aafa8ebfa2d8b8e`
- 测试：本地与GPU Python 3.9均 `4/4 PASS`
- 无解密canary协议：`results/parrot2025_no_decryption_canary_v1/protocol.json`，manifest SHA-256 `bd6e6546b6c26bf14ea8db84237c3a02180078a198dfb752c547b7f79178ec68`
- 无解密canary结果：4个跨应用PCAP、2,072包、2,028个IPv4/IPv6包、44个非IP包按协议跳过、解析异常0，共455条flow
- 特征契约：与 `configs/ustc_tfc2016_nfstream.json` 逐列一致的56个数值列；18个体量、15个时序、23个传输特征
- canary安全边界：SLL2仅转换链路封装；全零MAC；NFStream `n_dissections=0`、`decode_tunnels=false`；SSL key读取0、解密0、DPI 0
- canary结果/CSV SHA-256：`343fba1647c52042c293ecc8c38e9b67b032ac89a9e2a2a32ad11a6764b9f135` / `6fc814079aa36a008855015927a2e1bcbc21887c80c75215735286efb643a2a9`
- 正式良性安全设计：`results/parrot2025_external_benign_safety_v1/design_protocol.json`，manifest SHA-256 `333d4f14d44ec9859e9273ed765c1a587a4fc267a3b21d774ec7a0cc4897bca1`
- 全量无解密特征协议：`results/parrot2025_full_no_decryption_features_v1/protocol.json`，manifest/file SHA-256 `753253322208b11b4ea1faa9330993dd10238faad50e0715dcce4d96f62c40d3` / `cd4a11853b42da6989f6d677469839af28f158bfe15b49844268198a7e2adead`
- full分片契约：一个PCAP为一个不可拆分shard；临时目录完整写入后原子改名；断点续跑必须复验manifest自哈希、源member/CRC、56列CSV SHA和协议SHA
- full汇总契约：独立验证320成员全集、80应用各4次、无多余/缺失、列序、有限值、包计数和文件SHA后才写summary与完成标记
- full冻结状态：shard 0、summary 0、完成标记0、模型指标0；12项冻结检查通过，相关远端测试 `8/8 PASS`
- full调度：watcher PID `3331428` 等待strict-v4十门集成终审完成和连续5次资源空闲后，以 `nice=19`、idle I/O执行
- 正式执行状态：`execution_admission=false`、模型指标0；等待最终自有算法、完整部署模型包、全320捕获提取完成和域内良性参考重放先行冻结
- 标签边界：没有恶意攻击ground truth，不计恶意流量数据集、大类或细分类数量
- 实验角色：模型、特征和阈值全部冻结后的外部良性移动应用域偏移测试；只报告良性误报警率、恶意标签分配率、单列拒识率和风险分布漂移
- 禁止用途：阈值校准、未知恶意正样本、攻击家族覆盖和未知攻击检出率证据

## LSNM2024 与 CICDDoS2019 外部恶意确认准备度

- LSNM2024原始归档：`datasets/LSNM2024/LSNM2024_Dataset.zip`，223,508,263字节。
- CICDDoS2019原始归档：`datasets/cic/CICDDoS2019/CSVs/CSV-01-12.zip` 与 `CSV-03-11.zip`，分别为2,330,434,641和918,815,761字节。
- 三个ZIP的大小、成员数和中央目录SHA均与 `results/gpu_malicious_dataset_expansion_protocol_v1/protocol.json` 冻结身份一致。
- readiness auditor SHA：`80a7bc539af495c33d1a3facc4710e6d3d22f6daee01f66cde4ee1c8b2af794a`。
- 首快照：`results/strict_v4_krc_downstream_sota_design_v1/data_readiness.json`，canonical/file SHA为 `12a96ae2fed583e17aedff213bf071b9ff52cc185b4eeeeb78351a65dc8795f6` / `9006d0501ee676908bc578512006ab620b6679431550c8725dd2beca68ccb9a7`。
- 当前 `raw_data_available=true`：两套恶意原始数据与PARROT原始/无解密特征协议均匹配。
- 当前 `ready_for_downstream_execution=false`：`datasets/caeos_external_open_set_v1` 尚未生成，full admission与seed `223/227/229` prepared manifest均未完成。
- 全量admission于2026-07-26 05:04 UTC以idle I/O、nice15启动，PID `1902838`；只扫描标签、group、特征与源SHA，不训练模型或读取模型效果。
- preparation watcher PID `1174214` 等待admission；只有全量准入阳性才生成每数据集三种子CSV、sidecar、manifest与完成标记。
- LSNM2024在外部确认中覆盖多类攻击；CICDDoS2019只提供DDoS家族窄域证据，不能将其扩写为一般恶意流量覆盖。
- 首次full admission把SQLite精确group store置于NFS，05:11 UTC在首个PRAGMA处以 `database is locked` 失败；failure log SHA为 `4911398458b54eb7783d8b6cc00974f975ef726512928ba0026e0ee4ba2d5f35`，未生成audit或marker。
- 零结果恢复amendment：`results/gpu_dataset_full_admission_audit_v1/local_sqlite_amendment_v1.json`，canonical/file SHA为 `e8448f152d8d9d586a65a63404d890fca24593c0a2dd5e1775a8b1a268ad1627` / `72af20a30851db3c9be56cdccea4dee3df94e93931f9b6b5dc7f4c477c26cdaf`。
- 恢复仅将临时SQLite工作目录改为本地overlay `/tmp/wangwt_gpu_dataset_full_admission_v1_20260726`；原始文件、扫描实现、配置、科学门和权威输出根均未变化。
- 恢复扫描PID `2152681` 已确认持续计算并写出成员缓存；最终admission状态仍需等待全量audit和passed marker。
- 恢复扫描最终完成；v1 audit文件SHA为 `840d9a3c3710c8ecefedb1c6ec0e8f9f98a1685fd9135c5cba9b920ae50805a5`。LSNM2024为4,543,916行、16标签并通过；CICDDoS2019为70,427,637行，仅旧词表的unexpected-label门失败，故v1不生成passed marker，原watcher写入blocked。
- CICDDoS2019全扫描标签证据：`01-12/UDPLag.csv` 含 `UDP-lag` 366,461行和WebDDoS 439行；`03-11/UDPLag.csv` 含UDPLag 1,873行。WebDDoS有439个group，满足保留门。
- 标签调和protocol canonical/file：`2f4a5ccb3bb8974692a902cdf461809c9a32e5786bf2d382acb9f6cf98a9037d` / `0c835beec752b8ab548e5b0b9131d16d404ea34ca3c65b7204ff0adf22cad3db`。只允许成员绑定的 `UDP-lag -> UDPLag` 并保留WebDDoS为第17个攻击家族。
- v2准入audit canonical/file：`6ec8c3be0fe2293a21e457cc9f9f70a3eb7a4d94dec9a981014ff98a0afc9436` / `2d9b67b0ef6719b31b6846dc864d2a67549fc3860ec036a9b531a286a029bbc6`。三个源文件完整SHA未变，CICDDoS总行数保持70,427,637，UDPLag调和后368,334行/组、WebDDoS 439行/组，17家族全部通过。
- v2规范化目录：`datasets/caeos_external_open_set_v2`；准备协议canonical/file为 `0736101ea8bd838bf824f8947f80b7140c79d7f3015dffeb245524502497f6f3` / `a37bee2a1281aaf2f2ac4e2d74ad6e49277d08585b2f5c9a7906cea431ee3d26`。
- seed `223/227/229` 准备任务PID `4072053` 于06:01 UTC启动，当前从LSNM2024开始；任何CSV、sidecar、manifest和summary均需完整SHA门后才计完成。
- v2准备中readiness snapshot canonical/file：`9c38ae25e8d5829f280a5106ae785432a60c3c3dfae485ba76dac42892f859f5` / `1e08669ed9a417936ab6614fcbcb851a4a1e2ccf5ce5b633228c3fb20209f9bf`。当前调和准入通过但三种子与summary未完成，`ready_for_downstream_execution=false`。
- LSNM2024 v2三种子已完成：seed223/227/229分别31,222/31,335/31,204行，均覆盖normal与15攻击家族共16标签；manifest文件SHA为 `54655fd2f45627b762ed7c80f78b8d5829d53d754da0ea03d2b140da711477ee`。
- LSNM完成快照canonical/file：`ebfa49a72d8d1946571aacaf475834968942f7a78f764f8acfbba27e6aee5a72` / `3aec630cccd2d088a691cbc6442ce97bfb4156cf024b2ebb102e0fe29ef600ac`；三个seed的CSV SHA、sidecar内容、16标签、v2 provenance与完成标记全部通过。
- 当前runner已进入CICDDoS2019准备；在CIC三种子、总summary与完成标记形成前，整体ready仍为false。
- CICDDoS2019 v2三种子已完成：seed223/227/229均为68,439行、18标签；manifest文件SHA为 `0cbf2219a719079ec4c525accd203e3776b9ade2af63c5d07f6404e8fb76f591`。
- 三个CIC正式CSV独立逐行扫描一致：BENIGN、UDPLag及其余15个常规攻击标签各4,000行，WebDDoS各439行；`UDP-lag` 不存在，UDPLag与WebDDoS均存在。
- v2总summary：`results/gpu_external_dataset_preparation_v2/summary.json`，文件SHA为 `d52899abfd73dcb44a3a2cc7783a09c744df7173272ad103daff5fce2d5b8376`，`status=complete`、`ready_for_frozen_external_experiments=true`，总完成标记存在。
- 最终readiness：`results/strict_v4_krc_downstream_sota_design_v1/data_readiness_v2_complete.json`，canonical/file SHA为 `ba0240341364f404e1030d3f6c4455c01288bbdb4f8a84b1b98d32a60696e68b` / `506bdef1cdfda9d69d2395f85764b8bd48493d92d0d682c75e3f499e3db9a18e`。
- 最终五项检查全部通过，`raw_data_available=true`、`ready_for_downstream_execution=true`。这仅表示数据可供冻结外部实验读取，不代表模型效果或KRC选择已经通过。
- 外部逐攻击家族留一任务宇宙：LSNM 15家族 + CICDDoS 17家族，共32家族；三个种子合计96场景/每算法。

## 后续处理要求

1. Mal_TLS2023 新建专用加载器，显式指定 `Label`，并在训练/验证/测试切分后拟合预处理器。
2. USTC 保留 `pcap_path`、`class_name`、`source_file` 和 `segment_id`，按源文件或会话分组切分。
3. 原始压缩包保留不删除，预处理结果写入各数据集的 `processed/` 子目录。
4. 不覆盖原始 PCAP/CSV，所有采样、流切分和特征提取参数写入 manifest。
5. PARROT2025在冻结评估前不得进入训练、验证、阈值选择或特征选择；同一PCAP派生样本必须保留capture级group。
