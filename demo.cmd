@echo off
setlocal
pushd "%~dp0src"
if not exist ".venv\Scripts\python.exe" (
  echo Virtualenv not found. Follow src/README.md to install the lab first.
  popd
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m demo_ui.server --open %*
popd
