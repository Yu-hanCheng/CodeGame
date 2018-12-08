from flask import render_template, current_app
from app.email import send_email

def s_confirm_email(user,token):
    
    send_email('[CodeGame] confirm Your Email',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/confirm_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/confirm_email.html',
                                         user=user, token=token))

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[CodeGame] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))