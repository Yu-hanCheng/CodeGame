from flask import Flask
from flask_socketio import SocketIO


socketio = SocketIO()

app = Flask(__name__)

from app import routes

socketio.init_app(app)
socketio.run(app)