\
@echo off
REM Build EXE with PyInstaller (Windows)
REM 1) pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyinstaller
REM 2) run this bat

pyinstaller --noconfirm --onefile --windowed --name WeixinLauncher ^
  --add-data "plugins;plugins" ^
  --hidden-import win32timezone ^
  app.py

echo.
echo Done. Output: dist\WeixinLauncher.exe
pause
