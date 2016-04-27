from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import re
import math
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


class kg_tax_structure(osv.osv):
	
	def _check_line(self, cr, uid, ids, context=None):
		print "_check_line ================>>>>", ids
		tax_rec = self.browse(cr, uid, ids[0])
		if not tax_rec.tax_line:			
			return False					
		return True
	

	_name = "kg.tax.structure"
	_description = "KG Tax Structure"
	
	_columns = {
		'name': fields.char('Name', size=128, required=True,readonly=True, states={'draft':[('readonly',False)]}),		
		'type': fields.selection([('po','Purchase'),('serv','Service')], 'Type', required=True,
					readonly=True, states={'draft':[('readonly',False)]}),
		'state': fields.selection([('draft','Draft'),('app','Approved')], 'Status', readonly=True),
		'tax_line': fields.one2many('kg.tax.structure.line', 'stru_id', 'Tax Structure',
						readonly=True, states={'draft':[('readonly',False)]}),
	    'active': fields.boolean('Active'),
	    'creation_date':fields.datetime('Creation Date',readonly=True),
		
	}
	
	_sql_constraints = [
		('name', 'unique(name)', 'Tax Structure must be unique!'),
	]
	
	_constraints = [	
				(_check_line,'You can not save this Tax Structure with out Line !!!',['tax_line']),
		]
	
	_defaults = {
	
		'type': 'po',
		'state'	: 'draft',
		'active':True,
		'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
	}
	
	def create(self, cursor, user, vals, context=None):
		if vals.get('name'):
			vals['name'] = vals['name'].upper()
	   
		return super(kg_tax_structure, self).create(cursor, user, vals,
				context=context)

	def write(self, cursor, user, ids, vals, context=None):
		if vals.get('name'):
			vals['name'] = vals['name'].upper()

		return super(kg_tax_structure, self).write(cursor, user, ids, vals,
				context=context)
	
	def approve_tax(self, cr, uid, ids,context=None):		
		self.write(cr,uid,ids,{'state':'app'})
		return True
	
	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		stru = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for t in stru:
			if t['state'] in ('draft'):
				unlink_ids.append(t['id'])
			else:
				raise osv.except_osv(_('Invalid action !'), _('System not allow to delete a Approved state Tax Structure!!'))
		stru_lines_to_del = self.pool.get('kg.tax.structure.line').search(cr, uid, [('stru_id','in',unlink_ids)])
		self.pool.get('kg.tax.structure.line').unlink(cr, uid, stru_lines_to_del)
		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		return True
		
	def open_web(self, cr, uid, ids, context=None):
		print "open_web called from kg---------Tax><>>><><><><><><>"
		if not context:
			context = {}
		if not ids:
			return {}
		context.update({'active_id': ids[0]})
		return {
			'type' : 'ir.actions.client',
			'name' : _('Tax Structure'),
			'tag' : 'tax.ui',
			'context' : context,
		}
	
kg_tax_structure()

class kg_tax_structure_line(osv.osv):
	
	_name = "kg.tax.structure.line"
	_description = "Tax Structure Line"
	
	
	_columns = {

	'stru_id': fields.many2one('kg.tax.structure', 'Tax Structure', ondelete='cascade'),
	'tax_id':fields.many2one('account.tax','Tax Name',required=True),
	#'tax_name':fields.char('Tax Name', size=128, readonly=True),
	'tax_type': fields.selection([
				('percent','Percentage'), 
				('fixed','Fixed Amount'),
				('none','None'), 
				('code','Python Code'), 
				('balance','Balance')], 'Value Type', readonly=True),
	'value': fields.float('Value', readonly=True)
	}
	
		
	def onchange_tax_id(self, cr, uid,ids,tax_id):
		tax_obj = self.pool.get('account.tax')
		if tax_id:
			tax_rec = tax_obj.browse(cr, uid, tax_id)
			name = tax_rec.name
			tax_type = tax_rec.type
			amt = tax_rec.amount						
			return {'value': 
						{'tax_type' : tax_type,
						'value' : amt
						}}
		else:
			pass
			
	def create(self,cr,uid,vals,context={}):
		print "Line create called........vals===....",vals
		if vals['tax_id']:
			tax_rec = self.pool.get('account.tax').browse(cr,uid,vals['tax_id'])
			vals.update({'tax_type':tax_rec.type,
						'value':tax_rec.amount
						})	  
		return super(kg_tax_structure_line,self).create(cr,uid,vals,context)
		
	def write(self,cr,uid,ids,vals,context={}):
		print "Line write ------ called........vals===....",vals
		if vals.has_key('tax_id') and vals['tax_id']:
			tax_rec = self.pool.get('account.tax').browse(cr,uid,vals['tax_id'])
			vals.update({'tax_type':tax_rec.type,
						'value':tax_rec.amount
						})
		return super(kg_tax_structure_line,self).write(cr,uid,ids,vals,context)			
		
	
kg_tax_structure_line()
