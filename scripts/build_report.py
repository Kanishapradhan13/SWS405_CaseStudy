import sys, csv, re; sys.path.insert(0, "scripts")
import report_text as R
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
d = Document()
sec = d.sections[0]; sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Inches(1)
st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.line_spacing = 1.5; st.paragraph_format.space_after = Pt(6)
for n, sz in (("Heading 1", 14), ("Heading 2", 12), ("Heading 3", 12)):
    h = d.styles[n]; h.font.name = "Times New Roman"; h.font.size = Pt(sz); h.font.bold = True; h.font.color.rgb = RGBColor(0, 0, 0)
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman"); h.paragraph_format.space_before = Pt(12)
d.styles["Heading 2"].font.italic = False
def para(text="", bold=False, italic=False, align=None, size=None, space=None):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if align is not None: p.alignment = align
    if space is not None: p.paragraph_format.line_spacing = space
    return p
def lead_para(text):
    # italicise a leading label such as "Gap." / "Design." if followed by sentence
    p = d.add_paragraph(); p.paragraph_format.first_line_indent = Inches(0.5)
    m = re.match(r"^((?:What [^.]*|Local context|Weaknesses of SMS OTPs|Social engineering of OTPs|SIM swapping|Mobile banking app security|Android forensics|Gap|Design|Sources|Scenario|Phone data|Acquisition and integrity|Analysis tools|Time handling|Ethics)\.)(.*)$", text, re.S)
    if m: r = p.add_run(m.group(1)); r.bold = True; p.add_run(m.group(2))
    else: p.add_run(text)
def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), color); tcPr.append(sh)
def table(cap, head, rows, widths=None, size=9.5):
    p = para(cap, bold=True, size=11, space=1.0); p.paragraph_format.keep_with_next = True
    t = d.add_table(rows=1, cols=len(head)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(head):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(size); shade(c, "D9E2F3")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(size)
    for row in t.rows:
        for c in row.cells:
            for pp in c.paragraphs: pp.paragraph_format.line_spacing = 1.0; pp.paragraph_format.space_after = Pt(2)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Inches(w)
    d.add_paragraph().paragraph_format.space_after = Pt(4)
def figure(path, cap, width=6.4):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Inches(width))
    c = para(cap, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=10.5, space=1.0)
def page_break(): d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
def footer_pagenum():
    p = sec.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if t: e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t)
        else: e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
        r._r.append(e)
footer_pagenum()

