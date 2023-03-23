from flask import Blueprint, session, request, json, current_app
from .gpt.chains import Chains
import base64
import logging

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    # Start of login check
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        current_app.logger.error('No auth header')
        return json.jsonify({'message': 'no auth header'}), 401

    encoded_credentials = auth_header.split(' ')[1]  # 'Basic <encoded_credentials in base64>'
    decoded = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded.split(':')

    if username != 'test' or password != 'test':
        session['username'] = username
        current_app.logger.info(f"Session: {session}")
        return json.jsonify({'message': 'login failed'}), 401

    # End of login check

    data = request.get_json()
    message = data.get('message')
    chatUUID = data.get('conversationIdentifier')
    product = data.get('product')
    retrieval_method = data.get('retrievalMethod')

    # Retrieve chain and previous context
    chain, prev_context = Chains.get_chain_prevcontext(chatUUID)

    # Get product context
    product_context, ix = Chains.get_idsg_context(retrieval_method, message, prev_context)
    Chains.chatid_to_chain_prevcontext[chatUUID] = (chain, product_context)

    logging.info(f"Using Product Context:\n{product_context}")
    other_products = Chains.get_product_list_text(message)
    
    other_products_printable = other_products.replace(', ', ',\n')
    logging.info(f"Using Other Products:\n{other_products}")

    response = chain.predict(human_input=message, product_context=product_context, other_available_products=other_products)
    logging.info(f"Chat Details:\n"
             f"ChatUUID: {chatUUID}\n"
             f"Message: {message}\n"
             f"Response: {response}\n"
             f"Retrieval Method: {retrieval_method}")

    return json.jsonify({'message': response}), 200