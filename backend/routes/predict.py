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

# Load optimal threshold for job model (default to 0.5 if not found)
try:
    job_threshold = joblib.load(os.path.join(MODELS_DIR, 'job_threshold.pkl'))
except:
    job_threshold = 0.5  # Default threshold

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
    
    # Suspicious links and contact - FIXED: Only check for actual URLs/link text
    # Check for actual URLs (http/https) or link shorteners
    if any(word in text_lower for word in ['http://', 'https://', 'bit.ly', 'tinyurl', 'goo.gl', 'ow.ly', 'short.link']):
        indicators.append('Contains Suspicious Links')
    # Check for "click here" or "click link" phrases (not just the word "link")
    elif any(phrase in text_lower for phrase in ['click here', 'click link', 'tap link', 'open link', 'visit link']):
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
    suspicious_tlds = ["xyz","top","click","loan","win","gq","tk","ml","cf","io","info","biz","pw","cc"]
    
    # Expanded brand list - financial institutions, tech companies, popular services
    trusted_brands = [
        # Tech companies
        "google","facebook","instagram","amazon","microsoft","apple","paypal",
        "twitter","youtube","linkedin","github","netflix","spotify","dropbox",
        # Banks (Indian) - NOTE: "axis" removed to avoid false positives, use "axisbank"
        "sbi","hdfc","icici","axisbank","kotak","pnb","unionbank","bankofbaroda",
        "canarabank","idbi","indusind","yesbank",
        # Banks (International)
        "chase","wellsfargo","bankofamerica","citibank","hsbc","barclays",
        # Payment services
        "paytm","googlepay","phonepe","stripe","razorpay",
        # E-commerce
        "flipkart","myntra","snapdeal","ebay","alibaba",
        # Government
        "uidai","incometax","gst","epfo",
    ]
    
    # Check if domain contains brand keywords (more sophisticated)
    brand_in_domain = any(b in domain for b in trusted_brands)
    real_brand = any(
        domain == b + "." + t or domain.endswith("." + b + "." + t) or
        domain == "www." + b + "." + t  # Handle www prefix
        for b in trusted_brands for t in ["com","org","net","in","co.in","co.uk","gov.in"]
    )
    
    # Additional phishing indicators for financial/government sites
    financial_keywords = ["bank","verify","account","secure","login","signin","confirm","update","suspended"]
    has_financial_keywords = any(keyword in domain for keyword in financial_keywords)
    
    # Hyphen count (excessive hyphens are suspicious)
    hyphen_count = domain.count("-")
    
    subdomain_count = max(len(domain.split(".")) - 2, 0)
    special_chars = sum(1 for c in url if c in "-_~%@!$#")
    letters = sum(c.isalpha() for c in url)
    digits = sum(c.isdigit() for c in url)
    
    is_phishing = (
        re.match(r"^\d+\.\d+\.\d+\.\d+$", domain) or
        (brand_in_domain and not real_brand) or
        subdomain_count >= 3 or
        tld in suspicious_tlds or  # Includes .info, .biz now
        "@" in url or url.count(".") > 6 or
        hyphen_count >= 2 or  # Multiple hyphens suspicious
        (has_financial_keywords and tld not in ["com","in","co.in","gov","gov.in","org"])  # Financial keywords with suspicious TLD
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
        proba = url_model.predict_proba(df)[0]
        
        # FIXED: Confidence should be the probability of the PREDICTED class
        if prediction == 1:  # Phishing
            confidence = int(proba[1] * 100)
        else:  # Legitimate
            confidence = int(proba[0] * 100)
        
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
        if hyphen_count >= 2:
            indicators.append('Multiple Hyphens in Domain')
        if has_financial_keywords and tld not in ["com","in","co.in","gov","gov.in"]:
            indicators.append('Financial Keywords with Suspicious TLD')
        if any(keyword in domain for keyword in ["verify","account","secure","login","update"]):
            indicators.append('Suspicious Authentication Keywords')
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
    
    # ===== TEMPORARY DEBUG LOGGING =====
    print(f"\n{'='*60}")
    print(f"[EMAIL DEBUG] Text length: {len(text)} characters")
    print(f"[EMAIL DEBUG] Model: text_model (Logistic Regression)")
    print(f"{'='*60}")
    # ===================================
    
    # Detect language and translate if needed
    translated_text, detected_lang, was_translated = detect_and_translate(text)
    
    # Debug logging
    if was_translated:
        print(f"[EMAIL TRANSLATION] Detected language: {detected_lang}")
        print(f"[EMAIL TRANSLATION] Original: {text[:100]}")
        print(f"[EMAIL TRANSLATION] Translated: {translated_text[:100]}")
    
    # CRITICAL FIX: Preprocess text to match training preprocessing
    import string
    text_clean = translated_text.lower()
    text_clean = text_clean.translate(str.maketrans('', '', string.punctuation))
    # Note: Stopword removal is NOT needed here as TF-IDF will handle it
    
    print(f"[EMAIL PREPROCESSED] {text_clean[:100]}")
    
    # Use preprocessed text for prediction
    transformed = text_vectorizer.transform([text_clean])
    prediction = text_model.predict(transformed)[0]
    proba = text_model.predict_proba(transformed)[0]
    
    # ===== TEMPORARY DEBUG LOGGING =====
    print(f"[EMAIL DEBUG] Raw model prediction class: {prediction}")
    print(f"[EMAIL DEBUG] Raw probabilities: [Legit: {proba[0]:.4f}, Spam: {proba[1]:.4f}]")
    # ===================================
    
    print(f"[EMAIL PREDICTION] Class: {prediction}, Probabilities: {proba}")
    
    # FIXED: Confidence should be the probability of the PREDICTED class
    if prediction == 1:  # Spam/Phishing
        confidence = int(proba[1] * 100)  # Probability of spam class
    else:  # Legitimate
        confidence = int(proba[0] * 100)  # Probability of legitimate class
    
    result = "Spam/Phishing" if prediction == 1 else "Legitimate"
    
    # ===== RULE-BASED OVERRIDE FOR NON-ENGLISH PHISHING =====
    # Check for strong phishing patterns in translated text (especially for non-English)
    text_check = translated_text.lower()
    strong_phishing_patterns = [
        # Account suspension/blocking patterns
        ('suspend' in text_check or 'block' in text_check or 'deactivat' in text_check) and 
        ('card' in text_check or 'account' in text_check or 'atm' in text_check),
        
        # Verification urgency patterns
        ('verif' in text_check or 'confirm' in text_check or 'update' in text_check) and
        ('urgent' in text_check or 'immediate' in text_check or '24' in text_check or 'expire' in text_check),
        
        # OTP/security credential sharing
        ('otp' in text_check or 'password' in text_check or 'pin' in text_check or 'cvv' in text_check) and
        ('share' in text_check or 'provide' in text_check or 'send' in text_check or 'enter' in text_check),
        
        # Prize/lottery with payment
        ('won' in text_check or 'prize' in text_check or 'lottery' in text_check or 'reward' in text_check) and
        ('fee' in text_check or 'pay' in text_check or 'deposit' in text_check or 'transfer' in text_check),
        
        # Banking + urgency + link/action
        ('bank' in text_check or 'credit' in text_check or 'debit' in text_check) and
        ('click' in text_check or 'link' in text_check or 'call' in text_check or 'contact' in text_check) and
        ('urgent' in text_check or 'immediate' in text_check or 'now' in text_check),
    ]
    
    if any(strong_phishing_patterns):
        result = "Spam/Phishing"
        # Boost confidence to at least 85% for rule-based detection
        confidence = max(85, confidence)
        print(f"[RULE-BASED OVERRIDE] Strong phishing pattern detected, forced Spam/Phishing classification")
    
    print(f"[FINAL] Result: {result}, Confidence: {confidence}%")
    
    # ===== TEMPORARY DEBUG LOGGING =====
    print(f"[EMAIL DEBUG] Final API response - Result: {result}, Confidence: {confidence}%")
    print(f"{'='*60}\n")
    # ===================================
    
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
    
    # ===== TEMPORARY DEBUG LOGGING =====
    print(f"\n{'='*60}")
    print(f"[SCAM DEBUG] Text length: {len(text)} characters")
    print(f"[SCAM DEBUG] Model: text_model (Logistic Regression - same as email)")
    print(f"{'='*60}")
    # ===================================
    
    # Detect language and translate if needed
    translated_text, detected_lang, was_translated = detect_and_translate(text)
    
    # Debug logging
    if was_translated:
        print(f"[TRANSLATION] Detected language: {detected_lang}")
        print(f"[TRANSLATION] Original: {text[:100]}")
        print(f"[TRANSLATION] Translated: {translated_text[:100]}")
    
    # CRITICAL FIX: Preprocess text to match training preprocessing
    import string
    text_clean = translated_text.lower()
    text_clean = text_clean.translate(str.maketrans('', '', string.punctuation))
    
    print(f"[PREPROCESSED] {text_clean[:100]}")
    
    # Use preprocessed text for prediction
    transformed = text_vectorizer.transform([text_clean])
    prediction = text_model.predict(transformed)[0]
    proba = text_model.predict_proba(transformed)[0]
    
    # ===== TEMPORARY DEBUG LOGGING =====
    print(f"[SCAM DEBUG] Raw model prediction class: {prediction}")
    print(f"[SCAM DEBUG] Raw probabilities: [Legit: {proba[0]:.4f}, Spam: {proba[1]:.4f}]")
    # ===================================
    
    print(f"[PREDICTION] Class: {prediction}, Probabilities: {proba}")
    
    # FIXED: Confidence should be the probability of the PREDICTED class
    if prediction == 1:  # Spam/Phishing
        confidence = int(proba[1] * 100)  # Probability of spam class
    else:  # Legitimate
        confidence = int(proba[0] * 100)  # Probability of legitimate class
    
    result = "Spam/Phishing" if prediction == 1 else "Legitimate"
    
    # ===== RULE-BASED OVERRIDE FOR NON-ENGLISH PHISHING =====
    # Check for strong phishing patterns in translated text (especially for non-English)
    text_check = translated_text.lower()
    strong_phishing_patterns = [
        # Account suspension/blocking patterns
        ('suspend' in text_check or 'block' in text_check or 'deactivat' in text_check) and 
        ('card' in text_check or 'account' in text_check or 'atm' in text_check),
        
        # Verification urgency patterns
        ('verif' in text_check or 'confirm' in text_check or 'update' in text_check) and
        ('urgent' in text_check or 'immediate' in text_check or '24' in text_check or 'expire' in text_check),
        
        # OTP/security credential sharing
        ('otp' in text_check or 'password' in text_check or 'pin' in text_check or 'cvv' in text_check) and
        ('share' in text_check or 'provide' in text_check or 'send' in text_check or 'enter' in text_check),
        
        # Prize/lottery with payment
        ('won' in text_check or 'prize' in text_check or 'lottery' in text_check or 'reward' in text_check) and
        ('fee' in text_check or 'pay' in text_check or 'deposit' in text_check or 'transfer' in text_check),
        
        # Banking + urgency + link/action
        ('bank' in text_check or 'credit' in text_check or 'debit' in text_check) and
        ('click' in text_check or 'link' in text_check or 'call' in text_check or 'contact' in text_check) and
        ('urgent' in text_check or 'immediate' in text_check or 'now' in text_check),
    ]
    
    if any(strong_phishing_patterns):
        result = "Spam/Phishing"
        # Boost confidence to at least 85% for rule-based detection
        confidence = max(85, confidence)
        print(f"[RULE-BASED OVERRIDE] Strong phishing pattern detected, forced Spam/Phishing classification")
    
    print(f"[FINAL] Result: {result}, Confidence: {confidence}%")
    
    # ===== TEMPORARY DEBUG LOGGING =====
    print(f"[SCAM DEBUG] Final API response - Result: {result}, Confidence: {confidence}%")
    print(f"{'='*60}\n")
    # ===================================
    
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

def extract_job_features(text_lower, original_text, vectorizer):
    """Extract enhanced features for job posting classification"""
    # TF-IDF features
    tfidf_features = vectorizer.transform([text_lower])
    
    # Original 5 features
    has_pay_fee = 1 if any(w in text_lower for w in ['fee', 'registration', 'deposit', 'pay', 'payment', 'refundable']) else 0
    has_unrealistic_salary = 1 if any(w in text_lower for w in ['100000', '50000', 'lakh', 'crore']) else 0
    has_suspicious_words = 1 if any(w in text_lower for w in ['whatsapp', 'aadhar', 'urgent', 'guaranteed', 'telegram']) else 0
    has_no_company = 1 if len(text_lower.strip()) < 100 else 0
    has_email_in_post = 1 if any(domain in text_lower for domain in ['@gmail', '@yahoo', '@hotmail']) else 0
    
    # New structural features
    text_length = len(original_text)
    word_count = len(text_lower.split())
    avg_word_length = np.mean([len(w) for w in text_lower.split()]) if text_lower.split() else 0
    has_company_profile = 1 if text_length > 300 else 0
    has_requirements = 1 if any(word in text_lower for word in ['experience', 'skills', 'qualification', 'required']) else 0
    has_benefits = 1 if any(word in text_lower for word in ['benefits', 'insurance', '401k', 'vacation', 'pto']) else 0
    has_salary_range = 1 if any(word in text_lower for word in ['salary', 'lpa', 'usd', 'inr', 'annual', 'per month']) else 0
    
    # Linguistic features
    urgency_words = ['urgent', 'immediately', 'asap', 'hurry', 'quick', 'fast', 'now', 'today', 'limited']
    urgency_count = sum(1 for w in urgency_words if w in text_lower)
    money_words = ['earn', 'income', 'salary', 'paid', 'money', 'cash', 'payment', 'profit']
    money_mention_count = sum(1 for w in money_words if w in text_lower)
    caps_ratio = sum(1 for c in original_text if c.isupper()) / max(len(original_text), 1)
    exclamation_count = original_text.count('!')
    
    # Contact method features
    has_social_contact = 1 if any(platform in text_lower for platform in ['whatsapp', 'telegram', 'wechat', 'viber']) else 0
    personal_domains = ['gmail', 'yahoo', 'hotmail', 'outlook', 'aol', 'mail']
    personal_email_count = sum(1 for domain in personal_domains if f'@{domain}' in text_lower)
    
    # Scam pattern features
    no_experience = 1 if 'no experience' in text_lower or 'no qualification' in text_lower else 0
    work_from_home = 1 if 'work from home' in text_lower or 'remote work' in text_lower else 0
    guaranteed_income = 1 if 'guaranteed' in text_lower and any(w in text_lower for w in ['income', 'salary', 'earn', 'money']) else 0
    
    # Compound features
    fee_and_social = 1 if has_pay_fee and has_social_contact else 0
    fee_and_urgency = 1 if has_pay_fee and urgency_count > 0 else 0
    
    # Create feature array (ORDER MUST MATCH TRAINING!)
    manual_features = np.array([[
        has_pay_fee, has_unrealistic_salary, has_suspicious_words, has_no_company, has_email_in_post,
        text_length, word_count, avg_word_length, has_company_profile, has_requirements,
        has_benefits, has_salary_range, urgency_count, money_mention_count, caps_ratio,
        exclamation_count, has_social_contact, personal_email_count, no_experience, work_from_home,
        guaranteed_income, fee_and_social, fee_and_urgency
    ]])
    
    # Combine features
    manual_sparse = sp.csr_matrix(manual_features)
    combined = sp.hstack([tfidf_features, manual_sparse])
    return combined

@predict_bp.route("/predict-job", methods=["POST"])
def predict_job():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    text = data.get("text", "")
    
    # ===== TEMPORARY DEBUG LOGGING =====
    print(f"\n{'='*60}")
    print(f"[JOB DEBUG] Text length: {len(text)} characters")
    print(f"[JOB DEBUG] Model: job_model (XGBoost)")
    print(f"{'='*60}")
    # ===================================
    
    # Detect language and translate if needed
    translated_text, detected_lang, was_translated = detect_and_translate(text)
    
    # Extract features
    original_text = translated_text
    text_lower = translated_text.lower()
    combined = extract_job_features(text_lower, original_text, job_vectorizer)
    
    # Predict using optimal threshold
    proba = job_model.predict_proba(combined)[0]
    prediction = 1 if proba[1] >= job_threshold else 0
    
    # ===== TEMPORARY DEBUG LOGGING =====
    print(f"[JOB DEBUG] Raw model prediction class: {prediction}")
    print(f"[JOB DEBUG] Raw probabilities: [Legit: {proba[0]:.4f}, Fake: {proba[1]:.4f}]")
    print(f"[JOB DEBUG] Threshold used: {job_threshold:.4f}")
    # ===================================
    
    # Debug logging
    print(f"\n[JOB PREDICTION DEBUG]")
    print(f"Probabilities: [Legit: {proba[0]:.4f}, Fake: {proba[1]:.4f}]")
    print(f"Threshold: {job_threshold:.4f}")
    print(f"Prediction: {prediction} ({'Fake' if prediction == 1 else 'Legitimate'})")
    
    # FIXED: Confidence should be the probability of the predicted class
    if prediction == 1:  # Fake
        confidence = int(proba[1] * 100)  # Probability of being fake
    else:  # Legitimate
        confidence = int(proba[0] * 100)  # Probability of being legitimate
    
    result = "Fake" if prediction == 1 else "Legitimate"
    
    print(f"Result: {result}, Confidence: {confidence}%")
    
    # Extract basic features for rule-based checks
    has_pay_fee = 1 if any(w in text_lower for w in ['fee', 'registration', 'deposit', 'pay ', 'payment', 'refundable']) else 0
    has_social_contact = 1 if any(platform in text_lower for platform in ['whatsapp', 'telegram', 'wechat', 'viber']) else 0
    
    # Rule-based override: Strong fake indicators should force fake classification
    strong_fake_indicators = [
        ("registration fee" in text_lower or "verification fee" in text_lower or "document fee" in text_lower),
        ("refundable fee" in text_lower or "security deposit" in text_lower or "processing fee" in text_lower),
        (has_pay_fee == 1 and has_social_contact == 1),  # FIXED: Fee + suspicious contact method
        ("whatsapp" in text_lower and "fee" in text_lower),  # WhatsApp + fee is always suspicious
        # Unrealistic intern stipend + urgency + no experience
        (any(amt in original_text for amt in ["₹35", "₹40", "₹45", "₹50", "35000", "40000", "45000", "50000", "35,000", "40,000", "45,000", "50,000"]) and
         ("intern" in text_lower or "internship" in text_lower) and
         ("no experience" in text_lower or "no prior experience" in text_lower) and
         ("24 hours" in text_lower or "limited positions" in text_lower or "urgent" in text_lower)),
    ]
    
    if any(strong_fake_indicators):
        result = "Fake"
        confidence = max(confidence, 85)  # Boost confidence to at least 85%
        print(f"[RULE-BASED OVERRIDE] Forced Fake classification, confidence boosted to {confidence}%")
    
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
                print(f"[URL-BASED OVERRIDE] Suspicious URL detected, forced Fake classification")
                break
    
    print(f"[FINAL RESULT] {result}, Confidence: {confidence}%")
    print(f"[END DEBUG]\n")
    
    # ===== TEMPORARY DEBUG LOGGING =====
    print(f"[JOB DEBUG] Final API response - Result: {result}, Confidence: {confidence}%")
    print(f"{'='*60}\n")
    # ===================================
    
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

@predict_bp.route("/history", methods=["DELETE"])
def clear_history():
    token = request.headers.get("Authorization","...").replace("Bearer ","")
    try:
        data = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        email = data["email"]
    except:
        return jsonify({"error": "Unauthorized"}), 401

    # Delete all scans for this user
    result = scans.delete_many({"email": email})
    
    return jsonify({
        "message": "History cleared successfully",
        "deleted_count": result.deleted_count
    }), 200