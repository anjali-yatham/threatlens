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
from datetime import datetime
from pymongo import MongoClient
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["threatlens"]
scans = db["scans"]

predict_bp = Blueprint("predict", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, '..', 'models')

url_model = joblib.load(os.path.join(MODELS_DIR, 'url_model.pkl'))
url_columns = joblib.load(os.path.join(MODELS_DIR, 'url_columns.pkl'))
text_model = joblib.load(os.path.join(MODELS_DIR, 'text_model.pkl'))
text_vectorizer = joblib.load(os.path.join(MODELS_DIR, 'text_vectorizer.pkl'))
job_model = joblib.load(os.path.join(MODELS_DIR, 'job_model.pkl'))
job_vectorizer = joblib.load(os.path.join(MODELS_DIR, 'job_vectorizer.pkl'))

def save_scan(user_email, scan_type, input_text, result, confidence):
    scans.insert_one({
        "email": user_email,
        "type": scan_type,
        "input": input_text[:200],
        "result": result,
        "confidence": confidence,
        "timestamp": datetime.utcnow(),
        "is_threat": result in ["Phishing", "Spam/Phishing", "Fake"]
    })

def get_user_email(request):
    token = request.headers.get("Authorization","...").replace("Bearer ","")
    try:
        data = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return data["email"]
    except:
        return None

def check_auth(request):
    token = request.headers.get("Authorization","...").replace("Bearer ","")
    if not token:
        return False
    try:
        jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return True
    except:
        return False

def detect_and_translate(text):
    """
    Detect the language of the text and translate to English if needed.
    Returns: (translated_text, detected_language, was_translated)
    """
    if not text or not text.strip():
        return text, "unknown", False
    
    try:
        detected_lang = detect(text)
        
        # If already English, return as-is
        if detected_lang == "en":
            return text, detected_lang, False
        
        # Translate to English
        translator = GoogleTranslator(source=detected_lang, target='en')
        translated_text = translator.translate(text)
        return translated_text, detected_lang, True
        
    except LangDetectException:
        # If language detection fails, assume English
        return text, "unknown", False
    except Exception as e:
        # If translation fails, use original text
        print(f"Translation error: {e}")
        return text, "unknown", False

