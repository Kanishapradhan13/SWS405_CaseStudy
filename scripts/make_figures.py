import csv, datetime as dt, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams["font.family"] = "Helvetica"
# ---- Fig 1: attack flow ----
steps = [("1  Lure","WhatsApp message:\n'You won Nu 500,000'","WhatsApp msgstore.db\n(message, jid)"),
 ("2  Voice contact","Scammer phones victim;\nbuilds trust & urgency","Call log (calllog.db)\nWhatsApp call_log"),
 ("3  Trigger OTP #1","Scammer starts device\nregistration on own phone","Bank server log\n+ SMS inbox (OTP)"),
 ("4  OTP disclosed","Victim reads code\naloud on the call","NO direct artefact;\ninferred: call overlaps OTP"),
 ("5  Trigger OTP #2","MPIN reset on\nattacker's device","SMS inbox, notification\nlog, bank log"),
 ("6  Takeover","App bound to new device;\nvictim's device revoked","SMS 'new device' alert;\nmockbank.db rejects"),
 ("7  Cash-out","Two transfers empty\nthe account","Debit SMS + notifications;\nbank transfer log"),
 ("8  Cover-up / aftermath","'Do not tell anyone';\nvictim discovers loss","WhatsApp, UsageStats,\ncall to bank hotline")]
fig, ax = plt.subplots(figsize=(13, 6.3)); ax.set_xlim(0, 13); ax.set_ylim(0, 6.3); ax.axis("off")
for i, (t, d, e) in enumerate(steps):
    x = 0.25 + (i % 4) * 3.2; y = 3.55 if i < 4 else 0.45
    ax.add_patch(FancyBboxPatch((x, y), 2.85, 2.35, boxstyle="round,pad=0.03", fc="#EEF3FA", ec="#1F4E79", lw=1.4))
    ax.text(x+0.12, y+2.05, t, fontsize=11, weight="bold", color="#1F4E79", va="center")
    ax.text(x+0.12, y+1.25, d, fontsize=9.3, va="center")
    ax.add_patch(FancyBboxPatch((x+0.08, y+0.06), 2.69, 0.72, boxstyle="round,pad=0.02", fc="#FFF4D6" if i != 3 else "#FADBD8", ec="#C98A00" if i != 3 else "#C0392B", lw=1))
    ax.text(x+0.16, y+0.42, "Evidence: " + e.replace("\n", " "), fontsize=7.4, va="center", wrap=True)
    if i < 7 and i != 3:
        ax.annotate("", xy=(x+3.17, y+1.2), xytext=(x+2.88, y+1.2), arrowprops=dict(arrowstyle="->", color="#444", lw=1.5))
ax.annotate("", xy=(0.25+1.4, 2.95), xytext=(0.25+3*3.2+1.4, 3.5), arrowprops=dict(arrowstyle="->", color="#444", lw=1.5, connectionstyle="arc3,rad=0.0"))
ax.set_title("Figure 1. OTP-sharing account takeover: attack flow and where digital evidence is created", fontsize=12, loc="left")
plt.tight_layout(); plt.savefig("report/figures/fig1_attack_flow.png", dpi=200); plt.close()

# ---- Fig 2: swimlane timeline ----
rows = list(csv.DictReader(open("analysis/master_timeline_BTT.csv")))
lanes = ["Bank server log","SMS mmssms.db","Notification log","Call log calllog.db","WhatsApp msgstore.db","WhatsApp msgstore.db (call_log)","UsageStats protobuf","MockBank mockbank.db"]
lane_label = {"Bank server log":"Bank server (off-phone)","SMS mmssms.db":"SMS inbox","Notification log":"Notifications","Call log calllog.db":"Call log","WhatsApp msgstore.db":"WhatsApp chats","WhatsApp msgstore.db (call_log)":"WhatsApp calls","UsageStats protobuf":"App usage (foreground)","MockBank mockbank.db":"MockBank app DB"}
col = {"Bank server log":"#C0392B","SMS mmssms.db":"#1F4E79","Notification log":"#5D8AA8","Call log calllog.db":"#2E7D32","WhatsApp msgstore.db":"#7B1FA2","WhatsApp msgstore.db (call_log)":"#9C27B0","UsageStats protobuf":"#E67E22","MockBank mockbank.db":"#00838F"}
def tm(r): d = dt.datetime.strptime(r["time_BTT"], "%Y-%m-%d %H:%M:%S"); return d.hour*60 + d.minute + d.second/60
fig, ax = plt.subplots(figsize=(13, 5.2))
for r in rows:
    a = r["artefact"]
    if a not in lanes or tm(r) < 13*60+55: continue
    ax.scatter(tm(r), lanes.index(a), s=55, color=col[a], zorder=3)
ax.axvspan(14*60+3+45/60, 14*60+9+57/60, color="#F5B7B1", alpha=.45, label="Scam call 14:03:45-14:09:57")
for t, lab in [(14*60+4+50/60,"OTP #1"),(14*60+6+40/60,"OTP #2"),(14*60+8,"new device"),(14*60+9+10/60,"debits")]:
    ax.axvline(t, color="#888", ls=":", lw=1); ax.text(t, len(lanes)-0.35, lab, rotation=90, fontsize=8, va="bottom", ha="right")
ax.set_yticks(range(len(lanes))); ax.set_yticklabels([lane_label[l] for l in lanes], fontsize=9)
ticks = list(range(13*60+55, 14*60+23, 5)); ax.set_xticks(ticks); ax.set_xticklabels([f"{t//60}:{t%60:02d}" for t in ticks], fontsize=8)
ax.set_xlim(13*60+55, 14*60+22); ax.set_ylim(-0.6, len(lanes)+0.5); ax.grid(axis="x", alpha=.25); ax.legend(loc="upper right", fontsize=8)
ax.set_xlabel("Bhutan Time (UTC+6), 12 Nov 2026 (test data)"); ax.set_title("Figure 2. Evidence swim-lane timeline reconstructed from the extraction", fontsize=12, loc="left")
plt.tight_layout(); plt.savefig("report/figures/fig2_timeline.png", dpi=200)
print("ok")
