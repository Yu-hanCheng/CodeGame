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
code_data=""
isCodeOk=0
p_gamemain=""
p=""
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
def library():
    
    savepath = request.form.get('path',False)
    file_end = request.form.get('end',False) 
    save_code(savepath,"test_game",'.py',request.form.get('test_game',False),"")
    save_code(savepath,"test_lib",file_end,request.form.get('test_lib',False),"")
    
    return "set library ok"


@app.route('/commit',methods=['GET','POST'])
def commit():
    # save
    # {"encodedData":encodedData,"commit_msg":commit_msg,"lan_compiler":lan_compiler,'obj':obj,'user_id':1,}
    # // 0Game_lib.id,1Category.id,2Category.name,3Game.id,4Game.game_name,5Language.id, 6Language.language_name, 7Language.filename_extension
    # socket.emit('commit', {code: editor_content, commit_msg:commit_msg, game_id:game_id, glanguage:glanguage, user_id:1});
    global code_data,isCodeOk
    isCodeOk=0
    data = request.data
    json_obj=json.loads(data)
    obj=json_obj["obj"].split(",")
    code_model = json_obj['encodedData']
    code = code_model['code']
    save_path = obj[1]+"/"+obj[3]+"/"+obj[5]+"/"
    save_path_name = obj[2]+"/"+obj[4]+"/"+obj[6]+"/"
    file_end = obj[7]
    have_M=""
    # str(data.get('lan_compiler'))

    if code_model['choosed']!="":

        the_model = code_model['choosed'].split(",")
        save_code("model/","usermodel_"+time.strftime("%m_%d_%H_%M_%S", time.localtime()),".sav",the_model[-1],have_M)
        have_M="usermodel_"+time.strftime("%m_%d_%H_%M_%S", time.localtime())
        # save_code("","usermodel_"+time.strftime("%m_%d_%H_%M_%S", time.localtime()),".sav",the_model[-1])
        code_data={'code':code,'ml_model':code_model['choosed'],'user_id':int(json_obj['user_id']),'commit_msg':json_obj['commit_msg'],'game_id':obj[3],'file_end':obj[7]}
    else:
        code_data={'code':code,'ml_model':"",'user_id':int(json_obj['user_id']),'commit_msg':json_obj['commit_msg'],'game_id':obj[3],'file_end':obj[7]}

    decode = bytes(base64.b64decode(code))
    security_res=test_security(decode)
    socketio.emit('security', {'msg': security_res})

    if  security_res[0]:
        # set filename
        f = []
        for (dirpath, dirnames, filenames) in walk(save_path):
            f.extend(filenames)
            break
        filename=str(len(f)-2)#['.DS_Store', 'gamemain.py', 'lib.py']
        code_path=save_path+filename+file_end
    
        save_code(save_path,filename,file_end,code,have_M)
        compiler = json_obj['lan_compiler']
        
        
        code_res = test_code(compiler,save_path,filename,file_end) # run code and display on browser

        if code_res[0] and isCodeOk!=2 :
            print("code_ok")
            isCodeOk=1
            return "test ok"

        else:
            socketio.emit('code_inavailable', {'msg': code_res[1]})
            flash("Can't upload")

        return "test fail"
    else:
        return "unavailible lib"

@socketio.on('conn') #from localbrowser
def connect(message):
    print("conn from browser:",message['msg'])

@socketio.on('game_connect') #from test_game
def game_connect(message):
    socketio.emit('game_connect', {'msg': ''})
    print("conn from test game:",message['msg'])

@socketio.on('info')#from test_game
def gameobject(message):
    socketio.emit('info', {'msg': message['msg']})

@socketio.on('over')#from test_game
def gameobject(message):
    print("over")
    # global p_gamemain,p
    # p.kill()
    # p_gamemain.kill()
    message['msg']['l_report'] = message['msg']['l_report'].replace("'", '"')
    socketio.emit('gameover', {'msg': message['msg'],'log_id':message['log_id']})

