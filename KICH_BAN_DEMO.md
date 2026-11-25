# Kịch bản quay video demo — Agentic TestOps trên TrustBase (~4 phút)

**Câu chuyện của video:** công cụ của nhóm (MCP server, 9 tool) → chạy 1 ca kiểm thử thật trên TrustBase → ca đó FAIL (lỗi F-02, mức High) → dùng CDP bắt tận tay nguyên nhân trên RAM → báo cáo được xuất tự động.

Mọi lệnh dưới đây gõ trong **PowerShell** tại thư mục `agentic-test-ops`, trừ khi có ghi khác.

---

## 0. Chuẩn bị (không quay)

1. **Terminal 1, giữ mở suốt buổi quay:** bật Postgres và Redis trong WSL và giữ WSL sống. Docker chạy trong WSL (không có Docker Desktop), nên đóng terminal này là WSL tự tắt và mất cổng 5432/6379.
   ```powershell
   wsl -e sh -c "docker start trustbase-postgres trustbase-redis; sleep infinity"
   ```
   Ở một terminal khác, kiểm tra cả hai phải `True` (nếu `False`, đợi vài giây rồi thử lại):
   ```powershell
   Test-NetConnection localhost -Port 5432 -InformationLevel Quiet; Test-NetConnection localhost -Port 6379 -InformationLevel Quiet
   ```
2. **Terminal 2, giữ mở suốt buổi quay:** bật API TrustBase kèm debugger. Bật **sau** bước 1; nếu bật khi chưa có DB thì tắt đi bật lại.
   ```powershell
   cd $HOME\Documents\trustbase\trustbase-project\api; npx tsx --inspect=127.0.0.1:9229 --tsconfig tsconfig.json src/main.ts
   ```
   API mất khoảng **90 giây** để khởi động; đợi tới khi `http://localhost:4201/health` trả 200.
3. Dọn môi trường test (áp fixture, xóa bộ đếm rate limit):
   ```powershell
   & "C:\Program Files\Git\bin\bash.exe" testcases/reset-local-env.sh
   ```
4. Mở sẵn: VS Code tại repo; Obsidian mở thư mục `knowledge/` làm vault; một terminal PowerShell cỡ chữ lớn, đã `cls`.

---

## Cảnh 1 — Công cụ của nhóm (0:00 – 0:30)

```powershell
node scripts/mcp-call.mjs --list
```
**Màn hình:** `debug-controller 1.1.0: 9 tools` và danh sách 9 tool.

**Lời thoại:** "Đây là sản phẩm của nhóm: một MCP server có 9 công cụ: điều khiển trình duyệt, quản lý server, chạy test, gắn debugger vào backend Node.js, xuất báo cáo. Lệnh này nói chuyện với server đúng như cách Claude Code hay Gemini CLI làm."

---

## Cảnh 2 — Chạy 1 ca kiểm thử thật qua tool `debug_run_test` (0:30 – 1:15)

```powershell
node scripts/mcp-call.mjs debug_run_test '@testcases/demo/run-dsp04.json'
```
(Phải có nháy đơn: trong PowerShell, `@` đứng đầu là toán tử splatting.)

**Màn hình (sau khoảng 2 giây):** JSON với `"status": "FAILED"`; trong phần `stdout` có dòng `✖ TC_TB_DSP_04` và lý do `HTTP 201`.

Mở `testcases/results/latest.json` trong VS Code, chỉ vào trường `actual`: `đơn trạng thái awaiting_payment: HTTP 201 SUCCESS`.

**Lời thoại:** "Ca TC_TB_DSP_04: người mua mở khiếu nại trên một đơn **chưa thanh toán**. Theo đặc tả `admin-rules.md`, khiếu nại chỉ áp dụng sau khi giao hàng, nên kết quả mong đợi (đã chốt trước khi chạy) là bị từ chối 4xx. Thực tế hệ thống trả 201, tức là mở được. Đây là lỗi F-02. Playwright hay Postman chỉ thấy tới đây, không biết **vì sao**."

---

## Cảnh 3 — CDP bắt tận tay nguyên nhân trên RAM (1:15 – 2:30)

Trước cảnh này (cắt khỏi video) chạy lại bước 0.3 để xóa bộ đếm rate limit đăng nhập. Script tự nạp thêm mã vào kho nếu cảnh 2 đã dùng hết.

