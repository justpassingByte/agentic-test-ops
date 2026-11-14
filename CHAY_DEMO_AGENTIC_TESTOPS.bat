@echo off
chcp 65001 >nul
title Agentic TestOps - Live Browser Demo (TrustBase SUT)
color 0B
echo =====================================================================
echo    HE THONG KIEM THU TU DONG HOA AGENTIC TESTOPS - DEMO WEB THUC TE
echo    Truong: Dai hoc Nong Lam TP.HCM - Khoa CNTT
echo    De tai: Nghien cuu ky thuat Agentic TestOps va ung dung tren TrustBase
echo    Nhom 05: Nguyen Huu Thang - Pham Tran Nhut Quang - Huynh Van Si
echo =====================================================================
echo.
echo [*] Dang kiem tra may chu TrustBase va khoi dong Google Chrome...
echo [*] Trinh duyet Chrome se tu dong mo tren man hinh va tu thao tac:
echo     1. Trang chu thuc te TrustBase (/vi)
echo     2. Marketplace san pham so, go tim kiem va loc san pham (/vi/marketplace)
echo     3. Bieu mau dang ky tai khoan thuc te, tu dien form (/vi/sign-up)
echo     4. Bang phi dich vu & co che ky quy Escrow (/vi/fees)
echo.
cd /d "C:\Users\NoNomt007\agentic-test-ops"
node demo_trustbase_real.mjs
echo.
echo =====================================================================
echo    [HOAN TAT] Trinh duyet da luu cac anh screenshot tai:
echo    C:\Users\NoNomt007\agentic-test-ops\screenshots
echo =====================================================================
pause
