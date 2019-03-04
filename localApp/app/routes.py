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
    code_path=save_path+filename+file_end
   
    save_code(save_path,filename,file_end,code)
    compiler = json_obj['lan_compiler']
    code_res = test_code(compiler,save_path,filename,file_end) # run code and display on browser
    
    if code_res[0]:
        print("code_ok")
        global code_data
        code_data={'code':code,'user_id':int(json_obj['user_id']),'commit_msg':json_obj['commit_msg'],'game_id':obj[3],'file_end':obj[7]}

    else:
        flash("Can't upload")
    return "received code"

@socketio.on('conn') #from localbrowser
def connect(message):
    print("conn from browser:",message['msg'])

@socketio.on('game_connect') #from test_game
def game_connect(message):

    print("conn from test game:",message['msg'])

@socketio.on('info')#from test_game
def gameobject(message):
    print("recv socketio msg:",message['msg'])
    socketio.emit('info', {'msg': message['msg']})

@socketio.on('over')#from test_game
def gameobject(message):
    print("over")
    socketio.emit('gameover', {'msg': message['msg'],'log_id':message['log_id']})

@socketio.on('upload_toWeb')#from localbrowser
def upload_code(message):
    global code_data
    def respose_toLocalapp(*args):
        print("upload_ok")
        socketio.emit('upload_ok', {'msg':""})
    send_to_web("upload_code",code_data,"upload_ok",respose_toLocalapp)
    


def append_lib(save_path,filename,file_end):
    with open("%s%s%s"%(save_path,'test_usercode',file_end), "w") as f:
        
        with open(save_path+filename+file_end) as f_usercode: 
            lines = f_usercode.readlines() 
            for i, line in enumerate(lines):
                if i >= 0 and i < 6800:
                    f.write(line)
        f.write("\nglobal paddle_vel,ball_pos,move_unit\npaddle_pos=0\npaddle_vel=0\nball_pos=[[0,0],[0,0],[0,0]]\nmove_unit=3\nrun()\n")
        f.write("\nwho='P1'\n")
        with open(save_path+"lib"+file_end) as fin: 
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
        p = Popen(compiler + ' '+save_path + 'test_usercode'+file_end+' 0.0.0.0 1',shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stderr:
            print('stderr:', stderr)
            p_gamemain.kill()
            p.kill()
            flash("oops, there is an error--",stderr)
            return [0,stderr]
        else:
            print('stdout:', stdout)
            p_gamemain.kill()
            p.kill()
            flash("great, execuse successfully:",stdout)
            # browser

            return [1,stdout]
    except Exception as e:
        p_gamemain.kill()
        p.kill()
        print('e: ',e)
        return [-1,e]

def save_code(save_path,filename,file_end,code):
    
    try:
        os.makedirs( save_path )
    except Exception as e:
        print('mkdir error:',e)
    decode = base64.b64decode(code)
    try:
        with open("%s%s%s"%(save_path,filename,file_end), "wb") as f:
            f.write(decode)
    except Exception as e:
        print('write error:',e)

def send_to_web(event_name,send_data,listen_name,callback):
    try:
        socketIO.on(listen_name,callback)
        socketIO.emit(event_name,send_data)
        socketIO.wait(1)
    except Exception as e:
        print('write error:',e)

    
