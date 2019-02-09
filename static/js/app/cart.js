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
					}
			});

	var ShoppingCart = Backbone.Collection.extend({
			model:  ShoppingCartLine,

			initialize: function(models, options){
				console.log("new ShoppingCart #"+options.cart_id +" for "+options.locale);
				this.url = '/api/shopping_cart/'+options.locale+'/'+options.cart_id;
					
				console.log("@"+this.url);
				},

        });

	var CartView = Backbone.View.extend({
//					model: tweets,
					el: $('#cart-lines-container'),
					initialize: function() {
//						this.model.on('add', this.render, this);
						this.collection.on('remove', this.render, this);
					},

					events: {
						'click #cart-save-button': 'cartSave',
					},

					render: function() {
						this.$el.html('');
						this.collection.each(function(shoppingCartLine){
							var cartLineView = new CartLineView({model: shoppingCartLine, collection: this.collection});
							this.$el.append(cartLineView.render().el);
						}, this)

						this.$el.append('<hr> <button type="button" class="btn btn-success"  id="cart-save-button">SaveCart</button>').html();
						
						return this;
					},

					cartSave: function(){
						Backbone.sync('update', this.collection);
						console.log('updating');
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
						quantity--;
						this.model.set({"quantity": quantity});
						this.render();
					},
										
					remove_item: function(){
						this.collection.remove(this.model);				
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