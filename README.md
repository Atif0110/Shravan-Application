# 🧑‍⚕️ Shravan — Digital Health Companion for Senior Citizens

Shravan is a health-management platform built for senior citizens and the people who support them. It combines medicine reminders, symptom logging, AI-powered health assistance, yoga guidance, and doctor, hospital, and pharmacy discovery into one platform with dedicated dashboards for seniors, caretakers, and NGO/health workers.

Named after the symbol of devotion and care in Indian culture, **Shravan** aims to make day-to-day healthcare management simpler for elderly users while giving caregivers better visibility into their wellbeing.

> This repository primarily contains the **Vue.js + Flask web application**. A separate Flutter mobile application is available under `mobile-application/` and has its own README.

---

# ✨ Features

### 💊 Medicine Reminder
- Add medicines with dosage, timing, and frequency.
- Mark medicines as taken.
- Daily reminder status is preserved even after refreshing or revisiting the application.

### 🤖 AI Health Chatbot
- Powered by **Groq LLM**.
- Answers general health-related questions.
- Designed to provide educational information, **not medical diagnosis**.

### 💬 Personal Companion Chatbot
- Friendly AI companion for conversation.
- Supports voice input and voice output.
- Intended to help reduce loneliness among elderly users.

### 🧘 Age-Friendly Yoga
- Browse yoga asanas suitable for senior citizens.
- Watch instructional videos.
- Learn benefits and precautions.

### 🏥 Doctor, Hospital & Pharmacy Finder
- Search doctors stored in the application's database.
- Find nearby hospitals and pharmacies using Google Maps.
- Doctor profiles can be enriched using AI-powered web scraping.

### 📊 Community Health Trends
- NGO dashboard provides symptom trend analysis.
- View aggregated reports by pincode.
- Helps identify community-level health patterns.

### 👥 Multiple User Roles
- Senior Citizen (`user`)
- Caretaker (`caretaker`)
- NGO / Health Worker (`ngo`)

Each role has its own dashboard and permissions.

---

# 🏗 Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | Vue 3, Composition API, Vue Router, Pinia, Vite |
| Backend | Flask, SQLAlchemy, Flask-Session |
| Database | SQLite |
| Authentication | Flask Session Cookies |
| AI APIs | Groq, Google Gemini |
| External APIs | Google Maps Places API, YouTube Data API |
| Styling | CSS |

---

# 📂 Project Structure

```
Shravan-Application/
│
├── Backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── routes_*.py
│   ├── modules/
│   ├── docs/
│   ├── populate_yoga_data.py
│   ├── requirements.txt
│   └── .env.example
│
├── Frontend/
│   ├── src/
│   │   ├── views/
│   │   ├── router/
│   │   ├── stores/
│   │   └── components/
│   ├── package.json
│   └── .env.example
│
└── mobile-application/
```

---

# 🚀 Getting Started

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- Git

---

## Backend Setup

```bash
cd Backend

python -m venv env

# Windows
env\Scripts\activate

# Linux / macOS
source env/bin/activate

pip install -r requirements.txt

cp .env.example .env
```

### Configure `.env`

```env
GROQ_API_KEY=your_groq_api_key

GOOGLE_MAPS_API_KEY=your_google_maps_api_key

GEMINI_API_KEY=your_gemini_api_key

YOUTUBE_API_KEY=your_youtube_api_key

SECRET_KEY=generate_a_secret_key

FLASK_DEBUG=False

ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

SESSION_COOKIE_SECURE=False
```

Generate a Flask secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Start the backend:

```bash
python app.py
```

Backend runs at:

```
http://127.0.0.1:5000
```

On first launch the application automatically:

- Creates the SQLite database
- Creates default roles
- Seeds yoga data

No manual database setup is required.

---

## Frontend Setup

```bash
cd Frontend

npm install

cp .env.example .env

npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

Open the application and register an account.

---

# 🔐 Authentication

Shravan uses **server-side Flask sessions** instead of JWT authentication.

After login:

- Flask creates a session.
- The browser stores a secure session cookie.
- Every authenticated request includes that cookie.

The frontend communicates using:

```javascript
credentials: "include"
```

### Local Development

Use either:

```
localhost
```

for both frontend and backend

or

```
127.0.0.1
```

for both.

Do **not** mix them, otherwise cookies may not be sent correctly.

### Production

Enable secure cookies:

```env
SESSION_COOKIE_SECURE=True
```

Also ensure that:

- HTTPS is enabled.
- `ALLOWED_ORIGINS` includes your frontend URL.

---

# 👥 User Roles

| Role | Dashboard | Description |
|------|-----------|-------------|
| user | UserDashboard | Senior citizen dashboard |
| caretaker | CareTakerDashboard | Caregiver dashboard |
| ngo | TertiaryUserDashboard | NGO / Health Worker dashboard |

---

# ⚠ Known Limitations

### Caretaker Linking

Caretaker accounts currently cannot manage medicines for a specific senior citizen.

Medicine reminders belong only to the logged-in account.

Future work includes:

- Caretaker ↔ Senior linking
- Shared medicine schedules
- Permission management

---

### Doctor Finder

Advanced doctor profile enrichment requires:

```
GROQ_API_KEY
```

Without it, basic doctor search still works.

---

### Voice Recognition

Voice input depends on the browser's Web Speech API.

Best supported on:

- Google Chrome
- Microsoft Edge

Limited support exists in Firefox and Safari.

---

### Mobile Application

The Flutter application is maintained separately.

Its feature set may not exactly match the web application.

---

# 🧪 Testing

Run chatbot tests:

```bash
cd Backend

python -m pytest test_personal_chatbot.py
```

The project currently relies mostly on manual testing.

A complete automated test suite is planned.

---

# 🌐 API Documentation

Flasgger automatically serves Swagger documentation.

After starting the backend visit:

```
http://127.0.0.1:5000/apidocs/
```

Individual endpoint specifications are stored in:

```
Backend/docs/
```

---

# 🤝 Contributing

Contributions are welcome.

When submitting a pull request:

1. Describe the problem.
2. Explain your solution.
3. Include reproduction steps.
4. Test the complete login flow:

```
Register
↓

Login
↓

Use the feature
```

Many bugs only appear during the full authenticated workflow.

---

# 📄 License

Developed as part of a Software Engineering academic project for educational purposes.

---

## 👨‍💻 Authors

Developed by the Shravan project team as part of a Software Engineering course project.
