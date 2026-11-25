# Kịch bản quay video demo — Dual Trace với lỗi F-01 trên TrustBase

**Câu chuyện của video (~5 phút):**
1. Bộ hồi quy 30 ca báo ca `TC_TB_CAT_01` FAIL: tìm "windows", sắp xếp giá tăng dần nhưng giá trả về lộn xộn (lỗi **F-01**).
2. **Agent tự điều tra theo Dual Trace:** *Browser Trace* (trình duyệt thật thấy triệu chứng: giá lộn xộn dù server trả 200) → *Source Trace* (CDP đọc biến trên RAM: server có nhận `sort` nhưng bỏ qua).
3. **Human-in-the-loop:** lập trình viên mở đúng dòng agent chỉ ra, tự gắn debugger VS Code vào server đang chạy để xác minh.
4. Show báo cáo và kết quả tổng 30 ca.

> ⚠️ **Toàn bộ flow F-01 (trình duyệt, CDP, debugger VS Code) CHƯA được chạy thử.** Phải tập ít nhất một lượt trước khi quay. Những chỗ dễ trục trặc ghi ở Phụ lục B.

Vì sao chọn F-01: đây là lỗi **người dùng nhìn thấy bằng mắt** nhưng **không có lỗi HTTP nào** (server trả 200), nên test API thông thường hay Postman sẽ bỏ sót. Phải có trình duyệt để thấy triệu chứng và CDP để thấy nguyên nhân, đúng tinh thần "Browser Trace + Source Trace" của đề tài.

---

## 1. Chuẩn bị trước khi quay (không quay)

Mở 4 cửa sổ PowerShell:

| Cửa sổ | Thư mục | Việc |
|---|---|---|
| **T1** | bất kỳ | Giữ Postgres và Redis sống. Để nguyên, không đụng |
| **T2** | `...\trustbase-project\api` | Chạy API TrustBase kèm debugger. Để nguyên, không đụng |
| **T3** | `C:\Users\NoNomt007\agentic-test-ops` | Lệnh reset và lệnh dự phòng |
| **T4** | `...\trustbase-project` | Claude Code (agent). **Cửa sổ chính đưa lên video** |

**T1**: Docker chạy trong WSL; đóng cửa sổ này là WSL tự tắt và mất cổng 5432/6379:
```powershell
wsl -e sh -c "docker start trustbase-postgres trustbase-redis; sleep infinity"
```

**T2**: bật **sau** T1, đợi khoảng **90 giây** tới khi `http://localhost:4201/health` trả 200:
```powershell
cd C:\Users\NoNomt007\Documents\trustbase\trustbase-project\api; npx tsx --inspect=127.0.0.1:9229 --tsconfig tsconfig.json src/main.ts
```

**Customer web (cổng 4200)**: bật trong một cửa sổ nữa (hoặc như bạn vẫn bật):
```powershell
cd C:\Users\NoNomt007\Documents\trustbase\trustbase-project\customer; pnpm dev
```

**T3**: dọn môi trường (fixture, xóa bộ đếm rate limit). Chạy lại **trước mỗi lần tập hoặc quay**:
```powershell
cd C:\Users\NoNomt007\agentic-test-ops; & "C:\Program Files\Git\bin\bash.exe" testcases/reset-local-env.sh
```

**T4**: mở Claude Code **trong thư mục TrustBase**, như một lập trình viên đang làm việc trên dự án của mình. `debug-controller` đã đăng ký ở phạm vi user nên có mặt ở mọi thư mục, không cần thêm file nào vào TrustBase:
```powershell
cd C:\Users\NoNomt007\Documents\trustbase\trustbase-project; claude
```
Gõ `/mcp` để thấy `debug-controller` báo connected. Khi được hỏi quyền dùng tool thì chọn cho phép luôn, để lúc quay không bị hỏi lại.

