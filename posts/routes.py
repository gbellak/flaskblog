from flask import Blueprint
from flaskblog import db
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from flaskblog.decorators import check_confirmed


posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
@check_confirmed
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been saved', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='Write a post')


@posts.route('/post/<int:post_id>')
@check_confirmed
def post(post_id):
    post = Post.query.get_or_404(post_id)
    


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
@check_confirmed

def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('posts.post', post_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update your post')


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
@check_confirmed
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'warning')
    return redirect(url_for('main.home'))
