@echo off
setlocal
set "REMOTE_HOST=root@10.0.5.103"
set "REMOTE_PORT=25450"
set "REMOTE_DIR=/opt/data/private/wangwt/ParkAttackKE/Open-Detect"
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa"

tar -czf - --exclude=__pycache__ --exclude=*.pyc --exclude=runs --exclude=save_model . ^
  | ssh -o BatchMode=yes -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% "mkdir -p %REMOTE_DIR% && tar -xzf - -C %REMOTE_DIR%"
if errorlevel 1 exit /b 1

ssh -o BatchMode=yes -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% ^
  "cd %REMOTE_DIR% && /opt/data/private/wangwt/anaconda3/bin/conda run -n py3.9 python -m compileall -q ."
if errorlevel 1 exit /b 1
echo Open-Detect synchronization completed.
endlocal
