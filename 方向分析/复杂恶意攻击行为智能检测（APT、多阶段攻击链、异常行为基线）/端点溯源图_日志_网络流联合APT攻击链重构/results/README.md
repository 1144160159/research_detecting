# Results registry

这里只保存轻量、可 diff 的运行登记与指标长表。大型模型、原始图、PCAP 和中间数据留在受控数据目录，使用 `artifacts_manifest.csv` 保存绝对/相对路径和 SHA-256。

- `runs.csv`：一次运行一行；
- `metrics_long.csv`：一个 run × split × metric 一行；
- `artifacts_manifest.csv`：配置、日志、模型、图、案例和摘要文件清单。

当前仅建立空表头，没有模型实验结果。
