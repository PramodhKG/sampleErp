import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale

class kg_monthly_attend_rpt(report_sxw.rml_parse):
	_name = 'kg.monthly.attend.rpt'
	
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_monthly_attend_rpt, self).__init__(cr, uid, name, context=context)
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
		dep = []
		if form['emp_name']:
			emp_ids1=form['emp_name'][0]
			where_sql.append("mon.employee_id = %s"%(emp_ids1))
							
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql='' 
		print "where_sql --------------------------->>>", where_sql	
		print form['year']
		#print a
		if form['dep_id']:
			ids3=form['dep_id'][0]
			dep.append("emp.department_id = %s"%(ids3))
		if dep:
			dep = 'and '+' or ' .join(dep)
		else:
			dep = ''
		
		#print "aaaaaaaaaaaa............................", a
		
		self.cr.execute('''
		
			  SELECT
			  
			    emp.name_related as emp_name,
			    mon.employee_name as emp_code,
			    mon.mon_tot_days as payable,
			    dept.name as dept_name,
			    mon.cl as cl,
			    mon.on_duty as on_duty,
			    mon.absent as absent,
			    mon.worked as present,
			    mon.no_half_day as h_day,
			    mon.working_days as working,
			    mon.no_leave_day as late
			    
				FROM  kg_monthly_attendance mon
					
				JOIN hr_employee emp ON (emp.id=mon.employee_id)
				left JOIN hr_department dept ON (dept.id=emp.department_id)
				
			  where mon.mon_tot_days > 0 and Extract(month from start_date) = %s and Extract(year from start_date)=%s'''+ where_sql+dep+ '''
			   order by mon.employee_name''',(form['month'],form['year']))
			   
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
		
	"""def _get_end_date(self, data):
		if data.get('form', False) and data['form'].get('date_to', False):
			return data['form']['date_to']
		return ''		   """
report_sxw.report_sxw('report.kg.monthly.attend.rpt', 'hr.payslip', 
			'addons/kg_clin_reports/reports/kg_monthly_attend_rpt.rml', 
			parser=kg_monthly_attend_rpt, header = False)
	
