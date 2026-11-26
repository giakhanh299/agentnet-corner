@echo off
chcp 65001 >nul
title MUSE AUTO STUDIO DAEMON (24/7 - KHONG CAN AI)
echo Dang chay Auto Studio Daemon 24/7 tren o E:\MUSE_MEDIA_STUDIO ...
python "D:\AI_AGENT\agentnet-corner-core\studio\pipeline\auto_studio_daemon.py" --interval-min 15
pause
