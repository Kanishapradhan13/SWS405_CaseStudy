import sys, os, subprocess, glob, math
sys.path.insert(0, "scripts"); import term
from PIL import Image, ImageDraw, ImageFont
W, H = 1920, 1080
OUT = "demo/_build"; os.makedirs(OUT, exist_ok=True)
FB = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 46)
FR = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 30)
FS = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
def frame(title, narr, content=None, bullets=None, big=None, fit=(1760, 800)):
    im = Image.new("RGB", (W, H), "#0f172a"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 92], fill="#1e293b"); d.text((50, 22), title, font=FB, fill="#f8fafc")
    d.text((W - 640, 36), "OTP scam forensics | test data only", font=FS, fill="#94a3b8")
    y0 = 112
    if content is not None:
        c = Image.open(content) if isinstance(content, str) else content
        s = min(fit[0] / c.width, fit[1] / c.height); c = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
        im.paste(c, ((W - c.width) // 2, y0 + (fit[1] - c.height) // 2 if c.height < fit[1] else y0))
    if big: 
        for i, l in enumerate(big): d.text((120, 300 + i * 90), l, font=ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 64 if i == 0 else 40), fill="#f8fafc" if i == 0 else "#cbd5e1")
    if bullets:
        for i, b in enumerate(bullets):
            ls = wrap(d, b, FR, 1650); yy = 160 + i * 140
            d.ellipse([90, yy + 12, 110, yy + 32], fill="#38bdf8")
            for j, l in enumerate(ls): d.text((135, yy + j * 40), l, font=FR, fill="#e2e8f0")
    d.rectangle([0, H - 150, W, H], fill="#020617")
    for j, l in enumerate(wrap(d, narr, FS, 1780)[:3]): d.text((60, H - 135 + j * 40), l, font=FS, fill="#fde68a")
    return im
scenes = []
def scene(name, narr, **kw): scenes.append((name, narr, kw))
scene("s01", "This demonstration recreates an OTP scam and shows what the victim's Android phone can prove. Everything you see uses fictitious test data.", big=["Reconstructing an OTP scam", "from the victim's Android phone", "", "Bhutan case study | Topic 1 | all data fictitious"])
scene("s02", "The scenario: a caller says the victim won a prize, makes her read out two bank OTPs, and the banking app is bound to another phone. Minutes later the account is empty. We ask what the phone can prove.",
      bullets=["Lure on WhatsApp at 13:58, then a 6 minute 12 second phone call at 14:03", "Two OTP text messages arrive during the call, at 14:04 and 14:06", "Account bound to a new device at 14:08, Nu 49,950 transferred out by 14:09", "RQ1 steps and traces  |  RQ2 which phone artefacts  |  RQ3 what banks changed"])
scene("s03", "From Bhutanese news and police reports we modelled the attack as eight steps. Seven leave a trace. The spoken disclosure of the OTP, step four, leaves none on the phone.", content="report/figures/fig1_attack_flow.png")
T = {}
import subprocess as sp
def sh(c): return sp.run(c, shell=True, capture_output=True, text=True).stdout.rstrip("\n").split("\n")
t1 = ["$ python3 scripts/build_evidence.py evidence/victim_phone_extraction", "built evidence/victim_phone_extraction", "$ shasum -a 256 victim_phone_extraction.tar"] + sh("cat evidence/acquisition_sha256.txt") + ["$ shasum -a 256 each extracted file"] + sh("cut -c1-24,65- evidence/file_hashes.txt") + ["$ re-hash after analysis and diff", "ALL 8 FILE HASHES MATCH"]
scene("s04", "We generate the phone image with genuine Android database schemas, archive it, and record SHA-256 hashes. After analysis the hashes are recomputed. All eight match, so the evidence was not altered.", term=(t1, "acquisition and hashing"))
t2 = open("analysis_run.log").read().split("\n")
t2 = ["$ python aleapp.py -t fs -i evidence/victim_phone_extraction -o analysis"] + [l for l in t2 if any(k in l for k in ("Processes completed", "Report generation", "Report location"))] + ["", "$ ls _TSV Exports"] + sh("ls analysis/ALEAPP_Output_*/_TSV*")
scene("s05", "ALEAPP parses the image read-only and produces reports for SMS, call logs, WhatsApp and app usage.", term=(t2, "ALEAPP"))
scene("s06", "SMS inbox: the first OTP arrives at 14:04:50 Bhutan time, the second at 14:06:40. ALEAPP shows UTC, which is six hours behind.", content="report/screens/aleapp_SMS_Messages.png")
scene("s07", "Call log: an incoming call from the same number that sent the WhatsApp lure, lasting 372 seconds. Both OTPs and both debits fall inside it.", content="report/screens/aleapp_Call_logs_.png")
scene("s08", "WhatsApp: the prize lure, the scammer's instructions, and the victim's later message admitting she gave the code.", content="report/screens/aleapp_WhatsApp_-_One_To_One_Messages.png")
scene("s09", "Usage statistics: the dialer is in the foreground during the call, and the banking app is opened only at 14:13, after the money has gone. So the transfers did not come from her phone.", content="report/screens/aleapp_Usage_Stats.png")
t3 = [l for l in open("scripts/_sqlite_lines.txt").read().split("\n")]
scene("s10", "The mock banking app database, examined with SQLite, shows her device was rejected as unbound at 14:13:15 and her MPIN no longer worked. The binding record carries the time of the next app open, not the real revocation time.", term=(t3, "SQLite examination"))
scene("s11", "All sources merge into one forty-six event timeline. The scam call overlaps both codes and both debits. The bank's server log, which is off the phone, shows another device verified each code within seventy seconds.", content="report/figures/fig2_timeline.png")
scene("s12", "Findings. Cash-out began sixty-seven seconds after the new device was bound. The phone proves the lure, the call overlap, the alerts and the victim's absence from her app. It cannot prove who used the code, or that she read it aloud.",
      bullets=["First OTP request to last debit: 5 min 0 s  |  67 s from new-device binding to first transfer", "Phone proves: lure, call overlap, OTP and debit alerts, victim not using her app, her later admission", "Phone cannot prove: spoken disclosure, attacker device and IP, where the money went", "Bank and telecom logs are needed to close the gap"])
scene("s13", "Recommendations. Victims should keep the phone unchanged, call the bank to freeze the account, photograph screens and report to police. Banks should log device and OTP events, state the purpose in the OTP message, and add a cooling-off limit after new-device binding. Telecoms should log SIM replacements.",
      bullets=["Victim: do not reset or delete, call bank, screenshot SMS, calls and chats, report to RBP", "Banks: log OTP, device, IP and binding events; purpose-bearing OTP text; delay and limits after rebinding", "Telecoms: log SIM-replacement checks, delivery receipts and call records", "Limits: synthetic data, no live emulator, Autopsy not run"])
scene("s14", "Thank you. The full report, scripts, evidence hashes and this demo are in the project folder.", big=["Thank you", "Report, scripts, evidence and timeline: casestudy folder", "Questions?"])
# ---- render
clips = []
for name, narr, kw in scenes:
    aiff = f"{OUT}/{name}.aiff"; sp.run(["say", "-v", "Samantha", "-r", "170", "-o", aiff, narr], check=True)
    dur = float(sp.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", aiff], capture_output=True, text=True).stdout) + 0.8
    if "term" in kw:
        lines, ttl = kw.pop("term"); n = len(lines); steps = min(n, 12); imgs = []
        for k in range(1, steps + 1):
            cnt = math.ceil(n * k / steps); term.render(lines, f"{OUT}/{name}_t{k}.png", ttl, upto=cnt, w=1500, fs=21)
            imgs.append(frame(ttl, narr, content=f"{OUT}/{name}_t{k}.png", fit=(1760, 800)))
        per = dur / steps; lst = ""
        for k, im in enumerate(imgs, 1):
            p = f"{OUT}/{name}_f{k}.png"; im.save(p); lst += f"file '{os.path.abspath(p)}'\nduration {per if k < steps else per + 0.001}\n"
        lst += f"file '{os.path.abspath(f'{OUT}/{name}_f{steps}.png')}'\n"; open(f"{OUT}/{name}.txt", "w").write(lst)
        sp.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/{name}.txt", "-i", aiff, "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-c:a", "aac", "-shortest", f"{OUT}/{name}.mp4"], check=True)
    else:
        title = {"s01":"Case study demo","s02":"Scenario and research questions","s03":"RQ1: attack flow and evidence points","s06":"ALEAPP: SMS messages","s07":"ALEAPP: call log","s08":"ALEAPP: WhatsApp","s09":"ALEAPP: app usage","s11":"Merged timeline (Bhutan Time)","s12":"Findings","s13":"Recommendations","s14":"Done"}[name]
        im = frame(title, narr, **kw); im.save(f"{OUT}/{name}.png")
        sp.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "25", "-t", f"{dur:.2f}", "-i", f"{OUT}/{name}.png", "-i", aiff, "-vf", "format=yuv420p", "-c:v", "libx264", "-c:a", "aac", "-shortest", f"{OUT}/{name}.mp4"], check=True)
    clips.append(f"{OUT}/{name}.mp4")
open(f"{OUT}/all.txt", "w").write("".join(f"file '{os.path.abspath(c)}'\n" for c in clips))
sp.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/all.txt", "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", "demo/OTP_Scam_Forensics_Demo.mp4"], check=True)
print("video ok")
