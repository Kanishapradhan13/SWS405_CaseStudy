package bt.casestudy.mockbank

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

/**
 * Local store of the mock banking app. File: /data/data/bt.casestudy.mockbank/databases/mockbank.db
 * It deliberately keeps a client-side audit trail so that the experiment can show what a
 * *victim-side* acquisition can (and cannot) prove. Server-side logs would live at the bank.
 */
class BankDb(ctx: Context) : SQLiteOpenHelper(ctx, "mockbank.db", null, 1) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("CREATE TABLE auth_events(id INTEGER PRIMARY KEY AUTOINCREMENT, ts_ms INTEGER, event TEXT, device_id TEXT, result TEXT)")
        db.execSQL("CREATE TABLE otp_log(id INTEGER PRIMARY KEY AUTOINCREMENT, ts_ms INTEGER, purpose TEXT, otp_hash TEXT, delivered_to TEXT)")
        db.execSQL("CREATE TABLE device_bindings(device_id TEXT PRIMARY KEY, model TEXT, bound_ts_ms INTEGER, active INTEGER)")
        db.execSQL("CREATE TABLE transactions(id INTEGER PRIMARY KEY AUTOINCREMENT, ts_ms INTEGER, direction TEXT, amount_nu REAL, counterparty TEXT, balance_after REAL)")
    }
    override fun onUpgrade(db: SQLiteDatabase, o: Int, n: Int) {}

    fun auth(event: String, device: String, result: String) = writableDatabase.insert("auth_events", null,
        ContentValues().apply { put("ts_ms", System.currentTimeMillis()); put("event", event); put("device_id", device); put("result", result) })

    fun tx(dir: String, amt: Double, who: String, bal: Double) = writableDatabase.insert("transactions", null,
        ContentValues().apply { put("ts_ms", System.currentTimeMillis()); put("direction", dir); put("amount_nu", amt); put("counterparty", who); put("balance_after", bal) })
}
