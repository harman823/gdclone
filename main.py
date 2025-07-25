from datetime import datetime
from flask import Flask, request, jsonify
import supabase
from services.auth_handler import register_user, login_user, verify_otp_and_create_token
from flask import request, jsonify, send_file
from services.file_utils import BUCKET_NAME, upload_file, list_userfiles, download_file
import io

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    result = register_user(email, password)
    return jsonify(result)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    result = login_user(email, password)
    return jsonify(result)

@app.route("/otp_verification", methods=["POST"])
def otp_verification():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({"error": "Email and OTP required"}), 400

    result = verify_otp_and_create_token(email, otp)
    return jsonify(result)

@app.route('/upload', methods=['POST'])
def upload_endpoint():
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Get user_id and file from form data
        user_id = request.form.get('user_id')
        file = request.files.get('file')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        if not file:
            return jsonify({"error": "file is required"}), 400
            
        # Call your upload function
        result = upload_file(file, token, user_id)
        
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/files', methods=['GET'])
def list_files_endpoint():
    """List all files for a user"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Get user_id from query params
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400
            
        # Call list function
        result = list_userfiles(token, user_id)
        
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"List files failed: {str(e)}"}), 500

@app.route('/download', methods=['GET'])
def download_endpoint():
    """Download a specific file"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Get parameters
        user_id = request.args.get('user_id')
        filename = request.args.get('filename')
        
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400
        if not filename:
            return jsonify({"error": "filename parameter is required"}), 400
            
        # Call download function
        result = download_file(token, user_id, filename)
        
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 400
            
        # If result is bytes (file content), send it
        if isinstance(result, bytes):
            return send_file(
                io.BytesIO(result),
                as_attachment=True,
                download_name=filename
            )
        
        # If result has content attribute (requests.Response)
        if hasattr(result, 'content'):
            return send_file(
                io.BytesIO(result.content),
                as_attachment=True,
                download_name=filename
            )
            
        return jsonify({"error": "Invalid file response"}), 500
        
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

