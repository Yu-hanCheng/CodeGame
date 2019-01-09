from flask import session,redirect, url_for
from flask_socketio import emit, join_room, leave_room,send
from .. import socketio # //in CodeGame.py
from flask_login import current_user
from app.models import User, Game, Log, Code,Game_lib
from app import db
from websocket import create_connection
import json

@socketio.on('connect', namespace='/test')
def new_connect():
    print("client connect")

@socketio.on('gamemain_connect')
def gamemain_connect(message):
    print(" gamemain_connect")
    emit('connect_start',message,namespace = '/test',room= message['log_id'])
    
@socketio.on('over') 
def game_over(message):
    # msg：tuple([l_score,r_score,gametime])??
    # 使 webserver切換至 gameover路由
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
        # db.session.close()
        pass

    # if 
    # l[0].winner=
    # return redirect(url_for('games.gameover',log_id= message['log_id']))

@socketio.on('info')
def test_connect(message):
    # 接收來自 exec主機 gamemain傳送的訊息並再傳至browser
    # msg:??
    print(message['msg'])
    emit('gameobject', {'msg': message['msg']},namespace = '/test',room= message['log_id'])#,room= message['msg'][3]

@socketio.on('join' ,namespace = '/test')
def joined(message):
    # 一個房間會有 n+1的連線數(n個 browser, 一個gamemain)
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    log_id = message['room'] #session.get('room') 
    session['log_id']=log_id
    join_room(log_id)
    emit('enter_room', {'msg': log_id},namespace = '/test',room= log_id)
    l= Log.query.filter_by(id=log_id).first()
    print("log",log_id,l.privacy,l.status)
    players = l.current_users

    if l.privacy is 1: # public,可以
        if l.status is 0 : # room滿
            print("can't join game")
            
        else: # room還沒滿,可以進來參賽(新增 player_in_log data, update user的 current_log) # if s is not (0 or 1) :
            in_list=False
            for i,player in enumerate(players):
                if player == current_user.id:
                    print("already in")
                    in_list=True
                    break
            if not in_list:
                join_log(l,message['code'],message['glanguage'],players)
            if l.status is 0 :#這需要嗎? 開始遊戲的通知？
                # emit('arrived', {'msg': current_user.id},namespace = '/test',room= log_id)
                pass
    elif l.privacy == 2: # friend
        pass
    else: # only invited
        pass
@socketio.on('check_code' ,namespace = '/test')
def check_code(message): # mode_id
    log_id = session.get('log_id', '')
    l=Log.query.filter_by(id=log_id).first()
    checked_code =Code.query.with_entities(Code.id, Code.commit_msg).filter_by(game_id=l.game_id, user_id=current_user.id,compile_language_id=message).join(Log,(Log.id==log_id)).order_by(Code.id.desc()).first()
        if checked_code :
            code_id=checked_code[0]
            flash(code_id)

@socketio.on('commit' ,namespace = '/test')
def commit_code(message):
   
    log_id = session.get('log_id', '')
    l=Log.query.filter_by(id=log_id).first()
    editor_content = message['code']
    
    commit_msg =  message['commit_msg']
        
    code = Code(log_id=log_id, body=editor_content, commit_msg=commit_msg,game_id=l.game_id,user_id=current_user.id)
    
    try:
        db.session.add(code)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        # db.session.close()
        pass
    game = Game.query.filter_by(id=l.game_id).first()
    players = l.current_users
    player_list = []

    # player_list 原因, TypeError: Object of type 'User' is not JSON serializable
    # gameserver那邊, 如果 player_list已空 表示 arrived
    for i,player in enumerate(players):
        if player.id == current_user.id:
            print("no append ",player.id)
        else:
            print("append: ",player.id)
            player_list.append(player.id)

    ws = create_connection("ws://140.116.82.226:6005")
    ws.send(json.dumps({'from':'webserver','code':editor_content,'log_id':log_id,'user_id':current_user.id,'category_id':game.category_id,'game_id':l.game_id,'language':message['glanguage'],'player_list':player_list}))
    result =  ws.recv() #
    print("Received '%s'" % result)
    ws.close()
    
    
    @socketio.on('text' ,namespace = '/test')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)


@socketio.on('left',namespace = '/test' )
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

def join_log(l,code_id,glanguage,players):
# join_log(log_id,message['code'],message['commit_msg'],l.game_id,current_user.id,players)
    print('l:',type(l),l)
    game= Game.query.with_entities(Game.player_num,Game.category_id).filter_by(id=l.game_id).first()
    l.current_users.append(current_user) #current_users為該局的玩家名單
    current_users_len = len(l.current_users)
    l.status = int(game.player_num) - current_users_len
    current_user.current_log_id = l.id

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('update log error:',e)
    finally:
        # db.session.close()
        pass
    # ws = create_connection("ws://140.116.82.226:6005")
    code = Code.query.with_entities(Code.body).filter_by(id=code_id).first()

    ws = create_connection("ws://127.0.0.1:6005")
    ws.send(json.dumps({'from':'webserver','code':code[0],'log_id':l.id,'user_id': current_user.id,'category_id':game.category_id,'game_id':l.game_id,'language':glanguage,'player_num':int(game.player_num)}))
    result =  ws.recv() #
    print("Received '%s'" % result)
    ws.close()

        