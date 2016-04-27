
from osv import fields,osv
from datetime import date
from datetime import datetime
import calendar
import json
import datetime as dt
from datetime import time,timedelta

class kg_tax(osv.osv):
	_name = 'kg.tax'
	
	def _employee_get(self, cr, uid, context=None):
		ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
		if ids:
			return ids[0]
		return False
		
	_columns = {
	    'employee_id': fields.many2one('hr.employee', "Employee Name", select=True,required=True),
		'val_from': fields.date('Valid From', required=True),
		'val_to': fields.date('Valid To', required=True),
		'user_id':fields.related('employee_id', 'user_id', type='many2one', relation='res.users', string='User', store=True),
		'code': fields.char('Employee Code', required=True),	
		'designation': fields.char('Designation', required=True),
		
		'company': fields.char('Company', required=True),
		'phone': fields.char('Phone', required=True),
		'email': fields.char('Email', required=True),	
		'state': fields.selection([('approve','Approve'),('confirm','Entry Confirmed'),('draft','Draft')], 'Status'),
		'house_rent':fields.float('House rent Paid Per Annum'),
		'address_house_rent':fields.text('Address of House rent Paid'),
		'institution_house_loan':fields.char('Name of the Institution from Housing Loan Availed'),
		'date_house_loan':fields.date('Date of Housing Loan Availed'),
		'addr_house_loan':fields.text('Address of the House for Loan Availed'),
		'house_loan_interest':fields.float('Housing Loan Interest'),
		'house_loan_premium':fields.float('Housing Loan Principal -(Repayment Amount)'),
		'medi_premiun_self_fly':fields.float('Mediclaim insurance Premium- (Self+Family)'),
		'medi_premium_parent':fields.float('Mediclaim insurance Premium- Parents'),
		'pension_plan':fields.float('Pension Plan'),
		'life_insu_plan':fields.float('Life Insurance Premium'),
		'mutual_fund':fields.float('Mutual Funds - Tax Saving Scheme'),
		'unit_life_insu_plan':fields.float('Unit Life Insurance Plan (ULIP)'),
		'national_saving':fields.float('National Savings Certificate (NSC)'),
		'infra_bond':fields.float('Infrastructure Bonds (IDBI,ICICI)'),
		'public_provident_fund':fields.float('Public Provident Fund  (PPF)'),
		'expenditure_children':fields.float('Expenditure towards educaiton for Chidren'),
		'five_yr_depo_bank':fields.float('5 Year Term Deposit in Bank'),
		'five_yr_depo_po':	fields.float('5 Year Term Deposit in Post Office'),
		'others':	fields.float('Others'),
		'interest_edu_loan':fields.float('Interest on Education loan'),
		'total':fields.float('Total Amount'),
		'pan':fields.char('PAN Number',required=True),
				
			
	}
	
		
	def onchange_employee_name(self, cr, uid, ids, code,employee_id,designation,company,phone,email, context=None):
		value = {'code': '','designation':'','company':'','phone':'','email':''}
		if employee_id:
			emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
			print "Browse record  ",emp
			print "designation    ",emp.job_id.name
			
			print "company  ",emp.address_id.id
			print " phone   ",emp.work_phone
			print "email ",emp.work_email
			value = {'code': emp.emp_code,
			'designation':emp.job_id.name,
			
			'company':emp.address_id.name,
			'phone':emp.work_phone,
			'email':emp.work_email
			}
			
		return {'value': value}
		
	def confirm_data(self, cr, uid, ids,context=None):
		emp_rec=self.browse(cr,uid,ids[0])
		house_rent=emp_rec.house_rent
		house_loan_interest=emp_rec.house_loan_interest
		house_loan_premium=emp_rec.house_loan_premium
		medi_premiun_self_fly=emp_rec.medi_premiun_self_fly
		medi_premium_parent=emp_rec.medi_premium_parent
		pension_plan=emp_rec.pension_plan
		life_insu_plan=emp_rec.life_insu_plan
		mutual_fund=emp_rec.mutual_fund
		unit_life_insu_plan=emp_rec.unit_life_insu_plan
		national_saving=emp_rec.national_saving
		infra_bond=emp_rec.infra_bond
		public_provident_fund=emp_rec.public_provident_fund
		expenditure_children=emp_rec.expenditure_children
		five_yr_depo_bank=emp_rec.five_yr_depo_bank
		five_yr_depo_po=emp_rec.five_yr_depo_po
		others=emp_rec.others
		interest_edu_loan=emp_rec.interest_edu_loan
		total=emp_rec.total
		
		total=house_rent+house_loan_interest+house_loan_premium+medi_premiun_self_fly+medi_premium_parent+pension_plan+life_insu_plan+mutual_fund+unit_life_insu_plan+national_saving+infra_bond+public_provident_fund+expenditure_children+five_yr_depo_bank+five_yr_depo_po+others+interest_edu_loan
		print "Total   ",total
				
		self.write(cr,uid,ids,{'total':total})
		self.write(cr,uid,ids,{'state':'confirm'})
		return True
		
	
		
	def first_date(self, cr, uid, ids,context=None):
		current_month=date.today().month
		if current_month <=12 and current_month >3 :
			a = date(date.today().year, 04, 01)
			
		else:
			a=date(date.today().year-1, 04, 01)
			
		print a
		
		return a.strftime('%Y-%m-%d')
		
	def last_date(self, cr, uid, ids,context=None):
		current_month=date.today().month
		
		if current_month <=12 and current_month >3 :
			
			b = date(date.today().year+1, 03, 31)
		else:
			
			b = date(date.today().year, 03, 31)
			
		
		print b
		return b.strftime('%Y-%m-%d')
	
	_defaults = {
	'employee_id': _employee_get,
	'state':'draft',
	'val_from':first_date,
	'val_to':last_date,
	'user_id': lambda obj, cr, uid, context: uid,
	
	}	
		
kg_tax()
