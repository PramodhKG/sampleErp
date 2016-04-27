{
    'name': 'HRM_Users',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'User_Management',
    'website': 'http://www.openerp.com',
    'depends' : ['base'],
    'data': [
			'kg_user_groups.xml',
			'kg_hrm_employee.xml',
			'kg_hr_admin.xml',
			'kg_hrm_md.xml',
			],
			
    'auto_install': False,
    'installable': True,
}

