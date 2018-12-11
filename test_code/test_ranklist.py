import app
from app import db
from app.models import Log,User

rank_list = Log.query.with_entities(User.username,Log.game_id,Log.score).join(User,filter_by(game_id = self.game_id).order_by(Log.score.desc()).all()
rank_list = Log.query.join(User,(User.id==Log.winner_id)).filter_by(game_id = self.game_id).order_by(Log.score.desc()).all()
print(rank_list)