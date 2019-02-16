from flask import Flask, Blueprint, jsonify, request, render_template
from flask_restful import reqparse, abort, Api, Resource
from flaskblog import db, api
from flaskblog.models import Product, Cart, CartLineItem, ProductSellableUnit



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
        cartline = get_or_abort_if_doesnt_exist(CartLineItem, id)
        if cartline.cart_id != cart_id:
            abort(404, message=cart_id +"Line {} doesn't belong to Cart {}".format(cartline.cart_id, cart_id))

        product_sellable_unit = get_or_abort_if_doesnt_exist(ProductSellableUnit, cartline.product_sellable_unit_id)
        product = get_or_abort_if_doesnt_exist(Product, product_sellable_unit.product_id)
        reply = {"id":cartline.id,
                "product_id": product.id,   # Should have product identifier??? / Refactor Product first!
                "product_name": product.name,
                "reference": product_sellable_unit.reference,
                "quantity": cartline.quantity,
                "quantity_unit":  product_sellable_unit.quantity_unit,

                "tax_rate": product.tax_rate,
                "unit_price": product.base_unit_price + product_sellable_unit.delta_unit_price,
                "discount": max(product.base_discount + product_sellable_unit.delta_discount, cartline.cart_line_discount),
                
            }
        return reply

    def delete (self, locale_slug, cart_id, id):
        cartline = CartLineItem.query.get_or_404(id)      
        db.session.delete(cartline)
        db.session.commit()





