@echo off
TITLE MENIR OS CONSOLE
COLOR 07
cd /d "%~dp0"
python src/launcher.py
pause
python menir_runner_v2.py
