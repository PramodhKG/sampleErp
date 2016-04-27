import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_pay_abstract(report_sxw.rml_parse):
	
	_name = 'kg.pay.abstract'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_pay_abstract, self).__init__(cr, uid, name, context=context)
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
				where_sql.append("slip.dep_id = %s"%(ids2))
				
		if form['pay_sch']:
				where_sql.append("con.sal_date= '%s' "%form['pay_sch'])
		
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
					
		
		print "where_sql --------------------------->>>", where_sql	
		
		self.cr.execute('''
		
				SELECT distinct on (dep.id)
										  
				count(slip.id) as no_of_hands,
				sum(slip.tot_allowance) as tot_all,
				sum(slip.tot_deduction) as tot_ded,
				sum(slip.tot_sal) as net_amt,
				sum(slip.round_val) as rounded_amt,
				sum(slip.balance_val) as cf_amt,
				sum(emp.last_month_bal) as bf_amt,
				dep.id as dep_id,
				dep.name as dep_name

				FROM  hr_payslip slip					
				JOIN hr_employee emp ON(emp.id=slip.employee_id)
				JOIN hr_department dep ON(dep.id=slip.dep_id)
				JOIN hr_contract con ON(con.id=slip.contract_id)				

				where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s'''+ where_sql + '''
				group by dep.id order by dep.id''',('done', form['date_from'],form['date_to']))
		
		data=self.cr.dictfetchall()
		print "data ^^^^^^^^^^^^^^^^^^^...", data
		gr_hands = 0.00
		gr_ear = 0.00
		gr_bf = 0.00
		gr_ded = 0.00
		gr_cf = 0.00
		gr_net = 0.00
		gr_rounded = 0.00
		for val in data:
			gr_hands += val['no_of_hands']
			gr_hands = int(gr_hands)
			val['gr_hands'] = gr_hands
			gr_ear += val['tot_all']
			val['gr_ear'] = gr_ear
			gr_bf += val['bf_amt']
			val['gr_bf'] = gr_bf
			gr_ded += val['tot_ded']
			val['gr_ded'] = gr_ded
			gr_cf += val['cf_amt']
			val['gr_cf'] = gr_cf
			gr_net += val['net_amt']
			val['gr_net'] = gr_net
			gr_rounded += val['rounded_amt']
			val['gr_rounded'] = gr_rounded			
		
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
  

report_sxw.report_sxw('report.kg.pay.abstract', 'hr.payslip', 
			'addons/kg_payslip/report/kg_pay_abstract.rml', 
			parser=kg_pay_abstract, header = False)
