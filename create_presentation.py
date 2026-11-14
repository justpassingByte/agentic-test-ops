# -*- coding: utf-8 -*-
"""
Tạo slide PowerPoint báo cáo thi cuối kỳ (Chuẩn 10 slides, 16:9, Chuyên nghiệp)
Đề tài: Nghiên cứu kỹ thuật Agentic TestOps và ứng dụng kiểm thử hệ thống TrustBase
GVHD: ThS. Lê Phi Hùng - ĐH Nông Lâm TP.HCM
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation(output_path):
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Bảng màu
    BG_DARK = RGBColor(15, 23, 42)      # #0f172a
    PRIMARY = RGBColor(37, 99, 235)     # #2563eb
    PRIMARY_LIGHT = RGBColor(96, 165, 250) # #60a5fa
    ACCENT_GREEN = RGBColor(16, 185, 129)  # #10b981
    ACCENT_AMBER = RGBColor(245, 158, 11)  # #f59e0b
    TEXT_LIGHT = RGBColor(248, 250, 252)   # #f8fafc
    TEXT_MUTED = RGBColor(148, 163, 184)   # #94a3b8
    CARD_BG = RGBColor(30, 41, 59)         # #1e293b
    CARD_BORDER = RGBColor(51, 65, 85)     # #334155

    def add_background(slide, color=BG_DARK):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, subtitle_text="BÁO CÁO ĐỒ ÁN MÔN HỌC - KIỂM THỬ & ĐBCLPM"):
        # Header banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_sub = tf.paragraphs[0]
        p_sub.text = subtitle_text.upper()
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = PRIMARY_LIGHT
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_LIGHT

    def add_card(slide, left, top, width, height, title="", border_color=PRIMARY):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        
        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Segoe UI"
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = PRIMARY_LIGHT
        return card

    # =========================================================================
    # SLIDE 1: TRANG BÌA
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1)
    
    # Title box
    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(4.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "TRƯỜNG ĐẠI HỌC NÔNG LÂM TP. HỒ CHÍ MINH — KHOA CÔNG NGHỆ THÔNG TIN"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_LIGHT
    
    p = tf1.add_paragraph()
    p.text = "BÁO CÁO THI CUỐI KỲ — ĐỒ ÁN KIỂM THỬ & ĐBCL PHẦN MỀM"
    p.font.name = "Segoe UI"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_before = Pt(8)
    
    p = tf1.add_paragraph()
    p.text = "NGHIÊN CỨU KỸ THUẬT AGENTIC TESTOPS\nVÀ ỨNG DỤNG KIỂM THỬ HỆ THỐNG TRUSTBASE"
    p.font.name = "Segoe UI"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    p.space_before = Pt(16)
    
    p = tf1.add_paragraph()
    p.text = "Kiểm thử tự động chu trình giao dịch đa phân vai (Buyer -> Seller -> Admin) với cơ chế Tự sinh kịch bản, Tự chữa lành & Xuất bằng chứng kép (Dual Visual Evidence)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(12)

    # Info card at bottom
    add_card(s1, Inches(1.0), Inches(5.3), Inches(11.333), Inches(1.5), "", ACCENT_GREEN)
    ibox = s1.shapes.add_textbox(Inches(1.2), Inches(5.4), Inches(11.0), Inches(1.3))
    itf = ibox.text_frame
    itf.word_wrap = True
    
    p = itf.paragraphs[0]
    p.text = "👨‍🏫 Giảng viên hướng dẫn: ThS. LÊ PHI HÙNG"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    
    p = itf.add_paragraph()
    p.text = "👥 Nhóm thực hiện: NHÓM 05 | Thành viên: Nguyễn Hữu Thắng (Nhóm trưởng) — Phạm Trần Nhụt Quang — Huỳnh Văn Sĩ"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.color.rgb = PRIMARY_LIGHT
    p.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: THÀNH VIÊN NHÓM & TỰ ĐÁNH GIÁ (THANG ĐIỂM 10)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2)
    add_header(s2, "1. GIỚI THIỆU THÀNH VIÊN VÀ BẢNG TỰ ĐÁNH GIÁ ĐÓNG GÓP", "PHÂN CÔNG & ĐÁNH GIÁ TRÁCH NHIỆM")

    members = [
        {
            "name": "Nguyễn Hữu Thắng",
            "role": "Nhóm trưởng / Test Lead",
            "score": "10 / 10",
            "pct": "100%",
            "color": ACCENT_GREEN,
            "tasks": [
                "Nghiên cứu nguyên lý & kiến trúc Agentic TestOps",
                "Xây dựng MCP Server điều khiển CDP & Playwright",
                "Phát triển kịch bản kiểm thử E2E đa phân vai",
                "Tích hợp GitHub Actions CI/CD & Xuất video bằng chứng",
                "Chịu trách nhiệm thuyết trình chính & Demo live"
            ]
        },
        {
            "name": "Phạm Trần Nhụt Quang",
            "role": "QA Engineer / Test Designer",
            "score": "9.5 / 10",
            "pct": "100%",
            "color": PRIMARY,
            "tasks": [
                "Thiết kế Test Suite 30 Test Case cho hệ thống TrustBase",
                "Áp dụng 4 kỹ thuật kiểm thử hộp đen (EP, BVA, Decision Table, State Transition)",
                "Soạn thảo tài liệu đặc tả kiểm thử & ma trận truy vết (RTM)",
                "Đóng góp hoàn thiện Báo cáo Word 4 phần chuẩn quy định",
                "Hỗ trợ trả lời vấn đáp kỹ thuật kiểm thử"
            ]
        },
        {
            "name": "Huỳnh Văn Sĩ",
            "role": "Automation Engineer / QA Analyst",
            "score": "9.5 / 10",
            "pct": "100%",
            "color": ACCENT_AMBER,
            "tasks": [
                "Theo dõi, ghi nhận và quản lý 6 Defect Log thực tế",
                "Kiểm thử bảo mật (OWASP, SQLi, IDOR) & Kiểm thử tải SUT",
                "Tổng hợp số liệu Dashboard KPI chất lượng phần mềm",
                "Thiết kế bố cục Slide thuyết trình 10 trang & Đóng gói sản phẩm",
                "Hỗ trợ chuẩn bị môi trường Docker & cơ sở dữ liệu"
            ]
        }
    ]

    for i, m in enumerate(members):
        left = Inches(0.8 + i * 4.0)
        add_card(s2, left, Inches(1.7), Inches(3.733), Inches(5.2), "", m["color"])
        
        tb = s2.shapes.add_textbox(left + Inches(0.2), Inches(1.9), Inches(3.333), Inches(4.8))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = m["name"]
        p.font.name = "Segoe UI"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        
        p = tf.add_paragraph()
        p.text = m["role"]
        p.font.name = "Segoe UI"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = m["color"]
        
        p = tf.add_paragraph()
        p.text = f"Điểm tự chấm: {m['score']}  |  Đóng góp: {m['pct']}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(6)
        
        p = tf.add_paragraph()
        p.text = "Trách nhiệm & Sản phẩm bàn giao:"
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_LIGHT
        p.space_before = Pt(8)
        
        for task in m["tasks"]:
            p = tf.add_paragraph()
            p.text = f"• {task}"
            p.font.name = "Segoe UI"
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_MUTED
            p.space_before = Pt(4)

    # =========================================================================
    # SLIDE 3: HỆ THỐNG MỤC TIÊU TRUSTBASE & BÀI TOÁN KIỂM THỬ ĐA PHÂN VAI
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3)
    add_header(s3, "2. HỆ THỐNG KIỂM THỬ TRUSTBASE (SUT) & BÀI TOÁN KIỂM THỬ", "BỐI CẢNH THỰC TẾ & THÁCH THỨC")

    add_card(s3, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.2), "🏢 Giới thiệu Sàn Bản Quyền Số TrustBase", PRIMARY)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    pts = [
        ("Bản chất SUT:", "TrustBase là sàn thương mại điện tử chuyên biệt phân phối License Key, Steam Wallet, Voucher số với cơ chế Ký quỹ bảo đảm giao dịch trung gian (Digital Key Escrow)."),
        ("Công nghệ xây dựng:", "Kiến trúc Monorepo hiện đại gồm Customer Web (Port 4200), Admin Console (Port 4203), Backend Fastify API (Port 4201), PostgreSQL 15 (Docker) và Redis Cache."),
        ("Quy mô kiểm thử:", "54 bảng dữ liệu, 56 seed listings, 5 gian hàng mẫu và hệ thống tích hợp thanh toán VietQR đa ngân hàng.")
    ]
    for i, (k, v) in enumerate(pts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(10)

    add_card(s3, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.2), "⚠️ Thách Thức Khi Kiểm Thử Chu Trình Đa Phân Vai", ACCENT_AMBER)
    tb2 = s3.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    
    pts2 = [
        ("Vòng đời 3 Phân vai:", "Buyer (mua hàng, tiền đóng băng trong Escrow) -> Seller (giao key, hoàn tất KYC, yêu cầu rút tiền Payout) -> Admin (thẩm định gian hàng, đối soát và giải ngân)."),
        ("Kiểm thử thủ công (Manual):", "Tốn 15-20 phút cho một vòng lặp, dễ sót trạng thái, chuyển đổi session/cookie giữa 3 tài khoản rất dễ nhầm lẫn."),
        ("Kiểm thử tự động cũ (Automation):", "Kịch bản Playwright/Cypress thông thường dễ bị 'gãy' (Flaky) khi UI thay đổi class, không tự xử lý được các logic nghiệp vụ phức tạp như KYC payout lock.")
    ]
    for i, (k, v) in enumerate(pts2):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(10)

    # =========================================================================
    # SLIDE 4: GIẢI PHÁP AGENTIC TESTOPS LÀ GÌ?
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4)
    add_header(s4, "3. GIẢI PHÁP ĐỀ XUẤT: AGENTIC TESTOPS TIÊN PHONG", "ĐỘT PHÁ CÔNG NGHỆ KIỂM THỬ THẾ HỆ MỚI")

    add_card(s4, Inches(0.8), Inches(1.7), Inches(11.733), Inches(1.5), "💡 Bản chất của Agentic TestOps", PRIMARY)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(0.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Agentic TestOps là sự kết hợp giữa Mô hình Ngôn ngữ Lớn (LLM Agent), Giao thức Bối cảnh Chuẩn hóa (Model Context Protocol - MCP) và Khung kiểm thử tự động (Playwright/CDP). Agent đóng vai trò là một 'Kỹ sư QA thông minh' có thể tự tư duy, tự khám phá hệ sinh thái SUT và tự hành động."
    p.font.name = "Segoe UI"
    p.font.size = Pt(12.5)
    p.font.color.rgb = TEXT_LIGHT

    # So sánh 2 cột
    add_card(s4, Inches(0.8), Inches(3.4), Inches(5.7), Inches(3.5), "❌ Traditional Test Automation", CARD_BORDER)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(3.9), Inches(5.3), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True
    trad = [
        "Con người phải tự gõ code kịch bản (.spec.ts) thủ công từ đầu đến cuối.",
        "Kịch bản cứng (Hardcoded): UI đổi class hay ID là test gãy lập tức.",
        "Báo lỗi thụ động: Chỉ in ra assertion fail, không phân tích tại sao lỗi.",
        "Không biết xử lý luồng nghiệp vụ rẽ nhánh hoặc điều kiện tiên quyết (eKYC, OTP)."
    ]
    for i, t in enumerate(trad):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {t}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(6)

    add_card(s4, Inches(6.8), Inches(3.4), Inches(5.7), Inches(3.5), "✅ Agentic TestOps (Đề tài Nhóm 05)", ACCENT_GREEN)
    tb = s4.shapes.add_textbox(Inches(7.0), Inches(3.9), Inches(5.3), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True
    ag = [
        "Tự động sinh kịch bản test (Test Generation): Đọc DOM & API để tự viết code.",
        "Tự chữa lành kịch bản (Self-Healing): Tự phát hiện và cập nhật selector mới.",
        "Tự điều tra nguyên nhân gốc (Autonomous Root Cause Analysis): Đọc log DB & HTTP.",
        "Tự quản lý phiên đa phân vai: Tự động switch cookie Buyer -> Seller -> Admin."
    ]
    for i, t in enumerate(ag):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {t}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(6)

    # =========================================================================
    # SLIDE 5: KIẾN TRÚC KỸ THUẬT CỦA HỆ THỐNG
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5)
    add_header(s5, "4. KIẾN TRÚC KỸ THUẬT HỆ THỐNG AGENTIC TESTOPS", "THIẾT KẾ 4 TẦNG MODULE HÓA")

    layers = [
        ("TẦNG 1: LLM REASONING & ORCHESTRATION", "Đóng vai trò 'Bộ não' phân tích yêu cầu, chia tách kịch bản đa phân vai, lập kế hoạch hành động và diễn giải kết quả kiểm thử.", PRIMARY),
        ("TẦNG 2: GIAO THỨC CHUẨN HÓA MCP & CDP", "MCP Server (mcp/server.mjs) cung cấp công cụ chuẩn cho Agent: đọc DOM, dispatch click, nạp cookie, quản lý process cổng debug Node.js.", PRIMARY_LIGHT),
        ("TẦNG 3: AUTOMATION ENGINE & RECORDER", "Playwright kết hợp Chrome thật và FFmpeg engine: Thực thi thao tác gõ phím, click chuột thật, chụp ảnh checkpoints và ghi video 60fps.", ACCENT_AMBER),
        ("TẦNG 4: APPLICATION UNDER TEST (SUT)", "Môi trường TrustBase chạy nội bộ qua Docker: Web Khách (4200), Web Admin (4203), Fastify API (4201), PostgreSQL (5432) và Redis (6379).", ACCENT_GREEN)
    ]

    for i, (l_title, l_desc, color) in enumerate(layers):
        top = Inches(1.7 + i * 1.3)
        add_card(s5, Inches(0.8), top, Inches(11.733), Inches(1.15), "", color)
        tb = s5.shapes.add_textbox(Inches(1.0), top + Inches(0.12), Inches(11.333), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = l_title
        p.font.name = "Segoe UI"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = color
        
        p = tf.add_paragraph()
        p.text = l_desc
        p.font.name = "Segoe UI"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(3)

    # =========================================================================
    # SLIDE 6: THIẾT KẾ TEST SUITE & 4 KỸ THUẬT HỘP ĐEN
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6)
    add_header(s6, "5. THIẾT KẾ TEST SUITE (30 TEST CASES) & KỸ THUẬT HỘP ĐEN", "CHUẨN HÓA KIỂM THỬ THEO ISTQB")

    techs = [
        ("Phân Vùng Tương Đương (EP)", "Phân chia lớp hợp lệ và không hợp lệ cho thông tin người mua (Email domain allowlist, số điện thoại Việt Nam chuẩn 10 số, số tiền nạp rút).", PRIMARY),
        ("Phân Tích Giá Trị Biên (BVA)", "Kiểm thử giá trị cận biên của hạn mức rút tiền (Tối thiểu 50.000 ₫, tối đa 50.000.000 ₫), số lượng mua key (1 key đến tồn kho tối đa).", PRIMARY_LIGHT),
        ("Bảng Quyết Định (Decision Table)", "Kiểm thử ma trận logic điều kiện: Trạng thái KYC của Shop x Số dư khả dụng x Tài khoản ngân hàng liên kết => Quyết định cho phép rút hay khóa nút.", ACCENT_AMBER),
        ("Chuyển Đổi Trạng Thái (State Transition)", "Kiểm thử vòng đời trạng thái Escrow và Payout: CREATED -> ESCROW_HOLDING -> DELIVERED -> COMPLETED hoặc DISPUTED -> REFUNDED.", ACCENT_GREEN)
    ]

    for i, (t_title, t_desc, color) in enumerate(techs):
        top = Inches(1.7 + (i % 2) * 2.6)
        left = Inches(0.8 if i < 2 else 6.8)
        # 0: left, top 1.7; 1: left, top 4.3; 2: right, top 1.7; 3: right, top 4.3
        col_left = Inches(0.8) if i in [0, 1] else Inches(6.8)
        col_top = Inches(1.7) if i in [0, 2] else Inches(4.3)
        
        add_card(s6, col_left, col_top, Inches(5.7), Inches(2.4), f"🎯 {t_title}", color)
        tb = s6.shapes.add_textbox(col_left + Inches(0.2), col_top + Inches(0.55), Inches(5.3), Inches(1.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = t_desc
        p.font.name = "Segoe UI"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_LIGHT

    # =========================================================================
    # SLIDE 7: TÍCH HỢP CI/CD PIPELINE & BẰNG CHỨNG KÉP
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7)
    add_header(s7, "6. TÍCH HỢP CI/CD PIPELINE & CHIẾN LƯỢC BẰNG CHỨNG KÉP", "TỰ ĐỘNG HÓA HOÀN TOÀN TRÊN GITHUB ACTIONS")

    add_card(s7, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.2), "⚙️ Quy Trình CI/CD Pipeline (GitHub Actions)", PRIMARY)
    tb = s7.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    cicd_steps = [
        "1. Kích hoạt tự động: Khi Developer tạo Pull Request hoặc Push code lên nhánh main/develop.",
        "2. Service Containers: Tự động dựng Postgres 15 và Redis trong runner Ubuntu để phục vụ SUT.",
        "3. Setup Headless Chrome & FFmpeg: Cài đặt Playwright engine hỗ trợ quay video độ phân giải cao.",
        "4. Kích hoạt Agentic Runner: Chạy kịch bản đa phân vai khép kín 3 vai trò trong vòng ~60 giây.",
        "5. Xuất Artifacts: Đóng gói toàn bộ bằng chứng kiểm thử nạp lên GitHub Actions."
    ]
    for i, s in enumerate(cicd_steps):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = s
        p.font.name = "Segoe UI"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(8)

    add_card(s7, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.2), "📸 Chiến Lược Bằng Chứng Kép (Dual Visual Evidence)", ACCENT_GREEN)
    tb = s7.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    evidence_pts = [
        "Tại sao cần Bằng chứng kép?",
        "• 1. Ảnh Screenshots (.png): Bằng chứng xác định tại các checkpoint quan trọng (Đã tạo đơn, Đã bấm rút tiền, Đã giải ngân) để xem nhanh trên PR mà không cần tải video.",
        "• 2. Video Ghi hình (.webm): Bằng chứng liên tục chứng minh tương tác thật 100% (Gõ bàn phím, click chuột, QR code VietQR xuất hiện, chuyển vai), loại trừ việc làm giả kết quả.",
        "• Cơ chế if: always(): Ngay cả khi kiểm thử gặp lỗi (Fail), pipeline vẫn xuất toàn bộ video tại giây phút lỗi để lập trình viên điều tra ngay lập tức."
    ]
    for i, s in enumerate(evidence_pts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = s
        p.font.name = "Segoe UI"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(6)

    # =========================================================================
    # SLIDE 8: KẾT QUẢ THỰC NGHIỆM & 6 DEFECTS PHÁT HIỆN
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8)
    add_header(s8, "7. KẾT QUẢ KIỂM THỬ THỰC NGHIỆM & BÁO CÁO LỖI (DEFECT LOG)", "PHÁT HIỆN 6 LỖI NGHIỆM THU THỰC TẾ TRÊN TRUSTBASE")

    defects = [
        ("DEF-001 (High)", "Khóa rút tiền do KYC ngầm: Người bán có số dư nhưng nút rút bị disable do feature flag 'seller:kyc_gate_payouts' chưa thỏa điều kiện onboarding_progress."),
        ("DEF-002 (Medium)", "Form Checkout chặn email hợp lệ: Allowlist chỉ chấp nhận Gmail/Yahoo/Outlook, từ chối email doanh nghiệp/tên miền riêng."),
        ("DEF-003 (High)", "Lỗi HTTP 500 khi áp dụng voucher hết hạn: Backend ném Unhandled Exception thay vì trả về lỗi nghiệp vụ 400 Bad Request kèm thông báo thân thiện."),
        ("DEF-004 (Medium)", "Xung đột selector giao diện Desktop vs Mobile: Form Checkout render trùng lặp cả input mobile và desktop khiến automation bị click nhầm phần tử ẩn."),
        ("DEF-005 (Medium)", "Admin Console thiếu cảnh báo trạng thái Payout: Chưa hiển thị badge cảnh báo nếu người bán chưa liên kết thông tin thanh toán VietQR."),
        ("DEF-006 (Low)", "Thiếu cơ chế tự động giải phóng đơn ký quỹ hết hạn: Đơn hàng quá 24h không thanh toán vẫn giữ trạng thái PENDING thay vì CANCELLED.")
    ]

    for i, (d_title, d_desc) in enumerate(defects):
        top = Inches(1.7 + (i % 3) * 1.7)
        left = Inches(0.8 if i < 3 else 6.8)
        color = ACCENT_AMBER if "High" in d_title else PRIMARY_LIGHT
        
        add_card(s8, left, top, Inches(5.7), Inches(1.55), f"🐞 {d_title}", color)
        tb = s8.shapes.add_textbox(left + Inches(0.2), top + Inches(0.45), Inches(5.3), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = d_desc
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # =========================================================================
    # SLIDE 9: KẾ HOẠCH DEMO THỰC TẾ & BỐ TRÍ THỜI GIAN 10 PHÚT
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9)
    add_header(s9, "8. KẾ HOẠCH DEMO THỰC TẾ & PHÂN BỔ THỜI GIAN 10 PHÚT", "BỐ TRÍ BÁO CÁO KHOA HỌC — ĐÚNG QUY ĐỊNH HỘI ĐỒNG")

    schedule = [
        ("00:00 - 02:00 (2 phút)", "BÁO CÁO SLIDES TỔNG QUAN", "Giới thiệu thành viên, mục tiêu đề tài, bài toán kiểm thử đa phân vai trên TrustBase và bảng tự chấm điểm thang 10.", PRIMARY),
        ("02:00 - 06:30 (4.5 phút)", "DEMO TRỰC QUAN CHU TRÌNH 3 PHÂN VAI", "Chiếu Video thực tế / Demo live: Buyer đặt mua Steam Wallet (Escrow VietQR) -> Seller yêu cầu rút tiền Payout -> Admin thẩm định port 4203.", ACCENT_GREEN),
        ("06:30 - 08:30 (2 phút)", "DEMO FILE TEST TỰ SINH & CI/CD PIPELINE", "Mở file test script chuẩn Playwright do Agent tự sinh ra (tests/*.spec.ts) và quy trình GitHub Actions xuất Artifacts.", PRIMARY_LIGHT),
        ("08:30 - 10:00 (1.5 phút)", "TRẢ LỜI CÂU HỎI VẤN ĐÁP (Q&A)", "Giải đáp câu hỏi chuyên môn của Thầy Lê Phi Hùng về MCP Protocol, Self-healing, và tính trung thực của bằng chứng kép.", ACCENT_AMBER)
    ]

    for i, (t_time, t_step, t_detail, color) in enumerate(schedule):
        top = Inches(1.7 + i * 1.3)
        add_card(s9, Inches(0.8), top, Inches(11.733), Inches(1.15), "", color)
        tb = s9.shapes.add_textbox(Inches(1.0), top + Inches(0.12), Inches(11.333), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"{t_time} — {t_step}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = color
        
        p = tf.add_paragraph()
        p.text = t_detail
        p.font.name = "Segoe UI"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(3)

    # =========================================================================
    # SLIDE 10: KẾT LUẬN & ĐÓNG GÓP CỦA ĐỒ ÁN
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10)
    add_header(s10, "9. KẾT LUẬN, ĐÓNG GÓP & LỜI CẢM ƠN", "TỔNG KẾT KẾT QUẢ ĐỒ ÁN MÔN HỌC")

    add_card(s10, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.2), "🏆 Đóng Góp Chính Của Đề Tài", PRIMARY)
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    concl = [
        "1. Ứng dụng thành công kỹ thuật Agentic TestOps tiên phong vào hệ thống thực tế TrustBase, chứng minh tính khả thi vượt trội so với Automation truyền thống.",
        "2. Giải quyết triệt để bài toán kiểm thử chu trình đa phân vai (Multi-Role Lifecycle) phức tạp kéo dài qua 3 thực thể (Buyer -> Seller -> Admin).",
        "3. Xây dựng thành công cơ chế Bằng chứng kép (Dual Visual Evidence) trên CI/CD, xuất đồng thời Screenshots và Video ghi hình thực tế 100%.",
        "4. Phát hiện 6 Defect nghiệp vụ quan trọng giúp củng cố chất lượng cho hệ thống TrustBase."
    ]
    for i, c in enumerate(concl):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = c
        p.font.name = "Segoe UI"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(8)

    add_card(s10, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.2), "🚀 Định Hướng & Lời Cảm Ơn", ACCENT_GREEN)
    tb = s10.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    futs = [
        "Định hướng phát triển:",
        "• Mở rộng bộ công cụ MCP kết nối với kiểm thử hiệu năng k6 và kiểm thử bảo mật tự động ZAP.",
        "• Tích hợp Agent tự động tạo GitHub Issues kèm video và stack trace khi phát hiện bug.",
        "",
        "LỜI CẢM ƠN CHÂN THÀNH:",
        "Nhóm 05 xin trân trọng gửi lời cảm ơn sâu sắc đến ThS. Lê Phi Hùng đã tận tình hướng dẫn, truyền đạt kiến thức và định hướng quý báu cho nhóm trong suốt môn học Kiểm thử & Đảm bảo Chất lượng Phần mềm.",
        "",
        "XIN CHÂN THÀNH CẢM ƠN THẦY VÀ CÁC BẠN ĐÃ LẮNG NGHE!"
    ]
    for i, f in enumerate(futs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f
        p.font.name = "Segoe UI"
        p.font.size = Pt(11.5)
        if "LỜI CẢM ƠN" in f or "XIN CHÂN THÀNH" in f:
            p.font.bold = True
            p.font.color.rgb = ACCENT_AMBER
        elif "Định hướng" in f:
            p.font.bold = True
            p.font.color.rgb = PRIMARY_LIGHT
        else:
            p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(4)

    # Lưu file
    prs.save(output_path)
    print(f"Đã tạo file trình chiếu PowerPoint thành công: {output_path}")

if __name__ == "__main__":
    out = r"C:\Users\NoNomt007\agentic-test-ops\Nhom05_AgenticTestOps_ThuyetTrinh.pptx"
    build_presentation(out)
