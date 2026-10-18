@echo off
TITLE CPGRAMS Personal Workbench - MeitY AI Division
COLOR 0B
echo =========================================================================
echo    CPGRAMS PERSONAL WORKBENCH - LOCAL AUTOMATION & GRIEVANCE MANAGEMENT
echo    AI & Emerging Technologies Division
echo    Ministry of Electronics and Information Technology (MeitY)
echo =========================================================================
echo.

set PY_EXE=C:\Users\Hp\AppData\Local\Programs\Python\Python311\python.exe
if not exist "%PY_EXE%" (
    set PY_EXE=python.exe
)

echo [1/3] Checking Python environment...
%PY_EXE% --version
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not available. Please install Python 3.11+.
    pause
    exit /b 1
)

echo.
echo [2/3] Initializing local database and pre-flight checks...
cd /d "%~dp0"
%PY_EXE% -c "import backend.main; print('Pre-flight check passed.')"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Pre-flight check failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Starting Workbench Server on http://127.0.0.1:8000 (Localhost Only)...
echo.
echo =========================================================================
echo    Server running at: http://127.0.0.1:8000
echo    Press Ctrl+C to stop the server safely.
echo =========================================================================
echo.

start http://127.0.0.1:8000
%PY_EXE% -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
