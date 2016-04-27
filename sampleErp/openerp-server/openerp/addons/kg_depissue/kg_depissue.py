import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

import openerp.addons.decimal_precision as dp

class kg_depissue(osv.osv):

	_name = "kg.depissue"
	_description = "Dep Issue"
	_columns = {
		'name': fields.char('Dep.Issue.No', size=64, required=True, readonly=True),
		'dep_name': fields.many2one('kg.depmaster','Dep.Name',required=True, translate=True, select=True),
		'date': fields.date('Date', required=True, readonly=True),
		'dep_issue_line': fields.one2many('kg.depissue.line', 'issue_id', 'Issue Lines'),
		'active': fields.boolean('Active'),
		'src_location':fields.many2one('stock.location', 'Source Store', required=True),
		'des_location':fields.many2one('stock.location', 'Destination Store', required=True),		
		'state': fields.selection([('draft','Draft'),('confirm','Confirmed'),('approve','Approved'),('done', 'Done'),('cancel','Cancel')], 'Status', track_visibility='onchange', readonly=True, required=True)
		
	}
	_sql_constraints = [('name_uniq','unique(name)', 'Issue number must be unique!')]

	_defaults = {
		
		'name' : '/',
		'state' : 'draft',
		'active' : 'True',
		'date' : fields.date.context_today,
		
	}
	
	def draft_issue(self, cr, uid, ids,context=None):
		"""
		Draft Issue
		"""
		self.write(cr,uid,ids,{'state':'draft'})
		return True
		
	def confirm_issue(self, cr, uid, ids,context=None):
		"""
		Issue Done
		"""
		for t in self.browse(cr,uid,ids):
			if not t.dep_issue_line:
				raise osv.except_osv(
						_('Empty Department Issue'),
						_('You can not confirm an empty Department Issue'))
			if t.dep_issue_line[0].qty==0:   
				raise osv.except_osv(
						_('Error'),
						_('Department Issue quantity can not be zero'))
						
			self.write(cr,uid,ids,{'state':'confirm'})
			return True
		
	def approve_issue(self, cr, uid, ids,context=None):
		"""
		Issue Done
		"""
		self.write(cr,uid,ids,{'state':'approve'})
		return True
		
	def done_issue(self, cr, uid, ids,context=None):
		"""
		Issue Done
		"""
		self.write(cr,uid,ids,{'state':'done'})
		return True
		
	def cancel_indent(self, cr, uid, ids, context=None):
		"""
		Cancel Issue
		"""
		self.write(cr, uid,ids,{'state' : 'cancel'})
		return True
		
	def create(self, cr, uid, vals, context=None):
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'kg.depissue') or '/'
		order =  super(kg_depissue, self).create(cr, uid, vals, context=context)
		return order
	
	

kg_depissue()

class kg_depissue_line(osv.osv):
	
	_name = "kg.depissue.line"
	_description = "Dep Issue Line"
	
	_columns = {

	'issue_id': fields.many2one('kg.depissue', 'Issue NO', required=True, ondelete='cascade'),
	'product_id': fields.many2one('product.product', 'Product', required=True),
	'uom': fields.many2one('product.uom', 'UOM', required=True),
	'qty': fields.float('Indent Qty', required=True),
	'issue_qty': fields.float('Issue Qty', required=True),
	'src_location':fields.many2one('stock.location', 'Source Store', required=True),
	'des_location':fields.many2one('stock.location', 'Destination Store', required=True),			
	'note': fields.text('Remarks')

	
	}
	
kg_depissue_line()	
