@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   GeoJSON to LMD Converter
echo   Starting local web app...
echo ============================================

REM Try bioinfo conda env first
set "BIO_PY=D:\miniconda\envs\bioinfo\python.exe"
if exist "%BIO_PY%" (
    "%BIO_PY%" -m streamlit run app.py
    goto :end
)

REM Fall back to any python on PATH
python -m streamlit run app.py
if errorlevel 1 (
    echo.
    echo [ERROR] Python or Streamlit not found.
    echo Please install Python 3.9-3.12 and run:
    echo   python -m pip install -r requirements.txt
    pause
    exit /b 1
)

:end
pause
