from flaskblog import mail
from flask import url_for, current_app
from flask_login import current_user
from flaskblog.models import User, Post




def new_order_from_cart(locale, cart):
    pass












class kcoOrderJSON(object):
    
    def __init__(self, dictionary):
        self.orderJSON = dictionary

    def merge(self, dictionary):
        self.orderJSON = {**self.orderJSON, **dictionary}

    def getJSON(self):
        return self.orderJSON







