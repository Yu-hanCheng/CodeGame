from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User, Log, Code, Game
from flask_login import current_user
from app.games import current_game,current_log,current_code


class CreateGameForm(FlaskForm):
	user_id = HiddenField('User id', default=current_user)
	gamename = TextAreaField('gamename', validators=[DataRequired()])
	descript = TextAreaField('descript', validators=[DataRequired()])
	player_num = IntegerField('player_num')
	category_id = IntegerField('category_id')

	game_lib_id = TextAreaField('game_lib_id')#, validators=[DataRequired()]
	example_code = TextAreaField('example code')# , validators=[DataRequired()]
	language = SelectField(
		'Programming Language',
		choices=[('cpp', 'C++'), ('py', 'Python'), ('js', 'Javascript')]
	)
	create = SubmitField('Create Game')
	
class AddRoomForm(FlaskForm):
	roomname = StringField('roomname', validators=[Length(min=0, max=20)])
	game_category = SelectField('Game Category',coerce=int,choices=[])
	game =  SelectField('Game',coerce=int,choices=[])
	user_id = HiddenField('User id', default=current_user)
	privacy =  SelectField('Opponent',coerce=int,choices=[])
	player_num  = IntegerField('player_num')#game.player_num
	
	submit = SubmitField('Enter Gameroom')
	# def validate_roomname(self, roomname):
	# 	room = Log.query.filter_by(roomname=roomname.data).first()
		# if room is not None:
		# 	raise ValidationError('Please use a different roomname.')



class LoginForm(FlaskForm):
	"""Accepts a nickname and a room."""
	name = StringField('UserName', validators=[DataRequired()])
	room = StringField('GameRoomId', validators=[DataRequired()])
	submit = SubmitField('Enter Chatroom')

class JoinForm(FlaskForm):
	submit = SubmitField('Join game')
class LeaveForm(FlaskForm):
	submit = SubmitField('Leave Chatroom')
