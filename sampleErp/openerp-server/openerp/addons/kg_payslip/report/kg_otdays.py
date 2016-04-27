import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_otdays(report_sxw.rml_parse):
	
	_name = 'kg.otdays'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_otdays, self).__init__(cr, uid, name, context=context)
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
				
		if form['dep_id']:
			for ids2 in form['dep_id']:
				where_sql.append("emp.department_id = %s"%(ids2))
				
		if form['pay_sch']:
				where_sql.append("con.sal_date= '%s' "%form['pay_sch'])		
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
					
		
		print "where_sql --------------------------->>>", where_sql	
		
		self.cr.execute('''
		
			  SELECT distinct on (emp.id)
				slip.id AS sl_id,
				slip.att_id AS att_id,
				slip.dep_id AS dep_id,
				emp.id as emp_id,
				emp.emp_code as code,
				emp.name_related as emp_name,
				con.wage AS basic,
				con.allowance as alw,
				dep.name as dep_name

				FROM  hr_payslip slip
					
				JOIN hr_employee emp ON (emp.id=slip.employee_id)
				JOIN hr_contract con ON(con.employee_id=slip.employee_id)
				JOIN hr_department dep ON(dep.id=slip.dep_id)

			  where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s '''+ where_sql + '''
			   order by emp.id''',('done', form['date_from'],form['date_to']))
			   
		data=self.cr.dictfetchall()
		data.sort(key=lambda data: data['dep_id'])
		print "data_sort ------------------------>>>.........", data		
		data_emp_grouped = []
		
		gr_tot = 0.0
		if data:
			att_obj = self.pool.get('kg.monthly.attendance')
			
			for item in data:
				emp_id = item['emp_id']
				att_ids = att_obj.search(self.cr, self.uid,[('employee_id','=',emp_id),
							('start_date','>=',form['date_from']),('end_date','<=',form['date_to'])])
				if att_ids:					
					att_rec = att_obj.browse(self.cr,self.uid,att_ids[0])
					ot_day= att_rec.ot
				else:
					ot_day= 0				
				#ot_day= att_rec.ot
				print "ot_day...................", ot_day
				item['ot'] = ot_day
				basic_sal = item['basic']
				one_day_basic = basic_sal / 26
				alw = item['alw']
				one_day_alw = alw / 26
				ear_sal = one_day_basic * ot_day
				ot_alw = one_day_alw * ot_day
				item['ot_amt'] = ot_alw
				item['ear'] = ear_sal
				gr_tot += ot_alw + ear_sal			
			
			item['gr_total'] = gr_tot
		else:
			print "No Data"
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
  

report_sxw.report_sxw('report.kg.otdays', 'hr.payslip', 
			'addons/kg_payslip/report/kg_otdays.rml', 
			parser=kg_otdays, header = False)


"""
data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		gran_tot = 0.0		
		for val in data:
			emp_id = val['emp_id']
			att_rec = self.pool.get('kg.monthly.attendance').browse(self.cr, self.uid, val['att_id'])
			ot_day = att_rec.ot
			val['ot'] = ot_day
			basic_sal = val['basic']
			one_day_basic = basic_sal / 26
			ear_sal = one_day_basic * ot_day
			val['ear'] = ear_sal
			gran_tot += ear_sal
			val['total'] = gran_tot		
					
		return data	
		
		"""