def analyze_threat_indicators(text):
    """
    Analyze text and return specific threat indicators found.
    Returns: list of threat indicators
    """
    text_lower = text.lower()
    indicators = []
    
    # OTP/Password phishing patterns
    if any(word in text_lower for word in ['otp', 'one time password', 'verification code', 'passcode']):
        indicators.append('OTP/Password Request')
    if any(word in text_lower for word in ['send otp', 'share otp', 'provide otp', 'enter otp']):
        indicators.append('Requests OTP Sharing')
    
    # Personal info phishing
    if any(word in text_lower for word in ['password', 'pin', 'cvv', 'card number', 'account number']):
        indicators.append('Requests Sensitive Credentials')
    if any(word in text_lower for word in ['bank details', 'banking information', 'account details']):
        indicators.append('Requests Banking Information')
    if any(word in text_lower for word in ['aadhar', 'aadhaar', 'pan card', 'social security']):
        indicators.append('Requests ID Documents')
    
    # Urgency patterns
    if any(word in text_lower for word in ['urgent', 'immediately', 'right now', 'asap', 'hurry', 'expire', 'suspended']):
        indicators.append('Creates Urgency/Pressure')
    if any(word in text_lower for word in ['act now', 'limited time', 'expires soon', 'last chance', 'limited positions', '24 hours']):
        indicators.append('Time-Pressure Tactics')
    
    # Prize/lottery scams
    if any(word in text_lower for word in ['won', 'winner', 'prize', 'lottery', 'jackpot', 'lucky draw']):
        indicators.append('Prize/Lottery Scam Pattern')
    if any(word in text_lower for word in ['congratulations', 'congrats', 'selected', 'chosen', 'shortlisted']):
        indicators.append('Unsolicited Selection Claim')
    
    # Financial scams
    if any(word in text_lower for word in ['fee', 'payment', 'deposit', 'advance', 'registration fee', 'refundable']):
        indicators.append('Requests Upfront Payment')
    if any(word in text_lower for word in ['refund', 'cashback', 'reward', 'money back']):
        indicators.append('Promises Money/Refund')
    
    # Suspicious links and contact
    if any(word in text_lower for word in ['click here', 'apply here', 'link', 'http', 'bit.ly', 'tinyurl']):
        indicators.append('Contains Suspicious Links')
    if any(word in text_lower for word in ['whatsapp', 'telegram', 'call us', 'contact us']):
        indicators.append('Suspicious Contact Method')
    
    # Job scam patterns
    if any(word in text_lower for word in ['work from home', 'earn money', 'part time job', 'easy money']):
        indicators.append('Work-from-Home Scam')
    if any(word in text_lower for word in ['guaranteed', 'assured', 'no experience', 'no prior experience']):
        indicators.append('Unrealistic Job Promises')
    
    # Account verification scams
    if any(word in text_lower for word in ['verify', 'confirm', 'validate', 'update', 'authenticate']):
        indicators.append('Account Verification Scam')
    if any(word in text_lower for word in ['blocked', 'suspended', 'deactivated', 'locked']):
        indicators.append('Account Threat Claim')
    
    # Return indicators (max 4), empty list if none found
    return indicators[:4]

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
        result, confidence = "Phishing", 95
    elif is_legit:
        result, confidence = "Legitimate", 97
    else:
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

    email = get_user_email(request)
    if email:
        save_scan(email, "URL", url, result, confidence)

    # Add indicators for phishing URLs
    indicators = []
    if result == "Phishing":
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain):
            indicators.append('IP Address Used Instead of Domain')
        if brand_in_domain and not real_brand:
            indicators.append('Brand Impersonation Detected')
        if not url.startswith("https"):
            indicators.append('No HTTPS Encryption')
        if tld in suspicious_tlds:
            indicators.append('Suspicious TLD Domain')
        if subdomain_count >= 3:
            indicators.append('Excessive Subdomains')
        if "@" in url:
            indicators.append('URL Obfuscation Detected')
        if not indicators:
            indicators.append('Malicious Domain Pattern')
    
    return jsonify({
        "result": result, 
        "confidence": confidence,
        "indicators": indicators[:4]
    })

@predict_bp.route("/predict-email", methods=["POST"])
def predict_email():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    text = data.get("text", "")
    
    # Detect language and translate if needed
    translated_text, detected_lang, was_translated = detect_and_translate(text)
    
    # Use translated text for prediction
    transformed = text_vectorizer.transform([translated_text])
    prediction = text_model.predict(transformed)[0]
    confidence = int(max(text_model.predict_proba(transformed)[0]) * 100)
    result = "Spam/Phishing" if prediction == 1 else "Legitimate"
    
    # Analyze threat indicators from translated text
    indicators = analyze_threat_indicators(translated_text) if result == "Spam/Phishing" else []

    email = get_user_email(request)
    if email:
        save_scan(email, "Email", text, result, confidence)

    return jsonify({
        "result": result, 
        "confidence": confidence,
        "indicators": indicators
    })

@predict_bp.route("/predict-scam", methods=["POST"])
def predict_scam():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    text = data.get("text", "")
    
    # Detect language and translate if needed
    translated_text, detected_lang, was_translated = detect_and_translate(text)
    
    # Use translated text for prediction
    transformed = text_vectorizer.transform([translated_text])
    prediction = text_model.predict(transformed)[0]
    confidence = int(max(text_model.predict_proba(transformed)[0]) * 100)
    result = "Spam/Phishing" if prediction == 1 else "Legitimate"
    
    # Analyze threat indicators from translated text
    indicators = analyze_threat_indicators(translated_text) if result == "Spam/Phishing" else []

    email = get_user_email(request)
    if email:
        save_scan(email, "Scam", text, result, confidence)

    return jsonify({
        "result": result, 
        "confidence": confidence,
        "indicators": indicators
    })

