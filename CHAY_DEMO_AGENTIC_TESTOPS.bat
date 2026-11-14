@echo off
chcp 65001 >nul
title Agentic TestOps - Live Browser Demo (TrustBase SUT)
color 0B
echo =====================================================================
echo    HE THONG KIEM THU TU DONG HOA AGENTIC TESTOPS - DEMO TRUC QUAN
echo    Truong: Dai hoc Nong Lam TP.HCM - Khoa CNTT
echo    De tai: Nghien cuu ky thuat Agentic TestOps va ung dung tren TrustBase
echo    Nhom 05: Nguyen Huu Thang - Pham Tran Nhut Quang - Huynh Van Si
echo =====================================================================
echo.
echo [*] Dang khoi dong Google Chrome va kich hoat Flow Worker...
echo [*] Trinh duyet se tu dong mo len man hinh, thuc hien cac buoc test.
echo.
cd /d "C:\Users\NoNomt007\agentic-test-ops"
node demo_browser_live.mjs
echo.
echo =====================================================================
echo    [HOAN TAT] Trinh duyet da dong va luu anh screenshot loi vao:
echo    C:\Users\NoNomt007\agentic-test-ops\screenshots\live_demo_bug500.png
echo =====================================================================
pause
