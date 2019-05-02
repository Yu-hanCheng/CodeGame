from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import logging #python package, DEBUG, INFO, WARNING, ERROR and CRITICAL
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from flask_moment import Moment
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

login.login_view = 'auth.login' #would use in a url_for() call to get the URL.
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
# babel = Babel()

socketio = SocketIO()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)
	app.config['SECRET_KEY'] = 'secret!'
	app.config['MAIL_SERVER']='smtp.googlemail.com'
	app.config['MAIL_PORT']='587'
	app.config['MAIL_USE_TLS']='1'
	app.config['MAIL_USERNAME']='sarahcheng1231'
	app.config['MAIL_PASSWORD']='2016sarahcheng'
	socketio.init_app(app)

	db.init_app(app)
	migrate.init_app(app,db)
	login.init_app(app)
	mail.init_app(app)
	bootstrap.init_app(app)
	moment.init_app(app)
    # babel.init_app(app)
	
	
	from app.errors import bp as errors_bp
	app.register_blueprint(errors_bp)

	from app.auth import bp as auth_bp
	app.register_blueprint(auth_bp, url_prefix='/auth')
	from app.main import bp as main_bp
	app.register_blueprint(main_bp)

	from app.api import bp as api_bp
	app.register_blueprint(api_bp, url_prefix='/api')
	
	from app.games import bp as games_bp
	app.register_blueprint(games_bp, url_prefix='/games')

	app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '160139164703343',
        'secret': '4a005ebc42acab187de54ba991ef3ea6'
    },
    'google': {
        'id': '160139164703343',
        'secret': '4a005ebc42acab187de54ba991ef3ea6'
    }
	}

	if not app.debug and not app.testing:
		if app.config['MAIL_SERVER']:
			auth = None
			if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
				auth=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
			secure = None
			if app.config['MAIL_USE_TLS']: #Transport Layer Security 
				secure=()
			mail_handler = SMTPHandler(
				mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
				fromaddr = 'no-reply@'+app.config['MAIL_SERVER'],
				toaddrs = app.config['ADMINS'], subject='CodeGame Failure',
				credentials = auth, secure=secure
				)
			mail_handler.setLevel(logging.ERROR)
			app.logger.addHandler(mail_handler)
		if not os.path.exists('logs'):
			os.mkdir('logs')
		file_handler = RotatingFileHandler('logs/codegame.log', maxBytes=10240, backupCount=10)
		file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)

		app.logger.addHandler(logging.INFO)
		app.logger.info('CodeGame startup')
	return app
