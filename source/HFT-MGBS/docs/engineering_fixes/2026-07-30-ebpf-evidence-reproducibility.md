# eBPF 构建证据可复现性修复

## 问题现象

相同 XDP eBPF 源代码在不同批次得到两个对象哈希：
`1f81856e...` 与 `000ff3c6...`。如果只记录对象哈希，无法判断是数据面
载荷变化还是构建环境噪声。

## 根因

两对象剥离 debug section 后 SHA-256 均为
`ec1745ad93db2e3b6ed9c88f6a42384d78f13a8cfe210093cd75210a9974cb41`。
差异来自 DWARF `DW_AT_comp_dir`：一次从 `/root` 构建，另一次从
HFT-MGBS 根目录构建；可执行 eBPF 载荷没有变化。

## 修改范围

- 构建脚本固定在 HFT-MGBS 根目录运行 clang。
- 增加 `-fdebug-prefix-map`，避免绝对项目路径进入调试证据。
- 物理运行器除对象文件外，同时复制 eBPF C 源文件，并把二者路径和
  SHA-256 写入 manifest 与 `evidence_sha256.txt`。
- 未修改只读上游 `traffic-analysis-platform/rust`。

## 验证证据

分别从 `/root` 与 HFT-MGBS 根目录构建，完整对象 SHA-256 均为
`75b8fe05f5aeaa8bb107019fdef141bbca847a74167fe33aa0ea5d93d9bd4397`。
源文件 SHA-256 为
`671c374543b9367a0257ba8801e91b08df3ee26ce16000c8a3b032da241123be`。

修复后的物理验证目录：
`/home/wangwt/task/datasets/replay/hft_pdiag_20260730T083536460368093Z`。
该次诊断通过，抓包丢包 0、关键流覆盖 1.0；manifest、对象、源文件和
证据索引中的哈希相互一致。

## 性能影响与回退

固定构建目录和复制约数 KiB 的源文件不影响数据面性能。若源文件、
对象或 manifest 任一哈希不一致，运行证据失败关闭，不进入比较。

## 遗留风险

对象哈希仍与 clang/LLVM 版本、内核头文件和编译参数相关。后续生产
构建还需记录工具链版本并采用受控构建镜像；当前证据只证明同一物理机、
同一工具链下不再受调用目录影响。
