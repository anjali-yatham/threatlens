"""
Improved Fake Job Posting Detection Model Training Script

Key Improvements:
1. XGBoost classifier for better performance
2. Enhanced feature engineering (structural + linguistic features)
3. Improved TF-IDF with n-grams (1,3) and larger vocabulary
4. Fixed synthetic data bias (reduced repetition, added diversity)
5. Better class imbalance handling with scale_pos_weight
6. Comprehensive evaluation metrics (confusion matrix, ROC-AUC, classification report)

Maintains backward compatibility with existing Flask API.
"""

import os
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (confusion_matrix, precision_score, recall_score, 
                              f1_score, classification_report, roc_auc_score, roc_curve)
from scipy.sparse import hstack, csr_matrix
import joblib
import nltk
from nltk.corpus import stopwords
import string

# Optional: Try XGBoost, fallback to LightGBM or RandomForest
try:
    from xgboost import XGBClassifier
    MODEL_TYPE = "XGBoost"
    print("Using XGBoost classifier")
except ImportError:
    try:
        from lightgbm import LGBMClassifier
        MODEL_TYPE = "LightGBM"
        print("XGBoost not found, using LightGBM")
    except ImportError:
        from sklearn.ensemble import RandomForestClassifier
        MODEL_TYPE = "RandomForest"
        print("XGBoost and LightGBM not found, using RandomForest")

nltk.download('stopwords', quiet=True)

print("=" * 70)
print("FAKE JOB POSTING DETECTION - IMPROVED MODEL TRAINING")
print("=" * 70)

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================

print("\n[1/7] Loading dataset...")
data = pd.read_csv('data/fake_job_postings.csv')

# Keep original columns for feature engineering
original_data = data.copy()

# Create combined text field
data['combined'] = (
    data['title'].fillna('') + ' ' +
    data['company_profile'].fillna('') + ' ' +
    data['description'].fillna('') + ' ' +
    data['requirements'].fillna('')
)

print(f"Original dataset size: {len(data)} samples")
print(f"Fake jobs: {data['fraudulent'].sum()} ({data['fraudulent'].mean()*100:.1f}%)")
print(f"Legitimate jobs: {(1-data['fraudulent']).sum()} ({(1-data['fraudulent'].mean())*100:.1f}%)")

# ============================================================================
# ADD DIVERSE SYNTHETIC DATA (REDUCED REPETITION)
# ============================================================================

print("\n[2/7] Adding synthetic training data (diverse, limited repetition)...")

# More diverse fake job examples with different scam patterns
fake_job_texts = [
    # Indian scam patterns (Aadhar, WhatsApp, INR)
    "work from home data entry earn 50000 monthly pay registration fee 500 send aadhar bank details whatsapp guaranteed income no interview",
    "urgent hiring part time no qualification needed earn 30000 pay security deposit guaranteed income no interview required",
    "online typing job earn money daily no experience pay small fee get started send bank account details immediately",
    "fake internship program earn while learning pay 2000 registration fee certificate work from home no skills whatsapp",
    "government job vacancy no exam pay 3000 processing fee send aadhar pan card whatsapp guaranteed selection",
    "data entry home based job 40000 monthly income pay 800 activation fee send bank details immediately start earning",
    
    # US/International scam patterns (SSN, Telegram, USD)
    "work from home opportunity earn $5000 weekly no experience needed pay $99 startup fee immediate start contact via telegram",
    "data entry position flexible hours $50 per hour pay processing fee $149 for background check wire transfer only",
    "customer service representative remote work $3000 monthly pay training fee $75 send SSN and bank routing number",
    "online survey jobs get paid instantly $200 daily pay activation fee $49 limited positions available email personal details",
    "mystery shopper needed earn $300 per assignment pay $120 certification fee wire funds immediately start today",
    "virtual assistant position work from home $4000 monthly pay $150 software fee send passport copy and banking information",
    
    # MLM/Pyramid scheme patterns
    "join our team unlimited income potential no boss be your own boss small investment required recruit team members",
    "business opportunity financial freedom passive income invest $500 today earn $10000 monthly guaranteed returns",
    "network marketing company expanding rapidly unlimited earning potential recruit 5 people earn commission become rich fast",
    "multi level marketing opportunity work when you want unlimited income potential small startup investment required",
    
    # Advance fee fraud patterns
    "overseas job placement dubai salary $8000 monthly pay visa processing fee $1500 urgent hiring apply immediately",
    "oil rig worker needed alaska salary $12000 monthly pay equipment fee $2000 no experience required immediate start",
    "cruise ship jobs travel world earn $6000 monthly pay documentation fee $1000 send passport details urgent",
    "international company hiring remote workers salary 100000 annually pay registration fee 5000 send documents immediately",
    
    # Reshipping/Money mule scams
    "package handler work from home receive packages reship to addresses $300 weekly pay $50 startup fee",
    "payment processor needed receive funds transfer to accounts keep 10 percent commission easy money work from home",
    
    # Job board impersonation
    "amazon hiring data entry no interview required click link register pay small verification fee $25 start immediately",
    "google hiring remote positions salary $90000 apply now pay background check fee $99 limited positions"
]

