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
				

		self.cr.execute('''
		
			  
						SELECT distinct on (emp.id)
										slip.id AS sl_id,
										slip.att_id AS att_id,
										slip.dep_id AS dep_id,
										emp.id as emp_id,
										emp.emp_code as code,
										emp.name_related as emp_name,
										con.pf_acc_no AS pf_no,
										att.worked AS worked,
										con.id as con_id

										FROM  hr_payslip slip

										left JOIN hr_employee emp ON (emp.id=slip.employee_id)
										left JOIN hr_contract con ON(con.employee_id=slip.employee_id)
										left JOIN hr_department dep ON(dep.id=slip.dep_id)
										left JOIN kg_monthly_attendance att ON(att.employee_id=slip.employee_id)			 		 			  

						where slip.state=%s and extract(month from slip.date_from) >=%s and extract(year from slip.date_to) <=%s and con.pf_status=True 
						order by emp.id''',('done', form['month'],form['year']))
			   
		data=self.cr.dictfetchall()
		data.sort(key=lambda data: data['dep_id'])
		print "data_sort ------------------------>>>.........", data		
		gr_basic = 0.00
		gr_pf = 0.00
		gr_eps = 0.00
		gr_diff = 0.00
		gr_sub = 0.00
		gr_tot = 0.00
		one_day_pf = 0.00
		
		
		con_obj = self.pool.get('hr.contract')
		sal_obj = self.pool.get('kg.salary.detail')
		
		
		
		if data:
						
			for ele in data:				
				print  ele['emp_name']
				
				sal_ids = sal_obj.search(self.cr,self.uid,[('salary_id','=',ele['con_id'])])
				con_rec = con_obj.browse(self.cr,self.uid,ele['con_id'])
				gross_amt = con_rec.gross_salary
				for ids in sal_ids:
					
					sal_rec = sal_obj.browse(self.cr,self.uid,ids)
					mon_tot_days = ele['worked']
					
					
					if sal_rec.type == 'fixed_amt':
						if sal_rec.salary_type.code == 'BASIC' or sal_rec.salary_type.code == 'DA':
							one_day_basic = sal_rec.salary_amount / 26
							print "one_day_basic",one_day_basic
					else:
						if sal_rec.salary_type.code == 'BASIC' or sal_rec.salary_type.code == 'DA':	
							one_day_basic = ((sal_rec.salary_amount * gross_amt)/100)/26
							print "one_day_basic",one_day_basic
							
							
					if sal_rec.salary_type.code == 'BASIC' or sal_rec.salary_type.code == 'DA':		
						one_day_pf += one_day_basic	
						
						
					print "one_day_basic",one_day_pf	
					if mon_tot_days:						
						pf_basic = one_day_pf * mon_tot_days	
					else:
						pf_basic = 0.00
					basic_amt = (round(pf_basic))
					pf_amt = basic_amt * 12 / 100
					eps_amt = basic_amt * 8.33 / 100
				
				pf_amt = (round(pf_amt))
				eps_amt = (round(eps_amt))
				print "pf_amt....................", pf_amt
				print "eps_amt....................", eps_amt
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
			print "gr_sub..................",gr_sub
			
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
			'addons/kg_clin_reports/reports/kg_pf_pdf_report.rml', 
			parser=kg_pf_pdf_report, header = False)
