import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

class kg_dep_standard_entry(osv.osv):

	_name = "kg.dep.standard.entry"
	_description = "Dep Standard Entry"
	_columns = {
		'name': fields.char('Standard Name', size=128, required=True),
		'dep_name': fields.many2one('kg.depmaster','Department Name',required=True, select=True),
		'date': fields.date('Date', required=True),
		'issue_days': fields.integer('No.of Issue Days'),
		'active': fields.boolean('Active')
				
	}
	
	_defaults = {
	
		'active' : 'True',
		'date' : fields.date.context_today,
		
	}
	
	
kg_dep_standard_entry()
