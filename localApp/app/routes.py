from app import app
from flask import render_template
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace
@app.route('/')
@app.route('/index')
def index():
    try:
        socketIO=SocketIO('0.0.0.0', 5000, LoggingNamespace)
        socketIO.emit('get_gamelist',{'t1':'t1'})
        print("emit msg")
    except Exception as e:
        print('e',e)
    return render_template('index.html', title='Home')