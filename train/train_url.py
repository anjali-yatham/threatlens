import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, classification_report
import joblib
import nltk

nltk.download('stopwords')

# Load data
file_path = 'data/phishing_urls.csv'
data = pd.read_csv(file_path)

# Keep only numeric columns, target column is 'label'
numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
data = data[numeric_cols]

# Drop rows where label is NaN
data = data.dropna(subset=['label'])

# Separate features and target
X = data.drop(columns=['label'])
y = data['label'].values

# Split data: 70% train, 15% validation, 15% test
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Handle imbalanced data using class_weight='balanced'
class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weights_dict = {i: class_weights[i] for i in range(len(class_weights))}

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

# Save the best model and feature columns
os.makedirs('models', exist_ok=True)
joblib.dump(best_model, 'models/url_model.pkl')
joblib.dump(X.columns.tolist(), 'models/url_columns.pkl')
print("Model saved successfully!")