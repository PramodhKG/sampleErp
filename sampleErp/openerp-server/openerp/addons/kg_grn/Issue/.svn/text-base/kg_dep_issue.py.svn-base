from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import logging



class kg_stock_picking(osv.osv):
	
	_inherit = "stock.picking"
	_name = "stock.picking"
	
	_columns = {
	
	'name': fields.char('Dep.Issue.No', size=64, required=True, readonly=True),
	'dep_name': fields.many2one('kg.depmaster','Dep.Name',required=True, translate=True, select=True,
		states={'done':[('readonly', True)], 'cancel':[('readonly',True)], 'assigned':[('readonly',True)]}),
	'date': fields.date('Date', required=True, readonly=True),
	'active': fields.boolean('Active'),
	'user_id' : fields.many2one('res.users', 'User', readonly=False),
	'kg_dep_indent_line':fields.many2many('kg.depindent.line', 'kg_depline_picking', 'kg_depline_id', 'stock_picking_id', 'Department Indent'),
	'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('auto', 'Waiting'),
            ('confirmed', 'Confirmed'),
            ('assigned', 'Waiting for Approval'),
            ('done', 'Done'),
            ('qawaiting', 'QA Waiting'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange'),
	}
	
	def test_finished(self, cr, uid, ids, context=None):
		print "test_finished ---------------- FROM KG Issue stock.picking"
		""" Tests whether the move is in done or cancel state or not.
		@return: True or False
		"""
		move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id', 'in', ids)])
		print "move_ids?????????????????????????????", move_ids
		for move in self.pool.get('stock.move').browse(cr, uid, move_ids):
			if move.state not in ('done', 'cancel'):

				if move.product_qty != 0.0:
					return False
				else:
					move.write({'state': 'done'})
		depindent_line_obj=self.pool.get('kg.depindent.line')
		move_obj=self.pool.get('stock.move')
		for i in range(len(move_ids)):
			move_record=move_obj.browse(cr, uid, move_ids[i], context=context)
			print "move_record::::::::::::::", move_record
			if move_record.depindent_line_id:
				depindent_line_id = move_record.depindent_line_id
				issue_qty = move_record.product_qty
				depindent_line_qty = move_record.po_qty
				depindent_line_pending_qty = depindent_line_qty - issue_qty
				print "depindent_line_id :", depindent_line_id, "=====================po_qty", depindent_line_pending_qty
				depindent_line_obj.write(cr, uid, [move_record.depindent_line_id.id], {'issue_pending_qty' : depindent_line_pending_qty})
		return True
	
	
kg_stock_picking()


class kg_dep_issue(osv.osv):
	
	__name = "stock.picking"
	_inherit="stock.picking.out"
	
	
	_columns = {
	
	'dep_name': fields.many2one('kg.depmaster','Dep.Name',required=True, translate=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),
	'date': fields.date('Date', required=True, readonly=True),
	'active': fields.boolean('Active'),
	'kg_dep_indent_line':fields.many2many('kg.depindent.line', 'kg_depline_picking', 'kg_depline_id', 'stock_picking_id', 'Department Indent', 
		domain="[('indent_id.state','=','done'), '&', ('issue_pending_qty','>','0')]", readonly=True, states={'draft': [('readonly', False)]}),
	'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('auto', 'Waiting'),
            ('confirmed', 'Confirmed'),
            ('assigned', 'Waiting for Approval'),
            ('done', 'Done'),
            ('qawaiting', 'QA Waiting'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange'),
	'stock_journal_id': fields.many2one('stock.journal','Stock Journal', invisible=True),
	'origin': fields.char('Source Document', size=64, invisible=True),
	'user_id' : fields.many2one('res.users', 'User', readonly=False),
 
   	
	}
	
	_defaults = {
	
	'active' : 'True',
	'date' : fields.date.context_today,
	'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,

	
	}
	
	def onchange_user_id(self, cr, uid, ids, user_id, context=None):
		value = {'dep_name': ''}
		if user_id:
			user = self.pool.get('res.users').browse(cr, uid, user_id, context=context)
			value = {'dep_name': user.dep_name.id}
		return {'value': value}
		
	def create(self, cr, uid, vals, context=None):
		
		if vals.has_key('user_id') and vals['user_id']:
			user_dep_name = self.pool.get('res.users').browse(cr,uid,vals['user_id'])
			print "user_dep_name =======================", user_dep_name
			if user_dep_name.dep_name:
				vals.update({'dep_name':user_dep_name.dep_name.id})
		res = super(kg_dep_issue, self).create(cr, uid,vals, context)
		return res
		
	def write(self, cr, uid,ids, vals, context=None):
	
		if vals.has_key('user_id') and vals['user_id']:
			user_dep_name = self.pool.get('res.users').browse(cr,uid,vals['user_id'])
			if user_dep_name.dep_name:
				print "user_dep_name =======================", user_dep_name
				vals.update({'dep_name':user_dep_name.dep_name.id})
						 
		res = super(kg_dep_issue, self).write(cr, uid, ids,vals, context)
		
		return res
	
	
	def draft_force_assign(self, cr, uid, ids, *args):
		print "draft_force_assign ----------------From KG GRN OUT"
		""" Confirms picking directly from draft state.
		@return: True
		"""
		wf_service = netsvc.LocalService("workflow")
		for pick in self.browse(cr, uid, ids):
			if not pick.move_lines:
				raise osv.except_osv(_('Error!'),_('You cannot process empty Dep.Issue.'))
			wf_service.trg_validate(uid, 'stock.picking', pick.id,
				'button_confirm', cr)
		for move in pick.move_lines:
			print "move>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", move
			if move.depindent_line_id and move.product_qty > move.po_qty:
				raise osv.except_osv(_('If Issue from Indent!'),_('You cannot Issue, Qty more than Dep.Indent Qty.'))
				
				
		return True
	
	def update_issue(self,cr,uid,ids,context=False,):
		
		depindent_line_obj = self.pool.get('kg.depindent.line')
		move_obj = self.pool.get('stock.move')
		prod_obj = self.pool.get('product.product')
		line_ids = []			   
		res={}
		line_ids = []
		res['move_lines'] = []
		res['pi_flag'] = True
		obj =  self.browse(cr,uid,ids[0])
		if obj.move_lines:
			move_lines = map(lambda x:x.id,obj.move_lines)
			move_obj.unlink(cr,uid,move_lines)
		if obj.kg_dep_indent_line:
			depindent_line_ids = map(lambda x:x.id,obj.kg_dep_indent_line)
			depindent_line_browse = depindent_line_obj.browse(cr,uid,depindent_line_ids)
			depindent_line_browse = sorted(depindent_line_browse, key=lambda k: k.product_id.id)
			groups = []
			for key, group in groupby(depindent_line_browse, lambda x: x.product_id.id):
				groups.append(map(lambda r:r,group))
			for key,group in enumerate(groups):
				qty = sum(map(lambda x:float(x.qty),group)) #TODO: qty
				depindent_line_ids = map(lambda x:x.id,group)
				prod_browse = group[0].product_id			
				uom =False
				for ele in group:
					uom = (ele.product_id.product_tmpl_id and ele.product_id.product_tmpl_id.uom_id.id) or False
					qty = (ele.issue_pending_qty) or False
					depindent_id= ele.id
					dest_location = ele.dest_location_id.id
					indent_id = ele.indent_id.id
					depindent_obj = self.pool.get('kg.depindent').browse(cr, uid, indent_id)
					src_location = depindent_obj.dep_location.id
					print "src_location :::::::::::::::::::::", src_location


					
					break
					
				vals = {
			
				'product_id':prod_browse.id,
				'product_uom':uom,
				'product_qty':qty,
				'po_qty':qty,
				'name':prod_browse.name,
				'location_id':src_location,
				'location_dest_id':src_location,
				'state' : 'assigned',
				'move_type' : 'out',
				'depindent_line_id' : ele.id,
				}  
				
			
				if ids:
					self.write(cr,uid,ids[0],{'move_lines':[(0,0,vals)]})
				
			if ids:
				if obj.move_lines:
					move_lines = map(lambda x:x.id,obj.move_lines)
					for line_id in move_lines:
						self.write(cr,uid,ids,{'move_lines':[]})
		self.write(cr,uid,ids,res)		
		return True
		
	def action_process(self, cr, uid, ids, context=None):
		print "action_process >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FROM ISSUE"
		
		
		if context is None:
			context = {}
		"""Open the partial picking wizard"""
		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'stock.partial.picking',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}
		
	def test_finished(self, cr, uid, ids):
		""" Tests whether the move is in done or cancel state or not.
		@return: True or False
		"""
		move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id', 'in', ids)])
		for move in self.pool.get('stock.move').browse(cr, uid, move_ids):
			if move.state not in ('done', 'cancel'):

				if move.product_qty != 0.0:
					return False
				else:
					move.write({'state': 'done'})
		return True

	
		
kg_dep_issue()

"""
class kg_issue_stock_move(osv.osv):
	
	_name = "stock.move"
	_inherit = "stock.move"
	
	_columns = {

	'depindent_qty': fields.float('Indent Qty', states={'done':[('readonly', True)], 'cancel':[('readonly',True)], 'assigned':[('readonly',True)]}),
	'expiry_date': fields.date('Expiry Date', states={'done':[('readonly', True)], 'cancel':[('readonly',True)], 'assigned':[('readonly',False)]}),
	'product_qty': fields.float('Issue Qty', digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)], 'assigned':[('readonly',False)]}),
   	
	}
	
		
		
	def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
						  product_uom, product_uos):

		 On change of product quantity finds UoM and UoS quantities
		@param product_id: Product id
		@param product_qty: Changed Quantity of product
		@param product_uom: Unit of measure of product
		@param product_uos: Unit of sale of product
		@return: Dictionary of values

		result = {
				  'product_uos_qty': 0.00
		  }
		warning = {}

		if (not product_id) or (product_qty <=0.0):
			result['product_qty'] = 0.0
			return {'value': result}

		product_obj = self.pool.get('product.product')
		uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])

		# Warn if the quantity was decreased 
		if ids:
			for move in self.read(cr, uid, ids, ['product_qty', 'po_qty']):
				if product_qty > move['po_qty']:
					raise osv.except_osv(
						_('If Issue From Dep Indent'),
						_('Issue Qty should not be greater than Dep.Indent Qty.!!!'))
					break

		if product_uos and product_uom and (product_uom != product_uos):
			result['product_uos_qty'] = product_qty * uos_coeff['uos_coeff']
		else:
			result['product_uos_qty'] = product_qty

		return {'value': result}
	
kg_issue_stock_move()	
"""


