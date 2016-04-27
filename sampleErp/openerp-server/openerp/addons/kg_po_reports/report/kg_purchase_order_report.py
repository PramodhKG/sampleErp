import time
from report import report_sxw
from osv import osv
from tools import number_to_text_convert_india
from reportlab.pdfbase.pdfmetrics import stringWidth
from operator import itemgetter
import tools
from osv import fields, osv
import time, datetime
from datetime import *
import logging
import locale
import netsvc
import ast
import collections
logger = logging.getLogger('server')

class kg_purchase_order_report(report_sxw.rml_parse):
	_name = 'kg.purchase.order.report'
	_inherit='purchase.order,purchase.order.line'
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_purchase_order_report, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_end_date':self._get_end_date,
			'get_data':self.get_data,
			'locale':locale,
			'get_data_line':self.get_data_line,
			
			
		})
		self.context = context

	def get_data(self,form):
		res = {}
		order = []
		partner = []
		where_sql = []
				
		if form['order']:
			for ids1 in form['order']:
				order.append("po.id = %s"%(ids1))
				
		if form['supplier']:
			for ids2 in form['supplier']:
				partner.append("po.partner_id = %s"%(ids2))
				
		if form['delivery_id']:
			delivery_id = form['delivery_id']
			where_sql.append("po.delivery_type = %s"%(delivery_id[0]))
		
		if order:
			order = 'and ('+' or '.join(order)
			order =  order+')'
		else:
			order = ''
		
		if partner:
			partner = 'and ('+' or '.join(partner)
			partner =  partner+')'
		else:
			partner = ''			
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
		
		print "order ==========================>>>", order
		print "partner ==========================>>>", partner
		print "where_sql ==========================>>>", where_sql
		
		self.cr.execute('''
				SELECT  distinct on (po.id) po.id as po_id, 
				to_char(po.date_order,'dd/mm/yyyy') as date, 
				po.name as po_number,
				po.origin as origin,
				po.partner_id as part_id,
				po.state as postate,
				po.amount_total as total,
				po.amount_tax as tax,
				po.note as remarks,
				po.discount as discount,
				master.name as delivery,
				po.delivery_mode as mode,
				po.payment_mode as pay_mode,
				po.notes as remark,
				part.name as name,
				part.street as str1,
				city.name as city,
				part.zip as zip,
				st.name as state,
				coun.name as country,
				part.phone as phone,
				part.mobile as cell,
				part.fax as fax,
				part.email as email,
				pi.name as pi_no,
				to_char(pi.date_start, 'dd/mm/yyyy') as pi_date,
				dep_line.indent_id as indent,
				depmaster.dep_name as dep_name,
				po.id as order_id
				
				FROM  purchase_order po
				join res_partner part on (part.id=po.partner_id)
				join res_country_state st on(st.id=part.state_id)
				join res_country as coun on(coun.id=part.country_id)
				left join res_city as city on(city.id=part.city)
				join kg_deliverytype_master as master on(master.id=po.delivery_type)
				join purchase_order_line as po_line on(po_line.order_id = po.id)
				join purchase_requisition_line as pi_line on(pi_line.id = po_line.pi_line_id)
				join purchase_requisition as pi on(pi.id = pi_line.requisition_id)
				join kg_depindent_line as dep_line on(dep_line.id = pi_line.depindent_line_id)
				join kg_depindent as indent on(indent.id = dep_line.indent_id)
				join kg_depmaster as depmaster on(depmaster.id = indent.dep_name)
								
				where po.state = %s and po_line.line_state != %s and po.date_order >=%s and po.date_order <=%s  '''+ where_sql + order + partner + '''
				''',('approved','cancel', form['date_from'],form['date_to']))
				
		data = self.cr.dictfetchall()
		print "Data ABBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", data
		for i in data:
			if i['pay_mode'] == 'ap':
				i['pay_mode'] = 'Advance Paid'
			elif i['pay_mode'] == 'on_receipt':
				i['pay_mode'] = 'On Receipt of Goods and Acceptance'
		for j in data:
			if j['mode'] == 'direct':
				j['mode'] = 'DIRECT'
			elif j['mode'] == 'door':
				j['mode'] = 'DOOR DELIVERY'
		for k in data:
			if k['postate'] == 'draft':
				k['postate'] = 'DRAFT'
			elif k['postate'] == 'approved':
				k['postate'] = 'APPROVED'
				
		for po in data:
			po_id = po['po_number']
			order_id = po['order_id']
			partner_id = po['part_id']
			po_record = self.pool.get('purchase.order').browse(self.cr, self.uid,order_id)
			text_amount = number_to_text_convert_india.amount_to_text_india(po['total'],"INR: ")
			po['total_in_text']=text_amount
			charges = po_record.other_charge
			po['charges']=charges
			pi_data = []
			dep_ids = []
			fmt = '%Y-%m-%d %H:%M:%S'			
			if po_record.order_line:
				for line in po_record.order_line:
					pil_id = line.pi_line_id
					pi_id = pil_id.requisition_id.name
					pi_date = pil_id.requisition_id.date_start
					d = datetime.strptime(pi_date, fmt)
					day_string = d.strftime('%d/%m/%Y')				
					dep_id = pil_id.dep_id.dep_name
					pi_data.append(pi_id)
					pi_data.append(day_string)					
					dep_ids.append(dep_id)
					pi_new_data =  [x for x, y in collections.Counter(pi_data).items()]
					new_data = (', '.join('"' + item + '"' for item in pi_new_data))
					#new_dep_id = (', '.join('"' + item + '"' for item in dep_ids))
					#po_dep_id = [ item.encode('ascii') for item in ast.literal_eval(new_dep_id) ]							
				po_pi_data = [ item.encode('ascii') for item in ast.literal_eval(new_data) ]				
				a = ', '.join(po_pi_data)
				#b = ', '.join(po_dep_id)			
				po['pi_data'] = a
				po['dep_name'] = dep_id
					
		return data
		
		
	def get_data_line(self,data):
		line_data=[]
		po_line_id = self.pool.get('purchase.order.line').search(self.cr, self.uid,
						[('order_id', '=', data)], context=None)
		
		po_line_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, po_line_id)
		tot_item = len(po_line_browse)
		po_obj = self.pool.get('purchase.order')
		tax_name = False
		for po_line in po_line_browse:	 
			taxs = po_line.taxes_id
			if taxs and len(taxs) !=1:
				tax_name = []
				for tax in taxs:
					name = tax.name
					tax_name.append(name)					
				new_data = (', '.join('"' + item + '"' for item in tax_name))
				tax_name = [ item.encode('ascii') for item in ast.literal_eval(new_data) ]
				tax_name = ', '.join(tax_name)								
			else:
				if taxs:
					tax_name = taxs[0].name	
			
			line ={
			
			'product':po_line.product_id.name,
			'prod_uom':po_line.product_uom.name,
			'prod_qty':po_line.product_qty,
			'price':po_line.price_unit,
			'discount':po_line.kg_discount + po_line.kg_discount_per_value or 0.0,
			'note': po_line.name,
			'line_id':po_line.id,
			'tot_item' : len(po_line_browse),
			'line_total': po_line.price_subtotal,
			'line_tax' : tax_name,
			'disc_per': po_line.kg_discount_per,
			'amt_to_per': po_line.kg_disc_amt_per,
			#'line_tax_amt': po_obj._amount_line_tax(self.cr,self.uid,po_line,context=None),			
			}
			print "line.........................", line
			
			line_data.append(line)
			po_obj = self.pool.get('purchase.order')
			
		return line_data


	def _get_filter(self, data):
		if data.get('form', False) and data['form'].get('filter', False):
			if data['form']['filter'] == 'filter_date':
				return _('Date')
		return _('No Filter')
		
	def _get_start_date(self, data):
		if data['form']['filter'] == 'filter_date':
			if data.get('form', False) and data['form'].get('date_from', False):
				return data['form']['date_from']
		else:
			return False
		
	def _get_end_date(self, data):
		if data['form']['filter'] == 'filter_date':
			if data.get('form', False) and data['form'].get('date_to', False):
				return data['form']['date_to']
		else:
			return False
		
	def _get_currency_data(self,data):
		cur_browse = self.pool.get('res.currency').browse(self.cr, self.uid, data)
		return cur_browse.name
	   
 
report_sxw.report_sxw('report.kg.purchase.order.report','purchase.order',
						'addons/kg_po_reports/report/kg_purchase_order_report.rml',
						parser=kg_purchase_order_report, header= False)
