from flask import render_template, flash, redirect, url_for, request, current_app, session
from app import db
from app.games.forms import CreateGameForm, AddRoomForm, LoginForm, JoinForm, LeaveForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Game, Log, Code,Privacy,News,P_Score
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from app.games import bp
from websocket import create_connection
import json, sys
from .events import * # //in codegame.py

@bp.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    # 新增遊戲
    form = CreateGameForm()
    if form.validate_on_submit():
        game = Game(user_id=form.user_id.data,game_name=form.game_name.data,descript=form.descript.data, player_num=form.player_num.data,\
        category_id=form.category_id.data)
        db.session.add(game)
        db.session.commit()

        # '''obj_to_json'''
        g_query=Game.query.filter_by(game_name=form.game_name.data).first()
        result=""
        if isinstance(g_query, list):
            result = obj_to_json(g_query)
       
        game_result=json.dumps(result, cls=ComplexEncoder)
        flash('Congratulations, the game is created!')
        return redirect(url_for('games.add_room', gameObj=game_result))

    return render_template('games/create_game.html', title='Register', form=form)

def room_game_list(user_id,cat_id):
    code = Code.query.with_entities(Code.id,Code.game_id,Game.game_name,Game.descript,Category.name).filter(Code.user_id==user_id,Game.category_id==cat_id).join(Game,(Game.id==Code.game_id)).group_by(Game.id).all()
    game_choices=[(0,"default")]
    game_choices.extend([(g.game_id,g.game_name) for g in code])
    return game_choices

@bp.route('/get_g_list', methods=['GET','POST'])
@login_required
def get_g_list():
    if request.method == 'POST':
        if "text/plain" in request.headers['Content-Type']:
            set_g_option = room_game_list(current_user.id,int(request.data)) 
            # add_form.game.choices=set_g_option   
            return json.dumps({'g_list':set_g_option})

@bp.route('/get_g_player_num', methods=['GET','POST'])
@login_required
def get_g_player_num():
    if request.method == 'POST':
        if "text/plain" in request.headers['Content-Type']:
            game_player_num = Game.query.with_entities(Game.player_num).filter_by(id=int(request.data)).first()
            if len(game_player_num)>0:
                return str(game_player_num[0])
            else:
                return ""
        else:
            print("not \"text/plain\"")
            return ""
    else:
        print("not \"post\"")
        return ""

@bp.route('/add_room', methods=['GET','POST'])
@login_required
def add_room():
    # 開房間, add log data with game,user
    add_form = AddRoomForm()
    def room_category_list(user_id):  
        result_cat = Code.query.with_entities(Code.id,Code.game_id,Game.category_id,Category.name).filter_by(user_id=user_id).join(Game,(Game.id==Code.game_id)).join(Category,(Category.id==Game.category_id)).group_by(Category.id).all()
        cat_choices=[(0,"default")]
        cat_choices.extend([(c.category_id,c.name) for c in result_cat])
        return cat_choices

    if request.method == 'POST':
        add_form.game.choices=room_game_list(current_user.id,add_form.game_category.data) 
        category_list=room_category_list(current_user.id)
        add_form.game_category.choices=category_list  
        add_form.privacy.choices = Privacy.query.with_entities(Privacy.id,Privacy.privacy_name).all()
        if add_form.validate_on_submit():
            privacy=add_form.privacy.data
            player_num = add_form.player_num.data
            status = 0-player_num
            if privacy == 2: # 1-public, 2-official, 3-invited
                status = 0
            elif privacy == 3:
                invite_players = (add_form.invitelist.data).split(',')
            g = Game.query.filter_by(id=add_form.game.data).first()
            g.count +=1
            log = Log(roomname=add_form.roomname.data,game_id=add_form.game.data,privacy=privacy,status=status)
            db.session.add(log)
            # 若是設定 privacy==friends(指定玩家), log.current_users.append((choose_form.player_list).split(','))
            db.session.commit()
            return redirect(url_for('games.wait_to_play',log_id=log.id))
            # return redirect(url_for('games.room_wait',log_id=log.id))
        
    else:
        add_form.game_category.choices =  room_category_list(current_user.id)
        add_form.game.choices = [("0","default")]
        add_form.privacy.choices =  Privacy.query.with_entities(Privacy.id,Privacy.privacy_name).all()

    return render_template('games/room/add_room.html', title='add_room',form=add_form)


