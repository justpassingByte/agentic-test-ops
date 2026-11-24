# [F-01] Tham số sort bị bỏ qua khi tìm kiếm có từ khóa

- **Target Route**: `GET /catalog/listings?q=&sort=price_asc`
- **Execution Timestamp**: 2026-11-24T05:23:01.726Z
- **Test Result**: 0/1 Passed (0.0%) — DEFECT DETECTED
- **Severity**: MEDIUM
- **Testing Methodologies**: Happy path, White-box code trace

---

## 1. Test Scenarios Matrix
- **TC_TB_CAT_01**: Tìm kiếm từ khóa và sắp xếp giá tăng dần -> **FAILED** (HTTP 200, 7 kết quả, giá: 60000, 500000, 59000, 85000, 729000, 60000, 159000 | Technique: Happy path)
  *Summary*: Kỳ vọng: HTTP 200; danh sách có giá không giảm dần (non-decreasing)

---

## 2. Browser & Network Execution Trace (Playwright)
- **DOM Interaction**: `GET /catalog/listings?q=windows&sort=price_asc&limit=50`
- **Console Errors**:
```text
None recorded.
```
- **Failed HTTP Request**:
```text
HTTP 200 nhưng giá không tăng dần: giá: 60000, 500000, 59000, 85000, 729000, 60000, 159000
```
- **Screenshot Artifact**: N/A

---

## 3. Root Cause Analysis (RCA) & Regression Defense
- **Source Location**: `trustbase-project/api/src/modules/listings/listings.repo.ts:413 (Function: findMany)`
- **Root Cause**:
Khi có q, orderBy chỉ dùng ts_rank_cd (độ liên quan) và bỏ qua opts.sort; contract API vẫn nhận sort cùng q mà không báo lỗi.
- **Automated Regression Suite**: `tests/trustbase/trustbase.test.mjs (TC_TB_CAT_01)`