
{
    'name': 'KG General GRN',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'Item Details',
   
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to manage your Item Details.
===========================================================
""",
    'depends' : ['base', 'product','stock','kg_depmaster'],
    'data': ['kg_general_grn_view.xml',
		
			],
			
	"""'js': [ "static/src/js/kg_general_grn.js",
		
			],
			
	'qweb': [ "static/src/xml/kg_general_grn.xml",
		
			],"""
			
	
    'auto_install': False,
    'installable': True,
}

