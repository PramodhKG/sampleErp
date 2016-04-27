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

class kg_subcontract_master(osv.osv):

	_name = "kg.subcontract.master"
	_description = "KG Subcontract Master"
	_order = "creation_date desc"
	
	def write(self, cr, uid, ids, vals, context=None): 
		v_name = None 
		
		if vals.get('name'): 
			v_name = vals['name'].strip() 
			vals['name'] = v_name.upper() 
						
		result = super(kg_subcontract_master,self).write(cr, uid, ids, vals, context=context) 
		return result
		
	def create(self, cr, uid, vals, context=None): 
		v_name = None 
		if vals.get('name'): 
			v_name = vals['name'].strip() 
			vals['name'] = v_name.upper() 
		
			
		result = super(kg_subcontract_master,self).create(cr, uid, vals, context=context) 
		return result
	
	_columns = {
		'name':fields.char('Subcontractor Name',size=128,required=True),
		'creation_date':fields.datetime('Creation Date',readonly=True),
		
		#'type_of_process':fields.selection([('core','Core Subcontract'),('fettling','Fettling Subcontract'),('common','Common'),('others','Others')],'Subcontract Type',required=True,readonly=True,states={'draft': [('readonly', False)]}),
		'website': fields.char('Website', size=64, help="Website of Partner or Company"),
		'street': fields.char('Street', size=128),
		'street2': fields.char('Street2', size=128),
		'zip': fields.char('Zip', change_default=True, size=24),
		'city': fields.many2one("res.city",'City'),
		'state_id': fields.many2one("res.country.state", 'State'),
		'country_id': fields.many2one('res.country', 'Country'),
		'email': fields.char('Email', size=240),
		'phone': fields.char('Phone', size=64),
		'fax': fields.char('Fax', size=64),
		'mobile': fields.char('Mobile', size=64),
		#'state':fields.selection([('draft','Draft'),('confirmed','Confirmed')],'Status',readonly=True,states={'draft': [('readonly', False)]}),
		'active':fields.boolean('Active'),

	}
	_sql_constraints = [
		('name', 'unique(name)', 'Subcontrator name must be unique!'),
	]
	
	def  fields_validation(self, cr, uid, ids, context=None):
		flds = self.browse(cr , uid , ids[0])
		print "flds.work_email..........................",flds.name
		if flds.name and re.match("^([a-zA-Z]+(?:\.)?(?:(?:'| )[a-zA-Z]+(?:\.)?)*)$",flds.name) == None:
		
			return False
		if flds.email and re.match("^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$",flds.email)== None:
			return False
		if flds.mobile and re.match("^((\+){0,1}91(\s){0,1}(\-){0,1}(\s){0,1}){0,1}[7-9][0-9](\s){0,1}(\-){0,1}(\s){0,1}[0-9]{8}$",flds.mobile)== None:
			return False
		if flds.phone and re.match("^((\+){0,1}91(\s){0,1}(\-){0,1}(\s){0,1}){0,1}[7-9][0-9](\s){0,1}(\-){0,1}(\s){0,1}[0-9]{8}$",flds.phone)== None:
			return False
		return True
		
		
	_constraints = [
		(fields_validation, 'Please Enter the valid Format',['Invalid Format']),
	]
	
	_defaults = {
		'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		
		'active':True,
	   }
	   
kg_subcontract_master()
