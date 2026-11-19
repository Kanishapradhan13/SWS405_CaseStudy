#!/usr/bin/env python3
"""Builds a FICTITIOUS Android 'victim phone' file-system extraction (test data only).
Schemas follow AOSP Telephony/CallLog providers, WhatsApp msgstore.db and a mock bank app.
Timezone: Bhutan Time (BTT, UTC+6). Scenario day: 2026-11-12."""
import sqlite3, os, sys, json, shutil, datetime as dt, hashlib

ROOT = sys.argv[1]
BTT = dt.timezone(dt.timedelta(hours=6))
def ms(hms):  # local BTT time on scenario day -> epoch ms
    h, m, s = map(int, hms.split(":"))
    return int(dt.datetime(2026, 11, 12, h, m, s, tzinfo=BTT).timestamp() * 1000)

VICTIM = "97517000001"; SCAMMER = "97577000222"; FRIEND = "97517000003"; BANKHOT = "97522000000"
shutil.rmtree(ROOT, ignore_errors=True)
def db(pkg, name):
    p = f"{ROOT}/data/data/{pkg}/databases"; os.makedirs(p, exist_ok=True)
    return sqlite3.connect(f"{p}/{name}")

# ---------- SMS (com.android.providers.telephony / mmssms.db) ----------
c = db("com.android.providers.telephony", "mmssms.db")
c.execute("""CREATE TABLE sms(_id INTEGER PRIMARY KEY AUTOINCREMENT, thread_id INTEGER, address TEXT, person INTEGER,
 date INTEGER, date_sent INTEGER DEFAULT 0, protocol INTEGER, read INTEGER DEFAULT 0, status INTEGER DEFAULT -1, type INTEGER,
 reply_path_present INTEGER, subject TEXT, body TEXT, service_center TEXT, locked INTEGER DEFAULT 0, sub_id INTEGER DEFAULT -1,
 error_code INTEGER DEFAULT -1, creator TEXT, seen INTEGER DEFAULT 0)""")
sms = [
 ("14:04:50","DBB-BANK","Your OTP for MockBank device registration is 482913. Valid for 5 min. DO NOT share it with anyone, including bank staff."),
 ("14:06:40","DBB-BANK","Your OTP for MockBank MPIN reset is 730158. Valid for 5 min. DO NOT share it with anyone."),
 ("14:08:02","DBB-BANK","MockBank alert: your account TEST-0001 was activated on a NEW device (Redmi-X). If this was not you call 2000000."),
 ("14:09:10","DBB-BANK","MockBank: Nu 30,000.00 debited to A/C ****7788. Avl bal Nu 20,000.00."),
 ("14:09:48","DBB-BANK","MockBank: Nu 19,950.00 debited to A/C ****5521. Avl bal Nu 50.00."),
]
for t, a, b in sms:
    c.execute("INSERT INTO sms(thread_id,address,date,date_sent,protocol,read,type,body,service_center,seen) VALUES(1,?,?,?,0,0,1,?,?,1)",
              (a, ms(t), ms(t) - 1200, b, "+97517999999"))
c.commit(); c.close()

# ---------- Call log (com.android.providers.contacts / calllog.db) ----------
c = db("com.android.providers.contacts", "calllog.db")
c.execute("""CREATE TABLE calls(_id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, presentation INTEGER DEFAULT 1, date INTEGER,
 duration INTEGER, data_usage INTEGER, type INTEGER, features INTEGER DEFAULT 0, subscription_component_name TEXT, subscription_id TEXT,
 phone_account_address TEXT, new INTEGER DEFAULT 1, name TEXT, numbertype INTEGER, numberlabel TEXT, countryiso TEXT,
 voicemail_uri TEXT, is_read INTEGER, geocoded_location TEXT, lookup_uri TEXT, matched_number TEXT, normalized_number TEXT,
 photo_id INTEGER DEFAULT 0, formatted_number TEXT, _data TEXT, has_content INTEGER, mime_type TEXT, source_data TEXT,
 source_package TEXT, transcription TEXT, add_for_all_users INTEGER DEFAULT 1, last_modified INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0)""")
calls = [("14:03:45", "+" + SCAMMER, 372, 1), ("14:16:20", "+" + BANKHOT, 241, 2), ("14:20:05", "+" + SCAMMER, 0, 2)]
for t, n, d, ty in calls:
    c.execute("INSERT INTO calls(number,date,duration,type,countryiso,geocoded_location,formatted_number,is_read,last_modified) VALUES(?,?,?,?,?,?,?,1,?)",
              (n, ms(t), d, ty, "BT", "Bhutan", n, ms(t)))
c.commit(); c.close()

