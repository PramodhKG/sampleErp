## HRM with Payroll System for Dr.GB Health care  ##

import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import datetime as lastdate
import calendar

class kg_payslip(osv.osv):
	
	_name = 'hr.payslip'	
	_inherit = 'hr.payslip'
	_order = "date desc"	
	
	_columns = {
	
	'worked_days_line_ids': fields.one2many('hr.payslip.worked_days', 'payslip_id', 'Payslip Worked Days',
			readonly=True, states={'draft': [('readonly', False)]}),
	'tot_sal': fields.float('Total Salary',readonly=True),
	'round_val': fields.float('Net Salary', readonly=True),
	'balance_val': fields.float('Balance Salary', readonly=True),
	'cross_amt': fields.float('Net Gross Amount',readonly=True),
	'con_cross_amt': fields.float('Gross Amount',readonly=True),
	'date_from': fields.date('Date From', readonly=False, required=True),
	'date_to': fields.date('Date To', readonly=False, required=True),
	'emp_name': fields.char('Employee Code', size=128, readonly=True),
	'tot_paid_days': fields.float('Total Paid Days'),
	'tot_allowance': fields.float('Total Allowance',readonly=True),
	'tot_deduction': fields.float('Total Deduction',readonly=True),
	'tot_contribution': fields.float('Total Contribution',readonly=True),
	
	'att_id': fields.many2one('kg.monthly.attendance','Attendance Ref'),
	'dep_id': fields.many2one('hr.department','Department Name'),
	'cum_ded_id': fields.many2one('kg.advance.deduction','Cumulative Deduction', readonly=True),
	'date': fields.date('Creation Date'),
	'month':fields.char('Month')
	
	}
	
	
			
	def _get_last_month_name(self, cr, uid, context=None):
		today = lastdate.date.today()
		first = lastdate.date(day=1, month=today.month, year=today.year)
		last = first - lastdate.timedelta(days=1)
		res = last.strftime('%B-%Y')
		return res
	
	def _get_last_month_first(self, cr, uid, context=None):
		
		today = lastdate.date.today()
		print "today-----------", today
		first = lastdate.date(day=1, month=today.month, year=today.year)
		mon = today.month - 1
		if mon == 0:
			mon = 12
		else:
			mon = mon
		tot_days = calendar.monthrange(today.year,mon)[1]
		test = first - lastdate.timedelta(days=tot_days)
		res = test.strftime('%Y-%m-%d')
		print "---------------",res
		return res
		
	def _get_last_month_end(self, cr, uid, context=None):
		today = lastdate.date.today()
		first = lastdate.date(day=1, month=today.month, year=today.year)
		last = first - lastdate.timedelta(days=1)
		res = last.strftime('%Y-%m-%d')
		return res
	
	_defaults = {
		
		'month':_get_last_month_name,
		'date_from': _get_last_month_first,
		'date_to': _get_last_month_end,
		'date': lambda *a: time.strftime('%Y-%m-%d'),
		
		}	
	
		
	def get_contract(self, cr, uid, employee, date_from, date_to, context=None):
		"""
		@param employee: browse record of employee
		@param date_from: date field
		@param date_to: date field
		@return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
		"""
		contract_obj = self.pool.get('hr.contract')
		clause = []	
		clause_final =  [('employee_id', '=', employee.id)] 
		contract_ids = contract_obj.search(cr, uid, clause_final, context=context)
		return contract_ids
	
	def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
		empolyee_obj = self.pool.get('hr.employee')
		contract_obj = self.pool.get('hr.contract')
		worked_days_obj = self.pool.get('hr.payslip.worked_days')
		input_obj = self.pool.get('hr.payslip.input')
		
		if context is None:
			context = {}
		#delete old worked days lines
		old_worked_days_ids = ids and worked_days_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
		if old_worked_days_ids:
			worked_days_obj.unlink(cr, uid, old_worked_days_ids, context=context)

		#delete old input lines
		old_input_ids = ids and input_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
		if old_input_ids:
			input_obj.unlink(cr, uid, old_input_ids, context=context)


		#defaults
		res = {'value':{
					  'line_ids':[],
					  'input_line_ids': [],
					  'worked_days_line_ids': [],
					  #'details_by_salary_head':[], TODO put me back
					  'name':'',
					  'contract_id': False,
					  'struct_id': False,
					  }
			}
		if (not employee_id) or (not date_from) or (not date_to):
			return res
		ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
		print "...........ttyme..............",ttyme
		employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
		res['value'].update({
					'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
					'company_id': employee_id.company_id.id,
		})

		if not context.get('contract', False):
			#fill with the first contract of the employee
			contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)
		else:
			if contract_id:
				#set the list of contract for which the input have to be filled
				contract_ids = [contract_id]
			else:
				#if we don't give the contract, then the input to fill should be for all current contracts of the employee
				contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)

		if not contract_ids:
			return res
		contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
		res['value'].update({
					'contract_id': contract_record and contract_record.id or False
		})
		struct_record = contract_record and contract_record.struct_id or False
		if not struct_record:
			return res
		res['value'].update({
					'struct_id': struct_record.id,
		})
		#computation of the salary input
		worked_days_line_ids = self.get_worked_day_lines(cr, uid, ids,contract_ids, date_from, date_to, context=context)
		input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
		res['value'].update({
					'worked_days_line_ids': worked_days_line_ids,
					'input_line_idsslip_date': input_line_ids,
		})
		return res
		
	def get_worked_day_lines(self, cr, uid,ids,contract_ids, date_from, date_to, context=None):
		
		def was_on_leave(employee_id, datetime_day, context=None):
			res = False
			day = datetime_day.strftime("%Y-%m-%d")
			holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
			if holiday_ids:
				res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
			return res
		res = []
		for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
			if not contract.working_hours:
				emp_id = contract.employee_id.id
				start_date = "'"+date_from+"'"
				end_date = 	"'"+date_to+"'"
				month_att_obj = self.pool.get('kg.monthly.attendance')				
				sql = """ select mon_tot_days,worked from kg_monthly_attendance where employee_id=%s and start_date=%s and end_date=%s""" %(emp_id,start_date,end_date)
				cr.execute(sql)
				data = cr.dictfetchall()
				print "data...................", data
				val , val1 = 0, 0
				if data:					
					val = [d['mon_tot_days'] for d in data if 'mon_tot_days' in d]
					val = val[0]
					val1 = [d['worked'] for d in data if 'worked' in d]
					val1 = val1[0]
				else:
					pass
					#raise osv.except_osv(
						#_('Error !!'),
						#_('Attendance entry not availabe for employee -  %s !!'%(contract.employee_id.name)))					
				ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
				name = tools.ustr(ttyme.strftime('%B-%Y'))
				print "name.......////.........",name
				worked_day_obj = self.pool.get('hr.payslip.worked_days')					
				attendances = {
					 'name': name,
					 'sequence': 1,
					 'code': 'WORK100',
					 'number_of_days': val,
					 'number_of_hours': val,
					 'contract_id': contract.id,
				}				
				res += [attendances] 
			return res	
		
	def salary_slip_calculation(self, cr, uid, ids, context=None):
		
		""" This function have full functionality of payroll process
		based on earnings and deductions, PF, Income Tax and other calculations """
		
		all_ded_obj = self.pool.get('kg.allowance.deduction')
		all_ded_line_obj = self.pool.get('kg.allowance.deduction.line')
		sal_catg = self.pool.get('hr.salary.rule.category')
		line_obj = self.pool.get('hr.payslip.line')
		con_obj = self.pool.get('hr.contract')
		rule_obj = self.pool.get('hr.salary.rule')
		cum_obj = self.pool.get('kg.advance.deduction')
		mobile_ded_obj = self.pool.get('kg.mobile.bills')
		emp = self.pool.get('hr.employee')
		sal_det = self.pool.get('kg.salary.detail')
		empolyer_cont = self.pool.get('kg.emp.contribution')
		empolyer_cont_line = self.pool.get('kg.emp.contribution.line')
		employee_cont = self.pool.get('kg.employee.contribution')
		employee_cont_line = self.pool.get('kg.employee.contribution.line')
		pt_obj = self.pool.get('kg.pt.master')
		pt_line_obj = self.pool.get('kg.pt.master.line')
		
		# The Below type Allowance & Deduction should be created before salary slip run #
		
		basic_rule_id = rule_obj.search(cr, uid, [('code','=','BASIC')])
		allo_rule_id = rule_obj.search(cr, uid, [('code','=','HRA')])
		spal_rule_id = rule_obj.search(cr, uid, [('code','=','SPA')])
		ot_rule_id = rule_obj.search(cr, uid, [('code','=','OT')])
		pf_rule_id = rule_obj.search(cr, uid, [('code','=','PF')])
		esi_rule_id = rule_obj.search(cr, uid, [('code','=','ESI')])
		cum_rule_id = rule_obj.search(cr, uid, [('code','=','ADVDED')])
		mob_rule_id = rule_obj.search(cr, uid, [('code','=','MD')])
		itax_rule_id = rule_obj.search(cr, uid, [('code','=', 'ITAX')])
		epf_rule_id = rule_obj.search(cr, uid, [('code','=', 'EMP_PF')])
		emp_esi_rule_id = rule_obj.search(cr, uid, [('code','=', 'EMP_ESI')])
		pt_rule_id = rule_obj.search(cr, uid, [('code','=', 'PT')])
		pf_amt = 0
		print "cum_rule_id .........  ",cum_rule_id
		for slip_rec in self.browse(cr, uid, ids, context=context):
			print "slip_rec-------------...", slip_rec
			emp_rec = slip_rec.employee_id
			print "emp_rec********#########&&&&&&&",emp_rec
			dep_id = emp_rec.department_id.id
			emp_nam = emp_rec.emp_code
			emp_bal_amt = emp_rec.round_off
			print "Previous balanace......emp_bal_amt...............",emp_bal_amt
			print "emp_rec----------------------", emp_rec
			emp_id = slip_rec.employee_id.id
			start_date = "'"+slip_rec.date_from+"'"
			end_date = 	"'"+slip_rec.date_to+"'"
			
			# Employee Attendance details calculation
						
			sql = """ select worked,mon_tot_days,id,absent,working_days,ot from kg_monthly_attendance where employee_id=%s and start_date=%s
									and end_date=%s and state='confirm' """ %(emp_id,start_date,end_date,)
			cr.execute(sql)
			data = cr.dictfetchall()
			print "data---------------------------------",data
			worked, mon_tot_days,ot_days = 0,0,0
			att_id = False
			if data:					
				
				val1 = [d['worked'] for d in data if 'worked' in d]
				worked = val1[0]
				
				val3 = [d['working_days'] for d in data if 'working_days' in d]
				working_days= val3[0]
								
				val7 = [d['mon_tot_days'] for d in data if 'mon_tot_days' in d]
				mon_tot_days = val7[0]	
				tot_days = mon_tot_days
				print "tot_days--------------->>>>", tot_days
				
				val4 = [d['ot'] for d in data if 'ot' in d]
				ot_days = val4[0]
				print "ot_days.............................",ot_days
				
				val2 = [d['absent'] for d in data if 'absent' in d]
				absent = val2[0]
												
			else:
				print "No attendance entry available"
				raise osv.except_osv(
						_('Error !!'),
						_('Attendance entry not availabe for employee -  %s !!'%(slip_rec.employee_id.name)))
				
			con_id = con_obj.search(cr, uid, [('employee_id', '=', emp_id)])			
			con_rec= con_obj.browse(cr, uid,con_id)	
			if not con_id:
				raise osv.except_osv(
						_('Error :: No Contract Details !!'),
						_('Contract entry not availabe for employee -  %s !!'%(slip_rec.employee_id.name)))
			else:
				con_rec= con_obj.browse(cr, uid,con_id)				
				con_rec = con_rec[0]
				ctc_ids = sal_det.search(cr,uid,[('salary_id','=',con_id)])
				print "ctc_ids....................", ctc_ids
			tot_ctc = 0
			esi_amt = 0
			pf_basic = 0
			gross_amt = 0
			deduc_amt = 0
			net_amt = 0
			allowance_amt = 0
			allo_bas = 0
			tot_pf_amt = 0
			tot_esi_amt = 0
			tot_gross_amt = 0
			print "slip_Rec",slip_rec
			payslip_det = self.browse(cr,uid,slip_rec.id)
			for item in ctc_ids:
				sal_rec = sal_det.browse(cr,uid,item)
				print "sal_rec.salary_type.code..................",sal_rec.salary_type.code
				print "employee------------------------------cont----",sal_rec.salary_type.code
				con_pf_status = con_rec.pf_status
				con_esi_status = con_rec.esi
				con_gross_salary = con_rec.gross_salary
				pay_curt_date = payslip_det.date_from
				pf_date = con_rec.pf_eff_date
				esi_date = con_rec.esi_eff_date
				tot_ctc += sal_rec.salary_amount
				one_sal = 0.00
				
				#Calculating Gross Amount
				
				#working_days and absent days has been changed for cf_trail purpose
				
				print "working_days",working_days
				print "mon_tot_days",worked
				ded_gross_amt = con_rec.gross_salary /working_days
				
				print "ded_gross_amt.................",ded_gross_amt
				one_gross_amt = con_rec.gross_salary
				
				print "one_gross_amt....................",one_gross_amt
				
				#Contract Salary Details --> Fixed Amount or Percentage Calculation
				if sal_rec.type == 'fixed_amt':
					one_gross_amt = (sal_rec.salary_amount /working_days)
					print "ded_gross_amt.................",one_gross_amt
				else:
					print "before calculate................",one_gross_amt
					print "sal_rec.salary_amount...........",sal_rec.salary_amount
					one_gross_amt = (((one_gross_amt * sal_rec.salary_amount)/100)/working_days)
					print "after_gross_amt.................",one_gross_amt
				
				if worked > 0:
					esi_gross_amt = one_gross_amt/worked
				else:
					esi_gross_amt = 0
				
				
				#All Salaries that are given in contract 
								
				if worked > working_days:
					mon_sal = (one_gross_amt*working_days)	
				else:
					mon_sal = (one_gross_amt*tot_days)	
				basic_vals = {
					'slip_id': slip_rec.id,
					'code': sal_rec.salary_type.code,
					'category_id': sal_rec.salary_type.category_id,
					'contract_id':con_rec.id,
					'employee_id': emp_id,
					'salary_rule_id':sal_rec.salary_type.id,
					'name': sal_rec.salary_type.name,
					'amount': mon_sal,
					#'amount': mon_sal,
					}
				basic_entry = self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,basic_vals)]})
				print ".........................................pf_amt.......................",pf_amt
				
				#To Calculate Total Allowance
				if sal_rec.salary_type.category_id == 'BASIC':
					allo_bas = basic_vals['amount']
				
				if sal_rec.salary_type.category_id == 'ALW' or sal_rec.salary_type.category_id == 'BASIC':
					gross_amt += basic_vals['amount']
				print "gross_amt............................................................",gross_amt
				
				
			# PF Employee Basic
				if con_pf_status and (pay_curt_date > pf_date):
					if sal_rec.salary_type.code == "BASIC" or sal_rec.salary_type.code == "DA":
						empr_pf_ids = employee_cont.search(cr , uid ,[('active','=',True),('state','=','validate')])
						print "empr_pf_ids.......................",empr_pf_ids
						if empr_pf_ids !=[]:
							empr_pf_line_ids = employee_cont_line.search(cr , uid ,
										[('cont_line_entry','=',empr_pf_ids)])
							for i in empr_pf_line_ids:
								employee_pf_cont = employee_cont_line.browse(cr,uid,i)
								if employee_pf_cont.emp_contribution == 'pf':
									if employee_pf_cont.cont_type == 'percent':
										basic_amt = (sal_rec.salary_amount * con_gross_salary)/100
										pf_amt = (basic_amt * employee_pf_cont.contribution_percentage) / 100
										print "pf ------------- amt---------------....", pf_amt
									else:
										pf_amt = sal_rec.salary_amount - employee_pf_cont.contribution_percentage
					if sal_rec.salary_type.code == "BASIC" or sal_rec.salary_type.code == "DA":
						
						tot_pf_amt += pf_amt
					else:
						print "not basic or da"
				
			
			# ESI Employee Basic
				employee_esi_cont = employee_cont.search(cr,uid,[('active','=',True),('state','=','validate')])
				print "esi_id...........................",employee_esi_cont
				
				if 	sal_rec.salary_type.code == "BASIC":
					esi_basic_amt = (sal_rec.salary_amount * con_gross_salary)/100
				
				if con_esi_status and (pay_curt_date > esi_date):
					empr_esi_ids = employee_cont.search(cr,uid,[('active','=',True),('state','=','validate')])
					empr_esi_rec = employee_cont.browse(cr,uid,empr_esi_ids[0])
					if empr_esi_ids:
						empr_esi_line_ids = employee_cont_line.search(cr , uid ,
									[('cont_line_entry','=',empr_esi_ids[0])])
						for j in empr_esi_line_ids:
							employee_esi_cont = employee_cont_line.browse(cr,uid,j)
							if employee_esi_cont.emp_contribution == 'esi':
								if esi_basic_amt >= empr_esi_rec.esi_slab:
									if employee_esi_cont.cont_type == 'percent':
										print ".........esi......gross.......amount",gross_amt
										esi_amt = (gross_amt * employee_esi_cont.contribution_percentage)/100
										print "esi_amt..........................",esi_amt
									else:
										esi_amt = gross_amt - employee_esi_cont.contribution_percentage 
										print "esi_amt..........................",esi_amt
					tot_esi_amt += esi_amt
			#Writing PF Amount
			
			if con_pf_status  and (pay_curt_date > pf_date):
				pf_basic_vals = {
							'slip_id': slip_rec.id,
							'code': 'PF',
							'category_id':'DED',
							'contract_id':con_rec.id,
							'employee_id': emp_id,
							'salary_rule_id':sal_rec.salary_type.id,
							'name': 'Employee - PF ',
							'amount': (round(tot_pf_amt,0)),
							#'amount': tot_pf_amt,
						}
				
				deduc_amt += pf_basic_vals['amount']
				pf_basic_entry = self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,pf_basic_vals)]})	
			else:
				print "No PF is available for this employee"
				
				
			#Writing ESI Amount
			if con_esi_status and (pay_curt_date > esi_date):
				esi_basic_vals = {
							'slip_id': slip_rec.id,
							'code': 'ESI',
							'category_id':'DED',
							'contract_id':con_rec.id,
							'employee_id': emp_id,
							'salary_rule_id':sal_rec.salary_type.id,
							'name': 'Employee - ESI ',
							#'amount': (math.floor(esi_amt)),
							'amount': (round(esi_amt,0)),
						}
					
				deduc_amt += esi_basic_vals['amount']
				esi_basic_entry = self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,esi_basic_vals)]})
			else:
				print "No ESI is available for this employee"
			
			#Calculating ot wages
			
			ot_gross_amt = con_rec.gross_salary /working_days
			if ot_days > 0.00:
				ot_sal = ot_gross_amt * ot_days
				ot_basic_vals = {
					'slip_id': slip_rec.id,
					'code': 'OT',
					'category_id': 'ALW',
					'contract_id':con_rec.id,
					'employee_id': emp_id,
					'salary_rule_id':sal_rec.salary_type.id,
					'name': 'Over Time',
					'amount': ot_sal,
				}					
				ot_basic_entry = self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,ot_basic_vals)]})
				
				
				#total gross salary with ot salary
				gross_amt = ot_basic_vals['amount'] + gross_amt
			
				
				
			#To Calculate Total Deduction
							
			if sal_rec.salary_type.category_id == 'DED':
				deduc_amt += basic_vals['amount']
			
			
			#PT Caluclation for the month feb and august
			
			if payslip_det.month == 'February-2015' or payslip_det.month == 'August-2015':
				six_gross_salary = con_gross_salary * 6
				pt_amt = 0.00
				pt_ids = pt_obj.search(cr,uid,[('active','=',True)])
				print "pt_ids",pt_ids
				if pt_ids:
					pt_line_ids = pt_line_obj.search(cr,uid,[('pt_line','=',pt_ids[0])])
					print "pt_line_ids",pt_line_ids
					for line in pt_line_ids:
						pt_line_rec = pt_line_obj.browse(cr,uid,line)
						print "six_gross_salary",six_gross_salary
						print "min_value,max_values",pt_line_rec.min_value,pt_line_rec.max_value
						if (six_gross_salary < pt_line_rec.min_value):
							pt_amt = 0.00
						if (six_gross_salary >= pt_line_rec.min_value) and (six_gross_salary <= pt_line_rec.max_value ):
							pt_amt = pt_line_rec.pt_value
							print "1st if",pt_amt
					print "pt_amt  ....",pt_amt
					pt_vals = {
				
						'slip_id': slip_rec.id,
						'code': 'PT',
						'category_id': 'DED',
						'contract_id':con_rec.id,
						'employee_id': emp_id,
						'salary_rule_id':pt_rule_id[0],
						'name': 'Professional Tax',
						'amount': pt_amt,
								
							}
					
			else:
				raise openerp.exceptions.Warning(_('Values For the Professional Tax Master is Empty!!.Please Enter The Values !!!'))

			if pt_amt > 0.00:
				print "---------------------pt_vals---------------------------",pt_vals
				self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,pt_vals)]})
				deduc_amt += pt_vals['amount']
			else:
				print "No PT for this employee"
			
			
			
			#Cumulative Deduction Entry
			
			ele=False
			due_amt = 0.00
			cum_ids = cum_obj.search(cr, uid, [('employee_id','=',emp_id),
								('state','=','approve'),('allow','=',True)])
			print "cum_ids...........................", cum_ids
			
			if cum_ids:
				for ele in cum_ids:
					cum_rec = cum_obj.browse(cr, uid, ele)
					print "cum_rec.......................",cum_rec
					print "cum_rec.amt_paid......................",cum_rec.amt_paid
					print "cum_rec.tot_amt......................",cum_rec.tot_amt
					if cum_rec.amt_paid <= cum_rec.tot_amt:
						due_amt = cum_rec.pay_amt + cum_rec.round_bal
						print "due_amt...................",due_amt
						print "cum_rec.pay_amt...................",cum_rec.pay_amt
						print "cum_rec.round_bal...................",cum_rec.round_bal
						name = cum_rec.ded_type
						print "name...................",name
						cum_ded_vals = {
						
						'slip_id': slip_rec.id,
						'code': 'ADVDED',
						'category_id': 'DED',
						'contract_id':con_rec.id,
						'employee_id': emp_id,
						'salary_rule_id':cum_rule_id[0],
						'name': 'Advance Deduction - ' + name,
						'amount': due_amt,
								
							}					
						self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,cum_ded_vals)]})
						print "due_amt.....................",due_amt
						tot_paid = cum_rec.amt_paid
						print "tot_paid..................",tot_paid
						cum_det_ids = self.pool.get('hr.payslip').search(cr, uid, [('employee_id','=', payslip_det.employee_id.id),
											('date_from','=',payslip_det.date_from),('date_to','=',payslip_det.date_to),
											('state','=', 'done')])
						print "cum_det_ids......................................",cum_det_ids
						
						if cum_det_ids == []:
							tot_paid += due_amt
							bal_amt = cum_rec.tot_amt - tot_paid
						else:
							bal_amt = cum_rec.tot_amt - tot_paid
							pass
						print "tot_paid..................",tot_paid
						print "bal_amt................",bal_amt
						if bal_amt == 0:
							cum_rec.write({'state': 'expire', 'round_bal': 0.00})
						else:
							pass
						print "tot_paid...........,,,,,,,,,,,,............",tot_paid	
						#Total Deduction Calculation 
						deduc_amt += due_amt				
						cum_rec.write({'amt_paid': tot_paid, 'bal_amt': bal_amt, 'round_bal': 0.00})
						

					else:
						pass
						
			else:
				print "No Cumulative deduction for this employee"
			
			#Individual Employee Mobile deduction
			
			
			mob_bills_ids = mobile_ded_obj.search(cr, uid, [('employee_name','=',emp_id),('bill_date','>=',payslip_det.date_from),
									('bill_date','<=',payslip_det.date_to),('state','=','confirm'),])
			print "mobile_ids...........................", mob_bills_ids
			mob_all = con_rec.tel_allow
			if mob_bills_ids:
				for ids in mob_bills_ids:
					mobile_rec = mobile_ded_obj.browse(cr, uid, ids)
					mob_bill_amt = mobile_rec.balance_amt
					print "mob_bill_amt",mob_bill_amt
					if mob_bill_amt < 0.00:
						print "mob_bill_anrr",-(mob_bill_amt)
						mob_ded_vals = {
						
						'slip_id': slip_rec.id,
						'code': 'MD',
						'category_id': 'DED',
						'contract_id':con_rec.id,
						'employee_id': emp_id,
						'salary_rule_id':mob_rule_id[0],
						'name': 'Mobile Deduction',
						'amount': -(mob_bill_amt),
								
						}
						print "---------------------vals---------------------------",mob_ded_vals
						if mob_bill_amt < 0.00:
							self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,mob_ded_vals)]})
							mobile_rec.write({'payslip': True})
							deduc_amt += mob_ded_vals['amount']	
							
							
						else:
							print "no mobile deduction for this employee"
						
			else:
				print "No mobile deduction for this employee"
			
			
			
			
			
			# Calculate Total Other Allowance entry of this month
			
			alw_ids = all_ded_obj.search(cr, uid,[('start_date','=',payslip_det.date_from),
									('end_date','=',payslip_det.date_to),('type','=','ALW'),
									('state','=','confirm')])
			print "all..................alwid..................",alw_ids
			mon_tot_ear = 0.00
			for entry_ids in alw_ids:
				rec = all_ded_obj.browse(cr, uid, entry_ids)
				type_name = rec.pay_type.name
				print "type_name...................",rec.pay_type.code
				if rec.pay_type.code == 'OT':
					con_ot_id = con_obj.search(cr, uid, [('employee_id', '=', emp_id)])			
					print "con_ot_id.............................",con_ot_id
					con_ot_rec= con_obj.browse(cr, uid,con_ot_id[0])
					print "con_rec...............................",con_ot_rec.ot
					if con_ot_rec.ot and ot_days > 0.00:
						rule_id = rec.pay_type.id
						sql = """ select amount from kg_allowance_deduction_line where entry_id=%s and employee_id=%s """%(entry_ids,emp_id)
						cr.execute(sql)
						data = cr.dictfetchone()
						if data:				
							amt = data.values()[0]
							mon_tot_ear += amt				
							vals = {
												
							'slip_id': slip_rec.id,
							'code': rec.pay_type.code,
							'category_id': 'ALW',
							'contract_id':con_rec.id,
							'employee_id': emp_id,
							'salary_rule_id':rule_id,
							'name': type_name,
							'amount': (math.floor(amt)),
							#'amount': amt,
									
							}
							print ".....................................................",vals
							if amt > 0:
								self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,vals)]})
								rec.write({'payslip': True})
								gross_amt += vals['amount']
					
					else:
						pass
				if rec.pay_type.code != 'OT':
					rule_id = rec.pay_type.id
					sql = """ select amount from kg_allowance_deduction_line where entry_id=%s and employee_id=%s """%(entry_ids,emp_id)
					cr.execute(sql)
					data = cr.dictfetchone()
					if data:				
						amt = data.values()[0]
						mon_tot_ear += amt				
						vals = {
											
						'slip_id': slip_rec.id,
						'code': rec.pay_type.code,
						'category_id': 'ALW',
						'contract_id':con_rec.id,
						'employee_id': emp_id,
						'salary_rule_id':rule_id,
						'name': type_name,
						'amount': amt,
								
						}
						print ".....................................................",vals
						if amt > 0:
							self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,vals)]})
							rec.write({'payslip': True})
							gross_amt += vals['amount']
						
				else:
					print "No Allowance Entry for this employee"
			
			# Calculate Total Deduction entry of this month
			
			ded_ids = all_ded_obj.search(cr, uid,[('start_date','=',payslip_det.date_from),
									('end_date','=',payslip_det.date_to),('type','=','DED'),
									('state','=','confirm')])
			print "===================ded_ids=====================",ded_ids
			mon_tot_ded = 0.00
			for j in ded_ids:
				rec = all_ded_obj.browse(cr, uid, j)
				type_name = rec.pay_type.name
				rule_id = rec.pay_type.id
				sql = """ select amount from kg_allowance_deduction_line where entry_id=%s and employee_id=%s """%(j,emp_id)
				cr.execute(sql)
				data = cr.dictfetchone()
				print "data..................------------------............",data
				if data:				
					ded_amt = data.values()[0]
					mon_tot_ded += ded_amt				
					ded_vals = {
					
					'slip_id': slip_rec.id,
					'code': rec.pay_type.code,
					'category_id': 'DED',
					'contract_id':con_rec.id,
					'employee_id': emp_id,
					'salary_rule_id':rule_id,
					'name': type_name,
					'amount': ded_amt,
							
					}
					print "---------------------vals---------------------------",ded_vals
					if ded_amt > 0:
						self.write(cr,uid,slip_rec.id,{'line_ids':[(0,0,ded_vals)]})
						rec.write({'payslip': True})
						deduc_amt += ded_vals['amount']
				else:
					print "No Deduction Entry for this employee"	
					
			
			
					
			#Total Gross Amount
						
			gross_amt = (round(gross_amt,0))
			print "''''''''''''''''''''''gross_amt''''''''''''''''''''",gross_amt
			
			#Total Deduction Amount
			
			deduc_amt = (round(deduc_amt,0))
			print "''''''''''''''''''''''deduc_amt'''''''''''''''''''''",deduc_amt
			
			#Total Net Amount
			
			net_amt = gross_amt - deduc_amt
			
			
			#Contract gross salary
			
			contract_gross = con_rec.gross_salary
			
			#Total Allowance without Basic
			
			allowance_amt = gross_amt - allo_bas
			allowance_amt = (round(allowance_amt,0))
			print "allowance amt,,,,,,,,,,,,,,,,,,,,,,,,,,,",allowance_amt
			if emp_rec:				
				slip_rec.write({
								
								'round_val': net_amt or 0.00, 
								
								'emp_name': emp_nam,
								'tot_paid_days': tot_days or 0.00, 
								'tot_allowance': allowance_amt or 0.00, 
								'tot_deduction': deduc_amt or 0.00,
								'con_cross_amt': contract_gross or 0.00,
								'att_id':att_id,
								'dep_id':dep_id, 
								'cross_amt': gross_amt or 0.00,
								'cum_ded_id':ele,
								})
						
	
			else:
				pass
			
	def hr_verify_sheet(self, cr, uid, ids, context=None):
		self.salary_slip_calculation(cr, uid, ids, context)
		return self.write(cr, uid, ids, {'state': 'done'}, context=context)
		
	
	def employee_salary_run(self, cr, uid, ids, context=None):
		
		""" This function will generate employee payslip 
		if any changes needed after salary process has done """
		
		slip_obj = self.pool.get('hr.payslip')
		slip_rec = self.browse(cr, uid, ids[0])
		emp_rec = slip_rec.employee_id
		print "emp_rec...........12........", emp_rec 		
		last_mon_bal = slip_rec.employee_id.last_month_bal
		round_bal = slip_rec.employee_id.round_off
		emp_rec.write({'round_off': last_mon_bal})
		self.salary_slip_calculation(cr,uid, ids)
		print "ids....................", ids
		
		ex_ids = slip_obj.search(cr, uid, [('employee_id','=', slip_rec.employee_id.id),
					('date_from','=',slip_rec.date_from),('date_to','=',slip_rec.date_to),
					('state','=', 'done')])
		print "ex_ids.....................", ex_ids
		for i in ex_ids:
			sql = """ delete from hr_payslip where id=%s """%(i)
			cr.execute(sql)
		slip_rec.write({'state': 'done'})		
		
		
	def cancel_entry(self,cr,uid,ids,context = None):
		slip_obj = self.pool.get('hr.payslip')
		slip_rec = self.browse(cr, uid, ids[0])
		slip_rec.write({'state': 'draft'})		
		
		
	def print_individual_payslip(self, cr, uid, ids, context=None):		
		rec = self.browse(cr,uid,ids[0])	
		assert len(ids) == 1, 'This option should only be used for a single id at a time'
		wf_service = netsvc.LocalService("workflow")
		wf_service.trg_validate(uid, 'hr.payslip', ids[0], 'send_rfq', cr)
		datas = {
				 'model': 'hr.payslip',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'onscreen.emp.payslip', 'datas': datas, 'ids' : ids, 'nodestroy': True}	
		
	
		
		
