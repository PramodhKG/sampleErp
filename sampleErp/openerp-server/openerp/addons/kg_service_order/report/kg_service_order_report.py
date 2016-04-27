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
logger = logging.getLogger('server')

class kg_service_order_report(report_sxw.rml_parse):
	_name = 'kg.service.order.report'
	_inherit='kg.service.order,kg.service.order.line'
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_service_order_report, self).__init__(cr, uid, name, context=context)
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
		where_sql = []
				
		if form['order']:
			for ids1 in form['order']:
				where_sql.append("so.id = %s"%(ids1))
		if form['supplier']:
			for ids2 in form['supplier']:
				where_sql.append("so.partner_id = %s"%(ids2))
		if form['delivery_id']:
			delivery_id = form['delivery_id']
			where_sql.append("so.delivery_type = %s"%(delivery_id[0]))
			
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
			print "where_sql.............................", where_sql
		else:
			where_sql=''
		
				
		self.cr.execute('''
				SELECT  distinct on (so.id) so.id as so_id, 
				to_char(so.date,'dd/mm/yyyy') as date, 
				so.name as so_number,
				so.partner_id as part_id,
				so.state as so_state,
				so.amount_total as total,
				so.amount_tax as tax,
				so.note as remarks,
				so.discount as discount,
				master.name as delivery,
				so.delivery_mode as mode,
				so.payment_mode as pay_mode,
				so.note as remark,
				part.name as name,
				part.street as str1,
				part.city as city,
				part.zip as zip,
				st.name as state,
				coun.name as country,
				part.phone as phone,
				part.mobile as cell,
				part.fax as fax,
				part.email as email,
				si.name as si_no,
				to_char(si.date, 'dd/mm/yyyy') as si_date,
				dep.dep_name as dep_name
			
				
				FROM  kg_service_order so
				join res_partner part on (part.id=so.partner_id)
				join res_country_state st on(st.id=part.state_id)
				join res_country as coun on(coun.id=part.country_id)
				join kg_deliverytype_master as master on(master.id=so.delivery_type)
				join kg_service_order_line as so_line on(so_line.service_id = so.id)
				join kg_service_indent_line as si_line on(si_line.id = so_line.soindent_line_id)
				join kg_service_indent as si on(si.id = si_line.service_id)
				join kg_depmaster as dep on(dep.id=si.dep_name)

								
				where so.state = %s and so.date >=%s and so.date <=%s  '''+ where_sql + '''
				''',('done', form['date_from'],form['date_to']))
				
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
			if k['so_state'] == 'draft':
				k['so_state'] = 'DRAFT'
			elif k['so_state'] == 'done':
				k['so_state'] = 'Done'

				
		for so in data:
			so_id = so['so_number']
			partner_id = so['part_id']
			so_id=so['so_id']
			so_record = self.pool.get('kg.service.order').browse(self.cr, self.uid,so_id)
			text_amount = number_to_text_convert_india.amount_to_text_india(so['total'],"INR: ")
			so['total_in_text']=text_amount
			#print "total_in_text ::::::::::::::::::::::::::::::::", so['total_in_text']
			print "other change =========================>>>", so_record
			charges = so_record.other_charge
			so['charges']=charges
			print "charges ()()()()()()())()()()()()() -------------->>", charges
		return data
		
		
	def get_data_line(self,data):
		line_data=[]
		print "data~~~~~~~~~~~~~~~~~~~~~~~~", data
		so_line_id = self.pool.get('kg.service.order.line').search(self.cr, self.uid,
						[('service_id', '=', data)], context=None)
		
		so_line_browse = self.pool.get('kg.service.order.line').browse(self.cr, self.uid, so_line_id)
		tot_item = len(so_line_browse)
		so_obj = self.pool.get('kg.service.order')
		for so_line in so_line_browse:		
			
			line ={
			
			'product':so_line.product_id.name,
			'prod_uom':so_line.product_uom.name,
			'prod_qty':so_line.product_qty,
			'price':so_line.price_unit,
			'discount':so_line.kg_discount + so_line.kg_discount_per_value or 0.0,
			'line_id':so_line.id,
			'tot_item' : len(so_line_browse),
			'line_total': so_line.price_subtotal,
			'line_tax' : so_obj._amount_line_tax(self.cr,self.uid,so_line,context=None),
			'disc_per': so_line.kg_disc_amt_per,
			'amt_to_per': so_line.kg_discount_per,			
			}
			
			line_data.append(line)
			so_obj = self.pool.get('kg.service.order')
			print "line...............>>>>>>>>>>>>>>>>>>>==========", line
			
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
	   
 
report_sxw.report_sxw('report.kg.service.order.report','kg.service.order',
						'addons/kg_service_order/report/kg_service_order_report.rml',
						parser=kg_service_order_report, header= False)
