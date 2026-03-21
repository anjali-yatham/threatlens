from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
from urllib.parse import urlparse
import re
import itertools
import scipy.sparse as sp
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Load models and vectorizers at startup
url_model = joblib.load('models/url_model.pkl')
url_columns = joblib.load('models/url_columns.pkl')
text_model = joblib.load('models/text_model.pkl')
text_vectorizer = joblib.load('models/text_vectorizer.pkl')
job_model = joblib.load('models/job_model.pkl')
job_vectorizer = joblib.load('models/job_vectorizer.pkl')

# Route for index page
@app.route('/')
def index():
    return render_template('index.html')

# Route for URL prediction
@app.route('/predict-url', methods=['POST'])
def predict_url():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace('www.', '')
    path = parsed.path
    url_len = max(len(url), 1)
    tld = domain.split('.')[-1] if '.' in domain else ''
    
    known_legit_tlds = ['com', 'org', 'net', 'edu', 'gov', 'in', 'uk', 'co']
    suspicious_tlds = ['xyz', 'top', 'click', 'loan', 'win', 'gq', 'tk', 'ml', 'cf', 'io', 'biz']
    trusted_brands = ['google', 'facebook', 'instagram', 'amazon', 
                      'microsoft', 'apple', 'paypal', 'twitter', 
                      'youtube', 'linkedin', 'netflix', 'github']
    
    brand_in_domain = any(brand in domain for brand in trusted_brands)
    real_brand = any(
        domain == brand + '.' + t or domain.endswith('.' + brand + '.' + t)
        for brand in trusted_brands
        for t in ['com', 'org', 'net', 'in', 'co.in', 'co.uk']
    )
    subdomain_count = max(len(domain.split('.')) - 2, 0)
    special_chars = sum(1 for c in url if c in '-_~%@!$#')
    letters = sum(c.isalpha() for c in url)
    digits = sum(c.isdigit() for c in url)
    
    # Build feature dict matching trained column names exactly
    row = {col: 0 for col in url_columns}
    row['URLLength'] = url_len
    row['DomainLength'] = len(domain)
    row['IsDomainIP'] = 1 if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain) else 0
    row['TLDLength'] = len(tld)
    row['URLSimilarityIndex'] = 0 if (brand_in_domain and not real_brand) else 1
    row['TLDLegitimateProb'] = (
        0.95 if tld in known_legit_tlds else
        0.2 if tld in suspicious_tlds else 0.5
    )
    row['URLCharProb'] = sum(c.isalnum() for c in url) / url_len
    row['NoOfSubDomain'] = subdomain_count
    row['HasObfuscation'] = 1 if ('%' in url or '@' in url) else 0
    row['NoOfObfuscatedChar'] = url.count('%')
    row['ObfuscationRatio'] = url.count('%') / url_len
    row['NoOfLettersInURL'] = letters
    row['LetterRatioInURL'] = letters / url_len
    row['NoOfDegitsInURL'] = digits
    row['DegitRatioInURL'] = digits / url_len
    row['NoOfEqualsInURL'] = url.count('=')
    row['NoOfQMarkInURL'] = url.count('?')
    row['NoOfAmpersandInURL'] = url.count('&')
    row['NoOfOtherSpecialCharsInURL'] = special_chars
    row['SpacialCharRatioInURL'] = special_chars / url_len
    row['IsHTTPS'] = 1 if url.startswith('https') else 0
    row['NoOfSelfRedirect'] = max(url.lower().count(domain) - 1, 0)
    row['DomainTitleMatchScore'] = 1.0 if real_brand else (
        0.0 if brand_in_domain and not real_brand else 0.5
    )
    row['URLTitleMatchScore'] = row['DomainTitleMatchScore']
    row['CharContinuationRate'] = max(
        len(list(g)) 
        for _, g in __import__('itertools').groupby(url)
    ) / url_len
    
    # Override model prediction with rule-based logic for clear cases
    is_definitely_phishing = (
        row['IsDomainIP'] == 1 or
        (brand_in_domain and not real_brand) or
        subdomain_count >= 3 or
        tld in ['tk', 'ml', 'cf', 'gq'] or
        '@' in url or
        url.count('.') > 6
    )
    is_definitely_legit = (
        real_brand and 
        url.startswith('https') and 
        subdomain_count <= 1
    )
    
    if is_definitely_phishing:
        return jsonify({"result": "Phishing", "confidence": 95})
    elif is_definitely_legit:
        return jsonify({"result": "Legitimate", "confidence": 97})
    else:
        df = pd.DataFrame([row])[url_columns]
        prediction = url_model.predict(df)[0]
        confidence = int(max(url_model.predict_proba(df)[0]) * 100)
        result = 'Phishing' if prediction == 1 else 'Legitimate'
        return jsonify({"result": result, "confidence": confidence})

# Route for email prediction
@app.route('/predict-email', methods=['POST'])
def predict_email():
    data = request.get_json()
    text = data.get('text', '')

    # Transform text and predict
    transformed_text = text_vectorizer.transform([text])
    prediction = text_model.predict(transformed_text)[0]
    confidence = max(text_model.predict_proba(transformed_text)[0]) * 100
    result = 'Spam/Phishing' if prediction == 1 else 'Legitimate'

    return jsonify({"result": result, "confidence": int(confidence)})

# Route for scam prediction
@app.route('/predict-scam', methods=['POST'])
def predict_scam():
    return predict_email()  # Reuse the same logic as predict-email

# Route for job prediction
@app.route('/predict-job', methods=['POST'])
def predict_job():
    try:
        data = request.get_json()
        text = data.get('text', '').lower()

        # Step 1: TF-IDF transform (5000 features)
        tfidf_features = job_vectorizer.transform([text])

        # Step 2: Manual features (5 flags) - must match training exactly
        has_pay_fee = 1 if any(w in text for w in ['fee', 'registration', 'deposit', 'pay']) else 0
        has_unrealistic_salary = 1 if any(w in text for w in ['100000', '50000', 'lakh', 'crore']) else 0
        has_suspicious_words = 1 if any(w in text for w in ['whatsapp', 'aadhar', 'urgent', 'guaranteed']) else 0
        has_no_company = 1 if len(text.strip()) < 50 else 0
        has_email_in_post = 1 if ('@gmail' in text or '@yahoo' in text) else 0

        manual_features = sp.csr_matrix(np.array([
            [
                has_pay_fee,
                has_unrealistic_salary,
                has_suspicious_words,
                has_no_company,
                has_email_in_post
            ]
        ]))

        # Step 3: Combine both feature sets - now 5005 features total
        combined = sp.hstack([tfidf_features, manual_features])

        # Step 4: Predict
        prediction = job_model.predict(combined)[0]
        confidence = int(max(job_model.predict_proba(combined)[0]) * 100)
        result = 'Fake' if prediction == 1 else 'Legitimate'

        return jsonify({"result": result, "confidence": confidence})

    except Exception as e:
        print(f"Job prediction error: {e}")
        return jsonify({"result": "Error", "confidence": 0, "error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(port=5000, debug=True)