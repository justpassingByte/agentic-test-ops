@echo off
chcp 65001 >nul
title Agentic TestOps - Kiem Thu Da Phan Vai & Xuat Bang Chung Anh
color 0A
echo ==============================================================================
echo    HE THONG KIEM THU AGENTIC TESTOPS - E2E DA PHAN VAI (STRICT ASSERTIONS)
echo    Chu trinh: Buyer (Checkout + VietQR) -^> Seller (Payout) -^> Admin (Payouts)
echo ==============================================================================
echo.
echo [*] Yeu cau truoc khi chay: TrustBase dang chay o cac cong 4200, 4201, 4203.
echo [*] Trinh duyet Chrome se mo truc quan (khong cap/khong bo qua loi).
echo.
cd /d "%~dp0"
node record_multi_role_detailed_demo.mjs %*
echo.
echo ==============================================================================
echo [KET QUA] Anh chup tung buoc (va anh loi neu co) duoc luu tai:
echo     -^> %~dp0screenshots\
echo (Goi y: truyen them --record-video neu muon ghi them file .webm)
echo ==============================================================================
pause
