(function($) {

	var ShoppingCartLine = Backbone.Model.extend ({

			defaults: function(){	
				return {
						id:"",
		                product_name: "",
		                quantity: 0,
		                quantity_unit: "",
		                unit_price: "",
						}
					},

			total_amount: function(){
				var total_amount = this.quantity * this.unit_price;
				return total_amount
			},

			toJSON: function(){  //overriding toJSON of model
    				// get the standard json for the object
    				var json = Backbone.Model.prototype.toJSON.apply(this, arguments);

    				// get the calculated total_amount
    				json.total_amount = this.total_amount;

    				// send it all back
    				return json;
 					 },
			});

	var ShoppingCart = Backbone.Collection.extend({
			model:  ShoppingCartLine,

			initialize: function(models, options){
				this.url = '/api/shopping_cart/'+options.locale+'/'+options.cart_id;
				

				},

        });

	var CartView = Backbone.View.extend({

					el: $('#cart-lines-container'),
					initialize: function() {
						this.collection.on('remove', this.render, this);
						this.collection.on('change', this.render, this);

					},

					events: {
						'click .cart-save': 'cartSave',
						
					},

					render: function() {
						this.$el.html('');
						this.collection.each(function(shoppingCartLine){
							var cartLineView = new CartLineView({model: shoppingCartLine, collection: this.collection});
							this.$el.append(cartLineView.render().el);

						}, this)

						this.$el.append('<hr><h5>Cart Total: ' + this.cartTotal() +'  kr</h5>').html();

						this.$el.append('<hr><button type="button" class="btn btn-info cart-save"  id="cart-save-button">SaveCart</button>   '+

										'<a href="'+ CheckOut_URL +'" class="btn btn-success cart-save" + id="cart-checkout-button">CheckOut</a>'
							);
						
						return this;
					},

					cartSave: function(){
						Backbone.sync('update', this.collection);
						console.log('updating');
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
		var shoppingCart = new ShoppingCart([],{cart_id: myCart, locale:"se"}); //need myCart variable to be rendered on page

		shoppingCart.fetch({
			reset: true,
			success: function(){
						console.log(shoppingCart);
						var shoppingCartView = new CartView({collection: shoppingCart });
						shoppingCartView.render();
					},
		});

	});

})(jQuery);