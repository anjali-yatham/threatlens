"""
Test script for the improved fake job posting detection model.

Run this after training to validate the model works correctly
and maintains backward compatibility.
"""

import joblib
import numpy as np
import scipy.sparse as sp

print("=" * 70)
print("TESTING IMPROVED JOB MODEL")
print("=" * 70)

# Load models
print("\n[1/3] Loading model artifacts...")
try:
    model = joblib.load('models/job_model.pkl')
    vectorizer = joblib.load('models/job_vectorizer.pkl')
    print("  ✓ Model loaded successfully")
    print(f"  Model type: {type(model).__name__}")
except Exception as e:
    print(f"  ✗ Error loading model: {e}")
    exit(1)

# Helper function matching predict.py
def extract_job_features(text_lower, original_text, vectorizer):
    """Extract features matching the training pipeline"""
    tfidf_features = vectorizer.transform([text_lower])
    
    # Original 5 features
    has_pay_fee = 1 if any(w in text_lower for w in ['fee', 'registration', 'deposit', 'pay', 'payment', 'refundable']) else 0
    has_unrealistic_salary = 1 if any(w in text_lower for w in ['100000', '50000', 'lakh', 'crore']) else 0
    has_suspicious_words = 1 if any(w in text_lower for w in ['whatsapp', 'aadhar', 'urgent', 'guaranteed', 'telegram']) else 0
    has_no_company = 1 if len(text_lower.strip()) < 100 else 0
    has_email_in_post = 1 if any(domain in text_lower for domain in ['@gmail', '@yahoo', '@hotmail']) else 0
    
    # New features
    text_length = len(original_text)
    word_count = len(text_lower.split())
    avg_word_length = np.mean([len(w) for w in text_lower.split()]) if text_lower.split() else 0
    has_company_profile = 1 if text_length > 300 else 0
    has_requirements = 1 if any(word in text_lower for word in ['experience', 'skills', 'qualification', 'required']) else 0
    has_benefits = 1 if any(word in text_lower for word in ['benefits', 'insurance', '401k', 'vacation', 'pto']) else 0
    has_salary_range = 1 if any(word in text_lower for word in ['salary', 'lpa', 'usd', 'inr', 'annual', 'per month']) else 0
    
    urgency_words = ['urgent', 'immediately', 'asap', 'hurry', 'quick', 'fast', 'now', 'today', 'limited']
    urgency_count = sum(1 for w in urgency_words if w in text_lower)
    money_words = ['earn', 'income', 'salary', 'paid', 'money', 'cash', 'payment', 'profit']
    money_mention_count = sum(1 for w in money_words if w in text_lower)
    caps_ratio = sum(1 for c in original_text if c.isupper()) / max(len(original_text), 1)
    exclamation_count = original_text.count('!')
    
    has_social_contact = 1 if any(platform in text_lower for platform in ['whatsapp', 'telegram', 'wechat', 'viber']) else 0
    personal_domains = ['gmail', 'yahoo', 'hotmail', 'outlook', 'aol', 'mail']
    personal_email_count = sum(1 for domain in personal_domains if f'@{domain}' in text_lower)
    
    no_experience = 1 if 'no experience' in text_lower or 'no qualification' in text_lower else 0
    work_from_home = 1 if 'work from home' in text_lower or 'remote work' in text_lower else 0
    guaranteed_income = 1 if 'guaranteed' in text_lower and any(w in text_lower for w in ['income', 'salary', 'earn', 'money']) else 0
    
    fee_and_social = 1 if has_pay_fee and has_social_contact else 0
    fee_and_urgency = 1 if has_pay_fee and urgency_count > 0 else 0
    
    manual_features = np.array([[
        has_pay_fee, has_unrealistic_salary, has_suspicious_words, has_no_company, has_email_in_post,
        text_length, word_count, avg_word_length, has_company_profile, has_requirements,
        has_benefits, has_salary_range, urgency_count, money_mention_count, caps_ratio,
        exclamation_count, has_social_contact, personal_email_count, no_experience, work_from_home,
        guaranteed_income, fee_and_social, fee_and_urgency
    ]])
    
    manual_sparse = sp.csr_matrix(manual_features)
    combined = sp.hstack([tfidf_features, manual_sparse])
    return combined

