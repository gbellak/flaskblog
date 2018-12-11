from flask import Blueprint, current_app
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm, AccountUpdateForm, RequestResetPasswordForm,  ResetPasswordForm, Request_email_token
from flaskblog.users.utils import save_picture, remove_picture, send_reset_email, generate_email_confirmation_token, confirm_email_token, send_email_confirmation
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw, confirmed=False
                    )
        db.session.add(user)
        db.session.commit()

        token = generate_email_confirmation_token(form.email.data)
        username = form.username.data
        flash('Account created for {}! An email has been sent with instructions howto activate your account'.format(username), 'success')
        return redirect(url_for('main.home'))
    return render_template('register.html', title='Register', form=form)


@users.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    try:
        email = confirm_email_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    #flash message removed    
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed.', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.commit()
        flash('You have confirmed your email account. Thanks!', 'success')
    return redirect(url_for('main.home'))

@users.route('/send_confirmation_mail/<string:username>')
def send_confirmation_mail(username):
    user = User.query.filter_by(username=username).first_or_404()
    send_email_confirmation(user)
    flash('Account validation mail sent.', 'info')
    return redirect(url_for('main.home'))


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.home'))
        else:
            flash('Login failed! Please check your email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountUpdateForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            remove_picture(current_user.image_file)
            current_user.image_file = picture_file
        if current_user.email != form.email.data:
            current_user.confirmed = False
            current_user.confirmed_on = None
            flash('Email was changed! Please revalidate your account!', 'danger')
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_pw_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions howto reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('request_pw_reset.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_pw(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token is invalid or expired', 'warning')
        return redirect(url_for('users.reset_pw_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been successfully reset', 'success')
        return redirect(url_for('users.login'))
    return render_template('pw_reset.html', title='Reset Password', form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)
