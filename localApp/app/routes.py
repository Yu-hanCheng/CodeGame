from app import app
from flask import render_template
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace

socketIO = SocketIO('localhost', 5000, LoggingNamespace)

@app.route('/')
@app.route('/index')
def index():
    global g_list
    try:
        def on_g_list(*args):
            global g_list            
            g_list=args
        socketIO.on('g_list', on_g_list)
        socketIO.emit('get_gamelist',{'t1':'t1'})
        socketIO.wait(1)
    except Exception as e:
        print('e',e)
    return render_template('index.html', title='Home',glist=g_list)