# ---------- WhatsApp (com.whatsapp / msgstore.db, modern 'message'/'jid'/'chat' schema) ----------
c = db("com.whatsapp", "msgstore.db")
c.executescript("""
CREATE TABLE jid(_id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT NOT NULL, server TEXT NOT NULL, agent INTEGER, device INTEGER, type INTEGER, raw_string TEXT);
CREATE TABLE chat(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid_row_id INTEGER UNIQUE, hidden INTEGER, subject TEXT, created_timestamp INTEGER, display_message_row_id INTEGER, last_message_row_id INTEGER, archived INTEGER DEFAULT 0, sort_timestamp INTEGER);
CREATE TABLE message(_id INTEGER PRIMARY KEY AUTOINCREMENT, chat_row_id INTEGER NOT NULL, from_me INTEGER NOT NULL, key_id TEXT NOT NULL, sender_jid_row_id INTEGER, status INTEGER, broadcast INTEGER, recipient_count INTEGER, participant_hash TEXT, origination_flags INTEGER, origin INTEGER, timestamp INTEGER, received_timestamp INTEGER, receipt_server_timestamp INTEGER, message_type INTEGER, text_data TEXT, starred INTEGER, lookup_tables INTEGER, sort_id INTEGER, message_add_on_flags INTEGER);
CREATE TABLE message_media(message_row_id INTEGER PRIMARY KEY, chat_row_id INTEGER, autotransfer_retry_enabled INTEGER, multicast_id TEXT, media_job_uuid TEXT, transferred INTEGER, transcoded INTEGER, file_path TEXT, file_size INTEGER, suspicious_content INTEGER, trim_from INTEGER, trim_to INTEGER, face_x INTEGER, face_y INTEGER, media_duration INTEGER, media_caption TEXT, file_hash TEXT, enc_file_hash TEXT, width INTEGER, height INTEGER, mime_type TEXT);
CREATE TABLE message_location(message_row_id INTEGER PRIMARY KEY, chat_row_id INTEGER, latitude REAL, longitude REAL, place_name TEXT, place_address TEXT, url TEXT, live_location_share_duration INTEGER, live_location_sequence_number INTEGER, live_location_final_latitude REAL, live_location_final_longitude REAL, live_location_final_timestamp INTEGER);
CREATE TABLE message_system(message_row_id INTEGER PRIMARY KEY, action_type INTEGER);
CREATE TABLE message_quoted(message_row_id INTEGER, chat_row_id INTEGER, parent_message_chat_row_id INTEGER, from_me INTEGER, sender_jid_row_id INTEGER, key_id TEXT, timestamp INTEGER, message_type INTEGER, origin INTEGER, text_data TEXT, payment_transaction_id TEXT, lookup_tables INTEGER);
CREATE TABLE message_forwarded(message_row_id INTEGER PRIMARY KEY, forward_score INTEGER);
CREATE TABLE message_thumbnail(message_row_id INTEGER PRIMARY KEY, thumbnail BLOB);
CREATE TABLE message_vcard(_id INTEGER PRIMARY KEY, message_row_id INTEGER, vcard TEXT);
CREATE TABLE message_link(_id INTEGER PRIMARY KEY, message_row_id INTEGER, link_index INTEGER);
CREATE TABLE message_poll(message_row_id INTEGER PRIMARY KEY);
CREATE TABLE call_log(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid_row_id INTEGER, from_me INTEGER, call_id TEXT, transaction_id INTEGER, timestamp INTEGER, video_call INTEGER, duration INTEGER, call_result INTEGER, bytes_transferred INTEGER, group_jid_row_id INTEGER, is_joinable_group_call INTEGER, call_creator_device_jid_row_id INTEGER, call_random_id TEXT, call_link_row_id INTEGER, is_dnd_mode_on INTEGER, call_type INTEGER);
""")
def jid(u, s="s.whatsapp.net"):
    cur = c.execute("INSERT INTO jid(user,server,agent,device,type,raw_string) VALUES(?,?,0,0,0,?)", (u, s, f"{u}@{s}")); return cur.lastrowid
