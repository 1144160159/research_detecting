# A01--A10 有界算法资格 Campaign

## 结论与当前状态

本次新增的是一条独立、可恢复、默认只读的 A01--A10 统一资格链，不是一次新的生产发布。它解决旧证据协议不一致、A01--A08 缺少 normal/fallback 配对指标、A09/A10 指标未绑定结果哈希的问题。

当前状态为 `deferred_due_active_caeos_workload`。GPU 主机上存在正在运行的 CAEOS 正式处理任务；因此本轮只允许同步小型代码、解析合同、生成 dry-run 计划以及生成 legacy 发现清单，不启动任何正式算法评估。该状态不是算法 campaign 被永久阻断，而是为避免干扰既有正式任务而延期。

旧证据在 2026-08-13 的远端只读检查中为 10/10 可发现并可计算 SHA-256，但这些文件只属于 `legacy_discovery_only`：

- 它们使用的输入分组、重复结构或 normal/fallback 协议不完全一致。
- 它们不能增加 campaign 已完成候选数，不能证明 A09 在全部十个候选上最优。
- A07--A10 当时的远端 SHA-256 分别为 `1066e4aec76d408b3f6ddc1d6ce9a54ab50ea9236f72478179b1d88b17a0acd4`、`c83e15bab22a481f66494ef6cc9b665c6e754b3c1c095bae24331c34d73bf740`、`0af2b441ab9790bbdbeb40fb65b3ee5eab7666f70c2ebb7f5e42953f0bf6f186`、`911899c3ad96e56465751a3d53a8af294188cf760cb7c0f258aeae0d213934af`。这些值仅用于发现审计，不进入资格判断。

## 冻结合同

合同 `configs/algorithm_qualification_campaign_v1.json` 绑定：

- 当前 `configs/algorithm_search_rc1.json` 的 SHA-256：`8ee9f2f0b4758e7d4a8372d906e156ecc1b58198f0cc7077c4b9dd22e1a5efd4`；
- 数据角色清单、训练/评估实现和资源预算实现；
- campaign 核心模块、prepare/finalize CLI 和前台 runner 的实际 SHA-256；
- GPU 代码根与结果根，禁止把正式结果写到本地代码目录。

合同本身当前 SHA-256 为 `1d6a48f844e944a94324806239723f9688b81f87fa59c5e805e5f61b9cabce6b`。任何被绑定文件发生字节变化都会使预检失败关闭。

## 统一比较协议

搜索上限和实际候选数均为 10，候选必须恰好为 A01--A10，并与 `algorithm_search_rc1.json` 中五个算法维度逐项一致。每个候选执行：

- `normal` 与 `fallback` 两种模式；
- 每种模式固定种子 `7, 11, 19`，共 3 次重复；
- 固定 `batch_size=512`、`budget_us=5000`、预算安全系数 `0.5`；
- 固定 `estimators=200`、`n_jobs=8` 及训练/测试包和流数量上限；
- 仅使用 2015-02-17 的 shard7--9 作为 fresh evaluation；
- A01--A08 将 2015-01-22 shard1--3 全部作为校准数据，A09/A10 将 shard1--2 用于适配、shard3 用于校准，均不得进入 fresh evaluation。

因此正式作业量为 `10 candidates x 2 modes x 3 seeds = 60` 个独立评估单元。runner 一次只执行一个评估单元；单元内部最多使用 8 个 sklearn worker，主要消耗 CPU 和 PCAP 读取带宽。A6000 空闲不代表适合立即执行，因为当前候选主要是 CPU ExtraTrees/Logistic。准确总耗时必须在 CAEOS 任务结束后通过一个经批准的单元实测估算，当前不凭旧运行时长推断。

## 可恢复与失败关闭语义

`scripts/run_algorithm_qualification_campaign.sh` 默认只打印计划。正式执行必须同时满足三个精确授权条件，并且只能在合同绑定的 GPU 代码根运行：

```bash
export HFT_ALGORITHM_CAMPAIGN_EXECUTE=YES
export HFT_ALGORITHM_CAMPAIGN_AUTHORIZATION=APPROVED_BOUNDED_A01_A10_QUALIFICATION
export HFT_ALGORITHM_CAMPAIGN_TRUSTED_CONTRACT_SHA256=1d6a48f844e944a94324806239723f9688b81f87fa59c5e805e5f61b9cabce6b
export HFT_ALGORITHM_CAMPAIGN_RUN_ID=algorithm_qualification_YYYYMMDDTHHMMSSZ
bash scripts/run_algorithm_qualification_campaign.sh
```

上面的正式入口仅供 CAEOS 任务结束并重新授权后执行，本轮不得运行。恢复时必须复用同一个 `HFT_ALGORITHM_CAMPAIGN_RUN_ID`。

