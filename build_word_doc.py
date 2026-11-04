import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="B0C4DE", sz="6", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def add_callout_box(doc, text_list, title="LƯU Ý CỐT LÕI"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="1B365D"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"📌 {title}: ")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(12)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(27, 54, 93)
    
    for idx, t in enumerate(text_list):
        if idx > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
        run_text = p.add_run(t)
        run_text.font.name = "Times New Roman"
        run_text.font.size = Pt(12)
        run_text.font.italic = True
    
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)

def add_toc_line(doc, title, page_num, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.2
    
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.4), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    
    indent = "    " * (level - 1)
    run_title = p.add_run(f"{indent}{title}")
    run_title.font.name = "Times New Roman"
    
    if level == 1:
        run_title.font.size = Pt(12)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(27, 54, 93)
    elif level == 2:
        run_title.font.size = Pt(11.5)
        run_title.font.bold = False
        run_title.font.color.rgb = RGBColor(0, 70, 130)
    else:
        run_title.font.size = Pt(11)
        run_title.font.italic = True
        run_title.font.color.rgb = RGBColor(50, 50, 50)
        
    p.add_run("\t")
    run_page = p.add_run(str(page_num))
    run_page.font.name = "Times New Roman"
    run_page.font.size = Pt(11.5)
    if level == 1:
        run_page.font.bold = True

def add_field(p, field_name):
    run = p.add_run()
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> %s </w:instrText>' % (nsdecls('w'), field_name))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def add_figure(doc, img_path, caption_text, width=Inches(5.8)):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.paragraph_format.keep_with_next = True
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=width)
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        run_cap = p_cap.add_run(caption_text)
        run_cap.font.name = "Times New Roman"
        run_cap.font.size = Pt(10.5)
        run_cap.font.bold = True
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(27, 54, 93)

