from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

import openerp.addons.decimal_precision as dp

class kg_transport(osv.osv):

	_name = "kg.transport"
	_description = "KG Transport"
	
	_columns = {
		
		'name': fields.char('Transport Name', size=128, required=True, select=True),
		'company_id': fields.many2one('res.company', 'Company Name'),
		'contact_person': fields.char('Contact Person', size=128, required=True, select=True),
		'address': fields.char('Address', size=128),
		'address1': fields.char('Address1', size=128),
		'city': fields.char('City', size=128),
		'zip': fields.char('Zip', size=128),
		'mobile': fields.char('Mobile', size=128),
		'phone': fields.char('Phone', size=128),
		'email': fields.char('Email', size=128),
		'state_id': fields.many2one('res.country.state', 'State'),
		'country_id': fields.many2one('res.country', 'Country'),
		'active': fields.boolean('Active'),


		
	}
	
	_defaults = {
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg.segment', context=c),
		'active': True,
	}
	
	_sql_constraints = [
	
		('name', 'unique(name)', 'Transport name must be unique per Company !!'),
	]
	
	
kg_transport()
