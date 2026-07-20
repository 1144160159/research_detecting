# GPU 恶意流量数据集扩展审计

审计日期：2026-07-15

## 结论

本轮从 GPU 服务器新增确认 5 套可用恶意流量数据，共覆盖 38,394,492 条已审计或已提取记录、51 个“数据集-攻击标签槽位”。51 不是跨数据集语义去重后的攻击种类数；例如 DDoS、XSS、Ransomware 在不同数据集中重复出现。

当前已正式接入现有开集矩阵的优先数据集为：

1. Edge-IIoTset：14 个攻击细类，适合 IIoT 多攻击未知类评测。
2. NF-CSE-CIC-IDS2018-v2：14 个攻击细类，适合大规模 NetFlow 外部验证。
3. USTC-TFC2016：10 个恶意软件家族，适合加密/恶意流量家族未知检测。

ToN-IoT 已审计，可作为下一批接入；BoT-IoT 只有 4 个较粗攻击类，优先作为跨域鲁棒性补充。

## 已审计数据

| 数据集 | 原始/提取记录 | 正常类 | 恶意细类 | 状态 |
|---|---:|---:|---:|---|
| Edge-IIoTset | 157,800 | 1 | 14 | 已配置、已缓存、pilot 通过 |
| NF-CSE-CIC-IDS2018-v2 | 18,893,708 | 1 | 14 | 已配置、已缓存、pilot 通过 |
| CIC-ToN-IoT | 5,351,760 | 1 | 9 | 已审计，待接入 |
| CIC-BoT-IoT | 13,428,675 | 1 | 4 | 已审计，80 条缺失标签 |
| USTC-TFC2016 | 562,549 flows | 1 merged | 10 | 24 PCAP 已全量提取，pilot 通过 |

详细标签计数位于同目录 JSON：

- `edge_iiot.json`
- `nf_cse_cic_ids2018_v2.json`
- `cic_ton_iot.json`
- `cic_bot_iot.json`

## 标签覆盖

新增标签可归并为以下研究大类：DDoS/DoS、暴力破解/口令、扫描/侦察、Web 注入/XSS、Bot/C2/后门、勒索软件、中间人、上传/窃取、渗透，以及独立恶意软件家族。正式实验仍保留数据集原始细标签，不使用主观大类替换训练标签。

USTC 恶意家族为 Cridex、Geodo、Htbot、Miuref、Neris、Nsis-ay、Shifu、Tinba、Virut、Zeus。

## 无泄漏处理

Edge-IIoTset 不使用 IP、绝对时间、原始 payload、URI、DNS 名称或 MQTT 消息正文。极保守的首版字段过于稀疏，导致跨标签指纹过滤删除 9,670/15,000 条，已判定不可用。修订版补回 TCP 序列/确认、校验和与端口等协议元数据后，删除量降至 783/15,000，所有类别三划分非空。

NF-CSE 不使用 IP 与端口标识字段，沿用 NF-UNSW 已验证的 NetFlow 模态划分。分层缓存保留 SQL Injection 432 条与 Brute Force -XSS 927 条，不对稀有类做过采样伪造。

USTC 通过 NFStream 6.6.0 从 24 个 PCAP 提取 64 个无 IP、无 payload 的双向流统计特征。未知恶意家族整 PCAP 留出；已知 PCAP 内按 5 分钟窗口生成 `CaptureGroup`，分组切分后 train/validation/test 的 group overlap 为 0。

## 缓存证据

| 缓存 | 行数 | SHA-256 |
|---|---:|---|
| Edge seed7 max1000 | 15,000 | `a4487e95644bfb8f7424df494d70d1eb550bd8ab76f6f58639d4e43bbcec2de1` |
| NF-CSE seed7 max1000 | 14,359 | `1864b5766781c4fa340e2819df9d3034076acd88421e59131b711498b2e54692` |
| USTC NFStream full | 562,549 | `8b18379231367f4dad4b31e4d6aed9d5a8408d5e7f1bf068503f0f2bc1fc639c` |

完整清单位于 `cache_manifests/`。

## Pilot 结果

所有指标均为 seed 7 单场景管线验证，不作为正式多种子 SOTA 结论。

| 数据集/未知类 | 冲突删除 | 已知准确率 | 未知 AUROC | 未知 AUPR | OSCR |
|---|---:|---:|---:|---:|---:|
| Edge / Fingerprinting | 783/15,000 | 0.9421 | 0.7249 | 0.6879 | 0.5482 |
| NF-CSE / SQL Injection | 1,283/14,359 | 0.7681 | 0.7991 | 0.2081 | 0.7094 |
| USTC / Zeus | 985/33,000 | 0.9113 | 0.9741 | 0.9504 | 0.8981 |

本地结果证据位于 `../results/dataset_expansion_pilot_v2/`，GPU 完整运行目录为 `runs/dataset_expansion_pilot_v2/`。

## 复现实验入口

```bash
python run_nested_gate_matrix.py \
  --suite extended \
  --seeds 11,19,23,29 \
  --edge-iiot-cache-dir caches/edge_iiot \
  --nf-cse-cache-dir caches/nf_cse \
  --output-root runs/extended_confirmation
```

正式矩阵前需为每个确认种子生成对应的 Edge 与 NF-CSE 分层缓存。USTC 全量 NFStream CSV 已生成，不需要重复解析 PCAP。

## 后续候选

- CIC-ToN-IoT：9 个攻击类，CICFlowMeter 字段完整，下一批可直接接入。
- CIC-BoT-IoT：4 个粗粒度攻击类，适合作为跨域补充。
- LSNM2024：已发现 15 个恶意目录类别/20 个恶意 CSV，但字段格式需统一。
- CICAPT-IIoT2024：两期大型 CSV 已存在，尚需标签与泄漏字段审计。
- CTU-13：13 个 botnet 场景、约 75 GB，需按 scenario/capture 分组转换。
- CICDDoS2019：约 25 GB，当前主要为压缩归档，解压后再进入审计。
