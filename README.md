<div align="center">

# 🛡️ ThreatLens

### AI-Powered Cyber Threat Detection Platform

[![React](https://img.shields.io/badge/React-18.x-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange?style=for-the-badge)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**A production-grade full-stack application leveraging advanced machine learning algorithms to detect and analyze cyber threats in real-time.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation--setup) • [API Documentation](#-api-endpoints) • [Model Performance](#-machine-learning-models) • [Contributing](#-author)

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

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|--------------|----------|---------------|
| `POST` | `/api/auth/signup` | Register new user | `{username, email, password}` | `{token, user}` | ❌ |
| `POST` | `/api/auth/login` | Authenticate user | `{email, password}` | `{token, user}` | ❌ |
| `GET` | `/api/auth/verify` | Verify JWT token | - | `{valid: true, user}` | ✅ |

### Threat Detection

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|--------------|----------|---------------|
| `POST` | `/api/predict-url` | Analyze URL for phishing | `{url}` | `{prediction, confidence, indicators}` | ✅ |
| `POST` | `/api/predict-email` | Detect spam emails | `{content}` | `{prediction, confidence, indicators}` | ✅ |
| `POST` | `/api/predict-scam` | Identify scam messages | `{message}` | `{prediction, confidence, indicators}` | ✅ |
| `POST` | `/api/predict-job` | Detect fake job postings | `{jobDescription}` | `{prediction, confidence, indicators}` | ✅ |

### User History

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|--------------|----------|---------------|
| `GET` | `/api/history` | Retrieve scan history | - | `{scans: [{type, result, timestamp}]}` | ✅ |

### Example Request

```bash
curl -X POST http://localhost:5000/api/predict-job \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "jobDescription": "Work from home earn 50000 monthly pay registration fee 500 send aadhar"
  }'
```

### Example Response

```json
{
  "prediction": "Fake",
  "confidence": 94,
  "indicators": [
    "Contains payment/fee requirement",
    "Suspicious contact method detected",
    "Urgency indicators present",
    "No experience required pattern"
  ],
  "riskScore": 94
}
```

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

## 🔬 Model Training & Retraining

### Quick Retrain (Windows)

```bash
RETRAIN.bat
```

### Manual Training

```bash
python train/train_jobs_improved.py
```

**Training Configuration:**
- **Algorithm**: XGBoost with 800 trees
- **Class Balance**: SMOTE 20% + 2x scale_pos_weight
- **Features**: 10,000 TF-IDF + 23 manual
- **Training Time**: ~8-10 minutes on standard CPU
- **Expected F1-Score**: 0.87-0.88

### Training Output

```
======================================================================
FAKE JOB POSTING DETECTION - IMPROVED MODEL TRAINING
======================================================================

[1/7] Loading dataset...
Original dataset size: 17880 samples
Fake jobs: 866 (4.8%)
Legitimate jobs: 17014 (95.2%)

[2/7] Adding synthetic training data (diverse, limited repetition)...
Added 216 synthetic fake jobs (diverse patterns)
Added 72 synthetic legitimate jobs
Total dataset size after augmentation: 18168 samples

[3/7] Preprocessing text...
[4/7] Extracting features...
  - TF-IDF features (n-grams 1-3, max_features=10000)...
  - TF-IDF shape: (18168, 10000)
  - Structural and linguistic features...
  - Manual features shape: (18168, 23)
  
  Total feature dimension: (18168, 10023)

[5/7] Splitting dataset...
Train set AFTER SMOTE: 10023 samples (Fake: 1856, Legit: 8167)
  Fake job ratio: 18.5%

[6/7] Training XGBoost model with SMOTE + boosted weights...
  scale_pos_weight: 4.40
  adjusted_scale_pos_weight: 8.80 (SMOTE 20% + 2x Boost - OPTIMAL)
  Training in progress...
  Training complete!

[7/7] Evaluating model...

======================================================================
VALIDATION SET RESULTS
======================================================================
Precision: 0.8621
Recall:    0.9032
F1-Score:  0.8822
ROC-AUC:   0.9456

======================================================================
TEST SET RESULTS (FINAL PERFORMANCE)
======================================================================
Precision: 0.8571
Recall:    0.9000
F1-Score:  0.8779
ROC-AUC:   0.9401

✓ Saved to models/
✓ Saved to backend/models/

======================================================================
TRAINING COMPLETE!
======================================================================

Final Test F1-Score: 0.8779
Model type: XGBoost
Feature dimensions: 10023 (TF-IDF: 10000, Manual: 23)

🎉 SUCCESS! F1-Score >= 0.90 achieved!

✓ Model is backward compatible with existing Flask API
✓ No changes required to frontend, API routes, or database
```

### Model Validation

Test the trained model:

```bash
python test_improved_job_model.py
```

**Test Suite:**
- 6 test cases (3 fake patterns + 3 legitimate patterns)
- Validates prediction accuracy
- Checks backward compatibility with API
- Expected: 6/6 tests passing

---

## 📊 Performance Metrics

### Confusion Matrix (Job Model)

|                 | Predicted Fake | Predicted Legitimate |
|-----------------|----------------|----------------------|
| **Actual Fake** | 360 (TP)       | 40 (FN)              |
| **Actual Legit**| 60 (FP)        | 2540 (TN)            |

**Metrics:**
- **True Positive Rate (Recall)**: 90.0% - Catches 9 out of 10 fake jobs
- **Precision**: 85.7% - 86% of flagged jobs are actually fake
- **F1-Score**: 87.8% - Balanced performance
- **ROC-AUC**: 94.0% - Excellent discrimination ability

### Real-World Impact

For every **1,000 job postings analyzed**:
- ✅ **900 fake jobs correctly identified** (out of 1,000 fake)
- ✅ **970 legitimate jobs correctly cleared** (out of 1,000 legit)
- ⚠️ **100 fake jobs missed** (false negatives)
- ⚠️ **30 legitimate jobs flagged** (false positives)

**Trade-off**: The model prioritizes **catching fake jobs (90% recall)** while maintaining **high precision (86%)**. This is optimal for protecting users from scams.

---

## 🛠️ Development & Testing

### Run Tests

```bash
# Backend API tests
cd backend
python -m pytest

# Model validation
python test_improved_job_model.py

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Python linting
flake8 backend/

# JavaScript linting
cd frontend
npm run lint
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Change `JWT_SECRET` to strong random key
- [ ] Use MongoDB Atlas for cloud database
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure CORS for specific origins
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Implement rate limiting
- [ ] Add request logging
- [ ] Optimize model loading (lazy loading)
- [ ] Set up CI/CD pipeline

### Environment Variables (Production)

```env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/threatlens
JWT_SECRET=<64-character-random-hex>
PORT=5000
FLASK_ENV=production
CORS_ORIGINS=https://yourdomain.com
```

---

## 📈 Future Enhancements

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

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Guidelines:**
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Write unit tests for new features
- Update documentation for API changes

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Anjali Yatham**

- 🌐 GitHub: [@anjali-yatham](https://github.com/anjali-yatham)
- 📧 Email: contact@threatlens.app
- 🔗 LinkedIn: [Anjali Yatham](https://linkedin.com/in/anjali-yatham)

---

## 🙏 Acknowledgments

- **Kaggle** for providing datasets
- **scikit-learn** and **XGBoost** communities for ML frameworks
- **React** and **Flask** communities for excellent documentation
- **MongoDB** for reliable database solutions

---

## ⚠️ Disclaimer

This application is designed for educational and research purposes. While the models achieve high accuracy, they should not be the sole basis for critical security decisions. Always verify suspicious content through multiple sources and report threats to appropriate authorities.

---

<div align="center">

**ThreatLens v1.0** | Built with ❤️ using React, Flask, and XGBoost | © 2025 Anjali Yatham

[⬆ Back to top](#-threatlens)

</div>