runner 使用 campaign 级 `flock` 防止并发重复训练；每个候选、模式、种子保存独立 JSON 与 SHA-256 checkpoint；只有严格 JSON 可解析且 checkpoint 校验成功才跳过；失败或断线后重新运行会从首个不完整单元继续。计划在恢复时按字节重放检查，输入文件在 finalize 时重新计算大小和哈希。状态、作业状态、清单和 receipt 均通过临时文件后原子替换。runner 始终以前台进程运行，不在脚本内部用 `nohup`、`systemd-run` 或 `disown` 冒充成功；如需托管，应由调用方显式配置且仍以最终 receipt 为准。

锁路径固定为 GPU 本机 `/tmp/hft_algorithm_campaign_locks`，不接受环境覆盖；锁根和锁文件均拒绝 NFS、符号链接、错误 owner/mode 与多硬链接。runner 先以非截断 FD 获取 `flock`，复核 FD 与路径 inode 一致后才写 owner 元数据。真实双进程夹具验证竞争者返回 98 且不会截断持有者记录。该互斥只覆盖一台 GPU 主机，不能替代跨主机调度器。

finalizer 同时修复了正式结果目录的精确匹配：runner 和 finalizer 现在都使用 `${result_prefix}_${run_tag}`，不再用带尾随下划线的模糊 glob。输入 SHA manifest 必须与严格解析的 training/holdout 两份 manifest 所引用的 27 个路径完全相等；缺项、多项、替换项均拒绝。plan、manifest、summary 与 raw result 统一通过拒绝 symlink、前后 inode/size/mtime 不变的单 FD 稳定读取，证据大小、SHA 和 JSON 从同一份 bytes 派生。

上述最终冻结 SHA-256：`algorithm_campaign.py=b7413a64aeacf4a4cda9eea73ad4c1aba1b56a6bd6e6875e7c308dfa434f691c`；runner `d15911a3021442a59dafdae2a192ac47d6d05da180601f11b03c50628d17358c`；campaign tests `f0c3f849551e0472f755359b50613a7dfd48d60b69bd9676d48d925d8520d081`。本地 campaign 回归为 31/31。

2026-08-14 首次正式入口在任何候选运行前发现：campaign 结果根位于不提供 POSIX advisory lock 的 NFS，原 `${campaign_root}/campaign.lock` 返回 `flock: No locks available`。失败轮 `algorithm_qualification_20260813T194500Z_formal_r1` 作为入口失败证据保留，不复用；它没有生成 plan、input manifest 或候选结果，不计入 60 单元实验。

锁根现固定为 GPU 本机 `/tmp/hft_algorithm_campaign_locks`，不允许环境变量改写。runner 拒绝 `/tmp` 或锁根为符号链接、锁根位于 NFS、锁根不是当前有效 UID 所有的 `0700` 目录，以及锁文件为符号链接、非普通文件、多硬链接、非当前有效 UID 所有或权限不是 `0600`。锁文件以 `noclobber` 创建、以不截断方式打开，取得 `flock` 后再次核对文件描述符与路径的设备号/inode，最后才经已锁定的文件描述符截断并写入 PID、campaign root 和合同 SHA。因此竞争者不会在拿到锁之前擦除当前 owner 元数据。

该锁只提供同一 GPU 主机内的互斥，不是跨主机分布式锁。结果、checkpoint 与证据仍只写合同绑定的 campaign 根；正式重跑必须使用新的 run ID，且不得把同一 campaign 结果根同时挂载到另一台主机执行。

锁安全回归新增 3 项，连同既有 runner 合同测试为 `7/7` 通过。物理主机 `10.0.5.8` 已以标准输入对修改后 runner 执行 `bash -n`，返回 `0`；同时只读确认 `/tmp` 为 `tmpfs`、不是符号链接，且 `flock`、`truncate`、GNU `stat` 可用。完整 campaign 测试在并行修改 `algorithm_campaign.py` 后按合同哈希失败关闭，需等该文件冻结并统一刷新合同后再作为整套通过证据；本锁修复没有把这种失配改写为成功。

## 输出与信任边界

正式运行的原始结果、输入哈希清单、日志和模型相关运行产物只保存在 GPU 的 `algorithm_qualification_campaigns/<campaign_run_id>/`。本地只保留代码、合同、测试和文档。

finalize 仅在 60/60 单元、结果 SHA、输入 SHA、代码 SHA、候选参数、模式/种子/分组及指标重算全部一致时生成十个小型候选 receipt、campaign receipt 和 `suggested_algorithm_search_projection.json`。建议投影不会修改 `algorithm_search_rc1.json`。即使统一 campaign 证明某个候选是受约束算法 practical optimum，也只表示 `algorithm_only_practical_optimum_proven=true`；生产联合最优和最终 Pareto 接入仍保持 false，必须另行审核抓包、部署和端到端资源证据。

## 当前只读预检命令

本地：

```powershell
$env:PYTHONPATH='.'
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest -v tests.test_algorithm_campaign
```

GPU 默认 dry-run（不得设置三个执行授权变量）：

