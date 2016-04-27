from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

class kg_deliverytype_master(osv.osv):

	_name = "kg.deliverytype.master"
	_description = "Delivery Type Master"
	_columns = {
		
		'name': fields.char('Delivery Type', size=128, required=True, select=True),
		'date': fields.date('Date'),
		'active': fields.boolean('Active'),

		
	}
	
	_defaults = {
	
	'date': fields.date.context_today,
	'active' : 'True',
	
	}


	
kg_deliverytype_master()
