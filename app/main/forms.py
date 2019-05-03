from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField,PasswordField,BooleanField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User,Privacy,Status

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
	submit = SubmitField('Submit')
	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username

	def validate_username(self,username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
	post=TextAreaField('Say something', validators=[DataRequired(),Length(min=1, max=140)])
	submit = SubmitField('Submit')

class PrivacyForm(FlaskForm):
	privacy_name=TextAreaField('Privacy name', validators=[Length(min=1, max=140)])
	submit = SubmitField('Submit')
	def validate_privacy_name(self,name):
		privacy = Privacy.query.filter_by(privacy_name=self.privacy_name.data).first()
		if privacy is not None:
			raise ValidationError('Please use a different privacy name.')


class StatusForm(FlaskForm):
	status_name=TextAreaField('Status name', validators=[Length(min=1, max=140)])
	submit = SubmitField('Submit')
	def validate_status_name(self,name):
		status = Status.query.filter_by(status_name=self.status_name.data).first()
		if status is not None:
			raise ValidationError('Please use a different privacy name.')