@bp.route('/wait_to_play/<int:log_id>', methods=['GET','POST'])
@login_required
def wait_to_play(log_id):
    session['log_id']=log_id
    # 檢查這個log的game有哪些可用的code, 列出語言, 有才讓 html的btn visable
    log_id = session.get('log_id', '')
    l=Log.query.filter_by(id=log_id).first()
    if l:
        all_codes =Code.query.with_entities(Code.id, Code.commit_msg,Language.language_name).filter_by(game_id=l.game_id, user_id=current_user.id).join(Log,(Log.id==log_id)).join(Language,(Language.id==Code.compile_language_id)).order_by(Code.id.desc()).all()
        all_lan=[]
        have_code=False
        try: 
            if len(all_codes) :
                for e in all_codes:
                    all_lan.append(e[2])
                flash(all_lan,'test')
                have_code=True
            else:
                return redirect(url_for('games.index',msg="you need to upload code from the local app first"))
        except Exception as e:
            print('error:',e)
            return redirect(url_for('games.index',msg="error:"+e))
        finally:
            if have_code:
                l= Log.query.filter_by(id=log_id).first()
                current_users = l.current_users
                if l.privacy is 1: # public,可以
                    rank_list_delself=""
                    if l.status < 0: # room還沒滿,可以進來參賽(新增 player_in_log data, update user的 current_log) # if s is not (0 or 1) :
                        game_start=False
                        if current_user not in current_users:
                            join_log(l,l.privacy)
                    
                    elif l.status is 0 :
                        if current_user not in current_users: 
                            print("sorry room is full, can't join game")
                            return redirect(url_for('games.index',msg="sorry, the room is full, can't join game"))
                        else:
                            game_start=False
                            
                    elif l.status ==1 : # gaming
                        game_start=True

                    else: #l.status ==2
                        return redirect(url_for('games.index',msg="sorry, the game is end"))
                        
                elif l.privacy == 2: # official
                    join_log(l,l.privacy)
                    rank_list=l.get_rank_list()
                    rank_list_delself=[]
                    for each_log in rank_list:
                        if each_log.username!=current_user.username:
                            rank_list_delself.append(each_log)
                    game_start=False
                    if l.status ==1 : # gaming
                        game_start=True
                else: # only invited
                    pass
        return render_template('games/game/spa.html', title='wait_play_commit',log=l,rank_list=rank_list_delself,all_codes=all_codes,game_start=game_start)
    else:
        return redirect(url_for('games.index',msg="The room is deleted"))

@bp.route('/rank_list/<int:log_id>', methods=['GET','POST'])
@login_required
def rank_list(log_id):
    l=Log.query.filter_by(id=log_id).first()
    # p_game = P_Score.query.filter_by(game_id=l.game_id).order.all()
    # p_game
    rank_list = l.get_rank_list()
    return render_template('games/game/rank_list.html', title='rank_list',rank_list=rank_list)

@bp.route('/game_status/<int:game_id>', methods=['GET','POST'])
@login_required
def game_status(game_id):
    g_name = Game.query.filter_by(id=game_id).first().game_name
    a_log = Log.query.filter_by(game_id=game_id).first()
    wait_log = Log.query.filter(Log.status<0,Log.game_id==game_id).all()
    gaming_log = Log.query.filter(Log.status==1,Log.game_id==game_id).all()
    game_players = P_Score.query.join(User,User.id==P_Score.user_id).with_entities(User.username,P_Score.score).order_by(P_Score.score.desc()).all()
    if a_log:
        rank_list = a_log.get_rank_list()
        return render_template('games/game/game_status.html', title='game_status',g_name=g_name,game_players=game_players,wait_log=wait_log,gaming_log=gaming_log,rank_list=rank_list)
    else:
        return redirect(url_for('games.index',msg="The game has no room"))

