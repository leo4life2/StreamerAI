import os
from flask import Flask
from flask_cors import CORS
from apis.chat.chat import chat_bp
from apis.login import login_bp
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(chat_bp)
app.register_blueprint(login_bp)
app.secret_key = os.urandom(24)

@app.route('/ping')
def pingpong():
    return 'pong'

if __name__ == '__main__':
    app.run(debug=True)