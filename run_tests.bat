@echo off
setlocal
cd /d "%~dp0"
python -m unittest discover -s tests -v
if errorlevel 1 (
    echo.
    echo ========================================
    echo TESTES FALHARAM
    echo ========================================
    exit /b 1
)
echo.
echo ========================================
echo TODOS OS TESTES PASSARAM
echo ========================================
exit /b 0
