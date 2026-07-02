# 实验前体检报告 (Pre-experiment Health Check)

**检查时间**: 2026-05-26  
**仓库路径**: `/opt/data/private/wangwt/ParkAttackKE/F-DIDS-MFL`  
**推荐 Python**: `/opt/data/private/wangwt/anaconda3/envs/py3.8/bin/python`

---

## 结论：可开始实验

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 运行环境 | ✅ | Python 3.8 + PyTorch 2.1.2+cu121，CUDA 可用 |
| 脚本 `--help` | ✅ | 见 `logs/*_help.txt`（SimCLR 脚本名见下） |
| TemporalData `.pt` | ✅ | 5 个数据集可读，字段完整 |
| 输出目录 | ✅ | `results/`、`logs/`、`figs/` 已创建 |

---

## 1. 环境信息

详见 `logs/env_info.txt`，`pip freeze` 见 `logs/env_freeze.txt`。

| 项目 | 值 |
|------|-----|
| Python | 3.8.0 |
| PyTorch | 2.1.2+cu121 |
| CUDA | 可用 (12.1) |
| GPU | NVIDIA RTX A6000 × 1 |

```bash
export PY=/opt/data/private/wangwt/anaconda3/envs/py3.8/bin/python
$PY --version
$PY -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

---

## 2. 脚本与参数接口

### 已保存的 `--help`

| 请求脚本名 | 实际文件 | 帮助输出 |
|------------|----------|----------|
| `run_experiments.py` | ✅ 同名 | `logs/run_experiments_help.txt` |
| `sanity_checks.py` | ✅ 同名 | `logs/sanity_checks_help.txt` |
| `pretrain_encoder_simclr.py` | ⚠️ **不存在** | 使用 `pretrain_traffic_encoder.py`（SimCLR/InfoNCE）→ `logs/pretrain_traffic_encoder_help.txt`；说明见 `logs/pretrain_encoder_simclr_help.txt` |
| （补充）`pretrain_encoder_mfm.py` | MFM 预训练 | `logs/pretrain_encoder_mfm_help.txt` |
| （补充）`main.py` | 主训练/评测 | `logs/main_help.txt` |

### `run_experiments.py` 主要参数（当前版本）

- `--mode {in-domain,cross-domain,drift,all}`
- `--dataset_train`, `--dataset_test`, `--way`, `--k_shot`, `--q_query`
- `--meta_epochs`, `--pretrain_epochs`, `--episodes`
- `--settings`（默认 5 组：baseline / foundation / foundation_lora / foundation_cache / full）
- `--alpha_values`, `--foundation_ckpt`, `--output_dir`, `--smoke_test`

### `main.py` 贡献点开关（单次运行）

- Foundation: `--use_foundation_encoder`, `--load_foundation_ckpt`
- LoRA: `--use_lora`, `--use_lora_adapt`, `--lora_adapt_steps`
- Cache: `--use_cache`, `--alpha_fuse`
- 论文多 episode: `--experiment_episodes`, `--experiment_csv`, `--experiment_setting_name`, `--seed`
- 数据: `--dataset_train`, `--dataset_test`（cross-domain）

---

## 3. 数据文件

### 列表：`logs/data_pt_list.txt`

| 文件 | 大小 | 用途 |
|------|------|------|
| `data/CiC-ToN-IoT.pt` | ~86 MB | 默认训练集（注意文件名 **CiC** 大小写） |
| `data/CIC-BoT-IoT_new.pt` | ~231 MB | BoT-IoT |
| `data/DNN-EdgeIIoT-dataset.pt` | ~27 MB | Edge-IIoT |
| `data/NF-UNSW-NB15-v2_3d.pt` | ~30 MB | NF UNSW |
| `data/NF-CSE-CIC-IDS2018-v2.pt` | ~197 MB | NF CSE |
| `data/processed/pre_*.pt` | 极小 | PyG 处理缓存，**非** TemporalData |

原始 CSV 亦在 `data/` 下，可用于重新构图。

### 字段与维度：`logs/data_shapes.json`

所有 TemporalData 均包含：`src`, `dst`, `t`, `msg`, `label`, `attack`, `src_layer`, `dst_layer`, `dt`。

| 数据集 | num_events | msg 特征维 |
|--------|------------|------------|
| CiC-ToN-IoT | 246,496 | **76** |
| CIC-BoT-IoT_new | 672,881 | **76** |
| DNN-EdgeIIoT-dataset | 126,925 | **40** |
| NF-UNSW-NB15-v2_3d | 148,774 | **38** |
| NF-CSE-CIC-IDS2018-v2 | 972,461 | **38** |

**Cross-domain 注意**：`msg` 维不一致时（如 CIC 76 vs NF 38），`main.py` cross-domain 会报错；仅同维数据集间可做跨域 meta-test。

`main.py` / `run_experiments.py` 通过 `resolve_data_path()` 自动匹配 `CIC-ToN-IoT` → `CiC-ToN-IoT.pt`。

---

## 4. 输出目录结构

```
results/   # CSV 汇总（论文表格）
logs/      # env、help、data 元信息、每次 run 的 config_*.json
figs/      # t-SNE / heatmap 等图（main.py 默认仍写 ./pic/，建议实验时统一到 figs/）
```

已创建：`results/`、`logs/`、`figs/`。

建议实验命令将 CSV 写到 `results/`：

```bash
$PY run_experiments.py --output_dir ./results/exp_001 --episodes 5 --smoke_test  # 先 smoke
```

或单次 `main.py`：

```bash
$PY main.py --dataset_train CIC-ToN-IoT --experiment_episodes 5 \
  --experiment_csv results/run_baseline.csv --experiment_setting_name baseline
```

---

## 5. 快速自检命令（可选）

```bash
cd /opt/data/private/wangwt/ParkAttackKE/F-DIDS-MFL
PY=/opt/data/private/wangwt/anaconda3/envs/py3.8/bin/python

# 数据污染 / host-disjoint
$PY sanity_checks.py --dataset CIC-ToN-IoT --output logs/sanity_report.md

# SimCLR 预训练（短跑）
$PY pretrain_traffic_encoder.py --dataset CIC-ToN-IoT --epochs 1 --max_batches 5

# 主流程 smoke
$PY main.py --smoke_test --pretrain_epochs 0 --meta_epochs 1
```

---

## 6. 已知事项

1. **`pretrain_encoder_simclr.py` 不存在**：请使用 `pretrain_traffic_encoder.py`。
2. **默认数据集文件名**：磁盘为 `CiC-ToN-IoT.pt`，CLI 仍写 `CIC-ToN-IoT` 即可。
3. **`import main` 会加载全量数据**：耗时较长；日常请用子命令而非 `import main` 做轻量检查。
4. **画图路径**：`main.py` 默认输出 `./pic/`；若需全部进 `figs/`，可在后续实验脚本中统一改路径或软链接。

---

**体检执行人**: 实验执行 AI Agent  
**产物索引**: `logs/env_info.txt`, `logs/env_freeze.txt`, `logs/data_pt_list.txt`, `logs/data_shapes.json`, `logs/*_help.txt`
