# 處理 browser, localapp, gamemain的 socketio溝通, 目前browser 會用 namespace='/test', 其他沒用
from flask import session,redirect, url_for,flash,request,current_app
from flask_socketio import emit, join_room, leave_room,send
from .. import socketio # //in CodeGame.py
from flask_login import current_user
from app.models import User, Game, Log, Code, Game_lib, Language, Category
from app import db
from websocket import create_connection
import json,base64,time
from eventlet.green import threading
import eventlet

@socketio.on('gamemain_connect')
def gamemain_connect(message):
    users_list=[]
    the_p1 = User.query.with_entities(User.username).filter_by(id=message['msg']['P1']).first()
    users_list.append(the_p1[0])
    the_p2 = User.query.with_entities(User.username).filter_by(id=message['msg']['P2']).first()
    users_list.append(the_p2[0])
    emit('gamemain_connect',users_list,namespace = '/test',room= message['log_id'])

@socketio.on('timeout_over') 
def timeout_over(message):
    emit('timeout_over',message['msg']['user'],namespace = '/test',room= message['log_id'])
    app = current_app._get_current_object() 
    name = message['log_id']+"_stop"
    globals()[name] = threading.Event()
    globals()[name].clear()
    eventlet.spawn(notify_browser,60,message['log_id'],app,globals()[name]) 

@socketio.on('timeout') 
def timeout(message):
    emit('timeout',message['msg']['user'],namespace = '/test',room= message['log_id'])

@socketio.on('over') 
def game_over(message):
    # msg：tuple([l_score,r_score,gametime])??
    # alert myPopupjs(玩家成績報告) on browser
    # save all report not only record content -- 0122/2019
    message['msg']['l_report'] = message['msg']['l_report'].replace("'", '"')
    message['msg']['r_report'] = message['msg']['r_report'].replace("'", '"')
    
    l_report=json.loads(message['msg']['l_report'])
    r_report=json.loads(message['msg']['r_report'])
    emit('gameover', {'msg': message['msg'],'log_id':message['log_id']},namespace = '/test',room= message['log_id'])
    
    
    
    
    l=Log.query.filter_by(id=message['log_id']).first()
    if l_report['score']>r_report['score']:
        l.winner_id =l_report['user_id']
        l.winner_code_id=l_report['code_id']
    else:
        l.winner_id =r_report['user_id']
        l.winner_code_id=r_report['code_id']
    save_content = json.dumps(message['msg'])
    l.record_content = save_content
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        pass


@socketio.on('info')
def test_connect(message):
    # 接收來自 gamemain的訊息並再傳至browser
    # msg={'type':type_class,'who':who,'content':content, 'cnt':cnt} -- 0122/2019
    emit('gameobject', {'msg': message['msg']},namespace = '/test',room= message['log_id'])#,room= message['log_id']

@socketio.on('join_room' ,namespace = '/test')
def join_room_from_browser(message):
    join_room(message['room'])
    app = current_app._get_current_object()  # get the real app instance
    

    if int(message['status']) ==0:
        emit('enter_room',message['privacy'],namespace = '/test',room= message['room'])
        if int(message['privacy'])==1:
            # set_interval(app,notify_browser,1,60,message['room'])
            all_code = message['room']+"_all"
            globals()[all_code]=0
            name = message['room']+"_stop"
            globals()[name] = threading.Event()
            globals()[name].clear()
            eventlet.spawn(notify_browser,60,message['room'],app,globals()[name]) 
            print("join room",message['room'],threading.enumerate())
            
    else:
        emit('wait_room',namespace = '/test',room= message['room'])    

@socketio.on('change_code',namespace = '/test')
def change_code(message):
    l=Log.query.with_entities(Log.id,Log.game_id,Game.category_id,Game.player_num).filter_by(id=message['room']).first()
    select_code =Code.query.with_entities(Code.id,Code.body, Code.commit_msg,Code.compile_language_id,Language.language_name).filter_by(id=message['code_id']).join(Log,(Log.id==message['room'])).join(Language,(Language.id==Code.compile_language_id)).order_by(Code.id.desc()).first()
    emit('the_change_code',{'code':select_code.body,'code_commit_msg':select_code.commit_msg,'code_id':message['code_id']},namespace = '/test',room= message['room']) 

@socketio.on('select_code' ,namespace = '/test')
def select_code(message):
    all_code = message['room']+"_all"
    globals()[all_code]+=1
    print('globals()[all_code]:',globals()[all_code])
    # Sent by clients when they click btn.
    # call emit_code to send code to gameserver.-- 0122/2019
    l=Log.query.with_entities(Log.id,Log.game_id,Game.category_id,Game.player_num).filter_by(id=message['room']).first()
    if globals()[all_code]==l.player_num :
        name = message['room']+"_stop"
        globals()[name].set()

    print(message['room'],threading.enumerate())
    select_code =Code.query.with_entities(Code.id,Code.body,Code.attach_ml, Code.commit_msg,Code.compile_language_id,Language.language_name).filter_by(id=message['code_id']).join(Log,(Log.id==message['room'])).join(Language,(Language.id==Code.compile_language_id)).order_by(Code.id.desc()).first()
    emit_code(l, select_code,current_user.id)
    
    if message['opponent']!="":
        opponent = json.loads(message['opponent'].replace("'", '"'))
        select_code = Code.query.with_entities(Code.id,Code.body,Code.attach_ml, Code.commit_msg,Code.compile_language_id,Language.language_name).\
        filter_by(id=opponent['code_id']).join(Language,(Language.id==Code.compile_language_id)).first()
        emit_code(l, select_code,str(opponent['username']))
    