jv, js, jf = jid(VICTIM), jid(SCAMMER), jid(FRIEND)
chat_s = c.execute("INSERT INTO chat(jid_row_id,hidden,created_timestamp,archived) VALUES(?,0,?,0)", (js, ms("13:58:30"))).lastrowid
chat_f = c.execute("INSERT INTO chat(jid_row_id,hidden,created_timestamp,archived) VALUES(?,0,?,0)", (jf, ms("14:14:30"))).lastrowid
wa = [
 (chat_s,0,js,"13:58:30","Congratulations! Your number has WON Nu 500,000 in the Druk Mega Lucky Draw 2026. Reply YES to claim your prize."),
 (chat_s,1,jv,"13:59:12","Really? What should I do?"),
 (chat_s,0,js,"14:01:05","Do not tell anyone. I am a prize officer. I will call you now to verify your account. Keep your phone near you."),
 (chat_s,1,jv,"14:10:20","ok sir i gave the code. when will i get the prize?"),
 (chat_s,0,js,"14:11:30","Prize will be credited in 24 hours. Do not open your bank app or tell your family."),
 (chat_f,1,jv,"14:14:30","Someone took all my money from the bank app!! I think the lucky draw was a scam. Please call me"),
 (chat_f,0,jf,"14:15:05","Call the bank hotline NOW and freeze the account. Then go to the police."),
]
last = {}
for i, (ch, fm, sj, t, txt) in enumerate(wa, 1):
    cur = c.execute("INSERT INTO message(chat_row_id,from_me,key_id,sender_jid_row_id,status,timestamp,received_timestamp,message_type,text_data,sort_id,origin) VALUES(?,?,?,?,?,?,?,0,?,?,0)",
        (ch, fm, hashlib.md5(f"k{i}".encode()).hexdigest().upper(), 0 if fm else sj, 13 if fm else 0, ms(t), ms(t)+300, txt, i)); last[ch] = cur.lastrowid
for ch, rid in last.items():
    c.execute("UPDATE chat SET last_message_row_id=?, display_message_row_id=?, sort_timestamp=(SELECT MAX(timestamp) FROM message WHERE chat_row_id=?) WHERE _id=?", (rid, rid, ch, ch))
c.execute("INSERT INTO call_log(jid_row_id,from_me,call_id,timestamp,video_call,duration,call_result,call_type) VALUES(?,0,'WAC0001',?,0,0,5,1)", (js, ms("14:02:10")))  # missed WhatsApp call attempt
c.commit(); c.close()
c = db("com.whatsapp", "wa.db")
c.execute("CREATE TABLE wa_contacts(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid TEXT, is_whatsapp_user INTEGER, status TEXT, number TEXT, raw_contact_id INTEGER, display_name TEXT, phone_type INTEGER, phone_label TEXT, unseen_msg_count INTEGER, photo_ts INTEGER, thumb_ts INTEGER, photo_id_timestamp INTEGER, given_name TEXT, family_name TEXT, wa_name TEXT, sort_name TEXT, nickname TEXT, company TEXT, title TEXT, status_timestamp INTEGER, number_from_url TEXT, official_biz_name TEXT)")
for j, n, nm in [(f"{VICTIM}@s.whatsapp.net", "+"+VICTIM, "Pema Dema (TEST)"), (f"{SCAMMER}@s.whatsapp.net", "+"+SCAMMER, "~Prize Officer"), (f"{FRIEND}@s.whatsapp.net", "+"+FRIEND, "Karma (friend)")]:
    c.execute("INSERT INTO wa_contacts(jid,is_whatsapp_user,number,display_name,wa_name) VALUES(?,1,?,?,?)", (j, n, nm, nm))
c.commit(); c.close()

# ---------- Mock bank app (bt.casestudy.mockbank / mockbank.db) ----------
c = db("bt.casestudy.mockbank", "mockbank.db")
c.executescript("""CREATE TABLE auth_events(id INTEGER PRIMARY KEY AUTOINCREMENT, ts_ms INTEGER, event TEXT, device_id TEXT, result TEXT);
CREATE TABLE otp_log(id INTEGER PRIMARY KEY AUTOINCREMENT, ts_ms INTEGER, purpose TEXT, otp_hash TEXT, delivered_to TEXT);
CREATE TABLE device_bindings(device_id TEXT PRIMARY KEY, model TEXT, bound_ts_ms INTEGER, active INTEGER);
CREATE TABLE transactions(id INTEGER PRIMARY KEY AUTOINCREMENT, ts_ms INTEGER, direction TEXT, amount_nu REAL, counterparty TEXT, balance_after REAL);""")
c.execute("INSERT INTO device_bindings VALUES('DEV-VICTIM-01','Pixel-6 (emulated)',?,0)", (ms("09:00:00") - 86400000 * 30,))
c.executemany("INSERT INTO auth_events(ts_ms,event,device_id,result) VALUES(?,?,?,?)", [
 (ms("09:12:03"), "APP_OPEN", "DEV-VICTIM-01", "OK"),
 (ms("14:13:15"), "APP_OPEN", "DEV-VICTIM-01", "REJECTED_DEVICE_UNBOUND"),
 (ms("14:13:40"), "LOGIN_MPIN", "DEV-VICTIM-01", "REJECTED_MPIN_CHANGED")])
