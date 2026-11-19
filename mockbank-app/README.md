# MockBank (TEST ONLY)
Kotlin source of the mock banking app used in the case study. All identifiers, numbers and amounts are fictitious.
Build: open `mockbank-app` in Android Studio (compileSdk 34) and run on an emulator.
Data written by the app: `databases/mockbank.db` (tables: auth_events, otp_log, device_bindings, transactions).
In this submission the same schema is populated by `scripts/build_evidence.py` so the analysis is reproducible without an emulator image.
