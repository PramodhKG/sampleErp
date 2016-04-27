openerp.kg_depindent = function (instance) {
    instance.web.client_actions.add('example.action', 'instance.kg_depindent.Action');
    instance.kg_depindent.Action = instance.web.Widget.extend({
        template: 'kg_depindent.action'
    });
};