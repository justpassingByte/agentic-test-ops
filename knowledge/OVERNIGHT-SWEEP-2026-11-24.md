# 🌙 Multi-Flow Sweep Report: 2026-11-24

- **Sweep ID**: `TRUSTBASE-LOCAL-RUN7`
- **Execution Timestamp**: `2026-11-24T05:23:02.401Z`
- **Total Flows Tested**: 6
- **Flow Status**: **3/6 Passed (50.0%)** — ❌ 3 FLOW DEFECTS DETECTED
- **Total Test Cases Executed**: 25/30 Passed (83.3%)
- **CDP heap evidence attached**: yes

---

## 📊 1. Multi-Flow Health Summary Matrix

| Flow ID | Business Flow | Route | Status | Test Cases | Avg Latency | Notes |
|---|---|---|---|---|---|---|
| **FLOW-01** | Auth | `/auth/*` | PASSED ✅ | 5/5 | 82ms | AUTH_01: PASS; AUTH_02: PASS; AUTH_03: PASS; AUTH_04: PASS; AUTH_05: PASS |
| **FLOW-02** | Catalog | `/catalog/listings` | FAILED ❌ | 4/5 | 28ms | CAT_01: FAIL; CAT_02: PASS; CAT_03: PASS; CAT_04: PASS; CAT_05: PASS |
| **FLOW-03** | Order & Inventory | `/customer/orders` | PASSED ✅ | 5/5 | 49ms | ORD_01: PASS; ORD_02: PASS; ORD_03: PASS; ORD_04: PASS; ORD_05: PASS |
| **FLOW-04** | Voucher | `/customer/orders (voucherCode)` | FAILED ❌ | 3/5 | 60ms | VCH_01: PASS; VCH_02: PASS; VCH_03: FAIL; VCH_04: FAIL; VCH_05: PASS |
| **FLOW-05** | Payout & Fee | `/customer/orders/payout-estimate, /customer/seller/payouts/request` | PASSED ✅ | 5/5 | 11ms | PAY_01: PASS; PAY_02: PASS; PAY_03: PASS; PAY_04: PASS; PAY_05: PASS |
| **FLOW-06** | Dispute | `/customer/disputes` | FAILED ❌ | 3/5 | 23ms | DSP_01: PASS; DSP_02: PASS; DSP_03: FAIL; DSP_04: FAIL; DSP_05: PASS |

---

## 🔍 2. Defect Dossier (Root Cause & CDP Heap Evidence)

### 1. [FLOW-02] Catalog
- **Target Route**: `/catalog/listings`
- **HTTP Network Intercept**: HTTP 200 nhưng giá không tăng dần: giá: 60000, 500000, 59000, 85000, 729000, 60000, 159000
- **Frontend Console Error**: N/A
- **Source Code Location**: `trustbase-project/api/src/modules/listings/listings.repo.ts:413` (Function: `findMany`)

#### 🔬 CDP Heap Variables:
N/A

#### 💡 Root Cause Analysis (RCA):
F-01 (MEDIUM): Khi có q, orderBy chỉ dùng ts_rank_cd (độ liên quan) và bỏ qua opts.sort; contract API vẫn nhận sort cùng q mà không báo lỗi.

- **Regression Test**: `tests/trustbase/trustbase.test.mjs (TC_TB_CAT_01)`

---
### 2. [FLOW-04] Voucher
- **Target Route**: `/customer/orders (voucherCode)`
- **HTTP Network Intercept**: 400 VOUCHER_INVALID cho cả hai lý do (thông báo tiếng Việt đúng nghiệp vụ)
- **Frontend Console Error**: N/A
- **Source Code Location**: N/A

#### 🔬 CDP Heap Variables:
N/A

#### 💡 Root Cause Analysis (RCA):
F-04 (LOW): Service nội bộ có mã cụ thể (VOUCHER_MIN_ORDER_NOT_MET, VOUCHER_EXPIRED) nhưng luồng tạo đơn trả mã chung; client chỉ phân biệt được qua chuỗi thông báo.

- **Regression Test**: `tests/trustbase/trustbase.test.mjs (TC_TB_VCH_03, TC_TB_VCH_04)`

---
### 3. [FLOW-06] Dispute
- **Target Route**: `/customer/disputes`
- **HTTP Network Intercept**: POST /customer/disputes -> 201 SUCCESS trên đơn awaiting_payment
- **Frontend Console Error**: N/A
- **Source Code Location**: `trustbase-project/api/src/modules/disputes/adapters/postgres-backbone.adapter.ts:17` (Function: `DB_TO_NATIVE_STATUS`)

#### 🔬 CDP Heap Variables:
```json
{
  "orderStatus": "CHO_CK",
  "order && order.status": "awaiting_payment",
  "ALLOWED_OPEN_STATUSES": [
    "CHO_CK",
    "DANG_GIAO",
    "DA_GIAO",
    "delivered",
    "funds_held",
    "delivering"
  ],
  "input.category": "ITEM_NOT_AS_DESCRIBED"
}
```

#### 💡 Root Cause Analysis (RCA):
F-02 (HIGH): awaiting_payment và funds_held cùng được ánh xạ sang 'CHO_CK'; 'CHO_CK' nằm trong ALLOWED_OPEN_STATUSES (disputes.service.ts:31) nên openDispute (dòng 154) chấp nhận đơn chưa thanh toán. CDP breakpoint: order.status=awaiting_payment, orderStatus=CHO_CK. | F-03 (MEDIUM): findOpenByOrderId (dòng 142) và kiểm tra trạng thái đơn (148-156) chạy trước kiểm tra quyền PT-03 (dòng 167); phản hồi khác nhau tiết lộ trạng thái đơn cho người không liên quan.

- **Regression Test**: `tests/trustbase/trustbase.test.mjs (TC_TB_DSP_04)`

---