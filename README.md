# Smart FoodGuard AI

A student-friendly full-stack demonstration of food-quality screening workflows. The app includes:
- React + Vite + TypeScript frontend
- FastAPI backend with SQLite persistence
- Email/password signup and login using JWT
- Demo/manual analysis and authenticated ESP32 sensor ingestion
- Per-device connection state, sample/test-session association, duplicate message protection
- A scikit-learn demo model trained on explicitly synthetic data
- CSV export, history, model metadata, and API documentation

> **Scientific limitation:** The included dataset and model are synthetic software-workflow demonstrations only. They do not detect or prove food adulteration, establish food safety, or replace validated laboratory testing. Real sensor profiles and food-specific ML models require calibrated hardware and laboratory-labelled datasets.

## Requirements
- Python 3.11+
- Node.js 20+
- (Optional) ESP32 development board and sensors

## 1. Backend setup (Windows PowerShell)
```powershell
cd backend
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.ml.train
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API docs: http://localhost:8000/docs

## 2. Frontend setup
Open a second terminal:
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open http://localhost:5173

## 3. First use
1. Create an account on the Sign up page.
2. Sign in.
3. Use Manual / Demo mode for the software demonstration.
4. For Hardware mode, register a device in the Hardware page using its device ID and device API key from `backend/.env`.
5. Create a sample and test session in the Hardware page, then start the test.
6. Configure the ESP32 with the device ID, device key, backend LAN IP, and session ID. Send measurements to `POST /api/sensors/ingest`.

## Hardware API

`POST /api/sensors/ingest`

Headers:
- `X-Device-ID: <registered-device-id>`
- `X-Device-Key: <device-secret>`

Example JSON:
```json
{
  "message_id": "esp32-001-000012",
  "session_id": "paste-active-session-id-here",
  "food": "milk",
  "measured_at": "2026-10-31T12:30:00Z",
  "measurements": {
    "temperature_c": 22.4,
    "ph": 6.7,
    "conductivity_us_cm": 410.0
  }
}
```
The backend verifies device credentials, active session ownership, food compatibility, finite numeric values, timestamp, and duplicate `message_id`. Measurements are stored as device readings and linked to the active sample/test session. A session can be analyzed using the UI after readings arrive.

## Optional USB serial bridge
The example bridge in `backend/app/sensors/serial_bridge.py` reads newline-delimited JSON from a serial port and forwards it to the same authenticated ingestion endpoint. Install `pyserial` if needed:
```powershell
pip install pyserial requests
python -m app.sensors.serial_bridge --port COM5 --url http://127.0.0.1:8000 --device-id esp32-demo-01 --device-key CHANGE_ME
```
The bridge is optional and requires the ESP32 firmware to print the same JSON payload (one JSON object per line). It does not create a fake device connection.

## ESP32
See `hardware/esp32_foodguard.ino`. Install ArduinoJson in Arduino IDE, set Wi-Fi credentials, backend URL, device ID/key, and active session ID. Connect only the sensors that match a documented, calibrated food-specific profile. The example measurement fields are placeholders for integration testing—not validated food tests.

## Security notes
- Change `JWT_SECRET` and `DEVICE_API_KEY` in `.env`.
- Never put the device key or JWT secret in frontend code or commit real secrets.
- Use HTTPS and a secure secret provisioning process outside a local classroom network.
- The demo uses a single configured device key; production should store per-device hashed secrets and support rotation/revocation.
- This student demo uses SQLite and basic JWT auth; it is not a production security audit.

## ML and data
`backend/data/demo/synthetic_demo.csv` is generated for demonstrating the pipeline. Labels are synthetic. Run:
```powershell
python -m app.ml.train
```
Metrics in `backend/models/model_metadata.json` are computed from the synthetic holdout split and are prominently marked **NOT SCIENTIFIC VALIDATION**. Replace the CSV with verified food-specific laboratory-labelled data and review feature definitions, calibration, class balance, leakage, and external validation before real-world use.

## Tests
```powershell
pytest
```

## Implemented vs. requires hardware/data
Implemented: auth, demo workflow, API integration, SQLite history, device registration, test sessions, authenticated ingestion, duplicate handling, ESP32 example, optional serial bridge, demo ML pipeline, API docs.
Requires physical hardware: Wi-Fi/USB connection test with a real ESP32, calibrated sensor adapters, and reliable sensor sampling.
Requires validated data: any real food-specific adulteration screening claim, calibrated confidence, thresholds, and reference comparisons.
