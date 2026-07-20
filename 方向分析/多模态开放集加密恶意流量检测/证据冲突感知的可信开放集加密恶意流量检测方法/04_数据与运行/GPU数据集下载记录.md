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

## 后续处理要求

1. Mal_TLS2023 新建专用加载器，显式指定 `Label`，并在训练/验证/测试切分后拟合预处理器。
2. USTC 保留 `pcap_path`、`class_name`、`source_file` 和 `segment_id`，按源文件或会话分组切分。
3. 原始压缩包保留不删除，预处理结果写入各数据集的 `processed/` 子目录。
4. 不覆盖原始 PCAP/CSV，所有采样、流切分和特征提取参数写入 manifest。
