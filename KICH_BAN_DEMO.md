# Kịch bản quay video demo — Agentic TestOps trên TrustBase (~4 phút)

**Câu chuyện của video:** công cụ của nhóm (MCP server, 9 tool) → **AI agent tự** chạy 1 ca kiểm thử thật trên TrustBase → ca đó FAIL (lỗi F-02, mức High) → agent tự dùng CDP bắt tận tay nguyên nhân trên RAM → báo cáo được xuất tự động.

**Hai cách quay cảnh chính:**
- **Cách A (nên dùng): agent tự chạy.** Gõ 1 prompt vào Claude Code; AI tự chọn tool, tự soạn tham số, tự đọc mã nguồn và kết luận (cảnh 2A).
- **Cách B (dự phòng): lệnh dựng sẵn.** `testcases/demo/*.json` và `scripts/demo-f02-cdp.mjs` chứa đúng các tham số agent đã dùng khi chạy thật ngày 24/11, để quay ổn định khi agent trả lời lệch (cảnh 2B, 3B).

Mọi lệnh gõ trong **PowerShell**. Cần 3 cửa sổ terminal:

| Terminal | Thư mục | Dùng cho |
|---|---|---|
| **T1** | bất kỳ | Giữ WSL (Postgres, Redis) sống: bước 0.1, để nguyên không đụng |
| **T2** | `C:\Users\NoNomt007\Documents\trustbase\trustbase-project\api` | Chạy API TrustBase: bước 0.2, để nguyên không đụng |
| **T3** | `C:\Users\NoNomt007\agentic-test-ops` | **Tất cả lệnh còn lại** (bước 0.3 và mọi cảnh quay). Đây là cửa sổ đưa lên video |

Mỗi khối lệnh dưới đây đã kèm sẵn `cd` tới đúng thư mục, nên copy nguyên khối là chạy được. `cls` là lệnh xóa trắng màn hình terminal; gõ trước mỗi cảnh cho khung hình sạch.

---

## 0. Chuẩn bị (không quay)

1. **T1, giữ mở suốt buổi quay:** bật Postgres và Redis trong WSL và giữ WSL sống. Docker chạy trong WSL (không có Docker Desktop), nên đóng terminal này là WSL tự tắt và mất cổng 5432/6379.
   ```powershell
   wsl -e sh -c "docker start trustbase-postgres trustbase-redis; sleep infinity"
   ```
   Ở T3, kiểm tra cả hai phải `True` (nếu `False`, đợi vài giây rồi thử lại):
   ```powershell
   Test-NetConnection localhost -Port 5432 -InformationLevel Quiet; Test-NetConnection localhost -Port 6379 -InformationLevel Quiet
   ```
2. **T2, giữ mở suốt buổi quay:** bật API TrustBase kèm debugger. Bật **sau** bước 1; nếu bật khi chưa có DB thì tắt đi bật lại.
   ```powershell
   cd $HOME\Documents\trustbase\trustbase-project\api; npx tsx --inspect=127.0.0.1:9229 --tsconfig tsconfig.json src/main.ts
   ```
   API mất khoảng **90 giây** để khởi động; đợi tới khi `http://localhost:4201/health` trả 200.
3. Ở T3: dọn môi trường test (áp fixture, xóa bộ đếm rate limit):
   ```powershell
   cd C:\Users\NoNomt007\agentic-test-ops; & "C:\Program Files\Git\bin\bash.exe" testcases/reset-local-env.sh
   ```
4. Mở sẵn: VS Code (cảnh 3B sẽ tự mở file TrustBase trong đó); Obsidian mở thư mục `knowledge/` làm vault; T3 tăng cỡ chữ, gõ `cls`.
5. Cho cách A: mở Claude Code tại thư mục `C:\Users\NoNomt007\agentic-test-ops` (**mở mới sau khi pull code**, để MCP server nạp bản có tham số `trigger`). Gõ `/mcp` để kiểm tra `debug-controller` báo connected. Tập dượt prompt một lần; khi Claude Code hỏi quyền dùng tool `debug-controller`, chọn cho phép luôn để lúc quay không bị hỏi lại.

