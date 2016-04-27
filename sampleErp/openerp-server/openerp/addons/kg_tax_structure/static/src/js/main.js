
openerp.kg_tax_structure = function(instance) {

    instance.kg_tax_structure = {};

    var module = instance.kg_tax_structure;
    
    instance.web.client_actions.add('tax.ui', 'instance.kg_tax_structure.Taxweb');
};