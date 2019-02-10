from flask import Flask, Blueprint, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from flaskblog import db, api
from flaskblog.models import Product, Cart, CartLineItem



def get_or_abort_if_doesnt_exist(model, id):
    result = model.query.get(id)
    if result == None:
        abort(404, message="{} {} doesn't exist".format(model, id))

    return result



class ShoppingCart(Resource):
    def get(self, locale_slug, id):
        cart = get_or_abort_if_doesnt_exist( Cart, id)
        reply = []
        for cl in cart.cart_line_items:
                 reply.append(ShoppingCartLine.get(cl, locale_slug = locale_slug, cart_id=id, id = cl.id))
        
        return reply

    def put(self, locale_slug, id):
        json_data= request.get_json(force=True)
        for line in json_data:
            cartline = get_or_abort_if_doesnt_exist( CartLineItem, id=line['id'])
            cartline.quantity=line['quantity']
            db.session.add(cartline)

            print('id: '+str(line['id'])+ '  quantity : '+ str(line['quantity']))
        db.session.commit()

        

        

class ShoppingCartLine(Resource):
    def get(self, locale_slug, cart_id, id):
        cart_line = get_or_abort_if_doesnt_exist(CartLineItem, id)
        if cart_line.cart_id != cart_id:
            abort(404, message=cart_id +"Line {} doesn't belong to Cart {}".format(cart_line.cart_id, cart_id))

        product = get_or_abort_if_doesnt_exist(Product, cart_line.product_id)
        reply = {"id":cart_line.id,
                 "product_id": product.id,   # Should have product identifier??? / Refactor Product first!
                 "product_name": product.name,
                "quantity": cart_line.quantity,
                "quantity_unit":  product.quantity_unit,
                "unit_price": product.unit_price,
                
        }
        return reply

    def delete (self, locale_slug, cart_id, id):
        cartline = CartLineItem.query.get_or_404(id)      
        db.session.delete(cartline)
        db.session.commit()





