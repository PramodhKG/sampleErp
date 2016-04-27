import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_cumul_ded_report(report_sxw.rml_parse):
	
	_name = 'kg.cumul.ded.report'
	   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_cumul_ded_report, self).__init__(cr, uid, name, context=context)
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
		
			 select 
				
				ded.emp_name as emp_code,
				to_char(ded.date,'dd/mm/yyyy') AS date,
				ded.tot_amt as total_amt,
				ded.period as period,
				ded.pay_amt as repay_amt,
				emp.name_related as emp_name,
				ded.ded_type as deduc_type,
				ded.amt_paid as amt_paid



				from kg_advance_deduction ded
				
				JOIN hr_employee emp ON (emp.id=ded.employee_id)
				

			  where ded.date >=%s and ded.date <=%s and state != %s'''+ employee + '''
			  order by ded.employee_id''',(form['date_from'],form['date_to'],'expire'))
			   
		data=self.cr.dictfetchall()
		print "data ------------------------>>>.........", data
	
		for item in data:
			deduction_type = item['deduc_type']
			print "deduction_type................",deduction_type
			if deduction_type == 'adv':
				item['type'] = 'ADVANCE'
			elif deduction_type == 'ins1':
				item['type'] = 'ACDT.INSU1'
			elif deduction_type == 'ins2':
				item['type'] = 'MEDI.INSU2'
			elif deduction_type == 'tre':
				item['type'] = 'TREATMENT'
			elif deduction_type == 'rent':
				item['type'] = 'RENT'
				
			total_amount = item['total_amt']
			amount_paid = item['amt_paid']
			item['bal_amt'] = total_amount - amount_paid
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
  

report_sxw.report_sxw('report.kg.cumul.ded.wizard', 'hr.payslip', 
			'addons/kg_payslip/report/kg_cumul_ded_report.rml', 
			parser=kg_cumul_ded_report, header = False)
