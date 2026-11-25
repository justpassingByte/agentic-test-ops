# Kịch bản quay video demo — Agent tự chạy 1 flow trên TrustBase

**Nội dung video:** đưa cho Claude Code đúng **một prompt**. Agent tự dùng các tool của MCP server `debug-controller` để chạy ca `TC_TB_DSP_04`, thấy ca FAIL, tự đọc mã nguồn, tự gắn CDP bắt nguyên nhân trên RAM, kết luận và mở đúng dòng code trong VS Code. Sau đó show kết quả tổng 30 ca từ lần chạy chính thức ngày 24/11.

---

## 1. Chuẩn bị trước khi quay (không quay)

Mở 3 cửa sổ PowerShell:

**T1**: giữ Postgres và Redis sống, để nguyên suốt buổi (Docker chạy trong WSL, đóng cửa sổ này là WSL tự tắt và mất cổng 5432/6379):
```powershell
wsl -e sh -c "docker start trustbase-postgres trustbase-redis; sleep infinity"
```

**T2**: bật API TrustBase kèm debugger, đợi khoảng **90 giây** cho tới khi `http://localhost:4201/health` trả 200 (bật **sau** T1):
```powershell
cd C:\Users\NoNomt007\Documents\trustbase\trustbase-project\api; npx tsx --inspect=127.0.0.1:9229 --tsconfig tsconfig.json src/main.ts
```

**T3**: dọn môi trường test (áp fixture, nạp lại voucher, xóa bộ đếm rate limit). Chạy lại lệnh này **trước mỗi lần quay hoặc tập**:
```powershell
cd C:\Users\NoNomt007\agentic-test-ops; & "C:\Program Files\Git\bin\bash.exe" testcases/reset-local-env.sh
```

**Claude Code**: **mở mới** tại `C:\Users\NoNomt007\agentic-test-ops` (để MCP server nạp bản mới nhất), gõ `/mcp` để thấy `debug-controller` báo connected. Tập dượt một lần; khi được hỏi quyền dùng tool `debug-controller` thì chọn cho phép luôn, để lúc quay không bị hỏi lại.

Mở sẵn thêm: VS Code (agent sẽ tự mở file trong đó), Obsidian với thư mục `knowledge/` làm vault.

---

## 2. Quay: dán đúng một prompt này vào Claude Code

> Dùng các tool của MCP server debug-controller để điều tra ca kiểm thử TC_TB_DSP_04 trong tests/trustbase/trustbase.test.mjs.
> 1. Chạy riêng ca này bằng debug_run_test (dùng --test-name-pattern).
> 2. Nếu ca fail, đọc mã nguồn backend TrustBase ở C:\Users\NoNomt007\Documents\trustbase\trustbase-project\api\src\modules\disputes để tìm câu lệnh quyết định đơn có được mở khiếu nại hay không.
> 3. Gọi debug_inspect_cdp (cổng 9229) với breakpoint theo đoạn mã tại câu lệnh đó, các biến cần đọc, và trigger là lệnh chạy lại ca này.
> 4. Kết luận nguyên nhân gốc: file, dòng và giá trị biến đọc được trên RAM.
> 5. Mở câu lệnh đó trong VS Code bằng node scripts/open-in-vscode.mjs <file> "<đoạn mã>".

Rồi quay liên tục khoảng 1–2 phút. Agent tự làm:
1. gọi `debug_run_test` → ca **FAIL**: mở khiếu nại trên đơn chưa thanh toán vẫn trả **HTTP 201** (đặc tả yêu cầu từ chối 4xx);
2. đọc `disputes.service.ts`, tìm ra câu `if (!ALLOWED_OPEN_STATUSES.includes(orderStatus))`;
3. gọi `debug_inspect_cdp` với breakpoint và `trigger`: **một lời gọi** vừa chạy lại ca test vừa đọc trên RAM `order.status = "awaiting_payment"`, `orderStatus = "CHO_CK"`;
4. kết luận: `awaiting_payment` bị ánh xạ thành `CHO_CK` trong `postgres-backbone.adapter.ts`, mà `CHO_CK` nằm trong danh sách được phép khiếu nại (lỗi F-02);
5. bật VS Code đúng dòng 154 của `disputes.service.ts`.

**Lời thoại gợi ý:** "Tôi chỉ đưa mục tiêu. Agent tự chọn công cụ, tự soạn tham số, tự đọc mã nguồn, tự đặt breakpoint và tự kết luận. Công cụ của nhóm là tay và mắt của agent: chạy test, gắn debugger, đọc biến trên RAM."

