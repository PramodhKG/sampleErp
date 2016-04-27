import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
from tools import number_to_text_convert_india
import locale
class kg_emp_payslip_rpt(report_sxw.rml_parse):
	
	_name = 'kg.emp.payslip.rpt'
	   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_emp_payslip_rpt, self).__init__(cr, uid, name, context=context)
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
		print ">>>>>>>>>>>",form
		res = {}
		where_sql = []
		dep = []
		print ">>>>>>>>>>form['employee']....................",form['form']['employee']
		
		if form['form']['employee']:
			ids2=form['form']['employee'][0]
			where_sql.append("pay.employee_id = %s"%(ids2))
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
					
		print "where_sql --------------------------->>>", where_sql 
		self.cr.execute('''
		
					SELECT 
							distinct on (emp.id)
							emp.name_related as emp_name,
							emp.join_date as join_date,
							emp.emp_code as emp_code,
							job.name as deisgnation,
							dept.name as dept_name,
							cont.acc_no as account_no,
							cont.pf_acc_no as pf_acc_no,
							cont.pf_percentage as pf_percent,
							cont.esi_percentage as esi_percent,
							slip.slip_id as slip_id,
							mon_att.mon_tot_days as total_days,
							mon_att.leave as lop_days,
							pay.cross_amt as gross_amt,
							pay.tot_sal as total_salary,
							pay.round_val as round_value,
							pay.id as pay_id
							
						FROM  hr_payslip pay
					
						left JOIN hr_employee emp ON (emp.id=pay.employee_id)
						left JOIN hr_department dept ON (dept.id=emp.department_id)
						left JOIN hr_contract cont ON(emp.id = cont.employee_id)
						left JOIN kg_monthly_attendance mon_att ON (emp.id = mon_att.employee_id)
						left JOIN hr_job job ON (job.id = emp.job_id) 
						left JOIN hr_payslip_line slip ON(pay.id = slip.slip_id)
													  
					  where pay.date_from = %s and pay.date_to =%s and pay.state =%s'''+ where_sql+ '''
			   order by emp.id''',(form['form']['date_from'],form['form']['date_to'],'done'))
		
		
		data=self.cr.dictfetchall()
		print "len(data)....................",len(data)
		print "data ::::::::::::::>>>>", data
		for item in data:
			#basic amount
			basic_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid, 
								 [('slip_id','=',item['pay_id']),('code','=','BASIC')])
			if basic_ids:
				basic_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, basic_ids[0])
				item['basic'] = basic_rec.amount
				print "item[basic']..................",item['basic']
				
			#HRA amount
			hra_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid, 
								 [('slip_id','=',item['pay_id']),('name','=','HRA')])
			if hra_ids:
				hra_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, hra_ids[0])
				item['hra'] = hra_rec.amount
				print "item['hra']>>>>>>>>>>>>>>>>>",item['hra']
			 
			#Special Allowance
			spa_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid, 
								 [('slip_id','=',item['pay_id']),('name','=','Special Allowance')])
			if spa_ids != []:
				spa_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, spa_ids[0])
				item['spa'] = spa_rec.amount
				print "spa>>>>>>>>>",item['spa']
			
			#PF Amount
			pf_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,
								  [('slip_id','=',item['pay_id']),('code','=','PF')])
			if pf_ids != []:
				pf_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, pf_ids[0])
				item['pf'] = pf_rec.amount
				print "pf....................",item['pf']
				#Employer PF Contribution
				empr_pf_ids = self.pool.get('kg.emp.contribution').search(self.cr , self.uid ,
								  [('from_date','>=',form['form']['date_from']),('to_date','<=',form['form']['date_to']),
								  ('active','=',True)])
				print "empr_pf_ids.....",empr_pf_ids
				em_rec = self.pool.get('kg.emp.contribution').browse(self.cr,self.uid,empr_pf_ids[0])
				print "em_rec.............",em_rec
				if empr_pf_ids !=[]:
					empr_pf_line_ids = self.pool.get('kg.emp.contribution.line').search(self.cr, self.uid, [('line_entry','=',empr_pf_ids[0])])
					print "empr_pf_line_ids////",empr_pf_line_ids
					for line in empr_pf_line_ids:
						empr_pf_rec = self.pool.get('kg.emp.contribution.line').browse(self.cr,self.uid,line)
						print "empr_pf_rec",empr_pf_rec.emp_contribution
						if empr_pf_rec.emp_contribution == 'pf':
							print "empr_pf_rec.contribution_percentage....",empr_pf_rec.contribution_percentage
							item['empr_pf_con'] = item['basic']*(empr_pf_rec.contribution_percentage/100)
							print "item['empr_pf_con'] ",item['empr_pf_con'] 
			
				
			#ESI Amount
			esi_ids = self.pool.get('hr.payslip.line').search(self.cr , self.uid ,
								  [('slip_id','=',item['pay_id']),('code','=','ESI')])
			print "esi ................",esi_ids
			if esi_ids != []:
				esi_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, esi_ids[0])
				item['esi'] = esi_rec.amount
				print "esi.......................",item['esi']
				#Employer ESI Contribution
				empr_esi_ids = self.pool.get('kg.emp.contribution').search(self.cr , self.uid ,
								  [('from_date','>=',form['form']['date_from']),('to_date','<=',form['form']['date_to']),
								  ('active','=',True)])
				print "empr_esi_ids.....",empr_esi_ids
				empr_pf_rec = self.pool.get('kg.emp.contribution').browse(self.cr,self.uid,empr_esi_ids[0])
				print "em_rec.............",empr_pf_rec
				if empr_esi_ids !=[]:
					empr_esi_line_ids = self.pool.get('kg.emp.contribution.line').search(self.cr, self.uid, [('line_entry','=',empr_pf_ids[0])])
		
					for line in empr_esi_line_ids:
						empr_esi_rec = self.pool.get('kg.emp.contribution.line').browse(self.cr,self.uid,line)
						print "empr_esi_rec",empr_esi_rec.emp_contribution
						if empr_esi_rec.emp_contribution == 'esi':
							print "empr_pf_rec.contribution_percentage....",empr_esi_rec.contribution_percentage
							item['empr_esi_con'] = item['basic']*(empr_esi_rec.contribution_percentage/100)
							print "item['empr_pf_con'] ",item['empr_esi_con'] 
						else:
							continue
			#PT Amount
			print "item['pay_id'].....................", item['pay_id']
			
			pt_ids = self.pool.get('hr.payslip.line').search(self.cr , self.uid ,
								  [('slip_id','=',item['pay_id']),('code','=','PT')])
			print "pt_ids>>>>>>>>>>>>>>>>>>>>",pt_ids
			
			if pt_ids != []:
				pt_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, pt_ids[0])
				item['pt'] = pt_rec.amount
				print "item['pt']>>>>>>>>>",item['pt']
			
		
			if hra_ids and basic_ids and spa_ids:
				gro_amt_list = [item['basic'],item['hra'],item['spa']] 
				item['gross_amt'] = sum(gro_amt_list)
			else:
				gro_amt_list = []
			print "gross_amt...............",item['gross_amt']
			ded_amt_list = []
			if pf_ids:
				ded_amt_list.append(item['pf'])
				if empr_pf_ids:
					item['empr_pf_amt'] = item['empr_pf_con'] 
				else:
					item['empr_pf_amt']=0
					
			if esi_ids:
				ded_amt_list.append(item['esi'])
				if empr_esi_ids:
					item['empr_esi_amt'] = item ['empr_esi_con']
				else:
					item['empr_pf_amt'] = 0
			
			item['ded_amt'] = sum(ded_amt_list)
			print "ded_amt_list.........",item['ded_amt']
			item['net_salary'] = item['gross_amt'] - item['ded_amt']
			text_amount = number_to_text_convert_india.amount_to_text_india(item['net_salary'],"INR:")
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
  

report_sxw.report_sxw('report.kg.emp.payslip.rpt', 'hr.payslip', 
			'addons/kg_payslip/report/kg_emp_payslip_rpt.rml', 
			parser=kg_emp_payslip_rpt, header = False)
