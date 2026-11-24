# [F-02] Mở được khiếu nại trên đơn chưa thanh toán

- **Target Route**: `POST /customer/disputes`
- **Execution Timestamp**: 2026-11-24T05:23:01.854Z
- **Test Result**: 0/1 Passed (0.0%) — DEFECT DETECTED
- **Severity**: HIGH
- **Testing Methodologies**: State Transition (invalid), Grey-box CDP breakpoint

---

## 1. Test Scenarios Matrix
- **TC_TB_DSP_04**: Mở khiếu nại trên đơn chưa thanh toán -> **FAILED** (đơn trạng thái awaiting_payment: HTTP 201 SUCCESS Operation successful | Technique: State Transition (chuyển không hợp lệ))
  *Summary*: Kỳ vọng: HTTP 4xx; không tạo khiếu nại

---

## 2. Browser & Network Execution Trace (Playwright)
- **DOM Interaction**: `customer1 tạo đơn (awaiting_payment) rồi POST /customer/disputes, category ITEM_NOT_AS_DESCRIBED`
- **Console Errors**:
```text
None recorded.
```
- **Failed HTTP Request**:
```text
POST /customer/disputes -> 201 SUCCESS trên đơn awaiting_payment
```
- **Screenshot Artifact**: N/A

---

## 3. Root Cause Analysis (RCA) & Regression Defense
- **Source Location**: `trustbase-project/api/src/modules/disputes/adapters/postgres-backbone.adapter.ts:17 (Function: DB_TO_NATIVE_STATUS)`
- **Root Cause**:
awaiting_payment và funds_held cùng được ánh xạ sang 'CHO_CK'; 'CHO_CK' nằm trong ALLOWED_OPEN_STATUSES (disputes.service.ts:31) nên openDispute (dòng 154) chấp nhận đơn chưa thanh toán. CDP breakpoint: order.status=awaiting_payment, orderStatus=CHO_CK.
- **Automated Regression Suite**: `tests/trustbase/trustbase.test.mjs (TC_TB_DSP_04)`

### CDP In-Memory Heap Snapshot
```json
{
  "orderStatus": {
    "type": "string",
    "value": "CHO_CK"
  },
  "order && order.status": {
    "type": "string",
    "value": "awaiting_payment"
  },
  "ALLOWED_OPEN_STATUSES": {
    "type": "object",
    "value": [
      "CHO_CK",
      "DANG_GIAO",
      "DA_GIAO",
      "delivered",
      "funds_held",
      "delivering"
    ]
  },
  "input.category": {
    "type": "string",
    "value": "ITEM_NOT_AS_DESCRIBED"
  }
}
```