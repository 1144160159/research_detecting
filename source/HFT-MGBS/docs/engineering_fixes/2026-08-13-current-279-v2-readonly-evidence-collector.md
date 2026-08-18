# current-hardware 2.79 v2 只读证据采集与严格归一化

## 原问题

现有 raw-run adapter 能严格验证 v2 artifact，但不负责采集。第一次完成的
`normal-r1b` 只有 runner 原始文件和汇总 pipeline JSON，adapter 仍缺少 11 项：

1. `model`；
2. `runtime_manifest`；
3. `service_source`；
4. `engine_source`；
5. `service_launcher`；
6. `identity_receipt`；
7. `window_observations`；
8. `physical_resources`；
9. `service_resources`；
10. `quality_labels`；
11. `quality_predictions`。

其中部分文件可以从当前真实服务中只读冻结；窗口、双节点资源、质量和 fallback
则必须在正式运行期间形成。不能把运行总计数、汇总 P99、`mpstat` 总表或目录名扩展成
逐窗、逐样本和运行身份。

## 三阶段工具

新增 `scripts/current_hardware_279_v2_evidence.py`，固定为三个显式阶段。

### prepare

`prepare` 只读复制当前已经存在的 A09 模型、runtime manifest、服务源码、numpy engine
源码和启动器到新的冻结目录。复制后重新计算 SHA-256，并要求 runtime manifest 的
`model_sha256`、`service_source_sha256`、`numpy_engine_source_sha256`、`launcher_sha256`
逐项等于冻结文件。manifest 还必须包含真实 PID/start ticks、Python exe、cwd 和 cmdline SHA。

manifest 只提供待核对声明，不能成为运行身份事实。service collect 会从 `/proc/<pid>` 现场读取
PID/start ticks、exe、cwd、cmdline、argv/PYTHONPATH，从实际 argv 定位 model，从实际模块搜索路径
定位 `gpu_service.py` 与 numpy engine；开始和结束各自重新计算 SHA，并与 health 返回的 model
路径/SHA/inference engine、50051 listener owner 以及 prepare 冻结 SHA 交叉绑定。任一处漂移都会阻断
`identity_receipt`。

该阶段不启动、停止或重启 GPU 服务。

```bash
python3 scripts/current_hardware_279_v2_evidence.py prepare \
  --output-dir /tmp/hft-279-v2/prepare-normal-r1 \
  --campaign-id current-hardware-279-v2 \
  --candidate-id tpacket-v3-current-hardware \
  --backend tpacket_v3 --mode normal --repeat-index 1 \
  --runtime-manifest /opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/runs/split_deployment/runtime_manifest.json \
  --model /opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/models/a09/rc1/a09_bundle.joblib \
  --service-source /opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS/hft_mgbs/gpu_service.py \
  --engine-source /opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS/hft_mgbs/a09_numpy_inference.py \
  --service-launcher /opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS/scripts/start_gpu_service.sh
```

### collect

`collect` 每个节点独立运行，在 realtime 整秒边界形成 `N+1` 个 snapshot，供 finalize
派生 `N` 个一秒区间。物理节点采集 host CPU/memory、pktgen 累计包、NIC 累计 ucast/discard、
pipeline PID/start ticks/exe/cmdline、`kpktgend_*` PID/start ticks、物理机到 GPU 的 health，
以及 50052 listener/ESTABLISHED owner。GPU 节点采集 host CPU/memory、manifest PID
完整进程树累计 CPU/RSS、50051 owner、本机 health、`nvidia-smi` 系统 GPU 状态与 compute-app
PID/显存归属。

物理节点必须显式给出非 loopback GPU host，避免把 localhost 检查冒充跨机可达。
每次采集只读 `/proc`、`/sys`、`ethtool -S`、pktgen 状态、`ss`、health TCP 和
`nvidia-smi`；不加载模块、不改变 NIC/IRQ、不启停服务、不启动流量。

双节点时钟不以容器内存在 NTP daemon 为前提。物理节点必须用 chrony/systemd-timesyncd/ntpq
给出独立 UTC offset（上限 50 ms）；GPU Kubernetes 容器允许没有 chronyd/systemd。两端 collector
另外通过只读 nonce clock probe，在开始和结束分别记录 client realtime/monotonic 前后界、server
realtime/monotonic、RTT 与 offset interval；offset interval 必须包含 0（双端不确定区间重叠），
且最大绝对 offset 界必须不超过 250 ms。最终窗口还要求
同 epoch 边界的实测采样时刻差不超过 100 ms。推荐使用已经存在连通性的 GPU→物理方向：先启动
物理 collector 的临时 50053 probe server，再启动 GPU collector client。probe 只回答时间和 nonce，
不控制服务或流量，结束时关闭。

