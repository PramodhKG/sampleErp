from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

import openerp.addons.decimal_precision as dp

class kg_shift_time(osv.osv):

	_name = "kg.shift.time"
	_description = "Shift Time Master"
	_columns = {
		
		'name': fields.char('Shift Name', size=128, required=True, select=True),
		'company_id': fields.many2one('res.company', 'Company Name'),

		
	}
	
	
kg_shift_time()
