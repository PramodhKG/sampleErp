##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'KG_GRN',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'KG_GRN',
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to manage your Purchase Requisition.
===========================================================

When a purchase order is created, you now have the opportunity to save the
related requisition. This new object will regroup and will allow you to easily
keep track and order all your purchase orders.
""",
    'depends' : ['base','purchase','stock','kg_depindent'],
    'data': [
		'kg_grn_view.xml',
		'kg_stock_partial_picking_view.xml',
		'kg_po_invoice_wizard.xml',
		
	],
	
	'css': [
        'static/src/css/state.css', 
        
    ],
    'auto_install': False,
    'installable': True,
}

