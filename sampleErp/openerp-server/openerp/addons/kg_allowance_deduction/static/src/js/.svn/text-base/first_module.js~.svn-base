// static/src/js/first_module.js
openerp.web_example = function (instance) {
    instance.web.client_actions.add('example.action', 'instance.web_example.Action');
    instance.web_example.Action = instance.web.Widget.extend({
        className: 'oe_web_example',
        start: function () {
            this.$el.text("Hello, world!");
            return this._super();
        }
    });
};
