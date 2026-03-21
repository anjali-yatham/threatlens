import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
from scipy.sparse import hstack
import joblib
import nltk
from nltk.corpus import stopwords
import string

nltk.download('stopwords')

# Load data
data = pd.read_csv('data/fake_job_postings.csv')
data['combined'] = (
    data['title'].fillna('') + ' ' +
    data['company_profile'].fillna('') + ' ' +
    data['description'].fillna('') + ' ' +
    data['requirements'].fillna('')
)
data = data[['combined', 'fraudulent']].dropna()
data.columns = ['message', 'label']

# Add extra fake job examples
fake_job_texts = [
    "work from home data entry earn 50000 monthly pay registration fee 500 send aadhar bank details whatsapp guaranteed income no interview",
    "urgent hiring part time no qualification needed earn 30000 pay security deposit guaranteed income no interview required",
    "online typing job earn money daily no experience pay small fee get started send bank account details immediately",
    "fake internship program earn while learning pay 2000 registration fee certificate work from home no skills whatsapp",
    "hiring home based workers earn 500 per hour pay joining fee 1500 rupees receive work kit immediately",
    "government job guarantee pay 5000 processing fee central government job no exam send documents bank details",
    "abroad job offer salary 200000 monthly pay visa processing fee 10000 send passport bank account urgently",
    "data entry jobs work from home earn 40000 monthly submit fee 800 get training material send personal details",
]
legitimate_job_texts = [
    "software engineer python django rest api postgresql 2 years experience bangalore 8 LPA apply official careers portal",
    "data analyst sql python tableau 1 year experience hyderabad 6 lpa send resume hr formal interview process",
    "frontend developer react javascript html css 2 years experience pune salary negotiable apply linkedin",
    "machine learning engineer tensorflow pytorch deep learning research bangalore 12 lpa formal hiring",
    "java backend developer spring boot microservices aws 3 years experience chennai 9 lpa apply company website",
    "product manager roadmap agile scrum 5 years experience bangalore 15 lpa mba preferred formal process",
    "devops engineer kubernetes docker ci cd pipeline 3 years hyderabad 10 lpa apply naukri linkedin",
    "hr recruiter talent acquisition 2 years experience delhi 4 lpa submit resume official company email",
]

# Repeat extra data 15 times
fake_job_texts = fake_job_texts * 15
legitimate_job_texts = legitimate_job_texts * 15

# Create DataFrame for extra data
extra_data = pd.DataFrame({
    'label': [1] * len(fake_job_texts) + [0] * len(legitimate_job_texts),
    'message': fake_job_texts + legitimate_job_texts
})

# Combine original and extra data
data = pd.concat([data, extra_data], ignore_index=True)

# Preprocess text
data['message'] = data['message'].str.lower()
data['message'] = data['message'].str.translate(str.maketrans('', '', string.punctuation))
stop_words = set(stopwords.words('english'))
data['message'] = data['message'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))

# Feature extraction using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X_tfidf = vectorizer.fit_transform(data['message'])

# Manual binary features
manual_features = pd.DataFrame({
    'has_pay_fee': data['message'].str.contains('fee|registration|deposit|pay', regex=True).astype(int),
    'has_unrealistic_salary': data['message'].str.contains('100000|50000|lakh|crore', regex=True).astype(int),
    'has_suspicious_words': data['message'].str.contains('whatsapp|aadhar|urgent|guaranteed', regex=True).astype(int),
    'has_no_company': data['message'].str.contains('company_profile', regex=False).astype(int),
    'has_email_in_post': data['message'].str.contains('@gmail|@yahoo', regex=True).astype(int),
})

# Combine features
X = hstack([X_tfidf, manual_features])
y = data['label'].values

# Split data: 70% train, 15% validation, 15% test
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Handle imbalance using SMOTE
smote = SMOTE(random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# Train Random Forest
rf_model = RandomForestClassifier(n_estimators=200, max_depth=20, class_weight='balanced', random_state=42)
rf_model.fit(X_train, y_train)
rf_val_pred = rf_model.predict(X_val)
rf_val_f1 = f1_score(y_val, rf_val_pred)

# Train Logistic Regression
lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr_model.fit(X_train, y_train)
lr_val_pred = lr_model.predict(X_val)
lr_val_f1 = f1_score(y_val, lr_val_pred)

# Compare models
print("Validation Scores:")
print(f"Random Forest F1 Score: {rf_val_f1:.4f}")
print(f"Logistic Regression F1 Score: {lr_val_f1:.4f}")

# Select the better model
if rf_val_f1 > lr_val_f1:
    best_model = rf_model
    print("Selected Model: Random Forest")
else:
    best_model = lr_model
    print("Selected Model: Logistic Regression")

# Evaluate on test set
y_test_pred = best_model.predict(X_test)
print("Test Set Results:")
print(confusion_matrix(y_test, y_test_pred))
print(f"Precision: {precision_score(y_test, y_test_pred):.4f}")
print(f"Recall: {recall_score(y_test, y_test_pred):.4f}")
print(f"F1 Score: {f1_score(y_test, y_test_pred):.4f}")

# Save the best model, vectorizer, and manual feature names
os.makedirs('models', exist_ok=True)
joblib.dump(best_model, 'models/job_model.pkl')
joblib.dump(vectorizer, 'models/job_vectorizer.pkl')
joblib.dump(manual_features.columns.tolist(), 'models/job_features.pkl')
print("Model saved successfully!")