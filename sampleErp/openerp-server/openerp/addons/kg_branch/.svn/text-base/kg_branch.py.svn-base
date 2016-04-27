from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

import openerp.addons.decimal_precision as dp

class kg_branch(osv.osv):

	_name = "kg.branch"
	_description = "KG Branch"
	
	_columns = {
		
		'name': fields.char('Branch Name', size=128, required=True, select=True),
		'company_id': fields.many2one('res.company', 'Company Name'),
		'code': fields.char('Code', size=128, required=True),
		'crm_id':fields.integer('CRM ID'),
        'rsm_id':fields.many2one('hr.employee','RSM',required=False),
        'asi_id':fields.many2one('hr.employee','ASI',required=False),
        		
	}
	
	_defaults = {
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg.branch', context=c),		
	}
	
	_sql_constraints = [
	
		('name', 'unique(name)', 'Branch name must be unique per Company !!'),
		('code', 'unique(code)', 'Branch code must be unique per Company !!'),
	]
	
	
kg_branch()
