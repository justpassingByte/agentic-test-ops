# Ôn tập vấn đáp — Agentic TestOps (Nhóm 05)

Tài liệu ôn tập trọng tâm. Mọi con số dưới đây đều có dữ liệu gốc trong repo: `testcases/results/run7-final.json`, `knowledge/`, `testcases/cdp-*.json`.

---

## 1. Giới thiệu 60 giây (học thuộc)

> "Agentic TestOps là một **MCP server** viết bằng Node.js, giao tiếp JSON-RPC 2.0 qua stdio, cung cấp **9 công cụ** cho AI Agent: điều khiển trình duyệt (Playwright), quản lý tiến trình và cổng, chạy test, **gắn vào backend Node.js qua Chrome DevTools Protocol** để đọc callstack và giá trị biến trên RAM, và xuất báo cáo `.md` / `.canvas`.
> Nhóm áp dụng nó lên **TrustBase** chạy local với bản sao dữ liệu production: thiết kế lại 30 ca kiểm thử theo đặc tả thật, chạy qua công cụ `debug_run_test`, đạt **25/30**, tìm ra **5 lỗi thật** của TrustBase (1 High, 3 Medium, 1 Low), mỗi lỗi chỉ được tới file và dòng code."

Câu then chốt: **code của nhóm = công cụ; trí tuệ = LLM của AI host; quy trình = prompt** (`agents/`, `skills/`, `commands/`).

---

## 2. Kiến trúc: nói đúng cái gì là code

| Tầng (slide) | Hiện thực | Bản chất |
|---|---|---|
| 1. Browser | `debug_browser_run` ([mcp/server.mjs](mcp/server.mjs)) | Code |
| 2. Debug session / CDP | `debug_start_server`, [mcp/cdp-client.mjs](mcp/cdp-client.mjs) | Code |
| 3. RCA 4 bước | [skills/debug-rca/SKILL.md](skills/debug-rca/SKILL.md) | Prompt (LLM suy luận) |
| 4. "RAG" | File `knowledge/*.md`; agent tự đọc lại, **chưa có vector search** | Quy ước lưu file |
| 5. Xuất báo cáo | [mcp/rag-exporter.mjs](mcp/rag-exporter.mjs): `.md` + `.canvas.json` + `.canvas` (Obsidian) | Code |
| 6. Regression test | [tests/trustbase/trustbase.test.mjs](tests/trustbase/trustbase.test.mjs), chạy bằng `debug_run_test` | Code test |

Cách gọi công cụ trong thực nghiệm: [scripts/mcp-call.mjs](scripts/mcp-call.mjs) là client MCP nói đúng giao thức host dùng (`initialize` → `tools/call`). `.mcp.json` có sẵn để Claude Code nạp server trực tiếp.

---

## 3. Kết quả thực nghiệm (phải thuộc)

**Môi trường:** TrustBase local (API 4201 kèm `--inspect=127.0.0.1:9229`, customer 4200), PostgreSQL 18 và Redis 7 bằng Docker. Dữ liệu là bản sao dump production 18/11/2026. Email chuyển sang chế độ console, thanh toán mock, tắt web push, nên không đụng tới người dùng thật hay production.

**Lần chạy chính thức `run7-final`:** **25/30 đạt (83,3%)**, 5 không đạt, 0 bị chặn, 0 lỗi 5xx, chạy hết 308,6 giây.
Theo luồng: Auth 5/5 · Order 5/5 · Payout 5/5 · Catalog 4/5 · Voucher 3/5 · Dispute 3/5.

| Mã | Lỗi | Mức | Nguyên nhân gốc | Bằng chứng |
|---|---|---|---|---|
| **F-02** | Mở được khiếu nại trên đơn **chưa thanh toán** | High | `awaiting_payment` và `funds_held` cùng ánh xạ thành `CHO_CK`, mà `CHO_CK` nằm trong `ALLOWED_OPEN_STATUSES` | **CDP breakpoint**: `order.status=awaiting_payment`, `orderStatus=CHO_CK` |
| **F-03** | Người ngoài dò được trạng thái khiếu nại đơn người khác (403 khi chưa có, 409 khi đã có) | Medium | `openDispute` kiểm "đã có khiếu nại" **trước** khi kiểm quyền (dòng 142 so với 167) | run5 so với run6/run7 |
| **F-01** | `sort=price_asc` bị bỏ qua khi có từ khóa | Medium | `listings.repo.ts:413`: có `q` thì chỉ sắp theo `ts_rank_cd` | Giá trả về 60000, 500000, 59000… |
| **F-05** | Tạo 5 đơn/phút làm bị chặn mở khiếu nại (429) | Medium | `orderCreateLimiter` và `financialOpsLimiter` dùng chung khóa Redis `rl:financial:<user>` | Bộ đếm Redis = 5 → khiếu nại trả 429 |
| **F-04** | Mã lỗi voucher chung chung `VOUCHER_INVALID` | Low | Luồng tạo đơn gộp các mã cụ thể thành một | Thông báo đúng, mã sai kỳ vọng |
| E-01 | HTTP 500 ở `/catalog/categories` và khi tạo đơn | Môi trường | Dump thiếu migration 87–89; CDP chỉ ra `column ... does not exist` | Đã `pnpm db:migrate` |