Mở sẵn: **VS Code tại thư mục TrustBase** (`C:\Users\NoNomt007\Documents\trustbase\trustbase-project`) cho cảnh 4; Obsidian với thư mục `C:\Users\NoNomt007\agentic-test-ops\knowledge` làm vault cho cảnh 5. Gõ `cls` ở các terminal cho khung hình sạch.

---

## 2. Cảnh 1 — Ca kiểm thử từ đâu ra (~30 giây)

**Sự thật cần nói rõ:** bộ 30 ca được **AI agent (Claude trong Claude Code) sinh ra ngày 24/11** theo yêu cầu của nhóm. Nhóm đặt mục tiêu và nguyên tắc, agent đọc tài liệu và mã nguồn của TrustBase rồi soạn ca, nhóm duyệt.

| | Nội dung |
|---|---|
| **Đầu vào** | Đặc tả nghiệp vụ trong `docs/` của TrustBase; contract API (schema zod); cấu hình thật trong `system_settings`; ngưỡng rate limit |
| **Nguyên lý** | V-Model: thiết kế và **chốt kết quả mong đợi trước khi chạy**; oracle lấy từ **đặc tả/contract, không từ code**; mỗi luồng 1 happy path + 4 edge case; mỗi ca ghi nguồn (`source`) theo trường của IEEE 829 |
| **Kỹ thuật** | BVA, EP lớp không hợp lệ (đơn lỗi), State Transition, đồng thời, IDOR, SQLi/XSS |

**Riêng `TC_TB_CAT_01`:** ca **happy path** của luồng Catalog. Contract API (`libs/internal-contracts/src/listings.ts`) cho phép gửi `sort` (gồm `price_asc`) cùng từ khóa `q`, nên kỳ vọng là: HTTP 200 và **giá không giảm dần**. Lần chạy chính thức `run7-final`: HTTP 200 nhưng giá `60000, 500000, 59000, 85000, 729000, 60000, 159000` → **FAIL**.

**Màn hình:** mở `C:\Users\NoNomt007\agentic-test-ops\testcases\trustbase_testcases.json`, `Ctrl+F` tìm `TC_TB_CAT_01`, chỉ vào `technique`, `expected`, `source`.

**Lời thoại:** "Bộ hồi quy 30 ca này do AI agent sinh ra từ đặc tả, contract API và cấu hình thật của TrustBase, theo V-Model: thiết kế và chốt kết quả mong đợi trước khi chạy, oracle lấy từ contract chứ không lấy từ code. Ca CAT_01 kiểm tra tìm kiếm có sắp xếp giá tăng dần. Server trả 200 nhưng thứ tự sai, bộ hồi quy báo fail. Giờ tôi giao cho agent tìm nguyên nhân."

---

## 3. Cảnh 2 + 3 — Agent tự điều tra theo Dual Trace (~2–3 phút)

Dán vào Claude Code (T4):

> Bộ hồi quy báo ca TC_TB_CAT_01 fail: tìm "windows" trên marketplace và chọn sắp xếp giá tăng dần nhưng giá hiện lộn xộn. Dùng các tool debug-controller: mở trang http://localhost:4200/vi/marketplace?q=windows&sort=price_asc trên trình duyệt có hiện cửa sổ để xác nhận triệu chứng, rồi tìm nguyên nhân gốc trong backend (API cổng 4201, debugger cổng 9229), có bằng chứng giá trị biến đọc trên RAM.

Prompt chỉ nêu mục tiêu và những gì agent không tự đoán được (trang nào, cổng nào, yêu cầu có bằng chứng trên RAM). Chọn tool, đặt breakpoint ở đâu, đọc biến nào là agent tự quyết; cách dùng `breakpoints` theo đoạn mã và `trigger` nó đọc từ mô tả của tool.

**Cảnh 2: Browser Trace (hộp đen).** Agent gọi `debug_browser_run` với `headless: false`:
- **Chrome bật lên trên màn hình**, mở trang tìm "windows", sắp xếp giá tăng dần;
- người xem **thấy giá lộn xộn** bằng mắt;
- tool trả về ảnh chụp và request giao diện đã gửi `GET /catalog/listings?q=windows&sort=price_asc` → **200**. Không có lỗi HTTP nào.

