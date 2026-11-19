import copy, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

TPL = "CST_PPT_Template(Widescreen-16-9) Version 2.pptx"
OUT = "presentation/OTP_Scam_Forensics_Presentation.pptx"
BLUE, DK2, ACC, LT, TEAL, ORG, WHITE, INK = "0432FF", "17406D", "0F6FC6", "DBEFF9", "125463", "C2570C", "FFFFFF", "1F2937"
rgb = lambda h: RGBColor.from_string(h)
prs = Presentation(TPL)
# drop the template's example slides
for sid in list(prs.slides._sldIdLst):
    prs.part.drop_rel(sid.rId); prs.slides._sldIdLst.remove(sid)
L = {l.name: l for l in prs.slide_layouts}

def tb(s, x, y, w, h, text, size=16, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, name=None, italic=False):
    t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = t.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.03); tf.vertical_anchor = anchor
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        r = p.add_run(); r.text = ln; r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic; r.font.color.rgb = rgb(color); r.font.name = "Arial"
    if name: t.name = name
    return t
def card(s, x, y, w, h, fill=LT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, name=None, line=None):
    c = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h)); c.fill.solid(); c.fill.fore_color.rgb = rgb(fill)
    if line: c.line.color.rgb = rgb(line); c.line.width = Pt(1.25)
    else: c.line.fill.background()
    c.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: c.adjustments[0] = 0.06
    if name: c.name = name
    return c
def bullets(s, x, y, w, h, items, size=15, color=INK, gap=6, name=None):
    t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = t.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.space_after = Pt(gap)
        pPr = p._p.get_or_add_pPr(); pPr.set("marL", "228600"); pPr.set("indent", "-228600")
        bu = pPr.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}buChar", {"char": "•"}); pPr.append(bu)
        r = p.add_run(); r.text = it; r.font.size = Pt(size); r.font.color.rgb = rgb(color); r.font.name = "Arial"
    if name: t.name = name
    return t
def pic(s, path, x, y, w=None, h=None, name=None):
    im = Image.open(path); ar = im.width / im.height
    if w and h:
        if w / h > ar: w = h * ar
        else: h = w / ar
    elif w: h = w / ar
    else: w = h * ar
    p = s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    if name: p.name = name
    return p, w, h
def table(s, x, y, w, colw, head, rows, size=14, rowh=0.62, headfill=DK2):
    gt = s.shapes.add_table(len(rows) + 1, len(head), Inches(x), Inches(y), Inches(w), Inches(rowh * (len(rows) + 1)))
    t = gt.table; tblPr = t._tbl.tblPr; tblPr.set("bandRow", "0"); tblPr.set("firstRow", "1")
    for i, cw in enumerate(colw): t.columns[i].width = Inches(cw)
    def setc(c, txt, bold=False, color=INK, fill=None):
        c.text = ""; tf = c.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]; r = p.add_run(); r.text = txt
        r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = rgb(color); r.font.name = "Arial"
        c.margin_left = c.margin_right = Inches(0.1); c.margin_top = c.margin_bottom = Inches(0.05); c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.fill.solid(); c.fill.fore_color.rgb = rgb(fill or WHITE)
    for i, h in enumerate(head): setc(t.cell(0, i), h, True, WHITE, headfill)
    for ri, row in enumerate(rows, 1):
        for ci, v in enumerate(row): setc(t.cell(ri, ci), v, ci == 0, INK, LT if ri % 2 else WHITE)
    for r in t.rows: r.height = Inches(rowh)
    t.rows[0].height = Inches(0.5)
    return gt
def addnum(s, layout):
    for ph in layout.placeholders:
        if ph.placeholder_format.idx == 12: s.shapes._spTree.append(copy.deepcopy(ph._element))
SPK = {1: "Speaker 1", 2: "Speaker 2", 3: "Speaker 3"}
def content(title, spk, notes):
    s = prs.slides.add_slide(L["Title Only"]); s.shapes.title.text = title
    addnum(s, L["Title Only"])
    tb(s, 10.9, 0.17, 2.2, 0.45, f"{SPK[spk]}", 14, True, WHITE, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE, name="Speaker tag")
    s.notes_slide.notes_text_frame.text = notes
    return s