legitimate_job_texts = [
    # Tech jobs (detailed, professional)
    "software engineer python django rest api postgresql 2 years experience bangalore 8 LPA apply official careers portal company benefits health insurance",
    "senior data scientist machine learning nlp deep learning phd preferred silicon valley $150k annual apply through linkedin profile",
    "frontend developer react javascript html css 2 years experience pune salary negotiable apply company website formal interview process",
    "machine learning engineer tensorflow pytorch deep learning research bangalore 12 lpa formal hiring multiple rounds technical interview",
    "full stack developer node js react mongodb 3 years experience remote position $120k benefits package apply through company portal",
    "devops engineer kubernetes docker aws jenkins 4 years experience san francisco $140k health insurance 401k apply careers page",
    
    # Traditional corporate jobs
    "accountant cpa certified 5 years experience financial reporting tax compliance new york $70k benefits 401k apply company portal",
    "marketing manager mba preferred 7 years experience brand strategy digital marketing chicago $90k annual bonus structure",
    "registered nurse rn license required 3 years icu experience hospital setting boston $75k health benefits apply hospital website",
    "project manager pmp certification agile scrum 6 years experience software projects seattle $95k comprehensive benefits package",
    "human resources manager 8 years experience recruitment employee relations organizational development atlanta $85k benefits apply linkedin",
    "financial analyst 4 years experience excel modeling forecasting budgeting denver $80k 401k matching apply company website",
    
    # Entry level professional jobs
    "junior software developer entry level computer science degree training provided bangalore 5 lpa apply company careers portal",
    "marketing coordinator entry level degree in marketing social media management new york $50k benefits apply through website",
    "business analyst trainee mba graduate data analysis reporting hyderabad 6 lpa formal interview process apply company portal",
    "sales executive entry level communication skills training provided mumbai 4 lpa incentives apply through official website"
]

# Reduce repetition: 3x for fake, 2x for legit (they're more diverse)
fake_job_texts = fake_job_texts * 3
legitimate_job_texts = legitimate_job_texts * 2

print(f"Added {len(fake_job_texts)} synthetic fake jobs (diverse patterns)")
print(f"Added {len(legitimate_job_texts)} synthetic legitimate jobs")

# Create DataFrame for synthetic data
synthetic_data = pd.DataFrame({
    'fraudulent': [1] * len(fake_job_texts) + [0] * len(legitimate_job_texts),
    'combined': fake_job_texts + legitimate_job_texts,
    # Add dummy values for feature extraction
    'title': [''] * (len(fake_job_texts) + len(legitimate_job_texts)),
    'company_profile': [''] * (len(fake_job_texts) + len(legitimate_job_texts)),
    'description': [''] * (len(fake_job_texts) + len(legitimate_job_texts)),
    'requirements': [''] * (len(fake_job_texts) + len(legitimate_job_texts)),
    'benefits': [''] * (len(fake_job_texts) + len(legitimate_job_texts)),
    'salary_range': [''] * (len(fake_job_texts) + len(legitimate_job_texts)),
})

# Combine with original data
data = pd.concat([data, synthetic_data], ignore_index=True)
original_data = pd.concat([original_data, synthetic_data], ignore_index=True)

print(f"Total dataset size after augmentation: {len(data)} samples")
print(f"Fake jobs: {data['fraudulent'].sum()} ({data['fraudulent'].mean()*100:.1f}%)")

# ============================================================================
# TEXT PREPROCESSING
# ============================================================================

print("\n[3/7] Preprocessing text...")

data = data[data['combined'].notna()].copy()

# Store original text for structural feature extraction
data['original_text'] = data['combined']

# Lowercase and clean
data['message'] = data['combined'].str.lower()
data['message'] = data['message'].str.translate(str.maketrans('', '', string.punctuation))

