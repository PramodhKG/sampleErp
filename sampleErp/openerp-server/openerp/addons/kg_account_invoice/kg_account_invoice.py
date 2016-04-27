import time
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions
from datetime import date
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _


class kg_account_invoice(osv.osv):
	
	_name = "account.invoice"
	_inherit="account.invoice"
	
	
	def _amount_line_tax(self, cr, uid, line, context=None):
		val = 0.0
		amt_to_per = (line.kg_disc_amt / (line.quantity * line.price_unit or 1.0 )) * 100
		disc_per = line.discount
		tot_discount = amt_to_per + disc_per
		for c in self.pool.get('account.tax').compute_all(cr, uid, line.invoice_line_tax_id,
			line.price_unit * (1-(tot_discount or 0.0)/100.0), line.quantity, line.product_id,
				line.invoice_id.partner_id)['taxes']:
				 
			val += c.get('amount', 0.0)
			print "val ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", val
		return val
	
	def _amount_all(self, cr, uid, ids, name, args, context=None):
		res = {}
		for invoice in self.browse(cr, uid, ids, context=context):
			res[invoice.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0,
				'other_charge':0.0,
				'tot_discount' : 0.0,
			}
			val = 0.0
			val1 = 0.0
			for line in invoice.invoice_line:
				res[invoice.id]['amount_untaxed'] += line.price_subtotal
				amt_to_per = (line.kg_disc_amt / (line.quantity * line.price_unit or 1.0 )) * 100
				tot_discount = amt_to_per + line.discount
				tot_disc_amt = (line.quantity * line.price_unit * tot_discount) / 100
				val1 += self._amount_line_tax(cr, uid, line, context=context)
				val += tot_disc_amt
			for line in invoice.tax_line:
				res[invoice.id]['amount_tax'] += val1			
			res[invoice.id]['other_charge'] = invoice.value1 + invoice.value2
			res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
			res[invoice.id]['amount_total'] += res[invoice.id]['other_charge']
			res[invoice.id]['tot_discount'] = val
		return res
		
	def _get_invoice_line(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
			result[line.invoice_id.id] = True
		return result.keys()

	def _get_invoice_tax(self, cr, uid, ids, context=None):
		result = {}
		for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
			result[tax.invoice_id.id] = True
		return result.keys()
		
	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
			result[line.invoice_id.id] = True
		return result.keys()
		
	
	_columns = {
	
	'po_id': fields.many2one('purchase.order','PO NO',select=True, readonly=True,states={'draft':[('readonly',False)]}),
	'grn_id': fields.many2one('stock.picking','GRN NO',readonly=True, states={'draft':[('readonly',False)]}),
	'sup_inv_date': fields.date('Supplier Invoice Date',readonly=True, states={'proforma':[('readonly',False)]}),
	'supplier_invoice_number': fields.char('Supplier Invoice Number', size=64, readonly=True, states={'proforma':[('readonly',False)]}),
	'po_expenses_type1': fields.selection([('freight','Freight Charges'),('others','Others')],
			'Expenses Type1', readonly=True, states={'draft':[('readonly',False)]}),
	'po_expenses_type2': fields.selection([('freight','Freight Charges'),('others','Others')],
			'Expenses Type2', readonly=True, states={'draft':[('readonly',False)]}),
	'value1':fields.float('Value1', readonly=True, states={'draft':[('readonly',False)]}),
	'value2':fields.float('Value2', readonly=True, states={'draft':[('readonly',False)]}),
	'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Subtotal', track_visibility='always',
			store={
				'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
				'account.invoice.tax': (_get_invoice_tax, None, 20),
				'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
			},
			multi='all'),
	'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
			store={
				'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
				'account.invoice.tax': (_get_invoice_tax, None, 20),
				'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
			},
			multi='all'),
	'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
			store={
				'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
				'account.invoice.tax': (_get_invoice_tax, None, 20),
				'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
			},
			multi='all'),
			
	'other_charge': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Other Charges(+)', track_visibility='always',
			store={
				'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
				'account.invoice.tax': (_get_invoice_tax, None, 20),
				'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
			},
			multi='all'),
			
	'tot_discount': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total Discount(-)', track_visibility='always',
			store={
				'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
				'account.invoice.tax': (_get_invoice_tax, None, 20),
				'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
			},
			multi='all'),
	'state': fields.selection([
			('draft','Draft'),
			('proforma','Waiting For Confirmation'),
			('proforma2','Waiting For Approval'),
			('open','Open'),
			('paid','Paid'),
			('cancel','Cancelled'),
			],'Status', select=True, readonly=True, track_visibility='onchange'),
			
	'inv_confirm_date': fields.date('Confirm Date', readonly=True),
	'inv_approve_date':fields.date('Approved Date', readonly=True),
	'bill_type': fields.selection([('cash','Cash Bill'),('credit','Credit Bill')], 'Bill Type', 
				readonly=True, states={'proforma':[('readonly',False)]}),
	'approved_by': fields.many2one('res.users', 'Approved By', readonly=True),
	'confirmed_by': fields.many2one('res.users', 'Confirmed By',readonly=True),
	'po_date':fields.date('PO Date',readonly=True),
	'grn_date':fields.date('GRN Date',readonly=True),
	'department':fields.many2one('kg.depmaster','Department',readonly=True),
	
	}
	
	
	def confirm_pobill(self, cr, uid, ids,context=None):
		today = date.today()
		bill_rec = self.browse(cr,uid, ids[0])
		po_obj=self.pool.get('purchase.order.line')
		
		print "bill_rec...............",bill_rec
		if bill_rec.invoice_line:
			for lines in bill_rec.invoice_line:
				po_rec=po_obj.browse(cr,uid,lines.poline_id)
				po_rec.write({'line_bill': False})		
		print "Confirm -- today ----------------->>", today
		print "user -confirm----id ------------------>>", uid
		self.write(cr,uid,ids,{'state':'proforma2', 'inv_confirm_date': today, 'confirmed_by' : uid})
		return True
		
	def approve_pobill(self, cr, uid, ids,context=None):
		today = date.today()
		print "Approve -- today ----------------->>", today
		print "user -Approve----id ------------------>>", uid	
		self.write(cr,uid,ids,{'state':'open', 'inv_approve_date': today, 'approved_by' : uid})
		return True
	
kg_account_invoice()

class kg_account_invoice_line(osv.osv):
	
	_name = "account.invoice.line"
	_inherit="account.invoice.line"
	
	def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		for line in self.browse(cr, uid, ids):
			amt_to_per = (line.kg_disc_amt / (line.quantity * line.price_unit or 1.0 )) * 100
			discount = amt_to_per + line.discount
			price = line.price_unit * (1-(discount or 0.0)/100.0)
			taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			res[line.id] = taxes['total']
			if line.invoice_id:
				cur = line.invoice_id.currency_id
				res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
		return res
	
	
	_columns = {
	
	'price_subtotal': fields.function(_amount_line, string='Amount', type="float",
			digits_compute= dp.get_precision('Account'), store=True),
	'kg_disc_amt':fields.float('Discount Amt'),
	'poline_id':fields.integer('poline_id'),
	}
	
kg_account_invoice_line()
