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


@admin.route('/admin/posts/')
@login_required
@check_admin
def admin_posts():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('admin_posts_list.html', title='Administration', posts=posts)


@admin.route('/admin/posts/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@check_admin
def admin_edit_post():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('admin_posts_list.html', title='Administration', posts=posts)


@admin.route('/admin/users/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@check_admin
def admin_users():
    return "Admin only!!!!"