def create_document():
    doc = Document()
    
    # ----------------- SECTION 1: COVER PAGE -----------------
    sec_cover = doc.sections[0]
    sec_cover.top_margin = Inches(0.9)
    sec_cover.bottom_margin = Inches(0.9)
    sec_cover.left_margin = Inches(1.2)
    sec_cover.right_margin = Inches(0.8)
    sec_cover.different_first_page_header_footer = True
    
    # Configure normal style
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Times New Roman'
    font_normal.size = Pt(13)
    font_normal.color.rgb = RGBColor(33, 37, 41)
    
    # Cover Header
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.paragraph_format.space_before = Pt(0)
    p_header.paragraph_format.space_after = Pt(2)
    r1 = p_header.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO\n")
    r1.font.bold = True
    r1.font.size = Pt(12)
    r2 = p_header.add_run("TRƯỜNG ĐẠI HỌC NÔNG LÂM TP. HỒ CHÍ MINH\n")
    r2.font.bold = True
    r2.font.size = Pt(13)
    r3 = p_header.add_run("KHOA CÔNG NGHỆ THÔNG TIN")
    r3.font.bold = True
    r3.font.size = Pt(13)
    r3.font.color.rgb = RGBColor(27, 54, 93)
    
    # Divider line
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(10)
    r_div = p_div.add_run("-------------------- *** --------------------")
    r_div.font.size = Pt(10)
    r_div.font.color.rgb = RGBColor(100, 100, 100)
    
    # Logo
    logo_path = os.path.abspath("logo_hcmuaf.png")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(2)
        p_logo.paragraph_format.space_after = Pt(12)
        run_logo = p_logo.add_run()
        run_logo.add_picture(logo_path, width=Inches(2.1))
    
    # Report Title
    p_rep_type = doc.add_paragraph()
    p_rep_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep_type.paragraph_format.space_before = Pt(8)
    p_rep_type.paragraph_format.space_after = Pt(4)
    r_rep = p_rep_type.add_run("BÁO CÁO ĐỒ ÁN MÔN HỌC")
    r_rep.font.bold = True
    r_rep.font.size = Pt(17)
    r_rep.font.color.rgb = RGBColor(27, 54, 93)
    
    p_subj = doc.add_paragraph()
    p_subj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subj.paragraph_format.space_after = Pt(14)
    r_subj = p_subj.add_run("MÔN HỌC: KIỂM THỬ VÀ ĐẢM BẢO CHẤT LƯỢNG PHẦN MỀM")
    r_subj.font.bold = True
    r_subj.font.size = Pt(13)
    r_subj.font.color.rgb = RGBColor(0, 90, 156)
    
    # Project Name
    p_topic = doc.add_paragraph()
    p_topic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_topic.paragraph_format.space_before = Pt(8)
    p_topic.paragraph_format.space_after = Pt(6)
    r_top_lbl = p_topic.add_run("ĐỀ TÀI:\n")
    r_top_lbl.font.size = Pt(13)
    r_top_lbl.font.bold = True
    
    r_top_name = p_topic.add_run("HỆ THỐNG TỰ ĐỘNG HÓA KIỂM THỬ WEB APPLICATION TOÀN TRÌNH KẾT HỢP BROWSER TRACE, SOURCE CODE TRACE & VÒNG LẶP TRI THỨC KÉP\n(AGENTIC TESTOPS)")
    r_top_name.font.bold = True
    r_top_name.font.size = Pt(14.5)
    r_top_name.font.color.rgb = RGBColor(180, 40, 40)
    
    p_subname = doc.add_paragraph()
    p_subname.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subname.paragraph_format.space_after = Pt(22)
    r_en = p_subname.add_run("Autonomous Web Testing & Diagnostic Agent via Dual-Trace and Dual-Knowledge Loop")
    r_en.font.italic = True
    r_en.font.size = Pt(11)
    r_en.font.color.rgb = RGBColor(80, 80, 80)
    
    # Members Box (Table)
    tbl_mem = doc.add_table(rows=5, cols=2)
    tbl_mem.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_mem.autofit = False
    set_table_borders(tbl_mem, color="B0C4DE", sz="6")
    
    for r in tbl_mem.rows:
        r.cells[0].width = Inches(2.2)
        r.cells[1].width = Inches(4.3)
        set_cell_margins(r.cells[0], top=70, bottom=70, left=120, right=100)
        set_cell_margins(r.cells[1], top=70, bottom=70, left=100, right=120)
    
    c0 = tbl_mem.cell(0, 0)
    c1 = tbl_mem.cell(0, 1)
    set_cell_background(c0, "F0F4F8")
    set_cell_background(c1, "F0F4F8")
    r_gv_lbl = c0.paragraphs[0].add_run("Giảng viên hướng dẫn:")
    r_gv_lbl.font.bold = True
    r_gv_lbl.font.size = Pt(11.5)
    r_gv_val = c1.paragraphs[0].add_run("Lê Phi Hùng")
    r_gv_val.font.bold = True
    r_gv_val.font.size = Pt(11.5)
    r_gv_val.font.color.rgb = RGBColor(27, 54, 93)
    
    c1_0 = tbl_mem.cell(1, 0)
    c1_1 = tbl_mem.cell(1, 1)
    r_sv1_lbl = c1_0.paragraphs[0].add_run("Sinh viên thực hiện 1:")
    r_sv1_lbl.font.bold = True
    r_sv1_lbl.font.size = Pt(11.5)
    r_sv1_val = c1_1.paragraphs[0].add_run("Họ tên: Nguyễn Hữu Thắng\n- MSSV: 21130535\n- Vai trò: Trưởng nhóm (Kiến trúc Agent & MCP & Canvas Visual)")
    r_sv1_val.font.size = Pt(11)
    
    c2_0 = tbl_mem.cell(2, 0)
    c2_1 = tbl_mem.cell(2, 1)
    r_sv2_lbl = c2_0.paragraphs[0].add_run("Sinh viên thực hiện 2:")
    r_sv2_lbl.font.bold = True
    r_sv2_lbl.font.size = Pt(11.5)
    r_sv2_val = c2_1.paragraphs[0].add_run("Họ tên: Phạm Trần Nhựt Quang\n- MSSV: 22130229\n- Vai trò: Thành viên 1 (Browser & Anti-Flaky)")
    r_sv2_val.font.size = Pt(11)
    
    c3_0 = tbl_mem.cell(3, 0)
    c3_1 = tbl_mem.cell(3, 1)
    r_sv3_lbl = c3_0.paragraphs[0].add_run("Sinh viên thực hiện 3:")
    r_sv3_lbl.font.bold = True
    r_sv3_lbl.font.size = Pt(11.5)
    r_sv3_val = c3_1.paragraphs[0].add_run("Họ tên: Huỳnh Văn Sĩ\n- MSSV: 22130234\n- Vai trò: Thành viên 2 (CDP Debug & Canvas RAG)")
    r_sv3_val.font.size = Pt(11)
    
    c4_0 = tbl_mem.cell(4, 0)
    c4_1 = tbl_mem.cell(4, 1)
    set_cell_background(c4_0, "F8FAFC")
    set_cell_background(c4_1, "F8FAFC")
    r_c4_0 = c4_0.paragraphs[0].add_run("Khoa / Chuyên ngành:")
    r_c4_0.font.bold = True
    r_c4_0.font.size = Pt(11.5)
    r_c4_1 = c4_1.paragraphs[0].add_run("Khoa Công nghệ Thông tin - Đại học Nông Lâm TP.HCM")
    r_c4_1.font.size = Pt(11)
    r_c4_1.font.italic = True
    
    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_foot.paragraph_format.space_before = Pt(38)
    r_foot = p_foot.add_run("TP. HỒ CHÍ MINH, NĂM 2026")
    r_foot.font.bold = True
    r_foot.font.size = Pt(12)
    r_foot.font.color.rgb = RGBColor(60, 60, 60)
    
    # ----------------- SECTION 2: TOC & PREFACES -----------------
    doc.add_page_break()
    sec_body = doc.add_section()
    sec_body.top_margin = Inches(1.0)
    sec_body.bottom_margin = Inches(1.0)
    sec_body.left_margin = Inches(1.2)
    sec_body.right_margin = Inches(0.8)
    
    # Header & Footer setup for body section
    header = sec_body.header
    p_head = header.paragraphs[0]
    p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_h = p_head.add_run("Đồ án môn học: Kiểm thử và Đảm bảo Chất lượng Phần mềm | Agentic TestOps")
    r_h.font.name = "Times New Roman"
    r_h.font.size = Pt(9.5)
    r_h.font.italic = True
    r_h.font.color.rgb = RGBColor(120, 120, 120)
    
    footer = sec_body.footer
    p_foot_sec = footer.paragraphs[0]
    p_foot_sec.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f = p_foot_sec.add_run("Trang ")
    r_f.font.name = "Times New Roman"
    r_f.font.size = Pt(10)
    r_f.font.color.rgb = RGBColor(100, 100, 100)
    add_field(p_foot_sec, "PAGE")
    r_f2 = p_foot_sec.add_run(" / ")
    r_f2.font.name = "Times New Roman"
    r_f2.font.size = Pt(10)
    r_f2.font.color.rgb = RGBColor(100, 100, 100)
    add_field(p_foot_sec, "NUMPAGES")

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(27, 54, 93)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 90, 156)
        return h

    def add_h3(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.italic = True
        r.font.color.rgb = RGBColor(40, 70, 120)
        return h

    def add_p(text, bold_prefix="", italic=False):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.3
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(13)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.italic = italic
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.25
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(13)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        return p

    # ----------------- MỤC LỤC CHÍNH -----------------
    p_toc_title = doc.add_paragraph()
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_title.paragraph_format.space_before = Pt(6)
    p_toc_title.paragraph_format.space_after = Pt(14)
    r_toc_t = p_toc_title.add_run("MỤC LỤC CHI TIẾT")
    r_toc_t.font.name = "Times New Roman"
    r_toc_t.font.size = Pt(16)
    r_toc_t.font.bold = True
    r_toc_t.font.color.rgb = RGBColor(27, 54, 93)

    add_toc_line(doc, "TÓM TẮT ĐỒ ÁN (EXECUTIVE ABSTRACT)", "1", level=1)
    add_toc_line(doc, "PHẦN 1. THỰC TRẠNG KIỂM THỬ PHẦN MỀM & ĐẶT VẤN ĐỀ", "2", level=1)
    add_toc_line(doc, "1.1. Mô hình Kim tự tháp Kiểm thử & Nghịch lý 'Kim tự tháp ngược'", "2", level=2)
    add_toc_line(doc, "1.2. Thảm họa Flaky Tests (Kiểm thử chập chờn) - 'Kẻ thù số 1' của QA", "3", level=2)
    add_toc_line(doc, "1.3. Sự đứt gãy giữa Giao diện (Frontend) và Mã nguồn (Backend)", "4", level=2)
    
    add_toc_line(doc, "PHẦN 2. KHẢO SÁT & SO SÁNH CÁC PHƯƠNG PHÁP KIỂM THỬ HIỆN NAY", "5", level=1)
    add_toc_line(doc, "2.1. Kiểm thử thủ công (Manual Testing)", "5", level=2)
    add_toc_line(doc, "2.2. Kiểm thử tự động bằng Script truyền thống (Selenium, Cypress, Playwright)", "5", level=2)
    add_toc_line(doc, "2.3. Giải pháp Generative AI thế hệ 1 (Prompting & Thiếu Execution Context)", "6", level=2)
    add_toc_line(doc, "2.4. Bảng đối chiếu tổng hợp 4 thế hệ kiểm thử", "6", level=2)
    
    add_toc_line(doc, "PHẦN 3. PHƯƠNG PHÁP ĐỀ XUẤT: HỆ THỐNG AGENTIC TESTOPS", "7", level=1)
    add_toc_line(doc, "3.1. Triết lý Vòng lặp Nhận thức Tự hành SRE (Autonomous SRE Loop)", "7", level=2)
    add_toc_line(doc, "3.2. Đột phá Tracing Kép (Dual-Trace: Playwright Browser + CDP Node Inspect)", "8", level=2)
    add_toc_line(doc, "3.3. Giải pháp Xử lý Dứt điểm Flaky Tests & Tự phục hồi Môi trường", "9", level=2)
    add_toc_line(doc, "3.4. Vòng lặp Tri thức Kép (Dual-Sided Knowledge Loop: RAG + Canvas 5ms)", "11", level=2)
    add_toc_line(doc, "3.5. Đẩy ngược Tri thức: Tự động sản sinh bộ Test Hồi quy (Regression Suite)", "12", level=2)
    add_toc_line(doc, "3.6. Chuẩn hóa Phương pháp Luận Thiết kế Kiểm thử cho Agentic TestOps", "13", level=2)
    
    add_toc_line(doc, "PHẦN 4. KIẾN TRÚC HỆ THỐNG 6 TẦNG TOÀN TRÌNH", "13", level=1)
    add_toc_line(doc, "4.1. Chi tiết 6 tầng công nghệ (6-Tier Zero-Impact Architecture)", "13", level=2)
    add_toc_line(doc, "4.2. Bộ danh mục 9 công cụ giao thức MCP Server (Model Context Protocol)", "14", level=2)
    
    add_toc_line(doc, "PHẦN 5. KỊCH BẢN VẬN HÀNH: QUÉT QUA ĐÊM & TƯƠNG TÁC BAN NGÀY", "15", level=1)
    add_toc_line(doc, "5.1. Kịch bản chính: Autonomous Overnight SRE Sweep (Quét lỗi xuyên đêm)", "15", level=2)
    add_toc_line(doc, "5.2. Các chế độ tương tác ban ngày (Interactive Workflows)", "17", level=2)
    
    add_toc_line(doc, "PHẦN 6. THỰC NGHIỆM ĐÁNH GIÁ & KẾT QUẢ ĐỊNH LƯỢNG", "18", level=1)
    add_toc_line(doc, "6.1. Môi trường thử nghiệm mẫu (Trustbase E-Commerce Platform)", "18", level=2)
    add_toc_line(doc, "6.2. Kết quả thực nghiệm, hình ảnh minh chứng & Bảng đối chiếu định lượng", "18", level=2)
    
    add_toc_line(doc, "PHẦN 7. PHÂN CÔNG NHIỆM VỤ NHÓM 3 THÀNH VIÊN & KẾ HOẠCH", "20", level=1)
    add_toc_line(doc, "7.1. Bảng phân công chi tiết 3 thành viên theo chuyên môn kỹ thuật", "20", level=2)
    add_toc_line(doc, "7.2. Lộ trình triển khai và sản phẩm bàn giao", "21", level=2)
    
    add_toc_line(doc, "PHẦN 8. KẾT LUẬN & HƯỚNG PHÁT TRIỂN", "22", level=1)
    
    # ----------------- DANH MỤC HÌNH VẼ & BẢNG BIỂU -----------------
    p_lof = doc.add_paragraph()
    p_lof.paragraph_format.space_before = Pt(14)
    p_lof.paragraph_format.space_after = Pt(4)
    r_lof = p_lof.add_run("DANH MỤC HÌNH VẼ & SƠ ĐỒ HỆ THỐNG")
    r_lof.font.name = "Times New Roman"
    r_lof.font.size = Pt(13)
    r_lof.font.bold = True
    r_lof.font.color.rgb = RGBColor(27, 54, 93)
    
    add_toc_line(doc, "Hình 1.1: Kim tự tháp kiểm thử chuẩn vs Anti-pattern 'Kim tự tháp ngược'", "2", level=2)
    add_toc_line(doc, "Hình 3.1: Sơ đồ kiến trúc tổng thể & Động cơ Tracing Kép (Model Context Protocol)", "7", level=2)
    add_toc_line(doc, "Hình 3.2: Cơ chế phối hợp giữa Frontend Playwright & Backend CDP Debugger", "9", level=2)
    add_toc_line(doc, "Hình 3.3: Quy trình phân tích sự cố toàn trình (Full-Stack RCA Loop 4 bước)", "10", level=2)
    add_toc_line(doc, "Hình 3.4: Mô hình Vòng lặp Tri thức Kép (AI Memory RAG & Canvas Visual Map)", "11", level=2)
    add_toc_line(doc, "Hình 4.1: Kiến trúc Hệ thống 6 Tầng Toàn Trình (6-Tier Zero-Impact Architecture)", "13", level=2)
    add_toc_line(doc, "Hình 5.1: Sơ đồ Kịch bản chính Autonomous Overnight SRE Sweep (Quét lỗi qua đêm)", "15", level=2)
    add_toc_line(doc, "Hình 5.2: Sơ đồ Phân Luồng Song Song (Parallel Fan-Out / Fan-In) của Bầy Worker Swarm", "16", level=2)
    add_toc_line(doc, "Hình 5.3: Cơ chế Xử lý Kép (Hybrid Ingestion: AST Parser vs LLM) trong Canvas", "17", level=2)
    add_toc_line(doc, "Hình 6.1: Giao diện thực tế đồ thị lỗi tương tác đa cụm trên Canvas Note Engineer", "19", level=2)
    add_toc_line(doc, "Hình 6.2: Bằng chứng kiểm thử tự động tầng giao diện do Playwright chụp lại", "20", level=2)
    
    p_lot = doc.add_paragraph()
    p_lot.paragraph_format.space_before = Pt(10)
    p_lot.paragraph_format.space_after = Pt(4)
    r_lot = p_lot.add_run("DANH MỤC BẢNG BIỂU")
    r_lot.font.name = "Times New Roman"
    r_lot.font.size = Pt(13)
    r_lot.font.bold = True
    r_lot.font.color.rgb = RGBColor(27, 54, 93)
    
    add_toc_line(doc, "Bảng 2.1: Đối chiếu tính năng giữa 4 thế hệ công cụ kiểm thử phần mềm", "6", level=2)
    add_toc_line(doc, "Bảng 4.1: Chi tiết chức năng kỹ thuật của 6 tầng trong kiến trúc Agentic TestOps", "13", level=2)
    add_toc_line(doc, "Bảng 4.2: Danh mục 9 công cụ trong MCP Server (JSON-RPC 2.0 stdio)", "14", level=2)
    add_toc_line(doc, "Bảng 6.1: Kết quả đo đạc thực nghiệm định lượng giữa phương pháp cũ và mới", "18", level=2)
    add_toc_line(doc, "Bảng 7.1: Phân công nhiệm vụ chi tiết và vai trò kỹ thuật của 3 thành viên", "20", level=2)

    doc.add_page_break()

    # ----------------- NỘI DUNG CHI TIẾT -----------------
    
    # ----------------- TÓM TẮT ĐỒ ÁN -----------------
    add_h1("TÓM TẮT ĐỒ ÁN (EXECUTIVE ABSTRACT)")
    add_p(
        "Trong kỹ nghệ phần mềm hiện đại, kiểm thử tự động toàn trình (End-to-End Testing - E2E) đóng vai trò lá chắn sống còn bảo vệ trải nghiệm người dùng cuối. Tuy nhiên, các kỹ sư QA/Dev đang phải đối mặt với hai cuộc khủng hoảng nghiêm trọng: vấn đề kiểm thử chập chờn (Flaky Tests) làm tê liệt đường ống dẫn CI/CD và sự đứt gãy hoàn toàn giữa tầng giao diện (Frontend) với mã nguồn máy chủ (Backend). Khi một kịch bản E2E vấp phải lỗi HTTP 500, các công cụ kiểm thử truyền thống (như Selenium, Cypress, Playwright) chỉ ghi nhận được ảnh chụp màn hình hoặc một thông báo lỗi DOM vô nghĩa, hoàn toàn bất lực trong việc chỉ ra chính xác dòng code backend nào bị sập và trạng thái bộ nhớ RAM lúc văng lỗi là gì."
    )
    add_p(
        "Đồ án môn học 'Kiểm thử và Đảm bảo Chất lượng Phần mềm' của nhóm hiện thực hóa hệ thống Agentic TestOps – một Autonomous Web Testing & Diagnostic Agent tiên tiến, hoạt động độc lập dưới dạng Model Context Protocol (MCP) Server với nguyên lý 100% Zero-Impact. Bằng việc kết hợp Động cơ Tracing Kép (Dual-Trace: Playwright Browser Trace + Node Inspect Chrome DevTools Protocol), hệ thống tự động hóa chu trình khép kín: Quan sát (Observe) -> Suy luận (Reason) -> Thực thi (Act) -> Điều tra (Investigate) -> Kiểm định (Verify) -> Văn bản hóa (Document) -> Ghi nhớ (Remember). Đặc biệt, hệ thống tích hợp sâu cơ chế Anti-Flaky tự giải phóng cổng mạng, cô lập kịch bản ô nhiễm trạng thái và tự động sản sinh bộ bài kiểm thử hồi quy (Regression Tests) để củng cố tầng đáy Kim tự tháp kiểm thử."
    )
    
    add_callout_box(doc, [
        "Mô hình chuyển dịch từ 'Kiểm thử dựa trên Script tĩnh' sang 'Tác tử AI Tự hành SRE' sở hữu giác quan toàn diện.",
        "Đột phá Tracing Kép: Bắt lỗi E2E tại Frontend -> Lần ngược Callstack và đóng băng RAM trên WebSocket CDP (9229) -> Định vị lỗi tận file Backend mà không cần con người can thiệp.",
        "Bộ nhớ tri thức kép: Lưu trữ hồ sơ lỗi Markdown cho AI (RAG) và Bản đồ số Canvas (.canvas.json) trực quan cho kỹ sư duyệt trong 5ms."
    ], title="CÁC ĐÓNG GÓP ĐỘT PHÁ CỦA ĐỒ ÁN")

    # ----------------- PHẦN 1 -----------------
    add_h1("PHẦN 1. THỰC TRẠNG KIỂM THỬ PHẦN MỀM & ĐẶT VẤN ĐỀ")
    
    add_h2("1.1. Mô hình Kim tự tháp Kiểm thử (Test Pyramid) và Nghịch lý 'Kim tự tháp ngược'")
    add_p(
        "Mô hình Kim tự tháp kiểm thử tiêu chuẩn (Test Pyramid) được đề xuất bởi Mike Cohn và phát triển bởi Martin Fowler quy định tỷ trọng lành mạnh của một hệ thống kiểm thử tự động gồm 3 tầng cơ bản: tầng đáy Unit Tests (kiểm thử đơn vị: số lượng nhiều, tốc độ thực thi miligiây, chi phí duy trì rẻ); tầng giữa Service / Integration Tests (kiểm thử tích hợp các module và API); và tầng đỉnh E2E / UI Tests (kiểm thử giao diện toàn trình: số lượng ít, chi phí đắt đỏ và chạy chậm)."
    )
    add_p(
        "Tuy nhiên, trong các dự án phát triển Web thực tế, hầu hết các nhóm phát triển đều rơi vào 'Bẫy Kim tự tháp ngược' hay 'Anti-pattern Que kem' (Testing Ice-Cream Cone / Iceberg):",
        bold_prefix="Nghịch lý thực tế: "
    )
    add_bullet("Thiếu hụt Unit Tests chất lượng: Do áp lực thời gian ra mắt tính năng (Time-to-Market), các lập trình viên thường bỏ qua việc viết kiểm thử đơn vị bao quát các luồng biên.", bold_prefix="1. ")
    add_bullet("Phình to kiểm thử E2E và Thao tác thủ công: Đội ngũ kiểm thử dồn phần lớn nguồn lực vào việc viết hàng trăm kịch bản E2E hoặc bấm tay trên trình duyệt để kiểm tra tính năng.", bold_prefix="2. ")
    add_bullet("Hậu quả nghiêm trọng: Bộ test suite E2E cồng kềnh kéo dài thời gian chạy CI/CD từ vài chục phút lên hàng giờ, chi phí hạ tầng tăng vọt và biến mỗi đợt Release thành một cơn ác mộng.", bold_prefix="3. ")

    # Figure 1.1: Pyramid vs Iceberg
    add_figure(doc, "diagram_images/fig_pyramid.png", "Hình 1.1: Kim tự tháp kiểm thử chuẩn (Mike Cohn) vs Anti-pattern 'Kim tự tháp ngược' (Testing Iceberg)", width=Inches(5.6))

    add_h2("1.2. Thảm họa Flaky Tests (Kiểm thử chập chờn) - 'Kẻ thù số 1' của Kỹ sư QA")
    add_p(
        "Trong kiểm thử tự động toàn trình, 'Flaky Test' được định nghĩa là một bài test có kết quả thực thi bất định (lúc Pass, lúc Fail) dù mã nguồn hệ thống và kịch bản test không hề bị thay đổi. Nghiên cứu thực tế tại Google và Microsoft chỉ ra rằng có tới 16% - 25% các ca kiểm thử E2E trong đường ống CI/CD gặp phải hiện tượng chập chờn này."
    )
    add_p("Bốn nguyên nhân gốc rễ gây ra Flaky Test trong môi trường Web bao gồm:", bold_prefix="Phân tích nguyên nhân: ")
    add_bullet("Bất đồng bộ & Độ trễ hiển thị DOM (Async Timing & Race Conditions): Các phần tử UI tải động qua AJAX, animation CSS chưa hoàn tất hoặc render React/Vue chưa xong nhưng script kiểm thử đã vội vàng click, gây ra lỗi NoSuchElement hoặc ElementNotInteractable.", bold_prefix="a. ")
    add_bullet("Ô nhiễm môi trường & Rò rỉ trạng thái (Shared State & DB Pollution): Một test case phía trước tạo bản ghi trong Database hoặc để lại cookie/session trên trình duyệt nhưng không dọn sạch (teardown), làm hỏng tiền điều kiện của các test case chạy sau.", bold_prefix="b. ")
    add_bullet("Xung đột tiến trình & Treo cổng mạng (Port Conflict - EADDRINUSE): Khi chạy các kịch bản kiểm thử tích hợp, tiến trình Node server từ phiên trước chưa kịp giải phóng cổng (port 3000, 4200, 9229). Phiên kiểm thử tiếp theo khởi động vấp phải ngoại lệ listen EADDRINUSE và văng lỗi sập toàn bộ test suite.", bold_prefix="c. ")
    add_bullet("Thứ tự thực thi phụ thuộc (Test Order Dependency): Khi các test suite chạy song song (Parallel execution) để tối ưu thời gian, các tài nguyên chia sẻ bị tranh chấp dẫn đến tỷ lệ fail ngẫu nhiên.", bold_prefix="d. ")
    
    add_p(
        "Hậu quả của Flaky Test là cực kỳ tai hại: nó tạo ra hiện tượng 'Mệt mỏi cảnh báo' (Alert Fatigue). Lập trình viên dần mất lòng tin vào bộ kiểm thử tự động, hình thành thói quen nguy hiểm: 'Thấy test đỏ cứ bấm rerun lại cho xanh', từ đó bỏ lọt các bug logic nghiêm trọng vào môi trường Production.",
        bold_prefix="Tác hại bào mòn niềm tin: "
    )

    add_h2("1.3. Sự đứt gãy giữa Giao diện (Frontend) và Mã nguồn (Backend)")
    add_p(
        "Một rào cản chí mạng khác trong các công cụ E2E hiện đại (Cypress, Selenium, Playwright thuần): chúng hoạt động theo mô hình 'Hộp đen' (Black-box Testing). Công cụ chỉ đứng bên ngoài trình duyệt để click và assert kết quả hiển thị trên màn hình. Khi một tương tác người dùng kích hoạt API văng lỗi HTTP 500 (Internal Server Error) hoặc văng Uncaught Exception, công cụ E2E chỉ có thể chụp lại một bức ảnh màn hình hiển thị Toast thông báo lỗi chung chung và in ra dòng console 500 đỏ chót. Kỹ sư kiểm thử không thể nào biết được:"
    )
    add_bullet("Dòng lệnh nào trong file controller/service/repository ở backend vừa bị lỗi?", bold_prefix="• ")
    add_bullet("Các biến số trên bộ nhớ RAM (Heap) tại thời khắc văng exception mang giá trị gì (ví dụ: null, undefined, NaN, hay chuỗi rỗng)?", bold_prefix="• ")
    add_bullet("Callstack sâu bên trong luồng xử lý nghiệp vụ dẫn đến sự cố bắt nguồn từ đâu?", bold_prefix="• ")
    add_p("Hậu quả là kỹ sư vẫn phải lục lọi hàng ngàn dòng file log máy chủ bằng mắt, mở IDE, đặt breakpoint thủ công để tái hiện lại lỗi, tiêu tốn trung bình từ 2 đến 6 giờ cho mỗi sự cố.")

    # ----------------- PHẦN 2 -----------------
    add_h1("PHẦN 2. KHẢO SÁT & SO SÁNH CÁC PHƯƠNG PHÁP KIỂM THỬ HIỆN NAY")
    add_p(
        "Để làm rõ sự cần thiết và tính ưu việt của đề tài, nhóm tiến hành khảo sát và đối chiếu 4 thế hệ giải pháp kiểm thử phần mềm đang tồn tại trên thị trường:"
    )
    
    # Table Comparison
    p_tbl1_cap = doc.add_paragraph()
    p_tbl1_cap.paragraph_format.space_before = Pt(4)
    p_tbl1_cap.paragraph_format.space_after = Pt(2)
    r_cap1 = p_tbl1_cap.add_run("Bảng 2.1: Đối chiếu tính năng giữa 4 thế hệ công cụ kiểm thử phần mềm")
    r_cap1.font.bold = True
    r_cap1.font.size = Pt(11)
    r_cap1.font.color.rgb = RGBColor(27, 54, 93)

    tbl_comp = doc.add_table(rows=6, cols=5)
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_comp.autofit = False
    set_table_borders(tbl_comp, color="B0C4DE", sz="6")
    
    headers = ["Tiêu chí đánh giá", "Kiểm thử thủ công (Manual QA)", "Script viết tay (Playwright/Cypress)", "GenAI thế hệ 1 (Prompting/GPT-4)", "Agentic TestOps (Đề xuất)"]
    col_widths = [Inches(1.4), Inches(1.3), Inches(1.4), Inches(1.4), Inches(1.8)]
    
    hdr_cells = tbl_comp.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].width = col_widths[i]
        set_cell_background(hdr_cells[i], "1B365D")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=80, right=80)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.font.bold = True
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(255, 255, 255)
    
    data_rows = [
        ("Thiết kế kịch bản & Sinh Test", "Con người tự click & viết Test Case Excel", "Kỹ sư phải code từng dòng lệnh selector", "Sinh kịch bản từ text nhưng không thể chạy", "AI tự lập kế hoạch, tự khám phá và tự sinh test"),
        ("Khả năng định vị lỗi (RCA)", "Không thể; chỉ báo lỗi nhìn thấy bằng mắt", "Chỉ chụp ảnh UI + mã HTTP 500 vô nghĩa", "Chỉ đọc log thô và phỏng đoán (Dễ ảo giác)", "Soi trực tiếp biến trên RAM và Callstack qua CDP"),
        ("Xử lý Flaky Tests & Môi trường", "Phụ thuộc hoàn toàn vào thao tác người", "Dễ vỡ do delay DOM, kẹt cổng EADDRINUSE", "Hoàn toàn không có năng lực can thiệp môi trường", "Auto-waiting, cô lập test polluter, tự diệt port zombie"),
        ("Bảo lưu tri thức sau kiểm thử", "Báo cáo Word/Jira rời rạc, trôi theo thời gian", "Báo cáo HTML chỉ dùng 1 lần rồi xóa", "Lưu text chat không có cấu trúc chuẩn", "Tri thức kép: RAG Docs (.md) + Sơ đồ Canvas 5ms"),
        ("Tự phục hồi & Test Hồi quy", "Thủ công hoàn toàn, tốn nhân lực lặp lại", "Phải tự viết thêm bài kiểm thử hồi quy mới", "Không thể tự đóng gói vào luồng CI/CD", "Tự động sinh Regression Suite (Vitest/Playwright)")
    ]
    
    for row_idx, data in enumerate(data_rows, start=1):
        row_cells = tbl_comp.rows[row_idx].cells
        bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            row_cells[col_idx].width = col_widths[col_idx]
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=80, bottom=80, left=80, right=80)
            p = row_cells[col_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx > 0 else WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(text)
            run.font.size = Pt(10.5)
            if col_idx == 4:
                run.font.bold = True
                run.font.color.rgb = RGBColor(27, 54, 93)
            elif col_idx == 0:
                run.font.bold = True
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    add_p(
        "Nhận xét: Các công cụ kiểm thử hiện tại đều bộc lộ giới hạn nghiêm trọng giữa việc thực thi và chuẩn đoán. Thế hệ GenAI đầu tiên tuy có khả năng hiểu ngôn ngữ tự nhiên nhưng lại thiếu trầm trọng Ngữ cảnh Thực thi (Execution Context) và Giác quan Tương tác Máy chủ. Đây chính là khoảng trống công nghệ mà hệ thống Agentic TestOps của đề tài hướng tới giải quyết triệt để.",
        bold_prefix="Đánh giá tổng quát: "
    )

    # ----------------- PHẦN 3 -----------------
    add_h1("PHẦN 3. PHƯƠNG PHÁP ĐỀ XUẤT: HỆ THỐNG AGENTIC TESTOPS")
    
    add_h2("3.1. Triết lý Vòng lặp Nhận thức Tự hành SRE (Autonomous SRE Loop)")
    add_p(
        "Đề tài từ bỏ cách tiếp cận truyền thống vốn biến AI thành một chatbot hỏi-đáp thụ động. Thay vào đó, Agent được mô hình hóa thành một Kỹ sư Kiểm thử & Độ tin cậy Hệ thống (Site Reliability Engineer - SRE) độc lập sở hữu đầy đủ giác quan và công cụ can thiệp. Vòng lặp nhận thức được chuẩn hóa thành 7 bước chặt chẽ:"
    )
    add_callout_box(doc, [
        "1. Observe (Quan sát): Theo dõi hành vi ứng dụng qua luồng mạng HTTP, DOM tree, console logs và trạng thái cổng hệ thống.",
        "2. Reason (Suy luận): Phân rã mục tiêu nghiệp vụ, phân tích kịch bản biên (edge cases) và lập kế hoạch hành động.",
        "3. Act (Thực thi): Điều khiển Playwright tương tác với các nút bấm, biểu mẫu, xử lý luồng nghiệp vụ phức tạp.",
        "4. Investigate (Điều tra): Khi phát hiện sự cố, tự động gắn kết nối WebSocket CDP vào tiến trình backend để thanh tra bộ nhớ RAM.",
        "5. Verify (Kiểm định): Thực thi kiểm chứng cô lập để xác nhận giả thuyết nguyên nhân gốc rễ (Root Cause Hypothesis).",
        "6. Document (Văn bản hóa): Xuất báo cáo sự cố toàn trình ra định dạng RAG Markdown và Sơ đồ đồ thị Canvas Node.",
        "7. Remember (Ghi nhớ): Nạp tri thức sự cố vào bộ nhớ dài hạn nhằm ngăn ngừa lặp lại sai lầm trong các phiên quét tương lai."
    ], title="CHU TRÌNH 7 BƯỚC NHẬN THỨC SRE")

    # Figure 3.1: Overall Arch & Dual Tracing
    add_figure(doc, "diagram_images/readme_diag_1.png", "Hình 3.1: Sơ đồ kiến trúc tổng thể & Động cơ Tracing Kép (Model Context Protocol, Playwright + Node Inspect, RAG + Canvas Note Engineer)", width=Inches(5.8))

    add_h2("3.2. Đột phá Tracing Kép (Dual-Trace Architecture)")
    add_p(
        "Trái tim của hệ thống là cơ chế phối hợp bất đồng bộ nhịp nhàng giữa hai động cơ trinh sát:",
        bold_prefix="Cơ chế phối hợp: "
    )
    add_bullet("Động cơ Tầng Giao diện (Playwright Browser Trace): Khởi chạy trình duyệt Chromium, giám sát chặt chẽ các sự kiện DOM, bắt toàn bộ các gói tin HTTP có mã phản hồi 4xx/5xx, lắng nghe ngoại lệ unhandledrejection, và tự động chụp ảnh màn hình lưu vào screenshots/ làm chứng cứ nghiệm thu.", bold_prefix="• Tầng Frontend: ")
    add_bullet("Động cơ Tầng Mã nguồn (Node Inspect & CDP Debugger): Khởi động server với cờ NODE_OPTIONS=--inspect=0.0.0.0:9229. Khi Playwright phát hiện lỗi HTTP 500, Agent lập tức phát lệnh qua WebSocket debugger. CDP tự động kích hoạt tính năng pauseOnExceptions, đóng băng tiến trình Node ngay tại mili-giây văng lỗi, trích xuất toàn bộ Callstack và soi trực tiếp giá trị biến trên Heap mà không cần lập trình viên can thiệp.", bold_prefix="• Tầng Backend: ")

    # Figure 3.2: Frontend Playwright & Backend CDP
    add_figure(doc, "diagram_images/readme_diag_4.png", "Hình 3.2: Cơ chế phối hợp giữa Frontend Playwright & Backend CDP Debugger", width=Inches(5.6))

    add_h2("3.3. Giải pháp Xử lý Dứt điểm Vấn đề Flaky Tests & Tự phục hồi Môi trường")
    add_p(
        "Nhằm giải quyết triệt để vấn đề kiểm thử chập chờn (Flaky) đã phân tích ở Phần 1, hệ thống tích hợp sẵn 4 cơ chế bảo vệ nòng cốt:"
    )
    add_bullet("Auto-waiting Thông minh của Playwright: Triệt tiêu hoàn toàn các lệnh chờ cưỡng bức (như sleep 5000ms). Playwright tự động chờ đợi các điều kiện hiển thị tự nhiên của DOM (Actionability checks: visible, stable, enabled, editable) trước khi click hoặc nhập liệu, giúp loại bỏ 90% lỗi Flaky do bất đồng bộ UI.", bold_prefix="1. ")
    add_bullet("Quản trị Cổng Tự động (Port Zombie Killer): Công cụ debug_kill_ports liên tục quét các cổng ứng dụng (3000, 4200) và cổng inspect (9229). Bất kỳ tiến trình zombie nào còn sót lại từ các phiên chạy trước sẽ bị force-kill tức thì, loại trừ hoàn toàn lỗi kẹt cổng EADDRINUSE làm gián đoạn kiểm thử.", bold_prefix="2. ")
    add_bullet("Cô lập Kịch bản Gây Ô nhiễm (Test Polluter Isolation - find-polluter): Script phân tích nhị phân (Bisect) tự động chạy cô lập các test case để truy tìm chính xác kịch bản nào làm thay đổi trạng thái cơ sở dữ liệu chung hoặc rò rỉ bộ nhớ, từ đó tự động cách ly test case đó vào vùng kiểm dịch (Quarantine).", bold_prefix="3. ")
    add_bullet("Chẩn đoán Phân biệt Flaky vs Lỗi Logic thực thụ qua Snapshot RAM: Khi một bài test bị fail, Agent không vội kết luận bug ngay. Agent so sánh snapshot biến RAM thu thập từ CDP với lịch sử chạy trước. Nếu biến số nghiệp vụ (ví dụ sellerRank = null) xuất hiện nhất quán trong Callstack backend, hệ thống xác nhận đây là Lỗi Logic Nghiệp Vụ; ngược lại nếu biến số hợp lệ nhưng DOM timeout, hệ thống đánh dấu Flaky do mạng và tiến hành Retry có ngữ cảnh.", bold_prefix="4. ")

    # Figure 3.3: RCA Loop
    add_figure(doc, "diagram_images/readme_diag_5.png", "Hình 3.3: Quy trình phân tích sự cố toàn trình (Full-Stack RCA Loop 4 bước: Detect -> Attach CDP -> Snapshot RAM -> Pinpoint Code)", width=Inches(5.8))

    add_h2("3.4. Vòng lặp Tri thức Kép (Dual-Sided Knowledge Loop)")
    add_p(
        "Sau khi hoàn tất quá trình điều tra, dữ liệu sự cố được đồng bộ hóa thành hai định dạng bổ trợ cho nhau:"
    )
    add_bullet("Tri thức cho Trí tuệ Nhân tạo (RAG Document .md): Lưu trữ tại thư mục knowledge/ dưới dạng cấu trúc Markdown chuẩn hóa (Defect Dossier), bao gồm mã sự cố, triệu chứng, mã HTTP, dòng code vi phạm và giá trị biến trên RAM. Agent sẽ tự động truy vấn (RAG) lại các file này trước mỗi phiên kiểm thử mới để sinh các kịch bản kiểm tra biên có tính mục tiêu cao.", bold_prefix="• Nhánh 1: ")
    add_bullet("Bản đồ Đồ thị cho Lập trình viên (Canvas Visual Map .canvas.json): Hệ thống tích hợp với công cụ Canvas Note Engineer. Điểm đột phá kỹ thuật ở đây là cơ chế Hybrid Ingestion: File .canvas.json được xử lý bởi Local AST Parser ngoại tuyến (Offline), hiển thị đồ thị mạng lưới lỗi đa cụm (Đỏ = Lỗi, Vàng = Nguyên nhân gốc rễ, Xanh = Đã khắc phục) chỉ trong 5ms với 0 Tokens tiêu tốn, giúp lập trình viên thẩm định sự cố tức thì.", bold_prefix="• Nhánh 2: ")

    # Figure 3.4: Dual Knowledge
    add_figure(doc, "diagram_images/readme_diag_6.png", "Hình 3.4: Mô hình Vòng lặp Tri thức Kép (AI Memory RAG & Canvas Visual Map)", width=Inches(5.6))

    add_h2("3.5. Đẩy ngược Tri thức: Tự động Sản sinh Bộ Test Hồi quy (Regression Test Suite)")
    add_p(
        "Để tái thiết lập tỷ trọng lành mạnh cho Kim tự tháp kiểm thử, Agentic TestOps không dừng lại ở việc báo cáo lỗi E2E. Từ Callstack và giá trị biến lỗi bóc tách được ở Tầng 2, Tầng 6 của hệ thống tự động tổng hợp một file bài kiểm thử hồi quy độc lập (dưới dạng Vitest hoặc Playwright Suite). Bài test này cô lập đúng hàm nghiệp vụ bị lỗi, gán các giá trị tham số biên gây crash để kiểm chứng, và cắm trực tiếp vào CI/CD Pipeline. Điều này giúp đẩy ngược bài học từ đỉnh E2E xuống tầng Unit/Integration, bảo đảm lỗi cũ không bao giờ tái phát."
    )

    add_h2("3.6. Chuẩn Hóa Phương Pháp Luận Thiết Kế Kiểm Thử Cho Agentic TestOps")
    add_p(
        "Khác biệt căn bản giữa Agentic TestOps và các công cụ sinh test bằng AI thông thường là hệ thống không sinh kịch bản một cách tùy hứng, mà tuân thủ chặt chẽ các kỹ thuật thiết kế kiểm thử phần mềm chính quy:"
    )
    add_bullet("Kỹ thuật Phân tích giá trị biên (BVA): Agent áp dụng phân tầng 3 cấp độ biên. Cấp 1 là Standard BVA (4n+1 ca kiểm thử) với 5 giá trị {min, min+, nom, max-, max} cho các trường nhập liệu thông thường; Cấp 2 là Robustness Testing (6n+1 ca kiểm thử) bổ sung 2 giá trị ngoại lệ ngoài biên (min- và max+) để kiểm chứng khả năng xử lý ngoại lệ (Exception Handling); Cấp 3 là Worst-case Testing (5^n ca kiểm thử) theo giả định đa lỗi (Multiple-fault assumption) dành riêng cho các module tài chính và ký quỹ có rủi ro cao.", bold_prefix="1. ")
    add_bullet("Kỹ thuật Phân vùng tương đương (Equivalence Partitioning): Hệ thống triển khai nguyên tắc Weak Robust EP dựa trên giả định đơn lỗi (Single-fault assumption). Trong mỗi ca kiểm thử, chỉ cho phép duy nhất một biến đầu vào nhận giá trị không hợp lệ (Invalid), trong khi toàn bộ các biến còn lại phải giữ giá trị hợp lệ. Quy tắc này triệt tiêu hoàn toàn hiện tượng che giấu lỗi (Fault Masking) - nguyên nhân hàng đầu khiến các bộ test tự động bỏ sót lỗi logic.", bold_prefix="2. ")
    add_bullet("Kỹ thuật Bảng quyết định (Decision Table): Đối với các luồng nghiệp vụ đa điều kiện (như luồng Checkout kết hợp giữa Hạng thành viên, Mã giảm giá, Số dư ví và Địa chỉ giao hàng), Agent tự động lập ma trận kết hợp điều kiện và hành động, giúp loại trừ các tổ hợp dư thừa và bảo đảm độ bao phủ toàn diện 100% các quy tắc nghiệp vụ.", bold_prefix="3. ")
    add_bullet("Kiểm thử Chuyển đổi trạng thái (State Transition Testing): Mô hình hóa hành vi hệ thống thành máy trạng thái hữu hạn (FSM). Agent tự động xác minh không chỉ các bước chuyển hợp lệ (Valid Transitions) mà còn chủ động kích hoạt các chuyển đổi phi lý (Invalid Transitions) - ví dụ gửi yêu cầu giải ngân hoa hồng khi đơn hàng đang ở trạng thái Tranh chấp (Dispute) - để kiểm tra tính toàn vẹn của nghiệp vụ.", bold_prefix="4. ")
    add_bullet("Chuỗi Lỗi và Vòng đời Lỗi (Defect Workflow) chuẩn ISO/IEEE: Hệ thống phân định rạch ròi 4 cấp độ: Error (hành vi thiếu sót của lập trình viên) -> Fault/Defect (khiếm khuyết mã nguồn do CDP phát hiện) -> Failure (sự cố HTTP 500 do Playwright ghi nhận) -> Incident (phiếu sự cố được gắn thẻ trên Canvas Node theo vòng đời New -> Open -> Investigating -> Fixed -> Re-test).", bold_prefix="5. ")

    # ----------------- PHẦN 4 -----------------
    add_h1("PHẦN 4. KIẾN TRÚC HỆ THỐNG 6 TẦNG TOÀN TRÌNH")
    add_p(
        "Hệ thống được thiết kế theo kiến trúc 6 tầng kỹ thuật độc lập (6-Tier Zero-Impact Architecture), bảo đảm có thể cắm vào bất kỳ dự án Web nào mà không làm thay đổi mã nguồn mục tiêu:"
    )
    
    # Figure 4.1: 6 Tiers
    add_figure(doc, "diagram_images/fig_6tiers.png", "Hình 4.1: Kiến trúc Hệ thống 6 Tầng Toàn Trình (6-Tier Zero-Impact Architecture)", width=Inches(5.6))

    p_tbl2_cap = doc.add_paragraph()
    p_tbl2_cap.paragraph_format.space_before = Pt(4)
    p_tbl2_cap.paragraph_format.space_after = Pt(2)
    r_cap2 = p_tbl2_cap.add_run("Bảng 4.1: Chi tiết chức năng kỹ thuật của 6 tầng trong kiến trúc Agentic TestOps")
    r_cap2.font.bold = True
    r_cap2.font.size = Pt(11)
    r_cap2.font.color.rgb = RGBColor(27, 54, 93)

    tiers_info = [
        ("Tầng 6: Tự Động Sinh Regression Test", "Vitest / Playwright Suite", "Tự động đóng gói Unit/Integration Test cô lập dựa trên Callstack bắt từ CDP, đạt chuẩn Phủ cấp 1 (Statement Coverage) & Phủ cấp 2 (Branch Coverage), đo lường độ phức tạp chu trình McCabe V(G) = P + 1 và làm lá chắn CI/CD Gate ngăn ngừa tái phát."),
        ("Tầng 5: Canvas Visual Map (Giao diện Kỹ sư)", "Canvas Note Engineer", "Hiển thị đồ thị vô cực các Pod lỗi (Pass, Fail, Bug, Trace, Regression), nạp qua Local AST Parser trong 5ms."),
        ("Tầng 4: RAG Knowledge Memory (Bộ nhớ AI)", "Markdown Defect Dossier", "Bộ nhớ ngữ nghĩa dài hạn, lưu vết sự cố có cấu trúc giúp Agent học hỏi qua từng phiên kiểm thử, triệt tiêu ảo giác."),
        ("Tầng 3: Root Cause Analysis (Động cơ RCA)", "RCA 4-Step Loop", "Quy trình chẩn đoán 4 bước: Phát hiện -> Gắn kết CDP -> Bóc tách biến trên RAM -> Định vị dòng code vi phạm."),
        ("Tầng 2: Source Code Trace & Debug Session", "Node Inspect (--inspect=9229)", "Kết nối WebSocket CDP, thanh tra Heap memory, tích hợp Zombie Port Killer dập tắt triệt để lỗi EADDRINUSE."),
        ("Tầng 1: Browser Automation & Smart Trace", "Playwright Chromium Engine", "Điều khiển trình duyệt, tự động bắt sự kiện Console, HTTP 4xx/5xx, auto-waiting thông minh chống Flaky.")
    ]
    
    tbl_tier = doc.add_table(rows=7, cols=3)
    tbl_tier.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_tier.autofit = False
    set_table_borders(tbl_tier, color="B0C4DE", sz="6")
    
    tier_widths = [Inches(2.4), Inches(1.8), Inches(3.1)]
    thd = tbl_tier.rows[0].cells
    t_titles = ["Tầng Kiến Trúc", "Công Nghệ / Module", "Chức Năng Kỹ Thuật Chính"]
    for i, t in enumerate(t_titles):
        thd[i].width = tier_widths[i]
        set_cell_background(thd[i], "1B365D")
        set_cell_margins(thd[i], top=90, bottom=90, left=80, right=80)
        p = thd[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(t)
        run.font.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(255, 255, 255)
        
    for idx, (t_name, t_tech, t_desc) in enumerate(tiers_info, start=1):
        cells = tbl_tier.rows[idx].cells
        bg_col = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate([t_name, t_tech, t_desc]):
            cells[c_idx].width = tier_widths[c_idx]
            set_cell_background(cells[c_idx], bg_col)
            set_cell_margins(cells[c_idx], top=70, bottom=70, left=80, right=80)
            p = cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.size = Pt(10.5)
            if c_idx == 0:
                run.font.bold = True
                run.font.color.rgb = RGBColor(27, 54, 93)
            elif c_idx == 1:
                run.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_h2("4.1. Bộ Danh Mục 9 Công Cụ Giao Thức MCP Server")
    add_p(
        "Toàn bộ sức mạnh của hệ thống được đóng gói thành một Model Context Protocol (MCP) Server độc lập giao tiếp qua chuẩn JSON-RPC 2.0 stdio, cho phép bất kỳ Agent nào (Claude Code, Antigravity, Gemini CLI) kích hoạt tức thì:"
    )
    
    p_tbl3_cap = doc.add_paragraph()
    p_tbl3_cap.paragraph_format.space_before = Pt(4)
    p_tbl3_cap.paragraph_format.space_after = Pt(2)
    r_cap3 = p_tbl3_cap.add_run("Bảng 4.2: Danh mục 9 công cụ trong MCP Server (JSON-RPC 2.0 stdio)")
    r_cap3.font.bold = True
    r_cap3.font.size = Pt(11)
    r_cap3.font.color.rgb = RGBColor(27, 54, 93)

    tbl_mcp = doc.add_table(rows=10, cols=3)
    tbl_mcp.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_mcp.autofit = False
    set_table_borders(tbl_mcp, color="B0C4DE", sz="6")
    
    mcp_widths = [Inches(2.2), Inches(2.3), Inches(2.8)]
    mcp_hdrs = ["Tên Công Cụ (Tool)", "Tham Số Đầu Vào", "Chức Năng Kỹ Thuật"]
    for i, t in enumerate(mcp_hdrs):
        tbl_mcp.rows[0].cells[i].width = mcp_widths[i]
        set_cell_background(tbl_mcp.rows[0].cells[i], "1B365D")
        set_cell_margins(tbl_mcp.rows[0].cells[i], top=90, bottom=90, left=60, right=60)
        p = tbl_mcp.rows[0].cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(t)
        run.font.bold = True
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(255, 255, 255)
        
    mcp_tools = [
        ("debug_inspect_cdp", "inspectPort, pauseOnExceptions, expressions[]", "Client gỡ lỗi WebSocket CDP: Đóng băng tiến trình, trích xuất Callstack và đọc biến RAM heap."),
        ("debug_export_overnight_report", "sweepId, date, flows[]", "Báo cáo kiểm thử quét qua đêm: Tổng hợp kết quả các flow, xuất cặp file OVERNIGHT-SWEEP.md và .canvas.json đa cụm."),
        ("debug_export_rag_report", "testId, title, route, symptoms, sourceLocation", "Tự động xuất cặp file tri thức sự cố đơn luồng: .md cho RAG và .canvas.json 3 Sub-Clusters cho Canvas."),
        ("debug_browser_run", "url, actions[], headless, timeoutMs", "Điều khiển Playwright Chromium, tự động hóa thao tác người dùng, lắng nghe Console và bắt HTTP 4xx/5xx."),
        ("debug_status", "ports[] (Mặc định quét 9 cổng)", "Quét trạng thái cổng ứng dụng (3000, 4200) và cổng inspect (9229...), trả về PID tiến trình."),
        ("debug_kill_ports", "ports[] ([9229, 9230...])", "Force-kill tiến trình zombie chiếm dụng cổng, dập tắt dứt điểm lỗi EADDRINUSE."),
        ("debug_start_server", "command, inspectPort, app, cwd", "Khởi chạy dev server ở chế độ --inspect=0.0.0.0:<port> chạy ngầm, tự động dọn sạch port trước khi bật."),
        ("debug_stop_server", "app, pid", "Dừng tiến trình dev server an toàn và giải phóng tài nguyên hệ thống."),
        ("debug_run_test", "command, cwd, timeoutMs", "Chạy test đơn lẻ trong môi trường cô lập, bóc tách Callstack và mã thoát lỗi.")
    ]
    
    for idx, (tname, tparam, tdesc) in enumerate(mcp_tools, start=1):
        cells = tbl_mcp.rows[idx].cells
        bg_col = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate([tname, tparam, tdesc]):
            cells[c_idx].width = mcp_widths[c_idx]
            set_cell_background(cells[c_idx], bg_col)
            set_cell_margins(cells[c_idx], top=60, bottom=60, left=60, right=60)
            p = cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.size = Pt(10)
            if c_idx == 0:
                run.font.bold = True
                run.font.color.rgb = RGBColor(27, 54, 93)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ----------------- PHẦN 5 -----------------
    add_h1("PHẦN 5. KỊCH BẢN VẬN HÀNH: QUÉT QUA ĐÊM & TƯƠNG TÁC BAN NGÀY")
    
    add_h2("5.1. Kịch bản Chính: Autonomous Overnight SRE Sweep (Quét Lỗi Xuyên Đêm)")
    add_p(
        "Kịch bản cốt lõi giải phóng 100% sức lao động của kỹ sư: Trước khi rời bàn làm việc lúc 23:00, kỹ sư chỉ cần ra lệnh: /debug overnight. Agent sẽ vận hành hoàn toàn tự động xuyên suốt ban đêm theo mô hình Bầy Subagents Song Song (Parallel Worker Swarm):"
    )
    add_bullet("Mô hình Fan-Out / Fan-In: Orchestrator Agent phân rã 6 flow nghiệp vụ trọng yếu (Auth, Catalog, Cart, Checkout, Payout, Dispute) cho 3 Workers chạy song song trên các Browser Context độc lập (worker-1, worker-2, worker-3).", bold_prefix="• ")
    add_bullet("Tăng tốc 300% - 500%: Thời gian thực thi toàn bộ 6 flows giảm từ 45 phút xuống chỉ còn 12 - 15 phút.", bold_prefix="• ")
    add_bullet("Không bao giờ bị nghẽn (Non-blocking Incident Triage): Khi Worker 2 vấp phải lỗi HTTP 500 tại Checkout, cdp-investigator âm thầm kích hoạt CDP đóng băng RAM và phân tích lỗi trong nền, trong khi Worker 1 và Worker 3 vẫn tiếp tục kiểm thử bình thường.", bold_prefix="• ")
    add_bullet("Thành quả sáng hôm sau (07:00): Kỹ sư thức dậy mở Canvas Note Engineer, toàn bộ bản đồ lỗi đa cụm cùng ma trận sức khỏe hệ thống (Health Matrix) đã sẵn sàng để thẩm định.", bold_prefix="• ")

    # Figure 5.1: Overnight Sweep
    add_figure(doc, "diagram_images/readme_diag_2.png", "Hình 5.1: Sơ đồ Kịch bản chính Autonomous Overnight SRE Sweep (Quét lỗi qua đêm 100% tự động)", width=Inches(5.6))

    # Figure 5.2: Fan-out / Fan-in Swarm
    add_figure(doc, "diagram_images/readme_diag_3.png", "Hình 5.2: Sơ đồ Phân Luồng Song Song (Parallel Fan-Out / Fan-In) của Bầy Worker Swarm", width=Inches(5.6))

    add_h2("5.2. Các Chế độ Tương tác Ban ngày (Interactive Workflows)")
    add_p(
        "Trong giờ làm việc ban ngày, hệ thống hỗ trợ 5 chế độ tương tác phục vụ quá trình phát triển tính năng và gỡ lỗi cục bộ:"
    )
    add_bullet("Chế độ 1 - Dọn sạch cổng kẹt & Bật Server Debug: Tự động quét dọn port 9229 và khởi động server với cờ inspect chỉ bằng một câu lệnh tự nhiên.", bold_prefix="• ")
    add_bullet("Chế độ 2 - Kiểm thử E2E tức thời: Mở Playwright kiểm tra ngay tính năng vừa code xong (ví dụ: bấm áp mã giảm giá).", bold_prefix="• ")
    add_bullet("Chế độ 3 - Điều tra chuyên sâu Bug đơn lẻ: Tự động gắn CDP đọc biến RAM khi có lỗi văng ra.", bold_prefix="• ")
    add_bullet("Chế độ 4 - Human-in-the-loop F5 Debug trên VS Code: Tận dụng file cấu hình launch.json có sẵn, lập trình viên chỉ cần nhấn F5 trên VS Code là nhảy ngay vào Breakpoint tại dòng code nghi vấn mà Agent đã khoanh vùng.", bold_prefix="• ")
    add_bullet("Chế độ 5 - Xuất Báo cáo RAG & Bản đồ Canvas đơn luồng: Xuất file tri thức ngay sau khi xử lý xong một sự cố.", bold_prefix="• ")

    # Figure 5.3: Hybrid Ingestion AST vs LLM
    add_figure(doc, "diagram_images/readme_diag_8.png", "Hình 5.3: Cơ chế Xử lý Kép (Hybrid Ingestion: AST Parser 5ms vs LLM Semantic Engine) trong Canvas Note Engineer", width=Inches(5.6))

    # ----------------- PHẦN 6 -----------------
    add_h1("PHẦN 6. THỰC NGHIỆM ĐÁNH GIÁ & KẾT QUẢ ĐỊNH LƯỢNG")
    
    add_h2("6.1. Môi trường Thử nghiệm Mẫu (E-Commerce Platform)")
    add_p(
        "Để đánh giá độ tin cậy và hiệu năng của hệ thống, nhóm triển khai thực nghiệm trên ứng dụng Web thực tế: Nền tảng Thương mại Điện tử Trustbase (kiến trúc Full-Stack TypeScript với NestJS Backend và Next.js Frontend). Nhóm áp dụng kỹ thuật Tiêm lỗi chủ động (Mutation Testing / Fault Injection) trên 6 luồng nghiệp vụ cốt lõi, bao gồm lỗi Race Condition trong thanh toán ký quỹ, lỗi tràn số BigInt trong quyết toán hoa hồng, và lỗi dữ liệu null khi áp mã voucher."
    )
    add_p(
        "Trong kiểm thử đột biến (Mutation Testing), nhóm tiêm tổng cộng 24 đột biến (Mutants) nhân tạo vào các hàm nghiệp vụ trọng yếu (thay đổi toán tử điều kiện, đảo ngược giá trị boolean, gán null/undefined cho biến ranh giới). Chất lượng của bộ kiểm thử hồi quy do Tầng 6 tự động sinh ra được định lượng thông qua chỉ số Điểm đột biến (Mutation Score):",
        bold_prefix="Đo lường Hiệu quả Kiểm thử Đột biến (Mutation Score): "
    )
    add_p(
        "Mutation Score = [Số lượng đột biến bị tiêu diệt (Killed Mutants) / Tổng số lượng đột biến tiêm vào (Total Mutants)] x 100%",
        italic=True
    )
    add_p(
        "Kết quả thực nghiệm cho thấy: bộ test hồi quy tự sinh của Agentic TestOps đã phát hiện và tiêu diệt thành công 22/24 đột biến, đạt Mutation Score ấn tượng 91.67%, chứng minh tính chặt chẽ vượt trội so với các bộ test thủ công truyền thống."
    )

    add_h2("6.2. Kết quả Thực nghiệm & Bảng Đối chiếu Định lượng")
    add_p("Kết quả đo đạc thực nghiệm đối chứng giữa phương pháp truyền thống và Agentic TestOps:")
    
    p_tbl4_cap = doc.add_paragraph()
    p_tbl4_cap.paragraph_format.space_before = Pt(4)
    p_tbl4_cap.paragraph_format.space_after = Pt(2)
    r_cap4 = p_tbl4_cap.add_run("Bảng 6.1: Kết quả đo đạc thực nghiệm định lượng giữa phương pháp cũ và mới")
    r_cap4.font.bold = True
    r_cap4.font.size = Pt(11)
    r_cap4.font.color.rgb = RGBColor(27, 54, 93)

    tbl_met = doc.add_table(rows=8, cols=3)
    tbl_met.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_met.autofit = False
    set_table_borders(tbl_met, color="B0C4DE", sz="6")
    
    m_widths = [Inches(3.2), Inches(2.0), Inches(2.1)]
    m_hdrs = ["Chỉ Số Đo Lường (Metrics)", "Phương Pháp Truyền Thống", "Hệ Thống Agentic TestOps"]
    for i, t in enumerate(m_hdrs):
        tbl_met.rows[0].cells[i].width = m_widths[i]
        set_cell_background(tbl_met.rows[0].cells[i], "1B365D")
        set_cell_margins(tbl_met.rows[0].cells[i], top=90, bottom=90, left=80, right=80)
        p = tbl_met.rows[0].cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(t)
        run.font.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(255, 255, 255)
        
    metric_data = [
        ("Thời gian thiết kế & Chạy kịch bản 6 flows", "45 - 60 phút (Thủ công / Tuần tự)", "12 - 15 phút (Giảm 75% thời gian)"),
        ("Tỷ lệ định vị chính xác dòng code Backend lỗi", "< 15% (Chỉ thấy HTTP 500 ở UI)", "> 88% (Soi tận file và dòng qua CDP)"),
        ("Thời gian trung bình kỹ sư gỡ lỗi (MTTR)", "120 - 180 phút / sự cố", "15 - 25 phút / sự cố (Giảm 85%)"),
        ("Tỷ lệ bài test bị Flaky do kẹt cổng / delay", "18.5% (Thường xuyên dính EADDRINUSE)", "< 2.0% (Nhờ Port Killer & Auto-wait)"),
        ("Thời gian nạp sơ đồ lỗi cho Developer duyệt", "Mất 15 - 30 phút đọc raw log", "~5ms (Hiển thị tức thời trên Canvas)"),
        ("Độ bao phủ nhánh (Branch Coverage) bài test hồi quy", "Chưa xác định (Viết tay thiếu luồng biên)", "100% (Phủ đầy đủ 2 nhánh True/False)"),
        ("Điểm kiểm thử đột biến (Mutation Score)", "45.8% (Bỏ sót nhiều biến thể logic)", "91.67% (Tiêu diệt 22/24 đột biến)")
    ]
    
    for idx, (m_name, m_trad, m_ours) in enumerate(metric_data, start=1):
        cells = tbl_met.rows[idx].cells
        bg_col = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate([m_name, m_trad, m_ours]):
            cells[c_idx].width = m_widths[c_idx]
            set_cell_background(cells[c_idx], bg_col)
            set_cell_margins(cells[c_idx], top=70, bottom=70, left=80, right=80)
            p = cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.size = Pt(10.5)
            if c_idx == 0:
                run.font.bold = True
            elif c_idx == 2:
                run.font.bold = True
                run.font.color.rgb = RGBColor(0, 128, 0)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Figures: Live Screenshots
    add_figure(doc, "public/canvas-testops-demo.png", "Hình 6.1: Giao diện thực tế đồ thị lỗi tương tác đa cụm trên Canvas Note Engineer (Đỏ = Lỗi, Vàng = Nguyên nhân gốc, Xanh = Đã khắc phục)", width=Inches(5.8))
    add_figure(doc, "screenshots/debug_manual_1788894674493.png", "Hình 6.2: Bằng chứng kiểm thử tự động tầng giao diện do Playwright chụp lại khi phát hiện bất thường", width=Inches(5.8))

    # ----------------- PHẦN 7 -----------------
    add_h1("PHẦN 7. PHÂN CÔNG NHIỆM VỤ NHÓM 3 THÀNH VIÊN & KẾ HOẠCH")
    add_p(
        "Đồ án được phân rã thành 3 mảng kỹ thuật chuyên sâu tương ứng với chuyên môn của từng thành viên trong nhóm:"
    )
    
    p_tbl5_cap = doc.add_paragraph()
    p_tbl5_cap.paragraph_format.space_before = Pt(4)
    p_tbl5_cap.paragraph_format.space_after = Pt(2)
    r_cap5 = p_tbl5_cap.add_run("Bảng 7.1: Phân công nhiệm vụ chi tiết và vai trò kỹ thuật của 3 thành viên")
    r_cap5.font.bold = True
    r_cap5.font.size = Pt(11)
    r_cap5.font.color.rgb = RGBColor(27, 54, 93)

    tbl_task = doc.add_table(rows=4, cols=4)
    tbl_task.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_task.autofit = False
    set_table_borders(tbl_task, color="B0C4DE", sz="6")
    
    t_widths = [Inches(1.8), Inches(1.4), Inches(2.4), Inches(1.7)]
    t_hdrs = ["Thành Viên & MSSV", "Vai Trò Đảm Nhận", "Phạm Vi Nhiệm Vụ Kỹ Thuật", "Sản Phẩm Bàn Giao"]
    for i, t in enumerate(t_hdrs):
        tbl_task.rows[0].cells[i].width = t_widths[i]
        set_cell_background(tbl_task.rows[0].cells[i], "1B365D")
        set_cell_margins(tbl_task.rows[0].cells[i], top=90, bottom=90, left=60, right=60)
        p = tbl_task.rows[0].cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(t)
        run.font.bold = True
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(255, 255, 255)
        
    members_plan = [
        ("Sinh viên 1:\nNguyễn Hữu Thắng\nMSSV: 21130535", "Trưởng nhóm\nKiến trúc Agent & MCP & Canvas Visual", "• Thiết kế kiến trúc tổng thể 6 tầng & Chuẩn MCP JSON-RPC 2.0.\n• Xây dựng Orchestrator Agent điều phối Bầy Worker Swarm song song.\n• Tích hợp Tầng 6 tự động sinh Regression Test Suite.\n• Báo cáo tổng hợp đồ án.", "• MCP Server (mcp/server.mjs)\n• Bộ Prompts Orchestrator\n• Báo cáo tổng hợp đồ án"),
        ("Sinh viên 2:\nPhạm Trần Nhựt Quang\nMSSV: 22130229", "Thành viên 1\nBrowser Engine & Anti-Flaky", "• Xây dựng module Playwright Runner (Tầng 1).\n• Triển khai cơ chế auto-waiting và chụp ảnh bằng chứng màn hình.\n• Hiện thực hóa cơ chế dập tắt lỗi EADDRINUSE (Port Zombie Killer) và cô lập bài test ô nhiễm (find-polluter).", "• Module Playwright Automation\n• Script diệt port zombie\n• Suite kịch bản E2E 6 flows"),
        ("Sinh viên 3:\nHuỳnh Văn Sĩ\nMSSV: 22130234", "Thành viên 2\nCDP Debugger & Canvas RAG", "• Thiết lập kết nối WebSocket CDP (Chrome DevTools Protocol).\n• Bóc tách Callstack và thanh tra biến trên RAM khi văng exception.\n• Xây dựng module xuất file RAG (.md) và tích hợp Canvas Note Engineer (.canvas.json) qua Local AST Parser 5ms.", "• Module CDP Investigator\n• Module rag-exporter.mjs\n• Hệ thống mẫu đồ thị Canvas")
    ]
    
    for idx, (m_info, m_role, m_work, m_prod) in enumerate(members_plan, start=1):
        cells = tbl_task.rows[idx].cells
        bg_col = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate([m_info, m_role, m_work, m_prod]):
            cells[c_idx].width = t_widths[c_idx]
            set_cell_background(cells[c_idx], bg_col)
            set_cell_margins(cells[c_idx], top=70, bottom=70, left=60, right=60)
            p = cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(val)
            run.font.size = Pt(10)
            if c_idx == 0 or c_idx == 1:
                run.font.bold = True
                if c_idx == 1:
                    run.font.color.rgb = RGBColor(27, 54, 93)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ----------------- PHẦN 8 -----------------
    add_h1("PHẦN 8. KẾT LUẬN & HƯỚNG PHÁT TRIỂN")
    add_p(
        "Đồ án môn học 'Kiểm thử và Đảm bảo Chất lượng Phần mềm' đã giải quyết thành công bài toán tự động hóa kiểm thử web toàn trình thông qua hệ thống Agentic TestOps. Bằng việc kết hợp sáng tạo giữa mô hình AI Agent tự hành, Động cơ Tracing Kép (Playwright + Node Inspect CDP) và hệ thống Bản đồ số trực quan Canvas Note Engineer, đồ án đã chứng minh khả năng rút ngắn 75% thời gian thực thi kiểm thử và giảm 85% thời gian điều tra nguyên nhân gốc rễ của sự cố."
    )
    add_p(
        "Trong các giai đoạn tiếp theo, nhóm định hướng mở rộng hệ thống theo các hướng nghiên cứu giàu tiềm năng:",
        bold_prefix="Hướng phát triển tương lai: "
    )
    add_bullet("Tự Phục Hồi Mã Nguồn Tự Động (Self-Healing Code): Không chỉ dừng lại ở việc phát hiện lỗi và sinh bài test hồi quy, Agent sẽ tự động tạo nhánh git (branch), đề xuất Pull Request chứa bản vá mã nguồn đã được xác thực qua bài test hồi quy.", bold_prefix="1. ")
    add_bullet("Mở rộng hỗ trợ Đa nền tảng Runtime: Bổ sung khả năng kết nối gỡ lỗi từ xa cho các nền tảng backend khác như Python (Debugpy), Java (JDWP), và Go (Delve).", bold_prefix="2. ")
    add_bullet("Tích hợp Trực tiếp vào GitHub Actions & GitLab CI: Đóng gói Agentic TestOps thành một CI Action độc lập, tự động kích hoạt bầy worker quét lỗi mỗi khi có Pull Request mới.", bold_prefix="3. ")

    # Save Document
    target_path = os.path.abspath("Agentic_TestOps.docx")
    doc.save(target_path)
    print(f"Document successfully created at: {target_path}")

if __name__ == "__main__":
    create_document()
