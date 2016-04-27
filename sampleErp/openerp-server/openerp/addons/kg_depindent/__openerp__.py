##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'KG_Department_Indent',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'Department_Management',
    'images': ['images/purchase_requisitions.jpeg'],
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to manage your Purchase Requisition.
===========================================================

When a purchase order is created, you now have the opportunity to save the
related requisition. This new object will regroup and will allow you to easily
keep track and order all your purchase orders.
""",
    'depends' : ['base', 'product', 'kg_depmaster','kg_sale_projection'],
    'data': ['kg_depindent_view.xml',
			'wizard/kg_depindent_wizard.xml',
		    'wizard/kg_pending_depindent_wizard.xml',
			'kg_depindent_report.xml'
			],
			
	'test': [
        
        'test/ui/indent_report.yml',
        
    ],
    'css': [
        'static/src/css/state.css', 
        
    ],
    
    #'js': ['static/src/js/first_module.js'],
	#'qweb': ['static/src/xml/base.xml'],
    'auto_install': False,
    'installable': True,
}

