# SHRAVAN

SHRAVAN is a full-stack health companion for senior citizens, caretakers, and community health organizations. It combines medicine reminders, health logging, emergency contacts, nearby healthcare discovery, yoga content, and AI assistance in one application.

## Stack

- Frontend: Vue 3, Pinia, Vue Router, Vite
- Backend: Flask, SQLAlchemy, Flask-Session
- Database: SQLite by default, PostgreSQL-compatible through `DATABASE_URL`
- AI: Groq and Gemini, both optional
- Healthcare discovery: Google Places when configured, OpenStreetMap/Overpass fallback when it is not
- Geocoding: Google Maps when configured, Nominatim fallback when it is not
- Video discovery: YouTube Data API, optional
- Mobile: Flutter client included under `mobile-application/frontend`

## Security

The backend uses server-side sessions, secure password hashing, CSRF protection for state-changing API requests, role checks, session expiration, login throttling, restrictive CORS, response security headers, request size limits, user-scoped reminder and voice data, and validation for user-supplied external URLs.

API keys stay on the backend. The frontend does not require a Google Maps key for the core location and healthcare discovery flows.

## Local setup

### 1. Backend

```bash
cd Backend
python -m venv backend_venv

# macOS/Linux
source backend_venv/bin/activate

# Windows PowerShell
# .\\backend_venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
python app.py
```

On Windows, use `run_backend.ps1` from the repository root instead. On macOS/Linux, `run_backend.sh` prepares the virtual environment and local secret automatically.

### 2. Frontend

```bash
cd Frontend
npm install
npm run dev
```

The application normally runs at `http://localhost:5173` and the API at `http://127.0.0.1:5000`.

### 3. One-command startup

```bash
# macOS/Linux
./start.sh

# Windows PowerShell
./start.ps1
```

## API keys

The application can run without paid APIs.

Optional keys:

- `GROQ_API_KEY`: AI chatbot
- `GEMINI_API_KEY`: Gemini content generation
- `YOUTUBE_API_KEY`: YouTube search
- `GOOGLE_MAPS_API_KEY`: enhanced Google Places/geocoding support

Without a Google Maps key, nearby hospitals and pharmacies use OpenStreetMap data and geocoding uses Nominatim.

## Configuration

Copy `Backend/.env.example` to `Backend/.env` and set a strong `SECRET_KEY` for any persistent deployment.

For production behind HTTPS:

```env
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=None
```

Set `ALLOWED_ORIGINS` to the exact frontend origins that are allowed to call the API.

## Testing

The test suite is under `Tests/`.

```bash
pytest Tests -q
```

The suite should be run against a clean test database or an isolated application environment. Do not run destructive tests against production data.

## API documentation

Once the backend is running:

`http://127.0.0.1:5000/apidocs/`

## Project structure

```text
SHRAVAN/
├── Backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── security.py
│   ├── routes_*.py
│   ├── modules/
│   └── docs/
├── Frontend/
│   └── src/
├── mobile-application/
│   └── frontend/
└── Tests/
```

## Medical safety

The AI assistant is intended for general information and support. It must not be treated as a diagnosis or a substitute for a licensed healthcare professional. Emergency symptoms should be handled through local emergency services or an appropriate medical provider.
