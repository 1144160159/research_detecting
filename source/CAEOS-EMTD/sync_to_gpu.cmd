@echo off
setlocal EnableExtensions

set "REMOTE_HOST=root@10.0.5.103"
set "REMOTE_PORT=25696"
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa"
set "REMOTE_ROOT=/opt/data/private/wangwt/ParkAttackKE"
set "REMOTE_WORKSPACE=%REMOTE_ROOT%/CAEOS-EMTD"
set "REMOTE_RELEASE_ROOT=%REMOTE_WORKSPACE%/releases"
set "REMOTE_CURRENT=%REMOTE_WORKSPACE%/current"
set "REMOTE_LEGACY=%REMOTE_WORKSPACE%/active/CAEOS-EMTD-strict-v4-20260717"
set "REMOTE_STALE=%REMOTE_WORKSPACE%/legacy/CAEOS-EMTD-original"
set "REMOTE_PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python"
set "STAGE_ID=%RANDOM%-%RANDOM%"
set "REMOTE_STAGE=%REMOTE_RELEASE_ROOT%/.incoming-%STAGE_ID%"

if not exist "%SSH_KEY%" (
  echo SSH key not found: %SSH_KEY%
  exit /b 1
)

if not exist "contracts\caeos_delivery_contract_v1.json" (
  echo Run this script from the CAEOS-EMTD source root.
  exit /b 1
)

echo Publishing an immutable CAEOS-EMTD release...
ssh -o ClearAllForwardings=yes -o BatchMode=yes -o ConnectTimeout=10 -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% ^
  "mkdir -p %REMOTE_RELEASE_ROOT% && test ! -e %REMOTE_STAGE% && mkdir %REMOTE_STAGE%"
if errorlevel 1 exit /b 1

tar -czf - ^
  --exclude=__pycache__ ^
  --exclude=*.pyc ^
  --exclude=.pytest_cache ^
  --exclude=runs ^
  --exclude=source ^
  --exclude=sources ^
  --exclude=dataset_audits ^
  caeos configs contracts tests scripts reproducibility docs ^
  results/strict_v4_pug_design_v1/design_protocol.json ^
  results/strict_v4_pug_confirmation_v1/execution_protocol.json ^
  results/strict_v4_pug_confirmation_v1/candidate_training.failed.log ^
  results/strict_v4_pug_confirmation_v2/execution_protocol.json ^
  *.py *.md *.txt *.cmd ^
  | ssh -o ClearAllForwardings=yes -o BatchMode=yes -o ConnectTimeout=10 -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% "tar -xzf - -C %REMOTE_STAGE%"
if errorlevel 1 (
  echo Upload failed; validated current release was not changed.
  exit /b 1
)

ssh -o ClearAllForwardings=yes -o BatchMode=yes -o ConnectTimeout=10 -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% ^
  "cd %REMOTE_STAGE% && %REMOTE_PYTHON% -m compileall -q caeos *.py && %REMOTE_PYTHON% -m pytest -q tests/test_project_contract.py tests/test_strict_v4_open_set_metric_contract_v2.py tests/test_strict_v4_neural_empirical_tail_hybrid_screening.py tests/test_experiment_matrix.py && find . -type f ! -name SOURCE_MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > SOURCE_MANIFEST.sha256 && release_id=$(date -u +%%Y%%m%%dT%%H%%M%%SZ)-caeos_delivery_contract_v1-%STAGE_ID% && release_dir=%REMOTE_RELEASE_ROOT%/$release_id && mv %REMOTE_STAGE% $release_dir && ln -s $release_dir %REMOTE_CURRENT%.next-%STAGE_ID% && mv -Tf %REMOTE_CURRENT%.next-%STAGE_ID% %REMOTE_CURRENT% && cp $release_dir/docs/REMOTE_LEGACY_ACTIVE_WORKSPACE.md %REMOTE_LEGACY%/REMOTE_WORKSPACE_ROLE.md && cp $release_dir/docs/REMOTE_STALE_WORKSPACE.md %REMOTE_STALE%/REMOTE_WORKSPACE_ROLE.md && printf 'RELEASE_ID=%%s\nRELEASE_DIR=%%s\n' $release_id $release_dir"
if errorlevel 1 (
  echo Remote validation or release activation failed; current was not advanced.
  exit /b 1
)

echo Release published. Resolve %REMOTE_CURRENT% before every new experiment.
endlocal
