import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from itertools import groupby
import openerp.addons.decimal_precision as dp
import netsvc
import pooler
import logging
logger = logging.getLogger('server')

class kg_service_invoice(osv.osv):

	_name = "kg.service.invoice"
	_description = "KG Service Invoice"
	_order = "date desc"

	
	def _amount_line_tax(self, cr, uid, line, context=None):
		val = 0.0
		new_amt_to_per = line.kg_discount or 0.0 / line.product_qty
		print "new_amt_to_per ---------------;;;;;;>>>>>", new_amt_to_per
		amt_to_per = (line.kg_discount / (line.product_qty * line.price_unit or 1.0 )) * 100
		print "amt_to_per -----------------------;;;;;;>>>>>", amt_to_per
		kg_discount_per = line.kg_discount_per
		tot_discount_per = amt_to_per + kg_discount_per
		for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id,
			line.price_unit * (1-(tot_discount_per or 0.0)/100.0), line.product_qty, line.product_id,
			 line.service_id.partner_id)['taxes']:
			print "c ----------------------******************", c
				 
			val += c.get('amount', 0.0)
		return val
	
	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		cur_obj=self.pool.get('res.currency')
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0,
				'discount' : 0.0,
				'other_charge': 0.0,
			}
			val = val1 = val3 = 0.0
			cur = order.pricelist_id.currency_id
			po_charges=order.value1 + order.value2
			for line in order.service_invoice_line:
				tot_discount = line.kg_discount + line.kg_discount_per_value
				val1 += line.price_subtotal
				val += self._amount_line_tax(cr, uid, line, context=context)
				val3 += tot_discount
			print "po_charges :::", po_charges , "val ::::", val, "val1::::", val1, "val3:::::", val3
			res[order.id]['other_charge']=cur_obj.round(cr, uid, cur, po_charges)
			res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
			res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
			res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] + res[order.id]['other_charge']
			res[order.id]['discount']=cur_obj.round(cr, uid, cur, val3)
			#self.write(cr, uid,order.id, {'other_charge' : po_charges})
			print "res ^^^^^^^^^^^^^,", "amount_total====", res[order.id]['amount_total'], "^^^^^^^^^^^^^^", res
		return res
		
	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('kg.service.invoice.line').browse(cr, uid, ids, context=context):
			result[line.service_id.id] = True
		return result.keys()
	
	
	_columns = {
		'name': fields.char('Service Bill No', size=64,readonly=True, states={'draft': [('readonly', False)]}),
		'dep_name': fields.many2one('kg.depmaster','Dep.Name', translate=True, select=True),
		'date': fields.date('Date', required=True, readonly=True),
		'partner_id':fields.many2one('res.partner', 'Misc Supplier', required=True,readonly=True, 
					states={'draft':[('readonly',False)]}),
		'pricelist_id':fields.many2one('product.pricelist', 'Pricelist'),
		'partner_address':fields.char('Supplier Address', size=128, readonly=True, states={'draft':[('readonly',False)]}),
		'service_invoice_line': fields.one2many('kg.service.invoice.line', 'service_id', 'Order Lines', 
					readonly=True, states={'draft':[('readonly',False)]}),
		'active': fields.boolean('Active'),
		'user_id' : fields.many2one('res.users', 'User', readonly=False),
		'state': fields.selection([('draft', 'Draft'),('confirm','Waiting For Approval'),('approved','Approved'),('done','Done'),('cancel','Cancel')], 'Status', track_visibility='onchange'),
		'payment_mode': fields.selection([('ap','Advance Paid'),('on_receipt', 'On receipt of Goods and acceptance')], 'Mode of Payment', 
					required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'po_expenses_type1': fields.selection([('freight','Freight Charges'),('others','Others')], 'Expenses Type1', 
										readonly=True, states={'draft':[('readonly',False)]}),
		'po_expenses_type2': fields.selection([('freight','Freight Charges'),('others','Others')], 'Expenses Type2', 
								readonly=True, states={'draft':[('readonly',False)]}),
		'value1':fields.float('Value1', readonly=True, states={'draft':[('readonly',False)]}),
		'value2':fields.float('Value2', readonly=True, states={'draft':[('readonly',False)]}),
		'note': fields.text('Remarks'),
		'other_charge': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Other Charges(+)',
			 multi="sums", help="The amount without tax", track_visibility='always'),		
		
		'discount': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total Discount(-)',
			store={
				'kg.service.invoice': (lambda self, cr, uid, ids, c={}: ids, ['service_invoice_line'], 10),
				'kg.service.invoice.line': (_get_order, ['price_unit', 'tax_id', 'kg_discount', 'product_qty'], 10),
			}, multi="sums", help="The amount without tax", track_visibility='always'),
		'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
			store={
				'kg.service.invoice': (lambda self, cr, uid, ids, c={}: ids, ['service_invoice_line'], 10),
				'kg.service.invoice.line': (_get_order, ['price_unit', 'tax_id', 'kg_discount', 'product_qty'], 10),
			}, multi="sums", help="The amount without tax", track_visibility='always'),
		'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Taxes',
			store={
				'kg.service.invoice': (lambda self, cr, uid, ids, c={}: ids, ['service_invoice_line'], 10),
				'kg.service.invoice.line': (_get_order, ['price_unit', 'tax_id', 'kg_discount', 'product_qty'], 10),
			}, multi="sums", help="The tax amount"),
		'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total',
			store=True, multi="sums",help="The total amount"),
		
		'remark': fields.text('Remarks', readonly=True, states={'draft': [('readonly', False)]}),

		
	}
	_sql_constraints = [('code_uniq','unique(name)', 'Service Order number must be unique!')]

	_defaults = {
		'state' : 'draft',
		'active' : 'True',
		'date' : fields.date.context_today,
		'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,

	}
	
	def create(self, cr, uid, vals,context=None):		
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'kg.service.invoice') or '/'
		order =  super(kg_service_invoice, self).create(cr, uid, vals, context=context)
		return order
	
	
	def onchange_partner_id(self, cr, uid, ids, partner_id):
		partner = self.pool.get('res.partner')
		if not partner_id:
			return {'value': {
				'fiscal_position': False,
				'payment_term_id': False,
				}}
		supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
		supplier = partner.browse(cr, uid, partner_id)
		street = supplier.street or ''
		city = supplier.city.name or ''
		address = street+ city or ''

		return {'value': {
			'pricelist_id': supplier.property_product_pricelist_purchase.id,
			'partner_address' : address,
			}}
			
	def button_dummy(self, cr, uid, ids, context=None):
		return True
	
	
	def draft_order(self, cr, uid, ids,context=None):
		"""
		Draft Order
		"""
		self.write(cr,uid,ids,{'state':'draft'})
		return True
		
	def confirm_order(self, cr, uid, ids,context=None):
		"""
		Service Order Confirm
		"""
		for t in self.browse(cr,uid,ids):
			if not t.service_invoice_line:
				raise osv.except_osv(
						_('Empty Service Bill'),
						_('You can not confirm an empty Service Bill'))
			print "t.dep_order_line,,,,,,,,,,,,,,,,,", t.service_invoice_line
			for line in t.service_invoice_line:
				print "line ==========================>>", line
				if line.product_qty==0:
					raise osv.except_osv(
					_('Error'),
					_('Service invoice quantity can not be zero'))			
					
			self.write(cr,uid,ids,{'state':'confirm'})
			return True
			
	def approve_order(self, cr, uid, ids,context=None):
		
		self.write(cr,uid,ids,{'state':'approved'})
		return True		
	
		
	def cancel_order(self, cr, uid, ids, context=None):
		"""
		Cancel order
		"""
		
		self.write(cr, uid,ids,{'state' : 'cancel'})
		return True

		
	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		indent = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for t in indent:
			if t['state'] in ('draft'):
				unlink_ids.append(t['id'])
			else:
				raise osv.except_osv(_('Invalid action !'), _('System not allow to delete a UN-DRAFT state Service Order !!'))
		indent_lines_to_del = self.pool.get('kg.service.invoice.line').search(cr, uid, [('service_id','in',unlink_ids)])
		self.pool.get('kg.service.invoice.line').unlink(cr, uid, indent_lines_to_del)
		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		return True

		
	def onchange_user_id(self, cr, uid, ids, user_id, context=None):
		value = {'dep_name': ''}
		if user_id:
			user = self.pool.get('res.users').browse(cr, uid, user_id, context=context)
			value = {'dep_name': user.dep_name.id}
		return {'value': value}		
	
	
			
	def so_direct_print(self, cr, uid, ids, context=None):
		assert len(ids) == 1, 'This option should only be used for a single id at a time'
		wf_service = netsvc.LocalService("workflow")
		wf_service.trg_validate(uid, 'kg.service.order', ids[0], 'send_rfq', cr)
		datas = {
				 'model': 'kg.service.order',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'service.order.report', 'datas': datas, 'nodestroy': True}
		
			
	
	## The below part for create SO bill from SO ##
	
	def get_currency_id(self, cr, uid, so):
		return False
	
	def _invoice_line_hook(self, cr, uid, sol, invoice_line_id):
		return
		
	def _invoice_hook(self, cr, uid, so, invoice_id):
		return
		
	def _get_taxes_invoice(self, cr, uid, sol, type):
		
		if type in ('in_invoice', 'in_refund'):
			taxes = sol.taxes_id
		else:
			taxes = False

		if sol.service_id and sol.service_id.partner_id and sol.service_id.partner_id.id:
			return self.pool.get('account.fiscal.position').map_tax(
				cr,
				uid,
				sol.service_id.partner_id.property_account_position,
				taxes
			)
		else:
			return map(lambda x: x.id, taxes)	
	
		

