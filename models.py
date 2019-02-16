from flask import current_app, url_for
from flaskblog import db, login_manager, ma
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import json
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


class Locale(db.Model):
    __tablename__ = "locale"
    id = db.Column(db.Integer, primary_key=True)
    purchase_country = db.Column(db.String(8), nullable = False )
    purchase_currency = db.Column(db.String(8), nullable = False)
    locale = db.Column(db.String(8), nullable = False, unique=True)
    slug =  db.Column(db.String(8), nullable = False, unique=True)

    def get_JSON(self):
        return {'purchase_country':self.purchase_country, 'purchase_currency':self.purchase_currency, 'locale':self.locale}

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tags = (db.String(160))
    sellable_units = db.relationship('ProductSellableUnit', backref='Product', lazy=True)
    
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    
    tax_rate = db.Column(db.Integer, nullable=False, default = 25)
    base_unit_price = db.Column(db.Integer, nullable=False)
    base_discount = db.Column(db.Integer, nullable=False, default = 0)

    @property
    def product_url(self):
        return current_app.config['ROOT_DOMAIN_URL']+ url_for('webshop.product_page', product_id = self.product_id)

class ProductIdentifiers(db.Model):
    __tablename__ = "product_identifiers"
    id = db.Column(db.Integer, primary_key=True)
    product_sellable_id = db.Column(db.Integer, db.ForeignKey('product_sellable_unit.id'), nullable=False)
    category_path = db.Column(db.String(80))
    global_trade_item_number = db.Column(db.String(80))
    manufacturer_part_number = db.Column(db.String(80))
    brand = db.Column(db.String(80))

class ProductType(db.Model):
    __tablename__ = "product_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20) , nullable=False, unique = True)
    

class ProductSellableUnit(db.Model):
    __tablename__ = "product_sellable_unit"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_identifiers = db.relationship('ProductIdentifiers', backref='product', lazy=True, uselist=False) #only one allowed)
    
    product_type_id = db.Column(db.Integer, db.ForeignKey('product_type.id'), nullable=True, default = 1) #default is set to 'physical'
    
    cart_lines_using = db.relationship('CartLineItem', backref='ProductSellableUnit', lazy=True)
    shipping_attributes_id = db.Column(db.Integer, db.ForeignKey('shipping_attributes.id'), nullable=True)

    reference = db.Column(db.String(80)) #Article number, SKU or similar.
    quantity_unit = db.Column(db.String(8), default="pcs")
    delta_unit_price = db.Column(db.Integer, nullable=False, default = 0)
    delta_discount = db.Column(db.Integer, nullable=False, default = 0)
    
    merchant_data = db.Column(db.String(255))#Pass through field. (max 255 characters)

    @property
    def is_available(self):
        return True  #Not yet implemented, placeholder

    @property
    def type(self):
        return ProductType.query.get(self.product_type_id).name

    @property
    def unit_price(self):
        return self.Product.base_unit_price + self.delta_unit_price

    @property
    def unit_discount(self):
        return self.Product.base_discount + self.delta_discount

    @property
    def special_price(self):
        if self.unit_discount > 0:
            return (1-(self.unit_discount/100)) * self.unit_price  #percentage
        else:
            return None


    
class ShippingAttributes(db.Model):
    __tablename__ = "shipping_attributes"
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Integer, nullable=False, default = 1000)
    dimensions_id = db.Column(db.Integer, db.ForeignKey('shipping_dimensions.id'), nullable=False)

class ShippingDimensions(db.Model):
    __tablename__ = "shipping_dimensions"
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Integer, nullable=False, default= 200)
    width = db.Column(db.Integer, nullable=False, default= 200)
    length = db.Column(db.Integer, nullable=False, default= 200)


class KlarnaOrderStatus(db.Model):
    __tablename__ = "klarna_order_status"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), default = 'preliminary')
    orders = db.relationship('KlarnaOrder', backref='Status', lazy=True)



class KlarnaOrder(db.Model):
    __tablename__ = "klarna_order"
    id = db.Column(db.Integer, primary_key=True)
    locale_id = db.Column(db.Integer, db.ForeignKey('locale.id'))
    status = db.Column(db.Integer, db.ForeignKey('klarna_order_status.id'), nullable=False, default = 1)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
     # #  owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default = None)
    JSON = db.Column(db.Text)

    def __init__(self, dictionary = {}, status = 1, **kw):
        self.status = status
        dictionary['status'] = self.get_status()
        self.JSON = json.dumps(dictionary)

    def set_JSON(self, dictionary):
        js = json.loads(self.JSON)
        self.JSON = json.dumps({**js, **dictionary})
        self.updated = datetime.utcnow

    
    def get_JSON(self):
        return json.loads(self.JSON)

    def get_status(self):
        return KlarnaOrderStatus.query.get(self.status).name
        

class CartLineItem(db.Model):
    __tablename__ = "cart_line"
    id = db.Column(db.Integer, primary_key=True)
    product_sellable_unit_id = db.Column(db.Integer, db.ForeignKey('product_sellable_unit.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    quantity = db.Column(db.Integer, nullable=False, default = 1)

    cart_line_discount =  db.Column(db.Integer, nullable=False, default = 0)


    @property
    def unit_price(self):
        return self.ProductSellableUnit.unit_price

    @property
    def final_price(self):
        pass
        
 #               "discount": product.base_discount + product_sellable_unit.delta_discount,

    

class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    is_closed = db.Column(db.Boolean, nullable=False, default=False) # Historic Carts are checked out
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default = None)
    cart_line_items = db.relationship('CartLineItem', backref='cart', lazy=True)
    klarna_order_id = db.Column(db.Integer, db.ForeignKey('klarna_order.id'), nullable=True, default = None)
    discount_offer = db.Column(db.Integer, db.ForeignKey('discount_offer.id'), nullable=True, default = None)


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



class DiscountOffer(db.Model):
    __tablename__ = "discount_offer"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120))
    code =  db.Column(db.String(32), nullable=False, unique=True)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_to = db.Column(db.DateTime, default= None)
    
    valid_regular_price_only =  db.Column(db.Boolean, nullable=False, default=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default = None)
    valid_for_minimum_spend = db.Column(db.Integer, nullable=True)
    
    usage_count =  db.Column(db.Integer)
    usage_limit = db.Column(db.Integer, nullable=True)


    discount = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.usage_count = 0

    def increment_usecount(self):
        self.usage_count +=1



