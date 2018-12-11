from flaskblog import mail
from flask import url_for, current_app
from flask_login import current_user
import secrets
import os
from PIL import Image
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(current_app.root_path,
                                'static/profile_pics', picture_fn)

    output_size = (125, 125)
    image = Image.open(form_picture)
    image.convert('RGB')
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_fn


def remove_picture(current_picture):
    if current_picture != 'default.jpg':
        current_picture_path = os.path.join(current_app.root_path,
                                            'static/profile_pics',
                                            current_picture)
        os.remove(current_picture_path)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='gbcode62@gmail.com', recipients=[user.email])
    reset_url= url_for('users.reset_pw', token=token, _external = True)
    msg.body = '''To reset your password, visit the following link:
{}

If you did not request the password reset, then simply ignor this email.

'''.format(reset_url)
    mail.send(msg)

def send_email_confirmation(user=current_user):
    token = generate_email_confirmation_token(user.email)
    msg = Message('Email Confirmation Needed',
                  sender='gbcode62@gmail.com', recipients=[user.email])
    url = url_for('users.confirm_email', token=token, _external = True)
    msg.body = '''To confirm your email and activate your new account on Flask Blog, please visit the following link:
{}

If you did not sign up with Flask Blog, then simply ignor this email.

'''.format(url)
    mail.send(msg)


def generate_email_confirmation_token(email):
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    return serializer.dumps(email, salt=os.environ.get('SECURITY_PASSWORD_SALT'))

def confirm_email_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    try:
        email = serializer.loads(
            token,
            salt=os.environ.get('SECURITY_PASSWORD_SALT'),
            max_age=expiration
        )
    except:
        return False
    return email
