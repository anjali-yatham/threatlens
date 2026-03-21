from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"])

client = MongoClient(os.getenv("MONGO_URI"))
db = client["threatlens"]

from routes.auth import auth_bp
from routes.predict import predict_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(predict_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(port=5000, debug=True)