---

## 4. Câu hỏi trọng tâm và cách trả lời

**Q1. Vì sao chạy tới 7 lần? Có phải chạy đến khi đẹp số không?**
Không. Kết quả mong đợi được **chốt trong `testcases/trustbase_testcases.json` trước lần chạy đầu** và không đổi. Mỗi lần chạy lại chỉ để gỡ một nguyên nhân không thuộc sản phẩm:
- run1: sai cú pháp lệnh, không ca nào chạy.
- run2: DB thiếu migration.
- run3: hết hạn mức rate limit.
- run4: thiết kế luồng voucher sai.
- run5: lỗi fixture.
- run6: stub adapter khác production.

Mọi lần chạy đều lưu trong `testcases/results/`. Lần duy nhất có sửa thiết kế được ghi rõ trong `designRevisions`: **chỉ sửa bước thực hiện, giữ nguyên kết quả mong đợi**. VCH_03/04 vẫn FAIL vì nhóm không đổi kỳ vọng sau khi thấy kết quả.

**Q2. Oracle (kết quả mong đợi) lấy từ đâu?**
Từ đặc tả và cấu hình thật, **không lấy từ code**: `docs/admin-rules.md`, `seller-studio-rules.md`, `digital-auto-delivery.md`, contract zod (`users.schemas.ts`, `orders.schemas.ts`, `disputes.ts`), bảng `system_settings` (ví dụ `payout:min_amount_vnd = 50000`). Mỗi ca có trường `source`. Nếu suy kỳ vọng từ code thì test thành vòng lặp (code đúng theo chính nó).

**Q3. CDP giúp gì mà Playwright không làm được? Trình bày F-02.**
Playwright chỉ thấy `201 SUCCESS`. CDP dừng tại đúng câu lệnh `ALLOWED_OPEN_STATUSES.includes(orderStatus)` và đọc biến trên RAM: trạng thái thật là `awaiting_payment` nhưng được ánh xạ thành `CHO_CK`, nên lọt qua kiểm tra. Với lỗi 500 (E-01), CDP chỉ ra ngay câu SQL thiếu cột mà không cần đọc log.

**Q4. Công cụ CDP có hạn chế gì, nhóm xử lý ra sao?**
1. Mặc định `uncaught` không bắt được lỗi 500 vì framework đã bắt exception → đổi mặc định sang `all` và bỏ qua frame trong `node_modules`.
2. `npm`/`pnpm` chiếm cổng inspect khi dùng `NODE_OPTIONS` → tool từ chối kèm hướng dẫn; chạy `tsx --inspect` trực tiếp.
3. Chỉ dừng ở exception **đầu tiên**, dễ dính nhiễu (thư viện JWT tự ném rồi tự bắt) → thêm `exceptionFilter`.
4. `tsx` biên dịch file thành 2 dòng nên breakpoint theo dòng TypeScript không gắn được → thêm **breakpoint theo đoạn mã** (`match`).
5. URL frame rỗng với ES module → tra theo `scriptId`.
6. Agent gọi tool lần lượt, nên không thể vừa nghe CDP vừa gửi request lỗi → thêm tham số **`trigger`**: tool gắn breakpoint xong mới tự chạy lệnh tái hiện (ví dụ 1 ca test). **Một lời gọi** trả về cả output của lệnh lẫn giá trị trên RAM, nên agent tự điều tra trọn vẹn được.

Khi pause, toàn bộ event loop dừng vài chục ms; chỉ dùng ở môi trường test, bind `127.0.0.1`.

**Q5. Weak Robust EP, BVA, FSM áp dụng cụ thể ở đâu?**
- **BVA**: mật khẩu 7/8 ký tự, từ khóa 200/201 ký tự, quantity 0 và quantity bằng kho+1, gross 18/19 chữ số, lý do khiếu nại 19/20 ký tự, voucher có đơn tối thiểu 50.000/50.001, rate limit lần 5/lần 6.
- **EP lớp không hợp lệ**: email ngoài whitelist, `sort` sai enum, voucher hết hạn, hạng người bán lạ.
- **FSM**: refresh sau logout-all, hủy đơn chưa trả tiền, khiếu nại đơn chưa trả tiền, khiếu nại trùng.
- **Đồng thời**: 2 người mua 1 mã cuối → đúng 1 đơn thành công (ORD_05 PASS).
- **Bảo mật**: IDOR (DSP_03), SQLi/XSS (CAT_05; XSS kiểm trên giao diện bằng `debug_browser_run`).
- Weak Robust = mỗi ca chỉ **một** biến sai, các biến khác hợp lệ, để tránh che giấu lỗi (fault masking).

