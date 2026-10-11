@echo off
rem Arma dist\PasswordManager.exe (un solo archivo, sin consola).
rem Requiere el entorno virtual con las dependencias + PyInstaller:
rem   .venv\Scripts\pip install -r requirements.txt pyinstaller
cd /d "%~dp0passwordManager"
"..\.venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name PasswordManager ^
  --add-data "%~dp0passwordManager\style.qss;." ^
  --distpath ..\dist --workpath ..\build --specpath ..\build ^
  gui.py
echo.
echo Listo: dist\PasswordManager.exe
pause
