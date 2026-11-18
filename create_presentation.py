# -*- coding: utf-8 -*-
"""
Tạo bài thuyết trình PowerPoint báo cáo đồ án môn học (Chuẩn 10 slides, 16:9)
Phong cách: Học thuật, trang trọng, không emoji, không văn bản giả lập (no-cap).
Đề tài: Nghiên cứu kỹ thuật Agentic TestOps và ứng dụng kiểm thử hệ thống TrustBase
GVHD: ThS. Lê Phi Hùng - Trường ĐH Nông Lâm TP.HCM - Khoa CNTT
"""

import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


def add_fitted_image(slide, img_path, left, top, max_w, max_h):
    """Chèn ảnh giữ nguyên tỷ lệ khung hình, tự căn giữa trong khung (max_w, max_h)."""
    if not os.path.exists(img_path):
        return None
    with Image.open(img_path) as im:
        w_px, h_px = im.size
    ratio = w_px / h_px
    target_w = max_w
    target_h = target_w / ratio
    if target_h > max_h:
        target_h = max_h
        target_w = target_h * ratio
    x = left + (max_w - target_w) / 2
    y = top + (max_h - target_h) / 2
    return slide.shapes.add_picture(img_path, x, y, width=target_w, height=target_h)


def build_academic_presentation(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Bảng màu học thuật chuẩn (Academic Formal Theme)
    BG_PAGE = RGBColor(248, 250, 252)       # Slate 50
    CARD_BG = RGBColor(255, 255, 255)       # Pure White
    CARD_BORDER = RGBColor(203, 213, 225)   # Slate 300
    HEADER_NAVY = RGBColor(15, 23, 42)      # Slate 900
    TEXT_MAIN = RGBColor(30, 41, 59)        # Slate 800
    TEXT_MUTED = RGBColor(71, 85, 105)      # Slate 600
    PRIMARY_BLUE = RGBColor(27, 54, 93)     # Deep Academic Navy
    ACCENT_BLUE = RGBColor(30, 64, 175)     # Blue 800
    BADGE_BG = RGBColor(241, 245, 249)      # Slate 100

    TOTAL_SLIDES = 10

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_PAGE
        bg.line.fill.background()
        return bg

    def add_footer(slide, page_num):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.32))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = (
            f"Nhóm 05  |  Đề tài: Agentic TestOps & Ứng dụng kiểm thử TrustBase  |  "
            f"GVHD: ThS. Lê Phi Hùng  |  Trang {page_num}/{TOTAL_SLIDES}"
        )
        p.font.name = "Times New Roman"
        p.font.size = Pt(9.5)
        p.font.italic = True
        p.font.color.rgb = TEXT_MUTED
        p.alignment = PP_ALIGN.RIGHT

    def add_header(slide, title_text, section_text, page_num):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.733), Inches(1.05))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_sec = tf.paragraphs[0]
        p_sec.text = section_text.upper()
        p_sec.font.name = "Times New Roman"
        p_sec.font.size = Pt(10.5)
        p_sec.font.bold = True
        p_sec.font.color.rgb = ACCENT_BLUE

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Times New Roman"
        p_title.font.size = Pt(20)
        p_title.font.bold = True
        p_title.font.color.rgb = HEADER_NAVY
        p_title.space_before = Pt(3)

        # Đường gạch ngang mảnh dưới tiêu đề
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.36), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.fill.background()

        add_footer(slide, page_num)

    def add_card(slide, left, top, width, height, title="", border_color=CARD_BORDER, fill_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = fill_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.0)

        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.18), top + Inches(0.12), width - Inches(0.36), Inches(0.38))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Times New Roman"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = PRIMARY_BLUE
        return card

    def add_bullets(slide, left, top, width, height, items, font_size=11.0, space_before=5, text_color=TEXT_MAIN):
        tb = slide.shapes.add_textbox(left, top, width, height)
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        for idx, item in enumerate(items):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.space_before = Pt(0 if idx == 0 else space_before)
            if isinstance(item, tuple):
                prefix, body = item
                r1 = p.add_run()
                r1.text = prefix + " "
                r1.font.name = "Times New Roman"
                r1.font.size = Pt(font_size)
                r1.font.bold = True
                r1.font.color.rgb = PRIMARY_BLUE
                r2 = p.add_run()
                r2.text = body
                r2.font.name = "Times New Roman"
                r2.font.size = Pt(font_size)
                r2.font.color.rgb = text_color
            else:
                r = p.add_run()
                r.text = item
                r.font.name = "Times New Roman"
                r.font.size = Pt(font_size)
                r.font.color.rgb = text_color
        return tb

    # =========================================================================
    # SLIDE 1: TRANG TIÊU ĐỀ BÁO CÁO
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1)
    add_card(s1, Inches(0.75), Inches(0.65), Inches(11.833), Inches(6.2), "", PRIMARY_BLUE)

    # Logo trường (nếu tồn tại)
    add_fitted_image(s1, "logo_hcmuaf.png", Inches(5.966), Inches(0.85), Inches(1.4), Inches(1.1))

    tbox = s1.shapes.add_textbox(Inches(1.15), Inches(2.05), Inches(11.033), Inches(4.55))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0

    p = tf1.paragraphs[0]
    p.text = "TRƯỜNG ĐẠI HỌC NÔNG LÂM TP. HỒ CHÍ MINH  |  KHOA CÔNG NGHỆ THÔNG TIN"
    p.font.name = "Times New Roman"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.alignment = PP_ALIGN.CENTER

    p = tf1.add_paragraph()
    p.text = "BÁO CÁO THI KẾT THÚC HỌC PHẦN: KIỂM THỬ VÀ ĐẢM BẢO CHẤT LƯỢNG PHẦN MỀM"
    p.font.name = "Times New Roman"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(8)

    p = tf1.add_paragraph()
    p.text = "ĐỀ TÀI: NGHIÊN CỨU KỸ THUẬT AGENTIC TESTOPS\nVÀ ỨNG DỤNG KIỂM THỬ HỆ THỐNG TRUSTBASE"
    p.font.name = "Times New Roman"
    p.font.size = Pt(23)
    p.font.bold = True
    p.font.color.rgb = HEADER_NAVY
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(16)

    p = tf1.add_paragraph()
    p.text = (
        "Kiến trúc MCP 6 tầng Zero-Impact kết hợp Kiểm thử Hộp đen (EP, BVA, Decision Table, FSM),\n"
        "Kiểm thử Hộp xám / Hộp trắng qua CDP Heap Trace, Vòng lặp Tri thức Kép và Bộ test Hồi quy"
    )
    p.font.name = "Times New Roman"
    p.font.size = Pt(12.5)
    p.font.color.rgb = TEXT_MUTED
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(12)

    p = tf1.add_paragraph()
    p.text = (
        "Giảng viên hướng dẫn: ThS. Lê Phi Hùng\n"
        "Nhóm 05: Nguyễn Hữu Thắng (21130535)  |  Phạm Trần Nhựt Quang (22130229)  |  Huỳnh Văn Sĩ (22130234)"
    )
    p.font.name = "Times New Roman"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(22)

    # =========================================================================
    # SLIDE 2: THÀNH VIÊN NHÓM VÀ TỰ ĐÁNH GIÁ (THANG ĐIỂM 10)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2)
    add_header(s2, "1. Thành viên nhóm và Bảng tự đánh giá đóng góp", "Phân công trách nhiệm và nghiệm thu công việc", 2)

    members = [
        {
            "name": "Nguyễn Hữu Thắng",
            "mssv": "MSSV: 21130535",
            "role": "Nhóm trưởng / Test Lead",
            "score": "Điểm tự chấm: 10.0 / 10",
            "tasks": [
                "Nghiên cứu kiến trúc Agentic TestOps 6 tầng & chuẩn MCP JSON-RPC 2.0.",
                "Xây dựng MCP Server (mcp/server.mjs) điều phối Playwright & Node Inspect.",
                "Thiết lập luồng E2E đa phân vai (Buyer -> Seller -> Admin) có kiểm chứng DOM/HTTP.",
                "Xây dựng CI/CD GitHub Actions (agentic-testops-ci.yml) & Sổ tay HANDBOOK.md.",
                "Chủ trì thuyết trình tổng quan và điều phối phần Demo trực tiếp."
            ]
        },
        {
            "name": "Phạm Trần Nhựt Quang",
            "mssv": "MSSV: 22130229",
            "role": "QA Engineer / Test Designer",
            "score": "Điểm tự chấm: 9.5 / 10",
            "tasks": [
                "Thiết kế bộ Test Suite 30 Test Cases theo chuẩn IEEE 829 / ISO 29119.",
                "Áp dụng 4 kỹ thuật Hộp đen: Weak Robust EP, BVA 3 cấp (4n+1, 6n+1, 5^n), Decision Table, FSM.",
                "Xây dựng cơ chế chống Flaky Test (Port Zombie Killer, find-polluter bisect).",
                "Kiểm chứng dữ liệu hạt giống TrustBase (PostgreSQL) & Ma trận truy vết RTM.",
                "Chuẩn bị nội dung phản biện kỹ thuật và bộ câu hỏi vấn đáp."
            ]
        },
        {
            "name": "Huỳnh Văn Sĩ",
            "mssv": "MSSV: 22130234",
            "role": "CDP Debugger & Quality Analyst",
            "score": "Điểm tự chấm: 9.5 / 10",
            "tasks": [
                "Phát triển cdp-client.mjs kết nối WebSocket ws://9229 soi biến trên RAM Heap.",
                "Xây dựng rag-exporter.mjs xuất Tri thức kép (.md RAG & .canvas.json AST 5ms).",
                "Thiết kế test hồi quy Hộp trắng (Phủ cấp 1/2, McCabe V(G), Mutation Testing).",
                "Biên tập bảng nhật ký lỗi (Defect Log), Dashboard KPI và rà soát bảo mật.",
                "Duy trì hạ tầng Docker (PostgreSQL, Redis) và hoàn thiện slide/báo cáo."
            ]
        }
    ]

    for i, m in enumerate(members):
        left = Inches(0.8 + i * 4.0)
        add_card(s2, left, Inches(1.52), Inches(3.733), Inches(5.32), "", PRIMARY_BLUE)

        tb = s2.shapes.add_textbox(left + Inches(0.2), Inches(1.66), Inches(3.333), Inches(5.05))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = m["name"]
        p.font.name = "Times New Roman"
        p.font.size = Pt(14.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE

        p = tf.add_paragraph()
        p.text = f"{m['mssv']}  |  {m['role']}"
        p.font.name = "Times New Roman"
        p.font.size = Pt(10.5)
        p.font.color.rgb = ACCENT_BLUE
        p.space_before = Pt(2)

        p = tf.add_paragraph()
        p.text = f"{m['score']} (Đóng góp 100%)"
        p.font.name = "Times New Roman"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = HEADER_NAVY
        p.space_before = Pt(4)

        p = tf.add_paragraph()
        p.text = "Nhiệm vụ & sản phẩm hoàn thành:"
        p.font.name = "Times New Roman"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

        for task in m["tasks"]:
            p = tf.add_paragraph()
            p.text = f"- {task}"
            p.font.name = "Times New Roman"
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_MUTED
            p.space_before = Pt(4.5)

    # =========================================================================
    # SLIDE 3: HỆ THỐNG MỤC TIÊU TRUSTBASE VÀ BÀI TOÁN KIỂM THỬ
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3)
    add_header(s3, "2. Hệ thống mục tiêu TrustBase và Bài toán kiểm thử", "Bối cảnh ứng dụng và các nút thắt kỹ thuật cần giải quyết", 3)

    add_card(s3, Inches(0.8), Inches(1.52), Inches(5.7), Inches(5.32), "Kiến trúc nền tảng TrustBase (SUT)", PRIMARY_BLUE)
    add_bullets(s3, Inches(1.0), Inches(2.05), Inches(5.3), Inches(4.6), [
        ("Mô hình nghiệp vụ:", "Sàn thương mại điện tử chuyên biệt phân phối sản phẩm số, phần mềm bản quyền và thẻ nạp với cơ chế Ký quỹ trung gian (Digital Key Escrow 72h)."),
        ("Kiến trúc Monorepo:", "Gồm Customer & Seller Web (cổng 4200), Admin Console (cổng 4203), Backend API TypeScript (cổng 4201), PostgreSQL 15 (cổng 5432) và Redis 7 (cổng 6379)."),
        ("Quy mô thực nghiệm:", "54 bảng cơ sở dữ liệu, 56 seed listings, 5 gian hàng mẫu, xác thực eKYC và thanh toán chuyển khoản tự động VietQR."),
        ("Bài toán tích hợp tổng quát:", "Plugin được thiết kế dạng Zero-Impact để cắm vào bất kỳ mã nguồn (src) Web/Node.js nào mà không sửa code của SUT.")
    ], font_size=11.5, space_before=10)

    add_card(s3, Inches(6.8), Inches(1.52), Inches(5.7), Inches(5.32), "Thách thức của Kiểm thử E2E truyền thống", PRIMARY_BLUE)
    add_bullets(s3, Inches(7.0), Inches(2.05), Inches(5.3), Inches(4.6), [
        ("Vòng đời 3 phân vai phức tạp:", "Chu trình kéo dài qua Buyer (đặt hàng, ký quỹ Escrow) -> Seller (eKYC, đối soát ví, rút tiền Payout) -> Admin (thẩm định, phê duyệt giải ngân)."),
        ("Nghịch lý Kim tự tháp ngược:", "Dồn quá nhiều kiểm thử thủ công/E2E dễ vỡ (15-20 phút/vòng) trong khi thiếu Unit/Integration Test bao phủ rẽ nhánh."),
        ("Thảm họa Flaky Tests:", "Bất đồng bộ DOM, ô nhiễm trạng thái DB giữa các test và xung đột cổng EADDRINUSE (3000, 4200, 9229)."),
        ("Đứt gãy Hộp đen (Frontend vs Backend):", "Playwright/Cypress thuần khi gặp HTTP 500 chỉ chụp được ảnh UI lỗi, không biết dòng code nào sập hay biến RAM mang giá trị gì.")
    ], font_size=11.5, space_before=10)

    # =========================================================================
    # SLIDE 4: CƠ SỞ LÝ THUYẾT: AGENTIC TESTOPS, V-MODEL & ISO/IEEE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4)
    add_header(s4, "3. Cơ sở lý thuyết: Agentic TestOps, V-Model & Chuẩn ISO/IEEE", "Chuyển dịch từ script tĩnh sang Tác tử kiểm thử tự trị SRE", 4)

    add_card(s4, Inches(0.8), Inches(1.52), Inches(5.7), Inches(3.25), "Hạn chế của Tự động hóa truyền thống", CARD_BORDER)
    add_bullets(s4, Inches(1.0), Inches(1.98), Inches(5.3), Inches(2.65), [
        ("- Soạn thảo thủ công:", "Kỹ sư phải tự viết tay từng selector CSS/XPath trong file .spec.ts."),
        ("- Flaky khi DOM thay đổi:", "Kịch bản cứng dễ gãy; GenAI thế hệ 1 chỉ sinh text từ prompt nhưng thiếu Execution Context nên dễ ảo giác."),
        ("- Mù thông tin máy chủ:", "Chỉ báo lỗi assertion failed hoặc HTTP 500 chung chung, kỹ sư mất 2-6 giờ dò log tìm nguyên nhân."),
        ("- Quên tri thức sự cố:", "Báo cáo HTML/chat rời rạc, lỗi cũ không được cấu trúc hóa thành bộ phòng thủ hồi quy.")
    ], font_size=11.0, space_before=6, text_color=TEXT_MUTED)

    add_card(s4, Inches(6.8), Inches(1.52), Inches(5.7), Inches(3.25), "Mô hình Agentic TestOps (Đề xuất)", PRIMARY_BLUE)
    add_bullets(s4, Inches(7.0), Inches(1.98), Inches(5.3), Inches(2.65), [
        ("- Vòng lặp nhận thức SRE 7 bước:", "Observe -> Reason -> Act -> Investigate -> Verify -> Document -> Remember."),
        ("- Tự chủ môi trường (Anti-Flaky):", "Tự quét và giải phóng cổng zombie (debug_kill_ports), cô lập test gây ô nhiễm (find-polluter bisect)."),
        ("- Tracing kép Hộp đen + Hộp trắng:", "Chặn lỗi HTTP/Console tại trình duyệt rồi gắn ngay WebSocket CDP ws://9229 soi biến sống trên RAM Heap."),
        ("- Tri thức kép & Hồi quy tự động:", "Lưu Markdown RAG cho AI học lại và Canvas JSON (5ms) cho lập trình viên, đồng thời sinh test hồi quy.")
    ], font_size=11.0, space_before=6)

    add_card(s4, Inches(0.8), Inches(4.92), Inches(11.733), Inches(1.92), "Chuẩn hóa theo Mô hình chữ V (V-Model) và Tiêu chuẩn ISO/IEC/IEEE 29119", PRIMARY_BLUE, BADGE_BG)
    add_bullets(s4, Inches(1.0), Inches(5.38), Inches(11.333), Inches(1.38), [
        ("1. Đối ứng V-Model:", "Validation ('Are we building the right system?') kiểm định ở tầng UI E2E; Verification ('Are we building the system right?') kiểm chứng logic mã nguồn & bộ nhớ RAM qua CDP."),
        ("2. Chuỗi lỗi chuẩn ISO/IEEE:", "Phân tách rạch ròi Error (lỗi tư duy lập trình) -> Fault/Defect (dòng code sai do CDP bắt) -> Failure (HTTP 500/UI crash ở Playwright) -> Incident (hồ sơ Canvas)."),
        ("3. Vòng đời Defect Lifecycle:", "Theo dõi chặt trạng thái từng lỗi từ New -> Open -> Investigating (CDP) -> Fixed -> Re-test -> Closed hoặc Re-opened.")
    ], font_size=10.8, space_before=4)

    # =========================================================================
    # SLIDE 5: KIẾN TRÚC HỆ THỐNG 6 TẦNG ZERO-IMPACT
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5)
    add_header(s5, "4. Kiến trúc Hệ thống 6 Tầng Zero-Impact & MCP Server", "Đóng gói độc lập chuẩn JSON-RPC 2.0 stdio với 9 công cụ chuyên biệt", 5)

    add_card(s5, Inches(0.8), Inches(1.52), Inches(7.2), Inches(5.32), "Chi tiết 6 Tầng Kiến trúc Toàn trình", PRIMARY_BLUE)
    tiers = [
        ("Tầng 1 — Browser Automation & Smart Trace (Playwright):", "Điều khiển Chrome/Chromium đa context (contextId), bắt Console Error, Page Error, HTTP >= 400 và chụp ảnh thực tế vào screenshots/."),
        ("Tầng 2 — Source Code Trace & Debug Session (Node Inspect):", "Bật server với NODE_OPTIONS=--inspect=9229, tích hợp Port Zombie Killer và hỗ trợ kỹ sư nhấn F5 trên VS Code (launch.json) để attach trực tiếp."),
        ("Tầng 3 — Root Cause Analysis (RCA 4 bước & CDP Client):", "Kết nối WebSocket ws://127.0.0.1:9229 đóng băng runtime khi văng exception, đọc Callstack và giá trị biến Heap RAM qua Debugger.evaluateOnCallFrame."),
        ("Tầng 4 — RAG Knowledge Memory (knowledge/*.md):", "Lưu hồ sơ Defect Dossier chuẩn hóa để AI Agent truy vấn lại trước các phiên quét sau, giảm thiểu ảo giác (hallucination)."),
        ("Tầng 5 — Canvas Visual Map (.canvas.json):", "Đồng bộ đồ thị 3 hoặc 7 phân cụm (Đỏ - Vàng - Xanh) sang Canvas Note Engineer qua Local AST Parser (~5ms, 0 Token LLM)."),
        ("Tầng 6 — Auto Regression Shield (tests/*.spec.ts):", "Sinh bộ Unit/Integration/E2E Regression Test phủ nhánh thực chất (Zero Empty Tests), cắm trực tiếp vào CI/CD Pipeline.")
    ]
    add_bullets(s5, Inches(1.0), Inches(2.02), Inches(6.8), Inches(4.7), tiers, font_size=11.3, space_before=8)

    add_card(s5, Inches(8.2), Inches(1.52), Inches(4.333), Inches(5.32), "Sơ đồ Tổng thể & Dual-Trace", PRIMARY_BLUE)
    add_fitted_image(s5, "diagram_images/fig_overall_arch.png", Inches(8.35), Inches(1.98), Inches(4.033), Inches(4.72))

    # =========================================================================
    # SLIDE 6: PHƯƠNG PHÁP LUẬN KỸ THUẬT KIỂM THỬ (BLACK-BOX + WHITE/GREY-BOX)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6)
    add_header(s6, "5. Hệ thống Kỹ thuật Kiểm thử Áp dụng (Black-Box & Grey/White-Box)", "Kết hợp thiết kế ca kiểm thử chuẩn ISTQB với phân tích độ phủ & đột biến mã nguồn", 6)

    add_card(s6, Inches(0.8), Inches(1.52), Inches(5.7), Inches(5.32), "Kiểm thử Hộp đen (Black-Box — Flow Worker)", PRIMARY_BLUE)
    bb_items = [
        ("1. Phân vùng tương đương (Weak Robust EP):", "Tuân thủ giả định đơn lỗi (Single Fault Assumption): mỗi ca chỉ cho duy nhất 1 tham số nhận giá trị Invalid, các biến còn lại giữ Valid nhằm triệt tiêu hoàn toàn hiện tượng Che giấu lỗi (Fault Masking)."),
        ("2. Phân tích giá trị biên (BVA) 3 cấp độ:",
         "\n- Standard BVA (4n + 1): kiểm 5 điểm {min, min+, nom, max-, max} cho các biểu mẫu thông thường.\n"
         "- Robustness BVA (6n + 1): mở rộng 2 điểm ngoài biên {min-, max+} kiểm chứng Exception Handling (vd: rút dưới 50.000đ).\n"
         "- Worst-Case BVA (5^n): giả định đa lỗi đồng thời cho module tài chính rủi ro cao (Escrow, thuế/hoa hồng BigInt)."),
        ("3. Bảng quyết định (Decision Table):", "Lập ma trận tổ hợp điều kiện rẽ nhánh: Trạng thái eKYC x Số dư khả dụng x Tài khoản ngân hàng x Ngưỡng voucher."),
        ("4. Chuyển đổi trạng thái (FSM Testing):", "Kiểm thử cả Valid Transitions (PENDING -> ESCROW_HOLDING -> DELIVERED -> COMPLETED) lẫn Invalid Transitions (rút tiền khi đơn CANCELLED/DISPUTED).")
    ]
    add_bullets(s6, Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.75), bb_items, font_size=11.0, space_before=8)

    add_card(s6, Inches(6.8), Inches(1.52), Inches(5.7), Inches(5.32), "Kiểm thử Hộp xám / Hộp trắng & Đo độ phủ (CDP + Regression)", PRIMARY_BLUE)
    wb_items = [
        ("1. Grey-Box Dual-Trace (Playwright UI + CDP RAM):", "Tương tác từ giao diện người dùng (Hộp đen) để kích hoạt lỗi, đồng thời gắn WebSocket CDP vào Node.js runtime (Hộp trắng) đóng băng bộ nhớ Heap, đọc trực tiếp biến sai lệch và Callstack mà không cần sửa code."),
        ("2. Độ phủ câu lệnh (Phủ cấp 1 - Statement Coverage):", "Bộ test hồi quy do Tầng 6 sinh ra đảm bảo 100% các câu lệnh trong hàm/service phát sinh sự cố đều được thực thi."),
        ("3. Độ phủ nhánh (Phủ cấp 2 - Branch Coverage):", "Bảo đảm kiểm định đầy đủ cả hai nhánh True và False của mọi cấu trúc điều kiện (vd: đơn thương lượng vs đơn thường, sellerRank null vs verified)."),
        ("4. Độ phức tạp chu trình McCabe V(G) = P + 1:", "Tính toán số lượng đường đi độc lập tối thiểu dựa trên số điểm rẽ nhánh P để không bỏ sót kịch bản logic tiềm ẩn."),
        ("5. Kiểm thử đột biến (Mutation Testing):", "Tiêm 24 đột biến nhân tạo (đảo toán tử, biến đổi boolean, gán null/undefined) để đánh giá chất lượng bộ test qua chỉ số Mutation Score = Killed / Total.")
    ]
    add_bullets(s6, Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.75), wb_items, font_size=11.0, space_before=8)

    # =========================================================================
    # SLIDE 7: TRI THỨC KÉP, CI/CD VÀ BẰNG CHỨNG ẢNH THỰC TẾ (NO-CAP)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7)
    add_header(s7, "6. Tri thức Kép (RAG + Canvas), CI/CD & Bằng chứng Thực tế", "Trực quan hóa đồ thị lỗi 5ms, kiểm định tự động và bằng chứng minh bạch", 7)

    add_card(s7, Inches(0.8), Inches(1.52), Inches(5.4), Inches(2.6), "Vòng lặp Tri thức Kép & Pipeline CI/CD", PRIMARY_BLUE)
    add_bullets(s7, Inches(1.0), Inches(1.96), Inches(5.0), Inches(2.05), [
        ("RAG Markdown (knowledge/*.md):", "Lưu trữ triệu chứng, Network log, RAM Heap JSON và hướng dẫn tái hiện để AI học lại."),
        ("Canvas Note Engineer (.canvas.json):", "Chuẩn SpawnClusterPayload với 5 Pod chuyên biệt, nạp qua Local AST Parser chỉ ~5ms (0 Token)."),
        ("GitHub Actions CI/CD:", "Tự động kiểm định MCP Server (9 tools), Playwright Headless Runner và đóng gói Artifacts (screenshots/ + knowledge/).")
    ], font_size=10.3, space_before=5)

    add_card(s7, Inches(0.8), Inches(4.26), Inches(5.4), Inches(2.58), "Nguyên tắc Bằng chứng Thực tế (Zero Fake Overlays)", PRIMARY_BLUE)
    add_bullets(s7, Inches(1.0), Inches(4.7), Inches(5.0), Inches(2.05), [
        ("Kiểm chứng nghiêm ngặt (Strict Assertion):", "Mọi bước E2E bắt buộc xác minh HTTP status, URL đích và trạng thái DOM thật; nếu thất bại sẽ dừng và chụp ảnh lỗi (không tô màu xanh giả)."),
        ("Bằng chứng ảnh từng chặng:", "Lưu tại screenshots/ (ví dụ: detailed_01_buyer_order.png hiển thị đơn #T-6FT-2611-28903 và mã VietQR thật)."),
        ("Loại bỏ video giả lập:", "Xóa hoàn toàn file video cũ không đồng bộ; thay bằng trình duyệt Chrome chạy live trực tiếp + ảnh chụp chuẩn.")
    ], font_size=10.3, space_before=5)

    add_card(s7, Inches(6.4), Inches(1.52), Inches(6.133), Inches(5.32), "Minh họa Thực tế: Đồ thị Canvas & Ảnh chụp Đơn hàng VietQR", PRIMARY_BLUE)
    add_fitted_image(s7, "public/canvas-testops-demo.png", Inches(6.55), Inches(1.96), Inches(5.833), Inches(2.38))
    add_fitted_image(s7, "screenshots/detailed_01_buyer_order.png", Inches(6.55), Inches(4.42), Inches(5.833), Inches(2.3))

    # =========================================================================
    # SLIDE 8: KẾT QUẢ THỰC NGHIỆM VÀ PHÂN TÍCH LỖI (DEFECT LOG)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8)
    add_header(s8, "7. Kết quả Thực nghiệm & Phân tích Lỗi (Defect Log)", "Chỉ số đo lường định lượng và 6 lỗi thực tế phát hiện trên nền tảng TrustBase", 8)

    add_card(s8, Inches(0.8), Inches(1.52), Inches(5.5), Inches(5.32), "Chỉ số Định lượng Thực nghiệm (Đối chứng)", PRIMARY_BLUE)
    metrics = [
        ("Bộ ca kiểm thử 30 Test Cases (6 Flows):", "Vòng đầu đạt 26/30 (86.7%, phát hiện lỗi ở 4 luồng); sau khi vá lỗi và chạy hồi quy đạt 30/30 (100% PASS)."),
        ("Thời gian thực thi 6 luồng song song:", "Giảm từ 45-60 phút (tuần tự/thủ công) xuống còn 12-15 phút nhờ 3 Worker Swarm cô lập contextId."),
        ("Độ chính xác định vị mã nguồn (RCA):", "Đạt > 88% (chỉ thẳng file:dòng & biến Heap qua CDP) so với < 15% của E2E truyền thống; giảm MTTR xuống 15-25 phút."),
        ("Kiểm thử Đột biến (Mutation Testing):", "Bộ test hồi quy tự sinh tiêu diệt 22/24 đột biến, đạt Mutation Score 91.67% (vượt trội mức 45.8% viết tay) & Phủ nhánh 100%."),
        ("Chống Flaky & Tốc độ trực quan hóa:", "Tỷ lệ Flaky < 2.0% nhờ Port Killer + Auto-wait; nạp đồ thị Canvas mất ~5ms thay vì 15-30 phút đọc raw log.")
    ]
    add_bullets(s8, Inches(1.0), Inches(2.0), Inches(5.1), Inches(4.7), metrics, font_size=11.3, space_before=10)

    add_card(s8, Inches(6.5), Inches(1.52), Inches(6.033), Inches(5.32), "Nhật ký 6 Lỗi Thực tế trên TrustBase (SUT)", PRIMARY_BLUE)
    defects = [
        ("DEF-001 [High] Khóa rút tiền Seller do ràng buộc eKYC:", "Người bán có số dư 12.155.000 đ nhưng nút rút tiền bị vô hiệu hóa bởi cờ seller:kyc_gate_payouts khi onboarding_progress chưa approved."),
        ("DEF-002 [Medium] Biểu mẫu thanh toán/đăng ký chặn domain email:", "Chính sách allowlist chỉ chấp nhận Gmail/Yahoo/Outlook, từ chối các email tên miền doanh nghiệp/trường học hợp lệ (.vn, .local)."),
        ("DEF-003 [High] HTTP 500 khi áp mã Voucher ở đơn thương lượng/hết hạn:", "Thiếu null-check trên đối tượng phân hạng giá (tier/sellerRank) làm văng Uncaught TypeError thay vì trả HTTP 400 có kiểm soát."),
        ("DEF-004 [Medium] Trùng lặp định danh DOM Desktop & Mobile:", "Giao diện render song song 2 input ẩn/hiện dễ khiến script tự động tương tác nhầm phần tử ẩn."),
        ("DEF-005 [Medium] Admin Console thiếu cảnh báo cấu hình VietQR:", "Chưa hiển thị cảnh báo rõ ràng khi người bán chưa hoàn tất tài khoản thụ hưởng VietQR trong luồng duyệt chi trả."),
        ("DEF-006 [Low] Thiếu cơ chế tự hủy đơn hàng ký quỹ quá hạn 24h:", "Đơn hàng ở trạng thái chờ thanh toán vượt ngưỡng TTL không tự chuyển về trạng thái hủy để nhả tồn kho.")
    ]
    add_bullets(s8, Inches(6.7), Inches(1.98), Inches(5.633), Inches(4.75), defects, font_size=10.8, space_before=7)

    # =========================================================================
    # SLIDE 9: HANDBOOK ÁP DỤNG CHO SRC BẤT KỲ & KỊCH BẢN DEMO 10 PHÚT
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9)
    add_header(s9, "8. Handbook Tích hợp cho Mọi Dự án (src) & Kế hoạch Demo 10 phút", "Quy trình 4 bước cắm vào mã nguồn bất kỳ và phân bổ thời lượng báo cáo", 9)

    add_card(s9, Inches(0.8), Inches(1.52), Inches(5.7), Inches(5.32), "Cài đặt & Sử dụng cho 1 Mã nguồn (src) bất kỳ", PRIMARY_BLUE)
    handbook_steps = [
        ("Bước 1 — Cài Plugin Zero-Impact (1 lần):", "Chạy 'cd mcp && npm install && .\\setup-browser.ps1'. Gắn mcp/server.mjs vào Antigravity / Claude Code (tùy chọn set CANVAS_RAG_DIR) và copy vscode/launch.json vào src."),
        ("Bước 2 — Bật Backend đích kèm Debug Port:", "Chạy server của src với NODE_OPTIONS='--inspect=0.0.0.0:9229' hoặc để Agent tự gọi debug_start_server."),
        ("Bước 3 — Ra lệnh Prompt chuẩn kỹ thuật:",
         "\n- Black-Box: Yêu cầu Agent chạy BVA (4n+1, 6n+1, 5^n), Weak Robust EP, Decision Table, FSM trên URL.\n"
         "- Grey/White-Box: Mở Chrome live (headless: false), gặp 500 thì gắn debug_inspect_cdp soi biến RAM & sinh test phủ nhánh."),
        ("Bước 4 — Đọc Bằng chứng & Đồ thị:", "Kiểm tra ảnh trong screenshots/, file phân tích .md và kéo thả .canvas.json trong knowledge/ vào Canvas Note Engineer.")
    ]
    add_bullets(s9, Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.7), handbook_steps, font_size=11.0, space_before=9)

    add_card(s9, Inches(6.8), Inches(1.52), Inches(5.7), Inches(5.32), "Kịch bản Báo cáo & Demo trực quan trong 10 phút", PRIMARY_BLUE)
    schedule = [
        ("00:00 - 02:00 (2.0 phút) | Trình bày Tổng quan:", "Giới thiệu bài toán TrustBase, V-Model, Kiến trúc MCP 6 tầng, bộ kỹ thuật Hộp đen/Hộp trắng và Tự đánh giá thành viên."),
        ("02:00 - 06:30 (4.5 phút) | Demo Live trên Chrome thật:",
         "\n- Bật CHAY_DEMO_AGENTIC_TESTOPS.bat & XUAT_BANG_CHUNG_TESTOPS.bat cho Thầy quan sát Chrome tự điền form, tạo đơn VietQR thật và kiểm chứng trạng thái Seller/Admin.\n"
         "- Mở trực tiếp đồ thị Canvas Note Engineer nạp file .canvas.json trong 5ms."),
        ("06:30 - 08:30 (2.0 phút) | Chứng minh HANDBOOK, Test & CI:", "Mở HANDBOOK.md (cách test src bất kỳ), file test hồi quy .spec.ts, kết quả test MCP Server và cấu hình .github/workflows/agentic-testops-ci.yml."),
        ("08:30 - 10:00 (1.5 phút) | Vấn đáp cùng ThS. Lê Phi Hùng:", "Giải đáp chuyên sâu về giao thức MCP, kỹ thuật CDP Heap Inspection, BVA/EP/Mutation Score.")
    ]
    add_bullets(s9, Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.7), schedule, font_size=11.0, space_before=9)

    # =========================================================================
    # SLIDE 10: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN ĐỀ TÀI
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10)
    add_header(s10, "9. Kết luận, Hướng phát triển & Lời cảm ơn", "Tổng kết đóng góp khoa học và tri ân Giảng viên hướng dẫn", 10)

    add_card(s10, Inches(0.8), Inches(1.52), Inches(5.7), Inches(5.32), "Đóng góp chính của đề tài", PRIMARY_BLUE)
    concl = [
        ("1. Kiến trúc MCP 6 tầng Zero-Impact:", "Đóng gói độc lập hoàn chỉnh, cho phép gắn vào bất kỳ dự án Web/Node.js nào mà không làm biến đổi mã nguồn gốc."),
        ("2. Đột phá Grey-Box Dual-Trace:", "Kết hợp hoàn hảo Kiểm thử Hộp đen trên Playwright (EP, BVA 3 cấp, Decision Table, FSM) với Kiểm thử Hộp trắng qua CDP soi biến Heap RAM và Callstack."),
        ("3. Tri thức Kép & Độ phủ Hồi quy cao:", "Tự động xuất RAG Markdown cho AI và Canvas JSON (AST 5ms) cho kỹ sư, kèm bộ test hồi quy đạt Mutation Score 91.67%."),
        ("4. Thực nghiệm nghiêm ngặt trên TrustBase:", "Phát hiện 6 lỗi thực tế và hoàn thiện Sổ tay HANDBOOK.md kèm quy trình bằng chứng ảnh/DOM xác thực 100%.")
    ]
    add_bullets(s10, Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.65), concl, font_size=11.0, space_before=9)

    add_card(s10, Inches(6.8), Inches(1.52), Inches(5.7), Inches(5.32), "Hướng phát triển & Lời cảm ơn", PRIMARY_BLUE)
    tb = s10.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.65))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    futs = [
        ("Hướng phát triển tiếp theo:", True, PRIMARY_BLUE),
        ("- Tích hợp kiểm thử tải k6 và quét bảo mật OWASP ZAP trực tiếp thành tool trong MCP Server.", False, TEXT_MAIN),
        ("- Tự động sinh Pull Request kèm bản vá mã nguồn (Self-Healing Code) đã được kiểm chứng qua Mutation Testing.", False, TEXT_MAIN),
        ("- Hỗ trợ gỡ lỗi đa ngôn ngữ ngoài Node.js: Python (debugpy), Java (JDWP) và Go (Delve).", False, TEXT_MAIN),
        ("", False, TEXT_MAIN),
        ("Lời cảm ơn:", True, PRIMARY_BLUE),
        ("Nhóm 05 xin trân trọng cảm ơn ThS. Lê Phi Hùng đã tận tình giảng dạy, định hướng chuyên môn và đóng góp những nhận xét quý báu giúp nhóm hoàn thiện đồ án học phần Kiểm thử và Đảm bảo Chất lượng Phần mềm.", False, TEXT_MAIN),
        ("", False, TEXT_MAIN),
        ("Trân trọng cảm ơn Thầy và các bạn đã lắng nghe!", True, ACCENT_BLUE)
    ]
    for i, (txt, is_bold, col) in enumerate(futs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = txt
        p.font.name = "Times New Roman"
        p.font.size = Pt(11.2)
        p.font.bold = is_bold
        p.font.color.rgb = col
        p.space_before = Pt(3.5)

    prs.save(output_path)
    print(f"Đã tạo bài thuyết trình học thuật 10 slides tại: {output_path}")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nhom05_AgenticTestOps_ThuyetTrinh.pptx")
    build_academic_presentation(out)
