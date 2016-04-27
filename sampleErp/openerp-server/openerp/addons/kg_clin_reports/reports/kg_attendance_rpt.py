import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale

class kg_attendance_rpt(report_sxw.rml_parse):
	_name = 'kg.attendance.rpt'
	
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_attendance_rpt, self).__init__(cr, uid, name, context=context)
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
		dep = []		
		
		if form['emp_name']:
			ids2=form['emp_name'][0]
			where_sql.append("att.employee_id = %s"%(ids2))
		
		if form['dep_id']:
			for ids3 in form['dep_id']:
				dep.append("emp.department_id = %s"%(ids3))
				
		if dep:
			dep = ' and '+' or '.join(dep)
		else:
			dep=''
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
					
		print "where_sql --------------------------->>>", where_sql	
		print form['year']
		self.cr.execute('''
		
			  SELECT
			
			    emp.name_related as emp_name,
			    att.status as emp_status,
			    att.employee_code as emp_code,
			    att.duration as duration,
			    att.in_time as in_time,
			    att.out_time as out_time
			    
				FROM  kg_daily_attendance att
					
				JOIN hr_employee emp ON (emp.id=att.employee_id)
				
			  where extract(month from att.date) >=%s and extract(year from att.date )<=%s '''+ where_sql+ dep  + '''
			   order by att.id''',(form['month'],form['year']))
			   
		data=self.cr.dictfetchall()
		print "data..................",data
		return data
		
	def _get_filter(self, data):
		if data.get('form', False) and data['form'].get('filter', False):
			if data['form']['filter'] == 'filter_date':
				return _('Date')
			
		return _('No Filter')
		
	def _get_start_date(self, data):
		if data.get('form', False) and data['form'].get('month', False):
			return data['form']['month']
		return ''
		
	def _get_end_date(self, data):
		if data.get('form', False) and data['form'].get('year', False):
			return data['form']['year']
		return ''		   
report_sxw.report_sxw('report.kg.attendance.rpt', 'hr.payslip', 
			'addons/kg_clin_reports/reports/kg_attendance_rpt.rml', 
			parser=kg_attendance_rpt, header = False)
