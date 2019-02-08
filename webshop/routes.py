from flask import Blueprint, session
from flaskblog.models import Product, Cart, CartLineItem
from flask import render_template, request, session
from flask_login import current_user
import uuid
from flaskblog import db
from flaskblog.webshop.forms import Product2CartForm
from flaskblog.webshop.utils import add2cart

webshop = Blueprint('webshop', __name__)


@webshop.route('/')
@webshop.route('/home')
def webshop_home():
    if 'cart_id' in session:
        cart_id = session['cart_id']
    else:
        cart_id= "no active cart"

    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.unit_price.asc()).paginate(page=page, per_page=5)
    return render_template('webshop_home.html', products=products, cart_id= cart_id)


@webshop.route('/product/<int:product_id>', methods=['GET','POST'])
def product_page(product_id):
    form = Product2CartForm()
    product = Product.query.get_or_404(product_id)
    if form.validate_on_submit():
        add2cart(product_id = product_id, quantity = form.quantity.data)

    return render_template('webshop_product.html', title='Product', product=product, form = form)
