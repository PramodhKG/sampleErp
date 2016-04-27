from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import re
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class kg_depmaster(osv.osv):

	_name = "kg.depmaster"
	_description = "Department Master"
	_rec_name = 'dep_name' 
	
	_columns = {
		'name': fields.char('Dep.Code', size=64, required=True, readonly=True),
		'dep_name': fields.char('Dep.Name', size=64, required=True, translate=True),
		'consumerga': fields.many2one('account.account', 'Consumer GL/AC', size=64, translate=True, select=2),
		'cost': fields.many2one('account.account','Cost Centre', size=64, translate=True, select=2),
		'stock_location': fields.many2one('stock.location', 'Dep.Stock Location', size=64, translate=True, 
					select=True, required=True, domain=[('usage','<>','view')]),
					
		'main_location': fields.many2one('stock.location', 'Main Stock Location', size=64, translate=True, 
					select=True, required=True, domain=[('usage','<>','view')]),
		'used_location': fields.many2one('stock.location', 'Used Stock Location', size=64, translate=True, 
					select=True, required=True, domain=[('usage','<>','view')]),
		'creation_date':fields.datetime('Creation Date',readonly=True),
		'product_id': fields.many2many('product.product', 'product_deparment', 'depmaster_id', 'product_depid', 'Product'),
		'issue_period': fields.selection([('weekly','Weekly'), ('15th','15th Once'), ('monthly', 'Monthly')], 'Stock Issue Period'),
		'issue_date': fields.float('Stock Issue Days'),
		'active': fields.boolean("Active"),
		'sub_indent': fields.boolean("Sub.Store.Ind")

	}


	_defaults = {
		'active': True,
		'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'name': '/',
	}
	_sql_constraints = [
		('code_uniq', 'unique(name)', 'Department code must be unique!'),
		('name_uniq', 'unique(dep_name)', 'Department name must be unique !'),
	]
	
	def create(self, cr, uid, vals, context=None):
		v_name = None 
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'kg.depmaster') or '/'
		if vals.get('dep_name'): 
			v_name = vals['dep_name'].strip() 
			vals['dep_name'] = v_name.capitalize() 
		order =  super(kg_depmaster, self).create(cr, uid, vals, context=context) 
		return order
		
	def write(self, cr, uid, ids, vals, context=None):
		v_name = None 
		if vals.get('dep_name'): 
			v_name = vals['dep_name'].strip() 
			vals['dep_name'] = v_name.capitalize()
		order =  super(kg_depmaster, self).write(cr, uid, ids, vals, context=context) 
		return order
	

kg_depmaster()
