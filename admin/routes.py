# Admin routes
from flask import Blueprint
from flaskblog import db
from flaskblog.models import Post
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from flaskblog.decorators import check_admin


admin = Blueprint('admin', __name__)

@admin.route('/admin/', methods=['GET', 'POST'])
@login_required
@check_admin
def home():
    return render_template('admin_home.html', title='Administration')



@admin.route('/admin/users', methods=['GET', 'POST'])
@login_required
@check_admin
def manage_users():
    return "Admin only!!!!"