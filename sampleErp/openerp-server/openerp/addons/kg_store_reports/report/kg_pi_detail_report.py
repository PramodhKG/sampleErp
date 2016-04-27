import time
from report import report_sxw
from osv import osv
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

class kg_pi_detail_report(report_sxw.rml_parse):
	
	_name = 'kg.pi.detail.report'
	
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_pi_detail_report, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_end_date':self._get_end_date,
			'get_data':self.get_data,
			'locale':locale
			
			
			
		})
		self.context = context

	def get_data(self,form):
		res = {}
		where_sql = []
		
		
		if form['filter'] == 'filter_no':
			form['date_from'] = None
			form['date_to'] = None
		else:
			form['date_from'] = form['date_from']
			form['date_to'] = form['date_to']
			

		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
			
		else:
			where_sql=''		
			
		print "where_sql.............................", where_sql	
		
		self.cr.execute('''
				
				SELECT 
				
				pi.date_start as indent_date,
				pi.name as indent_number,
				product.name_template as product_name,
				pi_line.product_qty as pi_qty,
				pi_line.dep_indent_qty as di_qty,
				pi_line.pending_qty as pending_qty,
				uom.name as product_uom
				
				
				
				
			
				
				FROM  purchase_requisition pi
				
				join purchase_requisition_line pi_line on (pi.id=pi_line.requisition_id)
				join product_product product  on (product.id=pi_line.product_id)
				join product_uom uom on (uom.id=pi_line.product_uom_id)
				
				
				
				
				where pi.date_start >=%s and pi.date_start <=%s and pi.state = 'approved' '''+ where_sql + '''
				order by pi.name ''',(form['date_from'],form['date_to']))
				
		data = self.cr.dictfetchall()
		print "Data ABBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", data
		
		gr_pi_qty = 0.0
		gr_di_qty =0.0
		gr_pending_qty =0.0
		count = 0
		new_data = []
		
		for pos1, item1 in enumerate(data):
			pi_pending_qty = item1['pending_qty']
			di_qty = item1['di_qty']
			pi_qty = item1['pi_qty']
			
			gr_pending_qty += pi_pending_qty
			gr_di_qty += di_qty
			gr_pi_qty += pi_qty
			
			item1['gr_pending_qty'] = gr_pending_qty
			item1['gr_di_qty'] = gr_di_qty
			item1['gr_pi_qty'] = gr_pi_qty
				
			delete_items = []	
			for pos2, item2 in enumerate(data):
				if not pos1 == pos2:
					if item1['indent_number'] == item2['indent_number']:
						
												
						if count == 0:
							new_data.append(item1)
							print "new_data -------------------------------->>>>", new_data
							count = count + 1
						item2_2 = item2
						item2_2['indent_number'] = ''
						item2_2['indent_date'] = ''
						
						new_data.append(item2_2)
						print "new_data 2222222222222222", new_data
						delete_items.append(item2)
						print "delete_items _____________________>>>>>", delete_items
				else:
					print "Few Indent have one line"
				
			
		
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
 
report_sxw.report_sxw('report.kg.pi.detail.report','purchase.requisition','addons/kg_store_reports/report/kg_pi_detail_report.rml',
						parser=kg_pi_detail_report, header= False)
