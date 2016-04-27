import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale

class kg_salary_master_rpt(report_sxw.rml_parse):
	_name = 'kg.salary.master.rpt'
	
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_salary_master_rpt, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_data':self.get_data,
			'locale':locale,
		})
		self.context = context
		
	def get_data(self,form):
		res = {}
		where_sql = []
		
		if form['emp_name']:
			emp_ids1=form['emp_name']
			where_sql.append("mon.employee_id = %s"%(emp_ids1))
							
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql='' 
		print "where_sql --------------------------->>>", where_sql	
		a = tuple(form['month'])
		
		print "aaaaaaaaaaaa............................", a
		
		self.cr.execute('''
		
			  SELECT
			  
			     
			    employee_id as emp_id,
			    state as state,
			    name as name,
			    contract_id as c_id
			    
				FROM  hr_payslip ''')
				
			   
		data=self.cr.dictfetchall()
		print "data..................",data
		return data
		
	def _get_filter(self, data):
		if data.get('form', False) and data['form'].get('filter', False):
			if data['form']['filter'] == 'filter_month':
				return _('Date')
			
		return _('No Filter')
		
	def _get_start_date(self, data):
		if data.get('form', False) and data['form'].get('month', False):
			return data['form']['month']
		return ''
report_sxw.report_sxw('report.kg.salary.master.rpt', 'hr.payslip', 
			'addons/kg_clin_reports/reports/kg_salary_master_rpt.rml', 
			parser=kg_salary_master_rpt, header = False)
	
