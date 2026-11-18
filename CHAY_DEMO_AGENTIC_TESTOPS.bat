@echo off
chcp 65001 >nul
title Agentic TestOps - Live Browser Demo (TrustBase SUT)
color 0B
echo =====================================================================
echo    HE THONG KIEM THU TU DONG HOA AGENTIC TESTOPS - DEMO WEB THUC TE
echo    Truong: Dai hoc Nong Lam TP.HCM - Khoa CNTT
echo    Nhom 05: Nguyen Huu Thang - Pham Tran Nhut Quang - Huynh Van Si
echo =====================================================================
echo.
echo [*] Trinh duyet Google Chrome se mo truc tiep tren man hinh va thao tac:
echo     1. Trang chu TrustBase (/vi)
echo     2. Marketplace san pham so (/vi/marketplace)
echo     3. Bieu mau dang ky & kiem tra allowlist email (/vi/sign-up)
echo     4. Bang phi dich vu & co che ky quy Escrow (/vi/fees)
echo.
cd /d "%~dp0"
node demo_trustbase_real.mjs
echo.
echo =====================================================================
echo    [HOAN TAT] Cac anh chup thuc te da duoc luu tai thu muc:
echo    %~dp0screenshots
echo =====================================================================
pause