```bash
# 物理机：先启动，26 秒用于覆盖 GPU collector 启动偏移和完整正式窗
python3 scripts/current_hardware_279_v2_evidence.py collect \
  --role physical --duration-seconds 26 \
  --output /tmp/hft-279-v2/physical-normal-r1.json \
  --interface ens8f0 \
  --pipeline-identity-file <run>/pipeline_process_identity.env \
  --gpu-health-host 10.0.5.103 --gpu-health-port 50051 --reverse-port 50052 \
  --clock-probe-listen-host 0.0.0.0 --clock-probe-port 50053 \
  --pktgen-device /proc/net/pktgen/ens8f1@0 \
  --pktgen-device /proc/net/pktgen/ens8f1@1

# GPU Kubernetes 容器：随后启动，主动探测已可达的物理机
python3 scripts/current_hardware_279_v2_evidence.py collect \
  --role service --duration-seconds 22 \
  --output /tmp/hft-279-v2/service-normal-r1.json \
  --runtime-manifest /opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/runs/split_deployment/runtime_manifest.json \
  --clock-probe-host 10.0.5.8 --clock-probe-port 50053
```

实际 8 队列运行应传入全部 8 个 `--pktgen-device`。collect 本身不会等待 runner
特定事件；正式编排必须在 generator 前启动双节点 collector，使选出的 15 个窗口均有
两端边界覆盖。每端必须且只能选择 clock-probe client/server 之一；缺少两次有效跨机 probe、
offset 界超限、单个边界采样耗时超过 250 ms、物理 NTP 证据缺失或采集 receipt 自带任何
`errors`，finalize 均 fail closed。

### finalize

`finalize` 只在以下原始证据同时存在时写 adapter 可消费 artifact：

- pipeline 的逐秒累计 `counter_observations`；
- pipeline 的 `epoch_second_counts`，且每个正式秒必须等于同秒
  `packets_received` 累计边界差；
- NIC/pktgen 的同 epoch 累计边界；
- pipeline 的 `raw_latency_sample_receipts`，且每个 `source_id` 唯一、timestamp/window 一致；
- 每窗 packet/flow/kernel-feature/e2e 至少 1,000 个原始样本，GPU batch 至少 100 个；
- 15 个严格连续完整窗口；
- 双节点每个相同 epoch 至少一条可归属资源样本；
- 物理 UTC 同步证据、双端 start/end clock-probe offset interval 与逐边界跨机偏差；
- hash-bound GPU runtime/service/process/listener/health 与物理 50052 链；
- 独立 official/manual labels 和逐样本 predictions；
- fallback 模式还必须给出按顺序的真实故障注入完整事件链。

任何缺项只进入 `evidence_gaps`/`normalization_gaps`，不会创建对应 staged artifact；CLI
返回 2。完整时 `adapter_arguments` 可直接传给既有
`compose_current_hardware_279_raw_run_v2.py`。

```bash
python3 scripts/current_hardware_279_v2_evidence.py finalize \
  --output-dir /tmp/hft-279-v2/final-normal-r1 \
  --evidence-dir <runner-evidence-dir> \
  --campaign-id current-hardware-279-v2 \
  --candidate-id tpacket-v3-current-hardware \
  --backend tpacket_v3 --mode normal --repeat-index 1 \
  --prepare-receipt /tmp/hft-279-v2/prepare-normal-r1/prepare_receipt.json \
  --physical-raw /tmp/hft-279-v2/physical-normal-r1.json \
  --service-raw /tmp/hft-279-v2/service-normal-r1.json \
  --quality-labels <official-or-independent-manual-labels.json> \
  --quality-predictions <per-sample-predictions.json>
```

## GPU 归属与质量边界

服务是 CPU ExtraTrees/numpy 时，只有 `nvidia-smi --query-compute-apps` 证明服务进程树
没有 GPU compute process，才写 service `gpu_fraction=0`、`gpu_memory_fraction=0`；同时保留
系统 GPU utilization。若服务 PID 出现在 GPU apps 中，则必须由 `nvidia-smi pmon` 得到
进程 SM 利用率；只有系统 GPU 总利用率而没有进程归属时输出 gap，不能把系统值归给服务。

quality labels 只接受 `official_labels` 或 `independent_manual_labels`，必须
`synthetic=false`、`independent_holdout=true`。predictions 必须逐样本且同时绑定 labels、
冻结 model 和 runtime manifest SHA。工具不读取现有汇总质量结果来合成两份文件。

