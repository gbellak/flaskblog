from flask import Blueprint
from flaskblog.models import Post
from flask import render_template, request

from flaskblog.users.forms  import RegistrationForm


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@main.route('/about')
def about():
	form = RegistrationForm()
	return render_template('about.html', title='About', form = form)