"""
1440Sports Sponsorship Intelligence Brief — PDF Builder (Phase 2.1 / May 2026)

Phase 2 (May 2026) introduced Operational Fit as a 5th dimension and expanded
the score cap to /125. Phase 2.1 (21 May 2026) reverted the cap back to /100
at MD direction while keeping all 5 dimensions first-class — each now 0-20.

Phase 2.1 changes from Phase 2:
- Hero score label: "OPP / 125" -> "OPP / 100"
- Score Composition grid still 5 cells, each now 0-20 (was 0-25)
- HOT TOP TIER eyebrow trigger: score >= 85 (was >= 106)
- WHAT COULD RUN ON THE CAR section trigger: Operational Fit >= 14/20
  (was >= 18/25). Caller responsibility — builder just reads the flag.
- Tighter vertical spacing between score panel and THE CASE section
  (~16pt total vs ~34pt in Phase 2): Spacer(1, 8) + hairline + section_h
  spaceBefore=6 (was Spacer(1, 22) + hairline + spaceBefore=10)
- Logo asset: transparent RGBA PNG (was RGB with black background baked in)

Footer left text remains dynamic on confidence_level: MEDIUM appends
"· VERIFY BEFORE CIRCULATION". LOW briefs are not generated at all.

Used by app.py (Flask service on Railway) to render briefs from JSON requests.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ─────────────────────────────────────────────────────────────────────────
# Brand palette — 1440Sports official identity (unchanged from Phase 1)
# ─────────────────────────────────────────────────────────────────────────
NAVY        = colors.HexColor("#191A48")
GOLD        = colors.HexColor("#D1AE7A")
INK         = colors.HexColor("#0E0E10")
PAPER       = colors.HexColor("#FBFAF7")
MUTED       = colors.HexColor("#65656B")
SOFT        = colors.HexColor("#C9B89A")
PANEL       = colors.HexColor("#F4EFE5")
HAIRLINE    = colors.HexColor("#1A1A1E")

# ─────────────────────────────────────────────────────────────────────────
# Asset paths (unchanged)
# ─────────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(__file__)
FONT_DIR  = os.path.join(BASE_DIR, "fonts")
LOGO_PATH = os.path.join(BASE_DIR, "1440_logo.png")

pdfmetrics.registerFont(TTFont("Lora", f"{FONT_DIR}/Lora-Variable.ttf"))
pdfmetrics.registerFont(TTFont("Lora-Italic", f"{FONT_DIR}/Lora-Italic-Variable.ttf"))
pdfmetrics.registerFont(TTFont("Poppins", f"{FONT_DIR}/Poppins-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Poppins-Medium", f"{FONT_DIR}/Poppins-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Poppins-Bold", f"{FONT_DIR}/Poppins-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Poppins-Light", f"{FONT_DIR}/Poppins-Light.ttf"))

registerFontFamily("Lora", normal="Lora", bold="Lora",
                   italic="Lora-Italic", boldItalic="Lora-Italic")

SERIF      = "Lora"
SERIF_IT   = "Lora-Italic"
SANS       = "Poppins"
SANS_LIGHT = "Poppins-Light"
SANS_MED   = "Poppins-Medium"
SANS_BOLD  = "Poppins-Bold"


def build_brief(brief_data: dict, output_path: str) -> str:
    """
    Render a brief PDF to output_path. Returns output_path.
    
    Phase 2.1 brief_data accepts these optional fields:
      - operational_fit_section: bool  (True if OF >= 14/20 — render section)
      - operational_fit_content: str   (HTML/Paragraph-compatible body)
      - confidence_level: str          ('HIGH' | 'MEDIUM' | 'LOW')
                                       MEDIUM triggers footer warning
      - hot_top_tier: bool             (True if final score >= 85 of 100)
      - score_cells: list of 5 tuples  Each tuple (label, num, "/ 20", note).
                                       Backward-compat: handles 4 or 5 cells.
    """

    PAGE_W, PAGE_H = A4
    
    # Phase 2.1 defaults — backward-compat with Phase 1 / Phase 2 callers
    op_fit_section = brief_data.get('operational_fit_section', False)
    op_fit_content = brief_data.get('operational_fit_content', '')
    confidence    = brief_data.get('confidence_level', 'HIGH')
    hot_top_tier  = brief_data.get('hot_top_tier', False)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=22*mm, rightMargin=22*mm,
        topMargin=30*mm, bottomMargin=22*mm,
        title=f"{brief_data['company']} · Sponsorship Intelligence Brief",
        author="1440 Sports",
    )

    def page_chrome(c, doc_):
        c.saveState()
        c.setFillColor(PAPER)
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

        # Masthead — real logo (unchanged Phase 1 behaviour)
        LOGO_W = 36*mm
        LOGO_H = LOGO_W * (175/1000)
        y_logo_top = PAGE_H - 13*mm
        c.drawImage(LOGO_PATH, 22*mm, y_logo_top - LOGO_H,
                    width=LOGO_W, height=LOGO_H, mask='auto')

        c.setFont(SANS_MED, 7.5)
        c.setFillColor(MUTED)
        c.drawRightString(PAGE_W - 22*mm, y_logo_top - LOGO_H/2 - 1,
                          "INTELLIGENCE BRIEF  ·  CONFIDENTIAL")

        rule_y = PAGE_H - 22*mm
        c.setStrokeColor(HAIRLINE)
        c.setLineWidth(0.4)
        c.line(22*mm, rule_y, PAGE_W - 22*mm, rule_y)

        # Footer — Phase 2: dynamic on confidence_level
        foot_y = 14*mm
        c.setStrokeColor(HAIRLINE)
        c.setLineWidth(0.3)
        c.line(22*mm, foot_y + 4*mm, PAGE_W - 22*mm, foot_y + 4*mm)
        c.setFont(SANS_MED, 7.5)
        c.setFillColor(NAVY)
        if confidence == 'MEDIUM':
            c.drawString(22*mm, foot_y, 
                         "1440 SPORTS  ·  LONDON  ·  VERIFY BEFORE CIRCULATION")
        else:
            c.drawString(22*mm, foot_y, "1440 SPORTS  ·  LONDON")
        c.setFillColor(MUTED)
        c.drawCentredString(
            PAGE_W/2, foot_y,
            f"{brief_data['footer_company']}  ·  {brief_data['footer_date']}"
        )
        c.drawRightString(PAGE_W - 22*mm, foot_y, f"{doc_.page} / 2")
        c.restoreState()

    # ─────────────────────────────────────────────────────────────────
    # Styles — most unchanged from Phase 1; small adjustments noted
    # ─────────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    eyebrow = ParagraphStyle('Eyebrow', parent=styles['Normal'],
        fontName=SANS_BOLD, fontSize=8, leading=10,
        textColor=GOLD, alignment=TA_LEFT, spaceAfter=4)
    display = ParagraphStyle('Display', parent=styles['Title'],
        fontName=SERIF, fontSize=46, leading=50,
        textColor=NAVY, alignment=TA_LEFT, spaceAfter=2)
    display_meta = ParagraphStyle('DisplayMeta', parent=styles['Normal'],
        fontName=SERIF_IT, fontSize=12, leading=16,
        textColor=MUTED, alignment=TA_LEFT, spaceAfter=10)
    deck = ParagraphStyle('Deck', parent=styles['Normal'],
        fontName=SERIF_IT, fontSize=15, leading=22,
        textColor=INK, alignment=TA_LEFT, spaceAfter=12)
    section_h = ParagraphStyle('SectionH', parent=styles['Heading2'],
        fontName=SANS_BOLD, fontSize=8.5, leading=11,
        textColor=GOLD, alignment=TA_LEFT,
        spaceBefore=4, spaceAfter=5)
    body = ParagraphStyle('Body', parent=styles['Normal'],
        fontName=SERIF, fontSize=10, leading=14.5,
        textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6)
    callout = ParagraphStyle('Callout', parent=body,
        fontName=SERIF, fontSize=10, leading=14.5,
        textColor=INK, alignment=TA_LEFT, spaceAfter=0)
    big_num = ParagraphStyle('BigNum', parent=styles['Normal'],
        fontName=SERIF, fontSize=48, leading=52,
        textColor=NAVY, alignment=TA_LEFT, spaceAfter=0)
    big_num_label = ParagraphStyle('BigNumLab', parent=styles['Normal'],
        fontName=SANS_MED, fontSize=7.5, leading=10,
        textColor=MUTED, alignment=TA_LEFT, spaceAfter=0)
    mini_num = ParagraphStyle('MiniNum', parent=styles['Normal'],
        fontName=SANS_BOLD, fontSize=14, leading=18,
        textColor=NAVY, alignment=TA_LEFT)
    mini_lab = ParagraphStyle('MiniLab', parent=styles['Normal'],
        fontName=SANS, fontSize=7.5, leading=10,
        textColor=MUTED, alignment=TA_LEFT)
    contact_name = ParagraphStyle('CName', parent=styles['Normal'],
        fontName=SERIF, fontSize=22, leading=26,
        textColor=NAVY, alignment=TA_LEFT, spaceAfter=2)
    contact_role = ParagraphStyle('CRole', parent=styles['Normal'],
        fontName=SANS, fontSize=9, leading=12,
        textColor=MUTED, alignment=TA_LEFT, spaceAfter=8)
    small_body = ParagraphStyle('SmallBody', parent=body, fontSize=9.5, leading=13.5,
        spaceAfter=6)
    hook_quote = ParagraphStyle('HookQ', parent=styles['Normal'],
        fontName=SERIF_IT, fontSize=10.5, leading=15,
        textColor=INK, alignment=TA_LEFT,
        leftIndent=8, rightIndent=4, spaceBefore=4, spaceAfter=4)

    # Phase 2: Score grid styles — sizes reduced for 5-cell layout
    score_grid_lab = ParagraphStyle('SGL', parent=styles['Normal'],
        fontName=SANS_MED, fontSize=7.5, leading=9.5,
        textColor=MUTED, alignment=TA_LEFT)
    score_grid_num = ParagraphStyle('SGN', parent=styles['Normal'],
        fontName=SERIF, fontSize=20, leading=24,
        textColor=NAVY, alignment=TA_LEFT)
    score_grid_note = ParagraphStyle('SGNo', parent=styles['Normal'],
        fontName=SERIF, fontSize=8.5, leading=11.5,
        textColor=INK, alignment=TA_LEFT)

    story = []

    # ─────────────────────── PAGE 1 ───────────────────────
    # Eyebrow — Phase 2.1: append HOT TOP TIER for scores >= 85
    eyebrow_text = (
        f"INTELLIGENCE BRIEF&nbsp;&nbsp;/&nbsp;&nbsp;N° {brief_data['brief_number']}"
        f"{brief_data.get('track_label', '')}"
    )
    if hot_top_tier:
        eyebrow_text += "&nbsp;&nbsp;·&nbsp;&nbsp;HOT TOP TIER"
    story.append(Paragraph(eyebrow_text, eyebrow))
    
    story.append(Spacer(1, 4))
    story.append(Paragraph(brief_data['company'], display))
    story.append(Paragraph(brief_data['industry_meta'], display_meta))
    story.append(HRFlowable(width="100%", thickness=1.5,
                            color=GOLD, spaceBefore=2, spaceAfter=18))
    story.append(Paragraph(brief_data['deck'], deck))

    # Score row — Phase 2.1: hero label /100 (was /125 in Phase 2)
    score_row = Table([[
        [Paragraph(str(brief_data['score']), big_num),
         Spacer(1, 2),
         Paragraph("OPPORTUNITY  /  100", big_num_label)],
        [Paragraph(brief_data['timing_label'], mini_num),
         Paragraph("TIMING WINDOW", mini_lab),
         Spacer(1, 12),
         Paragraph(brief_data['series_label'], mini_num),
         Paragraph("SERIES", mini_lab)],
        [Paragraph(brief_data['team_label'], mini_num),
         Paragraph("RECOMMENDED TEAM", mini_lab),
         Spacer(1, 12),
         Paragraph(brief_data['horizon_label'], mini_num),
         Paragraph("ACTION HORIZON", mini_lab)],
    ]], colWidths=[58*mm, 50*mm, 58*mm])
    score_row.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEAFTER', (0,0), (0,0), 0.4, HAIRLINE),
        ('LINEAFTER', (1,0), (1,0), 0.4, HAIRLINE),
        ('LEFTPADDING', (1,0), (1,0), 16),
        ('LEFTPADDING', (2,0), (2,0), 16),
    ]))
    story.append(score_row)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.4,
                            color=HAIRLINE, spaceAfter=2))

    # THE CASE
    story.append(Paragraph("THE CASE", section_h))
    story.append(Paragraph(brief_data['the_case_p1'], body))
    story.append(Paragraph(brief_data['the_case_p2'], body))

    # Why Now Callout
    timing_callout = Table([[Paragraph(brief_data['why_now_callout'], callout)]],
                           colWidths=[166*mm])
    timing_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PANEL),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 13),
        ('BOTTOMPADDING', (0,0), (-1,-1), 13),
        ('LINEBEFORE', (0,0), (0,0), 3, GOLD),
    ]))
    story.append(Spacer(1, 6))
    story.append(timing_callout)

    story.append(PageBreak())

    # ─────────────────────── PAGE 2 ───────────────────────
    story.append(Paragraph(brief_data['why_team_label'], section_h))
    story.append(Paragraph(brief_data['why_team_para'], body))

    # PHASE 2: WHAT COULD RUN ON THE CAR — conditionally rendered
    if op_fit_section and op_fit_content:
        story.append(Paragraph("WHAT COULD RUN ON THE CAR", section_h))
        story.append(Paragraph(op_fit_content, body))

    story.append(Paragraph("DEAL ARCHITECTURE", section_h))
    story.append(Paragraph(brief_data['deal_arch_para'], body))

    # Two-column DM bio / Opening Angle
    left_col = [
        Paragraph("PRIMARY DECISION-MAKER", section_h),
        Paragraph(brief_data['decision_maker_name'], contact_name),
        Paragraph(brief_data['decision_maker_role'], contact_role),
        Paragraph(brief_data['decision_maker_bio'], small_body),
    ]
    right_col = [
        Paragraph("OPENING ANGLE", section_h),
        Paragraph(brief_data['opening_angle_intro'], small_body),
        Paragraph(brief_data['opening_angle_quote'], hook_quote),
    ]
    two_col = Table([[left_col, right_col]], colWidths=[80*mm, 86*mm])
    two_col.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (0,0), 0),
        ('RIGHTPADDING', (0,0), (0,0), 12),
        ('LEFTPADDING', (1,0), (1,0), 12),
        ('RIGHTPADDING', (1,0), (1,0), 0),
        ('LINEBEFORE', (1,0), (1,0), 0.4, HAIRLINE),
    ]))
    story.append(Spacer(1, 4))
    story.append(two_col)

    # Score Composition grid — Phase 2: 5 cells not 4
    story.append(Paragraph("SCORE COMPOSITION", section_h))
    story.append(Spacer(1, 4))

    score_grid_cells = []
    for label, num, denom, note in brief_data['score_cells']:
        score_grid_cells.append([
            Paragraph(label, score_grid_lab),
            Paragraph(f"{num}<font size='12' color='#C9B89A'> {denom}</font>",
                      score_grid_num),
            Paragraph(note, score_grid_note),
        ])

    # Phase 2: column count = len(score_cells). Backward-compat: handles 4 or 5.
    num_cells = len(score_grid_cells)
    total_width = 166 * mm
    col_width = total_width / num_cells

    score_grid = Table([score_grid_cells], colWidths=[col_width]*num_cells)
    grid_style = [
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,0), (-1,-1), PANEL),
    ]
    # Vertical hairlines between every cell
    for i in range(1, num_cells):
        grid_style.append(('LINEBEFORE', (i,0), (i,0), 0.3, SOFT))
    score_grid.setStyle(TableStyle(grid_style))
    story.append(score_grid)

    # Risks
    story.append(Paragraph("RISKS", section_h))
    for label, body_text in brief_data['risks']:
        story.append(Paragraph(
            f"<font name='Poppins-Bold' size='9'>{label}</font>&nbsp;&nbsp;{body_text}",
            body
        ))

    doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
    return output_path