kg_service_invoice()

class kg_service_invoice_line(osv.osv):
	
	_name = "kg.service.invoice.line"
	_description = "Service invoice"
	
	def onchange_discount_value_calc(self, cr, uid, ids, kg_discount_per, product_qty, price_unit):
		discount_value = (product_qty * price_unit) * kg_discount_per / 100
		print "discount_value ---------------------", discount_value
		return {'value': {'kg_discount_per_value': discount_value}}

	def onchange_product_id(self, cr, uid, ids, product_id, product_uom,context=None):
			
		value = {'product_uom': ''}
		if product_id:
			prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			value = {'product_uom': prod.uom_id.id}
		return {'value': value}
	
		
	def _amount_line(self, cr, uid, ids, prop, arg, context=None):
		cur_obj=self.pool.get('res.currency')
		tax_obj = self.pool.get('account.tax')
		res = {}
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			amt_to_per = (line.kg_discount / (line.product_qty * line.price_unit or 1.0 )) * 100
			kg_discount_per = line.kg_discount_per
			tot_discount_per = amt_to_per + kg_discount_per
			price = line.price_unit * (1 - (tot_discount_per or 0.0) / 100.0)
			taxes = tax_obj.compute_all(cr, uid, line.taxes_id, price, line.product_qty, line.product_id, line.service_id.partner_id)
			cur = line.service_id.pricelist_id.currency_id
			res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
		return res
	
	
	
	_columns = {

	'service_id': fields.many2one('kg.service.invoice', 'Service.order.NO', required=True, ondelete='cascade'),
	'price_subtotal': fields.function(_amount_line, string='Linetotal', digits_compute= dp.get_precision('Account')),
	'product_id': fields.many2one('product.product', 'Product',required=True,domain=[('type','=','service')]),
	'product_uom': fields.many2one('product.uom', 'UOM', required=True),
	'product_qty': fields.float('Quantity', required=True),
	'soindent_qty':fields.float('SOIndent Qty'),
	'pending_qty':fields.float('Pending Qty'),
	'taxes_id': fields.many2many('account.tax', 'service_invoice_tax', 'tax_id','line_id', 'Taxes'),
	'soindent_line_id':fields.many2one('kg.service.indent.line', 'Indent Line'),
	'kg_discount': fields.float('Discount Amount', digits_compute= dp.get_precision('Discount')),
	'kg_disc_amt_per': fields.float('Disc Amt(%)', digits_compute= dp.get_precision('Discount')),
	'price_unit': fields.float('Unit Price', digits_compute= dp.get_precision('Product Price')),
	'kg_discount_per': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
	'kg_discount_per_value': fields.float('Discount(%)Value', digits_compute= dp.get_precision('Discount')),
	'note': fields.text('Remarks'),
	
	
	}
	
	def onchange_disc_amt(self, cr, uid, ids, kg_discount,product_qty,price_unit,kg_disc_amt_per):
		print "idssssssssssssssssss", ids
		if kg_discount:
			print "kg_discount..........", 
			kg_discount = kg_discount + 0.00
			amt_to_per = (kg_discount / (product_qty * price_unit or 1.0 )) * 100
			print "amt_to_peramt_to_peramt_to_per", amt_to_per
			return {'value': {'kg_disc_amt_per': amt_to_per}}
		else:
			return {'value': {'kg_disc_amt_per': 0.0}}
		
	
kg_service_invoice_line()	
