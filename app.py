import os
from flask import Flask
from flask_cors import CORS
from apis.chat.chat import chat_bp
from apis.login import login_bp

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(chat_bp)
app.register_blueprint(login_bp)

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)