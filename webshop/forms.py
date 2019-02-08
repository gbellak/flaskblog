from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms_components import IntegerField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed

class Product2CartForm(FlaskForm):
    quantity = IntegerField('Quantity', default = 1, validators=[InputRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Cart')


class ProducRegisterForm(FlaskForm):
    name = StringField('Product Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    quantity_unit = StringField('Quantity Units',
                        validators=[DataRequired(), Length(min=1, max=8)])
    image_file = FileField('Update Profile Picture',
                        validators=[FileAllowed(['jpg', 'png'])])
    unit_price = IntegerField('Unit Price', default = 1,validators=[InputRequired()])
    tax_rate = IntegerField('Tax Rate', default = 1,validators=[InputRequired()])
    submit = SubmitField('Register Product')

