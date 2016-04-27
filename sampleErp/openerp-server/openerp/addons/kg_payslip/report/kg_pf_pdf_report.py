import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_pf_pdf_report(report_sxw.rml_parse):
	
	_name = 'kg.pf.pdf.report'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_pf_pdf_report, self).__init__(cr, uid, name, context=context)
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
				con.pf_acc_no AS pf_no,
				att.mon_tot_days AS worked

				FROM  hr_payslip slip
					
				JOIN hr_employee emp ON (emp.id=slip.employee_id)
				JOIN hr_contract con ON(con.employee_id=slip.employee_id)
				JOIN hr_department dep ON(dep.id=slip.dep_id)
				JOIN kg_monthly_attendance att ON(att.id=slip.att_id)			 		 			  

			  where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s and con.pf_status=True '''+ where_sql + '''
			  order by emp.id''',('done', form['date_from'],form['date_to']))
			   
		data=self.cr.dictfetchall()
		data.sort(key=lambda data: data['dep_id'])
		print "data_sort ------------------------>>>.........", data		
		gr_basic = 0.00
		gr_pf = 0.00
		gr_eps = 0.00
		gr_diff = 0.00
		gr_sub = 0.00
		gr_tot = 0.00
		
		if data:
						
			for ele in data:				
				mon_tot_days = ele['worked']
				one_day_basic = ele['basic'] / 26
				if mon_tot_days < 26:								
					pf_basic = one_day_basic * mon_tot_days				
					basic_amt = (round(pf_basic))
					pf_amt = pf_basic * 12 / 100
					if pf_basic > 6500:
						eps_amt = 6500 * 8.33 / 100
					else:
						eps_amt = pf_basic * 8.33 / 100
				else:
					basic_amt =  ele['basic']
					pf_amt = ele['basic'] * 12 / 100
					if ele['basic'] > 6500:
						eps_amt = 6500 * 8.33 / 100
					else:
						eps_amt = ele['basic'] * 8.33 / 100			
				
				pf_amt = (round(pf_amt))
				eps_amt = (round(eps_amt))
				print "pf_amt....................", pf_amt
				ele['basic_amt'] = basic_amt
				ele['pf_amt'] = pf_amt				
				ele['eps_amt'] = eps_amt							
				diff_amt = ele['pf_amt'] - ele['eps_amt']			
				total = ele['pf_amt'] + ele['eps_amt'] + diff_amt						
				ele['total'] = total
				gr_basic += basic_amt
				gr_pf += pf_amt
				gr_eps += eps_amt
				gr_diff += diff_amt
				gr_sub += gr_sub
				gr_tot += total
			contrib = gr_pf + gr_eps
			print "contrib..................",contrib
			val = contrib * 12 /100
			val = (round(val))
			ele['val'] = val
			val1 = gr_basic * 1.1 / 100
			val1 = (round(val1))
			ele['val1'] = val1
			#val2 = gr_eps * 8.33 / 100
			val2 = gr_eps
			ele['val2'] = val2
			val3 = gr_basic * 0.01 / 100
			val3 = (round(val3))
			ele['val3'] = val3
			val4 = gr_basic * 0.5 / 100
			val4 = (round(val4))
			ele['val4'] = val4				
			ele['gr_basic'] = gr_basic
			ele['gr_pf'] = gr_pf
			ele['gr_eps'] = gr_eps
			ele['gr_diff'] = gr_diff
			ele['gr_sub'] = gr_sub
			ele['gr_tot'] = gr_tot
			ele['final_tot'] = val + val1 + val2 + val3 + val4
		else:
			print "No Data Available"
			
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
  

report_sxw.report_sxw('report.kg.pf.pdf.report', 'hr.payslip', 
			'addons/kg_payslip/report/kg_pf_pdf_report.rml', 
			parser=kg_pf_pdf_report, header = False)
