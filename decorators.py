from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            flash('Please login to access page', 'info')
            return redirect(url_for('main.home'))
        elif current_user.confirmed is False:
            flash('Please validate your account!', 'danger')
            return redirect(url_for('users.account'))
        else:
            return func(*args, **kwargs)
    return decorated_function


def check_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            flash('Please login to access page', 'info')
            return redirect(url_for('main.home'))
        elif current_user.is_admin is False:
            flash('Administrators only!', 'danger')
            return redirect(url_for('main.home'))
        else:
            return func(*args, **kwargs)
    return decorated_function