# ---------- 1 Title
s = prs.slides.add_slide(L["Title Slide"])
s.shapes.title.text = "Reconstructing an OTP Scam from the Victim's Android Phone"
s.placeholders[1].text = "Mobile banking account takeover in Bhutan\nTopic 1 case study  |  [Member names]  |  19 November 2026"
s.notes_slide.notes_text_frame.text = ("[Speaker 1, 0:30] Good morning. Our topic is OTP scams and mobile banking account takeover. We recreated one such scam with fictitious data and asked a simple question the police ask: what can the victim's phone prove, and when? "
 "Our team has three speakers. Speaker 1 covers the problem, research questions, literature and the attack flow. Speaker 2 covers method, demo and the timeline. Speaker 3 covers findings, bank responses, recommendations and conclusion.")

# ---------- 2 Problem
s = content("A prize call, two OTPs, an empty account", 1,
 "[Speaker 1, 45 s] The story: a caller tells a woman she has won a prize, gets her to read out an SMS code, and within minutes her banking app is on another phone and her account is empty. "
 "This is not rare. The Royal Bhutan Police recorded 35 scam cases in the first three months of 2026, involving more than Nu 5.4 million. Only about Nu 830,000, roughly 15 percent, had been recovered. Sixteen of the 35 were email-compromise or SIM-replacement 'blackout' cases; the rest included lottery prizes and OTP sharing. Police then ask what the phone can prove.")
for i, (big, lab) in enumerate([("35", "scam cases recorded by the RBP in Jan to Mar 2026"), ("Nu 5.4 M", "involved in those cases"), ("about 15%", "recovered so far (Nu 830,000)")]):
    x = 0.92 + i * 3.9; card(s, x, 1.85, 3.65, 2.3, name=f"Stat card {i+1}")
    tb(s, x + 0.15, 2.0, 3.35, 1.1, big, 44, True, ACC, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, name=f"Stat {i+1}")
    tb(s, x + 0.15, 3.1, 3.35, 0.95, lab, 16, False, INK, name=f"Stat label {i+1}")
card(s, 0.92, 4.45, 11.5, 1.75, fill=DK2, name="Story card")
tb(s, 1.15, 4.55, 11.05, 1.55, ["She is told she won a prize, reads out an SMS code, and minutes later her banking app is on another phone.", "Police ask: what can her phone prove?"], 18, False, WHITE, anchor=MSO_ANCHOR.MIDDLE, name="Story")
tb(s, 0.92, 6.35, 11.5, 0.45, "Source: BBS (2026), Email fraud and mobile blackout scams rising, say police", 12, False, "475569", name="Source")

# ---------- 3 RQs
s = content("Three research questions", 1,
 "[Speaker 1, 30 s] We organised the study around three questions. RQ1: what steps do these scams follow in Bhutan and where does each step leave a trace? RQ2: which artefacts on the victim's Android phone can rebuild the timeline, and which steps leave nothing on the phone? RQ3: what have Bhutanese banks and telecoms changed, and what gaps remain? We answer RQ1 with the attack flow, RQ2 with the experiment and timeline, and RQ3 with the findings and recommendations.")
rq = [("RQ1", "Steps and traces", "What steps do OTP scams follow in Bhutan, and where does each step leave digital traces?", "Answered on slide 5"),
      ("RQ2", "Phone artefacts", "Which artefacts on the victim's Android phone (SMS, call log, WhatsApp, notifications, app usage) can rebuild the timeline?", "Answered on slides 7 to 10"),
      ("RQ3", "What changed", "What have Bhutanese banks changed since these scams began, and what gaps remain?", "Answered on slides 11 and 12")]
