# Local/GPU synchronization policy

The local directory is the source of truth:

`F:\泉城实验室\二期\论文\异常检测\source\CAEOS-EMTD`

The GPU mirror is:

`/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD`

After every local code or configuration edit:

1. run local `py_compile` or the affected unit tests;
2. run `sync_to_gpu.cmd` immediately;
3. require remote syntax validation and unit tests in Conda environment `py3.9`
   to pass before launching an experiment;
4. keep datasets, runs, caches, checkpoints, and generated results on the GPU only;
5. copy compact metrics and manifests back to the local method folder after each experiment.

The sync command transfers only source code, configurations, tests,
documentation, and requirements. It excludes `runs`, Python caches, datasets,
and model artifacts.

Experiments must not be launched from an unsynchronized remote edit. If an
emergency change is made on the server, first copy it back to the local source
of truth, review it locally, and then run the normal forward synchronization.
