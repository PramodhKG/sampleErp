import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale



class kg_clin_pay_report(report_sxw.rml_parse):
	
	_name = 'kg.clin_pay_report'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_clin_pay_report, self).__init__(cr, uid, name, context=context)
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
		
		
		where_sql = []
		dep = []
		
		
		
				
		if form['dep_id']:
			for ids2 in form['dep_id']:
				dep.append("emp.department_id = %s"%(ids2))
				
		
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
			
			
		if dep:
			dep = 'and ('+' or '.join(dep)
			dep =  dep+')'
		else:
			dep = ''
		
		print "where_sql --------------------------->>>", where_sql	
		print "dep --------------------------->>>", dep
		print "form['date_from'],form['date_to']", form['date_from'],form['date_to']
		
		
		self.cr.execute('''
		
			  SELECT 
			  
			  slip.emp_name as emp_code
			  
			  from hr_payslip slip
			 		 			  

			  where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s'''+ dep + '''
				order by slip.employee_id''',('done', form['date_from'],form['date_to']))
		
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		
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
		
  

report_sxw.report_sxw('report.kg.clin.pay.wizard', 'hr.payslip', 
			'addons/kg_payslip/report/kg_clin_pay_report.rml', 
			parser=kg_clin_pay_report, header = False)
