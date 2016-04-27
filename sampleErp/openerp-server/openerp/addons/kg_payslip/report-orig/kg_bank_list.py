import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_bank_list(report_sxw.rml_parse):
	
	_name = 'kg.bank.list'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_bank_list, self).__init__(cr, uid, name, context=context)
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
				dep.append("slip.dep_id = %s"%(ids2))		
		
				
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
		
		self.cr.execute('''
		
			  SELECT distinct on (emp.id)
				slip.id AS sl_id,			  
				slip.round_val AS net_sal,			  			  
				emp.name_related as emp_name,
				con.acc_no AS bank_no

				FROM  hr_payslip slip
					
				JOIN hr_employee emp ON (emp.id=slip.employee_id)
				JOIN hr_contract con ON(con.employee_id=slip.employee_id)
			 		 			  

			  where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s'''+ where_sql + dep +'''
			   order by emp.id''',('done', form['date_from'],form['date_to']))
		
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		gran_tot = 0.0
		for val in data:
			amt = val['net_sal']			
			val['net_amt'] = int(amt)
			print "net_amt........................",val['net_amt']		
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
  

report_sxw.report_sxw('report.kg.bank.list', 'hr.payslip', 
			'addons/kg_payslip/report/kg_bank_list.rml', 
			parser=kg_bank_list, header = False)