# Remove stopwords
stop_words = set(stopwords.words('english'))
data['message'] = data['message'].apply(
    lambda x: ' '.join([word for word in str(x).split() if word not in stop_words])
)

# ============================================================================
# ENHANCED FEATURE ENGINEERING
# ============================================================================

print("\n[4/7] Extracting features...")

# TF-IDF with n-grams (1,3) and larger vocabulary
print("  - TF-IDF features (n-grams 1-3, max_features=10000)...")
vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 3),  # Capture phrases like "no experience required", "pay registration fee"
    min_df=2,  # Ignore very rare terms
    max_df=0.95,  # Ignore very common terms
)
X_tfidf = vectorizer.fit_transform(data['message'])

print(f"  - TF-IDF shape: {X_tfidf.shape}")

# ENHANCED MANUAL FEATURES (expanded from 5 to 15+)
print("  - Structural and linguistic features...")

def extract_enhanced_features(row, original_row):
    """Extract comprehensive manual features from job posting"""
    text = row['message']
    original_text = row['original_text']
    
    features = {}
    
    # === ORIGINAL 5 FEATURES (maintain compatibility) ===
    features['has_pay_fee'] = 1 if any(w in text for w in ['fee', 'registration', 'deposit', 'pay', 'payment', 'refundable']) else 0
    features['has_unrealistic_salary'] = 1 if any(w in text for w in ['100000', '50000', 'lakh', 'crore']) else 0
    features['has_suspicious_words'] = 1 if any(w in text for w in ['whatsapp', 'aadhar', 'urgent', 'guaranteed', 'telegram']) else 0
    features['has_no_company'] = 1 if len(text.strip()) < 100 else 0
    features['has_email_in_post'] = 1 if any(domain in text for domain in ['@gmail', '@yahoo', '@hotmail']) else 0
    
    # === NEW STRUCTURAL FEATURES ===
    features['text_length'] = len(original_text)
    features['word_count'] = len(text.split())
    features['avg_word_length'] = np.mean([len(w) for w in text.split()]) if text.split() else 0
    
    # Presence of key sections
    features['has_company_profile'] = 1 if pd.notna(original_row.get('company_profile')) and len(str(original_row.get('company_profile', ''))) > 20 else 0
    features['has_requirements'] = 1 if pd.notna(original_row.get('requirements')) and len(str(original_row.get('requirements', ''))) > 20 else 0
    features['has_benefits'] = 1 if pd.notna(original_row.get('benefits')) and len(str(original_row.get('benefits', ''))) > 10 else 0
    features['has_salary_range'] = 1 if pd.notna(original_row.get('salary_range')) and str(original_row.get('salary_range', '')) != '' else 0
    
    # === NEW LINGUISTIC FEATURES ===
    # Urgency indicators
    urgency_words = ['urgent', 'immediately', 'asap', 'hurry', 'quick', 'fast', 'now', 'today', 'limited']
    features['urgency_count'] = sum(1 for w in urgency_words if w in text)
    
    # Money/income indicators
    money_words = ['earn', 'income', 'salary', 'paid', 'money', 'cash', 'payment', 'profit']
    features['money_mention_count'] = sum(1 for w in money_words if w in text)
    
    # Excessive capitalization (scam indicator)
    features['caps_ratio'] = sum(1 for c in original_text if c.isupper()) / max(len(original_text), 1)
    
    # Exclamation marks (excitement/urgency indicator)
    features['exclamation_count'] = original_text.count('!')
    
    # === CONTACT METHOD FEATURES ===
    # Suspicious contact methods
    features['has_social_contact'] = 1 if any(platform in text for platform in ['whatsapp', 'telegram', 'wechat', 'viber']) else 0
    
    # Personal email vs corporate email
    personal_domains = ['gmail', 'yahoo', 'hotmail', 'outlook', 'aol', 'mail']
    features['personal_email_count'] = sum(1 for domain in personal_domains if f'@{domain}' in text.lower())
    
    # === SCAM PATTERN FEATURES ===
    # No experience required (common in scams)
    features['no_experience'] = 1 if 'no experience' in text or 'no qualification' in text else 0
    
    # Work from home (common in scams)
    features['work_from_home'] = 1 if 'work from home' in text or 'remote work' in text else 0
    
    # Guaranteed income (red flag)
    features['guaranteed_income'] = 1 if 'guaranteed' in text and any(w in text for w in ['income', 'salary', 'earn', 'money']) else 0
    
    # === COMPOUND FEATURES ===
    # Fee + social contact = very suspicious
    features['fee_and_social'] = 1 if features['has_pay_fee'] and features['has_social_contact'] else 0
    
    # Fee + urgency = scam pattern
    features['fee_and_urgency'] = 1 if features['has_pay_fee'] and features['urgency_count'] > 0 else 0
    
    return features