kg_payslip()


class kg_batch_payslip(osv.osv): 
	
	_name = 'hr.payslip.run'	
	_inherit = 'hr.payslip.run'	
	
	_columns = {
	
	'name': fields.char('Month', size=64, readonly=True),
	'date_start': fields.date('Date From', required=True, readonly=False),
	'date_end': fields.date('Date To', required=True, readonly=False),
	'slip_date': fields.date('Creation Date'),
	'slip_ids': fields.one2many('hr.payslip', 'payslip_run_id', 'Payslips', required=False, readonly=True),
	'state': fields.selection([
			('draft', 'Draft'),			
			('done', 'Done'),
			('close', 'Close'),
		], 'Status', select=True, readonly=True),
	
	}
	
	def _get_last_month_first(self, cr, uid, context=None):
		
		today = lastdate.date.today()
		first = lastdate.date(day=1, month=today.month, year=today.year)
		mon = today.month - 1
		if mon == 0:
			mon = 12
		else:
			mon = mon
		tot_days = calendar.monthrange(today.year,mon)[1]
		test = first - lastdate.timedelta(days=tot_days)
		res = test.strftime('%Y-%m-%d')
		return res
		
	def _get_last_month_end(self, cr, uid, context=None):
		today = lastdate.date.today()
		first = lastdate.date(day=1, month=today.month, year=today.year)
		last = first - lastdate.timedelta(days=1)
		res = last.strftime('%Y-%m-%d')
		return res
		
	def _get_last_month_name(self, cr, uid, context=None):
		today = lastdate.date.today()
		first = lastdate.date(day=1, month=today.month, year=today.year)
		last = first - lastdate.timedelta(days=1)
		res = last.strftime('%B-%Y')
		return res
		
	def _check_employee_slip_dup(self, cr, uid, ids, context=None):		
		obj = self.pool.get('hr.payslip.run')
		slip = self.browse(cr, uid, ids[0])
		date_from = slip.date_start
		to_date = slip.date_end
		dup_ids = obj.search(cr, uid, [( 'date_start','=',date_from),( 'date_end','=',to_date),
									( 'state','=','done')])
		if len(dup_ids) > 1:
			return False
		return True
		
	def print_monthly_payslip(self, cr, uid, ids, context=None):		
		rec = self.browse(cr,uid,ids[0])	
		assert len(ids) == 1, 'This option should only be used for a single id at a time'
		wf_service = netsvc.LocalService("workflow")
		wf_service.trg_validate(uid, 'hr.payslip.run', ids[0], 'send_rfq', cr)
		datas = {
				 'model': 'hr.payslip.run',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'onscreen.salary.muster', 'datas': datas, 'ids' : ids, 'nodestroy': True}	
	
	
	#_constraints = [
		
		#(_check_employee_slip_dup, 'Payslip has been created already for this month. Check Month and State !!',['amount']),
		
		#] 
		
	
	_defaults = {
	
		'name' : _get_last_month_name,
		'date_start': _get_last_month_first,
		'date_end': _get_last_month_end,
		'slip_date': lambda *a: time.strftime('%Y-%m-%d'),
		
		}
	
	
	def unlink(self, cr, uid, ids, context=None):
		for batch in self.browse(cr, uid, ids, context=context):
			if batch.state not in  ['draft']:
				raise osv.except_osv(_('Warning!'),_('You cannot delete this Batch which is not in draft state !!'))
		return super(kg_batch_payslip, self).unlink(cr, uid, ids, context)

kg_batch_payslip()


class kg_salary_structure(osv.osv):
	
	_name = 'hr.payroll.structure'	
	_inherit = 'hr.payroll.structure'
	
	_columns = {
	
	'state': fields.selection([('draft','Draft'),('approved','Approved')], 'Status', readonly=True),
		
	}
	
	_defaults = {
	
	'state': 'draft',
	
	}
	
	def unlink(self, cr, uid, ids, context=None):
		contract_obj = self.pool.get('hr.contract')
		data = contract_obj.search(cr, uid, (['struct_id','=', ids[0]]))
		if batch.state not in  ['draft']:
			raise osv.except_osv(_('Warning!'),_('You cannot delete this Batch which is not draft state !!'))
		return super(kg_batch_payslip, self).unlink(cr, uid, ids, context)
	
kg_salary_structure()