→ *Kết luận của tầng này:* giao diện gửi đúng tham số, server báo thành công, nhưng thứ tự sai, tức là lỗi nằm trong backend.

**Cảnh 3: Source Trace (hộp xám).** Agent đọc `api/src/modules/listings/listings.repo.ts`, tìm chỗ dựng `ORDER BY`, rồi gọi `debug_inspect_cdp`:
- breakpoint theo đoạn mã tại câu `.orderBy(` (dòng 412), `trigger` là một request tới `/catalog/listings?q=windows&sort=price_asc`;
- **một lời gọi** vừa gửi request vừa dừng tại câu đó và đọc trên RAM: `opts.q = "windows"`, `opts.sort = "price_asc"`.

→ *Kết luận:* server **có nhận** yêu cầu sắp xếp, nhưng dòng 413–415 viết `opts.q ? ts_rank_cd(...) : ORDER_BY[opts.sort]`: **hễ có từ khóa là chỉ sắp theo độ liên quan và bỏ qua `sort`**.

**Câu nhắc khi cần** (gõ thêm, vẫn tự nhiên như người dùng thật):
- Agent mới chạy trình duyệt rồi đọc code mà chưa gọi CDP: *"Xác nhận bằng debug_inspect_cdp."*
- Agent đọc ra `opts.q` rỗng (dừng nhầm vào một danh sách khác trang tự tải): *"Dùng trigger gọi thẳng API /catalog/listings?q=windows&sort=price_asc."*
- Muốn agent mở dòng code: *"Mở dòng đó trong VS Code bằng node C:\Users\NoNomt007\agentic-test-ops\scripts\open-in-vscode.mjs <file> \"<đoạn mã>\"."*

**Lời thoại:** "Trình duyệt thấy triệu chứng: giao diện gửi đúng tham số sắp xếp, server trả 200, nhưng giá lộn xộn. Không có lỗi HTTP nào nên test API thông thường bỏ sót. CDP vào bên trong backend: server có nhận `sort = price_asc`, nhưng code hễ có từ khóa là bỏ qua tham số này. Trình duyệt trả lời *lỗi gì*, CDP trả lời *vì sao*: đó là Dual Trace. Tôi chỉ đưa mục tiêu; chọn công cụ, đặt breakpoint, đọc biến nào là agent tự quyết."

Quay vài lần, giữ bản đẹp nhất; giữa hai lần chạy lại lệnh reset ở T3. Nếu agent đi lệch nhiều lần, dùng prompt từng bước ở Phụ lục A.

---

## 4. Cảnh 4 — Lập trình viên xác minh bằng debugger VS Code (human-in-the-loop, ~1 phút)

**Ý nghĩa:** agent đã chỉ ra dòng 412–415 của `listings.repo.ts`. Lập trình viên mở đúng chỗ đó và **tự xác minh bằng debugger quen thuộc**, gắn vào chính server đang chạy, không phải khởi động lại.

**Trước khi gắn:** agent ở cảnh 3 phải trả lời xong (tool CDP của agent tự nhả cổng 9229 sau mỗi lần gọi; cổng chỉ nhận một debugger tại một thời điểm). Kiểm tra ở T3, lệnh phải in ra một dòng `ws://127.0.0.1:9229/...`:
```powershell
(Invoke-RestMethod http://127.0.0.1:9229/json/list).webSocketDebuggerUrl
```

**Các bước:**
1. Trong VS Code (đang mở thư mục TrustBase), mở `api/src/modules/listings/listings.repo.ts`, `Ctrl+G` → **412** (dòng `.orderBy(`).
2. Bấm vào lề trái dòng 412 để đặt chấm đỏ. **Chuột phải vào chấm đỏ → Edit Breakpoint → Expression**, gõ:
   ```
   opts.q === 'windows'
   ```
   Nhấn Enter. Đây là **breakpoint có điều kiện**: trang marketplace tự gọi nhiều danh sách khác khi tải, điều kiện này bảo VS Code chỉ dừng ở đúng request tìm "windows".