Mỗi lần chạy, câu chữ của agent một khác: quay vài lần, giữ bản đẹp nhất. Giữa hai lần quay, chạy lại lệnh T3.

---

## 3. Show kết quả

Có **hai loại kết quả**, nói rõ trong lời thoại:

- **Kết quả chạy trực tiếp trong video:** câu trả lời của agent (ca FAIL, giá trị trên RAM, file và dòng lỗi) được tạo ra ngay trước mắt người xem. Đây là phần chứng minh hệ thống chạy thật.
- **Kết quả tổng 30 ca: lần chạy chính thức ngày 24/11** (không quay lại 30 ca, mất khoảng 5 phút ngồi chờ). Sau cảnh agent, mở:
  - `README.md` mục **8.0**: 25/30 ca đạt, bảng 5 lỗi F-01..F-05;
  - `knowledge/F-02-mo-duoc-khieu-nai-tren-don-chua-thanh-to.md` và file `.canvas` cùng tên trong Obsidian: hồ sơ của chính lỗi vừa demo;
  - lời thoại: *"Đây là kết quả lần chạy đầy đủ 30 ca ngày 24/11; mọi bằng chứng lưu trong `testcases/results/run7-final.json`."*

**Lưu ý:**
- **Đừng bảo agent xuất báo cáo trong video**: tool export sẽ ghi đè `knowledge/F-02-...` của ngày 24/11 bằng một bản chỉ có 1 ca.
- Cảnh agent ghi đè `testcases/results/latest.json` (không đụng tới `run7-final.json`). Quay xong, khôi phục:
  ```powershell
  cd C:\Users\NoNomt007\agentic-test-ops; git checkout -- testcases/results/latest.json
  ```

---

## Phụ lục A — Phương án dự phòng nếu agent đi lệch

Chạy ở T3 các lệnh dựng sẵn (chứa đúng các tham số agent đã dùng khi chạy thật ngày 24/11):

```powershell
cd C:\Users\NoNomt007\agentic-test-ops; node scripts/mcp-call.mjs debug_run_test '@testcases/demo/run-dsp04.json'
```
Chạy riêng ca DSP_04 → FAIL, HTTP 201.

```powershell
cd C:\Users\NoNomt007\agentic-test-ops; node scripts/demo-f02-cdp.mjs
```
Tạo đơn chưa thanh toán, gắn CDP, mở khiếu nại, in giá trị trên RAM, rồi tự mở VS Code ở `disputes.service.ts:154` và `postgres-backbone.adapter.ts:17`.

```powershell
cd C:\Users\NoNomt007\agentic-test-ops; node scripts/mcp-call.mjs debug_inspect_cdp '@testcases/demo/f02-trigger.json'
```
Bản **một lời gọi** (giống điều agent làm ở bước 3): trả về `status: "PAUSED"`, giá trị trên RAM và `trigger.output` của ca test.

Trong PowerShell, tham số `'@testcases/...'` phải có nháy đơn (`@` đứng đầu là toán tử splatting).

---

## Phụ lục B — Xử lý sự cố

| Triệu chứng | Cách xử lý |
|---|---|
| API log báo `ECONNREFUSED ...:6379` / `5432`, hoặc lệnh treo không ra gì | WSL đã tự tắt: kiểm tra T1 còn chạy; nếu vẫn lỗi thì `wsl -e docker restart trustbase-postgres trustbase-redis`, rồi tắt và bật lại API ở T2 |
| Tạo đơn bị `429 RATE_LIMIT_EXCEEDED` hoặc `LISTING_SOLD_OUT` | Chạy lại lệnh T3 (reset môi trường) |
| `debug_inspect_cdp` báo không tìm thấy target 9229 | API phải chạy bằng lệnh `tsx --inspect=...` ở T2, không dùng `pnpm dev` |
| `/mcp` không thấy `debug-controller` | Mở Claude Code đúng thư mục `agentic-test-ops` (nơi có file `.mcp.json`) |
| Agent không gọi đúng tool hoặc trả lời lệch | Gõ thêm một câu nhắc (ví dụ "gọi debug_inspect_cdp với trigger"), hoặc dùng Phụ lục A |
| Không chạy được TrustBase | Show kết quả đã lưu: `testcases/results/run7-final.json`, `testcases/cdp-dsp04-breakpoint.json` |

`cls` là lệnh xóa trắng màn hình terminal; gõ trước khi quay cho khung hình sạch.
