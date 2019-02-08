var CartLine = Backbone.Model.extend ({
	
	defaults: {	

	}

});

var Cart = Backbone.Collection.extend({
	
	model:  CartLine,
	
	initialize: function(models, options){
		console.log("new Cart #"+options.cart_id +" for "+options.locale);
		this.url = '/api/shopping_cart/'+options.locale+'/'+options.cart_id;
			
		console.log("@"+this.url);
		},

	defaults: {		

	},

        });

var LineView= Backbone.View.extend({
	tagName: "tr",
	template: _.template($('#line_template').html()),

	events: {
    "keydown .form-input": "setAttribute"
	},

	initialize: function() {
    this.model.on("remove", this.remove);
    console.log(parseInt('lineprice: '+ this.model.quantity * this.model.unit_price));
    this.model.set({linetotal: parseInt(this.model.quantity * this.model.unit_price)});
		},

	render : function(){
		var model = this.model.toJSON();

        var html = this.template({
            model: model
        });
        this.$el.html(html);
        
        return this;
	},

	setAttribute : function(){
	
				var value = document.getElementById('quantity_input_'+this.model.id).value;
				this.model.set({ quantity: parseInt(value), linetotal: this.model.quantity * this.model.unit_price});
				this.model.save({}, {
		        error: function(){
		            console.log('error');
		        	},
		        success: function(){
		            console.log('success');
		           	}
        		});

    			this.render;
			
	}

});
 
var CartView = Backbone.CollectionView.extend({
  itemView: LineView
}); 

$(document).ready(function(){
       
	var testCart = new Cart([],{cart_id: myCart, locale:"se"});

	

	testCart.fetch({
		reset: true,
		success: function(){
			var cartview = new CartView({
				collection : testCart,
				el: "#cart_table",
				});



			cartview.render();
			cartview.renderAllItems();

		}
	});

	
})
	