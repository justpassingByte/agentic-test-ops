# [F-03] Người ngoài dò được trạng thái khiếu nại của đơn người khác

- **Target Route**: `POST /customer/disputes`
- **Execution Timestamp**: 2026-11-24T05:23:02.003Z
- **Test Result**: 0/1 Passed (0.0%) — DEFECT DETECTED
- **Severity**: MEDIUM
- **Testing Methodologies**: Phân quyền (IDOR), White-box code trace

---

## 1. Test Scenarios Matrix
- **TC_TB_DSP_03**: Người mua khác mở khiếu nại trên đơn của customer1 -> **FAILED** (customer2 mở khiếu nại trên đơn của customer1: HTTP 409 DISPUTE_ALREADY_OPEN | Technique: Phân quyền (IDOR))
  *Summary*: Kỳ vọng: HTTP 403 hoặc 404; không tạo khiếu nại

---

## 2. Browser & Network Execution Trace (Playwright)
- **DOM Interaction**: `customer2 gửi POST /customer/disputes với orderId của customer1`
- **Console Errors**:
```text
None recorded.
```
- **Failed HTTP Request**:
```text
Đơn chưa có khiếu nại -> 403 (run5); đơn đã có khiếu nại -> 409 DISPUTE_ALREADY_OPEN (run6, run7)
```
- **Screenshot Artifact**: N/A

---

## 3. Root Cause Analysis (RCA) & Regression Defense
- **Source Location**: `trustbase-project/api/src/modules/disputes/disputes.service.ts:142 (Function: openDispute)`
- **Root Cause**:
findOpenByOrderId (dòng 142) và kiểm tra trạng thái đơn (148-156) chạy trước kiểm tra quyền PT-03 (dòng 167); phản hồi khác nhau tiết lộ trạng thái đơn cho người không liên quan.
- **Automated Regression Suite**: `tests/trustbase/trustbase.test.mjs (TC_TB_DSP_03)`