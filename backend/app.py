from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Configure CORS for both local development and production
# Add your Vercel frontend URL to this list when deployed
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174", 
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    # Add your production frontend URL here when ready, e.g.:
    # "https://your-frontend.vercel.app"
]

CORS(app, origins=allowed_origins, supports_credentials=True)

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