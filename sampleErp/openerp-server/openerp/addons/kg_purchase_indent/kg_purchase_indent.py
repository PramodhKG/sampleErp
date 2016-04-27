## KG Purchase Indent Module ##

import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import datetime
from itertools import groupby
import openerp.addons.decimal_precision as dp
import logging
logger = logging.getLogger('server')

class kg_purchase_indent(osv.osv):
	
	_name = "purchase.requisition"
	_inherit = "purchase.requisition"
	_order = "date_start desc"	
	
	_columns = {
	
		'name': fields.char('Purchase Indent No', size=64, readonly=True, states={'draft': [('readonly', False)]}),
		'kg_store': fields.selection([('sub','Sub Store'), ('main','Main Store')], 'Store', readonly=True, states={'draft': [('readonly', False)]}),
		'dep_name' : fields.many2one('kg.depmaster', 'Dep.Name', readonly=True, states={'draft': [('readonly', False)]}),
		'state': fields.selection([('draft','Waiting for Confirmation'),('in_progress','Waiting for Approval'),('cancel','Cancelled'),('done','Purchase Done'),('approved','Approved')],
			'Status', track_visibility='onchange', required=True, readonly=True, states={'draft': [('readonly', False)]}),
		'date_start':fields.datetime('Indent Date', readonly=True),
		'line_ids' : fields.one2many('purchase.requisition.line','requisition_id','Products to Purchase', readonly=True, states={'draft': [('readonly', False)],'in_progress': [('readonly', False)]}),
		'pi_type': fields.selection([('direct','Direct'),('fromdep','From Dep Indent')], 'Type'),
		'pi_flag': fields.boolean('pi flag'),
		'kg_seq_id':fields.many2one('ir.sequence','Document Type',domain=[('code','=','kg.purchase.indent')],
			readonly=True, states={'draft': [('readonly', False)]}),			
		'remark': fields.text('Remarks'),
		'type_flag':fields.boolean('Type Flag'),

	}
	
	_defaults = {
		'exclusive': 'exclusive',
		'kg_store': 'main',
		'name':'',
		'type_flag': False,
		'pi_type': 'fromdep'
	}
	
	_sql_constraints = [
	
		('name_uniq', 'unique(name, company_id)', 'Indent Reference must be unique per Company!'),
	]	
	
	def onchange_seq_id(self, cr, uid, ids, kg_seq_id,name):
		print "kgggggggggggggggggg --  onchange_seq_id called"		
		value = {'name':''}
		if kg_seq_id:
			next_seq_num = self.pool.get('ir.sequence').kg_get_id(cr, uid, kg_seq_id,'id',{'noupdate':False})
			print "next_seq_num:::::::::::", next_seq_num
			value = {'name': next_seq_num}
		return {'value': value}
		
		
	def onchange_type_flag(self, cr, uid, ids, pi_type):
		print "kgggggggggggggggggg --  onchange_seq_id called"
		value = {'type_flag':False}
		if pi_type == 'direct':
			value = {'type_flag': True}
		return {'value': value}


	def create(self, cr, uid, vals, context=None):
		print "callled create from KG",vals
		if vals['type_flag'] == True:
			vals.update({
						'pi_type':'direct',
						
						})
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.requisition') or '/'
		order =  super(kg_purchase_indent, self).create(cr, uid, vals, context=context)
		return order
		
	def unlink(self, cr, uid, ids, context=None):
		print "unlink called ,,,,,,,,,,,,,,,,,,,,,,,,,,,, from KGGGGGG"
		if context is None:
			context = {}
		pi_indent = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for t in pi_indent:
			if t['state'] in ('draft'):
				unlink_ids.append(t['id'])
			else:
				raise osv.except_osv(_('Invalid action !'), _('System not allow to delete a UN-DRAFT state Purchase Indent!!'))
		pi_indent_lines_to_del = self.pool.get('purchase.requisition.line').search(cr, uid, [('requisition_id','in',unlink_ids)])
		self.pool.get('purchase.requisition.line').unlink(cr, uid, pi_indent_lines_to_del)
		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		return True		
		   
	def tender_in_progress(self, cr, uid, ids,kg_seq_id, context=None):
		print "callled tender_in_progress from KG"
		product_obj = self.pool.get('product.product')
		obj = self.browse(cr,uid,ids[0])
		
		for t in self.browse(cr,uid,ids):
			
			indent_line_obj = self.pool.get('kg.depindent.line')
			if not t.line_ids:
				raise osv.except_osv(
						_('Empty Purchase Indent'),
						_('You can not confirm an empty Purchase Indent'))
			for line in t.line_ids:
				if line.product_qty==0:
					raise osv.except_osv(
						_('Error'),
						_('Purchase Indent quantity can not be zero'))
				else:
					print "Line have enough Qty"
					
			self.write(cr,uid,ids,{'state':'approved'})
			cr.execute(""" select depindent_line_id from kg_depindent_pi_line where pi_id = %s """ %(str(ids[0])))
			data = cr.dictfetchall()
			val = [d['depindent_line_id'] for d in data if 'depindent_line_id' in d] # Get a values form list of dict if the dict have with empty values
			print "val...............................",val
			pi_lines = obj.line_ids
			print "obj:::::::::::::::::", obj, "pi_lines..........................",pi_lines
			for i in range(len(pi_lines)):

				product_id = pi_lines[i].product_id.id
				product_record = product_obj.browse(cr, uid, product_id)
				product = pi_lines[i].product_id.name
				print "pi_lines[i].group_flag()()()()()()()()()()()()", pi_lines[i].group_flag
				if pi_lines[i].depindent_line_id and pi_lines[i].group_flag == False:
					depindent_line_id=pi_lines[i].depindent_line_id
					orig_depindent_qty = pi_lines[i].dep_indent_qty
					pi_used_qty = pi_lines[i].product_qty
					po_uom_qty = pi_lines[i].po_uom_qty
					pending_stock_depindent_qty = pi_lines[i].dep_indent_qty -  pi_lines[i].po_uom_qty
					pending_po_depindent_qty = pi_lines[i].po_uom_qty - pi_lines[i].po_uom_qty
					tmp_qty = pi_used_qty * product_record.po_uom_coeff
			
					
					if pi_lines[i].product_uom_id.id != pi_lines[i].default_uom_id.id:
						print "If PArt ====>> product Name::", pi_lines[i].product_id.name, "pi_lines[i] ==>>", pi_lines[i].product_qty,":::", pi_lines[i].product_uom_id.name
						if tmp_qty > orig_depindent_qty or pi_used_qty > po_uom_qty :
							pending_stock_depindent_qty = 0.0
							pending_po_depindent_qty = po_uom_qty - pi_used_qty
							print "depindent_line_id.id******111111111111111111111111*************", depindent_line_id.id, "pending_po_depindent_qty ======>", pending_po_depindent_qty
							sql = """ update kg_depindent_line set po_qty=%s, pending_qty=%s where id = %s"""%(pending_po_depindent_qty,
										pending_stock_depindent_qty,pi_lines[i].depindent_line_id.id)
							cr.execute(sql)
							#indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
							if pending_po_depindent_qty == 0:
								print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
								indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'process'})
							elif pending_po_depindent_qty > 0:
								print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
								indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
						else:
							pending_stock_depindent_qty = orig_depindent_qty - tmp_qty
							pending_po_depindent_qty = po_uom_qty - pi_used_qty
							if pi_used_qty > po_uom_qty:
								pending_stock_depindent_qty = 0.0
								pending_po_depindent_qty = 0.0
								print "depindent_line_id.id*****222222222222222222222**************", depindent_line_id.id, "pending_po_depindent_qty ======>", pending_po_depindent_qty
								sql = """ update kg_depindent_line set po_qty=%s, pending_qty=%s where id = %s """%(pending_po_depindent_qty,
												pending_stock_depindent_qty,pi_lines[i].depindent_line_id.id)
								cr.execute(sql)
								#indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
								if pending_po_depindent_qty == 0:
									print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
									indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'process'})
								elif pending_po_depindent_qty > 0:
									print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
									indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
							else:
								print "depindent_line_id.id**********3333333333333333333333333333*********", depindent_line_id.id, "pending_po_depindent_qty ======>", pending_po_depindent_qty
								sql = """ update kg_depindent_line set po_qty=%s, pending_qty=%s where id = %s """%(pending_po_depindent_qty,
													pending_stock_depindent_qty,pi_lines[i].depindent_line_id.id)
								cr.execute(sql)
								#indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
								if pending_po_depindent_qty == 0:
									print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
									indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'process'})
								elif pending_po_depindent_qty > 0:
									print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
									indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
					else:
						print "Else PArt =====>product Name::", pi_lines[i].product_id.name, "pi_lines[i] ==>>", pi_lines[i].product_qty,":::", pi_lines[i].product_uom_id.name
						print "pi_used_qty :::", pi_used_qty, "po_uom_qty ::", po_uom_qty
						
						if pi_used_qty > po_uom_qty:
							pending_stock_depindent_qty = 0.0
							pending_po_depindent_qty = 0.0
							print "depindent_line_id.id*******44444444444444444444444444************", depindent_line_id.id, "pending_po_depindent_qty ======>", pending_po_depindent_qty
							sql1 = """ update kg_depindent_line set po_qty=%s, pending_qty=%s where id = %s """%(pending_po_depindent_qty,
										pending_stock_depindent_qty,pi_lines[i].depindent_line_id.id)
							cr.execute(sql1)
							#indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
							if pending_po_depindent_qty == 0:
								print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
								indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'process'})
							elif pending_po_depindent_qty > 0:
								print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
								indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
						else:
							pending_stock_depindent_qty = orig_depindent_qty - pi_used_qty
							pending_po_depindent_qty = po_uom_qty - pi_used_qty
							print "depindent_line_id.id********555555555555555555555555***********", depindent_line_id.id , "pending_po_depindent_qty ======>", pending_po_depindent_qty
							sql1 = """ update kg_depindent_line set po_qty=%s, pending_qty=%s where id = %s """%(pending_po_depindent_qty,
										pending_stock_depindent_qty,pi_lines[i].depindent_line_id.id)
							cr.execute(sql1)
							#indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
							if pending_po_depindent_qty == 0:
								print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
								indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'process'})
							elif pending_po_depindent_qty > 0:
								print "pi_lines[i].pending_qty...............",pi_lines[i].pending_qty
								indent_line_obj.write(cr,uid,depindent_line_id.id, {'line_state' : 'noprocess'})
								
				else:
					if pi_lines[i].group_flag == True:
						self.update_product_group(cr,uid,ids,line=pi_lines[i])
					else:
						print "All are correct Values"
			
			return True
			cr.close()
		
	def tender_cancel(self, cr, uid, ids, context=None):
		print "callled tender_cancel from KG"
		purchase_order_obj = self.pool.get('purchase.order')
		piindent = self.browse(cr, uid, ids[0], context=context)
	
		if piindent.state == 'in_progress':						
			for line in piindent.line_ids:
				if line.product_qty != line.pending_qty:
					raise osv.except_osv(
						_('Unable to cancel this Purchase Indent.'),
						_('First cancel all PO related to this Purchase Indent.'))
				else:
					if line.depindent_line_id and line.group_flag == False:
						orig_pending_qty = line.depindent_line_id.pending_qty
						pi_qty = line.product_qty
						orig_pending_qty += pi_qty
						line.depindent_line_id.write({'pending_qty':orig_pending_qty })
						line.depindent_line_id.write({'line_state':'noprocess' })
					else:
						pass
						# Need to do cancel process if a PI line is product Grouping
		else:
			if piindent.pi_type == 'fromdep':	
				for line in piindent.line_ids:
					line.depindent_line_id.write({'line_state' : 'noprocess'})			
		
		return self.write(cr, uid, ids, {'state': 'cancel'})
		
		
	def pi_approval(self, cr, uid, ids, context=None):
		
		self.write(cr, uid, ids, {'state': 'approved'})
		return True	
			

	def _check_line(self, cr, uid, ids, context=None):
		logger.info('[KG ERP] Class: kg_purchase_indent, Method: _check_line called...')
		for pi in self.browse(cr,uid,ids):
			print "pi.kg_depindent_lines...........", pi.kg_depindent_lines
			if pi.kg_depindent_lines==[]:
				tot = 0.0
				for line in pi.line_ids:
					tot += line.product_qty
					print "tot ===============================>>>>", tot
				if tot <= 0.0:			
					return False
			
			return True
			
	_constraints = [
	
		(_check_line,'You can not save this Purchase Indent with out Line and Zero Qty !',['line_ids']),
	]   	   	
		