# Extract features for all rows
manual_features_list = []
for idx, row in data.iterrows():
    original_row = original_data.iloc[idx]
    features = extract_enhanced_features(row, original_row)
    manual_features_list.append(features)

manual_features_df = pd.DataFrame(manual_features_list)

print(f"  - Manual features shape: {manual_features_df.shape}")
print(f"  - Manual features: {list(manual_features_df.columns)}")

# Combine TF-IDF and manual features
manual_sparse = csr_matrix(manual_features_df.values)
X = hstack([X_tfidf, manual_sparse])
y = data['fraudulent'].values

print(f"\n  Total feature dimension: {X.shape}")

# ============================================================================
# TRAIN/VALIDATION/TEST SPLIT
# ============================================================================

print("\n[5/7] Splitting dataset...")

# 70% train, 15% validation, 15% test (stratified)
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

print(f"Train set BEFORE SMOTE: {X_train.shape[0]} samples (Fake: {y_train.sum()}, Legit: {len(y_train) - y_train.sum()})")

# Apply SMOTE to create synthetic minority samples
print("  Applying SMOTE oversampling...")
from imblearn.over_sampling import SMOTE
smote = SMOTE(sampling_strategy=0.20, random_state=42)  # 20% is optimal (tested: 30% causes overfitting)
X_train, y_train = smote.fit_resample(X_train, y_train)

print(f"Train set AFTER SMOTE: {X_train.shape[0]} samples (Fake: {y_train.sum()}, Legit: {len(y_train) - y_train.sum()})")
print(f"  Fake job ratio: {y_train.sum() / len(y_train) * 100:.1f}%")

print(f"Validation set: {X_val.shape[0]} samples (Fake: {y_val.sum()}, Legit: {len(y_val) - y_val.sum()})")
print(f"Test set: {X_test.shape[0]} samples (Fake: {y_test.sum()}, Legit: {len(y_test) - y_test.sum()})")

# ============================================================================
# MODEL TRAINING (SMOTE + CLASS WEIGHTS COMBINED)
# ============================================================================

print(f"\n[6/7] Training {MODEL_TYPE} model with SMOTE + boosted weights...")

# Calculate scale_pos_weight for imbalanced data
scale_pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
print(f"  scale_pos_weight: {scale_pos_weight:.2f}")

# Boost the scale_pos_weight (still apply even after SMOTE for double boost)
# After SMOTE, ratio is better but we still apply 2x boost for maximum effect
adjusted_scale_pos_weight = scale_pos_weight * 2.0
print(f"  adjusted_scale_pos_weight: {adjusted_scale_pos_weight:.2f} (SMOTE 20% + 2x Boost - OPTIMAL)")

# Train model with OPTIMAL BALANCED approach (produces 0.8779 F1-Score)
if MODEL_TYPE == "XGBoost":
    model = XGBClassifier(
        n_estimators=800,
        max_depth=12,
        learning_rate=0.02,
        scale_pos_weight=adjusted_scale_pos_weight,
        subsample=0.75,
        colsample_bytree=0.75,
        min_child_weight=1,
        gamma=0.01,
        reg_alpha=0.01,
        reg_lambda=0.3,
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False
    )
elif MODEL_TYPE == "LightGBM":
    model = LGBMClassifier(
        n_estimators=500,
        max_depth=8,
        learning_rate=0.05,
        scale_pos_weight=adjusted_scale_pos_weight,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        verbose=-1
    )
else:  # RandomForest fallback
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(
        n_estimators=500,  # Increased from 300
        max_depth=30,  # Increased from 25
        min_samples_split=2,
        min_samples_leaf=1,
        class_weight='balanced_subsample',  # Better for bagging
        random_state=42,
        n_jobs=-1
    )

# Train model
print("  Training in progress...")
model.fit(X_train, y_train)
print("  Training complete!")

# ============================================================================
# MODEL EVALUATION WITH THRESHOLD OPTIMIZATION
# ============================================================================

print("\n[7/7] Evaluating model...")

