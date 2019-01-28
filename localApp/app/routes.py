from app import app
from flask import render_template,request,redirect, url_for,flash,session
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace
import base64
import os
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

@app.route('/library',methods=['GET','POST'])
def library():
    
    print("type_path",request.form.get('end',False))
    savepath = request.form.get('path',False)
    file_end = request.form.get('end',False) 
    save_code(savepath,"gamemain",file_end,request.form.get('gamemain',False))
    save_code(savepath,"lib",file_end,request.form.get('lib',False))
    return render_template('login.html')


@app.route('/commit',methods=['GET','POST'])
def commit():
    # save
    # {"encodedData":encodedData,"game_id":game_id,"lan_compiler":lan_compiler,"endname":endname,'user_id':1}
    # socket.emit('commit', {code: editor_content, commit_msg:commit_msg, game_id:game_id, glanguage:glanguage, user_id:1});
    print("sandbox recv:",request.content_type)
    
    data = request.get_json()
    print("get_json:",data)
    decoded = base64.b64decode(data.get('encodedData').split(",")[1])
    # str(data.get('lan_compiler'))
    try:
        os.makedirs( path )
    except Exception as e:
        print('e',e)
    with open("%s%s"%(path,filename), "wb") as f:
        f.write(decoded)
        f.write(b"\nglobal paddle_vel,ball_pos,move_unit\npaddle_vel=0\nball_pos=[[0,0],[0,0],[0,0]]\nmove_unit=3\nrun()\n")#要給假值
    
    from subprocess import Popen, PIPE

    try:
        p = Popen(compiler + ' ' + path_ + ' '+ filename + '',shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stderr:
            print('stderr:', stderr)
            return [0,stderr]
        else:
            print('stdout:', stdout)
            return [1,stdout]
    except Exception as e:
        print('e: ',e)
        return e
    return "received code"

def set_language(language):
    compiler = {
        "0": ["gcc",".c"],
        "1": ["python3",".py"],
        "2": ["sh",".sh"]
    }
    language_obj = compiler.get(language, "Invalid language ID")
    return language_obj

def save_code(save_path,filename,file_end,code):
    try:
        os.makedirs( save_path )
    except Exception as e:
        print('e',e)
    with open("%s%s%s"%(save_path,filename,file_end), "w+") as f:
        f.write(code)
        
    

    
