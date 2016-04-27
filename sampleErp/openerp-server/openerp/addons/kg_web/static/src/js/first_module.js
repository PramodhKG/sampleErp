openerp.kg_web = function (instance) {
    instance.web.client_actions.add('example.action', 'instance.kg_web.Action');
    instance.kg_web.Action = instance.web.Widget.extend({
        template: 'kg_web.action',
        events: {
            'click .oe_web_example_start button': 'watch_start',
            'click .oe_web_example_stop button': 'watch_stop',
            'click .oe_web_example_clear button': 'watch_clear'
        },        
        
        fetch: function(model, fields, domain, ctx){
            return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all()
		},
            
        watch_clear: function () {
			alert('Hello');
			return self.fetch('res.partner',name,null);
		}       
        
    });
};