@bp.route('/display_record/<int:log_id>', methods=['GET','POST'])
@login_required
def display_record(log_id):
    log = Log.query.filter_by(id=log_id).first()
    lan1=Language.query.filter_by(id=log.the_codes[0].compile_language_id).first()
    lan2=Language.query.filter_by(id=log.the_codes[1].compile_language_id).first()
    record_content = json.loads(log.record_content)
    p1=User.query.filter_by(id=record_content['record_content'][0]['P1']).first().username
    p2=User.query.filter_by(id=record_content['record_content'][0]['P2']).first().username
    func_type = request.args.get('func_type')
    
    return render_template('games/game/display.html', title='display',players=[p1,p2],content=record_content['record_content'][1:],func_type=func_type,log_id=log_id,p1_code=log.the_codes[0].body,p2_code=log.the_codes[1].body,p1_lan_mode=lan1.language_name,p2_lan_mode=lan2.language_name)


@bp.route('/<string:msg>', methods=['GET', 'POST'])
@login_required
def index(msg):
    # 主畫面會有很多tab(News, NewsGame, HotGames,Discuss, Rooms)
    """Login form to enter a room."""
    form = LoginForm()
    flash(msg)
    if form.validate_on_submit():
        # 進入觀賽
        session['name'] = form.name.data
        session['room'] = form.room.data

        return redirect(url_for('.wait_to_play',log_id=form.room.data))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
        wait_rooms = Log.query.with_entities(Log.id,Log.roomname,Log.game_id,Game.game_name,Log.status,Game.player_num).filter(Log.status<0).join(Game,(Game.id==Log.game_id)).order_by(Log.timestamp.desc()).all()
        wait_room_users = Log.query.filter(Log.status<0).order_by(Log.timestamp.desc()).all()
        game_rooms = Log.query.with_entities(Log.id,Log.roomname,Log.game_id,Game.game_name,Log.status,Game.player_num).filter(Log.status==1,User.id==current_user.id).join(Game,(Game.id==Log.game_id)).order_by(Log.timestamp.desc()).all()
        game_room_users = Log.query.filter(Log.status==1,User.id==current_user.id).order_by(Log.timestamp.desc()).all()
        games = Game.query.order_by(Game.timestamp.desc()).limit(10).all()
        h_games = Game.query.order_by(Game.count.desc()).limit(10).all()
        news = News.query.order_by(News.timestamp.desc()).limit(5).all()
 
     
    return render_template('games/index/index.html', form=form,wait_rooms=wait_rooms,game_rooms=game_rooms,w_users=wait_room_users,g_users=game_room_users,news=news,games=games,h_games=h_games)

@bp.route('/gameover/<log_id>', methods=['GET','POST'])
@login_required
def gameover(log_id):
    # event.py收到gameserver的 'score'訊息後, redirect到此遊戲結束的 route, update log, 顯示分數
    # get record_content from gameserver or local var ?
    # record display in many jpeg 為學習影像處理存擋, 也用來做回顧播放
    log=Log.query.with_entities(Log.game_id).filter_by(id=log_id).first()
    print(Log.get_rank_list(Log,str(log[0])))# log[1]=game_id
    return render_template('games/index/index.html', title='Register')


def join_log(l,privacy_info):
    l.current_users.append(current_user) #current_users為該局的玩家名單
    current_users_len = len(l.current_users)
    if privacy_info==1:
        l.status +=1
    session['user_id']=current_user.id
    try:
        db.session.commit()
        print('update log status successfully',l.current_users)
    except Exception as e:
        db.session.rollback()
        print('update log error:',e)
    finally:
        # db.session.close()
        pass