最小 labels schema（省略外层格式化空白）是：

```json
{
  "schema_version": 1,
  "scope": "hft_mgbs_independent_ground_truth_labels_v1",
  "source_kind": "official_labels",
  "synthetic": false,
  "independent_holdout": true,
  "source_artifact_path": "<collector可只读访问的官方/人工标签源文件>",
  "source_artifact_sha256": "<官方/人工标签源文件SHA-256>",
  "source_record_locator": "<可复查的数据集/分区/记录定位>",
  "records": [
    {"sample_id": "<稳定ID>", "label": 0, "group": "<独立组>", "event_id": "<真实事件ID>"}
  ]
}
```

最小 predictions schema 是：

```json
{
  "schema_version": 1,
  "scope": "hft_mgbs_independent_predictions_v1",
  "synthetic": false,
  "generation_kind": "frozen_model_inference_on_independent_holdout",
  "source_artifact_sha256": "<与labels相同的官方/人工标签源SHA-256>",
  "labels_sha256": "<上述labels文件SHA-256>",
  "model_sha256": "<prepare冻结模型SHA-256>",
  "runtime_manifest_sha256": "<prepare冻结runtime manifest SHA-256>",
  "records": [
    {"sample_id": "<与labels一一对应>", "prediction": 0, "score": 0.01}
  ]
}
```

`HFT_G14...060449Z` repeat JSON 中的混淆矩阵、重算质量和 summary 只有汇总值，不含独立
labels/predictions 的逐样本可追溯绑定，因此 collector 必须拒绝。合法生成边界是在 GPU 节点对
冻结 independent holdout 读取官方/独立人工标签，再用 prepare 已冻结的模型逐样本推理输出；
collector 只验证、复制和绑定，绝不从混淆矩阵、总指标或 runner 流量结果反推样本。

fallback events 只接受调用方提供的真实注入事件文件。normal 模式拒绝意外 fallback 文件；
工具不会从 GPU failures、断路器计数或时间差推断“已注入”。此外必须有外部 fault-injector
receipt SHA、非 remote-retry 的本地 backend identity、`quality_qualified=true`、真实
`local_completed_delta>0` 且切换窗口 `remote_scored_delta=0`。当前 Rust 明示
`local_fallback_backend_identity=none_without_equivalent_a09_model` 且本地质量固定 false，故 retry/
cache/reconnect 只能算远端恢复，不能生成合法 local fallback artifact。

## normal-r1b 只读演练

在物理机只把工具/config 临时复制到 `/tmp`，对既有目录
`/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T060428Z_normal_r1b`
执行 finalize。未写旧证据目录，结果位于
`/tmp/hft_279_normal_r1b_v2_readonly_dryrun/finalize_receipt.json`。

结果严格为 `adapter_ready=false`、`run_qualified=false`，11 个 adapter 缺口完整保留。
额外归一化缺口为：

- `windows.raw_latency_receipts_missing`；
- `windows.timestamped_internal_counters_missing`；
- `windows.timestamped_external_counters_missing`；
- `windows.physical_raw_missing`；
- `windows.insufficient_consecutive_complete`。

这说明 normal-r1b 的 18 个 packet epoch 和汇总 P99 不能追溯生成 v2 windows。

当前流量形态每窗约 145 个 closed flow，因此同一真实 flow 最多只能贡献约 145 个
flow/kernel-feature/e2e 原始 receipt，远低于 v2 每类 1,000 个的门槛；batch=8 时每窗
GPU batch receipt 也通常远低于 100。collector 会逐窗输出 `*.sample_count` gap，不复制、
重采样或把一个 receipt 拆成多个样本。达到 2.79 Mpps 并不自动满足这些统计样本门槛；
在流量语义、真实采样来源或正式 profile 合法变更前，该项保持未通过。

## 验证

新增 11 项测试：runtime hash 绑定、hash drift 拒绝、现场 argv/PYTHONPATH 文件哈希、GPU
进程归属、采集错误/时钟证据 fail closed、跨机 nonce/RTT clock probe、质量独立性绑定、remote retry 不得冒充 local
fallback、旧汇总 run fail closed、145 个真实 closed-flow receipt 不得扩增，以及由真实形态
raw boundaries/receipts 生成 artifact 后被现有 adapter 和 v2 composer 接受。验证命令：

```bash
python -m unittest discover -s tests \
  -p 'test_current_hardware_279_evidence_collector.py' -v
```

测试只用临时目录和合成合同 fixture；它证明工具合同和 adapter 兼容性，不是物理网卡或 GPU
性能证据。
