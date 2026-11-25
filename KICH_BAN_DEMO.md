# Kịch bản quay video demo — Agent tự chạy 1 flow trên TrustBase

**Nội dung video:** bộ hồi quy 30 ca (thiết kế từ đặc tả TrustBase, kết quả mong đợi chốt trước khi chạy) báo ca `TC_TB_DSP_04` FAIL. Đưa cho Claude Code một **prompt ngắn chỉ nêu mục tiêu**. Agent tự chọn tool của MCP server `debug-controller`, chạy lại ca, đọc mã nguồn, gắn CDP bắt nguyên nhân trên RAM và kết luận. Sau đó show kết quả tổng 30 ca từ lần chạy chính thức ngày 24/11.

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

**Claude Code (T4)**: mở mới **trong thư mục TrustBase**, đúng như một lập trình viên đang làm việc trên dự án của mình (`debug-controller` đã đăng ký ở phạm vi user nên có mặt ở mọi thư mục, không cần thêm file nào vào TrustBase):
```powershell
cd C:\Users\NoNomt007\Documents\trustbase\trustbase-project; claude
```
Gõ `/mcp` để thấy `debug-controller` báo connected. Tập dượt 2–3 lần; khi được hỏi quyền dùng tool `debug-controller` thì chọn cho phép luôn, để lúc quay không bị hỏi lại.

Mở sẵn thêm: VS Code (agent sẽ tự mở file trong đó), Obsidian với thư mục `knowledge/` làm vault.

---

## 2. Quay

### 2.1. Mở đầu: ca kiểm thử từ đâu ra (~15 giây)

Mở `C:\Users\NoNomt007\agentic-test-ops\testcases\trustbase_testcases.json` trong VS Code, tìm (`Ctrl+F`) `TC_TB_DSP_04`, chỉ vào 3 dòng:
- `"technique"`: *State Transition (chuyển không hợp lệ)*
- `"expected"`: *HTTP 4xx; không tạo khiếu nại*
- `"source"`: *docs/admin-rules.md §2-3 (khiếu nại áp dụng sau khi giao hàng)*

**Lời thoại:** "Ca này nằm trong bộ hồi quy 30 ca, được thiết kế từ đặc tả của TrustBase và chốt kết quả mong đợi trước khi chạy. Bộ hồi quy báo nó fail. Giờ tôi giao cho agent tìm nguyên nhân."

### 2.2. Giao việc cho agent: dán prompt ngắn này vào Claude Code (T4)

> Ca kiểm thử TC_TB_DSP_04 trong C:\Users\NoNomt007\agentic-test-ops\tests\trustbase\trustbase.test.mjs đang fail. Dùng các tool debug-controller tìm nguyên nhân gốc trong backend (API cổng 4201, debugger cổng 9229), có bằng chứng giá trị biến đọc trên RAM.

Prompt chỉ nêu mục tiêu và 3 thông tin agent không tự đoán được: ca test ở đâu, hệ thống chạy ở cổng nào, và yêu cầu **có bằng chứng trên RAM** (thiếu câu này agent có thể chỉ đọc code rồi đoán). Cách dùng `breakpoints` theo đoạn mã và `trigger` thì agent tự đọc từ mô tả của tool.

Rồi quay liên tục khoảng 1–3 phút. Agent tự làm (thứ tự và câu chữ mỗi lần một khác):
1. gọi `debug_run_test` → ca **FAIL**: mở khiếu nại trên đơn chưa thanh toán vẫn trả **HTTP 201** (đặc tả yêu cầu từ chối 4xx);
2. đọc `disputes.service.ts`, tìm ra câu `if (!ALLOWED_OPEN_STATUSES.includes(orderStatus))`;
3. gọi `debug_inspect_cdp` với breakpoint và `trigger`: **một lời gọi** vừa chạy lại ca test vừa đọc trên RAM `order.status = "awaiting_payment"`, `orderStatus = "CHO_CK"`;
4. kết luận: `awaiting_payment` bị ánh xạ thành `CHO_CK` trong `postgres-backbone.adapter.ts`, mà `CHO_CK` nằm trong danh sách được phép khiếu nại (lỗi F-02).

**Nếu agent dừng ở mức đọc code mà chưa gọi CDP**, gõ thêm một câu nhắc ngắn (vẫn tự nhiên như người dùng thật):
> Xác nhận bằng debug_inspect_cdp.

**Muốn agent mở luôn dòng code trong VS Code**, sau khi nó kết luận gõ tiếp:
> Mở dòng đó trong VS Code bằng node C:\Users\NoNomt007\agentic-test-ops\scripts\open-in-vscode.mjs <file> "<đoạn mã>".

**Lời thoại gợi ý:** "Tôi chỉ đưa mục tiêu và chỗ hệ thống đang chạy. Chọn công cụ, đặt breakpoint ở đâu, đọc biến nào là agent tự quyết. Công cụ của nhóm là tay và mắt của agent: chạy test, gắn debugger, đọc biến trên RAM."

Quay vài lần, giữ bản đẹp nhất. Giữa hai lần quay, chạy lại lệnh T3.

### 2.3. Prompt dự phòng (khi prompt ngắn đi lệch nhiều lần)

Prompt từng bước, chắc chắn hơn nhưng trông giống "chỉ đạo" agent hơn:

