# -*- coding: utf-8 -*-
"""
Cập nhật Báo cáo Word Nhom05_AgenticTestOps.docx với Phần 5:
- Bảng tự đánh giá thành viên nhóm (Thang điểm 10)
- Tóm tắt nội dung 10 slides PowerPoint chuẩn học thuật (không màu mè, không emoji, không dấu gạch nối AI)
- Kịch bản thuyết trình và demo 10 phút
- Bộ câu hỏi vấn đáp (Q&A FAQ) bảo vệ đồ án
"""

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

def update_doc(doc_path):
    doc = docx.Document(doc_path)

    # Helper functions
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

    # Thêm trang mới
    doc.add_page_break()

    add_h1("PHẦN 5: KẾ HOẠCH BÁO CÁO BẢO VỆ ĐỒ ÁN VÀ TỰ ĐÁNH GIÁ THÀNH VIÊN")
    
    add_h2("5.1 Bảng tự đánh giá đóng góp của các thành viên nhóm (Thang điểm 10)")
    add_p(
        "Nhóm 05 gồm 03 thành viên, đã phân công trách nhiệm rõ ràng theo năng lực chuyên môn và tinh thần trách nhiệm tập thể. Toàn bộ các hạng mục nghiên cứu lý thuyết, phát triển công cụ MCP, viết kịch bản E2E Playwright, xây dựng pipeline CI/CD, thiết kế 30 test case, ghi nhận 6 defect log và tài liệu báo cáo đều hoàn thành đúng hạn 100% với chất lượng đảm bảo."
    )
    add_p(
        "Căn cứ vào khối lượng công việc, mức độ chủ động, chất lượng sản phẩm bàn giao và mức độ cam kết, nhóm thống nhất tự đánh giá cho điểm theo thang điểm 10 như sau:",
        bold_prefix="Bảng tự chấm điểm thành viên: "
    )

    # Tạo bảng tự đánh giá
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
        ("1", "Nguyễn Hữu Thắng", "21130541", "Nhóm trưởng\nTest Lead",
         "- Nghiên cứu nguyên lý kỹ thuật Agentic TestOps và giao thức MCP.\n"
         "- Xây dựng MCP Server điều khiển CDP và Playwright Runner.\n"
         "- Lập trình kịch bản E2E kiểm thử chu trình đa phân vai khép kín.\n"
         "- Thiết lập pipeline CI/CD GitHub Actions và xuất bằng chứng tự động.\n"
         "- Chịu trách nhiệm thuyết trình báo cáo và điều phối phần demo.",
         "10.0 / 10\n(Đóng góp 100%)"),
        ("2", "Phạm Trần Nhụt Quang", "21130495", "QA Engineer\nTest Designer",
         "- Thiết kế bộ Test Suite 30 Test Cases chi tiết theo chuẩn IEEE 829.\n"
         "- Áp dụng 4 kỹ thuật kiểm thử hộp đen: EP, BVA, Decision Table, State Transition.\n"
         "- Xây dựng ma trận truy vết yêu cầu phần mềm (RTM).\n"
         "- Soạn thảo tài liệu đặc tả ca kiểm thử và kiểm chứng dữ liệu hạt giống.\n"
         "- Phản biện kỹ thuật và chuẩn bị nội dung câu hỏi vấn đáp.",
         "9.5 / 10\n(Đóng góp 100%)"),
        ("3", "Huỳnh Văn Sĩ", "21130528", "Automation Engineer\nQA Analyst",
         "- Quản lý và biên tập Bảng nhật ký 6 lỗi thực tế (Defect Log).\n"
         "- Thực hiện kiểm thử phi chức năng: Kiểm thử tải và rà soát an toàn bảo mật.\n"
         "- Tổng hợp số liệu Dashboard KPI đo lường chất lượng phần mềm.\n"
         "- Thiết kế tài liệu thuyết trình và đóng gói sản phẩm nghiệm thu.\n"
         "- Cấu hình và duy trì hạ tầng Docker Compose (PostgreSQL, Redis).",
         "9.5 / 10\n(Đóng góp 100%)")
    ]

    for row_idx, data in enumerate(eval_data):
        row = table_eval.add_row()
        for col_idx, val in enumerate(data):
            cell = row.cells[col_idx]
            p = cell.paragraphs[0]
            if col_idx in [0, 2, 5]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            if col_idx in [1, 5]:
                run.font.bold = True
                if col_idx == 5:
                    run.font.color.rgb = RGBColor(27, 54, 93)

    style_table(table_eval, [0.5, 1.3, 0.9, 1.1, 2.7, 1.1])
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 5.2 Tóm tắt nội dung 10 Slides PowerPoint
    add_h2("5.2 Tóm tắt cấu trúc bộ Slide trình chiếu báo cáo (10 slides chuẩn)")
    add_p(
        "Nhóm 05 đã thiết kế bộ Slide trình chiếu báo cáo thi cuối kỳ bằng file PowerPoint chuẩn (tỷ lệ 16:9), tuân thủ đúng giới hạn tối đa 10 slides theo thông báo của giảng viên hướng dẫn ThS. Lê Phi Hùng. Bố cục 10 slides được chuẩn hóa học thuật, không dùng biểu tượng không cần thiết và diễn đạt súc tích:",
        bold_prefix="Danh mục 10 slide thuyết trình: "
    )

    slides_summary = [
        ("Slide 1 (Trang bìa):", "Tên đề tài 'Nghiên cứu kỹ thuật Agentic TestOps và ứng dụng kiểm thử hệ thống TrustBase', môn học Kiểm thử và ĐBCLPM, GVHD: ThS. Lê Phi Hùng, Nhóm 05 (Nguyễn Hữu Thắng, Phạm Trần Nhụt Quang, Huỳnh Văn Sĩ)."),
        ("Slide 2 (Giới thiệu nhóm và Tự đánh giá):", "Danh sách 3 thành viên, vai trò cụ thể, chi tiết nhiệm vụ và bảng tự chấm điểm thang 10 (Thắng 10/10, Quang 9.5/10, Sĩ 9.5/10) với mức độ đóng góp 100%."),
        ("Slide 3 (Hệ thống SUT và Bài toán kiểm thử):", "Giới thiệu sàn bản quyền số TrustBase (Customer cổng 4200, Admin cổng 4203, API cổng 4201, Postgres, Redis) và thách thức khi kiểm thử chu trình giao dịch đa phân vai (Buyer -> Seller -> Admin)."),
        ("Slide 4 (Cơ sở lý thuyết Agentic TestOps):", "Bản chất Agentic TestOps (LLM + MCP Protocol + Playwright CDP). So sánh giữa Automation truyền thống (kịch bản cứng, dễ gãy) với Agentic TestOps (tự sinh test, tự chữa lành, tự phân tích lỗi)."),
        ("Slide 5 (Kiến trúc kỹ thuật phân tầng):", "Sơ đồ kiến trúc 4 tầng: Tầng LLM Reasoning, Tầng Giao thức MCP và CDP, Tầng Automation Engine và Recorder, và Tầng SUT TrustBase Infrastructure."),
        ("Slide 6 (Thiết kế Bộ kiểm thử 30 ca):", "Ứng dụng 4 kỹ thuật kiểm thử hộp đen ISTQB: Phân vùng tương đương (EP), Phân tích giá trị biên (BVA), Bảng quyết định (Decision Table) và Chuyển đổi trạng thái (State Transition)."),
        ("Slide 7 (Tự động hóa CI/CD và Quản lý Bằng chứng):", "Pipeline GitHub Actions tự động hóa hoàn toàn, cơ chế thu thập và đóng gói bằng chứng thực thi gồm ảnh chụp màn hình, video và nhật ký lỗi qua artifacts."),
        ("Slide 8 (Kết quả thực nghiệm và Phân tích lỗi):", "Thống kê thực thi và phân tích 6 lỗi thực tế phát hiện được trên TrustBase (Khóa rút tiền do KYC ngầm DEF-001, Chặn email allowlist DEF-002, Lỗi 500 voucher DEF-003, v.v.)."),
        ("Slide 9 (Kế hoạch báo cáo trong 10 phút):", "Kế hoạch phân bổ thời lượng 10 phút chi tiết: Báo cáo slide 2 phút, Demo trực quan 4.5 phút, Demo file test tự sinh và CI/CD 2 phút, Trả lời câu hỏi vấn đáp 1.5 phút."),
        ("Slide 10 (Kết luận và Hướng phát triển):", "Tổng kết các đóng góp chính của đề tài, định hướng mở rộng hệ thống sang kiểm thử hiệu năng/bảo mật, và lời cảm ơn gửi tới ThS. Lê Phi Hùng.")
    ]
    for s_title, s_desc in slides_summary:
        add_bullet(s_desc, bold_prefix=f"{s_title} ")

    # 5.3 Kịch bản thuyết trình và Demo trong 10 phút
    add_h2("5.3 Kịch bản báo cáo và Demo thực tế trong thời gian tối đa 10 phút")
    add_p(
        "Nhóm xây dựng kịch bản điều phối thời gian chặt chẽ, đảm bảo hoàn thành trọn vẹn toàn bộ nội dung thuyết trình, trình chiếu demo và trả lời chất vấn đúng trong khung 10 phút quy định:"
    )

    add_bullet("Trình bày Slide 1, 2, 3 và 4. Tập trung nêu bật điểm nghẽn của kiểm thử chu trình đa phân vai trên sàn giao dịch ký quỹ TrustBase và giải pháp ứng dụng Agentic TestOps.", bold_prefix="Chặng 1: Giới thiệu và Báo cáo tổng quan (00:00 đến 02:00, 2 phút): ")
    add_bullet("Chiếu video thực tế hoặc mở trình duyệt Chrome tự hành chạy chu trình khép kín: (1) Buyer tìm kiếm thẻ Steam Wallet, mở checkout và tạo đơn ký quỹ VietQR; (2) Chuyển vai Seller Studio với tài khoản KYC hợp lệ, bấm yêu cầu rút tiền thành công vào hàng đợi Pending; (3) Chuyển vai Admin Console cổng 4203 đăng nhập và thẩm định giải ngân.", bold_prefix="Chặng 2: Trình chiếu Demo trực quan đa phân vai (02:00 đến 06:30, 4.5 phút): ")
    add_bullet("Mở trực tiếp mã nguồn file test kịch bản tự sinh (tests/repro_voucher_bug.spec.ts) và file cấu hình CI/CD (.github/workflows/agentic-testops-ci.yml). Cho Thầy thấy thư mục artifacts chứa đồng thời ảnh screenshots và video webm được sinh ra tự động.", bold_prefix="Chặng 3: Chứng minh tính năng Tự sinh test và CI/CD (06:30 đến 08:30, 2 phút): ")
    add_bullet("Lắng nghe và giải đáp các câu hỏi chuyên môn từ ThS. Lê Phi Hùng về giao thức MCP, kỹ thuật xử lý ranh giới dữ liệu, và các bài học kinh nghiệm thu được.", bold_prefix="Chặng 4: Trả lời câu hỏi vấn đáp (08:30 đến 10:00, 1.5 phút): ")

    # 5.4 Bộ câu hỏi vấn đáp
    add_h2("5.4 Bộ câu hỏi vấn đáp phản biện thường gặp (Q&A FAQ)")
    add_p(
        "Nhóm đã chuẩn bị trước các phương án trả lời súc tích, khoa học và bám sát kiến trúc kỹ thuật để trả lời các câu hỏi phản biện của Giảng viên:"
    )

    faqs = [
        ("Câu hỏi 1: Agentic TestOps khác biệt gì so với Playwright hay Selenium thông thường?",
         "Trả lời: Playwright hoặc Selenium đóng vai trò là công cụ thực thi (Execution Engine) chạy các câu lệnh cố định do con người viết sẵn. Khi giao diện đổi selector, bài test sẽ thất bại ngay lập tức. Trong khi đó, Agentic TestOps bổ sung tầng suy luận AI kết nối qua giao thức MCP: Agent tự đọc DOM, tự sinh kịch bản test, tự chữa lành (Self-healing) khi selector thay đổi, và tự truy vấn log DB/API để tìm nguyên nhân gốc rễ của lỗi (Root Cause Analysis)."),
        ("Câu hỏi 2: Trong quá trình test, Agent có thực sự tạo ra các file test không?",
         "Trả lời: Hoàn toàn có. Khi nhận diện một API hoặc luồng màn hình mới, Agent tự động phân tích cấu trúc request/response và DOM tree, sau đó tự biên soạn thành các file kịch bản chuẩn TypeScript/Playwright (như tests/repro_voucher_bug.spec.ts). Các file này được lưu trực tiếp vào thư mục mã nguồn và có thể chạy lại trong CI/CD như bất kỳ bài test hồi quy chuẩn nào."),
        ("Câu hỏi 3: Việc thu thập bằng chứng kiểm thử tự động phục vụ mục đích gì trong CI/CD?",
         "Trả lời: Bằng chứng kiểm thử (Test Evidence) giúp kiểm chứng tính xác thực của quá trình kiểm thử tự động, tránh hiện tượng bài test giả lập kết quả. Ảnh screenshots hỗ trợ xem nhanh trạng thái tại các thời điểm then chốt trên Pull Request; còn Video ghi hình thực tế lưu lại toàn bộ thao tác gõ phím, click chuột, popup và thông tin thanh toán VietQR hiển thị thời gian thực, phục vụ đối soát và nghiệm thu."),
        ("Câu hỏi 4: Đâu là lỗi (Defect) thực tế tiêu biểu mà hệ thống đã phát hiện trên TrustBase?",
         "Trả lời: Đó là lỗi DEF-001 (Khóa rút tiền Seller do ràng buộc KYC ngầm). Người bán có số dư 12 triệu đồng nhưng nút rút tiền bị vô hiệu hóa vì tính năng kyc_gate_payouts kích hoạt trong khi dữ liệu hạt giống onboarding_progress chưa được phê duyệt. Thay vì chỉ báo lỗi giao diện, Agent đã truy vấn trực tiếp cơ sở dữ liệu PostgreSQL để chỉ ra đúng dòng code vi phạm logic KYC, giúp đội ngũ phát triển định vị lỗi nhanh chóng.")
    ]

    for q, a in faqs:
        add_bullet(a, bold_prefix=f"{q}\n")

    doc.save(doc_path)
    print(f"Đã cập nhật Báo cáo Word thành công: {doc_path}")

if __name__ == "__main__":
    p_repo = r"C:\Users\NoNomt007\agentic-test-ops\Nhom05_AgenticTestOps.docx"
    p_downloads = r"C:\Users\NoNomt007\Downloads\Nhom05_AgenticTestOps.docx"
    
    update_doc(p_repo)
    import shutil
    shutil.copyfile(p_repo, p_downloads)
    print("Đã đồng bộ sang Downloads!")
