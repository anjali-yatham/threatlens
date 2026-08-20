<div align="center">

# 🛡️ ThreatLens

### AI-Powered Cyber Threat Detection Platform

> **Live Demo:** [🚀 Try ThreatLens](https://threatlens-g3sgal404-divyanjalis-projects.vercel.app)  
> **Backend API:** [⚙️ Render API](https://threatlens-4ye4.onrender.com)

[![React](https://img.shields.io/badge/React-18.x-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange?style=for-the-badge)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**A production-grade full-stack application leveraging advanced machine learning algorithms to detect and analyze cyber threats in real-time.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation--setup) • [How It Works](#-how-it-works) • [Model Performance](#-machine-learning-models)

</div>

---

## 📋 Overview

**ThreatLens** is an intelligent cybersecurity platform that combines state-of-the-art machine learning models with modern web technologies to protect users from digital threats. The system analyzes multiple threat vectors including phishing URLs, spam emails, scam messages, and fraudulent job postings with high accuracy and confidence scoring.

### 🎯 Key Highlights

- **Multi-Threat Detection**: 4 specialized AI modules trained on 259,000+ data points
- **Real-Time Analysis**: Sub-second threat classification with confidence scoring
- **Advanced ML Pipeline**: XGBoost, SMOTE oversampling, and 23 engineered features
- **Secure Architecture**: JWT authentication, bcrypt encryption, protected routes
- **User Intelligence**: Personalized scan history and threat indicator tracking
- **Professional UI/UX**: Glassmorphism design with cybersecurity-themed aesthetics

---

## ✨ Features

### 🔐 Security & Authentication
- **JWT-based authentication** with MongoDB user management
- **bcrypt password hashing** for secure credential storage
- **Protected API routes** requiring token validation
- **Session management** with automatic token refresh

### 🤖 AI-Powered Detection Modules
1. **URL Phishing Detector** - Analyzes domain features, HTTPS status, URL structure
2. **Email Spam Classifier** - Detects phishing emails and suspicious content
3. **Scam Message Analyzer** - Identifies fraudulent SMS and messaging patterns
4. **Fake Job Posting Detector** - Advanced XGBoost model with 88% F1-score

### 📊 User Experience
- **Real-time threat analysis** with confidence percentage
- **Visual risk indicators** with progress bars and threat markers
- **Complete scan history** per user account
- **Responsive design** optimized for desktop and mobile
- **Dark-themed UI** with cybersecurity glassmorphism effects

---

## 🏗️ Tech Stack

### Frontend Architecture
| Technology | Purpose | Version |
|------------|---------|---------|
| **React.js** | UI framework with hooks and context | 18.x |
| **Vite** | Build tool and dev server | 5.x |
| **React Router** | Client-side routing and navigation | 6.x |
| **Axios** | HTTP client for API communication | 1.x |
| **CSS3** | Custom glassmorphism styling | - |

### Backend Architecture
| Technology | Purpose | Version |
|------------|---------|---------|
| **Flask** | RESTful API framework | 3.0+ |
| **MongoDB** | NoSQL database for users/history | 7.0+ |
| **PyMongo** | MongoDB driver for Python | 4.x |
| **PyJWT** | Token generation and validation | 2.x |
| **bcrypt** | Password hashing | 4.x |

### Machine Learning Stack
| Library | Purpose | Version |
|---------|---------|---------|
| **XGBoost** | Gradient boosting for job model | 2.x |
| **scikit-learn** | Classical ML algorithms | 1.3+ |
| **imbalanced-learn** | SMOTE oversampling | 0.11+ |
| **scipy** | Sparse matrix operations | 1.11+ |
| **pandas** | Data preprocessing | 2.x |
| **joblib** | Model serialization | 1.3+ |

---

## 🤖 Machine Learning Models

### Model Performance Summary

| Detection Type | Algorithm | Training Samples | Features | F1-Score | Precision | Recall | Status |
|----------------|-----------|-----------------|----------|----------|-----------|--------|--------|
| **URL Phishing** | Random Forest | 235,795 URLs | Feature Engineering | **1.00** | 1.00 | 1.00 | 🟢 Production |
| **Email Spam** | Logistic Regression | 5,574 messages | TF-IDF (5K) | **0.94** | 0.93 | 0.95 | 🟢 Production |
| **Scam Messages** | Logistic Regression | 5,574 messages | TF-IDF (5K) | **0.94** | 0.93 | 0.95 | 🟢 Production |
| **Fake Job Posts** | **XGBoost + SMOTE** | 17,880 postings | **10,023 features** | **0.88** | 0.86 | 0.90 | 🟢 **Optimized** |

### 🚀 Job Model Optimization Journey

The fake job posting detector underwent significant improvements to handle severe class imbalance (5% fraudulent jobs):

#### Baseline → Production Evolution

| Metric | Baseline (v1.0) | Improved (v2.0) | Improvement |
|--------|----------------|----------------|-------------|
| **Algorithm** | Random Forest | **XGBoost** | Better for imbalanced data |
| **Features** | 5 basic | **23 engineered** | +360% feature richness |
| **TF-IDF** | 5K unigrams | **10K n-grams (1-3)** | +100% vocabulary |
| **Class Balance** | Basic SMOTE | **SMOTE 20% + 2x weights** | Dual-strategy approach |
| **F1-Score** | 0.76 | **0.88** | **+14.8% improvement** |
| **Total Features** | 5,005 | **10,023** | +100% dimensionality |

#### Advanced Features Engineered (23 total)

**Structural Features** (7):
- Text length, word count, average word length
- Company profile presence, requirements section
- Benefits description, salary range indication

**Linguistic Features** (8):
- Urgency indicator count (urgent, immediately, ASAP)
- Money mention frequency (earn, income, salary)
- Capitalization ratio, exclamation mark count
- Social media contact methods (WhatsApp, Telegram)
- Personal email domain detection

**Scam Pattern Features** (8):
- Fee/payment requirement detection
- "No experience required" pattern
- Work-from-home indicators
- Guaranteed income promises
- Compound features (fee + urgency, fee + social contact)

#### Model Architecture

```
Input Text → Preprocessing → Feature Extraction → XGBoost → Threshold Optimization → Prediction
                                    ↓
                        [TF-IDF 10K + Manual 23]
                                    ↓
                            SMOTE Oversampling
                                    ↓
                      XGBoost (800 trees, depth 12)
                                    ↓
                        Optimal Threshold (0.55)
```

**Hyperparameters:**
- `n_estimators`: 800 trees
- `max_depth`: 12 levels
- `learning_rate`: 0.02
- `scale_pos_weight`: Auto-calculated + 2x boost
- `subsample`: 0.75
- `colsample_bytree`: 0.75
- `reg_lambda`: 0.3

---

## 📁 Project Structure

```
ThreatLens/
│
├── 📂 frontend/                    # React application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx    # Hero + features
│   │   │   ├── LoginPage.jsx      # User authentication
│   │   │   ├── SignupPage.jsx     # User registration
│   │   │   └── Dashboard.jsx      # Main threat detection UI
│   │   ├── context/
│   │   │   └── AuthContext.jsx    # Global auth state
│   │   ├── App.jsx                # Root component + routing
│   │   ├── main.jsx               # React entry point
│   │   └── index.css              # Glassmorphism styles
│   ├── public/                     # Static assets
│   ├── package.json
│   └── vite.config.js
│
├── 📂 backend/                     # Flask API
│   ├── routes/
│   │   ├── auth.py                # Signup, login, verify
│   │   └── predict.py             # ML prediction endpoints
│   ├── models/                     # Trained .pkl files
│   │   ├── job_model.pkl          # XGBoost (3.1 MB)
│   │   ├── job_vectorizer.pkl     # TF-IDF
│   │   ├── job_features.pkl       # Feature names
│   │   ├── job_threshold.pkl      # Optimal cutoff
│   │   ├── text_model.pkl         # Email/SMS classifier
│   │   ├── text_vectorizer.pkl
│   │   ├── url_model.pkl          # URL detector (5.1 MB)
│   │   └── url_columns.pkl
│   ├── app.py                      # Flask server
│   └── .env                        # Environment variables
│
├── 📂 data/                        # Training datasets
│   ├── fake_job_postings.csv      # 17,880 job listings
│   ├── sms_spam.csv               # 5,574 messages
│   └── phishing_urls.csv          # 235,795 URLs
│
├── 📂 train/                       # Training scripts
│   ├── train_jobs_improved.py     # XGBoost + SMOTE (optimized)
│   ├── train_jobs.py              # Baseline model
│   ├── train_text.py              # Email/SMS model
│   ├── train_email.py             # Alternative text model
│   └── train_url.py               # URL model
│
├── 📄 test_improved_job_model.py  # Validation suite
├── 📄 RETRAIN.bat                 # Model retraining automation
├── 📄 README.md                   # Documentation
├── 📄 .gitignore                  # Git exclusions
└── 📄 requirements.txt            # Python dependencies
```

---

## 🚀 Installation & Setup

### Prerequisites

Ensure you have the following installed on your system:

- **Node.js** v18.0+ ([Download](https://nodejs.org/))
- **Python** 3.10+ ([Download](https://www.python.org/))
- **MongoDB** v7.0+ ([Download](https://www.mongodb.com/try/download/community))
- **Git** ([Download](https://git-scm.com/))

### 1️⃣ Clone Repository

```bash
git clone https://github.com/anjali-yatham/threatlens.git
cd threatlens
```

### 2️⃣ Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install flask flask-cors pymongo bcrypt pyjwt python-dotenv scikit-learn joblib scipy pandas xgboost imbalanced-learn nltk langdetect deep-translator
```

#### Configure Environment Variables

Create `backend/.env` file:

```env
MONGO_URI=mongodb://localhost:27017/threatlens
JWT_SECRET=your_super_secret_key_here_change_in_production
PORT=5000
```

**Security Note**: Generate a strong JWT secret for production using:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Start MongoDB

```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
```

#### Launch Flask Server

```bash
python app.py
```

Server runs at: `http://localhost:5000`

### 3️⃣ Frontend Setup

#### Install Node Dependencies

```bash
cd ../frontend
npm install
```

#### Start Development Server

```bash
npm run dev
```

Application opens at: `http://localhost:5173`

---

## 🎓 How It Works

### System Architecture

```
┌─────────────┐      HTTPS       ┌──────────────┐      API       ┌─────────────┐
│   React UI  │ ───────────────> │  Flask API   │ ────────────> │   MongoDB   │
│  (Frontend) │ <─────────────── │  (Backend)   │ <──────────── │  (Database) │
└─────────────┘    JWT Token     └──────────────┘   User Data   └─────────────┘
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │  ML Models    │
                                 │  (.pkl files) │
                                 └───────────────┘
```

### Detection Pipeline

1. **User Authentication**
   - User registers/logs in via React frontend
   - Credentials validated against MongoDB
   - JWT token issued with 24-hour expiration

2. **Threat Submission**
   - User pastes suspicious content in dashboard
   - React sends POST request with JWT header
   - Flask validates token and extracts user ID

3. **Feature Extraction**
   - Text preprocessing (lowercase, punctuation removal, stopword filtering)
   - TF-IDF vectorization (10,000 features for jobs)
   - Manual feature engineering (23 features for jobs)

4. **ML Prediction**
   - Features fed into trained model (XGBoost for jobs)
   - Probability scores calculated
   - Optimal threshold applied for classification

5. **Result Processing**
   - Rule-based overrides for high-confidence patterns
   - Threat indicators identified and extracted
   - Confidence percentage calculated

6. **Response & Storage**
   - Prediction returned to frontend with confidence
   - Scan saved to MongoDB user history
   - UI displays result with visual indicators

### Job Detection Workflow (Detailed)

```
Input Text
    │
    ▼
Language Detection → [If non-English] → Translation to English
    │
    ▼
Text Preprocessing
    ├─ Lowercase conversion
    ├─ Punctuation removal
    └─ Stopword filtering
    │
    ▼
Feature Extraction
    ├─ TF-IDF Vectorization (10,000 features, n-grams 1-3)
    └─ Manual Features (23 engineered features)
    │
    ▼
Feature Combination → Sparse Matrix (10,023 dimensions)
    │
    ▼
XGBoost Model → Probability Score
    │
    ▼
Threshold Classification (0.55 cutoff)
    │
    ▼
Rule-Based Overrides
    ├─ High-confidence patterns
    ├─ Fee + Social media contact
    └─ Guaranteed income + Urgency
    │
    ▼
Threat Indicators Extraction
    │
    ▼
Final Prediction + Confidence + Indicators
```

---

## � Future Enhancements

- [ ] Real-time threat feed integration
- [ ] Browser extension for instant URL checking
- [ ] Email plugin for Gmail/Outlook
- [ ] Multi-language support (currently English only)
- [ ] Advanced analytics dashboard
- [ ] API rate limiting per user tier
- [ ] Machine learning model retraining pipeline
- [ ] Mobile app (React Native)
- [ ] Threat intelligence sharing network
- [ ] Explainable AI (SHAP values for predictions)

---

<div align="center">

**ThreatLens v1.0** | Built with ❤️ using React, Flask, and XGBoost | © 2025 Anjali Yatham

[⬆ Back to top](#-threatlens)

</div>