> Dùng các tool của MCP server debug-controller để điều tra ca kiểm thử TC_TB_DSP_04 trong C:\Users\NoNomt007\agentic-test-ops\tests\trustbase\trustbase.test.mjs.
> 1. Chạy riêng ca này bằng debug_run_test (dùng --test-name-pattern, cwd là C:\Users\NoNomt007\agentic-test-ops).
> 2. Nếu ca fail, đọc mã nguồn trong api\src\modules\disputes để tìm câu lệnh quyết định đơn có được mở khiếu nại hay không.
> 3. Gọi debug_inspect_cdp (cổng 9229) với breakpoint theo đoạn mã tại câu lệnh đó, các biến cần đọc, và trigger là lệnh chạy lại ca này.
> 4. Kết luận nguyên nhân gốc: file, dòng và giá trị biến đọc được trên RAM.
> 5. Mở câu lệnh đó trong VS Code bằng node C:\Users\NoNomt007\agentic-test-ops\scripts\open-in-vscode.mjs <file> "<đoạn mã>".

---

## 2b. Lập trình viên xác minh bằng debugger của VS Code (quay sau cảnh agent, ~1 phút)

**Ý nghĩa:** agent đã chỉ ra lỗi ở `disputes.service.ts` dòng 154; lập trình viên mở đúng chỗ đó và tự xác minh bằng debugger quen thuộc (chế độ human-in-the-loop).

**Trước khi bấm attach:** đợi agent ở cảnh 2 trả lời xong (tool CDP của agent tự nhả cổng 9229 sau mỗi lần gọi). Kiểm tra cổng đã trống, lệnh phải in ra một dòng `ws://127.0.0.1:9229/...`:
```powershell
(Invoke-RestMethod http://127.0.0.1:9229/json/list).webSocketDebuggerUrl
```

**Các bước:**
1. Mở thư mục `C:\Users\NoNomt007\Documents\trustbase\trustbase-project` trong VS Code (phải mở đúng thư mục TrustBase để VS Code đọc được source map của `tsx`).
2. Mở `api/src/modules/disputes/disputes.service.ts`, bấm vào lề trái **dòng 154** `if (!ALLOWED_OPEN_STATUSES.includes(orderStatus))` để đặt chấm đỏ breakpoint.
3. Gắn debugger vào API: `Ctrl+Shift+P` → gõ **Debug: Attach to Node Process** → chọn tiến trình có `src/main.ts` (API chạy ở T2). Thanh trạng thái chuyển màu cam là đã gắn.
   - Không dùng cấu hình "🐛 API: Attach to Process" có sẵn trong TrustBase, vì nó trỏ cổng 9237, còn API đang mở debugger ở cổng 9229.
4. Ở T3, chạy ca test để gửi request mở khiếu nại:
   ```powershell
   cd C:\Users\NoNomt007\agentic-test-ops; node --test --test-name-pattern=TC_TB_DSP_04 tests/trustbase/trustbase.test.mjs
   ```
5. VS Code **dừng tại dòng 154** (dòng tô vàng). Quay khung **Variables**: `orderStatus = "CHO_CK"`, `order.status = "awaiting_payment"`. Gõ `ALLOWED_OPEN_STATUSES` vào **Debug Console** để thấy `CHO_CK` nằm trong danh sách.
6. Bấm **F5 (Continue)** → terminal T3 báo ca FAIL với `HTTP 201`.
7. Bấm **Shift+F5** để ngắt debugger. **Bắt buộc** nếu còn quay lại cảnh agent: cổng 9229 chỉ nhận một debugger tại một thời điểm.

**Lời thoại gợi ý:** "Agent đã chỉ ra đúng dòng 154. Lập trình viên chỉ cần đặt breakpoint ở đó, gắn debugger vào chính server đang chạy, không phải khởi động lại, và thấy cùng giá trị trên RAM: đơn chưa thanh toán nhưng mang trạng thái `CHO_CK`."

Cảnh này chưa được chạy thử trên TrustBase: nên tập một lần. Chấm đỏ phải **đặc**; nếu là chấm rỗng, VS Code chưa bám được source map (xem Phụ lục B).

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
| Agent gọi `debug_inspect_cdp` báo "another debugger may already be attached" | VS Code vẫn đang gắn vào API: bấm Shift+F5 trong VS Code rồi chạy lại |
| VS Code không dừng ở dòng 154, chấm đỏ là chấm rỗng | VS Code chưa bám được source map: kiểm tra đang mở đúng thư mục TrustBase (không phải agentic-test-ops), ngắt (Shift+F5) rồi gắn lại; vẫn không được thì dùng Phụ lục A |
| Mọi request tới API đều treo sau khi debug | API đang bị dừng ở breakpoint: bấm F5 (Continue) trong VS Code, hoặc tắt và bật lại API ở T2 |
| `/mcp` không thấy `debug-controller` | Mở Claude Code đúng thư mục `agentic-test-ops` (nơi có file `.mcp.json`) |
| Agent không gọi đúng tool hoặc trả lời lệch | Gõ thêm một câu nhắc (ví dụ "gọi debug_inspect_cdp với trigger"), hoặc dùng Phụ lục A |
| Không chạy được TrustBase | Show kết quả đã lưu: `testcases/results/run7-final.json`, `testcases/cdp-dsp04-breakpoint.json` |

`cls` là lệnh xóa trắng màn hình terminal; gõ trước khi quay cho khung hình sạch.
