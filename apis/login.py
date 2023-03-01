from flask import Blueprint, session, request, current_app, json
import base64
import re

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        current_app.logger.error(f'No auth header')
        return json.jsonify({'message': 'no auth header'}), 401
    
    encoded_credentials = auth_header.split(' ')[1] # 'Basic <encoded_credentials in base64>'
    decoded = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded.split(':')
    
    if re.match('^[a-zA-Z0-9_]+$',username) and len(username) <= 20 and password == 'test':
        session['username'] = username
        return json.jsonify({'message': 'login successful'}), 200

    return json.jsonify({'message': 'login failed'}), 401