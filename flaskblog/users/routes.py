from datetime import timezone
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import render_template, url_for, flash, redirect, request, Blueprint,current_app
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm,DeleteAccountForm)
from flaskblog.users.utils import save_picture, send_reset_email,send_email_verification
from os.path import join
from os import remove
from secrets import token_hex

users = Blueprint('users',__name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        register.verification_code = token_hex(16)
        register.form = form
        send_email_verification(form.email.data,register.verification_code)
        flash("A verification link has been sent to your email. Verify to login", 'success')
        return redirect(url_for('main.home'))
    return render_template('register.html', title='Register', form=form)

@users.route('/emailverification/<token>',methods=['GET','POST'])
def email_verification(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        user_code = s.loads(token)['user_code']
    except:
        user_code = ""
    if user_code == register.verification_code:
        hashed_pw = bcrypt.generate_password_hash(register.form.password.data).decode('utf-8')
        user = User(username=register.form.username.data,email=register.form.email.data,password = hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("You account has been verified. You may now login", 'success')
        return redirect(url_for('users.login'))
    else:
        flash("Invalid/Expired token. Please try again", 'danger')
        return redirect(url_for('users.register'))

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check Email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route('/logout')
def logout():  
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    delform = DeleteAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            old_name = current_user.image_file 
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            if old_name != 'default.jpg':
                remove(join(current_app.root_path,'static/profile_pics',old_name))
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your Account Has Been Updated",'success')
        return redirect(url_for('users.account')) # we add this here else browser will say confirm reload 
        # your data will be lost. so in this way first we get and then post
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html',title ='Account',image_file=image_file,form = form,delform = delform)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user =User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())\
        .paginate(page = page ,per_page=5)
    return render_template('user_post.html', posts=posts,timezone=timezone,user=user)

@users.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password','info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', title='Reset Password',form = form)

@users.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash('The token is invalid/expired','warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash("Your password has been updated! You can now log in", 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password',form = form)

@users.route('/deleteaccount', methods=['GET', 'POST'])
@login_required
def delete_account(user_id):
    pass