
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow

from flask.json import JSONEncoder
import calendar
from datetime import datetime



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
api = Api()
ma = Marshmallow()

from flaskblog.rest.resources import ShoppingCart, ShoppingCartLine
api.add_resource(ShoppingCart, '/api/shopping_cart/<string:locale>/<int:id>')
api.add_resource(ShoppingCartLine, '/api/shopping_cart/<locale>/<int:cart_id>/<int:id>')




def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    api.init_app(app)
    ma.init_app(app)

    
    from flaskblog.users.routes import users
    from flaskblog.webshop.routes import webshop
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    from flaskblog.admin.routes import admin
    from flaskblog.klarnapay.routes import klarnapay
    from flaskblog.klarnakco.routes import klarnakco

    app.register_blueprint(users)
    app.register_blueprint(webshop, url_prefix='/webshop')
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(admin)
    app.register_blueprint(klarnapay)
    app.register_blueprint(klarnakco)

    return app