3. Gắn debugger: `Ctrl+Shift+P` → gõ **Debug: Attach to Node Process** → chọn tiến trình có `src/main.ts` (API ở T2). Thanh trạng thái chuyển màu cam là đã gắn.
   - Không dùng cấu hình "🐛 API: Attach to Process" có sẵn của TrustBase: nó trỏ cổng 9237, còn API đang mở debugger ở 9229.
4. Gửi request **như người dùng thật**: mở trình duyệt, vào `http://localhost:4200/vi/marketplace?q=windows&sort=price_asc` (hoặc tải lại trang).
5. VS Code **dừng tại dòng 412** (dòng tô vàng). Quay khung **Variables**: mở `opts` thấy `q: "windows"`, `sort: "price_asc"`. Có thể rê chuột lên `opts.sort` ở dòng 415 cho người xem thấy giá trị ngay trong code.
6. Bấm **F10 (Step Over)** một lần nếu muốn cho thấy nhánh `opts.q ? ...` được chọn; hoặc bấm **F5 (Continue)** → trang hiện danh sách giá lộn xộn.
7. Bấm **Shift+F5** để ngắt debugger. **Bắt buộc** nếu còn cho agent chạy lại: cổng 9229 chỉ nhận một debugger.

**Lời thoại:** "Agent chỉ ra dòng 412. Lập trình viên đặt breakpoint có điều kiện ở đó, gắn debugger vào chính server đang chạy, rồi thao tác trên giao diện như người dùng. Debugger dừng đúng chỗ và cho thấy cùng giá trị agent đã đọc: `sort = price_asc` có tới server nhưng bị nhánh `opts.q` bỏ qua. AI khoanh vùng, con người xác minh."

---

## 5. Cảnh 5 — Báo cáo và kết quả tổng (~45 giây)

- Mở `C:\Users\NoNomt007\agentic-test-ops\knowledge\F-01-tham-so-sort-bi-bo-qua-khi-tim-kiem-co-t.md` (Preview trong VS Code): ca kiểm thử, triệu chứng, vị trí `listings.repo.ts:413`, nguyên nhân, đề xuất sửa. Mở file `.canvas` cùng tên trong Obsidian để xem sơ đồ.
- Mở `README.md` của agentic-test-ops, mục **8.0**: bộ 30 ca đạt 25/30, tìm ra 5 lỗi (F-01..F-05).

**Lời thoại:** "Hồ sơ lỗi được xuất bởi tool `debug_export_rag_report`, gồm file Markdown để người và AI đọc lại và file canvas để xem trực quan. Đây là kết quả lần chạy đầy đủ 30 ca ngày 24/11; bằng chứng của mọi lần chạy lưu trong `testcases/results/`."

**Lưu ý:**
- **Đừng bảo agent xuất báo cáo trong video:** tool export sẽ ghi đè `knowledge/F-01-...` của ngày 24/11.
- Nếu agent có chạy bộ test qua `debug_run_test`, file `testcases/results/latest.json` sẽ bị ghi đè (không đụng `run7-final.json`). Quay xong khôi phục:
  ```powershell
  cd C:\Users\NoNomt007\agentic-test-ops; git checkout -- testcases/results/latest.json
  ```

---

## Phụ lục A — Phương án dự phòng nếu agent đi lệch

**Prompt từng bước** (chắc chắn hơn nhưng trông giống "chỉ đạo" agent hơn):
> Dùng các tool của MCP server debug-controller để điều tra ca TC_TB_CAT_01.
> 1. Gọi debug_browser_run mở http://localhost:4200/vi/marketplace?q=windows&sort=price_asc với headless false, chờ 5 giây, chụp ảnh; báo lại request /catalog/listings và mã HTTP.
> 2. Đọc api/src/modules/listings/listings.repo.ts, tìm chỗ dựng ORDER BY trong hàm findMany.
> 3. Gọi debug_inspect_cdp (cổng 9229, pauseOnExceptions none) với breakpoint theo đoạn mã ".orderBy(" trong listings/listings.repo.ts, đọc opts.q và opts.sort, trigger là lệnh node gọi http://localhost:4201/catalog/listings?q=windows&sort=price_asc.
> 4. Kết luận nguyên nhân gốc: file, dòng và giá trị biến đọc được trên RAM.

