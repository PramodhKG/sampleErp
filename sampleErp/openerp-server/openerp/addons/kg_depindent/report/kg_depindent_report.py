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

class kg_depindent_report(report_sxw.rml_parse):
	_name = 'kg.depindent.report'
	_inherit='kg.depindent,kg.depindent.line'
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_depindent_report, self).__init__(cr, uid, name, context=context)
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
				
		if form['dep_id']:
			for ids1 in form['dep_id']:
				where_sql.append("indent.dep_name = %s"%(ids1))
		
		if form['ind_id']:
			for ids2 in form['ind_id']:
				where_sql.append("indent.id = %s"%(ids2))
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
				SELECT  distinct on (indent.id) indent.id as indent_id, to_char(indent.date,'dd/mm/yyyy') as date, 
				indent.name as indent_number,
				indent.dep_name as id,
				dep.dep_name as dep_name,
				dep_user.login as user_name
				FROM  kg_depindent indent
				join kg_depmaster dep  on (dep.id=indent.dep_name)
				join res_users dep_user on (dep_user.id = indent.user_id)
				where indent.date >=%s and indent.date <=%s  '''+ where_sql + '''
				''',(form['date_from'],form['date_to']))
				
		data = self.cr.dictfetchall()
		print "Data ABBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", data
		
		for indent in data:
			part='x'
			indent_id = indent['indent_number']
		return data
		
	def get_data_line(self,data):
		print "get_data_line exexexexexxexexexex"
		line_data=[]
		print "data~~~~~~~~~~~~~~~~~~~~~~~~", data
		indent_line_id = self.pool.get('kg.depindent.line').search(self.cr, self.uid,
						[('indent_id', '=', data)], context=None)
		print "indent_line_id :::::::::::::::", indent_line_id
		
		indent_line_browse = self.pool.get('kg.depindent.line').browse(self.cr, self.uid, indent_line_id)
		print "indent_line_browse :::::::::::::", indent_line_browse
		tot_item = len(indent_line_browse)
		print "tot_item :::::::::::::", tot_item
		for indent_line in indent_line_browse:
			line ={
			'product':indent_line.product_id.name,
			'prod_uom':indent_line.uom.name,
			'prod_qty':indent_line.qty,
			'avail_qty':indent_line.main_store_qty,
			'note': indent_line.note,
			'line_id':indent_line.id,
			'tot_item' : len(indent_line_browse),
			}
			line_data.append(line)
			print "line =================>>", line
		return line_data


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
 
report_sxw.report_sxw('report.kg.depindent.report','kg.depindent','addons/kg_depindent/report/kg_depindent_report.rml',
						parser=kg_depindent_report, header= False)
