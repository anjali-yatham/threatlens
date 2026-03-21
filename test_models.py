import joblib

model = joblib.load('models/text_model.pkl')
vec = joblib.load('models/text_vectorizer.pkl')

tests = [
    'URGENT you have won 50000 cash prize send bank account OTP immediately',
    'Hey are you coming to college tomorrow assignment deadline',
    'Your account suspended verify credit card paypal security',
    'Dear Customer your account has been suspended click here to verify paypal',
    'Work from home earn 100000 per month pay registration fee send aadhar card',
    'Hi John meeting confirmed for tomorrow at 3pm bring the project report',
]

print("TEXT MODEL RESULTS")
print("=" * 60)
for t in tests:
    x = vec.transform([t])
    pred = model.predict(x)[0]
    prob = model.predict_proba(x)[0]
    label = "SPAM" if pred == 1 else "HAM"
    print(f"Text   : {t[:55]}...")
    print(f"Result : {label} | Ham={prob[0]:.2f} Spam={prob[1]:.2f}")
    print()

print("=" * 60)

job_model = joblib.load('models/job_model.pkl')
job_vec = joblib.load('models/job_vectorizer.pkl')

jobs = [
    'Work from home data entry no experience pay 500 registration fee whatsapp us send aadhar bank details guaranteed income',
    'Software Engineer Python Django REST APIs PostgreSQL 2 years experience Hyderabad apply infosys careers portal salary 6LPA',
]

print("JOB MODEL RESULTS")
print("=" * 60)
for t in jobs:
    x = job_vec.transform([t])
    pred = job_model.predict(x)[0]
    prob = job_model.predict_proba(x)[0]
    label = "FAKE" if pred == 1 else "REAL"
    print(f"Text   : {t[:55]}...")
    print(f"Result : {label} | Real={prob[0]:.2f} Fake={prob[1]:.2f}")
    print()