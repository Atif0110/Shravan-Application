# Shravan — Digital Health Companion for Senior Citizens

Shravan is a health-management platform built for senior citizens and the people who support them — medicine reminders, symptom logging, a health/companion chatbot, yoga guidance, and doctor/pharmacy/hospital finders, with separate dashboards for the senior, their caretaker, and an NGO/health-worker role.

Named after the symbol of devotion and care in Indian culture, Shravan aims to make day-to-day health management simpler for elderly users and give the people caring for them visibility into that care.

> This README documents the **Frontend (Vue.js) + Backend (Flask)** web app, which is the actively maintained part of this repo. A separate Flutter mobile app lives in `mobile-application/` — see its own README for that.

---

## ✨ Features

- **Medicine reminders** — add medicines with timing/frequency, mark them taken through the day; status is stored per day so it survives navigating away and coming back.
- **Health chatbot** — Groq-powered assistant for general health questions (not a diagnostic tool).
- **Personal companion chatbot** — a more conversational assistant aimed at reducing loneliness, with voice input/output.
- **Age-Friendly Yoga** — asana animations and instructional videos suited to older adults.
- **Doctor / Hospital / Pharmacy finder** — search your own database of doctors, or find nearby facilities via Google Maps.
- **Health trends (NGO role)** — aggregated symptom-report trends by pincode, for health workers monitoring a community.
- **Three account roles** — `user` (the senior/primary account), `caretaker`, and `ngo`, each with their own dashboard.

---

## 🏗️ Tech Stack

| Layer | Stack |
|---|---|
| Frontend | Vue 3 (Composition API, `<script setup>`), Vue Router, Vite |
| Backend | Flask, SQLAlchemy, Flask-Session (server-side sessions) |
| Database | SQLite by default (via SQLAlchemy — swappable) |
| AI / external APIs | Groq (chat + web-scraping extraction), Google Gemini, Google Maps (Places), YouTube Data API |
| Auth | Session-cookie based (not JWT) — see [Authentication](#-authentication--sessions) below |

---

## 📂 Project Structure
Shravan-Application/
├── Backend/                  # Flask API
│   ├── app.py                 # App entrypoint, DB init, seed data
│   ├── config.py              # Flask config, CORS, session cookie settings
│   ├── models.py              # SQLAlchemy models
│   ├── routes_*.py            # Route modules (users, reminders, health, asanas, doctors, analytics, ...)
│   ├── modules/                # Chatbot, web scraper, nearby-places, generative AI wrappers
│   ├── docs/                   # Flasgger/Swagger YAML specs per endpoint
│   ├── populate_yoga_data.py   # Seeds yoga asana data (runs automatically on first boot)
│   └── requirements.txt
├── Frontend/                 # Vue.js web app
│   ├── src/
│   │   ├── views/              # One component per screen/route
│   │   ├── router/index.js     # All routes + auth guards
│   │   └── stores/auth.js      # Pinia auth store
│   └── package.json
└── mobile-application/       # Flutter app (separate, see its own README)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Git

### 1. Backend setup

```bash
cd Backend
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

```env
GROQ_API_KEY="your_groq_api_key_here"
GOOGLE_MAPS_API_KEY="your_google_maps_api_key_here"
GEMINI_API_KEY="your_gemini_api_key_here"
YOUTUBE_API_KEY="your_youtube_data_api_v3_key_here"
SECRET_KEY="generate this — see below"
FLASK_DEBUG="False"
ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
SESSION_COOKIE_SECURE="False"   # set to "True" only when served over https
```

Generate `SECRET_KEY` with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

The API keys aren't required to boot the app — without them, only the features that call those specific services (doctor info scraping, nearby-places search, the AI chatbots, yoga video search) won't work; everything else runs fine with placeholder values.

Run it:
```bash
python app.py
```
The database, default roles (`user`, `caretaker`, `ngo`), and yoga asana data are all created/seeded automatically on first run — no manual scripts needed.

Backend runs at `http://127.0.0.1:5000`.

### 2. Frontend setup

```bash
cd Frontend
npm install
cp .env.example .env   # confirm VITE_BACKEND_URL points at your backend
npm run dev
```

Frontend runs at `http://localhost:5173`.

Open that URL, register an account, and pick a role (`user` for a senior/primary account, `caretaker`, or `ngo` for the health-worker dashboard).

---

## 🔐 Authentication & Sessions

This app uses **server-side session cookies**, not JWTs. On login, Flask sets a session cookie that the frontend sends back with `credentials: 'include'` on every request. This means:

- Frontend and backend must run on hostnames the browser considers a matching pair for cookies to work (e.g. both on `127.0.0.1` or both on `localhost` — not one of each) when running locally over http.
- In production behind https, set `SESSION_COOKIE_SECURE=True` in the backend env so the cookie is scoped correctly for cross-origin use.
- `ALLOWED_ORIGINS` in the backend `.env` must list every origin the frontend is actually served from, or CORS will reject the requests.

If you see login "succeeding" but subsequent requests (like fetching your profile) coming back `401`, it's almost always one of the two points above.

---

## 👥 Roles

| Role | Assigned via | Dashboard | Notes |
|---|---|---|---|
| `user` | Registration form | `UserDashboard.vue` | The primary/senior account — medicine reminders, chatbot, yoga, finders. |
| `caretaker` | Registration form | `CareTakerDashboard.vue` | Intended to manage a senior's care. Linking a caretaker account to a specific senior's data is not yet implemented — see [Known Limitations](#-known-limitations). |
| `ngo` | Registration form | `TertiaryUserDashboard.vue` | Health-worker view; can query community symptom trends by pincode. |

---

## ⚠️ Known Limitations

- **No caretaker-to-senior linking yet.** A caretaker account currently can't add a medicine reminder on behalf of a specific senior — reminders belong to whichever account is logged in and created them. Proper delegation (a caretaker managing one or more linked seniors' reminders) needs a linking table and permission checks that don't exist yet.
- **Doctor Finder's deeper features** (website scraping for doctor details) depend on `GROQ_API_KEY`; without it, basic doctor search still works but detail enrichment won't.
- **Voice input** relies on the Web Speech API, which is Chrome-only in practice (not supported in Firefox, limited in Safari).
- The mobile app under `mobile-application/` is a separate Flutter codebase and is not kept in sync with the web app's features.

---

## 🧪 Testing

```bash
cd Backend
python -m pytest test_personal_chatbot.py
```

There isn't yet a comprehensive automated test suite covering all routes — most testing so far has been manual/exploratory.

---

## 🌐 API Documentation

Swagger/OpenAPI specs for individual endpoints live in `Backend/docs/` as YAML files, served via Flasgger. With the backend running, browse to `http://127.0.0.1:5000/apidocs/` for the interactive docs.

---

## 🤝 Contributing

Issues and PRs welcome. If you're fixing a bug, please include the steps to reproduce it and confirm the fix against a real login flow (register → login → use the feature) rather than just a code review — several past issues in this app only showed up under the actual session/cookie flow, not in isolated component testing.

---

## 📄 License

Developed as part of a Software Engineering project, for educational purposes.
