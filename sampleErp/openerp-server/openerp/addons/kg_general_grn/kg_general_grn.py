import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
import datetime
import calendar
from datetime import date
import re
import urllib
import urllib2
import logging
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import calendar
today = datetime.now()

class kg_general_grn(osv.osv):

	_name = "kg.general.grn"
	_description = "General GRN Provision"

			
	_columns = {
		'name': fields.char('GRN NO',readonly=True),
		'creation_date':fields.date('Creation Date',required=True,readonly=True),
		
		'grn_date':fields.date('GRN Date',required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'supplier_id':fields.many2one('res.partner','Supplier',domain=[('supplier','=',True)],required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'dc_no': fields.char('DC NO', required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'dc_date':fields.date('DC Date',required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'bill': fields.selection([
			('applicable', 'Applicable'),
			('not_applicable', 'Not Applicable')], 'Bill',required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'user_id':fields.many2one('res.users','Created By',readonly=True),
		'grn_line':fields.one2many('kg.general.grn.line','grn_id','Line Entry'),
		'other_charge': fields.float('Other Charges',readonly=True, states={'draft':[('readonly',False)]}),
		'amount_total': fields.float('Total Amount',readonly=True),
			 
		'sub_total': fields.float('Line Total',readonly=True),
		'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')], 'Status',readonly=True),
		'expiry_flag':fields.boolean('Expiry Flag'),
		'dep_name': fields.many2one('kg.depmaster','Department',readonly=True, states={'draft':[('readonly',False)]}),
		'remark':fields.text('Remarks'),
	}
	
	def create(self, cr, uid, vals,context=None):
		print "vals..............................",vals	
		if vals.get('name',False)==False:
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'kg.general.grn') or False
		grn =  super(kg_general_grn, self).create(cr, uid, vals, context=context)
		return grn
		
		
	def onchange_user_id(self, cr, uid, ids, user_id, context=None):
		
		value = {'dep_name': ''}
		if user_id:
			user = self.pool.get('res.users').browse(cr, uid, user_id, context=context)
			value = {'dep_name': user.dep_name.id}
		return {'value': value}
		
		
	def kg_grn_confirm(self, cr, uid, ids,context=None):
		grn_entry = self.browse(cr, uid, ids[0])
		exp_grn_qty = 0
		
		for line in grn_entry.grn_line:
			product_id = line.product_id.id
			pro_rec = self.pool.get('product.product').browse(cr, uid, product_id)
			if pro_rec.expiry == True:
				if not line.exp_batch_id:
					raise osv.except_osv(_('Warning!'), _('You should specify Expiry date and batch no for this item!!'))
			
				
			
			if line.exp_batch_id:
				for exp_line in line.exp_batch_id:
					exp_grn_qty += exp_line.product_qty
					
					if exp_grn_qty > line.grn_qty:
						raise osv.except_osv(_('Please Check!'), _('Quantity should not exceed than GRN Quantity !!'))
					
			line.write({'state':'confirmed'})
		self.write(cr,uid,ids[0],{'state':'confirmed'})
						
		
		return True
		
		
	def kg_grn_approve(self, cr, uid, ids,context=None):
		user_id = self.pool.get('res.users').browse(cr, uid, uid)
		print "user_id................................>>>>",user_id.name
		grn_entry = self.browse(cr, uid, ids[0])
		lot_obj = self.pool.get('stock.production.lot')
		self.write(cr,uid,ids[0],{'state':'done'})
		stock_move_obj=self.pool.get('stock.move')
		dep_obj = self.pool.get('kg.depmaster')
		dep_id = grn_entry.dep_name.id
		dep_record = dep_obj.browse(cr,uid,dep_id)
		dest_location_id = dep_record.main_location.id 
		print "dep_record:::::::::::", dep_record, ids
		line_tot = 0
		for line in grn_entry.grn_line:
			print "lines............................",line.id
			# This code will create General GRN to Stock Move
			stock_move_obj.create(cr,uid,
				{
				
				'general_grn_id':line.id,
				'product_id': line.product_id.id,
				'name':line.product_id.name,
				'product_qty': line.grn_qty,
				'po_to_stock_qty':line.grn_qty,
				'stock_uom':line.uom_id.id,
				'product_uom': line.uom_id.id,
				'location_id': grn_entry.supplier_id.property_stock_supplier.id,
				'location_dest_id': dest_location_id,
				'move_type': 'in',
				'state': 'confirmed',
				'price_unit': line.price_unit or 0.0,
				'origin':'General GRN',
				'stock_rate':line.price_unit or 0.0,
				})
				
				
			grn_price = line.grn_qty * line.price_unit
			print "grn_price.......................>>>",grn_price
			line.write({'line_total':grn_price})
			line.write({'state':'done'})
			line_tot += grn_price
			print "line_total......................>>>>>>",line_tot
			
			
			# This code will create Production lot
			if line.exp_batch_id:
				print "sssssssssssssssss"
				for exp in line.exp_batch_id:
					print "exp................................",exp
					lot_obj.create(cr,uid,
							
						{
						
						'grn_no':line.grn_id.name,
						'product_id':line.product_id.id,
						'product_uom':line.uom_id.id,
						'product_qty':exp.product_qty,
						'pending_qty':exp.product_qty,
						'issue_qty':exp.product_qty,
						'batch_no':exp.batch_no,
						'expiry_date':exp.exp_date,
						'price_unit':line.price_unit or 0.0,
						'po_uom':line.uom_id.id,
						#'po_qty':move_record.po_to_stock_qty,
					})
						
			else:
				print "nnnnnnnnnnnnnnnnn"
				lot_obj.create(cr,uid,
							
					{
					
					'grn_no':line.grn_id.name,
					'product_id':line.product_id.id,
					'product_uom':line.uom_id.id,
					'product_qty':line.grn_qty,
					'pending_qty':line.grn_qty,
					'issue_qty':line.grn_qty,
					#'batch_no':exp.batch_no,
					#'expiry_date':exp.exp_date,
					'price_unit':line.price_unit or 0.0,
					'po_uom':line.uom_id.id,
					#'po_qty':move_record.po_to_stock_qty,
				})
				
		tot_amt = line_tot + grn_entry.other_charge
		self.write(cr,uid,ids[0],{'sub_total':line_tot,'amount_total':tot_amt})
				
		return True
		
	def grn_cancel(self, cr, uid, ids, context=None):
		grn = self.browse(cr, uid, ids[0])
		print "grn........................", grn
		if not grn.remark:
			raise osv.except_osv(_('Remarks is must !!'), _('Enter Remarks for GRN Cancel !!!'))
		else:
			self.write(cr, uid, ids[0], {'state' : 'cancel'})
		return True
		
	_defaults = {
	
		'creation_date':fields.date.context_today,
		'user_id': lambda obj, cr, uid, context: uid,
		'bill':'not_applicable',
		'state':'draft',
		'grn_date':fields.date.context_today,
		'dc_date':fields.date.context_today,
		
	}
	
	
	def _check_lineqty(self, cr, uid, ids, context=None):
		print "called _check_lineqty ___ function"
		grn = self.browse(cr, uid, ids[0])
		for line in grn.grn_line:
			if line.grn_qty <= 0:
				return False
			else:
				return True
		
	   
					
	def _check_lineprice(self, cr, uid, ids, context=None):
		print "called _check_lineprice ___ function"
		grn = self.browse(cr, uid, ids[0])
		for line in grn.grn_line:
			if line.price_unit <= 0:
				return False
			else:
				return True
				
	def _grndate_validation(self, cr, uid, ids, context=None):
		rec = self.browse(cr, uid, ids[0])
		print "rec...................", rec
		today = date.today()
		print "today................", type(today), today		
		grn_date = datetime.strptime(rec.grn_date,'%Y-%m-%d').date()
		print "rec.grn_date...........", type(grn_date), grn_date
		if grn_date > today:
			return False
		return True
		
	def _dcdate_validation(self, cr, uid, ids, context=None):
		rec = self.browse(cr, uid, ids[0])
		print "rec...................", rec
		today = date.today()
		print "today................", type(today), today		
		dc_date = datetime.strptime(rec.dc_date,'%Y-%m-%d').date()
		print "rec.grn_date...........", type(dc_date), dc_date
		if dc_date > today:
			return False
		return True
		
					
	def unlink(self, cr, uid, ids, context=None):		
		grn_rec = self.browse(cr, uid, ids[0])
		if grn_rec.state != 'draft':
			raise osv.except_osv(_('Invalid action !'), _('System not allow to delete Confirmed and Done state GRN !!'))
		else:
			return True
			
			
	
			
	def expiry_alert(self, cr, uid, ids, context=None):
		
		now = time.strftime("%Y-%m-%d")
		cr.execute(""" select id,grn_line_id,product_qty,exp_date,batch_no from kg_exp_batch """)
		data = cr.dictfetchall()
		print "data",data
		value_data = []
		rep=[]
		new_list = []
		for item in data:
			now = time.strftime("%Y-%m-%d")
			print "now",now
			
			
			# Product Name
			grn_line_rec = self.pool.get('kg.general.grn.line').browse(cr, uid, item['grn_line_id'])
			
			product_name = grn_line_rec.product_id.name_template
			print "grn_record",grn_line_rec.grn_id
			grn_no = grn_line_rec.grn_id.name
			
			exp_date = item['exp_date']
			exp_day = datetime.strptime(exp_date, "%Y-%m-%d")
			today = datetime.strptime(now, "%Y-%m-%d")
			print "exp_rec.exp_date",exp_day,type(exp_day)
			
			pre_day = exp_day - timedelta(hours=24)
			print "pre_day of exp_day",pre_day
			print "today............",today
			if pre_day == today:
				
				print "sssssssssss",item['exp_date']
				rep=[product_name,grn_no,item['exp_date'],item['batch_no']]
				value_data.append(rep)
		print "new_list----------->>>>>>",value_data
		return value_data
		
					
					
					
	_constraints = [
		(_check_lineqty, 'You can not save an GRN with 0 product qty!!',['grn_qty']),
		(_check_lineprice, 'You can not save an GRN with 0 price_unit!!',['price_unit']),
		(_grndate_validation, 'GRN date should not be greater than current date !!',['grn_date']),
		(_dcdate_validation, 'DC date should not be greater than current date !!',['dc_date']),
		]
	
	
	
	
	

kg_general_grn()




class kg_general_grn_line(osv.osv):

	_name = "kg.general.grn.line"
	_description = "General GRN Provision Line"

	
		
		
	_columns = {
		
		'grn_id':fields.many2one('kg.general.grn','GRN Entry'),
		'product_id':fields.many2one('product.product','Item Name',required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'uom_id':fields.many2one('product.uom','UOM',readonly=True, states={'draft':[('readonly',False)]}),
		'grn_qty':fields.integer('Quantity',required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'price_unit':fields.float('Price Unit',required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'line_total': fields.float('Amount',readonly=True, states={'draft':[('readonly',False)]}),
		'exp_batch_id':fields.one2many('kg.exp.batch','grn_line_id','Exp Batch No',readonly=True, states={'draft':[('readonly',False)]}),
		'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'),('done', 'Done'), ('cancel', 'Cancelled')], 'Status',readonly=True),
		'cancel_remark':fields.text('Cancel Remarks'),
		
		
	}
	
	_defaults = {
	
		'state':'draft',
		
		
	}
	
	def onchange_uom_id(self, cr, uid, ids, product_id, context=None):
		
		value = {'uom_id': ''}
		if product_id:
			pro_rec = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			value = {'uom_id': pro_rec.uom_id.id,'price_unit':pro_rec.standard_price}
		return {'value': value}	
	
	def create(self, cr, uid, vals,context=None):
		print "vals..............................",vals	
		if vals.has_key('product_id') and vals['product_id']:
			product_rec = self.pool.get('product.product').browse(cr,uid,vals['product_id'])
			if product_rec:
				vals.update({'uom_id':product_rec.uom_id.id})
		grn_line =  super(kg_general_grn_line, self).create(cr, uid, vals, context=context)
		return grn_line
		
	def grn_line_cancel(self, cr, uid, ids, context=None):
		grn_line = self.browse(cr, uid, ids[0])
		print "grn_line........................", grn_line
		if not grn_line.cancel_remark:
			raise osv.except_osv(_('Remarks is must !!'), _('Enter Cancel Remarks for GRN Line Cancel !!!'))
		else:
			self.write(cr, uid, ids[0], {'state' : 'cancel'})
		return True

kg_general_grn_line()


class kg_exp_batch(osv.osv):

	_name = "kg.exp.batch"
	_description = "Expiry Date and Batch NO"

	
	_columns = {
		
		'grn_line_id':fields.many2one('kg.general.grn.line','GRN Entry Line'),
		'exp_date':fields.date('Expiry Date'),
		'batch_no':fields.char('Batch No'),
		'product_qty':fields.integer('Product Qty'),
		
		
	}
	
	
	
kg_exp_batch()










