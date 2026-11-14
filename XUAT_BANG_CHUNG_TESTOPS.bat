@echo off
chcp 65001 >nul
title Agentic TestOps - Xuất Bằng Chứng Video & Screenshot Thực Tế
color 0A
echo ==============================================================================
echo    HE THONG KIEM THU AGENTIC TESTOPS - PIPELINE XUAT BANG CHUNG TU DONG
echo    Truong: Dai hoc Nong Lam TP.HCM - Khoa CNTT
echo    De tai: Nghien cuu ky thuat Agentic TestOps tren he thong TrustBase
echo    Nhom 05: Nguyen Huu Thang - Pham Tran Nhut Quang - Huynh Van Si
echo ==============================================================================
echo.
echo [*] Dang khoi chay chu trinh E2E da phan vai:
echo     1. BUYER: Tim kiem the Steam Wallet, dien form, bam [TAO DON] (Ky quy Escrow)
echo     2. SELLER: Vao Seller Studio, bam nut [Yeu cau rut tien], kiem tra tab [Pending]
echo     3. ADMIN: Truy cap Admin Console (Port 4203), tham dinh & ghi nhan giai ngan
echo.
echo [*] Trinh duyet Google Chrome dang tu dong thao tac va ghi hinh video...
echo.

cd /d "%~dp0"
node record_multi_role_detailed_demo.mjs

echo.
echo ==============================================================================
echo [HOAN TAT] DA XUAT TOAN BO BANG CHUNG KIEM THU (EVIDENCE):
echo.
echo  1. VIDEO THUC TE (~50 giay, day du click, dien form, chuyen role):
echo     -> Desktop:   %USERPROFILE%\Desktop\VIDEO_DEMO_AGENTIC_TESTOPS.webm
echo     -> Downloads: %USERPROFILE%\Downloads\VIDEO_DEMO_AGENTIC_TESTOPS.webm
echo.
echo  2. ANH CHUP MAN HINH TUNG BUOC (Deterministic Screenshots):
echo     -> %USERPROFILE%\agentic-test-ops\screenshots\detailed_01_buyer_order.png
echo     -> %USERPROFILE%\agentic-test-ops\screenshots\detailed_02_seller_payout_button.png
echo     -> %USERPROFILE%\agentic-test-ops\screenshots\detailed_03_admin_disbursement.png
echo.
echo  3. GOI ZIP TONG HOP NOP BAI:
echo     -> %USERPROFILE%\Downloads\Nhom05_DoAn_KiemThuPhanMem_AgenticTestOps.zip
echo ==============================================================================
echo.
pause
