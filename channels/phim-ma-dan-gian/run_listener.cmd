@echo off
chcp 65001 >nul
rem Runtime dang chay that nam o D:\AI_AGENT\AI_SYSTEM\RAG (giu nguyen session/outbox).
rem Ban co phien ban trong repo: ..\..\bridges\muse_mtproto_listener.py
set "PYTHONPATH=D:\AI_AGENT\AI_SYSTEM\RAG"
python "D:\AI_AGENT\AI_SYSTEM\RAG\muse_mtproto_listener.py"
pause