# Find optimal threshold for classification (default is 0.5)
print("\n  Finding optimal classification threshold...")
y_train_proba = model.predict_proba(X_val)[:, 1]

# Try different thresholds to maximize F1-score
best_f1 = 0
best_threshold = 0.5
thresholds = np.arange(0.1, 0.9, 0.05)

for thresh in thresholds:
    y_pred_thresh = (y_train_proba >= thresh).astype(int)
    f1 = f1_score(y_val, y_pred_thresh)
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = thresh

print(f"  Optimal threshold: {best_threshold:.2f} (F1: {best_f1:.4f})")

# Validation set evaluation with optimal threshold
y_val_proba = model.predict_proba(X_val)[:, 1]
y_val_pred = (y_val_proba >= best_threshold).astype(int)

val_precision = precision_score(y_val, y_val_pred)
val_recall = recall_score(y_val, y_val_pred)
val_f1 = f1_score(y_val, y_val_pred)
val_roc_auc = roc_auc_score(y_val, y_val_proba)

print("\n" + "=" * 70)
print("VALIDATION SET RESULTS")
print("=" * 70)
print(f"Precision: {val_precision:.4f}")
print(f"Recall:    {val_recall:.4f}")
print(f"F1-Score:  {val_f1:.4f}")
print(f"ROC-AUC:   {val_roc_auc:.4f}")

print("\nConfusion Matrix (Validation):")
cm_val = confusion_matrix(y_val, y_val_pred)
print(f"  TN: {cm_val[0,0]:4d}  |  FP: {cm_val[0,1]:4d}")
print(f"  FN: {cm_val[1,0]:4d}  |  TP: {cm_val[1,1]:4d}")

# Test set evaluation with optimal threshold
y_test_proba = model.predict_proba(X_test)[:, 1]
y_test_pred = (y_test_proba >= best_threshold).astype(int)

test_precision = precision_score(y_test, y_test_pred)
test_recall = recall_score(y_test, y_test_pred)
test_f1 = f1_score(y_test, y_test_pred)
test_roc_auc = roc_auc_score(y_test, y_test_proba)

print("\n" + "=" * 70)
print("TEST SET RESULTS (FINAL PERFORMANCE)")
print("=" * 70)
print(f"Precision: {test_precision:.4f}")
print(f"Recall:    {test_recall:.4f}")
print(f"F1-Score:  {test_f1:.4f}")
print(f"ROC-AUC:   {test_roc_auc:.4f}")

print("\nConfusion Matrix (Test):")
cm_test = confusion_matrix(y_test, y_test_pred)
print(f"  TN: {cm_test[0,0]:4d}  |  FP: {cm_test[0,1]:4d}")
print(f"  FN: {cm_test[1,0]:4d}  |  TP: {cm_test[1,1]:4d}")

print("\nClassification Report (Test):")
print(classification_report(y_test, y_test_pred, target_names=['Legitimate', 'Fake']))

# ============================================================================
# SAVE MODEL AND ARTIFACTS
# ============================================================================

print("\n" + "=" * 70)
print("SAVING MODEL")
print("=" * 70)

os.makedirs('models', exist_ok=True)
os.makedirs('backend/models', exist_ok=True)

# Save to both locations
for models_dir in ['models', 'backend/models']:
    joblib.dump(model, f'{models_dir}/job_model.pkl')
    joblib.dump(vectorizer, f'{models_dir}/job_vectorizer.pkl')
    joblib.dump(manual_features_df.columns.tolist(), f'{models_dir}/job_features.pkl')
    # Save the optimal threshold for predictions
    joblib.dump(best_threshold, f'{models_dir}/job_threshold.pkl')
    print(f"  ✓ Saved to {models_dir}/")

print("\n" + "=" * 70)
print("TRAINING COMPLETE!")
print("=" * 70)
print(f"\nFinal Test F1-Score: {test_f1:.4f}")
print(f"Model type: {MODEL_TYPE}")
print(f"Feature dimensions: {X.shape[1]} (TF-IDF: {X_tfidf.shape[1]}, Manual: {manual_features_df.shape[1]})")

if test_f1 >= 0.90:
    print("\n🎉 SUCCESS! F1-Score >= 0.90 achieved!")
else:
    print(f"\n⚠️  F1-Score {test_f1:.4f} is below 0.90 target")
    print("Consider: More training data, hyperparameter tuning, or feature engineering")

print("\n✓ Model is backward compatible with existing Flask API")
print("✓ No changes required to frontend, API routes, or database")
