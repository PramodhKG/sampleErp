
import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from datetime import datetime, date
import ast


class kg_po_register(report_sxw.rml_parse):
	
	_name = 'kg.po.register'
	_inherit='purchase.order,purchase.order.line'

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_po_register, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_end_date':self._get_end_date,
			'get_data':self.get_data,
			'locale':locale,
			#'get_data_line':self.get_data_line,

		})
		self.context = context
		
	def get_data(self,form):
		
		res = {}
		where_sql = []
		partner = []
		product = []
			
		if form['supplier']:
			for ids1 in form['supplier']:
				partner.append("po.partner_id = %s"%(ids1))
		
		if form['product_id']:
			for ids2 in form['product_id']:
				product.append("pol.product_id = %s"%(ids2))		
				

		if partner:
			partner = 'and ('+' or '.join(partner)
			partner =  partner+')'
			print "partner -------------------------->>>>", partner
		else:
			partner = ''
			
		if product:
			product = 'and ('+' or '.join(product)
			product =  product+')'
			print "product -------------------------->>>>", product
		else:
			product = ''

			
		self.cr.execute('''
		
			  SELECT
			  po.id AS po_id,
			  po.name AS po_no,
			  to_char(po.date_order,'dd/mm/yyyy') AS po_date,
			  po.date_order AS date,
			  po.note AS remark,
			  po.amount_total as total,
			  po.add_text as address,
			  po.amount_tax as taxamt,
			  pol.id as pol_id,
			  pol.product_qty AS qty,
			  pol.pending_qty AS pending_qty,
			  pol.price_unit as rate,
			  pol.kg_discount_per as disc1,
			  pol.kg_disc_amt_per as disc2,			  
			  uom.name AS uom,
			  pt.name AS pro_name,
			  res.name AS su_name,
			  res.street AS str1,
			  res.zip as zip,
			  city.name as city,
			  state.name as state
			  		  
			  			  
			  FROM  purchase_order po
			  			  
			  JOIN res_partner res ON (res.id=po.partner_id)
			  left join res_city city on(city.id=res.city)
			  left join res_country_state state on(state.id=res.state_id)
			  JOIN purchase_order_line pol ON (pol.order_id=po.id)
			  JOIN product_product prd ON (prd.id=pol.product_id)
			  JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
			  JOIN product_uom uom ON (uom.id=pol.product_uom)
			  

			  where po.state=%s and pol.line_state != %s and po.date_order >=%s and po.date_order <=%s '''+ product + partner + '''
			  order by po.name''',('approved','cancel',form['date_from'],form['date_to']))
			   
		data=self.cr.dictfetchall()
		#print "data ::::::::::::::=====>>>>", data										
		new_data = []
		count = 0
		gr_total = 0
		pol_obj = self.pool.get('purchase.order.line')
		for pos1, item1 in enumerate(data):
			if item1['disc1'] == None:
				item1['disc1'] = 0.00
			else:
				item1['disc1'] = item1['disc1']
				
			if item1['disc2'] == None:
				item1['disc2'] = 0.00
			else:
				item1['disc2'] = item1['disc2']							
			delete_items = []
			po_no = item1['po_no']
			print "po_no,,,,,,,,,,,,,,",po_no
			order_id = item1['po_id']
			po_date = item1['date']
			print "date,,,,,,,,,,,,,,,",po_date
			fmt = '%Y-%m-%d'
			from_date = po_date    
			to_date = date.today()
			to_date = str(to_date)
			d1 = datetime.strptime(from_date, fmt)
			d2 = datetime.strptime(to_date, fmt)
			daysDiff = str((d2-d1).days)
			print "daysDiff--------------->>", daysDiff
			item1['pending_days'] = daysDiff
			pol_rec = pol_obj.browse(self.cr, self.uid,item1['pol_id'])
			taxes = pol_rec.taxes_id
			if taxes and len(taxes) !=1:				
				tax_name = []
				for tax in taxes:
					name = tax.name
					tax_name.append(name)
					a = (', '.join('"' + item + '"' for item in tax_name))
					tax = [ item.encode('ascii') for item in ast.literal_eval(a) ]
					po_tax = ', '.join(tax)
					item1['tax'] = po_tax
			else:
				if taxes:						
					po_tax = taxes[0].name
					item1['tax'] = po_tax
			gr_total += item1['total']
			print "gr_total.........................>>>",gr_total
			
			for pos2, item2 in enumerate(data):
				if not pos1 == pos2:
					if item1['po_id'] == item2['po_id'] and item1['su_name'] == item2['su_name']:												
						if count == 0:
							new_data.append(item1)
							print "new_data.............",new_data
							count = count + 1
						item2_2 = item2
						item2_2['su_name'] = ''
						item2_2['str1'] = ''
						item2_2['zip'] = ''
						item2_2['city'] = ''
						item2_2['state'] = ''
						item2_2['po_no'] = ''
						item2_2['po_date'] = ''
						item2_2['address']=''
						item2_2['total']=0
						new_data.append(item2_2)
						print "new_data2.............>",new_data
						delete_items.append(item2)
				
				else:
					print "Few PO have one line"
					
		item1['gr_total'] = gr_total
		return data
		
		
	def _get_filter(self, data):
		if data.get('form', False) and data['form'].get('filter', False):
			if data['form']['filter'] == 'filter_date':
				return _('Date')
			
		return _('No Filter')
		
	def _get_start_date(self, data):
		if data.get('form', False) and data['form'].get('date_from', False):
			return data['form']['date_from']
		return ''
		
	def _get_end_date(self, data):
		if data.get('form', False) and data['form'].get('date_to', False):
			return data['form']['date_to']
		return ''		   
  

report_sxw.report_sxw('report.kg.po.register', 'purchase.order', 
			'addons/kg_po_reports/report/kg_po_register.rml', 
			parser=kg_po_register, header = False)
