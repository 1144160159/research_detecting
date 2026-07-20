# EACR-APT

Evidence-Aligned APT Attack-Chain Reconstruction 的基础代码仓。

本地目录是代码与配置的唯一编辑源：

`F:\泉城实验室\二期\论文\异常检测\source\EACR-APT`

GPU 镜像：

`/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/source/EACR-APT`

数据、模型参数、运行目录和大型结果只保存在 GPU 服务器，不回传本地。远端项目根为：

`/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction`

## 当前代码

- `eacr_apt/schema.py`：统一事件与独立真值模式；
- `eacr_apt/alignment.py`：可解释的跨源候选对齐评分；
- `eacr_apt/reconstruct.py`：链评分与确定性 beam-search 下界；
- `configs/paths.remote.yaml`：远端数据/模型/运行路径；
- `configs/public_datasets.yaml`：公开数据来源、许可、选择范围和预期字节数；
- `scripts/collect_zenodo_dataset.py`：仅在 GPU 运行的 Zenodo 断点续传与校验采集器；
- `scripts/collect_zenodo_parallel.py`：大型 Zenodo 数据集的多文件并行断点续传与状态恢复；
- `scripts/collect_dataverse_dataset.py`：仅在 GPU 运行的 Dataverse 选择性采集器；
- `scripts/collect_dataverse_parallel.py`：大型 Dataverse 数据集的多文件并行断点续传；
- `scripts/collect_http_manifest.py`：固定 HTTP 清单/Apache 索引的并行断点续传、字节数校验与可选 SOCKS5 代理；
- `scripts/collect_s3_prefix.py`：公开 S3 prefix 的对象枚举、断点续传与完整性校验；
- `scripts/collect_mendeley_dataset.py`：Mendeley Data API 元数据解析、并行断点续传及 SHA-256/字节数双校验；
- `scripts/public_dataset_status.py`：汇总服务器侧采集进度与完整性状态；
- `scripts/launch_public_dataset_collection.sh`：在 GPU 按批次幂等启动或恢复公开数据队列；
- `scripts/check_local_policy.py`：阻止数据、权重和运行产物落入本地代码仓；
- `tests/`：最小模式、对齐、重构和本地存储策略测试。

## 本地检查

```powershell
D:\soft\Anaconda3\envs\py3.9\python.exe scripts\check_local_policy.py
D:\soft\Anaconda3\envs\py3.9\python.exe -m unittest discover -s tests -v
```

## GPU 公开数据队列

```bash
# 默认行为保持为首批；不会重复启动已完成或正在运行的采集器。
bash scripts/launch_public_dataset_collection.sh --batch first

# 第二批：Unraveled processed、PWNJUTSU JSON/reference、SAGA v2。
bash scripts/launch_public_dataset_collection.sh --batch second

# 第三批（web 为 third 的别名）：Linux-APT、APT Sandworm、Windows-APT 2025。
bash scripts/launch_public_dataset_collection.sh --batch third
```

第四批包含 AutoLabel 两个多源攻击场景、CAM-LDS 场景 3 PCAP、OTRF APT29、
NODLINK Simulated-Data、APTsDataset、StreamSpot、DAPT2020，以及 Splunk Attack Data
的元数据与相关 LFS 子集。SimuLand 单列为攻击场景生成器，不把代码仓库误记为预采集数据。
这一批来源和固定版本记录在 `configs/public_datasets.yaml`；仍以 GPU 端各目录的
`manifests/state.json` 或 `collection_state.json` 为完成判据。

`CICAPT-IIoT2024` 是 P0 级受控访问集：已使用获授权的真实身份完成官方登记，并由
注册采集器在 GPU 端取得完整 43 个文件（逻辑总量 15,223,742,261 字节）。完整版本包含
端点 provenance CSV、网络 PCAP/packet CSV，以及带攻击时间、PID 和类别的 `Attack_info`
真值。历史已有的两份 NetworkData CSV（合计 9,809,174,913 字节）通过符号链接复用，
没有复制第二份载荷。采集器不保存登记密码，身份信息也不写入 manifest；任何重取仍必须
从[官方数据页](https://www.unb.ca/cic/datasets/iiot-dataset-2024.html)进入
[注册表单](https://cicresearch.ca/IOTDataset/CICAPT-IIoT-Dataset/)，禁止伪造身份。

SAGA 等仅能经代理访问的来源可在启动前设置
`EACR_DATASET_PROXY=socks5h://127.0.0.1:9999`。代理认证信息不会写入
`collection_state.json`。HTTP 清单保存于 `configs/http_manifests/`；每次启动都会
校验文件数和 `expected_bytes`，官方索引漂移或 Google Drive 配额页都会导致失败，
不会被误记为完整数据。

## 同步到 GPU

```cmd
sync_to_gpu.cmd
```

同步只包含源码、配置、测试、文档和 requirements；随后在 GPU 的 Conda `py3.9` 环境执行语法检查与单元测试。详见 `SYNC_POLICY.md`。