for i, (n, h, q, a) in enumerate(rq):
    x = 0.92 + i * 3.9; card(s, x, 1.85, 3.65, 4.7, name=f"RQ card {i+1}")
    c = card(s, x + 0.2, 2.05, 1.1, 0.62, fill=ACC, name=f"RQ badge {i+1}", shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tb(s, x + 0.2, 2.05, 1.1, 0.62, n, 20, True, WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, name=f"RQ id {i+1}")
    tb(s, x + 0.2, 2.85, 3.25, 0.5, h, 20, True, DK2, name=f"RQ head {i+1}")
    tb(s, x + 0.2, 3.45, 3.25, 2.2, q, 16, False, INK, name=f"RQ text {i+1}")
    tb(s, x + 0.2, 5.9, 3.25, 0.45, a, 14, True, ORG, name=f"RQ where {i+1}")

# ---------- 4 Literature
s = content("What the research says", 1,
 "[Speaker 1, 60 s] We reviewed seven peer-reviewed papers plus NIST guidance. Mulliner and colleagues showed SMS is not a secure channel. Siadati and colleagues found a code-forwarding attack succeeded 50 percent of the time against a standard SMS message, and about 8 percent with a redesigned message. Lee and colleagues tested five prepaid carriers and found all five used SIM-swap checks an attacker could subvert, and 17 websites could be compromised by a SIM swap alone. That matches the blackout cases the RBP describes. Reaves and colleagues examined 46 Android mobile-money apps and found pervasive vulnerabilities. Anglano and Azfar show that WhatsApp and other apps leave recoverable databases, which justifies our ALEAPP approach. For Bhutan we found news and police reports but no peer-reviewed study, and none that reconstructs a takeover from the victim's phone.")
table(s, 0.92, 1.75, 11.5, [2.6, 5.0, 3.9], ["Study", "Finding", "Why it matters here"],
 [["Mulliner et al. (2013)", "SMS is not a secure channel; handset malware can read OTPs", "An OTP proves only channel access"],
  ["Siadati et al. (2017)", "Code-forwarding attack: 50% success; redesigned message about 8%", "OTP message wording matters"],
  ["Lee et al. (2020)", "5 of 5 prepaid carriers' SIM-swap checks subvertable; 17 sites fall to a SIM swap alone", "Explains Bhutan's 'blackout' scams"],
  ["Reaves et al. (2017)", "46 Android mobile-money apps: pervasive flaws; liability on customers", "Weak apps, thin logs"],
  ["Anglano (2014); Azfar et al. (2016)", "WhatsApp and 30 comms apps leave recoverable databases", "Justifies an ALEAPP-based method"]], size=14, rowh=0.8)
tb(s, 0.92, 6.4, 11.5, 0.45, "Gap: no peer-reviewed Bhutan study, and none that rebuilds a takeover from the victim's handset.", 14, True, ORG, name="Gap")

# ---------- 5 Attack flow
s = content("Attack flow: eight steps, seven leave a trace", 1,
 "[Speaker 1, 50 s] RQ1. From Bhutanese reports we modelled eight steps. One: a WhatsApp lure about a lucky draw. Two: a phone call that builds urgency. Three: the scammer starts a device registration on their own phone, which triggers OTP number one. Four: the victim reads the code aloud. Five: a second OTP for an MPIN reset. Six: the banking app is bound to the attacker's device. Seven: two transfers empty the account. Eight: the cover story, 'do not tell anyone', and the victim's discovery. Every step leaves a trace on the phone or at the bank except step four, shown in red: the spoken disclosure leaves nothing on the phone.")
p, w, h = pic(s, "report/figures/fig1_attack_flow.png", 0, 0, w=11.5, h=5.1, name="Attack flow figure")
p.left = Inches(0.92 + (11.5 - w) / 2); p.top = Inches(1.75)
tb(s, 0.92, 6.45, 11.5, 0.4, "Red box: the only step with no direct artefact on the phone.", 12, False, "475569", PP_ALIGN.CENTER, name="Figure caption")

# ---------- 6 Method
s = content("Method: from a fake phone to a timeline", 2,
 "[Speaker 2, 45 s] Our method has six steps. We build a victim phone image from fictitious data using real Android database layouts: SMS, call log, WhatsApp, a usage-statistics protobuf, notifications and our mock banking app. We archive it and record SHA-256 hashes. ALEAPP parses it read-only; SQLite examines the mock bank database; a script merges everything into one Bhutan-time timeline; and we derive recommendations. Please note the honest scope: we could not download an Android emulator image on the connection available, so this is a schema-faithful synthetic image, Autopsy was not run, and the mock app source was written but not compiled.")
steps = [("1", "Build test phone image", "Python script, real Android schemas"), ("2", "Acquire and hash", "tar + SHA-256, re-checked after"), ("3", "Parse with ALEAPP", "SMS, calls, WhatsApp, usage"),
         ("4", "Examine with SQLite", "Mock bank database"), ("5", "Merge timeline", "46 events, Bhutan Time"), ("6", "Recommend", "Victims, banks, telecoms")]
for i, (n, h, d) in enumerate(steps):
    x = 0.92 + i * 1.94; card(s, x, 1.85, 1.82, 2.55, name=f"Step card {i+1}")
    card(s, x + 0.12, 1.97, 0.5, 0.5, fill=ACC, shape=MSO_SHAPE.OVAL, name=f"Step badge {i+1}"); tb(s, x + 0.12, 1.97, 0.5, 0.5, n, 16, True, WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, name=f"Step no {i+1}")
    tb(s, x + 0.08, 2.6, 1.68, 0.85, h, 15, True, DK2, name=f"Step head {i+1}"); tb(s, x + 0.08, 3.45, 1.68, 0.9, d, 13, False, INK, name=f"Step text {i+1}")
card(s, 0.92, 4.7, 11.5, 1.9, fill=WHITE, line=ORG, name="Scope card")
tb(s, 1.12, 4.78, 11.1, 0.4, "Honest scope", 16, True, ORG, name="Scope head")
bullets(s, 1.12, 5.2, 11.1, 1.4, ["No emulator: a 1.5 GB image could not be downloaded at about 60 KB/s, so the phone image is synthetic but schema-faithful", "Autopsy not run; DB Browser replaced by the sqlite3 client; mock app written in Kotlin but not compiled", "All people, numbers and amounts are fictitious test data"], 14, INK, 3, name="Scope list")

# ---------- 7 Demo
s = content("Demo: acquire, verify, analyse", 2,
 "[Speaker 2, 60 s, play the demo clip here] This is the demo. On the left, the evidence image is archived and each file is hashed; after analysis we recomputed the hashes and all eight matched, so the analysis did not change the evidence. Below it, the mock bank database examined with SQLite: at 14:13:15 the victim's device is rejected as unbound, and her MPIN no longer works. On the right, ALEAPP's report of the SMS inbox: the first OTP arrives at 14:04:50 Bhutan time; ALEAPP displays UTC, which is six hours behind. The 2 minute 39 second demo video is in the demo folder; play about the first minute here and offer the rest in Q and A.")
a, w1, h1 = pic(s, "report/screens/term_acquisition.png", 0.92, 1.75, w=5.75, name="Acquisition terminal")
b, w2, h2 = pic(s, "report/screens/term_sqlite.png", 0.92, 1.75 + h1 + 0.2, w=5.75, name="SQLite terminal")
c, w3, h3 = pic(s, "report/screens/aleapp_SMS_Messages.png", 6.9, 1.75, w=5.5, name="ALEAPP SMS screenshot")
tb(s, 6.9, 1.75 + h3 + 0.1, 5.5, 0.9, ["ALEAPP SMS report: OTP #1 at 08:04:50 UTC = 14:04:50 Bhutan Time", "Demo video: demo/OTP_Scam_Forensics_Demo.mp4"], 13, False, "334155", name="Demo captions")

# ---------- 8 Artefacts
s = content("Artefacts recovered and what each proves", 2,
 "[Speaker 2, 40 s] RQ2. This table lists what we recovered. SMS gives the arrival time of both OTPs, the new-device alert and both debit alerts. The call log gives the 372-second call from the same number that sent the WhatsApp lure. WhatsApp gives the lure, the instructions and the victim's later admission. Usage statistics show the dialer in the foreground during the call and the banking app opened only at 14:13. Notifications show OTP text displayed within a second. The mock bank database shows her device rejected as unbound. The last row is not on the phone: the bank's server log, which we simulated, is the only source for the attacker's device and address.")
table(s, 0.92, 1.75, 11.5, [3.0, 0.9, 7.6], ["Artefact", "Items", "What it establishes"],
 [["SMS (mmssms.db)", "5", "Both OTPs, new-device alert and both debits, with times"],
  ["Call log (calllog.db)", "3", "Incoming call 14:03:45 from scammer, 372 s; call to bank 14:16:20"],
  ["WhatsApp (msgstore.db)", "7 + 1", "Lure 13:58:30; victim's admission 14:10:20; warning to a friend"],
  ["UsageStats (protobuf)", "12", "Dialer in foreground during the call; banking app only at 14:13:15"],
  ["Notification log", "6", "OTP text visible on screen within 1 s of arrival"],
  ["MockBank database", "6", "Victim's device rejected as unbound at 14:13:15"],
  ["Bank server log (off phone)", "7", "Attacker device and IP, OTP verification times, transfers"]], size=14, rowh=0.62)

# ---------- 9 Timeline
s = content("Minute-by-minute timeline (Bhutan Time)", 2,
 "[Speaker 2, 60 s] This swim-lane chart merges 46 events from all sources. The shaded band is the scam call, 14:03:45 to about 14:09:57. Inside it you can see the first OTP at 14:04:50, 65 seconds after the call began; the second at 14:06:40; the new-device alert at 14:08:02; and both debits at 14:09:10 and 14:09:48. The bank-side row, in red at the bottom, shows another device verifying each code 45 and 70 seconds after delivery. After the call: the victim's admission at 14:10:20, her first app open at 14:13:15 where she is rejected, a message to a friend, and a call to the bank at 14:16:20.")
p, w, h = pic(s, "report/figures/fig2_timeline.png", 0, 0, w=11.5, h=4.6, name="Timeline figure")
p.left = Inches(0.92 + (11.5 - w) / 2); p.top = Inches(1.75)
tb(s, 0.92, 6.3, 11.5, 0.6, "The scam call (14:03:45 to 14:09:57) overlaps OTP #1, OTP #2, the new-device alert and both debits.", 15, True, DK2, name="Timeline takeaway")

# ---------- 10 Findings
s = content("What the phone proves, and what it cannot", 3,
 "[Speaker 3, 60 s] Four numbers summarise the speed: the call lasted 372 seconds; the first OTP arrived 65 seconds into it; cash-out began 67 seconds after the new device was bound; and from the first OTP request to the last debit took five minutes. On the right: the phone proves the lure, the overlap of the call with both OTPs and both debits, the alerts, and that the victim was not using her banking app while the money left. It cannot prove the spoken disclosure, nor which device used the code, nor where the money went. Those need the bank's and the telecom's logs.")
stats = [("372 s", "scam call length"), ("65 s", "call start to OTP #1"), ("67 s", "new device to first transfer"), ("5 min", "first OTP request to last debit")]
for i, (big, lab) in enumerate(stats):
    x = 0.92 + (i % 2) * 2.7; y = 1.85 + (i // 2) * 2.4; card(s, x, y, 2.55, 2.2, name=f"Stat card {i+1}")
    tb(s, x + 0.1, y + 0.15, 2.35, 1.0, big, 38, True, ACC, anchor=MSO_ANCHOR.MIDDLE, name=f"Stat {i+1}"); tb(s, x + 0.1, y + 1.2, 2.35, 0.9, lab, 15, False, INK, name=f"Stat label {i+1}")
card(s, 6.5, 1.85, 5.92, 2.45, fill=LT, name="Proves card"); tb(s, 6.7, 1.92, 5.5, 0.4, "The phone proves", 18, True, DK2, name="Proves head")
bullets(s, 6.7, 2.4, 5.55, 1.9, ["The lure and the 372 s call from the same number", "Both OTPs and both debits arrived during the call", "The victim was not using her banking app", "Her later admission: 'ok sir i gave the code'"], 16, INK, 6, name="Proves list")
card(s, 6.5, 4.5, 5.92, 2.25, fill=WHITE, line=ORG, name="Cannot card"); tb(s, 6.7, 4.57, 5.5, 0.4, "It cannot prove (needs bank or telecom logs)", 16, True, ORG, name="Cannot head")
bullets(s, 6.7, 5.0, 5.55, 1.7, ["That she read the codes aloud (inferred from overlap)", "Which device and IP used the OTPs", "Where the money went"], 16, INK, 6, name="Cannot list")

# ---------- 11 Banks
s = content("RQ3: Bhutan's response and the gaps", 3,
 "[Speaker 3, 50 s] What has changed? Banks reported disabling in-app MPIN and device resets, so customers must call or visit the bank. Banks send bulk SMS warnings, and the RMA advises people not to lend, share or rent accounts. Bhutan National Bank says disputed amounts are frozen on report and reimbursed after investigation. Bhutan Telecom offers SIM retention for up to three years for people abroad, and police, RMA and GovTech are studying de-linking email from bank accounts. The gaps our experiment suggests: any remaining registration path can still be abused; warnings sit beside the code but do not say what it does; speed decides the outcome, since the money left in five minutes while recovery is about 15 percent; and there is no public SIM-replacement verification standard.")
table(s, 0.92, 1.75, 11.5, [5.0, 6.5], ["Response reported", "Gap our experiment suggests"],
 [["In-app MPIN and device resets disabled (BBS, n.d.)", "Any remaining registration path can still bind a new device"],
  ["Bulk SMS and press warnings; RMA advice not to share accounts", "Warning sits beside the code; it does not say what the code does"],
  ["Freeze and reimburse after a report (BNB)", "Money left in 5 min; recovery about 15% in early 2026"],
  ["SIM retention up to 3 years (Bhutan Telecom)", "No public SIM-replacement verification standard; blackout cases continue"],
  ["Email de-linking under study (RBP, RMA, GovTech)", "Not yet reported as implemented"]], size=14, rowh=0.8)

# ---------- 12 Recommendations
s = content("Recommendations", 3,
 "[Speaker 3, 50 s] For victims: keep the phone on and unchanged; do not reset, uninstall or delete anything; call the bank at once to freeze the account; photograph the SMS, call log and chats; do not call the scammer back; report to the RBP and let them take a forensic copy. For banks: log OTP requests and verifications, device and installation identifiers, IP, and binding events on a synchronised clock; write purpose into the OTP message, for example 'code for NEW DEVICE'; and add a delay and a lower transfer limit after any new-device binding, with a push alert to the old device. For telecoms: log SIM-replacement requests and the identity checks done, delivery receipts for bank sender IDs and call records, and let banks query recent SIM changes.")
cols = [("Victims: preserve now", ["Keep the phone on; do not reset or delete", "Call the bank to freeze the account", "Photograph SMS, call log and chats", "Report to the RBP; offer the handset"]),
        ("Banks: log and limit", ["Log OTP, device, IP and binding events", "Purpose-bearing OTP text", "Delay and lower limits after a new device", "Push alert to the old device"]),
        ("Telecoms: log", ["SIM-replacement checks and agent", "SMS delivery receipts for bank IDs", "Call detail records, set retention", "Recent-SIM-change check for banks"])]
for i, (h, items) in enumerate(cols):
    x = 0.92 + i * 3.9; card(s, x, 1.85, 3.65, 4.85, name=f"Rec card {i+1}")
    tb(s, x + 0.2, 2.0, 3.25, 0.7, h, 19, True, DK2, name=f"Rec head {i+1}")
    bullets(s, x + 0.2, 2.8, 3.3, 3.8, items, 18, INK, 14, name=f"Rec list {i+1}")

# ---------- 13 Conclusion
s = content("Conclusion and limits", 3,
 "[Speaker 3, 40 s, then Q and A] To conclude: an OTP-sharing takeover leaves a thin but usable trail on the victim's phone. It establishes the lure, the call overlap, the alerts and the victim's absence from her app, but not the spoken disclosure or the attacker's device. Victims must act fast and preserve; banks and telecoms must log device-level events. The limits: synthetic data, no live emulator, WhatsApp messages inserted rather than exchanged, Autopsy not run. Next step: repeat on a real Android emulator. Thank you; we are happy to take questions.")
card(s, 0.92, 1.85, 5.65, 3.65, name="Conclusion card"); tb(s, 1.12, 1.95, 5.25, 0.45, "Conclusions", 20, True, DK2, name="Conclusion head")
bullets(s, 1.12, 2.5, 5.3, 2.95, ["The phone shows the lure, call overlap, alerts and the victim's absence from her app", "The spoken OTP and the attacker's device need bank and telecom logs", "Speed and message design decide the outcome"], 15, INK, 8, name="Conclusion list")
card(s, 6.77, 1.85, 5.65, 3.65, fill=WHITE, line=ORG, name="Limits card"); tb(s, 6.97, 1.95, 5.25, 0.45, "Limits and next steps", 20, True, ORG, name="Limits head")
bullets(s, 6.97, 2.5, 5.3, 2.95, ["Synthetic image, no live emulator; WhatsApp messages inserted", "Autopsy not run; mock app not compiled", "Next: repeat on a real emulator with live WhatsApp traffic and the SIM-replacement variant"], 15, INK, 8, name="Limits list")
card(s, 0.92, 5.75, 11.5, 0.95, fill=DK2, name="QA card"); tb(s, 0.92, 5.75, 11.5, 0.95, "Thank you. Questions?", 28, True, WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, name="QA text")
prs.save(OUT); print("saved", OUT, len(prs.slides))
