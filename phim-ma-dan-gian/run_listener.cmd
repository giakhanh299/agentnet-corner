@echo off
chcp 65001 >nul
set "PYTHONPATH=D:\AI_AGENT\AI_SYSTEM\RAG"
python "%~dp0muse_mtproto_listener.py"
pause
