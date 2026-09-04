"""
1440Sports Sponsorship Intelligence Brief — PDF Builder Template (Phase 2.1)

A parameterised version of the proven brief builder. To use:
1. Copy this file to /home/claude/build_[company].py
2. Edit the BRIEF_DATA dict at the top with the new company's content
3. Run: python build_[company].py

The builder.py file in this skill folder is the Railway-deployed
production version of the same logic (refactored as a callable function).
This file is the local canonical design source — keep them in sync.

Phase 2 (May 2026) introduced Operational Fit as a 5th dimension and
expanded the cap to /125. Phase 2.1 (21 May 2026) reverted the cap back
to /100 at MD direction while keeping all 5 dimensions as first-class —
each now scored 0-20 instead of 0-25.

Phase 2.1 changes vs Phase 2:
- Score grid: 5 cells now 0-20 each (was 0-25 each)
- Hero label: "OPP / 125" -> "OPP / 100"
- Tier thresholds revert to original /100 bands:
  HOT TOP TIER 85+, HOT 70-84, WARM 55-69, VERIFY 40-54, PLANT 25-39
- "WHAT COULD RUN ON THE CAR" section trigger: Operational Fit >= 14/20
  (was >= 18/25)
- HOT TOP TIER eyebrow tag trigger: total score >= 85 (was >= 106)
- Tighter vertical spacing between score panel and THE CASE section
  (~16pt total vs ~34pt in Phase 2)
- Logo file: transparent RGBA PNG (was RGB with black background baked in)

Footer remains dynamic on confidence_level: MEDIUM appends
"· VERIFY BEFORE CIRCULATION".

Tested with Phase 1: Mistral AI, Factory AI, Luminary Cloud (May 2026).
Produces: 2-page A4 PDF in 1440Sports brand format (Lora + Poppins,
navy + gold palette, real logo embedded).
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

# ═══════════════════════════════════════════════════════════════════════
# EDIT THIS SECTION FOR EACH NEW BRIEF
# ═══════════════════════════════════════════════════════════════════════

BRIEF_DATA = {
    # Header / identity
    "brief_number": "010",                         # Sequential brief number
    "track_label": "",                             # "" for Track 1, " · ALUMNI INTELLIGENCE" for Track 2
    "company": "Mistral AI",
    "industry_meta": "Sovereign foundation models  ·  Paris, France  ·  May 2026",
    "footer_company": "MISTRAL AI",
    "footer_date": "May 2026",

    # The deck — 4-5 line italic headline thought
    "deck": (
        "A French AI champion at the brand-reckoning inflection. Alpine F1 "
        "is the only sponsorship asset that delivers Mistral's investor "
        "narrative to enterprise buyers in Paris, Berlin and Brussels — and "
        "the window closes when Q3 brand planning begins."
    ),

    # Hero score (Phase 2.1: /100 cap, was /125 in Phase 2)
    "score": 82,                                   # Out of 100
    "timing_label": "HOT",
    "series_label": "F1",
    "team_label": "ALPINE",
    "horizon_label": "4–6 WKS",

    # Phase 2.1 flags
    "confidence_level": "HIGH",                    # 'HIGH' | 'MEDIUM' | 'LOW'
    "hot_top_tier": False,                         # True when score >= 85
    "operational_fit_section": True,               # True when OF >= 14/20

    # THE CASE — two paragraphs
    "the_case_p1": (
        "Mistral closed an $830M debt raise in March on top of a $1.7B Series C, "
        "valued at $14B and converging on $100M ARR. In the same quarter they "
        "signed Accenture as a strategic distribution partner, launched Forge "
        "for enterprise on-premise training, and opened offices in London, "
        "New York and Singapore. Compound signals like these — funding plus "
        "partnership plus product plus expansion — mark the "
        "<font name='Poppins-Bold' size='9.5'>BRAND RECKONING</font> "
        "moment when AI unicorns must earn cultural permission, not just "
        "technical respect."
    ),
    "the_case_p2": (
        "Mistral's competitive moat against OpenAI and Anthropic is not model "
        "performance. It is <i>European, sovereign, regulated, ours.</i> That "
        "story converts enterprise buyers in regulated industries — but only "
        "when delivered through a culturally European amplifier that the CIO "
        "audience already trusts. Alpine F1 is that amplifier."
    ),

    # WHY NOW callout (in beige panel with gold left bar)
    "why_now_callout": (
        "The Accenture partnership is announced, Forge has shipped, and the new "
        "offices are open. The technology and the distribution are set — what "
        "isn't set is the cultural amplifier for enterprise buyers in regulated "
        "European industries. That decision will be made between now and the "
        "Q3 brand planning cycle, which closes in roughly eight weeks. After "
        "that, Mistral will commit a year of brand investment elsewhere."
    ),

    # Page 2 — WHY [TEAM]
    "why_team_label": "WHY ALPINE",
    "why_team_para": (
        "Alpine is the only French-headquartered F1 team and the only team whose "
        "commercial narrative is explicitly aligned with European industrial "
        "sovereignty. The team's BWT title sponsorship and Renault-adjacent "
        "ownership structure means the partnership sits inside a recognisably "
        "European commercial logic — not a generic global F1 placement. For an "
        "AI lab whose differentiation is European sovereignty, that alignment is "
        "narrative-perfect."
    ),

    # Phase 2 NEW: WHAT COULD RUN ON THE CAR
    "operational_fit_content": (
        "Mistral's Forge platform — on-premise enterprise model training — maps "
        "directly to Alpine's race-strategy stack, which today runs on Microsoft "
        "(joined 2026) but lacks a dedicated generative-AI inference layer. A "
        "Forge deployment for Alpine's pit-wall would give Mistral a credible "
        "<font name='Poppins-Bold' size='9.5'>BROADCAST DATA FEED</font> for "
        "race-strategy decision graphics, and Alpine a competitive edge against "
        "the Mercedes-AMD and McLaren-Google Cloud benchmarks. Deployment surface: "
        "pit-wall strategy graphics, engineer headsets, factory telemetry wall."
    ),

    # DEAL ARCHITECTURE
    "deal_arch_para": (
        "<font name='Poppins-Bold' size='9.5'>TWO YEARS</font> minimum, structured "
        "as a co-branded Forge-Alpine technical partnership plus livery presence. "
        "Year 1 anchors on Paris and Spa hospitality (CIO and EU regulator audiences); "
        "Year 2 expands to Singapore and Las Vegas for the GTM markets. Forge runs "
        "publicly on Alpine's race-strategy stack as the live product demonstration. "
        "Mid-tier annual investment plus technical-services-in-kind."
    ),

    # PRIMARY DECISION-MAKER
    "decision_maker_name": "Arthur Mensch",
    "decision_maker_role": "CEO and Co-Founder, Mistral AI",
    "decision_maker_bio": (
        "Co-founder and CEO since 2023. Ex-DeepMind research scientist; one of the "
        "most-cited European AI researchers under 35. Sets brand strategy personally "
        "and has been clear publicly that Mistral's positioning is European sovereignty "
        "first, technical performance second. Speaks at Davos, French Senate, EU "
        "Commission roundtables. Source: Mistral company page; Le Monde profile, "
        "March 2026."
    ),

    # OPENING ANGLE
    "opening_angle_intro": (
        "Lead with the narrative-fit case before the deal mechanics. Mensch's strategic "
        "frame is sovereignty; the opener must speak in that register, not in "
        "sponsorship-agency language. The 25-minute ask is anchored to the Q3 brand "
        "planning cycle — a date Mensch knows is approaching."
    ),
    "opening_angle_quote": (
        "&ldquo;Arthur, following the Accenture partnership and Forge launch — the "
        "distribution is set, the technology is set, but the cultural amplifier for "
        "enterprise buyers in regulated European industries isn't yet defined. Wanted "
        "to share why Alpine specifically is the sharpest tool for that job before "
        "the Q3 brand planning cycle closes. 25 minutes in the next two weeks?&rdquo;"
    ),

    # SCORE COMPOSITION (Phase 2.1: 5 cells × /20, was 5 cells × /25 in Phase 2)
    # Format: (label, num, denom, note)
    "score_cells": [
        ("TIMING", "18", "/ 20", "Compound signals all within last 90 days. Q3 brand cycle opens in ~8 weeks."),
        ("CAPACITY", "17", "/ 20", "$14B valuation, mid-tier deal capacity ($5-10M/yr). Recent $830M debt raise confirms appetite for capex."),
        ("BRAND FIT", "18", "/ 20", "BRAND RECKONING archetype. European sovereignty narrative maps cleanly to Alpine's French ownership and BWT title."),
        ("URGENCY", "14", "/ 20", "Strong external trigger: Q3 brand planning deadline. Internal trigger: Forge launch needs cultural amplifier."),
        ("OPS FIT", "15", "/ 20", "Forge maps to A1 (race strategy) taxonomy. Alpine has no dedicated GenAI inference partner. Gate applied: Brand Fit ≥ 12 ✓"),
    ],

    # RISKS — Phase 2: 2 paragraphs (was 2-3), each with inline bold label
    "risks": [
        ("CAPITAL DISCIPLINE",
         "Mistral has been deliberate with marketing spend, preferring technical "
         "credibility through research output. The Alpine pitch must frame the deal "
         "as commercial-technical, not as a marketing line-item. Forge running on the "
         "car is the bridge between those two framings."),
        ("FOUNDER IDEOLOGY",
         "Mensch is publicly sceptical of US-style brand-building. The European-"
         "sovereignty wrapper is essential to him hearing the pitch at all. Generic "
         "F1 hospitality language will close the door before the meeting starts."),
    ],
}

# ═══════════════════════════════════════════════════════════════════════
# RENDERING LOGIC — DO NOT EDIT BELOW THIS LINE UNLESS DESIGN CHANGES
# ═══════════════════════════════════════════════════════════════════════

# Brand palette — 1440Sports official identity
NAVY        = colors.HexColor("#191A48")
GOLD        = colors.HexColor("#D1AE7A")
INK         = colors.HexColor("#0E0E10")
PAPER       = colors.HexColor("#FBFAF7")
MUTED       = colors.HexColor("#65656B")
SOFT        = colors.HexColor("#C9B89A")
PANEL       = colors.HexColor("#F4EFE5")
HAIRLINE    = colors.HexColor("#1A1A1E")

# Asset paths — assumes script is co-located with fonts/ and 1440_logo.png
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
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

PAGE_W, PAGE_H = A4
OUTPUT_FILENAME = f"1440_Intelligence_Brief_{BRIEF_DATA['company'].replace(' ', '_')}.pdf"

doc = SimpleDocTemplate(
    OUTPUT_FILENAME, pagesize=A4,
    leftMargin=22*mm, rightMargin=22*mm,
    topMargin=30*mm, bottomMargin=22*mm,
    title=f"{BRIEF_DATA['company']} · Sponsorship Intelligence Brief",
    author="1440 Sports",
)

# Phase 2 defaults
op_fit_section = BRIEF_DATA.get('operational_fit_section', False)
op_fit_content = BRIEF_DATA.get('operational_fit_content', '')
confidence     = BRIEF_DATA.get('confidence_level', 'HIGH')
hot_top_tier   = BRIEF_DATA.get('hot_top_tier', False)


def page_chrome(c, doc_):
    c.saveState()
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # Masthead — real logo
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
        f"{BRIEF_DATA['footer_company']}  ·  {BRIEF_DATA['footer_date']}"
    )
    c.drawRightString(PAGE_W - 22*mm, foot_y, f"{doc_.page} / 2")
    c.restoreState()


# Styles
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
    textColor=GOLD, alignment=TA_LEFT, spaceBefore=4, spaceAfter=5)
body = ParagraphStyle('Body', parent=styles['Normal'],
    fontName=SERIF, fontSize=10, leading=14.5,
    textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6)
callout = ParagraphStyle('Callout', parent=body, fontName=SERIF, fontSize=10,
    leading=14.5, textColor=INK, alignment=TA_LEFT, spaceAfter=0)
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
small_body = ParagraphStyle('SmallBody', parent=body, fontSize=9.5,
    leading=13.5, spaceAfter=6)
hook_quote = ParagraphStyle('HookQ', parent=styles['Normal'],
    fontName=SERIF_IT, fontSize=10.5, leading=15,
    textColor=INK, alignment=TA_LEFT,
    leftIndent=8, rightIndent=4, spaceBefore=4, spaceAfter=4)
# Phase 2: 5-cell grid styles (slightly smaller than 4-cell)
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
eyebrow_text = (
    f"INTELLIGENCE BRIEF&nbsp;&nbsp;/&nbsp;&nbsp;N° {BRIEF_DATA['brief_number']}"
    f"{BRIEF_DATA.get('track_label', '')}"
)
if hot_top_tier:
    eyebrow_text += "&nbsp;&nbsp;·&nbsp;&nbsp;HOT TOP TIER"
story.append(Paragraph(eyebrow_text, eyebrow))

story.append(Spacer(1, 4))
story.append(Paragraph(BRIEF_DATA['company'], display))
story.append(Paragraph(BRIEF_DATA['industry_meta'], display_meta))
story.append(HRFlowable(width="100%", thickness=1.5,
                        color=GOLD, spaceBefore=2, spaceAfter=18))
story.append(Paragraph(BRIEF_DATA['deck'], deck))

# Score row — Phase 2.1: /100 hero (was /125 in Phase 2)
score_row = Table([[
    [Paragraph(str(BRIEF_DATA['score']), big_num),
     Spacer(1, 2),
     Paragraph("OPPORTUNITY  /  100", big_num_label)],
    [Paragraph(BRIEF_DATA['timing_label'], mini_num),
     Paragraph("TIMING WINDOW", mini_lab),
     Spacer(1, 12),
     Paragraph(BRIEF_DATA['series_label'], mini_num),
     Paragraph("SERIES", mini_lab)],
    [Paragraph(BRIEF_DATA['team_label'], mini_num),
     Paragraph("RECOMMENDED TEAM", mini_lab),
     Spacer(1, 12),
     Paragraph(BRIEF_DATA['horizon_label'], mini_num),
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
story.append(HRFlowable(width="100%", thickness=0.4, color=HAIRLINE, spaceAfter=2))

# THE CASE
story.append(Paragraph("THE CASE", section_h))
story.append(Paragraph(BRIEF_DATA['the_case_p1'], body))
story.append(Paragraph(BRIEF_DATA['the_case_p2'], body))

# Why Now Callout
timing_callout = Table([[Paragraph(BRIEF_DATA['why_now_callout'], callout)]],
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
story.append(Paragraph(BRIEF_DATA['why_team_label'], section_h))
story.append(Paragraph(BRIEF_DATA['why_team_para'], body))

# PHASE 2: WHAT COULD RUN ON THE CAR — conditional
if op_fit_section and op_fit_content:
    story.append(Paragraph("WHAT COULD RUN ON THE CAR", section_h))
    story.append(Paragraph(op_fit_content, body))

story.append(Paragraph("DEAL ARCHITECTURE", section_h))
story.append(Paragraph(BRIEF_DATA['deal_arch_para'], body))

# Two-column DM bio / Opening Angle
left_col = [
    Paragraph("PRIMARY DECISION-MAKER", section_h),
    Paragraph(BRIEF_DATA['decision_maker_name'], contact_name),
    Paragraph(BRIEF_DATA['decision_maker_role'], contact_role),
    Paragraph(BRIEF_DATA['decision_maker_bio'], small_body),
]
right_col = [
    Paragraph("OPENING ANGLE", section_h),
    Paragraph(BRIEF_DATA['opening_angle_intro'], small_body),
    Paragraph(BRIEF_DATA['opening_angle_quote'], hook_quote),
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

# Score Composition grid — Phase 2: dynamic cell count (4 or 5)
story.append(Paragraph("SCORE COMPOSITION", section_h))
story.append(Spacer(1, 4))

score_grid_cells = []
for label, num, denom, note in BRIEF_DATA['score_cells']:
    score_grid_cells.append([
        Paragraph(label, score_grid_lab),
        Paragraph(f"{num}<font size='12' color='#C9B89A'> {denom}</font>",
                  score_grid_num),
        Paragraph(note, score_grid_note),
    ])

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
for i in range(1, num_cells):
    grid_style.append(('LINEBEFORE', (i,0), (i,0), 0.3, SOFT))
score_grid.setStyle(TableStyle(grid_style))
story.append(score_grid)

# Risks
story.append(Paragraph("RISKS", section_h))
for label, body_text in BRIEF_DATA['risks']:
    story.append(Paragraph(
        f"<font name='Poppins-Bold' size='9'>{label}</font>&nbsp;&nbsp;{body_text}",
        body
    ))

doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
print(f"✅ Brief built: {OUTPUT_FILENAME}")
