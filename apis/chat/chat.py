from flask import Blueprint, session, request, json, current_app
from .gpt.chains import Chains
import base64

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    # Start of login check
    # TODO: this is here because chrome won't set cookies for localhost. Otherwise we can just check the session.
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        current_app.logger.error(f'No auth header')
        return json.jsonify({'message': 'no auth header'}), 401
    
    encoded_credentials = auth_header.split(' ')[1] # 'Basic <encoded_credentials in base64>'
    decoded = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded.split(':')
    
    if password != 'test':
        session['username'] = username
        current_app.logger.info(f"Session: {session}")
        return json.jsonify({'message': 'login failed'}), 401

    # if not session.get('username'):
    #     return json.jsonify({'message': 'login failed'}), 401
    # End of login check
    
    data = request.get_json()
    message = data.get('message')
    chatUUID = data.get('conversationIdentifier')
    product = data.get('product')
    
    chain = Chains.get_chain(chatUUID) # each chain w/ its own memory for each chat. Not persistent.
    response = chain.predict(human_input=message)
    return json.jsonify({'message': response}), 200