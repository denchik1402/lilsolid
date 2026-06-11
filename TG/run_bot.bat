@echo off
echo Запуск Telegram-бота...
echo Сайт должен быть запущен в другом окне (run_site.bat)
echo.
cd /d "%~dp0.."
python TG\telegram_bot.py
