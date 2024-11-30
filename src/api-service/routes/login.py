from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from google.cloud import storage
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
bcrypt = Bcrypt(app)
app.config["JWT_SECRET_KEY"] = "your-strong-secret-key"  # Replace with a strong secret key
jwt = JWTManager(app)

# Initialize GCP storage client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/secrets/data-service-account.json"
bucket_name = "innit_articles_bucket"
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# Endpoint to register a user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    # Check if user already exists in the bucket
    blob = bucket.blob(f"users/{username}.json")
    if blob.exists():
        return jsonify({"message": "User already exists"}), 400

    # Hash the password and save user data to GCP
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user_data = {"username": username, "password": hashed_password}

    blob.upload_from_string(json.dumps(user_data), content_type="application/json")
    return jsonify({"message": "User registered successfully"}), 201

# Endpoint to log in a user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    # Retrieve user data from the bucket
    blob = bucket.blob(f"users/{username}.json")
    if not blob.exists():
        return jsonify({"message": "Invalid username or password"}), 401

    user_data = json.loads(blob.download_as_text())
    if not bcrypt.check_password_hash(user_data['password'], password):
        return jsonify({"message": "Invalid username or password"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
