from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

class kg_minormaster(osv.osv):

	_name = "kg.minormaster"
	_description = "KG Minormaster"
	_columns = {
		
		'major_name': fields.many2one('product.category', 'Major Name', required=True, select=True),
		'name': fields.char('Minor Name', size=64),
		'date': fields.date('Date'),
		'active': fields.boolean('Active'),


		
		
	}
	
	_defaults = {
	
	'date': fields.date.context_today,
	'active' : 'True',
	
	}
	
	_sql_constraints = [
	
	('name_uniq', 'unique(name)', 'Minor name must be unique !!!'),
	
	]


	
kg_minormaster()
