COSTIFY - Aplicacion multiplataforma (Windows + Android)
========================================================

CONTENIDO
- main.py: aplicacion multiplataforma en Kivy.
- build_windows.bat: instala dependencias y genera la aplicacion para Windows.
- buildozer.spec: configuracion para compilar el APK Android.
- requirements-windows.txt: dependencias para Windows.

FUNCIONES INCLUIDAS
1. Costo total.
2. Margen de contribucion.
3. Utilidad y utilidad neta.
4. Punto de equilibrio en unidades y pesos, y margen de seguridad.
5. Presupuesto segun utilidad objetivo.

WINDOWS 10/11
1. Instala Python 3.10 o 3.11 desde https://www.python.org/downloads/.
2. Durante la instalacion marca Add Python to PATH.
3. Descomprime esta carpeta.
4. Haz doble clic en build_windows.bat.
5. Al terminar, abre dist\COSTIFY\COSTIFY.exe.
   Para distribuirla, comparte la carpeta completa dist\COSTIFY, no solo el EXE.

ANDROID (APK)
La compilacion Android se realiza de forma mas fiable en Linux o Ubuntu/WSL2.
1. Instala Ubuntu 22.04/24.04 en Linux o WSL2.
2. Instala Java 17, build-essential, git, zip, unzip, python3-pip,
   python3-venv, autoconf, libtool, pkg-config, zlib1g-dev y libffi-dev.
3. Copia esta carpeta al entorno Linux.
4. En la carpeta del proyecto ejecuta:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip setuptools wheel
   pip install buildozer cython
   buildozer android debug
5. El APK quedara en la carpeta bin/.
6. Pasa el APK al celular, habilita la instalacion desde esa fuente e instalalo.

NOTAS IMPORTANTES
- Este paquete contiene el codigo fuente y las configuraciones de compilacion.
- No incluye un EXE ni APK ya compilados; esos archivos se generan siguiendo los pasos.
- La compilacion de APK requiere descargar Android SDK/NDK y puede tardar la primera vez.
- Los calculos conservan las formulas y modulos del programa original.
- No incluye metodo escalonado ni metodo reciproco.
