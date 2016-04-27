import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
from tools import number_to_text_convert_india
import locale
class onscreen_emp_payslip(report_sxw.rml_parse):
	
	_name = 'onscreen.emp.payslip'
	   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(onscreen_emp_payslip, self).__init__(cr, uid, name, context=context)
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
		print "form   ",form
		print "form [form]",form['form']['date_from']
					
		self.cr.execute('''
					SELECT
							distinct on (emp.id)
							emp.name_related as emp_name,
							dept.name as dept_name,
							emp.emp_code as code,
							to_char(emp.join_date,'dd-mm-yyyy') as join_date,
							br.name as branch,
							pay.con_cross_amt as cont_gross,
							pay.cross_amt as gross_amt,
							pay.round_val as net_sal,
							job.name as designation,
							emp.work_phone as mob_num,
							att.worked as pre_days,
							line.slip_id as slip_id,
							cont.payment_mode as payment_mode,
							cont.acc_no as account_no,
							cont.pf_status as pf_status,
							cont.pf_acc_no as pf_acc_no,
							cont.esi as esi_status,
							cont.esi_acc_no as esi_acc_no,
							pay.month as month_year,
							att.leave as lop_days,
							cont.gross_salary as gross_salary
							
							
							FROM  hr_payslip pay
							
							
							
							left JOIN hr_employee emp ON (emp.id=pay.employee_id)
							left JOIN hr_department dept ON (emp.department_id=dept.id)
							left JOIN hr_job job ON (emp.job_id=job.id)
							left JOIN hr_contract cont ON (cont.employee_id=emp.id)
							left join kg_branch br on (emp.branch = br.id)
							left join hr_payslip_line line on (pay.employee_id=line.employee_id)
							left join kg_monthly_attendance att on(pay.employee_id= att.employee_id)
							
							
							where date_from = %s  and date_to = %s
							and pay.id = %s and pay.state= 'done' 
							order by emp.id''',(form['form']['date_from'],form['form']['date_to'],form['form']['id']))
		
		
		data=self.cr.dictfetchall()
		print "data ::::::::::::::>>>>", data
		
		empr_cont_obj = self.pool.get('kg.emp.contribution')
		empr_cont_ids = empr_cont_obj.search(self.cr,self.uid,[('active','=','True')])
		
		empr_line_obj = self.pool.get('kg.emp.contribution.line')
		empr_cont_lne = empr_line_obj.search(self.cr,self.uid,[('emp_cont_line_entry','=',empr_cont_ids[0])])
		 
		for item in data:
			line_ids = self.pool.get('hr.payslip.line').search(self.cr,self.uid,[('slip_id','=',item['slip_id'])])
			for ids in empr_cont_lne:
				empr_line_rec =  empr_line_obj.browse(self.cr,self.uid,ids)
				print "empr_line_rec",empr_line_rec.cont_type
				if empr_line_rec.emp_contribution == 'pf':
					if empr_line_rec.cont_type == 'percent':
						empr_pf = (item['gross_salary'] * empr_line_rec.emp_cont_value)/100
					else:
						empr_pf = empr_line_rec.emp_cont_value
				if empr_line_rec.emp_contribution == 'esi':
					if empr_line_rec.cont_type == 'percent':
						empr_esi = (item['gross_salary'] * empr_line_rec.emp_cont_value)/100
					else:
						empr_esi = empr_line_rec.emp_cont_value
						 
				if item['pf_status'] == True and empr_line_rec.emp_contribution == 'pf':
					item['empr_pf'] = empr_pf
					print "item['empr_pf']",item['empr_pf']
				
				if item['esi_status'] == True and empr_line_rec.emp_contribution == 'esi':
					item['empr_esi'] = empr_esi
					print "item['empr_esi']",item['empr_esi']
				
			
			
			for ids in line_ids:
				line_rec = self.pool.get('hr.payslip.line').browse(self.cr,self.uid,ids)
				print "line_recs           ............    ",line_rec.code
				if item['mob_num']:
					if len(item['mob_num']) >= 10:
						item['mob_num_1'] = item['mob_num'][:10]
						item['mob_num_2'] = item['mob_num'][11:]
				else:
					item['mob_num'] = ' ' 
				if line_rec.code == 'BASIC':
					item['basic'] = line_rec.amount
				if line_rec.code == 'DA':
					item['da'] = line_rec.amount
				if line_rec.code == 'HRA':
					item['hra'] = line_rec.amount
				if line_rec.code == 'CON':
					item['con'] = line_rec.amount
				if line_rec.code == 'TA':
					item['ta'] = line_rec.amount
				if line_rec.code == 'PF':
					item['pf'] = line_rec.amount
					print "pf     ",item['pf']
				
				if line_rec.code == 'ESI':
					item['esi'] = line_rec.amount
					print "esi     ",item['esi']
								
					
 				if line_rec.code == 'ADVDED':
					item['sal_adv'] = line_rec.amount
					print "item['sal_adv']",item['sal_adv']
					
				if line_rec.code == 'MD':
					item['mob_ded'] = line_rec.amount
					print "mob_ded     ",item['mob_ded']
				else:
					item['mob_ded'] = 0
					
					
				if line_rec.code == 'ITAX':
					item['itax'] = line_rec.amount
					
					
				if line_rec.code == 'EMP_PF':
					item['emp_pf'] = line_rec.amount
					
					
				if line_rec.code == 'EMP_ESI':
					item['emp_esi'] = line_rec.amount
				
				if line_rec.code == 'PT':
					item['pt'] = line_rec.amount
			
				
				text_amount = number_to_text_convert_india.amount_to_text_india(item['net_sal'],"INR:")
				item['amt_in_words']=text_amount
			
	
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
  

report_sxw.report_sxw('report.onscreen.emp.payslip', 'hr.payslip', 
			'addons/kg_payslip/report/onscreen_emp_payslip.rml', 
			parser=onscreen_emp_payslip, header = False)