@socketio.on('upload_code')# ,namespace = '/local'
def upload_code(message):
    # 接收並儲存 localApp上傳的程式碼 -- 0122/2019
    # {'code':code,'user_id':json_obj['user_id'],'commit_msg':commit_msg,'game_id':obj[3],'file_end':obj[7]}
    # Language.filename_extension
    sid = request.sid
    lan_id = set_language_id(message['file_end'])
    code = Code(body=message['code'], commit_msg=message['commit_msg'],game_id=message['game_id'],compile_language_id=lan_id,user_id=message['user_id'])
    
    try:
        db.session.add(code)
        db.session.commit()
        the_model = message['ml_model'].split(",")
        if len(the_model[-1])>20:
            code.attach_ml=True
            db.session.commit()
            save_file(code.id,the_model[-1])
        emit('upload_ok',"ok, code save in web", room=sid)
    except:
        db.session.rollback()
    finally:
        pass
# -- 0122/2019
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    print("left log:",type(message['room']),message['room'])
    l=Log.query.filter_by(id=int(message['room'])).first()
    g=Game.query.filter_by(id=l.game_id).first()
    l.status -=1
    l.current_users.remove(current_user)
    leave_room(str(message['room']))
    if l.status+g.player_num == 0 and not l.winner_id:
        db.session.delete(l)
    else:
        name = str(message['room'])+"_stop"
        globals()[name].set()
        emit('wait_room',namespace = '/test',room= str(message['room']))
    db.session.commit()

@socketio.on('chat_message' ,namespace = '/test')
def chat_message(message):
    room = session.get('log_id')
    emit('chat_message_broadcast',{'user':current_user.username,'msg':message},namespace = '/test', room=str(room)) #{'user': current_user.id,'msg': message}

def emit_code(l,code,the_user):
# join_log(log_id,message['code'],message['commit_msg'],l.game_id,current_user.id,players)
    if type(the_user) is not int:
        opponent_id = User.query.with_entities(User.id).filter_by(username=the_user).first()
        user_id=opponent_id[0]
    else:
        user_id=the_user
    ml_file=""
    if code.attach_ml:
        with open("%s.sav"%(code.id), "rb") as f_ml:
            ml_file = f_ml.read().decode() # convert to str
    ws = create_connection("ws://127.0.0.1:6005")# to gameserver
    ws.send(json.dumps({'from':'webserver','code_id':code.id,'code':code.body,'attach_ml':code.attach_ml,'ml_file':ml_file,'log_id':l.id,'user_id': user_id,'category_id':l.category_id,'game_id':l.game_id,'language':code.language_name,'player_num':int(l.player_num)}))
    result =  ws.recv() #
    print("Received '%s'" % result)
    ws.close()

#for local
@socketio.on('get_gamelist')
def get_gamelist(msg):
    sid = request.sid
    g_list=Game.query.with_entities(Game.id,Game.gamename,Game.descript).all()
    
    emit('g_list',g_list, room=sid)

@socketio.on('get_lanlist')
def get_lanlist(message):
    sid = request.sid
    lan_list=Game_lib.query.with_entities(Game_lib.id,Category.id,Category.name,Game.id,Game.gamename,Language.id, Language.language_name, Language.filename_extension).filter_by(game_id=message['game_id']).join(Language,(Game_lib.language_id==Language.id)).join(Game,(Game.id==message['game_id'])).join(Category,(Category.id==Game.category_id)).group_by(Language.id).all()
    # 取Category.name,Game.gamename是為了localapp端將code存成檔案的路徑
    
    emit('lan_list',lan_list, room=sid)

@socketio.on('get_lib')
def get_lib(msg):
    sid = request.sid
    path = "%s/%s/%s/"%(msg['category_id'],msg['game_id'],msg['language_id'])
    end = msg['filename_extension']
    global library,gamemain
    with open("gameserver/%stest_lib%s"%(path,end), "r") as f:
        library = base64.b64encode(bytes(f.read(), 'utf8'))
    with open("gameserver/%stest_game.py"%(path), "r") as f_game:
        gamemain = base64.b64encode(bytes(f_game.read(), 'utf8'))
    emit('library',[path,end,library,gamemain], room=sid)

@socketio.on('check_user')# '/local'
def check_user(message):
    # localApp使用者登入確認 -- 0123/2019
    print("check_user")
    sid = request.sid
    user = User.query.filter_by(username=message['uname']).first()
    if user is None:
        emit('checked_user',{'checked':False,'msg':'uname'}, room=sid)
        print("user none")
        
    elif  not user.check_password(message['password']):
        emit('checked_user',{'checked':False,'msg':'pwd'}, room=sid)
        print("false pwd")
    else:
        emit('checked_user',{'checked':True,'user_id':user.id}, room=sid)
        print("ok user")

@socketio.on('disconnect')
def test_disconnect():
    log_id = session.get('log_id', '')

    if log_id:
        left({'room':log_id})
    else:
        print("log_id is ''")

def set_language_id(filename_extension):
    compiler = {
        ".c":1,
        ".py":2,
        ".sh":3
    }
    language_id = compiler.get(filename_extension, "Invalid language ID")
    return language_id

def save_file(filename, file): # filename = code_id
    with open("%s.sav"%(filename), "w") as f:
        f.write(file)
        
def notify_browser(data,sendroom,app,event):
    with app.app_context():
        times = data
        while times>0: 
            e = event.wait(1)
            if e:
                print("ready")
                return
            else:
                print(sendroom,"emit")
                emit('countdown',times, namespace = '/test',room= sendroom)
                time.sleep(1) 
                times -= 1
        emit('countdown',times, namespace = '/test',room= sendroom)
