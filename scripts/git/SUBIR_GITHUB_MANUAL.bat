@echo off
chcp 65001 >nul
cd /d "%~dp0"
start notepad "%~dp0LEEME.txt"
explorer "%~dp0"
