# Asthma Risk Prediction System with Explainability (XAI) + IoT

Personalized, explainable asthma risk monitoring using an ESP8266 sensor node.

## Architecture

```
[ESP8266 + MAX30102 + DHT22 + GP2Y1010AU0F] --HTTP POST JSON--> [FastAPI backend]
                                                                  |
                                                   SQLite storage (data/asthma.db)
                                                                  |
                                            XGBoost + SHAP risk engine (per-user)
                                                                  |
                                                   Web dashboard (frontend/)
```

## Setup

```bash
pip install -r requirements.txt
python -m app.ml          # trains model + SHAP explainer -> models/
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 for the dashboard. API docs at `/docs`.

## Create a user

```bash
curl -X POST http://127.0.0.1:8000/api/users -H "Content-Type: application/json" -d "{\"name\":\"Tanmay\",\"age\":21,\"gender\":\"male\",\"smoking\":\"never\",\"personal_best_pefr\":500,\"baseline_spo2\":97,\"baseline_pulse\":75}"
```

## Personalization

The model uses **each user's own baseline**: PEFR is expressed as % of the user's personal best, and SpO2/pulse deviations from that user's normal. So the same raw reading produces different risk for different users.

## Explainability

Every prediction stores SHAP values per feature — the dashboard shows which factors pushed the risk up or down (e.g., high dust + low PEFR).

## High-risk alerts (optional)

Set environment variables before starting the server:

```powershell
$env:TELEGRAM_BOT_TOKEN="your_bot_token"   # from @BotFather on Telegram
$env:TELEGRAM_CHAT_ID="your_chat_id"
$env:ALERT_EMAIL_FROM="you@gmail.com"
$env:ALERT_EMAIL_TO="you@gmail.com"
$env:ALERT_EMAIL_PASSWORD="app_password"
```

When risk level becomes "High" (and a 10-minute cooldown per user has passed), an alert is sent via Telegram and/or email.

## Mobile access (PWA)

The dashboard is a Progressive Web App — open it on your phone browser and use "Add to Home Screen" for an app-like experience.

## Testing without hardware

```bash
python simulate.py   # sends fake readings every 5s
```

## Firmware

Flash `firmware/asthma_node/asthma_node.ino` (Arduino IDE, ESP8266 board). Set WiFi + server IP. For a proper SpO2/pulse algorithm use the `spo2_algorithm.h` example from the SparkFun MAX3010x library.

# asthma_new
