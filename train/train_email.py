import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, classification_report
import joblib
import nltk
from nltk.corpus import stopwords
import string

nltk.download('stopwords')

# Load data
sms = pd.read_csv('data/sms_spam.csv', encoding='latin-1', header=None, skiprows=1)
sms.columns = ['label', 'message', 'c3', 'c4', 'c5']
sms = sms[['label', 'message']]
sms = sms[sms['label'].isin(['ham', 'spam'])]
sms['label'] = sms['label'].map({'ham': 0, 'spam': 1})

# Add phishing and legitimate examples
phishing_texts = [
    "Your account suspended verify credit card paypal immediately click here",
    "URGENT you won cash prize send bank account OTP immediately",
    "Dear customer unusual activity detected enter credentials to restore",
    "Work from home earn 100000 monthly pay registration fee send aadhar",
    "Your Netflix subscription failed update payment method immediately",
    "IRS tax refund pending verify social security number to receive refund",
    "Free gift card winner confirm address credit card to receive prize",
    "Security alert gmail account accessed unknown device verify now",
    "Your SBI account blocked update KYC details immediately suspension",
    "Congratulations lottery winner send bank details claim reward now",
]
legitimate_texts = [
    "Hi meeting confirmed for tomorrow at 3pm please bring the report",
    "Hey are you coming to college tomorrow assignment deadline reminder",
    "Team lunch scheduled Friday 1pm office cafeteria please confirm attendance",
    "Your order shipped arrives in 3 to 5 business days track online",
    "Interview confirmation software engineer position Monday 10am office",
    "Monthly newsletter company updates new products upcoming events schedule",
    "Please complete feedback form for training session attended last week",
    "Salary credited to account for March please check bank statement",
    "Office closed Monday public holiday normal operations resume Tuesday",
    "Your appointment confirmed tomorrow 2pm please arrive 10 minutes early",
]

# Repeat extra data 10 times
phishing_texts = phishing_texts * 10
legitimate_texts = legitimate_texts * 10

# Create DataFrame for extra data
extra_data = pd.DataFrame({
    'label': [1] * len(phishing_texts) + [0] * len(legitimate_texts),
    'message': phishing_texts + legitimate_texts
})

# Combine original and extra data
data = pd.concat([sms, extra_data], ignore_index=True)

# Drop NaN and preprocess text
data = data.dropna()
data['message'] = data['message'].str.lower()
data['message'] = data['message'].str.translate(str.maketrans('', '', string.punctuation))
stop_words = set(stopwords.words('english'))
data['message'] = data['message'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))

# Feature extraction using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(data['message'])
y = data['label'].values

# Split data: 70% train, 15% validation, 15% test
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Train Naive Bayes
nb_model = MultinomialNB()
nb_model.fit(X_train, y_train)
nb_val_pred = nb_model.predict(X_val)
nb_val_f1 = f1_score(y_val, nb_val_pred)

# Train Logistic Regression
lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr_model.fit(X_train, y_train)
lr_val_pred = lr_model.predict(X_val)
lr_val_f1 = f1_score(y_val, lr_val_pred)

# Compare models
print("Validation Scores:")
print(f"Naive Bayes F1 Score: {nb_val_f1:.4f}")
print(f"Logistic Regression F1 Score: {lr_val_f1:.4f}")

# Select the better model
if nb_val_f1 > lr_val_f1:
    best_model = nb_model
    print("Selected Model: Naive Bayes")
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

# Save the best model and vectorizer
os.makedirs('models', exist_ok=True)
joblib.dump(best_model, 'models/text_model.pkl')
joblib.dump(vectorizer, 'models/text_vectorizer.pkl')
print("Model saved successfully!")