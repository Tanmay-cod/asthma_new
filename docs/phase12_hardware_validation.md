# Phase 12 Hardware Validation

Hardware: ESP8266 + MAX30102 + DHT22 + GP2Y1010AU0F

Physical validation: NOT EXECUTED — physical device not connected in this environment.

Test A (User A) and Test B (User B) from the Phase 12 spec must be executed
manually with the physical device:
1. User A starts measurement → ESP001 assigned to A → readings appear → end.
2. User B starts measurement → ESP001 assigned to B → readings appear → end.
3. Isolation: A sees only A's data; B sees only B's data.

Software path: PASS (automated tests `backend/app/tests/test_phase12.py`).
Realtime: dashboard polls latest readings every 5s (no manual refresh required).