# ---- Title page
for _ in range(5): para("")
para("Reconstructing an OTP Scam from the Victim's Android Phone:", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER, space=1.2)
para("Mobile Banking Account Takeover in Bhutan, an Experiment with Test Data", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space=1.2)
para("")
para("Topic 1: OTP Scams and Mobile Banking Account Takeover", size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
for _ in range(3): para("")
for l in ["Group members: [Name 1, Student ID]  |  [Name 2, Student ID]  |  [Name 3, Student ID]", "Course: [Course code and title]", "Instructor: [Instructor name]", "Institution: [Institution name]", "Date: 19 November 2026"]:
    para(l, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space=1.2)
para(""); para("All persons, numbers, accounts and amounts in the experiment are fictitious test data.", italic=True, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
page_break()
# ---- Abstract
d.add_heading("Abstract", 1); p = d.add_paragraph(R.ABSTRACT)
para("Keywords: OTP fraud, mobile banking, account takeover, Android forensics, ALEAPP, Bhutan, SIM swap, digital evidence", italic=True, size=11)
page_break()
# ---- Body
for head, items in R.SECTIONS:
    d.add_heading(head, 1)
    for k, *c in items:
        if k == "p": lead_para(c[0])
        elif k == "h2": d.add_heading(c[0], 2)
        elif k == "bullets":
            for b in c[0]:
                p = d.add_paragraph(style="List Bullet"); m = re.match(r"^((?:RQ\d\.|[A-Z][A-Za-z ]{2,22}\.))(.*)$", b, re.S)
                if m and not b.startswith("RQ"): r = p.add_run(m.group(1)); r.bold = True; p.add_run(m.group(2))
                else: p.add_run(b)
        elif k == "fig": figure("report/figures/" + c[0], c[1])
        elif k == "table": table(c[1], c[2], c[3], widths={1:[1.7,0.9,0.9,3.0],2:[0.8,3.0,2.7],3:[3.0,3.5]}[c[0]])
    if head.startswith("4."):
        pass
# ---- References
page_break(); d.add_heading("References", 1)
for ref in R.REFERENCES:
    p = d.add_paragraph(ref); p.paragraph_format.left_indent = Inches(0.5); p.paragraph_format.first_line_indent = Inches(-0.5); p.paragraph_format.line_spacing = 1.15
# ---- Appendices
page_break(); d.add_heading("Appendices", 1)
d.add_heading("Appendix A. Complete merged timeline (46 events, Bhutan Time)", 2)
rows = list(csv.reader(open("analysis/master_timeline_BTT.csv")))
table("Table A1. analysis/master_timeline_BTT.csv", ["Time (BTT)", "Source", "Artefact", "Event"], [[r[0][11:], r[1], r[2], r[3][:120]] for r in rows[1:]], widths=[0.7, 0.9, 1.4, 3.5], size=7.5)
page_break()
d.add_heading("Appendix B. Evidence acquisition and integrity", 2)
para("The extraction folder was archived as victim_phone_extraction.tar; its SHA-256 is recorded below with per-file hashes. Hashes were recomputed after analysis and compared with diff: all 8 matched.", space=1.15)
figure("report/screens/term_acquisition.png", "Figure A1. Acquisition, SHA-256 hashing and post-analysis verification.", 6.4)
d.add_heading("Appendix C. Scenario script (fictitious)", 2)
table("Table C1. Ground-truth script used to generate the data", ["Time (BTT)", "Action", "Where it is recorded"],
 [["13:58:30","Scammer WhatsApp: prize message","Victim phone: WhatsApp"],["13:59:12","Victim: 'Really? What should I do?'","Victim phone: WhatsApp"],
  ["14:02:10","Unanswered WhatsApp call","Victim phone: WhatsApp call_log"],["14:03:45","GSM call from +97577000222, 372 s","Victim phone: call log"],
  ["14:04:48","Attacker requests registration OTP","Bank server"],["14:04:50","OTP #1 SMS (code 482913)","Victim phone: SMS, notification"],
  ["14:06:40","OTP #2 SMS (MPIN reset, 730158)","Victim phone: SMS, notification"],["14:08:02","New device bound","Bank server; SMS alert"],
  ["14:09:09 / 14:09:47","Transfers Nu 30,000 and Nu 19,950","Bank server; SMS alerts"],["14:10:20","Victim admits sharing code","Victim phone: WhatsApp"],
  ["14:13:15","Victim opens app: rejected","Mock app DB; UsageStats"],["14:16:20","Victim calls bank hotline","Victim phone: call log"]], widths=[1.2,3.0,2.3], size=9)
d.add_heading("Appendix D. Tool outputs", 2)
figure("report/screens/term_aleapp.png", "Figure D1. ALEAPP run and exported TSV files. Browser and SQLCipher modules were unavailable and are irrelevant to this data.", 6.2)
figure("report/screens/term_sqlite.png", "Figure D2. SQLite examination of the mock bank database and SMS store (equivalent to browsing the tables in DB Browser for SQLite).", 6.2)
figure("report/screens/aleapp_SMS_Messages.png", "Figure D3. ALEAPP report: SMS messages (times shown in UTC; Bhutan Time is UTC+6).", 5.6)
figure("report/screens/aleapp_Call_logs_.png", "Figure D4. ALEAPP report: call logs.", 5.6)
figure("report/screens/aleapp_WhatsApp_-_One_To_One_Messages.png", "Figure D5. ALEAPP report: WhatsApp one-to-one messages.", 5.6)
figure("report/screens/aleapp_Usage_Stats.png", "Figure D6. ALEAPP report: usage statistics (protobuf event log).", 5.6)
d.add_heading("Appendix E. Mock banking app schema and reproduction steps", 2)
para("MockBank (mockbank-app/, Kotlin) keeps four tables in databases/mockbank.db: auth_events(ts_ms, event, device_id, result), otp_log(ts_ms, purpose, otp_hash, delivered_to), device_bindings(device_id, model, bound_ts_ms, active) and transactions(ts_ms, direction, amount_nu, counterparty, balance_after). The app source was written but not compiled in this study.", space=1.15)
para("To reproduce: (1) python3 scripts/build_evidence.py evidence/victim_phone_extraction; (2) tar and hash the folder; (3) python aleapp.py -t fs -i evidence/victim_phone_extraction -o analysis; (4) python3 scripts/build_timeline.py; (5) python3 scripts/make_figures.py. With a real emulator, step 1 is replaced by installing MockBank and WhatsApp, performing the scenario, and pulling /data/data and /data/system with adb as root.", space=1.15)
d.save("report/Bhutan_OTP_Scam_Forensics_Report.docx"); print("saved")
