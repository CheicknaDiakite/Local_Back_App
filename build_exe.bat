@echo off
REM Construire un exécutable Windows avec PyInstaller depuis la racine du projet Django.
cd /d "%~dp0"

REM Vérifie que PyInstaller est disponible
where pyinstaller >nul 2>&1
if errorlevel 1 (
  echo PyInstaller n'est pas trouve. Active ton environnement virtuel ou installe-le.
  echo Exemple : python -m pip install pyinstaller
  pause
  exit /b 1
)

REM Construire l'exécutable et inclure les dossiers templates/static/media
pyinstaller --clean --onefile --name digital_back_exe ^
  --add-data "root\templates;root\templates" ^
  --add-data "static;static" ^
  --add-data "media;media" ^
  manage.py

if errorlevel 1 (
  echo Erreur durant la construction. Verifie le message ci-dessus.
  pause
  exit /b 1
)

echo.
echo Build termine : dist\digital_back_exe.exe
echo Pour lancer le serveur : dist\digital_back_exe.exe runserver 0.0.0.0:8000
echo (le reloader est desactive automatiquement dans l'executable)
pause
