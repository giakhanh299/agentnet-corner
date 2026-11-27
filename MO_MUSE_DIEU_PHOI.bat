@echo off
chcp 65001 >nul
echo ============================================================================
echo   TRUNG TAM GIAO LENH — 1 MUSE TONG DIEU PHOI (profile db93da63)
echo ============================================================================
echo   Cach 1 (Dong lenh / Telegram):
echo     python "%~dp0GIAO_LENH_MUSE_DIEU_PHOI.py" "Noi dung lenh..."
echo   Cach 2 (Mo giao dien Web Trung Tam Dieu Phoi + Bang Diem QA):
for /f "usebackq delims=" %%I in ("%LOCALAPPDATA%\MuseLoginHelper\hub_invite.txt") do set "INV=%%I"
start "" "https://muse.alltool.pro/chief?token=%INV%"
echo   Da mo trang Trung Tam Dieu Phoi tren trinh duyet!
pause
