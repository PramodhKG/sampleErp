
import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from datetime import datetime, date

class dep_indent_to_issue(report_sxw.rml_parse):
	_name = 'report.dep.indent.to.issue'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(dep_indent_to_issue, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_end_date':self._get_end_date,
			'get_data':self.get_data,
			'locale':locale,
		})
		self.context = context
		
	def get_data(self,form):
		res = {}
		"""
	   Write sql or orm queries to get detail as a list of dict
		"""
		where_sql = []
		product = []
		
		if form['dep_id']:
			for ids1 in form['dep_id']:
				where_sql.append("sp.dep_name = %s"%(ids1))
		
		if form['product_id']:
			for ids2 in form['product_id']:
				product.append("sm.product_id = %s"%(ids2))
				
		if product:
			product = 'and ('+' or '.join(product)
			product =  product+')'
		else:
			product = ''
				
		if where_sql:
			where_sql = 'and ('+' or '.join(where_sql)
			where_sql =  where_sql+')'
		else:
			where_sql = ''
		
		print "where_sql --------------------------->>>", where_sql
		print "product --------------------------->>>", product	
		
		self.cr.execute('''
		
			  SELECT 
			  sp.id AS sp_id,
			  sp.type AS type,
			  to_char(sp.date,'dd/mm/yyyy') AS date,
			  sp.date AS tat_date,
			  sp.name AS iss_number,
			  sm.name AS product_name,
 			  uom.name AS uom,
			  sm.po_to_stock_qty AS issue_qty,
			  sm.id AS sm_id,
			  line.qty AS ind_qty,
			  ind.name AS ind_no,
			  to_char(ind.date, 'dd/mm/yyyy') AS ind_date,
			  ind.date AS tat_in_date
			  			  
			  FROM  stock_picking sp

			  JOIN stock_move sm ON (sm.picking_id=sp.id)
			  JOIN product_uom uom ON (uom.id=sm.product_uom)
			  JOIN product_product prd ON (prd.id=sm.product_id)
			  JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
			  JOIN kg_depindent_line line ON (line.id = sm.depindent_line_id)
			  JOIN kg_depindent ind ON (ind.id = line.indent_id)

			  where sp.type=%s and sp.state=%s and sp.date >=%s and sp.date <=%s'''+ where_sql + product + '''
			   order by ind.name''',('out','done',form['date_from'],form['date_to']))
			   
		
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		for sp in data:
			ind_date = sp['tat_in_date']
			iss_date = sp['tat_date']
			fmt = '%Y-%m-%d'
			from_date = ind_date    
			to_date = iss_date
			print "from_date ::::::::::", from_date, "to_date  :::::::::", to_date
			d1 = datetime.strptime(from_date, fmt)
			d2 = datetime.strptime(to_date, fmt)
			daysDiff = str((d2-d1).days)
			print "daysDiff--------------->>", daysDiff
			sp['tat_days'] = daysDiff	
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
  

report_sxw.report_sxw('report.dep.indent.to.issue', 'stock.picking', 
			'addons/kg_grn/report/dep_indent_to_issue.rml', 
			parser=dep_indent_to_issue, header = False)
