from flask import Blueprint
from flask_login import login_required
from flask import render_template, url_for, flash, redirect, current_app, session
from flaskblog.decorators import check_confirmed
from flaskblog.klarnapay.forms import CheckoutForm
import requests, json



klarnapay = Blueprint('klarnapay', __name__)

payload = {
    "purchase_country": "SE",
    "purchase_currency": "SEK",
    "locale": "sv-se",
    "order_amount": 10,
    "order_tax_amount": 0,
    "order_lines": [{
        "type": "physical",
        "reference": "19-402",
        "name": "Battery Power Pack",
        "quantity": 1,
        "unit_price": 10,
        "tax_rate": 0,
        "total_amount": 10,
        "total_discount_amount": 0,
        "total_tax_amount": 0
    }]
}




@klarnapay.route('/klarnapay/checkout', methods=['GET', 'POST'])
@login_required
@check_confirmed
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        flash('You will be redirected to payments', 'success')
        try:
            response = requests.post(current_app.config['KLARNA_API_URL'], 
                auth=(current_app.config['KLARNA_API_USER']+'/payments/v1/sessions', current_app.config['KLARNA_API_PASSWORD']), json=payload)
            json_data = json.loads(response.text)
            flash(json_data,'warning')
            session['klarna_session'] = json_data['session_id']
            session['klarna_token'] = json_data['client_token']
            return redirect(url_for('klarnapay.payment'))
        except Exception as e:
            flash('Could not connect to payment portal \n '+ str(e), 'danger')

    return render_template('checkout.html', title='KlarnaPay', form=form, legend='Payment with Klarna', purchase = str(payload))

@klarnapay.route('/klarnapay/payment')
@check_confirmed
def payment():
#   session_id, client_token
    flash('Managed to establish connection to payments', 'success')
    return render_template('klarnapayment.html', title='KlarnaPay', legend='Payment with Klarna')
