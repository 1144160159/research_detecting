# 修复：DPDK 进度文档同步路径纠正

## 现象

一次 SCP 同时把 `ENGINEERING_PROGRESS.md` 与 `docs/experiments/2026-07-30-ten-mpps-r0-scaling.md` 发送到远端 `docs/`，使实验文档多出误投副本：

`/home/wangwt/phase_2/code/HFT-MGBS/docs/2026-07-30-ten-mpps-r0-scaling.md`

正确的 `docs/experiments/` 文件未被删除。

## 修复

- 先以 `test -f` 核验误投文件的精确绝对路径。
- 只删除该误投副本。
- 将本地实验文档重新同步到远端 `docs/experiments/2026-07-30-ten-mpps-r0-scaling.md`。
- 后续不同目标目录的文档不再合并到一次 SCP。

未修改或删除其他 HFT-MGBS 文件。
