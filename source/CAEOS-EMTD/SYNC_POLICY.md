# Local/GPU synchronization policy

## Single source of truth

Local code:

`F:\泉城实验室\二期\论文\异常检测\source\CAEOS-EMTD`

Validated remote pointer:

`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/current`

Immutable remote releases:

`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/releases`

Legacy active workspace:

`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/active/CAEOS-EMTD-strict-v4-20260717`

All inactive historical workspaces are retained without deletion under
`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/legacy`.

## Publication procedure

`sync_to_gpu.cmd` performs a release-style publication:

1. upload source, configuration, tests, contracts, scripts, and documentation
   into a new staging directory;
2. exclude datasets, results, runs, checkpoints, caches, PDFs, and nested
   historical source copies;
3. run remote compile checks and the contract/metric regression tests with the
   `py3.9` Python environment;
4. write a SHA-256 file manifest;
5. move the staging tree into an immutable release directory;
6. atomically update the `CAEOS-EMTD/current` symlink only after validation.

A failed validation leaves `CAEOS-EMTD/current` unchanged. The script does not
delete legacy workspaces or generated evidence.

## Operating rules

1. Run affected local tests before synchronization.
2. Run `sync_to_gpu.cmd` from this directory.
3. Start new GPU experiments only from the resolved `CAEOS-EMTD/current`
   release.
4. Record the resolved release path and `SOURCE_MANIFEST.sha256` digest in each
   formal result.
5. Keep raw datasets, checkpoints, sample-level outputs, and large results on
   the GPU; synchronize compact metrics and manifests back to the document
   evidence directory.
6. Emergency remote edits are prohibited. Bring a required fix back to local,
   review it, and publish a new immutable release.