```bash
cd /opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS
unset HFT_ALGORITHM_CAMPAIGN_EXECUTE HFT_ALGORITHM_CAMPAIGN_AUTHORIZATION HFT_ALGORITHM_CAMPAIGN_TRUSTED_CONTRACT_SHA256
PYTHONDONTWRITEBYTECODE=1 python scripts/prepare_algorithm_campaign.py \
  --campaign-run-id gpu_readonly_preflight_20260813
bash -n scripts/run_algorithm_qualification_campaign.sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. bash scripts/run_algorithm_qualification_campaign.sh
```

只读扫描旧 summary 并把小型机器可读 manifest 写入 `/tmp`：

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/prepare_algorithm_campaign.py \
  --campaign-run-id gpu_readonly_preflight_20260813 \
  --legacy-evidence-manifest /tmp/hft_algorithm_legacy_discovery_20260813.json
```

该 manifest 中每条记录都必须保持 `protocol_comparable=false`、`counts_toward_campaign=false`，不能把 legacy hash 误当作 campaign 资格证据。

## 2026-08-13 GPU 预检回执

本轮已把本文件所列新增代码、合同、测试和文档同步到合同代码根，并对合同的 20 个绑定 artifact 一次性核对存在性和 SHA-256。19/20 已与合同一致；唯一缺失的 `hft_mgbs/algorithm_optimality.py` 经本地 SHA `814cc737c01e5f73c3cf8f39815a83ccbea13d90f3e82a8c722a4d9a6d91d52c` 校验后以临时文件上传并原子就位。

随后默认 dry-run 在合同解析阶段继续失败关闭：远端 `configs/algorithm_search_rc1.json` 的实际 SHA-256 为 `b629ec3215ecd5b80b2eaeafe1cd5eb1f795c29686f4a1f52982eb772ef3b646`，与合同绑定的本地当前 SHA-256 `8ee9f2f0b4758e7d4a8372d906e156ecc1b58198f0cc7077c4b9dd22e1a5efd4` 不一致。回执错误为 `CampaignValidationError:algorithm search hash mismatch`；计划保持 `execution_authorized=false`，没有创建或启动 60 个评估单元，也没有生成 campaign 资格 receipt。

为在限时内保持最小变更并避免影响 CAEOS，本轮到此停止继续同步。恢复前需由统一发布方先决定以本地严格 JSON 版本覆盖远端搜索文件，或重新审核远端版本并生成新的合同；在这个一致性问题解决前，正式 campaign 必须保持延期且失败关闭。

## 2026-08-14 直接入口修复

本地复核发现 `scripts/prepare_algorithm_campaign.py` 在导入 `hft_mgbs` 之前尚未把项目根加入 `sys.path`，所以从项目根直接执行且未设置 `PYTHONPATH` 时会在任何计划校验前以 `ModuleNotFoundError` 退出。入口现先根据脚本绝对路径确定项目根，再导入项目模块；测试子进程显式删除 `PYTHONPATH` 后验证 dry-run 仍成功。该修改只影响模块查找，不改变候选、分组、预算、模式、种子或授权语义。

回归结果：campaign 合同测试 `25/25` 通过；无 `PYTHONPATH` 的直接 CLI 返回 `0`，生成 `candidate_count=10`、`job_count=10` 的计划，每个候选仍包含 normal/fallback 各三个种子，即 `60` 个独立评估单元；`execution_authorized=false`、`algorithm_only_qualification_complete=false`、`final_pareto_ingestion_allowed=false`。修复后的 prepare SHA-256 为 `57e15ce255cc5174fae827b3daefbb2915ebe785638e33720ef719181e72c63a`，合同已按该实际哈希重新冻结为 `0980bde18d354861d34c66d76d4a7ad5169a2e0c23a05445dbbeb2e00f215805`。

四个漂移文件随后以逐文件临时上传、SHA-256 校验、旧字节备份和原子替换方式同步到 GPU 合同代码根：`algorithm_search_rc1.json=8ee9f2f0...`、合同 `0980bde1...`、prepare `57e15ce2...`、测试 `376b98ea...`。GPU 上清除 `PYTHONPATH` 后的 prepare dry-run 已实际生成 10 候选计划，仍为未授权且 0/60 执行；GPU campaign 测试 `25/25` 通过。同步没有启动训练。

正式执行仍有两个独立硬阻断。第一，GPU 正在运行 8 个约 98% CPU 的 CAEOS 重复审计 worker，不能并发启动 CPU/PCAP 密集的算法 campaign。第二，训练 manifest 引用的 18 个 USTC-TFC2016 原始 PCAP 在本地、GPU 用户根和物理机用户根均为 `0/18` 个可信副本；完整冻结输入应为 27 项（2 个 manifest、18 个 USTC PCAP、6 个 UNSW PCAP、1 个 GT CSV）。任何派生缓存、来源不明的审计产物或符号链接都不得替代原始输入。
