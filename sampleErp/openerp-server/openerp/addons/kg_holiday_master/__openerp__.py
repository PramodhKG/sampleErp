##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'KG Holiday Master',
    'version': '0.1',
    'author': 'Shubashri',
    'category': 'HRM',
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to enter Holidays in a month.
===========================================================

""",
    'depends' : ['base','kg_branch'],
    'data': ['kg_holiday_master_view.xml'],
  
    'auto_install': False,
    'installable': True,
}