**Q6. Chạy trên dữ liệu production có an toàn không?**
Chỉ chạy trên **bản sao local**. Đã kiểm tra API chỉ kết nối localhost. Đổi `EMAIL_PROVIDER=console`, `PAYMENT_PROVIDER=mock`, `WEB_PUSH_ENABLED=false`. Chỉ dùng tài khoản demo. Fixture (`testcases/trustbase-fixtures.sql`) và bước reset (`reset-local-env.sh`) chỉ chạm vào container local. Bộ test **từ chối chạy** nếu URL API không phải localhost.

**Q7. MCP là gì, vì sao tự viết JSON-RPC?**
Là giao thức chuẩn để AI host phát hiện và gọi tool (`tools/list`, `tools/call`, `inputSchema` JSON Schema), transport stdio. Tự viết khoảng 100 dòng để không phụ thuộc thư viện và giải thích được giao thức. Đánh đổi: chưa hỗ trợ resources/prompts/progress. Lưu ý **không được `console.log` ra stdout** vì sẽ làm hỏng luồng JSON-RPC.

**Q8. "RAG" ở đâu?**
Hiện là kho tri thức dạng file `.md` có cấu trúc; agent tự đọc lại. Chưa có embedding hay tìm kiếm vector, đó là hướng phát triển. Đừng nói "AI tự học".

**Q9. Coverage, McCabe, mutation đã đo chưa?**
**Chưa**. Đó là phương pháp nhóm trình bày và là hướng tiếp theo (c8 cho coverage, StrykerJS cho mutation). Nhớ công thức: Mutation Score = mutant bị diệt / (tổng mutant − mutant tương đương). V(G) = E − N + 2P (P là số thành phần liên thông) = số nút quyết định nhị phân + 1.

**Q10. Verification và Validation khác nhau thế nào?**
Verification = làm đúng theo đặc tả (review, unit, integration, system test). Validation = làm đúng thứ người dùng cần (acceptance, UAT). Test E2E so với đặc tả **vẫn là verification**; nói "gần với validation nhất trong phạm vi nhóm" thì an toàn.

**Q11. Error, Fault, Failure khác nhau thế nào? Lấy ví dụ từ kết quả.**
- Error: lập trình viên ánh xạ `awaiting_payment` thành `CHO_CK`.
- Fault: dòng ánh xạ trong `postgres-backbone.adapter.ts`.
- Failure: API trả 201 cho khiếu nại trên đơn chưa trả tiền.
- Incident: hồ sơ `knowledge/F-02-*.md`.

**Q12. Hạn chế và hướng phát triển?**
- Chưa đo coverage/mutation; chưa có vector RAG.
- CDP chỉ dùng cho Node/V8; mở rộng bằng Debug Adapter Protocol (debugpy, delve...) cho ngôn ngữ khác.
- CI chưa chạy được SUT TrustBase (cần hạ tầng riêng); CI hiện kiểm chính công cụ.

---

## 5. Điểm phải chủ động thừa nhận

- Tài liệu cũ từng có Defect Log và số liệu **không có cơ sở**. Nhóm đã xóa hết và chạy lại thật; các file mẫu cũ trỏ tới code không tồn tại trong TrustBase.
- 5 lỗi F-01..F-05 **chưa được sửa** vì nằm trong code TrustBase; trạng thái là Open.
- F-02 cần PO xác nhận chủ đích: có thể nhằm hỗ trợ "đã chuyển khoản nhưng chưa ghi nhận", nhưng hiện không ràng buộc với category `PAYMENT_ISSUE`.
- Quan sát thêm (không phải lỗi theo oracle): ước tính payout với hạng lạ `platinum` cho hoa hồng 4%, thấp hơn hạng bronze (7%).

---

## 6. Kịch bản demo

Xem [KICH_BAN_DEMO.md](KICH_BAN_DEMO.md): chuẩn bị môi trường, 5 cảnh khoảng 4 phút (chạy 1 ca DSP_04 qua `debug_run_test` → FAIL, CDP breakpoint đọc biến trên RAM, báo cáo Obsidian), lời thoại và cách xử lý sự cố.

Dự phòng nếu demo hỏng: kết quả đã lưu ở `testcases/results/run7-final.json` và `testcases/cdp-dsp04-breakpoint.json`.