**Lệnh dựng sẵn** (chạy ở T3; chứa đúng các tham số agent cần dùng):
```powershell
cd C:\Users\NoNomt007\agentic-test-ops; node scripts/mcp-call.mjs debug_browser_run '@testcases/demo/f01-browser.json'
```
Chrome hiện trang marketplace khoảng 5 giây, chụp ảnh vào `screenshots/`, trả về danh sách request.
```powershell
cd C:\Users\NoNomt007\agentic-test-ops; node scripts/mcp-call.mjs debug_inspect_cdp '@testcases/demo/f01-cdp.json'
```
Trả về `status: "PAUSED"`, `opts.q` và `opts.sort` trên RAM, và `trigger.output` liệt kê giá theo thứ tự API trả về.
```powershell
cd C:\Users\NoNomt007\agentic-test-ops; node scripts/open-in-vscode.mjs C:/Users/NoNomt007/Documents/trustbase/trustbase-project/api/src/modules/listings/listings.repo.ts 'ts_rank_cd('
```
Mở VS Code tại dòng 414, ngay trong khối `opts.q ? ... : ORDER_BY[opts.sort]`.

Trong PowerShell, tham số `'@testcases/...'` phải có nháy đơn (`@` đứng đầu là toán tử splatting).

---

## Phụ lục B — Xử lý sự cố

| Triệu chứng | Cách xử lý |
|---|---|
| Trang marketplace không hiện kết quả theo `q`/`sort` trên URL | Gõ "windows" vào ô tìm kiếm và chọn "Giá thấp → cao" bằng tay (hoặc để agent tự thao tác) |
| Agent hoặc VS Code dừng ở một lời gọi danh sách khác (`opts.q` rỗng) | Với agent: nhắc dùng `trigger` gọi thẳng API. Với VS Code: kiểm tra breakpoint có điều kiện `opts.q === 'windows'` |
| Chấm đỏ breakpoint trong VS Code là chấm rỗng, không dừng | VS Code chưa bám được source map của `tsx`: kiểm tra đang mở đúng thư mục TrustBase, ngắt (Shift+F5) rồi gắn lại; vẫn không được thì dùng lệnh `f01-cdp.json` ở Phụ lục A |
| Agent gọi `debug_inspect_cdp` báo "another debugger may already be attached" | VS Code vẫn đang gắn vào API: bấm Shift+F5 rồi chạy lại |
| Mọi request tới API đều treo | API đang dừng ở breakpoint: bấm F5 (Continue) trong VS Code, hoặc tắt và bật lại API ở T2 |
| API log báo `ECONNREFUSED ...:6379` / `5432`, hoặc lệnh treo không ra gì | WSL đã tự tắt: kiểm tra T1 còn chạy; nếu vẫn lỗi thì `wsl -e docker restart trustbase-postgres trustbase-redis`, rồi tắt và bật lại API ở T2 |
| Bị `429 RATE_LIMIT_EXCEEDED` | Chạy lại lệnh reset ở T3 |
| `debug_inspect_cdp` báo không tìm thấy target 9229 | API phải chạy bằng lệnh `tsx --inspect=...` ở T2, không dùng `pnpm dev` |
| `/mcp` không thấy `debug-controller` | Thoát hẳn Claude Code rồi mở lại; chạy `claude mcp list` để kiểm tra |
| Không chạy được TrustBase | Show kết quả đã lưu: `testcases/results/run7-final.json` (ca `TC_TB_CAT_01`) và `knowledge/F-01-*.md` |
