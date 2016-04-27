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
from time import strptime, strftime
import collections
logger = logging.getLogger('server')

class onscreen_po_report(report_sxw.rml_parse):
		
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(onscreen_po_report, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_po_data':self.get_po_data,
			'locale':locale,
			'get_po_data_line':self.get_po_data_line,
			
			
		})
		self.context = context
		
	def get_po_data(self,datas):
		
		form = datas['form']
		print "form =================>>>>>>.",form				
		po_id = form['id']
		print "po_id **************************", po_id		
		
		sql = """
				SELECT  distinct on (po.id)
				po.id as po_id,
				to_char(po.date_order,'dd/mm/yyyy') as date, 
				po.name as po_number,
				po.origin as origin,
				po.partner_id as part_id,
				po.state as postate,
				po.amount_total as total,
				po.amount_tax as tax,
				po.notes as remarks,
				po.discount as discount,
				master.name as delivery,
				po.delivery_mode as mode,
				po.payment_mode as pay_mode,			
				part.name as name,
				part.street as str1,
				ct.name as city,
				part.zip as zip,
				st.name as state,
				coun.name as country,
				part.phone as phone,
				part.mobile as cell,
				part.fax as fax,
				part.email as email,
				po.id as order_id
				
				FROM  purchase_order po
				
				join res_partner part on (part.id=po.partner_id)
				left join res_country_state st on(st.id=part.state_id)
				left join res_city ct on(ct.id=part.city)
				left join res_country as coun on(coun.id=part.country_id)
				join kg_deliverytype_master as master on(master.id=po.delivery_type)
				join purchase_order_line as po_line on(po_line.order_id = po.id)
				join purchase_requisition_line as pi_line on(pi_line.id = po_line.pi_line_id)
				join purchase_requisition as pi on(pi.id = pi_line.requisition_id)
				join kg_depindent_line as dep_line on(dep_line.id = pi_line.depindent_line_id)
				join kg_depindent as indent on(indent.id = dep_line.indent_id)
				where po.id=%s """ %(po_id)
		self.cr.execute(sql)				
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
			print "order_id,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,", order_id
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
					print "pi_data -----------------------", pi_data
					print "dep_ids ------------------------->>>", dep_ids
					pi_new_data =  [x for x, y in collections.Counter(pi_data).items()]
					new_data = (', '.join('"' + item + '"' for item in pi_new_data))											
					#pi_new_dep =  [x for x, y in collections.Counter(dep_ids).items()]
					#new_dep_id = (', '.join('"' + item + '"' for item in pi_new_dep))
				#po_dep_id = [ item.encode('ascii') for item in ast.literal_eval(new_dep_id)]							
				print "new_data ----------------------->>>", new_data
				po_pi_data = [ item.encode('ascii') for item in ast.literal_eval(new_data) ]				
				a = ', '.join(po_pi_data)
				#b = ', '.join(po_dep_id)			
				print "list --- to --- string -------->>>", a
				po['pi_data'] = a
				po['dep_name'] = dep_id
					
		return data
		
		
	def get_po_data_line(self,data):
		line_data=[]
		print "data~~~~~~~~~~~~~~~~~~~~~~~~", data
		po_line_id = self.pool.get('purchase.order.line').search(self.cr, self.uid,
						[('order_id', '=', data)], context=None)
		
		po_line_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, po_line_id)
		tot_item = len(po_line_browse)
		po_obj = self.pool.get('purchase.order')
		tax_name = False
		for po_line in po_line_browse:			 
			taxs = po_line.taxes_id
			print "Tax ---------------->>>> ------->>", taxs
			if taxs and len(taxs) !=1:
				tax_name = []
				for tax in taxs:
					print "FOR --tax ----FOR", tax	
					name = tax.name
					tax_name.append(name)					
				new_data = (', '.join('"' + item + '"' for item in tax_name))
				print "new_data ==================>>>>>>>>>", new_data
				if new_data:
					tax_name = [ item.encode('ascii') for item in ast.literal_eval(new_data) ]
					tax_name = ', '.join(tax_name)
				else:
					print "No TAXXXXXXXXXXXXXXXx"
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
			'disc_per': po_line.kg_discount_per + po_line.kg_disc_amt_per
			#'line_tax_amt': po_obj._amount_line_tax(self.cr,self.uid,po_line,context=None),			
			}
			
			line_data.append(line)
			po_obj = self.pool.get('purchase.order')
			print "line...............>>>>>>>>>>>>>>>>>>>==========", line
			
		return line_data	
	   
 
report_sxw.report_sxw('report.onscreen.po.report','purchase.order',
						'addons/kg_purchase_order/report/onscreen_po_report.rml',
						parser=onscreen_po_report, header= False)

