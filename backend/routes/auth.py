from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os, bcrypt, jwt, datetime

load_dotenv()

auth_bp = Blueprint("auth", __name__)
client = MongoClient(os.getenv("MONGO_URI"))
db = client["threatlens"]
users = db["users"]
SECRET = os.getenv("JWT_SECRET")

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name","").strip()
    email = data.get("email","").strip().lower()
    password = data.get("password","").strip()

    if not name or not email or not password:
        return jsonify({"error": "All fields required"}), 400
    if users.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users.insert_one({"name": name, "email": email, "password": hashed})

    token = jwt.encode({
        "email": email,
        "name": name,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, SECRET, algorithm="HS256")

    return jsonify({"token": token, "name": name, "email": email}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email","").strip().lower()
    password = data.get("password","").strip()

    user = users.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    if not bcrypt.checkpw(password.encode(), user["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = jwt.encode({
        "email": email,
        "name": user["name"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, SECRET, algorithm="HS256")

    return jsonify({"token": token, "name": user["name"], "email": email}), 200

@auth_bp.route("/verify", methods=["GET"])
def verify():
    token = request.headers.get("Authorization","").replace("Bearer ","")
    if not token:
        return jsonify({"error": "No token"}), 401
    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        return jsonify({"name": data["name"], "email": data["email"]}), 200
    except:
        return jsonify({"error": "Invalid token"}), 401