# -*- coding: utf-8 -*-
"""
Tạo bài thuyết trình PowerPoint báo cáo đồ án môn học (Chuẩn 10 slides, 16:9)
Phong cách: Học thuật, trang trọng, không màu mè, không emoji, không dấu gạch nối kiểu AI.
Đề tài: Nghiên cứu kỹ thuật Agentic TestOps và ứng dụng kiểm thử hệ thống TrustBase
GVHD: ThS. Lê Phi Hùng - Trường ĐH Nông Lâm TP.HCM - Khoa CNTT
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_academic_presentation(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Bảng màu học thuật (Academic Formal Theme: Off-white nền sáng, chữ xanh đậm và than chì)
    BG_PAGE = RGBColor(248, 250, 252)       # Slate 50
    CARD_BG = RGBColor(255, 255, 255)       # Pure White
    CARD_BORDER = RGBColor(203, 213, 225)   # Slate 300
    HEADER_NAVY = RGBColor(15, 23, 42)      # Slate 900
    TEXT_MAIN = RGBColor(30, 41, 59)        # Slate 800
    TEXT_MUTED = RGBColor(71, 85, 105)      # Slate 600
    PRIMARY_BLUE = RGBColor(27, 54, 93)     # Deep Academic Navy
    ACCENT_BLUE = RGBColor(30, 64, 175)     # Blue 800
    TAG_BG = RGBColor(241, 245, 249)        # Slate 100

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_PAGE
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, section_text="BÁO CÁO ĐỒ ÁN MÔN HỌC: KIỂM THỬ VÀ ĐẢM BẢO CHẤT LƯỢNG PHẦN MỀM"):
        # Section header
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_sec = tf.paragraphs[0]
        p_sec.text = section_text.upper()
        p_sec.font.name = "Times New Roman"
        p_sec.font.size = Pt(11)
        p_sec.font.bold = True
        p_sec.font.color.rgb = ACCENT_BLUE
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Times New Roman"
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = HEADER_NAVY
        p_title.space_before = Pt(3)

    def add_card(slide, left, top, width, height, title="", border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.0)
        
        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Times New Roman"
            p.font.size = Pt(13.5)
            p.font.bold = True
            p.font.color.rgb = PRIMARY_BLUE
        return card

    # =========================================================================
    # SLIDE 1: TRANG TIÊU ĐỀ BÁO CÁO
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1)

    # Khung chính trang bìa
    main_card = add_card(s1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), "", PRIMARY_BLUE)
    
    tbox = s1.shapes.add_textbox(Inches(1.2), Inches(1.1), Inches(10.933), Inches(5.3))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "TRƯỜNG ĐẠI HỌC NÔNG LÂM TP. HỒ CHÍ MINH\nKHOA CÔNG NGHỆ THÔNG TIN"
    p.font.name = "Times New Roman"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.alignment = PP_ALIGN.CENTER
    
    p = tf1.add_paragraph()
    p.text = "BÁO CÁO THI KẾT THÚC HỌC PHẦN: KIỂM THỬ VÀ ĐBCL PHẦN MỀM"
    p.font.name = "Times New Roman"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(14)
    
    p = tf1.add_paragraph()
    p.text = "ĐỀ TÀI: NGHIÊN CỨU KỸ THUẬT AGENTIC TESTOPS\nVÀ ỨNG DỤNG KIỂM THỬ HỆ THỐNG TRUSTBASE"
    p.font.name = "Times New Roman"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = HEADER_NAVY
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(16)
    
    p = tf1.add_paragraph()
    p.text = "Tự động hóa kiểm thử chu trình giao dịch đa phân vai (Buyer -> Seller -> Admin)\nỨng dụng cơ chế sinh kịch bản tự động, tự chữa lành và lưu vết thực thi"
    p.font.name = "Times New Roman"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MUTED
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(12)
    
    p = tf1.add_paragraph()
    p.text = "Giảng viên hướng dẫn: ThS. Lê Phi Hùng\nNhóm thực hiện: Nhóm 05 (Nguyễn Hữu Thắng, Phạm Trần Nhụt Quang, Huỳnh Văn Sĩ)"
    p.font.name = "Times New Roman"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(22)

    # =========================================================================
    # SLIDE 2: THÀNH VIÊN NHÓM VÀ TỰ ĐÁNH GIÁ (THANG ĐIỂM 10)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2)
    add_header(s2, "1. Thành viên nhóm và Bảng tự đánh giá đóng góp", "Phân công trách nhiệm và nghiệm thu công việc")

    members = [
        {
            "name": "Nguyễn Hữu Thắng",
            "mssv": "MSSV: 21130541",
            "role": "Nhóm trưởng / Test Lead",
            "score": "Điểm tự chấm: 10/10",
            "tasks": [
                "Nghiên cứu nguyên lý kỹ thuật Agentic TestOps và giao thức MCP.",
                "Xây dựng MCP Server điều khiển CDP và Playwright Runner.",
                "Lập trình kịch bản E2E kiểm thử chu trình đa phân vai khép kín.",
                "Thiết lập pipeline CI/CD GitHub Actions và xuất bằng chứng tự động.",
                "Chịu trách nhiệm thuyết trình báo cáo và điều phối phần demo."
            ]
        },
        {
            "name": "Phạm Trần Nhụt Quang",
            "mssv": "MSSV: 21130495",
            "role": "QA Engineer / Test Designer",
            "score": "Điểm tự chấm: 9.5/10",
            "tasks": [
                "Thiết kế bộ Test Suite 30 Test Cases chi tiết theo chuẩn IEEE 829.",
                "Áp dụng 4 kỹ thuật kiểm thử hộp đen: EP, BVA, Decision Table, State Transition.",
                "Xây dựng ma trận truy vết yêu cầu phần mềm (RTM).",
                "Soạn thảo tài liệu đặc tả ca kiểm thử và kiểm chứng dữ liệu hạt giống.",
                "Phản biện kỹ thuật và chuẩn bị nội dung câu hỏi vấn đáp."
            ]
        },
        {
            "name": "Huỳnh Văn Sĩ",
            "mssv": "MSSV: 21130528",
            "role": "Automation Engineer / QA Analyst",
            "score": "Điểm tự chấm: 9.5/10",
            "tasks": [
                "Quản lý và biên tập Bảng nhật ký 6 lỗi thực tế (Defect Log).",
                "Thực hiện kiểm thử phi chức năng: Kiểm thử tải và rà soát an toàn bảo mật.",
                "Tổng hợp số liệu Dashboard KPI đo lường chất lượng phần mềm.",
                "Thiết kế tài liệu thuyết trình và đóng gói sản phẩm nghiệm thu.",
                "Cấu hình và duy trì hạ tầng Docker Compose (PostgreSQL, Redis)."
            ]
        }
    ]

    for i, m in enumerate(members):
        left = Inches(0.8 + i * 4.0)
        add_card(s2, left, Inches(1.6), Inches(3.733), Inches(5.3), "", PRIMARY_BLUE)
        
        tb = s2.shapes.add_textbox(left + Inches(0.2), Inches(1.75), Inches(3.333), Inches(5.0))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = m["name"]
        p.font.name = "Times New Roman"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        
        p = tf.add_paragraph()
        p.text = f"{m['mssv']} | {m['role']}"
        p.font.name = "Times New Roman"
        p.font.size = Pt(11)
        p.font.color.rgb = ACCENT_BLUE
        
        p = tf.add_paragraph()
        p.text = f"{m['score']} (Đóng góp 100%)"
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = HEADER_NAVY
        p.space_before = Pt(4)
        
        p = tf.add_paragraph()
        p.text = "Nhiệm vụ và sản phẩm hoàn thành:"
        p.font.name = "Times New Roman"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)
        
        for task in m["tasks"]:
            p = tf.add_paragraph()
            p.text = f"- {task}"
            p.font.name = "Times New Roman"
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_MUTED
            p.space_before = Pt(4)

    # =========================================================================
    # SLIDE 3: HỆ THỐNG MỤC TIÊU TRUSTBASE VÀ BÀI TOÁN KIỂM THỬ
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3)
    add_header(s3, "2. Hệ thống mục tiêu TrustBase và Bài toán kiểm thử", "Bối cảnh ứng dụng và yêu cầu nghiệp vụ thực tế")

    add_card(s3, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Kiến trúc nền tảng TrustBase (SUT)", PRIMARY_BLUE)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    sut_pts = [
        ("Mô hình hoạt động:", "Sàn thương mại điện tử chuyên biệt phân phối License Key, phần mềm bản quyền và thẻ nạp số với cơ chế Ký quỹ trung gian (Digital Key Escrow)."),
        ("Kiến trúc kỹ thuật:", "Hệ thống đa ứng dụng Monorepo gồm Customer Web (cổng 4200), Admin Console (cổng 4203), Backend Fastify API (cổng 4201), PostgreSQL 15 và Redis Cache."),
        ("Quy mô kiểm thử:", "54 bảng cơ sở dữ liệu, 56 seed listings, 5 gian hàng mẫu và tích hợp cổng thanh toán VietQR chuyển khoản tự động.")
    ]
    for i, (k, v) in enumerate(sut_pts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{k} {v}"
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(10)

    add_card(s3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Thách thức của chu trình kiểm thử đa phân vai", PRIMARY_BLUE)
    tb2 = s3.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.6))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0
    
    challenge_pts = [
        ("Vòng đời 3 phân vai:", "Kéo dài liên tục qua Buyer (đặt hàng, ký quỹ Escrow) -> Seller (giao hàng, eKYC, tạo yêu cầu rút tiền Payout) -> Admin (thẩm định và giải ngân chi trả)."),
        ("Hạn chế kiểm thử thủ công:", "Thời gian kiểm thử mỗi vòng lặp tốn 15 đến 20 phút, việc chuyển đổi qua lại giữa 3 phiên đăng nhập dễ phát sinh nhầm lẫn dữ liệu."),
        ("Hạn chế kiểm thử tự động cũ:", "Kịch bản Playwright hoặc Cypress thông thường dễ bị dừng hoạt động khi giao diện thay đổi class, không tự xử lý được các ràng buộc logic ngầm.")
    ]
    for i, (k, v) in enumerate(challenge_pts):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = f"{k} {v}"
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(10)

    # =========================================================================
    # SLIDE 4: CƠ SỞ LÝ THUYẾT: MÔ HÌNH AGENTIC TESTOPS
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4)
    add_header(s4, "3. Cơ sở lý thuyết: Mô hình Agentic TestOps", "So sánh phương pháp luận kiểm thử truyền thống và kiểm thử tự trị")

    # Bảng so sánh 2 cột
    add_card(s4, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Kiểm thử tự động truyền thống (Test Automation)", CARD_BORDER)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    trad = [
        ("Soạn thảo kịch bản:", "Kỹ sư kiểm thử phải tự viết mã kịch bản (.spec.ts) hoàn toàn thủ công."),
        ("Khả năng thích ứng:", "Kịch bản cố định, dễ gãy (flaky) khi frontend thay đổi cấu trúc DOM, ID hoặc selector CSS."),
        ("Xử lý lỗi:", "Chỉ thông báo lỗi assertion failed, không có khả năng phân tích nguyên nhân gốc rễ phía máy chủ."),
        ("Duy trì kịch bản:", "Chi phí bảo trì kiểm thử tăng tuyến tính theo số lượng sprint và tính năng mới.")
    ]
    for i, (k, v) in enumerate(trad):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"- {k} {v}"
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(10)

    add_card(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Mô hình Agentic TestOps (Phương pháp đề xuất)", PRIMARY_BLUE)
    tb = s4.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    agentic = [
        ("Tự động sinh kịch bản:", "Agent tự phân tích giao diện và hợp đồng API để tự viết file kịch bản Playwright chuẩn."),
        ("Cơ chế tự chữa lành (Self-Healing):", "Agent tự định vị lại phần tử khi UI thay đổi và cập nhật lại file kịch bản."),
        ("Điều tra nguyên nhân gốc (RCA):", "Tự động kết hợp kiểm tra trạng thái cơ sở dữ liệu và phản hồi HTTP để xác định nguyên nhân."),
        ("Tối ưu hóa tài nguyên:", "Tự động quản lý phiên làm việc đa phân vai và loại trừ các thao tác lặp lại.")
    ]
    for i, (k, v) in enumerate(agentic):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"- {k} {v}"
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(10)

    # =========================================================================
    # SLIDE 5: KIẾN TRÚC KỸ THUẬT CỦA HỆ THỐNG
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5)
    add_header(s5, "4. Kiến trúc kỹ thuật của hệ thống Agentic TestOps", "Thiết kế phân tầng từ mô hình suy luận đến hạ tầng thực thi")

    layers = [
        ("TẦNG 1: SUY LUẬN VÀ ĐIỀU PHỐI (LLM AGENT REASONING LAYER)",
         "Phân tích yêu cầu kiểm thử, lập kế hoạch thực thi từng phân vai, ra quyết định rẽ nhánh dựa trên phản hồi của hệ thống."),
        ("TẦNG 2: GIAO THỨC BỐI CẢNH VÀ KẾT NỐI (MCP & CDP PROTOCOL LAYER)",
         "Sử dụng Model Context Protocol (MCP) làm cầu nối chuẩn hóa giữa Agent với trình duyệt Chrome qua Chrome DevTools Protocol."),
        ("TẦNG 3: ĐỘNG CƠ KIỂM THỬ VÀ GHI HÌNH (TEST RUNNER & RECORDER LAYER)",
         "Sử dụng Playwright Engine điều khiển hành vi người dùng thật (nhập liệu, click chuột, xử lý popup) và ghi hình thực tế."),
        ("TẦNG 4: HỆ THỐNG ĐƯỢC KIỂM THỬ (APPLICATION UNDER TEST LAYER)",
         "Hệ thống TrustBase triển khai qua Docker: Cổng khách 4200, Cổng quản trị 4203, API 4201, PostgreSQL 5432 và Redis 6379.")
    ]

    for i, (l_title, l_desc) in enumerate(layers):
        top = Inches(1.6 + i * 1.35)
        add_card(s5, Inches(0.8), top, Inches(11.733), Inches(1.2), "", PRIMARY_BLUE)
        tb = s5.shapes.add_textbox(Inches(1.0), top + Inches(0.12), Inches(11.333), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = l_title
        p.font.name = "Times New Roman"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        
        p = tf.add_paragraph()
        p.text = l_desc
        p.font.name = "Times New Roman"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(3)

    # =========================================================================
    # SLIDE 6: THIẾT KẾ TEST SUITE VÀ KỸ THUẬT HỘP ĐEN
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6)
    add_header(s6, "5. Thiết kế Bộ kiểm thử (30 Test Cases) và Kỹ thuật áp dụng", "Áp dụng chuẩn quốc tế ISTQB và tài liệu đặc tả IEEE 829")

    techs = [
        ("Phân Vùng Tương Đương (Equivalence Partitioning)",
         "Phân chia các lớp giá trị hợp lệ và không hợp lệ cho dữ liệu biểu mẫu khách hàng: Kiểm tra danh sách tên miền email cho phép, định dạng số điện thoại chuẩn Việt Nam (10 chữ số) và độ dài họ tên người mua."),
        ("Phân Tích Giá Trị Biên (Boundary Value Analysis)",
         "Xác định và kiểm tra các điểm ranh giới nhạy cảm: Hạn mức rút tiền tối thiểu 50.000 VND, tối đa 50.000.000 VND trên mỗi giao dịch; số lượng mã key số được mua từ 1 key đến mức tồn kho khả dụng."),
        ("Bảng Quyết Định (Decision Table Testing)",
         "Thiết lập bảng kết hợp đa điều kiện đối với chức năng rút tiền người bán: Kiểm tra điều kiện đồng thời gồm Trạng thái KYC gian hàng (Approved/Pending/Rejected), Số dư khả dụng và Tài khoản ngân hàng hợp lệ."),
        ("Chuyển Đổi Trạng Thái (State Transition Testing)",
         "Kiểm thử toàn diện vòng đời đơn hàng ký quỹ và phiếu chi trả: Chuyển đổi trạng thái từ PENDING sang ESCROW_HOLDING, DELIVERED, COMPLETED; hoặc chuyển sang DISPUTED và REFUNDED khi có khiếu nại.")
    ]

    for i, (t_title, t_desc) in enumerate(techs):
        col_left = Inches(0.8) if i in [0, 1] else Inches(6.8)
        col_top = Inches(1.6) if i in [0, 2] else Inches(4.3)
        
        add_card(s6, col_left, col_top, Inches(5.7), Inches(2.5), t_title, PRIMARY_BLUE)
        tb = s6.shapes.add_textbox(col_left + Inches(0.2), col_top + Inches(0.55), Inches(5.3), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = t_desc
        p.font.name = "Times New Roman"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MAIN

    # =========================================================================
    # SLIDE 7: TỰ ĐỘNG HÓA CI/CD VÀ QUẢN LÝ BẰNG CHỨNG KIỂM THỬ
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7)
    add_header(s7, "6. Tự động hóa CI/CD và Quản lý Bằng chứng kiểm thử", "Tích hợp pipeline liên tục và lưu trữ bằng chứng thực nghiệm")

    add_card(s7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Tích hợp CI/CD Pipeline (GitHub Actions)", PRIMARY_BLUE)
    tb = s7.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    cicd = [
        ("Sự kiện kích hoạt:", "Pipeline được kích hoạt tự động khi có Pull Request mới hoặc mã nguồn được đẩy lên nhánh main."),
        ("Dịch vụ phụ trợ:", "Tự động khởi động dịch vụ cơ sở dữ liệu PostgreSQL và Redis thông qua Service Container của GitHub Actions."),
        ("Cài đặt môi trường:", "Thiết lập môi trường Node.js 20, cài đặt trình duyệt Playwright và thư viện FFmpeg phục vụ ghi hình."),
        ("Thực thi kịch bản:", "Triệu gọi kịch bản kiểm thử E2E đa phân vai khép kín trong môi trường headless/xvfb.")
    ]
    for i, (k, v) in enumerate(cicd):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{k} {v}"
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    add_card(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Thu thập và lưu trữ Bằng chứng kiểm thử (Artifacts)", PRIMARY_BLUE)
    tb = s7.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    evidence = [
        ("Ảnh chụp màn hình (Screenshots):", "Ghi lại hình ảnh tại các thời điểm quan trọng (Tạo đơn ký quỹ, Gửi yêu cầu rút tiền, Quản trị duyệt giải ngân) để xem nhanh trên báo cáo."),
        ("Video ghi hình thực tế:", "Quay lại toàn bộ quá trình tương tác thực tế của trình duyệt, chứng minh hệ thống chạy thật trên các cổng dịch vụ 4200 và 4203."),
        ("Lưu vết thực thi (Execution Logs):", "Ghi nhận chi tiết mã trạng thái phản hồi HTTP, truy vấn cơ sở dữ liệu và thời gian phản hồi của từng yêu cầu."),
        ("Cơ chế xuất luôn luôn (if: always):", "Đảm bảo artifacts luôn được đóng gói tải lên hệ thống kể cả khi kịch bản thành công hoặc thất bại.")
    ]
    for i, (k, v) in enumerate(evidence):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{k} {v}"
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 8: KẾT QUẢ THỰC NGHIỆM VÀ PHÂN TÍCH LỖI (DEFECT LOG)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8)
    add_header(s8, "7. Kết quả thực nghiệm và Phân tích lỗi (Defect Log)", "Tổng hợp các lỗi thực tế được phát hiện trên hệ thống TrustBase")

    defects = [
        ("DEF-001 (Nghiêm trọng cao):", "Khóa rút tiền do ràng buộc KYC ngầm: Người bán có số dư khả dụng nhưng nút rút tiền bị vô hiệu hóa do tính năng kyc_gate_payouts kích hoạt khi dữ liệu onboarding_progress chưa phê duyệt."),
        ("DEF-002 (Nghiêm trọng trung bình):", "Biểu mẫu thanh toán từ chối email hợp lệ: Cấu hình danh sách cho phép (domain allowlist) chỉ chấp nhận Gmail, Yahoo, Outlook và từ chối các email có tên miền riêng."),
        ("DEF-003 (Nghiêm trọng cao):", "Lỗi máy chủ nội bộ HTTP 500 khi áp dụng mã giảm giá: Backend phát sinh lỗi ngoại lệ chưa xử lý đối với mã giảm giá đã hết hạn thay vì trả về lỗi nghiệp vụ 400 kèm thông báo."),
        ("DEF-004 (Nghiêm trọng trung bình):", "Xung đột định danh phần tử giao diện Desktop và Mobile: Biểu mẫu render trùng lặp cả input mobile và desktop dẫn đến trường hợp công cụ automation tương tác nhầm phần tử ẩn."),
        ("DEF-005 (Nghiêm trọng trung bình):", "Giao diện quản trị thiếu thông báo trạng thái VietQR: Cổng Admin chưa hiển thị cảnh báo khi tài khoản người bán chưa hoàn tất cấu hình phương thức chi trả VietQR."),
        ("DEF-006 (Nghiêm trọng thấp):", "Thiếu cơ chế tự động hủy đơn hàng ký quỹ quá hạn: Đơn hàng ở trạng thái chờ thanh toán quá 24 giờ không tự động chuyển về trạng thái hủy.")
    ]

    for i, (d_title, d_desc) in enumerate(defects):
        top = Inches(1.6 + (i % 3) * 1.75)
        left = Inches(0.8 if i < 3 else 6.8)
        
        add_card(s8, left, top, Inches(5.7), Inches(1.6), "", PRIMARY_BLUE)
        tb = s8.shapes.add_textbox(left + Inches(0.2), top + Inches(0.12), Inches(5.3), Inches(1.35))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = d_title
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        
        p = tf.add_paragraph()
        p.text = d_desc
        p.font.name = "Times New Roman"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(3)

    # =========================================================================
    # SLIDE 9: KẾ HOẠCH BÁO CÁO VÀ DEMO THỰC TẾ TRONG 10 PHÚT
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9)
    add_header(s9, "8. Kế hoạch Báo cáo và Demo thực tế trong 10 phút", "Phân bổ thời gian chặt chẽ theo hướng dẫn của Giảng viên")

    schedule = [
        ("GIAI ĐOẠN 1: BÁO CÁO NỘI DUNG TỔNG QUAN (00:00 - 02:00 | 2 PHÚT)",
         "Trình bày tóm tắt mục tiêu đề tài, bài toán kiểm thử sàn ký quỹ TrustBase, kiến trúc Agentic TestOps và bảng tự đánh giá thành viên nhóm theo thang điểm 10."),
        ("GIAI ĐOẠN 2: TRÌNH CHIẾU DEMO CHU TRÌNH 3 PHÂN VAI (02:00 - 06:30 | 4.5 PHÚT)",
         "Chiếu video thực tế hoặc chạy kịch bản tự hành: (1) Buyer tạo đơn mua bản quyền số và ký quỹ VietQR; (2) Seller đã eKYC yêu cầu rút tiền; (3) Admin đăng nhập cổng 4203 thẩm định giải ngân."),
        ("GIAI ĐOẠN 3: MINH HỌA FILE TEST TỰ SINH VÀ CI/CD (06:30 - 08:30 | 2 PHÚT)",
         "Trình chiếu file kịch bản Playwright chuẩn do Agent tự sinh ra trong thư mục tests, cấu hình pipeline GitHub Actions và thư mục lưu trữ artifacts."),
        ("GIAI ĐOẠN 4: TRẢ LỜI CÂU HỎI VẤN ĐÁP CỦA GIẢNG VIÊN (08:30 - 10:00 | 1.5 PHÚT)",
         "Giải đáp các câu hỏi chuyên môn của ThS. Lê Phi Hùng về giao thức MCP, kỹ thuật xử lý ranh giới dữ liệu và kết quả thực nghiệm thu được.")
    ]

    for i, (t_time, t_detail) in enumerate(schedule):
        top = Inches(1.6 + i * 1.35)
        add_card(s9, Inches(0.8), top, Inches(11.733), Inches(1.2), "", PRIMARY_BLUE)
        tb = s9.shapes.add_textbox(Inches(1.0), top + Inches(0.12), Inches(11.333), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = t_time
        p.font.name = "Times New Roman"
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        
        p = tf.add_paragraph()
        p.text = t_detail
        p.font.name = "Times New Roman"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(3)

    # =========================================================================
    # SLIDE 10: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN ĐỀ TÀI
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10)
    add_header(s10, "9. Kết luận và Hướng phát triển đề tài", "Tổng kết đóng góp khoa học và lời cảm ơn")

    add_card(s10, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Đóng góp chính của đề tài", PRIMARY_BLUE)
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    concl = [
        "1. Ứng dụng thành công mô hình Agentic TestOps vào hệ thống thực tế TrustBase, chứng minh tính khả thi của việc kết hợp AI Agent với tự động hóa kiểm thử.",
        "2. Giải quyết trọn vẹn bài toán kiểm thử chu trình giao dịch đa phân vai phức tạp (Buyer -> Seller -> Admin) mà kiểm thử truyền thống gặp khó khăn.",
        "3. Xây dựng quy trình tự động hóa CI/CD với khả năng lưu vết bằng chứng thực thi minh bạch gồm ảnh chụp màn hình, video và nhật ký lỗi.",
        "4. Phát hiện 6 lỗi thực tế hỗ trợ nâng cao chất lượng và độ tin cậy cho nền tảng thương mại số TrustBase."
    ]
    for i, c in enumerate(concl):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = c
        p.font.name = "Times New Roman"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    add_card(s10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Định hướng phát triển và Lời cảm ơn", PRIMARY_BLUE)
    tb = s10.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    futs = [
        "Hướng phát triển tiếp theo:",
        "- Tích hợp công cụ MCP với kiểm thử tải k6 và công cụ quét lỗ hổng OWASP ZAP.",
        "- Tự động tạo Issue trên GitHub kèm theo log lỗi và video ghi hình khi phát hiện lỗi.",
        "",
        "Lời cảm ơn:",
        "Nhóm 05 xin trân trọng cảm ơn ThS. Lê Phi Hùng đã tận tình hướng dẫn và đóng góp những ý kiến quý báu cho nhóm trong suốt quá trình thực hiện đồ án môn học Kiểm thử và Đảm bảo Chất lượng Phần mềm.",
        "",
        "Trân trọng cảm ơn Thầy và các bạn đã lắng nghe!"
    ]
    for i, f in enumerate(futs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f
        p.font.name = "Times New Roman"
        p.font.size = Pt(11.5)
        if "Lời cảm ơn:" in f or "Hướng phát triển" in f:
            p.font.bold = True
            p.font.color.rgb = PRIMARY_BLUE
        elif "Trân trọng cảm ơn" in f:
            p.font.bold = True
            p.font.color.rgb = ACCENT_BLUE
        else:
            p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(3)

    prs.save(output_path)
    print(f"Đã tạo bài thuyết trình học thuật chuẩn 10 slides tại: {output_path}")

if __name__ == "__main__":
    out = r"C:\Users\NoNomt007\agentic-test-ops\Nhom05_AgenticTestOps_ThuyetTrinh.pptx"
    build_academic_presentation(out)
