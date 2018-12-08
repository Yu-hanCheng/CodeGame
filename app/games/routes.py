from flask import render_template, flash, redirect, url_for, request, current_app, session
from app import db
from app.games.forms import CreateGameForm, ChooseGameForm,CommentCodeForm, AddRoomForm, LoginForm, JoinForm, LeaveForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Game, Log, Code
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from app.games import bp, current_game, current_log, current_code, current_comment
from websocket import create_connection
import json, sys
from .events import * # //in codegame.py

current_game = '3333'
# print(current_log)
class ComplexDecoder(json.JSONDecoder):
	# 目前還沒用到
	def default(obj):
		return json.JSONDecoder.default(obj)
class ComplexEncoder(json.JSONEncoder):
	# 解開query時用到
	def default(self, obj):
		import datetime
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, datetime.date):
			return obj.strftime('%Y-%m-%d')
		else:
			return json.JSONEncoder.default(self, obj)

def obj_to_json(obj_list):
	# query出來之後 轉 json
	out = [q.__dict__ for q in obj_list]
	for objs, instance in zip(out, obj_list):
		for obj in objs.values():
			if callable(obj):
				for name in obj.mapper.relationships.keys():
					tmp = getattr(instance, name).__dict__
					if "_sa_instance_state" in tmp.keys():
						tmp.pop("_sa_instance_state")
						tmp.pop("id")
						objs.update(tmp)
					objs.pop(name)
		if "_sa_instance_state" in objs.keys():
			objs.pop("_sa_instance_state")
	return out
@bp.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
	# 新增遊戲
	form = CreateGameForm()
	if form.validate_on_submit():
		game = Game(user_id=form.user_id.data,gamename=form.gamename.data,descript=form.descript.data, player_num=form.player_num.data,\
		category_id=form.category_id.data,game_lib_id=form.game_lib_id.data)
		db.session.add(game)
		db.session.commit()


		# '''obj_to_json'''
		g_query=Game.query.filter_by(gamename=form.gamename.data).first()
		if isinstance(g_query, list):
			result = obj_to_json(g_query)
		elif getattr(g_query, '__dict__', ''):
			result = obj_to_json([g_query])
		else:
			result = {'result': g_query}
		game_result=json.dumps(result, cls=ComplexEncoder)
		# '''obj_to_json'''end

		flash('Congratulations, the game is created!')
		return redirect(url_for('games.add_room', gameObj=game_result))
	return render_template('games/create_game.html', title='Register', form=form)

@bp.route('/add_room', methods=['GET','POST'])
@login_required
def add_room():
	# 開房間, add log data with game,user
	add_form = AddRoomForm()
	if add_form.validate_on_submit():
		if add_form.privacy.data is 3:
			players = (add_form.players_status.data).split(',')
		else:
			game_player_num = Game.query.with_entities(Game.player_num).filter_by(id=add_form.game.data).first()
			players = game_player_num[0]
		log = Log(game_id=add_form.game.data,privacy=add_form.privacy.data,status=players)
		db.session.add(log)
		# 若是設定 privacy==friends(指定玩家), log.current_users.append((choose_form.player_list).split(','))
		db.session.commit()
		return redirect(url_for('games.wait_to_play',log_id=log.id))
		# return redirect(url_for('games.room_wait',log_id=log.id))

	return render_template('games/room/add_room.html', title='add_room',form=add_form)


@bp.route('/wait_to_play/<int:log_id>', methods=['GET','POST'])
@login_required
def wait_to_play(log_id):
	join_form = JoinForm()
	print("wait_to_play ",log_id)
	
	return render_template('games/game/spa.html', title='wait_play_commit',join_form=join_form,room_id=log_id)



@bp.route('/', methods=['GET', 'POST'])
def index():
	# 主畫面會有很多tab(News, NewsGame, HotGames,Discuss, Rooms)
	"""Login form to enter a room."""
	print("user:",session.get('username','nnnooo'))
	form = LoginForm()
	if form.validate_on_submit():
		session['name'] = form.name.data
		session['room'] = form.room.data

		return redirect(url_for('.game_view',log_id=current_log))
	elif request.method == 'GET':
		form.name.data = session.get('name', '')
		form.room.data = session.get('room', '')
		wait_rooms = Log.query.filter(Log.game_id>0).order_by(Log.timestamp.desc()).all()
		gaming_room = Log.query.filter(Log.game_id==0).order_by(Log.timestamp.desc()).all()
		# rooms = Room.query.order_by(Room.timestamp.desc()).all()
		
	   
	return render_template('games/index/index.html', form=form,wait_rooms=wait_rooms,gaming_room=gaming_room)

@bp.route('/gameover/<log_id>', methods=['GET','POST'])
@login_required
def gameover(log_id):
	# event.py收到gameserver的 'score'訊息後, redirect到此遊戲結束的 route, update log, 顯示分數
	# get record_content from gameserver or local var ?
	# record display in many jpeg 為學習影像處理存擋, 也用來做回顧播放
	Log.query.filter_by(id=log_id).update(dict(record_content=msg[1],score=msg[2],winner_id=msg[3]))
	# Log.query.filter_by(id=logId).update(dict(record_content='ooooo',score=300,winner_id=winner_id))
	log=Log.query.with_entities(Log.game_id).filter_by(id=log_id).first()
	db.session.commit()
	print(Log.get_rank_list(Log,str(log[0])))# log[1]=game_id
	return render_template('games/index.html', title='Register')

@bp.route('/uploader', methods = ['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return 'file uploaded successfully'
