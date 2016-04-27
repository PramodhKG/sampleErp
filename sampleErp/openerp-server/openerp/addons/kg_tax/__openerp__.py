##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'KG TDS',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'HRM',
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to manage Employees Leave Allocation.
===========================================================

""",
    'depends' : ['hr','base'],
    'data': ['kg_tax.xml'],
   
    'auto_install': False,
    'installable': True,
}