```powershell
node scripts/demo-f02-cdp.mjs
```
**Màn hình:** script in từng bước:
- `[1]` tạo đơn mới, trạng thái `awaiting_payment`;
- `[2]` gọi tool `debug_inspect_cdp`, đặt breakpoint tại câu kiểm tra trạng thái;
- `[3]` mở khiếu nại → `HTTP 201`;
- `[4]` giá trị đọc trên RAM:
  ```
  order && order.status    = "awaiting_payment"
  orderStatus              = "CHO_CK"
  ALLOWED_OPEN_STATUSES    = ["CHO_CK","DANG_GIAO","DA_GIAO","delivered","funds_held","delivering"]
  ```

Rồi mở trong VS Code (thư mục TrustBase):
- `api/src/modules/disputes/adapters/postgres-backbone.adapter.ts`, chỉ vào 2 dòng `awaiting_payment: 'CHO_CK'` và `funds_held: 'CHO_CK'`;
- `api/src/modules/disputes/disputes.service.ts` dòng 31 (`ALLOWED_OPEN_STATUSES`).

**Lời thoại:** "Tool gắn vào backend qua Chrome DevTools Protocol, dừng đúng tại câu `ALLOWED_OPEN_STATUSES.includes(orderStatus)` và đọc biến trên RAM, không cần thêm `console.log`. Trạng thái thật là `awaiting_payment`, nhưng bị ánh xạ chung với `funds_held` thành `CHO_CK`, mà `CHO_CK` lại nằm trong danh sách được phép khiếu nại. Nguyên nhân gốc nằm ở bảng ánh xạ này."

---

## Cảnh 4 — Báo cáo xuất tự động (2:30 – 3:15)

- VS Code: mở `knowledge/F-02-mo-duoc-khieu-nai-tren-don-chua-thanh-to.md` (Preview), lướt qua: ca kiểm thử, request lỗi, vị trí file:dòng, giá trị CDP, nguyên nhân, đề xuất sửa.
- Obsidian: mở file `.canvas` cùng tên. Sơ đồ: ca kiểm thử → trace trình duyệt/API → nguyên nhân gốc → regression test.
- Lướt nhanh `knowledge/OVERNIGHT-SWEEP-2026-11-24.md`: bảng 6 luồng.

**Lời thoại:** "Báo cáo do tool `debug_export_rag_report` xuất ra từ dữ liệu thật: file Markdown cho người và AI đọc lại, file canvas để xem trực quan trong Obsidian. Exporter chỉ ghi dữ liệu được truyền vào, không tự điền."

---

## Cảnh 5 — Tổng kết (3:15 – 3:45)

Mở `README.md`, mục **8.0 Kết quả thực nghiệm thật**.

**Lời thoại:** "Toàn bộ 30 ca, 6 luồng chạy hết khoảng 5 phút: 25/30 đạt, tìm ra 5 lỗi thật của TrustBase, 1 High, 3 Medium, 1 Low, mỗi lỗi đều chỉ tới file và dòng code. Kết quả và bằng chứng của mọi lần chạy đều lưu trong repo."

---

## Cảnh phụ (tùy chọn) — AI tự gọi tool

Trong Claude Code, mở tại repo (đã nạp `debug-controller` từ `.mcp.json`), gõ:

> Dùng tool debug_run_test chạy ca TC_TB_CAT_01 trong tests/trustbase/trustbase.test.mjs (dùng --test-name-pattern) và giải thích vì sao ca này fail.

Quay cảnh AI gọi tool `debug_run_test`, đọc kết quả và giải thích: tham số `sort` bị bỏ qua khi có từ khóa (lỗi F-01).

---

## Nếu có sự cố khi quay

| Triệu chứng | Cách xử lý |
|---|---|
| API log báo `ECONNREFUSED ...:6379` / `5432`, hoặc lệnh treo không ra gì | WSL đã tự tắt nên mất cổng: kiểm tra Terminal 1 (bước 0.1) còn chạy; nếu vẫn `False` thì `wsl -e docker restart trustbase-postgres trustbase-redis`, sau đó tắt và bật lại API |
| Tạo đơn bị `429 RATE_LIMIT_EXCEEDED` hoặc `LISTING_SOLD_OUT` | Chạy lại bước 0.3 (reset môi trường) |
| `debug_inspect_cdp` báo không tìm thấy target 9229 | API phải chạy bằng lệnh `tsx --inspect=...` ở bước 0.2, không dùng `pnpm dev` |
| Không quay được TrustBase | Dùng kết quả đã lưu: `testcases/results/run7-final.json`, `testcases/cdp-dsp04-breakpoint.json` |

Lưu ý: chạy lẻ 1 ca sẽ ghi đè `testcases/results/latest.json`, không đụng tới kết quả chính thức `run7-final.json`.
