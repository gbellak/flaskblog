from flask import Blueprint
from flask_login import login_required
from flask import render_template, url_for, flash, redirect, current_app, session
from flaskblog.decorators import check_confirmed
from flaskblog.klarnakco.forms import KCOCheckoutForm
import requests, json


klarnakco = Blueprint('klarnakco', __name__)


checkout_order = {
 "purchase_country": "se",
 "purchase_currency": "sek",
 "locale": "en-GB",
 "billing_address": {
   "given_name": "Testperson-se",
   "family_name": "Approved",
   "email": "youremail@email.com",
   "street_address": "Stårgatan 1",
   "postal_code": "12345",
   "city": "Ankeborg",
   "phone": "+46765260000",
   "country": "se"
 },
 "order_amount": 503341,
 "order_tax_amount": 100668,
 "order_lines": [
   {
     "type": "physical",
     "reference": "19-402-SWE",
     "name": "Camera Travel Set",
     "quantity": 1,
     "quantity_unit": "pcs",
     "unit_price": 603341,
     "tax_rate": 2500,
     "total_amount": 503341,
     "total_discount_amount": 100000,
     "total_tax_amount": 100668,
     "image_url": "http://merchant.com/logo.png"
   }
 ],
 "merchant_urls": {
   "terms": "https://flaskblog.duckdns.org/klarnakco/terms",
   "checkout": "https://flaskblog.duckdns.org/klarnakco/checkout/{checkout.order.id}",
   "confirmation": "https://flaskblog.duckdns.org/klarnakco/confirmation/{checkout.order.id}",
   "push": "https://flaskblog.duckdns.org/klarnakco/push/{checkout.order.id}"
 },
 "shipping_options": [
   {
     "id": "free_shipping",
     "name": "Free Shipping",
     "description": "Delivers in 5-7 days",
     "price": 0,
     "tax_amount": 0,
     "tax_rate": 0,
     "preselected": True,
     "shipping_method": "Home"
   },
   {
     "id": "pick_up_store",
     "name": "Pick up at closest store",
     "price": 399,
     "tax_amount": 0,
     "tax_rate": 0,
     "preselected": False,
     "shipping_method": "PickUpStore"
   }
 ]
}



@klarnakco.route('/klarnakco/', methods=['GET', 'POST'])
@login_required
@check_confirmed
def checkout_initiate():
    form = KCOCheckoutForm()
    if form.validate_on_submit():
        flash('You will be redirected to KCO checkout', 'success')
        try:
            response = requests.post(current_app.config['KLARNA_API_URL']+'/checkout/v3/orders', 
                auth=(current_app.config['KLARNA_API_USER'], current_app.config['KLARNA_API_PASSWORD']), json=checkout_order)
            json_data = json.loads(response.text)
            session['kco_order_id'] = json_data['order_id']
            return render_template('kco_checkout2.html', title='KlarnaKCO', snippet=json_data['html_snippet'])

        except Exception as e:
            flash('Could not connect to payment portal \n '+ str(e), 'danger')

    return render_template('kco_checkout.html', title='KlarnaPay', form=form, legend='Payment with Klarna')


@klarnakco.route('/klarnakco/terms')
def terms():
    return render_template('kco_terms.html', title='KlarnaCheckout- Terms', legend='Payment T&C with Klarna Checkout')


@klarnakco.route('/klarnakco/checkout/<order_id>')
@login_required
@check_confirmed
def checkout(order_id):
    checkout_order['merchant_urls']['terms'] = url_for('klarnakco.checkout', order_id = order_id)
    return render_template('kco_checkout.html', title='KlarnaCheckout', legend='Main Klarna Checkout Page', order=order_id)

@klarnakco.route('/klarnakco/confirmation/<order_id>')
@login_required
@check_confirmed
def thankyou(order_id):
    if order_id == session['kco_order_id']:
        try:
            response = requests.get(KLARNA_API_URL+'/checkout/v3/orders/'+ order_id, auth=(KLARNA_API_USER,KLARNA_API_PASSWORD))
            json_data = json.loads(response.text)
            return render_template('kco_thankyou.html', title='KlarnaKCO Confirm', snippet=json_data['html_snippet'])


        except Exception as e:
            flash('Could not conclude payment  '+ str(e), 'danger')
    return render_template('kco_thankyou.html', title='KlarnaCheckout- Terms', legend='Thank you for your purchase with Klarna Checkout', order=order_id)

@klarnakco.route('/klarnakco/push/<order_id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def push(order_id):
    return render_template('kco_push.html', title='KlarnaCheckout- Terms', legend='Order Confirmation', order=order_id)