---

## Cảnh 1 — Công cụ của nhóm (0:00 – 0:30)

Chạy ở **T3**:
```powershell
cd C:\Users\NoNomt007\agentic-test-ops; cls; node scripts/mcp-call.mjs --list
```
**Màn hình:** `debug-controller 1.1.0: 9 tools` và danh sách 9 tool.

**Lời thoại:** "Đây là sản phẩm của nhóm: một MCP server có 9 công cụ: điều khiển trình duyệt, quản lý server, chạy test, gắn debugger vào backend Node.js, xuất báo cáo. Lệnh này nói chuyện với server đúng như cách Claude Code hay Gemini CLI làm."

---

## Cảnh 2A — Agent tự điều tra lỗi (cách A, cảnh chính, 0:30 – 2:30)

Trong Claude Code (thư mục `agentic-test-ops`), dán prompt:

> Dùng các tool của MCP server debug-controller để điều tra ca kiểm thử TC_TB_DSP_04 trong tests/trustbase/trustbase.test.mjs.
> 1. Chạy riêng ca này bằng debug_run_test (dùng --test-name-pattern).
> 2. Nếu ca fail, đọc mã nguồn backend TrustBase ở C:\Users\NoNomt007\Documents\trustbase\trustbase-project\api\src\modules\disputes để tìm câu lệnh quyết định đơn có được mở khiếu nại hay không.
> 3. Gọi debug_inspect_cdp (cổng 9229) với breakpoint theo đoạn mã tại câu lệnh đó, các biến cần đọc, và trigger là lệnh chạy lại ca này.
> 4. Kết luận nguyên nhân gốc: file, dòng và giá trị biến đọc được trên RAM.

**Màn hình (agent tự làm, quay liên tục):**
1. Gọi `debug_run_test` → ca FAIL, request mở khiếu nại trả `HTTP 201`.
2. Đọc `disputes.service.ts`, tìm ra câu `if (!ALLOWED_OPEN_STATUSES.includes(orderStatus))`.
3. Gọi `debug_inspect_cdp` với `breakpoints: [{ match: ... }]` và `trigger`. **Một lời gọi:** tool gắn debugger, chạy lại ca test, dừng tại câu đó, đọc `order.status = "awaiting_payment"`, `orderStatus = "CHO_CK"`, rồi cho chạy tiếp.
4. Kết luận: `awaiting_payment` bị ánh xạ thành `CHO_CK` trong `postgres-backbone.adapter.ts`, mà `CHO_CK` nằm trong danh sách được phép khiếu nại.

**Lời thoại:** "Tôi chỉ đưa mục tiêu. Agent tự chọn công cụ, tự soạn tham số, tự đọc mã nguồn, tự đặt breakpoint và tự kết luận. Công cụ của nhóm là tay và mắt của agent: chạy test, gắn debugger, đọc biến trên RAM."

Lưu ý: câu chữ agent trả lời mỗi lần mỗi khác; tập dượt vài lần và giữ bản đẹp nhất. Nếu agent đi lệch, quay cách B bên dưới.

---

## Cảnh 2B — Chạy 1 ca kiểm thử thật qua tool `debug_run_test` (cách B, 0:30 – 1:15)

Chạy ở **T3**:
```powershell
cd C:\Users\NoNomt007\agentic-test-ops; cls; node scripts/mcp-call.mjs debug_run_test '@testcases/demo/run-dsp04.json'
```
(Phải có nháy đơn: trong PowerShell, `@` đứng đầu là toán tử splatting.)

**Màn hình (sau khoảng 2 giây):** JSON với `"status": "FAILED"`; trong phần `stdout` có dòng `✖ TC_TB_DSP_04` và lý do `HTTP 201`.

