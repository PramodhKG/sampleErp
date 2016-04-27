import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

class kg_dep_standard_issue(osv.osv):

	_name = "kg.dep.standard.issue"
	_description = "Dep Standard Issue"
	_columns = {
		'name': fields.many2one('kg.depmaster', 'Department Name', required=True),
		'std_name': fields.many2one('kg.depmaster','Standard Issue Name',required=True, select=True),
		'date': fields.date('Date', required=True),
		'std_lineid': fields.one2many('kg.dep.standard.issue.line', 'std_id', 'Standard Line', required=True)
				
	}
	
	_defaults = {
	
		'date' : fields.date.context_today,
		
	}
	
	
kg_dep_standard_issue()

class kg_dep_standard_issue_line(osv.osv):
	
	_name = "kg.dep.standard.issue.line"
	_description = "Stand Line"
	
	_columns = {

	'std_id': fields.many2one('kg.dep.standard.issue', 'Standard Reference', required=True, ondelete='cascade'),
	'product_id': fields.many2one('product.product', 'Item Name', required=True),
	'uom': fields.many2one('product.uom', 'UOM', required=True),
	'qty': fields.float('Standard Qty', required=True),
	'note': fields.text('Remarks')

	
	}
	
kg_dep_standard_issue_line()
