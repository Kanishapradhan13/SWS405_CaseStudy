#!/usr/bin/env python3
"""Merge ALEAPP TSV exports + notification log + mock bank DB + bank-side log into one BTT timeline."""
import csv, glob, json, sqlite3, datetime as dt, sys, os
BTT = dt.timezone(dt.timedelta(hours=6))
base = glob.glob("analysis/ALEAPP_Output_*/")[0]
tsv = lambda n: list(csv.DictReader(open(f"{base}_TSV Exports/{n}.tsv", encoding="utf-8-sig"), delimiter="\t"))
def btt(s):  # ALEAPP UTC string -> BTT datetime
    return dt.datetime.fromisoformat(s.replace("+00:00", "")[:19]).replace(tzinfo=dt.timezone.utc).astimezone(BTT)
rows = []
add = lambda t, src, art, ev: rows.append((t, src, art, ev))
for r in tsv("WhatsApp - One To One Messages"):
    d = "RECEIVED from" if r["Message Direction"] == "Incoming" else "SENT to"
    add(btt(r["Message Timestamp"]), "ALEAPP", "WhatsApp msgstore.db", f'{d} {r["Other Participant WA User Name"]}: "{r["Message"][:90]}"')
for r in tsv("SMS Messages"):
    add(btt(r["Date"]), "ALEAPP", "SMS mmssms.db", f'SMS {r["Type"]} from {r["Address"]}: {r["Body"][:95]}')
for r in tsv("Call logs "):
    ty = r["Type"].split(" <")[0]; n = r["Partner"]
    add(btt(r["Call Date"]), "ALEAPP", "Call log calllog.db", f'{ty} call {n}, duration {r["Duration in Secs"]}s ({int(r["Duration in Secs"])//60}m{int(r["Duration in Secs"])%60:02d}s)')
for r in tsv("WhatsApp - Call Logs"):
    add(btt(r["Call Start Timestamp"]), "ALEAPP", "WhatsApp msgstore.db (call_log)", f'WhatsApp {r["Call Type"]} call {r["Call Direction"]} from {r["Caller"]}, duration {r["Call Duration"]} (unanswered)')
# usage events straight from the protobuf via ALEAPP's own decoded types
import sqlite3 as s3
lava = s3.connect(glob.glob(base + "_lava_artifacts.db")[0])
tbls = [t[0] for t in lava.execute("select name from sqlite_master where type='table'")]
ut = [t for t in tbls if "usage" in t.lower() and "stats" in t.lower()]
for t in ut:
    cols = [c[1] for c in lava.execute(f"pragma table_info({t})")]
    if "types" in cols or "event_type" in cols:
        print("usage table", t, cols)
for ts, et, pkg in lava.execute("select timestamp_last_time_active,event_type,package from get_usagestats where usage_type='event-log' and event_type in ('ACTIVITY_RESUMED','ACTIVITY_PAUSED')"):
    add(dt.datetime.fromtimestamp(ts, BTT), "ALEAPP", "UsageStats protobuf", f'App {pkg} {"moved to FOREGROUND" if et=="ACTIVITY_RESUMED" else "moved to background"}')
nl = json.load(open("evidence/victim_phone_extraction/data/system/notification_log.json"))
for n in nl:
    add(dt.datetime.fromtimestamp(n["post_ms"]/1000, BTT), "custom parser", "Notification log", f'Notification from {n["package"].split(".")[-1]} ({n["title"]}): {n["text"][:70]}')
mb = sqlite3.connect("evidence/victim_phone_extraction/data/data/bt.casestudy.mockbank/databases/mockbank.db")
for ts, ev, dev, res in mb.execute("select ts_ms,event,device_id,result from auth_events"):
    add(dt.datetime.fromtimestamp(ts/1000, BTT), "DB Browser/sqlite", "MockBank mockbank.db", f"{ev} on {dev}: {res}")
for ts, p, h, to in mb.execute("select ts_ms,purpose,otp_hash,delivered_to from otp_log"):
    add(dt.datetime.fromtimestamp(ts/1000, BTT), "DB Browser/sqlite", "MockBank mockbank.db", f"OTP issued ({p}) to {to}")
for r in csv.DictReader(open("evidence/bank_requested_records/server_log_TEST-0001.csv")):
    add(dt.datetime.fromisoformat(r["time_btt"]).replace(tzinfo=BTT), "BANK (off-phone)", "Bank server log", f'{r["event"]} {r["detail"]} from {r["device_model"]} {r["ip"]}')
ev = json.load(open("/dev/null")) if False else None
rows.sort(key=lambda x: x[0])
os.makedirs("analysis", exist_ok=True)
with open("analysis/master_timeline_BTT.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["time_BTT", "source_tool", "artefact", "event"])
    for t, s, a, e in rows: w.writerow([t.strftime("%Y-%m-%d %H:%M:%S"), s, a, e])
for t, s, a, e in rows: print(t.strftime("%H:%M:%S"), "|", a, "|", e[:110])
