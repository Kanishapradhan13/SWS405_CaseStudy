package bt.casestudy.mockbank

import android.app.Activity
import android.os.Bundle
import android.widget.TextView

/** Minimal UI: shows balance and records that the *legitimate* device opened the app. */
class MainActivity : Activity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        val db = BankDb(this)
        db.auth("APP_OPEN", "DEV-VICTIM-01", "OK")
        setContentView(TextView(this).apply { text = "MockBank (TEST)\nAccount: TEST-0001\nBalance: Nu 50,000.00"; textSize = 22f })
    }
}
