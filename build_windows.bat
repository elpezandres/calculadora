@echo off
setlocal
python -m pip install --upgrade pip
python -m pip install -r requirements-windows.txt
pyinstaller --noconfirm --clean --windowed --name COSTIFY main.py
 echo.
echo Listo. El ejecutable esta en dist\COSTIFY\COSTIFY.exe
echo Puedes copiar toda la carpeta dist\COSTIFY a otro PC Windows.
pause
