# routes.py
import os
import secrets
import string
import time
from flask import Blueprint, jsonify, render_template, request, send_file
from lib.constants import TEMP_PATH, URL
from werkzeug.utils import secure_filename

cache = []

main_routes = Blueprint('main', __name__)

def generate_token():
    characters = string.ascii_uppercase + string.digits
    first_half = ''.join(secrets.choice(characters) for _ in range(3))
    second_half = ''.join(secrets.choice(characters) for _ in range(3))
    return f"{first_half}-{second_half}"

@main_routes.route('/')
def home():
    return render_template('index.html')

@main_routes.route('/r/<code>')
def send_response(code):
    return render_template('overview_code.html', code=code, current_url=URL, text="Don't put your credentials here, pls!")

@main_routes.route('/send-payload', methods=['POST'])
def send():
    token = generate_token()
    file_path = None
    
    if 'uploadedFile' in request.files:
        file = request.files['uploadedFile']
        if file and file.filename:
            ext = os.path.splitext(secure_filename(file.filename))[1]
            filename = f"{token}{ext}"
            file_path = os.path.join(TEMP_PATH, filename)
            file.save(file_path)

    if not file_path:
        msg = request.form.get('text')
        if not msg and request.is_json:
            json_data = request.get_json()
            msg = json_data.get('text') if json_data else None

        if msg:
            filename = f"{token}.txt"
            file_path = os.path.join(TEMP_PATH, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(msg)

    if file_path:
        file = {str(file_path): time.time()}
        cache.append(file)
        return jsonify(code=200, status="success", id=token), 200

    return jsonify(code=400, status="error", msg="Invalid."), 400

@main_routes.route('/receive/<code_id>', methods=['GET'])
def receive_payload(code_id):
    target_path = None
    
    if os.path.exists(TEMP_PATH):
        for f in os.listdir(TEMP_PATH):
            if f.startswith(code_id):
                target_path = os.path.join(TEMP_PATH, f)
                break

    if not target_path or not os.path.exists(target_path):
        return jsonify(code=404, status="error", message="Code expired or not found"), 404

    file_creation_time = os.path.getmtime(target_path)
    if time.time() - file_creation_time > 180:
        try:
            os.remove(target_path)
        except OSError:
            pass
        return jsonify(code=404, status="error", message="Code expired or not found"), 404

    as_attachment = not target_path.endswith('.txt')
    response = send_file(target_path, as_attachment=as_attachment)
    
    try:
        if os.path.exists(target_path):
           os.remove(target_path)
    except OSError:
        pass

    return response

@main_routes.route("/cancel/<code_id>")
def cancel():
    return ""
