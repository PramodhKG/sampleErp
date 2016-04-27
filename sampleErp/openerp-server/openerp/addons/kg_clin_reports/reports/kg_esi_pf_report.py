import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale

class kg_esi_pf_report(report_sxw.rml_parse):
	_name = 'kg.esi.pf.report'
	
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_esi_pf_report, self).__init__(cr, uid, name, context=context)
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
		
		branch =[]
		dep = []
		
		
		if form['dep_id']:
			ids3=form['dep_id'][0]
			dep.append("emp.department_id = %s"%(ids3))
		if dep:
			dep = 'and '+' or ' .join(dep)
		else:
			dep = ''
			
			
			
		if form['branch']:
			ids1=form['branch'][0]
			branch.append("branch.id = %s"%(ids1))
		
		if branch:
			branch = 'and' + 'or'.join(branch)
		else:
			branch = ''
				
				
				
		if form['filter'] == 'pf':
			self.cr.execute('''
								select emp.name_related as name , 
										emp.emp_code as code,
										emp.join_date as join_date, 
										to_char(cont.pf_eff_date, 'dd-mm-yyyy') as pf_effective_date,
										dept.name as departname
										
										from hr_contract cont 
										
										left join hr_employee emp on(cont.employee_id = emp.id)
										left join hr_department dept on (emp.department_id = dept.id)
										left join kg_branch branch on(branch.id = emp.branch)
										
								where pf_status ='t' '''+ dep + branch + ''' order by emp.name_related''')
			   
			data=self.cr.dictfetchall()
			print "data..................",data
		
				
		
		elif form['filter'] == 'esi':
			self.cr.execute('''
								select emp.name_related as name , 
										emp.emp_code as code,
										emp.join_date as join_date, 
										to_char(cont.esi_eff_date, 'dd-mm-yyyy') as esi_effective_date,
										dept.name as departname
										
										from hr_contract cont 
										
										left join hr_employee emp on(cont.employee_id = emp.id)
										left join hr_department dept on (emp.department_id = dept.id)
										left join kg_branch branch on(branch.id = emp.branch)
										
								where esi = 't' '''+ dep + branch + ''' order by emp.name_related''')
			   
			data=self.cr.dictfetchall()
			print "data..................",data
			
		elif form['filter'] == 'both':
			self.cr.execute('''
								select emp.name_related as name , 
										emp.emp_code as code,
										emp.join_date as join_date, 
										cont.pf_eff_date as pf_effective_date,
										to_char(cont.esi_eff_date, 'dd-mm-yyyy') as esi_effective_date,
										to_char(cont.pf_eff_date, 'dd-mm-yyyy') as pf_effective_date,
										dept.name as departname
										
										from hr_contract cont 
										
										left join hr_employee emp on(cont.employee_id = emp.id)
										left join hr_department dept on (emp.department_id = dept.id)
										left join kg_branch branch on(branch.id = emp.branch)
										
								where pf_status = 't' and esi = 't' '''+ dep + branch + ''' order by emp.name_related''')
			   
			data=self.cr.dictfetchall()
			print "data..................",data
			
			
		elif form['filter'] == 'not_both':
			self.cr.execute('''
								select emp.name_related as name , 
										emp.emp_code as code,
										emp.join_date as join_date, 
										dept.name as departname
										
										from hr_contract cont 
										
										left join hr_employee emp on(cont.employee_id = emp.id)
										left join hr_department dept on (emp.department_id = dept.id)
										left join kg_branch branch on(branch.id = emp.branch)
										
								where pf_status = 'f' and esi = 'f' '''+ dep + branch + ''' order by emp.name_related''')
			   
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
report_sxw.report_sxw('report.kg.esi.pf.report', 'hr.payslip', 
			'addons/kg_clin_reports/reports/kg_esi_pf_report.rml', 
			parser=kg_esi_pf_report, header = False)
	
