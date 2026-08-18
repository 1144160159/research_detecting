@echo off
setlocal EnableExtensions

pushd "%~dp0" || exit /b 1

set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa"
set "PHYSICAL_HOST=root@10.0.5.8"
set "PHYSICAL_DIR=/home/wangwt/phase_2/code/HFT-MGBS"
set "GPU_HOST=root@10.0.5.103"
set "GPU_PORT=25696"
set "GPU_DIR=/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS"
set "GPU_CONDA=/opt/data/private/wangwt/anaconda3/bin/conda"
set "GPU_ENV=py3.9"
set "LOCAL_PYTHON=D:\soft\Anaconda3\python.exe"
set "ARCHIVE=%TEMP%\hft-mgbs-code-%RANDOM%%RANDOM%.tgz"
set "REMOTE_ARCHIVE=/tmp/hft-mgbs-code-sync-%RANDOM%%RANDOM%.tgz"

if not exist "%SSH_KEY%" (
  echo SSH key not found: %SSH_KEY%
  goto :fail
)
if not exist "%LOCAL_PYTHON%" (
  echo Local Python not found: %LOCAL_PYTHON%
  goto :fail
)

"%LOCAL_PYTHON%" scripts\check_local_policy.py
if errorlevel 1 goto :fail

tar.exe -czf "%ARCHIVE%" ^
  --exclude=.pytest_cache ^
  --exclude=__pycache__ ^
  --exclude=*.pyc ^
  --exclude=target ^
  README.md SYNC_POLICY.md pyproject.toml requirements.txt .gitignore ^
  sync_to_gpu.cmd sync_split_deployment.cmd ^
  configs deploy docs hft_mgbs rust scripts tests
if errorlevel 1 goto :fail

scp -o BatchMode=yes -o ClearAllForwardings=yes -o ConnectTimeout=120 ^
  -o IdentitiesOnly=yes -i "%SSH_KEY%" "%ARCHIVE%" ^
  %PHYSICAL_HOST%:%REMOTE_ARCHIVE%
if errorlevel 1 goto :fail

scp -P %GPU_PORT% -o BatchMode=yes -o ClearAllForwardings=yes ^
  -o ConnectTimeout=120 -o IdentitiesOnly=yes -i "%SSH_KEY%" "%ARCHIVE%" ^
  %GPU_HOST%:%REMOTE_ARCHIVE%
if errorlevel 1 goto :fail

ssh -o BatchMode=yes -o ClearAllForwardings=yes -o ConnectTimeout=120 ^
  -o IdentitiesOnly=yes -i "%SSH_KEY%" %PHYSICAL_HOST% ^
  "set -e; mkdir -p %PHYSICAL_DIR%; tar -xzf %REMOTE_ARCHIVE% -C %PHYSICAL_DIR%; chmod 755 %PHYSICAL_DIR%/scripts/*.sh; rm -f -- %REMOTE_ARCHIVE%"
if errorlevel 1 goto :fail

ssh -p %GPU_PORT% -o BatchMode=yes -o ClearAllForwardings=yes ^
  -o ConnectTimeout=120 -o IdentitiesOnly=yes -i "%SSH_KEY%" %GPU_HOST% ^
  "set -e; mkdir -p %GPU_DIR%; tar -xzf %REMOTE_ARCHIVE% -C %GPU_DIR%; chmod 755 %GPU_DIR%/scripts/*.sh; rm -f -- %REMOTE_ARCHIVE%"
if errorlevel 1 goto :fail

ssh -o BatchMode=yes -o ClearAllForwardings=yes -o ConnectTimeout=120 ^
  -o IdentitiesOnly=yes -i "%SSH_KEY%" %PHYSICAL_HOST% ^
  "set -e; cd %PHYSICAL_DIR%; PYTHONPATH=. python3 -m pytest -q; python3 scripts/audit_release_candidate.py configs/algorithm_search_rc1.json configs/release_candidate_rc1.json; python3 scripts/check_local_policy.py; bash -n scripts/*.sh; test -x scripts/run_temporary_shadow_capture.sh; cd rust/hft-capture; cargo fmt -- --check; cargo test --all-targets; cargo build --release"
if errorlevel 1 goto :fail

ssh -p %GPU_PORT% -o BatchMode=yes -o ClearAllForwardings=yes ^
  -o ConnectTimeout=120 -o IdentitiesOnly=yes -i "%SSH_KEY%" %GPU_HOST% ^
  "set -e; cd %GPU_DIR%; %GPU_CONDA% run -n %GPU_ENV% env PYTHONPATH=. python -m pytest -q; %GPU_CONDA% run -n %GPU_ENV% env PYTHONPATH=. python scripts/audit_release_candidate.py configs/algorithm_search_rc1.json configs/release_candidate_rc1.json; %GPU_CONDA% run -n %GPU_ENV% python scripts/check_local_policy.py; bash -n scripts/*.sh; test -x scripts/start_gpu_service.sh"
if errorlevel 1 goto :fail

if exist "%ARCHIVE%" del /q "%ARCHIVE%"
popd
echo Split deployment synchronization and validation completed.
exit /b 0

:fail
set "RC=%ERRORLEVEL%"
if "%RC%"=="0" set "RC=1"
if exist "%ARCHIVE%" del /q "%ARCHIVE%"
popd
echo Split deployment synchronization failed with exit code %RC%.
exit /b %RC%
