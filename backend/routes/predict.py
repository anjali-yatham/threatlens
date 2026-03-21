import joblib
import os
import pandas as pd
from flask import Blueprint, request, jsonify
from urllib.parse import urlparse
import re
import scipy.sparse as sp
import numpy as np
import jwt
from dotenv import load_dotenv

load_dotenv()

predict_bp = Blueprint("predict", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, '..', 'models')

url_model = joblib.load(os.path.join(MODELS_DIR, 'url_model.pkl'))
url_columns = joblib.load(os.path.join(MODELS_DIR, 'url_columns.pkl'))
text_model = joblib.load(os.path.join(MODELS_DIR, 'text_model.pkl'))
text_vectorizer = joblib.load(os.path.join(MODELS_DIR, 'text_vectorizer.pkl'))
job_model = joblib.load(os.path.join(MODELS_DIR, 'job_model.pkl'))
job_vectorizer = joblib.load(os.path.join(MODELS_DIR, 'job_vectorizer.pkl'))

def check_auth(request):
    token = request.headers.get("Authorization","...").replace("Bearer ","")
    if not token:
        return False
    try:
        jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return True
    except:
        return False

@predict_bp.route("/predict-url", methods=["POST"])
def predict_url():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    url = data.get("url", "").strip()

    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "")
    url_len = max(len(url), 1)
    tld = domain.split(".")[-1] if "." in domain else ""

    known_legit_tlds = ["com","org","net","edu","gov","in","uk","co"]
    suspicious_tlds = ["xyz","top","click","loan","win","gq","tk","ml","cf","io"]
    trusted_brands = ["google","facebook","instagram","amazon","microsoft",
                      "apple","paypal","twitter","youtube","linkedin","github"]

    brand_in_domain = any(b in domain for b in trusted_brands)
    real_brand = any(
        domain == b + "." + t or domain.endswith("." + b + "." + t)
        for b in trusted_brands for t in ["com","org","net","in","co.in","co.uk"]
    )
    subdomain_count = max(len(domain.split(".")) - 2, 0)
    special_chars = sum(1 for c in url if c in "-_~%@!$#")
    letters = sum(c.isalpha() for c in url)
    digits = sum(c.isdigit() for c in url)

    is_phishing = (
        re.match(r"^\d+\.\d+\.\d+\.\d+$", domain) or
        (brand_in_domain and not real_brand) or
        subdomain_count >= 3 or
        tld in ["tk","ml","cf","gq"] or
        "@" in url or url.count(".") > 6
    )
    is_legit = real_brand and url.startswith("https") and subdomain_count <= 1

    if is_phishing:
        return jsonify({"result": "Phishing", "confidence": 95})
    if is_legit:
        return jsonify({"result": "Legitimate", "confidence": 97})

    row = {col: 0 for col in url_columns}
    row["URLLength"] = url_len
    row["DomainLength"] = len(domain)
    row["IsDomainIP"] = 1 if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain) else 0
    row["TLDLength"] = len(tld)
    row["URLSimilarityIndex"] = 0 if (brand_in_domain and not real_brand) else 1
    row["TLDLegitimateProb"] = 0.95 if tld in known_legit_tlds else (0.2 if tld in suspicious_tlds else 0.5)
    row["URLCharProb"] = sum(c.isalnum() for c in url) / url_len
    row["NoOfSubDomain"] = subdomain_count
    row["HasObfuscation"] = 1 if ("%" in url or "@" in url) else 0
    row["NoOfObfuscatedChar"] = url.count("%")
    row["ObfuscationRatio"] = url.count("%") / url_len
    row["NoOfLettersInURL"] = letters
    row["LetterRatioInURL"] = letters / url_len
    row["NoOfDegitsInURL"] = digits
    row["DegitRatioInURL"] = digits / url_len
    row["NoOfEqualsInURL"] = url.count("=")
    row["NoOfQMarkInURL"] = url.count("?")
    row["NoOfAmpersandInURL"] = url.count("&")
    row["NoOfOtherSpecialCharsInURL"] = special_chars
    row["SpacialCharRatioInURL"] = special_chars / url_len
    row["IsHTTPS"] = 1 if url.startswith("https") else 0
    row["DomainTitleMatchScore"] = 1.0 if real_brand else 0.0
    row["URLTitleMatchScore"] = 1.0 if real_brand else 0.0

    df = pd.DataFrame([row])[url_columns]
    prediction = url_model.predict(df)[0]
    confidence = int(max(url_model.predict_proba(df)[0]) * 100)
    result = "Phishing" if prediction == 1 else "Legitimate"
    return jsonify({"result": result, "confidence": confidence})

@predict_bp.route("/predict-email", methods=["POST"])
def predict_email():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    text = data.get("text", "")
    transformed = text_vectorizer.transform([text])
    prediction = text_model.predict(transformed)[0]
    confidence = int(max(text_model.predict_proba(transformed)[0]) * 100)
    result = "Spam/Phishing" if prediction == 1 else "Legitimate"
    return jsonify({"result": result, "confidence": confidence})

@predict_bp.route("/predict-scam", methods=["POST"])
def predict_scam():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    text = data.get("text", "")
    transformed = text_vectorizer.transform([text])
    prediction = text_model.predict(transformed)[0]
    confidence = int(max(text_model.predict_proba(transformed)[0]) * 100)
    result = "Spam/Phishing" if prediction == 1 else "Legitimate"
    return jsonify({"result": result, "confidence": confidence})

@predict_bp.route("/predict-job", methods=["POST"])
def predict_job():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    text = data.get("text", "").lower()
    tfidf_features = job_vectorizer.transform([text])
    has_pay_fee = 1 if any(w in text for w in ["fee","registration","deposit","pay"]) else 0
    has_unrealistic = 1 if any(w in text for w in ["100000","50000","lakh","crore"]) else 0
    has_suspicious = 1 if any(w in text for w in ["whatsapp","aadhar","urgent","guaranteed"]) else 0
    has_no_company = 1 if len(text.strip()) < 100 else 0
    has_email = 1 if ("@gmail" in text or "@yahoo" in text or "@hotmail" in text) else 0
    manual = sp.csr_matrix(np.array([[has_pay_fee, has_unrealistic, has_suspicious, has_no_company, has_email]]))
    combined = sp.hstack([tfidf_features, manual])
    prediction = job_model.predict(combined)[0]
    confidence = int(max(job_model.predict_proba(combined)[0]) * 100)
    result = "Fake" if prediction == 1 else "Legitimate"
    return jsonify({"result": result, "confidence": confidence})