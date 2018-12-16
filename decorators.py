from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            return func(*args, **kwargs)
        elif current_user.confirmed is False:
            flash('Please validate your account!', 'danger')
            return redirect(url_for('users.account'))
    return decorated_function
