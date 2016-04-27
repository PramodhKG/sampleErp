import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_baask_sal_muster(report_sxw.rml_parse):
	
	_name = 'kg.baask.sal.muster'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_baask_sal_muster, self).__init__(cr, uid, name, context=context)
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
				
		if form['pay_sch']:
				where_sql.append("con.sal_date= '%s' "%form['pay_sch'])
		
				
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
			  slip.tot_allowance AS tot_ear,
			  slip.tot_deduction AS tot_ded,
			  slip.round_val AS net_sal,
			  slip.cross_amt AS gross,
			  slip.balance_val as cf_amt,
			  slip.tot_paid_days as tot_day,
			  emp.emp_code as code,
			  emp.name_related as emp_name,
			  emp.last_month_bal as epf_amt,
			  to_char(emp.join_date,'dd/mm/yyyy') AS j_date,
			  con.acc_no AS bank_no,
			  con.pf_acc_no AS pf_no,
			  con.wage as basic,
			  con.allowance as allowa
			  
			  FROM  hr_payslip slip
						
			left JOIN hr_employee emp ON (emp.id=slip.employee_id)
			left JOIN hr_contract con ON (con.id=slip.contract_id)
								  

			  where slip.tot_paid_days > 0 and slip.state=%s and slip.date_from >=%s and slip.date_to <=%s'''+ where_sql + '''
				order by emp.id''',('done', form['date_from'],form['date_to']))
		
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		gran_tot_net = 0.0
		tot_net=0.00
		
		gran_tot_itax = 0.0
		tot_itax=0.00
		
		gran_tot_ptax = 0.0
		tot_ptax=0.00
		
		gran_tot_pf = 0.0
		tot_pf=0.00
		
		gran_tot_esi = 0.0
		tot_esi=0.00
		
		gran_tot_di = 0.0
		tot_di=0.00
		
		gran_tot_lwf = 0.0
		tot_lwf=0.00
		
		gran_tot_cum = 0.0
		tot_cum=0.00
		
		gran_tot_adv = 0.0
		tot_adv=0.00
		
		gran_tot_tre = 0.0
		tot_tre=0.00
		
		gran_tot_mins = 0.0
		tot_mins=0.00
		
		gran_tot_misc = 0.0
		tot_misc=0.00
		
		gran_tot_ains = 0.0
		tot_ains=0.00
		
		gran_tot_cant = 0.0
		tot_cant=0.00
		
		gran_tot_rent = 0.0
		tot_rent=0.00
		
		gran_tot_fine = 0.0
		tot_fine=0.00
		
		gran_tot_basic = 0.0
		tot_basic_amt=0.00
		
		gran_tot_ot = 0.0
		tot_ot_amt=0.00
		
		gran_tot_alw = 0.0
		tot_alw_amt=0.00
		
		gran_tot_oear = 0.0
		tot_oear_amt=0.00
		
		gran_tot_epf = 0.0
		tot_epf_amt=0.00
		
		gran_tot_cf = 0.0
		tot_cf_amt=0.00
		
		gran_tot_bp = 0.0
		tot_bp=0.00
		
		gran_tot_allowa = 0.0
		tot_allowa=0.00
		
		gran_tot_ded = 0.0
		total_deduction=0.00
		
		gran_tot_cross = 0.0
		total_cross_amt=0.0
		
		for val in data:			
			
			if val['tot_day'] > 0:
				
				# Basic

				one_day_basic = val['basic'] / 26.0
				one_day_alw = val['allowa'] / 26.0

				if val['tot_day'] >= 26:
					val['basic_amt'] = val['basic']
				else:
					val['basic_amt'] = one_day_basic * val['tot_day']

				print "val['basic_amt'].......................", val['basic_amt']
					

				"""
				
				basic_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','BASIC')])
				if basic_ids:
					basic_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, basic_ids[0])
					basic_amt = basic_rec.amount
					val['basic_amt'] = basic_amt
				else:
					val['basic_amt'] = 0
					
				print "basic_amt....................", val['basic_amt']

				"""
				
				# Allowance

				if val['tot_day'] >= 26:
					val['alw_amt'] = val['allowa']
				else:
					val['alw_amt'] = one_day_alw * val['tot_day']

				print "val['alw_amt'].......................", val['alw_amt']
				

				"""				
				allowance_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','ALW')])
				if allowance_ids:
					allowance_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, allowance_ids[0])
					alw_amt = allowance_rec.amount
					val['alw_amt'] = alw_amt
				else:
					val['alw_amt'] = 0
				"""
								
				# Over Time

				if val['tot_day'] > 26:
					ot_days = val['tot_day'] - 26
					ot_base = ot_days * one_day_basic
					ot_alw = ot_days * one_day_alw					
					val['ot_amt'] = ot_base + ot_alw
				else:
					val['ot_amt'] = 0
					ot_days = 0

				val['new_ot_days'] = ot_days
				val['new_tot_days'] = val['tot_day'] - ot_days

				print "val['ot_amt'].......................", val['ot_amt']

				

				"""				
				ot_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','OT')])
				
				if ot_ids:
					ot_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ot_ids[0])
					ot_amt = ot_rec.amount
					val['ot_amt'] = ot_amt
				else:
					val['ot_amt'] = 0

				"""
					
				# PF
								
				pf_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','PF')])
				if pf_ids:
					pf_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, pf_ids[0])
					pf_amt = pf_rec.amount
					val['pf_amt'] = pf_amt
				else:
					val['pf_amt'] = 0.00
						
				# ESI
				
				esi_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','ESI')])
				if esi_ids:
					esi_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, esi_ids[0])
					esi_amt = esi_rec.amount
					val['esi_amt'] = esi_amt
				else:
					val['esi_amt'] = 0.00
				
				# Salary Advance
								
				advance_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','SA')])
				if advance_ids:
					advance_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, advance_ids[0])
					adv_amt = allowance_rec.amount
					val['adv_amt'] = adv_amt
				else:
					val['adv_amt'] = 0
								
				# Canteen
				
				cant_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','CANT')])
				if cant_ids:
					cant_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, cant_ids[0])
					cant_amt = cant_rec.amount
					val['cant_amt'] = cant_amt
				else:
					val['cant_amt'] = 0
				
				# Miscellaneous
				
				misc_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','MISC')])
				if misc_ids:
					misc_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, misc_ids[0])
					misc_amt = misc_rec.amount
					val['misc_amt'] = misc_amt
				else:
					val['misc_amt'] = 0
				
				# RENT
				
				rent_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','RENT')])
				if rent_ids:
					rent_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, rent_ids[0])
					rent_amt = rent_rec.amount
					val['rent_amt'] = rent_amt
				else:
					val['rent_amt'] = 0
								
				# Medi Calim Insurance
				
				mins_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','MINS')])
				if mins_ids:
					mins_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, mins_ids[0])
					mins_amt = mins_rec.amount
					val['mins_amt'] = mins_amt
				else:
					val['mins_amt'] = 0
					
				# Fine
				
				fine_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','FINE')])
				if fine_ids:
					fine_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, fine_ids[0])
					fine_amt = fine_rec.amount
					val['fine_amt'] = fine_amt
				else:
					val['fine_amt'] = 0
					
				# Income Tax
				
				itax_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','ITAX')])
				if itax_ids:
					itax_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, itax_ids[0])
					itax_amt = itax_rec.amount
					val['itax_amt'] = itax_amt
				else:
					val['itax_amt'] = 0
					
				# Professional Tax
				
				ptax_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','PTAX')])
				if ptax_ids:
					ptax_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ptax_ids[0])
					ptax_amt = ptax_rec.amount
					val['ptax_amt'] = ptax_amt
				else:
					val['ptax_amt'] = 0
					
				# Treatment
				
				tre_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','TR')])
				if tre_ids:
					tre_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, tre_ids[0])
					tre_amt = tre_rec.amount
					val['tre_amt'] = tre_amt
				else:
					val['tre_amt'] = 0
				

				# Diary
				
				di_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']), 
																	('code','=','DI')])
				if di_ids:
					di_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, di_ids[0])
					di_amt = di_rec.amount
					val['di_amt'] = di_amt
				else:
					val['di_amt'] = 0
					
				# LWF
				
				lwf_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']), 
																	('code','=','LWF')])
				if lwf_ids:
					lwf_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, lwf_ids[0])
					lwf_amt = lwf_rec.amount
					val['lwf_amt'] = lwf_amt
				else:
					val['lwf_amt'] = 0
				
				"""	 
				# OCP Wages
				
				ocp_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','OCP')])
				if ocp_ids:
					ocp_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ocp_ids[0])
					ocp_amt = ocp_rec.amount
					val['ocp_amt'] = ocp_amt
				else:
					pass
				
				"""
					
				# Other Earnings
				
				oear_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','OEAR')])
				if oear_ids:
					oear_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, oear_ids[0])
					oear_amt = oear_rec.amount
					val['oear_amt'] = oear_amt
				else:
					val['oear_amt'] = 0
					
				# Acc. Insurance
				
				ains_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','INS')])
				if ains_ids:
					ains_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ains_ids[0])
					ains_amt = ains_rec.amount
					val['ains_amt'] = ains_amt
				else:
					val['ains_amt'] = 0
					
				# Cumulative Deduction
				
				cum_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
								('code','=','CUMDED')])
				if cum_ids:
					cum_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, cum_ids[0])
					cum_amt = cum_rec.amount
					val['cum_amt'] = cum_amt
				else:
					val['cum_amt'] = 0			
					
				
				tot_itax = val['itax_amt']
				tot_ptax = val['ptax_amt']  
				tot_pf = val['pf_amt']
				tot_esi = val['esi_amt']
				tot_di = val['di_amt']
				tot_lwf = val['lwf_amt']   
				tot_cum = val['cum_amt']
				tot_adv = val['adv_amt'] + val['cum_amt']
				tot_tre = val['tre_amt']	
				tot_mins = val['mins_amt']
				tot_misc = val['misc_amt']
				tot_ains = val['ains_amt']
				tot_cant = val['cant_amt']
				tot_rent = val['rent_amt']
				tot_fine = val['fine_amt']
				tot_basic_amt = val['basic_amt'] 
				tot_ot_amt = val['ot_amt']
				tot_alw_amt = val['alw_amt']
				tot_oear_amt = val['oear_amt']
				tot_epf_amt = val['epf_amt']
				tot_cf_amt = val['cf_amt']
				tot_bp = val['basic']
				tot_allowa = val['allowa']		   
				val['tot_deduc']=val['tot_ded']
				total_deduction=val['tot_deduc']
				val['tot_gross']= val['gross']
				total_cross_amt=val['tot_gross']
				val['tot_net']=val['net_sal']
				tot_net_amt=val['tot_net']
				
				gran_tot_net += tot_net_amt
				gran_tot_itax += (round(tot_itax,0))
				gran_tot_ptax += (round(tot_ptax,0))
				gran_tot_pf += (round(tot_pf,0))
				gran_tot_esi += (round(tot_esi,0))
				gran_tot_di += (round(tot_di,0))
				gran_tot_lwf += (round(tot_lwf,0))
				gran_tot_cum += (round(tot_cum,0))
				gran_tot_adv += (round(tot_adv,0))
				gran_tot_tre += (round(tot_tre,0))
				gran_tot_mins += (round(tot_mins,0))
				gran_tot_misc += (round(tot_misc,0))
				gran_tot_ains += (round(tot_ains,0))
				gran_tot_cant += (round(tot_cant,0))
				gran_tot_rent += (round(tot_rent,0))
				gran_tot_fine += (round(tot_fine,0))
				gran_tot_basic += (round(tot_basic_amt,0))
				gran_tot_ot += (round(tot_ot_amt,0))
				gran_tot_alw += (round(tot_alw_amt,0))
				gran_tot_oear += (round(tot_oear_amt,0))
				gran_tot_epf += tot_epf_amt
				gran_tot_cf += tot_cf_amt
				gran_tot_bp += (round(tot_bp,0))
				gran_tot_allowa += (round(tot_allowa,0))
				gran_tot_ded += total_deduction
				gran_tot_cross += (round(total_cross_amt,0))
				
				
				val['total_net'] = gran_tot_net
				val['total_itax'] = gran_tot_itax
				val['total_ptax'] = gran_tot_ptax
				val['total_pf'] = gran_tot_pf
				val['total_esi'] = gran_tot_esi
				val['total_di'] = gran_tot_di
				val['total_lwf'] = gran_tot_lwf
				val['total_cum'] = gran_tot_cum
				val['total_adv'] = gran_tot_adv
				val['total_tre'] = gran_tot_tre
				val['total_mins'] = gran_tot_mins
				val['total_misc'] = gran_tot_misc
				val['total_ains'] = gran_tot_ains
				val['total_cant'] = gran_tot_cant
				val['total_rent'] = gran_tot_rent
				val['total_fine'] = gran_tot_fine
				val['total_basic'] = gran_tot_basic
				val['total_ot'] = gran_tot_ot
				val['total_alw'] = gran_tot_alw
				val['total_oear'] = gran_tot_oear
				val['total_epf'] = gran_tot_epf
				val['total_cf']=gran_tot_cf
				val['total_bp'] = gran_tot_bp
				val['total_allowa'] = gran_tot_allowa
				val['total_ded'] = gran_tot_ded
				val['total_cross'] = gran_tot_cross
				
				
				print "slip_id..................", val['sl_id']
				print "epf amt...................", val['epf_amt']
				print "cf amt.....................",val['cf_amt']
			else:
				print "Employee Attendance is zero.........."
		
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
  

report_sxw.report_sxw('report.kg.baask.sal.muster', 'hr.payslip', 
			'addons/kg_payslip/report/kg_baask_sal_muster.rml', 
			parser=kg_baask_sal_muster, header = False)
