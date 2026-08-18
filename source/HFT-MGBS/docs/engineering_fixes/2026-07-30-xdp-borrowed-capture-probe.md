# XDP 借用式 capture-only 探针留存

## 问题现象

完整流水线在远低于 10 Mpps 时失败，但现有 `Capturer` 接口强制把每个 UMEM
包复制为 owned `Vec<u8>`，无法区分“AF_XDP 原始接收上限”和“复制、解析、
流表、调度、远端推理”的成本。没有分层探针就无法确定整改应先换后端还是
先改 Rust 计算路径。

## 修改范围

- 在 HFT 自有 `HftXdpCapture` 新增 `poll_borrowed`：callback 生命周期严格
  限于 UMEM frame 归还之前，不产生 packet payload `Vec`。
- 一次调用轮询全部活动 RX 队列，并返回本次 packets/bytes。
- 现有 owned `Capturer::poll` 改为复用同一 descriptor 验证/时间戳/归还
  逻辑，再在兼容层执行 `to_vec`，避免两套所有权实现漂移。
- visitor 即使返回错误也先归还当前 frame；metadata 校验提前失败时仍保留
  kernel-owned 标记，由 stop cleanup 归还。
- 新增 `xdp_fastpath_probe` 二进制，只做借用式包/字节/队列计数和每 1,024
  包一次的采样延迟，不做全解析或推理。
- 不修改只读上游 `/home/wangwt/phase_2/code/traffic-analysis-platform/rust`。

## 验证计划

1. Rust 全量测试、release 构建；
2. 先用当前发生器做 0.05/0.5/1 Mpps capture-only 对照；
3. 发生器升级后做 1/5/10/12 Mpps，R0 要求 12 Mpps、drop=0；
4. 同时记录 queue 分布、CPU cores average、采样 P99/P999 和接口清理。

首次 R0 启动目录
`/home/wangwt/task/datasets/replay/hft_r0_xdp_20260730T120944940459850Z`
在 preflight 阶段失败，未启动抓包或注入。原因是 R0 专用配置只写了
`max_raw_capture_p99/p999`，而公共物理机 preflight 还要求兼容字段
`max_parse_reject_rate`、`max_end_to_end_p99_us` 和
`max_end_to_end_p999_us`。两个 R0 配置已补充兼容字段，值与 raw gate
一致；该目录只作为失败关闭证据，不计入性能候选。

## 性能影响与回退

兼容 owned 路径应保持语义不变；新借用路径禁止 callback 保存 slice。若出现
UMEM 所有权错误、退出泄漏、指标计数不一致或现有测试回归，立即回退并保留
证据。capture-only 通过不代表完整特征链路通过。

## 遗留风险

当前 generic XDP 仍会在内核到用户态发生 copy；借用式仅消除用户态第二次
payload copy。单线程多队列仍未拆分，因此 R0 失败后要进入每队列独占 worker
或 TPACKET_V3/DPDK 后端验证。任何结果均为 diagnostic-only。
