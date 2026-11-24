# [F-04] Mã lỗi voucher không cụ thể (VOUCHER_INVALID chung)

- **Target Route**: `POST /customer/orders (voucherCode)`
- **Execution Timestamp**: 2026-11-24T05:23:02.129Z
- **Test Result**: 0/2 Passed (0.0%) — DEFECT DETECTED
- **Severity**: LOW
- **Testing Methodologies**: BVA, EP

---

## 1. Test Scenarios Matrix
- **TC_TB_VCH_03**: Voucher có đơn tối thiểu lớn hơn giá trị đơn 1 đồng -> **FAILED** (HTTP 400 VOUCHER_INVALID Đơn hàng tối thiểu 50.001đ để áp dụng voucher này | Technique: BVA (biên+1))
  *Summary*: Kỳ vọng: Bị từ chối với mã lỗi MIN_ORDER_NOT_MET / VOUCHER_MIN_ORDER_NOT_MET
- **TC_TB_VCH_04**: Áp voucher đã hết hạn -> **FAILED** (HTTP 400 VOUCHER_INVALID Voucher đã hết hạn sử dụng | Technique: EP (voucher hết hạn))
  *Summary*: Kỳ vọng: Bị từ chối với mã lỗi VOUCHER_EXPIRED

---

## 2. Browser & Network Execution Trace (Playwright)
- **DOM Interaction**: `Tạo đơn 50.000 đ kèm voucher TBQA_MIN50001 / TBQA_EXPIRED`
- **Console Errors**:
```text
None recorded.
```
- **Failed HTTP Request**:
```text
400 VOUCHER_INVALID cho cả hai lý do (thông báo tiếng Việt đúng nghiệp vụ)
```
- **Screenshot Artifact**: N/A

---

## 3. Root Cause Analysis (RCA) & Regression Defense
- **Source Location**: N/A
- **Root Cause**:
Service nội bộ có mã cụ thể (VOUCHER_MIN_ORDER_NOT_MET, VOUCHER_EXPIRED) nhưng luồng tạo đơn trả mã chung; client chỉ phân biệt được qua chuỗi thông báo.
- **Automated Regression Suite**: `tests/trustbase/trustbase.test.mjs (TC_TB_VCH_03, TC_TB_VCH_04)`