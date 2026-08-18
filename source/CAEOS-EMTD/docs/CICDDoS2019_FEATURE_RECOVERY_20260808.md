# CICDDoS2019 特征处理故障与恢复记录

## 结论

2026-08-08 已解决阻塞 CICDDoS2019 特征处理的两项问题，正式任务已从 871 个既有捕获继续推进。恢复验证时进度为 874/965；这表示处理链已经恢复，不表示数据集已全量完成。

## 问题一：有效标记被误判为过期

- 现象：监督器约每 5 分钟重启一次，入口立即报 `stale capture marker processing policy`。
- 根因：CICDDoS2019 专用入口把整个标签清单的全局 `registry_sha256` 写入数据集处理策略。新增其他数据集会改变该全局哈希，即使 CICDDoS2019 自身的 SQLite 官方标签索引、记录数和内容均未改变，也会错误地使已有标记失效。
- 审计：871 个标记引用的约 36 GB 分片全部通过文件存在性、分片 SHA-256、Schema 和 PCAP 修复身份核验；旧策略与当时预期策略仅 `label_alignment.registry_sha256` 不同。
- 修复：CICDDoS2019 冻结入口改为读取其 SQLite 标签索引中内嵌的注册哈希。871/871 个标记随后被完整验证并复用，没有修改已有 CSV 分片。

## 问题二：第 872 个归档成员末包截断

- 来源：`PCAP-03-11.zip::SAT-03-11-2018_0145`。
- 原始归档 SHA-256：`cdc8935296cab7a2354d4fd32939f7d5e6c592371e5fb89d6a3094cc05dc38c5`。
- 截断位置：第 232832 个包，记录声明捕获 72 字节，归档成员末尾实际保留 18 字节。
- 修复规则：只修正最后一个 PCAP 记录的 captured length，不减少包数量，不抽样，不减少特征。
- 验证：修复前可读包与修复后包的数量、捕获字节数、时间范围、摘要和异或指纹一致；`capinfos` 与完整 `tshark` 扫描均通过。
- 修复文件 SHA-256：`705afc0dbdef5cc03a42df9af45d792a9715f984aec9ca2efe64308b03cea93c`。
- 结果：第 872 个捕获生成 12283 行正式特征，分片 SHA-256 为 `60b90960fddaddf15ef52da0641643c6917960ad7812412bec9741db4e1987db`。

## 资源与回归验证

- 后续 CICDDoS2019 重启配置为 6 个 CPU worker、88 GiB 内存预算、16 GiB 保留内存，与四数据集并发约束一致。
- 远端相关回归测试：26 passed。
- 恢复日志中未再出现策略过期、PCAP 截断或 Python traceback。

## 证据位置

- 特征输出：`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5`
- 兼容性审计：`_control/feature_extraction/cicddos2019_marker_compatibility_audit.json`
- 正式恢复日志：`_control/feature_extraction/lane1_cicddos2019_supervised_20260808T103434.log`
- PCAP 修复清单：`_control/pcap_repair_manifest.json`
- 第 872 个标记：`_captures/cicddos2019/0331e2cabdd35f0947a0d67be8fae52b78c32d813a836cd3039902561c88b1de.json`
