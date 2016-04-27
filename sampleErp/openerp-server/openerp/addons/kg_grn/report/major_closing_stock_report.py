import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from datetime import date
import datetime

class major_closing_stock_report(report_sxw.rml_parse):
	
	_name = 'major.closing.stock.report'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(major_closing_stock_report, self).__init__(cr, uid, name, context=context)
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
		
		where_sql = []
		major = []
		
		
			
		if form['major_name']:
			majorwise = form['major_name'][0]
			major.append("pt.categ_id = %s" %(majorwise))
		
		if major:
			major = ' and '+' or '.join(major)
			
		else:
			major=''
			
		if form['product_type']:
				where_sql.append("pt.type= '%s' "%form['product_type'])
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
			
		print "date............"	, type(form['date'])
		
		
		self.cr.execute('''		
		
			  SELECT  
					pt.categ_id as category,
					
					sum(price_unit * pending_qty) as close_value
					
			   FROM stock_production_lot spl
			   
			   JOIN product_template pt ON (pt.id=spl.product_id)
			   JOIN product_category pc ON (pc.id=pt.categ_id)
			   
			   
			   
			   where spl.product_qty > 0''' + major + where_sql +'''
			   group by pt.categ_id''')
				   
			   
		data=self.cr.dictfetchall()
		print "in_data ::::::::::::::=====>>>>", data
		
		total = 0.0	
		for item in data:
			category_id = item['category']
			catg_rec = self.pool.get('product.category').browse(self.cr, self.uid,category_id)
			item['product_category'] = catg_rec.name
			
			total += item['close_value']
			item['total'] = total
				
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
  

report_sxw.report_sxw('report.major.closing.stock.wizard', 'stock.picking', 
			'addons/kg_grn/report/major_closing_stock_report.rml', 
			parser=major_closing_stock_report, header = False)
			
			
