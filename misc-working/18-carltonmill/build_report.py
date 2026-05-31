#!/usr/bin/env python3
"""Citadel Capital — branded acquisition work-up PDF for 602/18 Carlton Mill Road."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, FrameBreak, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

# ---- Brand palette -------------------------------------------------------
NAVY   = colors.HexColor("#0B1F3A")   # deep fortress navy
NAVY2  = colors.HexColor("#13294B")
GOLD   = colors.HexColor("#C8A24B")   # citadel gold accent
SLATE  = colors.HexColor("#33414E")
LIGHT  = colors.HexColor("#F4F6F8")
RULEG  = colors.HexColor("#D9DEE3")
WHITE  = colors.white
RED     = colors.HexColor("#9A2B2B")

PAGE_W, PAGE_H = A4
LM = RM = 18*mm
TM = 30*mm
BM = 20*mm

styles = {}
def S(name, **kw):
    styles[name] = ParagraphStyle(name, **kw); return styles[name]

S("h1", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=NAVY, spaceBefore=10, spaceAfter=4)
S("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=NAVY, spaceBefore=12, spaceAfter=3)
S("body", fontName="Helvetica", fontSize=9.3, leading=13.2, textColor=SLATE, spaceAfter=5)
S("bullet", fontName="Helvetica", fontSize=9.3, leading=13, textColor=SLATE, leftIndent=10, bulletIndent=0, spaceAfter=3)
S("small", fontName="Helvetica", fontSize=7.6, leading=10, textColor=colors.HexColor("#6B7884"))
S("kicker", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=GOLD, spaceAfter=2)
S("cellh", fontName="Helvetica-Bold", fontSize=8.4, leading=10.5, textColor=WHITE)
S("cell", fontName="Helvetica", fontSize=8.4, leading=10.8, textColor=SLATE)
S("cellb", fontName="Helvetica-Bold", fontSize=8.4, leading=10.8, textColor=NAVY)
S("coverttl", fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=WHITE)
S("coversub", fontName="Helvetica", fontSize=11, leading=15, textColor=colors.HexColor("#C9D3DE"))
S("wordmark", fontName="Helvetica-Bold", fontSize=15, leading=15, textColor=WHITE)
S("wordmarks", fontName="Helvetica", fontSize=7.5, leading=9, textColor=GOLD)

def para(t, st="body"): return Paragraph(t, styles[st])
def bullet(t): return Paragraph(t, styles["bullet"], bulletText="•")

# ---- page furniture ------------------------------------------------------
def header_footer(canvas, doc):
    canvas.saveState()
    # top brand strip
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H-16*mm, PAGE_W, 16*mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, PAGE_H-16.8*mm, PAGE_W, 0.8*mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 10.5)
    canvas.drawString(LM, PAGE_H-10.3*mm, "CITADEL CAPITAL")
    canvas.setFillColor(GOLD); canvas.setFont("Helvetica", 6.8)
    canvas.drawString(LM, PAGE_H-13.6*mm, "PRIVATE  ·  ACQUISITIONS")
    canvas.setFillColor(colors.HexColor("#C9D3DE")); canvas.setFont("Helvetica", 7.6)
    canvas.drawRightString(PAGE_W-RM, PAGE_H-11.4*mm, "602 / 18 Carlton Mill Road, Merivale")
    # footer
    canvas.setFillColor(RULEG); canvas.rect(LM, BM-3*mm, PAGE_W-LM-RM, 0.4, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#6B7884")); canvas.setFont("Helvetica", 6.9)
    canvas.drawString(LM, BM-7*mm, "STRICTLY PRIVATE & CONFIDENTIAL — Prepared by Citadel Capital Limited. Indicative desktop analysis; not advice. Verify all figures before offer.")
    canvas.drawRightString(PAGE_W-RM, BM-7*mm, "Page %d" % doc.page)
    canvas.restoreState()

def cover_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY); canvas.rect(0,0,PAGE_W,PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(NAVY2); canvas.rect(0, PAGE_H*0.46, PAGE_W, PAGE_H*0.54, fill=1, stroke=0)
    # gold rules
    canvas.setFillColor(GOLD)
    canvas.rect(LM, PAGE_H*0.46, 46*mm, 1.4*mm, fill=1, stroke=0)
    # wordmark top
    canvas.setFillColor(WHITE); canvas.setFont("Helvetica-Bold", 16)
    canvas.drawString(LM, PAGE_H-26*mm, "CITADEL CAPITAL")
    canvas.setFillColor(GOLD); canvas.setFont("Helvetica", 8)
    canvas.drawString(LM, PAGE_H-30*mm, "PRIVATE  ·  PROPERTY  ·  ACQUISITIONS")
    # kicker
    canvas.setFillColor(GOLD); canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(LM, PAGE_H*0.46+10*mm, "ACQUISITION WORK-UP  ·  STAGE 1 (DESKTOP)")
    # title
    canvas.setFillColor(WHITE); canvas.setFont("Helvetica-Bold", 26)
    canvas.drawString(LM, PAGE_H*0.46-6*mm, "602 / 18 Carlton Mill Road")
    canvas.setFont("Helvetica", 15); canvas.setFillColor(colors.HexColor("#C9D3DE"))
    canvas.drawString(LM, PAGE_H*0.46-15*mm, "Merivale, Christchurch  ·  Kamahi Apartments penthouse")
    # meta block
    canvas.setFillColor(colors.HexColor("#9FB0C2")); canvas.setFont("Helvetica", 9.5)
    y = PAGE_H*0.46-30*mm
    for line in [
        "Listing:  PropertyFiles RX4883894  ·  Cowdy & Co (Tom Rennie / Jake Wieblitz)",
        "Asking:   Offers Over $1,449,000   ·   HomesEstimate $1.43M – $1.6M",
        "Prepared: 31 May 2026   ·   Citadel Capital — Acquisitions",
    ]:
        canvas.drawString(LM, y, line); y -= 6.2*mm
    # confidential band bottom
    canvas.setFillColor(GOLD); canvas.rect(0, 14*mm, PAGE_W, 0.8*mm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#9FB0C2")); canvas.setFont("Helvetica", 7.5)
    canvas.drawString(LM, 9*mm, "STRICTLY PRIVATE & CONFIDENTIAL — for internal Citadel Capital use only.")
    canvas.restoreState()

# ---- table helper --------------------------------------------------------
def kv_table(rows, col_widths, header=None):
    data = []
    if header:
        data.append([Paragraph(h, styles["cellh"]) for h in header])
    for r in rows:
        data.append([Paragraph(str(c[0]) if not isinstance(c,(list,tuple)) else c[0], c[1] if isinstance(c,(list,tuple)) else styles["cell"]) for c in
                     ([(x, styles["cell"]) for x in r] if False else [(x,) for x in r])])
    # simpler: build below
    return data

def make_table(header, rows, widths, hsplit=None):
    data = [[Paragraph(h, styles["cellh"]) for h in header]]
    styled_rows = []
    for r in rows:
        cells = []
        for i, val in enumerate(r):
            st = "cellb" if (i == 0) else "cell"
            txt = val
            cells.append(Paragraph(txt, styles[st]))
        data.append(cells)
    t = Table(data, colWidths=widths, repeatRows=1)
    ts = [
        ("BACKGROUND",(0,0),(-1,0), NAVY),
        ("LINEBELOW",(0,0),(-1,0), 0.6, GOLD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LIGHT]),
        ("LINEBELOW",(0,1),(-1,-2), 0.3, RULEG),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),6),
        ("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),4.5),
        ("BOTTOMPADDING",(0,0),(-1,-1),4.5),
        ("BOX",(0,0),(-1,-1),0.4, RULEG),
    ]
    t.setStyle(TableStyle(ts))
    return t

# ---- document ------------------------------------------------------------
story = []
def H1(t): story.append(para(t,"h1"))
def H2(t): story.append(para(t,"h2"))
def P(t): story.append(para(t))
def B(t): story.append(bullet(t))
def SP(h=4): story.append(Spacer(1,h))

# Section 1
H1("1 &nbsp; Executive summary &amp; recommendation")
P("602/18 Carlton Mill Road is the <b>two-level penthouse</b> of the <i>Kamahi Apartments</i> — a small (13-unit), recently fully-renovated and <b>earthquake-strengthened to 100% NBS</b> boutique complex on the Avon River edge of Merivale, directly opposite Hagley Park and ~5 minutes to the Christchurch CBD. It is a <b>completed, prime-location lifestyle / owner-occupier asset</b>, not a development play.")
B("<b>Asking:</b> Offers Over <b>$1,449,000</b> (listed 10 Feb 2026; realestate.co.nz currently shows &ldquo;By Negotiation&rdquo;). <b>HomesEstimate $1.43M–$1.6M</b> (28 May 2026) — the ask sits at the bottom of the automated range; mildly encouraging, but the AVM band is wide.")
B("<b>Scale:</b> ~<b>210 m&sup2;</b> over two levels, <b>2 bed / 2 bath + separate study</b>, <b>3 private decks</b>, <b>2 secure underground car parks</b>, double glazing, 3 heat pumps + underfloor heating to bathrooms.")
B("<b>Implied rate:</b> &asymp; <b>$6,900/m&sup2;</b> at the ask — a clear penthouse premium over the rest of the building (standard 2-bed units list $789k–$850k). Defensible for the top-floor / dual-level / river-park aspect, but it is the building&rsquo;s price-setter, so there are no higher in-building comps to support it.")
B("<b>Yield:</b> <b>not a yield asset.</b> On an estimated ~$800–$900/week <font color='#9A2B2B'><b>[VERIFY — Rental Appraisal]</b></font>, gross yield &asymp; <b>2.8–3.2%</b> before body-corp and rates — typical of a trophy penthouse. The case is location, scarcity and capital quality, not cash-on-cash return.")
SP(3)
# recommendation callout
rec = Table([[Paragraph("<b>RECOMMENDATION</b>", ParagraphStyle("rk",parent=styles["cellh"],textColor=NAVY,fontSize=9)),
              Paragraph("<b>Proceed to Stage 2 due diligence.</b> Location plus the 100% NBS / full-refurb status materially de-risk the usual Christchurch-apartment concerns (seismic &amp; remediation). Before committing, resolve the four swing items: (i) <b>body-corporate financial health, LTMP &amp; levy</b>; (ii) <b>insurance — full replacement + EQ cover</b>; (iii) <b>rates &amp; RV</b>; and (iv) <b>whether it is already under offer</b> (a Harcourts duplicate shows a &ldquo;Sold&rdquo; tag — &sect;6). Recommend a <b>conditional offer</b> (LIM, BC records, builder&rsquo;s report, insurance, finance) at or modestly below the $1.449M ask, anchored to the in-building price ladder.", styles["cell"])]],
             colWidths=[26*mm, PAGE_W-LM-RM-26*mm])
rec.setStyle(TableStyle([("BACKGROUND",(0,0),(0,0),colors.HexColor("#FBF5E6")),
                         ("BACKGROUND",(1,1),(1,1),WHITE),
                         ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#FBF7EC")),
                         ("BOX",(0,0),(-1,-1),0.8,GOLD),
                         ("LINEAFTER",(0,0),(0,0),0.8,GOLD),
                         ("VALIGN",(0,0),(-1,-1),"TOP"),
                         ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
                         ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
story.append(rec)

# Section 2 snapshot
H2("2 &nbsp; Property snapshot")
snap = [
 ["Address","602/18 Carlton Mill Road, Merivale, Christchurch 8014","Confirmed"],
 ["Building","Kamahi Apartments (East &amp; West towers), 13 units","Web / agent"],
 ["Position","Penthouse, top (level 6) — two levels","Listing"],
 ["Floor area","~210 m&sup2;","realestate.co.nz"],
 ["Configuration","2 bed, 2 bath (master ensuite), separate study, laundry, open-plan upstairs lounge + dual balconies, wine storage","Listing"],
 ["Outdoor / parking","3 private decks (river + Hagley Park outlook); 2 secure underground car parks","Listing"],
 ["Services","3&times; heat pumps + wall heater; underfloor heating to bathrooms; full double glazing","Listing"],
 ["Tenure","Unit title (body corporate)","<font color='#9A2B2B'>[VERIFY — Title]</font>"],
 ["Asking","Offers Over $1,449,000","PropertyFiles"],
 ["AVM","HomesEstimate $1.43M–$1.6M @ 28 May 2026","homes.co.nz"],
 ["RV / CV","<font color='#9A2B2B'>[VERIFY — Rates Valuation]</font>","—"],
 ["Rates p.a.","<font color='#9A2B2B'>[VERIFY — Rates Valuation]</font>","—"],
 ["Body corp levy","<font color='#9A2B2B'>[VERIFY — BC financials / disclosure]</font>","—"],
 ["Rental appraisal","<font color='#9A2B2B'>[VERIFY — Rental Appraisal]</font>","—"],
]
story.append(make_table(["Attribute","Detail","Source / status"], snap, [30*mm, 108*mm, 36*mm]))

# Section 3 pricing
H2("3 &nbsp; Pricing &amp; valuation")
B("<b>Ask vs AVM.</b> $1,449,000 vs HomesEstimate $1.43M–$1.6M — ~1% above the bottom and ~10% below the top. AVMs are unreliable for unique penthouses (thin comp set); treat as a sanity check, not a value anchor.")
B("<b>$/m&sup2;.</b> &asymp; $6,900/m&sup2; (ask &divide; 210 m&sup2;). Prime new Christchurch product and refurbished Merivale stock typically transacts $6,000–$8,500/m&sup2; for premium floors; a renovated top-floor dual-level unit with river/park aspect and two car parks sits credibly in the upper half of that band.")
B("<b>In-building ladder.</b> 201/18 asking $789k (2bd/1ba/1 car); 401/18 and 2/18 EOI over ~$849k–$850k; 202/18, 301/18, 1/18 also listed. The penthouse at ~$1.45M is <b>~70–85% above</b> the standard 2-bed floors — a large but defensible premium given ~double the area, a second bathroom &amp; car park, the study, and the only two-level / top-floor / triple-deck configuration in the building.")
B("<b>Negotiation read.</b> &ldquo;Offers Over&rdquo; + a wide AVM + the bottom-of-range ask + a possible prior &ldquo;Sold&rdquo; flag suggest the vendor may be testing the market or re-listing. <b>Confirm live status first</b> (&sect;6) before spending on paid DD.")

# Section 4 building
H2("4 &nbsp; The building — Kamahi Apartments")
B("<b>Boutique scale:</b> only 13 units, predominantly <b>owner-occupied</b> — a positive for body-corp stability and building care.")
B("<b>Seismic:</b> total renovation and <b>earthquake strengthening to 100% NBS</b> — the single most important de-risking fact for a Christchurch apartment. <font color='#9A2B2B'><b>[VERIFY engineer&rsquo;s DEE / NBS rating in BC records &amp; LIM.]</b></font>")
B("<b>Configuration:</b> East and West towers, basement car parking, lift access, landscaped riverside courtyard garden, Avon River frontage, opposite Hagley Park.")
B("<b>Strategic fit.</b> Merivale + Carlton Mill Road riverfront is exactly the micro-location Citadel has been targeting (cf. the off-market 42–48 Carlton Mill Road holdings and the Liz Harris / Peterborough sites reviewed Jan–May 2026). This penthouse is the <i>finished-product</i> counterpart to that land thesis — useful as a standalone hold and as live market intelligence on achievable values/quality for the development sites.")

# Section 5 financials
H2("5 &nbsp; Financial &amp; holding analysis (indicative)")
fin = [
 ["Purchase price","$1,449,000","At ask; negotiate to ladder"],
 ["Gross rent (if let)","~$41,600–$46,800 p.a. (~$800–$900/wk)","<font color='#9A2B2B'>[VERIFY — Rental Appraisal]</font>"],
 ["Gross yield","~2.8–3.2%","Trophy level; sub-market for pure investment"],
 ["Council rates","<font color='#9A2B2B'>[VERIFY]</font>","Christchurch CC"],
 ["Body-corp levy","<font color='#9A2B2B'>[VERIFY]</font>","Driven by insurance + LTMP; small BC = higher per-unit fixed share"],
 ["Insurance","<font color='#9A2B2B'>[VERIFY]</font>","Confirm full replacement + EQ cover &amp; sum-insured adequacy"],
 ["Net yield (let)","&lt; gross by ~0.8–1.2%","After BC + rates + insurance + mgmt"],
]
story.append(make_table(["Item","Indicative","Notes"], fin, [34*mm, 52*mm, 88*mm]))
P("<b>Read:</b> as an investment the cash return is thin; the thesis is capital quality, scarcity and location. As an owner-occupied / part-time residence (consistent with the stated liking for the location after staying nearby on Carlton Mill Road), the yield question is secondary.")

# Section 6 comps + status
H2("6 &nbsp; Comparables &amp; live-status check")
B("<b>In-building (current/recent listings):</b> 201/18 — asking $789,000 (2bd/1ba/1 car); 401/18 — EOI over $849,000; 2/18 — EOI over $850,000; 202/18, 301/18, 1/18 — listed (gather sold prices).")
warn = Table([[Paragraph("&#9888;", ParagraphStyle("w",fontSize=14,textColor=RED,alignment=TA_CENTER)),
   Paragraph("<b>Live-status flag.</b> The Harcourts duplicate for 602/18 (PI66387) surfaced with an <b>&ldquo;Apartment Sold&rdquo;</b> tag, while Cowdy&rsquo;s PropertyFiles and realestate.co.nz still present it as available. Clarify with the agent <b>before</b> spending on DD — it may be under offer / conditional / recently sold, or the Harcourts record may be stale syndication.", styles["cell"])]],
   colWidths=[10*mm, PAGE_W-LM-RM-10*mm])
warn.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#FBEDED")),
   ("BOX",(0,0),(-1,-1),0.8,RED),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
   ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),8),
   ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
story.append(warn); SP(4)
P("<b>Action:</b> ask Cowdy (Rennie / Wieblitz) directly for (a) current status, (b) any existing conditional contract, (c) sold prices of the other 18 Carlton Mill units, and (d) days-on-market / price history since the 10 Feb 2026 launch.")

# Section 7 risks
H2("7 &nbsp; Risk register")
risk = [
 ["Already under offer / sold (Harcourts &ldquo;Sold&rdquo; tag)","High","Confirm live status with agent first"],
 ["Small 13-unit BC — high per-unit fixed cost, governance/key-person risk","Medium","Review BC accounts, LTMP, AGM minutes, reserves"],
 ["Insurance adequacy / EQ cover post-Canterbury","Med-High","Obtain policy; confirm full replacement + EQ sum insured"],
 ["Penthouse is the building price-setter (no higher comp)","Medium","Anchor to in-building ladder; conditional offer"],
 ["Thin rental yield (~3% gross)","Medium","Frame as lifestyle/capital asset, not income"],
 ["Latent remediation / leaks despite refurb","Medium","Builder&rsquo;s report; BC defect/maintenance history"],
 ["Liquefaction / flood overlay (riverfront)","Medium","LIM + LLUR + area geotech context"],
 ["Wide AVM range; &ldquo;Offers Over&rdquo; ambiguity","Low-Med","Negotiate; don&rsquo;t over-anchor to ask"],
]
story.append(make_table(["Risk","Severity","Mitigant / DD action"], risk, [82*mm, 22*mm, 70*mm]))

# Section 8 DD + next steps
H2("8 &nbsp; Due diligence &amp; next steps")
P("<b>Priority document review</b> (from the PropertyFiles register — gated pending registration): Title; LIM (strengthening/refurb consents + CCC sign-off, overlays); the full <b>Body Corporate pack</b> (AGM minutes 2022–25, financial accounts 2022–25, Long-Term Maintenance Plan, insurance policy, management contract, building rules, committee minutes 2015–25) — the key workstream; Pre-Contract Disclosure Statement; Rates Valuation; Rental Appraisal; LLUR enquiry; S&amp;P Agreement. <b>Independent:</b> builder&rsquo;s/weathertightness report, written insurance confirmation, and the engineering (DEE/seismic) report behind the 100% NBS claim.")
for i,t in enumerate([
  "<b>Call Cowdy</b> (Rennie / Wieblitz) — confirm live status, price history, conditions; request other-unit sold prices.",
  "<b>Register on PropertyFiles</b> and pull all listed documents.",
  "Stand up the <b>BC financial / LTMP / insurance review</b> (priority).",
  "Confirm <b>RV, rates, BC levy, rental appraisal</b> &rarr; finalise the numbers.",
  "If status is live and BC/insurance check out, <b>prepare a conditional offer</b> anchored to the in-building ladder.",
],1):
    story.append(Paragraph(t, styles["bullet"], bulletText=f"{i}."))

# Sources
H2("9 &nbsp; Sources")
P("<font size=7.6 color='#6B7884'>PropertyFiles RX4883894 · realestate.co.nz 42979106 · homes.co.nz (HomesEstimate) · Harcourts PI66387 (status) · Bayleys 201/18 (5515081) &amp; 401/18 (5529175) · Citadel internal (Drive): &ldquo;FW: Merivale Opportunity&rdquo; (Colliers, Jan–Mar 2026); briefing-inbox Carlton Mill task; 48 Carlton Mill Rd feasibility &amp; IM (Cowdy / Plus Architecture); Savills &ldquo;Liz Harris portfolio&rdquo; (Mar–May 2026). Web sources &amp; AVMs are indicative — confirm all financials against the PropertyFiles PDFs and Christchurch City Council records before offer.</font>")

# ---- build ---------------------------------------------------------------
doc = BaseDocTemplate("/tmp/Citadel_602-18-Carlton-Mill-Road_Workup.pdf", pagesize=A4,
                      leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                      title="Citadel Capital — 602/18 Carlton Mill Road Work-Up",
                      author="Citadel Capital Limited")
cover = PageTemplate(id="cover", frames=[Frame(LM, BM, PAGE_W-LM-RM, PAGE_H-TM-BM, id="c")], onPage=cover_bg)
main  = PageTemplate(id="main",  frames=[Frame(LM, BM, PAGE_W-LM-RM, PAGE_H-TM-BM, id="m")], onPage=header_footer)
doc.addPageTemplates([cover, main])
# cover is drawn by canvas; push a frame break to move to main template
from reportlab.platypus import NextPageTemplate, PageBreak
flow = [NextPageTemplate("main"), PageBreak()] + story
doc.build(flow)
print("OK built /tmp/Citadel_602-18-Carlton-Mill-Road_Workup.pdf")
