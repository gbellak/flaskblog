(function($) {

	// Add the view options functionality to all our views.
//	Backbone.ViewOptions.add( Backbone.View.prototype );
	var DiscountOffer = Backbone.Model.extend ({
			url : '/api/shopping_cart/discount_offer/' + myCart.toString(),

			defaults: function(){	
				return {
						discountCode:"",
						description:"",
		                discount: 0,
		                valid_regular_price_only: true,
		                }
					},

	});

	var CartDiscountView = Backbone.View.extend({

					

					el: $('#cart-discount-container'),

					events: {
        						'click .cart-discount': 'cartDiscountUpdate',
        					},

					initialize: function() {
						this.template = _.template($('#CartDiscount-template').html());
						this.model.on('change', this.render, this);
					},

					render: function(){
						this.$el.html(this.template(this.model.toJSON()) );
        				return this;
					},


					cartDiscountUpdate: function(){
						this.model.set({discountCode: $('#discount-input-field').val()});
						this.model.save(null, {
							success: function(){
								console.log('success!!!');
								},

							error: function(){
								console.log('error !!!!!');
								this.model.set({discountCode: "x"});
								this.render();
							},
						});


					},


					   });

	var ShoppingCartLine = Backbone.Model.extend ({

			defaults: function(){	
				return {
						id:"",
		                product_name: "",
		                reference: "",
		                quantity: 0,
		                quantity_unit: "",
		                unit_price: "",
		                tax_rate : 25,
		                discount : 0,
						}
					},

			total_amount: function(){
				var total_amount = this.quantity * this.unit_price *(1-(this.discount /100));
				return total_amount
			},

			total_tax_amount: function(){
				var total_tax_amount = this.quantity * this.unit_price * (this.tax_rate/100);
				return total_tax_amount
			},

			total_discount: function(){
				var total_discount = this.quantity * this.unit_price * (this.discount/100);
				return total_discount
			},

			toJSON: function(){  //overriding toJSON of model
    				// get the standard json for the object
    				var json = Backbone.Model.prototype.toJSON.apply(this, arguments);

    				// get the calculated total_amount
    				json.total_amount = this.total_amount;

    				// get the calculated total_amount
    				json.total_tax_amount = this.total_tax_amount;

    				// get the calculated total_amount
    				json.total_discount = this.total_discount;

    				// send it all back
    				return json;
 					 },
			});

	var ShoppingCart = Backbone.Collection.extend({
			model:  ShoppingCartLine,

			initialize: function(models, options){
				this.url = '/api/shopping_cart/'+locale_slug+'/'+options.cart_id;
//				this.check_out_url = '/orders/checkout/'+options.locale_slug+'/'+options.cart_id;

				},

        });

	var CartView = Backbone.View.extend({
		

					el: $('#cart-lines-container'),
					initialize: function() {
						this.collection.on('remove', this.render, this);
						this.collection.on('change', this.render, this);
//						this.locale_slug = options.locale_slug;					

						
						

					},

					events: {
						'click .cart-save': 'cartSave',
						'click .cart-checkout': 'cartCheckout',
						
					},

					render: function() {
						this.$el.html('');
						this.collection.each(function(shoppingCartLine){
							var cartLineView = new CartLineView({model: shoppingCartLine, collection: this.collection});
							this.$el.append(cartLineView.render().el);

						}, this)

						this.$el.append('<hr><h5>Cart Total: ' + this.cartTotal() +'  kr  |  VAT Total: ' + this.cartTotal_Tax() + ' kr  |  Discount Total: ' + this.cartTotal_Discount()+'kr</h5>').html();

						this.$el.append('<hr><button type="button" class="btn btn-outline-info btn-sm cart-save"  id="cart-save-button" >SaveCart</button>   '+

										'<button type="button" class="btn btn-success btn-sm cart-checkout"  id="cart-checkout-button" >CheckoutCart</button>'
							);
						
						return this;
					},

					cartSave: function(){



						Backbone.sync('update', this.collection);
						
					},

					cartCheckout: function(){
						Backbone.sync('update', this.collection);
						console.log('cart: ' + myCart + '   locale:  '+ locale_slug);
						
						setTimeout(function() {window.location.href = '/orders/checkout/'+ locale_slug+'/'+myCart;}, 500);

					},

					cartTotal_Tax: function(){
						var cartTaxSum = 0;
						
						var cartDiscountSum = 0;

						$('.total_tax_amount').each(function(){
							cartTaxSum += parseFloat($(this).text());
						});
						
						return cartTaxSum;

					},

					cartTotal_Discount: function(){
						var cartDiscount = 0;
						$('.total_discount').each(function(){
							cartDiscount += parseFloat($(this).text());
						});
						
						return cartDiscount;

					},

					cartTotal: function(){
						var cartSum = 0;
						$('.total_amount').each(function(){
							cartSum += parseFloat($(this).text());
						});
						
						return cartSum;

					},

				});

	var CartLineView = Backbone.View.extend({
					tagName: 'div',
					events: {
						'click .increase_quantity': 'increase_quantity',
						'click .decrease_quantity': 'decrease_quantity',
						'click .remove_item': 'remove_item',
					},

					initialize: function() {
						this.template = _.template($('#CartLine-template').html());
					},

					render: function(){
						this.$el.html(this.template(this.model.toJSON()) );
        				return this;
					},

					increase_quantity: function(){
						var quantity = this.model.get('quantity');
						quantity++;
						this.model.set({"quantity": quantity});
						this.render();
					},

					decrease_quantity: function(){
						var quantity = this.model.get('quantity');
						
						if (quantity >1){  //min 1 item must remain. Delete with delete action, not by setting quantity 0
							quantity--;
						}
						
						this.model.set({"quantity": quantity});
						this.render();
					},
										
					remove_item: function(){
						this.collection.remove(this.model.destroy());
						
					},
		});


	$(document).ready(function() {
		if(myCart){
		var shoppingCart = new ShoppingCart([],{cart_id: myCart}); //need myCart variable to be rendered on page

		shoppingCart.fetch({
			reset: true,
			success: function(){
						console.log(shoppingCart);
						var shoppingCartView = new CartView({collection: shoppingCart});
						shoppingCartView.render();
					},
		});

		var cartDiscount = new DiscountOffer();
		var cartDiscountView = new CartDiscountView({model: cartDiscount});

		cartDiscount.fetch({
				reset: true,
				success: function(){
						console.log(cartDiscount);
						
						cartDiscountView.render();
						}
				});

		
		}});
})(jQuery);