@echo off
call ..\.venv\Scripts\Activate
pyinstaller ..\ssff.py --onefile --clean
copy ..\setting.json .\dist\
pause
