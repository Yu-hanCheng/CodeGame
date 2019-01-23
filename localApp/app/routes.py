from app import app
from flask import render_template,request,redirect, url_for,flash,session
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace

socketIO = SocketIO('localhost', 5000, LoggingNamespace)
app.secret_key = "secretkey"
@app.route('/')
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Home')
    else:
        global canlogin
        uname = request.form.get('uname',False)
        password = request.form.get('psw',False)
        try:
            def checked_user(*args):
                global canlogin
                canlogin=args[0]

            socketIO.on('checked_user',checked_user)
            socketIO.emit('check_user',{'uname':uname,'password':password})
            socketIO.wait(1)
        except Exception as e:
            print('e',e)
    
        if canlogin['checked']:
            session['user_id']=canlogin['user_id']
            return redirect(url_for('index'))
        else:
            flash('Your '+canlogin['msg']+' is not found')
            return render_template('login.html')

@app.route('/index')
def index():
    global g_list
    try:
        def on_g_list(*args):
            global g_list            
            g_list=args
        socketIO.on('g_list', on_g_list)
        socketIO.emit('get_gamelist')
        socketIO.wait(1)
    except Exception as e:
        print('e',e)
    return render_template('index.html', title='Home',glist=g_list)
