import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_empsal_muster(report_sxw.rml_parse):
	
	_name = 'kg.empsal.muster'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_empsal_muster, self).__init__(cr, uid, name, context=context)
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
			  emp.emp_code as code,
			  emp.name_related as emp_name,
			  emp.last_month_bal as epf_amt,
			  to_char(emp.join_date,'dd/mm/yyyy') AS j_date,
			  con.acc_no AS bank_no,
			  con.pf_acc_no AS pf_no,
			  con.wage as basic,
			  con.allowance as allowa,
			  att.mon_tot_days AS tot_day
			  
			  FROM  hr_payslip slip
			  			
			left JOIN hr_employee emp ON (emp.id=slip.employee_id)
			left JOIN hr_contract con ON (con.id=slip.contract_id)
			left JOIN kg_monthly_attendance att ON (att.id=slip.att_id)		 			  

			  where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s'''+ where_sql + '''
				order by emp.id''',('done', form['date_from'],form['date_to']))
		
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		gran_tot = 0.0
		
		gran_tot_ded=0.00
		tot_ded_amt=0.00
		
		gran_tot_pf=0.00
		tot_pf_amt=0.00
		
		gran_tot_cf=0.00
		tot_cf_amt=0.00
		
		gran_tot_pt=0.00
		tot_pt_amt=0.00
		
		gran_tot_it=0.00
		tot_it_amt=0.00
		
		gran_tot_epf=0.00
		tot_epf_amt=0.00
		
		gran_tot_esi=0.00
		tot_esi_amt=0.00
		
		gran_tot_di=0.00
		tot_di_amt=0.00
		
		gran_tot_cum=0.00
		tot_cum_amt=0.00
		
		gran_tot_adv=0.00
		tot_adv_amt=0.00
		
		gran_tot_tre=0.00
		tot_tre_amt=0.00
		
		gran_tot_mins=0.00
		tot_mins_amt=0.00
		
		gran_tot_misc=0.00
		tot_misc_amt=0.00
		
		gran_tot_ains=0.00
		tot_ains_amt=0.00
		
		gran_tot_cant=0.00
		tot_cant_amt=0.00
		
		gran_tot_rent=0.00
		tot_rent_amt=0.00
		
		gran_tot_fine=0.00
		tot_fine_amt=0.00
		
		gran_tot_cross=0.00
		tot_basic_amt=0.00
		tot_ot_amt=0.00
		tot_alw_amt=0.00
		tot_oear_amt=0.00
		tot_epf_amt=0.00
		
		gran_tot_bp=0.00
		tot_bp_amt=0.00
		
		gran_tot_al=0.00
		tot_al_amt=0.00
		
		gran_tot_oear=0.00
		tot_oe_amt=0.00
		
		gran_tot_bas=0.00
		tot_bas_amt=0.00
		
		gran_tot_allowa=0.00
		tot_allowa_amt=0.00
		
		tot_net_amt=0.00
		
		
		
		
		for val in data:			
			
			# Grand total for total basic
			tot_bas_amt = val['basic']
			print "tot_bas_amt................",tot_bas_amt
			gran_tot_bas += tot_bas_amt
			val['total_bas'] = gran_tot_bas
			
			# Grand total for allowa
			tot_allowa_amt = val['allowa']
			print "tot_allowa_amt................",tot_allowa_amt
			gran_tot_allowa += tot_allowa_amt
			val['total_allowa'] = gran_tot_allowa
			
		
			
			# Grand total for pf deduction
			epf_amt = val['epf_amt'] or 0
			tot_epf_amt = epf_amt
			print "tot_epf_amt................",tot_epf_amt
			gran_tot_epf += tot_epf_amt
			val['total_epf'] = gran_tot_epf
			
			# Grand total for cf deduction
			tot_cf_amt = val['cf_amt']
			if not tot_cf_amt:
				tot_cf_amt = 0
			else:
				tot_cf_amt = tot_cf_amt
			print "tot_cf_amt................",tot_cf_amt
			gran_tot_cf += tot_cf_amt
			val['total_cf'] = gran_tot_cf
			
			print "slip_id..................", val['sl_id']
			# Basic
			
			basic_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','BASIC')])
			if basic_ids:
				basic_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, basic_ids[0])
				basic_amt = basic_rec.amount
				val['basic_amt'] = basic_amt
			else:
				val['basic_amt'] = 0			
			
			
			
			# Allowance
							
			allowance_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','ALW')])
			if allowance_ids:
				allowance_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, allowance_ids[0])
				alw_amt = allowance_rec.amount
				val['alw_amt'] = alw_amt
			else:
				val['alw_amt'] = 0
				
			# Grand total for allowancesss
			tot_al_amt = val['alw_amt']
			print "tot_al_amt................",tot_al_amt
			gran_tot_al += tot_al_amt
			val['total_al'] = gran_tot_al
							
			# Over Time
							
			ot_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','OT')])
			
			if ot_ids:
				ot_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ot_ids[0])
				ot_amt = ot_rec.amount
				val['ot_amt'] = ot_amt
			else:
				val['ot_amt'] = 0
				
				
			# Grand total for basic amount
			tot_bp_amt = val['basic_amt'] + val['ot_amt']
			print "tot_bp_amt................",tot_bp_amt
			gran_tot_bp += tot_bp_amt
			val['total_bp'] = gran_tot_bp
			print "total_bp......",val['total_bp']
				
			# PF
							
			pf_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','PF')])
			if pf_ids:
				pf_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, pf_ids[0])
				pf_amt = pf_rec.amount
				val['pf_amt'] = pf_amt
			else:
				val['pf_amt'] = 0.00
				
			# Grand total for pf
			tot_pf_amt = val['pf_amt']
			print "tot_pf_amt................",tot_pf_amt
			gran_tot_pf += tot_pf_amt
			val['total_pf'] = gran_tot_pf
					
			# ESI
			
			esi_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','ESI')])
			if esi_ids:
				esi_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, esi_ids[0])
				esi_amt = esi_rec.amount
				val['esi_amt'] = esi_amt
			else:
				val['esi_amt'] = 0.00
				
			# Grand total for esi
			tot_esi_amt = val['esi_amt']
			print "tot_esi_amt................",tot_esi_amt
			gran_tot_esi += tot_esi_amt
			val['total_esi'] = gran_tot_esi
			
			# Salary Advance
							
			advance_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','SA')])
			if advance_ids:
				advance_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, advance_ids[0])
				adv_amt = allowance_rec.amount
				val['adv_amt'] = adv_amt
			else:
				val['adv_amt'] = 0
			
			# Grand total for advance_amt
			tot_adv_amt = val['adv_amt']
			print "tot_adv_amt................",tot_adv_amt
			gran_tot_adv += tot_adv_amt
			val['total_adv'] = gran_tot_adv
				
							
			# Canteen
			
			cant_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','CANT')])
			if cant_ids:
				cant_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, cant_ids[0])
				cant_amt = cant_rec.amount
				val['cant_amt'] = cant_amt
			else:
				val['cant_amt'] = 0
				
			# Grand total for canteen_amt
			tot_cant_amt = val['cant_amt']
			print "tot_cant_amt................",tot_cant_amt
			gran_tot_cant += tot_cant_amt
			val['total_cant'] = gran_tot_cant
			
			# Miscellaneous
			
			misc_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','MISC')])
			if misc_ids:
				misc_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, misc_ids[0])
				misc_amt = misc_rec.amount
				val['misc_amt'] = misc_amt
			else:
				val['misc_amt'] = 0
				
			# Grand total for mics_amt
			tot_misc_amt = val['misc_amt']
			print "tot_misc_amt................",tot_misc_amt
			gran_tot_misc += tot_misc_amt
			val['total_misc'] = gran_tot_misc
			
			# RENT
			
			rent_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','RENT')])
			if rent_ids:
				rent_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, rent_ids[0])
				rent_amt = rent_rec.amount
				val['rent_amt'] = rent_amt
			else:
				val['rent_amt'] = 0
				
			# Grand total for rent_amt
			tot_rent_amt = val['rent_amt']
			print "tot_rent_amt................",tot_rent_amt
			gran_tot_rent += tot_rent_amt
			val['total_rent'] = gran_tot_rent
							
			# Medi Calim Insurance
			
			mins_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','MINS')])
			if mins_ids:
				mins_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, mins_ids[0])
				mins_amt = mins_rec.amount
				val['mins_amt'] = mins_amt
			else:
				val['mins_amt'] = 0
				
			# Grand total for mins_amt
			tot_mins_amt = val['mins_amt']
			print "tot_mins_amt................",tot_mins_amt
			gran_tot_mins += tot_mins_amt
			val['total_mins'] = gran_tot_mins
				
			# Fine
			
			fine_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','FINE')])
			if fine_ids:
				fine_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, fine_ids[0])
				fine_amt = fine_rec.amount
				val['fine_amt'] = fine_amt
			else:
				val['fine_amt'] = 0
				
			# Grand total for fine_amt
			tot_fine_amt = val['fine_amt']
			print "tot_fine_amt................",tot_fine_amt
			gran_tot_fine += tot_fine_amt
			val['total_fine'] = gran_tot_fine	
			# Income Tax
			
			itax_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','ITAX')])
			if itax_ids:
				itax_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, itax_ids[0])
				itax_amt = itax_rec.amount
				val['itax_amt'] = itax_amt
			else:
				val['itax_amt'] = 0
				
			# Grand total for Income tax
			tot_it_amt = val['itax_amt']
			print "tot_it_amt................",tot_it_amt
			gran_tot_it += tot_it_amt
			val['total_it'] = gran_tot_it
				
			# Professional Tax
			
			ptax_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','PTAX')])
			if ptax_ids:
				ptax_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ptax_ids[0])
				ptax_amt = ptax_rec.amount
				val['ptax_amt'] = ptax_amt
			else:
				val['ptax_amt'] = 0
				
			# Grand total for professional tax
			tot_pt_amt = val['ptax_amt']
			print "tot_pt_amt................",tot_pt_amt
			gran_tot_pt += tot_pt_amt
			val['total_pt'] = gran_tot_pt
				
			# Treatment
			
			tre_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','TR')])
			if tre_ids:
				tre_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, tre_ids[0])
				tre_amt = tre_rec.amount
				val['tre_amt'] = tre_amt
			else:
				val['tre_amt'] = 0
			
			# Grand total for advance_amt
			tot_tre_amt = val['tre_amt']
			print "tot_tre_amt................",tot_tre_amt
			gran_tot_tre += tot_tre_amt
			val['total_tre'] = gran_tot_tre
			

			# Diary
			
			di_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']), 
																('code','=','DI')])
			if di_ids:
				di_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, di_ids[0])
				di_amt = di_rec.amount
				val['di_amt'] = di_amt
			else:
				val['di_amt'] = 0
			
			# Grand total for diary
			tot_di_amt = val['di_amt']
			print "tot_di_amt................",tot_di_amt
			gran_tot_di += tot_di_amt
			val['total_di'] = gran_tot_di
				
			
			
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
				
			# Grand total for other earnings
			tot_oe_amt = val['oear_amt']
			print "tot_oe_amt................",tot_oe_amt
			gran_tot_oear += tot_oe_amt
			val['total_oear'] = gran_tot_oear
				
			# Acc. Insurance
			
			ains_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','INS')])
			if ains_ids:
				ains_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, ains_ids[0])
				ains_amt = ains_rec.amount
				val['ains_amt'] = ains_amt
			else:
				val['ains_amt'] = 0
			
			# Grand total for ains_amt
			tot_ains_amt = val['ains_amt']
			print "tot_ains_amt................",tot_ains_amt
			gran_tot_ains += tot_ains_amt
			val['total_ains'] = gran_tot_ains
				
			# Cumulative Deduction
			
			cum_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',val['sl_id']),
							('code','=','CUMDED')])
			if cum_ids:
				cum_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, cum_ids[0])
				cum_amt = cum_rec.amount
				val['cum_amt'] = cum_amt
			else:
				val['cum_amt'] = 0
				
			# Grand total for cum_ded
			tot_cum_amt = val['cum_amt']
			print "tot_cum_amt................",tot_cum_amt
			gran_tot_cum += tot_cum_amt
			val['total_cum'] = gran_tot_cum	
			
			
			# Grand total for cross amount
			val['tot_gross']=val['basic_amt'] + val['ot_amt'] + val['alw_amt'] + val['oear_amt'] + epf_amt
			tot_cross = val['tot_gross']
			gran_tot_cross += tot_cross
			val['total_cross']=gran_tot_cross
			
			# Grand total for total deduction
			val['tot_deduc']= val['cant_amt'] + val['rent_amt'] + val['fine_amt'] + val['mins_amt'] + val['misc_amt'] + val['ains_amt'] +val['cum_amt'] + val['adv_amt'] + val['tre_amt'] + val['pf_amt'] + val['esi_amt'] + val['di_amt'] + val['ptax_amt'] + val['itax_amt'] 	 
			tot_ded_amt = val['tot_deduc']
			print "tot_ded_amt................",tot_ded_amt
			gran_tot_ded += tot_ded_amt
			val['total_ded'] = gran_tot_ded
			
			# total net calculation
			val['tot_net']=val['tot_gross']-val['tot_deduc']
			tot_net_amt=val['tot_net']
			gran_tot += tot_net_amt
			val['total_net'] = gran_tot
			
								
		
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
			
report_sxw.report_sxw('report.kg.empsal.muster', 'hr.payslip', 
			'addons/kg_clin_reports/reports/kg_empsal_muster.rml', 
			parser=kg_empsal_muster, header = False)
