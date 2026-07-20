@echo off
setlocal

set "REMOTE_HOST=root@10.0.5.103"
set "REMOTE_PORT=25450"
set "REMOTE_DIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD"
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa"
set "REMOTE_CONDA=/opt/data/private/wangwt/anaconda3/bin/conda"
set "REMOTE_ENV=py3.9"

if not exist "%SSH_KEY%" (
  echo SSH key not found: %SSH_KEY%
  exit /b 1
)

echo Synchronizing CAEOS-EMTD source to %REMOTE_HOST%:%REMOTE_DIR% ...
tar -czf - --exclude=__pycache__ --exclude=*.pyc --exclude=runs --exclude=.pytest_cache caeos configs tests *.py *.md requirements.txt ^
  | ssh -o ClearAllForwardings=yes -o BatchMode=yes -o ConnectTimeout=10 -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% "mkdir -p %REMOTE_DIR% && tar -xzf - -C %REMOTE_DIR%"

if errorlevel 1 (
  echo Synchronization failed.
  exit /b 1
)

ssh -o ClearAllForwardings=yes -o BatchMode=yes -o ConnectTimeout=10 -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% ^
  "cd %REMOTE_DIR% && %REMOTE_CONDA% run -n %REMOTE_ENV% python -m compileall -q caeos *.py && %REMOTE_CONDA% run -n %REMOTE_ENV% python -m unittest discover -s tests"

if errorlevel 1 (
  echo Remote syntax or unit-test validation failed.
  exit /b 1
)

echo Synchronization and remote syntax validation completed.
endlocal
