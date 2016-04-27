## KG Purchase Order ##

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
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import logging
import netsvc
import pooler
logger = logging.getLogger('server')

class kg_purchase_order(osv.osv):
	
	def _amount_line_tax(self, cr, uid, line, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: _amount_line_tax called...')
		val = 0.0
		new_amt_to_per = line.kg_discount / line.product_qty
		amt_to_per = (line.kg_discount / (line.product_qty * line.price_unit or 1.0 )) * 100
		kg_discount_per = line.kg_discount_per
		tot_discount_per = amt_to_per + kg_discount_per
		for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id,
			line.price_unit * (1-(tot_discount_per or 0.0)/100.0), line.product_qty, line.product_id,
				line.order_id.partner_id)['taxes']:
			#print "cccccccccccc ------------------------->>>>>", c
				 
			val += c.get('amount', 0.0)
		return val	
	
	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: _amount_all called...')
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
			pol = self.pool.get('purchase.order.line')
			for line in order.order_line:
				tot_discount = line.kg_discount + line.kg_discount_per_value
				val1 += line.price_subtotal
				#for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, order.partner_id)['taxes']:
				val += self._amount_line_tax(cr, uid, line, context=context)
				val3 += tot_discount
			
			res[order.id]['other_charge']=cur_obj.round(cr, uid, cur, po_charges)
			res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
			res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1) - cur_obj.round(cr, uid, cur, val)
			res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] + res[order.id]['other_charge']
			res[order.id]['discount']=cur_obj.round(cr, uid, cur, val3)
			#print "RES--------RES-------RES---------------->>", res
		return res
		
	def _get_order(self, cr, uid, ids, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: _get_order called...')
		result = {}
		for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
			result[line.order_id.id] = True
		return result.keys()

	_name = "purchase.order"
	_inherit = "purchase.order"
	_order = "date_order desc"

	_columns = {
		
		'po_type': fields.selection([('direct', 'Direct'),('frompi', 'From PI')], 'PO Type'),
		'bill_type': fields.selection([('cash','CASH BILL'),('credit','CREDIT BILL')], 'Bill Type', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'po_expenses_type1': fields.selection([('freight','Freight Charges'),('others','Others')], 'Expenses Type1', readonly=True, states={'draft':[('readonly',False)]}),
		'po_expenses_type2': fields.selection([('freight','Freight Charges'),('others','Others')], 'Expenses Type2', readonly=True, states={'draft':[('readonly',False)]}),
		'value1':fields.float('Value1', readonly=True, states={'draft':[('readonly',False)]}),
		'value2':fields.float('Value2', readonly=True, states={'draft':[('readonly',False)]}),
		'note': fields.text('Remarks'),
		'vendor_bill_no': fields.float('Vendor.Bill.No', readonly=True, states={'draft':[('readonly',False)]}),
		'vendor_bill_date': fields.date('Vendor.Bill.Date', readonly=True, states={'draft':[('readonly',False)]}),
		'location_id': fields.many2one('stock.location', 'Destination', required=True, domain=[('usage','=','internal')], states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]} ),		
		'payment_term_id': fields.many2one('account.payment.term', 'Payment Term', readonly=True, states={'draft':[('readonly',False)]}),
		'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}, help="The pricelist sets the currency used for this purchase order. It also computes the supplier price for the selected products/quantities."),	
		'date_order': fields.date('Creation Date', readonly=True),
		'payment_mode': fields.selection([('ap','ADVANCE PAID'),('on_receipt', 'ON RECEIPT OF GOODS AND ACCEPTANCE')], 'Mode of Payment', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'delivery_type':fields.many2one('kg.deliverytype.master', 'Delivery Schedule', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'delivery_mode': fields.selection([('direct','DIRECT'),('door','DOOR DELIVERY')], 'Mode of delivery', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'partner_address':fields.char('Supplier Address', size=128, readonly=True, states={'draft':[('readonly',False)]}),
		'email':fields.char('Contact Email', size=128, readonly=True, states={'draft':[('readonly',False)]}),
		'contact_person':fields.char('Contact Person', size=128),
		'other_charge': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Other Charges(+)',
			 multi="sums", help="The amount without tax", track_visibility='always'),		
		
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
			store=True, multi="sums", help="The tax amount"),
		'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total Amount',
			 multi="sums", store=True, help="The amount without tax", track_visibility='always'),		
		
		'po_flag': fields.boolean('PO Flag'),
		'grn_flag': fields.boolean('GRN'),
		'kg_seq_id':fields.many2one('ir.sequence','Document Type',domain=[('code','=','purchase.order')],
			readonly=True, states={'draft': [('readonly', False)]}),
		'name': fields.char('Order Reference', size=64, select=True,readonly=True, states={'draft': [('readonly', False)]}),
		'user_id': fields.many2one('res.users', 'User'),
		'bill_flag':fields.boolean('PO Bill'),
		'amend_flag': fields.boolean('Amendment', select=True),
		'add_text': fields.text('Address',readonly=True, states={'draft': [('readonly', False)]}),
		'type_flag':fields.boolean('Type Flag'),
		
		
	}
	
	_defaults = {
	
	'bill_type' :'credit',
	'date_order': fields.date.context_today,
	'po_type': 'frompi',
	'name': '',
	'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
	}

	def create(self, cr, uid, vals,context=None):
		print "vals...............................", vals
		inv_seq = vals['kg_seq_id']
		next_seq_num = self.pool.get('ir.sequence').kg_get_id(cr, uid, inv_seq,'id',{'noupdate':False})
		print "next_seq_num...........................", next_seq_num
		vals.update({
						'name':next_seq_num,
						
						})
		if vals['type_flag'] == True:
			print "sssssssssss"
			vals.update({
						'po_type':'direct',
						
						})
			print vals['po_type']
		order =  super(kg_purchase_order, self).create(cr, uid, vals, context=context)
		return order
	
	
	def onchange_seq_id(self, cr, uid, ids, kg_seq_id,name):
		print "kgggggggggggggggggg --  onchange_seq_id called"		
		value = {'name':''}
		if kg_seq_id:
			next_seq_num = self.pool.get('ir.sequence').kg_get_id(cr, uid, kg_seq_id,'id',{'noupdate':False})
			print "next_seq_num:::::::::::", next_seq_num
			value = {'name': next_seq_num}
		return {'value': value}
		
	def onchange_type_flag(self, cr, uid, ids, po_type):
		print "kgggggggggggggggggg --  onchange_seq_id called"
		value = {'type_flag':False}
		if po_type == 'direct':
			value = {'type_flag': True}
		return {'value': value}
	
	def onchange_partner_id(self, cr, uid, ids, partner_id,add_text):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: onchange_partner_id called...')
		partner = self.pool.get('res.partner')
		if not partner_id:
			return {'value': {
				'fiscal_position': False,
				'payment_term_id': False,
				}}
		supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
		supplier = partner.browse(cr, uid, partner_id)
		tot_add = (supplier.street or '')+ ' ' + (supplier.street2 or '') + '\n'+(supplier.city.name or '')+ ',' +(supplier.state_id.name or '') + '-' +(supplier.zip or '') + '\nPh:' + (supplier.phone or '')+ '\n' +(supplier.mobile or '')		
		return {'value': {
			'pricelist_id': supplier.property_product_pricelist_purchase.id,
			'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
			'payment_term_id': supplier.property_supplier_payment_term.id or False,
			'add_text' : tot_add or False
			}}
			
	def onchange_user(self, cr, uid, ids, user_id,location_id):
		value = {'location_id': ''}
		if user_id:			
			user_obj = self.pool.get('res.users')
			user_rec = user_obj.browse(cr,uid,user_id)
			dep_rec = user_rec.dep_name
			location = dep_rec.main_location.id
			value = {'location_id': location}
		return {'value':value}
				
			
	def wkf_approve_order(self, cr, uid, ids, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: wkf_approve_order called...')
		obj = self.browse(cr,uid,ids[0])
		print obj.order_line
		line_obj = self.pool.get('purchase.order.line')
		line_rec = line_obj.search(cr, uid, [('order_id','=',obj.id)])
		print "000000000000000000000000000",line_rec
		for line in line_rec:
			line_obj.write(cr,uid,line,{'cancel_flag':'True'})
		print "PO confirm is called,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,", obj
		if obj.amount_total <= 0:
			raise osv.except_osv(
					_('Purchase Order Value Error !'),
					_('System not allow to confirm a Purchase Order with Zero Value'))			
		self.write(cr, uid, ids, {'state': 'approved', 'date_approve': fields.date.context_today(self,cr,uid,context=context),'order_line.line_state' : 'confirm'})
		po_order_obj=self.pool.get('purchase.order')
		po_id=obj.id
		po_lines = obj.order_line
		cr.execute("""select piline_id from kg_poindent_po_line where po_order_id = %s"""  %(str(ids[0])))
		data = cr.dictfetchall()
		val = [d['piline_id'] for d in data if 'piline_id' in d] # Get a values form list of dict if the dict have with empty values
		for i in range(len(po_lines)):
			print "po_lines==========>>", po_lines[i], "po_lines[i].group_flag()()()()()()()()()()()()", po_lines[i].group_flag
			if po_lines[i].pi_line_id and po_lines[i].group_flag == False:
				print "po_lines[i] ==============>>", po_lines[i] , "pi_line_id ==============>>", po_lines[i].pi_line_id			
				pi_line_id=po_lines[i].pi_line_id
				product = po_lines[i].product_id.name
				po_qty=po_lines[i].product_qty
				po_pending_qty=po_lines[i].pi_qty
				pi_pending_qty= po_pending_qty - po_qty
				if po_qty > po_pending_qty:
					raise osv.except_osv(
					_('If PO from Purchase Indent'),
					_('PO Qty should not be greater than purchase indent Qty. You can raise this PO Qty upto %s --FOR-- %s.'
								%(po_pending_qty, product)))
												
				pi_obj=self.pool.get('purchase.requisition.line')
				pi_line_obj=pi_obj.search(cr, uid, [('id','=',val[i])])
				print "pi_line_id ==============>>", pi_line_id.id , "pi_pending_qty ==============>>", pi_pending_qty
				sql = """ update purchase_requisition_line set pending_qty=%s where id = %s"""%(pi_pending_qty,pi_line_id.id)
				cr.execute(sql)
				pi_obj.write(cr,uid,pi_line_id.id,{'line_state' : 'noprocess'})
				
				if po_lines[i].group_flag == True:
						self.update_product_pending_qty(cr,uid,ids,line=po_lines[i])
				else:
					print "All are correct Values and working fine"
					
		#self.send_email(cr,uid,ids)
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
		product_obj = self.pool.get('product.product')
		pi_line_obj = self.pool.get('purchase.requisition.line')
		purchase = self.browse(cr, uid, ids[0], context=context)
		print "pick ids:::::::::::::::::::::::::::", purchase.picking_ids
		if purchase.state == 'approved':				
			for pick in purchase.picking_ids:
				if pick.state not in ('draft','cancel'):
					raise osv.except_osv(
						_('Unable to cancel this purchase order.'),
						_('First cancel all GRN related to this purchase order.'))
				wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
			for line in purchase.order_line:
				if line.pi_line_id and line.group_flag == False:
							pi_obj=self.pool.get('purchase.requisition.line')
							pi_line_obj=pi_obj.search(cr, uid, [('id','=',line.pi_line_id.id)])
							orig_pending_qty = line.pi_line_id.pending_qty
							po_qty = line.product_qty
							orig_pending_qty += po_qty
							print "orig_pending_qty:::::::::::::::::::", orig_pending_qty
							sql = """ update purchase_requisition_line set pending_qty=%s where id = %s"""%(orig_pending_qty,line.pi_line_id.id)
							cr.execute(sql)
				else:
					if line.pi_line_id and line.group_flag == True:
						cr.execute(""" select piline_id from kg_poindent_po_line where po_order_id = %s """ %(str(ids[0])))
						data = cr.dictfetchall()
						val = [d['piline_id'] for d in data if 'piline_id' in d] 
						print "val...............................",val
						product_id = line.product_id.id
						product_record = product_obj.browse(cr, uid, product_id)
						print "product_id....................", product_id
						list_line = pi_line_obj.search(cr,uid,[('id', 'in', val), ('product_id', '=', product_id)],context=context)
						print "list_line....................>>>>>", list_line
						po_used_qty = line.product_qty
						orig_pi_qty = line.group_qty
						for i in list_line:
							print "IIIIIIIIIIIIIIIIIII", i,"line:::::::::::pi id.", line.pi_line_id
							bro_record = pi_line_obj.browse(cr, uid,i)
							print "bro_record.............................", bro_record
							pi_pen_qty = bro_record.pending_qty
							pi_qty = orig_pi_qty + pi_pen_qty
							orig_pi_qty +=pi_pen_qty
							po_qty = po_used_qty
							print "pi_pen_qty::::::::::", pi_pen_qty, "pi_qty::::::::::", pi_qty, "po_qty::::::::::", po_qty
													 
							if po_qty < pi_qty:
								pi_qty = pi_pen_qty + po_qty
								sql = """ update purchase_requisition_line set pending_qty=%s where id = %s"""%(pi_qty,bro_record.id)
								cr.execute(sql)
								break		
							
							else:
								print "elllllllllllllllllselllllllllesese"
								print "orig_pi_qty...........................", orig_pi_qty
								remain_qty = po_used_qty - orig_pi_qty
								sql = """ update purchase_requisition_line set pending_qty=%s where id = %s"""%(orig_pi_qty,bro_record.id)
								cr.execute(sql)
								print "remain_qty========================>>>", remain_qty
								if remain_qty < 0:
									break
								po_used_qty = remain_qty
								orig_pi_qty = pi_pen_qty + remain_qty
		
		else:
			for line in purchase.order_line:
				pi_line_obj.write(cr,uid,line.pi_line_id.id,{'line_state' : 'noprocess'})		
														
		"""		
		for inv in purchase.invoice_ids:
			
			if inv:
				wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
				"""
				
		if not purchase.note:
			raise osv.except_osv(
						_('Remarks Needed !!'),
						_('Enter remark in Remarks Tab....'))
		else:
			self.write(cr,uid,ids,{'state':'cancel'})

		for (id, name) in self.name_get(cr, uid, ids):
			wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_cancel', cr)
		return True
		
			
	def send_email(self, cr, uid, ids,context=None):
		
		logger.info('[KG OpenERP] Class: kg_purchase_order, Method: send_email called...')
		po_rec = self.browse(cr,uid,ids[0])
		print "po_rec ======================>>>>", po_rec
		
		from_mailid = "kgopenerp@kggroup.com"
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "PO Confirmation from KGHealth Care Limited"
		street = po_rec.partner_id.street
		code = po_rec.partner_id.zip
		print "street1...................", street, "code::::", code
		if po_rec.email and po_rec.order_line:
			par_mailid = [po_rec.email] or ''
			mail = ",".join(par_mailid)
			to_mails = mail.split(",",4)
			po_lines = po_rec.order_line
			print "po_lines ::::::::::::::::", po_lines
			
			body_part_1 = """\
				<html>
					<body>
						<p>
							<h1><center><b>KG Health Care Limited</b></center></h1><br />
							<center>Goverment Arts College Road</center><br /></center>
							<center>Coimbatore - 641 018, Tamil Nadu, India.<br /></center>
							<center>Phone: +91-44-2212121/29 Fax: +91-44-23460048<br /></center>
							<center>E-mail: purchase@kgcare.com<br /></center>
						</p>
						<hr>			
					<center>Purchase Order Confirmation</center><br/>"""
			
			body_part_2 = """Order No : """+po_rec.name+"""<br/>
							 Date : """+po_rec.date_order+"""
							<br/>
							<br/>
							<br/>
							"""  
							
			body_part_3 = """<b>TO</b>, <br/>
							&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+po_rec.partner_id.name or ''+"""<br/>
							&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+str(po_rec.partner_id.street) or ''+"""<br/>
							&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+str(po_rec.partner_id.street2) or '' +"""<br/>
							
							
							<br/>
							<br/>
							""" 
							
						
			body_part_5 = """<table border='2' align="center"> 
					<br/>
					<br/>
					<br/>
					<tr>
						<th colspan='2'>SL.No</th>
						<th colspan='2'>Item Name</th>
						<th colspan='2'>Item Qty</th>
						<th colspan='2'>Uom</th>
						<th colspan='2'>Price</th>
					</tr>"""				
					
			body_part_6 = ""
			for position, line in enumerate(po_lines):
					
					body_part_6 += """<tr>
						<td colspan='2'>"""+str(position+1)+"""</td>
						<td colspan='2'>"""+line.product_id.name_template+"""</td>
						<td colspan='2'>"""+str(line.product_qty)+"""</td>
						<td colspan='2'>"""+line.product_uom.name+"""</td>
						<td colspan='2'>"""+str(line.price_unit)+"""</td>
					</tr>
					"""  
					
			body_part_7 = """</table>		   
				<br/>
				<br/>		  
				Kindly supply the items with this copy by as soon as possible.<br/>
				
				<br/>
				<br/>
				Thanking You
				<br/>
				<br/>
				Very Cordially Yours<br/>
				<b>KG HealthCare Limited</b><br/>
				<br/>
				<br/>
				<font size="1">Authorised Signatory</font><br/>
				<br/>
				<font size="1">Note: This is a computer generate output,does not require signature</font>
				</body>
			</html>
			"""
			
			html = body_part_1+body_part_2+body_part_3+body_part_5+body_part_6+body_part_7
			part2 = MIMEText(html, 'html')
			msg.attach(part2)
			
			# Check Server Connection
			try:
				server = smtplib.SMTP(host='10.100.1.64', port='25',timeout=socket.setdefaulttimeout(60))
			except Exception:
				logger.error('[KG ERP] Unable To Reach SMTP Server. Please Report To IT Team....!!!')
				return False

			## Check mail properties
			try:
				server.sendmail(from_mailid, to_mails ,msg.as_string())
				logger.info('[KG ERP] Email Sent Sucessfully To ===>>...!!!!!! %s' %(mail))
				return True
			except Exception: # try to avoid catching Exception unless you have too
				logger.error('[KG ERP] Unable To Load Email Properties. Please Check The Informations....!!!')
				return False
			finally:
				server.quit()
		else:
			logger.error('[KG ERP] Unable to Send a Mail ---- No Email address in Partner....PO Order is %s' %(po_rec.name))
				
	def _check_line(self, cr, uid, ids, context=None):
		logger.info('[KG ERP] Class: kg_purchase_order, Method: _check_line called...')
		for po in self.browse(cr,uid,ids):
			if po.po_type != 'direct': 
				if po.kg_poindent_lines==[]:
					tot = 0.0
					for line in po.order_line:
						tot += line.price_subtotal
						print "tot ===============================>>>>", tot
					if tot <= 0.0 or po.amount_total <=0:			
						return False
				return True
			
	def _check_total(self, cr, uid, ids, context=None):		
		po_rec = self.browse(cr, uid, ids[0])
		if po_rec.kg_seq_id:
			for line in po_rec.order_line:				
				if line.price_subtotal <= 0:
					return False					
		return True
			
	_constraints = [
	
		#(_check_line,'You can not save this Purchase Order with out Line and Zero Qty !',['order_line']),
		#(_check_total,'You can not save this Purchase Order with Zero value !',['order_line']),
	
	]
	
	def print_quotation(self, cr, uid, ids, context=None):		
		assert len(ids) == 1, 'This option should only be used for a single id at a time'
		wf_service = netsvc.LocalService("workflow")
		wf_service.trg_validate(uid, 'purchase.order', ids[0], 'send_rfq', cr)
		datas = {
				 'model': 'purchase.order',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		#print "datas ------------------------", datas
		return {'type': 'ir.actions.report.xml', 'report_name': 'onscreen.po.report', 'datas': datas, 'ids' : ids, 'nodestroy': True}
	
kg_purchase_order()


class kg_purchase_order_line(osv.osv):
	
	def onchange_discount_value_calc(self, cr, uid, ids, kg_discount_per, product_qty, price_unit):
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: onchange_discount_value_calc called...')
		discount_value = (product_qty * price_unit) * kg_discount_per / 100.00
		print "discount_value ------------------------->>>>", discount_value
		return {'value': {'kg_discount_per_value': discount_value }}
		
	def onchange_disc_amt(self,cr,uid,ids,kg_discount,product_qty,price_unit,kg_disc_amt_per):
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: onchange_disc_amt called...')
		if kg_discount:
			print "kg_discount..........", 
			kg_discount = kg_discount + 0.00
			amt_to_per = (kg_discount / (product_qty * price_unit or 1.0 )) * 100.00
			print "amt_to_peramt_to_peramt_to_per*******************", amt_to_per
			return {'value': {'kg_disc_amt_per': amt_to_per}}	
		else:
			return {'value': {'kg_disc_amt_per': 0.0}}	
	
	def _amount_line(self, cr, uid, ids, prop, arg, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: _amount_line called...')
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
			taxes = tax_obj.compute_all(cr, uid, line.taxes_id, price, line.product_qty, line.product_id, line.order_id.partner_id)
			cur = line.order_id.pricelist_id.currency_id
			#print "Taxes ==========================>>>", taxes
			res[line.id] = cur_obj.round(cr, uid, cur, taxes['total_included'])
		return res
		
	_name = "purchase.order.line"
	_inherit = "purchase.order.line"
	
	_columns = {

	'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
	'kg_discount': fields.float('Discount Amount'),
	'kg_disc_amt_per': fields.float('Disc Amt(%)', digits_compute= dp.get_precision('Discount')),
	'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
	'product_qty': fields.float('Quantity'),
	'pending_qty': fields.float('Pending QTY'),
	'received_qty':fields.float('Received QTY'),
	'cancel_qty':fields.float('Cancel QTY'),
	'pi_qty':fields.float('PI Qty'),
	'group_qty':fields.float('Group Qty'),
	'product_uom': fields.many2one('product.uom', 'UOM', required=True),
	'name': fields.text('Description'),
	'date_planned': fields.date('Scheduled Date', select=True),
	'note': fields.text('Remarks'),
	'pi_line_id':fields.many2one('purchase.requisition.line','PI Line'),
	'po_order':fields.one2many('kg.po.line','line_id','PO order Line'),
	'kg_discount_per': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
	'kg_discount_per_value': fields.float('Discount(%)Value', digits_compute= dp.get_precision('Discount')),
	'line_state': fields.selection([('draft', 'Active'),('confirm','Confirmed'),('cancel', 'Cancel')], 'State'),
	'group_flag': fields.boolean('Group By'),
	'total_disc': fields.float('Discount Amt'),
	'line_bill': fields.boolean('PO Bill'),
	'tax_structure_id':fields.many2one('kg.tax.structure', 'Tax Structure',
			domain="[('state','=','app'),'&',('type','=','po')]"),
	'cancel_remark':fields.text('Cancel Remarks'),
	'cancel_flag':fields.boolean('Cancel Flag'),
	'move_line_id':fields.many2one('stock.move','Move Id'),
	'line_flag':fields.boolean('Line Flag'),



	}
	
	_defaults = {
	
	'date_planned' : fields.date.context_today,
	'line_state' : 'draft',
	'name':'PO',
	'cancel_flag': False
	
	}
	
	def get_taxes_structure(self,cr,uid,struct_id):		
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: get_taxes_structure called...')
		if isinstance(struct_id,int):
			tax_struct_obj =  self.pool.get('kg.tax.structure')
			tax_struct_browse = tax_struct_obj.browse(cr,uid,struct_id)
			print "tax_struct_browse ---------------------.....", tax_struct_browse
			tax_ids  = map(lambda x:{'tax_id':x.tax_id.id},tax_struct_browse.tax_line)
			print "tax_ids =======================>>>", tax_ids
			return tax_ids
		return []
		
	def onchange_tax_structure(self, cr, uid,ids, tax_structure_id):
		print "ids =================>>",ids
		tax_struct_obj =  self.pool.get('kg.tax.structure')
		sql_check = """ select tax_id from purchase_order_taxe where ord_id=%s """ %(ids[0])
		cr.execute(sql_check)
		data = cr.dictfetchall()
		if data:
			del_sql = """ delete from purchase_order_taxe where ord_id=%s """ %(ids[0])
			cr.execute(del_sql)
		if tax_structure_id:
			stru_rec = tax_struct_obj.browse(cr, uid,tax_structure_id)					
			for line in stru_rec.tax_line:
				tax_id = line.tax_id.id
				sql = """ insert into purchase_order_taxe (ord_id,tax_id) VALUES(%s,%s) """ %(ids[0],tax_id)
				cr.execute(sql)
			return True
	
	def onchange_qty(self, cr, uid, ids,product_qty,pending_qty,pi_line_id,pi_qty,po_type=False):
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: onchange_qty called...')
		if po_type == 'frompi' and pi_line_id == False:
			raise osv.except_osv(_('PO From PI Only!'),_("You must select a PO lines From PI !") )
		# Need to do block flow
		value = {'pending_qty': ''}
		if po_type != 'direct':
			if product_qty and product_qty > pi_qty:
				raise osv.except_osv(_(' If PO From PI !!'),_("PO Qty can not be greater than Indent Qty !") )
			
			else:
				value = {'pending_qty': product_qty}
		return {'value': value}
	
	def onchange_pend_qty(self, cr, uid, ids,product_qty,pending_qty):
		
		value = {'pending_qty': ''}
		value = {'pending_qty': product_qty}
		return {'value': value}
	
	def pol_cancel(self, cr, uid, ids, context=None):
		logger.info('[KG OpenERP] Class: kg_purchase_order_line, Method: pol_cancel called...')
		line_rec = self.browse(cr,uid,ids)
		
		if line_rec[0].product_qty != line_rec[0].pending_qty:
			raise osv.except_osv(
				_('Few Quanties are Received !! '),
				_('You can cancel a PO line before receiving product'))
				
		if not line_rec[0].cancel_remark:
			
			raise osv.except_osv(
				_('Remarks !! '),
				_('Enter the remarks for po line cancel'))
		else:				
			self.write(cr,uid,ids,{'line_state':'cancel'})
		return True

			
	def unlink(self, cr, uid, ids, context=None):
		print "Purchase order line unlink method calling--->>", ids
		if context is None:
			context = {}
		for rec in self.browse(cr, uid, ids, context=context):
			print "rec ===================>>>>>", rec, "context====>", context
			parent_rec = rec.order_id
			print "parent_rec.state", parent_rec.state
			if parent_rec.state not in ['draft']:
				print "iffffffffffff"
				raise osv.except_osv(_('Invalid Action!'), _('Cannot delete a purchase order line which is in state \'%s\'.') %(parent_rec.state,))
			else:
				order_id = parent_rec.id
				pi_line_rec = rec.pi_line_id
				pi_line_id = rec.pi_line_id.id
				pi_line_rec.write({'line_state' : 'noprocess'})
				del_sql = """ delete from kg_poindent_po_line where po_order_id=%s and piline_id=%s """ %(order_id,pi_line_id)
				cr.execute(del_sql)				
				return super(kg_purchase_order_line, self).unlink(cr, uid, ids, context=context)
				
	def get_old_details(self,cr,uid,ids,context=None):
		print "ids..................",ids
		rec = self.browse(cr, uid, ids[0])
		last_obj = self.pool.get('kg.po.line')
		print "rec............................", rec.product_id.id		
		sql = """ select id,price_unit,order_id,kg_discount,kg_discount_per,tax_structure_id from purchase_order_line where product_id=%s and order_id != %s order by id desc limit 5 """%(rec.product_id.id,rec.order_id.id)
		cr.execute(sql)
		data = cr.dictfetchall()
		print "data.......................", data
		
		last_ids = last_obj.search(cr, uid, [('line_id','=',rec.id)])
		print "last_ids............>>>",last_ids
		if last_ids:
			for i in last_ids:
				last_obj.unlink(cr, uid, i, context=context)
		for item in data:
			print "item....................", item
			po_rec = self.pool.get('purchase.order').browse(cr,uid,item['order_id'])
			print "po_rec......................", po_rec
			
			vals = {
			
				'line_id':item['id'],
				'supp_name':po_rec.partner_id.id,
				'date_order':po_rec.date_order,
				'tax':item['tax_structure_id'],
				'other_ch':po_rec.other_charge,
				'kg_discount':item['kg_discount'],
				'kg_discount_per':item['kg_discount_per'],
				'price_unit':item['price_unit']
			
			
			}
			
			print "price..........",vals
			
			po_entry = self.write(cr,uid,rec.id,{'po_order':[(0,0,vals)]})
	
		return data
			
			
			
		
	
		
	
kg_purchase_order_line()

class kg_po_line(osv.osv):
		
	_name = "kg.po.line"
	
	_columns = {
	
	
	'line_id': fields.many2one('purchase.order.line', 'PO No'),
	'kg_discount': fields.float('Discount Amount'),
	'kg_discount_per': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
	'price_unit': fields.float('Unit Price', size=120),
	'date_order':fields.date('Date'),
	'supp_name':fields.many2one('res.partner','Supplier Name',size=120),
	'tax':fields.many2one('kg.tax.structure', 'Tax Structure'),
	'other_ch':fields.float('Other Charges',size=128),
		
	}
	
	
kg_po_line()

	




