from flask import Blueprint, current_app, session, jsonify
import simplejson as json
from flaskblog import db, bcrypt
from flaskblog.models import User, Locale, Order, OrderLine, Cart
import jsonpickle

orders = Blueprint('orders', __name__)


@orders.route('/home')
@orders.route('/')
def home():
	return 'hello Orders!'

@orders.route('/checkout/<string:locale_slug>/<int:cart_id>')
def order_checkout(locale_slug, cart_id):
	order = new_order_from_cart(locale_slug, cart_id) #initiate new order on each checkout request
	return jsonpickle.encode(order)


def new_order_from_cart(locale_slug, cart_id):
	locale = Locale.query.filter_by(slug = locale_slug).first_or_404()
	order = Order(locale_id=locale.id)
	cart = Cart.query.get_or_404(cart_id)
	for line in cart.cart_line_items:
		orderline = OrderLine(order_id = order.id, product_id= line.product_id, quantity=line.quantity)
	db.session.add(order)
	db.session.commit()

	return order