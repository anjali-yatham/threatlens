# ThreatLens - AI-Powered Cyber Threat Detection

![React](https://img.shields.io/badge/React-18-blue)
![Flask](https://img.shields.io/badge/Flask-Python-green)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-brightgreen)
![ML](https://img.shields.io/badge/ML-Scikit--learn-orange)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)

A full-stack AI-powered cybersecurity web application that detects phishing URLs, spam emails, scam messages and fake job postings in real-time using machine learning.

---

## Features
- JWT-based authentication with MongoDB
- 4 AI detection modules: URL, Email, Scam, Job Posting
- Real-time threat analysis with confidence score
- Risk score progress bar with detected threat indicators
- Scan history saved per user in MongoDB
- Responsive cybersecurity glassmorphism dark theme UI
- Protected routes — dashboard requires login

---

## Tech Stack

### Frontend
- React.js + Vite
- React Router DOM for client-side routing
- Axios for API calls
- CSS Glassmorphism dark cybersecurity theme
- Orbitron + Rajdhani fonts

### Backend
- Python Flask REST API
- PyMongo + MongoDB
- bcrypt for password hashing
- PyJWT for token authentication
- python-dotenv for environment variables

### Machine Learning Models

| Detection Type | Algorithm | Dataset Size | F1 Score |
|----------------|-----------|--------------|----------|
| URL Phishing | Random Forest | 235,795 URLs | 1.00 |
| Email Spam | Logistic Regression | 5,574 messages | 0.94 |
| Scam Messages | Logistic Regression | 5,574 messages | 0.94 |
| Fake Job Posts | Random Forest | 17,880 listings | 0.82 |

---

## Project Structure
```
ThreatLens/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── SignupPage.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
├── backend/
│   ├── routes/
│   │   ├── auth.py
│   │   └── predict.py
│   ├── models/
│   ├── app.py
│   └── .env
├── data/
└── train/
```

---

## Installation & Setup

### Prerequisites
- Node.js v18+
- Python 3.10+
- MongoDB running locally

### Backend Setup
```bash
cd backend
pip install flask flask-cors pymongo bcrypt pyjwt python-dotenv scikit-learn joblib scipy pandas
```

Create `backend/.env`:
```
MONGO_URI=mongodb://localhost:27017/threatlens
JWT_SECRET=threatlens_secret_key_2025
PORT=5000
```
```bash
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/auth/signup | Register user | No |
| POST | /api/auth/login | Login user | No |
| GET | /api/auth/verify | Verify JWT | Yes |
| POST | /api/predict-url | Analyze URL | Yes |
| POST | /api/predict-email | Analyze email | Yes |
| POST | /api/predict-scam | Analyze message | Yes |
| POST | /api/predict-job | Analyze job post | Yes |
| GET | /api/history | Scan history | Yes |

---

## How It Works

1. User registers or logs in — credentials stored in MongoDB
2. JWT token issued on successful authentication
3. User pastes suspicious content in dashboard
4. React sends POST to Flask API with JWT header
5. Flask extracts features from input
6. Trained ML model predicts threat or safe
7. Result returned with confidence score and indicators
8. Scan saved to MongoDB history

---

## Author

Developed by Anjali Yatham
ThreatLens v1.0 | 2025
All rights reserved
