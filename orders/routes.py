from flask import Blueprint, current_app, session, jsonify
import simplejson as json
from flaskblog import db, bcrypt
from flaskblog.models import User, Locale, KlarnaOrder, Cart, CartLineItem, ProductSellableUnit, ProductType, Product, DiscountOffer
import jsonpickle
from flask import render_template, url_for, flash, redirect, request

from flaskblog.webshop.forms import ApplyDiscountForm

orders = Blueprint('orders', __name__)


@orders.route('/home')
@orders.route('/')
def home():
    return 'hello'


@orders.route('/checkout/<string:locale_slug>/<int:cart_id>', methods=['GET', 'POST'])
def cart_checkout(locale_slug, cart_id):
    form = ApplyDiscountForm()
    cart = Cart.query.get_or_404(cart_id)
    locale = Locale.query.filter_by(slug = locale_slug).first_or_404()
    
    if form.validate_on_submit():
        #validate discount offer in form validation first
        try:
            discountOffer = DiscountOffer.query.filter_by(code = form.discount_code.data).first()
            cart.discount_offer = discountOffer.id
            flash('discountOffer' + str(discountOffer.discount) +' %', category="success")
        except:
            discountOffer = None 
            cart.discount_offer = None
        
        db.session.add(cart)
        
    
        for cartline in cart.cart_line_items:
            if discountOffer == None:
                cartline.cart_line_discount = 0
                continue

            if discountOffer.valid_regular_price_only and cartline.ProductSellableUnit.special_price:
                continue
            else:
                cartline.cart_line_discount = discountOffer.discount
                db.session.add(cartline)
        
        db.session.commit()
        redirect(url_for('orders.cart_checkout',locale_slug = locale_slug, cart_id=cart_id )) #refresh to ensure all changes applied to cart

        
    
    elif request.method == 'GET':
        if cart.discount_offer:
            discountOffer = DiscountOffer.query.get(cart.discount_offer)
            form.discount_code.data = discountOffer.code
#NTZ Check if offer still applicable- if so reapply to cart

    


    return render_template('webshop_checkout.html', title='Checkout', form = form, cartlines = cart.cart_line_items, cart = cart)





@orders.route('/create_order/<string:locale_slug>/<int:cart_id>')
def order_checkout(locale_slug, cart_id):
    cart = Cart.query.get_or_404(cart_id)
    locale = Locale.query.filter_by(slug = locale_slug).first_or_404()
    
    if cart.klarna_order_id:
        order = KlarnaOrder.query.get_or_404(cart.klarna_order_id)
        print('found order id :' + str(order.id))
        order.locale_id = locale.id  #overwrites locale to be sure!
    else:
        order = KlarnaOrder(locale_id=locale.id) # status CHECKOUT_INCOMPLETE = 1
        db.session.add(order)
        db.session.commit()
        print('created klarna_order id :' + str(order.id))
        cart.klarna_order_id = order.id
        db.session.add(cart)
        db.session.commit()

    localeJSON = locale.get_JSON()
    order.set_JSON(localeJSON)  #add locale to order json
    
    order_lines = []
    cart_discount = cart.cart_discount

    for cart_line in cart.cart_line_items:
        product_sellable_unit = ProductSellableUnit.query.get_or_404(cart_line.product_sellable_unit_id)
        product = Product.query.get_or_404(product_sellable_unit.product_id)
        
        unit_price = product.base_unit_price + product_sellable_unit.delta_unit_price
        unit_discount = product.base_discount + product_sellable_unit.delta_discount
        total_amount = 0

        
        order_line = {
            "type": product_sellable_unit.type,
            "name": product.name,
            "reference": product_sellable_unit.reference,
            "quantity": cart_line.quantity,
            "quantity_unit":  product_sellable_unit.quantity_unit,
            "tax_rate": product.tax_rate * 100,  #KLarna uses 100x values (minor units)
            "unit_price": unit_price * 100,   #KLarna uses 100x values (minor units)
            "total_amount": (unit_price - unit_discount) * cart_line.quantity *100 , #KLarna uses 100x values (minor units)
            "total_discount_amount": unit_discount * cart_line.quantity *unit_price, #KLarna uses 100x values (minor units)
            "total_tax_amount": 0,
            "merchant_data":"",
            "product_url":"",
            "image_url":"",
            "tags": product.tags   #array of strings



        }


    js = order.get_JSON()

    return json.dumps(js)

