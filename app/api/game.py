from app.games import bp
from flask import jsonify, request, url_for
from app.models import User
from app import db
from app.api.errors import bad_request 
from flask_httpauth import HTTPTokenAuth
from app.api.auth import token_auth

@bp.route('/games/view/<int:id>',methods=['GET'])
@token_auth.login_required
def get_game_view(id):
	return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/games/<int:game_id>/rank',methods=['GET'])
def over_game(id):
	game = Game.query.get_or_404(game_id)
	page = request.args.get('page',1,type=int)
	per_page = min(request.args.get('per_page',10,type=int),100)
	data = Game.to_collection_dict(game.ranks, page, per_page,'api.get_followers',id=id)
	return jsonify(data)
@bp.route('/games/<int:game_id>/history/<int:user_id>',methods=['GET'])
@bp.route('/games/<int:id>/rank',methods=['GET'])
@token_auth.login_required
def commit_code():
	page = request.args.get('page', 1, type=int)
	per_page = min(request.args.get('per_page',10, type=int), 100)
	data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
	return jsonify(data)


@bp.route('/games/<int:id>/followers',methods=['GET'])
@token_auth.login_required
def over_game(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page',1,type=int)
	per_page = min(request.args.get('per_page',10,type=int),100)
	data = User.to_collection_dict(user.followers, page, per_page,'api.get_followers',id=id)
	return jsonify(data)

@bp.route('/codes/<int:codeId>', methods=['GET','POST'])
@login_required
def comment_code(codeId):
	form = CommentCodeForm() #current_log.id
	if form.validate_on_submit():
		comment = Comment(code_id=form.code_id.data, body=form.body.data)
		db.session.add(code)
		db.session.commit()
		flash('Your code have been saved.')
		# return redirect(url_for('game.start_game')) #不重新整理頁面
	# elif request.method == 'GET':
	return render_template('games/comment_code.html', title='Commit Code',
                           form=form)
	
@bp.route('/games', methods=['POST'])
def create_game():
	data = request.get_json() or {}
	if 'descript' not in data or 'game_lib' not in data or 'example_code' not in data or 'gamename' not in data:
		return bad_request('must include descript, game_lib, example_code, gamename fields')
	if Game.query.filter_by(gamename=data['gamename']).first():
		return bad_request('please use a different gamename')
	game=Game()
	game.from_dict(data, new_user=True)
	db.session.add(game)
	db.session.commit()
	response = jsonify(game.to_dict())
	response.status_code = 201
	response.headers['Location'] = url_for('api.get_game', id=game.id)
	return response



@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
	print('update user')
	user = User.query.get_or_404(id)
	data = request.get_json() or {}
	if 'username' in data and data['username'] != user.username and User.query.filter_by(username=data['username']).first():
		return bad_request('must include username, email, password fields')
	if 'email' in data and data['email']!= user.email and User.query.filter_by(email=data['email']).first():
		return bad_request('please user a different email address')
	user.from_dict(data, new_user=False)
	db.session.commit()
	return jsonify(user.to_dict())