@socketio.on('upload_toWeb')#from localbrowser
def upload_code(message):
    global code_data
    print("upload_code")
    def respose_toLocalapp(*args):
        print("upload_ok,code_data:",code_data)
        socketio.emit('upload_ok', {'msg':""})
    send_to_web("upload_code",code_data,"upload_ok",respose_toLocalapp)

@socketio.on('timeout')#from localbrowser
def timeout(message):
    socketio.emit('timeout', {'msg':""})
    global p_gamemain,p,isCodeOk
    isCodeOk=2
    try :
        p.kill()
        p_gamemain.kill()
    except Exception as e:
        print("timeout kill, e:",e)


def test_security(only_user_code):
    a=[' os',' sys',' subprocess']
    byte_code = only_user_code.decode(encoding='UTF-8',errors='strict')
    time.sleep(0.1)
    res=[1]
    for x in a:
        if x in byte_code: 
            print("%s is illegal word:"%x)
            res[0]=0
            res.append(x)
        else: 
            print("%s ok"%x)
    print("res:",res)
    return res

def append_lib(save_path,filename,file_end):
    with open("%s%s%s"%(save_path,'test_usercode',file_end), "w") as f:
        f.write('\n')
        with open(save_path+filename+file_end) as f_usercode: 
            lines = f_usercode.readlines() 
            for i, line in enumerate(lines):
                if i >= 0 and i < 6800:
                    f.write(line)
        lan = save_path.split('/')[-2]
        if lan =="1":
            f.write("\n#define WHO 'P"+str(i+1)+"'\n")
        elif lan=="2":
            f.write("\nwho='P1'\n")

        with open(save_path+"test_lib"+file_end) as fin: 
            lines = fin.readlines() 
            for i, line in enumerate(lines):
                if i >= 0 and i < 6800:
                    f.write(line)

def test_code(compiler,save_path,filename,file_end):
    filetoexec=save_path+filename+file_end
    from subprocess import Popen, PIPE
    global p_gamemain,p
    append_lib(save_path,filename,file_end)
    
    try: 
        p_gamemain = Popen('python '+save_path+'test_game.py'+' 5501',shell=True, stdout=PIPE, stderr=PIPE,close_fds=True)
        
        time.sleep(2)
        if file_end=='.c':
            p = Popen(compiler + ' '+save_path + 'test_usercode'+file_end,shell=True, stdout=PIPE, stderr=PIPE,close_fds=True)
            stdout, stderr = p.communicate()
        elif file_end=='.py':
            p = Popen(compiler + ' '+save_path + 'test_usercode'+file_end+' 0.0.0.0 8800 1',shell=True, stdout=PIPE, stderr=PIPE,close_fds=True)
            stdout, stderr = p.communicate()
        if stderr:
            print('stderr:', p.returncode,stderr)
            p_gamemain.kill()
            p.kill()
            flash("oops, there is an error--",stderr)
            return [0,stderr]
        else:
            print("p.returncode",p.returncode)
            if p.returncode ==1:
                return [0,"type of paddle is not int"]
            flash("great, execuse successfully:",stdout)
            # browser

            return [1,stdout]
    except Exception as e:
        p_gamemain.kill()
        p.kill()
        print('e: ',e)
        return [-1,e]

def save_code(save_path,filename,file_end,code,have_M):
    
    try:
        os.makedirs( save_path )
    except Exception as e:
        print('mkdir error:',e)
    decode = base64.b64decode(code)
    try:
        with open("%s%s%s"%(save_path,filename,file_end), "wb") as f:
            if have_M!="":
                lib_part=bytes("import pickle\n\
import numpy as np\n\
filename=\"model/"+have_M+".sav\"\n\
load_model = pickle.load(open(filename, 'rb'))\n","utf-8")
                f.write(lib_part)
            f.write(decode)
    except Exception as e:
        print('write error:',e)

def send_to_web(event_name,send_data,listen_name,callback):
    try:
        print("send_to_web")
        socketIO.on(listen_name,callback)
        socketIO.emit(event_name,send_data)
        socketIO.wait(1)
    except Exception as e:
        print('write error:',e)

    
