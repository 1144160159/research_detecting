# Rust 当前工具链 Clippy 门禁修复

## 问题

DPDK 分支收敛后，对 `rust/hft-capture` 执行当前 Rust 1.93 工具链的
`cargo clippy --release --all-targets --no-deps -- -D warnings`，HFT-MGBS 自身出现
6 个错误：

- `XdpLinkId` 不实现 `Drop`，对其调用 `std::mem::forget` 无效果；
- owned RX batch 返回类型触发 `type_complexity`；
- 4 个 AF_XDP statistics 字段本身已是 `u64`，强转仍为 `u64`。

另有 15 条警告来自只读依赖
`/home/wangwt/phase_2/code/traffic-analysis-platform/rust`，不在本次修改范围。

## 修复

- XDP attach 返回的 link id 仅作为 program 内部 link map 的标识，不再调用无效
  `forget`；`Bpf` 仍保存在 `HftXdpCapture.bpf` 中维持程序生命周期。
- 增加 `OwnedPacket` 和 `OwnedReceiveBatch` 类型别名。
- 删除 4 个同类型冗余转换。
- 将当前工具链新增的整数倍数/范围 lint 改为标准方法，并把两个 8 参数 injector
  worker 调用收束为显式配置结构，避免用 lint `allow` 掩盖接口复杂度。
- 把 `kernel_af_packet` 测试模块移动到文件末尾，满足
  `items_after_test_module`，不改变测试内容。
- 不修改只读上游代码。

## 验证与回退

必须重新通过格式检查、release 全 target 测试和 HFT-MGBS 自身 Clippy
`-D warnings`。若 XDP attach 生命周期测试或运行回归失败，回退本文件对应修改，
不得用全局 `allow` 隐藏告警。

最终验证结果：格式检查通过，release 全 target 共 8 个测试全部通过，
HFT-MGBS 自身 Clippy `-D warnings` 通过。构建输出仍包含只读上游的 15 条既有
warning；未把这些 warning 误报为已修复，也未修改上游源码。
