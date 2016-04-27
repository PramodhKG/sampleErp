##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'GRN Moves',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'Inventory_Management',
    'images': ['images/purchase_requisitions.jpeg'],
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to manage your Stock Issue.
===========================================================

""",
    'depends' : ['base', 'product','kg_depmaster'],
    'data': ['kg_grn_moves_view.xml'],
    'auto_install': False,
    'installable': True,
}

