from app import create_app, db ,socketio
from app.models import User, Post, Log, Code

app = create_app()
# cli.register(app)


@app.shell_context_processor
def make_shell_context():
	return {'db':db, 'User':User, 'Post':Post, 'Log':Log, 'Code':Code}
	
if __name__ == '__main__':
	socketio.run(app)#,host='140.116.1.136'
	# ,ssl_context=('cert.pem', 'key.pem')