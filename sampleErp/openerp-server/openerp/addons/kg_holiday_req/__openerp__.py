##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'KG Leave Request',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'HRM',
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to manage Employees Leave Allocation.
===========================================================

""",
    'depends' : ['hr','base','kg_allocation_leave','kg_hrm_users'],
    'data': ['kg_holiday_req.xml'],
    'css': ['static/src/css/state.css'],
    'auto_install': False,
    'installable': True,
}
