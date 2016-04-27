##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'KG Inventory Users',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'User_Management',
    'images': ['images/purchase_requisitions.jpeg'],
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to manage your Purchase Requisition.
===========================================================

When a purchase order is created, you now have the opportunity to save the
related requisition. This new object will regroup and will allow you to easily
keep track and order all your purchase orders.
""",
    'depends' : ['base','kg_menus','kg_grn'],
    'data': [
			'kg_groups.xml',
			'kg_master_admin.xml',
			'kg_po_admin.xml',
			'kg_sub_store.xml',
			'kg_main_store.xml',
			
			
			],
			
    'auto_install': False,
    'installable': True,
}

