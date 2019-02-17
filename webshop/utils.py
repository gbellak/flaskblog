import os
from PIL import Image
from os import urandom
from flask import session, flash
import uuid
from flaskblog import db
from flaskblog.models import Product, Cart, CartLineItem, Locale
from flask_login import current_user

def save_picture(product_picture):
    random_hex = urandom(8).hex()
    _, file_ext = os.path.splitext(product_picture.filename)
    picture_prod = random_hex+file_ext
    picture_path = os.path.join(current_app.root_path,
                                'static/product_pics', picture_prod)

    output_size = (125, 125)
    image = Image.open(product_picture)
    image.convert('RGB')
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_fn


def get_active_cart():
#return active cart from session- or store a new one in db
    pop_or_takeover_not_owned_active_cart()

    if 'cart_id' in session:
        cart = Cart.query.get(session['cart_id'])
        if cart == None:
            cart= create_new_cart()

    elif current_user.is_authenticated: #retrieve if user known and has a stored or abandonned cart 
        cart = Cart.query.filter_by(owner = current_user.id, is_closed = False).order_by(Cart.timestamp.desc()).first() 
                #try to retreive latest non closed cart owned by user
        if cart:
            session['cart_id'] = cart.id

        else:
            cart = create_new_cart()


    else: #create new cart and cart id
        cart= create_new_cart()
    
    return cart

def add2cart(product_sellable_unit_id, quantity):
    cart = get_active_cart() #will return a new or existing (possibly saved) cart, stored in session
    #check if same product allready in cart, if so increment quantity
    cart_line_item = CartLineItem.query.filter_by(cart_id = cart.id, product_sellable_unit_id = product_sellable_unit_id).first()
    if cart_line_item:
        cart_line_item.quantity += quantity
    else:
        cart_line_item = CartLineItem(cart_id = cart.id, product_sellable_unit_id = product_sellable_unit_id, quantity = quantity)
    
    db.session.add(cart_line_item)
    db.session.commit()
  
    flash('Your product has been added to cart', 'success')

def create_new_cart():
    if current_user.is_authenticated:
        owner_id = current_user.id
    else:
        owner_id = None

    cart = Cart(owner = owner_id)
    
    db.session.add(cart)
    db.session.commit()

    session['cart_id'] = cart.id



    flash('New Cart created: '+str(cart.id) + 'for user: '+ str(owner_id), 'success')
    flash('Current user id is: '+str(owner_id), 'success')
    return cart

def pop_or_takeover_not_owned_active_cart():
    #If active cart owned by other user than current user
    if 'cart_id' in session:
        cart = Cart.query.get(session['cart_id'])

        if current_user.is_authenticated:
            if cart.owner == None:
                cart.owner = current_user.id
                db.session.add(cart)
                db.session.commit()
                flash("cart: "+str(cart.id) + "  take over", 'warning')

            elif cart.owner != current_user.id:
                session.pop('cart_id', None) #pop someone elses cart
                cart_id = None

            else:
                pass

        else:
            if cart.owner != None:
                session.pop('cart_id', None) #pop someone elses cart
                cart_id = None


def merge_saved_to_active_cart():
    if current_user.is_authenticated == False:
        return
           
    old_cart = Cart.query.filter_by(owner = current_user.id, is_closed = False).order_by(Cart.timestamp.desc()).first() 
                #try to retreive latest non checked out cart owned by user

    pop_or_takeover_not_owned_active_cart()


    if old_cart == None:
        flash('No saved cart for user: '+ str(current_user.id), 'success')
        return #return if no old cart found
                
    if 'cart_id' in session:     
        # if user has an anonymous cart at login- and has a owned  open cart, they will be merged
        if session['cart_id']  == old_cart.id:
            return #no further action needed
        
        old_cart_line_items = CartLineItem.query.filter_by(cart_id = old_cart.id).all()
        if old_cart_line_items == None:
            old_cart.is_closed = True #just close if no line items 

        else: 
            for line_item in old_cart_line_items:
                add2cart(line_item.product_sellable_unit_id, line_item.quantity)

            old_cart.is_closed = True

        db.session.add(old_cart)
        db.session.commit()
        flash('Merged Cart: '+str(old_cart.id) + ' with active: '+str(session['cart_id']), 'success')
    else:
        session['cart_id'] = old_cart.id

    return

def save_active_cart2user():
    if ('cart_id' in session) and (current_user.is_authenticated):
        cart = Cart.query.get(session['cart_id'])
        
        if cart:
            cart.owner = current_user.id
            db.session.add(cart)
            db.session.commit()
            session.pop('cart_id', None)




    
