##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'KG Allocation Request',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'HRM',
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to manage Employees Leave Allocation.
===========================================================

""",
    'depends' : ['hr','base'],
    'data': ['kg_allocation_leave.xml'],
    'css': ['static/src/css/state.css'],
    'auto_install': False,
    'installable': True,
}

