import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_mobile_bills_report(report_sxw.rml_parse):
	
	_name = 'kg.mobile.bills.report'
	   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_mobile_bills_report, self).__init__(cr, uid, name, context=context)
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
		
		
		employee=[]
		
		
		if form['employee']:
			ids = form['employee'][0]
			employee.append("ded.employee_id = %s" %(ids))
			
		
	
		
		if employee:
			employee = ' and '+' or '.join(employee)
		else:
			employee=''
					
		
		print "employee --------------------------->>>", employee	
		
		self.cr.execute('''
					
				select 	emp.name_related as name,
						emp.emp_code as code,
						emp.work_phone as mobile_no,
						con.tel_allow as limit,
						mob.total_amt as bill_amt
						from kg_mobile_bills mob 
						left join hr_employee emp on(mob.employee_name = emp.id)
						left join hr_contract con on(mob.employee_name = con.employee_id)

					where extract(month from mob.bill_date) >=%s and extract(year from mob.bill_date) <=%s and mob.state = %s'''+ employee + '''
					order by emp.name_related''',(form['month'],form['year'],'confirm'))
			   
		data=self.cr.dictfetchall()
		print "data ------------------------>>>.........", data
		
		for item in data:
			if item['limit']:
				if item['limit'] < item['bill_amt']:
					bal_amt = item['bill_amt'] - item['limit']
					item['bal_amt'] = bal_amt
					print item['bal_amt']
				else:
					item['bal_amt'] = 0
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
  

report_sxw.report_sxw('report.kg.mobile.bills.report', 'hr.payslip', 
			'addons/kg_clin_reports/reports/kg_mobile_bills_report.rml', 
			parser=kg_mobile_bills_report, header = False)

