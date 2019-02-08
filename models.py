from flask import current_app, url_for
from flaskblog import db, login_manager, ma
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from sqlalchemy_utils import aggregated
from sqlalchemy.orm.collections import attribute_mapped_collection

from marshmallow import Schema, fields, pre_load, validate

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)

    def __repr__(self):
        name = self.username
        email = self.email
        image = self.image_file
        return "User('{}', '{}', '{}')".format(name, email, image)


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        title = self.title
        date_posted = self.date_posted
        return "Post('{}', '{}')".format(title,date_posted)


class CountrySettings(db.Model):
    __tablename__ = "country_settings"
    id = db.Column(db.Integer, primary_key=True)
    purchase_country = db.Column(db.String(8), nullable = False, default="se")
    purchase_currency = db.Column(db.String(8), nullable = False, default="sek")
    locale = db.Column(db.String(8), nullable = False, default="sv-se")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity_unit = db.Column(db.String(8), default="pcs")
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    unit_price = db.Column(db.Integer, nullable=False)
    tax_rate = db.Column(db.Integer, nullable=False, default = 25)
    order_lines_using = db.relationship('OrderLine', backref='Product', lazy=True)
    cart_lines_using = db.relationship('CartLineItem', backref='Product', lazy=True)

    @property
    def is_available(self):
        return True  #Not yet implemented, placeholder

    @property
    def product_url(self):
        return current_app.config['ROOT_DOMAIN_URL']+ url_for('webshop.product_page', product_id = self.product_id)


class OrderLine(db.Model):
    __tablename__ = "order_line"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    quantity = db.Column(db.Integer, nullable=False)
    total_discount_amount = db.Column(db.Integer, default = 0)

    @property
    def total_amount(self):
        return (self.quantity * self.Product.unit_price)-self.total_discount_amount


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    order_lines= db.relationship('OrderLine', backref='Order', lazy=True)
    country_setting_id = db.Column(db.Integer, db.ForeignKey('country_settings.id'))
    
 #   def total_amount(self):
#        return db.func.sum(Product.unit_price)
    
 #   total = db.Column(db.Integer)
 #   total_amount
 #   total_tax_amount 


class CartLineAsDict(db.Model):
    __tablename__ = "cart_line_as_dict"
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False, default = 1)





class CartLineItem(db.Model):
    __tablename__ = "cart_line"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    quantity = db.Column(db.Integer, nullable=False, default = 1)
    

class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    is_closed = db.Column(db.Boolean, nullable=False, default=False) # Historic Carts are checked out
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    cart_owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default = None)
    cart_line_items = db.relationship('CartLineItem', backref='cart', lazy=True)


    @property
    def total_amount(self):
        total=0
        for cl in self.cart_line_items:
            total += cl.total_amount
        return total

    @property
    def total_tax(self):
        total=0
        for cl in self.cart_line_items:
            total += cl.total_tax_amount
        return total






