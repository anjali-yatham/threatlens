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

print(f"Total rows: {len(data)}")
print(f"Label unique values: {data['label'].unique()}")

tfidf = TfidfVectorizer(max_features=5000)
X = tfidf.fit_transform(data['message'])
y = data['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
print(classification_report(y_test, y_pred))

os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/text_model.pkl')
joblib.dump(tfidf, 'models/text_vectorizer.pkl')
print("Saved successfully!")