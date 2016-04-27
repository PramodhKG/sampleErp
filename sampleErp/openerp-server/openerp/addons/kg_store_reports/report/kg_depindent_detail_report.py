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

class kg_depindent_detail_report(report_sxw.rml_parse):
	
	_name = 'kg.depindent.detail.report'
	
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_depindent_detail_report, self).__init__(cr, uid, name, context=context)
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
				
		if form['dep_id']:
			for ids1 in form['dep_id']:
				where_sql.append("indent.dep_name = %s"%(ids1))
		
		
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
				
				indent.date as indent_date,
				indent.name as indent_number,
				indent.dep_name as dep_id,
				dep.dep_name as department_name,
				dep_line.product_id as product_id,
				dep_line.uom as uom,
				dep_line.qty as indent_qty,
				dep_line.pending_qty as pi_pending_qty,
				dep_line.issue_pending_qty as issue_pending_qty,
				product.name_template as product_name,
				uom.name as product_uom,
				indent.state as status
				
			
				
				FROM  kg_depindent indent
				
				join kg_depmaster dep  on (dep.id=indent.dep_name)
				join kg_depindent_line dep_line  on (indent.id=dep_line.indent_id)
				join product_product product  on (product.id=dep_line.product_id)
				join product_uom uom on (uom.id=dep_line.uom)
				
				
				
				where indent.date >=%s and indent.date <=%s and indent.state != 'draft' '''+ where_sql + '''
				order by indent.name ''',(form['date_from'],form['date_to']))
				
		data = self.cr.dictfetchall()
		print "Data ABBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", data
		
		gr_pi_qty = 0.0
		gr_indent_qty =0.0
		gr_issue_qty =0.0
		count = 0
		new_data = []
		
		for pos1, item1 in enumerate(data):
			pi_pending_qty = item1['pi_pending_qty']
			issue_pending_qty = item1['issue_pending_qty']
			indent_qty = item1['indent_qty']
			
			gr_pi_qty += pi_pending_qty
			gr_indent_qty += indent_qty
			gr_issue_qty += issue_pending_qty
			
			item1['gr_indent_qty'] = gr_indent_qty
			item1['gr_pi_qty'] = gr_pi_qty
			item1['gr_issue_qty'] = gr_issue_qty
			
			
			if item1['status'] == 'confirm':
				item1['status'] = 'Waiting for Approval'
			elif item1['status'] == 'approved':
				item1['status'] = 'Approved'
				
			elif item1['status'] == 'cancel':
				item1['status'] = 'Cancelled'
				
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
						item2_2['department_name'] = ''
						
						
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
 
report_sxw.report_sxw('report.kg.depindent.detail.report','kg.depindent','addons/kg_store_reports/report/kg_depindent_detail_report.rml',
						parser=kg_depindent_detail_report, header= False)
