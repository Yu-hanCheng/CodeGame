from flask import render_template, flash, redirect, url_for, request
from app import db
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
from app.auth.email import send_password_reset_email,s_confirm_email
from oauth import OAuthSignIn
from app.auth import bp


@bp.route('/send_confirm_email/<email_data>',methods=['GET'])
def send_confirm_email(email_data):
    user = User.query.filter_by(email=email_data).first()
    if user:
        token = user.create_confirm_token()
        s_confirm_email(user,token)
        return render_template('auth/send_confirm_email.html', title='Confirm', email_data=email_data)
    else:
        flash('email is not existed')
        form = RegistrationForm()
        return render_template('auth/register.html', title='Register', form=form)

@bp.route('/user_confirm/<token>')
def user_confirm(token):
    user = User()
    data = user.validate_confirm_token(token)
    if data:
        user = User.query.filter_by(id=data.get('user_id')).first()
        user.confirm = True
        print('user: ',user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    else:
        return 'wrong token'

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=form.username.data).first()
        print('user',user)
        flash('Congratulations, you are now a registered user! Please click the confirm link in your email')
        return redirect(url_for('auth.send_confirm_email',email_data=form.email.data))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        elif not user.confirm:
            flash('please confirm email first')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc !='':# not have a next argument or is set to a full URL
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@bp.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@bp.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = OAuthSignIn.get_provider(provider)
    try:
        social_id, username, email,picture,friends= oauth.callback()
        print('/friends:',friends[0])
    except:
        print("except")
    # for element in friends:
    #     print('element:',element[0])
    # ff=int(element[0] or 0)
    # if friend :
    #     print("No friend here")
    # else:
    #     print(element[0])
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('main.index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id,username=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    # return redirect(url_for('main.index',friends=friends['data']))
    return redirect(url_for('main.index',friends=["www","sss"]))
