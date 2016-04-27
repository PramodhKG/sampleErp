import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_leave_balance_rep(report_sxw.rml_parse):
	
	_name = 'kg.leave.balance.rep'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_leave_balance_rep, self).__init__(cr, uid, name, context=context)
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
		employee=[]
		
		
		if form['leave_type']:
				where_sql.append("alloc.leave_type= '%s' "%form['leave_type'])
		if form['dep_id']:
			ids = form['dep_id'][0]
			dep.append("alloc.department_id = %s" %(ids))
		if form['employee']:
			ids = form['employee'][0]
			employee.append("alloc.emp_name = %s" %(ids))
			
		
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
		
		if dep:
			dep = ' and '+' or '.join(dep)
		else:
			dep=''
		
		if employee:
			employee = ' and '+' or '.join(employee)
		else:
			employee=''
					
		
		print "where_sql --------------------------->>>", where_sql	
		
		self.cr.execute('''
		
			 select 
				emp.name_related as employee_name,
				alloc.emp_code as employee_code
				
				



				from hr_holidays alloc
				
				JOIN hr_employee emp ON (emp.id=alloc.emp_name)
				

			  where alloc.start_date >=%s and alloc.end_date <=%s and alloc.expiry != 'True' '''+ where_sql + dep + employee + '''
			  order by alloc.emp_name''',(form['date_from'],form['date_to']))
			   
		data=self.cr.dictfetchall()
		print "data_sort ------------------------>>>.........", data
		
		for item in data:
			hol_obj=self.pool.get('hr.holidays')
			emp_name = item['employee_name']
			if form['leave_type'] == 'cl':
				cl_id=hol_obj.search(self.cr, self.uid, [('expiry','!=',True),('emp_name','=',emp_name),('leave_type','=','cl')])
				print "holiday_id.............",cl_id
				if cl_id:
				
					cl_rec=hol_obj.browse(self.cr, self.uid,cl_id[0])
					item['total_days'] = cl_rec.number_of_days_temp
					item['used_leaves'] = cl_rec.used_leave
					item['remaining_day'] = cl_rec.rem_leave
					
			elif form['leave_type'] == 'sl':
				sl_id=hol_obj.search(self.cr, self.uid, [('expiry','!=',True),('emp_name','=',emp_name),('leave_type','=','sl')])
				print "holiday_id.............",sl_id
				if sl_id:
				
					sl_rec=hol_obj.browse(self.cr, self.uid,sl_id[0])
					item['total_days'] = sl_rec.number_of_days_temp
					item['used_leaves'] = sl_rec.used_leave
					item['remaining_day'] = sl_rec.rem_leave
					
			elif form['leave_type'] == 'el':
				el_id=hol_obj.search(self.cr, self.uid, [('expiry','!=',True),('emp_name','=',emp_name),('leave_type','=','el')])
				print "holiday_id.............",el_id
				if el_id:
				
					el_rec=hol_obj.browse(self.cr, self.uid,el_id[0])
					item['total_days'] = el_rec.number_of_days_temp
					item['used_leaves'] = el_rec.used_leave
					item['remaining_day'] = el_rec.rem_leave
					
			
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
  

report_sxw.report_sxw('report.kg.leave.balance.rep', 'hr.payslip', 
			'addons/kg_payslip/report/kg_leave_balance_rep.rml', 
			parser=kg_leave_balance_rep, header = False)
