# GPU SSH 入口切换到 25696 与推理服务恢复

## 问题现象

GPU 节点 `10.0.5.103` 的 SSH 映射端口由 `25150` 变更为 `25696`。节点容器于
2026-08-01 重新启动后，旧的 PID、日志和 runtime manifest 仍保留，但 50051 没有
监听，A09 Python 推理服务没有随容器自动恢复。

## 修改范围

- `sync_to_gpu.cmd` 和 `sync_split_deployment.cmd` 的 GPU SSH 端口改为 `25696`。
- `configs/optimization_profile.yaml` 与 `configs/split_deployment_rc1.json` 的
  `ssh_port` 改为 `25696`。
- 不修改模型、数据集或历史结果；服务仍绑定 `0.0.0.0:50051`，反向连接目标仍为
  `10.0.5.8:50052`。

## 恢复与验证证据

- 使用已部署的本机公钥、`BatchMode=yes`、`IdentitiesOnly=yes`、
  `ClearAllForwardings=yes` 和严格主机密钥检查直连 `10.0.5.103:25696` 成功；主机名
  为 `parkattack32`。
- 容器启动时间为 `2026-08-01 08:57:49 UTC`；恢复前 `ss -lntp` 仅有 SSH 监听，
  未发现 50051/50052 服务。
- 执行现有 `scripts/start_gpu_service.sh` 后，包装 PID 为 `1857`，实际 Python PID
  为 `1888`，`0.0.0.0:50051` 处于 LISTEN。
- 使用 NDJSON 健康协议访问 `127.0.0.1:50051` 返回 `ok=true`、候选 `A09`、
  `feature_profile=invariant_no_ports_v1`、`algorithm_device=cpu`、
  `gpu_required=false`、`failures=0`。
- 新 runtime manifest SHA-256 为
  `eac2beab0ba42d158c6ea4acb4c10b07c9e80b58f04fcff3dc71b83826035620`；模型包
  SHA-256 为
  `fa9d29858bb7a20f9a66be2105a6182368e4b3029a59ead5fd77f6228b0eb5d2`。

## 边界与遗留风险

- 当前只证明 GPU 节点本地服务健康；socket 快照中没有到
  `10.0.5.8:50052` 的 ESTABLISHED 连接，因此双机在线链路尚未通过。
- A09 当前是 CPU ExtraTrees 运行时，不能表述为 GPU 加速。
- 现有启动脚本不是容器平台级自启动保证；GPU 容器再次重建后仍需由平台启动钩子或
  外部守护器拉起并执行同一健康检查。
- `full_pipeline_qualified=false`、`final_pareto_ingestion_allowed=false` 保持不变。

## 回退

如果平台再次恢复旧 SSH 映射，只回退上述四个代码/配置端口字段；不要回退历史记录，
也不要通过密码或关闭主机密钥检查建立替代通道。
