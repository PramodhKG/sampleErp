from datetime import *
import time
from osv import fields, osv
from tools.translate import _
import netsvc
import decimal_precision as dp
from itertools import groupby
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
import smtplib
import socket
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import logging
import netsvc
logger = logging.getLogger('server')


class kg_purchase_order(osv.osv):
	
	def _amount_line_tax(self, cr, uid, line, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: _amount_line_tax called...')
		val = 0.0
		new_amt_to_per = line.kg_discount / line.product_qty
		amt_to_per = (line.kg_discount / (line.product_qty * line.price_unit or 1.0 )) * 100
		print "amt_to_per::::::::::::::::::", amt_to_per
		print "amt_to_per::::::::::::::::::", new_amt_to_per
		kg_discount_per = line.kg_discount_per
		print "kg_discount_per::::::::::::::::::", kg_discount_per
		tot_discount_per = amt_to_per + kg_discount_per
		print "tot_discount_per::::::::::::::::::", tot_discount_per
		for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id,
			line.price_unit * (1-(tot_discount_per or 0.0)/100.0), line.product_qty, line.product_id,
				line.order_id.partner_id)['taxes']:
				 
			val += c.get('amount', 0.0)
		return val
	
	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: _amount_all called...')
		res = {}
		cur_obj=self.pool.get('res.currency')
		for order in self.browse(cr, uid, ids, context=context):
			print "order <<<<<<<<<<<>>>>>>>>:::::::", order
			res[order.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0,
				'discount' : 0.0,
				'other_charge': 0.0,
			}
			val = val1 = val3 = 0.0
			cur = order.pricelist_id.currency_id
			for line in order.order_line:
				print "line.price_subtotal++++++++++++++++++++++++++++++++", line.price_subtotal
				tot_discount = line.kg_discount + line.kg_discount_per_value
				val1 += line.price_subtotal
				#for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, order.partner_id)['taxes']:
				val += self._amount_line_tax(cr, uid, line, context=context)
				val3 += tot_discount
			po_charges=order.value1 + order.value2
			print "po_charges :::", po_charges , "val ::::", val, "val1::::", val1, "val3:::::", val3
			print "res[order.id] ===================>>>", res[order.id]
			#res[order.id]['other_charge']=cur_obj.round(cr, uid, cur, po_charges)
			res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
			res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
			res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] + res[order.id]['other_charge']
			res[order.id]['discount']=cur_obj.round(cr, uid, cur, val3)
			self.write(cr, uid,order.id, {'other_charge' : po_charges})
		print "res ^^^^^^^^^^^^^,", "amount_total====", res[order.id]['amount_total'], "^^^^^^^^^^^^^^", res
		return res
		
	def _get_order(self, cr, uid, ids, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: _get_order called...')
		result = {}
		for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
			print "line =============================>>>>", line
			result[line.order_id.id] = True
		return result.keys()

	_name = "purchase.order"
	_inherit = "purchase.order"
	_columns = {
		
		'po_type': fields.selection([('direct', 'Direct'),('frompi', 'From PI')], 'PO Type'),
		'bill_type': fields.selection([('cash','Cash Bill'),('credit','Credit Bill')], 'Bill Type', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'po_expenses_type1': fields.selection([('freight','Freight Charges'),('others','Others')], 'Expenses Type1', readonly=True, states={'draft':[('readonly',False)]}),
		'po_expenses_type2': fields.selection([('freight','Freight Charges'),('others','Others')], 'Expenses Type2', readonly=True, states={'draft':[('readonly',False)]}),
		'other_charge': fields.float('Other Charges(+)',readonly=True),
		'value1':fields.float('Value1', readonly=True, states={'draft':[('readonly',False)]}),
		'value2':fields.float('Value2', readonly=True, states={'draft':[('readonly',False)]}),
		'note': fields.text('Remarks'),
		'vendor_bill_no': fields.float('Vendor.Bill.No', readonly=True, states={'draft':[('readonly',False)]}),
		'vendor_bill_date': fields.date('Vendor.Bill.Date', readonly=True, states={'draft':[('readonly',False)]}),
		'location_id': fields.many2one('stock.location', 'Destination', required=True, domain=[('usage','=','internal')], states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]} ),
		'kg_poindent_lines':fields.many2many('purchase.requisition.line','kg_poindent_po_line' , 'po_order_id', 'piline_id','POIndent Lines',
			domain="[('requisition_id.state','=','in_progress'),'&',('pending_qty','>','0'), '&',('line_state','!=','process')]", 
			readonly=True, states={'draft': [('readonly', False)]}),
		'payment_term_id': fields.many2one('account.payment.term', 'Payment Term', readonly=True, states={'draft':[('readonly',False)]}),
		'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}, help="The pricelist sets the currency used for this purchase order. It also computes the supplier price for the selected products/quantities."),
		'invoice_method': fields.selection([('picking','Based on incoming shipments'), ('other','shipments')], 'Invoicing Control',
			readonly=True, states={'draft':[('readonly',False)], 'sent':[('readonly',False)]}),
		'date_order': fields.date('Date', readonly=True),
		'payment_mode': fields.selection([('ap','Advance Paid'),('on_receipt', 'On receipt of Goods and acceptance')], 'Mode of Payment', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'delivery_type':fields.many2one('kg.deliverytype.master', 'Delivery Schedule', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'delivery_mode': fields.selection([('direct','Direct'),('door','DOOR DELIVERY')], 'Mode of delivery', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'partner_address':fields.char('Supplier Address', size=128, readonly=True, states={'draft':[('readonly',False)]}),
		'email':fields.char('Contact Email', size=128, readonly=True, states={'draft':[('readonly',False)]}),
		
		'discount': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total Discount(-)',
			store={
				'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'kg_discount', 'product_qty'], 10),
			}, multi="sums", help="The amount without tax", track_visibility='always'),
		'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
			store={
				'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'kg_discount', 'product_qty'], 10),
			}, multi="sums", help="The amount without tax", track_visibility='always'),
		'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Taxes',
			store={
				'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'kg_discount', 'product_qty'], 10),
			}, multi="sums", help="The tax amount"),
		'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total',
			store={
				'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'kg_discount', 'product_qty'], 10),
				
			}, multi="sums",help="The total amount"),
		'po_flag': fields.boolean('PO Flag'),
		'grn_flag': fields.boolean('GRN'),

   		
	
	}
	
	_defaults = {
	
	'bill_type' :'credit',
	'date_order': fields.date.context_today,
	'po_type': 'frompi'
	}
	
	def onchange_partner_id(self, cr, uid, ids, partner_id):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: onchange_partner_id called...')
		partner = self.pool.get('res.partner')
		if not partner_id:
			return {'value': {
				'fiscal_position': False,
				'payment_term_id': False,
				}}
		supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
		supplier = partner.browse(cr, uid, partner_id)
		street = supplier.street
		city = supplier.city
		address = street+ city

		return {'value': {
			'pricelist_id': supplier.property_product_pricelist_purchase.id,
			'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
			'payment_term_id': supplier.property_supplier_payment_term.id or False,
			'email' : supplier.email or False,
			'partner_address' : address or False,
			}}
			
		

	def update_poline(self,cr,uid,ids,context=False):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: update_poline called...')
		"""
		Purchase order line should be created from purchase indent while click on update to PO Line button
		"""
		poindent_line_obj = self.pool.get('purchase.requisition.line')
		po_line_obj = self.pool.get('purchase.order.line')
		prod_obj = self.pool.get('product.product')
		order_line = []			   
		res={}
		order_line = []
		res['order_line'] = []
		res['po_flag'] = True
		obj =  self.browse(cr,uid,ids[0])
		if obj.order_line:
			order_line = map(lambda x:x.id,obj.order_line)
			po_line_obj.unlink(cr,uid,order_line)
		if obj.kg_poindent_lines:
			poindent_line_ids = map(lambda x:x.id,obj.kg_poindent_lines)
			poindent_line_browse = poindent_line_obj.browse(cr,uid,poindent_line_ids)
			poindent_line_browse = sorted(poindent_line_browse, key=lambda k: k.product_id.id)
			groups = []
			for key, group in groupby(poindent_line_browse, lambda x: x.product_id.id):
				groups.append(map(lambda r:r,group))
			for key,group in enumerate(groups):
				qty = sum(map(lambda x:float(x.product_qty),group)) #TODO: qty
				poindent_line_ids = map(lambda x:x.id,group)
				prod_browse = group[0].product_id			
				uom =False
				for ele in group:
					#pi_line_id=poindent_line_browse[0].id
					uom = (ele.product_id.product_tmpl_id and ele.product_id.product_tmpl_id.uom_id.id) or False
					qty = (ele.pending_qty) or False
					po_pi_id = ele.id
					po_uom = (ele.product_uom_id.id) or uom
					break
					
				vals = {
			
				'product_id':prod_browse.id,
				'product_uom':po_uom,
				'product_qty':qty,
				'pending_qty':qty,
				'pi_qty':qty,
				'pi_line_id':po_pi_id,
				'price_unit' : 0.0
				
				
				}
				poindent_line_obj.write(cr,uid,ele.id,{'line_state' : 'process'})
				if ids:
					self.write(cr,uid,ids[0],{'order_line':[(0,0,vals)]})
				
			if ids:
				if obj.order_line:
					order_line = map(lambda x:x.id,obj.order_line)
					for line_id in order_line:
						self.write(cr,uid,ids,{'order_line':[]})
		self.write(cr,uid,ids,res)
		return True
		
	def wkf_approve_order(self, cr, uid, ids, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: wkf_approve_order called...')
		obj = self.browse(cr,uid,ids[0])
		print "PO confirm is called,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,", obj
		self.write(cr, uid, ids, {'state': 'approved', 'date_approve': fields.date.context_today(self,cr,uid,context=context),'order_line.line_state' : 'confirm'})
		po_order_obj=self.pool.get('purchase.order')
		po_id=obj.id
		po_lines = obj.order_line
		for id in ids:
				cr.execute("""select piline_id from kg_poindent_po_line where po_order_id = %s"""  %(str(id)))
				data = cr.dictfetchall()
				val = [d['piline_id'] for d in data if 'piline_id' in d] # Get a values form list of dict if the dict have with empty values
				for i in range(len(po_lines)):
					print "po_lines[i]???????????????????", po_lines[i], po_lines[i].id
					pi_line_id=po_lines[i].pi_line_id
					product = po_lines[i].product_id.name
					po_qty=po_lines[i].product_qty
					po_pending_qty=po_lines[i].pi_qty
					pi_pending_qty= po_pending_qty - po_qty
					if pi_line_id:
						if po_qty > po_pending_qty:
							raise osv.except_osv(
							_('If PO from Purchase Indent'),
							_('PO Qty should not be greater than purchase indent Qty. You can raise this PO Qty upto %s --FOR-- %s.' %(po_pending_qty, product)))
						pi_obj=self.pool.get('purchase.requisition.line')
						pi_line_obj=pi_obj.search(cr, uid, [('id','=',val[i])])
						sql = """ update purchase_requisition_line set pending_qty=%s where id = %s"""%(pi_pending_qty,val[i])
						cr.execute(sql)
						print "val[i] ===================>>", val[i]
						pi_obj.write(cr,uid,val[i],{'line_state' : 'noprocess'})
						#pi_obj.write(cr, uid, val[i], {'line_state' : 'done'})
					#self.write(cr,uid,po_lines[i].id, {'line_state' :'confirm'})
					else:
						raise osv.except_osv(
							_('Direct Purchase Order Not Allow'),
							_('System not allow to raise PO with out Purchase Indent Line for %s' %(product)))
		self.send_email(cr,uid,ids)
		#print "senf mail called ***************8"
		return True
		cr.close()
	
		
	def poindent_line_move(self, cr, uid,ids, poindent_lines , context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: poindent_line_move called...')
		return {}
		
	def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: _create_pickings called...')
		return {}
		# Default Openerp workflow stopped and inherited the function
		
	def action_cancel(self, cr, uid, ids, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: action_cancel called...')
		wf_service = netsvc.LocalService("workflow")
		purchase = self.browse(cr, uid, ids[0], context=context)
		print "pick ids:::::::::::::::::::::::::::", purchase.picking_ids
		for pick in purchase.picking_ids:
			if pick.state not in ('draft','cancel'):
				raise osv.except_osv(
					_('Unable to cancel this purchase order.'),
					_('First cancel all GRN related to this purchase order.'))
			wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
		for line in purchase.order_line:
			if line.pi_line_id:
						pi_obj=self.pool.get('purchase.requisition.line')
						pi_line_obj=pi_obj.search(cr, uid, [('id','=',line.pi_line_id.id)])
						orig_pending_qty = line.pi_line_id.pending_qty
						po_qty = line.product_qty
						orig_pending_qty += po_qty
						print "orig_pending_qty:::::::::::::::::::", orig_pending_qty
						sql = """ update purchase_requisition_line set pending_qty=%s where id = %s"""%(orig_pending_qty,line.pi_line_id.id)
						cr.execute(sql)
				
		for inv in purchase.invoice_ids:
			
			if inv:
				wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
		self.write(cr,uid,ids,{'state':'cancel'})

		for (id, name) in self.name_get(cr, uid, ids):
			wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_cancel', cr)
		return True
		
		
	def create_report(self,cr, uid, res_ids, report_name=False, file_name=False):
		print "res_ids, report_name, file_name=================>>>>", res_ids, report_name, file_name
		if not report_name or not res_ids:
			return (False, Exception('Report name and Resources ids are required !!!'))
		try:
			ret_file_name = '/home/sengottuvelu/test/'+file_name+'.pdf'
			print "ret_file_nameret_file_nameret_file_name<><><><><>>", ret_file_name
			service = netsvc.LocalService("report."+report_name)
			print "serviceserviceserviceservice <<<<<<<<<>>>>>>>>>>.", service
			(result, format) = service.create(cr, uid, res_ids, {'model': 'purchase.order'}, {})
			fp = open(ret_file_name, 'wb+');
			print "fpfpfpfpfpfpfpfpfpfp@@@@@@@@@@@@@@@@@@@@@@@@@@", fp
			try:
				fp.write(result);
			finally:
				fp.close();
		except Exception,e:
			print 'Exception in create report:',e
			return (False, str(e))
		return (True, ret_file_name)

		
	def send_email(self, cr, uid, ids,context=None):
		
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: send_email called...')
		po_rec = self.browse(cr,uid,ids[0])
		po_report_obj = self.pool.get('kg.purchase.order.wizard')
		par_mailid = [po_rec.email] or ''
		mail =  ",".join(par_mailid)
		to_mails = mail.split(",",4)
		from_mailid = "kgopenerp@kggroup.com"
		filename= '/home/sengottuvelu/Desktop/PO_mail.pdf'
		msg = MIMEMultipart()
		fo = open(filename, "rb")
		msg.attach(filename)
		subject = "PO Confirmation from KGHealth Care Limited"
		
		body = """
		Dear Team,
		
		We are pleasure for place a Purchase Order to you and supply the goods ASAP. This mail have attachment of Purchase Order soft copy.
		Please find the attachment.
		
		
		Thanks,
		KGHealth Care..
		"""	
		message = 'Subject: %s\n\n%s' % (subject, body)
			
			#################
		#### Attachment Part ####
			#################
		
		attachment_ids = []
		for data in attachments:
			attachment_data = {
				'name': data[0],
				'datas_fname': data[0],
				'datas': data[1],
				'res_model': mail_mail._name,
				'res_id': mail_id,
			}
			attachment_ids.append(ir_attachment.create(cursor, uid, attachment_data, context=context))
		if attachment_ids:
			mail_mail.write(cursor, uid, mail_id, {'attachment_ids': [(6, 0, attachment_ids)]}, context=context)
		mail_mail_obj.send(cursor, uid, [mail_id], context=context)
		
				
		"""
		if context is None:
			context = {}
		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		print "context =======================>>>>", context
		return {
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'kg.purchase.order.wizard',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}
		"""
		
		# Check Server Connection
		try:
			server = smtplib.SMTP(host='10.100.1.64', port='25',timeout=socket.setdefaulttimeout(60))
		except Exception:
			logger.error('[KG ERP] Unable To Reach SMTP Server. Please Report To IT Team....!!!')
			return False

		## Check mail properties
		try:
			server.sendmail(from_mailid, to_mails ,message)
			logger.info('[KG ERP] Email Sent Sucessfully...!!!!!!')
			print "The To Mail Addresses Are ::::::::::: ", mail
			return True
		except Exception: # try to avoid catching Exception unless you have too
			logger.error('[KG ERP] Unable To Load Email Properties. Please Check The Informations....!!!')
			return False
		finally:
			server.quit()
	
kg_purchase_order()


class kg_purchase_order_line(osv.osv):
	
	def onchange_discount_value_calc(self, cr, uid, ids, kg_discount_per, product_qty, price_unit):
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: onchange_discount_value_calc called...')
		discount_value = (product_qty * price_unit) * kg_discount_per / 100
		return {'value': {'kg_discount_per_value': discount_value}}
		
	
	def _amount_line(self, cr, uid, ids, prop, arg, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: _amount_line called...')
		print "KGGGGGGGG_amount_line...........................ids :", ids
		cur_obj=self.pool.get('res.currency')
		tax_obj = self.pool.get('account.tax')
		res = {}
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			amt_to_per = (line.kg_discount / (line.product_qty * line.price_unit or 1.0 )) * 100
			print "amt_to_per ====================>>", amt_to_per
			kg_discount_per = line.kg_discount_per
			print "kg_discount_per ====================>>", kg_discount_per
			tot_discount_per = amt_to_per + kg_discount_per
			print "tot_discount_per ====================>>", tot_discount_per
			price = line.price_unit * (1 - (tot_discount_per or 0.0) / 100.0)
			print "price ====================>>", price
			taxes = tax_obj.compute_all(cr, uid, line.taxes_id, price, line.product_qty, line.product_id, line.order_id.partner_id)
			cur = line.order_id.pricelist_id.currency_id
			res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
		return res
			
	
	_name = "purchase.order.line"
	_inherit = "purchase.order.line"
	
	_columns = {

	'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
	'kg_discount': fields.float('Discount Amount', digits_compute= dp.get_precision('Discount')),
	'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
	'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
	'pending_qty': fields.float('Pending Qty'),
	'pi_qty':fields.float('PI Qty'),
	'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
	'name': fields.text('Description'),
	'date_planned': fields.date('Scheduled Date', select=True),
	'note': fields.text('Remarks'),
	'pi_line_id':fields.many2one('purchase.requisition.line','PI Line'),
	'kg_discount_per': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
	'kg_discount_per_value': fields.float('Discount(%)Value', digits_compute= dp.get_precision('Discount')),
	'line_state': fields.selection([('draft', 'Draft'),('confirm','Confirmed'),('cancel', 'Cancel')], 'State'),


	}
	
	_defaults = {
	
	'date_planned' : fields.date.context_today,
	'line_state' : 'draft',
	
	} 
	
	def onchange_qty(self, cr, uid, ids,product_qty,pending_qty,pi_line_id,pi_qty,po_type=False):
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: onchange_qty called...')
		if po_type == 'frompi' and pi_line_id == False:
			raise osv.except_osv(_('PO From PI Only!'),_("You must select a PO lines From PI !") )
		# Need to do block flow
		value = {'pending_qty': ''}
		if product_qty and product_qty > pi_qty:
			raise osv.except_osv(_(' If PO From PI !!'),_("PO Qty can not be greater than Indent Qty !") )
		else:
			value = {'pending_qty': product_qty}
		return {'value': value}
		
	def pol_cancel(self, cr, uid, ids, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: pol_cancel called...')

		line_rec = self.browse(cr,uid,ids)
		if line_rec[0].product_qty != line_rec[0].pending_qty:
			raise osv.except_osv(
				_('Few Quanties are Received !! '),
				_('You can cancel a PO line before receiving product'))
		else:				
			self.write(cr,uid,ids,{'line_state':'cancel'})
		return True
	
	
kg_purchase_order_line()



"""
def wkf_approve_order(self, cr, uid, ids, context=None):
		obj = self.browse(cr,uid,ids[0])
		product_qty = 0
		print "PO confirm is called,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,", obj
		self.write(cr, uid, ids, {'state': 'approved', 'date_approve': fields.date.context_today(self,cr,uid,context=context)})
		po_order_obj=self.pool.get('purchase.order')
		po_id=obj.id
		po_lines = obj.order_line
		print "po_lines((((((((((((((((((((((((((", po_lines
		for order_line in po_lines:
			print "order_line)))))))))))))))))))))))))", order_line
			for id in ids:
				cr.execute(select piline_id from kg_poindent_po_line where po_order_id = %s  %(str(id)))
				data = cr.dictfetchall()
				val = [d['piline_id'] for d in data if 'piline_id' in d] # Get a values form list of dict if the dict have with empty values
				for pi_id in val:
					pi_obj=self.pool.get('purchase.requisition.line')
					pi_line_obj=self.pool.get('purchase.requisition.line').search(cr, uid, [('id','=',pi_id)]) 

					print "id====== pi_pending_qty^^^^^^^^^^^^^^", id
					print "Line~~~~~~~~~~~~~~~~~~~~~~~", order_line
					po_qty=order_line.product_qty
					print "po_qty@@@@@@@@@@@@@@@@@@@@@@@@@@", po_qty
					po_pending_qty=order_line.pending_qty
					print "po_pending_qty######################", po_pending_qty
					pi_pending_qty= po_pending_qty - po_qty
					print "pi_pending_qty######################", pi_pending_qty

					print "pi_line_obj................................",pi_line_obj
					for id in pi_line_obj:
						print "id,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,", id
						pi_obj.write(cr, uid, id, {'line_state' : 'pending'})
			
		
		return True
		"""	
		
			
"""
	
	def onchange_discount_per_calc(self, cr, uid, ids, kg_discount, product_qty, price_unit):
		
		discount_per = (kg_discount / (product_qty * price_unit)) * 100
		print "discount_per''''''''''''''''''", discount_per
		return {'value': {'kg_discount_per': discount_per}}
		
	def onchange_product_qty(self, cr, uid, product_qty, pending_qty):
		if product_qty:
			new_pending_qty = product_qty
			print "new_pending_qty:::::::::::::::::::::::::::::::::", new_pending_qty
			return{'value':{'pending_qty':new_pending_qty}}
		return False
"""	
		