kg_purchase_indent()

class kg_purchase_indent_line(osv.osv):
	
	_name = "purchase.requisition.line"
	_inherit = "purchase.requisition.line"
	_rec_name = 'name'
	
	_columns = {
	
	'rate': fields.float('Last Purchase Rate',readonly=True, state={'draft': [('readonly', False)]}),
	'note': fields.text('Remarks'),
	'line_date':fields.datetime('Date'),
	'line_state': fields.selection([('process', 'Approved'),('noprocess', 'Confirmed'),
					('cancel', 'Cancel')], 'Status'),
	'pending_qty': fields.float('Pending Qty'),
	'current_qty':fields.float('Current Stock Quantity'),
	'dep_indent_qty': fields.float('Dep.Indent Qty'),
	'name': fields.char('Name', size=64),
	'depindent_line_id':fields.many2one('kg.depindent.line', 'Dep.Indent Line'),
	'default_uom_id': fields.many2one('product.uom', 'PO.UOM'),
	'po_uom_qty': fields.float('PO.Qty'),
	'group_flag':fields.boolean('Group By'),
	'dep_id':fields.many2one('kg.depmaster', 'Department'),
	'user_id': fields.many2one('res.users', 'Users'),
	'cancel_remark': fields.text('Cancel Remarks'),
	'line_flag':fields.boolean('Line Flag')
	}
	
	_defaults = {
	
	'line_state' : 'process',
	'name': 'PILINE',
	'line_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
	'line_flag':True
	
	}		
	
	def onchange_product_id(self, cr, uid, ids, product_id, product_uom_id, context=None):
		print "callled onchange_product_id from KG"

		value = {'product_uom_id': ''}
		if product_id:
			prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			value = {'product_uom_id': prod.uom_po_id.id}
		return {'value': value}
			
	def onchange_qty(self, cr, uid, ids, product_qty, pending_qty, context=None):
		print "callled onchange_qty from KG"

		value = {'pending_qty': ''}
		if product_qty:
			value = {'pending_qty': product_qty}
		return {'value': value}
		
	def create(self,cr,uid,vals,context={}):
		print "Line create called............"
		if vals['product_id']:
			prod_record = self.pool.get('product.product').browse(cr,uid,vals['product_id'])
			vals.update({'product_uom_id':prod_record.uom_po_id.id})	  
		return super(kg_purchase_indent_line,self).create(cr,uid,vals,context)
		
	def write(self,cr,uid,ids,vals,context={}):
		if vals.has_key('product_id') and vals['product_id']:
			product_record = self.pool.get('product.product').browse(cr,uid,vals['product_id'])
			if product_record.uom_po_id:
					vals.update({'product_uom_id':prod_record.uom_po_id.id})
		return super(kg_purchase_indent_line,self).write(cr,uid,ids,vals,context)		

	def unlink(self, cr, uid, ids, context=None):
		print "kgggggggggggggg line unlike called ids ===", ids
		if context is None:
			context = {}
		for rec in self.browse(cr, uid, ids, context=context):
			print "rec ===================>>>>>", rec, "ids====>", context
			parent_rec = rec.requisition_id
			print "parent_rec.state", parent_rec.state
			if parent_rec.state not in ['draft','in_progress']:
				print "iffffffffffff"
				raise osv.except_osv(_('Invalid Action!'), _('Cannot delete a purchase indent line which is in state \'%s\'.') %(parent_rec.state,))
			else:
				pi_id = parent_rec.id
				dep_line_rec = rec.depindent_line_id				
				dep_line_id = rec.depindent_line_id.id
				dep_line_rec.write({'line_state' : 'noprocess'})
				del_sql = """ delete from kg_depindent_pi_line where pi_id=%s and depindent_line_id=%s """ %(pi_id,dep_line_id)
				cr.execute(del_sql)				
				return super(kg_purchase_indent_line, self).unlink(cr, uid, ids, context=context)
				
	def line_cancel(self, cr, uid, ids, context=None):
		line = self.browse(cr, uid, ids[0])
		print "line........................", line
		if not line.cancel_remark:
			raise osv.except_osv(_('Remarks is must !!'), _('Enter cancel remarks !!!'))
		else:							
			print "depindent_line_id//////////////////"	, line.depindent_line_id
			line.write({'line_state' : 'cancel'})
			#line.depindent_line_id.write({'pi_cancel' : True})
		return True

kg_purchase_indent_line()
