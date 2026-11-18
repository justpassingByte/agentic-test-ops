# Sổ Tay Kỹ Thuật & Hướng Dẫn Tích Hợp (Agentic TestOps Handbook)

> Tài liệu hướng dẫn thực hành đầy đủ: **Phương pháp luận Kiểm thử (Black-Box, Grey-Box / White-Box CDP, Coverage, Mutation Testing)**, cách **cài đặt & tích hợp vào một mã nguồn (`src`) bất kỳ**, **bộ Prompt thực chiến**, và **cách kiểm chứng bằng chứng thật** (không giả lập / không cap).

---

## Mục Lục
1. [Bức Tranh Kiến Trúc & Nguyên Lý Hoạt Động Thực Tế](#1-bức-tranh-kiến-trúc--nguyên-lý-hoạt-động-thực-tế)
2. [Hệ Thống Phương Pháp Luận & Kỹ Thuật Kiểm Thử](#2-hệ-thống-phương-pháp-luận--kỹ-thuật-kiểm-thử)
3. [Hướng Dẫn Cài Đặt & Tích Hợp Vào Một Mã Nguồn (`src`) Bất Kỳ](#3-hướng-dẫn-cài-đặt--tích-hợp-vào-một-mã-nguồn-src-bất-kỳ)
4. [Bộ Prompt Thực Chiến Cho Mọi Dự Án Web / Backend](#4-bộ-prompt-thực-chiến-cho-mọi-dự-án-web--backend)
5. [Xem Bằng Chứng Thực Thi & Sử Dụng Demo Trực Quan (No-Cap)](#5-xem-bằng-chứng-thực-thi--sử-dụng-demo-trực-quan-no-cap)
6. [Xử Lý Sự Cố Thường Gặp (Troubleshooting)](#6-xử-lý-sự-cố-thường-gặp-troubleshooting)

---

## 1. Bức Tranh Kiến Trúc & Nguyên Lý Hoạt Động Thực Tế

Agentic TestOps được đóng gói theo chuẩn **Model Context Protocol (MCP)** (`JSON-RPC 2.0 stdio`) với triết lý **100% Zero-Impact**: không cài thêm thư viện vào dự án mục tiêu (`target-src`), chỉ gắn ngoài để điều khiển trình duyệt và tiến trình Node.js runtime.

| Thành phần thực thi trong Repo | Vai trò kỹ thuật thực tế |
|---|---|
| `mcp/server.mjs` | MCP Server cung cấp **9 công cụ**: quản lý cổng (`debug_status`, `debug_kill_ports`), bật/tắt server kèm `--inspect` (`debug_start_server`, `debug_stop_server`), chạy Playwright (`debug_browser_run` hỗ trợ `contextId`, `headless`, `slowMo`), soi RAM qua CDP (`debug_inspect_cdp`), chạy test cô lập (`debug_run_test`), xuất RAG + Canvas (`debug_export_rag_report`, `debug_export_overnight_report`). |
| `mcp/cdp-client.mjs` | Client kết nối trực tiếp tới WebSocket `ws://127.0.0.1:<inspectPort>` của Node.js `--inspect`, bật `Debugger.setPauseOnExceptions`, đóng băng luồng khi văng Uncaught Exception, gọi `Debugger.evaluateOnCallFrame` để đọc giá trị biến trên Heap RAM và bóc tách Callstack rồi tự `Debugger.resume`. |
| `mcp/rag-exporter.mjs` | Xuất song song 2 định dạng trong `knowledge/`: **Markdown Defect Dossier (`.md`)** cho AI Semantic Memory và **Canvas Graph (`.canvas.json`)** chuẩn `SpawnClusterPayload` (nạp ~5ms vào Canvas Note Engineer, hỗ trợ biến môi trường `CANVAS_RAG_DIR`). |
| `agents/`, `skills/`, `commands/` | Bộ hướng dẫn điều phối cho AI Agent (`orchestrator`, `flow-worker`, `cdp-investigator`, `debugger`, `/debug`, `/overnight`), quy định chặt kỹ thuật thiết kế test và quy trình RCA 4 bước. |
| `vscode/` | Cấu hình `launch.json` và `tasks.json` cho phép lập trình viên nhấn **F5** trên VS Code để nhảy thẳng vào tiến trình đang mở `--inspect=9229/9230` (Human-in-the-loop). |

> **Lưu ý minh bạch:** Các file trong `agents/`, `commands/`, `skills/` là lớp điều phối (prompt orchestration) chạy bên trong một AI Host hỗ trợ MCP (như Antigravity IDE, Gemini CLI, Claude Code). Còn khi cần chạy định kỳ không cần AI (ví dụ trên CI/CD hoặc demo tự động 1-click), bạn chạy các script Playwright / Vitest hoặc workflow trong `.github/workflows/`.

---

## 2. Hệ Thống Phương Pháp Luận & Kỹ Thuật Kiểm Thử

Hệ thống kết hợp **Kiểm thử Hộp đen (Black-Box)** ở tầng giao diện/API và **Kiểm thử Hộp xám / Hộp trắng (Grey-Box / White-Box)** ở tầng runtime & bộ test hồi quy, tuân thủ mô hình **V-Model** và chuẩn **ISO/IEC/IEEE 29119 / 829**.

### 2.1. Kiểm thử Hộp đen (Black-Box Test Design — Tầng UI & API Contract)

Áp dụng trong `agents/flow-worker.md` và `skills/overnight-sweep/SKILL.md`:

1. **Happy Path (Main Flow):** Kiểm tra luồng nghiệp vụ chuẩn từ đầu đến cuối trước khi tiêm dữ liệu biên.
2. **Phân vùng tương đương (Equivalence Partitioning — EP) theo nguyên tắc Weak Robust EP:**
   - Chia miền dữ liệu thành các phân vùng Hợp lệ (*Valid*) và Không hợp lệ (*Invalid*).
   - Tuân thủ **Single Fault Assumption (Giả định đơn lỗi)**: mỗi ca kiểm thử chỉ gán **duy nhất 1 tham số** mang giá trị *Invalid*, tất cả tham số còn lại giữ *Valid*. Cách này triệt tiêu hoàn toàn hiện tượng **Che giấu lỗi (Fault Masking)** khi gửi nhiều trường sai cùng lúc khiến API chặn ở bước đầu và bỏ lọt lỗi ở bước sau.
3. **Phân tích giá trị biên (Boundary Value Analysis — BVA) 3 cấp độ:**
   - **Cấp 1 — Standard BVA ($4n + 1$ ca kiểm thử):** Kiểm tra 5 điểm $\{\min, \min^+, \text{nom}, \max^-, \max\}$ cho các biểu mẫu nhập liệu thông thường (độ dài tên, số lượng, khoảng giá).
   - **Cấp 2 — Robustness Testing ($6n + 1$ ca kiểm thử):** Bổ sung 2 giá trị vượt biên $\{\min^-, \max^+\}$ (ví dụ: số lượng `-1`, rút tiền `49.999đ` dưới ngưỡng tối thiểu `50.000đ`, hoặc vượt hạn mức tối đa) để kiểm định khả năng **Exception Handling**.
   - **Cấp 3 — Worst-Case Testing ($5^n$ ca kiểm thử):** Áp dụng **Multiple-fault assumption** (tổ hợp đồng thời nhiều giá trị biên) cho các module tài chính rủi ro cao (tính thuế, hoa hồng PPM dùng `BigInt`, ký quỹ Escrow, xếp chồng nhiều Voucher).
4. **Bảng quyết định (Decision Table Testing):**
   - Lập ma trận kết hợp điều kiện đa biến cho các nghiệp vụ rẽ nhánh phức tạp (ví dụ: *Trạng thái KYC Shop × Số dư khả dụng × Cấu hình ngân hàng VietQR*, hoặc *Hạng người bán × Giá thương lượng × Mã giảm giá*).
5. **Kiểm thử chuyển đổi trạng thái (State Transition Testing — FSM):**
   - Mô hình hóa vòng đời thực thể dưới dạng máy trạng thái hữu hạn (ví dụ: `PENDING -> ESCROW_HOLDING -> DELIVERED -> COMPLETED` hoặc `DISPUTED -> REFUNDED`).
   - Chủ động kích hoạt các **Invalid Transitions** (ví dụ: gửi lệnh rút tiền Payout khi đơn hàng đang `DISPUTED` hoặc `CANCELLED`) để kiểm chứng tính toàn vẹn nghiệp vụ.

### 2.2. Kiểm thử Hộp xám & Hộp trắng (Grey-Box / White-Box Analysis — CDP & Regression)

Đây là điểm khác biệt cốt lõi so với Playwright/Selenium thuần:

| Kỹ thuật | Cách Agentic TestOps thực thi |
|---|---|
| **Grey-Box Dual-Trace (UI + CDP Heap)** | Kích hoạt từ hành vi Black-Box trên trình duyệt (`debug_browser_run`) → khi bắt được HTTP `500` hoặc crash, chuyển sang **White-Box Runtime** bằng `debug_inspect_cdp` gắn vào `ws://127.0.0.1:9229`, đóng băng tiến trình tại dòng exception, đọc giá trị biến sống trên RAM (`Debugger.evaluateOnCallFrame`) và Callstack (`file:line:col`). |
| **Phủ cấp 1 (Statement Coverage)** | Khi Tầng 6 sinh bộ Regression Test cô lập (`.spec.ts`), bảo đảm 100% câu lệnh trong hàm/branch bị lỗi đều được thực thi ít nhất 1 lần. |
| **Phủ cấp 2 (Branch Coverage)** | Đảm bảo mọi nhánh điều kiện (`if/else`, `switch`, optional chaining `?.`, fallback `null/undefined`) đều có đủ ca kiểm thử cho cả nhánh `True` và `False`. |
| **Độ phức tạp chu trình McCabe** | Tính chỉ số $V(G) = P + 1$ (với $P$ là số điểm rẽ nhánh điều kiện) trên hàm nghi vấn để xác định số đường dẫn độc lập tối thiểu cần có trong bộ test hồi quy. |
| **Kiểm thử đột biến (Mutation Testing)** | Tiêm các đột biến nhân tạo (*Mutants*: đảo toán tử so sánh, đổi boolean, gán `null/undefined` cho biến biên) vào module trọng yếu để đo độ nhạy của bộ test tự sinh qua chỉ số:<br>`Mutation Score = (Killed Mutants / Total Mutants) x 100%`. |

### 2.3. Chuẩn V-Model & Chuỗi Lỗi ISO/IEEE 29119

- **Đối ứng V-Model (`agents/orchestrator.md`):**
  - **Validation** (*"Are we building the right system?"*): Tầng Playwright E2E mô phỏng hành vi Buyer / Seller / Admin trên giao diện thật.
  - **Verification** (*"Are we building the system right?"*): Tầng CDP Inspect + Unit/Integration Regression Test kiểm chứng tính đúng đắn bên trong mã nguồn và trạng thái bộ nhớ/DB.
- **Chuỗi truy vết sự cố chuẩn ISO/IEEE:**
  $$\text{Error (Mistake)} \longrightarrow \text{Fault / Defect (Code Line via CDP)} \longrightarrow \text{Failure (HTTP 500 / UI Crash)} \longrightarrow \text{Incident (Canvas Dossier)}$$
- **Vòng đời lỗi (Defect Life Cycle):** `New` → `Open` → `Investigating (CDP)` → `Fixed` → `Re-test` → `Closed` (nếu Pass) hoặc `Re-opened` (nếu Fail).

---

## 3. Hướng Dẫn Cài Đặt & Tích Hợp Vào Một Mã Nguồn (`src`) Bất Kỳ

Plugin hoạt động hoàn toàn độc lập (**Zero-Impact**), bạn **không cần `npm install` bất cứ thứ gì vào trong `src` dự án mục tiêu**.

### Bước 1: Cài đặt Agentic TestOps (chỉ làm 1 lần trên máy)

```powershell
# 1. Clone repo (hoặc giữ ở thư mục riêng ngoài dự án cần test)
git clone https://github.com/justpassingByte/agentic-test-ops.git
cd agentic-test-ops\mcp

# 2. Cài Playwright & trình duyệt Chromium
npm install
.\setup-browser.ps1    # Windows PowerShell
# Hoặc trên Linux / macOS:
# chmod +x setup-browser.sh && ./setup-browser.sh
```

> **Ghi chú:** Nếu máy đã có sẵn Google Chrome hoặc Microsoft Edge, `mcp/server.mjs` cũng tự động fallback sang Chrome/Edge ngay cả khi chưa tải xong Chromium của Playwright.

### Bước 2: Gắn MCP Server vào AI Agent (chọn công cụ bạn đang dùng)

#### Lựa chọn A — Antigravity IDE / Gemini CLI
1. Copy thư mục `agentic-test-ops` vào:
   - Toàn máy: `%USERPROFILE%\.gemini\config\plugins\agentic-test-ops\` (Windows) hoặc `~/.gemini/config/plugins/agentic-test-ops/` (Linux/macOS), **hoặc**
   - Cục bộ cho đúng dự án cần test: `<duong-dan-src-bat-ky>\.agents\plugins\agentic-test-ops\`
2. Hoặc khai báo trực tiếp trong file cấu hình MCP (`mcp_config.json`):
   ```json
   {
     "mcpServers": {
       "debug-controller": {
         "command": "node",
         "args": ["C:/Users/<TenUser>/agentic-test-ops/mcp/server.mjs"],
         "env": {
           "CANVAS_RAG_DIR": "C:/duong-dan/toi/plugin-canvas-engineer/rag"
         }
       }
     }
   }
   ```
   *(Biến `CANVAS_RAG_DIR` là tùy chọn; nếu có, báo cáo `.canvas.json` sẽ tự động đồng bộ sang Canvas Note Engineer).*

#### Lựa chọn B — Claude Code
```bash
# Cài dạng plugin
claude plugin install C:/Users/<TenUser>/agentic-test-ops

# Hoặc tạo file .mcp.json ở thư mục gốc của src cần test
```

#### Lựa chọn C — VS Code F5 Visual Debugging (Tùy chọn Human-in-the-loop)
Copy 2 file `vscode/launch.json` và `vscode/tasks.json` vào `<duong-dan-src-bat-ky>\.vscode\`. Khi Agent phát hiện dòng code nghi vấn, bạn chỉ cần đặt Breakpoint trong code của `src` và nhấn **F5** (*"F5: Attach to Node (Inspect Port 9229)"*) mà không cần restart server.

### Bước 3: Chuẩn bị `src` mục tiêu trước khi ra lệnh test

1. Nếu `src` dùng DB/Cache (Docker Compose, Postgres, Redis), hãy bật hạ tầng trước.
2. Cho phép Backend Node.js mở cổng `--inspect=0.0.0.0:9229` (để Agent dùng được kỹ thuật **Grey-Box / CDP Heap Trace**):
   - Bạn có thể tự bật backend trong `<target-src>` với biến môi trường:
     ```powershell
     $env:NODE_OPTIONS="--inspect=0.0.0.0:9229"
     pnpm dev:api
     ```
   - **Hoặc** để Agent tự bật hộ qua `debug_start_server({ command: 'pnpm dev:api', inspectPort: 9229, cwd: 'C:/path/to/src' })` (tool tự dọn cổng kẹt trước khi chạy).
3. Nếu `src` là Python / Java / Go / PHP (không phải Node.js): Tầng 1 (`debug_browser_run` — Black-Box UI/Network/Console/Screenshots) + Tầng 4–6 (`debug_export_rag_report`, `debug_run_test`, sinh Regression Test) vẫn hoạt động **100% bình thường**; chỉ riêng `debug_inspect_cdp` gắn heap RAM là dành riêng cho Node.js/V8 runtime (`--inspect`).

---

## 4. Bộ Prompt Thực Chiến Cho Mọi Dự Án Web / Backend

Bạn đứng ở thư mục `src` bất kỳ (sau khi gắn MCP `debug-controller`) và copy các mẫu prompt dưới đây, thay phần trong ngoặc `[...]` cho đúng dự án của bạn.

### Prompt 1 — Khảo sát `src` & Chạy Smoke Test trực quan trên Chrome thật
```text
Hãy đọc cấu trúc mã nguồn dự án tại [C:\path\to\my-project] để xác định cổng Frontend, Backend API và lệnh khởi động.
1. Gọi `debug_status` kiểm tra các cổng liên quan, dọn cổng kẹt nếu cần bằng `debug_kill_ports`.
2. Nếu server chưa chạy, khởi động Backend bằng `debug_start_server` với `inspectPort: 9229` và Frontend.
3. Dùng `debug_browser_run` với `headless: false`, `slowMo: 500` để mở trình duyệt trực tiếp trên màn hình qua luồng [đăng nhập / tìm sản phẩm / đặt hàng] tại [http://localhost:3000].
4. Báo cáo đúng sự thật mọi lỗi Console, HTTP >= 400 và đường dẫn ảnh chụp trong `screenshots/`. Không được tự suy diễn thành công nếu UI/API trả lỗi.
```

### Prompt 2 — Thiết kế & Chạy Bộ Test Black-Box Đầy Đủ (EP + BVA + Decision Table + FSM)
```text
Hãy đóng vai `flow-worker` và kiểm thử chức năng [Tên tính năng / Form / API, ví dụ: Rút tiền & Thanh toán] trên hệ thống tại [URL].
Áp dụng đầy đủ 5 bước thiết kế kiểm thử hộp đen:
- Phase A (Happy Path): Kiểm tra luồng chuẩn theo đặc tả trước.
- Phase B (BVA 3 cấp): Chạy Standard BVA (4n+1), Robustness BVA (6n+1 gồm min- và max+ để bắt lỗi xử lý ngoại lệ) và Worst-Case (5^n) cho các trường số/tiền tệ.
- Phase C (Weak Robust EP): Thực thi giả định đơn lỗi (mỗi request chỉ 1 biến invalid, các biến khác valid) để tránh Fault Masking.
- Phase D (Decision Table): Lập ma trận tổ hợp điều kiện nghiệp vụ (ví dụ: trạng thái tài khoản + số dư + mã giảm giá).
- Phase E (State Transition): Kiểm tra cả các chuyển đổi trạng thái không hợp lệ (Invalid Transitions).
Chạy các test case bằng `debug_browser_run` / `debug_run_test` và xuất bảng kết quả kèm `testingTechniques` qua `debug_export_rag_report`.
```

### Prompt 3 — Điều tra Lỗi 500 / UI Crash Theo Grey-Box / White-Box CDP
```text
Khi thực hiện thao tác [mô tả thao tác hoặc route bị lỗi] tại [URL], hệ thống bị lỗi [HTTP 500 / treo UI].
Hãy thực thi đúng quy trình RCA 4 bước:
1. Dùng `debug_browser_run` tái hiện lỗi trên trình duyệt để lấy `failedRequests`, `consoleErrors` và ảnh chụp lỗi trong `screenshots/`.
2. Kiểm tra Backend đang mở cổng `--inspect` (9229) chưa; gắn `debug_inspect_cdp` với `pauseOnExceptions: 'uncaught'` và danh sách biểu thức nghi vấn `expressions: [...]` rồi kích hoạt lại request lỗi để bắt Callstack (`file:line`) và giá trị biến sống trên RAM Heap.
3. Truy ngược về mã nguồn tại file mà CDP chỉ điểm để xác định nguyên nhân gốc (Root Cause), không vá ngọn.
4. Viết 1 Regression Test cô lập trong `tests/` tái hiện lỗi này, chạy xác minh bằng `debug_run_test`, và gọi `debug_export_rag_report` xuất hồ sơ `.md` + `.canvas.json` vào `knowledge/`.
```

### Prompt 4 — Sinh Bộ Test Hồi Quy Đạt Statement/Branch Coverage & Kiểm Định Mutation Testing
```text
Dựa trên các lỗi vừa phát hiện ở module [đường dẫn file service trong src], hãy:
1. Phân tích độ phức tạp chu trình McCabe V(G) = P + 1 của hàm bị lỗi.
2. Viết bộ Unit / Integration Regression Test hoàn chỉnh (Vitest / Jest / Playwright) đảm bảo 100% Phủ cấp 1 (Statement Coverage) và Phủ cấp 2 (Branch Coverage) cho các nhánh điều kiện biên (null/undefined/NaN/biên min-max).
3. Đề xuất hoặc chạy kiểm thử đột biến (Mutation Testing) với danh sách các đột biến (đổi toán tử, đảo boolean, bỏ null check) và chạy `debug_run_test` để tính Mutation Score thực tế.
```

### Prompt 5 — Quét Đa Luồng Song Song Qua Đêm (`/overnight`)
```text
/overnight --workers 3 --flows "[auth, catalog, checkout, payout]"
Hãy điều phối theo mô hình Orchestrator (V-Model):
- Chia luồng cho các worker dùng `contextId` độc lập ('worker-1', 'worker-2', 'worker-3') trong `debug_browser_run` để không đụng cookie/session.
- Gắn `debug_inspect_cdp` không chặn luồng (non-blocking) mỗi khi có HTTP 500.
- Tổng hợp kết quả cuối phiên bằng `debug_export_overnight_report`, xuất `knowledge/OVERNIGHT-SWEEP-<date>.md` và `.canvas.json` theo đúng Defect Lifecycle (New -> Open -> Investigating -> Fixed -> Re-test).
```

---

## 5. Xem Bằng Chứng Thực Thi & Sử Dụng Demo Trực Quan (No-Cap)

| Loại bằng chứng | Vị trí lưu | Cách mở & kiểm chứng sự thật |
|---|---|---|
| **Ảnh chụp màn hình thực tế** | `screenshots/*.png` | Mỗi khi chạy demo hoặc `debug_browser_run` gặp lỗi/lệnh `screenshot`, Playwright chụp nguyên khung DOM/VietQR/thông báo lỗi. Luôn đối chiếu ảnh với log HTTP để đảm bảo không lệch trạng thái. |
| **Tri thức lỗi Markdown (RAG)** | `knowledge/*.md` | Mở trực tiếp để đọc Matrix test case, Console error, Network failed request, Source location (`file:line`), và Heap RAM JSON. |
| **Bản đồ trực quan Canvas** | `knowledge/*.canvas.json` | Kéo thả file vào ứng dụng **Canvas Note Engineer** (hoặc set `CANVAS_RAG_DIR` để tự đồng bộ) — nạp trong ~5ms qua AST Parser để xem các Pod Xanh / Đỏ / Vàng / Tím. |
| **Demo trực quan trên Chrome (TrustBase)** | `CHAY_DEMO_AGENTIC_TESTOPS.bat` & `XUAT_BANG_CHUNG_TESTOPS.bat` | Bật `TrustBase` ở 3 cổng `4200`, `4201`, `4203` rồi chạy file `.bat`. Script mở Google Chrome thật (`headless: false`), **kiểm tra chặt chẽ URL, HTTP status và DOM** trước khi gắn overlay xanh; nếu kẹt eKYC hay sai mật khẩu Admin sẽ dừng và chụp ảnh lỗi `screenshots/error_*.png` thay vì báo ảo. *(Nếu muốn quay thêm `.webm`, truyền cờ `--record-video` vào `record_multi_role_detailed_demo.mjs`)*. |

---

## 6. Xử Lý Sự Cố Thường Gặp (Troubleshooting)

1. **`Executable doesn't exist` khi chạy `debug_browser_run`:**
   - Chạy `cd mcp && .\setup-browser.ps1` (hoặc cài Google Chrome / Edge vì bản vá mới của `mcp/server.mjs` tự động fallback sang `channel: 'chrome'` / `'msedge'`).
2. **`listen EADDRINUSE` khi bật server `src`:**
   - Yêu cầu Agent gọi `debug_status` và `debug_kill_ports({ ports: [4200, 4201, 4203, 9229] })` hoặc chạy VS Code Task *"Kill Debug Ports"*.
3. **`debug_inspect_cdp` báo không tìm thấy target ở cổng `9229`:**
   - Kiểm tra Backend có thực sự được khởi chạy bằng `NODE_OPTIONS="--inspect=0.0.0.0:9229"` (hoặc `--inspect=9229`) không, và thử mở `http://127.0.0.1:9229/json/list` xem có JSON trả về không.
4. **Demo E2E báo lỗi khóa KYC hoặc Admin Login thất bại:**
   - Kiểm tra trạng thái dữ liệu seed trong PostgreSQL:
     - Nếu `seller1` bị khóa eKYC trên `TrustBase`, chạy `python update_kyc.py` (hoặc dùng chính kết quả khóa KYC đó để minh họa Defect `DEF-001`!).
     - Kiểm tra mật khẩu `admin@trustbase.local` (script E2E hỗ trợ biến môi trường `TRUSTBASE_ADMIN_PASSWORD` nếu mật khẩu DB khác mặc định).
5. **File `.canvas.json` không tự chép sang Canvas Note Engineer:**
   - Đặt biến môi trường `CANVAS_RAG_DIR=<đường-dẫn-đến-thư-mục-rag-của-canvas-note-engineer>` hoặc truyền trực tiếp tham số `canvasRagDir` khi gọi tool.
