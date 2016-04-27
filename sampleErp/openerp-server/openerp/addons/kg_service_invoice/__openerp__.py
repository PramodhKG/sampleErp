##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'KG_Service_Invoice',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'Service_Management',
    'website': 'http://www.openerp.com',   
    'depends' : ['base', 'product','kg_depmaster'],
    'data': [
			
			'kg_service_invoice_view.xml',
			
			
			],
    'auto_install': False,
    'installable': True,
}

