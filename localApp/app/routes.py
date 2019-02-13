from app import app, socketio
from flask import render_template,request,redirect, url_for,flash,session
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace
import base64,json
import os,time
from os import walk
from functools import wraps
from flask_socketio import emit
socketIO = SocketIO('localhost', 5000, LoggingNamespace)
app.secret_key = "secretkey"


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        try:
            if session['user_id']:
                print("session:",session['user_id'])
                return func(*args, **kargs)
        except Exception as e:
            print("please login first")
            return redirect(url_for('login'))
    return wrapper


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
            data_to_send = {'uname':uname,'password':password}
            send_to_web("check_user",data_to_send,"checked_user",checked_user)
        except Exception as e:
            print('e',e)
    
        if canlogin['checked']:
            session['user_id']=canlogin['user_id']
            return redirect(url_for('index'))
        else:
            flash('Your '+canlogin['msg']+' is not found')
            return render_template('login.html')



@app.route('/index')
@login_required
def index():
    global g_list
    try:
        def on_g_list(*args):
            global g_list            
            g_list=args
        data_to_send=""
        send_to_web("get_gamelist",data_to_send,"g_list",on_g_list)
    except Exception as e:
        print('e',e)
    return render_template('index.html', title='Home',glist=g_list,user_id=session['user_id'])

@app.route('/library',methods=['GET','POST'])
@login_required
def library():
    
    savepath = request.form.get('path',False)
    file_end = request.form.get('end',False) 
    save_code(savepath,"test_game",file_end,request.form.get('test_game',False))
    save_code(savepath,"lib",file_end,request.form.get('lib',False))
    return "set library ok"


@app.route('/commit',methods=['GET','POST'])
def commit():
    # save
    # {"encodedData":encodedData,"commit_msg":commit_msg,"lan_compiler":lan_compiler,'obj':obj,'user_id':1,}
    # // 0Game_lib.id,1Category.id,2Category.name,3Game.id,4Game.gamename,5Language.id, 6Language.language_name, 7Language.filename_extension
    # socket.emit('commit', {code: editor_content, commit_msg:commit_msg, game_id:game_id, glanguage:glanguage, user_id:1});
    
    data = request.data
    json_obj=json.loads(data)
    obj=json_obj["obj"].split(",")
    code = json_obj['encodedData']
    save_path = obj[1]+"/"+obj[3]+"/"+obj[5]+"/"
    file_end = obj[7]
    # str(data.get('lan_compiler'))
    
    # set filename
    f = []
    for (dirpath, dirnames, filenames) in walk(save_path):
        f.extend(filenames)
        break
    filename=str(len(f)-2)#['.DS_Store', 'gamemain.py', 'lib.py']
    save_code(save_path,filename,file_end,code)
    compiler = json_obj['lan_compiler']
    
    dirpath=save_path+filename+file_end
    code_res = test_code(compiler,save_path,filename,file_end)
    if code_res[0]:
        def send_code_ok(msg):
                print("in callback send_code_ok")
                # flash to web
                flash("send_code_ok")
        data_to_send={'code':code,'user_id':int(json_obj['user_id']),'commit_msg':json_obj['commit_msg'],'game_id':obj[3],'file_end':obj[7]}
        send_to_web("commit_code",data_to_send,"commit_res",send_code_ok)
    return "received code"

@socketio.on('conn')
def connect(message):

    print("conn msg:",message['msg'])
    socketio.emit('gameobject', {'msg': "gameobj"})

@socketio.on('gameobj')
def gameobj(message):
    print("recv socketio msg:",message['msg'])
    socketio.emit('gameobject', {'msg': "gameobj"})

def append_lib(save_path,filename,file_end):
    with open("%s%s%s"%(save_path,filename,file_end), "a") as f:
        f.write("\nglobal paddle_vel,ball_pos,move_unit\npaddle_vel=0\nball_pos=[[0,0],[0,0],[0,0]]\nmove_unit=3\nrun()\n")#要給假值
        f.write("\nwho='P1'\n")
        with open(save_path+"lib"+file_end) as fin: 
            print("append lib:",filename)
            lines = fin.readlines() 
            for i, line in enumerate(lines):
                if i >= 0 and i < 6800:
                    f.write(line)

def test_code(compiler,save_path,filename,file_end):
    filetoexec=save_path+filename+file_end
    from subprocess import Popen, PIPE
    
    append_lib(save_path,filename,file_end)
    
    try: 
        p_gamemain = Popen(compiler+' '+save_path+'test_game'+file_end,shell=True, stdout=PIPE, stderr=PIPE)
        time.sleep(2)
        p = Popen(compiler + ' ' + filetoexec+' 0.0.0.0 1',shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stderr:
            print('stderr:', stderr)
            flash("oops, there is an error--",stderr)
            return [0,stderr]
        else:
            print('stdout:', stdout)
            flash("great, execuse successfully:",stdout)
            # browser
            
            return [1,stdout]
    except Exception as e:
        print('e: ',e)
        return [-1,e]

def save_code(save_path,filename,file_end,code):
    
    try:
        os.makedirs( save_path )
    except Exception as e:
        print('mkdir error:',e)
    decode = base64.b64decode(code)
    try:
        print("save code:",decode)
        with open("%s%s%s"%(save_path,filename,file_end), "wb") as f:
            f.write(decode)
    except Exception as e:
        print('write error:',e)

def send_to_web(event_name,send_data,listen_name,callback):
    print('sendtoweb')
    try:
        socketIO.on(listen_name,callback)
        socketIO.emit(event_name,send_data)
        socketIO.wait(1)
    except Exception as e:
        print('write error:',e)

    