Mở `testcases/results/latest.json` trong VS Code, chỉ vào trường `actual`: `đơn trạng thái awaiting_payment: HTTP 201 SUCCESS`.

**Lời thoại:** "Ca TC_TB_DSP_04: người mua mở khiếu nại trên một đơn **chưa thanh toán**. Theo đặc tả `admin-rules.md`, khiếu nại chỉ áp dụng sau khi giao hàng, nên kết quả mong đợi (đã chốt trước khi chạy) là bị từ chối 4xx. Thực tế hệ thống trả 201, tức là mở được. Đây là lỗi F-02. Playwright hay Postman chỉ thấy tới đây, không biết **vì sao**."

---

## Cảnh 3B — CDP bắt tận tay nguyên nhân trên RAM (cách B, 1:15 – 2:30)

Muốn quay bản gọn **một lệnh** (giống điều agent làm ở cảnh 2A: tool tự chạy lại ca test qua `trigger`), chạy ở T3:
```powershell
cd C:\Users\NoNomt007\agentic-test-ops; cls; node scripts/mcp-call.mjs debug_inspect_cdp '@testcases/demo/f02-trigger.json'
```
Kết quả là một JSON có `status: "PAUSED"`, `evaluatedVariables` (giá trị trên RAM) và `trigger.output` (ca test FAIL với HTTP 201). Hoặc dùng script dưới đây: in từng bước dễ đọc hơn và tự mở VS Code.

Trước cảnh này (cắt khỏi video) chạy lại bước 0.3 để xóa bộ đếm rate limit đăng nhập. Script tự nạp thêm mã vào kho nếu cảnh 2 đã dùng hết.

Chạy ở **T3**:
```powershell
cd C:\Users\NoNomt007\agentic-test-ops; cls; node scripts/demo-f02-cdp.mjs
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

- `[5]` script **tự mở VS Code** (chuyển sang cửa sổ VS Code để quay):
  1. `disputes.service.ts`, con trỏ đặt sẵn ở **dòng 154** `if (!ALLOWED_OPEN_STATUSES.includes(orderStatus))`, đúng câu mà CDP vừa dừng;
  2. 2,5 giây sau mở `postgres-backbone.adapter.ts` ở **dòng 17** `awaiting_payment: 'CHO_CK',`; chỉ thêm dòng ngay dưới `funds_held: 'CHO_CK',`.

  Cách tìm dòng: tool trả về đường dẫn file và đoạn mã đã dừng; script tìm đúng đoạn mã đó trong file `.ts` rồi gọi `code -g file:dòng:cột`. Muốn không tự mở thì thêm `--no-open`.

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

## Nếu có sự cố khi quay

| Triệu chứng | Cách xử lý |
|---|---|
| API log báo `ECONNREFUSED ...:6379` / `5432`, hoặc lệnh treo không ra gì | WSL đã tự tắt nên mất cổng: kiểm tra Terminal 1 (bước 0.1) còn chạy; nếu vẫn `False` thì `wsl -e docker restart trustbase-postgres trustbase-redis`, sau đó tắt và bật lại API |
| Tạo đơn bị `429 RATE_LIMIT_EXCEEDED` hoặc `LISTING_SOLD_OUT` | Chạy lại bước 0.3 (reset môi trường) |
| Agent trả lời lệch hoặc không gọi đúng tool | Gõ thêm một câu nhắc ("gọi debug_inspect_cdp với trigger"), hoặc chuyển sang cách B |
| `debug_inspect_cdp` báo không tìm thấy target 9229 | API phải chạy bằng lệnh `tsx --inspect=...` ở bước 0.2, không dùng `pnpm dev` |
| Không quay được TrustBase | Dùng kết quả đã lưu: `testcases/results/run7-final.json`, `testcases/cdp-dsp04-breakpoint.json` |

Lưu ý: chạy lẻ 1 ca sẽ ghi đè `testcases/results/latest.json`, không đụng tới kết quả chính thức `run7-final.json`.