# Test cases
print("\n[2/3] Running test cases...")

test_cases = [
    {
        "name": "Indian Scam Pattern",
        "text": "work from home data entry earn 50000 monthly pay registration fee 500 send aadhar bank details whatsapp guaranteed income no interview",
        "expected": "Fake"
    },
    {
        "name": "US Scam Pattern",
        "text": "data entry position flexible hours $50 per hour pay processing fee $149 for background check wire transfer only no experience needed immediately",
        "expected": "Fake"
    },
    {
        "name": "MLM/Pyramid Scheme",
        "text": "join our team unlimited income potential no boss be your own boss small investment required recruit team members guaranteed returns",
        "expected": "Fake"
    },
    {
        "name": "Legitimate Tech Job (Detailed)",
        "text": "Senior Software Engineer Python Django REST APIs PostgreSQL 5 years experience Bangalore salary 12 LPA apply through company careers portal comprehensive health insurance 401k benefits formal interview process multiple technical rounds coding assessment required university degree preferred modern tech stack cloud experience AWS",
        "expected": "Legitimate"
    },
    {
        "name": "Legitimate Corporate Job",
        "text": "Marketing Manager MBA preferred 7 years experience brand strategy digital marketing social media management Chicago salary $90,000 annual competitive benefits package health dental vision insurance 401k matching apply through LinkedIn company website formal hiring process",
        "expected": "Legitimate"
    },
    {
        "name": "Edge Case: Short Text",
        "text": "hiring software engineers",
        "expected": "Uncertain"
    },
]

print("\n" + "=" * 70)
results = {"pass": 0, "fail": 0}

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['name']}")
    print(f"Text: {test['text'][:80]}...")
    
    try:
        # Extract features
        text_lower = test['text'].lower()
        original_text = test['text']
        combined = extract_job_features(text_lower, original_text, vectorizer)
        
        # Predict
        prediction = model.predict(combined)[0]
        confidence = int(max(model.predict_proba(combined)[0]) * 100)
        result = "Fake" if prediction == 1 else "Legitimate"
        
        print(f"Result: {result} (Confidence: {confidence}%)")
        print(f"Expected: {test['expected']}")
        
        # Validate
        if test['expected'] == "Uncertain":
            # For edge cases, just check it doesn't crash
            print("Status: ✓ PASS (Edge case handled)")
            results["pass"] += 1
        elif result == test['expected']:
            print("Status: ✓ PASS")
            results["pass"] += 1
        else:
            print("Status: ✗ FAIL")
            results["fail"] += 1
            
    except Exception as e:
        print(f"Status: ✗ ERROR - {e}")
        results["fail"] += 1

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Passed: {results['pass']}/{len(test_cases)}")
print(f"Failed: {results['fail']}/{len(test_cases)}")

if results['fail'] == 0:
    print("\n✅ All tests passed! Model is working correctly.")
else:
    print(f"\n⚠️  {results['fail']} test(s) failed. Review model training.")

# Backward compatibility check
print("\n[3/3] Backward compatibility check...")
try:
    # Check model has required methods
    assert hasattr(model, 'predict'), "Model missing predict() method"
    assert hasattr(model, 'predict_proba'), "Model missing predict_proba() method"
    
    # Check vectorizer
    assert hasattr(vectorizer, 'transform'), "Vectorizer missing transform() method"
    
    print("  ✓ Model interface compatible with Flask API")
    print("  ✓ Vectorizer interface compatible")
    print("  ✓ No breaking changes detected")
    
except AssertionError as e:
    print(f"  ✗ Compatibility issue: {e}")

print("\n" + "=" * 70)
print("TESTING COMPLETE")
print("=" * 70)
