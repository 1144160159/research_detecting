@echo off
setlocal

set "REMOTE_HOST=root@10.0.5.103"
set "REMOTE_PORT=25450"
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa"
set "REMOTE_PROJECT=/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS"
set "REMOTE_DIR=%REMOTE_PROJECT%/source/HFT-MGBS"
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
if errorlevel 1 exit /b 1

echo Synchronizing code-only HFT-MGBS source to %REMOTE_HOST%:%REMOTE_DIR% ...
tar -czf - --exclude=__pycache__ --exclude=*.pyc --exclude=.pytest_cache hft_mgbs configs scripts tests *.md *.toml *.txt .gitignore ^
  | ssh -o BatchMode=yes -o ConnectTimeout=15 -o ClearAllForwardings=yes -o IdentitiesOnly=yes -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% ^
    "mkdir -p %REMOTE_DIR% %REMOTE_PROJECT%/features %REMOTE_PROJECT%/models %REMOTE_PROJECT%/runs %REMOTE_PROJECT%/results %REMOTE_PROJECT%/profiles %REMOTE_PROJECT%/manifests %REMOTE_PROJECT%/logs && tar -xzf - -C %REMOTE_DIR%"
if errorlevel 1 exit /b 1

ssh -o BatchMode=yes -o ConnectTimeout=15 -o ClearAllForwardings=yes -o IdentitiesOnly=yes -p %REMOTE_PORT% -i "%SSH_KEY%" %REMOTE_HOST% ^
  "set -e; cd %REMOTE_DIR%; %REMOTE_CONDA% run -n %REMOTE_ENV% python scripts/check_local_policy.py; %REMOTE_CONDA% run -n %REMOTE_ENV% python -m compileall -q hft_mgbs tests scripts; %REMOTE_CONDA% run -n %REMOTE_ENV% python -m unittest discover -s tests -v; PYTHONPATH=. %REMOTE_CONDA% run -n %REMOTE_ENV% python scripts/benchmark_synthetic.py --packets 20000 --flows 1000 > %REMOTE_PROJECT%/results/synthetic_smoke.json; PYTHONPATH=. %REMOTE_CONDA% run -n %REMOTE_ENV% python scripts/benchmark_synthetic.py --packets 20000 --flows 1000 --disable-deep > %REMOTE_PROJECT%/results/fallback_smoke.json; PYTHONPATH=. %REMOTE_CONDA% run -n %REMOTE_ENV% python scripts/benchmark_fallback_recovery.py --recovery-timeout-s 0.05 --poll-interval-s 0.005 > %REMOTE_PROJECT%/results/fallback_recovery_smoke.json; PYTHONPATH=. %REMOTE_CONDA% run -n %REMOTE_ENV% python scripts/benchmark_components_synthetic.py --flows 5000 --packets-per-flow 8 > %REMOTE_PROJECT%/results/component_cost_smoke.json; PYTHONPATH=. %REMOTE_CONDA% run -n %REMOTE_ENV% python scripts/evaluate_pareto.py --smoke > %REMOTE_PROJECT%/results/pareto_logic_smoke.json; find . -type f -not -path './__pycache__/*' -not -name '*.pyc' -print0 | sort -z | xargs -0 sha256sum > %REMOTE_PROJECT%/manifests/HFT-MGBS_code_sha256.txt"
if errorlevel 1 exit /b 1

echo Synchronization and remote py3.9 validation completed.
endlocal
