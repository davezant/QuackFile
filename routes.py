import os
import time
import io
from flask import Blueprint, jsonify, render_template, request, send_file
from lib.constants import TEMP_PATH, URL
from lib.ecrypt import generate_key, encrypt_data, decrypt_data
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
    key = generate_key()
    
    if 'uploadedFile' in request.files:
        file = request.files['uploadedFile']
        file_content = file.read()
        encrypted_content = encrypt_data(file_content, key)
        
        file.stream = io.BytesIO(encrypted_content)
        file.stream.seek(0)
        
        file_path = save_uploaded_file(file, token)

    if not file_path:
        msg = request.form.get('text')
        if not msg and request.is_json:
            json_data = request.get_json()
            msg = json_data.get('text') if json_data else None
        
        if msg:
            encrypted_content = encrypt_data(msg.encode('utf-8'), key)
            file_path = save_text_payload(encrypted_content.decode('utf-8'), token)

    if file_path:
        file_entry = {
            'path': str(file_path),
            'token': token,
            'time': time.time(),
            'key': key.decode('utf-8')
        }
        cache.append(file_entry)
        return jsonify(code=200, status="success", id=token), 200

    return jsonify(code=400, status="error", msg="Invalid."), 400


@main_routes.route('/receive/<code_id>', methods=['GET'])
def receive_payload(code_id):
    if len(code_id) <= 6:
        return jsonify(code=400, status="error", message="Invalid code format"), 400

    target_path = None
    encryption_key = None
    
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

    # Busca a chave correspondente no cache em memória
    cache_index_to_remove = -1
    for index, entry in enumerate(cache):
        if entry.get('token') == code_id:
            encryption_key = entry.get('key')
            cache_index_to_remove = index
            break

    if not encryption_key:
        try:
            os.remove(target_path)
        except OSError:
            pass
        return jsonify(code=500, status="error", message="Encryption key lost. File corrupted."), 500

    try:
        with open(target_path, 'rb') as f:
            file_data = f.read()
        
        try:
            raw_cipher = file_data.decode('utf-8').encode('utf-8')
        except UnicodeDecodeError:
            raw_cipher = file_data

        decrypted_data = decrypt_data(raw_cipher, encryption_key.encode('utf-8'))
        
        try:
            os.remove(target_path)
        except OSError:
            pass
        
        if cache_index_to_remove != -1:
            cache.pop(cache_index_to_remove)
            
    except Exception:
        return jsonify(code=500, status="error", message="Decryption failed"), 500

    as_attachment = not target_path.endswith('.txt')
    return send_file(
        io.BytesIO(decrypted_data),
        mimetype='application/octet-stream',
        as_attachment=as_attachment,
        download_name=os.path.basename(target_path)
    )

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
