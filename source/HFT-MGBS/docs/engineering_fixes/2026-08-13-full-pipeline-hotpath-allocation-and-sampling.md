# 完整流水线热路径分配与采样降载

## 审计结论

`2.794217 Mpps` 来自 `tpacket_v3_fastpath_probe`，其证据范围明确是 capture-only。
真正的 `hft-capture` 主程序依次执行 capture、parse、flow、feature、budget scheduler
和 GPU dispatch，但当前没有复用该 TPACKET_V3 mmap runner。主程序热路径还存在三项
可直接消除的固定开销：每包无闭流时仍创建空 `Vec<ClosedFlow>`；每包调用
`Instant::now()` 并锁住延迟样本 `Mutex<Vec<_>>`；每 16,384 包即扫描完整 flow map，
在 2.79 Mpps 下约为每秒 170 次，而默认 idle timeout 是 120 秒。

## 修复

- `HftFlowTable::update_into` 直接写入复用的 pending batch，无闭流包不再创建空 Vec；
  原 `update` API 保留以避免破坏兼容性。
- packet-processing latency 使用固定 1/1024 稀疏采样；首包必采，报告中新增
  `packet_processing_latency_sample_stride=1024`，避免把采样 P99 冒充全量采样。
- flow expiry 必须同时满足 16,384 包和 1 秒事件时间进展，把高流量全表扫描上限降为
  每秒一次。FIN/RST 立即闭流、特征顺序、预算策略和 dispatch 语义不变。

## 边界

这是完整流水线的可编译降载改造，不是 2.79 Mpps 全流水线验收。当前 Capturer trait 的
live XDP/AF_PACKET 路径仍把每个帧复制为 owned Vec，TPACKET_V3 borrowed mmap 尚未接入
主程序；Rust--GPU runtime identity 当前也未验证。因此必须经正式 runner 实测丢包、
P99、资源、关键流覆盖和 GPU 回退后才能声称完整闭环。

## 验证

执行 `cargo fmt --check`、`cargo test --release` 和 `cargo build --release`。单元测试新增
固定采样边界以及 expiry 的双门条件；既有 flow/scheduler/GPU/fallback 测试必须保持通过。