c.executemany("INSERT INTO otp_log(ts_ms,purpose,otp_hash,delivered_to) VALUES(?,?,?,?)", [
 (ms("14:04:50"), "DEVICE_REGISTRATION", hashlib.sha256(b"482913").hexdigest()[:16], "+"+VICTIM),
 (ms("14:06:40"), "MPIN_RESET", hashlib.sha256(b"730158").hexdigest()[:16], "+"+VICTIM)])
c.executemany("INSERT INTO transactions(ts_ms,direction,amount_nu,counterparty,balance_after) VALUES(?,?,?,?,?)", [
 (ms("09:12:30"), "SYNC", 0, "opening balance", 50000.0)])
c.commit(); c.close()
# bank-side record (NOT on phone): what police must request from the bank
os.makedirs(f"{ROOT}/../bank_requested_records", exist_ok=True)
open(f"{ROOT}/../bank_requested_records/server_log_TEST-0001.csv", "w").write(
"time_btt,event,device_id,device_model,ip,detail\n"
"2026-11-12 14:04:48,OTP_REQUEST,DEV-ATTACKER-77,Redmi-X,203.0.113.45,DEVICE_REGISTRATION\n"
"2026-11-12 14:05:35,OTP_VERIFY_OK,DEV-ATTACKER-77,Redmi-X,203.0.113.45,DEVICE_REGISTRATION\n"
"2026-11-12 14:06:38,OTP_REQUEST,DEV-ATTACKER-77,Redmi-X,203.0.113.45,MPIN_RESET\n"
"2026-11-12 14:07:50,OTP_VERIFY_OK,DEV-ATTACKER-77,Redmi-X,203.0.113.45,MPIN_RESET\n"
"2026-11-12 14:08:02,DEVICE_BOUND,DEV-ATTACKER-77,Redmi-X,203.0.113.45,old device DEV-VICTIM-01 revoked\n"
"2026-11-12 14:09:09,TRANSFER,DEV-ATTACKER-77,Redmi-X,203.0.113.45,30000.00 to ****7788\n"
"2026-11-12 14:09:47,TRANSFER,DEV-ATTACKER-77,Redmi-X,203.0.113.45,19950.00 to ****5521\n")

# ---------- UsageStats (legacy XML-like export used for app-usage timeline) ----------
us = f"{ROOT}/data/system/usagestats/0"; os.makedirs(us, exist_ok=True)
ev = [("13:58:40","com.whatsapp",1),("14:01:30","com.whatsapp",2),("14:03:44","com.android.dialer",1),("14:10:00","com.android.dialer",2),
      ("14:10:15","com.whatsapp",1),("14:11:40","com.whatsapp",2),("14:13:15","bt.casestudy.mockbank",1),("14:13:50","bt.casestudy.mockbank",2),
      ("14:14:20","com.whatsapp",1),("14:16:00","com.whatsapp",2),("14:16:18","com.android.dialer",1),("14:20:10","com.android.dialer",2)]
# Real Android UsageStats v1 protobuf (IntervalStatsProto), daily bucket -> /data/system/usagestats/0/daily/<bucket_start_ms>
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "ALEAPP-src"))
from scripts.artifacts.usagestats_pb import usagestatsservice_pb2 as pb
st = pb.IntervalStatsProto()
day0 = ms("00:00:00")
st.end_time_ms = 86400000
for t, p, k in ev:
    e = st.event_log.add(); e.time_ms = ms(t) - day0; e.package = p; e.type = k
for p_ in sorted({e[1] for e in ev}):
    q = st.packages.add(); q.package = p_; q.last_time_active_ms = max(ms(t) for t, pp, k in ev if pp == p_) - day0
os.makedirs(f"{us}/daily", exist_ok=True)
open(f"{us}/daily/{day0}", "wb").write(st.SerializeToString())
open(f"{us}/version", "w").write("1")
# notification log
nl = [("14:04:51","com.google.android.apps.messaging","DBB-BANK","Your OTP for MockBank device registration is 482913..."),
      ("14:06:41","com.google.android.apps.messaging","DBB-BANK","Your OTP for MockBank MPIN reset is 730158..."),
      ("14:08:03","com.google.android.apps.messaging","DBB-BANK","MockBank alert: new device activated"),
      ("14:09:11","com.google.android.apps.messaging","DBB-BANK","MockBank: Nu 30,000.00 debited"),
      ("14:09:49","com.google.android.apps.messaging","DBB-BANK","MockBank: Nu 19,950.00 debited"),
      ("14:11:31","com.whatsapp","~Prize Officer","Prize will be credited in 24 hours...")]
json.dump([{"post_ms": ms(t), "package": p, "title": ti, "text": tx} for t,p,ti,tx in nl], open(f"{ROOT}/data/system/notification_log.json","w"), indent=1)
print("built", ROOT)
