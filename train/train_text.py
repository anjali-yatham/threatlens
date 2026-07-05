import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

file_path = 'data/sms_spam.csv'
data = pd.read_csv(file_path, encoding='latin-1', header=None, skiprows=1)
data.columns = ['label', 'message', 'col3', 'col4', 'col5']
data = data.drop(columns=['col3', 'col4', 'col5'])
data = data[data['label'].isin(['ham', 'spam'])]
data['label'] = data['label'].map({'ham': 0, 'spam': 1})
data = data.dropna(subset=['label', 'message'])
data['label'] = data['label'].astype(int)

print(f"Original dataset: {len(data)} rows")

# Add diverse synthetic training data - EXPANDED
phishing_texts = [
    # Account/Security threats
    "Your account suspended verify credit card paypal immediately",
    "URGENT you won cash prize send bank account OTP immediately",
    "Dear customer unusual activity detected enter credentials restore",
    "Security alert gmail account accessed unknown device verify now",
    "Your SBI account blocked update KYC details immediately",
    "Bank account will be closed verify identity send documents today",
    "Account locked suspicious activity verify credentials immediately",
    
    # Prize/Lottery scams
    "Congratulations lottery winner send bank details claim reward now",
    "You have won lottery prize claim now send details immediately",
    "Lucky draw winner you won lakhs rupees send details",
    "You won free iPhone claim prize send shipping details now",
    "Prize money waiting provide account number claim today",
    "Congratulations selected for reward send personal information",
    
    # Work from home scams
    "Work from home earn 100000 monthly pay registration fee",
    "Easy money work from home no experience pay small fee start",
    "Earn thousands weekly part time job pay registration deposit",
    "Data entry online earn daily pay activation fee get started",
    
    # Tax/Refund scams
    "IRS tax refund pending verify social security number receive",
    "Tax refund approved deposit pending confirm bank details now",
    "Government refund waiting claim send bank account details",
    
    # Payment/Subscription scams
    "Your Netflix subscription failed update payment method immediately",
    "Payment failed update card information click link urgent",
    "Subscription expired renew now send payment details",
]

legitimate_texts = [
    # Normal communications
    "Hi meeting confirmed for tomorrow at 3pm bring report",
    "Hey are you coming to college tomorrow assignment deadline",
    "Team lunch scheduled Friday 1pm office cafeteria confirm",
    "Your order shipped arrives in 3 to 5 business days",
    "Interview confirmation software engineer position Monday 10am",
    "Monthly newsletter company updates new products events",
    "Please complete feedback form training session last week",
    "Salary credited to account for March check statement",
    "Office closed Monday public holiday operations resume Tuesday",
    "Your appointment confirmed tomorrow 2pm arrive 10 minutes early",
    
    # More legitimate patterns
    "Meeting rescheduled next week will send calendar invite",
    "Project deadline extended three days team notification",
    "Your package delivered check mailbox reception desk",
    "Reminder doctor appointment scheduled Friday morning",
    "Class timing changed new schedule starts Monday",
    "Application received will contact within five business days",
    "Thank you purchase receipt attached email",
    "Webinar registration confirmed link sent day before",
    "Report submitted successfully review in progress",
    "Team event planned next month details to follow",
]

# Repeat 20 times for stronger training
phishing_texts = phishing_texts * 20
legitimate_texts = legitimate_texts * 20

# Create synthetic DataFrame
synthetic_data = pd.DataFrame({
    'label': [1] * len(phishing_texts) + [0] * len(legitimate_texts),
    'message': phishing_texts + legitimate_texts
})

# Combine with original data
data = pd.concat([data, synthetic_data], ignore_index=True)

print(f"After adding synthetic data: {len(data)} rows")
print(f"Spam: {data['label'].sum()}, Ham: {(data['label'] == 0).sum()}")
print(f"Label unique values: {data['label'].unique()}")

# Preprocess text (match prediction API preprocessing)
import string
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

print("\nPreprocessing text...")
data['message'] = data['message'].str.lower()
data['message'] = data['message'].str.translate(str.maketrans('', '', string.punctuation))

# Remove stopwords
stop_words = set(stopwords.words('english'))
data['message'] = data['message'].apply(
    lambda x: ' '.join([word for word in str(x).split() if word not in stop_words])
)

tfidf = TfidfVectorizer(max_features=5000)
X = tfidf.fit_transform(data['message'])
y = data['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Use balanced class weights for better performance
model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
print(classification_report(y_test, y_pred))

os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/text_model.pkl')
joblib.dump(tfidf, 'models/text_vectorizer.pkl')

# Also copy to backend/models
os.makedirs('backend/models', exist_ok=True)
joblib.dump(model, 'backend/models/text_model.pkl')
joblib.dump(tfidf, 'backend/models/text_vectorizer.pkl')

print("Saved successfully to models/ and backend/models/!")