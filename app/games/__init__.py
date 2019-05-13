from flask import Blueprint

bp = Blueprint('games', __name__)
global current_game, current_log, current_code
current_game=123 
current_log='001'
current_code='010'
from app.games import routes,events

# class current_log(object):
# 	"""docstring for current_log"""
# 	def id():
# 		return '001'
# 	def game_id():
# 		pass
# 	def user_id():
# 		pass
