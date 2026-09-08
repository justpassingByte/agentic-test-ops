# [BUG-TEST-002] Voucher Discount Boundary Bypass

- **Thời gian**: 2026-09-08T19:21:39.024Z
- **Route ảnh hưởng**: `/cart/checkout`
- **Mức độ nghiêm trọng**: HIGH
- **Trạng thái**: ✅ Đã xác minh bằng Playwright & Replay Test

---

## 1. Triệu chứng & Bằng chứng Thu thập (Browser Trace)
- **Console Errors**:
```text
Invalid discount range
```
- **Yêu cầu mạng thất bại (Failed Request)**:
```text
POST /api/voucher/apply 422
```
- **Ảnh chụp màn hình**: `N/A`

---

## 2. Truy vết Mã nguồn (Source Code Trace)
- **File**: `orders.service.ts`
- **Hàm**: `validateDiscount` (Dòng 92)
- **Nguyên nhân gốc (Root Cause)**:
Max price snapshot not clamped against order bounds

---

## 3. Xác minh & Regression Test
- **Regression Test**: `tests/voucher.spec.ts`
