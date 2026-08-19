from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Configure CORS for both local development and production
# IMPORTANT: Wildcard origins don't work with credentials=True
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174", 
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    # Production Vercel frontend URL
    "https://threatlens-g3sgal404-divyanjalis-projects.vercel.app",
]

CORS(
    app,
    resources={r"/api/*": {"origins": allowed_origins}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "DELETE", "OPTIONS"],
    expose_headers=["Content-Type", "Authorization"]
)

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["threatlens"]

# Register blueprints
from routes.auth import auth_bp
from routes.predict import predict_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(predict_bp, url_prefix="/api")

# Health check endpoint for Render
@app.route("/")
def health_check():
    return {"status": "healthy", "service": "ThreatLens API"}, 200

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    # Local development server
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)