import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp


class kg_service_indent(osv.osv):

	_name = "kg.service.indent"
	_description = "KG Service Indent"
	_order = "date desc"

	
	_columns = {
		'name': fields.char('Service.Indent.No', size=64, readonly=True),
		'dep_name': fields.many2one('kg.depmaster','Dep.Name', translate=True, select=True),
		'date': fields.date('Date', required=True, readonly=True),
		'service_indent_line': fields.one2many('kg.service.indent.line', 'service_id', 'Indent Lines', readonly=True, states={'draft':[('readonly',False)]}),
		'active': fields.boolean('Active'),
		'user_id' : fields.many2one('res.users', 'User', readonly=False),
		'state': fields.selection([('draft', 'Draft'),('confirm','Waiting For Approval'),('approved','Approved'),('done','Done'),('cancel','Cancel')], 'Status', track_visibility='onchange', required=True),
		'gate_pass': fields.boolean('Gate Pass', readonly=True, states={'draft':[('readonly', False)]}),
		'test':fields.char('Test',size = 500)
		
	}
	_sql_constraints = [('code_uniq','unique(name)', 'Indent number must be unique!')]

	_defaults = {
		'state' : 'draft',
		'active' : 'True',
		'date' : fields.date.context_today,
		'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
		'name' : '/',

	}
	
	
	def draft_indent(self, cr, uid, ids,context=None):
		"""
		Draft Ident
		"""
		self.write(cr,uid,ids,{'state':'draft'})
		return True
		
	def confirm_indent(self, cr, uid, ids,context=None):
		print "ids----------confirm-------", ids
		"""
		Indent approve
		"""
		for t in self.browse(cr,uid,ids):
			if not t.service_indent_line:
				raise osv.except_osv(
						_('Empty Service Indent'),
						_('You can not confirm an empty Service Indent'))
			print "t.dep_indent_line,,,,,,,,,,,,,,,,,", t.service_indent_line
			service_indent_line = t.service_indent_line[0]
			service_indent_line_id = service_indent_line.id
			print "t.depindent_line_id,,,,,,,,,,,,,,,,,", service_indent_line_id

			if t.service_indent_line[0].qty==0:
				raise osv.except_osv(
						_('Error'),
						_('Service Indent quantity can not be zero'))
			self.write(cr,uid,ids,{'state':'confirm'})
			#self.write(cr, uid,depindent_line_id,{'state' : 'confirm'})
			return True
			
	def approve_indent(self, cr, uid, ids,context=None):
		si_rec = self.browse(cr, uid, ids)
		print "si_rec------------------", si_rec
		if si_rec[0].gate_pass == True:
			gate_obj = self.pool.get('kg.gate.pass')
			gate_line_obj = self.pool.get('kg.gate.pass.line')
			gate_pass_vals = {
		
			'name': self.pool.get('ir.sequence').get(cr, uid, 'kg.gate.pass'),
			'dep_id': si_rec[0].dep_name.id,
			'origin': si_rec[0].id, 
				
			}
			
			gate_id = gate_obj.create(cr, uid, gate_pass_vals, context=context)
			print "gate_id------------------>>>", gate_id
			for line in si_rec[0].service_indent_line:
				line_vals = {
		
				'gate_id' : gate_id,
				'product_id' : line.product_id.id,
				'uom': line.uom.id,
				'qty': line.qty,
				'note': line.note,					
				}			
				gate_line_id = gate_line_obj.create(cr, uid, line_vals, context=context)
			self.write(cr,uid,ids,{'state':'done'})			
		else:
			self.write(cr,uid,ids,{'state':'done'})
		return True
		
	def done_indent(self, cr, uid, ids,context=None):
			
		self.write(cr,uid,ids,{'state':'done'})
		return True
		
	def cancel_indent(self, cr, uid, ids, context=None):
		"""
		Cancel Indent
		"""
		
		self.write(cr, uid,ids,{'state' : 'cancel'})
		return True

	def create(self, cr, uid, vals, context=None):
		
		if vals.has_key('user_id') and vals['user_id']:
			user_dep_name = self.pool.get('res.users').browse(cr,uid,vals['user_id'])
			print "user_dep_name =======================", user_dep_name
			if user_dep_name.dep_name:
				vals.update({'dep_name':user_dep_name.dep_name.id})
				
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'kg.service.indent') or '/'
		order =  super(kg_service_indent, self).create(cr, uid, vals, context=context)
		return order
		
	def write(self, cr, uid,ids, vals, context=None):
	
		if vals.has_key('user_id') and vals['user_id']:
			user_dep_name = self.pool.get('res.users').browse(cr,uid,vals['user_id'])
			if user_dep_name.dep_name:
				vals.update({'dep_name':user_dep_name.dep_name.id})
						 
		res = super(kg_service_indent, self).write(cr, uid, ids,vals, context)
		
		return res
		
	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		indent = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for t in indent:
			if t['state'] in ('draft'):
				unlink_ids.append(t['id'])
			else:
				raise osv.except_osv(_('Invalid action !'), _('System not allow to delete a UN-DRAFT state Department Indent!!'))
		indent_lines_to_del = self.pool.get('kg.service.indent.line').search(cr, uid, [('service_id','in',unlink_ids)])
		self.pool.get('kg.service.indent.line').unlink(cr, uid, indent_lines_to_del)
		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		return True

		
	def onchange_user_id(self, cr, uid, ids, user_id, context=None):
		value = {'dep_name': ''}
		if user_id:
			user = self.pool.get('res.users').browse(cr, uid, user_id, context=context)
			value = {'dep_name': user.dep_name.id}
		return {'value': value}
		
		
	def _check_lineitem(self, cr, uid, ids, context=None):
		print "called liteitem ___ function"
		for si in self.browse(cr,uid,ids):
			if si.service_indent_line==[] or si.service_indent_line:
					tot = 0.0
					for line in si.service_indent_line:
						tot += line.qty
					if tot <= 0.0:			
						return False
						
			return True
	
	_constraints = [
        (_check_lineitem, 'You can not save this Service Indent with out Line and Zero Qty  !!',['qty']),
        ]
        
		

kg_service_indent()

class kg_service_indent_line(osv.osv):
	
	_name = "kg.service.indent.line"
	_description = "Service Indent"

	def onchange_product_id(self, cr, uid, ids, product_id, uom,context=None):
			
		value = {'uom': ''}
		if product_id:
			prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			value = {'uom': prod.uom_id.id}

		return {'value': value}
		
	def onchange_qty(self,cr,uid,ids,qty,pending_qty,context=None):
		print "called onchange_qty................."
		value = {'pending_qty': ''}
		if qty:
			pending_qty = qty
			value = {'pending_qty' : pending_qty}
		return {'value': value}
			
	
	
	
	_columns = {

	'service_id': fields.many2one('kg.service.indent', 'Service.Indent.NO', required=True, ondelete='cascade'),
	'product_id': fields.many2one('product.product', 'Product', required=True, domain=[('type','=','service')]),
	'uom': fields.many2one('product.uom', 'UOM', required=True),
	'qty': fields.float('Qty', required=True),
	'pending_qty':fields.float('Pending Qty'),
	'note': fields.text('Remarks'),
	
	
	}
		
	
kg_service_indent_line()	
