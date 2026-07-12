import os
import time
from flask import Blueprint, jsonify, render_template, request, send_file
from lib.constants import TEMP_PATH, URL
from lib.storage import generate_token, save_text_payload, save_uploaded_file

cache = []

main_routes = Blueprint('main', __name__)

def register_in_cache(file_path):
    file_entry = {str(file_path): time.time()}
    cache.append(file_entry)

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
        file_path = save_uploaded_file(request.files['uploadedFile'], token)

    if not file_path:
        msg = request.form.get('text')
        if not msg and request.is_json:
            json_data = request.get_json()
            msg = json_data.get('text') if json_data else None
        
        file_path = save_text_payload(msg, token)

    if file_path:
        register_in_cache(file_path)
        return jsonify(code=200, status="success", id=token), 200

    return jsonify(code=400, status="error", msg="Invalid."), 400

@main_routes.route('/receive/<code_id>', methods=['GET'])
def receive_payload(code_id):
    if len(code_id) <= 6:
        return jsonify(code=400, status="error", message="Invalid code format"), 400

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
        os.remove(target_path)
    except OSError:
        pass

    return response

@main_routes.route("/cancel/<code_id>", methods=['DELETE', 'POST', 'GET'])
def cancel(code_id):
    if len(code_id) <= 6:
        return jsonify(code=400, status="error", message="Invalid code format"), 400

    if not os.path.exists(TEMP_PATH):
        return jsonify(code=404, status="error", message="File not found"), 404

    for f in os.listdir(TEMP_PATH):
        if f.startswith(code_id):
            target_path = os.path.join(TEMP_PATH, f)
            try:
                os.remove(target_path)
                return jsonify(code=200, status="success", message="Payload removed"), 200
            except OSError:
                return jsonify(code=500, status="error", message="Could not remove file"), 500

    return jsonify(code=404, status="error", message="File not found or already removed"), 404
