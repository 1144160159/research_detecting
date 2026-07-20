@echo off
setlocal

set "REMOTE_HOST=root@10.0.5.103"
set "REMOTE_PORT=25450"
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa"
set "REMOTE_PROJECT=/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction"
set "REMOTE_DIR=%REMOTE_PROJECT%/source/EACR-APT"
set "REMOTE_CONDA=/opt/data/private/wangwt/anaconda3/bin/conda"
set "REMOTE_ENV=py3.9"
set "LOCAL_PYTHON=D:\soft\Anaconda3\python.exe"

if not exist "%SSH_KEY%" (
  echo SSH key not found: %SSH_KEY%
  exit /b 1
)

if not exist "%LOCAL_PYTHON%" (
  echo Local Python not found: %LOCAL_PYTHON%
  exit /b 1
)

"%LOCAL_PYTHON%" scripts\check_local_policy.py
if errorlevel 1 (
  echo Local policy check failed. No files were transferred.
  exit /b 1
)

echo Synchronizing code-only EACR-APT source to %REMOTE_HOST%:%REMOTE_DIR% ...
tar -czf - --exclude=__pycache__ --exclude=*.pyc --exclude=.pytest_cache eacr_apt configs scripts tests *.md *.toml *.txt .gitignore ^
  | ssh -o BatchMode=yes -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% ^
    "mkdir -p %REMOTE_DIR% %REMOTE_PROJECT%/datasets %REMOTE_PROJECT%/models %REMOTE_PROJECT%/runs %REMOTE_PROJECT%/results %REMOTE_PROJECT%/manifests %REMOTE_PROJECT%/logs && tar -xzf - -C %REMOTE_DIR%"

if errorlevel 1 (
  echo Synchronization failed.
  exit /b 1
)

ssh -o BatchMode=yes -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% ^
  "set -e; cd %REMOTE_DIR%; %REMOTE_CONDA% run -n %REMOTE_ENV% python scripts/check_local_policy.py; %REMOTE_CONDA% run -n %REMOTE_ENV% python -m compileall -q eacr_apt tests scripts; bash -n scripts/*.sh; %REMOTE_CONDA% run -n %REMOTE_ENV% python -m unittest discover -s tests -v; find . -type f -not -path './__pycache__/*' -not -name '*.pyc' -print0 | sort -z | xargs -0 sha256sum > %REMOTE_PROJECT%/manifests/EACR-APT_code_sha256.txt"

if errorlevel 1 (
  echo Remote syntax or unit-test validation failed.
  exit /b 1
)

echo Synchronization and remote py3.9 validation completed.
endlocal
