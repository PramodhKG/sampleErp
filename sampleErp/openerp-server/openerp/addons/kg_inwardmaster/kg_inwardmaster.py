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


class kg_inwardmaster(osv.osv):

	_name = "kg.inwardmaster"
	_description = "Inward Master"
	_columns = {
		
		'name': fields.char('Inward Type', size=128, required=True, select=True),
		'creation_date':fields.datetime('Creation Date',readonly=True),
		'bill': fields.boolean('Bill Indication'),
		'return': fields.boolean('Return Indication'),
		'valid': fields.boolean('Valid Indication'),
		'active': fields.boolean('Active'),

		
	}
	
	_sql_constraints = [
		('name', 'unique(name)', 'Inward Type must be unique!'),
	]
	
	_defaults = {
	
	'active':True,
	'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
	
	}
	
	def write(self, cr, uid, ids, vals, context=None): 
		v_name = None 
		
		if vals.get('name'): 
			v_name = vals['name'].strip() 
			vals['name'] = v_name.upper() 
						
		result = super(kg_inwardmaster,self).write(cr, uid, ids, vals, context=context) 
		return result
		
	def create(self, cr, uid, vals, context=None): 
		v_name = None 
		if vals.get('name'): 
			v_name = vals['name'].strip() 
			vals['name'] = v_name.upper() 
		
			
		result = super(kg_inwardmaster,self).create(cr, uid, vals, context=context) 
		return result


	
kg_inwardmaster()
