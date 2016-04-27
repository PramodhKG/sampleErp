import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale

class onscreen_salary_muster(report_sxw.rml_parse):
	
	
	def __init__(self, cr, uid, name, context=None):
		if context is None: 
			context = {}
		super(onscreen_salary_muster, self).__init__(cr, uid, name, context=context)
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
	
		
		self.cr.execute('''
		
			  SELECT
			    distinct on (emp.id)
			    emp.name_related as emp_name,
			    emp.emp_code as code,
				br.name as branch,
				pay.con_cross_amt as cont_gross,
				pay.cross_amt as gross_amt,
				pay.round_val as net_sal,
				job.name as designation,
				emp.work_phone as mob_num,
				att.worked as pre_days,
				line.slip_id as slip_id,
				slip.name as month_name
				
				FROM  hr_payslip_run slip 
				left join hr_payslip pay on (pay.payslip_run_id = slip.id)
				left JOIN hr_employee emp ON (emp.id=pay.employee_id)
				left join kg_branch br on (emp.branch = br.id)
				left join hr_payslip_line line on (pay.employee_id=line.employee_id)
				left join hr_job job on (emp.job_id = job.id)
				left join kg_monthly_attendance att on(pay.employee_id= att.employee_id)
			  where date_from =%s and date_to =%s and pay.state = 'done'
			   ''',(form['date_start'],form['date_end']))

		data=self.cr.dictfetchall()
		print "data..................",data
		
		
		
		tot_pre_days = 0.00
		tot_gross = 0.00
		tot_basic = 0.00
		tot_da = 0.00
		tot_hra = 0.00
		tot_con = 0.00
		tot_ma = 0.00
		tot_net_gross = 0.00
		tot_pf = 0.00
		tot_esi = 0.00
		tot_mob_ded = 0.00
		tot_sal_adv = 0.00
		tot_other_ded = 0.00
		tot_take_hme_sal = 0.00
		
		
		for item in data:
			print "             ",item['cont_gross']  
			amt = []
			line_ids = self.pool.get('hr.payslip.line').search(self.cr,self.uid,[('slip_id','=',item['slip_id'])])
			print "line_ids             ....................   ",line_ids
			for ids in line_ids:
				line_rec = self.pool.get('hr.payslip.line').browse(self.cr,self.uid,ids)
				print "line_recs           ............    ",line_rec.code
				if item['mob_num']:
					if len(item['mob_num']) >= 10:
						item['mob_num_1'] = item['mob_num'][:10]
						item['mob_num_2'] = item['mob_num'][11:]
				if line_rec.code == 'BASIC':
					item['basic'] = line_rec.amount
				if line_rec.code == 'DA':
					item['da'] = line_rec.amount
				if line_rec.code == 'HRA':
					item['hra'] = line_rec.amount
				if line_rec.code == 'CON':
					item['con'] = line_rec.amount
				if line_rec.code == 'tA':
					item['ta'] = line_rec.amount
				if line_rec.code == 'PF':
					item['pf'] = line_rec.amount
					print "pf     ",item['pf']
				else:	
					item['pf'] = 0
						
					
				if line_rec.code == 'ESI':
					item['esi'] = line_rec.amount
					print "esi     ",item['esi']
				else:	
					item['esi'] = 0
					
					
 				if line_rec.code == 'ADVDED':
					item['sal_adv'] = line_rec.amount
				else:
					item['sal_adv'] = 0
					
					
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
			
			
			tot_gross += item['cont_gross']
			item['tot_gross'] = tot_gross
			print "tot_gross..........",item['tot_gross']
			
			tot_pre_days += item['pre_days']
			item['tot_pre_days'] = tot_pre_days
			
			tot_basic += item['basic']
			item['tot_basic'] = tot_basic
			
			tot_da += item['da']
			item['tot_da'] = tot_da
		
			tot_hra += item['hra']
			item['tot_hra'] = tot_hra
			
			tot_con += item['con']
			item['tot_con'] = tot_con
			
			tot_ma += item['ta']
			item['tot_ta'] = tot_ta
			
			tot_net_gross += item['gross_amt']
			item['tot_net_gross'] = tot_net_gross
			
			if item.has_key('pf'):
				tot_pf += item['pf']
				item['tot_pf'] = tot_pf
			
			if item.has_key('esi'):
				tot_esi += item['esi']
				item['tot_esi'] = tot_esi
			
			if item.has_key('mob_ded'):
				tot_mob_ded += item['mob_ded']
				item['tot_mob_ded'] = tot_mob_ded
			
			if item.has_key('sal_adv'):
				tot_sal_adv += item['sal_adv']
				item['tot_sal_adv'] = tot_sal_adv
			
			if item.has_key('itax'):
				tot_other_ded += item['itax']
			if item.has_key('emp_pf'):
				tot_other_ded += item['emp_pf']
			if item.has_key('emp_esi'):
				tot_other_ded += item['emp_esi']
			if item.has_key('pt'):
				tot_other_ded += item['pt']
				item['tot_other_ded'] = tot_other_ded
				 
				 
			tot_take_hme_sal += item['net_sal']
			item['tot_take_hme_sal'] = tot_take_hme_sal 
				
		return data
		
	def _get_filter(self, data):
		if data.get('form', False) and data['form'].get('filter', False):
			if data['form']['filter'] == 'filter_date':
				return _('Date')
		return _('No Filter')
		
		
	def _get_start_date(self, data):
		if data.get('form', False) and data['form'].get('date_start', False):
			return data['form']['date_start']
		return ''
		
	def _get_end_date(self, data):
		if data.get('form', False) and data['form'].get('date_end', False):
			return data['form']['date_end']
		return ''		

report_sxw.report_sxw('report.onscreen.salary.muster', 'hr.payslip', 
			'addons/kg_payslip/report/onscreen_salary_muster.rml', 
			parser=onscreen_salary_muster, header= False)
			
			
