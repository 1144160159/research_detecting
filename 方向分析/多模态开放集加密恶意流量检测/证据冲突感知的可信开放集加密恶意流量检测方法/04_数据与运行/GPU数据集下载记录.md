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

## 后续处理要求

1. Mal_TLS2023 新建专用加载器，显式指定 `Label`，并在训练/验证/测试切分后拟合预处理器。
2. USTC 保留 `pcap_path`、`class_name`、`source_file` 和 `segment_id`，按源文件或会话分组切分。
3. 原始压缩包保留不删除，预处理结果写入各数据集的 `processed/` 子目录。
4. 不覆盖原始 PCAP/CSV，所有采样、流切分和特征提取参数写入 manifest。
5. PARROT2025在冻结评估前不得进入训练、验证、阈值选择或特征选择；同一PCAP派生样本必须保留capture级group。
