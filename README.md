# 🧑‍⚕️ Shravan – AI-powered Digital Health Solution for Senior Citizens

Shravan is a comprehensive **digital health companion** designed specifically for senior citizens.  
It provides an intuitive and accessible platform to manage health, medications, and wellness.  

Named after the symbol of devotion and care in Indian culture, **Shravan embodies compassionate healthcare for our elderly community.**

---

## 🌟 Overview
- 🏥 Manage health and medications with ease  
- 🤖 AI-powered chatbot assistance  
- 🧘 Yoga and wellness guidance  
- 📊 Smart health monitoring & analytics  
- 💊 Medication reminders with voice support  

---

## 🎯 Mission
Empower senior citizens with technology that:  
- Simplifies healthcare management  
- Promotes wellness and independence  
- Provides peace of mind through intelligent monitoring  

---

## ✨ Key Features

### 🤖 Medical Assistance Chatbot
- Groq AI-powered chatbot for **safe medical guidance**  
- Provides reliable health info *(no diagnostics)*  
- Interactive Q&A for queries  
- Alerts when professional supervision is needed  

---

### 🏥 Hospital & Pharmacy Finder
- Google Maps API integration (via free $300 GCP credits)  
- Location-based search using GPS or locality  
- Customizable distance radius  
- Real-time facility info  

---

### 👨‍⚕️ Doctor Finder
- Specialty-based doctor search nearby  
- Crawls hospital websites with **5-layer deep search**  
- Fuzzy matching for accurate URL selection  
- Selenium scraping + Groq AI-powered info extraction  

---

### 💬 Personalised Companion Chatbot
- Customizable personas for companionship  
- Helps reduce loneliness  
- Tailored conversation styles  
- Future fine-tuning for diverse responses  

---

### 🧘 Yoga Asana Animations
- Sequential AI-generated yoga pose images  
- Displayed in **looped animation style**  
- Backend-managed image delivery  
- Future: user-input → instant asana generation  

---

### 💊 Medical Adherence Assistant
- Medicine reminder notifications  
- Voice-enabled medication entry  
- Speech narration for accessibility  
- Caregiver dashboards *(in progress)*  

---

## 🏗️ Technical Architecture

### 🔹 Frontend (Mobile App)
- Framework: **Flutter (Dart)**  
- Design: Material Design + custom theming  
- State management: StatefulWidget  
- Local storage: SharedPreferences  

### 🔹 Backend (Flask API)
- Framework: **Flask (Python)**  
- Data: JSON-based storage  
- RESTful APIs with docs  
- Google Gemini AI integration  

### 📂 Mobile App Structure

lib/
├── screens/
│ ├── dashboard_screen.dart
│ ├── medication_logs_screen.dart
│ ├── login_screen.dart
│ └── add_prescription_screen.dart
├── services/
│ ├── data_storage_service.dart
│ ├── auth_service.dart
│ └── notification_service.dart
└── constants/
└── theme_constants.dart


---

## 🚀 Getting Started

### ✅ Prerequisites
- Flutter SDK (latest stable)  
- Python 3.8+  
- Android Studio / VS Code  
- Git  

### ⚙️ Setup

**Backend**
```bash
cd Backend
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
python app.py

cd frontend
npm run dev
# or
yarn dev

cd mobile-application/frontend
flutter pub get
flutter run

⚡ Quick Start Scripts

Full App → run_app.ps1 / run_app.sh

Backend Only → run_backend.ps1 / run_backend.sh

Tests → run_test.ps1

📱 User Experience

Modern dashboard with card-based design

Medication logs & reminders

AI chatbots for health + companionship

Easy navigation with swipe gestures

🔒 Privacy & Security

Encrypted local storage

HTTPS-secured API communication

HIPAA-compliant data handling

User consent for data usage

🧪 Testing & QA

Unit tests for API endpoints & mobile features

85%+ code coverage on critical modules

Accessibility & performance testing

📈 Analytics

Medication adherence trends

Wellness tracking with AI insights

Time-series visualization of health patterns

🌐 API Documentation

Available in Backend/docs/ with YAML specs for:

User management

Medication tracking

Health analytics

AI chatbot

Location-based services

🤝 Contributing

We welcome contributions! Please read our guidelines before submitting PRs.

📄 License

Developed as part of a Software Engineering course project.
For educational and healthcare improvement purposes only.

📞 Support

For technical support or healthcare-related queries:
Check the in-app help section or contact our development team.
