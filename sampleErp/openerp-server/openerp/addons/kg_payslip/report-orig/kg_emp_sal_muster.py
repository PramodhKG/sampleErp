import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_emp_sal_muster(report_sxw.rml_parse):
	
	_name = 'kg.emp.sal.muster'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_emp_sal_muster, self).__init__(cr, uid, name, context=context)
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
		slip = []
		dep = []
		
		if form['slip_id']:
			for ids1 in form['slip_id']:
				slip.append("slip.id = %s"%(ids1))
				
		if form['dep_id']:
			for ids2 in form['dep_id']:
				dep.append("emp.department_id = %s"%(ids2))		
		
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
			
		if slip:
			slip = 'and ('+' or '.join(slip)
			slip =  slip+')'
		else:
			slip = ''
			
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
			  slip.tot_allowance AS ear,
			  slip.tot_deduction AS ded,
			  slip.round_val AS net_sal,
			  slip.cross_amt AS gross,
			  emp.emp_code as code,
			  emp.name_related as emp_name,
			  emp.last_month_bal as bal_val,
			  to_char(emp.join_date,'dd/mm/yyyy') AS j_date,
			  con.acc_no AS bank_no,
			  con.pf_acc_no AS pf_no,
			  att.worked AS tot_day		  
			  
			  FROM  hr_payslip slip
			  			
			JOIN hr_employee emp ON (emp.id=slip.employee_id)
			JOIN hr_contract con ON (con.id=slip.contract_id)
			JOIN kg_monthly_attendance att ON (att.id=slip.att_id)
			 		 			  

			  where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s'''+ where_sql + '''
				order by emp.id''',('done', form['date_from'],form['date_to']))
		
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		gran_tot = 0.0
		for val in data:			
			amt = val['net_sal']
			print "amt................",amt
			gran_tot += amt
			val['total'] = gran_tot
			print "slip_id..................", val['sl_id']
			
			# Basic
			
			basic_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','BASIC')])
			if basic_ids:
				basic_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, basic_ids[0])
				basic_amt = basic_rec.amount
				val['basic_amt'] = basic_amt
			else:
				pass
			
			# Allowance
							
			allowance_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','ALW')])
			if allowance_ids:
				allowance_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, allowance_ids[0])
				alw_amt = allowance_rec.amount
				val['alw_amt'] = alw_amt
			else:
				pass
							
			# Over Time
							
			ot_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','OT')])
			
			if ot_ids:
				ot_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ot_ids[0])
				ot_amt = ot_rec.amount
				val['ot_amt'] = ot_amt
			else:
				pass
				
			# PF
							
			pf_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','PF')])
			if pf_ids:
				pf_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, pf_ids[0])
				pf_amt = pf_rec.amount
				val['pf_amt'] = pf_amt
			else:
				pass
					
			# ESI
			
			esi_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','ESI')])
			if esi_ids:
				esi_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, esi_ids[0])
				esi_amt = esi_rec.amount
				val['esi_amt'] = esi_amt
			else:
				pass
			
			# Personal Advance
							
			advance_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','PADV')])
			if advance_ids:
				advance_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, advance_ids[0])
				adv_amt = allowance_rec.amount
				val['adv_amt'] = adv_amt
			else:
				pass
							
			# Canteen
			
			cant_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','CANT')])
			if cant_ids:
				cant_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, cant_ids[0])
				cant_amt = cant_rec.amount
				val['cant_amt'] = cant_amt
			else:
				pass
			
			# Miscellaneous
			
			misc_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','MISC')])
			if misc_ids:
				misc_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, misc_ids[0])
				misc_amt = misc_rec.amount
				val['misc_amt'] = misc_amt
			else:
				pass
			
			# Professional Tax
			
			ptax_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','PTAX')])
			if ptax_ids:
				ptax_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ptax_ids[0])
				ptax_amt = ptax_rec.amount
				val['ptax_amt'] = ptax_amt
			else:
				pass
							
			# Bank Loan
			
			bank_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','BANK')])
			if bank_ids:
				bank_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, bank_ids[0])
				bank_amt = bank_rec.amount
				val['bank_amt'] = bank_amt
			else:
				pass
				
			# Fine
			
			fine_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','FINE')])
			if fine_ids:
				fine_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, fine_ids[0])
				fine_amt = fine_rec.amount
				val['fine_amt'] = fine_amt
			else:
				pass
				
			# Income Tax
			
			itax_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','ITAX')])
			if itax_ids:
				itax_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, itax_ids[0])
				itax_amt = itax_rec.amount
				val['itax_amt'] = itax_amt
			else:
				pass
				
			# Deposit
			
			dep_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','DEP')])
			if dep_ids:
				dep_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, dep_ids[0])
				dep_amt = dep_rec.amount
				val['dep_amt'] = dep_amt
			else:
				pass
				
			# INTERIM RELIEF
			
			rel_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','REL')])
			if rel_ids:
				rel_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, rel_ids[0])
				rel_amt = rel_rec.amount
				val['rel_amt'] = rel_amt
			else:
				pass
				
			# OCP Wages
			
			ocp_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','OCP')])
			if ocp_ids:
				ocp_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ocp_ids[0])
				ocp_amt = ocp_rec.amount
				val['ocp_amt'] = ocp_amt
			else:
				pass
				
			# Other Earnings
			
			oear_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','OEAR')])
			if oear_ids:
				oear_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, oear_ids[0])
				oear_amt = oear_rec.amount
				val['oear_amt'] = oear_amt
			else:
				pass
				
			# Annul Increment
			
			ainc_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','AINC')])
			if ainc_ids:
				ainc_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ainc_ids[0])
				ainc_amt = ainc_rec.amount
				val['ainc_amt'] = ainc_amt
			else:
				pass
				
			# Travel Allowance
			
			tra_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','TRA')])
			if tra_ids:
				tra_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, tra_ids[0])
				tra_amt = tra_rec.amount
				val['tra_amt'] = tra_amt
			else:
				pass						
		
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
  

report_sxw.report_sxw('report.kg.emp.sal.muster', 'hr.payslip', 
			'addons/kg_payslip/report/kg_emp_sal_muster.rml', 
			parser=kg_emp_sal_muster, header = False)
