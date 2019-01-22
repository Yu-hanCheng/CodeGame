# 處理 browser, localapp, gamemain的 socketio溝通, 目前browser 會用 namespace='/test', 其他沒用
from flask import session,redirect, url_for,flash,request
from flask_socketio import emit, join_room, leave_room,send
from .. import socketio # //in CodeGame.py
from flask_login import current_user
from app.models import User, Game, Log, Code,Game_lib, Language
from app import db
from websocket import create_connection
import json

@socketio.on('gamemain_connect')
def gamemain_connect(message):
    print(" gamemain_connect")
    emit('connect_start',message,namespace = '/test',room= message['log_id'])
    
@socketio.on('over') 
def game_over(message):
    # msg：tuple([l_score,r_score,gametime])??
    # alert myPopupjs(玩家成績報告) on browser
    # save all report not only record content -- 0122/2019
    # print('message[msg][score]:',type(json.loads(message['msg']['l_report'])),json.loads(message['msg']['l_report']))
    l_report=json.loads(message['msg']['l_report'])
    r_report=json.loads(message['msg']['r_report'])
    emit('gameover', {'msg': message['msg'],'log_id':message['log_id']},namespace = '/test',room= message['log_id'])
    print('message[log_id]:',message['log_id'])
    if l_report['score']>r_report['score']:
        winner=l_report['user_id']
    else:
        winner=r_report['user_id']
    
    l=Log.query.filter_by(id=message['log_id']).first()
    
    l.winner_id = winner
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
    print(message['msg'])
    emit('gameobject', {'msg': message['msg']},namespace = '/test',room= message['log_id'])#,room= message['msg'][3]

@socketio.on('select_code' ,namespace = '/test')
def select_code(message):
    # Sent by clients when they click btn.
    # call emit_code to send code to gameserver.-- 0122/2019
    print('msg in select_code',message)
    l=Log.query.with_entities(Log.id,Log.game_id,Game.category_id,Game.player_num).filter_by(id=message['room']).first()
    select_code =Code.query.with_entities(Code.id,Code.body, Code.commit_msg,Code.compile_language_id,Language.language_name).filter_by(id=message['code_id']).join(Log,(Log.id==message['room'])).join(Language,(Language.id==Code.compile_language_id)).order_by(Code.id.desc()).first()
    print('checked_code',select_code)
    emit_code(l, select_code)

@socketio.on('commit' ,namespace = '/local')
def commit_code(message):
    # 接收並儲存 localApp上傳的程式碼 -- 0122/2019
    print('commit:',message)
    code = Code(body=message['code'], commit_msg=message['commit_msg'],game_id=message['game_id'],compile_language_id=message['glanguage'],user_id=current_user.id)
    
    try:
        db.session.add(code)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        pass
# -- 0122/2019
@socketio.on('left',namespace = '/test' )
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

def emit_code(l,code):
# join_log(log_id,message['code'],message['commit_msg'],l.game_id,current_user.id,players)
    print('l:',type(l),l)
    ws = create_connection("ws://127.0.0.1:6005")
    ws.send(json.dumps({'from':'webserver','code':code.body,'log_id':l.id,'user_id': current_user.id,'category_id':l.category_id,'game_id':l.game_id,'language':code.language_name,'player_num':int(l.player_num)}))
    result =  ws.recv() #
    print("Received '%s'" % result)
    ws.close()

#for local
@socketio.on('get_gamelist')
def get_gamelist():
    sid = request.sid
    g_list=Game.query.with_entities(Game.id,Game.gamename,Game.descript).all()
    print("g_list:",g_list)
    emit('g_list',g_list, room=sid)

@socketio.on('get_lanlist')
def get_lanlist(message):
    sid = request.sid
    lan_list=Game_lib.query.with_entities(Game_lib.id, Language.id, Language.language_name).filter_by(game_id=message['game_id']).join(Language,(Game_lib.language_id==Language.id)).all()
    print("lan_list:",lan_list)
    emit('lan_list',lan_list, room=sid)





        