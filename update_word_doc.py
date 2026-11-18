# -*- coding: utf-8 -*-
"""
Cập nhật & Chuẩn hóa Báo cáo Word Nhom05_AgenticTestOps.docx (Idempotent):
1. Dọn sạch PHẦN 5 bị trùng lặp (nếu có) trước khi ghi lại.
2. Cập nhật Mục lục, thông số cổng TrustBase (4200 / 4201 / 4203), và bổ sung đầy đủ
   kỹ thuật kiểm thử (Black-Box BVA 3 cấp, Weak Robust EP, Decision Table, FSM;
   Grey/White-Box CDP Heap, Statement & Branch Coverage, McCabe V(G), Mutation Testing, V-Model).
3. Đồng bộ MSSV (21130535, 22130229, 22130234) thống nhất từ Trang bìa tới Phần 5 & Slide PPTX.
4. Loại bỏ nội dung video giả lập, thay bằng quy trình kiểm chứng DOM/HTTP thật & Ảnh thực tế.
5. Bổ sung PHẦN 6: Sổ tay cài đặt & Bộ Prompt áp dụng cho một mã nguồn (src) bất kỳ (Handbook).
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def style_table(table, col_widths, bg_hex="1B365D"):
    for i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if i == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

        for j, cell in enumerate(row.cells):
            cell.width = Inches(col_widths[j])
            tcPr = cell._tc.get_or_add_tcPr()
            tcMar = OxmlElement('w:tcMar')
            for m in ['top', 'bottom']:
                node = OxmlElement(f'w:{m}')
                node.set(qn('w:w'), '120')
                node.set(qn('w:type'), 'dxa')
                tcMar.append(node)
            for m in ['left', 'right']:
                node = OxmlElement(f'w:{m}')
                node.set(qn('w:w'), '160')
                node.set(qn('w:type'), 'dxa')
                tcMar.append(node)
            tcPr.append(tcMar)

            if i == 0:
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_hex}"/>')
                tcPr.append(shd)
            elif i % 2 == 1:
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
                tcPr.append(shd)


def remove_element(el):
    parent = el.getparent()
    if parent is not None:
        parent.remove(el)


def strip_old_part5_and_part6(doc):
    """Xóa mọi PHẦN 5 / PHẦN 6 cũ (và ngắt trang ngay trước nó) để script chạy lặp không bị trùng."""
    body = doc.element.body
    children = list(body)
    cut_index = None

    for idx, child in enumerate(children):
        if child.tag.endswith('}p'):
            text = ''.join(child.itertext()).strip()
            if text.startswith('PHẦN 5:') or text.startswith('PHẦN 5.'):
                # Nếu ngay phía trước là paragraph chứa page break thì cắt từ đó luôn
                if idx > 0 and children[idx - 1].tag.endswith('}p'):
                    prev_text = ''.join(children[idx - 1].itertext()).strip()
                    prev_xml = etree_xml(children[idx - 1])
                    if not prev_text and ('w:br' in prev_xml or 'pageBreakBefore' in prev_xml):
                        cut_index = idx - 1
                        break
                cut_index = idx
                break

    if cut_index is not None:
        for child in children[cut_index:]:
            if not child.tag.endswith('}sectPr'):
                remove_element(child)


def etree_xml(el):
    return el.xml if hasattr(el, 'xml') else ''


def set_paragraph_text_preserve_style(p, text, font_size=11):
    p.clear() if hasattr(p, 'clear') else None
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(font_size)


def update_doc(doc_path):
    doc = docx.Document(doc_path)

    # 1. Xóa sạch PHẦN 5 / PHẦN 6 cũ (tránh lặp 2 lần như bản trước)
    strip_old_part5_and_part6(doc)

    # 2. Đồng bộ các mục chính trong Phần 1-4 để phản ánh đúng kiến trúc & kỹ thuật mới
    for p in doc.paragraphs:
        txt = p.text
        if txt.startswith("PHẦN 1: TÀI LIỆU TÓM TẮT") and "PHẦN 4:" in txt:
            new_toc = (
                txt.rstrip() + "\n"
                "PHẦN 5: KẾ HOẠCH BÁO CÁO BẢO VỆ ĐỒ ÁN, TỰ ĐÁNH GIÁ VÀ VẤN ĐÁP\n"
                "    5.1 Bảng tự đánh giá đóng góp của các thành viên nhóm (Thang điểm 10)\n"
                "    5.2 Tóm tắt cấu trúc bộ Slide trình chiếu báo cáo (10 slides chuẩn)\n"
                "    5.3 Kịch bản báo cáo và Demo thực tế trong thời gian tối đa 10 phút\n"
                "    5.4 Bộ câu hỏi vấn đáp phản biện thường gặp (Q&A FAQ)\n"
                "PHẦN 6: SỔ TAY CÀI ĐẶT & BỘ PROMPT ÁP DỤNG CHO MÃ NGUỒN (SRC) BẤT KỲ (HANDBOOK)"
            )
            set_paragraph_text_preserve_style(p, new_toc, font_size=11)
        elif "Admin Portal:" in txt and "port 4201" in txt:
            updated = (
                "Hệ thống mục tiêu được chọn để kiểm thử thực nghiệm là TrustBase – một nền tảng sàn thương mại điện tử "
                "chuyên biệt cho các sản phẩm số (Digital Products, Game Keys, License Software, Dịch vụ số) với cơ chế bảo vệ giao dịch tín nhiệm cao (Trust Score & Escrow Protection).\n"
                "Kiến trúc kỹ thuật thực tế của TrustBase bao gồm:\n"
                "• Customer & Seller Portal: Ứng dụng web người mua/bán xây dựng trên React/Next.js (cổng 4200).\n"
                "• Admin Console: Giao diện quản trị, kiểm duyệt eKYC, phân xử tranh chấp và giải ngân chi trả (cổng 4203).\n"
                "• API Backend Server: Máy chủ dịch vụ trung tâm phát triển bằng Node.js / TypeScript (cổng 4201), sử dụng PostgreSQL 15 (cổng 5432) và Redis 7 (cổng 6379).\n"
                "Mục tiêu kiểm thử: Đánh giá độ tin cậy, an toàn giao dịch, tính đúng đắn của logic tính toán chiết khấu, eKYC gate và dòng tiền rút ví của người bán, ngăn chặn triệt để Race Condition và lỗi ngoại lệ làm sập server."
            )
            set_paragraph_text_preserve_style(p, updated, font_size=11.5)
        elif txt.startswith("Chiến lược kiểm thử kết hợp toàn diện giữa kiểm thử hộp đen"):
            updated = (
                "Chiến lược kiểm thử kết hợp chặt chẽ giữa Kiểm thử Hộp đen E2E theo V-Model (Validation) và Kiểm thử Hộp xám / Hộp trắng tích hợp CDP (Verification):\n"
                "• Kiểm thử chức năng Hộp đen (Black-Box): Flow Worker điều khiển Playwright Chrome chạy theo kịch bản Happy Path, Weak Robust EP, BVA 3 cấp (4n+1, 6n+1, 5^n), Decision Table và State Transition (cả Valid/Invalid Transitions).\n"
                "• Kiểm thử Hộp xám / Hộp trắng qua CDP: Gắn cdp-client vào tiến trình Node.js --inspect (port 9229) để đóng băng exception, soi biến trực tiếp trên Heap RAM và bóc tách Callstack.\n"
                "• Đo lường Độ phủ & Đột biến: Bộ test hồi quy Tầng 6 đạt Phủ cấp 1 (Statement Coverage), Phủ cấp 2 (Branch Coverage 100%), phân tích độ phức tạp chu trình McCabe V(G) = P + 1 và đạt Mutation Score 91.67% (tiêu diệt 22/24 đột biến).\n"
                "• Kiểm thử đồng thời & ngâm tải (Concurrency & Overnight Sweep): Mô phỏng mua key cuối cùng đồng thời để phát hiện race condition và chạy quét đa context (worker-1..3) dò rò rỉ bộ nhớ.\n"
                "• Kiểm thử hồi quy & bằng chứng ảnh: Tự động sinh file .spec.ts, xuất Tri thức kép (.md + .canvas.json) và lưu ảnh chụp xác thực DOM/HTTP tại screenshots/."
            )
            set_paragraph_text_preserve_style(p, updated, font_size=11.5)
        elif txt.startswith("Bộ ca kiểm thử được thiết kế khoa học bám sát 6 luồng"):
            updated = (
                "Bộ ca kiểm thử được thiết kế khoa học theo chuẩn ISTQB / IEEE 829 bám sát 6 luồng nghiệp vụ của TrustBase:\n"
                "• Phân vùng tương đương (Weak Robust EP - Single Fault Assumption): Mỗi ca kiểm thử chỉ gán duy nhất 1 biến nhận giá trị Invalid (các biến khác giữ Valid) nhằm triệt tiêu hiện tượng che giấu lỗi (Fault Masking).\n"
                "• Phân tích giá trị biên (BVA 3 cấp độ): Standard BVA (4n+1) cho biểu mẫu thường; Robustness BVA (6n+1) mở rộng min-/max+ kiểm thử Exception Handling (hạn mức rút tối thiểu 50.000đ); Worst-Case BVA (5^n) cho phép tính tài chính BigInt & Escrow.\n"
                "• Bảng quyết định (Decision Table): Lập ma trận tổ hợp điều kiện đa biến cho luồng rút tiền (Trạng thái eKYC x Số dư khả dụng x Ngân hàng VietQR) và áp mã giảm giá.\n"
                "• Kiểm thử chuyển đổi trạng thái (State Transition - FSM): Kiểm thử cả bước chuyển hợp lệ (PENDING -> ESCROW_HOLDING -> DELIVERED -> COMPLETED) lẫn bước chuyển phi lý (Invalid Transitions như giải ngân khi đang DISPUTED).\n"
                "• Kiểm thử Hộp trắng & Đột biến (Coverage & Mutation): Đánh giá Phủ cấp 1 (Statement), Phủ cấp 2 (Branch True/False), McCabe V(G) và Mutation Testing."
            )
            set_paragraph_text_preserve_style(p, updated, font_size=11.5)

    # Helper functions cho PHẦN 5 & PHẦN 6
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(27, 54, 93)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 76, 129)
        return p

    def add_p(text, bold_prefix=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.25
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = "Times New Roman"
            r_b.font.size = Pt(12)
            r_b.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.25
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = "Times New Roman"
            r_b.font.size = Pt(12)
            r_b.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        return p

    # =========================================================================
    # PHẦN 5: KẾ HOẠCH BÁO CÁO BẢO VỆ ĐỒ ÁN VÀ TỰ ĐÁNH GIÁ THÀNH VIÊN
    # =========================================================================
    doc.add_page_break()

    add_h1("PHẦN 5: KẾ HOẠCH BÁO CÁO BẢO VỆ ĐỒ ÁN VÀ TỰ ĐÁNH GIÁ THÀNH VIÊN")

    add_h2("5.1 Bảng tự đánh giá đóng góp của các thành viên nhóm (Thang điểm 10)")
    add_p(
        "Nhóm 05 gồm 03 thành viên, đã phân công trách nhiệm rõ ràng theo năng lực chuyên môn. Toàn bộ các hạng mục nghiên cứu lý thuyết, xây dựng MCP Server, hoàn thiện bộ kỹ thuật Hộp đen / Hộp trắng / Đột biến, chạy kiểm thử trên TrustBase, xây dựng pipeline CI/CD, sổ tay HANDBOOK.md, slide thuyết trình và báo cáo Word/Excel đều hoàn thành đầy đủ."
    )

    table_eval = doc.add_table(rows=1, cols=6)
    headers = ["STT", "Họ và Tên", "MSSV", "Vai trò", "Nhiệm vụ và Sản phẩm bàn giao", "Điểm tự chấm (Thang 10)"]
    for j, h in enumerate(headers):
        cell = table_eval.rows[0].cells[j]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.font.name = "Times New Roman"
        run.font.size = Pt(10.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)

    eval_data = [
        ("1", "Nguyễn Hữu Thắng", "21130535", "Nhóm trưởng\nTest Lead",
         "- Nghiên cứu kiến trúc Agentic TestOps 6 tầng & chuẩn MCP JSON-RPC 2.0.\n"
         "- Xây dựng MCP Server (mcp/server.mjs) điều khiển Playwright & Node Inspect.\n"
         "- Thiết lập kịch bản E2E đa phân vai có kiểm chứng DOM/HTTP (không giả lập).\n"
         "- Xây dựng CI/CD GitHub Actions & Sổ tay tích hợp HANDBOOK.md.\n"
         "- Chủ trì thuyết trình báo cáo và điều phối phần demo trực tiếp.",
         "10.0 / 10\n(Đóng góp 100%)"),
        ("2", "Phạm Trần Nhựt Quang", "22130229", "QA Engineer\nTest Designer",
         "- Thiết kế bộ Test Suite 30 Test Cases theo chuẩn IEEE 829 / ISO 29119.\n"
         "- Áp dụng 4 kỹ thuật Hộp đen: Weak Robust EP, BVA 3 cấp (4n+1, 6n+1, 5^n), Decision Table, FSM.\n"
         "- Xây dựng cơ chế chống Flaky Test (Port Zombie Killer, find-polluter bisect).\n"
         "- Kiểm chứng dữ liệu hạt giống TrustBase (PostgreSQL) & Ma trận truy vết RTM.\n"
         "- Chuẩn bị nội dung phản biện kỹ thuật và bộ câu hỏi vấn đáp.",
         "9.5 / 10\n(Đóng góp 100%)"),
        ("3", "Huỳnh Văn Sĩ", "22130234", "CDP Debugger &\nQuality Analyst",
         "- Phát triển cdp-client.mjs kết nối WebSocket ws://9229 soi biến RAM Heap.\n"
         "- Xây dựng rag-exporter.mjs xuất Tri thức kép (.md RAG & .canvas.json AST 5ms).\n"
         "- Thiết kế test hồi quy Hộp trắng (Phủ cấp 1/2, McCabe V(G), Mutation Testing).\n"
         "- Biên tập bảng nhật ký lỗi (Defect Log), Dashboard KPI & bảo mật.\n"
         "- Duy trì hạ tầng Docker (PostgreSQL, Redis) và hoàn thiện slide/báo cáo.",
         "9.5 / 10\n(Đóng góp 100%)")
    ]

    for data in eval_data:
        row = table_eval.add_row()
        for col_idx, val in enumerate(data):
            cell = row.cells[col_idx]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [0, 2, 5] else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            if col_idx in [1, 5]:
                run.font.bold = True
                if col_idx == 5:
                    run.font.color.rgb = RGBColor(27, 54, 93)

    style_table(table_eval, [0.5, 1.3, 0.9, 1.1, 2.7, 1.1])
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_h2("5.2 Tóm tắt cấu trúc bộ Slide trình chiếu báo cáo (10 slides chuẩn)")
    add_p(
        "Bộ Slide trình chiếu PowerPoint (Nhom05_AgenticTestOps_ThuyetTrinh.pptx, tỷ lệ 16:9, chuẩn 10 slides học thuật) được đồng bộ hoàn toàn với báo cáo Word và kiến trúc 6 tầng:"
    )

    slides_summary = [
        ("Slide 1 (Trang bìa):", "Tên đề tài 'Nghiên cứu kỹ thuật Agentic TestOps và ứng dụng kiểm thử hệ thống TrustBase', GVHD: ThS. Lê Phi Hùng, Nhóm 05 (Thắng 21130535, Quang 22130229, Sĩ 22130234)."),
        ("Slide 2 (Thành viên & Tự đánh giá):", "Chi tiết vai trò, sản phẩm kỹ thuật hoàn thành và bảng tự chấm điểm thang 10 của từng thành viên."),
        ("Slide 3 (Hệ thống SUT TrustBase & Bài toán):", "Kiến trúc TrustBase (Customer 4200, Admin 4203, API 4201, Postgres 5432, Redis 6379), thách thức chu trình 3 phân vai, Kim tự tháp ngược và Flaky Tests."),
        ("Slide 4 (Cơ sở lý thuyết & V-Model):", "So sánh Automation truyền thống với Agentic TestOps (SRE Loop 7 bước), đối ứng V-Model (Validation <-> Verification) và Chuỗi lỗi / Defect Lifecycle ISO/IEEE."),
        ("Slide 5 (Kiến trúc 6 tầng Zero-Impact):", "Chi tiết 6 tầng từ Playwright Trace -> Node Inspect CDP -> RCA 4 bước -> RAG Memory -> Canvas Visual Map (5ms) -> Regression Shield kèm sơ đồ tổng thể."),
        ("Slide 6 (Hệ thống Kỹ thuật Kiểm thử):", "Trình bày đầy đủ Black-Box (Weak Robust EP, BVA 3 cấp 4n+1/6n+1/5^n, Decision Table, FSM) và Grey/White-Box (CDP RAM, Statement Coverage, Branch Coverage, McCabe V(G), Mutation Testing)."),
        ("Slide 7 (Tri thức Kép, CI/CD & Bằng chứng thật):", "Cơ chế Tri thức Kép (.md + .canvas.json 5ms), GitHub Actions kiểm định MCP/Playwright, nguyên tắc No-Cap kiểm chứng DOM/HTTP thật kèm ảnh chụp Canvas & đơn hàng VietQR."),
        ("Slide 8 (Kết quả Thực nghiệm & Defect Log):", "Chỉ số đối chứng (30/30 PASS sau hồi quy, Mutation Score 91.67%, thời gian chạy 12-15p, RCA > 88%) và 6 lỗi thực tế phát hiện trên TrustBase (DEF-001..DEF-006)."),
        ("Slide 9 (Handbook cho src bất kỳ & Demo 10 phút):", "Quy trình 4 bước tích hợp plugin vào 1 mã nguồn bất kỳ theo HANDBOOK.md và kế hoạch báo cáo/demo trực quan trong 10 phút."),
        ("Slide 10 (Kết luận & Hướng phát triển):", "Tổng kết 4 đóng góp chính, định hướng tích hợp k6, OWASP ZAP, Self-Healing PR và lời cảm ơn ThS. Lê Phi Hùng.")
    ]
    for s_title, s_desc in slides_summary:
        add_bullet(s_desc, bold_prefix=f"{s_title} ")

    add_h2("5.3 Kịch bản báo cáo và Demo thực tế trong thời gian tối đa 10 phút")
    add_bullet("Trình bày Slide 1–6: Nêu bật bài toán TrustBase, V-Model, kiến trúc MCP 6 tầng và hệ thống kỹ thuật kiểm thử Hộp đen + Hộp trắng + Đột biến.", bold_prefix="Chặng 1 (00:00 - 02:00 | 2 phút): ")
    add_bullet("Bật CHAY_DEMO_AGENTIC_TESTOPS.bat & XUAT_BANG_CHUNG_TESTOPS.bat để chạy Chrome trực tiếp (headless: false) trên TrustBase thật (xác thực chặt DOM/HTTP, không dùng video giả lập); sau đó mở Canvas Note Engineer nạp file .canvas.json trong 5ms.", bold_prefix="Chặng 2 (02:00 - 06:30 | 4.5 phút): ")
    add_bullet("Mở HANDBOOK.md hướng dẫn gắn vào dự án src bất kỳ, xem file test hồi quy .spec.ts, chạy kiểm định MCP Server và mở pipeline .github/workflows/agentic-testops-ci.yml.", bold_prefix="Chặng 3 (06:30 - 08:30 | 2 phút): ")
    add_bullet("Trả lời câu hỏi chuyên môn của ThS. Lê Phi Hùng về MCP, CDP RAM Trace, Weak Robust EP, BVA 3 cấp và Mutation Testing.", bold_prefix="Chặng 4 (08:30 - 10:00 | 1.5 phút): ")

    add_h2("5.4 Bộ câu hỏi vấn đáp phản biện thường gặp (Q&A FAQ)")
    faqs = [
        ("Câu hỏi 1: Agentic TestOps khác biệt gì so với Playwright hay Selenium thông thường?",
         "Playwright/Selenium là công cụ Hộp đen chạy script cứng; khi API văng HTTP 500, nó chỉ chụp được ảnh UI. Agentic TestOps bổ sung tầng suy luận AI qua MCP và kết nối WebSocket CDP (ws://9229) vào tiến trình Node.js để soi trực tiếp biến RAM Heap & Callstack (Hộp xám/Hộp trắng), kết hợp RAG + Canvas Note Engineer."),
        ("Câu hỏi 2: Tại sao hệ thống phải dùng Weak Robust EP và BVA 3 cấp thay vì chọn bừa dữ liệu test?",
         "Weak Robust EP tuân thủ giả định đơn lỗi (chỉ 1 tham số Invalid mỗi test case) để tránh Che giấu lỗi (Fault Masking). BVA 3 cấp tách rõ mức chuẩn (4n+1), mức kiểm thử ngoại lệ ngoài biên (6n+1) và mức đa lỗi tài chính (5^n) cho các hàm tính hoa hồng/ký quỹ BigInt."),
        ("Câu hỏi 3: Độ tin cậy của bộ Regression Test tự sinh được kiểm chứng bằng cách nào?",
         "Bộ test do Tầng 6 sinh ra bắt buộc đạt Phủ cấp 1 (Statement), Phủ cấp 2 (Branch True/False), bám theo độ phức tạp chu trình McCabe V(G) = P + 1 và được kiểm định bằng Mutation Testing (tiêm 24 đột biến nhân tạo, đạt Mutation Score 91.67%)."),
        ("Câu hỏi 4: Hệ thống làm sao đảm bảo bằng chứng demo không bị giả lập ('cap')?",
         "Mọi bước trong kịch bản E2E đều dùng assertion thực (chờ HTTP response 2xx, kiểm tra URL chuyển khỏi /checkout hoặc /login, xác nhận DOM mục tiêu xuất hiện). Nếu bước nào bị khóa (như eKYC gate) hay login thất bại, script dừng ngay và chụp ảnh lỗi thật vào screenshots/ thay vì hiển thị trạng thái thành công giả.")
    ]
    for q, a in faqs:
        add_bullet(a, bold_prefix=f"{q}\nTrả lời: ")

    # =========================================================================
    # PHẦN 6: SỔ TAY CÀI ĐẶT & ÁP DỤNG CHO MỘT MÃ NGUỒN (SRC) BẤT KỲ
    # =========================================================================
    doc.add_page_break()
    add_h1("PHẦN 6: SỔ TAY CÀI ĐẶT & BỘ PROMPT CHO MÃ NGUỒN (SRC) BẤT KỲ (HANDBOOK)")
    add_p(
        "Phần này tóm tắt hướng dẫn trong HANDBOOK.md để bất kỳ kỹ sư nào cũng có thể lấy plugin agentic-test-ops đi kiểm thử cho một mã nguồn Web/Backend (src) bất kỳ:"
    )

    add_h2("6.1 Quy trình Cài đặt 4 bước (100% Zero-Impact với src mục tiêu)")
    add_bullet("Tại thư mục agentic-test-ops/mcp, chạy 'npm install' và '.\\setup-browser.ps1' (hoặc './setup-browser.sh'). Nếu máy đã cài sẵn Chrome/Edge, mcp/server.mjs cũng tự động fallback.", bold_prefix="Bước 1 — Cài đặt MCP & Playwright: ")
    add_bullet("Copy thư mục plugin vào '.agents/plugins/agentic-test-ops/' của dự án đích hoặc khai báo lệnh 'node <path>/mcp/server.mjs' trong mcp_config.json (Antigravity / Gemini CLI / Claude Code). Đặt biến CANVAS_RAG_DIR nếu muốn tự sync đồ thị sang Canvas Note Engineer.", bold_prefix="Bước 2 — Gắn MCP vào AI Host: ")
    add_bullet("Copy vscode/launch.json và vscode/tasks.json vào thư mục .vscode/ của src mục tiêu. Chạy Backend của src với 'NODE_OPTIONS=--inspect=0.0.0.0:9229' hoặc để Agent tự gọi tool debug_start_server.", bold_prefix="Bước 3 — Bật Debug Port trên src cần test: ")
    add_bullet("Mở thư mục screenshots/ xem ảnh chụp thực tế, knowledge/*.md xem báo cáo RAG, và kéo thả knowledge/*.canvas.json vào Canvas Note Engineer để kiểm tra sơ đồ lỗi trong 5ms.", bold_prefix="Bước 4 — Đọc Bằng chứng & Đồ thị: ")

    add_h2("6.2 Bộ Prompt mẫu thực chiến cho src bất kỳ")
    prompts = [
        ("Prompt 1 — Khảo sát & Chạy Live Chrome trên src mới:",
         "'Hãy đọc cấu trúc src hiện tại để xác định cổng Frontend/API. Gọi debug_status kiểm tra cổng, dùng debug_start_server bật Backend với inspectPort 9229, sau đó dùng debug_browser_run (headless: false, slowMo: 500) chạy qua luồng [X] và chụp ảnh màn hình.'"),
        ("Prompt 2 — Sinh bộ Test Black-Box chuẩn ISTQB:",
         "'Đóng vai flow-worker kiểm thử form/API [X]. Thiết kế ca test theo Weak Robust EP (đơn lỗi), Standard BVA (4n+1), Robustness BVA (6n+1 gồm min-/max+), Decision Table và FSM (cả Invalid Transitions). Thực thi thật và xuất ma trận qua debug_export_rag_report.'"),
        ("Prompt 3 — Điều tra lỗi 500 Grey-Box CDP & Sinh Regression Test phủ nhánh:",
         "'Khi thao tác [X] gặp lỗi HTTP 500, hãy dùng debug_browser_run lấy failedRequests, gắn debug_inspect_cdp (port 9229) bắt biến RAM Heap & Callstack, viết file Regression Test đạt Phủ cấp 1 & Phủ cấp 2 trong tests/, chạy debug_run_test xác minh và xuất Canvas JSON.'"),
        ("Prompt 4 — Quét đa luồng song song (/overnight):",
         "'/overnight --workers 3 --flows \"auth,catalog,checkout,payout\" — Chia luồng theo contextId (worker-1..3), gắn CDP không chặn luồng khi có HTTP 500, và tổng hợp báo cáo qua debug_export_overnight_report.'")
    ]
    for p_name, p_body in prompts:
        add_bullet(p_body, bold_prefix=f"{p_name}\n")

    doc.save(doc_path)
    print(f"Đã cập nhật & chuẩn hóa Báo cáo Word thành công: {doc_path}")


if __name__ == "__main__":
    p_repo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nhom05_AgenticTestOps.docx")
    update_doc(p_repo)
