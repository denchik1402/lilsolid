@echo off
REM Установка зависимостей (если pip не в PATH, используем py -m pip)
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    python -m pip install -r requirements.txt
)
echo.
echo Готово. Запуск: py app.py
pause
