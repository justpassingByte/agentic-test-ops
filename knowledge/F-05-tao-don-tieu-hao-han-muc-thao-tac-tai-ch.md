# [F-05] Tạo đơn tiêu hao hạn mức thao tác tài chính (chung bộ đếm rate limit)

- **Target Route**: `POST /customer/orders + POST /customer/disputes`
- **Execution Timestamp**: 2026-11-24T05:23:02.272Z
- **Test Result**: 0/1 Passed (0.0%) — DEFECT DETECTED
- **Severity**: MEDIUM
- **Testing Methodologies**: Exploratory testing, White-box code trace

---

## 1. Test Scenarios Matrix
- **EXP-01**: Thăm dò: 5 lần tạo đơn rồi mở khiếu nại trong cùng phút -> **FAILED** (rl:financial:<user> = 5 -> POST /customer/disputes 429 | Technique: Exploratory)
  *Summary*: Kỳ vọng: giới hạn tạo đơn (10/phút) độc lập với thao tác tài chính (5/phút)

---

## 2. Browser & Network Execution Trace (Playwright)
- **DOM Interaction**: `customer2 gọi POST /customer/orders 5 lần, sau đó POST /customer/disputes`
- **Console Errors**:
```text
None recorded.
```
- **Failed HTTP Request**:
```text
POST /customer/disputes -> 429 Too many operations. Please wait a minute.
```
- **Screenshot Artifact**: N/A

---

## 3. Root Cause Analysis (RCA) & Regression Defense
- **Source Location**: `trustbase-project/api/src/shared/rate-limit/limiters.ts:121 (Function: orderCreateLimiter)`
- **Root Cause**:
orderCreateLimiter = createRateLimiter(FINANCIAL_OPS, {max: 10}) và financialOpsLimiter = createRateLimiter(FINANCIAL_OPS) dùng chung prefix 'rl:financial:' và khóa theo user nên đếm chung.
- **Automated Regression Suite**: `(chưa có, đề xuất bổ sung)`