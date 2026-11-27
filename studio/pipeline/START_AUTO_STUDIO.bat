@echo off
chcp 65001 >nul
title MUSE AUTO STUDIO + CROC DIRECT E: (24/7 - KHONG CAN AI)
echo [1/2] Khoi dong Croc Receiver P2P lang nghe file day thang ve E:\MUSE_MEDIA_STUDIO ...
start "Croc Receiver E:" /min python "D:\AI_AGENT\agentnet-corner-core\studio\pipeline\croc_receiver_daemon.py"
echo [2/2] Khoi dong Auto Studio Daemon 24/7 tren o E:\MUSE_MEDIA_STUDIO ...
python "D:\AI_AGENT\agentnet-corner-core\studio\pipeline\auto_studio_daemon.py" --interval-min 15
pause