@predict_bp.route("/predict-job", methods=["POST"])
def predict_job():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    text = data.get("text", "")
    
    # Detect language and translate if needed
    translated_text, detected_lang, was_translated = detect_and_translate(text)
    
    # Use translated text for prediction (lowercase for job model)
    text_lower = translated_text.lower()
    tfidf_features = job_vectorizer.transform([text_lower])
    has_pay_fee = 1 if any(w in text_lower for w in ["fee","registration","deposit","pay","payment","refundable"]) else 0
    has_unrealistic = 1 if any(w in text_lower for w in ["100000","50000","lakh","crore"]) else 0
    has_suspicious = 1 if any(w in text_lower for w in ["whatsapp","aadhar","urgent","guaranteed"]) else 0
    has_no_company = 1 if len(text_lower.strip()) < 100 else 0
    has_email = 1 if ("@gmail" in text_lower or "@yahoo" in text_lower or "@hotmail" in text_lower) else 0
    manual = sp.csr_matrix(np.array([[has_pay_fee, has_unrealistic, has_suspicious, has_no_company, has_email]]))
    combined = sp.hstack([tfidf_features, manual])
    prediction = job_model.predict(combined)[0]
    confidence = int(max(job_model.predict_proba(combined)[0]) * 100)
    result = "Fake" if prediction == 1 else "Legitimate"
    
    # Rule-based override: Strong fake indicators should force fake classification
    strong_fake_indicators = [
        ("registration fee" in text_lower or "verification fee" in text_lower or "document fee" in text_lower),
        ("refundable fee" in text_lower or "security deposit" in text_lower or "processing fee" in text_lower),
        (has_pay_fee == 1 and has_suspicious == 1),  # Fee + suspicious contact method
        ("whatsapp" in text_lower and "fee" in text_lower),  # WhatsApp + fee is always suspicious
    ]
    
    if any(strong_fake_indicators):
        result = "Fake"
        confidence = max(confidence, 75)  # Boost confidence to at least 75%
    
    # Extract and check URLs in job posting
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls_found = re.findall(url_pattern, text_lower)
    
    if urls_found and result == "Legitimate":
        # Check the first URL found against phishing detection
        for url in urls_found:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            
            if not domain:
                continue
                
            # Suspicious patterns in job posting URLs
            suspicious_url_patterns = [
                # Suspicious TLDs for job sites
                domain.endswith(('.tk', '.ml', '.cf', '.gq', '.ga', '.xyz', '.top', '.click', '.info', '.online')),
                # IP address instead of domain
                re.match(r"^\d+\.\d+\.\d+\.\d+$", domain),
                # Too many subdomains (e.g., jobs.apply.company-hiring.tk)
                len(domain.split(".")) > 3,
                # Generic/vague company names with job keywords in .org/.com/.net
                (domain.endswith(('.org', '.net')) and any(word in domain for word in ['job', 'jobs', 'career', 'careers', 'hiring', 'work', 'apply', 'global', 'international', 'recruit'])),
                # Domain contains multiple hyphens (e.g., company-jobs-hiring.org)
                domain.count('-') >= 2,
                # Non-standard ports or obfuscation
                '@' in url,
                # Very short or suspicious domain names
                (len(domain.split('.')[0]) <= 4 and domain.endswith(('.org', '.com'))),
            ]
            
            if any(suspicious_url_patterns):
                result = "Fake"
                confidence = max(confidence, 80)
                break
    
    # Analyze threat indicators from translated text
    indicators = analyze_threat_indicators(translated_text) if result == "Fake" else []

    email = get_user_email(request)
    if email:
        save_scan(email, "Job", text, result, confidence)

    return jsonify({
        "result": result, 
        "confidence": confidence,
        "indicators": indicators
    })

@predict_bp.route("/history", methods=["GET"])
def get_history():
    token = request.headers.get("Authorization","...").replace("Bearer ","")
    try:
        data = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        email = data["email"]
    except:
        return jsonify({"error": "Unauthorized"}), 401

    history = list(scans.find(
        {"email": email},
        {"_id": 0}
    ).sort("timestamp", -1).limit(20))

    for scan in history:
        scan["timestamp"] = scan["timestamp"].strftime("%d %b %Y %I:%M %p")

    return jsonify(history)