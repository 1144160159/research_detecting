# Sanity Check 综合报告

**生成时间**: 2026-05-26  
**脚本**: `sanity_checks.py`（已扩展 metadata-only / host-disjoint / 去身份重映射）  
**逐数据集明细**: `logs/sanity_NF-UNSW-NB15-v2_3d.md`, `logs/sanity_NF-CSE-CIC-IDS2018-v2.md`  
**数值汇总**: `results/sanity.csv`

---

## 执行命令

```bash
PY=/opt/data/private/wangwt/anaconda3/envs/py3.8/bin/python

$PY sanity_checks.py --dataset NF-UNSW-NB15-v2_3d --way 5 --max_samples 10000 \
  --output logs/sanity_NF-UNSW-NB15-v2_3d.md --csv_output results/sanity.csv

$PY sanity_checks.py --dataset NF-CSE-CIC-IDS2018-v2 --way 5 --max_samples 10000 \
  --output logs/sanity_NF-CSE-CIC-IDS2018-v2.md --csv_output results/sanity.csv
```

**参数说明**（来自 `--help`）：`--dataset`（非 `--pt_path`）、`--way`、`--output`、`--csv_output`、`--max_samples`、`--mi_topk`。

---

## 1. Metadata contamination（元数据/身份捷径）

| 数据集 | msg→attack acc | msg→label acc | node-id only (src,dst) | port only (src_layer,dst_layer) | 去身份：随机节点重映射 |
|--------|----------------|---------------|------------------------|----------------------------------|-------------------------|
| NF-UNSW-NB15-v2_3d | **0.975** | **0.992** | **0.962** | **0.947** | 0.947 |
| NF-CSE-CIC-IDS2018-v2 | **0.969** | N/A* | **0.841** | 0.575 | 0.965 |

\* CSE 子集上 `label` 在抽样后可能类别不足，未得到稳定 acc。

### 解读

1. **msg 特征本身**即可极高精度预测 `attack`/`label`（≥0.97 on UNSW），存在 **“流量统计特征 ≈ 类别”** 的强相关，需警惕预处理是否仍残留类别信号或极度可分统计量。
2. **不读 msg、仅用图端点**时，UNSW 上 `src/dst` 节点 ID 准确率 **~0.96**，`src_layer/dst_layer`（端口层代理）**~0.95**，说明 **位置/身份类信息** 与攻击类型强相关——这是 **“位置=类别”式捷径** 的风险信号。
3. **随机重映射节点 ID** 后准确率仍高（UNSW 上几乎不变；CSE 上甚至更高），因为 **重标号不改变图拓扑**（同构），结构角色仍可被线性分类器利用。该检查用于说明：**仅靠打乱 ID 字面量不足以消除结构捷径**；论文中应强调 **msg 不含 IP/端口明文** 且评测采用 **host-disjoint / cross-domain**。
4. NF-CSE 原始 CSV 含 `IPV4_SRC_ADDR`, `L4_SRC_PORT`, `Label`, `Attack` 等列（见子报告）；需确认构图时 **未将标识符泄漏进 `msg`**。

---

## 2. Host-disjoint split（主机不相交划分）

### 默认 pipeline：按 **attack 类别** 划分 train/val/test

| 数据集 | train–test 共享 host 数 | 占 test host 比例（约） |
|--------|-------------------------|-------------------------|
| NF-UNSW-NB15-v2_3d | **2406** | ~7.9% |
| NF-CSE-CIC-IDS2018-v2 | **485** | ~9.8% |

**结论**：当前 main.py 使用的 **类均衡 episode 划分** 会让大量主机同时出现在 train 与 test，模型可在 test 上 **“见过相同主机”**，指标偏乐观。

### 推荐：按 **主机集合** 划分（host partition disjoint）

| 数据集 | train/test 主机集合是否不相交 | 跨分区边（train 主机 ↔ test 主机） | host-disjoint 下 msg→attack acc |
|--------|------------------------------|-------------------------------------|--------------------------------|
| NF-UNSW-NB15-v2_3d | ✅ 是 | 存在 | 0.977 |
| NF-CSE-CIC-IDS2018-v2 | ✅ 是 | 存在 | 0.916 |

- **主机集合层面** 已实现 train/test **零交集**（`host_disjoint_partition_ok=True`）。
- 仍有 **跨分区边**（一端 train 主机、一端 test 主机），故 **事件级** host 集合在 train/test 间仍可能有重叠（UNSW 上 event-level overlap=1413）；这比纯类划分更接近真实 **新主机泛化**，但仍非严格 inductive link prediction。
- 在 host-disjoint 混合样本上，msg→attack 仍 **>0.91**，说明即使限制主机，**流量特征** 仍高度可分——更应报告 **cross-domain**（不同数据集/分布）而不仅是随机类划分。

---

## 3. 对实验设计的建议（为何 cross-domain / host-disjoint 更可信）

| 风险 | 证据 | 缓解 |
|------|------|------|
| 主机记忆 | 类划分下 2406/485 个 test 主机亦在 train 出现 | host-disjoint 划分；或 cross-domain |
| 节点/端口捷径 | node-id-only acc 0.84–0.96 | 确认 `msg` 无 IP/port；报告 host-disjoint / 跨数据集 |
| 特征过强可分 | msg-only acc 0.97+ | 报告消融；跨域 NF↔CIC（需同 msg 维） |
| 拓扑同构 | 随机重映射 ID 后仍高分 | 不作为唯一去泄漏手段；配合跨域 |

**Cross-domain**（`--dataset_train` / `--dataset_test` 不同 `.pt`）在 **msg 维一致** 时，可同时削弱“记主机”和“数据集内固定统计规律”，比单纯调高 k-shot 更能支撑泛化 CLAIM。

---

## 4. 产物索引

| 文件 | 内容 |
|------|------|
| `results/sanity.csv` | 每数据集一行关键指标 |
| `logs/sanity_NF-UNSW-NB15-v2_3d.md` | UNSW 完整表格 + MI TopK |
| `logs/sanity_NF-CSE-CIC-IDS2018-v2.md` | CSE 完整表格 + MI TopK |
| `report.md` | 本综合报告 |

---

## 5. 总体结论

- **存在明显的元数据/身份捷径风险**（尤其 NF-UNSW：node-id、port-layer、msg 均可极高精度预测 attack）。
- **默认类划分下 host 泄漏严重**；**host-disjoint 主机划分** 已实现且更可信，建议在论文主表中 **至少补充 host-disjoint 或 cross-domain 一行**。
- **去身份随机重映射** 已实现，但因 **保拓扑同构**，不能单独证明无泄漏；须与 **host-disjoint / cross-domain** 联用。

**状态**: 可继续跑 `run_experiments.py`，但解读 F1 时应优先引用 **host-disjoint 或 cross-domain** 设置，并避免将类划分 + 重叠主机下的高分等同于真实部署泛化。
